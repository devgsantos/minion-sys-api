import math

from flask import request, jsonify, make_response

from app.shared.helpers.functions import Functions
from app.shared.helpers.model_operations import ModelOperations
from app.shared.singletons.logger import Logger
from models import ServicoModel, RelServicoProdutoModel, ServicoBaseModel


class ServiceUseCase:
    def __init__(self):
        self.logger = Logger()
        self.operations = ModelOperations()
        self.functions = Functions()
        self.service_model = ServicoModel
        # self.rel_service_product_model = RelServicoProdutoModel

    def get_service_by_id(self):
        print('a')

    def get_service_all(self):
        try:
            search_term = request.args.get('termo_pesquisa') if request.args.get('termo_pesquisa') else None
            page = int(request.args.get('pagina')) if request.args.get('pagina') else 1
            limit = int(request.args.get('limite')) if request.args.get('limite') else 10
            if search_term:
                search_fields = ['titulo', 'descricao', 'sku', 'detalhes_opcionais']
                services, total = self.operations.findManyByTerm(self.service_model, page, limit, search_term,
                                                                 search_fields, empresa_id=request.args.get('empresa_id'))
            else:
                services, total = self.operations.findMany(self.service_model, page, limit, empresa_id=request.args.get('empresa_id'))
            services_array = [ServicoBaseModel.from_orm(service).dict() for service in services]

            return make_response(jsonify(
                {
                    'status': True,
                    'message': 'Servicos carregados com sucesso.',
                    'data': {
                        'result': services_array,
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

    def create_service(self):
        try:
            user = self.functions.token_decript()
            data = request.json
            data['responsavel_cadastro_id'] = user.get('login_id')
            service_insert = {key: value for key, value in data.items() if key != 'produtos_relacionados'}
            result = self.operations.insert(self.service_model, **service_insert)
            # if len(data['produtos_relacionados']) > 0:
            #     for product in request.json['produtos_relacionados']:
            #         self.operations.insert(self.rel_service_product_model, servico_id=result.servico_id, produto_id=product)
            return make_response(jsonify(
                {
                    'status': True,
                    'message': 'Servico criado com sucesso.'
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

    def update_service(self):
        try:
            user = self.functions.token_decript()
            data = request.json
            data['responsavel_cadastro_id'] = user.get('login_id')
            service_update = {key: value for key, value in data.items() if key != 'produtos_relacionados' and key !='servico_id'}
            self.operations.update(self.service_model, data['servico_id'], **service_update)
            return make_response(jsonify(
                {
                    'status': True,
                    'message': 'Servico alterado com sucesso.'
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

    def virtual_delete_service(self):
        try:
            excluir_servico = self.operations.soft_delete(self.service_model, request.args.get('servico_id'), request.args.get('empresa_id'))
            if excluir_servico:
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