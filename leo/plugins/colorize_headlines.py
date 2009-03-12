#@+leo-ver=4-thin
#@+node:ville.20090310191936.10:@thin colorize_headlines.py
#@<< docstring >>
#@+node:ville.20090310191936.11:<< docstring >>
'''A plugin that manipulates appearance of individual tree widget items

'''
#@-node:ville.20090310191936.11:<< docstring >>
#@nl

__version__ = '0.1'
#@<< version history >>
#@+node:ville.20090310191936.12:<< version history >>
#@@killcolor
#@+at
# 
# v 0.1: Initial version.
#@-at
#@nonl
#@-node:ville.20090310191936.12:<< version history >>
#@nl

#@<< imports >>
#@+node:ville.20090310191936.13:<< imports >>
import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins

# Whatever other imports your plugins uses.
#@nonl
#@-node:ville.20090310191936.13:<< imports >>
#@nl

#@+others
#@+node:ville.20090310191936.14:init
def init ():

    ok = g.app.gui.guiName() == "qt"

    if ok:
        g.visit_tree_item.add(colorize_headlines_visitor)

    return ok
#@nonl
#@-node:ville.20090310191936.14:init
#@+node:ville.20090310191936.19:colorize_headlines_visitor
def colorize_headlines_visitor(c,p, item):
    """ Changes @thin, @auto, @shadow to bold """
    t = p.h.split(None, 1)
    if t and t[0] in ['@thin', '@auto', '@shadow']:
        f = item.font(0)
        f.setBold(True)
        item.setFont(0,f)
    raise leoPlugins.TryNext
#@-node:ville.20090310191936.19:colorize_headlines_visitor
#@-others
#@nonl
#@-node:ville.20090310191936.10:@thin colorize_headlines.py
#@-leo
