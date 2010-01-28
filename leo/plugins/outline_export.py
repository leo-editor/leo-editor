#@+leo-ver=4-thin
#@+node:edream.110203113231.720:@thin outline_export.py
"""Modify the way exported outlines are displayed"""

#@@language python
#@@tabwidth -4

import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins

__version__ = "1.2" # Set version for the plugin handler.

#@+others
#@+node:ekr.20100128073941.5375:init
def init():

    ok = not g.app.unitTesting # Not for unit testing: modifies core class.

    if ok:

        # Register the handlers...
        leoPlugins.registerHandler("start2", onStart)
        g.plugin_signon(__name__)

    return ok
#@nonl
#@-node:ekr.20100128073941.5375:init
#@+node:edream.110203113231.721:newMoreHead
# Returns the headline string in MORE format.

def newMoreHead (self,firstLevel,useVerticalBar=True):

    useVerticalBar = True # Force the vertical bar

    v = self
    level = self.level() - firstLevel
    if level > 0:
        if useVerticalBar:
            s = " |\t" * level
        else:
            s = "\t"
    else:
        s = ""
    s += g.choose(v.hasChildren(), "+ ", "- ")
    s += v.h
    return s
#@-node:edream.110203113231.721:newMoreHead
#@+node:ekr.20100128073941.5376:onStart
def onStart (tag,keywords):

    import leo.core.leoNodes as leoNodes

    g.funcToMethod(newMoreHead,leoNodes.vnode,"moreHead")
#@nonl
#@-node:ekr.20100128073941.5376:onStart
#@-others
#@-node:edream.110203113231.720:@thin outline_export.py
#@-leo
