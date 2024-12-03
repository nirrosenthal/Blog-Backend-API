from flask import Blueprint, request, jsonify
from src.database.odm_blog import Post, Message
from dataclasses import asdict
from src.database.repository import Repository
import src.server.flask_server.input_validation as Input_Validation
from pydantic import ValidationError

messages_bp = Blueprint('messages',__name__)


@messages_bp.route('create', methods=['POST'])
def create_message_blog():
    content = request.get_json().get('content', '')
    user_id_owner = request.get_json().get('user_id_owner','')
    try:
        Input_Validation.MessageCreateRequest(user_id_owner=user_id_owner, content=content)
        created_message: Message = Repository().create_message_blog(content, user_id_owner)
        return jsonify(asdict(created_message)), 200
    except ValidationError:
        return jsonify({"error":"Validation error"})

@messages_bp.route('edit',methods=['POST'])
def edit_message_blog():
    message_id = request.get_json().get('message_id','')
    content = request.get_json().get('content','')
    try:
        Input_Validation.MessageEditRequest(message_id=message_id, content=content)
        edited_message:Message = Repository().edit_message_blog(message_id, content)

        return jsonify(asdict(edited_message)), 200
    except ValidationError:
        return jsonify({"error":"Validation Error"})


@messages_bp.route('delete', methods=['DELETE'])
def delete_message_blog():
    message_id = request.get_json().get('message_id','')
    try:
        Input_Validation.MessageDeleteRequest(message_id)
        deleted_message:Message = Repository().delete_message_blog(message_id)
        return jsonify(asdict(deleted_message)), 200
    except ValidationError:
        return jsonify({"error":"Validation Error"})


@messages_bp.route('like/add', methods=['PUT'])
def add_message_like():
    message_id = request.get_json().get('message_id','')
    user_id = "need to get curr user id"
    try:
        Input_Validation.MessageLikeRequest(message_id,user_id)
        Repository().add_message_like(message_id, user_id)
    except ValidationError:
        return jsonify({"error":"Validation Error"})


@messages_bp.route('like/add', methods=['PUT'])
def remove_message_like():
    message_id = request.get_json().get('message_id','')
    user_id = "need to get curr user id"
    try:
        Input_Validation.MessageLikeRequest(message_id,user_id)
        Repository().remove_message_like(message_id, user_id)
    except ValidationError:
        return jsonify({"error":"Validation Error"})
