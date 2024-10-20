
from flask import request, jsonify, make_response

from app.shared.helpers.functions import Functions
from app.shared.helpers.model_operations import ModelOperations
from app.shared.singletons.logger import Logger
from models import ProdutoModel, ProdutoCategoriaModel, ProdutoSubcategoriaModel, ProdutoTipoModel, EstoqueModel
from models.produto_model import ProdutoBaseModel


class ProductUseCase:
    def __init__(self):
        self.logger = Logger()
        self.operations = ModelOperations()
        self.functions = Functions()
        self.product_model = ProdutoModel
        self.product_category_model = ProdutoCategoriaModel
        self.product_subcategory_model = ProdutoSubcategoriaModel
        self.product_type_model = ProdutoTipoModel
        self.stock_model = EstoqueModel


    # USAR A SERIALIZAÇÃO DESTA FUNÇÃO COMO BASE PARA AS OUTRAS
    def get_all_product(self):
        try:
            search_term = request.args.get('termo_pesquisa') if request.args.get('termo_pesquisa') else None
            page = int(request.args.get('pagina')) if request.args.get('pagina') else 1
            limit = int(request.args.get('limite')) if request.args.get('limite') else 10
            companies_list = request.args.get('empresa_id').split(',')
            companies = []
            for company in companies_list:
                companies.append(int(company))
            if search_term:
                search_fields = ['titulo', 'descricao', 'sku', 'detalhes_opcionais']
                products, total = self.operations.findManyByTerm(self.product_model, page, limit, search_term, search_fields, empresa_id=companies)
            else:
                products, total = self.operations.findMany(self.product_model, page, limit, empresa_id=companies)
            products_array = [ProdutoBaseModel.from_orm(product).dict() for product in products]
            # products_array = self.functions.instance_list_to_array(products)

            return make_response(jsonify(
                {
                    'status': True,
                    'message': 'Produtos carregados com sucesso.',
                    'data': {
                        'result': products_array,
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


    def create_product(self):
        try:
            user = self.functions.token_decript()
            request.json['responsavel_cadastro_id'] = user.get('login_id')
            product_insert = {key: value for key, value in request.json.items() if key != 'estoque'}
            result = self.operations.insert(self.product_model, **product_insert)
            if len(request.json['estoque']) > 0:
                for param in request.json['estoque']:
                    insert_data = {
                        "produto_id": result.produto_id,
                        "estoque_tipo_id": param['estoque_tipo_id'],
                        "quantidade_disponivel": param['quantidade_disponivel']
                    }
                    self.operations.insert(self.stock_model, **insert_data)
            return make_response(jsonify(
                {
                    'status': True,
                    'message': 'Produto criado com sucesso.'
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

    def update_product(self):
        try:
            user = self.functions.token_decript()
            request.json['responsavel_cadastro_id'] = user.get('login_id')
            product_update = {key: value for key, value in request.json.items() if key != 'estoque' and key !='produto_id'}
            self.operations.update(self.product_model, request.json['produto_id'], **product_update)
            if len(request.json['estoque']) > 0:
                for param in request.json['estoque']:
                    unique_data = {
                        "produto_id": request.json['produto_id'],
                        "estoque_tipo_id": param['estoque_tipo_id']
                    }
                    data_to_update = {
                        "quantidade_disponivel": param['quantidade_disponivel']
                    }
                    self.operations.merge_insert_if_not_exists(self.stock_model, unique_fields=unique_data, **data_to_update)
            return make_response(jsonify(
                {
                    'status': True,
                    'message': 'Produto alterado com sucesso.'
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

    def virtual_delete_product(self):
        try:
            excluir_produto = self.operations.soft_delete(self.product_model, request.args.get('produto_id'), request.args.get('empresa_id'))
            if excluir_produto:
                return make_response(jsonify(
                    {
                        'status': True,
                        'message': 'Produto excluído com sucesso.'
                    }
                ), 201)
            else:
                self.logger.log(message=f"Falha ao excluir produto.", level='error')

                return make_response(jsonify(
                    {
                        'status': False,
                        'message': 'Falha ao excluir produto.',
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
