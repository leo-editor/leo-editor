# -*- coding: utf-8 -*-
#@+leo-ver=4-thin
#@+node:ekr.20081004102201.619:@thin qtGui.py
#@@first

'''qt gui plugin.'''

#@@language python
#@@tabwidth -4
#@@pagewidth 80

safe_mode = True # True: Bypass k.masterKeyHandler for problem keys or visible characters.

# Define these to suppress pylint warnings...
__timing = None # For timing stats.
__qh = None # For quick headlines.

#@<< qt imports >>
#@+node:ekr.20081004102201.620: << qt imports >>
import leo.core.leoGlobals as g
import leo.core.leoChapters as leoChapters
import leo.core.leoColor as leoColor
import leo.core.leoFrame as leoFrame
import leo.core.leoFind as leoFind
import leo.core.leoGui as leoGui
import leo.core.leoKeys as leoKeys
import leo.core.leoMenu as leoMenu

import os
import string
import sys
import time
import types

try:
    # import PyQt4.Qt as Qt # Loads all modules of Qt.
    import qt_main # Contains Ui_MainWindow class
    import PyQt4.QtCore as QtCore
    import PyQt4.QtGui as QtGui
    from PyQt4 import Qsci
except ImportError:
    QtCore = None
    g.es_print('can not import Qt',color='red')
#@-node:ekr.20081004102201.620: << qt imports >>
#@nl

#@+at
# Notes:
# 1. All leoQtX classes are two-way adapator classes
#@-at
#@@c

#@+others
#@+node:ekr.20081004102201.623: Module level

#@+node:ekr.20081004102201.621:init
def init():

    if g.app.unitTesting: # Not Ok for unit testing!
        return False

    if not QtCore:
        return False

    if g.app.gui:
        return g.app.gui.guiName() == 'qt'
    else:
        g.app.gui = leoQtGui()

        # Override g.pdb
        def qtPdb():
            import pdb
            QtCore.pyqtRemoveInputHook()
            pdb.set_trace()
        g.pdb = qtPdb

        if False: # This will be done, if at all, in leoQtBody.
            def qtHandleDefaultChar(self,event,stroke):
                # This is an error.
                g.trace(stroke,g.callers())
                return False
            if safe_mode: # Override handleDefaultChar method.
                h = leoKeys.keyHandlerClass
                g.funcToMethod(qtHandleDefaultChar,h,"handleDefaultChar")

        g.app.gui.finishCreate()
        g.plugin_signon(__name__)
        return True
#@-node:ekr.20081004102201.621:init
#@+node:ekr.20081004102201.627:embed_ipython
def embed_ipython():

    import IPython.ipapi

    # sys.argv = ['ipython', '-p' , 'sh']
    # ses = IPython.ipapi.make_session(dict(w = window))
    # ip = ses.IP.getapi()
    # ip.load('ipy_leo')
    # ses.mainloop()
#@nonl
#@-node:ekr.20081004102201.627:embed_ipython
#@+node:ekr.20081004102201.626:tstart & tstop
def tstart():
    global __timing
    __timing = time.time()

def tstop():
    g.trace("%s Time: %1.2fsec" % (
        g.callers(1),time.time()-__timing))
#@-node:ekr.20081004102201.626:tstart & tstop
#@-node:ekr.20081004102201.623: Module level
#@+node:ekr.20081103071436.3:Frame and component classes...
#@+node:ekr.20081004102201.629:class  Window
class Window(QtGui.QMainWindow):

    '''A class representing all parts of the main Qt window
    as created by Designer.

    c.frame.top is a Window object.

    All leoQtX classes use the ivars of this Window class to
    support operations requested by Leo's core.
    '''

    #@    @+others
    #@+node:ekr.20081004172422.884: ctor (Window)
    # Called from leoQtFrame.finishCreate.

    def __init__(self,c,parent=None):

        '''Create Leo's main window, c.frame.top'''

        self.c = c ; top = c.frame.top

        # g.trace('Window')

        # Init both base classes.
        QtGui.QMainWindow.__init__(self,parent)
        #qt_main.Ui_MainWindow.__init__(self)

        self.ui = qt_main.Ui_MainWindow()
        # Init the QDesigner elements.
        self.ui.setupUi(self)

        # The following ivars (and more) are inherited from UiMainWindow:
            # self.lineEdit   = QtGui.QLineEdit(self.centralwidget) # The minibuffer.
            # self.menubar    = QtGui.QMenuBar(MainWindow)          # The menu bar.
            # self.tabWidget  = QtGui.QTabWidget(self.splitter)     # The log pane.
            # self.textEdit   = Qsci.QsciScintilla(self.splitter_2) # The body pane.
            # self.treeWidget = QtGui.QTreeWidget(self.splitter)    # The tree pane.

        self.iconBar = self.addToolBar("IconBar")
        self.statusBar = QtGui.QStatusBar()
        self.setStatusBar(self.statusBar)

        self.setStyleSheets()
    #@-node:ekr.20081004172422.884: ctor (Window)
    #@+node:ekr.20081020075840.11:closeEvent (qtFrame)
    def closeEvent (self,event):

        c = self.c

        if c.inCommand:
            # g.trace('requesting window close')
            c.requestCloseWindow = True
        else:
            ok = g.app.closeLeoWindow(c.frame)
            # g.trace('ok',ok)
            if ok:
                event.accept()
            else:
                event.ignore()
    #@-node:ekr.20081020075840.11:closeEvent (qtFrame)
    #@+node:ekr.20081016072304.14:setStyleSheets & helper
    styleSheet_inited = False

    def setStyleSheets(self):

        c = self.c

        sheet = c.config.getData('qt-gui-plugin-style-sheet')
        if sheet: sheet = '\n'.join(sheet)
        self.setStyleSheet(sheet or self.default_sheet())
    #@nonl
    #@+node:ekr.20081018053140.10:defaultStyleSheet
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
    #@-node:ekr.20081018053140.10:defaultStyleSheet
    #@-node:ekr.20081016072304.14:setStyleSheets & helper
    #@-others

#@-node:ekr.20081004102201.629:class  Window
#@+node:ville.20081104152150.2:class  DynamicWindow
from PyQt4 import uic

class DynamicWindow(QtGui.QMainWindow):

    '''A class representing all parts of the main Qt window
    as created by Designer.

    c.frame.top is a Window object.

    All leoQtX classes use the ivars of this Window class to
    support operations requested by Leo's core.
    '''

    #@    @+others
    #@+node:ville.20081104152150.3: ctor (Window)
    # Called from leoQtFrame.finishCreate.

    def __init__(self,c,parent=None):

        '''Create Leo's main window, c.frame.top'''

        self.c = c ; top = c.frame.top

        # g.trace('Window')

        # Init both base classes.

        ui_description_file = g.app.loadDir + "/../plugins/qt_main.ui"
        QtGui.QMainWindow.__init__(self,parent)        
        self.ui = uic.loadUi(ui_description_file, self)

        # Init the QDesigner elements.
        #self.setupUi(self)

        # The following ivars (and more) are inherited from UiMainWindow:
            # self.lineEdit   = QtGui.QLineEdit(self.centralwidget) # The minibuffer.
            # self.menubar    = QtGui.QMenuBar(MainWindow)          # The menu bar.
        ivars = """
        tabWidget treeWidget stackedWidget richTextEdit lineEdit
        findPattern findChange checkBoxWholeWord checkBoxIgnoreCase
        checkBoxWrapAround checkBoxReverse checkBoxRexexp checkBoxMarkFinds
        checkBoxEntireOutline checkBoxSubroutineOnly checkBoxNodeOnly
        checkBoxSearchHeadline checkBoxSearchBody checkBoxMarkChanges
        setWindowIcon setWindowTitle show setGeometry windowTitle
        menuBar

        """.strip().split()

        #for v in ivars:
        #    setattr(self, v, getattr(self.ui, v))


        self.iconBar = self.addToolBar("IconBar")
        self.menubar = self.menuBar()
        self.statusBar = QtGui.QStatusBar()
        self.setStatusBar(self.statusBar)

        self.setStyleSheets()
    #@-node:ville.20081104152150.3: ctor (Window)
    #@+node:ville.20081104152150.4:closeEvent (qtFrame)
    def closeEvent (self,event):

        c = self.c

        if c.inCommand:
            # g.trace('requesting window close')
            c.requestCloseWindow = True
        else:
            ok = g.app.closeLeoWindow(c.frame)
            # g.trace('ok',ok)
            if ok:
                event.accept()
            else:
                event.ignore()
    #@-node:ville.20081104152150.4:closeEvent (qtFrame)
    #@+node:ville.20081104152150.5:setStyleSheets & helper
    styleSheet_inited = False

    def setStyleSheets(self):

        c = self.c

        sheet = c.config.getData('qt-gui-plugin-style-sheet')
        if sheet: sheet = '\n'.join(sheet)
        self.ui.setStyleSheet(sheet or self.default_sheet())
    #@nonl
    #@+node:ville.20081104152150.6:defaultStyleSheet
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
    #@-node:ville.20081104152150.6:defaultStyleSheet
    #@-node:ville.20081104152150.5:setStyleSheets & helper
    #@-others

#@-node:ville.20081104152150.2:class  DynamicWindow
#@+node:ekr.20081004172422.502:class leoQtBody (leoBody)
class leoQtBody (leoFrame.leoBody):

    """A class that represents the body pane of a Qt window."""

    #@    @+others
    #@+node:ekr.20081004172422.503: Birth
    #@+node:ekr.20081004172422.504: ctor (qtBody)
    def __init__ (self,frame,parentFrame):

        # Call the base class constructor.
        leoFrame.leoBody.__init__(self,frame,parentFrame)

        c = self.c
        assert c.frame == frame and frame.c == c

        self.useScintilla = c.config.getBool('qt-use-scintilla')

        # Set the actual gui widget.
        if self.useScintilla:
            self.widget = w = leoQScintillaWidget(
                c.frame.top.textEdit,
                name='body',c=c)
            self.bodyCtrl = w # The widget as seen from Leo's core.
            self.colorizer = leoColor.nullColorizer(c)
        else:
            top = c.frame.top ; sw = top.ui.stackedWidget
            sw.setCurrentIndex(1)
            self.widget = w = leoQTextEditWidget(
                top.ui.richTextEdit,
                name = 'body',c=c) # A QTextEdit.
            self.bodyCtrl = w # The widget as seen from Leo's core.
            self.colorizer = leoColor.colorizer(c)
            w.acceptRichText = False

        # Config stuff.
        self.trace_onBodyChanged = c.config.getBool('trace_onBodyChanged')
        wrap = c.config.getBool('body_pane_wraps')
        wrap = g.choose(wrap,"word","none")
        self.wrapState = wrap

        # For multiple body editors.
        self.editor_name = None
        self.editor_v = None
        self.numberOfEditors = 1
        self.totalNumberOfEditors = 1
    #@nonl
    #@-node:ekr.20081004172422.504: ctor (qtBody)
    #@+node:ekr.20081004172422.505:createBindings (qtBody)
    def createBindings (self,w=None):

        '''(qtBody) Create gui-dependent bindings.
        These are *not* made in nullBody instances.'''

        # frame = self.frame ; c = self.c ; k = c.k
        # if not w: w = self.widget

        # c.bind(w,'<Key>', k.masterKeyHandler)

        # def onFocusOut(event,c=c):
            # # This interferes with inserting new nodes.
                # # c.k.setDefaultInputState()
            # self.setEditorColors(
                # bg=c.k.unselected_body_bg_color,
                # fg=c.k.unselected_body_fg_color)
            # # This is required, for example, when typing Alt-Shift-anyArrow in insert mode.
            # # But we suppress coloring in the widget.
            # oldState = k.unboundKeyAction
            # k.unboundKeyAction = k.defaultUnboundKeyAction
            # c.k.showStateAndMode(w=g.app.gui.get_focus(c))
            # k.unboundKeyAction = oldState

        # def onFocusIn(event,c=c):
            # # g.trace('callback')
            # c.k.setDefaultInputState()
            # c.k.showStateAndMode()  # TNB - fix color when window manager returns focus to Leo

        # c.bind(w,'<FocusOut>', onFocusOut)
        # c.bind(w,'<FocusIn>', onFocusIn)

        # table = [
            # ('<Button-1>',  frame.OnBodyClick,          k.masterClickHandler),
            # ('<Button-3>',  frame.OnBodyRClick,         k.masterClick3Handler),
            # ('<Double-1>',  frame.OnBodyDoubleClick,    k.masterDoubleClickHandler),
            # ('<Double-3>',  None,                       k.masterDoubleClick3Handler),
            # ('<Button-2>',  frame.OnPaste,              k.masterClickHandler),
        # ]

        # table2 = (
            # ('<Button-2>',  frame.OnPaste,              k.masterClickHandler),
        # )

        # if c.config.getBool('allow_middle_button_paste'):
            # table.extend(table2)

        # for kind,func,handler in table:
            # def bodyClickCallback(event,handler=handler,func=func):
                # return handler(event,func)

            # c.bind(w,kind,bodyClickCallback)
    #@-node:ekr.20081004172422.505:createBindings (qtBody)
    #@+node:ekr.20081011035036.13:get_name
    def getName (self):

        return 'body-widget'
    #@-node:ekr.20081011035036.13:get_name
    #@-node:ekr.20081004172422.503: Birth
    #@+node:ekr.20081016072304.11:Do-nothings

    # Configuration will be handled by style sheets.
    def cget(self,*args,**keys):        return None
    def configure (self,*args,**keys):  pass
    def setEditorColors (self,bg,fg):   pass

    def oops (self):
        g.trace('qtBody',g.callers(3))
    #@-node:ekr.20081016072304.11:Do-nothings
    #@+node:ekr.20081031074959.13:High-level interface to self.widget
    def appendText (self,s):
        return self.widget.appendText(s)

    def bind (self,kind,*args,**keys):
        return self.widget.bind(kind,*args,**keys)

    def deleteTextSelection (self):
        return self.widget.deleteTextSelection()

    def flashCharacter(self,i,bg='white',fg='red',flashes=3,delay=75):
        return self.widget(i,bg,fg,flashes,delay)

    def get(self,i,j=None):
        return self.widget.get(i,j)

    def getAllText (self):
        return self.widget.getAllText()

    def getFocus (self):
        return self.widget.getFocus()

    def getInsertPoint(self):
        return self.widget.getInsertPoint()

    def getSelectedText (self):
        return self.widget.getSelectedText()

    def getSelectionRange (self,sort=True):
        return self.widget.getSelectionRange(sort)

    def getYScrollPosition (self):
        return self.widget.getYScrollPosition()

    def insert(self,i,s):
        return self.widget.insert(i,s)

    def scrollLines (self,n):
        return self.widget.scrollLines(n)

    def see(self,index):
        return self.widget.see(index)

    def seeInsertPoint(self):
        return self.widget.seeInsertPoint()

    def setAllText (self,s):
        return self.widget.setAllText(s)

    def setBackgroundColor (self,color):
        return self.widget.setBackgroundColor(color)

    def setFocus (self):
        return self.widget.setFocus()

    def setForegroundColor (self,color):
        return self.widget.setForegroundColor(color)

    def setInsertPoint (self,pos):
        return self.widget.setInsertPoint(pos)

    def setSelectionRange (self,sel):
        i,j = sel
        return self.widget.setSelectionRange(i,j)

    def setYScrollPosition (self,i):
        return self.widget.setYScrollPosition(i)
    #@-node:ekr.20081031074959.13:High-level interface to self.widget
    #@+node:ekr.20081103095314.32:Editors (qtBody)
    #@+node:ekr.20081103095314.33:createEditorFrame
    def createEditorFrame (self,pane):

        return None

        # f = Tk.Frame(pane)
        # f.pack(side='top',expand=1,fill='both')
        # return f
    #@-node:ekr.20081103095314.33:createEditorFrame
    #@+node:ekr.20081103095314.34:packEditorLabelWidget
    def packEditorLabelWidget (self,w):

        '''Create a Tk label widget.'''

        # if not hasattr(w,'leo_label') or not w.leo_label:
            # # g.trace('w.leo_frame',id(w.leo_frame))
            # w.pack_forget()
            # w.leo_label = Tk.Label(w.leo_frame)
            # w.leo_label.pack(side='top')
            # w.pack(expand=1,fill='both')
    #@nonl
    #@-node:ekr.20081103095314.34:packEditorLabelWidget
    #@-node:ekr.20081103095314.32:Editors (qtBody)
    #@-others
#@-node:ekr.20081004172422.502:class leoQtBody (leoBody)
#@+node:ekr.20081007015817.56:class leoQtFindTab (findTab)
class leoQtFindTab (leoFind.findTab):

    '''A subclass of the findTab class containing all Qt Gui code.'''

    if 0: # We can use the base-class ctor.
        def __init__ (self,c,parentFrame):
            leoFind.findTab.__init__(self,c,parentFrame)
                # Init the base class.
                # Calls initGui, createFrame, createBindings & init(c), in that order.

    # Define these to suppress oops messages.
    def createBindings (self): pass
    def createFindTab (self,c,parentFrame): pass
    def createFrame (self,parentFrame): pass

    #@    @+others
    #@+node:ekr.20081018053140.14: Birth: called from leoFind ctor
    # leoFind.__init__ calls initGui, createFrame, createBindings & init, in that order.
    #@+node:ekr.20081007015817.59:initGui
    def initGui (self):

        self.svarDict = {}
            # Keys are ivar names, values are svar objects.

        for key in self.intKeys:
            self.svarDict[key] = self.svar()

        for key in self.newStringKeys:
            self.svarDict[key] = self.svar()
    #@nonl
    #@-node:ekr.20081007015817.59:initGui
    #@+node:ekr.20081007015817.60:init (qtFindTab) & helpers
    def init (self,c):

        '''Init the widgets of the 'Find' tab.'''

        self.createIvars()
        self.initIvars()
        self.initTextWidgets()
        self.initCheckBoxes()
        self.initRadioButtons()
    #@+node:ekr.20081018053140.19:createIvars
    def createIvars (self):

        c = self.c ; w = c.frame.top.ui # A Window ui object.

        # Bind boxes to Window objects.
        self.widgetsDict = {} # Keys are ivars, values are Qt widgets.
        data = (
            ('find_ctrl',       findTextWrapper(w.findPattern,'find-widget',c)),
            ('change_ctrl',     findTextWrapper(w.findChange,'change-widget',c)),
            ('whole_world',     w.checkBoxWholeWord),
            ('ignore_case',     w.checkBoxIgnoreCase),
            ('wrap',            w.checkBoxWrapAround),
            ('reverse',         w.checkBoxReverse),
            ('pattern_match',   w.checkBoxRexexp),
            ('mark_finds',      w.checkBoxMarkFinds),
            ('entire-outline',  w.checkBoxEntireOutline),
            ('suboutline-only', w.checkBoxSubroutineOnly),  
            ('node-only',       w.checkBoxNodeOnly),
            ('search_headline', w.checkBoxSearchHeadline),
            ('search_body',     w.checkBoxSearchBody),
            ('mark_changes',    w.checkBoxMarkChanges),
        )
        for ivar,widget in data:
            setattr(self,ivar,widget)
            self.widgetsDict[ivar] = widget
            # g.trace(ivar,widget)
    #@-node:ekr.20081018053140.19:createIvars
    #@+node:ekr.20081018053140.16:initIvars
    def initIvars(self):

        c = self.c

        # Separate c.ivars are much more convenient than a svarDict.
        for key in self.intKeys:
            # Get ivars from @settings.
            val = c.config.getBool(key)
            setattr(self,key,val)
            val = g.choose(val,1,0)
            svar = self.svarDict.get(key)
            if svar: svar.set(val)
            # g.trace('qtFindTab',key,val)
    #@-node:ekr.20081018053140.16:initIvars
    #@+node:ekr.20081018130812.10:initTextWidgets
    def initTextWidgets(self):

        '''Init the find/change text areas.'''

        c = self.c

        table = (
            (self.find_ctrl,    "find_text",    '<find pattern here>'),
            (self.change_ctrl,  "change_text",  ''),
        )

        for w,setting,defaultText in table:
            # w is a textWrapper object
            w.setAllText(c.config.getString(setting) or defaultText)
    #@-node:ekr.20081018130812.10:initTextWidgets
    #@+node:ekr.20081018053140.17:initCheckBoxes
    def initCheckBoxes (self):

        for ivar,key in (
            ("pattern_match","pattern-search"),
        ):
            svar = self.svarDict[ivar].get()
            if svar:
                self.svarDict["radio-find-type"].set(key)
                w = self.widgetsDict.get(key)
                if w: w.setChecked(True)
                break
        else:
            self.svarDict["radio-find-type"].set("plain-search")

        aList = (
            'ignore_case','mark_changes','mark_finds',
            'pattern_match','reverse','search_body','search_headline',
            'whole_word','wrap')

        for ivar in aList:
            svar = self.svarDict[ivar].get()
            if svar:
                # w is a QCheckBox.
                w = self.widgetsDict.get(ivar)
                if w: w.setChecked(True)
    #@-node:ekr.20081018053140.17:initCheckBoxes
    #@+node:ekr.20081018130812.11:initRadioButtons
    def initRadioButtons (self):

        for ivar,key in (
            ("suboutline_only","suboutline-only"),
            ("node_only","node-only"),
            # ("selection_only","selection-only")
        ):
            svar = self.svarDict[ivar].get()
            if svar:
                self.svarDict["radio-search-scope"].set(key)
                break
        else:
            key = 'entire-outline'
            self.svarDict["radio-search-scope"].set(key)
            # XXX At present w is a QCheckbox, not a QRadioButton.
            w = self.widgetsDict.get(key)
            if w: w.setChecked(True)
    #@-node:ekr.20081018130812.11:initRadioButtons
    #@-node:ekr.20081007015817.60:init (qtFindTab) & helpers
    #@-node:ekr.20081018053140.14: Birth: called from leoFind ctor
    #@+node:ekr.20081007015817.64:class svar
    class svar:
        '''A class like Tk's IntVar and StringVar classes.'''
        def __init__(self):
            self.val = None
        def get (self):
            return self.val
        def set (self,val):
            self.val = val
    #@-node:ekr.20081007015817.64:class svar
    #@+node:ekr.20081007015817.72:Support for minibufferFind class (qtFindTab)
    # This is the same as the Tk code because we simulate Tk svars.
    #@nonl
    #@+node:ekr.20081007015817.73:getOption
    def getOption (self,ivar):

        var = self.svarDict.get(ivar)

        if var:
            val = var.get()
            # g.trace('%s = %s' % (ivar,val))
            return val
        else:
            g.trace('bad ivar name: %s' % ivar)
            return None
    #@-node:ekr.20081007015817.73:getOption
    #@+node:ekr.20081007015817.74:setOption
    def setOption (self,ivar,val):

        if ivar in self.intKeys:
            if val is not None:
                var = self.svarDict.get(ivar)
                var.set(val)
                # g.trace('%s = %s' % (ivar,val))

        elif not g.app.unitTesting:
            g.trace('oops: bad find ivar %s' % ivar)
    #@-node:ekr.20081007015817.74:setOption
    #@+node:ekr.20081007015817.75:toggleOption
    def toggleOption (self,ivar):

        if ivar in self.intKeys:
            var = self.svarDict.get(ivar)
            val = not var.get()
            var.set(val)
            # g.trace('%s = %s' % (ivar,val),var)
        else:
            g.trace('oops: bad find ivar %s' % ivar)
    #@-node:ekr.20081007015817.75:toggleOption
    #@-node:ekr.20081007015817.72:Support for minibufferFind class (qtFindTab)
    #@-others
