
from mojo.utils import directory_handler
import os

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
        'list': 'list',
        'list/coadd': 'list/coadd',
        'list/mangle': 'list/mangle',
        'list/meds': 'list/meds',        
        'ctx': 'ctx',
        'log': 'log',
        'align': 'align',
        'coadd': 'coadd',
        'meds': 'meds',
        'inputs': 'inputs',
        'qa': 'qa',
        'qa/mangle': 'qa/mangle',
        'mangle_tiles':'mangle_tiles',
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
MSK_TYPE = 'msk'

# Mangle type
POL_EXT     = 'pol'
MANGLE_TYPE = 'mangle'

# MEDS
MEDS_TYPE = 'meds'

# Scamp/PSF/psfex/SEx types
PSFCAT_TYPE = 'psfcat'
PSFEX_TYPE  = 'psfex'
SEXCAT_TYPE = 'cat'
SEXSEG_TYPE = 'seg'
SCAMP_TYPE  = 'scamp'
SCAMPCAT_TYPE  = 'scampcat'
PSFEX_STARS_TYPE = 'psfex-starlist'

FITS_EXT  = 'fits'
HEAD_EXT  = 'head'
OHEAD_EXT = 'ohead'
AHEAD_EXT = 'ahead'
LIST_EXT  = 'list'
PSF_EXT   = 'psf'
XML_EXT   = 'xml'
YAML_EXT  = 'yaml'


# MULTIEPOCH FILENAME GENERATORS
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
    return dh.place_file(_me_fn(**fnkwargs), 'list/coadd') 

def get_wgt_list_file(tiledir, tilename, band):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'band':band, 'ftype':WGT_TYPE, 'ext':LIST_EXT}
    return dh.place_file(_me_fn(**fnkwargs), 'list/coadd')

def get_msk_list_file(tiledir, tilename, band):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'band':band, 'ftype':MSK_TYPE, 'ext':LIST_EXT}
    return dh.place_file(_me_fn(**fnkwargs), 'list/coadd')

# ------------------------------------
# 2. Output Coadd Files (sci/wgt/msk)
# ------------------------------------
def get_sci_fits_file(tiledir, tilename, band):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'band':band, 'ftype':SCI_TYPE, 'ext':FITS_EXT}
    return dh.place_file(_me_fn(**fnkwargs), 'coadd')

def get_wgt_fits_file(tiledir, tilename, band):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'band':band, 'ftype':WGT_TYPE, 'ext':FITS_EXT}
    return dh.place_file(_me_fn(**fnkwargs), 'coadd')

def get_msk_fits_file(tiledir, tilename, band):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'band':band, 'ftype':MSK_TYPE, 'ext':FITS_EXT}
    return dh.place_file(_me_fn(**fnkwargs), 'coadd')

def get_gen_fits_file(tiledir, tilename, band, type='gen'):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'band':band, 'ftype':type, 'ext':FITS_EXT}
    return dh.place_file(_me_fn(**fnkwargs), 'coadd')

# ------------------------------------
# 3. Misc files (log/fluxes/command)
# ------------------------------------
def get_flx_list_file(tiledir, tilename, band):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'band':band, 'ftype':FLX_TYPE, 'ext':LIST_EXT}
    return dh.place_file(_me_fn(**fnkwargs), 'list/coadd')

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
    return dh.place_file(filename, 'coadd')

def get_stiff_ptif_cmd_file(tiledir, tilename):
    dh = get_tiledir_handler(tiledir)
    filename = "%s_call_stiff_ptif.cmd" % tilename
    return dh.place_file(filename, 'aux')

def get_stiff_ptif_log_file(tiledir, tilename):
    dh = get_tiledir_handler(tiledir)
    filename = "%s_stiff_ptif.log" % tilename
    return dh.place_file(filename, 'log')

def get_color_file_ptif(tiledir, tilename):
    dh = get_tiledir_handler(tiledir)
    filename = "%s.ptif" % tilename
    return dh.place_file(filename, 'coadd')


# -----------------------------------------------------------------------------
#    ******* EXTINCTION FILES ********
def get_extinction_cmd_file(tiledir, tilename):
    dh = get_tiledir_handler(tiledir)
    filename = "%s_call_extinction.cmd" % tilename
    return dh.place_file(filename, 'aux')

