#@+leo-ver=5-thin
#@+node:ekr.20120913110135.10579: * @file screencast.py
#@+<< docstring >>
#@+node:ekr.20120913110135.10589: ** << docstring >>
'''Screencast tools for Leo.

Injects c.screencast_controller ivar into all commanders.
'''
#@-<< docstring >>
#@+<< imports >>
#@+node:ekr.20120913110135.10590: ** << imports >>
import random

import leo.core.leoGlobals as g
import leo.core.leoGui as leoGui # for leoKeyEvents.

# import PyQt4.Qt as Qt
import PyQt4.QtCore as QtCore
import PyQt4.QtGui as QtGui
#@-<< imports >>

# To do:
# Make sure ctrl-g calls c.screenCastController.delete_widgets.
# Convenience methods for common images.

#@@language python
#@@tabwidth -4

#@+others
#@+node:ekr.20120913110135.10608: ** top-level
#@+node:ekr.20120913110135.10603: *3* init
def init ():
        
    ok = g.app.gui.guiName() in ('qt','qttabs')

    if ok:
        g.registerHandler('after-create-leo-frame',onCreate)
        g.plugin_signon(__name__)

    return ok
#@+node:ekr.20120913110135.10604: *3* onCreate
def onCreate (tag, keys):
    
    '''Inject c.screenshot_controller into the commander.'''
    
    c = keys.get('c')
    if c:
        c.screencast_controller = scc = ScreenCastController(c)
