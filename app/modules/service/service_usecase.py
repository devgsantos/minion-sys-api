
from flask import request, jsonify, make_response

from app.shared.helpers.functions import Functions
from app.shared.helpers.model_operations import ModelOperations
from app.shared.singletons.logger import Logger
from models import ServicoModel, RelServicoProdutoModel


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
        print('b')

    def create_service(self):
        try:
            user = self.functions.token_decript()
            data = request.json
            data['responsavel_cadastro_id'] = user.get('login_id')
            service_insert = {key: value for key, value in data.items() if key != 'produtos_relacionados'}
            result = self.operations.insert(self.service_model, **service_insert)
            if len(data['produtos_relacionados']) > 0:
                for product in request.json['produtos_relacionados']:
                    self.operations.insert(self.rel_service_product_model, servico_id=result['id'], produto_id=product)
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