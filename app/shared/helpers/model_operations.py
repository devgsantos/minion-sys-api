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


class InsufficientStockError(Exception):
    def __init__(self, products: List[Dict[str, int]]):
        super().__init__('Estoque insuficiente para concluir a venda.')
        self.products = products


class SaleAlreadyExistsError(Exception):
    pass


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
    def findAll(self, model: Type[Base], order_by: str = 'data_criacao') -> List[Any]:
        with self.session_scope() as session:

            # Retorno o total de registros
            total_count = session.query(func.count(f'{getattr(model, "__tablename__", None)}_id')) \
                .filter(model.data_exclusao.is_(None)).scalar()

            # Consulta para obter os resultados ordenados
            query = session.query(model).options(joinedload('*')).filter(model.data_exclusao.is_(None))
            
            # Aplicar ordenação - padrão: mais recente primeiro
            if hasattr(model, order_by):
                order_column = getattr(model, order_by)
                query = query.order_by(order_column.desc())
            
            results = query.all()

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

    def findMany(self, model: Type[Base], page: int = 1, limit: int = 10, order_by: str = 'data_criacao', **kwargs) -> Tuple[Optional[List[Any]], int]:
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
                        elif isinstance(value, tuple) and value == ('is_not', None):
                            query_count = query_count.filter(column.is_not(None))
                        else:
                            query_count = query_count.filter(column == value)
                    else:
                        raise ValueError(f"Campo '{key}' não encontrado no modelo.")

                total_count = query_count.scalar()  # Total de registros com base nos filtros aplicados

                # Consulta para obter os resultados paginados e ordenados
                query_results = session.query(model)
                query_results = query_results.filter(model.data_exclusao.is_(None))

                for key, value in kwargs.items():
                    column = getattr(model, key, None)
                    if column is not None:
                        if isinstance(value, list):
                            query_results = query_results.filter(column.in_(value))
                        elif isinstance(value, tuple) and value == ('is_not', None):
                            query_results = query_results.filter(column.is_not(None))
                        else:
                            query_results = query_results.filter(column == value)

                # Aplicar ordenação - padrão: mais recente primeiro
                if hasattr(model, order_by):
                    order_column = getattr(model, order_by)
                    query_results = query_results.order_by(order_column.desc())

                results = query_results.offset(offset).limit(limit).all()
                return results, total_count
                return results, total_count
            except NoResultFound:
                return None, 0
            except Exception as e:
                print(f"Erro ao executar a consulta: {e}")
                raise

    def find_many_by_relation(
            self,
            model: Type[Base],
            related_model: Type[Base],
            join_condition,
            page: int = 1,
            limit: int = 10,
            order_by: str = 'data_cadastro',
            **related_filters
    ) -> Tuple[List[Any], int]:
        with self.session_scope() as session:
            offset = (page - 1) * limit
            query = session.query(model).join(related_model, join_condition)

            if hasattr(model, 'data_exclusao'):
                query = query.filter(model.data_exclusao.is_(None))
            if hasattr(related_model, 'data_exclusao'):
                query = query.filter(related_model.data_exclusao.is_(None))

            for key, value in related_filters.items():
                column = getattr(related_model, key, None)
                if column is None:
                    raise ValueError(f"Campo '{key}' não encontrado no modelo relacionado.")
                query = query.filter(column == value)

            total_count = query.count()
            if hasattr(model, order_by):
                query = query.order_by(getattr(model, order_by).desc())

            return query.offset(offset).limit(limit).all(), total_count

    def findManyNoffset(self, model: Type[Base], order_by: str = 'data_criacao', **kwargs) -> Tuple[Optional[List[Any]], int]:
        with self.session_scope() as session:
            try:
                # Aplica o filtro de soft delete (data_exclusao IS NULL) automaticamente
                query = session.query(model).filter(model.data_exclusao.is_(None))

                # Aplica filtros dinâmicos nos campos do modelo
                for key, value in kwargs.items():
                    column = getattr(model, key, None)
                    if column is not None:
                        if isinstance(value, list):
                            query = query.filter(column.in_(value))
                        else:
                            query = query.filter(column == value)
                    else:
                        raise ValueError(f"Campo '{key}' não encontrado no modelo.")

                # Aplicar ordenação - padrão: mais recente primeiro
                if hasattr(model, order_by):
                    order_column = getattr(model, order_by)
                    query = query.order_by(order_column.desc())

                # Executa a contagem total de registros com base nos filtros
                total_count = query.count()

                # Obter todos os resultados filtrados e ordenados
                results = query.all()

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
            order_by: str = 'data_criacao',
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

                # Consulta para resultados paginados e ordenados
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

                # Aplicar ordenação - padrão: mais recente primeiro
                if hasattr(model, order_by):
                    order_column = getattr(model, order_by)
                    query_results = query_results.order_by(order_column.desc())

                results = query_results.offset(offset).limit(limit).all()
                return results, total_count
                return results, total_count
            except NoResultFound:
                return None, 0
            except Exception as e:
                print(f"Erro ao executar a consulta: {e}")
                raise

    def findManyByFields(
            self,
            model: Type[Base],
            page: int = 1,
            limit: int = 10,
            search_term: Optional[str] = None,
            search_fields: Optional[List[str]] = None,
            order_by: str = 'data_criacao',
            **kwargs
    ) -> Tuple[Optional[List[Any]], int]:
        with self.session_scope() as session:
            offset = (page - 1) * limit

            try:
                # Normaliza o termo de busca se necessário
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

                # Adiciona filtros de igualdade para os campos de busca
                if normalized_term and search_fields:
                    equality_filters = []
                    for field in search_fields:
                        if hasattr(model, field):
                            attr = getattr(model, field)
                            # Aplica 'unaccent' apenas se o tipo do campo for textual
                            from sqlalchemy import String
                            if isinstance(attr.property.columns[0].type, String):
                                # Usando func.unaccent para garantir compatibilidade com acentos
                                equality_filters.append(
                                    func.lower(func.unaccent(attr)) == normalized_term
                                )
                            else:
                                equality_filters.append(attr == normalized_term)
                    if equality_filters:
                        query_count = query_count.filter(or_(*equality_filters))

                total_count = query_count.scalar()

                # Consulta para resultados paginados e ordenados
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

                # Aplicar filtros de igualdade nos resultados
                if normalized_term and search_fields:
                    equality_filters = []
                    for field in search_fields:
                        if hasattr(model, field):
                            attr = getattr(model, field)
                            # Aplicando unaccent somente em campos textuais
                            from sqlalchemy import String
                            if isinstance(attr.property.columns[0].type, String):
                                equality_filters.append(
                                    func.lower(func.unaccent(attr)) == normalized_term
                                )
                            else:
                                equality_filters.append(attr == normalized_term)
                    if equality_filters:
                        query_results = query_results.filter(or_(*equality_filters))

                # Aplicar ordenação - padrão: mais recente primeiro
                if hasattr(model, order_by):
                    order_column = getattr(model, order_by)
                    query_results = query_results.order_by(order_column.desc())

                results = query_results.offset(offset).limit(limit).all()
                return results, total_count
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
            query = session.query(model)
            primary_key = list(model.__mapper__.primary_key)[0]
            query = query.filter(primary_key == instance_id)
            if hasattr(model, 'data_exclusao'):
                query = query.filter(model.data_exclusao.is_(None))
            if hasattr(model, 'empresa_id') and 'empresa_id' in kwargs:
                query = query.filter(model.empresa_id == kwargs['empresa_id'])
            instance = query.one_or_none()
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

    def update_where(self, model: Type[Base], filters: Dict[str, Any], **kwargs) -> Optional[Any]:
        with self.session_scope() as session:
            query = session.query(model).filter_by(**filters)
            if hasattr(model, 'data_exclusao'):
                query = query.filter(model.data_exclusao.is_(None))

            instance = query.one_or_none()
            if instance is None:
                return None

            for key, value in kwargs.items():
                setattr(instance, key, value)

            if hasattr(instance, 'data_atualizacao'):
                instance.data_atualizacao = datetime.now()

            session.commit()
            return instance

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

    def merge_insert_if_not_exists(self, model: Type[Base], unique_fields: Optional[dict] = None, **kwargs) -> Optional[
        Any]:
        with self.session_scope() as session:
            try:
                # Verifica se unique_fields foi passado; se não, cria uma nova instância diretamente
                if not unique_fields:
                    instance = model(**kwargs)
                    session.add(instance)
                    session.commit()
                    return instance

                # Se unique_fields foi fornecido, tenta encontrar a instância existente
                query = session.query(model).filter_by(**unique_fields)
                if hasattr(model, 'data_exclusao'):
                    query = query.filter(model.data_exclusao.is_(None))  # Respeita soft delete

                instance = query.first()

                if instance:
                    # Atualiza a instância existente com os novos valores
                    for key, value in kwargs.items():
                        setattr(instance, key, value)

                    # Atualiza o campo 'data_atualizacao', se existir
                    if hasattr(instance, 'data_atualizacao'):
                        setattr(instance, 'data_atualizacao', datetime.utcnow())
                else:
                    # Cria uma nova instância se não encontrada
                    instance = model(**{**unique_fields, **kwargs})
                    session.add(instance)

                    # Define a 'data_cadastro', se existir
                    if hasattr(instance, 'data_cadastro'):
                        setattr(instance, 'data_cadastro', datetime.utcnow())

                session.commit()  # Salva as mudanças
                return instance

            except Exception as e:
                session.rollback()  # Reverte a transação em caso de erro
                print(f"Erro ao inserir ou atualizar registro: {e}")
                raise

    def merge_and_update_atomic(
            self,
            primary_model: Type[Base],
            primary_unique_fields: Dict[str, Any],
            primary_values: Dict[str, Any],
            related_model: Type[Base],
            related_filters: Dict[str, Any],
            related_values: Dict[str, Any],
    ) -> Optional[Any]:
        with self.session_scope() as session:
            try:
                primary_query = session.query(primary_model).filter_by(
                    **primary_unique_fields
                )
                if hasattr(primary_model, 'data_exclusao'):
                    primary_query = primary_query.filter(
                        primary_model.data_exclusao.is_(None)
                    )

                instance = primary_query.one_or_none()
                if instance is None:
                    instance = primary_model(
                        **{**primary_unique_fields, **primary_values}
                    )
                    session.add(instance)
                else:
                    for key, value in primary_values.items():
                        setattr(instance, key, value)

                session.flush()

                related_query = session.query(related_model).filter_by(
                    **related_filters
                )
                if hasattr(related_model, 'data_exclusao'):
                    related_query = related_query.filter(
                        related_model.data_exclusao.is_(None)
                    )
                related_instance = related_query.one_or_none()
                if related_instance is None:
                    raise ValueError('Registro relacionado não encontrado.')

                for key, value in related_values.items():
                    if value == '$primary_id':
                        value = getattr(
                            instance,
                            list(primary_model.__mapper__.primary_key)[0].key,
                        )
                    setattr(related_instance, key, value)

                session.commit()
                return instance
            except Exception:
                session.rollback()
                raise

    def create_sale_from_budget_atomic(
            self,
            sale_model: Type[Base],
            sale_unique_fields: Dict[str, Any],
            sale_values: Dict[str, Any],
            budget_model: Type[Base],
            budget_filters: Dict[str, Any],
            budget_values: Dict[str, Any],
            budget_item_model: Type[Base],
            stock_model: Type[Base],
            product_model: Type[Base],
            company_id: int,
            decrement_stock: bool = True,
    ) -> Any:
        with self.session_scope() as session:
            budget = session.query(budget_model).filter_by(
                **budget_filters
            ).with_for_update().one_or_none()
            if budget is None:
                raise ValueError('Orçamento não encontrado.')

            sale_query = session.query(sale_model).filter_by(
                **sale_unique_fields
            )
            if hasattr(sale_model, 'data_exclusao'):
                sale_query = sale_query.filter(sale_model.data_exclusao.is_(None))
            sale = sale_query.one_or_none()
            if sale is not None and decrement_stock:
                raise SaleAlreadyExistsError(
                    f'Já existe uma venda (ID: {sale.venda_id}) associada a este orçamento.'
                )

            requirements = dict(
                session.query(
                    budget_item_model.produto_id,
                    func.sum(budget_item_model.quantidade_orcamento),
                )
                .filter(
                    budget_item_model.orcamento_id == budget.orcamento_id,
                    budget_item_model.produto_id.is_not(None),
                    budget_item_model.data_exclusao.is_(None),
                )
                .group_by(budget_item_model.produto_id)
                .all()
            ) if decrement_stock else {}

            insufficient = []
            stock_rows = {}
            for product_id, required in requirements.items():
                rows = (
                    session.query(stock_model)
                    .join(
                        product_model,
                        stock_model.produto_id == product_model.produto_id,
                    )
                    .filter(
                        stock_model.produto_id == product_id,
                        stock_model.data_exclusao.is_(None),
                        product_model.empresa_id == company_id,
                        product_model.data_exclusao.is_(None),
                    )
                    .order_by(stock_model.estoque_id)
                    .with_for_update()
                    .all()
                )
                available = sum(row.quantidade_disponivel for row in rows)
                if available < required:
                    insufficient.append({
                        'produto_id': product_id,
                        'quantidade_necessaria': required,
                        'quantidade_disponivel': available,
                    })
                stock_rows[product_id] = rows

            if insufficient:
                raise InsufficientStockError(insufficient)

            for product_id, required in requirements.items():
                remaining = required
                for row in stock_rows[product_id]:
                    deducted = min(row.quantidade_disponivel, remaining)
                    row.quantidade_disponivel -= deducted
                    remaining -= deducted
                    if remaining == 0:
                        break

            if sale is None:
                sale = sale_model(**{**sale_unique_fields, **sale_values})
                session.add(sale)
            else:
                for key, value in sale_values.items():
                    setattr(sale, key, value)

            session.flush()
            sale_id = getattr(sale, list(sale_model.__mapper__.primary_key)[0].key)
            for key, value in budget_values.items():
                setattr(budget, key, sale_id if value == '$primary_id' else value)

            return sale

    # Deletar fisicamente um registro
    def delete(self, model: Type[Base], primary_key_value: Any) -> bool:
        with self.session_scope() as session:
            # Obtém o nome da chave primária dinamicamente
            primary_key_column = next(iter(model.__mapper__.primary_key)).name

            # Faz a consulta utilizando a chave primária
            instance = session.query(model).filter_by(**{primary_key_column: primary_key_value}).first()

            if instance:
                session.delete(instance)
                session.commit()  # Confirma a exclusão
                return True

            return False

    def soft_delete_relational(self, model: Type[Base], primary_key_value: Any) -> Optional[Base]:
        with self.session_scope() as session:
            try:
                # Obtém o nome da chave primária dinamicamente
                primary_key_column = next(iter(model.__mapper__.primary_key)).name

                # Faz a consulta utilizando a chave primária
                instance = session.query(model).filter_by(**{primary_key_column: primary_key_value}).first()

                if instance:
                    # Verifica se a instância possui 'data_exclusao' e atualiza
                    if hasattr(instance, 'data_exclusao'):
                        setattr(instance, 'data_exclusao', datetime.utcnow())

                    session.commit()  # Salva as mudanças
                    return instance  # Retorna a instância alterada

                return None  # Retorna None se a instância não for encontrada

            except Exception as e:
                session.rollback()  # Reverte a transação em caso de erro
                print(f"Erro ao realizar soft delete: {e}")
                raise

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

    def soft_delete_where(self, model: Type[Base], **filters) -> Optional[Any]:
        with self.session_scope() as session:
            query = session.query(model).filter_by(**filters)
            if hasattr(model, 'data_exclusao'):
                query = query.filter(model.data_exclusao.is_(None))

            instance = query.one_or_none()
            if instance is None:
                return None

            instance.data_exclusao = datetime.utcnow()
            session.commit()
            return instance

    def model_to_dict(self, model_instance):
        return {c.name: getattr(model_instance, c.name) for c in model_instance.__table__.columns}

