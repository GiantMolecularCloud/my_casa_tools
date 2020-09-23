####################################################################################################

# get noise estimate
####################

def get_noise(image):

    """
    Get the RMS noise of the image chunks and update the dataset info file.
    """

    casalog.post("*"*80)
    casalog.post("FUNCTION: GET NOISE ESTIMATE")
    casalog.post("*"*80)

    # get bunit
    bunit = imhead(imagename = image,
                mode  = 'get',
                hdkey = 'bunit'
                )

    # get noise from image
    stats=imstat(imagename=image, axes=[0,1])
    noises = [u.Quantity(str(x)+bunit) for x in stats['rms']]
    maxes  = [u.Quantity(str(x)+bunit) for x in stats['max']]
    snrs   = [m/n for m,n in zip(maxes,noises)]

    noise_median = u.Quantity(str(np.nanmedian(stats['rms']))+bunit)
    noise_std    = u.Quantity(str(np.nanstd(stats['rms']))+bunit)

    # plot stats
    plt.ion()
    fig,ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.plot([n.value for n in noises], color='r', linestyle='-', label='RMS')
    ax1.plot([m.value for m in maxes], color='g', linestyle='-', label='MAX')
    ax1.plot(np.nan, color='b', label='MAX SNR')
    ax2.plot(snrs, color='b', linestyle='-', label='MAX SNR')
    ax1.set_title(image.replace('_','$\_$'))
    ax1.set_xlabel('channel')
    ax1.set_ylabel('RMS ['+bunit+']')
    ax2.set_ylabel('SNR')
    ax1.legend(loc='upper right')
    ax1.grid(linestyle='--')
    ax2.grid(linestyle='..')
    plt.show()

    casalog.post("*"*80)
    casalog.post("MEDIAN NOISE: "+"{:.3f}".format(noise_median))
    casalog.post("STANDARD DEVIATION: "+"{:.3f}".format(noise_std))
    #casalog.post("UPDATED PROJECT_INFO.TXT")
    casalog.post("*"*80)

    return {'median': noise_median, 'stdev': noise_std}

####################################################################################################
