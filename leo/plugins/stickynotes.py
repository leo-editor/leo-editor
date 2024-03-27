#@+leo-ver=5-thin
#@+node:ekr.20100103093121.5329: * @file ../plugins/stickynotes.py
#@+<< docstring >>
#@+node:vivainio2.20091008133028.5821: ** << docstring >>
""" Adds simple "sticky notes" feature (popout editors) for Qt gui.

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

"""
#@-<< docstring >>
#@+<< imports >>
#@+node:vivainio2.20091008133028.5823: ** << imports >> (stickynotes.py)
import os
import time
from typing import Any
#
# Third-party imports.
try:
    from Crypto.Cipher import AES
    from Crypto.Hash import MD5, SHA
    import base64
    import textwrap
    __ENCKEY = [None]
    encOK = True
except ImportError:
    encOK = False
#
# Leo imports.
from leo.core import leoGlobals as g
from leo.core.leoQt import Qt, QtCore, QtGui, QtWidgets
from leo.core.leoQt import QAction, Weight

# Fail fast, right after all imports.
g.assertUi('qt')  # May raise g.UiTypeException, caught by the plugins manager.
#@-<< imports >>

# broad-exception-raised: Not valid in later pylints.

# Aliases...
# These can *not* be used as the base classes.
QInputDialog = QtWidgets.QInputDialog
QLineEdit = QtWidgets.QLineEdit
QMdiArea = QtWidgets.QMdiArea
QTextCharFormat = QtGui.QTextCharFormat
QTimer = QtCore.QTimer

# Keys are commanders. Values are inner dicts: keys are gnx's; values are widgets.
outer_dict: dict[Any, dict[str, Any]] = {}  # #2471
#@+others
#@+node:vivainio2.20091008140054.14555: ** decorate_window
def decorate_window(c, w):
    w.setStyleSheet(c.styleSheetManager.get_master_widget().styleSheet())
    # w.setWindowIcon(QIcon(g.app.leoDir + "/Icons/leoapp32.png"))
    g.app.gui.attachLeoIcon(w)
    w.resize(600, 300)
#@+node:vivainio2.20091008133028.5824: ** init
def init():
    """Return True if the plugin has loaded successfully."""
    ok = g.app.gui.guiName() == 'qt'
    if ok:
        g.plugin_signon(__name__)
        g.registerHandler('close-frame', onCloseFrame)
    return ok
#@+node:ekr.20220310040820.1: ** onCloseFrame
def onCloseFrame(tag, kwargs):
    """Close all stickynotes in c's outline."""
    global outer_dict
    c = kwargs.get('c')
    if not c:
        return
    d = outer_dict.get(c.hash(), {})
    for gnx in d:
        w = d.get(gnx)
        w.close()
    outer_dict[c.hash()] = {}
#@+node:ekr.20160403065412.1: ** commands
#@+node:vivainio2.20091008133028.5825: *3* g.command('stickynote')
@g.command('stickynote')
def stickynote_f(event):
    """ Launch editable 'sticky note' for c.p."""
    c = event['c']
    mknote(c, c.p)
#@+node:ville.20110304230157.6526: *3* g.command('stickynote-new')
@g.command('stickynote-new')
def stickynote_new_f(event):
    """Launch editable 'sticky note' for the node """
    c = event['c']
    p = find_or_create_stickynotes(c)
    p2 = p.insertAsLastChild()
    p2.h = time.asctime()
    mknote(c, p2)
    # Fix #249: Leo and Stickynote plugin do not request to save.
    c.setChanged()
    c.redraw(p2)
