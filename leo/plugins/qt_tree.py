# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20140907131341.18707: * @file ../plugins/qt_tree.py
#@@first

'''Leo's Qt tree classes'''
#@+<< imports >>
#@+node:ekr.20140907131341.18709: ** << imports >> (qt_tree.py)
import leo.core.leoGlobals as g
import leo.core.leoFrame as leoFrame
import leo.core.leoNodes as leoNodes
import leo.core.leoPlugins as leoPlugins # Uses leoPlugins.TryNext.
import leo.plugins.qt_text as qt_text

# This crashes pylint...
    # from leo.core.leoQt import QtConst,QtWidgets
try:
    from PyQt5 import QtCore
    from PyQt5 import QtWidgets
    QtConst = QtCore.Qt
except ImportError:
    import PyQt4.QtGui as QtGui
    import PyQt4.QtCore as QtCore
    QtConst = QtCore.Qt
    QtWidgets = QtGui
#@-<< imports >>
#@+others
#@+node:ekr.20140907131341.18710: ** class BaseNativeTreeWidget(leoFrame.LeoTree)
class BaseNativeTreeWidget (leoFrame.LeoTree):

    """The base class for native tree widgets.

    See the ctor for more notes.
    """

    callbacksInjected = False # A class var.

    #@+others
    #@+node:ekr.20110605121601.17864: *3*  Birth... (nativeTree)
    #@+node:ekr.20110605121601.17865: *4* __init__ (nativeTree)
    def __init__(self,c,frame):
        '''Ctor for BaseNativeTreeWidget.'''
        # Init the base class.
        leoFrame.LeoTree.__init__(self,frame)
        # Components.
        self.c = c
        self.canvas = self # An official ivar used by Leo's core.
        # Configuration.
        self.auto_edit = c.config.getBool('single_click_auto_edits_headline',False)
        self.headlineWrapper = None
            # The wrapper class for headlines.
            # Must be set in subclasses.
        self.treeWidget = None
            # The underlying native tree widget.
            # Must be set in subclasses.

        # Widget independent status ivars...
        self.contracting = False
        # self.dragging = False
        self.expanding = False
        self.prev_v = None
        self.redrawing = False
        self.redrawCount = 0 # Count for debugging.
        self.revertHeadline = None # Previous headline text for abortEditLabel.
        self.selecting = False

        # Debugging...
        self.nodeDrawCount = 0
        self.traceCallersFlag = False # Enable traceCallers method.

        # Associating items with position and vnodes...
        self.item2positionDict = {}
        self.item2vnodeDict = {}
        self.position2itemDict = {}
        self.vnode2itemsDict = {} # values are lists of items.
        self.editWidgetsDict = {} # keys are native edit widgets, values are wrappers.

        self.setConfigIvars()
        self.setEditPosition(None) # Set positions returned by LeoTree.editPosition()
    #@+node:ekr.20110605121601.17866: *4* get_name (nativeTree)
    def getName (self):

        name = 'canvas(tree)' # Must start with canvas.

        return name
    #@+node:ekr.20110605121601.17867: *4* Called from Leo's core (nativeTree)
    def initAfterLoad (self):
        '''The official way of doing late initialization.'''
        pass
    #@+node:ekr.20110605121601.17868: *3* Debugging & tracing
    def error (self,s):
        if not g.app.unitTesting:
            g.trace('(BaseNativeTreeWidget) Error: %s' % (s),g.callers())

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
    #@+node:ekr.20110605121601.17869: *3* Config... (nativeTree)
    #@+node:ekr.20110605121601.17871: *4* setConfigIvars
    def setConfigIvars (self):

        c = self.c

        self.allow_clone_drags    = c.config.getBool('allow_clone_drags')
        self.enable_drag_messages = c.config.getBool("enable_drag_messages")
        self.select_all_text_when_editing_headlines = c.config.getBool(
            'select_all_text_when_editing_headlines')
        self.stayInTree     = c.config.getBool('stayInTreeAfterSelect')
        self.use_chapters   = c.config.getBool('use_chapters')
    #@+node:ekr.20110605121601.17872: *3* Drawing... (nativeTree)
    #@+node:ekr.20110605121601.17873: *4* full_redraw & helpers (nativeTree)
    def full_redraw (self,p=None,scroll=True,forceDraw=False):
        '''
        Redraw all visible nodes of the tree.
        Preserve the vertical scrolling unless scroll is True.
        '''
        trace = False and not g.app.unitTesting
        verbose = False
        c = self.c
        if g.app.disable_redraw:
            if trace: g.trace('*** disabled',g.callers())
            return
        if self.busy():
            return g.trace('*** full_redraw: busy!',g.callers())
        if p is None:
            p = c.currentPosition()
        elif c.hoistStack and len(c.hoistStack) == 1 and p.h.startswith('@chapter') and p.hasChildren():
            # Make sure the current position is visible.
            # Part of fix of bug 875323: Hoist an @chapter node leaves a non-visible node selected.
            p = p.firstChild()
            if trace: g.trace('selecting',p.h)
            c.frame.tree.select(p)
            c.setCurrentPosition(p)
        else:
            c.setCurrentPosition(p)
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
            g.trace('*** %s: scroll %5s drew %3s nodes in %s' % (
                self.redrawCount,scroll,self.nodeDrawCount,theTime),g.callers())
        return p # Return the position, which may have changed.

    # Compatibility
    redraw = full_redraw 
    redraw_now = full_redraw
    #@+node:ekr.20110605121601.17874: *5* drawChildren (nativeTree)
    def drawChildren (self,p,parent_item):
        '''Draw the children of p if they should be expanded.'''
        c = self.c
        trace = False and not g.unitTesting
        # if trace: g.trace('children: %5s expanded: %5s %s childIndex: %s' % (
            # p.hasChildren(),p.isExpanded(),p.h,p._childIndex))
        if not p:
            return g.trace('can not happen: no p')
        if p.hasChildren():
            if p.isExpanded():
                if trace: g.trace('expanded',p,p._childIndex)
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
    #@+node:ekr.20110605121601.17875: *5* drawNode
    def drawNode (self,p,parent_item):
        '''Draw the node p.'''
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
    #@+node:ekr.20110605121601.17876: *5* drawTopTree
    def drawTopTree (self,p):
        '''Draw the tree rooted at p.'''
        trace = False and not g.unitTesting
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
            if trace: g.trace(p)
            while p:
                self.drawTree(p)
                p.moveToNext()
        # This method always retains previous scroll position.
        self.setHScroll(hPos)
        self.setVScroll(vPos)
        self.repaint()
    #@+node:ekr.20110605121601.17877: *5* drawTree
    def drawTree (self,p,parent_item=None):
        
        if g.app.gui.isNullGui:
            return
        # Draw the (visible) parent node.
        item = self.drawNode(p,parent_item)
        # Draw all the visible children.
        self.drawChildren(p,parent_item=item)
    #@+node:ekr.20110605121601.17878: *5* initData
    def initData (self):

        # g.trace('*****')

        self.item2positionDict = {}
        self.item2vnodeDict = {}
        self.position2itemDict = {}
        self.vnode2itemsDict = {}
        self.editWidgetsDict = {}
    #@+node:ekr.20110605121601.17879: *5* rememberItem
    def rememberItem (self,p,item):

        trace = False and not g.unitTesting
        if trace: g.trace('id',id(item),p)

        v = p.v

        # Update position dicts.
        itemHash = self.itemHash(item)
        self.position2itemDict[p.key()] = item
        self.item2positionDict[itemHash] = p.copy() # was item

        # Update item2vnodeDict.
        self.item2vnodeDict[itemHash] = v # was item

        # Update vnode2itemsDict.
        d = self.vnode2itemsDict
        aList = d.get(v,[])
        if item in aList:
            g.trace('*** ERROR *** item already in list: %s, %s' % (item,aList))
        else:
            aList.append(item)
        d[v] = aList
    #@+node:ekr.20110605121601.17880: *4* redraw_after_contract
    def redraw_after_contract (self,p=None):

        trace = False and not g.unitTesting

        if self.redrawing:
            return

        item = self.position2item(p)

        if item:
            if trace: g.trace('contracting item',item,p and p.h or '<no p>')
            self.contractItem(item)
        else:
            # This is not an error.
            # We may have contracted a node that was not, in fact, visible.
            if trace: g.trace('***full redraw',p and p.h or '<no p>')
            self.full_redraw(scroll=False)
    #@+node:ekr.20110605121601.17881: *4* redraw_after_expand
    def redraw_after_expand (self,p=None):

        # Important, setting scrolling to False makes the problem *worse*
        self.full_redraw (p,scroll=True)
    #@+node:ekr.20110605121601.17882: *4* redraw_after_head_changed
    def redraw_after_head_changed (self):

        trace = False and not g.unitTesting

        if self.busy(): return

        c = self.c ; p = c.currentPosition()
        ew = self.edit_widget(p)

        if trace: g.trace(p.h)

        currentItem = self.getCurrentItem()

        if p:
            h = p.h # 2010/02/09: Fix bug 518823.
            for item in self.vnode2items(p.v):
                if self.isValidItem(item):
                    self.setItemText(item,h)

        # Bug fix: 2009/10/06
        self.redraw_after_icons_changed()
    #@+node:ekr.20110605121601.17883: *4* redraw_after_icons_changed (nativeTree)
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
            for p in c.rootPosition().self_and_siblings():
                # Updates icons in p and all visible descendants of p.
                self.updateVisibleIcons(p)
        finally:
            self.redrawing = False
    #@+node:ekr.20110605121601.17884: *4* redraw_after_select (nativeTree)
    # Important: this can not replace before/afterSelectHint.

    def redraw_after_select (self,p=None):

        '''Redraw the entire tree when an invisible node
        is selected.'''

        trace = False and not g.unitTesting

        if trace: g.trace('(LeoQtTree) busy? %s %s' % (
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
    #@+node:ekr.20110605121601.17885: *3* Event handlers... (nativeTree)
    #@+node:ekr.20110605121601.17886: *4* busy (nativeTree)
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
    #@+node:ekr.20110605121601.17887: *4* Click Box... (nativeTree)
    #@+node:ekr.20110605121601.17888: *5* onClickBoxClick
    def onClickBoxClick (self,event,p=None):

        if self.busy(): return

        c = self.c

        g.doHook("boxclick1",c=c,p=p,v=p,event=event)
        g.doHook("boxclick2",c=c,p=p,v=p,event=event)

        c.outerUpdate()
    #@+node:ekr.20110605121601.17889: *5* onClickBoxRightClick
    def onClickBoxRightClick(self, event, p=None):

        if self.busy(): return

        c = self.c

        g.doHook("boxrclick1",c=c,p=p,v=p,event=event)
        g.doHook("boxrclick2",c=c,p=p,v=p,event=event)

        c.outerUpdate()
    #@+node:ekr.20110605121601.17890: *5* onPlusBoxRightClick
    def onPlusBoxRightClick (self,event,p=None):

        if self.busy(): return

        c = self.c

        g.doHook('rclick-popup',c=c,p=p,event=event,context_menu='plusbox')

        c.outerUpdate()
    #@+node:ekr.20110605121601.17891: *4* Icon Box... (nativeTree)
    # For Qt, there seems to be no way to trigger these events.
    #@+node:ekr.20110605121601.17892: *5* onIconBoxClick (nativeTree)
    def onIconBoxClick (self,event,p=None):

        if self.busy(): return

        c = self.c

        g.doHook("iconclick1",c=c,p=p,v=p,event=event)
        g.doHook("iconclick2",c=c,p=p,v=p,event=event)

        c.outerUpdate()
    #@+node:ekr.20110605121601.17893: *5* onIconBoxRightClick (nativeTree)
    def onIconBoxRightClick (self,event,p=None):

        """Handle a right click in any outline widget."""

        if self.busy(): return

        c = self.c

        g.doHook("iconrclick1",c=c,p=p,v=p,event=event)
        g.doHook("iconrclick2",c=c,p=p,v=p,event=event)

        c.outerUpdate()
    #@+node:ekr.20110605121601.17894: *5* onIconBoxDoubleClick (nativeTree)
    def onIconBoxDoubleClick (self,event,p=None):

        if self.busy(): return

        c = self.c
        if not p: p = c.p

        if not g.doHook("icondclick1",c=c,p=p,v=p,event=event):
            self.endEditLabel()
            self.OnIconDoubleClick(p) # Call the method in the base class.

        g.doHook("icondclick2",c=c,p=p,v=p,event=event)

        c.outerUpdate()
    #@+node:ekr.20110605121601.17895: *4* onItemCollapsed (nativeTree)
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
            if p.isCloned():
                self.select(p) # Calls before/afterSelectHint.
                # 2010/02/04: Keep the expansion bits of all tree nodes in sync.
                self.full_redraw(scroll=False)
            else:
                self.select(p) # Calls before/afterSelectHint.    
        else:
            self.error('no p')

        c.outerUpdate()
    #@+node:ekr.20110605121601.17896: *4* onItemClicked (nativeTree)
    def onItemClicked (self,item,col,auto_edit=False):
        '''Handle a click in a BaseNativeTree widget item.'''
        # This is called after an item is selected.
        trace = False and not g.unitTesting
        verbose = False
        if self.busy(): return
        c = self.c
        # if trace: g.trace(self.traceItem(item),g.callers(4))
        try:
            self.selecting = True
            p = self.item2position(item)
            auto_edit = self.prev_v == p.v
            if p:
                self.prev_v = p.v
                event = None
                mods = g.app.gui.qtApp.keyboardModifiers()
                isCtrl = bool(mods & QtConst.ControlModifier)
                if trace: g.trace('auto_edit',auto_edit,'ctrl',isCtrl,p.h)
                # We could also add support for QtConst.ShiftModifier, QtConst.AltModifier	& QtConst.MetaModifier.
                if isCtrl:
                    if g.doHook("iconctrlclick1",c=c,p=p,v=p,event=event) is None:
                        c.frame.tree.OnIconCtrlClick(p) # Call the base class method.
                    g.doHook("iconctrlclick2",c=c,p=p,v=p,event=event)
                else:
                    # 2014/02/21: generate headclick1/2 instead of iconclick1/2
                    g.doHook("headclick1",c=c,p=p,v=p,event=event)
                    g.doHook("headclick2",c=c,p=p,v=p,event=event)
            else:
                auto_edit = None
                g.trace('*** no p')
            # 2011/05/27: click here is like ctrl-g.
            c.k.keyboardQuit(setFocus=False)
            c.treeWantsFocus() # 2011/05/08: Focus must stay in the tree!
            c.outerUpdate()
            # 2011/06/01: A second *single* click on a selected node
            # enters editing state.
            if auto_edit and self.auto_edit:
                e,wrapper = self.createTreeEditorForItem(item)
        finally:
            self.selecting = False
    #@+node:ekr.20110605121601.17897: *4* onItemDoubleClicked (nativeTree)
    def onItemDoubleClicked (self,item,col):
        '''Handle a double click in a BaseNativeTree widget item.'''
        trace = False and not g.unitTesting
        verbose = False
        if self.busy(): return
        c = self.c
        if trace: g.trace(col,self.traceItem(item))
        try:
            self.selecting = True
            e,wrapper = self.createTreeEditorForItem(item)
            if not e:
                g.trace('*** no e')
            p = self.item2position(item)
        # 2011/07/28: End the lockout here, not at the end.
        finally:
            self.selecting = False
        if p:
            # 2014/02/21: generate headddlick1/2 instead of icondclick1/2.
            event = None
            if g.doHook("headdclick1",c=c,p=p,v=p,event=event) is None:
                c.frame.tree.OnIconDoubleClick(p) # Call the base class method.
            g.doHook("headclick2",c=c,p=p,v=p,event=event)
        else:
            g.trace('*** no p')
        c.outerUpdate()
    #@+node:ekr.20110605121601.17898: *4* onItemExpanded (nativeTree)
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
    #@+node:ekr.20110605121601.17899: *4* onTreeSelect (nativeTree)
    def onTreeSelect(self):

        '''Select the proper position when a tree node is selected.'''

        trace = False and not g.unitTesting
        verbose = True

        if self.busy(): return

        c = self.c

        item = self.getCurrentItem()
        p = self.item2position(item)

        if p:
            # Important: do not set lockouts here.
            # Only methods that actually generate events should set lockouts.
            if trace: g.trace(self.traceItem(item))
            self.select(p)
                # This is a call to LeoTree.select(!!)
                # Calls before/afterSelectHint.
        else:
            self.error('no p for item: %s' % item)

        c.outerUpdate()
    #@+node:ekr.20110605121601.17900: *4* tree.OnPopup & allies (nativeTree)
    def OnPopup (self,p,event):

        """Handle right-clicks in the outline.

        This is *not* an event handler: it is called from other event handlers."""

        # Note: "headrclick" hooks handled by VNode callback routine.

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
    #@+node:ekr.20110605121601.17901: *5* OnPopupFocusLost
    #@+at
    # On Linux we must do something special to make the popup menu "unpost" if the
    # mouse is clicked elsewhere. So we have to catch the <FocusOut> event and
    # explicitly unpost. In order to process the <FocusOut> event, we need to be able
    # to find the reference to the popup window again, so this needs to be an
    # attribute of the tree object; hence, "self.popupMenu".
    # 
    # Aside: though Qt tries to be muli-platform, the interaction with different
    # window managers does cause small differences that will need to be compensated by
    # system specific application code. :-(
    #@@c

    # 20-SEP-2002 DTHEIN: This event handler is only needed for Linux.

    def OnPopupFocusLost(self,event=None):

        # self.popupMenu.unpost()
        pass
    #@+node:ekr.20110605121601.17902: *5* createPopupMenu
    def createPopupMenu (self,event):

        '''This might be a placeholder for plugins.  Or not :-)'''
    #@+node:ekr.20110605121601.17903: *5* enablePopupMenuItems
    def enablePopupMenuItems (self,v,event):

        """Enable and disable items in the popup menu."""

    #@+node:ekr.20110605121601.17904: *5* showPopupMenu
    def showPopupMenu (self,event):

        """Show a popup menu."""
    #@+node:ekr.20110605121601.17905: *3* Selecting & editing... (nativeTree)
    #@+node:ekr.20110605121601.17906: *4* afterSelectHint (nativeTree)
    def afterSelectHint (self,p,old_p):

        trace = False and not g.unitTesting
        c = self.c

        self.selecting = False

        if self.busy():
            self.error('afterSelectHint busy!: %s' % self.busy())

        if not p:
            return self.error('no p')

        if p != c.p:
            if trace: self.error(
                '(afterSelectHint) p != c.p\np:   %s\nc.p: %s\n' % (
                repr(p),repr(c.currentPosition())))
            p = c.p

        # if trace: g.trace(c.p.h,g.callers())

        # We don't redraw during unit testing: an important speedup.
        if c.expandAllAncestors(p) and not g.unitTesting:
            if trace: g.trace('***self.full_redraw')
            self.full_redraw(p)
        else:
            if trace: g.trace('*** c.outerUpdate')
            c.outerUpdate() # Bring the tree up to date.
            item = self.setItemForCurrentPosition(scroll=False)
    #@+node:ekr.20110605121601.17907: *4* beforeSelectHint (nativeTree)
    def beforeSelectHint (self,p,old_p):

        trace = False and not g.unitTesting

        if self.busy(): return

        c = self.c

        if trace: g.trace(p and p.h,c.p.h)

        # Disable onTextChanged.
        self.selecting = True
        self.prev_v = c.p.v
    #@+node:ekr.20110605121601.17908: *4* edit_widget (nativeTree)
    def edit_widget (self,p):

        """Returns the edit widget for position p."""

        trace = False and not g.unitTesting
        verbose = False

        c = self.c
        item = self.position2item(p)
        if item:
            e = self.getTreeEditorForItem(item)
            if e:
                # Create a wrapper widget for Leo's core.
                w = self.getWrapper(e,item)
                if trace: g.trace(w,p and p.h)
                return w
            else:
                # This is not an error
                # But warning: calling this method twice might not work!
                if trace and verbose: g.trace('no e for %s' % (p))
                return None
        else:
            if trace and verbose: self.error('no item for %s' % (p))
            return None
    #@+node:ekr.20110605121601.17909: *4* editLabel (nativeTree)
    def editLabel (self,p,selectAll=False,selection=None):
        """Start editing p's headline."""
        trace = False and not g.unitTesting
        if self.busy():
            if trace: g.trace('busy')
            return
        c = self.c
        c.outerUpdate()
            # Do any scheduled redraw.
            # This won't do anything in the new redraw scheme.
        item = self.position2item(p)
        if item:
            e,wrapper = self.editLabelHelper(item,selectAll,selection)
        else:
            e,wrapper = None,None # 2011/06/07: define wrapper here too.
            self.error('no item for %s' % p)
        if trace: g.trace('p: %s e: %s' % (p and p.h,e))
        if e:
            # A nice hack: just set the focus request.
            c.requestedFocusWidget = e       
        # 2012/09/27.
        g.app.gui.add_border(c,c.frame.tree.treeWidget)
        return e,wrapper # 2011/02/12
    #@+node:ekr.20110605121601.17910: *4* editPosition (nativeTree)
    def editPosition(self):

        c = self.c ; p = c.currentPosition()
        ew = self.edit_widget(p)
        return ew and p or None
    #@+node:ekr.20110605121601.17911: *4* endEditLabel (nativeTree)
    def endEditLabel (self):

        '''Override LeoTree.endEditLabel.

        End editing of the presently-selected headline.'''

        c = self.c ; p = c.currentPosition()
        self.onHeadChanged(p)
    #@+node:ekr.20110605121601.17912: *4* onHeadChanged (nativeTree)
    # Tricky code: do not change without careful thought and testing.

    def onHeadChanged (self,p,undoType='Typing',s=None,e=None):

        '''Officially change a headline.'''

        trace = False and not g.unitTesting
        verbose = True
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
            if trace and verbose: g.trace('(nativeTree) ** not editing')
            return
        s = g.u(e.text())
        self.closeEditorHelper(e,item)
        if g.doHook("headkey1",c=c,p=c.p,v=c.p,s=s):
            return
        oldHead = p.h
        changed = s != oldHead
        if changed:
            # New in Leo 4.10.1.
            if trace: g.trace('(nativeTree) new',repr(s),'old',repr(p.h))
            #@+<< truncate s if it has multiple lines >>
            #@+node:ekr.20120409185504.10028: *5* << truncate s if it has multiple lines >>
            # Remove trailing newlines before warning of truncation.
            while s and s[-1] == '\n':
                s = s[:-1]

            # Warn if there are multiple lines.
            i = s.find('\n')
            if i > -1:
                s = s[:i]
                if s != oldHead:
                    g.warning("truncating headline to one line")

            limit = 1000
            if len(s) > limit:
                s = s[:limit]
                if s != oldHead:
                    g.warning("truncating headline to",limit,"characters")
            #@-<< truncate s if it has multiple lines >>
            p.initHeadString(s)
            item.setText(0,s) # Required to avoid full redraw.
            undoData = u.beforeChangeNodeContents(p,oldHead=oldHead)
            if not c.changed: c.setChanged(True)
            # New in Leo 4.4.5: we must recolor the body because
            # the headline may contain directives.
            c.frame.body.recolor(p,incremental=True)
            dirtyVnodeList = p.setDirty()
            u.afterChangeNodeContents(p,undoType,undoData,
                dirtyVnodeList=dirtyVnodeList,inHead=True) # 2013/08/26.
        g.doHook("headkey2",c=c,p=c.p,v=c.p,s=s)
        # This is a crucial shortcut.
        if g.unitTesting: return
        if changed:
            self.redraw_after_head_changed()
        if 0: # Don't do this: it interferes with clicks, and is not needed.
            if self.stayInTree:
                c.treeWantsFocus()
            else:
                c.bodyWantsFocus()
        p.v.contentModified()
        c.outerUpdate()
    #@+node:ekr.20110605121601.17913: *4* setItemForCurrentPosition (nativeTree)
    def setItemForCurrentPosition (self,scroll=True):

        '''Select the item for c.currentPosition()'''

        trace = False and not g.unitTesting
        verbose = True

        c = self.c ; p = c.currentPosition()

        if self.busy():
            if trace and verbose: g.trace('** busy')
            return None

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
            if trace and verbose: g.trace('no change',self.traceItem(item),p.h)
            if scroll:
                self.scrollToItem(item)
        else:
            try:
                self.selecting = True
                # This generates gui events, so we must use a lockout.
                if trace and verbose: g.trace('setCurrentItem',self.traceItem(item),p.h)
                self.setCurrentItemHelper(item)
                    # Just calls self.setCurrentItem(item)
                if scroll:
                    if trace: g.trace(self.traceItem(item))
                    self.scrollToItem(item)
            finally:
                self.selecting = False

        # if trace: g.trace('item',repr(item))
        if not item: g.trace('*** no item')
        return item
    #@+node:ekr.20110605121601.17914: *4* setHeadline (nativeTree)
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
    #@+node:ekr.20110605121601.17915: *4* getSelectedPositions (nativeTree)
    def getSelectedPositions(self):
        items = self.getSelectedItems()
        pl = leoNodes.PosList(self.item2position(it) for it in items)
        return pl
    #@+node:ekr.20110605121601.17916: *3* Widget-dependent helpers
    #@+node:ekr.20110605121601.17917: *4* Drawing
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
    #@+node:ekr.20110605121601.17918: *4* Icons
    #@+node:ekr.20110605121601.17919: *5* drawIcon
    def drawIcon (self,p):

        '''Redraw the icon at p.'''

        self.oops()
    #@+node:ekr.20110605121601.17920: *5* getIcon
    def getIcon(self,p):

        '''Return the proper icon for position p.'''

        self.oops()
    #@+node:ekr.20110605121601.17921: *5* setItemIconHelper
    def setItemIconHelper (self,item,icon):

        '''Set the icon for the given item.'''

        self.oops()
    #@+node:ekr.20110605121601.17922: *4* Items
    #@+node:ekr.20110605121601.17923: *5* childIndexOfItem
    def childIndexOfItem (self,item):

        '''Return the child index of item in item's parent.'''

        self.oops()

        return 0
    #@+node:ekr.20110605121601.17924: *5* nthChildItem
    def nthChildItem (self,n,parent_item):

        '''Return the item that is the n'th child of parent_item'''

        self.oops()

    #@+node:ekr.20110605121601.17925: *5* closeEditorHelper
    def closeEditorHelper (self,e,item):

        self.oops()
    #@+node:ekr.20110605121601.17926: *5* childItems
    def childItems (self,parent_item):

        '''Return the list of child items of the parent item,
        or the top-level items if parent_item is None.'''

        self.oops()
    #@+node:ekr.20110605121601.17927: *5* createTreeItem
    def createTreeItem(self,p,parent_item):

        '''Create a tree item for position p whose parent tree item is given.'''

        self.oops()
    #@+node:ekr.20110605121601.17928: *5* createTreeEditorForItem
    def createTreeEditorForItem(self,item):

        '''Create an editor widget for the given tree item.'''

        self.oops()
        return None,None
    #@+node:ekr.20110605121601.17929: *5* getCurrentItem
    def getCurrentItem (self):

        '''Return the currently selected tree item.'''

        self.oops()
    #@+node:ekr.20110605121601.17930: *5* getItemText
    def getItemText (self,item):

        '''Return the text of the item.'''

        self.oops()
    #@+node:ekr.20110605121601.17931: *5* getParentItem
    def getParentItem (self,item):

        '''Return the parent of the given item.'''

        self.oops()
    #@+node:ekr.20110605121601.17932: *5* getSelectedItems
    def getSelectedItems(self):

        self.oops()
    #@+node:ekr.20110605121601.17933: *5* getWrapper
    def getWrapper (self,e,item):

        '''A do-nothing that can be over-ridden in subclasses.'''

        return e
    #@+node:ekr.20110605121601.17934: *5* getTreeEditorForItem
    def getTreeEditorForItem(self,item):

        '''Return the edit widget if it exists.

        Do *not* create one if it does not exist.'''

        self.oops()
    #@+node:ekr.20110605121601.17935: *5* scrollToItem
    def scrollToItem (self,item):

        self.oops()
    #@+node:ekr.20110605121601.17936: *5* setCurrentItemHelper
    def setCurrentItemHelper(self,item):

        '''Select the given item.'''

        self.oops()
    #@+node:ekr.20110605121601.17937: *5* setItemText
    def setItemText (self,item,s):

        '''Set the headline text for the given item.'''

        self.oops()
    #@+node:ekr.20110605121601.17938: *5* editLabelHelper
    def editLabelHelper(self,item,selectAll=False,selection=None):

        '''Called by nativeTree.editLabel to do gui-specific stuff
        relating to editing a headline.'''

        self.oops()
    #@+node:ekr.20110605121601.17939: *4* Scroll bars (nativeTree)
    # Do-nothings, for use by null classes.

    def getScroll (self):
        '''Return the hPos,vPos for the tree's scrollbars.'''
        return 0,0

    def setHScroll (self,hPos):
        pass

    def setVScroll (self,vPos):
        pass
    #@+node:ekr.20110605121601.17940: *4* wrapQLineEdit (nativeTree)
    def wrapQLineEdit (self,w):

        '''A wretched kludge for MacOs k.masterMenuHandler.'''
        c = self.c

        if isinstance(w,QtWidgets.QLineEdit):
            wrapper = self.edit_widget(c.p)
        else:
            wrapper = w

        # g.trace(wrapper)
        return wrapper

    #@+node:ekr.20110605121601.17941: *3* Widget-independent helpers
    #@+node:ekr.20110605121601.17942: *4* Associating items and positions
    #@+node:ekr.20110605121601.17943: *5* item dict getters
    def itemHash(self,item):
        return '%s at %s' % (repr(item),str(id(item)))

    def item2position(self,item):
        itemHash = self.itemHash(item)
        p = self.item2positionDict.get(itemHash) # was item
        # g.trace(item,p.h)
        return p

    def item2vnode (self,item):
        itemHash = self.itemHash(item)
        return self.item2vnodeDict.get(itemHash) # was item

    def position2item(self,p):
        item = self.position2itemDict.get(p.key())
        return item

    def vnode2items(self,v):
        return self.vnode2itemsDict.get(v,[])

    def isValidItem (self,item):
        itemHash = self.itemHash(item)
        return itemHash in self.item2vnodeDict # was item.
    #@+node:ekr.20110605121601.17944: *4* Focus (nativeTree)
    def getFocus(self):

        return g.app.gui.get_focus(self.c) # Bug fix: 2009/6/30

    findFocus = getFocus

    def setFocus (self):

        g.app.gui.set_focus(self.c,self.treeWidget)
    #@+node:ekr.20110605121601.17945: *4* Icons (nativeTree)
    #@+node:ekr.20110605121601.17946: *5* drawItemIcon
    def drawItemIcon (self,p,item):

        '''Set the item's icon to p's icon.'''

        icon = self.getIcon(p)
        if icon:
            self.setItemIcon(item,icon)
    #@+node:ekr.20110605121601.17947: *5* getIconImage
    def getIconImage(self,p):

        # User icons are not supported in the base class.
        if g.app.gui.isNullGui:
            return None
        else:
            return self.getStatusIconImage(p)
    #@+node:ekr.20110605121601.17948: *5* getStatusIconImage
    def getStatusIconImage (self,p):

        val = p.v.computeIcon()

        r = g.app.gui.getIconImage(
            "box%02d.GIF" % val)

        # g.trace(r)

        return r
    #@+node:ekr.20110605121601.17949: *5* getVnodeIcon
    def getVnodeIcon(self,p):

        '''Return the proper icon for position p.'''

        return self.getIcon(p)
    #@+node:ekr.20110605121601.17950: *5* setItemIcon (nativeTree)
    def setItemIcon (self,item,icon):

        trace = False and not g.unitTesting

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
    #@+node:ekr.20110605121601.17951: *5* updateIcon (nativeTree)
    def updateIcon (self,p,force=False):

        '''Update p's icon.'''

        trace = False and not g.unitTesting
        if not p: return

        val = p.v.computeIcon()

        # The force arg is needed:
        # Leo's core may have updated p.v.iconVal.
        if p.v.iconVal == val and not force:
            return

        icon = self.getIcon(p) # sets p.v.iconVal

        # Update all cloned items.
        items = self.vnode2items(p.v)
        for item in items:
            self.setItemIcon(item,icon)
    #@+node:ekr.20110605121601.17952: *5* updateVisibleIcons (nativeTree)
    def updateVisibleIcons (self,p):

        '''Update the icon for p and the icons
        for all visible descendants of p.'''

        self.updateIcon(p,force=True)

        if p.hasChildren() and p.isExpanded():
            for child in p.children():
                self.updateVisibleIcons(child)
    #@+node:ekr.20110605121601.17953: *4* oops
    def oops(self):

        g.pr("LeoTree oops: should be overridden in subclass",
            g.callers(4))
    #@-others
#@+node:ekr.20110605121601.18403: ** class LeoQtTree(BaseNativeTreeWidget)
class LeoQtTree (BaseNativeTreeWidget):

    """Leo qt tree class, a subclass of BaseNativeTreeWidget."""

    callbacksInjected = False # A class var.

    #@+others
    #@+node:ekr.20110605121601.18404: *3*  Birth (LeoQtTree)
    #@+node:ekr.20110605121601.18405: *4* ctor (LeoQtTree)
    def __init__(self,c,frame):
        '''Ctor for the LeoQtTree class.'''
        BaseNativeTreeWidget.__init__(self,c,frame)
            # Init the base class.
        # Components.
        self.headlineWrapper = qt_text.QHeadlineWrapper # This is a class.
        self.treeWidget = w = frame.top.leo_ui.treeWidget # An internal ivar.
            # w is a LeoQTreeWidget, a subclass of QTreeWidget.
        if 0: # Drag and drop
            w.setDragEnabled(True)
            w.viewport().setAcceptDrops(True)
            w.showDropIndicator = True
            w.setAcceptDrops(True)
            w.setDragDropMode(w.InternalMove)
            if 1: # Does not work
                def dropMimeData(self,data,action,row,col,parent):
                    g.trace()
                # w.dropMimeData = dropMimeData
                def mimeData(self,indexes):
                    g.trace()
        # Early inits...
        try: w.headerItem().setHidden(True)
        except Exception: pass
        w.setIconSize(QtCore.QSize(160,16))
    #@+node:ekr.20110605121601.18406: *4* qtTree.initAfterLoad
    def initAfterLoad (self):
        '''Do late-state inits.'''
        # Called by Leo's core.
        c = self.c
        w = c.frame.top
        tw = self.treeWidget
        if not LeoQtTree.callbacksInjected:
            LeoQtTree.callbacksInjected = True
            self.injectCallbacks() # A base class method.
        tw.itemDoubleClicked.connect(self.onItemDoubleClicked)
        tw.itemClicked.connect(self.onItemClicked)
        tw.itemSelectionChanged.connect(self.onTreeSelect)
        tw.itemCollapsed.connect(self.onItemCollapsed)
        tw.itemExpanded.connect(self.onItemExpanded)
        tw.customContextMenuRequested.connect(self.onContextMenu)
        # tw.onItemChanged.connect(self.onItemChanged)
        g.app.gui.setFilter(c,tw,self,tag='tree')
        # 2010/01/24: Do not set this here.
        # The read logic sets c.changed to indicate nodes have changed.
        # c.setChanged(False)
    #@+node:ekr.20110605121601.18407: *3* Widget-dependent helpers (LeoQtTree)
    #@+node:ekr.20110605121601.18408: *4* Drawing
    def clear (self):
        '''Clear all widgets in the tree.'''
        w = self.treeWidget
        w.clear()

    def repaint (self):
        '''Repaint the widget.'''
        w = self.treeWidget
        w.repaint()
        w.resizeColumnToContents(0) # 2009/12/22
    #@+node:ekr.20110605121601.18409: *4* Icons (LeoQtTree)
    #@+node:ekr.20110605121601.18410: *5* drawIcon
    def drawIcon (self,p):

        '''Redraw the icon at p.'''

        w = self.treeWidget
        itemOrTree = self.position2item(p) or w
        item = QtWidgets.QTreeWidgetItem(itemOrTree)
        icon = self.getIcon(p)
        self.setItemIcon(item,icon)

    #@+node:ekr.20110605121601.18411: *5* getIcon & helper (qtTree)
    def getIcon(self,p):

        '''Return the proper icon for position p.'''

        p.v.iconVal = val = p.v.computeIcon()
        return self.getCompositeIconImage(p,val)
    #@+node:ekr.20110605121601.18412: *6* getCompositeIconImage
    def getCompositeIconImage(self,p,val):
        '''Get the icon at position p.'''
        trace = False and not g.unitTesting
        userIcons = self.c.editCommands.getIconList(p)
        # don't take this shortcut - not theme aware, see getImageImage()
        # which is called below - TNB 20130313
        # if not userIcons:
        #     # if trace: g.trace('no userIcons')
        #     return self.getStatusIconImage(p)
        hash = [i['file'] for i in userIcons if i['where'] == 'beforeIcon']
        hash.append(str(val))
        hash.extend([i['file'] for i in userIcons if i['where'] == 'beforeHeadline'])
        hash = ':'.join(hash)
        if hash in g.app.gui.iconimages:
            icon = g.app.gui.iconimages[hash]
            if trace: g.trace('cached %s' % (icon))
            return icon
        images = [g.app.gui.getImageImage(i['file']) for i in userIcons
                 if i['where'] == 'beforeIcon']
        images.append(g.app.gui.getImageImage("box%02d.GIF" % val))
        images.extend([g.app.gui.getImageImage(i['file']) for i in userIcons
                      if i['where'] == 'beforeHeadline'])
        images = [z for z in images if z] # 2013/12/23: Remove missing images.
        if not images:
            return None
        width = sum([i.width() for i in images])
        height = max([i.height() for i in images])
        pix = QtGui.QPixmap(width,height)
        pix.fill(QtGui.QColor(0,0,0,0))  # transparent fill, rgbA
        painter = QtGui.QPainter(pix)
        x = 0
        for i in images:
            painter.drawPixmap(x,(height-i.height())//2,i)
            x += i.width()
        painter.end()
        icon = QtGui.QIcon(pix)
        g.app.gui.iconimages[hash] = icon
        if trace: g.trace('new %s' % (icon))
        return icon
    #@+node:ekr.20110605121601.18413: *5* setItemIconHelper (qtTree)
    def setItemIconHelper (self,item,icon):

        # Generates an item-changed event.
        # g.trace(id(icon))
        if item:
            item.setIcon(0,icon)
    #@+node:ekr.20110605121601.18414: *4* Items (LeoQtTree)
    #@+node:ekr.20110605121601.18415: *5* childIndexOfItem
    def childIndexOfItem (self,item):

        parent = item and item.parent()

        if parent:
            n = parent.indexOfChild(item)
        else:
            w = self.treeWidget
            n = w.indexOfTopLevelItem(item)

        return n

    #@+node:ekr.20110605121601.18416: *5* childItems
    def childItems (self,parent_item):

        '''Return the list of child items of the parent item,
        or the top-level items if parent_item is None.'''

        if parent_item:
            n = parent_item.childCount()
            items = [parent_item.child(z) for z in range(n)]
        else:
            w = self.treeWidget
            n = w.topLevelItemCount()
            items = [w.topLevelItem(z) for z in range(n)]

        return items
    #@+node:ekr.20110605121601.18417: *5* closeEditorHelper (LeoQtTree)
    def closeEditorHelper (self,e,item):
        'End editing of the underlying QLineEdit widget for the headline.'''
        w = self.treeWidget
        if e:
            w.closeEditor(e,QtWidgets.QAbstractItemDelegate.NoHint)
            try:
                # work around https://bugs.launchpad.net/leo-editor/+bug/1041906
                # underlying C/C++ object has been deleted
                w.setItemWidget(item,0,None)
                    # Make sure e is never referenced again.
                w.setCurrentItem(item)
            except RuntimeError:
                if 1: # Testing.
                    g.es_exception()
                else:
                    # Recover silently even if there is a problem.
                    pass
    #@+node:ekr.20110605121601.18418: *5* connectEditorWidget & helper
    def connectEditorWidget(self,e,item):

        if not e:
            return g.trace('can not happen: no e')
        # Hook up the widget.
        wrapper = self.getWrapper(e,item)
        def editingFinishedCallback(e=e,item=item,self=self,wrapper=wrapper):
            # g.trace(wrapper,g.callers(5))
            c = self.c
            w = self.treeWidget
            self.onHeadChanged(p=c.p,e=e)
            w.setCurrentItem(item)
        e.editingFinished.connect(editingFinishedCallback)
        return wrapper # 2011/02/12
    #@+node:ekr.20110605121601.18419: *5* contractItem & expandItem
    def contractItem (self,item):

        # g.trace(g.callers(4))

        self.treeWidget.collapseItem(item)

    def expandItem (self,item):

        # g.trace(g.callers(4))

        self.treeWidget.expandItem(item)
    #@+node:ekr.20110605121601.18420: *5* createTreeEditorForItem (LeoQtTree)
    def createTreeEditorForItem(self,item):

        trace = False and not g.unitTesting

        w = self.treeWidget
        w.setCurrentItem(item) # Must do this first.
        w.editItem(item)
        e = w.itemWidget(item,0)
        e.setObjectName('headline')
        wrapper = self.connectEditorWidget(e,item)

        if trace: g.trace(e,wrapper)

        return e,wrapper
    #@+node:ekr.20110605121601.18421: *5* createTreeItem
    def createTreeItem(self,p,parent_item):

        trace = False and not g.unitTesting

        w = self.treeWidget
        itemOrTree = parent_item or w
        item = QtWidgets.QTreeWidgetItem(itemOrTree)
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)

        if trace: g.trace(id(item),p.h,g.callers(4))
        try:
            g.visit_tree_item(self.c, p, item)
        except leoPlugins.TryNext:
            pass
        #print "item",item
        return item
    #@+node:ekr.20110605121601.18422: *5* editLabelHelper (leoQtTree)
    def editLabelHelper (self,item,selectAll=False,selection=None):
        '''
        Called by nativeTree.editLabel to do
        gui-specific stuff.
        '''
        trace = False and not g.unitTesting
        c,vc = self.c,self.c.vimCommands
        w = self.treeWidget
        w.setCurrentItem(item)
            # Must do this first.
            # This generates a call to onTreeSelect.
        w.editItem(item)
            # Generates focus-in event that tree doesn't report.
        e = w.itemWidget(item,0) # A QLineEdit.
        if e:
            s = e.text() ; len_s = len(s)
            if s == 'newHeadline': selectAll=True
            if selection:
                # pylint: disable=unpacking-non-sequence
                i,j,ins = selection
                start,n = i,abs(i-j)
                    # Not right for backward searches.
            elif selectAll: start,n,ins = 0,len_s,len_s
            else:           start,n,ins = len_s,0,len_s
            e.setObjectName('headline')
            e.setSelection(start,n)
            # e.setCursorPosition(ins) # Does not work.
            e.setFocus()
            wrapper = self.connectEditorWidget(e,item) # Hook up the widget.
            if vc and c.vim_mode: #  and selectAll
                # For now, *always* enter insert mode.
                if vc.is_text_wrapper(wrapper):
                    vc.begin_insert_mode(w=wrapper)
                else:
                    g.trace('not a text widget!',wrapper)
        if trace: g.trace(e,wrapper)
        return e,wrapper # 2011/02/11
    #@+node:ekr.20110605121601.18423: *5* getCurrentItem
    def getCurrentItem (self):

        w = self.treeWidget
        return w.currentItem()
    #@+node:ekr.20110605121601.18424: *5* getItemText
    def getItemText (self,item):

        '''Return the text of the item.'''

        if item:
            return g.u(item.text(0))
        else:
            return '<no item>'
    #@+node:ekr.20110605121601.18425: *5* getParentItem
    def getParentItem(self,item):

        return item and item.parent()
    #@+node:ekr.20110605121601.18426: *5* getSelectedItems
    def getSelectedItems(self):
        w = self.treeWidget    
        return w.selectedItems()
    #@+node:ekr.20110605121601.18427: *5* getTreeEditorForItem (LeoQtTree)
    def getTreeEditorForItem(self,item):

        '''Return the edit widget if it exists.
        Do *not* create one if it does not exist.'''

        trace = False and not g.unitTesting
        w = self.treeWidget
        e = w.itemWidget(item,0)
        if trace and e: g.trace(e.__class__.__name__)
        return e
    #@+node:ekr.20110605121601.18428: *5* getWrapper (LeoQtTree)
    def getWrapper (self,e,item):
        '''Return headlineWrapper that wraps e (a QLineEdit).'''
        trace = False and not g.unitTesting
        c = self.c
        if e:
            wrapper = self.editWidgetsDict.get(e)
            if wrapper:
                pass # g.trace('old wrapper',e,wrapper)
            else:
                if item:
                    # 2011/02/12: item can be None.
                    wrapper = self.headlineWrapper(c,item,name='head',widget=e)
                    if trace: g.trace('new wrapper',e,wrapper)
                    self.editWidgetsDict[e] = wrapper
                else:
                    if trace: g.trace('no item and no wrapper',
                        e,self.editWidgetsDict)
            return wrapper
        else:
            g.trace('no e')
            return None
    #@+node:ekr.20110605121601.18429: *5* nthChildItem
    def nthChildItem (self,n,parent_item):

        children = self.childItems(parent_item)

        if n < len(children):
            item = children[n]
        else:
            # This is **not* an error.
            # It simply means that we need to redraw the tree.
            item = None

        return item
    #@+node:ekr.20110605121601.18430: *5* scrollToItem (LeoQtTree)
    def scrollToItem (self,item):

        w = self.treeWidget

        # g.trace(self.traceItem(item),g.callers(4))

        hPos,vPos = self.getScroll()

        w.scrollToItem(item,w.PositionAtCenter)

        self.setHScroll(0)
    #@+node:ekr.20110605121601.18431: *5* setCurrentItemHelper (LeoQtTree)
    def setCurrentItemHelper(self,item):

        w = self.treeWidget
        w.setCurrentItem(item)
    #@+node:ekr.20110605121601.18432: *5* setItemText
    def setItemText (self,item,s):

        if item:
            item.setText(0,s)
    #@+node:ekr.20110605121601.18433: *4* Scroll bars (LeoQtTree)
    #@+node:ekr.20110605121601.18434: *5* getSCroll
    def getScroll (self):

        '''Return the hPos,vPos for the tree's scrollbars.'''

        w = self.treeWidget
        hScroll = w.horizontalScrollBar()
        vScroll = w.verticalScrollBar()
        hPos = hScroll.sliderPosition()
        vPos = vScroll.sliderPosition()
        return hPos,vPos
    #@+node:ekr.20110605121601.18435: *5* setH/VScroll
    def setHScroll (self,hPos):
        w = self.treeWidget
        hScroll = w.horizontalScrollBar()
        hScroll.setValue(hPos)

    def setVScroll (self,vPos):
        # g.trace(vPos)
        w = self.treeWidget
        vScroll = w.verticalScrollBar()
        vScroll.setValue(vPos)
    #@+node:btheado.20111110215920.7164: *5* scrollDelegate (LeoQtTree)
    def scrollDelegate (self,kind):

        '''Scroll a QTreeWidget up or down or right or left.
        kind is in ('down-line','down-page','up-line','up-page', 'right', 'left')
        '''
        c = self.c ; w = self.treeWidget
        if kind in ('left', 'right'):
            hScroll = w.horizontalScrollBar()
            if kind == 'right':
                delta = hScroll.pageStep()
            else: 
                delta = -hScroll.pageStep()
            hScroll.setValue(hScroll.value() + delta)
        else:
            vScroll = w.verticalScrollBar()
            h = w.size().height()
            lineSpacing = w.fontMetrics().lineSpacing()
            n = h/lineSpacing
            if   kind == 'down-half-page': delta = n/2
            elif kind == 'down-line':      delta = 1
            elif kind == 'down-page':      delta = n
            elif kind == 'up-half-page':   delta = -n/2
            elif kind == 'up-line':        delta = -1
            elif kind == 'up-page':        delta = -n
            else:
                delta = 0 ; g.trace('bad kind:',kind)
            val = vScroll.value()
            # g.trace(kind,n,h,lineSpacing,delta,val)
            vScroll.setValue(val+delta)
        c.treeWantsFocus()
    #@+node:ekr.20110605121601.18437: *4* onContextMenu (LeoQtTree)
    def onContextMenu(self, point):
        c = self.c
        w = self.treeWidget
        handlers = g.tree_popup_handlers    
        menu = QtWidgets.QMenu()
        menuPos = w.mapToGlobal(point)
        if not handlers:
            menu.addAction("No popup handlers")
        p = c.p.copy()
        done = set()
        for h in handlers:
            # every handler has to add it's QActions by itself
            if h in done:
                # do not run the same handler twice
                continue
            h(c,p,menu)
        menu.popup(menuPos)
        self._contextmenu = menu
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 80
#@-leo
