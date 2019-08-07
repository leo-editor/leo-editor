#@+leo-ver=5-thin
#@+node:ekr.20190805022257.1: * @file pyzo_file_browser.py
'''
Experimental plugin that adds pyzo's file browser dock to Leo.
'''
#@+<< pyzo_file_browser imports >>
#@+node:ekr.20190805031511.1: ** << pyzo_file_browser imports >>
def after(s):
    '''A good trace for imports.'''
    g.pr('\n===== AFTER %s\n' % s)

import leo.core.leoGlobals as g
from leo.core.leoQt import QtWidgets # QtGui, QtCore, 
import sys

# 0. Crucial.
pyzo_dir = g.os_path_finalize_join(g.app.loadDir, '..', 'external')
assert g.os_path_exists(pyzo_dir), repr(pyzo_dir)
sys.path.insert(0, pyzo_dir)
# 1. Must be first.
after('1')
import pyzo
assert pyzo
after('pyzo')
# 2. Must be next.
import pyzo.core.main as main
after('pyzo.core.main')
main.loadIcons()
main.loadFonts()
from pyzo.core import menu
after('pyzo.core.menu')
assert menu
# 3. All other imports:
import pyzo.tools
assert pyzo.tools
after('pyzo.tools')
from pyzo.tools.pyzoFileBrowser import PyzoFileBrowser
after('pyzo.tools.pyzoFileBrowser')
assert PyzoFileBrowser
#
# Instantiate tool manager
from pyzo.tools import ToolManager
    # tools/__init__.py defines ToolManager.
pyzo.toolManager = ToolManager()
    # From mainWindow._populate.
after('2')

if 0: # May be required in overrides.
    import os.path as op
    assert op
#@-<< pyzo_file_browser imports >>

#@+others
#@+node:ekr.20190805032828.1: ** top-level functions
#@+node:ekr.20190805022358.1: *3* init (pyzo_file_browser.py)
init_warning_given = False

def init():
    '''Return True if the pyzo_file_browser plugin can be loaded.'''
    
    def oops(message):
        global init_warning_given
        if not init_warning_given:
            init_warning_given = True
            print('%s %s' % (__name__, message))
        return False

    if g.app.gui.guiName() != "qt":
        return oops('requires Qt gui')
    # if not pyzo:
        # return oops('requires pyzo')
    if not g.app.dock:
        return oops('is incompatible with --no-dock')
    g.plugin_signon(__name__)
    g.registerHandler('after-create-leo-frame', onCreate)
    return True
#@+node:ekr.20190805022841.1: *3* onCreate (pyzo_file_browser.py)
def onCreate(tag, keys):
    '''Create a pyzo file browser in c's outline.'''
    c = keys.get('c')
    dw = c and c.frame and c.frame.top
    if not dw:
        return
    #
    # Use Leo's main window, not pyzo's main window.
    assert isinstance(dw, QtWidgets.QMainWindow), repr(dw)
    pyzo.main = dw
        # pyzo.MainWindow.__init__ does pyzo.main = self
    #
    # Load the file browser.
    ### tm, tool_id = pyzo.toolManager, 'pyzofilebrowser'
    tm = pyzo.toolManager
    tm.loadTool('pyzofilebrowser')
    after('onCreate: %s' % c.shortFileName())
    # 
    # Monkey-patch the file browser.
    if 0:
        fb = tm.getTool('pyzofilebrowser')
        assert fb
    
#@-others
#@-leo
