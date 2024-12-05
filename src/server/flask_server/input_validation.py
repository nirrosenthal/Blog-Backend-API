from bson import ObjectId
from bson.errors import InvalidId
from pydantic import BaseModel, Field, ValidationError, validator
import src.database.repository as repository
from src.server.flask_server.exceptions import InputValidationError

INPUT_LENGTH_LIMIT:int = 1000
POSTS_GET_LIMIT:int = 1000

class MessageId(BaseModel):
    message_id: str = Field(...,min_length=1, max_length=INPUT_LENGTH_LIMIT)
    @validator('message_id')
    def validate_message_id(cls, message_id):
        try:
            ObjectId(message_id)
            return message_id
        except InvalidId as e:
            raise InputValidationError from e


class PostsGetRequest(BaseModel):
    start_index:int = Field(...,ge=0)
    posts_limit:int = Field(...,ge=0,le=POSTS_GET_LIMIT)


class MessageGetRequest(BaseModel):
    user_id: str = ''


class MessageCreateRequest(BaseModel):
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
    message_id:MessageId
    content: str = Field(...,min_length=1, max_length=INPUT_LENGTH_LIMIT)


class MessageDeleteRequest(BaseModel):
    message_id:MessageId


class MessageLikeRequest(BaseModel):
    message_id:MessageId
    user_id: str = Field(...,min_length=1, max_length=INPUT_LENGTH_LIMIT)

class CredentialsValidation(BaseModel):
    user_id: str = Field(...,min_length=1, max_length=INPUT_LENGTH_LIMIT)
    password: str = Field(...,min_length=1, max_length=INPUT_LENGTH_LIMIT)



if __name__ == '__main__':
    print("done")