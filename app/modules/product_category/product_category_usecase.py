import math

from flask import request, jsonify, make_response

from app.shared.helpers.functions import Functions
from app.shared.helpers.model_operations import ModelOperations
from app.shared.singletons.logger import Logger
from app.modules.file_repository.file_repository_usecase import FileRepositoryUseCase
from models import ProdutoCategoriaModel


class ProductCategoryUseCase:
    def __init__(self):
        self.logger = Logger()
        self.operations = ModelOperations()
        self.functions = Functions()
        self.product_category_model = ProdutoCategoriaModel

    #  ESTA TRATATIVA DE SERIALIZAÇÃO DEVE SER USADO EM MODELOS GENÉRICOS
    def get_product_category_all(self):
        try:
            search_term = request.args.get('termo_pesquisa') if request.args.get('termo_pesquisa') else None
            page = int(request.args.get('pagina'))
            limit = int(request.args.get('limite'))
            if search_term:
                search_fields = ['titulo', 'descricao', 'sku', 'detalhes_opcionais']
                categories, total = self.operations.findManyByTerm(self.product_category_model, page, limit, search_term,
                                                                 search_fields,
                                                                 empresa_id=request.company_id)
            else:
                categories, total = self.operations.findMany(
                    self.product_category_model, page, limit, empresa_id=request.company_id
                )
            categories_array = self.functions.instance_list_to_array(categories)

            return {
                'status': True,
                'message': 'Categorias carregadas com sucesso.',
                'data': {
                    'result': categories_array,
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

    def get_product_category_by_id(self):
        print('by id')

    def create_product_category(self):
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
            
            # Inserir categoria
            result = self.operations.insert(self.product_category_model, **data)
            
            # Processar upload da imagem após inserção (usando o ID da categoria)
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
                file_name = f"{result.produto_categoria_id}.{extension}"
                
                # Chamar upload_image_str diretamente
                upload_result = file_repo.upload_image_str(
                    tipo='categoria_produto',  # Tipo específico para categorias
                    arquivo=image_data['arquivo'],
                    nome_arquivo=file_name,
                    empresa_id=str(data.get('empresa_id', '')),
                )
                
                # Verificar se o upload foi bem-sucedido
                if upload_result.get('status'):
                    # Atualizar a categoria com o caminho da imagem
                    self.operations.update(self.product_category_model, result.produto_categoria_id, imagem=upload_result.get('file_path', ''))
                else:
                    # Log do erro, mas não falha a criação da categoria
                    self.logger.log(message=f"Erro no upload da imagem: {upload_result.get('message', 'Erro desconhecido')}", level='warning')
            
            return {
                'status': True,
                'message': 'Categoria de produtos criada com sucesso.'
            }, 201
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')
            return {
                'status': False,
                'message': str(exc),
                'data': None,
            }, 500

    def update_product_category(self):
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
            category_data = {key: value for key, value in data.items() if key != 'produto_categoria_id'}
            
            # Verificar se category_data é um dicionário válido
            if not isinstance(category_data, dict):
                category_data = {}
            
            # Atualizar categoria
            update_category = self.operations.update(self.product_category_model, data['produto_categoria_id'], **category_data)
            
            # Processar upload da imagem após atualização (usando o ID da categoria)
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
                file_name = f"{data['produto_categoria_id']}.{extension}"
                
                # Chamar upload_image_str diretamente
                upload_result = file_repo.upload_image_str(
                    tipo='categoria_produto',  # Tipo específico para categorias
                    arquivo=image_data['arquivo'],
                    nome_arquivo=file_name,
                    empresa_id=str(data.get('empresa_id', '')),
                )
                
                # Verificar se o upload foi bem-sucedido
                if upload_result.get('status'):
                    # Atualizar a categoria com o caminho da imagem
                    update_category = self.operations.update(self.product_category_model, data['produto_categoria_id'], imagem=upload_result.get('file_path', ''))
                else:
                    # Log do erro, mas não falha a atualização da categoria
                    self.logger.log(message=f"Erro no upload da imagem: {upload_result.get('message', 'Erro desconhecido')}", level='warning')
            
            if update_category:
                return {
                    'status': True,
                    'message': 'Categoria de produtos alterada com sucesso.'
                }, 201
            else:
                return {
                    'status': True,
                    'message': 'Nenhuma categoria de produtos alterada.'
                }, 204
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')
            return {
                'status': False,
                'message': str(exc),
                'data': None,
            }, 500

    def virtual_delete_product_category(self):
        try:
            delete_product_category = self.operations.soft_delete(self.product_category_model, request.args.get('produto_categoria_id'), request.company_id)
            if delete_product_category:
                return {
                    'status': True,
                    'message': 'Categoria de produtos excluída com sucesso.'
                }, 201
            else:
                self.logger.log(message=f"Falha ao excluir categoria de produtos.", level='error')

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
