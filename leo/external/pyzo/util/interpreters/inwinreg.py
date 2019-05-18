# -*- coding: utf-8 -*-
# Copyright (c) 2016, Almar Klein

"""
This module implements functionality to obtain registered
Python interpreters and to register a Python interpreter in the Windows
registry.

"""

import sys
import os

try:
    import winreg
except ImportError:
    winreg = None

PYTHON_KEY = 'SOFTWARE\\Python\\PythonCore'
PYTHON_KEY_WOW64 = 'SOFTWARE\\Wow6432Node\\Python\\PythonCore'
INSTALL_KEY = "InstallPath"
PATH_KEY = "PythonPath"


class PythonInReg:
    """ Class to represent a specific version of the Python interpreter
    registered (or being registered in the registry).
    This is a helper class for the functions defined in this module; it
    should not be instantiated directly.
    """
    
    USER_ONE = 1
    USER_ALL = 2
    
    def __init__(self, user, version, wow64=False):
        self._user = user
        self._key = (wow64 and PYTHON_KEY_WOW64 or PYTHON_KEY) + '\\' + version
    
    def __repr__(self):
        userstr = [None, 'USER_ONE', 'USER_ALL'][self._user]
        installPath = self.installPath()
        reg = self._reg()
        if not reg:
            return '<PythonInReg %s at %s (unregistered)>' % (self.version(), userstr)
        elif installPath:
            return '<PythonInReg %s at %s in "%s">' % (self.version(), userstr, installPath)
        else:
            return '<PythonInReg %s at %s>' % (self.version(), userstr)
    
    def _root(self):
        if self._user == PythonInReg.USER_ONE:
            return winreg.HKEY_CURRENT_USER
        else:
            return winreg.HKEY_LOCAL_MACHINE
    
    def _reg(self):
        # Get key for this version
        try:
            return winreg.OpenKey(self._root(), self._key, 0, winreg.KEY_READ)
        except Exception:
            return None
    
    def create(self):
        """ Create key. If already exists, does nothing.
        """
        
        # Get key for this version
        reg = self._reg()
        
        if reg:
            winreg.CloseKey(reg)
            #print('Unable to create Python version %s: already exists.' % self.version())
        
        else:
            # Try to create
            try:
                reg = winreg.CreateKey(self._root(), self._key)
                winreg.CloseKey(reg)
            except Exception:
                raise RuntimeError('Unable to create python version %s.' % self.version())
            print('Created %s.' % str(self))
    
    
    def delete(self):
        
        # Get key for this version
        reg = self._reg()
        if not reg:
            print('Unable to delete Python version %s: does not exist.')
        
        # Delete attributes
        try:
            winreg.DeleteKey(reg, INSTALL_KEY)
        except Exception:
            pass
        try:
            winreg.DeleteKey(reg, PATH_KEY)
        except Exception:
            pass
        
        # Delete main key for this version, or show warning
        try:
            winreg.DeleteKey(self._root(), self._key)
        except Exception:
            print('Could not delete %s.' % str(self))
            return
        print('Deleted %s.' % str(self))
    
    def setInstallPath(self, installPath):
        # Get key for this version
        reg = self._reg()
        if not reg:
            raise RuntimeError('Could not set installPath for version %s: version does not exist.' % self.version())
        
        # Set value or raise error
        try:
            winreg.SetValue(reg, INSTALL_KEY, winreg.REG_SZ, installPath)
            winreg.CloseKey(reg)
        except Exception:
            winreg.CloseKey(reg)
            raise RuntimeError('Could not set installPath for %s.' % str(self))
    
    def installPath(self):
        # Get key for this version
        reg = self._reg()
        if not reg:
            return None
        
        # Get value or return None
        try:
            installPath = winreg.QueryValue(reg, INSTALL_KEY)
            winreg.CloseKey(reg)
            return installPath
        except Exception:
            winreg.CloseKey(reg)
            return None
    
    def setPythonPath(self, pythonPath):
        # Get key for this version
        reg = self._reg()
        if not reg:
            raise RuntimeError('Could not set pythonPath for version %s: version does not exist.' % self.version())
        
        # Set value or raise error
        try:
            winreg.SetValue(reg, PATH_KEY, winreg.REG_SZ, pythonPath)
            winreg.CloseKey(reg)
        except Exception:
            winreg.CloseKey(reg)
            raise RuntimeError('Could not set pythonPath for %s.' % str(self))
    
    def pythonPath(self):
        # Get key for this version
        reg = self._reg()
        if not reg:
            return None
        
        # Get value or return None
        try:
            pythonPath = winreg.QueryValue(reg, PATH_KEY)
            winreg.CloseKey(reg)
            return pythonPath
        except Exception:
            winreg.CloseKey(reg)
            return None
    
    def version(self):
        """ Get the Python version.
        """
        return self._key[-3:]



