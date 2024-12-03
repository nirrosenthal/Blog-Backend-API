from abc import ABC, abstractmethod
from typing import List
from odm_blog import Post,Comment, User

class Repository(ABC):

    @abstractmethod
    def get_posts_blog(self)->List[Post]:
        pass

    @abstractmethod
    def create_post_blog(self, content:str, user_id_owner: str)->Post:
        pass

    def edit_post_blog(self, post_id: str, new_content:str, user_id_owner: str)->Post:
        pass

    @abstractmethod
    def delete_post_blog(self, post_id:str, user_id_owner: str)->Post:
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

    ### what should I return from these messages
    @abstractmethod
    def add_message_like(self, message_id:str, user_id:str)->bool:
        pass

    @abstractmethod
    def remove_message_like(self, message_id:str, user_id:str)->bool:
        pass