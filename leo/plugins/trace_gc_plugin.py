#@+leo-ver=4-thin
#@+node:edream.110203113231.735:@thin trace_gc_plugin.py
"""Trace changes to Leo's objects at idle time"""

#@@language python
#@@tabwidth -4

import leoGlobals as g
import leoPlugins

g.debugGC = True # Force debugging on.
gcCount = 0

#@+others
#@+node:ekr.20050111084900:printIdleRefs
def printIdleRefs(tag,keywords):

    g.printGcRefs(verbose=False)
#@nonl
#@-node:ekr.20050111084900:printIdleRefs
#@+node:ekr.20050111084900.1:printIdleGC
def printIdleGC(tag,keywords):

    # Calling printGc is too expensive to do on every idle call.
    if g.app.killed:
        return # Work around a Tk bug.
    elif tag == "idle":
        global gcCount ; gcCount += 1
        if (gcCount % 20) == 0:
            g.printGc(tag,onlyPrintChanges=True)
    else:
        g.printGc(tag,onlyPrintChanges=False)
#@nonl
#@-node:ekr.20050111084900.1:printIdleGC
#@-others

if not g.app.unitTesting: # Not for unit testing.

    # Register the handlers...
    if 1: # Very effective.
        leoPlugins.registerHandler("idle", printIdleGC)
    else: # Very precise.
        leoPlugins.registerHandler("all", printIdleGC)
    if 0: # Another idea.
        leoPlugins.registerHandler("command2", printIdleRefs)

    __version__ = "1.3"
    g.plugin_signon(__name__)
#@nonl
#@-node:edream.110203113231.735:@thin trace_gc_plugin.py
#@-leo
