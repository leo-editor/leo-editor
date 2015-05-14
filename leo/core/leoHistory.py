# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20150514154159.1: * @file leoHistory.py
#@@first

import leo.core.leoGlobals as g

class NodeHistory:
    '''A class encapsulating knowledge of visited nodes.'''
    #@+others
    #@+node:ekr.20070615131604.1: ** NodeHistory.ctor
    def __init__ (self,c):
        '''Ctor for NodeHistory class.'''
        self.c = c
        self.beadList = []
            # a list of (position,chapter) tuples.
        self.beadPointer = -1
        self.skipBeadUpdate = False
    #@+node:ekr.20070615134813: ** NodeHistory.goNext
    def goNext (self):
        '''Select the next node, if possible.'''
        if self.beadPointer + 1 < len(self.beadList):
            self.beadPointer += 1
            p,chapter = self.beadList[self.beadPointer]
            # g.trace(self.beadPointer,p.h)
            self.select(p,chapter)
    #@+node:ekr.20130915111638.11288: ** NodeHistory.goPrev
    def goPrev (self):
        '''Select the previously visited node, if possible.'''
        if self.beadPointer > 0:
            self.beadPointer -= 1
            p,chapter = self.beadList[self.beadPointer]
            # g.trace(self.beadPointer,p.h)
            self.select(p,chapter)
    #@+node:ekr.20130915111638.11294: ** NodeHistory.select
    def select (self,p,chapter):
        '''
        if p.v exists anywhere, select p in chapter p if possible.
        Otherwise, remove p from self.beadList.
        '''
        trace = False and not g.unitTesting
        c,cc = self.c,self.c.chapterController
        if trace: g.trace(c.positionExists(p),p and p.h)
        if c.positionExists(p):
            self.skipBeadUpdate = True
            try:
                oldChapter = cc.getSelectedChapter()
                if oldChapter != chapter:
                    cc.selectChapterForPosition(p,chapter=chapter)
                c.selectPosition(p) # Calls cc.selectChapterForPosition
            finally:
                self.skipBeadUpdate = False
        else:
            self.beadList = [data for data in self.beadList if data[0].v != p.v]
            self.beadPointer = len(self.beadList)-1
    #@+node:ville.20090724234020.14676: ** NodeHistory.update
    def update (self,p):
        '''Update the beadList.  Called from c.frame.tree.selectHelper.'''
        trace = False and not g.unitTesting
        c,cc = self.c,self.c.chapterController
        if not p or self.skipBeadUpdate:
            # We have been called from self.doNext or self.doPrev.
            # Do *not* update the bead list here!
            return
        # A hack: don't add @chapter nodes.
        # These are selected during the transitions to a new chapter.
        if p.h.startswith('@chapter '):
            return
        # Leo 4.11: remove any duplicates of p.
        self.beadList = [data for data in self.beadList if data[0].v != p.v]
        data = p.copy(),cc.getSelectedChapter()
        self.beadList.append(data)
        # Leo 4.11: always set beadPointer to the end.
        # This works because self.doNext and self.doPrev do not change the beadList.
        self.beadPointer = len(self.beadList)-1
        if trace: g.trace(len(self.beadList),self.beadPointer,p and p.h,g.callers())
    #@-others

#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
