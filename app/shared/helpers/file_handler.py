import base64
import io
from typing import Union, Optional
from werkzeug.datastructures import FileStorage
from PIL import Image
import os


class FileHandler:
    """
    Classe para tratar uploads de arquivos e conversões de imagem
    """
    
    @staticmethod
    def process_image(image: Union[str, FileStorage], max_size: tuple = (800, 600)) -> Optional[str]:
        """
        Processa uma imagem, seja ela uma string base64 ou um arquivo upload.
        
        Args:
            image: String base64 ou objeto FileStorage
            max_size: Tupla (largura, altura) para redimensionar a imagem
            
        Returns:
            String base64 da imagem processada ou None se houver erro
        """
        try:
            if image is None:
                return None
                
            # Se já for uma string, assume que é base64 válida
            if isinstance(image, str):
                # Validar se é um base64 válido
                if image.startswith('data:image'):
                    return image
                else:
                    # Adicionar prefixo se necessário
                    return f"data:image/jpeg;base64,{image}"
            
            # Se for um arquivo FileStorage
            if isinstance(image, FileStorage):
                # Ler o conteúdo do arquivo
                image_data = image.read()
                
                # Resetar o ponteiro do arquivo para o início
                image.seek(0)
                
                # Abrir com PIL para processamento
                pil_image = Image.open(io.BytesIO(image_data))
                
                # Converter para RGB se necessário (para JPEG)
                if pil_image.mode in ('RGBA', 'LA', 'P'):
                    pil_image = pil_image.convert('RGB')
                
                # Redimensionar se necessário
                if max_size:
                    pil_image.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Converter para base64
                output_buffer = io.BytesIO()
                pil_image.save(output_buffer, format='JPEG', quality=85, optimize=True)
                
                # Converter para base64
                base64_string = base64.b64encode(output_buffer.getvalue()).decode('utf-8')
                
                # Retornar com prefixo data URI
                return f"data:image/jpeg;base64,{base64_string}"
                
            return None
            
        except Exception as e:
            print(f"Erro ao processar imagem: {str(e)}")
            return None
    
    @staticmethod
    def validate_image_file(file: FileStorage) -> bool:
        """
        Valida se o arquivo é uma imagem válida
        
        Args:
            file: Objeto FileStorage
            
        Returns:
            True se for uma imagem válida, False caso contrário
        """
        try:
            # Verificar mimetype
            allowed_mimetypes = [
                'image/jpeg', 'image/jpg', 'image/png', 
                'image/gif', 'image/webp', 'image/bmp'
            ]
            
            if file.mimetype not in allowed_mimetypes:
                return False
            
            # Verificar extensão
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
            filename = file.filename.lower() if file.filename else ''
            
            if not any(filename.endswith(ext) for ext in allowed_extensions):
                return False
            
            # Tentar abrir com PIL para validar se é realmente uma imagem
            file_data = file.read()
            file.seek(0)  # Reset file pointer
            
            Image.open(io.BytesIO(file_data))
            
            return True
            
        except Exception:
            return False
    
    @staticmethod
    def get_file_size_mb(file: FileStorage) -> float:
        """
        Retorna o tamanho do arquivo em MB
        
        Args:
            file: Objeto FileStorage
            
        Returns:
            Tamanho em MB
        """
        try:
            file.seek(0, os.SEEK_END)  # Ir para o final do arquivo
            size = file.tell()  # Obter posição (tamanho)
            file.seek(0)  # Voltar ao início
            
            return size / (1024 * 1024)  # Converter bytes para MB
            
        except Exception:
            return 0.0
