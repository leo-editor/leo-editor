# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20140907123524.18774: * @file ../plugins/qt_frame.py
#@@first
"""Leo's qt frame classes."""
#@+<< imports >>
#@+node:ekr.20110605121601.18003: **  << imports >> (qt_frame.py)
import leo.core.leoGlobals as g
import leo.core.leoColor as leoColor
import leo.core.leoColorizer as leoColorizer
import leo.core.leoFrame as leoFrame
import leo.core.leoMenu as leoMenu
import leo.commands.gotoCommands as gotoCommands
from leo.core.leoQt import isQt5, QtCore, QtGui, QtWidgets
from leo.core.leoQt import Qsci
import leo.plugins.qt_events as qt_events
import leo.plugins.qt_text as qt_text
import leo.plugins.qt_tree as qt_tree
from leo.plugins.mod_scripting import build_rclick_tree
import os
import sys
import platform
from collections import defaultdict
try:
    import leo.plugins.nested_splitter as nested_splitter
    splitter_class = nested_splitter.NestedSplitter
    nested_splitter.NestedSplitter.enabled = False
        # Disable special behavior, turned back on by associated plugin.
except ImportError:
    print('Can not import nested_splitter')
    splitter_class = QtWidgets.QSplitter
#@-<< imports >>
floatable_docks = True
    # True: allow QDockWidgets to float.

