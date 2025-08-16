import math
import requests

from flask import jsonify, request
from werkzeug.datastructures import FileStorage

from app.shared.helpers.functions import Functions
from app.shared.helpers.model_operations import ModelOperations
from app.shared.helpers.file_handler import FileHandler
from app.shared.singletons.logger import Logger
from app.modules.file_repository.file_repository_usecase import FileRepositoryUseCase
from models import ProdutoModel, ProdutoCategoriaModel, ProdutoSubcategoriaModel, ProdutoTipoModel, EstoqueModel
from models.produto_model import ProdutoBaseModel
from app.shared.helpers.find_new_products import FindNewProducts


class ProductUseCase:
    def __init__(self):
        self.logger = Logger()
        self.operations = ModelOperations()
        self.functions = Functions()
        self.product_model = ProdutoModel
        self.product_category_model = ProdutoCategoriaModel
        self.product_subcategory_model = ProdutoSubcategoriaModel
        self.product_type_model = ProdutoTipoModel
        self.stock_model = EstoqueModel
        self.find_new_products = FindNewProducts()


    # USAR A SERIALIZAÇÃO DESTA FUNÇÃO COMO BASE PARA AS OUTRAS
    def get_all_product(self):
        try:
            search_term = request.args.get('termo_pesquisa') if request.args.get('termo_pesquisa') else None
            page = int(request.args.get('pagina')) if request.args.get('pagina') else 1
            limit = int(request.args.get('limite')) if request.args.get('limite') else 10
            if search_term:
                search_fields = ['titulo', 'descricao', 'sku', 'detalhes_opcionais']
                products, total = self.operations.findManyByTerm(self.product_model, page, limit, search_term, search_fields, empresa_id=request.args.get('empresa_id'))
            else:
                products, total = self.operations.findMany(self.product_model, page, limit, empresa_id=request.args.get('empresa_id'))
            products_array = [ProdutoBaseModel.from_orm(product).dict() for product in products]
            # products_array = self.functions.instance_list_to_array(products)

            return {
                'status': True,
                'message': 'Produtos carregados com sucesso.',
                'data': {
                    'result': products_array,
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'total_pages': math.ceil(total / limit)
                }
            }, 200
        except Exception as exc:
            return {
                'status': False,
                'message': str(exc),
                'data': None,
            }, 500


    def create_product(self):
        try:
            user = self.functions.token_decript()
            data = request.json.copy() if request.json else {}
            
            # Separar dados da imagem para processar após inserção
            image_data = None
            if 'imagem' in data and data['imagem'] is not None:
                image_data = data['imagem']
                
                # Verificar se tem a estrutura correta (agora sem nome_arquivo)
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
            
            # Definir responsável pelo cadastro
            data['responsavel_cadastro_id'] = user.get('login_id')
            product_insert = {key: value for key, value in data.items() if key != 'estoque'}
            
            # Inserir produto
            result = self.operations.insert(self.product_model, **product_insert)
            
            # Processar upload da imagem após inserção (usando o ID do produto)
            if image_data and isinstance(image_data, dict):
                file_repo = FileRepositoryUseCase()
                
                # Criar nome do arquivo baseado em SKU + ID
                file_name = f"{data.get('sku', 'produto')}_{result.produto_id}"
                
                # Chamar upload_image_str diretamente
                upload_result = file_repo.upload_image_str(
                    tipo='produto',  # Usar 'produto' como tipo fixo
                    arquivo=image_data['arquivo'],
                    nome_arquivo=file_name,
                    empresa_id=str(data.get('empresa_id', '')),
                    produto_id=result.produto_id  # Usar o ID do produto recém-criado
                )
                
                # Verificar se o upload foi bem-sucedido
                if upload_result.get('status'):
                    # Atualizar o produto com o caminho da imagem
                    self.operations.update(self.product_model, result.produto_id, imagem=upload_result.get('file_path', ''))
                else:
                    # Log do erro, mas não falha a criação do produto
                    self.logger.log(message=f"Erro no upload da imagem: {upload_result.get('message', 'Erro desconhecido')}", level='warning')
            
            # Processar estoque se fornecido
            if data.get('estoque') and len(data['estoque']) > 0:
                for param in data['estoque']:
                    insert_data = {
                        "produto_id": result.produto_id,
                        "estoque_tipo_id": param['estoque_tipo_id'],
                        "quantidade_disponivel": param['quantidade_disponivel']
                    }
                    self.operations.insert(self.stock_model, **insert_data)
            
            return {
                'status': True,
                'message': 'Produto criado com sucesso.'
            }, 201
            
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')
            return {
                'status': False,
                'message': str(exc),
                'data': None,
            }, 500

    def update_product(self):
        try:
            user = self.functions.token_decript()
            data = request.json.copy() if request.json else {}
            
            # Separar dados da imagem para processar após atualização
            image_data = None
            if 'imagem' in data and data['imagem'] is not None:
                image_data = data['imagem']
                
                # Verificar se tem a estrutura correta (agora sem nome_arquivo)
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
            product_update = {key: value for key, value in data.items() if key != 'estoque' and key != 'produto_id'}
            
            # Atualizar produto
            self.operations.update(self.product_model, data['produto_id'], **product_update)
            
            # Processar upload da imagem após atualização (usando o ID do produto)
            if image_data and isinstance(image_data, dict):
                file_repo = FileRepositoryUseCase()
                
                # Buscar o produto para obter o SKU
                produto = self.operations.findOne(self.product_model, produto_id=data['produto_id'])
                if not produto:
                    return {
                        'status': False,
                        'message': 'Produto não encontrado.',
                        'data': None
                    }, 404
                
                # Criar nome do arquivo baseado em SKU + ID
                file_name = f"{produto.sku}_{produto.produto_id}"
                
                # Chamar upload_image_str diretamente
                upload_result = file_repo.upload_image_str(
                    tipo='produto',  # Usar 'produto' como tipo fixo
                    arquivo=image_data['arquivo'],
                    nome_arquivo=file_name,
                    empresa_id=str(data.get('empresa_id', '')),
                    sku=data.get('sku', ''),  # Usar SKU do produto atualizado
                    produto_id=data['produto_id']  # Usar o ID do produto sendo atualizado
                )
                
                # Verificar se o upload foi bem-sucedido
                if upload_result.get('status'):
                    # Atualizar o produto com o caminho da imagem
                    self.operations.update(self.product_model, data['produto_id'], imagem=upload_result.get('file_path', ''))
                else:
                    # Log do erro, mas não falha a atualização do produto
                    self.logger.log(message=f"Erro no upload da imagem: {upload_result.get('message', 'Erro desconhecido')}", level='warning')
            
            if data.get('estoque') and len(data['estoque']) > 0:
                for param in data['estoque']:
                    unique_data = {
                        "produto_id": data['produto_id'],
                        "estoque_tipo_id": param['estoque_tipo_id']
                    }
                    data_to_update = {
                        "quantidade_disponivel": param['quantidade_disponivel']
                    }
                    self.operations.merge_insert_if_not_exists(self.stock_model, unique_fields=unique_data, **data_to_update)
            
            return {
                'status': True,
                'message': 'Produto alterado com sucesso.'
            }, 201
            
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')
            return {
                'status': False,
                'message': str(exc),
                'data': None,
            }, 500

    def virtual_delete_product(self):
        try:
            delete_product = self.operations.soft_delete(self.product_model, request.args.get('produto_id'), request.args.get('empresa_id'))
            if delete_product:
                return {
                    'status': True,
                    'message': 'Produto excluído com sucesso.'
                }, 201
            else:
                self.logger.log(message=f"Falha ao excluir produto.", level='error')

                return {
                    'status': False,
                    'message': 'Falha ao excluir produto.',
                }, 500
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')
            return {
                'status': False,
                'message': str(exc),
                'data': None,
            }, 500
        
    def search_by_ean_fallback(self):
        ean = request.args.get('ean')
        if not ean:
            return {
                "status": False,
                "message": "EAN não fornecido.",
                "result": None
            }, 400
        produto = self.find_new_products.find_new_products_product_search_net(ean)
        if not produto:
            return {
                "status": False,
                "message": "Produto não encontrado.",
                "result": None
            }, 404

        return {
            "status": True,
            "message": "Produto encontrado via fallback.",
            "result": produto
        }, 200

    def search_new_by_ean(self):
        try:
            url = f"https://world.openfoodfacts.org/api/v0/product/{request.args.get('ean') }.json"
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                return {
                    "status": False,
                    "message": "Erro ao acessar a API externa.",
                    "result": None
                }, 502

            data = response.json()
            product = data.get("product", {})
            if not product:
                return {
                    "status": False,
                    "message": "Produto não encontrado na base externa.",
                    "result": None
                }, 404

            return {
                "status": True,
                "message": "Produto encontrado.",
                "result": {
                    "titulo": product.get("product_name", "").strip(),
                    "descricao": product.get("ingredients_text", "").strip(),
                    "marca": product.get("brands", "").strip(),
                    "imagem": product.get("image_url", "").strip(),
                    "categorias": product.get("categories", "").strip()
                }
            }, 200

        except Exception as e:
            return {
                "status": False,
                "message": f"Erro inesperado: {str(e)}",
                "result": None
            }, 500