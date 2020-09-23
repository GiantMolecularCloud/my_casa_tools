#############################
# CASA region to mask image #
#############################

def region_to_mask(region, template, overwrite=False):

    """Convert a CASA region file to a mask image.

    Parameters
    ----------
    region : string
        Region file name
    template : string
        Template image file name

    Returns
    -------
    CASA image
        Creates CASA image containing the mask. Returns nothing.

    """

    import uuid
    tempfile = 'temp_r2m.'+str(uuid.uuid4())[:6]

    # add degenerate axes if necessary
    ia.open(template)
    shape = ia.shape()
    if ( len(shape) == 2 ):
        ia.adddegaxes(spectral = True, stokes='I', outfile=tempfile, overwrite=True)
        inpimage = tempfile
    elif ( len(shape) == 3 ):
        ia.adddegaxes(stokes='I', outfile=tempfile, overwrite=True)
        inpimage = tempfile
    else:
        inpimage = template
    ia.close()
    ia.done()

    # region to mask
    makemask(mode = 'copy',
        inpimage  = inpimage,
        inpmask   = region,
        output    = '.'.join(region.split('.')[:-1])+'.mask',
        overwrite = overwrite
        )

    os.system('rm -rf '+tempfile)
