
"""
Set of utility functions used across different multi-epoch tasks
Felipe Menanteau, NCSA Jan 2015.

"""

import os
import sys

# Define order of HDU for MEF
SCI_HDU = 0
MSK_HDU = 1
WGT_HDU = 2

ARCHIVE_NAME = {'db-destest':'prodbeta',
                'db-desoper':'desar2home',
                }

def check_archive_name(ctx, logger=None):

    if 'archive_name' not in ctx:
        ctx.archive_name = ARCHIVE_NAME[ctx.db_section]
        mess = "Getting archive name for: %s, got: %s " % (ctx.db_section, ctx.archive_name)
        if logger: logger.info(mess)
        else: print mess
    return ctx

def read_tileinfo(geomfile,logger=None):
    import json
    mess = "Reading the tile Geometry from file: %s" % geomfile
    if logger: logger.info(mess)
    else: print mess
    with open(geomfile, 'rb') as fp:
        json_dict = json.load(fp)
    return json_dict


# Check if database handle is in the context
def check_dbh(ctx, logger=None):

    from despydb import desdbi
    import os

    """ Check if we have a valid database handle (dbh)"""
    
    if 'dbh' not in ctx:
        try:
            db_section = ctx.get('db_section')
            mess = "Creating db-handle to section: %s" % db_section
            if logger: logger.info(mess)
            else: print mess
            try:
                desservicesfile = ctx.get('desservicesfile',
                                          os.path.join(os.environ['HOME'],'.desservices.ini'))
                ctx.dbh = desdbi.DesDbi(desservicesfile, section=db_section)
            except:
                mess = "Cannot find des service file -- will try none"
                if logger: logger.warning(mess)
                else: print mess
                ctx.dbh = desdbi.DesDbi(section=db_section)
        except:
            raise
    else:
        mess = "Will recycle existing db-handle"
        if logger: logger.debug(mess)
        else: print mess
    return ctx


def get_NP(MP):

    """ Get the number of processors in the machine
    if MP == 0, use all available processor
    """
    import multiprocessing
    
    # For it to be a integer
    MP = int(MP)
    if MP == 0:
        NP = multiprocessing.cpu_count()
    elif isinstance(MP,int):
        NP = MP
    else:
        raise ValueError('MP is wrong type: %s, integer type' % MP)
    return NP

def create_local_archive(local_archive,logger=None):
    
    import os
    """ Creates the local cache directory for the desar archive data to be transfered"""
    if not os.path.exists(local_archive):
        message = "Will create LOCAL ARCHIVE at %s" % local_archive
        if logger: logger.info(message)
        else: print message
        os.mkdir(local_archive)
    return

def dict2arrays(dictionary):
    """
    Re-cast list in contained in a dictionary as numpy arrays
    """
    import numpy
    for key, value in dictionary.iteritems():
        if isinstance(value, list):
            dictionary[key] = numpy.array(value)
    return dictionary


def arglist2dict(inputlist,separator='='):
    """
    Re-shape a list of items ['VAL1=value1', 'VAL2=value2', etc]  into a dictionary
    dict['VAL1'] = value1, dict['VAL2'] = values, etc
    This is used to pass optional command-line argument option to the astromatic codes.
    
    We Re-pack as a dictionary the astromatic extras fron the command-line, if run as script
    """
    return dict( [ inputlist[index].split(separator) for index, item in enumerate(inputlist) ] )


def parse_comma_separated_list(inputlist):

    if inputlist[0].find(',') >= 0:
        return inputlist[0].split(',')
    else:
        return inputlist

