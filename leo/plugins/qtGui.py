# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20110605121601.18002: * @file ../plugins/qtGui.py
#@@first
'''qt gui plugin.'''
python_qsh = True
    # True use PythonQSyntaxHighlighter
    # False use QtGui.QSyntaxHighlighter
# if python_qsh: print('===== python_qsh ===== ')
#@@language python
#@@tabwidth -4
#@@pagewidth 80

# Define these to suppress pylint warnings...
# pylint: disable=cell-var-from-loop
__timing = None # For timing stats.
__qh = None # For quick headlines.

# A switch telling whether to use qt_main.ui and qt_main.py.
useUI = False # True: use qt_main.ui. False: use DynamicWindow.createMainWindow.
#@+<< imports >>
#@+node:ekr.20110605121601.18003: **  << imports >> (qtGui.py)
import leo.core.leoGlobals as g

import leo.core.leoColor as leoColor
import leo.core.leoColorizer as leoColorizer
import leo.core.leoFrame as leoFrame
# import leo.core.LeoFind as LeoFind
import leo.core.leoGui as leoGui
import leo.core.leoMenu as leoMenu
import leo.core.leoPlugins as leoPlugins
    # Uses leoPlugins.TryNext.

import leo.plugins.baseNativeTree as baseNativeTree
from leo.plugins.mod_scripting import build_rclick_tree

import datetime
import os
import string
import sys
import time
import platform
import time
from collections import defaultdict

from leo.core.leoQt import isQt5,QtCore,QtGui,QtWidgets
from leo.core.leoQt import Qsci,uic

from leo.plugins.qt_text import PlainTextWrapper # BaseQTextWrapper,
from leo.plugins.qt_text import QTextMixin,LeoQTextBrowser
from leo.plugins.qt_text import QHeadlineWrapper,QMinibufferWrapper
from leo.plugins.qt_text import QScintillaWrapper,QTextEditWrapper

try:
    import leo.plugins.nested_splitter as nested_splitter
    splitter_class = nested_splitter.NestedSplitter
    # disable special behavior, turned back on by associated plugin,
    # if the plugin's loaded
    nested_splitter.NestedSplitter.enabled = False
except ImportError:
    print('Can not import nested_splitter')
    splitter_class = QtWidgets.QSplitter
#@-<< imports >>

#@+others
#@+node:ekr.20110605121601.18133: **  Module level

#@+node:ekr.20110605121601.18134: *3* init (qtGui.py top level) (qtPdb)
def init():

    trace = (False or g.trace_startup) and not g.unitTesting
    if trace and g.trace_startup: print('qtGui.__init__')

    if g.app.unitTesting: # Not Ok for unit testing!
        return False

    if not QtCore:
        return False
    
    if g.app.gui:
        return g.app.gui.guiName() == 'qt'
    else:
        g.app.gui = LeoQtGui()

        # Now done in g.pdb.
        # # Override g.pdb
        # def qtPdb(message=''):
            # if message: print(message)
            # import pdb
            # if not g.app.useIpython:
                # QtCore.pyqtRemoveInputHook()
            # pdb.set_trace()
        # g.pdb = qtPdb

        g.app.gui.finishCreate()
        g.plugin_signon(__name__)
        return True
#@+node:tbrown.20140620095406.40066: *3* show/hide icon/menu/status bar
# create the commands gui-<menu|iconbar|statusbar|minibuffer>-<hide|show>
widgets = [
    ('menu', lambda c: c.frame.top.menuBar()),
    ('iconbar', lambda c: c.frame.top.iconBar),
    ('statusbar', lambda c: c.frame.top.statusBar),
    ('minibuffer', lambda c: c.frame.miniBufferWidget.widget.parent()),
    ('tabbar', lambda c: g.app.gui.frameFactory.masterFrame.tabBar()),
]
for vis in 'hide', 'show', 'toggle':
    for name, widget in widgets:
        def dovis(event, widget=widget, vis=vis):
            c = event['c']
            w = widget(c)
            if vis == 'toggle':
                vis = 'hide' if w.isVisible() else 'show'
            getattr(w, vis)()
        g.command("gui-%s-%s"%(name, vis))(dovis)
    def doall(event, vis=vis):
        
        c = event['c']
        for name, widget in widgets:
            w = widget(c)
            if vis == 'toggle':
                # note, this *intentionally* toggles all to on/off
                # based on the state of the first
                vis = 'hide' if w.isVisible() else 'show'
            getattr(w, vis)()
    g.command("gui-all-%s"%vis)(doall)
#@+node:tbrown.20140814090009.55875: *3* manage styles
#@+node:tbrown.20140814090009.55874: *4* style_reload
@g.command('style-reload')
def style_reload(kwargs):
    """reload_styles - recompile, if necessary, the stylesheet, and re-apply
    
    This method, added 20140814, is intended to replace execution of the
    `stylesheet & source` node in (my)LeoSettings.leo, and the script in the
    `@button reload-styles` node, which should just become
    `c.k.simulateCommand('style-reload')`.

    :Parameters:
    - `kwargs`: kwargs from Leo command
    
    Returns True on success, otherwise False
    """
    
    c = kwargs['c']
    
    # first, rebuild the stylesheet template from the tree, if
    # the stylesheet source is in tree form, e.g. dark themes, currently the
    # default light theme uses a single @data qt-gui-plugin-style-sheet node
    settings_p = g.findNodeAnywhere(c, '@settings')
    if not settings_p:
        # pylint: disable=fixme
        g.es("No '@settings' node found in outline")
        g.es("Please see http://leoeditor.com/FIXME.html")
        return False
    themes = []
    theme_name = 'unknown'
    for i in settings_p.subtree_iter():
        if i.h.startswith('@string color_theme'):
            theme_name = i.h.split()[-1]
        if i.h == 'stylesheet & source':
            themes.append((theme_name, i.copy()))
            theme_name = 'unknown'
    if themes:
        g.es("Found theme(s):")
        for i in themes:
            g.es("   "+i[0])
        if len(themes) > 1:
            g.es("WARNING: using the *last* theme found")
        theme_p = themes[-1][1]
        unl = theme_p.get_UNL()+'-->'
        seen = 0
        for i in theme_p.subtree_iter():
            if i.h == '@data qt-gui-plugin-style-sheet':
                i.h = '@@data qt-gui-plugin-style-sheet'
                seen += 1
        if seen == 0:
            g.es("NOTE: Did not find compiled stylesheet for theme")
        if seen > 1:
            g.es("NOTE: Found multiple compiled stylesheets for theme")
        text = [
            "/*\n  DON'T EDIT THIS, EDIT THE OTHER NODES UNDER "
            "('stylesheet & source')\n  AND RECREATE THIS BY "
            "Alt-X style-reload"
            "\n\n  AUTOMATICALLY GENERATED FROM:\n  %s\n  %s\n*/\n\n"
            % (
                theme_p.get_UNL(with_proto=True),
                datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
            )]
        for i in theme_p.subtree_iter():
            src = i.get_UNL().replace(unl, '')
            if i.h.startswith('@data '):
                i.h = '@'+i.h
            if ('@ignore' in src) or ('@data' in src):
                continue
            text.append("/*### %s %s*/\n%s\n\n" % (
                src, '#'*(70-len(src)),
                i.b.strip()
            ))
            
        data_p = theme_p.insertAsLastChild()
        data_p.h = '@data qt-gui-plugin-style-sheet'
        data_p.b = '\n'.join(text)
        g.es("Stylesheet compiled")
        
    else:
        g.es("No theme found, assuming static stylesheet")
        sheets = [i.copy() for i in settings_p.subtree_iter()
                  if i.h == '@data qt-gui-plugin-style-sheet']
        if not sheets:
            g.es("Didn't find '@data qt-gui-plugin-style-sheet' node")
            return False
        if len(sheets) > 1:
            g.es("WARNING: found multiple\n'@data qt-gui-plugin-style-sheet' nodes")
            g.es("Using the *last* node found")
        else:
            g.es("Stylesheet found")
        data_p = sheets[-1]

    # then, reload settings from this file
    shortcuts, settings = g.app.loadManager.createSettingsDicts(c, True)
    c.config.settingsDict.update(settings)
    
    # apply the stylesheet
    c.frame.top.setStyleSheets()
    # check that our styles were applied
    used = str(g.app.gui.frameFactory.masterFrame.styleSheet())
    sheet = g.expand_css_constants(c, data_p.b)
    # Qt normalizes whitespace, so we must too
    used = ' '.join(used.split())
    sheet = ' '.join(sheet.split())
    c.redraw()
    if used != sheet:
        g.es("WARNING: styles in use do not match applied styles")
        return False
    else:
        g.es("Styles reloaded")
        return True
#@+node:ekr.20110605121601.18136: ** Frame and component classes...
#@+node:ekr.20110605121601.18137: *3* class  DynamicWindow (QtWidgets.QMainWindow)
class DynamicWindow(QtWidgets.QMainWindow):

    '''A class representing all parts of the main Qt window.
    
    **Important**: when using tabs, the LeoTabbedTopLevel widget
    is the top-level window, **not** this QMainWindow!

    c.frame.top is a DynamicWindow object.

    For --gui==qttabs:
        c.frame.top.parent is a TabbedFrameFactory
        c.frame.top.leo_master is a LeoTabbedTopLevel

    All leoQtX classes use the ivars of this Window class to
    support operations requested by Leo's core.
    '''

    #@+others
    #@+node:ekr.20110605121601.18138: *4*  ctor (DynamicWindow)
    # Called from LeoQtFrame.finishCreate.

    def __init__(self,c,parent=None):

        '''Create Leo's main window, c.frame.top'''

        # For qttabs gui, parent is a LeoTabbedTopLevel.

        # g.trace('(DynamicWindow)',g.callers())
        QtWidgets.QMainWindow.__init__(self,parent)
        self.leo_c = c
        self.leo_master = None # Set in construct.
        self.leo_menubar = None # Set in createMenuBar.
        self.leo_ui = None # Set in construct.
        c._style_deltas = defaultdict(lambda: 0) # for adjusting styles dynamically
        # g.trace('(DynamicWindow)',g.listToString(dir(self),sort=True))
    #@+node:ekr.20110605121601.18140: *4* dw.closeEvent
    def closeEvent (self,event):

        trace = False and not g.unitTesting

        c = self.leo_c

        if not c.exists:
            # Fixes double-prompt bug on Linux.
            if trace: g.trace('destroyed')
            event.accept()
            return

        if c.inCommand:
            if trace: g.trace('in command')
            c.requestCloseWindow = True
        else:
            if trace: g.trace('closing')
            ok = g.app.closeLeoWindow(c.frame)
            if ok:
                event.accept()
            else:
                event.ignore()
    #@+node:ekr.20110605121601.18139: *4* dw.construct
    def construct(self,master=None):
        """ Factor 'heavy duty' code out from ctor """

        c = self.leo_c
        # top = c.frame.top
        self.leo_master=master # A LeoTabbedTopLevel for tabbed windows.
        # g.trace('(DynamicWindow)',g.callers())
        # Init the base class.
        ui_file_name = c.config.getString('qt_ui_file_name')
        self.useScintilla = c.config.getBool('qt-use-scintilla')
        if not ui_file_name:
            ui_file_name = 'qt_main.ui'
        ui_description_file = g.app.loadDir + "/../plugins/" + ui_file_name
        # g.pr('DynamicWindw.__init__,ui_description_file)
        assert g.os_path_exists(ui_description_file)
        self.bigTree = c.config.getBool('big_outline_pane')
        if useUI:  
            self.leo_ui = uic.loadUi(ui_description_file, self)
        else:
            self.createMainWindow()
        self.iconBar = self.addToolBar("IconBar")
        # Set orientation if requested.
        d = {
            'bottom':QtCore.Qt.BottomToolBarArea,
            'left':QtCore.Qt.LeftToolBarArea,
            'right':QtCore.Qt.RightToolBarArea,
            'top':QtCore.Qt.TopToolBarArea,
        }
        where = c.config.getString('qt-toolbar-location')
        if where:
            where = d.get(where)
            if where: self.addToolBar(where,self.iconBar)
        self.leo_menubar = self.menuBar()
        self.statusBar = QtWidgets.QStatusBar()
        self.setStatusBar(self.statusBar)
        orientation = c.config.getString('initial_split_orientation')
        self.setSplitDirection(orientation)
        self.setStyleSheets()
        
        # self.setLeoWindowIcon()
    #@+node:ekr.20110605121601.18141: *4* dw.createMainWindow & helpers
    # Called instead of uic.loadUi(ui_description_file, self)

    def createMainWindow (self):

        '''Create the component ivars of the main window.

        Copied/adapted from qt_main.py'''

        MainWindow = self
        self.leo_ui = self

        self.setMainWindowOptions()
        self.createCentralWidget()
        self.createMainLayout(self.centralwidget)
            # Creates .verticalLayout, .splitter and .splitter_2.
        # g.trace(self.bigTree)
        if self.bigTree:
            self.createBodyPane(self.splitter)
            self.createLogPane(self.splitter)
            treeFrame = self.createOutlinePane(self.splitter_2)
            self.splitter_2.addWidget(treeFrame)
            self.splitter_2.addWidget(self.splitter)
        else:
            self.createOutlinePane(self.splitter)
            self.createLogPane(self.splitter)
            self.createBodyPane(self.splitter_2)
        self.createMiniBuffer(self.centralwidget)
        self.createMenuBar()
        self.createStatusBar(MainWindow)

        # Signals
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
    #@+node:ekr.20110605121601.18142: *5* dw.top-level
    #@+node:ekr.20110605121601.18143: *6* dw.createBodyPane
    def createBodyPane (self,parent):
        '''Create the body pane.'''
        # Create widgets.
        bodyFrame = self.createFrame(parent,'bodyFrame')
        innerFrame = self.createFrame(bodyFrame,'innerBodyFrame',
            hPolicy=QtWidgets.QSizePolicy.Expanding)
        sw = self.createStackedWidget(innerFrame,'bodyStackedWidget')
        page2 = QtWidgets.QWidget()
        self.setName(page2,'bodyPage2')
        body = self.createText(page2,'richTextEdit')
        # Pack.
        vLayout = self.createVLayout(page2,'bodyVLayout',spacing=6)
        grid = self.createGrid(bodyFrame,'bodyGrid')
        innerGrid = self.createGrid(innerFrame,'bodyInnerGrid')
        vLayout.addWidget(body)
        sw.addWidget(page2)
        innerGrid.addWidget(sw, 0, 0, 1, 1)
        grid.addWidget(innerFrame, 0, 0, 1, 1)
        self.verticalLayout.addWidget(parent)
        # Official ivars
        self.text_page = page2
        self.stackedWidget = sw # used by LeoQtBody
        self.richTextEdit = body
        self.leo_body_frame = bodyFrame
        self.leo_body_inner_frame = innerFrame
    #@+node:ekr.20110605121601.18144: *6* dw.createCentralWidget
    def createCentralWidget (self):

        MainWindow = self

        w = QtWidgets.QWidget(MainWindow)
        w.setObjectName("centralwidget")

        MainWindow.setCentralWidget(w)

        # Official ivars.
        self.centralwidget = w
    #@+node:ekr.20110605121601.18145: *6* dw.createLogPane & helper
    def createLogPane (self,parent):

        # Create widgets.
        logFrame = self.createFrame(parent,'logFrame',
            vPolicy = QtWidgets.QSizePolicy.Minimum)
        innerFrame = self.createFrame(logFrame,'logInnerFrame',
            hPolicy=QtWidgets.QSizePolicy.Preferred,
            vPolicy=QtWidgets.QSizePolicy.Expanding)
        tabWidget = self.createTabWidget(innerFrame,'logTabWidget')
        # Pack.
        innerGrid = self.createGrid(innerFrame,'logInnerGrid')
        innerGrid.addWidget(tabWidget, 0, 0, 1, 1)
        outerGrid = self.createGrid(logFrame,'logGrid')
        outerGrid.addWidget(innerFrame, 0, 0, 1, 1)
        # Embed the Find tab in a QScrollArea.
        findScrollArea = QtWidgets.QScrollArea()
        findScrollArea.setObjectName('findScrollArea')
        # Find tab.
        findTab = QtWidgets.QWidget()
        findTab.setObjectName('findTab')
        tabWidget.addTab(findScrollArea,'Find')
        if 1: # Do this later, in LeoFind.finishCreate
            self.findScrollArea = findScrollArea
            self.findTab = findTab
        else:
            self.createFindTab(findTab,findScrollArea)
            findScrollArea.setWidget(findTab)
        # Spell tab.
        spellTab = QtWidgets.QWidget()
        spellTab.setObjectName('spellTab')
        tabWidget.addTab(spellTab,'Spell')
        self.createSpellTab(spellTab)
        tabWidget.setCurrentIndex(1)
        # Official ivars
        self.tabWidget = tabWidget # Used by LeoQtLog.
    #@+node:ekr.20131118172620.16858: *7* dw.finishCreateLogPane
    def finishCreateLogPane(self):
        '''It's useful to create this late, because c.config is now valid.'''
        self.createFindTab(self.findTab,self.findScrollArea)
        self.findScrollArea.setWidget(self.findTab)
    #@+node:ekr.20110605121601.18146: *6* dw.createMainLayout
    def createMainLayout (self,parent):

        # c = self.leo_c
        vLayout = self.createVLayout(parent,'mainVLayout',margin=3)
        # Splitter two is the "main" splitter, containing splitter.
        splitter2 = splitter_class(parent)
        splitter2.setOrientation(QtCore.Qt.Vertical)
        splitter2.setObjectName("splitter_2")
        splitter2.splitterMoved.connect(self.onSplitter2Moved)
        splitter = splitter_class(splitter2)
        splitter.setOrientation(QtCore.Qt.Horizontal)
        splitter.setObjectName("splitter")
        splitter.splitterMoved.connect(self.onSplitter1Moved)
        # g.trace('splitter %s splitter2 %s' % (id(splitter),id(splitter2)))
        # Official ivars
        self.verticalLayout = vLayout
        self.splitter = splitter
        self.splitter_2 = splitter2
        self.setSizePolicy(self.splitter)
        self.verticalLayout.addWidget(self.splitter_2)
    #@+node:ekr.20110605121601.18147: *6* dw.createMenuBar
    def createMenuBar (self):

        MainWindow = self
        w = QtWidgets.QMenuBar(MainWindow)
        w.setNativeMenuBar(False)
        w.setGeometry(QtCore.QRect(0, 0, 957, 22))
        w.setObjectName("menubar")
        MainWindow.setMenuBar(w)
        # Official ivars.
        self.leo_menubar = w
    #@+node:ekr.20110605121601.18148: *6* dw.createMiniBuffer
    def createMiniBuffer (self,parent):

        # Create widgets.
        frame = self.createFrame(self.centralwidget,'minibufferFrame',
            hPolicy = QtWidgets.QSizePolicy.MinimumExpanding,
            vPolicy = QtWidgets.QSizePolicy.Fixed)
        frame.setMinimumSize(QtCore.QSize(100, 0))
        label = self.createLabel(frame,'minibufferLabel','Minibuffer:')
        class VisLineEdit(QtWidgets.QLineEdit):
            """In case user has hidden minibuffer with gui-minibuffer-hide"""
            def focusInEvent(self, event):
                self.parent().show()
                QtWidgets.QLineEdit.focusInEvent(self,event)
                    # EKR: 2014/06/28: Call the base class method.
        lineEdit = VisLineEdit(frame)
        lineEdit.setObjectName('lineEdit') # name important.

        # Pack.
        hLayout = self.createHLayout(frame,'minibufferHLayout',spacing=4)
        hLayout.setContentsMargins(3, 2, 2, 0)
        hLayout.addWidget(label)
        hLayout.addWidget(lineEdit)
        self.verticalLayout.addWidget(frame)
        label.setBuddy(lineEdit)

        # Official ivars.
        self.lineEdit = lineEdit
        # self.leo_minibuffer_frame = frame
        # self.leo_minibuffer_layout = layout
    #@+node:ekr.20110605121601.18149: *6* dw.createOutlinePane
    def createOutlinePane (self,parent):

        # Create widgets.
        treeFrame = self.createFrame(parent,'outlineFrame',
            vPolicy = QtWidgets.QSizePolicy.Expanding)
        innerFrame = self.createFrame(treeFrame,'outlineInnerFrame',
            hPolicy = QtWidgets.QSizePolicy.Preferred)

        treeWidget = self.createTreeWidget(innerFrame,'treeWidget')

        grid = self.createGrid(treeFrame,'outlineGrid')
        grid.addWidget(innerFrame, 0, 0, 1, 1)
        innerGrid = self.createGrid(innerFrame,'outlineInnerGrid')
        innerGrid.addWidget(treeWidget, 0, 0, 1, 1)

        # Official ivars...
        self.treeWidget = treeWidget

        return treeFrame
    #@+node:ekr.20110605121601.18150: *6* dw.createStatusBar
    def createStatusBar (self,parent):

        w = QtWidgets.QStatusBar(parent)
        w.setObjectName("statusbar")
        parent.setStatusBar(w)

        # Official ivars.
        self.statusBar = w
    #@+node:ekr.20110605121601.18151: *6* dw.setMainWindowOptions
    def setMainWindowOptions (self):

        MainWindow = self

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(691, 635)
        MainWindow.setDockNestingEnabled(False)
        MainWindow.setDockOptions(
            QtWidgets.QMainWindow.AllowTabbedDocks |
            QtWidgets.QMainWindow.AnimatedDocks)
    #@+node:ekr.20110605121601.18152: *5* dw.widgets
    #@+node:ekr.20110605121601.18153: *6* dw.createButton
    def createButton (self,parent,name,label):

        w = QtWidgets.QPushButton(parent)
        w.setObjectName(name)
        w.setText(self.tr(label))
        return w
    #@+node:ekr.20110605121601.18154: *6* dw.createCheckBox
    def createCheckBox (self,parent,name,label):

        w = QtWidgets.QCheckBox(parent)
        self.setName(w,name)
        w.setText(self.tr(label))
        return w
    #@+node:ekr.20110605121601.18155: *6* dw.createFrame
    def createFrame (self,parent,name,
        hPolicy=None,vPolicy=None,
        lineWidth = 1,
        shadow = QtWidgets.QFrame.Plain,
        shape = QtWidgets.QFrame.NoFrame,
    ):

        if name == 'innerBodyFrame':
            class InnerBodyFrame(QtWidgets.QFrame):
                def paintEvent(self,event):
                    # A kludge.  g.app.gui.innerBodyFrameColor is set by paint_qframe.
                    if hasattr(g.app.gui,'innerBodyFrameColor'):
                        color = g.app.gui.innerBodyFrameColor
                        painter = QtWidgets.QPainter()
                        painter.begin(w)
                        painter.fillRect(w.rect(),QtWidgets.QColor(color))
                        painter.end()
            w = InnerBodyFrame(parent)
        else:
            w = QtWidgets.QFrame(parent)
        self.setSizePolicy(w,kind1=hPolicy,kind2=vPolicy)
        w.setFrameShape(shape)
        w.setFrameShadow(shadow)
        w.setLineWidth(lineWidth)
        self.setName(w,name)
        return w
    #@+node:ekr.20110605121601.18156: *6* dw.createGrid
    def createGrid (self,parent,name,margin=0,spacing=0):

        w = QtWidgets.QGridLayout(parent)
        w.setContentsMargins(QtCore.QMargins(margin,margin,margin,margin))
            # 2014/08/24: honor margin argument.
        w.setSpacing(spacing)
        self.setName(w,name)
        return w
    #@+node:ekr.20110605121601.18157: *6* dw.createHLayout & createVLayout
    def createHLayout (self,parent,name,margin=0,spacing=0):

        hLayout = QtWidgets.QHBoxLayout(parent)
        hLayout.setSpacing(spacing)
        hLayout.setContentsMargins(QtCore.QMargins(0,0,0,0))
        self.setName(hLayout,name)
        return hLayout

    def createVLayout (self,parent,name,margin=0,spacing=0):

        vLayout = QtWidgets.QVBoxLayout(parent)
        vLayout.setSpacing(spacing)
        vLayout.setContentsMargins(QtCore.QMargins(0,0,0,0))
        self.setName(vLayout,name)
        return vLayout
    #@+node:ekr.20110605121601.18158: *6* dw.createLabel
    def createLabel (self,parent,name,label):

        w = QtWidgets.QLabel(parent)
        self.setName(w,name)
        w.setText(self.tr(label))
        return w
    #@+node:ekr.20110605121601.18159: *6* dw.createLineEdit
    def createLineEdit (self,parent,name,disabled=True):

        w = QtWidgets.QLineEdit(parent)
        w.setObjectName(name)
        w.leo_disabled = disabled # Inject the ivar.

        # g.trace(disabled,w,g.callers())
        return w
    #@+node:ekr.20110605121601.18160: *6* dw.createRadioButton
    def createRadioButton (self,parent,name,label):

        w = QtWidgets.QRadioButton(parent)
        self.setName(w,name)
        w.setText(self.tr(label))
        return w
    #@+node:ekr.20110605121601.18161: *6* dw.createStackedWidget
    def createStackedWidget (self,parent,name,
        lineWidth = 1,
        hPolicy=None,vPolicy=None,
    ):

        w = QtWidgets.QStackedWidget(parent)
        self.setSizePolicy(w,kind1=hPolicy,kind2=vPolicy)
        w.setAcceptDrops(True)
        w.setLineWidth(1)
        self.setName(w,name)
        return w
    #@+node:ekr.20110605121601.18162: *6* dw.createTabWidget
    def createTabWidget (self,parent,name,hPolicy=None,vPolicy=None):

        # w = LeoBaseTabWidget(parent)
        w = QtWidgets.QTabWidget(parent)
        tb = w.tabBar()
        # tb.setTabsClosable(True)
        self.setSizePolicy(w,kind1=hPolicy,kind2=vPolicy)
        self.setName(w,name)
        return w
    #@+node:ekr.20110605121601.18163: *6* dw.createText
    def createText (self,parent,name,
        # hPolicy=None,vPolicy=None,
        lineWidth = 0,
        shadow = QtWidgets.QFrame.Plain,
        shape = QtWidgets.QFrame.NoFrame,
    ):
        # Create a text widget.
        c = self.leo_c
        if name == 'richTextEdit' and self.useScintilla and Qsci:
            # Do this in finishCreate, when c.frame.body exists.
            w = Qsci.QsciScintilla(parent)
            self.scintilla_widget = w
        else:
            w = LeoQTextBrowser(parent,c,None)
            # self.setSizePolicy(w,kind1=hPolicy,kind2=vPolicy)
            w.setFrameShape(shape)
            w.setFrameShadow(shadow)
            w.setLineWidth(lineWidth)
            self.setName(w,name)
        return w
    #@+node:ekr.20110605121601.18164: *6* dw.createTreeWidget
    def createTreeWidget (self,parent,name):

        c = self.leo_c
        # w = QtWidgets.QTreeWidget(parent)
        w = LeoQTreeWidget(c,parent)
        self.setSizePolicy(w)

        # 12/01/07: add new config setting.
        multiple_selection = c.config.getBool('qt-tree-multiple-selection',default=True)
        if multiple_selection:
            w.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
            w.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        else:
            w.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
            w.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        w.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        w.setHeaderHidden(False)
        self.setName(w,name)
        return w
    #@+node:ekr.20110605121601.18165: *5* dw.log tabs
    #@+node:ekr.20110605121601.18167: *6* dw.createSpellTab
    def createSpellTab (self,parent):

        # MainWindow = self
        vLayout = self.createVLayout(parent,'spellVLayout',margin=2)
        spellFrame = self.createFrame(parent,'spellFrame')
        vLayout2 = self.createVLayout(spellFrame,'spellVLayout')
        grid = self.createGrid(None,'spellGrid',spacing=2)
        table = (
            ('Add',     'Add',          2,1),
            ('Find',    'Find',         2,0),
            ('Change',  'Change',       3,0),
            ('FindChange','Change,Find',3,1),
            ('Ignore',  'Ignore',       4,0),
            ('Hide',    'Hide',         4,1),
        )
        for (ivar,label,row,col) in table:
            name = 'spell_%s_button' % label
            button = self.createButton(spellFrame,name,label)
            grid.addWidget(button,row,col)
            func = getattr(self,'do_leo_spell_btn_%s' % ivar)
            button.clicked.connect(func)
            # This name is significant.
            setattr(self,'leo_spell_btn_%s' % (ivar),button)
        self.leo_spell_btn_Hide.setCheckable(False)
        spacerItem = QtWidgets.QSpacerItem(20, 40,
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        grid.addItem(spacerItem, 5, 0, 1, 1)
        listBox = QtWidgets.QListWidget(spellFrame)
        self.setSizePolicy(listBox,
            kind1 = QtWidgets.QSizePolicy.MinimumExpanding,
            kind2 = QtWidgets.QSizePolicy.Expanding)
        listBox.setMinimumSize(QtCore.QSize(0, 0))
        listBox.setMaximumSize(QtCore.QSize(150, 150))
        listBox.setObjectName("leo_spell_listBox")
        grid.addWidget(listBox, 1, 0, 1, 2)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20,
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        grid.addItem(spacerItem1, 2, 2, 1, 1)
        lab = self.createLabel(spellFrame,'spellLabel','spellLabel')
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
    #@+node:ekr.20110605121601.18166: *6* dw.createFindTab & helpers
    def createFindTab (self,parent,tab_widget):
        # g.trace('***(DynamicWindow)***',g.callers())
        c,dw = self.leo_c,self
        fc = c.findCommands
        assert not fc.ftm
        fc.ftm = ftm = FindTabManager(c)
        assert c.findCommands
        grid = self.create_find_grid(parent)
        row = 0 # The index for the present row.
        row = dw.create_find_header(grid,parent,row)
        row = dw.create_find_findbox(grid,parent,row)
        row = dw.create_find_replacebox(grid,parent,row)
        max_row2 = 1
        max_row2 = dw.create_find_checkboxes(grid,parent,max_row2,row)
        row = dw.create_find_buttons(grid,parent,max_row2,row)
        row = dw.create_help_row(grid,parent,row)
        dw.override_events()
        # Last row: Widgets that take all additional vertical space.
        w = QtWidgets.QWidget()
        grid.addWidget(w,row,0)
        grid.addWidget(w,row,1)
        grid.addWidget(w,row,2)
        grid.setRowStretch(row,100)
        # Official ivars (in addition to checkbox ivars).
        self.leo_find_widget = tab_widget # A scrollArea.
        ftm.init_widgets()
    #@+node:ekr.20131118152731.16847: *7* dw.create_find_grid
    def create_find_grid(self,parent):
        grid = self.createGrid(parent,'findGrid',margin=10,spacing=10)
        grid.setColumnStretch(0,100)
        grid.setColumnStretch(1,100)
        grid.setColumnStretch(2,10)
        grid.setColumnMinimumWidth(1,75)
        grid.setColumnMinimumWidth(2,175)
        grid.setColumnMinimumWidth(3,50)
        return grid
    #@+node:ekr.20131118152731.16849: *7* dw.create_find_header
    def create_find_header(self,grid,parent,row):
        if False:
            dw = self
            lab1 = dw.createLabel(parent,'findHeading','Find/Change Settings...')
            grid.addWidget(lab1,row,0,1,2,QtCore.Qt.AlignLeft)
                # AlignHCenter
            row += 1
        return row
    #@+node:ekr.20131118152731.16848: *7* dw.create_find_findbox
    def create_find_findbox(self,grid,parent,row):
        '''Create the Find: label and text area.'''
        c,dw = self.leo_c,self
        fc = c.findCommands
        ftm = fc.ftm
        assert ftm.find_findbox is None
        ftm.find_findbox = w = dw.createLineEdit(parent,'findPattern',disabled=fc.expert_mode)
        lab2 = self.createLabel(parent,'findLabel','Find:')
        grid.addWidget(lab2,row,0)
        grid.addWidget(w,row,1,1,2)
        row += 1
        return row
    #@+node:ekr.20131118152731.16850: *7* dw.create_find_replacebox
    def create_find_replacebox(self,grid,parent,row):
        '''Create the Replace: label and text area.'''
        c,dw = self.leo_c,self
        fc = c.findCommands
        ftm = fc.ftm
        assert ftm.find_replacebox is None
        ftm.find_replacebox = w = dw.createLineEdit(parent,'findChange',disabled=fc.expert_mode)
        lab3 = dw.createLabel(parent,'changeLabel','Replace:') # Leo 4.11.1.
        grid.addWidget(lab3,row,0)
        grid.addWidget(w,row,1,1,2)
        row += 1
        return row
    #@+node:ekr.20131118152731.16851: *7* dw.create_find_checkboxes
    def create_find_checkboxes(self,grid,parent,max_row2,row):
        '''Create check boxes and radio buttons.'''
        c,dw = self.leo_c,self
        fc = c.findCommands
        ftm = fc.ftm
        def mungeName(kind,label):
            # The returned value is the namve of an ivar.
            kind = 'check_box_' if kind == 'box' else 'radio_button_'
            name = label.replace(' ','_').replace('&','').lower()
            return '%s%s' % (kind,name)
        # Rows for check boxes, radio buttons & execution buttons...
        d = {
            'box': dw.createCheckBox,
            'rb':  dw.createRadioButton,
        }
        table = (
            # Note: the Ampersands create Alt bindings when the log pane is enable.
            # The QShortcut class is the workaround.
            # First row.
            ('box', 'whole &Word',      0,0),
            ('rb',  '&Entire outline',  0,1),
            # Second row.
            ('box', '&Ignore case',     1,0),
            ('rb',  '&Suboutline only', 1,1),
            # Third row.
            ('box', 'wrap &Around',     2,0),
            ('rb',  '&Node only',       2,1),
            # Fourth row.
            ('box', 'rege&Xp',          3,0),
            ('box', 'search &Headline', 3,1),
            # Fifth row.
            ('box', 'mark &Finds',      4,0),
            ('box', 'search &Body',     4,1),
            # Sixth row.
            ('box', 'mark &Changes',    5,0),
            # a,b,c,e,f,h,i,n,rs,w
        )
        for kind,label,row2,col in table:
            max_row2 = max(max_row2,row2)
            name = mungeName(kind,label)
            func = d.get(kind)
            assert func
            # Fix the greedy checkbox bug:
            label = label.replace('&','')
            w = func(parent,name,label)
            grid.addWidget(w,row+row2,col)
            # The the checkbox ivars in dw and ftm classes.
            assert getattr(ftm,name) is None
            setattr(ftm,name,w)
        return max_row2
        
    #@+node:ekr.20131118152731.16852: *7* dw.create_find_buttons
    def create_find_buttons(self,grid,parent,max_row2,row):
        c,dw = self.leo_c,self
        k = c.k
        ftm = c.findCommands.ftm
        def mungeName(label):
            kind = 'push-button'
            name = label.replace(' ','').replace('&','')
            return '%s%s' % (kind,name)
        # Create Buttons in column 2 (Leo 4.11.1.)
        table = (
            (0,2,'findButton','Find Next','find-next'),
            (1,2,'findPreviousButton','Find Previous','find-prev'),
            (2,2,'findAllButton','Find All','find-all'),
            (3,2,'changeButton', 'Replace','replace'),
            (4,2,'changeThenFindButton','Replace Then Find','replace-then-find'),
            (5,2,'changeAllButton','Replace All','replace-all'),
            # (6,2,'helpForFindCommands','Help','help-for-find-commands'),
        )
        # findTabHandler does not exist yet.
        for row2,col,func_name,label,cmd_name in table:
            def find_tab_button_callback(event,c=c,func_name=func_name):
                # h will exist when the Find Tab is open.
                fc = c.findCommands
                func = getattr(fc,func_name,None)
                if func: func()
                else: g.trace('* does not exist:',func_name)
            name = mungeName(label)
            # Prepend the shortcut if it exists:
            stroke = k.getShortcutForCommandName(cmd_name)
            if stroke:
                label = '%s:  %s' % (label,k.prettyPrintKey(stroke))
            if 1: # Not bad.
                w = dw.createButton(parent,name,label)
                grid.addWidget(w,row+row2,col)
            else:
                # grid.addLayout(layout,row+row2,col)
                # layout = dw.createHLayout(frame,name='button_layout',margin=0,spacing=0)
                # frame.setLayout(layout)
                frame = dw.createFrame(parent,name='button:%s' % label)
                w = dw.createButton(frame,name,label)
                grid.addWidget(frame,row+row2,col)
            # Connect the button with the command.
            w.clicked.connect(find_tab_button_callback)
            # Set the ivar.
            ivar = '%s-%s' % (cmd_name,'button')
            ivar = ivar.replace('-','_')
            assert getattr(ftm,ivar) is None
            setattr(ftm,ivar,w)
        row += max_row2
        row += 2
        return row
    #@+node:ekr.20131118152731.16853: *7* dw.create_help_row
    def create_help_row(self,grid,parent,row):
        # Help row.
        if False:
            w = self.createLabel(parent,
                'findHelp','For help: <alt-x>help-for-find-commands<return>')
            grid.addWidget(w,row,0,1,3)
            row += 1
        return row
    #@+node:ekr.20131118172620.16891: *7* dw.override_events
    def override_events(self):

        c,dw = self.leo_c,self
        fc = c.findCommands
        ftm = fc.ftm
        # Define class EventWrapper.
        #@+others
        #@+node:ekr.20131118172620.16892: *8* class EventWrapper
        class EventWrapper:

            #@+others
            #@+node:ekr.20131119204029.18406: *9* ctor
            def __init__(self,c,w,next_w,func):
                self.c = c
                self.d = self.create_d() # Keys: strokes; values: command-names.
                self.w = w
                self.next_w = next_w
                self.eventFilter = LeoQtEventFilter(c,w,'EventWrapper')
                self.func = func
                self.oldEvent = w.event
                w.event = self.wrapper
            #@+node:ekr.20131120054058.16281: *9* create_d
            def create_d(self):
                '''Create self.d dictionary.'''
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
                )
                for cmd_name in table:
                    stroke = c.k.getShortcutForCommandName(cmd_name)
                    # if not stroke: g.trace('missing',cmd_name)
                    if stroke:
                        d[stroke.s] = cmd_name
                return d
            #@+node:ekr.20131118172620.16893: *9* wrapper
            def wrapper(self,event):
                
                trace = False
                e = QtCore.QEvent
                type_ = event.type()
                # Must intercept KeyPress for events that generate FocusOut!
                if type_ == e.KeyPress:
                    return self.keyPress(event)
                elif type_ == e.KeyRelease:
                    return self.keyRelease(event)
                elif trace and  type_ not in (12,170):
                    # (5,10,11,12,110,127,128,129,170):
                    # http://qt-project.org/doc/qt-4.8/qevent.html#Type-enum
                    g.trace(type_)
                return self.oldEvent(event)
            #@+node:ekr.20131118172620.16894: *9* keyPress
            def keyPress(self,event):
                
                trace = False
                s = g.u(event.text())
                if 0: # This doesn't work.
                    eat = isinstance(self.w,(QtWidgets.QCheckBox,QtWidgets.QRadioButton))
                    g.trace('eat',eat,w)
                    if eat and s in ('\n','\r'):
                        return True
                out = s in ('\t','\r','\n')
                if trace: g.trace(out,repr(s))
                if out:
                    # Move focus to next widget.
                    if s == '\t':
                        if self.next_w:
                            if trace: g.trace('tab widget',self.next_w)
                            self.next_w.setFocus(QtCore.Qt.TabFocusReason)
                        else:
                            # Do the normal processing.
                            return self.oldEvent(event)
                    elif self.func:
                        if trace: g.trace('return func',self.func.__name__)
                        self.func()
                    return True
                else:
                    ef = self.eventFilter
                    tkKey,ch,ignore = ef.toTkKey(event)
                    stroke = ef.toStroke(tkKey,ch) # ch not used.
                    cmd_name = self.d.get(stroke)
                    if cmd_name:
                        # g.trace(cmd_name,s,tkKey,stroke,
                        self.c.k.simulateCommand(cmd_name)
                        return True
                    else:
                        # Do the normal processing.
                        return self.oldEvent(event)
            #@+node:ekr.20131118172620.16895: *9* keyRelease
            def keyRelease(self,event):
                return self.oldEvent(event)
            #@-others
            
        #@-others
        EventWrapper(c,w=ftm.find_findbox,next_w=ftm.find_replacebox,func=fc.findNextCommand)
        EventWrapper(c,w=ftm.find_replacebox,next_w=ftm.find_next_button,func=fc.findNextCommand)
        table = (
            ('findNextCommand','find-next'),
            ('findPrevCommand','find-prev'),
            ('findAll','find-all'),
            ('changeCommand','replace'),
            ('changeThenFind','replace-then-find'),
            ('changeAll','replace-all'),
        )
        for func_name,cmd_name in table:
            ivar = '%s-%s' % (cmd_name,'button')
            ivar = ivar.replace('-','_')
            w = getattr(ftm,ivar,None)
            func = getattr(fc,func_name,None)
            if w and func:
                # g.trace(cmd_name,ivar,bool(w),func and func.__name__)
                next_w = ftm.check_box_whole_word if cmd_name == 'replace-all' else None
                EventWrapper(c,w=w,next_w=next_w,func=func)
            else:
                g.trace('**oops**')
        # Finally, checkBoxMarkChanges goes back to ftm.find_findBox.
        EventWrapper(c,w=ftm.check_box_mark_changes,next_w=ftm.find_findbox,func=None)
    #@+node:ekr.20110605121601.18168: *5* dw.utils
    #@+node:ekr.20110605121601.18169: *6* dw.setName
    def setName (self,widget,name):

        if name:
            # if not name.startswith('leo_'):
                # name = 'leo_' + name
            widget.setObjectName(name)
    #@+node:ekr.20110605121601.18170: *6* dw.setSizePolicy
    def setSizePolicy (self,widget,kind1=None,kind2=None):

        if kind1 is None: kind1 = QtWidgets.QSizePolicy.Ignored
        if kind2 is None: kind2 = QtWidgets.QSizePolicy.Ignored

        sizePolicy = QtWidgets.QSizePolicy(kind1,kind2)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)

        sizePolicy.setHeightForWidth(
            widget.sizePolicy().hasHeightForWidth())

        widget.setSizePolicy(sizePolicy)
    #@+node:ekr.20110605121601.18171: *6* dw.tr
    def tr(self,s):

        if isQt5:
            # QApplication.UnicodeUTF8 no longer exists.
            return QtWidgets.QApplication.translate('MainWindow',s,None)
        else:
            return QtWidgets.QApplication.translate(
                'MainWindow',s,None,QtWidgets.QApplication.UnicodeUTF8)
    #@+node:ekr.20110605121601.18172: *4* do_leo_spell_btn_*
    def doSpellBtn(self, btn):
        getattr(self.leo_c.spellCommands.handler.tab, btn)() 

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
    #@+node:ekr.20110605121601.18173: *4* select (DynamicWindow)
    def select (self,c):

        '''Select the window or tab for c.'''

        # self is c.frame.top
        if self.leo_master:
            # A LeoTabbedTopLevel.
            self.leo_master.select(c)
        else:
            w = c.frame.body.wrapper
            g.app.gui.set_focus(c,w)

    #@+node:ekr.20110605121601.18178: *4* setGeometry (DynamicWindow)
    def setGeometry (self,rect):

        '''Set the window geometry, but only once when using the qttabs gui.'''

        # g.trace('(DynamicWindow)',rect,g.callers())

        if g.app.qt_use_tabs:
            m = self.leo_master
            assert self.leo_master

            # Only set the geometry once, even for new files.
            if not hasattr(m,'leo_geom_inited'):
                m.leo_geom_inited = True
                self.leo_master.setGeometry(rect)
                QtWidgets.QMainWindow.setGeometry(self,rect)
        else:
            QtWidgets.QMainWindow.setGeometry(self,rect)
    #@+node:ekr.20110605121601.18177: *4* setLeoWindowIcon
    def setLeoWindowIcon(self):
        """ Set icon visible in title bar and task bar """
        # xxx do not use 
        self.setWindowIcon(QtWidgets.QIcon(g.app.leoDir + "/Icons/leoapp32.png"))
    #@+node:ekr.20110605121601.18174: *4* setSplitDirection (DynamicWindow)
    def setSplitDirection (self,orientation='vertical'):

        vert = orientation and orientation.lower().startswith('v')
        h,v = QtCore.Qt.Horizontal,QtCore.Qt.Vertical

        orientation1 = h if vert else v
        orientation2 = v if vert else h

        self.splitter.setOrientation(orientation1)
        self.splitter_2.setOrientation(orientation2)

        # g.trace('vert',vert)

    #@+node:ekr.20110605121601.18175: *4* setStyleSheets & helper (DynamicWindow)
    def setStyleSheets(self):

        trace = False
        c = self.leo_c
        
        sheets = []
        for name in 'qt-gui-plugin-style-sheet', 'qt-gui-user-style-sheet':
            sheet = c.config.getData(name, strip_comments=False)
            # don't strip `#selector_name { ...` type syntax
            if sheet:
                if '\n' in sheet[0]:
                    sheet = ''.join(sheet)
                else:
                    sheet = '\n'.join(sheet)
            if sheet and sheet.strip():
                sheets.append(sheet)

        if not sheets:
            if trace: g.trace('no style sheet')
            return
        
        sheet = "\n".join(sheets)

        # store *before* expanding, so later expansions get new zoom
        c.active_stylesheet = sheet

        sheet = g.expand_css_constants(c, sheet)
        
        if trace: g.trace(len(sheet))
        w = self.leo_ui
        if g.app.qt_use_tabs:
            w = g.app.gui.frameFactory.masterFrame
        a = w.setStyleSheet(sheet or self.default_sheet())
    #@+node:ekr.20110605121601.18176: *5* defaultStyleSheet
    def defaultStyleSheet (self):

        '''Return a reasonable default style sheet.'''

        # Valid color names: http://www.w3.org/TR/SVG/types.html#ColorKeywords
        return '''\

    /* A QWidget: supports only background attributes.*/
    QSplitter::handle {

        background-color: #CAE1FF; /* Leo's traditional lightSteelBlue1 */
    }
    QSplitter {
        border-color: white;
        background-color: white;
        border-width: 3px;
        border-style: solid;
    }
    QTreeWidget {
        background-color: #ffffec; /* Leo's traditional tree color */
    }
    /* Not supported. */
    QsciScintilla {
        background-color: pink;
    }
    '''
    #@+node:ekr.20130804061744.12425: *4* setWindowTitle (DynamicWindow)
    if 0: # Override for debugging only.
        def setWindowTitle (self,s):
            g.trace('***(DynamicWindow)',s,self.parent())
            # Call the base class method.
            QtWidgets.QMainWindow.setWindowTitle(self,s)
    #@+node:ekr.20110605121601.18179: *4* splitter event handlers
    def onSplitter1Moved (self,pos,index):

        c = self.leo_c
        c.frame.secondary_ratio = self.splitterMovedHelper(
            self.splitter,pos,index)

    def onSplitter2Moved (self,pos,index):

        c = self.leo_c
        c.frame.ratio = self.splitterMovedHelper(
            self.splitter_2,pos,index)

    def splitterMovedHelper(self,splitter,pos,index):

        i,j = splitter.getRange(index)
        ratio = float(pos)/float(j-i)
        # g.trace(pos,j,ratio)
        return ratio
    #@-others

