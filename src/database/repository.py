from abc import ABC, abstractmethod
from typing import List
from src.database.odm_blog import Post,Comment, User

class Repository(ABC):

    @abstractmethod
    def get_posts_blog(self, start_id:int =0, posts_limit:int = 50)->List[Post]:
        pass

    @abstractmethod
    def get_post_blog(self, post_id:str)->Post:
        pass

    @abstractmethod
    def create_post_blog(self, content:str, user_id_owner: str)->Post:
        pass

    @abstractmethod
    def edit_post_blog(self, post_id: str, new_content:str, user_id_owner: str)->Post:
        pass

    @abstractmethod
    def delete_post_blog(self, post_id:str, user_id_owner: str)->Post:
        pass

    @abstractmethod
    def get_comment_blog(self, comment_id:str)->Comment:
        pass

    @abstractmethod
    def create_comment_blog(self, content:str, reply_to_message_id:str, user_id_owner:str)->Comment:
        pass

    @abstractmethod
    def edit_comment_blog(self, comment_id:str, new_content: str, user_id_owner: str)->Comment:
        pass

    @abstractmethod
    def delete_comment_blog(self, comment_id:str, user_id_owner: str)->Comment:
        pass

    @abstractmethod
    def add_post_like(self, post_id:str, user_id:str)->bool:
        pass

    @abstractmethod
    def remove_post_like(self, post_id:str, user_id:str)->bool:
        pass

    @abstractmethod
    def add_comment_like(self, comment_id:str, user_id:str)->bool:
        pass

    @abstractmethod
    def remove_comment_like(self, comment_id:str, user_id:str)->bool:
        pass