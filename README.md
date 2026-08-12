# MinionSys API

API do MinionSys para autenticacao e gestao multiempresa de produtos, estoque,
servicos, clientes, orcamentos e vendas.

## Stack

- Python 3, Flask 3.1 e Flask-RESTful
- Waitress
- SQLAlchemy 2 e PostgreSQL
- Pydantic 2
- Alembic
- JWT HS256

## Documentacao

- [Contexto tecnico da API](docs/API_CONTEXT.md)
- Documento mestre local:
  `/home/gilson/Documentos/Projetos/Angular/portal-minion-sys/docs/PROJECT_CONTEXT.md`

No GitHub, o documento mestre pertence ao repositorio
`devgsantos/minion-sys-ui`.

## Execucao

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

Testes que nao dependem de banco podem ser executados com:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

Os testes de transacao PostgreSQL usam um schema temporario e somente executam
quando uma base descartavel e fornecida explicitamente:

```bash
TEST_DATABASE_URL=postgresql+psycopg2://usuario:senha@localhost/minion_test \
  .venv/bin/python -m unittest tests.test_sales_transaction_postgres -v
```

Nunca use uma base de desenvolvimento compartilhada ou de producao nessa
variavel; a suite cria e remove seu proprio schema.

O Waitress usa `APP_PORT` e a conexao SQLAlchemy usa `DB_URL`. O catalogo de
variaveis e os passos ainda pendentes de bootstrap estao no contexto tecnico.
O Alembic tambem usa `DB_URL`; `alembic.ini` contem apenas um fallback local sem
credenciais.

## Linha de base em 2026-08-12

- `python3 -m compileall -q app models main.py alembic` passou;
- 29 testes unitarios e 3 testes PostgreSQL de commit, rollback e concorrencia
  passam no CI; localmente os 3 testes sao ignorados sem `TEST_DATABASE_URL`;
- o grafo Alembic possui um unico head (`b46052c344b0`) e nenhuma branch;
- banco real e integracao HTTP completa com o portal nao foram executados;
- conversao de orcamento em venda, aprovacao e baixa de estoque compartilham a
  transacao; concorrencia e rollback ainda precisam de teste em PostgreSQL.
