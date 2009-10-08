#@+leo-ver=4-thin
#@+node:ville.20091008210853.5241:@thin stickynotes.py
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

g.assertUi('qt')

from PyQt4 import QtGui, QtCore
#@nonl
#@-node:vivainio2.20091008133028.5823:<< imports >>
#@nl

#@+others
#@+node:vivainio2.20091008140054.14555:styling
stickynote_stylesheet = """
/* The body pane */
QPlainTextEdit {
    background-color: #fdf5f5; /* A kind of pink. */
    selection-color: white;
    selection-background-color: lightgrey;
    font-family: DejaVu Sans Mono;
    /* font-family: Courier New; */
    font-size: 12px;
    font-weight: normal; /* normal,bold,100,..,900 */
    font-style: normal; /* normal,italic,oblique */
}
"""

def decorate_window(w):
    w.setStyleSheet(stickynote_stylesheet)
    w.setWindowIcon(QtGui.QIcon(g.app.leoDir + "/Icons/leoapp32.png"))    
    w.resize(600, 300)

#@-node:vivainio2.20091008140054.14555:styling
#@+node:vivainio2.20091008133028.5824:init
def init ():

    ok = True

    if ok:
        #leoPlugins.registerHandler('start2',onStart2)
        g.plugin_signon(__name__)

    g.app.stickynotes = {}    
    return ok
#@-node:vivainio2.20091008133028.5824:init
#@+node:ville.20091008210853.7616:class StickyNote
class FocusingPlaintextEdit(QtGui.QPlainTextEdit):

    def __init__(self, focusin, focusout):
        QtGui.QPlainTextEdit.__init__(self)        
        self.focusin = focusin
        self.focusout = focusout

    def focusOutEvent ( self, event ):
        #print "focus out"
        self.focusout()

    def focusInEvent ( self, event ):        
        self.focusin()





#@-node:ville.20091008210853.7616:class StickyNote
#@+node:vivainio2.20091008133028.5825:g.command('stickynote')
@g.command('stickynote')
def stickynote_f(event):
    """ Launch editable 'sticky note' for the node """

    c= event['c']
    p = c.p
    v = p.v
    def focusin():
        #print "focus in"
        if v is c.p.v:
            nf.setPlainText(v.b)
            nf.setWindowTitle(p.h)
            nf.dirty = False


    def focusout():
        #print "focus out"
        if not nf.dirty:
            return
        v.b = nf.toPlainText()
        v.setDirty()
        nf.dirty = False
        p = c.p
        if p.v is v:
            c.selectPosition(c.p)


    nf = FocusingPlaintextEdit(focusin, focusout)
    nf.dirty = False
    decorate_window(nf)
    nf.setWindowTitle(p.h)
    nf.setPlainText(p.b)
    p.setDirty()

    def textchanged_cb():
        nf.dirty = True

    nf.connect(nf,
        QtCore.SIGNAL("textChanged()"),textchanged_cb)

    nf.show()

    g.app.stickynotes[p.gnx] = nf
#@-node:vivainio2.20091008133028.5825:g.command('stickynote')
#@-others
#@nonl
#@-node:ville.20091008210853.5241:@thin stickynotes.py
#@-leo
