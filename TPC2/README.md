---
Título: TPC2
Data: 21/02/2025
Autor: Diogo Pinto Araújo
Id: pg55935
UC: RPCW
---

# TPC2: Queries SPARQL

### Quantos triplos existem na Ontologia?

```sparql
select (count (*) as ?count) {
    ?a ?p ?s .
}
```

### Que classes estão definidas?

```sparql
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>

select ?classe where {
    ?classe rdf:type owl:Class
} 
```

### Que propriedades tem a classe "Rei"?

```sparql
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>

select distinct ?prop where {
    ?s rdf:type :Rei .
    ?s ?prop ?o .
}
order by ?prop 
```

### Quantos reis aparecem na ontologia?

```sparql
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>

select (count(distinct ?reis) as ?count) {
    ?reis rdf:type :Rei .
} 
```

### Calcula uma tabela com o seu nome, data de nascimento e cognome.

```sparql
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>

select ?nome ?nascimento ?cognome where {
    ?reis rdf:type :Rei .
    ?reis :nome ?nome .
    ?reis :nascimento ?nascimento .
    ?reis :cognomes ?cognome .
}
order by ?nome
```

### Acrescenta à tabela anterior a dinastia em que cada rei reinou.

```sparql
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>

select ?nome ?nascimento ?cognome ?dinastia where {
    ?reis rdf:type :Rei .
    ?reis :nome ?nome .
    ?reis :nascimento ?nascimento .
    ?reis :cognomes ?cognome .
    ?reinado :temMonarca ?reis .
    ?reinado :dinastia ?dinastia .
}
order by ?nome
```

### Qual a distribuição de reis pelas 4 dinastias?

```sparql
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>

select ?dinastia (count (distinct ?reis) as ?count) where {
    ?reinado :dinastia ?dinastia .
    ?reinado :temMonarca ?reis .
    ?reis rdf:type :Rei .
} 
group by ?dinastia order by ?count
```

### Lista os descobrimentos (sua descrição) por ordem cronológica.

```sparql
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>

select ?Rei ?Data ?Descrição where {
    ?descobrimento rdf:type :Descobrimento .
    ?descobrimento :data ?Data .
    ?descobrimento :notas ?Descrição .
    ?descobrimento :temReinado ?reinado .
    ?reinado :temMonarca ?rei .
    ?rei rdf:type :Rei .
    ?rei :nome ?Rei . 
}
order by asc(?Data)
```

### Lista as várias conquistas, nome e data, com o nome do rei que reinava no momento.

```sparql
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>

select ?Conquista ?Data ?Rei where {
    ?conquista rdf:type :Conquista .
    ?conquista :nome ?Conquista .
    ?conquista :data ?Data .
    ?conquista :temReinado ?reinado .
    ?reinado :temMonarca ?rei .
    ?rei rdf:type :Rei .
    ?rei :nome ?Rei . 
}
order by asc(?Data)
```

### Calcula uma tabela com o nome, data de nascimento e número de mandatos de todos os presidentes portugueses.

```sparql
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>

select ?Presidente ?Nascimento (count(distinct ?mandato) as ?Mandatos) where {
    ?presidente rdf:type :Presidente .
    ?presidente :nome ?Presidente . 
    ?presidente :nascimento ?Nascimento .
    ?presidente :mandato ?mandato .
}
group by ?Presidente ?Nascimento order by asc(?Presidente)
```

### Quantos mandatos teve o presidente Sidónio Pais? Em que datas iniciaram e terminaram esses mandatos?

```sparql
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>

select ?Mandato ?Inicio ?Fim ?Descrição where {
    ?presidente rdf:type :Presidente .
    ?presidente :nome "Sidónio Bernardino Cardoso da Silva Pais" .
    ?presidente :mandato ?Mandato .
    ?Mandato :comeco ?Inicio .
    ?Mandato :fim ?Fim .
    ?Mandato :notas ?Descrição .
}
```

### Quais os nomes dos partidos politicos presentes na ontologia?

```sparql
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>

select ?Partido where {
    ?partido rdf:type :Partido .
    ?partido :nome ?Partido .
}
```

### Qual a distribuição dos militantes por cada partido politico?

```sparql
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>

select ?Partido (count (distinct ?militante) as ?Militantes) where {
    ?partido rdf:type :Partido .
    ?partido :nome ?Partido .
    ?partido :temMilitante ?militante .
} group by ?Partido 
```

### Qual o partido com maior número de presidentes militantes?

```sparql
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>

select ?Partido (count (distinct ?militante) as ?Militantes) where {
    ?partido rdf:type :Partido .
    ?partido :nome ?Partido .
    ?partido :temMilitante ?militante .
} group by ?Partido order by desc(?Militantes) limit 1
```