#@-node:ekr.20081007015817.56:class leoQtFindTab (findTab)
#@+node:ekr.20081004172422.523:class leoQtFrame
class leoQtFrame (leoFrame.leoFrame):

    """A class that represents a Leo window rendered in qt."""

    #@    @+others
    #@+node:ekr.20081004172422.524: Birth & Death (qtFrame)
    #@+node:ekr.20081004172422.525:__init__ (qtFrame)
    def __init__(self,title,gui):

        # Init the base class.
        leoFrame.leoFrame.__init__(self,gui)

        self.title = title
        self.initComplete = False # Set by initCompleteHint().
        leoQtFrame.instances += 1

        self.c = None # Set in finishCreate.
        self.iconBarClass = self.qtIconBarClass
        self.statusLineClass = self.qtStatusLineClass
        self.iconBar = None

        self.trace_status_line = None # Set in finishCreate.

        #@    << set the leoQtFrame ivars >>
        #@+node:ekr.20081004172422.526:<< set the leoQtFrame ivars >> (removed frame.bodyCtrl ivar)
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
        # self.treeBar = None # Replaced by injected frame.canvas.leo_treeBar.

        # Used by event handlers...
        self.controlKeyIsDown = False # For control-drags
        self.draggedItem = None
        self.isActive = True
        self.redrawCount = 0
        self.wantedWidget = None
        self.wantedCallbackScheduled = False
        self.scrollWay = None
        #@-node:ekr.20081004172422.526:<< set the leoQtFrame ivars >> (removed frame.bodyCtrl ivar)
        #@nl

        self.minibufferVisible = True
    #@-node:ekr.20081004172422.525:__init__ (qtFrame)
    #@+node:ekr.20081004172422.527:__repr__ (qtFrame)
    def __repr__ (self):

        return "<leoQtFrame: %s>" % self.title
    #@-node:ekr.20081004172422.527:__repr__ (qtFrame)
    #@+node:ekr.20081004172422.528:qtFrame.finishCreate & helpers
    def finishCreate (self,c):

        f = self ; f.c = c

        # g.trace('***qtFrame')

        self.bigTree           = c.config.getBool('big_outline_pane')
        self.trace_status_line = c.config.getBool('trace_status_line')
        self.use_chapters      = c.config.getBool('use_chapters')
        self.use_chapter_tabs  = c.config.getBool('use_chapter_tabs')

        # xx todo
        f.top = DynamicWindow(c)
        g.app.gui.attachLeoIcon(f.top)
        f.top.setWindowTitle(self.title)
        f.top.show()

        # This must be done after creating the commander.
        f.splitVerticalFlag,f.ratio,f.secondary_ratio = f.initialRatios()
        # # f.createOuterFrames()
        f.createIconBar() # A base class method.
        # # f.createLeoSplitters(f.outerFrame)
        f.createSplitterComponents()
        f.createStatusLine() # A base class method.
        f.createFirstTreeNode() # Call the base-class method.
        f.menu = leoQtMenu(f)
        c.setLog()
        g.app.windowList.append(f)
        c.initVersion()
        c.signOnWithVersion()
        f.miniBufferWidget = leoQtMinibuffer(c)
        c.bodyWantsFocusNow()
    #@+node:ekr.20081004172422.530:createSplitterComponents (qtFrame)
    def createSplitterComponents (self):

        f = self ; c = f.c

        f.tree  = leoQtTree(c,f)
        f.log   = leoQtLog(f,None)
        f.body  = leoQtBody(f,None)

        if f.use_chapters:
            c.chapterController = cc = leoChapters.chapterController(c)

        # # Create the canvas, tree, log and body.
        # if f.use_chapters:
            # c.chapterController = cc = leoChapters.chapterController(c)

        # # split1.pane1 is the secondary splitter.

        # if self.bigTree: # Put outline in the main splitter.
            # if self.use_chapters and self.use_chapter_tabs:
                # cc.tt = leoQtTreeTab(c,f.split1Pane2,cc)
            # f.canvas = f.createCanvas(f.split1Pane1)
            # f.tree  = leoQtTree(c,f,f.canvas)
            # f.log   = leoQtLog(f,f.split2Pane2)
            # f.body  = leoQtBody(f,f.split2Pane1)
        # else:
            # if self.use_chapters and self.use_chapter_tabs:
                # cc.tt = leoQtTreeTab(c,f.split2Pane1,cc)
            # f.canvas = f.createCanvas(f.split2Pane1)
            # f.tree   = leoQtTree(c,f,f.canvas)
            # f.log    = leoQtLog(f,f.split2Pane2)
            # f.body   = leoQtBody(f,f.split1Pane2)

        # # Yes, this an "official" ivar: this is a kludge.
        # # f.bodyCtrl = f.body.bodyCtrl

        # # Configure.
        # f.setTabWidth(c.tab_width)
        # f.reconfigurePanes()
        # f.body.setFontFromConfig()
        # f.body.setColorFromConfig()
    #@-node:ekr.20081004172422.530:createSplitterComponents (qtFrame)
    #@-node:ekr.20081004172422.528:qtFrame.finishCreate & helpers
    #@+node:ekr.20081020075840.20:initCompleteHint
    def initCompleteHint (self):

        '''A kludge: called to enable text changed events.'''

        self.initComplete = True
        # g.trace(self.c)
    #@-node:ekr.20081020075840.20:initCompleteHint
    #@+node:ekr.20081004172422.545:Destroying the qtFrame
    #@+node:ekr.20081004172422.546:destroyAllObjects
    def destroyAllObjects (self):

        """Clear all links to objects in a Leo window."""

        frame = self ; c = self.c

        # g.printGcAll()

        # Do this first.
        #@    << clear all vnodes and tnodes in the tree >>
        #@+node:ekr.20081004172422.547:<< clear all vnodes and tnodes in the tree>>
        # Using a dict here is essential for adequate speed.
        vList = [] ; tDict = {}

        for p in c.all_positions_with_unique_vnodes_iter():
            vList.append(p.v)
            if p.v.t:
                key = id(p.v.t)
                if key not in tDict:
                    tDict[key] = p.v.t

        for key in tDict:
            g.clearAllIvars(tDict[key])

        for v in vList:
            g.clearAllIvars(v)

        vList = [] ; tDict = {} # Remove these references immediately.
        #@-node:ekr.20081004172422.547:<< clear all vnodes and tnodes in the tree>>
        #@nl

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

    #@-node:ekr.20081004172422.546:destroyAllObjects
    #@+node:ekr.20081004172422.549:destroySelf (qtFrame)
    def destroySelf (self):

        # Remember these: we are about to destroy all of our ivars!
        c,top = self.c,self.top 

        # Indicate that the commander is no longer valid.
        c.exists = False

        if 0: # We can't do this unless we unhook the event filter.
            # Destroys all the objects of the commander.
            self.destroyAllObjects()

        c.exists = False # Make sure this one ivar has not been destroyed.

        # g.trace('qtFrame',c,g.callers(4))
        top.close()

    #@-node:ekr.20081004172422.549:destroySelf (qtFrame)
    #@-node:ekr.20081004172422.545:Destroying the qtFrame
    #@-node:ekr.20081004172422.524: Birth & Death (qtFrame)
    #@+node:ekr.20081004172422.550:class qtStatusLineClass (qtFrame)
    class qtStatusLineClass:

        '''A class representing the status line.'''

        #@    @+others
        #@+node:ekr.20081004172422.551:ctor
        def __init__ (self,c,parentFrame):

            self.c = c
            self.statusBar = c.frame.top.statusBar
            self.lastFcol= 0
            self.lastRow = 0
            self.lastCol = 0

            # Create the text widgets.
            self.textWidget1 = w1 = QtGui.QLineEdit(self.statusBar)
            self.textWidget2 = w2 = QtGui.QLineEdit(self.statusBar)
            w1.setObjectName('status1')
            w2.setObjectName('status2')
            self.statusBar.addWidget(w1,True)
            self.statusBar.addWidget(w2,True)
            self.put('')
            self.update()
            c.frame.top.setStyleSheets()
        #@-node:ekr.20081004172422.551:ctor
        #@+node:ekr.20081029110341.12: do-nothings
        def disable (self,background=None): pass
        def enable(self,background="white"):pass
        def getFrame (self):                return None
        def isEnabled(self):                return True
        def onActivate (self,event=None):   pass
        def pack (self):                    pass
        def setBindings (self):             pass
        def unpack (self):                  pass

        hide = unpack
        show = pack

        #@-node:ekr.20081029110341.12: do-nothings
        #@+node:ekr.20081004172422.554:clear, get & put/1
        def clear (self):
            self.put('')

        def get (self):
            return self.textWidget2.text()

        def put(self,s,color=None):
            self.put_helper(s,self.textWidget2)

        def put1(self,s,color=None):
            self.put_helper(s,self.textWidget1)

        def put_helper(self,s,w):
            # w.setEnabled(True)
            w.setText(s)
            # w.setEnabled(False)
        #@-node:ekr.20081004172422.554:clear, get & put/1
        #@+node:ekr.20081004172422.561:update
        def update (self):

            if g.app.killed: return
            c = self.c ; body = c.frame.body
            s = body.getAllText()
            i = body.getInsertPoint()
            # Compute row,col & fcol
            row,col = g.convertPythonIndexToRowCol(s,i)
            if col > 0:
                s2 = s[i-col:i]
                s2 = g.toUnicode(s2,g.app.tkEncoding)
                col = g.computeWidth (s2,c.tab_width)
            fcol = col + c.currentPosition().textOffset()
            self.put1(
                "line: %d, col: %d, fcol: %d" % (row,col,fcol))
            self.lastRow = row
            self.lastCol = col
            self.lastFcol = fcol
        #@-node:ekr.20081004172422.561:update
        #@-others
    #@-node:ekr.20081004172422.550:class qtStatusLineClass (qtFrame)
    #@+node:ekr.20081004172422.562:class qtIconBarClass
    class qtIconBarClass:

        '''A class representing the singleton Icon bar'''

        #@    @+others
        #@+node:ekr.20081004172422.563: ctor
        def __init__ (self,c,parentFrame):

            self.c = c
            self.parentFrame = parentFrame
            self.w = c.frame.top.iconBar # A QToolBar.

            # g.app.iconWidgetCount = 0
        #@-node:ekr.20081004172422.563: ctor
        #@+node:ekr.20081029205046.10: do-nothings
        def addRow(self,height=None):   pass
        def getFrame (self):            return None
        def getNewFrame (self):         return None
        def pack (self):                pass
        def unpack (self):              pass

        hide = unpack
        show = pack
        #@-node:ekr.20081029205046.10: do-nothings
        #@+node:ekr.20081004172422.564:add
        def add(self,*args,**keys):

            '''Add a button to the icon bar.'''

            c = self.c
            command = keys.get('command')
            text = keys.get('text')
            if not text: return

            # imagefile = keys.get('imagefile')
            # image = keys.get('image')

            b = QtGui.QPushButton(text,self.w)
            self.w.addWidget(b)

            if command:
                def button_callback(c=c,command=command):
                    g.trace('command',command.__name__)
                    val = command()
                    if c.exists:
                        c.bodyWantsFocus()
                        c.outerUpdate()
                    return val

                QtCore.QObject.connect(b,
                    QtCore.SIGNAL("clicked()"),
                    button_callback)

            return b
        #@-node:ekr.20081004172422.564:add
        #@+node:ekr.20081004172422.567:addRowIfNeeded
        def addRowIfNeeded (self):

            '''Add a new icon row if there are too many widgets.'''

            # n = g.app.iconWidgetCount

            # if n >= self.widgets_per_row:
                # g.app.iconWidgetCount = 0
                # self.addRow()

            # g.app.iconWidgetCount += 1
        #@-node:ekr.20081004172422.567:addRowIfNeeded
        #@+node:ekr.20081004172422.568:addWidget
        def addWidget (self,w):

            self.w.addWidget(w)
        #@-node:ekr.20081004172422.568:addWidget
        #@+node:ekr.20081004172422.569:clear
        def clear(self):

            """Destroy all the widgets in the icon bar"""

            self.w.clear()

            g.app.iconWidgetCount = 0
        #@-node:ekr.20081004172422.569:clear
        #@+node:ekr.20081004172422.570:deleteButton
        def deleteButton (self,w):

            g.trace(w)
            # self.w.deleteWidget(w)
            self.c.bodyWantsFocus()
            self.c.outerUpdate()
        #@-node:ekr.20081004172422.570:deleteButton
        #@+node:ekr.20081004172422.573:setCommandForButton
        def setCommandForButton(self,button,command):

            if command:
                QtCore.QObject.connect(button,
                    QtCore.SIGNAL("clicked()"),command)
        #@-node:ekr.20081004172422.573:setCommandForButton
        #@-others
    #@-node:ekr.20081004172422.562:class qtIconBarClass
    #@+node:ekr.20081004172422.575:Minibuffer methods
    #@+node:ekr.20081004172422.576:showMinibuffer
    def showMinibuffer (self):

        '''Make the minibuffer visible.'''

        # frame = self

        # if not frame.minibufferVisible:
            # frame.minibufferFrame.pack(side='bottom',fill='x')
            # frame.minibufferVisible = True
    #@-node:ekr.20081004172422.576:showMinibuffer
    #@+node:ekr.20081004172422.577:hideMinibuffer
    def hideMinibuffer (self):

        '''Hide the minibuffer.'''

        # frame = self

        # if frame.minibufferVisible:
            # frame.minibufferFrame.pack_forget()
            # frame.minibufferVisible = False
    #@-node:ekr.20081004172422.577:hideMinibuffer
    #@+node:ekr.20081004172422.579:f.setMinibufferBindings
    def setMinibufferBindings (self):

        '''Create bindings for the minibuffer..'''

        # return ###

        # f = self ; c = f.c ; k = c.k ; w = f.miniBufferWidget

        # table = [
            # ('<Key>',           k.masterKeyHandler),
            # ('<Button-1>',      k.masterClickHandler),
            # ('<Button-3>',      k.masterClick3Handler),
            # ('<Double-1>',      k.masterDoubleClickHandler),
            # ('<Double-3>',      k.masterDoubleClick3Handler),
        # ]

        # table2 = (
            # ('<Button-2>',      k.masterClickHandler),
        # )

        # if c.config.getBool('allow_middle_button_paste'):
            # table.extend(table2)

        # for kind,callback in table:
            # c.bind(w,kind,callback)

        # if 0:
            # if sys.platform.startswith('win'):
                # # Support Linux middle-button paste easter egg.
                # c.bind(w,"<Button-2>",f.OnPaste)
    #@-node:ekr.20081004172422.579:f.setMinibufferBindings
    #@-node:ekr.20081004172422.575:Minibuffer methods
    #@+node:ekr.20081004172422.580:Configuration (qtFrame)
    #@+node:ekr.20081004172422.581:configureBar (qtFrame)
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
    #@-node:ekr.20081004172422.581:configureBar (qtFrame)
    #@+node:ekr.20081004172422.582:configureBarsFromConfig (qtFrame)
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
    #@-node:ekr.20081004172422.582:configureBarsFromConfig (qtFrame)
    #@+node:ekr.20081004172422.583:reconfigureFromConfig (qtFrame)
    def reconfigureFromConfig (self):

        frame = self ; c = frame.c

        frame.tree.setFontFromConfig()
        frame.configureBarsFromConfig()

        frame.body.setFontFromConfig()
        frame.body.setColorFromConfig()

        frame.setTabWidth(c.tab_width)
        frame.log.setFontFromConfig()
        frame.log.setColorFromConfig()

        c.redraw_now()
    #@-node:ekr.20081004172422.583:reconfigureFromConfig (qtFrame)
    #@+node:ekr.20081004172422.584:setInitialWindowGeometry (qtFrame)
    def setInitialWindowGeometry(self):

        """Set the position and size of the frame to config params."""

        c = self.c

        h = c.config.getInt("initial_window_height") or 500
        w = c.config.getInt("initial_window_width") or 600
        x = c.config.getInt("initial_window_left") or 10
        y = c.config.getInt("initial_window_top") or 10

        if h and w and x and y:
            self.setTopGeometry(w,h,x,y)
    #@-node:ekr.20081004172422.584:setInitialWindowGeometry (qtFrame)
    #@+node:ekr.20081004172422.585:setTabWidth (qtFrame)
    def setTabWidth (self, w):

        return

        # try: # This can fail when called from scripts
            # # Use the present font for computations.
            # font = self.body.bodyCtrl.cget("font") # 2007/10/27
            # root = g.app.root # 4/3/03: must specify root so idle window will work properly.
            # font = tkFont.Font(root=root,font=font)
            # tabw = font.measure(" " * abs(w)) # 7/2/02
            # self.body.bodyCtrl.configure(tabs=tabw)
            # self.tab_width = w
            # # g.trace(w,tabw)
        # except:
            # g.es_exception()
    #@-node:ekr.20081004172422.585:setTabWidth (qtFrame)
    #@+node:ekr.20081004172422.586:setWrap (qtFrame)
    def setWrap (self,p):

        c = self.c
        theDict = c.scanAllDirectives(p)
        if not theDict: return

        return

        # wrap = theDict.get("wrap")
        # if self.body.wrapState == wrap: return

        # self.body.wrapState = wrap
        # w = self.body.bodyCtrl

        # # g.trace(wrap)
        # if wrap:
            # w.configure(wrap="word") # 2007/10/25
            # w.leo_bodyXBar.pack_forget() # 2007/10/31
        # else:
            # w.configure(wrap="none")
            # # Bug fix: 3/10/05: We must unpack the text area to make the scrollbar visible.
            # w.pack_forget()  # 2007/10/25
            # w.leo_bodyXBar.pack(side="bottom", fill="x") # 2007/10/31
            # w.pack(expand=1,fill="both")  # 2007/10/25
    #@-node:ekr.20081004172422.586:setWrap (qtFrame)
    #@+node:ekr.20081004172422.588:reconfigurePanes (use config bar_width) (qtFrame)
    def reconfigurePanes (self):

        return

        # c = self.c

        # border = c.config.getInt('additional_body_text_border')
        # if border == None: border = 0

        # # The body pane needs a _much_ bigger border when tiling horizontally.
        # border = g.choose(self.splitVerticalFlag,2+border,6+border)
        # self.body.bodyCtrl.configure(bd=border) # 2007/10/25

        # # The log pane needs a slightly bigger border when tiling vertically.
        # border = g.choose(self.splitVerticalFlag,4,2) 
        # self.log.configureBorder(border)
    #@-node:ekr.20081004172422.588:reconfigurePanes (use config bar_width) (qtFrame)
    #@+node:ekr.20081004172422.589:resizePanesToRatio (qtFrame)
    def resizePanesToRatio(self,ratio,ratio2):

        pass

        # g.trace(ratio,ratio2,g.callers())

        # self.divideLeoSplitter(self.splitVerticalFlag,ratio)
        # self.divideLeoSplitter(not self.splitVerticalFlag,ratio2)
    #@-node:ekr.20081004172422.589:resizePanesToRatio (qtFrame)
    #@-node:ekr.20081004172422.580:Configuration (qtFrame)
    #@+node:ekr.20081004172422.590:Event handlers (qtFrame)
    #@+node:ekr.20081004172422.591:frame.OnCloseLeoEvent
    # Called from quit logic and when user closes the window.
    # Returns True if the close happened.

    def OnCloseLeoEvent(self):

        f = self ; c = f.c

        if c.inCommand:
            # g.trace('requesting window close')
            c.requestCloseWindow = True
        else:
            g.app.closeLeoWindow(self)
    #@-node:ekr.20081004172422.591:frame.OnCloseLeoEvent
    #@+node:ekr.20081004172422.592:frame.OnControlKeyUp/Down
    def OnControlKeyDown (self,event=None):

        self.controlKeyIsDown = True

    def OnControlKeyUp (self,event=None):

        self.controlKeyIsDown = False
    #@-node:ekr.20081004172422.592:frame.OnControlKeyUp/Down
    #@+node:ekr.20081004172422.593:OnActivateBody (qtFrame)
    def OnActivateBody (self,event=None):

        # try:
            # frame = self ; c = frame.c
            # c.setLog()
            # w = c.get_focus()
            # if w != c.frame.body.bodyCtrl:
                # frame.tree.OnDeactivate()
            # c.bodyWantsFocusNow()
        # except:
            # g.es_event_exception("activate body")

        return 'break'
    #@-node:ekr.20081004172422.593:OnActivateBody (qtFrame)
    #@+node:ekr.20081004172422.594:OnActivateLeoEvent, OnDeactivateLeoEvent
    def OnActivateLeoEvent(self,event=None):

        '''Handle a click anywhere in the Leo window.'''

        self.c.setLog()

    def OnDeactivateLeoEvent(self,event=None):

        pass # This causes problems on the Mac.
    #@-node:ekr.20081004172422.594:OnActivateLeoEvent, OnDeactivateLeoEvent
    #@+node:ekr.20081004172422.595:OnActivateTree
    def OnActivateTree (self,event=None):

        try:
            frame = self ; c = frame.c
            c.setLog()

            if 0: # Do NOT do this here!
                # OnActivateTree can get called when the tree gets DE-activated!!
                c.bodyWantsFocus()

        except:
            g.es_event_exception("activate tree")
    #@-node:ekr.20081004172422.595:OnActivateTree
    #@+node:ekr.20081004172422.596:OnBodyClick, OnBodyRClick (Events)
    def OnBodyClick (self,event=None):

        try:
            c = self.c ; p = c.currentPosition()
            if not g.doHook("bodyclick1",c=c,p=p,v=p,event=event):
                self.OnActivateBody(event=event)
                c.k.showStateAndMode(w=c.frame.body.bodyCtrl)
            g.doHook("bodyclick2",c=c,p=p,v=p,event=event)
        except:
            g.es_event_exception("bodyclick")

    def OnBodyRClick(self,event=None):

        try:
            c = self.c ; p = c.currentPosition()
            if not g.doHook("bodyrclick1",c=c,p=p,v=p,event=event):
                c.k.showStateAndMode(w=c.frame.body.bodyCtrl)
            g.doHook("bodyrclick2",c=c,p=p,v=p,event=event)
        except:
            g.es_event_exception("iconrclick")
    #@-node:ekr.20081004172422.596:OnBodyClick, OnBodyRClick (Events)
    #@+node:ekr.20081004172422.597:OnBodyDoubleClick (Events)
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
    #@-node:ekr.20081004172422.597:OnBodyDoubleClick (Events)
    #@-node:ekr.20081004172422.590:Event handlers (qtFrame)
    #@+node:ekr.20081004172422.599:Gui-dependent commands
    #@+node:ekr.20081004172422.600:Minibuffer commands... (qtFrame)
    #@+node:ekr.20081004172422.601:contractPane
    def contractPane (self,event=None):

        '''Contract the selected pane.'''

        # f = self ; c = f.c
        # w = c.get_requested_focus()
        # wname = c.widget_name(w)

        # # g.trace(wname)
        # if not w: return

        # if wname.startswith('body'):
            # f.contractBodyPane()
        # elif wname.startswith('log'):
            # f.contractLogPane()
        # elif wname.startswith('head') or wname.startswith('canvas'):
            # f.contractOutlinePane()
    #@-node:ekr.20081004172422.601:contractPane
    #@+node:ekr.20081004172422.602:expandPane
    def expandPane (self,event=None):

        '''Expand the selected pane.'''

        # f = self ; c = f.c

        # w = c.get_requested_focus()
        # wname = c.widget_name(w)

        # # g.trace(wname)
        # if not w: return

        # if wname.startswith('body'):
            # f.expandBodyPane()
        # elif wname.startswith('log'):
            # f.expandLogPane()
        # elif wname.startswith('head') or wname.startswith('canvas'):
            # f.expandOutlinePane()
    #@-node:ekr.20081004172422.602:expandPane
    #@+node:ekr.20081004172422.603:fullyExpandPane
    def fullyExpandPane (self,event=None):

        '''Fully expand the selected pane.'''

        # f = self ; c = f.c

        # w = c.get_requested_focus()
        # wname = c.widget_name(w)

        # # g.trace(wname)
        # if not w: return

        # if wname.startswith('body'):
            # f.fullyExpandBodyPane()
        # elif wname.startswith('log'):
            # f.fullyExpandLogPane()
        # elif wname.startswith('head') or wname.startswith('canvas'):
            # f.fullyExpandOutlinePane()
    #@-node:ekr.20081004172422.603:fullyExpandPane
    #@+node:ekr.20081004172422.604:hidePane
    def hidePane (self,event=None):

        '''Completely contract the selected pane.'''

        # f = self ; c = f.c

        # w = c.get_requested_focus()
        # wname = c.widget_name(w)

        # g.trace(wname)
        # if not w: return

        # if wname.startswith('body'):
            # f.hideBodyPane()
            # c.treeWantsFocusNow()
        # elif wname.startswith('log'):
            # f.hideLogPane()
            # c.bodyWantsFocusNow()
        # elif wname.startswith('head') or wname.startswith('canvas'):
            # f.hideOutlinePane()
            # c.bodyWantsFocusNow()
    #@-node:ekr.20081004172422.604:hidePane
    #@+node:ekr.20081004172422.605:expand/contract/hide...Pane
    #@+at 
    #@nonl
    # The first arg to divideLeoSplitter means the following:
    # 
    #     f.splitVerticalFlag: use the primary   (tree/body) ratio.
    # not f.splitVerticalFlag: use the secondary (tree/log) ratio.
    #@-at
    #@@c

    def contractBodyPane (self,event=None):
        '''Contract the body pane.'''
        # f = self ; r = min(1.0,f.ratio+0.1)
        # f.divideLeoSplitter(f.splitVerticalFlag,r)

    def contractLogPane (self,event=None):
        '''Contract the log pane.'''
        # f = self ; r = min(1.0,f.ratio+0.1)
        # f.divideLeoSplitter(not f.splitVerticalFlag,r)

    def contractOutlinePane (self,event=None):
        '''Contract the outline pane.'''
        # f = self ; r = max(0.0,f.ratio-0.1)
        # f.divideLeoSplitter(f.splitVerticalFlag,r)

    def expandBodyPane (self,event=None):
        '''Expand the body pane.'''
        # self.contractOutlinePane()

    def expandLogPane(self,event=None):
        '''Expand the log pane.'''
        # f = self ; r = max(0.0,f.ratio-0.1)
        # f.divideLeoSplitter(not f.splitVerticalFlag,r)

    def expandOutlinePane (self,event=None):
        '''Expand the outline pane.'''
        # self.contractBodyPane()
    #@-node:ekr.20081004172422.605:expand/contract/hide...Pane
    #@+node:ekr.20081004172422.606:fullyExpand/hide...Pane
    def fullyExpandBodyPane (self,event=None):
        '''Fully expand the body pane.'''
        f = self
        # f.divideLeoSplitter(f.splitVerticalFlag,0.0)

    def fullyExpandLogPane (self,event=None):
        '''Fully expand the log pane.'''
        f = self
        # f.divideLeoSplitter(not f.splitVerticalFlag,0.0)

    def fullyExpandOutlinePane (self,event=None):
        '''Fully expand the outline pane.'''
        f = self
        # f.divideLeoSplitter(f.splitVerticalFlag,1.0)

    def hideBodyPane (self,event=None):
        '''Completely contract the body pane.'''
        f = self
        # f.divideLeoSplitter(f.splitVerticalFlag,1.0)

    def hideLogPane (self,event=None):
        '''Completely contract the log pane.'''
        f = self
        # f.divideLeoSplitter(not f.splitVerticalFlag,1.0)

    def hideOutlinePane (self,event=None):
        '''Completely contract the outline pane.'''
        f = self
        # f.divideLeoSplitter(f.splitVerticalFlag,0.0)
    #@-node:ekr.20081004172422.606:fullyExpand/hide...Pane
    #@-node:ekr.20081004172422.600:Minibuffer commands... (qtFrame)
    #@+node:ekr.20081004172422.607:Window Menu...
    #@+node:ekr.20081004172422.608:toggleActivePane (qtFrame)
    def toggleActivePane (self,event=None):

        '''Toggle the focus between the outline and body panes.'''

        frame = self ; c = frame.c

        if c.get_focus() == frame.body.bodyCtrl: # 2007/10/25
            c.treeWantsFocusNow()
        else:
            c.endEditing()
            c.bodyWantsFocusNow()
    #@-node:ekr.20081004172422.608:toggleActivePane (qtFrame)
    #@+node:ekr.20081004172422.609:cascade
    def cascade (self,event=None):

        '''Cascade all Leo windows.'''

        # x,y,delta = 10,10,10
        # for frame in g.app.windowList:
            # top = frame.top

            # # Compute w,h
            # top.update_idletasks() # Required to get proper info.
            # geom = top.geometry() # geom = "WidthxHeight+XOffset+YOffset"
            # dim,junkx,junky = geom.split('+')
            # w,h = dim.split('x')
            # w,h = int(w),int(h)

            # # Set new x,y and old w,h
            # frame.setTopGeometry(w,h,x,y,adjustSize=False)

            # # Compute the new offsets.
            # x += 30 ; y += 30
            # if x > 200:
                # x = 10 + delta ; y = 40 + delta
                # delta += 10
    #@-node:ekr.20081004172422.609:cascade
    #@+node:ekr.20081004172422.610:equalSizedPanes
    def equalSizedPanes (self,event=None):

        '''Make the outline and body panes have the same size.'''

        frame = self
        frame.resizePanesToRatio(0.5,frame.secondary_ratio)
    #@-node:ekr.20081004172422.610:equalSizedPanes
    #@+node:ekr.20081004172422.611:hideLogWindow
    def hideLogWindow (self,event=None):

        frame = self

        # frame.divideLeoSplitter2(0.99, not frame.splitVerticalFlag)
    #@-node:ekr.20081004172422.611:hideLogWindow
    #@+node:ekr.20081004172422.612:minimizeAll
    def minimizeAll (self,event=None):

        '''Minimize all Leo's windows.'''

        self.minimize(g.app.pythonFrame)
        for frame in g.app.windowList:
            self.minimize(frame)
            self.minimize(frame.findPanel)

    def minimize(self,frame):

        pass

        # if frame and frame.top.state() == "normal":
            # frame.top.iconify()
    #@-node:ekr.20081004172422.612:minimizeAll
    #@+node:ekr.20081004172422.613:toggleSplitDirection (qtFrame)
    # The key invariant: self.splitVerticalFlag tells the alignment of the main splitter.

    def toggleSplitDirection (self,event=None):

        '''Toggle the split direction in the present Leo window.'''

        # # Switch directions.
        # c = self.c
        # self.splitVerticalFlag = not self.splitVerticalFlag
        # orientation = g.choose(self.splitVerticalFlag,"vertical","horizontal")
        # c.config.set("initial_splitter_orientation","string",orientation)

        # self.toggleQtSplitDirection(self.splitVerticalFlag)
    #@+node:ekr.20081004172422.614:toggleQtSplitDirection
    def toggleQtSplitDirection (self,verticalFlag):

        # Abbreviations.
        frame = self
        # bar1 = self.bar1 ; bar2 = self.bar2
        # split1Pane1,split1Pane2 = self.split1Pane1,self.split1Pane2
        # split2Pane1,split2Pane2 = self.split2Pane1,self.split2Pane2
        # # Reconfigure the bars.
        # bar1.place_forget()
        # bar2.place_forget()
        # self.configureBar(bar1,verticalFlag)
        # self.configureBar(bar2,not verticalFlag)
        # # Make the initial placements again.
        # self.placeSplitter(bar1,split1Pane1,split1Pane2,verticalFlag)
        # self.placeSplitter(bar2,split2Pane1,split2Pane2,not verticalFlag)
        # # Adjust the log and body panes to give more room around the bars.
        # self.reconfigurePanes()
        # # Redraw with an appropriate ratio.
        # vflag,ratio,secondary_ratio = frame.initialRatios()
        # self.resizePanesToRatio(ratio,secondary_ratio)
    #@-node:ekr.20081004172422.614:toggleQtSplitDirection
    #@-node:ekr.20081004172422.613:toggleSplitDirection (qtFrame)
    #@+node:ekr.20081004172422.615:resizeToScreen
    def resizeToScreen (self,event=None):

        '''Resize the Leo window so it fill the entire screen.'''

        top = self.top

        # w = top.winfo_screenwidth()
        # h = top.winfo_screenheight()

        # if sys.platform.startswith('win'):
            # top.state('zoomed')
        # elif sys.platform == 'darwin':
            # # Must leave room to get at very small resizing area.
            # geom = "%dx%d%+d%+d" % (w-20,h-55,10,25)
            # top.geometry(geom)
        # else:
            # # Fill almost the entire screen.
            # # Works on Windows. YMMV for other platforms.
            # geom = "%dx%d%+d%+d" % (w-8,h-46,0,0)
            # top.geometry(geom)
    #@-node:ekr.20081004172422.615:resizeToScreen
    #@-node:ekr.20081004172422.607:Window Menu...
    #@+node:ekr.20081004172422.616:Help Menu...
    #@+node:ekr.20081004172422.617:leoHelp
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
                    if 0: # Download directly.  (showProgressBar needs a lot of work)
                        url = "http://umn.dl.sourceforge.net/sourceforge/leo/sbooks.chm"
                        import urllib
                        self.scale = None
                        urllib.urlretrieve(url,theFile,self.showProgressBar)
                        if self.scale:
                            self.scale.destroy()
                            self.scale = None
                    else:
                        url = "http://prdownloads.sourceforge.net/leo/sbooks.chm?download"
                        import webbrowser
                        os.chdir(g.app.loadDir)
                        webbrowser.open_new(url)
                except:
                    g.es("exception downloading","sbooks.chm")
                    g.es_exception()
    #@+node:ekr.20081004172422.618:showProgressBar
    def showProgressBar (self,count,size,total):

        # g.trace("count,size,total:",count,size,total)
        if self.scale == None:
            pass
            #@        << create the scale widget >>
            #@+node:ekr.20081004172422.619:<< create the scale widget >>
            # top = qt.Toplevel()
            # top.title("Download progress")
            # self.scale = scale = qt.Scale(top,state="normal",orient="horizontal",from_=0,to=total)
            # scale.pack()
            # top.lift()
            #@-node:ekr.20081004172422.619:<< create the scale widget >>
            #@nl
        # self.scale.set(count*size)
        # self.scale.update_idletasks()
    #@-node:ekr.20081004172422.618:showProgressBar
    #@-node:ekr.20081004172422.617:leoHelp
    #@-node:ekr.20081004172422.616:Help Menu...
    #@-node:ekr.20081004172422.599:Gui-dependent commands
    #@+node:ekr.20081004172422.621:Qt bindings... (qtFrame)
    def bringToFront (self):
        self.top.showNormal()
    def deiconify (self):
        self.top.showNormal()
    def getFocus(self):
        return g.app.gui.get_focus() 
    def get_window_info(self):
        rect = self.top.geometry()
        topLeft = rect.topLeft()
        x,y = topLeft.x(),topLeft.y()
        w,h = rect.width(),rect.height()
        return w,h,x,y
    def iconify(self):
        g.trace()
        self.top.showMinimized()
    def lift (self):
        self.top.activateWindow()
    def update (self):
        pass
    def getTitle (self):
        return g.toUnicode(self.top.windowTitle(),'utf-8')
    def setTitle (self,s):
        self.top.setWindowTitle(s)
    def setTopGeometry(self,w,h,x,y,adjustSize=True):
        self.top.setGeometry(QtCore.QRect(x,y,w,h))
    #@-node:ekr.20081004172422.621:Qt bindings... (qtFrame)
    #@-others
