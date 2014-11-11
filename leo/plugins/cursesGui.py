#@+leo-ver=5-thin
#@+node:ekr.20141110215426.72: * @file cursesGui.py
'''A minimal text-oriented gui.'''

#@+at
# Things not found in the GUI 'interface' classes (in leoFrame.py, leoGui.py, etc)
# are labeled: # undoc: where the AttributeError comes from other implementations
# of method.
#@@c

#@+<< imports >>
#@+node:ekr.20141110215426.73: ** << imports >>
import leo.core.leoGlobals as g
import leo.core.leoChapters as leoChapters
import leo.core.leoGui as leoGui
import leo.core.leoKeys as leoKeys
import leo.core.leoFrame as leoFrame
import leo.core.leoMenu as leoMenu
import leo.core.leoNodes as leoNodes

import os
#@-<< imports >>
#@+<< TODO >>
#@+node:ekr.20141110215426.74: ** << TODO >>
#@@nocolor-node
#@+at
# Body text:
# Is the "signature" of the typing event right?
# What does the InsertPoint do when text is inserted and deleted?
# What does the SelectionRange do, period?
# What about mouse input? What does createBindings() do?
# What does set_focus() do?
# What does the GUI need to do for Leo's undo features?
# What about that minibuffer thing? (I've never used it.)
# When should runMainLoop return?
# What kind of newlines does the body text control get? How should it treat them?
# Headline editing?
# Body text selection.
# (Strip trailing whitespace from this file. :P)
# < < Random cruft >>
# Pay attention to being direct and code-terse.
# Not at all user-friendly.
# Comments in the body reflect current status only.
# Ideally, comments in the body go away as the "leoGUI interface" improves.
# Written on a hundred-column terminal. :S
#@-<< TODO >>
get_input = input if g.isPython3 else raw_input

#@+others
#@+node:ekr.20141110215426.76: ** init
def init ():

    ok = not g.app.gui and not g.app.unitTesting # Not Ok for unit testing!
    if ok:
        g.app.gui = textGui()
        g.app.root = g.app.gui.createRootWindow()
        g.app.gui.finishCreate()
        g.plugin_signon(__name__)
    elif g.app.gui and not g.app.unitTesting:
        s = "Can't install text gui: previous gui installed"
        g.es_print(s,color="red")
    return ok
#@+node:ekr.20141110215426.77: ** underline
def underline(s, idx):

    if idx < 0 or idx > len(s) - 1:
        return s

    return s[:idx] + '&' + s[idx:]
#@+node:ekr.20141110215426.78: ** class textGui
class textGui(leoGui.LeoGui):
    #@+others
    #@+node:ekr.20141110215426.79: *3* __init__
    def __init__(self):
        
        leoGui.LeoGui.__init__(self, "text")
        self.frames = []
        self.killed = False
        # TODO leoTkinterFrame finishCreate g.app.windowList.append(f) - use that?
    #@+node:ekr.20141110215426.80: *3* createKeyHandlerClass
    def createKeyHandlerClass (self,c):

        # import leo.core.leoKeys as leoKeys
            # Do this here to break a circular dependency.
        return leoKeys.KeyHandlerClass(c)

    #@+node:ekr.20141110215426.81: *3* createLeoFrame
    def createLeoFrame(self,c,title):

        ret = textFrame(self, title)
        self.frames.append(ret)
        return ret
    #@+node:ekr.20141110215426.82: *3* createRootWindow
    def createRootWindow(self):
        pass # N/A
    #@+node:ekr.20141110215426.83: *3* destroySelf
    def destroySelf (self):
        self.killed = True
    #@+node:ekr.20141110215426.84: *3* finishCreate
    def finishCreate(self):
        pass
    #@+node:ekr.20141110215426.85: *3* isTextWidget
    def isTextWidget (self,w):
        '''Return True if w is a Text widget suitable for text-oriented commands.'''
        return w and isinstance(w,leoFrame.StringTextWrapper)
    #@+node:ekr.20141110215426.86: *3* oops
    def oops(self):
        g.pr("textGui oops", g.callers(), "should be implemented")
    #@+node:ekr.20141110215426.87: *3* runMainLoop
    def runMainLoop(self):
        self.text_run()
    #@+node:ekr.20141110215426.88: *3* runOpenFileDialog
    def runOpenFileDialog(self,title,filetypes,defaultextension,multiple=False,startpath=None):

        initialdir = g.app.globalOpenDir or g.os_path_abspath(os.getcwd())
        ret = get_input("Open which %s file (from %s?) > " % (repr(filetypes), initialdir))
        if multiple:
            return [ret,]
        return ret
    #@+node:ekr.20141110215426.89: *3* get/set_focus
    def get_focus(self,c):
        pass

    def set_focus(self,c,w):
        pass
    #@+node:ekr.20141110215426.90: *3* text_run & helper
    def text_run(self):
        
        frame_idx = 0
        get_input = input if g.isPython3 else raw_input
        while not self.killed:

            # Frames can come and go.
            if frame_idx > len(self.frames) - 1:
                frame_idx = 0
            f = self.frames[frame_idx]
            g.pr(f.getTitle())
            s = get_input('Do what? (menu,key,body,frames,tree,quit) > ')
            try:
                self.doChoice(f,s)
            except Exception:
                g.es_exception()
    #@+node:ekr.20141110215426.91: *4* doChoice
    def doChoice(self,f,s):

        if s in ('m','menu'):
            f.menu.show_menu()
        elif s in ('k','key'):
            f.text_key()
        elif s in ('b','body'):
            f.body.text_show()
        elif s in ('f','frames'):
            for i, f in enumerate(self.frames):
                g.pr(i, ')', f.getTitle())
            s = get_input('Operate on which frame? > ')
            try:
                s = int(s)
            except ValueError:
                s = -1
            if s >= 0 and s <= len(self.frames) - 1:
                frame_idx = s
        elif s in ('t','tree'):
            f.tree.text_draw_tree()
        elif s in ('q','quit'):
            self.killed = True
    #@+node:ekr.20141110215426.92: *3* widget_name
    def widget_name(self, w):
        if isinstance(w, textBodyCtrl):
            return 'body'
        return leoGui.LeoGui.widget_name(self, w)
    #@-others