#@+node:ekr.20131117054619.16698: *3* class FindTabManager
class FindTabManager:
    
    '''A helper class for the LeoFind class.'''
    
    #@+others
    #@+node:ekr.20131117120458.16794: *4*  ftm.ctor
    def __init__ (self,c):
        # g.trace('(FindTabManager)',c.shortFileName(),g.callers())
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
    #@+node:ekr.20131117164142.16853: *4* ftm.text getters/setters
    def getFindText(self):
        return g.u(self.find_findbox.text())
        
    def getReplaceText(self):
        return g.u(self.find_replacebox.text())

    getChangeText = getReplaceText

    def setFindText(self,s):
        w = self.find_findbox
        s = g.toUnicode(s)
        w.clear()
        w.insert(s)
        
    def setReplaceText(self,s):
        w = self.find_replacebox
        s = g.toUnicode(s)
        w.clear()
        w.insert(s)
        
    setChangeText = setReplaceText
    #@+node:ekr.20131119185305.16478: *4* ftm.clear_focus & init_focus & set_entry_focus
    def clear_focus(self):

        self.entry_focus = None
        self.find_findbox.clearFocus()

    def init_focus(self):

        self.set_entry_focus()
        w = self.find_findbox
        w.setFocus()
        s = g.u(w.text())
        w.setSelection(0,len(s))
        
    def set_entry_focus(self):
        # Remember the widget that had focus, changing headline widgets
        # to the tree pane widget.  Headline widgets can disappear!
        c = self.c
        w = g.app.gui.get_focus(raw=True)
        if w != c.frame.body.wrapper.widget:
            w = c.frame.tree.treeWidget
        self.entry_focus = w
        # g.trace(w,g.app.gui.widget_name(w))
    #@+node:ekr.20131117120458.16789: *4* ftm.init_widgets (creates callbacks)
    def init_widgets(self):
        '''
        Init widgets and ivars from c.config settings.
        Create callbacks that always keep the LeoFind ivars up to date.
        '''
        c = self.c
        find = c.findCommands
        # Find/change text boxes.
        table = (
            ('find_findbox','find_text','<find pattern here>'),
            ('find_replacebox','change_text',''),
        )
        for ivar,setting_name,default in table:
            s = c.config.getString(setting_name) or default
            s = g.u(s)
            w = getattr(self,ivar)
            w.insert(s)
            if find.minibuffer_mode:
                w.clearFocus()
            else:
                w.setSelection(0,len(s))
        # Check boxes.
        table = (
            ('ignore_case',     self.check_box_ignore_case),
            ('mark_changes',    self.check_box_mark_changes),
            ('mark_finds',      self.check_box_mark_finds),
            ('pattern_match',   self.check_box_regexp),
            ('search_body',     self.check_box_search_body),
            ('search_headline', self.check_box_search_headline),
            ('whole_word',      self.check_box_whole_word),
            ('wrap',            self.check_box_wrap_around),
        )
        for setting_name,w in table:
            val = c.config.getBool(setting_name,default=False)
            # The setting name is also the name of the LeoFind ivar.
            assert hasattr(find,setting_name),setting_name
            setattr(find,setting_name,val)
            if val:
                w.toggle()
            def check_box_callback(n,setting_name=setting_name,w=w):
                # The focus has already change when this gets called.
                # focus_w = QtWidgets.QApplication.focusWidget()
                # g.trace(setting_name,val,focus_w,g.callers())
                val = w.isChecked()
                assert hasattr(find,setting_name),setting_name
                setattr(find,setting_name,val)
                ### Too kludgy: we must use an accurate setting.
                ### It would be good to have an "about to change" signal.
                ### Put focus in minibuffer if minibuffer find is in effect.
                c.bodyWantsFocusNow()
            w.stateChanged.connect(check_box_callback)
        # Radio buttons
        table = (
            ('node_only',       'node_only',        self.radio_button_node_only),
            ('entire_outline',  None,               self.radio_button_entire_outline),
            ('suboutline_only', 'suboutline_only',  self.radio_button_suboutline_only),
        )
        for setting_name,ivar,w in table:
            val = c.config.getBool(setting_name,default=False)
            # The setting name is also the name of the LeoFind ivar.
            # g.trace(setting_name,ivar,val)
            if ivar is not None:
                assert hasattr(find,setting_name),setting_name
                setattr(find,setting_name,val)
                w.toggle()
            def radio_button_callback(n,ivar=ivar,setting_name=setting_name,w=w):
                val = w.isChecked()
                find.radioButtonsChanged = True
                # g.trace(setting_name,ivar,val,g.callers())
                if ivar:
                    assert hasattr(find,ivar),ivar
                    setattr(find,ivar,val)
            w.toggled.connect(radio_button_callback)
        # Ensure one radio button is set.
        if not find.node_only and not find.suboutline_only:
            w = self.radio_button_entire_outline
            w.toggle()
    #@+node:ekr.20131117120458.16792: *4* ftm.set_radio_button
    def set_radio_button(self,name):
        '''Set the value of the radio buttons'''
        
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
    #@+node:ekr.20131117120458.16791: *4* ftm.toggle_checkbox
    def toggle_checkbox(self,checkbox_name):
        '''Toggle the value of the checkbox whose name is given.'''
        find = self.c.findCommands
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
        old_val = getattr(find,checkbox_name)
        w.toggle() # The checkbox callback toggles the ivar.
        new_val = getattr(find,checkbox_name)
        # g.trace(checkbox_name,old_val,new_val)
    #@-others
#@+node:ekr.20131115120119.17376: *3* class LeoBaseTabWidget(QtWidgets.QTabWidget)
class LeoBaseTabWidget (QtWidgets.QTabWidget):
    """Base class for all QTabWidgets in Leo."""

    #@+others
    #@+node:ekr.20131115120119.17390: *4* __init__ (LeoBaseTabWidget)
    def __init__(self,*args,**kwargs):

        self.factory = kwargs.get('factory')
        if self.factory:
            del kwargs['factory']
        QtWidgets.QTabWidget.__init__(self,*args,**kwargs)
        self.detached = []
        self.setMovable(True)
        def tabContextMenu(point):
            index = self.tabBar().tabAt(point)
            if index < 0 or (self.count() < 2 and not self.detached):
                return
            menu = QtWidgets.QMenu()
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
    #@+node:ekr.20131115120119.17391: *4* detach
    def detach(self, index):
        """detach tab (from tab's context menu)"""
        w = self.widget(index)
        name = self.tabText(index)
        self.detached.append((name, w))
        self.factory.detachTab(w)
        
        icon = g.app.gui.getImageImageFinder("application-x-leo-outline.png")
        icon = QtWidgets.QIcon(icon)
        
        w.window().setWindowIcon(icon)
        
        c = w.leo_c
       
        sheet = c.config.getData('qt-gui-plugin-style-sheet')
        
        if sheet:
            if '\n' in sheet[0]:
                sheet = ''.join(sheet)
            else:
                sheet = '\n'.join(sheet)
            c.active_stylesheet = sheet
            sheet = g.expand_css_constants(c, sheet)
            w.setStyleSheet(sheet)
        else:
            main = g.app.gui.frameFactory.masterFrame
            w.setStyleSheet(main.styleSheet())

        if platform.system() == 'Windows':
            w.move(20, 20)  # Windows (XP and 7) conspire to place the windows title bar off screen
            
        return w
    #@+node:ekr.20131115120119.17392: *4* tile
    def tile(self, index, orientation='V'):
        """detach tab and tile with parent window"""
        w = self.widget(index)
        window = w.window()
        # window.showMaximized()
        # this doesn't happen until we've returned to main even loop
        # user needs to do it before using this function
        fg = window.frameGeometry()
        geom = window.geometry()
        x,y,fw,fh = fg.x(),fg.y(),fg.width(),fg.height()
        ww, wh = geom.width(), geom.height()
        w = self.detach(index)
        if window.isMaximized():
            window.showNormal()
        if orientation == 'V':
            # follow MS Windows convention for which way is horizontal/vertical
            window.resize(ww/2, wh)
            window.move(x, y)
            w.resize(ww/2, wh)
            w.move(x+fw/2, y)
        else:
            window.resize(ww, wh/2)
            window.move(x, y)
            w.resize(ww, wh/2)
            w.move(x, y+fh/2)
    #@+node:ekr.20131115120119.17393: *4* reattach_all
    def reattach_all(self):
        """reattach all detached tabs"""
        for name, w in self.detached:
            self.addTab(w, name)
            self.factory.leoFrames[w] = w.leo_c.frame
        self.detached = []
    #@+node:ekr.20131115120119.17394: *4* delete (LeoTabbedTopLevel)
    def delete(self, w):
        """called by TabbedFrameFactory to tell us a detached tab
        has been deleted"""
        self.detached = [i for i in self.detached if i[1] != w]
    #@+node:ekr.20131115120119.17395: *4* setChanged (LeoTabbedTopLevel)
    def setChanged (self,c,changed):

        # 2011/03/01: Find the tab corresponding to c.
        trace = False and not g.unitTesting
        dw = c.frame.top # A DynamicWindow
        i = self.indexOf(dw)
        if i < 0: return
        s = self.tabText(i)
        s = g.u(s)
        # g.trace('LeoTabbedTopLevel',changed,repr(s),g.callers())
        if len(s) > 2:
            if changed:
                if not s.startswith('* '):
                    title = "* " + s
                    self.setTabText(i,title)
                    if trace: g.trace(title)
            else:
                if s.startswith('* '):
                    title = s[2:]
                    self.setTabText(i,title)
                    if trace: g.trace(title)
    #@+node:ekr.20131115120119.17396: *4* setTabName (LeoTabbedTopLevel)
    def setTabName (self,c,fileName):

        '''Set the tab name for c's tab to fileName.'''

        # Find the tab corresponding to c.
        dw = c.frame.top # A DynamicWindow
        i = self.indexOf(dw)
        if i > -1:
            self.setTabText(i,g.shortFileName(fileName))
    #@+node:ekr.20131115120119.17397: *4* closeEvent (leoTabbedTopLevel)
    def closeEvent(self, event):

        noclose = False

        # g.trace('(leoTabbedTopLevel)',g.callers())

        if g.app.save_session and g.app.sessionManager:
            g.app.sessionManager.save_snapshot()

        for c in g.app.commanders():
            res = c.exists and g.app.closeLeoWindow(c.frame)
            if not res:
                noclose = True

        if noclose:
            event.ignore()
        else:            
            event.accept()
    #@+node:ekr.20131115120119.17398: *4* select (leoTabbedTopLevel)
    def select (self,c):

        '''Select the tab for c.'''

        # g.trace(c.frame.title,g.callers())
        dw = c.frame.top # A DynamicWindow
        i = self.indexOf(dw)
        self.setCurrentIndex(i)
        # Fix bug 844953: tell Unity which menu to use.
        c.enableMenuBar()
    #@-others
