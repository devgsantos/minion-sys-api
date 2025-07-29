import math
import requests

from flask import request

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
            if search_term:
                search_fields = ['titulo', 'descricao', 'sku', 'detalhes_opcionais']
                products, total = self.operations.findManyByTerm(self.product_model, page, limit, search_term, search_fields, empresa_id=request.args.get('empresa_id'))
            else:
                products, total = self.operations.findMany(self.product_model, page, limit, empresa_id=request.args.get('empresa_id'))
            products_array = [ProdutoBaseModel.from_orm(product).dict() for product in products]
            # products_array = self.functions.instance_list_to_array(products)

            return {
                'status': True,
                'message': 'Produtos carregados com sucesso.',
                'data': {
                    'result': products_array,
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
            return {
                'status': True,
                'message': 'Produto criado com sucesso.'
            }, 201
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')
            return {
                'status': False,
                'message': str(exc),
                'data': None,
            }, 500

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
            return {
                'status': True,
                'message': 'Produto alterado com sucesso.'
            }, 201
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')
            return {
                'status': False,
                'message': str(exc),
                'data': None,
            }, 500

    def virtual_delete_product(self):
        try:
            delete_product = self.operations.soft_delete(self.product_model, request.args.get('produto_id'), request.args.get('empresa_id'))
            if delete_product:
                return {
                    'status': True,
                    'message': 'Produto excluído com sucesso.'
                }, 201
            else:
                self.logger.log(message=f"Falha ao excluir produto.", level='error')

                return {
                    'status': False,
                    'message': 'Falha ao excluir produto.',
                }, 500
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')
            return {
                'status': False,
                'message': str(exc),
                'data': None,
            }, 500

    def search_new_by_ean(self):
        try:
            url = f"https://world.openfoodfacts.org/api/v0/product/{request.args.get('ean') }.json"
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                return {
                    "status": False,
                    "message": "Erro ao acessar a API externa.",
                    "result": None
                }, 502

            data = response.json()
            product = data.get("product", {})
            if not product:
                return {
                    "status": False,
                    "message": "Produto não encontrado na base externa.",
                    "result": None
                }, 404

            return {
                "status": True,
                "message": "Produto encontrado.",
                "result": {
                    "titulo": product.get("product_name", "").strip(),
                    "descricao": product.get("ingredients_text", "").strip(),
                    "marca": product.get("brands", "").strip(),
                    "imagem": product.get("image_url", "").strip(),
                    "categorias": product.get("categories", "").strip()
                }
            }, 200

        except Exception as e:
            return {
                "status": False,
                "message": f"Erro inesperado: {str(e)}",
                "result": None
            }, 500