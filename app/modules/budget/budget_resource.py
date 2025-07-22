from flask_restx import Resource

from app.modules.budget.budget_usecase import BudgetUseCase
from app.shared.middlewares.auth import auth_decorator
from app.shared.middlewares.user_company_validator import user_company_validator
from app.shared.middlewares.dto import dto_decorator
from models import OrcamentoRequestModel

class BudgetResource(Resource):

    @auth_decorator
    @user_company_validator
    def get(self, action=None):
        if action == 'por_id':
            return BudgetUseCase().get_by_id()
        elif action == 'todos':
            return BudgetUseCase().get_all_budget()

    @auth_decorator
    @user_company_validator
    @dto_decorator(OrcamentoRequestModel)
    def post(self):
        return BudgetUseCase().save_budget()

    @auth_decorator
    @user_company_validator
    @dto_decorator(OrcamentoRequestModel)
    def put(self):
        return BudgetUseCase().save_budget()

    @auth_decorator
    @user_company_validator
    def delete(self):
        return BudgetUseCase().virtual_delete_budget()
