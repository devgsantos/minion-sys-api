import pyodbc

import os

from app.shared.singletons.logger import Logger
from app.shared.helpers.query_formatter import QueryFormatter


class DbMssqlConfig:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.logger = Logger()
        self.query_formatter = QueryFormatter()

    def execute(self, query, *params):
        try:
            server = os.environ.get('MSSQL_SERVER')
            database = os.environ.get('MSSQL_DATABASE')
            username = os.environ.get('MSSQL_USERNAME')
            password = os.environ.get('MSSQL_PASSWORD')
            driver = 'ODBC Driver 18 for SQL Server'

            self.connection = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};TrustServerCertificate=yes;UID={username};PWD={password}')
            self.cursor = self.connection.cursor()

            formatted_query = query.strip().replace("\n", "")

            self.cursor.execute(formatted_query, *params)

            if formatted_query.split(' ')[0].upper() == 'SELECT' or formatted_query.split(' ')[0].upper() == 'WITH':
                result = self.cursor.fetchall()

                status, formatted_result = self.query_formatter.execute(result, self.cursor)

            else:
                formatted_result = self.cursor.rowcount
                self.connection.commit()

                status = True

            return status, formatted_result
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')

            return False, {
                "status": False,
                "message": str(exc),
                "result": None,
                "code": 500
            }
        finally:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
