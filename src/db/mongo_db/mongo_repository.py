from pymongo.results import UpdateResult, InsertOneResult
from pymongo.synchronous.collection import Collection
from pymongo.synchronous.database import Database
from src.server.flask.exceptions import ResourceNotFoundError, DatabaseError, BlogAppException
from src.db.odm_blog import Post, Comment, Message, User
from src.db.repository import Repository
from typing import List, Mapping, Optional, Union
from pymongo import MongoClient
from bson import ObjectId
import os
import logging

logging.basicConfig(level=logging.INFO)


class MongoDBRepository(Repository):
    _instance: Optional['MongoDBRepository'] = None

    def __new__(cls, *args, **kwargs):
        """Ensure that only one instance of MongoDBRepository exists."""
        if cls._instance is None:
            cls._instance = super(MongoDBRepository, cls).__new__(cls, *args, **kwargs)
            cls.__init_mongo_client()  # Initialize MongoDB client
        return cls._instance

    @classmethod
    def __init_mongo_client(cls):
        """
        Create MongoClient and setup databases and collections
        :return: None
        """
        MONGO_USER:str = str(os.getenv("SERVER_API_USER"))
        MONGO_PASSWORD:str = str(os.getenv("SERVER_API_PASSWORD"))
        MONGO_HOST:str = str(os.getenv("MONGO_HOST"))
        MONGO_PORT:str = str(os.getenv("MONGO_PORT"))

        CONNECTION_STRING = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/"
        cls._client:MongoClient = MongoClient(CONNECTION_STRING)
        cls._messages_db:Database = cls._client["messages"]
        cls._users_db:Database = cls._client["users"]
        cls._messages_collection:Collection = cls._messages_db["comments"]
        cls._messages_collection.create_index(
        [("reply_to_message_id", 1)],
            partialFilterExpression={"reply_to_message_id": {"$eq": None}}
        )
        cls._users_collection:Collection = cls._users_db["users"]
        cls._users_collection.create_index("user_id", unique=True)

    @staticmethod
    def __message_data_to_message_object(message_data:Mapping[str,any])->Message:
        """
        create Post or Comment object from message_data
        :param message_data: message data from MongoDB
        :return: Message object representing message
        """
        if message_data["reply_to_message_id"] is None:
            return MongoDBRepository.__message_data_to_post_object(message_data)
        else:
            return MongoDBRepository.__message_data_to_comment_object(message_data)

    @staticmethod
    def __message_data_to_post_object(message_data:Mapping[str,any])->Post:
        """
        create Post object from message_data
        :param message_data: message data from MongoDB
        :return: Post object representing message
        """
        return Post(message_id=str(message_data["_id"]), content=message_data["content"],
                    user_id_owner=message_data["user_id_owner"],
                    user_likes=message_data["user_likes"])

    @staticmethod
    def __message_data_to_comment_object(message_data:Mapping[str,any])->Comment:
        """
        create Comment object from message_data
        :param message_data: message data from MongoDB
        :return: Comment object representing message
        """
        return Comment(message_id=str(message_data["_id"]), content=message_data["content"],
                user_id_owner=message_data["user_id_owner"],
                user_likes=message_data["user_likes"],
                reply_to_message_id=str(message_data["reply_to_message_id"]))


    def get_posts_blog(self, posts_limit:int, start_index:int = 0, **kwargs)->List[Post]:
        try:
            query = {"reply_to_message_id": {"$eq": None}}
            posts = self._messages_collection.find(query).skip(start_index).limit(posts_limit)
            posts_objects:List[Post] = [MongoDBRepository.__message_data_to_post_object(post_data) for post_data in posts]
        except Exception as e:
            raise DatabaseError from e

        return posts_objects

    def get_message_blog(self, message_id:str, user_id_owner:str='') ->Message:
        filter_criteria:dict = {"_id": ObjectId(message_id)}
        if user_id_owner!='':
            filter_criteria["user_id_owner"] = user_id_owner
        try:
            message_data:Mapping[str,any] = self._messages_collection.find_one(filter_criteria)
            if message_data is None:
                raise ResourceNotFoundError
        except ResourceNotFoundError:
                if user_id_owner!='':
                  raise ResourceNotFoundError(f"Message ID {message_id} with user_id_owner {user_id_owner} not found")
                raise ResourceNotFoundError(f"Message ID {message_id} not found")
        except BlogAppException as e:
            raise e
        except Exception as e:
            raise DatabaseError from e

        return MongoDBRepository.__message_data_to_message_object(message_data)


    def create_message_blog(self, content:str, user_id_owner:str, reply_to_message_id:str)->Message:
        new_message = {
            "content": content,
            "user_id_owner": user_id_owner,
            "user_likes": [],
            "reply_to_message_id": None if reply_to_message_id =='' else ObjectId(reply_to_message_id)
        }
        try:
            insert_one_result:InsertOneResult = self._messages_collection.insert_one(new_message)
            created_message_data = self._messages_collection.find_one({"_id": insert_one_result.inserted_id})
        except BlogAppException as e:
            raise e
        except Exception as e:
            raise DatabaseError from e

        return MongoDBRepository.__message_data_to_message_object(created_message_data)

    def edit_message_blog(self, message_id: str, new_content:str)->Message:
        message_id_obj:ObjectId = ObjectId(message_id)
        try:
            update_result:UpdateResult = self._messages_collection.update_one(filter={"_id": message_id_obj},
                                           update={"$set": {"content": new_content}},
                                           upsert=False)
            if update_result.matched_count == 0:
                raise ResourceNotFoundError(f"Message ID {message_id} not found")
            if update_result.modified_count == 0:
                raise DatabaseError(f"Edit message ID {message_id} fail")
            edited_message_data = self._messages_collection.find_one({"_id": message_id_obj})
        except BlogAppException as e:
            raise e
        except Exception as e:
            raise DatabaseError from e

        return MongoDBRepository.__message_data_to_message_object(edited_message_data)


    def delete_message_blog(self, message_id:str)->Union[Message,None]:
        filter_message:dict = {"_id": ObjectId(message_id)}
        message_data:Mapping[str,any] = self._messages_collection.find_one(filter=filter_message)
        if message_data:
            try:
                # delete messages that replied to original message being deleted
                reply_comments_to_delete = self._messages_collection.find({"reply_to_message_id": ObjectId(message_id)})
                if reply_comments_to_delete != None:
                    for comment_data in reply_comments_to_delete:
                        self.delete_message_blog(comment_data["_id"])
                self._messages_collection.delete_one({"_id": ObjectId(message_id)})
            except BlogAppException as e:
                raise e
            except Exception as e:
                raise DatabaseError from e

            return None if message_data is None \
                else MongoDBRepository.__message_data_to_message_object(message_data)

    def __update_message_like(self, update_type:str, message_id:str, user_id:str)->bool:
        """
        update operation on likes array field of document based on message id
        :param update_type:  $push or $pull DB operation
        :param message_id: unique identifier for message_id
        :param user_id: unique identifier for user that will be added/remove from likes field array
        :return: True
        :raises: DatabaseError for MongoDB fail
        """
        message_id_obj = ObjectId(message_id)
        try:
            update_result:UpdateResult = self._messages_collection.update_one(
                upsert=False,
                filter = {"_id": message_id_obj},
                update={update_type: {"user_likes": user_id}}
            )
            if update_result.matched_count==0:
                raise ResourceNotFoundError(f"Message ID {message_id} not found")
        except BlogAppException as e:
            raise e
        except Exception as e:
            raise DatabaseError from e

        return True

    def add_message_like(self, message_id: str, user_id: str) -> bool:
        return self.__update_message_like("$push", message_id, user_id)


    def remove_message_like(self, message_id: str, user_id: str) -> bool:
        return self.__update_message_like("$pull", message_id, user_id)

    @staticmethod
    def __user_data_to_user_object(user_data:Mapping[str,any]):
        """
         create User object from user_data
        :param user_data: user data from MongoDB
        :return: User object representing user in database
        """
        return User(user_id=user_data["user_id"],password=user_data["password"], email=user_data["email"],name=user_data["name"], roles=user_data["roles"])


    def create_user_blog(self, user_id: str,password:str, email:str, name:str, roles:List[str]) -> User:
        new_user = {
            "user_id": user_id,
            "password": password,
            "email":email,
            "name": name,
            "roles": roles,
        }
        try:
            if self._users_collection.find_one(filter={"user_id": user_id}):
                raise Exception(f"User Id {user_id} already exists")
            insert_one_result: InsertOneResult = self._users_collection.insert_one(new_user)
            created_user_data = self._users_collection.find_one({"_id": insert_one_result.inserted_id})
        except BlogAppException as e:
            raise e
        except Exception as e:
            raise DatabaseError from e

        return MongoDBRepository.__user_data_to_user_object(created_user_data)

    def get_user_blog(self, user_id: str) -> User:
        filter:dict = {"user_id": user_id}
        try:
            user_data:Mapping[str,any] = self._users_collection.find_one(filter=filter)
            if user_data is None:
                raise ResourceNotFoundError(f"User ID {user_id} not found")
        except BlogAppException as e:
            raise e
        except Exception as e:
            raise DatabaseError from e

        return MongoDBRepository.__user_data_to_user_object(user_data)


    def update_user_details_blog(self, user_id: str,password:str = '', email:str = '', name:str= '')->User:
        filter:dict = {"user_id": user_id}
        set_dict: dict = {}
        if password!='':
            set_dict['password'] = password
        if email != '':
            set_dict['email'] = email
        if name!='':
            set_dict['name'] = name
        update: dict = {"$set": set_dict}
        try:
            update_result: UpdateResult = (self._users_collection.
                    update_one(filter=filter,update=update,upsert=False))
            if update_result.matched_count==0:
                raise ResourceNotFoundError(f"User ID {user_id} not found")

            updated_user_data = self._users_collection.find_one(filter=filter)
        except BlogAppException as e:
            raise e
        except Exception as e:
            raise DatabaseError from e

        return MongoDBRepository.__user_data_to_user_object(updated_user_data)


    def delete_user_blog(self, user_id: str) -> Union[User,None]:
        filter_user:dict = {"user_id": user_id}
        user_data:Mapping[str,any] = self._users_collection.find_one(filter=filter_user)
        if user_data:
            try:
                self._users_collection.delete_one(filter=filter_user)
            except Exception as e:
                raise DatabaseError from e

            return MongoDBRepository.__user_data_to_user_object(user_data)

    def __update_user_role(self,update_type:str, user_id:str, role:str)->bool:
        """
        update operation on roles array field of document based on user_id
        :param update_type: $push or $pull DB operation
        :param user_id:  unique identifier for user
        :param role: role that will be added/removed from roles field
        :return: True
        :raises: DatabaseError for MongoDB fail
        """
        try:
            update_result:UpdateResult = self._users_collection.update_one(
                upsert=False,
                filter = {"user_id": user_id},
                update={update_type: {"roles": role}}
            )
            if update_result.matched_count==0:
                raise ResourceNotFoundError(f"User ID {user_id} not found")
        except BlogAppException as e:
            raise e
        except Exception as e:
            raise DatabaseError from e

        return True

    def add_user_role(self, user_id:str, role:str)->bool:
        return self.__update_user_role("$push", user_id, role)

    def remove_user_role(self, user_id:str, role:str):
        return self.__update_user_role("$pull", user_id, role)


