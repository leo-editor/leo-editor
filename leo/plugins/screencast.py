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

import PyQt4.QtCore as QtCore
import PyQt4.QtGui as QtGui
#@-<< imports >>

# To do:
# Put images in log.

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
        self.p1 = None # The first slide of the show.
        self.p = None # The present slide of the show.
        self.speed = 1.0 # Amount to multiply wait times.
    #@+node:ekr.20120913110135.10580: *3* body_keys
    def body_keys (self,s,n1=0,n2=0):
        
        c = self.c
        c.bodyWantsFocusNow()
        p = c.p
        w = c.frame.body.bodyCtrl.widget
        for ch in s:
            p.b = p.b + ch
            w.repaint()
            self.wait(n1,n2)
        c.redraw()
    #@+node:ekr.20120913110135.10612: *3* clear_log
    def clear_log (self):
        
        '''Clear the log.'''

        self.c.frame.log.clearTab('Log')
    #@+node:ekr.20120913110135.10581: *3* command
    def command(self,command_name):
        
        c = self.c
        c.k.simulateCommand(command_name)
        c.redraw()
        self.repaint('all')
    #@+node:ekr.20120913110135.10615: *3* dialog (not ready yet)
    def dialog(self,s,image_fn):
        
        pass
    #@+node:ekr.20120913110135.10582: *3* focus
    def focus(self,pane):

        c = self.c
        d = {
            'body': c.bodyWantsFocus,
            'log': c.logWantsFocus,
            'tree': c.treeWantsFocus,
        }
        
        f = d.get(pane)
        if f:
            f()
            c.outerUpdate()
            self.repaint(pane)
        else:
            g.trace('bad pane: %s' % (pane))
    #@+node:ekr.20120913110135.10583: *3* head_keys
    def head_keys(self,s,n1=0,n2=0):
        
        c = self.c
        p = c.p
        p.h=''
        tree = c.frame.tree
        c.editHeadline()
        w = tree.edit_widget(p)
        for ch in s:
            p.h = p.h + ch
            tree.repaint() # *not* tree.update.
            self.wait(n1,n2)
            event = leoGui.leoKeyEvent(c,ch,ch,w,x=0,y=0,x_root=0,y_root=0)
            c.k.masterKeyHandler(event)
        # Ensure the final result is correct.
        # tree.repaint()
        p.h=s
        c.redraw()
    #@+node:ekr.20120913110135.10584: *3* key
    def key(self,setting,command):
        '''Simulate hitting the key.  Show the key in the log pane.'''

        c = self.c
        stroke = c.k.strokeFromSetting(setting)
        # g.es(stroke.s)
        c.k.simulateCommand(command)
        c.redraw()
        self.repaint('all')
    #@+node:ekr.20120913110135.10610: *3* log
    def log(self,s,begin=False,end=False,image_fn=None):
        
        '''Put a message to the log pane, highlight it, and pause.'''
        
        m = self
        if not begin:
            m.wait(1)
        g.es(s,color=m.log_color)
        
        # Images do not appear to work.  We could use dialogs for that...
        if False and image_fn:
            w = self.c.frame.log.logCtrl.widget # A subclass of QTextBrowser.
            kind = QtGui.QTextDocument.ImageResource
            # image = QtGui.QImage(image_fn)
            # image = QtGui.QPixmap(image_fn)
            # g.trace(image_fn)
            w.loadResource(kind,image_fn)
        if self.log_focus:
            m.focus('log')
        m.repaint('all')
        if not end:
            m.wait(1)
        
        
    #@+node:ekr.20120914074855.10721: *3* next
    def next (self):
        
        '''Find the next non-empty screencast node and execute its script.'''
        
        m = self
        
        while m.p:
            g.trace(m.p.h)
            p2 = m.p.copy()
            m.p.moveToThreadNext()
            if p2.b.strip(): # Probably should test after stripping comments...
                g.trace('executing',p2.h)
                d = {'c':m.c,'g:':g,'m':m,'p':p2}
                m.c.executeScript(p=p2,namespace=d,useSelectedText=False)
                    # event=None, args=None, p=None,
                    # script=None, define_g=True,
                    # define_name='__main__', silent=False
                break
        else:
            m.quit()
    #@+node:ekr.20120914074855.10722: *3* quit
    def quit (self):
        
        '''Terminate the slide show.'''
        
        m = self
        g.trace('end of slide show at: %s' % (m.p1.h))
        m.c.k.keyboardQuit()
    #@+node:ekr.20120913110135.10585: *3* repaint
    def repaint(self,pane):

        c = self.c
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
    #@+node:ekr.20120913110135.10611: *3* set_log_focus & set_speed
    def set_log_focus(self,val):

        self.log_focus = bool(val)

    def set_speed (self,speed):
        
        if speed < 0:
            g.trace('speed must be >= 0.0')
        else:
            self.speed = speed
    #@+node:ekr.20120914074855.10720: *3* start
    def start (self,p):
        
        self.p1 = p.copy()
        self.p = p.copy()
        self.state_handler(event=None)
    #@+node:ekr.20120914074855.10715: *3* state_handler
    def state_handler (self,event):

        trace = False and not g.unitTesting
        m = self
        k = m.c.k
        tag = 'screencast'
        state = k.getState(tag)
        char = event and event.char or ''
        if trace: g.trace('state: %s char: %s' % (state,char))

        if state == 0:
            k.setLabel('screencast') # We might want to lock this label...
            k.setState(tag,1,self.state_handler)
            assert m.p1 and m.p1 == m.p
            m.next()
        elif char == 'Escape': # k.masterKeyHandler handles ctrl-g.
            g.trace('end of slide show')
            k.keyboardQuit()
        elif char == 'Right':
            m.next()
        elif char == 'Left':
            g.trace('screencast-reverse not ready yet.')
        else:
            g.trace('ignore %s' % (char))
            # k.clearState()
            # k.resetLabel()
            # k.showStateAndMode()
    #@+node:ekr.20120913110135.10587: *3* wait
    def wait(self,n=1,high=0):
        
        m = self

        if n > 0 and high > 0:
            n = random.uniform(n,n+high)
        if n > 0:
            g.sleep(n * self.speed)
    #@-others
#@-others
#@-leo
