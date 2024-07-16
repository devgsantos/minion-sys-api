from flask_restful import Resource

# from app.modules.authentication.account_model import AccountLoginModel
from app.shared.middlewares.dto import dto_decorator
from app.modules.authentication.account_usecase import AccountUseCase


# class AccountResource(Resource):
#     @dto_decorator(AccountLoginModel)
#     def post(self):
#         return AccountUseCase().login()
