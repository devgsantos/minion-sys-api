from flask_restful import Resource

from app.modules.product.product_usecase import ProductUseCase
from app.modules.product_category.product_category_usecase import ProductCategoryUseCase
from app.shared.middlewares.auth import auth_decorator
from app.shared.middlewares.dto import dto_decorator
from models import ProdutoCategoriaRequestModel


class ProductCategoryResource(Resource):

    @auth_decorator
    def get(self, action=None):
        if action == 'by_id':
            return ProductCategoryUseCase().get_product_category_by_id()
        if action == 'all':
            return ProductCategoryUseCase().get_product_category_all()

    @auth_decorator
    @dto_decorator(ProdutoCategoriaRequestModel)
    def post(self):
        return ProductCategoryUseCase().create_product_category()