#@+others
#@+node:ekr.20110605121601.18137: ** class  DynamicWindow (QMainWindow)
class DynamicWindow(QtWidgets.QMainWindow):
    """
    A class representing all parts of the main Qt window.
    
    c.frame.top is a DynamicWindow.
    c.frame.top.leo_master is a LeoTabbedTopLevel.
    c.frame.top.parent() is a QStackedWidget()

    All leoQtX classes use the ivars of this Window class to
    support operations requested by Leo's core.
    """
    #@+others
    #@+node:ekr.20110605121601.18138: *3*  dw.ctor & reloadSettings
    def __init__(self, c, parent=None):
        """Ctor for the DynamicWindow class.  The main window is c.frame.top"""
            # Called from LeoQtFrame.finishCreate.
            # parent is a LeoTabbedTopLevel.
        if 'startup' in g.app.debug:
            print('DynamicWindow.__init__', c.shortFileName())
        super().__init__(parent)
        self.leo_c = c
        self.leo_docks = [] # List of created QDockWidgets.
        self.leo_master = None # Set in construct.
        self.leo_menubar = None # Set in createMenuBar.
        c._style_deltas = defaultdict(lambda: 0) # for adjusting styles dynamically
        self.reloadSettings()

    def reloadSettings(self):
        c = self.leo_c
        c.registerReloadSettings(self)
        self.bigTree = c.config.getBool('big-outline-pane')
        self.show_iconbar = c.config.getBool('show-iconbar', default=True)
        self.toolbar_orientation = c.config.getString('qt-toolbar-location') or ''
        self.use_gutter = c.config.getBool('use-gutter', default=False)
        if getattr(self, 'iconBar', None):
            if self.show_iconbar:
                self.iconBar.show()
            else:
                self.iconBar.hide()
    #@+node:ekr.20110605121601.18172: *3* dw.do_leo_spell_btn_*
    def doSpellBtn(self, btn):
        """Execute btn, a button handler."""
        # Make *sure* this never crashes.
        try:
            tab = self.leo_c.spellCommands.handler.tab
            button = getattr(tab, btn)
            button()
        except Exception:
            g.es_exception()

    def do_leo_spell_btn_Add(self):
        self.doSpellBtn('onAddButton')

    def do_leo_spell_btn_Change(self):
        self.doSpellBtn('onChangeButton')

    def do_leo_spell_btn_Find(self):
        self.doSpellBtn('onFindButton')

    def do_leo_spell_btn_FindChange(self):
        self.doSpellBtn('onChangeThenFindButton')

    def do_leo_spell_btn_Hide(self):
        self.doSpellBtn('onHideButton')

    def do_leo_spell_btn_Ignore(self):
        self.doSpellBtn('onIgnoreButton')
    #@+node:ekr.20190523115826.1: *3* dw.addEditorDock
    added_bodies = 0

    def addEditorDock(self, closeable=True, moveable=True):
        """Add an editor dock"""
        #
        # Create the new dock.
        c = self.leo_c
        self.added_bodies += 1
        dock = g.app.gui.create_dock_widget(
            closeable=closeable,
            moveable=moveable,
            height=50,
            name=f"body-{self.added_bodies}",
        )
        self.leo_docks.append(dock)
        w = self.createBodyPane(parent=None)
        dock.setWidget(w)
        self.splitDockWidget(self.body_dock, dock, QtCore.Qt.Horizontal)
        #
        # monkey-patch dock.closeEvent
        def patched_closeEvent(event=None):
            c.frame.body.delete_editor_command(event,dock=dock)
           
        dock.closeEvent = patched_closeEvent
        return dock
    #@+node:ekr.20110605121601.18140: *3* dw.closeEvent
    def closeEvent(self, event):
        """Handle a close event in the Leo window."""
        c = self.leo_c
        if not c.exists:
            # Fixes double-prompt bug on Linux.
            event.accept()
            return
        if c.inCommand:
            c.requestCloseWindow = True
            return
        ok = g.app.closeLeoWindow(c.frame)
        if ok:
            event.accept()
        else:
            event.ignore()
    #@+node:ekr.20110605121601.18139: *3* dw.construct & helpers
    def construct(self, master=None):
        """ Factor 'heavy duty' code out from the DynamicWindow ctor """
        c = self.leo_c
        self.leo_master = master
            # A LeoTabbedTopLevel for tabbed windows.
            # None for non-tabbed windows.
        self.useScintilla = c.config.getBool('qt-use-scintilla')
        self.reloadSettings()
        main_splitter, secondary_splitter = self.createMainWindow()
        self.iconBar = self.addToolBar("IconBar")
        self.iconBar.setObjectName('icon-bar')
            # Required for QMainWindow.saveState().
        self.set_icon_bar_orientation(c)
        # #266 A setting to hide the icon bar.
        # Calling reloadSettings again would also work.
        if not self.show_iconbar:
            self.iconBar.hide()
        self.leo_menubar = self.menuBar()
        self.statusBar = QtWidgets.QStatusBar()
        self.setStatusBar(self.statusBar)
        if g.app.dock:
            pass
        else:
            orientation = c.config.getString('initial-split-orientation')
            self.setSplitDirection(main_splitter, secondary_splitter, orientation)
        if hasattr(c, 'styleSheetManager'):
            c.styleSheetManager.set_style_sheets(top=self, all=True)
    #@+node:ekr.20140915062551.19519: *4* dw.set_icon_bar_orientation
    def set_icon_bar_orientation(self, c):
        """Set the orientation of the icon bar based on settings."""
        d = {
            'bottom': QtCore.Qt.BottomToolBarArea,
            'left': QtCore.Qt.LeftToolBarArea,
            'right': QtCore.Qt.RightToolBarArea,
            'top': QtCore.Qt.TopToolBarArea,
        }
        where = self.toolbar_orientation
        if not where:
            where = 'top'
        where = d.get(where.lower())
        if where:
            self.addToolBar(where, self.iconBar)
    #@+node:ekr.20110605121601.18141: *3* dw.createMainWindow & helpers
    def createMainWindow(self):
        """
        Create the component ivars of the main window.
        Copied/adapted from qt_main.py.
        Called instead of uic.loadUi(ui_description_file, self)
        """
        self.setMainWindowOptions()
        if g.app.dock:
            # Widgets.
            self.createAllDockWidgets()
            # Signals.
            QtCore.QMetaObject.connectSlotsByName(self)
            return None, None
        #
        # Legacy code: will not go away.
        self.createCentralWidget()
        main_splitter, secondary_splitter = self.createMainLayout(self.centralwidget)
            # Creates .verticalLayout
        if self.bigTree:
            # Top pane contains only outline.  Bottom pane contains body and log panes.
            self.createBodyPane(secondary_splitter)
            self.createLogPane(secondary_splitter)
            treeFrame = self.createOutlinePane(main_splitter)
            main_splitter.addWidget(treeFrame)
            main_splitter.addWidget(secondary_splitter)
        else:
            # Top pane contains outline and log panes.
            self.createOutlinePane(secondary_splitter)
            self.createLogPane(secondary_splitter)
            self.createBodyPane(main_splitter)
        self.createMiniBuffer(self.centralwidget)
        self.createMenuBar()
        self.createStatusBar(self)
        # Signals...
        QtCore.QMetaObject.connectSlotsByName(self)
        return main_splitter, secondary_splitter
    #@+node:ekr.20110605121601.18142: *4* dw.top-level
    #@+node:ekr.20190118150859.10: *5* dw.addNewEditor
    def addNewEditor(self, name):
        """Create a new body editor."""
        c, p = self.leo_c, self.leo_c.p
        body = c.frame.body
        assert isinstance(body, LeoQtBody), repr(body)
        if not g.app.dock:
            #@+<< legacy dw.addNewEditor >>
            #@+node:ekr.20190526113348.1: *6* << legacy dw.addNewEditor >>
            #
            # Step 1: create the editor.
            parent_frame = c.frame.top.leo_body_inner_frame
            widget = qt_text.LeoQTextBrowser(parent_frame, c, self)
            widget.setObjectName('richTextEdit') # Will be changed later.
            wrapper = qt_text.QTextEditWrapper(widget, name='body', c=c)
            self.packLabel(widget)
            #
            # Step 2: inject ivars, set bindings, etc.
            inner_frame = c.frame.top.leo_body_inner_frame
                # Inject ivars *here*, regardless of docking.
            body.injectIvars(inner_frame, name, p, wrapper)
            body.updateInjectedIvars(widget, p)
            wrapper.setAllText(p.b)
            wrapper.see(0)
            c.k.completeAllBindingsForWidget(wrapper)
            if isinstance(widget, QtWidgets.QTextEdit):
                colorizer = leoColorizer.make_colorizer(c, widget, wrapper)
                colorizer.highlighter.setDocument(widget.document())
            else:
                # Scintilla only.
                body.recolorWidget(p, wrapper)

            #@-<< legacy dw.addNewEditor >>
            return parent_frame, wrapper
        #
        # Create the editor.
        parent_frame = self.addEditorDock()
        widget = qt_text.LeoQTextBrowser(None, c, self)
            # Splits the body dock.
        widget.setObjectName('richTextEdit')
        wrapper = qt_text.QTextEditWrapper(widget, name='body', c=c)
        self.packLabel(widget)
        #
        # Inject ivars, set bindings, etc.
        inner_frame = self.leo_body_inner_frame
            # Inject ivars *here*, regardless of docking.
        body.injectIvars(inner_frame, name, p, wrapper)
        body.updateInjectedIvars(widget, p)
        wrapper.setAllText(p.b)
        wrapper.see(0)
        c.k.completeAllBindingsForWidget(wrapper)
        if isinstance(widget, QtWidgets.QTextEdit):
            colorizer = leoColorizer.make_colorizer(c, widget, wrapper)
            colorizer.highlighter.setDocument(widget.document())
        else:
            # Scintilla only.
            body.recolorWidget(p, wrapper)
        return parent_frame, wrapper
    #@+node:ekr.20190522165123.1: *5* dw.createAllDockWidgets (changed)
    def createAllDockWidgets(self):
        """Create all the dock widgets."""
        c = self.leo_c
        #
        # Compute constants.
        Qt = QtCore.Qt
        bottom, top = Qt.BottomDockWidgetArea, Qt.TopDockWidgetArea
        lt, rt = Qt.LeftDockWidgetArea, Qt.RightDockWidgetArea
        g.placate_pyflakes(bottom, lt, rt, top)
        #
        # Create all the docks.
        central_widget = g.app.get_central_widget(c)
        dockable = c.config.getBool('dockable-log-tabs', default=False)
        table = [
            (True, 50, lt, 'outline', self.createOutlineDock), # was 100: #1339.
            (True, 50, bottom, 'body', self.createBodyPane), # was 100: #1339.
            (True, 50, rt, 'tabs', self.createTabsDock), # was 20: #1339.
            (dockable, 20, rt, 'find', self.createFindDockOrTab),
            (dockable, 20, rt, 'spell', self.createSpellDockOrTab),
        ]
        for make_dock, height, area, name, creator in table:
            w = creator(parent=None)
            if not make_dock:
                setattr(self, f"{name}_dock", None)
                continue
            dock = g.app.gui.create_dock_widget(
                closeable=name != central_widget,
                moveable=name != central_widget,
                height=0,
                name=name)
            dock.setWidget(w)
            # Remember the dock.
            setattr(self, '%s_dock' % (name), dock)
            if name == central_widget:
                self.setCentralWidget(dock)
                    # Important: the central widget should be a dock.
                dock.show() # #1327.
            else:
                self.addDockWidget(area, dock)
        #
        # Create minibuffer.
        bottom_toolbar = QtWidgets.QToolBar(self)
        bottom_toolbar.setObjectName('minibuffer-toolbar')
        bottom_toolbar.setWindowTitle('Minibuffer')
        self.addToolBar(Qt.BottomToolBarArea, bottom_toolbar)
        w = self.createMiniBuffer(bottom_toolbar)
        bottom_toolbar.addWidget(w)
        # 
        # Create other widgets...
        self.createMenuBar()
        self.createStatusBar(self)
    #@+node:ekr.20110605121601.18143: *5* dw.createBodyPane
    def createBodyPane(self, parent):
        """
        Create the *pane* for the body, but does not create the actual QTextBrowser.
        parent is None when --dock is in effect.
        """
        c = self.leo_c
        if not g.app.dock:
            #@+<< legacy createBodyPane >>
            #@+node:ekr.20190526113145.1: *6* << legacy createBodyPane >>
            #
            # Create widgets.
            bodyFrame = self.createFrame(parent, 'bodyFrame')
            innerFrame = self.createFrame(bodyFrame, 'innerBodyFrame')
            sw = self.createStackedWidget(innerFrame, 'bodyStackedWidget',
                 hPolicy=QtWidgets.QSizePolicy.Expanding,
                    # Needed for docks.
                 vPolicy=QtWidgets.QSizePolicy.Expanding,
            )
            page2 = QtWidgets.QWidget()
            self.setName(page2, 'bodyPage2')
            body = self.createText(page2, 'richTextEdit') # A LeoQTextBrowser
            #
            # Pack.
            vLayout = self.createVLayout(page2, 'bodyVLayout', spacing=0)
            grid = self.createGrid(bodyFrame, 'bodyGrid')
            innerGrid = self.createGrid(innerFrame, 'bodyInnerGrid')
            if self.use_gutter:
                lineWidget = qt_text.LeoLineTextWidget(c, body)
                vLayout.addWidget(lineWidget)
            else:
                vLayout.addWidget(body)
            sw.addWidget(page2)
            innerGrid.addWidget(sw, 0, 0, 1, 1)
            grid.addWidget(innerFrame, 0, 0, 1, 1)
            self.verticalLayout.addWidget(parent)
            #
            # Official ivars
            self.text_page = page2
            self.stackedWidget = sw # used by LeoQtBody
            self.richTextEdit = body
            self.leo_body_frame = bodyFrame
            self.leo_body_inner_frame = innerFrame
            #@-<< legacy createBodyPane >>
            return bodyFrame
        #
        # Create widgets.
        #
        # bodyFrame has a VGridLayout.
        bodyFrame = self.createFrame(parent, 'bodyFrame')
        grid = self.createGrid(bodyFrame, 'bodyGrid')
        #
        # innerFrame has a VBoxLayout.
        innerFrame = self.createFrame(bodyFrame, 'innerBodyFrame')
        box = self.createVLayout(innerFrame, 'bodyVLayout', spacing=0)
        #
        # Pack the body alone or *within* a LeoLineTextWidget.
        body = self.createText(None, 'richTextEdit') # A LeoQTextBrowser
        if self.use_gutter:
            lineWidget = qt_text.LeoLineTextWidget(c, body)
            box.addWidget(lineWidget)
        else:
            box.addWidget(body)
        grid.addWidget(innerFrame, 0, 0, 1, 1)
        #
        # Official ivars
        self.richTextEdit = body
        self.leo_body_frame = bodyFrame
        self.leo_body_inner_frame = innerFrame
        return bodyFrame
    #@+node:ekr.20110605121601.18144: *5* dw.createCentralWidget
    def createCentralWidget(self):
        """Create the central widget."""
        dw = self
        w = QtWidgets.QWidget(dw)
        w.setObjectName("centralwidget")
        dw.setCentralWidget(w)
        # Official ivars.
        self.centralwidget = w
        return w
    #@+node:ekr.20110605121601.18145: *5* dw.createLogPane & helpers (legacy)
    def createLogPane(self, parent):
        """Create all parts of Leo's log pane."""
        c = self.leo_c
        #
        # Create the log frame.
        logFrame = self.createFrame(parent, 'logFrame',
            vPolicy=QtWidgets.QSizePolicy.Minimum)
        innerFrame = self.createFrame(logFrame, 'logInnerFrame',
            hPolicy=QtWidgets.QSizePolicy.Preferred,
            vPolicy=QtWidgets.QSizePolicy.Expanding)
        tabWidget = self.createTabWidget(innerFrame, 'logTabWidget')
        #
        # Pack.
        innerGrid = self.createGrid(innerFrame, 'logInnerGrid')
        innerGrid.addWidget(tabWidget, 0, 0, 1, 1)
        outerGrid = self.createGrid(logFrame, 'logGrid')
        outerGrid.addWidget(innerFrame, 0, 0, 1, 1)
        #
        # Create the Find tab, embedded in a QScrollArea.
        findScrollArea = QtWidgets.QScrollArea()
        findScrollArea.setObjectName('findScrollArea')
        # Find tab.
        findTab = QtWidgets.QWidget()
        findTab.setObjectName('findTab')
        # Fix #516:
        use_minibuffer = c.config.getBool('minibuffer-find-mode', default=False)
        use_dialog = c.config.getBool('use-find-dialog', default=False)
        if not use_minibuffer and not use_dialog:
            tabWidget.addTab(findScrollArea, 'Find')
        # Do this later, in LeoFind.finishCreate
        self.findScrollArea = findScrollArea
        self.findTab = findTab
        #
        # Spell tab.
        spellTab = QtWidgets.QWidget()
        spellTab.setObjectName('spellTab')
        tabWidget.addTab(spellTab, 'Spell')
        self.createSpellTab(spellTab)
        tabWidget.setCurrentIndex(1)
        #
        # Official ivars
        self.tabWidget = tabWidget # Used by LeoQtLog.
    #@+node:ekr.20131118172620.16858: *6* dw.finishCreateLogPane
    def finishCreateLogPane(self):
        """It's useful to create this late, because c.config is now valid."""
        # self.findTab exists even if there is not Find tab in the Log pane.
        assert self.findTab
        self.createFindTab(self.findTab, self.findScrollArea)
        self.findScrollArea.setWidget(self.findTab)
    #@+node:ekr.20110605121601.18146: *5* dw.createMainLayout
    def createMainLayout(self, parent):
        """Create the layout for Leo's main window."""
        # c = self.leo_c
        vLayout = self.createVLayout(parent, 'mainVLayout', margin=3)
        main_splitter = splitter_class(parent)
        main_splitter.setObjectName('main_splitter')
        main_splitter.setOrientation(QtCore.Qt.Vertical)
        secondary_splitter = splitter_class(main_splitter)
        secondary_splitter.setObjectName('secondary_splitter')
        secondary_splitter.setOrientation(QtCore.Qt.Horizontal)
        # Official ivar:
        self.verticalLayout = vLayout
        self.setSizePolicy(secondary_splitter)
        self.verticalLayout.addWidget(main_splitter)
        return main_splitter, secondary_splitter
    #@+node:ekr.20110605121601.18147: *5* dw.createMenuBar
    def createMenuBar(self):
        """Create Leo's menu bar."""
        dw = self
        w = QtWidgets.QMenuBar(dw)
        w.setNativeMenuBar(platform.system() == 'Darwin')
        w.setGeometry(QtCore.QRect(0, 0, 957, 22))
        w.setObjectName("menubar")
        dw.setMenuBar(w)
        # Official ivars.
        self.leo_menubar = w
    #@+node:ekr.20110605121601.18148: *5* dw.createMiniBuffer (class VisLineEdit)
    def createMiniBuffer(self, parent):
        """Create the widgets for Leo's minibuffer area."""
        dw = self # For VisLineEdit
        # Create widgets.
        frame = self.createFrame(parent, 'minibufferFrame',
            hPolicy=QtWidgets.QSizePolicy.MinimumExpanding,
            vPolicy=QtWidgets.QSizePolicy.Fixed)
        frame.setMinimumSize(QtCore.QSize(100, 0))
        label = self.createLabel(frame, 'minibufferLabel', 'Minibuffer:')

        class VisLineEdit(QtWidgets.QLineEdit):
            """In case user has hidden minibuffer with gui-minibuffer-hide"""

            def focusInEvent(self, event):
                self.parent().show()
                if g.app.dock:
                    # Ensure the Tabs dock is visible, for completions.
                    dock = getattr(dw, 'tabs_dock', None)
                    if dock:
                        dock.raise_()
                        parent.raise_()
                super().focusInEvent(event)
                    # Call the base class method.

            def focusOutEvent(self, event):
                self.store_selection()
                super().focusOutEvent(event)

            def restore_selection(self):
                w = self
                i, j, ins = self._sel_and_insert
                if i == j:
                    w.setCursorPosition(i)
                else:
                    length = j - i
                    # Set selection is a QLineEditMethod
                    if ins < j:
                        w.setSelection(j, -length)
                    else:
                        w.setSelection(i, length)

            def store_selection(self):
                w = self
                ins = w.cursorPosition()
                if w.hasSelectedText():
                    i = w.selectionStart()
                    s = w.selectedText()
                    j = i + len(s)
                else:
                    i = j = ins
                w._sel_and_insert = (i, j, ins)

        lineEdit = VisLineEdit(frame)
        lineEdit._sel_and_insert = (0, 0, 0)
        lineEdit.setObjectName('lineEdit') # name important.
        # Pack.
        hLayout = self.createHLayout(frame, 'minibufferHLayout', spacing=4)
        hLayout.setContentsMargins(3, 2, 2, 0)
        hLayout.addWidget(label)
        hLayout.addWidget(lineEdit)
        if g.app.dock:
            # Parent is a QDockWidget.
            pass
        else:
            self.verticalLayout.addWidget(frame)
        label.setBuddy(lineEdit)
            # Transfers focus request from label to lineEdit.
        #
        # Official ivars.
        self.lineEdit = lineEdit
        # self.leo_minibuffer_frame = frame
        # self.leo_minibuffer_layout = layout
        return frame
    #@+node:ekr.20110605121601.18149: *5* dw.createOutlinePane
    def createOutlinePane(self, parent):
        """Create the widgets and ivars for Leo's outline."""
        # Create widgets.
        treeFrame = self.createFrame(parent, 'outlineFrame',
            vPolicy=QtWidgets.QSizePolicy.Expanding)
        innerFrame = self.createFrame(treeFrame, 'outlineInnerFrame',
            hPolicy=QtWidgets.QSizePolicy.Preferred)
        treeWidget = self.createTreeWidget(innerFrame, 'treeWidget')
        grid = self.createGrid(treeFrame, 'outlineGrid')
        grid.addWidget(innerFrame, 0, 0, 1, 1)
        innerGrid = self.createGrid(innerFrame, 'outlineInnerGrid')
        innerGrid.addWidget(treeWidget, 0, 0, 1, 1)
        # Official ivars...
        self.treeWidget = treeWidget
        return treeFrame
    #@+node:ekr.20110605121601.18150: *5* dw.createStatusBar
    def createStatusBar(self, parent):
        """Create the widgets and ivars for Leo's status area."""
        w = QtWidgets.QStatusBar(parent)
        w.setObjectName("statusbar")
        parent.setStatusBar(w)
        # Official ivars.
        self.statusBar = w
    #@+node:ekr.20110605121601.18212: *5* dw.packLabel
    def packLabel(self, w, n=None):
        """
        Pack w into the body frame's QVGridLayout.
        
        The type of w does not affect the following code. In fact, w is a
        QTextBrowser possibly packed inside a LeoLineTextWidget.
        """
        c = self.leo_c
        #
        # Reuse the grid layout in the body frame.
        grid = self.leo_body_frame.layout()
        #
        # Create the label.
        label = QtWidgets.QLineEdit(None)
        label.setObjectName('editorLabel')
        label.setText(c.p.h)
        #
        # Pack the label and the text widget.
        if g.app.dock:
            grid.addWidget(label, 0, 0)
            grid.addWidget(w, 1, 0)
        else:
            if n is None:
                n = c.frame.body.numberOfEditors
            n = max(0, n-1)
            grid.addWidget(label, 0, n)
            grid.addWidget(w, 1, n)
        grid.setColumnStretch(0, 1) # Grow the label horizontally.
        grid.setRowStretch(0, 0) # Don't grow the label vertically.
        grid.setRowStretch(1, 1) # Give row 1 as much as vertical room as possible.
        w.leo_label = label # Inject the ivar.
    #@+node:ekr.20110605121601.18151: *5* dw.setMainWindowOptions
    def setMainWindowOptions(self):
        """Set default options for Leo's main window."""
        dw = self
        dw.setObjectName("MainWindow")
        dw.resize(691, 635)
        dw.setDockNestingEnabled(False)
        dw.setDockOptions(
            QtWidgets.QMainWindow.AllowTabbedDocks |
            QtWidgets.QMainWindow.AnimatedDocks)
    #@+node:ekr.20190527162547.1: *4* dw.docks
    # Used when legacy_log_dock is False.
    #@+node:ekr.20190527120808.1: *5* dw.createFindDockOrTab
    def createFindDockOrTab(self, parent):
        """Create a Find dock or tab in the Log pane."""
        assert g.app.dock
        assert not parent, repr(parent)
        c = self.leo_c
        #
        # Create widgets.
        findTab = QtWidgets.QWidget()
        findTab.setObjectName('findTab')
        findScrollArea = QtWidgets.QScrollArea()
        findScrollArea.setObjectName('findScrollArea')
        #
        # For LeoFind.finishCreate.
        self.findScrollArea = findScrollArea
        self.findTab = findTab
        #
        # Create a tab in the log Dock, if necessary.
        if not c.config.getBool('dockable-log-tabs', default=False):
            self.tabWidget.addTab(findScrollArea, 'Find')
        return findScrollArea
    #@+node:ekr.20190528112002.1: *5* dw.createOutlineDock
    def createOutlineDock(self, parent):
        """Create the widgets and ivars for Leo's outline."""
        # Create widgets.
        treeFrame = self.createFrame(parent, 'outlineFrame',
            vPolicy=QtWidgets.QSizePolicy.Expanding)
        innerFrame = self.createFrame(treeFrame, 'outlineInnerFrame',
            hPolicy=QtWidgets.QSizePolicy.Preferred)
        treeWidget = self.createTreeWidget(innerFrame, 'treeWidget')
        grid = self.createGrid(treeFrame, 'outlineGrid')
        grid.addWidget(innerFrame, 0, 0, 1, 1)
        innerGrid = self.createGrid(innerFrame, 'outlineInnerGrid')
        innerGrid.addWidget(treeWidget, 0, 0, 1, 1)
        # Official ivars...
        self.treeWidget = treeWidget
        return treeFrame
    #@+node:ekr.20190527120829.1: *5* dw.createSpellDockOrTab
    def createSpellDockOrTab(self, parent):
        """Create a Spell dock  or tab in the Log pane."""
        assert g.app.dock
        assert not parent, repr(parent)
        c = self.leo_c
        #
        # Create an outer widget.
        spellTab = QtWidgets.QWidget()
        spellTab.setObjectName('docked.spellTab')
        #
        # Create the contents.
        self.createSpellTab(spellTab)
        #
        # Create the Spell tab in the Log dock, if necessary.
        if not c.config.getBool('dockable-log-tabs', default=False):
            tabWidget = self.tabWidget
            tabWidget.addTab(spellTab, 'Spell')
            tabWidget.setCurrentIndex(1)
        return spellTab
    #@+node:ekr.20190527163203.1: *5* dw.createTabbedLogDock (legacy)
    def createTabbedLogDock(self, parent):
        """Create a tabbed (legacy) Log dock."""
        assert g.app.dock
        assert not parent, repr(parent)
        c = self.leo_c
        #
        # Create the log frame.
        logFrame = self.createFrame(parent, 'logFrame',
            vPolicy=QtWidgets.QSizePolicy.Minimum)
        innerFrame = self.createFrame(logFrame, 'logInnerFrame',
            hPolicy=QtWidgets.QSizePolicy.Preferred,
            vPolicy=QtWidgets.QSizePolicy.Expanding)
        tabWidget = self.createTabWidget(innerFrame, 'logTabWidget')
        #
        # Pack.
        innerGrid = self.createGrid(innerFrame, 'logInnerGrid')
        innerGrid.addWidget(tabWidget, 0, 0, 1, 1)
        outerGrid = self.createGrid(logFrame, 'logGrid')
        outerGrid.addWidget(innerFrame, 0, 0, 1, 1)
        #
        # Create the Find tab, embedded in a QScrollArea.
        findScrollArea = QtWidgets.QScrollArea()
        findScrollArea.setObjectName('findScrollArea')
        # Find tab.
        findTab = QtWidgets.QWidget()
        findTab.setObjectName('findTab')
        # Fix #516:
        use_minibuffer = c.config.getBool('minibuffer-find-mode', default=False)
        use_dialog = c.config.getBool('use-find-dialog', default=False)
        if not use_minibuffer and not use_dialog:
            tabWidget.addTab(findScrollArea, 'Find')
        # Do this later, in LeoFind.finishCreate
        self.findScrollArea = findScrollArea
        self.findTab = findTab
        #
        # Spell tab.
        spellTab = QtWidgets.QWidget()
        spellTab.setObjectName('spellTab')
        tabWidget.addTab(spellTab, 'Spell')
        self.createSpellTab(spellTab)
        tabWidget.setCurrentIndex(1)
        #
        # Official ivars
        self.tabWidget = tabWidget # Used by LeoQtLog.
        return logFrame
    #@+node:ekr.20190527121112.1: *5* dw.createTabsDock
    def createTabsDock(self, parent):
        """Create the Tabs dock."""
        assert g.app.dock
        assert not parent, repr(parent)
        #
        # Create the log contents
        logFrame = self.createFrame(None, 'logFrame',
            vPolicy=QtWidgets.QSizePolicy.Minimum)
        innerFrame = self.createFrame(logFrame, 'logInnerFrame',
            hPolicy=QtWidgets.QSizePolicy.Preferred,
            vPolicy=QtWidgets.QSizePolicy.Expanding)
        tabWidget = self.createTabWidget(innerFrame, 'logTabWidget')
        #
        # Pack. This *is* required.
        innerGrid = self.createGrid(innerFrame, 'logInnerGrid')
        innerGrid.addWidget(tabWidget, 0, 0, 1, 1)
        outerGrid = self.createGrid(logFrame, 'logGrid')
        outerGrid.addWidget(innerFrame, 0, 0, 1, 1)
        #
        # Official ivars
        self.tabWidget = tabWidget # Used by LeoQtLog.
        return logFrame
    #@+node:ekr.20110605121601.18152: *4* dw.widgets
    #@+node:ekr.20110605121601.18153: *5* dw.createButton
    def createButton(self, parent, name, label):
        w = QtWidgets.QPushButton(parent)
        w.setObjectName(name)
        w.setText(self.tr(label))
        return w
    #@+node:ekr.20110605121601.18154: *5* dw.createCheckBox
    def createCheckBox(self, parent, name, label):
        w = QtWidgets.QCheckBox(parent)
        self.setName(w, name)
        w.setText(self.tr(label))
        return w
    #@+node:ekr.20110605121601.18155: *5* dw.createFrame
    def createFrame(self, parent, name,
        hPolicy=None, vPolicy=None,
        lineWidth=1,
        shadow=QtWidgets.QFrame.Plain,
        shape=QtWidgets.QFrame.NoFrame,
    ):
        """Create a Qt Frame."""
        w = QtWidgets.QFrame(parent)
        self.setSizePolicy(w, kind1=hPolicy, kind2=vPolicy)
        w.setFrameShape(shape)
        w.setFrameShadow(shadow)
        w.setLineWidth(lineWidth)
        self.setName(w, name)
        return w
    #@+node:ekr.20110605121601.18156: *5* dw.createGrid
    def createGrid(self, parent, name, margin=0, spacing=0):
        w = QtWidgets.QGridLayout(parent)
        w.setContentsMargins(QtCore.QMargins(margin, margin, margin, margin))
        w.setSpacing(spacing)
        self.setName(w, name)
        return w
    #@+node:ekr.20110605121601.18157: *5* dw.createHLayout & createVLayout
    def createHLayout(self, parent, name, margin=0, spacing=0):
        hLayout = QtWidgets.QHBoxLayout(parent)
        hLayout.setSpacing(spacing)
        hLayout.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
        self.setName(hLayout, name)
        return hLayout

    def createVLayout(self, parent, name, margin=0, spacing=0):
        vLayout = QtWidgets.QVBoxLayout(parent)
        vLayout.setSpacing(spacing)
        vLayout.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
        self.setName(vLayout, name)
        return vLayout
    #@+node:ekr.20110605121601.18158: *5* dw.createLabel
    def createLabel(self, parent, name, label):
        w = QtWidgets.QLabel(parent)
        self.setName(w, name)
        w.setText(self.tr(label))
        return w
    #@+node:ekr.20110605121601.18159: *5* dw.createLineEdit
    def createLineEdit(self, parent, name, disabled=True):

        w = QtWidgets.QLineEdit(parent)
        w.setObjectName(name)
        w.leo_disabled = disabled # Inject the ivar.
        return w
    #@+node:ekr.20110605121601.18160: *5* dw.createRadioButton
    def createRadioButton(self, parent, name, label):
        w = QtWidgets.QRadioButton(parent)
        self.setName(w, name)
        w.setText(self.tr(label))
        return w
    #@+node:ekr.20110605121601.18161: *5* dw.createStackedWidget
    def createStackedWidget(self, parent, name,
        lineWidth=1,
        hPolicy=None, vPolicy=None,
    ):
        w = QtWidgets.QStackedWidget(parent)
        self.setSizePolicy(w, kind1=hPolicy, kind2=vPolicy)
        w.setAcceptDrops(True)
        w.setLineWidth(1)
        self.setName(w, name)
        return w
    #@+node:ekr.20110605121601.18162: *5* dw.createTabWidget
    def createTabWidget(self, parent, name, hPolicy=None, vPolicy=None):
        w = QtWidgets.QTabWidget(parent)
        # tb = w.tabBar()
        # tb.setTabsClosable(True)
        self.setSizePolicy(w, kind1=hPolicy, kind2=vPolicy)
        self.setName(w, name)
        return w
    #@+node:ekr.20110605121601.18163: *5* dw.createText (creates QTextBrowser)
    def createText(self, parent, name,
        lineWidth=0,
        shadow=QtWidgets.QFrame.Plain,
        shape=QtWidgets.QFrame.NoFrame,
    ):
        # Create a text widget.
        c = self.leo_c
        if name == 'richTextEdit' and self.useScintilla and Qsci:
            # Do this in finishCreate, when c.frame.body exists.
            w = Qsci.QsciScintilla(parent)
            self.scintilla_widget = w
        else:
            w = qt_text.LeoQTextBrowser(parent, c, None)
            w.setFrameShape(shape)
            w.setFrameShadow(shadow)
            w.setLineWidth(lineWidth)
            self.setName(w, name)
        return w
    #@+node:ekr.20110605121601.18164: *5* dw.createTreeWidget
    def createTreeWidget(self, parent, name):
        c = self.leo_c
        w = LeoQTreeWidget(c, parent)
        self.setSizePolicy(w)
        # 12/01/07: add new config setting.
        multiple_selection = c.config.getBool('qt-tree-multiple-selection', default=True)
        if multiple_selection:
            w.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
            w.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        else:
            w.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
            w.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        w.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        w.setHeaderHidden(False)
        self.setName(w, name)
        return w
    #@+node:ekr.20110605121601.18165: *4* dw.log tabs
    #@+node:ekr.20110605121601.18167: *5* dw.createSpellTab
    def createSpellTab(self, parent):
        # dw = self
        vLayout = self.createVLayout(parent, 'spellVLayout', margin=2)
        spellFrame = self.createFrame(parent, 'spellFrame')
        vLayout2 = self.createVLayout(spellFrame, 'spellVLayout')
        grid = self.createGrid(None, 'spellGrid', spacing=2)
        table = (
            ('Add', 'Add', 2, 1),
            ('Find', 'Find', 2, 0),
            ('Change', 'Change', 3, 0),
            ('FindChange', 'Change,Find', 3, 1),
            ('Ignore', 'Ignore', 4, 0),
            ('Hide', 'Hide', 4, 1),
        )
        for(ivar, label, row, col) in table:
            name = f"spell_{label}_button"
            button = self.createButton(spellFrame, name, label)
            grid.addWidget(button, row, col)
            func = getattr(self, f"do_leo_spell_btn_{ivar}")
            button.clicked.connect(func)
            # This name is significant.
            setattr(self, 'leo_spell_btn_%s' % (ivar), button)
        self.leo_spell_btn_Hide.setCheckable(False)
        spacerItem = QtWidgets.QSpacerItem(20, 40,
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        grid.addItem(spacerItem, 5, 0, 1, 1)
        listBox = QtWidgets.QListWidget(spellFrame)
        self.setSizePolicy(listBox,
            kind1=QtWidgets.QSizePolicy.MinimumExpanding,
            kind2=QtWidgets.QSizePolicy.Expanding)
        listBox.setMinimumSize(QtCore.QSize(0, 0))
        listBox.setMaximumSize(QtCore.QSize(150, 150))
        listBox.setObjectName("leo_spell_listBox")
        grid.addWidget(listBox, 1, 0, 1, 2)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20,
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        grid.addItem(spacerItem1, 2, 2, 1, 1)
        lab = self.createLabel(spellFrame, 'spellLabel', 'spellLabel')
        grid.addWidget(lab, 0, 0, 1, 2)
        vLayout2.addLayout(grid)
        vLayout.addWidget(spellFrame)
        listBox.itemDoubleClicked.connect(self.do_leo_spell_btn_FindChange)
        # Official ivars.
        self.spellFrame = spellFrame
        self.spellGrid = grid
        self.leo_spell_widget = parent # 2013/09/20: To allow bindings to be set.
        self.leo_spell_listBox = listBox # Must exist
        self.leo_spell_label = lab # Must exist (!!)
    #@+node:ekr.20110605121601.18166: *5* dw.createFindTab & helpers
    def createFindTab(self, parent, tab_widget):
        """Create a Find Tab in the given parent."""
        c, dw = self.leo_c, self
        fc = c.findCommands
        assert not fc.ftm
        fc.ftm = ftm = FindTabManager(c)
        grid = self.create_find_grid(parent)
        row = 0 # The index for the present row.
        row = dw.create_find_header(grid, parent, row)
        row = dw.create_find_findbox(grid, parent, row)
        row = dw.create_find_replacebox(grid, parent, row)
        max_row2 = 1
        max_row2 = dw.create_find_checkboxes(grid, parent, max_row2, row)
        row = dw.create_find_buttons(grid, parent, max_row2, row)
        row = dw.create_help_row(grid, parent, row)
        dw.override_events()
        # Last row: Widgets that take all additional vertical space.
        w = QtWidgets.QWidget()
        grid.addWidget(w, row, 0)
        grid.addWidget(w, row, 1)
        grid.addWidget(w, row, 2)
        grid.setRowStretch(row, 100)
        # Official ivars (in addition to checkbox ivars).
        self.leo_find_widget = tab_widget # A scrollArea.
        ftm.init_widgets()
    #@+node:ekr.20131118152731.16847: *6* dw.create_find_grid
    def create_find_grid(self, parent):
        grid = self.createGrid(parent, 'findGrid', margin=10, spacing=10)
        grid.setColumnStretch(0, 100)
        grid.setColumnStretch(1, 100)
        grid.setColumnStretch(2, 10)
        grid.setColumnMinimumWidth(1, 75)
        grid.setColumnMinimumWidth(2, 175)
        return grid
    #@+node:ekr.20131118152731.16849: *6* dw.create_find_header
    def create_find_header(self, grid, parent, row):
        if False:
            dw = self
            lab1 = dw.createLabel(parent, 'findHeading', 'Find/Change Settings...')
            grid.addWidget(lab1, row, 0, 1, 2, QtCore.Qt.AlignLeft)
                # AlignHCenter
            row += 1
        return row
    #@+node:ekr.20131118152731.16848: *6* dw.create_find_findbox
    def create_find_findbox(self, grid, parent, row):
        """Create the Find: label and text area."""
        c, dw = self.leo_c, self
        fc = c.findCommands
        ftm = fc.ftm
        assert ftm.find_findbox is None
        ftm.find_findbox = w = dw.createLineEdit(parent, 'findPattern', disabled=fc.expert_mode)
        lab2 = self.createLabel(parent, 'findLabel', 'Find:')
        grid.addWidget(lab2, row, 0)
        grid.addWidget(w, row, 1, 1, 2)
        row += 1
        return row
    #@+node:ekr.20131118152731.16850: *6* dw.create_find_replacebox
    def create_find_replacebox(self, grid, parent, row):
        """Create the Replace: label and text area."""
        c, dw = self.leo_c, self
        fc = c.findCommands
        ftm = fc.ftm
        assert ftm.find_replacebox is None
        ftm.find_replacebox = w = dw.createLineEdit(parent, 'findChange', disabled=fc.expert_mode)
        lab3 = dw.createLabel(parent, 'changeLabel', 'Replace:') # Leo 4.11.1.
        grid.addWidget(lab3, row, 0)
        grid.addWidget(w, row, 1, 1, 2)
        row += 1
        return row
    #@+node:ekr.20131118152731.16851: *6* dw.create_find_checkboxes
    def create_find_checkboxes(self, grid, parent, max_row2, row):
        """Create check boxes and radio buttons."""
        c, dw = self.leo_c, self
        fc = c.findCommands
        ftm = fc.ftm

        def mungeName(kind, label):
            # The returned value is the namve of an ivar.
            kind = 'check_box_' if kind == 'box' else 'radio_button_'
            name = label.replace(' ', '_').replace('&', '').lower()
            return f"{kind}{name}"
        # Rows for check boxes, radio buttons & execution buttons...

        d = {
            'box': dw.createCheckBox,
            'rb': dw.createRadioButton,
        }
        table = (
            # Note: the Ampersands create Alt bindings when the log pane is enable.
            # The QShortcut class is the workaround.
            # First row.
            ('box', 'whole &Word', 0, 0),
            ('rb', '&Entire outline', 0, 1),
            # Second row.
            ('box', '&Ignore case', 1, 0),
            ('rb', '&Suboutline only', 1, 1),
            # Third row.
            ('box', 'wrap &Around', 2, 0),
            ('rb', '&Node only', 2, 1),
            # Fourth row.
            ('box', 'rege&Xp', 3, 0),
            ('box', 'search &Headline', 3, 1),
            # Fifth row.
            ('box', 'mark &Finds', 4, 0),
            ('box', 'search &Body', 4, 1),
            # Sixth row.
            ('box', 'mark &Changes', 5, 0),
            # a,b,c,e,f,h,i,n,rs,w
        )
        for kind, label, row2, col in table:
            max_row2 = max(max_row2, row2)
            name = mungeName(kind, label)
            func = d.get(kind)
            assert func
            # Fix the greedy checkbox bug:
            label = label.replace('&', '')
            w = func(parent, name, label)
            grid.addWidget(w, row + row2, col)
            # The the checkbox ivars in dw and ftm classes.
            assert getattr(ftm, name) is None
            setattr(ftm, name, w)
        return max_row2
    #@+node:ekr.20131118152731.16852: *6* dw.create_find_buttons
    def create_find_buttons(self, grid, parent, max_row2, row):
        """
        Per #1342, this method now creates labels, not real buttons.
        """
        dw, k = self, self.leo_c.k

        # Create Buttons in column 2 (Leo 4.11.1.)
        table = (
            (0, 2, 'findButton', 'find-next'),
            (1, 2, 'findPreviousButton', 'find-prev'),
            (2, 2, 'findAllButton', 'find-all'),
            (3, 2, 'changeButton', 'replace'),
            (4, 2, 'changeThenFindButton', 'replace-then-find'),
            (5, 2, 'changeAllButton', 'replace-all'),
        )
        for row2, col, func_name, cmd_name in table:
            stroke = k.getStrokeForCommandName(cmd_name)
            if stroke:
                label = f"{cmd_name}:  {k.prettyPrintKey(stroke)}"
            else:
                label = cmd_name
            # #1342: Create a label, not a button.
            w = dw.createLabel(parent, cmd_name, label)
            w.setObjectName('find-label')
            grid.addWidget(w, row + row2, col)
        row += max_row2
        row += 2
        return row
    #@+node:ekr.20131118152731.16853: *6* dw.create_help_row
    def create_help_row(self, grid, parent, row):
        # Help row.
        if False:
            w = self.createLabel(parent,
                'findHelp', 'For help: <alt-x>help-for-find-commands<return>')
            grid.addWidget(w, row, 0, 1, 3)
            row += 1
        return row
    #@+node:ekr.20150618072619.1: *6* dw.create_find_status
    if 0:
        def create_find_status(self, grid, parent, row):
            """Create the status line."""
            dw = self
            status_label = dw.createLabel(parent, 'status-label', 'Status')
            status_line = dw.createLineEdit(parent, 'find-status', disabled=True)
            grid.addWidget(status_label, row, 0)
            grid.addWidget(status_line, row, 1, 1, 2)
            # Official ivars.
            dw.find_status_label = status_label
            dw.find_status_edit = status_line
    #@+node:ekr.20131118172620.16891: *6* dw.override_events
    def override_events(self):
        # dw = self
        c = self.leo_c
        fc = c.findCommands
        ftm = fc.ftm
        # Define class EventWrapper.
        #@+others
        #@+node:ekr.20131118172620.16892: *7* class EventWrapper
        class EventWrapper:
            
            def __init__(self, c, w, next_w, func):
                self.c = c
                self.d = self.create_d()
                    # Keys: stroke.s; values: command-names.
                self.w = w
                self.next_w = next_w
                self.eventFilter = qt_events.LeoQtEventFilter(c, w, 'EventWrapper')
                self.func = func
                self.oldEvent = w.event
                w.event = self.wrapper

            #@+others
            #@+node:ekr.20131120054058.16281: *8* create_d
            def create_d(self):
                """Create self.d dictionary."""
                c = self.c
                d = {}
                table = (
                    'toggle-find-ignore-case-option',
                    'toggle-find-in-body-option',
                    'toggle-find-in-headline-option',
                    'toggle-find-mark-changes-option',
                    'toggle-find-mark-finds-option',
                    'toggle-find-regex-option',
                    'toggle-find-word-option',
                    'toggle-find-wrap-around-option',
                    # New in Leo 5.2: Support these in the Find Dialog.
                    'find-all',
                    'find-next',
                    'find-prev',
                    'hide-find-tab',
                    'replace',
                    'replace-all',
                    'replace-then-find',
                    'set-find-everywhere',
                    'set-find-node-only',
                    'set-find-suboutline-only',
                )
                for cmd_name in table:
                    stroke = c.k.getStrokeForCommandName(cmd_name)
                    if stroke:
                        d[stroke.s] = cmd_name
                return d
            #@+node:ekr.20131118172620.16893: *8* wrapper
            def wrapper(self, event):

                e = QtCore.QEvent
                type_ = event.type()
                # Must intercept KeyPress for events that generate FocusOut!
                if type_ == e.KeyPress:
                    return self.keyPress(event)
                if type_ == e.KeyRelease:
                    return self.keyRelease(event)
                return self.oldEvent(event)
            #@+node:ekr.20131118172620.16894: *8* keyPress (EventWrapper)
            def keyPress(self, event):

                s = event.text()
                out = s and s in '\t\r\n'
                if out:
                    # Move focus to next widget.
                    if s == '\t':
                        if self.next_w:
                            self.next_w.setFocus(QtCore.Qt.TabFocusReason)
                        else:
                            # Do the normal processing.
                            return self.oldEvent(event)
                    elif self.func:
                        self.func()
                    return True
                # Stay in the present widget.
                binding, ch = self.eventFilter.toBinding(event)
                if  binding:
                    cmd_name = self.d.get(binding)
                    if cmd_name:
                        self.c.k.simulateCommand(cmd_name)
                        return True
                # Do the normal processing.
                return self.oldEvent(event)
            #@+node:ekr.20131118172620.16895: *8* keyRelease
            def keyRelease(self, event):
                return self.oldEvent(event)
            #@-others
        #@-others
        EventWrapper(c, w=ftm.find_findbox, next_w=ftm.find_replacebox, func=fc.findNextCommand)
        EventWrapper(c, w=ftm.find_replacebox, next_w=ftm.find_next_button, func=fc.findNextCommand)
        
        if 0: # #1342: These are no longer needed, because there are no buttons.
            table = (
                ('findNextCommand', 'find-next'),
                ('findPrevCommand', 'find-prev'),
                ('findAll', 'find-all'),
                ('changeCommand', 'replace'),
                ('changeThenFind', 'replace-then-find'),
                ('changeAll', 'replace-all'),
            )
            for func_name, cmd_name in table:
                ivar = f"{cmd_name}-{'button'}"
                ivar = ivar.replace('-', '_')
                w = getattr(ftm, ivar, None)
                func = getattr(fc, func_name, None)
                if w and func:
                    next_w = ftm.check_box_whole_word if cmd_name == 'replace-all' else None
                    EventWrapper(c, w=w, next_w=next_w, func=func)
                else:
                    g.trace('**oops**')
        # Finally, checkBoxMarkChanges goes back to ftm.find_findBox.
        EventWrapper(c, w=ftm.check_box_mark_changes, next_w=ftm.find_findbox, func=None)
    #@+node:ekr.20110605121601.18168: *4* dw.utils
    #@+node:ekr.20110605121601.18169: *5* dw.setName
    def setName(self, widget, name):
        if name:
            # if not name.startswith('leo_'):
                # name = 'leo_' + name
            widget.setObjectName(name)
    #@+node:ekr.20110605121601.18170: *5* dw.setSizePolicy
    def setSizePolicy(self, widget, kind1=None, kind2=None):
        if kind1 is None: kind1 = QtWidgets.QSizePolicy.Ignored
        if kind2 is None: kind2 = QtWidgets.QSizePolicy.Ignored
        sizePolicy = QtWidgets.QSizePolicy(kind1, kind2)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            widget.sizePolicy().hasHeightForWidth())
        widget.setSizePolicy(sizePolicy)
    #@+node:ekr.20110605121601.18171: *5* dw.tr
    def tr(self, s):
        # pylint: disable=no-member
        if isQt5:
            # QApplication.UnicodeUTF8 no longer exists.
            return QtWidgets.QApplication.translate('MainWindow', s, None)
        return QtWidgets.QApplication.translate(
            'MainWindow',
            s,
            None,
            QtWidgets.QApplication.UnicodeUTF8)
    #@+node:ekr.20110605121601.18173: *3* dw.select
    def select(self, c):
        """Select the window or tab for c."""
        # Called from the save commands.
        self.leo_master.select(c)
    #@+node:ekr.20110605121601.18178: *3* dw.setGeometry (legacy)
    def setGeometry(self, rect):
        """Set the window geometry, but only once when using the qt gui."""
        if g.app.qt_use_tabs:
            m = self.leo_master
            assert self.leo_master
            # Only set the geometry once, even for new files.
            if not hasattr(m, 'leo_geom_inited'):
                m.leo_geom_inited = True
                self.leo_master.setGeometry(rect)
                super().setGeometry(rect)
        else:
            super().setGeometry(rect)
    #@+node:ekr.20110605121601.18177: *3* dw.setLeoWindowIcon
    def setLeoWindowIcon(self):
        """ Set icon visible in title bar and task bar """
        # self.setWindowIcon(QtGui.QIcon(g.app.leoDir + "/Icons/leoapp32.png"))
        g.app.gui.attachLeoIcon(self)
    #@+node:ekr.20110605121601.18174: *3* dw.setSplitDirection
    def setSplitDirection(self, main_splitter, secondary_splitter, orientation):
        """Set the orientations of the splitters in the Leo main window."""
        # c = self.leo_c
        vert = orientation and orientation.lower().startswith('v')
        h, v = QtCore.Qt.Horizontal, QtCore.Qt.Vertical
        orientation1 = v if vert else h
        orientation2 = h if vert else v
        main_splitter.setOrientation(orientation1)
        secondary_splitter.setOrientation(orientation2)
    #@+node:ekr.20130804061744.12425: *3* dw.setWindowTitle
    if 0: # Override for debugging only.

        def setWindowTitle(self, s):
            g.trace('***(DynamicWindow)', s, self.parent())
            # Call the base class method.
            QtWidgets.QMainWindow.setWindowTitle(self, s)
    #@-others
