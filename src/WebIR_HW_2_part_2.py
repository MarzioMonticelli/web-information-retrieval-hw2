import pprint as pp
import dataretrieving as dr
import PartOne as po
import sys
import os
import operator


# TODO: remember to remove all the prints except for the printing of the results!


def usage(do_exit=True):
    print "python WebIR_HW_2_part_2.py path_to_graph_file path_to_users_ratings USER_ID"
    if do_exit:
        exit(1)


if __name__ == '__main__':
    # parsing input
    if len(sys.argv) < 4:
        print "Not enough parameter passed."
        print usage()

    # check inputs
    graph_file = sys.argv[1]
    users_ratings_file = sys.argv[2]
    user_id = 2048  # due to annoying IDE warning

    try:
        user_id = int(sys.argv[3])
    except ValueError:
        print "The User ID passed is not a number: ", sys.argv[3]
        exit(1)

    if not os.path.isfile(graph_file):
        print "Graph file not found: ", graph_file
        exit(1)

    if not os.path.isfile(users_ratings_file):
        print "Users' ratings file not found: ", users_ratings_file
        exit(1)

    # extract users_ratings
    users_movie_ratings = dr.extract_users_movie_rating(file_path=users_ratings_file)
    if user_id not in users_movie_ratings.keys():
        keys = users_movie_ratings.keys()
        pp.pprint(keys)
        print "User id not found: ", user_id
        exit(0)

    user_rated_movies = users_movie_ratings[user_id]

    # graph creation
    movie_graph = dr.extract_graph(file_path=graph_file)

    # extract personalization from user-rating
    personalization = {}
    ratings_sum = float(sum(user_rated_movies.values()))

    # normalization
    for movie_id, rating in user_rated_movies.items():
        personalization[movie_id] = rating / ratings_sum

    user_page_rank = po.calculate_page_rank(graph=movie_graph, personalization=personalization)

    # Filter user_page_ranks:
    # Of course, the output list must not contain movies_id associated to
    # movies already rated by the input user.
    for movie_id in user_rated_movies.keys():
        user_page_rank.pop(movie_id)

    # renormalize pagerank to 1.0
    pagerank_sum = float(sum(user_page_rank.values()))
    for movie_id, pagerank in user_page_rank.items():
        user_page_rank[movie_id] = pagerank / pagerank_sum

    pagerank_sorted = sorted(user_page_rank.items(), key=operator.itemgetter(1), reverse=True)

    # print
    for node_id, pagerank in pagerank_sorted:
        print str(node_id), ", ", str(pagerank)

    """ DEBUG
      import networkx as nx

      # padd personalization
      for node_index in movie_graph.nodes():
          personalization.setdefault(node_index, 0.)

      nx_page_rank = nx.pagerank(G=movie_graph, alpha=1 - po.alpha, tol=po.epsilon, personalization=personalization)

      # check pageranks
      close_results = 0
      for nx_node_index, nx_rank in nx_page_rank.items():
          if not po.is_close(user_page_rank[nx_node_index], nx_rank, rel_tol=1e-02):
              print "Different values for node ", str(nx_node_index), ":\tnx: ", str(nx_rank), "\tmine: ", str(
                  user_page_rank[nx_node_index])
          else:
              close_results += 1

      print "\nClose results: ", str(close_results), "/", str(len(nx_page_rank.keys()))

      # order pageranks through score
      import operator

      nx_pagerank_sorted = sorted(nx_page_rank.items(), key=operator.itemgetter(1), reverse=True)
      pagerank_sorted = sorted(user_page_rank.items(), key=operator.itemgetter(1), reverse=True)

      count_equals_ordered = 0
      count_equals_positions = 0
      stop = False
      for nx_pg, my_pg in zip(nx_pagerank_sorted, pagerank_sorted):
          print "nx: (", str(nx_pg[0]), ", ", str(nx_pg[1]), ")\tmy: (", str(my_pg[0]), ", ", str(my_pg[1]), ")"
          if nx_pg[0] == my_pg[0]:
              count_equals_positions += 1
              if not stop:
                  count_equals_ordered += 1
          elif not stop:
              stop = True

      print "The firsts ", str(count_equals_ordered), " are equally ranked!"
      print "Among all, ", str(count_equals_positions), " are ranked in the same position!"
      """