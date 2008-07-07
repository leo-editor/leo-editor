#@+leo-ver=4-thin
#@+node:EKR.20040517080049.4:@thin open_shell.py
#@<< docstring >>
#@+node:ekr.20050111112200:<< docstring >>
'''
Creates an 'extensions' menu with commands to open either an xterm on linux
or a cmd windows/explorer window on win32 in the directory of the current @file.
This allows quick navigation to facilitate testing and navigating large systems
with complex direcgtories.

Please submit bugs / feature requests to etaekema@earthlink.net

Current limitations:
- Not tested on Mac OS X ...
- On linux, xterm must be in your path.
'''
#@nonl
#@-node:ekr.20050111112200:<< docstring >>
#@nl

# Written by Ed Taekema.  Modified by EKR

#@@language python
#@@tabwidth -4

__version__ = "0.7"

#@<< version history >>
#@+node:ekr.20040909100119:<< version history >>
#@+at
# 
# 0.5 EKR:
#     - Generalized the code for any kind of @file node.
#     - Changed _getpath so that explicit paths in @file nodes override @path 
# directives.
# 0.6 EKR:
#     - Moved most docs into the docstring.
# 0.7 EKR: (Removed g.top)
#     - Added init function.
#     - Created per-commander pluginController class.
#@-at
#@nonl
#@-node:ekr.20040909100119:<< version history >>
#@nl
#@<< imports >>
#@+node:ekr.20040909100226:<< imports >>

import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins

import os
import sys
#@nonl
#@-node:ekr.20040909100226:<< imports >>
#@nl

# Changes these as required.
if sys.platform == "win32":
    pathToExplorer = 'c:/windows/explorer.exe'
    pathToCmd = 'c:/windows/system32/cmd.exe'
else:
    # Set these as needed...
    pathToExplorer = ''
    pathToCmd = ''

#@+others
#@+node:ekr.20060107110126:init
def init ():

    if 1: # Ok for unit testing: creates a new menu.

        # Register the handlers...
        leoPlugins.registerHandler("after-create-leo-frame", onCreate)

        g.plugin_signon(__name__)

        return True
#@nonl
#@-node:ekr.20060107110126:init
#@+node:ekr.20060107110126.1:onCreate
def onCreate (tag, keywords):

    c = keywords.get('c')
    if c:
        controller = pluginController(c)
        controller.load_menu()
#@nonl
#@-node:ekr.20060107110126.1:onCreate
#@+node:ekr.20060107110126.2:class pluginController
class pluginController:

    #@    @+others
    #@+node:ekr.20060107110126.3:ctor
    def __init__ (self,c):

        self.c = c
    #@nonl
    #@-node:ekr.20060107110126.3:ctor
    #@+node:EKR.20040517080049.6:load_menu
    def load_menu (self):

        if sys.platform == "win32":
            table = (
                ("&Open Console Window",None,self.launchCmd),
                ("Open &Explorer",None,self.launchExplorer))
        else:
            table = (("Open &xterm",None,self.launchxTerm),)

        c = self.c
        c.frame.menu.createNewMenu("E&xtensions","top")
        c.frame.menu.createMenuItemsFromTable("Extensions",table,dynamicMenu=True)
    #@nonl
    #@-node:EKR.20040517080049.6:load_menu
    #@+node:EKR.20040517080049.7:_getpath
    def _getpath (self,p):

        c = self.c
        dict = g.scanDirectives(c,p=p)
        d = dict.get("path")

        if p.isAnyAtFileNode():
            filename = p.anyAtFileNodeName()
            filename = g.os_path_join(d,filename)
            if filename:
                d = g.os_path_dirname(filename)

        if d is None:
            return ""
        else:
            return g.os_path_normpath(d)
    #@nonl
    #@-node:EKR.20040517080049.7:_getpath
    #@+node:EKR.20040517080049.8:_getCurrentNodePath
    def _getCurrentNodePath(self):

        c = self.c
        p = c.currentPosition()
        d = self._getpath(p)
        return d
    #@nonl
    #@-node:EKR.20040517080049.8:_getCurrentNodePath
    #@+node:EKR.20040517080049.9:launchCmd
    def launchCmd(self,event=None):

        global pathToCmd

        d = self._getCurrentNodePath()
        myCmd = 'cd ' + d
        os.spawnl(os.P_NOWAIT, pathToCmd, '/k ', myCmd)
    #@nonl
    #@-node:EKR.20040517080049.9:launchCmd
    #@+node:EKR.20040517080049.10:launchExplorer
    def launchExplorer(self,event=None):

        global pathToExplorer

        d = self._getCurrentNodePath()
        os.spawnl(os.P_NOWAIT,pathToExplorer, ' ', d)

    #@-node:EKR.20040517080049.10:launchExplorer
    #@+node:EKR.20040517080049.11:launchxTerm
    def launchxTerm(self,event=None):

        d = self._getCurrentNodePath()
        curdir = os.getcwd()
        os.chdir(d)
        os.spawnlp(os.P_NOWAIT, 'xterm', '-title Leo')
        os.chdir(curdir)
    #@nonl
    #@-node:EKR.20040517080049.11:launchxTerm
    #@-others
#@nonl
#@-node:ekr.20060107110126.2:class pluginController
#@-others
#@nonl
#@-node:EKR.20040517080049.4:@thin open_shell.py
#@-leo
