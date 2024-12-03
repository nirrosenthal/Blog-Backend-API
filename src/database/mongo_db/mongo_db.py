from ..odm_blog import Post,Comment
from ..repository import Repository
from typing import List
from pymongo import MongoClient
from bson import ObjectId

READ_WRITE_USER = "root_example"
READ_WRITE_PASSWORD = "password_example"
MONGO_PORT = "27017"
MONGO_HOST = "localhost"
# MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME", "root_example")
# MONGO_PASSWORD = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "password_example")
# MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
# MONGO_PORT = os.getenv("MONGO_PORT", "27017")

CONNECTION_STRING = f"mongodb://{READ_WRITE_USER}:{READ_WRITE_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/"

class MongoDBRepository(Repository):

    def __init__(self):
        self._client = MongoClient(CONNECTION_STRING)
        self._messages_db = self._client["messages"]
        self._messages_db.create_index(
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

    def get_posts_blog(self)->List[Post]:
        pass


    def get_post_blog(self, post_id:str) ->Post:
        post_data = self._messages_db.find_one({"_id": ObjectId(post_id)})
        return MongoDBRepository._create_post_with_post_data(post_data)


    def create_post_blog(self, content:str, user_id_owner: str)->Post:
        new_post = {
            "content": content,
            "user_id_owner": user_id_owner,
            "user_likes": [],
        }

        created_post_result = self._messages_db.insert_one(new_post)
        post_data = self._messages_db.find_one({"_id": created_post_result.inserted_id})

        return MongoDBRepository._create_post_with_post_data(post_data)


    def edit_post_blog(self, post_id: str, new_content:str, user_id_owner: str)->Post:
        post_id_obj = ObjectId(post_id)
        edited_post_data = self._messages_db.update_one({"_id": post_id_obj},
                                           {"$set": {"content": new_content}},
                                           return_document=True)

        return MongoDBRepository._create_post_with_post_data(edited_post_data)


    def delete_post_blog(self, post_id:str, user_id_owner: str)->Post:
        post_id_obj = ObjectId(post_id)
        post_to_delete = self._messages_db.find_one({"_id": post_id_obj})
        reply_comments_to_delete = self._messages_db.find({"reply_to_message_id": post_id_obj})
        for comment in reply_comments_to_delete:
            self.delete_comment_blog(comment["_id"], comment["user_id_owner"])

        self._messages_db.delete_one({"_id": post_id_obj})

        return MongoDBRepository._create_post_with_post_data(post_to_delete)


    def get_comment_blog(self, comment_id:str) ->Comment:
        comment_data = self._messages_db.find_one({"_id": ObjectId(comment_id)})
        return MongoDBRepository._create_comment_with_comment_data(comment_data)


    def create_comment_blog(self, content:str, reply_to_message_id:str, user_id_owner:str)->Comment:
        new_comment = {
            "content": content,
            "user_id_owner": user_id_owner,
            "user_likes": [],
            "reply_to_message_id": ObjectId(reply_to_message_id)
        }

        created_comment_result = self._messages_db.insert_one(new_comment)
        comment_data = self._messages_db.find_one({"_id": created_comment_result.inserted_id})
        return MongoDBRepository._create_comment_with_comment_data(comment_data)


    def edit_comment_blog(self, comment_id:str, new_content: str, user_id_owner: str)->Comment:
        comment_id_obj = ObjectId(comment_id)
        edited_comment_data = self._messages_db.update_one({"_id": comment_id_obj},
                                                        {"$set": {"content": new_content}},
                                                        return_document=True)

        return MongoDBRepository._create_comment_with_comment_data(edited_comment_data)


    def delete_comment_blog(self, comment_id:str, user_id_owner: str)->Comment:
        comment_id_obj = ObjectId(comment_id)
        comment_to_delete = self._messages_db.find_one({"_id": comment_id_obj})
        reply_comments_to_delete = self._messages_db.find({"reply_to_message_id": comment_id_obj})
        for comment in reply_comments_to_delete:
            self.delete_comment_blog(comment["_id"], comment["user_id_owner"])

        self._messages_db.delete_one({"_id": comment_id_obj})

        return MongoDBRepository._create_comment_with_comment_data(comment_to_delete)


    def add_message_like(self, message_id: str, user_id: str) -> bool:
        message_id_obj = ObjectId(message_id)
        message = self._messages_db.find_one({"_id": message_id_obj})

        if not message or user_id in message.get("user_likes", []):
            return False

        self._messages_db.update_one(
            {"_id": message_id_obj},
            {"$push": {"user_likes": user_id}}
        )
        return True


    def remove_message_like(self, message_id: str, user_id: str) -> bool:
        message_id_obj = ObjectId(message_id)
        message = self._messages_db.find_one({"_id": message_id_obj})

        if not message or user_id not in message.get("user_likes", []):
            return False

        self._messages_db.update_one(
            {"_id": message_id_obj},
            {"$pull": {"user_likes": user_id}}
        )
        return True