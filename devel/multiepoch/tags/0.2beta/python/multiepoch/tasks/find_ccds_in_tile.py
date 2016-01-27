#!/usr/bin/env python

import json
import numpy
import time
import despyastro

# Mojo imports
from mojo.jobs.base_job import BaseJob
from traitlets import Unicode, Bool, Float, Int, CUnicode, CBool, CFloat, CInt, Instance, Dict
from mojo.jobs.base_job import BaseJob, IO, IO_ValidationError
from mojo.context import ContextProvider
# Mutiepoch loads
import multiepoch.utils as utils
import multiepoch.contextDefs as contextDefs

from despyastro import tableio
from despymisc.miscutils import elapsed_time
npadd = numpy.core.defchararray.add

"""
Finds all of the CCCs in the IMAGE table that fall inside the (RACMI,RACMAX)
and (DECCMIN,DECCMAX) of a DES tile with a given set of extras SQL and/or
constraints provided into the function. 

Here we consider the simple case in which the CCDs are always smaller that the
DESTILE footprint, and therefore in order to have overlap at least on the
corners need to be inside. We'll consider the more general case where the any
TILE size (x or y) is smaller that the CCDs later.

In order for a CCD image to be considered inside the footprint of a DES tile it
needs to satifies:

either:

(RAC1,DEC1) or (RAC2,DECC2) or (RAC3,DECC3) or (RAC4,DECC4) have to been inside
(TILE_RACMIN,TILE_RACMAX) and (TILE_DECCMIN, TILE_DECCMAX), which are the min
and max boundaries of a DES tile.

The following driagram describes how this works:


                                                              (RAC4,DEC4)                          (RAC3,DEC3)
                                                               +----------------------------------+         
                                                               |                                  |         
          Corner4                                       Corner |                                  |         
            +----------------------------------------------+   |                                  |         
            |                                              |   |     Corner2                      |         
            |                                              |   |                                  |         
            |                DES TILE                      |   |  CCD outside (all corners out)   |         
            |                                              |   +----------------------------------+         
            |                                              |  (RAC1,DEC1)                          (RAC2,DEC2)
(RAC4,DEC4) |                        (RAC3,DEC3)           |       
   +--------|-------------------------+                    |
   |        | CCD inside              |                    |
   |        | (2 corners in)          |                    |
   |        |                         |                    |
   |        |                         |                    |
   |        |                         |                    |
   |        |                         |                    |
   +----------------------------------+                    |
(RAC1,DEC1)  |                       (RAC2,DEC2)            |
            |                                              |
            |                                  (RAC4,DEC4) |                        (RAC3,DEC3)
            |                                     +--------|-------------------------+
            |                                     |        |                         |
            |                                     |        |                         |
            +----------------------------------------------+                         |
          Corner1                                 |     Corner2                      |
                                                  |                                  |
                                                  | CCD inside (one corner in)       |
                                                 +----------------------------------+
                                                (RAC1,DEC1)                          (RAC2,DEC2) 

                                                
TILE_RACMIN  = min(RA Corners[1,4])
TILE_RACMAX  = man(RA Conrers[1,4])
TILE_DECCMIN = min(DEC Corners[1,4])
TILE_DECCMAX = man(DEC Corners[1,4])

**** Note1: We need to do something about inverting MIN,MAX when crossRAzero='Y' ****
**** Note2: We need add the general query, when the tile is smaller than the CCDs ****

Author: Felipe Menanteau, NCSA, Nov 2014.

"""


# THE QUERY TEMPLATE THAT IS RUN TO GET THE CCDs
# -----------------------------------------------------------------------------
#

