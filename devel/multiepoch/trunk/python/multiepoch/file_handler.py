
from mojo.utils import directory_handler

# DIRECTORIES
# -----------------------------------------------------------------------------
# - tiledir 
#   |+ aux_dir 
#   |+ ctx_dir 
#   |+ log_dir 
#   |+ products_dir 
#   `- ..

TILEDIR_SUBDIRECTORIES = {
        'aux': 'aux',
        'ctx': 'ctx',
        'log': 'log',
        'products': 'products',
        }

def get_tiledir_handler(tiledir, logger=None):
    ''' Provides a DirectoryHandler for the tile directory
    '''
    dh = directory_handler.DirectoryHandler([tiledir,],
            subdirs=TILEDIR_SUBDIRECTORIES, logger=logger,)
    return dh


# FILENAMES 
# -----------------------------------------------------------------------------
# SWarp types
SCI_TYPE = 'sci'
WGT_TYPE = 'wgt'
FLX_TYPE = 'flx'
MEF_TYPE = 'mef'
MSK_TYPE = 'msk'

# PSF/psfex/SEx types
PSFCAT_TYPE = 'psfcat'
PSFEX_TYPE  = 'psfex'
SEXCAT_TYPE = 'cat'
SEXSEG_TYPE = 'seg'
SCAMP_TYPE  = 'scamp'

FITS_EXT = 'fits'
LIST_EXT = 'list'
PSF_EXT  = 'psf'
XML_EXT  = 'xml'

# scamp types
CCDCAT_TYPE = 'ccdcat'
EXPCAT_TYPE = 'expcat'

# GENERIC MULTIEPOCH FILENAME GENERATOR 

_GENERIC_FILENAMEPATTERN          = "{base}_{band}_{ftype}.{ext}"
_GENERIC_FILENAMEPATTERN_NOBAND   = "{base}_{ftype}.{ext}"
_GENERIC_FILENAMEPATTERN_NOFTYPE  = "{base}_{band}.{ext}"
_GENERIC_FILENAMEPATTERN_EXPOSURE = "{base}_{exposure}_{ftype}.{ext}"


def _me_fn(**kwargs):
    ''' the generic multiepoch filename generator '''
    return _GENERIC_FILENAMEPATTERN.format(**kwargs)

def _me_noband_fn(**kwargs):
    ''' the generic multiepoch filename generator without band '''
    return _GENERIC_FILENAMEPATTERN_NOBAND.format(**kwargs)

def _me_notype_fn(**kwargs):
    ''' the generic multiepoch filename generator without ftype'''
    return _GENERIC_FILENAMEPATTERN_NOFTYPE.format(**kwargs)

def _me_exposure_fn(**kwargs):
    ''' the generic multiepoch filename generator for exposure=-based names'''
    return _GENERIC_FILENAMEPATTERN_EXPOSURE.format(**kwargs)

# FILENAME GENERATOR FUNCTIONS

#  ***** SWARP FILES *****
# -----------------------------------
# 1. Input List Names (sci/wgt/swg)
# -----------------------------------
def get_sci_list_file(tiledir, tilename, band):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'band':band, 'ftype':SCI_TYPE, 'ext':LIST_EXT}
    return dh.place_file(_me_fn(**fnkwargs), 'aux') 

def get_wgt_list_file(tiledir, tilename, band):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'band':band, 'ftype':WGT_TYPE, 'ext':LIST_EXT}
    return dh.place_file(_me_fn(**fnkwargs), 'aux')

def get_msk_list_file(tiledir, tilename, band):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'band':band, 'ftype':MSK_TYPE, 'ext':LIST_EXT}
    return dh.place_file(_me_fn(**fnkwargs), 'aux')

# ------------------------------------
# 2. Output Coadd Files (sci/wgt/msk)
# ------------------------------------
def get_sci_fits_file(tiledir, tilename, band):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'band':band, 'ftype':SCI_TYPE, 'ext':FITS_EXT}
    return dh.place_file(_me_fn(**fnkwargs), 'products')

def get_wgt_fits_file(tiledir, tilename, band):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'band':band, 'ftype':WGT_TYPE, 'ext':FITS_EXT}
    return dh.place_file(_me_fn(**fnkwargs), 'products')

def get_msk_fits_file(tiledir, tilename, band):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'band':band, 'ftype':MSK_TYPE, 'ext':FITS_EXT}
    return dh.place_file(_me_fn(**fnkwargs), 'products')

def get_gen_fits_file(tiledir, tilename, band, type='gen'):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'band':band, 'ftype':type, 'ext':FITS_EXT}
    return dh.place_file(_me_fn(**fnkwargs), 'products')

# ------------------------------------
# 3. Misc files (log/fluxes/command)
# ------------------------------------
def get_flx_list_file(tiledir, tilename, band):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'band':band, 'ftype':FLX_TYPE, 'ext':LIST_EXT}
    return dh.place_file(_me_fn(**fnkwargs), 'aux')

def get_swarp_log_file(tiledir, tilename):
    dh = get_tiledir_handler(tiledir)
    filename = "%s_swarp.log" % tilename
    return dh.place_file(filename, 'log')

def get_swarp_cmd_file(tiledir, tilename):
    dh = get_tiledir_handler(tiledir)
    filename = "%s_call_swarp.cmd" % tilename
    return dh.place_file(filename, 'aux')

# -----------------------------------------------------------------------------
#    ******* STIFF FILES ********
def get_stiff_cmd_file(tiledir, tilename):
    dh = get_tiledir_handler(tiledir)
    filename = "%s_call_stiff.cmd" % tilename
    return dh.place_file(filename, 'aux')

def get_stiff_log_file(tiledir, tilename):
    dh = get_tiledir_handler(tiledir)
    filename = "%s_stiff.log" % tilename
    return dh.place_file(filename, 'log')

