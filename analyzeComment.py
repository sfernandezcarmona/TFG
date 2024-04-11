import re

from pysentimiento import create_analyzer
from py2neo import Graph,Node, Relationship



def add_properties_to_nodes(node,sentiment,sentiment_score_neg,sentiment_score_neu,sentiment_score_pos,graph):
    node['Score_NEU'] = sentiment_score_neu
    node['Score_NEG'] = sentiment_score_neg
    node['Score_POS'] = sentiment_score_pos
    node['Sentiment'] = sentiment
    graph.push(node)


def crear_entidad_grafo(node, entity_name, entity_type,graph):

    query = f'MATCH (entity:Entity {{name: "{entity_name}", type: "{entity_type}"}}) RETURN entity'
    result = graph.run(query).data()
    if len(result) > 0:
        entity_node = result[0]['entity']
        relationship = Relationship(node, "HAS_ENTITY", entity_node)
        graph.create(relationship)
    else:
        entity_node = Node("Entity", name=entity_name, type=entity_type)
        graph.merge(entity_node, 'Entity', ("name","type"))
        relationship = Relationship(node, "HAS_ENTITY", entity_node)
        graph.merge(relationship, "HAS_ENTITY", 'name')





graph = Graph('bolt://localhost:7687', auth=('neo4j', 'etsisi123'))




analyzer = create_analyzer(task="sentiment", lang="es")

ner_analyzer = create_analyzer(task="ner", lang="es")


cypher_query = """
MATCH (p:Post)
WHERE p.content <> "" AND NOT (p)-[:HAS_ENTITY]->(:Entity)
RETURN p, p.content AS commentText
"""
result = graph.run(cypher_query).data()


print("Cantidad: ",len(result))

prog = 0
for record in result:
    try:
        prog = prog + 1
        resultados = ner_analyzer.predict(record["commentText"].split("."))
        if hasattr(resultados, '__iter__'):
            ntokens = 0
            for resultado in resultados:
                ntokens = len(resultado.labels) + ntokens
                entidades = resultado.entities
                for entidad in entidades:
                    entidad_normalized = re.sub(r'[^\w\s]+', '', entidad["text"], flags=re.UNICODE).lower()
                    crear_entidad_grafo(record["p"], entidad_normalized, entidad["type"], graph)
        else:
            entidades = resultados.entities
            ntokens = len(resultados.labels)
            for entidad in entidades:
                entidad_normalized = re.sub(r'[^\w\s]+', '', entidad["text"], flags=re.UNICODE).lower()
                crear_entidad_grafo(record["p"], entidad_normalized, entidad["type"], graph)

        if prog % 500 == 0:
            print("Progreso:",prog/len(result) * 100,"% (",prog,")")
    except:
        pass

cypher_query = """
MATCH (comment:Comment)-[:REPLIED_TO]->()
WHERE comment.Score_NEG is null AND NOT (comment)-[:HAS_ENTITY]->(:Entity)
RETURN comment, comment.body AS commentText
"""
result = graph.run(cypher_query).data()

print("Cantidad: ",len(result))

prog = 0
for record in result:
    prog = prog + 1
    resultados = ner_analyzer.predict(record["commentText"].split("."))
    if hasattr(resultados, '__iter__'):
        ntokens = 0
        for resultado in resultados:
            ntokens = len(resultado.labels) + ntokens
            entidades = resultado.entities
            for entidad in entidades:
                entidad_normalized = re.sub(r'[^\w\s]+', '', entidad["text"], flags=re.UNICODE).lower()
                crear_entidad_grafo(record["comment"], entidad_normalized, entidad["type"], graph)
    else:
        entidades = resultados.entities
        ntokens = len(resultados.labels)
        for entidad in entidades:
            entidad_normalized = re.sub(r'[^\w\s]+', '', entidad["text"], flags=re.UNICODE).lower()
            crear_entidad_grafo(record["comment"], entidad_normalized, entidad["type"], graph)

    if ntokens < 150:
        sentiment_score = analyzer.predict(record["commentText"])
        sentiment_score_neg = sentiment_score.probas["NEG"]
        sentiment_score_neu = sentiment_score.probas["NEU"]
        sentiment_score_pos = sentiment_score.probas["POS"]
        sentiment = sentiment_score.output
        add_properties_to_nodes(record["comment"],sentiment,sentiment_score_neg,sentiment_score_neu,sentiment_score_pos,graph)
    if prog % 500 == 0:
        print("Progreso:",prog/len(result) * 100,"% (",prog,")")