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
            # Important: chapter names never change, even if their @chapter node changes.

        self.chaptersNode = None # Set later
        self.selectedChapter = None
        self.trace = False
        self.tt = None # May be set in finishCreate.
        self.use_tabs = c.config.getBool('use_chapter_tabs')

        # g.trace('chapterController',g.callers())
    #@+node:ekr.20070325104904: *4* cc.finishCreate
    def finishCreate (self):

        '''Find or make the @chapters and @chapter trash nodes.'''

        # This must be called late in the init process:
        # at present, called by g.openWithFileName and c.new.

        # g.trace('(chapterController)',g.callers(4))

        cc = self ; c = cc.c

        # Create the @chapters node if needed, and set cc.chaptersNode.
        if 0: # Now done in cc.createChapterNode.
            if not cc.chaptersNode and not cc.findChaptersNode():
                cc.createChaptersNode()

        if cc.findChaptersNode():
            if hasattr(c.frame.iconBar,'createChaptersIcon'):
                c.frame.iconBar.createChaptersIcon()

        # Create the main chapter
        cc.chaptersDict['main'] = chapter(c=c,chapterController=cc,name='main',root=c.rootPosition())

        tag = '@chapter'
        for p in c.all_unique_positions():
            h = p.h
            if h.startswith(tag) and not h.startswith('@chapters'):
                tabName = h[len(tag):].strip()
                if tabName and tabName not in ('main',):
                    if cc.chaptersDict.get(tabName):
                        self.error('duplicate chapter name: %s' % tabName)
                    else:
                        cc.chaptersDict[tabName] = chapter(c=c,chapterController=cc,name=tabName,root=p)

        # Always select the main chapter.
        # It can be alarming to open a small chapter in a large .leo file.
        cc.selectChapterByName('main',collapse=False)
            # 2010/10/09: an important bug fix!
    #@+node:ekr.20070317085437.30: *3* Commands (chapters)
    #@+node:ekr.20070317085437.50: *4* cc.cloneNodeToChapter & helper
    def cloneNodeToChapter (self,event=None):

        '''Prompt for a chapter name,
        then clone the selected node to the chapter.'''

        cc = self ; k = cc.c.k ; tag = 'clone-node-to-chapter'
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

        cc = self ; c = cc.c ; p = c.p ; u = c.undoer
        undoType = 'Clone Node To Chapter'
        fromChapter = cc.getSelectedChapter()
        toChapter = cc.getChapter(toChapterName)
        if not toChapter:
            return cc.error('chapter "%s" does not exist' % toChapterName)
        if fromChapter.name == 'main' and g.match_word(p.h,0,'@chapter'):
            return cc.error('can not clone @chapter node')

        # Open the group undo.
        c.undoer.beforeChangeGroup(toChapter.root,undoType)
        # Do the clone.  c.clone handles the inner undo.
        clone = c.clone()
        # Do the move.
        undoData2 = u.beforeMoveNode(clone)
        if toChapter.name == 'main':
            clone.moveAfter(toChapter.p)
        else:
            clone.moveToLastChildOf(toChapter.root)
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

        cc = self ; c = cc.c ; k = c.k ; tag = 'convert-node-to-chapter'
        state = k.getState(tag)

        p = c.p
        if p.h.startswith('@chapter'):
            cc.error('Can not create a new chapter from from an @chapter or @chapters node.')
            return

        if state == 0:
            names = list(cc.chaptersDict.keys())
            k.setLabelBlue('Convert node to chapter: ',protect=True)
            k.getArg(event,tag,1,self.convertNodeToChapter,tabList=names)
        else:
            k.clearState()
            k.resetLabel()
            if k.arg:
                cc.createChapterByName(k.arg,p=c.p,
                    undoType='Convert Node To Chapter')
    #@+node:ekr.20070317085437.51: *4* cc.copyNodeToChapter & helper
    def copyNodeToChapter (self,event=None):

        '''Prompt for a chapter name,
        then copy the selected node to the chapter.'''

        cc = self ; k = cc.c.k ; tag = 'copy-node-to-chapter'
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

        cc = self ; c = cc.c ; p = c.p ; u = c.undoer
        undoType = 'Copy Node To Chapter'
        fromChapter = cc.getSelectedChapter()
        toChapter = cc.getChapter(toChapterName)
        if not toChapter:
            return cc.error('no such chapter: %s' % toChapterName)
        if fromChapter.name == 'main' and g.match_word(p.h,0,'@chapter'):
            return cc.error('can not copy @chapter node')

        # For undo, we treat the copy like a pasted (inserted) node.
        undoData = u.beforeInsertNode(toChapter.root,pasteAsClone=False,copiedBunchList=[])
        s = c.fileCommands.putLeoOutline()
        p2 = c.fileCommands.getLeoOutline(s)
        p2.moveToLastChildOf(toChapter.root)
        c.redraw(p2)
        u.afterInsertNode(p2,undoType,undoData)
        c.setChanged(True)

        toChapter.p = p2.copy()
        toChapter.select()
        fromChapter.p = p.copy()
    #@+node:ekr.20070317085437.31: *4* cc.createChapter
    def createChapter (self,event=None):

        '''create-chapter command.
        Create a chapter with a dummy first node.'''

        cc = self ; k = cc.c.k ; tag = 'create-chapter'
        state = k.getState(tag)

        if state == 0:
            names = list(cc.chaptersDict.keys())
            k.setLabelBlue('Create chapter: ',protect=True)
            k.getArg(event,tag,1,self.createChapter,tabList=names)
        else:
            k.clearState()
            k.resetLabel()
            if k.arg:
                cc.createChapterByName(k.arg,p=None,
                    undoType='Create Chapter')
    #@+node:ekr.20070603190617: *4* cc.createChapterByName
    def createChapterByName (self,name,p,undoType):

        cc = self ; c = cc.c

        if not name:
            return cc.error('No name')

        oldChapter = cc.getSelectedChapter()
        theChapter = cc.chaptersDict.get(name)
        if theChapter:
            return cc.error('Duplicate chapter name: %s' % name)

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

        cc.chaptersDict[name] = chapter(c=c,chapterController=cc,name=name,root=root)
        cc.selectChapterByName(name)
        cc.afterCreateChapter(bunch,c.p)

        # g.es('created chapter',name,color='blue')
        return True
    #@+node:ekr.20070607092909: *4* cc.createChapterFromNode
    def createChapterFromNode (self,event=None):

        '''create-chapter-from-node command.

        Create a chapter whose first node is a clone of the presently selected node.'''

        cc = self ; c = cc.c ; k = c.k ; tag = 'create-chapter-from-node'
        state = k.getState(tag)

        p = c.p
        if p.h.startswith('@chapter'):
            cc.error('Can not create a new chapter from from an @chapter or @chapters node.')
            return

        if state == 0:
            names = list(cc.chaptersDict.keys())
            k.setLabelBlue('Create chapter from node: ',protect=True)
            k.getArg(event,tag,1,self.createChapterFromNode,tabList=names)
        else:
            k.clearState()
            k.resetLabel()
            if k.arg:
                cc.createChapterByName(k.arg,p=p,
                    undoType='Create Chapter From Node')
    #@+node:ekr.20070604155815.3: *4* cc.moveNodeToChapter & helper
    def moveNodeToChapter (self,event=None):

        '''Prompt for a chapter name,
        then move the selected node to the chapter.'''

        cc = self ; k = cc.c.k ; tag = 'move-node-to-chapter'
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

        cc = self ; c = cc.c ; p = c.p ; u = c.undoer
        undoType = 'Move Node To Chapter'
        fromChapter = cc.getSelectedChapter()
        toChapter = cc.getChapter(toChapterName)
        if not toChapter:
            return cc.error('chapter "%s" does not exist' % toChapterName)
        if fromChapter.name == 'main' and g.match_word(p.h,0,'@chapter'):
            return cc.error('can not move @chapter node')

        if toChapter.name == 'main':
            sel = (p.threadBack() != fromChapter.root and p.threadBack()) or p.nodeAfterTree()
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
                p.moveToLastChildOf(toChapter.root)
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
            cc.error('Can not move the last remaining node of a chapter.')
    #@+node:ekr.20070317085437.40: *4* cc.removeChapter
    def removeChapter (self,event=None):

        cc = self ; c = cc.c

        theChapter = cc.selectedChapter
        if not theChapter: return

        name = theChapter.name

        if name == 'main':
            return cc.error('Can not remove the main chapter')
        else:
            cc.removeChapterByName(name)
    #@+node:ekr.20070606075434: *4* cc.removeChapterByName
    def removeChapterByName (self,name):

        cc = self ; c = cc.c ; tt = cc.tt

        theChapter = cc.chaptersDict.get(name)
        if not theChapter: return

        savedRoot = theChapter.root
        bunch = cc.beforeRemoveChapter(c.p,name,savedRoot)
        cc.deleteChapterNode(name)
        del cc.chaptersDict[name] # Do this after calling deleteChapterNode.
        if tt:tt.destroyTab(name)
        cc.selectChapterByName('main')
        cc.afterRemoveChapter(bunch,c.p)
        c.redraw()
    #@+node:ekr.20070317085437.41: *4* cc.renameChapter
    # newName is for unitTesting.

    def renameChapter (self,event=None,newName=None):

        '''Use the minibuffer to get a new name for the present chapter.'''

        cc = self ; c = cc.c ; k = cc.c.k ; tt = cc.tt
        tag = 'rename-chapter'
        theChapter = cc.selectedChapter
        if not theChapter: return
        if theChapter.name == 'main':
            return cc.error('Can not rename the main chapter')

        state = k.getState(tag)

        if state == 0 and not newName:
            names = list(cc.chaptersDict.keys())
            prefix = 'Rename this chapter: '
            k.setLabelBlue(prefix,protect=True)
            k.getArg(event,tag,1,self.renameChapter,prefix=prefix,tabList=names)
        else:
            k.clearState()
            k.resetLabel()
            if newName: k.arg = newName
            if k.arg and k.arg != theChapter.name:
                oldChapterName = theChapter.name
                del cc.chaptersDict[theChapter.name]
                cc.chaptersDict[k.arg] = theChapter
                theChapter.name = k.arg
                root = theChapter.root
                root.initHeadString('@chapter %s' % k.arg)
                if tt:
                    tt.setTabLabel(k.arg)
                    tt.destroyTab(oldChapterName)
                    tt.createTab(k.arg)
                c.redraw()
    #@+node:ekr.20070604165126: *4* cc.selectChapter
    def selectChapter (self,event=None):

        '''Use the minibuffer to get a chapter name,
        then create the chapter.'''

        cc = self ; k = cc.c.k ; tag = 'select-chapter'
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
                cc.selectChapterByName(k.arg)
    #@+node:ekr.20070317130250: *4* cc.selectChapterByName & helper
    def selectChapterByName (self,name,collapse=True):

        '''Select a chapter.  Return True if a redraw is needed.'''

        cc = self ; c = cc.c

        chapter = cc.chaptersDict.get(name)

        if chapter:
            self.selectChapterByNameHelper(chapter,collapse=collapse)
        else:
            cc.error('cc.selectChapter: no such chapter: %s' % name)
            chapter = cc.chaptersDict.get('main')
            if chapter:
                self.selectChapterByNameHelper(chapter,collapse=collapse)
            else:
                cc.error('no main chapter!')
    #@+node:ekr.20090306060344.2: *5* selectChapterHelper
    def selectChapterByNameHelper (self,chapter,collapse=True):

        cc = self ; c = cc.c

        if chapter != cc.selectedChapter:
            if cc.selectedChapter:
                cc.selectedChapter.unselect()
            chapter.select()
            c.setCurrentPosition(chapter.p)
            cc.selectedChapter = chapter

            # New in Leo 4.6 b2: clean up, but not initially.
            if collapse and chapter.name == 'main':
                for p in c.all_unique_positions():
                    # 2010/01/26: compare vnodes, not positions.
                    if p.v != c.p.v:
                        p.contract()

            # New in Leo 4.6 b2: *do* call c.redraw.
            c.redraw()
    #@+node:ekr.20070511081405: *3* Creating/deleting nodes (chapterController)
    #@+node:ekr.20070325101652: *4* cc.createChaptersNode
    def createChaptersNode (self):

        cc = self ; c = cc.c ; root = c.rootPosition()

        # Create the node with a postion method
        # so we don't involve the undo logic.
        # g.trace('root',root)
        p = root.insertAsLastChild()
        p.initHeadString('@chapters')
        p.moveToRoot(oldRoot=root)
        # c.setRootPosition()
        cc.chaptersNode = p.copy()
        v = p.v
        assert(v.fileIndex)
        c.setChanged(True)
    #@+node:ekr.20070325063303.2: *4* cc.createChapterNode
    def createChapterNode (self,chapterName,p=None):

        '''Create an @chapter node for the named chapter.
        Use p for the first child, or create a first child if p is None.'''

        cc = self ; c = cc.c
        current = c.p or c.rootPosition()

        # 2010/06/17: Create an @chapters node if necessary.
        # This is no longer done automatically when creating a new window.
        if not cc.chaptersNode and not cc.findChaptersNode():
            cc.createChaptersNode()
            if hasattr(c.frame.iconBar,'createChaptersIcon'):
                c.frame.iconBar.createChaptersIcon()

        # Create the node with a postion method
        # so we don't involve the undo logic.
        root = current.insertAsLastChild()
        root.initHeadString('@chapter ' + chapterName)
        root.moveToFirstChildOf(cc.chaptersNode)
        if p:
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

        chapter = cc.chaptersDict.get(chapterName)

        if chapter:
            # Do not involve undo logic.
            c.setCurrentPosition(chapter.root)
            chapter.root.doDelete()
            # The chapter selection logic will select a new node.
            c.setChanged(True)
    #@+node:ekr.20070317130648: *3* Utils
    #@+node:ekr.20070320085610: *4* cc.error
    def error (self,s):

        g.es_print(s,color='red')
    #@+node:ekr.20070325093617: *4* cc.findChapterNode
    def findChapterNode (self,chapterName,giveError=True):

        '''Return the position of the @chapter node with the given name.'''

        cc = self

        if not cc.chaptersNode:
            return # An error has already been given.

        s = '@chapter ' + chapterName
        for p in cc.chaptersNode.children():
            h = p.h
            if h == s:
                return p

        if giveError:
            cc.error('*** findChapterNode: no @chapter node for: %s' % (chapterName))

        return None
    #@+node:ekr.20070325094401: *4* cc.findChaptersNode
    def findChaptersNode (self):

        '''Return the position of the @chapters node.'''

        cc = self ; c = cc.c

        for p in c.all_unique_positions():
            if p.h == '@chapters':
                cc.chaptersNode = p.copy()
                return p

        # This is *not* an error.
        return None
    #@+node:ekr.20070605124356: *4* cc.inChapter
    def inChapter (self):

        cc = self

        theChapter = cc.getSelectedChapter()
        return theChapter and theChapter.name != 'main'
    #@+node:ekr.20070325115102: *4* cc.getChapterNode
    def getChapterNode (self,chapterName,p=None):

        '''Return the position of the @chapter node with the given name.'''

        cc = self ; c = cc.c

        if chapterName == 'main':
            return c.rootPosition()
        else:
            val = (
                cc.findChapterNode(chapterName,giveError=False) or
                cc.createChapterNode(chapterName,p=p))
            return val
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

        cc = self ; c = cc.c ; root = cc.chaptersNode

        for p in c.rootPosition().self_and_siblings():
            for p2 in p.self_and_subtree():
                if p2 == root:
                    inTree = True ; break
        else:
            inTree = False

        g.trace('-'*40)

        full = True

        if root and full:
            g.pr('@chapters tree...','(in main tree: %s)' % inTree)
            for p in root.self_and_subtree():
                g.pr('.'*p.level(),p.v)
    #@+node:ekr.20070615075643: *4* cc.selectChapterForPosition
    def selectChapterForPosition (self,p):

        '''
        Select a chapter containing position p.
        Do nothing if p if p does not exist or is in the presently selected chapter.
        '''

        # trace = False and not g.unitTesting
        cc = self ; c = cc.c

        if not p or not c.positionExists(p):
            return

        theChapter = cc.getSelectedChapter()
        if not theChapter:
            # if trace: g.trace('no chapter')
            return

        # if trace: g.trace('selected:',theChapter.name)

        # First, try the presently selected chapter.
        firstName = theChapter.name
        if firstName == 'main' or theChapter.positionIsInChapter(p):
            # if trace: g.trace('in chapter:',theChapter.name)
            return

        for name in cc.chaptersDict:
            if name not in (firstName,'main'):
                theChapter = cc.chaptersDict.get(name)
                if theChapter.positionIsInChapter(p):
                    # if trace: g.trace('select:',theChapter.name)
                    cc.selectChapterByName(name)
                    return
        else:
            # if trace: g.trace('select main')
            cc.selectChapterByName('main')
    #@+node:ekr.20071028091719: *4* cc.findChapterNameForPosition
    def findChapterNameForPosition (self,p):

        '''
        Return the name of a chapter containing p or None if p does not exist.
        '''
        cc = self ; c = cc.c

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
            root = theChapter.root
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
        bunch.savedRoot = root = newChapter.root

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
        cc.chaptersDict[name] = chapter(c=c,chapterController=cc,name=name,root=u.savedRoot)
        cc.selectChapterByName(name)
    #@-others
