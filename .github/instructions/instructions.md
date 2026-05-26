
# 🧭 Backend Code Standards — api-minion-sys

O backend deste projeto segue uma arquitetura modular e desacoplada para garantir escalabilidade, manutenibilidade e facilidade de colaboração. Utiliza **Flask** e **Flask-RESTful** com SQLAlchemy. As orientações abaixo devem ser seguidas por todos os desenvolvedores.

## 📁 Estrutura Principal

```
api-minion-sys/
├── main.py                      # Entry point usando waitress (host: 0.0.0.0, porta dinâmica via APP_PORT)
├── app/
│   ├── __init__.py              # Flask app initialization, CORS, DB session management, response gzip compression
│   ├── routes/                  # Registro centralizado de rotas
│   │   └── api_routes.py        # Api.add_resource() pattern para Flask-RESTful
│   ├── modules/                 # Módulos organizados por domínio (17 módulos ativos)
│   │   └── <modulo>/
│   │       ├── <modulo>_resource.py
│   │       └── <modulo>_usecase.py
│   ├── shared/
│   │   ├── config/              # Configurações de banco de dados (PostgreSQL, MSSQL, Oracle)
│   │   ├── enums/               # Enumerações globais
│   │   ├── helpers/             # Utilitários e operações CRUD genéricas
│   │   ├── middlewares/         # Decoradores: auth, dto, user_company_validator
│   │   ├── singletons/          # Logger e outras instâncias únicas
│   │   └── swagger/             # Documentação Swagger
│   └── logs/                    # Logs organizados por ano/mês (YYYY/MM/)
├── models/                      # SQLAlchemy models (23 modelos)
├── alembic/                     # Migrations do banco de dados (Alembic)
├── requirements.txt             # Dependências (Flask, SQLAlchemy, Pydantic, etc)
├── .env                         # Variáveis de ambiente (DB_URL, APP_PORT, etc)
└── README.md
```

## 🔁 Padrão de Módulo

Cada módulo de negócio segue:

- `*_resource.py`: herda de `Resource` (Flask-RESTful) e expõe endpoints HTTP (GET, POST, PUT, DELETE).
- `*_usecase.py`: contém a lógica de negócio isolada.
- (Opcional) `*_model.py`: usado para schemas/DTOs locais com Pydantic.

Exemplo:
```python
# app/modules/product/product_resource.py
from flask_restful import Resource
from app.shared.middlewares.auth import auth_decorator
from .product_usecase import ProductUseCase

class ProductResource(Resource):
    @auth_decorator
    def get(self):
        return ProductUseCase().get_all()
    
    @auth_decorator
    def post(self):
        return ProductUseCase().create(request.json)
```

## 🌐 Registro de Rotas

Centralizado em `app/routes/api_routes.py` usando **Flask-RESTful**:
```python
from flask import Blueprint
from flask_restful import Api
from app.modules.product.product_resource import ProductResource

api_blueprint = Blueprint('api', __name__)
api = Api(api_blueprint)

# Rota com múltiplos endpoints
api.add_resource(ProductResource, '/produto', '/produto/<string:action>')
```

**Montagem em `app/__init__.py`:**
```python
app.register_blueprint(api_blueprint, url_prefix='/api/v1')
```

**URLs resultantes:** `https://host:port/api/v1/produto`

## 🧱 Models e Operações com o Banco

- **SQLAlchemy models** localizados em `models/`
- Usar `shared/helpers/model_operations.py` para operações CRUD reutilizáveis
- Modelos com Soft Delete herdam de `SoftDeleteQuery`
- Modelos com Pydantic schemas: seguir padrão `<entity>_model.py` com classes `<Entity>Model` (SQLAlchemy) e `<Entity>BaseModel` (Pydantic)

**Modelos sem módulo dedicado (apenas persistência):**
- `LeadModel` / `LeadFunilModel` - Funil de vendas
- `FaturaModel` / `FaturaItemModel` - Faturamento

## 🔐 Middlewares (Decoradores)

Localizados em `shared/middlewares/`:

- `@auth_decorator`: valida token JWT
- `@dto_decorator(PydanticModel)`: valida corpo da requisição contra schema Pydantic
- `@user_company_validator`: valida escopo de empresa do usuário

Uso em `*_resource.py`:
```python
from flask_restful import Resource, reqparse
from app.shared.middlewares.auth import auth_decorator
from app.shared.middlewares.dto import dto_decorator
from app.shared.middlewares.user_company_validator import user_company_validator

class ProductResource(Resource):
    @auth_decorator
    @user_company_validator
    @dto_decorator(ProductInputModel)
    def post(self):
        # request.json contém dados validados
        ...
```

## 🛠 Helpers e Utilitários

`shared/helpers/`:
- `db_pg_connection.py`: Conexão PostgreSQL específica
- `file_handler.py`: Gestão de arquivos
- `model_operations.py`: Operações CRUD genéricas
- `query_formatter.py`: Formatação de queries
- `singleton.py`: Padrão Singleton
- `token.py`: Gestão de JWT
- `validators.py`: Validadores customizados
- `functions.py`: Funções utilitárias diversas