#@+node:ekr.20110605121601.18180: *3* class LeoQtBody(leoFrame.LeoBody)
class LeoQtBody (leoFrame.LeoBody):
    """A class that represents the body pane of a Qt window."""
    # pylint: disable=interface-not-implemented
    #@+others
    #@+node:ekr.20110605121601.18181: *4* LeoQtBody.Birth
    #@+node:ekr.20110605121601.18182: *5* LeoQtBody.ctor
    def __init__ (self,frame,parentFrame):
        '''Ctor for LeoQtBody class.'''
        trace = False and not g.unitTesting
        # Call the base class constructor.
        leoFrame.LeoBody.__init__(self,frame,parentFrame)
        c = self.c
        assert c.frame == frame and frame.c == c
        self.set_config()
        self.set_widget()
        
        # Config stuff.
        self.trace_onBodyChanged = c.config.getBool('trace_onBodyChanged')
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
        if trace: g.trace('(qtBody)',self.widget)
    #@+node:ekr.20140901062324.18562: *6* LeoQtBody.set_config
    def set_config(self):
        '''Set configuration ivars.'''
        c = self.c
        self.useScintilla = c.config.getBool('qt-use-scintilla')
        self.unselectedBackgroundColor = c.config.getColor(
            'unselected_body_bg_color')
        self.unselectedForegroundColor = c.config.getColor(
            'unselected_body_fg_color')
    #@+node:ekr.20140901062324.18563: *6* LeoQtBody.set_widget
    def set_widget(self):
        '''Set the actual gui widget.'''
        c = self.c
        top = c.frame.top
        sw = top.leo_ui.stackedWidget
        sw.setCurrentIndex(1)
        if self.useScintilla and not Qsci:
            g.trace('Can not import Qsci: ignoring @bool qt-use-scintilla')
        if self.useScintilla and Qsci:
            self.widget = c.frame.top.scintilla_widget
                # dw.createText sets self.scintilla_widget
            self.wrapper = QScintillaWrapper(self.widget,name='body',c=c)
            self.colorizer = leoFrame.NullColorizer(c) # 2011/02/07
        else:
            self.widget = top.leo_ui.richTextEdit # A LeoQTextBrowser
            self.wrapper = QTextEditWrapper(self.widget,name='body',c=c)
            self.widget.setAcceptRichText(False)
            self.colorizer = leoColorizer.LeoQtColorizer(c,self.wrapper.widget)
    #@+node:ekr.20110605121601.18183: *6* LeoQtBody.setWrap
    def setWrap (self,p):

        if not p: return
        if self.useScintilla: return
        c = self.c
        w = c.frame.body.wrapper.widget
        wrap = g.scanAllAtWrapDirectives(c,p)
        # g.trace(wrap,w.verticalScrollBar())
        option,qt = QtGui.QTextOption,QtCore.Qt
        w.setHorizontalScrollBarPolicy(
            qt.ScrollBarAlwaysOff if wrap else qt.ScrollBarAsNeeded)
        w.setWordWrapMode(option.WordWrap if wrap else option.NoWrap)
    #@+node:ekr.20110605121601.18185: *6* LeoQtBody.get_name
    def getName (self):

        return 'body-widget'
    #@+node:ekr.20110605121601.18193: *4* LeoQtBody.Editors
    #@+node:ekr.20110605121601.18194: *5* LeoQtBody.entries
    #@+node:ekr.20110605121601.18195: *6* LeoQtBody.addEditor & helper
    # An override of leoFrame.addEditor.
    def addEditor (self,event=None):
        '''Add another editor to the body pane.'''
        trace = False and not g.unitTesting
        c,p = self.c,self.c.p
        wrapper = c.frame.body.wrapper # A QTextEditWrapper
        widget = wrapper.widget
        self.editorWidgets['1'] = wrapper
        self.totalNumberOfEditors += 1
        self.numberOfEditors += 1
        if self.totalNumberOfEditors == 2:
            # Pack the original body editor.
            self.packLabel(widget,n=1)
        name = '%d' % self.totalNumberOfEditors
        f,wrapper = self.createEditor(name)
        assert isinstance(wrapper,QTextEditWrapper),wrapper
        assert isinstance(widget,QtWidgets.QTextEdit),widget
        assert isinstance(f,QtWidgets.QFrame),f
        self.editorWidgets[name] = wrapper
        if trace: g.trace('name %s wrapper %s widget %s' % (
            name,id(wrapper),id(widget)))
        if self.numberOfEditors == 2:
            # Inject the ivars into the first editor.
            # The name of the last editor need not be '1'
            d = self.editorWidgets
            keys = list(d.keys())
            old_name = keys[0]
            old_wrapper = d.get(old_name)
            old_w = old_wrapper.widget
            self.injectIvars(f,old_name,p,old_wrapper)
            self.updateInjectedIvars (old_w,p)
            self.selectLabel(old_wrapper) # Immediately create the label in the old editor.
        # Switch editors.
        c.frame.body.bodyCtrl = wrapper
        self.selectLabel(wrapper)
        self.selectEditor(wrapper)
        self.updateEditors()
        c.bodyWantsFocus()
    #@+node:ekr.20110605121601.18196: *7* LeoQtBody.createEditor
    def createEditor (self,name):

        c = self.c ; p = c.p
        f = c.frame.top.leo_ui.leo_body_inner_frame
            # Valid regardless of qtGui.useUI
        # Step 1: create the editor.
        # w = QtWidgets.QTextBrowser(f)
        w = LeoQTextBrowser(f,c,self)
        w.setObjectName('richTextEdit') # Will be changed later.
        wrapper = QTextEditWrapper(w,name='body',c=c)
        self.packLabel(w)
        # Step 2: inject ivars, set bindings, etc.
        self.injectIvars(f,name,p,wrapper)
        self.updateInjectedIvars(w,p)
        wrapper.setAllText(p.b)
        wrapper.see(0)
        # self.createBindings(w=wrapper)
        c.k.completeAllBindingsForWidget(wrapper)
        self.recolorWidget(p,wrapper)
        return f,wrapper
    #@+node:ekr.20110605121601.18197: *6* LeoQtBody.assignPositionToEditor
    def assignPositionToEditor (self,p):
        '''Called *only* from tree.select to select the present body editor.'''
        c = self.c
        wrapper = c.frame.body.bodyCtrl
        w = wrapper.widget
        self.updateInjectedIvars(w,p)
        self.selectLabel(wrapper)
        # g.trace('===',id(w),w.leo_chapter,w.leo_p.h)
    #@+node:ekr.20110605121601.18198: *6* LeoQtBody.cycleEditorFocus
    # Use the base class method.

    # def cycleEditorFocus (self,event=None):

        # '''Cycle keyboard focus between the body text editors.'''

        # c = self.c ; d = self.editorWidgets
        # w = c.frame.body.bodyCtrl
        # values = list(d.values())
        # if len(values) > 1:
            # i = values.index(w) + 1
            # if i == len(values): i = 0
            # w2 = list(d.values())[i]
            # assert(w!=w2)
            # self.selectEditor(w2)
            # c.frame.body.bodyCtrl = w2

    #@+node:ekr.20110605121601.18199: *6* LeoQtBody.deleteEditor
    def deleteEditor (self,event=None):
        '''Delete the presently selected body text editor.'''
        trace = False and not g.unitTesting
        c = self.c ; d = self.editorWidgets
        wrapper = c.frame.body.bodyCtrl
        w = wrapper.widget
        # This seems not to be a valid assertion.
        # assert wrapper == d.get(name),'wrong wrapper'
        assert isinstance(wrapper,QTextEditWrapper),wrapper
        assert isinstance(w,QtWidgets.QTextEdit),w
        if len(list(d.keys())) <= 1: return
        name = w.leo_name if hasattr(w,'leo_name') else '1'
            # Defensive programming.
        # At present, can not delete the first column.
        if name == '1':
            g.warning('can not delete leftmost editor')
            return
        # Actually delete the widget.
        if trace: g.trace('**delete name %s id(wrapper) %s id(w) %s' % (
            name,id(wrapper),id(w)))
        del d [name]
        f = c.frame.top.leo_ui.leo_body_inner_frame
        layout = f.layout()
        for z in (w,w.leo_label):
            if z: # 2011/11/12
                self.unpackWidget(layout,z)
        w.leo_label = None # 2011/11/12
        # Select another editor.
        new_wrapper = list(d.values())[0]
        if trace: g.trace(wrapper,new_wrapper)
        self.numberOfEditors -= 1
        if self.numberOfEditors == 1:
            w = new_wrapper.widget
            if w.leo_label: # 2011/11/12
                self.unpackWidget(layout,w.leo_label)
                w.leo_label = None # 2011/11/12
        self.selectEditor(new_wrapper)
    #@+node:ekr.20110605121601.18200: *6* LeoQtBody.findEditorForChapter
    def findEditorForChapter (self,chapter,p):

        '''Return an editor to be assigned to chapter.'''

        trace = False and not g.unitTesting
        c = self.c ; d = self.editorWidgets
        values = list(d.values())

        # First, try to match both the chapter and position.
        if p:
            for w in values:
                if (
                    hasattr(w,'leo_chapter') and w.leo_chapter == chapter and
                    hasattr(w,'leo_p') and w.leo_p and w.leo_p == p
                ):
                    if trace: g.trace('***',id(w),'match chapter and p',p.h)
                    return w

        # Next, try to match just the chapter.
        for w in values:
            if hasattr(w,'leo_chapter') and w.leo_chapter == chapter:
                if trace: g.trace('***',id(w),'match only chapter',p.h)
                return w

        # As a last resort, return the present editor widget.
        if trace: g.trace('***',id(self.bodyCtrl),'no match',p.h)
        return c.frame.body.bodyCtrl
    #@+node:ekr.20110605121601.18201: *6* LeoQtBody.select/unselectLabel
    def unselectLabel (self,wrapper):

        pass
        # self.createChapterIvar(wrapper)

    def selectLabel (self,wrapper):

        c = self.c
        w = wrapper.widget
        lab = hasattr(w,'leo_label') and w.leo_label
        if lab:
            lab.setEnabled(True)
            lab.setText(c.p.h)
            lab.setEnabled(False)
    #@+node:ekr.20110605121601.18202: *6* LeoQtBody.selectEditor & helpers
    selectEditorLockout = False

    def selectEditor(self,wrapper):
        '''Select editor w and node w.leo_p.'''
        trace = False and not g.unitTesting
        verbose = False
        c = self.c ; bodyCtrl = c.frame.body.bodyCtrl
        if not wrapper: return bodyCtrl
        if self.selectEditorLockout:
            if trace: g.trace('**busy')
            return
        w = wrapper.widget
        assert isinstance(wrapper,(QScintillaWrapper,QTextEditWrapper)),wrapper
        if Qsci:
            assert isinstance(w,(Qsci.QsciScintilla,QtWidgets.QTextEdit)),w
        else:
            assert isinstance(w,QtWidgets.QTextEdit),w
        def report(s):
            g.trace('*** %9s wrapper %s w %s %s' % (
                s,id(wrapper),id(w),c.p.h))
        if wrapper and wrapper == bodyCtrl:
            self.deactivateEditors(wrapper)
            if hasattr(w,'leo_p') and w.leo_p and w.leo_p != c.p:
                if trace: report('select')
                c.selectPosition(w.leo_p)
                c.bodyWantsFocus()
            elif trace and verbose: report('no change')
            return
        try:
            val = None
            self.selectEditorLockout = True
            val = self.selectEditorHelper(wrapper)
        finally:
            self.selectEditorLockout = False
        return val # Don't put a return in a finally clause.
    #@+node:ekr.20110605121601.18203: *7* LeoQtBody.selectEditorHelper
    def selectEditorHelper (self,wrapper):

        trace = False and not g.unitTesting
        c = self.c
        assert isinstance(wrapper,QTextEditWrapper),wrapper
        w = wrapper.widget
        assert isinstance(w,QtWidgets.QTextEdit),w
        if not w.leo_p:
            g.trace('no w.leo_p') 
            return 'break'
        # The actual switch.
        self.deactivateEditors(wrapper)
        self.recolorWidget (w.leo_p,wrapper) # switches colorizers.
        # g.trace('c.frame.body',c.frame.body)
        # g.trace('c.frame.body.bodyCtrl',c.frame.body.bodyCtrl)
        # g.trace('wrapper',wrapper)
        c.frame.body.bodyCtrl = wrapper
        c.frame.body.widget = wrapper # Major bug fix: 2011/04/06
        w.leo_active = True
        self.switchToChapter(wrapper)
        self.selectLabel(wrapper)
        if not self.ensurePositionExists(w):
            return g.trace('***** no position editor!')
        if not (hasattr(w,'leo_p') and w.leo_p):
            return g.trace('***** no w.leo_p',w)
        p = w.leo_p
        assert p,p
        if trace: g.trace('wrapper %s old %s p %s' % (
            id(wrapper),c.p.h,p.h))
        c.expandAllAncestors(p)
        c.selectPosition(p)
            # Calls assignPositionToEditor.
            # Calls p.v.restoreCursorAndScroll.
        c.redraw()
        c.recolor_now()
        c.bodyWantsFocus()
    #@+node:ekr.20110605121601.18205: *6* LeoQtBody.updateEditors
    # Called from addEditor and assignPositionToEditor

    def updateEditors (self):

        c = self.c ; p = c.p ; body = p.b
        d = self.editorWidgets
        if len(list(d.keys())) < 2: return # There is only the main widget

        w0 = c.frame.body.bodyCtrl
        i,j = w0.getSelectionRange()
        ins = w0.getInsertPoint()
        sb0 = w0.widget.verticalScrollBar()
        pos0 = sb0.sliderPosition()
        for key in d:
            wrapper = d.get(key)
            w = wrapper.widget
            v = hasattr(w,'leo_p') and w.leo_p.v
            if v and v == p.v and w != w0:
                sb = w.verticalScrollBar()
                pos = sb.sliderPosition()
                wrapper.setAllText(body)
                self.recolorWidget(p,wrapper)
                sb.setSliderPosition(pos)

        c.bodyWantsFocus()
        w0.setSelectionRange(i,j,insert=ins)
            # 2011/11/21: bug fix: was ins=ins
        # g.trace(pos0)
        sb0.setSliderPosition(pos0)
    #@+node:ekr.20110605121601.18206: *5* LeoQtBody.utils
    #@+node:ekr.20110605121601.18207: *6* LeoQtBody.computeLabel
    def computeLabel (self,w):

        if hasattr(w,'leo_label') and w.leo_label: # 2011/11/12
            s = w.leo_label.text()
        else:
            s = ''

        if hasattr(w,'leo_chapter') and w.leo_chapter:
            s = '%s: %s' % (w.leo_chapter,s)

        return s
    #@+node:ekr.20110605121601.18208: *6* LeoQtBody.createChapterIvar
    def createChapterIvar (self,w):

        c = self.c ; cc = c.chapterController

        if hasattr(w,'leo_chapter') and w.leo_chapter:
            pass
        elif cc and self.use_chapters:
            w.leo_chapter = cc.getSelectedChapter()
        else:
            w.leo_chapter = None
    #@+node:ekr.20110605121601.18209: *6* LeoQtBody.deactivateEditors
    def deactivateEditors(self,wrapper):

        '''Deactivate all editors except wrapper's editor.'''

        trace = False and not g.unitTesting
        d = self.editorWidgets

        # Don't capture ivars here! assignPositionToEditor keeps them up-to-date. (??)
        for key in d:
            wrapper2 = d.get(key)
            w2 = wrapper2.widget
            if hasattr(w2,'leo_active'):
                active = w2.leo_active
            else:
                active = True
            if wrapper2 != wrapper and active:
                w2.leo_active = False
                self.unselectLabel(wrapper2)
                if trace: g.trace(w2)
                self.onFocusOut(w2)
    #@+node:ekr.20110605121601.18210: *6* LeoQtBody.ensurePositionExists
    def ensurePositionExists(self,w):
        '''Return True if w.leo_p exists or can be reconstituted.'''
        trace = False and not g.unitTesting
        c = self.c
        if c.positionExists(w.leo_p):
            return True
        if trace: g.trace('***** does not exist',w.leo_name)
        for p2 in c.all_unique_positions():
            if p2.v and p2.v == w.leo_p.v:
                if trace: g.trace(p2.h)
                w.leo_p = p2.copy()
                return True
        # This *can* happen when selecting a deleted node.
        w.leo_p = c.p.copy()
        return False
    #@+node:ekr.20110605121601.18211: *6* LeoQtBody.injectIvars
    def injectIvars (self,parentFrame,name,p,wrapper):

        trace = False and not g.unitTesting
        w = wrapper.widget
        assert isinstance(wrapper,QTextEditWrapper),wrapper
        assert isinstance(w,QtWidgets.QTextEdit),w
        if trace: g.trace(w)
        # Inject ivars
        if name == '1':
            w.leo_p = None # Will be set when the second editor is created.
        else:
            w.leo_p = p.copy()
        w.leo_active = True
        w.leo_bodyBar = None
        w.leo_bodyXBar = None
        w.leo_chapter = None
        # w.leo_colorizer = None # Set in LeoQtColorizer ctor.
        w.leo_frame = parentFrame
        # w.leo_label = None # Injected by packLabel.
        w.leo_name = name
        w.leo_wrapper = wrapper
    #@+node:ekr.20110605121601.18212: *6* LeoQtBody.packLabel
    def packLabel (self,w,n=None):

        trace = False and not g.unitTesting
        c = self.c
        f = c.frame.top.leo_ui.leo_body_inner_frame
            # Valid regardless of qtGui.useUI

        if n is None:n = self.numberOfEditors
        layout = f.layout()
        f.setObjectName('editorFrame')

        # Create the text: to do: use stylesheet to set font, height.
        lab = QtWidgets.QLineEdit(f)
        lab.setObjectName('editorLabel')
        lab.setText(c.p.h)

        # Pack the label and the text widget.
        # layout.setHorizontalSpacing(4)
        layout.addWidget(lab,0,max(0,n-1),QtCore.Qt.AlignVCenter)
        layout.addWidget(w,1,max(0,n-1))
        layout.setRowStretch(0,0)
        layout.setRowStretch(1,1) # Give row 1 as much as possible.

        w.leo_label = lab # Inject the ivar.
        if trace: g.trace('w.leo_label',w,lab)
    #@+node:ekr.20110605121601.18213: *6* LeoQtBody.recolorWidget
    def recolorWidget (self,p,wrapper):

        trace = False and not g.unitTesting
        c = self.c
        # Save.
        old_wrapper = c.frame.body.bodyCtrl
        c.frame.body.bodyCtrl = wrapper
        w = wrapper.widget
        if not hasattr(w,'leo_colorizer'):
            if trace: g.trace('*** creating colorizer for',w)
            leoColorizer.LeoQtColorizer(c,w) # injects w.leo_colorizer
            assert hasattr(w,'leo_colorizer'),w
        c.frame.body.colorizer = w.leo_colorizer
        if trace: g.trace(w,c.frame.body.colorizer)
        try:
            # c.recolor_now(interruptable=False) # Force a complete recoloring.
            c.frame.body.colorizer.colorize(p,incremental=False,interruptable=False)
        finally:
            # Restore.
            c.frame.body.bodyCtrl = old_wrapper
    #@+node:ekr.20110605121601.18214: *6* LeoQtBody.switchToChapter
    def switchToChapter (self,w):

        '''select w.leo_chapter.'''

        trace = False and not g.unitTesting
        c = self.c ; cc = c.chapterController

        if hasattr(w,'leo_chapter') and w.leo_chapter:
            chapter = w.leo_chapter
            name = chapter and chapter.name
            oldChapter = cc.getSelectedChapter()
            if chapter != oldChapter:
                if trace: g.trace('***old',oldChapter.name,'new',name,w.leo_p)
                cc.selectChapterByName(name)
                c.bodyWantsFocus()
    #@+node:ekr.20110605121601.18215: *6* LeoQtBody.updateInjectedIvars
    def updateInjectedIvars (self,w,p):

        trace = False and not g.unitTesting
        if trace: g.trace('w %s len(p.b) %s %s' % (
            id(w),len(p.b),p.h),g.callers(5))
        c = self.c
        cc = c.chapterController
        if Qsci:
            assert isinstance(w,(Qsci.QsciScintilla,QtWidgets.QTextEdit)),w
        else:
            assert isinstance(w,QtWidgets.QTextEdit),w
        if cc and self.use_chapters:
            w.leo_chapter = cc.getSelectedChapter()
        else:
            w.leo_chapter = None
        w.leo_p = p.copy()
    #@+node:ekr.20110605121601.18216: *6* LeoQtBody.unpackWidget
    def unpackWidget (self,layout,w):

        trace = False and not g.unitTesting

        if trace: g.trace(w)

        index = layout.indexOf(w)
        item = layout.itemAt(index)
        item.setGeometry(QtCore.QRect(0,0,0,0))
        layout.removeItem(item)


    #@+node:ekr.20110605121601.18223: *4* LeoQtBody.Event handlers
    #@+node:ekr.20110930174206.15472: *5* LeoQtBody.onFocusIn
    def onFocusIn (self,obj):
        '''Handle a focus-in event in the body pane.'''
        trace = False and not g.unitTesting
        if trace: g.trace(str(obj.objectName()))
        # Update history only in leoframe.tree.select.
        # c.NodeHistory.update(c.p)
        if obj.objectName() == 'richTextEdit':
            wrapper = hasattr(obj,'leo_wrapper') and obj.leo_wrapper
            if wrapper and wrapper != self.bodyCtrl:
                self.selectEditor(wrapper)
            self.onFocusColorHelper('focus-in',obj)
            if hasattr(obj,'leo_copy_button') and obj.leo_copy_button:
                # g.trace('read only text')
                obj.setReadOnly(True)
            else:
                # g.trace('read/write text')
                obj.setReadOnly(False)
            obj.setFocus() # Weird, but apparently necessary.
    #@+node:ekr.20110930174206.15473: *5* LeoQtBody.onFocusOut
    def onFocusOut (self,obj):
        '''Handle a focus-out event in the body pane.'''
        trace = False and not g.unitTesting
        if trace: g.trace(str(obj.objectName()))
        # Apparently benign.
        if obj.objectName() == 'richTextEdit':
            self.onFocusColorHelper('focus-out',obj)
            obj.setReadOnly(True)
    #@+node:ekr.20110605121601.18224: *5* LeoQtBody.qtBody.onFocusColorHelper (revised)
    # badFocusColors = []

    def onFocusColorHelper(self,kind,obj):
        '''Handle changes of style when focus changes.'''
        c,vc = self.c,self.c.vimCommands
        if vc and c.vim_mode:
            try:
                assert kind in ('focus-in','focus-out')
                w = c.frame.body.wrapper.widget
                vc.set_border(w=w,activeFlag=kind=='focus-in')
            except Exception:
                # g.es_exception()
                pass
    #@+node:ekr.20110605121601.18191: *4* LeoQtBody.High-level interface
    # The required high-level interface.
    def appendText (self,s):                return self.wrapper.appendText(s)
    def clipboard_append(self,s):           return self.wrapper.clipboard_append(s)
    def clipboard_clear(self):              return self.wrapper.clipboard_clear()
    def delete(self,i,j=None):              self.wrapper.delete(i,j)
    def deleteTextSelection (self):         return self.wrapper.deleteTextSelection()
    def flashCharacter(self,i,
        bg='white',fg='red',
        flashes=3,delay=75):                return self.wrapper(i,bg,fg,flashes,delay)
    def get(self,i,j=None):                 return self.wrapper.get(i,j)
    def getAllText (self):                  return self.wrapper.getAllText()
    def getFocus (self):                    return self.wrapper.getFocus()
    def getInsertPoint(self):               return self.wrapper.getInsertPoint()
    def getSelectedText (self):             return self.wrapper.getSelectedText()
    def getSelectionRange(self):            return self.wrapper.getSelectionRange()
    def getYScrollPosition (self):          return self.wrapper.getYScrollPosition()
    def hasSelection (self):                return self.wrapper.hasSelection()
    def insert(self,i,s):                   return self.wrapper.insert(i,s)
    def replace (self,i,j,s):               self.wrapper.replace (i,j,s)
    def rowColToGuiIndex (self,s,row,col):  return self.wrapper.rowColToGuiIndex(s,row,col)
    def see(self,index):                    return self.wrapper.see(index)
    def seeInsertPoint(self):               return self.wrapper.seeInsertPoint()
    def selectAllText (self,insert=None):   self.wrapper.selectAllText(insert)
    # def setAllText (self,s,new_p=None):     return self.wrapper.setAllText(s,new_p=new_p)
    def setAllText(self,s):                 return self.wrapper.setAllText(s)
    def setBackgroundColor (self,color):    return self.wrapper.setBackgroundColor(color)
    def setFocus (self):                    return self.wrapper.setFocus()
    def setForegroundColor (self,color):    return self.wrapper.setForegroundColor(color)
    def setInsertPoint (self,pos,s=None):   return self.wrapper.setInsertPoint(pos,s=s)
    def setSelectionRange (self,i,j,insert=None):
        self.wrapper.setSelectionRange(i,j,insert=insert)
    def setYScrollPosition (self,i):        return self.wrapper.setYScrollPosition(i)
    def tag_configure(self,colorName,**keys):pass
    def toPythonIndex(self,index):          return self.wrapper.toPythonIndex(index)
    def toPythonIndexRowCol(self,index):    return self.wrapper.toPythonIndexRowCol(index)

    set_focus = setFocus
    toGuiIndex = toPythonIndex
    #@+node:ekr.20110605121601.18190: *4* LeoQtBody.oops (no longer used)
    # def oops (self):
        # g.trace('qtBody',g.callers(3))
    #@+node:ekr.20110605121601.18217: *4* LeoQtBody.Renderer panes
    #@+node:ekr.20110605121601.18218: *5* LeoQtBody.hideCanvasRenderer
    def hideCanvasRenderer (self,event=None):
        '''Hide canvas pane.'''
        trace = False and not g.unitTesting
        c = self.c ; d = self.editorWidgets
        wrapper = c.frame.body.bodyCtrl
        w = wrapper.widget
        name = w.leo_name
        assert name
        assert wrapper == d.get(name),'wrong wrapper'
        assert isinstance(wrapper,QTextEditWrapper),wrapper
        assert isinstance(w,QtWidgets.QTextEdit),w
        if len(list(d.keys())) <= 1: return
        # At present, can not delete the first column.
        if name == '1':
            g.warning('can not delete leftmost editor')
            return
        # Actually delete the widget.
        if trace: g.trace('**delete name %s id(wrapper) %s id(w) %s' % (
            name,id(wrapper),id(w)))
        del d [name]
        f = c.frame.top.leo_ui.leo_body_inner_frame
        layout = f.layout()
        for z in (w,w.leo_label):
            if z: # 2011/11/12
                self.unpackWidget(layout,z)
        w.leo_label = None # 2011/11/12
        # Select another editor.
        new_wrapper = list(d.values())[0]
        if trace: g.trace(wrapper,new_wrapper)
        self.numberOfEditors -= 1
        if self.numberOfEditors == 1:
            w = new_wrapper.widget
            if w.leo_label: # 2011/11/12
                self.unpackWidget(layout,w.leo_label)
                w.leo_label = None # 2011/11/12
        self.selectEditor(new_wrapper)
    #@+node:ekr.20110605121601.18219: *5* LeoQtBody.hideTextRenderer
    def hideCanvas (self,event=None):
        '''Hide canvas pane.'''
        trace = False and not g.unitTesting
        c = self.c ; d = self.editorWidgets
        wrapper = c.frame.body.bodyCtrl
        w = wrapper.widget
        name = w.leo_name
        assert name
        assert wrapper == d.get(name),'wrong wrapper'
        assert isinstance(wrapper,QTextEditWrapper),wrapper
        assert isinstance(w,QtWidgets.QTextEdit),w
        if len(list(d.keys())) <= 1: return
        # At present, can not delete the first column.
        if name == '1':
            g.warning('can not delete leftmost editor')
            return
        # Actually delete the widget.
        if trace: g.trace('**delete name %s id(wrapper) %s id(w) %s' % (
            name,id(wrapper),id(w)))
        del d [name]
        f = c.frame.top.leo_ui.leo_body_inner_frame
        layout = f.layout()
        for z in (w,w.leo_label):
            if z: # 2011/11/12
                self.unpackWidget(layout,z)
        w.leo_label = None  # 2011/11/12
        # Select another editor.
        new_wrapper = list(d.values())[0]
        if trace: g.trace(wrapper,new_wrapper)
        self.numberOfEditors -= 1
        if self.numberOfEditors == 1:
            w = new_wrapper.widget
            if w.leo_label:  # 2011/11/12
                self.unpackWidget(layout,w.leo_label)
                w.leo_label = None # 2011/11/1
        self.selectEditor(new_wrapper)
    #@+node:ekr.20110605121601.18220: *5* LeoQtBody.packRenderer
    def packRenderer (self,f,name,w):

        n = max(1,self.numberOfEditors)
        assert isinstance(f,QtWidgets.QFrame),f
        layout = f.layout()
        f.setObjectName('%s Frame' % name)
        # Create the text: to do: use stylesheet to set font, height.
        lab = QtWidgets.QLineEdit(f)
        lab.setObjectName('%s Label' % name)
        lab.setText(name)
        # Pack the label and the widget.
        layout.addWidget(lab,0,max(0,n-1),QtCore.Qt.AlignVCenter)
        layout.addWidget(w,1,max(0,n-1))
        layout.setRowStretch(0,0)
        layout.setRowStretch(1,1) # Give row 1 as much as possible.
        return lab
    #@+node:ekr.20110605121601.18221: *5* LeoQtBody.showCanvasRenderer
    # An override of leoFrame.addEditor.

    def showCanvasRenderer (self,event=None):

        '''Show the canvas area in the body pane, creating it if necessary.'''

        # bodyCtrl = self.c.frame.body.bodyCtrl # A QTextEditWrapper
        c = self.c
        f = c.frame.top.leo_ui.leo_body_inner_frame
        assert isinstance(f,QtWidgets.QFrame),f
        if not self.canvasRenderer:
            name = 'Graphics Renderer'
            self.canvasRenderer = w = QtWidgets.QGraphicsView(f)
            w.setObjectName(name)
        if not self.canvasRendererVisible:
            self.canvasRendererLabel = self.packRenderer(f,name,w)
            self.canvasRendererVisible = True
    #@+node:ekr.20110605121601.18222: *5* LeoQtBody.showTextRenderer
    # An override of leoFrame.addEditor.

    def showTextRenderer (self,event=None):

        '''Show the canvas area in the body pane, creating it if necessary.'''

        c = self.c
        f = c.frame.top.leo_ui.leo_body_inner_frame
        assert isinstance(f,QtWidgets.QFrame),f

        if not self.textRenderer:
            name = 'Text Renderer'
            self.textRenderer = w = LeoQTextBrowser(f,c,self)
            w.setObjectName(name)
            self.textRendererWrapper = QTextEditWrapper(
                w,name='text-renderer',c=c)

        if not self.textRendererVisible:
            self.textRendererLabel = self.packRenderer(f,name,w)
            self.textRendererVisible = True
    #@-others
