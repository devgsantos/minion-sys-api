from sqlalchemy import orm

from models.soft_delete import SoftDeleteQuery

Base = orm.declarative_base()

def get_query_class():
    return SoftDeleteQuery