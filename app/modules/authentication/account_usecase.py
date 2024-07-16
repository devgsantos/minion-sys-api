from flask import request
import requests

import os

from app.shared.singletons.logger import Logger
from app.shared.helpers.token import Token


class AccountUseCase:
    def __init__(self):
        self.logger = Logger()

    def login(self):
        try:
            ad_response = (requests.post(os.environ.get('AD_LOGIN_URL'), json={
                'username': request.json.get('username'),
                'password': request.json.get('password')
            })).json()

            if not ad_response.get('status'):
                return ad_response

            return Token().generate(username=request.json.get('username'))

        except Exception as exc:
            self.logger.log(message=str(exc), level='error')

            return {
                'status': False,
                'message': str(exc),
                'result': None,
                'code': 500
            }
