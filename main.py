from datos import Reddit
from neo4jDriver import *


redditDatos = Reddit()

for post in redditDatos.getSubmissions():
    save_post_to_neo4j(post)