#@+node:ekr.20131117054619.16698: ** class FindTabManager
class FindTabManager:
    """A helper class for the LeoFind class."""
    #@+others
    #@+node:ekr.20131117120458.16794: *3*  ftm.ctor
    def __init__(self, c):
        """Ctor for the FindTabManager class."""
        self.c = c
        self.entry_focus = None # The widget that had focus before find-pane entered.
        # Find/change text boxes.
        self.find_findbox = None
        self.find_replacebox = None
        # Check boxes.
        self.check_box_ignore_case = None
        self.check_box_mark_changes = None
        self.check_box_mark_finds = None
        self.check_box_regexp = None
        self.check_box_search_body = None
        self.check_box_search_headline = None
        self.check_box_whole_word = None
        self.check_box_wrap_around = None
        # Radio buttons
        self.radio_button_entire_outline = None
        self.radio_button_node_only = None
        self.radio_button_suboutline_only = None
        # Push buttons
        self.find_next_button = None
        self.find_prev_button = None
        self.find_all_button = None
        self.help_for_find_commands_button = None
        self.replace_button = None
        self.replace_then_find_button = None
        self.replace_all_button = None
    #@+node:ekr.20131117164142.16853: *3* ftm.text getters/setters
    def getFindText(self):
        return self.find_findbox.text()

    def getReplaceText(self):
        return self.find_replacebox.text()

    getChangeText = getReplaceText

    def setFindText(self, s):
        w = self.find_findbox
        s = g.checkUnicode(s)
        w.clear()
        w.insert(s)

    def setReplaceText(self, s):
        w = self.find_replacebox
        s = g.checkUnicode(s)
        w.clear()
        w.insert(s)

    setChangeText = setReplaceText
    #@+node:ekr.20131119185305.16478: *3* ftm.clear_focus & init_focus & set_entry_focus
    def clear_focus(self):
        self.entry_focus = None
        self.find_findbox.clearFocus()

    def init_focus(self):
        self.set_entry_focus()
        w = self.find_findbox
        w.setFocus()
        s = w.text()
        w.setSelection(0, len(s))

    def set_entry_focus(self):
        # Remember the widget that had focus, changing headline widgets
        # to the tree pane widget.  Headline widgets can disappear!
        c = self.c
        w = g.app.gui.get_focus(raw=True)
        if w != c.frame.body.wrapper.widget:
            w = c.frame.tree.treeWidget
        self.entry_focus = w

    #@+node:ekr.20150619082825.1: *3* ftm.set_ignore_case
    def set_ignore_case(self, aBool):
        """Set the ignore-case checkbox to the given value."""
        c = self.c
        c.findCommands.ignore_case = aBool
        w = self.check_box_ignore_case
        w.setChecked(aBool)
    #@+node:ekr.20131117120458.16789: *3* ftm.init_widgets (creates callbacks)
    def init_widgets(self):
        """
        Init widgets and ivars from c.config settings.
        Create callbacks that always keep the LeoFind ivars up to date.
        """
        c = self.c
        find = c.findCommands
        # Find/change text boxes.
        table = (
            ('find_findbox', 'find_text', '<find pattern here>'),
            ('find_replacebox', 'change_text', ''),
        )
        for ivar, setting_name, default in table:
            s = c.config.getString(setting_name) or default
            w = getattr(self, ivar)
            w.insert(s)
            if find.minibuffer_mode:
                w.clearFocus()
            else:
                w.setSelection(0, len(s))
        # Check boxes.
        table = (
            ('ignore_case', self.check_box_ignore_case),
            ('mark_changes', self.check_box_mark_changes),
            ('mark_finds', self.check_box_mark_finds),
            ('pattern_match', self.check_box_regexp),
            ('search_body', self.check_box_search_body),
            ('search_headline', self.check_box_search_headline),
            ('whole_word', self.check_box_whole_word),
            ('wrap', self.check_box_wrap_around),
        )
        for setting_name, w in table:
            val = c.config.getBool(setting_name, default=False)
            # The setting name is also the name of the LeoFind ivar.
            assert hasattr(find, setting_name), setting_name
            setattr(find, setting_name, val)
            if val:
                w.toggle()

            def check_box_callback(n, setting_name=setting_name, w=w):
                # The focus has already change when this gets called.
                # focus_w = QtWidgets.QApplication.focusWidget()
                val = w.isChecked()
                assert hasattr(find, setting_name), setting_name
                setattr(find, setting_name, val)
                # Too kludgy: we must use an accurate setting.
                # It would be good to have an "about to change" signal.
                # Put focus in minibuffer if minibuffer find is in effect.
                c.bodyWantsFocusNow()

            w.stateChanged.connect(check_box_callback)
        # Radio buttons
        table = (
            ('node_only', 'node_only', self.radio_button_node_only),
            ('entire_outline', None, self.radio_button_entire_outline),
            ('suboutline_only', 'suboutline_only', self.radio_button_suboutline_only),
        )
        for setting_name, ivar, w in table:
            val = c.config.getBool(setting_name, default=False)
            # The setting name is also the name of the LeoFind ivar.
            if ivar is not None:
                assert hasattr(find, setting_name), setting_name
                setattr(find, setting_name, val)
                w.toggle()

            def radio_button_callback(n, ivar=ivar, setting_name=setting_name, w=w):
                val = w.isChecked()
                find.radioButtonsChanged = True
                if ivar:
                    assert hasattr(find, ivar), ivar
                    setattr(find, ivar, val)

            w.toggled.connect(radio_button_callback)
        # Ensure one radio button is set.
        if not find.node_only and not find.suboutline_only:
            w = self.radio_button_entire_outline
            w.toggle()
    #@+node:ekr.20131117120458.16792: *3* ftm.set_radio_button
    def set_radio_button(self, name):
        """Set the value of the radio buttons"""
        c = self.c
        find = c.findCommands
        d = {
            # Name is not an ivar. Set by find.setFindScope... commands.
            'node-only': self.radio_button_node_only,
            'entire-outline': self.radio_button_entire_outline,
            'suboutline-only': self.radio_button_suboutline_only,
        }
        w = d.get(name)
        assert w
        # Most of the work will be done in the radio button callback.
        if not w.isChecked():
            w.toggle()
        if find.minibuffer_mode:
            find.showFindOptionsInStatusArea()
    #@+node:ekr.20131117120458.16791: *3* ftm.toggle_checkbox
    #@@nobeautify

    def toggle_checkbox(self,checkbox_name):
        """Toggle the value of the checkbox whose name is given."""
        c = self.c
        find = c.findCommands
        if not find:
            return
        d = {
            'ignore_case':     self.check_box_ignore_case,
            'mark_changes':    self.check_box_mark_changes,
            'mark_finds':      self.check_box_mark_finds,
            'pattern_match':   self.check_box_regexp,
            'search_body':     self.check_box_search_body,
            'search_headline': self.check_box_search_headline,
            'whole_word':      self.check_box_whole_word,
            'wrap':            self.check_box_wrap_around,
        }
        w = d.get(checkbox_name)
        assert w
        assert hasattr(find,checkbox_name),checkbox_name
        w.toggle() # The checkbox callback toggles the ivar.
        if find.minibuffer_mode:
            find.showFindOptionsInStatusArea()
    #@-others
#@+node:ekr.20131115120119.17376: ** class LeoBaseTabWidget(QTabWidget)
class LeoBaseTabWidget(QtWidgets.QTabWidget):
    """Base class for all QTabWidgets in Leo."""
    #@+others
    #@+node:ekr.20131115120119.17390: *3* qt_base_tab.__init__
    def __init__(self, *args, **kwargs):
        
        #
        # Called from frameFactory.createMaster.
        #
        self.factory = kwargs.get('factory')
        if self.factory:
            del kwargs['factory']
        super().__init__(*args, **kwargs)
        self.detached = []
        self.setMovable(True)

        def tabContextMenu(point):
            index = self.tabBar().tabAt(point)
            if index < 0: # or (self.count() < 1 and not self.detached):
                return
            menu = QtWidgets.QMenu()
            # #310: Create new file on right-click in file tab in UI.
            if True:
                a = menu.addAction("New Outline")
                a.triggered.connect(lambda checked: self.new_outline(index))
            if self.count() > 1:
                a = menu.addAction("Detach")
                a.triggered.connect(lambda checked: self.detach(index))
                a = menu.addAction("Horizontal tile")
                a.triggered.connect(
                    lambda checked: self.tile(index, orientation='H'))
                a = menu.addAction("Vertical tile")
                a.triggered.connect(
                    lambda checked: self.tile(index, orientation='V'))
            if self.detached:
                a = menu.addAction("Re-attach All")
                a.triggered.connect(lambda checked: self.reattach_all())
            menu.exec_(self.mapToGlobal(point))

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(tabContextMenu)
    #@+node:ekr.20180123082452.1: *3* qt_base_tab.new_outline
    def new_outline(self, index):
        """Open a new outline tab."""
        w = self.widget(index)
        c = w.leo_c
        c.new()
    #@+node:ekr.20131115120119.17391: *3* qt_base_tab.detach
    def detach(self, index):
        """detach tab (from tab's context menu)"""
        w = self.widget(index)
        name = self.tabText(index)
        self.detached.append((name, w))
        self.factory.detachTab(w)
        icon = g.app.gui.getImageFinder("application-x-leo-outline.png")
        icon = QtGui.QIcon(icon)
        if icon:
            w.window().setWindowIcon(icon)
        c = w.leo_c
        if c.styleSheetManager:
            c.styleSheetManager.set_style_sheets(w=w)
        if platform.system() == 'Windows':
            w.move(20, 20)
                # Windows (XP and 7) put the windows title bar off screen.
        return w
    #@+node:ekr.20131115120119.17392: *3* qt_base_tab.tile
    def tile(self, index, orientation='V'):
        """detach tab and tile with parent window"""
        w = self.widget(index)
        window = w.window()
        # window.showMaximized()
        # this doesn't happen until we've returned to main even loop
        # user needs to do it before using this function
        fg = window.frameGeometry()
        geom = window.geometry()
        x, y, fw, fh = fg.x(), fg.y(), fg.width(), fg.height()
        ww, wh = geom.width(), geom.height()
        w = self.detach(index)
        if window.isMaximized():
            window.showNormal()
        if orientation == 'V':
            # follow MS Windows convention for which way is horizontal/vertical
            window.resize(ww / 2, wh)
            window.move(x, y)
            w.resize(ww / 2, wh)
            w.move(x + fw / 2, y)
        else:
            window.resize(ww, wh / 2)
            window.move(x, y)
            w.resize(ww, wh / 2)
            w.move(x, y + fh / 2)
    #@+node:ekr.20131115120119.17393: *3* qt_base_tab.reattach_all
    def reattach_all(self):
        """reattach all detached tabs"""
        for name, w in self.detached:
            self.addTab(w, name)
            self.factory.leoFrames[w] = w.leo_c.frame
        self.detached = []
    #@+node:ekr.20131115120119.17394: *3* qt_base_tab.delete
    def delete(self, w):
        """called by TabbedFrameFactory to tell us a detached tab
        has been deleted"""
        self.detached = [i for i in self.detached if i[1] != w]
    #@+node:ekr.20131115120119.17395: *3* qt_base_tab.setChanged (changed)
    def setChanged(self, c, changed):
        """Set the changed indicator in c's tab."""
        # Find the tab corresponding to c.
        dw = c.frame.top # A DynamicWindow
        i = self.indexOf(dw)
        if i < 0: return
        s = self.tabText(i)
        if len(s) > 2:
            if changed:
                if not s.startswith('* '):
                    title = "* " + s
                    self.setTabText(i, title)
            else:
                if s.startswith('* '):
                    title = s[2:]
                    self.setTabText(i, title)
    #@+node:ekr.20131115120119.17396: *3* qt_base_tab.setTabName
    def setTabName(self, c, fileName):
        """Set the tab name for c's tab to fileName."""
        # Find the tab corresponding to c.
        dw = c.frame.top # A DynamicWindow
        i = self.indexOf(dw)
        if i > -1:
            self.setTabText(i, g.shortFileName(fileName))
    #@+node:ekr.20131115120119.17397: *3* qt_base_tab.closeEvent (changed)
    def closeEvent(self, event):
        """Handle a close event."""
        g.app.gui.close_event(event)
    #@+node:ekr.20131115120119.17398: *3* qt_base_tab.select (leoTabbedTopLevel)
    def select(self, c):
        """Select the tab for c."""
        dw = c.frame.top # A DynamicWindow
        i = self.indexOf(dw)
        self.setCurrentIndex(i)
        # Fix bug 844953: tell Unity which menu to use.
            # c.enableMenuBar()
    #@-others
