# @+leo-ver=5-thin
# @+node:ekr.20150107090324.1: * @file ../plugins/cursesGui.py
"""
A minimal text-oriented gui.

This is *not* a plugin.
"""

# py--lint: disable=arguments-differ
# @+<< cursesGui.py: imports & annotations >>
# @+node:ekr.20150107090324.2: ** << cursesGui.py: imports & annotations >>
# from collections.abc import Callable
import os
from typing import Any
from leo.core import (
    # leoApp,
    leoBridge,
    leoChapters,
    leoCommands,
    leoFrame,
    leoGlobals as g,
    leoGui,
    leoKeys,
    leoMenu,
    leoNodes,
)
from leo.core.leoAPI import StringTextWrapper

get_input = input


# @-<< cursesGui.py: imports & annotations >>
# @+<< TODO >>
# @+node:ekr.20150107090324.3: ** << TODO >>
# @+at
# Things not found in the GUI 'interface' classes (in leoFrame.py, leoGui.py, etc)
# are labeled: # undoc: where the AttributeError comes from other implementations
# of method.
#
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
# Body text selection.
#
# Headline editing?
#
# Random cruft:
#
# Pay attention to being direct and code-terse.
# Not at all user-friendly.
# Comments in the body reflect current status only.
# Ideally, comments in the body go away as the "leoGUI interface" improves.
# @-<< TODO >>
# @+others
# @+node:ekr.20150107090324.4: ** main
def main() -> None:
    """cursesGui2.py: initialize and run."""
    try:
        # Create minimal g.app
        x = leoBridge.BridgeController(
            guiName='nullGui',
            loadPlugins=False,
            readSettings=False,
            silent=False,
            tracePlugins=False,
            useCaches=False,
            verbose=True,
        )
        g.app.gui = TextGui()
        g.app.gui.finishCreate()
        g.app.gui.runMainLoop()
    except Exception:
        g.es('Exception in cursesGui.py')
        g.es_exception()


# @+node:ekr.20150107090324.5: ** underline
def underline(s, idx):
    if idx < 0 or idx > len(s) - 1:
        return s
    return s[:idx] + '&' + s[idx:]


# @+node:ekr.20150107090324.6: ** class TextGui(leoGui.LeoGui): cursesGui.py
class TextGui(leoGui.LeoGui):
    # @+others
    # @+node:ekr.20150107090324.7: *3* __init__
    def __init__(self):
        self.frames = []
        super().__init__("text")
        self.killed = False
        self.c = leoCommands.Commands(fileName=None, gui=self)

    # @+node:ekr.20150107090324.8: *3* createKeyHandlerClass
    def createKeyHandlerClass(self, c):
        return leoKeys.KeyHandlerClass(c)

    # @+node:ekr.20150107090324.9: *3* createLeoFrame
    def createLeoFrame(self, c, title=None) -> Any:
        frame = TextFrame(c, gui=self)
        self.frames.append(frame)
        return frame

    # @+node:ekr.20150107090324.11: *3* destroySelf
    def destroySelf(self):
        self.killed = True

    # @+node:ekr.20150107090324.17: *3* get/set_focus
    def get_focus(self, c):
        pass

    def set_focus(self, c, w):
        pass

    # @+node:ekr.20150107090324.13: *3* isTextWidget (cursesGui.py)
    def isTextWidget(self, w):
        """Return True if w is a Text widget suitable for text-oriented commands."""
        return isinstance(w, StringTextWrapper)

    # @+node:ekr.20150107090324.69: *3* runAskYesNoDialog (cursesGui.py)
    def runAskYesNoDialog(self, c, title, message=None, yes_all=False, no_all=False):
        return 'yes'

    # @+node:ekr.20150107090324.15: *3* runMainLoop
    def runMainLoop(self):
        self.text_run()

    # @+node:ekr.20150107090324.16: *3* runOpenFileDialog (cursesGui2)
    def runOpenFileDialog(
        self,
        c,
        title,
        *,
        filetypes: list[tuple[str, str]],
        defaultextension='',  # Not used.
        startpath=None,
    ) -> str:
        initialdir = g.app.globalOpenDir or g.os_path_abspath(os.getcwd())
        ret = get_input("Open which %s file (from %s?) > " % (repr(filetypes), initialdir))
        return ret

    # @+node:ekr.20150107090324.18: *3* TextGui.text_run & helper
    def text_run(self):
        frame_idx = 0
        while not self.killed:
            # Frames can come and go.
            if frame_idx > len(self.frames) - 1:
                frame_idx = 0
            frame = self.frames[frame_idx]
            g.pr(frame.getTitle())
            s = get_input('Do what? (menu,key,body,frames,tree,quit) > ')
            try:
                self.doChoice(frame, s)
            except Exception:
                g.es_exception()

    # @+node:ekr.20150107090324.19: *4* doChoice
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

    # @+node:ekr.20150107090324.20: *3* widget_name (cursesGui.py)
    def widget_name(self, w):
        if isinstance(w, textBodyCtrl):
            return 'body'
        return leoGui.LeoGui.widget_name(self, w)

    # @-others


