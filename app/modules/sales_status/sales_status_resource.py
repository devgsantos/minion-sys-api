from flask_restful import Resource
from app.modules.sales_status.sales_status_usecase import SalesStatusUseCase
from app.shared.middlewares.auth import auth_decorator
from app.shared.middlewares.user_company_validator import user_company_validator


class SalesStatusResource(Resource):
    @auth_decorator
    def get(self, action=None):
        if action == 'todos':
            return SalesStatusUseCase().get_all_sales_status()
        return {
            'status': False,
            'message': 'Ação não encontrada.'
        }, 404
