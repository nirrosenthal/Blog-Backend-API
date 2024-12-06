from flask import Blueprint, request, jsonify, make_response
from src.server.flask.exceptions import AuthenticationError, BlogAppException, InputValidationError
import src.db.repository as repository
from src.db.odm_blog import User
from src.server.routes.token import generate_jwt
import src.server.routes.input_validation as input_validation
import bcrypt
import logging
from typing import List

logging.basicConfig(level=logging.INFO)

auth_bp = Blueprint('auth',__name__)

def hash_password(password: str) -> str:
    """
    hash password to be stored in the database
    :param password: unhashed password
    :return: hashed password
    """
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')


def check_password(stored_hash: str, password: str) -> bool:
    """
    compare between stored_hash password and unhashed password using bycrypt
    :param stored_hash: database stored hashed password
    :param password: unhashed password
    :return: True if passwords are the same and False otherwise
    """
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))


def verify_credentials(user_id_input:str, password_input:str)-> bool:
    """
    Verify inputed user_id and password match information in database
    :param user_id_input: inputed unique user identifier
    :param password_input: inputed matching password
    :return: False if the user_id and password don't match
    :raise: ResourceNotFoundError if user_id doesn't exist in database
    """
    user:User = repository.SERVER_REPOSITORY.get_user_blog(user_id_input)
    return check_password(user.password, password_input)

@auth_bp.errorhandler(BlogAppException)
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



@auth_bp.route('login', methods=['POST'])
def login():
    """
    checks inputed user_id and password and sure they match database details
    :return: json response with generated JWT token for API calls
    :raise: AuthenticationError for invalid credentials
    """
    user_id = request.json.get('user_id','')
    password = request.json.get('password','')
    logging.info(f"User {user_id} Login started")
    try:
        input_validation.CredentialsValidation(user_id=user_id, password=password)
        if not verify_credentials(user_id, password):
            raise AuthenticationError("Invalid Credentials")
        user:User = repository.SERVER_REPOSITORY.get_user_blog(user_id)
    except Exception as e:
        logging.info(str(e))
        raise AuthenticationError("Invalid Credentials") from e

    token = generate_jwt(user.user_id, user.password, user.roles)
    logging.info(f"User {user_id} Login success, returning JWT")
    return jsonify({'token': token}), 200

@auth_bp.route('register', methods=['POST'])
def register():
    """
    create user_id, password user with inputed roles
    :return: empty json response success
    """
    user_id:str = request.json.get('user_id','')
    password:str = request.json.get('password','')
    name:str = request.json.get('name','')
    email:str = request.json.get('email','')
    roles:List[str] = request.json.get('roles',[])

    input_validation.CredentialsValidation(user_id=user_id, password=password)
    input_validation.RolesValidation(roles=roles)
    hashed_password:str = hash_password(password)
    repository.SERVER_REPOSITORY.create_user_blog(user_id=user_id, name=name, email=email,password=hashed_password,roles=roles)

    return make_response(f'User {user_id} created', 204)


@auth_bp.route('account/delete', methods=['DELETE'])
def delete_user_account():
    user_id:str = request.json.get('user_id','')
    user:User = repository.SERVER_REPOSITORY.delete_user_blog(user_id)
    if user is None:
        return jsonify({"message": f"User {user_id} doesn't exist"}), 200

    return make_response(f'User {user_id} removed', 204)
