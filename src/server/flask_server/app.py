from flask import Flask
from flask_login import LoginManager
import os
from src.server.routes.messages import messages_bp
import src.database.repository as repository
from src.database.mongo_db.mongo_repository import MongoDBRepository
from src.server.routes.auth import auth_bp

app:Flask = Flask(__name__)
login_manager:LoginManager = LoginManager()

@app.route('/')
def home():
    return "Hello, Flask!"

app.register_blueprint(messages_bp, url_prefix='/api/v0/messages')
app.register_blueprint(auth_bp, url_prefix='/api/v0/auth')

def init_app():
    repository.SERVER_REPOSITORY = MongoDBRepository()
    app.config["JWT_EXPIRATION_TIME"] = os.getenv("JWT_EXPIRATION_DATE",3600)
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.run(debug=True,port=os.getenv("FLASK_PORT",5000))
    return app

if __name__ == '__main__':
    init_app()




