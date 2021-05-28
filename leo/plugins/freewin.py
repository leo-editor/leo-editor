#@+leo-ver=5-thin
#@+node:tom.20210527153256.1: * @file ../plugins/freewin.py
#@@tabwidth -4
#@@language python
"""A plugin with a basic editor pane that tracks an outline node.

   Version 1.0b1
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
    from leo.core.leoQt import isQt6, QtCore, QtWidgets
except ImportError as e:
    g.trace(e)


#@+node:tom.20210527153422.1: ** Declarations
WindowFlags = QtCore.Qt.WindowFlags if isQt6 else QtCore.Qt
# pylint: disable=invalid-name
# Dimensions and placing of editor windows
W = 500
H = 300
X = 1200
Y = 250

BACK_COLOR = 'aliceblue'
EDITOR_FONT_SIZE = '11pt'
FONT_FAMILY = 'Consolas, Droid Sans Mono, DejaVu Sans Mono'

STYLESHEET = f'''QTextEdit {{
    background: {BACK_COLOR};
    font-family: {FONT_FAMILY};
    font-size: {EDITOR_FONT_SIZE};
    }}'''

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
    id_ = c.p.gnx

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

        widget = self.editor = QtWidgets.QTextEdit(self)
        self.doc = widget.document()

        self.setCentralWidget(widget)
        self.setWindowTitle(c.p.h)
        self.setGeometry(QtCore.QRect(X, Y, W, H))
        widget.setStyleSheet(STYLESHEET)
        widget.setText(c.p.b) 

        self.handlers = [('idle', self.update)]
        self._register_handlers()
    #@+node:tom.20210528090313.1: *3* update
    # Must have this signature: called by leoPlugins.callTagHandler.
    def update(self, tag, keywords):
        """Update host node if this card's text has changed.  Otherwise
           if the host node's text has changed, update the card's text 
           with the host's changed text.
        """
        if self.doc.isModified():
            self.p.b = self.doc.toRawText()
            self.doc.setModified(False)
        else:
            w = self.c.frame.body.wrapper
            editor = w.widget
            doc = editor.document()
            if doc.isModified():
                new_text = doc.toRawText()
                self.doc.setPlainText(new_text)
                self.doc.setModified(False)

    #@+node:tom.20210527234644.1: *3* _register_handlers (floating_pane.py)
    def _register_handlers(self):
        """_register_handlers - attach to Leo signals
        """
        for hook, handler in self.handlers:
            g.registerHandler(hook, handler)

    #@-others
#@-others

#@-leo
