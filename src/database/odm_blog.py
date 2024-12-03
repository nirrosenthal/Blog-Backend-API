from abc import ABC
from typing import List


class User:
    def __init__(self, user_name:str):
        self._user_name = user_name

    @property
    def user_name(self):
        return self._user_name


class Message(ABC):
    def __init__(self, message_id: str, user_id_owner: str, content:str, user_likes: List[User]):
        self._message_id = message_id
        self._user_id_owner = user_id_owner
        self._content = content
        self._user_likes = user_likes

    @property
    def message_id(self):
        return self._message_id
    @property
    def user_id_owner(self):
        return self._user_id_owner
    @property
    def content(self):
        return self._content
    @property
    def user_likes(self):
        return self._user_likes

class Post(Message):
    def __init__(self, post_id: str, user_id_owner: str, content: str, user_likes:List[User]):
        super().__init__(message_id = post_id, user_id_owner= user_id_owner, content=content, user_likes=user_likes)

    @property
    def post_id(self):
        return self.message_id

    def __getattr__(self, attr):
        return getattr(super(), attr)

class Comment(Message):
    def __init__(self, comment_id: str, user_id_owner: str, content: str, user_likes: List[User], reply_to_message_id: str):
        super().__init__(message_id = comment_id, user_id_owner= user_id_owner, content=content, user_likes=user_likes)
        self._reply_to_message_id = reply_to_message_id

    @property
    def comment_id(self):
        return super().message_id

    @property
    def reply_to_message_id(self):
        return self._reply_to_message_id

    def __getattr__(self, attr):
        return getattr(super(), attr)


