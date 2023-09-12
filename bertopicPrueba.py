from bertopic import BERTopic
from bertopic.representation import KeyBERTInspired
from py2neo import Graph


graph = Graph('bolt://localhost:7687', auth=('neo4j', 'etsisi123'))

cypher_query_post = """
MATCH (post:Post)
WHERE post.content <> ""
RETURN post.content AS postText;
"""

cypher_query_comment = """
MATCH (comment:Comment)
RETURN comment.body AS commentText;
"""
resultComment = graph.run(cypher_query_comment).data()
resultPost = graph.run(cypher_query_post).data()
contenido =[]

for record in resultComment:
    contenido.append(record["commentText"])

for record in resultPost:
    contenido.append(record["postText"])


representation_model = KeyBERTInspired()
topic_model = BERTopic("multilingual",representation_model=representation_model)
topics, probs = topic_model.fit_transform(contenido)
topic_model.get_topic_info()
embedding_model = "paraphrase-multilingual-MiniLM-L12-v2"
topic_model.save("D:\TFGReddit\modelo", serialization="pytorch", save_ctfidf=True, save_embedding_model=embedding_model)