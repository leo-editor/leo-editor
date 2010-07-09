#@+leo-ver=5-thin
#@+node:edream.110203113231.736: * @thin trace_keys.py
"""Trace keystrokes in the outline and body panes"""

#@@language python
#@@tabwidth -4

import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins

__version__ = "1.2"

#@+others
#@+node:ekr.20100128091412.5387: ** newHeadline
def init():

    ok = not g.app.unitTesting # Not for unit testing.

    if ok:
        # Register the handlers...
        leoPlugins.registerHandler(("bodykey1","bodykey2","headkey1","headkey2"), onKey)
        g.plugin_signon(__name__)

    return ok
#@+node:edream.110203113231.737: ** onKey
def onKey (tag,keywords):

    ch = keywords.get("ch")
    if ch and len(ch) > 0:
        g.es("key",repr(ch))
#@-others
#@-leo
