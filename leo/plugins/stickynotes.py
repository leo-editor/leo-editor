#@+leo-ver=5-thin
#@+node:ekr.20100103093121.5329: * @file stickynotes.py
#@+<< docstring >>
#@+node:vivainio2.20091008133028.5821: ** << docstring >>
''' Adds simple "sticky notes" feature (popout editors) for Qt gui.

Adds the following (``Alt-X``) commands:

``stickynote``
  pop out current node as a sticky note
``stickynoter``
  pop out current node as a rich text note
``stickynoteenc``
  pop out current node as an encrypted note
``stickynoteenckey``
  enter a new en/decryption key
``stickynoterekey``
  enter the old key for the node, followed by the new, to change keys
``tabula``
  add the current node to the stickynotes in the `Tabula`
  sticky note dock window, and show the window
``tabula-show``
  show the`Tabula` sticky note dock window
  (without adding the current node)
``tabula-marked``
  add all marked nodes to the stickynotes in the `Tabula`
  sticky note dock window, and show the window

Sticky notes are synchronized (both ways) with their parent Leo node.

Encrypted mode requires the python-crypto module.

The first time you open a note in encrypted mode you'll be asked for a pass
phrase. That phrase will be used for the rest of the session, you can change it
with ``Alt-X`` ``stickynoteenckey``, but probably won't need to.

The encrypted note is stored in base64 encoded *encrypted* text in the parent
Leo node, if you forget the pass phrase there's no way to un-encrypt it again.
Also, you must not edit the text in the Leo node.

When **creating an encrypted note**, you should **start with an empty node**.
If you want to encrypt text that already exists in a node, select-all cut it to
empty the node, then paste it into the note.

If your data doesn't decode, you may need to upgrade your key.  Use the
``Alt-X`` ``stickynoterekey`` command on the encryted node in Leo.  Prefix
the old key with "v0:" (vee zero colon without the quotes).  Enter whatever
you want for the new key, even the old key again without the "v0:".
The decoded data should appear in the popoup window, if not, close the Leo
file **without saving**.  If you have multiple encoded nodes, repeat this
process for each one.

'''
#@-<< docstring >>

__version__ = '0.0'

#@+<< imports >>
#@+node:vivainio2.20091008133028.5823: ** << imports >>
import leo.core.leoGlobals as g

# Whatever other imports your plugins uses.

g.assertUi('qt')

import sys,os,time
import webbrowser

encOK = False
try:
    from Crypto.Cipher import AES
    from Crypto.Hash import MD5, SHA
    import base64
    import textwrap
    __ENCKEY = [None]
    encOK = True
except ImportError:
    pass

from PyQt4.QtCore import (QSize, QVariant, Qt, SIGNAL, QTimer)

try:
   from PyQt4.QtCore import QString
except ImportError:
   QString = str


from PyQt4.QtGui import (QAction, QApplication, QColor, QFont,
        QFontMetrics, QIcon, QKeySequence, QMenu, QPixmap, QTextCursor,
        QTextCharFormat, QTextBlockFormat, QTextListFormat,QTextEdit,
        QPlainTextEdit, QInputDialog, QMainWindow, QMdiArea, QLineEdit)

#@-<< imports >>

#@+others
#@+node:vivainio2.20091008140054.14555: ** styling
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

#@+node:vivainio2.20091008133028.5824: ** init
def init ():

    ok = True

    if ok:
        #g.registerHandler('start2',onStart2)
        g.plugin_signon(__name__)

    g.app.stickynotes = {}    
    return ok
#@+node:ville.20091008210853.7616: ** class FocusingPlainTextEdit
class FocusingPlaintextEdit(QPlainTextEdit):

    def __init__(self, focusin, focusout, closed = None, parent = None):
        QPlainTextEdit.__init__(self, parent)        
        self.focusin = focusin
        self.focusout = focusout
        self.closed = closed

    def focusOutEvent (self, event):
        #print "focus out"
        self.focusout()

    def focusInEvent (self, event):        
        self.focusin()

    def closeEvent(self, event):
        event.accept()
        if self.closed:
            self.closed()
        self.focusout()
