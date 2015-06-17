#@+leo-ver=5-thin
#@+node:edream.110203113231.734: * @file quit_leo.py
""" Shows how to force Leo to quit."""
#@@language python
#@@tabwidth -4
import leo.core.leoGlobals as g

def init():
    '''Return True if the plugin has loaded successfully.'''
    ok = not g.app.unitTesting # Not for unit testing.
    if ok:

        def forceLeoToQuit(tag, keywords):
            if not g.app.initing:
                g.pr("forceLeoToQuit", tag)
                g.app.forceShutdown()
        # Force a shutdown at any other time, even "idle" time.
        # Exception: do not call g.app.forceShutdown in a "start2" hook.

        g.pr(__doc__)
        g.registerHandler("idle", forceLeoToQuit)
        g.plugin_signon(__name__)
    return ok
#@-leo
