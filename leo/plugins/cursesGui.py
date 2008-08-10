#@+leo-ver=4-thin
#@+node:ekr.20061207074949:@thin cursesGui.py
#@+at 
#@nonl
# Things not found in the GUI 'interface' classes (in leoFrame.py, leoGui.py, 
# etc)
# are labeled: # undoc: where the AttributeError comes from ; other 
# implementations of method
#@-at
#@@c

#@<< imports >>
#@+node:ekr.20061207074949.1:<< imports >>
import leo.core.leoGlobals as g

import leo.core.leoChapters as leoChapters
import leo.core.leoColor as leoColor
import leo.core.leoGui as leoGui
import leo.core.leoKeys as leoKeys
import leo.core.leoFrame as leoFrame
import leo.core.leoMenu as leoMenu
import leo.core.leoNodes as leoNodes
#@-node:ekr.20061207074949.1:<< imports >>
#@nl
#@<< TODO >>
#@+node:ekr.20061207075428:<< TODO >>
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
# What kind of newlines does the body text control get? How should it treat 
# them?
# Headline editing?
# Body text selection.
# (Strip trailing whitespace from this file. :P)
# < < Random cruft >>
# Pay attention to being direct and code-terse.
# Not at all user-friendly.
# Comments in the body reflect current status only.
# Ideally, comments in the body go away as the "leoGUI interface" improves.
# Written on a hundred-column terminal. :S
#@-at
#@nonl
#@-node:ekr.20061207075428:<< TODO >>
#@nl
__version__ = '0.2'
#@<< version history >>
#@+node:ekr.20061207081338:<< version history >>
#@@nocolor
#@+at
# 
# 0.1: Initial checkin, converted to Leo outline(!) by EKR.
# 0.2: EKR:
# - Fixed several crashers related to Leo 4.x code base.
# - textBodyCtrl is now just leoFrame.stringTextWidget.
# - Improved main input loop.
# - You can now enter menu accelerators instead of menu indices in the menu 
# menu.
#@-at
#@nonl
#@-node:ekr.20061207081338:<< version history >>
#@nl

#@@language python
#@@tabwidth -2

#@+others
#@+node:ekr.20061207074949.2:init
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
#@-node:ekr.20061207074949.2:init
#@+node:ekr.20061207074949.44:underline
def underline(s, idx):

  if idx < 0 or idx > len(s) - 1:
    return s

  return s[:idx] + '&' + s[idx:]
