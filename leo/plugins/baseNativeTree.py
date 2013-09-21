# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20110605121601.17863: * @file ../plugins/baseNativeTree.py
#@@first

'''Base classes for native tree widgets.'''

#@@language python
#@@tabwidth -4
#@@pagewidth 80

#@+<< imports >>
#@+node:ekr.20120219194520.10465: ** << imports >> (baseNativeTree.py)
import leo.core.leoGlobals as g

import leo.core.leoFrame as leoFrame
import leo.core.leoNodes as leoNodes

import PyQt4.QtGui as QtGui
import PyQt4.QtCore as QtCore
#@-<< imports >>

class baseNativeTreeWidget (leoFrame.leoTree):

    """The base class for native tree widgets.

    See the ctor for more notes.
    """

    callbacksInjected = False # A class var.

    #@+others
    #@+node:ekr.20110605121601.17864: **  Birth... (nativeTree)
    #@+node:ekr.20110605121601.17865: *3* __init__ (nativeTree)
    def __init__(self,c,frame):

        # Init the base class.
        leoFrame.leoTree.__init__(self,frame)

        # Components.
        self.c = c
        self.canvas = self # An official ivar used by Leo's core.

        # Configuration.
        self.auto_edit = c.config.getBool('single_click_auto_edits_headline',False)

        # Subclasses should define headline wrappers to
        # be a subclass of leoFrame.baseTextWidget.
        self.headlineWrapper = leoFrame.baseTextWidget

        # Subclasses should define .treeWidget to be the underlying
        # native tree widget.
        self.treeWidget = None

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
        self.setEditPosition(None) # Set positions returned by leoTree.editPosition()
    #@+node:ekr.20110605121601.17866: *3* get_name (nativeTree)
    def getName (self):

        name = 'canvas(tree)' # Must start with canvas.

        return name
    #@+node:ekr.20110605121601.17867: *3* Called from Leo's core (nativeTree)
    def initAfterLoad (self):
        '''The official way of doing late initialization.'''
        pass
    #@+node:ekr.20110605121601.17868: ** Debugging & tracing
    def error (self,s):
        if not g.app.unitTesting:
            g.trace('(baseNativeTree) Error: %s' % (s),g.callers())

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
    #@+node:ekr.20110605121601.17869: ** Config... (nativeTree)
    #@+node:ekr.20110605121601.17871: *3* setConfigIvars
    def setConfigIvars (self):

        c = self.c

        self.allow_clone_drags    = c.config.getBool('allow_clone_drags')
        self.enable_drag_messages = c.config.getBool("enable_drag_messages")
        self.select_all_text_when_editing_headlines = c.config.getBool(
            'select_all_text_when_editing_headlines')
        self.stayInTree     = c.config.getBool('stayInTreeAfterSelect')
        self.use_chapters   = c.config.getBool('use_chapters')
    #@+node:ekr.20110605121601.17872: ** Drawing... (nativeTree)
    #@+node:ekr.20110605121601.17873: *3* full_redraw & helpers
    # forceDraw not used. It is used in the Tk code.

    def full_redraw (self,p=None,scroll=True,forceDraw=False):

        '''Redraw all visible nodes of the tree.

        Preserve the vertical scrolling unless scroll is True.'''

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
    #@+node:ekr.20110605121601.17874: *4* drawChildren
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
    #@+node:ekr.20110605121601.17875: *4* drawNode
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
    #@+node:ekr.20110605121601.17876: *4* drawTopTree
    def drawTopTree (self,p):

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
    #@+node:ekr.20110605121601.17877: *4* drawTree
    def drawTree (self,p,parent_item=None):
        
        if g.app.gui.isNullGui:
            return

        # Draw the (visible) parent node.
        item = self.drawNode(p,parent_item)

        # Draw all the visible children.
        self.drawChildren(p,parent_item=item)
    #@+node:ekr.20110605121601.17878: *4* initData
    def initData (self):

        # g.trace('*****')

        self.item2positionDict = {}
        self.item2vnodeDict = {}
        self.position2itemDict = {}
        self.vnode2itemsDict = {}
        self.editWidgetsDict = {}
    #@+node:ekr.20110605121601.17879: *4* rememberItem
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
    #@+node:ekr.20110605121601.17880: *3* redraw_after_contract
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
    #@+node:ekr.20110605121601.17881: *3* redraw_after_expand
    def redraw_after_expand (self,p=None):

        # Important, setting scrolling to False makes the problem *worse*
        self.full_redraw (p,scroll=True)
    #@+node:ekr.20110605121601.17882: *3* redraw_after_head_changed
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
    #@+node:ekr.20110605121601.17883: *3* redraw_after_icons_changed
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
    #@+node:ekr.20110605121601.17884: *3* redraw_after_select (nativeTree)
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
    #@+node:ekr.20110605121601.17885: ** Event handlers... (nativeTree)
    #@+node:ekr.20110605121601.17886: *3* busy (nativeTree)
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
    #@+node:ekr.20110605121601.17887: *3* Click Box... (nativeTree)
    #@+node:ekr.20110605121601.17888: *4* onClickBoxClick
    def onClickBoxClick (self,event,p=None):

        if self.busy(): return

        c = self.c

        g.doHook("boxclick1",c=c,p=p,v=p,event=event)
        g.doHook("boxclick2",c=c,p=p,v=p,event=event)

        c.outerUpdate()
    #@+node:ekr.20110605121601.17889: *4* onClickBoxRightClick
    def onClickBoxRightClick(self, event, p=None):

        if self.busy(): return

        c = self.c

        g.doHook("boxrclick1",c=c,p=p,v=p,event=event)
        g.doHook("boxrclick2",c=c,p=p,v=p,event=event)

        c.outerUpdate()
    #@+node:ekr.20110605121601.17890: *4* onPlusBoxRightClick
    def onPlusBoxRightClick (self,event,p=None):

        if self.busy(): return

        c = self.c

        g.doHook('rclick-popup',c=c,p=p,event=event,context_menu='plusbox')

        c.outerUpdate()
    #@+node:ekr.20110605121601.17891: *3* Icon Box... (nativeTree)
    # For Qt, there seems to be no way to trigger these events.
    #@+node:ekr.20110605121601.17892: *4* onIconBoxClick (nativeTree)
    def onIconBoxClick (self,event,p=None):

        if self.busy(): return

        c = self.c

        g.doHook("iconclick1",c=c,p=p,v=p,event=event)
        g.doHook("iconclick2",c=c,p=p,v=p,event=event)

        c.outerUpdate()
    #@+node:ekr.20110605121601.17893: *4* onIconBoxRightClick (nativeTree)
    def onIconBoxRightClick (self,event,p=None):

        """Handle a right click in any outline widget."""

        if self.busy(): return

        c = self.c

        g.doHook("iconrclick1",c=c,p=p,v=p,event=event)
        g.doHook("iconrclick2",c=c,p=p,v=p,event=event)

        c.outerUpdate()
    #@+node:ekr.20110605121601.17894: *4* onIconBoxDoubleClick (nativeTree)
    def onIconBoxDoubleClick (self,event,p=None):

        if self.busy(): return

        c = self.c
        if not p: p = c.p

        if not g.doHook("icondclick1",c=c,p=p,v=p,event=event):
            self.endEditLabel()
            self.OnIconDoubleClick(p) # Call the method in the base class.

        g.doHook("icondclick2",c=c,p=p,v=p,event=event)

        c.outerUpdate()
    #@+node:ekr.20110605121601.17895: *3* onItemCollapsed (nativeTree)
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
    #@+node:ekr.20110605121601.17896: *3* onItemClicked (nativeTree)
    def onItemClicked (self,item,col,auto_edit=False):

        # This is called after an item is selected.
        trace = False and not g.unitTesting ; verbose = False

        if self.busy(): return

        c = self.c
        qt = QtCore.Qt
        # if trace: g.trace(self.traceItem(item),g.callers(4))
        try:
            self.selecting = True
            p = self.item2position(item)
            auto_edit = self.prev_v == p.v
            if p:
                self.prev_v = p.v
                event = None
                mods = g.app.gui.qtApp.keyboardModifiers()
                isCtrl = bool(mods & qt.ControlModifier)
                if trace: g.trace('auto_edit',auto_edit,'ctrl',isCtrl,p.h)
                # We could also add support for qt.ShiftModifier, qt.AltModifier	& qt.MetaModifier.
                if isCtrl:
                    if g.doHook("iconctrlclick1",c=c,p=p,v=p,event=event) is None:
                        c.frame.tree.OnIconCtrlClick(p) # Call the base class method.
                    g.doHook("iconctrlclick2",c=c,p=p,v=p,event=event)
                else:
                    if g.doHook("iconclick1",c=c,p=p,v=p,event=event) is None:
                        pass
                        # if c.positionExists(p): c.selectPosition(p) # 2011/03/07
                        # c.frame.tree.OnIconDoubleClick(p) # Call the base class method.
                    g.doHook("iconclick2",c=c,p=p,v=p,event=event)
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
    #@+node:ekr.20110605121601.17897: *3* onItemDoubleClicked (nativeTree)
    def onItemDoubleClicked (self,item,col):

        trace = False and not g.unitTesting
        verbose = False

        if self.busy(): return

        c = self.c

        if trace: g.trace(col,self.traceItem(item))

        try:
            self.selecting = True

            e,wrapper = self.createTreeEditorForItem(item)
            if e:
                wrapper.setEditorColors(
                    c.k.insert_mode_bg_color,
                    c.k.insert_mode_fg_color)
            else:
                g.trace('*** no e')

            p = self.item2position(item)

        # 2011/07/28: End the lockout here, not at the end.
        finally:
            self.selecting = False

        if p:
            event = None
            if g.doHook("icondclick1",c=c,p=p,v=p,event=event) is None:
                c.frame.tree.OnIconDoubleClick(p) # Call the base class method.
            g.doHook("icondclick2",c=c,p=p,v=p,event=event)
        else:
            g.trace('*** no p')

        c.outerUpdate()
    #@+node:ekr.20110605121601.17898: *3* onItemExpanded (nativeTree)
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
    #@+node:ekr.20110605121601.17899: *3* onTreeSelect (nativeTree)
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
                # This is a call to leoTree.select(!!)
                # Calls before/afterSelectHint.
        else:
            self.error('no p for item: %s' % item)

        c.outerUpdate()
    #@+node:ekr.20110605121601.17900: *3* tree.OnPopup & allies (nativeTree)
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
    #@+node:ekr.20110605121601.17901: *4* OnPopupFocusLost
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
    #@+node:ekr.20110605121601.17902: *4* createPopupMenu
    def createPopupMenu (self,event):

        '''This might be a placeholder for plugins.  Or not :-)'''
    #@+node:ekr.20110605121601.17903: *4* enablePopupMenuItems
    def enablePopupMenuItems (self,v,event):

        """Enable and disable items in the popup menu."""

    #@+node:ekr.20110605121601.17904: *4* showPopupMenu
    def showPopupMenu (self,event):

        """Show a popup menu."""
    #@+node:ekr.20110715053352.16519: ** Event wrappers ... (nativeTree)
    # These are used by leoEditCommands.
    #@+node:ekr.20110715053352.16518: *3* onDoubleClickHeadline (nativeTree)
    def onDoubleClickHeadline (self,event,p):

        c = self.c

        try:
            if not g.doHook("headdclick1",c=c,p=p,v=p,event=event):
                self.editLabel(p,selectAll=True,selection=None)
            g.doHook("headdclick2",c=c,p=p,v=p,event=event)
        except:
            g.es_event_exception("headdclick")
    #@+node:ekr.20110715053352.16520: *3* onHeadlineClick (nativeTree)
    def onHeadlineClick (self,event,p):

        c = self.c

        try:
            g.doHook("headclick1",c=c,p=p,v=p,event=event)
            g.doHook("headclick2",c=c,p=p,v=p,event=event)
        except:
            g.es_event_exception("headclick")
    #@+node:ekr.20110715053352.16521: *3* onHeadlineRightClick (nativeTree)
    def onHeadlineRightClick (self,event,p):

        c = self.c

        try:
            g.doHook("headrclick1",c=c,p=p,v=p,event=event)
            g.doHook("headrclick2",c=c,p=p,v=p,event=event)
        except:
            g.es_event_exception("headrclick")
    #@+node:ekr.20110605121601.17905: ** Selecting & editing... (nativeTree)
    #@+node:ekr.20110605121601.17906: *3* afterSelectHint (nativeTree)
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
    #@+node:ekr.20110605121601.17907: *3* beforeSelectHint (nativeTree)
    def beforeSelectHint (self,p,old_p):

        trace = False and not g.unitTesting

        if self.busy(): return

        c = self.c

        if trace: g.trace(p and p.h,c.p.h)

        # Disable onTextChanged.
        self.selecting = True
        self.prev_v = c.p.v
    #@+node:ekr.20110605121601.17908: *3* edit_widget (nativeTree)
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
    #@+node:ekr.20110605121601.17909: *3* editLabel (nativeTree)
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
    #@+node:ekr.20110605121601.17910: *3* editPosition (nativeTree)
    def editPosition(self):

        c = self.c ; p = c.currentPosition()
        ew = self.edit_widget(p)
        return ew and p or None
    #@+node:ekr.20110605121601.17911: *3* endEditLabel (nativeTree)
    def endEditLabel (self):

        '''Override leoTree.endEditLabel.

        End editing of the presently-selected headline.'''

        c = self.c ; p = c.currentPosition()

        self.onHeadChanged(p)
    #@+node:ekr.20110605121601.17912: *3* onHeadChanged (nativeTree)
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
        if g.doHook("headkey1",c=c,p=c.p,v=c.p,s=s):
            return
        self.closeEditorHelper(e,item)
        oldHead = p.h
        changed = s != oldHead
        if changed:
            # New in Leo 4.10.1.
            if trace: g.trace('(nativeTree) new',repr(s),'old',repr(p.h))
            #@+<< truncate s if it has multiple lines >>
            #@+node:ekr.20120409185504.10028: *4* << truncate s if it has multiple lines >>
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
    #@+node:ekr.20110605121601.17913: *3* setItemForCurrentPosition (nativeTree)
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
    #@+node:ekr.20110605121601.17914: *3* setHeadline (nativeTree)
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
    #@+node:ekr.20110605121601.17915: *3* getSelectedPositions (nativeTree)
    def getSelectedPositions(self):
        items = self.getSelectedItems()
        pl = leoNodes.poslist(self.item2position(it) for it in items)
        return pl
    #@+node:ekr.20110605121601.17916: ** Widget-dependent helpers
    #@+node:ekr.20110605121601.17917: *3* Drawing
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
    #@+node:ekr.20110605121601.17918: *3* Icons
    #@+node:ekr.20110605121601.17919: *4* drawIcon
    def drawIcon (self,p):

        '''Redraw the icon at p.'''

        self.oops()
    #@+node:ekr.20110605121601.17920: *4* getIcon
    def getIcon(self,p):

        '''Return the proper icon for position p.'''

        self.oops()
    #@+node:ekr.20110605121601.17921: *4* setItemIconHelper
    def setItemIconHelper (self,item,icon):

        '''Set the icon for the given item.'''

        self.oops()
    #@+node:ekr.20110605121601.17922: *3* Items
    #@+node:ekr.20110605121601.17923: *4* childIndexOfItem
    def childIndexOfItem (self,item):

        '''Return the child index of item in item's parent.'''

        self.oops()

        return 0
    #@+node:ekr.20110605121601.17924: *4* nthChildItem
    def nthChildItem (self,n,parent_item):

        '''Return the item that is the n'th child of parent_item'''

        self.oops()

    #@+node:ekr.20110605121601.17925: *4* closeEditorHelper
    def closeEditorHelper (self,e,item):

        self.oops()
    #@+node:ekr.20110605121601.17926: *4* childItems
    def childItems (self,parent_item):

        '''Return the list of child items of the parent item,
        or the top-level items if parent_item is None.'''

        self.oops()
    #@+node:ekr.20110605121601.17927: *4* createTreeItem
    def createTreeItem(self,p,parent_item):

        '''Create a tree item for position p whose parent tree item is given.'''

        self.oops()
    #@+node:ekr.20110605121601.17928: *4* createTreeEditorForItem
    def createTreeEditorForItem(self,item):

        '''Create an editor widget for the given tree item.'''

        self.oops()
        return None,None
    #@+node:ekr.20110605121601.17929: *4* getCurrentItem
    def getCurrentItem (self):

        '''Return the currently selected tree item.'''

        self.oops()
    #@+node:ekr.20110605121601.17930: *4* getItemText
    def getItemText (self,item):

        '''Return the text of the item.'''

        self.oops()
    #@+node:ekr.20110605121601.17931: *4* getParentItem
    def getParentItem (self,item):

        '''Return the parent of the given item.'''

        self.oops()
    #@+node:ekr.20110605121601.17932: *4* getSelectedItems
    def getSelectedItems(self):

        self.oops()
    #@+node:ekr.20110605121601.17933: *4* getWrapper
    def getWrapper (self,e,item):

        '''A do-nothing that can be over-ridden in subclasses.'''

        return e
    #@+node:ekr.20110605121601.17934: *4* getTreeEditorForItem
    def getTreeEditorForItem(self,item):

        '''Return the edit widget if it exists.

        Do *not* create one if it does not exist.'''

        self.oops()
    #@+node:ekr.20110605121601.17935: *4* scrollToItem
    def scrollToItem (self,item):

        self.oops()
    #@+node:ekr.20110605121601.17936: *4* setCurrentItemHelper
    def setCurrentItemHelper(self,item):

        '''Select the given item.'''

        self.oops()
    #@+node:ekr.20110605121601.17937: *4* setItemText
    def setItemText (self,item,s):

        '''Set the headline text for the given item.'''

        self.oops()
    #@+node:ekr.20110605121601.17938: *4* editLabelHelper
    def editLabelHelper(self,item,selectAll=False,selection=None):

        '''Called by nativeTree.editLabel to do gui-specific stuff
        relating to editing a headline.'''

        self.oops()
    #@+node:ekr.20110605121601.17939: *3* Scroll bars (nativeTree)
    # Do-nothings, for use by null classes.

    def getScroll (self):
        '''Return the hPos,vPos for the tree's scrollbars.'''
        return 0,0

    def setHScroll (self,hPos):
        pass

    def setVScroll (self,vPos):
        pass
    #@+node:ekr.20110605121601.17940: *3* wrapQLineEdit (nativeTree)
    def wrapQLineEdit (self,w):

        '''A wretched kludge for MacOs k.masterMenuHandler.'''
        c = self.c

        if isinstance(w,QtGui.QLineEdit):
            wrapper = self.edit_widget(c.p)
        else:
            wrapper = w

        # g.trace(wrapper)
        return wrapper

    #@+node:ekr.20110605121601.17941: ** Widget-independent helpers
    #@+node:ekr.20110605121601.17942: *3* Associating items and positions
    #@+node:ekr.20110605121601.17943: *4* item dict getters
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
    #@+node:ekr.20110605121601.17944: *3* Focus (nativeTree)
    def getFocus(self):

        return g.app.gui.get_focus(self.c) # Bug fix: 2009/6/30

    findFocus = getFocus

    # def hasFocus (self):

        # return g.app.gui.get_focus(self.c)

    def setFocus (self):

        g.app.gui.set_focus(self.c,self.treeWidget)
    #@+node:ekr.20110605121601.17945: *3* Icons (nativeTree)
    #@+node:ekr.20110605121601.17946: *4* drawItemIcon
    def drawItemIcon (self,p,item):

        '''Set the item's icon to p's icon.'''

        icon = self.getIcon(p)
        if icon:
            self.setItemIcon(item,icon)
    #@+node:ekr.20110605121601.17947: *4* getIconImage
    def getIconImage(self,p):

        # User icons are not supported in the base class.
        if g.app.gui.isNullGui:
            return None
        else:
            return self.getStatusIconImage(p)
    #@+node:ekr.20110605121601.17948: *4* getStatusIconImage
    def getStatusIconImage (self,p):

        val = p.v.computeIcon()

        r = g.app.gui.getIconImage(
            "box%02d.GIF" % val)

        # g.trace(r)

        return r
    #@+node:ekr.20110605121601.17949: *4* getVnodeIcon
    def getVnodeIcon(self,p):

        '''Return the proper icon for position p.'''

        return self.getIcon(p)
    #@+node:ekr.20110605121601.17950: *4* setItemIcon (nativeTree)
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
    #@+node:ekr.20110605121601.17951: *4* updateIcon (nativeTree)
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
    #@+node:ekr.20110605121601.17952: *4* updateVisibleIcons (nativeTree)
    def updateVisibleIcons (self,p):

        '''Update the icon for p and the icons
        for all visible descendants of p.'''

        self.updateIcon(p,force=True)

        if p.hasChildren() and p.isExpanded():
            for child in p.children():
                self.updateVisibleIcons(child)
    #@+node:ekr.20110605121601.17953: *3* oops
    def oops(self):

        g.pr("leoTree oops: should be overridden in subclass",
            g.callers(4))
    #@-others
#@-leo
