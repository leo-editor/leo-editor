#@+leo-ver=5-thin
#@+node:tom.20210527153256.1: * @file ../plugins/freewin.py
#@@tabwidth -4
#@@language python
"""A plugin with a basic editor pane that tracks an outline node.

   Version 1.0b4
"""

#@+others
#@+node:tom.20210527153415.1: ** Imports
try:
    # pylint: disable=import-error
    # this can fix an issue with Qt Web views in Ubuntu
    from OpenGL import GL
    assert GL  # To keep pyflakes happy.
except Exception:
    # but not need to stop if it doesn't work
    pass

from leo.core import leoGlobals as g

qt_imports_ok = False
try:
    from leo.core.leoQt import Qt, isQt5, isQt6, QtCore, QtWidgets
    qt_imports_ok = True
except ImportError as e:
    g.trace(e)

if not qt_imports_ok:
    g.trace('Qt imports failed')
    raise Exception('Qt Imports failed')

#@+<<import docutils>>
#@+node:tom.20210529002833.1: *3* <<import docutils>>
try:
    import docutils
    import docutils.core
except ImportError:
    docutils = None
if docutils:
    try:
        from docutils.core import publish_string
        from docutils.utils import SystemMessage
        got_docutils = True
    except ImportError:
        got_docutils = False
        g.es_exception()
    except SyntaxError:
        got_docutils = False
        g.es_exception()
else:
    got_docutils = False
    print('ZEditorWin: *** no docutils')

#@-<<import docutils>>
#@+<<set Qt Objects>>
#@+node:tom.20210601000633.1: *3* <<set Qt Objects>>
QWidget = QtWidgets.QWidget
QTextEdit = QtWidgets.QTextEdit
QVBoxLayout = QtWidgets.QVBoxLayout
QPushButton = QtWidgets.QPushButton
QStackedWidget = QtWidgets.QStackedWidget
QRect = QtCore.QRect

QWebView = None
if isQt5:
    try:
        from leo.core.leoQt import QtWebKitWidgets
        QWebView = QtWebKitWidgets.QWebView
    except ImportError:
        g.trace("Can't import QtWebKitWidgets")
    except Exception as e:
        g.trace(e)
else:
    try:
        QWebView = QtWidgets.QTextBrowser
    except Exception as e:
        g.trace(e)
        # The top-level init function gives the error.
#@-<<set Qt Objects>>
#@+node:tom.20210527153422.1: ** Declarations
# pylint: disable=invalid-name
# Dimensions and placing of editor windows
W = 570
H = 350
X = 1200
Y = 250

BACK_COLOR = 'aliceblue'
BROWSER = 1
EDITOR = 0
EDITOR_FONT_SIZE = '11pt'
ENCODING = 'utf-8'

FONT_FAMILY = 'Consolas, Droid Sans Mono, DejaVu Sans Mono'
RST_NO_WARNINGS = 5

STYLESHEET = f'''QTextEdit {{
    background: {BACK_COLOR};
    font-family: {FONT_FAMILY};
    font-size: {EDITOR_FONT_SIZE};
    }}'''

ENCODING='utf-8'
instances = {}
#@+node:tom.20210527153848.1: ** z-commands
@g.command('z-open-win')
def open_z_window(event):
    """Open or show editing window for the selected node."""
    if g.app.gui.guiName() != 'qt':
        return
    c = event.get('c')
    if not c:
        return
    id_ = c.p.gnx[:]

    zwin = instances.get(id_)
    if not zwin:
        zwin = instances[id_] = ZEditorWin(c)

    zwin.show()
    zwin.activateWindow()
