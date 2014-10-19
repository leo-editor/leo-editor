#@+leo-ver=5-thin
#@+node:ekr.20140919181357.24956: * @file ../plugins/qt_big_text.py
"""Leo aware Qt Dialog for delaying loading of big text"""
import leo.core.leoGlobals as g
from leo.core.leoQt import QtGui

#@+others
#@+node:tbrown.20140919120654.24038: ** class BigTextController
class BigTextController:
    #@+others
    #@+node:tbrown.20140919120654.24039: *3* __init__
    def __init__(self,c,layout,old_p,old_w,owner,p,parent,s):
        '''Ctor for BigTextController.'''
        self.c = c
        self.widgets = {} # Keys are strings, values are buttons.
        self.old_p = old_p
        self.p = p
        self.layout = layout
        self.old_p = old_p
        self.old_w = old_w # A LeoQTextBrowser.
        self.owner = owner # A LeoQtTree.
        self.parent = parent
        self.s = s
        self.traceTime = False
        # Create the big-text widgets.
        self.create()
        # g.trace('----- (LeoBigTextDialog)',len(s),self.w)
    #@+node:tbrown.20140919120654.24040: *3* copy
    def copy(self):
        '''Copy self.s (c.p.b) to the clipboard.'''
        g.app.gui.replaceClipboardWith(self.s)
    #@+node:ekr.20141018081615.18272: *3* create
    def create(self):
        '''Create the big-text buttons.'''
        c = self.c
        warning = self.warning_message()
        self.old_w.setPlainText(self.p.b) # essential.
        self.w = w = QtGui.QWidget() # No parent needed.
        layout = QtGui.QVBoxLayout() # No parent needed.
        w.setLayout(layout)
        w.text = tw = QtGui.QTextBrowser()
        tw.setText(warning)
        tw.setObjectName('bigtextwarning')
        self.widgets['bigtextwarning'] = tw
        layout.addWidget(tw)
        table = (
            ('remove','Remove These Buttons',self.go_away),
            ('load_nc','Load Text With @killcolor',self.load_nc),
            ('more','Double limit for this session',self.more),
            ('copy','Copy body to clipboard',self.copy),
        )
        for key,label,func in table:
            self.widgets[key] = button = QtGui.QPushButton(label)
            layout.addWidget(button)
            def button_callback(checked,func=func):
                func()
            button.clicked.connect(button_callback)
        # layout.addItem(QtGui.QSpacerItem(
            # 10, 10, vPolicy=QtGui.QSizePolicy.Expanding))
        self.layout.addWidget(w)
        w.show()
    #@+node:ekr.20141018081615.18276: *3* go_away
    def go_away(self):
        '''Delete all buttons and self.'''
        # g.trace(self.w or 'None')
        if self.w:
            self.layout.removeWidget(self.w)
            self.w.deleteLater()
            self.w = None
            self.c.bodyWantsFocus()
    #@+node:tbrown.20140919120654.24042: *3* load_nc
    def load_nc(self):
        '''Load the big text with a leading @killcolor directive.'''
        c,p,traceTime = self.c,self.c.p,self.traceTime
        if not c.positionExists(p):
            return
        self.wait_message()
        # Recreate the entire select code.
        tag = "@killcolor\n"
        if not p.b.startswith(tag):
            p.b = tag+p.b
        w = self.c.frame.body.wrapper
        self.go_away()
        self.owner.set_body_text_after_select(p,self.old_p,traceTime,force=True)
        self.owner.scroll_cursor(p,traceTime)
        w.setInsertPoint(0)
        w.seeInsertPoint()
        c.bodyWantsFocusNow()
        c.recolor_now()
    #@+node:tbrown.20140919120654.24043: *3* more
    def more(self):
        '''
        Double the big text limit for this session.
        Load the text if the text is less than this limit.
        '''
        c = self.c
        c.max_pre_loaded_body_chars *= 2
        if len(c.p.b) < c.max_pre_loaded_body_chars:
            self.wait_message()
            self.go_away()
            c.selectPosition(self.p)
        else:
            tw = self.widgets.get('bigtextwarning')
            tw.setText(self.warning_message())
            g.es('limit is now: %s' % c.max_pre_loaded_body_chars)
    #@+node:tbrown.20140919120654.24044: *3* wait_message
    def wait_message(self):
        '''Issue a message asking the user to wait until all text loads.'''
        g.es("Loading large text, please wait\nuntil scrollbar stops shrinking",color='red')
    #@+node:ekr.20141018081615.18279: *3* warning_message
    def warning_message(self):
        '''Return the warning message.'''
        c = self.c
        s = '''\
    Loading big text (%s characters, limit is %s characters)

    Beware of a Qt bug: You will **lose data** if you change the text
    before it is fully loaded (before the scrollbar stops moving).
    '''
        s = s.rstrip() % (len(self.s),c.max_pre_loaded_body_chars)
        return g.adjustTripleString(s,c.tab_width)
    #@-others
#@-others
#@-leo
