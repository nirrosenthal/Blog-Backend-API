from typing import List
from dataclasses import dataclass

@dataclass
class Message:
    """
    Represents a message in the blog
    """
    message_id:str
    user_id_owner:str
    content:str
    user_likes:List[str]
    reply_to_message_id:str = None

@dataclass
class Post(Message):
    """
    A message with no reply_to_message_id
    """
    reply_to_message_id:str = None

@dataclass
class Comment(Message):
    """
    A message that originated form a reply_to_message_id
    """
    reply_to_message_id:str

@dataclass
class User:
    """
    Represent a user in the db
    """
    user_id:str
    email:str
    name:str
    password:str
    roles:List[str]