#@+node:ville.20091023181249.5266: *3* g.command('stickynoter')
@g.command('stickynoter')
def stickynoter_f(event):
    """
    Launch editable 'sticky note' for the node.
    The result is saved as rich text, that is, html...
    """
    global outer_dict
    c = event['c']
    p = c.p
    v = p.v
    # #2471: Just show the node if it already exists.
    d = outer_dict.get(c.hash(), {})
    nf: Any = d.get(p.gnx)  # Hard to annotate.
    if nf:
        nf.show()
        nf.raise_()
        return

    def stickynoter_focusin():
        if v is c.p.v:
            nf.setHtml(v.b)
            nf.setWindowTitle(p.h)
            nf.dirty = False

    def stickynoter_focusout():
        if nf.dirty:
            v.b = nf.toHtml()
            v.setDirty()
            nf.dirty = False
            p = c.p
            if p.v is v:
                c.selectPosition(c.p)
            # Fix #249: Leo and Stickynote plugin do not request to save
            c.setChanged()
            c.redraw()

    # not LessSimpleRichText
    nf = SimpleRichText(stickynoter_focusin, stickynoter_focusout)
    nf.dirty = False
    decorate_window(c, nf)
    nf.setWindowTitle(p.h)
    nf.setHtml(p.b)
    # Fix #249: Leo and Stickynote plugin do not request to save.
    # Do this only on focusout:
        # p.setDirty()
        # c.setChanged()
        # c.redraw()

    def textchanged_cb():
        nf.dirty = True

    nf.textChanged.connect(textchanged_cb)
    nf.show()
    d = outer_dict.get(c.hash(), {})
    d[p.gnx] = nf
    outer_dict[c.hash()] = d
#@+node:tbrown.20100120100336.7829: *3* g.command('stickynoteenc')
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
        c = event['c']
        p = c.p
        v = p.v

        def stickynoteenc_focusin():
            if v is c.p.v:
                decoded = sn_decode(v.b)
                if decoded is None:
                    return
                if decoded != nf.toPlainText():
                    # only when needed to avoid scroll jumping
                    nf.setPlainText(decoded)
                nf.setWindowTitle(p.h)
                nf.dirty = False

        def stickynoteenc_focusout():
            if not nf.dirty:
                return
            enc = sn_encode(str(nf.toPlainText()))
            if v.b != enc:
                v.b = enc
                v.setDirty()
                # Fix #249: Leo and Stickynote plugin do not request to save
                c.setChanged()
            nf.dirty = False
            p = c.p
            if p.v is v:
                c.selectPosition(c.p)
            c.redraw()

        if rekey:
            unsecret = sn_decode(v.b)
            if unsecret is None:
                return
            sn_getenckey()
            secret = sn_encode(unsecret)
            v.b = secret

        if v.b:
            decoded = sn_decode(v.b)
            if decoded is None:
                return
        else:
            decoded = v.b
        nf: Any = mknote(c, p,  # Hard to annotate.
            focusin=stickynoteenc_focusin,
            focusout=stickynoteenc_focusout)
        nf.setPlainText(decoded)
        if rekey:
            g.es("Key updated, data decoded with new key shown in window")
#@+node:tbrown.20100120100336.7830: *3* g.command('stickynoteenckey')
if encOK:

    def get_AES():
        if hasattr(AES, 'MODE_EAX'):
            return AES.new(__ENCKEY[0], AES.MODE_EAX)
        return AES.new(__ENCKEY[0])

    def sn_decode(s):
        try:
            s1 = base64.b64decode(s)
            return get_AES().decrypt(s1).decode('utf8').strip()
        except Exception:
            g.es("encryption failed")
            __ENCKEY[0] = None
            return None

    def sn_encode(s):
        s1 = s.encode('utf8')
        pad = b' ' * (16 - len(s1) % 16)
        txta = get_AES().encrypt(s1 + pad)
        txt_b = base64.b64encode(txta)
        txt = str(txt_b, 'utf-8')
        wrapped = textwrap.wrap(txt, break_long_words=True)
        return '\n'.join(wrapped)

    @g.command('stickynoteenckey')
    def sn_getenckey(dummy=None):
        txt, ok = QInputDialog.getText(None,
            'Enter key',
            'Enter key.\nData lost if key is lost.\nSee docs. for key upgrade notes.',
        )
        if not ok:
            return
        txt = g.toUnicode(txt)
        if txt.startswith('v0:'):
            txt = txt[3:]
        # arbitrary kludge to convert string to 256 bits - don't change
        sha = SHA.new()
        md5 = MD5.new()
        sha.update(txt.encode('utf-8'))
        md5.update(txt.encode('utf-8'))
        __ENCKEY[0] = sha.digest()[:16] + md5.digest()[:16]
        if len(__ENCKEY[0]) != 32:
            raise KeyError("sn_getenckey failed to build key")
