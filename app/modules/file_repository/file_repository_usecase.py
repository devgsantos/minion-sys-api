import jwt
import os

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
        while os.path.exists(os.path.join(directory, f"{counter}.png")):
            counter += 1
        return f"{counter}.png"


    def product_image(self):
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
                    file_name = self.get_available_filename(product_folder)
                    file_path = os.path.join(product_folder, file_name)
                    img = Image.open(file)
                    img.save(file_path, 'png')

                    try:
                        image_update = {'imagem': os.path.join(product_subfolder, file_name).replace('\\','/')}
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

            return make_response(jsonify({"status": True, "message": "Arquivo salvo com sucesso.", "file_path": file_path}), 200)

        except Exception as exc:
            self.logger.log(message=str(exc), level='error')
            return make_response(jsonify({"status": False, "message": f"Falha ao salvar arquivo: {str(exc)}"}), 500)
