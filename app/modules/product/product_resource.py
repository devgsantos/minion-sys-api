from flask_restx import Resource


from app.modules.company.company_usecase import CompanyUseCase
from app.modules.product.product_usecase import ProductUseCase
from app.shared.middlewares.auth import auth_decorator
from app.shared.middlewares.user_company_validator import user_company_validator
from app.shared.middlewares.dto import dto_decorator
from models import ProdutoRequestModel

class ProductResource(Resource):

    @auth_decorator
    @user_company_validator
    def get(self, action=None):
        if action == 'por_id':
            return ProductUseCase().get_by_id()
        elif action == 'todos':
            return ProductUseCase().get_all_product()

    @auth_decorator
    @user_company_validator
    @dto_decorator(ProdutoRequestModel)
    def post(self):
        return ProductUseCase().create_product()

    @auth_decorator
    @user_company_validator
    @dto_decorator(ProdutoRequestModel)
    def put(self):
        return ProductUseCase().update_product()

    @auth_decorator
    @user_company_validator
    def delete(self):
        return ProductUseCase().virtual_delete_product()
