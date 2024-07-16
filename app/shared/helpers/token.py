import jwt

import os
import datetime

from app.shared.singletons.logger import Logger


class Token:
    def __init__(self):
        self.secret_key = os.environ.get('JWT_SECRET')
        self.logger = Logger()

    def generate(self, username):
        try:
            payload = {
                'username': username,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=6)
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
