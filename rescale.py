from __future__ import print_function

####################################################################################################
# RESIDUAL SCALING
####################################################################################################

__all__ = ['rescale_image']


####################################################################################################

# imports
#########

import numpy as np
from astropy.io import fits
from astropy.modeling import models


####################################################################################################

# load data
###########

def load_cubes(im, p, mod, res):
    print("Loading cube 1 of 4 (image)", end='\r')
    image = fits.open(im)[0]
    print("Loading cube 2 of 4 (psf)", end='\r')
    psf   = fits.open(p)[0]
    print("Loading cube 3 of 4 (model)", end='\r')
    model = fits.open(mod)[0]
    print("Loading cube 4 of 4 (residual)", end='\r')
    residual = fits.open(res)[0]

    return image, psf, model, residual


####################################################################################################

# image dimensions
##################

def check_image_dimensions(psf_header):
    if (psf_header['naxis'] == 2):
        n_x = psf_header['naxis1']
        n_y = psf_header['naxis2']
        n_chan = 1
    elif (psf_header['naxis'] == 3):
        n_x = psf_header['naxis1']
        n_y = psf_header['naxis2']
        n_chan = psf_header['naxis3']
    else:
        raise NotImplementedError("You most specified an image with "+str(psf.header['naxis'])+" axes. I can only handle 3 axes so far. Drop the stokes axis.")

    return n_x,n_y,n_chan


####################################################################################################

# beam area
###########

def get_beam_area(array, n_x, n_y):
    """
    Calculate the beam area of a psf image (single plane) with n_x by n_y pixels.
    The psf peak is assumed to be in the center of the image. Beam area is calculated in circular regions.
    """

    # calculate distance to center
    y, x = np.mgrid[n_y-1:-1:-1, :n_x]
    dist = np.sqrt((x-n_x/2)**2 + (y-n_y/2)**2)

    # loop over distances
    area = []
    for d in np.arange(np.nanmax(dist)):
        A = np.nansum(array[dist<=d])
        area.append([d,A])

    return area

    # psf_areas = []
    # box_sizes = []
    # # calculate 20 beam areas to get the asymptotic area
    # for idx in np.arange(101):
    #
    #     # box size
    #     box_x = int( n_x/100*idx )
    #     box_y = int( n_y/100*idx )
    #     box_sizes.append([box_x,box_y])
    #
    #     # limits of the box
    #     xl = int( n_x/2. - box_x/2. )
    #     xu = int( n_x/2. + box_x/2. )
    #     yl = int( n_y/2. - box_y/2. )
    #     yu = int( n_y/2. + box_y/2. )
    #
    #     # sum flux in box
    #     psf_areas.append( np.nansum(array[yl:yu,xl:xu]) )
    #
    # return box_sizes,psf_areas


####################################################################################################

# clean beam
############

def calculate_clean_beam(image_header, n_x, n_y):
    bmaj_pix = (image_header['bmaj']*u.degree/u.Quantity(str(np.abs(image_header['cdelt1']))+image_header['cunit1'])).value
    bmin_pix = (image_header['bmin']*u.degree/u.Quantity(str(np.abs(image_header['cdelt2']))+image_header['cunit2'])).value
    bpa_rad  = (image_header['bpa']*u.degree).to(u.radian).value

    gauss2d = models.Gaussian2D(amplitude = 1,
                                x_mean    = n_x/2,
                                y_mean    = n_y/2,
                                x_stddev  = bmaj_pix,
                                y_stddev  = bmaj_pix,
                                theta     = bpa_rad
                               )

    y, x = np.mgrid[n_y-1:-1:-1, :n_x]
    clean_beam = gauss2d(x,y)

    return clean_beam


####################################################################################################

# rescale factor
################

def get_f_rescale(psf_data,clean_beam, n_x,n_y):
    """
    Calculate rescaling factoring for a given psf and image (astropyHDU objects).
    """

    A_dirty_beam = get_beam_area(psf_data,n_x,n_y)
    A_clean_beam = get_beam_area(clean_beam,n_x,n_y)

    f_rescale = [c/d for c,d in zip([a[1] for a in A_clean_beam], [a[1] for a in A_dirty_beam])]

    return np.nanmax(f_rescale)


####################################################################################################

# rescale image
###############

def rescale_image(image_file, psf_file, model_file, residual_file, rescaled_image=None, overwrite=False):
    """
    Perform the rescaling: Multiply the residuals with f_rescale and add to model.
    This task obviously requires model and residuals, but also the image because CASA saves the clean beam only in the restored image.
    Inputs are the file names as strings.
    """

    # set default file name
    if ( rescaled_image == None ):
        rescaled_image = '.'.join(image_file.split('.')[:-1])+'.rescaled.fits'
    print("rescaled image file name: "+rescaled_image)

    # load data
    print("Loading data ...")
    image, psf, model, residual = load_cubes(image_file, psf_file, model_file, residual_file)

    # get image dimensions
    print("Checking image dimensions ...")
    n_x, n_y, n_chan = check_image_dimensions(psf.header)

    # clean beam
    clean_beam = calculate_clean_beam(image.header, n_x, n_y)

    # rescaled image
    print("Creating rescaled cube ...")
    rescaled = fits.PrimaryHDU(data=np.full_like(image.data, np.nan), header=image.header)
    rescaled.header.add_history('Correcting for clean beam/dirty beam mismatch by residual scaling.')

    # rescale single channel
    if ( n_chan == None ):
        print("Rescaling image ...")
        f_rescale      = get_f_rescale(psf.data, psf.header, image.header)
        rescaled.data  = model.data + f_rescale*residual.data
        rescaled.header.add_history('The residual scaling factor is '+str(f_rescale))

    # rescale multiple channels with the respective factor
    else:
        for chan in np.arange(n_chan):
            print("Rescaling channel "+str(chan)+" of "+str(n_chan), end='\r')
            f_rescale           = get_f_rescale(psf.data[chan], clean_beam, n_x, n_y)
            rescaled.data[chan] = model.data[chan] + f_rescale*residual.data[chan]
            rescaled.header.add_history('The residual scaling factor of channel '+str(chan)+' is '+str(f_rescale))

    # save rescaled image
    rescaled.writeto(rescaled_image, overwrite=overwrite)


####################################################################################################
