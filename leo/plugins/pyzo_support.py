# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20190410171646.1: * @file pyzo_support.py
#@@first
'''
pyzo_support.py: Allow access to pyzo features within Leo.

This plugin will work only if pyzo can be imported successfully.
'''
#@+<< copyright >>
#@+node:ekr.20190412042616.1: ** << copyright >>
#@+at
# This file uses code from pyzo. Here is the pyzo copyright notice:
# 
# Copyright (C) 2013-2018, the Pyzo development team
# 
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.
# 
# Yoton is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.
#@-<< copyright >>
import os
import sys
import leo.core.leoGlobals as g
# from leo.core.leoQt import QtCore
#@+<< set pyzo switches >>
#@+node:ekr.20190410200749.1: ** << set pyzo switches >>
#
# Only my personal copy of pyzo supports these switches:
#
# --pyzo is part 1 of the two-step enabling of traces.
#
# The unpatch pyzo will say that the file '--pyzo' does not exist.
if '--pyzo' not in sys.argv:
    sys.argv.append('--pyzo')
#
# These switches are part 2 of two-step enabling of traces.
# My personal copy of pyzo uses `getattr(g, 'switch_name', None)`
# to avoid crashes in case these vars do not exist.
g.pyzo = True
g.pyzo_pdb = False
g.pyzo_trace = True
g.pyzo_trace_imports = True
#@-<< set pyzo switches >>
_saveConfigFile = False
#@+others
#@+node:ekr.20190415051706.1: **  top-level functions
#@+node:ekr.20190410171905.1: *3* init (pyzo_support.py)
def init():
    '''Return True if the plugin has loaded successfully.'''
    if g.app.gui.guiName() != "qt":
        print('pyzo_support.py requires Qt gui')
        return False
    ###
        # This obscures testing of pyzo imports.
        # if not is_pyzo_loaded():
            # print('pyzo_support.py requires pyzo')
            # return False
    g.plugin_signon(__name__)
    g.registerHandler('after-create-leo-frame', onCreate)
    return True
#@+node:ekr.20190415051754.1: *3* onCreate (pyzo_support.py)
def onCreate(tag, keys):
    c = keys.get('c')
    if c:
        c.pyzoController = PyzoController(c)

    
#@+node:ekr.20190414034531.1: ** class ConfigShim
class ConfigShim(object):
    # pylint: disable=no-member
    pass
#@+node:ekr.20190415051335.1: ** class PyzoController
class PyzoController (object):
    '''A per-commander controller providing pyzo support.'''
    
    def __init__(self, c):
    
        self.c = c
        # Not used at present: importing main sets pyzo's config.
            # self.use_config = True
                # True: use pyzo's config.
                # False: use ConfigShim class.
        self.widgets = []
            # Permanent references, to prevent widgets from disappearing.

    #@+others
    #@+node:ekr.20190415051125.13: *3* pz.monkey_patch
    def monkey_patch(self):
        
        from pyzo.tools.pyzoFileBrowser.tree import FileItem

        def patchedOnActivated(self, c=self.c):
            path = self.path()
            g.trace(path)
            ext = os.path.splitext(path)[1]
            if ext == '.leo': ### not in ['.pyc','.pyo','.png','.jpg','.ico']:
                g.openWithFileName(path, old_c=c)
        
        FileItem.onActivated = patchedOnActivated
    #@+node:ekr.20190413074155.1: *3* pz.open_file_browser
    def open_file_browser(self):
        '''Open pyzo's file browser.'''
        try:
            #@+<< import the file browser >>
            #@+node:ekr.20190415051125.9: *4* << import the file browser >>
            #
            # Modified from pyzo.
            # Copyright (C) 2013-2018, the Pyzo development team
            #
            # 1. Import main, which imports pyzo.
            import pyzo.core.main as main
            #
            # 2. Set fonts and icons.
            main.loadIcons()
            main.loadFonts()
            #
            # 3. Import menu and tree packages.
            from pyzo.core.menu import Menu
            from pyzo.tools.pyzoFileBrowser.tree import Tree
            assert Menu
            assert Tree
            #
            # 4. Import the pyzoFileBrowser package.
            from pyzo.tools.pyzoFileBrowser import PyzoFileBrowser
            self.PyzoFileBrowser = PyzoFileBrowser
            #@-<< import the file browser >>
            self.monkey_patch()
            w = PyzoFileBrowser(parent=None)
            w.show()
            self.widgets.append(w)
        except Exception:
            g.es_exception()
    #@-others
#@-others
#@-leo
