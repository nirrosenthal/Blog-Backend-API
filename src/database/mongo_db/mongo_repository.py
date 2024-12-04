from pymongo.results import UpdateResult, InsertOneResult
from pymongo.synchronous.collection import Collection
from pymongo.synchronous.database import Database
from src.server.flask_server.exceptions import ResourceNotFoundError, DatabaseError
from src.database.odm_blog import Post, Comment, Message
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
        cls._messages_collection:Collection = cls._messages_db["comments"]
        cls._messages_collection.create_index(
        [("reply_to_message_id", 1)],
            partialFilterExpression={"reply_to_message_id": {"$eq": None}}
        )

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

    def get_posts_blog(self, start_index:int =0, posts_limit:int = 50)->List[Post]:
        try:
            query = {"reply_to_message_id": {"$eq": None}}
            posts = self._messages_collection.find(query).skip(start_index).limit(posts_limit)
            posts_objects:List[Post] = [MongoDBRepository.__message_data_to_post_object(post_data) for post_data in posts]
            return posts_objects
        except Exception as e:
            raise DatabaseError(str(e))


    def get_message_blog(self, message_id:str, user_id_owner:str='') ->Message:
        filter_criteria:dict = {"_id": ObjectId(message_id)}
        if user_id_owner!='':
            filter_criteria["user_id_owner"] = user_id_owner
        try:
            message_data:Mapping[str,any] = self._messages_collection.find_one(filter_criteria)

            if message_data is None:
                raise ResourceNotFoundError

            return MongoDBRepository.__message_data_to_message_object(message_data)
        except ResourceNotFoundError:
                if user_id_owner!='':
                  raise ResourceNotFoundError(f"Message ID {message_id} with user_id_owner {user_id_owner} not found")
                raise ResourceNotFoundError(f"Message ID {message_id} not found")
        except Exception as e:
            raise DatabaseError(str(e))



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
            return MongoDBRepository.__message_data_to_message_object(created_message_data)
        except ResourceNotFoundError:
            raise ResourceNotFoundError
        except Exception as e:
            raise DatabaseError(str(e))

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
            return MongoDBRepository.__message_data_to_message_object(edited_message_data)
        except ResourceNotFoundError or DatabaseError as e:
            raise e
        except Exception as e:
            raise DatabaseError(str(e))


    def delete_message_blog(self, message_id:str)->Message:
        message_to_delete:Message = self.get_message_blog(message_id)
        try:
            reply_comments_to_delete = self._messages_collection.find({"reply_to_message_id": ObjectId(message_id)})
            if reply_comments_to_delete is None:
                raise ResourceNotFoundError(f"Message ID {message_id} not found")

            for comment_data in reply_comments_to_delete:
                self.delete_message_blog(comment_data["_id"])

            delete_result = self._messages_collection.delete_one({"_id": ObjectId(message_id)})
            if delete_result.deleted_count == 0:
                raise DatabaseError(f"Delete Message ID {message_id} fail")

            return message_to_delete
        except DatabaseError or ResourceNotFoundError as e:
            raise e
        except Exception as e:
            raise DatabaseError(str(e))


    def add_message_like(self, message_id: str, user_id: str) -> bool:
        message_id_obj = ObjectId(message_id)
        try:
            update_result:UpdateResult = self._messages_collection.update_one(
                upsert=False,
                filter = {"_id": message_id_obj},
                update={"$push": {"user_likes": user_id}}
            )
            if update_result.matched_count==0:
                raise ResourceNotFoundError(f"Message ID {message_id} not found")
        except Exception as e:
            raise DatabaseError(str(e))

        return True

    def remove_message_like(self, message_id: str, user_id: str) -> bool:
        message_id_obj = ObjectId(message_id)
        try:
            update_result:UpdateResult = self._messages_collection.update_one(
                upsert=False,
                filter = {"_id": message_id_obj},
                update={"$pull": {"user_likes": user_id}}
            )
            if update_result.matched_count==0:
                raise ResourceNotFoundError(f"Message ID {message_id} not found")
        except Exception as e:
            raise DatabaseError(str(e))

        return True



if __name__=="__main__":
    mongo = MongoDBRepository()
    for post in mongo.get_posts_blog(0,20):
        mongo.delete_message_blog(post.message_id)
    print("posts deleted")
    first_post:Message = mongo.create_message_blog("my very first post", '', "first_user")
    print(first_post.content)
    b1 = mongo.add_message_like(first_post.message_id,"second_user")
    updated_post = mongo.get_message_blog(first_post.message_id)
    print(updated_post.user_likes)
    b2 = mongo.remove_message_like(first_post.message_id, "second_user")
    if not (b1 and b2):
        print("like didn't work")

    print(len(mongo.get_posts_blog(0,20)))
    mongo.create_message_blog("second message", '',"first user")
    print(len(mongo.get_posts_blog(0,20)))
    print(len(mongo.get_posts_blog(1, 20)))
    updated_post = mongo.get_message_blog(first_post.message_id)
    print(updated_post.user_likes)
    mongo.delete_message_blog(first_post.message_id)
    mongo.get_message_blog(first_post.message_id) ## expected error