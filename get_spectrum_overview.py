# simple script to get a spectrum
#################################

def get_spectrum_overview(image, position=None, out=None):

    # define images: image, model, residual
    fname, fext = os.path.splitext(image)
    images = ['.'.join(fname.split('.')[:-1])+'.'+imtype+'.fits' for imtype in ['image','model','residual']]
    colors   = ['blue', 'green', 'red']

    # set position
    if ( position == None ):
        raise NotImplementedError("No default yet. Please give astropy.SkyCoord position.")

    # load spectra
    ##############

    spectra = []
    if ( fext == '.fits' ):
        for image in tqdm(images):

            image_data   = fits.open(image)[0].data
            image_header = fits.open(image)[0].header
            image_wcs    = WCS(image)

            # get spectrum
            posx,posy,posv = image_wcs.all_world2pix(position.ra.value, position.dec.value, 0,1)
            freq = [image_wcs.all_pix2world(0, 0, v, 1)[2]*u.Hz for v in np.arange(len(image_data))]
            freq = [f.to(u.GHz) for f in freq]
            posx = int(np.round(posx))
            posy = int(np.round(posy))
            data = (image_data[:,posy,posx]*u.Jy).to(u.mJy)
            spectra.append([image.split('.')[-2] ,freq, data])

    else:
        # use casa to load spectra with ia.getchunk
        raise Warning("Not a FITS image. Assuming CASA image.")
        raise NotImplementedError("CASA images are not implemented yet.")
        # for image in tqdm(images):
        #     ia.open(image)
        #     data = ia.getchunk( *conversion necessary*)
        #     ia.done()


    # plot
    ######

    # set up figure and axes
    fig = plt.figure(figsize=(10,8))
    fig.subplots_adjust(hspace=0)
    ax1 = plt.subplot2grid((5,1), (0,0), rowspan=3)
    ax1.xaxis.set_visible(False)
    ax2 = plt.subplot2grid((5,1), (3,0), rowspan=2) #, sharex=ax1)
    ax12 = ax1.twinx()
    ax22 = ax2.twinx()

    # plot spectra
    for idx, spectrum in enumerate(spectra):
        ax1.step([s.value for s in spectrum[1]], spectrum[2], where='mid', label=tex_escape(spectrum[0]), color=colors[idx])
        ax2.step([s.value for s in spectrum[1]], spectrum[2], where='mid', label=tex_escape(spectrum[0]), color=colors[idx])
    ax1.set_xlim([freq[0].value,freq[-1].value])
    ax2.set_xlim([freq[0].value,freq[-1].value])

    # set axis limits
    marg_im   = (abs(np.nanmax(spectra[0][2])) if abs(np.nanmax(spectra[0][2])) > abs(np.nanmin(spectra[0][2])) else abs(np.nanmin(spectra[0][2])))
    marg_res  = (abs(np.nanmax(spectra[2][2])) if abs(np.nanmax(spectra[2][2])) > abs(np.nanmin(spectra[2][2])) else abs(np.nanmin(spectra[2][2])))
    range_im   = [(np.nanmin(spectra[0][2])-0.1*marg_im).value,   (np.nanmax(spectra[0][2])+0.1*marg_im).value]
    range_res  = [(2.*np.nanmin(spectra[2][2])).value,  (2.*np.nanmax(spectra[2][2])).value]
    ax1.set_ylim(range_im)
    ax12.set_ylim(range_im)
    ax2.set_ylim(range_res)
    ax22.set_ylim(range_res)

    # set labels
    ax1.set_title(tex_escape(os.path.basename(fname)))
    ax2.set_xlabel('frequency [GHz]')
    ax1.set_ylabel('flux [mJy\,beam$^{-1}$]')
    ax12.set_ylabel('flux [mJy\,pix$^{-1}$]')
    ax2.set_ylabel('flux [mJy\,beam$^{-1}$]')
    ax22.set_ylabel('flux [mJy\,pix$^{-1}$]')
    ax1.legend(loc='best')
    plt.show()

    # save figure
    if not ( out == None ):
        fig.savefig(out, dpi=300, transparent=True, bbox_inches='tight')


####################################################################################################
