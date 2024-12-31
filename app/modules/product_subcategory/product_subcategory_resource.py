from flask_restful import Resource

from app.modules.product_subcategory.product_subcategory_usecase import ProductSubcategoryUseCase
from app.shared.middlewares.auth import auth_decorator
from app.shared.middlewares.dto import dto_decorator
from app.shared.middlewares.user_company_validator import user_company_validator
from models import  ProdutoSubcategoriaRequestModel


class ProductSubcategoryResource(Resource):

    @auth_decorator
    def get(self, action=None):
        if action == 'por_id':
            return ProductSubcategoryUseCase().get_product_subcategory_by_id()
        if action == 'todos':
            return ProductSubcategoryUseCase().get_product_subcategory_all()
        if action == 'por_categoria':
            return ProductSubcategoryUseCase().get_product_subcategory_by_category()

    @auth_decorator
    @dto_decorator(ProdutoSubcategoriaRequestModel)
    def post(self):
        return ProductSubcategoryUseCase().create_product_subcategory()

    @auth_decorator
    @user_company_validator
    @dto_decorator(ProdutoSubcategoriaRequestModel)
    def put(self):
        return ProductSubcategoryUseCase().update_product_subcategory()

    @auth_decorator
    @user_company_validator
    def delete(self):
        return ProductSubcategoryUseCase().virtual_delete_product_subcategory()