def get_extinction_log_file(tiledir, tilename):
    dh = get_tiledir_handler(tiledir)
    filename = "%s_extinction.log" % tilename
    return dh.place_file(filename, 'log')

# -----------------------------------------------------------------------------
#    ******* HPIX FILES ********
def get_hpix_cmd_file(tiledir, tilename):
    dh = get_tiledir_handler(tiledir)
    filename = "%s_call_hpix.cmd" % tilename
    return dh.place_file(filename, 'aux')

def get_hpix_log_file(tiledir, tilename):
    dh = get_tiledir_handler(tiledir)
    filename = "%s_hpix.log" % tilename
    return dh.place_file(filename, 'log')



# -----------------------------------------------------------------------------
#     ***** SEX for PSF FILES *****
def get_psf_file(tiledir, tilename, band):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'band':band, 'ftype':PSFCAT_TYPE, 'ext':PSF_EXT}
    return dh.place_file(_me_fn(**fnkwargs), 'coadd')

def get_psfcat_file(tiledir, tilename, band):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'band':band, 'ftype':PSFCAT_TYPE, 'ext':FITS_EXT}
    return dh.place_file(_me_fn(**fnkwargs), 'coadd')

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

def get_psfex_stars_file(tiledir, tilename, band):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'band':band, 'ftype':PSFEX_STARS_TYPE, 'ext':FITS_EXT}
    return dh.place_file(_me_fn(**fnkwargs), 'coadd')

def get_psfxml_file(tiledir, tilename, band):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'band':band, 'ftype':PSFEX_TYPE, 'ext':XML_EXT}
    return dh.place_file(_me_fn(**fnkwargs), 'coadd')

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
    return dh.place_file(_me_fn(**fnkwargs), 'coadd')

def get_seg_file(tiledir, tilename, band):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'band':band, 'ftype':SEXSEG_TYPE, 'ext':FITS_EXT}
    return dh.place_file(_me_fn(**fnkwargs), 'coadd')

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
    return dh.place_file(_me_notype_fn(**fnkwargs), 'coadd')

def get_mef_cmd_file(tiledir, tilename,band=None):
    dh = get_tiledir_handler(tiledir)
    if band:
        filename = "%s_%s_call_coadd_assemble.cmd" % (tilename,band)
    else:
        filename = "%s_call_coadd_asseble.cmd" % tilename
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

# ----------------------------------
#  ******** DEPTH PLOTS ************

def get_plot_depth_file(tiledir, tilename):
    dh = get_tiledir_handler(tiledir)
    filename = "%s_depth.pdf" % tilename
    return dh.place_file(filename, 'aux')

def get_plot_depth_fits(tiledir, tilename,band):
    dh = get_tiledir_handler(tiledir)
    filename = "%s_%s_depth.fits" % (tilename,band)
    return dh.place_file(filename, 'aux')

def get_plot_depth_fraction(tiledir, tilename):
    dh = get_tiledir_handler(tiledir)
    filename = "%s_depth.json" % tilename
    return dh.place_file(filename, 'aux')


def get_ccd_plot_file(tiledir, tilename, search_type=None):
    dh = get_tiledir_handler(tiledir)
    if search_type:
        filename = "%s_overlap_%s.pdf" % (tilename,search_type)
    else:
        filename = "%s_overlap.pdf" % tilename
    return dh.place_file(filename, 'aux')

def get_ccd_plot_file_image(tiledir, tilename, search_type=None):
    dh = get_tiledir_handler(tiledir)
    if search_type:
        filename = "%s_overlap_image_%s.pdf" % (tilename,search_type)
    else:
        filename = "%s_overlap_image.pdf" % tilename
    return dh.place_file(filename, 'aux')



#  ***** SCAMP FILES *****

# The list of CCD finalcut red catalogs that go into an exposure-based catalog
def get_catlist_file(tiledir, tilename, exposure):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'exposure':exposure, 'ftype':SCAMPCAT_TYPE, 'ext':LIST_EXT}
    return dh.place_file(_me_exposure_fn(**fnkwargs), 'list/coadd') 

# The list of head CCD associated to the red catalogs
def get_headlist_file(tiledir, tilename, exposure):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'exposure':exposure, 'ftype':SCAMP_TYPE, 'ext':LIST_EXT}
    return dh.place_file(_me_exposure_fn(**fnkwargs), 'list/coadd') 