#@-node:ekr.20061207074949.44:underline
#@+node:ekr.20061207074949.3:class textGui
class textGui(leoGui.leoGui):
  #@	@+others
  #@+node:ekr.20061207074949.4:__init__
  def __init__(self):
    leoGui.leoGui.__init__(self, "text")

    self.frames = []
    self.killed = False
    # TODO leoTkinterFrame finishCreate g.app.windowList.append(f) - use that?
  #@-node:ekr.20061207074949.4:__init__
  #@+node:ekr.20071211151202:createKeyHandlerClass
  def createKeyHandlerClass (self,c,useGlobalKillbuffer=True,useGlobalRegisters=True):

      # import leo.core.leoKeys as leoKeys # Do this here to break a circular dependency.

      return leoKeys.keyHandlerClass(c,useGlobalKillbuffer,useGlobalRegisters)
  #@nonl
  #@-node:ekr.20071211151202:createKeyHandlerClass
  #@+node:ekr.20061207074949.6:createLeoFrame
  def createLeoFrame(self, title):
    ret = textFrame(self, title)
    self.frames.append(ret)
    return ret
  #@-node:ekr.20061207074949.6:createLeoFrame
  #@+node:ekr.20061207074949.7:createRootWindow
  def createRootWindow(self):
    pass # N/A

  #@-node:ekr.20061207074949.7:createRootWindow
  #@+node:ekr.20071211151659:destroySelf
  def destroySelf (self):
    self.killed = True
  #@nonl
  #@-node:ekr.20071211151659:destroySelf
  #@+node:ekr.20061207074949.12:finishCreate
  def finishCreate(self):
    pass
  #@-node:ekr.20061207074949.12:finishCreate
  #@+node:ekr.20071212073036:isTextWidget
  def isTextWidget (self,w):

      '''Return True if w is a Text widget suitable for text-oriented commands.'''

      return w and isinstance(w,leoFrame.baseTextWidget)
  #@-node:ekr.20071212073036:isTextWidget
  #@+node:ekr.20061207074949.5:oops
  def oops(self):
    g.pr("textGui oops", g.callers(), "should be implemented")
  #@-node:ekr.20061207074949.5:oops
  #@+node:ekr.20061207074949.8:runMainLoop
  def runMainLoop(self):
    self.text_run()
  #@-node:ekr.20061207074949.8:runMainLoop
  #@+node:ekr.20061207074949.11:runOpenFileDialog
  def runOpenFileDialog(self, title, filetypes, defaultextension, multiple=False):
    import os

    initialdir = g.app.globalOpenDir or g.os_path_abspath(os.getcwd())
    ret = raw_input("Open which %s file (from %s?) > " % (`filetypes`, initialdir))
    if multiple:
      return [ret,]
    return ret
  #@-node:ekr.20061207074949.11:runOpenFileDialog
  #@+node:ekr.20071211180217:get/set_focus
  def get_focus(self,c):
    pass

  def set_focus(self,c,w):
    pass
  #@-node:ekr.20071211180217:get/set_focus
  #@+node:ekr.20061207074949.13:text_run & helper
  def text_run(self):
    frame_idx = 0

    while not self.killed:

      # Frames can come and go.
      if frame_idx > len(self.frames) - 1:
        frame_idx = 0
      f = self.frames[frame_idx]
      g.pr(f.getTitle())
      s = raw_input('Do what? (menu,key,body,frames,tree,quit) > ')

      try:
        self.doChoice(f,s)
      except Exception:
          g.es_exception()
  #@+node:ekr.20071212072046:doChoice
  def doChoice(self,f,s):

    if s in ('m','menu'):
      f.menu.text_menu()
    elif s in ('k','key'):
      f.text_key()
    elif s in ('b','body'):
      f.body.text_show()
    elif s in ('f','frames'):
      for i, f in enumerate(self.frames):
        g.pr(i, ')', f.getTitle())
      s = raw_input('Operate on which frame? > ')
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
  #@nonl
  #@-node:ekr.20071212072046:doChoice
  #@-node:ekr.20061207074949.13:text_run & helper
  #@+node:ekr.20061207074949.10:widget_name
  def widget_name(self, w):
    if isinstance(w, textBodyCtrl):
      return 'body'
    return leoGui.leoGui.widget_name(self, w)
  #@-node:ekr.20061207074949.10:widget_name
  #@-others
