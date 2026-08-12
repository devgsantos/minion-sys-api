import math

from flask import request, jsonify, make_response

from app.shared.helpers.functions import Functions
from app.shared.helpers.http import InvalidPaginationError, internal_error, parse_pagination
from app.shared.helpers.model_operations import ModelOperations
from app.shared.singletons.logger import Logger
from models import ServicoTipoModel, ServicoTipoBaseModel


class ServiceTypeUseCase:
    def __init__(self):
        self.logger = Logger()
        self.operations = ModelOperations()
        self.functions = Functions()
        self.service_type_model = ServicoTipoModel

    def get_service_type_all(self):
        try:
            search_term = request.args.get('termo_pesquisa') if request.args.get('termo_pesquisa') else None
            page, limit = parse_pagination(request.args)
            if search_term:
                search_fields = ['titulo', 'descricao']
                types, total = self.operations.findManyByTerm(self.service_type_model, page, limit, search_term,
                                                                 search_fields,
                                                                 empresa_id=request.company_id)
            else:
                types, total = self.operations.findMany(self.service_type_model, page, limit, empresa_id=request.company_id)
            types_array = [ServicoTipoBaseModel.from_orm(type).dict() for type in types]

            return {
                'status': True,
                'message': 'Tipos de serviços carregadas com sucesso.',
                'data': {
                    'result': types_array,
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'total_pages': math.ceil(total / limit)
                }
            }, 200
        except InvalidPaginationError as exc:
            return {'status': False, 'message': str(exc), 'data': None}, 400
        except Exception as exc:
            return internal_error(self.logger, exc)

    def get_service_type_by_id(self):
        try:
            service_type = self.operations.findOne(
                self.service_type_model,
                servico_tipo_id=request.args.get('servico_tipo_id'),
                empresa_id=request.company_id,
            )
            if service_type is None:
                return {'status': False, 'message': 'Tipo de serviço não encontrado.', 'data': None}, 404
            return {
                'status': True,
                'message': 'Tipo de serviço carregado com sucesso.',
                'data': ServicoTipoBaseModel.from_orm(service_type).dict(),
            }, 200
        except Exception as exc:
            return internal_error(self.logger, exc)

    def create_service_type(self):
        try:
            user = self.functions.token_decript()
            request.json['empresa_id'] = request.company_id
            request.json['responsavel_cadastro_id'] = user.get('login_id')
            self.operations.insert(self.service_type_model, **request.json)
            return {
                'status': True,
                'message': 'Tipo de serviço criado com sucesso.'
            }, 201
        except Exception as exc:
            return {
                'status': False,
                'message': str(exc),
                'data': None,
            }, 500

    def update_service_type(self):
        try:
            user = self.functions.token_decript()
            request.json['empresa_id'] = request.company_id
            request.json['responsavel_cadastro_id'] = user.get('login_id')
            update_type = self.operations.update(self.service_type_model, request.json['servico_tipo_id'], **request.json)
            if update_type:
                return {
                    'status': True,
                    'message': 'Tipos de serviço alterado com sucesso.'
                }, 201
            else:
                return {
                    'status': True,
                    'message': 'Nenhum tipo de serviço alterada.'
                }, 204
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')
            return {
                'status': False,
                'message': str(exc),
                'data': None,
            }, 500

    def virtual_delete_service_type(self):
        try:
            delete_type = self.operations.soft_delete(self.service_type_model, request.args.get('servico_tipo_id'), request.company_id)
            if delete_type:
                return {
                    'status': True,
                    'message': 'Tipo de serviço excluído com sucesso.'
                }, 201
            else:
                self.logger.log(message=f"Falha ao excluir tipo de produto.", level='error')
                return {
                    'status': False,
                    'message': 'Falha ao excluir tipo de produto.',
                }, 500
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')
            return {
                'status': False,
                'message': str(exc),
                'data': None,
            }, 500
