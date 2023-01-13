# Ben Levi 318811304 and Eliran Eiluz 313268146

# This function is used to estimate the quality of the crawler by 3 parameters:
# precision: amount of "good" links that the crawler returned / amount of links that the crawler returned
# recall: amount of "good" links that the crawler returned / amount of links that the crawler should have been return
# F1: (2 * precision * recall) / (precision + recall)

# Notice that any of the parameters can't be calculated precisely.

# For the calculation of the precision parameter, we need to know the amount of "good" links we returned,
# but we can only estimate this value by counting the number of links that we know for sure that they are good.

# For the calculation of the recall parameter, we should also know the amount of "good" links we returned as in
# precision. But, we should also know how many "good" links there is. To estimate how many good links there is,
# we counted the number of members in the british royal family according to the definition in the exercise.
# we reached 43.

def crawlerQuality(listOfPairs):
    # a dictionary to hold the quality parameters and its values.
    metrics_dict = dict()

    # the links that the crawler returned. we save them in a set because we don't want to count the same link
    # more than one time.
    links_set = set()

    # the estimated amount of "good" links as explained above.
    p_size = 43

    # add all the returned links to set.
    for pair in listOfPairs:
        links_set.add(pair[0])
        links_set.add(pair[1])

    # crate a set of valid links. a link is counted as valid if it appears on the left side of a pair
    # or if it appears on the right side of a pair and the is_crawled value is 1.
    valid_links = set()
    for lst in listOfPairs:
        valid_links.add(lst[0])
        if lst[2] == 1:
            valid_links.add(lst[1])
    amount_of_valid_links = len(valid_links)

    # calculate the quality parameters, save them in the dictionary and return the dictionary.
    metrics_dict['precision'] = amount_of_valid_links / len(links_set)
    metrics_dict['recall'] = amount_of_valid_links / p_size
    metrics_dict['F1'] = (2 * metrics_dict['precision'] * metrics_dict['recall']) / (
            metrics_dict['precision'] + metrics_dict['recall'])

    return metrics_dict
