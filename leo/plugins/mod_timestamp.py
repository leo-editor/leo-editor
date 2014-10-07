#@+leo-ver=5-thin
#@+node:edream.110203113231.727: * @file mod_timestamp.py
""" Timestamps all save operations to show when they occur."""

#@@language python
#@@tabwidth -4

# By Paul Paterson.
import leo.core.leoGlobals as g

import time

__version__ = "0.1"

#@+others
#@+node:ekr.20100128073941.5374: ** init
def init():
    '''Return True if the plugin has loaded successfully.'''
    g.registerHandler("command1", timestamp)
    g.plugin_signon(__name__)
    return True # OK for unit testing.
#@+node:edream.110203113231.728: ** timestamp
def timestamp(tag=None, keywords=None):

    cmd = keywords.get('label','save')

    if cmd.startswith("save") or cmd.startswith("tangle"):
        g.es("%s: %s" % (cmd, time.ctime()))
#@-others
#@-leo