#@+node:tom.20210527153906.1: ** class ZEditorWin
class ZEditorWin(QtWidgets.QMainWindow):
    """An basic editing window that echos the contents of an outline node."""
    #@+others
    #@+node:tom.20210527185804.1: *3* ctor
    def __init__(self, c, title='Z-editor'):
        super().__init__()
        QWidget.__init__(self) # per http://enki-editor.org/2014/08/23/Pyqt_mem_mgmt.html
        self.c = c
        self.p = c.p
        w = self.c.frame.body.wrapper
        self.host_editor = w.widget
        self.switching = False

        self.editor = QTextEdit()
        self.browser = QWebView()

        #@+<<set up editor>>
        #@+node:tom.20210602172856.1: *4* <<set up editor>>
        self.doc = self.editor.document()
        self.editor.setStyleSheet(STYLESHEET)
        #@-<<set up editor>>
        #@+<<set up render button>>
        #@+node:tom.20210602173354.1: *4* <<set up render button>>
        self.render_button  = QPushButton("Rendered <--> Plain")
        self.render_button.clicked.connect(self.switch_and_render)
        #@-<<set up render button>>

        #@+<<build central widget>>
        #@+node:tom.20210528235126.1: *4* <<build central widget>>
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.insertWidget(EDITOR, self.editor)
        self.stacked_widget.insertWidget(BROWSER, self.browser)

        layout = QVBoxLayout()
        layout.addWidget(self.render_button)
        layout.addWidget(self.stacked_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        #@-<<build central widget>>
        #@+<<set geometry>>
        #@+node:tom.20210528235451.1: *4* <<set geometry>>
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        self.setGeometry(QtCore.QRect(X, Y, W, H))
        #@-<<set geometry>>
        #@+<<set window title>>
        #@+node:tom.20210531235412.1: *4* <<set window title>>
        parents_ = [p for p in c.p.parents()]
        ph = parents_[0].h + '-->' if parents_ else ''
        self.setWindowTitle(f'{ph}{c.p.h}   {c.p.gnx}')
        #@-<<set window title>>

        self.render_kind = EDITOR
        self.setCentralWidget(central_widget)

        self.handlers = [('idle', self.update)]
        self._register_handlers()

        self.current_text = c.p.b
        self.editor.setPlainText(self.current_text)

        self.show()
    #@+node:tom.20210528090313.1: *3* update
    # Must have this signature: called by leoPlugins.callTagHandler.
    def update(self, tag, keywords):
        """Update host node if this card's text has changed.  Otherwise
           if the host node's text has changed, update the card's text 
           with the host's changed text.
        """
        if self.switching: return

        if self.doc.isModified():
            self.current_text = self.doc.toRawText()
            self.p.b = self.current_text
            self.doc.setModified(False)

        # if the current position in the outline is our own node, 
        # then synchronize the text if it's changed in the outline.
        elif self.c.p == self.p:
            doc = self.host_editor.document()
            if doc.isModified():
                self.current_text = doc.toRawText()
                self.editor.setPlainText(self.current_text)
                self.set_and_render(False)

        self.doc.setModified(False)
    #@+node:tom.20210527234644.1: *3* _register_handlers (floating_pane.py)
    def _register_handlers(self):
        """_register_handlers - attach to Leo signals
        """
        for hook, handler in self.handlers:
            g.registerHandler(hook, handler)

    #@+node:tom.20210529000221.1: *3* set_and_render
    def set_and_render(self, switch=True):
        """Switch between the editor and RsT viewer, and render text."""
        self.switching = True

        if not got_docutils:
            self.render_kind = EDITOR
        elif switch:
            if self.render_kind == BROWSER:
                self.render_kind = EDITOR
            else: 
                self.render_kind = BROWSER

        if self.render_kind == BROWSER:
            text = self.editor.document().toRawText()
            html = self.render_rst(text)
            self.browser.setHtml(html)

        self.stacked_widget.setCurrentIndex(self.render_kind)
        self.switching = False

    def switch_and_render(self):
        self.set_and_render(True)
    #@+node:tom.20210602174838.1: *3* render_rst
    def render_rst(self, text):
        """Render text of the editor widget as HTML and display it."""
        # Call docutils to get the html rendering.
        _html = ''
        args = {'embed_stylesheet': True,
                'report_level': RST_NO_WARNINGS,
               }

        if text:
            try:
                _html = publish_string(text, writer_name='html',
                                       settings_overrides=args)\
                        .decode(ENCODING)
            except SystemMessage as sm:
                msg = sm.args[0]
                if 'SEVERE' in msg or 'FATAL' in msg:
                    _html = f'RST error:\n{msg}\n\n{text}'
        return _html
    #@-others
#@-others
#@-leo
