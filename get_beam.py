####################################################################################################

# get beam
##########

def get_beam(images):

    """
    Get (median) beams of image files.

    Parameters
    ----------
    images : list,str
        Single image file name or list of file names. Must be CASA images or fits file that casa
        can read.

    Returns
    -------
    median major/minor beam size as astropy.units objects
    """




    casalog.post("*"*80)
    casalog.post("FUNCTION: GET BEAM")
    casalog.post("*"*80)

    if isinstance(images, (list,)):
        inp_type = 'multiple images'
        pass
    elif isinstance(images, basestring):
        images = [images]
        inp_type = 'single image'


    major_list = []
    minor_list = []
    beam_types = []
    for image in images:
        ia.open(image)
        beams = ia.restoringbeam()
        ia.done()

        if ( 'major' in beams.keys() ):
            major_list.append(u.Quantity(str(beams['major']['value'])+str(beams['major']['unit'])))
            minor_list.append(u.Quantity(str(beams['minor']['value'])+str(beams['minor']['unit'])))
            beam_types.append('simple beam')
        elif ( 'beams' in beams.keys() ):
            beam_types.append('multiple beams')
            for chan,beam in beams['beams'].iteritems():
                major_list.append(u.Quantity(str(beam['*0']['major']['value'])+str(beam['*0']['major']['unit'])))
                minor_list.append(u.Quantity(str(beam['*0']['minor']['value'])+str(beam['*0']['minor']['unit'])))

    major_med = np.median( [(maj.to(u.arcsec)).value for maj in major_list] )*u.arcsec
    minor_med = np.median( [(min.to(u.arcsec)).value for min in minor_list] )*u.arcsec

    if ( 'multiple beams' in beam_types):
        beam_type = 'multiple beams in at least one image.'
    else:
        beam_type = 'single beam(s).'

    casalog.post("*"*80)
    casalog.post('Found '+inp_type+' with '+beam_type)
    casalog.post("major: "+str(major_med))
    casalog.post("minor: "+str(minor_med))
    casalog.post("*"*80)

    return major_med, minor_med

###############################################################################
