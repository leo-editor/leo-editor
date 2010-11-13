#@+leo-ver=5-thin
#@+node:EKR.20040517080049.4: * @file open_shell.py
#@+<< docstring >>
#@+node:ekr.20050111112200: ** << docstring >>
''' Creates an 'Extensions' menu containing two commands:
Open Console Window and Open Explorer.

The Open Console Window command opens xterm on Linux.
The Open Explorer command Opens a Windows explorer window.

This allows quick navigation to facilitate testing and navigating large systems
with complex directories.

Please submit bugs / feature requests to etaekema@earthlink.net

Current limitations:
- Not tested on Mac OS X ...
- On Linux, xterm must be in your path.

'''
#@-<< docstring >>

# Written by Ed Taekema.  Modified by EKR

#@@language python
#@@tabwidth -4

__version__ = "0.7"

#@+<< version history >>
#@+node:ekr.20040909100119: ** << version history >>
#@+at
# 
# 0.5 EKR:
#     - Generalized the code for any kind of @file node.
#     - Changed _getpath so that explicit paths in @file nodes override @path directives.
# 0.6 EKR:
#     - Moved most docs into the docstring.
# 0.7 EKR: (Removed g.top)
#     - Added init function.
#     - Created per-commander pluginController class.
#@-<< version history >>
#@+<< imports >>
#@+node:ekr.20040909100226: ** << imports >>
import leo.core.leoGlobals as g

import os
import sys
#@-<< imports >>

# Changes these as required.
if sys.platform == "win32":
    pathToExplorer = 'c:/windows/explorer.exe'
    pathToCmd = 'c:/windows/system32/cmd.exe'
else:
    # Set these as needed...
    pathToExplorer = ''
    pathToCmd = ''

#@+others
#@+node:ekr.20060107110126: ** init
def init ():

    if 1: # Ok for unit testing: creates a new menu.

        # Register the handlers...
        g.registerHandler("after-create-leo-frame", onCreate)
        g.plugin_signon(__name__)
        return True
#@+node:ekr.20060107110126.1: ** onCreate
def onCreate (tag, keywords):

    c = keywords.get('c')
    if c:
        controller = pluginController(c)
        controller.load_menu()
#@+node:ekr.20060107110126.2: ** class pluginController
class pluginController:

    #@+others
    #@+node:ekr.20060107110126.3: *3* ctor
    def __init__ (self,c):

        self.c = c
    #@+node:EKR.20040517080049.6: *3* load_menu
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
    #@+node:EKR.20040517080049.7: *3* _getpath
    def _getpath (self,p):

        c = self.c
        dict = c.scanAllDirectives(p)
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
    #@+node:EKR.20040517080049.8: *3* _getCurrentNodePath
    def _getCurrentNodePath(self):

        c = self.c
        p = c.p
        d = self._getpath(p)
        return d
    #@+node:EKR.20040517080049.9: *3* launchCmd
    def launchCmd(self,event=None):

        global pathToCmd

        d = self._getCurrentNodePath()
        myCmd = 'cd ' + d
        os.spawnl(os.P_NOWAIT, pathToCmd, '/k ', myCmd)
    #@+node:EKR.20040517080049.10: *3* launchExplorer
    def launchExplorer(self,event=None):

        global pathToExplorer

        d = self._getCurrentNodePath()
        os.spawnl(os.P_NOWAIT,pathToExplorer, ' ', d)

    #@+node:EKR.20040517080049.11: *3* launchxTerm
    def launchxTerm(self,event=None):

        d = self._getCurrentNodePath()
        curdir = os.getcwd()
        os.chdir(d)
        os.spawnlp(os.P_NOWAIT, 'xterm', '-title Leo')
        os.chdir(curdir)
    #@-others
#@-others
#@-leo
