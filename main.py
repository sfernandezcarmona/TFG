import requests
from datos import Reddit
from neo4jDriver import *
import torch
from transformers import pipeline

import pandas as pd


redditDatos = Reddit()

for post in redditDatos.getSubmissions():
    save_post_to_neo4j(post)

#for post in subreddit_list:
    #print(post[0])
    #save_post_to_neo4j(post[0])




