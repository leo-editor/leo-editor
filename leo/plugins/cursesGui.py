#@+leo-ver=5-thin
#@+node:ekr.20150107090324.1: * @file ../plugins/cursesGui.py
"""A minimal text-oriented gui."""
#@+at
# Things not found in the GUI 'interface' classes (in leoFrame.py, leoGui.py, etc)
# are labeled: # undoc: where the AttributeError comes from other implementations
# of method.
#@@c
# pylint: disable=arguments-differ
#@+<< imports >>
#@+node:ekr.20150107090324.2: ** << imports >>
from collections.abc import Callable
import os
from typing import Any
from leo.core import leoGlobals as g
from leo.core import leoChapters
from leo.core import leoGui
from leo.core import leoKeys
from leo.core import leoFrame
from leo.core import leoMenu
from leo.core import leoNodes
get_input = input

#@-<< imports >>
Widget = Any
#@+<< TODO >>
#@+node:ekr.20150107090324.3: ** << TODO >>
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
#@+others
#@+node:ekr.20150107090324.4: ** init
def init():
    ok = not g.app.gui and not g.unitTesting  # Not Ok for unit testing!
    if ok:
        g.app.gui = textGui()
        g.app.root = g.app.gui.createRootWindow()
        g.app.gui.finishCreate()
        g.plugin_signon(__name__)
    elif g.app.gui and not g.unitTesting:
        s = "Can't install text gui: previous gui installed"
        g.es_print(s, color="red")
    return ok
#@+node:ekr.20150107090324.5: ** underline
def underline(s, idx):
    if idx < 0 or idx > len(s) - 1:
        return s
    return s[:idx] + '&' + s[idx:]
#@+node:ekr.20150107090324.6: ** class textGui
class textGui(leoGui.LeoGui):
    #@+others
    #@+node:ekr.20150107090324.7: *3* __init__
    def __init__(self):
        super().__init__("text")
        self.frames = []
        self.killed = False
        # TODO leoTkinterFrame finishCreate g.app.windowList.append(f) - use that?
    #@+node:ekr.20150107090324.8: *3* createKeyHandlerClass
    def createKeyHandlerClass(self, c):

        return leoKeys.KeyHandlerClass(c)
    #@+node:ekr.20150107090324.9: *3* createLeoFrame
    def createLeoFrame(self, c, title=None) -> Any:
        gui = self
        ret = TextFrame(c, gui)
        self.frames.append(ret)
        return ret
    #@+node:ekr.20150107090324.10: *3* createRootWindow
    def createRootWindow(self):
        pass  # N/A
    #@+node:ekr.20150107090324.11: *3* destroySelf
    def destroySelf(self):
        self.killed = True
    #@+node:ekr.20150107090324.12: *3* finishCreate
    def finishCreate(self):
        pass
    #@+node:ekr.20150107090324.17: *3* get/set_focus
    def get_focus(self, c):
        pass

    def set_focus(self, c, w):
        pass
    #@+node:ekr.20150107090324.13: *3* isTextWidget
    def isTextWidget(self, w):
        """Return True if w is a Text widget suitable for text-oriented commands."""
        return w and isinstance(w, leoFrame.StringTextWrapper)
    #@+node:ekr.20150107090324.69: *3* runAskYesNoDialog
    def runAskYesNoDialog(self, c, title, message=None, yes_all=False, no_all=False):
        return 'yes'
    #@+node:ekr.20150107090324.15: *3* runMainLoop
    def runMainLoop(self):
        self.text_run()
    #@+node:ekr.20150107090324.16: *3* runOpenFileDialog
    def runOpenFileDialog(self,
        c, title, filetypes, defaultextension, multiple=False, startpath=None,
    ) -> str:
        initialdir = g.app.globalOpenDir or g.os_path_abspath(os.getcwd())
        ret = get_input("Open which %s file (from %s?) > " % (repr(filetypes), initialdir))
        if multiple:
            return [ret,]
        return ret
    #@+node:ekr.20150107090324.18: *3* text_run & helper
    def text_run(self):
        frame_idx = 0
        while not self.killed:
            # Frames can come and go.
            if frame_idx > len(self.frames) - 1:
                frame_idx = 0
            f = self.frames[frame_idx]
            g.pr(f.getTitle())
            s = get_input('Do what? (menu,key,body,frames,tree,quit) > ')
            try:
                self.doChoice(f, s)
            except Exception:
                g.es_exception()
    #@+node:ekr.20150107090324.19: *4* doChoice
    def doChoice(self, f, s):
        if s in ('m', 'menu'):
            f.menu.show_menu()
        elif s in ('k', 'key'):
            f.text_key()
        elif s in ('b', 'body'):
            f.body.text_show()
        elif s in ('f', 'frames'):
            for i, f in enumerate(self.frames):
                g.pr(i, ')', f.getTitle())
            s = get_input('Operate on which frame? > ')
            try:
                s = int(s)
            except ValueError:
                s = -1
            # if s >= 0 and s <= len(self.frames) - 1:
            #    frame_idx = s
        elif s in ('t', 'tree'):
            f.tree.text_draw_tree()
        elif s in ('q', 'quit'):
            self.killed = True
    #@+node:ekr.20150107090324.20: *3* widget_name
    def widget_name(self, w):
        if isinstance(w, textBodyCtrl):
            return 'body'
        return leoGui.LeoGui.widget_name(self, w)
    #@-others
