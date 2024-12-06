from flask import Flask
from flask_login import LoginManager
import os
from src.server.routes.messages import messages_bp
import src.db.repository as repository
from src.db.mongo_db.mongo_repository import MongoDBRepository
from src.server.routes.auth import auth_bp
import logging

logging.basicConfig(level=logging.INFO)
app:Flask = Flask(__name__)
login_manager:LoginManager = LoginManager()
repository.SERVER_REPOSITORY = MongoDBRepository()

@app.route('/')
def home():
    """
    Default home route
    """
    return "Welcome to Blog App home route!"

app.register_blueprint(messages_bp, url_prefix='/api/v0/messages')
app.register_blueprint(auth_bp, url_prefix='/api/v0/auth')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.getenv("FLASK_PORT", 5000)))