#@+node:ekr.20120913110135.10607: ** class ScreenCastController
class ScreenCastController:
    
    #@+others
    #@+node:ekr.20120913110135.10606: *3* __init__ (ScreenCastController)
    def __init__(self,c):
        
        self.c = c
        self.log_color = 'black'
        self.log_focus = True # True: writing to log sets focus to log.
        self.ignore_keys = False # True: ignore keys in state_handler.
        self.manual = True # True: transition manually between scenes.
        self.n1 = 0.02 # default minimal typing delay.
        self.n2 = 0.175 # default maximum typing delay.
        self.p1 = None # The first slide of the show.
        self.p = None # The present slide of the show.
        self.speed = 1.0 # Amount to multiply wait times.
        self.widgets = [] # List of (popup) widgets created by this class.
        
        # inject c.screenCastController
        c.screenCastController = self
    #@+node:ekr.20120913110135.10580: *3* body_keys
    def body_keys (self,s,n1=None,n2=None):
        
        m = self
        c = m.c
        if n1 is None: n1 = m.n1
        if n2 is None: n2 = m.n2
        c.bodyWantsFocusNow()
        p = c.p
        w = c.frame.body.bodyCtrl.widget
        for ch in s:
            p.b = p.b + ch
            w.repaint()
            m.wait(n1,n2,force=True)
        c.redraw()
    #@+node:ekr.20120914133947.10578: *3* caption
    def caption (self,pane,s,center=False):
        
        '''Pop up a QPlainTextEdit in the indicated pane.'''
        
        m = self
        parent = m.pane_widget(pane)
        if parent:
            s = s.rstrip()
            if s and s[-1].isalpha(): s = s+'.'
            w = QtGui.QPlainTextEdit(s,parent)
            m.widgets.append(w)
            w2 = m.pane_widget(pane)
            geom = w2.geometry()
            w.resize(geom.width(),min(100,geom.height()/2))
            off = QtCore.Qt.ScrollBarAlwaysOff
            w.setHorizontalScrollBarPolicy(off)
            w.setVerticalScrollBarPolicy(off)
            font = w.font()
            font.setPointSize(18)
            w.setFont(font)
            w.show()
            return w
        else:
            g.trace('bad pane: %s' % (pane))
            return None
    #@+node:ekr.20120913110135.10612: *3* clear_log
    def clear_log (self):
        
        '''Clear the log.'''

        m = self
        m.c.frame.log.clearTab('Log')
    #@+node:ekr.20120913110135.10581: *3* command
    def command(self,command_name):
        
        m = self
        c = m.c
        c.k.simulateCommand(command_name)
        c.redraw()
        m.repaint('all')
    #@+node:ekr.20120914163440.10581: *3* delete_widgets
    def delete_widgets (self):
        
        m = self
        for w in m.widgets:
            w.deleteLater()
        m.widgets=[]
    #@+node:ekr.20120913110135.10582: *3* focus
    def focus(self,pane):

        m = self
        c = m.c
        d = {
            'body': c.bodyWantsFocus,
            'log': c.logWantsFocus,
            'tree': c.treeWantsFocus,
        }
        
        f = d.get(pane)
        if f:
            f()
            c.outerUpdate()
            m.repaint(pane)
        else:
            g.trace('bad pane: %s' % (pane))
    #@+node:ekr.20120913110135.10583: *3* head_keys
    def head_keys(self,s,n1=None,n2=None):
        
        m = self
        c = m.c
        p = c.p
        if n1 is None: n1 = m.n1
        if n2 is None: n2 = m.n2
        p.h=''
        tree = c.frame.tree
        c.editHeadline()
        w = tree.edit_widget(p)
        m.ignore_keys = True
        try:
            for ch in s:
                p.h = p.h + ch
                tree.repaint() # *not* tree.update.
                m.wait(n1,n2,force=True)
                event = leoGui.leoKeyEvent(c,ch,ch,w,x=0,y=0,x_root=0,y_root=0)
                c.k.masterKeyHandler(event)
        finally:
            m.ignore_keys = False
        # Ensure the final result is correct.
        # tree.repaint()
        p.h=s
        c.redraw()
    #@+node:ekr.20120913110135.10615: *3* image
    def image(self,pane,pixmap):
        
        '''Put an image in the indicated pane.'''

        m = self
        parent = m.pane_widget(pane)
        if parent:
            w = QtGui.QLabel('label',parent)
            m.widgets.append(w)
            w.setPixmap(pixmap)
            w.show()
            return w
        else:
            g.trace('bad pane: %s' % (pane))
            return None

        
    #@+node:ekr.20120913110135.10584: *3* key
    def key(self,setting,command):

        '''Simulate hitting the key.  Show the key in the log pane.'''

        m = self
        c = m.c
        stroke = c.k.strokeFromSetting(setting)
        # g.es(stroke.s)
        c.k.simulateCommand(command)
        c.redraw()
        m.repaint('all')
    #@+node:ekr.20120913110135.10610: *3* log
    def log(self,s,begin=False,end=False,image_fn=None,pane='log'):
        
        '''Put a message to the log pane, highlight it, and pause.'''
        
        m = self

        if not begin:
            m.wait(1)
            
        m.caption(pane,s)
        
        # if m.log_focus:
            # m.focus('log')

        m.repaint('all')
        
        if not end:
            m.wait(1)
        
        
    #@+node:ekr.20120914074855.10721: *3* next
    def next (self):
        
        '''Find the next non-empty screencast node and execute its script.'''
        
        trace = False and not g.unitTesting
        m = self
        m.delete_widgets()
        
        while m.p:
            if trace: g.trace(m.p.h)
            h = m.p.h.replace('_','').replace('-','')
            if g.match_word(h,0,'@ignore'):
                if trace: g.trace(h)
                m.p.moveToThreadNext()
            elif g.match_word(h,0,'@ignoretree'):
                if trace: g.trace(h)
                m.p.moveToNodeAfterTree()
            else:
                p2 = m.p.copy()
                m.p.moveToThreadNext()
                if p2.b.strip():
                    if trace: g.trace('executing',p2.h)
                    d = {'c':m.c,'g:':g,'m':m,'p':p2}
                    m.c.executeScript(p=p2,namespace=d,useSelectedText=False)
                        # event=None, args=None, p=None,
                        # script=None, define_g=True,
                        # define_name='__main__', silent=False
                    break
        else:
            m.quit()
    #@+node:ekr.20120914133947.10579: *3* pane_widget
    def pane_widget (self,pane):
        
        '''Return the pane's widget.'''
        
        m = self
        c = m.c
        d = {
            'all':  c.frame.top,
            'body': c.frame.body.bodyCtrl.widget,
            'log':  c.frame.log.logCtrl.widget,
            'tree': c.frame.tree.treeWidget,
        }
        return d.get(pane)
    #@+node:ekr.20120914074855.10722: *3* quit
    def quit (self):
        
        '''Terminate the slide show.'''
        
        m = self
        g.trace('\n *** end of slide show at: %s' % (m.p1.h))
        m.delete_widgets()
        m.c.k.keyboardQuit()
    #@+node:ekr.20120913110135.10585: *3* repaint
    def repaint(self,pane):

        m = self
        c = m.c
        d = {
            'all':  c.frame.top,
            'body': c.frame.body.bodyCtrl.widget,
            'log':  c.frame.log.logCtrl.widget,
            'tree': c.frame.tree.treeWidget,
        }
        w = d.get(pane)
        if w:
            # g.trace(pane,w)
            w.repaint()
        else:
            g.trace('bad pane: %s' % (pane))
    #@+node:ekr.20120914163440.10582: *3* resolve_icon_fn
    def resolve_icon_fn (self,fn):
        
        m = self

        # Resolve relative file names relative to the Icons directory.
        dir_ = g.os_path_finalize_join(g.app.loadDir,'..','Icons')
        path = g.os_path_finalize_join(dir_,fn)
        
        if g.os_path_exists(path):
            return path
        else:
            g.trace('does not exist: %s' % (path))
            return None
    #@+node:ekr.20120913110135.10611: *3* set_log_focus & set_speed
    def set_log_focus(self,val):

        m = self
        m.log_focus = bool(val)

    def set_speed (self,speed):
        
        m = self
        if speed < 0:
            g.trace('speed must be >= 0.0')
        else:
            m.speed = speed
    #@+node:ekr.20120914074855.10720: *3* start
    def start (self,p,manual=True):
        
        '''Start a screencast whose root node is p.
        
        Important: p is not necessarily c.p!
        '''
        
        m = self
        self.manual=manual
        m.p1 = p.copy()
        m.p = p.copy()
        m.state_handler()
    #@+node:ekr.20120914074855.10715: *3* state_handler
    def state_handler (self,event=None):

        trace = False and not g.unitTesting
        m = self
        k = m.c.k
        tag = 'screencast'
        state = k.getState(tag)
        char = event and event.char or ''
        if trace: g.trace('state: %s char: %s' % (state,char))
        
        if m.ignore_keys:
            return

        if state == 0:
            m.delete_widgets()
            k.setLabel('screencast') # We might want to lock this label...
            k.setState(tag,1,m.state_handler)
            assert m.p1 and m.p1 == m.p
            m.next()
        elif char == 'Escape': # k.masterKeyHandler handles ctrl-g.
            m.quit()
        elif char == 'Right':
            m.next()
        elif char == 'Left':
            g.trace('screencast-reverse not ready yet.')
        else:
            g.trace('ignore %s' % (char))
            m.quit()
    #@+node:ekr.20120913110135.10587: *3* wait
    def wait(self,n=1,high=0,force=False):
        
        m = self
        
        if m.manual and not force:
            return

        if n > 0 and high > 0:
            n = random.uniform(n,n+high)

        if n > 0:
            n = n * m.speed
            # g.trace(n)
            g.sleep(n)
    #@-others
#@-others
#@-leo
