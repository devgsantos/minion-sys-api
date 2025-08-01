from flask_restful import Resource

from app.modules.customer.customer_usecase import CustomerUseCase
from app.shared.middlewares.user_company_validator import user_company_validator
from app.shared.middlewares.auth import auth_decorator
from app.shared.middlewares.dto import dto_decorator
from models import ClienteRequestModel


class CustomerResource(Resource):

    @auth_decorator
    def get(self, action=None):
        if action == 'por_id':
            return CustomerUseCase().get_customer_by_id()
        if action == 'todos':
            return CustomerUseCase().get_customer_all()

    @auth_decorator
    @dto_decorator(ClienteRequestModel)
    def post(self):
        return CustomerUseCase().create_customer()

    @auth_decorator
    @dto_decorator(ClienteRequestModel)
    def put(self):
        return CustomerUseCase().update_customer()

    @auth_decorator
    @user_company_validator
    def delete(self):
        return CustomerUseCase().virtual_delete_customer()
