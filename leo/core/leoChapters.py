#@+leo-ver=5-thin
#@+node:ekr.20070317085508.1: * @file leoChapters.py
"""Classes that manage chapters in Leo's core."""
#@+<< leoChapters imports & annotations >>
#@+node:ekr.20220824080606.1: ** << leoChapters imports & annotations >>
from __future__ import annotations
from collections.abc import Callable
import re
import string
from typing import Any, Optional, TYPE_CHECKING
from leo.core import leoGlobals as g

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent as Event
    from leo.plugins.qt_frame import LeoQtTreeTab
    from leo.core.leoNodes import Position
    from leo.plugins.qt_text import QTextEditWrapper as Wrapper
#@-<< leoChapters imports & annotations >>

#@+others
#@+node:ekr.20150509030349.1: ** cc.cmd (decorator)
def cmd(name: Any) -> Callable:
    """Command decorator for the ChapterController class."""
    return g.new_cmd_decorator(name, ['c', 'chapterController',])
#@+node:ekr.20070317085437: ** class ChapterController
class ChapterController:
    """A per-commander controller that manages chapters and related nodes."""
    #@+others
    #@+node:ekr.20070530075604: *3* Birth
    #@+node:ekr.20070317085437.2: *4*  cc.ctor
    def __init__(self, c: Cmdr) -> None:
        """Ctor for ChapterController class."""
        self.c = c
        # Note: chapter names never change, even if their @chapter node changes.
        self.chaptersDict: dict[str, Any] = {}  # Keys are chapter names, values are chapters.
        self.initing = True  # #31: True: suppress undo when creating chapters.
        self.re_chapter: re.Pattern = None  # Set where used.
        self.selectedChapter = None
        self.selectChapterLockout = False  # True: cc.selectChapterForPosition does nothing.
        self.tt: LeoQtTreeTab = None  # May be set in createChaptersIcon.
        self.reloadSettings()

    def reloadSettings(self) -> None:
        c = self.c
        self.use_tabs = c.config.getBool('use-chapter-tabs')
    #@+node:ekr.20160402024827.1: *4* cc.createIcon
    def createIcon(self) -> None:
        """Create chapter-selection Qt ListBox in the icon area."""
        cc = self
        c = cc.c
        if cc.use_tabs:
            if hasattr(c.frame.iconBar, 'createChaptersIcon'):
                if not cc.tt:
                    cc.tt = c.frame.iconBar.createChaptersIcon()
    #@+node:ekr.20070325104904: *4* cc.finishCreate
    # This must be called late in the init process, after the first redraw.

    def finishCreate(self) -> None:
        """Create the box in the icon area."""
        c, cc = self.c, self
        cc.createIcon()
        cc.setAllChapterNames()  # Create all chapters.
        # #31.
        cc.initing = False
        # Always select the main chapter.
        # It can be alarming to open a small chapter in a large .leo file.
        cc.selectChapterByName('main')
        c.redraw()
    #@+node:ekr.20160411145155.1: *4* cc.makeCommand
    def makeCommand(self, chapterName: str, binding: str = None) -> None:
        """Make chapter-select-<chapterName> command."""
        c, cc = self.c, self
        commandName = f"chapter-select-{chapterName}"
        #
        # For tracing:
        # inverseBindingsDict = c.k.computeInverseBindingDict()
        if commandName in c.commandsDict:
            return

        def select_chapter_callback(event: Event, cc: ChapterController = cc, name: str = chapterName) -> None:
            """
            Select specific chapter.
            """
            # docstring will be replaced below with specific chapterName string
            chapter = cc.chaptersDict.get(name)
            if chapter:
                try:
                    cc.selectChapterLockout = True
                    cc.selectChapterByNameHelper(chapter, collapse=True)
                    c.redraw(chapter.p)  # 2016/04/20.
                finally:
                    cc.selectChapterLockout = False
            elif not g.unitTesting:
                # Possible, but not likely.
                cc.note(f"no such chapter: {name}")

        # Always bind the command without a shortcut.
        # This will create the command bound to any existing settings.

        bindings = (None, binding) if binding else (None,)
        # Replace the docstring for proper details label in minibuffer, etc.
        if chapterName == 'main':
            select_chapter_callback.__doc__ = "Select the main chapter"
        else:
            select_chapter_callback.__doc__ = "Select chapter \"" + chapterName + "\"."
        for shortcut in bindings:
            c.k.registerCommand(commandName, select_chapter_callback, shortcut=shortcut)
    #@+node:ekr.20070604165126: *3* cc: chapter-select
    @cmd('chapter-select')
    def selectChapter(self, event: Event = None) -> None:
        """Prompt for a chapter name and select the given chapter."""
        cc, k = self, self.c.k
        names = cc.setAllChapterNames()
        g.es('Chapters:\n' + '\n'.join(names))
        k.setLabelBlue('Select chapter: ')
        k.get1Arg(event, handler=self.selectChapter1, tabList=names)

    def selectChapter1(self, event: Event) -> None:
        cc, k = self, self.c.k
        k.clearState()
        k.resetLabel()
        if k.arg:
            cc.selectChapterByName(k.arg)
    #@+node:ekr.20170202061705.1: *3* cc: chapter-back/next
    @cmd('chapter-back')
    def backChapter(self, event: Event = None) -> None:
        """Select the previous chapter."""
        cc = self
        names = cc.setAllChapterNames()
        sel_name = cc.selectedChapter.name if cc.selectedChapter else 'main'
        i = names.index(sel_name)
        new_name = names[i - 1 if i > 0 else len(names) - 1]
        cc.selectChapterByName(new_name)

    @cmd('chapter-next')
    def nextChapter(self, event: Event = None) -> None:
        """Select the next chapter."""
        cc = self
        names = cc.setAllChapterNames()
        sel_name = cc.selectedChapter.name if cc.selectedChapter else 'main'
        i = names.index(sel_name)
        new_name = names[i + 1 if i + 1 < len(names) else 0]
        cc.selectChapterByName(new_name)
    #@+node:ekr.20070317130250: *3* cc.selectChapterByName & helper
    def selectChapterByName(self, name: Any) -> None:
        """Select a chapter without redrawing."""
        cc = self
        if self.selectChapterLockout:
            return
        if isinstance(name, int):
            cc.note('PyQt5 chapters not supported')
            return
        chapter = cc.getChapter(name)
        if not chapter:
            if not g.unitTesting:
                g.es_print(f"no such @chapter node: {name}")
            return
        try:
            cc.selectChapterLockout = True
            cc.selectChapterByNameHelper(chapter)
        finally:
            cc.selectChapterLockout = False
    #@+node:ekr.20090306060344.2: *4* cc.selectChapterByNameHelper
    def selectChapterByNameHelper(self, chapter: Any, collapse: bool = True) -> None:
        """Select the chapter."""
        cc, c = self, self.c
        if not cc.selectedChapter and chapter.name == 'main':
            chapter.p = c.p
            return
        if chapter == cc.selectedChapter:
            chapter.p = c.p
            return
        if cc.selectedChapter:
            cc.selectedChapter.unselect()
        else:
            main_chapter = cc.getChapter('main')
            if main_chapter:
                main_chapter.unselect()
        if chapter.p and c.positionExists(chapter.p):
            pass
        elif chapter.name == 'main':
            pass  # Do not use c.p.
        else:
            chapter.p = chapter.findRootNode()
        # #2718: Leave the expansion state of all nodes strictly unchanged!
        #        - c.contractAllHeadlines can change c.p!
        #        - Expanding chapter.p would be confusing and annoying.
        chapter.select()
        c.selectPosition(chapter.p)
        c.redraw()  # #2718.
    #@+node:ekr.20070317130648: *3* cc.Utils
    #@+node:ekr.20070320085610: *4* cc.error/note/warning
    def error(self, s: str) -> None:
        g.error(f"Error: {s}")

    def note(self, s: str, killUnitTest: bool = False) -> None:
        if g.unitTesting:
            if 0:  # To trace cause of failed unit test.
                g.trace('=====', s, g.callers())
            if killUnitTest:
                assert False, s  # noqa
        else:
            g.note(f"Note: {s}")

    def warning(self, s: str) -> None:
        g.es_print(f"Warning: {s}")
    #@+node:ekr.20160402025448.1: *4* cc.findAnyChapterNode
    def findAnyChapterNode(self) -> bool:
        """Return True if the outline contains any @chapter node."""
        cc = self
        for p in cc.c.all_unique_positions():
            if p.h.startswith('@chapter '):
                return True
        return False
    #@+node:ekr.20071028091719: *4* cc.findChapterNameForPosition
    def findChapterNameForPosition(self, p: Position) -> str:
        """Return the name of a chapter containing p or None if p does not exist."""
        cc, c = self, self.c
        if not p or not c.positionExists(p):
            return None
        for name in cc.chaptersDict:
            if name != 'main':
                theChapter = cc.chaptersDict.get(name)
                if theChapter.positionIsInChapter(p):
                    return name
        return 'main'
    #@+node:ekr.20070325093617: *4* cc.findChapterNode
    def findChapterNode(self, name: Any) -> Optional[Position]:
        """
        Return the position of the first @chapter node with the given name
        anywhere in the entire outline.

        All @chapter nodes are created as children of the @chapters node,
        but users may move them anywhere.
        """
        cc = self
        name = g.checkUnicode(name)
        for p in cc.c.all_positions():
            chapterName, binding = self.parseHeadline(p)
            if chapterName == name:
                return p
        return None  # Not an error.
    #@+node:ekr.20070318124004: *4* cc.getChapter
    def getChapter(self, name: Any) -> Any:
        cc = self
        return cc.chaptersDict.get(name)
    #@+node:ekr.20070318122708: *4* cc.getSelectedChapter
    def getSelectedChapter(self) -> Any:
        cc = self
        return cc.selectedChapter
    #@+node:ekr.20070605124356: *4* cc.inChapter
    def inChapter(self) -> bool:
        cc = self
        theChapter = cc.getSelectedChapter()
        return bool(theChapter and theChapter.name != 'main')
    #@+node:ekr.20160411152842.1: *4* cc.parseHeadline
    def parseHeadline(self, p: Position) -> tuple[str, str]:
        """Return the chapter name and key binding for p.h."""
        if not self.re_chapter:
            self.re_chapter = re.compile(
                r'^@chapter\s+([^@]+)\s*(@key\s*=\s*(.+)\s*)?')
                #@verbatim
                # @chapter (all up to @) (@key=(binding))?
                # name=group(1), binding=group(3)
        if m := self.re_chapter.search(p.h):
            chapterName, binding = m.group(1), m.group(3)
            if chapterName:
                chapterName = self.sanitize(chapterName)
            if binding:
                binding = binding.strip()
        else:
            chapterName = binding = None
        return chapterName, binding
    #@+node:ekr.20160414183716.1: *4* cc.sanitize
    def sanitize(self, s: str) -> str:
        """Convert s to a safe chapter name."""
        # Similar to g.sanitize_filename, but simpler.
        result = []
        for ch in s.strip():
            # pylint: disable=superfluous-parens
            if ch in (string.ascii_letters + string.digits):
                result.append(ch)
            elif ch in ' \t':
                result.append('-')
        s = ''.join(result)
        s = s.replace('--', '-')
        return s[:128]
    #@+node:ekr.20070615075643: *4* cc.selectChapterForPosition (calls c.redraw_later)
    def selectChapterForPosition(self, p: Position, chapter: "Chapter" = None) -> None:
        """
        Select a chapter containing position p.
        New in Leo 4.11: prefer the given chapter if possible.
        Do nothing if p if p does not exist or is in the presently selected chapter.

        Note: this code calls c.redraw() if the chapter changes.
        """
        c, cc = self.c, self
        # New in Leo 4.11
        if cc.selectChapterLockout:
            return
        selChapter = cc.getSelectedChapter()
        if not chapter and not selChapter:
            return
        if not p:
            return
        if not c.positionExists(p):
            return
        # New in Leo 4.11: prefer the given chapter if possible.
        theChapter = chapter or selChapter
        if not theChapter:
            return
        # First, try the presently selected chapter.
        firstName = theChapter.name
        if firstName == 'main':
            return
        if theChapter.positionIsInChapter(p):
            cc.selectChapterByName(theChapter.name)
            return
        for name in cc.chaptersDict:
            if name not in (firstName, 'main'):
                theChapter = cc.chaptersDict.get(name)
                if theChapter.positionIsInChapter(p):
                    cc.selectChapterByName(name)
                    break
        else:
            cc.selectChapterByName('main')
        # Fix bug 869385: Chapters make the nav_qt.py plugin useless
        assert not self.selectChapterLockout
        # New in Leo 5.6: don't call c.redraw immediately.
        c.redraw_later()
    #@+node:ekr.20130915052002.11289: *4* cc.setAllChapterNames
    def setAllChapterNames(self) -> list[str]:
        """Called early and often to discover all chapter names."""
        c, cc = self.c, self
        # sel_name = cc.selectedChapter and cc.selectedChapter.name or 'main'
        if 'main' not in cc.chaptersDict:
            cc.chaptersDict['main'] = Chapter(c, cc, 'main')
            # This binds any existing bindings to chapter-select-main.
            cc.makeCommand('main')
        result, seen = ['main'], set()
        for p in c.all_unique_positions():
            chapterName, binding = self.parseHeadline(p)
            if chapterName and p.v not in seen:
                seen.add(p.v)
                result.append(chapterName)
                if chapterName not in cc.chaptersDict:
                    cc.chaptersDict[chapterName] = Chapter(c, cc, chapterName)
                    cc.makeCommand(chapterName, binding)
        return result
    #@-others
