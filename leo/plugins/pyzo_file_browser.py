#@+leo-ver=5-thin
#@+node:ekr.20190805022257.1: * @file pyzo_file_browser.py
'''
Experimental plugin that adds pyzo's file browser dock to Leo.
'''
#@+<< pyzo_file_browser imports >>
#@+node:ekr.20190805031511.1: ** << pyzo_file_browser imports >>
def banner(s):
    '''A good trace for imports.'''
    if 1: g.pr('\n===== %s\n' % s)

import leo.core.leoGlobals as g
from leo.core.leoQt import QtWidgets # QtGui, QtCore, 
import sys

# 0: Crucial.
pyzo_dir = g.os_path_finalize_join(g.app.loadDir, '..', 'external')
assert g.os_path_exists(pyzo_dir), repr(pyzo_dir)
sys.path.insert(0, pyzo_dir)
# 1: Must import pyzo first.
banner('START top-level imports')
import pyzo
assert pyzo
banner('AFTER pyzo')
# 2: Import main.
import pyzo.core.main as main
main.loadIcons()
main.loadFonts()
banner('pyzo.core.main')
# 3: Import menus.
from pyzo.core import menu
    # Previoiusly this imported pyzo.core.pyzoLogging.py.
    # Changed menu.py so it no longer does so.
banner('AFTER pyzo.core.menu')
assert menu
#
# Delayed imports form MainWindow._populate.
from pyzo.core.editorTabs import EditorTabs
assert EditorTabs
from pyzo.core.shellStack import ShellStackWidget
assert ShellStackWidget
from pyzo.core import codeparser
from pyzo.core.history import CommandHistory
from pyzo.tools import ToolManager
banner('After MainWindow._populate imports')
#
# Instantiate singleton objects, from MainWindow._populate.
pyzo.keyMapper = menu.KeyMapper()
pyzo.command_history = CommandHistory('command_history.py')
pyzo.toolManager = ToolManager()
if pyzo.parser is None:
    pyzo.parser = codeparser.Parser()
    pyzo.parser.start()
banner('AFTER top-level imports')
#@-<< pyzo_file_browser imports >>

#@+others
#@+node:ekr.20190805032828.1: ** top-level functions
#@+node:ekr.20190808025414.1: *3* get_tool_ids
def get_tool_ids(c): # pyzo_file_browser.py
    '''Return a list of tool id's from c.config.getData.'''
    valid_ids = [
        'pyzofilebrowser',
        'pyzohistoryviewer',
        'pyzointeractivehelp',
        'pyzologger',
        'pyzowebbrowser',
        #
        # 'pyzosourcestructure', # Requires pyzo.editors and 
            # File "leo\external\pyzo\tools\pyzoSourceStructure.py", line 100, in __init__
            # pyzo.editors.currentChanged.connect(self.onEditorsCurrentChanged)
            # AttributeError: 'NoneType' object has no attribute 'currentChanged'
        #
        # 'pyzoworkspace', # Requires pyzo.shells.
            # File "leo\external\pyzo\tools\pyzoWorkspace.py", line 41, in __init__
            # pyzo.shells.currentShellChanged.connect(self.onCurrentShellChanged)
            # AttributeError: 'NoneType' object has no attribute 'currentShellChanged'
    ]
    result = []
    aList = c.config.getData('pyzo_tool_ids')
    for tool_id in aList:
        try:
            tool_id = tool_id.lower()
            if tool_id in valid_ids:
                result.append(tool_id)
            else:
                raise ValueError
        except Exception:
            g.es_print('bad @data pyzo_tool_ids value: %r' % tool_id)
    return result
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
#@+node:ekr.20190805022841.1: *3* onCreate
def onCreate(tag, keys): # pyzo_file_browser.py
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
    #@+<< Define patches to dw >>
    #@+node:ekr.20190808021850.1: *4* << Define patches to dw >>
    def setMainTitle(self, path=None):
        pass
        
    g.funcToMethod(setMainTitle, dw.__class__, name=None)
    #@-<< Define patches to dw >>
    banner('BEFORE onCreate: %s' % c.shortFileName())
    #
    # Instantiate pyzo.editors.
    from pyzo.core.editorTabs import EditorTabs
    pyzo.editors = EditorTabs(pyzo.main)
    #
    # Load all enabled tools from @data pyzo_tool_ids.
    tm = pyzo.toolManager
    for tool_id in get_tool_ids(c):
        tm.loadTool(tool_id)
    banner('AFTER onCreate: %s' % c.shortFileName())
#@-others
#@-leo