#@-node:ekr.20081004172422.523:class leoQtFrame
#@+node:ekr.20081004172422.622:class leoQtLog
class leoQtLog (leoFrame.leoLog):

    """A class that represents the log pane of a Qt window."""

    #@    @+others
    #@+node:ekr.20081004172422.623:qtLog Birth
    #@+node:ekr.20081004172422.624:qtLog.__init__
    def __init__ (self,frame,parentFrame):

        # g.trace("leoQtLog")

        # Call the base class constructor and calls createControl.
        leoFrame.leoLog.__init__(self,frame,parentFrame)

        self.c = c = frame.c # Also set in the base constructor, but we need it here.
        self.logCtrl = None # The text area for log messages.

        self.contentsDict = {} # Keys are tab names.  Values are widgets.
        self.logDict = {} # Keys are tab names text widgets.  Values are the widgets.
        self.menu = None # A menu that pops up on right clicks in the hull or in tabs.

        self.tabWidget = c.frame.top.ui.tabWidget # The Qt.TabWidget that holds all the tabs.
        self.wrap = g.choose(c.config.getBool('log_pane_wraps'),"word","none")

        self.filter = leoQtEventFilter(c,w=self,tag='tabbed-log')

        self.setFontFromConfig()
        self.setColorFromConfig()
    #@-node:ekr.20081004172422.624:qtLog.__init__
    #@+node:ekr.20081004172422.626:qtLog.finishCreate
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
            if w.tabText(i) == 'Tab 2':
                # g.trace('found Tab 2',w.currentWidget())
                w.setTabText(i,'Find')
                self.contentsDict['Find'] = w.currentWidget()
                break

        # Create the log tab as the leftmost tab.
        log.selectTab('Log')

        logWidget = self.contentsDict.get('Log')
        for i in range(w.count()):
            if w.tabText(i) == 'Log':
                w.removeTab(i)
                w.insertTab(0,logWidget,'Log')
                break

        c.searchCommands.openFindTab(show=False)
        c.spellCommands.openSpellTab()
    #@nonl
    #@-node:ekr.20081004172422.626:qtLog.finishCreate
    #@-node:ekr.20081004172422.623:qtLog Birth
    #@+node:ekr.20081017015442.30:Do nothings
    # def createCanvas (self,tabName=None): pass

    # def getSelectedTab (self): return self.tabName

    # def lowerTab (self,tabName):
        # self.c.invalidateFocus()
        # self.c.bodyWantsFocus()

    # def makeTabMenu (self,tabName=None,allowRename=True): pass

    # def onLogTextRightClick(self, event):
        # g.doHook('rclick-popup',c=self.c,event=event, context_menu='log')

    # def raiseTab (self,tabName):
        # self.c.invalidateFocus()
        # self.c.bodyWantsFocus()

    # def renameTab (self,oldName,newName): pass

    # def setCanvasTabBindings (self,tabName,menu): pass

    # def setTabBindings (self,tabName): pass

    #@+node:ekr.20081004172422.630:Config
    # These will probably be replaced by style sheets.

    def configureBorder(self,border):   pass
    def configureFont(self,font):       pass
    def getFontConfig (self):           pass

    def setColorFromConfig (self):
        c = self.c
        # bg = c.config.getColor("log_pane_background_color") or 'white'

    def SetWidgetFontFromConfig (self,logCtrl=None):
        c = self.c
        # font = c.config.getFontFromParams(
            # "log_text_font_family", "log_text_font_size",
            # "log_text_font_slant", "log_text_font_weight",
            # c.config.defaultLogFontSize)

    def saveAllState (self):
        '''Return a dict containing all data needed to recreate the log in another widget.'''
        # Save text and colors
    def restoreAllState (self,d):
        '''Restore the log from a dict created by saveAllState.'''
        # Restore text and colors.
    #@-node:ekr.20081004172422.630:Config
    #@+node:ekr.20081004172422.637:Focus & update
    def onActivateLog (self,event=None):    pass
    def hasFocus (self):                    return None
    def forceLogUpdate (self,s):            pass
    #@-node:ekr.20081004172422.637:Focus & update
    #@-node:ekr.20081017015442.30:Do nothings
    #@+node:ekr.20081004172422.641:put & putnl (qtLog)
    #@+node:ekr.20081004172422.642:put
    # All output to the log stream eventually comes here.
    def put (self,s,color=None,tabName='Log'):

        c = self.c
        if g.app.quitting or not c or not c.exists:
            return

        self.selectTab(tabName or 'Lob')

        # Note: this must be done after the call to selectTab.
        w = self.logCtrl # w is a QTextBrowser
        if w:
            # g.trace(repr(s))
            if s.endswith('\n'): s = s[:-1]
            s = s.replace(' ','&nbsp;')
            if color:
                s = '<font color="%s">%s</font>' % (color, s)
            s = s.replace('\n','<br>')
            sb = w.horizontalScrollBar()
            pos = sb.sliderPosition()
            w.append(s)
            w.moveCursor(QtGui.QTextCursor.End)
            sb.setSliderPosition(pos)
        else:
            # put s to logWaiting and print s
            g.app.logWaiting.append((s,color),)
            if type(s) == type(u""):
                s = g.toEncodedString(s,"ascii")
            print s
    #@-node:ekr.20081004172422.642:put
    #@+node:ekr.20081004172422.645:putnl
    def putnl (self,tabName='Log'):

        if g.app.quitting:
            return

        if tabName:
            self.selectTab(tabName)

        w = self.logCtrl
        if w:
            sb = w.horizontalScrollBar()
            pos = sb.sliderPosition()
            contents = w.toHtml()
            w.setHtml(contents + '\n')
            w.moveCursor(QtGui.QTextCursor.End)
            sb.setSliderPosition(pos)
            w.repaint()
        else:
            # put s to logWaiting and print  a newline
            g.app.logWaiting.append(('\n','black'),)
    #@-node:ekr.20081004172422.645:putnl
    #@-node:ekr.20081004172422.641:put & putnl (qtLog)
    #@+node:ekr.20081004172422.646:Tab (qtLog)
    #@+node:ekr.20081004172422.647:clearTab
    def clearTab (self,tabName,wrap='none'):

        w = self.logDict.get(tabName)
        if w:
            w.clear() # w is a QTextBrowser.
    #@-node:ekr.20081004172422.647:clearTab
    #@+node:ekr.20081004172422.649:createTab
    def createTab (self,tabName,createText=True,wrap='none'):

        c = self.c ; w = self.tabWidget

        if createText:
            contents = QtGui.QTextBrowser()
            contents.setWordWrapMode(QtGui.QTextOption.NoWrap)
            self.logDict[tabName] = contents
            contents.installEventFilter(self.filter)
            if tabName == 'Log':
                self.logCtrl = contents
        else:
            contents = QtGui.QWidget()

        self.contentsDict[tabName] = contents
        w.addTab(contents,tabName)
        return contents

    #@-node:ekr.20081004172422.649:createTab
    #@+node:ekr.20081004172422.651:cycleTabFocus (to do)
    def cycleTabFocus (self,event=None,stop_w = None):

        '''Cycle keyboard focus between the tabs in the log pane.'''

        c = self.c ; w = self.tabWidget

        i = w.currentIndex()
        i += 1
        if i >= w.count():
            i = 0

        tabName = w.tabText(i)
        w.setCurrentIndex(i)
        log = self.logDict.get(tabName)
        if log: self.logCtrl = log

    #@-node:ekr.20081004172422.651:cycleTabFocus (to do)
    #@+node:ekr.20081004172422.652:deleteTab
    def deleteTab (self,tabName,force=False):

        c = self.c ; w = self.tabWidget

        if tabName not in ('Log','Find','Spell'):
            for i in range(w.count()):
                if tabName == w.tabText(i):
                    w.removeTab(i)
                    break

        self.selectTab('Log')
        c.invalidateFocus()
        c.bodyWantsFocus()
    #@-node:ekr.20081004172422.652:deleteTab
    #@+node:ekr.20081004172422.653:hideTab
    def hideTab (self,tabName):

        self.selectTab('Log')
    #@-node:ekr.20081004172422.653:hideTab
    #@+node:ekr.20081004172422.656:numberOfVisibleTabs
    def numberOfVisibleTabs (self):

        return len([val for val in self.frameDict.values() if val != None])
    #@-node:ekr.20081004172422.656:numberOfVisibleTabs
    #@+node:ekr.20081004172422.658:selectTab & helper
    def selectTab (self,tabName,createText=True,wrap='none'):

        '''Create the tab if necessary and make it active.'''

        c = self.c ; w = self.tabWidget ; trace = False

        ok = self.selectHelper(tabName)
        if ok: return

        contents = self.createTab(tabName,createText,wrap)

        if createText and tabName not in ('Spell','Find',):
            # g.trace(tabName,contents,g.callers(4))
            self.logCtrl = contents

        self.selectHelper(tabName)

    #@+node:ekr.20081030092313.11:selectHelper
    def selectHelper (self,tabName):

        w = self.tabWidget

        for i in range(w.count()):
            if tabName == w.tabText(i):
                w.setCurrentIndex(i)
                return True
        else:
            return False
    #@-node:ekr.20081030092313.11:selectHelper
    #@-node:ekr.20081004172422.658:selectTab & helper
    #@-node:ekr.20081004172422.646:Tab (qtLog)
    #@+node:ekr.20081004172422.667:qtLog color tab stuff
    def createColorPicker (self,tabName):

        return

        # log = self

        #@    << define colors >>
        #@+node:ekr.20081004172422.668:<< define colors >>
        # colors = (
            # "gray60", "gray70", "gray80", "gray85", "gray90", "gray95",
            # "snow1", "snow2", "snow3", "snow4", "seashell1", "seashell2",
            # "seashell3", "seashell4", "AntiqueWhite1", "AntiqueWhite2", "AntiqueWhite3",
            # "AntiqueWhite4", "bisque1", "bisque2", "bisque3", "bisque4", "PeachPuff1",
            # "PeachPuff2", "PeachPuff3", "PeachPuff4", "NavajoWhite1", "NavajoWhite2",
            # "NavajoWhite3", "NavajoWhite4", "LemonChiffon1", "LemonChiffon2",
            # "LemonChiffon3", "LemonChiffon4", "cornsilk1", "cornsilk2", "cornsilk3",
            # "cornsilk4", "ivory1", "ivory2", "ivory3", "ivory4", "honeydew1", "honeydew2",
            # "honeydew3", "honeydew4", "LavenderBlush1", "LavenderBlush2",
            # "LavenderBlush3", "LavenderBlush4", "MistyRose1", "MistyRose2",
            # "MistyRose3", "MistyRose4", "azure1", "azure2", "azure3", "azure4",
            # "SlateBlue1", "SlateBlue2", "SlateBlue3", "SlateBlue4", "RoyalBlue1",
            # "RoyalBlue2", "RoyalBlue3", "RoyalBlue4", "blue1", "blue2", "blue3", "blue4",
            # "DodgerBlue1", "DodgerBlue2", "DodgerBlue3", "DodgerBlue4", "SteelBlue1",
            # "SteelBlue2", "SteelBlue3", "SteelBlue4", "DeepSkyBlue1", "DeepSkyBlue2",
            # "DeepSkyBlue3", "DeepSkyBlue4", "SkyBlue1", "SkyBlue2", "SkyBlue3",
            # "SkyBlue4", "LightSkyBlue1", "LightSkyBlue2", "LightSkyBlue3",
            # "LightSkyBlue4", "SlateGray1", "SlateGray2", "SlateGray3", "SlateGray4",
            # "LightSteelBlue1", "LightSteelBlue2", "LightSteelBlue3",
            # "LightSteelBlue4", "LightBlue1", "LightBlue2", "LightBlue3",
            # "LightBlue4", "LightCyan1", "LightCyan2", "LightCyan3", "LightCyan4",
            # "PaleTurquoise1", "PaleTurquoise2", "PaleTurquoise3", "PaleTurquoise4",
            # "CadetBlue1", "CadetBlue2", "CadetBlue3", "CadetBlue4", "turquoise1",
            # "turquoise2", "turquoise3", "turquoise4", "cyan1", "cyan2", "cyan3", "cyan4",
            # "DarkSlateGray1", "DarkSlateGray2", "DarkSlateGray3",
            # "DarkSlateGray4", "aquamarine1", "aquamarine2", "aquamarine3",
            # "aquamarine4", "DarkSeaGreen1", "DarkSeaGreen2", "DarkSeaGreen3",
            # "DarkSeaGreen4", "SeaGreen1", "SeaGreen2", "SeaGreen3", "SeaGreen4",
            # "PaleGreen1", "PaleGreen2", "PaleGreen3", "PaleGreen4", "SpringGreen1",
            # "SpringGreen2", "SpringGreen3", "SpringGreen4", "green1", "green2",
            # "green3", "green4", "chartreuse1", "chartreuse2", "chartreuse3",
            # "chartreuse4", "OliveDrab1", "OliveDrab2", "OliveDrab3", "OliveDrab4",
            # "DarkOliveGreen1", "DarkOliveGreen2", "DarkOliveGreen3",
            # "DarkOliveGreen4", "khaki1", "khaki2", "khaki3", "khaki4",
            # "LightGoldenrod1", "LightGoldenrod2", "LightGoldenrod3",
            # "LightGoldenrod4", "LightYellow1", "LightYellow2", "LightYellow3",
            # "LightYellow4", "yellow1", "yellow2", "yellow3", "yellow4", "gold1", "gold2",
            # "gold3", "gold4", "goldenrod1", "goldenrod2", "goldenrod3", "goldenrod4",
            # "DarkGoldenrod1", "DarkGoldenrod2", "DarkGoldenrod3", "DarkGoldenrod4",
            # "RosyBrown1", "RosyBrown2", "RosyBrown3", "RosyBrown4", "IndianRed1",
            # "IndianRed2", "IndianRed3", "IndianRed4", "sienna1", "sienna2", "sienna3",
            # "sienna4", "burlywood1", "burlywood2", "burlywood3", "burlywood4", "wheat1",
            # "wheat2", "wheat3", "wheat4", "tan1", "tan2", "tan3", "tan4", "chocolate1",
            # "chocolate2", "chocolate3", "chocolate4", "firebrick1", "firebrick2",
            # "firebrick3", "firebrick4", "brown1", "brown2", "brown3", "brown4", "salmon1",
            # "salmon2", "salmon3", "salmon4", "LightSalmon1", "LightSalmon2",
            # "LightSalmon3", "LightSalmon4", "orange1", "orange2", "orange3", "orange4",
            # "DarkOrange1", "DarkOrange2", "DarkOrange3", "DarkOrange4", "coral1",
            # "coral2", "coral3", "coral4", "tomato1", "tomato2", "tomato3", "tomato4",
            # "OrangeRed1", "OrangeRed2", "OrangeRed3", "OrangeRed4", "red1", "red2", "red3",
            # "red4", "DeepPink1", "DeepPink2", "DeepPink3", "DeepPink4", "HotPink1",
            # "HotPink2", "HotPink3", "HotPink4", "pink1", "pink2", "pink3", "pink4",
            # "LightPink1", "LightPink2", "LightPink3", "LightPink4", "PaleVioletRed1",
            # "PaleVioletRed2", "PaleVioletRed3", "PaleVioletRed4", "maroon1",
            # "maroon2", "maroon3", "maroon4", "VioletRed1", "VioletRed2", "VioletRed3",
            # "VioletRed4", "magenta1", "magenta2", "magenta3", "magenta4", "orchid1",
            # "orchid2", "orchid3", "orchid4", "plum1", "plum2", "plum3", "plum4",
            # "MediumOrchid1", "MediumOrchid2", "MediumOrchid3", "MediumOrchid4",
            # "DarkOrchid1", "DarkOrchid2", "DarkOrchid3", "DarkOrchid4", "purple1",
            # "purple2", "purple3", "purple4", "MediumPurple1", "MediumPurple2",
            # "MediumPurple3", "MediumPurple4", "thistle1", "thistle2", "thistle3",
            # "thistle4" )
        #@-node:ekr.20081004172422.668:<< define colors >>
        #@nl

        # parent = log.frameDict.get(tabName)
        # w = log.textDict.get(tabName)
        # w.pack_forget()

        # colors = list(colors)
        # bg = parent.cget('background')

        # outer = qt.Frame(parent,background=bg)
        # outer.pack(side='top',fill='both',expand=1,pady=10)

        # f = qt.Frame(outer)
        # f.pack(side='top',expand=0,fill='x')
        # f1 = qt.Frame(f) ; f1.pack(side='top',expand=0,fill='x')
        # f2 = qt.Frame(f) ; f2.pack(side='top',expand=1,fill='x')
        # f3 = qt.Frame(f) ; f3.pack(side='top',expand=1,fill='x')

        # label = g.app.gui.plainTextWidget(f1,height=1,width=20)
        # label.insert('1.0','Color name or value...')
        # label.pack(side='left',pady=6)

        #@    << create optionMenu and callback >>
        #@+node:ekr.20081004172422.669:<< create optionMenu and callback >>
        # colorBox = Pmw.ComboBox(f2,scrolledlist_items=colors)
        # colorBox.pack(side='left',pady=4)

        # def colorCallback (newName): 
            # label.delete('1.0','end')
            # label.insert('1.0',newName)
            # try:
                # for theFrame in (parent,outer,f,f1,f2,f3):
                    # theFrame.configure(background=newName)
            # except: pass # Ignore invalid names.

        # colorBox.configure(selectioncommand=colorCallback)
        #@-node:ekr.20081004172422.669:<< create optionMenu and callback >>
        #@nl
        #@    << create picker button and callback >>
        #@+node:ekr.20081004172422.670:<< create picker button and callback >>
        # def pickerCallback ():
            # return

            # rgb,val = tkColorChooser.askcolor(parent=parent,initialcolor=f.cget('background'))
            # if rgb or val:
                # # label.configure(text=val)
                # label.delete('1.0','end')
                # label.insert('1.0',val)
                # for theFrame in (parent,outer,f,f1,f2,f3):
                    # theFrame.configure(background=val)

        # b = qt.Button(f3,text="Color Picker...",
            # command=pickerCallback,background=bg)
        # b.pack(side='left',pady=4)
        #@-node:ekr.20081004172422.670:<< create picker button and callback >>
        #@nl
    #@-node:ekr.20081004172422.667:qtLog color tab stuff
    #@+node:ekr.20081004172422.671:qtLog font tab stuff
    #@+node:ekr.20081004172422.672:createFontPicker
    def createFontPicker (self,tabName):

        return

        # log = self ; c = self.c
        # parent = log.frameDict.get(tabName)
        # w = log.textDict.get(tabName)
        # w.pack_forget()

        # bg = parent.cget('background')
        # font = self.getFont()

        #@    << create the frames >>
        #@+node:ekr.20081004172422.673:<< create the frames >>
        # f = qt.Frame(parent,background=bg) ; f.pack (side='top',expand=0,fill='both')
        # f1 = qt.Frame(f,background=bg)     ; f1.pack(side='top',expand=1,fill='x')
        # f2 = qt.Frame(f,background=bg)     ; f2.pack(side='top',expand=1,fill='x')
        # f3 = qt.Frame(f,background=bg)     ; f3.pack(side='top',expand=1,fill='x')
        # f4 = qt.Frame(f,background=bg)     ; f4.pack(side='top',expand=1,fill='x')
        #@-node:ekr.20081004172422.673:<< create the frames >>
        #@nl
        #@    << create the family combo box >>
        #@+node:ekr.20081004172422.674:<< create the family combo box >>
        # names = tkFont.families()
        # names = list(names)
        # names.sort()
        # names.insert(0,'<None>')

        # self.familyBox = familyBox = Pmw.ComboBox(f1,
            # labelpos="we",label_text='Family:',label_width=10,
            # label_background=bg,
            # arrowbutton_background=bg,
            # scrolledlist_items=names)

        # familyBox.selectitem(0)
        # familyBox.pack(side="left",padx=2,pady=2)
        #@-node:ekr.20081004172422.674:<< create the family combo box >>
        #@nl
        #@    << create the size entry >>
        #@+node:ekr.20081004172422.675:<< create the size entry >>
        # qt.Label(f2,text="Size:",width=10,background=bg).pack(side="left")

        # sizeEntry = qt.Entry(f2,width=4)
        # sizeEntry.insert(0,'12')
        # sizeEntry.pack(side="left",padx=2,pady=2)
        #@-node:ekr.20081004172422.675:<< create the size entry >>
        #@nl
        #@    << create the weight combo box >>
        #@+node:ekr.20081004172422.676:<< create the weight combo box >>
        # weightBox = Pmw.ComboBox(f3,
            # labelpos="we",label_text="Weight:",label_width=10,
            # label_background=bg,
            # arrowbutton_background=bg,
            # scrolledlist_items=['normal','bold'])

        # weightBox.selectitem(0)
        # weightBox.pack(side="left",padx=2,pady=2)
        #@-node:ekr.20081004172422.676:<< create the weight combo box >>
        #@nl
        #@    << create the slant combo box >>
        #@+node:ekr.20081004172422.677:<< create the slant combo box>>
        # slantBox = Pmw.ComboBox(f4,
            # labelpos="we",label_text="Slant:",label_width=10,
            # label_background=bg,
            # arrowbutton_background=bg,
            # scrolledlist_items=['roman','italic'])

        # slantBox.selectitem(0)
        # slantBox.pack(side="left",padx=2,pady=2)
        #@-node:ekr.20081004172422.677:<< create the slant combo box>>
        #@nl
        #@    << create the sample text widget >>
        #@+node:ekr.20081004172422.678:<< create the sample text widget >>
        # self.sampleWidget = sample = g.app.gui.plainTextWidget(f,height=20,width=80,font=font)
        # sample.pack(side='left')

        # s = 'The quick brown fox\njumped over the lazy dog.\n0123456789'
        # sample.insert(0,s)
        #@-node:ekr.20081004172422.678:<< create the sample text widget >>
        #@nl
        #@    << create and bind the callbacks >>
        #@+node:ekr.20081004172422.679:<< create and bind the callbacks >>
        # def fontCallback(event=None):
            # self.setFont(familyBox,sizeEntry,slantBox,weightBox,sample)

        # for w in (familyBox,slantBox,weightBox):
            # w.configure(selectioncommand=fontCallback)

        # c.bind(sizeEntry,'<Return>',fontCallback)
        #@-node:ekr.20081004172422.679:<< create and bind the callbacks >>
        #@nl

        # self.createBindings()
    #@-node:ekr.20081004172422.672:createFontPicker
    #@+node:ekr.20081004172422.680:createBindings (fontPicker)
    def createBindings (self):

        c = self.c ; k = c.k

        # table = (
            # ('<Button-1>',  k.masterClickHandler),
            # ('<Double-1>',  k.masterClickHandler),
            # ('<Button-3>',  k.masterClickHandler),
            # ('<Double-3>',  k.masterClickHandler),
            # ('<Key>',       k.masterKeyHandler),
            # ("<Escape>",    self.hideFontTab),
        # )

        # w = self.sampleWidget
        # for event, callback in table:
            # c.bind(w,event,callback)

        # k.completeAllBindingsForWidget(w)
    #@-node:ekr.20081004172422.680:createBindings (fontPicker)
    #@+node:ekr.20081004172422.681:getFont
    def getFont(self,family=None,size=12,slant='roman',weight='normal'):

        return g.app.config.defaultFont

        # try:
            # return tkFont.Font(family=family,size=size,slant=slant,weight=weight)
        # except Exception:
            # g.es("exception setting font")
            # g.es('','family,size,slant,weight:','',family,'',size,'',slant,'',weight)
            # # g.es_exception() # This just confuses people.
            # return g.app.config.defaultFont
    #@-node:ekr.20081004172422.681:getFont
    #@+node:ekr.20081004172422.682:setFont
    def setFont(self,familyBox,sizeEntry,slantBox,weightBox,label):

        pass

        # d = {}
        # for box,key in (
            # (familyBox, 'family'),
            # (None,      'size'),
            # (slantBox,  'slant'),
            # (weightBox, 'weight'),
        # ):
            # if box: val = box.get()
            # else:
                # val = sizeEntry.get().strip() or ''
                # try: int(val)
                # except ValueError: val = None
            # if val and val.lower() not in ('none','<none>',):
                # d[key] = val

        # family=d.get('family',None)
        # size=d.get('size',12)
        # weight=d.get('weight','normal')
        # slant=d.get('slant','roman')
        # font = self.getFont(family,size,slant,weight)
        # label.configure(font=font)
    #@-node:ekr.20081004172422.682:setFont
    #@+node:ekr.20081004172422.683:hideFontTab
    def hideFontTab (self,event=None):

        c = self.c
        c.frame.log.selectTab('Log')
        c.bodyWantsFocus()
    #@-node:ekr.20081004172422.683:hideFontTab
    #@-node:ekr.20081004172422.671:qtLog font tab stuff
    #@-others
