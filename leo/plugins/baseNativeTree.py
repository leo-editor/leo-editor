# -*- coding: utf-8 -*-
#@+leo-ver=4-thin
#@+node:ekr.20090124174652.7:@thin baseNativeTree.py
#@@first

'''Base classes for native tree widgets.'''

#@@language python
#@@tabwidth -4
#@@pagewidth 80

import leo.core.leoGlobals as g
import leo.core.leoFrame as leoFrame
import leo.core.leoNodes as leoNodes

class baseNativeTreeWidget (leoFrame.leoTree):

    """The base class for native tree widgets.

    See the ctor for more notes.
    """

    callbacksInjected = False # A class var.

    #@    @+others
    #@+node:ekr.20090124174652.9: Birth... (nativeTree)
    #@+node:ekr.20090124174652.10:__init__ (nativeTree)
    def __init__(self,c,frame):

        # Init the base class.
        leoFrame.leoTree.__init__(self,frame)

        # Components.
        self.c = c
        self.canvas = self # An official ivar used by Leo's core.

        # Subclasses should define headline wrappers to
        # be a subclass of leoFrame.baseTextWidget.
        self.headlineWrapper = leoFrame.baseTextWidget

        # Subclasses should define .treeWidget to be the underlying
        # native tree widget.
        self.treeWidget = None

        # Widget independent status ivars...
        self.contracting = False
        self.dragging = False
        self.expanding = False
        self.prev_p = None
        self.redrawing = False
        self.redrawCount = 0 # Count for debugging.
        self.revertHeadline = None # Previous headline text for abortEditLabel.
        self.selecting = False

        # Debugging...
        self.nodeDrawCount = 0
        self.traceCallersFlag = False # Enable traceCallers method.

        # Associating items with vnodes...
        self.item2vnodeDict = {}
        self.tnode2itemsDict = {} # values are lists of items.
        self.vnode2itemsDict = {} # values are lists of items.

        self.setConfigIvars()
        self.setEditPosition(None) # Set positions returned by leoTree.editPosition()
    #@-node:ekr.20090124174652.10:__init__ (nativeTree)
    #@+node:ekr.20090124174652.11:get_name (nativeTree)
    def getName (self):

        name = 'canvas(tree)' # Must start with canvas.

        return name
    #@-node:ekr.20090124174652.11:get_name (nativeTree)
    #@+node:ekr.20090124174652.121:Called from Leo's core
    def initAfterLoad (self):
        pass

    def setBindings (self):
        '''Create master bindings for all headlines.'''
        pass

    def setCanvasBindings (self,canvas):
        '''Create master tree bindings.'''
        pass
    #@nonl
    #@-node:ekr.20090124174652.121:Called from Leo's core
    #@-node:ekr.20090124174652.9: Birth... (nativeTree)
    #@+node:ekr.20090126120517.26:Debugging & tracing
    def error (self,s):
        g.trace('*** %s' % (s),g.callers(8))

    def traceItem(self,item):
        if item:
            return 'item %s: %s' % (id(item),self.getItemText(item))
        else:
            return '<no item>'

    def traceCallers(self):
        if self.traceCallersFlag:
            return g.callers(5,excludeCaller=True)
        else:
            return '' 
    #@nonl
    #@-node:ekr.20090126120517.26:Debugging & tracing
    #@+node:ekr.20090124174652.12:Config... (nativeTree)
    #@+node:ekr.20090124174652.13:do-nothin config methods
    # These can be over-ridden if desired,
    # but they do not have to be over-ridden.

    def bind (self,*args,**keys):               pass

    def headWidth(self,p=None,s=''):            return 0
    def widthInPixels(self,s):                  return 0

    def setEditLabelState (self,p,selectAll=False): pass # not called.

    def setSelectedLabelState (self,p):         pass
    def setUnselectedLabelState (self,p):       pass
    def setDisabledHeadlineColors (self,p):     pass
    def setEditHeadlineColors (self,p):         pass
    def setUnselectedHeadlineColors (self,p):   pass

    setNormalLabelState = setEditLabelState # For compatibility.
    #@nonl
    #@-node:ekr.20090124174652.13:do-nothin config methods
    #@+node:ekr.20090124174652.14:setConfigIvars
    def setConfigIvars (self):

        c = self.c

        self.allow_clone_drags    = c.config.getBool('allow_clone_drags')
        self.enable_drag_messages = c.config.getBool("enable_drag_messages")
        self.select_all_text_when_editing_headlines = c.config.getBool(
            'select_all_text_when_editing_headlines')
        self.stayInTree     = c.config.getBool('stayInTreeAfterSelect')
        self.use_chapters   = c.config.getBool('use_chapters')
    #@nonl
    #@-node:ekr.20090124174652.14:setConfigIvars
    #@-node:ekr.20090124174652.12:Config... (nativeTree)
    #@+node:ekr.20090124174652.15:Drawing... (nativeTree)
    #@+node:ekr.20090124174652.16:Entry points (nativeTree)
    #@+node:ekr.20090124174652.17:full_redraw & helpers
    # forceDraw not used. It is used in the Tk code.

    def full_redraw (self,p=None,scroll=True,forceDraw=False):

        '''Redraw all visible nodes of the tree.

        Preserve the vertical scrolling unless scroll is True.'''

        trace = False and not g.app.unitTesting
        verbose = False
        c = self.c

        if self.busy():
            return g.trace('*** full_redraw: busy!',g.callers(5))

        if p is None:   p = c.currentPosition()
        else:           c.setCurrentPosition(p)

        self.redrawCount += 1
        if trace: t1 = g.getTime()
        self.initData()
        self.nodeDrawCount = 0
        try:
            self.redrawing = True
            self.drawTopTree(p)
        finally:
            self.redrawing = False

        self.setItemForCurrentPosition(scroll=scroll)
        c.requestRedrawFlag= False

        if trace:
            theTime = g.timeSince(t1)
            callers = g.choose(verbose,g.callers(5),'')
            g.trace('%s: scroll %5s drew %3s nodes in %s' % (
                self.redrawCount,scroll,self.nodeDrawCount,theTime),callers)

    # Compatibility
    redraw = full_redraw 
    redraw_now = full_redraw
    #@+node:ekr.20090124174652.19:drawChildren
    def drawChildren (self,p,parent_item):

        trace = False and not g.unitTesting

        if trace: g.trace('children? %5s expanded? %5s %s' % (
            p.hasChildren(),p.isExpanded(),p.h))

        if not p:
            return g.trace('can not happen: no p')

        if p.hasChildren():
            if p.isExpanded():
                self.expandItem(parent_item)
                child = p.firstChild()
                while child:
                    self.drawTree(child,parent_item)
                    child.moveToNext()
            else:
                # Draw the hidden children.
                child = p.firstChild()
                while child:
                    self.drawNode(child,parent_item)
                    child.moveToNext()
                self.contractItem(parent_item)
        else:
            self.contractItem(parent_item)
    #@-node:ekr.20090124174652.19:drawChildren
    #@+node:ekr.20090124174652.20:drawNode
    def drawNode (self,p,parent_item):

        trace = False
        c = self.c 
        self.nodeDrawCount += 1

        # Allocate the item.
        item = self.createTreeItem(p,parent_item) 

        # Do this now, so self.isValidItem will be true in setItemIcon.
        self.rememberItem(p,item)

        # Set the headline and maybe the icon.
        self.setItemText(item,p.h)
        if p:
            self.drawItemIcon(p,item)

        if trace: g.trace(self.traceItem(item))

        return item
    #@-node:ekr.20090124174652.20:drawNode
    #@+node:ekr.20090129062500.12:drawTopTree
    def drawTopTree (self,p):

        c = self.c
        hPos,vPos = self.getScroll()
        self.clear()
        # Draw all top-level nodes and their visible descendants.
        if c.hoistStack:
            bunch = c.hoistStack[-1]
            p = bunch.p ; h = p.h
            if len(c.hoistStack) == 1 and h.startswith('@chapter') and p.hasChildren():
                p = p.firstChild()
                while p:
                    self.drawTree(p)
                    p.moveToNext()
            else:
                self.drawTree(p)
        else:
            p = c.rootPosition()
            while p:
                self.drawTree(p)
                p.moveToNext()

        # This method always retains previous scroll position.
        self.setHScroll(hPos)
        self.setVScroll(vPos)

        self.repaint()
    #@nonl
    #@-node:ekr.20090129062500.12:drawTopTree
    #@+node:ekr.20090124174652.21:drawTree
    def drawTree (self,p,parent_item=None):

        # Draw the (visible) parent node.
        item = self.drawNode(p,parent_item)

        # Draw all the visible children.
        self.drawChildren(p,parent_item=item)


    #@-node:ekr.20090124174652.21:drawTree
    #@+node:ekr.20090124174652.22:initData
    def initData (self):

        # g.trace('*****')

        self.item2vnodeDict = {}
        self.tnode2itemsDict = {}
        self.vnode2itemsDict = {}
    #@-node:ekr.20090124174652.22:initData
    #@+node:ekr.20090124174652.23:rememberItem & rememberVnodeItem
    def rememberItem (self,p,item):

        self.rememberVnodeItem(p.v,item)

    def rememberVnodeItem (self,v,item):

        # Update item2vnodeDict.
        self.item2vnodeDict[item] = v

        # Update tnode2itemsDict & vnode2itemsDict.
        table = (
            (self.tnode2itemsDict,v.t),
            (self.vnode2itemsDict,v))

        for d,key in table:
            aList = d.get(key,[])
            if item in aList:
                g.trace('*** ERROR *** item already in list: %s, %s' % (item,aList))
            else:
                aList.append(item)
            d[key] = aList
    #@nonl
    #@-node:ekr.20090124174652.23:rememberItem & rememberVnodeItem
    #@-node:ekr.20090124174652.17:full_redraw & helpers
    #@+node:ekr.20090124174652.24:redraw_after_contract
    def redraw_after_contract (self,p=None):

        if self.redrawing:
            return

        item = self.position2item(p)

        if item:
            self.contractItem(item)
        else:
            # This is not an error.
            # We may have contracted a node that was not, in fact, visible.
            self.full_redraw(scroll=False)
    #@-node:ekr.20090124174652.24:redraw_after_contract
    #@+node:ekr.20090124174652.25:redraw_after_expand
    def redraw_after_expand (self,p=None):

        # Important, setting scrolling to False makes the problem *worse*
        self.full_redraw (p,scroll=True)
    #@-node:ekr.20090124174652.25:redraw_after_expand
    #@+node:ekr.20090124174652.26:redraw_after_head_changed
    def redraw_after_head_changed (self):

        trace = False and not g.unitTesting

        if self.busy(): return

        c = self.c ; p = c.currentPosition()
        ew = self.edit_widget(p)

        if trace: g.trace(p.h)

        currentItem = self.getCurrentItem()

        if p:
            for item in self.tnode2items(p.v.t):
                if self.isValidItem(item):
                    self.setItemText(item,p.h)
    #@-node:ekr.20090124174652.26:redraw_after_head_changed
    #@+node:ekr.20090124174652.27:redraw_after_icons_changed
    def redraw_after_icons_changed (self):

        trace = False and not g.unitTesting

        if self.busy(): return

        self.redrawCount += 1 # To keep a unit test happy.

        c = self.c

        if trace: g.trace(c.p.h,g.callers(4))

        # Suppress call to setHeadString in onItemChanged!
        self.redrawing = True
        try:
            item = self.getCurrentItem()
            for p in c.rootPosition().self_and_siblings_iter():
                self.updateVisibleIcons(p)
        finally:
            self.redrawing = False
    #@-node:ekr.20090124174652.27:redraw_after_icons_changed
    #@+node:ekr.20090124174652.28:redraw_after_select
    # Important: this can not replace before/afterSelectHint.

    def redraw_after_select (self,p=None):

        '''Redraw the entire tree when an invisible node
        is selected.'''

        trace = False and not g.unitTesting

        if trace: g.trace('(leoQtTree) busy? %s %s' % (
            self.busy(),p and p.h or '<no p>'),g.callers(4))

        # Prevent the selecting lockout from disabling the redraw.
        oldSelecting = self.selecting
        self.selecting = False
        try:
            if not self.busy():
                self.full_redraw(p,scroll=False)
        finally:
            self.selecting = oldSelecting

        # c.redraw_after_select calls tree.select indirectly.
        # Do not call it again here.
    #@-node:ekr.20090124174652.28:redraw_after_select
    #@-node:ekr.20090124174652.16:Entry points (nativeTree)
    #@-node:ekr.20090124174652.15:Drawing... (nativeTree)
    #@+node:ekr.20090124174652.29:Event handlers... (nativeTree)
    #@+node:ekr.20090129062500.10:busy (nativeTree)
    def busy (self):

        '''Return True (actually, a debugging string)
        if any lockout is set.'''

        trace = False
        table = (
            (self.contracting,  'contracting'),
            (self.expanding,    'expanding'),
            (self.redrawing,    'redrawing'),
            (self.selecting,    'selecting'))

        item = self.getCurrentItem()

        aList = []
        for ivar,kind in table:
            if ivar:
                aList.append(kind)
        kinds = ','.join(aList)

        if aList and trace:
            g.trace(self.traceItem(item),kinds,g.callers(4))

        return kinds # Return the string for debugging
    #@-node:ekr.20090129062500.10:busy (nativeTree)
    #@+node:ekr.20090124174652.30:Click Box... (nativeTree)
    #@+node:ekr.20090124174652.31:onClickBoxClick
    def onClickBoxClick (self,event,p=None):

        if self.busy(): return

        c = self.c

        g.doHook("boxclick1",c=c,p=p,v=p,event=event)
        g.doHook("boxclick2",c=c,p=p,v=p,event=event)

        c.outerUpdate()
    #@-node:ekr.20090124174652.31:onClickBoxClick
    #@+node:ekr.20090124174652.32:onClickBoxRightClick
    def onClickBoxRightClick(self, event, p=None):

        if self.busy(): return

        c = self.c

        g.doHook("boxrclick1",c=c,p=p,v=p,event=event)
        g.doHook("boxrclick2",c=c,p=p,v=p,event=event)

        c.outerUpdate()
    #@-node:ekr.20090124174652.32:onClickBoxRightClick
    #@+node:ekr.20090124174652.33:onPlusBoxRightClick
    def onPlusBoxRightClick (self,event,p=None):

        if self.busy(): return

        c = self.c

        g.doHook('rclick-popup',c=c,p=p,event=event,context_menu='plusbox')

        c.outerUpdate()
    #@-node:ekr.20090124174652.33:onPlusBoxRightClick
    #@-node:ekr.20090124174652.30:Click Box... (nativeTree)
    #@+node:ekr.20090124174652.35:Icon Box... (nativeTree)
    # For Qt, there seems to be no way to trigger these events.
    #@nonl
    #@+node:ekr.20090124174652.36:onIconBoxClick
    def onIconBoxClick (self,event,p=None):

        if self.busy(): return

        c = self.c

        g.doHook("iconclick1",c=c,p=p,v=p,event=event)
        g.doHook("iconclick2",c=c,p=p,v=p,event=event)

        c.outerUpdate()
    #@-node:ekr.20090124174652.36:onIconBoxClick
    #@+node:ekr.20090124174652.37:onIconBoxRightClick
    def onIconBoxRightClick (self,event,p=None):

        """Handle a right click in any outline widget."""

        if self.busy(): return

        c = self.c

        g.doHook("iconrclick1",c=c,p=p,v=p,event=event)
        g.doHook("iconrclick2",c=c,p=p,v=p,event=event)

        c.outerUpdate()
    #@-node:ekr.20090124174652.37:onIconBoxRightClick
    #@+node:ekr.20090124174652.38:onIconBoxDoubleClick
    def onIconBoxDoubleClick (self,event,p=None):

        if self.busy(): return

        c = self.c

        g.doHook("icondclick1",c=c,p=p,v=p,event=event)
        g.doHook("icondclick2",c=c,p=p,v=p,event=event)

        c.outerUpdate()
    #@-node:ekr.20090124174652.38:onIconBoxDoubleClick
    #@-node:ekr.20090124174652.35:Icon Box... (nativeTree)
    #@+node:ekr.20090124174652.40:onItemCollapsed (nativeTree)
    def onItemCollapsed (self,item):

        trace = False
        verbose = False

        if self.busy(): return

        c = self.c
        if trace: g.trace(self.traceItem(item))
        p = self.item2position(item)

        if p:
            # Important: do not set lockouts here.
            # Only methods that actually generate events should set lockouts.
            p.contract()
            self.select(p) # Calls before/afterSelectHint.    
        else:
            self.error('no p')

        c.outerUpdate()
    #@-node:ekr.20090124174652.40:onItemCollapsed (nativeTree)
    #@+node:ekr.20090124174652.41:onItemDoubleClicked (nativeTree)
    def onItemDoubleClicked (self,item,col):

        trace = False
        verbose = False

        if self.busy(): return

        c = self.c

        if trace: g.trace(col,self.traceItem(item),g.callers(4))

        try:
            self.selecting = True

            e = self.createTreeEditorForItem(item)
            if not e: g.trace('*** no e')

            p = self.item2position(item)
            if p:
                event = None
                g.doHook("icondclick1",c=c,p=p,v=p,event=event)
                g.doHook("icondclick2",c=c,p=p,v=p,event=event)
            else:
                g.trace('*** no p')

            c.outerUpdate()
        finally:
            self.selecting = False
    #@-node:ekr.20090124174652.41:onItemDoubleClicked (nativeTree)
    #@+node:ekr.20090124174652.42:onItemExpanded (nativeTree)
    def onItemExpanded (self,item):

        '''Handle and tree-expansion event.'''

        trace = False
        verbose = False

        if self.busy(): return

        c = self.c
        if trace: g.trace(self.traceItem(item))
        p = self.item2position(item)

        if p:
            # Important: do not set lockouts here.
            # Only methods that actually generate events should set lockouts.
            if not p.isExpanded():
                p.expand()
                self.select(p) # Calls before/afterSelectHint.
                # Important: setting scroll=False here has no effect
                # when a keystroke causes the expansion, but is a
                # *big* improvement when clicking the outline.
                self.full_redraw(scroll=False)
            else:
                self.select(p)
        else:
            self.error('no p')

        c.outerUpdate()
    #@-node:ekr.20090124174652.42:onItemExpanded (nativeTree)
    #@+node:ekr.20090124174652.43:onTreeSelect (nativeTree)
    def onTreeSelect(self):

        '''Select the proper position when a tree node is selected.'''

        trace = False and not g.unitTesting
        verbose = False

        if self.busy(): return

        c = self.c

        item = self.getCurrentItem()
        p = self.item2position(item)

        if p:
            # Important: do not set lockouts here.
            # Only methods that actually generate events should set lockouts.
            if trace: g.trace(self.traceItem(item))
            self.select(p) # Calls before/afterSelectHint.
        else:
            self.error('no p for item: %s' % item,g.callers(4))

        c.outerUpdate()
    #@-node:ekr.20090124174652.43:onTreeSelect (nativeTree)
    #@+node:ekr.20090124174652.45:tree.OnPopup & allies (nativeTree)
    def OnPopup (self,p,event):

        """Handle right-clicks in the outline.

        This is *not* an event handler: it is called from other event handlers."""

        # Note: "headrclick" hooks handled by vnode callback routine.

        if event != None:
            c = self.c
            c.setLog()

            if not g.doHook("create-popup-menu",c=c,p=p,v=p,event=event):
                self.createPopupMenu(event)
            if not g.doHook("enable-popup-menu-items",c=c,p=p,v=p,event=event):
                self.enablePopupMenuItems(p,event)
            if not g.doHook("show-popup-menu",c=c,p=p,v=p,event=event):
                self.showPopupMenu(event)

        return "break"
    #@+node:ekr.20090124174652.46:OnPopupFocusLost
    #@+at
    # On Linux we must do something special to make the popup menu "unpost" if 
    # the
    # mouse is clicked elsewhere. So we have to catch the <FocusOut> event and
    # explicitly unpost. In order to process the <FocusOut> event, we need to 
    # be able
    # to find the reference to the popup window again, so this needs to be an
    # attribute of the tree object; hence, "self.popupMenu".
    # 
    # Aside: though Qt tries to be muli-platform, the interaction with 
    # different
    # window managers does cause small differences that will need to be 
    # compensated by
    # system specific application code. :-(
    #@-at
    #@@c

    # 20-SEP-2002 DTHEIN: This event handler is only needed for Linux.

    def OnPopupFocusLost(self,event=None):

        # self.popupMenu.unpost()
        pass
    #@-node:ekr.20090124174652.46:OnPopupFocusLost
    #@+node:ekr.20090124174652.47:createPopupMenu
    def createPopupMenu (self,event):

        c = self.c ; frame = c.frame

        # self.popupMenu = menu = Qt.Menu(g.app.root, tearoff=0)

        # # Add the Open With entries if they exist.
        # if g.app.openWithTable:
            # frame.menu.createOpenWithMenuItemsFromTable(menu,g.app.openWithTable)
            # table = (("-",None,None),)
            # frame.menu.createMenuEntries(menu,table)

        #@    << Create the menu table >>
        #@+node:ekr.20090124174652.48:<< Create the menu table >>
        # table = (
            # ("&Read @file Nodes",c.readAtFileNodes),
            # ("&Write @file Nodes",c.fileCommands.writeAtFileNodes),
            # ("-",None),
            # ("&Tangle",c.tangle),
            # ("&Untangle",c.untangle),
            # ("-",None),
            # ("Toggle Angle &Brackets",c.toggleAngleBrackets),
            # ("-",None),
            # ("Cut Node",c.cutOutline),
            # ("Copy Node",c.copyOutline),
            # ("&Paste Node",c.pasteOutline),
            # ("&Delete Node",c.deleteOutline),
            # ("-",None),
            # ("&Insert Node",c.insertHeadline),
            # ("&Clone Node",c.clone),
            # ("Sort C&hildren",c.sortChildren),
            # ("&Sort Siblings",c.sortSiblings),
            # ("-",None),
            # ("Contract Parent",c.contractParent),
        # )
        #@-node:ekr.20090124174652.48:<< Create the menu table >>
        #@nl

        # # New in 4.4.  There is no need for a dontBind argument because
        # # Bindings from tables are ignored.
        # frame.menu.createMenuEntries(menu,table)
    #@-node:ekr.20090124174652.47:createPopupMenu
    #@+node:ekr.20090124174652.49:enablePopupMenuItems
    def enablePopupMenuItems (self,v,event):

        """Enable and disable items in the popup menu."""

        c = self.c 

        # menu = self.popupMenu

        #@    << set isAtRoot and isAtFile if v's tree contains @root or @file nodes >>
        #@+node:ekr.20090124174652.50:<< set isAtRoot and isAtFile if v's tree contains @root or @file nodes >>
        # isAtFile = False
        # isAtRoot = False

        # for v2 in v.self_and_subtree_iter():
            # if isAtFile and isAtRoot:
                # break
            # if (v2.isAtFileNode() or
                # v2.isAtNorefFileNode() or
                # v2.isAtAsisFileNode() or
                # v2.isAtNoSentFileNode()
            # ):
                # isAtFile = True

            # isRoot,junk = g.is_special(v2.bodyString(),0,"@root")
            # if isRoot:
                # isAtRoot = True
        #@-node:ekr.20090124174652.50:<< set isAtRoot and isAtFile if v's tree contains @root or @file nodes >>
        #@nl
        # isAtFile = g.choose(isAtFile,1,0)
        # isAtRoot = g.choose(isAtRoot,1,0)
        # canContract = v.parent() != None
        # canContract = g.choose(canContract,1,0)

        # enable = self.frame.menu.enableMenu

        # for name in ("Read @file Nodes", "Write @file Nodes"):
            # enable(menu,name,isAtFile)
        # for name in ("Tangle", "Untangle"):
            # enable(menu,name,isAtRoot)

        # enable(menu,"Cut Node",c.canCutOutline())
        # enable(menu,"Delete Node",c.canDeleteHeadline())
        # enable(menu,"Paste Node",c.canPasteOutline())
        # enable(menu,"Sort Children",c.canSortChildren())
        # enable(menu,"Sort Siblings",c.canSortSiblings())
        # enable(menu,"Contract Parent",c.canContractParent())
    #@-node:ekr.20090124174652.49:enablePopupMenuItems
    #@+node:ekr.20090124174652.51:showPopupMenu
    def showPopupMenu (self,event):

        """Show a popup menu."""

        # c = self.c ; menu = self.popupMenu

        # g.app.gui.postPopupMenu(c, menu, event.x_root, event.y_root)

        # self.popupMenu = None

        # # Set the focus immediately so we know when we lose it.
        # #c.widgetWantsFocus(menu)
    #@-node:ekr.20090124174652.51:showPopupMenu
    #@-node:ekr.20090124174652.45:tree.OnPopup & allies (nativeTree)
    #@-node:ekr.20090124174652.29:Event handlers... (nativeTree)
    #@+node:ekr.20090124174652.52:Selecting & editing... (nativeTree)
    #@+node:ekr.20090124174652.53:afterSelectHint (nativeTree)
    def afterSelectHint (self,p,old_p):

        trace = False and not g.unitTesting
        c = self.c

        self.selecting = False

        if self.busy():
            self.error('afterSelectHint busy!: %s' % self.busy())

        if not p:
            return self.error('no p')
        if p != c.currentPosition():
            return self.error('p is not c.currentPosition()')

        if trace: g.trace(p and p.h,g.callers(4))

        # We don't redraw during unit testing: an important speedup.
        if c.expandAllAncestors(p) and not g.unitTesting:
            self.full_redraw(p)
        else:
            c.outerUpdate() # Bring the tree up to date.
            self.setItemForCurrentPosition(scroll=False)
    #@-node:ekr.20090124174652.53:afterSelectHint (nativeTree)
    #@+node:ekr.20090124174652.54:beforeSelectHint (nativeTree)
    def beforeSelectHint (self,p,old_p):

        trace = False and not g.unitTesting

        if self.busy(): return

        if trace: g.trace(p and p.h)

        # Disable onTextChanged.
        self.selecting = True
    #@-node:ekr.20090124174652.54:beforeSelectHint (nativeTree)
    #@+node:ekr.20090124174652.55:edit_widget (nativeTree)
    def edit_widget (self,p):

        """Returns the edit widget for position p."""

        trace = False and not g.unitTesting
        verbose = True

        c = self.c
        item = self.position2item(p)
        if item:
            e = self.getTreeEditorForItem(item)
            if e:
                # Create a wrapper widget for Leo's core.
                w = self.headlineWrapper(widget=e,name='head',c=c)
                # if trace: g.trace(e,p and p.h)
                return w
            else:
                # This is not an error
                # But warning: calling this method twice might not work!
                if trace and verbose: g.trace('no e for %s' % (p))
                return None
        else:
            if trace and verbose: self.error('no item for %s' % (p))
            return None
    #@nonl
    #@-node:ekr.20090124174652.55:edit_widget (nativeTree)
    #@+node:ekr.20090124174652.56:editLabel (nativeTree)
    def editLabel (self,p,selectAll=False,selection=None):

        """Start editing p's headline."""

        trace = False ; verbose = False

        if self.busy():
            return

        c = self.c

        if trace: g.trace('***',p and p.h,g.callers(4))

        c.outerUpdate()
            # Do any scheduled redraw.
            # This won't do anything in the new redraw scheme.

        item = self.position2item(p)
        if item:
            e = self.editLabelHelper(item,selectAll,selection)
        else:
            e = None
            self.error('no item for %s' % p)

        # A nice hack: just set the focus request.
        if e: c.requestedFocusWidget = e
    #@-node:ekr.20090124174652.56:editLabel (nativeTree)
    #@+node:ekr.20090124174652.57:editPosition (nativeTree)
    def editPosition(self):

        c = self.c ; p = c.currentPosition()
        ew = self.edit_widget(p)
        return ew and p or None
    #@-node:ekr.20090124174652.57:editPosition (nativeTree)
    #@+node:ekr.20090124174652.58:endEditLabel (nativeTree)
    def endEditLabel (self):

        '''Override leoTree.endEditLabel.

        End editing of the presently-selected headline.'''

        c = self.c ; p = c.currentPosition()

        self.onHeadChanged(p)
    #@nonl
    #@-node:ekr.20090124174652.58:endEditLabel (nativeTree)
    #@+node:ekr.20090124174652.59:onHeadChanged (nativeTree)
    # Tricky code: do not change without careful thought and testing.

    def onHeadChanged (self,p,undoType='Typing',s=None,e=None):

        '''Officially change a headline.'''

        trace = False and not g.unitTesting
        verbose = False

        c = self.c ; u = c.undoer
        if not p:
            if trace: g.trace('** no p')
            return

        item = self.getCurrentItem()
        if not item:
            if trace and verbose: g.trace('** no item')
            return
        if not e:
            e = self.getTreeEditorForItem(item)
        if not e:
            if trace and verbose: g.trace('** not editing')
            return

        s = unicode(e.text())
        self.closeEditorHelper(e,item)
        oldHead = p.h
        changed = s != oldHead
        if changed:
            if trace: g.trace('new',repr(s),'old',p.h,g.callers())
            p.initHeadString(s)
            item.setText(0,s) # Required to avoid full redraw.
            undoData = u.beforeChangeNodeContents(p,oldHead=oldHead)
            if not c.changed: c.setChanged(True)
            # New in Leo 4.4.5: we must recolor the body because
            # the headline may contain directives.
            c.frame.body.recolor(p,incremental=True)
            dirtyVnodeList = p.setDirty()
            u.afterChangeNodeContents(p,undoType,undoData,
                dirtyVnodeList=dirtyVnodeList)

        # This is a crucial shortcut.
        if g.unitTesting: return

        self.redraw_after_head_changed()

        if self.stayInTree:
            c.treeWantsFocus()
        else:
            c.bodyWantsFocus()
        c.outerUpdate()
    #@-node:ekr.20090124174652.59:onHeadChanged (nativeTree)
    #@+node:ekr.20090124174652.44:setItemForCurrentPosition (nativeTree)
    def setItemForCurrentPosition (self,scroll=True):

        '''Select the item for c.currentPosition()'''

        trace = False and not g.unitTesting
        verbose = False

        c = self.c ; p = c.currentPosition()

        if self.busy(): return

        if not p:
            if trace and verbose: g.trace('** no p')
            return None

        item = self.position2item(p)

        if not item:
            # This is not necessarily an error.
            # We often attempt to select an item before redrawing it.
            if trace and verbose: g.trace('** no item for',p)
            return None

        item2 = self.getCurrentItem()
        if item == item2:
            if trace and verbose: g.trace('no change',self.traceItem(item))
            if scroll:
                self.scrollToItem(item)
        else:
            try:
                self.selecting = True
                # This generates gui events, so we must use a lockout.
                self.setCurrentItemHelper(item)
                if scroll:
                    if trace: g.trace(self.traceItem(item),g.callers(4))
                    self.scrollToItem(item)
            finally:
                self.selecting = False

        return item
    #@-node:ekr.20090124174652.44:setItemForCurrentPosition (nativeTree)
    #@+node:ekr.20090124174652.60:setHeadline (nativeTree)
    def setHeadline (self,p,s):

        '''Force the actual text of the headline widget to p.h.'''

        trace = False and not g.unitTesting

        # This is used by unit tests to force the headline and p into alignment.
        if not p:
            if trace: g.trace('*** no p')
            return

        # Don't do this here: the caller should do it.
        # p.setHeadString(s)
        e = self.edit_widget(p)
        if e:
            if trace: g.trace('e',s)
            e.setAllText(s)
        else:
            item = self.position2item(p)
            if item:
                if trace: g.trace('item',s)
                self.setItemText(item,s)
            else:
                if trace: g.trace('*** failed. no item for %s' % p.h)
    #@-node:ekr.20090124174652.60:setHeadline (nativeTree)
    #@-node:ekr.20090124174652.52:Selecting & editing... (nativeTree)
    #@+node:ekr.20090124174652.78:Widget-dependent helpers
    #@+node:ekr.20090125063447.10:Drawing
    # These must be overridden in subclasses

    def clear (self):
        '''Clear all widgets in the tree.'''
        self.oops()

    def contractItem (self,item):
        '''Contract (collapse) the given item.'''
        self.oops()

    def expandItem (self,item):
        '''Expand the given item.'''
        self.oops()

    def repaint (self):
        '''Repaint the widget.'''
        self.oops()
    #@-node:ekr.20090125063447.10:Drawing
    #@+node:ekr.20090124174652.85:Icons
    #@+node:ekr.20090124174652.86:drawIcon
    def drawIcon (self,p):

        '''Redraw the icon at p.'''

        self.oops()
    #@-node:ekr.20090124174652.86:drawIcon
    #@+node:ekr.20090124174652.87:getIcon
    def getIcon(self,p):

        '''Return the proper icon for position p.'''

        self.oops()
    #@-node:ekr.20090124174652.87:getIcon
    #@+node:ekr.20090124174652.88:setItemIconHelper
    def setItemIconHelper (self,item,icon):

        '''Set the icon for the given item.'''

        self.oops()
    #@-node:ekr.20090124174652.88:setItemIconHelper
    #@-node:ekr.20090124174652.85:Icons
    #@+node:ekr.20090124174652.116:Items
    #@+node:ekr.20090125063447.12:childIndexOfItem
    def childIndexOfItem (self,item):

        '''Return the child index of item in item's parent.'''

        self.oops()

        return 0
    #@-node:ekr.20090125063447.12:childIndexOfItem
    #@+node:ekr.20090125063447.13:nthChildItem
    def nthChildItem (self,n,parent_item):

        '''Return the item that is the n'th child of parent_item'''

        self.oops()

    #@-node:ekr.20090125063447.13:nthChildItem
    #@+node:ekr.20090125063447.11:childItems
    def childItems (self,parent_item):

        '''Return the list of child items of the parent item,
        or the top-level items if parent_item is None.'''

        self.oops()
    #@-node:ekr.20090125063447.11:childItems
    #@+node:ekr.20090124174652.79:createTreeItem
    def createTreeItem(self,p,parent_item):

        '''Create a tree item for position p whose parent tree item is given.'''

        self.oops()
    #@-node:ekr.20090124174652.79:createTreeItem
    #@+node:ekr.20090124174652.80:createTreeEditorForItem
    def createTreeEditorForItem(self,item):

        '''Create an editor widget for the given tree item.'''

        self.oops()
    #@-node:ekr.20090124174652.80:createTreeEditorForItem
    #@+node:ekr.20090124174652.81:getCurrentItem
    def getCurrentItem (self):

        '''Return the currently selected tree item.'''

        self.oops()
    #@-node:ekr.20090124174652.81:getCurrentItem
    #@+node:ekr.20090127141022.10:getItemText
    def getItemText (self,item):

        '''Return the text of the item.'''

        self.oops()
    #@nonl
    #@-node:ekr.20090127141022.10:getItemText
    #@+node:ekr.20090126120517.23:getParentItem
    def getParentItem (self,item):

        '''Return the parent of the given item.'''

        self.oops()
    #@-node:ekr.20090126120517.23:getParentItem
    #@+node:ekr.20090124174652.82:getTreeEditorForItem
    def getTreeEditorForItem(self,item):

        '''Return the edit widget if it exists.

        Do *not* create one if it does not exist.'''

        self.oops()
    #@nonl
    #@-node:ekr.20090124174652.82:getTreeEditorForItem
    #@+node:ekr.20090201080444.11:scrollToItem
    def scrollToItem (self,item):

        self.oops()
    #@nonl
    #@-node:ekr.20090201080444.11:scrollToItem
    #@+node:ekr.20090124174652.83:setCurrentItemHelper
    def setCurrentItemHelper(self,item):

        '''Select the given item.'''

        self.oops()
    #@-node:ekr.20090124174652.83:setCurrentItemHelper
    #@+node:ekr.20090124174652.84:setItemText
    def setItemText (self,item,s):

        '''Set the headline text for the given item.'''

        self.oops()
    #@-node:ekr.20090124174652.84:setItemText
    #@+node:ekr.20090129164840.11:editLabelHelper
    def editLabelHelper(self,item,selectAll=False,selection=None):

        '''Called by nativeTree.editLabel to do gui-specific stuff
        relating to editing a headline.'''

        self.oops()
    #@-node:ekr.20090129164840.11:editLabelHelper
    #@-node:ekr.20090124174652.116:Items
    #@+node:ekr.20090124174652.123:Scroll bars
    def getScroll (self):

        '''Return the hPos,vPos for the tree's scrollbars.'''

        return 0,0

    def setHScroll (self,hPos):
        pass

    def setVScroll (self,vPos):
        pass
    #@-node:ekr.20090124174652.123:Scroll bars
    #@-node:ekr.20090124174652.78:Widget-dependent helpers
    #@+node:ekr.20090124174652.62:Widget-independent helpers
    #@+node:ekr.20090124174652.63:Associating items and positions
    #@@nocolor-node
    #@+at
    # 
    # item2position and position2item allow the drawing code to avoid storing 
    # any
    # positions, a crucial simplification.
    # 
    # Without the burden of keeping position up-to-date, or worse, 
    # recalculating them
    # all whenever the outline changes, the tree code becomes straightforward.
    #@-at
    #@nonl
    #@+node:ekr.20090124174652.64:item dict getters
    def item2tnode (self,item):
        v = self.item2vnodeDict.get(item)
        return v and v.t

    def item2vnode (self,item):
        return self.item2vnodeDict.get(item)

    def tnode2items(self,t):
        return self.tnode2itemsDict.get(t,[])

    def vnode2items(self,v):
        return self.vnode2itemsDict.get(v,[])

    def isValidItem (self,item):
        return item in self.item2vnodeDict
    #@-node:ekr.20090124174652.64:item dict getters
    #@+node:ekr.20090124174652.68:item2position (baseNativeTree)
    def item2position (self,item):

        '''Reconstitute a position given an item.'''

        trace = False
        stack = []
        childIndex = self.childIndexOfItem(item)
        v = self.item2vnode(item)
        if trace: g.trace(self.traceItem(item),repr(v))
        if not v:
            return self.error('no v for item')

        item = self.getParentItem(item)
        while item:
            n2 = self.childIndexOfItem(item)
            v2 = self.item2vnode(item)
            data = v2,n2
            if trace: g.trace(self.traceItem(item),n2,
                v2 and repr(v2 and v2.h))
            stack.insert(0,data)
            item = self.getParentItem(item)

        p = leoNodes.position(v,childIndex,stack)

        if not p:
            self.error('item2position failed. p: %s, v: %s, childIndex: %s stack: %s' % (
                p,v,childIndex,stack))

        return p
    #@-node:ekr.20090124174652.68:item2position (baseNativeTree)
    #@+node:ekr.20090124174652.70:position2item
    def position2item (self,p):

        '''Return the unique tree item associated with position p.

        Return None if there no such tree item.  This is *not* an error.'''

        parent_item = None

        for v,n in p.stack:
            parent_item = self.nthChildItem(n,parent_item)

        item = self.nthChildItem(p.childIndex(),parent_item)

        return item
    #@-node:ekr.20090124174652.70:position2item
    #@-node:ekr.20090124174652.63:Associating items and positions
    #@+node:ekr.20090124174652.71:Focus
    def getFocus(self):

        return g.app.gui.get_focus()

    findFocus = getFocus

    def hasFocus (self):

        return g.app.gui.get_focus(self.c)

    def setFocus (self):

        g.app.gui.set_focus(self.c,self.treeWidget)
    #@-node:ekr.20090124174652.71:Focus
    #@+node:ekr.20090124174652.72:Icons
    #@+node:ekr.20090124174652.73:drawItemIcon
    def drawItemIcon (self,p,item):

        '''Set the item's icon to p's icon.'''

        icon = self.getIcon(p)
        if icon:
            self.setItemIcon(item,icon)
    #@nonl
    #@-node:ekr.20090124174652.73:drawItemIcon
    #@+node:ekr.20090124174652.74:getIconImage
    def getIconImage(self,val):

        return g.app.gui.getIconImage(
            "box%02d.GIF" % val)
    #@nonl
    #@-node:ekr.20090124174652.74:getIconImage
    #@+node:ekr.20090124174652.75:getVnodeIcon
    def getVnodeIcon(self,p):

        '''Return the proper icon for position p.'''

        p.v.iconVal = val = p.v.computeIcon()
        return self.getIconImage(val)
    #@-node:ekr.20090124174652.75:getVnodeIcon
    #@+node:ekr.20090124174652.76:setItemIcon (nativeTree)
    def setItemIcon (self,item,icon):

        trace = False

        valid = item and self.isValidItem(item)

        if icon and valid:
            # Important: do not set lockouts here.
            # This will generate changed events,
            # but there is no itemChanged event handler.
            self.setItemIconHelper(item,icon)
        elif trace:
            # Apparently, icon can be None due to recent icon changes.
            if icon:
                g.trace('** item %s, valid: %s, icon: %s' % (
                    item and id(item) or '<no item>',valid,icon),
                    g.callers(4))
    #@-node:ekr.20090124174652.76:setItemIcon (nativeTree)
    #@+node:ekr.20090124174652.113:updateIcon
    def updateIcon (self,p,force=False):

        '''Update p's icon.'''

        if not p: return

        val = p.v.computeIcon()

        # The force arg is needed:
        # Leo's core may have updated p.v.iconVal.
        if p.v.iconVal == val and not force:
            return

        p.v.iconVal = val
        icon = self.getIconImage(val)
        # Update all cloned/joined items.
        items = self.tnode2items(p.v.t)
        for item in items:
            self.setItemIcon(item,icon)
    #@nonl
    #@-node:ekr.20090124174652.113:updateIcon
    #@+node:ekr.20090124174652.114:updateVisibleIcons
    def updateVisibleIcons (self,p):

        '''Update the icon for p and the icons
        for all visible descendants of p.'''

        self.updateIcon(p,force=True)

        if p.hasChildren() and p.isExpanded():
            for child in p.children_iter():
                self.updateVisibleIcons(child)
    #@-node:ekr.20090124174652.114:updateVisibleIcons
    #@-node:ekr.20090124174652.72:Icons
    #@+node:ekr.20090124174652.77:oops
    def oops(self):

        g.pr("leoTree oops: should be overridden in subclass",
            g.callers(4))
    #@-node:ekr.20090124174652.77:oops
    #@-node:ekr.20090124174652.62:Widget-independent helpers
    #@-others
#@-node:ekr.20090124174652.7:@thin baseNativeTree.py
#@-leo
