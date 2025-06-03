from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort, session
from library_queries_graphdb import LibraryQueries
from datetime import datetime, timedelta
import re

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

queries = LibraryQueries("http://localhost:7200/repositories/TrabalhoPratico")

@app.route('/')
@app.route('/page/<int:page>')
def index(page=1):
    """Home page with book listing"""
    per_page = 15
    books, total_books = queries.get_all_books(page=page, per_page=per_page)
    total_pages = (total_books + per_page - 1) // per_page  
    
    stats = queries.get_ontology_stats()
    
    return render_template('index.html', books=books, page=page, total_pages=total_pages, 
                          total_books=total_books, stats=stats)

@app.route('/authors')
@app.route('/authors/page/<int:page>')
def authors(page=1):
    """Authors page"""
    per_page = 15
    authors, total_authors = queries.get_all_authors(page=page, per_page=per_page)
    
    authors_books = {}
    for author in authors:
        author_id = extract_id(author.author)
        if author_id:
            books = list(queries.get_author_books(author_id))[:3]  
            authors_books[author_id] = books
    
    total_pages = (total_authors + per_page - 1) // per_page  
    return render_template('authors.html', authors=authors, page=page, 
                          total_pages=total_pages, total_authors=total_authors,
                          authors_books=authors_books)

@app.route('/search', methods=['GET', 'POST'])
@app.route('/search/page/<int:page>', methods=['GET', 'POST'])
def search(page=1):
    """Advanced search functionality with pagination"""
    per_page = 15
    
    if request.method == 'POST':
        search_term = request.form.get('search_term', '').strip()
        search_type = request.form.get('search_type', 'all')
        
        show_advanced = 'show_advanced' in request.form
        
        try:
            year_from = int(request.form.get('year_from')) if request.form.get('year_from') else None
        except ValueError:
            year_from = None
            
        try:
            year_to = int(request.form.get('year_to')) if request.form.get('year_to') else None
        except ValueError:
            year_to = None
            
        sort_by = request.form.get('sort_by', 'title')
        
        session['search_params'] = {
            'search_term': search_term,
            'search_type': search_type,
            'show_advanced': show_advanced,
            'year_from': year_from,
            'year_to': year_to,
            'sort_by': sort_by
        }
        
        return redirect(url_for('search', page=1))
    
    elif 'search_params' in session:
        params = session['search_params']
        search_term = params.get('search_term', '')
        search_type = params.get('search_type', 'all')
        show_advanced = params.get('show_advanced', False)
        year_from = params.get('year_from')
        year_to = params.get('year_to')
        sort_by = params.get('sort_by', 'title')
        
        search_filters = []
        if year_from:
            search_filters.append(f"From year {year_from}")
        if year_to:
            search_filters.append(f"To year {year_to}")
        search_filters = ", ".join(search_filters)
        
        results = []
        total_results = 0
        if search_term:
            results, total_results = queries.search_books(
                search_term=search_term,
                search_type=search_type,
                year_from=year_from,
                year_to=year_to,
                sort_by=sort_by,
                page=page,
                per_page=per_page
            )
            
        total_pages = (total_results + per_page - 1) // per_page 
            
        return render_template(
            'search.html',
            results=results,
            search_term=search_term,
            search_type=search_type,
            show_advanced=show_advanced,
            year_from=year_from,
            year_to=year_to,
            sort_by=sort_by,
            search_filters=search_filters,
            page=page,
            total_pages=total_pages,
            total_results=total_results
        )
        
    return render_template('search.html')

@app.route('/ontology_info')
def ontology_info():
    """Display ontology statistics and information"""
    stats = queries.get_ontology_stats()
    return render_template('ontology_info.html', stats=stats)

@app.route('/users')
@app.route('/users/page/<int:page>')
def users(page=1):
    """Users page"""
    per_page = 15
    users, total_users = queries.get_all_users(page=page, per_page=per_page)
    
    users_loans = {}
    today = datetime.now().date()
    for user in users:
        user_id = extract_id(user.user)
        if user_id:
            all_loans = queries.get_user_loans(user_id)
            active_loans = [loan for loan in all_loans if loan['return_date'].date() >= today][:3]
            users_loans[user_id] = active_loans
    
    total_pages = (total_users + per_page - 1) // per_page 
    return render_template('users.html', users=users, page=page, 
                          total_pages=total_pages, total_users=total_users,
                          users_loans=users_loans)

@app.route('/loans')
def loans():
    """Loans page"""
    loans = queries.get_all_loans()
    return render_template('loans.html', loans=loans)


@app.route('/book/<book_id>')
def book_detail(book_id):
    """Book detail page"""
    book = queries.get_book_by_id(book_id)
    if not book:
        abort(404)
    
    loans = queries.get_book_loans(book_id)
    
    related_books = queries.get_related_books(book_id)
    
    return render_template(
        'book_detail.html', 
        book=book, 
        book_id=book_id,
        loans=loans,
        related_books=related_books
    )

@app.route('/author/<author_id>')
def author_detail(author_id):
    """Author detail page"""
    author = queries.get_author_by_id(author_id)
    if not author:
        abort(404)
    
    books = queries.get_author_books(author_id)
    
    genres = queries.get_author_genres(author_id)
    
    return render_template(
        'author_detail.html', 
        author=author, 
        author_id=author_id,
        books=books,
        genres=genres
    )

@app.route('/user/<user_id>')
def user_detail(user_id):
    """User detail page"""
    user = queries.get_user_by_id(user_id)
    if not user:
        abort(404)
    
    loans = queries.get_user_loans(user_id)
    
    favorite_genres = queries.get_user_favorite_genres(user_id)
    
    favorite_authors = queries.get_user_favorite_authors(user_id)
    
    return render_template(
        'user_detail.html', 
        user=user, 
        user_id=user_id,
        loans=loans,
        favorite_genres=favorite_genres,
        favorite_authors=favorite_authors
    )

@app.template_filter('extract_id')
def extract_id(uri):
    """Extract ID from URI"""
    if uri:
        match = re.search(r'#([^#]+)$', str(uri))
        if match:
            return match.group(1)
    return ''

@app.context_processor
def utility_processor():
    def now():
        return datetime.now()
    
    return dict(now=now)

if __name__ == '__main__':
    app.run(debug=True)