from pydantic import BaseModel, Field, ValidationError, validator

INPUT_LENGTH_LIMIT = 1000


class MessageGetRequest(BaseModel):
    message_id: str = Field(...,min_length=1, max_length=INPUT_LENGTH_LIMIT)
    user_id: str = ''


class MessageCreateRequest(BaseModel):
    content: str = Field(...,min_length=1, max_length=INPUT_LENGTH_LIMIT)
    user_id_owner: str = Field(...,min_length=1, max_length=INPUT_LENGTH_LIMIT)
    reply_to_message_id: str =  Field(...,min_length=1, max_length=INPUT_LENGTH_LIMIT)


class MessageEditRequest(BaseModel):
    message_id: str = Field(...,min_length=1, max_length=INPUT_LENGTH_LIMIT)
    content: str = Field(...,min_length=1, max_length=INPUT_LENGTH_LIMIT)


class MessageDeleteRequest(BaseModel):
    message_id: str = Field(...,min_length=1, max_length=INPUT_LENGTH_LIMIT)


class MessageLikeRequest(BaseModel):
    message_id: str = Field(...,min_length=1, max_length=INPUT_LENGTH_LIMIT)
    user_id: str = Field(...,min_length=1, max_length=INPUT_LENGTH_LIMIT)


if __name__ == '__main__':
    print("done")