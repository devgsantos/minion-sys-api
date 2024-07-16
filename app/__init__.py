import flask
import gzip
from dotenv import load_dotenv

import os

from app.routes.api_routes import api_blueprint
from app.shared.singletons.logger import Logger

load_dotenv(dotenv_path=os.path.join(os.getcwd(), '.env'))
Logger()

app = flask.Flask(__name__)
app.register_blueprint(api_blueprint, url_prefix='/api/v1')


@app.after_request
def after_request(request_response):
    if isinstance(request_response, flask.wrappers.Response):
        if request_response.mimetype == 'application/json':
            content = gzip.compress(flask.json.dumps(request_response.json).encode('utf8'))

            response = flask.make_response(content)

            if request_response.json.get('code'):
                response.status = request_response.json['code']

            response.headers = {
                "Content-Type": 'application/json',
                "Content-Encoding": 'gzip',
                "Content-length": len(content),
            }

            return response

    return request_response
