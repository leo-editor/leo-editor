#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2016, the Pyzo development team
#
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

"""EKR: A stripped-down version of pyzo.__init__.py, for use only with the file browser.

Leo will never copy all of pyzo into leo/external.

"""

# Set version number
__version__ = '4.6.2'

import os
import sys
import locale
import traceback

# Import yoton as an absolute package
from pyzo import yotonloader  # noqa
from pyzo.util import paths

from pyzo.util import zon as ssdf  # zon is ssdf-light
from pyzo.util.qt import QtCore, QtGui, QtWidgets

# Import language/translation tools
from pyzo.util._locale import translate, setLanguage  # noqa

## Define some functions

def getResourceDirs():
    """ getResourceDirs()
    Get the directories to the resources: (pyzoDir, appDataDir).
    Also makes sure that the appDataDir has a "tools" directory and
    a style file.
    """

#     # Get root of the Pyzo code. If frozen its in a subdir of the app dir
#     pyzoDir = paths.application_dir()
#     if paths.is_frozen():
#         pyzoDir = os.path.join(pyzoDir, 'source')
    pyzoDir = os.path.abspath(os.path.dirname(__file__))
    if '.zip' in pyzoDir:
        raise RuntimeError('The Pyzo package cannot be run from a zipfile.')

    # Get where the application data is stored (use old behavior on Mac)
    appDataDir = paths.appdata_dir('pyzo', roaming=True, macAsLinux=True)

    # Create tooldir if necessary
    toolDir = os.path.join(appDataDir, 'tools')
    if not os.path.isdir(toolDir):
        os.mkdir(toolDir)

    return pyzoDir, appDataDir

def loadConfig(defaultsOnly=False):
    """ loadConfig(defaultsOnly=False)
    Load default and site-wide configuration file(s) and that of the user (if it exists).
    Any missing fields in the user config are set to the defaults.
    """

    # Function to insert names from one config in another
    def replaceFields(base, new):
        for key in new:
            if key in base and isinstance(base[key], ssdf.Struct):
                replaceFields(base[key], new[key])
            else:
                base[key] = new[key]

    # Reset our pyzo.config structure
    ssdf.clear(config)

    # Load default and inject in the pyzo.config
    fname = os.path.join(pyzoDir, 'resources', 'defaultConfig.ssdf')
    defaultConfig = ssdf.load(fname)
    replaceFields(config, defaultConfig)

    # Platform specific keybinding: on Mac, Ctrl+Tab (actually Cmd+Tab) is a system shortcut
    if sys.platform == 'darwin':
        config.shortcuts2.view__select_previous_file = 'Alt+Tab,'

    # Load site-wide config if it exists and inject in pyzo.config
    fname = os.path.join(pyzoDir, 'resources', 'siteConfig.ssdf')
    if os.path.isfile(fname):
        try:
            siteConfig = ssdf.load(fname)
            replaceFields(config, siteConfig)
        except Exception:
            t = 'Error while reading config file %r, maybe its corrupt?'
            print(t % fname)
            raise

    # Load user config and inject in pyzo.config
    fname = os.path.join(appDataDir, "config.ssdf")
    if os.path.isfile(fname):
        try:
            userConfig = ssdf.load(fname)
            replaceFields(config, userConfig)
        except Exception:
            t = 'Error while reading config file %r, maybe its corrupt?'
            print(t % fname)
            raise

## Init

# List of names that are later overriden (in main.py)
if 0: ###
    editors = None # The editor stack instance
    shells = None # The shell stack instance
    main = None # The mainwindow
    icon = None # The icon
    parser = None # The source parser
    status = None # The statusbar (or None)

# Get directories of interest
pyzoDir, appDataDir = getResourceDirs()

# Create ssdf in module namespace, and fill it
config = ssdf.new()
loadConfig()

# Init default style name (set in main.restorePyzoState())
### defaultQtStyleName = ''