#@-node:ekr.20081004172422.622:class leoQtLog
#@+node:ekr.20081004172422.856:class leoQtMenu (leoMenu)
class leoQtMenu (leoMenu.leoMenu):

    #@    @+others
    #@+node:ekr.20081004172422.858:leoQtMenu.__init__
    def __init__ (self,frame):

        assert frame
        assert frame.c

        # Init the base class.
        leoMenu.leoMenu.__init__(self,frame)

        # g.trace('leoQtMenu',g.callers(4))

        self.frame = frame
        self.c = c = frame.c
        self.leo_label = '<no leo_label>'

        self.menuBar = c.frame.top.menuBar()
        assert self.menuBar

        # Inject this dict into the commander.
        if not hasattr(c,'menuAccels'):
            setattr(c,'menuAccels',{})

        if 0:
            self.font = c.config.getFontFromParams(
                'menu_text_font_family', 'menu_text_font_size',
                'menu_text_font_slant',  'menu_text_font_weight',
                c.config.defaultMenuFontSize)
    #@-node:ekr.20081004172422.858:leoQtMenu.__init__
    #@+node:ekr.20081004172422.859:Activate menu commands (to do)
    #@+node:ekr.20081004172422.860:qtMenu.activateMenu
    def activateMenu (self,menuName):

        c = self.c ;  top = c.frame.top
        # topx,topy = top.winfo_rootx(),top.winfo_rooty()
        # menu = c.frame.menu.getMenu(menuName)

        # if menu:
            # d = self.computeMenuPositions()
            # x = d.get(menuName)
            # if x is None:
                # x = 0 ; g.trace('oops, no menu offset: %s' % menuName)

            # menu.tk_popup(topx+d.get(menuName,0),topy) # Fix by caugm.  Thanks!
        # else:
            # g.trace('oops, no menu: %s' % menuName)
    #@-node:ekr.20081004172422.860:qtMenu.activateMenu
    #@+node:ekr.20081004172422.861:qtMenu.computeMenuPositions
    def computeMenuPositions (self):

        # A hack.  It would be better to set this when creating the menus.
        menus = ('File','Edit','Outline','Plugins','Cmds','Window','Help')

        # Compute the *approximate* x offsets of each menu.
        d = {}
        n = 0
        # for z in menus:
            # menu = self.getMenu(z)
            # fontName = menu.cget('font')
            # font = tkFont.Font(font=fontName)
            # # g.pr('%8s' % (z),menu.winfo_reqwidth(),menu.master,menu.winfo_x())
            # d [z] = n
            # # A total hack: sorta works on windows.
            # n += font.measure(z+' '*4)+1

        return d
    #@-node:ekr.20081004172422.861:qtMenu.computeMenuPositions
    #@-node:ekr.20081004172422.859:Activate menu commands (to do)
    #@+node:ekr.20081004172422.862:Tkinter menu bindings
    # See the Tk docs for what these routines are to do
    #@+node:ekr.20081004172422.863:Methods with Tk spellings
    #@+node:ekr.20081004172422.864:add_cascade
    def add_cascade (self,parent,label,menu,underline):

        """Wrapper for the Tkinter add_cascade menu method.

        Adds a submenu to the parent menu, or the menubar."""

        c = self.c ; leoFrame = c.frame
        n = underline
        if -1 < n < len(label):
            label = label[:n] + '&' + label[n:]

        menu.setTitle(label)
        menu.leo_label = label

        if parent:
            parent.addMenu(menu)
        else:
            self.menuBar.addMenu(menu)

        return menu
    #@-node:ekr.20081004172422.864:add_cascade
    #@+node:ekr.20081004172422.865:add_command
    def add_command (self,**keys):

        """Wrapper for the Tkinter add_command menu method."""

        c = self.c
        accel = keys.get('accelerator') or ''
        command = keys.get('command')
        label = keys.get('label')
        n = keys.get('underline')
        menu = keys.get('menu') or self
        if not label: return

        if -1 < n < len(label):
            label = label[:n] + '&' + label[n:]
        if accel:
            label = '%s\t%s' % (label,accel)

        action = menu.addAction(label)

        if command:
            def add_command_callback(label=label,command=command):
                return command()

            QtCore.QObject.connect(action,
                QtCore.SIGNAL("triggered()"),add_command_callback)
    #@-node:ekr.20081004172422.865:add_command
    #@+node:ekr.20081004172422.866:add_separator
    def add_separator(self,menu):

        """Wrapper for the Tkinter add_separator menu method."""

        if menu:
            menu.addSeparator()
    #@-node:ekr.20081004172422.866:add_separator
    #@+node:ekr.20081004172422.868:delete
    def delete (self,menu,realItemName):

        """Wrapper for the Tkinter delete menu method."""

        # if menu:
            # return menu.delete(realItemName)
    #@-node:ekr.20081004172422.868:delete
    #@+node:ekr.20081004172422.869:delete_range
    def delete_range (self,menu,n1,n2):

        """Wrapper for the Tkinter delete menu method."""

        # if menu:
            # return menu.delete(n1,n2)
    #@-node:ekr.20081004172422.869:delete_range
    #@+node:ekr.20081004172422.870:destroy
    def destroy (self,menu):

        """Wrapper for the Tkinter destroy menu method."""

        # if menu:
            # return menu.destroy()
    #@-node:ekr.20081004172422.870:destroy
    #@+node:ekr.20081004172422.871:insert
    def insert (self,menuName,position,label,command,underline=None):

        # g.trace(menuName,position,label,command,underline)

        menu = self.getMenu(menuName)
        if menu and label:
            n = underline
            if -1 > n > len(label):
                label = label[:n] + '&' + label[n:]
            action = menu.addAction(label)
            if command:
                def insert_callback(label=label,command=command):
                    command()
                QtCore.QObject.connect(
                    action,QtCore.SIGNAL("triggered()"),insert_callback)
    #@-node:ekr.20081004172422.871:insert
    #@+node:ekr.20081004172422.872:insert_cascade
    def insert_cascade (self,parent,index,label,menu,underline):

        """Wrapper for the Tkinter insert_cascade menu method."""

        g.trace(label,menu)

        menu.setTitle(label)
        menu.leo_label = label

        if parent:
            parent.addMenu(menu)
        else:
            self.menuBar.addMenu(menu)

        return menu
    #@-node:ekr.20081004172422.872:insert_cascade
    #@+node:ekr.20081004172422.873:new_menu
    def new_menu(self,parent,tearoff=False):

        """Wrapper for the Tkinter new_menu menu method."""

        c = self.c ; leoFrame = self.frame

        # g.trace(parent)

        # Parent can be None, in which case it will be added to the menuBar.
        menu = qtMenuWrapper(c,leoFrame,parent)

        return menu
    #@nonl
    #@-node:ekr.20081004172422.873:new_menu
    #@-node:ekr.20081004172422.863:Methods with Tk spellings
    #@+node:ekr.20081004172422.874:Methods with other spellings (Qtmenu)
    #@+node:ekr.20081004172422.875:clearAccel
    def clearAccel(self,menu,name):

        pass

        # if not menu:
            # return

        # realName = self.getRealMenuName(name)
        # realName = realName.replace("&","")

        # menu.entryconfig(realName,accelerator='')
    #@-node:ekr.20081004172422.875:clearAccel
    #@+node:ekr.20081004172422.876:createMenuBar (Qtmenu)
    def createMenuBar(self,frame):

        '''Create all top-level menus.
        The menuBar itself has already been created.'''

        self.createMenusFromTables()
    #@-node:ekr.20081004172422.876:createMenuBar (Qtmenu)
    #@+node:ekr.20081004172422.877:createOpenWithMenu
    def createOpenWithMenu(self,parent,label,index,amp_index):

        '''Create a submenu.'''

        c = self.c ; leoFrame = c.frame

        g.trace()

        # menu = qtMenuWrapper(c,leoFrame,parent)
        # self.insert_cascade(parent,index,label,menu,underline=amp_index)

        # menu = Tk.Menu(parent,tearoff=0)
        # if menu:
            # parent.insert_cascade(index,label=label,menu=menu,underline=amp_index)
        # return menu
    #@-node:ekr.20081004172422.877:createOpenWithMenu
    #@+node:ekr.20081004172422.878:disableMenu
    def disableMenu (self,menu,name):

        if not menu:
            return

        # try:
            # menu.entryconfig(name,state="disabled")
        # except: 
            # try:
                # realName = self.getRealMenuName(name)
                # realName = realName.replace("&","")
                # menu.entryconfig(realName,state="disabled")
            # except:
                # g.pr("disableMenu menu,name:",menu,name)
                # g.es_exception()
    #@-node:ekr.20081004172422.878:disableMenu
    #@+node:ekr.20081004172422.879:enableMenu
    # Fail gracefully if the item name does not exist.

    def enableMenu (self,menu,name,val):

        if not menu:
            return

        # state = g.choose(val,"normal","disabled")
        # try:
            # menu.entryconfig(name,state=state)
        # except:
            # try:
                # realName = self.getRealMenuName(name)
                # realName = realName.replace("&","")
                # menu.entryconfig(realName,state=state)
            # except:
                # g.pr("enableMenu menu,name,val:",menu,name,val)
                # g.es_exception()
    #@nonl
    #@-node:ekr.20081004172422.879:enableMenu
    #@+node:ekr.20081004172422.880:getMenuLabel
    def getMenuLabel (self,menu,name):

        '''Return the index of the menu item whose name (or offset) is given.
        Return None if there is no such menu item.'''

        g.trace('menu',menu,'name',name)

        actions = menu.actions()
        for action in actions:
            g.trace(action.label())

        # try:
            # index = menu.index(name)
        # except:
            # index = None

        # return index
    #@-node:ekr.20081004172422.880:getMenuLabel
    #@+node:ekr.20081004172422.881:setMenuLabel
    def setMenuLabel (self,menu,name,label,underline=-1):

        def munge(s):
            s = g.toUnicode(s,'utf-8')
            return s.replace('&','')

        # menu is a qtMenuWrapper.

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
    #@-node:ekr.20081004172422.881:setMenuLabel
    #@-node:ekr.20081004172422.874:Methods with other spellings (Qtmenu)
    #@-node:ekr.20081004172422.862:Tkinter menu bindings
    #@+node:ekr.20081004172422.882:getMacHelpMenu
    def getMacHelpMenu (self,table):

        return None

        # defaultTable = [
                # # &: a,b,c,d,e,f,h,l,m,n,o,p,r,s,t,u
                # ('&About Leo...',           'about-leo'),
                # ('Online &Home Page',       'open-online-home'),
                # '*open-online-&tutorial',
                # '*open-&users-guide',
                # '-',
                # ('Open Leo&Docs.leo',       'open-leoDocs-leo'),
                # ('Open Leo&Plugins.leo',    'open-leoPlugins-leo'),
                # ('Open Leo&Settings.leo',   'open-leoSettings-leo'),
                # ('Open &myLeoSettings.leo', 'open-myLeoSettings-leo'),
                # ('Open scr&ipts.leo',       'open-scripts-leo'),
                # '-',
                # '*he&lp-for-minibuffer',
                # '*help-for-&command',
                # '-',
                # '*&apropos-autocompletion',
                # '*apropos-&bindings',
                # '*apropos-&debugging-commands',
                # '*apropos-&find-commands',
                # '-',
                # '*pri&nt-bindings',
                # '*print-c&ommands',
            # ]

        # try:
            # topMenu = self.getMenu('top')
            # # Use the name argument to create the special Macintosh Help menu.
            # helpMenu = Tk.Menu(topMenu,name='help',tearoff=0)
            # self.add_cascade(topMenu,label='Help',menu=helpMenu,underline=0)
            # self.createMenuEntries(helpMenu,table or defaultTable)
            # return helpMenu

        # except Exception:
            # g.trace('Can not get MacOS Help menu')
            # g.es_exception()
            # return None
    #@-node:ekr.20081004172422.882:getMacHelpMenu
    #@-others
#@-node:ekr.20081004172422.856:class leoQtMenu (leoMenu)
#@+node:ekr.20081007015817.35:class leoQtSpellTab
class leoQtSpellTab:

    #@    @+others
    #@+node:ekr.20081007015817.36:leoQtSpellTab.__init__
    def __init__ (self,c,handler,tabName):

        self.c = c
        self.handler = handler
        self.tabName = tabName

        self.createFrame()
        self.createBindings()

        ###self.fillbox([])
    #@-node:ekr.20081007015817.36:leoQtSpellTab.__init__
    #@+node:ekr.20081007015817.37:createBindings TO DO
    def createBindings (self):

        return

        # c = self.c ; k = c.k
        # widgets = (self.listBox, self.outerFrame)

        # for w in widgets:

            # # Bind shortcuts for the following commands...
            # for commandName,func in (
                # ('full-command',            k.fullCommand),
                # ('hide-spell-tab',          self.handler.hide),
                # ('spell-add',               self.handler.add),
                # ('spell-find',              self.handler.find),
                # ('spell-ignore',            self.handler.ignore),
                # ('spell-change-then-find',  self.handler.changeThenFind),
            # ):
                # junk, bunchList = c.config.getShortcut(commandName)
                # for bunch in bunchList:
                    # accel = bunch.val
                    # shortcut = k.shortcutFromSetting(accel)
                    # if shortcut:
                        # # g.trace(shortcut,commandName)
                        # w.bind(shortcut,func)

        # self.listBox.bind("<Double-1>",self.onChangeThenFindButton)
        # self.listBox.bind("<Button-1>",self.onSelectListBox)
        # self.listBox.bind("<Map>",self.onMap)
    #@nonl
    #@-node:ekr.20081007015817.37:createBindings TO DO
    #@+node:ekr.20081007015817.38:createFrame (to be done in Qt designer)
    def createFrame (self):

        c = self.c ; log = c.frame.log ; tabName = self.tabName

        # parentFrame = log.frameDict.get(tabName)
        # w = log.textDict.get(tabName)
        # w.pack_forget()

        # # Set the common background color.
        # bg = c.config.getColor('log_pane_Spell_tab_background_color') or 'LightSteelBlue2'

        #@    << Create the outer frames >>
        #@+node:ekr.20081007015817.39:<< Create the outer frames >>
        # self.outerScrolledFrame = Pmw.ScrolledFrame(
            # parentFrame,usehullsize = 1)

        # self.outerFrame = outer = self.outerScrolledFrame.component('frame')
        # self.outerFrame.configure(background=bg)

        # for z in ('borderframe','clipper','frame','hull'):
            # self.outerScrolledFrame.component(z).configure(
                # relief='flat',background=bg)
        #@-node:ekr.20081007015817.39:<< Create the outer frames >>
        #@nl
        #@    << Create the text and suggestion panes >>
        #@+node:ekr.20081007015817.40:<< Create the text and suggestion panes >>
        # f2 = Tk.Frame(outer,bg=bg)
        # f2.pack(side='top',expand=0,fill='x')

        # self.wordLabel = Tk.Label(f2,text="Suggestions for:")
        # self.wordLabel.pack(side='left')
        # self.wordLabel.configure(font=('verdana',10,'bold'))

        # fpane = Tk.Frame(outer,bg=bg,bd=2)
        # fpane.pack(side='top',expand=1,fill='both')

        # self.listBox = Tk.Listbox(fpane,height=6,width=10,selectmode="single")
        # self.listBox.pack(side='left',expand=1,fill='both')
        # self.listBox.configure(font=('verdana',11,'normal'))

        # listBoxBar = Tk.Scrollbar(fpane,name='listBoxBar')

        # bar, txt = listBoxBar, self.listBox
        # txt ['yscrollcommand'] = bar.set
        # bar ['command'] = txt.yview
        # bar.pack(side='right',fill='y')
        #@-node:ekr.20081007015817.40:<< Create the text and suggestion panes >>
        #@nl
        #@    << Create the spelling buttons >>
        #@+node:ekr.20081007015817.41:<< Create the spelling buttons >>
        # # Create the alignment panes
        # buttons1 = Tk.Frame(outer,bd=1,bg=bg)
        # buttons2 = Tk.Frame(outer,bd=1,bg=bg)
        # buttons3 = Tk.Frame(outer,bd=1,bg=bg)
        # for w in (buttons1,buttons2,buttons3):
            # w.pack(side='top',expand=0,fill='x')

        # buttonList = [] ; font = ('verdana',9,'normal') ; width = 12
        # for frame, text, command in (
            # (buttons1,"Find",self.onFindButton),
            # (buttons1,"Add",self.onAddButton),
            # (buttons2,"Change",self.onChangeButton),
            # (buttons2,"Change, Find",self.onChangeThenFindButton),
            # (buttons3,"Ignore",self.onIgnoreButton),
            # (buttons3,"Hide",self.onHideButton),
        # ):
            # b = Tk.Button(frame,font=font,width=width,text=text,command=command)
            # b.pack(side='left',expand=0,fill='none')
            # buttonList.append(b)

        # # Used to enable or disable buttons.
        # (self.findButton,self.addButton,
         # self.changeButton, self.changeFindButton,
         # self.ignoreButton, self.hideButton) = buttonList
        #@-node:ekr.20081007015817.41:<< Create the spelling buttons >>
        #@nl

        # Pack last so buttons don't get squished.
        # self.outerScrolledFrame.pack(expand=1,fill='both',padx=2,pady=2)
    #@-node:ekr.20081007015817.38:createFrame (to be done in Qt designer)
    #@+node:ekr.20081007015817.42:Event handlers
    #@+node:ekr.20081007015817.43:onAddButton
    def onAddButton(self):
        """Handle a click in the Add button in the Check Spelling dialog."""

        self.handler.add()
    #@-node:ekr.20081007015817.43:onAddButton
    #@+node:ekr.20081007015817.44:onChangeButton & onChangeThenFindButton
    def onChangeButton(self,event=None):

        """Handle a click in the Change button in the Spell tab."""

        self.handler.change()
        self.updateButtons()


    def onChangeThenFindButton(self,event=None):

        """Handle a click in the "Change, Find" button in the Spell tab."""

        if self.handler.change():
            self.handler.find()
        self.updateButtons()
    #@-node:ekr.20081007015817.44:onChangeButton & onChangeThenFindButton
    #@+node:ekr.20081007015817.45:onFindButton
    def onFindButton(self):

        """Handle a click in the Find button in the Spell tab."""

        c = self.c
        self.handler.find()
        self.updateButtons()
        c.invalidateFocus()
        c.bodyWantsFocusNow()
    #@-node:ekr.20081007015817.45:onFindButton
    #@+node:ekr.20081007015817.46:onHideButton
    def onHideButton(self):

        """Handle a click in the Hide button in the Spell tab."""

        self.handler.hide()
    #@-node:ekr.20081007015817.46:onHideButton
    #@+node:ekr.20081007015817.47:onIgnoreButton
    def onIgnoreButton(self,event=None):

        """Handle a click in the Ignore button in the Check Spelling dialog."""

        self.handler.ignore()
    #@-node:ekr.20081007015817.47:onIgnoreButton
    #@+node:ekr.20081007015817.48:onMap
    def onMap (self, event=None):
        """Respond to a Tk <Map> event."""

        self.update(show= False, fill= False)
    #@-node:ekr.20081007015817.48:onMap
    #@+node:ekr.20081007015817.49:onSelectListBox
    def onSelectListBox(self, event=None):
        """Respond to a click in the selection listBox."""

        c = self.c
        self.updateButtons()
        c.bodyWantsFocus()
    #@-node:ekr.20081007015817.49:onSelectListBox
    #@-node:ekr.20081007015817.42:Event handlers
    #@+node:ekr.20081007015817.50:Helpers
    #@+node:ekr.20081007015817.51:bringToFront
    def bringToFront (self):

        self.c.frame.log.selectTab('Spell')
    #@-node:ekr.20081007015817.51:bringToFront
    #@+node:ekr.20081007015817.52:fillbox
    def fillbox(self, alts, word=None):
        """Update the suggestions listBox in the Check Spelling dialog."""

        # self.suggestions = alts

        # if not word:
            # word = ""

        # self.wordLabel.configure(text= "Suggestions for: " + word)
        # self.listBox.delete(0, "end")

        # for i in range(len(self.suggestions)):
            # self.listBox.insert(i, self.suggestions[i])

        # # This doesn't show up because we don't have focus.
        # if len(self.suggestions):
            # self.listBox.select_set(1)
    #@-node:ekr.20081007015817.52:fillbox
    #@+node:ekr.20081007015817.53:getSuggestion
    def getSuggestion(self):
        """Return the selected suggestion from the listBox."""

        # # Work around an old Python bug.  Convert strings to ints.
        # items = self.listBox.curselection()
        # try:
            # items = map(int, items)
        # except ValueError: pass

        # if items:
            # n = items[0]
            # suggestion = self.suggestions[n]
            # return suggestion
        # else:
            # return None
    #@-node:ekr.20081007015817.53:getSuggestion
    #@+node:ekr.20081007015817.54:update
    def update(self,show=True,fill=False):

        """Update the Spell Check dialog."""

        c = self.c

        if fill:
            self.fillbox([])

        self.updateButtons()

        if show:
            self.bringToFront()
            c.bodyWantsFocus()
    #@-node:ekr.20081007015817.54:update
    #@+node:ekr.20081007015817.55:updateButtons (spellTab)
    def updateButtons (self):

        """Enable or disable buttons in the Check Spelling dialog."""

        c = self.c ; w = c.frame.body.bodyCtrl

        # start, end = w.getSelectionRange()
        # state = g.choose(self.suggestions and start,"normal","disabled")

        # self.changeButton.configure(state=state)
        # self.changeFindButton.configure(state=state)

        # # state = g.choose(self.c.undoer.canRedo(),"normal","disabled")
        # # self.redoButton.configure(state=state)
        # # state = g.choose(self.c.undoer.canUndo(),"normal","disabled")
        # # self.undoButton.configure(state=state)

        # self.addButton.configure(state='normal')
        # self.ignoreButton.configure(state='normal')
    #@-node:ekr.20081007015817.55:updateButtons (spellTab)
    #@-node:ekr.20081007015817.50:Helpers
    #@-others
