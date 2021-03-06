from despyastro import CCD_corners
import fitsio
import json
import multiepoch.utils as mutils

def define_tileinfo(tilename,**kwargs):

    # These are all of the inputs
    xsize       = kwargs.get('xsize')
    ysize       = kwargs.get('ysize')
    xsize_pix   = kwargs.get('xsize_pix',0)
    ysize_pix   = kwargs.get('ysize_pix',0)
    ra_center   = kwargs.get('ra_cent')
    dec_center  = kwargs.get('dec_cent')
    pixelscale  = kwargs.get('pixelscale',0.263) # in arsec/pixel
    units       = kwargs.get('units','arcmin')
    json_file   = kwargs.get('json_file',None)
    logger      = kwargs.get('logger',None)

    # Get the dimensions
    if xsize_pix > 0 and ysize_pix > 0 :
        NAXIS1 = xsize_pix
        NAXIS2 = ysize_pix
    else:
        NAXIS1, NAXIS2 = get_image_size(xsize,ysize, pixelscale=pixelscale, units=units)

    kw = {'pixelscale' : pixelscale,
          'ra_cent'    : ra_center,
          'dec_cent'   : dec_center,
          'NAXIS1'     : NAXIS1,
          'NAXIS2'     : NAXIS2}
    # create hdr and update corners
    header = create_header(**kw)

    # Now we write the json file (if defined) and get the tileinfo dictionary
    tileinfo = write_tileinfo_json(tilename,header,json_file,logger)

    return tileinfo

def write_tileinfo_json(tilename,hdr,json_file=None,logger=None):
    
    # TODO:
    # Make all keywords consisten with CCD_corners.update_DESDM_corners definitions
    # these are not consisten and should be fixed in destiling and when generating the tiles definitions
    tileinfo = {
        'RA_CENT'     : hdr['RA_CENT'],
        'DEC_CENT'    : hdr['DEC_CENT'],
        'CROSSRA0'    : hdr['CROSSRA0']}

    keys = ['NAXIS1','NAXIS2',
            'RAC1', 'RAC2', 'RAC3', 'RAC4',
            'DECC1', 'DECC2', 'DECC3', 'DECC4',
            'RACMIN','RACMAX','DECCMIN','DECCMAX',
            'RA_SIZE','DEC_SIZE',
            'PIXELSCALE',]
    for k in keys:
        tileinfo[k] = hdr[k]

    # Make it a json-like dictionary
    json_dict = {"tileinfo":tileinfo,
                 "tilename":tilename}

    # Now write if defined
    if json_file:
        mutils.pass_logger_info("# Writing json file to %s" % json_file,logger=logger)
        with open(json_file, 'w') as outfile:
            json.dump(json_dict, outfile, sort_keys = True, indent = 4)

    return tileinfo

def get_image_size(xsize,ysize, pixelscale=0.263, units='arcmin'):

    """ Computes the NAXIS1/NAXIS2 for a pixel scale and TAN projection """

    if units == 'arcsec':
        scale = pixelscale
    elif units == 'arcmin':
        scale = pixelscale/60.
    elif units == 'degree':
        scale = pixelscale/3600.
    elif units == 'pixel':
        scale = 1
    else:
        exit("ERROR: units not defined")
    NAXIS1 = int(xsize/scale)
    NAXIS2 = int(ysize/scale)
    return NAXIS1,NAXIS2
    

def create_header(**kwargs):


    """ Defines in full the tile header as a dictionary, notice that only CRVAL[1,2] are changing"""

    pixelscale = kwargs.get('pixelscale',0.263) # in arsec/pixel
    NAXIS1     = kwargs.get('NAXIS1')
    NAXIS2     = kwargs.get('NAXIS2')
    RA_CENT    = kwargs.get('ra_cent')  # in dec
    DEC_CENT   = kwargs.get('dec_cent') # in dec
    
    header_dict = {
        'NAXIS'   :  2,                      #/ Number of pixels along this axis
        'NAXIS1'  :  NAXIS1,            #/ Number of pixels along this axis
        'NAXIS2'  :  NAXIS2,            #/ Number of pixels along this axis
        'CTYPE1'  : 'RA---TAN',              #/ WCS projection type for this axis
        'CTYPE2'  : 'DEC--TAN',              #/ WCS projection type for this axis
        'CUNIT1'  : 'deg',                   #/ Axis unit
        'CUNIT2'  : 'deg',                   #/ Axis unit
        'CRVAL1'  :  RA_CENT,         #/ World coordinate on this axis
        'CRPIX1'  :  (NAXIS1+1)/2.0,    #/ Reference pixel on this axis
        'CD1_1'   :  -pixelscale/3600., #/ Linear projection matrix -- CD1_1 is negative
        'CD1_2'   :  0,                      #/ Linear projection matrix -- CD1_2 is zero, no rotation
        'CRVAL2'  :  DEC_CENT,        #/ World coordinate on this axis
        'CRPIX2'  :  (NAXIS2+1)/2.0,    #/ Reference pixel on this axis
        'CD2_1'   :  0,                      #/ Linear projection matrix -- CD2_1 is zero, no rotation
        'CD2_2'   :  pixelscale/3600.,  #/ Linear projection matrix -- CD2_2 is positive
        'PIXELSCALE' :  pixelscale  #/ Linear projection matrix -- CD2_2 is positive
        }

    header = fitsio.FITSHDR()
    for k, v in header_dict.items():
        new_record = {'name': k,'value':v}
        header.add_record(new_record)

    # Update corners
    header = CCD_corners.update_DESDM_corners(header,border=0,get_extent=True,verb=False)

    # We now compute RA_SIZE and DEC_SIZE
    if header['CROSSRA0'] == 'Y':
        # Maybe we substract 360 instead?
        RA_SIZE = abs( header['RACMAX'] - (header['RACMIN']-360))
    else:
        RA_SIZE = abs( header['RACMAX'] - header['RACMIN'])

    # And we add them as fitsio records
    new_record = {'name':'RA_SIZE','value':RA_SIZE}
    header.add_record(new_record)
    
    DEC_SIZE = abs( header['DECCMAX'] - header['DECCMIN'])
    new_record = {'name':'DEC_SIZE','value':DEC_SIZE}
    header.add_record(new_record)
    return header


