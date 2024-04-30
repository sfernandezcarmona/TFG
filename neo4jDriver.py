import praw
from praw.models import MoreComments
from py2neo import Graph, Node, Relationship
import datetime,time

reddit = praw.Reddit(client_id="",
                    client_secret="",
                     password="",
                     username="",
                     user_agent="")

graph = Graph('bolt://localhost:7687', auth=('neo4j', ''))




def save_post_to_neo4j(post):
    try:
        # Recupera el post de reddit a partir de su id
        reddit.comment_sort = "controversial"
        if post.author is not None:
            # Crea el nodo del post
            post_node = crearNodoPost(post)

            # Crea el nodo del subreddit y la relacion con el post
            crearNodoSubreddit(post, post_node)
            post_node = crearNodoPost(post)
            author_node = crearNodoUsuario(post)
            posted_rel = Relationship(author_node, 'POSTED', post_node)
            graph.merge(posted_rel, 'POSTED', 'id')

            # Crea nodos para todos los comentarios de primer nivel del post asi como nodos para los autores de los comentarios
            for comment in post.contenido.list():
                    if isinstance(comment, MoreComments):
                        continue
                    if comment.author is not None:
                        # Crea el nodo autor del comentario
                        user_node = crearNodoUsuario(comment)

                        # Crea el nodo del comentario
                        comment_node = crearNodoComentario(comment)

                        # Crea la relacion entre el nodo del comentario y el nodo de su autor (Usuario)
                        authored_rel = Relationship(user_node, 'AUTHORED', comment_node)
                        graph.merge(authored_rel, 'AUTHORED', 'id')
                        replied_to_rel = Relationship(comment_node, 'REPLIED_TO', post_node)
                        graph.merge(replied_to_rel, 'REPLIED_TO', 'id')
            print("Comentarios DONE")
    except:
        time.sleep(1)

def crearNodoPost(post):
    if not existeNodoPost(post.id):
        post_node = Node('Post', id=post.id, title=post.title,
                         created_utc=datetime.datetime.fromtimestamp(post.created_utc).strftime(
                             '%d-%m-%Y %H:%M:%S'),
                         num_comments=post.num_comments,
                         author=post.author.name if post.author is not None else None, score=post.score,
                         content=post.selftext, url=post.url)
        graph.merge(post_node, 'Post', 'id')
        print("Post " + post.title + " creado!")
        return post_node
    else:
        return obtenerNodoPost(post.id)


def crearNodoComentario(comment):
    if not existeNodoComentario(comment.id):
        comment_node = Node('Comment', id=comment.id, body=comment.body,
                            created_utc=datetime.datetime.fromtimestamp(comment.created_utc).strftime('%d/%m/%Y %H:%M:%S'),
                            score=comment.score, permalink=comment.permalink, gilded=comment.gilded,
                            controversiality=comment.controversiality, distinguished=comment.distinguished)
        graph.merge(comment_node, 'Comment', 'id')
        return comment_node
    else:
        return obtenerNodoComentario(comment.id)


def crearNodoUsuario(comment):
    if not existeNodoUsuario(comment.author.name):
        try:
            user_node = Node('User', name=comment.author.name,
                             created_utc=datetime.datetime.fromtimestamp(comment.author.created_utc).strftime(
                                 '%d/%m/%Y %H:%M:%S'),
                             comment_karma=comment.author.comment_karma, link_karma=comment.author.link_karma,
                             is_mod=comment.author.is_mod, is_employee=comment.author.is_employee, is_suspended=False)
        except Exception:
            user_node = Node('User', name=comment.author.name, created_utc="Undefined",
                             comment_karma=0, link_karma=0,
                             is_mod=False, is_employee=False, is_suspended=True)
        graph.merge(user_node, 'User', 'name')
        print("Usuario " + comment.author.name + " creado!")
        return user_node
    else:
        return obtenerNodoUsuario(comment.author.name)