#@+node:ville.20091023181249.5264: ** class SimpleRichText
class SimpleRichText(QTextEdit):
    def __init__(self, focusin, focusout):
        QTextEdit.__init__(self)        
        self.focusin = focusin
        self.focusout = focusout
        self.createActions()

        #self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)

    def focusOutEvent ( self, event ):
        #print "focus out"
        self.focusout()

    def focusInEvent ( self, event ):        
        self.focusin()


    def closeEvent(self, event):
        event.accept()        

    def createActions(self):
        self.boldAct = QAction(self.tr("&Bold"), self)
        self.boldAct.setCheckable(True)
        self.boldAct.setShortcut(self.tr("Ctrl+B"))
        self.boldAct.setStatusTip(self.tr("Make the text bold"))
        self.connect(self.boldAct, SIGNAL("triggered()"), self.setBold)
        self.addAction(self.boldAct)

        boldFont = self.boldAct.font()
        boldFont.setBold(True)
        self.boldAct.setFont(boldFont)

        self.italicAct = QAction(self.tr("&Italic"), self)
        self.italicAct.setCheckable(True)
        self.italicAct.setShortcut(self.tr("Ctrl+I"))
        self.italicAct.setStatusTip(self.tr("Make the text italic"))
        self.connect(self.italicAct, SIGNAL("triggered()"), self.setItalic)
        self.addAction(self.italicAct)

    def setBold(self):
        format = QTextCharFormat()
        if self.boldAct.isChecked():
                weight = QFont.Bold
        else:
                weight = QFont.Normal
        format.setFontWeight(weight)
        self.setFormat(format)

    def setItalic(self):
        format = QTextCharFormat()
        #format.setFontItalic(self.__italic.isChecked())
        format.setFontItalic(self.italicAct.isChecked())
        self.setFormat(format)

    def setUnderline(self):
        format = QTextCharFormat()
        format.setFontUnderline(self.__underline.isChecked())
        self.setFormat(format)

    def setFormat(self, format):
        self.textCursor().mergeCharFormat(format)
        self.mergeCurrentCharFormat(format)

    def bold(self):
        print("bold")

    def italic(self):
        print("italic")



#@+node:vivainio2.20091008133028.5825: ** g.command('stickynote')
@g.command('stickynote')
def stickynote_f(event):
    """ Launch editable 'sticky note' for the node """

    c = event['c']
    p = c.p
    nf = mknote(c,p)
#@+node:ville.20110304230157.6526: ** g.command('stickynote-new')
@g.command('stickynote-new')
def stickynote_f(event):
    """ Launch editable 'sticky note' for the node """

    c = event['c']
    p,wb = find_or_create_stickynotes()
    
    n = p.insertAsLastChild()
    c.redraw(n)
    n.h = time.asctime()
    
    nf = mknote(wb,n)
#@+node:ville.20110304230157.6527: ** get_workbook
def get_workbook():
    for co in g.app.commanders():
        if co.mFileName.endswith('workbook.leo'):
            return co

def find_or_create_stickynotes():
    wb = get_workbook()
    assert wb,'no wb'
    pl = wb.find_h('stickynotes')
    if not pl:
        p = wb.rootPosition().insertAfter()
        wb.redraw(p)
        p.h = "stickynotes"
    else:
        p = pl[0]
        
    return p, wb
                  
# print(get_workbook())       
#@+node:ville.20091023181249.5266: ** g.command('stickynoter')
@g.command('stickynoter')
def stickynoter_f(event):
    """ Launch editable 'sticky note' for the node """

    c= event['c']
    p = c.p
    v = p.v

    def focusin():
        print("focus in")
        if v is c.p.v:
            nf.setHtml(v.b)
            nf.setWindowTitle(p.h)
            nf.dirty = False

    def focusout():
        print("focus out")
        if not nf.dirty:
            return
        v.b = nf.toHtml()
        v.setDirty()
        nf.dirty = False
        p = c.p
        if p.v is v:
            c.selectPosition(c.p)

    nf = SimpleRichText(focusin, focusout)  # not LessSimpleRichText
    nf.dirty = False
    decorate_window(nf)
    nf.setWindowTitle(p.h)
    nf.setHtml(p.b)
    p.setDirty()

    def textchanged_cb():
        nf.dirty = True

    nf.connect(nf,
        SIGNAL("textChanged()"),textchanged_cb)

    nf.show()

    g.app.stickynotes[p.gnx] = nf
