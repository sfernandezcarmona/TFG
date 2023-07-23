import praw
import datetime as dt
import requests
from langdetect import detect

class Reddit:
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

    def obtenerPostsMes(self,subreddit_name,ano,mes):
        api = PushshiftAPI(praw=self.reddit)
        desde = int(dt.datetime(ano, mes, 1).timestamp())
        hasta = int(dt.datetime(ano, mes+1, 1).timestamp())
        request = api.search_submissions(subreddit=subreddit_name,before=hasta,after=desde,limit=1000)
        lista = [post for post in request]
        posts = []
        for post in lista:
            praw_submission = self.reddit.submission(id=post['id'])

        return list(api.search_submissions(subreddit=subreddit_name,before=hasta,after=desde))


    #Devuelve hasta 1000 publicaciones del usuario indicado (limitacion de la API)
    def obtenerPublicacionesUsuario(self,usuario):
        resultado = []
        publicaciones = self.reddit.redditor(usuario).submissions
        for publicacion in publicaciones.controversial(time_filter='all'):
            resultado.append(publicacion)
        return resultado

    #Devuelve una lista con los 500 comentarios mas votados de una publicacion (500 por razones de rendimiento)
    def obtenerComentariosPublicacion(self,publicacion):
        resultado = []
        publicacion.comment_sort = "top"
        publicacion.comments.replace_more(limit=500)
        for comentario in publicacion.comments.list():
            resultado.append(comentario)
        return resultado

    def submissions_pushshift_praw(self,palabraClave,limit=1000):

        subreddit = self.reddit.subreddit("Python")

        for post in subreddit.hot(limit=5):
            print(post.title)
            print()

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

    def submissions_pushshift_praw_fecha(self,palabraClave, month, year, limit=1000):
        """
        A simple function that returns a list of PRAW submission objects during a particular period from a defined sub.
        This function serves as a replacement for the now deprecated PRAW `submissions()` method.

        :param subreddit: A subreddit name to fetch submissions from.
        :param start: A Unix time integer. Posts fetched will be AFTER this time. (default: None)
        :param end: A Unix time integer. Posts fetched will be BEFORE this time. (default: None)
        :param limit: There needs to be a defined limit of results (default: 100), or Pushshift will return only 25.
        :param extra_query: A query string is optional. If an extra_query string is not supplied,
                            the function will just grab everything from the defined time period. (default: empty string)

        Submissions are yielded newest first.

        For more information on PRAW, see: https://github.com/praw-dev/praw
        For more information on Pushshift, see: https://github.com/pushshift/api
        """
        matching_praw_submissions = []

        # Default time values if none are defined (credit to u/bboe's PRAW `submissions()` for this section)
        start = str(int(dt.datetime(year, month, 1).timestamp()))
        end = str(int(dt.datetime(year, month+1, 2).timestamp()))

        print(start)
        print(end)

        # Format our search link properly.
        search_link = ('https://api.pushshift.io/reddit/search/submission?is_video=false&over_18=false&q=' + palabraClave +'&after=' + start + '&before=' + end + '&limit=' + str(limit))

        # Get the data from Pushshift as JSON.
        retrieved_data = requests.get(search_link)
        #print(retrieved_data.text)
        returned_submissions = retrieved_data.json()['data']

        # Iterate over the returned submissions to convert them to PRAW submission objects.
        for submission in returned_submissions:
            # Take the ID, fetch the PRAW submission object, and append to our list
            praw_submission = self.submission(id=submission['id'])
            matching_praw_submissions.append(praw_submission)

        # Return all PRAW submissions that were obtained.
        return matching_praw_submissions



            