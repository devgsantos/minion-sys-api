from flask import request
from functools import wraps
import jwt

import os

from app.shared.singletons.logger import Logger
logger = Logger()

def user_company(func):
    try:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                company_from_json = request.json.get('company') if request.json else None
                company_from_link = request.args.get('company') if request.args.get('company') else None
                request_company = company_from_json or company_from_link or None
                token = request.headers.get('x-auth-token')
                decoded_token_info = jwt.decode(token, os.environ.get('JWT_SECRET'), algorithms=['HS256'])
                print(decoded_token_info)
            except Exception as exc:
                logger.log(message='Token inválido', level='error')

                return {
                    'status': False,
                    'message': 'Token inválido',
                    'result': None,
                    'code': 401
                }

            logger.log(message='Usuario autenticado com sucesso!', level='info')

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
