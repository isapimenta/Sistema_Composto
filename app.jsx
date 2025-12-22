import React, { useState, useEffect } from 'react';
import './App.css';

const API_URL = 'http://localhost:5000/api';
const OPEN_LIBRARY_API = 'https://openlibrary.org/search.json';

function App() {
  const [books, setBooks] = useState([]);
  const [selectedBook, setSelectedBook] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [externalSearchQuery, setExternalSearchQuery] = useState('');
  const [externalBooks, setExternalBooks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('myBooks');

  // Form states
  const [newBook, setNewBook] = useState({
    title: '',
    author: '',
    isbn: '',
    description: '',
    cover_url: ''
  });

  const [newReview, setNewReview] = useState({
    user_name: '',
    rating: 5,
    comment: ''
  });

  // GET - Buscar livros da API
  useEffect(() => {
    fetchBooks();
  }, []);

  const fetchBooks = async () => {
    try {
      const response = await fetch(`${API_URL}/books?per_page=20`);
      const data = await response.json();
      setBooks(data.books);
    } catch (error) {
      console.error('Erro ao buscar livros:', error);
    }
  };

  // GET - Buscar livro específico
  const fetchBookDetails = async (bookId) => {
    try {
      const response = await fetch(`${API_URL}/books/${bookId}`);
      const data = await response.json();
      setSelectedBook(data);
    } catch (error) {
      console.error('Erro ao buscar detalhes:', error);
    }
  };

  // POST - Criar novo livro
  const handleCreateBook = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API_URL}/books`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newBook)
      });

      if (response.ok) {
        alert('Livro criado com sucesso!');
        setNewBook({ title: '', author: '', isbn: '', description: '', cover_url: '' });
        fetchBooks();
      }
    } catch (error) {
      console.error('Erro ao criar livro:', error);
    }
  };

  // PUT - Atualizar livro
  const handleUpdateBook = async (bookId) => {
    const updatedData = {
      title: prompt('Novo título:', selectedBook.title) || selectedBook.title,
      author: prompt('Novo autor:', selectedBook.author) || selectedBook.author
    };

    try {
      const response = await fetch(`${API_URL}/books/${bookId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedData)
      });

      if (response.ok) {
        alert('Livro atualizado!');
        fetchBookDetails(bookId);
        fetchBooks();
      }
    } catch (error) {
      console.error('Erro ao atualizar livro:', error);
    }
  };

  // DELETE - Remover livro
  const handleDeleteBook = async (bookId) => {
    if (!window.confirm('Tem certeza que deseja deletar este livro?')) return;

    try {
      const response = await fetch(`${API_URL}/books/${bookId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        alert('Livro deletado!');
        setSelectedBook(null);
        fetchBooks();
      }
    } catch (error) {
      console.error('Erro ao deletar livro:', error);
    }
  };

  // POST - Adicionar avaliação
  const handleAddReview = async (e) => {
    e.preventDefault();
    if (!selectedBook) return;

    try {
      const response = await fetch(`${API_URL}/books/${selectedBook.id}/reviews`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newReview)
      });

      if (response.ok) {
        alert('Avaliação adicionada!');
        setNewReview({ user_name: '', rating: 5, comment: '' });
        fetchBookDetails(selectedBook.id);
      }
    } catch (error) {
      console.error('Erro ao adicionar avaliação:', error);
    }
  };

  // API Externa - Buscar livros na Open Library
  const searchExternalBooks = async () => {
    if (!externalSearchQuery.trim()) return;

    setLoading(true);
    try {
      const response = await fetch(
        `${OPEN_LIBRARY_API}?q=${encodeURIComponent(externalSearchQuery)}&limit=10`
      );
      const data = await response.json();
      setExternalBooks(data.docs || []);
    } catch (error) {
      console.error('Erro ao buscar na API externa:', error);
    } finally {
      setLoading(false);
    }
  };

  // Importar livro da API externa para nossa API
  const importBook = async (externalBook) => {
    const bookData = {
      title: externalBook.title,
      author: externalBook.author_name?.[0] || 'Desconhecido',
      isbn: externalBook.isbn?.[0] || '',
      description: externalBook.first_sentence?.[0] || '',
      cover_url: externalBook.cover_i 
        ? `https://covers.openlibrary.org/b/id/${externalBook.cover_i}-M.jpg`
        : ''
    };

    try {
      const response = await fetch(`${API_URL}/books`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(bookData)
      });

      if (response.ok) {
        alert('Livro importado com sucesso!');
        fetchBooks();
        setActiveTab('myBooks');
      }
    } catch (error) {
      console.error('Erro ao importar livro:', error);
    }
  };

  return (
    <div className="App">
      <header>
        <h1>📚 Biblioteca Online</h1>
        <p>Gerencie sua coleção de livros e avaliações</p>
      </header>

      <div className="tabs">
        <button 
          className={activeTab === 'myBooks' ? 'active' : ''} 
          onClick={() => setActiveTab('myBooks')}
        >
          Meus Livros
        </button>
        <button 
          className={activeTab === 'search' ? 'active' : ''} 
          onClick={() => setActiveTab('search')}
        >
          Buscar Livros (API Externa)
        </button>
        <button 
          className={activeTab === 'add' ? 'active' : ''} 
          onClick={() => setActiveTab('add')}
        >
          Adicionar Livro
        </button>
      </div>

      <div className="content">
        {/* Tab: Meus Livros */}
        {activeTab === 'myBooks' && (
          <div className="my-books">
            <h2>Minha Coleção</h2>
            <div className="books-grid">
              {books.map(book => (
                <div key={book.id} className="book-card" onClick={() => fetchBookDetails(book.id)}>
                  {book.cover_url && <img src={book.cover_url} alt={book.title} />}
                  <h3>{book.title}</h3>
                  <p className="author">{book.author}</p>
                  <p className="rating">⭐ {book.average_rating || 'Sem avaliações'}</p>
                  <p className="reviews-count">{book.reviews_count} avaliações</p>
                </div>
              ))}
            </div>

            {selectedBook && (
              <div className="modal" onClick={() => setSelectedBook(null)}>
                <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                  <span className="close" onClick={() => setSelectedBook(null)}>&times;</span>
                  <h2>{selectedBook.title}</h2>
                  <p><strong>Autor:</strong> {selectedBook.author}</p>
                  <p><strong>ISBN:</strong> {selectedBook.isbn || 'N/A'}</p>
                  <p><strong>Descrição:</strong> {selectedBook.description || 'Sem descrição'}</p>
                  <p><strong>Nota Média:</strong> ⭐ {selectedBook.average_rating}</p>

                  <div className="actions">
                    <button onClick={() => handleUpdateBook(selectedBook.id)}>Editar</button>
                    <button onClick={() => handleDeleteBook(selectedBook.id)} className="delete">Deletar</button>
                  </div>

                  <h3>Avaliações</h3>
                  <div className="reviews">
                    {selectedBook.reviews?.map(review => (
                      <div key={review.id} className="review">
                        <p><strong>{review.user_name}</strong> - {'⭐'.repeat(review.rating)}</p>
                        <p>{review.comment}</p>
                      </div>
                    ))}
                  </div>

                  <h3>Adicionar Avaliação</h3>
                  <form onSubmit={handleAddReview} className="review-form">
                    <input
                      type="text"
                      placeholder="Seu nome"
                      value={newReview.user_name}
                      onChange={(e) => setNewReview({...newReview, user_name: e.target.value})}
                      required
                    />
                    <select
                      value={newReview.rating}
                      onChange={(e) => setNewReview({...newReview, rating: parseInt(e.target.value)})}
                    >
                      {[5,4,3,2,1].map(n => <option key={n} value={n}>{n} estrelas</option>)}
                    </select>
                    <textarea
                      placeholder="Comentário (opcional)"
                      value={newReview.comment}
                      onChange={(e) => setNewReview({...newReview, comment: e.target.value})}
                    />
                    <button type="submit">Enviar Avaliação</button>
                  </form>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Tab: Buscar na API Externa */}
        {activeTab === 'search' && (
          <div className="external-search">
            <h2>Buscar Livros na Open Library</h2>
            <div className="search-box">
              <input
                type="text"
                placeholder="Digite o nome do livro..."
                value={externalSearchQuery}
                onChange={(e) => setExternalSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && searchExternalBooks()}
              />
              <button onClick={searchExternalBooks}>Buscar</button>
            </div>

            {loading && <p>Carregando...</p>}

            <div className="books-grid">
              {externalBooks.map((book, index) => (
                <div key={index} className="book-card external">
                  {book.cover_i && (
                    <img 
                      src={`https://covers.openlibrary.org/b/id/${book.cover_i}-M.jpg`} 
                      alt={book.title} 
                    />
                  )}
                  <h3>{book.title}</h3>
                  <p className="author">{book.author_name?.[0] || 'Autor desconhecido'}</p>
                  <p className="year">Ano: {book.first_publish_year || 'N/A'}</p>
                  <button onClick={() => importBook(book)}>Importar para Minha Coleção</button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tab: Adicionar Livro */}
        {activeTab === 'add' && (
          <div className="add-book">
            <h2>Adicionar Novo Livro</h2>
            <form onSubmit={handleCreateBook}>
              <input
                type="text"
                placeholder="Título"
                value={newBook.title}
                onChange={(e) => setNewBook({...newBook, title: e.target.value})}
                required
              />
              <input
                type="text"
                placeholder="Autor"
                value={newBook.author}
                onChange={(e) => setNewBook({...newBook, author: e.target.value})}
                required
              />
              <input
                type="text"
                placeholder="ISBN (opcional)"
                value={newBook.isbn}
                onChange={(e) => setNewBook({...newBook, isbn: e.target.value})}
              />
              <textarea
                placeholder="Descrição (opcional)"
                value={newBook.description}
                onChange={(e) => setNewBook({...newBook, description: e.target.value})}
              />
              <input
                type="text"
                placeholder="URL da Capa (opcional)"
                value={newBook.cover_url}
                onChange={(e) => setNewBook({...newBook, cover_url: e.target.value})}
              />
              <button type="submit">Adicionar Livro</button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;