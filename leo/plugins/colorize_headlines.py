#@+leo-ver=5-thin
#@+node:ville.20090310191936.10: * @file colorize_headlines.py
''' Manipulates appearance of individual tree widget items. (Qt only).

This plugin is mostly an example of how to change the appearance of headlines. As
such, it does a relatively mundane chore of highlighting @thin, @auto, @shadow
nodes in bold.

'''
# By VMV.
#@+<< imports >>
#@+node:ville.20090310191936.13: ** << imports >>
import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins
    # Uses leoPlugins.TryNext.
#@-<< imports >>
#@+others
#@+node:ville.20090310191936.14: ** init
def init ():
    '''Return True if the plugin has loaded successfully.'''
    ok = g.app.gui.guiName() == "qt"
    if ok:
        g.visit_tree_item.add(colorize_headlines_visitor)
    return ok
#@+node:ville.20090310191936.19: ** colorize_headlines_visitor
def colorize_headlines_visitor(c,p, item):
    """ Changes @thin, @auto, @shadow to bold """
    t = p.h.split(None, 1)
    if t and t[0] in ['@file','@thin', '@auto', '@shadow']:
        f = item.font(0)
        f.setBold(True)
        item.setFont(0,f)
    raise leoPlugins.TryNext
#@-others
#@@language python
#@@tabwidth -4
#@-leo
