
from flask import request, jsonify, make_response

from app.shared.helpers.functions import Functions
from app.shared.helpers.model_operations import ModelOperations
from app.shared.singletons.logger import Logger
from models import OrcamentoModel, OrcamentoItemModel, OrcamentoBaseModel

class BudgetUseCase:
    def __init__(self):
        self.logger = Logger()
        self.operations = ModelOperations()
        self.functions = Functions()
        self.budget_model = OrcamentoModel
        self.budget_items_model = OrcamentoItemModel


    # USAR A SERIALIZAÇÃO DESTA FUNÇÃO COMO BASE PARA AS OUTRAS
    def get_all_budget(self):
        try:
            page = int(request.args.get('pagina')) if request.args.get('pagina') else 1
            limit = int(request.args.get('limite')) if request.args.get('limite') else 10
            budgets, total = self.operations.findMany(self.budget_model, page, limit, empresa_id=request.args.get('empresa_id'))
            budgets_array = [OrcamentoBaseModel.from_orm(budget).dict() for budget in budgets]

            return make_response(jsonify(
                {
                    'status': True,
                    'message': 'Orçamentos carregados com sucesso.',
                    'data': {
                        'result': budgets_array,
                        'page': page,
                        'limit': limit,
                        'total': total
                    }

                }
            ), 201)
        except Exception as exc:
            return make_response(jsonify(
                {
                    'status': False,
                    'message': str(exc),
                    'data': None,
                }
            ), 500)


    def create_budget(self):
        try:
            user = self.functions.token_decript()
            request.json['responsavel_cadastro_id'] = user.get('login_id')
            request.json['valor'] = user.get('login_id')
            product_insert = {key: value for key, value in request.json.items() if key != 'estoque'}
            result = self.operations.insert(self.budget_model, **product_insert)
            if len(request.json['estoque']) > 0:
                for param in request.json['estoque']:
                    insert_data = {
                        "orcamento_id": result.orcamento_id,
                        "estoque_tipo_id": param['estoque_tipo_id'],
                        "quantidade_disponivel": param['quantidade_disponivel']
                    }
                    self.operations.insert(self.stock_model, **insert_data)
            return make_response(jsonify(
                {
                    'status': True,
                    'message': 'Orçamento criado com sucesso.'
                }
            ), 201)
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')

            return make_response(jsonify(
                {
                    'status': False,
                    'message': str(exc),
                    'data': None,
                }
            ), 500)

    def update_budget(self):
        try:
            user = self.functions.token_decript()
            request.json['responsavel_cadastro_id'] = user.get('login_id')
            product_update = {key: value for key, value in request.json.items() if key != 'estoque' and key !='orcamento_id'}
            self.operations.update(self.budget_model, request.json['orcamento_id'], **product_update)
            if len(request.json['estoque']) > 0:
                for param in request.json['estoque']:
                    unique_data = {
                        "orcamento_id": request.json['orcamento_id'],
                        "estoque_tipo_id": param['estoque_tipo_id']
                    }
                    data_to_update = {
                        "quantidade_disponivel": param['quantidade_disponivel']
                    }
                    self.operations.merge_insert_if_not_exists(self.stock_model, unique_fields=unique_data, **data_to_update)
            return make_response(jsonify(
                {
                    'status': True,
                    'message': 'Orçamento alterado com sucesso.'
                }
            ), 201)
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')

            return make_response(jsonify(
                {
                    'status': False,
                    'message': str(exc),
                    'data': None,
                }
            ), 500)

    def virtual_delete_budget(self):
        try:
            delete_budget = self.operations.soft_delete(self.budget_model, request.args.get('orcamento_id'), request.args.get('empresa_id'))
            if delete_budget:
                return make_response(jsonify(
                    {
                        'status': True,
                        'message': 'Orçamento excluído com sucesso.'
                    }
                ), 201)
            else:
                self.logger.log(message=f"Falha ao excluir orçamento.", level='error')

                return make_response(jsonify(
                    {
                        'status': False,
                        'message': 'Falha ao excluir orçamento.',
                    }
                ), 500)
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')

            return make_response(jsonify(
                {
                    'status': False,
                    'message': str(exc),
                    'data': None,
                }
            ), 500)
