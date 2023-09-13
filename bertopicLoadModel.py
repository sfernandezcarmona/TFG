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
MATCH (comment:Comment)-[rt:REPLIED_TO]->()-[bt:BELONGS_TO]->(subreddit:Subreddit{name:'SpainPolitics'}) 
RETURN comment.body AS commentText
"""
resultComment = graph.run(cypher_query_comment).data()
resultPost = graph.run(cypher_query_post).data()
contenido =[]

for record in resultComment:
    contenido.append(record["commentText"])



topic_model = BERTopic.load("D:\TFGReddit\modelo")

topic_model.topic_embeddings_

topic_model.visualize_barchart().show()

topic_model.visualize_heatmap().show()

print(topic_model.get_topic_info())
