# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20140907131341.18707: * @file ../plugins/qt_tree.py
#@@first
"""Leo's Qt tree class."""
#@+<< imports >>
#@+node:ekr.20140907131341.18709: ** << imports >> (qt_tree.py)
import re
import time
from typing import Any, List
from leo.core.leoQt import isQt6, QtCore, QtGui, QtWidgets
from leo.core.leoQt import EndEditHint, Format, ItemFlag, KeyboardModifier
from leo.core import leoGlobals as g
from leo.core import leoFrame
from leo.core import leoNodes
from leo.core import leoPlugins  # Uses leoPlugins.TryNext.
from leo.plugins import qt_text
#@-<< imports >>
#@+others
#@+node:ekr.20160514120051.1: ** class LeoQtTree
class LeoQtTree(leoFrame.LeoTree):
    """Leo Qt tree class"""
    #@+others
    #@+node:ekr.20110605121601.18404: *3* qtree.Birth
    #@+node:ekr.20110605121601.18405: *4* qtree.__init__
    def __init__(self, c, frame):
        """Ctor for the LeoQtTree class."""
        super().__init__(frame)
        self.c = c
        # Widget independent status ivars...
        self.prev_v = None
        self.redrawCount = 0  # Count for debugging.
        self.revertHeadline = None  # Previous headline text for abortEditLabel.
        self.busy = False
        # Debugging...
        self.traceCallersFlag = False  # Enable traceCallers method.
        # Associating items with position and vnodes...
        self.items = []
        self.item2positionDict = {}
        self.item2vnodeDict = {}
        self.nodeIconsDict = {}  # keys are gnx, values are declutter generated icons
        self.position2itemDict = {}
        self.vnode2itemsDict = {}  # values are lists of items.
        self.editWidgetsDict = {}  # keys are native edit widgets, values are wrappers.
        self.reloadSettings()
        # Components.
        self.canvas = self  # An official ivar used by Leo's core.
        self.headlineWrapper = qt_text.QHeadlineWrapper  # This is a class.
        self.treeWidget = w = frame.top.treeWidget  # An internal ivar.
            # w is a LeoQTreeWidget, a subclass of QTreeWidget.
        #
        # "declutter", node appearance tweaking
        self.declutter_patterns = None  # list of pairs of patterns for decluttering
        self.declutter_data = {}
        self.loaded_images = {}
        if 0:  # Drag and drop
            w.setDragEnabled(True)
            w.viewport().setAcceptDrops(True)
            w.showDropIndicator = True
            w.setAcceptDrops(True)
            w.setDragDropMode(w.InternalMove)
            if 1:  # Does not work

                def dropMimeData(self, data, action, row, col, parent):
                    g.trace()

                # w.dropMimeData = dropMimeData

                def mimeData(self, indexes):
                    g.trace()

        # Early inits...

        try:
            w.headerItem().setHidden(True)
        except Exception:
            pass
        n = c.config.getInt('icon-height') or 16
        w.setIconSize(QtCore.QSize(160, n))
    #@+node:ekr.20110605121601.17866: *4* qtree.get_name
    def getName(self):
        """Return the name of this widget: must start with "canvas"."""
        return 'canvas(tree)'
    #@+node:ekr.20110605121601.18406: *4* qtree.initAfterLoad
    def initAfterLoad(self):
        """Do late-state inits."""
        # Called by Leo's core.
        c = self.c
        # w = c.frame.top
        tw = self.treeWidget
        tw.itemDoubleClicked.connect(self.onItemDoubleClicked)
        tw.itemClicked.connect(self.onItemClicked)
        tw.itemSelectionChanged.connect(self.onTreeSelect)
        tw.itemCollapsed.connect(self.onItemCollapsed)
        tw.itemExpanded.connect(self.onItemExpanded)
        tw.customContextMenuRequested.connect(self.onContextMenu)
        # tw.onItemChanged.connect(self.onItemChanged)
        g.app.gui.setFilter(c, tw, self, tag='tree')
        # 2010/01/24: Do not set this here.
        # The read logic sets c.changed to indicate nodes have changed.
        # c.clearChanged()
    #@+node:ekr.20110605121601.17871: *4* qtree.reloadSettings
    def reloadSettings(self):
        """LeoQtTree."""
        c = self.c
        self.auto_edit = c.config.getBool('single-click-auto-edits-headline', False)
        self.enable_drag_messages = c.config.getBool("enable-drag-messages")
        self.select_all_text_when_editing_headlines = c.config.getBool(
            'select_all_text_when_editing_headlines')
        self.stayInTree = c.config.getBool('stayInTreeAfterSelect')
        self.use_chapters = c.config.getBool('use-chapters')
        self.use_declutter = c.config.getBool('tree-declutter', default=False)
    #@+node:ekr.20110605121601.17940: *4* qtree.wrapQLineEdit
    def wrapQLineEdit(self, w):
        """A wretched kludge for MacOs k.masterMenuHandler."""
        c = self.c
        if isinstance(w, QtWidgets.QLineEdit):
            wrapper = self.edit_widget(c.p)
        else:
            wrapper = w
        return wrapper
    #@+node:ekr.20110605121601.17868: *3* qtree.Debugging & tracing
    def error(self, s):
        if not g.app.unitTesting:
            g.trace('LeoQtTree Error: ', s, g.callers())

    def traceItem(self, item):
        if item:
            # A QTreeWidgetItem.
            return f"item {id(item)}: {self.getItemText(item)}"
        return '<no item>'

    def traceCallers(self):
        if self.traceCallersFlag:
            return g.callers(5, excludeCaller=True)
        return ''
    #@+node:ekr.20110605121601.17872: *3* qtree.Drawing
    #@+node:ekr.20110605121601.18408: *4* qtree.clear
    def clear(self):
        """Clear all widgets in the tree."""
        w = self.treeWidget
        w.clear()
    #@+node:ekr.20180810052056.1: *4* qtree.drawVisible & helpers (not used)
    def drawVisible(self, p):
        """
        Add only the visible nodes to the outline.

        Not used, as this causes scrolling issues.
        """
        t1 = time.process_time()
        c = self.c
        parents: List[Any] = []
        # Clear the widget.
        w = self.treeWidget
        w.clear()
        # Clear the dicts.
        self.initData()
        if c.hoistStack:
            first_p = c.hoistStack[-1].p
            target_p = first_p.nodeAfterTree().visBack(c)
        else:
            first_p = c.rootPosition()
            target_p = None
        n = 0
        for p in self.yieldVisible(first_p, target_p):
            n += 1
            level = p.level()
            parent_item = w if level == 0 else parents[level - 1]
            item = QtWidgets.QTreeWidgetItem(parent_item)
            item.setFlags(item.flags() | ItemFlag.ItemIsEditable)
            item.setChildIndicatorPolicy(
                item.ShowIndicator if p.hasChildren()
                else item.DontShowIndicator)
            item.setExpanded(bool(p.hasChildren() and p.isExpanded()))
            self.items.append(item)
            # Update parents.
            parents = [] if level == 0 else parents[:level]
            parents.append(item)
            # Update the dicts.
            itemHash = self.itemHash(item)
            self.item2positionDict[itemHash] = p.copy()
            self.item2vnodeDict[itemHash] = p.v
            self.position2itemDict[p.key()] = item
            d = self.vnode2itemsDict
            v = p.v
            aList = d.get(v, [])
            aList.append(item)
            d[v] = aList
            # Enter the headline.
            item.setText(0, p.h)
            if self.use_declutter:
                item._real_text = p.h
            # Draw the icon.
            v.iconVal = v.computeIcon()
            icon = self.getCompositeIconImage(p, v.iconVal)
            if icon:
                self.setItemIcon(item, icon)
            # Set current item.
            if p == c.p:
                w.setCurrentItem(item)
        # Useful, for now.
        t2 = time.process_time()
        if t2 - t1 > 0.1:
            g.trace(f"{n} nodes, {t2 - t1:5.2f} sec")
    #@+node:ekr.20180810052056.2: *5* qtree.yieldVisible (not used)
    def yieldVisible(self, first_p, target_p=None):
        """
        A generator yielding positions from first_p to target_p.
        """
        c = self.c
        p = first_p.copy()
        yield p
        while p:
            if p == target_p:
                return
            v = p.v
            if (v.children and (
                # Use slower test for clones:
                len(v.parents) > 1 and p in v.expandedPositions or
                # Use a quick test for non-clones:
                len(v.parents) <= 1 and (v.statusBits & v.expandedBit) != 0
            )):
                # p.moveToFirstChild()
                p.stack.append((v, p._childIndex),)
                p.v = v.children[0]
                p._childIndex = 0
                yield p
                continue
            # if p.hasNext():
            parent_v = p.stack[-1][0] if p.stack else c.hiddenRootNode
            if p._childIndex + 1 < len(parent_v.children):
                # p.moveToNext()
                p._childIndex += 1
                p.v = parent_v.children[p._childIndex]
                yield p
                continue
            #
            # A fast version of p.moveToThreadNext().
            # We look for a parent with a following sibling.
            while p.stack:
                # p.moveToParent()
                p.v, p._childIndex = p.stack.pop()
                # if p.hasNext():
                parent_v = p.stack[-1][0] if p.stack else c.hiddenRootNode
                if p._childIndex + 1 < len(parent_v.children):
                    # p.moveToNext()
                    p._childIndex += 1
                    p.v = parent_v.children[p._childIndex]
                    break  # Found: moveToThreadNext()
            else:
                break  # Not found.
            # Found moveToThreadNext()
            yield p
            continue
        if target_p:
            g.trace('NOT FOUND:', target_p.h)
    #@+node:ekr.20180810052056.3: *5* qtree.slowYieldVisible
    def slowYieldVisible(self, first_p, target_p=None):
        """
        A generator yielding positions from first_p to target_p.
        """
        c = self.c
        p = first_p.copy()
        while p:
            yield p
            if p == target_p:
                return
            p.moveToVisNext(c)
        if target_p:
            g.trace('NOT FOUND:', target_p.h)
    #@+node:ekr.20110605121601.17873: *4* qtree.full_redraw & helpers
    def full_redraw(self, p=None):
        """
        Redraw all visible nodes of the tree.
        Preserve the vertical scrolling unless scroll is True.
        """
        c = self.c
        if g.app.disable_redraw:
            return None
        if self.busy:
            return None
        # Cancel the delayed redraw request.
        c.requestLaterRedraw = False
        if not p:
            p = c.currentPosition()
        elif c.hoistStack and p.h.startswith('@chapter') and p.hasChildren():
            # Make sure the current position is visible.
            # Part of fix of bug 875323: Hoist an @chapter node leaves a non-visible node selected.
            p = p.firstChild()
            c.frame.tree.select(p)
            c.setCurrentPosition(p)
        else:
            c.setCurrentPosition(p)
        assert not self.busy, g.callers()
        self.redrawCount += 1
        self.initData()
        try:
            self.busy = True
            self.drawTopTree(p)
        finally:
            self.busy = False
        self.setItemForCurrentPosition()
        return p  # Return the position, which may have changed.

    # Compatibility

    redraw = full_redraw
    redraw_now = full_redraw
    #@+node:vitalije.20200329160945.1: *5* tree declutter code
    #@+node:tbrown.20150807090639.1: *6* qtree.declutter_node & helpers
    def declutter_node(self, c, p, item):
        """declutter_node - change the appearance of a node

        :param commander c: commander containing node
        :param position p: position of node
        :param QWidgetItem item: tree node widget item

        returns composite icon for this node
        """
        dd = self.declutter_data
        iconVal = p.v.computeIcon()
        iconName = f'box{iconVal:02d}.png'
        loaded_images = self.loaded_images
        #@+others
        #@+node:vitalije.20200329153544.1: *7* sorted_icons
        def sorted_icons(p):
            '''
            Returns a list of icon filenames for this node.
            The list is sorted to owner the 'where' key of image dicts.
            '''
            icons = c.editCommands.getIconList(p)
            a = [x['file'] for x in icons if x['where'] == 'beforeIcon']
            a.append(iconName)
            a.extend(x['file'] for x in icons if x['where'] == 'beforeHeadline')
            return a
        #@+node:ekr.20171122064635.1: *7* declutter_replace
        def declutter_replace(arg, cmd):
            """
            Executes cmd if cmd is any replace command and returns
            pair (commander, s), where 'commander' corresponds
            to the executed replacement operation, 's' is the substituted string.
            If cmd is not a replacement command returns (None, None)
            """
            # pylint: disable=undefined-loop-variable

            replacement, s = None, None

            if cmd == 'REPLACE':
                s = pattern.sub(arg, text)
            elif cmd == 'REPLACE-HEAD':
                s = text[: m.start()].rstrip()
            elif cmd == 'REPLACE-TAIL':
                s = text[m.end() :].lstrip()
            elif cmd == 'REPLACE-REST':
                s = (text[:m.start] + text[m.end() :]).strip()

            # 's' is string when 'cmd' is recognised
            # and is None otherwise
            if isinstance(s,str):
                # Save the operation
                replacement = lambda item, s: item.setText(0, s)
                # ... and apply it
                replacement(item, s)

            return replacement, s
        #@+node:ekr.20171122055719.1: *7* declutter_style
        def declutter_style(arg, cmd):
            """
            Handles style options and returns pair '(commander, param)',
            where 'commander' is the applied style-modifying operation,
            param - the saved argument of that operation.
            Returns (None, param) if 'cmd' is not a style option.
            """
            # pylint: disable=function-redefined
            param = c.styleSheetManager.expand_css_constants(arg).split()[0]
            modifier = None
            if cmd == 'ICON':
                def modifier(item, param):
                    # Does not fit well this function. And we cannot
                    # wrap list 'new_icons' in a saved argument as
                    # the list is recreated before each call.
                    new_icons.append(param)
            elif cmd == 'BG':
                def modifier(item, param):
                    item.setBackground(0, QtGui.QBrush(QtGui.QColor(param)))
            elif cmd == 'FG':
                def modifier(item, param):
                    item.setForeground(0, QtGui.QBrush(QtGui.QColor(param)))
            elif cmd == 'FONT':
                def modifier(item, param):
                    item.setFont(0, QtGui.QFont(param))
            elif cmd == 'ITALIC':
                def modifier(item, param):
                    font = item.font(0)
                    font.setItalic(bool(int(param)))
                    item.setFont(0, font)
            elif cmd == 'WEIGHT':
                def modifier(item, param):
                    arg = getattr(QtGui.QFont, param, 75)
                    font = item.font(0)
                    font.setWeight(arg)
                    item.setFont(0, font)
            elif cmd == 'PX':
                def modifier(item, param):
                    font = item.font(0)
                    font.setPixelSize(int(param))
                    item.setFont(0, font)
            elif cmd == 'PT':
                def modifier(item, param):
                    font = item.font(0)
                    font.setPointSize(int(param))
                    item.setFont(0, font)
            # Apply the style update
            if modifier:
                modifier(item, param)
            return modifier, param
        #@+node:vitalije.20200327163522.1: *7* apply_declutter_rules
        def apply_declutter_rules(cmds):
            """
            Applies all commands for the matched rule. Returns the list
            of the applied operations paired with their single parameter.
            """
            modifiers = []
            for cmd, arg in cmds:
                modifier, param = declutter_replace(arg, cmd)
                if not modifier:
                    modifier, param = declutter_style(arg, cmd)
                if modifier:
                    modifiers.append((modifier, param))
            return modifiers
        #@+node:vitalije.20200329162015.1: *7* preload_images
        def preload_images():
            for f in new_icons:
                if f not in loaded_images:
                    loaded_images[f] = g.app.gui.getImageImage(f)
        #@-others
        if (p.h, iconVal) in dd:
            # Apply saved adjustments to the text and to the _style_
            # of the node
            new_icons, modifiers_and_args = dd[(p.h, iconVal)]
            for modifier, arg in modifiers_and_args:
                modifier(item, arg)

            new_icons = sorted_icons(p) + new_icons
        else:
            text = p.h
            new_icons = []
            modifiers_and_args = []
            for pattern, cmds in self.get_declutter_patterns():
                m = pattern.match(text) or pattern.search(text)
                if m:
                    modifiers_and_args.extend(apply_declutter_rules(cmds))

            # Save the lists of the icons and the adjusting operations
            # for future reuse.
            dd[(p.h, iconVal)] = new_icons, modifiers_and_args
            new_icons = sorted_icons(p) + new_icons
            preload_images()
        self.nodeIconsDict[p.gnx] = new_icons
        h = ':'.join(new_icons)
        icon = g.app.gui.iconimages.get(h)
        if not icon:
            preload_images()
            images = [loaded_images.get(x) for x in new_icons]
            icon = self.make_composite_icon(images)
            g.app.gui.iconimages[h] = icon
        return icon
    #@+node:vitalije.20200327162532.1: *6* qtree.get_declutter_patterns
    def get_declutter_patterns(self):
        "Initializes self.declutter_patterns from configuration and returns it"
        if self.declutter_patterns is not None:
            return self.declutter_patterns
        c = self.c
        patterns: List[Any] = []
        warned = False
        lines = c.config.getData("tree-declutter-patterns")
        for line in lines:
            try:
                cmd, arg = line.split(None, 1)
            except ValueError:
                # Allow empty arg, and guard against user errors.
                cmd = line.strip()
                arg = ''
            if cmd.startswith('#'):
                pass
            elif cmd == 'RULE':
                patterns.append((re.compile(arg), []))
            else:
                if patterns:
                    patterns[-1][1].append((cmd, arg))
                elif not warned:
                    warned = True
                    g.log('Declutter patterns must start with RULE*',
                        color='error')
        self.declutter_patterns = patterns
        return patterns
    #@+node:ekr.20110605121601.17874: *5* qtree.drawChildren
    def drawChildren(self, p, parent_item):
        """Draw the children of p if they should be expanded."""
        if not p:
            g.trace('can not happen: no p')
            return
        if p.hasChildren():
            if p.isExpanded():
                self.expandItem(parent_item)
                child = p.firstChild()
                while child:
                    self.drawTree(child, parent_item)
                    child.moveToNext()
            else:
                # Draw the hidden children.
                child = p.firstChild()
                while child:
                    self.drawNode(child, parent_item)
                    child.moveToNext()
                self.contractItem(parent_item)
        else:
            self.contractItem(parent_item)
    #@+node:ekr.20110605121601.17875: *5* qtree.drawNode
    def drawNode(self, p, parent_item):
        """Draw the node p."""
        c = self.c
        v = p.v
        # Allocate the QTreeWidgetItem.
        item = self.createTreeItem(p, parent_item)
        #
        # Update the data structures.
        itemHash = self.itemHash(item)
        self.position2itemDict[p.key()] = item
        self.item2positionDict[itemHash] = p.copy()  # was item
        self.item2vnodeDict[itemHash] = v  # was item
        d = self.vnode2itemsDict
        aList = d.get(v, [])
        if item not in aList:
            aList.append(item)
        d[v] = aList
        # Set the headline and maybe the icon.
        self.setItemText(item, p.h)
        # #1310: Add a tool tip.
        item.setToolTip(0, p.h)
        if self.use_declutter:
            icon = self.declutter_node(c, p, item)
            if icon:
                item.setIcon(0, icon)
            return item
        # Draw the icon.
        v.iconVal = v.computeIcon()
        icon = self.getCompositeIconImage(p, v.iconVal)
            # **Slow**, but allows per-vnode icons.
        if icon:
            item.setIcon(0, icon)
        return item
    #@+node:ekr.20110605121601.17876: *5* qtree.drawTopTree
    def drawTopTree(self, p):
        """Draw the tree rooted at p."""
        trace = 'drawing' in g.app.debug and not g.unitTesting
        if trace:
            t1 = time.process_time()
        c = self.c
        self.clear()
        # Draw all top-level nodes and their visible descendants.
        if c.hoistStack:
            bunch = c.hoistStack[-1]
            p = bunch.p; h = p.h
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
        if trace:
            t2 = time.process_time()
            g.trace(f"{t2 - t1:5.2f} sec.", g.callers(5))
    #@+node:ekr.20110605121601.17877: *5* qtree.drawTree
    def drawTree(self, p, parent_item=None):
        if g.app.gui.isNullGui:
            return
        # Draw the (visible) parent node.
        item = self.drawNode(p, parent_item)
        # Draw all the visible children.
        self.drawChildren(p, parent_item=item)
    #@+node:ekr.20110605121601.17878: *5* qtree.initData
    def initData(self):
        self.item2positionDict = {}
        self.item2vnodeDict = {}
        self.position2itemDict = {}
        self.vnode2itemsDict = {}
        self.editWidgetsDict = {}
    #@+node:ekr.20110605121601.17880: *4* qtree.redraw_after_contract
    def redraw_after_contract(self, p):

        if self.busy:
            return
        self.update_expansion(p)
    #@+node:ekr.20110605121601.17881: *4* qtree.redraw_after_expand
    def redraw_after_expand(self, p):

        if 0:  # Does not work. Newly visible nodes do not show children correctly.
            c = self.c
            c.selectPosition(p)
            self.update_expansion(p)
        else:
            self.full_redraw(p)
                # Don't try to shortcut this!
    #@+node:ekr.20110605121601.17882: *4* qtree.redraw_after_head_changed
    def redraw_after_head_changed(self):
        """Redraw all Qt outline items cloned to c.p."""
        if self.busy:
            return
        p = self.c.p
        if p:
            h = p.h  # 2010/02/09: Fix bug 518823.
            for item in self.vnode2items(p.v):
                if self.isValidItem(item):
                    self.setItemText(item, h)
        # Bug fix: 2009/10/06
        self.redraw_after_icons_changed()
    #@+node:ekr.20110605121601.17883: *4* qtree.redraw_after_icons_changed
    def redraw_after_icons_changed(self):

        if self.busy:
            return
        self.redrawCount += 1  # To keep a unit test happy.
        c = self.c
        try:
            self.busy = True
                # Suppress call to setHeadString in onItemChanged!
            self.getCurrentItem()
            for p in c.rootPosition().self_and_siblings(copy=False):
                # Updates icons in p and all visible descendants of p.
                self.updateVisibleIcons(p)
        finally:
            self.busy = False
    #@+node:ekr.20110605121601.17884: *4* qtree.redraw_after_select
    def redraw_after_select(self, p=None):
        """Redraw the entire tree when an invisible node is selected."""
        if self.busy:
            return
        self.full_redraw(p)
        # c.redraw_after_select calls tree.select indirectly.
        # Do not call it again here.
    #@+node:ekr.20140907201613.18986: *4* qtree.repaint (not used)
    def repaint(self):
        """Repaint the widget."""
        w = self.treeWidget
        w.repaint()
        w.resizeColumnToContents(0)  # 2009/12/22
    #@+node:ekr.20180817043619.1: *4* qtree.update_expansion
    def update_expansion(self, p):
        """Update expansion bits for p, including all clones."""
        c = self.c
        w = self.treeWidget
        expand = c.shouldBeExpanded(p)
        if 'drawing' in g.app.debug:
            g.trace('expand' if expand else 'contract')
        item = self.position2itemDict.get(p.key())
        if p:
            try:
                # These generate events, which would trigger a full redraw.
                self.busy = True
                if expand:
                    w.expandItem(item)
                else:
                    w.collapseItem(item)
            finally:
                self.busy = False
            w.repaint()
        else:
            g.trace('NO P')
            c.redraw()
    #@+node:ekr.20110605121601.17885: *3* qtree.Event handlers
    #@+node:ekr.20110605121601.17887: *4*  qtree.Click Box
    #@+node:ekr.20110605121601.17888: *5* qtree.onClickBoxClick
    def onClickBoxClick(self, event, p=None):
        if self.busy:
            return
        c = self.c
        g.doHook("boxclick1", c=c, p=p, event=event)
        g.doHook("boxclick2", c=c, p=p, event=event)
        c.outerUpdate()
    #@+node:ekr.20110605121601.17889: *5* qtree.onClickBoxRightClick
    def onClickBoxRightClick(self, event, p=None):
        if self.busy:
            return
        c = self.c
        g.doHook("boxrclick1", c=c, p=p, event=event)
        g.doHook("boxrclick2", c=c, p=p, event=event)
        c.outerUpdate()
    #@+node:ekr.20110605121601.17890: *5* qtree.onPlusBoxRightClick
    def onPlusBoxRightClick(self, event, p=None):
        if self.busy:
            return
        c = self.c
        g.doHook('rclick-popup', c=c, p=p, event=event, context_menu='plusbox')
        c.outerUpdate()
    #@+node:ekr.20110605121601.17891: *4*  qtree.Icon Box
    # For Qt, there seems to be no way to trigger these events.
    #@+node:ekr.20110605121601.17892: *5* qtree.onIconBoxClick
    def onIconBoxClick(self, event, p=None):
        if self.busy:
            return
        c = self.c
        g.doHook("iconclick1", c=c, p=p, event=event)
        g.doHook("iconclick2", c=c, p=p, event=event)
        c.outerUpdate()
    #@+node:ekr.20110605121601.17893: *5* qtree.onIconBoxRightClick
    def onIconBoxRightClick(self, event, p=None):
        """Handle a right click in any outline widget."""
        if self.busy:
            return
        c = self.c
        g.doHook("iconrclick1", c=c, p=p, event=event)
        g.doHook("iconrclick2", c=c, p=p, event=event)
        c.outerUpdate()
    #@+node:ekr.20110605121601.17894: *5* qtree.onIconBoxDoubleClick
    def onIconBoxDoubleClick(self, event, p=None):
        if self.busy:
            return
        c = self.c
        if not p: p = c.p
        if not g.doHook("icondclick1", c=c, p=p, event=event):
            self.endEditLabel()
            self.OnIconDoubleClick(p)  # Call the method in the base class.
        g.doHook("icondclick2", c=c, p=p, event=event)
        c.outerUpdate()
    #@+node:ekr.20110605121601.18437: *4* qtree.onContextMenu
    def onContextMenu(self, point):
        """LeoQtTree: Callback for customContextMenuRequested events."""
        # #1286.
        c, w = self.c, self.treeWidget
        g.app.gui.onContextMenu(c, w, point)
    #@+node:ekr.20110605121601.17896: *4* qtree.onItemClicked
    def onItemClicked(self, item, col):
        """Handle a click in a BaseNativeTree widget item."""
        # This is called after an item is selected.
        if self.busy:
            return
        c = self.c
        try:
            self.busy = True
            p = self.item2position(item)
            if p:
                auto_edit = self.prev_v == p.v
                    # Fix #1049.
                self.prev_v = p.v
                event = None
                #
                # Careful. We may have switched gui during unit testing.
                if hasattr(g.app.gui, 'qtApp'):
                    mods = g.app.gui.qtApp.keyboardModifiers()
                    isCtrl = bool(mods & KeyboardModifier.ControlModifier)
                    # We could also add support for QtConst.ShiftModifier, QtConst.AltModifier
                    # & QtConst.MetaModifier.
                    if isCtrl:
                        if g.doHook("iconctrlclick1", c=c, p=p, event=event) is None:
                            c.frame.tree.OnIconCtrlClick(p)
                                # Call the base class method.
                        g.doHook("iconctrlclick2", c=c, p=p, event=event)
                    else:
                        # 2014/02/21: generate headclick1/2 instead of iconclick1/2
                        g.doHook("headclick1", c=c, p=p, event=event)
                        g.doHook("headclick2", c=c, p=p, event=event)
            else:
                auto_edit = None
                g.trace('*** no p')
            # 2011/05/27: click here is like ctrl-g.
            c.k.keyboardQuit(setFocus=False)
            c.treeWantsFocus()  # 2011/05/08: Focus must stay in the tree!
            c.outerUpdate()
            # 2011/06/01: A second *single* click on a selected node
            # enters editing state.
            if auto_edit and self.auto_edit:
                e, wrapper = self.createTreeEditorForItem(item)
        finally:
            self.busy = False
    #@+node:ekr.20110605121601.17895: *4* qtree.onItemCollapsed
    def onItemCollapsed(self, item):

        if self.busy:
            return
        c = self.c
        p = self.item2position(item)
        if not p:
            self.error('no p')
            return
        # Do **not** set lockouts here.
        # Only methods that actually generate events should set lockouts.
        if p.isExpanded():
            p.contract()
            c.redraw_after_contract(p)
        self.select(p)
        c.outerUpdate()
    #@+node:ekr.20110605121601.17897: *4* qtree.onItemDoubleClicked
    def onItemDoubleClicked(self, item, col):
        """Handle a double click in a BaseNativeTree widget item."""
        if self.busy:  # Required.
            return
        c = self.c
        try:
            self.busy = True
            e, wrapper = self.createTreeEditorForItem(item)
            if not e:
                g.trace('*** no e')
            p = self.item2position(item)
        # 2011/07/28: End the lockout here, not at the end.
        finally:
            self.busy = False
        if not p:
            self.error('no p')
            return
        # 2014/02/21: generate headddlick1/2 instead of icondclick1/2.
        if g.doHook("headdclick1", c=c, p=p, event=None) is None:
            c.frame.tree.OnIconDoubleClick(p)  # Call the base class method.
        g.doHook("headclick2", c=c, p=p, event=None)
        c.outerUpdate()
    #@+node:ekr.20110605121601.17898: *4* qtree.onItemExpanded
    def onItemExpanded(self, item):
        """Handle and tree-expansion event."""
        if self.busy:  # Required
            return
        c = self.c
        p = self.item2position(item)
        if not p:
            self.error('no p')
            return
        # Do **not** set lockouts here.
        # Only methods that actually generate events should set lockouts.
        if not p.isExpanded():
            p.expand()
            c.redraw_after_expand(p)
        self.select(p)
        c.outerUpdate()
    #@+node:ekr.20110605121601.17899: *4* qtree.onTreeSelect
    def onTreeSelect(self):
        """Select the proper position when a tree node is selected."""
        if self.busy:  # Required
            return
        c = self.c
        item = self.getCurrentItem()
        p = self.item2position(item)
        if not p:
            self.error(f"no p for item: {item}")
            return
        # Do **not** set lockouts here.
        # Only methods that actually generate events should set lockouts.
        self.select(p)
            # This is a call to LeoTree.select(!!)
        c.outerUpdate()
    #@+node:ekr.20110605121601.17944: *3* qtree.Focus
    def getFocus(self):
        return g.app.gui.get_focus(self.c)  # Bug fix: 2009/6/30

    findFocus = getFocus

    def setFocus(self):
        g.app.gui.set_focus(self.c, self.treeWidget)
    #@+node:ekr.20110605121601.18409: *3* qtree.Icons
    #@+node:ekr.20110605121601.18410: *4* qtree.drawIcon
    def drawIcon(self, p):
        """Redraw the icon at p."""
        return self.updateIcon(p)
        # the following code is wrong. It constructs a new item
        # and assignes the icon to it. However this item is never
        # added to the treeWidget so it is soon garbage collected
            # w = self.treeWidget
            # itemOrTree = self.position2item(p) or w
            # item = QtWidgets.QTreeWidgetItem(itemOrTree)
            # icon = self.getIcon(p)
            # self.setItemIcon(item, icon)
    #@+node:ekr.20110605121601.18411: *4* qtree.getIcon & helper
    def getIcon(self, p):
        """Return the proper icon for position p."""
        if self.use_declutter:
            item = self.position2item(p)
            return item and self.declutter_node(self.c, p, item)
        p.v.iconVal = iv = p.v.computeIcon()
        return self.getCompositeIconImage(p, iv)


    #@+node:vitalije.20200329153148.1: *5* qtree.icon_filenames_for_node
    def icon_filenames_for_node(self, p, val):
        '''Prepares and returns a list of icon filenames
           related to this node.
        '''
        nicon = f'box{val:02d}.png'
        fnames = self.nodeIconsDict.get(p.gnx)
        if not fnames:
            icons = self.c.editCommands.getIconList(p)
            fnames = [x['file'] for x in icons if x['where'] == 'beforeIcon']
            fnames.append(nicon)
            fnames.extend(x['file'] for x in icons if x['where'] == 'beforeHeadline')
            self.nodeIconsDict[p.gnx] = fnames
        pat = re.compile(r'^box\d\d\.png$')
        loaded_images = self.loaded_images
        for i, f in enumerate(fnames):
            if pat.match(f):
                fnames[i] = nicon
                self.nodeIconsDict[p.gnx] = fnames
                f = nicon
            if f not in loaded_images:
                loaded_images[f] = g.app.gui.getImageImage(f)
        return fnames
    #@+node:vitalije.20200329153154.1: *5* qtree.make_composite_icon
    def make_composite_icon(self, images):
        hsep = self.c.config.getInt('tree-icon-separation') or 0
        images = [x for x in images if x]
        height = max([i.height() for i in images])
        images = [i.scaledToHeight(height) for i in images]
        width = sum([i.width() for i in images]) + hsep * (len(images) - 1)
        pix = QtGui.QImage(width, height, Format.Format_ARGB32_Premultiplied)
        pix.fill(QtGui.QColor(0, 0, 0, 0).rgba())  # transparent fill, rgbA
        # .rgba() call required for Qt4.7, later versions work with straight color
        painter = QtGui.QPainter()
        if not painter.begin(pix):
            print("Failed to init. painter for icon")
            # don't return, the code still makes an icon for the cache
            # which stops this being called again and again
        x = 0
        for i in images:
            painter.drawPixmap(x, 0, i)
            x += i.width() + hsep
        painter.end()
        return QtGui.QIcon(QtGui.QPixmap.fromImage(pix))
    #@+node:ekr.20110605121601.18412: *5* qtree.getCompositeIconImage
    def getCompositeIconImage(self, p, val):
        """Get the icon at position p."""
        fnames = self.icon_filenames_for_node(p, val)
        h = ':'.join(fnames)
        icon = g.app.gui.iconimages.get(h)
        loaded_images = self.loaded_images
        images = list(map(loaded_images.get, fnames))
        if not icon:
            icon = self.make_composite_icon(images)
            g.app.gui.iconimages[h] = icon
        return icon
    #@+node:ekr.20110605121601.17950: *4* qtree.setItemIcon
    def setItemIcon(self, item, icon):

        valid = item and self.isValidItem(item)
        if icon and valid:
            # Important: do not set lockouts here.
            # This will generate changed events,
            # but there is no itemChanged event handler.
            item.setIcon(0, icon)

    #@+node:ekr.20110605121601.17951: *4* qtree.updateIcon & updateAllIcons
    def updateIcon(self, p):
        """Update p's icon."""
        if not p:
            return
        val = p.v.computeIcon()
        if p.v.iconVal != val:
            self.nodeIconsDict.pop(p.gnx, None)
            self.getIcon(p)  # sets p.v.iconVal

    def updateAllIcons(self, p):
        if not p:
            return
        self.nodeIconsDict.pop(p.gnx, None)
        icon = self.getIcon(p)  # sets p.v.iconVal
        # Update all cloned items.
        items = self.vnode2items(p.v)
        for item in items:
            self.setItemIcon(item, icon)
    #@+node:ekr.20110605121601.17952: *4* qtree.updateVisibleIcons
    def updateVisibleIcons(self, p):
        """Update the icon for p and the icons
        for all visible descendants of p."""
        self.updateAllIcons(p)
        if p.hasChildren() and p.isExpanded():
            for child in p.children():
                self.updateVisibleIcons(child)
    #@+node:ekr.20110605121601.18414: *3* qtree.Items
    #@+node:ekr.20110605121601.17943: *4*  qtree.item dict getters
    def itemHash(self, item):
        return f"{repr(item)} at {str(id(item))}"

    def item2position(self, item):
        itemHash = self.itemHash(item)
        p = self.item2positionDict.get(itemHash)  # was item
        return p

    def item2vnode(self, item):
        itemHash = self.itemHash(item)
        return self.item2vnodeDict.get(itemHash)  # was item

    def position2item(self, p):
        item = self.position2itemDict.get(p.key())
        return item

    def vnode2items(self, v):
        return self.vnode2itemsDict.get(v, [])

    def isValidItem(self, item):
        itemHash = self.itemHash(item)
        return itemHash in self.item2vnodeDict  # was item.
    #@+node:ekr.20110605121601.18415: *4* qtree.childIndexOfItem
    def childIndexOfItem(self, item):
        parent = item and item.parent()
        if parent:
            n = parent.indexOfChild(item)
        else:
            w = self.treeWidget
            n = w.indexOfTopLevelItem(item)
        return n
    #@+node:ekr.20110605121601.18416: *4* qtree.childItems
    def childItems(self, parent_item):
        """
        Return the list of child items of the parent item,
        or the top-level items if parent_item is None.
        """
        if parent_item:
            n = parent_item.childCount()
            items = [parent_item.child(z) for z in range(n)]
        else:
            w = self.treeWidget
            n = w.topLevelItemCount()
            items = [w.topLevelItem(z) for z in range(n)]
        return items
    #@+node:ekr.20110605121601.18418: *4* qtree.connectEditorWidget & callback
    def connectEditorWidget(self, e, item):
        """
        Connect QLineEdit e to QTreeItem item.

        Also callback for when the editor ends.

        New in Leo 6.4: The callback handles all updates w/o calling onHeadChanged.
        """
        c, p, u = self.c, self.c.p, self.c.undoer
        #@+others  # define the callback.
        #@+node:ekr.20201109043641.1: *5* function: editingFinished_callback
        def editingFinished_callback():
            """Called when Qt emits the editingFinished signal."""
            s = e.text()
            i = s.find('\n')
            # Truncate to one line.
            if i > -1:
                s = s[:i]
            # #1310: update the tooltip.
            if p.h != s:
                # Update p.h and handle undo.
                item.setToolTip(0, s)
                undoData = u.beforeChangeHeadline(p)
                p.v.setHeadString(s)  # Set v.h *after* calling the undoer's before method.
                if not c.changed:
                    c.setChanged()
                # We must recolor the body because
                # the headline may contain directives.
                c.frame.body.recolor(p)
                p.setDirty()
                u.afterChangeHeadline(p, 'Edit Headline', undoData)
            self.redraw_after_head_changed()
            c.outerUpdate()
        #@-others
        if e:
            # Hook up the widget.
            wrapper = self.getWrapper(e, item)
            e.editingFinished.connect(editingFinished_callback)
            return wrapper  # 2011/02/12
        g.trace('can not happen: no e')
        return None
    #@+node:ekr.20110605121601.18419: *4* qtree.contractItem & expandItem
    def contractItem(self, item):
        self.treeWidget.collapseItem(item)

    def expandItem(self, item):
        self.treeWidget.expandItem(item)
    #@+node:ekr.20110605121601.18420: *4* qtree.createTreeEditorForItem
    def createTreeEditorForItem(self, item):

        c = self.c
        w = self.treeWidget
        w.setCurrentItem(item)  # Must do this first.
        if self.use_declutter:
            item.setText(0, item._real_text)
        w.editItem(item)
        e = w.itemWidget(item, 0)  # e is a QLineEdit
        e.setObjectName('headline')
        wrapper = self.connectEditorWidget(e, item)
        self.sizeTreeEditor(c, e)
        return e, wrapper
    #@+node:ekr.20110605121601.18421: *4* qtree.createTreeItem
    def createTreeItem(self, p, parent_item):

        w = self.treeWidget
        itemOrTree = parent_item or w
        item = QtWidgets.QTreeWidgetItem(itemOrTree)
        if isQt6:
            item.setFlags(item.flags() | ItemFlag.ItemIsEditable)
            ChildIndicatorPolicy = QtWidgets.QTreeWidgetItem.ChildIndicatorPolicy
            item.setChildIndicatorPolicy(ChildIndicatorPolicy.DontShowIndicatorWhenChildless)  # pylint: disable=no-member
        else:
            item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable | item.DontShowIndicatorWhenChildless)
        try:
            g.visit_tree_item(self.c, p, item)
        except leoPlugins.TryNext:
            pass
        return item
    #@+node:ekr.20110605121601.18423: *4* qtree.getCurrentItem
    def getCurrentItem(self):
        w = self.treeWidget
        return w.currentItem()
    #@+node:ekr.20110605121601.18424: *4* qtree.getItemText
    def getItemText(self, item):
        """Return the text of the item."""
        return item.text(0) if item else '<no item>'
    #@+node:ekr.20110605121601.18425: *4* qtree.getParentItem
    def getParentItem(self, item):
        return item and item.parent()
    #@+node:ekr.20110605121601.18426: *4* qtree.getSelectedItems
    def getSelectedItems(self):
        w = self.treeWidget
        return w.selectedItems()
    #@+node:ekr.20110605121601.18427: *4* qtree.getTreeEditorForItem
    def getTreeEditorForItem(self, item):
        """Return the edit widget if it exists.
        Do *not* create one if it does not exist.
        """
        w = self.treeWidget
        e = w.itemWidget(item, 0)
        return e
    #@+node:ekr.20110605121601.18428: *4* qtree.getWrapper
    def getWrapper(self, e, item):
        """Return headlineWrapper that wraps e (a QLineEdit)."""
        c = self.c
        if e:
            wrapper = self.editWidgetsDict.get(e)
            if wrapper:
                pass
            else:
                if item:
                    # 2011/02/12: item can be None.
                    wrapper = self.headlineWrapper(c, item, name='head', widget=e)
                    self.editWidgetsDict[e] = wrapper
            return wrapper
        g.trace('no e')
        return None
    #@+node:ekr.20110605121601.18429: *4* qtree.nthChildItem
    def nthChildItem(self, n, parent_item):
        children = self.childItems(parent_item)
        if n < len(children):
            item = children[n]
        else:
            # This is **not* an error.
            # It simply means that we need to redraw the tree.
            item = None
        return item
    #@+node:ekr.20110605121601.18430: *4* qtree.scrollToItem
    def scrollToItem(self, item):
        """
        Scroll the tree widget so that item is visible.
        Leo's core no longer calls this method.
        """
        w = self.treeWidget
        hPos, vPos = self.getScroll()
        w.scrollToItem(item, w.EnsureVisible)
            # Fix #265: Erratic scrolling bug.
            # w.PositionAtCenter causes unwanted scrolling.
        self.setHScroll(0)
            # Necessary
    #@+node:ekr.20110605121601.18431: *4* qtree.setCurrentItemHelper
    def setCurrentItemHelper(self, item):
        w = self.treeWidget
        w.setCurrentItem(item)
    #@+node:ekr.20110605121601.18432: *4* qtree.setItemText
    def setItemText(self, item, s):
        if item:
            item.setText(0, s)
            if self.use_declutter:
                item._real_text = s
    #@+node:tbrown.20160406221505.1: *4* qtree.sizeTreeEditor
    @staticmethod
    def sizeTreeEditor(c, editor):
        """Size a QLineEdit in a tree headline so scrolling occurs"""
        # space available in tree widget
        space = c.frame.tree.treeWidget.size().width()
        # left hand edge of editor within tree widget
        used = editor.geometry().x() + 4  # + 4 for edit cursor
        # limit width to available space
        editor.resize(space - used, editor.size().height())
    #@+node:ekr.20110605121601.18433: *3* qtree.Scroll bars
    #@+node:ekr.20110605121601.18434: *4* qtree.getSCroll
    def getScroll(self):
        """Return the hPos,vPos for the tree's scrollbars."""
        w = self.treeWidget
        hScroll = w.horizontalScrollBar()
        vScroll = w.verticalScrollBar()
        hPos = hScroll.sliderPosition()
        vPos = vScroll.sliderPosition()
        return hPos, vPos
    #@+node:btheado.20111110215920.7164: *4* qtree.scrollDelegate
    def scrollDelegate(self, kind):
        """
        Scroll a QTreeWidget up or down or right or left.
        kind is in ('down-line','down-page','up-line','up-page', 'right', 'left')
        """
        c = self.c; w = self.treeWidget
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
            n = h / lineSpacing
            if kind == 'down-half-page': delta = n / 2
            elif kind == 'down-line': delta = 1
            elif kind == 'down-page': delta = n
            elif kind == 'up-half-page': delta = -n / 2
            elif kind == 'up-line': delta = -1
            elif kind == 'up-page': delta = -n
            else:
                delta = 0
                g.trace('bad kind:', kind)
            val = vScroll.value()
            vScroll.setValue(val + delta)
        c.treeWantsFocus()
    #@+node:ekr.20110605121601.18435: *4* qtree.setH/VScroll
    def setHScroll(self, hPos):

        w = self.treeWidget
        hScroll = w.horizontalScrollBar()
        hScroll.setValue(hPos)

    def setVScroll(self, vPos):

        w = self.treeWidget
        vScroll = w.verticalScrollBar()
        vScroll.setValue(vPos)
    #@+node:ekr.20110605121601.17905: *3* qtree.Selecting & editing
    #@+node:ekr.20110605121601.17908: *4* qtree.edit_widget
    def edit_widget(self, p):
        """Returns the edit widget for position p."""
        item = self.position2item(p)
        if item:
            e = self.getTreeEditorForItem(item)
            if e:
                # Create a wrapper widget for Leo's core.
                w = self.getWrapper(e, item)
                return w
            # This is not an error
            # But warning: calling this method twice might not work!
            return None
        return None
    #@+node:ekr.20110605121601.17909: *4* qtree.editLabel and helper
    def editLabel(self, p, selectAll=False, selection=None):
        """Start editing p's headline."""
        if self.busy:
            return None
        c = self.c
        c.outerUpdate()
            # Do any scheduled redraw.
            # This won't do anything in the new redraw scheme.
        item = self.position2item(p)
        if item:
            if self.use_declutter:
                item.setText(0, item._real_text)
            e, wrapper = self.editLabelHelper(item, selectAll, selection)
        else:
            e, wrapper = None, None
            self.error(f"no item for {p}")
        if e:
            self.sizeTreeEditor(c, e)
            # A nice hack: just set the focus request.
            c.requestedFocusWidget = e
        return e, wrapper
    #@+node:ekr.20110605121601.18422: *5* qtree.editLabelHelper
    def editLabelHelper(self, item, selectAll=False, selection=None):
        """Helper for qtree.editLabel."""
        c, vc = self.c, self.c.vimCommands
        w = self.treeWidget
        w.setCurrentItem(item)
            # Must do this first.
            # This generates a call to onTreeSelect.
        w.editItem(item)
            # Generates focus-in event that tree doesn't report.
        e = w.itemWidget(item, 0)  # A QLineEdit.
        s = e.text()
        if s == 'newHeadline':
            selectAll = True
        if selection:
            # pylint: disable=unpacking-non-sequence
            # Fix bug https://groups.google.com/d/msg/leo-editor/RAzVPihqmkI/-tgTQw0-LtwJ
            # Note: negative lengths are allowed.
            i, j, ins = selection
            if ins is None:
                start, n = i, abs(i - j)
                # This case doesn't happen for searches.
            elif ins == j:
                start, n = i, j - i
            else:
                start = start, n = j, i - j
        elif selectAll:
            start, n, ins = 0, len(s), len(s)
        else:
            start, n, ins = len(s), 0, len(s)
        e.setObjectName('headline')
        e.setSelection(start, n)
        # e.setCursorPosition(ins) # Does not work.
        e.setFocus()
        wrapper = self.connectEditorWidget(e, item)  # Hook up the widget.
        if vc and c.vim_mode:  #  and selectAll
            # For now, *always* enter insert mode.
            if vc.is_text_wrapper(wrapper):
                vc.begin_insert_mode(w=wrapper)
            else:
                g.trace('not a text widget!', wrapper)
        return e, wrapper
    #@+node:ekr.20110605121601.17911: *4* qtree.endEditLabel
    def endEditLabel(self):
        """
        Override LeoTree.endEditLabel.

        Just end editing of the presently-selected QLineEdit!
        This will trigger the editingFinished_callback defined in createEditorForItem.
        """
        item = self.getCurrentItem()
        if not item:
            return
        e = self.getTreeEditorForItem(item)
        if not e:
            return
        # Trigger the end-editing event.
        w = self.treeWidget
        w.closeEditor(e, EndEditHint.NoHint)
        w.setCurrentItem(item)
    #@+node:ekr.20110605121601.17915: *4* qtree.getSelectedPositions
    def getSelectedPositions(self):
        items = self.getSelectedItems()
        pl = leoNodes.PosList(self.item2position(it) for it in items)
        return pl
    #@+node:ekr.20110605121601.17914: *4* qtree.setHeadline
    def setHeadline(self, p, s):
        """Force the actual text of the headline widget to p.h."""
        # This is used by unit tests to force the headline and p into alignment.
        if not p:
            return
        # Don't do this here: the caller should do it.
        # p.setHeadString(s)
        e = self.edit_widget(p)
        if e:
            e.setAllText(s)
        else:
            item = self.position2item(p)
            if item:
                self.setItemText(item, s)
    #@+node:ekr.20110605121601.17913: *4* qtree.setItemForCurrentPosition
    def setItemForCurrentPosition(self):
        """Select the item for c.p"""
        c = self.c; p = c.currentPosition()
        if self.busy:
            return None
        if not p:
            return None
        item = self.position2item(p)
        if not item:
            # This is not necessarily an error.
            # We often attempt to select an item before redrawing it.
            return None
        item2 = self.getCurrentItem()
        if item == item2:
            return item
        try:
            self.busy = True
            self.treeWidget.setCurrentItem(item)
                # This generates gui events, so we must use a lockout.
        finally:
            self.busy = False
        return item
    #@+node:ekr.20190613080606.1: *4* qtree.unselectItem
    def unselectItem(self, p):

        item = self.position2item(p)
        if item:
            item.setSelected(False)
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 80
#@-leo
