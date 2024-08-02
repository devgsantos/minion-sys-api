from flask_restful import Resource

from app.modules.company.company_usecase import CompanyUseCase
from app.modules.product.product_usecase import ProductUseCase
from app.shared.middlewares.auth import auth_decorator
from app.shared.middlewares.dto import dto_decorator
from app.modules.permission.permission_usecase import PermissionUseCase
from models import ProdutoRequestModel


class ProductResource(Resource):

    @auth_decorator
    def get(self, action=None):
        if action == 'by_id':
            return ProductUseCase().get_by_id()
        return ProductUseCase().get_all()

    @auth_decorator
    @dto_decorator(ProdutoRequestModel)
    def post(self):
        return ProductUseCase().create_product()