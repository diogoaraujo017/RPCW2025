import json

# Ttl file prefix
ttl = """@prefix : <http://www.semanticweb.org/codemaster/ontologies/2025/1/untitled-ontology-5/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@base <http://www.semanticweb.org/codemaster/ontologies/2025/1/untitled-ontology-5/> .

<http://rpcw.di.uminho.pt/2025/emd> rdf:type owl:Ontology .

#################################################################
#    Object Properties
#################################################################

###  http://rpcw.di.uminho.pt/2025/emd#atleta
:atleta rdf:type owl:ObjectProperty ;
        rdfs:domain :Exame .


###  http://rpcw.di.uminho.pt/2025/emd#pratica
:pratica rdf:type owl:ObjectProperty ;
         rdfs:domain :Pessoa .


###  http://rpcw.di.uminho.pt/2025/emd#representa
:representa rdf:type owl:ObjectProperty ;
            rdfs:domain :Pessoa .


###  http://rpcw.di.uminho.pt/2025/emd#temModalidade
:temModalidade rdf:type owl:ObjectProperty ;
               rdfs:domain :Clube .


#################################################################
#    Data properties
#################################################################

###  http://rpcw.di.uminho.pt/2025/emd#data
:data rdf:type owl:DatatypeProperty ;
      rdfs:domain :Exame ;
      rdfs:range xsd:string .


###  http://rpcw.di.uminho.pt/2025/emd#email
:email rdf:type owl:DatatypeProperty ;
       rdfs:domain :Pessoa ;
       rdfs:range xsd:string .


###  http://rpcw.di.uminho.pt/2025/emd#federado
:federado rdf:type owl:DatatypeProperty ;
          rdfs:domain :Pessoa ;
          rdfs:range xsd:boolean .


###  http://rpcw.di.uminho.pt/2025/emd#genero
:genero rdf:type owl:DatatypeProperty ;
        rdfs:domain :Pessoa ;
        rdfs:range xsd:string .


###  http://rpcw.di.uminho.pt/2025/emd#idade
:idade rdf:type owl:DatatypeProperty ;
       rdfs:domain :Pessoa ;
       rdfs:range xsd:int .


###  http://rpcw.di.uminho.pt/2025/emd#morada
:morada rdf:type owl:DatatypeProperty ;
        rdfs:domain :Pessoa ;
        rdfs:range xsd:string .


###  http://rpcw.di.uminho.pt/2025/emd#num_jogadores
:num_jogadores rdf:type owl:DatatypeProperty ;
               rdfs:domain :Clube ;
               rdfs:range xsd:int .


###  http://rpcw.di.uminho.pt/2025/emd#num_praticantes
:num_praticantes rdf:type owl:DatatypeProperty ;
                 rdfs:domain :Modalidade ;
                 rdfs:range xsd:int .


###  http://rpcw.di.uminho.pt/2025/emd#primeiro_nome
:primeiro_nome rdf:type owl:DatatypeProperty ;
               rdfs:domain [ rdf:type owl:Class ;
                             owl:unionOf ( :Pessoa
                                           :Clube
                                           :Modalidade
                                         )
                           ] ;
               rdfs:range xsd:string .


###  http://rpcw.di.uminho.pt/2025/emd#resultado
:resultado rdf:type owl:DatatypeProperty ;
           rdfs:domain :Exame ;
           rdfs:range xsd:boolean .


###  http://rpcw.di.uminho.pt/2025/emd#ultimo_nome
:ultimo_nome rdf:type owl:DatatypeProperty ;
             rdfs:domain [ rdf:type owl:Class ;
                           owl:unionOf ( :Pessoa
                                         :Clube
                                         :Modalidade
                                       )
                         ] ;
             rdfs:range xsd:string .


#################################################################
#    Classes
#################################################################

###  http://rpcw.di.uminho.pt/2025/emd#Pessoa
:Pessoa rdf:type owl:Class .


###  http://rpcw.di.uminho.pt/2025/emd#Clube
:Clube rdf:type owl:Class .


###  http://rpcw.di.uminho.pt/2025/emd#Exame
:Exame rdf:type owl:Class .


###  http://rpcw.di.uminho.pt/2025/emd#Modalidade
:Modalidade rdf:type owl:Class .

#################################################################
#    Individuals
#################################################################

"""

## Read the file
with open('REPO_TPC/RPCW2025/TPC1/emd.json', encoding='utf-8') as f:
    data = json.load(f)
  
## Data example  
# {
#       "_id": "60b3ee0ee00725274024d5a2",
#       "index": 0,
#       "dataEMD": "2020-07-27",
#       "nome": {
#         "primeiro": "Emily",
#         "último": "Terrell"
#       },
#       "idade": 28,
#       "género": "F",
#       "morada": "Clay",
#       "modalidade": "Futebol",
#       "clube": "GDGoma",
#       "email": "emily.terrell@gdgoma.org",
#       "federado": false,
#       "resultado": true
#     }    