#@+node:ekr.20110605121601.18245: *3* class LeoQtFrame
class LeoQtFrame (leoFrame.LeoFrame):

    """A class that represents a Leo window rendered in qt."""

    #@+others
    #@+node:ekr.20110605121601.18246: *4*  Birth & Death (qtFrame)
    #@+node:ekr.20110605121601.18247: *5* __init__ (qtFrame)
    def __init__(self,c,title,gui):

        # Init the base class.
        leoFrame.LeoFrame.__init__(self,c,gui)

        assert self.c == c
        leoFrame.LeoFrame.instances += 1 # Increment the class var.

        # Official ivars...
        self.iconBar = None
        self.iconBarClass = self.QtIconBarClass
        self.initComplete = False # Set by initCompleteHint().
        self.minibufferVisible = True
        self.statusLineClass = self.QtStatusLineClass
        self.title = title

        # Config settings.
        self.trace_status_line = c.config.getBool('trace_status_line')
        self.use_chapters      = c.config.getBool('use_chapters')
        self.use_chapter_tabs  = c.config.getBool('use_chapter_tabs')

        self.setIvars()

    #@+node:ekr.20110605121601.18248: *6* setIvars (qtFrame)
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
    #@+node:ekr.20110605121601.18249: *5* __repr__ (qtFrame)
    def __repr__ (self):

        return "<LeoQtFrame: %s>" % self.title
    #@+node:ekr.20110605121601.18250: *5* qtFrame.finishCreate & helpers
    def finishCreate (self):

        trace = (False or g.trace_startup) and not g.unitTesting
        if trace: print('qtFrame.finishCreate')
        f = self
        c = self.c
        assert c
        # returns DynamicWindow
        f.top = g.app.gui.frameFactory.createFrame(f)
        f.createIconBar() # A base class method.
        f.createSplitterComponents()
        f.createStatusLine() # A base class method.
        f.createFirstTreeNode() # Call the base-class method.
        f.menu = LeoQtMenu(c,f,label='top-level-menu')
        g.app.windowList.append(f)
        f.miniBufferWidget = QMinibufferWrapper(c)
        c.bodyWantsFocus()
    #@+node:ekr.20110605121601.18251: *6* createSplitterComponents (qtFrame)
    def createSplitterComponents (self):

        f = self ; c = f.c

        f.tree  = LeoQtTree(c,f)
        f.log   = LeoQtLog(f,None)
        f.body  = LeoQtBody(f,None)

        f.splitVerticalFlag,f.ratio,f.secondary_ratio = f.initialRatios()
        f.resizePanesToRatio(f.ratio,f.secondary_ratio)
    #@+node:ekr.20110605121601.18252: *5* initCompleteHint
    def initCompleteHint (self):

        '''A kludge: called to enable text changed events.'''

        self.initComplete = True
        # g.trace(self.c)
    #@+node:ekr.20110605121601.18253: *5* Destroying the qtFrame
    #@+node:ekr.20110605121601.18254: *6* destroyAllObjects
    def destroyAllObjects (self):

        """Clear all links to objects in a Leo window."""

        frame = self ; c = self.c

        # g.printGcAll()

        # Do this first.
        #@+<< clear all vnodes in the tree >>
        #@+node:ekr.20110605121601.18255: *7* << clear all vnodes in the tree>>
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
            tree = frame.tree ; body = self.body
            g.clearAllIvars(body.colorizer)
            g.clearAllIvars(body)
            g.clearAllIvars(tree)

    #@+node:ekr.20110605121601.18256: *6* destroySelf (qtFrame)
    def destroySelf (self):

        # Remember these: we are about to destroy all of our ivars!
        c,top = self.c,self.top 

        g.app.gui.frameFactory.deleteFrame(top)
        # Indicate that the commander is no longer valid.
        c.exists = False

        if 0: # We can't do this unless we unhook the event filter.
            # Destroys all the objects of the commander.
            self.destroyAllObjects()

        c.exists = False # Make sure this one ivar has not been destroyed.

        # g.trace('qtFrame',c,g.callers(4))
        top.close()


    #@+node:ekr.20110605121601.18257: *4* class QtStatusLineClass (qtFrame)
    class QtStatusLineClass:

        '''A class representing the status line.'''

        #@+others
        #@+node:ekr.20110605121601.18258: *5* ctor (qtFrame)
        def __init__ (self,c,parentFrame):

            self.c = c
            self.statusBar = c.frame.top.statusBar
            self.lastFcol= 0
            self.lastRow = 0
            self.lastCol = 0

            # Create the text widgets.
            self.textWidget1 = w1 = QtWidgets.QLineEdit(self.statusBar)
            self.textWidget2 = w2 = QtWidgets.QLineEdit(self.statusBar)
            w1.setObjectName('status1')
            w2.setObjectName('status2')
            splitter = QtWidgets.QSplitter()
            self.statusBar.addWidget(splitter, True)
            
            sizes = c.config.getString('status_line_split_sizes') or '1 2'
            sizes = [int(i) for i in sizes.replace(',', ' ').split()]
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
                verbose = c.status_line_unl_mode=='canonical'
                w2.setText(c.p.get_UNL(with_proto=verbose, with_index=verbose))

            def add_item(event, w2=w2):
                menu = w2.createStandardContextMenu()
                menu.addSeparator()
                menu.addAction("Toggle UNL mode", cycle_unl_mode)
                menu.exec_(event.globalPos())

            w2.contextMenuEvent = add_item

            self.put('')
            self.update()
            #X c.frame.top.setStyleSheets()
        #@+node:ekr.20110605121601.18260: *5* clear, get & put/1
        def clear (self):
            self.put('')

        def get (self):
            return self.textWidget2.text()

        def put(self,s,color=None):
            self.put_helper(s,self.textWidget2)

        def put1(self,s,color=None):
            self.put_helper(s,self.textWidget1)

        def put_helper(self,s,w):
            w.setText(s)
        #@+node:ekr.20110605121601.18261: *5* update (QtStatusLineClass)
        def update (self):

            if g.app.killed: return
            c = self.c ; body = c.frame.body
            # te is a QTextEdit.
            # 2010/02/19: Fix bug 525090
            # An added editor window doesn't display line/col
            te = body.widget
            if isinstance(te,QtGui.QTextEdit):
                cr = te.textCursor()
                bl = cr.block()
                col = cr.columnNumber()
                row = bl.blockNumber() + 1
                line = bl.text()
                if col > 0:
                    s2 = line[0:col]        
                    col = g.computeWidth (s2,c.tab_width)
                fcol = col + c.currentPosition().textOffset()
                # g.trace('fcol',fcol,'te',id(te),g.callers(2))
                # g.trace('c.frame.body.bodyCtrl',body.bodyCtrl)
                # g.trace(row,col,fcol)
            else:
                row,col,fcol = 0,0,0
            self.put1(
                "line: %d, col: %d, fcol: %d" % (row,col,fcol))
            self.lastRow = row
            self.lastCol = col
            self.lastFcol = fcol
        #@-others
    #@+node:ekr.20110605121601.18262: *4* class QtIconBarClass
    class QtIconBarClass:

        '''A class representing the singleton Icon bar'''

        #@+others
        #@+node:ekr.20110605121601.18263: *5*  ctor (QtIconBarClass)
        def __init__ (self,c,parentFrame):

            # g.trace('(QtIconBarClass)')

            self.c = c
            self.chapterController = None
            self.parentFrame = parentFrame
            self.toolbar = self
            self.w = c.frame.top.iconBar # A QToolBar.

            self.actions = []

            # Options
            self.buttonColor = c.config.getString('qt-button-color')

            # g.app.iconWidgetCount = 0
        #@+node:ekr.20110605121601.18264: *5*  do-nothings (QtIconBarClass)
        # These *are* called from Leo's core.

        def addRow(self,height=None):
            pass # To do.
            
        def getNewFrame (self): 
            return None # To do
        #@+node:ekr.20110605121601.18265: *5* add (QtIconBarClass)
        def add(self,*args,**keys):
            '''Add a button to the icon bar.'''
            trace = False and not g.unitTesting
            c = self.c
            if not self.w: return
            command = keys.get('command')
            text = keys.get('text')
            # able to specify low-level QAction directly (QPushButton not forced)
            qaction = keys.get('qaction')
            if not text and not qaction:
                g.es('bad toolbar item')
            kind = keys.get('kind') or 'generic-button'
            # imagefile = keys.get('imagefile')
            # image = keys.get('image')

            class leoIconBarButton (QtWidgets.QWidgetAction):
                def __init__ (self,parent,text,toolbar):
                    QtWidgets.QWidgetAction.__init__(self,parent)
                    self.button = None # set below
                    self.text = text
                    self.toolbar = toolbar
                def createWidget (self,parent):
                    # g.trace('leoIconBarButton',self.toolbar.buttonColor)
                    self.button = b = QtWidgets.QPushButton(self.text,parent)
                    self.button.setProperty('button_kind', kind)  # for styling
                    return b

            if qaction is None:
                action = leoIconBarButton(parent=self.w,text=text,toolbar=self)
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
            if trace: g.trace(button_name)
            b.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
            def delete_callback(checked, action=action,):
                self.w.removeAction(action)
            b.leo_removeAction = rb = QtWidgets.QAction('Remove Button' ,b)
            b.addAction(rb)
            rb.triggered.connect(delete_callback)
            if command:
                def button_callback(event,c=c,command=command):
                    # g.trace('command',command.__name__)
                    val = command()
                    if c.exists:
                        # c.bodyWantsFocus()
                        c.outerUpdate()
                    return val
                b.clicked.connect(button_callback)
            return action
        #@+node:ekr.20110605121601.18266: *5* addRowIfNeeded
        def addRowIfNeeded (self):

            '''Add a new icon row if there are too many widgets.'''

            # n = g.app.iconWidgetCount

            # if n >= self.widgets_per_row:
                # g.app.iconWidgetCount = 0
                # self.addRow()

            # g.app.iconWidgetCount += 1
        #@+node:ekr.20110605121601.18267: *5* addWidget
        def addWidget (self,w):

            self.w.addWidget(w)
        #@+node:ekr.20110605121601.18268: *5* clear
        def clear(self):

            """Destroy all the widgets in the icon bar"""

            self.w.clear()
            self.actions = []

            g.app.iconWidgetCount = 0
        #@+node:ekr.20110605121601.18269: *5* createChaptersIcon
        def createChaptersIcon(self):

            # g.trace('(QtIconBarClass)')
            c = self.c
            f = c.frame
            if f.use_chapters and f.use_chapter_tabs:
                return LeoQtTreeTab(c,f.iconBar)
            else:
                return None
        #@+node:ekr.20110605121601.18270: *5* deleteButton
        def deleteButton (self,w):
            """ w is button """

            self.w.removeAction(w)

            self.c.bodyWantsFocus()
            self.c.outerUpdate()
        #@+node:ekr.20110605121601.18271: *5* setCommandForButton (@rclick nodes)
        def setCommandForButton(self,button,command):

            # EKR 2013/09/12: fix bug 1193819: Script buttons cant "go to script" after outline changes.
            # The command object now has a gnx ivar instead of a p ivar.
            # The code below uses command.controller.find_gnx to determine the proper position.
            if command:
                # button is a leoIconBarButton.
                button.button.clicked.connect(command)
                # can get here from @buttons in the current outline, in which
                # case p exists, or from @buttons in @settings elsewhere, in
                # which case it doesn't
                if not hasattr(command,'gnx'):
                    return
                command_p = command.controller.find_gnx(command.gnx)
                if not command_p:
                    return
                # 20100518 - TNB command is instance of callable class with
                #   c and gnx attributes, so we can add a context menu item...
                def goto_command(checked, command = command):
                    c = command.c
                    p = command.controller.find_gnx(command.gnx)
                    if p:
                        c.selectPosition(p)
                        c.redraw()
                b = button.button
                docstring = g.getDocString(command_p.b)
                if docstring:
                    b.setToolTip(docstring)
                b.goto_script = gts = QtWidgets.QAction('Goto Script', b)
                b.addAction(gts)
                gts.triggered.connect(goto_command)
                
                rclicks = build_rclick_tree(command_p, top_level=True)
                self.add_rclick_menu(b, rclicks, command.controller)

        def add_rclick_menu(self, action_container, rclicks, controller,
                            top_level=True, button=None, from_settings=False):

            if from_settings:
                top_offset = -1  # insert before the remove button item
            else:
                top_offset = -2  # insert before the remove button and goto script items

            if top_level:
                button = action_container

            for rc in rclicks:
                headline = rc.position.h[8:].strip()
                act = QtWidgets.QAction(headline, action_container)
                if '---' in headline and headline.strip().strip('-') == '':
                    act.setSeparator(True)
                elif rc.position.b.strip():
                    if from_settings:
                        def cb(checked, script=rc.position.b, button=button,
                               controller=controller, buttonText=rc.position.h[8:].strip()):
                            controller.executeScriptFromSettingButton(
                                [],  # args,
                                button,
                                script,
                                buttonText
                            )
                    else:
                        def cb(checked, p=rc.position, button=button,
                               controller=controller):
                            controller.executeScriptFromButton(
                                button,
                                p.h[8:].strip(),
                                p.gnx
                            )
                            if controller.c.exists:
                                controller.c.outerUpdate()
                    act.triggered.connect(cb)
                    
                else:  # recurse submenu
                    sub_menu = QtWidgets.QMenu(action_container)
                    act.setMenu(sub_menu)
                    self.add_rclick_menu(sub_menu, rc.children, controller,
                                         top_level=False, button=button,
                                         from_settings=from_settings)
                                         
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
                    g.u(action_container.text()) + 
                    (controller.c.config.getString(
                        'mod_scripting_subtext') or '')
                )
        #@-others
    #@+node:ekr.20110605121601.18274: *4* Configuration (qtFrame)
    #@+node:ekr.20110605121601.18275: *5* configureBar (qtFrame)
    def configureBar (self,bar,verticalFlag):

        c = self.c

        # Get configuration settings.
        w = c.config.getInt("split_bar_width")
        if not w or w < 1: w = 7
        relief = c.config.get("split_bar_relief","relief")
        if not relief: relief = "flat"
        color = c.config.getColor("split_bar_color")
        if not color: color = "LightSteelBlue2"

        try:
            if verticalFlag:
                # Panes arranged vertically; horizontal splitter bar
                bar.configure(relief=relief,height=w,bg=color,cursor="sb_v_double_arrow")
            else:
                # Panes arranged horizontally; vertical splitter bar
                bar.configure(relief=relief,width=w,bg=color,cursor="sb_h_double_arrow")
        except: # Could be a user error. Use all defaults
            g.es("exception in user configuration for splitbar")
            g.es_exception()
            if verticalFlag:
                # Panes arranged vertically; horizontal splitter bar
                bar.configure(height=7,cursor="sb_v_double_arrow")
            else:
                # Panes arranged horizontally; vertical splitter bar
                bar.configure(width=7,cursor="sb_h_double_arrow")
    #@+node:ekr.20110605121601.18276: *5* configureBarsFromConfig (qtFrame)
    def configureBarsFromConfig (self):

        c = self.c

        w = c.config.getInt("split_bar_width")
        if not w or w < 1: w = 7

        relief = c.config.get("split_bar_relief","relief")
        if not relief or relief == "": relief = "flat"

        color = c.config.getColor("split_bar_color")
        if not color or color == "": color = "LightSteelBlue2"

        if self.splitVerticalFlag:
            bar1,bar2=self.bar1,self.bar2
        else:
            bar1,bar2=self.bar2,self.bar1

        try:
            bar1.configure(relief=relief,height=w,bg=color)
            bar2.configure(relief=relief,width=w,bg=color)
        except: # Could be a user error.
            g.es("exception in user configuration for splitbar")
            g.es_exception()
    #@+node:ekr.20110605121601.18277: *5* reconfigureFromConfig (qtFrame)
    def reconfigureFromConfig (self):

        frame = self ; c = frame.c

        # frame.tree.setFontFromConfig()
        frame.configureBarsFromConfig()

        # frame.body.setFontFromConfig()
        # frame.body.setColorFromConfig()

        frame.setTabWidth(c.tab_width)
        # frame.log.setFontFromConfig()
        # frame.log.setColorFromConfig()

        c.redraw()
    #@+node:ekr.20110605121601.18278: *5* setInitialWindowGeometry (qtFrame)
    def setInitialWindowGeometry(self):

        """Set the position and size of the frame to config params."""

        c = self.c

        h = c.config.getInt("initial_window_height") or 500
        w = c.config.getInt("initial_window_width") or 600
        x = c.config.getInt("initial_window_left") or 10
        y = c.config.getInt("initial_window_top") or 10

        # g.trace(h,w,x,y)

        if h and w and x and y:
            self.setTopGeometry(w,h,x,y)
    #@+node:ekr.20110605121601.18279: *5* setTabWidth (qtFrame)
    def setTabWidth (self, w):

        # A do-nothing because tab width is set automatically.
        # It *is* called from Leo's core.
        pass

    #@+node:ekr.20110605121601.18280: *5* setWrap (qtFrame)
    def setWrap (self,p):

        self.c.frame.body.setWrap(p)
    #@+node:ekr.20110605121601.18281: *5* reconfigurePanes (qtFrame)
    def reconfigurePanes (self):

        f = self ; c = f.c

        if f.splitVerticalFlag:
            r = c.config.getRatio("initial_vertical_ratio")
            if r == None or r < 0.0 or r > 1.0: r = 0.5
            r2 = c.config.getRatio("initial_vertical_secondary_ratio")
            if r2 == None or r2 < 0.0 or r2 > 1.0: r2 = 0.8
        else:
            r = c.config.getRatio("initial_horizontal_ratio")
            if r == None or r < 0.0 or r > 1.0: r = 0.3
            r2 = c.config.getRatio("initial_horizontal_secondary_ratio")
            if r2 == None or r2 < 0.0 or r2 > 1.0: r2 = 0.8

        f.ratio,f.secondary_ratio = r,r2
        f.resizePanesToRatio(r,r2)
    #@+node:ekr.20110605121601.18282: *5* resizePanesToRatio (qtFrame)
    def resizePanesToRatio(self,ratio,ratio2):

        trace = False and not g.unitTesting

        f = self
        if trace: g.trace('%5s, %0.2f %0.2f' % (
            self.splitVerticalFlag,ratio,ratio2),g.callers(4))
        f.divideLeoSplitter(self.splitVerticalFlag,ratio)
        f.divideLeoSplitter(not self.splitVerticalFlag,ratio2)
    #@+node:ekr.20110605121601.18283: *5* divideLeoSplitter
    # Divides the main or secondary splitter, using the key invariant.
    def divideLeoSplitter (self, verticalFlag, frac):

        # g.trace(verticalFlag,frac)

        if self.splitVerticalFlag == verticalFlag:
            self.divideLeoSplitter1(frac,verticalFlag)
            self.ratio = frac # Ratio of body pane to tree pane.
        else:
            self.divideLeoSplitter2(frac,verticalFlag)
            self.secondary_ratio = frac # Ratio of tree pane to log pane.

    # Divides the main splitter.
    def divideLeoSplitter1 (self, frac, verticalFlag): 
        self.divideAnySplitter(frac, self.top.splitter_2 )

    # Divides the secondary splitter.
    def divideLeoSplitter2 (self, frac, verticalFlag): 
        self.divideAnySplitter (frac, self.top.leo_ui.splitter)

    #@+node:ekr.20110605121601.18284: *5* divideAnySplitter
    # This is the general-purpose placer for splitters.
    # It is the only general-purpose splitter code in Leo.

    def divideAnySplitter (self,frac,splitter):

        sizes = splitter.sizes()

        if len(sizes)!=2:
            g.trace('%s widget(s) in %s' % (len(sizes),id(splitter)))
            return

        if frac > 1 or frac < 0:
            g.trace('split ratio [%s] out of range 0 <= frac <= 1'%frac)

        s1, s2 = sizes
        s = s1+s2
        s1 = int(s * frac + 0.5)
        s2 = s - s1 

        splitter.setSizes([s1,s2])
    #@+node:ekr.20110605121601.18285: *4* Event handlers (qtFrame)
    #@+node:ekr.20110605121601.18286: *5* frame.OnCloseLeoEvent
    # Called from quit logic and when user closes the window.
    # Returns True if the close happened.

    def OnCloseLeoEvent(self):

        f = self ; c = f.c

        if c.inCommand:
            # g.trace('requesting window close')
            c.requestCloseWindow = True
        else:
            g.app.closeLeoWindow(self)
    #@+node:ekr.20110605121601.18287: *5* frame.OnControlKeyUp/Down
    def OnControlKeyDown (self,event=None):

        self.controlKeyIsDown = True

    def OnControlKeyUp (self,event=None):

        self.controlKeyIsDown = False
    #@+node:ekr.20110605121601.18290: *5* OnActivateTree
    def OnActivateTree (self,event=None):

        pass
    #@+node:ekr.20110605121601.18291: *5* OnBodyClick, OnBodyRClick (not used)
    # At present, these are not called,
    # but they could be called by LeoQTextBrowser.

    def OnBodyClick (self,event=None):

        g.trace()

        try:
            c = self.c ; p = c.currentPosition()
            if g.doHook("bodyclick1",c=c,p=p,v=p,event=event):
                g.doHook("bodyclick2",c=c,p=p,v=p,event=event)
                return
            else:
                c.k.showStateAndMode(w=c.frame.body.bodyCtrl)
                g.doHook("bodyclick2",c=c,p=p,v=p,event=event)
        except:
            g.es_event_exception("bodyclick")

    def OnBodyRClick(self,event=None):

        try:
            c = self.c ; p = c.currentPosition()
            if g.doHook("bodyrclick1",c=c,p=p,v=p,event=event):
                g.doHook("bodyrclick2",c=c,p=p,v=p,event=event)
                return
            else:
                c.k.showStateAndMode(w=c.frame.body.bodyCtrl)
                g.doHook("bodyrclick2",c=c,p=p,v=p,event=event)
        except:
            g.es_event_exception("iconrclick")
    #@+node:ekr.20110605121601.18292: *5* OnBodyDoubleClick (Events) (not used)
    # Not called

    def OnBodyDoubleClick (self,event=None):

        try:
            c = self.c ; p = c.currentPosition()
            if event and not g.doHook("bodydclick1",c=c,p=p,v=p,event=event):
                c.editCommands.extendToWord(event) # Handles unicode properly.
                c.k.showStateAndMode(w=c.frame.body.bodyCtrl)
            g.doHook("bodydclick2",c=c,p=p,v=p,event=event)
        except:
            g.es_event_exception("bodydclick")

        return "break" # Restore this to handle proper double-click logic.
    #@+node:ekr.20110605121601.18293: *4* Gui-dependent commands
    #@+node:ekr.20110605121601.18294: *5* Minibuffer commands... (qtFrame)
    #@+node:ekr.20110605121601.18295: *6* contractPane
    def contractPane (self,event=None):

        '''Contract the selected pane.'''

        f = self ; c = f.c

        w = c.get_requested_focus() or g.app.gui.get_focus(c)
        wname = c.widget_name(w)

        # g.trace(wname)
        if not w: return

        if wname.startswith('body'):
            f.contractBodyPane()
            c.bodyWantsFocus()
        elif wname.startswith('log'):
            f.contractLogPane()
            c.logWantsFocus()
        else:
            for z in ('head','canvas','tree'):
                if wname.startswith(z):
                    f.contractOutlinePane()
                    c.treeWantsFocus()
                    break
    #@+node:ekr.20110605121601.18296: *6* expandPane
    def expandPane (self,event=None):

        '''Expand the selected pane.'''

        f = self ; c = f.c

        w = c.get_requested_focus() or g.app.gui.get_focus(c)
        wname = c.widget_name(w)

        # g.trace(wname)
        if not w: return

        if wname.startswith('body'):
            f.expandBodyPane()
            c.bodyWantsFocus()
        elif wname.startswith('log'):
            f.expandLogPane()
            c.logWantsFocus()
        else:
            for z in ('head','canvas','tree'):
                if wname.startswith(z):
                    f.expandOutlinePane()
                    c.treeWantsFocus()
                    break
    #@+node:ekr.20110605121601.18297: *6* fullyExpandPane
    def fullyExpandPane (self,event=None):

        '''Fully expand the selected pane.'''

        f = self ; c = f.c

        w = c.get_requested_focus() or g.app.gui.get_focus(c)
        wname = c.widget_name(w)

        # g.trace(wname)
        if not w: return

        if wname.startswith('body'):
            f.fullyExpandBodyPane()
            c.treeWantsFocus()
        elif wname.startswith('log'):
            f.fullyExpandLogPane()
            c.bodyWantsFocus()
        else:
            for z in ('head','canvas','tree'):
                if wname.startswith(z):
                    f.fullyExpandOutlinePane()
                    c.bodyWantsFocus()
                    break
    #@+node:ekr.20110605121601.18298: *6* hidePane
    def hidePane (self,event=None):

        '''Completely contract the selected pane.'''

        f = self ; c = f.c

        w = c.get_requested_focus() or g.app.gui.get_focus(c)
        wname = c.widget_name(w)

        # g.trace(wname)
        if not w: return

        if wname.startswith('body'):
            f.hideBodyPane()
            c.treeWantsFocus()
        elif wname.startswith('log'):
            f.hideLogPane()
            c.bodyWantsFocus()
        else:
            for z in ('head','canvas','tree'):
                if wname.startswith(z):
                    f.hideOutlinePane()
                    c.bodyWantsFocus()
                    break
    #@+node:ekr.20110605121601.18299: *6* expand/contract/hide...Pane
    #@+at The first arg to divideLeoSplitter means the following:
    # 
    #     f.splitVerticalFlag: use the primary   (tree/body) ratio.
    # not f.splitVerticalFlag: use the secondary (tree/log) ratio.
    #@@c

    def contractBodyPane (self,event=None):
        '''Contract the body pane.'''
        f = self ; r = min(1.0,f.ratio+0.1)
        f.divideLeoSplitter(f.splitVerticalFlag,r)

    def contractLogPane (self,event=None):
        '''Contract the log pane.'''
        f = self ; r = min(1.0,f.secondary_ratio+0.1) # 2010/02/23: was f.ratio
        f.divideLeoSplitter(not f.splitVerticalFlag,r)

    def contractOutlinePane (self,event=None):
        '''Contract the outline pane.'''
        f = self ; r = max(0.0,f.ratio-0.1)
        f.divideLeoSplitter(f.splitVerticalFlag,r)

    def expandBodyPane (self,event=None):
        '''Expand the body pane.'''
        self.contractOutlinePane()

    def expandLogPane(self,event=None):
        '''Expand the log pane.'''
        f = self ; r = max(0.0,f.secondary_ratio-0.1) # 2010/02/23: was f.ratio
        f.divideLeoSplitter(not f.splitVerticalFlag,r)

    def expandOutlinePane (self,event=None):
        '''Expand the outline pane.'''
        self.contractBodyPane()
    #@+node:ekr.20110605121601.18300: *6* fullyExpand/hide...Pane
    def fullyExpandBodyPane (self,event=None):
        '''Fully expand the body pane.'''
        f = self
        f.divideLeoSplitter(f.splitVerticalFlag,0.0)

    def fullyExpandLogPane (self,event=None):
        '''Fully expand the log pane.'''
        f = self
        f.divideLeoSplitter(not f.splitVerticalFlag,0.0)

    def fullyExpandOutlinePane (self,event=None):
        '''Fully expand the outline pane.'''
        f = self
        f.divideLeoSplitter(f.splitVerticalFlag,1.0)

    def hideBodyPane (self,event=None):
        '''Completely contract the body pane.'''
        f = self
        f.divideLeoSplitter(f.splitVerticalFlag,1.0)

    def hideLogPane (self,event=None):
        '''Completely contract the log pane.'''
        f = self
        f.divideLeoSplitter(not f.splitVerticalFlag,1.0)

    def hideOutlinePane (self,event=None):
        '''Completely contract the outline pane.'''
        f = self
        f.divideLeoSplitter(f.splitVerticalFlag,0.0)
    #@+node:ekr.20110605121601.18301: *5* Window Menu...
    #@+node:ekr.20110605121601.18302: *6* toggleActivePane (qtFrame)
    def toggleActivePane (self,event=None):

        '''Toggle the focus between the outline and body panes.'''

        frame = self ; c = frame.c
        w = c.get_focus()
        w_name = g.app.gui.widget_name(w)

        # g.trace(w,w_name)

        if w_name in ('canvas','tree','treeWidget'):
            c.endEditing()
            c.bodyWantsFocus()
        else:
            c.treeWantsFocus()
    #@+node:ekr.20110605121601.18303: *6* cascade
    def cascade (self,event=None):

        '''Cascade all Leo windows.'''

        x,y,delta = 50,50,50
        for frame in g.app.windowList:

            w = frame and frame.top
            if w:
                r = w.geometry() # a Qt.Rect
                # 2011/10/26: Fix bug 823601: cascade-windows fails.
                w.setGeometry(QtCore.QRect(x,y,r.width(),r.height()))

                # Compute the new offsets.
                x += 30 ; y += 30
                if x > 200:
                    x = 10 + delta ; y = 40 + delta
                    delta += 10
    #@+node:ekr.20110605121601.18304: *6* equalSizedPanes
    def equalSizedPanes (self,event=None):

        '''Make the outline and body panes have the same size.'''

        frame = self
        frame.resizePanesToRatio(0.5,frame.secondary_ratio)
    #@+node:ekr.20110605121601.18305: *6* hideLogWindow
    def hideLogWindow (self,event=None):

        frame = self

        frame.divideLeoSplitter2(0.99, not frame.splitVerticalFlag)
    #@+node:ekr.20110605121601.18306: *6* minimizeAll (qtFrame)
    def minimizeAll (self,event=None):

        '''Minimize all Leo's windows.'''

        for frame in g.app.windowList:
            self.minimize(frame)

    def minimize(self,frame):

        # This unit test will fail when run externally.

        if frame and frame.top:

            # For --gui=qttabs, frame.top.leo_master is a LeoTabbedTopLevel.
            # For --gui=qt,     frame.top is a DynamicWindow.
            w = frame.top.leo_master or frame.top
            if g.unitTesting:
                g.app.unitTestDict['minimize-all'] = True
                assert hasattr(w,'setWindowState'),w
            else:
                w.setWindowState(QtCore.Qt.WindowMinimized)
    #@+node:ekr.20110605121601.18307: *6* toggleSplitDirection (qtFrame)
    def toggleSplitDirection (self,event=None):

        '''Toggle the split direction in the present Leo window.'''

        trace = False and not g.unitTesting
        c,f = self.c,self

        if trace: g.trace('*'*20)

        def getRatio(w):
            sizes = w.sizes()
            if len(sizes) == 2:
                size1,size2 = sizes
                ratio = float(size1)/float(size1+size2)
                if trace: g.trace(
                    '   ratio: %0.2f, size1: %3s, size2: %3s, total: %4s, w: %s' % (
                    ratio,size1,size2,size1+size2,w))
                return ratio
            else:
                if trace: g.trace('oops: len(sizes)',len(sizes),'default 0.5')
                return float(0.5)

        def getNewSizes(sizes,ratio):
            size1,size2 = sizes
            total = size1+size2
            size1 = int(float(ratio)*float(total))
            size2 = total - size1
            if trace: g.trace(
                'ratio: %0.2f, size1: %3s, size2: %3s, total: %4s' % (
                ratio,size1,size2,total))
            return [size1,size2]

        # Compute the actual ratios before reorienting.
        w1,w2 = f.top.splitter, f.top.splitter_2
        r1 = getRatio(w1)
        r2 = getRatio(w2)
        f.ratio,f.secondary_ratio = r1,r2

        # Remember the sizes before reorienting.
        sizes1 = w1.sizes()
        sizes2 = w2.sizes()

        # Reorient the splitters.
        for w in (f.top.splitter,f.top.splitter_2):
            w.setOrientation(
                QtCore.Qt.Vertical if w.orientation() == QtCore.Qt.Horizontal else QtCore.Qt.Horizontal)

        # Fix bug 580328: toggleSplitDirection doesn't preserve existing ratio.
        if len(sizes1) == 2 and len(sizes2) == 2:
            w1.setSizes(getNewSizes(sizes1,r1))
            w2.setSizes(getNewSizes(sizes2,r2))

        # Maintain the key invariant: self.splitVerticalFlag
        # tells the alignment of the main splitter.
        f.splitVerticalFlag = not f.splitVerticalFlag

        # Fix bug 581031: Scrollbar position is not preserved.
        # This is better than adjust the scroll value directy.
        c.frame.tree.setItemForCurrentPosition(scroll=True)
        c.frame.body.seeInsertPoint()
    #@+node:ekr.20110605121601.18308: *6* resizeToScreen (qtFrame)
    def resizeToScreen (self,event=None):

        '''Resize the Leo window so it fill the entire screen.'''

        frame = self

        # This unit test will fail when run externally.

        if frame and frame.top:

            # For --gui=qttabs, frame.top.leo_master is a LeoTabbedTopLevel.
            # For --gui=qt,     frame.top is a DynamicWindow.
            w = frame.top.leo_master or frame.top
            if g.unitTesting:
                g.app.unitTestDict['resize-to-screen'] = True
                assert hasattr(w,'setWindowState'),w
            else:
                w.setWindowState(QtCore.Qt.WindowMaximized)
    #@+node:ekr.20110605121601.18309: *5* Help Menu...
    #@+node:ekr.20110605121601.18310: *6* leoHelp
    def leoHelp (self,event=None):

        '''Open Leo's offline tutorial.'''

        frame = self ; c = frame.c

        theFile = g.os_path_join(g.app.loadDir,"..","doc","sbooks.chm")

        if g.os_path_exists(theFile):
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
                except:
                    if 0:
                        g.es("exception downloading","sbooks.chm")
                        g.es_exception()
    #@+node:ekr.20110605121601.18311: *4* Qt bindings... (qtFrame)
    def bringToFront (self):
        self.lift()
    def deiconify (self):
        if self.top and self.top.isMinimized(): # Bug fix: 400739.
            self.lift()
    def getFocus(self):
        return g.app.gui.get_focus(self.c) # Bug fix: 2009/6/30.
    def get_window_info(self):
        if hasattr(self.top,'leo_master') and self.top.leo_master:
            f = self.top.leo_master
        else:
            f = self.top
        rect = f.geometry()
        topLeft = rect.topLeft()
        x,y = topLeft.x(),topLeft.y()
        w,h = rect.width(),rect.height()
        # g.trace(w,h,x,y)
        return w,h,x,y
    def iconify(self):
        if self.top: self.top.showMinimized()
    def lift (self):
        # g.trace(self.c,'\n',g.callers(9))
        if not self.top: return
        if self.top.isMinimized(): # Bug 379141
            self.top.showNormal()
        self.top.activateWindow()
        self.top.raise_()
    def getTitle (self):
        # Fix https://bugs.launchpad.net/leo-editor/+bug/1194209
        # When using tabs, leo_master (a LeoTabbedTopLevel) contains the QMainWindow.
        w = self.top.leo_master if g.app.qt_use_tabs else self.top
        s = g.u(w.windowTitle())
        return s
    def setTitle (self,s):
        # g.trace('**(qtFrame)',repr(s))
        if self.top:
            # Fix https://bugs.launchpad.net/leo-editor/+bug/1194209
            # When using tabs, leo_master (a LeoTabbedTopLevel) contains the QMainWindow.
            w = self.top.leo_master if g.app.qt_use_tabs else self.top
            w.setWindowTitle(s)
    def setTopGeometry(self,w,h,x,y,adjustSize=True):
        # self.top is a DynamicWindow.
        # g.trace('(qtFrame)',x,y,w,h,self.top,g.callers())
        if self.top:
            self.top.setGeometry(QtCore.QRect(x,y,w,h))
    def update(self,*args,**keys):
        self.top.update()
    #@-others
#@+node:ekr.20110605121601.18312: *3* class LeoQtLog (LeoLog)
class LeoQtLog (leoFrame.LeoLog):

    """A class that represents the log pane of a Qt window."""

    # pylint: disable=R0923
    # R0923:LeoQtLog: Interface not implemented

    #@+others
    #@+node:ekr.20110605121601.18313: *4* LeoQtLog Birth
    #@+node:ekr.20110605121601.18314: *5* LeoQtLog.__init__
    def __init__ (self,frame,parentFrame):

        # g.trace('(LeoQtLog)',frame,parentFrame)

        # Call the base class constructor and calls createControl.
        leoFrame.LeoLog.__init__(self,frame,parentFrame)
        self.c = c = frame.c # Also set in the base constructor, but we need it here.
        self.contentsDict = {} # Keys are tab names.  Values are widgets.
        self.eventFilters = [] # Apparently needed to make filters work!
        self.logDict = {} # Keys are tab names text widgets.  Values are the widgets.
        self.menu = None # A menu that pops up on right clicks in the hull or in tabs.
        self.tabWidget = tw = c.frame.top.leo_ui.tabWidget
            # The Qt.QTabWidget that holds all the tabs.
        # Fixes bug 917814: Switching Log Pane tabs is done incompletely.
        tw.currentChanged.connect(self.onCurrentChanged)
        self.wrap = True if c.config.getBool('log_pane_wraps') else False
        if 0: # Not needed to make onActivateEvent work.
            # Works only for .tabWidget, *not* the individual tabs!
            theFilter = LeoQtEventFilter(c,w=tw,tag='tabWidget')
            tw.installEventFilter(theFilter)
        # 2013/11/15: Partial fix for bug 1251755: Log-pane refinements
        tw.setMovable(True)
    #@+node:ekr.20110605121601.18315: *5* LeoQtLog.finishCreate
    def finishCreate (self):

        c = self.c ; log = self ; w = self.tabWidget
        # Remove unneeded tabs.
        for name in ('Tab 1','Page'):
            for i in range(w.count()):
                if name == w.tabText(i):
                    w.removeTab(i)
                    break
        # Rename the 'Tab 2' tab to 'Find'.
        for i in range(w.count()):
            if w.tabText(i) in ('Find','Tab 2'):
                w.setTabText(i,'Find')
                self.contentsDict['Find'] = w.currentWidget()
                break
        # Create the log tab as the leftmost tab.
        # log.selectTab('Log')
        log.createTab('Log')
        logWidget = self.contentsDict.get('Log')
        option = QtGui.QTextOption
        logWidget.setWordWrapMode(
            option.WordWrap if self.wrap else option.NoWrap)
        for i in range(w.count()):
            if w.tabText(i) == 'Log':
                w.removeTab(i)
        w.insertTab(0,logWidget,'Log')
        c.findCommands.openFindTab(show=False)
        c.spellCommands.openSpellTab()
    #@+node:ekr.20110605121601.18316: *5* LeoQtLog.getName
    def getName (self):
        return 'log' # Required for proper pane bindings.
    #@+node:ekr.20120304214900.9940: *4* Event handler (LeoQtLog)
    def onCurrentChanged(self,idx):

        trace = False and not g.unitTesting

        tabw = self.tabWidget
        w = tabw.widget(idx)

        # Fixes bug 917814: Switching Log Pane tabs is done incompletely
        wrapper = hasattr(w,'leo_log_wrapper') and w.leo_log_wrapper
        if wrapper:
            self.widget = wrapper

        if trace: g.trace(idx,tabw.tabText(idx),self.c.frame.title) # wrapper and wrapper.widget)
    #@+node:ekr.20111120124732.10184: *4* isLogWidget (LeoQtLog)
    def isLogWidget(self,w):

        val = w == self or w in list(self.contentsDict.values())
        # g.trace(val,w)
        return val
    #@+node:ekr.20110605121601.18321: *4* put & putnl (LeoQtLog)
    #@+node:ekr.20110605121601.18322: *5* put (LeoQtLog)
    def put (self,s,color=None,tabName='Log',from_redirect=False):
        '''All output to the log stream eventually comes here.'''
        trace = False and not g.unitTesting
        c = self.c
        if g.app.quitting or not c or not c.exists:
            print('qtGui.log.put fails',repr(s))
            return
        if color:
            color = leoColor.getColor(color,'black')
        else:
            color = leoColor.getColor('black')
        self.selectTab(tabName or 'Log')
        # Must be done after the call to selectTab.
        w = self.logCtrl.widget # w is a QTextBrowser
        if w:
            sb = w.horizontalScrollBar()
            # pos = sb.sliderPosition()
            # g.trace(pos,sb,g.callers())
            s=s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            if not self.wrap: # 2010/02/21: Use &nbsp; only when not wrapping!
                s = s.replace(' ','&nbsp;')
            if from_redirect:
                s = s.replace('\n','<br>')
            else:
                s = s.rstrip().replace('\n','<br>')
            s = '<font color="%s">%s</font>' % (color,s)
            if trace: print('LeoQtLog.put',type(s),len(s),s[:40],w)
            if from_redirect:
                w.insertHtml(s)
            else:
                w.append(s) # w.append is a QTextBrowser method.
                # w.insertHtml(s+'<br>') # Also works.
            w.moveCursor(QtGui.QTextCursor.End)
            sb.setSliderPosition(0) # Force the slider to the initial position.
        else:
            # put s to logWaiting and print s
            g.app.logWaiting.append((s,color),)
            if g.isUnicode(s):
                s = g.toEncodedString(s,"ascii")
            print(s)
    #@+node:ekr.20110605121601.18323: *5* putnl (LeoQtLog)
    def putnl (self,tabName='Log'):
        '''Put a newline to the Qt log.'''
        if g.app.quitting:
            return
        if tabName:
            self.selectTab(tabName)
        w = self.logCtrl.widget
        if w:
            sb = w.horizontalScrollBar()
            pos = sb.sliderPosition()
            # Not needed!
                # contents = w.toHtml()
                # w.setHtml(contents + '\n')
            w.moveCursor(QtGui.QTextCursor.End)
            sb.setSliderPosition(pos)
            w.repaint() # Slow, but essential.
        else:
            # put s to logWaiting and print  a newline
            g.app.logWaiting.append(('\n','black'),)
    #@+node:ekr.20120913110135.10613: *4* putImage (LeoQtLog)
    #@+node:ekr.20110605121601.18324: *4* Tab (LeoQtLog)
    #@+node:ekr.20110605121601.18325: *5* clearTab
    def clearTab (self,tabName,wrap='none'):

        w = self.logDict.get(tabName)
        if w:
            w.clear() # w is a QTextBrowser.
    #@+node:ekr.20110605121601.18326: *5* createTab (LeoQtLog)
    def createTab (self,tabName,createText=True,widget=None,wrap='none'):
        """
        Create a new tab in tab widget
        if widget is None, Create a QTextBrowser,
        suitable for log functionality.
        """
        trace = False and not g.unitTesting
        c = self.c
        if trace: g.trace(tabName,widget and g.app.gui.widget_name(widget) or '<no widget>')
        if widget is None:
            widget = LeoQTextBrowser(parent=None,c=c,wrapper=self)
                # widget is subclass of QTextBrowser.
            contents = QTextEditWrapper(widget=widget,name='log',c=c)
                # contents a wrapper.
            widget.leo_log_wrapper = contents
                # Inject an ivar into the QTextBrowser that points to the wrapper.
            if trace: g.trace('** creating',tabName,'widget',widget,'wrapper',contents)
            option = QtGui.QTextOption
            widget.setWordWrapMode(option.WordWrap if self.wrap else option.NoWrap)
            widget.setReadOnly(False) # Allow edits.
            self.logDict[tabName] = widget
            if tabName == 'Log':
                ##### Huh???
                self.widget = contents # widget is an alias for logCtrl.
                widget.setObjectName('log-widget')
            # Set binding on all log pane widgets.
            g.app.gui.setFilter(c,widget,self,tag='log')
            # A bad hack.  Set the standard bindings in the Find and Spell tabs here.
            if tabName == 'Log':
                assert c.frame.top.__class__.__name__ == 'DynamicWindow'
                find_widget = c.frame.top.leo_find_widget
                # 2011/11/21: A hack: add an event filter.
                g.app.gui.setFilter(c,find_widget,widget,'find-widget')
                if trace: g.trace('** Adding event filter for Find',find_widget)
                # 2011/11/21: A hack: make the find_widget an official log widget.
                self.contentsDict['Find']=find_widget
                # 2013/09/20:
                if hasattr(c.frame.top,'leo_spell_widget'):
                    spell_widget = c.frame.top.leo_spell_widget
                    if trace: g.trace('** Adding event filter for Spell',find_widget)
                    g.app.gui.setFilter(c,spell_widget,widget,'spell-widget')
            self.contentsDict[tabName] = widget
            self.tabWidget.addTab(widget,tabName)
        else:
            contents = widget
                # Unlike text widgets, contents is the actual widget.
            widget.leo_log_wrapper = contents
                # The leo_log_wrapper is the widget itself.
            if trace: g.trace('** using',tabName,widget)
            g.app.gui.setFilter(c,widget,contents,'tabWidget')
            self.contentsDict[tabName] = contents
            self.tabWidget.addTab(contents,tabName)
        return contents
    #@+node:ekr.20110605121601.18327: *5* cycleTabFocus (LeoQtLog)
    def cycleTabFocus (self,event=None):

        '''Cycle keyboard focus between the tabs in the log pane.'''

        trace = False and not g.unitTesting
        w = self.tabWidget
        i = w.currentIndex()
        i += 1
        if i >= w.count():
            i = 0
        tabName = w.tabText(i)
        self.selectTab(tabName,createText=False)
        if trace: g.trace('(LeoQtLog)',i,w,w.count(),w.currentIndex(),g.u(tabName))
        return i
    #@+node:ekr.20110605121601.18328: *5* deleteTab (LeoQtLog)
    def deleteTab (self,tabName,force=False):
        '''Delete the tab if it exists.  Otherwise do *nothing*.'''
        c = self.c
        w = self.tabWidget
        if force or tabName not in ('Log','Find','Spell'):
            for i in range(w.count()):
                if tabName == w.tabText(i):
                    w.removeTab(i)
                    self.selectTab('Log')
                    c.invalidateFocus()
                    c.bodyWantsFocus()
                    return
    #@+node:ekr.20110605121601.18329: *5* hideTab
    def hideTab (self,tabName):

        self.selectTab('Log')
    #@+node:ekr.20111122080923.10185: *5* orderedTabNames (LeoQtLog)
    def orderedTabNames (self,LeoLog=None): # Unused: LeoLog

        '''Return a list of tab names in the order in which they appear in the QTabbedWidget.'''

        w = self.tabWidget

        return [w.tabText(i) for i in range(w.count())]

    #@+node:ekr.20110605121601.18330: *5* numberOfVisibleTabs (LeoQtLog)
    def numberOfVisibleTabs (self):

        return len([val for val in self.contentsDict.values() if val != None])
            # **Note**: the base-class version of this uses frameDict.
    #@+node:ekr.20110605121601.18331: *5* selectTab & helper (LeoQtLog)
    # createText is used by LeoLog.selectTab.
    def selectTab (self,tabName,createText=True,widget=None,wrap='none'):
        '''Create the tab if necessary and make it active.'''
        if not self.selectHelper(tabName):
            self.createTab(tabName,widget=widget,wrap=wrap)
            self.selectHelper(tabName)
    #@+node:ekr.20110605121601.18332: *6* selectHelper (LeoQtLog)
    def selectHelper (self,tabName):

        trace = False and not g.unitTesting
        c,w = self.c,self.tabWidget
        for i in range(w.count()):
            if tabName == w.tabText(i):
                w.setCurrentIndex(i)
                widget = w.widget(i)
                # 2011/11/21: Set the .widget ivar only if there is a wrapper.
                wrapper = hasattr(widget,'leo_log_wrapper') and widget.leo_log_wrapper
                if wrapper:
                    self.widget = wrapper
                if trace: g.trace(tabName,'widget',widget,'wrapper',wrapper)
                # Do *not* set focus here!
                    # c.widgetWantsFocus(tab_widget)
                if tabName == 'Find':
                    # Fix bug 1254861: Ctrl-f doesn't ensure find input field visible.
                    findbox = c.findCommands.ftm.find_findbox
                    widget.ensureWidgetVisible(findbox)
                elif tabName == 'Spell':
                    # the base class uses this as a flag to see if
                    # the spell system needs initing
                    self.frameDict['Spell'] = widget
                self.tabName = tabName # 2011/11/20
                return True
        # General case.
        self.tabName = None # 2011/11/20
        if trace: g.trace('** not found',tabName)
        return False
    #@+node:ekr.20110605121601.18333: *4* LeoQtLog color tab stuff
    def createColorPicker (self,tabName):

        g.warning('color picker not ready for qt')
    #@+node:ekr.20110605121601.18334: *4* LeoQtLog font tab stuff
    #@+node:ekr.20110605121601.18335: *5* createFontPicker
    def createFontPicker (self,tabName):

        # log = self
        QFont = QtWidgets.QFont
        font,ok = QtWidgets.QFontDialog.getFont()
        if not (font and ok): return
        style = font.style()
        table = (
            (QFont.StyleNormal,'normal'),
            (QFont.StyleItalic,'italic'),
            (QFont.StyleOblique,'oblique'))
        for val,name in table:
            if style == val:
                style = name
                break
        else:
            style = ''
        weight = font.weight()
        table = (
            (QFont.Light,'light'),
            (QFont.Normal,'normal'),
            (QFont.DemiBold,'demibold'),
            (QFont.Bold	,'bold'),
            (QFont.Black,'black'))
        for val,name in table:
            if weight == val:
                weight = name
                break
        else:
            weight = ''
        table = (
            ('family',str(font.family())),
            ('size  ',font.pointSize()),
            ('style ',style),
            ('weight',weight),
        )
        for key,val in table:
            if val: g.es(key,val,tabName='Fonts')
    #@+node:ekr.20110605121601.18339: *5* hideFontTab
    def hideFontTab (self,event=None):

        c = self.c
        c.frame.log.selectTab('Log')
        c.bodyWantsFocus()
    #@-others