def inDESARcluster(domain_name='cosmology.illinois.edu',logger=None,verb=False):

    import os,re
    """ Figure out if we are in the cosmology.illinois.edu cluster """
    
    uname    = os.uname()[0]
    hostname = os.uname()[1]
    mach     = os.uname()[4]
    
    pattern = r"%s$" % domain_name
        
    if re.search(pattern, hostname) and uname == 'Linux':
        LOCAL = True
        message = "Found hostname: %s, running:%s --> in %s cluster." % (hostname, uname, domain_name)
    else:
        LOCAL = False
        message = "Found hostname: %s, running:%s --> NOT in %s cluster." % (hostname, uname, domain_name)
                
    if logger: logger.debug(message)
    else:
        if verb: print message

    return LOCAL


def check_filepath_exist(filepath,logger=None):

    import os

    if not os.path.isdir(filepath):
        mess = "Filepath: %s is not a directory" % os.path.split(filepath)[0]
        if logger: logger(mess)
        return

    if not os.path.exists(os.path.split(filepath)[0]):
        mess = "Making: %s" % os.path.split(filepath)[0]
        os.makedirs(os.path.split(filepath)[0])
    else:
        mess = "Filepath: %s already exists" % os.path.split(filepath)[0]

    if logger: logger(mess)
    return

"""
A collection of utilities to call subprocess from multiprocess in python.
F. Menanteau, NCSA, Dec 2014
"""

def work_subprocess(cmd):

    import subprocess
    """ Dummy function to call in multiprocess"""

    # Make sure we pass the DYDL Library path for El Capitan and above
    args = cmd.split()
    return subprocess.call(args,env=os.environ.copy())

def work_subprocess_logging(tup):

    import subprocess
    """
    Dummy function to call in multiprocess and a
    logfile using a tuple as inputs
    """
    cmd,logfile = tup
    log = open(logfile,"w")
    #print "# Will write to logfile: %s" % logfile
    status = subprocess.call(cmd,shell=True,stdout=log, stderr=log)
    if status > 0:
        raise RuntimeError("\n***\nERROR while running, check logfile: %s\n***" % logfile)
    return status


def checkTABLENAMEexists(tablename,dbh=None,db_section=None,verb=False,logger=None):

    from despydb import desdbi

    """
    Check if exists. Tablename has to be a full owner.table_name format
    """

    # Make sure is all upper case
    tablename = tablename.upper()

    mess = "Checking if %s exists." % tablename
    if logger: logger.info(mess)
    elif verb: print mess

    if len(tablename.split("."))>1:
        TABLE_NAME = tablename.split(".")[1]
        OWNER = tablename.split(".")[0]
        query = "select count (*) from all_tables where table_name='%s' and owner='%s'" % (TABLE_NAME,OWNER)
    else:
        query = "select count (*) from all_tables where table_name='%s'" % tablename
        

    # Get a dbh if not provided
    if not dbh:
        dbh = desdbi.DesDbi(section=db_section)
        
    cur = dbh.cursor()
    cur.execute(query)
    count = cur.fetchone()[0]
    cur.close()
    
    if count >= 1:
        table_exists = True
    else:
        table_exists = False
    mess = "%s exists: %s " % (tablename,table_exists)
    if logger: logger.info(mess)
    elif verb: print mess
    return table_exists

def grant_read_permission(tablename,dbh, roles=['DES_READER','PROD_ROLE','PROD_READER_ROLE']):

    # Grand permission to a table
    cur = dbh.cursor()
    for role in roles:
        grant = "grant select on %s to %s" % (tablename,role)
        print "# Granting permission: %s" % grant
        cur.execute(grant)
    dbh.commit()
    cur.close()
    return

# Pass mess to debug logger or print
def pass_logger_debug(mess,logger=None):
    if logger: logger.debug(mess)
    else: print mess
    return

# Pass mess to info logger or print
def pass_logger_info(mess,logger=None):
    if logger: logger.info(mess)
    else: print mess
    return

# ----------------------------------------
# Update RAs when crosssing RA=0
def update_tileinfo_RAZERO(tileinfo):
    keys = ['RA_CENT','RAC1','RAC2','RAC3','RAC4','RACMIN','RACMAX']
    # We move the tile to RA=-180/+180
    if tileinfo['CROSSRA0'] == 'Y':
        for key in keys:
            if tileinfo[key] > 180: tileinfo[key] -= 360 
    return tileinfo

