#@+leo-ver=5-thin
#@+node:edream.110203113231.736: * @file ../plugins/trace_keys.py
""" Traces keystrokes in the outline and body panes."""

from leo.core import leoGlobals as g

#@+others
#@+node:ekr.20100128091412.5387: ** init
def init():
    '''Return True if the plugin has loaded successfully.'''
    ok = not g.app.unitTesting # Not for unit testing.
    if ok:
        g.registerHandler(("bodykey1", "bodykey2", "headkey1", "headkey2"), onKey)
        g.plugin_signon(__name__)
    return ok
#@+node:edream.110203113231.737: ** onKey
def onKey(tag, keywords):
    ch = keywords.get("ch")
    if ch:
        g.es("key", repr(ch))
#@-others
#@@language python
#@@tabwidth -4
#@-leo
