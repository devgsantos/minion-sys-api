from flask_restful import Resource

# from app.modules.login.account_model import AccountLoginModel
from app.shared.middlewares.dto import dto_decorator
from app.modules.login.login_usecase import LoginUseCase
from models import LoginModel


class LoginResource(Resource):
    @dto_decorator(LoginModel)
    def post(self):
        return LoginUseCase().login()
