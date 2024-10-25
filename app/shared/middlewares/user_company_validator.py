from flask import request
from functools import wraps
import jwt

import os

from app.shared.singletons.logger import Logger
logger = Logger()

def user_company_validator(func):
    try:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                company_from_json = None
                if request.method in ['POST', 'PUT']:
                    company_from_json = request.json.get('empresa_id') if request.json else None
                    company_from_form = request.json.get('empresa_id') if request.json else None
                    company_from_link = request.args.get('empresa_id') if request.args.get('empresa_id') else None
                else:
                    company_from_link = request.args.get('empresa_id') if request.args.get('empresa_id') else None
                request_company = int(company_from_json or company_from_link) or None
                token = request.headers.get('x-auth-token')
                decoded_token_info = jwt.decode(token, os.environ.get('JWT_SECRET'), algorithms=['HS256'])
                if request_company in decoded_token_info['companies']:

                    return func(*args, **kwargs)

                else:
                    logger.log(message=f"Você não tem permissão nesta empresa. -> login_id: {decoded_token_info['logib_id']} | empresa_id: {request_company}", level='error')

                    return {
                        'status': False,
                        'message': 'Você não tem permissão nesta empresa.',
                        'result': None,
                        'code': 401
                    }
            except Exception as exc:
                logger.log(message='Falha ao validar empresa.', level='error')

                return {
                    'status': False,
                    'message': 'Falha ao validar empresa.',
                    'result': None,
                    'code': 400
                }

            logger.log(message=f'Usuario com permissão na empresa_id -> {request_company}', level='info')

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
