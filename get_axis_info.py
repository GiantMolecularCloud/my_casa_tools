def get_axis_info(image,axis):
    """
    Get the axis information (crpix, crval, cddelt) as astropy.units objects.

    Parameters
    ----------
    image : string
        File name of a fits image.
    axis : int
        Axis number. No default.

    Returns
    -------
    list
        Returns crpix, crval, cdelt with astropy units.

    """

    import astropy.units as u
    from astropy.io import fits

    header = fits.open(image)[0].header
    crpix = header['crpix'+str(axis)]*u.pix
    crval = u.Quantity(str(header['crval'+str(axis)])+header['cunit'+str(axis)])
    cdelt = u.Quantity(str(header['cdelt'+str(axis)])+header['cunit'+str(axis)])

    return crpix, crval, cdelt