#@+node:ekr.20141110215426.93: ** class textFrame
class textFrame(leoFrame.LeoFrame):
    #@+others
    #@+node:ekr.20141110215426.94: *3* __init__
    def __init__(self, gui, title):

        leoFrame.LeoFrame.__init__(self, gui)
        self.title = title # Per leoFrame.__init__
    #@+node:ekr.20141110215426.95: *3* createFirstTreeNode
    # From leoTkinterFrame.py
    def createFirstTreeNode (self):

        f = self ; c = f.c

        v = leoNodes.vnode(context=c)
        p = leoNodes.position(v)
        v.initHeadString("NewHeadline")
        # New in Leo 4.5: p.moveToRoot would be wrong: the node hasn't been linked yet.
        p._linkAsRoot(oldRoot=None)
        # c.setRootPosition(p) # New in 4.4.2.
        c.editPosition(p)
    #@+node:ekr.20141110215426.96: *3* deiconify
    def deiconify(self): pass # N/A
    def lift(self): pass # N/A
    #@+node:ekr.20141110215426.97: *3* destroySelf
    def destroySelf (self):
        pass
    #@+node:ekr.20141110215426.98: *3* finishCreate
    def finishCreate(self, c):

        f = self ; f.c = c
        f.tree = textTree(self)
        f.body = textBody(frame=self, parentFrame=None)        
        f.log = textLog(frame=self, parentFrame=None)
        f.menu = textLeoMenu(self)
        if f.body.use_chapters:
            c.chapterController = leoChapters.ChapterController(c)
        f.createFirstTreeNode()
        c.initVersion()
        # (*after* setting self.log)
        c.setLog() # writeWaitingLog hangs without this(!)
        # So updateRecentFiles will update our menus.
        g.app.windowList.append(f)
    #@+node:ekr.20141110215426.99: *3* setInitialWindowGeometry
    def setInitialWindowGeometry(self): pass # N/A
    #@+node:ekr.20141110215426.100: *3* setMinibufferBindings
    def setMinibufferBindings(self):
        pass

    def setTopGeometry (self,w,h,x,y,adjustSize=True):
        pass # N/A
    #@+node:ekr.20141110215426.101: *3* text_key
    def text_key(self):
        c = self.c ; k = c.k ; w = self.body.bodyCtrl

        if g.isPython3: get_input = input
        else:                     get_input = raw_input

        key = get_input('Keystroke > ')
        if not key: return

        class leoTypingEvent:
            def __init__ (self,c,w,char,keysym):
                self.c = c
                self.char = char
                self.keysym = keysym
                self.leoWidget = w
                self.widget = w

        # Leo uses widget_name(event.widget) to decide if a 'default' keystroke belongs
        # to typing in the body text, in the tree control, or whereever. 

        # Canonicalize the setting.
        char = key
        stroke = c.k.shortcutFromSetting(char)
        g.trace('char',repr(char),'stroke',repr(stroke))

        e = leoTypingEvent(c,w,char,stroke)
        k.masterKeyHandler(event=e) ## ,stroke=key)
    #@+node:ekr.20141110215426.102: *3* update
    def update(self): pass
    def resizePanesToRatio(self, ratio, ratio2): pass # N/A
    #@-others
