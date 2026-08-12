from datetime import datetime
from typing import Type

from flask import request, jsonify, make_response
from app.shared.helpers.model_operations import ModelOperations
from app.shared.singletons.logger import Logger
from app.shared.helpers.token import Token
from app.shared.helpers.password import hash_password, verify_password
from models import LoginModel


class LoginUseCase:
    def __init__(self):
        self.logger = Logger()
        self.operations = ModelOperations()
        self.login_model = LoginModel

    def login(self):
        try:
            login: Type[LoginModel] = self.operations.findOne(
                self.login_model,
                email=request.json['email'],
            )
            password_is_valid = False
            should_migrate_password = False
            if login:
                password_is_valid, should_migrate_password = verify_password(
                    login.senha,
                    request.json['senha'],
                )

            if login and password_is_valid:
                token = Token().generate(login_id=login.login_id, permissions=login.permissoes, companies=login.empresas)
                update_data = {
                    'ultimo_login': datetime.now(),
                    'token': token.get('result'),
                }
                if should_migrate_password:
                    update_data['senha'] = hash_password(request.json['senha'])
                self.operations.update(self.login_model, login.login_id, **update_data)
                return {
                    'status': True,
                    'message': 'Autenticação realizada com sucesso.',
                    'data': {
                        'result': token.get('result')
                    }
                }, 200
            else:
                return {
                    'status': False,
                    'message': "Usuário ou senha incorretos.",
                    'data': None,
                }, 401
        except Exception as exc:
            return {
                'status': False,
                'message': str(exc),
                'data': None,
            }, 500
