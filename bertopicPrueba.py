from bertopic import BERTopic
from bertopic.representation import KeyBERTInspired
from py2neo import Graph


graph = Graph('bolt://localhost:7687', auth=('neo4j', 'etsisi123'))


cypher_query = """
MATCH (comment:Comment)-[rt:REPLIED_TO]->()-[bt:BELONGS_TO]->(subreddit:Subreddit{name:'podemos'}) RETURN comment, comment.body AS commentText
LIMIT 10000
"""
result = graph.run(cypher_query).data()

comments =[]
prog = 0
print("Comienza lectura de comentarios",len(result))
for record in result:
    comments.append(record["commentText"])
    prog = prog + 1
    print(prog/len(result)*100,"% ------- ",prog,"/",len(result))

representation_model = KeyBERTInspired()
topic_model = BERTopic("spanish",representation_model=representation_model)
topics, probs = topic_model.fit_transform(comments)
topic_model.get_topic_info()