
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

    def create_product_category(self):
        try:
            user = self.functions.token_decript()
            request.json['responsavel_cadastro_id'] = user.get('login_id')
            request.json['sigla'] = self.functions.gerar_sigla(request.json['titulo'])
            self.operations.insert(self.product_category_model, **request.json)
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

