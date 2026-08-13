from flask_restful import Resource

from app.modules.stock_type.stock_type_usecase import StockTypeUseCase
from app.shared.middlewares.auth import auth_decorator
from app.shared.middlewares.dto import dto_decorator
from app.shared.middlewares.user_company_validator import user_company_validator
from models import ProdutoTipoRequestModel


class StockTypeResource(Resource):

    @auth_decorator
    def get(self, action=None):
        if action == 'por_id':
            return StockTypeUseCase().get_stock_type_by_id()
        if action == 'todos':
            return StockTypeUseCase().get_stock_type_all()

    @auth_decorator
    @dto_decorator(ProdutoTipoRequestModel)
    def post(self):
        return StockTypeUseCase().create_stock_type()

    @auth_decorator
    @user_company_validator
    @dto_decorator(ProdutoTipoRequestModel)
    def put(self):
        return StockTypeUseCase().update_stock_type()

    @auth_decorator
    @user_company_validator
    def delete(self):
        return StockTypeUseCase().virtual_delete_stock_type()
