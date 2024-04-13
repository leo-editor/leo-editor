#@+leo-ver=5-thin
#@+node:EKR.20040517080049.4: * @file ../plugins/open_shell.py
#@+<< docstring >>
#@+node:ekr.20050111112200: ** << docstring >>
"""
Creates an 'Extensions' menu containing two commands:
Open Console Window and Open Explorer.

The Open Console Window command opens xterm on Linux.
The Open Explorer command Opens a Windows explorer window.

This allows quick navigation to facilitate testing and navigating large systems
with complex directories.

Please submit bugs / feature requests to etaekema@earthlink.net

Current limitations:
- Not tested on Mac OS X ...
- On Linux, xterm must be in your path.

"""
#@-<< docstring >>

# Written by Ed Taekema.  Modified by EKR
import os
import sys
from leo.core import leoGlobals as g

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
def init():
    """Return True if the plugin has loaded successfully."""
    # Ok for unit testing: creates a new menu.
    g.registerHandler("after-create-leo-frame", onCreate)
    g.plugin_signon(__name__)
    return True
#@+node:ekr.20060107110126.1: ** onCreate
def onCreate(tag, keywords):

    c = keywords.get('c')
    if c:
        controller = pluginController(c)
        controller.load_menu()
#@+node:ekr.20060107110126.2: ** class pluginController
class pluginController:

    #@+others
    #@+node:ekr.20060107110126.3: *3* ctor
    def __init__(self, c):

        self.c = c
    #@+node:EKR.20040517080049.6: *3* load_menu
    def load_menu(self):

        c = self.c
        if sys.platform == "win32":
            table = (
                ("&Open Console Window", None, self.launchCmd),
                ("Open &Explorer", None, self.launchExplorer))
        else:
            table = (("Open &xterm", None, self.launchxTerm),)
        c.frame.menu.createNewMenu("E&xtensions", "top")
        c.frame.menu.createMenuItemsFromTable("Extensions", table)
    #@+node:EKR.20040517080049.7: *3* _getpath (open_shell.py)
    def _getpath(self, p):

        c = self.c
        path = c.fullPath(p)  # #1914
        # Use os.path.normpath to give system separators.
        return os.path.normpath(g.os_path_dirname(path))  # #1914
    #@+node:EKR.20040517080049.8: *3* _getCurrentNodePath
    def _getCurrentNodePath(self):

        c = self.c
        p = c.p
        d = self._getpath(p)
        return d
    #@+node:EKR.20040517080049.9: *3* launchCmd
    def launchCmd(self, event=None):

        global pathToCmd

        d = self._getCurrentNodePath()
        myCmd = 'cd ' + d
        os.spawnl(os.P_NOWAIT, pathToCmd, '/k ', myCmd)
    #@+node:EKR.20040517080049.10: *3* launchExplorer
    def launchExplorer(self, event=None):

        global pathToExplorer

        d = self._getCurrentNodePath()
        os.spawnl(os.P_NOWAIT, pathToExplorer, ' ', d)

    #@+node:EKR.20040517080049.11: *3* launchxTerm
    def launchxTerm(self, event=None):

        d = self._getCurrentNodePath()
        curdir = os.getcwd()
        os.chdir(d)
        os.spawnlp(os.P_NOWAIT, 'xterm', '-title Leo')
        os.chdir(curdir)
    #@-others
#@-others
#@@language python
#@@tabwidth -4

#@-leo