#@+node:ekr.20110605121601.18180: ** class LeoQtBody(leoFrame.LeoBody)
class LeoQtBody(leoFrame.LeoBody):
    """A class that represents the body pane of a Qt window."""
    #@+others
    #@+node:ekr.20150521061618.1: *3* LeoQtBody.cmd (decorator)
    def cmd(name):
        """Command decorator for the c.frame.body class."""
        # pylint: disable=no-self-argument
        return g.new_cmd_decorator(name, ['c', 'frame', 'body'])
    #@+node:ekr.20110605121601.18181: *3* LeoQtBody.Birth
    #@+node:ekr.20110605121601.18182: *4* LeoQtBody.ctor
    def __init__(self, frame, parentFrame):
        """Ctor for LeoQtBody class."""
        # Call the base class constructor.
        super().__init__(frame, parentFrame)
        c = self.c
        assert c.frame == frame and frame.c == c
        self.reloadSettings()
        self.set_widget()
            # Sets self.widget and self.wrapper.
        self.setWrap(c.p)
        # For multiple body editors.
        self.editor_name = None
        self.editor_v = None
        self.numberOfEditors = 1
        self.totalNumberOfEditors = 1
        # For renderer panes.
        self.canvasRenderer = None
        self.canvasRendererLabel = None
        self.canvasRendererVisible = False
        self.textRenderer = None
        self.textRendererLabel = None
        self.textRendererVisible = False
        self.textRendererWrapper = None
    #@+node:ekr.20110605121601.18185: *5* LeoQtBody.get_name
    def getName(self):
        return 'body-widget'
    #@+node:ekr.20140901062324.18562: *5* LeoQtBody.reloadSettings
    def reloadSettings(self):
        c = self.c
        self.useScintilla = c.config.getBool('qt-use-scintilla')
        self.use_chapters = c.config.getBool('use-chapters')
        self.use_gutter = c.config.getBool('use-gutter', default=False)
    #@+node:ekr.20160309074124.1: *5* LeoQtBody.set_invisibles
    def set_invisibles(self, c):
        """Set the show-invisibles bit in the document."""
        d = c.frame.body.wrapper.widget.document()
        option = QtGui.QTextOption()
        if c.frame.body.colorizer.showInvisibles:
            option.setFlags(QtGui.QTextOption.ShowTabsAndSpaces)
        d.setDefaultTextOption(option)
    #@+node:ekr.20140901062324.18563: *5* LeoQtBody.set_widget
    def set_widget(self):
        """Set the actual gui widget."""
        c = self.c
        top = c.frame.top
        sw = getattr(top, 'stackedWidget', None)
        if sw:
            sw.setCurrentIndex(1)
        if self.useScintilla and not Qsci:
            g.trace('Can not import Qsci: ignoring @bool qt-use-scintilla')
        if self.useScintilla and Qsci:
            self.widget = c.frame.top.scintilla_widget
                # A Qsci.QsciSintilla object.
                # dw.createText sets self.scintilla_widget
            self.wrapper = qt_text.QScintillaWrapper(self.widget, name='body', c=c)
            self.colorizer = leoColorizer.QScintillaColorizer(c, self.widget, self.wrapper)
        else:
            self.widget = top.richTextEdit # A LeoQTextBrowser
            self.wrapper = qt_text.QTextEditWrapper(self.widget, name='body', c=c)
            self.widget.setAcceptRichText(False)
            self.colorizer = leoColorizer.make_colorizer(c, self.widget, self.wrapper)
    #@+node:ekr.20110605121601.18183: *5* LeoQtBody.setWrap
    def setWrap(self, p=None, force=False):
        """Set **only** the wrap bits in the body."""
        if not p or self.useScintilla:
            return
        c = self.c
        w = c.frame.body.wrapper.widget
        option, qt = QtGui.QTextOption, QtCore.Qt
        if force:
            wrap = option.WrapAtWordBoundaryOrAnywhere
        else:
            wrap = g.scanAllAtWrapDirectives(c, p)
            w.setHorizontalScrollBarPolicy(
                qt.ScrollBarAlwaysOff if wrap else qt.ScrollBarAsNeeded)
            wrap = option.WrapAtWordBoundaryOrAnywhere if wrap else option.NoWrap
                # was option WordWrap
        w.setWordWrapMode(wrap)
    #@+node:ekr.20110605121601.18193: *3* LeoQtBody.Editors
    #@+node:ekr.20110605121601.18194: *4* LeoQtBody.entries
    #@+node:ekr.20110605121601.18195: *5* LeoQtBody.add_editor_command
    # An override of leoFrame.addEditor.
    @cmd('editor-add')
    @cmd('add-editor')
    def add_editor_command(self, event=None):
        """Add another editor to the body pane."""
        c, p = self.c, self.c.p
        dw = c.frame.top
        d = self.editorWidgets
        wrapper = c.frame.body.wrapper # A QTextEditWrapper
        widget = wrapper.widget
        self.totalNumberOfEditors += 1
        self.numberOfEditors += 1
        if self.totalNumberOfEditors == 2:
            self.editorWidgets['1'] = wrapper
            # Pack the original body editor.
            # Fix #1021: Pack differently depending on whether the gutter exists.
            if self.use_gutter:
                dw.packLabel(widget.parent(), n=1)
                widget.leo_label = widget.parent().leo_label
            else:
                dw.packLabel(widget, n=1)
        name = f"{self.totalNumberOfEditors}"
        f, wrapper = dw.addNewEditor(name)
        assert g.isTextWrapper(wrapper), wrapper
        assert g.isTextWidget(widget), widget
        assert isinstance(f, (QtWidgets.QFrame, QtWidgets.QDockWidget)), f
        d[name] = wrapper
        if self.numberOfEditors == 2:
            # Inject the ivars into the first editor.
            # The name of the last editor need not be '1'
            d = self.editorWidgets
            keys = list(d.keys())
            old_name = keys[0]
            old_wrapper = d.get(old_name)
            old_w = old_wrapper.widget
            self.injectIvars(f, old_name, p, old_wrapper)
            self.updateInjectedIvars(old_w, p)
            self.selectLabel(old_wrapper) # Immediately create the label in the old editor.
        # Switch editors.
        c.frame.body.wrapper = wrapper
        self.selectLabel(wrapper)
        self.selectEditor(wrapper)
        self.updateEditors()
        c.bodyWantsFocus()
    #@+node:ekr.20110605121601.18197: *5* LeoQtBody.assignPositionToEditor
    def assignPositionToEditor(self, p):
        """Called *only* from tree.select to select the present body editor."""
        c = self.c
        wrapper = c.frame.body.wrapper
        w = wrapper and wrapper.widget
            # Careful: w may not exist during unit testing.
        if w:
            self.updateInjectedIvars(w, p)
            self.selectLabel(wrapper)
    #@+node:ekr.20110605121601.18198: *5* LeoQtBody.cycleEditorFocus
    # Use the base class method.
    #@+node:ekr.20110605121601.18199: *5* LeoQtBody.delete_editor_command
    @cmd('delete-editor')
    @cmd('editor-delete')
    def delete_editor_command(self, event=None, dock=None):
        """Delete the presently selected body text editor."""
        c, d = self.c, self.editorWidgets
        dw = c.frame.top
        wrapper = c.frame.body.wrapper
        w = wrapper.widget
        assert g.isTextWrapper(wrapper), wrapper
        assert g.isTextWidget(w), w
        # Fix bug 228: make *sure* the old text is saved.
        c.p.b = wrapper.getAllText()
        if not g.app.dock:
            #@+<< legacy delete_editor_command >>
            #@+node:ekr.20190527072132.1: *6* << legacy delete_editor_command >>
            name = getattr(w, 'leo_name', None)
            if len(list(d.keys())) <= 1 or name == '1':
                g.warning('can not delete main editor')
                return
            #
            # Actually delete the widget.
            del d[name]
            f = c.frame.top.leo_body_frame
            layout = f.layout()
            for z in (w, w.leo_label):
                if z:
                    self.unpackWidget(layout, z)
            #
            # Select another editor.
            new_wrapper = list(d.values())[0]
            self.numberOfEditors -= 1
            if self.numberOfEditors == 1:
                w = new_wrapper.widget
                label = getattr(w, 'leo_label', None)
                if label:
                    self.unpackWidget(layout, label)
            w.leo_label = None
            self.selectEditor(new_wrapper)
            #@-<< legacy delete_editor_command >>
            return
        #
        # Sanity checks.
        if not dock:
            dock = w.parent().parent()
            if (getattr(w, 'leo_name', None) == '1' or
                not isinstance(dock, QtWidgets.QDockWidget)
            ):
                g.warning('can not delete main editor')
                return
        #
        # Actually delete the widget.
        if dock in dw.leo_docks:
            dw.leo_docks.remove(dock)
        dw.removeDockWidget(dock)
            # A QMainWidget method.
        #
        # Select another editor.
        w.leo_label = None
        new_wrapper = list(d.values())[0]
        self.numberOfEditors -= 1
        self.selectEditor(new_wrapper)
    #@+node:ekr.20110605121601.18200: *5* LeoQtBody.findEditorForChapter
    def findEditorForChapter(self, chapter, p):
        """Return an editor to be assigned to chapter."""
        c = self.c; d = self.editorWidgets
        values = list(d.values())
        # First, try to match both the chapter and position.
        if p:
            for w in values:
                if (
                    hasattr(w, 'leo_chapter') and w.leo_chapter == chapter and
                    hasattr(w, 'leo_p') and w.leo_p and w.leo_p == p
                ):
                    return w
        # Next, try to match just the chapter.
        for w in values:
            if hasattr(w, 'leo_chapter') and w.leo_chapter == chapter:
                return w
        # As a last resort, return the present editor widget.
        return c.frame.body.wrapper
    #@+node:ekr.20110605121601.18201: *5* LeoQtBody.select/unselectLabel
    def unselectLabel(self, wrapper):
        # pylint: disable=arguments-differ
        pass
        # self.createChapterIvar(wrapper)

    def selectLabel(self, wrapper):
        # pylint: disable=arguments-differ
        c = self.c
        w = wrapper.widget
        lab = hasattr(w, 'leo_label') and w.leo_label
        if lab:
            lab.setEnabled(True)
            lab.setText(c.p.h)
            lab.setEnabled(False)
    #@+node:ekr.20110605121601.18202: *5* LeoQtBody.selectEditor & helpers
    selectEditorLockout = False

    def selectEditor(self, wrapper):
        """Select editor w and node w.leo_p."""
        # pylint: disable=arguments-differ
        c = self.c
        if not wrapper:
            return c.frame.body.wrapper
        if self.selectEditorLockout:
            return None
        w = wrapper.widget
        assert g.isTextWrapper(wrapper), wrapper
        assert g.isTextWidget(w), w

        def report(s):
            g.trace('*** %9s wrapper %s w %s %s' % (
                s, id(wrapper), id(w), c.p.h))

        if wrapper and wrapper == c.frame.body.wrapper:
            self.deactivateEditors(wrapper)
            if hasattr(w, 'leo_p') and w.leo_p and w.leo_p != c.p:
                c.selectPosition(w.leo_p)
                c.bodyWantsFocus()
            return None
        try:
            val = None
            self.selectEditorLockout = True
            val = self.selectEditorHelper(wrapper)
        finally:
            self.selectEditorLockout = False
        return val # Don't put a return in a finally clause.
    #@+node:ekr.20110605121601.18203: *6* LeoQtBody.selectEditorHelper
    def selectEditorHelper(self, wrapper):

        c = self.c
        w = wrapper.widget
        assert g.isTextWrapper(wrapper), wrapper
        assert g.isTextWidget(w), w
        if not w.leo_p:
            g.trace('no w.leo_p')
            return 'break'
        # The actual switch.
        self.deactivateEditors(wrapper)
        self.recolorWidget(w.leo_p, wrapper) # switches colorizers.
        c.frame.body.wrapper = wrapper
        # 2014/09/04: Must set both wrapper.widget and body.widget.
        c.frame.body.wrapper.widget = w
        c.frame.body.widget = w
        w.leo_active = True
        self.switchToChapter(wrapper)
        self.selectLabel(wrapper)
        if not self.ensurePositionExists(w):
            return g.trace('***** no position editor!')
        if not (hasattr(w, 'leo_p') and w.leo_p):
            g.trace('***** no w.leo_p', w)
            return None
        p = w.leo_p
        assert p, p
        c.expandAllAncestors(p)
        c.selectPosition(p)
            # Calls assignPositionToEditor.
            # Calls p.v.restoreCursorAndScroll.
        c.redraw()
        c.recolor()
        c.bodyWantsFocus()
        return None
    #@+node:ekr.20110605121601.18205: *5* LeoQtBody.updateEditors
    # Called from addEditor and assignPositionToEditor

    def updateEditors(self):
        c = self.c; p = c.p; body = p.b
        d = self.editorWidgets
        if len(list(d.keys())) < 2: return # There is only the main widget
        w0 = c.frame.body.wrapper
        i, j = w0.getSelectionRange()
        ins = w0.getInsertPoint()
        sb0 = w0.widget.verticalScrollBar()
        pos0 = sb0.sliderPosition()
        for key in d:
            wrapper = d.get(key)
            w = wrapper.widget
            v = hasattr(w, 'leo_p') and w.leo_p.v
            if v and v == p.v and w != w0:
                sb = w.verticalScrollBar()
                pos = sb.sliderPosition()
                wrapper.setAllText(body)
                self.recolorWidget(p, wrapper)
                sb.setSliderPosition(pos)
        c.bodyWantsFocus()
        w0.setSelectionRange(i, j, insert=ins)
        sb0.setSliderPosition(pos0)
    #@+node:ekr.20110605121601.18206: *4* LeoQtBody.utils
    #@+node:ekr.20110605121601.18207: *5* LeoQtBody.computeLabel
    def computeLabel(self, w):
        if hasattr(w, 'leo_label') and w.leo_label: # 2011/11/12
            s = w.leo_label.text()
        else:
            s = ''
        if hasattr(w, 'leo_chapter') and w.leo_chapter:
            s = f"{w.leo_chapter}: {s}"
        return s
    #@+node:ekr.20110605121601.18208: *5* LeoQtBody.createChapterIvar
    def createChapterIvar(self, w):
        c = self.c; cc = c.chapterController
        if hasattr(w, 'leo_chapter') and w.leo_chapter:
            pass
        elif cc and self.use_chapters:
            w.leo_chapter = cc.getSelectedChapter()
        else:
            w.leo_chapter = None
    #@+node:ekr.20110605121601.18209: *5* LeoQtBody.deactivateEditors
    def deactivateEditors(self, wrapper):
        """Deactivate all editors except wrapper's editor."""
        d = self.editorWidgets
        # Don't capture ivars here! assignPositionToEditor keeps them up-to-date. (??)
        for key in d:
            wrapper2 = d.get(key)
            w2 = wrapper2.widget
            if hasattr(w2, 'leo_active'):
                active = w2.leo_active
            else:
                active = True
            if wrapper2 != wrapper and active:
                w2.leo_active = False
                self.unselectLabel(wrapper2)
                self.onFocusOut(w2)
    #@+node:ekr.20110605121601.18210: *5* LeoQtBody.ensurePositionExists
    def ensurePositionExists(self, w):
        """Return True if w.leo_p exists or can be reconstituted."""
        c = self.c
        if c.positionExists(w.leo_p):
            return True
        for p2 in c.all_unique_positions():
            if p2.v and p2.v == w.leo_p.v:
                w.leo_p = p2.copy()
                return True
        # This *can* happen when selecting a deleted node.
        w.leo_p = c.p.copy()
        return False
    #@+node:ekr.20110605121601.18211: *5* LeoQtBody.injectIvars
    def injectIvars(self, parentFrame, name, p, wrapper):

        w = wrapper.widget
        assert g.isTextWrapper(wrapper), wrapper
        assert g.isTextWidget(w), w
        # Inject ivars
        if name == '1':
            w.leo_p = None # Will be set when the second editor is created.
        else:
            w.leo_p = p and p.copy()
        w.leo_active = True
        w.leo_bodyBar = None
        w.leo_bodyXBar = None
        w.leo_chapter = None
        # w.leo_colorizer = None # Set in JEditColorizer ctor.
        w.leo_frame = parentFrame
        # w.leo_label = None # Injected by packLabel.
        w.leo_name = name
        w.leo_wrapper = wrapper
    #@+node:ekr.20110605121601.18213: *5* LeoQtBody.recolorWidget (QScintilla only)
    def recolorWidget(self, p, wrapper):
        """Support QScintillaColorizer.colorize."""
        # pylint: disable=arguments-differ
        c = self.c
        colorizer = c.frame.body.colorizer
        if p and colorizer and hasattr(colorizer, 'colorize'):
            g.trace('=====', hasattr(colorizer, 'colorize'), p.h, g.callers())
            old_wrapper = c.frame.body.wrapper
            c.frame.body.wrapper = wrapper
            try:
                colorizer.colorize(p)
            finally:
                # Restore.
                c.frame.body.wrapper = old_wrapper
    #@+node:ekr.20110605121601.18214: *5* LeoQtBody.switchToChapter
    def switchToChapter(self, w):
        """select w.leo_chapter."""
        c = self.c; cc = c.chapterController
        if hasattr(w, 'leo_chapter') and w.leo_chapter:
            chapter = w.leo_chapter
            name = chapter and chapter.name
            oldChapter = cc.getSelectedChapter()
            if chapter != oldChapter:
                cc.selectChapterByName(name)
                c.bodyWantsFocus()
    #@+node:ekr.20110605121601.18216: *5* LeoQtBody.unpackWidget
    def unpackWidget(self, layout, w):

        index = layout.indexOf(w)
        if index == -1:
            return
        item = layout.itemAt(index)
        if item:
            item.setGeometry(QtCore.QRect(0, 0, 0, 0))
            layout.removeItem(item)
    #@+node:ekr.20110605121601.18215: *5* LeoQtBody.updateInjectedIvars
    def updateInjectedIvars(self, w, p):

        c = self.c
        cc = c.chapterController
        assert g.isTextWidget(w), w
        if cc and self.use_chapters:
            w.leo_chapter = cc.getSelectedChapter()
        else:
            w.leo_chapter = None
        w.leo_p = p.copy()
    #@+node:ekr.20110605121601.18223: *3* LeoQtBody.Event handlers
    #@+node:ekr.20110930174206.15472: *4* LeoQtBody.onFocusIn
    def onFocusIn(self, obj):
        """Handle a focus-in event in the body pane."""
        # Update history only in leoframe.tree.select.
        # c.nodeHistory.update(c.p)
        if obj.objectName() == 'richTextEdit':
            wrapper = hasattr(obj, 'leo_wrapper') and obj.leo_wrapper
            if wrapper and wrapper != self.wrapper:
                self.selectEditor(wrapper)
            self.onFocusColorHelper('focus-in', obj)
            if hasattr(obj, 'leo_copy_button') and obj.leo_copy_button:
                obj.setReadOnly(True)
            else:
                obj.setReadOnly(False)
            obj.setFocus() # Weird, but apparently necessary.
    #@+node:ekr.20110930174206.15473: *4* LeoQtBody.onFocusOut
    def onFocusOut(self, obj):
        """Handle a focus-out event in the body pane."""
        # Apparently benign.
        if obj.objectName() == 'richTextEdit':
            self.onFocusColorHelper('focus-out', obj)
            obj.setReadOnly(True)
    #@+node:ekr.20110605121601.18224: *4* LeoQtBody.qtBody.onFocusColorHelper (revised)
    # badFocusColors = []

    def onFocusColorHelper(self, kind, obj):
        """Handle changes of style when focus changes."""
        c, vc = self.c, self.c.vimCommands
        if vc and c.vim_mode:
            try:
                assert kind in ('focus-in', 'focus-out')
                w = c.frame.body.wrapper.widget
                vc.set_border(w=w, activeFlag=kind == 'focus-in')
            except Exception:
                # g.es_exception()
                pass
    #@+node:ekr.20110605121601.18217: *3* LeoQtBody.Renderer panes
    #@+node:ekr.20110605121601.18218: *4* LeoQtBody.hideCanvasRenderer
    def hideCanvasRenderer(self, event=None):
        """Hide canvas pane."""
        c = self.c; d = self.editorWidgets
        wrapper = c.frame.body.wrapper
        w = wrapper.widget
        name = w.leo_name
        assert name
        assert wrapper == d.get(name), 'wrong wrapper'
        assert g.isTextWrapper(wrapper), wrapper
        assert g.isTextWidget(w), w
        if len(list(d.keys())) <= 1: return
        #
        # At present, can not delete the first column.
        if name == '1':
            g.warning('can not delete leftmost editor')
            return
        #
        # Actually delete the widget.
        del d[name]
        f = c.frame.top.leo_body_inner_frame
        layout = f.layout()
        for z in (w, w.leo_label):
            if z:
                self.unpackWidget(layout, z)
        #
        # Select another editor.
        w.leo_label = None
        new_wrapper = list(d.values())[0]
        self.numberOfEditors -= 1
        if self.numberOfEditors == 1:
            w = new_wrapper.widget
            if w.leo_label: # 2011/11/12
                self.unpackWidget(layout, w.leo_label)
                w.leo_label = None # 2011/11/12
        self.selectEditor(new_wrapper)
    #@+node:ekr.20110605121601.18219: *4* LeoQtBody.hideTextRenderer
    def hideCanvas(self, event=None):
        """Hide canvas pane."""
        c = self.c; d = self.editorWidgets
        wrapper = c.frame.body.wrapper
        w = wrapper.widget
        name = w.leo_name
        assert name
        assert wrapper == d.get(name), 'wrong wrapper'
        assert g.isTextWrapper(wrapper), wrapper
        assert g.isTextWidget(w), w
        if len(list(d.keys())) <= 1: return
        # At present, can not delete the first column.
        if name == '1':
            g.warning('can not delete leftmost editor')
            return
        #
        # Actually delete the widget.
        del d[name]
        f = c.frame.top.leo_body_inner_frame
        layout = f.layout()
        for z in (w, w.leo_label):
            if z:
                self.unpackWidget(layout, z)
        #
        # Select another editor.
        w.leo_label = None
        new_wrapper = list(d.values())[0]
        self.numberOfEditors -= 1
        if self.numberOfEditors == 1:
            w = new_wrapper.widget
            if w.leo_label:
                self.unpackWidget(layout, w.leo_label)
                w.leo_label = None
        self.selectEditor(new_wrapper)
    #@+node:ekr.20110605121601.18220: *4* LeoQtBody.packRenderer
    def packRenderer(self, f, name, w):
        n = max(1, self.numberOfEditors)
        assert isinstance(f, QtWidgets.QFrame), f
        layout = f.layout()
        f.setObjectName(f"{name} Frame")
        # Create the text: to do: use stylesheet to set font, height.
        lab = QtWidgets.QLineEdit(f)
        lab.setObjectName(f"{name} Label")
        lab.setText(name)
        # Pack the label and the widget.
        layout.addWidget(lab, 0, max(0, n - 1), QtCore.Qt.AlignVCenter)
        layout.addWidget(w, 1, max(0, n - 1))
        layout.setRowStretch(0, 0)
        layout.setRowStretch(1, 1) # Give row 1 as much as possible.
        return lab
    #@+node:ekr.20110605121601.18221: *4* LeoQtBody.showCanvasRenderer
    # An override of leoFrame.addEditor.

    def showCanvasRenderer(self, event=None):
        """Show the canvas area in the body pane, creating it if necessary."""
        c = self.c
        f = c.frame.top.leo_body_inner_frame
        assert isinstance(f, QtWidgets.QFrame), f
        if not self.canvasRenderer:
            name = 'Graphics Renderer'
            self.canvasRenderer = w = QtWidgets.QGraphicsView(f)
            w.setObjectName(name)
        if not self.canvasRendererVisible:
            self.canvasRendererLabel = self.packRenderer(f, name, w)
            self.canvasRendererVisible = True
    #@+node:ekr.20110605121601.18222: *4* LeoQtBody.showTextRenderer
    # An override of leoFrame.addEditor.

    def showTextRenderer(self, event=None):
        """Show the canvas area in the body pane, creating it if necessary."""
        c = self.c
        f = c.frame.top.leo_body_inner_frame
        assert isinstance(f, QtWidgets.QFrame), f
        if not self.textRenderer:
            name = 'Text Renderer'
            self.textRenderer = w = qt_text.LeoQTextBrowser(f, c, self)
            w.setObjectName(name)
            self.textRendererWrapper = qt_text.QTextEditWrapper(
                w, name='text-renderer', c=c)
        if not self.textRendererVisible:
            self.textRendererLabel = self.packRenderer(f, name, w)
            self.textRendererVisible = True
    #@-others
