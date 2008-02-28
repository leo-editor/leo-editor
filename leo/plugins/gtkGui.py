#@+leo-ver=4-thin
#@+node:ekr.20080112150934:@thin gtkGui.py
'''The plugin part of the gtk gui code.'''

import leoGlobals as g
import leoGtkGui

try:
    import gtk
except ImportError:
    gtk = None
    g.es_print('can not import gtk')

#@+others
#@+node:ekr.20080112150934.1:init
def init():

    if g.app.unitTesting: # Not Ok for unit testing!
        return False

    if not gtk:
        return False

    if g.app.gui:
        return g.app.gui.guiName() == 'gtk'
    else:
        g.app.gui = leoGtkGui.gtkGui()
        # g.app.root = g.app.gui.createRootWindow()
        g.app.gui.finishCreate()
        g.plugin_signon(__name__)
        return True
#@-node:ekr.20080112150934.1:init
#@-others
#@-node:ekr.20080112150934:@thin gtkGui.py
#@-leo