#@-node:ekr.20061207074949.3:class textGui
#@+node:ekr.20061207074949.14:class textFrame
class textFrame(leoFrame.leoFrame):
  #@	@+others
  #@+node:ekr.20061207074949.15:__init__
  def __init__(self, gui, title):

    leoFrame.leoFrame.__init__(self, gui)

    self.title = title # Per leoFrame.__init__
  #@-node:ekr.20061207074949.15:__init__
  #@+node:ekr.20071211151551:destroySelf
  def destroySelf (self):
      pass
  #@nonl
  #@-node:ekr.20071211151551:destroySelf
  #@+node:ekr.20061207074949.16:finishCreate
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
  #@-node:ekr.20061207074949.16:finishCreate
  #@+node:ekr.20061207074949.17:createFirstTreeNode
  # From leoTkinterFrame.py
  def createFirstTreeNode (self):

    f = self ; c = f.c

    t = leoNodes.tnode()
    v = leoNodes.vnode(context=c,t=t)
    p = leoNodes.position(v)
    v.initHeadString("NewHeadline")
    p.moveToRoot(oldRoot=None)
    c.setRootPosition(p) # New in 4.4.2.
    c.editPosition(p)
  #@-node:ekr.20061207074949.17:createFirstTreeNode
  #@+node:ekr.20061207074949.18:setMinibufferBindings
  # undoc: leoKeys.makeAllBindings ; nullFrame 
  def setMinibufferBindings(self):
    self.oops()
  #@-node:ekr.20061207074949.18:setMinibufferBindings
  #@+node:ekr.20061207074949.19:setMinibufferBindings
  def setMinibufferBindings(self):
    pass

  def setTopGeometry(self, w, h, x, y):
    pass # N/A
  #@-node:ekr.20061207074949.19:setMinibufferBindings
  #@+node:ekr.20061207074949.20:deiconify
  def deiconify(self): pass # N/A
  def lift(self): pass # N/A
  #@-node:ekr.20061207074949.20:deiconify
  #@+node:ekr.20061207074949.21:update
  def update(self): pass
  def resizePanesToRatio(self, ratio, ratio2): pass # N/A
  #@-node:ekr.20061207074949.21:update
  #@+node:ekr.20061207074949.22:setInitialWindowGeometry
  def setInitialWindowGeometry(self): pass # N/A
  #@-node:ekr.20061207074949.22:setInitialWindowGeometry
  #@+node:ekr.20061207074949.23:text_key
  def text_key(self):
    c = self.c ; k = c.k ; w = self.body.bodyCtrl
    key = raw_input('Keystroke > ')
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
    k.masterKeyHandler(event=e,stroke=key)
  #@-node:ekr.20061207074949.23:text_key
  #@-others
#@-node:ekr.20061207074949.14:class textFrame
#@+node:ekr.20061207074949.24:class textBody
class textBody(leoFrame.leoBody):
  #@	@+others
  #@+node:ekr.20061207074949.25:__init__
  def __init__(self, frame, parentFrame):
    leoFrame.leoBody.__init__(self, frame, parentFrame)

    c = frame.c ; name = 'body'

    self.bodyCtrl = textBodyCtrl(c,name)
    self.colorizer = leoColor.nullColorizer(self.c)
  #@-node:ekr.20061207074949.25:__init__
  #@+node:ekr.20061207074949.26:bind
  # undoc: newLeoCommanderAndFrame -> c.finishCreate -> k.finishCreate -> k.completeAllBindings -> k.makeMasterGuiBinding -> 2156 w.bind ; nullBody 
  def bind(self, bindStroke, callback): 
    # Quiet, please.    
    ##self.oops()
    pass
  #@-node:ekr.20061207074949.26:bind
  #@+node:ekr.20061207074949.27:setEditorColors
  # TODO Tkinter onBodyChanged undo call and many others. =(

  def setEditorColors(self, bg, fg): pass # N/A
  def createBindings(self, w=None): pass
  #@-node:ekr.20061207074949.27:setEditorColors
  #@+node:ekr.20061207074949.28:text_show
  def text_show(self):

    w = self.bodyCtrl
    g.pr('--- body ---')
    g.pr('ins',w.ins,'sel',w.sel)
    g.pr(w.s)
  #@-node:ekr.20061207074949.28:text_show
  #@-others
#@-node:ekr.20061207074949.24:class textBody
#@+node:ekr.20071212070608:class textBodyCtrl (stringTextWidget)
class textBodyCtrl (leoFrame.stringTextWidget):
  pass
#@-node:ekr.20071212070608:class textBodyCtrl (stringTextWidget)
#@+node:ekr.20061207074949.45:class textMenu
class textMenu:
  #@	@+others
  #@+node:ekr.20061207074949.46:__init__
  def __init__(self):
    self.entries = []

  def delete_range(self,*args,**keys):
    pass
  #@nonl
  #@-node:ekr.20061207074949.46:__init__
  #@-others