#@+node:ekr.20110605121601.18340: *3* class LeoQtMenu (LeoMenu)
class LeoQtMenu (leoMenu.LeoMenu):

    #@+others
    #@+node:ekr.20110605121601.18341: *4* LeoQtMenu.__init__
    def __init__ (self,c,frame,label):
        '''ctor for LeoQtMenu class.'''
        assert frame
        assert frame.c
        # Init the base class.
        leoMenu.LeoMenu.__init__(self,frame)
        self.leo_menu_label = label.replace('&','').lower()
        # called from createMenuFromConfigList,createNewMenu,new_menu,QtMenuWrapper.ctor.
        # g.trace('(LeoQtMenu) %s' % (self.leo_menu_label or '<no label!>'))
        self.frame = frame
        self.c = c
        self.menuBar = c.frame.top.menuBar()
        assert self.menuBar is not None
        # Inject this dict into the commander.
        if not hasattr(c,'menuAccels'):
            setattr(c,'menuAccels',{})
        if 0:
            self.font = c.config.getFontFromParams(
                'menu_text_font_family', 'menu_text_font_size',
                'menu_text_font_slant',  'menu_text_font_weight',
                c.config.defaultMenuFontSize)
    #@+node:ekr.20120306130648.9848: *4* LeoQtMenu.__repr__
    def __repr__ (self):

        return '<LeoQtMenu: %s>' % self.leo_menu_label

    __str__ = __repr__
    #@+node:ekr.20110605121601.18342: *4* Tkinter menu bindings
    # See the Tk docs for what these routines are to do
    #@+node:ekr.20110605121601.18343: *5* Methods with Tk spellings
    #@+node:ekr.20110605121601.18344: *6* add_cascade (LeoQtMenu)
    def add_cascade (self,parent,label,menu,underline):

        """Wrapper for the Tkinter add_cascade menu method.

        Adds a submenu to the parent menu, or the menubar."""

        # menu and parent are a QtMenuWrappers, subclasses of  QMenu.
        n = underline
        if -1 < n < len(label):
            label = label[:n] + '&' + label[n:]
        menu.setTitle(label)
        if parent:
            parent.addMenu(menu) # QMenu.addMenu.
        else:
            self.menuBar.addMenu(menu)
        label = label.replace('&','').lower()
        menu.leo_menu_label = label
        return menu
    #@+node:ekr.20110605121601.18345: *6* add_command (LeoQtMenu) (Called by createMenuEntries)
    def add_command (self,**keys):

        """Wrapper for the Tkinter add_command menu method."""

        trace = False and not g.unitTesting # and label.startswith('Paste')
        accel = keys.get('accelerator') or ''
        command = keys.get('command')
        commandName = keys.get('commandName')
        label = keys.get('label')
        n = keys.get('underline')
        menu = keys.get('menu') or self
        if not label: return
        if trace: g.trace(label)
            # command is always add_commandCallback,
            # defined in c.add_command.
        if -1 < n < len(label):
            label = label[:n] + '&' + label[n:]
        if accel:
            label = '%s\t%s' % (label,accel)
        action = menu.addAction(label)

        # 2012/01/20: Inject the command name into the action
        # so that it can be enabled/disabled dynamically.
        action.leo_command_name = commandName
        if command:
            def qt_add_command_callback(checked, label=label,command=command):
                return command()
            action.triggered.connect(qt_add_command_callback)
    #@+node:ekr.20110605121601.18346: *6* add_separator (LeoQtMenu)
    def add_separator(self,menu):

        """Wrapper for the Tkinter add_separator menu method."""

        if menu:
            action = menu.addSeparator()
            action.leo_menu_label = '*seperator*'
    #@+node:ekr.20110605121601.18347: *6* delete (LeoQtMenu)
    def delete (self,menu,realItemName='<no name>'):

        """Wrapper for the Tkinter delete menu method."""

        # g.trace(menu)

        # if menu:
            # return menu.delete(realItemName)
    #@+node:ekr.20110605121601.18348: *6* delete_range (LeoQtMenu)
    def delete_range (self,menu,n1,n2):

        """Wrapper for the Tkinter delete menu method."""

        # Menu is a subclass of QMenu and LeoQtMenu.

        # g.trace(menu,n1,n2,g.callers(4))

        for z in menu.actions()[n1:n2]:
            menu.removeAction(z)
    #@+node:ekr.20110605121601.18349: *6* destroy (LeoQtMenu)
    def destroy (self,menu):

        """Wrapper for the Tkinter destroy menu method."""

        # Fixed bug https://bugs.launchpad.net/leo-editor/+bug/1193870
        if menu:
            menu.menuBar.removeAction(menu.menuAction())
    #@+node:ekr.20110605121601.18350: *6* index (LeoQtMenu)
    def index (self,label):

        '''Return the index of the menu with the given label.'''
        # g.trace(label)

        return 0
    #@+node:ekr.20110605121601.18351: *6* insert (LeoQtMenu)
    def insert (self,menuName,position,label,command,underline=None):

        # g.trace(menuName,position,label,command,underline)

        menu = self.getMenu(menuName)

        if menu and label:
            n = underline or 0
            if -1 > n > len(label):
                label = label[:n] + '&' + label[n:]
            action = menu.addAction(label)
            if command:
                def insert_callback(checked,label=label,command=command):
                    command()
                action.triggered.connect(insert_callback)
    #@+node:ekr.20110605121601.18352: *6* insert_cascade (LeoQtMenu)
    def insert_cascade (self,parent,index,label,menu,underline):

        """Wrapper for the Tkinter insert_cascade menu method."""

        menu.setTitle(label)

        label.replace('&','').lower()
        menu.leo_menu_label = label # was leo_label

        if parent:
            parent.addMenu(menu)
        else:
            self.menuBar.addMenu(menu)

        action = menu.menuAction()
        if action:
            action.leo_menu_label = label
        else:
            g.trace('no action for menu',label)

        return menu
    #@+node:ekr.20110605121601.18353: *6* new_menu (LeoQtMenu)
    def new_menu(self,parent,tearoff=False,label=''): # label is for debugging.
        """Wrapper for the Tkinter new_menu menu method."""
        c,leoFrame = self.c,self.frame
        # Parent can be None, in which case it will be added to the menuBar.
        menu = QtMenuWrapper(c,leoFrame,parent,label)
        return menu
    #@+node:ekr.20110605121601.18354: *5* Methods with other spellings (leoQtmenu)
    #@+node:ekr.20110605121601.18355: *6* clearAccel
    def clearAccel(self,menu,name):

        pass

        # if not menu:
            # return

        # realName = self.getRealMenuName(name)
        # realName = realName.replace("&","")

        # menu.entryconfig(realName,accelerator='')
    #@+node:ekr.20110605121601.18356: *6* createMenuBar (leoQtmenu)
    def createMenuBar(self,frame):

        '''Create all top-level menus.
        The menuBar itself has already been created.'''

        self.createMenusFromTables()
    #@+node:ekr.20110605121601.18357: *6* createOpenWithMenu (LeoQtMenu)
    def createOpenWithMenu(self,parent,label,index,amp_index):

        '''Create the File:Open With submenu.

        This is called from LeoMenu.createOpenWithMenuFromTable.'''

        # Use the existing Open With menu if possible.
        # g.trace(parent,label,index)

        menu = self.getMenu('openwith')

        if not menu:
            menu = self.new_menu(parent,tearoff=False,label=label)
            menu.insert_cascade(parent,index,
                label,menu,underline=amp_index)

        return menu
    #@+node:ekr.20110605121601.18358: *6* disable/enableMenu (LeoQtMenu) (not used)
    def disableMenu (self,menu,name):
        self.enableMenu(menu,name,False)

    def enableMenu (self,menu,name,val):

        '''Enable or disable the item in the menu with the given name.'''

        trace = False and name.startswith('Paste') and not g.unitTesting

        if trace: g.trace(val,name,menu)

        if menu and name:
            val = bool(val)
            # g.trace('%5s %s %s' % (val,name,menu))
            for action in menu.actions():
                s = g.toUnicode(action.text()).replace('&','')
                if s.startswith(name):
                    action.setEnabled(val)
                    break
            else:
                if trace: g.trace('not found:',name)
    #@+node:ekr.20110605121601.18359: *6* getMenuLabel
    def getMenuLabel (self,menu,name):

        '''Return the index of the menu item whose name (or offset) is given.
        Return None if there is no such menu item.'''

        # At present, it is valid to always return None.
    #@+node:ekr.20110605121601.18360: *6* setMenuLabel
    def setMenuLabel (self,menu,name,label,underline=-1):

        def munge(s):
            return g.u(s or '').replace('&','')

        # menu is a QtMenuWrapper.
        # g.trace('menu',menu,'name: %20s label: %s' % (name,label))
        if not menu: return

        realName  = munge(self.getRealMenuName(name))
        realLabel = self.getRealMenuName(label)
        for action in menu.actions():
            s = munge(action.text())
            s = s.split('\t')[0]
            if s == realName:
                action.setText(realLabel)
                break
    #@+node:ekr.20110605121601.18361: *4* LeoQtMenu.activateMenu & helper
    def activateMenu (self,menuName):

        '''Activate the menu with the given name'''

        menu = self.getMenu(menuName)
            # Menu is a QtMenuWrapper, a subclass of both QMenu and LeoQtMenu.
        g.trace(menu)
        if menu:
            self.activateAllParentMenus(menu)
        else:       
            g.trace('No such menu: %s' % (menuName))
    #@+node:ekr.20120922041923.10607: *5* activateAllParentMenus
    def activateAllParentMenus (self,menu):

        '''menu is a QtMenuWrapper.  Activate it and all parent menus.'''

        parent = menu.parent()
        action = menu.menuAction()
        # g.trace(parent,action)
        if action:
            if parent and isinstance(parent,QtWidgets.QMenuBar):
                parent.setActiveAction(action)
            elif parent:
                self.activateAllParentMenus(parent)
                parent.setActiveAction(action)
            else:
                g.trace('can not happen: no parent for %s' % (menu))
        else:
            g.trace('can not happen: no action for %s' % (menu))
    #@+node:ekr.20120922041923.10613: *4* LeoQtMenu.deactivateMenuBar
    # def deactivateMenuBar (self):

        # '''Activate the menu with the given name'''

        # menubar = self.c.frame.top.leo_menubar
        # menubar.setActiveAction(None)
        # menubar.repaint()
    #@+node:ekr.20110605121601.18362: *4* getMacHelpMenu
    def getMacHelpMenu (self,table):

        return None
    #@-others
#@+node:ekr.20110605121601.18363: *3* class LeoQTreeWidget (QTreeWidget)
class LeoQTreeWidget(QtWidgets.QTreeWidget):

    # To do: Generate @auto or @file nodes when appropriate.

    def __init__(self,c,parent):

        QtWidgets.QTreeWidget.__init__(self, parent)
        self.setAcceptDrops(True)
        enable_drag = c.config.getBool('enable-tree-dragging')
        # g.trace(enable_drag,c)
        self.setDragEnabled(bool(enable_drag)) # EKR.
        self.c = c
        self.trace = False

    def __repr__(self):
        return 'LeoQTreeWidget: %s' % id(self)

    __str__ = __repr__

    # This is called during drags.
    def dragMoveEvent(self,ev):
        pass

    #@+others
    #@+node:ekr.20111022222228.16980: *4* Event handlers (LeoQTreeWidget)
    #@+node:ekr.20110605121601.18364: *5* dragEnterEvent
    def dragEnterEvent(self,ev):

        '''Export c.p's tree as a Leo mime-data.'''

        trace = False and not g.unitTesting
        c = self.c
        if not ev:
            g.trace('no event!')
            return
        md = ev.mimeData()
        if not md:
            g.trace('No mimeData!')
            return
        c.endEditing()
        # if g.app.dragging:
            # if trace or self.trace: g.trace('** already dragging')
        # g.app.dragging = True
        g.app.drag_source = c, c.p
        # if self.trace: g.trace('set g.app.dragging')
        self.setText(md)
        if self.trace: self.dump(ev,c.p,'enter')
        # Always accept the drag, even if we are already dragging.
        ev.accept()
    #@+node:ekr.20110605121601.18365: *5* dropEvent & helpers
    def dropEvent(self,ev):

        trace = False and not g.unitTesting
        if not ev: return
        c = self.c ; tree = c.frame.tree
        # Always clear the dragging flag, no matter what happens.
        # g.app.dragging = False
        # if self.trace: g.trace('clear g.app.dragging')
        # Set p to the target of the drop.
        item = self.itemAt(ev.pos())
        if not item: return
        itemHash = tree.itemHash(item)
        p = tree.item2positionDict.get(itemHash)
        if not p:
            if trace or self.trace: g.trace('no p!')
            return
        md = ev.mimeData()
        #print "drop md",mdl
        if not md:
            g.trace('no mimeData!') ; return
        # g.trace("t",str(md.text()))
        # g.trace("h", str(md.html()))
        formats = set(str(f) for f in md.formats())
        ev.setDropAction(QtCore.Qt.IgnoreAction)
        ev.accept()
        hookres = g.doHook("outlinedrop",c=c,p=p,dropevent=ev,formats=formats)
        if hookres:
            # True => plugins handled the drop already
            return
        if trace or self.trace: self.dump(ev,p,'drop ')
        if md.hasUrls():
            self.urlDrop(ev,p)
        else:
            self.outlineDrop(ev,p)
    #@+node:ekr.20110605121601.18366: *6* outlineDrop & helpers
    def outlineDrop (self,ev,p):

        trace = False and not g.unitTesting
        c = self.c
        mods = ev.keyboardModifiers()
        md = ev.mimeData()
        fn,s = self.parseText(md)
        if not s or not fn:
            if trace or self.trace: g.trace('no fn or no s')
            return
        if fn == self.fileName():
            if p and p == c.p:
                if trace or self.trace: g.trace('same node')
            else:
                cloneDrag = (int(mods) & QtCore.Qt.ControlModifier) != 0
                as_child = (int(mods) & QtCore.Qt.AltModifier) != 0
                self.intraFileDrop(cloneDrag,fn,c.p,p,as_child)
        else:
            # Clone dragging between files is not allowed.
            self.interFileDrop(fn,p,s)
    #@+node:ekr.20110605121601.18367: *7* interFileDrop
    def interFileDrop (self,fn,p,s):

        '''Paste the mime data after (or as the first child of) p.'''

        trace = False and not g.unitTesting
        c = self.c
        u = c.undoer
        undoType = 'Drag Outline'
        isLeo = g.match(s,0,g.app.prolog_prefix_string)
        if not isLeo: return
        c.selectPosition(p)
        pasted = c.fileCommands.getLeoOutlineFromClipboard(
            s,reassignIndices=True)
        if not pasted:
            if trace: g.trace('not pasted!')
            return
        if trace: g.trace('pasting...')
        if c.config.getBool('inter_outline_drag_moves'):
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
            pasteAsClone=False,copiedBunchList=[])
        c.validateOutline()
        c.selectPosition(pasted)
        pasted.setDirty()
        pasted.setAllAncestorAtFileNodesDirty() # 2011/02/27: Fix bug 690467.
        c.setChanged(True)
        back = pasted.back()
        if back and back.isExpanded():
            pasted.moveToNthChildOf(back,0)
        # c.setRootPosition(c.findRootPosition(pasted))
        u.afterInsertNode(pasted,undoType,undoData)
        c.redraw_now(pasted)
        c.recolor()
    #@+node:ekr.20110605121601.18368: *7* intraFileDrop
    def intraFileDrop (self,cloneDrag,fn,p1,p2,as_child=False):

        '''Move p1 after (or as the first child of) p2.'''

        c = self.c ; u = c.undoer
        c.selectPosition(p1)
        if as_child or p2.hasChildren() and p2.isExpanded():
            # Attempt to move p1 to the first child of p2.
            # parent = p2
            def move(p1,p2):
                if cloneDrag: p1 = p1.clone()
                p1.moveToNthChildOf(p2,0)
                p1.setDirty()
                p1.setAllAncestorAtFileNodesDirty() # 2011/02/27: Fix bug 690467.
                return p1
        else:
            # Attempt to move p1 after p2.
            # parent = p2.parent()
            def move(p1,p2):
                if cloneDrag: p1 = p1.clone()
                p1.moveAfter(p2)
                p1.setDirty()
                p1.setAllAncestorAtFileNodesDirty() # 2011/02/27: Fix bug 690467.
                return p1
        ok = (
            # 2011/10/03: Major bug fix.
            c.checkDrag(p1,p2) and
            c.checkMoveWithParentWithWarning(p1,p2,True))
        # g.trace(ok,cloneDrag)
        if ok:
            undoData = u.beforeMoveNode(p1)
            dirtyVnodeList = p1.setAllAncestorAtFileNodesDirty()
            p1 = move(p1,p2)
            if cloneDrag:
                # Set dirty bits for ancestors of *all* cloned nodes.
                # Note: the setDescendentsDirty flag does not do what we want.
                for z in p1.self_and_subtree():
                    z.setAllAncestorAtFileNodesDirty(
                        setDescendentsDirty=False)
            c.setChanged(True)
            u.afterMoveNode(p1,'Drag',undoData,dirtyVnodeList)
            c.redraw_now(p1)
        elif not g.unitTesting:
            g.trace('** move failed')
    #@+node:ekr.20110605121601.18369: *6* urlDrop & helpers
    def urlDrop (self,ev,p):

        c = self.c ; u = c.undoer ; undoType = 'Drag Urls'
        md = ev.mimeData()
        urls = md.urls()
        if not urls:
            return
        c.undoer.beforeChangeGroup(c.p,undoType)
        changed = False
        for z in urls:
            url = QtCore.QUrl(z)
            scheme = url.scheme()
            if scheme == 'file':
                changed |= self.doFileUrl(p,url)
            elif scheme in ('http',): # 'ftp','mailto',
                changed |= self.doHttpUrl(p,url)
            # else: g.trace(url.scheme(),url)
        if changed:
            c.setChanged(True)
            u.afterChangeGroup(c.p,undoType,reportFlag=False,dirtyVnodeList=[])
            c.redraw_now()
    #@+node:ekr.20110605121601.18370: *7* doFileUrl & helper
    def doFileUrl (self,p,url):

        # 2014/06/06: Work around a possible bug in QUrl class.  str(aUrl) fails here.
        # fn = str(url.path())
        e = sys.getfilesystemencoding()
        fn = g.toUnicode(url.path(),encoding=e)
        if sys.platform.lower().startswith('win'):
            if fn.startswith('/'):
                fn = fn[1:]
        if os.path.isdir(fn):
            self.doPathUrlHelper(fn,p)
            return True
        if g.os_path_exists(fn):
            try:
                f = open(fn,'rb') # 2012/03/09: use 'rb'
            except IOError:
                f = None
            if f:
                s = f.read()
                s = g.toUnicode(s)
                f.close()
                self.doFileUrlHelper(fn,p,s)
                return True
        g.es_print('not found: %s' % (fn))
        return False
    #@+node:ekr.20110605121601.18371: *8* doFileUrlHelper & helper
    def doFileUrlHelper (self,fn,p,s):

        '''Insert s in an @file, @auto or @edit node after p.'''

        c = self.c
        u,undoType = c.undoer,'Drag File'
        undoData = u.beforeInsertNode(p,pasteAsClone=False,copiedBunchList=[])
        if p.hasChildren() and p.isExpanded():
            p2 = p.insertAsNthChild(0)
        else:
            p2 = p.insertAfter()
        self.createAtFileNode(fn,p2,s)
        u.afterInsertNode(p2,undoType,undoData)
        c.selectPosition(p2)
    #@+node:ekr.20110605121601.18372: *9* createAtFileNode & helpers
    def createAtFileNode (self,fn,p,s):

        '''Set p's headline, body text and possibly descendants
        based on the file's name fn and contents s.

        If the file is an thin file, create an @file tree.
        Othewise, create an @auto tree.
        If all else fails, create an @auto node.

        Give a warning if a node with the same headline already exists.
        '''

        c = self.c
        c.init_error_dialogs()
        if self.isThinFile(fn,s):
            self.createAtFileTree(fn,p,s)
        elif self.isAutoFile(fn):
            self.createAtAutoTree(fn,p)
        elif self.isBinaryFile(fn):
            self.createUrlForBinaryFile(fn,p)
        else:
            self.createAtEditNode(fn,p)
        self.warnIfNodeExists(p)
        c.raise_error_dialogs(kind='read')
    #@+node:ekr.20110605121601.18373: *10* createAtAutoTree
    def createAtAutoTree (self,fn,p):

        '''Make p an @auto node and create the tree using
        s, the file's contents.
        '''

        c = self.c ; at = c.atFileCommands

        p.h = '@auto %s' % (fn)

        at.readOneAtAutoNode(fn,p)

        # No error recovery should be needed here.

        p.clearDirty() # Don't automatically rewrite this node.
    #@+node:ekr.20110605121601.18374: *10* createAtEditNode
    def createAtEditNode(self,fn,p):

        c = self.c ; at = c.atFileCommands

        # Use the full @edit logic, so dragging will be
        # exactly the same as reading.
        at.readOneAtEditNode(fn,p)
        p.h = '@edit %s' % (fn)
        p.clearDirty() # Don't automatically rewrite this node.
    #@+node:ekr.20110605121601.18375: *10* createAtFileTree
    def createAtFileTree (self,fn,p,s):

        '''Make p an @file node and create the tree using
        s, the file's contents.
        '''

        c = self.c ; at = c.atFileCommands

        p.h = '@file %s' % (fn)

        # Read the file into p.
        ok = at.read(root=p.copy(),
            importFileName=None,
            fromString=s,
            atShadow=False,
            force=True) # Disable caching.

        if not ok:
            g.error('Error reading',fn)
            p.b = '' # Safe: will not cause a write later.
            p.clearDirty() # Don't automatically rewrite this node.
    #@+node:ekr.20120309075544.9882: *10* createUrlForBinaryFile
    def createUrlForBinaryFile(self,fn,p):

        # Fix bug 1028986: create relative urls when dragging binary files to Leo.
        c = self.c
        base_fn = g.os_path_normcase(g.os_path_abspath(c.mFileName))
        abs_fn  = g.os_path_normcase(g.os_path_abspath(fn))
        prefix = os.path.commonprefix([abs_fn,base_fn])
        if prefix and len(prefix) > 3: # Don't just strip off c:\.
            p.h = abs_fn[len(prefix):].strip()
        else:
            p.h = '@url file://%s' % fn
        
    #@+node:ekr.20110605121601.18377: *10* isAutoFile
    def isAutoFile (self,fn):
        '''Return true if fn (a file name) can be parsed with an @auto parser.'''
        c = self.c
        d = c.importCommands.classDispatchDict
        junk,ext = g.os_path_splitext(fn)
        return d.get(ext)
    #@+node:ekr.20120309075544.9881: *10* isBinaryFile
    def isBinaryFile(self,fn):

        # The default for unknown files is True. Not great, but safe.
        junk,ext = g.os_path_splitext(fn)
        ext = ext.lower()
        if not ext:
            val = False
        elif ext.startswith('~'):
            val = False
        elif ext in ('.css','.htm','.html','.leo','.txt'):
            val = False
        # elif ext in ('.bmp','gif','ico',):
            # val = True
        else:
            keys = (z.lower() for z in g.app.extension_dict.keys())
            val = ext not in keys

        # g.trace('binary',ext,val)
        return val
    #@+node:ekr.20110605121601.18376: *10* isThinFile
    def isThinFile (self,fn,s):

        '''Return true if the file whose contents is s
        was created from an @thin or @file tree.'''

        c = self. c ; at = c.atFileCommands

        # Skip lines before the @+leo line.
        i = s.find('@+leo')
        if i == -1:
            return False
        else:
            # Like at.isFileLike.
            j,k = g.getLine(s,i)
            line = s[j:k]
            valid,new_df,start,end,isThin = at.parseLeoSentinel(line)
            # g.trace('valid',valid,'new_df',new_df,'isThin',isThin)
            return valid and new_df and isThin
    #@+node:ekr.20110605121601.18378: *10* warnIfNodeExists
    def warnIfNodeExists (self,p):

        c = self.c ; h = p.h
        for p2 in c.all_unique_positions():
            if p2.h == h and p2 != p:
                g.warning('Warning: duplicate node:',h)
                break
    #@+node:ekr.20110605121601.18379: *8* doPathUrlHelper
    def doPathUrlHelper (self,fn,p):

        '''Insert fn as an @path node after p.'''
        
        c = self.c
        u,undoType = c.undoer,'Drag Directory'
        undoData = u.beforeInsertNode(p,pasteAsClone=False,copiedBunchList=[])
        if p.hasChildren() and p.isExpanded():
            p2 = p.insertAsNthChild(0)
        else:
            p2 = p.insertAfter()
        p2.h = '@path ' + fn
        u.afterInsertNode(p2,undoType,undoData)
        c.selectPosition(p2)
    #@+node:ekr.20110605121601.18380: *7* doHttpUrl
    def doHttpUrl (self,p,url):

        '''Insert the url in an @url node after p.'''

        c = self.c ; u = c.undoer ; undoType = 'Drag Url'
        s = str(url.toString()).strip()
        # 2014/06/06: this code may be necessary.  More testing is needed.
        # e = sys.getfilesystemencoding()
        # s = g.toUnicode(url.toString(),encoding=e)
        if not s: return False

        undoData = u.beforeInsertNode(p,pasteAsClone=False,copiedBunchList=[])

        if p.hasChildren() and p.isExpanded():
            p2 = p.insertAsNthChild(0)
        else:
            p2 = p.insertAfter()

        # p2.h,p2.b = '@url %s' % (s),''
        p2.h = '@url'
        p2.b = s
        p2.clearDirty() # Don't automatically rewrite this node.

        u.afterInsertNode(p2,undoType,undoData)
        return True
    #@+node:ekr.20110605121601.18381: *4* utils...
    #@+node:ekr.20110605121601.18382: *5* dump
    def dump (self,ev,p,tag):

        if ev:
            md = ev.mimeData()
            assert md,'dump: no md'
            fn,s = self.parseText(md)
            if fn:
                g.trace('',tag,'fn',repr(g.shortFileName(fn)),
                    'len(s)',len(s),p and p.h)
            else:
                g.trace('',tag,'no fn! s:',repr(s))
        else:
            g.trace('',tag,'** no event!')
    #@+node:ekr.20110605121601.18383: *5* parseText
    def parseText (self,md):

        '''Parse md.text() into (fn,s)'''

        fn = ''
        # Fix bug 1046195: character encoding changes when dragging outline between leo files
        s = g.toUnicode(md.text(),'utf-8')
        if s:
            i = s.find(',')
            if i == -1:
                pass
            else:
                fn = s[:i]
                s = s[i+1:]
        return fn,s
    #@+node:ekr.20110605121601.18384: *5* setText & fileName
    def fileName (self):

        return self.c.fileName() or '<unsaved file>'

    def setText (self,md):

        c = self.c
        fn = self.fileName()
        s = c.fileCommands.putLeoOutline()
        if not g.isPython3:
            s = g.toEncodedString(s,encoding='utf-8',reportErrors=True)
            fn = g.toEncodedString(fn,encoding='utf-8', reportErrors=True)
        md.setText('%s,%s' % (fn,s))
    #@-others
