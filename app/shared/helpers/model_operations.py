import os
from datetime import datetime
from typing import Type, List, Optional, Any

from flask import request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, joinedload
from sqlalchemy.orm.exc import NoResultFound
from contextlib import contextmanager

from app.shared.singletons.logger import Logger
from models.base import Base


# Classe que abstrai operações com modelos SQLAlchemy
class ModelOperations:
    def __init__(self):
        self.Session = request.db_session
        self.logger = Logger()


    # Context manager para gerenciar a sessão do SQLAlchemy
    @contextmanager
    def session_scope(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as exc:
            self.logger.log(message=str(f"ModelOperations -> {exc}"), level='error')
            session.rollback()
            raise
        # finally:
        #     session.close()

    # Buscar todos os registros de um modelo
    def findAll(self, model: Type[Base]) -> List[Any]:
        with self.session_scope() as session:
            return session.query(model).options(joinedload('*')).all()

    # Buscar um único registro baseado em uma condição
    def findOne(self, model: Type[Base], **kwargs) -> Optional[Any]:
        with self.session_scope() as session:
            try:
                results = session.query(model).filter_by(**kwargs).one()
                return results
            except NoResultFound:
                return None

    # Buscar um registro pelo ID
    def findById(self, model: Type[Base], id: int) -> Optional[Any]:
        with self.session_scope() as session:
            return session.query(model).get(id)

    # Inserir um novo registro
    def insert(self, model: Type[Base], **kwargs) -> Any:
        with self.session_scope() as session:
            if any(isinstance(value, list) for value in kwargs.values()):
                instances = []
                for key, value in kwargs.items():
                    if isinstance(value, list):
                        for item in value:
                            instance_kwargs = {k: v if k != key else item for k, v in kwargs.items() if not isinstance(v, list)}
                            instances.append(model(**item))
                session.add_all(instances)
                return instances
            else:
                instance = model(**kwargs)
                session.add(instance)
                return instance

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

    # Deletar um registro
    def delete(self, model: Type[Base], id: int) -> bool:
        with self.session_scope() as session:
            instance = session.query(model).get(id)
            if instance:
                session.delete(instance)
                return True
            return False

    def model_to_dict(self, model_instance):
        return {c.name: getattr(model_instance, c.name) for c in model_instance.__table__.columns}

