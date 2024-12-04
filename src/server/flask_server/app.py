from flask import Flask
from flask_login import LoginManager
import os
from src.server.routes.messages import messages_bp
import src.database.repository as repository
from src.database.mongo_db.mongo_repository import MongoDBRepository
from .authentication import auth_bp

app:Flask = Flask(__name__)
login_manager:LoginManager = LoginManager()
# app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SECRET_KEY'] = "temp_sercret_key_example"
app.config['JWT_EXPIRATION_TIME'] = 3600

@app.route('/')
def home():
    return "Hello, Flask!"

app.register_blueprint(messages_bp, url_prefix='/api/v0/messages')
app.register_blueprint(auth_bp, url_prefix="auth/")

def init_app():
    repository.SERVER_REPOSITORY = MongoDBRepository()
    app.run(debug=True)
    return app

if __name__ == '__main__':
    init_app()