#@+node:ekr.20110605121601.18245: ** class LeoQtFrame (leoFrame)
class LeoQtFrame(leoFrame.LeoFrame):
    """A class that represents a Leo window rendered in qt."""
    #@+others
    #@+node:ekr.20110605121601.18246: *3*  qtFrame.Birth & Death
    #@+node:ekr.20110605121601.18247: *4* qtFrame.__init__ & reloadSettings
    def __init__(self, c, title, gui):

        super().__init__(c, gui)
        assert self.c == c
        leoFrame.LeoFrame.instances += 1 # Increment the class var.
        # Official ivars...
        self.iconBar = None
        self.iconBarClass = self.QtIconBarClass
        self.initComplete = False # Set by initCompleteHint().
        self.minibufferVisible = True
        self.statusLineClass = self.QtStatusLineClass
        self.title = title
        self.setIvars()
        self.reloadSettings()
        
    def reloadSettings(self):
        c = self.c
        self.cursorStay = c.config.getBool("cursor-stay-on-paste", default=True)
        self.use_chapters = c.config.getBool('use-chapters')
        self.use_chapter_tabs = c.config.getBool('use-chapter-tabs')
    #@+node:ekr.20110605121601.18248: *5* qtFrame.setIvars
    def setIvars(self):
        # "Official ivars created in createLeoFrame and its allies.
        self.bar1 = None
        self.bar2 = None
        self.body = None
        self.f1 = self.f2 = None
        self.findPanel = None # Inited when first opened.
        self.iconBarComponentName = 'iconBar'
        self.iconFrame = None
        self.log = None
        self.canvas = None
        self.outerFrame = None
        self.statusFrame = None
        self.statusLineComponentName = 'statusLine'
        self.statusText = None
        self.statusLabel = None
        self.top = None # This will be a class Window object.
        self.tree = None
        # Used by event handlers...
        self.controlKeyIsDown = False # For control-drags
        self.isActive = True
        self.redrawCount = 0
        self.wantedWidget = None
        self.wantedCallbackScheduled = False
        self.scrollWay = None
    #@+node:ekr.20110605121601.18249: *4* qtFrame.__repr__
    def __repr__(self):
        return f"<LeoQtFrame: {self.title}>"
    #@+node:ekr.20150509040227.1: *4* qtFrame.cmd (decorator)
    def cmd(name):
        """Command decorator for the LeoQtFrame class."""
        # pylint: disable=no-self-argument
        return g.new_cmd_decorator(name, ['c', 'frame',])
    #@+node:ekr.20110605121601.18250: *4* qtFrame.finishCreate & helpers (changed)
    def finishCreate(self):
        """Finish creating the outline's frame."""
        # Called from app.newCommander, Commands.__init__
        c = self.c
        assert c
        frameFactory = g.app.gui.frameFactory
        if not frameFactory.masterFrame:
            frameFactory.createMaster()
            if g.app.use_global_docks:
                dock = g.app.gui.outlines_dock
                dock.setWidget(frameFactory.masterFrame)
        self.top = frameFactory.createFrame(leoFrame=self)
        self.createIconBar() # A base class method.
        self.createSplitterComponents()
        self.createStatusLine() # A base class method.
        self.createFirstTreeNode() # Call the base-class method.
        self.menu = LeoQtMenu(c, self, label='top-level-menu')
        g.app.windowList.append(self)
        self.miniBufferWidget = qt_text.QMinibufferWrapper(c)
        c.bodyWantsFocus()
    #@+node:ekr.20110605121601.18251: *5* qtFrame.createSplitterComponents
    def createSplitterComponents(self):
        
        c = self.c
        self.tree = qt_tree.LeoQtTree(c, self)
        self.log = LeoQtLog(self, None)
        self.body = LeoQtBody(self, None)
        if g.app.dock:
            return 
        self.splitVerticalFlag, ratio, secondary_ratio = self.initialRatios()
        self.resizePanesToRatio(ratio, secondary_ratio)

    #@+node:ekr.20190412044556.1: *5* qtFrame.setQtStyle
    def setQtStyle(self):
        """
        Set the default Qt style.  Based on pyzo code.
        
        Copyright (C) 2013-2018, the Pyzo development team

        Pyzo is distributed under the terms of the (new) BSD License.
        The full license can be found in 'license.txt'.
        """
        c = self.c
        #
        # Get the requested style name.
        stylename = c.config.getString('qt-style-name') or ''
        if not stylename:
            return
        #
        # Return if the style does not exist.
        styles = [z.lower() for z in QtWidgets.QStyleFactory.keys()]
        if stylename.lower() not in styles:
            g.es_print('ignoring unknown Qt style name: %r' % stylename)
            return
        #
        # Change the style and palette.
        QtWidgets.qApp.nativePalette = QtWidgets.qApp.palette()
        qstyle = QtWidgets.qApp.setStyle(stylename)
        if not qstyle:
            g.es_print('failed to set Qt style name: %r' % stylename)
            return
        g.app.gui.qtApp.setPalette(QtWidgets.qApp.nativePalette)
        # g.es_print('set qt style: %r' % stylename)
    #@+node:ekr.20110605121601.18252: *4* qtFrame.initCompleteHint
    def initCompleteHint(self):
        """A kludge: called to enable text changed events."""
        self.initComplete = True

    #@+node:ekr.20110605121601.18253: *4* Destroying the qtFrame
    #@+node:ekr.20110605121601.18254: *5* qtFrame.destroyAllObjects (not used)
    def destroyAllObjects(self):
        """Clear all links to objects in a Leo window."""
        frame = self; c = self.c
        # g.printGcAll()
        # Do this first.
        #@+<< clear all vnodes in the tree >>
        #@+node:ekr.20110605121601.18255: *6* << clear all vnodes in the tree>> (qtFrame)
        vList = [z for z in c.all_unique_nodes()]
        for v in vList:
            g.clearAllIvars(v)
        vList = [] # Remove these references immediately.
        #@-<< clear all vnodes in the tree >>
        if 1:
            # Destroy all ivars in subcommanders.
            g.clearAllIvars(c.atFileCommands)
            if c.chapterController: # New in Leo 4.4.3 b1.
                g.clearAllIvars(c.chapterController)
            g.clearAllIvars(c.fileCommands)
            g.clearAllIvars(c.keyHandler) # New in Leo 4.4.3 b1.
            g.clearAllIvars(c.importCommands)
            g.clearAllIvars(c.tangleCommands)
            g.clearAllIvars(c.undoer)
            g.clearAllIvars(c)
        if 0: # No need.
            tree = frame.tree; body = self.body
            g.clearAllIvars(body.colorizer)
            g.clearAllIvars(body)
            g.clearAllIvars(tree)
    #@+node:ekr.20110605121601.18256: *5* qtFrame.destroySelf
    def destroySelf(self):
        # Remember these: we are about to destroy all of our ivars!
        c, top = self.c, self.top
        if hasattr(g.app.gui, 'frameFactory'):
            g.app.gui.frameFactory.deleteFrame(top)
        # Indicate that the commander is no longer valid.
        c.exists = False
        if 0: # We can't do this unless we unhook the event filter.
            # Destroys all the objects of the commander.
            self.destroyAllObjects()
        c.exists = False # Make sure this one ivar has not been destroyed.
        # print('destroySelf: qtFrame: %s' % c,g.callers(4))
        top.close()
    #@+node:ekr.20110605121601.18257: *3* qtFrame.class QtStatusLineClass
    class QtStatusLineClass:
        """A class representing the status line."""
        #@+others
        #@+node:ekr.20110605121601.18258: *4* QtStatusLineClass.ctor
        def __init__(self, c, parentFrame):
            """Ctor for LeoQtFrame class."""
            self.c = c
            self.statusBar = c.frame.top.statusBar
            self.lastFcol = 0
            self.lastRow = 0
            self.lastCol = 0
            # Create the text widgets.
            self.textWidget1 = w1 = QtWidgets.QLineEdit(self.statusBar)
            self.textWidget2 = w2 = QtWidgets.QLineEdit(self.statusBar)
            w1.setObjectName('status1')
            w2.setObjectName('status2')
            w1.setReadOnly(True)
            w2.setReadOnly(True)
            splitter = QtWidgets.QSplitter()
            self.statusBar.addWidget(splitter, True)
            sizes = c.config.getString('status-line-split-sizes') or '1 2'
            sizes = [int(i) for i in sizes.replace(',', ' ').split()]
            # pylint: disable=consider-using-ternary
            for n, i in enumerate(sizes):
                w = [w1, w2][n]
                policy = w.sizePolicy()
                policy.setHorizontalStretch(i)
                policy.setHorizontalPolicy(policy.Minimum)
                w.setSizePolicy(policy)
            splitter.addWidget(w1)
            splitter.addWidget(w2)
            c.status_line_unl_mode = 'original'

            def cycle_unl_mode():
                if c.status_line_unl_mode == 'original':
                    c.status_line_unl_mode = 'canonical'
                else:
                    c.status_line_unl_mode = 'original'
                verbose = c.status_line_unl_mode == 'canonical'
                w2.setText(c.p.get_UNL(with_proto=verbose, with_index=verbose))

            def add_item(event, w2=w2):
                menu = w2.createStandardContextMenu()
                menu.addSeparator()
                menu.addAction("Toggle UNL mode", cycle_unl_mode)
                menu.exec_(event.globalPos())

            w2.contextMenuEvent = add_item
            self.put('')
            self.update()
        #@+node:ekr.20110605121601.18260: *4* QtStatusLineClass.clear, get & put/1
        def clear(self):
            self.put('')

        def get(self):
            return self.textWidget2.text()

        def put(self, s, bg=None, fg=None):
            self.put_helper(s, self.textWidget2, bg, fg)

        def put1(self, s, bg=None, fg=None):
            self.put_helper(s, self.textWidget1, bg, fg)

        styleSheetCache = {}
            # Keys are widgets, values are stylesheets.

        def put_helper(self, s, w, bg=None, fg=None):
            """Put string s in the indicated widget, with proper colors."""
            c = self.c
            bg = bg or c.config.getColor('status-bg') or 'white'
            fg = fg or c.config.getColor('status-fg') or 'black'
            if True:
                # Work around #804. w is a QLineEdit.
                w.setStyleSheet('background: %s; color: %s;' % (bg, fg))
            else:
                # Rather than put(msg, explicit_color, explicit_color) we should use
                # put(msg, status) where status is None, 'info', or 'fail'.
                # Just as a quick hack to avoid dealing with propagating those changes
                # back upstream, infer status like this:
                if (fg == c.config.getColor('find-found-fg') and
                    bg == c.config.getColor('find-found-bg')
                ):
                    status = 'info'
                elif (fg == c.config.getColor('find-not-found-fg') and
                    bg == c.config.getColor('find-not-found-bg')
                ):
                    status = 'fail'
                else:
                    status = None
                d = self.styleSheetCache
                if status != d.get(w, '__undefined__'):
                    d[w] = status
                    c.styleSheetManager.mng.remove_sclass(w, ['info', 'fail'])
                    c.styleSheetManager.mng.add_sclass(w, status)
                    c.styleSheetManager.mng.update_view(w)  # force appearance update
            w.setText(s)
        #@+node:chris.20180320072817.1: *4* QtStatusLineClass.update & helpers
        def update(self):
            if g.app.killed: return
            c, body = self.c, self.c.frame.body
            if not c.p:
                return
            te = body.widget
            if not isinstance(te, QtWidgets.QTextEdit):
                return
            cursor = te.textCursor()
            block = cursor.block()
            row = block.blockNumber() + 1
            col, fcol = self.compute_columns(block, cursor)
            words = len(c.p.b.split(None))
            self.put_status_line(col, fcol, row, words)
            self.lastRow = row
            self.lastCol = col
            self.lastFcol = fcol
        #@+node:ekr.20190118082646.1: *5* qstatus.compute_columns
        def compute_columns(self, block, cursor):
            
            c = self.c
            line = block.text()
            col = cursor.columnNumber()
            offset = c.p.textOffset()
            fcol_offset = 0
            s2 = line[0: col]
            col = g.computeWidth(s2, c.tab_width)
            #
            # #195: fcol when using @first directive is inaccurate
            i = line.find('<<')
            j = line.find('>>')
            if -1 < i < j or g.match_word(line.strip(), 0, '@others'):
                offset = None
            else:
                for tag in ('@first ', '@last '):
                    if line.startswith(tag):
                        fcol_offset = len(tag)
                        break
            #
            # fcol is '' if there is no ancestor @<file> node.
            fcol = None if offset is None else max(0, col + offset - fcol_offset)
            return col, fcol
        #@+node:chris.20180320072817.2: *5* qstatus.file_line (not used)
        def file_line(self):
            """
            Return the line of the first line of c.p in its external file.
            Return None if c.p is not part of an external file.
            """
            c, p = self.c, self.c.p
            if p:
                goto = gotoCommands.GoToCommands(c)
                return goto.find_node_start(p)
            return None
        #@+node:ekr.20190118082047.1: *5* qstatus.put_status_line
        def put_status_line(self, col, fcol, row, words):
            
            if 1:
                fcol_part = '' if fcol is None else f" fcol: {fcol}"
                # For now, it seems to0 difficult to get alignment *exactly* right.
                self.put1("line: %d col: %d %s words: %s" % (row, col, fcol_part, words))
            else:
                # #283 is not ready yet, and probably will never be.
                fline = self.file_line()
                fline = '' if fline is None else fline + row
                self.put1(
                    "fline: %2s line: %2d col: %2s fcol: %2s" % (fline, row, col, fcol))
        #@-others
    #@+node:ekr.20110605121601.18262: *3* qtFrame.class QtIconBarClass
    class QtIconBarClass:
        """A class representing the singleton Icon bar"""
        #@+others
        #@+node:ekr.20110605121601.18263: *4*  ctor & reloadSettings (QtIconBarClass)
        def __init__(self, c, parentFrame):
            """Ctor for QtIconBarClass."""
            # Copy ivars
            self.c = c
            self.parentFrame = parentFrame
            # Status ivars.
            self.actions = []
            self.chapterController = None
            self.toolbar = self
            self.w = c.frame.top.iconBar # A QToolBar.
            self.reloadSettings()

        def reloadSettings(self):
            c = self.c
            c.registerReloadSettings(self)
            self.buttonColor = c.config.getString('qt-button-color')
            self.toolbar_orientation = c.config.getString('qt-toolbar-location')
        #@+node:ekr.20110605121601.18264: *4*  do-nothings (QtIconBarClass)
        # These *are* called from Leo's core.

        def addRow(self, height=None):
            pass # To do.

        def getNewFrame(self):
            return None # To do
        #@+node:ekr.20110605121601.18265: *4* add (QtIconBarClass)
        def add(self, *args, **keys):
            """Add a button to the icon bar."""
            c = self.c
            if not self.w:
                return None
            command = keys.get('command')
            text = keys.get('text')
            # able to specify low-level QAction directly (QPushButton not forced)
            qaction = keys.get('qaction')
            if not text and not qaction:
                g.es('bad toolbar item')
            kind = keys.get('kind') or 'generic-button'
            # imagefile = keys.get('imagefile')
            # image = keys.get('image')

            class leoIconBarButton(QtWidgets.QWidgetAction):

                def __init__(self, parent, text, toolbar):
                    super().__init__(parent)
                    self.button = None # set below
                    self.text = text
                    self.toolbar = toolbar

                def createWidget(self, parent):
                    self.button = b = QtWidgets.QPushButton(self.text, parent)
                    self.button.setProperty('button_kind', kind) # for styling
                    return b

            if qaction is None:
                action = leoIconBarButton(parent=self.w, text=text, toolbar=self)
                button_name = text
            else:
                action = qaction
                button_name = action.text()
            self.w.addAction(action)
            self.actions.append(action)
            b = self.w.widgetForAction(action)
            # Set the button's object name so we can use the stylesheet to color it.
            if not button_name: button_name = 'unnamed'
            button_name = button_name + '-button'
            b.setObjectName(button_name)
            b.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)

            def delete_callback(checked, action=action,):
                self.w.removeAction(action)

            b.leo_removeAction = rb = QtWidgets.QAction('Remove Button', b)
            b.addAction(rb)
            rb.triggered.connect(delete_callback)
            if command:

                def button_callback(event, c=c, command=command):
                    val = command()
                    if c.exists:
                        # c.bodyWantsFocus()
                        c.outerUpdate()
                    return val

                b.clicked.connect(button_callback)
            return action
        #@+node:ekr.20110605121601.18266: *4* addRowIfNeeded
        def addRowIfNeeded(self):
            """Add a new icon row if there are too many widgets."""
            # n = g.app.iconWidgetCount
            # if n >= self.widgets_per_row:
                # g.app.iconWidgetCount = 0
                # self.addRow()
            # g.app.iconWidgetCount += 1
        #@+node:ekr.20110605121601.18267: *4* addWidget
        def addWidget(self, w):
            self.w.addWidget(w)
        #@+node:ekr.20110605121601.18268: *4* clear (QtIconBarClass)
        def clear(self):
            """Destroy all the widgets in the icon bar"""
            self.w.clear()
            self.actions = []
            g.app.iconWidgetCount = 0
        #@+node:ekr.20110605121601.18269: *4* createChaptersIcon
        def createChaptersIcon(self):

            c = self.c
            f = c.frame
            if f.use_chapters and f.use_chapter_tabs:
                return LeoQtTreeTab(c, f.iconBar)
            return None
        #@+node:ekr.20110605121601.18270: *4* deleteButton
        def deleteButton(self, w):
            """ w is button """
            self.w.removeAction(w)
            self.c.bodyWantsFocus()
            self.c.outerUpdate()
        #@+node:ekr.20141031053508.14: *4* goto_command (QtIconBarClass)
        def goto_command(self, controller, gnx):
            """
            Select the node corresponding to the given gnx.
            controller is a ScriptingController instance.
            """
            # Fix bug 74: command_p may be in another outline.
            c = self.c
            c2, p = controller.open_gnx(c, gnx)
            if p:
                assert c2.positionExists(p)
                if c == c2:
                    c2.selectPosition(p)
                else:
                    # Fix #367: complete the selection at idle time.
                    g.app.selectLeoWindow(c2)

                    def handler(timer, c=c2, p=p):
                        c2.selectPosition(p)
                        timer.stop()

                    timer = g.IdleTime(handler, delay=0, tag='goto-script-button')
                    if timer: timer.start()
            else:
                g.trace('not found', gnx)
        #@+node:ekr.20110605121601.18271: *4* setCommandForButton (@rclick nodes) & helper
        # qtFrame.QtIconBarClass.setCommandForButton

        def setCommandForButton(self, button, command, command_p, controller, gnx, script):
            """
            Set the "Goto Script" rlick item of an @button button.
            Called from mod_scripting.py plugin.

            button is a leoIconBarButton.
            command is a callback, defined in mod_scripting.py.
            command_p exists only if the @button node exists in the local .leo file.
            gnx is the gnx of the @button node.
            script is a static script for common @button nodes.
            """
            if not command:
                return
            # Fix bug 74: use the controller and gnx arguments.
            b = button.button
            b.clicked.connect(command)

            def goto_callback(checked, controller=controller, gnx=gnx):
                self.goto_command(controller, gnx)

            b.goto_script = gts = QtWidgets.QAction('Goto Script', b)
            b.addAction(gts)
            gts.triggered.connect(goto_callback)
            rclicks = build_rclick_tree(command_p, top_level=True)
            self.add_rclick_menu(b, rclicks, controller, script=script)
        #@+node:ekr.20141031053508.15: *5* add_rclick_menu (QtIconBarClass)
        def add_rclick_menu(self, action_container, rclicks, controller,
            top_level=True,
            button=None,
            script=None
        ):
            c = controller.c
            top_offset = -2 # insert before the remove button and goto script items
            if top_level:
                button = action_container
            for rc in rclicks:
                # pylint: disable=cell-var-from-loop
                headline = rc.position.h[8:].strip()
                act = QtWidgets.QAction(headline, action_container)
                if '---' in headline and headline.strip().strip('-') == '':
                    act.setSeparator(True)
                elif rc.position.b.strip():

                    def cb(checked, p=rc.position, button=button):
                        controller.executeScriptFromButton(
                            b=button,
                            buttonText=p.h[8:].strip(),
                            p=p,
                            script=script,
                        )
                        if c.exists:
                            c.outerUpdate()

                    act.triggered.connect(cb)
                else: # recurse submenu
                    sub_menu = QtWidgets.QMenu(action_container)
                    act.setMenu(sub_menu)
                    self.add_rclick_menu(sub_menu, rc.children, controller,
                        top_level=False, button=button)
                if top_level:
                    # insert act before Remove Button
                    action_container.insertAction(
                        action_container.actions()[top_offset], act)
                else:
                    action_container.addAction(act)
            if top_level and rclicks:
                act = QtWidgets.QAction('---', action_container)
                act.setSeparator(True)
                action_container.insertAction(
                    action_container.actions()[top_offset], act)
                action_container.setText(
                    action_container.text() +
                    (c.config.getString('mod-scripting-subtext') or '')
                )
        #@-others
    #@+node:ekr.20110605121601.18274: *3* qtFrame.Configuration
    #@+node:ekr.20110605121601.18275: *4* qtFrame.configureBar
    def configureBar(self, bar, verticalFlag):
        c = self.c
        # Get configuration settings.
        w = c.config.getInt("split-bar-width")
        if not w or w < 1: w = 7
        relief = c.config.get("split_bar_relief", "relief")
        if not relief: relief = "flat"
        color = c.config.getColor("split-bar-color")
        if not color: color = "LightSteelBlue2"
        try:
            if verticalFlag:
                # Panes arranged vertically; horizontal splitter bar
                bar.configure(relief=relief, height=w, bg=color, cursor="sb_v_double_arrow")
            else:
                # Panes arranged horizontally; vertical splitter bar
                bar.configure(relief=relief, width=w, bg=color, cursor="sb_h_double_arrow")
        except Exception:
            # Could be a user error. Use all defaults
            g.es("exception in user configuration for splitbar")
            g.es_exception()
            if verticalFlag:
                # Panes arranged vertically; horizontal splitter bar
                bar.configure(height=7, cursor="sb_v_double_arrow")
            else:
                # Panes arranged horizontally; vertical splitter bar
                bar.configure(width=7, cursor="sb_h_double_arrow")
    #@+node:ekr.20110605121601.18276: *4* qtFrame.configureBarsFromConfig
    def configureBarsFromConfig(self):
        c = self.c
        w = c.config.getInt("split-bar-width")
        if not w or w < 1: w = 7
        relief = c.config.get("split_bar_relief", "relief")
        if not relief or relief == "": relief = "flat"
        color = c.config.getColor("split-bar-color")
        if not color or color == "": color = "LightSteelBlue2"
        if self.splitVerticalFlag:
            bar1, bar2 = self.bar1, self.bar2
        else:
            bar1, bar2 = self.bar2, self.bar1
        try:
            bar1.configure(relief=relief, height=w, bg=color)
            bar2.configure(relief=relief, width=w, bg=color)
        except Exception:
            # Could be a user error.
            g.es("exception in user configuration for splitbar")
            g.es_exception()
    #@+node:ekr.20110605121601.18277: *4* qtFrame.reconfigureFromConfig
    def reconfigureFromConfig(self):
        """Init the configuration of the Qt frame from settings."""
        c, frame = self.c, self
        frame.configureBarsFromConfig()
        frame.setTabWidth(c.tab_width)
        c.redraw()
    #@+node:ekr.20110605121601.18278: *4* qtFrame.setInitialWindowGeometry
    def setInitialWindowGeometry(self):
        """Set the position and size of the frame to config params."""
        c = self.c
        h = c.config.getInt("initial-window-height") or 500
        w = c.config.getInt("initial-window-width") or 600
        x = c.config.getInt("initial-window-left") or 50 # #1190: was 10
        y = c.config.getInt("initial-window-top") or 50 # #1190: was 10
        if h and w and x and y:
            if 'size' in g.app.debug:
                g.trace(w, h, x, y)
            self.setTopGeometry(w, h, x, y)
    #@+node:ekr.20110605121601.18279: *4* qtFrame.setTabWidth
    def setTabWidth(self, w):
        # A do-nothing because tab width is set automatically.
        # It *is* called from Leo's core.
        pass
    #@+node:ekr.20110605121601.18280: *4* qtFrame.setWrap
    def setWrap(self, p=None, force=False):
        return self.c.frame.body.setWrap(p, force)
    #@+node:ekr.20110605121601.18281: *4* qtFrame.reconfigurePanes
    def reconfigurePanes(self):
        c, f = self.c, self
        if f.splitVerticalFlag:
            r = c.config.getRatio("initial-vertical-ratio")
            if r is None or r < 0.0 or r > 1.0: r = 0.5
            r2 = c.config.getRatio("initial-vertical-secondary-ratio")
            if r2 is None or r2 < 0.0 or r2 > 1.0: r2 = 0.8
        else:
            r = c.config.getRatio("initial-horizontal-ratio")
            if r is None or r < 0.0 or r > 1.0: r = 0.3
            r2 = c.config.getRatio("initial-horizontal-secondary-ratio")
            if r2 is None or r2 < 0.0 or r2 > 1.0: r2 = 0.8
        f.resizePanesToRatio(r, r2)
    #@+node:ekr.20110605121601.18282: *4* qtFrame.resizePanesToRatio
    def resizePanesToRatio(self, ratio, ratio2):
        """Resize splitter1 and splitter2 using the given ratios."""
        # pylint: disable=arguments-differ
        self.divideLeoSplitter1(ratio)
        self.divideLeoSplitter2(ratio2)
    #@+node:ekr.20110605121601.18283: *4* qtFrame.divideLeoSplitter1/2
    def divideLeoSplitter1(self, frac):
        """Divide the main splitter."""
        layout = self.c and self.c.free_layout
        if not layout:
            return
        w = layout.get_main_splitter()
        if w:
            self.divideAnySplitter(frac, w)

    def divideLeoSplitter2(self, frac):
        """Divide the secondary splitter."""
        layout = self.c and self.c.free_layout
        if not layout:
            return
        w = layout.get_secondary_splitter()
        if w:
            self.divideAnySplitter(frac, w)
    #@+node:ekr.20110605121601.18284: *4* qtFrame.divideAnySplitter
    # This is the general-purpose placer for splitters.
    # It is the only general-purpose splitter code in Leo.

    def divideAnySplitter(self, frac, splitter):
        """Set the splitter sizes."""
        sizes = splitter.sizes()
        if len(sizes) != 2:
            g.trace(f"{len(sizes)} widget(s) in {id(splitter)}")
            return
        if frac > 1 or frac < 0:
            g.trace(f"split ratio [{frac}] out of range 0 <= frac <= 1")
            return
        s1, s2 = sizes
        s = s1 + s2
        s1 = int(s * frac + 0.5)
        s2 = s - s1
        # g.trace("%2d %2d %5.2f => %2d %2d" % (sizes[0], sizes[1], frac, s1, s2))
        splitter.setSizes([s1, s2])
    #@+node:ekr.20110605121601.18285: *3* qtFrame.Event handlers
    #@+node:ekr.20110605121601.18286: *4* qtFrame.OnCloseLeoEvent
    # Called from quit logic and when user closes the window.
    # Returns True if the close happened.

    def OnCloseLeoEvent(self):
        f = self; c = f.c
        if c.inCommand:
            c.requestCloseWindow = True
        else:
            g.app.closeLeoWindow(self)
    #@+node:ekr.20110605121601.18287: *4* qtFrame.OnControlKeyUp/Down
    def OnControlKeyDown(self, event=None):
        self.controlKeyIsDown = True

    def OnControlKeyUp(self, event=None):
        self.controlKeyIsDown = False
    #@+node:ekr.20110605121601.18290: *4* qtFrame.OnActivateTree
    def OnActivateTree(self, event=None):
        pass
    #@+node:ekr.20110605121601.18291: *4* qtFrame.OnBodyClick, OnBodyRClick (not used)
    # At present, these are not called,
    # but they could be called by LeoQTextBrowser.

    def OnBodyClick(self, event=None):
        g.trace()
        try:
            c = self.c; p = c.currentPosition()
            if g.doHook("bodyclick1", c=c, p=p, event=event):
                g.doHook("bodyclick2", c=c, p=p, event=event)
                return
            c.k.showStateAndMode(w=c.frame.body.wrapper)
            g.doHook("bodyclick2", c=c, p=p, event=event)
        except Exception:
            g.es_event_exception("bodyclick")

    def OnBodyRClick(self, event=None):
        try:
            c = self.c; p = c.currentPosition()
            if g.doHook("bodyrclick1", c=c, p=p, event=event):
                g.doHook("bodyrclick2", c=c, p=p, event=event)
                return
            c.k.showStateAndMode(w=c.frame.body.wrapper)
            g.doHook("bodyrclick2", c=c, p=p, event=event)
        except Exception:
            g.es_event_exception("iconrclick")
    #@+node:ekr.20110605121601.18292: *4* qtFrame.OnBodyDoubleClick (Events) (not used)
    # Not called

    def OnBodyDoubleClick(self, event=None):
        try:
            c = self.c; p = c.currentPosition()
            if event and not g.doHook("bodydclick1", c=c, p=p, event=event):
                c.editCommands.extendToWord(event) # Handles unicode properly.
                c.k.showStateAndMode(w=c.frame.body.wrapper)
            g.doHook("bodydclick2", c=c, p=p, event=event)
        except Exception:
            g.es_event_exception("bodydclick")
        return "break" # Restore this to handle proper double-click logic.
    #@+node:ekr.20110605121601.18293: *3* qtFrame.Gui-dependent commands
    #@+node:ekr.20110605121601.18301: *4* qtFrame.Window Menu...
    #@+node:ekr.20110605121601.18302: *5* qtFrame.toggleActivePane
    @cmd('toggle-active-pane')
    def toggleActivePane(self, event=None):
        """Toggle the focus between the outline and body panes."""
        frame = self; c = frame.c
        w = c.get_focus()
        w_name = g.app.gui.widget_name(w)
        if w_name in ('canvas', 'tree', 'treeWidget'):
            c.endEditing()
            c.bodyWantsFocus()
        else:
            c.treeWantsFocus()
    #@+node:ekr.20110605121601.18303: *5* qtFrame.cascade
    @cmd('cascade-windows')
    def cascade(self, event=None):
        """Cascade all Leo windows."""
        x, y, delta = 50, 50, 50
        for frame in g.app.windowList:
            w = frame and frame.top
            if w:
                r = w.geometry() # a Qt.Rect
                # 2011/10/26: Fix bug 823601: cascade-windows fails.
                w.setGeometry(QtCore.QRect(x, y, r.width(), r.height()))
                # Compute the new offsets.
                x += 30; y += 30
                if x > 200:
                    x = 10 + delta; y = 40 + delta
                    delta += 10
    #@+node:ekr.20110605121601.18304: *5* qtFrame.equalSizedPanes
    @cmd('equal-sized-panes')
    def equalSizedPanes(self, event=None):
        """Make the outline and body panes have the same size."""
        self.resizePanesToRatio(0.5, self.secondary_ratio)
    #@+node:ekr.20110605121601.18305: *5* qtFrame.hideLogWindow
    def hideLogWindow(self, event=None):
        """Hide the log pane."""
        self.divideLeoSplitter2(0.99)
    #@+node:ekr.20110605121601.18306: *5* qtFrame.minimizeAll
    @cmd('minimize-all')
    def minimizeAll(self, event=None):
        """Minimize all Leo's windows."""
        for frame in g.app.windowList:
            self.minimize(frame)

    def minimize(self, frame):
        # This unit test will fail when run externally.
        if frame and frame.top:
            w = frame.top.leo_master or frame.top
            if g.unitTesting:
                g.app.unitTestDict['minimize-all'] = True
                assert hasattr(w, 'setWindowState'), w
            else:
                w.setWindowState(QtCore.Qt.WindowMinimized)
    #@+node:ekr.20110605121601.18307: *5* qtFrame.toggleSplitDirection
    @cmd('toggle-split-direction')
    def toggleSplitDirection(self, event=None):
        """
        Toggle the split direction in the present Leo window.
        
        This command does noting when --dock is in effect.
        """
        if g.app.dock:
            g.es('toggle-split-direction works only when')
            g.es('--no-dock is in effect')
            return
        if hasattr(self.c, 'free_layout'):
            self.c.free_layout.get_top_splitter().rotate()
    #@+node:ekr.20110605121601.18308: *5* qtFrame.resizeToScreen
    @cmd('resize-to-screen')
    def resizeToScreen(self, event=None):
        """Resize the Leo window so it fill the entire screen."""
        frame = self
        # This unit test will fail when run externally.
        if frame and frame.top:
            # frame.top.leo_master is a LeoTabbedTopLevel.
            # frame.top is a DynamicWindow.
            w = frame.top.leo_master or frame.top
            if g.unitTesting:
                g.app.unitTestDict['resize-to-screen'] = True
                assert hasattr(w, 'setWindowState'), w
            else:
                w.setWindowState(QtCore.Qt.WindowMaximized)
    #@+node:ekr.20110605121601.18309: *4* qtFrame.Help Menu...
    #@+node:ekr.20110605121601.18310: *5* qtFrame.leoHelp
    @cmd('open-offline-tutorial')
    def leoHelp(self, event=None):
        """Open Leo's offline tutorial."""
        frame = self; c = frame.c
        theFile = g.os_path_join(g.app.loadDir, "..", "doc", "sbooks.chm")
        if g.os_path_exists(theFile) and sys.platform.startswith('win'):
            # pylint: disable=no-member
            os.startfile(theFile)
        else:
            answer = g.app.gui.runAskYesNoDialog(c,
                "Download Tutorial?",
                "Download tutorial (sbooks.chm) from SourceForge?")
            if answer == "yes":
                try:
                    url = "http://prdownloads.sourceforge.net/leo/sbooks.chm?download"
                    import webbrowser
                    os.chdir(g.app.loadDir)
                    webbrowser.open_new(url)
                except Exception:
                    if 0:
                        g.es("exception downloading", "sbooks.chm")
                        g.es_exception()
    #@+node:ekr.20160424080647.1: *3* qtFrame.Properties
    # The ratio and secondary_ratio properties are read-only.
    #@+node:ekr.20160424080815.2: *4* qtFrame.ratio property
    def __get_ratio(self):
        """Return splitter ratio of the main splitter."""
        c = self.c
        free_layout = c.free_layout
        if free_layout:
            w = free_layout.get_main_splitter()
            if w:
                aList = w.sizes()
                if len(aList) == 2:
                    n1, n2 = aList
                    # 2017/06/07: guard against division by zero.
                    ratio = 0.5 if n1 + n2 == 0 else float(n1) / float(n1 + n2)
                    return ratio
        return 0.5

    ratio = property(
        __get_ratio, # No setter.
        doc="qtFrame.ratio property")
    #@+node:ekr.20160424080815.3: *4* qtFrame.secondary_ratio property
    def __get_secondary_ratio(self):
        """Return the splitter ratio of the secondary splitter."""
        c = self.c
        free_layout = c.free_layout
        if free_layout:
            w = free_layout.get_secondary_splitter()
            if w:
                aList = w.sizes()
                if len(aList) == 2:
                    n1, n2 = aList
                    ratio = float(n1) / float(n1 + n2)
                    return ratio
        return 0.5

    secondary_ratio = property(
        __get_secondary_ratio, # no setter.
        doc="qtFrame.secondary_ratio property")
    #@+node:ekr.20110605121601.18311: *3* qtFrame.Qt bindings...
    #@+node:ekr.20190611053431.1: *4* qtFrame.bringToFront
    def bringToFront(self):
        if 'size' in g.app.debug:
            g.trace()
        self.lift()

    #@+node:ekr.20190611053431.2: *4* qtFrame.deiconify
    def deiconify(self):
        """Undo --minimized"""
        if 'size' in g.app.debug:
            g.trace('top:', bool(self.top), 'isMinimized:', self.top and self.top.isMinimized())
        if self.top and self.top.isMinimized(): # Bug fix: 400739.
            self.lift()

    #@+node:ekr.20190611053431.4: *4* qtFrame.get_window_info (changed)
    def get_window_info(self):
        """Return the geometry of the top window."""
        if g.app.use_global_docks:
            f = g.app.gui.main_window
        elif getattr(self.top, 'leo_master', None):
            f = self.top.leo_master
        else:
            f = self.top
        rect = f.geometry()
        topLeft = rect.topLeft()
        x, y = topLeft.x(), topLeft.y()
        w, h = rect.width(), rect.height()
        if 'size' in g.app.debug:
            g.trace('\n', w, h, x, y)
        return w, h, x, y
    #@+node:ekr.20190611053431.3: *4* qtFrame.getFocus
    def getFocus(self):
        return g.app.gui.get_focus(self.c) # Bug fix: 2009/6/30.

    #@+node:ekr.20190611053431.7: *4* qtFrame.getTitle
    def getTitle(self):
        # Fix https://bugs.launchpad.net/leo-editor/+bug/1194209
        # For qt, leo_master (a LeoTabbedTopLevel) contains the QMainWindow.
        w = self.top.leo_master if g.app.qt_use_tabs else self.top
        return w.windowTitle()

    #@+node:ekr.20190611053431.5: *4* qtFrame.iconify
    def iconify(self):
        if 'size' in g.app.debug:
            g.trace(bool(self.top))
        if self.top: self.top.showMinimized()

    #@+node:ekr.20190611053431.6: *4* qtFrame.lift
    def lift(self):
        if 'size' in g.app.debug:
            g.trace(bool(self.top), self.top and self.top.isMinimized())
        if not self.top:
            return
        if self.top.isMinimized(): # Bug 379141
            self.top.showNormal()
        self.top.activateWindow()
        self.top.raise_()

    #@+node:ekr.20190611053431.8: *4* qtFrame.setTitle
    def setTitle(self, s):
        # pylint: disable=arguments-differ
        if self.top:
            # Fix https://bugs.launchpad.net/leo-editor/+bug/1194209
            # When using tabs, leo_master (a LeoTabbedTopLevel) contains the QMainWindow.
            w = self.top.leo_master if g.app.qt_use_tabs else self.top
            w.setWindowTitle(s)

    #@+node:ekr.20190611053431.9: *4* qtFrame.setTopGeometry
    def setTopGeometry(self, w, h, x, y):
        # self.top is a DynamicWindow.
        if 'size' in g.app.debug:
            g.trace(bool(self.top), w, h, x, y)
        if self.top:
            self.top.setGeometry(QtCore.QRect(x, y, w, h))
    #@+node:ekr.20190611053431.10: *4* qtFrame.update
    def update(self, *args, **keys):
        if 'size' in g.app.debug:
            g.trace(bool(self.top))
        self.top.update()
    #@-others
