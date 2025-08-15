import math

from flask import request, jsonify, make_response

from app.shared.helpers.functions import Functions
from app.shared.helpers.model_operations import ModelOperations
from app.shared.singletons.logger import Logger
from app.modules.file_repository.file_repository_usecase import FileRepositoryUseCase
from models import ProdutoTipoModel, ProdutoTipoBaseModel


class ProductTypeUseCase:
    def __init__(self):
        self.logger = Logger()
        self.operations = ModelOperations()
        self.functions = Functions()
        self.product_type_model = ProdutoTipoModel

    def get_product_type_all(self):
        try:
            search_term = request.args.get('termo_pesquisa') if request.args.get('termo_pesquisa') else None
            page = int(request.args.get('pagina'))
            limit = int(request.args.get('limite'))
            if search_term:
                search_fields = ['titulo', 'descricao', 'sku', 'detalhes_opcionais']
                types, total = self.operations.findManyByTerm(self.product_type_model, page, limit, search_term,
                                                                 search_fields,
                                                                 empresa_id=request.args.get('empresa_id'))
            else:
                types, total = self.operations.findMany(self.product_type_model, page, limit)
            types_array = [ProdutoTipoBaseModel.from_orm(product_type).dict() for product_type in types]

            return make_response(jsonify(
                {
                    'status': True,
                    'message': 'Tipos de produtos carregadas com sucesso.',
                    'data': {
                        'result': types_array,
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

    def get_product_type_by_id(self):
        print('by id')

    def create_product_type(self):
        try:
            user = self.functions.token_decript()
            data = request.json.copy() if request.json else {}
            
            # Separar dados da imagem para processar após inserção
            image_data = None
            if 'imagem' in data and data['imagem'] is not None:
                image_data = data['imagem']
                
                # Verificar se tem a estrutura correta
                if isinstance(image_data, dict) and all(k in image_data for k in ['tipo', 'arquivo']):
                    # Remover imagem dos dados de inserção (será processada depois)
                    data['imagem'] = None
                elif isinstance(image_data, str):
                    # Formato antigo (string) - manter compatibilidade
                    data['imagem'] = image_data
                    image_data = None  # Não processar upload
                else:
                    return make_response(jsonify({
                        'status': False,
                        'message': 'Campo imagem deve ter a estrutura: {tipo: str, arquivo: str}',
                        'data': None
                    }), 400)
            
            data['responsavel_cadastro_id'] = user.get('login_id')
            
            # Inserir tipo de produto
            result = self.operations.insert(self.product_type_model, **data)
            
            # Processar upload da imagem após inserção (usando o ID do tipo)
            if image_data and isinstance(image_data, dict):
                file_repo = FileRepositoryUseCase()
                
                # Determinar extensão baseada no tipo MIME
                extension = 'png'  # padrão
                if 'jpeg' in image_data['tipo'].lower():
                    extension = 'jpg'
                elif 'png' in image_data['tipo'].lower():
                    extension = 'png'
                elif 'webp' in image_data['tipo'].lower():
                    extension = 'webp'
                
                # Criar nome do arquivo: {id}.{extensão}
                file_name = f"{result.produto_tipo_id}.{extension}"
                
                # Chamar upload_image_str diretamente
                upload_result = file_repo.upload_image_str(
                    tipo='tipo_produto',  # Tipo específico para tipos de produto
                    arquivo=image_data['arquivo'],
                    nome_arquivo=file_name,
                    empresa_id=str(data.get('empresa_id', '')),
                )
                
                # Verificar se o upload foi bem-sucedido
                if upload_result.get('status'):
                    # Atualizar o tipo com o caminho da imagem
                    self.operations.update(self.product_type_model, result.produto_tipo_id, imagem=upload_result.get('file_path', ''))
                else:
                    # Log do erro, mas não falha a criação do tipo
                    self.logger.log(message=f"Erro no upload da imagem: {upload_result.get('message', 'Erro desconhecido')}", level='warning')
            
            return make_response(jsonify({
                'status': True,
                'message': 'Tipo de produto criado com sucesso.'
            }), 201)
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')
            return make_response(jsonify({
                'status': False,
                'message': str(exc),
            }), 500)

    def update_product_type(self):
        try:
            user = self.functions.token_decript()
            data = request.json.copy() if request.json else {}
            
            # Separar dados da imagem para processar após atualização
            image_data = None
            if 'imagem' in data and data['imagem'] is not None:
                image_data = data['imagem']
                
                # Verificar se tem a estrutura correta
                if isinstance(image_data, dict) and all(k in image_data for k in ['tipo', 'arquivo']):
                    # Remover imagem dos dados de atualização (será processada depois)
                    data['imagem'] = None
                elif isinstance(image_data, str):
                    # Formato antigo (string) - manter compatibilidade
                    data['imagem'] = image_data
                    image_data = None  # Não processar upload
                else:
                    return make_response(jsonify({
                        'status': False,
                        'message': 'Campo imagem deve ter a estrutura: {tipo: str, arquivo: str}',
                        'data': None
                    }), 400)
            
            data['responsavel_cadastro_id'] = user.get('login_id')
            
            # Remover o ID dos dados de atualização para evitar duplicação
            type_data = {key: value for key, value in data.items() if key != 'produto_tipo_id'}
            
            # Atualizar tipo de produto
            update_type = self.operations.update(self.product_type_model, data['produto_tipo_id'], **type_data)
            
            # Processar upload da imagem após atualização (usando o ID do tipo)
            if image_data and isinstance(image_data, dict):
                file_repo = FileRepositoryUseCase()
                
                # Determinar extensão baseada no tipo MIME
                extension = 'png'  # padrão
                if 'jpeg' in image_data['tipo'].lower():
                    extension = 'jpg'
                elif 'png' in image_data['tipo'].lower():
                    extension = 'png'
                elif 'webp' in image_data['tipo'].lower():
                    extension = 'webp'
                
                # Criar nome do arquivo: {id}.{extensão}
                file_name = f"{data['produto_tipo_id']}.{extension}"
                
                # Chamar upload_image_str diretamente
                upload_result = file_repo.upload_image_str(
                    tipo='tipo_produto',  # Tipo específico para tipos de produto
                    arquivo=image_data['arquivo'],
                    nome_arquivo=file_name,
                    empresa_id=str(data.get('empresa_id', '')),
                )
                
                # Verificar se o upload foi bem-sucedido
                if upload_result.get('status'):
                    # Atualizar o tipo com o caminho da imagem
                    update_type = self.operations.update(self.product_type_model, data['produto_tipo_id'], imagem=upload_result.get('file_path', ''))
                else:
                    # Log do erro, mas não falha a atualização do tipo
                    self.logger.log(message=f"Erro no upload da imagem: {upload_result.get('message', 'Erro desconhecido')}", level='warning')
            
            update_dict = ProdutoTipoBaseModel.from_orm(update_type).dict() if update_type else None
            if update_type:
                return (
                    {
                        'status': True,
                        'message': 'Tipos de produto alterado com sucesso.',
                        'data': {
                            'result': update_dict
                        }
                    }
                ), 201
            else:
                return (
                    {
                        'status': True,
                        'message': 'Nenhum tipo de produto alterada.'
                    }
                ), 204
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')

            return (
                {
                    'status': False,
                    'message': str(exc),
                    'data': None,
                }
            ), 500

    def virtual_delete_product_type(self):
        try:
            delete_type = self.operations.soft_delete(self.product_type_model, request.args.get('produto_tipo_id'), request.args.get('empresa_id'))
            if delete_type:
                return make_response(jsonify(
                    {
                        'status': True,
                        'message': 'Tipo de produto excluído com sucesso.'
                    }
                ), 201)
            else:
                self.logger.log(message=f"Falha ao excluir tipo de produto.", level='error')

                return make_response(jsonify(
                    {
                        'status': False,
                        'message': 'Falha ao excluir tipo de produto.',
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
