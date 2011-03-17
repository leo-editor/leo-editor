#@+leo-ver=5-thin
#@+node:tbrown.20100318101414.5990: * @file viewrendered.py
#@+<< docstring >>
#@+node:tbrown.20100318101414.5991: ** << docstring >>
''' Creates a window for *live* rendering of rst, html, etc.  (Qt only).

viewrendered.py creates the following (``Alt-X``) commands:

``viewrendered``
    opens a new window where the current body text is rendered as HTML
    (if it starts with '<'), or otherwise reStructuredText.
``viewrendered-big``
    as above, but zoomed in, useful for presentations
``viewrendered-html``
    displays the html source generated from reStructuredText, useful for
    debugging

``viewrendered`` sets the process current directory (os.chdir()) to the path
to the node being rendered, to allow relative paths to work in
``.. image::`` directives.

reStructuredText errors and warnings may be shown.  For example, both::

    Heading
    -------

    `This` is **really** a line of text.

and::

    <h1>Heading<h1>

    <tt>This</tt> is <b>really</b> a line of text.

will look something like:

**Heading**

`This` is **really** a line of text.

'''
#@-<< docstring >>

__version__ = '0.1'

#@+<< imports >>
#@+node:tbrown.20100318101414.5993: ** << imports >>
import leo.core.leoGlobals as g

g.assertUi('qt')

import sys
import os
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
#@+<< define stylesheet >>
#@+node:ekr.20110317024548.14377: ** << define stylesheet >>
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
#@-<< define stylesheet >>

controllers = {} # Keys are c.hash(): values are PluginControllers

#@+others
#@+node:tbrown.20100318101414.5994: ** decorate_window
def decorate_window(w):
    
    w.setStyleSheet(stickynote_stylesheet)
    w.setWindowIcon(QIcon(g.app.leoDir + "/Icons/leoapp32.png"))    
    w.resize(600, 300)
#@+node:tbrown.20100318101414.5995: ** init
def init ():

    g.viewrendered_count = 0
    g.plugin_signon(__name__)
    g.registerHandler('after-create-leo-frame',onCreate)

    return True
#@+node:ekr.20110317024548.14376: ** onCreate
def onCreate (tag, keys):
    
    global controllers
    
    c = keys.get('c')
    if c:
        controllers[c.hash()] = PluginController(c)
#@+node:ekr.20110317024548.14375: ** class PluginController
class PluginController:
    
    def __init__ (self,c):
        
        self.c = c
        self.viewrendered = c.viewrendered = ViewRendered(c)
        
    def view (self,big=False,html=False):
        self.viewrendered.view(big=big,html=html)
#@+node:tbrown.20100318101414.5997: ** class ViewRendered(QTextEdit)
class ViewRendered(QTextEdit):

    #@+others
    #@+node:ekr.20101112195628.5429: *3* __init__ & __del_& activate
    def __init__(self,c):  ###, view_html=False):
        
        g.trace('(ViewRendered)',c)

        QTextEdit.__init__(self)
        self.inited = False
        self.length = 0
        self.gnx = 0
        self.setReadOnly(True)
        self.c = c
        ### self.view_html = None ### view_html
        # c.viewrendered = self
        
    def activate (self):
        if not self.inited:
            self.inited = True
            g.registerHandler('select2',self.update)
            g.registerHandler('idle',self.update)
            g.enableIdleTimeHook(idleTimeDelay=1000)
            g.viewrendered_count += 1
            self.view()
            # self.show()
            # self.update(tag='activate', {'c':c})

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
    #@+node:ekr.20110317024548.14379: *3* view (new)
    def view(self,big=False,html=False):
        
        if not self.inited:
            self.activate()

        self.show()
        self.update(tag='view',keywords={'c':self.c,'html':html})
        if big:
            self.zoomIn(4)
    #@+node:ekr.20101112195628.5426: *3* update
    def update(self,tag,keywords):
        
        # if tag != 'idle': g.trace(tag,keywords)

        if keywords['c'] != self.c:
            return  # not our problem
        html = keywords.get('html')

        p = self.c.currentPosition()
        b = p.b.strip()
        self.setWindowTitle(p.h)

        if self.gnx == p.v.gnx and len(b) == self.length:
            return  # no change

        self.gnx = p.v.gnx
        self.length = len(b)

        if got_docutils and not b.startswith('<'):

            path = g.scanAllAtPathDirectives(self.c,p) or self.c.getNodePath(p)
            if not os.path.isdir(path):
                path = os.path.dirname(path)
            if os.path.isdir(path):
                os.chdir(path)

            try:
                b = publish_string(b, writer_name='html')
                s = g.toUnicode(b) # 2011/03/15
            except SystemMessage as sm:
                if 0:
                    g.trace(sm)
                    print(sm.args)
                    msg = sm.args[0]
                    if 'SEVERE' in msg or 'FATAL' in msg:
                        s = 'RST rendering failed with\n\n  %s\n\n%s' % (msg,s)
                self.setPlainText(s)
                return

        if html: ### self.view_html:
            self.setPlainText(s)
        else:
            # self.setHtml(g.toUnicode(b))
            self.setHtml(s)
    #@-others
#@+node:tbrown.20100318101414.5998: ** g.command('viewrendered')
@g.command('viewrendered')
def viewrendered(event):
    """Open render view for commander"""

    c = event.get('c')
    if c:
        # ViewRendered(c)
        pc = controllers.get(c.hash())
        if pc: pc.view()
#@+node:tbrown.20101127112443.14856: ** g.command('viewrendered-html')
@g.command('viewrendered-html')
def viewrendered(event):
    """Open view of html which would be rendered"""

    c = event.get('c')
    if c:
        # ViewRendered(c, view_html=True)
        pc = controllers.get(c.hash())
        if pc: pc.view(html=True)
#@+node:tbrown.20101127112443.14854: ** g.command('viewrendered-big')
@g.command('viewrendered-big')
def viewrendered(event):
    """Open render view for commander, with big text

    (useful for presentations)

    """

    c = event.get('c')
    if c:
        # vr = ViewRendered(c)
        # vr.zoomIn(4)
        pc = controllers.get(c.hash())
        if pc: pc.view(big=True)
#@-others
#@-leo
