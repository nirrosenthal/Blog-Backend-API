from typing import List
from dataclasses import dataclass, asdict, is_dataclass

@dataclass
class Message:
    message_id:str
    user_id_owner:str
    content:str
    user_likes:List[str]
    reply_to_message_id:str = None

@dataclass
class Post(Message):
    reply_to_message_id:str = None

@dataclass
class Comment(Message):
    reply_to_message_id:str
