from flask_restful import Resource

from app.modules.service.service_usecase import ServiceUseCase
from app.shared.middlewares.auth import auth_decorator
from app.shared.middlewares.dto import dto_decorator
from models import ServicoRequestModel


class ServiceResource(Resource):

    @auth_decorator
    def get(self, action=None):
        if action == 'by_id':
            return ServiceUseCase().get_service_by_id()
        if action == 'all':
            return ServiceUseCase().get_service_all()

    @auth_decorator
    @dto_decorator(ServicoRequestModel)
    def post(self):
        return ServiceUseCase().create_service()
