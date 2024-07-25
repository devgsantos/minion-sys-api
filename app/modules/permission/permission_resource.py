from flask_restful import Resource

from app.shared.middlewares.auth import auth_decorator
from app.shared.middlewares.dto import dto_decorator
from app.modules.permission.permission_usecase import PermissionUseCase
from models import PermissaoModel, LoginModel, LoginPermissoesRequest


class PermissionResource(Resource):

    @auth_decorator
    @dto_decorator(LoginPermissoesRequest)
    def post(self):
        return PermissionUseCase().set_permissions()

        # EXEMPLO DE MÚLTIPLOS ENDPOINTS PARA O MESMO RESOURCE
        # def post(self, action):
        #     if action == 'set':
        #         return PermissionsUseCase().set_permissions()
        #     else:
        #         return jsonify({"error": "Invalid action"}),
