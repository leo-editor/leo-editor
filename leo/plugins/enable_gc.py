#@+leo-ver=4-thin
#@+node:edream.110203113231.732:@thin enable_gc.py
"""Enable debugging and tracing for Python's garbage collector"""

#@@language python
#@@tabwidth -4

import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins

#@+others
#@+node:edream.110203113231.733:onStart
def onStart (tag,keywords):

    try:
        import gc
        gc.set_debug(gc.DEBUG_LEAK)
    except: pass
#@nonl
#@-node:edream.110203113231.733:onStart
#@-others

if not g.app.unitTesting: # Not for unit testing.

    # Register the handlers...
    leoPlugins.registerHandler("start2", onStart)

    __version__ = "1.2"
    g.plugin_signon(__name__)
#@nonl
#@-node:edream.110203113231.732:@thin enable_gc.py
#@-leo
