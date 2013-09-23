#@+leo-ver=5-thin
#@+node:ekr.20070317085508.1: * @file leoChapters.py
'''Classes that manage chapters in Leo's core.'''

#@@language python
#@@tabwidth -4
#@@pagewidth 70

import leo.core.leoGlobals as g

# To do later or never: Make body editors persistent. Create @body-editor node?

#@+others
#@+node:ekr.20070317085437: ** class chapterController
class chapterController:

    '''A per-commander controller that manages chapters and related nodes.'''

    #@+others
    #@+node:ekr.20070530075604: *3* Birth
    #@+node:ekr.20070317085437.2: *4*  ctor: chapterController
    def __init__ (self,c):

        self.c = c
        self.chaptersDict = {}
            # Keys are chapter names, values are chapters.
            # Important: chapter names never change,
            # even if their @chapter node changes.
        self.selectedChapter = None
        self.selectChapterLockout = False
            # True: cc.selectChapterForPosition does nothing.
        self.tt = None # May be set in finishCreate.
        self.use_tabs = c.config.getBool('use_chapter_tabs')
    #@+node:ekr.20070325104904: *4* cc.finishCreate
    # This must be called late in the init process, after the first redraw.

    def finishCreate (self):

        '''Find or make the @chapters and @chapter trash nodes.'''
        trace = (False or g.trace_startup) and not g.unitTesting
        if trace: print('cc.finishCreate',g.callers())
        cc,c = self,self.c
        if cc.findChaptersNode():
            if hasattr(c.frame.iconBar,'createChaptersIcon'):
                if not cc.tt:
                    cc.tt = c.frame.iconBar.createChaptersIcon()
        # Create the main chapter
        cc.chaptersDict['main'] = chapter(c,cc,'main')
        tag = '@chapter'
        for p in c.all_unique_positions():
            h = p.h
            # if h.startswith(tag) and not h.startswith('@chapters'):
            if g.match_word(h,0,tag):
                tabName = h[len(tag):].strip()
                if tabName and tabName not in ('main',):
                    if cc.chaptersDict.get(tabName):
                        self.error('duplicate chapter name: %s' % tabName)
                    else:
                        cc.chaptersDict[tabName] = chapter(c,cc,tabName)
        # Always select the main chapter.
        # It can be alarming to open a small chapter in a large .leo file.
        cc.selectChapterByName('main',collapse=False)
            # 2010/10/09: an important bug fix!
    #@+node:ekr.20070317085437.30: *3* Commands (chapters)
    #@+node:ekr.20070317085437.50: *4* cc.cloneNodeToChapter & helper
    def cloneNodeToChapter (self,event=None):

        '''Prompt for a chapter name,
        then clone the selected node to the chapter.'''

        cc,k,tag = self,self.c.k,'clone-node-to-chapter'
        state = k.getState(tag)
        if state == 0:
            names = list(cc.chaptersDict.keys())
            g.es('Chapters:\n' + '\n'.join(names))
            prefix = 'Clone node to chapter: '
            k.setLabelBlue(prefix,protect=True)
            k.getArg(event,tag,1,self.cloneNodeToChapter,prefix=prefix,tabList=names)
        else:
            k.clearState()
            k.resetLabel()
            if k.arg:
                cc.cloneNodeToChapterHelper(k.arg)
    #@+node:ekr.20070604155815.1: *5* cc.cloneToChapterHelper
    def cloneNodeToChapterHelper (self,toChapterName):

        cc,c,p,u,undoType = self,self.c,self.c.p,self.c.undoer,'Clone Node To Chapter'
        # Find the @chapter nodes and related chapter objects.
        fromChapter = cc.getSelectedChapter()
        if not fromChapter:
            return cc.note('no @chapter %s' % (fromChapter and fromChapter.name))
        toChapter = cc.getChapter(toChapterName)
        if not toChapter:
            return cc.note('no @chapter %s' % (toChapter.name))
        # Find the root of each chapter.
        toRoot = toChapter.findRootNode()
        assert toRoot
        if g.match_word(p.h,0,'@chapter'):
            return cc.note('can not clone @chapter node')
        # Open the group undo.
        c.undoer.beforeChangeGroup(toRoot,undoType)
        # Do the clone.  c.clone handles the inner undo.
        clone = c.clone()
        # Do the move.
        undoData2 = u.beforeMoveNode(clone)
        if toChapter.name == 'main':
            clone.moveAfter(toChapter.p)
        else:
            clone.moveToLastChildOf(toRoot)
        u.afterMoveNode(clone,'Move Node',undoData2,dirtyVnodeList=[])
        c.redraw(clone)
        c.setChanged(True)
        # Close the group undo.
        # Only the ancestors of the moved node get set dirty.
        dirtyVnodeList = clone.setAllAncestorAtFileNodesDirty()
        c.undoer.afterChangeGroup(clone,undoType,reportFlag=False,dirtyVnodeList=dirtyVnodeList)
        toChapter.p = clone.copy()
        toChapter.select()
        fromChapter.p = p.copy()
    #@+node:ekr.20070608072116: *4* cc.convertNodeToChapter
    def convertNodeToChapter (self,event=None):

        '''convert-node-to-chapter command.

        Make the selected node into a new chapter, 'in place'.
        That is, create the new @chapter node as the next sibling of the node,
        then move the node as the first child of the new @chapter node.'''

        cc,c,k,p,tag = self,self.c,self.c.k,self.c.p,'convert-node-to-chapter'
        state = k.getState(tag)
        if p.h.startswith('@chapter'):
            cc.note('can not create a new chapter from from an @chapter or @chapters node.')
            return
        if state == 0:
            names = list(cc.chaptersDict.keys())
            k.setLabelBlue('Convert node to chapter: ',protect=True)
            k.getArg(event,tag,1,self.convertNodeToChapter,tabList=names)
        else:
            k.clearState()
            k.resetLabel()
            if k.arg:
                cc.createChapterByName(k.arg,p=p,undoType='Convert Node To Chapter')
    #@+node:ekr.20070317085437.51: *4* cc.copyNodeToChapter & helper
    def copyNodeToChapter (self,event=None):

        '''Prompt for a chapter name,
        then copy the selected node to the chapter.'''

        cc,k,tag = self,self.c.k,'copy-node-to-chapter'
        state = k.getState(tag)
        if state == 0:
            names = list(cc.chaptersDict.keys())
            g.es('Chapters:\n' + '\n'.join(names))
            prefix = 'Copy node to chapter: '
            k.setLabelBlue(prefix,protect=True)
            k.getArg(event,tag,1,self.copyNodeToChapter,prefix=prefix,tabList=names)
        else:
            k.clearState()
            k.resetLabel()
            if k.arg:
                cc.copyNodeToChapterHelper(k.arg)
    #@+node:ekr.20070604155815.2: *5* cc.copyNodeToChapterHelper
    def copyNodeToChapterHelper (self,toChapterName):

        cc,c,p,u,undoType = self,self.c,self.c.p,self.c.undoer,'Copy Node To Chapter'
        if g.match_word(p.h,0,'@chapter'):
            return cc.note('can not copy @chapter node')
        # Get the chapter objects.
        fromChapter = cc.getSelectedChapter()
        if not fromChapter:
            return cc.note('no @chapter %s' % (toChapterName))
        toChapter = cc.getChapter(toChapterName)
        if not toChapter:
            return cc.note('no such chapter: %s' % toChapterName)
        toRoot = toChapter.findRootNode()
        assert toRoot
        # For undo, we treat the copy like a pasted (inserted) node.
        undoData = u.beforeInsertNode(toRoot,pasteAsClone=False,copiedBunchList=[])
        s = c.fileCommands.putLeoOutline()
        p2 = c.fileCommands.getLeoOutline(s)
        p2.moveToLastChildOf(toRoot)
        c.redraw(p2)
        u.afterInsertNode(p2,undoType,undoData)
        c.setChanged(True)
        toChapter.p = p2.copy()
        toChapter.select()
        fromChapter.p = p.copy()
    #@+node:ekr.20070317085437.31: *4* cc.createChapter
    def createChapter (self,event=None):

        '''create-chapter command.

        Create a chapter with a dummy first node.
        
        '''
        cc,k,tag = self,self.c.k,'create-chapter'
        state = k.getState(tag)
        if state == 0:
            names = list(cc.chaptersDict.keys())
            k.setLabelBlue('Create chapter: ',protect=True)
            k.getArg(event,tag,1,self.createChapter,tabList=names)
        else:
            k.clearState()
            k.resetLabel()
            if k.arg:
                cc.createChapterByName(k.arg,p=None,undoType='Create Chapter')
    #@+node:ekr.20070603190617: *4* cc.createChapterByName (common helper)
    def createChapterByName (self,name,p,undoType='Create Chapter'):

        cc,c = self,self.c
        if not name:
            return cc.note('no name')
        oldChapter = cc.getSelectedChapter()
        theChapter = cc.chaptersDict.get(name)
        if theChapter:
            return cc.note('duplicate chapter name: %s' % (name),killUnitTest=True)
        bunch = cc.beforeCreateChapter(c.p,oldChapter.name,name,undoType)
        if undoType == 'Convert Node To Chapter':
            root = p.insertAfter()
            root.initHeadString('@chapter %s' % name)
            p.moveToFirstChildOf(root)
        elif undoType in ('Create Chapter From Node','Create Chapter'):
            # Create the @chapter node.
            # If p exists, clone it as the first child, else create a dummy first child.
            root = cc.getChapterNode(name,p=p)
        else:
            return g.trace('Can not happen: bad undoType: %s' % undoType)
        cc.chaptersDict[name] = chapter(c,cc,name)
        cc.selectChapterByName(name)
        cc.afterCreateChapter(bunch,c.p)
        return True
    #@+node:ekr.20070607092909: *4* cc.createChapterFromNode
    def createChapterFromNode (self,event=None):

        '''create-chapter-from-node command.

        Create a chapter whose first node is a clone of the presently selected node.'''

        cc,c,k,p,tag = self,self.c,self.c.k,self.c.p,'create-chapter-from-node'
        state = k.getState(tag)
        if p.h.startswith('@chapter'):
            cc.note('can not create a new chapter from from an @chapter or @chapters node.')
            return
        if state == 0:
            names = list(cc.chaptersDict.keys())
            k.setLabelBlue('Create chapter from node: ',protect=True)
            k.getArg(event,tag,1,self.createChapterFromNode,tabList=names)
        else:
            k.clearState()
            k.resetLabel()
            if k.arg:
                cc.createChapterByName(k.arg,p=p,undoType='Create Chapter From Node')
    #@+node:ekr.20070604155815.3: *4* cc.moveNodeToChapter & helper
    def moveNodeToChapter (self,event=None):

        '''Prompt for a chapter name,
        then move the selected node to the chapter.'''

        cc,k,tag = self,self.c.k,'move-node-to-chapter'
        state = k.getState(tag)
        if state == 0:
            names = list(cc.chaptersDict.keys())
            g.es('Chapters:\n' + '\n'.join(names))
            prefix = 'Move node to chapter: '
            k.setLabelBlue(prefix,protect=True)
            k.getArg(event,tag,1,self.moveNodeToChapter,prefix=prefix,tabList=names)
        else:
            k.clearState()
            k.resetLabel()
            if k.arg:
                cc.moveNodeToChapterHelper(k.arg)
    #@+node:ekr.20070317085437.52: *5* cc.moveNodeToChapterHelper (works)
    def moveNodeToChapterHelper (self,toChapterName):

        cc,c,p,u = self,self.c,self.c.p,self.c.undoer
        undoType = 'Move Node To Chapter'
        if g.match_word(p.h,0,'@chapter'):
            return cc.note('can not move @chapter node to another chapter')
        # Get the chapter objects.
        fromChapter = cc.getSelectedChapter()
        toChapter = cc.getChapter(toChapterName)
        if not fromChapter:
            return cc.note('no selected chapter')
        if not fromChapter:
            return cc.note('no chapter: %s' % (toChapterName))
        # Get the roots
        fromRoot,toRoot = fromChapter.findRootNode(),toChapter.findRootNode()
        if not fromRoot:
            return cc.note('no @chapter %s' % (fromChapter.name))
        if not toRoot:
            return cc.note('no @chapter %s' % (toChapter.name))
        if toChapter.name == 'main':
            sel = (p.threadBack() != fromRoot and p.threadBack()) or p.nodeAfterTree()
        else:
            sel = p.threadBack() or p.nodeAfterTree()
        if sel:
            # Get 'before' undo data.
            inAtIgnoreRange = p.inAtIgnoreRange()
            undoData = u.beforeMoveNode(p)
            dirtyVnodeList = p.setAllAncestorAtFileNodesDirty()
            # Do the move.
            if toChapter.name == 'main':
                p.moveAfter(toChapter.p)
            else:
                p.moveToLastChildOf(toRoot)
            c.redraw(sel)
            c.setChanged(True)
            # Do the 'after' undo operation.
            if inAtIgnoreRange and not p.inAtIgnoreRange():
                # The moved nodes have just become newly unignored.
                dirtyVnodeList2 = p.setDirty() # Mark descendent @thin nodes dirty.
                dirtyVnodeList.extend(dirtyVnodeList2)
            else: # No need to mark descendents dirty.
                dirtyVnodeList2 = p.setAllAncestorAtFileNodesDirty()
                dirtyVnodeList.extend(dirtyVnodeList2)
            u.afterMoveNode(p,undoType,undoData,dirtyVnodeList=dirtyVnodeList)
        if sel:
            toChapter.p = p.copy()
            toChapter.select()
            fromChapter.p = sel.copy()
        else:
            cc.note('can not move the last remaining node of a chapter.')
    #@+node:ekr.20070317085437.40: *4* cc.removeChapter & helper
    def removeChapter (self,event=None):

        '''Prompt for the name of a chapter, then remove it.'''

        cc = self
        theChapter = cc.selectedChapter
        if not theChapter: return
        name = theChapter.name
        if name == 'main':
            return cc.note('can not remove the main chapter')
        else:
            cc.removeChapterByName(name)
    #@+node:ekr.20070606075434: *5* cc.removeChapterByName
    def removeChapterByName (self,name):

        cc,c,tt = self,self.c,self.tt
        theChapter = cc.chaptersDict.get(name)
        if not theChapter:
            return
        root = theChapter.findRootNode()
        if root:
            savedRoot = root
            bunch = cc.beforeRemoveChapter(c.p,name,savedRoot)
            cc.deleteChapterNode(name)
            if tt:tt.destroyTab(name)
            cc.selectChapterByName('main')
            cc.afterRemoveChapter(bunch,c.p)
        del cc.chaptersDict[name]
            # Do this after calling deleteChapterNode.
        cc.note('Removed chapter %s' % name)
        c.redraw()
    #@+node:ekr.20070317085437.41: *4* cc.renameChapter & helper
    def renameChapter (self,event=None,newName=None): # newName is for unitTesting.

        '''Use the minibuffer to get a new name for the present chapter.'''

        cc,c,k,tag = self,self.c,self.c.k,'rename-chapter'
        state = k.getState(tag)
        if state == 0 and not newName:
            chapter = cc.selectedChapter
            if not chapter: return
            if chapter.name == 'main':
                return cc.note('can not rename the main chapter')
            else:
                names = list(cc.chaptersDict.keys())
                prefix = 'Rename this chapter: '
                k.setLabelBlue(prefix,protect=True)
                k.getArg(event,tag,1,self.renameChapter,prefix=prefix,tabList=names)
        else:
            k.clearState()
            k.resetLabel()
            chapter = cc.selectedChapter
            if newName: k.arg = newName # A hack for unit testing.
            if chapter and k.arg and k.arg != chapter.name:
                cc.renameChapterByName(k.arg)
    #@+node:ekr.20110608135633.16553: *5* cc.renameChapterByName
    def renameChapterByName (self,newName):

        cc,c,d,tt = self,self.c,self.chaptersDict,self.tt
        chapter = cc.selectedChapter
        oldName = chapter.name
        del d [oldName]
        d [newName] = chapter
        chapter.name = newName
        root = cc.findChapterNode(oldName)
        if root:
            root.initHeadString('@chapter %s' % newName)
            if tt:
                try:
                    tt.lockout = True
                    tt.destroyTab(oldName)
                    tt.createTab(newName)
                    tt.setTabLabel(newName)
                finally:
                    tt.lockout = False
            cc.selectChapterByName(newName) # Necessary.
            # cc.note('renamed "%s" to "%s"' % (oldName,newName))
        else:
            cc.note('no @chapter %s' % (oldName))
    #@+node:ekr.20070604165126: *4* cc.selectChapter & helper
    def selectChapter (self,event=None):

        '''Use the minibuffer to get a chapter name,
        then create the chapter.'''

        cc,k,tag = self,self.c.k,'select-chapter'
        state = k.getState(tag)
        if state == 0:
            names = list(cc.chaptersDict.keys())
            g.es('Chapters:\n' + '\n'.join(names))
            prefix = 'Select chapter: '
            k.setLabelBlue(prefix,protect=True)
            k.getArg(event,tag,1,self.selectChapter,prefix=prefix,tabList=names)
        else:
            k.clearState()
            k.resetLabel()
            if k.arg:
                cc.selectChapterByName(k.arg,create=False)
    #@+node:ekr.20070317130250: *5* cc.selectChapterByName & helper
    def selectChapterByName (self,name,collapse=True,create=True):

        '''Select a chapter.  Return True if a redraw is needed.'''

        trace = True and not g.unitTesting
        cc,c = self,self.c
        chapter = cc.chaptersDict.get(name)
        if chapter:
            cc.selectChapterByNameHelper(chapter,collapse=collapse)
        elif create:
            # There is an @chapter node, but no actual chapter.
            if trace: g.trace('*** creating',name)
            cc.createChapterByName(name,p=c.p,undoType='Create Chapter')
        else:
            # create is False if called from the minibuffer.
            # do nothing if the user mis-types.
            cc.note('no such chapter: %s' % name)
            chapter = cc.chaptersDict.get('main')
            if chapter:
                self.selectChapterByNameHelper(chapter,collapse=collapse)
            else:
                g.trace(g.callers())
                cc.error('no main chapter!')
    #@+node:ekr.20090306060344.2: *6* selectChapterByNameHelper
    def selectChapterByNameHelper (self,chapter,collapse=True):

        trace = False and not g.unitTesting
        cc,c = self,self.c
        if trace:
            g.trace('old: %s, new: %s' % (
                cc.selectedChapter and cc.selectedChapter.name,
                chapter and chapter.name))
        if chapter == cc.selectedChapter:
            if trace: g.trace('already selected')
            return
        if cc.selectedChapter:
            cc.selectedChapter.unselect()
        p = chapter.p
        if p and not c.positionExists(p):
            if trace: g.trace('*** switching to root node for',chapter.name)
            ### p = c.rootPosition()
            chapter.p = chapter.findRootNode()
        chapter.select()
        c.setCurrentPosition(chapter.p)
        cc.selectedChapter = chapter
        # Clean up, but not initially.
        if collapse and chapter.name == 'main':
            for p in c.all_unique_positions():
                # Compare vnodes, not positions.
                if p.v != c.p.v:
                    p.contract()
        # New in Leo 4.6 b2: *do* call c.redraw.
        c.redraw()
    #@+node:ekr.20070511081405: *3* Creating/deleting/finding chapter nodes
    #@+node:ekr.20070325101652: *4* cc.createChaptersNode
    def createChaptersNode (self):

        cc = self ; c = cc.c
        root = c.rootPosition()

        # Use a position method to avoid undo logic.
        p = root.insertAsLastChild()
        p.initHeadString('@chapters')
        p.moveToRoot(oldRoot=root)
        assert(p.v.fileIndex)
        c.setChanged(True)

        if hasattr(c.frame.iconBar,'createChaptersIcon'):
            if not cc.tt:
                cc.tt = c.frame.iconBar.createChaptersIcon()

        return p
    #@+node:ekr.20070325063303.2: *4* cc.createChapterNode
    def createChapterNode (self,chapterName,p=None):

        '''Create an @chapter node for the named chapter.
        Use a clone p for the first child, or create a first child if p is None.'''

        cc = self ; c = cc.c

        chaptersNode = cc.findChaptersNode() or cc.createChaptersNode()

        # Use a position method to avoid undo logic.
        root = chaptersNode.insertAsLastChild()
        root.initHeadString('@chapter ' + chapterName)
        root.moveToFirstChildOf(chaptersNode)

        if p and not p.h.startswith('@chapter'):
            # Clone p and move it to the first child of the root.
            clone = p.clone()
            clone.moveToFirstChildOf(root)
        else:
            cc.createChild(root,'%s node 1' % chapterName)

        c.setChanged(True)
        return root
    #@+node:ekr.20070509081915.1: *4* cc.createChild
    def createChild (self,parent,s):

        '''Create a child node of parent without changing the undo stack.
        set the headString of the new node to s.'''

        c = self.c
        p = parent.insertAsLastChild()
        p.initHeadString(s)
        c.setChanged(True)

        return p
    #@+node:ekr.20070325063303.4: *4* cc.deleteChapterNode
    def deleteChapterNode (self,chapterName):

        '''Delete the @chapter with the given name.'''

        cc = self ; c = cc.c
        root = cc.findChapterNode(chapterName)

        if root:
            # Do not involve undo logic.
            c.setCurrentPosition(root)
            root.doDelete()
            # The chapter selection logic will select a new node.
            c.setChanged(True)
        else:
            cc.note('no @chapter %s' % (chapterName))
    #@+node:ekr.20070325094401: *4* cc.findChaptersNode
    def findChaptersNode (self):

        '''Return the position of the @chapters node.'''

        cc = self ; c = cc.c

        for p in c.all_unique_positions():
            if p.h == '@chapters':
                return p.copy()

        return None # Not an error
    #@+node:ekr.20070325093617: *4* cc.findChapterNode
    def findChapterNode (self,name):

        '''Return the position of the first @chapter node with the given name
        anywhere in the entire outline.

        All @chapter nodes are created as children of the @chapters node,
        but users may move them anywhere.'''

        trace = False and not g.unitTesting
        cc,s = self,'@chapter ' + name
        for p in cc.c.all_positions():
            if p.h == s:
                if trace: g.trace('found',p.h)
                return p
        if trace: g.trace('not found: @chapter',name)
        return None # Not an error.
    #@+node:ekr.20070325115102: *4* cc.getChapterNode (creates if necessary)
    def getChapterNode (self,chapterName,p=None):

        '''Return the position of the @chapter node with the given name.'''

        cc = self ; c = cc.c

        if chapterName == 'main':
            return c.rootPosition()
        else:
            val = (
                cc.findChapterNode(chapterName) or
                cc.createChapterNode(chapterName,p=p))
            return val
    #@+node:ekr.20070317130648: *3* Utils
    #@+node:ekr.20070320085610: *4* cc.error/note/warning
    def error (self,s):

        g.error('Error: %s' % (s))

    def note (self,s,killUnitTest=False):

        if g.unitTesting:
            if killUnitTest:
                assert False,s
        else:
            g.note('Note: %s' % (s))

    def warning (self,s):

        g.es_print('Warning: %s' % (s))

    #@+node:ekr.20070605124356: *4* cc.inChapter
    def inChapter (self):

        cc = self
        theChapter = cc.getSelectedChapter()
        return theChapter and theChapter.name != 'main'
    #@+node:ekr.20070318124004: *4* cc.getChapter
    def getChapter(self,name):

        cc = self
        return cc.chaptersDict.get(name)
    #@+node:ekr.20070318122708: *4* cc.getSelectedChapter
    def getSelectedChapter (self):

        cc = self
        return cc.selectedChapter
    #@+node:ekr.20070510064813: *4* cc.printChaptersTree
    def printChaptersTree(self,tag=''):

        cc = self ; c = cc.c

        chaptersNode = cc.findChaptersNode()

        for p in c.rootPosition().self_and_siblings():
            for p2 in p.self_and_subtree():
                if p2 == chaptersNode:
                    inTree = True ; break
        else:
            inTree = False

        g.trace('-'*40)

        full = True

        if chaptersNode and full:
            g.pr('@chapters tree...','(in main tree: %s)' % inTree)
            for p in chaptersNode.self_and_subtree():
                g.pr('.'*p.level(),p.v)
    #@+node:ekr.20070615075643: *4* cc.selectChapterForPosition
    def selectChapterForPosition (self,p,chapter=None):

        '''
        Select a chapter containing position p.
        New in Leo 4.11: prefer the given chapter if possible.
        Do nothing if p if p does not exist or is in the presently selected chapter.

        Note: this code calls c.redraw() if the chapter changes.
        '''

        trace = False and not g.unitTesting
        c,cc = self.c,self
        # New in Leo 4.11
        if cc.selectChapterLockout:
            return
        selChapter = cc.getSelectedChapter()
        if trace: g.trace('***',p.h,
            chapter.name if chapter else None,
            selChapter.name if selChapter else None,
            g.callers())
        if not p:
            if trace: g.trace('no p')
            return
        if not c.positionExists(p):
            if trace: g.trace('does not exist',p.h) 
            return
        # New in Leo 4.11: prefer the given chapter if possible.
        theChapter = chapter or selChapter
        if not theChapter:
            return
        # First, try the presently selected chapter.
        firstName = theChapter.name
        if firstName == 'main':
            if trace: g.trace('no search: main chapter:',p.h)
            return
        if theChapter.positionIsInChapter(p):
            if trace: g.trace('position found in chapter:',theChapter.name,p.h)
            cc.selectChapterByName(theChapter.name) ### New.
            return
        for name in cc.chaptersDict:
            if name not in (firstName,'main'):
                theChapter = cc.chaptersDict.get(name)
                if theChapter.positionIsInChapter(p):
                    if trace: g.trace('select:',theChapter.name)
                    cc.selectChapterByName(name)
                    break
        else:
            if trace: g.trace('select main')
            cc.selectChapterByName('main')
        # Fix bug 869385: Chapters make the nav_qt.py plugin useless
        c.redraw_now()
    #@+node:ekr.20130915052002.11289: *4* cc.setAllChapterNames (New in Leo 4.11)
    def setAllChapterNames(self):
        
        cc,result = self,[]
        sel_name = cc.selectedChapter and cc.selectedChapter.name or 'main'
        root = cc.findChaptersNode()
        if root:
            tag = '@chapter '
            for p in root.subtree():
                if p.h.startswith(tag):
                    name = p.h[len(tag):].strip()
                    if name and name != sel_name:
                        result.append(name)
        if 'main' not in result and sel_name != 'main':
            result.append('main')
        result.sort()
        result.insert(0,sel_name)
        return result
    #@+node:ekr.20071028091719: *4* cc.findChapterNameForPosition
    def findChapterNameForPosition (self,p):

        '''Return the name of a chapter containing p or None if p does not exist.'''
        cc,c = self,self.c
        if not p or not c.positionExists(p):
            return None
        for name in cc.chaptersDict:
            if name != 'main':
                theChapter = cc.chaptersDict.get(name)
                if theChapter.positionIsInChapter(p):
                    return name
        else:
            return 'main'
    #@+node:ekr.20070610100031: *3* Undo
    #@+node:ekr.20070606075125: *4* afterCreateChapter
    def afterCreateChapter (self,bunch,p):

        cc = self ; u = cc.c.undoer
        if u.redoing or u.undoing: return

        bunch.kind = 'create-chapter'
        bunch.newP = p.copy()

        # Set helpers
        bunch.undoHelper = cc.undoInsertChapter
        bunch.redoHelper = cc.redoInsertChapter

        u.pushBead(bunch)
    #@+node:ekr.20070610091608: *4* afterRemoveChapter
    def afterRemoveChapter (self,bunch,p):

        cc = self ; u = cc.c.undoer
        if u.redoing or u.undoing: return

        bunch.kind = 'remove-chapter'
        bunch.newP = p.copy()

        # Set helpers
        bunch.undoHelper = cc.undoRemoveChapter
        bunch.redoHelper = cc.redoRemoveChapter

        u.pushBead(bunch)
    #@+node:ekr.20070606082729: *4* beforeCreateChapter
    def beforeCreateChapter (self,p,oldChapterName,newChapterName,undoType):

        cc = self ; u = cc.c.undoer

        bunch = u.createCommonBunch(p)

        bunch.oldChapterName = oldChapterName
        bunch.newChapterName = newChapterName
        bunch.savedRoot = None
        bunch.undoType = undoType

        return bunch
    #@+node:ekr.20070610091608.1: *4* beforeRemoveChapter
    def beforeRemoveChapter (self,p,newChapterName,savedRoot):

        cc = self ; u = cc.c.undoer

        bunch = u.createCommonBunch(p)

        bunch.newChapterName = newChapterName
        bunch.savedRoot = savedRoot
        bunch.undoType = 'Remove Chapter'

        return bunch
    #@+node:ekr.20070606081341: *4* redoInsertChapter
    def redoInsertChapter (self):

        cc = self ; c = cc.c ; u = c.undoer

        # g.trace(u.newChapterName,u.oldChapterName,u.p)

        cc.createChapterByName(u.newChapterName,p=u.savedRoot,undoType=u.undoType)
        theChapter = cc.getChapter(u.newChapterName)

        if u.undoType == 'Convert Node To Chapter':
            pass
        elif u.undoType in ('Create Chapter From Node','Create Chapter'):
            root = theChapter.findRootNode()
            firstChild = root.firstChild()
            firstChild._unlink()
            firstChild = u.savedRoot.firstChild()
            firstChild._linkAsNthChild(root,0)
        else:
            return g.trace('Can not happen: bad undoType: %s' % u.undoType)
    #@+node:ekr.20070610100555: *4* redoRemoveChapter
    def redoRemoveChapter (self):

        cc = self ; u = cc.c.undoer

        cc.removeChapterByName(u.newChapterName)
        cc.selectChapterByName('main')
    #@+node:ekr.20070606074705: *4* undoInsertChapter
    def undoInsertChapter (self):

        cc = self ; c = cc.c ; u = c.undoer

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
    #@+node:ekr.20070610100555.1: *4* undoRemoveChapter
    def undoRemoveChapter (self):

        cc = self ; c = cc.c ; u = c.undoer

        # u.savedRoot is the entire @chapter tree.
        # Link it as the last child of the @chapters node.
        parent = cc.findChaptersNode()
        u.savedRoot._linkAsNthChild(parent,parent.numberOfChildren())

        # Now recreate the chapter.
        name = u.newChapterName
        cc.chaptersDict[name] = chapter(c,cc,name)
        cc.selectChapterByName(name)
    #@-others