# @+node:ekr.20150107090324.21: ** class TextFrame(leoFrame.LeoFrame) cursesGui.py
class TextFrame(leoFrame.LeoFrame):
    # @+others
    # @+node:ekr.20150107090324.22: *3* __init__
    def __init__(self, c, gui):
        super().__init__(c, gui)
        assert self.c == c
        self.title = c.shortFileName() or '<no file>'
        self.top = None

    # @+node:ekr.20150107090324.23: *3* createFirstTreeNode (cursesGui.py)
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

    # @+node:ekr.20150107090324.24: *3* deiconify
    def deiconify(self):
        pass  # N/A

    def lift(self):
        pass  # N/A

    # @+node:ekr.20150107090324.25: *3* destroySelf
    def destroySelf(self):
        pass

    # @+node:ekr.20150107090324.26: *3* finishCreate (cursesGui.py)
    def finishCreate(self):
        c, f = self.c, self
        f.tree = textTree(self)
        f.body = TextBody(frame=self)
        f.log = TextLog(frame=self)
        f.menu = TextLeoMenu(self)
        if f.body.use_chapters:
            c.chapterController = leoChapters.ChapterController(c)
        f.createFirstTreeNode()
        # (*after* setting self.log)
        c.setLog()  # writeWaitingLog hangs without this(!)
        # So updateRecentFiles will update our menus.
        g.app.windowList.append(f)

    # @+node:ekr.20161118195504.1: *3* getFocus
    def getFocus(self):
        return None

    # @+node:ekr.20150107090324.27: *3* setInitialWindowGeometry
    def setInitialWindowGeometry(self):
        pass  # N/A

    # @+node:ekr.20150107090324.28: *3* setMinibufferBindings
    def setMinibufferBindings(self):
        pass

    def setTopGeometry(self, w, h, x, y):
        pass  # N/A

    # @+node:ekr.20150107090324.29: *3* TextFrame.text_key
    def text_key(self):
        c = self.c
        k = c.k
        w = self.body.bodyCtrl
        char = get_input('Keystroke > ')
        if not char:
            return
        g.trace(repr(char))

        # class LeoTypingEvent:
        #     def __init__(self, c, w, char, keysym):
        #         self.c = c
        #         self.char = char
        #         self.keysym = keysym
        #         self.leoWidget = w
        #         self.widget = w

        ### char = key
        ### stroke = c.k.shortcutFromSetting(char)
        ### g.trace('char', repr(char), 'stroke', repr(stroke))
        ### e = LeoTypingEvent(c, w, char, stroke)
        event = leoGui.LeoKeyEvent(c, char=char, w=w)
        k.masterKeyHandler(event=event)

    # @+node:ekr.20150107090324.30: *3* update
    def update(self):
        pass

    def resizePanesToRatio(self, ratio: float, ratio2: float) -> None:
        pass  # N/A

    # @-others


# @+node:ekr.20150107090324.31: ** class TextBody: (leoFrame.LeoBody) cursesGui.py
class TextBody(leoFrame.LeoBody):
    # @+others
    # @+node:ekr.20150107090324.32: *3* TextBody.__init__
    def __init__(self, frame):
        super().__init__(frame)
        c = frame.c
        name = 'body'
        self.bodyCtrl = textBodyCtrl(c, name)
        self.colorizer = leoFrame.NullColorizer(self.c)

    # @+node:ekr.20150107090324.33: *3* TextBody.bind
    # undoc: newLeoCommanderAndFrame -> c.finishCreate -> k.finishCreate ->
    # k.completeAllBindings -> k.makeMasterGuiBinding -> 2156 w.bind ; nullBody

    def bind(self, bindStroke, callback):
        pass

    # @+node:ekr.20150107090324.34: *3* TextBody.setEditorColors
    def setEditorColors(self, bg, fg):
        pass  # N/A

    def createBindings(self, w=None):
        pass

    # @+node:ekr.20150107090324.35: *3* TextBody.text_show
    def text_show(self):
        w = self.bodyCtrl
        g.pr('--- body ---')
        g.pr('ins', w.ins, 'sel', w.sel)
        g.pr(w.s)

    # @-others


