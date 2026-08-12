import os
import unittest
from unittest.mock import patch

import jwt
from flask import Flask, jsonify

from app.shared.middlewares.auth import auth_decorator


class AuthMiddlewareTestCase(unittest.TestCase):
    secret = 'test-secret'

    def setUp(self):
        self.app = Flask(__name__)

        @self.app.get('/protected')
        @auth_decorator
        def protected():
            return jsonify({'status': True})

        self.client = self.app.test_client()

    def test_missing_token_returns_http_401(self):
        response = self.client.get('/protected')

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json()['code'], 401)

    def test_invalid_token_returns_http_401(self):
        with patch.dict(os.environ, {'JWT_SECRET': self.secret}):
            response = self.client.get(
                '/protected',
                headers={'x-auth-token': 'invalid-token'},
            )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json()['message'], 'Token inválido')

    def test_valid_token_calls_protected_handler(self):
        token = jwt.encode(
            {'login_id': 1, 'companies': [10]},
            self.secret,
            algorithm='HS256',
        )

        with patch.dict(os.environ, {'JWT_SECRET': self.secret}):
            response = self.client.get(
                '/protected',
                headers={'x-auth-token': token},
            )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()['status'])


if __name__ == '__main__':
    unittest.main()
