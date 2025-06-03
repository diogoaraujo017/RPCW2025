# Sistema de Gestão de Ontologia de Biblioteca

## Relatório de Projeto RPCW2025

**Autores:**

- Afonso Silva - PG55920
- Daniel Rodrigues - PG57871
- Diogo Araujo - PG55935

**Junho de 2025**

---

## Correr a aplicação

- Criar repositório no GraphDB com o nome `TrabalhoPratico` e inserir o ficheiro `./library_populated_with_users_loans.ttl`.

- Executar na shell `python3 app.py` e abrir o browser no `http://127.0.0.1:5000/`.

## 1. Introdução

### 1.1 Contexto e Motivação

O Sistema de Gestão de Ontologia de Biblioteca é uma aplicação web desenvolvida para explorar as capacidades das tecnologias da web semântica na gestão de dados bibliotecários. As bases de dados relacionais tradicionais são comuns em sistemas de gestão de bibliotecas, mas carecem da capacidade de expressar relações ricas entre entidades, realizar raciocínio semântico e interligar dados entre diferentes domínios.

Ao representar a informação da biblioteca como uma ontologia utilizando RDF (Resource Description Framework), obtemos várias vantagens:

- Semântica aprimorada através de relações explícitas entre entidades
- Melhoria na integração e interoperabilidade de dados
- Capacidades de consulta mais poderosas
- Esquema flexível que pode evoluir ao longo do tempo

### 1.2 Objetivos

Os principais objetivos deste projeto foram:

1. Projetar uma ontologia abrangente para um domínio de biblioteca que modele livros, autores, editoras, géneros, utilizadores e empréstimos
2. Implementar uma interface web para navegar, pesquisar e visualizar esta ontologia
3. Permitir operações básicas de gestão de biblioteca através da interface
4. Garantir a persistência de dados utilizando o GraphDB como armazenamento semântico de triplos
5. Fornecer visualizações e estatísticas significativas para obter insights a partir dos dados

### 1.3 Tecnologias Utilizadas

O projeto utiliza várias tecnologias:

- **Flask**: Uma framework web leve em Python para construir a aplicação
- **Jinja2**: Motor de templates para renderizar páginas HTML
- **RDFLib**: Biblioteca Python para trabalhar com dados RDF
- **GraphDB**: Armazenamento de triplos para persistir dados RDF
- **SPARQL**: Linguagem de consulta para recuperar e manipular dados RDF
- **Bootstrap 5**: Framework frontend para design de interface responsivo
- **Font Awesome**: Biblioteca de ícones para elementos visuais

## 2. Design da Ontologia

### 2.1 Modelação do Domínio

O domínio da biblioteca foi modelado com as seguintes classes principais:

- **Livro**: Representando obras literárias com propriedades como título, ISBN e ano de publicação
- **Autor**: Criadores de livros com informação biográfica
- **Editora**: Organizações que publicam livros
- **Género**: Categorias ou tipos de livros
- **Utilizador**: Indivíduos que requisitam livros da biblioteca
- **Empréstimo**: Representando o ato de requisitar um livro por um utilizador

Estas classes estão interligadas através de várias propriedades que descrevem as suas relações. Por exemplo, um Livro tem um Autor, pertence a um Género e pode estar associado a um Empréstimo.

### 2.2 Classes e Propriedades

A ontologia consiste nas seguintes classes primárias e as suas propriedades associadas:

**Livro**

- `hasTitle` - Título do livro (string)
- `hasISBN` - Número ISBN (string)
- `publicationYear` - Ano de publicação (inteiro)
- `hasAuthor` - Ligação ao autor (relação)
- `hasPublisher` - Ligação à editora (relação)
- `hasGenre` - Ligação ao género (relação)
- `numberOfPages` - Número de páginas (string)
- `activeLoan` - Empréstimo atualmente ativo (relação)

**Autor**

- `name` - Nome do autor (string)
- `birthYear` - Ano de nascimento (inteiro)
- `deathYear` - Ano de morte (inteiro, opcional)
- `bio` - Informação biográfica (string)

**Editora**

- `name` - Nome da editora (string)

**Género**

- `name` - Nome do género (string)

**Utilizador**

- `name` - Nome do utilizador (string)
- `userEmail` - Endereço de email do utilizador (string)

**Empréstimo**

- `borrowedBook` - Livro a ser emprestado (relação)
- `borrower` - Utilizador que requisita o livro (relação)
- `loanDate` - Data em que o livro foi requisitado (data)
- `returnDate` - Data em que o livro deve ser devolvido (data)

### 2.3 Estrutura RDF

