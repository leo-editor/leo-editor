#@+leo-ver=4-thin
#@+node:edream.110203113231.924:@thin redirect_to_log.py
"""Send all output to the log pane"""

#@@language python
#@@tabwidth -4

import leoGlobals as g
import leoPlugins

def onStart (tag,keywords):
    g.redirectStdout() # Redirect stdout
    g.redirectStderr() # Redirect stderr

if not g.app.unitTesting: # Not for unit tests.

    # Register the handlers...
    leoPlugins.registerHandler("start2", onStart)

    __version__ = "1.3"
    g.plugin_signon(__name__)
#@nonl
#@-node:edream.110203113231.924:@thin redirect_to_log.py
#@-leo
