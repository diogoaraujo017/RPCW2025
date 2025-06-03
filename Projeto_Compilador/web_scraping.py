"""Module for scapping the web and obtaining info on the entities."""
import re
import time
import tqdm
import requests
from rdflib import Graph, Literal, Namespace, URIRef, RDF, OWL, XSD

g = Graph()
g.parse("library_ontology.ttl")
library = Namespace("http://example.org/library#")

SUBJECTS = {
    # "Music": "music",
    # "Fantasy": "fantasy",
    # "Horror": "horror",
    # "Literature": "literature",
    "Mystery and detective stories": "mystery_and_detective_stories",
    # "Poetry": "poetry",
    # "Romance": "romance",
    # "Thriller": "thriller",
    "Programming": "programming",
    "Science Fiction": "science_fiction",
    # "Young Adult": "young_adult_fiction",
    # "Baby books": "infancy",
    "Bedtime books": "bedtime",
    # "Ancient Civilization": "ancient_civilization",
    # "Religion": "religion",
}

books_set = set()
authors_set = set()
publishers_set = set()
genres_set = set()
triplos_para_adicionar = []

def safe_uri(s):
    """Transforma a string numa string válida para URI."""
    safe_name = re.sub(r"[ \. \-/,'&]","_",s.strip())
    return URIRef(library[safe_name])

def add_triplo(subject, predicate, obj):
    """Adiciona um triplo à lista para processamento posterior."""
    triplos_para_adicionar.append((subject, predicate, obj))

def get_author_info(author_key):
    """Extrair informações sobre um autor dado o seu id."""
    # author_key tem a "/" antes já
    author_url = f"https://openlibrary.org{author_key}.json"
    try:
        response = requests.get(author_url)
        if response.status_code != 200:
            return "N/A", 0, 0, "N/A"

        data = response.json()
        author_name = data.get("personal_name","N/A")
        if author_name == "N/A":
            author_name = data.get("name","N/A")
        author_birth_date = data.get("birth_date","N/A")
        if author_birth_date != "N/A":
            match = re.search(r"\d{4}", author_birth_date)
            if isinstance(match, re.Match):
                author_birth_year = match.group(0)
            else:
                author_birth_year = 0
        else:
            author_birth_year = 0
        author_death_date = data.get("death_date","N/A")
        if author_death_date != "N/A":
            match = re.search(r"\d{4}", author_death_date)
            if isinstance(match, re.Match):
                author_death_year = match.group(0)
            else:
                author_death_year = 0
        else:
            author_death_year = 0
        author_bio = data.get("bio","N/A")
        if isinstance(author_bio, dict):
            author_bio = author_bio["value"]
        return author_name, author_birth_year, author_death_year, author_bio
    except Exception as e:
        print(f"Erro ao obter edições para {author_key}: {e}")
        return "N/A", 0, 0, "N/A"

def add_author_info():
    """Inserir informações sobre todos os autores."""
    for author_url in tqdm.tqdm(authors_set,desc="authors:"):
        name,by,dy,bio = get_author_info(author_url)
        author_id = author_url.split("/")[-1]
        author_uri = safe_uri(f"author_{author_id}")
        add_triplo(author_uri,library.name,Literal(name,datatype=XSD.string))
        add_triplo(author_uri,library.birthYear,Literal(by,datatype=XSD.integer))
        if dy != 0:
            add_triplo(author_uri,library.deathYear,Literal(dy,datatype=XSD.integer))
        add_triplo(author_uri,library.bio,Literal(bio,datatype=XSD.string))

def get_publishers_and_isbns_for_work(work_key):
    """A cada work ir buscar informações adicionais sobre o livro."""
    # work key tem a "/" antes já
    editions_url = f"https://openlibrary.org{work_key}/editions.json?limit=5"
    try:
        response = requests.get(editions_url)
        if response.status_code != 200:
            return "N/A", "N/A", "N/A"

        data = response.json()
        entries = data.get('entries', [])
        if not entries:
            return "N/A", "N/A", "N/A"

        edition = entries[0]
        for entry in entries:
            if 'isbn_13' in entry.keys() or 'isbn_10' in entry.keys():
                edition = entry
        number_of_pages = edition.get('number_of_pages',0)
        publishers = edition.get('publishers', [])
        publisher = publishers[0] if len(publishers) >= 1 else "N/A"
        isbn = edition.get('isbn_13', "N/A")
        if isbn == "N/A":
            isbn = edition.get('isbn_10', "N/A")
        return publisher, isbn[0], number_of_pages # se [0] der problemas fazer verificação antes
    except Exception as e:
        print(f"Erro ao obter edições para {work_key}: {e}")
        return "N/A", "N/A", "N/A"

