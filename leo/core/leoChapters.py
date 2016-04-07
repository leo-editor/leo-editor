#@+leo-ver=5-thin
#@+node:ekr.20070317085508.1: * @file leoChapters.py
'''Classes that manage chapters in Leo's core.'''
import leo.core.leoGlobals as g
#@+others
#@+node:ekr.20070317085437: ** class ChapterController
class ChapterController:
    '''A per-commander controller that manages chapters and related nodes.'''
    #@+others
    #@+node:ekr.20070530075604: *3* Birth
    #@+node:ekr.20070317085437.2: *4*  ctor: chapterController
    def __init__(self, c):
        self.c = c
        self.chaptersDict = {}
            # Keys are chapter names, values are chapters.
            # Important: chapter names never change,
            # even if their @chapter node changes.
        self.initing = True
            # Fix bug: https://github.com/leo-editor/leo-editor/issues/31
            # True: suppress undo when creating chapters.
        self.selectedChapter = None
        self.selectChapterLockout = False
            # True: cc.selectChapterForPosition does nothing.
        self.tt = None # May be set in finishCreate.
        self.use_tabs = c.config.getBool('use_chapter_tabs')
    #@+node:ekr.20160402024827.1: *4* cc.createIcon
    def createIcon(self):
        '''Create chapter-selection Qt ListBox in the icon area.'''
        cc = self
        c = cc.c
        if cc.use_tabs:
            if hasattr(c.frame.iconBar, 'createChaptersIcon'):
                if not cc.tt:
                    cc.tt = c.frame.iconBar.createChaptersIcon()
    #@+node:ekr.20070325104904: *4* cc.finishCreate
    # This must be called late in the init process, after the first redraw.

    def finishCreate(self):
        '''Create the box in the icon area.'''
        trace = (False or g.trace_startup) and not g.unitTesting
        if trace: g.es_debug('(cc)')
        cc, c = self, self.c
        cc.createIcon()
        # Create the main chapter
        cc.chaptersDict['main'] = Chapter(c, cc, 'main')
        tag = '@chapter'
        for p in c.all_unique_positions():
            h = p.h
            if g.match_word(h, 0, tag):
                tabName = h[len(tag):].strip()
                if tabName:
                    if cc.chaptersDict.get(tabName):
                        self.error('duplicate chapter name: %s' % tabName)
                    else:
                        cc.chaptersDict[tabName] = Chapter(c, cc, tabName)
        # Fix bug: https://github.com/leo-editor/leo-editor/issues/31
        cc.initing = False
        # Always select the main chapter.
        # It can be alarming to open a small chapter in a large .leo file.
        cc.selectChapterByName('main', collapse=False)
            # 2010/10/09: an important bug fix!
    #@+node:ekr.20150509030349.1: *3* cc.cmd (decorator)
    def cmd(name):
        '''Command decorator for the ChapterController class.'''
        # pylint: disable=no-self-argument
        return g.new_cmd_decorator(name, ['c', 'chapterController',])
    #@+node:ekr.20070604165126: *3* cc.selectChapter
    @cmd('chapter-select')
    def selectChapter(self, event=None):
        '''Use the minibuffer to get a chapter name,
        then create the chapter.'''
        cc, k, tag = self, self.c.k, 'select-chapter'
        state = k.getState(tag)
        if state == 0:
            names = cc.setAllChapterNames()
            g.es('Chapters:\n' + '\n'.join(names))
            k.setLabelBlue('Select chapter: ')
            k.getArg(event, tag, 1, self.selectChapter, tabList=names)
        else:
            k.clearState()
            k.resetLabel()
            if k.arg:
                cc.selectChapterByName(k.arg, create=False)
    #@+node:ekr.20070317130250: *3* cc.selectChapterByName & helper
    def selectChapterByName(self, name, collapse=True, create=True):
        '''Select a chapter.  Return True if a redraw is needed.'''
        trace = False and not g.unitTesting
        cc, c = self, self.c
        if g.isInt(name):
            return cc.note('PyQt5 chapaters not supported')
        chapter = cc.chaptersDict.get(name)
        if chapter:
            cc.selectChapterByNameHelper(chapter, collapse=collapse)
        elif create:
            # There is an @chapter node, but no actual chapter.
            if trace: g.trace('*** creating', name)
            cc.createChapterByName(name, p=c.p, undoType='Create Chapter')
        else:
            # create is False if called from the minibuffer.
            # do nothing if the user mis-types.
            cc.note('no such chapter: %s' % name)
            chapter = cc.chaptersDict.get('main')
            if chapter:
                self.selectChapterByNameHelper(chapter, collapse=collapse)
            else:
                g.trace(g.callers())
                cc.error('no main chapter!')
    #@+node:ekr.20090306060344.2: *4* selectChapterByNameHelper
    def selectChapterByNameHelper(self, chapter, collapse=True):
        trace = False and not g.unitTesting
        cc, c = self, self.c
        if trace:
            g.trace('old: %s, new: %s' % (
                cc.selectedChapter and cc.selectedChapter.name,
                chapter and chapter.name))
        if not cc.selectedChapter and chapter.name == 'main':
            if trace: g.trace('already selected1')
            return
        if chapter == cc.selectedChapter:
            if trace: g.trace('already selected2')
            return
        if cc.selectedChapter:
            cc.selectedChapter.unselect()
        p = chapter.p
        if p and not c.positionExists(p):
            if trace: g.trace('*** switching to root node for', chapter.name)
            chapter.p = chapter.findRootNode()
        chapter.select()
        c.setCurrentPosition(chapter.p)
        cc.selectedChapter = chapter
        # Clean up, but not initially.
        if collapse and chapter.name == 'main':
            for p in c.all_positions():
                # Compare vnodes, not positions.
                if p.v != c.p.v:
                    p.contract()
        # New in Leo 4.6 b2: *do* call c.redraw.
        c.redraw()
    #@+node:ekr.20070317130648: *3* cc.Utils
    #@+node:ekr.20070320085610: *4* cc.error/note/warning
    def error(self, s):
        g.error('Error: %s' % (s))

    def note(self, s, killUnitTest=False):
        if g.unitTesting:
            if 0: # To trace cause of failed unit test.
                g.trace('=====',s, g.callers())
            if killUnitTest:
                assert False, s
        else:
            g.note('Note: %s' % (s))

    def warning(self, s):
        g.es_print('Warning: %s' % (s))
    #@+node:ekr.20160402025448.1: *4* cc.findAnyChapterNode
    def findAnyChapterNode(self):
        '''Return True if the outline contains any @chapter node.'''
        cc = self
        for p in cc.c.all_unique_positions():
            if p.h.startswith('@chapter '):
                return True
        return False
    #@+node:ekr.20071028091719: *4* cc.findChapterNameForPosition
    def findChapterNameForPosition(self, p):
        '''Return the name of a chapter containing p or None if p does not exist.'''
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
    def findChapterNode(self, name):
        '''Return the position of the first @chapter node with the given name
        anywhere in the entire outline.

        All @chapter nodes are created as children of the @chapters node,
        but users may move them anywhere.'''
        trace = False and not g.unitTesting
        name = g.toUnicode(name)
        cc, s = self, '@chapter ' + name
        for p in cc.c.all_positions():
            if p.h == s:
                if trace: g.trace('found', p.h)
                return p
        if trace: g.trace('not found: @chapter', name)
        return None # Not an error.
    #@+node:ekr.20070318124004: *4* cc.getChapter
    def getChapter(self, name):
        cc = self
        return cc.chaptersDict.get(name)
    #@+node:ekr.20070318122708: *4* cc.getSelectedChapter
    def getSelectedChapter(self):
        cc = self
        return cc.selectedChapter
    #@+node:ekr.20070605124356: *4* cc.inChapter
    def inChapter(self):
        cc = self
        theChapter = cc.getSelectedChapter()
        return theChapter and theChapter.name != 'main'
    #@+node:ekr.20070615075643: *4* cc.selectChapterForPosition
    def selectChapterForPosition(self, p, chapter=None):
        '''
        Select a chapter containing position p.
        New in Leo 4.11: prefer the given chapter if possible.
        Do nothing if p if p does not exist or is in the presently selected chapter.

        Note: this code calls c.redraw() if the chapter changes.
        '''
        trace = (False or g.app.debug) and not g.unitTesting
        c, cc = self.c, self
        # New in Leo 4.11
        if cc.selectChapterLockout:
            return
        selChapter = cc.getSelectedChapter()
        if trace: g.trace('***', p.h,
            chapter.name if chapter else 'main',
            selChapter.name if selChapter else 'main',
            g.callers(2))
        if not chapter and not selChapter:
            if trace: g.trace('*** selecting main chapter')
            return 
        if not p:
            if trace: g.trace('no p')
            return
        if not c.positionExists(p):
            if trace: g.trace('does not exist', p.h)
            return
        # New in Leo 4.11: prefer the given chapter if possible.
        theChapter = chapter or selChapter
        if not theChapter:
            return
        # First, try the presently selected chapter.
        firstName = theChapter.name
        # g.trace('===== firstName', firstName)
        if firstName == 'main':
            if trace: g.trace('no search: main chapter:', p.h)
            return
        if theChapter.positionIsInChapter(p):
            if trace: g.trace('position found in chapter:', theChapter.name, p.h)
            cc.selectChapterByName(theChapter.name)
            return
        for name in cc.chaptersDict:
            if name not in (firstName, 'main'):
                theChapter = cc.chaptersDict.get(name)
                if theChapter.positionIsInChapter(p):
                    if trace: g.trace('select:', theChapter.name)
                    cc.selectChapterByName(name)
                    break
        else:
            if trace: g.trace('select main')
            cc.selectChapterByName('main')
        # Fix bug 869385: Chapters make the nav_qt.py plugin useless
        c.redraw_now()
    #@+node:ekr.20130915052002.11289: *4* cc.setAllChapterNames
    def setAllChapterNames(self):
        c, cc, result = self.c, self, []
        sel_name = cc.selectedChapter and cc.selectedChapter.name or 'main'
        tag = '@chapter '
        seen = set()
        for p in c.all_positions():
            if p.h.startswith(tag):
                if p.v not in seen:
                    seen.add(p.v)
                    name = p.h[len(tag):].strip()
                    if name and name != sel_name:
                        result.append(name)
        if 'main' not in result and sel_name != 'main':
            result.append('main')
        result.sort()
        result.insert(0, sel_name)
        return result
    #@+node:ekr.20070610100031: *3* cc.Undo
    #@+node:ekr.20070606075125: *4* cc.afterCreateChapter
    def afterCreateChapter(self, bunch, p):
        cc = self; u = cc.c.undoer
        if u.redoing or u.undoing:
            return
        if cc.initing:
            # Fix bug: https://github.com/leo-editor/leo-editor/issues/31
            return
        bunch.kind = 'create-chapter'
        bunch.newP = p.copy()
        # Set helpers
        bunch.undoHelper = cc.undoInsertChapter
        bunch.redoHelper = cc.redoInsertChapter
        u.pushBead(bunch)
    #@+node:ekr.20070610091608: *4* cc.afterRemoveChapter
    def afterRemoveChapter(self, bunch, p):
        cc = self; u = cc.c.undoer
        if u.redoing or u.undoing: return
        bunch.kind = 'remove-chapter'
        bunch.newP = p.copy()
        # Set helpers
        bunch.undoHelper = cc.undoRemoveChapter
        bunch.redoHelper = cc.redoRemoveChapter
        u.pushBead(bunch)
    #@+node:ekr.20070606082729: *4* cc.beforeCreateChapter
    def beforeCreateChapter(self, p, oldChapterName, newChapterName, undoType):
        cc = self; u = cc.c.undoer
        bunch = u.createCommonBunch(p)
        bunch.oldChapterName = oldChapterName
        bunch.newChapterName = newChapterName
        bunch.savedRoot = None
        bunch.undoType = undoType
        return bunch
    #@+node:ekr.20070610091608.1: *4* cc.beforeRemoveChapter
    def beforeRemoveChapter(self, p, newChapterName, savedRoot):
        cc = self; u = cc.c.undoer
        bunch = u.createCommonBunch(p)
        bunch.newChapterName = newChapterName
        bunch.savedRoot = savedRoot
        bunch.undoType = 'Remove Chapter'
        return bunch
    #@+node:ekr.20070606081341: *4* cc.redoInsertChapter
    def redoInsertChapter(self):
        cc = self; c = cc.c; u = c.undoer
        # g.trace(u.newChapterName,u.oldChapterName,u.p)
        cc.createChapterByName(u.newChapterName, p=u.savedRoot, undoType=u.undoType)
        theChapter = cc.getChapter(u.newChapterName)
        if u.undoType == 'Convert Node To Chapter':
            pass
        elif u.undoType in ('Create Chapter From Node', 'Create Chapter'):
            root = theChapter.findRootNode()
            firstChild = root.firstChild()
            firstChild._unlink()
            firstChild = u.savedRoot.firstChild()
            firstChild._linkAsNthChild(root, 0)
        else:
            return g.trace('Can not happen: bad undoType: %s' % u.undoType)
    #@+node:ekr.20070610100555: *4* cc.redoRemoveChapter
    def redoRemoveChapter(self):
        cc = self; u = cc.c.undoer
        cc.removeChapterByName(u.newChapterName)
        cc.selectChapterByName('main')
    #@+node:ekr.20070606074705: *4* cc.undoInsertChapter
    def undoInsertChapter(self):
        cc = self; c = cc.c; u = c.undoer
        newChapter = cc.getChapter(u.newChapterName)
        bunch = u.beads[u.bead]
        bunch.savedRoot = root = newChapter.findRootNode()
        if u.undoType == 'Convert Node To Chapter':
            p = root.firstChild()
            p.moveAfter(root)
        else:
            pass # deleting the chapter will delete the node.
        cc.removeChapterByName(u.newChapterName)
        cc.selectChapterByName('main')
    #@+node:ekr.20070610100555.1: *4* cc.undoRemoveChapter
    def undoRemoveChapter(self):
        cc = self; c = cc.c; u = c.undoer
        # u.savedRoot is the entire @chapter tree.
        # Link it as the last child of the @chapters node.
        parent = cc.findChaptersNode()
        u.savedRoot._linkAsNthChild(parent, parent.numberOfChildren())
        # Now recreate the chapter.
        name = u.newChapterName
        cc.chaptersDict[name] = Chapter(c, cc, name)
        cc.selectChapterByName(name)
    #@-others