#@-node:ekr.20061207074949.45:class textMenu
#@+node:ekr.20061207074949.47:class textMenuCascade
class textMenuCascade:
  #@	@+others
  #@+node:ekr.20061207074949.48:__init__
  def __init__(self, menu, label, underline):
    self.menu = menu
    self.label = label
    self.underline = underline
  #@-node:ekr.20061207074949.48:__init__
  #@+node:ekr.20061207074949.49:display
  def display(self):      
    ret = underline(self.label, self.underline)
    if len(self.menu.entries) == 0:
      ret += ' [Submenu with no entries]'
    return ret
  #@-node:ekr.20061207074949.49:display
  #@-others
#@-node:ekr.20061207074949.47:class textMenuCascade
#@+node:ekr.20061207074949.50:class textMenuEntry
class textMenuEntry:
  #@	@+others
  #@+node:ekr.20061207074949.51:__init__
  def __init__(self, label, underline, accel, callback):
    self.label = label
    self.underline = underline
    self.accel = accel
    self.callback = callback
  #@-node:ekr.20061207074949.51:__init__
  #@+node:ekr.20061207074949.52:display
  def display(self):
    return "%s %s" % (underline(self.label, self.underline), self.accel,)
  #@-node:ekr.20061207074949.52:display
  #@-others
#@-node:ekr.20061207074949.50:class textMenuEntry
#@+node:ekr.20061207074949.53:class textMenuSep
class textMenuSep:  
  #@	@+others
  #@+node:ekr.20061207074949.54:display
  def display(self): 
    return '-' * 5
  #@-node:ekr.20061207074949.54:display
  #@-others
#@-node:ekr.20061207074949.53:class textMenuSep
#@+node:ekr.20061207074949.55:class textLeoMenu
class textLeoMenu(leoMenu.leoMenu):
  #@	@+others
  #@+node:ekr.20061207074949.56:createMenuBar
  def createMenuBar(self, frame):
    self._top_menu = textMenu()

    self.createMenusFromTables()
  #@-node:ekr.20061207074949.56:createMenuBar
  #@+node:ekr.20061207074949.57:new_menu
  def new_menu(self, parent, tearoff=False):

    if tearoff != False: raise NotImplementedError(`tearoff`)

    # I don't know what the 'parent' argument is for; neither does the wx GUI.

    return textMenu()
  #@-node:ekr.20061207074949.57:new_menu
  #@+node:ekr.20061207074949.58:add_cascade
  def add_cascade(self, parent, label, menu, underline):    
    if parent == None:
      parent = self._top_menu
    parent.entries.append(textMenuCascade(menu, label, underline,))
  #@-node:ekr.20061207074949.58:add_cascade
  #@+node:ekr.20061207074949.59:add_command
  def add_command(self, menu, label, underline, command, accelerator=''):
    # ?
    # underline - Offset into label. For those who memorised Alt, F, X rather than Alt+F4.
    # accelerator - For display only; these are implemented by Leo's key handling.

    menu.entries.append(textMenuEntry(label, underline, accelerator, command))
  #@-node:ekr.20061207074949.59:add_command
  #@+node:ekr.20061207074949.60:add_separator
  def add_separator(self, menu):
    menu.entries.append(textMenuSep())
  #@-node:ekr.20061207074949.60:add_separator
  #@+node:ekr.20061207074949.61:text_menu
  def text_menu(self):
    last_menu = self._top_menu

    while True:
      entries = last_menu.entries

      for i, entry in enumerate(entries):
        g.pr(i, ')', entry.display())
      g.pr(len(last_menu.entries), ')', '[Prev]')

      which = raw_input('Which menu entry? > ')
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
  #@-node:ekr.20061207074949.61:text_menu
  #@-others