`shared/singletons/`:
- `logger.py`: Logger centralizado com rotação automática por data (logs/YYYY/MM/)

## ⚙️ Configuração Flask

**app/__init__.py** configura:
- **CORS**: habilitado para todas as origens
- **Session Management**: scoped_session com SQLAlchemy
  - `pool_size=5`: conexões mantidas abertas
  - `max_overflow=12`: conexões extras permitidas
  - `pool_timeout=30`: timeout em segundos
  - `pool_recycle=1800`: recicla conexões a cada 30 minutos
- **Request/Teardown Hooks**: commit/rollback automático
- **GZIP Compression**: respostas JSON são comprimidas automaticamente
- **Logging**: todas as respostas são logadas

**Suporte a múltiplos bancos:**
- PostgreSQL (primário via DB_URL)
- MSSQL (config em `shared/config/db_mssql_config.py`)
- Oracle (config em `shared/config/db_oracle_config.py`)

## 🧪 Testes

- Exemplos em `modules/test/test_resource.py`
- Estrutura: modelos com CRUD completo usando padrão resource/usecase
- Para testes automatizados: usar pytest no futuro em `tests/`

## 📝 Boas Práticas

### Convenções
- Arquivos em `snake_case`, classes em `CamelCase`
- Módulos: `<entity>_resource.py`, `<entity>_usecase.py`
- Models: `<entity>_model.py` (inclui SQLAlchemy + Pydantic)

### Arquitetura
- ❌ Nunca misture lógica de negócio com rotas
- ✅ Toda lógica vai em `*_usecase.py`
- ✅ Recursos only gerenciam HTTP (Request/Response)

### Decoradores
- Aplicar sempre na ordem: `@auth_decorator` → `@user_company_validator` → `@dto_decorator`
- DTOs garantem type safety e validação automática

### Logging
- Usar `Logger()` do singleton centralizado
- Logs armazenados automaticamente por data: `logs/YYYY/MM/`
- Respostas HTTP logadas automaticamente (via `app/__init__.py`)

### Database
- Usar `ModelOperations` para CRUD padrão
- Criar novas operações em `shared/helpers/model_operations.py` se necessário
- Sempre validar constraints (unique, foreign keys)
- Testar com múltiplos bancos se suportarem diferentes

## 🚀 Módulos Implementados

| Módulo | Rotas | Status |
|--------|-------|--------|
| login | `/login` | ✅ Ativo |
| permission | `/permissao` | ✅ Ativo |
| user | `/usuarios` | ✅ Ativo |
| company | `/empresa` | ✅ Ativo |
| product | `/produto` | ✅ Ativo |
| product_category | `/produto-categoria` | ✅ Ativo |
| product_subcategory | `/produto-subcategoria` | ✅ Ativo |
| product_type | `/produto-tipo` | ✅ Ativo |
| service | `/servico` | ✅ Ativo |
| service_type | `/servico-tipo` | ✅ Ativo |
| stock | `/estoque` | ✅ Ativo |
| stock_type | `/estoque-tipo` | ✅ Ativo |
| budget | `/orcamento` | ✅ Ativo |
| sales | `/venda` | ✅ Ativo |
| sales_status | `/venda-status` | ✅ Ativo |
| customer | `/cliente` | ✅ Ativo |
| file_repository | `/arquivo` | ✅ Ativo |

## 📌 Stack Tecnológico

- **Framework**: Flask 3.1.0 + Flask-RESTful 0.3.10
- **ORM**: SQLAlchemy 2.0.31
- **Validação**: Pydantic 2.10.4
- **Autenticação**: PyJWT 2.9.0
- **Database Drivers**: psycopg2 (PostgreSQL), pyodbc (MSSQL/Oracle)
- **Server**: Waitress 3.0.0 (thread-based, thread_count=4)
- **Utilitários**: python-dotenv, pytz, Pillow

## 🔄 Fluxo de Criação de Novo Módulo

1. Criar pasta em `app/modules/<novo_modulo>/`
2. Criar model em `models/<novo_modulo>_model.py` (se necessário)
3. Criar `<novo_modulo>_resource.py` herdando de `Resource`
4. Criar `<novo_modulo>_usecase.py` com lógica de negócio
5. Importar e registrar em `app/routes/api_routes.py` via `Api.add_resource()`
6. Criar migration se necessário: `alembic revision --autogenerate -m "message"`
7. Aplicar migration: `alembic upgrade head`

## 📊 Operações CRUD

Sempre que criar novo CRUD:
1. Verifique se operação genérica existe em `model_operations.py`
2. Se não, implemente nova função e documente
3. Não altere CRUD existentes sem confirmação
4. Considere relacionamentos e constraints (foreign keys, unique, soft delete)
