#@+leo-ver=5-thin
#@+node:edream.110203113231.732: * @thin enable_gc.py
"""Enable debugging and tracing for Python's garbage collector"""

#@@language python
#@@tabwidth -4

import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins

__version__ = "1.2"

#@+others
#@+node:ekr.20100128091412.5385: ** init
def init():

    ok = not g.app.unitTesting # Not for unit testing.

    if ok:
        # Register the handlers...
        leoPlugins.registerHandler("start2", onStart)
        g.plugin_signon(__name__)

    return ok
#@+node:edream.110203113231.733: ** onStart
def onStart (tag,keywords):

    try:
        import gc
        gc.set_debug(gc.DEBUG_LEAK)
    except: pass
#@-others
#@-leo