# The combined exposure-based set of SEx fits catalogs
def get_expcat_file(tiledir, tilename, exposure):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'exposure':exposure, 'ftype':SCAMPCAT_TYPE, 'ext':FITS_EXT}
    return dh.place_file(_me_exposure_fn(**fnkwargs), 'align') 

# The scamp output for the combined exposure-based head file
def get_exphead_file(tiledir, tilename, exposure):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'exposure':exposure, 'ftype':SCAMPCAT_TYPE, 'ext':HEAD_EXT}
    return dh.place_file(_me_exposure_fn(**fnkwargs), 'align') 

# The scamp output for the combined exposure-based head file
def get_expahead_file(tiledir, tilename, exposure):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'exposure':exposure, 'ftype':SCAMPCAT_TYPE, 'ext':AHEAD_EXT}
    return dh.place_file(_me_exposure_fn(**fnkwargs), 'align') 

# The scamp input list of exposure-based catalogs
def get_expcat_list_file(tiledir, tilename):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'ftype':SCAMPCAT_TYPE, 'ext':LIST_EXT}
    return dh.place_file(_me_noband_fn(**fnkwargs), 'list/coadd') 

# The scamp input list of exposure-based head output files
def get_expcat_list_head(tiledir, tilename):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'ftype':SCAMPCAT_TYPE, 'ext':HEAD_EXT}
    return dh.place_file(_me_noband_fn(**fnkwargs), 'list/coadd') 

# The output scamp xml file
def get_scamp_xml_file(tiledir, tilename):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'ftype':SCAMP_TYPE, 'ext':XML_EXT}
    return dh.place_file(_me_noband_fn(**fnkwargs), 'align') 

# Filenames to hold the command-line 
def get_combine_cats_cmd_file(tiledir, tilename):
    dh = get_tiledir_handler(tiledir)
    filename = "%s_call_combine_cats.cmd" % tilename
    return dh.place_file(filename, 'aux')

def get_split_head_cmd_file(tiledir, tilename):
    dh = get_tiledir_handler(tiledir)
    filename = "%s_call_split_head.cmd" % tilename
    return dh.place_file(filename, 'aux')

def get_scamp_cmd_file(tiledir, tilename):
    dh = get_tiledir_handler(tiledir)
    filename = "%s_call_scamp.cmd" % tilename
    return dh.place_file(filename, 'aux')

def get_scamp_log_file(tiledir, tilename,suffix='scamp'):
    dh = get_tiledir_handler(tiledir)
    filename = "%s_%s.log" % (tilename,suffix)
    return dh.place_file(filename, 'log')

# Default assoc name catlist
def get_default_assoc_file(tiledir, tilename,imagetype=None):
    dh = get_tiledir_handler(tiledir)
    if imagetype:
        filename = "%s_%s.assoc" % (tilename,imagetype)
    else:
        filename = "%s.assoc" % tilename
    return dh.place_file(filename, 'aux')

def get_default_cats_file(tiledir, tilename):
    dh = get_tiledir_handler(tiledir)
    filename = "%s_cats.list" % tilename
    return dh.place_file(filename, 'aux')

def get_default_scampcats_file(tiledir, tilename):
    dh = get_tiledir_handler(tiledir)
    filename = "%s_scampcats.list" % tilename
    return dh.place_file(filename, 'aux')

def get_default_scampheads_file(tiledir, tilename):
    dh = get_tiledir_handler(tiledir)
    filename = "%s_scampheads.list" % tilename
    return dh.place_file(filename, 'aux')

def get_scamp_plots(tiledir, tilename,plotnames):
    dh = get_tiledir_handler(tiledir)
    filenames = []
    for plotname in plotnames:
        filename = "%s_%s" % (tilename,plotname)
        filenames.append(dh.place_file(filename, 'qa'))
    return filenames

def get_scamp_plots_relative(tilename,plotnames):
    filenames = []
    for plotname in plotnames:
        filename = "%s_%s" % (tilename,plotname)
        filenames.append(os.path.join('qa',filename))
    return filenames

# --------------------
#    Mangle files
# --------------------

