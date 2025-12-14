# Books API - Backend

API REST desenvolvida em Flask para gerenciamento de livros e avaliações.

## Descrição

Esta API permite criar, listar, atualizar e deletar livros, além de gerenciar avaliações (reviews) dos usuários. Utiliza SQLite como banco de dados e implementa funcionalidades extras como busca, filtros, ordenação e paginação.

## Tecnologias

- Python 3.11
- Flask 3.0.0
- Flask-SQLAlchemy
- Flask-CORS
- SQLite

## Instalação

### Opção 1: Executar com Docker (Recomendado)

1. Clone o repositório:
```bash
git clone <seu-repositorio>
cd books-api
```

2. Construa a imagem Docker:
```bash
docker build -t books-api .
```

3. Execute o container:
```bash
docker run -p 5000:5000 books-api
```

A API estará disponível em: `http://localhost:5000`

### Opção 2: Executar localmente

1. Clone o repositório:
```bash
git clone <seu-repositorio>
cd books-api
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute a aplicação:
```bash
python app.py
```

A API estará disponível em: `http://localhost:5000`

## Rotas da API

### Books

#### GET `/api/books`
Lista todos os livros com suporte a paginação, busca e ordenação.

**Query Parameters:**
- `page` (opcional): número da página (padrão: 1)
- `per_page` (opcional): itens por página (padrão: 10)
- `search` (opcional): busca por título ou autor
- `sort_by` (opcional): ordenar por 'title', 'author' ou 'created_at'

**Resposta:**
```json
{
  "books": [...],
  "total": 25,
  "pages": 3,
  "current_page": 1
}
```

#### GET `/api/books/<id>`
Busca um livro específico por ID, incluindo suas avaliações.

#### POST `/api/books`
Cria um novo livro.

**Body:**
```json
{
  "title": "1984",
  "author": "George Orwell",
  "isbn": "978-0451524935",
  "description": "Dystopian novel",
  "cover_url": "https://example.com/cover.jpg"
}
```

#### PUT `/api/books/<id>`
Atualiza um livro existente.

**Body:** (todos os campos são opcionais)
```json
{
  "title": "Novo título",
  "author": "Novo autor",
  "description": "Nova descrição"
}
```

#### DELETE `/api/books/<id>`
Remove um livro (e todas suas avaliações).

### Reviews

#### POST `/api/books/<book_id>/reviews`
Cria uma nova avaliação para um livro.

**Body:**
```json
{
  "user_name": "João Silva",
  "rating": 5,
  "comment": "Excelente livro!"
}
```

#### GET `/api/books/<book_id>/reviews`
Lista todas as avaliações de um livro.

#### DELETE `/api/reviews/<review_id>`
Remove uma avaliação.

### Health Check

#### GET `/api/health`
Verifica se a API está funcionando.

## Estrutura do Banco de Dados

### Tabela: books
- id (INTEGER, PK)
- title (STRING)
- author (STRING)
- isbn (STRING, UNIQUE)
- description (TEXT)
- cover_url (STRING)
- created_at (DATETIME)

### Tabela: reviews
- id (INTEGER, PK)
- book_id (INTEGER, FK)
- user_name (STRING)
- rating (INTEGER)
- comment (TEXT)
- created_at (DATETIME)

## Docker

O Dockerfile está configurado para:
- Usar Python 3.11 slim
- Instalar todas as dependências
- Expor a porta 5000
- Executar a aplicação automaticamente

## Exemplo de Uso

```bash
# Criar um livro
curl -X POST http://localhost:5000/api/books \
  -H "Content-Type: application/json" \
  -d '{
    "title": "O Senhor dos Anéis",
    "author": "J.R.R. Tolkien",
    "isbn": "978-0544003415"
  }'

# Listar livros
curl http://localhost:5000/api/books

# Adicionar avaliação
curl -X POST http://localhost:5000/api/books/1/reviews \
  -H "Content-Type: application/json" \
  -d '{
    "user_name": "Maria",
    "rating": 5,
    "comment": "Obra-prima!"
  }'
```

## Funcionalidades Extras

- ✅ Paginação de resultados
- ✅ Busca por título ou autor
- ✅ Ordenação customizável
- ✅ Cálculo automático de média de avaliações
- ✅ Validação de dados
- ✅ CORS habilitado
- ✅ Relacionamento entre entidades (Books -> Reviews)
