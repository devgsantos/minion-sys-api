# Módulo de Estoque

Este módulo gerencia o estoque de produtos no sistema, permitindo controlar a quantidade disponível de cada produto por tipo de estoque.

## Endpoints

### GET /estoque/todos
Lista todos os registros de estoque com paginação.

**Parâmetros:**
- `pagina` - Número da página (padrão: 1)
- `limite` - Número de itens por página (padrão: 10)
- `termo_pesquisa` - Termo para busca (opcional)

**Resposta:**
```json
{
  "status": true,
  "message": "Estoque carregado com sucesso.",
  "data": {
    "result": [
      {
        "estoque_id": 1,
        "produto_id": 1,
        "estoque_tipo_id": 1,
        "quantidade_disponivel": 100,
        "data_cadastro": "2023-08-10T14:30:00",
        "data_atualizacao": "2023-08-10T14:30:00",
        "tipo_estoque": {
          "estoque_tipo_id": 1,
          "nome": "Principal",
          "descricao": "Estoque principal da empresa"
        }
      }
    ],
    "page": 1,
    "limit": 10,
    "total": 1,
    "total_pages": 1
  }
}
```

### GET /estoque/por_id
Busca um registro de estoque específico pelo ID.

**Parâmetros:**
- `estoque_id` - ID do registro de estoque

**Resposta:**
```json
{
  "status": true,
  "message": "Registro de estoque encontrado com sucesso.",
  "data": {
    "estoque_id": 1,
    "produto_id": 1,
    "estoque_tipo_id": 1,
    "quantidade_disponivel": 100,
    "data_cadastro": "2023-08-10T14:30:00",
    "data_atualizacao": "2023-08-10T14:30:00",
    "tipo_estoque": {
      "estoque_tipo_id": 1,
      "nome": "Principal",
      "descricao": "Estoque principal da empresa"
    }
  }
}
```

### GET /estoque/por_produto
Busca todos os registros de estoque associados a um produto específico.

**Parâmetros:**
- `produto_id` - ID do produto

**Resposta:**
```json
{
  "status": true,
  "message": "Estoque do produto carregado com sucesso.",
  "data": [
    {
      "estoque_id": 1,
      "produto_id": 1,
      "estoque_tipo_id": 1,
      "quantidade_disponivel": 100,
      "data_cadastro": "2023-08-10T14:30:00",
      "data_atualizacao": "2023-08-10T14:30:00",
      "tipo_estoque": {
        "estoque_tipo_id": 1,
        "nome": "Principal",
        "descricao": "Estoque principal da empresa"
      }
    }
  ]
}
```

### POST /estoque
Cria um novo registro de estoque ou atualiza um existente se já houver um para o mesmo produto e tipo de estoque.

**Corpo da requisição:**
```json
{
  "produto_id": 1,
  "estoque_tipo_id": 1,
  "quantidade_disponivel": 100
}
```

**Resposta:**
```json
{
  "status": true,
  "message": "Registro de estoque criado com sucesso.",
  "data": {
    "estoque_id": 1,
    "quantidade_disponivel": 100
  }
}
```

### PUT /estoque
Atualiza um registro de estoque existente.

**Corpo da requisição:**
```json
{
  "estoque_id": 1,
  "quantidade_disponivel": 150
}
```

**Resposta:**
```json
{
  "status": true,
  "message": "Estoque atualizado com sucesso."
}
```

### DELETE /estoque
Remove (soft delete) um registro de estoque.

**Parâmetros:**
- `estoque_id` - ID do registro de estoque a ser removido

**Resposta:**
```json
{
  "status": true,
  "message": "Registro de estoque excluído com sucesso."
}
```
