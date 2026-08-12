import math

from flask import request

from app.shared.helpers.functions import Functions
from app.shared.helpers.model_operations import ModelOperations
from app.shared.singletons.logger import Logger
from models import EstoqueModel, EstoqueBaseModel, ProdutoModel, OrcamentoModel, OrcamentoItemModel


class StockUseCase:
    def __init__(self):
        self.logger = Logger()
        self.operations = ModelOperations()
        self.functions = Functions()
        self.stock_model = EstoqueModel
        self.product_model = ProdutoModel
        self.budget_model = OrcamentoModel
        self.budget_item_model = OrcamentoItemModel

    def get_stock_all(self):
        try:
            search_term = request.args.get('termo_pesquisa') if request.args.get('termo_pesquisa') else None
            page = int(request.args.get('pagina')) if request.args.get('pagina') else 1
            limit = int(request.args.get('limite')) if request.args.get('limite') else 10
            
            stocks, total = self.operations.find_many_by_relation(
                self.stock_model,
                self.product_model,
                self.stock_model.produto_id == self.product_model.produto_id,
                page,
                limit,
                empresa_id=request.company_id,
            )
            
            stocks_array = [EstoqueBaseModel.from_orm(stock).dict() for stock in stocks]

            return {
                'status': True,
                'message': 'Estoque carregado com sucesso.',
                'data': {
                    'result': stocks_array,
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'total_pages': math.ceil(total / limit)
                }
            }, 200
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')
            return {
                'status': False,
                'message': str(exc),
                'data': None,
            }, 500

    def get_stock_by_id(self):
        try:
            stock = self.operations.findOne(self.stock_model, estoque_id=request.args.get('estoque_id'))
            if stock and self._find_authorized_product(stock.produto_id):
                return {
                    'status': True,
                    'message': 'Registro de estoque encontrado com sucesso.',
                    'data': EstoqueBaseModel.from_orm(stock).dict()
                }, 200
            else:
                return {
                    'status': False,
                    'message': 'Registro de estoque não encontrado.',
                    'data': None
                }, 404
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')
            return {
                'status': False,
                'message': str(exc),
                'data': None,
            }, 500

    def get_stock_by_product(self):
        try:
            product_id = request.args.get('produto_id')
            if not self._find_authorized_product(product_id):
                return {
                    'status': False,
                    'message': 'Produto não encontrado.',
                    'data': None,
                }, 404
            stocks, total = self.operations.findMany(self.stock_model, produto_id=product_id)
            
            if stocks:
                stocks_array = [EstoqueBaseModel.from_orm(stock).dict() for stock in stocks]
                return {
                    'status': True,
                    'message': 'Estoque do produto carregado com sucesso.',
                    'data': stocks_array
                }, 200
            else:
                return {
                    'status': False,
                    'message': 'Nenhum estoque encontrado para este produto.',
                    'data': []
                }, 200
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')
            return {
                'status': False,
                'message': str(exc),
                'data': None,
            }, 500

    def create_stock(self):
        try:
            user = self.functions.token_decript()
            data = request.json
            
            # Verificar se o produto existe
            product = self._find_authorized_product(data['produto_id'])
            if not product:
                return {
                    'status': False,
                    'message': f"Produto ID {data['produto_id']} não encontrado.",
                    'data': None
                }, 400
                
            # Verificar se já existe um registro para este produto e tipo de estoque
            existing_stock = self.operations.findOne(
                self.stock_model, 
                produto_id=data['produto_id'], 
                estoque_tipo_id=data['estoque_tipo_id']
            )
            
            if existing_stock:
                # Se já existe, atualiza a quantidade
                existing_stock.quantidade_disponivel += data['quantidade_disponivel']
                self.operations.update(
                    self.stock_model,
                    existing_stock.estoque_id,
                    quantidade_disponivel=existing_stock.quantidade_disponivel
                )
                
                return {
                    'status': True,
                    'message': 'Estoque atualizado com sucesso.',
                    'data': {
                        'estoque_id': existing_stock.estoque_id,
                        'quantidade_disponivel': existing_stock.quantidade_disponivel
                    }
                }, 200
            else:
                # Se não existe, cria um novo registro
                result = self.operations.insert(self.stock_model, **data)
                
                return {
                    'status': True,
                    'message': 'Registro de estoque criado com sucesso.',
                    'data': {
                        'estoque_id': result.estoque_id,
                        'quantidade_disponivel': result.quantidade_disponivel
                    }
                }, 201
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')
            return {
                'status': False,
                'message': str(exc),
                'data': None,
            }, 500

    def update_stock(self):
        try:
            user = self.functions.token_decript()
            data = request.json
            
            # Verificar se o registro de estoque existe
            stock = self.operations.findOne(self.stock_model, estoque_id=data['estoque_id'])
            if not stock or not self._find_authorized_product(stock.produto_id):
                return {
                    'status': False,
                    'message': f"Registro de estoque ID {data['estoque_id']} não encontrado.",
                    'data': None
                }, 404
                
            # Atualizar o registro
            update_data = {key: value for key, value in data.items() if key != 'estoque_id'}
            update_stock = self.operations.update(self.stock_model, data['estoque_id'], **update_data)
            
            if update_stock:
                return {
                    'status': True,
                    'message': 'Estoque atualizado com sucesso.'
                }, 200
            else:
                return {
                    'status': False,
                    'message': 'Nenhuma alteração realizada no estoque.'
                }, 304
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')
            return {
                'status': False,
                'message': str(exc),
                'data': None,
            }, 500

    def virtual_delete_stock(self):
        try:
            stock = self.operations.findOne(
                self.stock_model,
                estoque_id=request.args.get('estoque_id'),
            )
            if not stock or not self._find_authorized_product(stock.produto_id):
                return {
                    'status': False,
                    'message': 'Registro de estoque não encontrado.',
                    'data': None,
                }, 404

            delete_stock = self.operations.soft_delete_where(
                self.stock_model,
                estoque_id=stock.estoque_id,
                produto_id=stock.produto_id,
            )
            
            if delete_stock:
                return {
                    'status': True,
                    'message': 'Registro de estoque excluído com sucesso.'
                }, 200
            else:
                self.logger.log(message=f"Falha ao excluir registro de estoque.", level='error')
                return {
                    'status': False,
                    'message': 'Falha ao excluir registro de estoque.',
                }, 500
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')
            return {
                'status': False,
                'message': str(exc),
                'data': None,
            }, 500

    def _find_authorized_product(self, product_id):
        return self.operations.findOne(
            self.product_model,
            produto_id=product_id,
            empresa_id=request.company_id,
        )
            
    def check_budget_stock(self):
        """
        Endpoint para verificar se há estoque suficiente para todos os produtos de um orçamento.
        
        Parâmetros de requisição:
        - orcamento_id: ID do orçamento a verificar
        
        Retorna:
        - Lista de produtos com estoque insuficiente ou mensagem de sucesso se todos têm estoque
        """
        try:
            budget_id = request.args.get('orcamento_id')
            if not budget_id:
                return {
                    'status': False,
                    'message': "O parâmetro 'orcamento_id' é obrigatório.",
                    'data': None
                }, 400
            
            # Verificar disponibilidade de estoque
            resultado = self.check_stock_by_product(int(budget_id))
            
            # Se o orçamento não foi encontrado, retorna 404
            if not resultado['status'] and resultado['message'] == 'Orçamento não encontrado.':
                return resultado, 404
                
            # Qualquer outro resultado mantém o código 200
            return resultado, 200
                
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')
            return {
                'status': False,
                'message': f'Erro ao verificar estoque: {str(exc)}',
                'data': None,
            }, 500


    def check_stock_by_product(self, budget_id: int) -> dict:
        """
        Verifica se todos os produtos do orçamento possuem estoque suficiente.
        Busca todos os produtos de uma vez para evitar múltiplas consultas ao banco.

        :param budget_id: ID do orçamento a verificar
        :return: Dicionário com status, mensagem e dados (se aplicável)
        """
        try:
            budget = self.operations.findOne(
                self.budget_model,
                orcamento_id=budget_id,
                empresa_id=request.company_id,
            )
            
            if not budget:
                return {
                    'status': False,
                    'message': 'Orçamento não encontrado.',
                    'data': None
                }
            
            budget_items, _ = self.operations.findManyNoffset(
                self.budget_item_model,
                orcamento_id=budget_id,
            )
            if not budget_items:
                return {
                    'status': True,
                    'message': 'O orçamento não possui itens.',
                    'data': None
                }
                
            # Extrair todos os IDs de produtos do orçamento
            produto_ids = [
                item.produto_id for item in budget_items
                if item.produto_id is not None
            ]
            
            if not produto_ids:
                return {
                    'status': True,
                    'message': 'O orçamento não possui produtos.',
                    'data': None
                }
                
            # Buscar todos os estoques relacionados a esses produtos em uma única consulta
            estoque_por_produto = {}
            for produto_id in set(produto_ids):
                if not self._find_authorized_product(produto_id):
                    estoque_por_produto[produto_id] = 0
                    continue
                stocks, _ = self.operations.findManyNoffset(
                    self.stock_model,
                    produto_id=produto_id,
                )
                estoque_por_produto[produto_id] = sum(
                    stock.quantidade_disponivel for stock in stocks
                )
            
            # Verificar se cada produto tem estoque suficiente
            produtos_insuficientes = []
            required_by_product = {}
            for item in budget_items:
                if not item.produto_id:
                    continue
                required_by_product[item.produto_id] = (
                    required_by_product.get(item.produto_id, 0)
                    + (item.quantidade_orcamento or 0)
                )

            for produto_id, quantidade_necessaria in required_by_product.items():
                quantidade_disponivel = estoque_por_produto.get(produto_id, 0)
                
                if quantidade_disponivel < quantidade_necessaria:
                    # O produto já está relacionado no objeto do item
                    produtos_insuficientes.append({
                        "produto_id": produto_id,
                        "quantidade_necessaria": quantidade_necessaria,
                        "quantidade_disponivel": quantidade_disponivel
                    })
            
            # Retorna o resultado formatado
            if produtos_insuficientes:
                return {
                    'status': False,
                    'message': 'Estoque insuficiente para alguns produtos do orçamento.',
                    'data': {
                        'produtos_insuficientes': produtos_insuficientes
                    }
                }
            else:
                return {
                    'status': True,
                    'message': 'Estoque disponível para todos os produtos do orçamento.',
                    'data': None
                }
            
        except Exception as exc:
            self.logger.log(message=f"Erro ao verificar estoque em orçamento: {str(exc)}", level='error')
            # Em caso de erro, retornamos um objeto de resposta formatado
            return {
                'status': False,
                'message': f"Erro ao verificar disponibilidade de estoque: {str(exc)}",
                'data': None
            }
