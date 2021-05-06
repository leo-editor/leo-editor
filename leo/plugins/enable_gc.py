#@+leo-ver=5-thin
#@+node:edream.110203113231.732: * @file ../plugins/enable_gc.py
"""Enables debugging and tracing for Python's garbage collector."""

from leo.core import leoGlobals as g

#@+others
#@+node:ekr.20100128091412.5385: ** init
def init():
    '''Return True if the plugin has loaded successfully.'''
    ok = not g.app.unitTesting # Not for unit testing.
    if ok:
        g.registerHandler("start2", onStart)
        g.plugin_signon(__name__)
    return ok
#@+node:edream.110203113231.733: ** onStart
def onStart(tag, keywords):
    try:
        import gc
        gc.set_debug(gc.DEBUG_LEAK)
    except Exception:
        pass
#@-others
#@@language python
#@@tabwidth -4
#@-leo
