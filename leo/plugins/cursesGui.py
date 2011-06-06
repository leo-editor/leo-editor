#@+leo-ver=5-thin
#@+node:ekr.20081121105001.12: * @file cursesGui.py
#@+at
# Things not found in the GUI 'interface' classes (in leoFrame.py, leoGui.py, etc)
# are labeled: # undoc: where the AttributeError comes from other implementations
# of method.
#@@c

#@+<< imports >>
#@+node:ekr.20081121105001.13: ** << imports >>
import leo.core.leoGlobals as g

import leo.core.leoChapters as leoChapters
import leo.core.leoColor as leoColor
import leo.core.leoGui as leoGui
import leo.core.leoKeys as leoKeys
import leo.core.leoFrame as leoFrame
import leo.core.leoMenu as leoMenu
import leo.core.leoNodes as leoNodes
#@-<< imports >>
#@+<< TODO >>
#@+node:ekr.20081121105001.14: ** << TODO >>
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
__version__ = '0.2'
#@+<< version history >>
#@+node:ekr.20081121105001.15: ** << version history >>
#@@nocolor
#@+at
# 
# 0.1: Initial checkin, converted to Leo outline(!) by EKR.
# 0.2: EKR:
# - Fixed several crashers related to Leo 4.x code base.
# - textBodyCtrl is now just leoFrame.stringTextWidget.
# - Improved main input loop.
# - You can now enter menu accelerators instead of menu indices in the menu menu.
#@-<< version history >>

if g.isPython3: get_input = input
else:           get_input = raw_input

#@@language python
#@@tabwidth -2

#@+others
#@+node:ekr.20081121105001.16: ** init
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
#@+node:ekr.20081121105001.17: ** underline
def underline(s, idx):

  if idx < 0 or idx > len(s) - 1:
    return s

  return s[:idx] + '&' + s[idx:]
#@+node:ekr.20081121105001.18: ** class textGui
class textGui(leoGui.leoGui):
  #@+others
  #@+node:ekr.20081121105001.19: *3* __init__
  def __init__(self):
    leoGui.leoGui.__init__(self, "text")

    self.frames = []
    self.killed = False
    # TODO leoTkinterFrame finishCreate g.app.windowList.append(f) - use that?
  #@+node:ekr.20081121105001.20: *3* createKeyHandlerClass
  def createKeyHandlerClass (self,c,useGlobalKillbuffer=True,useGlobalRegisters=True):

      # import leo.core.leoKeys as leoKeys # Do this here to break a circular dependency.

      return leoKeys.keyHandlerClass(c,useGlobalKillbuffer,useGlobalRegisters)
  #@+node:ekr.20081121105001.21: *3* createLeoFrame
  def createLeoFrame(self, title):
    ret = textFrame(self, title)
    self.frames.append(ret)
    return ret
  #@+node:ekr.20081121105001.22: *3* createRootWindow
  def createRootWindow(self):
    pass # N/A

  #@+node:ekr.20081121105001.23: *3* destroySelf
  def destroySelf (self):
    self.killed = True
  #@+node:ekr.20081121105001.24: *3* finishCreate
  def finishCreate(self):
    pass
  #@+node:ekr.20081121105001.25: *3* isTextWidget
  def isTextWidget (self,w):

      '''Return True if w is a Text widget suitable for text-oriented commands.'''

      return w and isinstance(w,leoFrame.baseTextWidget)
  #@+node:ekr.20081121105001.26: *3* oops
  def oops(self):
    g.pr("textGui oops", g.callers(), "should be implemented")
  #@+node:ekr.20081121105001.27: *3* runMainLoop
  def runMainLoop(self):
    self.text_run()
  #@+node:ekr.20081121105001.28: *3* runOpenFileDialog
  def runOpenFileDialog(self, title, filetypes, defaultextension, multiple=False):
    import os

    initialdir = g.app.globalOpenDir or g.os_path_abspath(os.getcwd())

    if g.isPython3: get_input = input
    else:           get_input = raw_input

    ret = get_input("Open which %s file (from %s?) > " % (repr(filetypes), initialdir))

    if multiple:
      return [ret,]
    return ret
  #@+node:ekr.20081121105001.29: *3* get/set_focus
  def get_focus(self,c):
    pass

  def set_focus(self,c,w):
    pass
  #@+node:ekr.20081121105001.30: *3* text_run & helper
  def text_run(self):
    frame_idx = 0

    if g.isPython3: get_input = input
    else:           get_input = raw_input

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
  #@+node:ekr.20081121105001.31: *4* doChoice
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
  #@+node:ekr.20081121105001.32: *3* widget_name
  def widget_name(self, w):
    if isinstance(w, textBodyCtrl):
      return 'body'
    return leoGui.leoGui.widget_name(self, w)
  #@-others
