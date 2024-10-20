from flask import Blueprint
from flask_restful import Api

from app.modules.company.company_resource import CompanyResource
from app.modules.login.login_resource import LoginResource
from app.modules.permission.permission_resource import PermissionResource
from app.modules.product.product_resource import ProductResource
from app.modules.product_category.product_category_resource import ProductCategoryResource
from app.modules.service.service_resource import ServiceResource
from app.modules.test.test_resource import TestResource
from app.modules.user.user_resource import UserResource
from app.shared.helpers.functions import Functions

api_blueprint = Blueprint('api', __name__)
api = Api(api_blueprint)


api.add_resource(TestResource, '/teste')

# LOGIN
api.add_resource(LoginResource, '/login')

# PERMISSION
api.add_resource(PermissionResource, '/permissao')

# USER
api.add_resource(UserResource, '/usuarios')

# COMPANY
api.add_resource(CompanyResource, '/empresa', '/empresa/<string:action>')

# PRODUCT
api.add_resource(ProductResource, '/produto', '/produto/<string:action>')

# PRODUCT CATEGORY
api.add_resource(ProductCategoryResource, '/produto-categoria', '/produto-categoria/<string:action>')

# SERVICE
api.add_resource(ServiceResource, '/servico', '/servico/<string:action>')
