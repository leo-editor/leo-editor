#@+leo-ver=5-thin
#@+node:tbrown.20100318101414.5990: * @file viewrendered.py
#@+<< docstring >>
#@+node:tbrown.20100318101414.5991: ** << docstring >>
''' Creates a window for *live* rendering of rst, html, etc.  Qt only.

viewrendered.py creates a single ``Alt-X`` style command, ``viewrendered``,
which opens a new window where the current body text is rendered as HTML
(if it starts with '<'), or otherwise reStructuredText.  reStructuredText
errors and warnings may be shown.

So both::

    Heading
    -------

    `This` is **really** a line of text.

and::

    <h1>Heading<h1>

    <tt>This</tt> is <b>really</b> a line of text.

will look something like:

Heading
-------

`This` is **really** a line of text.

'''
#@-<< docstring >>

__version__ = '0.1'

#@+<< imports >>
#@+node:tbrown.20100318101414.5993: ** << imports >>
import leo.core.leoGlobals as g

g.assertUi('qt')

import sys
import webbrowser

try:
    from docutils.core import publish_string
    from docutils.utils import SystemMessage
    got_docutils = True
except ImportError:
    got_docutils = False

from PyQt4.QtCore import (QSize, QVariant, Qt, SIGNAL, QTimer)
from PyQt4.QtGui import (QAction, QApplication, QColor, QFont,
        QFontMetrics, QIcon, QKeySequence, QMenu, QPixmap, QTextCursor,
        QTextCharFormat, QTextBlockFormat, QTextListFormat,QTextEdit,
        QPlainTextEdit, QInputDialog)
#@-<< imports >>

#@+others
#@+node:tbrown.20100318101414.5994: ** styling
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
    w.setWindowIcon(QIcon(g.app.leoDir + "/Icons/leoapp32.png"))    
    w.resize(600, 300)
#@+node:tbrown.20100318101414.5995: ** init
def init ():

    g.viewrendered_count = 0
    g.plugin_signon(__name__)

    return True
#@+node:tbrown.20100318101414.5997: ** class ViewRendered(QTextEdit)
class ViewRendered(QTextEdit):

    #@+others
    #@+node:ekr.20101112195628.5429: *3* __init__ & __del__
    def __init__(self, c):

        QTextEdit.__init__(self)
        self.length = 0
        self.gnx = 0
        self.setReadOnly(True)
        self.c = c
        c.viewrendered = self
        g.registerHandler('select2',self.update)
        g.registerHandler('idle',self.update)
        g.enableIdleTimeHook(idleTimeDelay=1000)
        g.viewrendered_count += 1
        self.show()
        self.update(None, {'c':c})

    def __del__(self):

        self.close()
    #@+node:ekr.20101112195628.5430: *3* close & closeEvent
    def close(self):

        if g.viewrendered_count > 0:
            g.viewrendered_count -= 1
        if g.viewrendered_count <= 0:
            g.disableIdleTimeHook()
        g.unregisterHandler('select2',self.update)
        g.unregisterHandler('idle',self.update)
        self.setVisible(False)
        self.destroy()  # if this doesn't work, hopefully it's hidden
        if hasattr(self.c, 'viewrendered'):
            del self.c.viewrendered

    def closeEvent(self, event):

        event.accept()        
        self.close()
    #@+node:ekr.20101112195628.5426: *3* update
    def update(self, tag, keywords):

        if keywords['c'] != self.c:
            return  # not our problem

        p = self.c.currentPosition()
        b = p.b.strip()
        self.setWindowTitle(p.h)

        if self.gnx == p.v.gnx and len(b) == self.length:
            return  # no change

        self.gnx = p.v.gnx
        self.length = len(b)

        if got_docutils and not b.startswith('<'):
            try:
                b = publish_string(b, writer_name='html')
            except SystemMessage as sm:
                g.trace(sm)
                print(sm.args)
                msg = sm.args[0]
                if 'SEVERE' in msg or 'FATAL' in msg:
                    b = 'RST rendering failed with\n\n  %s\n\n%s' % (msg,b)
                    self.setPlainText(b)
                    return

        self.setHtml(g.toUnicode(b))
    #@-others
#@+node:tbrown.20100318101414.5998: ** g.command('viewrendered')
@g.command('viewrendered')
def viewrendered(event):
    """Open render view for commander"""

    c = event['c']

    ViewRendered(c)

@g.command('viewrendered-big')
def viewrendered(event):
    """Open render view for commander, with big text

    (useful for presentations)

    """

    c = event['c']

    vr = ViewRendered(c)
    vr.zoomIn(4)
#@-others
#@-leo
