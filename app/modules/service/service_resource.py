from flask_restful import Resource

from app.modules.service.service_usecase import ServiceUseCase
from app.shared.middlewares import user_company_validator
from app.shared.middlewares.auth import auth_decorator
from app.shared.middlewares.dto import dto_decorator
from models import ServicoRequestModel


class ServiceResource(Resource):

    @auth_decorator
    def get(self, action=None):
        if action == 'por_id':
            return ServiceUseCase().get_service_by_id()
        if action == 'todos':
            return ServiceUseCase().get_service_all()

    @auth_decorator
    @dto_decorator(ServicoRequestModel)
    def post(self):
        return ServiceUseCase().create_service()

    @auth_decorator
    @dto_decorator(ServicoRequestModel)
    def put(self):
        return ServiceUseCase().update_service()

    @auth_decorator
    @user_company_validator
    def delete(self):
        return ServiceUseCase().virtual_delete_service()
