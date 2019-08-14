# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20190805022257.1: * @file pyzo_file_browser.py
#@@first
"""pyzo_file_browser.py: Experimental plugin that adds pyzo's file browser dock to Leo."""
#@+<< pyzo_file_browser imports >>
#@+node:ekr.20190809093446.1: **  << pyzo_file_browser imports >>
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
# pylint: disable=no-member

#@-<< pyzo_file_browser imports >>
#@+others
#@+node:ekr.20190809093459.1: **  top-level Leo functions
#@+node:ekr.20190809093459.3: *3* init
init_warning_given = False

def init(): # pyzo_file_browser.py
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
#@+node:ekr.20190809093459.4: *3* onCreate
def onCreate(tag, keys): # pyzo_file_browser.py
    '''Create a pyzo file browser in c's outline.'''
    c = keys.get('c')
    dw = c and c.frame and c.frame.top
    if not dw:
        return
    pyzo.start_pyzo_in_leo(c, pyzo)
    from pyzo.tools.pyzoFileBrowser import PyzoFileBrowser
    make_dock(c,
        name="File Browser",
        widget=PyzoFileBrowser(parent=None),
    )
#@+node:ekr.20190814050007.1: *3* make_dock
def make_dock(c, name, widget): # pyzo_file_browser.py
    """Create a dock with the given name and widget in c's main window."""
    dw = c.frame.top
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