#@+node:ekr.20110605121601.18385: *3* class LeoQtSpellTab
class LeoQtSpellTab:

    #@+others
    #@+node:ekr.20110605121601.18386: *4* LeoQtSpellTab.__init__
    def __init__ (self,c,handler,tabName):

        # g.trace('(LeoQtSpellTab)')
        self.c = c
        self.handler = handler
        # hack:
        handler.workCtrl = leoFrame.StringTextWrapper(c, 'spell-workctrl')
        self.tabName = tabName
        ui = c.frame.top.leo_ui
        # self.createFrame()
        if not hasattr(ui, 'leo_spell_label'):
            self.handler.loaded = False
            return
        self.wordLabel = ui.leo_spell_label
        self.listBox = ui.leo_spell_listBox
        self.fillbox([])
    #@+node:ekr.20110605121601.18389: *4* Event handlers
    #@+node:ekr.20110605121601.18390: *5* onAddButton
    def onAddButton(self):
        """Handle a click in the Add button in the Check Spelling dialog."""

        self.handler.add()
    #@+node:ekr.20110605121601.18391: *5* onChangeButton & onChangeThenFindButton
    def onChangeButton(self,event=None):

        """Handle a click in the Change button in the Spell tab."""

        state = self.updateButtons()
        if state:
            self.handler.change()
        self.updateButtons()

    def onChangeThenFindButton(self,event=None):

        """Handle a click in the "Change, Find" button in the Spell tab."""

        state = self.updateButtons()
        if state:
            self.handler.change()
            if self.handler.change():
                self.handler.find()
            self.updateButtons()
    #@+node:ekr.20110605121601.18392: *5* onFindButton
    def onFindButton(self):

        """Handle a click in the Find button in the Spell tab."""

        c = self.c
        self.handler.find()
        self.updateButtons()
        c.invalidateFocus()
        c.bodyWantsFocus()
    #@+node:ekr.20110605121601.18393: *5* onHideButton
    def onHideButton(self):

        """Handle a click in the Hide button in the Spell tab."""

        self.handler.hide()
    #@+node:ekr.20110605121601.18394: *5* onIgnoreButton
    def onIgnoreButton(self,event=None):

        """Handle a click in the Ignore button in the Check Spelling dialog."""

        self.handler.ignore()
    #@+node:ekr.20110605121601.18395: *5* onMap
    def onMap (self, event=None):
        """Respond to a Tk <Map> event."""

        self.update(show= False, fill= False)
    #@+node:ekr.20110605121601.18396: *5* onSelectListBox
    def onSelectListBox(self, event=None):
        """Respond to a click in the selection listBox."""

        c = self.c
        self.updateButtons()
        c.bodyWantsFocus()
    #@+node:ekr.20110605121601.18397: *4* Helpers
    #@+node:ekr.20110605121601.18398: *5* bringToFront
    def bringToFront (self):

        self.c.frame.log.selectTab('Spell')
    #@+node:ekr.20110605121601.18399: *5* fillbox
    def fillbox(self, alts, word=None):
        """Update the suggestions listBox in the Check Spelling dialog."""

        # ui = self.c.frame.top.leo_ui
        self.suggestions = alts
        if not word: word = ""
        self.wordLabel.setText("Suggestions for: " + word)
        self.listBox.clear()
        if len(self.suggestions):
            self.listBox.addItems(self.suggestions)
            self.listBox.setCurrentRow(0)
    #@+node:ekr.20110605121601.18400: *5* getSuggestion
    def getSuggestion(self):
        """Return the selected suggestion from the listBox."""

        idx = self.listBox.currentRow()
        value = self.suggestions[idx]
        return value
    #@+node:ekr.20110605121601.18401: *5* update (LeoQtSpellTab)
    def update(self,show=True,fill=False):

        """Update the Spell Check dialog."""

        c = self.c

        if fill:
            self.fillbox([])

        self.updateButtons()

        if show:
            self.bringToFront()
            c.bodyWantsFocus()
    #@+node:ekr.20110605121601.18402: *5* updateButtons (spellTab)
    def updateButtons (self):

        """Enable or disable buttons in the Check Spelling dialog."""

        c = self.c

        ui = c.frame.top.leo_ui

        w = c.frame.body.bodyCtrl
        state = self.suggestions and w.hasSelection()

        ui.leo_spell_btn_Change.setDisabled(not state)
        ui.leo_spell_btn_FindChange.setDisabled(not state)

        return state
    #@-others
#@+node:ekr.20110605121601.18403: *3* class LeoQtTree (baseNativeTree)
class LeoQtTree (baseNativeTree.BaseNativeTreeWidget):

    """Leo qt tree class, a subclass of BaseNativeTreeWidget."""

    callbacksInjected = False # A class var.

    #@+others
    #@+node:ekr.20110605121601.18404: *4*  Birth (LeoQtTree)
    #@+node:ekr.20110605121601.18405: *5* ctor (LeoQtTree)
    def __init__(self,c,frame):

        # Init the base class.
        baseNativeTree.BaseNativeTreeWidget.__init__(self,c,frame)

        # Components.
        self.headlineWrapper = QHeadlineWrapper # This is a class.
        self.treeWidget = w = frame.top.leo_ui.treeWidget # An internal ivar.
            # w is a LeoQTreeWidget, a subclass of QTreeWidget.
            
        # g.trace('LeoQtTree',w)

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
    #@+node:ekr.20110605121601.18406: *5* qtTree.initAfterLoad
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
    #@+node:ekr.20110605121601.18407: *4* Widget-dependent helpers (LeoQtTree)
    #@+node:ekr.20110605121601.18408: *5* Drawing
    def clear (self):
        '''Clear all widgets in the tree.'''
        w = self.treeWidget
        w.clear()

    def repaint (self):
        '''Repaint the widget.'''
        w = self.treeWidget
        w.repaint()
        w.resizeColumnToContents(0) # 2009/12/22
    #@+node:ekr.20110605121601.18409: *5* Icons (LeoQtTree)
    #@+node:ekr.20110605121601.18410: *6* drawIcon
    def drawIcon (self,p):

        '''Redraw the icon at p.'''

        w = self.treeWidget
        itemOrTree = self.position2item(p) or w
        item = QtWidgets.QTreeWidgetItem(itemOrTree)
        icon = self.getIcon(p)
        self.setItemIcon(item,icon)

    #@+node:ekr.20110605121601.18411: *6* getIcon & helper (qtTree)
    def getIcon(self,p):

        '''Return the proper icon for position p.'''

        p.v.iconVal = val = p.v.computeIcon()
        return self.getCompositeIconImage(p,val)
    #@+node:ekr.20110605121601.18412: *7* getCompositeIconImage
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
    #@+node:ekr.20110605121601.18413: *6* setItemIconHelper (qtTree)
    def setItemIconHelper (self,item,icon):

        # Generates an item-changed event.
        # g.trace(id(icon))
        if item:
            item.setIcon(0,icon)
    #@+node:ekr.20110605121601.18414: *5* Items (LeoQtTree)
    #@+node:ekr.20110605121601.18415: *6* childIndexOfItem
    def childIndexOfItem (self,item):

        parent = item and item.parent()

        if parent:
            n = parent.indexOfChild(item)
        else:
            w = self.treeWidget
            n = w.indexOfTopLevelItem(item)

        return n

    #@+node:ekr.20110605121601.18416: *6* childItems
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
    #@+node:ekr.20110605121601.18417: *6* closeEditorHelper (LeoQtTree)
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
    #@+node:ekr.20110605121601.18418: *6* connectEditorWidget & helper
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
    #@+node:ekr.20110605121601.18419: *6* contractItem & expandItem
    def contractItem (self,item):

        # g.trace(g.callers(4))

        self.treeWidget.collapseItem(item)

    def expandItem (self,item):

        # g.trace(g.callers(4))

        self.treeWidget.expandItem(item)
    #@+node:ekr.20110605121601.18420: *6* createTreeEditorForItem (LeoQtTree)
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
    #@+node:ekr.20110605121601.18421: *6* createTreeItem
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
    #@+node:ekr.20110605121601.18422: *6* editLabelHelper (leoQtTree)
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
                if vc.is_text_widget(wrapper):
                    vc.begin_insert_mode(w=wrapper)
                else:
                    g.trace('not a text widget!',wrapper)
        if trace: g.trace(e,wrapper)
        return e,wrapper # 2011/02/11
    #@+node:ekr.20110605121601.18423: *6* getCurrentItem
    def getCurrentItem (self):

        w = self.treeWidget
        return w.currentItem()
    #@+node:ekr.20110605121601.18424: *6* getItemText
    def getItemText (self,item):

        '''Return the text of the item.'''

        if item:
            return g.u(item.text(0))
        else:
            return '<no item>'
    #@+node:ekr.20110605121601.18425: *6* getParentItem
    def getParentItem(self,item):

        return item and item.parent()
    #@+node:ekr.20110605121601.18426: *6* getSelectedItems
    def getSelectedItems(self):
        w = self.treeWidget    
        return w.selectedItems()
    #@+node:ekr.20110605121601.18427: *6* getTreeEditorForItem (LeoQtTree)
    def getTreeEditorForItem(self,item):

        '''Return the edit widget if it exists.
        Do *not* create one if it does not exist.'''

        trace = False and not g.unitTesting
        w = self.treeWidget
        e = w.itemWidget(item,0)
        if trace and e: g.trace(e.__class__.__name__)
        return e
    #@+node:ekr.20110605121601.18428: *6* getWrapper (LeoQtTree)
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
    #@+node:ekr.20110605121601.18429: *6* nthChildItem
    def nthChildItem (self,n,parent_item):

        children = self.childItems(parent_item)

        if n < len(children):
            item = children[n]
        else:
            # This is **not* an error.
            # It simply means that we need to redraw the tree.
            item = None

        return item
    #@+node:ekr.20110605121601.18430: *6* scrollToItem (LeoQtTree)
    def scrollToItem (self,item):

        w = self.treeWidget

        # g.trace(self.traceItem(item),g.callers(4))

        hPos,vPos = self.getScroll()

        w.scrollToItem(item,w.PositionAtCenter)

        self.setHScroll(0)
    #@+node:ekr.20110605121601.18431: *6* setCurrentItemHelper (LeoQtTree)
    def setCurrentItemHelper(self,item):

        w = self.treeWidget
        w.setCurrentItem(item)
    #@+node:ekr.20110605121601.18432: *6* setItemText
    def setItemText (self,item,s):

        if item:
            item.setText(0,s)
    #@+node:ekr.20110605121601.18433: *5* Scroll bars (LeoQtTree)
    #@+node:ekr.20110605121601.18434: *6* getSCroll
    def getScroll (self):

        '''Return the hPos,vPos for the tree's scrollbars.'''

        w = self.treeWidget
        hScroll = w.horizontalScrollBar()
        vScroll = w.verticalScrollBar()
        hPos = hScroll.sliderPosition()
        vPos = vScroll.sliderPosition()
        return hPos,vPos
    #@+node:ekr.20110605121601.18435: *6* setH/VScroll
    def setHScroll (self,hPos):
        w = self.treeWidget
        hScroll = w.horizontalScrollBar()
        hScroll.setValue(hPos)

    def setVScroll (self,vPos):
        # g.trace(vPos)
        w = self.treeWidget
        vScroll = w.verticalScrollBar()
        vScroll.setValue(vPos)
    #@+node:btheado.20111110215920.7164: *6* scrollDelegate (LeoQtTree)
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
    #@+node:ekr.20110605121601.18437: *5* onContextMenu (LeoQtTree)
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
#@+node:ekr.20110605121601.18438: *3* class LeoQtTreeTab
class LeoQtTreeTab:

    '''A class representing a so-called tree-tab.

    Actually, it represents a combo box'''

    #@+others
    #@+node:ekr.20110605121601.18439: *4*  Birth & death
    #@+node:ekr.20110605121601.18440: *5*  ctor (LeoTreeTab)
    def __init__ (self,c,iconBar):

        # g.trace('(LeoTreeTab)',g.callers(4))

        self.c = c
        self.cc = c.chapterController
        assert self.cc
        self.iconBar = iconBar
        self.lockout = False # True: do not redraw.
        self.tabNames = []
            # The list of tab names. Changes when tabs are renamed.
        self.w = None # The QComboBox

        self.createControl()
    #@+node:ekr.20110605121601.18441: *5* tt.createControl (defines class LeoQComboBox)
    def createControl (self):
        
        class LeoQComboBox(QtWidgets.QComboBox):
            '''Create a subclass in order to handle focusInEvents.'''
            def __init__(self,tt):
                self.leo_tt = tt
                QtWidgets.QComboBox.__init__(self) # Init the base class.
            def focusInEvent(self,event):
                self.leo_tt.setNames()
                QtWidgets.QComboBox.focusInEvent(self,event) # Call the base class

        tt = self
        frame = QtWidgets.QLabel('Chapters: ')
        tt.iconBar.addWidget(frame)
        tt.w = w = LeoQComboBox(tt)
        tt.setNames()
        tt.iconBar.addWidget(w)
        def onIndexChanged(s,tt=tt):
            if type(s) == type(9):
                s = '' if s == -1 else tt.w.currentText()
            else: # s is the tab name.
                s = g.u(s)
            if s and not tt.cc.selectChapterLockout:
                tt.cc.selectChapterLockout = True
                try:
                    tt.selectTab(s)
                finally:
                    tt.cc.selectChapterLockout = False
        # A change: the argument could now be an int instead of a string.
        w.currentIndexChanged.connect(onIndexChanged)
    #@+node:ekr.20110605121601.18443: *4* tt.createTab
    def createTab (self,tabName,select=True):

        tt = self
        # Avoid a glitch during initing.
        if tabName != 'main' and tabName not in tt.tabNames:
            tt.tabNames.append(tabName)
            tt.setNames()
    #@+node:ekr.20110605121601.18444: *4* tt.destroyTab
    def destroyTab (self,tabName):

        tt = self
        if tabName in tt.tabNames:
            tt.tabNames.remove(tabName)
            tt.setNames()
    #@+node:ekr.20110605121601.18445: *4* tt.selectTab
    def selectTab (self,tabName):

        tt,c,cc = self,self.c,self.cc
        exists = tabName in self.tabNames
        if not exists:
            tt.createTab(tabName) # Calls tt.setNames()
        if not tt.lockout:
            cc.selectChapterByName(tabName)
            c.redraw()
            c.outerUpdate()
    #@+node:ekr.20110605121601.18446: *4* tt.setTabLabel
    def setTabLabel (self,tabName):

        tt,w = self,self.w
        i = w.findText (tabName)
        if i > -1:
            w.setCurrentIndex(i)
    #@+node:ekr.20110605121601.18447: *4* tt.setNames
    def setNames (self):

        '''Recreate the list of items.'''

        tt,w = self,self.w
        names = self.cc.setAllChapterNames()
        w.clear()
        w.insertItems(0,names)
    #@-others
#@+node:ekr.20110605121601.18448: *3* class LeoTabbedTopLevel (LeoBaseTabWidget)
class LeoTabbedTopLevel(LeoBaseTabWidget):
    """ Toplevel frame for tabbed ui """
    def __init__(self, *args, **kwargs):
        LeoBaseTabWidget.__init__(self,*args,**kwargs)
        ## middle click close on tabs -- JMP 20140505
        self.setMovable(False)
        tb = QtTabBarWrapper(self)
        self.setTabBar(tb)
#@+node:peckj.20140505102552.10377: *3* class QtTabBarWrapper (QTabBar)
class QtTabBarWrapper(QtWidgets.QTabBar): 
    #@+others
    #@+node:peckj.20140516114832.10108: *4* __init__
    def __init__(self, parent=None):
        QtWidgets.QTabBar.__init__(self, parent)
        self.setMovable(True)
    #@+node:peckj.20140516114832.10109: *4* mouseReleaseEvent
    def mouseReleaseEvent(self, event):
        ## middle click close on tabs -- JMP 20140505
        ## closes Launchpad bug: https://bugs.launchpad.net/leo-editor/+bug/1183528
        ## Using this blogpost as a guide:
        ## http://www.mikeyd.com.au/2011/03/12/adding-the-ability-to-close-a-tab-with-mouses-middle-button-to-qts-qtabwidget/
        if event.button() == QtCore.Qt.MidButton:
            self.tabCloseRequested.emit(self.tabAt(event.pos()))
        QtWidgets.QTabBar.mouseReleaseEvent(self, event)
    #@-others
     
#@+node:ekr.20110605121601.18458: *3* class QtMenuWrapper (LeoQtMenu,QMenu)
class QtMenuWrapper (LeoQtMenu,QtWidgets.QMenu): ### Reversed order.

    #@+others
    #@+node:ekr.20110605121601.18459: *4* ctor and __repr__(QtMenuWrapper)
    def __init__ (self,c,frame,parent,label):
        '''ctor for QtMenuWrapper class.'''
        assert c
        assert frame
        if parent is None:
            parent = c.frame.top.menuBar()
        # g.trace('(QtMenuWrapper) label: %s parent: %s' % (label,parent))
        if True: ### isQt5:
            # g.trace(QtWidgets.QMenu.__init__)
            # For reasons unknown, the calls must be in this order.
            # Presumably, the order of base classes also matters(!)
            LeoQtMenu.__init__(self,c,frame,label)
            QtWidgets.QMenu.__init__(self,parent)
        else:
            QtWidgets.QMenu.__init__(self,parent)
            LeoQtMenu.__init__(self,c,frame,label)

        label = label.replace('&','').lower()
        self.leo_menu_label = label
        action = self.menuAction()
        if action:
            action.leo_menu_label = label
        # g.trace('(qtMenuWrappter)',label)
        self.aboutToShow.connect(self.onAboutToShow)

    def __repr__(self):
        return '<QtMenuWrapper %s>' % self.leo_menu_label
    #@+node:ekr.20110605121601.18460: *4* onAboutToShow & helpers (QtMenuWrapper)
    def onAboutToShow(self,*args,**keys):

        trace = False and not g.unitTesting
        name = self.leo_menu_label
        if not name: return
        for action in self.actions():
            commandName = hasattr(action,'leo_command_name') and action.leo_command_name
            if commandName:
                if trace: g.trace(commandName)
                self.leo_update_shortcut(action,commandName)
                self.leo_enable_menu_item(action,commandName)
                self.leo_update_menu_label(action,commandName)

    #@+node:ekr.20120120095156.10261: *5* leo_enable_menu_item
    def leo_enable_menu_item (self,action,commandName):

        func = self.c.frame.menu.enable_dict.get(commandName)

        if action and func:
            val = func()
            # g.trace('%5s %20s %s' % (val,commandName,val))
            action.setEnabled(bool(val))

    #@+node:ekr.20120124115444.10190: *5* leo_update_menu_label
    def leo_update_menu_label(self,action,commandName):

        c = self.c

        if action and commandName == 'mark':
            action.setText('UnMark' if c.p.isMarked() else 'Mark')
            self.leo_update_shortcut(action,commandName)
                # Set the proper shortcut.
    #@+node:ekr.20120120095156.10260: *5* leo_update_shortcut
    def leo_update_shortcut(self,action,commandName):

        trace = False and not g.unitTesting
        c = self.c ; k = c.k

        if action:
            s = action.text()
            parts = s.split('\t')
            if len(parts) >= 2: s = parts[0]
            key,aList = c.config.getShortcut(commandName)
            if aList:
                result = []
                for si in aList:
                    assert g.isShortcutInfo(si),si
                    # Don't show mode-related bindings.
                    if not si.isModeBinding():
                        accel = k.prettyPrintKey(si.stroke)
                        if trace: g.trace('%20s %s' % (accel,si.dump()))
                        result.append(accel)
                        # Break here if we want to show only one accerator.
                action.setText('%s\t%s' % (s,', '.join(result)))
            else:
                action.setText(s)
        else:
            g.trace('can not happen: no action for %s' % (commandName))
    #@-others
#@+node:ekr.20110605121601.18461: *3* class QtSearchWidget
class QtSearchWidget:

    """A dummy widget class to pass to Leo's core find code."""

    def __init__ (self):

        self.insertPoint = 0
        self.selection = 0,0
        self.bodyCtrl = self
        self.body = self
        self.text = None
#@+node:ekr.20110605121601.18462: *3* class SDIFrameFactory
class SDIFrameFactory:
    """ 'Toplevel' frame builder 

    This only deals with Qt level widgets, not Leo wrappers
    """

    #@+others
    #@+node:ekr.20110605121601.18463: *4* createFrame (SDIFrameFactory)
    def createFrame(self, leoFrame):

        c = leoFrame.c
        dw = DynamicWindow(c)    
        dw.construct()
        g.app.gui.attachLeoIcon(dw)
        dw.setWindowTitle(leoFrame.title)
        g.app.gui.setFilter(c,dw,dw,tag='sdi-frame')
        if g.app.start_minimized:
            dw.showMinimized()
        elif g.app.start_maximized:
            dw.showMaximized()
        elif g.app.start_fullscreen:
            dw.showFullScreen()
        else:
            dw.show()
        return dw

    def deleteFrame(self, wdg):
        # Do not delete.  Called from destroySelf.
        pass
    #@-others
#@+node:ekr.20110605121601.18464: *3* class TabbedFrameFactory
class TabbedFrameFactory:
    """ 'Toplevel' frame builder for tabbed toplevel interface

    This causes Leo to maintain only one toplevel window,
    with multiple tabs for documents
    """

    #@+others
    #@+node:ekr.20110605121601.18465: *4*  ctor (TabbedFrameFactory)
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

        # g.trace('(TabbedFrameFactory)',g.callers())
    #@+node:ekr.20110605121601.18466: *4* createFrame (TabbedFrameFactory)
    def createFrame(self, leoFrame):

        # g.trace('*** (TabbedFrameFactory)')
        c = leoFrame.c
        if self.masterFrame is None:
            self.createMaster()
        tabw = self.masterFrame
        dw = DynamicWindow(c,tabw)
        self.leoFrames[dw] = leoFrame
        # Shorten the title.
        title = os.path.basename(c.mFileName) if c.mFileName else leoFrame.title
        tip = leoFrame.title
        dw.setWindowTitle(tip) # 2010/1/1
        idx = tabw.addTab(dw, title)
        if tip: tabw.setTabToolTip(idx, tip)
        dw.construct(master=tabw)
        tabw.setCurrentIndex(idx)
        g.app.gui.setFilter(c,dw,dw,tag='tabbed-frame')
        # Work around the problem with missing dirty indicator
        # by always showing the tab.
        tabw.tabBar().setVisible(self.alwaysShowTabs or tabw.count() > 1)
        tabw.setTabsClosable(c.config.getBool('outline_tabs_show_close', True))
        dw.show()
        tabw.show()
        return dw
    #@+node:ekr.20110605121601.18468: *4* createMaster (TabbedFrameFactory)
    def createMaster(self):
        mf = self.masterFrame = LeoTabbedTopLevel(factory=self)
        #g.trace('(TabbedFrameFactory) (sets tabbed geom)')
        g.app.gui.attachLeoIcon(mf)
        tabbar = mf.tabBar()
        try:
            tabbar.setTabsClosable(True)
            tabbar.tabCloseRequested.connect(self.slotCloseRequest)
        except AttributeError:
            pass # Qt 4.4 does not support setTabsClosable
        mf.currentChanged.connect(self.slotCurrentChanged)
        if g.app.start_minimized:
            mf.showMinimized()
        elif g.app.start_maximized:
            mf.showMaximized()
        elif g.app.start_fullscreen:
            mf.showFullScreen()
        else:
            mf.show()
    #@+node:ekr.20110605121601.18472: *4* createTabCommands (TabbedFrameFactory)
    def detachTab(self, wdg):
        """ Detach specified tab as individual toplevel window """

        del self.leoFrames[wdg]
        wdg.setParent(None)
        wdg.show()

    def createTabCommands(self):
        #@+<< Commands for tabs >>
        #@+node:ekr.20110605121601.18473: *5* << Commands for tabs >>
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
                cur = count -1
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
    #@+node:ekr.20110605121601.18467: *4* deleteFrame (TabbedFrameFactory)
    def deleteFrame(self, wdg):

        trace = False and not g.unitTesting
        if not wdg: return
        if wdg not in self.leoFrames:
            # probably detached tab
            self.masterFrame.delete(wdg)
            return
        if trace: g.trace('old',wdg.leo_c.frame.title)
            # wdg is a DynamicWindow.
        tabw = self.masterFrame
        idx = tabw.indexOf(wdg)
        tabw.removeTab(idx)
        del self.leoFrames[wdg]
        wdg2 = tabw.currentWidget()
        if wdg2:
            if trace: g.trace('new',wdg2 and wdg2.leo_c.frame.title)
            g.app.selectLeoWindow(wdg2.leo_c)
        tabw.tabBar().setVisible(self.alwaysShowTabs or tabw.count() > 1)
    #@+node:ekr.20110605121601.18471: *4* focusCurrentBody (TabbedFrameFactory)
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
    #@+node:ekr.20110605121601.18469: *4* setTabForCommander (TabbedFrameFactory)
    def setTabForCommander (self,c):

        tabw = self.masterFrame # a QTabWidget

        for dw in self.leoFrames: # A dict whose keys are DynamicWindows.
            if dw.leo_c == c:
                for i in range(tabw.count()):
                    if tabw.widget(i) == dw:
                        tabw.setCurrentIndex(i)
                        break
                break

    #@+node:ekr.20110605121601.18470: *4* signal handlers (TabbedFrameFactory)
    def slotCloseRequest(self,idx):

        trace = False and not g.unitTesting
        tabw = self.masterFrame
        w = tabw.widget(idx)
        f = self.leoFrames[w]
        c = f.c
        if trace: g.trace(f.title)
        c.close(new_c=None)
            # 2012/03/04: Don't set the frame here.
            # Wait until the next slotCurrentChanged event.
            # This keeps the log and the QTabbedWidget in sync.

    def slotCurrentChanged(self, idx):

        # Two events are generated, one for the tab losing focus,
        # and another event for the tab gaining focus.
        trace = False and not g.unitTesting
        tabw = self.masterFrame
        w = tabw.widget(idx)
        f = self.leoFrames.get(w)
        if f:
            if trace: g.trace(f.title)
            tabw.setWindowTitle(f.title)
            # g.app.selectLeoWindow(f.c)
                # would break --minimize
    #@-others
