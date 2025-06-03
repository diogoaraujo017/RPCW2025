from SPARQLWrapper import SPARQLWrapper, JSON
from datetime import datetime
import re

class LibraryQueries:
    def __init__(self, endpoint_url="http://localhost:7200/repositories/library"):
        """Inicializa a classe de consultas usando o GraphDB"""
        self.endpoint = endpoint_url
        self.sparql = SPARQLWrapper(endpoint_url)
        self.sparql.setReturnFormat(JSON)
        
        self.prefixes = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX library: <http://example.org/library#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        """
    
    def execute_query(self, query):
        """Executa uma consulta SPARQL e retorna os resultados"""
        full_query = self.prefixes + query
        self.sparql.setQuery(full_query)
        results = self.sparql.query().convert()
        return results["results"]["bindings"]
    
    def get_all_books(self, page=1, per_page=15):
        """Get all books with their properties with pagination"""
        offset = (page - 1) * per_page
        query = f"""
        SELECT ?book ?title ?isbn ?year ?author ?author_name ?publisher ?publisher_name ?genre ?genre_name ?active_loan
        WHERE {{
            ?book rdf:type library:Book .
            ?book library:hasTitle ?title .
            OPTIONAL {{ ?book library:hasISBN ?isbn }}
            OPTIONAL {{ ?book library:publicationYear ?year }}
            OPTIONAL {{ 
                ?book library:hasAuthor ?author .
                ?author library:name ?author_name 
            }}
            OPTIONAL {{ 
                ?book library:hasPublisher ?publisher .
                ?publisher library:name ?publisher_name 
            }}
            OPTIONAL {{ 
                ?book library:hasGenre ?genre .
                ?genre library:name ?genre_name 
            }}
            OPTIONAL {{ ?book library:activeLoan ?active_loan }}
        }}
        ORDER BY ?title
        LIMIT {per_page}
        OFFSET {offset}
        """
        results = self.execute_query(query)
        
        count_query = """
        SELECT (COUNT(?book) as ?count)
        WHERE {
            ?book rdf:type library:Book .
        }
        """
        count_result = self.execute_query(count_query)
        total_count = int(count_result[0]["count"]["value"])
        
        formatted_results = []
        for book in results:
            formatted_book = {}
            for key, value in book.items():
                formatted_book[key] = value["value"]
            formatted_results.append(type('obj', (object,), formatted_book))
        
        return formatted_results, total_count
    
    def get_all_authors(self, page=1, per_page=15):
        """Get all authors with pagination"""
        offset = (page - 1) * per_page
        query = f"""
        SELECT ?author ?name ?birth_year
        WHERE {{
            ?author rdf:type library:Author .
            ?author library:name ?name .
            OPTIONAL {{ ?author library:birthYear ?birth_year }}
        }}
        ORDER BY ?name
        LIMIT {per_page}
        OFFSET {offset}
        """
        results = self.execute_query(query)
        
        count_query = """
        SELECT (COUNT(?author) as ?count)
        WHERE {
            ?author rdf:type library:Author .
        }
        """
        count_result = self.execute_query(count_query)
        total_count = int(count_result[0]["count"]["value"])
        
        formatted_results = []
        for author in results:
            formatted_author = {}
            for key, value in author.items():
                formatted_author[key] = value["value"]
            formatted_results.append(type('obj', (object,), formatted_author))
        
        return formatted_results, total_count
    
    def get_author_books(self, author_id):
        """Get all books by a specific author"""
        author_uri = f"http://example.org/library#{author_id}"
        
        query = f"""
        SELECT ?book ?title ?isbn ?year ?publisher_name ?genre_name
        WHERE {{
            ?book rdf:type library:Book .
            ?book library:hasAuthor <{author_uri}> .
            ?book library:hasTitle ?title .
            OPTIONAL {{ ?book library:hasISBN ?isbn }}
            OPTIONAL {{ ?book library:publicationYear ?year }}
            OPTIONAL {{ 
                ?book library:hasPublisher ?publisher .
                ?publisher library:name ?publisher_name 
            }}
            OPTIONAL {{ 
                ?book library:hasGenre ?genre .
                ?genre library:name ?genre_name 
            }}
        }}
        ORDER BY ?year ?title
        """
        results = self.execute_query(query)
        
        formatted_results = []
        for book in results:
            formatted_book = {}
            for key, value in book.items():
                formatted_book[key] = value["value"]
            formatted_results.append(type('obj', (object,), formatted_book))
        
        return formatted_results
    
    def search_books(self, search_term, search_type='all', year_from=None, year_to=None, sort_by='title', page=1, per_page=15):
        """
        Search books with advanced filtering options and pagination
        """
        offset = (page - 1) * per_page
        
        query = """
        SELECT ?book ?title ?isbn ?year ?author ?author_name ?publisher ?publisher_name ?genre ?genre_name
        WHERE {
            ?book rdf:type library:Book .
            ?book library:hasTitle ?title .
            
            # Campos opcionais para garantir que todos os dados disponíveis sejam retornados
            OPTIONAL { ?book library:hasISBN ?isbn }
            OPTIONAL { ?book library:publicationYear ?year }
            OPTIONAL { 
                ?book library:hasAuthor ?author .
                ?author library:name ?author_name 
            }
            OPTIONAL { 
                ?book library:hasPublisher ?publisher .
                ?publisher library:name ?publisher_name 
            }
            OPTIONAL { 
                ?book library:hasGenre ?genre .
                ?genre library:name ?genre_name 
            }
        """
        
        if search_term:
            if search_type == 'all':
                query += f"""
                FILTER (
                    CONTAINS(LCASE(?title), LCASE("{search_term}")) || 
                    CONTAINS(LCASE(?author_name), LCASE("{search_term}")) ||
                    CONTAINS(LCASE(?genre_name), LCASE("{search_term}")) ||
                    CONTAINS(LCASE(?publisher_name), LCASE("{search_term}")) ||
                    CONTAINS(LCASE(?isbn), LCASE("{search_term}"))
                )
                """
            elif search_type == 'title':
                query += f'FILTER (CONTAINS(LCASE(?title), LCASE("{search_term}")))'
            elif search_type == 'author':
                query += f'FILTER (CONTAINS(LCASE(?author_name), LCASE("{search_term}")))'
            elif search_type == 'genre':
                query += f'FILTER (CONTAINS(LCASE(?genre_name), LCASE("{search_term}")))'
            elif search_type == 'publisher':
                query += f'FILTER (CONTAINS(LCASE(?publisher_name), LCASE("{search_term}")))'
            elif search_type == 'isbn':
                query += f'FILTER (CONTAINS(LCASE(?isbn), LCASE("{search_term}")))'
        
        if year_from is not None:
            query += f'FILTER (?year >= {year_from})'
        if year_to is not None:
            query += f'FILTER (?year <= {year_to})'
        
        query += "\n}"
        
        if sort_by == 'title':
            query += "\nORDER BY ?title"
        elif sort_by == 'title_desc':
            query += "\nORDER BY DESC(?title)"
        elif sort_by == 'year':
            query += "\nORDER BY ?year ?title"
        elif sort_by == 'year_desc':
            query += "\nORDER BY DESC(?year) ?title"
        elif sort_by == 'author':
            query += "\nORDER BY ?author_name ?title"
        else:
            query += "\nORDER BY ?title"  
        
        query += f"\nLIMIT {per_page} OFFSET {offset}"
        
        results = self.execute_query(query)
        
        count_query = """
        SELECT (COUNT(DISTINCT ?book) as ?count)
        WHERE {
            ?book rdf:type library:Book .
            ?book library:hasTitle ?title .
            
            # Campos opcionais para garantir que todos os dados disponíveis sejam retornados
            OPTIONAL { ?book library:hasISBN ?isbn }
            OPTIONAL { ?book library:publicationYear ?year }
            OPTIONAL { 
                ?book library:hasAuthor ?author .
                ?author library:name ?author_name 
            }
            OPTIONAL { 
                ?book library:hasPublisher ?publisher .
                ?publisher library:name ?publisher_name 
            }
            OPTIONAL { 
                ?book library:hasGenre ?genre .
                ?genre library:name ?genre_name 
            }
        """
        
        if search_term:
            if search_type == 'all':
                count_query += f"""
                FILTER (
                    CONTAINS(LCASE(?title), LCASE("{search_term}")) || 
                    CONTAINS(LCASE(?author_name), LCASE("{search_term}")) ||
                    CONTAINS(LCASE(?genre_name), LCASE("{search_term}")) ||
                    CONTAINS(LCASE(?publisher_name), LCASE("{search_term}")) ||
                    CONTAINS(LCASE(?isbn), LCASE("{search_term}"))
                )
                """
            elif search_type == 'title':
                count_query += f'FILTER (CONTAINS(LCASE(?title), LCASE("{search_term}")))'
            elif search_type == 'author':
                count_query += f'FILTER (CONTAINS(LCASE(?author_name), LCASE("{search_term}")))'
            elif search_type == 'genre':
                count_query += f'FILTER (CONTAINS(LCASE(?genre_name), LCASE("{search_term}")))'
            elif search_type == 'publisher':
                count_query += f'FILTER (CONTAINS(LCASE(?publisher_name), LCASE("{search_term}")))'
            elif search_type == 'isbn':
                count_query += f'FILTER (CONTAINS(LCASE(?isbn), LCASE("{search_term}")))'
        
        if year_from is not None:
            count_query += f'FILTER (?year >= {year_from})'
        if year_to is not None:
            count_query += f'FILTER (?year <= {year_to})'
        
        count_query += "\n}"
        
        count_results = self.execute_query(count_query)
        total_count = int(count_results[0]["count"]["value"]) if count_results else 0
        
        formatted_results = []
        for book in results:
            formatted_book = {}
            for key, value in book.items():
                formatted_book[key] = value["value"]
            formatted_results.append(type('obj', (object,), formatted_book))
        
        return formatted_results, total_count
    
    def get_ontology_stats(self):
        """Get statistics about the ontology"""
        books_query = """
        SELECT (COUNT(?book) as ?count)
        WHERE {
            ?book rdf:type library:Book .
        }
        """
        authors_query = """
        SELECT (COUNT(?author) as ?count)
        WHERE {
            ?author rdf:type library:Author .
        }
        """
        publishers_query = """
        SELECT (COUNT(?publisher) as ?count)
        WHERE {
            ?publisher rdf:type library:Publisher .
        }
        """
        genres_query = """
        SELECT (COUNT(?genre) as ?count)
        WHERE {
            ?genre rdf:type library:Genre .
        }
        """
        triples_query = """
        SELECT (COUNT(*) as ?count)
        WHERE {
            ?s ?p ?o .
        }
        """
        
        books_count = int(self.execute_query(books_query)[0]["count"]["value"])
        authors_count = int(self.execute_query(authors_query)[0]["count"]["value"])
        publishers_count = int(self.execute_query(publishers_query)[0]["count"]["value"])
        genres_count = int(self.execute_query(genres_query)[0]["count"]["value"])
        triples_count = int(self.execute_query(triples_query)[0]["count"]["value"])
        
        return {
            'books': books_count,
            'authors': authors_count,
            'publishers': publishers_count,
            'genres': genres_count,
            'total_triples': triples_count
        }
    
    def get_all_users(self, page=1, per_page=15):
        """Get all users with pagination"""
        offset = (page - 1) * per_page
        query = f"""
        SELECT ?user ?name ?email
        WHERE {{
            ?user rdf:type library:User .
            ?user library:name ?name .
            ?user library:userEmail ?email .
        }}
        ORDER BY ?name
        LIMIT {per_page}
        OFFSET {offset}
        """
        results = self.execute_query(query)
        
        count_query = """
        SELECT (COUNT(?user) as ?count)
        WHERE {
            ?user rdf:type library:User .
        }
        """
        count_result = self.execute_query(count_query)
        total_count = int(count_result[0]["count"]["value"])
        
        formatted_results = []
        for user in results:
            formatted_user = {}
            for key, value in user.items():
                formatted_user[key] = value["value"]
            formatted_results.append(type('obj', (object,), formatted_user))
        
        return formatted_results, total_count

    def get_all_loans(self):
        """Get all loans with details including book_id and user_id"""
        query = """
        SELECT ?loan ?book ?book_title ?user ?user_name ?loan_date ?return_date
        WHERE {
            ?loan rdf:type library:Loan .
            ?loan library:borrower ?user .
            ?loan library:borrowedBook ?book .
            ?loan library:loanDate ?loan_date .
            ?loan library:returnDate ?return_date .
            ?user library:name ?user_name .
            ?book library:hasTitle ?book_title .
        }
        ORDER BY ?loan_date
        """
        
        results = self.execute_query(query)
        
        processed_loans = []
        for row in results:
            book_uri = row["book"]["value"]
            user_uri = row["user"]["value"]
            book_id = book_uri.split('#')[-1] if '#' in book_uri else ''
            user_id = user_uri.split('#')[-1] if '#' in user_uri else ''
            
            loan_date = datetime.strptime(row["loan_date"]["value"], '%Y-%m-%d')
            return_date = datetime.strptime(row["return_date"]["value"], '%Y-%m-%d')
            
            processed_loans.append({
                'loan': row["loan"]["value"],
                'book': book_uri,
                'book_id': book_id,
                'book_title': row["book_title"]["value"],
                'user': user_uri,
                'user_id': user_id,
                'user_name': row["user_name"]["value"],
                'loan_date': loan_date,
                'return_date': return_date
            })
        
        return processed_loans
    
    def get_book_by_id(self, book_id):
        """Get detailed information about a specific book"""
        book_uri = f"http://example.org/library#{book_id}"
        
        query = f"""
        SELECT ?title ?isbn ?year ?author ?author_name ?publisher ?publisher_name 
               ?genre ?genre_name ?active_loan ?number_of_pages
        WHERE {{
            <{book_uri}> rdf:type library:Book .
            <{book_uri}> library:hasTitle ?title .
            OPTIONAL {{ <{book_uri}> library:hasISBN ?isbn }}
            OPTIONAL {{ <{book_uri}> library:publicationYear ?year }}
            OPTIONAL {{ 
                <{book_uri}> library:hasAuthor ?author .
                ?author library:name ?author_name 
            }}
            OPTIONAL {{ 
                <{book_uri}> library:hasPublisher ?publisher .
                ?publisher library:name ?publisher_name 
            }}
            OPTIONAL {{ 
                <{book_uri}> library:hasGenre ?genre .
                ?genre library:name ?genre_name 
            }}
            OPTIONAL {{ <{book_uri}> library:activeLoan ?active_loan }}
            OPTIONAL {{ <{book_uri}> library:numberOfPages ?number_of_pages }}
        }}
        """
        results = self.execute_query(query)
        if results:
            formatted_book = {}
            for key, value in results[0].items():
                formatted_book[key] = value["value"]
            return type('obj', (object,), formatted_book)
        return None
    
    def get_book_loans(self, book_id):
        """Get loan history for a specific book"""
        book_uri = f"http://example.org/library#{book_id}"
        
        query = f"""
        SELECT ?loan ?user ?user_name ?loan_date ?return_date
        WHERE {{
            ?loan rdf:type library:Loan .
            ?loan library:borrowedBook <{book_uri}> .
            ?loan library:borrower ?user .
            ?user library:name ?user_name .
            ?loan library:loanDate ?loan_date .
            ?loan library:returnDate ?return_date .
        }}
        ORDER BY DESC(?loan_date)
        """
        
        results = self.execute_query(query)
        
        processed_loans = []
        for row in results:
            loan_date = datetime.strptime(row["loan_date"]["value"], '%Y-%m-%d')
            return_date = datetime.strptime(row["return_date"]["value"], '%Y-%m-%d')
            
            processed_loans.append({
                'loan': row["loan"]["value"],
                'user': row["user"]["value"],
                'user_name': row["user_name"]["value"],
                'loan_date': loan_date,
                'return_date': return_date
            })
        
        return processed_loans
    
    def get_active_loan(self, book_id):
        """Get active loan information for a specific book"""
        book_uri = f"http://example.org/library#{book_id}"
        
        query = f"""
        SELECT ?loan ?user ?user_name ?loan_date ?return_date
        WHERE {{
            <{book_uri}> library:activeLoan ?loan .
            ?loan library:borrower ?user .
            ?user library:name ?user_name .
            ?loan library:loanDate ?loan_date .
            ?loan library:returnDate ?return_date .
        }}
        """
        
        results = self.execute_query(query)
        if not results:
            return None
        
        row = results[0]
        loan_date = datetime.strptime(row["loan_date"]["value"], '%Y-%m-%d')
        return_date = datetime.strptime(row["return_date"]["value"], '%Y-%m-%d')
        
        return {
            'loan': row["loan"]["value"],
            'user': row["user"]["value"],
            'user_name': row["user_name"]["value"],
            'loan_date': loan_date,
            'return_date': return_date
        }
    
    def get_loaned_books(self):
        """Get all currently loaned books"""
        query = """
        SELECT ?book ?title ?author_name ?loan ?user_name ?return_date
        WHERE {
            ?book library:activeLoan ?loan .
            ?book library:hasTitle ?title .
            ?loan library:borrower ?user .
            ?user library:name ?user_name .
            ?loan library:returnDate ?return_date .
            
            OPTIONAL { 
                ?book library:hasAuthor ?author .
                ?author library:name ?author_name 
            }
        }
        ORDER BY ?return_date
        """
        
        results = self.execute_query(query)
        
        processed_loans = []
        for row in results:
            return_date = datetime.strptime(row["return_date"]["value"], '%Y-%m-%d')
            
            processed_loans.append({
                'book': row["book"]["value"],
                'title': row["title"]["value"],
                'author_name': row["author_name"]["value"] if "author_name" in row else None,
                'loan': row["loan"]["value"],
                'user_name': row["user_name"]["value"],
                'return_date': return_date
            })
        
        return processed_loans
    
    def get_author_by_id(self, author_id):
        """Get detailed information about a specific author"""
        author_uri = f"http://example.org/library#{author_id}"
        
        query = f"""
        SELECT ?name ?birth_year ?death_year ?bio
        WHERE {{
            <{author_uri}> rdf:type library:Author .
            <{author_uri}> library:name ?name .
            OPTIONAL {{ <{author_uri}> library:birthYear ?birth_year }}
            OPTIONAL {{ <{author_uri}> library:deathYear ?death_year }}
            OPTIONAL {{ <{author_uri}> library:bio ?bio }}
        }}
        """
        results = self.execute_query(query)
        if results:
            formatted_author = {}
            for key, value in results[0].items():
                formatted_author[key] = value["value"]
            return type('obj', (object,), formatted_author)
        return None
    
    def get_author_genres(self, author_id):
        """Get genres used by a specific author with count"""
        author_uri = f"http://example.org/library#{author_id}"
        
        query = f"""
        SELECT ?genre_name (COUNT(?book) as ?count)
        WHERE {{
            ?book rdf:type library:Book .
            ?book library:hasAuthor <{author_uri}> .
            ?book library:hasGenre ?genre .
            ?genre library:name ?genre_name .
        }}
        GROUP BY ?genre_name
        ORDER BY DESC(?count)
        """
        results = self.execute_query(query)
        
        formatted_results = []
        for genre in results:
            formatted_genre = {}
            for key, value in genre.items():
                formatted_genre[key] = value["value"]
            formatted_results.append(type('obj', (object,), formatted_genre))
        
        return formatted_results
    
    def get_user_by_id(self, user_id):
        """Get detailed information about a specific user"""
        user_uri = f"http://example.org/library#{user_id}"
        
        query = f"""
        SELECT ?name ?email
        WHERE {{
            <{user_uri}> rdf:type library:User .
            <{user_uri}> library:name ?name .
            <{user_uri}> library:userEmail ?email .
        }}
        """
        results = self.execute_query(query)
        if results:
            formatted_user = {}
            for key, value in results[0].items():
                formatted_user[key] = value["value"]
            return type('obj', (object,), formatted_user)
        return None
    
    def get_user_loans(self, user_id):
        """Get loan history for a specific user"""
        user_uri = f"http://example.org/library#{user_id}"
        
        query = f"""
        SELECT ?loan ?book ?book_title ?loan_date ?return_date
        WHERE {{
            ?loan rdf:type library:Loan .
            ?loan library:borrower <{user_uri}> .
            ?loan library:borrowedBook ?book .
            ?book library:hasTitle ?book_title .
            ?loan library:loanDate ?loan_date .
            ?loan library:returnDate ?return_date .
        }}
        ORDER BY DESC(?loan_date)
        """
        
        results = self.execute_query(query)
        
        processed_loans = []
        for row in results:
            loan_date = datetime.strptime(row["loan_date"]["value"], '%Y-%m-%d')
            return_date = datetime.strptime(row["return_date"]["value"], '%Y-%m-%d')
            
            processed_loans.append({
                'loan': row["loan"]["value"],
                'book': row["book"]["value"],
                'book_title': row["book_title"]["value"],
                'loan_date': loan_date,
                'return_date': return_date
            })
        
        return processed_loans
    
    def get_user_favorite_genres(self, user_id):
        """Get favorite genres for a specific user based on loan history"""
        user_uri = f"http://example.org/library#{user_id}"
        
        query = f"""
        SELECT ?genre_name (COUNT(?book) as ?count)
        WHERE {{
            ?loan rdf:type library:Loan .
            ?loan library:borrower <{user_uri}> .
            ?loan library:borrowedBook ?book .
            ?book library:hasGenre ?genre .
            ?genre library:name ?genre_name .
        }}
        GROUP BY ?genre_name
        ORDER BY DESC(?count)
        LIMIT 5
        """
        results = self.execute_query(query)
        
        formatted_results = []
        for genre in results:
            formatted_genre = {}
            for key, value in genre.items():
                formatted_genre[key] = value["value"]
            formatted_results.append(type('obj', (object,), formatted_genre))
        
        return formatted_results
    
    def get_user_favorite_authors(self, user_id):
        """Get favorite authors for a specific user based on loan history"""
        user_uri = f"http://example.org/library#{user_id}"
        
        query = f"""
        SELECT ?author_name (COUNT(?book) as ?count)
        WHERE {{
            ?loan rdf:type library:Loan .
            ?loan library:borrower <{user_uri}> .
            ?loan library:borrowedBook ?book .
            ?book library:hasAuthor ?author .
            ?author library:name ?author_name .
        }}
        GROUP BY ?author_name
        ORDER BY DESC(?count)
        LIMIT 5
        """
        results = self.execute_query(query)
        
        formatted_results = []
        for author in results:
            formatted_author = {}
            for key, value in author.items():
                formatted_author[key] = value["value"]
            formatted_results.append(type('obj', (object,), formatted_author))
        
        return formatted_results
    
    def get_related_books(self, book_id, limit=5):
        """Get books related to a specific book (same author or genre)"""
        book_uri = f"http://example.org/library#{book_id}"
        
        query_book_info = f"""
        SELECT ?author ?genre
        WHERE {{
            <{book_uri}> library:hasAuthor ?author .
            OPTIONAL {{ <{book_uri}> library:hasGenre ?genre }}
        }}
        """
        book_info = self.execute_query(query_book_info)
        
        if not book_info:
            return []
        
        author_uri = book_info[0].get("author", {}).get("value")
        genre_uri = book_info[0].get("genre", {}).get("value") if "genre" in book_info[0] else None
        
        if author_uri and genre_uri:
            related_query = f"""
            SELECT DISTINCT ?book ?title ?author_name ?genre_name
            WHERE {{
                ?book rdf:type library:Book .
                ?book library:hasTitle ?title .
                
                # Associação com autor
                ?book library:hasAuthor ?author .
                ?author library:name ?author_name .
                
                # Associação com gênero
                OPTIONAL {{
                    ?book library:hasGenre ?genre .
                    ?genre library:name ?genre_name .
                }}
                
                # Filtro para excluir o livro atual
                FILTER(?book != <{book_uri}>)
                
                # Filtro para incluir apenas livros do mesmo autor ou mesmo gênero
                FILTER(?author = <{author_uri}> || EXISTS {{
                    ?book library:hasGenre <{genre_uri}>
                }})
            }}
            ORDER BY ?title
            LIMIT {limit}
            """
        elif author_uri:
            related_query = f"""
            SELECT DISTINCT ?book ?title ?author_name ?genre_name
            WHERE {{
                ?book rdf:type library:Book .
                ?book library:hasTitle ?title .
                
                # Associação com autor
                ?book library:hasAuthor <{author_uri}> .
                <{author_uri}> library:name ?author_name .
                
                # Associação com gênero (opcional)
                OPTIONAL {{
                    ?book library:hasGenre ?genre .
                    ?genre library:name ?genre_name .
                }}
                
                # Filtro para excluir o livro atual
                FILTER(?book != <{book_uri}>)
            }}
            ORDER BY ?title
            LIMIT {limit}
            """
        elif genre_uri:
            related_query = f"""
            SELECT DISTINCT ?book ?title ?author_name ?genre_name
            WHERE {{
                ?book rdf:type library:Book .
                ?book library:hasTitle ?title .
                
                # Associação com autor
                ?book library:hasAuthor ?author .
                ?author library:name ?author_name .
                
                # Associação com gênero
                ?book library:hasGenre <{genre_uri}> .
                <{genre_uri}> library:name ?genre_name .
                
                # Filtro para excluir o livro atual
                FILTER(?book != <{book_uri}>)
            }}
            ORDER BY ?title
            LIMIT {limit}
            """
        else:
            return []
        
        results = self.execute_query(related_query)
        
        formatted_results = []
        for book in results:
            formatted_book = {}
            for key, value in book.items():
                formatted_book[key] = value["value"]
            formatted_results.append(type('obj', (object,), formatted_book))
        
        return formatted_results