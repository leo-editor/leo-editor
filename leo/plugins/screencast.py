#@+leo-ver=5-thin
#@+node:ekr.20120913110135.10579: * @file screencast.py
#@+<< docstring >>
#@+node:ekr.20120913110135.10589: ** << docstring >>
'''

#####################
The screencast plugin
#####################

Executive Summary
-----------------

- Within \@screencast trees, the body text of nodes contain scripts. As
  usual, nodes without body text are organizer nodes.
  
- The 'm' variable in these scripts is a ScreenCastController (SCC).

- The SCC handles keystrokes, executes the script in each node, and
  provides convenience methods to show key handling, captions and (scaled)
  graphics.
  
- When the human presenter types <Right Arrow>, the SCC executes the script
  in the next node (in outline order), ignoring \@ignore-node nodes and
  \@ignore-tree trees.
  
- Each slide's appearance is just the appearance of the Leo window after
  the SCC executes the node's script. However, the SCC shows the body
  text of each \@text node as it is, rather than treating it as a script.

- A screencast is the sequence of slides shown by the SCC. Within a
  screencast, the SCC manages keystrokes flexibly so that both scripts and
  the human presenter can demonstrate Leo's minibuffer-based commands as
  each slide is shown.


Overview
--------

This plugin provides tools for showing **screencasts**, a series of
**slides** controlled by a human presenter. Nodes represent slides. With a
few exceptions discussed below, each screencast node contains a script. The
**appearance** of a slide is simply the appearance of Leo's main window
after this plugin executes the node's script.

**Important**: screencast scripts typically consist of just a few simple
calls to convenience methods provided by this plugin. In essence, each
node's script is the *same as* writer's script. There is no need for a
separate script that gets laboriously translated to a screencast script.

**Important**: it's much harder to explain this plugin than to use it!
Before reading further, please look at the example @screencast trees in
test.leo to see what slides nodes typically contain and to see what
the screencasts actually do as a result.

Screencast nodes
----------------

**@screencast nodes** are nodes whose headline start with \@screencast.
Generally speaking, **@slide nodes** are all the descendants of a
particular \@screencast node that have non-empty body text.  Exceptions:

- **Organizer nodes** are nodes with empty body text.  Such nodes serve
  only to organize slide nodes.
  
- **Ignored nodes** are nodes whose headline start with \@ignore-node or
  \@ignore-tree. This plugin ignores \@ignore-node and \@ignore-tree nodes,
  and ignores all nodes contained in \@ignore-tree** trees.
  
Thus, a slide node is any descendant of an \@screencast node that

a) contains body text and

b) is neither an \@ignore-node node nor an \@gnore-tree node nor any
   descendant of an \@ignore-tree node.
   
**Note**: \@ignore is a synonym for \@ignore-tree.

There are two special kinds of slide nodes. Nodes whose headlines start
with **@text** and **@rst** are also considered to be slide nodes, but the
body text of such nodes do *not* contain scripts. Instead, the plugin shows
the body text of \@text nodes as is, and shows the body text of \@rst nodes
rendered as reStructuredText.

Commands and keys
-----------------

The screencast-start command starts a screencast. This command executes the
script in the first slide node of the tree and then pauses. Thereafter, the
Right Arrow key executes the script in the next slide node (in outline order).
The Left Arrow key executes the script in the previous slide node. The Escape
or Ctrl-G keys terminate any screencast.

**Important**: as discussed below, screencasts can activate the minibuffer
or execute commands such as the Find command *while showing a screencast*.
In other words, the presenter can move from slide to slide while the Find
command is prompting for input! This requires some behind-the-scenes magic,
but allows screencast to demo any of Leo's commands "for real".

Screencast scripts
------------------

Except for \@text and \@rst nodes, each non-empty, non-ignored screencast
node must contain a **screencast script**. When the presenter moves to a
new screenshot node, the screenshot plugin excutes the script in the node.
Screencast scripts are simply Leo scripts that alter the appearance of the
Leo main window, and thus the appearance of a slide. Scripts have access to
the 'c', 'g' and 'p' vars as usual. Scripts also have access to the 'm'
variable, representing the screencast controller for Leo outline. Scripts
typically use 'm' to access convenience methods, but advanced scripts can
use 'm' in other ways.

The ScreenCastController
------------------------

The ScreenCastController (SCC) controls key handling during screencasts and
executes screencast scripts as the screencast moves from node to node. As a
result, screencasts scripts are usually *very* simple: each script
typically consists of just a few lines of code, and each line typically
just calls a single scc convenience methods.

SCC convenience methods
-----------------------

**m.body(s)**, **m.log(s) and **m.tree(s)** create caption with text s in
the indicated pane. A **caption** is a text area that overlays part of
Leo's screen. By default, captions have a distinctive yellow background.
The appearance of captions can be changed using Qt stylesheets.  See below.

**m.body_keys(s,n1=None,n2=None)**

**m.head_keys(s,n1=None,n2=None)**

**m.plain_keys(s,n1=None,n2=None,pane='body')**

**m.redraw(p)**

**m.single_key(setting)** generates a key event. Examples::
    
   m.single_key('Alt-X') # Activates the minibuffer
   m.single_key('Ctrl-F') # Activates Leo's Find command
   
**Important**: the SCC allows key handling in key-states *during*
the execution of a screencast.  For example::
    
    m.single_key('Alt-X')
    m.plain_keys('ins\tno\t\n')
    
actually executes the insert-node command!

**Note**: the 'setting' arg can be anything that would be a valid key
setting. The following are equivalent: "ctrl-f", "Ctrl-f", "Ctrl+F", etc.,
but "ctrl-F" is different from "ctrl-shift-f".

**m.quit** ends the screencast. By definition, the last slide of screencast
is the first non-ignored screencast node that calls m.quit.

Node order vs. selection order
-------------------------------

Screencast nodes are usually invisible.
    
- m.p is the "program counter", completely distinct from c.p.

- the arg to m.ctrl_key can be anything that would be a valid key setting.
  So the following are all equivalent: "ctrl-f", "Ctrl-f", "Ctrl+F", etc.
  But "ctrl-F" is different from "ctrl-shift-f".
  
Stylesheets
-----------


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
        c.screencast_controller = ScreenCastController(c)
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
        self.n1 = 0.02 # default minimal typing delay.
        self.n2 = 0.175 # default maximum typing delay.
        self.p1 = None # The first slide of the show.
        self.p = None # The present slide of the show.
        self.speed = 1.0 # Amount to multiply wait times.
        self.state_name = 'screencast' # The state name to enable m.state_handler.
        self.node_stack = [] # For m.prev and m.undo.
        self.text_flag = False # True: m.next shows body text instead of executing it.
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
        if n1 is None: n1 = 0.02
        if n2 is None: n2 = 0.095
        
        m.key_w = m.pane_widget('body')
        c.bodyWantsFocusNow()
        p = c.p
        w = c.frame.body.bodyCtrl.widget
        c.undoer.setUndoTypingParams(p,'typing',
            oldText=p.b,newText=p.b+s,oldSel=None,newSel=None,oldYview=None)
        for ch in s:
            p.b = p.b + ch
            w.repaint()
            m.wait(n1,n2)
        c.redraw()
    #@+node:ekr.20120914133947.10578: *4* caption and abbreviations: body, log, tree
    def caption (self,s,pane): # To do: center option.
        
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

    def body (self,s):
        return self.caption(s,'body')
        
    def log (self,s):
        return self.caption(s,'log')
        
    def tree (self,s):
        return self.caption(s,'tree')
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
        if n1 is None: n1 = 0.02
        if n2 is None: n2 = 0.095
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
                m.wait(n1,n2)
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

        
    #@+node:ekr.20120913110135.10610: *4* old_log
    def old_log(self,s,begin=False,end=False,image_fn=None,pane='log'):
        
        '''Put a message to the log pane, highlight it, and pause.'''
        
        m = self

        if not begin:
            m.wait(1)
            
        m.caption(pane,s)
        m.repaint('all')
        
        if not end:
            m.wait(1)
    #@+node:ekr.20120921064434.10605: *4* open_menu
    def open_menu (self,menu_name):
        
        '''Activate the indicated *top-level* menu.'''
        
        m = self
        
        m.c.frame.menu.activateMenu(menu_name)
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
        
        if m.quit_flag:
            return
        if not m.p1:
            return
        
        print('end slide show: %s' % (m.p1.h))
        g.es('end slide show',color='red')
        m.delete_widgets()
        k.keyboardQuit()
        m.clear_state()
        m.quit_flag = True
        c.bodyWantsFocus()
    #@+node:ekr.20120918103526.10594: *4* redraw
    def redraw(self,p=None):
        
        m = self
        m.c.redraw_now(p)
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
    #@+node:ekr.20120918103526.10595: *4* show_text
    def show_child_text (self):
        
        m = self ; c = m.c
        
        c.redraw(m.p.threadBack().firstChild())
    #@+node:ekr.20120916062255.10593: *4* single_key
    def single_key (self,ch,n1=None,n2=None,pane=None,w=None):
        
        '''Simulate typing a single key, properly saving and restoring m.k_state.'''
        
        trace = True and not g.unitTesting
        m = self ; k = m.c.k
        
        w =  w or m.pane_widget(pane or 'body')
        force = n1 is not None or n2 is not None
        if force and n1 is None: n1 = 0.02
        if force and n2 is None: n2 = 0.095

        try:
            if m.k_state.kind:
                old_state_kind = m.k_state.kind
                k.setState(m.k_state.kind,m.k_state.n,m.k_state.handler)
            else:
                old_state_kind = None
                k.clearState()
            w.repaint() # *not* tree.update.
            m.wait(n1,n2)
            event = m.get_key_event(ch,w)
            k.masterKeyHandler(event)
        finally:
            # Save k.state in m.k_state.
            if k.state.kind != m.state_name:
                m.set_state(k.state)
            # Important: do *not* re-enable m.state_handler here.
            # This should be done *only* in m.next.
    #@+node:ekr.20120913110135.10587: *4* wait
    def wait(self,n1=1,n2=0):
        
        '''Wait for an interval between n1 and n2.'''
        
        m = self
        
        if n1 is None: n1 = 0
        if n2 is None: n2 = 0

        if n1 > 0 and n2 > 0:
            n = random.uniform(n1,n2)
        else:
            n = n1

        if n > 0:
            n = n * m.speed
            # g.trace(n)
            g.sleep(n)
    #@+node:ekr.20120916193057.10607: *3* State handling
    #@+node:ekr.20120914074855.10721: *4* next & helper
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
            if g.match_word(h,0,'@ignorenode'):
                m.p.moveToThreadNext()
            elif g.match_word(h,0,'@ignoretree') or g.match_word(h,0,'@ignore'):
                m.p.moveToNodeAfterTree()
            elif m.p.b.strip():
                p_next = m.p.threadNext()
                p_old = m.p.copy()
                if g.match_word(m.p.h,0,'@text'):
                    c.redraw(m.p) # Selects the node, thereby showing the body text.
                else:
                    m.exec_node(m.p)
                # Save k.state in m.k_state.
                if k.state:
                    if k.state.kind == m.state_name:
                        m.clear_state()
                    else:
                        m.set_state(k.state)
                # Re-enable m.state_handler.
                if not m.quit_flag:
                    k.setState(m.state_name,1,m.state_handler)
                # Change m.p only if the script has not already changed it.
                if not m.p or m.p == p_old:
                    m.p = p_next
                break
            else:
                m.p.moveToThreadNext()
        else:
            # No non-empty node found.
            m.quit()
    #@+node:ekr.20120918103526.10596: *5* exec_node
    def exec_node (self,p):
        
        '''Execute the script in node p.'''
        
        trace = False and not g.unitTesting
        m = self ; c = m.c
        if trace: g.trace(p.h,c.p.v)
        assert p.b
        d = {'c':c,'g:':g,'m':m,'p':p}
        tag = 'screencast'
        m.node_stack.append(p)
        undoData = c.undoer.beforeChangeGroup(c.p,tag,verboseUndoGroup=False)
        c.executeScript(p=p,namespace=d,useSelectedText=False)
        c.undoer.afterChangeGroup(c.p,tag,undoData)
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
    def start (self,p):
        
        '''Start a screencast whose root node is p.
        
        Important: p is not necessarily c.p!
        '''
        
        m = self ; c = m.c ; k = c.k
        
        assert p
        
        # Reset Leo's state.
        k.keyboardQuit()
        
        # Set ivars
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
