from bertopic import BERTopic
from bertopic.representation import KeyBERTInspired
from py2neo import Graph

topic_model = BERTopic.load("D:\TFGReddit\modelo")

topic_model.visualize_barchart().show()

topic_model.visualize_heatmap().show()

print(topic_model.get_topic_info())
