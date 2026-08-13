import math

from flask import request, jsonify, make_response

from app.shared.helpers.functions import Functions
from app.shared.helpers.model_operations import ModelOperations
from app.shared.singletons.logger import Logger
from app.modules.file_repository.file_repository_usecase import FileRepositoryUseCase
from models import ProdutoSubcategoriaModel
from models.produto_subcategorias_model import ProdutoSubcategoriaBaseModel


class ProductSubcategoryUseCase:
    def __init__(self):
        self.logger = Logger()
        self.operations = ModelOperations()
        self.functions = Functions()
        self.product_subcategory_model = ProdutoSubcategoriaModel

    def get_product_subcategory_all(self):
        try:
            search_term = request.args.get('termo_pesquisa') if request.args.get('termo_pesquisa') else None
            category_id = request.args.get('por_categoria') if request.args.get('por_categoria') else None
            page = int(request.args.get('pagina'))
            limit = int(request.args.get('limite'))
            if search_term:
                search_fields = ['titulo', 'descricao', 'sku', 'detalhes_opcionais']
                subcategories, total = self.operations.findManyByTerm(self.product_subcategory_model, page, limit, search_term,
                                                                 search_fields,
                                                                 empresa_id=request.company_id)
            elif category_id:
                search_fields = ['produto_categoria_id']
                subcategories, total = self.operations.findManyByTerm(self.product_subcategory_model, page, limit,
                                                                      category_id,
                                                                      search_fields,
                                                                      empresa_id=request.company_id)
            else:
                subcategories, total = self.operations.findMany(
                    self.product_subcategory_model, page, limit, empresa_id=request.company_id
                )
            subcategories_array = self.functions.instance_list_to_array(subcategories)

            return {
                'status': True,
                'message': 'Subcategorias carregadas com sucesso.',
                'data': {
                    'result': subcategories_array,
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'total_pages': math.ceil(total / limit)
                }
            }, 201
        except Exception as exc:
            return {
                'status': False,
                'message': str(exc),
                'data': None,
            }, 500

    def get_product_subcategory_by_category(self):
        try:
            category_id = request.args.get('categoria_id') if request.args.get('categoria_id') else None
            page = int(request.args.get('pagina'))
            limit = int(request.args.get('limite'))
            if category_id:
                search_fields = ['produto_categoria_id']
                subcategories, total = self.operations.findManyByFields(self.product_subcategory_model, page, limit,
                                                                      category_id,
                                                                      search_fields,
                                                                      empresa_id=request.company_id)
            else:
                return {
                    'status': False,
                    'message': 'Forneça o id da cartegoria desejada',
                    'data': None,
                }, 500

            # subcategories_array = self.functions.instance_list_to_array(subcategories)
            subcategories_array = [ProdutoSubcategoriaBaseModel.from_orm(subcategory).dict() for subcategory in subcategories]

            return {
                'status': True,
                'message': 'Subcategorias carregadas com sucesso.',
                'data': {
                    'result': subcategories_array,
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'total_pages': math.ceil(total / limit)
                }
            }, 201
        except Exception as exc:
            return {
                'status': False,
                'message': str(exc),
                'data': None,
            }, 500

    def get_product_subcategory_by_id(self):
        print('by id')

    def create_product_subcategory(self):
        try:
            user = self.functions.token_decript()
            data = request.json.copy() if request.json else {}
            data['empresa_id'] = request.company_id
            
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
                    return {
                        'status': False,
                        'message': 'Campo imagem deve ter a estrutura: {tipo: str, arquivo: str}',
                        'data': None
                    }, 400
            
            data['responsavel_cadastro_id'] = user.get('login_id')
            data['sigla'] = self.functions.gerar_sigla(data['titulo'])
            
            # Inserir subcategoria
            result = self.operations.insert(self.product_subcategory_model, **data)
            
            # Processar upload da imagem após inserção (usando o ID da subcategoria)
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
                file_name = f"{result.produto_subcategoria_id}.{extension}"
                
                # Chamar upload_image_str diretamente
                upload_result = file_repo.upload_image_str(
                    tipo='subcategoria_produto',  # Tipo específico para subcategorias
                    arquivo=image_data['arquivo'],
                    nome_arquivo=file_name,
                    empresa_id=str(data.get('empresa_id', '')),
                )
                
                # Verificar se o upload foi bem-sucedido
                if upload_result.get('status'):
                    # Atualizar a subcategoria com o caminho da imagem
                    self.operations.update(self.product_subcategory_model, result.produto_subcategoria_id, imagem=upload_result.get('file_path', ''))
                else:
                    # Log do erro, mas não falha a criação da subcategoria
                    self.logger.log(message=f"Erro no upload da imagem: {upload_result.get('message', 'Erro desconhecido')}", level='warning')
            
            return {
                'status': True,
                'message': 'Subcategoria de produtos criada com sucesso.'
            }, 201
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')
            return {
                'status': False,
                'message': str(exc),
                'data': None,
            }, 500

    def update_product_subcategory(self):
        try:
            user = self.functions.token_decript()
            data = request.json.copy() if request.json else {}
            data['empresa_id'] = request.company_id
            
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
                    return {
                        'status': False,
                        'message': 'Campo imagem deve ter a estrutura: {tipo: str, arquivo: str}',
                        'data': None
                    }, 400
            
            data['responsavel_cadastro_id'] = user.get('login_id')
            
            # Remover o ID dos dados de atualização para evitar duplicação
            subcategory_data = {key: value for key, value in data.items() if key != 'produto_subcategoria_id'}
            
            # Verificar se subcategory_data é um dicionário válido
            if not isinstance(subcategory_data, dict):
                subcategory_data = {}
            
            # Atualizar subcategoria
            update_subcategory = self.operations.update(self.product_subcategory_model, data['produto_subcategoria_id'], **subcategory_data)
            
            # Processar upload da imagem após atualização (usando o ID da subcategoria)
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
                file_name = f"{data['produto_subcategoria_id']}.{extension}"
                
                # Chamar upload_image_str diretamente
                upload_result = file_repo.upload_image_str(
                    tipo='subcategoria_produto',  # Tipo específico para subcategorias
                    arquivo=image_data['arquivo'],
                    nome_arquivo=file_name,
                    empresa_id=str(data.get('empresa_id', '')),
                )
                
                # Verificar se o upload foi bem-sucedido
                if upload_result.get('status'):
                    # Atualizar a subcategoria com o caminho da imagem
                    update_subcategory = self.operations.update(self.product_subcategory_model, data['produto_subcategoria_id'], imagem=upload_result.get('file_path', ''))
                else:
                    # Log do erro, mas não falha a atualização da subcategoria
                    self.logger.log(message=f"Erro no upload da imagem: {upload_result.get('message', 'Erro desconhecido')}", level='warning')
            
            if update_subcategory:
                return {
                    'status': True,
                    'message': 'Subcategoria de produtos alterada com sucesso.'
                }, 201
            else:
                return {
                    'status': True,
                    'message': 'Nenhuma subcategoria de produtos alterada.'
                }, 204
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')
            return {
                'status': False,
                'message': str(exc),
                'data': None,
            }, 500

    def virtual_delete_product_subcategory(self):
        try:
            delete_product_subcategory = self.operations.soft_delete(self.product_subcategory_model, request.args.get('produto_subcategoria_id'), request.company_id)
            if delete_product_subcategory:
                return {
                    'status': True,
                    'message': 'Subcategoria de produtos excluída com sucesso.'
                }, 201
            else:
                self.logger.log(message=f"Falha ao excluir subcategoria de produtos.", level='error')

                return {
                    'status': False,
                    'message': 'Falha ao excluir categoria de produtos.',
                }, 500
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')
            return {
                'status': False,
                'message': str(exc),
                'data': None,
            }, 500
