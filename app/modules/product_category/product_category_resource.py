from flask_restful import Resource

from app.modules.product_category.product_category_usecase import ProductCategoryUseCase
from app.shared.middlewares.auth import auth_decorator
from app.shared.middlewares.dto import dto_decorator
from app.shared.middlewares.user_company_validator import user_company_validator
from models import ProdutoCategoriaRequestModel


class ProductCategoryResource(Resource):

    @auth_decorator
    def get(self, action=None):
        if action == 'por_id':
            return ProductCategoryUseCase().get_product_category_by_id()
        if action == 'todos':
            return ProductCategoryUseCase().get_product_category_all()

    @auth_decorator
    @dto_decorator(ProdutoCategoriaRequestModel)
    def post(self):
        return ProductCategoryUseCase().create_product_category()

    @auth_decorator
    @user_company_validator
    @dto_decorator(ProdutoCategoriaRequestModel)
    def put(self):
        return ProductCategoryUseCase().update_product_category()

    @auth_decorator
    @user_company_validator
    def delete(self):
        return ProductCategoryUseCase().virtual_delete_product_category()
