from flask_restful import Resource

from app.shared.middlewares.dto import dto_decorator
from app.modules.login.login_usecase import LoginUseCase
from models import LoginModel, LoginRequestModel


class LoginResource(Resource):
    @dto_decorator(LoginRequestModel)
    def post(self):
        return LoginUseCase().login()
