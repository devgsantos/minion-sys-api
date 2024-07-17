from datetime import datetime
from flask import request, jsonify
from app.shared.helpers.model_operations import ModelOperations
from app.shared.singletons.logger import Logger
from app.shared.helpers.token import Token
from models import LoginModel


class LoginUseCase:
    def __init__(self):
        self.logger = Logger()
        self.operations = ModelOperations
        self.login_model = LoginModel

    def login(self):
        try:
            user = self.operations.findOne(self.login_model, email=request.json['email'], senha=request.json['senha'])
            if user:
                user.ultimo_login = datetime.now
                user.token = Token().generate(username=request.json.get('email'))
                self.operations.update(user)

            return jsonify(
                {
                    'status': True,
                    'message': 'Falha na autorização. Token inválido.',
                    'data': Token().generate(username=request.json.get('email')),
                }
            ), 200

        except Exception as exc:
            self.logger.log(message=str(exc), level='error')

            return jsonify(
                {
                    'status': True,
                    'message': str(exc),
                    'data': None,
                }
            ), 500
