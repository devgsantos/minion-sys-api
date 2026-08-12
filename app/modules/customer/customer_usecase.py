import math

from flask import request

from app.shared.helpers.functions import Functions
from app.shared.helpers.model_operations import ModelOperations
from app.shared.singletons.logger import Logger
from models import ClienteModel, ClienteBaseModel


class CustomerUseCase:
    def __init__(self):
        self.logger = Logger()
        self.operations = ModelOperations()
        self.functions = Functions()
        self.customer_model = ClienteModel

    def get_customer_by_id(self):
        try:
            customer = self.operations.findOne(
                self.customer_model,
                cliente_id=request.args.get('cliente_id'),
                empresa_id=request.company_id,
            )
            if customer:
                customer_data = ClienteBaseModel.from_orm(customer).dict()
                return {
                    'status': True,
                    'message': 'Cliente carregado com sucesso.',
                    'data': customer_data
                }, 200
            else:
                return {
                    'status': False,
                    'message': 'Cliente não encontrado.',
                    'data': None
                }, 404
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')
            return {
                'status': False,
                'message': str(exc),
                'data': None,
            }, 500

    def get_customer_all(self):
        try:
            search_term = request.args.get('termo_pesquisa') if request.args.get('termo_pesquisa') else None
            page = int(request.args.get('pagina')) if request.args.get('pagina') else 1
            limit = int(request.args.get('limite')) if request.args.get('limite') else 10
            if search_term:
                search_fields = ['nome', 'email', 'cpf', 'cnpj', 'cidade', 'uf']
                customers, total = self.operations.findManyByTerm(self.customer_model, page, limit, search_term,
                                                                 search_fields, empresa_id=request.company_id)
            else:
                customers, total = self.operations.findMany(self.customer_model, page, limit, empresa_id=request.company_id)
            customers_array = [ClienteBaseModel.from_orm(customer).dict() for customer in customers]

            return {
                'status': True,
                'message': 'Clientes carregados com sucesso.',
                'data': {
                    'result': customers_array,
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'total_pages': math.ceil(total / limit)
                }
            }, 200
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')
            return {
                'status': False,
                'message': str(exc),
                'data': None,
            }, 500

    def create_customer(self):
        try:
            user = self.functions.token_decript()
            data = request.json
            data['empresa_id'] = request.company_id
            data['responsavel_cadastro'] = user.get('login_id')
            # Convert nacionalidade to pais_id field name
            data['pais_id'] = data.pop('nacionalidade', None)
            result = self.operations.insert(self.customer_model, **data)
            return {
                'status': True,
                'message': 'Cliente criado com sucesso.',
                'data': {'cliente_id': result.cliente_id}
            }, 201
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')
            return {
                'status': False,
                'message': str(exc),
                'data': None,
            }, 500

    def update_customer(self):
        try:
            user = self.functions.token_decript()
            data = request.json
            data['empresa_id'] = request.company_id
            data['responsavel_cadastro'] = user.get('login_id')
            # Convert nacionalidade to pais_id field name
            if 'nacionalidade' in data:
                data['pais_id'] = data.pop('nacionalidade')
            
            update_data = {key: value for key, value in data.items() if key != 'cliente_id'}
            customer = self.operations.update_where(
                self.customer_model,
                {
                    'cliente_id': data['cliente_id'],
                    'empresa_id': request.company_id,
                },
                **update_data,
            )
            if customer is None:
                return {
                    'status': False,
                    'message': 'Cliente não encontrado.',
                    'data': None,
                }, 404
            return {
                'status': True,
                'message': 'Cliente alterado com sucesso.'
            }, 200
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')
            return {
                'status': False,
                'message': str(exc),
                'data': None,
            }, 500

    def virtual_delete_customer(self):
        try:
            excluir_cliente = self.operations.soft_delete(
                self.customer_model,
                request.args.get('cliente_id'),
                request.company_id,
            )
            if excluir_cliente:
                return {
                    'status': True,
                    'message': 'Cliente excluído com sucesso.'
                }, 200
            else:
                return {
                    'status': False,
                    'message': 'Cliente não encontrado.'
                }, 404
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')
            return {
                'status': False,
                'message': str(exc),
                'data': None,
            }, 500
