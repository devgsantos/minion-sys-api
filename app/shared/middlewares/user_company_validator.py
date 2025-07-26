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
                company_id = None

                # Verifica se o Content-Type é application/json e tenta obter o 'empresa_id' do corpo JSON
                if request.content_type == 'application/json':
                    company_id = request.json.get('empresa_id')

                # Caso não seja JSON ou 'empresa_id' não esteja no JSON, tenta obter de outros métodos
                if not company_id:
                    company_id = request.args.get('empresa_id') or request.form.get('empresa_id')

                if not company_id:
                    return {
                        'status': False,
                        'message': 'Forneça o empresa_id.',
                        'result': None,
                        'code': 400
                    }

                request_company = int(company_id)
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
                logger.log(message=f'Falha ao validar empresa. {exc}', level='error')

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
