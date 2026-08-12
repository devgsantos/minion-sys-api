import os
import unittest
from unittest.mock import patch

import jwt
from flask import Flask, jsonify

from app.shared.middlewares.auth import auth_decorator
from app.shared.middlewares.user_company_validator import user_company_validator


class CompanyMiddlewareTestCase(unittest.TestCase):
    secret = 'test-secret'

    def setUp(self):
        self.app = Flask(__name__)

        @self.app.route('/protected', methods=['GET', 'POST'])
        @auth_decorator
        @user_company_validator
        def protected():
            from flask import request
            return jsonify({'company_id': request.company_id})

        self.client = self.app.test_client()
        self.token = jwt.encode(
            {'login_id': 1, 'companies': [10]},
            self.secret,
            algorithm='HS256',
        )

    def request(self, method='get', **kwargs):
        headers = {'x-auth-token': self.token}
        with patch.dict(os.environ, {'JWT_SECRET': self.secret}):
            return getattr(self.client, method)('/protected', headers=headers, **kwargs)

    def test_missing_company_returns_http_400(self):
        response = self.request()
        self.assertEqual(response.status_code, 400)

    def test_invalid_company_returns_http_400(self):
        response = self.request(query_string={'empresa_id': 'invalid'})
        self.assertEqual(response.status_code, 400)

    def test_company_outside_token_returns_http_403(self):
        response = self.request(query_string={'empresa_id': 20})
        self.assertEqual(response.status_code, 403)

    def test_authorized_company_from_query_is_added_to_request(self):
        response = self.request(query_string={'empresa_id': 10})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['company_id'], 10)

    def test_authorized_company_from_json_is_added_to_request(self):
        response = self.request(method='post', json={'empresa_id': 10})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['company_id'], 10)


if __name__ == '__main__':
    unittest.main()
