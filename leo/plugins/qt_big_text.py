#@+leo-ver=5-thin
#@+node:ekr.20140919181357.24956: * @file ../plugins/qt_big_text.py
"""Leo aware Qt Dialog for delaying loading of big text"""
import leo.core.leoGlobals as g
from leo.core.leoQt import QtGui

#@+others
#@+node:tbrown.20140919120654.24038: ** class LeoBigTextDialog
class LeoBigTextDialog(QtGui.QWidget):
    #@+others
    #@+node:tbrown.20140919120654.24039: *3* __init__
    def __init__(self, *args, **kwargs):
        our_args = 'c', 'old_p', 'p', 's', 'traceTime', 'w', 'layout', 'owner'
        for arg in our_args:
            setattr(self, arg, kwargs.get(arg, None))
            if arg in kwargs:
                del kwargs[arg]
                
        assert hasattr(self.w, 'leo_big_text')
                
        QtGui.QWidget.__init__(self, *args, **kwargs)
        
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        self.text = text = QtGui.QTextBrowser()
        text.setText(
            "%d character text exceeds %d limit, not shown.\n\n"
            "To load the body text, click the 'load' button.\n"
            "Warning: make sure the text is fully loaded before using it!.\n\n"
            "Set @int max-pre-loaded-body-chars in @settings\n"
            "to permanently change limit."
            % (len(self.s), self.c.max_pre_loaded_body_chars))
        layout.addWidget(text)
        if self.s.startswith('@nocolor'):
            self.leo_load_nc_button = None
        else:
            self.leo_load_nc_button = QtGui.QPushButton(
            'Load Text with @nocolor: %s' % (self.p.h))
            layout.addWidget(self.leo_load_nc_button)
            self.leo_load_nc_button.clicked.connect(
                lambda checked: self.load(nocolor=True))
        self.leo_load_button = QtGui.QPushButton(
            'Load Text: %s' % (self.p.h))
        self.leo_more_button = QtGui.QPushButton(
            'Double limit for this session')
        self.leo_copy_button = QtGui.QPushButton(
            'Copy body to clipboard: %s' % (self.p.h))
        # Put the @nocolor button second: it should not be the "default".
        for w in (
            self.leo_load_button, self.leo_load_nc_button,
            self.leo_copy_button, self.leo_more_button,
        ):
            if w:
                layout.addWidget(w)
        layout.addItem(QtGui.QSpacerItem(
            10, 10, vPolicy=QtGui.QSizePolicy.Expanding))
        self.leo_copy_button.clicked.connect(lambda checked: self.copy())
        self.leo_load_button.clicked.connect(lambda checked: self.load())
        self.leo_more_button.clicked.connect(lambda checked: self.more())
        self.show()
    #@+node:tbrown.20140919120654.24040: *3* copy
    def copy(self): 
        g.app.gui.replaceClipboardWith(self.s)
    #@+node:tbrown.20140919120654.24041: *3* go_away
    def go_away(self):
        bt = self
        bt.layout.addWidget(bt.w)
        bt.layout.removeWidget(bt)
        bt.w.leo_big_text_w.deleteLater()
        bt.w.leo_big_text_w = None
        bt.w.leo_big_text = None
    #@+node:tbrown.20140919120654.24042: *3* load
    def load(self, nocolor=False):
        bt = self
        bt.wait()
        if bt.c.positionExists(bt.p):
            # Recreate the entire select code.
            if nocolor:
                bt.p.b = "@nocolor\n"+bt.p.b
            bt.owner.set_body_text_after_select(bt.p,bt.old_p,bt.traceTime,force=True)
            bt.owner.scroll_cursor(bt.p,bt.traceTime)
            # g.trace('calling onBodyChanged')
            ### bt.c.frame.body.onBodyChanged(undoType='Typing')
        bt.go_away()
        bt.c.bodyWantsFocusNow()
        bt.c.recolor_now()
    #@+node:tbrown.20140919120654.24043: *3* more
    def more(self):
        bt = self
        c = bt.c
        c.max_pre_loaded_body_chars *= 2
        if len(c.p.b) < c.max_pre_loaded_body_chars:
            bt.wait()
            bt.go_away()
            c.selectPosition(bt.p)
        else:
            g.es_print('limit is now: %s' % c.max_pre_loaded_body_chars)
    #@+node:tbrown.20140919120654.24044: *3* wait
    def wait(self):
        bt = self
        msg = "Loading large text, please wait\nuntil scrollbar stops shrinking"
        bt.text.setText(msg)
        g.es(msg)
        bt.leo_load_button.hide()
        bt.leo_more_button.hide()
        bt.leo_copy_button.hide()
        if hasattr(bt, 'leo_load_nc_button'):
            bt.leo_load_nc_button.hide()
        QtGui.QApplication.processEvents()  
        # hide buttons *now* to prevent extra clicks
    #@-others
#@-others
#@-leo
