import pprint as pp
import sys
import WebIR_HW_2_part_3_offline as offline
import operator

# TODO: remember to remove all the prints except for the printing of the results!


def usage(do_exit=True):
    print "python WebIR_HW_2_part_3_online.py user_preference_vector"
    if do_exit:
        exit(1)


if __name__ == '__main__':
    # parsing input
    if len(sys.argv) != 2:
        print "Not enough parameter passed."
        print usage()

    # parsing and checking inputs
    user_preference_string = sys.argv[1]  # type: str
    user_preference_vector = user_preference_string.split("_")  # type: list
    if len(user_preference_vector) != 5:
        print "Invalid vector passed: ", str(user_preference_vector)

    user_preference_vector_float = {}
    sum_f = 0.
    for index, preference in enumerate(user_preference_vector):
        if float(preference) < 0:
            print "Invalid value passed: ", preference
            exit(1)

        user_preference_vector_float[index] = float(preference)
        sum_f += float(preference)

    # normalize categories_interest
    interest_sum = float(sum(user_preference_vector_float.values()))
    for cat_id in user_preference_vector_float.keys():
        user_preference_vector_float[cat_id] /= interest_sum

    if not offline.are_category_pagerank_generated():
        offline.create_datasets()

    # page_rank = po.calculate_page_rank_categories(category_interest=user_preference_vector_float)
    # pp.pprint(page_rank)

    # Calculating composite pagerank
    num_pagerank_entries = len(offline.get_category_pagerank(0).keys())
    composite_pagerank = dict((x, 0.) for x in xrange(1, num_pagerank_entries + 1))

    for cat_id, interest in user_preference_vector_float.items():
        if interest > 0.:
            cat_pagerank = offline.get_category_pagerank(cat_id)
            for comp_cat_id, comp_interest in composite_pagerank.items():
                composite_pagerank[comp_cat_id] += cat_pagerank[comp_cat_id] * interest

    # sort
    pagerank_sorted = sorted(composite_pagerank.items(), key=operator.itemgetter(1), reverse=True)

    # print
    for node_id, pagerank in pagerank_sorted:
        print str(node_id), ", ", str(pagerank)

    """counter = 0
    for comp_interest, dir_interest in zip(composite_pagerank.values(), page_rank.values()):
        if not po.is_close(comp_interest, dir_interest):
            print "Elements at index ", str(counter), " differs:\tc: ", str(comp_interest), "\td: ", str(dir_interest)
        else:
            print "Elements at index ", str(counter), " are EQUALS:\tc: ", str(comp_interest), "\td: ", str(
                dir_interest)
            differents = True
        counter += 1
    """

