import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from flask import Flask

from app.modules.login.login_usecase import LoginUseCase
from app.shared.helpers.password import hash_password


class LoginPasswordMigrationTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.operations = MagicMock()

    def execute_login(self, stored_password, provided_password):
        login = SimpleNamespace(
            login_id=1,
            email='user@example.com',
            senha=stored_password,
            permissoes=[],
            empresas=[],
        )
        self.operations.findOne.return_value = login
        token = MagicMock()
        token.generate.return_value = {'result': 'jwt-token'}

        with (
            self.app.test_request_context(
                '/login',
                method='POST',
                json={'email': login.email, 'senha': provided_password},
            ),
            patch(
                'app.modules.login.login_usecase.ModelOperations',
                return_value=self.operations,
            ),
            patch('app.modules.login.login_usecase.Token', return_value=token),
        ):
            return LoginUseCase().login()

    def test_legacy_password_is_replaced_after_successful_login(self):
        _, status = self.execute_login('legacy-password', 'legacy-password')

        self.assertEqual(status, 200)
        self.operations.findOne.assert_called_once()
        self.assertNotIn('senha', self.operations.findOne.call_args.kwargs)
        migrated_password = self.operations.update.call_args.kwargs['senha']
        self.assertNotEqual(migrated_password, 'legacy-password')

    def test_hashed_password_is_not_rehashed_on_login(self):
        _, status = self.execute_login(
            hash_password('secret-password'),
            'secret-password',
        )

        self.assertEqual(status, 200)
        self.assertNotIn('senha', self.operations.update.call_args.kwargs)

    def test_invalid_password_does_not_update_login(self):
        _, status = self.execute_login(hash_password('secret-password'), 'wrong')

        self.assertEqual(status, 401)
        self.operations.update.assert_not_called()


if __name__ == '__main__':
    unittest.main()
