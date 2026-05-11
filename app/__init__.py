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
engine = create_engine(
    os.environ.get("DB_URL"),
    pool_size=5,  # Número de conexões que o pool vai manter abertas (ajuste conforme necessário)
    max_overflow=12,  # Número máximo de conexões além do `pool_size`
    pool_timeout=30,  # Tempo máximo de espera por uma conexão antes de lançar um erro
    pool_recycle=1800
)
Session = scoped_session(sessionmaker(bind=engine, autoflush=False, expire_on_commit=False))

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
def after_request(request):
    if isinstance(request, flask.wrappers.Response):
        if request.mimetype == 'application/json':
            # Usa o corpo da resposta original
            raw_data = request.get_data()
            content = gzip.compress(raw_data)
            response = flask.make_response(content, request.status_code)
            response.headers = dict(request.headers)
            response.headers["Content-Type"] = 'application/json'
            response.headers["Content-Encoding"] = 'gzip'
            # Remove Content-Length antigo, se existir, para evitar duplicidade
            response.headers.pop("Content-Length", None)
            Logger().log(message=raw_data, level='info' if response.status_code < 300 else 'error')
            return response
    return request