#@+node:ekr.20070317085708: ** class Chapter
class Chapter:
    """A class representing the non-gui data of a single chapter."""
    #@+others
    #@+node:ekr.20070317085708.1: *3* chapter.__init__
    def __init__(self, c: Cmdr, chapterController: Any, name: str) -> None:
        self.c = c
        self.cc = cc = chapterController
        self.name: str = g.checkUnicode(name)
        self.selectLockout = False  # True: in chapter.select logic.
        # State variables: saved/restored when the chapter is unselected/selected.
        self.p = c.p
        self.root = self.findRootNode()
        if cc.tt:
            cc.tt.createTab(name)
    #@+node:ekr.20070317085708.2: *3* chapter.__str__ and __repr__
    def __str__(self) -> str:
        """Chapter.__str__"""
        return f"<chapter: {self.name}, p: {repr(self.p and self.p.h)}>"

    __repr__ = __str__
    #@+node:ekr.20110607182447.16464: *3* chapter.findRootNode
    def findRootNode(self) -> Optional[Position]:
        """Return the @chapter node for this chapter."""
        if self.name == 'main':
            return None
        return self.cc.findChapterNode(self.name)
    #@+node:ekr.20070317131205.1: *3* chapter.select & helpers
    def select(self, w: Wrapper = None) -> None:
        """Restore chapter information and redraw the tree when a chapter is selected."""
        if self.selectLockout:
            return
        try:
            tt = self.cc.tt
            self.selectLockout = True
            self.chapterSelectHelper(w)
            if tt:
                # A bad kludge: update all the chapter names *after* the selection.
                tt.setTabLabel(self.name)
        finally:
            self.selectLockout = False
    #@+node:ekr.20070423102603.1: *4* chapter.chapterSelectHelper
    def chapterSelectHelper(self, w: Wrapper = None) -> None:

        c, cc, u = self.c, self.cc, self.c.undoer
        cc.selectedChapter = self
        if self.name == 'main':
            return  # 2016/04/20
        # Remember the root (it may have changed) for dehoist.
        self.root = root = self.findRootNode()
        if not root:
            # Might happen during unit testing or startup.
            return
        if self.p and not c.positionExists(self.p):
            self.p = p = root.copy()
        # Next, recompute p and possibly select a new editor.
        if w:
            assert w == c.frame.body.wrapper
            assert w.leo_p
            self.p = p = self.findPositionInChapter(w.leo_p) or root.copy()
        else:
            # This must be done *after* switching roots.
            self.p = p = self.findPositionInChapter(self.p) or root.copy()
            # Careful: c.selectPosition would pop the hoist stack.
            w = self.findEditorInChapter(p)
            c.frame.body.selectEditor(w)  # Switches text.
            self.p = p  # 2016/04/20: Apparently essential.
        if g.match_word(p.h, 0, '@chapter'):
            if p.hasChildren():
                self.p = p = p.firstChild()
            else:
                bunch = u.beforeInsertNode(p)
                # Create a dummy first child.
                self.p = p = p.insertAsLastChild()
                p.h = 'New Headline'
                u.afterInsertNode(self.p, 'Insert Node', bunch)
        c.hoistStack.append(g.Bunch(p=root.copy(), expanded=True))
        # Careful: c.selectPosition would pop the hoist stack.
        c.setCurrentPosition(p)
        g.doHook('hoist-changed', c=c)
    #@+node:ekr.20070317131708: *4* chapter.findPositionInChapter
    def findPositionInChapter(self, p1: Position, strict: bool = False) -> Optional[Position]:
        """Return a valid position p such that p.v == v."""
        c, name = self.c, self.name
        # Bug fix: 2012/05/24: Search without root arg in the main chapter.
        if name == 'main' and c.positionExists(p1):
            return p1
        if not p1:
            return None
        root = self.findRootNode()
        if not root:
            return None
        if c.positionExists(p1, root=root.copy()):
            return p1
        if strict:
            return None
        if name == 'main':
            theIter = c.all_unique_positions
        else:
            theIter = root.self_and_subtree
        for p in theIter(copy=False):
            if p.v == p1.v:
                return p.copy()
        return None
    #@+node:ekr.20070425175522: *4* chapter.findEditorInChapter
    def findEditorInChapter(self, p: Position) -> Wrapper:
        """return w, an editor displaying position p."""
        chapter, c = self, self.c
        w = c.frame.body.findEditorForChapter(chapter, p)
        if w:
            w.leo_chapter = chapter
            w.leo_p = p and p.copy()
        return w
    #@+node:ekr.20070615065222: *4* chapter.positionIsInChapter
    def positionIsInChapter(self, p: Position) -> bool:
        p2 = self.findPositionInChapter(p, strict=True)
        return bool(p2)
    #@+node:ekr.20070320091806.1: *3* chapter.unselect
    def unselect(self) -> None:
        """Remember chapter info when a chapter is about to be unselected."""
        c = self.c
        # Always try to return to the same position.
        self.p = c.p
        if self.name == 'main':
            return
        root = None
        while c.hoistStack:
            bunch = c.hoistStack.pop()
            root = bunch.p
            if root == self.root:
                break
        # Re-institute the previous hoist.
        if c.hoistStack:
            p = c.hoistStack[-1].p
            # Careful: c.selectPosition would pop the hoist stack.
            c.setCurrentPosition(p)
        else:
            p = root or c.p
            c.setCurrentPosition(p)
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