#@+node:ekr.20110605121601.18312: ** class LeoQtLog (LeoLog)
class LeoQtLog(leoFrame.LeoLog):
    """A class that represents the log pane of a Qt window."""
    #@+others
    #@+node:ekr.20150717102609.1: *3* LeoQtLog.cmd (decorator)
    def cmd(name):
        """Command decorator for the c.frame.log class."""
        # pylint: disable=no-self-argument
        return g.new_cmd_decorator(name, ['c', 'frame', 'log'])
    #@+node:ekr.20110605121601.18313: *3* LeoQtLog.Birth
    #@+node:ekr.20110605121601.18314: *4* LeoQtLog.__init__ & reloadSettings
    def __init__(self, frame, parentFrame):
        """Ctor for LeoQtLog class."""
        super().__init__(frame, parentFrame)
            # Calls createControl.
        assert self.logCtrl is None, self.logCtrl # Set in finishCreate.
            # Important: depeding on the log *tab*,
            # logCtrl may be either a wrapper or a widget.
        self.c = c = frame.c
            # Also set in the base constructor, but we need it here.
        self.contentsDict = {}
            # Keys are tab names.  Values are widgets.
        self.eventFilters = []
            # Apparently needed to make filters work!
        self.logDict = {}
            # Keys are tab names text widgets.  Values are the widgets.
        self.logWidget = None
            # Set in finishCreate.
        self.menu = None
            # A menu that pops up on right clicks in the hull or in tabs.
        self.tabWidget = tw = c.frame.top.tabWidget
            # The Qt.QTabWidget that holds all the tabs.
        #
        # Bug 917814: Switching Log Pane tabs is done incompletely.
        tw.currentChanged.connect(self.onCurrentChanged)
        if 0: # Not needed to make onActivateEvent work.
            # Works only for .tabWidget, *not* the individual tabs!
            theFilter = qt_events.LeoQtEventFilter(c, w=tw, tag='tabWidget')
            tw.installEventFilter(theFilter)
        #
        # 2013/11/15: Partial fix for bug 1251755: Log-pane refinements
        tw.setMovable(True)
        self.reloadSettings()
        
    def reloadSettings(self):
        c = self.c
        self.wrap = bool(c.config.getBool('log-pane-wraps'))
        
    #@+node:ekr.20110605121601.18315: *4* LeoQtLog.finishCreate
    def finishCreate(self):
        """Finish creating the LeoQtLog class."""
        c, log, w = self.c, self, self.tabWidget
        #
        # Create the log tab as the leftmost tab.
        log.createTab('Log')
        self.logWidget = logWidget = self.contentsDict.get('Log')
        option = QtGui.QTextOption
        logWidget.setWordWrapMode(option.WordWrap if self.wrap else option.NoWrap)
        w.insertTab(0, logWidget, 'Log')
            # Required.
        #
        # set up links in log handling
        logWidget.setTextInteractionFlags(
            QtCore.Qt.LinksAccessibleByMouse |
            QtCore.Qt.TextEditable |
            QtCore.Qt.TextSelectableByMouse
        )
        logWidget.setOpenLinks(False)
        logWidget.setOpenExternalLinks(False)
        logWidget.anchorClicked.connect(self.linkClicked)
        #
        # Show the spell tab.
        c.spellCommands.openSpellTab()
        #
        #794: Clicking Find Tab should do exactly what pushing Ctrl-F does
        
        def tab_callback(index):
            name = w.tabText(index)
            if name == 'Find':
                c.findCommands.startSearch(event=None)

        w.currentChanged.connect(tab_callback)
    #@+node:ekr.20110605121601.18316: *4* LeoQtLog.getName
    def getName(self):
        return 'log' # Required for proper pane bindings.
    #@+node:ekr.20150717102728.1: *3* LeoQtLog.Commands
    @cmd('clear-log')
    def clearLog(self, event=None):
        """Clear the log pane."""
        w = self.logCtrl.widget # w is a QTextBrowser
        if w:
            w.clear()
    #@+node:ekr.20110605121601.18333: *3* LeoQtLog.color tab stuff
    def createColorPicker(self, tabName):
        g.warning('color picker not ready for qt')
    #@+node:ekr.20110605121601.18334: *3* LeoQtLog.font tab stuff
    #@+node:ekr.20110605121601.18335: *4* LeoQtLog.createFontPicker
    def createFontPicker(self, tabName):
        # log = self
        QFont = QtGui.QFont
        font, ok = QtWidgets.QFontDialog.getFont()
        if not (font and ok): return
        style = font.style()
        table = (
            (QFont.StyleNormal, 'normal'),
            (QFont.StyleItalic, 'italic'),
            (QFont.StyleOblique, 'oblique'))
        for val, name in table:
            if style == val:
                style = name
                break
        else:
            style = ''
        weight = font.weight()
        table = (
            (QFont.Light, 'light'),
            (QFont.Normal, 'normal'),
            (QFont.DemiBold, 'demibold'),
            (QFont.Bold, 'bold'),
            (QFont.Black, 'black'))
        for val, name in table:
            if weight == val:
                weight = name
                break
        else:
            weight = ''
        table = (
            ('family', str(font.family())),
            ('size  ', font.pointSize()),
            ('style ', style),
            ('weight', weight),
        )
        for key, val in table:
            if val: g.es(key, val, tabName='Fonts')
    #@+node:ekr.20110605121601.18339: *4* LeoQtLog.hideFontTab
    def hideFontTab(self, event=None):
        c = self.c
        c.frame.log.selectTab('Log')
        c.bodyWantsFocus()
    #@+node:ekr.20111120124732.10184: *3* LeoQtLog.isLogWidget
    def isLogWidget(self, w):
        val = w == self or w in list(self.contentsDict.values())
        return val
    #@+node:tbnorth.20171220123648.1: *3* LeoQtLog.linkClicked
    def linkClicked(self, link):
        """linkClicked - link clicked in log

        :param QUrl link: link that was clicked
        """
        # see addition of '/' in LeoQtLog.put()
        url = s = g.toUnicode(link.toString())
        if platform.system() == 'Windows':
            for scheme in 'file', 'unl':
                if s.startswith(scheme+':///') and s[len(scheme)+5] == ':':
                    url = s.replace(':///', '://', 1)
                    break
        g.handleUrl(url, c=self.c)
    #@+node:ekr.20120304214900.9940: *3* LeoQtLog.onCurrentChanged
    def onCurrentChanged(self, idx):

        tabw = self.tabWidget
        w = tabw.widget(idx)
        #
        # #917814: Switching Log Pane tabs is done incompletely
        wrapper = getattr(w, 'leo_log_wrapper', None)
        #
        # #1161: Don't change logs unless the wrapper is correct.
        if wrapper and isinstance(wrapper, qt_text.QTextEditWrapper):
            self.logCtrl = wrapper
    #@+node:ekr.20110605121601.18321: *3* LeoQtLog.put & putnl
    #@+node:ekr.20110605121601.18322: *4* LeoQtLog.put
    def put(self, s, color=None, tabName='Log', from_redirect=False, nodeLink=None):
        """
        Put s to the Qt Log widget, converting to html.
        All output to the log stream eventually comes here.

        The from_redirect keyword argument is no longer used.
        """
        c = self.c
        if g.app.quitting or not c or not c.exists:
            return
        # Note: g.actualColor does all color translation.
        if color:
            color = leoColor.getColor(color)
        if not color:
            # #788: First, fall back to 'log_black_color', not 'black.
            color = c.config.getColor('log-black-color')
            if not color:
                # Should never be necessary.
                color = 'black'
        self.selectTab(tabName or 'Log')
        # Must be done after the call to selectTab.
        wrapper = self.logCtrl
        if not isinstance(wrapper, qt_text.QTextEditWrapper):
            g.trace('BAD wrapper', wrapper.__class__.__name__)
            return
        w = wrapper.widget
        if not isinstance(w, QtWidgets.QTextEdit):
            g.trace('BAD widget', w.__class__.__name__)
            return
        sb = w.horizontalScrollBar()
        s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        # #884: Always convert leading blanks and tabs to &nbsp.
        n = len(s) - len(s.lstrip())
        if n > 0 and s.strip():
            s = '&nbsp;' * (n) + s[n:]
        if not self.wrap:
            # Convert all other blanks to &nbsp;
            s = s.replace(' ', '&nbsp;')
        s = s.replace('\n', '<br>')
            # The caller is responsible for newlines!
        s = '<font color="%s">%s</font>' % (color, s)
        if nodeLink:
            url = nodeLink
            for scheme in 'file', 'unl':
                # QUrl requires paths start with '/'
                if url.startswith(scheme+'://') and not url.startswith(scheme+':///'):
                    url = url.replace('://', ':///', 1)
            s = f'<a href="{url}" title="{nodeLink}">{s}</a>'
        w.insertHtml(s)
        w.moveCursor(QtGui.QTextCursor.End)
        sb.setSliderPosition(0) # Force the slider to the initial position.
        w.repaint() # Slow, but essential.
    #@+node:ekr.20110605121601.18323: *4* LeoQtLog.putnl
    def putnl(self, tabName='Log'):
        """Put a newline to the Qt log."""
        # 
        # This is not called normally.
        if g.app.quitting:
            return
        if tabName:
            self.selectTab(tabName)
        wrapper = self.logCtrl
        if not isinstance(wrapper, qt_text.QTextEditWrapper):
            g.trace('BAD wrapper', wrapper.__class__.__name__)
            return
        w = wrapper.widget
        if not isinstance(w, QtWidgets.QTextEdit):
            g.trace('BAD widget', w.__class__.__name__)
            return
        sb = w.horizontalScrollBar()
        pos = sb.sliderPosition()
        # Not needed!
            # contents = w.toHtml()
            # w.setHtml(contents + '\n')
        w.moveCursor(QtGui.QTextCursor.End)
        sb.setSliderPosition(pos)
        w.repaint() # Slow, but essential.
    #@+node:ekr.20150205181818.5: *4* LeoQtLog.scrollToEnd
    def scrollToEnd(self, tabName='Log'):
        """Scroll the log to the end."""
        if g.app.quitting:
            return
        if tabName:
            self.selectTab(tabName)
        w = self.logCtrl.widget
        if w:
            sb = w.horizontalScrollBar()
            pos = sb.sliderPosition()
            w.moveCursor(QtGui.QTextCursor.End)
            sb.setSliderPosition(pos)
            w.repaint() # Slow, but essential.
    #@+node:ekr.20120913110135.10613: *3* LeoQtLog.putImage
    #@+node:ekr.20110605121601.18324: *3* LeoQtLog.Tab
    #@+node:ekr.20110605121601.18325: *4* LeoQtLog.clearTab
    def clearTab(self, tabName, wrap='none'):
        w = self.logDict.get(tabName)
        if w:
            w.clear() # w is a QTextBrowser.
    #@+node:ekr.20110605121601.18326: *4* LeoQtLog.createTab
    def createTab(self, tabName, createText=True, widget=None, wrap='none'):
        """
        Create a new tab in tab widget
        if widget is None, Create a QTextBrowser,
        suitable for log functionality.
        """
        c = self.c
        # #1159: Raise dockwidget with focus to top of tabified dock.
        if g.app.dock and tabName in ('Find', 'Spell'):
            return None
        if widget is None:
            widget = qt_text.LeoQTextBrowser(parent=None, c=c, wrapper=self)
                # widget is subclass of QTextBrowser.
            contents = qt_text.QTextEditWrapper(widget=widget, name='log', c=c)
                # contents a wrapper.
            widget.leo_log_wrapper = contents
                # Inject an ivar into the QTextBrowser that points to the wrapper.
            option = QtGui.QTextOption
            widget.setWordWrapMode(option.WordWrap if self.wrap else option.NoWrap)
            widget.setReadOnly(False) # Allow edits.
            self.logDict[tabName] = widget
            if tabName == 'Log':
                self.logCtrl = contents
                widget.setObjectName('log-widget')
            # Set binding on all log pane widgets.
            g.app.gui.setFilter(c, widget, self, tag='log')
            self.contentsDict[tabName] = widget
            self.tabWidget.addTab(widget, tabName)
        else:
            # #1161: Don't set the wrapper unless it has the correct type.
            contents = widget
                # Unlike text widgets, contents is the actual widget.
            if isinstance(contents, qt_text.QTextEditWrapper):
                widget.leo_log_wrapper = widget
                    # The leo_log_wrapper is the widget itself.
            else:
                widget.leo_log_wrapper = None
                    # Tell the truth.
            g.app.gui.setFilter(c, widget, contents, 'tabWidget')
            self.contentsDict[tabName] = contents
            if g.app.dock and c.config.getBool('dockable-log-tabs', default=False):
                # #1154: Support docks in the Log pane.
                dw = c.frame.top
                dock = g.app.gui.create_dock_widget(
                    closeable=True, moveable=True, height=50, name=tabName) # was 100: #1339.
                        # #1207: all plugins docks should be closeable.
                dock.setWidget(contents)
                area = QtCore.Qt.RightDockWidgetArea
                dw.addDockWidget(area, dock)
            else:
                self.tabWidget.addTab(contents, tabName)
        return contents
    #@+node:ekr.20110605121601.18328: *4* LeoQtLog.deleteTab
    def deleteTab(self, tabName, force=False):
        """
        Delete the tab if it exists.  Otherwise do *nothing*.
        
        The spell code sets force=True if there is no spell dict.
        """
        c = self.c
        w = self.tabWidget
        if force and tabName != 'Spell':
            g.trace('can not force delete tab:', tabName)
            return 
        i = self.findTabIndex(tabName)
        if i is None:
            return
        w.removeTab(i)
        self.selectTab('Log')
        c.invalidateFocus()
        c.bodyWantsFocus()
    #@+node:ekr.20190603062456.1: *4* LeoQtLog.findTabIndex
    def findTabIndex(self, tabName):
        """Return the tab index for tabName, or None."""
        w = self.tabWidget
        for i in range(w.count()):
            if tabName == w.tabText(i):
                return i
        return None
    #@+node:ekr.20110605121601.18329: *4* LeoQtLog.hideTab
    def hideTab(self, tabName):
        self.selectTab('Log')
    #@+node:ekr.20111122080923.10185: *4* LeoQtLog.orderedTabNames
    def orderedTabNames(self, LeoLog=None): # Unused: LeoLog
        """Return a list of tab names in the order in which they appear in the QTabbedWidget."""
        w = self.tabWidget
        return [w.tabText(i) for i in range(w.count())]
    #@+node:ekr.20110605121601.18330: *4* LeoQtLog.numberOfVisibleTabs
    def numberOfVisibleTabs(self):
        return len([val for val in self.contentsDict.values() if val is not None])
            # **Note**: the base-class version of this uses frameDict.
    #@+node:ekr.20110605121601.18331: *4* LeoQtLog.selectTab & helpers
    def selectTab(self, tabName, createText=True, widget=None, wrap='none'):
        """Create the tab if necessary and make it active."""
        i = self.findTabIndex(tabName)
        if i is None:
            self.createTab(tabName, widget=widget, wrap=wrap)
            self.finishCreateTab(tabName)
        self.finishSelectTab(tabName)
    #@+node:ekr.20190603064815.1: *5* LeoQtLog.finishCreateTab
    def finishCreateTab(self, tabName):
        """Finish creating the given tab. Do not set focus!"""
        c = self.c
        # Special case for the Spell tab.
        if g.app.dock and tabName == 'Spell':
            return
        i = self.findTabIndex(tabName)
        if i is None:
            g.trace('Can not happen', tabName)
            self.tabName = None
            return
        # # #1161.
        if tabName == 'Log':
            wrapper = None
            widget = self.contentsDict.get('Log')
                # a qt_text.QTextEditWrapper
            if widget:
                wrapper = getattr(widget, 'leo_log_wrapper', None)
                if wrapper and isinstance(wrapper, qt_text.QTextEditWrapper):
                    self.logCtrl = wrapper
            if not wrapper: g.trace('NO LOG WRAPPER')
        if tabName == 'Find':
            # Do *not* set focus here!
            # #1254861: Ctrl-f doesn't ensure find input field visible.
            if c.config.getBool('auto-scroll-find-tab', default=True):
                # This is the cause of unwanted scrolling.
                findbox = c.findCommands.ftm.find_findbox
                if hasattr(widget, 'ensureWidgetVisible'):
                    widget.ensureWidgetVisible(findbox)
                else:
                    findbox.setFocus()
        if tabName == 'Spell':
            # Set a flag for the spell system.
            widget = self.tabWidget.widget(i)
            self.frameDict['Spell'] = widget
    #@+node:ekr.20190603064816.1: *5* LeoQtLog.finishSelectTab
    def finishSelectTab(self, tabName):
        """
        Select the proper tab, raising it's enclosing dock as needed.
        """
        # #1159: raise a parent QDockWidget.
        c, w = self.c, self.tabWidget
        #
        # Raise the dock.
        if g.app.dock:
            # Raise the proper dock.
            dw = c.frame.top
            tabName2 = 'tabs' if tabName in ('Completion', 'Log') else tabName
            ivar = '%s_dock' % tabName2.lower()
            dock = getattr(dw, ivar, None)
            if dock:
                dock.raise_()
        #
        # Special case for Spell tab.
        if tabName == 'Spell':
            return
        #
        # Select the proper tab, regardless of g.app.dock.
        i = self.findTabIndex(tabName)
        if i is None:
            g.trace('can not happen', tabName)
            self.tabName = None
            return
        w.setCurrentIndex(i)
        self.tabName = tabName
    #@-others