A ontologia é armazenada no formato Turtle (TTL), que fornece uma forma concisa e legível de representar triplos RDF. Eis um excerto de exemplo que mostra a estrutura:

```turtle
@prefix library: <http://example.org/library#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

library:Book a rdfs:Class .
library:Author a rdfs:Class .

library:book_OL103123W a library:Book ;
    library:hasAuthor library:author_OL24137A ;
    library:hasGenre library:genre_science_fiction ;
    library:hasISBN "9781508760863"^^xsd:string ;
    library:hasPublisher library:publisher_CreateSpace_Independent_Publishing_Platform ;
    library:hasTitle "Fahrenheit 451"^^xsd:string ;
    library:numberOfPages "184"^^xsd:string ;
    library:publicationYear 1953 .

library:author_OL24137A a library:Author ;
    library:bio """Ray Bradbury é um daqueles indivíduos raros cuja escrita mudou a forma como as pessoas pensam..."""^^xsd:string ;
    library:birthYear 1920 ;
    library:deathYear 2012 ;
    library:name "Ray Bradbury"^^xsd:string .
```

## 3. Arquitetura da Aplicação

### 3.1 Estrutura da Aplicação Flask

A aplicação segue uma estrutura modular:

- `app.py`: Aplicação Flask principal com rotas e controladores
- `library_queries_graphdb.py`: Interface de consulta SPARQL para o GraphDB
- `populate-user-loans.py`: Script para popular dados de exemplo
- `web_scraping.py`: Script para adquirir dados de fontes web
- Pasta de templates: Templates Jinja2 para renderizar páginas HTML

A aplicação utiliza um padrão Modelo-Vista-Controlador (MVC):

- Modelo: Dados RDF no GraphDB e a classe `LibraryQueries`
- Vista: Templates Jinja2
- Controlador: Rotas Flask em `app.py`

### 3.2 Fluxo de Dados

O fluxo de dados na aplicação segue este padrão:

1. O utilizador interage com a interface web para solicitar informações
2. As rotas Flask tratam o pedido e determinam quais dados são necessários
3. A classe `LibraryQueries` constrói consultas SPARQL apropriadas
4. As consultas são executadas no repositório GraphDB
5. Os resultados são transformados em objetos Python para manipulação mais fácil
6. Os dados são passados para os templates Jinja2 para renderização
7. O HTML renderizado é enviado de volta para o navegador do utilizador

### 3.3 Integração com GraphDB

A integração com o GraphDB é conseguida através da biblioteca SPARQLWrapper, que facilita a comunicação com endpoints SPARQL. A classe `LibraryQueries` encapsula toda a lógica de consulta SPARQL:

```python
class LibraryQueries:
    def __init__(self, endpoint_url="http://localhost:7200/repositories/library"):
        """Inicializa a classe de consulta usando o GraphDB"""
        self.endpoint = endpoint_url
        self.sparql = SPARQLWrapper(endpoint_url)
        self.sparql.setReturnFormat(JSON)

    def execute_query(self, query):
        """Executa uma consulta SPARQL e retorna os resultados"""
        full_query = self.prefixes + query
        self.sparql.setQuery(full_query)
        results = self.sparql.query().convert()
        return results["results"]["bindings"]
```

O sistema conecta-se a um repositório GraphDB em `http://localhost:7200/repositories/TrabalhoPratico` por padrão, que pode ser configurado conforme necessário.

## 4. Detalhes de Implementação

### 4.1 Interface Web

A interface web é construída utilizando o Bootstrap 5 para design responsivo e o Font Awesome para ícones. As páginas principais incluem:

- **Página inicial**: Exibe uma lista paginada de livros com informações básicas
- **Página de autores**: Mostra todos os autores com paginação e pré-visualização dos seus livros
- **Detalhes do livro**: Informação abrangente sobre um livro específico, incluindo histórico de empréstimos
- **Detalhes do autor**: Informação detalhada sobre um autor e as suas obras
- **Perfis de utilizador**: Informação do utilizador e histórico de empréstimos
- **Página de pesquisa**: Funcionalidade de pesquisa avançada com múltiplos filtros
- **Informação da ontologia**: Estatísticas e informações sobre a estrutura da ontologia

Cada página é implementada como um template Jinja2 que estende um template base. Esta abordagem assegura um design consistente e reduz a duplicação de código.

### 4.2 Sistema de Consulta

O sistema de consulta é construído em torno do SPARQL, com a classe `LibraryQueries` fornecendo vários métodos para diferentes tipos de consulta:

- Recuperação básica de entidades (livros, autores, utilizadores)
- Exploração de relações (livros de um autor, livros relacionados)
- Pesquisas complexas com filtragem e ordenação
- Geração de estatísticas

