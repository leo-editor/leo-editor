#@+leo-ver=5-thin
#@+node:ekr.20040915073259.1: * @file ../plugins/maximizeNewWindows.py
"""Maximizes all new windows."""

# Original written by Jaakko Kourula.
# Edited by EKR.

#@+<< imports >>
#@+node:Dmitry.20101128013501.1258: ** << imports >>
from leo.core import leoGlobals as g
from leo.core import leoPlugins

#@-<< imports >>

#@+others
#@+node:Dmitry.20101128013501.1259: ** init
def init():
    '''Return True if the plugin has loaded successfully.'''
    leoPlugins.registerHandler("after-create-leo-frame", maximize_window)
    g.plugin_signon(__name__)
    return True

#@+node:Dmitry.20101128013501.1260: ** maximize_window
def maximize_window(tag, keywords):

    c = keywords.get('c')

    if c and c.exists and c.frame and not c.frame.isNullFrame:
        gui = g.app.gui.guiName()
        if gui in ('qt','qttabs'):
            c.frame.top.showMaximized()
        # elif gui == 'tkinter':
            # c.frame.resizeToScreen()
#@-others
#@@language python
#@@tabwidth -4
#@-leo
