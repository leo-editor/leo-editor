#@+leo-ver=5-thin
#@+node:edream.110203113231.741: * @thin add_directives.py
"""Support new @direcives"""

#@@language python
#@@tabwidth -4

__version__ = "1.2"

import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins

directives = "markup", # A tuple with one string.

#@+others
#@+node:ekr.20070725103420: ** init
def init ():

    ok = True # not  g.app.unitTesting:

    # Register the handlers...
    leoPlugins.registerHandler("start1",addPluginDirectives)
    # leoPlugins.registerHandler("scan-directives",scanPluginDirectives)
    g.plugin_signon(__name__)

    return ok
#@+node:edream.110203113231.742: ** addPluginDirectives
def addPluginDirectives (tag,keywords):

    """Add all new directives to g.globalDirectiveList"""

    global directives

    for s in directives:
        if s.startswith('@'): s = s[1:]
        if s not in g.globalDirectiveList:
            # g.trace(s)
            g.globalDirectiveList.append(s)
#@+node:edream.110203113231.743: ** scanPluginDirectives (no longer used)
def scanPluginDirectives (tag, keywords):

    """Add a tuple (d,v,s,k) to list for every directive d found"""

    global directives

    keys = ("c","p","s","theDict","pluginsList")
    c,p,s,theDict,pluginsList = [keywords.get(key) for key in keys]

    for d in directives:
        if d in theDict:
            # Point k at whatever follows the directive.
            s = theDict.get(d)
            g.trace('s',s)
            kind = d
            pluginsList.append((kind,p.v,s),)
#@-others
#@-leo
