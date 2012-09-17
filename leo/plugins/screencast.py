#@+leo-ver=5-thin
#@+node:ekr.20120913110135.10579: * @file screencast.py
#@+<< docstring >>
#@+node:ekr.20120913110135.10589: ** << docstring >>
'''Screencast tools for Leo.

Injects c.screencast_controller ivar into all commanders.

To document:
    
- m.p is the "program counter", completely distinct from c.p.

- the arg to m.ctrl_key can be anything that would be a valid key setting.
  So the following are all equivalent: "ctrl-f", "Ctrl-f", "Ctrl+F", etc.
  But "ctrl-F" is different from "ctrl-shift-f".

- 
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

#@+at
# To do:
# - Document this plugin in the docstring and with a screencast.
# - Commands that invoke screencasts.
#@@c

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
        self.quit_flag = False # True if m.quit has been called.
        self.k_state = g.bunch(kind=None,n=None,handler=None) # Saved k.state.
        self.key_w = None # Saved widget for passed-along key handling.
        self.manual = True # True: transition manually between scenes.
        self.n1 = 0.02 # default minimal typing delay.
        self.n2 = 0.175 # default maximum typing delay.
        self.p1 = None # The first slide of the show.
        self.p = None # The present slide of the show.
        self.speed = 1.0 # Amount to multiply wait times.
        self.state_name = 'screencast' # The state name to enable m.state_handler.
        self.node_stack = [] # For m.prev and m.undo.
        self.user_dict = {} # For use by scripts.
        self.widgets = [] # List of (popup) widgets created by this class.
        
        # inject c.screenCastController
        c.screenCastController = self
    #@+node:ekr.20120916193057.10604: *3* Unused
    if 0:
        #@+others
        #@+node:ekr.20120915091327.13817: *4* minibuffer_keys
        def minibuffer_keys (self,s,n1=None,n2=None):
            
            '''Simulate typing in the minibuffer.
            n1 and n2 indicate the range of delays between keystrokes.
            '''
            
            m = self ; c = m.c

            w = m.pane_widget('minibuffer')
            for ch in s:
                m.single_key(ch,n1=n1,n2=n2,w=w)

            c.redraw_now() # Sets focus.
            c.widgetWantsFocusNow(c.frame.miniBufferWidget.widget)
            c.outerUpdate()
        #@+node:ekr.20120916062255.10585: *4* set_minibuffer_prefix
        def set_minibuffer_prefix (self,s1,s2):
            
            '''Set the simulated minibuffer prefix.'''
            
            m = self ; k = m.c.k
            
            k.mb_prompt = s1
            # k.mb_tabList = []
            k.setLabel(s1+s2)
        #@-others
    #@+node:ekr.20120916193057.10605: *3* Entry points
    #@+node:ekr.20120913110135.10580: *4* body_keys
    def body_keys (self,s,n1=None,n2=None):
        
        '''Simulate typing in the body pane.
        n1 and n2 indicate the range of delays between keystrokes.
        '''
        
        m = self ; c = m.c
        if n1 is None: n1 = m.n1
        if n2 is None: n2 = m.n2
        m.key_w = m.pane_widget('body')
        c.bodyWantsFocusNow()
        p = c.p
        w = c.frame.body.bodyCtrl.widget
        c.undoer.setUndoTypingParams(p,'typing',
            oldText=p.b,newText=p.b+s,oldSel=None,newSel=None,oldYview=None)
        for ch in s:
            p.b = p.b + ch
            w.repaint()
            m.wait(n1,n2,force=True)
        c.redraw()
    #@+node:ekr.20120914133947.10578: *4* caption
    def caption (self,pane,s,center=False):
        
        '''Pop up a QPlainTextEdit in the indicated pane.'''
        
        m = self
        parent = m.pane_widget(pane)
        if parent:
            s = s.rstrip()
            if s and s[-1].isalpha(): s = s+'.'
            w = QtGui.QPlainTextEdit(s,parent)
            w.setObjectName('screencastcaption')
            m.widgets.append(w)
            w2 = m.pane_widget(pane)
            geom = w2.geometry()
            w.resize(geom.width(),min(150,geom.height()/2))
            off = QtCore.Qt.ScrollBarAlwaysOff
            w.setHorizontalScrollBarPolicy(off)
            w.setVerticalScrollBarPolicy(off)
            w.show()
            return w
        else:
            g.trace('bad pane: %s' % (pane))
            return None
    #@+node:ekr.20120913110135.10612: *4* clear_log
    def clear_log (self):
        
        '''Clear the log.'''

        m = self
        m.c.frame.log.clearTab('Log')
    #@+node:ekr.20120913110135.10581: *4* command
    def command(self,command_name):
        
        '''Execute the command whose name is given and update the screen immediately.'''

        m = self ; c = m.c

        c.k.simulateCommand(command_name)
            # Named commands handle their own undo!
            # The undo handling in m.next should suffice.

        c.redraw_now()
        m.repaint('all')
    #@+node:ekr.20120915091327.13816: *4* find_screencast & helpers
    def find_screencast(self,p):
        
        '''Find the nearest screencast, prefering previous screencasts
        because that makes it easier to create screencasts.'''
        
        m = self
        return m.find_prev_screencast(p) or m.find_next_screencast(p)
    #@+node:ekr.20120916193057.10608: *5* find_next_screencast
    def find_next_screencast(self,p):

        m = self ; p = p.copy()

        while p:
            if p.h.startswith('@screencast'):
                return p
            else:
                p.moveToThreadNext()
        else:
            return None
        
    #@+node:ekr.20120916193057.10609: *5* find_prev_screencast
    def find_prev_screencast(self,p):
        
        m = self ; p = p.copy()
        
        while p:
            if p.h.startswith('@screencast'):
                return p
            else:
                p.moveToThreadBack()
        else:
            return None
    #@+node:ekr.20120913110135.10582: *4* focus
    def focus(self,pane):
        
        '''Immediately set the focus to the given pane.'''

        m = self ; c = m.c
        d = {
            'body': c.bodyWantsFocus,
            'log':  c.logWantsFocus,
            'tree': c.treeWantsFocus,
        }
        
        f = d.get(pane)
        if f:
            f()
            c.outerUpdate()
            m.repaint(pane)
        else:
            g.trace('bad pane: %s' % (pane))
    #@+node:ekr.20120913110135.10583: *4* head_keys
    def head_keys(self,s,n1=None,n2=None):
        
        '''Simulate typing in the headline.
        n1 and n2 indicate the range of delays between keystrokes.
        '''
        
        m = self ; c = m.c ; p = c.p ; undoType = 'Typing'
        oldHead = p.h ; tree = c.frame.tree
        if n1 is None: n1 = m.n1
        if n2 is None: n2 = m.n2
        p.h=''
        c.editHeadline()
        w = tree.edit_widget(p)
        # Support undo.
        undoData = c.undoer.beforeChangeNodeContents(p,oldHead=oldHead)
        dirtyVnodeList = p.setDirty()
        c.undoer.afterChangeNodeContents(p,undoType,undoData,
            dirtyVnodeList=dirtyVnodeList)
        # Lock out key handling in m.state_handler.
        m.ignore_keys = True
        try:
            m.key_w = w
            for ch in s:
                p.h = p.h + ch
                tree.repaint() # *not* tree.update.
                m.wait(n1,n2,force=True)
                event = m.get_key_event(ch,w)
                c.k.masterKeyHandler(event)
        finally:
            m.ignore_keys = False
        p.h=s
        c.redraw()
    #@+node:ekr.20120913110135.10615: *4* image
    def image(self,pane,fn,center=None,height=None,width=None):
        
        '''Put an image in the indicated pane.'''

        m = self
        parent = m.pane_widget(pane)
        if parent:
            w = QtGui.QLabel('label',parent)
            fn = m.resolve_icon_fn(fn)
            if not fn: return None
            pixmap = QtGui.QPixmap(fn)
            if not pixmap:
                return g.trace('Not a pixmap: %s' % (fn))
            if height:
                pixmap = pixmap.scaledToHeight(height)
            if width:
                pixmap = pixmap.scaledToWidth(width)
            w.setPixmap(pixmap)
            if center:
                g_w=w.geometry()
                g_p=parent.geometry()
                dx = (g_p.width()-g_w.width())/2
                w.move(g_w.x()+dx,g_w.y()+10)
            w.show()
            m.widgets.append(w)
            return w
        else:
            g.trace('bad pane: %s' % (pane))
            return None

        
    #@+node:ekr.20120913110135.10610: *4* log
    def log(self,s,begin=False,end=False,image_fn=None,pane='log'):
        
        '''Put a message to the log pane, highlight it, and pause.'''
        
        m = self

        if not begin:
            m.wait(1)
            
        m.caption(pane,s)
        m.repaint('all')
        
        if not end:
            m.wait(1)
        
        
    #@+node:ekr.20120916062255.10590: *4* plain_keys
    def plain_keys(self,s,n1=None,n2=None,pane='body'):
        
        '''Simulate typing a string of plain keys.'''
        
        m = self

        for ch in s:
            m.single_key(ch,n1=n1,n2=n2,pane=pane)
    #@+node:ekr.20120914074855.10722: *4* quit
    def quit (self):
        
        '''Terminate the slide show.'''
        
        m = self ; c = m.c ; k = c.k
        print('end slide show: %s' % (m.p1.h))
        g.es('end slide show',color='red')
        m.delete_widgets()
        k.keyboardQuit()
        m.clear_state()
        m.quit_flag = True
        c.bodyWantsFocus()
        c.redraw_now()
    #@+node:ekr.20120913110135.10611: *4* set_log_focus & set_speed
    def set_log_focus(self,val):
        
        '''Set m.log_focus to the given value.'''

        m = self
        m.log_focus = bool(val)

    def set_speed (self,speed):
        
        '''Set m.speed to the given value.'''
        
        m = self
        if speed < 0:
            g.trace('speed must be >= 0.0')
        else:
            m.speed = speed
    #@+node:ekr.20120916062255.10593: *4* single_key
    def single_key (self,ch,n1=None,n2=None,pane=None,w=None):
        
        '''Simulate typing a single key, properly saving and restoring m.k_state.'''
        
        trace = True and not g.unitTesting
        m = self ; k = m.c.k
        
        w =  w or m.pane_widget(pane or 'body')
        force = n1 is not None or n2 is not None
        if force and n1 is None: n1 = m.n1
        if force and n2 is None: n2 = m.n2
        try:
            if m.k_state.kind:
                old_state_kind = m.k_state.kind
                k.setState(m.k_state.kind,m.k_state.n,m.k_state.handler)
            else:
                old_state_kind = None
                k.clearState()
            w.repaint() # *not* tree.update.
            m.wait(n1,n2,force=force)
            event = m.get_key_event(ch,w)
            k.masterKeyHandler(event)
        finally:
            # Save k.state in m.k_state.
            if k.state.kind != m.state_name:
                m.set_state(k.state)
            # Important: do *not* re-enable m.state_handler here.
            # This should be done *only* in m.next.
    #@+node:ekr.20120913110135.10587: *4* wait
    def wait(self,n=1,high=0,force=False):
        
        '''Wait for an interval between n and high.
        Do nothing if in manual mode unless force is True.'''
        
        m = self
        
        if m.manual and not force:
            return

        if n > 0 and high > 0:
            n = random.uniform(n,n+high)

        if n > 0:
            n = n * m.speed
            # g.trace(n)
            g.sleep(n)
    #@+node:ekr.20120916193057.10607: *3* State handling
    #@+node:ekr.20120914074855.10721: *4* next
    def next (self):
        
        '''Find the next screencast node and execute its script.
        Call m.quit if no more nodes remain.'''
        
        trace = False and not g.unitTesting
        m = self ; c = m.c ; k = c.k
        m.delete_widgets()
        # Restore k.state from m.k_state.
        if m.k_state.kind and m.k_state.kind != m.state_name:
            k.setState(kind=m.k_state.kind,n=m.k_state.n,handler=m.k_state.handler)
        while m.p:
            if trace: g.trace(m.p.h)
            h = m.p.h.replace('_','').replace('-','')
            if g.match_word(h,0,'@ignore'):
                m.p.moveToThreadNext()
            elif g.match_word(h,0,'@ignoretree'):
                m.p.moveToNodeAfterTree()
            else:
                p2 = m.p.copy()
                m.p.moveToThreadNext()
                if p2.b.strip():
                    if trace: g.trace(p2.h,c.p.v)
                    d = {'c':c,'g:':g,'m':m,'p':p2}
                    tag = 'screencast'
                    m.node_stack.append(p2)
                    undoData = c.undoer.beforeChangeGroup(c.p,tag,verboseUndoGroup=False)
                    c.executeScript(p=p2,namespace=d,useSelectedText=False)
                    c.undoer.afterChangeGroup(c.p,tag,undoData)
                    # Save k.state in m.k_state.
                    if k.state:
                        if k.state.kind == m.state_name:
                            m.clear_state()
                        else:
                            m.set_state(k.state)
                    # Re-enable m.state_handler.
                    if not m.quit_flag:
                        k.setState(m.state_name,1,m.state_handler)
                    if m.p: return
        # No non-empty node found.
        m.quit()
    #@+node:ekr.20120917132841.10609: *4* prev
    def prev (self):
        
        '''Show the previous slide.  This will recreate the slide's widgets,
        but the user may have to adjust the minibuffer or other widgets by hand.'''
        
        trace = False and not g.unitTesting
        m = self
        
        if m.p and m.p == m.p1:
            g.trace('at start: %s' % (m.p and m.p.h))
            m.start(m.p1)
        else:
            p = m.undo()
            if p and p == m.p1:
                if trace: g.trace('at start: %s' % (m.p and m.p.h))
                m.start(m.p1)
            elif p:
                if trace: g.trace('undo, undo, next: %s' % (m.p and m.p.h))
                m.undo()
                m.next()
            else:
                if trace: g.trace('no undo: restart: %s' % (m.p and m.p.h))
                m.start(m.p1)
    #@+node:ekr.20120914074855.10720: *4* start
    def start (self,p,manual=True):
        
        '''Start a screencast whose root node is p.
        
        Important: p is not necessarily c.p!
        '''
        
        m = self ; c = m.c ; k = c.k
        
        assert p
        
        # Reset Leo's state.
        k.keyboardQuit()
        
        # Set ivars
        m.manual=manual
        m.n1 = 0.02 # default minimal typing delay.
        m.n2 = 0.175 # default maximum typing delay.
        m.p1 = p.copy()
        m.p = p.copy()
        m.quit_flag = False
        m.clear_state()

        p.contract()
        c.redraw_now(p)
        m.delete_widgets()
            # Clear widgets left over from previous, unfinished, slideshows.
        m.state_handler()
    #@+node:ekr.20120914074855.10715: *4* state_handler
    def state_handler (self,event=None):
        
        '''Handle keys while in the "screencast" input state.'''

        trace = False and not g.unitTesting
        m = self ; c = m.c ; k = c.k
        state = k.getState(m.state_name)
        char = event and event.char or ''
        if trace:
            g.trace('char: %s k.state.kind: %s m.k_state: %s' % (
                repr(char),repr(k.state.kind),
                m.k_state and repr(m.k_state.kind) or '<none>'))
        if m.ignore_keys:
            return
        if state == 0:
            # Init the minibuffer as in k.fullCommand.
            if trace: g.trace('======= state 0 =====')
            assert m.p1 and m.p1 == m.p
            k.mb_event = event
            k.mb_prefix = k.getLabel()
            k.mb_prompt = 'Screencast: '
            k.mb_tabList = []
            k.setLabel(k.mb_prompt)
            k.setState(m.state_name,1,m.state_handler)
            m.next()
        elif char == 'Escape': # k.masterKeyHandler handles ctrl-g.
            m.quit()
        elif char == 'Right':
            m.next()
        elif char == 'Left':
            m.prev()
        elif m.k_state.kind != m.state_name:
            # We are simulating another state.
            # Pass the character to *that* state,
            # making *sure* to save/restore all state.
            kind,n,handler = k.state.kind,k.state.n,k.state.handler
            m_state_copy = g.bunch(kind=m.k_state.kind,
                n=m.k_state.n,handler=m.k_state.handler)
            m.single_key(char)
            k.setState(kind,n,handler)
            m.set_state(m_state_copy)
        elif trace:
            g.trace('ignore %s' % (repr(char)))
    #@+node:ekr.20120914195404.11208: *4* undo
    def undo (self):
        
        '''Undo the previous screencast scene.'''

        m = self
        
        m.delete_widgets()
        
        if m.node_stack:
            c = m.c
            m.p = m.node_stack.pop()
            c.undoer.undo()
            c.redraw()
            return m.p
        else:
            return None
    #@+node:ekr.20120916062255.10596: *4* set_state & clear_state
    def set_state (self,state):
        
        m = self
        
        # g.trace('**** setting m.k_state: %s' % (state.kind))
        m.k_state.kind = state.kind
        m.k_state.n = state.n
        m.k_state.handler = state.handler
        
    def clear_state (self):
        
        m = self
        
        # g.trace('**** clearing m.k_state')
        m.k_state.kind = None
        m.k_state.n = None
        m.k_state.handler = None
    #@+node:ekr.20120916193057.10606: *3* Utilities
    #@+node:ekr.20120916062255.10589: *4* get_key_event
    def get_key_event (self,ch,w):
        
        m = self ; c = m.c ; k = c.k
        
        m.key_w = w
        
        if len(ch) > 1:
            key = None
            stroke = k.strokeFromSetting(ch).s
        else:
            stroke = key = ch
            
        # g.trace(ch,key,stroke)
        
        return leoGui.leoKeyEvent(c,key,stroke,w=w,
            x=0,y=0,x_root=0,y_root=0) # These are required.
    #@+node:ekr.20120914163440.10581: *4* delete_widgets
    def delete_widgets (self):
        
        m = self

        for w in m.widgets:
            w.deleteLater()

        m.widgets=[]
    #@+node:ekr.20120914133947.10579: *4* pane_widget
    def pane_widget (self,pane):
        
        '''Return the pane's widget.'''
        
        m = self ; c = m.c

        d = {
            'all':  c.frame.top,
            'body': c.frame.body.bodyCtrl.widget,
            'log':  c.frame.log.logCtrl.widget,
            'minibuffer': c.frame.miniBufferWidget.widget,
            'tree': c.frame.tree.treeWidget,
        }

        return d.get(pane)
    #@+node:ekr.20120913110135.10585: *4* repaint
    def repaint(self,pane):
        
        '''Repaint the given pane.'''

        m = self
        w = m.pane_widget(pane)
        if w:
            w.repaint()
        else:
            g.trace('bad pane: %s' % (pane))
    #@+node:ekr.20120914163440.10582: *4* resolve_icon_fn
    def resolve_icon_fn (self,fn):
        
        '''Resolve fn relative to the Icons directory.'''
        
        m = self

        dir_ = g.os_path_finalize_join(g.app.loadDir,'..','Icons')
        path = g.os_path_finalize_join(dir_,fn)
        
        if g.os_path_exists(path):
            return path
        else:
            g.trace('does not exist: %s' % (path))
            return None
    #@-others
#@-others
#@-leo
