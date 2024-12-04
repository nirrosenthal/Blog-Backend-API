import jwt
from datetime import datetime, timedelta, timezone
from src.server.flask_server.app import app
from src.server.flask_server.authentication import Role

def generate_jwt(user_id:str, role:Role)->str:
    payload = {
        'user_id': user_id,
        'role': str(role),
        'exp': datetime.now(timezone.utc) + timedelta(seconds=app.config['JWT_EXPIRATION_TIME'])
    }
    token:str = jwt.encode(payload=payload, key=app.config['SECRET_KEY'], algorithm='HS256')
    return token


def verify_jwt(token:str)->bool:
    pass