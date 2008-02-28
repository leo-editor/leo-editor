#@+leo-ver=4-thin
#@+node:edream.110203113231.736:@thin trace_keys.py
"""Trace keystrokes in the outline and body panes"""

#@@language python
#@@tabwidth -4

import leoGlobals as g
import leoPlugins

#@+others
#@+node:edream.110203113231.737:onKey
def onKey (tag,keywords):

    ch = keywords.get("ch")
    if ch and len(ch) > 0:
        g.es("key",`ch`)
#@nonl
#@-node:edream.110203113231.737:onKey
#@-others

if not g.app.unitTesting: # Not for unit testing.

    # Register the handlers...
    leoPlugins.registerHandler(("bodykey1","bodykey2","headkey1","headkey2"), onKey)

    __version__ = "1.2"
    g.plugin_signon(__name__)
#@nonl
#@-node:edream.110203113231.736:@thin trace_keys.py
#@-leo
