import flask
import gzip
from dotenv import load_dotenv

import os

from flask import request
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from app.routes.api_routes import api_blueprint
from app.shared.helpers.model_operations import ModelOperations
from app.shared.singletons.logger import Logger

load_dotenv(dotenv_path=os.path.join(os.getcwd(), '.env'))
Logger()

app = flask.Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})
app.register_blueprint(api_blueprint, url_prefix='/api/v1')
engine = create_engine(os.environ.get("DB_URL"))
Session = scoped_session(sessionmaker(bind=engine))

@app.before_request
def before_request():
    request.db_session = Session

@app.teardown_request
def teardown_request(exception=None):
    db_session = getattr(request, 'db_session', None)
    if db_session is not None:
        if exception:
            db_session.rollback()
        else:
            db_session.commit()
        db_session.close()
        db_session.remove()

@app.after_request
def after_request(request):
    if isinstance(request, flask.wrappers.Response):
        if request.mimetype == 'application/json':
            content = gzip.compress(flask.json.dumps(request.json).encode('utf8'))

            response = flask.make_response(content)

            response.headers = {
                "Content-Type": 'application/json',
                "Content-Encoding": 'gzip',
                "Content-length": len(content),
            }

            Logger().log(message=request.response[0], level='info' if response.status_code < 300 else 'error')

            return response

    return request
