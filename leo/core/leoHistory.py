# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20150514154159.1: * @file leoHistory.py
#@@first
import leo.core.leoGlobals as g
assert g
#@+others
#@+node:ekr.20160514120255.1: ** class NodeHistory
class NodeHistory:
    """A class encapsulating knowledge of visited nodes."""
    #@+others
    #@+node:ekr.20070615131604.1: *3* NodeHistory.ctor
    def __init__(self, c):
        """Ctor for NodeHistory class."""
        self.c = c
        self.beadList = []
            # a list of (position,chapter) tuples.
        self.beadPointer = -1
        self.skipBeadUpdate = False
    #@+node:ekr.20160426061203.1: *3* NodeHistory.dump
    def dump(self):
        """Dump the beadList"""
        for i, data in enumerate(self.beadList):
            p, chapter = data
            p = p.h if p else 'no p'
            chapter = chapter.name if chapter else 'main'
            mark = '**' if i == self.beadPointer else '  '
            print(f"{mark} {i} {chapter} {p}")
    #@+node:ekr.20070615134813: *3* NodeHistory.goNext
    def goNext(self):
        """Select the next node, if possible."""
        if self.beadPointer + 1 < len(self.beadList):
            self.beadPointer += 1
            p, chapter = self.beadList[self.beadPointer]
            self.select(p, chapter)
    #@+node:ekr.20130915111638.11288: *3* NodeHistory.goPrev
    def goPrev(self):
        """Select the previously visited node, if possible."""
        if self.beadPointer > 0:
            self.beadPointer -= 1
            p, chapter = self.beadList[self.beadPointer]
            self.select(p, chapter)
    #@+node:ekr.20130915111638.11294: *3* NodeHistory.select
    def select(self, p, chapter):
        """
        Update the history list when selecting p.
        Called only from self.goToNext/PrevHistory
        """
        c, cc = self.c, self.c.chapterController
        if c.positionExists(p):
            self.skipBeadUpdate = True
            try:
                oldChapter = cc.getSelectedChapter()
                if oldChapter != chapter:
                    cc.selectChapterForPosition(p, chapter=chapter)
                c.selectPosition(p) # Calls cc.selectChapterForPosition
            finally:
                self.skipBeadUpdate = False
        # Fix bug #180: Always call self.update here.
        self.update(p, change=False)
    #@+node:ville.20090724234020.14676: *3* NodeHistory.update
    def update(self, p, change=True):
        """
        Update the beadList while p is being selected.
        Called *only* from c.frame.tree.selectHelper.
        """
        c, cc = self.c, self.c.chapterController
        if not p or not c.positionExists(p) or self.skipBeadUpdate:
            return
        # A hack: don't add @chapter nodes.
        # These are selected during the transitions to a new chapter.
        if p.h.startswith('@chapter '):
            return
        # Fix bug #180: handle the change flag.
        aList, found = [], -1
        for i, data in enumerate(self.beadList):
            p2, junk_chapter = data
            if c.positionExists(p2):
                if p == p2:
                    if change:
                        pass # We'll append later.
                    elif found == -1:
                        found = i
                        aList.append(data)
                    else:
                        pass # Remove any duplicate.
                else:
                    aList.append(data)
        if change or found == -1:
            data = p.copy(), cc.getSelectedChapter()
            aList.append(data)
            self.beadPointer = len(aList) - 1
        else:
            self.beadPointer = found
        self.beadList = aList
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