def crearNodoSubreddit(post, post_node):
    if not existeNodoSubreddit(post.subreddit.display_name):
        subreddit_node = Node('Subreddit', name=post.subreddit.display_name, subscribers=post.subreddit.subscribers,
                              description=post.subreddit.public_description, subreddit_type=post.subreddit.subreddit_type)
        graph.merge(subreddit_node, 'Subreddit', 'name')
    else:
        print("Ya existe el subreddit",post.subreddit.display_name)
        subreddit_node = obtenerNodoSubreddit(post.subreddit.display_name)

    belongs_to_rel = Relationship(post_node, 'BELONGS_TO', subreddit_node)
    graph.merge(belongs_to_rel, 'BELONGS_TO', 'id')

def crearNodoTema(name, values,commentids):
    tema_node = Node('Topic', name=name, values=values)
    graph.merge(tema_node, 'Topic', 'name')

    for commentid in commentids:
        relacionarComentarioTema(name,commentid)



def get_comments():
    query = "MATCH (c:Comment) RETURN c"
    results = graph.run(query)
    return [record['c'] for record in results]

def existeNodoComentario(id):
    query = f"MATCH (n:Comment) WHERE n.id = '{id}' RETURN n"
    result = graph.run(query).data()
    return len(result) > 0

def existeNodoPost(id):
    query = f"MATCH (n:Post) WHERE n.id = '{id}' RETURN n"
    result = graph.run(query).data()
    return len(result) > 0

def existeNodoUsuario(nombre):
    query = f"MATCH (n:User) WHERE n.name = '{nombre}' RETURN n"
    result = graph.run(query).data()
    return len(result) > 0

def existeNodoSubreddit(nombre):
    query = f"MATCH (n:Subreddit) WHERE n.name = '{nombre}' RETURN n"
    result = graph.run(query).data()
    return len(result) > 0

def obtenerNodoComentario(id):
    query = f"MATCH (n:Comment) WHERE n.id = '{id}' RETURN n"
    result = graph.run(query).data()
    comentario = None
    for record in result:
        comentario = record['n']
    return comentario

def relacionarComentarioTema(name,id):
    query = f"MATCH(tema: Topic) WHERE tema.name = '{name}' MATCH(comment: Comment) WHERE comment.id= '{id}' CREATE(tema)<-[: HAS_TOPIC]-(comment)"
    graph.run(query).data()

def obtenerNodoPost(id):
    query = f"MATCH (n:Post) WHERE n.id = '{id}' RETURN n"
    result = graph.run(query).data()
    for record in result:
        post = record['n']
    return post

def obtenerNodoSubreddit(nombre):
    query = f"MATCH (n:Subreddit) WHERE n.name = '{nombre}' RETURN n"
    result = graph.run(query).data()
    for record in result:
        subreddit = record['n']
    return subreddit

def obtenerNodoUsuario(nombre):
    query = f"MATCH (u:User) WHERE u.name = '{nombre}' RETURN u"
    result = graph.run(query).data()
    for record in result:
        usuario = record['u']
    return usuario

def obtenerPonerRelacionPost(idComentario,nodoPost):
    query = f"MATCH (c:Comment)-[:REPLIED_TO]->(p:Post) WHERE c.id = '{idComentario}' RETURN c"
    result = graph.run(query).data()
    if len(result)<1:
        comentario = obtenerNodoComentario(idComentario)
        replied_to_rel = Relationship(comentario, 'REPLIED_TO', nodoPost)
        graph.merge(replied_to_rel, 'REPLIED_TO', 'id')



def incluircomentarios(comment,post_node):
    for reply in comment.replies.list():
        if isinstance(reply, MoreComments):
            continue
        if reply.author is not None:
            user_node = crearNodoUsuario(reply)
            print("Reply: " + reply.author.name + " " + reply.id)
            reply_node = crearNodoComentario(reply)
            padre_node = obtenerNodoComentario(reply.parent_id.split("t1_")[1])
            if padre_node is None:
                if "t3_" in reply.parent_id:
                    padre_node = crearNodoComentario(reddit.comment(reply.parent_id.split("t3_")[1]))
                else:
                    padre_node = crearNodoComentario(reddit.comment(reply.parent_id.split("t1_")[1]))
            obtenerPonerRelacionPost(padre_node["id"], post_node)
            authored_rel = Relationship(user_node, 'AUTHORED', reply_node)
            graph.merge(authored_rel, 'AUTHORED', 'id')
            replied_to_rel = Relationship(reply_node, 'REPLIED_TO', padre_node)
            graph.merge(replied_to_rel, 'REPLIED_TO', 'id')
