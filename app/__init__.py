import flask
import gzip
from dotenv import load_dotenv

import os

from flask import request
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from werkzeug.exceptions import HTTPException

from app.routes.api_routes import api_blueprint
from app.shared.config.database_url import normalize_database_url
from app.shared.helpers.model_operations import ModelOperations
from app.shared.helpers.http import INTERNAL_ERROR_MESSAGE, error_payload
from app.shared.singletons.logger import Logger

load_dotenv(dotenv_path=os.path.join(os.getcwd(), '.env'))
Logger()

app = flask.Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})
app.register_blueprint(api_blueprint, url_prefix='/api/v1')
engine = create_engine(
    normalize_database_url(os.environ["DB_URL"]),
    pool_size=5,  # Número de conexões que o pool vai manter abertas (ajuste conforme necessário)
    max_overflow=12,  # Número máximo de conexões além do `pool_size`
    pool_timeout=30,  # Tempo máximo de espera por uma conexão antes de lançar um erro
    pool_recycle=1800
)
Session = scoped_session(sessionmaker(bind=engine, autoflush=False, expire_on_commit=False))


def register_error_handlers(flask_app):
    @flask_app.errorhandler(HTTPException)
    def handle_http_error(exc):
        return flask.jsonify(error_payload(exc.description)), exc.code

    @flask_app.errorhandler(Exception)
    def handle_unexpected_error(exc):
        Logger().log(message=str(exc), level='error')
        return flask.jsonify(error_payload(INTERNAL_ERROR_MESSAGE)), 500


register_error_handlers(app)

@app.before_request
def before_request():
    request.db_session = Session

@app.teardown_request
def teardown_request(exception=None):
    db_session = getattr(request, 'db_session', None)
    if db_session is not None:
        try:
            if exception:
                db_session.rollback()  # Desfaz alterações em caso de erro
            else:
                db_session.commit()  # Confirma alterações
        finally:
            db_session.remove()

@app.after_request
def after_request(response):
    if isinstance(response, flask.wrappers.Response):
        if response.mimetype == 'application/json':
            # Usa o corpo da resposta original
            raw_data = response.get_data()
            content = gzip.compress(raw_data)
            compressed_response = flask.make_response(content, response.status_code)
            compressed_response.headers = dict(response.headers)
            compressed_response.headers["Content-Type"] = 'application/json'
            compressed_response.headers["Content-Encoding"] = 'gzip'
            # Remove Content-Length antigo, se existir, para evitar duplicidade
            compressed_response.headers.pop("Content-Length", None)
            Logger().log(
                message=f'status={response.status_code}',
                level='info' if response.status_code < 400 else 'error',
            )
            return compressed_response
    return response
