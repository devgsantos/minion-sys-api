# Sales Status Module

Este módulo fornece endpoints para gerenciar os status de vendas.

## Endpoints

### GET /venda-status/todos
Retorna todos os status de venda disponíveis no sistema.

#### Resposta
```json
{
  "status": true,
  "message": "Status de vendas carregados com sucesso.",
  "data": [
    {
      "venda_status_id": 1,
      "nome": "Pendente",
      "descricao": "Venda pendente de pagamento"
    },
    {
      "venda_status_id": 2,
      "nome": "Pago",
      "descricao": "Venda com pagamento confirmado"
    },
    ...
  ]
}
```

### Códigos de Status

- 200: Sucesso
- 401: Não autorizado
- 500: Erro no servidor
