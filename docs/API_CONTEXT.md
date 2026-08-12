# Contexto Tecnico da MinionSys API

Atualizado em: 12 de agosto de 2026

## 1. Papel e arquitetura

A API concentra persistencia, autenticacao e regras do MinionSys. Atende o
portal Angular sob `/api/v1`.

```text
main.py                     entrada do Waitress
app/__init__.py             Flask, CORS, blueprint e SQLAlchemy
app/routes/api_routes.py    registro dos recursos
app/modules/<dominio>/      Resource e UseCase
app/shared/middlewares/     autenticacao, DTO e empresa
app/shared/helpers/         token, arquivos e operacoes de banco
models/                     SQLAlchemy e DTOs Pydantic
alembic/                    migrations
```

Fluxo predominante:

```text
HTTP -> Resource -> decorators -> UseCase -> ModelOperations -> SQLAlchemy
```

Os Resources escolhem operacoes por verbo e, frequentemente, pelo segmento
`<action>`. UseCases leem `request.args`, `request.json` ou `request.form`,
executam regras e montam o envelope HTTP.

## 2. Modulos registrados

- login, usuario, permissao e empresa;
- produto, categoria, subcategoria e tipo;
- servico e tipo de servico;
- estoque e tipo de estoque;
- cliente;
- orcamento;
- venda e status de venda;
- arquivo;
- teste.

## 3. Configuracao

| Variavel | Uso observado |
| --- | --- |
| `APP_PORT` | Porta do Waitress |
| `DB_URL` | URL SQLAlchemy principal |
| `JWT_SECRET` | JWT HS256 |
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | Helper PostgreSQL |
| `MSSQL_SERVER`, `MSSQL_DATABASE`, `MSSQL_USERNAME`, `MSSQL_PASSWORD` | MSSQL |
| `ORACLE_USERNAME`, `ORACLE_PASSWORD`, `ORACLE_DSN` | Oracle |
| `LIMITE_GLOBAL_IMAGENS_PRODUTO` | Limite de imagens |
| `images_folder` | Diretorio de imagens |
| `uploads` | Diretorio de arquivos |

O `.env` esta versionado e a regra correspondente no `.gitignore` esta
comentada. Deve-se auditar segredos, rotacionar credenciais publicadas e manter
somente `.env.example`. Remover do commit atual nao apaga o historico Git.

## 4. Inicializacao

`main.py` inicia Waitress em `0.0.0.0`, com quatro threads, timeout de 60
segundos, limite de 2000 conexoes e `expose_tracebacks=True`.

Pendencias:

- validar tipo e presenca de `APP_PORT`, `DB_URL` e `JWT_SECRET` no startup;
- desabilitar tracebacks em producao;
- restringir CORS aos origins oficiais;
- adicionar health e readiness checks;
- falhar cedo com mensagem segura quando configuracao estiver ausente.

## 5. Autenticacao

### 5.1 Login

`POST /login` valida email e senha com Pydantic. O use case consulta o banco por
ambos, gera JWT, atualiza `ultimo_login` e grava o token.

O login usa hash `scrypt` do Werkzeug. Registros legados em texto sao comparados
em tempo constante e substituidos por hash imediatamente apos um login valido.
Ainda faltam:

- rate limiting;
- politica de troca/recuperacao;
- proibicao de logs com credenciais.

### 5.2 JWT

Rotas protegidas usam `x-auth-token` e HS256. O token inclui login, permissoes,
empresas e expiracao.

O `auth_decorator` devolve HTTP 401 para token ausente ou invalido e disponibiliza
o payload validado em `request.auth_context` para os demais middlewares.

### 5.3 Empresa e autorizacao

`user_company_validator` procura `empresa_id` em query, form-data ou JSON e
confere se esta em `companies` do token.

Estado atual e pendencias:

- decorator nao cobre uniformemente todos os verbos;
- `request.json.get` pode ser usado mesmo sem corpo JSON;
- empresa nao autorizada retorna 403;
- a empresa validada fica em `request.company_id`;
- validar o request nao garante que a query SQL use `empresa_id`;
- permissoes do JWT nao sao aplicadas uniformemente por recurso/acao.

## 6. Matriz observada de decorators

| Recurso | GET | POST | PUT | DELETE |
| --- | --- | --- | --- | --- |
| Orcamento | auth + empresa | auth + empresa | auth + empresa | auth + empresa |
| Produto | auth + empresa | auth + empresa | auth + empresa | auth + empresa |
| Venda | auth + empresa | auth + empresa | auth + empresa | auth + empresa |
| Cliente | auth + empresa | auth + empresa | auth + empresa | auth + empresa |
| Servico | auth + empresa | auth + empresa | auth + empresa | auth + empresa |
| Estoque | auth + empresa | auth + empresa | auth + empresa | auth + empresa |
| Categoria produto | auth + empresa | auth + empresa | auth + empresa | auth + empresa |
| Subcategoria produto | auth + empresa | auth + empresa | auth + empresa | auth + empresa |
| Tipo produto | auth + empresa | auth + empresa | auth + empresa | auth + empresa |
| Tipo servico | auth + empresa | auth + empresa | auth + empresa | auth + empresa |
| Tipo estoque | auth | auth | auth + empresa | auth + empresa |
| Status venda | auth | N/A | N/A | N/A |
| Empresa | auth | auth + DTO | N/A | N/A |
| Usuario | N/A | auth + DTO | N/A | N/A |
| Permissao | N/A | auth + DTO | N/A | N/A |
| Arquivo | N/A | auth + empresa | N/A | N/A |
| Teste | publico | N/A | N/A | N/A |

Essa matriz registra somente decorators. Cada operacao ainda precisa de teste
que prove isolamento no banco.

