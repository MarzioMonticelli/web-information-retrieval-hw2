import dataretrieving as dr
import networkx as nx
import operator

movie_graph_file_path = '../datasets/movie_graph.txt'
user_movie_rating_file_path = '../datasets/user_movie_rating.txt'
category_movies_file_path = '../datasets/category_movies.txt'

reduced_graph_file = "../datasets/reduced_datasets/reduced_movie_graph.txt"
reduced_category_movie_file = "../datasets/reduced_datasets/reduced_category_movies.txt"
reduced_user_movie_ratings_file = "../datasets/reduced_datasets/reduced_user_movie_rating.txt"

alpha = .15
epsilon = 10 ** -6


def create_initial_pagerank_vector(graph):
    """

    :param networkx.Graph graph: 
    :return:
    :rtype: dict
    """
    page_rank_vec = {}
    num_nodes = graph.number_of_nodes()
    for node_index in xrange(1, num_nodes + 1):
        page_rank_vec[node_index] = 1. / num_nodes

    return page_rank_vec


def single_iteration_page_rank(graph, page_rank_vector, alpha=alpha, personalization=None,
                               precomputed_weights=None):
    """
    Calculates a single iteration pagerank from the previous pagerank
    
    :param networkx.Graph graph:
    :param dict[int, float] page_rank_vector: previous iteration pagerank 
    :param float alpha: the alpha value of the pagerank
    :param dict[int, float] | None personalization: a map <node_id, interest> used to personalize 
     the teleport 
    :param dict[int, float] precomputed_weights: it is an optimization in order to speed up the 
     algorithm using the Dynamic Programming technique. Without this optimization the sum of the 
     weights of all the edges of each node will be computed at each iteration, while with this 
     optimization it would not be needed and the algorithm will be much faster.
    :return: the current iteration pagerank
    :rtype: dict[int, float]
    """

    if precomputed_weights is None:
        precomputed_weights = dict()
    next_page_rank_vector = {}
    sum_rjs = 0.
    for node_j in graph.nodes(data=False):
        r_j = 0.
        for adj_node_j in graph.neighbors(node_j):
            data = graph.get_edge_data(node_j, adj_node_j)
            assert 'weight' in data.keys()
            weight = float(data['weight'])

            # retrieve or calculate the sum of the weights of the edges of the adjacent node
            if adj_node_j in precomputed_weights:
                weight_tot = precomputed_weights[adj_node_j]
            else:
                weight_tot = 0.
                for adj2_node_j in graph.neighbors(adj_node_j):
                    data = graph.get_edge_data(adj_node_j, adj2_node_j)
                    assert 'weight' in data.keys()
                    weight_tot += float(data['weight'])
                precomputed_weights[adj_node_j] = weight_tot

            # increases the pagerank value of the current node with the contribute from the edge
            # in analysis
            r_j += (1. - alpha) * page_rank_vector[adj_node_j] * weight / weight_tot

        next_page_rank_vector[node_j] = r_j
        sum_rjs += r_j
    leaked_pr = 1. - sum_rjs

    # here it divides the leaked_pr
    # (the alpha % of probability that has to be given to the Teleport)
    if personalization:
        assert type(personalization) == dict
        personalization_total_values = \
            float(sum(
                personalization.values()))  # it is 1.0 if the personalization vector is normalized

        # distributes the probability with respect to the preferences
        # expressed with the personalization vector
        for node_index, personalization_value in personalization.items():
            assert node_index in next_page_rank_vector
            next_page_rank_vector[
                node_index] += leaked_pr * personalization_value / personalization_total_values

    else:
        # uniform distribution among all nodes
        num_nodes = graph.number_of_nodes()
        for index in next_page_rank_vector.keys():
            next_page_rank_vector[index] += leaked_pr / num_nodes

    # check: the sum of all the PageRanks must be 1.0, because it is a probability distribution
    next_page_rank_vector_sum = float(sum(next_page_rank_vector.values()))
    assert is_close(next_page_rank_vector_sum, 1.)

    return next_page_rank_vector


def get_distance(vector_1, vector_2):
    dist = 0.
    for node_id in vector_1.keys():
        dist += abs(vector_1[node_id] - vector_2[node_id])

    return dist


def from_preference_to_weights(categories, categories_interest):
    """
    
    :param categories: 
    :param dict[int, float] categories_interest: 
    :return: 
    """

    # normalize categories-interest
    categories_interest_sum = float(sum(categories_interest.values()))
    for category, interest in categories_interest.items():
        categories_interest[category] = interest / categories_interest_sum

    # counting node in categories
    nodes_in_categories = 0
    for category_nodes in categories.values():
        nodes_in_categories += len(category_nodes)

    # build the personalization vector from the category interest
    personalization_categories = {}
    for index, category_nodes in categories.items():
        rate = categories_interest[index]
        if rate > 0.:
            elements_in_category = len(category_nodes)
            for category_node in category_nodes:
                if category_node in personalization_categories:
                    personalization_categories[category_node] += 1. / (rate * elements_in_category)
                else:
                    personalization_categories[category_node] = 1. / (rate * elements_in_category)

    return personalization_categories


