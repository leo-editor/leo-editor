#@+leo-ver=5-thin
#@+node:edream.110203113231.735: * @file trace_gc_plugin.py
""" Traces changes to Leo's objects at idle time."""

#@@language python
#@@tabwidth -4

import leo.core.leoGlobals as g

__version__ = "1.3"

g.debugGC = True # Force debugging on.
gcCount = 0

#@+others
#@+node:ekr.20100128091412.5386: ** init
def init():
    '''Return True if the plugin has loaded successfully.'''
    ok = not g.app.unitTesting # Not for unit testing.
    if ok: # Register the handlers...
        if 1: # Very effective.
            g.registerHandler("idle", printIdleGC)
        else: # Very precise.
            g.registerHandler("all", printIdleGC)
        if 0: # Another idea.
            g.registerHandler("command2", printIdleRefs)
        g.plugin_signon(__name__)
    return ok
#@+node:ekr.20050111084900: ** printIdleRefs
def printIdleRefs(tag,keywords):

    g.printGcRefs(tag)
#@+node:ekr.20050111084900.1: ** printIdleGC
def printIdleGC(tag,keywords):

    # Calling printGc is too expensive to do on every idle call.
    if g.app.killed:
        return
    elif tag == "idle":
        global gcCount ; gcCount += 1
        if (gcCount % 20) == 0:
            g.printGc(tag)
    else:
        g.printGc(tag)
#@-others
#@-leo
