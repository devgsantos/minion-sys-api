from flask import request
from functools import wraps

from app.shared.singletons.logger import Logger
logger = Logger()

def user_company_validator(func):
    try:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                json_data = request.get_json(silent=True) or {}
                company_id = (
                    request.args.get('empresa_id')
                    or request.form.get('empresa_id')
                    or json_data.get('empresa_id')
                )

                if company_id in (None, ''):
                    return {
                        'status': False,
                        'message': 'Forneça o empresa_id.',
                        'result': None,
                    }, 400

                try:
                    request_company = int(company_id)
                except (TypeError, ValueError):
                    return {
                        'status': False,
                        'message': 'empresa_id inválido.',
                        'result': None,
                    }, 400

                auth_context = getattr(request, 'auth_context', {})
                authorized_companies = auth_context.get('companies', [])
                if request_company in authorized_companies:
                    request.company_id = request_company

                    return func(*args, **kwargs)

                else:
                    logger.log(
                        message=f"Você não tem permissão nesta empresa. -> login_id: {auth_context.get('login_id')} | empresa_id: {request_company}",
                        level='error'
                    )
                    return {
                        'status': False,
                        'message': 'Você não tem permissão nesta empresa.',
                        'result': None,
                    }, 403
                
            except Exception as exc:
                logger.log(message=f'Falha ao validar empresa. {exc}', level='error')

                return {
                    'status': False,
                    'message': 'Falha ao validar empresa.',
                    'result': None
                }, 400
            
        return wrapper

    except Exception as exc:
        logger.log(message=str(exc), level='error')

        return {
            'status': False,
            'message': str(exc),
            'result': None,
        }, 500
