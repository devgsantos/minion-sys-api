from datetime import datetime
from typing import Type

from flask import request, jsonify, make_response
from app.shared.helpers.model_operations import ModelOperations
from app.shared.singletons.logger import Logger
from models import LoginModel, PermissaoModel, LoginPermissaoModel


class PermissionUseCase:
    def __init__(self):
        self.logger = Logger()
        self.operations = ModelOperations()
        self.login_model = LoginModel
        self.permission_model = PermissaoModel
        self.login_permission_model = LoginPermissaoModel

    def set_permissions(self):
        try:
            permissions = []
            for permission_id in request.json['permissoes']:
                permissions.append({'login_id': request.json['login_id'], 'permissao_id':permission_id})
            insert_permissions = self.operations.insert(self.login_permission_model, permissions=permissions)
            if len(insert_permissions) > 0:
                return make_response(
                    jsonify({
                        {
                            'status': True,
                            'message': 'Permissões atualizadas com sucesso.'
                        }
                    }), 200
                )
            else:
                return make_response(
                    jsonify({
                        {
                            'status': False,
                            'message': 'Nenhuma linha adicionada'
                        }
                    }), 204
                )
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')

            return jsonify(
                {
                    'status': True,
                    'message': str(exc),
                    'data': None,
                }
            ), 500