#@+node:tbrown.20100120100336.7829: ** g.command('stickynoteenc')
if encOK:    
    @g.command('stickynoterekey')
    def stickynoteenc_rk(event):
        stickynoteenc_f(event, rekey=True)

    @g.command('stickynoteenc')
    def stickynoteenc_f(event, rekey=False):
        """ Launch editable 'sticky note' for the encrypted node """

        if not encOK:
            g.es('no en/decryption - need python-crypto module')
            return

        if not __ENCKEY[0] or rekey:
            sn_getenckey()

        c= event['c']
        p = c.p
        v = p.v
        def focusin():
            #print "focus in"
            if v is c.p.v:
                if sn_decode(v.b) != nf.toPlainText():
                    # only when needed to avoid scroll jumping
                    nf.setPlainText(sn_decode(v.b))
                nf.setWindowTitle(p.h)
                nf.dirty = False

        def focusout():
            #print "focus out"
            if not nf.dirty:
                return
            v.b = sn_encode(str(nf.toPlainText()))
            v.setDirty()
            nf.dirty = False
            p = c.p
            if p.v is v:
                c.selectPosition(c.p)

        if rekey:
            unsecret = sn_decode(v.b)
            sn_getenckey()
            secret = sn_encode(unsecret)
            v.b = secret
            
        c = event['c']
        p = c.p
        nf = mknote(c,p)
        nf.focusout = focusout
        nf.focusin = focusin
        
        nf.setPlainText(sn_decode(v.b))
        
        if rekey:
            g.es("Key updated, data decoded with new key shown in window")
#@+node:tbrown.20100120100336.7830: ** sn_de/encode
if encOK:
    def sn_decode(s):
        return AES.new(__ENCKEY[0]).decrypt(base64.b64decode(s)).strip()

    def sn_encode(s):
        pad = ' '*(16-len(s)%16)
        return '\n'.join(textwrap.wrap(
            base64.b64encode(AES.new(__ENCKEY[0]).encrypt(s+pad)),
            break_long_words = True
        ))

    @g.command('stickynoteenckey')
    def sn_getenckey(dummy=None):
        txt,ok = QInputDialog.getText(None, 'Enter key', 'Enter key.\nData lost if key is lost.\nSee docs. for key upgrade notes.')
        if not ok:
            return
        
        if str(txt).startswith('v0:'):
            txt = QString(txt[3:])
        else:
            txt = unicode(txt)

        # arbitrary kludge to convert string to 256 bits - don't change
        sha = SHA.new()
        md5 = MD5.new()
        sha.update(txt)
        md5.update(txt)
        __ENCKEY[0] = sha.digest()[:16] + md5.digest()[:16]
        if len(__ENCKEY[0]) != 32:
            raise Exception("sn_getenckey failed to build key")
#@+node:ville.20100703234124.9976: ** Tabula
#@+node:ville.20100707205336.5610: *3* def create_subnode
def create_subnode(c, heading):
    """  Find node with heading, then add new node as child under this heading 

    Returns new position.


    """
    h = c.find_h(heading)
    if not h:
        p = c.rootPosition()
        p.moveToNodeAfterTree()
        p = p.insertAfter()
        p.h = heading
    else:
        p = h[0]

    chi = p.insertAsLastChild()
    return chi.copy()
#@+node:ville.20100703194946.5587: *3* def mknote
def mknote(c,p, parent=None):
    """ Launch editable 'sticky note' for the node """

    v = p.v
    def focusin():
        #print "focus in"
        if v is c.p.v:
            if v.b != nf.toPlainText():
                # only when needed to avoid scroll jumping
                nf.setPlainText(v.b)
            nf.setWindowTitle(v.h)
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


    def closeevent():
        pass
        # print "closeevent"


    nf = FocusingPlaintextEdit(focusin, focusout, closeevent, parent = parent)
    nf.setWindowIcon(QIcon(g.app.leoDir + "/Icons/leoapp32.png"))
    nf.dirty = False
    nf.resize(600, 300)
    nf.setWindowTitle(p.h)
    nf.setPlainText(p.b)
    p.setDirty()

    def textchanged_cb():
        nf.dirty = True

    nf.connect(nf,
        SIGNAL("textChanged()"),textchanged_cb)

    nf.show()

    g.app.stickynotes[p.gnx] = nf
    return nf