QUERY = """
     SELECT
         {select_extras}
         file_archive_info.FILENAME,file_archive_info.PATH, image.BAND,
         image.RAC1,  image.RAC2,  image.RAC3,  image.RAC4,
         image.DECC1, image.DECC2, image.DECC3, image.DECC4
     FROM
         file_archive_info, wgb, image, ops_proctag,
         {from_extras} 
     WHERE
         file_archive_info.FILENAME  = image.FILENAME AND
         file_archive_info.FILENAME  = wgb.FILENAME  AND
         image.FILETYPE  = 'red' AND
         wgb.FILETYPE    = 'red' AND
         wgb.EXEC_NAME   = '{exec_name}' AND
         wgb.REQNUM      = ops_proctag.REQNUM AND
         wgb.UNITNAME    = ops_proctag.UNITNAME AND
         wgb.ATTNUM      = ops_proctag.ATTNUM AND
         ops_proctag.TAG = '{tagname}'
      AND
         {and_extras} 
         """

# DEFAULT PARAMETER VALUES -- Change from felipe.XXXXX --> XXXXX
# -----------------------------------------------------------------------------
SELECT_EXTRAS = "felipe.extraZEROPOINT.MAG_ZERO,"
FROM_EXTRAS   = "felipe.extraZEROPOINT"
AND_EXTRAS    = "felipe.extraZEROPOINT.FILENAME = image.FILENAME" 
# -----------------------------------------------------------------------------


