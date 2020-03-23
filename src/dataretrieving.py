import csv
import networkx as nx

movie_graph_file_path = '../datasets/movie_graph.txt'
user_movie_rating_file_path = '../datasets/user_movie_rating.txt'
category_movies_file_path = '../datasets/category_movies.txt'


def extract_categories(file_path=category_movies_file_path):
    """
    Extract the categories from the file
    
    :param str file_path: a path to the file that contains information about nodes <-> categories relation
    :return: a dictionary { category_id: list of nodes in the category }
    :rtype: dict[int, list[int]]
    """

    categories_file = open(file_path, 'r')
    categories_file_csv_reader = csv.reader(categories_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_NONE)
    categories = dict((int(x), list()) for x in xrange(0, 5))
    for row_number, categories_row in enumerate(categories_file_csv_reader):
        for movie_id in categories_row:
            categories[int(row_number)].append(int(movie_id))
    categories_file.close()

    return categories


def extract_graph(file_path=movie_graph_file_path):
    """
    Extract the graph from the file
    
    :param str file_path: a path to the file that stores the representation of the graph   
    :return: the undirected weighted graph
    :rtype: networkx.Graph
    """

    # graph creation
    movie_graph = nx.Graph(name="Movie Graph")

    # load graph
    input_file = open(file_path, 'r')
    input_file_csv_reader = csv.reader(input_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_NONE)
    max_rows = 20
    counter = 0
    for node__adjacency_list in input_file_csv_reader:
        if counter > max_rows:
            break
        # counter += 1
        assert len(node__adjacency_list) == 3
        source = int(node__adjacency_list[0])
        sink = int(node__adjacency_list[1])
        weight = int(node__adjacency_list[2])
        movie_graph.add_edge(source, sink, weight=weight)

    input_file.close()

    return movie_graph


def extract_users_movie_rating(file_path=user_movie_rating_file_path):
    """
    
    :param str file_path: the path to the file that contains the users' ratings to movies  
    :return: a dictionary with key the user id and as value another dictionary with key a movie id and value the user's 
        rating to the movie
    :rtype: dict[int, dict[int, int]]
    """

    # user_id     movie_id        rating
    users_ratings = {}
    input_file = open(file_path, 'r')
    input_file_csv_reader = csv.reader(input_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_NONE)
    for line in input_file_csv_reader:
        user_id = int(line[0])
        movie_id = int(line[1])
        rating = int(line[2])  # int - [0, 5]
        if user_id not in users_ratings:
            users_ratings[user_id] = dict()
        users_ratings[user_id][movie_id] = rating

    return users_ratings


if __name__ == "__main__":
    graph = extract_graph()
    users_movie_ratings = extract_users_movie_rating()
    ratings = 0
    movies = set()
    for user, rating in users_movie_ratings.items():
        for movie in rating.keys():
            ratings += 1
            movies.add(movie)

    print "Number of nodes: ", str(len(graph.nodes()))
    print "Number of edges: ", str(len(graph.edges()))
    print "Number of users: ", str(len(users_movie_ratings.keys()))
    print "Number of ratings: ", str(ratings)
    print "Number of different rated movies: ", str(len(movies))