#@+node:ekr.20150107090324.21: ** class TextFrame
class TextFrame(leoFrame.LeoFrame):
    #@+others
    #@+node:ekr.20150107090324.22: *3* __init__
    def __init__(self, c, gui):
        super().__init__(c, gui)
        assert self.c == c
        self.top = None
        self.ratio = self.secondary_ratio = 0.0
    #@+node:ekr.20150107090324.23: *3* createFirstTreeNode (cursesGui.py)
    def createFirstTreeNode(self):
        c = self.c
        #
        # #1631: Initialize here, not in p._linkAsRoot.
        c.hiddenRootNode.children = []
        #
        # #1817: Clear the gnxDict.
        c.fileCommands.gnxDict = {}
        #
        v = leoNodes.vnode(context=c)
        p = leoNodes.Position(v)
        v.initHeadString("newHeadline")
        # New in Leo 4.5: p.moveToRoot would be wrong:
        # the node hasn't been linked yet.
        p._linkAsRoot()
        # c.setRootPosition(p) # New in 4.4.2.
    #@+node:ekr.20150107090324.24: *3* deiconify
    def deiconify(self):
        pass  # N/A

    def lift(self):
        pass  # N/A
    #@+node:ekr.20150107090324.25: *3* destroySelf
    def destroySelf(self):
        pass
    #@+node:ekr.20150107090324.26: *3* finishCreate
    def finishCreate(self):
        c, f = self.c, self
        f.tree = textTree(self)
        f.body = textBody(frame=self, parentFrame=None)
        f.log = textLog(frame=self, parentFrame=None)
        f.menu = textLeoMenu(self)
        if f.body.use_chapters:
            c.chapterController = leoChapters.ChapterController(c)
        f.createFirstTreeNode()
        # (*after* setting self.log)
        c.setLog()  # writeWaitingLog hangs without this(!)
        # So updateRecentFiles will update our menus.
        g.app.windowList.append(f)
    #@+node:ekr.20161118195504.1: *3* getFocus
    def getFocus(self):
        return None
    #@+node:ekr.20150107090324.27: *3* setInitialWindowGeometry
    def setInitialWindowGeometry(self):
        pass  # N/A
    #@+node:ekr.20150107090324.28: *3* setMinibufferBindings
    def setMinibufferBindings(self):
        pass

    def setTopGeometry(self, w, h, x, y):
        pass  # N/A
    #@+node:ekr.20150107090324.29: *3* text_key
    def text_key(self):
        c = self.c
        k = c.k
        w = self.body.bodyCtrl
        key = get_input('Keystroke > ')
        if not key:
            return

        class leoTypingEvent:

            def __init__(self, c, w, char, keysym):
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
        g.trace('char', repr(char), 'stroke', repr(stroke))
        e = leoTypingEvent(c, w, char, stroke)
        k.masterKeyHandler(event=e)  ## ,stroke=key)
    #@+node:ekr.20150107090324.30: *3* update
    def update(self):
        pass

    def resizePanesToRatio(self, ratio: float, ratio2: float) -> None:
        pass  # N/A
    #@-others
