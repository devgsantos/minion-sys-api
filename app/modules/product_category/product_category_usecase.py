import math

from flask import request, jsonify, make_response

from app.shared.helpers.functions import Functions
from app.shared.helpers.model_operations import ModelOperations
from app.shared.singletons.logger import Logger
from models import ProdutoCategoriaModel


class ProductCategoryUseCase:
    def __init__(self):
        self.logger = Logger()
        self.operations = ModelOperations()
        self.functions = Functions()
        self.product_category_model = ProdutoCategoriaModel

    #  ESTA TRATATIVA DE SERIALIZAÇÃO DEVE SER USADO EM MODELOS GENÉRICOS
    def get_product_category_all(self):
        try:
            search_term = request.args.get('termo_pesquisa') if request.args.get('termo_pesquisa') else None
            page = int(request.args.get('pagina'))
            limit = int(request.args.get('limite'))
            if search_term:
                search_fields = ['titulo', 'descricao', 'sku', 'detalhes_opcionais']
                categories, total = self.operations.findManyByTerm(self.product_category_model, page, limit, search_term,
                                                                 search_fields,
                                                                 empresa_id=request.args.get('empresa_id'))
            else:
                categories, total = self.operations.findMany(self.product_category_model, page, limit)
            categories_array = self.functions.instance_list_to_array(categories)

            return make_response(jsonify(
                {
                    'status': True,
                    'message': 'Categorias carregadas com sucesso.',
                    'data': {
                        'result': categories_array,
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

    def get_product_category_by_id(self):
        print('by id')

    def create_product_category(self):
        try:
            user = self.functions.token_decript()
            request.json['responsavel_cadastro_id'] = user.get('login_id')
            request.json['sigla'] = self.functions.gerar_sigla(request.json['titulo'])
            self.operations.insert(self.product_category_model, **request.json)
            return make_response(jsonify(
                {
                    'status': True,
                    'message': 'Categoria de produtos criada com sucesso.'
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

    def update_product_category(self):
        try:
            user = self.functions.token_decript()
            request.json['responsavel_cadastro_id'] = user.get('login_id')
            update_category = self.operations.update(self.product_category_model, request.json['produto_categoria_id'], **request.json)
            if update_category:
                return make_response(jsonify(
                    {
                        'status': True,
                        'message': 'Categoria de produtos alterada com sucesso.'
                    }
                ), 201)
            else:
                return make_response(jsonify(
                    {
                        'status': True,
                        'message': 'Nenhuma categoria de produtos alterada.'
                    }
                ), 204)
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')

            return make_response(jsonify(
                {
                    'status': False,
                    'message': str(exc),
                    'data': None,
                }
            ), 500)

    def virtual_delete_product_category(self):
        try:
            delete_product_category = self.operations.soft_delete(self.product_category_model, request.args.get('produto_categoria_id'), request.args.get('empresa_id'))
            if delete_product_category:
                return make_response(jsonify(
                    {
                        'status': True,
                        'message': 'Categoria de produtos excluída com sucesso.'
                    }
                ), 201)
            else:
                self.logger.log(message=f"Falha ao excluir categoria de produtos.", level='error')

                return make_response(jsonify(
                    {
                        'status': False,
                        'message': 'Falha ao excluir categoria de produtos.',
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