def get_mangle_list_red(tiledir, tilename, band):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'band':band, 'ftype':'mangle-red', 'ext':LIST_EXT}
    return dh.place_file(_me_fn(**fnkwargs), 'list/mangle') 

def get_mangle_list_me(tiledir, tilename, band):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'band':band, 'ftype':'mangle-me', 'ext':LIST_EXT}
    return dh.place_file(_me_fn(**fnkwargs), 'list/mangle') 

def get_poltiles_name(tileid,version='Y3A1v1'):
    """ Example: Y3A1v1_tiles_10s.124050.pol"""
    return "%s_tiles_10s.%s.pol" % (version, tileid)

def get_poltolys_name(tileid,version='Y3A1v1'):
    """ Example: Y3A1v1_tolys_10s.124050.pol"""
    return "%s_tolys_10s.%s.pol" % (version, tileid)

def get_poltiles(tiledir,tileid,version='Y3A1v1'):
    dh = get_tiledir_handler(tiledir)
    filename = get_poltiles_name(tileid,version='Y3A1v1')
    return dh.place_file(filename, 'mangle_tiles')

def get_poltolys(tiledir,tileid,version='Y3A1v1'):
    dh = get_tiledir_handler(tiledir)
    filename = get_poltolys_name(tileid,version='Y3A1v1')
    return dh.place_file(filename, 'mangle_tiles')

def get_mangle_plot(tiledir,tilename,band,number=None):
    dh = get_tiledir_handler(tiledir)
    filename = "%s_%s_mangle-%s.png" % (tilename,band,number)
    return dh.place_file(filename, 'qa/mangle')

def get_mangle_cmd_file(tiledir, tilename):
    dh = get_tiledir_handler(tiledir)
    filename = "%s_call_mangle.cmd" % tilename
    return dh.place_file(filename, 'aux')

def get_mangle_log_file(tiledir, tilename):
    dh = get_tiledir_handler(tiledir)
    filename = "%s_mangle.log" % tilename
    return dh.place_file(filename, 'mangle')

#  --------------
#    MEDS file
#  --------------
def get_meds_list_nwg(tiledir, tilename, band):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'band':band, 'ftype':'nwg', 'ext':LIST_EXT}
    return dh.place_file(_me_fn(**fnkwargs), 'list/meds') 

def get_meds_list_bkg(tiledir, tilename, band):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'band':band, 'ftype':'bkg', 'ext':LIST_EXT}
    return dh.place_file(_me_fn(**fnkwargs), 'list/meds') 

def get_meds_list_seg(tiledir, tilename, band):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'band':band, 'ftype':'seg', 'ext':LIST_EXT}
    return dh.place_file(_me_fn(**fnkwargs), 'list/meds') 

def get_meds_tileconf(tiledir, tilename, band):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'band':band, 'ftype':'fileconf', 'ext':YAML_EXT}
    return dh.place_file(_me_fn(**fnkwargs), 'meds')

def get_meds_cmd_file(tiledir, tilename):
    dh = get_tiledir_handler(tiledir)
    filename = "%s_call_meds.cmd" % tilename
    return dh.place_file(filename, 'aux')


def get_meds_log_file(tiledir, tilename,band=None):
    dh = get_tiledir_handler(tiledir)
    if band:
        filename = "%s_%s_meds.log" % (tilename,band)
    else:
        filename = "%s_meds.log" % tilename
    return dh.place_file(filename, 'log')

def get_meds_output(tiledir, tilename, band):
    dh = get_tiledir_handler(tiledir)
    fnkwargs = {'base':tilename, 'band':band, 'ftype':MEDS_TYPE, 'ext':FITS_EXT}
    return dh.place_file(_me_fn(**fnkwargs), 'meds')
    

# Push mask DECam
def get_mask_DECam_cmd_file(tiledir, tilename):
    dh = get_tiledir_handler(tiledir)
    filename = "%s_mask_DECam.cmd" % tilename
    return dh.place_file(filename, 'aux')


# -----------------------
def get_configfile(exec_name,date=None,ext='config'):

    if date:
        CONFIG_DATE = date
    else:
        CONFIG_DATE = os.environ['MULTIEPOCH_CONFIG_DATE']
    return os.path.join(os.environ['MULTIEPOCH_DIR'],'etc','%s_%s.%s' % (CONFIG_DATE,exec_name,ext))
