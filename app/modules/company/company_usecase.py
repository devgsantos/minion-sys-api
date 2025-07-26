from datetime import datetime
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

    def get_company_all(self):
        try:
            page = int(request.args.get('page')) if request.args.get('page') else 1
            limit = int(request.args.get('limit')) if request.args.get('limit') else 10
            companies, total = self.operations.findMany(self.empresa_model, page, limit)

            if companies:
                companies_array = self.functions.instance_list_to_array(companies)
                return make_response(
                    jsonify(
                        {
                            'status': True,
                            'message': 'Todas as empresas carregadas com sucesso.',
                            'data': {
                                'result': companies_array,
                                'page': page,
                                'limit': limit,
                                'total': total
                            }
                        }
                    ), 200
                )
            else:
                return make_response(
                    jsonify(
                        {
                            'status': False,
                            'message': 'Nenhuma empresa encontrada.',
                            'data': None
                        }
                    ), 404
                )
        except Exception as exc:
            return make_response(
                jsonify(
                    {
                        'status': False,
                        'message': str(exc),
                        'data': None,
                    }
                ), 500
            )

    def get_company_by_user(self):
        try:
            page = int(request.args.get('page')) if request.args.get('page') else 1
            limit = int(request.args.get('limit')) if request.args.get('limit') else 10
            user = self.functions.token_decript()
            companies, total = self.operations.findRelated(
                self.empresa_model,
                [self.login_empresa_model, self.login_model],
                login_id=user.get('login_id')
            )

            if companies:
                companies_array = self.functions.instance_list_to_array(companies)
                return make_response(
                    jsonify(
                        {
                            'status': True,
                            'message': 'Listagem de empresas carregada com sucesso.',
                            'data': {
                                'result': companies_array,
                                'page': page,
                                'limit': limit,
                                'total': total
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
            return make_response(
                jsonify(
                    {
                        'status': False,
                        'message': str(exc),
                        'data': None,
                    }
                ), 500
            )

    def create_company(self):
        try:
            user = self.functions.token_decript()
            request.json['responsavel_cadastro_id'] = user.get('login_id')
            inserted_company = self.operations.insert(self.empresa_model, **request.json)
            self.operations.insert(self.login_empresa_model, login_id=user.get('login_id'), empresa_id=inserted_company.empresa_id)
            return make_response(
                jsonify(
                    {
                        'status': True,
                        'message': 'Empresa criada com sucesso.'
                    }
                ), 201
            )
        except Exception as exc:
            return make_response(
                jsonify(
                    {
                        'status': False,
                        'message': str(exc),
                        'data': None,
                    }
                ), 500
            )

    def update_company(self, empresa_id: int):
        try:
            user = self.functions.token_decript()
            request.json['responsavel_atualizacao_id'] = user.get('login_id')
            request.json['data_atualizacao'] = datetime.now()

            updated_company = self.operations.update(
                self.empresa_model,
                {'empresa_id': empresa_id},
                **request.json
            )

            if updated_company:
                return make_response(
                    jsonify(
                        {
                            'status': True,
                            'message': 'Empresa atualizada com sucesso.'
                        }
                    ), 200
                )
            else:
                return make_response(
                    jsonify(
                        {
                            'status': False,
                            'message': 'Empresa não encontrada.'
                        }
                    ), 404
                )
        except Exception as exc:
            return make_response(
                jsonify(
                    {
                        'status': False,
                        'message': str(exc),
                        'data': None,
                    }
                ), 500
            )

    def delete_company(self, empresa_id: int):
        try:
            deleted = self.operations.delete(self.empresa_model, empresa_id=empresa_id)

            if deleted:
                return make_response(
                    jsonify(
                        {
                            'status': True,
                            'message': 'Empresa excluída com sucesso.'
                        }
                    ), 200
                )
            else:
                return make_response(
                    jsonify(
                        {
                            'status': False,
                            'message': 'Empresa não encontrada.'
                        }
                    ), 404
                )
        except Exception as exc:
            return make_response(
                jsonify(
                    {
                        'status': False,
                        'message': str(exc),
                        'data': None,
                    }
                ), 500
            )

    def soft_delete_company(self, empresa_id: int):
        try:
            soft_deleted = self.operations.soft_delete(self.empresa_model, empresa_id=empresa_id)

            if soft_deleted:
                return make_response(
                    jsonify(
                        {
                            'status': True,
                            'message': 'Empresa excluída logicamente com sucesso.'
                        }
                    ), 200
                )
            else:
                return make_response(
                    jsonify(
                        {
                            'status': False,
                            'message': 'Empresa não encontrada.'
                        }
                    ), 404
                )
        except Exception as exc:
            return make_response(
                jsonify(
                    {
                        'status': False,
                        'message': str(exc),
                        'data': None,
                    }
                ), 500
            )
