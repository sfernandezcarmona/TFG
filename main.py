import requests
from datos import Reddit
from neo4jDriver import *
import torch
from transformers import pipeline

import pandas as pd


redditDatos = Reddit()
listaTerminos = ["Sumar","PP","PSOE","Unidas Podemos","VOX","Partido Popular","Partido Socialista","Podemos","Ultraderecha","Ultraizquierda"]
for partido in listaTerminos:
    for post in redditDatos.submissions_pushshift_praw(partido + " españa"):
        save_post_to_neo4j(post.id)

#for post in subreddit_list:
    #print(post[0])
    #save_post_to_neo4j(post[0])




