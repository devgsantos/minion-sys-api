from flask_restful import Resource

from app.modules.product_type.product_type_usecase import ProductTypeUseCase
from app.shared.middlewares.auth import auth_decorator
from app.shared.middlewares.dto import dto_decorator
from app.shared.middlewares.user_company_validator import user_company_validator
from models import ProdutoTipoRequestModel


class ProductTypeResource(Resource):

    @auth_decorator
    @user_company_validator
    def get(self, action=None):
        if action == 'por_id':
            return ProductTypeUseCase().get_product_type_by_id()
        if action == 'todos':
            return ProductTypeUseCase().get_product_type_all()

    @auth_decorator
    @user_company_validator
    @dto_decorator(ProdutoTipoRequestModel)
    def post(self):
        return ProductTypeUseCase().create_product_type()

    @auth_decorator
    @user_company_validator
    @dto_decorator(ProdutoTipoRequestModel)
    def put(self):
        return ProductTypeUseCase().update_product_type()

    @auth_decorator
    @user_company_validator
    def delete(self):
        return ProductTypeUseCase().virtual_delete_product_type()