#@+node:ekr.20110605121601.18474: ** Gui wrapper
#@+node:ekr.20110605121601.18475: *3* class LeoQtGui
class LeoQtGui(leoGui.LeoGui):

    '''A class implementing Leo's Qt gui.'''

    #@+others
    #@+node:ekr.20110605121601.18476: *4*  LeoQtGui.Birth & death
    #@+node:ekr.20110605121601.18477: *5*  LeoQtGui.__init__
    def __init__ (self):
        '''Ctor for qtGui class.'''
        # Initialize the base class.
        leoGui.LeoGui.__init__(self,'qt')
        # g.trace('(qtGui)',g.callers())
        self.qtApp = QtWidgets.QApplication(sys.argv)
        self.bodyTextWidget = QTextMixin ### BaseQTextWrapper
        self.iconimages = {}
        self.idleTimeClass = IdleTime
        self.insert_char_flag = False # A flag for eventFilter.
        self.plainTextWidget = PlainTextWrapper ### BaseQTextWrapper
        self.mGuiName = 'qt'
        self.color_theme = g.app.config and g.app.config.getString('color_theme') or None
        # Communication between idle_focus_helper and activate/deactivate events.
        self.active = True
        # Put up the splash screen()
        if (g.app.use_splash_screen and
            not g.app.batchMode and
            not g.app.silentMode and
            not g.unitTesting
        ):
            self.splashScreen = self.createSplashScreen()
        if g.app.qt_use_tabs:    
            self.frameFactory = TabbedFrameFactory()
        else:
            self.frameFactory = SDIFrameFactory()
    #@+node:ekr.20110605121601.18483: *5* LeoQtGui.runMainLoop & runWithIpythonKernel
    #@+node:ekr.20130930062914.16000: *6* qtGui.runMainLoop
    def runMainLoop(self):
        '''Start the Qt main loop.'''
        g.app.gui.dismiss_splash_screen()
        if self.script:
            log = g.app.log
            if log:
                g.pr('Start of batch script...\n')
                log.c.executeScript(script=self.script)
                g.pr('End of batch script')
            else:
                g.pr('no log, no commander for executeScript in qtGui.runMainLoop')
        elif g.app.useIpython and g.app.ipython_inited:
            self.runWithIpythonKernel()
        else:
            # This can be alarming when using Python's -i option.                           
            sys.exit(self.qtApp.exec_())
    #@+node:ekr.20130930062914.16001: *6* qtGui.runWithIpythonKernel & helper
    def runWithIpythonKernel(self):
        '''Init Leo to run in an IPython shell.'''
        try:
            import leo.core.leoIPython as leoIPython
            g.app.ipk = ipk = leoIPython.InternalIPKernel()
            ipk.new_qt_console(event=None)
                # ipk.ipkernel is an IPKernelApp.
        except Exception:
            g.es_exception()
            print('can not init leo.core.leoIPython.py')
            sys.exit(1)
            # self.runMainLoop()

        @g.command("ipython-new")
        def qtshell_f(event):            
            """ Launch new ipython shell window, associated with the same ipython kernel """
            g.app.ipk.new_qt_console(event=event)

        @g.command("ipython-exec")
        def ipython_exec_f(event):
            """ Execute script in current node in ipython namespace """
            self.exec_helper(event)

        # blocks forever, equivalent of QApplication.exec_()
        ipk.ipkernel.start()
    #@+node:ekr.20130930062914.16010: *7* exec_helper
    def exec_helper(self,event):
        '''This helper is required because an unqualified "exec"
        may not appear in a nested function.
        
        '''
        c = event and event.get('c')
        ipk = g.app.ipk
        ns = ipk.namespace # The actual IPython namespace.
        ipkernel = ipk.ipkernel # IPKernelApp
        shell = ipkernel.shell # ZMQInteractiveShell
        if c and ns is not None:
            try:
                script = g.getScript(c,c.p)
                if 1:
                    code = compile(script,c.p.h,'exec')
                    shell.run_code(code) # Run using IPython.
                else:
                    exec(script,ns) # Run in Leo in the IPython namespace.
            except Exception:
                g.es_exception()
            finally:
                sys.stdout.flush()
                # sys.stderr.flush()
    #@+node:ekr.20110605121601.18484: *5* LeoQtGui.destroySelf
    def destroySelf (self):
        QtCore.pyqtRemoveInputHook()
        self.qtApp.exit()
    #@+node:ekr.20111022215436.16685: *4* LeoQtGui.Borders
    #@+node:ekr.20120927164343.10092: *5* add_border (qtGui)
    def add_border(self,c,w):
        
        trace = False and not g.unitTesting
        state = c.k and c.k.unboundKeyAction
        if state and c.use_focus_border:
            d = {
                'command':  c.focus_border_command_state_color,
                'insert':   c.focus_border_color,
                'overwrite':c.focus_border_overwrite_state_color,
            }
            color = d.get(state,c.focus_border_color)
            name = g.u(w.objectName())
            if trace: g.trace(name,'color',color)
            # if name =='richTextEdit':
                # w = c.frame.top.leo_body_inner_frame
                # self.paint_qframe(w,color)
            # elif
            if not name.startswith('head'):
                selector = w.__class__.__name__
                color = c.focus_border_color
                sheet = "border: %spx solid %s" % (c.focus_border_width,color)
                self.update_style_sheet(w,'border',sheet,selector=selector)
    #@+node:ekr.20120927164343.10093: *5* remove_border (qtGui)
    def remove_border(self,c,w):

        if c.use_focus_border:
            name = g.u(w.objectName())
            # if w.objectName()=='richTextEdit':
                # w = c.frame.top.leo_body_inner_frame
                # self.paint_qframe(w,'white')
            # elif
            if not name.startswith('head'):
                selector = w.__class__.__name__
                sheet = "border: %spx solid white" % c.focus_border_width
                self.update_style_sheet(w,'border',sheet,selector=selector)
    #@+node:ekr.20120927164343.10094: *5* paint_qframe (qtGui)
    def paint_qframe (self,w,color):

        assert isinstance(w,QtWidgets.QFrame)

        # How's this for a kludge.
        # Set this ivar for InnerBodyFrame.paintEvent.
        g.app.gui.innerBodyFrameColor = color
    #@+node:ekr.20110605121601.18485: *4* LeoQtGui.Clipboard
    def replaceClipboardWith (self,s):

        '''Replace the clipboard with the string s.'''

        trace = False and not g.unitTesting
        cb = self.qtApp.clipboard()
        if cb:
            # cb.clear()  # unnecessary, breaks on some Qt versions
            s = g.toUnicode(s)
            QtWidgets.QApplication.processEvents()
            cb.setText(s)
            QtWidgets.QApplication.processEvents()
            if trace: g.trace(len(s),type(s),s[:25])
        else:
            g.trace('no clipboard!')

    def getTextFromClipboard (self):

        '''Get a unicode string from the clipboard.'''

        trace = False and not g.unitTesting
        cb = self.qtApp.clipboard()
        if cb:
            QtWidgets.QApplication.processEvents()
            s = cb.text()
            if trace: g.trace (len(s),type(s),s[:25])
            s = g.app.gui.toUnicode(s)
                # Same as g.u(s), but with error handling.
            return s
        else:
            g.trace('no clipboard!')
            return ''
    #@+node:ekr.20110605121601.18487: *4* LeoQtGui.Dialogs & panels
    #@+node:ekr.20110605121601.18488: *5* alert (qtGui)
    def alert (self,c,message):

        if g.unitTesting: return

        b = QtWidgets.QMessageBox
        d = b(None)
        d.setWindowTitle('Alert')
        d.setText(message)
        d.setIcon(b.Warning)
        d.addButton('Ok',b.YesRole)
        c.in_qt_dialog = True
        d.exec_()
        c.in_qt_dialog = False
    #@+node:ekr.20110605121601.18489: *5* makeFilter
    def makeFilter (self,filetypes):

        '''Return the Qt-style dialog filter from filetypes list.'''

        filters = ['%s (%s)' % (z) for z in filetypes]

        return ';;'.join(filters)
    #@+node:ekr.20110605121601.18492: *5* qtGui panels (qtGui)
    def createComparePanel(self,c):

        """Create a qt color picker panel."""
        return None # This window is optional.
        # return leoQtComparePanel(c)

    def createFindTab (self,c,parentFrame):
        """Create a qt find tab in the indicated frame."""
        pass # Now done in dw.createFindTab.

    def createLeoFrame(self,c,title):
        """Create a new Leo frame."""
        gui = self
        return LeoQtFrame(c,title,gui)

    def createSpellTab(self,c,spellHandler,tabName):
        return LeoQtSpellTab(c,spellHandler,tabName)

    #@+node:ekr.20110605121601.18493: *5* runAboutLeoDialog
    def runAboutLeoDialog(self,c,version,theCopyright,url,email):

        """Create and run a qt About Leo dialog."""

        if g.unitTesting: return None

        b = QtWidgets.QMessageBox
        d = b(c.frame.top)

        d.setText('%s\n%s\n%s\n%s' % (
            version,theCopyright,url,email))
        d.setIcon(b.Information)
        yes = d.addButton('Ok',b.YesRole)
        d.setDefaultButton(yes)
        c.in_qt_dialog = True
        d.exec_()
        c.in_qt_dialog = False
    #@+node:ekr.20110605121601.18496: *5* runAskDateTimeDialog
    def runAskDateTimeDialog(self, c, title, 
        message='Select Date/Time', init=None, step_min={}):
        """Create and run a qt date/time selection dialog.

        init - a datetime, default now
        step_min - a dict, keys are QtWidgets.QDateTimeEdit Sections, like
          QtWidgets.QDateTimeEdit.MinuteSection, and values are integers,
          the minimum amount that section of the date/time changes
          when you roll the mouse wheel.

        E.g. (5 minute increments in minute field):

            print g.app.gui.runAskDateTimeDialog(c, 'When?',
              message="When is it?",
              step_min={QtWidgets.QDateTimeEdit.MinuteSection: 5})

        """

        class DateTimeEditStepped(QtWidgets.QDateTimeEdit):
            """QDateTimeEdit which allows you to set minimum steps on fields, e.g.
              DateTimeEditStepped(parent, {QtWidgets.QDateTimeEdit.MinuteSection: 5})
            for a minimum 5 minute increment on the minute field.
            """
            def __init__(self, parent=None, init=None, step_min={}):

                self.step_min = step_min
                if init:
                    QtWidgets.QDateTimeEdit.__init__(self, init, parent)
                else:
                    QtWidgets.QDateTimeEdit.__init__(self, parent)

            def stepBy(self, step):
                cs = self.currentSection()
                if cs in self.step_min and abs(step) < self.step_min[cs]:
                    step = self.step_min[cs] if step > 0 else -self.step_min[cs]
                QtWidgets.QDateTimeEdit.stepBy(self, step)

        class Calendar(QtWidgets.QDialog):
            def __init__(self, parent=None, message='Select Date/Time',
                init=None, step_min={}):
                QtWidgets.QDialog.__init__(self, parent)

                layout = QtWidgets.QVBoxLayout()
                self.setLayout(layout)

                layout.addWidget(QtWidgets.QLabel(message))

                self.dt = DateTimeEditStepped(init=init, step_min=step_min)
                self.dt.setCalendarPopup(True)
                layout.addWidget(self.dt)

                buttonBox = QtWidgets.QDialogButtonBox(
                QtWidgets.QDialogButtonBox.Ok
                    | QtWidgets.QDialogButtonBox.Cancel)
                layout.addWidget(buttonBox)

                buttonBox.accepted.connect(self.accept)
                buttonBox.rejected.connect(self.reject)

        if g.unitTesting: return None

        b = Calendar
        if not init:
            init = datetime.datetime.now()
        d = b(c.frame.top, message=message, init=init, step_min=step_min)

        d.setWindowTitle(title)

        c.in_qt_dialog = True
        val = d.exec_()
        c.in_qt_dialog = False

        if val != d.Accepted:
            return None
        else:
            return d.dt.dateTime().toPyDateTime()
    #@+node:ekr.20110605121601.18494: *5* runAskLeoIDDialog
    def runAskLeoIDDialog(self):

        """Create and run a dialog to get g.app.LeoID."""

        if g.unitTesting: return None

        message = (
            "leoID.txt not found\n\n" +
            "Please enter an id that identifies you uniquely.\n" +
            "Your cvs/bzr login name is a good choice.\n\n" +
            "Leo uses this id to uniquely identify nodes.\n\n" +
            "Your id must contain only letters and numbers\n" +
            "and must be at least 3 characters in length.")
        parent = None
        title = 'Enter Leo id'
        s,ok = QtWidgets.QInputDialog.getText(parent,title,message)
        return g.u(s)
    #@+node:ekr.20110605121601.18491: *5* runAskOkCancelNumberDialog
    def runAskOkCancelNumberDialog(self,c,title,message,cancelButtonText=None,okButtonText=None):

        """Create and run askOkCancelNumber dialog ."""

        if g.unitTesting: return None

        # n,ok = QtWidgets.QInputDialog.getDouble(None,title,message)
        d = QtWidgets.QInputDialog()
        d.setWindowTitle(title)
        d.setLabelText(message)
        if cancelButtonText:
            d.setCancelButtonText(cancelButtonText)
        if okButtonText:
            d.setOkButtonText(okButtonText)
        ok = d.exec_()
        n = d.textValue()
        try:
            n = float(n)
        except ValueError:
            n = None
        return n if ok else None
    #@+node:ekr.20110605121601.18490: *5* runAskOkCancelStringDialog
    def runAskOkCancelStringDialog(self,c,title,message,cancelButtonText=None,
                                   okButtonText=None,default=""):

        """Create and run askOkCancelString dialog ."""

        if g.unitTesting: return None

        d = QtWidgets.QInputDialog()
        d.setWindowTitle(title)
        d.setLabelText(message)
        d.setTextValue(default)
        if cancelButtonText:
            d.setCancelButtonText(cancelButtonText)
        if okButtonText:
            d.setOkButtonText(okButtonText)
        ok = d.exec_()
        return str(d.textValue()) if ok else None
    #@+node:ekr.20110605121601.18495: *5* runAskOkDialog
    def runAskOkDialog(self,c,title,message=None,text="Ok"):

        """Create and run a qt askOK dialog ."""

        if g.unitTesting: return None
        b = QtWidgets.QMessageBox
        d = b(c.frame.top)
        d.setWindowTitle(title)
        if message: d.setText(message)
        d.setIcon(b.Information)
        d.addButton(text,b.YesRole)
        c.in_qt_dialog = True
        d.exec_()
        c.in_qt_dialog = False
    #@+node:ekr.20110605121601.18497: *5* runAskYesNoCancelDialog
    def runAskYesNoCancelDialog(self,c,title,
        message=None,
        yesMessage="&Yes",
        noMessage="&No",
        yesToAllMessage=None,
        defaultButton="Yes"
    ):

        """Create and run an askYesNo dialog."""

        if g.unitTesting:
            return None
        b = QtWidgets.QMessageBox
        d = b(c.frame.top)
        if message: d.setText(message)
        d.setIcon(b.Warning)
        d.setWindowTitle(title)
        yes      = d.addButton(yesMessage,b.YesRole)
        no       = d.addButton(noMessage,b.NoRole)
        yesToAll = d.addButton(yesToAllMessage,b.YesRole) if yesToAllMessage else None
        cancel = d.addButton(b.Cancel)
        if   defaultButton == "Yes": d.setDefaultButton(yes)
        elif defaultButton == "No": d.setDefaultButton(no)
        else: d.setDefaultButton(cancel)
        c.in_qt_dialog = True
        val = d.exec_()
        c.in_qt_dialog = False
        if   val == 0: val = 'yes'
        elif val == 1: val = 'no'
        elif yesToAll and val == 2: val = 'yes-to-all'
        else: val = 'cancel'
        return val
    #@+node:ekr.20110605121601.18498: *5* runAskYesNoDialog
    def runAskYesNoDialog(self,c,title,message=None):

        """Create and run an askYesNo dialog."""

        if g.unitTesting: return None
        b = QtWidgets.QMessageBox
        d = b(c.frame.top)
        d.setWindowTitle(title)
        if message: d.setText(message)
        d.setIcon(b.Information)
        yes = d.addButton('&Yes',b.YesRole)
        d.addButton('&No',b.NoRole)
        d.setDefaultButton(yes)
        c.in_qt_dialog = True
        val = d.exec_()
        c.in_qt_dialog = False
        return 'yes' if val == 0 else 'no'
    #@+node:ekr.20110605121601.18499: *5* runOpenDirectoryDialog (qtGui)
    def runOpenDirectoryDialog(self,title,startdir):

        """Create and run an Qt open directory dialog ."""

        parent = None
        s = QtWidgets.QFileDialog.getExistingDirectory (parent,title,startdir)
        return g.u(s)
    #@+node:ekr.20110605121601.18500: *5* runOpenFileDialog (qtGui)
    def runOpenFileDialog(self,title,filetypes,defaultextension='',multiple=False,startpath=None):

        """Create and run an Qt open file dialog ."""

        if g.unitTesting:
            return ''
        else:
            if startpath is None:
                startpath = os.curdir

            parent = None
            filter = self.makeFilter(filetypes)

            if multiple:
                lst = QtWidgets.QFileDialog.getOpenFileNames(parent,title,startpath,filter)
                if isQt5:  # this is a *Py*Qt change rather than a Qt change
                    lst, selected_filter = lst
                return [g.u(s) for s in lst]
            else:
                s = QtWidgets.QFileDialog.getOpenFileName(parent,title,startpath,filter)
                if isQt5:
                    s, selected_filter = s
                return g.u(s)
    #@+node:ekr.20110605121601.18501: *5* runPropertiesDialog (qtGui)
    def runPropertiesDialog(self,
        title='Properties',data={}, callback=None, buttons=None):

        """Dispay a modal TkPropertiesDialog"""

        # g.trace(data)
        g.warning('Properties menu not supported for Qt gui')
        result = 'Cancel'
        return result,data
    #@+node:ekr.20110605121601.18502: *5* runSaveFileDialog (qtGui)
    def runSaveFileDialog(self,initialfile='',title='Save',filetypes=[],defaultextension=''):

        """Create and run an Qt save file dialog ."""

        if g.unitTesting:
            return ''
        else:
            parent = None
            filter_ = self.makeFilter(filetypes)
            s = QtWidgets.QFileDialog.getSaveFileName(parent,title,os.curdir,filter_)
            return g.u(s)
    #@+node:ekr.20110605121601.18503: *5* runScrolledMessageDialog (qtGui)
    def runScrolledMessageDialog (self,
        short_title= '',
        title='Message',
        label= '',
        msg='',
        c=None,**kw
    ):

        if g.unitTesting: return None

        def send(title=title, label=label, msg=msg, c=c, kw=kw):
            return g.doHook('scrolledMessage',
                short_title=short_title,title=title,
                label=label, msg=msg,c=c, **kw)

        if not c or not c.exists:
            #@+<< no c error>>
            #@+node:ekr.20110605121601.18504: *6* << no c error>>
            g.es_print_error('%s\n%s\n\t%s' % (
                "The qt plugin requires calls to g.app.gui.scrolledMessageDialog to include 'c'",
                "as a keyword argument",
                g.callers()
            ))
            #@-<< no c error>>
        else:        
            retval = send()
            if retval: return retval
            #@+<< load viewrendered plugin >>
            #@+node:ekr.20110605121601.18505: *6* << load viewrendered plugin >>
            pc = g.app.pluginsController
            # 2011/10/20: load viewrendered (and call vr.onCreate)
            # *only* if not already loaded.
            if not pc.isLoaded('viewrendered.py') and not pc.isLoaded('viewrendered2.py'):
                vr = pc.loadOnePlugin('viewrendered.py')
                if vr:
                    g.blue('viewrendered plugin loaded.')
                    vr.onCreate('tag',{'c':c})
            #@-<< load viewrendered plugin >>
            retval = send()
            if retval: return retval
            #@+<< no dialog error >>
            #@+node:ekr.20110605121601.18506: *6* << no dialog error >>
            g.es_print_error(
                'No handler for the "scrolledMessage" hook.\n\t%s' % (
                    g.callers()))
            #@-<< no dialog error >>
        #@+<< emergency fallback >>
        #@+node:ekr.20110605121601.18507: *6* << emergency fallback >>
        b = QtWidgets.QMessageBox
        d = b(None) # c.frame.top)
        d.setWindowFlags(QtCore.Qt.Dialog)
            # That is, not a fixed size dialog.
        d.setWindowTitle(title)
        if msg: d.setText(msg)
        d.setIcon(b.Information)
        d.addButton('Ok',b.YesRole)
        c.in_qt_dialog = True
        d.exec_()
        c.in_qt_dialog = False
        #@-<< emergency fallback >>
    #@+node:ekr.20110607182447.16456: *4* LeoQtGui.Event handlers
    #@+node:ekr.20110605121601.18481: *5* LeoQtGui.onDeactiveEvent
    deactivated_name = ''

    def onDeactivateEvent (self,event,c,obj,tag):
        '''Gracefully deactivate the Leo window.'''
        trace = False and not g.unitTesting
        # This is called several times for each window activation.
        if c.exists and not self.deactivated_name:
            self.deactivated_name = self.widget_name(self.get_focus())
            self.active = False
            if trace: g.trace(self.deactivated_name)
            c.k.keyboardQuit(setFocus=False)
                # The best way to retain as much focus as possible.
            g.doHook('deactivate',c=c,p=c.p,v=c.p,event=event)
    #@+node:ekr.20110605121601.18480: *5* LeoQtGui.onActivateEvent
    # Called from eventFilter

    def onActivateEvent (self,event,c,obj,tag):
        '''Restore the focus when the Leo window is activated.'''
        # This is called several times for each window activation.
        trace = False and not g.unitTesting
        if c.exists and self.deactivated_name:
            self.active = True
            w_name = self.deactivated_name
            self.deactivated_name = None
            if trace: g.trace(w_name)
            if c.p.v:
                c.p.v.restoreCursorAndScroll()
            if w_name.startswith('tree') or w_name.startswith('head'):
                c.treeWantsFocusNow()
            else:
                c.bodyWantsFocusNow()
            g.doHook('activate',c=c,p=c.p,v=c.p,event=event)
    #@+node:ekr.20130921043420.21175: *5* LeoQtGui.setFilter
    # w's type is in (DynamicWindow,QMinibufferWrapper,LeoQtLog,LeoQtTree,
    # QTextEditWrapper,LeoQTextBrowser,LeoQuickSearchWidget,cleoQtUI)
    def setFilter(self,c,obj,w,tag):
        '''
        Create an event filter in obj.
        w is a wrapper object, not necessarily a QWidget.
        '''
        if 0:
            g.trace(isinstance(w,QtWidgets.QWidget),
                hasattr(w,'getName') and w.getName() or None,
                w.__class__.__name__)
        if 0:
            g.trace('obj: %4s %20s w: %5s %s' % (
                isinstance(obj,QtWidgets.QWidget),obj.__class__.__name__,
                isinstance(w,QtWidgets.QWidget),w.__class__.__name__))
        assert isinstance(obj,QtWidgets.QWidget),obj
        gui = self
        theFilter = LeoQtEventFilter(c,w=w,tag=tag)
        obj.installEventFilter(theFilter)
        w.ev_filter = theFilter
            # Set the official ivar in w.
    #@+node:ekr.20110605121601.18508: *4* LeoQtGui.Focus
    def get_focus(self,c=None,raw=False):
        """Returns the widget that has focus."""
        # pylint: disable=w0221
        # Arguments number differs from overridden method.
        trace = False and not g.unitTesting
        app = QtWidgets.QApplication
        w = app.focusWidget()
        if w and not raw and isinstance(w,LeoQTextBrowser):
            has_w = hasattr(w,'leo_wrapper') and w.leo_wrapper
            if has_w:
                if trace: g.trace(w)
            elif c:
                # Kludge: DynamicWindow creates the body pane
                # with wrapper = None, so return the LeoQtBody.
                w = c.frame.body
        if trace: g.trace('(qtGui)',w.__class__.__name__,g.callers())
        return w

    def set_focus(self,c,w):
        """Put the focus on the widget."""
        trace = False and not g.unitTesting
        gui = self
        if w:
            if hasattr(w,'widget') and w.widget: w = w.widget
            if trace: g.trace('(qtGui)',w.__class__.__name__)
            w.setFocus()

    def ensure_commander_visible(self, c1):
        """Check to see if c.frame is in a tabbed ui, and if so, make sure
        the tab is visible"""

        # START: copy from Code-->Startup & external files-->@file runLeo.py -->run & helpers-->doPostPluginsInit & helpers (runLeo.py)
        # For qttabs gui, select the first-loaded tab.
        if hasattr(g.app.gui,'frameFactory'):
            factory = g.app.gui.frameFactory
            if factory and hasattr(factory,'setTabForCommander'):
                c = c1
                factory.setTabForCommander(c)
                c.bodyWantsFocusNow()
        # END: copy
    #@+node:ekr.20110605121601.18509: *4* LeoQtGui.Fonts
    #@+node:ekr.20110605121601.18510: *5* qtGui.getFontFromParams
    def getFontFromParams(self,family,size,slant,weight,defaultSize=12):

        trace = False and not g.unitTesting
        try: size = int(size)
        except Exception: size = 0
        if size < 1: size = defaultSize
        d = {
            'black':QtGui.QFont.Black,
            'bold':QtGui.QFont.Bold,
            'demibold':QtGui.QFont.DemiBold,
            'light':QtGui.QFont.Light,
            'normal':QtGui.QFont.Normal,
        }
        weight_val = d.get(weight.lower(),QtGui.QFont.Normal)
        italic = slant == 'italic'
        if not family:
            family = g.app.config.defaultFontFamily
        if not family:
            family = 'DejaVu Sans Mono'
        try:
            font = QtGui.QFont(family,size,weight_val,italic)
            if trace: g.trace(family,size,g.callers())
            return font
        except:
            g.es("exception setting font",g.callers(4))
            g.es("","family,size,slant,weight:","",family,"",size,"",slant,"",weight)
            # g.es_exception() # This just confuses people.
            return g.app.config.defaultFont
    #@+node:ekr.20110605121601.18511: *4* LeoQtGui.getFullVersion
    def getFullVersion (self,c=None):
        '''Return the PyQt version (for signon)'''
        try:
            qtLevel = 'version %s' % QtCore.QT_VERSION_STR
        except Exception:
            # g.es_exception()
            qtLevel = '<qtLevel>'
        return 'PyQt %s' % (qtLevel)
    #@+node:ekr.20110605121601.18514: *4* LeoQtGui.Icons
    #@+node:ekr.20110605121601.18515: *5* attachLeoIcon (qtGui)
    def attachLeoIcon (self,window):

        """Attach a Leo icon to the window."""

        #icon = self.getIconImage('leoApp.ico')

        #window.setWindowIcon(icon)
        window.setWindowIcon(QtGui.QIcon(g.app.leoDir + "/Icons/leoapp32.png"))    
        #window.setLeoWindowIcon()
    #@+node:ekr.20110605121601.18516: *5* getIconImage (qtGui)
    def getIconImage (self,name):

        '''Load the icon and return it.'''

        trace = False and not g.unitTesting
        verbose = False

        # Return the image from the cache if possible.
        if name in self.iconimages:
            image = self.iconimages.get(name)
            if trace and verbose: # and not name.startswith('box'):
                g.trace('cached',id(image),name,image)
            return image
        try:
            iconsDir = g.os_path_join(g.app.loadDir,"..","Icons")
            homeIconsDir = g.os_path_join(g.app.homeLeoDir,"Icons")
            for theDir in (homeIconsDir,iconsDir):
                fullname = g.os_path_finalize_join(theDir,name)
                if g.os_path_exists(fullname):
                    if 0: # Not needed: use QTreeWidget.setIconsize.
                        pixmap = QtWidgets.QPixmap()
                        pixmap.load(fullname)
                        image = QtWidgets.QIcon(pixmap)
                    else:
                        image = QtWidgets.QIcon(fullname)
                        if trace: g.trace('name',fullname,'image',image)

                    self.iconimages[name] = image
                    if trace: g.trace('new',id(image),theDir,name)
                    return image
                elif trace: g.trace('Directory not found',theDir)
            # No image found.
            if trace: g.trace('Not found',name)
            return None
        except Exception:
            g.es_print("exception loading:",fullname)
            g.es_exception()
            return None
    #@+node:ekr.20110605121601.18517: *5* getImageImage
    def getImageImage (self, name):
        '''Load the image in file named `name` and return it.
        
        If self.color_theme, set from @settings -> @string color_theme is set,
        
         - look first in $HOME/.leo/themes/<theme_name>/Icons,
         - then in .../leo/themes/<theme_name>/Icons,
         - then in .../leo/Icons,
         - as well as trying absolute path
        '''

        fullname = self.getImageImageFinder(name)
        try:
            pixmap = QtGui.QPixmap()
            pixmap.load(fullname)
            return pixmap
        except Exception:
            g.es("exception loading:",name)
            g.es_exception()
            return None
    #@+node:tbrown.20130316075512.28478: *5* getImageImageFinder
    def getImageImageFinder(self, name):
        '''Theme aware image (icon) path searching
        
        If self.color_theme, set from @settings -> @string color_theme is set,
        
         - look first in $HOME/.leo/themes/<theme_name>/Icons,
         - then in .../leo/themes/<theme_name>/Icons,
         - then in .../leo/Icons,
         - as well as trying absolute path
        '''

        if self.color_theme:
            
            # normal, unthemed path to image
            pathname = g.os_path_finalize_join(g.app.loadDir,"..","Icons")
            pathname = g.os_path_normpath(g.os_path_realpath(pathname))
            
            if g.os_path_isabs(name):
                testname = g.os_path_normpath(g.os_path_realpath(name))
            else:
                testname = name
                
            #D print(name, self.color_theme)
            #D print('pathname', pathname)
            #D print('testname', testname)
            
            if testname.startswith(pathname):
                # try after removing icons dir from path
                namepart = testname.replace(pathname, '').strip('\\/')
            else:
                namepart = testname
                
            # home dir first
            fullname = g.os_path_finalize_join(
                g.app.homeLeoDir, 'themes',
                self.color_theme, 'Icons', namepart)
                
            #D print('namepart', namepart)
            #D print('fullname', fullname)
            
            if g.os_path_exists(fullname):
                return fullname
                
            # then load dir
            fullname = g.os_path_finalize_join(
                g.app.loadDir, "..", 'themes',
                self.color_theme, 'Icons', namepart)
            
            #D print('fullname', fullname)
            
            if g.os_path_exists(fullname):
                return fullname

        # original behavior, if name is absolute this will just return it
        #D print(g.os_path_finalize_join(g.app.loadDir,"..","Icons",name))
        return g.os_path_finalize_join(g.app.loadDir,"..","Icons",name)
    #@+node:ekr.20110605121601.18518: *5* getTreeImage (test)
    def getTreeImage (self,c,path):

        image = QtGui.QPixmap(path)

        if image.height() > 0 and image.width() > 0:
            return image,image.height()
        else:
            return None,None
    #@+node:ekr.20110605121601.18519: *4* LeoQtGui.Idle Time
    #@+node:ekr.20110605121601.18520: *5* qtGui.setIdleTimeHook & setIdleTimeHookAfterDelay
    timer = None
    timer_last_delay = 0

    def setIdleTimeHook(self):
        '''
        Define a timer and its callback so that:
        a) g.app.idleTimeHook() actually gets called at idle-time,
        b) avoids busy waiting and,
        c) waits at least g.app.idleTimeDelay msec. between calls to g.app.idleTimeHook()
        '''
        #@+<< define timerCallBack >>
        #@+node:ekr.20140701055615.16735: *6* << define timerCallBack >>
        def timerCallBack():
            '''
            This is the idle time callback. It calls g.app.gui.idleTimeHook not
            more than once every g.app.idleTimeDelay msec.
            '''
            trace = False and g.app.trace_idle_time
            if g.app.idleTimeHook and g.app.idleTimeDelay > 0:
                # Idle-time processing is enabled.
                if self.timer_last_delay == 0:
                    # We are actually at idle time.
                    if trace: g.trace(g.app.idleTimeDelay,'calling:',g.app.idleTimeHook.__name__)
                    g.app.idleTimeHook() # usually g.idleTimeHookHanlder.
                    # Now wait at for at least g.app.idleTimeDelay msec.
                    self.timer_last_delay = g.app.idleTimeDelay
                    self.timer.stop()
                    self.timer.start(g.app.idleTimeDelay)
                else:
                    # We have waited at least g.app.idleTimeDelay msec.
                    # Now wait for idle time.
                    if trace: g.trace('waiting for idle time')
                    self.timer_last_delay = 0
                    self.timer.stop()
                    self.timer.start(0)
            elif self.timer:
                # Idle-time processing is disabled.  Stop the timer.
                if trace: g.trace('Null g.app.idleTimeHook: stopping timer.')
                self.timer.stop()
        #@-<< define timerCallBack >>
        if not self.timer:
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(timerCallBack)
        # Fire a single-shot at idle time.
        self.timer_last_delay = 0
        self.timer.start(0)

    setIdleTimeHookAfterDelay = setIdleTimeHook
    #@+node:ekr.20110605121601.18521: *5* qtGui.runAtIdle
    def runAtIdle (self,aFunc):
        '''This can not be called in some contexts.'''
        QtCore.QTimer.singleShot(0,aFunc)
    #@+node:ekr.20131007055150.17608: *4* LeoQtGui.insertKeyEvent
    def insertKeyEvent (self,event,i):
        
        '''Insert the key given by event in location i of widget event.w.'''
        
        import leo.core.leoGui as leoGui
        assert isinstance(event,leoGui.LeoKeyEvent)
        qevent = event.event
        assert isinstance(qevent,QtWidgets.QKeyEvent)
        qw = hasattr(event.w,'widget') and event.w.widget or None
        if qw and isinstance(qw,QtWidgets.QTextEdit):
            g.trace(i,qevent.modifiers(),g.u(qevent.text()))
            if 1:
                # Assume that qevent.text() *is* the desired text.
                # This means we don't have to hack eventFilter.
                qw.insertPlainText(qevent.text())
            else:
                # Make no such assumption.
                # We would like to use qevent to insert the character,
                # but this would invoke eventFilter again!
                # So set this flag for eventFilter, which will
                # return False, indicating that the widget must handle
                # qevent, which *presumably* is the best that can be done.
                g.app.gui.insert_char_flag = True
    #@+node:ekr.20110605121601.18528: *4* LeoQtGui.makeScriptButton
    def makeScriptButton (self,c,
        args=None,
        p=None, # A node containing the script.
        script=None, # The script itself.
        buttonText=None,
        balloonText='Script Button',
        shortcut=None,bg='LightSteelBlue1',
        define_g=True,define_name='__main__',silent=False, # Passed on to c.executeScript.
    ):

        '''Create a script button for the script in node p.
        The button's text defaults to p.headString'''

        k = c.k
        if p and not buttonText: buttonText = p.h.strip()
        if not buttonText: buttonText = 'Unnamed Script Button'
        #@+<< create the button b >>
        #@+node:ekr.20110605121601.18529: *5* << create the button b >>
        iconBar = c.frame.getIconBarObject()
        b = iconBar.add(text=buttonText)
        #@-<< create the button b >>
        #@+<< define the callbacks for b >>
        #@+node:ekr.20110605121601.18530: *5* << define the callbacks for b >>
        def deleteButtonCallback(event=None,b=b,c=c):
            if b: b.pack_forget()
            c.bodyWantsFocus()

        def executeScriptCallback (event=None,
            b=b,c=c,buttonText=buttonText,p=p and p.copy(),script=script):

            if c.disableCommandsMessage:
                g.blue('',c.disableCommandsMessage)
            else:
                g.app.scriptDict = {}
                c.executeScript(args=args,p=p,script=script,
                define_g= define_g,define_name=define_name,silent=silent)
                # Remove the button if the script asks to be removed.
                if g.app.scriptDict.get('removeMe'):
                    g.es("removing","'%s'" % (buttonText),"button at its request")
                    b.pack_forget()
            # Do not assume the script will want to remain in this commander.
        #@-<< define the callbacks for b >>
        b.configure(command=executeScriptCallback)
        if shortcut:
            #@+<< bind the shortcut to executeScriptCallback >>
            #@+node:ekr.20110605121601.18531: *5* << bind the shortcut to executeScriptCallback >>
            func = executeScriptCallback
            shortcut = k.canonicalizeShortcut(shortcut)
            ok = k.bindKey ('button', shortcut,func,buttonText)
            if ok:
                g.blue('bound @button',buttonText,'to',shortcut)
            #@-<< bind the shortcut to executeScriptCallback >>
        #@+<< create press-buttonText-button command >>
        #@+node:ekr.20110605121601.18532: *5* << create press-buttonText-button command >>
        aList = [ch if ch.isalnum() else '-' for ch in buttonText]

        buttonCommandName = ''.join(aList)
        buttonCommandName = buttonCommandName.replace('--','-')
        buttonCommandName = 'press-%s-button' % buttonCommandName.lower()

        # This will use any shortcut defined in an @shortcuts node.
        k.registerCommand(buttonCommandName,None,executeScriptCallback,pane='button',verbose=False)
        #@-<< create press-buttonText-button command >>
    #@+node:ekr.20111215193352.10220: *4* LeoQtGui.Splash Screen
    #@+node:ekr.20110605121601.18479: *5* createSplashScreen (qtGui)
    def createSplashScreen (self):
        '''Put up a splash screen with the Leo logo.'''
        trace = False and not g.unitTesting
        from leo.core.leoQt import QtCore
        qt = QtCore.Qt
        splash = None
        if sys.platform.startswith('win'):
            table = ('SplashScreen.jpg','SplashScreen.png','SplashScreen.ico')
        else:
            table = ('SplashScreen.xpm',)
        for name in table:
            fn = g.os_path_finalize_join(g.app.loadDir,'..','Icons',name)
            if g.os_path_exists(fn):
                pm = QtGui.QPixmap(fn)
                if not pm.isNull():
                    if trace: g.trace(fn)
                    splash = QtWidgets.QSplashScreen(pm,
                        qt.WindowStaysOnTopHint)
                    splash.show()
                    # This sleep is required to do the repaint.
                    QtCore.QThread.msleep(10)
                    splash.repaint()
                    break
            else:
                if trace: g.trace('no splash screen icon')
        return splash
    #@+node:ekr.20110613103140.16424: *5* dismiss_splash_screen (qtGui)
    def dismiss_splash_screen (self):

        # g.trace(g.callers())

        gui = self

        # Warning: closing the splash screen must be done in the main thread!
        if g.unitTesting:
            return

        if gui.splashScreen:
            gui.splashScreen.hide()
            # gui.splashScreen.deleteLater()
            gui.splashScreen = None
    #@+node:ekr.20110605121601.18523: *4* LeoQtGui.Style Sheets
    #@+node:ekr.20110605121601.18524: *5* setStyleSetting (qtGui)
    def setStyleSetting(self,w,widgetKind,selector,val):

        '''Set the styleSheet for w to
           "%s { %s: %s; }  % (widgetKind,selector,val)"
        '''

        s = '%s { %s: %s; }' % (widgetKind,selector,val)

        try:
            w.setStyleSheet(s)
        except Exception:
            g.es_print('bad style sheet: %s' % s)
            g.es_exception()
    #@+node:ekr.20110605121601.18525: *5* setWidgetColor (qtGui)
    badWidgetColors = []

    def setWidgetColor (self,w,widgetKind,selector,colorName):

        if not colorName: return

        # g.trace(widgetKind,selector,colorName,g.callers(4))

        # A bit of a hack: Qt color names do not end with a digit.
        # Remove them to avoid annoying qt color warnings.
        if colorName[-1].isdigit():
            colorName = colorName[:-1]

        if colorName in self.badWidgetColors:
            pass
        elif QtWidgets.QColor(colorName).isValid():
            g.app.gui.setStyleSetting(w,widgetKind,selector,colorName)
        else:
            self.badWidgetColors.append(colorName)
            g.warning('bad widget color %s for %s' % (colorName,widgetKind))
    #@+node:ekr.20111026115337.16528: *5* update_style_sheet (qtGui)
    def update_style_sheet (self,w,key,value,selector=None):
        
        # NOT USED / DON'T USE - interferes with styles, zooming etc.

        trace = False and not g.unitTesting

        # Step one: update the dict.
        d = hasattr(w,'leo_styles_dict') and w.leo_styles_dict or {}
        d[key] = value
        aList = [d.get(z) for z in list(d.keys())]
        w.leo_styles_dict = d

        # Step two: update the stylesheet.
        s = '; '.join(aList)
        if selector:
            s = '%s { %s }' % (selector,s)
        old = str(w.styleSheet())
        if old == s:
            # if trace: g.trace('no change')
            return
        if trace:
            # g.trace('old: %s\nnew: %s' % (str(w.styleSheet()),s))
            g.trace(s)
        # This call is responsible for the unwanted scrolling!
        # To avoid problems, we now set the color of the innerBodyFrame without using style sheets.
        w.setStyleSheet(s)
    #@+node:ekr.20140825042850.18411: *4* LeoQtGui.Utils...
    #@+node:ekr.20110605121601.18522: *5* LeoQtGui.isTextWidget
    def isTextWidget (self,w):
        '''Return True if w is a Text widget suitable for text-oriented commands.'''
        return w and isinstance(w,(
            LeoQtBody,LeoQtLog,QTextMixin,
            leoFrame.BaseTextWrapper, ### To be deleted.
        ))
            # 
            # BaseQTextWrapper,
    #@+node:ekr.20110605121601.18526: *5* LeoQtGui.toUnicode
    def toUnicode (self,s):

        try:
            s = g.u(s)
            return s
        except Exception:
            g.trace('*** Unicode Error: bugs possible')
            # The mass update omitted the encoding param.
            return g.toUnicode(s,reportErrors='replace')
    #@+node:ekr.20110605121601.18527: *5* LeoQtGui.widget_name
    def widget_name (self,w):

        # First try the widget's getName method.
        if not 'w':
            name = '<no widget>'
        elif hasattr(w,'getName'):
            name = w.getName()
        elif hasattr(w,'objectName'):
            name = str(w.objectName())
        elif hasattr(w,'_name'):
            name = w._name
        else:
            name = repr(w)

        # g.trace(id(w),name)
        return name
    #@+node:ekr.20111027083744.16532: *5* LeoQtGui.enableSignalDebugging
    # enableSignalDebugging(emitCall=foo) and spy your signals until you're sick to your stomach.

    if isQt5:
        pass # Not ready yet.
    else:
        _oldConnect     = QtCore.QObject.connect
        _oldDisconnect  = QtCore.QObject.disconnect
        _oldEmit        = QtCore.QObject.emit
        
        def _wrapConnect(self,callableObject):
            """Returns a wrapped call to the old version of QtCore.QObject.connect"""
            @staticmethod
            def call(*args):
                callableObject(*args)
                self._oldConnect(*args)
            return call
        
        def _wrapDisconnect(self,callableObject):
            """Returns a wrapped call to the old version of QtCore.QObject.disconnect"""
            @staticmethod
            def call(*args):
                callableObject(*args)
                self._oldDisconnect(*args)
            return call
        
        def enableSignalDebugging(self,**kwargs):
        
            """Call this to enable Qt Signal debugging. This will trap all
            connect, and disconnect calls."""
        
            f = lambda *args: None
            connectCall     = kwargs.get('connectCall', f)
            disconnectCall  = kwargs.get('disconnectCall', f)
            emitCall        = kwargs.get('emitCall', f)
        
            def printIt(msg):
                def call(*args):
                    print(msg,args)
                return call
        
            # Monkey-patch.
            QtCore.QObject.connect    = self._wrapConnect(connectCall)
            QtCore.QObject.disconnect = self._wrapDisconnect(disconnectCall)
        
            def new_emit(self, *args):
                emitCall(self, *args)
                self._oldEmit(self, *args)
        
            QtCore.QObject.emit = new_emit
    #@-others
