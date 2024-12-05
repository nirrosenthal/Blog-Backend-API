import jwt
from datetime import timedelta, timezone
from src.server.flask_server.exceptions import AuthenticationError, UnauthorizedError, BlogAppException, ResourceNotFoundError
import src.database.repository as repository
import os
from src.database.odm_blog import User
from datetime import datetime
from flask import request
from functools import wraps


def generate_jwt(user_id:str, password:str, roles: list[str])->str:
    payload = {
        'user_id': user_id,
        'password': password,
        'roles': roles,
        'exp': datetime.now(timezone.utc) + timedelta(seconds=int(os.environ.get('JWT_EXPIRATION_TIME')))
    }
    token:str = jwt.encode(payload=payload, key=os.environ.get('SECRET_KEY'), algorithm='HS256')
    return token


def decode_jwt(token: str):
    try:
        return jwt.decode(token, os.environ.get('SECRET_KEY'), algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid token")


def valid_token_required(api_request):
    @wraps(api_request)
    def verify_token(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            raise AuthenticationError("Token is missing")
        try:
            payload = decode_jwt(token)
            request.user_id = payload['user_id']
            request.roles = payload['roles']
            user:User = repository.SERVER_REPOSITORY.get_user_blog(user_id=request.user_id)
            if set(user.roles) != set(request.roles):
                raise AuthenticationError("Invalid User Roles")
        except Exception as e:
            raise AuthenticationError("Bad Token") from e

        return api_request(*args, **kwargs)

    return verify_token


def role_required(required_role:str):
    def decorator(api_request):
        @wraps(api_request)
        def check_required_role(*args, **kwargs):
            if required_role not in request.get_json().get('roles', []):
                raise UnauthorizedError
            return api_request(*args, **kwargs)
        return check_required_role
    return decorator


def message_user_id_owner_required(api_request):
    def decorator(api_request):
        @wraps(api_request)
        def verify_message_owner(*args, **kwargs):
            message_id:str = request.get_json().get('message_id','')
            user_id:str = request.get_json().get('user_id')
            try:
                repository.SERVER_REPOSITORY.get_message_blog(message_id=message_id, user_id_owner=user_id)
            except ResourceNotFoundError:
                raise UnauthorizedError(f"User ID {user_id} is not owner of message_id {message_id}")
            return api_request(*args, **kwargs)
        return verify_message_owner
    return decorator