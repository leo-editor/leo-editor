#@+leo-ver=5-thin
#@+node:ekr.20140919181357.24956: * @file ../plugins/qt_big_text.py
"""Leo aware Qt Dialog for delaying loading of big text"""
import leo.core.leoGlobals as g
from leo.core.leoQt import QtWidgets
import leo.plugins.qt_text as qt_text

#@+others
#@+node:tbrown.20140919120654.24038: ** class BigTextController
class BigTextController:
    #@+others
    #@+node:tbrown.20140919120654.24039: *3* btc.__init__
    def __init__(self,c):
        '''Ctor for BigTextController.'''
        self.active_flag = None # True: warning text/buttons are visible.
        self.c = c
        self.inhibit = set() # Set of inhibited vnodes.
        self.layout = None
        self.old_p = None
        self.old_w = None # A LeoQTextBrowser.
        self.p = None
        self.parent = None
        self.s = None
        self.w = None
    #@+node:ekr.20141019133149.18299: *3* btc.add_buttons
    def add_buttons(self,old_p,p):
        '''Init the big text controller for node p.'''
        c = self.c
        w = c.frame.body.wrapper.widget
        parent = w.parent() # A QWidget
        layout = parent.layout()
        # Set ivars
        self.active_flag = True
        self.layout = layout
        self.old_p = old_p
        self.old_w = w # A LeoQTextBrowser.
        self.p = p
        self.parent = parent
        self.s = p.b
        self.widgets = {}
            # Keys are strings, values are buttons.
        if p.v not in self.inhibit:
            self.create_widgets()
                # Create the big-text widgets.
        # g.trace('----- (LeoBigTextDialog)',len(self.s),self.w)
    #@+node:ekr.20141018081615.18272: *3* btc.create_widgets
    def create_widgets(self):
        '''Create the big-text buttons and text warning area.'''
        c = self.c
        self.active_flag = True
        warning = self.warning_message()
        self.old_w.setPlainText(self.p.b) # essential.
        self.w = w = QtWidgets.QWidget() # No parent needed.
        layout = QtWidgets.QVBoxLayout() # No parent needed.
        w.setLayout(layout)
        w.text = tw = QtWidgets.QTextBrowser()
        tw.setText(warning)
        tw.setObjectName('bigtextwarning')
        self.widgets['bigtextwarning'] = tw
        layout.addWidget(tw)
        table = [
                ('remove','Remove These Buttons',self.remove),
                ('load_nc','Load Text With @killcolor',self.load_nc),
                ('more','Double limit for this session',self.more),
                ('copy','Copy body to clipboard',self.copy),
        ]
        if self.s.startswith('@killcolor'):
            del table[1]
        for key,label,func in table:
            self.widgets[key] = button = QtWidgets.QPushButton(label)
            layout.addWidget(button)
            def button_callback(checked,func=func):
                func()
            button.clicked.connect(button_callback)
        # layout.addItem(QtWidgets.QSpacerItem(
            # 10, 10, vPolicy=QtWidgets.QSizePolicy.Expanding))
        self.layout.addWidget(w)
        w.show()
    #@+node:tbrown.20140919120654.24040: *3* btc.copy
    def copy(self):
        '''Copy self.s (c.p.b) to the clipboard.'''
        g.app.gui.replaceClipboardWith(self.s)
    #@+node:ekr.20141018081615.18276: *3* btc.go_away
    def go_away(self):
        '''Delete all buttons and self.'''
        # g.trace(self.w or 'None')
        self.active_flag = False
        c = self.c
        if self.w:
            self.layout.removeWidget(self.w)
            self.w.deleteLater()
            self.w = None
        c.bodyWantsFocusNow()
    #@+node:ekr.20141019133149.18298: *3* btc.is_qt_body
    def is_qt_body(self):
        '''Return True if the body widget is a QTextEdit.'''
        c = self.c
        w = c.frame.body.wrapper.widget
        val = isinstance(w,qt_text.LeoQTextBrowser)
            # c.frame.body.wrapper.widget is a LeoQTextBrowser.
            # c.frame.body.wrapper is a QTextEditWrapper or QScintillaWrapper.
        # g.trace(self.c.shortFileName(),val)
        return val

    #@+node:ekr.20141019133149.18296: *3* btc.is_big_text
    def is_big_text(self,p):
        '''True if p.b is large and the text widget supports big text buttons.'''
        c = self.c
        if c.max_pre_loaded_body_chars > 0:
            wrapper = c.frame.body.wrapper
            w = wrapper and wrapper.widget
            val = w and len(p.b) > c.max_pre_loaded_body_chars
        else:
            val = False
        # g.trace(c.shortFileName(),p.h,val)
        return val
    #@+node:tbrown.20140919120654.24042: *3* btc.load_nc
    def load_nc(self):
        '''Load the big text with a leading @killcolor directive.'''
        traceTime = False
        c,p = self.c,self.c.p
        if not c.positionExists(p):
            return
        self.wait_message()
        # Recreate the entire select code.
        tag = "@killcolor\n"
        if not p.b.startswith(tag):
            p.b = tag+p.b
        w = self.c.frame.body.wrapper
        self.go_away()
        w.setInsertPoint(0)
        w.seeInsertPoint()
        c.bodyWantsFocusNow()
        c.recolor_now()
    #@+node:tbrown.20140919120654.24043: *3* btc.more
    def more(self):
        '''
        Double the big text limit for this session.
        Load the text if the text is less than this limit.
        '''
        c = self.c
        c.max_pre_loaded_body_chars *= 2
        if len(c.p.b) < c.max_pre_loaded_body_chars:
            self.wait_message()
            self.inhibit.add(c.p.v)
            self.go_away()
            c.selectPosition(self.p)
        else:
            tw = self.widgets.get('bigtextwarning')
            tw.setText(self.warning_message())
            g.es('limit is now: %s' % c.max_pre_loaded_body_chars)
    #@+node:ekr.20141020112451.18341: *3* btc.remove
    def remove(self):
        '''Remove the buttons and inhibit them hereafter.'''
        c = self.c
        self.inhibit.add(c.p.v)
        self.go_away()
    #@+node:ekr.20141019133149.18295: *3* btc.should_add_buttons
    def should_add_buttons(self,old_p,p):
        '''Return True if big-text buttons should be added.'''
        if g.app.unitTesting:
            return False # Don't add buttons during testing.
        if self.c.undoer.undoing:
            return False # Suppress buttons during undo.
        if self.active_flag:
            return False # Buttons already created.
        if p.v in self.inhibit:
            return False # Buttons are inhibited for this vnode.
        return self.is_big_text(p) and self.is_qt_body()
    #@+node:ekr.20141019190455.18296: *3* btc.should_go_away
    def should_go_away(self,p):
        '''Return True if big-text buttons should be removed.'''
        if self.c.undoer.undoing:
            return False # Suppress buttons during undo.
        else:
            return self.active_flag and not self.is_big_text(p)
    #@+node:tbrown.20140919120654.24044: *3* btc.wait_message
    def wait_message(self):
        '''Issue a message asking the user to wait until all text loads.'''
        g.es(
            "Loading large text, please wait\n"
            "until scrollbar stops shrinking",color='red')
    #@+node:ekr.20141018081615.18279: *3* btc.warning_message
    def warning_message(self):
        '''Return the warning message.'''
        c = self.c
        s = '''\
    Loading big text (%s characters, limit is %s characters)

    Beware of a Qt bug: You will **lose data** if you change the text
    before it is fully loaded (before the scrollbar stops moving).

    To disable these buttons set @bool max-pre-loaded-body-chars = 0
    '''
        s = s.rstrip() % (len(self.s),c.max_pre_loaded_body_chars)
        return g.adjustTripleString(s,c.tab_width)
    #@-others
#@-others
#@-leo
