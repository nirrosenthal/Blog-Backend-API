from flask import Blueprint, request, jsonify
import src.server.flask_server.input_validation as Input_Validation
import src.database.repository as repository
from src.server.flask_server.jwt import generate_jwt
auth_bp = Blueprint('auth',__name__)


# from werkzeug.security import generate_password_hash, check_password_hash
# def hash_password(password:str)->str:
#     return generate_password_hash(password)

def verify_credentials(username:str,password:str)->bool:
    return True


@auth_bp.route('login/', methods=['POST'])
def login():
    username = request.json.get('username','')
    password = request.json.get('password','')

    # Here, implement your logic to authenticate the user
    user = repository.SERVER_REPOSITORY.get_user_blog(username)
    if user and user.password == password:  # Replace with actual password validation
        token = generate_jwt(user.id, user.role)
        return jsonify({'token': token}), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401