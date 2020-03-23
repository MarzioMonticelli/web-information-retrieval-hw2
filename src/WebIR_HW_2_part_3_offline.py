import pprint as pp
import dataretrieving as dr
import PartOne as po
import os

# TODO: remember to remove all the prints except for the printing of the results!

dataset_dir = "../datasets/"

""" 
    MAIN IDEA:
    I can calculate the pagerank for each category and then linearly sum their weighted values. 
    Each of the elements of the sum must be weighted with the category preference of the user. 
"""
category_file_prefix = "category-"
none_file_path = dataset_dir + category_file_prefix + "Base"


def create_datasets():
    categories = dr.extract_categories()

    for cat_num, category in enumerate(categories):
        cat_file_path = dataset_dir + category_file_prefix + str(cat_num)
        if os.path.isfile(cat_file_path):
            continue

        cat_file = open(cat_file_path, 'w')

        cat_personalization = {0: 0., 1: 0., 2: 0., 3: 0., 4: 0., cat_num: 1.}
        category_pagerank = po.calculate_page_rank_categories(category_interest=cat_personalization)

        for movie_id, movie_pagerank in category_pagerank.items():
            cat_file.write(str(movie_id) + ": " + str(movie_pagerank) + "\n")

        cat_file.close()

    """
    if not os.path.isfile(none_file_path):
        none_file = open(none_file_path, 'w')
        none_pagerank = po.calculate_page_rank(teleporting=False)

        for movie_id, movie_pagerank in none_pagerank.items():
            none_file.write(str(movie_id) + ": " + str(movie_pagerank) + "\n")

        none_file.close()
    """


def get_category_pagerank(category_id):
    """
    
    :param int | None category_id: the id of the category, must be one of the following values: 0, 1, 2, 3, 4 
    :return: the pagerank for the choosen category
    :rtype: dict[int, float]
    """
    assert type(category_id) == int, category_id in range(0, 5, step=1)

    cat_file_path = dataset_dir + category_file_prefix + str(category_id)
    cat_file = open(cat_file_path, 'r')

    pagerank = {}
    for line in cat_file:
        splits = line.split(": ")
        movie_id = int(splits[0])
        movie_pagerank = float(splits[1])
        pagerank[movie_id] = movie_pagerank

    return pagerank


def are_category_pagerank_generated():
    """
    Checks if there exists the files with the pagerank for the categories
    :return: True iff all the files category-X (with X in {0, ..., 4}) exists
     :rtype: bool
    """
    for category_id in xrange(0, 5):
        if not os.path.isfile(dataset_dir + category_file_prefix + str(category_id)):
            return False
    return os.path.isfile(none_file_path)


if __name__ == '__main__':
    if not are_category_pagerank_generated():
        create_datasets()

    categories_interests = {0: 1., 1: 1., 2: 1., 3: .0, 4: .0}

    # normalize categories_interest
    interest_sum = float(sum(categories_interests.values()))
    for cat_id in categories_interests.keys():
        categories_interests[cat_id] /= interest_sum

    # print "Calculating composite pagerank"
    num_pagerank_entries = len(get_category_pagerank(0).keys())
    composite_pagerank = dict((x, 0.) for x in xrange(1, num_pagerank_entries + 1))

    for cat_id, interest in categories_interests.items():
        if interest > 0.:
            cat_pagerank = get_category_pagerank(cat_id)
            for comp_cat_id, comp_interest in composite_pagerank.items():
                composite_pagerank[comp_cat_id] += cat_pagerank[comp_cat_id] * interest

    """
    print "Calculating direct pagerank"
    direct_pagerank = po.calculate_page_rank_categories(category_interest=categories_interests)

    print "Comparing direct and composite pageranks"
    counter = 0
    differents = False
    import PartOne as po

    for comp_interest, dir_interest in zip(composite_pagerank.values(), direct_pagerank.values()):
        if not po.is_close(comp_interest, dir_interest):
            print "Elements at index ", str(counter), " differs:\tc: ", str(comp_interest), "\td: ", str(dir_interest)
        else:
            print "Elements at index ", str(counter), " are EQUALS:\tc: ", str(comp_interest), "\td: ", str(
                dir_interest)
            differents = True
        counter += 1

    print
    print

    import operator

    nx_pagerank_sorted = sorted(direct_pagerank.items(), key=operator.itemgetter(1), reverse=True)
    pagerank_sorted = sorted(composite_pagerank.items(), key=operator.itemgetter(1), reverse=True)

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