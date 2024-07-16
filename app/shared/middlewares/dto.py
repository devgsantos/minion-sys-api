from functools import wraps
from flask import request
from pydantic import ValidationError

from app.shared.singletons.logger import Logger
logger = Logger()


def dto_decorator(model):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                model(**request.json)
                logger.log(message='Dados externos verificados com sucesso!')

                return func(*args, **kwargs)

            except ValidationError as exc:
                messages = []

                for error in exc.errors():
                    messages.append(f"{error.get('loc')[0]} -> {error.get('msg')}")

                logger.log(message=' || '.join(messages), level='error')

                return {
                    'status': False,
                    'message': ' || '.join(messages),
                    'result': None,
                    'code': 500
                }

            except Exception as exc:
                logger.log(message=str(exc), level='error')

                return {
                    'status': False,
                    'message': str(exc),
                    'result': None,
                    'code': 500
                }
        return wrapper
    return decorator