#@-node:ekr.20081007015817.35:class leoQtSpellTab
#@+node:ekr.20081004172422.732:class leoQtTree
class leoQtTree (leoFrame.leoTree):

    """Leo qt tree class."""

    callbacksInjected = False # A class var.

    #@    @+others
    #@+node:ekr.20081004172422.737: Birth... (qt Tree)
    #@+node:ekr.20081004172422.738:__init__ (qtTree)
    def __init__(self,c,frame):

        # g.trace('*****qtTree')

        # Init the base class.
        leoFrame.leoTree.__init__(self,frame)

        # Components.
        self.c = c
        self.canvas = self # An official ivar used by Leo's core.
        self.treeWidget = w = frame.top.ui.treeWidget # An internal ivar.
        self.treeWidget.setIconSize(QtCore.QSize(20,11))

        # Status ivars.
        self.dragging = False
        self._editWidgetPosition = None
        self._editWidget = None
        self._editWidgetWrapper = None
        self.expanding = False
        self.fullDrawing = False
        self.generation = 0
        self.prev_p = None
        self.redrawing = False
        self.redrawCount = 0 # Count for debugging.
        self.revertHeadline = None # Previous headline text for abortEditLabel.
        self.selecting = False

        # Debugging.
        self.nodeDrawCount = 0

        # Drawing ivars.
        self.itemsDict = {} # keys are items, values are positions
        self.parentsDict = {} 
        self.tnodeDict = {} # keys are tnodes, values are lists of (p,it)
        self.vnodeDict = {} # keys are vnodes, values are lists of (p,it)

        self.setConfigIvars()
        self.setEditPosition(None) # Set positions returned by leoTree.editPosition()
    #@-node:ekr.20081004172422.738:__init__ (qtTree)
    #@+node:ekr.20081005065934.10:qtTree.initAfterLoad
    def initAfterLoad (self):

        c = self.c ; frame = c.frame
        w = c.frame.top ; tw = self.treeWidget

        if not leoQtTree.callbacksInjected:
            leoQtTree.callbacksInjected = True
            self.injectCallbacks() # A base class method.

        w.connect(self.treeWidget,QtCore.SIGNAL(
            "itemSelectionChanged()"), self.onTreeSelect)

        w.connect(self.treeWidget,QtCore.SIGNAL(
            "itemChanged(QTreeWidgetItem*, int)"),self.sig_itemChanged)

        w.connect(self.treeWidget,QtCore.SIGNAL(
            "itemCollapsed(QTreeWidgetItem*)"),self.sig_itemCollapsed)

        w.connect(self.treeWidget,QtCore.SIGNAL(
            "itemExpanded(QTreeWidgetItem*)"),self.sig_itemExpanded)

        self.ev_filter = leoQtEventFilter(c,w=self,tag='tree')
        tw.installEventFilter(self.ev_filter)

        c.setChanged(False)
    #@-node:ekr.20081005065934.10:qtTree.initAfterLoad
    #@+node:ekr.20081004172422.742:qtTree.setBindings & helper
    def setBindings (self):

        '''Create master bindings for all headlines.'''

        tree = self ; k = self.c.k


        # # g.trace('self',self,'canvas',self.canvas)

        # tree.setBindingsHelper()

        # tree.setCanvasBindings(self.canvas)

        # k.completeAllBindingsForWidget(self.canvas)

        # k.completeAllBindingsForWidget(self.bindingWidget)

    #@+node:ekr.20081004172422.743:qtTree.setBindingsHelper
    def setBindingsHelper (self):

        tree = self ; c = tree.c ; k = c.k

        # self.bindingWidget = w = g.app.gui.plainTextWidget(
            # self.canvas,name='bindingWidget')

        # c.bind(w,'<Key>',k.masterKeyHandler)

        # table = [
            # ('<Button-1>',       k.masterClickHandler,          tree.onHeadlineClick),
            # ('<Button-3>',       k.masterClick3Handler,         tree.onHeadlineRightClick),
            # ('<Double-Button-1>',k.masterDoubleClickHandler,    tree.onHeadlineClick),
            # ('<Double-Button-3>',k.masterDoubleClick3Handler,   tree.onHeadlineRightClick),
        # ]

        # for a,handler,func in table:
            # def treeBindingCallback(event,handler=handler,func=func):
                # # g.trace('func',func)
                # return handler(event,func)
            # c.bind(w,a,treeBindingCallback)

        # self.textBindings = w.bindtags()
    #@-node:ekr.20081004172422.743:qtTree.setBindingsHelper
    #@-node:ekr.20081004172422.742:qtTree.setBindings & helper
    #@+node:ekr.20081004172422.744:qtTree.setCanvasBindings
    def setCanvasBindings (self,canvas):

        c = self.c ; k = c.k

        # c.bind(canvas,'<Key>',k.masterKeyHandler)
        # c.bind(canvas,'<Button-1>',self.onTreeClick)
        # c.bind(canvas,'<Button-3>',self.onTreeRightClick)
        # # c.bind(canvas,'<FocusIn>',self.onFocusIn)

        #@    << make bindings for tagged items on the canvas >>
        #@+node:ekr.20081004172422.745:<< make bindings for tagged items on the canvas >>
        # where = g.choose(self.expanded_click_area,'clickBox','plusBox')

        # table = (
            # (where,    '<Button-1>',self.onClickBoxClick),
            # ('iconBox','<Button-1>',self.onIconBoxClick),
            # ('iconBox','<Double-1>',self.onIconBoxDoubleClick),
            # ('iconBox','<Button-3>',self.onIconBoxRightClick),
            # ('iconBox','<Double-3>',self.onIconBoxRightClick),
            # ('iconBox','<B1-Motion>',self.onDrag),
            # ('iconBox','<Any-ButtonRelease-1>',self.onEndDrag),

            # ('plusBox','<Button-3>', self.onPlusBoxRightClick),
            # ('plusBox','<Button-1>', self.onClickBoxClick),
            # ('clickBox','<Button-3>',  self.onClickBoxRightClick),
        # )
        # for tag,event_kind,callback in table:
            # c.tag_bind(canvas,tag,event_kind,callback)
        #@-node:ekr.20081004172422.745:<< make bindings for tagged items on the canvas >>
        #@nl
        #@    << create baloon bindings for tagged items on the canvas >>
        #@+node:ekr.20081004172422.746:<< create baloon bindings for tagged items on the canvas >>
        # if 0: # I find these very irritating.
            # for tag,text in (
                # # ('plusBox','plusBox'),
                # ('iconBox','Icon Box'),
                # ('selectBox','Click to select'),
                # ('clickBox','Click to expand or contract'),
                # # ('textBox','Headline'),
            # ):
                # # A fairly long wait is best.
                # balloon = Pmw.Balloon(self.canvas,initwait=700)
                # balloon.tagbind(self.canvas,tag,balloonHelp=text)
        #@-node:ekr.20081004172422.746:<< create baloon bindings for tagged items on the canvas >>
        #@nl
    #@-node:ekr.20081004172422.744:qtTree.setCanvasBindings
    #@+node:ekr.20081014095718.15:get_name (qtTree)
    def getName (self):

        name = 'canvas(tree)' # Must start with canvas.

        # c = self.c ; e = self._editWidget

        # if e and e == g.app.gui.get_focus():
            # name = 'head(tree)' # Must start with 'head'
        # else:
            # self._editWidget = None
            # self._editWidgetPosition = None
            # self._editWidgetWrapper = None
            # name = 'canvas(tree)' # Must start with 'canvas'

        # g.trace('**tree',name,g.callers(4))
        return name
    #@-node:ekr.20081014095718.15:get_name (qtTree)
    #@-node:ekr.20081004172422.737: Birth... (qt Tree)
    #@+node:ekr.20081004172422.758:Config... (qtTree)
    #@+node:ekr.20081010070648.18:do-nothin config stuff
    # These can be do-nothings, replaced by QTree settings.

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
    #@-node:ekr.20081010070648.18:do-nothin config stuff
    #@+node:ekr.20081009055104.7:setConfigIvars
    def setConfigIvars (self):

        c = self.c

        self.allow_clone_drags          = c.config.getBool('allow_clone_drags')
        # self.center_selected_tree_node  = c.config.getBool('center_selected_tree_node')
        self.enable_drag_messages       = c.config.getBool("enable_drag_messages")
        # self.expanded_click_area        = c.config.getBool('expanded_click_area')
        # self.gc_before_redraw           = c.config.getBool('gc_before_redraw')

        # self.headline_text_editing_foreground_color = c.config.getColor(
            # 'headline_text_editing_foreground_color')
        # self.headline_text_editing_background_color = c.config.getColor(
            # 'headline_text_editing_background_color')
        # self.headline_text_editing_selection_foreground_color = c.config.getColor(
            # 'headline_text_editing_selection_foreground_color')
        # self.headline_text_editing_selection_background_color = c.config.getColor(
            # 'headline_text_editing_selection_background_color')
        # self.headline_text_selected_foreground_color = c.config.getColor(
            # "headline_text_selected_foreground_color")
        # self.headline_text_selected_background_color = c.config.getColor(
            # "headline_text_selected_background_color")
        # self.headline_text_editing_selection_foreground_color = c.config.getColor(
            # "headline_text_editing_selection_foreground_color")
        # self.headline_text_editing_selection_background_color = c.config.getColor(
            # "headline_text_editing_selection_background_color")
        # self.headline_text_unselected_foreground_color = c.config.getColor(
            # 'headline_text_unselected_foreground_color')
        # self.headline_text_unselected_background_color = c.config.getColor(
            # 'headline_text_unselected_background_color')

        # self.idle_redraw = c.config.getBool('idle_redraw')
        # self.initialClickExpandsOrContractsNode = c.config.getBool(
            # 'initialClickExpandsOrContractsNode')
        # self.look_for_control_drag_on_mouse_down = c.config.getBool(
            # 'look_for_control_drag_on_mouse_down')

        self.select_all_text_when_editing_headlines = c.config.getBool(
            'select_all_text_when_editing_headlines')

        self.stayInTree     = c.config.getBool('stayInTreeAfterSelect')

        self.use_chapters   = c.config.getBool('use_chapters')

        # Debugging.
            # self.trace_alloc    = c.config.getBool('trace_tree_alloc')
            # self.trace_chapters = c.config.getBool('trace_chapters')
            # self.trace_edit     = c.config.getBool('trace_tree_edit')
            # self.trace_gc       = c.config.getBool('trace_tree_gc')
            # self.trace_redraw   = c.config.getBool('trace_tree_redraw')
            # self.trace_select   = c.config.getBool('trace_select')
            # self.trace_stats    = c.config.getBool('show_tree_stats')
    #@-node:ekr.20081009055104.7:setConfigIvars
    #@-node:ekr.20081004172422.758:Config... (qtTree)
    #@+node:ekr.20081010070648.19:Drawing... (qtTree)
    #@+node:ekr.20081011035036.12:allAncestorsExpanded
    def allAncestorsExpanded (self,p):

        for p in p.self_and_parents_iter():
            if not p.isExpanded():
                return False
        else:
            return True
    #@-node:ekr.20081011035036.12:allAncestorsExpanded
    #@+node:ekr.20081021043407.23:full_redraw & helpers
    def full_redraw (self,scroll=False,forceDraw=False): # forceDraw not used.

        '''Redraw all visible nodes of the tree'''

        c = self.c ; w = self.treeWidget
        trace = False; verbose = False
        if not w: return
        if self.redrawing:
            g.trace('***** already drawing',g.callers(5))
            return

        self.redrawCount += 1
        if trace and verbose: tstart()

        # Init the data structures.
        self.initData()
        self.nodeDrawCount = 0
        self.redrawing = True
        self.fullDrawing = True # To suppress some traces.
        try:
            w.clear()
            # Draw all top-level nodes and their visible descendants.
            p = c.rootPosition()
            while p:
                self.drawTree(p)
                p.moveToNext()
        finally:
            if not self.selecting:
                item = self.setCurrentItem()
                if item:
                    if 0: # Annoying.
                        w.scrollToItem(item,
                            QtGui.QAbstractItemView.PositionAtCenter)
                elif p and self.redrawCount > 1:
                    g.trace('Error: no current item: %s' % (p.headString()))

            # Necessary to get the tree drawn initially.
            w.repaint()

            c.requestRedrawFlag= False
            self.redrawing = False
            self.fullDrawing = False
            if trace:
                if verbose: tstop()
                g.trace('%s: drew %3s nodes' % (
                    self.redrawCount,self.nodeDrawCount),g.callers())

    redraw = full_redraw # Compatibility
    redraw_now = full_redraw
    #@+node:ekr.20081021043407.30:initData
    def initData (self):

        self.tnodeDict = {} # keys are tnodes, values are lists of items (p,it)
        self.vnodeDict = {} # keys are vnodes, values are lists of items (p,it)
        self.itemsDict = {} # keys are items, values are positions
        self.parentsDict = {}
        self._editWidgetPosition = None
        self._editWidget = None
        self._editWidgetWrapper = None
    #@nonl
    #@-node:ekr.20081021043407.30:initData
    #@+node:ekr.20081021043407.24:drawNode
    def drawNode (self,p,dummy=False):

        w = self.treeWidget ; trace = False
        self.nodeDrawCount += 1

        # Allocate the qt tree item.
        parent = p.parent()
        it = self.parentsDict.get(parent and parent.v,w)

        if trace and not self.fullDrawing:
            g.trace(id(it),parent and parent.headString())

        it = QtGui.QTreeWidgetItem(it)
        it.setFlags(it.flags() | QtCore.Qt.ItemIsEditable)

        # Draw the headline and the icon.
        it.setText(0,p.headString())
        icon = self.getIcon(p)
        if icon: it.setIcon(0,icon)

        if dummy: return it

        # Remember the associatiation of it with p, and vice versa.
        self.itemsDict[it] = p.copy()
        self.parentsDict[p.v] = it 

        # Remember the association of p.v with (p,it)
        aList = self.vnodeDict.get(p.v,[])
        data = p.copy(),it
        aList.append(data)
        self.vnodeDict[p.v] = aList

        # Remember the association of p.v.t with (p,it).
        aList = self.tnodeDict.get(p.v.t,[])
        data = p.copy(),it
        aList.append(data)
        self.tnodeDict[p.v.t] = aList

        return it
    #@-node:ekr.20081021043407.24:drawNode
    #@+node:ekr.20081021043407.25:drawTree
    def drawTree (self,p):

        c = self.c ; w = self.treeWidget

        p = p.copy()

        # g.trace(p.headString())

        # Draw the (visible) parent node.
        it = self.drawNode(p)

        if p.hasChildren():
            if p.isExpanded():
                w.expandItem(it)
                child = p.firstChild()
                while child:
                    self.drawTree(child)
                    child.moveToNext()
            else:
                if 0:
                    # Just draw one dummy child.
                    # This doesn't work with the new expansion code.
                    self.drawNode(p.firstChild(),dummy=True)
                else:
                    # Draw the hidden children.
                    child = p.firstChild()
                    while child:
                        self.drawNode(child)
                        child.moveToNext()
                w.collapseItem(it)
        else:
            w.collapseItem(it)
    #@-node:ekr.20081021043407.25:drawTree
    #@+node:ekr.20081027082521.12:setCurrentItem
    def setCurrentItem (self):

        c = self.c ; p = c.currentPosition()
        trace = False
        w = self.treeWidget

        if self.expanding:
            if trace: g.trace('already expanding')
            return None
        if self.selecting:
            if trace: g.trace('already selecting')
            return None

        aList = self.vnodeDict.get(p.v,[])
        h = p and p.headString() or '<no p!>'
        if not p: return False

        for p2,item in aList:
            if p == p2:
                if trace: g.trace('found: %s, %s' % (id(item),h))
                # Actually select the item only if necessary.
                # This prevents any side effects.
                item2 = w.currentItem()
                if item != item2:
                    if trace: g.trace(item==item,'old item',item2)
                    self.selecting = True
                    try:
                        w.setCurrentItem(item)
                    finally:
                        self.selecting = False
                return item
        else:
            if trace: g.trace('** no item for',p.headString())
            return None
    #@-node:ekr.20081027082521.12:setCurrentItem
    #@-node:ekr.20081021043407.23:full_redraw & helpers
    #@+node:ekr.20081010070648.14:getIcon & getIconImage
    def getIcon(self,p):

        '''Return the proper icon for position p.'''

        p.v.iconVal = val = p.v.computeIcon()
        return self.getIconImage(val)

    def getIconImage(self,val):

        return g.app.gui.getIconImage(
            "box%02d.GIF" % val)

    #@-node:ekr.20081010070648.14:getIcon & getIconImage
    #@+node:ekr.20081021043407.4:redraw_after_clone
    def redraw_after_clone (self):

        self.full_redraw()
    #@-node:ekr.20081021043407.4:redraw_after_clone
    #@+node:ekr.20081021043407.5:redraw_after_contract
    def redraw_after_contract (self):

        self.full_redraw()
    #@-node:ekr.20081021043407.5:redraw_after_contract
    #@+node:ekr.20081021043407.6:redraw_after_delete
    def redraw_after_delete (self):

        self.full_redraw()


    #@-node:ekr.20081021043407.6:redraw_after_delete
    #@+node:ekr.20081021043407.7:redraw_after_expand & helper
    def redraw_after_expand (self):

        # This is reasonable now that we only allocate
        # one dummy node in collapsed trees.
        return self.full_redraw()

        # trace = True ; verbose = False
        # c = self.c ; p = c.currentPosition()
        # w = self.treeWidget

        # if self.redrawing:
            # if trace: g.trace('already drawing',p.headString())
            # return
        # self.redrawCount += 1
        # if trace: g.trace(self.redrawCount,p.headString())
        # it = self.parentsDict.get(p.v)
        # if not it:
            # g.trace('can not happen: no item for %s' % p.headString())
            # return self.full_redraw()
        # self.nodeDrawCount = 0
        # self.redrawing = True
        # self.expanding = True
        # try:
            # w.expandItem(it)
            # # Delete all the children from the tree.
            # items = it.takeChildren()
            # if trace and verbose:
                # g.trace(id(it),len(items),p.headString())
            # # Delete all descendant entries from dictionaries.
            # for child in p.children_iter():
                # for z in child.self_and_subtree_iter():
                    # self.removeFromDicts(z)
            # # Redraw all descendants.
            # for child in p.children_iter():
                # self.drawTree(child)
        # finally:
            # w.setCurrentItem(it)
            # self.redrawing = False
            # self.expanding = False
            # c.requestRedrawFlag= False
            # if trace:
                # g.trace('drew %3s nodes' %self.nodeDrawCount)
    #@+node:ekr.20081021043407.28:removeFromDicts
    def removeFromDicts (self,p):

        # Important: items do not necessarily exist.

        # Remove item from parentsDict.
        it = self.parentsDict.get(p.v)
        if it: del self.parentsDict[p.v]

        # Remove position from itemsDict.
        p2 = self.itemsDict.get(it)
        if p2 == p: del self.itemsDict[it]

        # Remove items from vnodeDict
        aList = self.vnodeDict.get(p.v,[])
        # aList = [z for z in aList if z[1] != it] # Wrong
        aList = [z for z in aList if z[0] != p]
        self.vnodeDict[p.v] = aList

        # Remove items from tnodeDict
        aList = self.tnodeDict.get(p.v.t,[])
        # aList = [z for z in aList if z[1] != it] # Wrong
        aList = [z for z in aList if z[0] != p]
        self.tnodeDict[p.v.t] = aList
    #@-node:ekr.20081021043407.28:removeFromDicts
    #@-node:ekr.20081021043407.7:redraw_after_expand & helper
    #@+node:ekr.20081021043407.3:redraw_after_icons_changed
    def redraw_after_icons_changed (self,all=False):

        g.trace('should not be called',g.callers(4))

        c = self.c ; p = c.currentPosition()

        if all:
            self.full_redraw()
        else:
            self.updateIcon(p)


    #@-node:ekr.20081021043407.3:redraw_after_icons_changed
    #@+node:ekr.20081021043407.8:redraw_after_insert
    def redraw_after_insert (self):

        self.full_redraw()
    #@-node:ekr.20081021043407.8:redraw_after_insert
    #@+node:ekr.20081021043407.9:redraw_after_move_down
    def redraw_after_move_down (self):

        self.full_redraw()
    #@nonl
    #@-node:ekr.20081021043407.9:redraw_after_move_down
    #@+node:ekr.20081021043407.10:redraw_after_move_left
    def redraw_after_move_left (self):

        self.full_redraw()
    #@nonl
    #@-node:ekr.20081021043407.10:redraw_after_move_left
    #@+node:ekr.20081021043407.11:redraw_after_move_right
    def redraw_after_move_right (self):

        if 0: # now done in c.moveOutlineRight.
            c = self.c ; p = c.currentPosition()
            parent = p.parent()
            if parent: parent.expand()


        # g.trace('parent',c.currentPosition().parent() or "non")

        self.full_redraw()
    #@-node:ekr.20081021043407.11:redraw_after_move_right
    #@+node:ekr.20081021043407.12:redraw_after_move_up
    def redraw_after_move_up (self):

        self.full_redraw()
    #@-node:ekr.20081021043407.12:redraw_after_move_up
    #@+node:ekr.20081021043407.13:redraw_after_select
    def redraw_after_select (self):

        '''Redraw the screen after selecting a node.'''

        w = self.treeWidget ; trace = False
        c = self.c ; p = c.currentPosition()

        if not p:
            return g.trace('Error: no p')
        if self.selecting:
            if trace: g.trace('already selecting')
            return
        if self.redrawing:
            return g.trace('Error: already redrawing')

        if trace: g.trace(p.headString(),g.callers(4))

        # setCurrentItem sets .selecting ivar
        self.setCurrentItem()
    #@-node:ekr.20081021043407.13:redraw_after_select
    #@+node:ekr.20081011035036.11:updateIcon
    def updateIcon (self,p):

        '''Update p's icon.'''

        if not p: return

        val = p.v.computeIcon()
        if p.v.iconVal == val: return

        icon = self.getIconImage(val)
        aList = self.tnodeDict.get(p.v.t,[])
        for p,it in aList:
            # g.trace(id(it),p.headString())
            it.setIcon(0,icon)
    #@-node:ekr.20081011035036.11:updateIcon
    #@-node:ekr.20081010070648.19:Drawing... (qtTree)
    #@+node:ekr.20081004172422.795:Event handlers... (qtTree)
    #@+node:ekr.20081009055104.8:onTreeSelect
    def onTreeSelect(self):

        '''Select the proper position when a tree node is selected.'''

        c = self.c ; w = self.treeWidget ; trace = False ; verbose = False

        if self.selecting:
            if trace: g.trace('already selecting')
            return
        if self.redrawing:
            if trace: g.trace('drawing')
            return

        it = w.currentItem()
        if trace and verbose: g.trace('it 1',it)
        p = self.itemsDict.get(it)
        if p:
            if trace: g.trace(p and p.headString())
            c.frame.tree.select(p) # The crucial hook.
            # g.trace(g.callers())
            c.outerUpdate()
        else:
            # An error: we are not redrawing.
            g.trace('no p for item: %s' % it,g.callers(4))
    #@nonl
    #@-node:ekr.20081009055104.8:onTreeSelect
    #@+node:ville.20081014172405.10:sig_itemChanged
    def sig_itemChanged(self, item, col):

        '''Handle a change event in a headline.
        This only gets called when the user hits return.'''

        # Ignore changes when redrawing.
        if self.redrawing:
            return

        p = self.itemsDict.get(item)
        if p:
            # so far, col is always 0
            s = g.toUnicode(item.text(col),'utf-8')
            p.setHeadString(s)
            # g.trace("changed: ",p.headString(),g.callers(4))
            self._editWidget = None
            self._editWidgetPosition = None
            self._editWidgetWrapper = None
        else:
            g.trace('can not happen: no p')
    #@-node:ville.20081014172405.10:sig_itemChanged
    #@+node:ekr.20081027124640.10:sig_itemCollapsed
    def sig_itemCollapsed (self,item):

        c = self.c ; p = c.currentPosition() ; w = self.treeWidget
        trace = False ; verbose = False

        # Ignore events generated by redraws.
        if self.redrawing:
            if trace and verbose: g.trace('already redrawing',g.callers(4))
            return
        if self.expanding:
            if trace and verbose: g.trace('already expanding',g.callers(4))
            return
        if self.selecting:
            if trace and verbose: g.trace('already selecting',g.callers(4))
            return

        if trace: g.trace(p.headString() or "<no p>",g.callers(4))

        p2 = self.itemsDict.get(item)
        if p2:
            p2.contract()
            c.setCurrentPosition(p2)
            item = self.setCurrentItem()
            if 0: # Annoying.
                w.scrollToItem(item,
                    QtGui.QAbstractItemView.PositionAtCenter)
        else:
            g.trace('Error no p2')
    #@-node:ekr.20081027124640.10:sig_itemCollapsed
    #@+node:ekr.20081021043407.26:sig_itemExpanded
    def sig_itemExpanded (self,item):

        '''Handle and tree-expansion event.'''

        # The difficult case is when the user clicks the expansion box.

        c = self.c ; p = c.currentPosition() ; w = self.treeWidget
        trace = False ; verbose = False

        # Ignore events generated by redraws.
        if self.redrawing:
            if trace and verbose: g.trace('already redrawing',g.callers(4))
            return
        if self.expanding:
            if trace and verbose: g.trace('already expanding',g.callers(4))
            return
        if self.selecting:
            if trace and verbose: g.trace('already selecting',g.callers(4))
            return

        if trace: g.trace(p.headString() or "<no p>",g.callers(4))

        self.expanding = True
        try:
            redraw = False
            p2 = self.itemsDict.get(item)
            if p2:
                if trace: g.trace(p2)
                if not p2.isExpanded():
                    p2.expand()
                c.setCurrentPosition(p2)
                self.full_redraw()
                redraw = True
            else:
                g.trace('Error no p2')

        finally:
            self.expanding = False
            if redraw:
                item = self.setCurrentItem()
                if item:
                    w.scrollToItem(item,
                        QtGui.QAbstractItemView.PositionAtCenter)
    #@-node:ekr.20081021043407.26:sig_itemExpanded
    #@+node:ekr.20081004172422.801:findEditWidget
    def findEditWidget (self,p):

        """Return the Qt.Text item corresponding to p."""

        # g.trace(p,g.callers(4))

        return None

        # c = self.c ; trace = False

        # # if trace: g.trace(g.callers())

        # if p and c:
            # # if trace: g.trace('h',p.headString(),'key',p.key())
            # aTuple = self.visibleText.get(p.key())
            # if aTuple:
                # w,theId = aTuple
                # # if trace: g.trace('id(p.v):',id(p.v),'%4d' % (theId),self.textAddr(w),p.headString())
                # return w
            # else:
                # if trace: g.trace('oops: not found',p,g.callers())
                # return None

        # if trace: g.trace('not found',p and p.headString())
        # return None
    #@-node:ekr.20081004172422.801:findEditWidget
    #@+node:ekr.20081004172422.803:Click Box...
    #@+node:ekr.20081004172422.804:onClickBoxClick
    def onClickBoxClick (self,event,p=None):

        c = self.c ; p1 = c.currentPosition()

        # g.trace(p and p.headString())

        # if not p: p = self.eventToPosition(event)
        # if not p: return

        # c.setLog()

        # if p and not g.doHook("boxclick1",c=c,p=p,v=p,event=event):
            # c.endEditing()
            # if p == p1 or self.initialClickExpandsOrContractsNode:
                # if p.isExpanded(): p.contract()
                # else:              p.expand()
            # self.select(p)
            # if c.frame.findPanel:
                # c.frame.findPanel.handleUserClick(p)
            # if self.stayInTree:
                # c.treeWantsFocus()
            # else:
                # c.bodyWantsFocus()
        # g.doHook("boxclick2",c=c,p=p,v=p,event=event)
        # c.redraw()

        # c.outerUpdate()
    #@-node:ekr.20081004172422.804:onClickBoxClick
    #@+node:ekr.20081004172422.805:onClickBoxRightClick
    def onClickBoxRightClick(self, event, p=None):
        #g.trace()
        return 'break'
    #@nonl
    #@-node:ekr.20081004172422.805:onClickBoxRightClick
    #@+node:ekr.20081004172422.806:onPlusBoxRightClick
    def onPlusBoxRightClick (self,event,p=None):

        c = self.c

        # self._block_canvas_menu = True

        # if not p: p = self.eventToPosition(event)
        # if not p: return

        # self.OnActivateHeadline(p)
        # self.endEditLabel()

        # g.doHook('rclick-popup',c=c,p=p,event=event,context_menu='plusbox')

        # c.outerUpdate()

        # return 'break'
    #@-node:ekr.20081004172422.806:onPlusBoxRightClick
    #@-node:ekr.20081004172422.803:Click Box...
    #@+node:ekr.20081004172422.816:Icon Box...
    #@+node:ekr.20081004172422.817:onIconBoxClick
    def onIconBoxClick (self,event,p=None):

        c = self.c ; tree = self

        # if not p: p = self.eventToPosition(event)
        # if not p:
            # return

        # c.setLog()

        # if not g.doHook("iconclick1",c=c,p=p,v=p,event=event):
            # if event:
                # self.onDrag(event)
            # tree.endEditLabel()
            # tree.select(p,scroll=False)
            # if c.frame.findPanel:
                # c.frame.findPanel.handleUserClick(p)
        # g.doHook("iconclick2",c=c,p=p,v=p,event=event)

        # return "break" # disable expanded box handling.
    #@-node:ekr.20081004172422.817:onIconBoxClick
    #@+node:ekr.20081004172422.818:onIconBoxRightClick
    def onIconBoxRightClick (self,event,p=None):

        """Handle a right click in any outline widget."""

        #g.trace()

        # c = self.c

        # if not p: p = self.eventToPosition(event)
        # if not p:
            # c.outerUpdate()
            # return

        # c.setLog()

        # try:
            # if not g.doHook("iconrclick1",c=c,p=p,v=p,event=event):
                # self.OnActivateHeadline(p)
                # self.endEditLabel()
                # if not g.doHook('rclick-popup', c=c, p=p, event=event, context_menu='iconbox'):
                    # self.OnPopup(p,event)
            # g.doHook("iconrclick2",c=c,p=p,v=p,event=event)
        # except:
            # g.es_event_exception("iconrclick")

        # self._block_canvas_menu = True

        # c.outerUpdate()
        # return 'break'
    #@-node:ekr.20081004172422.818:onIconBoxRightClick
    #@+node:ekr.20081004172422.819:onIconBoxDoubleClick
    def onIconBoxDoubleClick (self,event,p=None):

        c = self.c

        # if not p: p = self.eventToPosition(event)
        # if not p:
            # c.outerUpdate()
            # return

        # c.setLog()

        # try:
            # if not g.doHook("icondclick1",c=c,p=p,v=p,event=event):
                # self.endEditLabel() # Bug fix: 11/30/05
                # self.OnIconDoubleClick(p) # Call the method in the base class.
            # g.doHook("icondclick2",c=c,p=p,v=p,event=event)
        # except:
            # g.es_event_exception("icondclick")

        # c.outerUpdate()
        # return 'break'
    #@-node:ekr.20081004172422.819:onIconBoxDoubleClick
    #@-node:ekr.20081004172422.816:Icon Box...
    #@+node:ekr.20081004172422.828:tree.OnPopup & allies
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
    #@+node:ekr.20081004172422.829:OnPopupFocusLost
    #@+at 
    #@nonl
    # On Linux we must do something special to make the popup menu "unpost" if 
    # the mouse is clicked elsewhere.  So we have to catch the <FocusOut> 
    # event and explicitly unpost.  In order to process the <FocusOut> event, 
    # we need to be able to find the reference to the popup window again, so 
    # this needs to be an attribute of the tree object; hence, 
    # "self.popupMenu".
    # 
    # Aside: though Qt tries to be muli-platform, the interaction with 
    # different window managers does cause small differences that will need to 
    # be compensated by system specific application code. :-(
    #@-at
    #@@c

    # 20-SEP-2002 DTHEIN: This event handler is only needed for Linux.

    def OnPopupFocusLost(self,event=None):

        # self.popupMenu.unpost()
        pass
    #@-node:ekr.20081004172422.829:OnPopupFocusLost
    #@+node:ekr.20081004172422.830:createPopupMenu
    def createPopupMenu (self,event):

        c = self.c ; frame = c.frame

        # self.popupMenu = menu = Qt.Menu(g.app.root, tearoff=0)

        # # Add the Open With entries if they exist.
        # if g.app.openWithTable:
            # frame.menu.createOpenWithMenuItemsFromTable(menu,g.app.openWithTable)
            # table = (("-",None,None),)
            # frame.menu.createMenuEntries(menu,table)

        #@    << Create the menu table >>
        #@+node:ekr.20081004172422.831:<< Create the menu table >>
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
        #@-node:ekr.20081004172422.831:<< Create the menu table >>
        #@nl

        # # New in 4.4.  There is no need for a dontBind argument because
        # # Bindings from tables are ignored.
        # frame.menu.createMenuEntries(menu,table)
    #@-node:ekr.20081004172422.830:createPopupMenu
    #@+node:ekr.20081004172422.832:enablePopupMenuItems
    def enablePopupMenuItems (self,v,event):

        """Enable and disable items in the popup menu."""

        c = self.c 

        # menu = self.popupMenu

        #@    << set isAtRoot and isAtFile if v's tree contains @root or @file nodes >>
        #@+node:ekr.20081004172422.833:<< set isAtRoot and isAtFile if v's tree contains @root or @file nodes >>
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
        #@-node:ekr.20081004172422.833:<< set isAtRoot and isAtFile if v's tree contains @root or @file nodes >>
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
    #@-node:ekr.20081004172422.832:enablePopupMenuItems
    #@+node:ekr.20081004172422.834:showPopupMenu
    def showPopupMenu (self,event):

        """Show a popup menu."""

        # c = self.c ; menu = self.popupMenu

        # g.app.gui.postPopupMenu(c, menu, event.x_root, event.y_root)

        # self.popupMenu = None

        # # Set the focus immediately so we know when we lose it.
        # #c.widgetWantsFocus(menu)
    #@-node:ekr.20081004172422.834:showPopupMenu
    #@-node:ekr.20081004172422.828:tree.OnPopup & allies
    #@-node:ekr.20081004172422.795:Event handlers... (qtTree)
    #@+node:ekr.20081019045904.2:Focus (qtTree)
    def getFocus(self):

        # g.trace('leoQtTree',self.widget,g.callers(4))
        return g.app.gui.get_focus()

    findFocus = getFocus

    def hasFocus (self):

        val = self.treeWidget == g.app.gui.get_focus(self.c)
        # g.trace('leoQtTree returns',val,self.widget,g.callers(4))
        return val

    def setFocus (self):

        # g.trace('leoQtTree',self.treeWidget,g.callers(4))
        g.app.gui.set_focus(self.c,self.treeWidget)
    #@-node:ekr.20081019045904.2:Focus (qtTree)
    #@+node:ekr.20081004172422.844:Selecting & editing... (qtTree)
    #@+node:ekr.20081004172422.799:edit_widget
    def edit_widget (self,p):

        """Returns the Qt.Edit widget for position p."""

        w = self._editWidgetWrapper

        if p and p == self._editWidgetPosition:
            return w
        else:
            return None

        # Decouple all of the core's headline code.
        # Except for over-ridden methods.
    #@-node:ekr.20081004172422.799:edit_widget
    #@+node:ekr.20081025124450.14:beforeSelectHint
    def beforeSelectHint (self,p,old_p):

        w = self.treeWidget ; trace = True

        if self.selecting:
            return g.trace('*** Error: already selecting',g.callers(4))

        if self.redrawing:
            if trace: g.trace('already redrawing')
            return

        # Disable onTextChanged.
        self.selecting = True
    #@-node:ekr.20081025124450.14:beforeSelectHint
    #@+node:ekr.20081025124450.15:afterSelectHint
    def afterSelectHint (self,p,old_p):

        # g.trace(p and p.headString(),g.callers(4))

        self.selecting = False

        self.redraw_after_select()
    #@-node:ekr.20081025124450.15:afterSelectHint
    #@+node:ekr.20081004172422.854:setHeadline
    def setHeadline (self,p,s):

        '''Set the actual text of the headline widget.

        This is called from the undo/redo logic to change the text before redrawing.'''

        # w = self.edit_widget(p)
        # if w:
            # w.configure(state='normal')
            # w.delete(0,'end')
            # if s.endswith('\n') or s.endswith('\r'):
                # s = s[:-1]
            # w.insert(0,s)
            # self.revertHeadline = s
            # # g.trace(repr(s),w.getAllText())
        # else:
            # g.trace('-'*20,'oops')
    #@-node:ekr.20081004172422.854:setHeadline
    #@+node:ekr.20081004172422.846:editLabel (override)
    def editLabel (self,p,selectAll=False):

        """Start editing p's headline."""

        c = self.c ; trace = False ; verbose = False

        if self.redrawing:
            if trace and verbose: g.trace('redrawing')
            return
        if self._editWidget:
            # Not an error, because of key weirdness.
            g.trace('already editing')
            return

        if trace:
            g.trace('*** all',selectAll,p.headString(),g.callers(4))

        w = self.treeWidget
        data = self.vnodeDict.get(p.v)
        if not data:
            if trace and verbose:
                g.trace('No data: redrawing if possible')
            c.outerUpdate() # Do any scheduled redraw.
            data = self.vnodeDict.get(p.v)

        if data:
            item = data [0][1]
        else:
            if trace and not g.app.unitTesting:
                g.trace('*** Can not happen: no data',p and p.headString())
            return None

        if item:
            w.setCurrentItem(item) # Must do this first.
            w.editItem(item)
            e = w.itemWidget(item,0) # A QLineEdit
            if e:
                s = e.text() ; len_s = len(s)
                # Hook up the widget to Leo's core.
                self._editWidgetPosition = p.copy()
                self._editWidget = e
                self._editWidgetWrapper = leoQtHeadlineWidget(
                    widget=e,name='head',c=c)
                start,n = g.choose(selectAll,
                    tuple([0,len_s]),tuple([len_s,0]))
                e.setObjectName('headline')
                e.setSelection(start,n)
                e.setFocus()
            else: g.trace('*** no e')
        else:
            self._editWidgetPosition = None
            self._editWidget = None
            self._editWidgetWrapper = None
            e = None
            g.trace('*** no item')

        # A nice hack: just set the focus request.
        c.requestedFocusWidget = e

        # g.trace('leoQtTree','it',it,p and p.headString())

        # if p and p != self.editPosition():
            # self.endEditLabel()
            # # This redraw *is* required so the c.edit_widget(p) will exist.
            # c.redraw()
            # c.outerUpdate()

        # self.setEditPosition(p) # That is, self._editPosition = p
        # w = c.edit_widget(p)
        # if p and w:
            # self.revertHeadline = p.headString() # New in 4.4b2: helps undo.
            # self.setEditLabelState(p,selectAll=selectAll) # Sets the focus immediately.
            # c.headlineWantsFocus(p) # Make sure the focus sticks.
            # c.k.showStateAndMode(w)
    #@-node:ekr.20081004172422.846:editLabel (override)
    #@+node:ekr.20081030120643.11:onHeadChanged
    # Tricky code: do not change without careful thought and testing.

    def onHeadChanged (self,p,undoType='Typing',s=None):

        '''Officially change a headline.'''

        trace = False ; verbose = False
        c = self.c
        e = self._editWidget
        p = self._editWidgetPosition

        # These are not errors: sig_itemChanged may
        # have been called first.
        if not e:
            if trace and verbose: g.trace('No widget')
            return 
        if e != g.app.gui.get_focus():
            if trace and verbose: g.trace('Wrong focus')
            self._editWidget = None
            self._editWidgetPosition = None
            self._editWidgetWrapper = None
            return
        if not p:
            if trace and verbose: g.trace('No widget position')
            return
        s = e.text() ; len_s = len(s)
        s = g.toUnicode(s,'utf-8')
        if trace: g.trace(repr(s),g.callers(4))
        p.setHeadString(s)
        # End the editing!
        self._editWidget = None
        self._editWidgetPosition = None
        self._editWidgetWrapper = None
        c.redraw(scroll=False)
        if self.stayInTree:
            c.treeWantsFocus()
        else:
            c.bodyWantsFocus()
    #@nonl
    #@-node:ekr.20081030120643.11:onHeadChanged
    #@-node:ekr.20081004172422.844:Selecting & editing... (qtTree)
    #@-others
