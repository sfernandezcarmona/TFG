import praw
import datetime as dt
import requests
from pmaw import PushshiftAPI
from langdetect import detect
import time

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
                        count = count + 1
                        submissions.append(submission)
                except:
                    time.sleep(1)
            print("Terminado ---------- " + subreddit.display_name + " (", count,")   TOTAL: ", len(submissions))
        return submissions


    def submissions_pushshift_praw(self,palabraClave,limit=1000):

        self.getSubredditsPolitica()

        matching_praw_submissions = []

        # Format our search link properly.
        search_link = ('https://api.pushshift.io/reddit/search/submission?is_video=false&over_18=false&q=' + palabraClave +'&sort_type=num_comments'+ '&limit=' + str(limit))

        # Get the data from Pushshift as JSON.
        retrieved_data = requests.get(search_link)
        print(retrieved_data)
        returned_submissions = retrieved_data.json()['data']

        # Iterate over the returned submissions to convert them to PRAW submission objects.
        for submission in returned_submissions:
            # Take the ID, fetch the PRAW submission object, and append to our list
            praw_submission = self.reddit.submission(id=submission['id'])
            try:
                print(submission['id'])
                titulo = praw_submission.title
                if detect(titulo) == "es" or detect(titulo) == "en":
                    print(titulo)
                    matching_praw_submissions.append(praw_submission)
            except:
                pass

        # Return all PRAW submissions that were obtained.
        return matching_praw_submissions





            