from datetime import datetime
from typing import Type

from flask import request, jsonify, make_response

from app.shared.helpers.functions import Functions
from app.shared.helpers.model_operations import ModelOperations
from app.shared.helpers.token import Token
from app.shared.singletons.logger import Logger
from models import UsuarioModel


class UserUseCase:
    def __init__(self):
        self.logger = Logger()
        self.operations = ModelOperations()
        self.user_model = UsuarioModel
        self.functions = Functions()

    def set_user(self):
        try:
            user = self.functions.token_decript()
            request.json['login_id'] = user.get('login_id')
            insert_user = self.operations.insert(self.user_model, **request.json)
            if insert_user:
                return make_response(
                    jsonify({
                        {
                            'status': True,
                            'message': 'Perfil de usuário criado com sucesso.'
                        }
                    }, 200)
                )
            else:
                return make_response(
                    jsonify({
                        {
                            'status': False,
                            'message': 'Nenhum perfil foi criado.'
                        }
                    }, 204)
                )
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')
            return make_response(jsonify(
                {
                    'status': True,
                    'message': str(exc),
                }
            ), 500)

