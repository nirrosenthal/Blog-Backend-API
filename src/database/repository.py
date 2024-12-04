from abc import ABC, abstractmethod
from typing import List, Optional
from src.database.odm_blog import Message, Post, User

SERVER_REPOSITORY:Optional['Repository'] = None

class Repository(ABC):

    @abstractmethod
    def get_posts_blog(self, posts_limit:int, start_index:int = 0, **kwargs)->List[Post]:
        pass

    @abstractmethod
    def get_message_blog(self, message_id:str, user_id_owner:str='')->Message:
        pass

    @abstractmethod
    def create_message_blog(self, content:str, user_id_owner: str, reply_to_message_id:str)->Message:
        pass

    @abstractmethod
    def edit_message_blog(self, message_id: str, edited_content:str)->Message:
        pass

    @abstractmethod
    def delete_message_blog(self, message_id:str)->Message|None:
        pass


    @abstractmethod
    def add_message_like(self, message_id:str, user_id:str)->bool:
        pass

    @abstractmethod
    def remove_message_like(self, message_id:str, user_id:str)->bool:
        pass

    @abstractmethod
    def create_user_blog(self, user_id: str, email:str, name:str, roles:list[str])->User:
        pass

    @abstractmethod
    def get_user_blog(self, user_id:str)->User:
        pass

    @abstractmethod
    def update_user_details_blog(self, user_id: str, email:str, name:str)->User:
        pass

    @abstractmethod
    def delete_user_blog(self, user_id:str)->User|None:
        pass


    @abstractmethod
    def add_user_role(self, user_id:str, role: str)->bool:
        pass

    @abstractmethod
    def remove_user_role(self, user_id:str, role:str)->bool:
        pass