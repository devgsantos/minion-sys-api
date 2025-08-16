import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

host=os.environ.get("DB_HOST"),
port=os.environ.get("DB_PORT"),
database=os.environ.get("DB_NAME"),
user=os.environ.get("DB_USER"),
password=os.environ.get("DB_PASSWORD")

# URL de conexão ao banco de dados PostgreSQL
DATABASE_URL = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"

# Criação do engine
engine = create_engine(DATABASE_URL)

# Criação da base declarativa
Base = declarative_base()

# Criação da sessão
SessionLocal = sessionmaker(autocommit=True, autoflush=False, bind=engine)