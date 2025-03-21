import json

import requests

def execute_query(endpoint, query):
    
    headers = {
        'Accept': 'application/sparql-results+json'
    }
    
    response = requests.get(endpoint, params={'query': query}, headers=headers)
    
    if response.status_code not in range(200, 300):
        print('Failed to execute query')
        return None
    
    return response.json()

query = """
select distinct ?movie ?title ?country ?realese ?director ?sinapsis where {
     ?movie a dbo:Film .
     ?movie rdfs:label ?title . 
     ?movie dbp:country ?country .
     ?movie dbo:releaseDate ?realese .
     ?movie dbo:abstract ?sinapsis .
     ?movie dbo:director ?diretorAux .
     ?movie dbo:starring ?cast .
     ?movie dbo:genre ?genre .
     ?diretorAux rdfs:label ?director .
     

     FILTER(LANG(?title) = 'en') .
     FILTER(LANG(?director) = 'en')
     FILTER(LANG(?country) = 'en')
     FILTER(LANG(?sinapsis) = 'en')
}
"""

endpoint = 'http://dbpedia.org/sparql'

response = execute_query(endpoint, query)
movies = response['results']['bindings']

info = []
for movie in movies:
    
    # Get the movie info
    id = movie['movie']['value']
    title = movie['title']['value']
    country = movie['country']['value']
    release = movie['realese']['value']
    director = movie['director']['value']
    sinapsis = movie['sinapsis']['value']
    
    # Get the movie cast informations
    cast = []
    
    query_cast = f"""
    select distinct ?name ?birthdate ?birthplace where {{
        <{id}> dbo:starring ?castAux .
        ?castAux rdfs:label ?name .
        ?castAux dbo:birthDate ?birthdate .
        ?castAux dbo:birthPlace ?birthplaceAux .
        ?birthplaceAux rdfs:label ?birthplace .
        
        FILTER(LANG(?name) = 'en')
        FILTER(LANG(?birthplace) = 'en')
    }}
    """
    response_cast = execute_query(endpoint, query_cast)
    
    for person in response_cast['results']['bindings']:
        #print(person)
        cast.append({
            'name': person['name']['value'],
            'birthdate': person['birthdate']['value'],
            'birthplace': person['birthplace']['value']
        })
    
    # Get the movie genres
    genres = []
    
    query_genres = f"""
    select distinct ?genre where {{
        <{id}> dbo:genre ?genreAux .
        ?genreAux rdfs:label ?genre .
        FILTER(LANG(?genre) = 'en')
    }}
    """
    
    response_genres = execute_query(endpoint, query_genres)
    
    for genre in response_genres['results']['bindings']:
        genres.append(genre['genre']['value'])
        
    info.append({
        'id': id,
        'title': title,
        'country': country,
        'release': release,
        'director': director,
        'cast': cast,
        'genres': genres,
        'sinapsis': sinapsis
    })

# Output the information in a JSON file
with open('REPO_TPC/RPCW2025/TPC4/movies.json', 'w') as file:
    #print pretty json
    file.write(json.dumps(info, indent=4))