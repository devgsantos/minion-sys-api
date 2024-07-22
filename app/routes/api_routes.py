from flask import Blueprint
from flask_restful import Api

from app.modules.login.login_resource import LoginResource
from app.modules.permissions.permissions_resource import PermissionsResource
from app.modules.test.test_resource import TestResource
from app.modules.user.user_resource import UserResource

api_blueprint = Blueprint('api', __name__)
api = Api(api_blueprint)

api.add_resource(TestResource, '/test')
api.add_resource(LoginResource, '/login')
api.add_resource(PermissionsResource, '/permissions')
api.add_resource(UserResource, '/users')