def get_interpreters_in_reg():
    """ get_interpreters_in_reg()
    Get a list of PythonInReg instances: one for each interpreter
    in the registry. This function checks both LOCAL_MACHINE and CURRENT_USER.
    """
    versions = []
    for user in [1, 2]:
        for wow64 in [False, True]:
            versions.extend( _get_interpreter_in_reg(user, wow64) )
    return versions


def _get_interpreter_in_reg(user, wow64=False):
    
    # Get base key
    if user == PythonInReg.USER_ONE:
        HKEY = winreg.HKEY_CURRENT_USER
    else:
        HKEY = winreg.HKEY_LOCAL_MACHINE
    
    # Get Python key
    if wow64:
        PYKEY = PYTHON_KEY_WOW64
    else:
        PYKEY = PYTHON_KEY
    
    # Try to open Python key
    try:
        reg = winreg.OpenKey(HKEY, PYKEY, 0, winreg.KEY_READ)
    except Exception:
        return []
    
    # Get info about subkeys
    nsub, nval, modified = winreg.QueryInfoKey(reg)
    
    # Query all
    versions = []
    for i in range(nsub):
        # Get name and subkey
        version = winreg.EnumKey(reg, i)
        versions.append( PythonInReg(user, version, wow64) )
    
    # Done
    winreg.CloseKey(reg)
    return versions


def register_interpreter(version=None, installPath=None, user=None, wow64=False):
    """ register_interpreter(version=None, installPath=None, user=None, wow64=False)
    Register a certain Python version. If version and installPath
    are not given, the current Python process is registered.
    if user is not given, tries LOCAL_MACHINE first but uses CURRENT_USER
    if that fails.
    """
    if version is None:
        version = sys.version[:3]
    if installPath is None:
        installPath = sys.prefix
    
    # Get existing versions
    existingVersions = get_interpreters_in_reg()
    
    # Determine what users to try
    if user is None:
        users = [2, 1]
    else:
        users = [user]
    
    success = False
    
    for user in users:
        
        # Create new PythonInReg instance
        v = PythonInReg(user, version, wow64)
        
        # Check if already exists
        ok = True
        for ev in existingVersions:
            if ev._key != v._key or ev._user != v._user:
                continue # Different key; no problem
            if (not ev.installPath()) or (not os.path.isdir(ev.installPath())):
                continue # Key the same, but existing entry is invalid
            if ev.installPath() == installPath:
                # Exactly the same, no action required, return now!
                return ev
            # Ok, there's a problem
            ok = False
            print('Warning: version %s is already installed in "%s".'
                                            % (version, ev.installPath()))
        if not ok:
            continue
        
        # Try to create the key
        try:
            v.create()
            v.setInstallPath(installPath)
            success = True
            break
        except RuntimeError:
            continue
    
    if success:
        return v
    else:
        raise RuntimeError('Could not register Python version %s at %s.'
                                    % (version, installPath))


if __name__ == '__main__':
    
    for v in get_interpreters_in_reg():
        print(v)
