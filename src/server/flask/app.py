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

def init_app():
    repository.SERVER_REPOSITORY = MongoDBRepository()
    app.run(debug=True,port=os.getenv("FLASK_PORT",5000))
    logging.info(f"Flask app started running on port {os.getenv('FLASK_PORT')}")
    return app

if __name__ == '__main__':
    init_app()




