# -*- coding: utf-8 -*-
# Copyright (c) 2016, Almar Klein, Rob Reilink
#
# This file is distributed under the terms of the (new) BSD License.

""" Module paths

Get paths to useful directories in a cross platform manner. The functions
in this module are designed to be stand-alone, so that they can easily
be copied and used in code that does not want pyzo as a dependency.

This code was first part of pyzolib, and later moved to pyzo.

"""

# Notes:
# * site.getusersitepackages() returns a dir in roaming userspace on Windows
#   so better avoid that.
# * site.getuserbase() returns appdata_dir('Python', True)
# * See docstring: that's why the functions tend to not re-use each-other

import sys

ISWIN = sys.platform.startswith('win')
ISMAC = sys.platform.startswith('darwin')
ISLINUX = sys.platform.startswith('linux')

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3



# From pyzolib/paths.py (https://bitbucket.org/pyzo/pyzolib/src/tip/paths.py)
import sys
def is_frozen():
    """ is_frozen()
    Return whether this app is a frozen application (using e.g. cx_freeze).
    """
    return bool( getattr(sys, 'frozen', None) )



# From pyzolib/paths.py (https://bitbucket.org/pyzo/pyzolib/src/tip/paths.py)
import os, sys, tempfile
def temp_dir(appname=None, nospaces=False):
    """ temp_dir(appname=None, nospaces=False)
    Get path to a temporary directory with write access.
    If appname is given, a subdir is appended (and created if necessary).
    If nospaces, will ensure that the path has no spaces.
    """
    
    # Do it the Python way
    path = tempfile.gettempdir()
    
    # Try harder if we have to
    if nospaces and ' ' in path:
        if sys.platform.startswith('win'):
            for path in ['c:\\TEMP', 'c:\\TMP']:
                if os.path.isdir(path):
                    break
            if not os.path.isdir(path):
                os.mkdir(path)
        else:
            for path in ['/tmp', '/var/tmp']: # http://www.tuxfiles.org/linuxhelp/linuxdir.html
                if os.path.isdir(path):
                    break
            else:
                raise RuntimeError('Could not locate temporary directory.')
    
    # Get path specific for this app
    if appname:
        path = os.path.join(path, appname)
        if not os.path.isdir(path):
            os.mkdir(path)
    
    # Done
    return path



# From pyzolib/paths.py (https://bitbucket.org/pyzo/pyzolib/src/tip/paths.py)
import os
def user_dir():
    """ user_dir()
    Get the path to the user directory. (e.g. "/home/jack", "c:/Users/jack")
    """
    return os.path.expanduser('~')



# From pyzolib/paths.py (https://bitbucket.org/pyzo/pyzolib/src/tip/paths.py)
import os, sys
def appdata_dir(appname=None, roaming=False, macAsLinux=False):
    """ appdata_dir(appname=None, roaming=False,  macAsLinux=False)
    Get the path to the application directory, where applications are allowed
    to write user specific files (e.g. configurations). For non-user specific
    data, consider using common_appdata_dir().
    If appname is given, a subdir is appended (and created if necessary).
    If roaming is True, will prefer a roaming directory (Windows Vista/7).
    If macAsLinux is True, will return the Linux-like location on Mac.
    """
    
    # Define default user directory
    userDir = os.path.expanduser('~')
    
    # Get system app data dir
    path = None
    if sys.platform.startswith('win'):
        path1, path2 = os.getenv('LOCALAPPDATA'), os.getenv('APPDATA')
        path = (path2 or path1) if roaming else (path1 or path2)
    elif sys.platform.startswith('darwin') and not macAsLinux:
        path = os.path.join(userDir, 'Library', 'Application Support')
    # On Linux and as fallback
    if not (path and os.path.isdir(path)):
        path = userDir
    
    # Maybe we should store things local to the executable (in case of a
    # portable distro or a frozen application that wants to be portable)
    prefix = sys.prefix
    if getattr(sys, 'frozen', None): # See application_dir() function
        prefix = os.path.abspath(os.path.dirname(sys.executable))
    for reldir in ('settings', '../settings'):
        localpath = os.path.abspath(os.path.join(prefix, reldir))
        if os.path.isdir(localpath):
            try:
                open(os.path.join(localpath, 'test.write'), 'wb').close()
                os.remove(os.path.join(localpath, 'test.write'))
            except IOError:
                pass # We cannot write in this directory
            else:
                path = localpath
                break
    
    # Get path specific for this app
    if appname:
        if path == userDir:
            appname = '.' + appname.lstrip('.') # Make it a hidden directory
        path = os.path.join(path, appname)
        if not os.path.isdir(path):
            os.mkdir(path)
    
    # Done
    return path



