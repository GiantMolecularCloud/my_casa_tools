def mkdir(path):
    """mkdir

    Parameters
    ----------
    path : str
        Path to directory to create
    """
    import os
    if ' ' in path:
        raise Exception("Path contains spaces! This will most probably not create the directory you want!")
    os.system('mkdir -p '+path)
    print("Created "+path)
