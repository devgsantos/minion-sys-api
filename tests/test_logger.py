import logging
import unittest
from unittest.mock import patch

from app.shared.singletons.logger import Logger


class LoggerTestCase(unittest.TestCase):
    def test_vercel_uses_stream_handler(self):
        logger = Logger()

        with patch.dict('os.environ', {'VERCEL': '1'}):
            logger.update_log_handler()

        self.assertTrue(
            any(
                isinstance(handler, logging.StreamHandler)
                and not isinstance(handler, logging.FileHandler)
                for handler in logger.logger.handlers
            )
        )


if __name__ == '__main__':
    unittest.main()