def get_color_file(tiledir, tilename):
    dh = get_tiledir_handler(tiledir)
    filename = "%s.tiff" % tilename
    return dh.place_file(filename, 'products')


# -----------------------------------------------------------------------------
#     ***** SEX for PSF FILES *****
def get_psf_file(tiledir, tilename, band):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'band':band, 'ftype':PSFCAT_TYPE, 'ext':PSF_EXT}
    return dh.place_file(_me_fn(**fnkwargs), 'products')

def get_psfcat_file(tiledir, tilename, band):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'band':band, 'ftype':PSFCAT_TYPE, 'ext':FITS_EXT}
    return dh.place_file(_me_fn(**fnkwargs), 'products')

def get_sexpsf_cmd_file(tiledir, tilename):
    dh = get_tiledir_handler(tiledir)
    filename = "%s_call_SExpsf.cmd" % tilename
    return dh.place_file(filename, 'aux')

def get_sexpsf_log_file(tiledir, tilename,band=None):
    dh = get_tiledir_handler(tiledir)
    if band:
        filename = "%s_%s_SExpsf.log" % (tilename,band)
    else:
        filename = "%s_SExpsf.log" % tilename
    return dh.place_file(filename, 'log')

# -----------------------------------------
#    ****** PSFEX FILES *****

def get_psfxml_file(tiledir, tilename, band):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'band':band, 'ftype':PSFEX_TYPE, 'ext':XML_EXT}
    return dh.place_file(_me_fn(**fnkwargs), 'products')

def get_psfex_cmd_file(tiledir, tilename):
    dh = get_tiledir_handler(tiledir)
    filename = "%s_call_psfex.cmd" % tilename
    return dh.place_file(filename, 'aux')

def get_psfex_log_file(tiledir, tilename,band=None):
    dh = get_tiledir_handler(tiledir)
    if band:
        filename = "%s_%s_psfex.log" % (tilename,band)
    else:
        filename = "%s_psfex.log" % tilename
    return dh.place_file(filename, 'log')

# -----------------------------------------
#    ****** SEx Dual FILES *****

def get_cat_file(tiledir, tilename, band):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'band':band, 'ftype':SEXCAT_TYPE, 'ext':FITS_EXT}
    return dh.place_file(_me_fn(**fnkwargs), 'products')

def get_seg_file(tiledir, tilename, band):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'band':band, 'ftype':SEXSEG_TYPE, 'ext':FITS_EXT}
    return dh.place_file(_me_fn(**fnkwargs), 'products')

def get_SExdual_cmd_file(tiledir, tilename):
    dh = get_tiledir_handler(tiledir)
    filename = "%s_call_SExdual.cmd" % tilename
    return dh.place_file(filename, 'aux')

def get_SExdual_log_file(tiledir, tilename,band=None):
    dh = get_tiledir_handler(tiledir)
    if band:
        filename = "%s_%s_SExdual.log" % (tilename,band)
    else:
        filename = "%s_SExdual.log" % tilename
    return dh.place_file(filename, 'log')


# *** MEF (sci+msk+wgt files) ****
def get_mef_file(tiledir, tilename, band):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'band':band, 'ext':FITS_EXT}
    return dh.place_file(_me_notype_fn(**fnkwargs), 'products')

def get_mef_cmd_file(tiledir, tilename,band=None):
    dh = get_tiledir_handler(tiledir)
    if band:
        filename = "%s_%s_coadd_merge.cmd" % (tilename,band)
    else:
        filename = "%s_coadd_merge.cmd" % tilename
    return dh.place_file(filename, 'aux')


# ME prepare
def get_me_prepare_cmd_file(tiledir, tilename):
    dh = get_tiledir_handler(tiledir)
    filename = "%s_call_me_prepare.cmd" % tilename
    return dh.place_file(filename, 'aux')

def get_me_prepare_log_file(tiledir, tilename):
    dh = get_tiledir_handler(tiledir)
    filename = "%s_me_prepare.log" % tilename
    return dh.place_file(filename, 'log')

# -------------------------------------------------

def get_ccd_plot_file(tiledir, tilename):
    dh = get_tiledir_handler(tiledir)
    filename = "%s_overlap.pdf" % tilename
    return dh.place_file(filename, 'aux')



#  ***** SCAMP FILES *****

# The lit of CCD finalcut red catalos that go into an exposure-based catalog
def get_catlist_file(tiledir, tilename, exposure):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'exposure':exposure, 'ftype':CCDCAT_TYPE, 'ext':LIST_EXT}
    return dh.place_file(_me_exposure_fn(**fnkwargs), 'aux') 

def get_expcat_file(tiledir, tilename, exposure):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'exposure':exposure, 'ftype':EXPCAT_TYPE, 'ext':FITS_EXT}
    return dh.place_file(_me_exposure_fn(**fnkwargs), 'aux') 

def get_expcat_list_file(tiledir, tilename):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'ftype':EXPCAT_TYPE, 'ext':LIST_EXT}
    return dh.place_file(_me_noband_fn(**fnkwargs), 'aux') 

def get_combine_cats_cmd_file(tiledir, tilename):
    dh = get_tiledir_handler(tiledir)
    filename = "%s_call_combine_cats.cmd" % tilename
    return dh.place_file(filename, 'aux')

def get_scamp_xml_file(tiledir, tilename):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'ftype':SCAMP_TYPE, 'ext':XML_EXT}
    return dh.place_file(_me_noband_fn(**fnkwargs), 'products') 

def get_scamp_cmd_file(tiledir, tilename):
    dh = get_tiledir_handler(tiledir)
    filename = "%s_call_scamp.cmd" % tilename
    return dh.place_file(filename, 'aux')