#@-node:ekr.20081004172422.732:class leoQtTree
#@+node:ekr.20081004172422.684:class leoQtTreeTab
class leoQtTreeTab (leoFrame.leoTreeTab):

    '''A class representing a tabbed outline pane drawn with Qt.'''

    #@    @+others
    #@+node:ekr.20081004172422.685: Birth & death
    #@+node:ekr.20081004172422.686: ctor (leoTreeTab)
    def __init__ (self,c,parentFrame,chapterController):

        leoFrame.leoTreeTab.__init__ (self,c,chapterController,parentFrame)
            # Init the base class.  Sets self.c, self.cc and self.parentFrame.

        self.tabNames = [] # The list of tab names.  Changes when tabs are renamed.

        self.createControl()
    #@-node:ekr.20081004172422.686: ctor (leoTreeTab)
    #@+node:ekr.20081004172422.687:tt.createControl
    def createControl (self):

        return None

        # tt = self ; c = tt.c

        # # Create the main container, possibly in a new row.
        # tt.frame = c.frame.getNewIconFrame()

        # # Create the chapter menu.
        # self.chapterVar = var = qt.StringVar()
        # var.set('main')

        # tt.chapterMenu = menu = Pmw.OptionMenu(tt.frame,
            # labelpos = 'w', label_text = 'chapter',
            # menubutton_textvariable = var,
            # items = [],
            # command = tt.selectTab,
        # )
        # menu.pack(side='left',padx=5)

        # # Actually add tt.frame to the icon row.
        # c.frame.addIconWidget(tt.frame)
    #@-node:ekr.20081004172422.687:tt.createControl
    #@-node:ekr.20081004172422.685: Birth & death
    #@+node:ekr.20081004172422.688:Tabs...
    #@+node:ekr.20081004172422.689:tt.createTab
    def createTab (self,tabName,select=True):

        tt = self

        # if tabName not in tt.tabNames:
            # tt.tabNames.append(tabName)
            # tt.setNames()
    #@-node:ekr.20081004172422.689:tt.createTab
    #@+node:ekr.20081004172422.690:tt.destroyTab
    def destroyTab (self,tabName):

        tt = self

        # if tabName in tt.tabNames:
            # tt.tabNames.remove(tabName)
            # tt.setNames()
    #@-node:ekr.20081004172422.690:tt.destroyTab
    #@+node:ekr.20081004172422.691:tt.selectTab
    def selectTab (self,tabName):

        tt = self

        # if tabName not in self.tabNames:
            # tt.createTab(tabName)

        # tt.cc.selectChapterByName(tabName)

        # self.c.redraw()
        # self.c.outerUpdate()
    #@-node:ekr.20081004172422.691:tt.selectTab
    #@+node:ekr.20081004172422.692:tt.setTabLabel
    def setTabLabel (self,tabName):

        tt = self
    #     tt.chapterVar.set(tabName)
    #@-node:ekr.20081004172422.692:tt.setTabLabel
    #@+node:ekr.20081004172422.693:tt.setNames
    def setNames (self):

        '''Recreate the list of items.'''

        # tt = self
        # names = tt.tabNames[:]
        # if 'main' in names: names.remove('main')
        # names.sort()
        # names.insert(0,'main')
        # tt.chapterMenu.setitems(names)
    #@-node:ekr.20081004172422.693:tt.setNames
    #@-node:ekr.20081004172422.688:Tabs...
    #@-others
#@nonl
#@-node:ekr.20081004172422.684:class leoQtTreeTab
#@+node:ekr.20081006073635.34:class qtMenuWrapper (QtMenu,leoQtMenu)
class qtMenuWrapper (QtGui.QMenu,leoQtMenu):

    def __init__ (self,c,frame,parent):

        assert c
        assert frame
        QtGui.QMenu.__init__(self,parent)
        leoQtMenu.__init__(self,frame)

    def __repr__(self):

        return '<qtMenuWrapper %s>' % self.leo_label or 'unlabeled'
#@-node:ekr.20081006073635.34:class qtMenuWrapper (QtMenu,leoQtMenu)
#@+node:ekr.20081007015817.34:class qtSearchWidget
class qtSearchWidget:

    """A dummy widget class to pass to Leo's core find code."""

    def __init__ (self):

        self.insertPoint = 0
        self.selection = 0,0
        self.bodyCtrl = self
        self.body = self
        self.text = None
#@nonl
#@-node:ekr.20081007015817.34:class qtSearchWidget
#@-node:ekr.20081103071436.3:Frame and component classes...
#@+node:ekr.20081109092601.10:Gui wrapper
#@+node:ekr.20081004102201.631:class leoQtGui
class leoQtGui(leoGui.leoGui):

    '''A class implementing Leo's Qt gui.'''

    #@    @+others
    #@+node:ekr.20081004102201.632:  Birth & death (qtGui)
    #@+node:ekr.20081004102201.633: qtGui.__init__
    def __init__ (self):

        # Initialize the base class.
        leoGui.leoGui.__init__(self,'qt')

        self.qtApp = QtGui.QApplication(sys.argv)

        self.bodyTextWidget  = leoQtBaseTextWidget
        self.plainTextWidget = leoQtBaseTextWidget

        self.iconimages = {} # Image cache set by getIconImage().

        self.mGuiName = 'qt'
    #@-node:ekr.20081004102201.633: qtGui.__init__
    #@+node:ekr.20081004102201.634:createKeyHandlerClass (qtGui)
    def createKeyHandlerClass (self,c,useGlobalKillbuffer=True,useGlobalRegisters=True):

        ### Use the base class
        return leoKeys.keyHandlerClass(c,useGlobalKillbuffer,useGlobalRegisters)

        ### return qtKeyHandlerClass(c,useGlobalKillbuffer,useGlobalRegisters)
    #@-node:ekr.20081004102201.634:createKeyHandlerClass (qtGui)
    #@+node:ekr.20081004102201.635:runMainLoop (qtGui)
    def runMainLoop(self):

        '''Start the Qt main loop.'''

        if self.script:
            log = g.app.log
            if log:
                g.pr('Start of batch script...\n')
                log.c.executeScript(script=self.script)
                g.pr('End of batch script')
            else:
                g.pr('no log, no commander for executeScript in qtGui.runMainLoop')
        else:
            sys.exit(self.qtApp.exec_())
    #@-node:ekr.20081004102201.635:runMainLoop (qtGui)
    #@+node:ekr.20081004102201.636:destroySelf
    def destroySelf (self):
        QtCore.pyqtRemoveInputHook()
        self.qtApp.exit()
    #@nonl
    #@-node:ekr.20081004102201.636:destroySelf
    #@-node:ekr.20081004102201.632:  Birth & death (qtGui)
    #@+node:ekr.20081004102201.648:Clipboard
    def replaceClipboardWith (self,s):

        '''Replace the clipboard with the string s.'''

        cb = self.qtApp.clipboard()
        if cb:
            cb.clear()
            cb.setText(g.toEncodedString(s,'utf-8'))

    def getTextFromClipboard (self):

        '''Get a unicode string from the clipboard.'''

        cb = self.qtApp.clipboard()
        s = cb and cb.text() or ''
        return g.toUnicode(s,'utf-8')
    #@-node:ekr.20081004102201.648:Clipboard
    #@+node:ekr.20081004102201.651:Do nothings
    def color (self,color):         return None

    def createRootWindow(self):     pass

    def killGui(self,exitFlag=True):
        """Destroy a gui and terminate Leo if exitFlag is True."""

    def recreateRootWindow(self):
        """Create the hidden root window of a gui
        after a previous gui has terminated with killGui(False)."""


    #@-node:ekr.20081004102201.651:Do nothings
    #@+node:ekr.20081004102201.640:Dialogs & panels
    #@+node:ekr.20081109092601.11:makeFilter
    def makeFilter (self,filetypes):

        '''Return the Qt-style dialog filter from filetypes list.'''

        filters = ['%s (%s)' % (z) for z in filetypes]

        return ';;'.join(filters)
    #@-node:ekr.20081109092601.11:makeFilter
    #@+node:ekr.20081020075840.18:not used
    def runAskOkCancelNumberDialog(self,c,title,message):

        """Create and run askOkCancelNumber dialog ."""

        if g.unitTesting: return None
        g.trace('not ready yet')

    def runAskOkCancelStringDialog(self,c,title,message):

        """Create and run askOkCancelString dialog ."""

        if g.unitTesting: return None
        g.trace('not ready yet')


    #@-node:ekr.20081020075840.18:not used
    #@+node:ekr.20081004102201.646:qtGui panels
    def createComparePanel(self,c):

        """Create a qt color picker panel."""
        return None # This window is optional.
        # return leoQtComparePanel(c)

    def createFindTab (self,c,parentFrame):
        """Create a qt find tab in the indicated frame."""
        return leoQtFindTab(c,parentFrame)

    def createLeoFrame(self,title):
        """Create a new Leo frame."""
        gui = self
        return leoQtFrame(title,gui)

    def createSpellTab(self,c,spellHandler,tabName):
        return leoQtSpellTab(c,spellHandler,tabName)

    #@-node:ekr.20081004102201.646:qtGui panels
    #@+node:ekr.20081020075840.14:runAboutLeoDialog
    def runAboutLeoDialog(self,c,version,theCopyright,url,email):

        """Create and run a qt About Leo dialog."""

        if g.unitTesting: return None

        b = QtGui.QMessageBox
        d = b(c.frame.top)

        d.setText('%s\n%s\n%s\n%s' % (
            version,theCopyright,url,email))
        d.setIcon(b.Information)
        yes = d.addButton('Ok',b.YesRole)
        d.setDefaultButton(yes)
        d.exec_()
    #@-node:ekr.20081020075840.14:runAboutLeoDialog
    #@+node:ekr.20081020075840.15:runAskLeoIDDialog
    def runAskLeoIDDialog(self):

        """Create and run a dialog to get g.app.LeoID."""

        if g.unitTesting: return None

        message = (
            "leoID.txt not found\n\n" +
            "Please enter an id that identifies you uniquely.\n" +
            "Your cvs/bzr login name is a good choice.\n\n" +
            "Your id must contain only letters and numbers\n" +
            "and must be at least 3 characters in length.")
        parent = None
        title = 'Enter Leo id'
        s,ok = QtGui.QInputDialog.getText(parent,title,message)
        s = g.toUnicode(s,'utf-8')
        return s
    #@-node:ekr.20081020075840.15:runAskLeoIDDialog
    #@+node:ekr.20081020075840.17:runAskOkDialog
    def runAskOkDialog(self,c,title,message=None,text="Ok"):

        """Create and run a qt an askOK dialog ."""

        if g.unitTesting: return None

        b = QtGui.QMessageBox
        d = b(c.frame.top)

        d.setWindowTitle(title)
        if message: d.setText(message)
        d.setIcon(b.Information)
        yes = d.addButton(text,b.YesRole)
        d.exec_()

    #@-node:ekr.20081020075840.17:runAskOkDialog
    #@+node:ekr.20081020075840.12:runAskYesNoCancelDialog
    def runAskYesNoCancelDialog(self,c,title,
        message=None,
        yesMessage="&Yes",noMessage="&No",defaultButton="Yes"
    ):

        """Create and run an askYesNo dialog."""

        if g.unitTesting: return None

        b = QtGui.QMessageBox

        d = b(c.frame.top)
        if message: d.setText(message)
        d.setIcon(b.Warning)
        d.setWindowTitle(title)
        yes    = d.addButton(yesMessage,b.YesRole)
        no     = d.addButton(noMessage,b.NoRole)
        cancel = d.addButton(b.Cancel)
        if   defaultButton == "Yes": d.setDefaultButton(yes)
        elif defaultButton == "No": d.setDefaultButton(no)
        else: d.setDefaultButton(cancel)
        val = d.exec_()

        if   val == 0: val = 'yes'
        elif val == 1: val = 'no'
        else:          val = 'cancel'
        return val
    #@-node:ekr.20081020075840.12:runAskYesNoCancelDialog
    #@+node:ekr.20081020075840.16:runAskYesNoDialog
    def runAskYesNoDialog(self,c,title,message=None):

        """Create and run an askYesNo dialog."""

        if g.unitTesting: return None

        b = QtGui.QMessageBox
        d = b(c.frame.top)

        d.setWindowTitle(title)
        if message: d.setText(message)
        d.setIcon(b.Information)
        yes = d.addButton('&Yes',b.YesRole)
        no  = d.addButton('&No',b.NoRole)
        d.setDefaultButton(yes)
        val = d.exec_()
        return g.choose(val == 0,'yes','no')

    #@-node:ekr.20081020075840.16:runAskYesNoDialog
    #@+node:ekr.20081004102201.644:runOpenFileDialog
    def runOpenFileDialog(self,title,filetypes,defaultextension,multiple=False):

        """Create and run an Qt open file dialog ."""

        parent = None
        filter = self.makeFilter(filetypes)
        s = QtGui.QFileDialog.getOpenFileName(parent,title,os.curdir,filter)
        return g.toUnicode(s,'utf-8')
    #@nonl
    #@-node:ekr.20081004102201.644:runOpenFileDialog
    #@+node:ekr.20081004102201.645:runSaveFileDialog
    def runSaveFileDialog(self,initialfile,title,filetypes,defaultextension):

        """Create and run an Qt save file dialog ."""

        parent = None
        filter = self.makeFilter(filetypes)
        s = QtGui.QFileDialog.getSaveFileName(parent,title,os.curdir,filter)
        return g.toUnicode(s,'utf-8')
    #@-node:ekr.20081004102201.645:runSaveFileDialog
    #@-node:ekr.20081004102201.640:Dialogs & panels
    #@+node:ekr.20081004102201.657:Focus (qtGui)
    def get_focus(self,c=None):

        """Returns the widget that has focus."""

        w = QtGui.QApplication.focusWidget()
        # g.trace('leoQtGui',w)
        return w

    def set_focus(self,c,w):

        """Put the focus on the widget."""

        if w:
            # g.trace('leoQtGui',w,g.callers(4))
            w.setFocus()
    #@-node:ekr.20081004102201.657:Focus (qtGui)
    #@+node:ekr.20081004102201.660:Font
    #@+node:ekr.20081004102201.661:qtGui.getFontFromParams
    def getFontFromParams(self,family,size,slant,weight,defaultSize=12):

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

        try:
            font = QtGui.QFont(family,size,weight_val,italic)
            # g.trace(family,size,slant,weight,'returns',font)
            return font
        except:
            g.es("exception setting font",g.callers(4))
            g.es("","family,size,slant,weight:","",family,"",size,"",slant,"",weight)
            # g.es_exception() # This just confuses people.
            return g.app.config.defaultFont
    #@-node:ekr.20081004102201.661:qtGui.getFontFromParams
    #@-node:ekr.20081004102201.660:Font
    #@+node:ekr.20081004102201.662:getFullVersion
    def getFullVersion (self,c):

        try:
            qtLevel = 'version %s' % QtCore.QT_VERSION
        except Exception:
            # g.es_exception()
            qtLevel = '<qtLevel>'

        return 'qt %s' % (qtLevel)
    #@-node:ekr.20081004102201.662:getFullVersion
    #@+node:ekr.20081004102201.663:Icons
    #@+node:ekr.20081004102201.664:attachLeoIcon
    def attachLeoIcon (self,window):

        """Attach a Leo icon to the window."""

        icon = self.getIconImage('leoApp.ico')

        window.setWindowIcon(icon)
    #@-node:ekr.20081004102201.664:attachLeoIcon
    #@+node:ekr.20081010070648.12:getIconImage
    def getIconImage (self,name):

        '''Load the icon and return it.'''

        # Return the image from the cache if possible.
        if name in self.iconimages:
            return self.iconimages.get(name)
        try:
            fullname = g.os_path_finalize_join(g.app.loadDir,"..","Icons",name)

            if 0: # Not needed: use QTreeWidget.setIconsize.
                pixmap = QtGui.QPixmap()
                pixmap.load(fullname)
                image = QtGui.QIcon(pixmap)
            else:
                image = QtGui.QIcon(fullname)

            self.iconimages[name] = image
            return image

        except Exception:
            g.es("exception loading:",fullname)
            g.es_exception()
            return None
    #@-node:ekr.20081010070648.12:getIconImage
    #@-node:ekr.20081004102201.663:Icons
    #@+node:ekr.20081004102201.667:Idle Time (to do)
    #@+node:ekr.20081004102201.668:qtGui.setIdleTimeHook
    def setIdleTimeHook (self,idleTimeHookHandler):

        # if self.root:
            # self.root.after_idle(idleTimeHookHandler)

        pass
    #@nonl
    #@-node:ekr.20081004102201.668:qtGui.setIdleTimeHook
    #@+node:ekr.20081004102201.669:setIdleTimeHookAfterDelay
    def setIdleTimeHookAfterDelay (self,idleTimeHookHandler):

        pass

        # if self.root:
            # g.app.root.after(g.app.idleTimeDelay,idleTimeHookHandler)
    #@-node:ekr.20081004102201.669:setIdleTimeHookAfterDelay
    #@-node:ekr.20081004102201.667:Idle Time (to do)
    #@+node:ekr.20081004102201.670:isTextWidget
    def isTextWidget (self,w):

        '''Return True if w is a Text widget suitable for text-oriented commands.'''

        if not w: return False

        return (
            isinstance(w,leoFrame.baseTextWidget) or
            isinstance(w,leoQtBody) or
            isinstance(w,leoQtBaseTextWidget)
        )

    #@-node:ekr.20081004102201.670:isTextWidget
    #@+node:ekr.20081015062931.11:widget_name (qtGui)
    def widget_name (self,w):

        # First try the widget's getName method.
        if not 'w':
            name = '<no widget>'
        elif hasattr(w,'getName'):
            name = w.getName()
        elif hasattr(w,'objectName'):
            name = str(w.objectName())
            # if name == 'treeWidget':
                # name = 'canvas(treeWidget)'
        elif hasattr(w,'_name'):
            name = w._name
        else:
            name = repr(w)

        # g.trace(name,w,g.callers(4))
        return name
    #@-node:ekr.20081015062931.11:widget_name (qtGui)
    #@+node:ekr.20081004102201.671:makeScriptButton (to do)
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
        if p and not buttonText: buttonText = p.headString().strip()
        if not buttonText: buttonText = 'Unnamed Script Button'
        #@    << create the button b >>
        #@+node:ekr.20081004102201.672:<< create the button b >>
        iconBar = c.frame.getIconBarObject()
        b = iconBar.add(text=buttonText)
        #@-node:ekr.20081004102201.672:<< create the button b >>
        #@nl
        #@    << define the callbacks for b >>
        #@+node:ekr.20081004102201.673:<< define the callbacks for b >>
        def deleteButtonCallback(event=None,b=b,c=c):
            if b: b.pack_forget()
            c.bodyWantsFocus()

        def executeScriptCallback (event=None,
            b=b,c=c,buttonText=buttonText,p=p and p.copy(),script=script):

            if c.disableCommandsMessage:
                g.es('',c.disableCommandsMessage,color='blue')
            else:
                g.app.scriptDict = {}
                c.executeScript(args=args,p=p,script=script,
                define_g= define_g,define_name=define_name,silent=silent)
                # Remove the button if the script asks to be removed.
                if g.app.scriptDict.get('removeMe'):
                    g.es("removing","'%s'" % (buttonText),"button at its request")
                    b.pack_forget()
            # Do not assume the script will want to remain in this commander.
        #@-node:ekr.20081004102201.673:<< define the callbacks for b >>
        #@nl
        b.configure(command=executeScriptCallback)
        c.bind(b,'<3>',deleteButtonCallback)
        if shortcut:
            #@        << bind the shortcut to executeScriptCallback >>
            #@+node:ekr.20081004102201.674:<< bind the shortcut to executeScriptCallback >>
            func = executeScriptCallback
            shortcut = k.canonicalizeShortcut(shortcut)
            ok = k.bindKey ('button', shortcut,func,buttonText)
            if ok:
                g.es_print('bound @button',buttonText,'to',shortcut,color='blue')
            #@-node:ekr.20081004102201.674:<< bind the shortcut to executeScriptCallback >>
            #@nl
        #@    << create press-buttonText-button command >>
        #@+node:ekr.20081004102201.675:<< create press-buttonText-button command >>
        aList = [g.choose(ch.isalnum(),ch,'-') for ch in buttonText]

        buttonCommandName = ''.join(aList)
        buttonCommandName = buttonCommandName.replace('--','-')
        buttonCommandName = 'press-%s-button' % buttonCommandName.lower()

        # This will use any shortcut defined in an @shortcuts node.
        k.registerCommand(buttonCommandName,None,executeScriptCallback,pane='button',verbose=False)
        #@-node:ekr.20081004102201.675:<< create press-buttonText-button command >>
        #@nl
    #@-node:ekr.20081004102201.671:makeScriptButton (to do)
    #@-others
#@-node:ekr.20081004102201.631:class leoQtGui
#@-node:ekr.20081109092601.10:Gui wrapper
#@+node:ville.20081011134505.13:Non-essential
#@+node:ville.20081011134505.11:class LeoQuickSearchWidget
import qt_quicksearch

def install_qt_quicksearch_tab(c):
    tabw = c.frame.top.tabWidget
    wdg = LeoQuickSearchWidget(c,tabw)
    tabw.addTab(wdg, "QuickSearch")

g.insqs = install_qt_quicksearch_tab

