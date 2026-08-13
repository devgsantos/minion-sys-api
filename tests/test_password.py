import unittest

from app.shared.helpers.password import hash_password, verify_password


class PasswordTestCase(unittest.TestCase):
    def test_hash_is_not_plaintext_and_can_be_verified(self):
        password_hash = hash_password('secret-password')

        self.assertNotEqual(password_hash, 'secret-password')
        self.assertEqual(
            verify_password(password_hash, 'secret-password'),
            (True, False),
        )

    def test_invalid_password_is_rejected(self):
        password_hash = hash_password('secret-password')

        self.assertEqual(verify_password(password_hash, 'wrong'), (False, False))

    def test_valid_legacy_password_requests_migration(self):
        self.assertEqual(
            verify_password('legacy-password', 'legacy-password'),
            (True, True),
        )

    def test_invalid_legacy_password_does_not_request_migration(self):
        self.assertEqual(
            verify_password('legacy-password', 'wrong'),
            (False, False),
        )


if __name__ == '__main__':
    unittest.main()
