import jwt
from datetime import timedelta, timezone
from src.server.flask.exceptions import AuthenticationError, UnauthorizedError, BlogAppException, ResourceNotFoundError
import src.db.repository as repository
from src.db.odm_blog import User, Message
from datetime import datetime
from flask import request, Flask
from functools import wraps
import logging
import os
from typing import List

logging.basicConfig(level=logging.INFO)

jwt_algorithm:str = 'HS256'

def generate_jwt(user_id:str, password:str, roles: List[str])->str:
    """
    Generate jwt token based on environment variables JWT_SECRET_KEY,JWT_EXPIRATION_TIME
    :param user_id: user_id of generated token
    :param password: hashed password from database
    :param roles: role permissions for user_id
    :return: jwt token
    """
    payload = {
        'user_id': user_id,
        'password': password,
        'roles': roles,
        'exp': datetime.now(timezone.utc) + timedelta(seconds=os.environ.get('JWT_EXPIRATION_TIME',3600))
    }
    token:str = jwt.encode(payload=payload, key=os.environ.get('JWT_SECRET_KEY'), algorithm=jwt_algorithm)
    return token


def decode_jwt(token: str):
    """
    Decode jwt token to return the payload
    :param token: jwt token
    :return: jwt payload
    :raises: AuthenticationError if token if not valid
    """
    try:
        return jwt.decode(token, os.environ.get('JWT_SECRET_KEY'), algorithms=[jwt_algorithm])
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid token")


def get_payload_from_request(request):
    """
    Get jwt token from http request and decode payload
    :param request: http request
    :return: payload
    :raises AuthenticationError if jwt is not valid
    """
    token = None
    if 'Authorization' in request.headers:
        token = request.headers['Authorization'].split(" ")[1]
    if not token:
        raise AuthenticationError("Token is missing")
    return decode_jwt(token)


def valid_token_required(api_request):
    """
    Decorator to verify JWT token is valid:
     - valid and not expired
     - contains legal role permissions for user_id

    :param api_request: api function request to be performed
    :return: api_request function
    :raises AuthenticationError if token or roles are invalid
            BlogAppException for missing payload property
    """
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
    """
    Decorator to verify required role is included in jwt
    :param required_role: role needed for api_request
    :return: decorator for function of api request
    """
    def decorator(api_request):
        @wraps(api_request)
        def check_required_role(*args, **kwargs):
            payload = get_payload_from_request(request)
            roles_payload: List[str] = payload['roles']
            if required_role not in roles_payload:
                raise UnauthorizedError
            logging.info(f"User {payload['user_id']} has required role")
            return api_request(*args, **kwargs)
        return check_required_role
    return decorator


def message_user_id_owner_required(api_request):
    """
    Decorator to verify user_id_owner of the message_id input matches user_id from jwt
    :param api_request: function of api request
    :return: api_request
    :raise: UnathorizedError if user_id is not message owner
    """
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
