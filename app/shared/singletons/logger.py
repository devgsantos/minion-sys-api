import os
import logging
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
import locale

from app.shared.helpers.singleton import Singleton

# Configurando o locale para português do Brasil
locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')

class Logger(metaclass=Singleton):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.update_log_handler()

    def get_log_month_directory_name(self, current_date):
        # Usando strftime para obter o nome do mês diretamente
        return current_date.strftime('%B').lower()

    def update_log_handler(self):
        current_date = datetime.now()
        log_directory = os.path.join('app', 'logs', str(current_date.year),
                                     self.get_log_month_directory_name(current_date), str(current_date.day))
        os.makedirs(log_directory, exist_ok=True)
        log_path = os.path.join(log_directory, 'info.log')

        log_handler = TimedRotatingFileHandler(log_path, when='S', interval=999999, backupCount=5)
        log_handler.setLevel(logging.DEBUG)
        log_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))

        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        self.logger.addHandler(log_handler)

    def log(self, message='', level='info'):
        self.update_log_handler()

        request_path = '/'.join(request.path.strip('/').split('/')[2:])

        log_message = f'{level.upper()} - {request.method} /{request_path} - {request.remote_addr} -> {message.upper()}'

        self.logger.info(log_message)
