# -*- coding: utf-8 -*-
# Copyright (c) 2016, Almar Klein

"""
This module implements functionality to detect available Python
interpreters. This is done by looking at common locations, the Windows
registry, and conda's environment list.
"""

import sys
import os

from .pythoninterpreter import EXE_DIR, PythonInterpreter, versionStringToTuple
from .inwinreg import get_interpreters_in_reg
from .. import paths


def get_interpreters(minimumVersion=None):
    """ get_interpreters(minimumVersion=None)
    Returns a list of PythonInterpreter instances.
    If minimumVersion is given, return only the interprers with at least that
    version, and also sort the result by version number.
    """
    
    # Get Python interpreters
    if sys.platform.startswith('win'):
        pythons = _get_interpreters_win()
    else:
        pythons = _get_interpreters_posix()
    pythons = set([PythonInterpreter(p) for p in pythons])
    
    # Get conda paths
    condas = set([PythonInterpreter(p) for p in _get_interpreters_conda()])
    
    # Get relative interpreters
    relative = set([PythonInterpreter(p) for p in _get_interpreters_relative()])
    
    # Get Pyzo paths
    pyzos = set([PythonInterpreter(p) for p in _get_interpreters_pyzo()])
    
    # Get pipenv paths
    pipenvs = set([PythonInterpreter(p) for p in _get_interpreters_pipenv()])
    
    # Almost done
    interpreters = set.union(pythons, condas, relative, pyzos, pipenvs)
    minimumVersion = minimumVersion or '0'
    return _select_interpreters(interpreters, minimumVersion)


def _select_interpreters(interpreters, minimumVersion):
    """ Given a list of PythonInterpreter instances, return a list with
    the interpreters selected that are valid and have their version equal
    or larger than the given minimimVersion. The returned list is sorted
    by version number.
    """
    if not isinstance(minimumVersion, str):
        raise ValueError('minimumVersion in get_interpreters must be a string.')
    # Remove invalid interpreters
    interpreters = [i for i in interpreters if i.version]
    # Remove the ones below the reference version
    if minimumVersion is not None:
        refTuple = versionStringToTuple(minimumVersion)
        interpreters = [i for i in interpreters if (i.version_info >= refTuple)]
    # Return, sorted by version
    return sorted(interpreters, key=lambda x:x.version_info)


def _get_interpreters_win():
    found = []
    
    # Query from registry
    for v in get_interpreters_in_reg():
        found.append(v.installPath() )
    
    # Check common locations
    for rootname in ['C:/', '~/',
                     'C:/program files/', 'C:/program files (x86)/', 'C:/ProgramData/',
                     '~/appdata/local/programs/python/',
                     '~/appdata/local/continuum/', '~/appdata/local/anaconda/',
                     ]:
        rootname = os.path.expanduser(rootname)
        if not os.path.isdir(rootname):
            continue
        for dname in os.listdir(rootname):
            if dname.lower().startswith(('python', 'pypy', 'miniconda', 'anaconda')):
                found.append(os.path.join(rootname, dname))
    
    # Normalize all paths, and remove trailing backslashes
    found = [os.path.normcase(os.path.abspath(v)).strip('\\') for v in found]
    
    # Append "python.exe" and check if that file exists
    found2 = []
    for dname in found:
        for fname in ('python.exe', 'pypy.exe'):
            exename = os.path.join(dname, fname)
            if os.path.isfile(exename):
                found2.append(exename)
                break
    
    # Returnas set (remove duplicates)
    return set(found2)


def _get_interpreters_posix():
    found=[]
    
    # Look for system Python interpreters
    for searchpath in ['/usr/bin','/usr/local/bin','/opt/local/bin']:
        searchpath = os.path.expanduser(searchpath)
        
        # Get files
        try:
            files = os.listdir(searchpath)
        except Exception:
            continue
        
        # Search for python executables
        for fname in files:
            if fname.startswith(('python', 'pypy')) and not fname.count('config'):
                if len(fname) < 16:
                    # Get filename and resolve symlink
                    filename = os.path.join(searchpath, fname)
                    filename = os.path.realpath(filename)
                    # Seen on OS X that was not a valid file
                    if os.path.isfile(filename):
                        found.append(filename)
    
    # Look for user-installed Python interpreters such as pypy and anaconda
    for rootname in ['~', '/usr/local']:
        rootname = os.path.expanduser(rootname)
        if not os.path.isdir(rootname):
            continue
        for dname in os.listdir(rootname):
            if dname.lower().startswith(('python', 'pypy', 'miniconda', 'anaconda')):
                for fname in ('bin/python', 'bin/pypy'):
                    exename = os.path.join(rootname, dname, fname)
                    if os.path.isfile(exename):
                        found.append(exename)
    
    # Remove pythonw, pythonm and the like
    found = set(found)
    for path in list(found):
        if path.endswith(('m', 'w')) and path[:-1] in found:
            found.discard(path)
    
    # Return as set (remove duplicates)
    return set(found)


def _get_interpreters_pyzo():
    """ Get a list of known Pyzo interpreters.
    """
    pythonname = 'python' + '.exe' * sys.platform.startswith('win')
    exes = []
    for d in paths.pyzo_dirs():
        for fname in [  os.path.join(d, 'bin', pythonname + '3'),
                        os.path.join(d, pythonname), ]:
            if os.path.isfile(fname):
                exes.append(fname)
                break
    return exes


def _get_interpreters_conda():
    """ Get known conda environments
    """
    if sys.platform.startswith('win'):
        pythonname = 'python' + '.exe'
    else:
        pythonname = 'bin/python'
    
    exes = []
    filename = os.path.expanduser('~/.conda/environments.txt')
    if os.path.isfile(filename):
        for line in open(filename, 'rt').readlines():
            line = line.strip()
            exe_filename = os.path.join(line, pythonname)
            if line and os.path.isfile(exe_filename):
                exes.append(exe_filename)
    return exes


def _get_interpreters_pipenv():
    """ Get known pipenv environments
    """
    if sys.platform.startswith('win'):
        pythonname = 'Scripts\\python' + '.exe'
    else:
        pythonname = 'bin/python'
    
    exes = []
    for basedir in [os.path.join(os.path.expanduser('~'), '.virtualenvs')]:
        if os.path.isdir(basedir):
            for d in os.listdir(basedir):
                exe_filename = os.path.join(basedir, d, pythonname)
                if os.path.isfile(exe_filename):
                    exes.append(exe_filename)
    return exes


def _get_interpreters_relative():
    """ Get interpreters relative to our prefix and the parent directory.
    This allows Pyzo to be shipped inside a pre-installed conda env.
    """
    pythonname = 'python' + '.exe' * sys.platform.startswith('win')
    exes = []
    for d in ['.', '..']:
        for fname in [  os.path.join(d, 'bin', pythonname),
                        os.path.join(d, pythonname), ]:
            filename = os.path.abspath(os.path.join(EXE_DIR, fname))
            if os.path.isfile(filename):
                exes.append(fname)
                break
    return exes


if __name__ == '__main__':
    for pi in get_interpreters():
        print(pi)

