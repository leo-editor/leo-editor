#@+leo-ver=5-thin
#@+node:ekr.20100103093121.5339: * @file ../plugins/stickynotes_plus.py
#@+<< docstring >>
#@+node:ekr.20100103100944.5389: ** << docstring >>
""" Adds simple "sticky notes" feature (popout editors) for Qt gui.

alt-x stickynote to pop out current node as a note.

"""
#@-<< docstring >>
# Disable Qt warnings.
#@+<< imports >>
#@+node:ekr.20100103100944.5391: ** << imports >> (stickynotes_plus.py)
import webbrowser
from leo.core import leoGlobals as g
from leo.core.leoQt import Qt, QtCore, QtGui, QtWidgets
from leo.core.leoQt import QAction, KeyboardModifier, Weight
# Third-party tools.
try:
    import markdown
except ImportError:
    print('stickynotes_plus.py: can not import markdown')
    markdown = None
except SyntaxError:
    print('stickynotes_plus.py: syntax error in markdown')
    markdown = None
#
# Fail fast, right after all imports.
g.assertUi('qt')  # May raise g.UiTypeException, caught by the plugins manager.
# Abbreviations...
QMenu = QtWidgets.QMenu
QPlainTextEdit = QtWidgets.QPlainTextEdit
QTextEdit = QtWidgets.QTextEdit
# Other gui elements.
QFont = QtGui.QFont
QIcon = QtGui.QIcon
QSize = QtCore.QSize
QTextBlockFormat = QtGui.QTextBlockFormat
QTextCharFormat = QtGui.QTextCharFormat
QTextCursor = QtGui.QTextCursor
QTextListFormat = QtGui.QTextListFormat
QTimer = QtCore.QTimer
QVariant = QtCore.QVariant
#@-<< imports >>
#@+others
#@+node:ekr.20100103100944.5392: ** styling
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
    # w.setWindowIcon(QIcon(g.app.leoDir + "/Icons/leoapp32.png"))
    g.app.gui.attachLeoIcon(w)
    w.resize(600, 300)

#@+node:ekr.20100103100944.5393: ** init
def init():
    """Return True if the plugin has loaded successfully."""
    ok = markdown is not None and g.app.gui.guiName() == "qt"
    if ok:
        g.plugin_signon(__name__)
    g.app.stickynotes = {}
    return ok
#@+node:ekr.20100103100944.5394: ** class FocusingPlainTextEdit
class FocusingPlaintextEdit(QPlainTextEdit):

    def __init__(self, focusin, focusout):
        super().__init__()
        self.focusin = focusin
        self.focusout = focusout

    def focusOutEvent(self, event):
        self.focusout()

    def focusInEvent(self, event):
        self.focusin()

    def closeEvent(self, event):
        event.accept()
        self.focusout()


#@+node:ekr.20100103100944.5395: ** class SimpleRichText
class SimpleRichText(QTextEdit):
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
        # self.connect(self.boldAct, SIGNAL("triggered()"), self.setBold)
        self.triggered.connect(self.setBold)
        self.addAction(self.boldAct)

        boldFont = self.boldAct.font()
        boldFont.setBold(True)
        self.boldAct.setFont(boldFont)

        self.italicAct = QAction(self.tr("&Italic"), self)
        self.italicAct.setCheckable(True)
        self.italicAct.setShortcut(self.tr("Ctrl+I"))
        self.italicAct.setStatusTip(self.tr("Make the text italic"))
        self.triggered.connect(self.setItalic)
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



