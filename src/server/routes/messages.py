from flask import Blueprint, request, jsonify, make_response
from src.db.odm_blog import Post, Message
from dataclasses import asdict
import src.db.repository as repository
from pydantic import ValidationError
from src.server.flask.exceptions import InputValidationError, BlogAppException
from src.server.routes.token import valid_token_required,role_required,message_user_id_owner_required
import logging
from src.server.routes.token import get_payload_from_request
from typing import Union
logging.basicConfig(level=logging.INFO)


messages_bp = Blueprint('messages',__name__)


@messages_bp.errorhandler(BlogAppException)
def handle_blog_app_exception(exception:BlogAppException):
    """
    Returns any error raised as a failed JSON response
    :param exception: BlogAppException that lead to request failure
    :return: json with error code and message
    """
    response = {
        "error": type(exception).__name__,
        "message": exception.message
    }
    return jsonify(response),exception.error_code


@role_required('post_user')
def __verify_post_user_if_no_reply_to_message_id():
    """
    Verify if user_id can create posts
    :return: None
    :raise: UnauthorizedError if user doesn't have post_user role
    """
    pass


@messages_bp.route('posts',methods=['GET'])
@valid_token_required
def get_posts_blog():
    """
    Get a lists of Posts that exist in the blog database
    :return: json response with a list of Post objects
    """
    start_index = int(request.get_json().get('start_index',0))
    limit:int = int(request.get_json().get('limit', input_validation.POSTS_GET_LIMIT))
    try:
        input_validation.PostsGetRequest(start_index=start_index, posts_limit=limit)
        posts:list[Post] = repository.SERVER_REPOSITORY.get_posts_blog(start_index=start_index, posts_limit=limit)
    except ValidationError or TypeError as e:
        raise InputValidationError from e
    logging.info("GET Posts Blog success")
    return jsonify(posts), 200


@messages_bp.route('create', methods=['POST'])
@valid_token_required
def create_message_blog():
    """
    Creates a message in the blog database.
    Message could be a Post or Comment based on reply_to_message_id
    :return: json response with created Post/Comment
    """
    payload = get_payload_from_request(request)
    user_id_owner:str = payload['user_id']
    content = request.get_json().get('content', '')
    reply_to_message_id = request.get_json().get('reply_to_message_id','')
    if reply_to_message_id=='':
        __verify_post_user_if_no_reply_to_message_id()
    try:
        input_validation.MessageCreateRequest(user_id_owner=user_id_owner, content=content, reply_to_message_id=reply_to_message_id)

        created_message: Message = repository.SERVER_REPOSITORY.create_message_blog(content=content, user_id_owner=user_id_owner, reply_to_message_id=reply_to_message_id)
    except ValidationError or TypeError as e:
        raise InputValidationError from e
    logging.info(f"Created message {created_message.message_id} by {created_message.user_id_owner}")
    return jsonify(asdict(created_message)), 200


@messages_bp.route('edit',methods=['POST'])
@message_user_id_owner_required
@valid_token_required
def edit_message_blog():
    """
    Edits a message that requesting user owns.
    :return: json response with edited Post/Comment
    """
    message_id = request.get_json().get('message_id','')
    content = request.get_json().get('content','')
    try:
        input_validation.MessageEditRequest(message_id={"message_id":message_id}, content=content)
        edited_message:Message = repository.SERVER_REPOSITORY.edit_message_blog(message_id, content)
    except ValidationError as e:
        raise InputValidationError from e

    return jsonify(asdict(edited_message)), 200



@messages_bp.route('delete', methods=['DELETE'])
@message_user_id_owner_required
@valid_token_required
def delete_message_blog():
    """
    Delete a message that requesting user owns.
    :return: json response with deleted Post/Comment or None if message doesn't exist
    """
    message_id = request.get_json().get('message_id','')
    try:
        input_validation.MessageDeleteRequest(message_id={"message_id":message_id})
        deleted_message:Union[Message|None] = repository.SERVER_REPOSITORY.delete_message_blog(message_id)
    except ValidationError as e:
        raise InputValidationError from e

    if deleted_message is None:
        return jsonify({"message": "Message doesn't exist in db"}),200
    return jsonify(asdict(deleted_message)), 200

@messages_bp.route('like/add', methods=['PUT'])
@valid_token_required
def add_message_like():
    """
    Add like to message from user, no error if user already likes message
    :return: empty json response
    """
    payload = get_payload_from_request(request)
    user_id:str = payload['user_id']
    message_id = request.get_json().get('message_id','')
    try:
        input_validation.MessageLikeRequest(message_id={"message_id":message_id}, user_id=user_id)
        repository.SERVER_REPOSITORY.add_message_like(message_id, user_id)
    except ValidationError as e:
        raise InputValidationError from e

    return make_response(f'User {user_id} Like Added', 204)

@messages_bp.route('like/remove', methods=['PUT'])
@valid_token_required
def remove_message_like():
    """
    Remove like to message from user, no error if user doesn't like message
    :return: empty json response
    """
    payload = get_payload_from_request(request)
    user_id:str = payload['user_id']
    message_id = request.get_json().get('message_id','')
    try:
        input_validation.MessageLikeRequest(message_id={"message_id":message_id}, user_id=user_id)
        repository.SERVER_REPOSITORY.remove_message_like(message_id, user_id)
    except ValidationError as e:
        raise InputValidationError from e

    return make_response(f'User {user_id} Like Removed', 204)