#@+node:ekr.20110605121601.18340: ** class LeoQtMenu (LeoMenu)
class LeoQtMenu(leoMenu.LeoMenu):
    
    # #1199: Supress menu items when g.app.dock is True.
    no_dock_only_menus = (
        'equal-sized-panes',
        'toggle-split-direction',
    )
    #@+others
    #@+node:ekr.20110605121601.18341: *3* LeoQtMenu.__init__
    def __init__(self, c, frame, label):
        """ctor for LeoQtMenu class."""
        assert frame
        assert frame.c
        super().__init__(frame)
        self.leo_menu_label = label.replace('&', '').lower()
        self.frame = frame
        self.c = c
        self.menuBar = c.frame.top.menuBar()
        assert self.menuBar is not None
        # Inject this dict into the commander.
        if not hasattr(c, 'menuAccels'):
            setattr(c, 'menuAccels', {})
        if 0:
            self.font = c.config.getFontFromParams(
                'menu_text_font_family', 'menu_text_font_size',
                'menu_text_font_slant', 'menu_text_font_weight',
                c.config.defaultMenuFontSize)
    #@+node:ekr.20120306130648.9848: *3* LeoQtMenu.__repr__
    def __repr__(self):
        return f"<LeoQtMenu: {self.leo_menu_label}>"

    __str__ = __repr__
    #@+node:ekr.20110605121601.18342: *3* LeoQtMenu.Tkinter menu bindings
    # See the Tk docs for what these routines are to do
    #@+node:ekr.20110605121601.18343: *4* LeoQtMenu.Methods with Tk spellings
    #@+node:ekr.20110605121601.18344: *5* LeoQtMenu.add_cascade
    def add_cascade(self, parent, label, menu, underline):
        """Wrapper for the Tkinter add_cascade menu method.

        Adds a submenu to the parent menu, or the menubar."""
        # menu and parent are a QtMenuWrappers, subclasses of  QMenu.
        n = underline
        if -1 < n < len(label):
            label = label[: n] + '&' + label[n:]
        menu.setTitle(label)
        if parent:
            parent.addMenu(menu) # QMenu.addMenu.
        else:
            self.menuBar.addMenu(menu)
        label = label.replace('&', '').lower()
        menu.leo_menu_label = label
        return menu
    #@+node:ekr.20110605121601.18345: *5* LeoQtMenu.add_command (Called by createMenuEntries)
    def add_command(self, **keys):
        """Wrapper for the Tkinter add_command menu method."""
        # pylint: disable=arguments-differ
        accel = keys.get('accelerator') or ''
        command = keys.get('command') or ''
        commandName = keys.get('commandName')
        #
        # #1199: Suppress equal-sized-panes and toggle-split-direction
        #        when g.app.dock is True.
        if (g.app.dock and commandName and
            commandName.replace('&','') in self.no_dock_only_menus
        ):
            return
        label = keys.get('label')
        n = keys.get('underline')
        if n is None: n = -1
        menu = keys.get('menu') or self
        if not label:
            return
        if -1 < n < len(label):
            label = label[: n] + '&' + label[n:]
        if accel:
            label = f'{label}\t{accel}'
        action = menu.addAction(label)
        # 2012/01/20: Inject the command name into the action
        # so that it can be enabled/disabled dynamically.
        action.leo_command_name = commandName
        if command:

            def qt_add_command_callback(checked, label=label, command=command):
                return command()

            action.triggered.connect(qt_add_command_callback)
    #@+node:ekr.20110605121601.18346: *5* LeoQtMenu.add_separator
    def add_separator(self, menu):
        """Wrapper for the Tkinter add_separator menu method."""
        if menu:
            action = menu.addSeparator()
            action.leo_menu_label = '*seperator*'
    #@+node:ekr.20110605121601.18347: *5* LeoQtMenu.delete
    def delete(self, menu, realItemName='<no name>'):
        """Wrapper for the Tkinter delete menu method."""
        # if menu:
            # return menu.delete(realItemName)
    #@+node:ekr.20110605121601.18348: *5* LeoQtMenu.delete_range
    def delete_range(self, menu, n1, n2):
        """Wrapper for the Tkinter delete menu method."""
        # Menu is a subclass of QMenu and LeoQtMenu.
        for z in menu.actions()[n1: n2]:
            menu.removeAction(z)
    #@+node:ekr.20110605121601.18349: *5* LeoQtMenu.destroy
    def destroy(self, menu):
        """Wrapper for the Tkinter destroy menu method."""
        # Fixed bug https://bugs.launchpad.net/leo-editor/+bug/1193870
        if menu:
            menu.menuBar.removeAction(menu.menuAction())
    #@+node:ekr.20110605121601.18350: *5* LeoQtMenu.index
    def index(self, label):
        """Return the index of the menu with the given label."""
        return 0
    #@+node:ekr.20110605121601.18351: *5* LeoQtMenu.insert
    def insert(self, menuName, position, label, command, underline=None):

        menu = self.getMenu(menuName)
        if menu and label:
            n = underline or 0
            if -1 > n > len(label):
                label = label[: n] + '&' + label[n:]
            action = menu.addAction(label)
            if command:

                def insert_callback(checked, label=label, command=command):
                    command()

                action.triggered.connect(insert_callback)
    #@+node:ekr.20110605121601.18352: *5* LeoQtMenu.insert_cascade
    def insert_cascade(self, parent, index, label, menu, underline):
        """Wrapper for the Tkinter insert_cascade menu method."""
        menu.setTitle(label)
        label.replace('&', '').lower()
        menu.leo_menu_label = label # was leo_label
        if parent:
            parent.addMenu(menu)
        else:
            self.menuBar.addMenu(menu)
        action = menu.menuAction()
        if action:
            action.leo_menu_label = label
        else:
            g.trace('no action for menu', label)
        return menu
    #@+node:ekr.20110605121601.18353: *5* LeoQtMenu.new_menu
    def new_menu(self, parent, tearoff=False, label=''): # label is for debugging.
        """Wrapper for the Tkinter new_menu menu method."""
        c, leoFrame = self.c, self.frame
        # Parent can be None, in which case it will be added to the menuBar.
        menu = QtMenuWrapper(c, leoFrame, parent, label)
        return menu
    #@+node:ekr.20110605121601.18354: *4* LeoQtMenu.Methods with other spellings
    #@+node:ekr.20110605121601.18355: *5* LeoQtMenu.clearAccel
    def clearAccel(self, menu, name):
        pass
        # if not menu:
            # return
        # realName = self.getRealMenuName(name)
        # realName = realName.replace("&","")
        # menu.entryconfig(realName,accelerator='')
    #@+node:ekr.20110605121601.18356: *5* LeoQtMenu.createMenuBar
    def createMenuBar(self, frame):
        """
        (LeoQtMenu) Create all top-level menus.
        The menuBar itself has already been created.
        """
        self.createMenusFromTables()
            # This is LeoMenu.createMenusFromTables.
    #@+node:ekr.20110605121601.18357: *5* LeoQtMenu.createOpenWithMenu
    def createOpenWithMenu(self, parent, label, index, amp_index):
        """
        Create the File:Open With submenu.

        This is called from LeoMenu.createOpenWithMenuFromTable.
        """
        # Use the existing Open With menu if possible.
        menu = self.getMenu('openwith')
        if not menu:
            menu = self.new_menu(parent, tearoff=False, label=label)
            menu.insert_cascade(parent, index,
                label, menu, underline=amp_index)
        return menu
    #@+node:ekr.20110605121601.18358: *5* LeoQtMenu.disable/enableMenu (not used)
    def disableMenu(self, menu, name):
        self.enableMenu(menu, name, False)

    def enableMenu(self, menu, name, val):
        """Enable or disable the item in the menu with the given name."""
        if menu and name:
            val = bool(val)
            for action in menu.actions():
                s = g.checkUnicode(action.text()).replace('&', '')
                if s.startswith(name):
                    action.setEnabled(val)
                    break
    #@+node:ekr.20110605121601.18359: *5* LeoQtMenu.getMenuLabel
    def getMenuLabel(self, menu, name):
        """Return the index of the menu item whose name (or offset) is given.
        Return None if there is no such menu item."""
        # At present, it is valid to always return None.
    #@+node:ekr.20110605121601.18360: *5* LeoQtMenu.setMenuLabel
    def setMenuLabel(self, menu, name, label, underline=-1):

        def munge(s):
            return (s or '').replace('&', '')

        # menu is a QtMenuWrapper.
        if not menu: return
        realName = munge(self.getRealMenuName(name))
        realLabel = self.getRealMenuName(label)
        for action in menu.actions():
            s = munge(action.text())
            s = s.split('\t')[0]
            if s == realName:
                action.setText(realLabel)
                break
    #@+node:ekr.20110605121601.18361: *3* LeoQtMenu.activateMenu & helper
    def activateMenu(self, menuName):
        """Activate the menu with the given name"""
        menu = self.getMenu(menuName)
            # Menu is a QtMenuWrapper, a subclass of both QMenu and LeoQtMenu.
        if menu:
            self.activateAllParentMenus(menu)
        else:
            g.trace(f"No such menu: {menuName}")
    #@+node:ekr.20120922041923.10607: *4* LeoQtMenu.activateAllParentMenus
    def activateAllParentMenus(self, menu):
        """menu is a QtMenuWrapper.  Activate it and all parent menus."""
        parent = menu.parent()
        action = menu.menuAction()
        if action:
            if parent and isinstance(parent, QtWidgets.QMenuBar):
                parent.setActiveAction(action)
            elif parent:
                self.activateAllParentMenus(parent)
                parent.setActiveAction(action)
            else:
                g.trace(f"can not happen: no parent for {menu}")
        else:
            g.trace(f"can not happen: no action for {menu}")
    #@+node:ekr.20120922041923.10613: *3* LeoQtMenu.deactivateMenuBar
    # def deactivateMenuBar (self):
        # """Activate the menu with the given name"""
        # menubar = self.c.frame.top.leo_menubar
        # menubar.setActiveAction(None)
        # menubar.repaint()
    #@+node:ekr.20110605121601.18362: *3* LeoQtMenu.getMacHelpMenu
    def getMacHelpMenu(self, table):
        return None
    #@-others
#@+node:ekr.20110605121601.18363: ** class LeoQTreeWidget (QTreeWidget)
class LeoQTreeWidget(QtWidgets.QTreeWidget):
    # To do: Generate @auto or @file nodes when appropriate.

    def __init__(self, c, parent):
        super().__init__(parent)
        self.setAcceptDrops(True)
        enable_drag = c.config.getBool('enable-tree-dragging')
        self.setDragEnabled(bool(enable_drag))
        self.c = c
        self.was_alt_drag = False
        self.was_control_drag = False

    def __repr__(self):
        return 'LeoQTreeWidget: %s' % id(self)

    __str__ = __repr__
    # This is called during drags.

    def dragMoveEvent(self, ev):
        pass
    #@+others
    #@+node:ekr.20111022222228.16980: *3* LeoQTreeWidget: Event handlers
    #@+node:ekr.20110605121601.18364: *4* LeoQTreeWidget.dragEnterEvent & helper
    def dragEnterEvent(self, ev):
        """Export c.p's tree as a Leo mime-data."""
        c = self.c
        if not ev:
            g.trace('no event!')
            return
        md = ev.mimeData()
        if not md:
            g.trace('No mimeData!')
            return
        c.endEditing()
        # Fix bug 135: cross-file drag and drop is broken.
        # This handler may be called several times for the same drag.
        # Only the first should should set g.app.drag_source.
        if g.app.dragging:
            pass
        else:
            g.app.dragging = True
            g.app.drag_source = c, c.p
            self.setText(md)
        # Always accept the drag, even if we are already dragging.
        ev.accept()
    #@+node:ekr.20110605121601.18384: *5* LeoQTreeWidget.setText
    def setText(self, md):
        c = self.c
        fn = self.fileName()
        s = c.fileCommands.putLeoOutline()
        md.setText(f"{fn},{s}")
    #@+node:ekr.20110605121601.18365: *4* LeoQTreeWidget.dropEvent & helpers
    def dropEvent(self, ev):
        """Handle a drop event in the QTreeWidget."""
        if not ev:
            return
        md = ev.mimeData()
        if not md:
            g.trace('no mimeData!')
            return
        mods = int(ev.keyboardModifiers())
        self.was_alt_drag = (mods & QtCore.Qt.AltModifier) != 0
        self.was_control_drag = (mods & QtCore.Qt.ControlModifier) != 0
        c, tree = self.c, self.c.frame.tree
        p = None
        item = self.itemAt(ev.pos())
        if item:
            itemHash = tree.itemHash(item)
            p = tree.item2positionDict.get(itemHash)
        if not p:
            # #59: Drop at last node.
            p = c.rootPosition()
            while p.hasNext():
                p.moveToNext()
        formats = set(str(f) for f in md.formats())
        ev.setDropAction(QtCore.Qt.IgnoreAction)
        ev.accept()
        hookres = g.doHook("outlinedrop", c=c, p=p, dropevent=ev, formats=formats)
        if hookres:
            # A plugin handled the drop.
            pass
        else:
            if md.hasUrls():
                self.urlDrop(md, p)
            else:
                self.nodeDrop(md, p)
        g.app.dragging = False
    #@+node:ekr.20110605121601.18366: *5* LeoQTreeWidget.nodeDrop & helpers
    def nodeDrop(self, md, p):
        """
        Handle a drop event when not md.urls().
        This will happen when we drop an outline node.
        We get the copied text from md.text().
        """
        c = self.c
        fn, s = self.parseText(md)
        if not s or not fn:
            return
        if fn == self.fileName():
            if p and p == c.p:
                pass
            elif g.os_path_exists(fn):
                self.intraFileDrop(fn, c.p, p)
        else:
            self.interFileDrop(fn, p, s)
    #@+node:ekr.20110605121601.18367: *6* LeoQTreeWidget.interFileDrop
    def interFileDrop(self, fn, p, s):
        """Paste the mime data after (or as the first child of) p."""
        c = self.c
        u = c.undoer
        undoType = 'Drag Outline'
        isLeo = g.match(s, 0, g.app.prolog_prefix_string)
        if not isLeo:
            return
        c.selectPosition(p)
        pasted = c.fileCommands.getLeoOutlineFromClipboard(s)
            # Paste the node after the presently selected node.
        if not pasted:
            return
        if c.config.getBool('inter-outline-drag-moves'):
            src_c, src_p = g.app.drag_source
            if src_p.hasVisNext(src_c):
                nxt = src_p.getVisNext(src_c).v
            elif src_p.hasVisBack(src_c):
                nxt = src_p.getVisBack(src_c).v
            else:
                nxt = None
            if nxt is not None:
                src_p.doDelete()
                src_c.selectPosition(src_c.vnode2position(nxt))
                src_c.setChanged(True)
                src_c.redraw()
            else:
                g.es("Can't move last node out of outline")
        undoData = u.beforeInsertNode(p,
            pasteAsClone=False, copiedBunchList=[])
        c.validateOutline()
        c.selectPosition(pasted)
        pasted.setDirty()
        pasted.setAllAncestorAtFileNodesDirty()
            # 2011/02/27: Fix bug 690467.
        c.setChanged(True)
        back = pasted.back()
        if back and back.isExpanded():
            pasted.moveToNthChildOf(back, 0)
        # c.setRootPosition(c.findRootPosition(pasted))
        u.afterInsertNode(pasted, undoType, undoData)
        c.redraw(pasted)
        c.recolor()
    #@+node:ekr.20110605121601.18368: *6* LeoQTreeWidget.intraFileDrop (changed)
    def intraFileDrop(self, fn, p1, p2):
        """Move p1 after (or as the first child of) p2."""
        as_child = self.was_alt_drag
        cloneDrag = self.was_control_drag
        c = self.c; u = c.undoer
        c.selectPosition(p1)
        if as_child or p2.hasChildren() and p2.isExpanded():
            # Attempt to move p1 to the first child of p2.
            # parent = p2

            def move(p1, p2):
                if cloneDrag:
                    p1 = p1.clone()
                p1.moveToNthChildOf(p2, 0)
                p1.setDirty()
                return p1

        else:
            # Attempt to move p1 after p2.
            # parent = p2.parent()

            def move(p1, p2):
                if cloneDrag:
                    p1 = p1.clone()
                p1.moveAfter(p2)
                p1.setDirty()
                return p1

        ok = (
            # 2011/10/03: Major bug fix.
            c.checkDrag(p1, p2) and
            c.checkMoveWithParentWithWarning(p1, p2, True))
        if ok:
            undoData = u.beforeMoveNode(p1)
            dirtyVnodeList = p1.setAllAncestorAtFileNodesDirty()
            p1 = move(p1, p2)
            if cloneDrag:
                # Set dirty bits for ancestors of *all* cloned nodes.
                # Note: the setDescendentsDirty flag does not do what we want.
                for z in p1.self_and_subtree():
                    z.setAllAncestorAtFileNodesDirty(
                        setDescendentsDirty=False)
            c.setChanged(True)
            u.afterMoveNode(p1, 'Drag', undoData, dirtyVnodeList)
            if (not as_child or
                p2.isExpanded() or
                c.config.getBool("drag-alt-drag-expands") is not False
            ):
                c.redraw(p1)
            else:
                c.redraw(p2)
    #@+node:ekr.20110605121601.18383: *6* LeoQTreeWidget.parseText
    def parseText(self, md):
        """Parse md.text() into (fn,s)"""
        fn = ''
        s = md.text()
        if s:
            i = s.find(',')
            if i == -1:
                pass
            else:
                fn = s[: i]
                s = s[i + 1:]
        return fn, s
    #@+node:ekr.20110605121601.18369: *5* LeoQTreeWidget.urlDrop & helpers
    def urlDrop(self, md, p):
        """Handle a drop when md.urls()."""
        c, u, undoType = self.c, self.c.undoer, 'Drag Urls'
        urls = md.urls()
        if not urls:
            return
        c.undoer.beforeChangeGroup(c.p, undoType)
        changed = False
        for z in urls:
            url = QtCore.QUrl(z)
            scheme = url.scheme()
            if scheme == 'file':
                changed |= self.doFileUrl(p, url)
            elif scheme in ('http',): # 'ftp','mailto',
                changed |= self.doHttpUrl(p, url)
        if changed:
            c.setChanged(True)
            u.afterChangeGroup(c.p, undoType, reportFlag=False, dirtyVnodeList=[])
            c.redraw()
    #@+node:ekr.20110605121601.18370: *6* LeoQTreeWidget.doFileUrl & helper
    def doFileUrl(self, p, url):
        """Read the file given by the url and put it in the outline."""
        # 2014/06/06: Work around a possible bug in QUrl.
            # fn = str(url.path()) # Fails.
        e = sys.getfilesystemencoding()
        fn = g.toUnicode(url.path(), encoding=e)
        if sys.platform.lower().startswith('win'):
            if fn.startswith('/'):
                fn = fn[1:]
        if os.path.isdir(fn):
            # Just insert an @path directory.
            self.doPathUrlHelper(fn, p)
            return True
        if g.os_path_exists(fn):
            try:
                f = open(fn, 'rb') # 2012/03/09: use 'rb'
            except IOError:
                f = None
            if f:
                s = f.read()
                s = g.toUnicode(s)
                f.close()
                return self.doFileUrlHelper(fn, p, s)
        g.es_print(f"not found: {fn}", nodeLink=p.get_UNL(with_proto=True, with_count=True))
        return False
    #@+node:ekr.20110605121601.18371: *7* LeoQTreeWidget.doFileUrlHelper & helper
    def doFileUrlHelper(self, fn, p, s):
        """
        Insert s in an @file, @auto or @edit node after p.
        If fn is a .leo file, insert a node containing its top-level nodes as children.
        """
        c = self.c
        if self.isLeoFile(fn, s) and not self.was_control_drag:
            g.openWithFileName(fn, old_c=c)
            return False # Don't set the changed marker in the original file.
        u, undoType = c.undoer, 'Drag File'
        undoData = u.beforeInsertNode(p, pasteAsClone=False, copiedBunchList=[])
        if p.hasChildren() and p.isExpanded():
            p2 = p.insertAsNthChild(0)
            parent = p
        elif p.h.startswith('@path '):
            # #60: create relative paths & urls when dragging files.
            p2 = p.insertAsNthChild(0)
            p.expand()
            parent = p
        else:
            p2 = p.insertAfter()
            parent = p.parent()
        # #60: create relative paths & urls when dragging files.
        aList = g.get_directives_dict_list(parent)
        path = g.scanAtPathDirectives(c, aList)
        if path:
            fn = os.path.relpath(fn, path)
            fn = g.toUnicodeFileEncoding(fn)
        self.createAtFileNode(fn, p2, s)
        u.afterInsertNode(p2, undoType, undoData)
        c.selectPosition(p2)
        return True # The original .leo file has changed.
    #@+node:ekr.20110605121601.18372: *8* LeoQTreeWidget.createAtFileNode & helpers (QTreeWidget)
    def createAtFileNode(self, fn, p, s):
        """
        Set p's headline, body text and possibly descendants
        based on the file's name fn and contents s.

        If the file is an thin file, create an @file tree.
        Othewise, create an @auto tree.
        If all else fails, create an @edit node.

        Give a warning if a node with the same headline already exists.
        """
        c = self.c
        c.init_error_dialogs()
        if self.isLeoFile(fn, s):
            self.createLeoFileTree(fn, p)
        elif self.isThinFile(fn, s):
            self.createAtFileTree(fn, p, s)
        elif self.isAutoFile(fn):
            self.createAtAutoTree(fn, p)
        elif self.isBinaryFile(fn):
            self.createUrlForBinaryFile(fn, p)
        else:
            self.createAtEditNode(fn, p)
        self.warnIfNodeExists(p)
        c.raise_error_dialogs(kind='read')
    #@+node:ekr.20110605121601.18373: *9* LeoQTreeWidget.createAtAutoTree (QTreeWidget)
    def createAtAutoTree(self, fn, p):
        """
        Make p an @auto node and create the tree using s, the file's contents.
        """
        c = self.c; at = c.atFileCommands
        p.h = f"@auto {fn}"
        at.readOneAtAutoNode(fn, p)
        # No error recovery should be needed here.
        p.clearDirty() # Don't automatically rewrite this node.
    #@+node:ekr.20110605121601.18374: *9* LeoQTreeWidget.createAtEditNode
    def createAtEditNode(self, fn, p):
        c = self.c; at = c.atFileCommands
        # Use the full @edit logic, so dragging will be
        # exactly the same as reading.
        at.readOneAtEditNode(fn, p)
        p.h = f"@edit {fn}"
        p.clearDirty() # Don't automatically rewrite this node.
    #@+node:ekr.20110605121601.18375: *9* LeoQTreeWidget.createAtFileTree
    def createAtFileTree(self, fn, p, s):
        """Make p an @file node and create the tree using
        s, the file's contents.
        """
        c = self.c; at = c.atFileCommands
        p.h = f"@file {fn}"
        # Read the file into p.
        ok = at.read(root=p.copy(),
            importFileName=None,
            fromString=s,
            atShadow=False,
            force=True) # Disable caching.
        if not ok:
            g.error('Error reading', fn)
            p.b = '' # Safe: will not cause a write later.
            p.clearDirty() # Don't automatically rewrite this node.
    #@+node:ekr.20141007223054.18004: *9* LeoQTreeWidget.createLeoFileTree
    def createLeoFileTree(self, fn, p):
        """Copy all nodes from fn, a .leo file, to the children of p."""
        c = self.c
        p.h = 'From %s' % g.shortFileName(fn)
        c.selectPosition(p)
        # Create a dummy first child of p.
        dummy_p = p.insertAsNthChild(0)
        c.selectPosition(dummy_p)
        c2 = g.openWithFileName(fn, old_c=c, gui=g.app.nullGui)
        for p2 in c2.rootPosition().self_and_siblings():
            c2.selectPosition(p2)
            s = c2.fileCommands.putLeoOutline()
            # Paste the outline after the selected node.
            c.fileCommands.getLeoOutlineFromClipboard(s)
        dummy_p.doDelete()
        c.selectPosition(p)
        p.v.contract()
        c2.close()
        g.app.forgetOpenFile(c2.fileName())
            # Necessary.
    #@+node:ekr.20120309075544.9882: *9* LeoQTreeWidget.createUrlForBinaryFile
    def createUrlForBinaryFile(self, fn, p):
        # Fix bug 1028986: create relative urls when dragging binary files to Leo.
        c = self.c
        base_fn = g.os_path_normcase(g.os_path_abspath(c.mFileName))
        abs_fn = g.os_path_normcase(g.os_path_abspath(fn))
        prefix = os.path.commonprefix([abs_fn, base_fn])
        if prefix and len(prefix) > 3: # Don't just strip off c:\.
            p.h = abs_fn[len(prefix):].strip()
        else:
            p.h = f"@url file://{fn}"
    #@+node:ekr.20110605121601.18377: *9* LeoQTreeWidget.isAutoFile (LeoQTreeWidget)
    def isAutoFile(self, fn):
        """Return true if fn (a file name) can be parsed with an @auto parser."""
        d = g.app.classDispatchDict
        junk, ext = g.os_path_splitext(fn)
        return d.get(ext)
    #@+node:ekr.20120309075544.9881: *9* LeoQTreeWidget.isBinaryFile
    def isBinaryFile(self, fn):
        # The default for unknown files is True. Not great, but safe.
        junk, ext = g.os_path_splitext(fn)
        ext = ext.lower()
        if not ext:
            val = False
        elif ext.startswith('~'):
            val = False
        elif ext in ('.css', '.htm', '.html', '.leo', '.txt'):
            val = False
        # elif ext in ('.bmp','gif','ico',):
            # val = True
        else:
            keys = (z.lower() for z in g.app.extension_dict.keys())
            val = ext not in keys
        return val
    #@+node:ekr.20141007223054.18003: *9* LeoQTreeWidget.isLeoFile
    def isLeoFile(self, fn, s):
        """Return true if fn (a file name) represents an entire .leo file."""
        return fn.endswith('.leo') and s.startswith(g.app.prolog_prefix_string)
    #@+node:ekr.20110605121601.18376: *9* LeoQTreeWidget.isThinFile
    def isThinFile(self, fn, s):
        """
        Return true if the file whose contents is s
        was created from an @thin or @file tree.
        """
        c = self.c; at = c.atFileCommands
        # Skip lines before the @+leo line.
        i = s.find('@+leo')
        if i == -1:
            return False
        # Like at.isFileLike.
        j, k = g.getLine(s, i)
        line = s[j: k]
        valid, new_df, start, end, isThin = at.parseLeoSentinel(line)
        return valid and new_df and isThin
    #@+node:ekr.20110605121601.18378: *9* LeoQTreeWidget.warnIfNodeExists
    def warnIfNodeExists(self, p):
        c = self.c; h = p.h
        for p2 in c.all_unique_positions():
            if p2.h == h and p2 != p:
                g.warning('Warning: duplicate node:', h)
                break
    #@+node:ekr.20110605121601.18379: *7* LeoQTreeWidget.doPathUrlHelper
    def doPathUrlHelper(self, fn, p):
        """Insert fn as an @path node after p."""
        c = self.c
        u, undoType = c.undoer, 'Drag Directory'
        undoData = u.beforeInsertNode(p, pasteAsClone=False, copiedBunchList=[])
        if p.hasChildren() and p.isExpanded():
            p2 = p.insertAsNthChild(0)
        else:
            p2 = p.insertAfter()
        p2.h = '@path ' + fn
        u.afterInsertNode(p2, undoType, undoData)
        c.selectPosition(p2)
    #@+node:ekr.20110605121601.18380: *6* LeoQTreeWidget.doHttpUrl
    def doHttpUrl(self, p, url):
        """Insert the url in an @url node after p."""
        c = self.c; u = c.undoer; undoType = 'Drag Url'
        s = str(url.toString()).strip()
        if not s: return False
        undoData = u.beforeInsertNode(p, pasteAsClone=False, copiedBunchList=[])
        if p.hasChildren() and p.isExpanded():
            p2 = p.insertAsNthChild(0)
        else:
            p2 = p.insertAfter()
        # p2.h,p2.b = '@url %s' % (s),''
        p2.h = '@url'
        p2.b = s
        p2.clearDirty() # Don't automatically rewrite this node.
        u.afterInsertNode(p2, undoType, undoData)
        return True
    #@+node:ekr.20110605121601.18381: *3* LeoQTreeWidget: utils
    #@+node:ekr.20110605121601.18382: *4* LeoQTreeWidget.dump
    def dump(self, ev, p, tag):
        if ev:
            md = ev.mimeData()
            s = g.checkUnicode(md.text(), encoding='utf-8')
            g.trace('md.text:', repr(s) if len(s) < 100 else len(s))
            for url in md.urls() or []:
                g.trace('     url:', url)
                g.trace('  url.fn:', url.toLocalFile())
                g.trace('url.text:', url.toString())
        else:
            g.trace('', tag, '** no event!')
    #@+node:ekr.20141007223054.18002: *4* LeoQTreeWidget.fileName
    def fileName(self):
        """Return the commander's filename."""
        return self.c.fileName() or '<unsaved file>'
    #@-others
