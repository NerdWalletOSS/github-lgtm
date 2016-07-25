from collections import OrderedDict


def ordered_set(item_list):
    """
    Return a list of the unique set of items, with order maintained by first appearance
    :param item_list: A list of items that can be compared to each other
    :return: a list of unique items
    """
    # useful b/c Python does not have an ordered set builtin
    items = OrderedDict()
    for item in item_list:
        items[item] = item
    return items.values()
