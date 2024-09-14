
from flask import request, jsonify, make_response

from app.shared.helpers.functions import Functions
from app.shared.helpers.model_operations import ModelOperations
from app.shared.singletons.logger import Logger
from models import ProdutoModel, ProdutoCategoriaModel, ProdutoSubcategoriaModel, ProdutoTipoModel
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

    # USAR A SERIALIZAÇÃO DESTA FUNÇÃO COMO BASE PARA AS OUTRAS
    def get_product_all(self):
        try:
            user = self.functions.token_decript()
            # companies = user.get('companies')
            page = int(request.args.get('page')) if request.args.get('page') else 1
            limit = int(request.args.get('limit')) if request.args.get('limit') else 10
            companies_list = request.args.get('company').split(',')
            companies = []
            for company in companies_list:
                companies.append(int(company))
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