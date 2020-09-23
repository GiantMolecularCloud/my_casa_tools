def get_idx(alist, name, key='name'):
    """
    return the the index of an item called by its name in dictionary
    """

    for idx, itm in enumerate(alist):
        if (itm[key] in name):
            if not ( alist[idx][key] == name ):
                raise NameError("Names in list are not unique!")
            else:
                return idx
