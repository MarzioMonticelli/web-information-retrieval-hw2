import dataretrieving as dr
import networkx as nx

movie_graph = dr.extract_graph()
category_movies = dr.extract_categories()
user_movie_ratings = dr.extract_users_movie_rating()

reduced_graph_size = 200
reduced_graph = nx.Graph()
reduced_category_movie = {}
reduced_user_movie_ratings = {}

reduced_graph_file = "../datasets/reduced_datasets/reduced_movie_graph.txt"
reduced_category_movie_file = "../datasets/reduced_datasets/reduced_category_movies.txt"
reduced_user_movie_ratings_file = "../datasets/reduced_datasets/reduced_user_movie_rating.txt"

if __name__ == "__main__":
    for node in movie_graph.nodes():
        if node <= reduced_graph_size:
            reduced_graph.add_node(node)

    for source, sink, data in movie_graph.edges(data=True):
        weight = data['weight']
        if source in reduced_graph.nodes() and sink in reduced_graph.nodes():
            reduced_graph.add_edge(source, sink, weight=weight)

    for category in category_movies.keys():
        reduced_category_movie[category] = []
        for movie_id in category_movies[category]:
            if movie_id <= reduced_graph_size:
                reduced_category_movie[category].append(movie_id)

    for user in user_movie_ratings.keys():
        reduced_user_movie_ratings[user] = {}
        for movie_id, rate in user_movie_ratings[user].items():
            if movie_id <= reduced_graph_size:
                reduced_user_movie_ratings[user][movie_id] = rate

    # print to file
    rgfd = open(reduced_graph_file, 'w')
    rcmfd = open(reduced_category_movie_file, 'w')
    rumrfd = open(reduced_user_movie_ratings_file, 'w')

    for source, sink, data in reduced_graph.edges(data=True):
        weight = data['weight']
        line = str(source) + "\t" + str(sink) + "\t" + str(weight) + "\n"
        rgfd.write(line)

    rgfd.close()

    for category in reduced_category_movie.keys():
        line = str(category)
        for movie_id in reduced_category_movie[category]:
            line += "\t" + str(movie_id)
        line += "\n"
        rcmfd.write(line)

    rcmfd.close()

    for user_id in reduced_user_movie_ratings.keys():
        for movie_id, rate in reduced_user_movie_ratings[user_id].items():
            line = str(user_id) + "\t" + str(movie_id) + "\t" + str(rate) + "\n"
            rumrfd.write(line)

    rumrfd.close()
