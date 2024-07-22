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
            check_user = self.functions.check_user_login()
            if check_user.get('login_id'):
                return check_user
            else:
                insert_user = self.operations.insert(self.user_model, **request.json)
                if len(insert_user) > 0:
                    self.logger(message='Perfil de usuário criado com sucesso.', level='info')
                    return make_response(
                        jsonify({
                            {
                                'status': True,
                                'message': 'Perfil de usuário criado com sucesso.'
                            }
                        }), 200
                    )
                else:
                    self.logger(message='Nenhum perfil foi criado.', level='info')
                    return make_response(
                        jsonify({
                            {
                                'status': False,
                                'message': 'Nenhum perfil foi criado.'
                            }
                        }), 204
                    )
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')
            return jsonify(
                {
                    'status': True,
                    'message': str(exc),
                }
            ), 500

