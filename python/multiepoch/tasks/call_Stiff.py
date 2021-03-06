#!/usr/bin/env python

# Mojo imports
from mojo.jobs.base_job import BaseJob
from traitlets import Unicode, Bool, Float, Int, CUnicode, CBool, CFloat, CInt, Instance, Dict, List, Integer
from mojo.jobs.base_job import BaseJob, IO, IO_ValidationError
from mojo.context import ContextProvider

import os
import sys
import subprocess
import time
import pandas as pd
from despymisc.miscutils import elapsed_time

# Multi-epoch
import multiepoch.utils as utils
import multiepoch.contextDefs as contextDefs
from multiepoch import file_handler as fh

# JOB INTERNAL CONFIGURATION
STIFF_EXE = 'stiff'
BKLINE = "\\\n"
DETNAME = 'det'

class Job(BaseJob):

    """
    Stiff call for the multi-epoch pipeline
    """

    class Input(IO):

        """
        Stiff call for the multi-epoch pipeline
        """
        ######################
        # Positional Arguments
        # 1. Tilename amd association file and assoc dictionary
        assoc      = Dict(None,help="The Dictionary containing the association file",argparse=False)
        assoc_file = CUnicode('',help="Input association file with CCDs information",input_file=True,
                              argparse={ 'argtype': 'positional', })
        # Optional Arguments
        tilename     = Unicode(None, help="The Name of the Tile Name to query",argparse=True)
        tilename_fh = CUnicode('',  help="Alternative tilename handle for unique identification default=TILENAME")
        tiledir     = Unicode(None, help='The output directory for this tile')
        execution_mode_stiff  = CUnicode("tofile",help="Stiff excution mode",
                                         argparse={'choices': ('tofile','dryrun','execute')})
        stiff_parameters      = Dict({},help="A list of parameters to pass to Stiff",
                                     argparse={'nargs':'+',})
        stiff_conf = CUnicode(help="Optional Stiff configuration file")

        doBANDS  = List(['all'],help="BANDS to processs (default=all)",argparse={'nargs':'+',})
        detname  = CUnicode(DETNAME,help="File label for detection image, default=%s." % DETNAME)
        nthreads = CInt(1,help="Number of threads to use in stiff/psfex/swarp")
        
        # Add DECam shape?
        DECam_mask = Bool(False, help="Push DECam Mask on files")

        ## TODO
        # Define color set from command-line option
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
        def _argparse_postproc_stiff_parameters(self, v):
            return utils.arglist2dict(v, separator='=')

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
        # 0. Prepare the context
        self.prewash()
        # 1. Run stiff
        self.run_stiff()
        if self.ctx.DECam_mask:
            self.logger.info("Will run stiff for DECam mask images")
            self.run_stiff(DECam_mask=True)


    def run_stiff(self,DECam_mask=False):

        # 2. get the update stiff parameters  --
        stiff_parameters = self.ctx.get('stiff_parameters', {})
        cmd_list = self.get_stiff_cmd_list(DECam_mask)
        
        # 3. check execution mode and write/print/execute commands accordingly --------------
        execution_mode = self.input.execution_mode_stiff

        if execution_mode == 'tofile':
            bkline  = self.ctx.get('breakline',BKLINE)
            # The file where we'll write the commands
            if DECam_mask:
                cmdfile = fh.get_stiff_cmd_file(self.input.tiledir, self.input.tilename_fh+"_DECam")
            else:
                cmdfile = fh.get_stiff_cmd_file(self.input.tiledir, self.input.tilename_fh)

            self.logger.info("Will write stiff call to: %s" % cmdfile)
            with open(cmdfile, 'w') as fid:
                fid.write(bkline.join(cmd_list)+'\n')
                fid.write('\n')

        elif execution_mode == 'dryrun':
           self.logger.info("For now we only print the commands (dry-run)")
           self.logger.info(' '.join(cmd_list))

        elif execution_mode == 'execute':
            logfile = fh.get_stiff_log_file(self.input.tiledir, self.input.tilename_fh)
            log = open(logfile,"w")
            self.logger.info("Will proceed to run the stiff call now:")
            self.logger.info("Will write to logfile: %s" % logfile)
            t0 = time.time()
            cmd  = ' '.join(cmd_list)
            self.logger.info("Executing stiff for tile:%s " % self.input.tilename_fh)
            self.logger.info("%s " % cmd)

            # We can get away using shell=True on OSX
            status = subprocess.call(cmd,shell=True,stdout=log, stderr=log)
            if status != 0:
                raise ValueError(" ERROR while running Stiff, check logfile: %s " % logfile)
            self.logger.info("Total stiff time %s" % elapsed_time(t0))
        else:
            raise ValueError('Execution mode %s not implemented.' % execution_mode)
        return


    def get_stiff_parameter_set(self,**kwargs):

        """
        Set the Stiff default options and have the options to
        overwrite them with kwargs to this function.
        """
        stiff_parameters = {
            "NTHREADS"    : self.ctx.nthreads,
            "DESCRIPTION" : "'Pseudo Color of coadded image for DES tile %s'" % self.ctx.tilename,
        }
        stiff_parameters.update(kwargs)
        return stiff_parameters


    def get_CSET(self):

        # Define the color filter sets we'd like to use, by priority depending on what BANDS will be combined
        cset1 = ['i','r','g']
        cset2 = ['z','r','g']
        cset3 = ['z','i','g']
        cset4 = ['z','i','r']
        csets = (cset1,cset2,cset3,cset4)
        CSET = False
        for color_set in csets:
            if CSET: break
            inset = list( set(color_set) & set(self.ctx.doBANDS))
            if len(inset) == 3:
                CSET = color_set

        if not CSET:
            self.logger.info("WARNING: Could not find a suitable filter set for color image")
            return 
        return CSET

    def get_stiff_cmd_list(self,DECam_mask=False):

        """ Make a color tiff of the TILENAME using stiff"""


        CSET = self.get_CSET()

        self.logger.info("assembling commands for Stiff call")
        if DECam_mask:
            self.logger.info("Will use DECam_mask=True")


        
        if self.ctx.NBANDS < 3:
            self.logger.info("WARINING: Not enough filters to create color image")
            self.logger.info("WARINING: No color images will be created")
            return 
        
        # The update parameters set
        pars = self.get_stiff_parameter_set(**self.input.stiff_parameters)
        # Set the output name of the color tiff file
        if DECam_mask:
            pars["OUTFILE_NAME"] = fh.get_color_file(self.input.tiledir, self.input.tilename_fh+'_DEcam')
        else:
            pars["OUTFILE_NAME"] = fh.get_color_file(self.input.tiledir, self.input.tilename_fh)

        # The Stiff configuration file
        if self.input.stiff_conf == '':
            self.ctx.stiff_conf = fh.get_configfile('stiff')
            self.logger.info("Will use Stiff default configuration file: %s" % self.ctx.stiff_conf)
        
        cmd_list = []
        cmd_list.append("%s" % STIFF_EXE)
        for BAND in CSET:
            if DECam_mask:
                sci_fits = fh.get_mef_file(self.input.tiledir,self.input.tilename_fh+'_DECam',BAND)
            else:
                sci_fits = fh.get_mef_file(self.input.tiledir,self.input.tilename_fh,BAND)
            cmd_list.append( "%s" % sci_fits)


        cmd_list.append("-c %s" % self.ctx.stiff_conf)
        for param,value in pars.items():
            cmd_list.append("-%s %s" % (param,value))
        return cmd_list

    def __str__(self):
        return 'Creates the call to Stiff'

if __name__ == '__main__':
    from mojo.utils import main_runner
    job = main_runner.run_as_main(Job)

