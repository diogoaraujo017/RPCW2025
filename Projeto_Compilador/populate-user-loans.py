import random
from datetime import datetime, timedelta
from rdflib import Graph, Literal, Namespace, URIRef, RDF, XSD, OWL

g = Graph()
g.parse("library_populated.ttl")

library = Namespace("http://example.org/library#")

books = list(g.subjects(RDF.type, library.Book))

existing_users = list(g.subjects(RDF.type, library.User))
existing_loans = list(g.subjects(RDF.type, library.Loan))
books_with_active_loans = list(g.subjects(library.activeLoan, None))

def random_date(start_date, end_date):
    time_between = end_date - start_date
    days_between = time_between.days
    random_days = random.randrange(days_between)
    return start_date + timedelta(days=random_days)

users = existing_users.copy()
new_users_count = 0

user_names = [
    "John Smith", "Emma Johnson", "Michael Brown", "Sarah Davis", 
    "Robert Wilson", "Jennifer Thompson", "David Martinez", "Lisa Anderson",
    "Carlos Rodriguez", "Maria Garcia", "James Wilson", "Patricia Moore",
    "Thomas White", "Jessica Taylor", "Daniel Miller", "Sophia Lewis",
    "Ana Sousa", "José Silva", "António Oliveira", "Mariana Costa",
    "Pedro Santos", "Francisca Pereira", "João Ferreira", "Inês Rodrigues",
    "Miguel Almeida", "Sofia Martins", "Francisco Fernandes", "Beatriz Gomes",
    "Tiago Lopes", "Matilde Marques", "André Ribeiro", "Leonor Cardoso",
    "Diogo Pinto", "Carolina Carvalho", "Tomás Teixeira", "Madalena Moreira",
    "Rodrigo Nunes", "Lara Mendes", "Afonso Vieira", "Catarina Dias",
    "Duarte Araújo", "Alice Correia", "Guilherme Antunes", "Rita Gaspar"
]

if len(existing_users) < len(user_names):
    users_to_add = len(user_names) - len(existing_users)
    
    for i in range(users_to_add):
        user_id = f"user_{len(existing_users) + i + 1}"
        user_uri = URIRef(library[user_id])
        name = user_names[len(existing_users) + i]
        email = f"{name.lower().replace(' ', '.')}@example.com"
        
        g.add((user_uri, RDF.type, library.User))
        g.add((user_uri, RDF.type, OWL.NamedIndividual))
        g.add((user_uri, library.name, Literal(name)))
        g.add((user_uri, library.userEmail, Literal(email)))
        
        users.append(user_uri)
        new_users_count += 1

new_loans_count = 0
today = datetime.now().date()
past_start = today - timedelta(days=365)  
future_end = today + timedelta(days=30)   

total_loans_needed = 60 - len(existing_loans)
if total_loans_needed > 0:
    active_loans_to_add = min(total_loans_needed // 3, len(books) - len(books_with_active_loans))
    historical_loans_to_add = total_loans_needed - active_loans_to_add
    
    if active_loans_to_add > 0:
        available_books = [book for book in books if book not in books_with_active_loans]
        if available_books:
            books_for_active_loans = random.sample(available_books, active_loans_to_add) if len(available_books) > active_loans_to_add else available_books
            
            loan_count = len(existing_loans)
            for i, book in enumerate(books_for_active_loans):
                loan_id = f"loan_{loan_count + i + 1}"
                loan_uri = URIRef(library[loan_id])
                
                user = random.choice(users)
                
                loan_date = random_date(today - timedelta(days=30), today).strftime('%Y-%m-%d')
                return_date = random_date(today, future_end).strftime('%Y-%m-%d')
                
                g.add((book, library.activeLoan, loan_uri))
                
                g.add((loan_uri, RDF.type, library.Loan))
                g.add((loan_uri, RDF.type, OWL.NamedIndividual))
                g.add((loan_uri, library.borrowedBook, book))
                g.add((loan_uri, library.borrower, user))
                g.add((loan_uri, library.loanDate, Literal(loan_date, datatype=XSD.date)))
                g.add((loan_uri, library.returnDate, Literal(return_date, datatype=XSD.date)))
                
                new_loans_count += 1
    
    if historical_loans_to_add > 0:
        books_for_history = random.sample(books, historical_loans_to_add) if len(books) > historical_loans_to_add else books
        
        loan_count = len(existing_loans) + new_loans_count
        for i, book in enumerate(books_for_history):
            loan_id = f"loan_{loan_count + i + 1}"
            loan_uri = URIRef(library[loan_id])
            
            user = random.choice(users)
            
            loan_date = random_date(past_start, today - timedelta(days=10)).strftime('%Y-%m-%d')
            return_date = random_date(datetime.strptime(loan_date, '%Y-%m-%d').date() + timedelta(days=1), today).strftime('%Y-%m-%d')
            
            g.add((loan_uri, RDF.type, library.Loan))
            g.add((loan_uri, RDF.type, OWL.NamedIndividual))
            g.add((loan_uri, library.borrowedBook, book))
            g.add((loan_uri, library.borrower, user))
            g.add((loan_uri, library.loanDate, Literal(loan_date, datatype=XSD.date)))
            g.add((loan_uri, library.returnDate, Literal(return_date, datatype=XSD.date)))
            
            new_loans_count += 1

g.serialize(destination="library_populated_with_users_loans.ttl", format="turtle")

print(f"Resumo:")
print(f"- Total de livros na ontologia: {len(books)}")
print(f"- Usuários existentes encontrados: {len(existing_users)}")
print(f"- Novos usuários adicionados: {new_users_count}")
print(f"- Total de usuários na ontologia: {len(existing_users) + new_users_count}")
print(f"- Empréstimos existentes encontrados: {len(existing_loans)}")
print(f"- Novos empréstimos adicionados: {new_loans_count}")
print(f"- Total de empréstimos na ontologia: {len(existing_loans) + new_loans_count}")
print(f"- Livros com empréstimos ativos: {len(list(g.subjects(library.activeLoan, None)))}")
print(f"Salvo como 'library_populated_with_users_loans.ttl'")