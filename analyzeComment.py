import nltk
from pysentimiento import create_analyzer
from pysentimiento.preprocessing import preprocess_tweet
import spacy
from nltk.probability import FreqDist
from py2neo import Graph,Node, Relationship
from nltk.stem import WordNetLemmatizer
from nltk.stem.snowball import SnowballStemmer
import nltk.data

import string

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

def clean_text(text):
    # Convert text to lowercase
    text = text.lower()
    # Remove punctuation
    special_chars = ''.join([char for char in string.punctuation if char not in [',', '.','?','!']])
    text = text.translate(str.maketrans('', '', special_chars))
    # Remove whitespace and newlines
    text = text.strip()
    return text

def lemmatize_word(word, language):
    if language == "english":
        lemmatizer = WordNetLemmatizer()
        lemmatized_word = lemmatizer.lemmatize(word)
    elif language == "spanish":
        stemmer = SnowballStemmer("spanish")
        lemmatized_word = stemmer.stem(word)
    return lemmatized_word


def add_properties_to_nodes(node,topics,sentiment_score_neg,sentiment_score_neu,sentiment_score_pos,graph):
    # Add Topics property (list of words)
    node['Topics'] = topics  # Replace with your desired list of words

    # Add Score_NEU, Score_NEG, Score_POS properties (numbers with decimals)
    node['Score_NEU'] = sentiment_score_neu  # Replace with your desired value
    node['Score_NEG'] = sentiment_score_neg  # Replace with your desired value
    node['Score_POS'] = sentiment_score_pos  # Replace with your desired value
    graph.push(node)


def create_entity_and_connect(node, entity_name, entity_type,graph):

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


# Initialize spaCy with language models
nlp_en = spacy.load("en_core_web_sm")

nlp_es = spacy.load("es_core_news_sm")

def checkTieneEntity(comment):
    query = f"MATCH (c:Comment)-[:HAS_ENTITY]->(e:Entity) WHERE c.id = '{comment['id']}' RETURN c"
    result = graph.run(query).data()
    return len(result) > 0



def analyze_comment(comment,idioma,analyzer):
    # Clean the text
    doc = nlp_es(comment)

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

graph = Graph('bolt://localhost:7687', auth=('neo4j', 'etsisi123'))


cypher_query = """
MATCH (comment:Comment)-[:REPLIED_TO]->(post:Post)
WHERE NOT EXISTS((comment)-[:HAS_ENTITY]->(:Entity))
RETURN comment, comment.body AS commentText, post.dioma AS idioma, post.id AS id
"""
result = graph.run(cypher_query).data()

analyzer = create_analyzer(task="sentiment", lang="es")


progreso = 0
# Iterate over the comments and analyze each one
for index,record in enumerate(result):
    if index > 4993:
        if not checkTieneEntity(record["comment"]):
            comment_text = clean_text(record["commentText"])

            # Skip empty or None comments
            if comment_text:
                sentiment_score_neg,sentiment_score_neu,sentiment_score_pos, comment_topics,entities = analyze_comment(comment_text,record["idioma"],analyzer)

                for entidad in entities.entities:
                    create_entity_and_connect(record["comment"], entidad["text"], entidad["type"], graph)

                temas = list(comment_topics)

                listaTemas = []
                for tema in temas:
                    listaTemas.append(tema[0])

                add_properties_to_nodes(record["comment"],listaTemas,sentiment_score_neg,sentiment_score_neu,sentiment_score_pos,graph)
                progreso = progreso + 1
        else:
            progreso = progreso + 1

        print(progreso,"/",len(result)," ---> ",progreso/len(result)*100,"%")
    else:
        progreso = progreso + 1