def calculate_page_rank(graph=dr.extract_graph(), alpha=alpha, epsilon=epsilon,
                        personalization=None):
    """
    It computes the pagerank for the given Undirected Weighted Graph, alpha, epsilon,
    and personalization.
    
    :param networkx.Graph graph: Weighted Undirected graph
    :param float alpha: the pagerank alpha value
    :param float epsilon: the degree of convergence
    :param dict[int, float] personalization: a map <node_id, interest> used to personalize 
     the teleport
    :return: the pagerank with a degree of convergence of epsilon
    """
    # creates an initial uniform distribution of probability among all nodes
    previous_page_rank_vector = create_initial_pagerank_vector(graph)

    num_iterations = 0
    # pre-compute weights vector for optimization
    precomputed_weights = {}
    for node_j in graph.nodes(data=False):
        if node_j not in precomputed_weights:
            weight_tot = 0.
            for adj2_node_j in graph.neighbors(node_j):
                data = graph.get_edge_data(node_j, adj2_node_j)
                assert 'weight' in data.keys()
                weight_tot += float(data['weight'])
            precomputed_weights[node_j] = weight_tot

    while True:
        # compute next pagerank from the previous one
        pagerank_vector = single_iteration_page_rank(graph, previous_page_rank_vector,
                                                     alpha=alpha, personalization=personalization,
                                                     precomputed_weights=precomputed_weights)

        num_iterations += 1
        # evaluate the distance between the old and new pagerank vectors
        distance = get_distance(previous_page_rank_vector, pagerank_vector)
        # check convergency
        if distance <= epsilon:
            # print
            # print " Convergence!"
            # print
            break

        previous_page_rank_vector = pagerank_vector

    # sort the pagerank vector in decreasing order of pagerank value
    sorted_pagerank_vector = sorted(pagerank_vector.items(), key=operator.itemgetter(1),
                                    reverse=True)
    sorted_pagerank_dict = {}
    for pr_tuple in sorted_pagerank_vector:
        sorted_pagerank_dict[pr_tuple[0]] = pr_tuple[1]

    return sorted_pagerank_dict


def calculate_page_rank_categories(graph=dr.extract_graph(), categories=dr.extract_categories(),
                                   category_interest=None, alpha=alpha):
    """
    
    :param networkx.Graph graph: movie graph
    :param dict[int, list[int]] categories: relation category_id <-> movie_id 
    :param dict[int, float] category_interest: float values for interests in category
    :return: a PageRank vector: one Real value for each node (movie_id) of the graph
    :rtype: dict[int, float]
    """

    personalization = None
    if category_interest:
        personalization = from_preference_to_weights(categories, category_interest)

    return calculate_page_rank(graph=graph, personalization=personalization, alpha=alpha)


def is_close(a, b, rel_tol=1e-03, abs_tol=0.1):
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


if __name__ == '__main__':
    # extract users_ratings
    users_ratings = dr.extract_users_movie_rating(user_movie_rating_file_path)

    # load categories
    categories = dr.extract_categories(category_movies_file_path)

    # graph creation
    movie_graph = dr.extract_graph(movie_graph_file_path)

    # Compute Topic-Specific PageRank
    categories_interest = {0: .1,
                           1: .1,
                           2: .1,
                           3: .1,
                           4: .1}

    personalization = from_preference_to_weights(categories=categories,
                                                 categories_interest=categories_interest)
    # pad personalization
    for node_id in movie_graph.nodes():
        if node_id not in personalization:
            personalization[node_id] = 0

    import time

    nx_pg_time_start = time.clock()
    print "Calculating Networkx Pagerank"
    nx_pagerank = nx.pagerank(G=movie_graph, alpha=1 - alpha, tol=epsilon,
                              weight='weight', personalization=personalization)
    # pp.pprint(nx_pagerank)

    my_pg_time_start = time.clock()
    print "Calculating My Pagerank"
    page_rank_vector = calculate_page_rank_categories(graph=movie_graph,
                                                      categories=categories,
                                                      category_interest=categories_interest)
    # pp.pprint(page_rank_vector)
    my_pg_time_end = time.clock()

    print "Comparing mine pagerank and networkx pagerank"
    equals = True
    wrongs = 0
    totals = 0
    for movie_id, movie_pagerank in nx_pagerank.items():
        my_res = page_rank_vector[movie_id]
        totals += 1
        if not is_close(a=movie_pagerank, b=my_res, ):
            print "Different values for movie id: ", str(movie_id), ":\tnx: ", str(
                movie_pagerank), "\tmine: ", str(
                page_rank_vector[movie_id])
            wrongs += 1
            equals = False

    if equals:
        print "\nThe Pageranks are equals"
    else:
        print "\nThe Pageranks are different"

    print "Totals: ", str(totals)
    print "Wrongs: ", str(wrongs)
    print "Corrects: ", str(totals - wrongs)

    # order pageranks through score
    nx_pagerank_sorted = sorted(nx_pagerank.items(), key=operator.itemgetter(1), reverse=True)
    pagerank_sorted = sorted(page_rank_vector.items(), key=operator.itemgetter(1), reverse=True)

    count_equals_ordered = 0
    count_equals_positions = 0
    stop = False
    for nx_pg, my_pg in zip(nx_pagerank_sorted, pagerank_sorted):
        print "nx: (", str(nx_pg[0]), ", ", str(nx_pg[1]), ")\tmy: (", str(my_pg[0]), ", ", str(
            my_pg[1]), ")"
        if nx_pg[0] == my_pg[0]:
            count_equals_positions += 1
            if not stop:
                count_equals_ordered += 1
        elif not stop:
            stop = True

    print "The firsts ", str(count_equals_ordered), " are equally ranked!"
    print "Among all, ", str(count_equals_positions), " are ranked in the same position!"
    print "Time spent for Networkx pagerank: ", str(my_pg_time_start - nx_pg_time_start), " seconds"
    print "Time spent for My pagerank: ", str(my_pg_time_end - my_pg_time_start), " seconds"
