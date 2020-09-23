def check_for_old_images(check_image):
    """
    Check if there are any previous images and suffix them with "_old" if applicable.
    """
    if (os.path.exists(check_image)):
        for old_file in glob.glob(check_image[:-5]+'*'):
            os.system('mv '+old_file+' '+old_file+'_old')
