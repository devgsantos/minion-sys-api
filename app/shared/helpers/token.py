import jwt

import os
import datetime

from app.shared.helpers.model_operations import ModelOperations
from app.shared.singletons.logger import Logger


class Token:
    def __init__(self):
        self.secret_key = os.environ.get('JWT_SECRET')
        self.logger = Logger()

    def generate(self, login_id, permissions, companies):
        try:
            list_permissions = []
            list_companies = []
            for permission in permissions:
                list_permissions.append({
                    'login_permissao_id': permission.login_permissao_id,
                    'permissao_id': permission.permissao_id,
                    'titulo': permission.permissao.titulo,
                    'apelido': permission.permissao.apelido,
                    'descricao': permission.permissao.descricao
                })
            for company in companies:
                list_companies.append(
                    company.empresa_id
                )
            payload = {
                'login_id': login_id,
                'permissoes': list_permissions,
                'companies': list_companies,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=8)
            }

            token = jwt.encode(payload, self.secret_key, algorithm='HS256')

            self.logger.log('Usuário autenticado com sucesso!')

            return {
                'status': True,
                'message': 'Usuário autenticado com sucesso!',
                'code': 200,
                'result': token
            }
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')

            return {
                'status': False,
                'message': str(exc),
                'result': None,
                'code': 500
            }

    def decode_token(self, payload):
        return jwt.decode(payload, self.secret_key, algorithms='HS256')