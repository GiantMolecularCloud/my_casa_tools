def get_idx2(alist, name):
    """
    return the the index of an item called by its name in dictionary
    """
    for idx, itm in enumerate(alist):
        if (name in itm['name']):
            return idx