#@+node:ville.20100704010850.5589: *3* def tabula_show
def tabula_show(c):
    try:
       t = c.tabula
    except AttributeError:
        t = c.tabula = Tabula(c) 
    t.show()
    return t

#@+node:ville.20100703194946.5585: *3* @g.command('tabula')
@g.command('tabula')
def tabula_f(event):
    """ Show "tabula" - a MDI window with stickynotes that remember their status """
    c= event['c']
    t = tabula_show(c)
    p = c.p
    t.add_note(p)


#@+node:ville.20100704010850.5588: *3* @g.command('tabula-show')
@g.command('tabula-show')
def tabula_show_f(event):
    c= event['c']

    tabula_show(c)



#@+node:ville.20100704125228.5592: *3* @g.command('tabula-marked')
@g.command('tabula-marked')
def tabula_marked_f(event):
    """ Create tabula from all marked nodes """
    c= event['c']

    t=tabula_show(c)

    for p in c.all_unique_positions():
        if p.isMarked():
            t.add_note(p)

#@+node:ville.20101128205511.6114: *3* @g.command('tabula-subtree')
@g.command('tabula-subtree')
def tabula_subtree_f(event):
    """ Create tabula from all nodes in subtree """
    c= event['c']

    t=tabula_show(c)

    for p in c.p.self_and_subtree():
        t.add_note(p)

