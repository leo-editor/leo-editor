#@+leo-ver=5-thin
#@+node:ekr.20040915073259.1: * @file maximizeNewWindows.py
"""Maximizes all new windows."""

#@@language python
#@@tabwidth -4

__version__ = "1.4"
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
# 1.4 EKR: Gui independent.
#@-<< version history >>

import leo.core.leoGlobals as g

#@+others
#@+node:ekr.20070602072200.1: ** init
def init():

    g.registerHandler(('new','open2'), maximize_window)
    g.plugin_signon(__name__)
    return True
#@+node:ekr.20070602072200.2: ** maximize_window
def maximize_window(tag, keywords):

    c = keywords.get('c')
    if c and c.exists and c.frame and not c.frame.isNullFrame:
        c.frame.resizeToScreen()
#@-others
#@-leo
