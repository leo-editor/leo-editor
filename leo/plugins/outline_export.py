#@+leo-ver=5-thin
#@+node:edream.110203113231.720: * @file outline_export.py
"""Modifies the way exported outlines are written."""

#@@language python
#@@tabwidth -4

import leo.core.leoGlobals as g

__version__ = "1.2" # Set version for the plugin handler.

#@+others
#@+node:ekr.20100128073941.5375: ** init
def init():
    '''Return True if the plugin has loaded successfully.'''
    ok = not g.app.unitTesting # Not for unit testing: modifies core class.
    if ok:
        g.registerHandler("start2", onStart)
        g.plugin_signon(__name__)
    return ok
#@+node:edream.110203113231.721: ** newMoreHead
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
    s += "+ " if v.hasChildren() else "- "
    s += v.h
    return s
#@+node:ekr.20100128073941.5376: ** onStart
def onStart (tag,keywords):

    import leo.core.leoNodes as leoNodes

    g.funcToMethod(newMoreHead,leoNodes.VNode,"moreHead")
#@-others
#@-leo
