from bertopic import BERTopic
import pandas as pd
import re
from neo4j import GraphDatabase
from neo4jDriver import *

def remove_links(text):

    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    text = re.sub(r'\*\*', '', text)
    text = re.sub(r'\n', '', text)
    text = re.sub(r'\r', '', text)

    return re.sub(url_pattern, '', text)

graph = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'etsisi123'))

cypher_query_comment = """
MATCH (comment:Comment)
RETURN comment AS comment;
"""

with graph.session() as session:
    resultComment = session.run(cypher_query_comment).data()

contenido = []
commentIds = []
timestamps = []


for record in resultComment:
    timestamps.append(record["comment"]["created_utc"])
    commentIds.append(record["comment"]["id"])
    comment_text = record["comment"]["body"]
    comment_text_without_links = remove_links(comment_text)
    contenido.append(comment_text_without_links)

topic_model = BERTopic(verbose=True).load("MODELO_FINAL",embedding_model="hiiamsid/sentence_similarity_spanish_es")


representative_docs = pd.DataFrame({"Document": contenido, "Topic": topic_model.topics_})

doc_info = topic_model.get_document_info( contenido)


docs = contenido

documents = pd.DataFrame({"Document": docs,
                          "ID": range(len(docs)),
                          "Topic": topic_model.topics_})

repr_docs, _, _, _ = topic_model._extract_representative_docs(c_tf_idf=topic_model.c_tf_idf_,
                                                          documents=documents,
nr_samples = 80000,
                                                          topics=topic_model.topic_representations_,)


representativedocs = pd.DataFrame(repr_docs)

"""
#Añadir topics al grafo

df = pd.DataFrame({"Document": contenido,"id":commentIds, "Topic": topic_model.topics_})

for key, value in topic_model.get_topics().items():
        valores = []
        tema = str(key)
        for word in value:
            valores.append(word[0])
        new_dataframe = df[df['Topic'] == key].copy()
        crearNodoTema(tema,valores,new_dataframe['id'].tolist())
        
        
"""