# From pyzolib/paths.py (https://bitbucket.org/pyzo/pyzolib/src/tip/paths.py)
import os, sys
def common_appdata_dir(appname=None):
    """ common_appdata_dir(appname=None)
    Get the path to the common application directory. Applications are
    allowed to write files here. For user specific data, consider using
    appdata_dir().
    If appname is given, a subdir is appended (and created if necessary).
    """
    
    # Try to get path
    path = None
    if sys.platform.startswith('win'):
        path = os.getenv('ALLUSERSPROFILE', os.getenv('PROGRAMDATA'))
    elif sys.platform.startswith('darwin'):
        path = '/Library/Application Support'
    else:
        # Not sure what to use. Apps are only allowed to write to the home
        # dir and tmp dir, right?
        pass
    
    # If no success, use appdata_dir() instead
    if not (path and os.path.isdir(path)):
        path = appdata_dir()
    
    # Get path specific for this app
    if appname:
        path = os.path.join(path, appname)
        if not os.path.isdir(path):
            os.mkdir(path)
    
    # Done
    return path



#  Other approaches that we considered, but which did not work for links,
#  or are less reliable for other reasons are:
#      * sys.executable: does not work for links
#      * sys.prefix: dito
#      * sys.exec_prefix: dito
#      * os.__file__: does not work when frozen
#      * __file__: only accessable from main module namespace, does not work when frozen

# todo: get this included in Python sys or os module!

# From pyzolib/paths.py (https://bitbucket.org/pyzo/pyzolib/src/tip/paths.py)
import os, sys
def application_dir():
    """ application_dir()
    Get the directory in which the current application is located.
    The "application" can be a Python script or a frozen application.
    This function raises a RuntimeError if in interpreter mode.
    """
    if getattr(sys, 'frozen', False):
        # When frozen, use sys.executable
        thepath = os.path.dirname(sys.executable)
    else:
        # Test if the current process can be considered an "application"
        if not sys.path or not sys.path[0]:
            raise RuntimeError('Cannot determine app path because sys.path[0] is empty!')
        thepath = sys.path[0]
    # Return absolute version, or symlinks may not work
    return os.path.abspath(thepath)



## Pyzo specific
#
# A Pyzo distribution maintains a file in the appdata dir that lists
# the directory where it is intalled. Pyzo can in principle be installed
# multiple times. In that case the file contains multiple entries.
# This file is checked each time the pyzo executable is run. Therefore
# a user can move the Pyzo directory and simply run the Pyzo executable
# to update the registration.

def pyzo_dirs(newdir=None, makelast=False):
    """ pyzo_dirs(newdir=None,  makelast=False)
    Compatibility function. Like pyzo_dirs2, but returns a list of
    directories and does not allow setting the version.
    """
    return [p[0] for p in pyzo_dirs2(newdir, makelast=makelast)]


# From pyzolib/paths.py (https://bitbucket.org/pyzo/pyzolib/src/tip/paths.py)
import os, sys
def pyzo_dirs2(path=None, version='0', **kwargs):
    """ pyzo_dirs2(dir=None, version='0', makelast=False)
    Get the locations of installed Pyzo directories. Returns a list of
    tuples: (dirname, version). In future versions more information may
    be added to the file, so please take larger tuples into account.
    If path is a dir containing a python exe, it is added it to the
    list. If the keyword arg 'makelast' is given and True, will ensure
    that the given path is the last in the list (i.e. the default).
    """
    defaultPyzo = '', '0'  # To fill in values for shorter items
    newPyzo = (str(path), str(version)) if path else None
    # Get application dir
    userDir = os.path.expanduser('~')
    path = None
    if sys.platform.startswith('win'):
        path = os.getenv('LOCALAPPDATA', os.getenv('APPDATA'))
    elif sys.platform.startswith('darwin'):
        path = os.path.join(userDir, 'Library', 'Application Support')
    # Get application dir for Pyzo
    if path and os.path.isdir(path):
        path = os.path.join(path, 'pyzo')
    else:
        path = os.path.join(userDir, '.pyzo')  # On Linux and as fallback
    if not os.path.isdir(path):
        os.mkdir(path)
    # Open file and parse
    fname = os.path.join(path, 'pyzodirs')
    pyzos, npyzos = [], 0
    if os.path.isfile(fname):
        lines = open(fname, 'rb').read().decode('utf-8').split('\n')
        pyzos = [tuple(d.split(':::')) for d in [d.strip() for d in lines] if d]
        npyzos = len(pyzos)
    # Add dir if necessary
    if newPyzo and os.path.isdir(newPyzo[0]):
        if kwargs.get('makelast', False) or newPyzo not in pyzos:
            npyzos = 0  # force save
            pyzos = [p for p in pyzos if p[0] != newPyzo[0]]  # rm based on dir
            pyzos.append(newPyzo)
    # Check validity of all pyzos, write back if necessary, and return
    pythonname = 'python' + '.exe' * sys.platform.startswith('win')
    pyzos = [p for p in pyzos if os.path.isfile(os.path.join(p[0], pythonname))]
    if len(pyzos) != npyzos:
        lines = [':::'.join(p) for p in pyzos]
        open(fname, 'wb').write( ('\n'.join(lines)).encode('utf-8') )
    return [p+defaultPyzo[len(p):] for p in pyzos]




## Windows specific

# Maybe for directory of programs, pictures etc.
