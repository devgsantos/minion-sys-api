import hashlib
import os

import jwt
from flask import request, jsonify



class Functions:
    def __init__(self):
        self.jwt = jwt
        self.auth_key = os.getenv('JWT_SECRET')

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