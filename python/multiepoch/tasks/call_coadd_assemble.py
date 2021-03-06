#!/usr/bin/env python

# Mojo imports
from mojo.jobs.base_job import BaseJob
from traitlets import Unicode, Bool, Float, Int, CUnicode, CBool, CFloat, CInt, Instance, Dict, List, Integer
from mojo.jobs.base_job import BaseJob, IO, IO_ValidationError
from mojo.context import ContextProvider

from mojo.jobs.base_job import BaseJob
import os,sys

from despymisc.miscutils import elapsed_time
import time
import pandas as pd
from collections import OrderedDict

import multiepoch.utils as utils
from multiepoch import metools
import multiepoch.contextDefs as contextDefs
from multiepoch import file_handler as fh
from despyfits import coadd_assemble 

DETNAME = 'det'
COADD_ASSEMBLE_EXE = 'coadd_assemble'
BKLINE = "\\\n"
MAGBASE = 30.0

class Job(BaseJob):

    """
    Create the MEF files based on the comb_sci, comb_msk and comb_wgt files using coadd_assemble
    """

    class Input(IO):
        
        """
        Create and prepare MEF for the coadded fits files
        """

        ######################
        # Required inputs
        # 1. Association file and assoc dictionary
        assoc      = Dict(None,help="The Dictionary containing the association file",argparse=False)
        assoc_file = CUnicode('',help="Input association file with CCDs information",input_file=True,
                              argparse={ 'argtype': 'positional', })
        #####################
        # Optional Arguments
        tilename     = Unicode(None, help="The Name of the Tile Name to query",argparse=True)
        tilename_fh  = CUnicode('',  help="Alternative tilename handle for unique identification default=TILENAME")
        tiledir      = Unicode(None, help="The output directory for this tile")
        tileid       = CInt(-1,    help="The COADDTILE_ID for the Tile Name")
        clobber_MEF  = Bool(False, help="Cloober the existing MEF fits")
        cleanupSWarp = Bool(False, help="Clean-up SWarp files")
        execution_mode_MEF  = CUnicode("tofile",help="excution mode",
                                       argparse={'choices': ('tofile','dryrun','execute')})
        doBANDS       = List(['all'],help="BANDS to processs (default=all)",argparse={'nargs':'+',})
        detname       = CUnicode(DETNAME,help="File label for detection image, default=%s." % DETNAME)
        magbase       = CFloat(MAGBASE, help="Zero point magnitude base for SWarp, default=%s." % MAGBASE)

        # Weight for mask
        weight_for_mask  = Bool(False, help="Create coadded weight for mask creation")

        # image to use to interpolate
        interp_image = Unicode('MSK', help="Image to use to define interpolation (MSK or WGT)",
                               argparse={'choices': ('MSK','WGT')})
        # zipper params
        xblock    = CInt(10, help="Block size of zipper in x-direction")
        yblock    = CInt(3, help="Block size of zipper in y-direction")
        add_noise = Bool(False,help="Add Poisson Noise to the zipper")
        ydilate   = CInt(0,help="Dilate pixels in the y-axis")
        maxcols   = CInt(100, help="Widest feature to interpolate.  Default=None means no limit.")
        mincols   = CInt(1,help="Narrowest feature to interpolate.")
                        
        region_file = CUnicode('',help="Write ds9 region file with interpolated region")
        # Keep zeros in SCI (yes/no)
        keep_sci_zeros = Bool(False, help="Keep zeros in SCI frame")

        # Add DECam shape?
        DECam_mask = Bool(False, help="Push DECam Mask on files")
        
        # Logging -- might be factored out
        stdoutloglevel = CUnicode('INFO', help="The level with which logging info is streamed to stdout",
                                  argparse={'choices': ('DEBUG','INFO','CRITICAL')} )
        fileloglevel   = CUnicode('INFO', help="The level with which logging info is written to the logfile",
                                  argparse={'choices': ('DEBUG','INFO','CRITICAL')} )

        # Function to read ASCII/panda framework file (instead of json)
        # Comment if you want to use json files
        def _read_assoc_file(self):
            mydict = {}
            df = pd.read_csv(self.assoc_file,sep=' ')
            mydict['assoc'] = {col: df[col].values.tolist() for col in df.columns}
            return mydict

        def _validate_conditional(self):
            if self.tilename_fh == '':
                self.tilename_fh = self.tilename

        # To also accept comma-separeted input lists
        def _argparse_postproc_doBANDS(self, v):
            return utils.parse_comma_separated_list(v)

    def prewash(self):

        """ Pre-wash of inputs, some of these are only needed when run as script"""

        # Re-cast the ctx.assoc as dictionary of arrays instead of lists
        self.ctx.assoc  = utils.dict2arrays(self.ctx.assoc)
        # Get the BANDs information in the context if they are not present
        if self.ctx.get('gotBANDS'):
            self.logger.info("BANDs already defined in context -- skipping")
        else:
            self.ctx.update(contextDefs.get_BANDS(self.ctx.assoc, detname=self.ctx.detname,logger=self.logger,doBANDS=self.ctx.doBANDS))

        # Check info OK
        self.logger.info("BANDS:   %s" % self.ctx.BANDS)
        self.logger.info("doBANDS: %s" % self.ctx.doBANDS)
        self.logger.info("dBANDS:  %s" % self.ctx.dBANDS)

    def run(self):

        t0 = time.time()

        # Prepare the context
        self.prewash()

        # check execution mode and write/print/execute commands accordingly --------------
        execution_mode = self.ctx.execution_mode_MEF
        
        # Build the args dictionary for all BANDS
        args = self.assemble_args()

        if execution_mode == 'execute':
            for BAND in self.ctx.dBANDS:
                self.logger.info("Running coadd_assemble for BAND:%s --> %s" % (BAND,args[BAND]['outname']))
                args[BAND]['DEFAULT_MAXCOLS'] = args[BAND]['maxcols']
                args[BAND]['DEFAULT_MINCOLS'] = args[BAND]['mincols']
                coadd_assemble.merge(**args[BAND])

        elif execution_mode == 'dryrun':
            for BAND in self.ctx.dBANDS:
                cmd = self.get_merge_cmd(args[BAND])
                self.logger.info(" ".join(cmd))
                
        elif execution_mode == 'tofile':
            bkline  = self.ctx.get('breakline',BKLINE)
            cmdfile = fh.get_mef_cmd_file(self.input.tiledir, self.input.tilename_fh)
            self.logger.info("Will write coadd_assemble call to: %s" % cmdfile)
            with open(cmdfile, "w") as fid:
                for BAND in self.ctx.dBANDS:
                    cmd = self.get_merge_cmd(args[BAND])
                    fid.write(bkline.join(cmd)+'\n')
                    fid.write('\n\n')
        else:
            raise ValueError('Execution mode %s not implemented.' % execution_mode)

        if self.input.cleanupSWarp and execution_mode == 'execute':
            self.cleanup_SWarpFiles(execute=True)
            
        if self.ctx.DECam_mask:
            self.push_mask(execution_mode)
            
        self.logger.info("Coadd Assemble Creation Total time: %s" % elapsed_time(t0))

        return

    def push_mask(self,execution_mode='tofile'):

        """ Push the DECam shape into the coadd_assemble files"""


        tiledir     = self.ctx.tiledir
        tilename_fh = self.ctx.tilename_fh

        if execution_mode == 'execute':
            for BAND in self.ctx.dBANDS:
                filename  = fh.get_mef_file(tiledir, tilename_fh, BAND)
                outname   = fh.get_mef_file(tiledir, tilename_fh+"_DECam", BAND)
                self.logger.info("Pushing mask for %s" % filename)
                metools.addDECamMask(filename,outname,ext=0)

                
        elif execution_mode == 'dryrun':
            for BAND in self.ctx.dBANDS:
                filename  = fh.get_mef_file(tiledir, tilename_fh, BAND)
                outname   = fh.get_mef_file(tiledir, tilename_fh+"_DECam", BAND)
                print "push_mask %s %s --hdu 0" % (filename,outname)

        elif execution_mode == 'tofile':
            bkline  = self.ctx.get('breakline',BKLINE)
            cmdfile = fh.get_mask_DECam_cmd_file(tiledir, tilename_fh)
            self.logger.info("Will write push mask call to: %s" % cmdfile)
            with open(cmdfile, "w") as fid:
                for BAND in self.ctx.dBANDS:
                    cmdlist = ['push_mask']
                    filename  = fh.get_mef_file(tiledir, tilename_fh, BAND)
                    outname   = fh.get_mef_file(tiledir, tilename_fh+"_DECam", BAND)
                    cmdlist.append("%s" % filename)
                    cmdlist.append("%s" % outname)
                    cmdlist.append("--hdu 0")
                    fid.write(bkline.join(cmdlist)+'\n')
                    fid.write('\n\n')
        else:
            raise ValueError('Execution mode %s not implemented.' % execution_mode)

        return
        

    def get_merge_cmd(self,args):

        cmd = []
        cmd.append(COADD_ASSEMBLE_EXE)

        for key in args.keys():
            if key == 'logger':
                continue
            if isinstance(args[key],bool) and args[key] is True:
                cmd.append("--%s" % key)
            elif args[key] is not False:
                cmd.append("--%s %s" % (key,args[key]))
        return cmd


    def assemble_args(self):
        """ Build the args dictionary to be pass as **kwrgs or comand-line """
        args = {}
        tiledir     = self.input.tiledir
        tilename_fh = self.input.tilename_fh
        for BAND in self.ctx.dBANDS:
            outname = fh.get_mef_file(tiledir, tilename_fh, BAND)
            args[BAND] = {'sci_file': fh.get_sci_fits_file(tiledir, tilename_fh, BAND),                          
                          'wgt_file': fh.get_wgt_fits_file(tiledir, tilename_fh, BAND),
                          'outname' : outname,
                          'logger'  : self.logger,
                          'clobber' : self.ctx.clobber_MEF,
                          'xblock'  : self.ctx.xblock,
                          'yblock'  : self.ctx.yblock,
                          'ydilate'  : self.ctx.ydilate,
                          'add_noise' : self.ctx.add_noise,
                          'mincols'  : self.ctx.mincols,
                          'maxcols'  : self.ctx.maxcols,
                          'interp_image': self.ctx.interp_image,
                          'magzero'  : self.ctx.magbase,
                          'tilename' : self.ctx.tilename,
                          'tileid' : self.ctx.tileid,
                          'keep_sci_zeros' : self.ctx.keep_sci_zeros,
                          }

            if self.ctx.keep_sci_zeros is False:
                args[BAND]['no-keep_sci_zeros'] = True

            if self.input.weight_for_mask:
                args[BAND]['msk_file'] = fh.get_msk_fits_file(tiledir, tilename_fh, BAND)

            if BAND == 'det':
                args[BAND]['band'] = BAND

        return args

    def cleanup_SWarpFiles(self,execute=False):

        # Sortcuts for less typing
        tiledir     = self.input.tiledir
        tilename_fh = self.input.tilename_fh

        for BAND in self.ctx.dBANDS:
            SWarpfiles = [fh.get_sci_fits_file(tiledir,tilename_fh, BAND),
                          fh.get_wgt_fits_file(tiledir,tilename_fh, BAND),
                          fh.get_gen_fits_file(tiledir,tilename_fh, BAND, type='tmp_sci') # tmp_sci.fits
                          ]
            if self.input.weight_for_mask:
                SWarpfiles.append(fh.get_msk_fits_file(tiledir,tilename_fh, BAND))
            
            for sfile in SWarpfiles:
                self.logger.info("Cleaning up %s" % sfile)
                if execute:
                    try:
                        os.remove(sfile)
                    except:
                        self.logger.info("Warning: cannot remove %s" % sfile)

        return

    def __str__(self):
        return 'Create MEF file for a coadded TILE fron SCI/MSK/WGT image planes using coadd_assemble'
 
if __name__ == '__main__':
    from mojo.utils import main_runner
    job = main_runner.run_as_main(Job)