#@+node:ekr.20150107090324.31: ** class textBody
class textBody(leoFrame.LeoBody):
    #@+others
    #@+node:ekr.20150107090324.32: *3* __init__
    def __init__(self, frame, parentFrame):
        super().__init__(frame, parentFrame)
        c = frame.c
        name = 'body'
        self.bodyCtrl = textBodyCtrl(c, name)
        self.colorizer = leoFrame.NullColorizer(self.c)
    #@+node:ekr.20150107090324.33: *3* bind
    # undoc: newLeoCommanderAndFrame -> c.finishCreate -> k.finishCreate ->
    # k.completeAllBindings -> k.makeMasterGuiBinding -> 2156 w.bind ; nullBody

    def bind(self, bindStroke, callback):
        pass
    #@+node:ekr.20150107090324.34: *3* setEditorColors
    def setEditorColors(self, bg, fg):
        pass  # N/A

    def createBindings(self, w=None):
        pass
    #@+node:ekr.20150107090324.35: *3* text_show
    def text_show(self):
        w = self.bodyCtrl
        g.pr('--- body ---')
        g.pr('ins', w.ins, 'sel', w.sel)
        g.pr(w.s)
    #@-others
#@+node:ekr.20150107090324.36: ** class textBodyCtrl (stringTextWrapper)
class textBodyCtrl(leoFrame.StringTextWrapper):
    pass
#@+node:ekr.20150107090324.37: ** class textMenuCascade
class textMenuCascade:
    #@+others
    #@+node:ekr.20150107090324.38: *3* __init__
    def __init__(self, menu, label, underline):
        self.menu = menu
        self.label = label
        self.underline = underline
    #@+node:ekr.20150107090324.39: *3* display
    def display(self):
        ret = underline(self.label, self.underline)
        if not self.menu.entries:
            ret += ' [Submenu with no entries]'
        return ret
    #@-others
#@+node:ekr.20150107090324.40: ** class textMenuEntry
class textMenuEntry:
    #@+others
    #@+node:ekr.20150107090324.41: *3* __init__
    def __init__(self, label, underline, accel, callback):
        self.label = label
        self.underline = underline
        self.accel = accel
        self.callback = callback
    #@+node:ekr.20150107090324.42: *3* display
    def display(self):
        return "%s %s" % (underline(self.label, self.underline), self.accel,)
    #@-others
#@+node:ekr.20150107090324.43: ** class textMenuSep
class textMenuSep:
    #@+others
    #@+node:ekr.20150107090324.44: *3* display
    def display(self):
        return '-' * 5
    #@-others
