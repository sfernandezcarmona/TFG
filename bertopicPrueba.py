import nltk
import pickle
from bertopic import BERTopic
from bertopic.representation import KeyBERTInspired
from py2neo import Graph
from hdbscan import HDBSCAN
from umap import UMAP
from sklearn.feature_extraction.text import CountVectorizer
from sentence_transformers import SentenceTransformer
import csv



graph = Graph('bolt://localhost:7687', auth=('neo4j', 'etsisi123'))

cypher_query_comment = """
MATCH (comment:Comment)
RETURN comment.body AS commentText;
"""
resultComment = graph.run(cypher_query_comment).data()
contenido =[]

for record in resultComment:
    contenido.append(record["commentText"])






nltk.download('stopwords')
stopwords = nltk.corpus.stopwords.words('spanish')
vectorizer_model = CountVectorizer(ngram_range=(1,1), stop_words=stopwords.append(nltk.corpus.stopwords.words('english')))


umap_model = UMAP(n_neighbors=15, n_components=10, metric='cosine')

hdbscan_model = HDBSCAN(min_cluster_size=20,min_samples=5, metric='euclidean')

embedding_model = SentenceTransformer('hiiamsid/sentence_similarity_spanish_es')

#embeddings precomputados
with open('embeddings\doc_embedding.pickle', 'rb') as pkl:
    embeddings = pickle.load(pkl)

representation_model = KeyBERTInspired()


topic_model = BERTopic(umap_model=umap_model,
                       hdbscan_model=hdbscan_model,
                       embedding_model = embedding_model,
                       vectorizer_model=vectorizer_model,
                       verbose=True,
                       representation_model=representation_model)

topics, probs = topic_model.fit_transform(contenido,embeddings)

topic_model.get_topic_info()

topic_model.save("MODELO_FINAL", serialization="pytorch", save_ctfidf=True, save_embedding_model='hiiamsid/sentence_similarity_spanish_es')