#@+leo-ver=5-thin
#@+node:ekr.20040915073259.1: * @thin maximizeNewWindows.py
"""Maximizes all new windows."""

#@@language python
#@@tabwidth -4

__version__ = "1.3"
#@+<< version history >>
#@+node:ekr.20040915073259.2: ** << version history >>
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
#@-<< version history >>
#@+<< imports >>
#@+node:ekr.20070602072200: ** << imports >>
import leo.core.leoGlobals as g

Tk = g.importExtension('Tkinter',pluginName=__name__,verbose=True)
#@-<< imports >>

#@+others
#@+node:ekr.20070602072200.1: ** init
def init():
    ok = Tk and not g.app.unitTesting
    if ok:
        # g.app.pluginsController.registerHandler("after-create-leo-frame", maximize_window)
        g.app.pluginsController.registerHandler(('new','open2'), maximize_window)
        g.plugin_signon(__name__)
    return ok
#@+node:ekr.20070602072200.2: ** maximize_window
def maximize_window(tag, keywords):

    c = keywords.get('c')
    if c and c.exists and c.frame and not c.frame.isNullFrame:
        c.frame.resizeToScreen()
#@-others
#@-leo
