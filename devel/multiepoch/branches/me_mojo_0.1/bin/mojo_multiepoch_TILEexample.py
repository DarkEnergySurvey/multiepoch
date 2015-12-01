#!/usr/bin/env python

"""
Make sure we do:
 setup -v -r ~/DESDM-Code/devel/multiepoch/branches/me_mojo_0.1
"""

from mojo import job_operator
import os,sys
import time
from despymisc.miscutils import elapsed_time

# Take time
t0 = time.time()

# 0. Initialize Job Operator
jo  = job_operator.JobOperator('multiepoch.config_db-destest')

# 1.  Get the tile information from the table
jo.run_job('multiepoch.jobs.query_tileinfo', tilename='DES2246-4457', coaddtile_table='felipe.coaddtile_new')

# 2. Set up the output directory
jo.run_job('multiepoch.jobs.set_tile_directory', outputpath=os.environ['HOME']+"/TILEBUILDER_TEST")

# 3. Get the CCDs inside the tile
SELECT_EXTRAS = "felipe.extraZEROPOINT.MAG_ZERO,"
FROM_EXTRAS   = "felipe.extraZEROPOINT"
AND_EXTRAS    = "felipe.extraZEROPOINT.FILENAME = image.FILENAME" 
jo.run_job('multiepoch.jobs.find_ccds_in_tile',
           select_extras = SELECT_EXTRAS,
           from_extras = FROM_EXTRAS,
           and_extras = AND_EXTRAS,
           tagname='Y2T1_FIRSTCUT',
           exec_name='immask',
           )

# 4a. Plot the corners -- all  bands (default)
jo.run_job('multiepoch.jobs.plot_ccd_corners_destile')

# 4b. Plot the corners -- single band
#jo.run_job('multiepoch.jobs.plot_ccd_corners_destile', band='r')
#jo.run_job('multiepoch.jobs.plot_ccd_corners_destile', band='i')

# 5 Collect files for swarp
jo.run_job('multiepoch.jobs.find_fitsfiles_location',archive_name='desar2home')

# 6. Retrieve the files -- if remotely
LOCAL_DESAR = os.path.join(os.environ['HOME'],'LOCAL_DESAR')
jo.run_job('multiepoch.jobs.get_fitsfiles',local_archive=LOCAL_DESAR)

# 7 Create custom weights for SWarp
jo.run_job('multiepoch.jobs.make_SWarp_weights',clobber_weights=False, MP_weight=4)

# Prepare call to SWarp
swarp_params={
    "NTHREADS"     :8,
    "COMBINE_TYPE" : "AVERAGE",    
    "PIXEL_SCALE"  : 0.263}
# 8a. The simple call, no custom weights (deprecated?)
#jo.run_job('multiepoch.jobs.call_SWarp',swarp_parameters=swarp_params, DETEC_COMBINE_TYPE="CHI-MEAN",swarp_execution_mode='execute')
#jo.run_job('multiepoch.jobs.call_SWarp',swarp_parameters=swarp_params, DETEC_COMBINE_TYPE="CHI-MEAN",swarp_execution_mode='dryrun')

# 8b. The Custom call with custom weights 
jo.run_job('multiepoch.jobs.call_SWarp_CustomWeights',swarp_parameters=swarp_params, DETEC_COMBINE_TYPE="CHI-MEAN",swarp_execution_mode='execute')
#jo.run_job('multiepoch.jobs.call_SWarp_CustomWeights',swarp_parameters=swarp_params, DETEC_COMBINE_TYPE="CHI-MEAN",swarp_execution_mode='dryrun')

# 9. Create the color images using stiff
stiff_params={
    "NTHREADS"  :8,
    "COPYRIGHT" : "NCSA/DESDM",
    "WRITE_XML" : "N"}
jo.run_job('multiepoch.jobs.call_Stiff',stiff_parameters=stiff_params, stiff_execution_mode='execute')
#jo.run_job('multiepoch.jobs.call_Stiff',stiff_parameters=stiff_params, stiff_execution_mode='dryrun')

# 10. Set up the catalogs names for SEx and psfex
jo.run_job('multiepoch.jobs.set_catNames')

# 11. make the SEx psf Call
#jo.run_job('multiepoch.jobs.call_SExpsf',SExpsf_execution_mode='dryrun')
jo.run_job('multiepoch.jobs.call_SExpsf',SExpsf_execution_mode='execute',MP_SEx=8)

# 11. Run  psfex
#jo.run_job('multiepoch.jobs.call_psfex',psfex_parameters={"NTHREADS"  :8,},psfex_execution_mode='dryrun')
jo.run_job('multiepoch.jobs.call_psfex',psfex_parameters={"NTHREADS"  :8,},psfex_execution_mode='execute')

# 12. Run SExtractor un dual mode
#jo.run_job('multiepoch.jobs.call_SExDual',SExDual_parameters={"MAG_ZEROPOINT":30,}, SExDual_execution_mode='dryrun',MP_SEx=8)
jo.run_job('multiepoch.jobs.call_SExDual',SExDual_parameters={"MAG_ZEROPOINT":30,}, SExDual_execution_mode='execute',MP_SEx=8)

# 13. Create the MEF fits files in the formar we like
jo.run_job('multiepoch.jobs.make_MEFs',clobber_MEF=False)

print "# Grand Total time: %s" % elapsed_time(t0)