#@+node:tbrown.20141214173054.3: ** class TextEditSearch
class TextEditSearch(QtWidgets.QWidget):  # type:ignore
    """A QTextEdit with a search box

    Used to make decoded encoded body text searchable, so when you've decoded
    your password list you dont't have to scan through five pages of text to
    find the one you need.
    """

    @staticmethod
    def _call_old_first(oldfunc, newfunc):
        """Focus in/out methods need to call base class method"""
        def f(event, oldfunc=oldfunc, newfunc=newfunc):
            oldfunc(event)
            newfunc()
        return f

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.textedit = QtWidgets.QTextEdit(*args, **kwargs)
        # need to call focusin/out set on parent by FocusingPlaintextEdit / mknote
        self.textedit.focusInEvent = self._call_old_first(  # type:ignore
            self.textedit.focusInEvent, self.focusin)
        self.textedit.focusOutEvent = self._call_old_first(  # type:ignore
            self.textedit.focusOutEvent, self.focusout)
        self.searchbox = QLineEdit()
        self.searchbox.focusInEvent = self._call_old_first(  # type:ignore
            self.searchbox.focusInEvent, self.focusin)
        self.searchbox.focusOutEvent = self._call_old_first(  # type:ignore
            self.searchbox.focusOutEvent, self.focusout)

        # invoke find when return pressed
        self.searchbox.returnPressed.connect(self.search)

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.textedit)
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.setContentsMargins(0, 0, 0, 0)
        hlayout.addWidget(QtWidgets.QLabel("Find:"))
        hlayout.addWidget(self.searchbox)
        layout.addLayout(hlayout)

    def __getattr__(self, name):
        """Delegate things QWidget doesn't have to QTextEdit, takes care
        of attempts to access the text."""
        return getattr(self.textedit, name)

    def search(self):
        """Search text"""
        text = self.searchbox.text()
        doc = self.textedit.document()
        result = doc.find(text, self.textedit.textCursor())
        if not result.isNull():
            self.textedit.setTextCursor(result)
#@+node:ville.20091008210853.7616: ** class FocusingPlainTextEdit
class FocusingPlaintextEdit(TextEditSearch):

    def __init__(self, focusin, focusout, closed=None, parent=None):
        self.focusin = focusin
        self.focusout = focusout
        self.closed = closed
        super().__init__(parent)

    def focusOutEvent(self, event):
        self.focusout()

    def focusInEvent(self, event):
        self.focusin()

    def closeEvent(self, event):
        event.accept()
        if self.closed:
            self.closed()
        self.focusout()
