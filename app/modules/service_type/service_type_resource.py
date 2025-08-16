from flask_restful import Resource

from app.modules.service_type.service_type_usecase import ServiceTypeUseCase
from app.shared.middlewares.auth import auth_decorator
from app.shared.middlewares.dto import dto_decorator
from app.shared.middlewares.user_company_validator import user_company_validator
from models import ServicoTipoRequestModel


class ServiceTypeResource(Resource):

    @auth_decorator
    def get(self, action=None):
        if action == 'por_id':
            return ServiceTypeUseCase().get_service_type_by_id()
        if action == 'todos':
            return ServiceTypeUseCase().get_service_type_all()

    @auth_decorator
    @dto_decorator(ServicoTipoRequestModel)
    def post(self):
        return ServiceTypeUseCase().create_service_type()

    @auth_decorator
    @user_company_validator
    @dto_decorator(ServicoTipoRequestModel)
    def put(self):
        return ServiceTypeUseCase().update_service_type()

    @auth_decorator
    @user_company_validator
    def delete(self):
        return ServiceTypeUseCase().virtual_delete_service_type()
