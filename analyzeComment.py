
from pysentimiento import create_analyzer
from py2neo import Graph,Node, Relationship



def add_properties_to_nodes(node,sentiment,sentiment_score_neg,sentiment_score_neu,sentiment_score_pos,graph):
    # Add Score_NEU, Score_NEG, Score_POS properties (numbers with decimals)
    node['Score_NEU'] = sentiment_score_neu  # Replace with your desired value
    node['Score_NEG'] = sentiment_score_neg  # Replace with your desired value
    node['Score_POS'] = sentiment_score_pos  # Replace with your desired value
    node['Sentiment'] = sentiment
    graph.push(node)


def crear_entidad_grafo(node, entity_name, entity_type,graph):

    # Check if the Entity node already exists
    query = f"MATCH (entity:Entity {{name: '{entity_name}', type: '{entity_type}'}}) RETURN entity"
    result = graph.run(query).data()
    if len(result) > 0:
        # Entity node already exists, connect it to the node
        entity_node = result[0]['entity']
        relationship = Relationship(node, "HAS_ENTITY", entity_node)
        graph.create(relationship)
        print("Conectado al nodo", entity_name, "(", entity_type, ")")
    else:
        # Entity node does not exist, create it and connect it to the character node
        entity_node = Node("Entity", name=entity_name, type=entity_type)
        graph.merge(entity_node, 'Entity', ("name","type"))
        relationship = Relationship(node, "HAS_ENTITY", entity_node)
        graph.merge(relationship, "HAS_ENTITY", 'name')
        print("Nodo",entity_name,"(",entity_type,") creado")





graph = Graph('bolt://localhost:7687', auth=('neo4j', 'etsisi123'))


cypher_query = """
MATCH (comment:Comment)-[:REPLIED_TO]->()
RETURN comment, comment.body AS commentText
LIMIT 100
"""
result = graph.run(cypher_query).data()

analyzer = create_analyzer(task="sentiment", lang="es")

ner_analyzer = create_analyzer(task="ner", lang="es")

for record in result:
    print(record["commentText"])
    resultados = ner_analyzer.predict(record["commentText"].split("."))
    if hasattr(resultados, '__iter__'):
        ntokens = 0
        for resultado in resultados:
            ntokens = len(resultado.labels) + ntokens
            entidades = resultado.entities
            for entidad in entidades:
                crear_entidad_grafo(record["comment"], entidad["text"], entidad["type"], graph)
    else:
        entidades = resultados.entities
        ntokens = len(resultados.labels)
        for entidad in entidades:
            crear_entidad_grafo(record["comment"], entidad["text"], entidad["type"], graph)

    if ntokens < 150:
        sentiment_score = analyzer.predict(record["commentText"])
        sentiment_score_neg = sentiment_score.probas["NEG"]
        sentiment_score_neu = sentiment_score.probas["NEU"]
        sentiment_score_pos = sentiment_score.probas["POS"]
        sentiment = sentiment_score.output
        print(sentiment)
        add_properties_to_nodes(record["comment"],sentiment,sentiment_score_neg,sentiment_score_neu,sentiment_score_pos,graph)