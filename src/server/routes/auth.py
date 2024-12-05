from flask import Blueprint, request, jsonify
import src.server.flask_server.input_validation as Input_Validation
from src.server.flask_server.exceptions import AuthenticationError
import src.database.repository as repository
from src.database.odm_blog import User
from src.server.flask_server.authentication import generate_jwt
import bcrypt

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


@auth_bp.route('login', methods=['POST'])
def login():
    user_id = request.json.get('user_id','')
    password = request.json.get('password','')
    try:
        Input_Validation.CredentialsValidation(user_id=user_id,password=password)
        if not verify_credentials(user_id, password):
            raise AuthenticationError("Invalid Credentials")
        user:User = repository.SERVER_REPOSITORY.get_user_blog(user_id)
    except ValidationError or TypeError as e:
        raise AuthenticationError("Invalid Credentials") from e

    token = generate_jwt(user.user_id, user.roles)
    return jsonify({'token': token}), 200