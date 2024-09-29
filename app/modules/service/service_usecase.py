
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
        self.rel_service_product_model = RelServicoProdutoModel

    def get_service_by_id(self):
        print('a')

    def get_service_all(self):
        try:
            page = int(request.args.get('page')) if request.args.get('page') else 1
            limit = int(request.args.get('limit')) if request.args.get('limit') else 10
            companies_list = request.args.get('company').split(',')
            companies = []
            for company in companies_list:
                companies.append(int(company))
            services, total = self.operations.findMany(self.service_model, page, limit, empresa_id=companies)
            # for service in services:
            #     for produto in service
            services_array = [ServicoBaseModel.from_orm(service).dict() for service in services]
            # services_array = self.functions.instance_list_to_array(services)

            return make_response(jsonify(
                {
                    'status': True,
                    'message': 'Servicos carregados com sucesso.',
                    'data': {
                        'result': services_array,
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

    def create_service(self):
        try:
            user = self.functions.token_decript()
            data = request.json
            data['responsavel_cadastro_id'] = user.get('login_id')
            service_insert = {key: value for key, value in data.items() if key != 'produtos_relacionados'}
            result = self.operations.insert(self.service_model, **service_insert)
            if len(data['produtos_relacionados']) > 0:
                for product in request.json['produtos_relacionados']:
                    self.operations.insert(self.rel_service_product_model, servico_id=result.servico_id, produto_id=product)
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