# @+node:ekr.20150107090324.36: ** class textBodyCtrl (StringTextWrapper) cursesGui.py
class textBodyCtrl(StringTextWrapper):
    pass


# @+node:ekr.20150107090324.37: ** class textMenuCascade: cursesGui.py
class textMenuCascade:
    def __init__(self, menu, label, underline):
        self.menu = menu
        self.label = label
        self.underline = underline

    # @+others
    # @+node:ekr.20150107090324.39: *3* display
    def display(self):
        ret = underline(self.label, self.underline)
        if not self.menu.entries:
            ret += ' [Submenu with no entries]'
        return ret

    # @-others


# @+node:ekr.20150107090324.40: ** class textMenuEntry: cursesGui.py
class textMenuEntry:
    # @+others
    # @+node:ekr.20150107090324.41: *3* __init__
    def __init__(self, label, underline, accel, callback):
        self.label = label
        self.underline = underline
        self.accel = accel
        self.callback = callback

    # @+node:ekr.20150107090324.42: *3* display
    def display(self):
        return "%s %s" % (
            underline(self.label, self.underline),
            self.accel,
        )

    # @-others


# @+node:ekr.20150107090324.43: ** class textMenuSep: cursesGui.py
class textMenuSep:
    # @+others
    # @+node:ekr.20150107090324.44: *3* display
    def display(self):
        return '-' * 5

    # @-others


# @+node:ekr.20150107090324.45: ** class TextLeoMenu (leoMenu.LeoMenu) cursesGui.py
class TextLeoMenu(leoMenu.LeoMenu):
    # @+others
    # @+node:ekr.20150107090324.46: *3* TextLeoMenu.__init__
    def __init__(self, frame):
        super().__init__(frame)
        self.entries = []
        self.c = frame.c
        self._top_menu = self
        self.createMenusFromTables()

    # @+node:ekr.20150107090324.53: *3* TextLeoMenu.show_menu
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
                else:
                    continue
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

    # @-others


# @+node:ekr.20150107090324.54: ** class TextLog(leoFrame.LeoLog) cursesGui.py
class TextLog(leoFrame.LeoLog):
    # @+others
    # @+node:ekr.20150107090324.68: *3* TextLog.finishCreate (cursesGui.py)
    def finishCreate(self):
        pass

    # @-others


# @+node:ekr.20150107090324.60: ** class textTree: cursesGui.py
class textTree(leoFrame.LeoTree):
    # @+others
    # @+node:ekr.20150107090324.61: *3* setBindings
    def setBindings(self):
        pass

    # @+node:ekr.20150107090324.62: *3* begin/endUpdate & redraw/now
    def redraw(self, p=None):
        self.text_draw_tree()

    redraw_now = redraw

    # @+node:ekr.20150107090324.63: *3* endUpdate
    # @+node:ekr.20150107090324.64: *3* textTree.__init__
    def __init__(self, frame):
        # undoc: openWithFileName -> treeWantsFocus -> c.frame.tree.canvas
        self.c = frame.c
        super().__init__(frame)

    # @+node:ekr.20150107090324.65: *3* select
    def select(self, p, scroll=True):
        # TODO Much more here: there's four hooks and all sorts of other things called in the TK version.
        c = self.c
        w = c.frame.body.bodyCtrl
        c.setCurrentPosition(p)
        # This is also where the body-text control is given the text of the selected node...
        # Always do this.    Otherwise there can be problems with trailing hewlines.
        w.setAllText(p.b)
        # and something to do with undo?

    # @+node:ekr.20150107090324.66: *3* editLabel & headline_wrapper (cursesGui)
    def editLabel(self, v, selectAll: bool = False, selection: tuple = None) -> tuple[None, None]:
        return None, None

    def headline_wrapper(self, p):
        return None

    # @+node:ekr.20150107090324.67: *3* text_draw_tree & helper
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
                '*' if p.isDirty() else ' ',
            )
            g.pr(" " * indent * 2, icons, box, p.h)
            if p.isExpanded() and p.hasChildren():
                self.draw_tree_helper(p.firstChild(), indent + 1)

    # @-others


# @-others

if __name__ == '__main__':
    main()

# @@language python
# @@tabwidth -4
# @-leo
