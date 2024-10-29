import jwt
import os

from PIL import Image
from flask import request, jsonify, make_response
from app.shared.singletons.logger import Logger


class FileRepositoryUseCase:
    def __init__(self):
        self.logger = Logger()

    def product_image(self):
        try:
            file_type = 'produtos'
            # Verificar se o arquivo foi enviado
            if 'file' not in request.files or 'company_id' not in request.form or 'type' not in request.form or 'file_name' not in request.form:
                return make_response(
                    jsonify(
                        {
                            'status': False,
                            'message': "Dados incompletos.",
                        }
                    ), 400
                )

            # Recuperar dados do form-data
            # file_name deve ser SKU + _ + PRODUTO_ID
            file = request.files['arquivo']
            company_id = request.form['empresa_id']
            file_name = request.form['nome_arquivo']

            if file.filename == '':
                return make_response(
                    jsonify(
                        {
                            'status': False,
                            'message': "Nenhum arquivo enviado.",
                        }
                    ), 400
                )

            # Definir a pasta raiz e criar a estrutura de diretórios com company_id e type
            if file.content_type.startswith('image'):
                folder = os.getenv('images_folder')
                company_folder = os.path.join(folder, company_id, file_type)
            else:
                folder = os.getenv('uploads')
                company_folder = os.path.join(folder, company_id)

            if not os.path.exists(company_folder):
                os.makedirs(company_folder)

            # Gerar o caminho completo do arquivo
            file_path = os.path.join(company_folder, file_name)

            # Se for uma imagem, converter para formato webp
            if file.content_type.startswith('image'):
                img = Image.open(file)
                webp_file_path = file_path.rsplit('.', 1)[0] + '.webp'  # Mudar a extensão para .webp
                img.save(webp_file_path, 'webp')
                file_path = webp_file_path

            else:
                # Salvar o arquivo diretamente se não for imagem
                file.save(file_path)

            # Responder com sucesso
            return jsonify({
                "status": True,
                "message": "Arquivo salvo com sucesso.",
                "file_path": file_path
            }), 200

        except Exception as e:
            return jsonify({
                "status": False,
                "message": f"Falha ao salvar arquivo: {str(e)}",
            }), 500