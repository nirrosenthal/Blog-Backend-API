from flask import Flask, jsonify

from src.server.flask_server.exceptions import BlogAppException, InputValidationError
from src.server.flask_server.routes import messages_bp
import src.database.repository as repository
from src.database.mongo_db.mongo_repository import MongoDBRepository

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, Flask!"

app.register_blueprint(messages_bp, url_prefix='/api/v0/messages')


if __name__ == '__main__':
    repository.SERVER_REPOSITORY = MongoDBRepository()
    app.run(debug=True)





