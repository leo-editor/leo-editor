#@+leo-ver=5-thin
#@+node:ekr.20181004143535.1: * @file ../plugins/xdb_pane.py
"""
Creates a Debug tab in the log pane, containing buttons for common xdb
commands, and an input area in which the user can type other commands.
"""
#@+<< imports: xdb_pane.py >>
#@+node:ekr.20220424085736.1: ** << imports: xdb_pane.py >>
from typing import Any
from leo.core import leoGlobals as g
from leo.core.leoQt import QtGui, QtWidgets
from leo.core.leoQt import ScrollBarPolicy, WrapMode
# Fail fast, right after all imports.
g.assertUi('qt')  # May raise g.UiTypeException, caught by the plugins manager.
#@-<< imports: xdb_pane.py >>

# Globals.
controllers: dict[str, Any] = {}

#@+others
#@+node:ekr.20181005051820.1: ** Top-level functions
#@+node:ekr.20181004143535.4: *3* init (xdb_pane.py)
def init():
    """Return True if the plugin has loaded successfully."""
    name = g.app.gui.guiName()
    if name != "qt":
        if name not in ('curses', 'nullGui'):
            print('xdb_pane.py plugin not loading because gui is not Qt')
        return False
    # Can't use before-create-leo-frame because Qt dock's not ready
    g.registerHandler('after-create-leo-frame', onCreate)
    g.plugin_signon(__name__)
    return True
#@+node:ekr.20181004143535.5: *3* onCreate (xdb_pane.py)
def onCreate(tag, key):
    c = key.get('c')
    c.xpd_pane = w = XdbPane(c)
    c.frame.log.createTab('Debug', widget=w)
#@+node:ekr.20181004143535.7: ** class XdbPane
if g.app.gui.guiName() == "qt":

    class XdbPane(QtWidgets.QWidget):  # type:ignore
        """Create the contents of the Debug pane."""

        def __init__(self, c):
            self.c = c
            super().__init__()
            self.create()

        #@+others
        #@+node:ekr.20181005043209.1: *3* create & helpers
        def create(self):
            """Create the Debug tab in the Log pane."""
            c = self.c
            layout = QtWidgets.QVBoxLayout(self)
            self.create_buttons(layout)
            self.create_input_area(layout)
            if c.config.getBool('use-xdb-pane-output-area', default=True):
                self.create_output_area(layout)
            else:
                self.output_area = None
            layout.addStretch()
            self.setLayout(layout)
        #@+node:ekr.20181004182608.1: *4* create_buttons
        def create_buttons(self, layout):
            """Create two rows of buttons."""
            vlayout = QtWidgets.QVBoxLayout()
            table1 = (
                ('start', self.debug_xdb),
                ('quit', self.debug_quit),
                ('help', self.debug_help),
                ('list', self.debug_list),
                ('where', self.debug_where),
            )
            table2 = (
                ('break', self.debug_break),
                ('continue', self.debug_continue),
                ('next', self.debug_next),
                ('step', self.debug_step),
                ('return', self.debug_return),
            )
            for table in (table1, table2):
                hlayout = QtWidgets.QHBoxLayout()
                for name, func in table:
                    w = QtWidgets.QPushButton()
                    w.setText(name)
                    w.clicked.connect(func)
                    hlayout.addWidget(w)
                vlayout.addLayout(hlayout)
            layout.addLayout(vlayout)
        #@+node:ekr.20181005054101.1: *4* create_input_area
        def create_input_area(self, layout):

            # Create the Label
            label = QtWidgets.QLabel()
            label.setText('Debugger command:')
            # Create the editor.
            self.line_edit = w = QtWidgets.QLineEdit()
            w.setStyleSheet('background: white; color: black;')
            w.returnPressed.connect(self.debug_input)
            # Add the widgets to a new layout.
            layout2 = QtWidgets.QVBoxLayout()
            layout2.addWidget(label)
            layout2.addWidget(w)
            layout.addLayout(layout2)
        #@+node:ekr.20181006154605.1: *4* create_output_area
        def create_output_area(self, layout):

            # Create the Label
            label = QtWidgets.QLabel()
            label.setText('Debugger outpuit:')
            # Create the output area.
            self.output_area = w = QtWidgets.QTextEdit()
            w.setStyleSheet('background: white; color: black;')
            w.setHorizontalScrollBarPolicy(ScrollBarPolicy.ScrollBarAsNeeded)
            w.setWordWrapMode(WrapMode.NoWrap)
            # Add the widgets to a new layout.
            vlayout = QtWidgets.QVBoxLayout()
            vlayout.addWidget(label)
            vlayout.addWidget(w)
            layout.addLayout(vlayout)
        #@+node:ekr.20181004143535.20: *4* get_icon
        def get_icon(self, fn):
            """return the icon from Icons/debug_icons"""
            path = g.finalize_join(g.app.loadDir, '..', 'Icons', 'debug_icons', fn)
            return QtGui.QIcon(g.app.gui.getImageImage(path))
        #@+node:ekr.20181005042637.1: *3* debug_*
        def debug_break(self, checked):
            self.c.k.simulateCommand('db-b')

        def debug_continue(self, checked):
            self.c.k.simulateCommand('db-c')

        def debug_help(self, checked):
            self.c.k.simulateCommand('db-h')

        def debug_input(self):
            xdb = getattr(g.app, 'xdb', None)
            if xdb:
                command = self.line_edit.text()
                xdb.qc.put(command)
            else:
                print('xdb not active')

        def debug_list(self, checked):
            self.c.k.simulateCommand('db-l')

        def debug_next(self, checked):
            self.c.k.simulateCommand('db-n')

        def debug_quit(self, *args):
            self.c.k.simulateCommand('db-q')

        def debug_return(self, *args):
            self.c.k.simulateCommand('db-r')

        def debug_step(self, *args):
            self.c.k.simulateCommand('db-s')

        def debug_where(self, *args):
            self.c.k.simulateCommand('db-w')

        def debug_xdb(self, *args):
            self.c.k.simulateCommand('xdb')
        #@+node:ekr.20181006161938.1: *3* write & clear
        def clear(self):
            """Clear the output area."""
            w = self.output_area
            if w:
                w.setPlainText('')

        def write(self, s):
            """Write the line s to the output area, or print it."""
            w = self.output_area
            if w:
                w.insertPlainText(s)
                w.moveCursor(QtGui.QTextCursor.End)
            else:
                print(s.rstrip())
        #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
