from flask import Flask
from flask_login import LoginManager
import os
from src.server.routes.messages import messages_bp
import src.database.repository as repository
from src.database.mongo_db.mongo_repository import MongoDBRepository
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
#
#
# def flask_app_run():
#     """Custom run command to make sure repository will run first"""
#     init_database_repository()
#     app.run(host="0.0.0.0", port=int(os.getenv("FLASK_PORT", 5000)))
#     logging.info(f"Flask app started running on port {os.getenv('FLASK_PORT')}")
#     return app

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.getenv("FLASK_PORT", 5000)))




