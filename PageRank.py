import csv
import pprint as pp
import networkx as nx

# input_graph_adjacency_list_file_name = './small_graph__adjacency_list.tsv'
input_graph_adjacency_list_file_name = './wiki_graph__adjacency_list.tsv'

alpha = .15
epsilon = 10 ** -6


########################################################################################
########################################################################################
########################################################################################

# Complete the method, please.
def create_initial_pagerank_vector(graph):
    """
    
    :param networkx.DiGraph graph: 
    :return:
    :rtype: dict
    """
    page_rank_vec = {}
    num_nodes = graph.number_of_nodes()
    for node_index in xrange(0, num_nodes):
        page_rank_vec[node_index] = 1. / num_nodes

    return page_rank_vec


# Complete the method, please.
def single_iteration_page_rank(graph, reverse_graph, page_rank_vector, alpha, personalization=None):
    """
    
    :param networkx.DiGraph graph:
    :param networkx.DiGraph reverse_graph: 
    :param dict page_rank_vector:
    :param float alpha: 
    :return: 
    """
    next_page_rank_vector = {}
    sum_rjs = 0.
    for node_j in graph.nodes(data=False):
        r_j = 0.
        for in_edge_j in graph.in_edges(node_j):  # type: tuple(int, int)
            adj_node_index = in_edge_j[0]
            r_j += (1. - alpha) * page_rank_vector[adj_node_index] / graph.out_degree(adj_node_index)
        next_page_rank_vector[node_j] = r_j
        sum_rjs += r_j
    leaked_pr = 1. - sum_rjs

    num_nodes = graph.number_of_nodes()
    for index in next_page_rank_vector.keys():
        next_page_rank_vector[index] += leaked_pr / num_nodes

    return next_page_rank_vector


# Complete the method, please.
def get_distance(vector_1, vector_2):
    distance = 0.

    for node_id in vector_1.keys():
        distance += abs(vector_1[node_id] - vector_2[node_id])

    return distance


########################################################################################
########################################################################################
########################################################################################

# graph creation
g = nx.DiGraph()

# load graph
input_file = open(input_graph_adjacency_list_file_name, 'r')
input_file_csv_reader = csv.reader(input_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_NONE)
for node__adjacency_list in input_file_csv_reader:
    g.add_node(int(node__adjacency_list[0]))
    for adjacent in node__adjacency_list[1:]:
        g.add_edge(*[int(node__adjacency_list[0]), int(adjacent)])

input_file.close()

# print graph
print
print "Graph"
print type(g)
for node in g:
    print str(node) + " -- " + str(g[node])
print

reverse_g = g.reverse(copy=True)

# print reverse graph
print
print "Reverse or Transpose Graph"
for node in reverse_g:
    print str(node) + " -- " + str(reverse_g[node])
print

# Compute PageRank
previous_page_rank_vector = create_initial_pagerank_vector(g)
page_rank_vector = {}
num_iterations = 0
while True:

    pp.pprint(previous_page_rank_vector)

    # compute next value
    page_rank_vector = single_iteration_page_rank(g, reverse_g, previous_page_rank_vector, alpha)

    num_iterations += 1

    # evaluate the distance between the old and new pagerank vectors
    distance = get_distance(previous_page_rank_vector, page_rank_vector)

    print
    print " iteration number " + str(num_iterations)
    print " distance= " + str(distance)
    # check convergency
    if distance <= epsilon:
        print
        print " Convergence!"
        print
        break

    previous_page_rank_vector = page_rank_vector

pp.pprint(page_rank_vector)

print "Page rank vector size: ", len(page_rank_vector)
print "Graph nodes: ", len(g.nodes())
# Useful code for debugging ;)
'''
print
print "start PR"
damping_factor = 1. - alpha
pr = nx.pagerank(g, alpha=damping_factor, tol=epsilon)
print "end PR"
print
pp.pprint(pr)
print
print
distance = get_distance(page_rank_vector, pr)
print " distance(just_implemented_pr, NetworkX_pr)= " + str(distance)
print
'''
