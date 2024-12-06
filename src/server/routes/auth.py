import traceback

from flask import Blueprint, request, jsonify, g, app
import src.server.flask.input_validation as Input_Validation
from src.server.flask.exceptions import AuthenticationError, BlogAppException
import src.db.repository as repository
from src.db.odm_blog import User
from src.server.flask.token import generate_jwt
import bcrypt
import logging


logging.basicConfig(level=logging.INFO)

auth_bp = Blueprint('auth',__name__)

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')


def check_password(stored_hash: str, password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))


def verify_credentials(user_id:str,password_input:str)-> bool:
    user:User = repository.SERVER_REPOSITORY.get_user_blog(user_id)
    return check_password(user.password, password_input)

@auth_bp.errorhandler(BlogAppException)
def handle_blog_app_exception(exception:BlogAppException):
    response = {
        "error": type(exception).__name__,
        "message": exception.message
    }
    return jsonify(response),exception.error_code



@auth_bp.route('login', methods=['POST'])
def login():
    user_id = request.json.get('user_id','')
    password = request.json.get('password','')
    logging.info(f"User {user_id} Login started")
    try:
        Input_Validation.CredentialsValidation(user_id=user_id,password=password)
        if not verify_credentials(user_id, password):
            raise AuthenticationError("Invalid Credentials")
        user:User = repository.SERVER_REPOSITORY.get_user_blog(user_id)
    except Exception as e:
        logging.info(str(e))
        raise AuthenticationError("Invalid Credentials") from e

    token = generate_jwt(user.user_id, user.password, user.roles)
    logging.info(f"User {user_id} Login success, returning JWT")
    return jsonify({'token': token}), 200