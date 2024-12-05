from pymongo.results import UpdateResult, InsertOneResult
from pymongo.synchronous.collection import Collection
from pymongo.synchronous.database import Database
from src.server.flask_server.exceptions import ResourceNotFoundError, DatabaseError, BlogAppException
from src.database.odm_blog import Post, Comment, Message, User
from src.database.repository import Repository
from typing import List, Mapping, Optional
from pymongo import MongoClient
from bson import ObjectId

READ_WRITE_USER = "root"
READ_WRITE_PASSWORD = "password"
MONGO_PORT = "27017"
MONGO_HOST = "localhost"
# MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME", "root_example")
# MONGO_PASSWORD = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "password_example")
# MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
# MONGO_PORT = os.getenv("MONGO_PORT", "27017")

CONNECTION_STRING = f"mongodb://{READ_WRITE_USER}:{READ_WRITE_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/"

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
        if message_data["reply_to_message_id"] is None:
            return MongoDBRepository.__message_data_to_post_object(message_data)
        else:
            return MongoDBRepository.__message_data_to_comment_object(message_data)

    @staticmethod
    def __message_data_to_post_object(message_data:Mapping[str,any])->Post:
        return Post(message_id=str(message_data["_id"]), content=message_data["content"],
                    user_id_owner=message_data["user_id_owner"],
                    user_likes=message_data["user_likes"])

    @staticmethod
    def __message_data_to_comment_object(message_data:Mapping[str,any])->Comment:
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


    def delete_message_blog(self, message_id:str)->Message|None:
        filter_message:dict = {"_id": ObjectId(message_id)}
        message_data:Mapping[str,any] = self._messages_collection.find_one(filter=filter_message)
        if message_data:
            try:
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
        return User(user_id=user_data["user_id"],password=user_data["password"], email=user_data["email"],name=user_data["name"], roles=user_data["roles"])


    def create_user_blog(self, user_id: str,password:str, email:str, name:str, roles:list[str]) -> User:
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


    def update_user_details_blog(self, user_id: str = '',password:str = '', email:str = '', name:str= '')->User:
        filter:dict = {"user_id": user_id}
        set_dict:dict = {variable:value for variable,value in locals().items() if variable!='self' and value!=''}
        update: dict = {"$set": set_dict}
        try:
            update_result: UpdateResult = (self._users_collection.
                    update_one(filter=filter,update=update,upsert=False))
            if update_result.matched_count==0:
                raise ResourceNotFoundError(f"User ID {user_id} not found")
            if update_result.modified_count == 0:
                raise DatabaseError(f"Update User ID {user_id} fail")
            updated_user_data = self._users_collection.find_one(filter=filter)
        except BlogAppException as e:
            raise e
        except Exception as e:
            raise DatabaseError from e

        return MongoDBRepository.__user_data_to_user_object(updated_user_data)


    def delete_user_blog(self, user_id: str) -> User|None:
        filter_user:dict = {"user_id": user_id}
        user_data:Mapping[str,any] = self._users_collection.find_one(filter=filter_user)
        if user_data:
            try:
                self._users_collection.delete_one(filter=filter_user)
            except Exception as e:
                raise DatabaseError from e

            return MongoDBRepository.__user_data_to_user_object(user_data)

    def __update_user_role(self,update_type:str, user_id:str, role:str)->bool:
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
    # mongo.delete_user_blog("user1")
    # mongo.create_user_blog(user_id="user1",name="user1",password="$2b$12$ec8wsNHjZq6gZu7Lqa.SmekrPBLxe/Dl0uQICpPRM/L3dEeAkg8O.",email="user1@gmail.com",roles=["post_user"])
    # mongo.create_user_blog(user_id="user2",name="user2", password="user2", email="user2@gmail.com", roles=[])
    print(mongo.get_user_blog("user2"))
    # mongo.update_user_details_blog(user_id ="user2",password='$2b$12$G9vjh1e8DS.nU0e.Xo6DWu1Y64we2kKXL75laTuGfQJIPUKFAQMYq')
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