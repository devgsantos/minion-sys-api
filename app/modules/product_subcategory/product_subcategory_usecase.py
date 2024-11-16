import math

from flask import request, jsonify, make_response

from app.shared.helpers.functions import Functions
from app.shared.helpers.model_operations import ModelOperations
from app.shared.singletons.logger import Logger
from models import ProdutoSubcategoriaModel


class ProductSubcategoryUseCase:
    def __init__(self):
        self.logger = Logger()
        self.operations = ModelOperations()
        self.functions = Functions()
        self.product_subcategory_model = ProdutoSubcategoriaModel

    def get_product_subcategory_all(self):
        try:
            search_term = request.args.get('termo_pesquisa') if request.args.get('termo_pesquisa') else None
            page = int(request.args.get('pagina'))
            limit = int(request.args.get('limite'))
            if search_term:
                search_fields = ['titulo', 'descricao', 'sku', 'detalhes_opcionais']
                subcategories, total = self.operations.findManyByTerm(self.product_subcategory_model, page, limit, search_term,
                                                                 search_fields,
                                                                 empresa_id=request.args.get('empresa_id'))
            else:
                subcategories, total = self.operations.findMany(self.product_subcategory_model, page, limit)
            subcategories_array = self.functions.instance_list_to_array(subcategories)

            return make_response(jsonify(
                {
                    'status': True,
                    'message': 'Subcategorias carregadas com sucesso.',
                    'data': {
                        'result': subcategories_array,
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

    def get_product_subcategory_by_id(self):
        print('by id')

    def create_product_subcategory(self):
        try:
            user = self.functions.token_decript()
            request.json['responsavel_cadastro_id'] = user.get('login_id')
            request.json['sigla'] = self.functions.gerar_sigla(request.json['titulo'])
            self.operations.insert(self.product_subcategory_model, **request.json)
            return make_response(jsonify(
                {
                    'status': True,
                    'message': 'Subcategoria de produtos criada com sucesso.'
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

    def update_product_subcategory(self):
        try:
            user = self.functions.token_decript()
            request.json['responsavel_cadastro_id'] = user.get('login_id')
            update_subcategory = self.operations.update(self.product_subcategory_model, request.json['produto_subcategoria_id'], **request.json)
            if update_subcategory:
                return make_response(jsonify(
                    {
                        'status': True,
                        'message': 'Subcategoria de produtos alterada com sucesso.'
                    }
                ), 201)
            else:
                return make_response(jsonify(
                    {
                        'status': True,
                        'message': 'Nenhuma subcategoria de produtos alterada.'
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

    def virtual_delete_product_subcategory(self):
        try:
            delete_product_subcategory = self.operations.soft_delete(self.product_subcategory_model, request.args.get('produto_subcategoria_id'), request.args.get('empresa_id'))
            if delete_product_subcategory:
                return make_response(jsonify(
                    {
                        'status': True,
                        'message': 'Subcategoria de produtos excluída com sucesso.'
                    }
                ), 201)
            else:
                self.logger.log(message=f"Falha ao excluir subcategoria de produtos.", level='error')

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
