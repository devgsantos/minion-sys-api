from flask_restful import Resource

from app.modules.company.company_usecase import CompanyUseCase
from app.shared.middlewares.auth import auth_decorator
from app.shared.middlewares.dto import dto_decorator
from app.modules.permission.permission_usecase import PermissionUseCase
from models import PermissaoModel, LoginModel, LoginPermissoesRequest, EmpresaRequestModel


class CompanyResource(Resource):

    @auth_decorator
    def get(self, action=None):
        if action == 'by_user':
            return CompanyUseCase().get_company_by_user()
        return CompanyUseCase().get_company_all()

    @auth_decorator
    @dto_decorator(EmpresaRequestModel)
    def post(self):
        return CompanyUseCase().create_company()

        # EXEMPLO DE MÚLTIPLOS ENDPOINTS PARA O MESMO RESOURCE
        # def post(self, action):
        #     if action == 'set':
        #         return PermissionsUseCase().set_permissions()
        #     else:
        #         return jsonify({"error": "Invalid action"}),