#@+node:ville.20100703194946.5584: *3* class Tabula(QMainWindow)
class Tabula(QMainWindow):

    #@+others
    #@+node:ekr.20101114061906.5445: *4* __init__
    def __init__(self, c):

        QMainWindow.__init__(self)

        mdi = self.mdi = QMdiArea(self)
        self.setCentralWidget(mdi)
        self.create_actions()
        self.menuBar().setVisible(False)

        self.notes = {}
        self.c = c

        def delayed_load():
            self.load_states()
        QTimer.singleShot(0, delayed_load)

        self.setWindowTitle("Tabula " + os.path.basename(self.c.mFileName))

        g.registerHandler("end1",self.on_quit)
    #@+node:ekr.20101114061906.5443: *4* add_note
    def add_note(self, p):

        gnx = p.gnx
        if gnx in self.notes:
            n = self.notes[gnx]
            n.show()
            return n

        n = mknote(self.c, p, parent = self.mdi)
        sw = self.mdi.addSubWindow(n)
        sw.setAttribute(Qt.WA_DeleteOnClose, False)
        self.notes[gnx] = n
        n.show()
        return n
    #@+node:ekr.20101114061906.5442: *4* closeEvent
    def closeEvent(self,event):

        self.save_states()
        g.trace(event)
        event.accept() # EKR: doesn't help: we don't get the event.

    #@+node:ekr.20101114061906.5444: *4* create_actions (has all toolbar commands!)

    def create_actions(self):

        self.tb = self.addToolBar("toolbar")
        self.tb.setObjectName("toolbar")
        #self.addToolBar(Qt.BottomToolBarArea, self.tb)
        def do_tile():
            self.mdi.setViewMode(QMdiArea.SubWindowView)
            self.mdi.tileSubWindows()
        def do_cascade():
            self.mdi.setViewMode(QMdiArea.SubWindowView)
            self.mdi.cascadeSubWindows()
        def do_un_tab():
            if self.mdi.viewMode() == QMdiArea.SubWindowView:
                self.mdi.setViewMode(QMdiArea.TabbedView)
            else:
                self.mdi.setViewMode(QMdiArea.SubWindowView)
        def do_close_all():
            for i in self.mdi.subWindowList():
                self.mdi.removeSubWindow(i)
            self.notes = {}


        def do_go():
            p, _ = self.get_current_pos()
            self.c.selectPosition(p)

        def do_new():
            n = create_subnode(self.c, "Tabula")
            n.h = time.asctime()
            self.c.redraw()
            self.add_note(n)

        def do_edit_h():
            p, w = self.get_current_pos()        

            new, r = QInputDialog.getText(None, "Edit headline", "", QLineEdit.Normal, p.h)
            if not r: 
                return
            new = g.u(new)
            p.h = new
            w.setWindowTitle(new)




        self.tb.addAction("Tile", do_tile)
        self.tb.addAction("Cascade", do_cascade)
        self.tb.addAction("(Un)Tab", do_un_tab)
        self.tb.addAction("Go", do_go)
        self.tb.addAction("New", do_new)
        self.tb.addAction("Headline", do_edit_h)

        self.tb.addSeparator()
        self.tb.addAction("Close All", do_close_all)

        # ca = QAction("Close All", self.tb)
        # ca.setMenuRole(QAction.QuitRole)
        # ca.connect(ca, SIGNAL("triggered()"), do_close_all)
        # self.tb.addAction(ca)
    #@+node:ekr.20101114061906.5440: *4* load_states
    def load_states(self):

        if not self.c.cacher.db:
            return
        try:
            stored = self.c.cacher.db['tabulanotes']
        except KeyError:
            return

        mwstate = stored.pop("mainwindow")
        self.restoreState(mwstate)

        # still think leo should maintain a dict like this.
        # EKR: :-)
        ncache = dict((p.gnx, p.copy()) for p in self.c.all_unique_positions())

        for gnx, geom in stored.items():
            try:
                po = ncache[gnx]
            except KeyError:
                g.trace("lost note", gnx)
                continue

            n = self.add_note(ncache[gnx])
            n.parent().restoreGeometry(geom)
    #@+node:ekr.20101114061906.5446: *4* on_quit
    def on_quit(self,tag, kw):

        g.trace(tag,kw,self)
        # saving when hidden nukes all

        if self.isVisible():
            self.save_states()

        # None of these work on Python 3.x.
        # self.destroy()

        # self.mdi.close()
        # self.close() # EKR
        # self.midi.delete() # EKR
    #@+node:ville.20101128212002.6111: *4* get_current_pos
    def get_current_pos(self):
        cur = self.mdi.activeSubWindow()
        active = [gnx for (gnx, n) in self.notes.items() if n.parent() == cur]
        if not active:
            g.trace("no node")
            return
        tgt = active[0]

        p = next(p for p in self.c.all_unique_positions() if p.gnx == tgt)
        return p, cur

    #@+node:ekr.20101114061906.5441: *4* save_states
    def save_states(self):

        # n.parent() because the wrapper QMdiSubWindow holds the geom relative to parent
        geoms = dict(
            (gnx, n.parent().saveGeometry())
                for (gnx, n) in self.notes.items() if n.isVisible())

        geoms['mainwindow'] = self.saveState()

        if self.c.cacher.db:
            self.c.cacher.db['tabulanotes'] = geoms
    #@-others
#@+node:ville.20100703194946.5587: ** def mknote
def mknote(c,p, parent=None):
    """ Launch editable 'sticky note' for the node """

    v = p.v
    def focusin():
        #print "focus in"
        if v is c.p.v:
            if v.b != nf.toPlainText():
                # only when needed to avoid scroll jumping
                nf.setPlainText(v.b)
            nf.setWindowTitle(v.h)
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


    def closeevent():
        pass
        # print "closeevent"


    nf = FocusingPlaintextEdit(focusin, focusout, closeevent, parent = parent)
    nf.setWindowIcon(QIcon(g.app.leoDir + "/Icons/leoapp32.png"))
    nf.dirty = False
    nf.resize(600, 300)
    nf.setWindowTitle(p.h)
    nf.setPlainText(p.b)
    p.setDirty()

    def textchanged_cb():
        nf.dirty = True

    nf.connect(nf,
        SIGNAL("textChanged()"),textchanged_cb)

    nf.show()

    g.app.stickynotes[p.gnx] = nf
    return nf
#@-others
#@-leo
