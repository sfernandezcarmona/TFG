from newspaper import Article
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

url = 'https://notesfrompoland.com/2023/03/03/woman-goes-on-trial-in-poland-for-praising-russias-war-against-ukraine-on-social-media/'

# Create an instance of the Article class and pass in the URL
article = Article(url,language="en")
article.download()
#article.set_html("<p>Creación del registro de organizaciones del voluntariado colaboradoras de la proteccióncivil de la Comunidad Autónoma de Euskadi. En el registro tendrán que inscribirseaquellas organizaciones de voluntarios y voluntarias que cumplan los requisitos previstosen el Decreto 24/2010, ya que la inscripción en el registro es condición necesaria paraque las organizaciones del voluntariado tengan acceso a canales de financiación concargo a los recursos de la Comunidad Autónoma del País Vasco y a las vías departicipación, de fomento, formación y actuación en materia de atención de emergenciasy protección civil en el ámbito territorial de la Comunidad Autónoma del País Vasco. <p>")
article.parse()
article.nlp()
# Get the text of the article
# Print the text of the article
texto = article.text
texto = texto.lower()
sid = SentimentIntensityAnalyzer()
scores = sid.polarity_scores(texto)
print(article.keywords)
print(article.summary)
print(scores)





def procesarURL(link):
    articulo = Article(url)
    articulo.download()
    articulo.parse()
    return articulo.text