#@+leo-ver=5-thin
#@+node:ekr.20070317085508.1: * @file leoChapters.py
'''Classes that manage chapters in Leo's core.'''
import re
import string
import leo.core.leoGlobals as g
#@+others
#@+node:ekr.20070317085437: ** class ChapterController
class ChapterController(object):
    '''A per-commander controller that manages chapters and related nodes.'''
    #@+others
    #@+node:ekr.20070530075604: *3* Birth
    #@+node:ekr.20070317085437.2: *4*  cc.ctor
    def __init__(self, c):
        '''Ctor for ChapterController class.'''
        self.c = c
        self.chaptersDict = {}
            # Keys are chapter names, values are chapters.
            # Important: chapter names never change,
            # even if their @chapter node changes.
        self.initing = True
            # Fix bug: https://github.com/leo-editor/leo-editor/issues/31
            # True: suppress undo when creating chapters.
        self.re_chapter = None
            # Set where used.
        self.selectedChapter = None
        self.selectChapterLockout = False
            # True: cc.selectChapterForPosition does nothing.
            # Note: Used in qt_frame.py.
        self.tt = None # May be set in finishCreate.
        self.reloadSettings()
        
    def reloadSettings(self):
        c = self.c
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
        trace = False and not g.unitTesting
        if trace: g.trace('(cc)')
        cc = self
        cc.createIcon()
        if trace: g.trace('===== ChapterController.finishCreate')
        cc.setAllChapterNames()
            # Create all chapters.
        # Fix bug: https://github.com/leo-editor/leo-editor/issues/31
        cc.initing = False
        cc.selectChapterByName('main', collapse=False)
            # Always select the main chapter.
            # It can be alarming to open a small chapter in a large .leo file.
    #@+node:ekr.20160411145155.1: *4* cc.makeCommand
    def makeCommand(self, chapterName, binding=None):
        '''Make chapter-select-<chapterName> command.'''
        trace = False and not g.unitTesting
        trace_redef = True
        c, cc = self.c, self
        commandName = 'chapter-select-%s' % chapterName
        inverseBindingsDict = c.k.computeInverseBindingDict()
        if commandName in c.commandsDict:
            if trace and trace_redef:
                g.trace('===== already defined', commandName)
                g.trace('inverse', inverseBindingsDict.get(commandName))
            return
        if trace:
            g.trace('===== defining', commandName, binding, g.callers(1))
            g.trace('inverse', inverseBindingsDict.get(commandName))

        def select_chapter_callback(event,cc=cc,name=chapterName):
            chapter = cc.chaptersDict.get(name)
            if chapter:
                try:
                    cc.selectChapterLockout = True
                    cc.selectChapterByNameHelper(chapter,collapse=True)
                    c.redraw(chapter.p) # 2016/04/20.
                finally:
                    cc.selectChapterLockout = False
            else:
                # Possible, but not likely.
                cc.note('no such chapter: %s' % name)

        # Always bind the command without a shortcut.
        # This will create the command bound to any existing settings.
        bindings = (None, binding) if binding else (None,)
        for shortcut in bindings:
            c.k.registerCommand(commandName, select_chapter_callback, shortcut=shortcut)
    #@+node:ekr.20150509030349.1: *3* cc.cmd (decorator)
    def cmd(name):
        '''Command decorator for the ChapterController class.'''
        # pylint: disable=no-self-argument
        return g.new_cmd_decorator(name, ['c', 'chapterController',])
    #@+node:ekr.20070604165126: *3* cc.selectChapter
    @cmd('chapter-select')
    def selectChapter(self, event=None):
        '''Use the minibuffer to get a chapter name, then create the chapter.'''
        cc, k = self, self.c.k
        names = cc.setAllChapterNames()
        g.es('Chapters:\n' + '\n'.join(names))
        k.setLabelBlue('Select chapter: ')
        k.get1Arg(event, handler=self.selectChapter1, tabList=names)

    def selectChapter1(self, event):
        cc, k = self, self.c.k
        k.clearState()
        k.resetLabel()
        if k.arg:
            cc.selectChapterByName(k.arg)
    #@+node:ekr.20170202061705.1: *3* cc.selectNext/Back
    @cmd('chapter-back')
    def backChapter(self, event=None):
        cc = self
        names = sorted(cc.setAllChapterNames())
        sel_name = cc.selectedChapter.name if cc.selectedChapter else 'main'
        i = names.index(sel_name)
        new_name = names[i-1 if i > 0 else len(names)-1]
        cc.selectChapterByName(new_name)

    @cmd('chapter-next')
    def nextChapter(self, event=None):
        cc = self
        names = sorted(cc.setAllChapterNames())
        sel_name = cc.selectedChapter.name if cc.selectedChapter else 'main'
        i = names.index(sel_name)
        new_name = names[i+1 if i+1 < len(names) else 0]
        cc.selectChapterByName(new_name)
    #@+node:ekr.20070317130250: *3* cc.selectChapterByName & helper
    def selectChapterByName(self, name, collapse=True):
        '''Select a chapter.  Return True if a redraw is needed.'''
        trace = False and not g.unitTesting
        cc = self
        if self.selectChapterLockout:
            if trace: g.trace('lockout', g.callers())
            return
        if g.isInt(name):
            return cc.note('PyQt5 chapters not supported')
        chapter = cc.getChapter(name)
        if not chapter:
            g.es_print('no such @chapter node: %s' % name)
            return
        try:
            cc.selectChapterLockout = True
            cc.selectChapterByNameHelper(chapter, collapse=collapse)
        finally:
            cc.selectChapterLockout = False
    #@+node:ekr.20090306060344.2: *4* cc.selectChapterByNameHelper
    def selectChapterByNameHelper(self, chapter, collapse=True):
        '''Select the chapter, and redraw if necessary.'''
        trace = False and not g.unitTesting
        cc, c = self, self.c
        if trace: g.trace('===== %s' % chapter)
        if not cc.selectedChapter and chapter.name == 'main':
            chapter.p = c.p
            if trace: g.trace('main already selected:', chapter)
            return
        if chapter == cc.selectedChapter:
            chapter.p = c.p
            if trace: g.trace('already selected:', chapter)
            return
        if cc.selectedChapter:
            if trace: g.trace('unselecting:', cc.selectedChapter)
            cc.selectedChapter.unselect()
        else:
            main_chapter = cc.getChapter('main')
            if main_chapter:
                main_chapter.unselect()
        if chapter.p and c.positionExists(chapter.p):
            p = chapter.p
        elif chapter.name == 'main':
            p = chapter.p # Do *not* use c.p here!
        else:
            p = chapter.p = chapter.findRootNode()
            if not p:
                if trace: g.trace('no root node!', chapter)
                return
        if trace: g.trace('select:', chapter)
        chapter.select()
        c.setCurrentPosition(chapter.p)
        # Clean up, but not initially.
        if collapse and chapter.name == 'main':
            for p in c.all_positions():
                # Compare vnodes, not positions.
                if p.v != c.p.v:
                    p.contract()
        c.redraw(chapter.p)
            # Fix part of #265.
            # Redraw only here, when we are sure it is needed.
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
        cc = self
        name = g.toUnicode(name)
        for p in cc.c.all_positions():
            chapterName, binding = self.parseHeadline(p)
            if chapterName == name:
                if trace: g.trace('found @chapter', name)
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
    #@+node:ekr.20160411152842.1: *4* cc.parseHeadline
    def parseHeadline(self, p):
        '''Return the chapter name and key binding for p.h.'''
        if not self.re_chapter:
            self.re_chapter = re.compile(
                r'^@chapter\s+([^@]+)\s*(@key\s*=\s*(.+)\s*)?')
                # @chapter (all up to @) (@key=(binding))?
                # name=group(1), binding=group(3)
        m = self.re_chapter.search(p.h)
        if m:
            chapterName, binding = m.group(1), m.group(3)
            if chapterName:
                chapterName = self.sanitize(chapterName)
            if binding: binding = binding.strip()
        else:
            chapterName = binding = None
        return chapterName, binding
    #@+node:ekr.20160414183716.1: *4* cc.sanitize
    def sanitize(self, s):
        '''Convert s to a safe chapter name.'''
        # Similar to g.sanitize_filename, but simpler.
        result = []
        for ch in s.strip():
            if ch in (string.ascii_letters + string.digits):
                result.append(ch)
            elif ch in ' \t':
                result.append('-')
        s = ''.join(result)
        s = s.replace('--','-')
        return s[: 128]
    #@+node:ekr.20070615075643: *4* cc.selectChapterForPosition
    def selectChapterForPosition(self, p, chapter=None):
        '''
        Select a chapter containing position p.
        New in Leo 4.11: prefer the given chapter if possible.
        Do nothing if p if p does not exist or is in the presently selected chapter.

        Note: this code calls c.redraw() if the chapter changes.
        '''
        trace = False and not g.unitTesting
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
        assert not self.selectChapterLockout
        # New in Leo 5.6: don't call c.redraw immediately.
        c.redraw_later()
    #@+node:ekr.20130915052002.11289: *4* cc.setAllChapterNames
    def setAllChapterNames(self):
        '''Called early and often to discover all chapter names.'''
        c, cc = self.c, self
        # sel_name = cc.selectedChapter and cc.selectedChapter.name or 'main'
        if 'main' not in cc.chaptersDict:
            cc.chaptersDict['main'] = Chapter(c, cc, 'main')
            cc.makeCommand('main')
                # This binds any existing bindings to chapter-select-main.
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
class Chapter(object):
    '''A class representing the non-gui data of a single chapter.'''
    #@+others
    #@+node:ekr.20070317085708.1: *3* chapter.__init__
    def __init__(self, c, chapterController, name):
        self.c = c
        self.cc = cc = chapterController
        self.name = g.toUnicode(name)
        self.selectLockout = False # True: in chapter.select logic.
        # State variables: saved/restored when the chapter is unselected/selected.
        self.p = c.p
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
        c, cc = self.c, self.cc
        if trace: g.trace('-----------', self, 'w:', bool(w))
        cc.selectedChapter = self
        if self.name == 'main':
            return # 2016/04/20
        # Remember the root (it may have changed) for dehoist.
        self.root = root = self.findRootNode()
        if not root:
            # Might happen during unit testing or startup.
            return
        if self.p and not c.positionExists(self.p):
            self.p = p = root.copy()
            if trace: g.trace('switch to root', self)
        # Next, recompute p and possibly select a new editor.
        if w:
            assert w == c.frame.body.wrapper
            assert w.leo_p
            self.p = p = self.findPositionInChapter(w.leo_p) or root.copy()
            if trace: g.trace('recomputed1:', self)
        else:
            # This must be done *after* switching roots.
            self.p = p = self.findPositionInChapter(self.p) or root.copy()
            if trace: g.trace('recomputed2', self)
            if selectEditor:
                # Careful: c.selectPosition would pop the hoist stack.
                w = self.findEditorInChapter(p)
                c.frame.body.selectEditor(w) # Switches text.
                self.p = p # 2016/04/20: Apparently essential.
            if trace: g.trace('recomputed3', self)
        if g.match_word(p.h, 0, '@chapter'):
            if p.hasChildren():
                self.p = p = p.firstChild()
            else:
                # 2016/04/20: Create a dummy first child.
                self.p = p = p.insertAsLastChild()
                p.h = 'New Headline'
                if trace: g.trace('inserted child of @chapter node', p.h)
        c.hoistStack.append(g.Bunch(p=root.copy(), expanded=True))
        # Careful: c.selectPosition would pop the hoist stack.
        if trace: g.trace('done:', self)
        c.setCurrentPosition(p)
        g.doHook('hoist-changed', c=c)
    #@+node:ekr.20070317131708: *4* chapter.findPositionInChapter
    def findPositionInChapter(self, p1, strict=False):
        '''Return a valid position p such that p.v == v.'''
        trace = False and not g.unitTesting
        verbose = False
        c, name = self.c, self.name
        # Bug fix: 2012/05/24: Search without root arg in the main chapter.
        if name == 'main' and c.positionExists(p1):
            return p1
        if not p1:
            if trace and verbose: g.trace('no p1', self)
            return None
        root = self.findRootNode()
        if not root:
            if trace: g.trace('no root:', self)
            return None
        if c.positionExists(p1, root=root.copy()):
            if trace and verbose: g.trace('found', p1.h, 'in', self)
            return p1
        if strict:
            if trace: g.trace('strict test fails', p1.h, 'in', self)
            return None
        if name == 'main':
            theIter = c.all_unique_positions
        else:
            theIter = root.self_and_subtree
        for p in theIter():
            if p.v == p1.v:
                if trace: g.trace('found vnode', p1.h, 'in', self)
                return p.copy()
        if trace: g.trace('not found', p1.h, 'in', self)
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
        # Always try to return to the same position.
        if trace:
            g.trace('======================', self)
            # g.trace('main', self.cc.getChapter('main'))
        self.p = c.p
        if self.name == 'main':
            if trace: g.trace(self)
            return
        root = None
        while c.hoistStack:
            bunch = c.hoistStack.pop()
            root = bunch.p
            if root == self.root:
                if trace: g.trace('found', root.h)
                break
        if trace and not root:
            # Not serious. Can be caused by a user de-hoist.
            g.trace('error unselecting', self)
        # Re-institute the previous hoist.
        if c.hoistStack:
            p = c.hoistStack[-1].p
            if trace: g.trace('re-hoist', p.h, c.positionExists(p))
            # Careful: c.selectPosition would pop the hoist stack.
            c.setCurrentPosition(p)
        else:
            if trace: g.trace('empty hoist-stack')
            p = root or c.p
            c.setCurrentPosition(p)
        if trace: g.trace(c.hoistStack)
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