def fetch_books(n,url_name,name):
    """Fetch the books of a given genre (subjects)."""
    genres_set.add((url_name,name))

    url = f"https://openlibrary.org/subjects/{url_name}.json?limit={n}&offset=0"
    response = requests.get(url)
    data = response.json()

    works = data.get("works", [])
    if not works:
        print("not docs")
        return

    for work in tqdm.tqdm(works,desc="works:",leave=False):
        work_key = work.get("key")
        book_title = work.get("title","N/A")
        book_uri = safe_uri(f"book_{work_key.split('/')[-1]}")
        publisher, isbn, number_of_pages = get_publishers_and_isbns_for_work(work_key)
        if isbn == "N":
            continue  # Ignore books with no ISBN value
        books_set.add(work_key)
        publishers_set.add(publisher)
        book_authors = work.get("authors",[])
        book_year = work.get("first_publish_year")

        if len(book_authors) > 0:
            author_dict = book_authors[0]
            author_uri = author_dict["key"].strip()
            authors_set.add(author_uri)
            author_id = author_uri.split("/")[-1]
            add_triplo(book_uri, library.hasAuthor, safe_uri(f"author_{author_id}"))
        add_triplo(book_uri, library.publicationYear, Literal(int(book_year),datatype=XSD.integer))
        add_triplo(book_uri, library.hasTitle, Literal(book_title,datatype=XSD.string))
        add_triplo(book_uri, library.hasPublisher, safe_uri(f"publisher_{publisher}"))
        add_triplo(book_uri, library.hasISBN, Literal(isbn,datatype=XSD.string))
        add_triplo(book_uri, library.hasGenre, safe_uri(f"genre_{url_name}"))
        add_triplo(
            book_uri,
            library.numberOfPages,
            Literal(number_of_pages,datatype=XSD.string)
        )

def create_all_entities():
    """Cria todas as entidades mencionadas com pelo menos o nome."""
    # Criar conceitos
    # books_set = set()
    # authors_set = set()
    # publisher_set = set()
    # genres_set = set()
    for book in books_set:
        uri_book = safe_uri(f"book_{book.split('/')[-1]}")
        g.add((uri_book, RDF.type, library.Book))
        g.add((uri_book, RDF.type, OWL.NamedIndividual))
    for author in authors_set:
        author = author.split("/")[-1]
        uri_author = safe_uri(f"author_{author}")
        g.add((uri_author, RDF.type, library.Author))
        g.add((uri_author, RDF.type, OWL.NamedIndividual))
    add_author_info()
    for publisher in publishers_set:
        uri_publisher = safe_uri(f"publisher_{publisher}")
        g.add((uri_publisher, RDF.type, library.Publisher))
        g.add((uri_publisher, RDF.type, OWL.NamedIndividual))
        g.add((uri_publisher, library.name, Literal(publisher, datatype=XSD.string)))
    for (genre,genre_name) in genres_set:
        uri_genre = safe_uri(f"genre_{genre}")
        g.add((uri_genre, RDF.type, library.Genre))
        g.add((uri_genre, RDF.type, OWL.NamedIndividual))
        g.add((uri_genre, library.name, Literal(genre_name, datatype=XSD.string)))

def add_all_triplos():
    """Adiciona todos os triplos coletados ao grafo."""
    for triplo in triplos_para_adicionar:
        g.add(triplo)

def print_graph():
    """Print new ontology to the stdout."""
    print(g.serialize(format='turtle'))

def save_graph():
    """Save the populated ontology to a file."""
    g.serialize(destination="library_populated.ttl", format="turtle")

def main():
    """Função principal responsável por delegar funções."""
    # Exemplo de uso:
    for url_name,url in tqdm.tqdm(SUBJECTS.items(),desc="subjects"):
        fetch_books(30,url,url_name) # TODO: Change number of book per genre
        time.sleep(1)  # Não matar completamente o servidor, seria porco da nossa parte
    print(f"Total de livros coletados: {len(books_set)}")
    create_all_entities()
    add_all_triplos()
    # print_graph()
    save_graph()

if __name__ == "__main__":
    main()
