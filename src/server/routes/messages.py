from flask import Blueprint, request, jsonify, make_response, g ,app
from src.database.odm_blog import Post, Message
from dataclasses import asdict
import src.database.repository as repository
import src.server.flask_server.input_validation as Input_Validation
from pydantic import ValidationError
from src.server.flask_server.exceptions import InputValidationError, BlogAppException
from src.server.flask_server.authentication import valid_token_required,role_required,message_user_id_owner_required
import logging
from src.server.flask_server.authentication import get_payload_from_request

logging.basicConfig(level=logging.INFO)


messages_bp = Blueprint('messages',__name__)


@messages_bp.errorhandler(BlogAppException)
def handle_blog_app_exception(exception:BlogAppException):
    response = {
        "error": type(exception).__name__,
        "message": exception.message
    }
    return jsonify(response),exception.error_code


@role_required('post_user')
def verify_post_user_if_no_reply_to_message_id():
    pass


@messages_bp.route('posts',methods=['GET'])
@valid_token_required
def get_posts_blog():
    start_index = int(request.get_json().get('start_index',0))
    limit:int = int(request.get_json().get('limit',Input_Validation.POSTS_GET_LIMIT))
    try:
        Input_Validation.PostsGetRequest(start_index=start_index, posts_limit=limit)
        posts:list[Post] = repository.SERVER_REPOSITORY.get_posts_blog(start_index=start_index, posts_limit=limit)
    except ValidationError or TypeError as e:
        raise InputValidationError from e
    logging.info("GET Posts Blog success")
    return jsonify(posts), 200


@messages_bp.route('create', methods=['POST'])
@valid_token_required
def create_message_blog():
    payload = get_payload_from_request(request)
    user_id_owner:str = payload['user_id']
    content = request.get_json().get('content', '')
    reply_to_message_id = request.get_json().get('reply_to_message_id','')
    if reply_to_message_id=='':
        verify_post_user_if_no_reply_to_message_id()
    try:
        Input_Validation.MessageCreateRequest(user_id_owner=user_id_owner, content=content, reply_to_message_id=reply_to_message_id)

        created_message: Message = repository.SERVER_REPOSITORY.create_message_blog(content=content, user_id_owner=user_id_owner, reply_to_message_id=reply_to_message_id)
    except ValidationError or TypeError as e:
        raise InputValidationError from e
    logging.info(f"Created message {created_message.message_id} by {created_message.user_id_owner}")
    return jsonify(asdict(created_message)), 200


@messages_bp.route('edit',methods=['POST'])
@message_user_id_owner_required
@valid_token_required
def edit_message_blog():
    message_id = request.get_json().get('message_id','')
    content = request.get_json().get('content','')
    try:
        Input_Validation.MessageEditRequest(message_id={"message_id":message_id}, content=content)
        edited_message:Message = repository.SERVER_REPOSITORY.edit_message_blog(message_id, content)
    except ValidationError as e:
        raise InputValidationError from e

    return jsonify(asdict(edited_message)), 200



@messages_bp.route('delete', methods=['DELETE'])
@message_user_id_owner_required
@valid_token_required
def delete_message_blog():
    message_id = request.get_json().get('message_id','')
    try:
        Input_Validation.MessageDeleteRequest(message_id={"message_id":message_id})
        deleted_message:Message|None = repository.SERVER_REPOSITORY.delete_message_blog(message_id)
    except ValidationError as e:
        raise InputValidationError from e

    if deleted_message is None:
        return jsonify({"message": "Message doesn't exist in database"}),200
    return jsonify(asdict(deleted_message)), 200

@messages_bp.route('like/add', methods=['PUT'])
@valid_token_required
def add_message_like():
    payload = get_payload_from_request(request)
    user_id:str = payload['user_id']
    message_id = request.get_json().get('message_id','')
    try:
        Input_Validation.MessageLikeRequest(message_id={"message_id":message_id},user_id=user_id)
        repository.SERVER_REPOSITORY.add_message_like(message_id, user_id)
    except ValidationError as e:
        raise InputValidationError from e

    return make_response(f'User {user_id} Like Added', 204)

@messages_bp.route('like/remove', methods=['PUT'])
@valid_token_required
def remove_message_like():
    payload = get_payload_from_request(request)
    user_id:str = payload['user_id']
    message_id = request.get_json().get('message_id','')
    try:
        Input_Validation.MessageLikeRequest(message_id={"message_id":message_id},user_id=user_id)
        repository.SERVER_REPOSITORY.remove_message_like(message_id, user_id)
    except ValidationError as e:
        raise InputValidationError from e

    return make_response(f'User {user_id} Like Removed', 204)
