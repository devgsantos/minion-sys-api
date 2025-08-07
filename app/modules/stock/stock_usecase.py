import math

from flask import request

from app.shared.helpers.functions import Functions
from app.shared.helpers.model_operations import ModelOperations
from app.shared.singletons.logger import Logger
from models import EstoqueModel, EstoqueBaseModel, ProdutoModel


class StockUseCase:
    def __init__(self):
        self.logger = Logger()
        self.operations = ModelOperations()
        self.functions = Functions()
        self.stock_model = EstoqueModel
        self.product_model = ProdutoModel

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


    def verificar_estoque_em_orcamento(self, budget_items: list[dict]) -> bool:
        """
        Verifica se todos os produtos do orçamento possuem estoque suficiente.

        :param budget_items: Lista de dicionários com 'produto_id' e 'quantidade'
        :return: Lista de produtos com estoque insuficiente (vazia se tudo OK)
        """
        operations = ModelOperations()
        produtos_insuficientes = []

        for item in budget_items:
            produto_id = item.get('produto_id')
            quantidade_necessaria = item.get('quantidade')

            estoque = operations.findOne(EstoqueModel, produto_id=produto_id)

            if not estoque or estoque.quantidade_disponivel < quantidade_necessaria:
                produtos_insuficientes.append({
                    "produto_id": produto_id,
                    "quantidade_necessaria": quantidade_necessaria,
                    "quantidade_disponivel": estoque.quantidade_disponivel if estoque else 0
                })

        return produtos_insuficientes
