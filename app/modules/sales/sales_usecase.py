import math
from datetime import datetime
from typing import Optional
from flask import request, jsonify, make_response

from app.shared.helpers.functions import Functions
from app.shared.helpers.model_operations import ModelOperations
from app.shared.singletons.logger import Logger
from models import VendaModel, OrcamentoModel, OrcamentoItemModel, VendaBaseModel
from models import VendaStatusModel, VendaStatusBaseModel


class SalesUseCase:
    def __init__(self):
        self.logger = Logger()
        self.operations = ModelOperations()
        self.functions = Functions()
        self.sales_model = VendaModel
        self.budget_model = OrcamentoModel
        self.budget_item_model = OrcamentoItemModel
        self.sales_status_model = VendaStatusModel

    def get_all_sales(self):
        try:
            page = int(request.args.get('pagina')) if request.args.get('pagina') else 1
            limit = int(request.args.get('limite')) if request.args.get('limite') else 10
            sales, total = self.operations.findMany(self.sales_model, page, limit, empresa_id=request.args.get('empresa_id'))
            sales_array = [VendaBaseModel.from_orm(sale).dict() for sale in sales]

            return {
                'status': True,
                'message': 'Vendas carregadas com sucesso.',
                'data': {
                    'result': sales_array,
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'total_pages': math.ceil(total / limit)
                }
            }, 201
        except Exception as exc:
            return {
                'status': False,
                'message': str(exc),
                'data': None,
            }, 500

    def save_sale(self, venda_id: Optional[int] = None):
        try:
            user = self.functions.token_decript()
            request.json['responsavel_cadastro_id'] = user.get('login_id')

            # Pega o orçamento_id para validar o status antes de continuar
            budget_id = request.json.get('orcamento_id')
            budget = self.operations.findOne(self.budget_model, orcamento_id=budget_id)

            # Verifica o status do orçamento usando os enums
            from app.shared.enums.budget_status_enum import BudgetStatusEnum
            
            if budget.orcamento_status_id == BudgetStatusEnum.REPROVADO.value:
                return {
                    'status': False,
                    'message': 'Operação não permitida: o orçamento já foi reprovado.'
                }, 403

            if budget.orcamento_status_id == BudgetStatusEnum.APROVADO.value:
                return {
                    'status': False,
                    'message': 'Operação não permitida: o orçamento já foi aprovado.'
                }, 403

            # Pega dados de itens de orçamento para conversão em venda
            budget_items, _ = self.operations.findMany(self.budget_item_model, orcamento_id=budget_id)

            # Prepara os dados da venda com base no orçamento
            sale_data = self.convert_budget_to_sale(budget)
            sale_data['responsavel_cadastro_id'] = user.get('login_id')
            sale_data['gera_ordem_servico'] = True if request.json['gera_ordem_servico'] == True else False
            unique_fields = {'venda_id': venda_id} if venda_id else {}

            # Cria ou atualiza a venda
            result = self.operations.merge_insert_if_not_exists(self.sales_model, unique_fields, **sale_data)

            # Atualiza o orçamento para 'aprovado', usando o enum BudgetStatusEnum, e define data_aprovacao
            from app.shared.enums.budget_status_enum import BudgetStatusEnum
            
            self.operations.update(
                self.budget_model,
                {'orcamento_id': budget_id},
                orcamento_status_id=BudgetStatusEnum.APROVADO.value,
                data_aprovacao=datetime.now(),
                venda_id=result.venda_id
            )

            return {
                'status': True,
                'message': 'Venda salva com sucesso e orçamento atualizado.',
                'data': VendaBaseModel.from_orm(result).dict()
            }, 200 if venda_id else 201

        except Exception as exc:
            self.logger.log(message=str(exc), level='error')
            return {
                'status': False,
                'message': str(exc),
                'data': None,
            }, 500

    def virtual_delete_sale(self):
        try:
            delete_sale = self.operations.soft_delete(self.sales_model, request.args.get('venda_id'), request.args.get('empresa_id'))
            if delete_sale:
                return {
                    'status': True,
                    'message': 'Venda excluída com sucesso.'
                }, 201
            else:
                self.logger.log(message="Falha ao excluir venda.", level='error')
                return {
                    'status': False,
                    'message': 'Falha ao excluir venda.',
                }, 500
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')
            return {
                'status': False,
                'message': str(exc),
                'data': None,
            }, 500

    def get_all_sales_status(self):
        try:
            status_list = self.operations.findMany(self.sales_status_model)
            return {
                'status': True,
                'message': 'Status de vendas carregados com sucesso.',
                'data': [VendaStatusBaseModel.from_orm(status).dict() for status in status_list]
            }, 200
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')
            return {
                'status': False,
                'message': str(exc),
                'data': None,
            }, 500

    def convert_budget_to_sale(self, budget):
        # Converte os dados do orçamento para os dados da venda
        sale_data = {
            'orcamento_id': budget.orcamento_id,
            'empresa_id': budget.empresa_id,
            'data_cadastro': budget.data_cadastro,
            'valor': budget.valor - budget.desconto
        }
        return sale_data
