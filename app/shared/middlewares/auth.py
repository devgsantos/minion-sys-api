from flask import request
from functools import wraps
import jwt

import os

from app.shared.singletons.logger import Logger
logger = Logger()


def auth_decorator(func):
    try:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not request.headers.get('Authorization'):
                logger.log(message='Requisição sem token de autenticação', level='error')

                return {
                    'status': False,
                    'message': 'Requisição sem token de autenticação',
                    'result': None,
                    'code': 401
                }

            bearer, token = request.headers.get('Authorization').split(' ')

            if not token:
                logger.log(message='Requisição sem token de autenticação', level='error')

                return {
                    'status': False,
                    'message': 'Requisição sem token de autenticação',
                    'result': None,
                    'code': 401
                }

            try:
                decoded_token_info = jwt.decode(token, os.environ.get('JWT_SECRET'), algorithms=['HS256'])
            except Exception as exc:
                logger.log(message='Token inválido', level='error')

                return {
                    'status': False,
                    'message': 'Token inválido',
                    'result': None,
                    'code': 401
                }

            logger.log(message='Usuario autenticado com sucesso!', level='error')

            request.username = decoded_token_info.get('username')

            return func(*args, **kwargs)

        return wrapper
    except Exception as exc:
        logger.log(message=str(exc), level='error')

        return {
            'status': False,
            'message': str(exc),
            'result': None,
            'code': 500
        }