class Job(BaseJob):

    '''
    DESDM multi-epoch pipeline : QUERY TILEINFO JOB
    ===============================================

    Required INPUT from context (ctx):
    ``````````````````````````````````
    - tile_edges: tuple of four floats (RACMIN, RACMAX, DECCMIN, DECCMAX)

    Writes as OUTPUT to context (ctx):
    ``````````````````````````````````
    - CCDS
    - ccdinfo

    '''
    
    class Input(IO):

        """Find the CCDs that fall inside a tile"""
    
        # Required inputs to run the job (in ctx, after loading files)
        # because we set the argparse keyword to False they are not interfaced
        # to the command line parser
        tileinfo = Dict(None, help="The json file with the tile information",
                        argparse=False)
        tilename = Unicode(None, help="The Name of the Tile Name to query",
                           argparse=False)

        # Required inputs when run as script
        #
        # variables with keyword input_file=True are loaded into the ctx
        # automatically when intializing the Job class if provided, Input
        # validation happens only thereafter
        # you can implement a implement a custom reader for you input file in
        # your input class, let's say for a variable like
        #
        # my_input_file = CUnicode('',
        #        help='My input file.',
        #        argparse={'argtype': 'positional'})
        #
        # def _read_my_input_file(self):
        #     do the stuff
        #     return a dict

        tile_geom_input_file = CUnicode('',help='The json file with the tile information',
                # declare this variable as input_file, this leads the content
                # of the file to be loaded into the ctx at initialization
                input_file=True,
                # set argtype=positional !! to make this a required positional
                # argument when using the parser
                argparse={ 'argtype': 'positional', })

        # Optional inputs, also when interfaced to argparse
        db_section    = CUnicode("db-destest",
                                 help="DataBase Section to connect", 
                                 argparse={'choices': ('db-desoper','db-destest', )} )
        archive_name  = CUnicode("desar2home",
                                 help="DataBase Archive Name section",)
        select_extras = CUnicode(SELECT_EXTRAS,
                                 help="string with extra SELECT for query",)
        and_extras    = CUnicode(AND_EXTRAS,
                                 help="string with extra AND for query",)
        from_extras   = CUnicode(FROM_EXTRAS,
                                 help="string with extra FROM for query",)
        tagname       = CUnicode('Y2T1_FIRSTCUT',
                                 help="TAGNAME for images in the database",)
        exec_name     = CUnicode('immask',
                                 help="EXEC_NAME for images in the database",)
        assoc_file    = CUnicode(None, 
                                 help="Name of the output ASCII association file where we will store the cccds information for coadd")
        assoc_json    = CUnicode(None, 
                                 help="Name of the output JSON association file where we will store the cccds information for coadd")
        plot_outname  = CUnicode(None, help="Output file name for plot, in case we want to plot",)

    def run(self):

        
        # Check for the db_handle
        self.ctx = utils.check_dbh(self.ctx)

        # Call the query built function
        print "# Getting CCD images within the tile definition"
        self.get_CCDS(**self.ctx.get_kwargs_dict())

        # Now we get the locations
        self.get_fitsfile_locations()
        

    def get_CCDS(self,**kwargs): 

        '''
        Get the database query that returns the ccds and store them in a numpy
        record array

        kwargs
        ``````
            - exec_name
            - tagname
            - select_extras
            - and_extras
            - from_extras
        '''
        select_extras = kwargs.get('select_extras', SELECT_EXTRAS)
        and_extras    = kwargs.get('and_extras',    AND_EXTRAS)
        from_extras   = kwargs.get('from_extras',   FROM_EXTRAS)
        tagname       = kwargs.get('tagname',       'Y2T1_FIRSTCUT')
        exec_name     = kwargs.get('exec_name',     'immask')


        # Create the tile_edges tuple structure
        self.ctx.tile_edges = (
            self.ctx.tileinfo['RACMIN'], self.ctx.tileinfo['RACMAX'],
            self.ctx.tileinfo['DECCMIN'],self.ctx.tileinfo['DECCMAX']
            )

        corners_and = [
                "((image.RAC1 BETWEEN %.10f AND %.10f) AND (image.DECC1 BETWEEN %.10f AND %.10f))\n" % self.ctx.tile_edges,
                "((image.RAC2 BETWEEN %.10f AND %.10f) AND (image.DECC2 BETWEEN %.10f AND %.10f))\n" % self.ctx.tile_edges,
                "((image.RAC3 BETWEEN %.10f AND %.10f) AND (image.DECC3 BETWEEN %.10f AND %.10f))\n" % self.ctx.tile_edges,
                "((image.RAC4 BETWEEN %.10f AND %.10f) AND (image.DECC4 BETWEEN %.10f AND %.10f))\n" % self.ctx.tile_edges,
                ]

        query = QUERY.format(
                tagname       = tagname,
                exec_name     = exec_name,
                select_extras = select_extras,
                from_extras   = from_extras,
                and_extras    = and_extras + ' AND\n (' + ' OR '.join(corners_and) + ')',
                )

        print "# Will execute the query:\n%s\n" %  query
        # Get the ccd images that are part of the DESTILE
        #self.ctx.CCDS = despyastro.genutil.query2dict_of_columns(query,dbhandle=self.ctx.dbh,array=True)
        t0 = time.time()
        self.ctx.CCDS = despyastro.genutil.query2rec(query,dbhandle=self.ctx.dbh)
        print "# Query time: %s" % elapsed_time(t0)
        print "# Nelem %s" % len(self.ctx.CCDS['FILENAME'])
        return 


    def get_fitsfile_locations(self):

        """ Find the location of the files in the des archive and https urls"""

        # Get all of the relevant kwargs
        kwargs = self.ctx.get_kwargs_dict()
        archive_name = kwargs.pop('archive_name', 'desar2home') # or get?

        # Number of images/filenames
        Nimages = len(self.ctx.CCDS['FILENAME'])

        # 1. Figure out the archive root and root_http variables, it returns
        # self.ctx.root_archive and self.ctx.root_https
        self.get_root_archive(archive_name)


        # 2. Construct an new dictionary that will store the
        # information required to associate files for co-addition
        self.ctx.assoc = {}
        self.ctx.assoc['MAG_ZERO'] = self.ctx.CCDS['MAG_ZERO']
        self.ctx.assoc['BAND']     = self.ctx.CCDS['BAND']
        self.ctx.assoc['FILENAME'] = self.ctx.CCDS['FILENAME']

        self.ctx.assoc['FILEPATH'] = npadd(self.ctx.CCDS['PATH'],"/")
        self.ctx.assoc['FILEPATH'] = npadd(self.ctx.assoc['FILEPATH'],self.ctx.CCDS['FILENAME'])

        # 3. Create the archive locations for each file
        path = [self.ctx.root_archive+"/"]*Nimages
        self.ctx.assoc['FILEPATH_ARCHIVE'] = npadd(path,self.ctx.assoc['FILEPATH'])

        # 4. Create the https locations for each file
        path = [self.ctx.root_https+"/"]*Nimages
        self.ctx.assoc['FILEPATH_HTTPS']   = npadd(path,self.ctx.assoc['FILEPATH'])
        
        return

    def get_root_archive(self,archive_name='desar2home'):

        """
        Get the root-archive  and root_https fron the database
        """

        cur = self.ctx.dbh.cursor()
        
        # root_archive
        query = "select root from ops_archive where name='%s'" % archive_name
        print "# Getting the archive root name for section: %s" % archive_name
        print "# Will execute the SQL query:\n********\n** %s\n********" % query
        cur.execute(query)
        self.ctx.root_archive = cur.fetchone()[0]
        print "# root_archive: %s" % self.ctx.root_archive

        # root_https
        query = "select val from ops_archive_val where name='%s' and key='root_https'" % archive_name
        print "# Getting root_https for section: %s" % archive_name
        print "# Will execute the SQL query:\n********\n** %s\n********" % query
        cur.execute(query)
        self.ctx.root_https = cur.fetchone()[0]
        print "# root_https:   %s" % self.ctx.root_https
        cur.close()
        return


    def write_assoc_file(self,assoc_file,names=['FILEPATH_ARCHIVE','FILENAME','BAND','MAG_ZERO']):

        variables = []
        for name in names:
            variables.append(self.ctx.assoc[name].tolist())
            
        print "# Writing CCDS files information to: %s" % assoc_file
        N = len(names)
        header =  "# " + "%s "*N % tuple(names)
        format =  "%-s "*N 
        tableio.put_data(assoc_file,tuple(variables), header=header, format=format)
        return


    def write_assoc_json(self,assoc_jsonfile,names=['FILEPATH_ARCHIVE','FILENAME','BAND','MAG_ZERO']):

        print "# Writing CCDS information to: %s" % assoc_jsonfile
        dict_assoc = {}
        for name in names:
            # Make them lists instead of rec arrays
            dict_assoc[name] =  self.ctx.assoc[name].tolist()
        o = open(assoc_jsonfile,"w")
        # Put in the proper container
        jsondict = {'assoc': dict_assoc}
        o.write(json.dumps(jsondict,sort_keys=False,indent=4))
        o.close()
        return


    def __str__(self):
        return 'find ccds in tile'


