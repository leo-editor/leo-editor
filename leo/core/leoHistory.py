#@+leo-ver=5-thin
#@+node:ekr.20150514154159.1: * @file leoHistory.py
#@+<< leoHistory imports & annotations >>
#@+node:ekr.20221213120137.1: ** << leoHistory imports & annotations >>
from __future__ import annotations
from typing import Any, Optional, TYPE_CHECKING
from leo.core import leoGlobals as g

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoChapters import Chapter
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position

assert g
#@-<< leoHistory imports & annotations >>

#@+others
#@+node:ekr.20160514120255.1: ** class NodeHistory
class NodeHistory:
    """A class encapsulating knowledge of visited nodes."""

    def __init__(self, c: Cmdr) -> None:
        """Ctor for NodeHistory class."""
        self.c = c
        self.beadList: list[tuple[Position, Chapter]] = []
        self.beadPointer = -1
        self.skipBeadUpdate = False

    #@+others
    #@+node:ekr.20160426061203.1: *3* NodeHistory.dump
    def dump(self) -> None:
        """Dump the beadList"""
        c = self.c
        if g.unitTesting or not self.beadList:
            return
        print(f"NodeHisory.beadList: {c.shortFileName()}:")
        for i, data in enumerate(self.beadList):
            p, chapter = data
            p_s = p.h if p else 'no p'
            chapter_s = f"chapter: {chapter.name} " if chapter else ''
            mark_s = '**' if i == self.beadPointer else '  '
            print(f"{mark_s} {chapter_s} {p_s}")
        print('')
    #@+node:ekr.20070615134813: *3* NodeHistory.goNext
    def goNext(self) -> Optional[Position]:
        """Select the next node, if possible."""
        if self.beadPointer + 1 < len(self.beadList):
            self.beadPointer += 1
            p, chapter = self.beadList[self.beadPointer]
            self.select(p, chapter)
            return p
        return None
    #@+node:ekr.20130915111638.11288: *3* NodeHistory.goPrev
    def goPrev(self) -> Optional[Position]:
        """Select the previously visited node, if possible."""
        if self.beadPointer > 0:
            self.beadPointer -= 1
            p, chapter = self.beadList[self.beadPointer]
            self.select(p, chapter)
            return p
        return None
    #@+node:ekr.20130915111638.11294: *3* NodeHistory.select
    def select(self, p: Position, chapter: Any) -> None:
        """
        Update the history list when selecting p.

        Only self.goNext and self.goPrev call this method.
        """
        c, cc = self.c, self.c.chapterController
        if c.positionExists(p):
            self.skipBeadUpdate = True
            try:
                oldChapter = cc.getSelectedChapter()
                if oldChapter != chapter:
                    cc.selectChapterForPosition(p, chapter=chapter)
                c.selectPosition(p)  # Calls cc.selectChapterForPosition
            finally:
                self.skipBeadUpdate = False
        # Fix bug #180: Always call self.update here.
        self.update(p, change=False)
    #@+node:ville.20090724234020.14676: *3* NodeHistory.update
    def update(self, p: Position, change: bool = True) -> None:
        """
        Update the beadList while p is being selected.

        change: True:  The caller is c.frame.tree.selectHelper.
                False: The caller is NodeHistory.select.
        """
        c, cc = self.c, self.c.chapterController
        if not p or not c.positionExists(p) or self.skipBeadUpdate:
            return
        # A hack: don't add @chapter nodes.
        # These are selected during the transitions to a new chapter.
        if p.h.startswith('@chapter '):
            return
        # Fix bug #180: handle the change flag.
        aList: list[tuple[Position, Chapter]] = []
        found = -1
        for i, data in enumerate(self.beadList):
            p2, junk_chapter = data
            if c.positionExists(p2):
                if p == p2:
                    if change:
                        pass  # We'll append later.
                    elif found == -1:
                        found = i
                        aList.append(data)
                    else:
                        pass  # Remove any duplicate.
                else:
                    aList.append(data)
        if change or found == -1:
            data = (p.copy(), cc.getSelectedChapter())
            aList.append(data)
            self.beadPointer = len(aList) - 1
        else:
            self.beadPointer = found
        self.beadList = aList
        # self.dump()
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
