from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from dotenv import load_dotenv

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.shared.helpers.model_operations import ModelOperations
from models.base import Base

from models.produto_model import ProdutoModel
from models.produto_categorias_model import ProdutoCategoriaModel
from models.produto_tipos_model import ProdutoTipoModel
from models.produto_subcategorias_model import ProdutoSubcategoriaModel

from models.cliente_model import ClienteModel
from models.empresa_model import EmpresaModel
from models.empresa_categorias_model import EmpresaCategoriaModel
from models.usuario_model import UsuarioModel

from models.estoque_model import EstoqueModel
from models.orcamento_model import OrcamentoModel
from models.orcamento_item_model import OrcamentoItemModel

from models.lead_model import LeadModel
from models.pais_model import PaisModel
from models.profissao_model import ProfissaoModel

from models.login_model import LoginModel
from models.login_permissao_model import LoginPermissaoModel
from models.login_empresa import LoginEmpresaModel
from models.permissao_model import PermissaoModel
from models.venda_model import VendaModel

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
context.config.set_main_option('render_as_batch', 'True')


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
url = os.environ.get('DB_URL') or config.get_main_option('sqlalchemy.url')
config.set_main_option('sqlalchemy.url', url.replace('%', '%%'))
fileConfig(config.config_file_name)


# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata
# model_operations = ModelOperations(engine)

context.configure(
    url=url,
    target_metadata=target_metadata,
    compare_type=True,
    compare_server_default=True,
)

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
