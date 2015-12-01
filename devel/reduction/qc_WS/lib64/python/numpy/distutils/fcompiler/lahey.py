import os
import sys

from numpy.distutils.cpuinfo import cpu
from numpy.distutils.fcompiler import FCompiler

class LaheyFCompiler(FCompiler):

    compiler_type = 'lahey'
    version_pattern =  r'Lahey/Fujitsu Fortran 95 Compiler Release (?P<version>[^\s*]*)'

    executables = {
        'version_cmd'  : ["lf95", "--version"],
        'compiler_f77' : ["lf95", "--fix"],
        'compiler_fix' : ["lf95", "--fix"],
        'compiler_f90' : ["lf95"],
        'linker_so'    : ["lf95","-shared"],
        'archiver'     : ["ar", "-cr"],
        'ranlib'       : ["ranlib"]
        }

    module_dir_switch = None  #XXX Fix me
    module_include_switch = None #XXX Fix me

    def get_flags_opt(self):
        return ['-O']
    def get_flags_debug(self):
        return ['-g','--chk','--chkglobal']
    def get_library_dirs(self):
        opt = []
        d = os.environ.get('LAHEY')
        if d:
            opt.append(os.path.join(d,'lib'))
        return opt
    def get_libraries(self):
        opt = []
        opt.extend(['fj9f6', 'fj9i6', 'fj9ipp', 'fj9e6'])
        return opt

if __name__ == '__main__':
    from distutils import log
    log.set_verbosity(2)
    from numpy.distutils.fcompiler import new_fcompiler
    compiler = new_fcompiler(compiler='lahey')
    compiler.customize()
    print compiler.get_version()