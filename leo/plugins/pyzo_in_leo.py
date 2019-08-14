# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20190813161639.1: * @file pyzo_in_leo.py
#@@first
"""pyzo_in_leo.py: Experimental plugin that adds all of pyzo's features to Leo."""
#@+<< pyzo_in_leo imports >>
#@+node:ekr.20190813161639.2: **  << pyzo_in_leo imports >>
def banner(message):
    print('')
    print(message)
    print('')

import leo.core.leoGlobals as g
from leo.core.leoQt import QtCore
#
# Must patch sys.path here.
import sys
plugins_dir = g.os_path_finalize_join(g.app.loadDir, '..', 'plugins')
sys.path.insert(0, plugins_dir)
#
# Start pyzo, de-fanged.
import pyzo
#
#@-<< pyzo_in_leo imports >>
#@+others
#@+node:ekr.20190813161639.3: **  top-level Leo functions (pyzo_in_leo.py)
#@+node:ekr.20190813161639.4: *3* init
init_warning_given = False

def init(): # pyzo_in_leo.py
    '''Return True if this plugin can be loaded.'''
    
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
#@+node:ekr.20190813161639.5: *3* onCreate
def onCreate(tag, keys): # pyzo_in_leo.py
    '''Create pyzo docks in Leo's own main window'''
    c = keys.get('c')
    if not c and c.frame:
        return
    # pylint: disable=no-member
    pyzo.start_pyzo_in_leo(c, pyzo)
    if 1:
        table = (
            'PyzoFileBrowser',
            'PyzoHistoryViewer',
            'PyzoInteractiveHelp',
            'PyzoLogger',
            'PyzoSourceStructure',
            'PyzoWebBrowser',
            'PyzoWorkspace',
        )
        for tool_id in table:
            pyzo.toolManager.loadTool(tool_id)
                # This puts the dock on the right.
    else:
        #
        # Import the dock classes last.
        from pyzo.tools.pyzoFileBrowser import PyzoFileBrowser
        from pyzo.tools.pyzoHistoryViewer import PyzoHistoryViewer
        from pyzo.tools.pyzoInteractiveHelp import PyzoInteractiveHelp
        from pyzo.tools.pyzoLogger import PyzoLogger
        from pyzo.tools.pyzoSourceStructure import PyzoSourceStructure
        from pyzo.tools.pyzoWebBrowser import PyzoWebBrowser
        from pyzo.tools.pyzoWorkspace import PyzoWorkspace
        banner("END onCreate imports")
        #
        # Make the docks.
        table = (
            ("File Browser", PyzoFileBrowser),
            ("History Viewer", PyzoHistoryViewer),
            ("Interactive Help", PyzoInteractiveHelp),
            ("Logger", PyzoLogger),
            ("Source Structure", PyzoSourceStructure),
                # Uses pyzo.editors.
            ("Web Browser", PyzoWebBrowser),
            ("Workspace", PyzoWorkspace),
                # Uses pyzo.editors and pyzo.shells.
        )
        for name, widget_class in table:
            make_dock(c, name=name, widget=widget_class(parent=None))
                # This puts the dock on the left.
#@+node:ekr.20190813161921.1: *3* make_dock
def make_dock(c, name, widget): # pyzo_in_leo.py
    """Create a dock with the given name and widget in c's main window."""
    dw = c.frame.top
    if not c:
        return
    dock = dw.createDockWidget(
        closeable=True,
        moveable=True,
        height=100,
        name=name,
    )
    dw.leo_docks.append(dock)
    dock.setWidget(widget)
    area = QtCore.Qt.LeftDockWidgetArea
    dw.addDockWidget(area, dock)
    widget.show()
#@-others
#@@language python
#@@tabwidth -4
#@-leo
