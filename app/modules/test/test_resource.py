from flask_restful import Resource

from app.shared.middlewares.auth import auth_decorator
from app.shared.middlewares.dto import dto_decorator
from app.modules.test.test_model import TestModel
from app.modules.test.test_usecase import TestUseCase


class TestResource(Resource):
    @auth_decorator
    @dto_decorator(TestModel)
    def post(self):
        return TestUseCase().execute()
