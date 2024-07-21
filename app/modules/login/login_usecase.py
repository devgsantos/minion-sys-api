from datetime import datetime
from flask import request, jsonify, make_response
from app.shared.helpers.model_operations import ModelOperations
from app.shared.singletons.logger import Logger
from app.shared.helpers.token import Token
from models import LoginModel


class LoginUseCase:
    def __init__(self):
        self.logger = Logger()
        self.operations = ModelOperations()
        self.login_model = LoginModel

    def login(self):
        try:
            login = self.operations.findOne(self.login_model, email=request.json['email'], senha=request.json['senha'])
            if login:
                token = Token().generate(username=request.json.get('email'))
                self.operations.update(self.login_model, login.login_id, ultimo_login=datetime.now(), token=token.get('result'))

            return make_response(jsonify(
                {
                    'status': True,
                    'message': 'Autenticação realizada com sucesso.',
                    'data': token.get('result')
                }
            ), 200)

        except Exception as exc:
            self.logger.log(message=str(exc), level='error')

            return jsonify(
                {
                    'status': True,
                    'message': str(exc),
                    'data': None,
                }
            ), 500