#@+node:ekr.20110605121601.18385: ** class LeoQtSpellTab
class LeoQtSpellTab:
    #@+others
    #@+node:ekr.20110605121601.18386: *3* LeoQtSpellTab.__init__
    def __init__(self, c, handler, tabName):
        """Ctor for LeoQtSpellTab class."""
        self.c = c
        top = c.frame.top
        self.handler = handler
        # hack:
        handler.workCtrl = leoFrame.StringTextWrapper(c, 'spell-workctrl')
        self.tabName = tabName
        if hasattr(top, 'leo_spell_label'):
            self.wordLabel = top.leo_spell_label
            self.listBox = top.leo_spell_listBox
            self.fillbox([])
        else:
            self.handler.loaded = False
    #@+node:ekr.20110605121601.18389: *3* Event handlers
    #@+node:ekr.20110605121601.18390: *4* onAddButton
    def onAddButton(self):
        """Handle a click in the Add button in the Check Spelling dialog."""
        self.handler.add()
    #@+node:ekr.20110605121601.18391: *4* onChangeButton & onChangeThenFindButton
    def onChangeButton(self, event=None):
        """Handle a click in the Change button in the Spell tab."""
        state = self.updateButtons()
        if state:
            self.handler.change()
        self.updateButtons()

    def onChangeThenFindButton(self, event=None):
        """Handle a click in the "Change, Find" button in the Spell tab."""
        state = self.updateButtons()
        if state:
            self.handler.change()
            if self.handler.change():
                self.handler.find()
            self.updateButtons()
    #@+node:ekr.20110605121601.18392: *4* onFindButton
    def onFindButton(self):
        """Handle a click in the Find button in the Spell tab."""
        c = self.c
        self.handler.find()
        self.updateButtons()
        c.invalidateFocus()
        c.bodyWantsFocus()
    #@+node:ekr.20110605121601.18393: *4* onHideButton
    def onHideButton(self):
        """Handle a click in the Hide button in the Spell tab."""
        self.handler.hide()
    #@+node:ekr.20110605121601.18394: *4* onIgnoreButton
    def onIgnoreButton(self, event=None):
        """Handle a click in the Ignore button in the Check Spelling dialog."""
        self.handler.ignore()
    #@+node:ekr.20110605121601.18395: *4* onMap
    def onMap(self, event=None):
        """Respond to a Tk <Map> event."""
        self.update(show=False, fill=False)
    #@+node:ekr.20110605121601.18396: *4* onSelectListBox
    def onSelectListBox(self, event=None):
        """Respond to a click in the selection listBox."""
        c = self.c
        self.updateButtons()
        c.bodyWantsFocus()
    #@+node:ekr.20110605121601.18397: *3* Helpers
    #@+node:ekr.20110605121601.18398: *4* bringToFront (LeoQtSpellTab)
    def bringToFront(self):
        self.c.frame.log.selectTab('Spell')
    #@+node:ekr.20110605121601.18399: *4* fillbox (LeoQtSpellTab)
    def fillbox(self, alts, word=None):
        """Update the suggestions listBox in the Check Spelling dialog."""
        self.suggestions = alts
        if not word: word = ""
        self.wordLabel.setText("Suggestions for: " + word)
        self.listBox.clear()
        if self.suggestions:
            self.listBox.addItems(self.suggestions)
            self.listBox.setCurrentRow(0)
    #@+node:ekr.20110605121601.18400: *4* getSuggestion (LeoQtSpellTab)
    def getSuggestion(self):
        """Return the selected suggestion from the listBox."""
        idx = self.listBox.currentRow()
        value = self.suggestions[idx]
        return value
    #@+node:ekr.20141113094129.13: *4* setFocus (LeoQtSpellTab)
    def setFocus(self):
        """Actually put focus in the tab."""
        # Not a great idea: there is no indication of focus.
        c = self.c
        if c.frame and c.frame.top and hasattr(c.frame.top, 'spellFrame'):
            w = self.c.frame.top.spellFrame
            c.widgetWantsFocus(w)
    #@+node:ekr.20110605121601.18401: *4* update (LeoQtSpellTab)
    def update(self, show=True, fill=False):
        """Update the Spell Check dialog."""
        c = self.c
        if fill:
            self.fillbox([])
        self.updateButtons()
        if show:
            self.bringToFront()
            c.bodyWantsFocus()
    #@+node:ekr.20110605121601.18402: *4* updateButtons (spellTab)
    def updateButtons(self):
        """Enable or disable buttons in the Check Spelling dialog."""
        c = self.c
        top, w = c.frame.top, c.frame.body.wrapper
        state = self.suggestions and w.hasSelection()
        top.leo_spell_btn_Change.setDisabled(not state)
        top.leo_spell_btn_FindChange.setDisabled(not state)
        return state
    #@-others
#@+node:ekr.20110605121601.18438: ** class LeoQtTreeTab
class LeoQtTreeTab:
    """
    A class representing a so-called tree-tab.

    Actually, it represents a combo box
    """
    #@+others
    #@+node:ekr.20110605121601.18439: *3*  Birth & death
    #@+node:ekr.20110605121601.18440: *4*  ctor (LeoQtTreeTab)
    def __init__(self, c, iconBar):
        """Ctor for LeoQtTreeTab class."""

        self.c = c
        self.cc = c.chapterController
        assert self.cc
        self.iconBar = iconBar
        self.lockout = False # True: do not redraw.
        self.tabNames = []
            # The list of tab names. Changes when tabs are renamed.
        self.w = None # The QComboBox
        # self.reloadSettings()
        self.createControl()
        
    #@+node:ekr.20110605121601.18441: *4* tt.createControl (defines class LeoQComboBox)
    def createControl(self):

        class LeoQComboBox(QtWidgets.QComboBox):
            """Create a subclass in order to handle focusInEvents."""

            def __init__(self, tt):
                self.leo_tt = tt
                super().__init__()
                # Fix #458: Chapters drop-down list is not automatically resized.
                self.setSizeAdjustPolicy(self.AdjustToContents)

            def focusInEvent(self, event):
                self.leo_tt.setNames()
                QtWidgets.QComboBox.focusInEvent(self, event) # Call the base class

        tt = self
        frame = QtWidgets.QLabel('Chapters: ')
        tt.iconBar.addWidget(frame)
        tt.w = w = LeoQComboBox(tt)
        tt.setNames()
        tt.iconBar.addWidget(w)

        def onIndexChanged(s, tt=tt):
            if isinstance(s, int):
                s = '' if s == -1 else tt.w.currentText()
            else: # s is the tab name.
                pass
            if s and not tt.cc.selectChapterLockout:
                tt.selectTab(s)
        # A change: the argument could now be an int instead of a string.

        w.currentIndexChanged.connect(onIndexChanged)
    #@+node:ekr.20110605121601.18443: *3* tt.createTab
    def createTab(self, tabName, select=True):
        """LeoQtTreeTab."""
        tt = self
        # Avoid a glitch during initing.
        if tabName != 'main' and tabName not in tt.tabNames:
            tt.tabNames.append(tabName)
            tt.setNames()
    #@+node:ekr.20110605121601.18444: *3* tt.destroyTab
    def destroyTab(self, tabName):
        """LeoQtTreeTab."""
        tt = self
        if tabName in tt.tabNames:
            tt.tabNames.remove(tabName)
            tt.setNames()
    #@+node:ekr.20110605121601.18445: *3* tt.selectTab
    def selectTab(self, tabName):
        """LeoQtTreeTab."""
        tt, c, cc = self, self.c, self.cc
        exists = tabName in self.tabNames
        c.treeWantsFocusNow()
            # Fix #969. Somehow this is important.
        if not exists:
            tt.createTab(tabName) # Calls tt.setNames()
        if tt.lockout:
            return
        cc.selectChapterByName(tabName)
        c.redraw()
        c.outerUpdate()
    #@+node:ekr.20110605121601.18446: *3* tt.setTabLabel
    def setTabLabel(self, tabName):
        """LeoQtTreeTab."""
        w = self.w
        i = w.findText(tabName)
        if i > -1:
            w.setCurrentIndex(i)
    #@+node:ekr.20110605121601.18447: *3* tt.setNames
    def setNames(self):
        """LeoQtTreeTab: Recreate the list of items."""
        w = self.w
        names = self.cc.setAllChapterNames()
        w.clear()
        w.insertItems(0, names)
    #@-others
#@+node:ekr.20110605121601.18448: ** class LeoTabbedTopLevel (LeoBaseTabWidget)
class LeoTabbedTopLevel(LeoBaseTabWidget):
    """ Toplevel frame for tabbed ui """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ## middle click close on tabs -- JMP 20140505
        self.setMovable(False)
        tb = QtTabBarWrapper(self)
        self.setTabBar(tb)
#@+node:peckj.20140505102552.10377: ** class QtTabBarWrapper (QTabBar)
class QtTabBarWrapper(QtWidgets.QTabBar):
    #@+others
    #@+node:peckj.20140516114832.10108: *3* __init__
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(True)
    #@+node:peckj.20140516114832.10109: *3* mouseReleaseEvent (QtTabBarWrapper)
    def mouseReleaseEvent(self, event):
        # middle click close on tabs -- JMP 20140505
        # closes Launchpad bug: https://bugs.launchpad.net/leo-editor/+bug/1183528
        if event.button() == QtCore.Qt.MidButton:
            self.tabCloseRequested.emit(self.tabAt(event.pos()))
        QtWidgets.QTabBar.mouseReleaseEvent(self, event)
    #@-others
#@+node:ekr.20110605121601.18458: ** class QtMenuWrapper (LeoQtMenu,QMenu)
class QtMenuWrapper(LeoQtMenu, QtWidgets.QMenu):
    #@+others
    #@+node:ekr.20110605121601.18459: *3* ctor and __repr__(QtMenuWrapper)
    def __init__(self, c, frame, parent, label):
        """ctor for QtMenuWrapper class."""
        assert c
        assert frame
        if parent is None:
            parent = c.frame.top.menuBar()
        #
        # For reasons unknown, the calls must be in this order.
        # Presumably, the order of base classes also matters(!)
        LeoQtMenu.__init__(self, c, frame, label)
        QtWidgets.QMenu.__init__(self, parent)
        label = label.replace('&', '').lower()
        self.leo_menu_label = label
        action = self.menuAction()
        if action:
            action.leo_menu_label = label
        self.aboutToShow.connect(self.onAboutToShow)

    def __repr__(self):
        return f"<QtMenuWrapper {self.leo_menu_label}>"
    #@+node:ekr.20110605121601.18460: *3* onAboutToShow & helpers (QtMenuWrapper)
    def onAboutToShow(self, *args, **keys):

        name = self.leo_menu_label
        if not name: return
        for action in self.actions():
            commandName = hasattr(action, 'leo_command_name') and action.leo_command_name
            if commandName:
                self.leo_update_shortcut(action, commandName)
                self.leo_enable_menu_item(action, commandName)
                self.leo_update_menu_label(action, commandName)
    #@+node:ekr.20120120095156.10261: *4* leo_enable_menu_item
    def leo_enable_menu_item(self, action, commandName):
        func = self.c.frame.menu.enable_dict.get(commandName)
        if action and func:
            val = func()
            action.setEnabled(bool(val))
    #@+node:ekr.20120124115444.10190: *4* leo_update_menu_label
    def leo_update_menu_label(self, action, commandName):
        c = self.c
        if action and commandName == 'mark':
            action.setText('UnMark' if c.p.isMarked() else 'Mark')
            self.leo_update_shortcut(action, commandName)
                # Set the proper shortcut.
    #@+node:ekr.20120120095156.10260: *4* leo_update_shortcut
    def leo_update_shortcut(self, action, commandName):

        c = self.c; k = c.k
        if action:
            s = action.text()
            parts = s.split('\t')
            if len(parts) >= 2: s = parts[0]
            key, aList = c.config.getShortcut(commandName)
            if aList:
                result = []
                for bi in aList:
                    # Don't show mode-related bindings.
                    if not bi.isModeBinding():
                        accel = k.prettyPrintKey(bi.stroke)
                        result.append(accel)
                        # Break here if we want to show only one accerator.
                action.setText(f"{s}\t{', '.join(result)}")
            else:
                action.setText(s)
        else:
            g.trace(f"can not happen: no action for {commandName}")
    #@-others
#@+node:ekr.20110605121601.18461: ** class QtSearchWidget
class QtSearchWidget:
    """A dummy widget class to pass to Leo's core find code."""

    def __init__(self):
        self.insertPoint = 0
        self.selection = 0, 0
        self.wrapper = self
        self.body = self
        self.text = None
#@+node:ekr.20110605121601.18464: ** class TabbedFrameFactory
class TabbedFrameFactory:
    """
    'Toplevel' frame builder for tabbed toplevel interface

    This causes Leo to maintain only one toplevel window,
    with multiple tabs for documents
    """
    #@+others
    #@+node:ekr.20110605121601.18465: *3* frameFactory.__init__	 & __repr__
    def __init__(self):
        # will be created when first frame appears
        # DynamicWindow => Leo frame map
        self.alwaysShowTabs = True
            # Set to true to workaround a problem
            # setting the window title when tabs are shown.
        self.leoFrames = {}
            # Keys are DynamicWindows, values are frames.
        self.masterFrame = None
        self.createTabCommands()
        
    #@+node:ekr.20110605121601.18466: *3* frameFactory.createFrame (changed, makes dw)
    def createFrame(self, leoFrame):

        c = leoFrame.c
        tabw = self.masterFrame
        dw = DynamicWindow(c, tabw)
        self.leoFrames[dw] = leoFrame
        # Shorten the title.
        title = os.path.basename(c.mFileName) if c.mFileName else leoFrame.title
        tip = leoFrame.title
        dw.setWindowTitle(tip)
        idx = tabw.addTab(dw, title)
        if tip:
            tabw.setTabToolTip(idx, tip)
        dw.construct(master=tabw)
        tabw.setCurrentIndex(idx)
        g.app.gui.setFilter(c, dw, dw, tag='tabbed-frame')
        #
        # Work around the problem with missing dirty indicator
        # by always showing the tab.
        tabw.tabBar().setVisible(self.alwaysShowTabs or tabw.count() > 1)
        tabw.setTabsClosable(c.config.getBool('outline-tabs-show-close', True))
        if True: # #1327: Must always do this.
            dw.show()
            tabw.show()
        return dw
    #@+node:ekr.20110605121601.18468: *3* frameFactory.createMaster (changed)
    def createMaster(self):
        
        window = self.masterFrame = LeoTabbedTopLevel(factory=self)
        tabbar = window.tabBar()
        if g.app.use_global_docks:
           pass
        else:
            g.app.gui.attachLeoIcon(window)
        try:
            tabbar.setTabsClosable(True)
            tabbar.tabCloseRequested.connect(self.slotCloseRequest)
        except AttributeError:
            pass # Qt 4.4 does not support setTabsClosable
        window.currentChanged.connect(self.slotCurrentChanged)
        if 'size' in g.app.debug:
            g.trace(
                f"minimized: {g.app.start_minimized}, "
                f"maximized: {g.app.start_maximized}, "
                f"fullscreen: {g.app.start_fullscreen}")
        #
        # #1189: We *can* (and should) minimize here, to eliminate flash.
        if g.app.use_global_docks:
            pass
        else:
            if g.app.start_minimized:
                window.showMinimized()
    #@+node:ekr.20110605121601.18472: *3* frameFactory.createTabCommands
    def detachTab(self, wdg):
        """ Detach specified tab as individual toplevel window """
        del self.leoFrames[wdg]
        wdg.setParent(None)
        wdg.show()

    def createTabCommands(self):
        #@+<< Commands for tabs >>
        #@+node:ekr.20110605121601.18473: *4* << Commands for tabs >>
        @g.command('tab-detach')
        def tab_detach(event):
            """ Detach current tab from tab bar """
            if len(self.leoFrames) < 2:
                g.es_print_error("Can't detach last tab")
                return
            c = event['c']
            f = c.frame
            tabwidget = g.app.gui.frameFactory.masterFrame
            tabwidget.detach(tabwidget.indexOf(f.top))
            f.top.setWindowTitle(f.title + ' [D]')
        # this is actually not tab-specific, move elsewhere?

        @g.command('close-others')
        def close_others(event):
            """Close all windows except the present window."""
            myc = event['c']
            for c in g.app.commanders():
                if c is not myc:
                    c.close()

        def tab_cycle(offset):

            tabw = self.masterFrame
            cur = tabw.currentIndex()
            count = tabw.count()
            # g.es("cur: %s, count: %s, offset: %s" % (cur,count,offset))
            cur += offset
            if cur < 0:
                cur = count - 1
            elif cur >= count:
                cur = 0
            tabw.setCurrentIndex(cur)
            self.focusCurrentBody()

        @g.command('tab-cycle-next')
        def tab_cycle_next(event):
            """ Cycle to next tab """
            tab_cycle(1)

        @g.command('tab-cycle-previous')
        def tab_cycle_previous(event):
            """ Cycle to next tab """
            tab_cycle(-1)
        #@-<< Commands for tabs >>
    #@+node:ekr.20110605121601.18467: *3* frameFactory.deleteFrame
    def deleteFrame(self, wdg):

        if not wdg:
            return
        if wdg not in self.leoFrames:
            # probably detached tab
            self.masterFrame.delete(wdg)
            return
        tabw = self.masterFrame
        idx = tabw.indexOf(wdg)
        tabw.removeTab(idx)
        del self.leoFrames[wdg]
        wdg2 = tabw.currentWidget()
        if wdg2:
            g.app.selectLeoWindow(wdg2.leo_c)
        tabw.tabBar().setVisible(self.alwaysShowTabs or tabw.count() > 1)
    #@+node:ekr.20110605121601.18471: *3* frameFactory.focusCurrentBody
    def focusCurrentBody(self):
        """ Focus body control of current tab """
        tabw = self.masterFrame
        w = tabw.currentWidget()
        w.setFocus()
        f = self.leoFrames[w]
        c = f.c
        c.bodyWantsFocusNow()
        # Fix bug 690260: correct the log.
        g.app.log = f.log
    #@+node:ekr.20110605121601.18469: *3* frameFactory.setTabForCommander
    def setTabForCommander(self, c):
        tabw = self.masterFrame # a QTabWidget
        for dw in self.leoFrames: # A dict whose keys are DynamicWindows.
            if dw.leo_c == c:
                for i in range(tabw.count()):
                    if tabw.widget(i) == dw:
                        tabw.setCurrentIndex(i)
                        break
                break
    #@+node:ekr.20110605121601.18470: *3* frameFactory.signal handlers
    def slotCloseRequest(self, idx):

        tabw = self.masterFrame
        w = tabw.widget(idx)
        f = self.leoFrames[w]
        c = f.c
        c.close(new_c=None)
            # 2012/03/04: Don't set the frame here.
            # Wait until the next slotCurrentChanged event.
            # This keeps the log and the QTabbedWidget in sync.

    def slotCurrentChanged(self, idx):
        # Two events are generated, one for the tab losing focus,
        # and another event for the tab gaining focus.
        tabw = self.masterFrame
        w = tabw.widget(idx)
        f = self.leoFrames.get(w)
        if not f:
            return
        tabw.setWindowTitle(f.title)
        # Don't do this: it would break --minimize.
            # g.app.selectLeoWindow(f.c)
        # Fix bug 690260: correct the log.
        g.app.log = f.log
        # Redraw the tab.
        c = f.c
        if c:
            c.redraw()
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