Um exemplo de método de consulta para recuperar detalhes de um livro:

```python
def get_book_by_id(self, book_id):
    """Obter informação detalhada sobre um livro específico"""
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
        # ... padrões OPTIONAL adicionais ...
    }}
    """
    results = self.execute_query(query)
    # Processamento dos resultados...
```

### 4.3 Gestão de Dados

O sistema utiliza duas abordagens para a gestão de dados:

1. **Web scraping**: O módulo `web_scraping.py` adquire dados iniciais da API Open Library, enriquecendo o conjunto de dados com informações reais de livros
2. **Geração de dados de exemplo**: O script `populate-user-loans.py` cria utilizadores e empréstimos de exemplo para demonstrar a funcionalidade do sistema

Os dados são armazenados no formato Turtle, que pode ser carregado no GraphDB ou utilizado diretamente com o RDFLib para persistência baseada em ficheiros.

## 5. Funcionalidades

### 5.1 Navegação e Visualização

O sistema fornece formas intuitivas de navegar e visualizar os dados da biblioteca:

- **Listagens paginadas**: Livros, autores e utilizadores são exibidos em vistas paginadas
- **Páginas de detalhes**: Informação abrangente sobre entidades individuais
- **Visualizações de linha temporal**: Histórico de publicação de um autor e histórico de empréstimos de um utilizador
- **Painéis de estatísticas**: Insights sobre a ontologia e utilização da biblioteca
- **Visualização de relações**: Rede de livros, autores e géneros relacionados

### 5.2 Capacidades de Pesquisa

A funcionalidade de pesquisa é um destaque do sistema:

- **Pesquisa multi-campo**: Pesquisa por título, autor, género, editora ou ISBN
- **Filtragem avançada**: Filtrar por intervalo de anos de publicação
- **Ordenação personalizada**: Ordenar resultados por vários critérios (título, ano, autor)
- **Destaque de resultados**: Destaque visual dos termos de pesquisa nos resultados
- **Indicação de relevância**: Mostra onde foram encontradas correspondências em cada resultado

### 5.3 Gestão de Empréstimos

O sistema rastreia empréstimos de livros com funcionalidades como:

- **Rastreio de empréstimos**: Registo de quando os livros são requisitados e quando devem ser devolvidos
- **Estado atual**: Indica se um livro está disponível ou emprestado
- **Histórico do utilizador**: Histórico completo de requisições para cada utilizador
- **Preferências de leitura**: Análise dos géneros e autores favoritos de um utilizador com base no histórico de requisições
- **Alertas de data de devolução**: Indicadores visuais para datas de devolução próximas

## 6. Desafios e Soluções

### 6.1 Desafios Técnicos

Durante o desenvolvimento deste projeto, foram encontrados vários desafios técnicos:

1. **Complexidade SPARQL**: Elaborar consultas SPARQL eficientes para operações complexas exigiu um planeamento cuidadoso. Abordámos isto criando uma biblioteca de padrões de consulta reutilizáveis e utilizando parametrização.

2. **Aquisição de Dados**: Obter dados realistas suficientes para demonstrar o sistema foi desafiante. Resolvemos isto criando um módulo de web scraping que extrai dados da API Open Library e completando os mesmos com dados fictícios sobre utilizadores e empréstimos.

3. **Otimização de Desempenho**: Grandes conjuntos de resultados de consultas SPARQL poderiam abrandar a aplicação. Implementámos paginação ao nível da consulta em vez de filtrar resultados em Python, o que melhorou significativamente o desempenho.

4. **Tratamento de Datas**: Trabalhar com datas em SPARQL e RDF exigiu atenção cuidadosa à conversão de formatos. Padronizámos a utilização do formato de data ISO e implementámos funções utilitárias para conversão.

## 7. Conclusão e Trabalho Futuro

### 7.1 Resumo de Realizações

O Sistema de Gestão de Ontologia de Biblioteca demonstra com sucesso o poder das tecnologias da web semântica para a gestão de dados bibliotecários. As principais realizações incluem:

- Criação de uma ontologia abrangente de biblioteca
- Desenvolvimento de uma interface web intuitiva para navegação e pesquisa
- Implementação de funcionalidade de pesquisa avançada
- Integração com GraphDB para persistência de dados
- Visualização de relações entre entidades da biblioteca
- Análise de preferências de leitura e padrões de empréstimo de utilizadores

O Sistema de Gestão de Ontologia de Biblioteca demonstra que as tecnologias da web semântica podem fornecer soluções poderosas para domínios com relações ricas e estruturas de dados complexas.

---