#@+node:ekr.20141110215426.103: ** class textBody
class textBody(leoFrame.LeoBody):
    #@+others
    #@+node:ekr.20141110215426.104: *3* __init__
    def __init__(self, frame, parentFrame):
        
        leoFrame.LeoBody.__init__(self, frame, parentFrame)
        c = frame.c
        name = 'body'
        self.bodyCtrl = textBodyCtrl(c,name)
        self.colorizer = leoFrame.NullColorizer(self.c)
    #@+node:ekr.20141110215426.105: *3* bind
    # undoc: newLeoCommanderAndFrame -> c.finishCreate -> k.finishCreate -> k.completeAllBindings -> k.makeMasterGuiBinding -> 2156 w.bind ; nullBody 
    def bind(self, bindStroke, callback): 
        # Quiet, please.        
        ##self.oops()
        pass
    #@+node:ekr.20141110215426.106: *3* setEditorColors
    # TODO Tkinter onBodyChanged undo call and many others. =(

    def setEditorColors(self, bg, fg): pass # N/A
    def createBindings(self, w=None): pass
    #@+node:ekr.20141110215426.107: *3* text_show
    def text_show(self):

        w = self.bodyCtrl
        g.pr('--- body ---')
        g.pr('ins',w.ins,'sel',w.sel)
        g.pr(w.s)
    #@-others
#@+node:ekr.20141110215426.108: ** class textBodyCtrl (stringTextWrapper)
class textBodyCtrl (leoFrame.StringTextWrapper):
    pass
#@+node:ekr.20141110215426.109: ** class textMenuCascade
class textMenuCascade:
    #@+others
    #@+node:ekr.20141110215426.110: *3* __init__
    def __init__(self, menu, label, underline):
        self.menu = menu
        self.label = label
        self.underline = underline
    #@+node:ekr.20141110215426.111: *3* display
    def display(self):            
        ret = underline(self.label, self.underline)
        if len(self.menu.entries) == 0:
            ret += ' [Submenu with no entries]'
        return ret
    #@-others
#@+node:ekr.20141110215426.112: ** class textMenuEntry
class textMenuEntry:
    #@+others
    #@+node:ekr.20141110215426.113: *3* __init__
    def __init__(self, label, underline, accel, callback):
        self.label = label
        self.underline = underline
        self.accel = accel
        self.callback = callback
    #@+node:ekr.20141110215426.114: *3* display
    def display(self):
        return "%s %s" % (underline(self.label, self.underline), self.accel,)
    #@-others
#@+node:ekr.20141110215426.115: ** class textMenuSep
class textMenuSep:    
    #@+others
    #@+node:ekr.20141110215426.116: *3* display
    def display(self): 
        return '-' * 5
    #@-others
#@+node:ekr.20141110215426.117: ** class textLeoMenu (LeoMenu)
class textLeoMenu(leoMenu.LeoMenu):

    #@+others
    #@+node:ekr.20141110215426.118: *3* ctor (textLeoMenu)
    def __init__ (self,frame):

        self.entries = []
        self.c = frame.c
        # Init the base class
        leoMenu.LeoMenu.__init__(self,frame)
    #@+node:ekr.20141110215426.119: *3* createMenuBar
    def createMenuBar(self, frame):

        g.trace(frame.c)

        self._top_menu = textLeoMenu(frame)

        self.createMenusFromTables()
    #@+node:ekr.20141110215426.120: *3* new_menu
    def new_menu(self,parent,tearoff=0,label=''):

        if tearoff != False:
            raise NotImplementedError(repr(tearoff))
        # I don't know what the 'parent' argument is for; neither does the wx GUI.
        ### return textMenu()
        menu = textLeoMenu(parent or self.frame)
        menu.entries = []
        return menu
    #@+node:ekr.20141110215426.121: *3* add_cascade
    def add_cascade(self, parent, label, menu, underline):

        if parent == None:
            parent = self._top_menu
        parent.entries.append(textMenuCascade(menu, label, underline,))
    #@+node:ekr.20141110215426.122: *3* add_command
    ### def add_command(self, menu, label, underline, command, accelerator=''):

    def add_command(self,**keys):
        # ?
        # underline - Offset into label. For those who memorised Alt, F, X rather than Alt+F4.
        # accelerator - For display only; these are implemented by Leo's key handling.

        menu = self

        # g.trace(keys)

        def doNothingCallback():
            pass

        label = keys.get('label') or 'no label'
        underline = keys.get('underline') or 0
        accelerator = keys.get('accelerator') or ''
        command = keys.get('command') or doNothingCallback


        entry = textMenuEntry(label, underline, accelerator, command)
        menu.entries.append(entry)
    #@+node:ekr.20141110215426.123: *3* add_separator
    def add_separator(self, menu):
        menu.entries.append(textMenuSep())
    #@+node:ekr.20141110215426.124: *3* delete_range
    def delete_range (self,*args,**keys):

        pass
    #@+node:ekr.20141110215426.125: *3* show_menu
    def show_menu(self):
        last_menu = self._top_menu

        while True:
            entries = last_menu.entries

            for i, entry in enumerate(entries):
                g.pr(i, ')', entry.display())
            g.pr(len(last_menu.entries), ')', '[Prev]')

            which = get_input('Which menu entry? > ')
            which = which.strip()            
            if not which: continue

            try:
                n = int(which)
            except ValueError:
                # Look for accelerator character.
                ch = which[0].lower()
                for n,z in enumerate(entries):
                    if hasattr(z,'underline') and ch == z.label[z.underline].lower():
                        break
                else: continue

            if n == len(entries):
                return
            if n < 0 or n > len(entries) - 1:
                continue

            menu = entries[n]
            if isinstance(menu, textMenuEntry):
                menu.callback()
                return
            if isinstance(menu, textMenuCascade):
                last_menu = menu.menu
            else:                
                pass
    #@-others
