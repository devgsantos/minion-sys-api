from flask import request

from app.shared.singletons.logger import Logger


class TestUseCase:
    def __init__(self):
        self.logger = Logger()

    def execute(self):
        try:
            self.logger.log(message='MinionSys online!')

            return {
                'status': True,
                'message': 'MinionSys online!',
                'result': request.json,
                'code': 200
            }

        except Exception as exc:
            self.logger.log(message=str(exc), level='error')

            return {
                'status': False,
                'message': str(exc),
                'result': None,
                'code': 500
            }
