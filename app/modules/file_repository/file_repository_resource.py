from flask_restful import Resource

from app.shared.middlewares.user_company_validator import user_company_validator
from app.shared.middlewares.auth import auth_decorator
from app.modules.file_repository.file_repository_usecase import FileRepositoryUseCase


class FileRepositoryResource(Resource):
    @auth_decorator
    @user_company_validator
    def post(self):
        return FileRepositoryUseCase().product_image()
