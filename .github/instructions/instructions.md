
# 🧭 Backend Code Standards — api-minion-sys

O backend deste projeto segue uma arquitetura modular e desacoplada para garantir escalabilidade, manutenibilidade e facilidade de colaboração. As orientações abaixo devem ser seguidas por todos os desenvolvedores.

## 📁 Estrutura Principal

```
api-minion-sys/
├── main.py                      # Entry point usando waitress
├── app/
│   ├── routes/                  # Registro centralizado de rotas
│   │   └── api_routes.py
│   ├── modules/                 # Módulos organizados por domínio
│   │   └── <modulo>/
│   │       ├── <modulo>_resource.py
│   │       └── <modulo>_usecase.py
│   ├── shared/                  # Código reutilizável (helpers, middlewares, singletons)
│   └── logs/                    # Logs organizados por data
├── alembic/                    # Migrations do banco de dados
├── requirements.txt
└── README.md
```

## 🔁 Padrão de Módulo

Cada módulo de negócio segue:

- `*_resource.py`: expõe endpoints REST.
- `*_usecase.py`: contém a lógica de negócio isolada.
- (Opcional) `*_model.py`: usado para schemas locais.

Exemplo:
```python
# app/modules/product/product_resource.py
from .product_usecase import ProductUseCase

class ProductResource:
    def get(self):
        return ProductUseCase().get_all()
```

## 🌐 Registro de Rotas

Centralizado em `app/routes/api_routes.py`:
```python
def register_routes(app):
    from app.modules.product.product_resource import ProductResource
    app.add_url_rule('/product', view_func=ProductResource().get)
```

## 🧱 Models e Operações com o Banco

- Models SQLAlchemy/Pydantic devem ficar em `models/` ou no módulo específico.
- Usar `shared/helpers/model_operations.py` para operações CRUD reutilizáveis.

## 🔐 Middlewares

Localizados em `shared/middlewares/`:

- `auth.py`: autenticação via token
- `dto.py`: validação de corpo da requisição
- `user_company_validator.py`: validação de escopo

Uso típico:
```python
@auth_decorator
@user_company_validator
@dto_decorator(InputModel)
def post(self):
    ...
```

## 🛠 Helpers

- Operações utilitárias e banco genéricas: `shared/helpers/`
- Token management: `token.py`
- Query builder, singleton, funções diversas inclusas

## 🧪 Testes

- Exemplos em `modules/test/`
- Para testes reais, usar `tests/` com pytest no futuro.

## 📝 Boas Práticas

- Arquivos em `snake_case`, classes em `CamelCase`
- Nunca misture lógica de negócio com rotas
- Logs são armazenados automaticamente por data em `logs/YYYY/MM/DD/info.log`
- Use logger centralizado (`shared/singletons/logger.py`)

---

## Operações

Sempre que for necessário criar um novo CRUD, não altere os existentes sem confirmação e, ao criar novos, se necessário observe a relação das models e crie novas operações para no arquivo app/shared/helpers/model_operations.py caso nenhuma das funções cubram a nova funcionalidade.