# Update the RAs for the CCDS query
# NOTE: We only use this when calculating distance using numpy
def update_CCDS_RAZERO(CCDS,crossrazero=False):
    import numpy
    keys = ['RA_CENT','RAC1','RAC2','RAC3','RAC4']
    # We move the tile to RA=180
    if crossrazero == 'Y' or crossrazero is True:
        for key in keys:
            CCDS[key] = numpy.where( CCDS[key] > 180, CCDS[key] - 360,  CCDS[key])
    return CCDS
# ----------------------------------------


def symlink_force(target, link_name,clobber=True):
    import os, errno
    try:
        os.symlink(target, link_name)
    except OSError, e:
        if e.errno == errno.EEXIST and clobber:
            os.remove(link_name)
            os.symlink(target, link_name)
        else:
            raise e
    return

def symlink_clobber(target, link_name, clobber=True):
    import os, errno

    if os.path.exists(link_name) and clobber:
        os.remove(link_name)
    else:
        os.symlink(target, link_name)
    return


# -----------------------------------------

def transfer_input_files(infodict, clobber, section, logger=None):

    from despymisc import http_requests
    
    """ Transfer the files contained in an info dictionary"""
    
    # Now get the files via http
    Nfiles = len(infodict['FILEPATH_HTTPS'])
    for k in range(Nfiles):
            
        url       = infodict['FILEPATH_HTTPS'][k]
        localfile = infodict['FILEPATH_LOCAL'][k]
        
        # Make sure the file does not already exists exits
        if not os.path.exists(localfile) or clobber:
            
            dirname   = os.path.dirname(localfile)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
                
            logger.info("Getting:  %s (%s/%s)" % (url,k+1,Nfiles))
            sys.stdout.flush()

            try:
                # Get a file using the $HOME/.desservices.ini credentials
                http_requests.download_file_des(url,localfile,section=section)
            except:
                warning = """WARNING: could not fetch file: %s using Request class. Will try using old fashion wget now"""  % url
                logger.info(warning)
                status = get_file_des_wget(url,localfile,section=section,clobber=clobber)
                if status > 0:
                    raise RuntimeError("\n***\nERROR while fetching file: %s\n\n" % url)

        else:
            logger.info("Skipping: %s (%s/%s) -- file exists" % (url,k+1,Nfiles))
        


def get_file_des_wget(url,localfile,section='http-desarchive',desfile=None,clobber=False):

    from despymisc import http_requests

    """
    A way to catch errors on http_requests.
    This whole fuction maybe you should go
    """

    # Read the credentials for the .desservices file
    USERNAME, PASSWORD, URLBASE = http_requests.get_credentials(desfile=desfile, section=section)
    WGET = "wget -q --user {user} --password {password} {url} -O {localfile}"
    kw = {'user':USERNAME, 'password':PASSWORD, 'url':url, 'localfile':localfile}
    cmd = WGET.format(**kw)
    if clobber:
        os.remove(localfile)
    
    status = work_subprocess(cmd)
    return status


#def fix_library_path():
#    """
#    we fix the OSX EL Capitan and above
#    DYLD_LIBRARY_PATH problem, but re-assigning it to DESDM_LIBRARY_PATH
#    """
#    
#    import platform
#    if platform.system() == 'Darwin' and int(platform.mac_ver()[0].split(".")[1]) >=1:
#        print "Fixing DYLD_LIBRARY_PATH"
#        print os.environ['DYLD_LIBRARY_PATH']
#        os.environ['DYLD_LIBRARY_PATH'] = os.environ['DESDM_LIBRARY_PATH']
#        print os.environ['DYLD_LIBRARY_PATH']
#    return