#@+node:ville.20091023181249.5264: ** class SimpleRichText
class SimpleRichText(QtWidgets.QTextEdit):  # type:ignore

    # pylint: disable=method-hidden

    def __init__(self, focusin, focusout):
        super().__init__()
        self.focusin = focusin
        self.focusout = focusout
        self.createActions()

    def focusOutEvent(self, event):
        self.focusout()

    def focusInEvent(self, event):
        self.focusin()


    def closeEvent(self, event):
        event.accept()

    def createActions(self):
        self.boldAct = QAction(self.tr("&Bold"), self)
        self.boldAct.setCheckable(True)
        self.boldAct.setShortcut(self.tr("Ctrl+B"))
        self.boldAct.setStatusTip(self.tr("Make the text bold"))
        self.boldAct.triggered.connect(self.setBold)
        self.addAction(self.boldAct)

        boldFont = self.boldAct.font()
        boldFont.setBold(True)
        self.boldAct.setFont(boldFont)

        self.italicAct = QAction(self.tr("&Italic"), self)
        self.italicAct.setCheckable(True)
        self.italicAct.setShortcut(self.tr("Ctrl+I"))
        self.italicAct.setStatusTip(self.tr("Make the text italic"))
        self.italicAct.triggered.connect(self.setItalic)
        self.addAction(self.italicAct)

    def setBold(self):
        format = QTextCharFormat()
        if self.boldAct.isChecked():
            weight = Weight.Bold
        else:
            weight = Weight.Normal
        format.setFontWeight(weight)
        self.setFormat(format)

    def setItalic(self):
        format = QTextCharFormat()
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
#@+node:ekr.20160403065519.1: ** Utils
#@+node:ville.20100707205336.5610: *3* create_subnode
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
#@+node:ekr.20160403065539.1: *3* find_or_create_stickynotes
def find_or_create_stickynotes(c):

    # Huh? This makes no sense, and can cause a crash.
        # wb = get_workbook()
        # assert wb,'no wb'
    aList = c.find_h('stickynotes')
    if aList:
        p = aList[0]
    else:
        p = c.rootPosition().insertAfter()
        c.redraw(p)
        p.h = "stickynotes"
    # return p, wb
    return p
#@+node:ville.20110304230157.6527: *3* get_workbook (no longer used)
def get_workbook():
    for co in g.app.commanders():
        if co.mFileName.endswith('workbook.leo'):
            return co
    return None
#@+node:ville.20100703194946.5587: *3* mknote
def mknote(c, p, parent=None, focusin=None, focusout=None):
    """ Launch editable 'sticky note' for the node """
    global outer_dict
    v = p.v
    if focusin is None:
        def mknote_focusin():
            if v is c.p.v:
                if v.b.encode('utf-8') != nf.toPlainText():
                    # only when needed to avoid scroll jumping
                    nf.setPlainText(v.b)
                nf.setWindowTitle(v.h)
                nf.dirty = False
    else:
        mknote_focusin = focusin

    if focusout is None:
        def mknote_focusout():
            if nf.dirty:
                if v.b.encode('utf-8') != nf.toPlainText():
                    v.b = nf.toPlainText()
                    v.setDirty()
                    # Fix #249: Leo and Stickynote plugin do not request to save
                    c.setChanged()
                nf.dirty = False
                p = c.p
                if p.v is v:
                    c.selectPosition(c.p)
                c.redraw()
    else:
        mknote_focusout = focusout

    def closeevent():
        pass

    # #2471: Create a new editor only if it doesn't already exist.
    d = outer_dict.get(c.hash(), {})
    nf = d.get(p.gnx)
    if nf:
        nf.show()
        nf.raise_()
        return nf
    nf = FocusingPlaintextEdit(
        focusin=mknote_focusin,
        focusout=mknote_focusout,
        closed=closeevent,
        parent=parent)
    decorate_window(c, nf)
    nf.dirty = False
    nf.resize(600, 300)
    nf.setWindowTitle(p.h)
    nf.setPlainText(p.b)
    # Fix #249: Leo and Stickynote plugin do not request to save
    # Don't set the node dirty unless it has been changed.
    # p.setDirty()

    def textchanged_cb():
        nf.dirty = True

    nf.textChanged.connect(textchanged_cb)
    nf.show()
    d = outer_dict.get(c.hash(), {})
    d[p.gnx] = nf
    outer_dict[c.hash()] = d
    return nf
#@+node:ville.20100703234124.9976: ** Tabula
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
    c = event['c']
    t = tabula_show(c)
    p = c.p
    t.add_note(p)


#@+node:ville.20100704010850.5588: *3* @g.command('tabula-show')
@g.command('tabula-show')
def tabula_show_f(event):
    """Show the`Tabula` sticky note dock window, without adding the current node."""
    c = event['c']

    tabula_show(c)
