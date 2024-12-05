import jwt
from datetime import timedelta, timezone
from src.server.flask_server.exceptions import AuthenticationError, UnauthorizedError, BlogAppException, ResourceNotFoundError
import src.database.repository as repository
import os
from src.database.odm_blog import User, Message
from datetime import datetime
from flask import request, app
from functools import wraps
import logging
from app import app
logging.basicConfig(level=logging.INFO)

##TODO## # update all environ to app configurations

def generate_jwt(user_id:str, password:str, roles: list[str])->str:
    payload = {
        'user_id': user_id,
        'password': password,
        'roles': roles,
        'exp': datetime.now(timezone.utc) + timedelta(seconds=app.config['JWT_EXPIRATION_TIME'])
    }
    token:str = jwt.encode(payload=payload, key=app.config['JWT_SECRET_KEY'], algorithm='HS256')
    return token


def decode_jwt(token: str):
    try:
        return jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid token")


def get_payload_from_request(request):
    token = None
    if 'Authorization' in request.headers:
        token = request.headers['Authorization'].split(" ")[1]
    if not token:
        raise AuthenticationError("Token is missing")
    return decode_jwt(token)


def valid_token_required(api_request):
    @wraps(api_request)
    def verify_token(*args, **kwargs):
        try:
            payload = get_payload_from_request(request)
            user_odm:User = repository.SERVER_REPOSITORY.get_user_blog(user_id=payload['user_id'])
            if payload['roles']!=[] and not set(payload['roles']).issubset(set(user_odm.roles)):
                raise AuthenticationError("Invalid User Roles")
        except BlogAppException as e:
            raise e
        except Exception as e:
            raise AuthenticationError("Bad Token") from e

        logging.info(f"Token verification success for {user_odm.user_id}")
        return api_request(*args, **kwargs)
    return verify_token


def role_required(required_role:str):
    def decorator(api_request):
        @wraps(api_request)
        def check_required_role(*args, **kwargs):
            payload = get_payload_from_request(request)
            roles_payload: list[str] = payload['roles']
            if required_role not in roles_payload:
                raise UnauthorizedError
            logging.info(f"User {payload['user_id']} has required role")
            return api_request(*args, **kwargs)
        return check_required_role
    return decorator


def message_user_id_owner_required(api_request):
    @wraps(api_request)
    def verify_message_owner(*args, **kwargs):
        payload = get_payload_from_request(request)
        user_id: str = payload['user_id']
        message_id:str = request.get_json().get('message_id','')
        message:Message = repository.SERVER_REPOSITORY.get_message_blog(message_id=message_id)
        if message.user_id_owner!=user_id:
            raise UnauthorizedError(f"User ID {user_id} is not owner of message_id {message_id}")

        logging.info(f"User {user_id} is verified as message owner of {message_id}")
        return api_request(*args, **kwargs)
    return verify_message_owner
