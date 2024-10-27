import hashlib
import os
from datetime import datetime
from flask_restx import Api, fields
from pydantic import BaseModel
from typing import Type

import jwt
from flask import request, jsonify
import json

from app.shared.helpers.model_operations import ModelOperations
from app.shared.helpers.token import Token
from app.shared.singletons.logger import Logger
from sqlalchemy.inspection import inspect
from models import UsuarioModel
from models.base import Base


class Functions:
    def __init__(self):
        self.jwt = jwt
        self.auth_key = os.getenv('JWT_SECRET')
        self.operations = ModelOperations()
        self.logger = Logger()
        self.user_model = UsuarioModel

    def password_encrypt(string):
        hash = hashlib.md5(string.encode('utf-8'))
        hash_hex = hash.hexdigest()
        return hash_hex

    def hide_phone(phone):
        if len(phone) == 11:
            hidden_phone = '*' * 7 + phone[7:]
            return hidden_phone
        elif len(phone) == 10:
            hidden_phone = '*' * 6 + phone[6:]
            return hidden_phone

    def token_decript(self):
        payload = self.jwt.decode(request.headers.get("x-auth-token"), self.auth_key, algorithms=['HS256'])
        return payload

    def check_user_login(self):
        try:
            payload = Token().decode_token(request.headers.get('x-auth-token'))
            user = self.operations.findOne(self.user_model, login_id=payload.get('login_id'))
            if user:
                return {
                    'status': True,
                    'data': user
                }
            else:
                return {
                    'status': True,
                    'data': None
                }
        except Exception as exc:
            self.logger.log(message=str(exc), level='error')
            return jsonify(
                {
                    'status': True,
                    'message': str(exc),
                }
            ), 500

    # def model_to_dict(self, model):
    #     return {
    #         c.key: getattr(model, c.key)
    #         for c in inspect(model).mapper.column_attrs
    #     }

    def instance_list_to_array(self, list):
        array = []
        for item in list:
            dict = self.instance_to_object(item)
            array.append(dict)
        return array

    def instance_to_object(self, instance):
        """Iterate over each attribute of a SQLAlchemy model instance and print its name and value."""
        if not isinstance(instance, Base):
            raise TypeError("model must be an instance of SQLAlchemy model")

        # Use SQLAlchemy's inspect to get the model's attributes
        obj = {}
        mapper = inspect(instance)
        for attr_name in mapper.unmodified:
            attr_value = getattr(instance, attr_name)
            if not isinstance(attr_value, Base):
                if isinstance(attr_value, datetime):
                    attr_value = attr_value.strftime('%Y-%m-%d %H:%M:%S')
                obj[attr_name] = attr_value
            else:
                obj[attr_name] = self.instance_to_object(attr_value)
        return obj

    def gerar_sigla(self, string: str) -> str:
        # Divide a string em palavras
        palavras = string.split()

        # Verifica se é uma única palavra
        if len(palavras) == 1:
            # Retorna as três primeiras letras em maiúsculo
            return palavras[0][:3].upper()
        else:
            # Itera sobre as palavras para encontrar a segunda palavra válida
            primeira = palavras[0][:2].upper()
            segunda = ""

            for palavra in palavras[1:]:
                if len(palavra) > 2:
                    segunda = palavra[0].upper()
                    break

            # Se não encontrou uma segunda palavra válida, use a próxima palavra disponível
            if not segunda and len(palavras) > 1:
                segunda = palavras[1][0].upper()

            return primeira + segunda


    def pydantic_to_flask_restx_model(self, model: Type[BaseModel], api) -> dict:
        """Converte um modelo Pydantic para um modelo Flask-RESTX."""
        model_fields = {}
        for name, field in model.__annotations__.items():
            # Mapeia tipos Pydantic para tipos Flask-RESTX
            if field == int:
                model_fields[name] = fields.Integer
            elif field == float:
                model_fields[name] = fields.Float
            elif field == str:
                model_fields[name] = fields.String
            elif field == bool:
                model_fields[name] = fields.Boolean
            elif field == list:
                model_fields[name] = fields.List(fields.Raw)  # Suporte básico para listas
            elif field == dict:
                model_fields[name] = fields.Raw  # Suporte básico para dicionários
            elif hasattr(field, '__origin__'):
                origin = getattr(field, '__origin__')
                if origin == list:
                    # Se for uma lista, usa o primeiro tipo genérico encontrado
                    item_type = field.__args__[0]
                    model_fields[name] = fields.List(self.pydantic_to_flask_restx_model(item_type, api))
                elif origin == dict:
                    # Se for um dicionário, define um formato genérico
                    model_fields[name] = fields.Raw
            else:
                model_fields[name] = fields.Raw  # Tipo não reconhecido, usa Raw
        return api.model(model.__name__, model_fields)

    def budget_value(self, itens):
        print('teste')