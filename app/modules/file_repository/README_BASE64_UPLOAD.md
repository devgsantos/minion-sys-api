# Documentação - Upload de Imagem via Base64

A nova função `upload_image_str` permite fazer upload de arquivos enviando dados em formato JSON com base64, como alternativa ao upload tradicional via form-data.

## Endpoint

**POST** `/arquivo/base64?empresa_id={id_empresa}`

## Formato da Requisição

### Headers
```
Content-Type: application/json
x-auth-token: {seu_token_jwt}
```

### Body (JSON)
```json
{
  "tipo": "produto",
  "file": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD...",
  "filename": "produto_123.jpg"
}
```

### Parâmetros

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `tipo` | string | ✅ | Tipo do arquivo (ex: "produto", "categoria", etc.) |
| `file` | string | ✅ | Dados do arquivo em base64 (com ou sem prefixo data:) |
| `filename` | string | ✅ | Nome do arquivo com extensão |
| `empresa_id` | string | ✅ | ID da empresa (parâmetro na URL) |

## Exemplos de Uso

### JavaScript/TypeScript
```javascript
const uploadImage = async (imageBase64, filename, type, companyId) => {
  const response = await fetch(`/arquivo/base64?empresa_id=${companyId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-auth-token': localStorage.getItem('token')
    },
    body: JSON.stringify({
      tipo: type,
      file: imageBase64,
      filename: filename
    })
  });
  
  return await response.json();
};

// Uso com FileReader
const handleFileUpload = (file) => {
  const reader = new FileReader();
  reader.onload = async (e) => {
    const base64 = e.target.result;
    const result = await uploadImage(base64, file.name, 'produto', '1');
    console.log(result);
  };
  reader.readAsDataURL(file);
};
```

### Curl
```bash
curl -X POST "http://localhost:5000/arquivo/base64?empresa_id=1" \
  -H "Content-Type: application/json" \
  -H "x-auth-token: seu_token_aqui" \
  -d '{
    "tipo": "produto",
    "file": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD...",
    "filename": "produto_123.jpg"
  }'
```

### Python
```python
import requests
import base64

def upload_image_base64(image_path, filename, file_type, company_id, token):
    # Ler e codificar imagem
    with open(image_path, 'rb') as img_file:
        img_data = base64.b64encode(img_file.read()).decode('utf-8')
    
    # Dados da requisição
    data = {
        'tipo': file_type,
        'file': f'data:image/jpeg;base64,{img_data}',
        'filename': filename
    }
    
    # Headers
    headers = {
        'Content-Type': 'application/json',
        'x-auth-token': token
    }
    
    # Requisição
    response = requests.post(
        f'http://localhost:5000/arquivo/base64?empresa_id={company_id}',
        json=data,
        headers=headers
    )
    
    return response.json()
```

## Processamento de Imagens

### Para tipo "produto":
1. Cria subpasta com nome do arquivo (sem extensão)
2. Gera nome sequencial (1.png, 2.png, etc.)
3. Processa com PIL e salva como PNG
4. Atualiza registro do produto no banco
5. Respeita limite de imagens por produto

### Para outros tipos:
1. Processa com PIL se for imagem
2. Converte para PNG
3. Salva na pasta do tipo especificado

### Para arquivos não-imagem:
1. Salva binário diretamente
2. Mantém nome original

## Respostas

### Sucesso (200)
```json
{
  "status": true,
  "message": "Arquivo salvo com sucesso.",
  "file_path": "produto_123/1.png"
}
```

### Erros Possíveis

#### Dados incompletos (400)
```json
{
  "status": false,
  "message": "Dados incompletos. Campos obrigatórios: tipo, file, filename."
}
```

#### Empresa ID faltando (400)
```json
{
  "status": false,
  "message": "Parâmetro 'empresa_id' é obrigatório na URL."
}
```

#### Base64 inválido (400)
```json
{
  "status": false,
  "message": "Erro ao decodificar base64: Invalid base64-encoded string"
}
```

#### Limite de imagens atingido (304)
```json
{
  "status": false,
  "message": "Este produto já possui o limite de imagens cadastradas. Por favor apague ou substitua uma das imagens."
}
```

#### Erro no processamento (400)
```json
{
  "status": false,
  "message": "Erro ao processar imagem: cannot identify image file"
}
```

## Vantagens

✅ **Integração simples** com aplicações SPA  
✅ **Não requer form-data** - apenas JSON  
✅ **Compatível** com bibliotecas de upload  
✅ **Processamento automático** de imagens  
✅ **Validação** de base64 e tipos de arquivo  
✅ **Estrutura de pastas** organizada  

## Diferenças vs Upload Tradicional

| Aspecto | upload_image | upload_image_str |
|---------|--------------|------------------|
| Formato | form-data | JSON |
| Arquivo | FileStorage | base64 string |
| Headers | multipart/form-data | application/json |
| Empresa ID | form field | URL parameter |
| Uso | Formulários tradicionais | APIs REST/SPA |

## Compatibilidade

A função é **totalmente compatível** com a estrutura existente e usa as mesmas validações e processamentos da função original `upload_image`.
