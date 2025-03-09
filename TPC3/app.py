# Backend & Frontend: app.py (Flask with Jinja templates)
import json
from flask import Flask, render_template, request, session, redirect, url_for
from flask_cors import CORS
from SPARQLWrapper import SPARQLWrapper, JSON
import random
import ssl
import certifi

# Override SSL context globally
ssl._create_default_https_context = ssl._create_unverified_context

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
CORS(app)

def battles():
    sparql = SPARQLWrapper("http://localhost:7200/repositories/HistoriaSemana3")
    sparql.setQuery("""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>
        select ?nome ?data ?localnome ?resultado where {
            ?batalhas rdf:type :Batalha .
            ?batalhas :nome ?nome .
            ?batalhas :data ?data .
            ?batalhas :resultado ?resultado .
            ?batalhas :temLocal ?local .
            ?local :nome ?localnome .
        }          
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    # Write into a file
    with open('batles.json', 'w') as f:
        json.dump(results, f)
    
    questions = []
    
    ## Question 1
    ## A/O {nome de uma batalha} aconteceu em :
    ##
    ## {data 1}
    ## {data 2}
    ## {data 3}
    ## {data 4}
    
    for result in results['results']['bindings']:
        question = {}
        question['question'] = f"A/O {result['nome']['value']} aconteceu em :"
        question['answer'] = result['data']['value']
        question['options'] = [result['data']['value']]
    
        for result in results['results']['bindings']:
            if len(question['options']) == 4:
                break
            if result['data']['value'] not in question['options']:
                question['options'].append(result['data']['value'])
    
        random.shuffle(question['options'])
        questions.append(question)
    
    ## Question 2
    ## A/O {nome de uma batalha} decorreu em :
    ##
    ## {local 1}
    ## {local 2}
    ## {local 3}
    ## {local 4}
    
    for result in results['results']['bindings']:
        question = {}
        question['question'] = f"A/O {result['nome']['value']} decorreu em :"
        question['answer'] = result['localnome']['value']
        question['options'] = [result['localnome']['value']]
        
        for result in results['results']['bindings']:
            if len(question['options']) == 4:
                break
            if result['localnome']['value'] not in question['options']:
                question['options'].append(result['localnome']['value'])
        
        random.shuffle(question['options'])
        questions.append(question)
    
    ## Question 3
    ## Portugal ganhou a/o {nome de uma batalha} ?
    ##
    ## {Sim}
    ## {Não}
    
    for result in results['results']['bindings']:
        question = {}
        question['question'] = f"Portugal ganhou a/o {result['nome']['value']}?:"
        if result['resultado']['value'].lower() == 'derrota' or result['resultado']['value'].lower() == 'derrotado':
            question['answer'] = 'Não'
        else:
            question['answer'] = 'Sim'
        question['options'] = ['Sim', 'Não']
        random.shuffle(question['options'])
        questions.append(question)
    
    return questions

def kings():
    sparql = SPARQLWrapper("http://localhost:7200/repositories/HistoriaSemana3")
    sparql.setQuery("""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>
        select ?nome ?nascimento ?cognome ?datareinado where {
            ?reis rdf:type :Rei .
            ?reis :nome ?nome .
            ?reis :nascimento ?nascimento .
            ?reis :cognomes ?cognome .
            ?reinado :temMonarca ?reis .
            ?reinado :comeco ?datareinado .
        }          
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    # Write into a file
    with open('kings.json', 'w') as f:
        json.dump(results, f)
    
    questions = []
    
    ## Question 1
    ## Quando nasceu {nome de rei}:
    ##
    ## {data 1}
    ## {data 2}
    ## {data 3}
    ## {data 4}
    
    for result in results['results']['bindings']:
        question = {}
        question['question'] = f"Quando nasceu {result['nome']['value']}?"
        question['answer'] = result['nascimento']['value']
        question['options'] = [result['nascimento']['value']]
        
        for result in results['results']['bindings']:
            if len(question['options']) == 4:
                break
            if result['nascimento']['value'] not in question['options']:
                question['options'].append(result['nascimento']['value'])
        
        questions.append(question)
    
    ## Question 2
    ## Que rei tinha o cognome de {cognome do rei}:
    ##
    ## {rei 1}
    ## {rei 2}
    ## {rei 3}
    ## {rei 4}
    
    for result in results['results']['bindings']:
        question = {}
        question['question'] = f"Que rei tinha o cognome de {result['cognome']['value']}?"
        question['answer'] = result['nome']['value']
        question['options'] = [result['nome']['value']]
        
        for result in results['results']['bindings']:
            if len(question['options']) == 4:
                break
            if result['nome']['value'] not in question['options']:
                question['options'].append(result['nome']['value'])
                    
        
        random.shuffle(question['options'])
        questions.append(question)
    
    ## Question 3
    ## {nome de rei} teve um reinado que comecou a {data random}:
    ##
    ## {Sim}
    ## {Não}
    
    for result in results['results']['bindings']:
        question = {}
        
        ## find a random date
        dates = []
        for result1 in results['results']['bindings']:
            dates.append(result1['datareinado']['value'])
            
        randomdate = random.choice(dates)    
        
        question['question'] = f"{result['nome']['value']} teve um reinado que comecou a {randomdate}:"
        if result['datareinado']['value'] != randomdate:
            question['answer'] = 'Não'
        else:
            question['answer'] = 'Sim'
        question['options'] = ['Sim', 'Não']
        random.shuffle(question['options'])
        questions.append(question)
    
    return questions

# Function to fetch questions from db
def fetch_questions():
    results1 = battles()
    results1_last = random.sample(results1, 3)
    results2 = kings()
    results2_last = random.sample(results2, 3)
    
    questions = results1_last + results2_last
    return questions

@app.route('/')
def home():
    session['score'] = 0
    session['questions'] = fetch_questions()
    return redirect(url_for('quiz'))

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if request.method == 'POST':
        user_answer = request.form.get('answer')
        question_text = request.form.get('question')
        
        for question in session.get('questions', []):
            if question['question'] == question_text:
                correct = question['answer'] == user_answer
                session['score'] = session.get('score', 0) + (1 if correct else 0)
                session['questions'] = [q for q in session['questions'] if q['question'] != question_text]
                session.modified = True
                return render_template('result.html', correct=correct, correct_answer=question['answer'], score=session['score'])
    
    if session.get('questions'):
        question = session['questions'][0]
        return render_template('quiz.html', question=question)
    else:
        return redirect(url_for('score'))

@app.route('/score')
def score():
    return render_template('score.html', score=session.get('score', 0))

if __name__ == '__main__':
    app.run(debug=True)