#@-node:ekr.20061207074949.55:class textLeoMenu
#@+node:ekr.20061207074949.62:class textLog
class textLog(leoFrame.leoLog):
	# undoc: leoKeys.py makeAllBindings c.frame.log.setTabBindings('Log') ; nullLog 
  #@	@+others
  #@+node:ekr.20061207074949.64:setTabBindings
  def setTabBindings(self, tabName):
    pass  
  #@-node:ekr.20061207074949.64:setTabBindings
  #@+node:ekr.20061207074949.65:put
  def put(self, s, color=None, tabName='log'):
    g.pr(s,newline=False)
  #@-node:ekr.20061207074949.65:put
  #@+node:ekr.20061207074949.66:putnl
  def putnl(self, tabName='log'):
    g.pr('')
  #@-node:ekr.20061207074949.66:putnl
  #@+node:ekr.20061207074949.67:createControl
  # < < HACK Quiet, oops. >>
  def createControl(self, parentFrame): pass
  def setFontFromConfig(self): pass # N/A
  #@-node:ekr.20061207074949.67:createControl
  #@+node:ekr.20061207074949.68:setColorFromConfig
  def setColorFromConfig(self): pass

  #@-node:ekr.20061207074949.68:setColorFromConfig
  #@-others
#@-node:ekr.20061207074949.62:class textLog
#@+node:ekr.20061207074949.69:class textTree
class textTree(leoFrame.leoTree):
	# undoc: k.makeAllBindings ; nullTree 
  #@	@+others
  #@+node:ekr.20061207074949.71:setBindings
  def setBindings(self):
    pass
  #@-node:ekr.20061207074949.71:setBindings
  #@+node:ekr.20061207074949.72:beginUpdate
  def beginUpdate(self):
    pass # N/A
  #@-node:ekr.20061207074949.72:beginUpdate
  #@+node:ekr.20061207074949.73:endUpdate
  def endUpdate(self, flag, scroll=True): 

    self.text_draw_tree()
  #@-node:ekr.20061207074949.73:endUpdate
  #@+node:ekr.20061207074949.74:__init__
  def __init__(self, frame):
    # undoc: openWithFileName -> treeWantsFocusNow -> c.frame.tree.canvas
    self.canvas = None

    leoFrame.leoTree.__init__(self, frame)
  #@-node:ekr.20061207074949.74:__init__
  #@+node:ekr.20061207074949.75:select
  def select(self,p,updateBeadList=True,scroll=True):
    # TODO Much more here: there's four hooks and all sorts of other things called in the TK version. 

    c = self.c ; frame = c.frame
    body = w = c.frame.body.bodyCtrl

    c.setCurrentPosition(p)

    # This is also where the body-text control is given the text of the selected node...
    # Always do this.  Otherwise there can be problems with trailing hewlines.
    s = g.toUnicode(p.v.t._bodyString,"utf-8")
    w.setAllText(s)
    # and something to do with undo?
  #@-node:ekr.20061207074949.75:select
  #@+node:ekr.20061207074949.76:editLabel
  def editLabel(self,p,selectAll=False):
    pass # N/A?
  #@-node:ekr.20061207074949.76:editLabel
  #@+node:ekr.20061207074949.77:text_draw_tree & helper
  def text_draw_tree (self):

    # g.trace(g.callers())
    g.pr('--- tree ---')

    self.draw_tree_helper(self.c.rootPosition(),indent=0)

  def draw_tree_helper (self,p,indent):

    for p in p.self_and_siblings_iter():

      if p.hasChildren():
        box = g.choose(p.isExpanded(),'+','-')
      else:
        box = ' '

      icons = '%s%s%s%s' % (
        g.choose(p.v.t.hasBody(),'b',' '),
        g.choose(p.isMarked(),'m',' '),
        g.choose(p.isCloned(),'@',' '),
        g.choose(p.isDirty(),'*',' '))

      g.pr(" " * indent * 2, icons, box, p.headString())

      if p.isExpanded() and p.hasChildren():
        self.draw_tree_helper(p.firstChild(),indent+1)
  #@-node:ekr.20061207074949.77:text_draw_tree & helper
  #@-others
#@-node:ekr.20061207074949.69:class textTree
#@-others
#@-node:ekr.20061207074949:@thin cursesGui.py
#@-leo
