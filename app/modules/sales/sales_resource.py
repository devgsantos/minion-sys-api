from flask_restx import Resource
from app.modules.sales.sales_usecase import SalesUseCase
from app.shared.middlewares.auth import auth_decorator
from app.shared.middlewares.user_company_validator import user_company_validator
from app.shared.middlewares.dto import dto_decorator
from models.venda_model import VendaRequestBaseModel


class SalesResource(Resource):

    @auth_decorator
    @user_company_validator
    def get(self, action=None):
        if action == 'por_id':
            return SalesUseCase().get_by_id()
        elif action == 'todos':
            return SalesUseCase().get_all_sales()

    @auth_decorator
    @user_company_validator
    @dto_decorator(VendaRequestBaseModel)
    def post(self):
        return SalesUseCase().save_sale()

    @auth_decorator
    @user_company_validator
    def delete(self):
        return SalesUseCase().virtual_delete_sale()
