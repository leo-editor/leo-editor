#@+leo-ver=5-thin
#@+node:edream.110203113231.730: * @file ../plugins/dump_globals.py
"""Dumps Python globals at startup."""
from leo.core import leoGlobals as g
#@+others
#@+node:ekr.20100128091412.5380: ** init
def init():
    '''Return True if the plugin has loaded successfully.'''
    ok = not g.unitTesting # Not for unit testing.
    if ok:
        g.registerHandler("start2", onStart)
        g.plugin_signon(__name__)
    return ok
#@+node:edream.110203113231.731: ** onStart
def onStart(tag, keywords):
    g.pr("\nglobals...")
    for s in globals():
        if s not in __builtins__:
            g.pr(s)
    g.pr("\nlocals...")
    for s in locals():
        if s not in __builtins__:
            g.pr(s)
#@-others
#@@language python
#@@tabwidth -4
#@-leo