#@+node:ekr.20150107090324.45: ** class textLeoMenu (LeoMenu)
class textLeoMenu(leoMenu.LeoMenu):
    #@+others
    #@+node:ekr.20150107090324.46: *3* ctor (textLeoMenu)
    def __init__(self, frame):
        self.entries = []
        self.c = frame.c
        super().__init__(frame)
    #@+node:ekr.20150107090324.47: *3* createMenuBar
    def createMenuBar(self, frame):
        g.trace(frame.c)
        self._top_menu = textLeoMenu(frame)
        self.createMenusFromTables()
    #@+node:ekr.20150107090324.48: *3* new_menu
    def new_menu(self, parent: Widget, tearoff: int=0, labe: str=''):
        if tearoff:
            raise NotImplementedError(repr(tearoff))
        menu = textLeoMenu(parent or self.frame)
        menu.entries = []
        return menu
    #@+node:ekr.20150107090324.49: *3* add_cascade
    def add_cascade(self, parent: Any, label: str, menu: Any, underline: int):
        if parent is None:
            parent = self._top_menu
        parent.entries.append(textMenuCascade(menu, label, underline,))
    #@+node:ekr.20150107090324.50: *3* add_command (cursesGui.py)
    def add_command(self, menu: Widget,
        accelerator: str='',
        command: Callable=None,
        commandName: str=None,
        label: str=None,
        underline: int=0,
    ) -> None:
        # ?
        # underline - Offset into label. For those who memorised Alt, F, X rather than Alt+F4.
        # accelerator - For display only; these are implemented by Leo's key handling.
        menu = self

        def doNothingCallback():
            pass

        if not command:
            command = doNothingCallback

        # label = keys.get('label') or 'no label'
        # underline = keys.get('underline') or 0
        # accelerator = keys.get('accelerator') or ''
        # command = keys.get('command') or doNothingCallback
        entry = textMenuEntry(label, underline, accelerator, command)
        menu.entries.append(entry)
    #@+node:ekr.20150107090324.51: *3* add_separator
    def add_separator(self, menu):
        menu.entries.append(textMenuSep())
    #@+node:ekr.20150107090324.52: *3* delete_range
    def delete_range(self, *args, **keys):
        pass
    #@+node:ekr.20150107090324.53: *3* show_menu
    def show_menu(self):
        last_menu = self._top_menu
        while True:
            entries = last_menu.entries
            for i, entry in enumerate(entries):
                g.pr(i, ')', entry.display())
            g.pr(len(last_menu.entries), ')', '[Prev]')
            which = get_input('Which menu entry? > ')
            which = which.strip()
            if not which:
                continue
            try:
                n = int(which)
            except ValueError:
                # Look for accelerator character.
                ch = which[0].lower()
                for n, z in enumerate(entries):
                    if hasattr(z, 'underline') and ch == z.label[z.underline].lower():
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
#@+node:ekr.20150107090324.54: ** class textLog
class textLog(leoFrame.LeoLog):
    #@+others
    #@+node:ekr.20150107090324.58: *3* createControl
    # < < HACK Quiet, oops. >>

    def createControl(self, parentFrame):
        pass

    def setFontFromConfig(self):
        pass  # N/A
    #@+node:ekr.20150107090324.68: *3* finishCreate
    def finishCreate(self):
        pass
    #@+node:ekr.20150107090324.56: *3* put
    def put(self, s, color=None, tabName='Log', from_redirect=False):
        g.pr(s, newline=False)
    #@+node:ekr.20150107090324.57: *3* putnl
    def putnl(self, tabName='log'):
        g.pr('')
    #@+node:ekr.20150107090324.59: *3* setColorFromConfig
    def setColorFromConfig(self):
        pass
    #@+node:ekr.20150107090324.55: *3* setTabBindings
    def setTabBindings(self, tabName):
        pass
    #@-others
#@+node:ekr.20150107090324.60: ** class textTree
class textTree(leoFrame.LeoTree):
    #@+others
    #@+node:ekr.20150107090324.61: *3* setBindings
    def setBindings(self):
        pass
    #@+node:ekr.20150107090324.62: *3* begin/endUpdate & redraw/now
    def redraw(self, p=None):
        self.text_draw_tree()

    redraw_now = redraw
    #@+node:ekr.20150107090324.63: *3* endUpdate
    #@+node:ekr.20150107090324.64: *3* __init__
    def __init__(self, frame):
        # undoc: openWithFileName -> treeWantsFocus -> c.frame.tree.canvas
        self.c = frame.c
        self.canvas = None
        super().__init__(frame)
    #@+node:ekr.20150107090324.65: *3* select
    def select(self, p, scroll=True):
        # TODO Much more here: there's four hooks and all sorts of other things called in the TK version.
        c = self.c
        w = c.frame.body.bodyCtrl
        c.setCurrentPosition(p)
        # This is also where the body-text control is given the text of the selected node...
        # Always do this.    Otherwise there can be problems with trailing hewlines.
        w.setAllText(p.b)
        # and something to do with undo?
    #@+node:ekr.20150107090324.66: *3* editLabel & edit_widget
    def editLabel(self, v, selectAll: bool=False, selection: tuple=None):
        pass  # N/A?

    def edit_widget(self, p):
        return None
    #@+node:ekr.20150107090324.67: *3* text_draw_tree & helper
    def text_draw_tree(self):

        g.pr('--- tree ---')
        self.draw_tree_helper(self.c.rootPosition(), indent=0)

    def draw_tree_helper(self, p, indent):
        for p in p.self_and_siblings():
            if p.hasChildren():
                box = '+' if p.isExpanded() else '-'
            else:
                box = ' '
            icons = '%s%s%s%s' % (
                'b' if p.b else ' ',
                'm' if p.isMarked() else ' ',
                '@' if p.isCloned() else ' ',
                '*' if p.isDirty() else ' ')
            g.pr(" " * indent * 2, icons, box, p.h)
            if p.isExpanded() and p.hasChildren():
                self.draw_tree_helper(p.firstChild(), indent + 1)
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
