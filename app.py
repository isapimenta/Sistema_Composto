from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# Configuração do CORS manualmente
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Configuração do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de Dados - Livro
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(20), unique=True)
    description = db.Column(db.Text)
    cover_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviews = db.relationship('Review', backref='book', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'description': self.description,
            'cover_url': self.cover_url,
            'created_at': self.created_at.isoformat(),
            'average_rating': self.get_average_rating(),
            'reviews_count': len(self.reviews)
        }

    def get_average_rating(self):
        if not self.reviews:
            return 0
        return round(sum(r.rating for r in self.reviews) / len(self.reviews), 1)

# Modelo de Dados - Avaliação
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    user_name = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'book_id': self.book_id,
            'user_name': self.user_name,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat()
        }

# Criar tabelas
with app.app_context():
    db.create_all()

# ============ ROTAS - BOOKS ============

# GET - Listar todos os livros (com filtros e paginação)
@app.route('/api/books', methods=['GET'])
def get_books():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'created_at')

    query = Book.query
    
    if search:
        query = query.filter(
            (Book.title.ilike(f'%{search}%')) | 
            (Book.author.ilike(f'%{search}%'))
        )
    
    if sort_by == 'title':
        query = query.order_by(Book.title)
    elif sort_by == 'author':
        query = query.order_by(Book.author)
    else:
        query = query.order_by(Book.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'books': [book.to_dict() for book in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

# GET - Buscar livro por ID
@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = Book.query.get_or_404(book_id)
    book_data = book.to_dict()
    book_data['reviews'] = [review.to_dict() for review in book.reviews]
    return jsonify(book_data), 200

# POST - Criar novo livro
@app.route('/api/books', methods=['POST'])
def create_book():
    data = request.get_json()
    
    if not data.get('title') or not data.get('author'):
        return jsonify({'error': 'Title and author are required'}), 400
    
    if data.get('isbn'):
        existing = Book.query.filter_by(isbn=data['isbn']).first()
        if existing:
            return jsonify({'error': 'Book with this ISBN already exists'}), 400
    
    new_book = Book(
        title=data['title'],
        author=data['author'],
        isbn=data.get('isbn'),
        description=data.get('description'),
        cover_url=data.get('cover_url')
    )
    
    db.session.add(new_book)
    db.session.commit()
    
    return jsonify(new_book.to_dict()), 201

# PUT - Atualizar livro
@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    data = request.get_json()
    
    if data.get('title'):
        book.title = data['title']
    if data.get('author'):
        book.author = data['author']
    if data.get('isbn'):
        book.isbn = data['isbn']
    if data.get('description'):
        book.description = data['description']
    if data.get('cover_url'):
        book.cover_url = data['cover_url']
    
    db.session.commit()
    
    return jsonify(book.to_dict()), 200

# DELETE - Remover livro
@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    
    return jsonify({'message': 'Book deleted successfully'}), 200

# ============ ROTAS - REVIEWS ============

# POST - Criar avaliação
@app.route('/api/books/<int:book_id>/reviews', methods=['POST'])
def create_review(book_id):
    book = Book.query.get_or_404(book_id)
    data = request.get_json()
    
    if not data.get('user_name') or not data.get('rating'):
        return jsonify({'error': 'User name and rating are required'}), 400
    
    if not 1 <= data['rating'] <= 5:
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400
    
    new_review = Review(
        book_id=book_id,
        user_name=data['user_name'],
        rating=data['rating'],
        comment=data.get('comment', '')
    )
    
    db.session.add(new_review)
    db.session.commit()
    
    return jsonify(new_review.to_dict()), 201

# GET - Listar avaliações de um livro
@app.route('/api/books/<int:book_id>/reviews', methods=['GET'])
def get_reviews(book_id):
    book = Book.query.get_or_404(book_id)
    reviews = [review.to_dict() for review in book.reviews]
    return jsonify(reviews), 200

# DELETE - Remover avaliação
@app.route('/api/reviews/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    db.session.delete(review)
    db.session.commit()
    
    return jsonify({'message': 'Review deleted successfully'}), 200

# Rota de health check
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)