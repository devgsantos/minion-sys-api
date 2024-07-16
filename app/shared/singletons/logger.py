from flask import request

import os
import logging
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

from app.shared.helpers.singleton import Singleton


class Logger(metaclass=Singleton):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.update_log_handler()

    @staticmethod
    def get_log_month_directory_name(month_index):
        month_names = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto',
                       'setembro', 'outubro', 'novembro', 'dezembro']

        return month_names[month_index]

    def update_log_handler(self):
        current_date = datetime.now()
        log_directory = os.path.join('app', 'logs', str(current_date.year),
                                     self.get_log_month_directory_name(month_index=current_date.month), str(current_date.day))
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
