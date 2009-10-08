#@+leo-ver=4-thin
#@+node:vivainio2.20091008133028.5820:@thin stickynotes.py
#@<< docstring >>
#@+node:vivainio2.20091008133028.5821:<< docstring >>
''' Simple "sticky notes" feature (popout editors)

alt-x stickynote to pop out current node as a note

'''
#@-node:vivainio2.20091008133028.5821:<< docstring >>
#@nl

__version__ = '0.0'
#@<< version history >>
#@+node:vivainio2.20091008133028.5822:<< version history >>
#@@killcolor
#@+at
# 
# Put notes about each version here.
#@-at
#@nonl
#@-node:vivainio2.20091008133028.5822:<< version history >>
#@nl

#@<< imports >>
#@+node:vivainio2.20091008133028.5823:<< imports >>
import leo.core.leoGlobals as g
from leo.core import leoPlugins 
# Whatever other imports your plugins uses.
#@nonl
#@-node:vivainio2.20091008133028.5823:<< imports >>
#@nl

#@+others
#@+node:vivainio2.20091008133028.5824:init
def init ():

    ok = True

    if ok:
        #leoPlugins.registerHandler('start2',onStart2)
        g.plugin_signon(__name__)

    g.app.stickynotes = {}    
    return ok
#@-node:vivainio2.20091008133028.5824:init
#@+node:vivainio2.20091008133028.5825:g.command('stickynote')
@g.command('stickynote')
def stickynote_f(event):
    from PyQt4 import QtGui
    c= event['c']
    p = c.p
    nf = QtGui.QTextEdit()
    nf.setPlainText(p.b)
    nf.show()
    nf.setWindowTitle(p.h)
    g.app.stickynotes[p.gnx] = nf



#@-node:vivainio2.20091008133028.5825:g.command('stickynote')
#@-others
#@nonl
#@-node:vivainio2.20091008133028.5820:@thin stickynotes.py
#@-leo
