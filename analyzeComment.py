import nltk
from pysentimiento import create_analyzer
from nltk.probability import FreqDist
from py2neo import Graph,Node, Relationship

import nltk.data



def scoreCommentLargo(comment,idioma,analyzer):
    tokenizer = nltk.data.load('tokenizers/punkt/spanish.pickle')
    comentarios = tokenizer.tokenize(comment)
    sentiment_score_neg= 0
    sentiment_score_neu = 0
    sentiment_score_pos = 0
    for comentario in comentarios:
        sentiment_score = analyzer.predict(comment)
        sentiment_score_neg = sentiment_score_neg + sentiment_score.probas["NEG"]
        sentiment_score_neu = sentiment_score_neu + sentiment_score.probas["NEU"]
        sentiment_score_pos = sentiment_score_pos + sentiment_score.probas["POS"]

    sentiment_score_neg = sentiment_score_neg/len(comentarios)
    sentiment_score_neu = sentiment_score_neu/len(comentarios)
    sentiment_score_pos = sentiment_score_pos/len(comentarios)


    return sentiment_score_neg,sentiment_score_neu,sentiment_score_pos


def add_properties_to_nodes(node,topics,sentiment_score_neg,sentiment_score_neu,sentiment_score_pos,graph):
    # Add Topics property (list of words)
    node['Topics'] = topics  # Replace with your desired list of words

    # Add Score_NEU, Score_NEG, Score_POS properties (numbers with decimals)
    node['Score_NEU'] = sentiment_score_neu  # Replace with your desired value
    node['Score_NEG'] = sentiment_score_neg  # Replace with your desired value
    node['Score_POS'] = sentiment_score_pos  # Replace with your desired value
    graph.push(node)




def checkTieneEntity(comment):
    query = f"MATCH (c:Comment)-[:HAS_ENTITY]->(e:Entity) WHERE c.id = '{comment['id']}' RETURN c"
    result = graph.run(query).data()
    return len(result) > 0



def analyze_comment(comment,idioma,analyzer):
    # Clean the text
    doc = 1

    cleaned_words = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop]

    # Sentiment Analysis
    analyzerNER = create_analyzer(task="ner", lang="es")

    sentiment_score = analyzer.predict(comment)
    entidades = analyzerNER.predict(comment)
    # Access sentiment scores

    # Topic Extraction
    fdist = FreqDist(cleaned_words)
    topics = fdist.most_common(5)  # Extract the top 5 most common words as topics

    sentiment_score_neg = sentiment_score.probas["NEG"]
    sentiment_score_neu = sentiment_score.probas["NEU"]
    sentiment_score_pos = sentiment_score.probas["POS"]

    for ent in entidades.labels:
        if(ent == None):
            sentiment_score_neg,sentiment_score_neu,sentiment_score_pos = scoreCommentLargo(comment,idioma,analyzer)
            break


    return sentiment_score_neg, sentiment_score_neu, sentiment_score_pos, topics,entidades



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
        for resultado in resultados:
            entidades = resultado.entities
            for entidad in entidades:
                crear_entidad_grafo(record["comment"], entidad["text"], entidad["type"], graph)
    else:
        entidades = resultados.entities
        for entidad in entidades:
            crear_entidad_grafo(record["comment"], entidad["text"], entidad["type"], graph)