if __name__=="__main__":
    mongo = MongoDBRepository()

    # print(mongo.get_message_blog("67503c91afe4259d3efd1732"))
    # mongo.delete_user_blog("user1")
    # mongo.create_user_blog(user_id="user1",name="user1",password="$2b$12$ec8wsNHjZq6gZu7Lqa.SmekrPBLxe/Dl0uQICpPRM/L3dEeAkg8O.",email="user1@gmail.com",roles=["post_user"])
    print(mongo.get_user_blog("user2"))
    # mongo.create_user_blog(user_id="user2",name="user2", password="user2", email="user2@gmail.com", roles=[])
    mongo.update_user_details_blog(user_id ="user2",password='$2b$12$TqqCf5JQh5W9oXjbqK4oguu/4D9ndD0fTr2ni3qpNvV1Z79nAVgzy')
    # mongo.remove_user_role("user1","post_user")
    # print(mongo.get_user_blog("user1"))
    # for post in mongo.get_posts_blog(0,20):
    #     mongo.delete_message_blog(post.message_id)
    # print("posts deleted")
    # first_post:Message = mongo.create_message_blog(content="my very first post", user_id_owner="first_user", reply_to_message_id='')
    # print(first_post.content)
    # b1 = mongo.add_message_like(first_post.message_id,"second_user")
    # updated_post = mongo.get_message_blog(first_post.message_id)
    # print(updated_post.user_likes)
    # b2 = mongo.remove_message_like(first_post.message_id, "second_user")
    # if not (b1 and b2):
    #     print("like didn't work")
    #
    # print(len(mongo.get_posts_blog(0,20)))
    # mongo.create_message_blog("second message","first user",'')
    # print(len(mongo.get_posts_blog(0,20)))
    # print(len(mongo.get_posts_blog(1, 20)))
    # updated_post = mongo.get_message_blog(first_post.message_id)
    # print(updated_post.user_likes)
    # mongo.delete_message_blog(first_post.message_id)
    # mongo.get_message_blog(first_post.message_id) ## expected error