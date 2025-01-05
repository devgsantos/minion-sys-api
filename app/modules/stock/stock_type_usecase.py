import math

from flask import request, jsonify, make_response

from app.shared.helpers.functions import Functions
from app.shared.helpers.model_operations import ModelOperations
from app.shared.singletons.logger import Logger
from models import ProdutoTipoModel, EstoqueTipoModel


class StockTypeUseCase:
    def __init__(self):
        self.logger = Logger()
        self.operations = ModelOperations()
        self.functions = Functions()
        self.stock_type_model = EstoqueTipoModel

    def get_stock_type_all(self):
        try:
            search_term = request.args.get('termo_pesquisa') if request.args.get('termo_pesquisa') else None
            page = int(request.args.get('pagina'))
            limit = int(request.args.get('limite'))
            if search_term:
                search_fields = ['titulo', 'descricao', 'detalhes_opcionais']
                types, total = self.operations.findManyByTerm(self.stock_type_model, page, limit, search_term,
                                                                 search_fields,
                                                                 empresa_id=request.args.get('empresa_id'))
            else:
                types, total = self.operations.findMany(self.stock_type_model, page, limit)
            types_array = self.functions.instance_list_to_array(types)

            return make_response(jsonify(
                {
                    'status': True,
                    'message': 'Tipos de produtos carregadas com sucesso.',
                    'data': {
                        'result': types_array,
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

    def get_product_type_by_id(self):
        print('by id')

    def create_product_type(self):
        try:
            user = self.functions.token_decript()
            request.json['responsavel_cadastro_id'] = user.get('login_id')
            self.operations.insert(self.stock_type_model, **request.json)
            return make_response(jsonify(
                {
                    'status': True,
                    'message': 'Tipo de produto criado com sucesso.'
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

    def update_product_type(self):
        try:
            user = self.functions.token_decript()
            request.json['responsavel_cadastro_id'] = user.get('login_id')
            update_type = self.operations.update(self.stock_type_model, request.json['produto_tipo_id'], **request.json)
            if update_type:
                return make_response(jsonify(
                    {
                        'status': True,
                        'message': 'Tipos de produto alterado com sucesso.'
                    }
                ), 201)
            else:
                return make_response(jsonify(
                    {
                        'status': True,
                        'message': 'Nenhum tipo de produto alterada.'
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

    def virtual_delete_product_type(self):
        try:
            delete_type = self.operations.soft_delete(self.stock_type_model, request.args.get('produto_tipo_id'), request.args.get('empresa_id'))
            if delete_type:
                return make_response(jsonify(
                    {
                        'status': True,
                        'message': 'Tipo de produto excluído com sucesso.'
                    }
                ), 201)
            else:
                self.logger.log(message=f"Falha ao excluir tipo de produto.", level='error')

                return make_response(jsonify(
                    {
                        'status': False,
                        'message': 'Falha ao excluir tipo de produto.',
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