#@+node:ekr.20070317085708: ** class chapter
class chapter:

    '''A class representing the non-gui data of a single chapter.'''

    #@+others
    #@+node:ekr.20070317085708.1: *3*  ctor: chapter
    def __init__ (self,c,chapterController,name,root):

        self.c = c 
        self.cc = cc = chapterController
        self.hoistStack = []
        self.name = name
        self.selectLockout = False # True: in chapter.select logic.
        self.trace = False

        # State variables: saved/restored when the chapter is unselected/selected.
        if self.name == 'main':
            self.p = c.p or c.rootPosition()
            self.root = None # Not used.
        else:
            self.p = None # Set later.
            self.root = root and root.copy() # The immutable @chapter node.
            bunch = g.Bunch(p=self.root.copy(),expanded=True)
            self.hoistStack.append(bunch)

        if cc.tt:
            cc.tt.createTab(name)
    #@+node:ekr.20070317085708.2: *3* __str__ and __repr__(chapter)
    def __str__ (self):

        return '<chapter id: %s name: %s p: %s>' % (
            id(self),
            self.name,
            self.p and self.p.h or '<no p>')

    __repr__ = __str__
    #@+node:ekr.20070325155208.1: *3* chapter.error
    def error (self,s):

        self.cc.error(s)
    #@+node:ekr.20070317131205.1: *3* chapter.select & helpers
    def select (self,w=None,selectEditor=True):

        '''Restore chapter information and redraw the tree when a chapter is selected.'''

        if self.selectLockout: return

        try:
            self.selectLockout = True
            self.chapterSelectHelper(w,selectEditor)
            if self.cc.tt:
                self.cc.tt.setTabLabel(self.name)
        finally:
            self.selectLockout = False
    #@+node:ekr.20070423102603.1: *4* chapterSelectHelper
    def chapterSelectHelper (self,w=None,selectEditor=True):

        c = self.c ; cc = self.cc ; name = self.name

        # g.trace(name,'self.p',self.p) # ,'self.root',self.root) # 'w.leo_p',w and w.leo_p)

        cc.selectedChapter = self

        # Next, recompute p and possibly select a new editor.
        if w:
            assert w == c.frame.body.bodyCtrl
            assert w.leo_p
            # g.trace(name,'w.leo_p',w.leo_p,'p',p)
            self.p = p = self.findPositionInChapter(w.leo_p)
            if p != w.leo_p: g.trace('****** can not happen: lost p',w.leo_p)
        else:
            # This must be done *after* switching roots.
            target_p = self.p or self.root.firstChild() or self.root
            #g.trace(name,'target_p',target_p)
            #g.trace(name,'self.p',self.p,'self.root',self.root)
            self.p = p = self.findPositionInChapter(target_p)
            if selectEditor:
                w = self.findEditorInChapter(p)
                c.frame.body.selectEditor(w) # Switches text.

        if name == 'main' and cc.chaptersNode:
            cc.chaptersNode.contract()    
        c.hoistStack = self.hoistStack[:]

        c.selectPosition(p)
        c.redraw_after_select(p)
        g.doHook('hoist-changed',c=c)
        c.bodyWantsFocus()
    #@+node:ekr.20070317131708: *4* chapter.findPositionInChapter
    def findPositionInChapter (self,p1,strict=False):

        '''Return a valid position p such that p.v == v.'''

        # trace = False and not g.unitTesting

        # Do nothing if the present position is in the proper chapter.
        c = self.c ; name = self.name 

        root = g.choose(self.name=='main',c.rootPosition(),self.root)

        # if trace:
            # g.trace('searching for: %s in chapter %s' % (p1.h,self.name))
            # g.trace(g.callers(6))

        if p1 and c.positionExists(p1,root=root):
            # if trace: g.trace('using existing position:',p1.h)
            return p1

        if name == 'main':
            for p in self.c.all_unique_positions():
                if p.v == p1.v:
                    # if trace: g.trace('*** found in chapter main:',p.h)
                    self.p = p.copy()
                    return self.p
            if strict:
                return None
            else:
                self.p = c.rootPosition()
        else:
            for p in self.root.self_and_subtree():
                # g.trace('testing',p,p1)
                if p.v == p1.v:
                    # if trace: g.trace('*** found in chapter %s: %s' % (self.name,p.h))
                    self.p = p.copy()
                    return self.p
            if strict:
                return None
            else:
                self.p = self.root.copy()

        # if trace:
            # # self.error('***** chapter: %s findPositionInChapter: lost %s' % (
                # # self.name,p1.h))
            # g.trace('fail',g.callers())

        return self.p.copy()
    #@+node:ekr.20070425175522: *4* chapter.findEditorInChapter
    def findEditorInChapter (self,p):

        '''return w, an editor displaying position p.'''

        chapter = self ; c = self.c

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

        p = self.root
        s = '@chapter ' + newName
        p.setHeadString(s)
    #@+node:ekr.20070320091806.1: *3* chapter.unselect
    def unselect (self):

        '''Remember chapter info when a chapter is about to be unselected.'''

        c = self.c ; cc = self.cc
        self.hoistStack = c.hoistStack[:]
        self.p = c.p
        if self.trace: g.trace('chapter',self.name,'p',self.p.h)
    #@-others
#@-others
#@-leo