## Instantiate the variables
exams = {}
athletes = {}
sports = {}
clubs = {}

athlete_id_fix = 0
for exam in data:
    
    # Get the exam data
    exam_id = exam['_id']
    exam_date = exam['dataEMD']
    exam_result = exam['resultado']
    
    # Get the athlete data
    athlete_first_name = exam['nome']['primeiro']
    athlete_last_name = exam['nome'].get('último')
    athlete_age = exam['idade']
    athlete_gender = exam.get('género')
    athlete_address = exam['morada']
    athlete_email = exam['email']
    athlete_federated = exam['federado']
    athlete_sport = exam['modalidade']
    athlete_club = exam['clube'].replace(' ', '_')
    
    # Add exam to the exams dictionary
    exams[exam_id] = {'date': exam_date, 'result': exam_result, 'athlete': athlete_id_fix}
    
    # Add athlete to the athletes dictionary
    athletes[athlete_id_fix] = {'first_name': athlete_first_name,
                            'last_name': athlete_last_name,
                            'age': athlete_age,
                            'gender': athlete_gender,
                            'address': athlete_address,
                            'email': athlete_email,
                            'federated': athlete_federated,
                            'sport': athlete_sport,
                            'club': athlete_club}
    athlete_id_fix += 1
    
    # Add the sport to the sports set
    if athlete_sport not in sports.keys():
        sports[athlete_sport] = {'name': athlete_sport}
     
    # Add the club to the clubs set   
    if athlete_club not in clubs.keys():
        clubs[athlete_club] = {'name': athlete_club, 'sports': []}
        
    # Add the sport to the club
    if athlete_sport not in clubs[athlete_club]['sports']:
        clubs[athlete_club]['sports'].append(athlete_sport)

  
## Add the data to the ttl file

# Add the Athletes
for athlete_id, athlete in athletes.items():
    id_sport = None
    for sport_id, sport in sports.items():
        if sport['name'] == athlete['sport']:
            id_sport = sport_id
            break
        
    id_club = None
    for club_id, club in clubs.items():
        if club['name'] == athlete['club']:
            id_club = club_id
            break
    
    ttl += f"""###  http://rpcw.di.uminho.pt/2025/emd#Pessoa{athlete_id}
:Pessoa{athlete_id} rdf:type owl:NamedIndividual ,
                            :Pessoa ;
                 :primeiro_nome "{athlete['first_name']}" ;
                 :ultimo_nome "{athlete['last_name']}" ;
                 :idade {athlete['age']} ;
                 :genero "{athlete['gender']}" ;
                 :morada "{athlete['address']}" ;
                 :email "{athlete['email']}" ;
                 :federado "{athlete['federated']}"^^xsd:boolean ;
                 :pratica :Modalidade{id_sport} ;
                 :representa :Clube{id_club} . 
                 
                 
                 
"""

# Add the Exams
for exam_id, exam in exams.items():
    ttl += f"""###  http://rpcw.di.uminho.pt/2025/emd#Exame{exam_id}
:Exame{exam_id} rdf:type owl:NamedIndividual ,
                          :Exame ;
               :data "{exam['date']}" ;
               :resultado "{exam['result']}"^^xsd:boolean ;
               :atleta :Pessoa{exam['athlete']} .
               
               
               
"""

# Add the Sports
for sport_id, sport_name in sports.items():
    # Calculate how many athletes practice the sport
    athletes_practicing = len([athlete for athlete in athletes.values() if athlete['sport'] == sport_name['name']])

    ttl += f"""###  http://rpcw.di.uminho.pt/2025/emd#Modalidade{sport_id}
:Modalidade{sport_id} rdf:type owl:NamedIndividual ,
                              :Modalidade ;
                   :nome "{sport_name}" ;
                   :num_praticantes {athletes_practicing} .
                   
                   
                   
"""
                    
# Add the Clubs
for club_id, club in clubs.items():
    # Calculate how many athletes represent the club
    athletes_representing = len([athlete for athlete in athletes.values() if athlete['club'] == club['name']])
    
    ttl += f"""###  http://rpcw.di.uminho.pt/2025/emd#Clube{club_id}
:Clube{club_id} rdf:type owl:NamedIndividual ,
                          :Clube ;
               :temNome "{club['name']}" ;
"""
    # Add the sports practiced in the club
    for sport in club['sports']:
        # Find the sport id
        id = None 
        for sport_id, sport_data in sports.items():
            if sport_data['name'] == sport:
                id = sport_id
                break
        
        ttl += f"""               :temModalidade :Modalidade{sport_id} ;
""" 

    ttl += f"""               :num_jogadores {athletes_representing} .



"""               

# Write the ttl file
with open('REPO_TPC/RPCW2025/TPC1/emd_finalized.ttl', 'w') as f:
    f.write(ttl)        
    
    
    