#@+node:ekr.20081121105001.33: ** class textFrame
class textFrame(leoFrame.leoFrame):
  #@+others
  #@+node:ekr.20081121105001.34: *3* __init__
  def __init__(self, gui, title):

    leoFrame.leoFrame.__init__(self, gui)

    self.title = title # Per leoFrame.__init__
  #@+node:ekr.20081121105001.35: *3* createFirstTreeNode
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
  #@+node:ekr.20081121105001.36: *3* deiconify
  def deiconify(self): pass # N/A
  def lift(self): pass # N/A
  #@+node:ekr.20081121105001.37: *3* destroySelf
  def destroySelf (self):
      pass
  #@+node:ekr.20081121105001.38: *3* finishCreate
  def finishCreate(self, c):
    f = self ; f.c = c

    f.tree = textTree(self)
    f.body = textBody(frame=self, parentFrame=None)    
    f.log = textLog(frame=self, parentFrame=None)
    f.menu = textLeoMenu(self)

    if f.body.use_chapters:
      c.chapterController = leoChapters.chapterController(c)

    f.createFirstTreeNode()
    c.initVersion()

    # (*after* setting self.log)
    c.setLog() # writeWaitingLog hangs without this(!)

    # So updateRecentFiles will update our menus.
    g.app.windowList.append(f)
  #@+node:ekr.20081121105001.39: *3* setInitialWindowGeometry
  def setInitialWindowGeometry(self): pass # N/A
  #@+node:ekr.20081121105001.40: *3* setMinibufferBindings
  def setMinibufferBindings(self):
    pass

  def setTopGeometry(self, w, h, x, y):
    pass # N/A
  #@+node:ekr.20081121105001.41: *3* text_key
  def text_key(self):
    c = self.c ; k = c.k ; w = self.body.bodyCtrl

    if g.isPython3: get_input = input
    else:           get_input = raw_input

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
  #@+node:ekr.20081121105001.42: *3* update
  def update(self): pass
  def resizePanesToRatio(self, ratio, ratio2): pass # N/A
  #@-others
#@+node:ekr.20081121105001.43: ** class textBody
class textBody(leoFrame.leoBody):
  #@+others
  #@+node:ekr.20081121105001.44: *3* __init__
  def __init__(self, frame, parentFrame):
    leoFrame.leoBody.__init__(self, frame, parentFrame)

    c = frame.c ; name = 'body'

    self.bodyCtrl = textBodyCtrl(c,name)
    self.colorizer = leoColor.nullColorizer(self.c)
  #@+node:ekr.20081121105001.45: *3* bind
  # undoc: newLeoCommanderAndFrame -> c.finishCreate -> k.finishCreate -> k.completeAllBindings -> k.makeMasterGuiBinding -> 2156 w.bind ; nullBody 
  def bind(self, bindStroke, callback): 
    # Quiet, please.    
    ##self.oops()
    pass
  #@+node:ekr.20081121105001.46: *3* setEditorColors
  # TODO Tkinter onBodyChanged undo call and many others. =(

  def setEditorColors(self, bg, fg): pass # N/A
  def createBindings(self, w=None): pass
  #@+node:ekr.20081121105001.47: *3* text_show
  def text_show(self):

    w = self.bodyCtrl
    g.pr('--- body ---')
    g.pr('ins',w.ins,'sel',w.sel)
    g.pr(w.s)
  #@-others
#@+node:ekr.20081121105001.48: ** class textBodyCtrl (stringTextWidget)
class textBodyCtrl (leoFrame.stringTextWidget):
  pass
#@+node:ekr.20081121105001.49: ** class textMenuCascade
class textMenuCascade:
  #@+others
  #@+node:ekr.20081121105001.50: *3* __init__
  def __init__(self, menu, label, underline):
    self.menu = menu
    self.label = label
    self.underline = underline
  #@+node:ekr.20081121105001.51: *3* display
  def display(self):      
    ret = underline(self.label, self.underline)
    if len(self.menu.entries) == 0:
      ret += ' [Submenu with no entries]'
    return ret
  #@-others
#@+node:ekr.20081121105001.52: ** class textMenuEntry
class textMenuEntry:
  #@+others
  #@+node:ekr.20081121105001.53: *3* __init__
  def __init__(self, label, underline, accel, callback):
    self.label = label
    self.underline = underline
    self.accel = accel
    self.callback = callback
  #@+node:ekr.20081121105001.54: *3* display
  def display(self):
    return "%s %s" % (underline(self.label, self.underline), self.accel,)
  #@-others
