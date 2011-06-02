#@+leo-ver=5-thin
#@+node:ekr.20040915073259.1: * @file maximizeNewWindows.py
"""Maximizes all new windows."""

#@@language python
#@@tabwidth -4

__version__ = "1.4"
#@+<< version history >>
#@+node:Dmitry.20101128013501.1257: ** << version history >>
#@+at
# 
# Original written by Jaakko Kourula.
# 
# 1.0 EKR:
#     - Enabled only for windows platform.
#     - Minor style changes.
# 1.1 EKR: Make sure c exists in maximize_window.
# 1.2 EKR:
#     - The proper guard is:
#         if c and c.exists and c.frame and not c.frame.isNullFrame:
#     - Added init function.
# 1.3 EKR: Now works on Linux.
# 1.4 Ivanov Dmitriy, Ville M. Vainio:
#     Added the support for Qt UI, removed Tk check in init function
#@-<< version history >>
#@+<< imports >>
#@+node:Dmitry.20101128013501.1258: ** << imports >>
import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins

#@-<< imports >>

#@+others
#@+node:Dmitry.20101128013501.1259: ** init
def init():

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
#@-leo
