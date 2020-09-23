def is_casa_version(version):
    """Check CASA version

    Parameters
    ----------
    version : string
        A string specifying the CASA version.
        E.g. '5.5.0-31' or '5.3.0-139'

    Returns
    -------
    bool
        Returns True or False to be used in statements.

    """

    try:
        if ( casa['version'] == version ):
            return True
        else:
            raise Exception("You checked for CASA version "+version+", but "+casa['version']+" is installed.")
            return False
    except:
        raise Exception("Could not determine CASA version. This is probably because you use a CASA build with the old versioning system.")
