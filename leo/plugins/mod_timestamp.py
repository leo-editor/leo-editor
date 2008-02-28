#@+leo-ver=4-thin
#@+node:edream.110203113231.727:@thin mod_timestamp.py
"""Timestamp all save operations to show when they occur"""

#@@language python
#@@tabwidth -4

# By Paul Paterson.
import leoGlobals as g
import leoPlugins

import time

#@+others
#@+node:edream.110203113231.728:timestamp
def timestamp(tag=None, keywords=None):

    cmd = keywords.get('label','save')

    if cmd.startswith("save") or cmd.startswith("tangle"):
        g.es("%s: %s" % (cmd, time.ctime()))
#@-node:edream.110203113231.728:timestamp
#@-others

if 1: # OK for unit testing.

    # Register the handlers...
    leoPlugins.registerHandler("command1", timestamp)
    __version__ = "0.1"
    g.plugin_signon(__name__)
#@nonl
#@-node:edream.110203113231.727:@thin mod_timestamp.py
#@-leo
