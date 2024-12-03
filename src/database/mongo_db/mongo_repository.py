from pymongo.synchronous.collection import Collection
from pymongo.synchronous.database import Database

from src.database.odm_blog import Post,Comment
from src.database.repository import Repository
from typing import List
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

    def __init__(self):
        self._client:MongoClient = MongoClient(CONNECTION_STRING)
        self._messages_db:Database = self._client["messages"]
        self._posts_collection:Collection = self._messages_db["posts"]
        self._comments_collection:Collection = self._messages_db["comments"]
        self._users_db:Database = self._client["users"]
        self._comments_collection.create_index(
        [("reply_to_message_id", 1)],
            partialFilterExpression={"reply_to_message_id": {"$exists": True}}
            )

    @staticmethod
    def _create_post_with_post_data(post_data:dict)->Post:
        return Post(post_id=str(post_data["_id"]), content=post_data["content"],
                    user_id_owner=post_data["user_id_owner"],
                    user_likes=post_data["user_likes"])

    @staticmethod
    def _create_comment_with_comment_data(comment_data:dict)->Comment:
        return Comment(comment_id=str(comment_data["_id"]), content=comment_data["content"],
                user_id_owner=comment_data["user_id_owner"],
                user_likes=comment_data["user_likes"],
                reply_to_message_id=str(comment_data["reply_to_message_id"]))

    def get_posts_blog(self, start_id:int =0, posts_limit:int = 50)->List[Post]:
        pass


    def get_post_blog(self, post_id:str) ->Post:
        post_data = self._posts_collection.find_one({"_id": ObjectId(post_id)})
        return MongoDBRepository._create_post_with_post_data(post_data)


    def create_post_blog(self, content:str, user_id_owner: str)->Post:
        new_post = {
            "content": content,
            "user_id_owner": user_id_owner,
            "user_likes": [],
        }

        created_post_result = self._posts_collection.insert_one(new_post)
        post_data = self._posts_collection.find_one({"_id": created_post_result.inserted_id})

        return MongoDBRepository._create_post_with_post_data(post_data)


    def edit_post_blog(self, post_id: str, new_content:str, user_id_owner: str)->Post:
        post_id_obj = ObjectId(post_id)
        self._posts_collection.update_one({"_id": post_id_obj},
                                           {"$set": {"content": new_content}})

        edited_post_data = self._posts_collection.find_one({"_id": post_id_obj})
        return MongoDBRepository._create_post_with_post_data(edited_post_data)


    def delete_post_blog(self, post_id:str, user_id_owner: str)->Post:
        post_id_obj = ObjectId(post_id)
        post_to_delete = self._posts_collection.find_one({"_id": post_id_obj})
        reply_comments_to_delete = self._comments_collection.find({"reply_to_message_id": post_id_obj})
        for comment in reply_comments_to_delete:
            self.delete_comment_blog(comment["_id"], comment["user_id_owner"])

        self._posts_collection.delete_one({"_id": post_id_obj})

        return MongoDBRepository._create_post_with_post_data(post_to_delete)


    def get_comment_blog(self, comment_id:str) ->Comment:
        comment_data = self._comments_collection.find_one({"_id": ObjectId(comment_id)})
        return MongoDBRepository._create_comment_with_comment_data(comment_data)


    def create_comment_blog(self, content:str, reply_to_message_id:str, user_id_owner:str)->Comment:
        new_comment = {
            "content": content,
            "user_id_owner": user_id_owner,
            "user_likes": [],
            "reply_to_message_id": ObjectId(reply_to_message_id)
        }

        created_comment_result = self._comments_collection.insert_one(new_comment)
        comment_data = self._comments_collection.find_one({"_id": created_comment_result.inserted_id})
        return MongoDBRepository._create_comment_with_comment_data(comment_data)


    def edit_comment_blog(self, comment_id:str, new_content: str, user_id_owner: str)->Comment:
        comment_id_obj = ObjectId(comment_id)
        self._comments_collection.update_one({"_id": comment_id_obj},
                                           {"$set": {"content": new_content}})

        edited_comment_data = self._comments_collection.find_one({"_id": comment_id_obj})
        return MongoDBRepository._create_comment_with_comment_data(edited_comment_data)


    def delete_comment_blog(self, comment_id:str, user_id_owner: str)->Comment:
        comment_id_obj = ObjectId(comment_id)
        comment_to_delete = self._comments_collection.find_one({"_id": comment_id_obj})
        reply_comments_to_delete = self._comments_collection.find({"reply_to_message_id": comment_id_obj})
        for comment in reply_comments_to_delete:
            self.delete_comment_blog(comment["_id"], comment["user_id_owner"])

        self._comments_collection.delete_one({"_id": comment_id_obj})

        return MongoDBRepository._create_comment_with_comment_data(comment_to_delete)


    @staticmethod
    def _add_message_like(collection:Collection, message_id:str, user_id: str)->bool:
        message_id_obj = ObjectId(message_id)
        message = collection.find_one({"_id": message_id_obj})

        if not message or user_id in message.get("user_likes", []):
            return False

        collection.update_one(
            {"_id": message_id_obj},
            {"$push": {"user_likes": user_id}}
        )
        return True

    @staticmethod
    def _remove_message_like(collection:Collection, message_id:str, user_id:str)->bool:
        message_id_obj = ObjectId(message_id)
        message = collection.find_one({"_id": message_id_obj})

        if not message or user_id not in message.get("user_likes", []):
            return False

        collection.update_one(
            {"_id": message_id_obj},
            {"$pull": {"user_likes": user_id}}
        )
        return True


    def add_post_like(self, message_id: str, user_id: str) -> bool:
        return MongoDBRepository._add_message_like(self._posts_collection, message_id, user_id)


    def remove_post_like(self, message_id: str, user_id: str) -> bool:
        return MongoDBRepository._remove_message_like(self._posts_collection, message_id, user_id)


    def add_comment_like(self, message_id: str, user_id: str) -> bool:
        return MongoDBRepository._add_message_like(self._comments_collection, message_id, user_id)


    def remove_comment_like(self, message_id: str, user_id: str) -> bool:
        return MongoDBRepository._remove_message_like(self._comments_collection, message_id, user_id)



if __name__=="__main__":
    mongo = MongoDBRepository()
    first_post:Post = mongo.create_post_blog("my very first post", "first_user")
    b1 = mongo.add_post_like(first_post.post_id,"second_user")
    updated_post = mongo.get_post_blog(first_post.post_id)
    print(updated_post.user_likes)
    b2 = mongo.remove_post_like(first_post.post_id, "second_user")
    if not (b1 and b2):
        print("like didn't work")

    updated_post = mongo.get_post_blog(first_post.post_id)
    print(updated_post.user_likes)
    mongo.delete_post_blog(first_post.post_id,user_id_owner=first_post.user_id_owner)
    mongo.get_post_blog(first_post.post_id) ## expected error