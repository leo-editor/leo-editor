#@+leo-ver=4-thin
#@+node:edream.110203113231.741:@thin add_directives.py
"""Support new @direcives"""

#@@language python
#@@tabwidth -4

__version__ = "1.2"

import leoGlobals as g
import leoPlugins

directives = "markup", # A tuple with one string.

#@+others
#@+node:ekr.20070725103420:init
def init ():

    ok = True # not  g.app.unitTesting:

    # Register the handlers...
    leoPlugins.registerHandler("start1",addPluginDirectives)
    leoPlugins.registerHandler("scan-directives",scanPluginDirectives)
    g.plugin_signon(__name__)

    return ok
#@nonl
#@-node:ekr.20070725103420:init
#@+node:edream.110203113231.742:addPluginDirectives
def addPluginDirectives (tag,keywords):

    """Add all new directives to g.globalDirectiveList"""

    global directives

    for s in directives:
        if s.startswith('@'): s = s[1:]
        if s not in g.globalDirectiveList:
            # g.trace(s)
            g.globalDirectiveList.append(s)
#@nonl
#@-node:edream.110203113231.742:addPluginDirectives
#@+node:edream.110203113231.743:scanPluginDirectives
def scanPluginDirectives (tag, keywords):

    """Add a tuple (d,v,s,k) to list for every directive d found"""

    global directives

    keys = ("c","v","s","old_dict","dict","pluginsList")
    c,v,s,old_dict,dict,pluginsList = [keywords.get(key) for key in keys]

    for d in directives:
        if not old_dict.has_key(d) and dict.has_key(d):
            # Point k at whatever follows the directive.
            s = dict.get(d)
            kind = d
            pluginsList.append((kind,v,s),)
#@-node:edream.110203113231.743:scanPluginDirectives
#@-others
#@-node:edream.110203113231.741:@thin add_directives.py
#@-leo