Clientes, servicos, classificacoes, estoque, orcamentos e vendas ja receberam o novo contexto. O
estoque nao possui `empresa_id` proprio e e filtrado pelo relacionamento com
`ProdutoModel.empresa_id`. Tipos de estoque permanecem globais conforme o schema
atual.

## 7. Persistencia e transacoes

`ModelOperations` centraliza busca unica/paginada, busca por termo, insert,
update/upsert e soft delete.

Riscos:

- updates podem usar somente o ID primario;
- uma operacao generica pode omitir regras especificas de tenant;
- `except Exception` dificulta distinguir validacao, conflito e falha de banco;
- existem prints em vez de logging estruturado;
- criacao da venda, aprovacao do orcamento e baixa de estoque compartilham a
  transacao e bloqueiam orcamento/linhas de estoque durante a conversao;
- saldo insuficiente cancela a operacao com HTTP 409; o rollback e a disputa
  concorrente ainda precisam ser exercitados em PostgreSQL real;
- concorrencia pode permitir saldo inconsistente se nao houver lock ou update
  condicional adequado.

Regra necessaria para dados multiempresa:

1. A empresa deve pertencer ao contexto autenticado.
2. Toda query de recurso tenant-aware deve filtrar ID e empresa.
3. Updates/deletes devem verificar quantidade afetada.
4. Relacionamentos tambem devem pertencer a mesma empresa.

## 8. Contrato HTTP

Formato frequente:

```json
{
  "status": true,
  "message": "Mensagem",
  "data": { "result": [] }
}
```

Inconsistencias:

- erros alternam `data` e `result`;
- ha 201 em leitura, update ou soft delete;
- autenticacao pode responder HTTP 200 em erro;
- `str(exc)` pode expor SQL/detalhes internos;
- paginacao nao tem contrato formal;
- nao ha OpenAPI mantida como fonte verificavel.

Uma futura padronizacao deve ter erro estavel (`code`, `message`, `fields`) e
`request_id`, mantendo compatibilidade temporaria com o portal.

## 9. Migracoes

Existem revisions para produtos, categorias, clientes, orcamentos e vendas. O
ambiente `.venv` permitiu confirmar um unico head (`b46052c344b0`) e nenhuma
branch. Ainda falta confirmar em banco descartavel:

- upgrade de banco vazio ate head;
- correspondencia entre modelos e schema;
- estrategia de rollback.

Isso deve ser resolvido antes de migrations de seguranca ou senha.

## 10. Uploads

Ha upload por multipart/base64 e paths definidos por ambiente. A auditoria deve
cobrir:

- tamanho global e por arquivo;
- MIME detectado pelo conteudo, nao apenas pelo cliente;
- extensoes permitidas;
- normalizacao de nome/path traversal;
- autorizacao da empresa antes de ler/gravar;
- sobrescrita e colisao;
- limpeza em falha transacional;
- imagens malformadas e arquivos executaveis;
- exposicao publica do servidor de imagens.

## 11. Testes propostos

```text
tests/
  conftest.py
  unit/
    test_token.py
    test_validators.py
  integration/
    test_auth.py
    test_company_isolation.py
    test_customers.py
    test_products.py
    test_stock_budget_sales.py
```

Casos minimos:

- login valido/invalido;
- token ausente, adulterado e expirado;
- empresa autorizada e proibida;
- leitura, update e delete cruzados;
- validacao Pydantic e soft delete;
- paginacao e busca;
- conflito de SKU;
- upload invalido/limites;
- estoque insuficiente;
- atomicidade de orcamento para venda.

O banco de teste deve ser descartavel. Mock unitario nao substitui teste SQL de
isolamento e transacao.

## 12. Observabilidade e operacao

Necessario:

- logs JSON com request ID, rota, status, duracao, login e empresa;
- nunca registrar token, senha ou dados sensiveis;
- error handlers globais;
- `/health` para processo e `/ready` para dependencias;
- metricas de latencia e taxa de erro;
- runbook de migration, deploy e rollback;
- CI com compile, lint, testes e migration check.

## 13. Higiene do repositorio

Revisar sem remocao precipitada:

- `.env` versionado;
- `api-minion-sys.zip`;
- endpoint/modulo `test`;
- scripts e READMEs historicos;
- dependencias sem lock/hash reproduzivel.

Antes de remover, verificar se deploy atual depende desses arquivos.

## 14. Validacao realizada

```bash
python3 -m compileall -q app models main.py alembic
```

Resultado: sucesso. A suite unitaria possui 29 testes. Isso nao substitui banco
real, endpoints integrados ou validacao de concorrencia.

```bash
.venv/bin/alembic heads
.venv/bin/alembic branches
```

Resultado: um unico head (`b46052c344b0`) e nenhuma branch.

## 15. Sequencia recomendada

1. Criar ambiente e infraestrutura minima de testes.
2. Testar token ausente, invalido e expirado.
3. Testar dois usuarios/empresas com IDs conhecidos.
4. Corrigir status HTTP e criar contexto autenticado unico.
5. Corrigir CRUD de clientes como piloto tenant-aware.
6. Expandir para classificacoes, servicos, produtos e estoque.
7. Testar rollback e concorrencia da transacao orcamento/venda/estoque no banco.
8. Implementar hashing e migracao de senha.
9. Restringir CORS, uploads, tracebacks e endpoint de teste.
10. Consolidar CI, OpenAPI e observabilidade.

## 16. Gate por mudanca

Antes de concluir um pacote:

- confirmar branch e worktree;
- criar teste de regressao;
- verificar consumidores no portal;
- aplicar migrations quando necessario;
- rodar compile, lint, testes e `git diff --check`;
- testar banco/API reais quando o escopo exigir;
- atualizar esta documentacao se contrato ou arquitetura mudar.
