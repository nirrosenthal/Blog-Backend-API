from pymongo.synchronous.collection import Collection
from pymongo.synchronous.database import Database

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
        # Ensures that only one instance of MongoDBRepository exists
        if not cls._instance:
            cls._instance = super(MongoDBRepository, cls).__new__(cls, *args, **kwargs)
            cls._instance.__init_mongo_client()
        return cls._instance

    def __init_mongo_client(self):
        self._client:MongoClient = MongoClient(CONNECTION_STRING)
        self._messages_db:Database = self._client["messages"]
        self._messages_collection:Collection = self._messages_db["comments"]
        self._messages_collection.create_index(
        [("reply_to_message_id", 1)],
            partialFilterExpression={"reply_to_message_id": {"$eq": None}}
        )

    # def __init__(self):
    #     self._client:MongoClient = MongoClient(CONNECTION_STRING)
    #     self._messages_db:Database = self._client["messages"]
    #     self._messages_collection:Collection = self._messages_db["comments"]
    #     self._messages_collection.create_index(
    #     [("reply_to_message_id", 1)],
    #         partialFilterExpression={"reply_to_message_id": {"$ne": None}}
    #         )

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
        query = {"reply_to_message_id": {"$eq": None}}
        posts = self._messages_collection.find(query).skip(start_index).limit(posts_limit)
        posts_objects:List[Post] = [MongoDBRepository.__message_data_to_post_object(post_data) for post_data in posts]
        return posts_objects


    def get_message_blog(self, message_id:str, user_id_owner:str='') ->Message:
        filter_criteria:dict = {"_id": ObjectId(message_id)}
        if user_id_owner!='':
            filter_criteria["user_id_owner"] = user_id_owner

        message_data:Mapping[str,any] = self._messages_collection.find_one(filter_criteria)
        if message_data is None:
            raise Exception("message not exist")

        return MongoDBRepository.__message_data_to_message_object(message_data)


    def create_message_blog(self, content:str, reply_to_message_id:str, user_id_owner:str)->Message:
        new_message = {
            "content": content,
            "user_id_owner": user_id_owner,
            "user_likes": [],
            "reply_to_message_id": None if reply_to_message_id =='' else ObjectId(reply_to_message_id)
        }

        created_message_result = self._messages_collection.insert_one(new_message)
        created_message_data = self._messages_collection.find_one({"_id": created_message_result.inserted_id})
        return MongoDBRepository.__message_data_to_message_object(created_message_data)


    def edit_message_blog(self, message_id: str, new_content:str)->Message:
        message_id_obj:ObjectId = ObjectId(message_id)
        self._messages_collection.update_one({"_id": message_id_obj},
                                           {"$set": {"content": new_content}})

        edited_message_data = self._messages_collection.find_one({"_id": message_id_obj})
        return MongoDBRepository.__message_data_to_message_object(edited_message_data)


    def delete_message_blog(self, message_id:str)->Message:
        message_to_delete:Message = self.get_message_blog(message_id)
        reply_comments_to_delete = self._messages_collection.find({"reply_to_message_id": ObjectId(message_id)})
        for comment_data in reply_comments_to_delete:
            self.delete_message_blog(comment_data["_id"])

        self._messages_collection.delete_one({"_id": ObjectId(message_id)})

        return message_to_delete


    def add_message_like(self, message_id: str, user_id: str) -> bool:
        message_id_obj = ObjectId(message_id)
        operation_result = self._messages_collection.update_one(
            {"_id": message_id_obj},
            {"$push": {"user_likes": user_id}}
        )
        return True


    def remove_message_like(self, message_id: str, user_id: str) -> bool:
        message_id_obj = ObjectId(message_id)
        operation_result = self._messages_collection.update_one(
            {"_id": message_id_obj},
            {"$pull": {"user_likes": user_id}}
        )
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