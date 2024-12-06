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

@app.route('/')
def home():
    return "Hello, Flask!"

app.register_blueprint(messages_bp, url_prefix='/api/v0/messages')
app.register_blueprint(auth_bp, url_prefix='/api/v0/auth')

@app.cli.command("init-repository")
def init_database_repository():
    repository.SERVER_REPOSITORY = MongoDBRepository()
    logging.info(f"Database Repository Initiated")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.getenv("FLASK_PORT", 5000)))




