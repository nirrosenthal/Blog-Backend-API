from bson import ObjectId
from bson.errors import InvalidId
from pydantic import BaseModel, Field, ValidationError, validator
import src.db.repository as repository
from src.server.flask.exceptions import InputValidationError
from typing import List

INPUT_LENGTH_LIMIT:int = 1000
POSTS_GET_LIMIT:int = 1000

class MessageId(BaseModel):
    """
    Validate input of type message_id
    """
    message_id: str = Field(...,min_length=1, max_length=INPUT_LENGTH_LIMIT)
    @validator('message_id')
    def validate_message_id(cls, message_id):
        try:
            ObjectId(message_id)
            return message_id
        except InvalidId as e:
            raise InputValidationError from e


class PostsGetRequest(BaseModel):
    """
    Validate input for a get posts request
    """
    start_index:int = Field(...,ge=0)
    posts_limit:int = Field(...,ge=0,le=POSTS_GET_LIMIT)


class MessageCreateRequest(BaseModel):
    """
    Validate input for a creating a message
    reply_to_message_id needs to be empty or a valid message_id that exists in database
    """
    content: str = Field(...,min_length=1, max_length=INPUT_LENGTH_LIMIT)
    user_id_owner: str = Field(...,min_length=1, max_length=INPUT_LENGTH_LIMIT)
    reply_to_message_id:str = None
    @validator('reply_to_message_id')
    def message_id_exists(cls, reply_to_message_id):
        try:
            if reply_to_message_id != '':
                ObjectId(reply_to_message_id)
                repository.SERVER_REPOSITORY.get_message_blog(reply_to_message_id)
            return reply_to_message_id
        except InvalidId as e:
            raise InputValidationError from e


class MessageEditRequest(BaseModel):
    """
    Validate input for a editing a message
    """
    message_id:MessageId
    content: str = Field(...,min_length=1, max_length=INPUT_LENGTH_LIMIT)


class MessageDeleteRequest(BaseModel):
    """
    Validate input for deleting a message
    """
    message_id:MessageId


class MessageLikeRequest(BaseModel):
    """
    Validate input for adding/removing a message like
    """
    message_id:MessageId
    user_id: str = Field(...,min_length=1, max_length=INPUT_LENGTH_LIMIT)

class CredentialsValidation(BaseModel):
    """
    Validate input for credentials
    """
    user_id: str = Field(...,min_length=1, max_length=INPUT_LENGTH_LIMIT)
    password: str = Field(...,min_length=1, max_length=INPUT_LENGTH_LIMIT)

class RolesValidation(BaseModel):
    """
    Validate input for list of roles
    """
    roles: List[str]