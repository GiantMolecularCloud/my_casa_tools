def angle_to_parsec(angle, source=None, distance=None):
    if (source==None) and (distance==None):
        raise Exception("Need to provide either source name or distance.")

    if ( source == 'NGC253' ):
        distance = 3.5*u.Mpc
    if ( source == 'GC' ):
        distance = 8178*u.pc

    return (distance*np.sin(angle)).to(u.pc)