class LeoQuickSearchWidget(QtGui.QWidget):
    """ Real-time search widget """
    #@    @+others
    #@+node:ville.20081011134505.12:methods
    import qt_quicksearch
    def __init__(self, c, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = qt_quicksearch.Ui_LeoQuickSearchWidget()
        self.ui.setupUi(self)

        self.connect(self.ui.lineEdit,
                    QtCore.SIGNAL("textChanged(const QString&)"),
                      self.textChanged)
        self.connect(self.ui.tableWidget,
                    QtCore.SIGNAL("cellClicked(int, int)"),
                      self.cellClicked)

        self.c = c                  
        self.ps = {} # item=> pos

    def textChanged(self):
        print "New text", self.ui.lineEdit.text()
        idx = 0
        self.ui.tableWidget.clear()
        for p in self.match_headlines(g.toUnicode(self.ui.lineEdit.text(),'utf-8')):
            it = QtGui.QTableWidgetItem(p.headString())
            self.ps[idx] = p.copy()
            self.ui.tableWidget.setItem(idx, 0, it)
            idx+=1

        self.ui.tableWidget.setRowCount(idx)

        print "Matches",idx

    def cellClicked (self, row, column ) :
        p = self.ps[row]
        print "Go to pos",p
        self.c.selectPosition(p)


    def match_headlines(self, pat):

        c = self.c
        pat = pat.lower()
        for p in c.allNodes_iter():
            if pat in p.headString():
                yield p
        return 
    #@-node:ville.20081011134505.12:methods
    #@-others
#@-node:ville.20081011134505.11:class LeoQuickSearchWidget
#@+node:ville.20081014172405.11:quickheadlines
def install_qt_quickheadlines_tab(c):
    global __qh
    __qh = QuickHeadlines(c)

g.insqh = install_qt_quickheadlines_tab

class QuickHeadlines:
    def __init__(self, c):
        self.c = c
        tabw = c.frame.top.tabWidget
        self.listWidget = QtGui.QListWidget(tabw)
        tabw.addTab(self.listWidget, "Headlines")
        c.frame.top.connect(c.frame.top.treeWidget,
          QtCore.SIGNAL("itemSelectionChanged()"), self.req_update)
        self.requested = False
    def req_update(self):
        """ prevent too frequent updates (only one/100 msec) """
        if self.requested:
            return
        QtCore.QTimer.singleShot(100, self.update)
        self.requested = True

    def update(self):

        print "quickheadlines update"
        self.requested = False
        self.listWidget.clear()
        p = self.c.currentPosition()
        for n in p.children_iter():
            self.listWidget.addItem(n.headString())



#@-node:ville.20081014172405.11:quickheadlines
#@-node:ville.20081011134505.13:Non-essential
#@+node:ekr.20081103071436.4:Key handling
#@+node:ekr.20081004102201.676:class leoKeyEvent
class leoKeyEvent:

    '''A gui-independent wrapper for gui events.'''

    def __init__ (self,event,c,w,tkKey):

        # The main ivars.
        self.actualEvent = event
        self.c      = c
        self.char   = tkKey 
        self.keysym = tkKey
        self.w = self.widget = w # A leoQtX object

        # Auxiliary info.
        self.x      = hasattr(event,'x') and event.x or 0
        self.y      = hasattr(event,'y') and event.y or 0
        # Support for fastGotoNode plugin
        self.x_root = hasattr(event,'x_root') and event.x_root or 0
        self.y_root = hasattr(event,'y_root') and event.y_root or 0

    def __repr__ (self):

        return 'qtGui.leoKeyEvent: char: %s, keysym: %s' % (repr(self.char),repr(self.keysym))
#@-node:ekr.20081004102201.676:class leoKeyEvent
#@+node:ekr.20081004102201.628:class leoQtEventFilter
class leoQtEventFilter(QtCore.QObject):

    #@    << about internal bindings >>
    #@+node:ekr.20081007115148.6:<< about internal bindings >>
    #@@nocolor-node
    #@+at
    # 
    # Here are the rules for translating key bindings (in leoSettings.leo) 
    # into keys for k.bindingsDict:
    # 
    # 1.  The case of plain letters is significant:  a is not A.
    # 
    # 2. The Shift- prefix can be applied *only* to letters. Leo will ignore 
    # (with a
    # warning) the shift prefix applied to any other binding, e.g., 
    # Ctrl-Shift-(
    # 
    # 3. The case of letters prefixed by Ctrl-, Alt-, Key- or Shift- is *not*
    # significant. Thus, the Shift- prefix is required if you want an 
    # upper-case
    # letter (with the exception of 'bare' uppercase letters.)
    # 
    # The following table illustrates these rules. In each row, the first 
    # entry is the
    # key (for k.bindingsDict) and the other entries are equivalents that the 
    # user may
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
    # This table is consistent with how Leo already works (because it is 
    # consistent
    # with Tk's key-event specifiers). It is also, I think, the least 
    # confusing set of
    # rules.
    #@-at
    #@nonl
    #@-node:ekr.20081007115148.6:<< about internal bindings >>
    #@nl

    #@    @+others
    #@+node:ekr.20081018155359.10: ctor
    def __init__(self,c,w,tag=''):

        # Init the base class.
        QtCore.QObject.__init__(self)

        self.c = c
        self.w = w      # A leoQtX object, *not* a Qt object.
        self.tag = tag
    #@-node:ekr.20081018155359.10: ctor
    #@+node:ekr.20081013143507.12:eventFilter
    def eventFilter(self, obj, event):

        c = self.c ; k = c.k 
        trace = False ; verbose = True
        eventType = event.type()
        ev = QtCore.QEvent
        kinds = (ev.ShortcutOverride,ev.KeyPress,ev.KeyRelease)

        if eventType in kinds:
            tkKey,ch,ignore = self.toTkKey(event)
            aList = c.k.masterGuiBindingsDict.get('<%s>' %tkKey,[])

            if 0: ### not c.frame.body.useScintilla:
                # Send *all* non-ignored keystrokes to the widget.
                override = not ignore
            elif tkKey == 'Tab':
                override = True
            elif k.inState():
                override = not ignore # allow all keystrokes.
            elif safe_mode:
                override = len(aList) > 0 and not self.isDangerous(tkKey,ch)
            else:
                override = len(aList) > 0
        else:
            override = False ; tkKey = '<no key>'

        if eventType == ev.KeyPress:
            if override:
                w = self.w # Pass the wrapper class, not the wrapped widget.
                stroke = self.toStroke(tkKey,ch)
                leoEvent = leoKeyEvent(event,c,w,stroke)
                ret = k.masterKeyHandler(leoEvent,stroke=stroke)
                c.outerUpdate()
            else:
                if trace: g.trace(self.tag,'unbound',tkKey)

        if trace: self.traceEvent(obj,event,tkKey,override)

        return override
    #@-node:ekr.20081013143507.12:eventFilter
    #@+node:ekr.20081015132934.10:isDangerous
    def isDangerous (self,tkKey,ch):


        c = self.c

        if not c.frame.body.useScintilla: return False

        arrows = ('home','end','left','right','up','down')
        special = ('tab','backspace','period','parenright','parenleft')

        key = tkKey.lower()
        ch = ch.lower()
        isAlt = key.find('alt') > -1
        w = g.app.gui.get_focus()
        inTree = w == self.c.frame.tree.treeWidget

        val = (
            key in special or
            ch in arrows and not inTree and not isAlt or
            key == 'return' and not inTree # Just barely works.
        )

        g.trace(tkKey,ch,val)
        return val
    #@-node:ekr.20081015132934.10:isDangerous
    #@+node:ekr.20081011152302.10:toStroke
    def toStroke (self,tkKey,ch):

        k = self.c.k ; s = tkKey

        special = ('Alt','Ctrl','Control',)
        isSpecial = [True for z in special if s.find(z) > -1]

        if not isSpecial:
            # Keep the Tk spellings for special keys.
            ch2 = k.guiBindNamesInverseDict.get(ch)
            if ch2: s = s.replace(ch,ch2)

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

        # g.trace('tkKey',tkKey,'-->',s)
        return s
    #@-node:ekr.20081011152302.10:toStroke
    #@+node:ekr.20081008084746.1:toTkKey & helpers
    def toTkKey (self,event):

        mods = self.qtMods(event)

        keynum,text,toString,ch = self.qtKey(event)

        tkKey,ch,ignore = self.tkKey(
            event,mods,keynum,text,toString,ch)

        return tkKey,ch,ignore
    #@+node:ekr.20081024164012.10:isFKey
    def isFKey(self,ch):

        return (
            ch and len(ch) in (2,3) and
            ch[0].lower() == 'f' and
            ch[1:].isdigit()
        )
    #@-node:ekr.20081024164012.10:isFKey
    #@+node:ekr.20081028055229.1:qtKey
    def qtKey (self,event):

        '''Return the components of a Qt key event.'''

        keynum = event.key()
        text   = event.text()
        toString = QtGui.QKeySequence(keynum).toString()
        try:
            ch = chr(keynum)
        except ValueError:
            ch = ''
        encoding = 'utf-8'
        ch       = g.toUnicode(ch,encoding)
        text     = g.toUnicode(text,encoding)
        toString = g.toUnicode(toString,encoding)

        return keynum,text,toString,ch


    #@-node:ekr.20081028055229.1:qtKey
    #@+node:ekr.20081028055229.2:qtMods
    def qtMods (self,event):

        modifiers = event.modifiers()

        # The order of this table is significant.
        # It must the order of modifiers in bindings
        # in k.masterGuiBindingsDict

        table = (
            (QtCore.Qt.AltModifier,     'Alt'),
            (QtCore.Qt.ControlModifier, 'Control'),
            (QtCore.Qt.MetaModifier,    'Meta'),
            (QtCore.Qt.ShiftModifier,   'Shift'),
        )

        mods = [b for a,b in table if (modifiers & a)]

        return mods
    #@-node:ekr.20081028055229.2:qtMods
    #@+node:ekr.20081028055229.3:tkKey & helpers
    def tkKey (self,event,mods,keynum,text,toString,ch):

        '''Carefully convert the Qt key to a 
        Tk-style binding compatible with Leo's core
        binding dictionaries.'''

        k = self.c.k ; trace = False ; verbose = True

        special = {
            'Backspace':'BackSpace',
            'Esc':'Escape',
        }

        # Convert '&' to 'ampersand', for example.
        ch2 = k.guiBindNamesDict.get(ch or toString)

        if not ch: ch = ch2
        if not ch: ch = ''

        # Handle special cases.
        ch3 = special.get(toString)
        if ch3: ch = ch3

        ch4 = k.guiBindNamesDict.get(ch)
        if ch4: ch = ch4

        if trace and verbose: g.trace(
    'keynum: %s, mods: %s text: %s, toString: %s, '
    'ch: %s, ch2: %s, ch3: %s, ch4: %s' % (
    keynum,mods,repr(text),toString,
    repr(ch),repr(ch2),repr(ch3),repr(ch4)))

        if 'Shift' in mods:
            mods,ch = self.shifted(mods,ch)
        elif len(ch) == 1:
            ch = ch.lower()

        if 'Alt' in mods and ch and ch in string.digits:
            mods.append('Key')

        tkKey = '%s%s%s' % ('-'.join(mods),mods and '-' or '',ch)
        ignore = not ch

        if trace and (ignore or verbose):
            g.trace('tkKey: %s, ch: %s, ignore: %s' % (
                repr(tkKey),repr(ch),ignore))

        return tkKey,ch,ignore
    #@+node:ekr.20081028055229.16:keyboardUpper1
    def keyboardUpper1 (self,ch):

        '''A horrible, keyboard-dependent hack.

        Return the upper-case version of the given character
        whose original spelling has length == 1.'''

        d = {
            '1':'exclam',
            '2':'at',
            '3':'numbersign',
            '4':'dollar',
            '5':'percent',
            '6':'asciicircum',
            '7':'ampersand',
            '8':'asterisk',
            '9':'parenleft',
            '0':'parenright',
        }

        # g.trace(ch,d.get(ch))
        return d.get(ch)

    #@-node:ekr.20081028055229.16:keyboardUpper1
    #@+node:ekr.20081028055229.17:keyboardUpperLong
    def keyboardUpperLong (self,ch):

        '''A horrible, keyboard-dependent hack.

        Return the upper-case version of the given character
        whose original spelling has length > 1.'''

        d = {
            "quoteleft":    "asciitilde",
            "minus":        "underscore",
            "equal":        "plus",
            "bracketleft":  "braceleft",
            "bracketright": "braceright",
            "semicolon":    "colon",
            "quoteright":   "quotedbl",
            "backslash":    "bar",
            "comma":        "less",
            "period":       "greater",
            "slash":        "question",
        }
        # g.trace(ch,d.get(ch))
        return d.get(ch)
    #@-node:ekr.20081028055229.17:keyboardUpperLong
    #@+node:ekr.20081028055229.14:shifted
    def shifted (self,mods,ch):
        '''
            A horrible, keyboard-dependent kludge.
            return the shifted version of the letter.
            return mods, ch.
        '''

        # Special tk symbols, like '&' have already
        # been converted to names like 'ampersand'.

        # These special characters should be handled in Leo's core.
        noShiftList = ('Return','BackSpace','Tab',)

        special = ('Home','End','Right','Left','Up','Down',)

        if len(ch) == 1:
            ch2 = self.keyboardUpper1(ch)
            if ch2:
                mods.remove('Shift')
                ch = ch2
            elif len(ch) == 1:
                # Correct regardless of alt/ctrl mods.
                mods.remove('Shift')
                ch = ch.upper()
            elif len(mods) == 1: # No alt/ctrl.
                mods.remove('Shift')
            else:
                pass
        else:
            ch3 = self.keyboardUpperLong(ch)
            if ch3: ch = ch3

            if ch3 or ch in noShiftList:
                mods.remove('Shift')
            elif ch in special:
                pass # Allow the shift.
            elif len(mods) == 1: # No alt/ctrl.
                mods.remove('Shift')
            else:
                pass # Retain shift modifier for all special keys.

        return mods,ch
    #@-node:ekr.20081028055229.14:shifted
    #@+node:ekr.20081028134004.11:shifted2
    # This idea doesn't work.  The key-code in the ctor overrides everything else.

    def shifted2 (self,event):

        mods = event.modifiers()
        mods2 = mods & QtCore.Qt.ShiftModifier

        event2 = QtGui.QKeyEvent (
            QtCore.QEvent.KeyPress,
            event.key(),mods2,event.text())

        encoding = 'utf-8'
        keynum = event2.key()
        text   = g.toUnicode(event2.text(),encoding)
        toString = g.toUnicode(QtGui.QKeySequence(keynum).toString(),encoding)
        mods = self.qtMods(event2)

        g.trace(
            'keynum: %s, mods: %s text: %s, toString: %s' % (
            keynum,mods,repr(text),toString))
    #@-node:ekr.20081028134004.11:shifted2
    #@-node:ekr.20081028055229.3:tkKey & helpers
    #@-node:ekr.20081008084746.1:toTkKey & helpers
    #@+node:ekr.20081013143507.11:traceEvent
    def traceEvent (self,obj,event,tkKey,override):

        c = self.c ; e = QtCore.QEvent

        eventType = event.type()


        if 0: # Show focus events.
            show = (
                (e.FocusIn,'focus-in'),(e.FocusOut,'focus-out'),
                (e.Enter,'enter'),(e.Leave,'leave'),
            )

        else:
            show = (
                (e.KeyPress,'key-press'),(e.KeyRelease,'key-release'),
                (e.ShortcutOverride,'shortcut-override'),
            )

        ignore = (
            e.ToolTip,
            e.FocusIn,e.FocusOut,e.Enter,e.Leave,
            e.MetaCall,e.Move,e.Paint,e.Resize,
            e.Polish,e.PolishRequest,
        )

        for val,kind in show:
            if eventType == val:
                g.trace(
                'tag: %s, kind: %s, in-state: %s, key: %s, override: %s' % (
                self.tag,kind,repr(c.k.inState()),tkKey,override))
                return

        # if trace: g.trace(self.tag,
            # 'bound in state: %s, key: %s, returns: %s' % (
            # k.getState(),tkKey,ret))

        if False and eventType not in ignore:
            g.trace('%3s:%s' % (eventType,'unknown'))
    #@-node:ekr.20081013143507.11:traceEvent
    #@-others
#@-node:ekr.20081004102201.628:class leoQtEventFilter
#@-node:ekr.20081103071436.4:Key handling
#@+node:ekr.20081031074959.16:Text widget classes...
#@+node:ekr.20081031074959.12: class leoQtBaseTextWidget
class leoQtBaseTextWidget (leoFrame.baseTextWidget):

    #@    @+others
    #@+node:ekr.20081031074959.20: Birth
    #@+node:ekr.20081031074959.17:ctor (leoQtBaseTextWidget)
    def __init__ (self,widget,name='leoQtBaseTextWidget',c=None):

        self.widget = widget
        self.c = c or self.widget.c

        # Init the base class.
        leoFrame.baseTextWidget.__init__(
            self,c,baseClassName='leoQtBaseTextWidget',
            name=name,
            widget=widget,
            highLevelInterface=True)

        # Init ivars.
        self.tags = {}
        self.useScintilla = False # This is used!

        if not c: return ### Can happen.

        # Hook up qt events.
        self.ev_filter = leoQtEventFilter(c,w=self,tag='body')
        self.widget.installEventFilter(self.ev_filter)

        self.widget.connect(self.widget,
            QtCore.SIGNAL("textChanged()"),self.onTextChanged)

        self.injectIvars(c)
    #@-node:ekr.20081031074959.17:ctor (leoQtBaseTextWidget)
    #@+node:ekr.20081007015817.77:injectIvars
    def injectIvars (self,name='1',parentFrame=None):

        w = self ; p = self.c.currentPosition()

        if name == '1':
            w.leo_p = w.leo_v = None # Will be set when the second editor is created.
        else:

            w.leo_p = p.copy()
            w.leo_v = w.leo_p.v

        w.leo_active = True

        # New in Leo 4.4.4 final: inject the scrollbar items into the text widget.
        w.leo_bodyBar = None ### bodyBar
        w.leo_bodyXBar = None ### bodyXBar
        w.leo_chapter = None
        w.leo_frame = None ### parentFrame
        w.leo_name = name
        w.leo_label = None
        w.leo_label_s = None
        w.leo_scrollBarSpot = None
        w.leo_insertSpot = None
        w.leo_selection = None

        return w
    #@-node:ekr.20081007015817.77:injectIvars
    #@-node:ekr.20081031074959.20: Birth
    #@+node:ekr.20081031074959.15: Do nothings
    def bind (self,stroke,command,**keys):
        pass # eventFilter handles all keys.

    #@-node:ekr.20081031074959.15: Do nothings
    #@+node:ekr.20081031074959.40: Must be defined in base class
    #@+node:ekr.20081004172422.510: Focus
    def getFocus(self):

        g.trace('leoQtBody',self.widget,g.callers(4))
        return g.app.gui.get_focus()

    findFocus = getFocus

    def hasFocus (self):

        val = self.widget == g.app.gui.get_focus(self.c)
        # g.trace('leoQtBody returns',val,self.widget,g.callers(4))
        return val

    def setFocus (self):

        # g.trace('leoQtBody',self.widget,g.callers(4))
        g.app.gui.set_focus(self.c,self.widget)
    #@-node:ekr.20081004172422.510: Focus
    #@+node:ekr.20081007115148.7: Indices
    def toPythonIndex (self,index):

        w = self

        if type(index) == type(99):
            return index
        elif index == '1.0':
            return 0
        elif index == 'end':
            return w.getLastPosition()
        else:
            # g.trace(repr(index))
            s = w.getAllText()
            row,col = index.split('.')
            row,col = int(row),int(col)
            i = g.convertRowColToPythonIndex(s,row,col)
            # g.trace(index,row,col,i,g.callers(6))
            return i

    toGuiIndex = toPythonIndex
    #@-node:ekr.20081007115148.7: Indices
    #@+node:ekr.20081007015817.99: Text getters/settters
    #@+node:ekr.20081007015817.79:appendText
    def appendText(self,s):

        s2 = self.getAllText()
        self.setAllText(s2+s,insert=len(s2))

    #@-node:ekr.20081007015817.79:appendText
    #@+node:ekr.20081008084746.6:delete
    def delete (self,i,j=None):

        w = self.widget
        s = self.getAllText()

        i = self.toGuiIndex(i)
        if j is None: j = i+1
        j = self.toGuiIndex(j)
        if i > j: i,j = j,i

        # g.trace('i',i,'j',j)

        s = s[:i] + s[j:]
        self.setAllText(s,insert=i)

        if i > 0 or j > 0: self.indexWarning('leoQtBody.delete')
        return i
    #@-node:ekr.20081008084746.6:delete
    #@+node:ekr.20081103131824.13:deleteTextSelection
    def deleteTextSelection (self):

        i,j = self.getSelectionRange()
        self.delete(i,j)
    #@-node:ekr.20081103131824.13:deleteTextSelection
    #@+node:ekr.20081007015817.80:get
    def get(self,i,j=None):

        w = self.widget
        s = self.getAllText()
        i = self.toGuiIndex(i)
        if j is None: j = i+1
        j = self.toGuiIndex(j)
        return s[i:j]
    #@-node:ekr.20081007015817.80:get
    #@+node:ekr.20081007015817.84:getLastPosition
    def getLastPosition(self):

        return len(self.getAllText())
    #@-node:ekr.20081007015817.84:getLastPosition
    #@+node:ekr.20081007015817.85:getSelectedText
    def getSelectedText(self):

        w = self.widget

        i,j = self.getSelectionRange()
        if i == j:
            return ''
        else:
            s = self.getAllText()
            # g.trace(repr(s[i:j]))
            return s[i:j]
    #@-node:ekr.20081007015817.85:getSelectedText
    #@+node:ekr.20081007015817.89:insert
    def insert(self,i,s):

        s2 = self.getAllText()
        i = self.toGuiIndex(i)
        self.setAllText(s2[:i] + s + s2[i:],insert=i+len(s))
        return i
    #@-node:ekr.20081007015817.89:insert
    #@+node:ekr.20081008175216.5:selectAllText
    def selectAllText(self,insert=None):

        w = self.widget
        w.selectAll()
        if insert is not None:
            self.setInsertPoint(insert)
        # g.trace('insert',insert)

    #@-node:ekr.20081008175216.5:selectAllText
    #@+node:ekr.20081007015817.96:setSelectionRange
    def setSelectionRange(self,*args,**keys):

        # A kludge to allow a single arg containing i,j
        w = self.widget

        if len(args) == 1:
            i,j = args[0]
        elif len(args) == 2:
            i,j = args
        else:
            g.trace('can not happen',args)
        insert = keys.get('insert')
        i,j = self.toGuiIndex(i),self.toGuiIndex(j)
        if i > j: i,j = j,i

        return self.setSelectionRangeHelper(i,j,insert)

        # g.trace('i',i,'j',j,'insert',insert,g.callers(4))

        # if self.useScintilla:
            # if i > j: i,j = j,i
            # if insert in (j,None):
                # self.setInsertPoint(j)
                # w.SendScintilla(w.SCI_SETANCHOR,i)
            # else:
                # self.setInsertPoint(i)
                # w.SendScintilla(w.SCI_SETANCHOR,j)
        # else:
            # e = QtGui.QTextCursor
            # if i > j: i,j = j,i
            # s = w.toPlainText()
            # i = max(0,min(i,len(s)))
            # j = max(0,min(j,len(s)))
            # k = max(0,min(j-i,len(s)))
            # cursor = w.textCursor()
            # if i == j:
                # cursor.setPosition(i)
            # elif insert in (j,None):
                # cursor.setPosition(i)
                # k = max(0,min(k,len(s)))
                # cursor.movePosition(e.Right,e.KeepAnchor,k)
            # else:
                # cursor.setPosition(j)
                # cursor.movePosition(e.Left,e.KeepAnchor,k)

            # w.setTextCursor(cursor)
    #@-node:ekr.20081007015817.96:setSelectionRange
    #@-node:ekr.20081007015817.99: Text getters/settters
    #@+node:ekr.20081103092019.10:getName (baseTextWidget)
    def getName (self):

        # g.trace('leoQtBaseTextWidget',self.name,g.callers())

        return self.name
    #@-node:ekr.20081103092019.10:getName (baseTextWidget)
    #@+node:ekr.20081011035036.1:onTextChanged
    def onTextChanged (self):

        '''Update Leo after the body has been changed.

        self.selecting is guaranteed to be True during
        the entire selection process.'''

        c = self.c ; p = c.currentPosition()
        tree = c.frame.tree ; w = self
        trace = True ; verbose = False

        if tree.selecting:
            if trace and verbose: g.trace('selecting')
            return
        if tree.redrawing:
            if trace and verbose: g.trace('redrawing')
            return
        if not p:
            return g.trace('*** no p')

        newInsert = w.getInsertPoint()
        newSel = w.getSelectionRange()
        newText = w.getAllText() # Converts to unicode.

        # Get the previous values from the tnode.
        oldText = g.toUnicode(p.v.t._bodyString,"utf-8")
        if oldText == newText:
            # This can happen as the result of undo.
            # g.trace('*** unexpected non-change',color="red")
            return

        if trace and verbose:
            g.trace(p.headString(),len(oldText),len(newText))

        oldIns  = p.v.t.insertSpot
        i,j = p.v.t.selectionStart,p.v.t.selectionLength
        oldSel  = (i,j-i)
        oldYview = None
        undoType = 'Typing'
        c.undoer.setUndoTypingParams(p,undoType,
            oldText=oldText,newText=newText,
            oldSel=oldSel,newSel=newSel,oldYview=oldYview)

        # Update the tnode.
        p.v.setBodyString(newText)
        p.v.t.insertSpot = newInsert
        i,j = newSel
        i,j = self.toGuiIndex(i),self.toGuiIndex(j)
        if i > j: i,j = j,i
        p.v.t.selectionStart,p.v.t.selectionLength = (i,j-i)

        # No need to redraw the screen.
        if not self.useScintilla:
            c.recolor()
        if not c.changed and c.frame.initComplete:
            c.setChanged(True)
        c.frame.body.updateEditors()
        c.frame.tree.updateIcon(p)
        c.outerUpdate()
    #@-node:ekr.20081011035036.1:onTextChanged
    #@+node:ekr.20081016072304.12:indexWarning
    warningsDict = {}

    def indexWarning (self,s):

        return

        # if s not in self.warningsDict:
            # g.es_print('warning: using dubious indices in %s' % (s),color='red')
            # g.es_print('callers',g.callers(5))
            # self.warningsDict[s] = True
    #@-node:ekr.20081016072304.12:indexWarning
    #@-node:ekr.20081031074959.40: Must be defined in base class
    #@+node:ekr.20081031074959.38: May be overridden in subclasses
    def flashCharacter(self,i,bg='white',fg='red',flashes=3,delay=75):
        pass

    def getYScrollPosition(self):
        return None # A flag

    def seeInsertPoint (self):
        self.see(self.getInsertPoint())

    def setYScrollPosition(self,pos):
        pass

    def scrollLines(self,n):
        pass

    #@+node:ekr.20081023113729.1:Configuration
    # Configuration will be handled by style sheets.
    def cget(self,*args,**keys):            return None
    def configure (self,*args,**keys):      pass
    def setBackgroundColor(self,color):     pass
    def setEditorColors (self,bg,fg):       pass
    def setForegroundColor(self,color):     pass
    #@-node:ekr.20081023113729.1:Configuration
    #@+node:ekr.20081004172422.516:Idle time
    def after_idle(self,func,threadCount):
        # g.trace(func.__name__,'threadCount',threadCount)
        return func(threadCount)

    def after(self,n,func,threadCount):
        def after_callback(func=func,threadCount=threadCount):
            # g.trace(func.__name__,threadCount)
            return func(threadCount)
        QtCore.QTimer.singleShot(n,after_callback)

    def scheduleIdleTimeRoutine (self,function,*args,**keys):
        g.trace()
        # if not g.app.unitTesting:
            # self.widget.after_idle(function,*args,**keys)
    #@-node:ekr.20081004172422.516:Idle time
    #@+node:ekr.20081023131208.10:Coloring
    # These are body methods.
    # def forceFullRecolor (self): pass
    # def update_idletasks(self):  pass

    def removeAllTags(self):
        s = self.getAllText()
        self.colorSelection(0,len(s),'black')

    def tag_add(self,tag,x1,x2):
        if tag == 'comment1':
            self.colorSelection(x1,x2,'firebrick')

    def tag_config (self,*args,**keys):
        if len(args) == 1:
            key = args[0]
            # g.trace(key,keys)
            self.tags[key] = keys
        else:
            g.trace('oops',args,keys)

    tag_configure = tag_config

    def tag_names (self):
        return []
    #@+node:ekr.20081029084058.10:colorSelection
    def colorSelection (self,i,j,colorName):

        w = self.widget
        color = QtGui.QColor(colorName)
        sb = w.verticalScrollBar()
        pos = sb.sliderPosition()
        old_i,old_j = self.getSelectionRange()
        old_ins = self.getInsertPoint()
        self.setSelectionRange(i,j)
        w.setTextColor(color)
        self.setSelectionRange(old_i,old_j,insert=old_ins)
        sb.setSliderPosition(pos)
    #@-node:ekr.20081029084058.10:colorSelection
    #@-node:ekr.20081023131208.10:Coloring
    #@-node:ekr.20081031074959.38: May be overridden in subclasses
    #@+node:ekr.20081031074959.29: Must be overridden in subclasses
    #@+node:ekr.20081007015817.81:getAllText
    def getAllText(self):

        self.oops()

        # w = self.widget

        # if self.useScintilla:
            # s = w.text()
        # else:
            # s = w.toPlainText()

        # s = g.toUnicode(s,'utf-8')
        # return s
    #@-node:ekr.20081007015817.81:getAllText
    #@+node:ekr.20081007015817.83:getInsertPoint
    def getInsertPoint(self):

        self.oops()

        # w = self.widget
        # if self.useScintilla:
            # s = self.getAllText()
            # row,col = w.getCursorPosition()  
            # i = g.convertRowColToPythonIndex(s, row, col)
            # if i > 0: self.indexWarning('leoQtBody.getInsertPoint')
            # return i
        # else:
            # i = w.textCursor().position()
            # # g.trace(i) # ,g.callers(4))
            # return i
    #@-node:ekr.20081007015817.83:getInsertPoint
    #@+node:ekr.20081007015817.86:getSelectionRange
    def getSelectionRange(self,sort=True):

        self.oops()

        # w = self.widget
        # if self.useScintilla:
            # if w.hasSelectedText():
                # s = self.getAllText()
                # row_i,col_i,row_j,col_j = w.getSelection()
                # i = g.convertRowColToPythonIndex(s, row_i, col_i)
                # j = g.convertRowColToPythonIndex(s, row_j, col_j)
                # if sort and i > j: sel = j,i
            # else:
                # i = j = self.getInsertPoint()
            # if i > 0 or j > 0: self.indexWarning('leoQtBody.getSelectionRange')
            # return i,j
        # else:
            # tc = w.textCursor()
            # i,j = tc.selectionStart(),tc.selectionEnd()
            # # g.trace(i,j,g.callers(4))
            # return i,j
    #@-node:ekr.20081007015817.86:getSelectionRange
    #@+node:ville.20081011134505.6:hasSelection
    def hasSelection(self):

        self.oops()

        # w = self.widget
        # if self.useScintilla:
            # return w.hasSelectedText()
        # else:
            # return w.textCursor().hasSelection()
    #@-node:ville.20081011134505.6:hasSelection
    #@+node:ekr.20081031074959.46:see
    def see(self,i):

        self.oops()

        # w = self.widget

        # if self.useScintilla:
            # # Ok for now.  Using SCI_SETYCARETPOLICY might be better.
            # s = self.getAllText()
            # row,col = g.convertPythonIndexToRowCol(s,i)
            # w.ensureLineVisible(row)
        # else:
            # w.ensureCursorVisible()
    #@-node:ekr.20081031074959.46:see
    #@+node:ekr.20081007015817.92:setAllText
    def setAllText(self,s,insert=None):

        '''Set the text of the widget.

        If insert is None, the insert point, selection range and scrollbars are initied.
        Otherwise, the scrollbars are preserved.'''

        self.oops()

        # w = self.widget ; c = self.c ; p = c.currentPosition()

        # if self.useScintilla:
            # w.setText(s)
        # else:
            # # g.trace('len(s)',len(s),p and p.headString())
            # sb = w.verticalScrollBar()
            # if insert is None: i,pos = 0,0
            # else: i,pos = insert,sb.sliderPosition()
            # w.setPlainText(s)
            # self.setSelectionRange(i,i,insert=i)
            # sb.setSliderPosition(pos)
    #@-node:ekr.20081007015817.92:setAllText
    #@+node:ekr.20081007015817.95:setInsertPoint
    def setInsertPoint(self,i):

        self.oops()

        # w = self.widget
        # if self.useScintilla:
            # w.SendScintilla(w.SCI_SETCURRENTPOS,i)
            # w.SendScintilla(w.SCI_SETANCHOR,i)
        # else:
            # # g.trace(i) # ,g.callers(4))
            # s = w.toPlainText()
            # cursor = w.textCursor()
            # i = max(0,min(i,len(s)))
            # cursor.setPosition(i)
            # w.setTextCursor(cursor)
    #@-node:ekr.20081007015817.95:setInsertPoint
    #@-node:ekr.20081031074959.29: Must be overridden in subclasses
    #@-others
#@-node:ekr.20081031074959.12: class leoQtBaseTextWidget
#@+node:ekr.20081101134906.13: class leoQLineEditWidget
class leoQLineEditWidget (leoQtBaseTextWidget):

    #@    @+others
    #@+node:ekr.20081101134906.14:Birth
    #@+node:ekr.20081101134906.15:ctor
    def __init__ (self,widget,name,c=None):

        # Init the base class.
        leoQtBaseTextWidget.__init__(self,widget,name,c=c)

        self.baseClassName='leoQLineEditWidget'

        # g.trace('leoQLineEditWidget',id(widget),g.callers(4))

        self.setConfig()
        self.setFontFromConfig()
        self.setColorFromConfig()
    #@-node:ekr.20081101134906.15:ctor
    #@+node:ekr.20081101134906.16:setFontFromConfig
    def setFontFromConfig (self,w=None):

        '''Set the font in the widget w (a body editor).'''

        return

        # c = self.c
        # if not w: w = self.widget

        # font = c.config.getFontFromParams(
            # "head_text_font_family", "head_text_font_size",
            # "head_text_font_slant",  "head_text_font_weight",
            # c.config.defaultBodyFontSize)

        # self.fontRef = font # ESSENTIAL: retain a link to font.
        # # w.configure(font=font)

        # # g.trace("BODY",body.cget("font"),font.cget("family"),font.cget("weight"))
    #@-node:ekr.20081101134906.16:setFontFromConfig
    #@+node:ekr.20081101134906.17:setColorFromConfig
    def setColorFromConfig (self,w=None):

        '''Set the font in the widget w (a body editor).'''

        return

        # c = self.c
        # if w is None: w = self.widget

        # bg = c.config.getColor("body_text_background_color") or 'white'
        # try:
            # pass ### w.configure(bg=bg)
        # except:
            # g.es("exception setting body text background color")
            # g.es_exception()

        # fg = c.config.getColor("body_text_foreground_color") or 'black'
        # try:
            # pass ### w.configure(fg=fg)
        # except:
            # g.es("exception setting body textforeground color")
            # g.es_exception()

        # bg = c.config.getColor("body_insertion_cursor_color")
        # if bg:
            # try:
                # pass ### w.configure(insertbackground=bg)
            # except:
                # g.es("exception setting body pane cursor color")
                # g.es_exception()

        # sel_bg = c.config.getColor('body_text_selection_background_color') or 'Gray80'
        # try:
            # pass ### w.configure(selectbackground=sel_bg)
        # except Exception:
            # g.es("exception setting body pane text selection background color")
            # g.es_exception()

        # sel_fg = c.config.getColor('body_text_selection_foreground_color') or 'white'
        # try:
            # pass ### w.configure(selectforeground=sel_fg)
        # except Exception:
            # g.es("exception setting body pane text selection foreground color")
            # g.es_exception()

        # # if sys.platform != "win32": # Maybe a Windows bug.
            # # fg = c.config.getColor("body_cursor_foreground_color")
            # # bg = c.config.getColor("body_cursor_background_color")
            # # if fg and bg:
                # # cursor="xterm" + " " + fg + " " + bg
                # # try:
                    # # pass ### w.configure(cursor=cursor)
                # # except:
                    # # import traceback ; traceback.print_exc()
    #@-node:ekr.20081101134906.17:setColorFromConfig
    #@+node:ekr.20081101134906.18:setConfig
    def setConfig (self):
        pass
    #@nonl
    #@-node:ekr.20081101134906.18:setConfig
    #@-node:ekr.20081101134906.14:Birth
    #@+node:ekr.20081101134906.19:Widget-specific overrides (QLineEdit)
    #@+node:ekr.20081101134906.20:getAllText
    def getAllText(self):

        w = self.widget
        s = w.text()
        s = g.toUnicode(s,'utf-8')
        # g.trace(repr(s))
        return s
    #@-node:ekr.20081101134906.20:getAllText
    #@+node:ekr.20081101134906.21:getInsertPoint
    def getInsertPoint(self):

        i = self.widget.cursorPosition()
        # g.trace(i)
        return i
    #@-node:ekr.20081101134906.21:getInsertPoint
    #@+node:ekr.20081101134906.22:getSelectionRange
    def getSelectionRange(self,sort=True):

        w = self.widget

        if w.hasSelectedText():
            i = w.selectionStart()
            s = w.selectedText()
            s = g.toUnicode(s,'utf-8')
            j = i + len(s)
        else:
            i = j = w.cursorPosition()

        # g.trace(i,j)
        return i,j
    #@-node:ekr.20081101134906.22:getSelectionRange
    #@+node:ekr.20081101134906.23:hasSelection
    def hasSelection(self):

        return self.widget.hasSelection()
    #@-node:ekr.20081101134906.23:hasSelection
    #@+node:ekr.20081101134906.24:see & seeInsertPoint
    def see(self,i):
        pass

    def seeInsertPoint (self):
        pass
    #@-node:ekr.20081101134906.24:see & seeInsertPoint
    #@+node:ekr.20081101134906.25:setAllText
    def setAllText(self,s,insert=None):

        w = self.widget
        i = g.choose(insert is None,0,insert)
        w.setText(s)
        if insert is not None:
            self.setSelectionRange(i,i,insert=i)

        # g.trace(i,repr(s))
    #@-node:ekr.20081101134906.25:setAllText
    #@+node:ekr.20081101134906.26:setInsertPoint
    def setInsertPoint(self,i):

        w = self.widget
        s = w.text()
        s = g.toUnicode(s,'utf-8')
        i = max(0,min(i,len(s)))
        w.setCursorPosition(i)
    #@-node:ekr.20081101134906.26:setInsertPoint
    #@+node:ekr.20081101134906.27:setSelectionRangeHelper
    def setSelectionRangeHelper(self,i,j,insert):

        w = self.widget
        # g.trace('i',i,'j',j,'insert',insert,g.callers(4))
        if i > j: i,j = j,i
        s = w.text()
        s = g.toUnicode(s,'utf-8')
        i = max(0,min(i,len(s)))
        j = max(0,min(j,len(s)))
        k = max(0,min(j-i,len(s)))
        if i == j:
            w.setCursorPosition(i)
        else:
            w.setSelection(i,k)
    #@-node:ekr.20081101134906.27:setSelectionRangeHelper
    #@-node:ekr.20081101134906.19:Widget-specific overrides (QLineEdit)
    #@-others
#@-node:ekr.20081101134906.13: class leoQLineEditWidget
#@+node:ekr.20081031074959.11: class leoQScintillaWidget
class leoQScintillaWidget (leoQtBaseTextWidget):

    #@    @+others
    #@+node:ekr.20081031074959.21:Birth
    #@+node:ekr.20081031074959.22:ctor
    def __init__ (self,widget,name,c=None):

        # Init the base class.
        leoQtBaseTextWidget.__init__(self,widget,name,c=c)

        self.baseClassName='leoQScintillaWidget'

        self.useScintilla = True
        self.setConfig()
    #@-node:ekr.20081031074959.22:ctor
    #@+node:ekr.20081023060109.11:setConfig
    def setConfig (self):

        c = self.c ; w = self.widget
        tag = 'qt-scintilla-styles'
        qcolor,qfont = QtGui.QColor,QtGui.QFont

        def oops(s): g.trace('bad @data %s: %s' % (tag,s))

        # To do: make this configurable the leo way
        if 0: # Suppress lexing.
            w.setLexer()
            lexer = w.lexer()
        else:
            lexer = Qsci.QsciLexerPython(w)
            # A small font size, to be magnified.
            font = qfont("Courier New",8,qfont.Bold)
            lexer.setFont(font)
            table = None
            aList = c.config.getData('qt-scintilla-styles')
            if aList:
                aList = [s.split(',') for s in aList]
                table = []
                for z in aList:
                    if len(z) == 2:
                        color,style = z
                        table.append((color.strip(),style.strip()),)
                    else: oops('entry: %s' % z)
                # g.trace(g.printList(table))

            if not table:
                table = (
                    ('red','Comment'),
                    ('green','SingleQuotedString'),
                    ('green','DoubleQuotedString'),
                    ('green','TripleSingleQuotedString'),
                    ('green','TripleDoubleQuotedString'),
                    ('green','UnclosedString'),
                    ('blue','Keyword'),
                )
            for color,style in table:
                if hasattr(lexer,style):
                    style = getattr(lexer,style)
                    try:
                        lexer.setColor(qcolor(color),style)
                    except Exception:
                        oops('bad color: %s' % color)
                else: oops('bad style: %s' % style)

        w.setLexer(lexer)

        n = c.config.getInt('qt-scintilla-zoom-in')
        if n not in (None,0): w.zoomIn(n)

        w.setIndentationWidth(4)
        w.setIndentationsUseTabs(False)
        w.setAutoIndent(True)
    #@-node:ekr.20081023060109.11:setConfig
    #@-node:ekr.20081031074959.21:Birth
    #@+node:ekr.20081031074959.25:Widget-specific overrides (QScintilla)
    #@+node:ekr.20081031074959.41:getAllText
    def getAllText(self):

        w = self.widget
        s = w.text()
        s = g.toUnicode(s,'utf-8')
        return s
    #@-node:ekr.20081031074959.41:getAllText
    #@+node:ekr.20081031074959.26:getInsertPoint
    def getInsertPoint(self):

        w = self.widget
        s = self.getAllText()
        row,col = w.getCursorPosition()  
        i = g.convertRowColToPythonIndex(s, row, col)
        return i
    #@-node:ekr.20081031074959.26:getInsertPoint
    #@+node:ekr.20081031074959.30:getSelectionRange
    def getSelectionRange(self,sort=True):

        w = self.widget

        if w.hasSelectedText():
            s = self.getAllText()
            row_i,col_i,row_j,col_j = w.getSelection()
            i = g.convertRowColToPythonIndex(s, row_i, col_i)
            j = g.convertRowColToPythonIndex(s, row_j, col_j)
            if sort and i > j: sel = j,i
        else:
            i = j = self.getInsertPoint()

        return i,j

    #@-node:ekr.20081031074959.30:getSelectionRange
    #@+node:ekr.20081031074959.32:hasSelection
    def hasSelection(self):

        return self.widget.hasSelectedText()
    #@-node:ekr.20081031074959.32:hasSelection
    #@+node:ekr.20081031074959.47:see
    def see(self,i):

        # Ok for now.  Using SCI_SETYCARETPOLICY might be better.
        w = self.widget
        s = self.getAllText()
        row,col = g.convertPythonIndexToRowCol(s,i)
        w.ensureLineVisible(row)

    # Use base-class method for seeInsertPoint.
    #@nonl
    #@-node:ekr.20081031074959.47:see
    #@+node:ekr.20081031074959.44:setAllText
    def setAllText(self,s,insert=None):

        '''Set the text of the widget.

        If insert is None, the insert point, selection range and scrollbars are initied.
        Otherwise, the scrollbars are preserved.'''

        w = self.widget
        w.setText(s)

    #@-node:ekr.20081031074959.44:setAllText
    #@+node:ekr.20081031074959.35:setInsertPoint
    def setInsertPoint(self,i):

        w = self.widget
        w.SendScintilla(w.SCI_SETCURRENTPOS,i)
        w.SendScintilla(w.SCI_SETANCHOR,i)
    #@-node:ekr.20081031074959.35:setInsertPoint
    #@+node:ekr.20081031074959.39:setSelectionRangeHelper
    def setSelectionRangeHelper(self,i,j,insert):

        w = self.widget

        # g.trace('i',i,'j',j,'insert',insert,g.callers(4))

        if insert in (j,None):
            self.setInsertPoint(j)
            w.SendScintilla(w.SCI_SETANCHOR,i)
        else:
            self.setInsertPoint(i)
            w.SendScintilla(w.SCI_SETANCHOR,j)
    #@-node:ekr.20081031074959.39:setSelectionRangeHelper
    #@-node:ekr.20081031074959.25:Widget-specific overrides (QScintilla)
    #@-others
#@-node:ekr.20081031074959.11: class leoQScintillaWidget
#@+node:ekr.20081031074959.10: class leoQTextEditWidget
class leoQTextEditWidget (leoQtBaseTextWidget):

    #@    @+others
    #@+node:ekr.20081031074959.23:Birth
    #@+node:ekr.20081031074959.24:ctor
    def __init__ (self,widget,name,c=None):

        # Init the base class.
        leoQtBaseTextWidget.__init__(self,widget,name,c=c)

        self.baseClassName='leoQTextEditWidget'

        widget.setUndoRedoEnabled(False)

        self.setConfig()
        self.setFontFromConfig()
        self.setColorFromConfig()
    #@-node:ekr.20081031074959.24:ctor
    #@+node:ekr.20081004172422.509:setFontFromConfig
    def setFontFromConfig (self,w=None):

        '''Set the font in the widget w (a body editor).'''

        c = self.c
        if not w: w = self.widget

        font = c.config.getFontFromParams(
            "body_text_font_family", "body_text_font_size",
            "body_text_font_slant",  "body_text_font_weight",
            c.config.defaultBodyFontSize)

        self.fontRef = font # ESSENTIAL: retain a link to font.
        # w.configure(font=font)

        # g.trace("BODY",body.cget("font"),font.cget("family"),font.cget("weight"))
    #@-node:ekr.20081004172422.509:setFontFromConfig
    #@+node:ekr.20081004172422.508:setColorFromConfig
    def setColorFromConfig (self,w=None):

        '''Set the font in the widget w (a body editor).'''

        c = self.c
        if w is None: w = self.widget

        bg = c.config.getColor("body_text_background_color") or 'white'
        try:
            pass ### w.configure(bg=bg)
        except:
            g.es("exception setting body text background color")
            g.es_exception()

        fg = c.config.getColor("body_text_foreground_color") or 'black'
        try:
            pass ### w.configure(fg=fg)
        except:
            g.es("exception setting body textforeground color")
            g.es_exception()

        bg = c.config.getColor("body_insertion_cursor_color")
        if bg:
            try:
                pass ### w.configure(insertbackground=bg)
            except:
                g.es("exception setting body pane cursor color")
                g.es_exception()

        sel_bg = c.config.getColor('body_text_selection_background_color') or 'Gray80'
        try:
            pass ### w.configure(selectbackground=sel_bg)
        except Exception:
            g.es("exception setting body pane text selection background color")
            g.es_exception()

        sel_fg = c.config.getColor('body_text_selection_foreground_color') or 'white'
        try:
            pass ### w.configure(selectforeground=sel_fg)
        except Exception:
            g.es("exception setting body pane text selection foreground color")
            g.es_exception()

        # if sys.platform != "win32": # Maybe a Windows bug.
            # fg = c.config.getColor("body_cursor_foreground_color")
            # bg = c.config.getColor("body_cursor_background_color")
            # if fg and bg:
                # cursor="xterm" + " " + fg + " " + bg
                # try:
                    # pass ### w.configure(cursor=cursor)
                # except:
                    # import traceback ; traceback.print_exc()
    #@-node:ekr.20081004172422.508:setColorFromConfig
    #@+node:ekr.20081023060109.12:setConfig
    def setConfig (self):

        c = self.c ; w = self.widget

        n = c.config.getInt('qt-rich-text-zoom-in')

        w.setWordWrapMode(QtGui.QTextOption.NoWrap)

        # w.zoomIn(1)
        # w.updateMicroFocus()
        if n not in (None,0):
            # This only works when there is no style sheet.
            # g.trace('zoom-in',n)
            w.zoomIn(n)
            w.updateMicroFocus()
    #@-node:ekr.20081023060109.12:setConfig
    #@-node:ekr.20081031074959.23:Birth
    #@+node:ekr.20081031074959.27:Widget-specific overrides (QTextEdit)
    #@+node:ekr.20081024163213.12:flashCharacter
    def flashCharacter(self,i,bg='white',fg='red',flashes=3,delay=75):

        c = self.c ; w = self.widget

        # Reduce the flash time to the minimum.
        flashes = max(1,min(2,flashes))
        flashes = 1
        delay = max(10,min(50,delay))

        def after(func):
            QtCore.QTimer.singleShot(delay,func)

        def addFlashCallback(self=self,w=w):
            n,i = self.flashCount,self.flashIndex
            # g.trace(n)
            self.setSelectionRange(i,i+1)
            self.flashCount -= 1
            after(removeFlashCallback)

        def removeFlashCallback(self=self,w=w):
            n,i = self.flashCount,self.flashIndex
            self.setSelectionRange(i,i)
            if n > 0:
                after(addFlashCallback)
            else:
                w.blockSignals(False)
                w.setDisabled(False)
                self.setInsertPoint(self.afterFlashIndex)
                w.setFocus()

        self.flashCount = flashes
        self.flashIndex = i
        self.afterFlashIndex = self.getInsertPoint()
        w.setDisabled(True)
        w.blockSignals(True)
        addFlashCallback()
    #@-node:ekr.20081024163213.12:flashCharacter
    #@+node:ekr.20081031074959.42:getAllText
    def getAllText(self):

        w = self.widget
        s = w.toPlainText()
        s = g.toUnicode(s,'utf-8')
        return s
    #@-node:ekr.20081031074959.42:getAllText
    #@+node:ekr.20081031074959.28:getInsertPoint
    def getInsertPoint(self):

        return self.widget.textCursor().position()
    #@-node:ekr.20081031074959.28:getInsertPoint
    #@+node:ekr.20081031074959.31:getSelectionRange
    def getSelectionRange(self,sort=True):

        w = self.widget
        tc = w.textCursor()
        i,j = tc.selectionStart(),tc.selectionEnd()
        # g.trace(i,j,g.callers(4))
        return i,j
    #@nonl
    #@-node:ekr.20081031074959.31:getSelectionRange
    #@+node:ekr.20081031074959.36:getYScrollPosition
    def getYScrollPosition(self):

        w = self.widget
        sb = w.verticalScrollBar()
        i = sb.sliderPosition()

        # Return a tuple, only the first of which is used.
        return i,i 
    #@-node:ekr.20081031074959.36:getYScrollPosition
    #@+node:ekr.20081031074959.33:hasSelection
    def hasSelection(self):

        return self.widget.textCursor().hasSelection()
    #@-node:ekr.20081031074959.33:hasSelection
    #@+node:ekr.20081031074959.48:see
    def see(self,i):

        self.widget.ensureCursorVisible()
    #@nonl
    #@-node:ekr.20081031074959.48:see
    #@+node:ekr.20081031074959.50:seeInsertPoint
    def seeInsertPoint (self):

        self.widget.ensureCursorVisible()
    #@-node:ekr.20081031074959.50:seeInsertPoint
    #@+node:ekr.20081031074959.45:setAllText
    def setAllText(self,s,insert=None):

        '''Set the text of the widget.

        If insert is None, the insert point, selection range and scrollbars are initied.
        Otherwise, the scrollbars are preserved.'''

        w = self.widget
        # g.trace('len(s)',len(s),p and p.headString())
        sb = w.verticalScrollBar()
        if insert is None: i,pos = 0,0
        else: i,pos = insert,sb.sliderPosition()
        w.setPlainText(s)
        self.setSelectionRange(i,i,insert=i)
        sb.setSliderPosition(pos)
    #@-node:ekr.20081031074959.45:setAllText
    #@+node:ekr.20081031074959.37:setInsertPoint
    def setInsertPoint(self,i):

        w = self.widget
        s = w.toPlainText()
        cursor = w.textCursor()
        i = max(0,min(i,len(s)))
        cursor.setPosition(i)
        w.setTextCursor(cursor)
    #@-node:ekr.20081031074959.37:setInsertPoint
    #@+node:ekr.20081031074959.43:setSelectionRangeHelper & helper
    def setSelectionRangeHelper(self,i,j,insert):

        w = self.widget
        # g.trace('i',i,'j',j,'insert',insert,g.callers(4))
        e = QtGui.QTextCursor
        if i > j: i,j = j,i
        n = self.lengthHelper()
        # s = w.toPlainText() ; n = len(s)
        i = max(0,min(i,n))
        j = max(0,min(j,n))
        k = max(0,min(j-i,n))
        cursor = w.textCursor()
        if i == j:
            cursor.setPosition(i)
        elif insert in (j,None):
            cursor.setPosition(i)
            cursor.movePosition(e.Right,e.KeepAnchor,k)
        else:
            cursor.setPosition(j)
            cursor.movePosition(e.Left,e.KeepAnchor,k)

        w.setTextCursor(cursor)
    #@+node:ekr.20081104103442.1:lengthHelper
    def lengthHelper(self):

        '''Return the length of the text.'''

        w = self.widget
        cursor = w.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        n = cursor.position()

        # Check.
        # s = w.toPlainText()
        # s = g.toUnicode(s,'utf-8')
        # n2 = len(s)
        # if n != n2:
            # g.trace('mismatch',n,n2)
            # return n2

        return n



    #@-node:ekr.20081104103442.1:lengthHelper
    #@-node:ekr.20081031074959.43:setSelectionRangeHelper & helper
    #@+node:ekr.20081025124450.12:setYScrollPosition
    def setYScrollPosition(self,pos):

        w = self.widget
        sb = w.verticalScrollBar()
        if pos is None: pos = 0
        elif type(pos) == types.TupleType:
            pos = pos[0]
        sb.setSliderPosition(pos)
    #@-node:ekr.20081025124450.12:setYScrollPosition
    #@-node:ekr.20081031074959.27:Widget-specific overrides (QTextEdit)
    #@-others
#@-node:ekr.20081031074959.10: class leoQTextEditWidget
#@+node:ekr.20081103092019.11:class leoQtHeadlineWidget
class leoQtHeadlineWidget (leoQLineEditWidget):

    pass
#@-node:ekr.20081103092019.11:class leoQtHeadlineWidget
#@+node:ekr.20081018130812.12:class findTextWrapper
class findTextWrapper (leoQLineEditWidget):

    '''A class representing the find/change edit widgets.'''

    pass
#@-node:ekr.20081018130812.12:class findTextWrapper
#@+node:ekr.20081017015442.12:class leoQtMinibuffer (leoQLineEditWidget)
class leoQtMinibuffer (leoQLineEditWidget):

    def __init__ (self,c):
        self.c = c
        w = c.frame.top.ui.lineEdit # QLineEdit
        # Init the base class.
        leoQLineEditWidget.__init__(self,widget=w,name='minibuffer',c=c)

        self.ev_filter = leoQtEventFilter(c,w=self,tag='minibuffer')
        w.installEventFilter(self.ev_filter)

    def setBackgroundColor(self,color):
        self.widget.setStyleSheet('background-color:%s' % color)

    def setForegroundColor(self,color):
        pass
#@-node:ekr.20081017015442.12:class leoQtMinibuffer (leoQLineEditWidget)
#@-node:ekr.20081031074959.16:Text widget classes...
#@-others
#@-node:ekr.20081004102201.619:@thin qtGui.py
#@-leo
