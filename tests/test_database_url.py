import unittest

from app.shared.config.database_url import normalize_database_url


class DatabaseUrlTestCase(unittest.TestCase):
    def test_removes_supabase_pgbouncer_parameter(self):
        url = normalize_database_url(
            'postgresql://user:secret@example.com:6543/postgres?pgbouncer=true'
        )

        self.assertNotIn('pgbouncer', url.query)
        self.assertEqual(url.host, 'example.com')
        self.assertEqual(url.port, 6543)

    def test_preserves_supported_query_parameters(self):
        url = normalize_database_url(
            'postgresql://user:secret@example.com/postgres?sslmode=require'
        )

        self.assertEqual(url.query['sslmode'], 'require')


if __name__ == '__main__':
    unittest.main()
