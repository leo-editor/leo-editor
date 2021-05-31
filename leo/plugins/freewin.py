#@+leo-ver=5-thin
#@+node:tom.20210527153256.1: * @file ../plugins/freewin.py
#@@tabwidth -4
#@@language python
"""A plugin with a basic editor pane that tracks an outline node.

   Version 1.0b3
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

try:
    from leo.core.leoQt import Qt, isQt6, QtCore, QtWidgets
except ImportError as e:
    g.trace(e)

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

#@+node:tom.20210527153422.1: ** Declarations
# pylint: disable=invalid-name
# Dimensions and placing of editor windows
W = 570
H = 350
X = 1200
Y = 250

BACK_COLOR = 'aliceblue'
EDITOR_FONT_SIZE = '11pt'
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
        self.c = c
        self.p = c.p

        w = self.c.frame.body.wrapper
        self.host_editor = w.widget

        QtWidgets.QWidget.__init__(self) # per http://enki-editor.org/2014/08/23/Pyqt_mem_mgmt.html

        #self.setObjectName('ZEditorWindow')

        #@+<<create widgets>>
        #@+node:tom.20210528235126.1: *4* <<create widgets>>
        widget = self.editor = QtWidgets.QTextEdit(self)
        self.doc = widget.document()
        widget.setStyleSheet(STYLESHEET)

        self.render_button  = QtWidgets.QPushButton("Rendered/Plain")
        self.render_button.clicked.connect(self.render)

        central_widget = QtWidgets.QWidget()

        #@-<<create widgets>>
        #@+<<create layouts>>
        #@+node:tom.20210528235142.1: *4* <<create layouts>>
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.render_button)
        layout.addWidget(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        #@-<<create layouts>>
        #@+<<set geometry>>
        #@+node:tom.20210528235451.1: *4* <<set geometry>>
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        self.setGeometry(QtCore.QRect(X, Y, W, H))
        #@-<<set geometry>>

        self.handlers = [('idle', self.update)]
        self._register_handlers()

        self.setWindowTitle(f'{c.p.h}   {c.p.gnx}')
        self.current_text = c.p.b
        widget.setText(self.current_text) 

        self.show_rendered = False
    #@+node:tom.20210528090313.1: *3* update
    # Must have this signature: called by leoPlugins.callTagHandler.
    def update(self, tag, keywords):
        """Update host node if this card's text has changed.  Otherwise
           if the host node's text has changed, update the card's text 
           with the host's changed text.
        """
        if self.doc.isModified():
            if not self.show_rendered:
                new_text = self.doc.toRawText()
                self.p.b = new_text
                self.current_text = new_text
                self.doc.setModified(False)
        # if the current position in the outline is our own node, 
        # then synchronize the text if it's changed in the outline.
        elif self.c.p == self.p:
            doc = self.host_editor.document()
            if doc.isModified():
                new_text = doc.toRawText()
                if self.show_rendered:
                    self.editor.setHtml(new_text)
                else:
                    self.doc.setPlainText(new_text)
                self.doc.setModified(False)
                doc.setModified(False)
                self.current_text = new_text
    #@+node:tom.20210527234644.1: *3* _register_handlers (floating_pane.py)
    def _register_handlers(self):
        """_register_handlers - attach to Leo signals
        """
        for hook, handler in self.handlers:
            g.registerHandler(hook, handler)

    #@+node:tom.20210529000221.1: *3* render
    def render(self):
        """Render text of the editor widget as HTML and display it."""
        self.show_rendered = not self.show_rendered
        text = self.current_text

        if not self.show_rendered:
            self.editor.setTextInteractionFlags(Qt.Qt.TextEditorInteraction)
            self.editor.setPlainText(text)
        else:
            # Call docutils to get the html rendering.
            _html = ''
            args = {'report_level':RST_NO_WARNINGS}
            if text:
                try:
                    _html = publish_string(text, writer_name='html',
                                           settings_overrides=args)
                    _html = _html.decode(ENCODING)
                except SystemMessage as sm:
                    msg = sm.args[0]
                    if 'SEVERE' in msg or 'FATAL' in msg:
                        _html = f'RST error:\n{msg}\n\n{text}'
                self.editor.setTextInteractionFlags(Qt.Qt.NoTextInteraction or Qt.Qt.LinksAccessibleByMouse)
                self.editor.setHtml(_html)
                self.doc.setModified(False)
    #@-others
#@-others
#@-leo