#@+node:ekr.20070317085708: ** class Chapter
class Chapter:
    '''A class representing the non-gui data of a single chapter.'''
    #@+others
    #@+node:ekr.20070317085708.1: *3* chapter.__init__
    def __init__(self, c, chapterController, name):
        self.c = c
        self.cc = cc = chapterController
        self.name = g.toUnicode(name)
        self.selectLockout = False # True: in chapter.select logic.
        # State variables: saved/restored when the chapter is unselected/selected.
        self.p = None
        self.root = self.findRootNode()
        if cc.tt:
            #g.trace('(chapter) calling cc.tt.createTab(%s)' % (name))
            cc.tt.createTab(name)
    #@+node:ekr.20070317085708.2: *3* chapter.__str__ and __repr__
    def __str__(self):
        '''Chapter.__str__'''
        return '<chapter: %s, p: %s>' % (self.name, repr(self.p and self.p.h))

    __repr__ = __str__
    #@+node:ekr.20110607182447.16464: *3* chapter.findRootNode
    def findRootNode(self):
        '''Return the @chapter node for this chapter.'''
        if self.name == 'main':
            return None
        else:
            return self.cc.findChapterNode(self.name)
    #@+node:ekr.20070317131205.1: *3* chapter.select & helpers
    def select(self, w=None, selectEditor=True):
        '''Restore chapter information and redraw the tree when a chapter is selected.'''
        if self.selectLockout:
            return
        try:
            tt = self.cc.tt
            self.selectLockout = True
            self.chapterSelectHelper(w, selectEditor)
            if tt:
                # A bad kludge: update all the chapter names *after* the selection.
                tt.setTabLabel(self.name)
        finally:
            self.selectLockout = False
    #@+node:ekr.20070423102603.1: *4* chapter.chapterSelectHelper
    def chapterSelectHelper(self, w=None, selectEditor=True):
        trace = False and not g.unitTesting
        c, cc, name = self.c, self.cc, self.name
        if trace:
            g.trace('%s exists: %s p: %s' % (
                name, c.positionExists(self.p), self.p))
        cc.selectedChapter = self
        # Remember the root (it may have changed) for dehoist.
        self.root = root = self.findRootNode()
        if not root:
            return
                # root is None for the 'main' chapter.
                # Might also happen during unit testing or startup.
        if self.p and not c.positionExists(self.p):
            self.p = root.copy()
            if trace: g.trace('*** switching to root', self.p)
        p = self.p
        # Next, recompute p and possibly select a new editor.
        if w:
            assert w == c.frame.body.wrapper
            assert w.leo_p
            self.p = p = self.findPositionInChapter(w.leo_p) or root.copy()
            if trace: g.trace('recomputed: %s' % (self.p))
        else:
            # This must be done *after* switching roots.
            self.p = p = self.findPositionInChapter(p) or root.copy()
            if trace: g.trace('recomputed: %s' % (self.p))
            if selectEditor:
                c.selectPosition(p)
                w = self.findEditorInChapter(p)
                c.frame.body.selectEditor(w) # Switches text.
        if name != 'main' and g.match_word(p.h, 0, '@chapter'):
            if p.hasChildren():
                p = p.firstChild()
            else:
                if trace: g.trace('can not happen: no child of @chapter node')
        if name == 'main':
            g.error('can not happen: main chapter has root node')
        else:
            c.hoistStack.append(g.Bunch(p=root.copy(), expanded=True))
        c.selectPosition(p)
        g.doHook('hoist-changed', c=c)
        c.redraw_now(p)
    #@+node:ekr.20070317131708: *4* chapter.findPositionInChapter
    def findPositionInChapter(self, p1, strict=False):
        '''Return a valid position p such that p.v == v.'''
        trace = False and not g.unitTesting
        verbose = False
        c, cc, name = self.c, self.cc, self.name
        if trace:
            g.trace('%s exists: %s p: %s' % (
                self.name, c.positionExists(p1), p1))
        # Bug fix: 2012/05/24: Search without root arg in the main chapter.
        if name == 'main' and c.positionExists(p1):
            return p1
        if not p1:
            if trace and verbose: g.trace('*** no p')
            return None
        root = self.findRootNode()
        if not root:
            if trace: g.trace('no root for ', self.name)
            return None
        if c.positionExists(p1, root=root.copy()):
            if trace and verbose: g.trace('found existing', p1.h)
            return p1
        if strict:
            if trace: g.trace('strict test fails', p1.h)
            return None
        if name == 'main':
            theIter = c.all_unique_positions
        else:
            theIter = root.self_and_subtree
        for p in theIter():
            if p.v == p1.v:
                if trace: g.trace('*** found VNode match', p1.h)
                return p.copy()
        if trace: g.trace('*** not found', p1.h)
        return None
    #@+node:ekr.20070425175522: *4* chapter.findEditorInChapter
    def findEditorInChapter(self, p):
        '''return w, an editor displaying position p.'''
        chapter, c = self, self.c
        w = c.frame.body.findEditorForChapter(chapter, p)
        if w:
            w.leo_chapter = chapter
            w.leo_p = p and p.copy()
        return w
    #@+node:ekr.20070615065222: *4* chapter.positionIsInChapter
    def positionIsInChapter(self, p):
        p2 = self.findPositionInChapter(p, strict=True)
        # g.trace(self.name,'returns',p2)
        return p2
    #@+node:ekr.20070320091806.1: *3* chapter.unselect
    def unselect(self):
        '''Remember chapter info when a chapter is about to be unselected.'''
        trace = False and not g.unitTesting
        c = self.c
        if self.name != 'main':
            root = None
            while c.hoistStack:
                try:
                    bunch = c.hoistStack.pop()
                    root = bunch.p
                    if root == self.root:
                        break
                except Exception:
                    g.trace('c.hoistStack underflow', g.callers())
                    g.es_exception()
                    break
            if not root:
                g.trace('error unselecting', self.name, color='red')
        self.p = c.p
        if trace: g.trace('*** %s, p: %s' % (self.name, self.p.h))
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
