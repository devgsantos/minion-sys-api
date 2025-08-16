import jwt
import os
import base64
from io import BytesIO

from PIL import Image
from flask import request, jsonify, make_response

from app.shared.helpers.functions import Functions
from app.shared.helpers.model_operations import ModelOperations
from app.shared.singletons.logger import Logger
from models import ProdutoModel


class FileRepositoryUseCase:
    def __init__(self):
        self.logger = Logger()
        self.product_model = ProdutoModel
        self.functions = Functions()
        self.operations = ModelOperations()

    def get_available_filename(self, directory):
        # Esta função agora gera o nome do arquivo apenas com números sequenciais
        counter = 1
        if int(os.getenv('LIMITE_GLOBAL_IMAGENS_PRODUTO')) == 1:
            return f"{counter}.png"
        while os.path.exists(os.path.join(directory, f"{counter}.png")):
            counter += 1
        if counter > int(os.getenv('LIMITE_GLOBAL_IMAGENS_PRODUTO')):
            return False
        else:
            return f"{counter}.png"


    def upload_image(self):
        try:
            # Verificar se o arquivo foi enviado
            if 'arquivo' not in request.files or 'tipo' not in request.form:
                return make_response(
                    jsonify(
                        {
                            'status': False,
                            'message': "Dados incompletos.",
                        }
                    ), 400
                )

            # Recuperar dados do form-data
            file_type = request.form['tipo']
            file = request.files['arquivo']
            company_id = request.form['empresa_id']
            file_name = file.filename

            if file_name == '':
                return make_response(
                    jsonify(
                        {
                            'status': False,
                            'message': "Obrigatório nome do arquivo.",
                        }
                    ), 400
                )

            # Definir a pasta raiz e criar a estrutura de diretórios com company_id e type
            folder = os.getenv('images_folder') if file.content_type.startswith('image') else os.getenv('uploads')
            company_folder = os.path.join(folder, company_id, file_type)

            if not os.path.exists(company_folder):
                os.makedirs(company_folder)

            file_path = os.path.join(company_folder, file_name)

            if file.content_type.startswith('image'):
                if file_type == 'produto':
                    product_subfolder = file.filename.rsplit('.', 1)[0]
                    product_folder = os.path.join(company_folder, product_subfolder)
                    os.makedirs(product_folder, exist_ok=True)
                    file_order = self.get_available_filename(product_folder)
                    if file_order == False:
                        return make_response(jsonify(
                            {
                                "status": False,
                                "message": "Este produto já possui o limite de imagens cadastradas. Por favor apague ou substitua uma das imagens."
                            }
                        ), 304)
                    file_path = os.path.join(product_folder, file_order)
                    img = Image.open(file)
                    img.save(file_path, 'png')

                    try:
                        image_update = {'imagem': os.path.join(product_subfolder, file_order).replace('\\','/')}
                        self.operations.update(self.product_model, file_name.split('_')[1], **image_update)
                    except Exception as exc:
                        self.logger.log(message=str(exc), level='error')
                        return make_response(jsonify({'status': False, 'message': str(exc), 'data': None}), 500)
                else:
                    img = Image.open(file)
                    webp_file_path = file_path.rsplit('.', 1)[0] + '.png'
                    img.save(webp_file_path, 'png')
                    file_path = webp_file_path
            else:
                file.save(file_path)

            return make_response(jsonify({"status": True, "message": "Arquivo salvo com sucesso.", "file_path": os.path.join(product_subfolder, file_order)}), 200)

        except Exception as exc:
            self.logger.log(message=str(exc), level='error')
            return make_response(jsonify({"status": False, "message": f"Falha ao salvar arquivo: {str(exc)}"}), 500)

    def upload_image_str(self, tipo=None, arquivo=None, nome_arquivo=None, empresa_id=None, sku=None, produto_id=None):
        try:
            # Usar parâmetros diretos ou dados do request
            file_type = tipo or (request.json and request.json.get('tipo'))
            base64_file = arquivo or (request.json and request.json.get('arquivo'))
            file_name = nome_arquivo or (request.json and request.json.get('nome_arquivo'))
            company_id = empresa_id or request.args.get('empresa_id')

            # Verificar se os dados essenciais foram fornecidos
            if not file_type or not base64_file or not file_name:
                result = {
                    'status': False,
                    'message': "Dados incompletos. Campos obrigatórios: tipo, arquivo, nome_arquivo.",
                }
                # Retornar response HTTP se chamado via API (sem parâmetros diretos)
                if not tipo:
                    return make_response(jsonify(result), 400)
                return result

            if not company_id:
                result = {
                    'status': False,
                    'message': "Parâmetro 'empresa_id' é obrigatório.",
                }
                # Retornar response HTTP se chamado via API (sem parâmetros diretos)
                if not empresa_id:
                    return make_response(jsonify(result), 400)
                return result

            if not file_name or file_name.strip() == '':
                result = {
                    'status': False,
                    'message': "Nome do arquivo é obrigatório.",
                }
                # Retornar response HTTP se chamado via API (sem parâmetros diretos)
                if not nome_arquivo:
                    return make_response(jsonify(result), 400)
                return result

            # Processar base64 - remover prefixo se existir
            if base64_file.startswith('data:'):
                # Remove o prefixo data:image/xxx;base64,
                base64_file = base64_file.split(',', 1)[1]

            # Validar e limpar string base64
            try:
                # Remover espaços em branco e quebras de linha
                base64_file = base64_file.strip().replace(' ', '').replace('\n', '').replace('\r', '')
                
                # Verificar se contém apenas caracteres válidos de base64
                import re
                if not re.match(r'^[A-Za-z0-9+/]*={0,2}$', base64_file):
                    raise ValueError("String contém caracteres inválidos para base64")
                
                # Verificar se o comprimento é válido (múltiplo de 4 após padding)
                missing_padding = len(base64_file) % 4
                if missing_padding:
                    base64_file += '=' * (4 - missing_padding)
                
                # Decodificar base64
                file_data = base64.b64decode(base64_file)
                
                # Verificar se os dados decodificados não estão vazios
                if not file_data:
                    raise ValueError("Dados decodificados estão vazios")
                    
            except Exception as e:
                result = {
                    'status': False,
                    'message': f"Erro ao decodificar base64: {str(e)}",
                }
                # Retornar response HTTP se chamado via API (sem parâmetros diretos)
                if not arquivo:
                    return make_response(jsonify(result), 400)
                return result

            # Determinar se é imagem pelo conteúdo ou extensão
            is_image = (
                file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')) or 
                file_type == 'produto'
            )

            # Definir a pasta raiz
            folder = os.getenv('images_folder') if is_image else os.getenv('uploads')
            company_folder = os.path.join(folder, company_id, file_type)

            if not os.path.exists(company_folder):
                os.makedirs(company_folder)

            # Se produto_id foi fornecido, usar estrutura específica para produtos
            if produto_id and file_type == 'produto':
                product_folder_name = f"{sku}_{produto_id}"
                product_folder = os.path.join(company_folder, product_folder_name)
                os.makedirs(product_folder, exist_ok=True)
                
                # Obter nome de arquivo disponível
                file_order = self.get_available_filename(product_folder)
                if file_order == False:
                    result = {
                        "status": False,
                        "message": "Este produto já possui o limite de imagens cadastradas. Por favor apague ou substitua uma das imagens."
                    }
                    # Retornar response HTTP se chamado via API (sem parâmetros diretos)
                    if not arquivo:
                        return make_response(jsonify(result), 304)
                    return result
                
                file_path = os.path.join(product_folder, file_order)
                final_file_path = os.path.join(product_folder_name, file_order).replace('\\','/')
            else:
                # Para outros tipos (categoria_produto, subcategoria_produto, tipo_produto), usar estrutura simples
                file_path = os.path.join(company_folder, file_name)
                final_file_path = file_name

            if is_image:
                if file_type == 'produto':
                    # Processar imagem com PIL
                    try:
                        img = Image.open(BytesIO(file_data))
                        img.save(file_path, 'png')
                    except Exception as e:
                        result = {
                            'status': False,
                            'message': f"Erro ao processar imagem: {str(e)}",
                        }
                        # Retornar response HTTP se chamado via API (sem parâmetros diretos)
                        if not arquivo:
                            return make_response(jsonify(result), 400)
                        return result
                else:
                    # Para outras imagens, processar com PIL e salvar como PNG
                    try:
                        img = Image.open(BytesIO(file_data))
                        png_file_path = file_path.rsplit('.', 1)[0] + '.png'
                        img.save(png_file_path, 'png')
                        file_path = png_file_path
                        final_file_path = os.path.basename(png_file_path)
                    except Exception as e:
                        result = {
                            'status': False,
                            'message': f"Erro ao processar imagem: {str(e)}",
                        }
                        # Retornar response HTTP se chamado via API (sem parâmetros diretos)
                        if not arquivo:
                            return make_response(jsonify(result), 400)
                        return result
            else:
                # Para arquivos não-imagem, salvar diretamente
                with open(file_path, 'wb') as f:
                    f.write(file_data)

            result = {
                "status": True, 
                "message": "Arquivo salvo com sucesso.", 
                "file_path": final_file_path
            }
            
            # Retornar response HTTP se chamado via API (sem parâmetros diretos)
            if not arquivo:
                return make_response(jsonify(result), 200)
            return result

        except Exception as exc:
            self.logger.log(message=str(exc), level='error')
            result = {"status": False, "message": f"Falha ao salvar arquivo: {str(exc)}"}
            # Retornar response HTTP se chamado via API (sem parâmetros diretos)
            if not arquivo:
                return make_response(jsonify(result), 500)
            return result
