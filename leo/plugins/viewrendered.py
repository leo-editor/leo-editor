#@+leo-ver=5-thin
#@+node:tbrown.20100318101414.5990: * @thin viewrendered.py
#@+<< docstring >>
#@+node:tbrown.20100318101414.5991: ** << docstring >>
'''Rendered rst, html, etc., *live*, in another window.  Qt only.

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

__version__ = '0.0'
#@+<< version history >>
#@+node:tbrown.20100318101414.5992: ** << version history >>
#@@killcolor
#@+at
# 
# Put notes about each version here.
#@-<< version history >>

#@+<< imports >>
#@+node:tbrown.20100318101414.5993: ** << imports >>
import leo.core.leoGlobals as g

# Whatever other imports your plugins uses.

g.assertUi('qt')

import sys
import webbrowser

try:
    from docutils.core import publish_string
    from docutils.utils import SystemMessage
    got_docutils = True
except ImportError:
    got_docutils = False

from PyQt4.QtCore import (QSize, QString, QVariant, Qt, SIGNAL, QTimer)
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

    ok = True

    if ok:
        #g.app.pluginsController.registerHandler('start2',onStart2)
        g.plugin_signon(__name__)

        g.viewrendered_count = 0

    return ok
#@+node:tbrown.20100318101414.5997: ** class ViewRendered
class ViewRendered(QTextEdit):

    def __init__(self, c):
        QTextEdit.__init__(self)

        self.length = 0
        self.gnx = 0

        self.setReadOnly(True)
        self.c = c
        c.viewrendered = self

        g.app.pluginsController.registerHandler('select2',self.update)
        g.app.pluginsController.registerHandler('idle',self.update)
        g.enableIdleTimeHook(idleTimeDelay=1000)
        g.viewrendered_count += 1

        self.show()

        self.update(None, {'c':c})

    def __del__(self):

        self.close()

    def close(self):

        if g.viewrendered_count > 0:
            g.viewrendered_count -= 1
        if g.viewrendered_count <= 0:
            g.disableIdleTimeHook()
        g.app.pluginsController.unregisterHandler('select2',self.update)
        g.app.pluginsController.unregisterHandler('idle',self.update)
        self.setVisible(False)
        self.destroy()  # if this doesn't work, hopefully it's hidden
        if hasattr(self.c, 'viewrendered'):
            del self.c.viewrendered

    def closeEvent(self, event):
        event.accept()        
        self.close()

    def update(self, tag, keywords):

        if keywords['c'] != self.c:
            return  # not out problem

        p = self.c.currentPosition()
        b = p.b.strip()

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

        self.setHtml(b)
#@+node:tbrown.20100318101414.5998: ** g.command('viewrendered')
@g.command('viewrendered')
def viewrendered(event):
    """Open render view for commander"""

    c = event['c']

    ViewRendered(c)
#@-others
#@-leo
