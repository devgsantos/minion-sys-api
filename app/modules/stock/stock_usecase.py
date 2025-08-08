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
            
            if search_term:
                # Para pesquisar no estoque, relacionamos com produtos para buscar também pelo nome do produto
                search_fields = ['produto.nome', 'quantidade_disponivel']
                stocks, total = self.operations.findManyByTerm(self.stock_model, page, limit, search_term,
                                                             search_fields)
            else:
                stocks, total = self.operations.findMany(self.stock_model, page, limit)
            
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
            if stock:
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
            stocks, total = self.operations.findMany(self.stock_model, produto_id=request.args.get('produto_id'))
            
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
            product = self.operations.findOne(self.product_model, produto_id=data['produto_id'])
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
            if not stock:
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
            delete_stock = self.operations.soft_delete(
                self.stock_model, 
                request.args.get('estoque_id')
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
            # Buscar o orçamento pelo ID
            budget = self.budget_model.find_by_id(budget_id)
            
            if not budget:
                return {
                    'status': False,
                    'message': 'Orçamento não encontrado.',
                    'data': None
                }
            
            # Verificar se o orçamento tem itens
            if not budget.items or len(budget.items) == 0:
                return {
                    'status': True,
                    'message': 'O orçamento não possui itens.',
                    'data': None
                }
                
            # Extrair todos os IDs de produtos do orçamento
            produto_ids = [item.produto_id for item in budget.items if item.produto_id is not None]
            
            if not produto_ids:
                return {
                    'status': True,
                    'message': 'O orçamento não possui produtos.',
                    'data': None
                }
                
            # Buscar todos os estoques relacionados a esses produtos em uma única consulta
            estoques = []
            for produto_id in produto_ids:
                estoque_items = self.stock_model.find_by_produto_id(produto_id)
                estoques.extend(estoque_items)
            
            # Criar um dicionário para acesso rápido ao estoque por produto_id
            estoque_por_produto = {}
            for estoque in estoques:
                if estoque.produto_id in estoque_por_produto:
                    # Se já existe um registro para esse produto, somamos a quantidade disponível
                    estoque_por_produto[estoque.produto_id] += estoque.quantidade_disponivel
                else:
                    estoque_por_produto[estoque.produto_id] = estoque.quantidade_disponivel
            
            # Verificar se cada produto tem estoque suficiente
            produtos_insuficientes = []
            for item in budget.items:
                if not item.produto_id:
                    continue
                    
                quantidade_necessaria = item.quantidade or 0
                quantidade_disponivel = estoque_por_produto.get(item.produto_id, 0)
                
                if quantidade_disponivel < quantidade_necessaria:
                    # O produto já está relacionado no objeto do item
                    nome_produto = item.produto.nome if hasattr(item, 'produto') and item.produto else f"Produto #{item.produto_id}"
                    
                    produtos_insuficientes.append({
                        "produto_id": item.produto_id,
                        "nome_produto": nome_produto,
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