#@+node:ekr.20081121105001.55: ** class textMenuSep
class textMenuSep:  
  #@+others
  #@+node:ekr.20081121105001.56: *3* display
  def display(self): 
    return '-' * 5
  #@-others
#@+node:ekr.20081121105001.57: ** class textLeoMenu (leoMenu)
class textLeoMenu(leoMenu.leoMenu):

  #@+others
  #@+node:ekr.20081121105001.58: *3* ctor (textLeoMenu)
  def __init__ (self,frame):


      self.entries = []
      self.c = frame.c

      # Init the base class
      leoMenu.leoMenu.__init__(self,frame)
  #@+node:ekr.20081121105001.59: *3* createMenuBar
  def createMenuBar(self, frame):

    g.trace(frame.c)

    self._top_menu = textLeoMenu(frame)

    self.createMenusFromTables()
  #@+node:ekr.20081121105001.60: *3* new_menu
  def new_menu(self, parent,tearoff=False):

    if tearoff != False: raise NotImplementedError(repr(tearoff))

    # I don't know what the 'parent' argument is for; neither does the wx GUI.

    ### return textMenu()
    menu = textLeoMenu(parent or self.frame)
    menu.entries = []
    return menu
  #@+node:ekr.20081121105001.61: *3* add_cascade
  def add_cascade(self, parent, label, menu, underline):

    # g.trace('parent',parent)

    if parent == None:
        parent = self._top_menu
    parent.entries.append(textMenuCascade(menu, label, underline,))
  #@+node:ekr.20081121105001.62: *3* add_command
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
  #@+node:ekr.20081121105001.63: *3* add_separator
  def add_separator(self, menu):
    menu.entries.append(textMenuSep())
  #@+node:ekr.20081121105001.64: *3* delete_range
  def delete_range (self,*args,**keys):

    pass
  #@+node:ekr.20081121105001.65: *3* show_menu
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
#@+node:ekr.20081121105001.66: ** class textLog
class textLog(leoFrame.leoLog):
	# undoc: leoKeys.py makeAllBindings c.frame.log.setTabBindings('Log') ; nullLog 
  #@+others
  #@+node:ekr.20081121105001.67: *3* setTabBindings
  def setTabBindings(self, tabName):
    pass  
  #@+node:ekr.20081121105001.68: *3* put
  def put(self, s, color=None, tabName='log'):
    g.pr(s,newline=False)
  #@+node:ekr.20081121105001.69: *3* putnl
  def putnl(self, tabName='log'):
    g.pr('')
  #@+node:ekr.20081121105001.70: *3* createControl
  # < < HACK Quiet, oops. >>
  def createControl(self, parentFrame): pass
  def setFontFromConfig(self): pass # N/A
  #@+node:ekr.20081121105001.71: *3* setColorFromConfig
  def setColorFromConfig(self): pass

  #@-others
#@+node:ekr.20081121105001.72: ** class textTree
class textTree(leoFrame.leoTree):
	# undoc: k.makeAllBindings ; nullTree 
  #@+others
  #@+node:ekr.20081121105001.73: *3* setBindings
  def setBindings(self):
    pass
  #@+node:ekr.20081121105001.74: *3* begin/endUpdate & redraw/now
  def beginUpdate(self):
    pass # N/A

  def endUpdate(self,flag=True,scroll=True):
    if flag:
      self.redraw()

  def redraw(self,scroll=True):
    self.text_draw_tree()

  def redraw_now(self,scroll=True,forceDraw=True):
    if forceDraw:
      self.redraw()
  #@+node:ekr.20081121105001.75: *3* endUpdate
  #@+node:ekr.20081121105001.76: *3* __init__
  def __init__(self, frame):
    # undoc: openWithFileName -> treeWantsFocus -> c.frame.tree.canvas
    self.canvas = None

    leoFrame.leoTree.__init__(self, frame)
  #@+node:ekr.20081121105001.77: *3* select
  def select(self,p,scroll=True):
    # TODO Much more here: there's four hooks and all sorts of other things called in the TK version. 

    c = self.c ; frame = c.frame
    body = w = c.frame.body.bodyCtrl

    c.setCurrentPosition(p)

    # This is also where the body-text control is given the text of the selected node...
    # Always do this.  Otherwise there can be problems with trailing hewlines.
    w.setAllText(p.b)
    # and something to do with undo?
  #@+node:ekr.20081121105001.78: *3* editLabel & edit_widget
  def editLabel(self,p,selectAll=False):
    pass # N/A?

  def edit_widget(self,p):
    return None
  #@+node:ekr.20081121105001.79: *3* text_draw_tree & helper
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
#@-leo
