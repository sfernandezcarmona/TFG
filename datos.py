import praw
from langdetect import detect
import time
from neo4jDriver import *

class Reddit:
    listaTerminos = ["Sumar", "PP", "PSOE", "Unidas Podemos", "VOX", "Partido Popular", "Partido Socialista",
                     "Podemos", "Ultraderecha", "Ultraizquierda"]

    reddit = praw.Reddit(
        client_id="4sn_H1XsYXdsaBCu08CbrA",
        client_secret="_ZVU_3dfw9qefABWeqKJ2FKMtfkuIg",
        password="etsisi123",
        username="bp0330UPM",
        user_agent="TFGBP0330",
    )

    def obtenerUsuario(self,usr):
        return self.reddit.redditor(usr)

    def obtenerComentario(self,cmnt):
        return self.reddit.comment(cmnt)

    def obtenerPublicacion(self,pub):
        return self.reddit.submission(pub)


    def obtenerDatosSubreddit(self,subreddit):
        for submission in self.reddit.subreddit(subreddit).hot(limit=10):
            print(submission.title)


    #Devuelve hasta 1000 publicaciones del usuario indicado (limitacion de la API)
    def obtenerPublicacionesUsuario(self,usuario):
        resultado = []
        publicaciones = self.reddit.redditor(usuario).submissions
        for publicacion in publicaciones.controversial(time_filter='all'):
            resultado.append(publicacion)
        return resultado

    def getSubredditsPolitica(self):
        listaResults = []
        for termino in self.listaTerminos:
            results = self.reddit.subreddits.search(termino)
            for result in results:
                if result not in listaResults:
                    try:
                        description = self.reddit.subreddit(result.display_name).description

                        if(description is not None and detect(description)=="es"):
                            listaResults.append(result)
                    except:
                        pass
        for result in listaResults:
            print(result)
        return listaResults



    def getSubmissions(self):

        submissions = []
        subreddits = self.getSubredditsPolitica()

        for subreddit in subreddits:
            count = 0
            for termino in self.listaTerminos:
                try:
                    for submission in subreddit.search(termino,limit=None):
                        if not existeNodoPost(submission.id):
                            count = count + 1
                            submissions.append(submission)
                except:
                    time.sleep(1)
            print("Terminado ---------- " + subreddit.display_name + " (", count,")   TOTAL: ", len(submissions))
        return submissions





            