#@+node:ekr.20141110215426.126: ** class textLog
class textLog(leoFrame.LeoLog):

	# undoc: leoKeys.py makeAllBindings c.frame.log.setTabBindings('Log') ; nullLog 
    #@+others
    #@+node:ekr.20141110215426.127: *3* setTabBindings
    def setTabBindings(self, tabName):
        pass    
    #@+node:ekr.20141110215426.128: *3* put
    def put (self,s,color=None,tabName='Log',from_redirect=False):
        g.pr(s,newline=False)
    #@+node:ekr.20141110215426.129: *3* putnl
    def putnl(self, tabName='log'):
        g.pr('')
    #@+node:ekr.20141110215426.130: *3* createControl
    # < < HACK Quiet, oops. >>
    def createControl(self, parentFrame): pass
    def setFontFromConfig(self): pass # N/A
    #@+node:ekr.20141110215426.131: *3* setColorFromConfig
    def setColorFromConfig(self): pass

    #@-others
#@+node:ekr.20141110215426.132: ** class textTree
class textTree(leoFrame.LeoTree):

	# undoc: k.makeAllBindings ; nullTree 
    #@+others
    #@+node:ekr.20141110215426.133: *3* setBindings
    def setBindings(self):
        pass
    #@+node:ekr.20141110215426.134: *3* begin/endUpdate & redraw/now
    def beginUpdate(self):
        pass # N/A

    def endUpdate(self,flag=True,scroll=True):
        if flag:
            self.redraw()

    def redraw(self,p=None,scroll=True,forceDraw=False):
        self.text_draw_tree()

    def redraw_now(self,p=None,scroll=True,forceDraw=False):
        if forceDraw:
            self.redraw()
    #@+node:ekr.20141110215426.135: *3* endUpdate
    #@+node:ekr.20141110215426.136: *3* __init__
    def __init__(self,frame):
        
        # undoc: openWithFileName -> treeWantsFocus -> c.frame.tree.canvas
        self.c = frame.c
        self.canvas = None
        leoFrame.LeoTree.__init__(self,frame)
    #@+node:ekr.20141110215426.137: *3* select
    def select(self,p,scroll=True):
        # TODO Much more here: there's four hooks and all sorts of other things called in the TK version. 

        c = self.c ; frame = c.frame
        body = w = c.frame.body.bodyCtrl

        c.setCurrentPosition(p)

        # This is also where the body-text control is given the text of the selected node...
        # Always do this.    Otherwise there can be problems with trailing hewlines.
        w.setAllText(p.b)
        # and something to do with undo?
    #@+node:ekr.20141110215426.138: *3* editLabel & edit_widget
    def editLabel(self,v,selectAll=False,selection=None):
        pass # N/A?

    def edit_widget(self,p):
        return None
    #@+node:ekr.20141110215426.139: *3* text_draw_tree & helper
    def text_draw_tree (self):

        # g.trace(g.callers())
        g.pr('--- tree ---')
        self.draw_tree_helper(self.c.rootPosition(),indent=0)

    def draw_tree_helper (self,p,indent):

        for p in p.self_and_siblings():

            if p.hasChildren():
                box = g.choose(p.isExpanded(),'+','-')
            else:
                box = ' '

            icons = '%s%s%s%s' % (
                g.choose(p.v.t.hasBody(),'b',' '),
                g.choose(p.isMarked(),'m',' '),
                g.choose(p.isCloned(),'@',' '),
                g.choose(p.isDirty(),'*',' '))

            g.pr(" " * indent * 2, icons, box, p.h)

            if p.isExpanded() and p.hasChildren():
                self.draw_tree_helper(p.firstChild(),indent+1)
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
