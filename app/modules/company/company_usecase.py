from datetime import datetime
from typing import Type

from flask import request, jsonify, make_response

from app.shared.helpers.functions import Functions
from app.shared.helpers.model_operations import ModelOperations
from app.shared.singletons.logger import Logger
from models import LoginModel, PermissaoModel, LoginPermissaoModel, EmpresaModel, LoginEmpresaModel


class CompanyUseCase:
    def __init__(self):
        self.logger = Logger()
        self.operations = ModelOperations()
        self.functions = Functions()
        self.login_model = LoginModel
        self.permission_model = PermissaoModel
        self.empresa_model = EmpresaModel
        self.login_empresa_model = LoginEmpresaModel

    def get_company(self):
        print('pegou a empresa')

    def get_company_by_user(self):
        try:
            user = self.functions.token_decript()
            companies = self.operations.findRelated(self.empresa_model, [self.login_empresa_model, self.login_model],
                                                    login_id=user.get('login_id'))
            if companies:
                companies_array = []
                for company in companies:
                    dict = self.functions.instance_to_object(company)
                    companies_array.append(dict)
                return make_response(
                    jsonify(
                        {
                            'status': True,
                            'message': 'Listagem de empresas carregada com sucesso.',
                            'data': {
                                'result': companies_array
                            }
                        }
                    ), 200
                )
            else:
                return make_response(
                    jsonify(
                        {
                            'status': False,
                            'message': 'Sem empresas para listar.',
                            'data': None
                        }
                    ), 404
                )
        except Exception as exc:
            return make_response(jsonify(
                {
                    'status': True,
                    'message': str(exc),
                    'data': None,
                }
            ), 500)

    def create_company(self):
        try:
            user = self.functions.token_decript()
            request.json['responsavel_cadastro_id'] = user.get('login_id')
            inserted_company = self.operations.insert(self.empresa_model, **request.json)
            self.operations.insert(self.login_empresa_model, login_id=user.get('login_id'), empresa_id=inserted_company.empresa_id)
            return make_response(jsonify(
                {
                    'status': True,
                    'message': 'Empresa criada com sucesso.'
                }
            ), 201)
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')

            return make_response(jsonify(
                {
                    'status': True,
                    'message': str(exc),
                    'data': None,
                }
            ), 500)