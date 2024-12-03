from abc import ABC, abstractmethod
from typing import List
from src.database.odm_blog import Message, Post

class Repository(ABC):

    @abstractmethod
    def get_posts_blog(self, start_index:int = 0, posts_limit:int = -1)->List[Post]:
        pass

    @abstractmethod
    def get_message_blog(self, message_id:str, user_id_owner:str='')->Message:
        pass

    @abstractmethod
    def create_message_blog(self, content:str, user_id_owner: str, reply_to)->Message:
        pass

    @abstractmethod
    def edit_message_blog(self, message_id: str, edited_content:str)->Message:
        pass

    @abstractmethod
    def delete_message_blog(self, message_id:str)->Message:
        pass


    @abstractmethod
    def add_message_like(self, message_id:str, user_id:str)->bool:
        pass

    @abstractmethod
    def remove_message_like(self, message_id:str, user_id:str)->bool:
        pass
