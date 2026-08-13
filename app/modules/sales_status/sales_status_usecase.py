import math

from flask import request
from app.shared.helpers.functions import Functions
from app.shared.helpers.model_operations import ModelOperations
from app.shared.singletons.logger import Logger
from models import VendaStatusModel, VendaStatusBaseModel


class SalesStatusUseCase:
    def __init__(self):
        self.logger = Logger()
        self.operations = ModelOperations()
        self.functions = Functions()
        self.sales_status_model = VendaStatusModel

    def get_all_sales_status(self):
        try:
            status_list, total = self.operations.findMany(self.sales_status_model)
            status_array = [VendaStatusBaseModel.from_orm(status).dict() for status in status_list]

            return {
                'status': True,
                'message': 'Status de vendas carregados com sucesso.',
                'data': status_array
            }, 200
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')
            return {
                'status': False,
                'message': str(exc),
                'data': None,
            }, 500
