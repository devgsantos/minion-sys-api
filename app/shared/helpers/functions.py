import hashlib
import os

import jwt
from flask import request, jsonify

from app.shared.helpers.model_operations import ModelOperations
from app.shared.helpers.token import Token
from app.shared.singletons.logger import Logger
from models import UsuarioModel


class Functions:
    def __init__(self):
        self.jwt = jwt
        self.auth_key = os.getenv('JWT_SECRET')
        self.operations = ModelOperations()
        self.logger = Logger()
        self.user_model = UsuarioModel

    def password_encrypt(string):
        hash = hashlib.md5(string.encode('utf-8'))
        hash_hex = hash.hexdigest()
        return hash_hex

    def hide_phone(phone):
        if len(phone) == 11:
            hidden_phone = '*' * 7 + phone[7:]
            return hidden_phone
        elif len(phone) == 10:
            hidden_phone = '*' * 6 + phone[6:]
            return hidden_phone

    def token_decript(self):
        payload = self.jwt.decode(request.headers.get("x-auth-token"), self.auth_key, algorithms=['HS256'])
        return payload

    def check_user_login(self):
        try:
            payload = Token().decode_token(request.headers.get('Authorization').split(' ')[1])
            user = self.operations.findOne(self.user_model, login_id=payload.get('login_id'))
            if user:
                return {
                    'status': True,
                    'data': user
                }
            else:
                return {
                    'status': True,
                    'data': None
                }
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')
            return jsonify(
                {
                    'status': True,
                    'message': str(exc),
                }
            ), 500