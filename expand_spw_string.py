# frequency to channel
######################


def expand_spw_string(MS_file, spw, return_type='string'):
    """
    Expands the spectral window selector * to a list of spws for the given MS.

    Parameters
    ----------
    MS_file : string
        CASA MS file name
    spw : string
        spw string using fequencies.
    return_type : string or dictionary list
        Returns the expanded spw string or a dictionary (when return_type=dict).

    Returns
    -------
    type
        Description of returned object.

    """

    if ( '*' in spw ):

        # parse CASA spw string
        freq_spws   = [x.split(':')[1] for x in spw.split(',')]
        freq_ranges = [x.split(';') for x in freq_spws]
        freq_edges  = [x.split('~') for y in freq_ranges for x in y]
        freq_edges  = [[float(re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", x)[0])*u.GHz for x in y] for y in freq_edges]

        # get corresponding spws
        spws = [[au.getScienceSpwsForFrequency(MS_file, str(freq)) for freq in x] for x in freq_edges]

        expanded_ranges = []
        for z,y in zip(freq_edges,spws):
            # within a single spw
            if ( y[0] == y[1] ):
                if not ( y[0] == [] ):
                    for x in y[0]:
                        expanded_ranges.append({'spw': x, 'range': z})
            # across spws
            else:
                ms.open(MS_file)
                ms_info = ms.getspectralwindowinfo()
                ms.done()
                for x in y[0]:
                    chan1freq = ms_info[str(x)]['Chan1Freq']
                    spwwidth  = ms_info[str(x)]['TotalWidth']
                    chanwidth = ms_info[str(x)]['ChanWidth']
                    if ( chanwidth > 0 ):
                        lastchanfreq = chan1freq+spwwidth
                    elif ( chanwidth < 0 ):
                        lastchanfreq = chan1freq-spwwidth
                    upper_spw_edge = max(chan1freq,lastchanfreq)*u.Hz
                    upper_spw_edge = upper_spw_edge - 5*abs(chanwidth)*u.Hz
                    expanded_ranges.append({'spw': x, 'range': [z[0],upper_spw_edge.to(u.GHz)]})
                for x in y[1]:
                    chan1freq = ms_info[str(x)]['Chan1Freq']
                    spwwidth  = ms_info[str(x)]['TotalWidth']
                    chanwidth = ms_info[str(x)]['ChanWidth']
                    if ( chanwidth > 0 ):
                        lastchanfreq = chan1freq+spwwidth
                    elif ( chanwidth < 0 ):
                        lastchanfreq = chan1freq-spwwidth
                    lower_spw_edge = min(chan1freq,lastchanfreq)*u.Hz
                    lower_spw_edge = lower_spw_edge + 5*abs(chanwidth)*u.Hz
                    expanded_ranges.append({'spw': x, 'range': [lower_spw_edge.to(u.GHz), z[1]]})

        # convert to CASA spw string
        spw_expanded = ''
        for i in expanded_ranges:
            spw_expanded += str(i['spw']) + ':' + str(i['range'][0].value) + '~' + str(i['range'][1].value) + str(i['range'][0].unit) + ','
        spw_expanded = spw_expanded[:-1]


        # return string or dictionery list
        if ( return_type == 'string' ):
            return spw_expanded
        elif ( return_type == 'dict' ):
            return expanded_ranges

    else:
        print("Nothing to expand. No '*' in sw string. Returning given spw.")
        return spw
