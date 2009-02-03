#@+leo-ver=4-thin
#@+node:edream.110203113231.734:@thin quit_leo.py
"""A plugin showing how to force Leo to quit."""

#@@language python
#@@tabwidth -4

import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins

if not g.app.unitTesting: # Not for unit testing.

    def forceLeoToQuit(tag,keywords):
        if not g.app.initing:
            g.pr("forceLeoToQuit",tag)
            g.app.forceShutdown()

    if 0: # Force a shutdown during startup.
        g.pr("quitting during startup")
        g.app.forceShutdown()

    if 1: # Force a shutdown at any other time, even "idle" time.

        # Exception: do not call g.app.forceShutdown in a "start2" hook.

        g.pr(__doc__)
        leoPlugins.registerHandler("idle",forceLeoToQuit)

        __version__ = "1.2"
        g.plugin_signon(__name__)
#@nonl
#@-node:edream.110203113231.734:@thin quit_leo.py
#@-leo
