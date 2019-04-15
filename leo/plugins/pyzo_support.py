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
#@+<< imports >>
#@+node:ekr.20190415121818.1: ** << imports >> (pyzo_support.py)
import os
import sys
import leo.core.leoGlobals as g
try:
    import pyzo
except Exception:
    pyzo=None
#@-<< imports >>
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
g.pyzo_trace = False
g.pyzo_trace_imports = False
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
    if not pyzo:
        print('pyzo_support.py requires pyzo')
        return False
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
    #@+node:ekr.20190415051125.13: *3* pz.monkey_patch_file_browser
    def monkey_patch_file_browser(self):
        
        from pyzo.tools.pyzoFileBrowser.tree import FileItem
        pyzo_controller = self

        def patchedOnActivated(self):
            path = self.path()
            ext = os.path.splitext(path)[1]
            #
            # This test is not great,
            # but other tests for binary files may be worse.
            if ext not in ['.pyc','.pyo','.png','.jpg','.ico']:
                pyzo_controller.open_file_in_commander(ext, path)
        
        FileItem.onActivated = patchedOnActivated
    #@+node:ekr.20190415182936.1: *3* pz.monkey_patch_shell (to do)
    def monkey_patch_shell(self):
        pass
        
        ###
            # from pyzo.tools.pyzoFileBrowser.tree import FileItem
            # pyzo_controller = self
        
            # def patchedOnActivated(self):
                # path = self.path()
                # ext = os.path.splitext(path)[1]
                # #
                # # This test is not great,
                # # but other tests for binary files may be worse.
                # if ext not in ['.pyc','.pyo','.png','.jpg','.ico']:
                    # pyzo_controller.open_file_in_commander(ext, path)
            
            # FileItem.onActivated = patchedOnActivated
    #@+node:ekr.20190415122136.1: *3* pz.open_file_in_commander
    def open_file_in_commander(self, ext, path):
        '''Open the given path in a Leonine manner.'''
        #
        # 1. Open .leo files as in open-outline command...
        path = os.path.normpath(path)
        if g.app.loadManager.isLeoFile(path):
            c = g.openWithFileName(path, old_c=self.c)
            if not c:
                return
            c.k.makeAllBindings()
            g.chdir(path)
            g.setGlobalOpenDir(path)
            return
        #
        # 2. Search open commanders for a matching @<file> node.
        for c in g.app.commanders():
            for p in c.all_unique_positions():
                if (
                    p.isAnyAtFileNode() and
                    path == os.path.normpath(g.fullPath(c, p))
                ):
                    if getattr(c.frame.top, 'leo_master', None):
                        c.frame.top.leo_master.select(c)
                        c.selectPosition(p)
                    c.redraw()
                    return
        #
        # 3. Open a dummy file, removing sentinels from derived files.
        c = g.openWithFileName(path, old_c=self.c)
        c.k.makeAllBindings()
        g.chdir(path)
        g.setGlobalOpenDir(path)
        c.selectPosition(c.rootPosition())
        c.redraw()
    #@+node:ekr.20190413074155.1: *3* pz.open_file_browser
    def open_file_browser(self):
        '''Open pyzo's file browser.'''
        try:
            #@+<< import the file browser >>
            #@+node:ekr.20190415051125.9: *4* << import the file browser >>
            #
            # Order is important!
            #
            # import pyzo # Done at the top level.
            import pyzo.core.main as main
            main.loadIcons()
            main.loadFonts()
            #
            from pyzo.core.menu import Menu
            from pyzo.tools.pyzoFileBrowser.tree import Tree
            assert Menu and Tree # Keep pyflakes happy.
            #
            from pyzo.tools.pyzoFileBrowser import PyzoFileBrowser
            #@-<< import the file browser >>
            self.monkey_patch_file_browser()
            w = PyzoFileBrowser(parent=None)
            w.show()
            self.widgets.append(w)
        except Exception:
            g.es_exception()
    #@+node:ekr.20190415182735.1: *3* pz.open_shell_window (To do)
    def open_shell_window(self):
        '''Open pyzo's file browser.'''
        try:
            #@+<< imports for the shell >>
            #@+node:ekr.20190415182821.1: *4* << imports for the shell >>
            #
            # Order is important!
            #
            # import pyzo # Done at the top level.
            import pyzo.core.main as main
            main.loadIcons()
            main.loadFonts()
            #
            # from pyzo.core.menu import Menu
            # from pyzo.tools.pyzoFileBrowser.tree import Tree
            # assert Menu and Tree # Keep pyflakes happy.
            #
            # from pyzo.tools.pyzoFileBrowser import PyzoFileBrowser
            #@-<< imports for the shell >>
            self.monkey_patch_shell()
            # w = PyzoFileBrowser(parent=None)
            # w.show()
            # self.widgets.append(w)
        except Exception:
            g.es_exception()
    #@-others
#@-others
#@-leo