if __name__ == "__main__":

    # 0. take care of the sys arguments
    import sys
    args = sys.argv[1:]
    # 1. read the input arguments into the job input
    inp = Job.Input()
    # 2. load a context
    ctx = ContextProvider.create_ctx(**inp.parse_arguments(args))
    # 3. set the pipeline execution mode
    ctx['mojo_execution_mode'] = 'job as script'
    # 4. create an empty JobOperator with context
    from mojo import job_operator
    jo = job_operator.JobOperator(**ctx)
    # 5. run the job
    job_instance = jo.run_job(Job)
    # 6. dump the context if json_dump
    if jo.ctx.get('json_dump_file', ''):
        jo.json_dump_ctx()

    # 7 - Custom step, write the files as column-separated 
    # FELIPE: We need to decide whether want to write the assoc file
    # as json or space-separated ascii file.
    job_instance.write_assoc_file(ctx.assoc_file)
    job_instance.write_assoc_json(ctx.assoc_json)

    # 8 - Custom step, in Case we want to plot the overlapping CCDs
    if ctx.plot_outname:
        print "# Will plot overlapping tiles"
        from multiepoch.tasks.plot_ccd_corners_destile import Job as plot_job
        plot = plot_job(ctx=jo.ctx)
        plot()

    # ALTERNATIVELY the following code does exactly the same as the above
    '''
    from mojo.utils import main_runner
    job = main_runner.run_as_main(Job)
    '''