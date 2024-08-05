
from flask import request, jsonify, make_response

from app.shared.helpers.functions import Functions
from app.shared.helpers.model_operations import ModelOperations
from app.shared.singletons.logger import Logger
from models import ProdutoModel, ProdutoCategoriaModel, ProdutoSubcategoriaModel, ProdutoTipoModel


class ProductUseCase:
    def __init__(self):
        self.logger = Logger()
        self.operations = ModelOperations()
        self.functions = Functions()
        self.product_model = ProdutoModel
        self.product_category_model = ProdutoCategoriaModel
        self.product_subcategory_model = ProdutoSubcategoriaModel
        self.product_type_model = ProdutoTipoModel

    def create_product(self):
        try:
            user = self.functions.token_decript()
            request.json['responsavel_cadastro_id'] = user.get('login_id')
            self.operations.insert(self.product_model, **request.json)
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
