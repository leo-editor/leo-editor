# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20190813161639.1: * @file pyzo_in_leo.py
#@@first
"""pyzo_in_leo.py: Experimental plugin that adds all of pyzo's features to Leo."""
#@+<< pyzo_in_leo imports >>
#@+node:ekr.20190813161639.2: **  << pyzo_in_leo imports >>
import leo.core.leoGlobals as g
#
# Must patch sys.path here.
import sys
plugins_dir = g.os_path_finalize_join(g.app.loadDir, '..', 'plugins')
sys.path.insert(0, plugins_dir)
#
# Start pyzo, de-fanged.
import pyzo

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
    # pylint: disable=no-member.
        # pylint doesn't know where pyzo is defined.
    pyzo.start_pyzo_in_leo(c, pyzo)
#@-others
#@@language python
#@@tabwidth -4
#@-leo