#@+node:ville.20100704125228.5592: *3* @g.command('tabula-marked')
@g.command('tabula-marked')
def tabula_marked_f(event):
    """ Create tabula from all marked nodes """
    c = event['c']

    t = tabula_show(c)

    for p in c.all_unique_positions():
        if p.isMarked():
            t.add_note(p)

#@+node:ville.20101128205511.6114: *3* @g.command('tabula-subtree')
@g.command('tabula-subtree')
def tabula_subtree_f(event):
    """ Create tabula from all nodes in subtree """
    c = event['c']

    t = tabula_show(c)

    for p in c.p.self_and_subtree():
        t.add_note(p)

#@+node:ville.20100703194946.5584: *3* class Tabula(QMainWindow)
class Tabula(QtWidgets.QMainWindow):  # type:ignore

    #@+others
    #@+node:ekr.20101114061906.5445: *4* __init__
    def __init__(self, c):

        super().__init__()
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
        g.registerHandler("end1", self.on_quit)
    #@+node:ekr.20101114061906.5443: *4* add_note
    def add_note(self, p):

        gnx = p.gnx
        if gnx in self.notes:
            n = self.notes[gnx]
            n.show()
            return n
        n = mknote(self.c, p, parent=self.mdi)
        sw = self.mdi.addSubWindow(n)
        try:
            sw.setAttribute(Qt.WA_DeleteOnClose, False)
        except AttributeError:
            pass
        self.notes[gnx] = n
        n.show()
        return n
    #@+node:ekr.20101114061906.5442: *4* closeEvent (Tabula)
    def closeEvent(self, event):

        self.save_states()
        event.accept()  # EKR: doesn't help: we don't get the event.
    #@+node:ekr.20101114061906.5444: *4* create_actions (has all toolbar commands!)
    def create_actions(self):

        self.tb = self.addToolBar("toolbar")
        self.tb.setObjectName("toolbar")

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
            new, r = QInputDialog.getText(None,
                "Edit headline", "",
                QLineEdit.Normal, p.h)
            if not r:
                return
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
        # ca.triggered.connect(do_close_all)
        # self.tb.addAction(ca)
    #@+node:ekr.20101114061906.5440: *4* load_states
    def load_states(self):

        if not self.c.db:
            return
        try:
            stored = self.c.db['tabulanotes']
        except KeyError:
            return

        mwstate = stored.pop("mainwindow")
        self.restoreState(mwstate)

        # still think leo should maintain a dict like this.
        # EKR: :-)
        ncache = dict((p.gnx, p.copy()) for p in self.c.all_unique_positions())

        for gnx, geom in stored.items():
            try:
                ncache[gnx]
            except KeyError:
                g.trace("lost note", gnx)
                continue

            n = self.add_note(ncache[gnx])
            n.parent().restoreGeometry(geom)
    #@+node:ekr.20101114061906.5446: *4* on_quit
    def on_quit(self, tag, kw):

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
            return None, None
        tgt = active[0]

        p = next(p for p in self.c.all_unique_positions() if p.gnx == tgt)
        return p, cur

    #@+node:ekr.20101114061906.5441: *4* save_states
    def save_states(self):

        self.update_notes()

        # n.parent() because the wrapper QMdiSubWindow holds the geom relative to parent
        geoms = dict(
            (gnx, n.parent().saveGeometry())
                for (gnx, n) in self.notes.items() if n.isVisible())

        geoms['mainwindow'] = self.saveState()

        if self.c.db:
            self.c.db['tabulanotes'] = geoms
    #@+node:ekr.20180822134952.1: *4* update_nodes (new)
    def update_notes(self):

        # #940: update self.notes. Ensure note n still exists.
        visible = []
        for (gnx, n) in self.notes.items():
            try:
                if n.isVisible():
                    visible.append(gnx)
            except RuntimeError:
                pass
        self.notes = dict(
            (gnx, n) for (gnx, n) in self.notes.items()
                if gnx in visible
        )
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
