from flask_restful import Resource

from app.shared.middlewares.auth import auth_decorator
from app.modules.file_repository.file_repository_usecase import FileRepositoryUseCase


class FileRepositoryResource(Resource):
    @auth_decorator
    def post(self):
        return FileRepositoryUseCase().file_upload()
