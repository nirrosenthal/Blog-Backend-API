from abc import ABC, abstractmethod
from typing import List, Optional, Union
from src.db.odm_blog import Message, Post, User

SERVER_REPOSITORY:Optional['Repository'] = None

class Repository(ABC):

    @abstractmethod
    def get_posts_blog(self, posts_limit:int, start_index:int = 0)->List[Post]:
        """
        Get Lists of up to posts_limit posts from the db starting from start_index position
        :param posts_limit: post limit for pagination
        :param start_index: starting post index
        :return: list of Post objects retrieved from db
        :raises DatabaseError if db operation fail
        """
        pass


    @abstractmethod
    def get_message_blog(self, message_id:str, user_id_owner:str='')->Message:
        """
        Get message from db.
        :param message_id: unique identifier for message in db
        :param user_id_owner: optional unique identifier for user
        :return:
        :raises:
            ResourceNotFoundError if message doesn't exist in db
            DatabaseError for DB operation fail
        """
        pass


    @abstractmethod
    def create_message_blog(self, content:str, user_id_owner: str, reply_to_message_id:str)->Message:
        """
        Create message and return Message with db message_id
        :param content: message text field
        :param user_id_owner: unique user_id of message creator
        :param reply_to_message_id: message_id of message being replied
        :return: Message object with message_id
        :raises: DatabaseError for DB operation fail
        """
        pass


    @abstractmethod
    def edit_message_blog(self, message_id: str, edited_content:str)->Message:
        """
        Change content field of message, and updated message
        :param message_id: unique identifier for message
        :param edited_content: message text field to be updated
        :return: Message object with edited content
        :raises:
            ResourceNotFoundError if message_id doesn't exist in DB
            DatabaseError for DB operation fail
        """
        pass


    @abstractmethod
    def delete_message_blog(self, message_id:str)->Union[Message,None]:
        """
        Delete message from db, and any other comments that replied to that message
        No error if message doesn't exist
        :param message_id: unique identifier for message
        :return: Message object of deleted message, or None if already doesn't exist
        :raises DatabaseError for DB operation fail
        """
        pass

    ### no errors if like already exists
    @abstractmethod
    def add_message_like(self, message_id:str, user_id:str)->bool:
        """
        Add the user_id to message Likes.
        Does not verify user_id.
        No error if user_id exists in like list
        :param message_id: unique identifier for message
        :param user_id: unique user identifier to add to likes
        :return: True if operation succeeded
        :raises
            DatabaseError for DB operation fail
        """
        pass


    @abstractmethod
    def remove_message_like(self, message_id:str, user_id:str)->bool:
        """
        Remove the user_id from message Likes
        Does not verify user_id.
        No error if user_id doesn't exist in like list
        :param message_id: unique identifier for message
        :param user_id: unique user identifier to remove from likes
        :return: True if operation succeeded
        :raises
            DatabaseError for DB operation fail
        """
        pass


    @abstractmethod
    def create_user_blog(self, user_id: str, password:str, email:str, name:str, roles:List[str])->User:
        """
        Create new user_id in Database
        :param user_id: unique identifier for user
        :param password: hashed password
        :param email: email address
        :param name: username
        :param roles: list of permitted roles for user
        :return: User object based on created record
        :raises:
            DatabaseError for operation fail or if user already exists
        """
        pass


    @abstractmethod
    def get_user_blog(self, user_id:str)->User:
        """
        Get User object from Database
        :param user_id: unique identifier for user
        :return: User Object with properties from db
        :raises:
            DatabaseError for DB operation fail
            ResourceNotFound for user_id that isn't found
        """
        pass


    @abstractmethod
    def update_user_details_blog(self, user_id: str,password:str = '', email:str = '', name:str= '')->User:
        """
        Update fields for user_id inserted.
        Default '' value won't be updated
        :param user_id: unique identifier for user
        :param password: hashed password
        :param email: email address
        :param name: username
        :return: User object with updated properties
        :raises:
            DatabaseError for DB operation fail
            ResourceNotFound for user_id that isn't found
        """
        pass


    @abstractmethod
    def delete_user_blog(self, user_id:str)->Union[User,None]:
        """
        Delete user from Database
        :param user_id: unique identifier for user
        :return: User obejct of deleted user or None if user is already deleted
        :raise DatabaseError for DB operation fail
        """
        pass


    @abstractmethod
    def add_user_role(self, user_id:str, role: str)->bool:
        """
        Add role to user, no errors if user already has role
        :param user_id: unique identifier for user
        :param role: role to add to user roles
        :return: True if action succeeded
        :raise: DatabaseError for DB operation fail
        """
        pass

    @abstractmethod
    def remove_user_role(self, user_id:str, role:str)->bool:
        """
        Add role to user, no errors if user doesn't have role
        :param user_id: unique identifier for user
        :param role: role to add to user roles
        :return: True if action succeeded
        :raise: DatabaseError for DB operation fail
        """
        pass