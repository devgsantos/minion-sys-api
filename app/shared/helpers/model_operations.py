import os
from datetime import datetime
from typing import Type, List, Optional, Any, Dict, Tuple

from flask import request
from sqlalchemy import func, or_
from sqlalchemy.orm import sessionmaker, scoped_session, joinedload
from sqlalchemy.orm.exc import NoResultFound
from contextlib import contextmanager

from unicodedata import normalize

from app.shared.singletons.logger import Logger
from models.base import Base


# Classe que abstrai operações com modelos SQLAlchemy
class ModelOperations:
    def __init__(self):
        self.Session = request.db_session
        self.logger = Logger()

    def normalize_term(self, term: str) -> str:
        """Remove acentos e retorna o termo normalizado."""
        return normalize('NFKD', term).encode('ASCII', 'ignore').decode('utf-8').lower()

    # Context manager para gerenciar a sessão do SQLAlchemy
    @contextmanager
    def session_scope(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        # finally:
        #     session.close()

    # Buscar todos os registros de um modelo
    def findAll(self, model: Type[Base]) -> List[Any]:
        with self.session_scope() as session:

            # Retorno o total de registros
            total_count = session.query(func.count(f'{getattr(model, "__tablename__", None)}_id')) \
                .filter(model.data_exclusao.is_(None)).scalar()

            # Consulta para obter os resultados paginados
            results = session.query(model).options(joinedload('*')).filter(model.data_exclusao.is_(None)).all()

            return results, total_count

    # Buscar um único registro baseado em uma condição
    def findOne(self, model: Type[Base], **kwargs) -> Optional[Any]:
        with self.session_scope() as session:
            try:
                # Criar a query e filtrar por data_exclusao is None e outros filtros fornecidos
                query = session.query(model).filter_by(**kwargs)
                query = query.filter(model.data_exclusao.is_(None))  # Soft delete

                # Obter o resultado único
                result = query.one()
                return result

            except NoResultFound:
                return None

    def findMany(self, model: Type[Base], page: int = 1, limit: int = 10, **kwargs) -> Tuple[Optional[List[Any]], int]:
        with self.session_scope() as session:
            offset = (page - 1) * limit

            try:
                # Contar o total de registros com base nos filtros aplicados
                query_count = session.query(func.count()).select_from(model)
                query_count = query_count.filter(model.data_exclusao.is_(None))

                for key, value in kwargs.items():
                    column = getattr(model, key, None)
                    if column is not None:
                        if isinstance(value, list):
                            query_count = query_count.filter(column.in_(value))
                        else:
                            query_count = query_count.filter(column == value)
                    else:
                        raise ValueError(f"Campo '{key}' não encontrado no modelo.")

                total_count = query_count.scalar()  # Total de registros com base nos filtros aplicados

                # Consulta para obter os resultados paginados
                query_results = session.query(model)
                query_results = query_results.filter(model.data_exclusao.is_(None))

                for key, value in kwargs.items():
                    column = getattr(model, key, None)
                    if column is not None:
                        if isinstance(value, list):
                            query_results = query_results.filter(column.in_(value))
                        else:
                            query_results = query_results.filter(column == value)

                results = query_results.offset(offset).limit(limit).all()
                return results, total_count
            except NoResultFound:
                return None, 0
            except Exception as e:
                print(f"Erro ao executar a consulta: {e}")
                raise

    def findManyNoffset(self, model: Type[Base], **kwargs) -> Tuple[Optional[List[Any]], int]:
        with self.session_scope() as session:  # Context manager para a sessão
            try:
                # Contar o total de registros com base nos filtros aplicados
                query_count = session.query(func.count()).select_from(model)
                query_count = query_count.filter(model.data_exclusao.is_(None))

                # Aplicar filtros dinâmicos nos campos do modelo
                for key, value in kwargs.items():
                    column = getattr(model, key, None)
                    if column is not None:
                        if isinstance(value, list):
                            query_count = query_count.filter(column.in_(value))
                        else:
                            query_count = query_count.filter(column == value)
                    else:
                        raise ValueError(f"Campo '{key}' não encontrado no modelo.")

                total_count = query_count.scalar()  # Total de registros filtrados

                # Consulta para obter todos os resultados sem paginação
                query_results = session.query(model).filter(model.data_exclusao.is_(None))

                for key, value in kwargs.items():
                    column = getattr(model, key, None)
                    if column is not None:
                        if isinstance(value, list):
                            query_results = query_results.filter(column.in_(value))
                        else:
                            query_results = query_results.filter(column == value)

                results = query_results.all()  # Obter todos os resultados
                return results, total_count

            except NoResultFound:
                return None, 0  # Se não encontrar resultados
            except Exception as e:
                print(f"Erro ao executar a consulta: {e}")
                raise  # Levantar a exceção para tratamento externo

    def findManyByTerm(
            self,
            model: Type[Base],
            page: int = 1,
            limit: int = 10,
            search_term: Optional[str] = None,
            search_fields: Optional[List[str]] = None,
            **kwargs
    ) -> Tuple[Optional[List[Any]], int]:
        with self.session_scope() as session:
            offset = (page - 1) * limit

            try:
                # Normaliza o termo de busca
                normalized_term = self.normalize_term(search_term) if search_term else None

                # Consulta para contar o total de registros
                query_count = session.query(func.count()).select_from(model)
                query_count = query_count.filter(model.data_exclusao.is_(None))

                # Filtros exatos com kwargs
                for key, value in kwargs.items():
                    column = getattr(model, key, None)
                    if column is not None:
                        if isinstance(value, list):
                            query_count = query_count.filter(column.in_(value))
                        else:
                            query_count = query_count.filter(column == value)
                    else:
                        raise ValueError(f"Campo '{key}' não encontrado no modelo.")

                # Adiciona filtros LIKE com normalização
                if normalized_term and search_fields:
                    like_filters = [
                        func.lower(func.unaccent(getattr(model, field))).ilike(f"%{normalized_term}%")
                        for field in search_fields if hasattr(model, field)
                    ]
                    if like_filters:
                        query_count = query_count.filter(or_(*like_filters))

                total_count = query_count.scalar()

                # Consulta para resultados paginados
                query_results = session.query(model)
                query_results = query_results.filter(model.data_exclusao.is_(None))

                # Aplicar novamente os filtros exatos
                for key, value in kwargs.items():
                    column = getattr(model, key, None)
                    if column is not None:
                        if isinstance(value, list):
                            query_results = query_results.filter(column.in_(value))
                        else:
                            query_results = query_results.filter(column == value)

                # Adiciona filtros LIKE para resultados
                if normalized_term and search_fields:
                    like_filters = [
                        func.lower(func.unaccent(getattr(model, field))).ilike(f"%{normalized_term}%")
                        for field in search_fields if hasattr(model, field)
                    ]
                    if like_filters:
                        query_results = query_results.filter(or_(*like_filters))

                results = query_results.offset(offset).limit(limit).all()
                return results, total_count
            except NoResultFound:
                return None, 0
            except Exception as e:
                print(f"Erro ao executar a consulta: {e}")
                raise

    # def findRelated(self, model: Type[Base], joins: List[Type[Base]], offset: int = 0, limit: int = 10, **kwargs) -> List[Any]:
    #     with self.session_scope() as session:
    #         query = session.query(model)
    #
    #         # Join with each model in the joins list
    #         for join_model in joins:
    #             # Make sure that joins are made on the right attributes
    #             join_attr = getattr(join_model, f'{getattr(model, "__tablename__", None)}_id', None)
    #             if join_attr:
    #                 query = query.join(join_model, getattr(model, f'{getattr(model, "__tablename__", None)}_id') == join_attr)
    #
    #                 # Apply filters dynamically
    #                 for attr, value in kwargs.items():
    #                     if hasattr(model, attr):
    #                         query = query.filter(getattr(model, attr) == value)
    #
    #                 query = query.offset(offset).limit(limit)
    #
    #                 # Execute the query and return results
    #                 try:
    #                     results = query.all()
    #                 except NoResultFound:
    #                     results = []
    #
    #                 return results

    def findRelated(self, model: Type[Base], joins: List[Type[Base]], page: int = 1, limit: int = 10, **kwargs) -> \
    Tuple[List[Any], int]:
        with self.session_scope() as session:
            query = session.query(model)
            offset = (page - 1) * limit

            # Join with each model in the joins list
            for join_model in joins:
                join_attr = getattr(join_model, f'{getattr(model, "__tablename__", None)}_id', None)
                if join_attr:
                    query = query.join(join_model,
                                       getattr(model, f'{getattr(model, "__tablename__", None)}_id') == join_attr)

            # Apply filters dynamically
            for attr, value in kwargs.items():
                if hasattr(model, attr):
                    query = query.filter(getattr(model, attr) == value)

            # Filter out records with non-null data_exclusao if the field exists
            if hasattr(model, 'data_exclusao'):
                query = query.filter(model.data_exclusao.is_(None))

            # Total count of records
            total_count = query.count()

            # Apply pagination
            query = query.offset(offset).limit(limit)

            # Execute the query and return results
            try:
                results = query.all()
            except NoResultFound:
                results = []

            return results, total_count

    # Buscar um registro pelo ID
    def findById(self, model: Type[Base], id: int) -> Optional[Any]:
        with self.session_scope() as session:
            return session.query(model).get(id)

    # Inserir um novo registro
    def insert(self, model: Type[Base], **kwargs) -> Any:
        with self.session_scope() as session:
            try:
                instances = []

                # Identificar listas em kwargs e garantir que todas tenham o mesmo tamanho
                list_keys = [k for k, v in kwargs.items() if isinstance(v, list)]
                if list_keys:
                    # Verifica se todas as listas têm o mesmo tamanho
                    list_length = len(kwargs[list_keys[0]])
                    if not all(len(kwargs[key]) == list_length for key in list_keys):
                        raise ValueError("Todas as listas devem ter o mesmo tamanho.")

                    # Criar uma instância para cada conjunto de valores na mesma posição nas listas
                    for i in range(list_length):
                        instance_data = {
                            k: (v[i] if isinstance(v, list) else v) for k, v in kwargs.items()
                        }
                        instances.append(model(**instance_data))

                    # Inserção em massa das instâncias
                    session.add_all(instances)
                    session.commit()  # Confirma a transação
                    return instances

                else:
                    # Inserção simples se não houver listas
                    instance = model(**kwargs)
                    session.add(instance)
                    session.commit()  # Confirma a transação
                    return instance

            except Exception as e:
                session.rollback()  # Reverter transação em caso de erro
                print(f"Erro ao inserir: {e}")
                raise

    # Atualizar um registro existente
    def update(self, model: Type[Base], instance_id: int, **kwargs) -> Optional[Any]:
        with self.session_scope() as session:
            instance = session.query(model).get(instance_id)
            if instance:
                for key, value in kwargs.items():
                    setattr(instance, key, value)

                session.commit()  # Commit inicial das alterações

                # Verifica se o modelo tem a coluna 'data_atualizacao'
                if hasattr(instance, 'data_atualizacao'):
                    setattr(instance, 'data_atualizacao', datetime.now())
                    session.commit()  # Commit após atualização da data_atualizacao

                return instance
            return None

    def merge(self, model: Type[Base], instance_id: Optional[int] = None, **kwargs) -> Optional[Any]:
        with self.session_scope() as session:
            # Tenta buscar a instância existente, se um 'instance_id' foi passado
            instance = session.query(model).get(instance_id) if instance_id else None

            if instance:
                # Atualiza a instância existente
                for key, value in kwargs.items():
                    setattr(instance, key, value)

                # Verifica se o modelo tem a coluna 'data_atualizacao'
                if hasattr(instance, 'data_atualizacao'):
                    setattr(instance, 'data_atualizacao', datetime.now())
            else:
                # Cria uma nova instância caso não exista
                instance = model(**kwargs)
                session.add(instance)

                # Verifica se o modelo tem a coluna 'data_cadastro'
                if hasattr(instance, 'data_cadastro'):
                    setattr(instance, 'data_cadastro', datetime.now())

            session.commit()  # Faz o commit das alterações
            return instance

    def merge_insert_if_not_exists(self, model: Type[Base], unique_fields: dict, **kwargs) -> Optional[Any]:
        """
        Função merge que verifica se uma combinação única de campos existe.
        Se existir, atualiza o registro. Se não existir, insere um novo registro.

        Parâmetros:
        - model: O modelo SQLAlchemy da tabela
        - unique_fields: Um dicionário contendo os campos únicos usados para identificar a instância
        - kwargs: Os campos a serem atualizados ou inseridos

        Retorno:
        - A instância atualizada ou criada
        """
        with self.session_scope() as session:
            # Verifica se já existe uma instância com base nos campos únicos
            instance = session.query(model).filter_by(**unique_fields).first()

            if instance:
                # Atualiza a instância existente com os novos valores
                if kwargs:
                    for key, value in kwargs.items():
                        setattr(instance, key, value)

                # Verifica se o modelo tem a coluna 'data_atualizacao' e atualiza
                if hasattr(instance, 'data_atualizacao'):
                    setattr(instance, 'data_atualizacao', datetime.now())
            else:
                # Cria uma nova instância caso não exista
                instance = model(**{**unique_fields, **kwargs})

                # Verifica se o modelo tem a coluna 'data_cadastro'
                if hasattr(instance, 'data_cadastro'):
                    setattr(instance, 'data_cadastro', datetime.now())

                session.add(instance)

            session.commit()  # Faz o commit após inserção ou atualização
            return instance

    # Deletar fisicamente um registro
    def delete(self, model: Type[Base], id: int) -> bool:
        with self.session_scope() as session:
            instance = session.query(model).get(id)
            if instance:
                session.delete(instance)
                return True
            return False

    # Deletar virtualmente um registro
    def soft_delete(self, model: Type[Base], instance_id: int, empresa_id: int) -> Optional[Any]:
        with self.session_scope() as session:
            # Identifica dinamicamente o nome da chave primária do modelo
            primary_key = list(model.__mapper__.primary_key)[0].key  # Obtém o nome da chave primária

            # Busca a instância usando filtros dinâmicos para instance_id e empresa_id
            instance = (
                session.query(model)
                .filter(getattr(model, primary_key) == instance_id, model.empresa_id == empresa_id)
                .first()
            )

            if instance:
                # Verifica se a instância possui 'data_exclusao' e atualiza
                if hasattr(instance, 'data_exclusao'):
                    setattr(instance, 'data_exclusao', datetime.utcnow())

                session.commit()  # Salva as mudanças
                return instance  # Retorna a instância alterada

            return None  # Retorna None se não encontrar a instância

    def model_to_dict(self, model_instance):
        return {c.name: getattr(model_instance, c.name) for c in model_instance.__table__.columns}

