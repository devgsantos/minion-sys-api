from flask_restful import Resource

from app.modules.user.user_usecase import UserUseCase
from app.shared.middlewares.auth import auth_decorator
from app.shared.middlewares.dto import dto_decorator
from models import UsuarioModel, UsuarioRequestModel


class UserResource(Resource):

    @auth_decorator
    @dto_decorator(UsuarioRequestModel)
    def post(self):
        return UserUseCase().set_user()
