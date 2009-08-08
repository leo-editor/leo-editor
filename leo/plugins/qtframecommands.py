#@+leo-ver=4-thin
#@+node:ville.20090808222331.5229:@thin qtframecommands.py
#@<< docstring >>
#@+node:ville.20090808222331.5230:<< docstring >>
''' Various commands to manipulate GUI under qt
'''
#@-node:ville.20090808222331.5230:<< docstring >>
#@nl

__version__ = '0.0'
#@<< version history >>
#@+node:ville.20090808222331.5231:<< version history >>
#@@killcolor
#@+at
# 
# Put notes about each version here.
#@-at
#@nonl
#@-node:ville.20090808222331.5231:<< version history >>
#@nl

#@<< imports >>
#@+node:ville.20090808222331.5232:<< imports >>
import leo.core.leoGlobals as g
from leo.core import leoPlugins 
# Whatever other imports your plugins uses.
#@nonl
#@-node:ville.20090808222331.5232:<< imports >>
#@nl

#@+others
#@+node:ville.20090808222331.5233:init
def init ():

    ok = True

    if ok:
        #leoPlugins.registerHandler('start2',onStart2)
        g.plugin_signon(__name__)

    leoPlugins.registerHandler("select2", onSelect)
    return ok

def onSelect(tag,keywords):
    c = keywords.get('c') or keywords.get('new_c')    
    wdg = c.frame.top.leo_body_frame
    wdg.setWindowTitle(c.p.h)

#@-node:ville.20090808222331.5233:init
#@+node:ville.20090808222331.5236:detach-editor-toggle
@g.command('detach-editor-toggle')
def detach_editor_toggle(event):
    c = event['c']
    #g.pdb()
    detach = True
    try:
        if c.frame.detached_body_info is not None:
            detach = False
    except AttributeError:
        pass

    if detach:
        detach_editor(c)
    else:
        undetach_editor(c)

def detach_editor(c):
    wdg = c.frame.top.leo_body_frame
    parent = wdg.parent()
    if parent is None:
        # just show if already detached
        wdg.show()
        return

    c.frame.detached_body_info = parent, parent.sizes()
    wdg.setParent(None)
    wdg.show()

def undetach_editor(c):
    wdg = c.frame.top.leo_body_frame
    parent, sizes = c.frame.detached_body_info
    parent.addWidget(wdg)
    wdg.show()
    parent.setSizes(sizes)
    c.frame.detached_body_info = None

#@-node:ville.20090808222331.5236:detach-editor-toggle
#@-others
#@nonl
#@-node:ville.20090808222331.5229:@thin qtframecommands.py
#@-leo
