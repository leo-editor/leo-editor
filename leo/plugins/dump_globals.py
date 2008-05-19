#@+leo-ver=4-thin
#@+node:edream.110203113231.730:@thin dump_globals.py
"""Dump Python globals at startup"""

#@@language python
#@@tabwidth -4

import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins

#@+others
#@+node:edream.110203113231.731:onStart
def onStart (tag,keywords):

    print "\nglobals..."
    for s in globals():
        if s not in __builtins__:
            print s

    print "\nlocals..."
    for s in locals():
        if s not in __builtins__:
            print s
#@-node:edream.110203113231.731:onStart
#@-others

if not g.app.unitTesting: # Not for unit testing.

    # Register the handlers...
    leoPlugins.registerHandler("start2", onStart)

    __version__ = "1.2"
    g.plugin_signon(__name__)
#@nonl
#@-node:edream.110203113231.730:@thin dump_globals.py
#@-leo
