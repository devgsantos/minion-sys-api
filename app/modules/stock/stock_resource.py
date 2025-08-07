from flask_restful import Resource

from app.modules.stock.stock_usecase import StockUseCase
from app.shared.middlewares.auth import auth_decorator
from app.shared.middlewares.user_company_validator import user_company_validator
from app.shared.middlewares.dto import dto_decorator
from models import EstoqueProdutoBaseModel


class StockResource(Resource):
    
    @auth_decorator
    def get(self, action=None):
        if action == 'por_id':
            return StockUseCase().get_stock_by_id()
        if action == 'por_produto':
            return StockUseCase().get_stock_by_product()
        if action == 'todos':
            return StockUseCase().get_stock_all()

    @auth_decorator
    @dto_decorator(EstoqueProdutoBaseModel)
    def post(self):
        return StockUseCase().create_stock()

    @auth_decorator
    @dto_decorator(EstoqueProdutoBaseModel)
    def put(self):
        return StockUseCase().update_stock()

    @auth_decorator
    @user_company_validator
    def delete(self):
        return StockUseCase().virtual_delete_stock()