#@+node:ekr.20070317085708: ** class chapter
class chapter:

    '''A class representing the non-gui data of a single chapter.'''

    #@+others
    #@+node:ekr.20070317085708.1: *3*  ctor: chapter
    def __init__ (self,c,chapterController,name):

        self.c = c 
        self.cc = cc = chapterController
        self.name = name
        self.selectLockout = False # True: in chapter.select logic.
        # State variables: saved/restored when the chapter is unselected/selected.
        if self.name == 'main':
            self.p = c.p or c.rootPosition()
        else:
            self.p = None # Set later.
            root = self.findRootNode()
        if cc.tt:
            # g.trace('(chapter) calling cc.tt.createTab(%s)' % (name))
            cc.tt.createTab(name)
    #@+node:ekr.20070317085708.2: *3* __str__ and __repr__(chapter)
    def __str__ (self):

        # return '<chapter id: %s name: %s p: %s>' % (
            # id(self),
            # self.name,
            # self.p and self.p.h or '<no p>')

        return '<chapter: %s, p: %s>' % (self.name,repr(self.p and self.p.h))

    __repr__ = __str__
    #@+node:ekr.20070325155208.1: *3* chapter.error
    def error (self,s):

        self.cc.error(s)
    #@+node:ekr.20110607182447.16464: *3* chapter.findRootNode
    def findRootNode (self):

        '''Return the @chapter node for this chapter.'''

        if self.name == 'main':
            return self.c.rootPosition()
        else:
            return self.cc.findChapterNode(self.name)
    #@+node:ekr.20070317131205.1: *3* chapter.select & helpers
    def select (self,w=None,selectEditor=True):

        '''Restore chapter information and redraw the tree when a chapter is selected.'''

        if self.selectLockout:
            return
        try:
            tt = self.cc.tt
            self.selectLockout = True
            self.chapterSelectHelper(w,selectEditor)
            if tt:
                # A bad kludge: update all the chapter names *after* the selection.
                ### tt.setNames()
                tt.setTabLabel(self.name)
        finally:
            self.selectLockout = False
    #@+node:ekr.20070423102603.1: *4* chapter.chapterSelectHelper
    def chapterSelectHelper (self,w=None,selectEditor=True):

        trace = False and not g.unitTesting
        c,cc,name = self.c,self.cc,self.name
        if trace:
            g.trace('%s exists: %s p: %s' % (
                name,c.positionExists(self.p),self.p))
        cc.selectedChapter = self
        root = self.findRootNode()
        if self.p and not c.positionExists(self.p):
            self.p = root.copy()
            if trace: g.trace('*** switching to root',self.p)
        p = self.p
        # Next, recompute p and possibly select a new editor.
        if w:
            assert w == c.frame.body.bodyCtrl
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
        if name != 'main' and g.match_word(p.h,0,'@chapter'):
            if p.hasChildren():
                p = p.firstChild()
            else:
                if trace: g.trace('can not happen: no child of @chapter node')
        chaptersNode = cc.findChaptersNode()
        if name == 'main' and chaptersNode:
            chaptersNode.contract()
        if name != 'main':
            c.hoistStack.append(g.Bunch(p=root and root.copy(),expanded=True))
        c.selectPosition(p)
        g.doHook('hoist-changed',c=c)
        c.redraw_now(p)
    #@+node:ekr.20070317131708: *4* chapter.findPositionInChapter
    def findPositionInChapter (self,p1,strict=False):

        '''Return a valid position p such that p.v == v.'''

        trace = False and not g.unitTesting
        verbose = False
        c,cc,name = self.c,self.cc,self.name
        if trace:
            g.trace('%s exists: %s p: %s' % (
                self.name,c.positionExists(p1),p1))
        # Bug fix: 2012/05/24: Search without root arg in the main chapter.
        if name == 'main' and c.positionExists(p1):
            return p1
        if not p1:
            if trace and verbose: g.trace('*** no p')
            return None
        root = self.findRootNode()
        if not root:
            if trace: g.trace('no root for ',self.name)
            return None
        if c.positionExists(p1,root=root.copy()):
            if trace and verbose: g.trace('found existing',p1.h)
            return p1
        if strict:
            if trace: g.trace('strict test fails',p1.h)
            return None
        ### theIter = g.choose(name=='main',
            # self.c.all_unique_positions,
            # root.self_and_subtree)
        if name == 'main':
            theIter = c.all_unique_positions
        else:
            theIter = root.self_and_subtree
        for p in theIter():
            if p.v == p1.v:
                if trace: g.trace('*** found vnode match',p1.h)
                return p.copy()
        if trace: g.trace('*** not found',p1.h)
        return None
    #@+node:ekr.20070425175522: *4* chapter.findEditorInChapter
    def findEditorInChapter (self,p):

        '''return w, an editor displaying position p.'''

        chapter,c = self,self.c
        w = c.frame.body.findEditorForChapter(chapter,p)
        w.leo_chapter = chapter
        w.leo_p = p and p.copy()
        return w
    #@+node:ekr.20070615065222: *4* chapter.positionIsInChapter
    def positionIsInChapter (self,p):

        p2 = self.findPositionInChapter (p,strict=True)
        # g.trace(self.name,'returns',p2)
        return p2
    #@+node:ekr.20070529171934.1: *4* chapter.rename (not used)
    def rename (self,newName):

        cc = self.cc
        p = cc.findChapterNode(self.name)
        if p:
            s = '@chapter ' + newName
            p.setHeadString(s)
        else:
            g.trace('Can not happen: no @chapter %s' % (self.name))
    #@+node:ekr.20070320091806.1: *3* chapter.unselect
    def unselect (self):

        '''Remember chapter info when a chapter is about to be unselected.'''

        trace = False and not g.unitTesting
        c = self.c
        if self.name != 'main':
            try:
                c.hoistStack.pop()
            except Exception:
                g.trace('c.hoistStack underflow')
        self.p = c.p
        if trace: g.trace('*** %s, p: %s' % (self.name,self.p.h))
    #@-others
#@-others
#@-leo
