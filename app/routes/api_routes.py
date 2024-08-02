from flask import Blueprint
from flask_restful import Api

from app.modules.company.company_resource import CompanyResource
from app.modules.login.login_resource import LoginResource
from app.modules.permission.permission_resource import PermissionResource
from app.modules.product.product_resource import ProductResource
from app.modules.product_category.product_category_resource import ProductCategoryResource
from app.modules.test.test_resource import TestResource
from app.modules.user.user_resource import UserResource

api_blueprint = Blueprint('api', __name__)
api = Api(api_blueprint)

api.add_resource(TestResource, '/test')

# LOGIN
api.add_resource(LoginResource, '/login')

# PERMISSION
api.add_resource(PermissionResource, '/permission')

# USER
api.add_resource(UserResource, '/users')

# COMPANY
api.add_resource(CompanyResource, '/company/<string:action>')

# PRODUCT
api.add_resource(ProductResource, '/product')

# PRODUCT CATEGORY
api.add_resource(ProductCategoryResource, '/product_category')
