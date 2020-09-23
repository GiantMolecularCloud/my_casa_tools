#####################################################################
#                            CASA TOOLS                             #
#####################################################################
# These functions perform standard CASA operations that are not     #
# included as CASA tasks, toolkits or extensions.                   #
#####################################################################

def grow_image(infile, outfile, growpix):

    """

    grow image: grow the size of an image
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Grow the spatial size of an image by the given number of pixels. Growing is
    done symmetrically to each side at the moment. The final image will be
    larger by 2*growpix.
    To be done: option to treat the input size as the target size
                option to enter physical size (e.g. in arcmin)

    Mandatory unnamed, ordered arguments:
        infile      Path and file name of the input file. Must be a format known
                    to CASA: image, fits or miriad image
        outfile     Path and file name of the grown image. Is always a CASA image
        growpix     Number of pixels that the image is grown. A single integer
                    grows the image on all four sides. Differing grow scales can
                    be given as a list of two integers.

    examples:

    grow_image(infile  = 'test.image',
               outfile = 'test_grown.image',
               growpix = 100
              )
    grow_image(infile  = 'test.image',
               outfile = 'test_grown.image',
               growpix = [100,200]
              )

    """


    casalog.origin('grow_image')
    casalog.post('growing image: '+infile)

    # check CASA version and stop execution if 5.0.0
    import casadef
    if (casadef.casa_version == '5.0.0'):
        casalog.post('CASA 5.0.0 contains a bug. The ia tool is not available through the taskinit module.')
        casalog.post('Please use a CASA version < 5.0.0 or > 5.0')
        casalog.post('Canceling task ...')
        quit()

    # get current size
    ia.open(infile)
    shape = ia.shape()
    ia.done()

    if isinstance(growpix, int):
        grow_x = growpix
        grow_y = growpix

    elif isinstance(growpix, (list,tuple)):
        grow_x = growpix[0]
        grow_y = growpix[1]
    else:
        raise TypeError('growpix must be an integer or a two-element list of integers')

    # inform user
    casalog.post('current size: ['+str(shape[0])+','+str(shape[1])+'], growing to ['+str(shape[0]+2*grow_x)+','+str(shape[1]+2*grow_y)+']')

    # get image coordinate system
    csys = imregrid(imagename  = infile,
                    output     = '',
                    template   = 'get',
                    asvelocity = True,
                    axes       = [0,1],
                    interpolation = 'linear'
                    )

    # grow image
    csys['shap'][0] += 2.0*grow_x
    csys['shap'][1] += 2.0*grow_y

    # correct reference pixels
    csys['csys']['direction0']['crpix'][0] += grow_x
    csys['csys']['direction0']['crpix'][1] += grow_y

    # write corrected coordinate system to file
    imregrid(imagename  = infile,
            output     = outfile,
            template   = csys,
            asvelocity = True,
            axes       = [0,1],
            interpolation = 'linear'
            )

####################################################################################################
