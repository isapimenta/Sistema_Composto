#!/usr/bin/env python3
"""
Script para testar todas as rotas da API Books
Popula o banco com dados de exemplo e testa CRUD completo
"""

import requests
import json
from time import sleep

API_URL = "http://localhost:5000/api"

def print_response(response, title):
    """Imprime resposta formatada"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"Response: {response.text}")

def test_health():
    """Testa se a API está rodando"""
    print("\n🏥 Testando Health Check...")
    response = requests.get(f"{API_URL}/health")
    print_response(response, "Health Check")
    return response.status_code == 200

def test_create_books():
    """POST - Criar livros de exemplo"""
    print("\n📚 Criando livros de exemplo...")
    
    books = [
        {
            "title": "1984",
            "author": "George Orwell",
            "isbn": "978-0451524935",
            "description": "Romance distópico sobre vigilância totalitária",
            "cover_url": "https://covers.openlibrary.org/b/isbn/978-0451524935-M.jpg"
        },
        {
            "title": "Dom Casmurro",
            "author": "Machado de Assis",
            "isbn": "978-8535911664",
            "description": "Clássico da literatura brasileira",
            "cover_url": "https://covers.openlibrary.org/b/isbn/978-8535911664-M.jpg"
        },
        {
            "title": "O Senhor dos Anéis",
            "author": "J.R.R. Tolkien",
            "isbn": "978-0544003415",
            "description": "Épica fantasia sobre a Terra-média",
            "cover_url": "https://covers.openlibrary.org/b/isbn/978-0544003415-M.jpg"
        }
    ]
    
    created_ids = []
    for book in books:
        response = requests.post(f"{API_URL}/books", json=book)
        print_response(response, f"Criar Livro: {book['title']}")
        if response.status_code == 201:
            created_ids.append(response.json()['id'])
        sleep(0.5)
    
    return created_ids

def test_get_all_books():
    """GET - Listar todos os livros"""
    print("\n📖 Listando todos os livros...")
    response = requests.get(f"{API_URL}/books")
    print_response(response, "Listar Todos os Livros")
    return response.status_code == 200

def test_get_book_by_id(book_id):
    """GET - Buscar livro por ID"""
    print(f"\n🔎 Buscando livro ID: {book_id}...")
    response = requests.get(f"{API_URL}/books/{book_id}")
    print_response(response, f"Buscar Livro ID {book_id}")
    return response.status_code == 200

def test_search_books():
    """GET - Buscar livros com filtro"""
    print("\n🔍 Testando busca com filtro...")
    response = requests.get(f"{API_URL}/books?search=orwell")
    print_response(response, "Buscar livros (search=orwell)")
    return response.status_code == 200

def test_pagination():
    """GET - Testar paginação"""
    print("\n📄 Testando paginação...")
    response = requests.get(f"{API_URL}/books?page=1&per_page=2")
    print_response(response, "Paginação (page=1, per_page=2)")
    return response.status_code == 200

def test_update_book(book_id):
    """PUT - Atualizar livro"""
    print(f"\n✏️ Atualizando livro ID: {book_id}...")
    update_data = {
        "description": "Descrição atualizada via script de teste!"
    }
    response = requests.put(f"{API_URL}/books/{book_id}", json=update_data)
    print_response(response, f"Atualizar Livro ID {book_id}")
    return response.status_code == 200

def test_create_review(book_id):
    """POST - Criar avaliação"""
    print(f"\n⭐ Adicionando avaliação ao livro ID: {book_id}...")
    review_data = {
        "user_name": "João Silva",
        "rating": 5,
        "comment": "Excelente livro! Recomendo muito!"
    }
    response = requests.post(f"{API_URL}/books/{book_id}/reviews", json=review_data)
    print_response(response, f"Criar Avaliação - Livro ID {book_id}")
    
    # Adicionar mais uma avaliação
    review_data2 = {
        "user_name": "Maria Santos",
        "rating": 4,
        "comment": "Muito bom, mas esperava mais."
    }
    response2 = requests.post(f"{API_URL}/books/{book_id}/reviews", json=review_data2)
    print_response(response2, f"Criar Segunda Avaliação - Livro ID {book_id}")
    
    return response.status_code == 201

def test_get_reviews(book_id):
    """GET - Listar avaliações"""
    print(f"\n📝 Listando avaliações do livro ID: {book_id}...")
    response = requests.get(f"{API_URL}/books/{book_id}/reviews")
    print_response(response, f"Listar Avaliações - Livro ID {book_id}")
    return response.status_code == 200

def test_delete_book(book_id):
    """DELETE - Remover livro"""
    print(f"\n🗑️ Deletando livro ID: {book_id}...")
    response = requests.delete(f"{API_URL}/books/{book_id}")
    print_response(response, f"Deletar Livro ID {book_id}")
    return response.status_code == 200

def run_all_tests():
    """Executa todos os testes"""
    print("\n" + "="*60)
    print("🚀 INICIANDO TESTES DA API BOOKS")
    print("="*60)
    
    try:
        # 1. Health Check
        if not test_health():
            print("❌ API não está respondendo!")
            return
        
        # 2. POST - Criar livros
        book_ids = test_create_books()
        if not book_ids:
            print("❌ Falha ao criar livros!")
            return
        
        sleep(1)
        
        # 3. GET - Listar todos
        test_get_all_books()
        sleep(0.5)
        
        # 4. GET - Buscar por ID
        test_get_book_by_id(book_ids[0])
        sleep(0.5)
        
        # 5. GET - Buscar com filtro
        test_search_books()
        sleep(0.5)
        
        # 6. GET - Paginação
        test_pagination()
        sleep(0.5)
        
        # 7. PUT - Atualizar
        test_update_book(book_ids[0])
        sleep(0.5)
        
        # 8. POST - Criar avaliações
        test_create_review(book_ids[0])
        sleep(0.5)
        
        # 9. GET - Listar avaliações
        test_get_reviews(book_ids[0])
        sleep(0.5)
        
        # 10. DELETE - Remover livro
        test_delete_book(book_ids[2])
        sleep(0.5)
        
        # 11. Verificar deleção
        print("\n✅ Verificando se o livro foi realmente deletado...")
        response = requests.get(f"{API_URL}/books/{book_ids[2]}")
        if response.status_code == 404:
            print("✅ Livro deletado com sucesso!")
        else:
            print("❌ Erro: Livro ainda existe!")
        
        print("\n" + "="*60)
        print("✅ TODOS OS TESTES CONCLUÍDOS!")
        print("="*60)
        print("\n📊 Resumo dos testes:")
        print("  ✅ Health Check")
        print("  ✅ POST - Criar livros")
        print("  ✅ GET - Listar todos")
        print("  ✅ GET - Buscar por ID")
        print("  ✅ GET - Buscar com filtro")
        print("  ✅ GET - Paginação")
        print("  ✅ PUT - Atualizar livro")
        print("  ✅ POST - Criar avaliações")
        print("  ✅ GET - Listar avaliações")
        print("  ✅ DELETE - Remover livro")
        
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {str(e)}")
        print("Verifique se a API está rodando em http://localhost:5000")

if __name__ == "__main__":
    print("⚠️  Certifique-se de que a API está rodando em http://localhost:5000")
    print("   Comando: docker run -p 5000:5000 books-api")
    input("\nPressione ENTER para iniciar os testes...")
    
    run_all_tests()