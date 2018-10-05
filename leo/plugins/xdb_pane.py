#@+leo-ver=5-thin
#@+node:ekr.20181004143535.1: * @file xdb_pane.py
'''
Creates a Debug tab in the log pane, containing buttons for common xdb
commands, and an input area in which the user can type other commands.
'''
import leo.core.leoGlobals as g
from leo.core.leoQt import QtGui,QtWidgets # QtConst,QtCore,
#@+others
#@+node:ekr.20181005051820.1: ** Top-level functions
#@+node:ekr.20181004143535.4: *3* init (xdb_pane.py)
def init():
    '''Return True if the plugin has loaded successfully.'''
    name = g.app.gui.guiName()
    if name != "qt":
        if name not in ('curses', 'nullGui'):
            print('xdb_pane.py plugin not loading because gui is not Qt')
        return False
    g.registerHandler('after-create-leo-frame',onCreate)
        # Can't use before-create-leo-frame because Qt dock's not ready
    g.plugin_signon(__name__)
    return True
#@+node:ekr.20181004143535.5: *3* onCreate (xdb_pane.py)
def onCreate (tag,key):
    c = key.get('c')
    w = XdbPane(c)
    c.frame.log.createTab('Debug',widget=w)
#@+node:ekr.20181004143535.7: ** class XdbPane
if g.app.gui.guiName() == "qt":

    class XdbPane(QtWidgets.QWidget):
        
        def __init__(self, c):
            self.c = c
            QtWidgets.QWidget.__init__(self)
            self.create()

        #@+others
        #@+node:ekr.20181005043209.1: *3* create & helpers
        def create(self):
            '''Create the Debug pane in the Log pane.'''
            layout = QtWidgets.QVBoxLayout(self)
            self.create_icons(layout)
            self.create_input_area(layout)
            layout.addStretch()
            self.setLayout(layout)
            
        #@+node:ekr.20181004182608.1: *4* create_icons
        def create_icons(self, layout):
            
            layout2 = QtWidgets.QHBoxLayout()
            for name, fn, func in [
                ('start', 'pyzo_run_file.png', self.debug_start),
                ('stop', 'pyzo_debug_quit.png', self.debug_stop),
                ('continue', 'pyzo_debug_continue.png', self.debug_continue),
                ('next', 'pyzo_debug_next.png', self.debug_next),
                ('step', 'pyzo_debug_step.png', self.debug_step),
                ('return', 'pyzo_debug_return.png', self.debug_return),
            ]:
                w = QtWidgets.QPushButton(None)
                layout2.addWidget(w)
                w.setText(name)
                # icon = self.get_icon(fn)
                # w.setIcon(icon)
                w.clicked.connect(func)
            layout.addLayout(layout2)
        #@+node:ekr.20181005054101.1: *4* create_input_area
        def create_input_area(self, layout):
            
            layout2 = QtWidgets.QHBoxLayout()
            # Create the Label
            label = QtWidgets.QLabel()
            label.setText('Debugger command:')
            # Create the editor.
            self.line_edit = w = QtWidgets.QLineEdit()
            w.setStyleSheet('background: white; color: black;')
            w.returnPressed.connect(self.debug_input)
            # Add the widgets.
            layout2.addWidget(label)
            layout2.addWidget(w)
            layout.addLayout(layout2)
        #@+node:ekr.20181004143535.20: *4* get_icon
        def get_icon(self, fn):
            """return the icon from Icons/debug_icons"""
            path = g.os_path_finalize_join(
                g.app.loadDir, '..', 'Icons', 'debug_icons', fn)
            return QtGui.QIcon(g.app.gui.getImageImage(path))
        #@+node:ekr.20181005042637.1: *3* debug_*
        def debug_continue(self, checked):
            self.c.k.simulateCommand('db-c')
            
        def debug_input(self):
            xdb = getattr(g.app, 'xdb', None)
            if xdb:
                command = self.line_edit.text()
                xdb.qc.put(command)
            else:
                print('xdb not active')

        def debug_next(self, checked):
            self.c.k.simulateCommand('db-n')
            
        def debug_return(self, *args):
            self.c.k.simulateCommand('db-r')
            
        def debug_start(self, *args):
            self.c.k.simulateCommand('xdb')
            
        def debug_step(self, *args):
            self.c.k.simulateCommand('db-s')
            
        def debug_stop(self, *args):
            self.c.k.simulateCommand('db-kill')
        #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
