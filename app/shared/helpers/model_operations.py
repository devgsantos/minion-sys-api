from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from contextlib import contextmanager

# Classe que abstrai operações com modelos SQLAlchemy
class ModelOperations:
    def __init__(self, engine):
        self.engine = engine
        self.Session = sessionmaker(bind=engine)

    # Context manager para gerenciar a sessão do SQLAlchemy
    @contextmanager
    def session_scope(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    # Buscar todos os registros de um modelo
    def findAll(self, model):
        with self.session_scope() as session:
            return session.query(model).all()

    # Buscar um único registro baseado em uma condição
    def findOne(self, model, **kwargs):
        with self.session_scope() as session:
            try:
                return session.query(model).filter_by(**kwargs).one()
            except NoResultFound:
                return None

    # Buscar um registro pelo ID
    def findById(self, model, id):
        with self.session_scope() as session:
            return session.query(model).get(id)

    # Inserir um novo registro
    def insert(self, instance):
        with self.session_scope() as session:
            session.add(instance)

    # Atualizar um registro existente
    def update(self, instance):
        with self.session_scope() as session:
            session.merge(instance)

    # Deletar um registro
    def delete(self, instance):
        with self.session_scope() as session:
            session.delete(instance)