#@+node:ekr.20110605121601.18533: ** Non-essential
#@+node:ekr.20110605121601.18534: *3* quickheadlines
def install_qt_quickheadlines_tab(c):
    global __qh
    __qh = QuickHeadlines(c)

g.insqh = install_qt_quickheadlines_tab

class QuickHeadlines:
    def __init__(self, c):
        self.c = c
        tabw = c.frame.top.tabWidget
        self.listWidget = QtWidgets.QListWidget(tabw)
        tabw.addTab(self.listWidget, "Headlines")
        c.frame.top.treeWidget.itemSelectionChanged.connect(self.req_update)
        self.requested = False
    def req_update(self):
        """ prevent too frequent updates (only one/100 msec) """
        if self.requested:
            return
        QtCore.QTimer.singleShot(100, self.update)
        self.requested = True
    def update(self):
        g.trace("quickheadlines update")
        self.requested = False
        self.listWidget.clear()
        p = self.c.currentPosition()
        for n in p.children():
            self.listWidget.addItem(n.h)
#@+node:ekr.20140825042850.18405: ** class IdleTime (qtGui.py)
class IdleTime:
    '''A class that executes a handler at idle time.'''
    #@+others
    #@+node:ekr.20140825042850.18406: *3*  IdleTime.ctor
    def __init__(self,handler,delay=500,tag=None):
        '''ctor for IdleTime class.'''
        # g.trace('(IdleTime)',g.callers(2))
        self.count = 0
            # The number of times handler has been called.
        self.delay = delay
            # The argument to self.timer.start:
            # 0 for idle time, otherwise a delay in msec.
        self.enabled = False
            # True: run the timer continuously.
        self.handler = handler
            # The user-provided idle-time handler.
        self.starting_time = None
            # Time that the timer started.
        self.tag = tag
            # An arbitrary string/object for use during debugging.
        self.time = None
            # Time that the handle is called.
        self.waiting_for_idle = False
            # True if we have already waited for the minimum delay
        # Create the timer, but do not fire it.
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.at_idle_time)
        # Add this instance to the global idle_timers.list.
        # This reference prevents this instance from being destroyed.
        g.app.idle_timers.append(self)
    #@+node:ekr.20140825102404.18525: *3*  IdleTime.__repr__
    def __repr__(self):
        '''IdleTime repr.'''
        tag = self.tag
        if tag:
            return '<IdleTime: %s>' % (tag if g.isString(tag) else repr(tag))
        else:
            return '<IdleTime: id: %s>' % id(self)

    __str__ = __repr__
    #@+node:ekr.20140825042850.18407: *3* IdleTime.at_idle_time
    def at_idle_time(self):
        '''Call self.handler not more than once every self.delay msec.'''
        if g.app.killed:
            self.stop()
        elif self.enabled:
            if self.waiting_for_idle:
                # At idle time: call the handler.
                self.call_handler()
            # Requeue the timer with the appropriate delay.
            # 0 means wait until idle time.
            self.waiting_for_idle = not self.waiting_for_idle
            if self.timer.isActive():
                self.timer.stop()
            self.timer.start(0 if self.waiting_for_idle else self.delay)
        elif self.timer.isActive():
            self.timer.stop()
    #@+node:ekr.20140825042850.18408: *3* IdleTime.call_handler
    def call_handler(self):
        '''Carefully call the handler.'''
        try:
            self.count += 1
            self.time = time.time()
            self.handler(self)
        except Exception:
            g.es_exception()
            self.stop()
    #@+node:ekr.20140825080012.18529: *3* IdleTime.destory_self
    def destroy_self(self):
        '''Remove the instance from g.app.idle_timers.'''
        if not g.app.killed and self in g.app.idle_timers:
            g.app.idle_timers.remove(self)
    #@+node:ekr.20140825042850.18409: *3* IdleTime.start & stop
    def start(self):
        '''Start idle-time processing'''
        self.enabled = True
        if self.starting_time is None:
            self.starting_time = time.time()
        # Wait at least self.delay msec, then wait for idle time.
        self.last_delay = self.delay
        self.timer.start(self.delay)

    def stop(self):
        '''Stop idle-time processing. May be called during shutdown.'''
        self.enabled = False
        if hasattr(self,'timer') and self.timer.isActive():
            self.timer.stop()
    #@-others
#@+node:ekr.20110605121601.18537: ** class LeoQtEventFilter
class LeoQtEventFilter(QtCore.QObject):

    #@+<< about internal bindings >>
    #@+node:ekr.20110605121601.18538: *3* << about internal bindings >>
    #@@nocolor-node
    #@+at
    # 
    # Here are the rules for translating key bindings (in leoSettings.leo) into keys
    # for k.bindingsDict:
    # 
    # 1.  The case of plain letters is significant:  a is not A.
    # 
    # 2. The Shift- prefix can be applied *only* to letters. Leo will ignore (with a
    # warning) the shift prefix applied to any other binding, e.g., Ctrl-Shift-(
    # 
    # 3. The case of letters prefixed by Ctrl-, Alt-, Key- or Shift- is *not*
    # significant. Thus, the Shift- prefix is required if you want an upper-case
    # letter (with the exception of 'bare' uppercase letters.)
    # 
    # The following table illustrates these rules. In each row, the first entry is the
    # key (for k.bindingsDict) and the other entries are equivalents that the user may
    # specify in leoSettings.leo:
    # 
    # a, Key-a, Key-A
    # A, Shift-A
    # Alt-a, Alt-A
    # Alt-A, Alt-Shift-a, Alt-Shift-A
    # Ctrl-a, Ctrl-A
    # Ctrl-A, Ctrl-Shift-a, Ctrl-Shift-A
    # !, Key-!,Key-exclam,exclam
    # 
    # This table is consistent with how Leo already works (because it is consistent
    # with Tk's key-event specifiers). It is also, I think, the least confusing set of
    # rules.
    #@-<< about internal bindings >>

    #@+others
    #@+node:ekr.20110605121601.18539: *3*  ctor (LeoQtEventFilter)
    def __init__(self,c,w,tag=''):

        # g.trace('LeoQtEventFilter',tag,w)

        # Init the base class.
        QtCore.QObject.__init__(self)

        self.c = c
        self.w = w      # A leoQtX object, *not* a Qt object.
        self.tag = tag

        # Debugging.
        self.keyIsActive = False

        # Pretend there is a binding for these characters.
        close_flashers = c.config.getString('close_flash_brackets') or ''
        open_flashers  = c.config.getString('open_flash_brackets') or ''
        self.flashers = open_flashers + close_flashers

        # Support for ctagscompleter.py plugin.
        self.ctagscompleter_active = False
        self.ctagscompleter_onKey = None
    #@+node:ekr.20110605121601.18540: *3* eventFilter (LeoQtEventFilter)
    def eventFilter(self, obj, event):

        trace = False and not g.unitTesting
        verbose = True
        traceEvent = True # True: call self.traceEvent.
        traceKey = True
        c = self.c ; k = c.k
        eventType = event.type()
        ev = QtCore.QEvent
        gui = g.app.gui
        aList = []
        # g.app.debug_app enables traceWidget.
        self.traceWidget(event)
        kinds = [ev.ShortcutOverride,ev.KeyPress,ev.KeyRelease]
        # Hack: QLineEdit generates ev.KeyRelease only on Windows,Ubuntu
        lineEditKeyKinds = [ev.KeyPress,ev.KeyRelease]
        # Important:
        # QLineEdit: ignore all key events except keyRelease events.
        # QTextEdit: ignore all key events except keyPress events.
        if eventType in lineEditKeyKinds:
            p = c.currentPosition()
            isEditWidget = obj == c.frame.tree.edit_widget(p)
            self.keyIsActive = eventType == ev.KeyRelease if isEditWidget else eventType == ev.KeyPress
        else:
            self.keyIsActive = False
        if eventType == ev.WindowActivate:
            gui.onActivateEvent(event,c,obj,self.tag)
            override = False ; tkKey = None
        elif eventType == ev.WindowDeactivate:
            gui.onDeactivateEvent(event,c,obj,self.tag)
            override = False ; tkKey = None
            if self.tag in ('body','tree','log'):
                g.app.gui.remove_border(c,obj)
        elif eventType in kinds:
            tkKey,ch,ignore = self.toTkKey(event)
            aList = c.k.masterGuiBindingsDict.get('<%s>' %tkKey,[])
            # g.trace('instate',k.inState(),'tkKey',tkKey,'ignore',ignore,'len(aList)',len(aList))
            if ignore: override = False
            # This is extremely bad.
            # At present, it is needed to handle tab properly.
            elif self.isSpecialOverride(tkKey,ch):
                override = True
            elif k.inState():
                override = not ignore # allow all keystrokes.
            else:
                override = len(aList) > 0
        else:
            override = False ; tkKey = '<no key>'
            if self.tag == 'body':
                if eventType == ev.FocusIn:
                    g.app.gui.add_border(c,obj)
                    c.frame.body.onFocusIn(obj)
                elif eventType == ev.FocusOut:
                    g.app.gui.remove_border(c,obj)
                    c.frame.body.onFocusOut(obj)
            elif self.tag in ('log','tree'):
                if eventType == ev.FocusIn:
                    g.app.gui.add_border(c,obj)
                elif eventType == ev.FocusOut:
                    g.app.gui.remove_border(c,obj)
        if self.keyIsActive:
            shortcut = self.toStroke(tkKey,ch) # ch is unused.
            if override:
                # Essentially *all* keys get passed to masterKeyHandler.
                if trace and traceKey:
                    g.trace('ignore',ignore,'bound',repr(shortcut),repr(aList))
                w = self.w # Pass the wrapper class, not the wrapped widget.
                qevent = event
                event = self.create_key_event(event,c,w,ch,tkKey,shortcut)
                k.masterKeyHandler(event)
                if g.app.gui.insert_char_flag:
                    # if trace and traceKey: g.trace('*** insert_char_flag',event.text())
                    g.trace('*** insert_char_flag',qevent.text())
                    g.app.gui.insert_char_flag = False
                    override = False # *Do* pass the character back to the widget!
                c.outerUpdate()
            else:
                if trace and traceKey and verbose:
                    g.trace(self.tag,'unbound',tkKey,shortcut)
            if trace and traceEvent:
                # Trace key events.
                self.traceEvent(obj,event,tkKey,override)
        elif trace and traceEvent:
            # Trace non-key events.
            self.traceEvent(obj,event,tkKey,override)
        return override
    #@+node:ekr.20110605195119.16937: *3* create_key_event (LeoQtEventFilter)
    def create_key_event (self,event,c,w,ch,tkKey,shortcut):

        trace = False and not g.unitTesting ; verbose = False

        if trace and verbose: g.trace('ch: %s, tkKey: %s, shortcut: %s' % (
            repr(ch),repr(tkKey),repr(shortcut)))

        # Last-minute adjustments...
        if shortcut == 'Return':
            ch = '\n' # Somehow Qt wants to return '\r'.
        elif shortcut == 'Escape':
            ch = 'Escape'

        # Switch the Shift modifier to handle the cap-lock key.
        if len(ch) == 1 and len(shortcut) == 1 and ch.isalpha() and shortcut.isalpha():
            if ch != shortcut:
                if trace and verbose: g.trace('caps-lock')
                shortcut = ch

        # Patch provided by resi147.
        # See the thread: special characters in MacOSX, like '@'.
        if sys.platform.startswith('darwin'):
            darwinmap = {
                'Alt-Key-5': '[',
                'Alt-Key-6': ']',
                'Alt-Key-7': '|',
                'Alt-slash': '\\',
                'Alt-Key-8': '{',
                'Alt-Key-9': '}',
                'Alt-e': '€',
                'Alt-l': '@',
            }
            if tkKey in darwinmap:
                shortcut = darwinmap[tkKey]

        char = ch
        # Auxiliary info.
        x      = hasattr(event,'x') and event.x or 0
        y      = hasattr(event,'y') and event.y or 0
        # Support for fastGotoNode plugin
        x_root = hasattr(event,'x_root') and event.x_root or 0
        y_root = hasattr(event,'y_root') and event.y_root or 0

        if trace and verbose: g.trace('ch: %s, shortcut: %s printable: %s' % (
            repr(ch),repr(shortcut),ch in string.printable))

        return leoGui.LeoKeyEvent(c,char,event,shortcut,w,x,y,x_root,y_root)
    #@+node:ekr.20120204061120.10088: *3* Key construction (LeoQtEventFilter)
    #@+node:ekr.20110605121601.18543: *4* toTkKey & helpers (must not change!)
    def toTkKey (self,event):

        '''Return tkKey,ch,ignore:

        tkKey: the Tk spelling of the event used to look up
               bindings in k.masterGuiBindingsDict.
               **This must not ever change!**

        ch:    the insertable key, or ''.

        ignore: True if the key should be ignored.
                This is **not** the same as 'not ch'.
        '''

        mods = self.qtMods(event)

        keynum,text,toString,ch = self.qtKey(event)

        tkKey,ch,ignore = self.tkKey(
            event,mods,keynum,text,toString,ch)

        return tkKey,ch,ignore
    #@+node:ekr.20110605121601.18546: *5* tkKey & helper
    def tkKey (self,event,mods,keynum,text,toString,ch):

        '''Carefully convert the Qt key to a 
        Tk-style binding compatible with Leo's core
        binding dictionaries.'''

        trace = False and not g.unitTesting
        ch1 = ch # For tracing.
        use_shift = (
            'Home','End','Tab',
            'Up','Down','Left','Right',
            'Next','Prior', # 2010/01/10: Allow Shift-PageUp and Shift-PageDn.
            # 2011/05/17: Fix bug 681797.
            # There is nothing 'dubious' about these provided that they are bound.
            # If they are not bound, then weird characters will be inserted.
            'Delete','Ins','Backspace',
            'F1','F2','F3','F4','F5','F6','F7','F8','F9','F10','F11','F12',
        )

        # Convert '&' to 'ampersand', etc.
        # *Do* allow shift-bracketleft, etc.
        ch2 = self.char2tkName(ch or toString)
        if ch2: ch = ch2 
        if not ch: ch = ''

        if 'Shift' in mods:
            if trace: g.trace(repr(ch))
            if len(ch) == 1 and ch.isalpha():
                mods.remove('Shift')
                ch = ch.upper()
            elif len(ch) > 1 and ch not in use_shift:
                # Experimental!
                mods.remove('Shift')
            # 2009/12/19: Speculative.
            # if ch in ('parenright','parenleft','braceright','braceleft'):
                # mods.remove('Shift')
        elif len(ch) == 1:
            ch = ch.lower()

        if ('Alt' in mods or 'Control' in mods) and ch and ch in string.digits:
            mods.append('Key')

        # *Do* allow bare mod keys, so they won't be passed on.
        tkKey = '%s%s%s' % ('-'.join(mods),mods and '-' or '',ch)

        if trace: g.trace(
            'text: %s toString: %s ch1: %s ch: %s' % (
            repr(text),repr(toString),repr(ch1),repr(ch)))

        ignore = not ch # Essential
        ch = text or toString
        return tkKey,ch,ignore
    #@+node:ekr.20110605121601.18547: *6* char2tkName
    char2tkNameDict = {
        # Part 1: same as g.app.guiBindNamesDict
        "&" : "ampersand",
        "^" : "asciicircum",
        "~" : "asciitilde",
        "*" : "asterisk",
        "@" : "at",
        "\\": "backslash",
        "|" : "bar",
        "{" : "braceleft",
        "}" : "braceright",
        "[" : "bracketleft",
        "]" : "bracketright",
        ":" : "colon",  
        "," : "comma",
        "$" : "dollar",
        "=" : "equal",
        "!" : "exclam",
        ">" : "greater",
        "<" : "less",
        "-" : "minus",
        "#" : "numbersign",
        '"' : "quotedbl",
        "'" : "quoteright",
        "(" : "parenleft",
        ")" : "parenright", 
        "%" : "percent",
        "." : "period",     
        "+" : "plus",
        "?" : "question",
        "`" : "quoteleft",
        ";" : "semicolon",
        "/" : "slash",
        " " : "space",      
        "_" : "underscore",
        # Part 2: special Qt translations.
        'Backspace':'BackSpace',
        'Backtab':  'Tab', # The shift mod will convert to 'Shift+Tab',
        'Esc':      'Escape',
        'Del':      'Delete',
        'Ins':      'Insert', # was 'Return',
        # Comment these out to pass the key to the QTextWidget.
        # Use these to enable Leo's page-up/down commands.
        'PgDown':    'Next',
        'PgUp':      'Prior',
        # New entries.  These simplify code.
        'Down':'Down','Left':'Left','Right':'Right','Up':'Up',
        'End':'End',
        'F1':'F1','F2':'F2','F3':'F3','F4':'F4','F5':'F5',
        'F6':'F6','F7':'F7','F8':'F8','F9':'F9',
        'F10':'F10','F11':'F11','F12':'F12',
        'Home':'Home',
        # 'Insert':'Insert',
        'Return':'Return',
        'Tab':'Tab',
        # 'Tab':'\t', # A hack for QLineEdit.
        # Unused: Break, Caps_Lock,Linefeed,Num_lock
    }

    # Called only by tkKey.

    def char2tkName (self,ch):
        val = self.char2tkNameDict.get(ch)
        # g.trace(repr(ch),repr(val))
        return val
    #@+node:ekr.20120204061120.10087: *4* Common key construction helpers
    #@+node:ekr.20110605121601.18541: *5* isSpecialOverride
    def isSpecialOverride (self,tkKey,ch):

        '''Return True if tkKey is a special Tk key name.
        '''

        return tkKey or ch in self.flashers
    #@+node:ekr.20110605121601.18542: *5* toStroke (LeoQtEventFilter)
    def toStroke (self,tkKey,ch):  # ch is unused

        '''Convert the official tkKey name to a stroke.'''

        trace = False and not g.unitTesting
        s = tkKey
        table = (
            ('Alt-','Alt+'),
            ('Ctrl-','Ctrl+'),
            ('Control-','Ctrl+'),
            # Use Alt+Key-1, etc.  Sheesh.
            # ('Key-','Key+'),
            ('Shift-','Shift+')
        )
        for a,b in table:
            s = s.replace(a,b)
        if trace: g.trace('tkKey',tkKey,'-->',s)
        return s
    #@+node:ekr.20110605121601.18544: *5* qtKey
    def qtKey (self,event):

        '''Return the components of a Qt key event.

        Modifiers are handled separately.

        Return keynum,text,toString,ch

        keynum: event.key()
        ch:     g.u(chr(keynum)) or '' if there is an exception.
        toString:
            For special keys: made-up spelling that become part of the setting.
            For all others:   QtWidgets.QKeySequence(keynum).toString()
        text:   event.text()
        '''

        trace = False and not g.unitTesting
        keynum = event.key()
        text   = event.text() # This is the unicode text.

        qt = QtCore.Qt
        d = {
            qt.Key_Shift:   'Key_Shift',
            qt.Key_Control: 'Key_Control',  # MacOS: Command key
            qt.Key_Meta:	'Key_Meta',     # MacOS: Control key, Alt-Key on Microsoft keyboard on MacOs.
            qt.Key_Alt:	    'Key_Alt',	 
            qt.Key_AltGr:	'Key_AltGr',
                # On Windows, when the KeyDown event for this key is sent,
                # the Ctrl+Alt modifiers are also set.
        }

        if d.get(keynum):
            toString = d.get(keynum)
        else:
            toString = QtGui.QKeySequence(keynum).toString()

        try:
            ch1 = chr(keynum)
        except ValueError:
            ch1 = ''

        try:
            ch = g.u(ch1)
        except UnicodeError:
            ch = ch1

        text     = g.u(text)
        toString = g.u(toString)

        if trace and self.keyIsActive:
            mods = '+'.join(self.qtMods(event))
            g.trace(
                'keynum %7x ch %3s toString %s %s' % (
                keynum,repr(ch),mods,repr(toString)))

        return keynum,text,toString,ch
    #@+node:ekr.20120204061120.10084: *5* qtMods
    def qtMods (self,event):

        '''Return the text version of the modifiers of the key event.'''

        modifiers = event.modifiers()

        # The order of this table must match the order created by k.strokeFromSetting.
        # When g.new_keys is True, k.strokeFromSetting will canonicalize the setting.

        qt = QtCore.Qt

        if sys.platform.startswith('darwin'):
            # Yet another MacOS hack:
            table = (
                (qt.AltModifier,     'Alt'), # For Apple keyboard.
                (qt.MetaModifier,    'Alt'), # For Microsoft keyboard.
                (qt.ControlModifier, 'Control'),
                # No way to generate Meta.
                (qt.ShiftModifier,   'Shift'),
            )

        else:
            table = (
                (qt.AltModifier,     'Alt'),
                (qt.ControlModifier, 'Control'),
                (qt.MetaModifier,    'Meta'),
                (qt.ShiftModifier,   'Shift'),
            )

        mods = [b for a,b in table if (modifiers & a)]
        return mods
    #@+node:ekr.20110605121601.18548: *3* traceEvent (LeoQtEventFilter)
    def traceEvent (self,obj,event,tkKey,override):

        if g.unitTesting: return
        # http://qt-project.org/doc/qt-4.8/qevent.html#properties
        traceFocus = False
        traceKey   = True
        traceLayout = False
        traceMouse = False
        c,e = self.c,QtCore.QEvent
        eventType = event.type()
        show = []
        ignore = [
            e.MetaCall, # 43
            e.Timer, # 1
            e.ToolTip, # 110
        ]
        focus_events = (
            (e.Enter,'enter'), # 10
            (e.Leave,'leave'), # 11
            (e.FocusIn,'focus-in'), # 8
            (e.FocusOut,'focus-out'), # 9
            (e.Hide,'hide'), # 18
            (e.HideToParent, 'hide-to-parent'), # 27
            (e.HoverEnter, 'hover-enter'), # 127
            (e.HoverLeave,'hover-leave'), # 128
            (e.HoverMove,'hover-move'), # 129
            # (e.LeaveEditFocus,'leave-edit-focus'), # 151
            (e.Show,'show'), # 17
            (e.ShowToParent,'show-to-parent'), # 26
            (e.WindowActivate,'window-activate'), # 24
            (e.WindowBlocked,'window-blocked'), # 103
            (e.WindowUnblocked,'window-unblocked'), # 104
            (e.WindowDeactivate,'window-deactivate'), # 25
        )
        key_events = (
            (e.KeyPress,'key-press'), # 6
            (e.KeyRelease,'key-release'), # 7
            (e.Shortcut,'shortcut'), # 117
            (e.ShortcutOverride,'shortcut-override'), # 51
        )
        layout_events = (
            (e.ChildPolished,'child-polished'), # 69
            #(e.CloseSoftwareInputPanel,'close-sip'), # 200
                # Event does not exist on MacOS.
            (e.ChildAdded,'child-added'), # 68
            (e.DynamicPropertyChange,'dynamic-property-change'), # 170
            (e.FontChange,'font-change'),# 97
            (e.LayoutRequest,'layout-request'), # 76
            (e.Move,'move'), # 13 widget's position changed.
            (e.PaletteChange,'palette-change'),# 39
            (e.ParentChange,'parent-change'), # 21
            (e.Paint,'paint'), # 12
            (e.Polish,'polish'), # 75
            (e.PolishRequest,'polish-request'), # 74
            # (e.RequestSoftwareInputPanel,'sip'), # 199
                # Event does not exist on MacOS.
            (e.Resize,'resize'), # 14
            (e.StyleChange,'style-change'), # 100
            (e.ZOrderChange,'z-order-change'), # 126
        )
        mouse_events = (
            (e.MouseMove,'mouse-move'), # 155
            (e.MouseButtonPress,'mouse-press'), # 2
            (e.MouseButtonRelease,'mouse-release'), # 3
            (e.Wheel,'mouse-wheel'), # 31
        )
        option_table = (
            (traceFocus,focus_events),
            (traceKey,key_events),
            (traceLayout,layout_events),
            (traceMouse,mouse_events),
        )
        for option,table in option_table:
            if option:
                show.extend(table)
            else:
                for n,tag in table:
                    ignore.append(n)
        for val,kind in show:
            if eventType == val:
                g.trace(
                    '%5s %18s in-state: %5s key: %s override: %s: obj: %s' % (
                    self.tag,kind,repr(c.k and c.k.inState()),tkKey,override,obj))
                return
        if eventType not in ignore:
            g.trace('%3s:%s obj:%s' % (eventType,'unknown',obj))
    #@+node:ekr.20131121050226.16331: *3* traceWidget (LeoQtEventFilter)
    def traceWidget(self,event):
        '''Show unexpected events in unusual widgets.'''
        # pylint: disable=E1101
        # E1101:9240,0:Class 'QEvent' has no 'CloseSoftwareInputPanel' member
        # E1101:9267,0:Class 'QEvent' has no 'RequestSoftwareInputPanel' member
        if not g.app.debug_app: return
        c = self.c
        e = QtCore.QEvent
        assert isinstance(event,QtCore.QEvent)
        et = event.type()
        # http://qt-project.org/doc/qt-4.8/qevent.html#properties
        ignore_d = {
            e.ChildAdded:'child-added', # 68
            e.ChildPolished:'child-polished', # 69
            e.ChildRemoved:'child-removed', # 71
            e.Close:'close', # 19
            e.CloseSoftwareInputPanel:'close-software-input-panel', # 200
            178:'contents-rect-change', # 178
            # e.DeferredDelete:'deferred-delete', # 52 (let's trace this)
            e.DynamicPropertyChange:'dynamic-property-change', # 170
            e.FocusOut:'focus-out', # 9 (We don't care if we are leaving an unknown widget)
            e.FontChange:'font-change',# 97
            e.Hide:'hide', # 18
            e.HideToParent: 'hide-to-parent', # 27
            e.HoverEnter: 'hover-enter', # 127
            e.HoverLeave:'hover-leave', # 128
            e.HoverMove:'hover-move', # 129
            e.KeyPress:'key-press', # 6
            e.KeyRelease:'key-release', # 7
            e.LayoutRequest:'layout-request', # 76
            e.Leave:'leave', # 11 (We don't care if we are leaving an unknown widget)
            # e.LeaveEditFocus:'leave-edit-focus', # 151
            e.MetaCall:'meta-call', # 43
            e.Move:'move', # 13 widget's position changed.
            e.MouseButtonPress:'mouse-button-press', # 2
            e.MouseButtonRelease:'mouse-button-release', # 3
            e.MouseButtonDblClick:'mouse-button-double-click', # 4
            e.MouseMove:'mouse-move', # 5
            e.Paint:'paint', # 12
            e.PaletteChange:'palette-change', # 39
            e.ParentChange:'parent-change', # 21
            e.Polish:'polish', # 75
            e.PolishRequest:'polish-request', # 74
            e.RequestSoftwareInputPanel:'request-software-input-panel', # 199
            e.Resize:'resize', # 14
            e.ShortcutOverride:'shortcut-override', # 51
            e.Show:'show', # 17
            e.ShowToParent:'show-to-parent', # 26
            e.StyleChange:'style-change', # 100
            e.StatusTip:'status-tip', # 112
            e.Timer:'timer', # 1
            e.ToolTip:'tool-tip', # 110
            e.WindowBlocked:'window-blocked', # 103
            e.WindowUnblocked:'window-unblocked', # 104
            e.ZOrderChange:'z-order-change', # 126
        }
        focus_d = {
            e.DeferredDelete:'deferred-delete', # 52
            e.Enter:'enter', # 10
            e.FocusIn:'focus-in', # 8
            e.WindowActivate:'window-activate', # 24
            e.WindowDeactivate:'window-deactivate', # 25
        }
        line_edit_ignore_d = {
            e.Enter:'enter', # 10 (mouse over)
            e.Leave:'leave', # 11 (mouse over)
            e.FocusOut:'focus-out', # 9
            e.WindowActivate:'window-activate', # 24
            e.WindowDeactivate:'window-deactivate', # 25
        }
        none_ignore_d = {
            e.Enter:'enter', # 10 (mouse over)
            e.Leave:'leave', # 11 (mouse over)
            e.FocusOut:'focus-out', # 9
            e.WindowActivate:'window-activate', # 24
        }
        table = (
            c.frame.miniBufferWidget and c.frame.miniBufferWidget.widget,
            c.frame.body.bodyCtrl and c.frame.body.bodyCtrl.widget,
            c.frame.tree and c.frame.tree.treeWidget,
            c.frame.log and c.frame.log.logCtrl and c.frame.log.logCtrl.widget,
        )
        w = QtWidgets.QApplication.focusWidget()
        if g.app.debug_widgets: # verbose:
            for d in (ignore_d,focus_d,line_edit_ignore_d,none_ignore_d):
                t = d.get(et)
                if t: break
            else:
                t = et
            g.trace('%20s %s' % (t,w.__class__))
        elif w is None:
            if et not in none_ignore_d and et not in ignore_d:
                t = focus_d.get(et) or et
                g.trace('None %s' % (t))
        elif w not in table:
            if isinstance(w,QtWidgets.QPushButton):
                pass
            elif isinstance(w,QtWidgets.QLineEdit):
                if et not in ignore_d and et not in line_edit_ignore_d:
                    t = focus_d.get(et) or et
                    g.trace('%20s %s' % (t,w.__class__))
            elif et not in ignore_d:
                t = focus_d.get(et) or et
                g.trace('%20s %s' % (t,w.__class__))
    #@-others
#@-others
#@-leo
