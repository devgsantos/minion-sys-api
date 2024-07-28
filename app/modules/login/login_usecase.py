from datetime import datetime
from typing import Type

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
            login: Type[LoginModel] = self.operations.findOne(self.login_model, email=request.json['email'], senha=request.json['senha'])
            if login:
                token = Token().generate(login_id=login.login_id, permissions=login.permissoes)
                self.operations.update(self.login_model, login.login_id, ultimo_login=datetime.now(), token=token.get('result'))
            else:
                return make_response(
                    jsonify(
                        {
                            'status': False,
                            'message': "Usuário ou senha incorretos.",
                            'data': None,
                        }
                    ), 404
                )

            return make_response(
                jsonify(
                    {
                        'status': True,
                        'message': 'Autenticação realizada com sucesso.',
                        'data': {
                            'result': token.get('result')
                        }
                    }
                ), 200
            )

        except Exception as exc:

            return make_response(
                jsonify(
                    {
                        'status': True,
                        'message': str(exc),
                        'data': None,
                    }
                ), 500
            )
