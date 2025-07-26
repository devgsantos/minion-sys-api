import math
from typing import Optional

from flask import request, jsonify, make_response

from app.shared.helpers.functions import Functions
from app.shared.helpers.model_operations import ModelOperations
from app.shared.singletons.logger import Logger
from models import OrcamentoModel, OrcamentoItemModel, OrcamentoBaseModel, ProdutoModel, ServicoModel


class BudgetUseCase:
    def __init__(self):
        self.logger = Logger()
        self.operations = ModelOperations()
        self.functions = Functions()
        self.budget_model = OrcamentoModel
        self.budget_item_model = OrcamentoItemModel
        self.product_model = ProdutoModel
        self.service_model = ServicoModel


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
                        'total': total,
                        'total_pages': math.ceil(total / limit)
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

    def save_budget(self, orcamento_id: Optional[int] = None):
        try:
            # Decodifica o token e define o responsável pela ação
            user = self.functions.token_decript()
            request.json['responsavel_cadastro_id'] = user.get('login_id')

            # Separar produtos e serviços do orçamento
            products_items = [item for item in request.json.get('orcamento_itens', []) if item['tipo'] == 'produto']
            services_items = [item for item in request.json.get('orcamento_itens', []) if item['tipo'] == 'servico']

            # Calcula o valor do orçamento
            budget_value = self.calculate_items_value(products_items, services_items)
            request.json['valor'] = budget_value

            # Prepara os dados do orçamento
            budget_data = {key: value for key, value in request.json.items() if key != 'orcamento_itens'}

            # Atualiza ou cria o orçamento
            unique_fields = {'orcamento_id': request.json['orcamento_id']} if request.json['orcamento_id'] else {}
            result = self.operations.merge_insert_if_not_exists(self.budget_model, unique_fields, **budget_data)

            # Define o ID do orçamento criado ou atualizado
            orcamento_id = result.orcamento_id

            # Obter todos os itens existentes no banco de dados relacionados ao orçamento
            existing_items, count = self.operations.findManyNoffset(self.budget_item_model, orcamento_id=orcamento_id)

            # Função para acessar campos de forma segura
            def get_field(item, field_name):
                if isinstance(item, dict):
                    return item.get(field_name)
                return getattr(item, field_name, None)

            # Coletar os IDs de produtos e serviços enviados na nova requisição
            new_product_ids = {item['produto_id'] for item in products_items}
            new_service_ids = {item['servico_id'] for item in services_items}

            # Coletar os IDs de produtos e serviços existentes no banco de dados
            existing_product_ids = {
                get_field(item, 'produto_id') for item in existing_items if get_field(item, 'produto_id') is not None
            }
            existing_service_ids = {
                get_field(item, 'servico_id') for item in existing_items if get_field(item, 'servico_id') is not None
            }

            # Identificar quais itens precisam ser removidos
            product_ids_to_delete = existing_product_ids - new_product_ids
            service_ids_to_delete = existing_service_ids - new_service_ids

            # Função genérica para exclusão de itens
            def delete_obsolete_items(existing_items, ids_to_delete, id_type):
                for item in existing_items:
                    item_id = get_field(item, 'orcamento_item_id') or result.orcamento_id
                    item_key = get_field(item, id_type)

                    if item_key and item_key in ids_to_delete:
                        self.operations.soft_delete_relational(self.budget_item_model, item_id)

            # Excluir produtos e serviços obsoletos
            delete_obsolete_items(existing_items, product_ids_to_delete, 'produto_id')
            delete_obsolete_items(existing_items, service_ids_to_delete, 'servico_id')

            # Atualizar ou inserir novos produtos
            for item in products_items:
                self.operations.merge_insert_if_not_exists(
                    self.budget_item_model,
                    unique_fields={'orcamento_id': orcamento_id, 'produto_id': item['produto_id']},
                    quantidade_orcamento=item['quantidade_orcamento']
                )

            # Atualizar ou inserir novos serviços
            for item in services_items:
                self.operations.merge_insert_if_not_exists(
                    self.budget_item_model,
                    unique_fields={'orcamento_id': orcamento_id, 'servico_id': item['servico_id']},
                    quantidade_orcamento=item['quantidade_orcamento']
                )

            budget_value = self.calculate_items_value(products_items, services_items)

            # Retorna uma resposta de sucesso
            return make_response(jsonify(
                {
                    'status': True,
                    'message': 'Orçamento salvo com sucesso.'
                }
            ), 200 if orcamento_id else 201)

        except Exception as exc:
            # Loga e retorna uma resposta de erro
            self.logger.log(message=str(exc), level='error')
            return make_response(jsonify(
                {
                    'status': False,
                    'message': str(exc),
                    'data': None,
                }
            ), 500)

    def calculate_items_value(self, products_items, services_items):
        try:
            total_value = 0

            # Calcula o valor total dos produtos
            for item in products_items:
                produto = self.operations.findOne(self.product_model, produto_id=item['produto_id'])
                if not produto:
                    raise ValueError(f"Produto ID {item['produto_id']} não encontrado.")
                preco_venda = produto.preco_venda
                quantidade = item['quantidade_orcamento']
                total_value += preco_venda * quantidade

            # Calcula o valor total dos serviços
            for item in services_items:
                servico = self.operations.findOne(self.service_model, servico_id=item['servico_id'])
                if not servico:
                    raise ValueError(f"Serviço ID {item['servico_id']} não encontrado.")
                preco_mao_de_obra = servico.preco_mao_de_obra
                quantidade = item['quantidade_orcamento']
                total_value += preco_mao_de_obra * quantidade

            return total_value

        except Exception as exc:
            self.logger.log(message=f"Erro ao calcular o valor do orçamento: {str(exc)}", level='error')
            raise

    # LEGADO
    def create_budget(self):
        try:
            user = self.functions.token_decript()
            request.json['responsavel_cadastro_id'] = user.get('login_id')
            products_items = []
            services_items = []
            for item in request.json.get('orcamento_itens', []):
                if item.get('produto_id') is not None:
                    products_items.append(item)
                elif item.get('servico_id') is not None:
                    services_items.append(item)
            budget_value = self.calculate_items_value(products_items, services_items)
            request.json['valor'] = budget_value
            budget_insert = {key: value for key, value in request.json.items() if key != 'orcamento_itens'}
            result = self.operations.insert(self.budget_model, **budget_insert)
            if len(products_items) > 0:
                data_insert = {
                    'orcamento_id': result.orcamento_id,
                    'produto_id': [item['produto_id'] for item in products_items],  # Lista de IDs de produtos
                    'quantidade_orcamento': [item['quantidade_orcamento'] for item in products_items]  # Quantidades correspondentes
                }
                products_items_result = self.operations.insert(self.budget_item_model, **data_insert)
            if len(services_items) > 0:
                data_insert = {
                    'orcamento_id': result.orcamento_id,
                    'servico_id': [item['servico_id'] for item in services_items],  # Lista de IDs de produtos
                    'quantidade_orcamento': [item['quantidade_orcamento'] for item in services_items]  # Quantidades correspondentes
                }
                services_items_result = self.operations.insert(self.budget_item_model, **data_insert)
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

    # LEGADO
    def update_budget(self, orcamento_id: int):
        try:
            # Decodifica o token e define o responsável pela atualização
            user = self.functions.token_decript()
            request.json['responsavel_cadastro_id'] = user.get('login_id')

            # Separar produtos e serviços do orçamento
            products_items = []
            services_items = []
            for item in request.json.get('orcamento_itens', []):
                if item.get('produto_id') is not None:
                    products_items.append(item)
                elif item.get('servico_id') is not None:
                    services_items.append(item)

            # Calcula o valor atualizado do orçamento
            budget_value = self.calculate_items_value(products_items, services_items)
            request.json['valor'] = budget_value

            # Remove a chave 'orcamento_itens' antes de atualizar o orçamento
            budget_update = {key: value for key, value in request.json.items() if key != 'orcamento_itens'}

            # Atualiza ou cria o orçamento
            self.operations.merge_insert_if_not_exists(
                self.budget_model,
                unique_fields={'orcamento_id': orcamento_id},
                **budget_update
            )

            # Obtém os produtos e serviços existentes no banco
            existing_items = self.operations.findManyNoffset(
                self.budget_item_model, orcamento_id=orcamento_id
            )

            # Coleta os IDs dos itens enviados na nova requisição
            new_product_ids = {item['produto_id'] for item in products_items}
            new_service_ids = {item['servico_id'] for item in services_items}

            # Identifica os itens existentes que não estão mais na nova lista
            to_delete = [
                item for item in existing_items
                if (item.produto_id and item.produto_id not in new_product_ids) or
                   (item.servico_id and item.servico_id not in new_service_ids)
            ]

            # Remove os itens obsoletos
            for item in to_delete:
                self.operations.delete(self.budget_item_model, id=item.id)

            # Atualiza ou insere os produtos
            for item in products_items:
                self.operations.merge_insert_if_not_exists(
                    self.budget_item_model,
                    unique_fields={'orcamento_id': orcamento_id, 'produto_id': item['produto_id']},
                    quantidade_orcamento=item['quantidade_orcamento']
                )

            # Atualiza ou insere os serviços
            for item in services_items:
                self.operations.merge_insert_if_not_exists(
                    self.budget_item_model,
                    unique_fields={'orcamento_id': orcamento_id, 'servico_id': item['servico_id']},
                    quantidade_orcamento=item['quantidade_orcamento']
                )

            # Retorna resposta de sucesso
            return make_response(jsonify(
                {
                    'status': True,
                    'message': 'Orçamento atualizado com sucesso.'
                }
            ), 200)

        except Exception as exc:
            # Loga e retorna uma resposta de erro
            self.logger.log(message=str(exc), level='error')
            return make_response(jsonify(
                {
                    'status': False,
                    'message': str(exc),
                    'data': None,
                }
            ), 500)


        except Exception as exc:
            # Loga e retorna uma resposta de erro
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

    def calculate_items_value(self, products_items, services_items):
        products_value = 0
        services_value = 0
        if len(products_items) > 0:
            products_ids = [item['produto_id'] for item in products_items if 'produto_id' in item]
            products, products_count = self.operations.findManyNoffset(self.product_model, produto_id=products_ids)
            products_value = sum(product.preco_venda for product in products)
        if len(services_items) > 0:
            services_ids = [item['servico_id'] for item in services_items if 'servico_id' in item]
            services, services_count = self.operations.findManyNoffset(self.service_model, servico_id=services_ids)
            services_value = sum(service.preco_mao_de_obra for service in services)
        return products_value + services_value
