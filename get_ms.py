def get_ms(ms):
    """
    Check if the requested measurement set is available and copy it if necessaery.
    """
    if not (os.path.exists(ms)):
        print("Copying "+ms+" ...")
        print("This might take a while for large datasets.")
        os.system('rsync -ah --progress '+datadir+ms+' .')
        print("")