#@+node:ekr.20100103100944.5396: ** class notetextedit
class notetextedit(QTextEdit):

    (Bold, Italic, Pre, List, Remove,
     Plain, Code, H1, H2, H3, Anchor, Save) = range(12)

    #@+others
    #@+node:ekr.20100103100944.5397: *3* __init__
    def __init__(self, get_markdown, save, parent=None):
        super().__init__(parent)
        self.save = save
        self.setLineWrapMode(QTextEdit.WidgetWidth)
        self.setTabChangesFocus(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setMinimumWidth(300)
        self.setMouseTracking(True)
        font = QFont()
        font.setPointSize(10)
        font.setFamily("helvetica")
        document = self.document()
        document.setDefaultFont(font)
        self.font = font
        document.setDefaultStyleSheet(
            "pre{margin-top:0px; margin-bottom:0px} li{margin-top:0px; margin-bottom:0px}")
        QTimer.singleShot(0, get_markdown)
    #@+node:ekr.20100103100944.5398: *3* focusOutEvent
    def focusOutEvent__(self, event):
        self.focusout()

    #@+node:ekr.20100103100944.5399: *3* focusInEvent
    def focusInEvent__(self, event):
        self.focusin()

    #@+node:ekr.20100103100944.5400: *3* toggleItalic
    def toggleItalic(self):
        if self.which_header():
            return
        italic = self.fontItalic()
        cursor = self.textCursor()
        char_format = QTextCharFormat()
        char_format.setFont(self.font)
        char_format.setFontItalic(not italic)
        cursor.setCharFormat(char_format)

    #@+node:ekr.20100103100944.5401: *3* toggleUnderline
    def toggleUnderline(self):
        # not in use, markdown doesn't support
        self.setFontUnderline(not self.fontUnderline())

    #@+node:ekr.20100103100944.5402: *3* make_plain_text
    def make_plain_text(self):
        cursor = self.textCursor()

        char_format = QTextCharFormat()
        char_format.setFont(self.font)

        cursor.setCharFormat(char_format)

        block_format = QTextBlockFormat()
        block_format.setNonBreakableLines(False)
        cursor.setBlockFormat(block_format)

    #@+node:ekr.20100103100944.5403: *3* make_pre_block
    def make_pre_block(self):
        cursor = self.textCursor()
        block_format = cursor.blockFormat()
        if block_format.nonBreakableLines():
            block_format.setNonBreakableLines(False)
            cursor.setBlockFormat(block_format)
            char_format = QTextCharFormat()
            char_format.setFontFixedPitch(False)
            cursor.setCharFormat(char_format)
        else:
            block_format.setNonBreakableLines(True)
            cursor.setBlockFormat(block_format)

            char_format = QTextCharFormat()
            char_format.setFontFixedPitch(True)
            cursor.setCharFormat(char_format)

    #@+node:ekr.20100103100944.5404: *3* toggleBold
    def toggleBold(self):
        if self.which_header():
            return
        bold = self.fontWeight() > Weight.Normal
        cursor = self.textCursor()
        char_format = QTextCharFormat()
        char_format.setFont(self.font)
        char_format.setFontWeight(Weight.Normal if bold else Weight.Bold)
        cursor.setCharFormat(char_format)

    #@+node:ekr.20100103100944.5405: *3* toggleCode
    def toggleCode(self):
        if self.which_header():
            return
        cursor = self.textCursor()
        char_format = cursor.charFormat()

        if char_format.fontFixedPitch():
            # didn't do exhaustive testing but appear to need both statements
            char_format.setFontFixedPitch(False)
            char_format.setFontFamily("helvetica")
        else:
            char_format.setFontFixedPitch(True)
            char_format.setFontFamily("courier")

        char_format.setFontItalic(False)
        char_format.setFontWeight(Weight.Normal)

        cursor.setCharFormat(char_format)

    #@+node:ekr.20100103100944.5406: *3* create_anchor
    def create_anchor(self):
        cursor = self.textCursor()
        if not cursor.hasSelection():
            return
        text = cursor.selectedText()
        if text.startswith('http://'):
            text = '<a href="{0}">{1}</a> '.format(text, text[7:])
        else:
            text = '<a href="http://{0}">{0}</a> '.format(text)
        #
        # The below works but doesn't pick up highlighting of an anchor
        # would have to do the underlining and blue color
            # format = QTextCharFormat()
            # format.setAnchor(True)
            # format.setAnchorHref(text)
            # cursor.setCharFormat(format)
            # self.setTextCursor(cursor)
        #
        # This also works and generates highlighting
        cursor.deleteChar()
        cursor.insertHtml(text)  # also self.insertHtml should work

    #@+node:ekr.20100103100944.5407: *3* create_list
    def create_list(self):
        cursor = self.textCursor()
        if not cursor.hasSelection():
            return
        cursor.createList(QTextListFormat.ListDecimal)

    #@+node:ekr.20100103100944.5408: *3* make_heading
    def make_heading(self, heading):
        # not finished
        cursor = self.textCursor()
        cursor.select(QTextCursor.BlockUnderCursor)  #QTextCursor.LineUnderCursor

        char_format = QTextCharFormat()
        font = QFont()
        font.setFamily("helvetica")
        font.setPointSize({1: 20, 2: 15, 3: 12}[heading])
        font.setBold(True)
        char_format.setFont(font)

        cursor.setCharFormat(char_format)

    #@+node:ekr.20100103100944.5409: *3* sizeHint
    def sizeHint(self):  # this makes the text box taller when launched than if I don't have it
        return QSize(self.document().idealWidth() + 5, self.maximumHeight())

    #@+node:ekr.20100103100944.5410: *3* contextMenuEvent
    def contextMenuEvent(self, event):  # this catches the context menu right click
        self.textEffectMenu()

    #@+node:ekr.20100103100944.5411: *3* keyPressEvent__ (stickynotes_plus.py)
    def keyPressEvent__(self, event):
        # needed because text edit is not going to recognize short cuts
        # because will do something with control key
        # not needed if have global shortcuts
        if event.modifiers() & KeyboardModifier.ControlModifier:
            handled = False
            if event.key() == Qt.Key_A:
                self.create_anchor()
                handled = True
            elif event.key() == Qt.Key_B:
                self.toggleBold()
                handled = True
            elif event.key() == Qt.Key_I:
                self.toggleItalic()
                handled = True
            elif event.key() == Qt.Key_M:
                self.textEffectMenu()
                handled = True
            elif event.key() == Qt.Key_P:
                self.make_plain_text()
                handled = True
            elif event.key() == Qt.Key_Z:
                self.make_pre_block()
                handled = True
            elif event.key() == Qt.Key_U:
                self.toggleUnderline()
                handled = True
            if handled:
                event.accept()
                return

        QTextEdit.keyPressEvent(self, event)

    #@+node:ekr.20100103100944.5412: *3* fontFixedPitch
    def fontFixedPitch(self):
        cursor = self.textCursor()
        format = cursor.charFormat()
        return format.fontFixedPitch()

    #@+node:ekr.20100103100944.5413: *3* which_header
    def which_header(self):
        cursor = self.textCursor()
        char_format = cursor.charFormat()
        ps = char_format.font().pointSize()
        return {20: 'H1', 15: 'H2', 12: 'H3'}.get(ps)


    #@+node:ekr.20100103100944.5414: *3* textEffectMenu
    def textEffectMenu(self):
        # format = self.currentCharFormat()
        # cursor = self.textCursor()
        # blockformat = cursor.blockFormat()
        menu = QMenu("Text Effect")
        for text, shortcut, data, checked in (
                ("&Bold", "Ctrl+B", notetextedit.Bold,
                 self.fontWeight() > Weight.Normal),
                ("&Italic", "Ctrl+I", notetextedit.Italic,
                 self.fontItalic()),
                ("&Monospaced", None, notetextedit.Code,
                 self.fontFixedPitch())
                ):

            action = menu.addAction(text, self.setTextEffect)
            action.setData(QVariant(data))
            action.setCheckable(True)
            action.setChecked(checked)

        menu.addSeparator()

        action = menu.addAction("Anchor", self.setTextEffect)
        action.setData(notetextedit.Anchor)

        action = menu.addAction("Code Block", self.setTextEffect)
        action.setData(notetextedit.Pre)

        action = menu.addAction("Numbered List", self.setTextEffect)
        action.setData(notetextedit.List)

        header_menu = QMenu("Header")
        action = header_menu.addAction('H1', self.setTextEffect)
        action.setData(notetextedit.H1)
        action.setCheckable(True)
        action.setChecked(self.which_header() == 'H1')

        action = header_menu.addAction('H2', self.setTextEffect)
        action.setData(notetextedit.H2)
        action.setCheckable(True)
        action.setChecked(self.which_header() == 'H2')

        action = header_menu.addAction('H3', self.setTextEffect)
        action.setData(notetextedit.H3)
        action.setCheckable(True)
        action.setChecked(self.which_header() == 'H3')

        action = menu.addAction("Remove All Formatting", self.setTextEffect)
        action.setData(notetextedit.Remove)

        menu.addMenu(header_menu)

        menu.addSeparator()

        action = menu.addAction("Save", self.setTextEffect)
        action.setData(notetextedit.Save)

        self.ensureCursorVisible()

        global_point = self.viewport().mapToGlobal(self.cursorRect().center())
        menu.exec(global_point)
    #@+node:ekr.20100103100944.5415: *3* setTextEffect
    def setTextEffect(self):
        action = self.sender()
        if action is not None and isinstance(action, QAction):
            what = action.data().toInt()[0]
            if what == notetextedit.Bold:
                self.toggleBold()

            elif what == notetextedit.Italic:
                self.toggleItalic()

            elif what == notetextedit.Code:
                self.toggleCode()

            elif what == notetextedit.Anchor:
                self.create_anchor()

            elif what == notetextedit.Pre:
                self.make_pre_block()

            elif what == notetextedit.Remove:
                self.make_plain_text()

            elif what == notetextedit.List:
                self.create_list()

            elif what == notetextedit.H1:
                self.make_heading(1)

            elif what == notetextedit.H2:
                self.make_heading(2)

            elif what == notetextedit.H3:
                self.make_heading(3)

            elif what == notetextedit.Save:
                self.save()

    #@+node:ekr.20100103100944.5416: *3* mouseMoveEvent (stickynotes_plus.py)
    def mouseMoveEvent(self, event):

        pos = event.pos()
        anch = self.anchorAt(pos)
        self.viewport().setCursor(Qt.PointingHandCursor if anch else Qt.IBeamCursor)
        QTextEdit.mouseMoveEvent(self, event)  #? recursion

    #@+node:ekr.20100103100944.5417: *3* mouseReleaseEvent
    def mouseReleaseEvent(self, event):

        pos = event.pos()
        url = self.anchorAt(pos)
        if url:
            if not url.startswith('http://'):  #linux seems to need this
                url = 'http://{0}'.format(url)
            webbrowser.open(url, new=2, autoraise=True)
        else:
            QTextEdit.mouseReleaseEvent(self, event)
    #@+node:ekr.20100103100944.5418: *3* insertFromMimeData
    def insertFromMimeData(self, source):
        # not sure really necessary since it actually appears to paste URLs correctly
        # I am stripping the http
        print("Paste")
        text = source.text()
        if (
            len(text.split()) == 1
            and (
                text.startswith('http://')
                or 'www' in text
                or '.com' in text
                or '.html' in text
            )
        ):
            if text.startswith('http://'):
                text = '<a href="{0}">{1}</a> '.format(text, text[7:])
            else:
                text = '<a href="http://{0}">{0}</a> '.format(text)
            self.insertHtml(text)
        else:
            QTextEdit.insertFromMimeData(self, source)

    #@+node:ekr.20100103100944.5419: *3* toMarkdown (stickynotes)
    def toMarkdown(self):
        references = ''
        i = 1
        doc = ''
        block = self.document().begin()  # block is like a para; text fragment is sequence of same char format
        while block.isValid():
            if block.blockFormat().nonBreakableLines():
                doc += '    ' + block.text() + '\n'
            else:
                if block.textList():
                    doc += '  ' + block.textList().itemText(block) + ' '
                para = ''
                iterator = block.begin()
                while iterator != block.end():
                    fragment = iterator.fragment()
                    if fragment.isValid():
                        char_format = fragment.charFormat()
                        text = Qt.escape(fragment.text())  # turns chars like < into entities &lt;
                        font_size = char_format.font().pointSize()
                        # a fragment can only be an anchor, italics or bold
                        if char_format.isAnchor():
                            ref = text if text.startswith('http://') else 'http://{0}'.format(text)
                            # too lazy right now to check if URL has already been referenced but should
                            references += "  [{0}]: {1}\n".format(i, ref)
                            text = "[{0}][{1}]".format(text, i)
                            i += 1
                        elif font_size > 10:
                            if font_size > 15:
                                text = '#{0}'.format(text)
                            elif font_size > 12:
                                text = '##{0}'.format(text)
                            else:
                                text = '###{0}'.format(text)
                        elif char_format.fontFixedPitch():
                            text = "`%1`".arg(text)
                        elif char_format.fontItalic():
                            text = "*%1*".arg(text)
                        elif char_format.fontWeight() > Weight.Normal:
                            text = "**%1**".arg(text)
                        para += text
                    iterator += 1
                doc += para + '\n\n'
            block = block.next()
        return doc + references

    #@-others
#@+node:ekr.20100103100944.5420: ** g.command('stickynote')
@g.command('stickynote')
def stickynote_f(event):
    """ Launch editable 'sticky note' for the node """

    c = event['c']
    p = c.p
    v = p.v

    def focusin():
        if v is c.p.v:
            nf.setPlainText(v.b)
            nf.setWindowTitle(p.h)
            nf.dirty = False

    def focusout():
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

    # nf.connect(nf, SIGNAL("textChanged()"),textchanged_cb)
    nf.textChanged.connect(textchanged_cb)
    nf.show()
    g.app.stickynotes[p.gnx] = nf
#@+node:ekr.20100103100944.5421: ** g.command('stickynoter')
@g.command('stickynoter')
def stickynoter_f(event):
    """ Launch editable 'sticky note' for the node """

    c = event['c']
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

    nf = SimpleRichText(focusin, focusout)
    nf.dirty = False
    decorate_window(nf)
    nf.setWindowTitle(p.h)
    nf.setHtml(p.b)
    p.setDirty()

    def textchanged_cb():
        nf.dirty = True

    # nf.connect(nf,SIGNAL("textChanged()"),textchanged_cb)
    nf.textChanged.connect(textchanged_cb)
    nf.show()
    g.app.stickynotes[p.gnx] = nf
#@+node:ekr.20100103100944.5422: ** g.command('stickynoteplus')
@g.command('stickynoteplus')
def stickynoteplus_f(event):
    """ Launch editable 'sticky note' for the node """
    c = event['c']
    p = c.p
    v = p.v
    def get_markdown():  #focusin():
        print("focus in")
        if v is c.p.v:
            nf.setHtml(markdown.markdown(v.b))
            nf.setWindowTitle(p.h)
            nf.dirty = False


    def save():  #focusout():
        print("focus out")
        if not nf.dirty:
            return
        v.b = nf.toMarkdown()
        v.setDirty()
        nf.dirty = False
        p = c.p
        if p.v is v:
            c.selectPosition(c.p)


    nf = notetextedit(get_markdown, save)
    nf.dirty = False
    decorate_window(nf)
    nf.setWindowTitle(p.h)
    nf.setHtml(p.b)
    p.setDirty()

    def textchanged_cb():
        nf.dirty = True

    # nf.connect(nf, SIGNAL("textChanged()"),textchanged_cb)
    nf.textChanged.connect(textchanged_cb)
    nf.show()
    g.app.stickynotes[p.gnx] = nf
#@-others
#@@language python
#@@tabwidth -4


#@-leo
