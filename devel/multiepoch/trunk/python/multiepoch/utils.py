
"""
Set of utility functions used across different multi-epoch tasks
"""

# Check if database handle is in the context
def check_dbh(ctx):

    from despydb import desdbi

    """ Check if we have a valid database handle (dbh)"""
    
    if 'dbh' not in ctx:
        try:
            db_section = ctx.get('db_section','db-desoper')
            print "# Creating db-handle to section: %s" % db_section
            ctx.dbh = desdbi.DesDbi(section=db_section)
        except:
            raise ValueError('ERROR: Database handler could not be provided for context.')
    else:
        print "# Will recycle existing db-handle"
    return ctx


def get_NP(MP):

    """ Get the number of processors in the machine
    if MP == 0, use all available processor
    """

    # For it to be a integer
    MP = int(MP)
    import multiprocessing
    if MP == 0:
        NP = multiprocessing.cpu_count()
    elif isinstance(MP,int):
        NP = MP
    else:
        raise ValueError('MP is wrong type: %s, integer type' % MP)
    return NP


# def get_NP_old(MP):
#     """ Get the number of processors in the machine"""
#     import multiprocessing
#     if type(MP) is bool:
#         NP = multiprocessing.cpu_count()
#     elif type(MP) is int:
#         NP = MP
#     else:
#         raise ValueError('MP is wrong type: %s, must be bool or integer type' % MP)
#     return NP

def create_local_archive(local_archive):

    import os

    """ Creates the local cache for the desar archive """
    if not os.path.exists(local_archive):
        print "# Will create LOCAL ARCHIVE at %s" % local_archive
        os.mkdir(local_archive)
    return


def get_local_weight_names(ctx,wgt_ext):

    """
    A common method to define the local weight names based on
    FILEPATH_LOCAL passed in the ctx, and wgt_ext
    """
    # A shortcut
    filepath_local = ctx.assoc['FILEPATH_LOCAL']
    Nfiles = len(filepath_local)
    # Define the wgt local filenames
    filepath_local_wgt = []
    for k in range(Nfiles):
        basename  = filepath_local[k].split(".fits")[0] 
        extension = filepath_local[k].split(".fits")[1:]
        local_wgt = "%s%s.fits" % (basename,wgt_ext)
        filepath_local_wgt.append(local_wgt)
    return filepath_local_wgt

def dict2arrays(dictionary):

    """
    Re-cast list in contained in a dictionary as numpy arrays
    """
    import numpy
    for key, value in dictionary.iteritems():
        if isinstance(value, list):
            dictionary[key] = numpy.array(value)
    return dictionary

