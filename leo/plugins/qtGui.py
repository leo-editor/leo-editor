# -*- coding: utf-8 -*-
#@+leo-ver=4-thin
#@+node:ekr.20081121105001.188:@thin qtGui.py
#@@first

'''qt gui plugin.'''

#@@language python
#@@tabwidth -4
#@@pagewidth 80

safe_mode = False # True: Bypass k.masterKeyHandler for problem keys or visible characters.

useQSyntaxHighlighter = True

# Define these to suppress pylint warnings...
__timing = None # For timing stats.
__qh = None # For quick headlines.

#@<< qt imports >>
#@+node:ekr.20081121105001.189: << qt imports >>
import leo.core.leoGlobals as g

import leo.core.leoChapters as leoChapters
import leo.core.leoColor as leoColor
import leo.core.leoFrame as leoFrame
import leo.core.leoFind as leoFind
import leo.core.leoGui as leoGui
import leo.core.leoKeys as leoKeys
import leo.core.leoMenu as leoMenu

import re
import string

import os
import re # For colorizer
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
    print('qtGui.py: can not import Qt')
#@-node:ekr.20081121105001.189: << qt imports >>
#@nl

#@+at
# Notes:
# 1. All leoQtX classes are two-way adapator classes
#@-at
#@@c

#@+others
#@+node:ekr.20081121105001.190: Module level

#@+node:ekr.20081121105001.191:init
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
#@-node:ekr.20081121105001.191:init
#@+node:ekr.20081121105001.192:embed_ipython
def embed_ipython():

    import IPython.ipapi

    # sys.argv = ['ipython', '-p' , 'sh']
    # ses = IPython.ipapi.make_session(dict(w = window))
    # ip = ses.IP.getapi()
    # ip.load('ipy_leo')
    # ses.mainloop()
#@nonl
#@-node:ekr.20081121105001.192:embed_ipython
#@+node:ekr.20081121105001.193:tstart & tstop
def tstart():
    global __timing
    __timing = time.time()

def tstop():
    g.trace("%s Time: %1.2fsec" % (
        g.callers(1),time.time()-__timing))
#@-node:ekr.20081121105001.193:tstart & tstop
#@-node:ekr.20081121105001.190: Module level
#@+node:ekr.20081121105001.194:Frame and component classes...
#@+node:ekr.20081121105001.200:class  DynamicWindow
from PyQt4 import uic

class DynamicWindow(QtGui.QMainWindow):

    '''A class representing all parts of the main Qt window
    as created by Designer.

    c.frame.top is a Window object.

    All leoQtX classes use the ivars of this Window class to
    support operations requested by Leo's core.
    '''

    #@    @+others
    #@+node:ekr.20081121105001.201: ctor (Window)
    # Called from leoQtFrame.finishCreate.

    def __init__(self,c,parent=None):

        '''Create Leo's main window, c.frame.top'''

        self.c = c ; top = c.frame.top
        # g.trace('DynamicWindow')

        # Init both base classes.

        ui_file_name = c.config.getString('qt_ui_file_name')
        for f in (ui_file_name, 'qt_main.ui', None):
            assert f, "can not find user interface file"
            ui_description_file = g.app.loadDir + "/../plugins/" + f
            g.pr(ui_description_file)
            if g.os_path_exists(ui_description_file): break

        QtGui.QMainWindow.__init__(self,parent)        
        self.ui = uic.loadUi(ui_description_file, self)

        # Init the QDesigner elements.
        #self.setupUi(self)

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

        orientation = c.config.getString('initial_split_orientation')
        self.setSplitDirection(orientation)
        self.setStyleSheets()
    #@-node:ekr.20081121105001.201: ctor (Window)
    #@+node:leohag.20081203210510.17:do_leo_spell_btn_*
    def do_leo_spell_btn_Add(self):
        g.trace()

    def do_leo_spell_btn_Change(self):
        g.trace()

    def do_leo_spell_btn_Find(self):
        g.trace()

    def do_leo_spell_btn_FindChange(self):
        g.trace()

    def do_leo_spell_btn_Hide(self):
        g.trace()

    def do_leo_spell_btn_Ignore(self):
        g.trace()

    #@-node:leohag.20081203210510.17:do_leo_spell_btn_*
    #@+node:ekr.20081121105001.202:closeEvent (qtFrame)
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
    #@-node:ekr.20081121105001.202:closeEvent (qtFrame)
    #@+node:edward.20081129091117.1:setSplitDirection (dynamicWindow)
    def setSplitDirection (self,orientation='vertical'):

        vert = orientation and orientation.lower().startswith('v')
        # g.trace('vert',vert)

        orientation1 = g.choose(vert,QtCore.Qt.Horizontal, QtCore.Qt.Vertical)
        orientation2 = g.choose(vert,QtCore.Qt.Vertical, QtCore.Qt.Horizontal)
        self.splitter.setOrientation(orientation1)
        self.splitter_2.setOrientation(orientation2)
    #@-node:edward.20081129091117.1:setSplitDirection (dynamicWindow)
    #@+node:ekr.20081121105001.203:setStyleSheets & helper
    styleSheet_inited = False

    def setStyleSheets(self):

        c = self.c

        sheet = c.config.getData('qt-gui-plugin-style-sheet')
        if sheet: sheet = '\n'.join(sheet)
        self.ui.setStyleSheet(sheet or self.default_sheet())
    #@nonl
    #@+node:ekr.20081121105001.204:defaultStyleSheet
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
    #@-node:ekr.20081121105001.204:defaultStyleSheet
    #@-node:ekr.20081121105001.203:setStyleSheets & helper
    #@-others

#@-node:ekr.20081121105001.200:class  DynamicWindow
#@+node:ekr.20081121105001.205:class leoQtBody (leoBody)
class leoQtBody (leoFrame.leoBody):

    """A class that represents the body pane of a Qt window."""

    #@    @+others
    #@+node:ekr.20081121105001.206: Birth
    #@+node:ekr.20081121105001.207: ctor (qtBody)
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

            # Hook up the QSyntaxHighlighter
            if useQSyntaxHighlighter:
                self.colorizer = leoQtColorizer(c,w.widget)
            else:
                self.colorizer = leoColor.colorizer(c)
            w.acceptRichText = False

        # Config stuff.
        self.trace_onBodyChanged = c.config.getBool('trace_onBodyChanged')
        wrap = c.config.getBool('body_pane_wraps')
        if self.useScintilla:
            pass
        else:
            self.widget.widget.setWordWrapMode(g.choose(wrap,
                QtGui.QTextOption.WordWrap,
                QtGui.QTextOption.NoWrap))
        wrap = g.choose(wrap,"word","none")
        self.wrapState = wrap

        # For multiple body editors.
        self.editor_name = None
        self.editor_v = None
        self.numberOfEditors = 1
        self.totalNumberOfEditors = 1
    #@-node:ekr.20081121105001.207: ctor (qtBody)
    #@+node:ekr.20081121105001.208:createBindings (qtBody)
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
    #@-node:ekr.20081121105001.208:createBindings (qtBody)
    #@+node:ekr.20081121105001.209:get_name
    def getName (self):

        return 'body-widget'
    #@-node:ekr.20081121105001.209:get_name
    #@-node:ekr.20081121105001.206: Birth
    #@+node:ekr.20081121105001.210:Do-nothings

    # Configuration will be handled by style sheets.
    def cget(self,*args,**keys):        return None
    def configure (self,*args,**keys):  pass
    def setEditorColors (self,bg,fg):   pass

    def oops (self):
        g.trace('qtBody',g.callers(3))
    #@-node:ekr.20081121105001.210:Do-nothings
    #@+node:ekr.20081121105001.211:High-level interface to self.widget
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
    #@-node:ekr.20081121105001.211:High-level interface to self.widget
    #@+node:ekr.20081121105001.212:Editors (qtBody)
    # This code uses self.pb, a paned body widget,
    # created by tkBody.finishCreate.
    #@+node:ekr.20081121105001.213:createEditorFrame
    def createEditorFrame (self,pane):

        return None

        # f = Tk.Frame(pane)
        # f.pack(side='top',expand=1,fill='both')
        # return f
    #@-node:ekr.20081121105001.213:createEditorFrame
    #@+node:ekr.20081121105001.214:packEditorLabelWidget
    def packEditorLabelWidget (self,w):

        '''Create a Tk label widget.'''

        # if not hasattr(w,'leo_label') or not w.leo_label:
            # # g.trace('w.leo_frame',id(w.leo_frame))
            # w.pack_forget()
            # w.leo_label = Tk.Label(w.leo_frame)
            # w.leo_label.pack(side='top')
            # w.pack(expand=1,fill='both')
    #@nonl
    #@-node:ekr.20081121105001.214:packEditorLabelWidget
    #@+node:ekr.20081121105001.215:entries
    if 1:
        #@    @+others
        #@+node:ekr.20081121105001.216:addEditor
        def addEditor (self,event=None):

            '''Add another editor to the body pane.'''

            self.editorWidgets['1'] = self.c.frame.body.bodyCtrl

            # c = self.c ; p = c.currentPosition()

            # self.totalNumberOfEditors += 1
            # self.numberOfEditors += 1

            # if self.numberOfEditors == 2:
                # # Inject the ivars into the first editor.
                # # Bug fix: Leo 4.4.8 rc1: The name of the last editor need not be '1'
                # d = self.editorWidgets ; keys = d.keys()
                # if len(keys) == 1:
                    # w_old = d.get(keys[0])
                    # self.updateInjectedIvars(w_old,p)
                    # self.selectLabel(w_old) # Immediately create the label in the old editor.
                # else:
                    # g.trace('can not happen: unexpected editorWidgets',d)

            # name = '%d' % self.totalNumberOfEditors
            # pane = self.pb.add(name)
            # panes = self.pb.panes()
            # minSize = float(1.0/float(len(panes)))

            # f = self.createEditorFrame(pane)
            # 
            #@nonl
            #@<< create text widget w >>
            #@+node:ekr.20081121105001.217:<< create text widget w >>
            # w = self.createTextWidget(f,name=name,p=p)
            # w.delete(0,'end')
            # w.insert('end',p.bodyString())
            # w.see(0)

            # self.setFontFromConfig(w=w)
            # self.setColorFromConfig(w=w)
            # self.createBindings(w=w)
            # c.k.completeAllBindingsForWidget(w)

            # self.recolorWidget(p,w)
            #@nonl
            #@-node:ekr.20081121105001.217:<< create text widget w >>
            #@nl
            # self.editorWidgets[name] = w

            # for pane in panes:
                # self.pb.configurepane(pane,size=minSize)

            # self.pb.updatelayout()
            # c.frame.body.bodyCtrl = w

            # self.updateInjectedIvars(w,p)
            # self.selectLabel(w)
            # self.selectEditor(w)
            # self.updateEditors()
            # c.bodyWantsFocusNow()
        #@-node:ekr.20081121105001.216:addEditor
        #@+node:ekr.20081121105001.218:assignPositionToEditor
        def assignPositionToEditor (self,p):

            '''Called *only* from tree.select to select the present body editor.'''

            c = self.c ; cc = c.chapterController ; w = c.frame.body.bodyCtrl

            # self.updateInjectedIvars(w,p)
            # self.selectLabel(w)

            # g.trace('===',id(w),w.leo_chapter.name,w.leo_p.headString())
        #@-node:ekr.20081121105001.218:assignPositionToEditor
        #@+node:ekr.20081121105001.219:cycleEditorFocus
        def cycleEditorFocus (self,event=None):

            '''Cycle keyboard focus between the body text editors.'''

            # c = self.c ; d = self.editorWidgets ; w = c.frame.body.bodyCtrl
            # values = d.values()
            # if len(values) > 1:
                # i = values.index(w) + 1
                # if i == len(values): i = 0
                # w2 = d.values()[i]
                # assert(w!=w2)
                # self.selectEditor(w2)
                # c.frame.body.bodyCtrl = w2
                # # g.pr('***',g.app.gui.widget_name(w2),id(w2))

            # return 'break'
        #@-node:ekr.20081121105001.219:cycleEditorFocus
        #@+node:ekr.20081121105001.220:deleteEditor
        def deleteEditor (self,event=None):

            '''Delete the presently selected body text editor.'''

            # c = self.c ; w = c.frame.body.bodyCtrl ; d = self.editorWidgets

            # if len(d.keys()) == 1: return

            # name = w.leo_name

            # del d [name] 
            # self.pb.delete(name)
            # panes = self.pb.panes()
            # minSize = float(1.0/float(len(panes)))

            # for pane in panes:
                # self.pb.configurepane(pane,size=minSize)

            # # Select another editor.
            # w = d.values()[0]
            # # c.frame.body.bodyCtrl = w # Don't do this now?
            # self.numberOfEditors -= 1
            # self.selectEditor(w)
        #@-node:ekr.20081121105001.220:deleteEditor
        #@+node:ekr.20081121105001.221:findEditorForChapter (leoBody)
        def findEditorForChapter (self,chapter,p):

            '''Return an editor to be assigned to chapter.'''

            return self.c.frame.body.bodyCtrl

            # c = self.c ; d = self.editorWidgets ; values = d.values()

            # # First, try to match both the chapter and position.
            # if p:
                # for w in values:
                    # if (
                        # hasattr(w,'leo_chapter') and w.leo_chapter == chapter and
                        # hasattr(w,'leo_p') and w.leo_p and w.leo_p == p
                    # ):
                        # # g.trace('***',id(w),'match chapter and p',p.headString())
                        # return w

            # # Next, try to match just the chapter.
            # for w in values:
                # if hasattr(w,'leo_chapter') and w.leo_chapter == chapter:
                    # # g.trace('***',id(w),'match only chapter',p.headString())
                    # return w

            # # As a last resort, return the present editor widget.
            # # g.trace('***',id(self.bodyCtrl),'no match',p.headString())
            # return c.frame.body.bodyCtrl
        #@-node:ekr.20081121105001.221:findEditorForChapter (leoBody)
        #@+node:ekr.20081121105001.222:select/unselectLabel
        def unselectLabel (self,w):

            pass

            # self.createChapterIvar(w)
            # self.packEditorLabelWidget(w)
            # s = self.computeLabel(w)
            # if hasattr(w,'leo_label') and w.leo_label:
                # w.leo_label.configure(text=s,bg='LightSteelBlue1')

        def selectLabel (self,w):

            pass

            # if self.numberOfEditors > 1:
                # self.createChapterIvar(w)
                # self.packEditorLabelWidget(w)
                # s = self.computeLabel(w)
                # # g.trace(s,g.callers())
                # if hasattr(w,'leo_label') and w.leo_label:
                    # w.leo_label.configure(text=s,bg='white')
            # elif hasattr(w,'leo_label') and w.leo_label:
                # w.leo_label.pack_forget()
                # w.leo_label = None
        #@-node:ekr.20081121105001.222:select/unselectLabel
        #@+node:ekr.20081121105001.223:selectEditor & helpers
        selectEditorLockout = False

        def selectEditor(self,w):

            '''Select editor w and node w.leo_p.'''

            return self.c.frame.body.bodyCtrl

            #  Called by body.onClick and whenever w must be selected.
            # trace = False
            # c = self.c
            # if not w: return self.c.frame.body.bodyCtrl
            # if self.selectEditorLockout: return

            # if w and w == self.c.frame.body.bodyCtrl:
                # if w.leo_p and w.leo_p != c.currentPosition():
                    # c.selectPosition(w.leo_p)
                    # c.bodyWantsFocusNow()
                # return

            # try:
                # val = None
                # self.selectEditorLockout = True
                # val = self.selectEditorHelper(w)
            # finally:
                # self.selectEditorLockout = False

            # return val # Don't put a return in a finally clause.
        #@+node:ekr.20081121105001.224:selectEditorHelper
        def selectEditorHelper (self,w):

            c = self.c ; cc = c.chapterController ; d = self.editorWidgets

            trace = False

            if not w.leo_p:
                g.trace('no w.leo_p') 
                return 'break'

            if trace:
                g.trace('==1',id(w),
                    hasattr(w,'leo_chapter') and w.leo_chapter and w.leo_chapter.name,
                    hasattr(w,'leo_p') and w.leo_p and w.leo_p.headString())

            self.inactivateActiveEditor(w)

            # The actual switch.
            c.frame.body.bodyCtrl = w
            w.leo_active = True

            self.switchToChapter(w)
            self.selectLabel(w)

            if not self.ensurePositionExists(w):
                g.trace('***** no position editor!')
                return 'break'

            if trace:
                g.trace('==2',id(w),
                    hasattr(w,'leo_chapter') and w.leo_chapter and w.leo_chapter.name,
                    hasattr(w,'leo_p') and w.leo_p and w.leo_p.headString())

            # g.trace('expanding ancestors of ',w.leo_p.headString(),g.callers())
            c.frame.tree.expandAllAncestors(w.leo_p)
            c.selectPosition(w.leo_p) # Calls assignPositionToEditor.
            c.redraw()

            c.recolor_now()
            #@    << restore the selection, insertion point and the scrollbar >>
            #@+node:ekr.20081121105001.225:<< restore the selection, insertion point and the scrollbar >>
            # g.trace('active:',id(w),'scroll',w.leo_scrollBarSpot,'ins',w.leo_insertSpot)

            if w.leo_insertSpot:
                w.setInsertPoint(w.leo_insertSpot)
            else:
                w.setInsertPoint(0)

            if w.leo_scrollBarSpot is not None:
                first,last = w.leo_scrollBarSpot
                w.yview('moveto',first)
            else:
                w.seeInsertPoint()

            if w.leo_selection:
                try:
                    start,end = w.leo_selection
                    w.setSelectionRange(start,end)
                except Exception:
                    pass
            #@-node:ekr.20081121105001.225:<< restore the selection, insertion point and the scrollbar >>
            #@nl
            c.bodyWantsFocusNow()
            return 'break'
        #@-node:ekr.20081121105001.224:selectEditorHelper
        #@-node:ekr.20081121105001.223:selectEditor & helpers
        #@+node:ekr.20081121105001.226:updateEditors
        # Called from addEditor and assignPositionToEditor

        def updateEditors (self):

            pass

            # c = self.c ; p = c.currentPosition()
            # d = self.editorWidgets
            # if len(d.keys()) < 2: return # There is only the main widget.

            # for key in d:
                # w = d.get(key)
                # v = w.leo_v
                # if v and v == p.v and w != c.frame.body.bodyCtrl:
                    # w.delete(0,'end')
                    # w.insert('end',p.bodyString())
                    # # g.trace('update',w,v)
                    # self.recolorWidget(p,w)

            # c.bodyWantsFocus()
        #@-node:ekr.20081121105001.226:updateEditors
        #@-others
    #@nonl
    #@-node:ekr.20081121105001.215:entries
    #@+node:ekr.20081121105001.227:utils
    #@+node:ekr.20081121105001.228:computeLabel
    def computeLabel (self,w):

        s = w.leo_label_s

        if hasattr(w,'leo_chapter') and w.leo_chapter:
            s = '%s: %s' % (w.leo_chapter.name,s)

        return s
    #@-node:ekr.20081121105001.228:computeLabel
    #@+node:ekr.20081121105001.229:createChapterIvar
    def createChapterIvar (self,w):

        c = self.c ; cc = c.chapterController

        if not hasattr(w,'leo_chapter') or not w.leo_chapter:
            if cc and self.use_chapters:
                w.leo_chapter = cc.getSelectedChapter()
            else:
                w.leo_chapter = None
    #@-node:ekr.20081121105001.229:createChapterIvar
    #@+node:ekr.20081121105001.230:ensurePositionExists
    def ensurePositionExists(self,w):

        '''Return True if w.leo_p exists or can be reconstituted.'''

        c = self.c

        if c.positionExists(w.leo_p):
            return True
        else:
            g.trace('***** does not exist',w.leo_name)
            for p2 in c.all_positions_with_unique_vnodes_iter():
                if p2.v and p2.v == w.leo_v:
                    w.leo_p = p2.copy()
                    return True
            else:
                 # This *can* happen when selecting a deleted node.
                w.leo_p = c.currentPosition()
                return False
    #@-node:ekr.20081121105001.230:ensurePositionExists
    #@+node:ekr.20081121105001.231:inactivateActiveEditor
    def inactivateActiveEditor(self,w):

        '''Inactivate the previously active editor.'''

        d = self.editorWidgets

        # Don't capture ivars here! assignPositionToEditor keeps them up-to-date. (??)
        for key in d:
            w2 = d.get(key)
            if w2 != w and w2.leo_active:
                w2.leo_active = False
                self.unselectLabel(w2)
                w2.leo_scrollBarSpot = w2.yview()
                w2.leo_insertSpot = w2.getInsertPoint()
                w2.leo_selection = w2.getSelectionRange()
                # g.trace('inactive:',id(w2),'scroll',w2.leo_scrollBarSpot,'ins',w2.leo_insertSpot)
                # g.trace('inactivate',id(w2))
                return
    #@-node:ekr.20081121105001.231:inactivateActiveEditor
    #@+node:ekr.20081121105001.232:recolorWidget
    def recolorWidget (self,p,w):

        c = self.c ; old_w = c.frame.body.bodyCtrl

        # g.trace('w',id(w),p.headString(),len(w.getAllText()))

        # Save.
        c.frame.body.bodyCtrl = w
        try:
            # c.recolor_now(interruptable=False) # Force a complete recoloring.
            c.frame.body.colorizer.colorize(p,incremental=False,interruptable=False)
        finally:
            # Restore.
            c.frame.body.bodyCtrl = old_w
    #@-node:ekr.20081121105001.232:recolorWidget
    #@+node:ekr.20081121105001.233:switchToChapter (leoBody)
    def switchToChapter (self,w):

        '''select w.leo_chapter.'''

        c = self.c ; cc = c.chapterController

        if hasattr(w,'leo_chapter') and w.leo_chapter:
            chapter = w.leo_chapter
            name = chapter and chapter.name
            oldChapter = cc.getSelectedChapter()
            if chapter != oldChapter:
                # g.trace('===','old',oldChapter.name,'new',name,w.leo_p)
                cc.selectChapterByName(name)
                c.bodyWantsFocusNow()
    #@-node:ekr.20081121105001.233:switchToChapter (leoBody)
    #@+node:ekr.20081121105001.234:updateInjectedIvars
    # Called from addEditor and assignPositionToEditor.

    def updateInjectedIvars (self,w,p):

        c = self.c ; cc = c.chapterController

        if cc and self.use_chapters:
            w.leo_chapter = cc.getSelectedChapter()
        else:
            w.leo_chapter = None

        w.leo_p = p.copy()
        w.leo_v = w.leo_p.v
        w.leo_label_s = p.headString()

        # g.trace('   ===', id(w),w.leo_chapter and w.leo_chapter.name,p.headString())
    #@-node:ekr.20081121105001.234:updateInjectedIvars
    #@-node:ekr.20081121105001.227:utils
    #@-node:ekr.20081121105001.212:Editors (qtBody)
    #@-others
#@-node:ekr.20081121105001.205:class leoQtBody (leoBody)
#@+node:ekr.20081121105001.235:class leoQtFindTab (findTab)
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
    #@+node:ekr.20081121105001.236: Birth: called from leoFind ctor
    # leoFind.__init__ calls initGui, createFrame, createBindings & init, in that order.
    #@+node:ekr.20081121105001.237:initGui
    def initGui (self):

        self.svarDict = {}
            # Keys are ivar names, values are svar objects.

        for key in self.intKeys:
            self.svarDict[key] = self.svar()

        for key in self.newStringKeys:
            self.svarDict[key] = self.svar()
    #@nonl
    #@-node:ekr.20081121105001.237:initGui
    #@+node:ekr.20081121105001.238:init (qtFindTab) & helpers
    def init (self,c):

        '''Init the widgets of the 'Find' tab.'''

        self.createIvars()
        self.initIvars()
        self.initTextWidgets()
        self.initCheckBoxes()
        self.initRadioButtons()
    #@+node:ekr.20081121105001.239:createIvars
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
    #@-node:ekr.20081121105001.239:createIvars
    #@+node:ekr.20081121105001.240:initIvars
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
    #@-node:ekr.20081121105001.240:initIvars
    #@+node:ekr.20081121105001.241:initTextWidgets
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
    #@-node:ekr.20081121105001.241:initTextWidgets
    #@+node:ekr.20081121105001.242:initCheckBoxes
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
    #@-node:ekr.20081121105001.242:initCheckBoxes
    #@+node:ekr.20081121105001.243:initRadioButtons
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
    #@-node:ekr.20081121105001.243:initRadioButtons
    #@-node:ekr.20081121105001.238:init (qtFindTab) & helpers
    #@-node:ekr.20081121105001.236: Birth: called from leoFind ctor
    #@+node:ekr.20081121105001.244:class svar
    class svar:
        '''A class like Tk's IntVar and StringVar classes.'''
        def __init__(self):
            self.val = None
        def get (self):
            return self.val
        def set (self,val):
            self.val = val
    #@-node:ekr.20081121105001.244:class svar
    #@+node:ekr.20081121105001.245:Support for minibufferFind class (qtFindTab)
    # This is the same as the Tk code because we simulate Tk svars.
    #@nonl
    #@+node:ekr.20081121105001.246:getOption
    def getOption (self,ivar):

        var = self.svarDict.get(ivar)

        if var:
            val = var.get()
            # g.trace('%s = %s' % (ivar,val))
            return val
        else:
            g.trace('bad ivar name: %s' % ivar)
            return None
    #@-node:ekr.20081121105001.246:getOption
    #@+node:ekr.20081121105001.247:setOption
    def setOption (self,ivar,val):

        if ivar in self.intKeys:
            if val is not None:
                var = self.svarDict.get(ivar)
                var.set(val)
                # g.trace('%s = %s' % (ivar,val))

        elif not g.app.unitTesting:
            g.trace('oops: bad find ivar %s' % ivar)
    #@-node:ekr.20081121105001.247:setOption
    #@+node:ekr.20081121105001.248:toggleOption
    def toggleOption (self,ivar):

        if ivar in self.intKeys:
            var = self.svarDict.get(ivar)
            val = not var.get()
            var.set(val)
            # g.trace('%s = %s' % (ivar,val),var)
        else:
            g.trace('oops: bad find ivar %s' % ivar)
    #@-node:ekr.20081121105001.248:toggleOption
    #@-node:ekr.20081121105001.245:Support for minibufferFind class (qtFindTab)
    #@-others
#@-node:ekr.20081121105001.235:class leoQtFindTab (findTab)
#@+node:ekr.20081121105001.249:class leoQtFrame
class leoQtFrame (leoFrame.leoFrame):

    """A class that represents a Leo window rendered in qt."""

    #@    @+others
    #@+node:ekr.20081121105001.250: Birth & Death (qtFrame)
    #@+node:ekr.20081121105001.251:__init__ (qtFrame)
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
        #@+node:ekr.20081121105001.252:<< set the leoQtFrame ivars >> (removed frame.bodyCtrl ivar)
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
        #@-node:ekr.20081121105001.252:<< set the leoQtFrame ivars >> (removed frame.bodyCtrl ivar)
        #@nl

        self.minibufferVisible = True
    #@-node:ekr.20081121105001.251:__init__ (qtFrame)
    #@+node:ekr.20081121105001.253:__repr__ (qtFrame)
    def __repr__ (self):

        return "<leoQtFrame: %s>" % self.title
    #@-node:ekr.20081121105001.253:__repr__ (qtFrame)
    #@+node:ekr.20081121105001.254:qtFrame.finishCreate & helpers
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
    #@+node:ekr.20081121105001.255:createSplitterComponents (qtFrame)
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
    #@-node:ekr.20081121105001.255:createSplitterComponents (qtFrame)
    #@-node:ekr.20081121105001.254:qtFrame.finishCreate & helpers
    #@+node:ekr.20081121105001.256:initCompleteHint
    def initCompleteHint (self):

        '''A kludge: called to enable text changed events.'''

        self.initComplete = True
        # g.trace(self.c)
    #@-node:ekr.20081121105001.256:initCompleteHint
    #@+node:ekr.20081121105001.257:Destroying the qtFrame
    #@+node:ekr.20081121105001.258:destroyAllObjects
    def destroyAllObjects (self):

        """Clear all links to objects in a Leo window."""

        frame = self ; c = self.c

        # g.printGcAll()

        # Do this first.
        #@    << clear all vnodes and tnodes in the tree >>
        #@+node:ekr.20081121105001.259:<< clear all vnodes and tnodes in the tree>>
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
        #@-node:ekr.20081121105001.259:<< clear all vnodes and tnodes in the tree>>
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

    #@-node:ekr.20081121105001.258:destroyAllObjects
    #@+node:ekr.20081121105001.260:destroySelf (qtFrame)
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

    #@-node:ekr.20081121105001.260:destroySelf (qtFrame)
    #@-node:ekr.20081121105001.257:Destroying the qtFrame
    #@-node:ekr.20081121105001.250: Birth & Death (qtFrame)
    #@+node:ekr.20081121105001.261:class qtStatusLineClass (qtFrame)
    class qtStatusLineClass:

        '''A class representing the status line.'''

        #@    @+others
        #@+node:ekr.20081121105001.262:ctor
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
        #@-node:ekr.20081121105001.262:ctor
        #@+node:ekr.20081121105001.263: do-nothings
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

        #@-node:ekr.20081121105001.263: do-nothings
        #@+node:ekr.20081121105001.264:clear, get & put/1
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
        #@-node:ekr.20081121105001.264:clear, get & put/1
        #@+node:ekr.20081121105001.265:update
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
        #@-node:ekr.20081121105001.265:update
        #@-others
    #@-node:ekr.20081121105001.261:class qtStatusLineClass (qtFrame)
    #@+node:ekr.20081121105001.266:class qtIconBarClass
    class qtIconBarClass:

        '''A class representing the singleton Icon bar'''

        #@    @+others
        #@+node:ekr.20081121105001.267: ctor
        def __init__ (self,c,parentFrame):

            self.c = c
            self.parentFrame = parentFrame
            self.w = c.frame.top.iconBar # A QToolBar.

            # g.app.iconWidgetCount = 0
        #@-node:ekr.20081121105001.267: ctor
        #@+node:ekr.20081121105001.268: do-nothings
        def addRow(self,height=None):   pass
        def getFrame (self):            return None
        def getNewFrame (self):         return None
        def pack (self):                pass
        def unpack (self):              pass

        hide = unpack
        show = pack
        #@-node:ekr.20081121105001.268: do-nothings
        #@+node:ekr.20081121105001.269:add
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
        #@-node:ekr.20081121105001.269:add
        #@+node:ekr.20081121105001.270:addRowIfNeeded
        def addRowIfNeeded (self):

            '''Add a new icon row if there are too many widgets.'''

            # n = g.app.iconWidgetCount

            # if n >= self.widgets_per_row:
                # g.app.iconWidgetCount = 0
                # self.addRow()

            # g.app.iconWidgetCount += 1
        #@-node:ekr.20081121105001.270:addRowIfNeeded
        #@+node:ekr.20081121105001.271:addWidget
        def addWidget (self,w):

            self.w.addWidget(w)
        #@-node:ekr.20081121105001.271:addWidget
        #@+node:ekr.20081121105001.272:clear
        def clear(self):

            """Destroy all the widgets in the icon bar"""

            self.w.clear()

            g.app.iconWidgetCount = 0
        #@-node:ekr.20081121105001.272:clear
        #@+node:ekr.20081121105001.273:deleteButton
        def deleteButton (self,w):

            g.trace(w)
            # self.w.deleteWidget(w)
            self.c.bodyWantsFocus()
            self.c.outerUpdate()
        #@-node:ekr.20081121105001.273:deleteButton
        #@+node:ekr.20081121105001.274:setCommandForButton
        def setCommandForButton(self,button,command):

            if command:
                QtCore.QObject.connect(button,
                    QtCore.SIGNAL("clicked()"),command)
        #@-node:ekr.20081121105001.274:setCommandForButton
        #@-others
    #@-node:ekr.20081121105001.266:class qtIconBarClass
    #@+node:ekr.20081121105001.275:Minibuffer methods
    #@+node:ekr.20081121105001.276:showMinibuffer
    def showMinibuffer (self):

        '''Make the minibuffer visible.'''

        # frame = self

        # if not frame.minibufferVisible:
            # frame.minibufferFrame.pack(side='bottom',fill='x')
            # frame.minibufferVisible = True
    #@-node:ekr.20081121105001.276:showMinibuffer
    #@+node:ekr.20081121105001.277:hideMinibuffer
    def hideMinibuffer (self):

        '''Hide the minibuffer.'''

        # frame = self

        # if frame.minibufferVisible:
            # frame.minibufferFrame.pack_forget()
            # frame.minibufferVisible = False
    #@-node:ekr.20081121105001.277:hideMinibuffer
    #@+node:ekr.20081121105001.278:f.setMinibufferBindings
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
    #@-node:ekr.20081121105001.278:f.setMinibufferBindings
    #@-node:ekr.20081121105001.275:Minibuffer methods
    #@+node:ekr.20081121105001.279:Configuration (qtFrame)
    #@+node:ekr.20081121105001.280:configureBar (qtFrame)
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
    #@-node:ekr.20081121105001.280:configureBar (qtFrame)
    #@+node:ekr.20081121105001.281:configureBarsFromConfig (qtFrame)
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
    #@-node:ekr.20081121105001.281:configureBarsFromConfig (qtFrame)
    #@+node:ekr.20081121105001.282:reconfigureFromConfig (qtFrame)
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
    #@-node:ekr.20081121105001.282:reconfigureFromConfig (qtFrame)
    #@+node:ekr.20081121105001.283:setInitialWindowGeometry (qtFrame)
    def setInitialWindowGeometry(self):

        """Set the position and size of the frame to config params."""

        c = self.c

        h = c.config.getInt("initial_window_height") or 500
        w = c.config.getInt("initial_window_width") or 600
        x = c.config.getInt("initial_window_left") or 10
        y = c.config.getInt("initial_window_top") or 10

        if h and w and x and y:
            self.setTopGeometry(w,h,x,y)
    #@-node:ekr.20081121105001.283:setInitialWindowGeometry (qtFrame)
    #@+node:ekr.20081121105001.284:setTabWidth (qtFrame)
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
    #@-node:ekr.20081121105001.284:setTabWidth (qtFrame)
    #@+node:ekr.20081121105001.285:setWrap (qtFrame)
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
    #@-node:ekr.20081121105001.285:setWrap (qtFrame)
    #@+node:ekr.20081121105001.286:reconfigurePanes (use config bar_width) (qtFrame)
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
    #@-node:ekr.20081121105001.286:reconfigurePanes (use config bar_width) (qtFrame)
    #@+node:ekr.20081121105001.287:resizePanesToRatio (qtFrame)
    def resizePanesToRatio(self,ratio,ratio2):

        pass

        # g.trace(ratio,ratio2,g.callers())

        # self.divideLeoSplitter(self.splitVerticalFlag,ratio)
        # self.divideLeoSplitter(not self.splitVerticalFlag,ratio2)
    #@-node:ekr.20081121105001.287:resizePanesToRatio (qtFrame)
    #@-node:ekr.20081121105001.279:Configuration (qtFrame)
    #@+node:ekr.20081121105001.288:Event handlers (qtFrame)
    #@+node:ekr.20081121105001.289:frame.OnCloseLeoEvent
    # Called from quit logic and when user closes the window.
    # Returns True if the close happened.

    def OnCloseLeoEvent(self):

        f = self ; c = f.c

        if c.inCommand:
            # g.trace('requesting window close')
            c.requestCloseWindow = True
        else:
            g.app.closeLeoWindow(self)
    #@-node:ekr.20081121105001.289:frame.OnCloseLeoEvent
    #@+node:ekr.20081121105001.290:frame.OnControlKeyUp/Down
    def OnControlKeyDown (self,event=None):

        self.controlKeyIsDown = True

    def OnControlKeyUp (self,event=None):

        self.controlKeyIsDown = False
    #@-node:ekr.20081121105001.290:frame.OnControlKeyUp/Down
    #@+node:ekr.20081121105001.291:OnActivateBody (qtFrame)
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
    #@-node:ekr.20081121105001.291:OnActivateBody (qtFrame)
    #@+node:ekr.20081121105001.292:OnActivateLeoEvent, OnDeactivateLeoEvent
    def OnActivateLeoEvent(self,event=None):

        '''Handle a click anywhere in the Leo window.'''

        self.c.setLog()

    def OnDeactivateLeoEvent(self,event=None):

        pass # This causes problems on the Mac.
    #@-node:ekr.20081121105001.292:OnActivateLeoEvent, OnDeactivateLeoEvent
    #@+node:ekr.20081121105001.293:OnActivateTree
    def OnActivateTree (self,event=None):

        try:
            frame = self ; c = frame.c
            c.setLog()

            if 0: # Do NOT do this here!
                # OnActivateTree can get called when the tree gets DE-activated!!
                c.bodyWantsFocus()

        except:
            g.es_event_exception("activate tree")
    #@-node:ekr.20081121105001.293:OnActivateTree
    #@+node:ekr.20081121105001.294:OnBodyClick, OnBodyRClick (Events)
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
    #@-node:ekr.20081121105001.294:OnBodyClick, OnBodyRClick (Events)
    #@+node:ekr.20081121105001.295:OnBodyDoubleClick (Events)
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
    #@-node:ekr.20081121105001.295:OnBodyDoubleClick (Events)
    #@-node:ekr.20081121105001.288:Event handlers (qtFrame)
    #@+node:ekr.20081121105001.296:Gui-dependent commands
    #@+node:ekr.20081121105001.297:Minibuffer commands... (qtFrame)
    #@+node:ekr.20081121105001.298:contractPane
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
    #@-node:ekr.20081121105001.298:contractPane
    #@+node:ekr.20081121105001.299:expandPane
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
    #@-node:ekr.20081121105001.299:expandPane
    #@+node:ekr.20081121105001.300:fullyExpandPane
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
    #@-node:ekr.20081121105001.300:fullyExpandPane
    #@+node:ekr.20081121105001.301:hidePane
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
    #@-node:ekr.20081121105001.301:hidePane
    #@+node:ekr.20081121105001.302:expand/contract/hide...Pane
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
    #@-node:ekr.20081121105001.302:expand/contract/hide...Pane
    #@+node:ekr.20081121105001.303:fullyExpand/hide...Pane
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
    #@-node:ekr.20081121105001.303:fullyExpand/hide...Pane
    #@-node:ekr.20081121105001.297:Minibuffer commands... (qtFrame)
    #@+node:ekr.20081121105001.304:Window Menu...
    #@+node:ekr.20081121105001.305:toggleActivePane (qtFrame)
    def toggleActivePane (self,event=None):

        '''Toggle the focus between the outline and body panes.'''

        frame = self ; c = frame.c

        if c.get_focus() == frame.body.bodyCtrl: # 2007/10/25
            c.treeWantsFocusNow()
        else:
            c.endEditing()
            c.bodyWantsFocusNow()
    #@-node:ekr.20081121105001.305:toggleActivePane (qtFrame)
    #@+node:ekr.20081121105001.306:cascade
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
    #@-node:ekr.20081121105001.306:cascade
    #@+node:ekr.20081121105001.307:equalSizedPanes
    def equalSizedPanes (self,event=None):

        '''Make the outline and body panes have the same size.'''

        frame = self
        frame.resizePanesToRatio(0.5,frame.secondary_ratio)
    #@-node:ekr.20081121105001.307:equalSizedPanes
    #@+node:ekr.20081121105001.308:hideLogWindow
    def hideLogWindow (self,event=None):

        frame = self

        # frame.divideLeoSplitter2(0.99, not frame.splitVerticalFlag)
    #@-node:ekr.20081121105001.308:hideLogWindow
    #@+node:ekr.20081121105001.309:minimizeAll
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
    #@-node:ekr.20081121105001.309:minimizeAll
    #@+node:ekr.20081121105001.310:toggleSplitDirection (qtFrame)
    # The key invariant: self.splitVerticalFlag tells the alignment of the main splitter.

    def toggleSplitDirection (self,event=None):

        '''Toggle the split direction in the present Leo window.'''

        frame = self ; top = frame.top

        for w in (top.splitter,top.splitter_2):
            w.setOrientation(
                g.choose(w.orientation() == QtCore.Qt.Horizontal,
                    QtCore.Qt.Vertical,QtCore.Qt.Horizontal))
    #@nonl
    #@+node:ekr.20081121105001.311:toggleQtSplitDirection
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
    #@-node:ekr.20081121105001.311:toggleQtSplitDirection
    #@-node:ekr.20081121105001.310:toggleSplitDirection (qtFrame)
    #@+node:ekr.20081121105001.312:resizeToScreen
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
    #@-node:ekr.20081121105001.312:resizeToScreen
    #@-node:ekr.20081121105001.304:Window Menu...
    #@+node:ekr.20081121105001.313:Help Menu...
    #@+node:ekr.20081121105001.314:leoHelp
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
    #@+node:ekr.20081121105001.315:showProgressBar
    def showProgressBar (self,count,size,total):

        # g.trace("count,size,total:",count,size,total)
        if self.scale == None:
            pass
            #@        << create the scale widget >>
            #@+node:ekr.20081121105001.316:<< create the scale widget >>
            # top = qt.Toplevel()
            # top.title("Download progress")
            # self.scale = scale = qt.Scale(top,state="normal",orient="horizontal",from_=0,to=total)
            # scale.pack()
            # top.lift()
            #@-node:ekr.20081121105001.316:<< create the scale widget >>
            #@nl
        # self.scale.set(count*size)
        # self.scale.update_idletasks()
    #@-node:ekr.20081121105001.315:showProgressBar
    #@-node:ekr.20081121105001.314:leoHelp
    #@-node:ekr.20081121105001.313:Help Menu...
    #@-node:ekr.20081121105001.296:Gui-dependent commands
    #@+node:ekr.20081121105001.317:Qt bindings... (qtFrame)
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
        return g.app.gui.toUnicode(self.top.windowTitle())

    def setTitle (self,s):
        self.top.setWindowTitle(s)
    def setTopGeometry(self,w,h,x,y,adjustSize=True):
        self.top.setGeometry(QtCore.QRect(x,y,w,h))
    #@-node:ekr.20081121105001.317:Qt bindings... (qtFrame)
    #@-others
#@-node:ekr.20081121105001.249:class leoQtFrame
#@+node:ekr.20081121105001.318:class leoQtLog
class leoQtLog (leoFrame.leoLog):

    """A class that represents the log pane of a Qt window."""

    #@    @+others
    #@+node:ekr.20081121105001.319:qtLog Birth
    #@+node:ekr.20081121105001.320:qtLog.__init__
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

        self.setFontFromConfig()
        self.setColorFromConfig()
    #@-node:ekr.20081121105001.320:qtLog.__init__
    #@+node:ekr.20081121105001.321:qtLog.finishCreate
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
                w.setTabText(i,'Find')
                self.contentsDict['Find'] = w.currentWidget()
            if w.tabText(i) == 'Spell':
                self.contentsDict['Spell'] = w.widget(i)
                self.frameDict['Spell'] = w.widget(i)

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
    #@-node:ekr.20081121105001.321:qtLog.finishCreate
    #@-node:ekr.20081121105001.319:qtLog Birth
    #@+node:ekr.20081121105001.322:Do nothings
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

    #@+node:ekr.20081121105001.323:Config
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
    #@-node:ekr.20081121105001.323:Config
    #@+node:ekr.20081121105001.324:Focus & update
    def onActivateLog (self,event=None):    pass
    def hasFocus (self):                    return None
    def forceLogUpdate (self,s):            pass
    #@-node:ekr.20081121105001.324:Focus & update
    #@-node:ekr.20081121105001.322:Do nothings
    #@+node:ekr.20081121105001.325:put & putnl (qtLog)
    #@+node:ekr.20081121105001.326:put
    # All output to the log stream eventually comes here.
    def put (self,s,color=None,tabName='Log'):

        c = self.c
        if g.app.quitting or not c or not c.exists:
            return

        self.selectTab(tabName or 'Log')
        # print('qtLog.put',tabName,'%3s' % (len(s)),self.logCtrl)

        # Note: this must be done after the call to selectTab.
        w = self.logCtrl # w is a QTextBrowser
        if w:
            if s.endswith('\n'): s = s[:-1]
            s=s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
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
            if g.isUnicode(s):
                s = g.toEncodedString(s,"ascii")
            print (s)
    #@-node:ekr.20081121105001.326:put
    #@+node:ekr.20081121105001.327:putnl
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
    #@-node:ekr.20081121105001.327:putnl
    #@-node:ekr.20081121105001.325:put & putnl (qtLog)
    #@+node:ekr.20081121105001.328:Tab (qtLog)
    #@+node:ekr.20081121105001.329:clearTab
    def clearTab (self,tabName,wrap='none'):

        w = self.logDict.get(tabName)
        if w:
            w.clear() # w is a QTextBrowser.
    #@-node:ekr.20081121105001.329:clearTab
    #@+node:ekr.20081121105001.330:createTab
    def createTab (self,tabName,createText=True,wrap='none'):

        c = self.c ; w = self.tabWidget

        if createText:
            contents = QtGui.QTextBrowser()
            contents.setWordWrapMode(QtGui.QTextOption.NoWrap)
            self.logDict[tabName] = contents
            if tabName == 'Log': self.logCtrl = contents
        else:
            contents = QtGui.QWidget()

        self.contentsDict[tabName] = contents
        w.addTab(contents,tabName)
        return contents

    #@-node:ekr.20081121105001.330:createTab
    #@+node:ekr.20081121105001.331:cycleTabFocus (to do)
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

    #@-node:ekr.20081121105001.331:cycleTabFocus (to do)
    #@+node:ekr.20081121105001.332:deleteTab
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
    #@-node:ekr.20081121105001.332:deleteTab
    #@+node:ekr.20081121105001.333:hideTab
    def hideTab (self,tabName):

        self.selectTab('Log')
    #@-node:ekr.20081121105001.333:hideTab
    #@+node:ekr.20081121105001.334:numberOfVisibleTabs
    def numberOfVisibleTabs (self):

        return len([val for val in self.frameDict.values() if val != None])
    #@-node:ekr.20081121105001.334:numberOfVisibleTabs
    #@+node:ekr.20081121105001.335:selectTab & helper
    def selectTab (self,tabName,createText=True,wrap='none'):

        '''Create the tab if necessary and make it active.'''

        c = self.c ; w = self.tabWidget ; trace = False

        ok = self.selectHelper(tabName,createText)
        if ok: return

        self.createTab(tabName,createText,wrap)
        self.selectHelper(tabName,createText)

    #@+node:ekr.20081121105001.336:selectHelper
    def selectHelper (self,tabName,createText):

        w = self.tabWidget

        for i in range(w.count()):
            if tabName == w.tabText(i):
                w.setCurrentIndex(i)
                if createText and tabName not in ('Spell','Find',):
                    self.logCtrl = w.widget(i)
                return True
        else:
            return False
    #@-node:ekr.20081121105001.336:selectHelper
    #@-node:ekr.20081121105001.335:selectTab & helper
    #@-node:ekr.20081121105001.328:Tab (qtLog)
    #@+node:ekr.20081121105001.337:qtLog color tab stuff
    def createColorPicker (self,tabName):

        return

        # log = self

        #@    << define colors >>
        #@+node:ekr.20081121105001.338:<< define colors >>
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
        #@-node:ekr.20081121105001.338:<< define colors >>
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
        #@+node:ekr.20081121105001.339:<< create optionMenu and callback >>
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
        #@-node:ekr.20081121105001.339:<< create optionMenu and callback >>
        #@nl
        #@    << create picker button and callback >>
        #@+node:ekr.20081121105001.340:<< create picker button and callback >>
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
        #@-node:ekr.20081121105001.340:<< create picker button and callback >>
        #@nl
    #@-node:ekr.20081121105001.337:qtLog color tab stuff
    #@+node:ekr.20081121105001.341:qtLog font tab stuff
    #@+node:ekr.20081121105001.342:createFontPicker
    def createFontPicker (self,tabName):

        return

        # log = self ; c = self.c
        # parent = log.frameDict.get(tabName)
        # w = log.textDict.get(tabName)
        # w.pack_forget()

        # bg = parent.cget('background')
        # font = self.getFont()

        #@    << create the frames >>
        #@+node:ekr.20081121105001.343:<< create the frames >>
        # f = qt.Frame(parent,background=bg) ; f.pack (side='top',expand=0,fill='both')
        # f1 = qt.Frame(f,background=bg)     ; f1.pack(side='top',expand=1,fill='x')
        # f2 = qt.Frame(f,background=bg)     ; f2.pack(side='top',expand=1,fill='x')
        # f3 = qt.Frame(f,background=bg)     ; f3.pack(side='top',expand=1,fill='x')
        # f4 = qt.Frame(f,background=bg)     ; f4.pack(side='top',expand=1,fill='x')
        #@-node:ekr.20081121105001.343:<< create the frames >>
        #@nl
        #@    << create the family combo box >>
        #@+node:ekr.20081121105001.344:<< create the family combo box >>
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
        #@-node:ekr.20081121105001.344:<< create the family combo box >>
        #@nl
        #@    << create the size entry >>
        #@+node:ekr.20081121105001.345:<< create the size entry >>
        # qt.Label(f2,text="Size:",width=10,background=bg).pack(side="left")

        # sizeEntry = qt.Entry(f2,width=4)
        # sizeEntry.insert(0,'12')
        # sizeEntry.pack(side="left",padx=2,pady=2)
        #@-node:ekr.20081121105001.345:<< create the size entry >>
        #@nl
        #@    << create the weight combo box >>
        #@+node:ekr.20081121105001.346:<< create the weight combo box >>
        # weightBox = Pmw.ComboBox(f3,
            # labelpos="we",label_text="Weight:",label_width=10,
            # label_background=bg,
            # arrowbutton_background=bg,
            # scrolledlist_items=['normal','bold'])

        # weightBox.selectitem(0)
        # weightBox.pack(side="left",padx=2,pady=2)
        #@-node:ekr.20081121105001.346:<< create the weight combo box >>
        #@nl
        #@    << create the slant combo box >>
        #@+node:ekr.20081121105001.347:<< create the slant combo box>>
        # slantBox = Pmw.ComboBox(f4,
            # labelpos="we",label_text="Slant:",label_width=10,
            # label_background=bg,
            # arrowbutton_background=bg,
            # scrolledlist_items=['roman','italic'])

        # slantBox.selectitem(0)
        # slantBox.pack(side="left",padx=2,pady=2)
        #@-node:ekr.20081121105001.347:<< create the slant combo box>>
        #@nl
        #@    << create the sample text widget >>
        #@+node:ekr.20081121105001.348:<< create the sample text widget >>
        # self.sampleWidget = sample = g.app.gui.plainTextWidget(f,height=20,width=80,font=font)
        # sample.pack(side='left')

        # s = 'The quick brown fox\njumped over the lazy dog.\n0123456789'
        # sample.insert(0,s)
        #@-node:ekr.20081121105001.348:<< create the sample text widget >>
        #@nl
        #@    << create and bind the callbacks >>
        #@+node:ekr.20081121105001.349:<< create and bind the callbacks >>
        # def fontCallback(event=None):
            # self.setFont(familyBox,sizeEntry,slantBox,weightBox,sample)

        # for w in (familyBox,slantBox,weightBox):
            # w.configure(selectioncommand=fontCallback)

        # c.bind(sizeEntry,'<Return>',fontCallback)
        #@-node:ekr.20081121105001.349:<< create and bind the callbacks >>
        #@nl

        # self.createBindings()
    #@-node:ekr.20081121105001.342:createFontPicker
    #@+node:ekr.20081121105001.350:createBindings (fontPicker)
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
    #@-node:ekr.20081121105001.350:createBindings (fontPicker)
    #@+node:ekr.20081121105001.351:getFont
    def getFont(self,family=None,size=12,slant='roman',weight='normal'):

        return g.app.config.defaultFont

        # try:
            # return tkFont.Font(family=family,size=size,slant=slant,weight=weight)
        # except Exception:
            # g.es("exception setting font")
            # g.es('','family,size,slant,weight:','',family,'',size,'',slant,'',weight)
            # # g.es_exception() # This just confuses people.
            # return g.app.config.defaultFont
    #@-node:ekr.20081121105001.351:getFont
    #@+node:ekr.20081121105001.352:setFont
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
    #@-node:ekr.20081121105001.352:setFont
    #@+node:ekr.20081121105001.353:hideFontTab
    def hideFontTab (self,event=None):

        c = self.c
        c.frame.log.selectTab('Log')
        c.bodyWantsFocus()
    #@-node:ekr.20081121105001.353:hideFontTab
    #@-node:ekr.20081121105001.341:qtLog font tab stuff
    #@-others
#@-node:ekr.20081121105001.318:class leoQtLog
#@+node:ekr.20081121105001.354:class leoQtMenu (leoMenu)
class leoQtMenu (leoMenu.leoMenu):

    #@    @+others
    #@+node:ekr.20081121105001.355:leoQtMenu.__init__
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
    #@-node:ekr.20081121105001.355:leoQtMenu.__init__
    #@+node:ekr.20081121105001.356:Activate menu commands (to do)
    #@+node:ekr.20081121105001.357:qtMenu.activateMenu
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
    #@-node:ekr.20081121105001.357:qtMenu.activateMenu
    #@+node:ekr.20081121105001.358:qtMenu.computeMenuPositions
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
    #@-node:ekr.20081121105001.358:qtMenu.computeMenuPositions
    #@-node:ekr.20081121105001.356:Activate menu commands (to do)
    #@+node:ekr.20081121105001.359:Tkinter menu bindings
    # See the Tk docs for what these routines are to do
    #@+node:ekr.20081121105001.360:Methods with Tk spellings
    #@+node:ekr.20081121105001.361:add_cascade
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
    #@-node:ekr.20081121105001.361:add_cascade
    #@+node:ekr.20081121105001.362:add_command
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
    #@-node:ekr.20081121105001.362:add_command
    #@+node:ekr.20081121105001.363:add_separator
    def add_separator(self,menu):

        """Wrapper for the Tkinter add_separator menu method."""

        if menu:
            menu.addSeparator()
    #@-node:ekr.20081121105001.363:add_separator
    #@+node:ekr.20081121105001.364:delete
    def delete (self,menu,realItemName):

        """Wrapper for the Tkinter delete menu method."""

        # if menu:
            # return menu.delete(realItemName)
    #@-node:ekr.20081121105001.364:delete
    #@+node:ekr.20081121105001.365:delete_range
    def delete_range (self,menu,n1,n2):

        """Wrapper for the Tkinter delete menu method."""

        # if menu:
            # return menu.delete(n1,n2)
    #@-node:ekr.20081121105001.365:delete_range
    #@+node:ekr.20081121105001.366:destroy
    def destroy (self,menu):

        """Wrapper for the Tkinter destroy menu method."""

        # if menu:
            # return menu.destroy()
    #@-node:ekr.20081121105001.366:destroy
    #@+node:ekr.20081121105001.367:insert
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
    #@-node:ekr.20081121105001.367:insert
    #@+node:ekr.20081121105001.368:insert_cascade
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
    #@-node:ekr.20081121105001.368:insert_cascade
    #@+node:ekr.20081121105001.369:new_menu
    def new_menu(self,parent,tearoff=False):

        """Wrapper for the Tkinter new_menu menu method."""

        c = self.c ; leoFrame = self.frame

        # g.trace(parent)

        # Parent can be None, in which case it will be added to the menuBar.
        menu = qtMenuWrapper(c,leoFrame,parent)

        return menu
    #@nonl
    #@-node:ekr.20081121105001.369:new_menu
    #@-node:ekr.20081121105001.360:Methods with Tk spellings
    #@+node:ekr.20081121105001.370:Methods with other spellings (Qtmenu)
    #@+node:ekr.20081121105001.371:clearAccel
    def clearAccel(self,menu,name):

        pass

        # if not menu:
            # return

        # realName = self.getRealMenuName(name)
        # realName = realName.replace("&","")

        # menu.entryconfig(realName,accelerator='')
    #@-node:ekr.20081121105001.371:clearAccel
    #@+node:ekr.20081121105001.372:createMenuBar (Qtmenu)
    def createMenuBar(self,frame):

        '''Create all top-level menus.
        The menuBar itself has already been created.'''

        self.createMenusFromTables()
    #@-node:ekr.20081121105001.372:createMenuBar (Qtmenu)
    #@+node:ekr.20081121105001.373:createOpenWithMenu
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
    #@-node:ekr.20081121105001.373:createOpenWithMenu
    #@+node:ekr.20081121105001.374:disableMenu
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
    #@-node:ekr.20081121105001.374:disableMenu
    #@+node:ekr.20081121105001.375:enableMenu
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
    #@-node:ekr.20081121105001.375:enableMenu
    #@+node:ekr.20081121105001.376:getMenuLabel
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
    #@-node:ekr.20081121105001.376:getMenuLabel
    #@+node:ekr.20081121105001.377:setMenuLabel
    def setMenuLabel (self,menu,name,label,underline=-1):

        def munge(s):
            s = g.app.gui.toUnicode(s)
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
    #@-node:ekr.20081121105001.377:setMenuLabel
    #@-node:ekr.20081121105001.370:Methods with other spellings (Qtmenu)
    #@-node:ekr.20081121105001.359:Tkinter menu bindings
    #@+node:ekr.20081121105001.378:getMacHelpMenu
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
    #@-node:ekr.20081121105001.378:getMacHelpMenu
    #@-others
#@-node:ekr.20081121105001.354:class leoQtMenu (leoMenu)
#@+node:ekr.20081121105001.379:class leoQtSpellTab
class leoQtSpellTab:

    #@    @+others
    #@+node:ekr.20081121105001.380:leoQtSpellTab.__init__
    def __init__ (self,c,handler,tabName):

        self.c = c
        self.handler = handler
        self.tabName = tabName

        self.createFrame()
        self.createBindings()

        ###self.fillbox([])
    #@-node:ekr.20081121105001.380:leoQtSpellTab.__init__
    #@+node:ekr.20081121105001.381:createBindings TO DO
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
    #@-node:ekr.20081121105001.381:createBindings TO DO
    #@+node:ekr.20081121105001.382:createFrame (to be done in Qt designer)
    def createFrame (self):

        c = self.c ; log = c.frame.log ; tabName = self.tabName

        # parentFrame = log.frameDict.get(tabName)
        # w = log.textDict.get(tabName)
        # w.pack_forget()

        # # Set the common background color.
        # bg = c.config.getColor('log_pane_Spell_tab_background_color') or 'LightSteelBlue2'

        #@    << Create the outer frames >>
        #@+node:ekr.20081121105001.383:<< Create the outer frames >>
        # self.outerScrolledFrame = Pmw.ScrolledFrame(
            # parentFrame,usehullsize = 1)

        # self.outerFrame = outer = self.outerScrolledFrame.component('frame')
        # self.outerFrame.configure(background=bg)

        # for z in ('borderframe','clipper','frame','hull'):
            # self.outerScrolledFrame.component(z).configure(
                # relief='flat',background=bg)
        #@-node:ekr.20081121105001.383:<< Create the outer frames >>
        #@nl
        #@    << Create the text and suggestion panes >>
        #@+node:ekr.20081121105001.384:<< Create the text and suggestion panes >>
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
        #@-node:ekr.20081121105001.384:<< Create the text and suggestion panes >>
        #@nl
        #@    << Create the spelling buttons >>
        #@+node:ekr.20081121105001.385:<< Create the spelling buttons >>
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
        #@-node:ekr.20081121105001.385:<< Create the spelling buttons >>
        #@nl

        # Pack last so buttons don't get squished.
        # self.outerScrolledFrame.pack(expand=1,fill='both',padx=2,pady=2)
    #@-node:ekr.20081121105001.382:createFrame (to be done in Qt designer)
    #@+node:ekr.20081121105001.386:Event handlers
    #@+node:ekr.20081121105001.387:onAddButton
    def onAddButton(self):
        """Handle a click in the Add button in the Check Spelling dialog."""

        self.handler.add()
    #@-node:ekr.20081121105001.387:onAddButton
    #@+node:ekr.20081121105001.388:onChangeButton & onChangeThenFindButton
    def onChangeButton(self,event=None):

        """Handle a click in the Change button in the Spell tab."""

        self.handler.change()
        self.updateButtons()


    def onChangeThenFindButton(self,event=None):

        """Handle a click in the "Change, Find" button in the Spell tab."""

        if self.handler.change():
            self.handler.find()
        self.updateButtons()
    #@-node:ekr.20081121105001.388:onChangeButton & onChangeThenFindButton
    #@+node:ekr.20081121105001.389:onFindButton
    def onFindButton(self):

        """Handle a click in the Find button in the Spell tab."""

        c = self.c
        self.handler.find()
        self.updateButtons()
        c.invalidateFocus()
        c.bodyWantsFocusNow()
    #@-node:ekr.20081121105001.389:onFindButton
    #@+node:ekr.20081121105001.390:onHideButton
    def onHideButton(self):

        """Handle a click in the Hide button in the Spell tab."""

        self.handler.hide()
    #@-node:ekr.20081121105001.390:onHideButton
    #@+node:ekr.20081121105001.391:onIgnoreButton
    def onIgnoreButton(self,event=None):

        """Handle a click in the Ignore button in the Check Spelling dialog."""

        self.handler.ignore()
    #@-node:ekr.20081121105001.391:onIgnoreButton
    #@+node:ekr.20081121105001.392:onMap
    def onMap (self, event=None):
        """Respond to a Tk <Map> event."""

        self.update(show= False, fill= False)
    #@-node:ekr.20081121105001.392:onMap
    #@+node:ekr.20081121105001.393:onSelectListBox
    def onSelectListBox(self, event=None):
        """Respond to a click in the selection listBox."""

        c = self.c
        self.updateButtons()
        c.bodyWantsFocus()
    #@-node:ekr.20081121105001.393:onSelectListBox
    #@-node:ekr.20081121105001.386:Event handlers
    #@+node:ekr.20081121105001.394:Helpers
    #@+node:ekr.20081121105001.395:bringToFront
    def bringToFront (self):

        self.c.frame.log.selectTab('Spell')
    #@-node:ekr.20081121105001.395:bringToFront
    #@+node:ekr.20081121105001.396:fillbox
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
    #@-node:ekr.20081121105001.396:fillbox
    #@+node:ekr.20081121105001.397:getSuggestion
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
    #@-node:ekr.20081121105001.397:getSuggestion
    #@+node:ekr.20081121105001.398:update
    def update(self,show=True,fill=False):

        """Update the Spell Check dialog."""

        c = self.c

        if fill:
            self.fillbox([])

        self.updateButtons()

        if show:
            self.bringToFront()
            c.bodyWantsFocus()
    #@-node:ekr.20081121105001.398:update
    #@+node:ekr.20081121105001.399:updateButtons (spellTab)
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
    #@-node:ekr.20081121105001.399:updateButtons (spellTab)
    #@-node:ekr.20081121105001.394:Helpers
    #@-others
#@-node:ekr.20081121105001.379:class leoQtSpellTab
#@+node:ekr.20081121105001.400:class leoQtTree
class leoQtTree (leoFrame.leoTree):

    """Leo qt tree class."""

    callbacksInjected = False # A class var.

    #@    @+others
    #@+node:ekr.20081121105001.401: Birth... (qt Tree)
    #@+node:ekr.20081121105001.402:__init__ (qtTree)
    def __init__(self,c,frame):

        # g.trace('*****qtTree')

        # Init the base class.
        leoFrame.leoTree.__init__(self,frame)

        # Components.
        self.c = c
        self.canvas = self # An official ivar used by Leo's core.
        self.treeWidget = w = frame.top.ui.treeWidget # An internal ivar.
        w.setIconSize(QtCore.QSize(20,11))
        # w.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

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
    #@-node:ekr.20081121105001.402:__init__ (qtTree)
    #@+node:ekr.20081121105001.159:qtTree.initAfterLoad
    def initAfterLoad (self):

        c = self.c ; frame = c.frame
        w = c.frame.top ; tw = self.treeWidget

        if not leoQtTree.callbacksInjected:
            leoQtTree.callbacksInjected = True
            self.injectCallbacks() # A base class method.

        w.connect(self.treeWidget,QtCore.SIGNAL(
                "itemDoubleClicked(QTreeWidgetItem*, int)"),
            self.onItemDoubleClicked)

        w.connect(self.treeWidget,QtCore.SIGNAL(
                "itemSelectionChanged()"),
            self.onTreeSelect)

        w.connect(self.treeWidget,QtCore.SIGNAL(
                "itemChanged(QTreeWidgetItem*, int)"),
            self.sig_itemChanged)

        w.connect(self.treeWidget,QtCore.SIGNAL(
                "itemCollapsed(QTreeWidgetItem*)"),
            self.sig_itemCollapsed)

        w.connect(self.treeWidget,QtCore.SIGNAL(
                "itemExpanded(QTreeWidgetItem*)"),
            self.sig_itemExpanded)

        self.ev_filter = leoQtEventFilter(c,w=self,tag='tree')
        tw.installEventFilter(self.ev_filter)

        c.setChanged(False)
    #@-node:ekr.20081121105001.159:qtTree.initAfterLoad
    #@+node:ekr.20081121105001.403:qtTree.setBindings & helper
    def setBindings (self):

        '''Create master bindings for all headlines.'''

        tree = self ; k = self.c.k


        # # g.trace('self',self,'canvas',self.canvas)

        # tree.setBindingsHelper()

        # tree.setCanvasBindings(self.canvas)

        # k.completeAllBindingsForWidget(self.canvas)

        # k.completeAllBindingsForWidget(self.bindingWidget)

    #@+node:ekr.20081121105001.404:qtTree.setBindingsHelper
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
    #@-node:ekr.20081121105001.404:qtTree.setBindingsHelper
    #@-node:ekr.20081121105001.403:qtTree.setBindings & helper
    #@+node:ekr.20081121105001.405:qtTree.setCanvasBindings
    def setCanvasBindings (self,canvas):

        c = self.c ; k = c.k

        # c.bind(canvas,'<Key>',k.masterKeyHandler)
        # c.bind(canvas,'<Button-1>',self.onTreeClick)
        # c.bind(canvas,'<Button-3>',self.onTreeRightClick)
        # # c.bind(canvas,'<FocusIn>',self.onFocusIn)

        #@    << make bindings for tagged items on the canvas >>
        #@+node:ekr.20081121105001.406:<< make bindings for tagged items on the canvas >>
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
        #@-node:ekr.20081121105001.406:<< make bindings for tagged items on the canvas >>
        #@nl
        #@    << create baloon bindings for tagged items on the canvas >>
        #@+node:ekr.20081121105001.407:<< create baloon bindings for tagged items on the canvas >>
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
        #@-node:ekr.20081121105001.407:<< create baloon bindings for tagged items on the canvas >>
        #@nl
    #@-node:ekr.20081121105001.405:qtTree.setCanvasBindings
    #@+node:ekr.20081121105001.408:get_name (qtTree)
    def getName (self):

        name = 'canvas(tree)' # Must start with canvas.

        return name
    #@-node:ekr.20081121105001.408:get_name (qtTree)
    #@-node:ekr.20081121105001.401: Birth... (qt Tree)
    #@+node:ekr.20081121105001.409:Config... (qtTree)
    #@+node:ekr.20081121105001.410:do-nothin config stuff
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
    #@-node:ekr.20081121105001.410:do-nothin config stuff
    #@+node:ekr.20081121105001.411:setConfigIvars
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
    #@-node:ekr.20081121105001.411:setConfigIvars
    #@-node:ekr.20081121105001.409:Config... (qtTree)
    #@+node:ekr.20081121105001.412:Drawing... (qtTree)
    #@+node:ekr.20081121105001.413:allAncestorsExpanded
    def allAncestorsExpanded (self,p):

        for p in p.self_and_parents_iter():
            if not p.isExpanded():
                return False
        else:
            return True
    #@-node:ekr.20081121105001.413:allAncestorsExpanded
    #@+node:ekr.20081121105001.414:full_redraw & helpers
    def full_redraw (self,scroll=False,forceDraw=False): # forceDraw not used.

        '''Redraw all visible nodes of the tree'''

        trace = False; verbose = False
        c = self.c ; w = self.treeWidget
        if not w: return
        if self.redrawing:
            g.trace('***** already drawing',g.callers(5))
            return

        # Bug fix: 2008/11/10
        self.expandAllAncestors(c.currentPosition())

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
                    pass
                elif p and self.redrawCount > 1:
                    g.trace('Error: no current item: %s' % (p.headString()))

            if 0: # This causes horizontal scrolling on Ubuntu.
                item = w.currentItem()
                if item:
                    w.scrollToItem(item,
                        QtGui.QAbstractItemView.PositionAtCenter)

            # Necessary to get the tree drawn initially.
            w.repaint()

            c.requestRedrawFlag= False
            self.redrawing = False
            self.fullDrawing = False
            if trace:
                if verbose: tstop()
                g.trace('%s: drew %3s nodes' % (
                    self.redrawCount,self.nodeDrawCount),g.callers(5))

    redraw = full_redraw # Compatibility
    redraw_now = full_redraw
    #@+node:ekr.20081121105001.415:initData
    def initData (self):

        self.tnodeDict = {} # keys are tnodes, values are lists of items (p,it)
        self.vnodeDict = {} # keys are vnodes, values are lists of items (p,it)
        self.itemsDict = {} # keys are items, values are positions
        self.parentsDict = {}
        self._editWidgetPosition = None
        self._editWidget = None
        self._editWidgetWrapper = None
    #@nonl
    #@-node:ekr.20081121105001.415:initData
    #@+node:ekr.20081121105001.164:drawNode
    def drawNode (self,p,dummy=False):

        c = self.c ; w = self.treeWidget ; trace = False
        self.nodeDrawCount += 1

        # Allocate the qt tree item.
        parent = p.parent()
        itemOrTree = self.parentsDict.get(parent and parent.v,w)

        if trace and not self.fullDrawing:
            g.trace(id(itemOrTree),parent and parent.headString())

        item = QtGui.QTreeWidgetItem(itemOrTree)
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)

        # Draw the headline and the icon.
        item.setText(0,p.headString())
        icon = self.getIcon(p)
        if icon: item.setIcon(0,icon)

        if dummy: return item

        # Remember the associatiation of item with p, and vice versa.
        self.itemsDict[item] = p.copy()
        self.parentsDict[p.v] = item 

        # Remember the association of p.v with (p,item)
        aList = self.vnodeDict.get(p.v,[])
        data = p.copy(),item
        aList.append(data)
        self.vnodeDict[p.v] = aList

        # Remember the association of p.v.t with (p,item).
        aList = self.tnodeDict.get(p.v.t,[])
        data = p.copy(),item
        aList.append(data)
        self.tnodeDict[p.v.t] = aList

        return item
    #@-node:ekr.20081121105001.164:drawNode
    #@+node:ekr.20081121105001.416:drawTree
    def drawTree (self,p):

        trace = False
        c = self.c ; w = self.treeWidget

        p = p.copy()

        if trace: g.trace(
            'children?',p.hasChildren(),
            'expanded?',p.isExpanded(),p.headString())

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
                if 0: # Requires a full redraw in the expansion code.
                    # Just draw one dummy child.
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
    #@-node:ekr.20081121105001.416:drawTree
    #@+node:ekr.20081121105001.417:drawIcon
    def drawIcon (self,p):

        '''Redraw the icon at p.
        This is called from leoFind.changeSelection.'''

        w = self.treeWidget
        parent = p.parent()
        itemOrTree = self.parentsDict.get(parent and parent.v,w)
        item = QtGui.QTreeWidgetItem(itemOrTree)

        icon = self.getIcon(p)
        if icon: item.setIcon(0,icon)
    #@-node:ekr.20081121105001.417:drawIcon
    #@-node:ekr.20081121105001.414:full_redraw & helpers
    #@+node:ekr.20081121105001.418:getIcon & getIconImage
    def getIcon(self,p):

        '''Return the proper icon for position p.'''

        p.v.iconVal = val = p.v.computeIcon()
        return self.getIconImage(val)

    def getIconImage(self,val):

        return g.app.gui.getIconImage(
            "box%02d.GIF" % val)

    #@-node:ekr.20081121105001.418:getIcon & getIconImage
    #@+node:ekr.20081121105001.419:redraw_after_clone
    def redraw_after_clone (self):

        self.full_redraw()
    #@-node:ekr.20081121105001.419:redraw_after_clone
    #@+node:ekr.20081121105001.420:redraw_after_contract
    def redraw_after_contract (self):

        self.full_redraw()
    #@-node:ekr.20081121105001.420:redraw_after_contract
    #@+node:ekr.20081121105001.421:redraw_after_delete
    def redraw_after_delete (self):

        self.full_redraw()


    #@-node:ekr.20081121105001.421:redraw_after_delete
    #@+node:ekr.20081121105001.422:redraw_after_expand & helper
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
    #@+node:ekr.20081121105001.423:removeFromDicts
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
    #@-node:ekr.20081121105001.423:removeFromDicts
    #@-node:ekr.20081121105001.422:redraw_after_expand & helper
    #@+node:ekr.20081121105001.424:redraw_after_icons_changed
    def redraw_after_icons_changed (self,all=False):

        g.trace('should not be called',g.callers(4))

        c = self.c ; p = c.currentPosition()

        if all:
            self.full_redraw()
        else:
            self.updateIcon(p)


    #@-node:ekr.20081121105001.424:redraw_after_icons_changed
    #@+node:ekr.20081121105001.425:redraw_after_insert
    def redraw_after_insert (self):

        self.full_redraw()
    #@-node:ekr.20081121105001.425:redraw_after_insert
    #@+node:ekr.20081121105001.426:redraw_after_move_down
    def redraw_after_move_down (self):

        self.full_redraw()
    #@nonl
    #@-node:ekr.20081121105001.426:redraw_after_move_down
    #@+node:ekr.20081121105001.427:redraw_after_move_left
    def redraw_after_move_left (self):

        self.full_redraw()
    #@nonl
    #@-node:ekr.20081121105001.427:redraw_after_move_left
    #@+node:ekr.20081121105001.428:redraw_after_move_right
    def redraw_after_move_right (self):

        if 0: # now done in c.moveOutlineRight.
            c = self.c ; p = c.currentPosition()
            parent = p.parent()
            if parent: parent.expand()


        # g.trace('parent',c.currentPosition().parent() or "non")

        self.full_redraw()
    #@-node:ekr.20081121105001.428:redraw_after_move_right
    #@+node:ekr.20081121105001.429:redraw_after_move_up
    def redraw_after_move_up (self):

        self.full_redraw()
    #@-node:ekr.20081121105001.429:redraw_after_move_up
    #@+node:ekr.20081121105001.430:redraw_after_select
    def redraw_after_select (self):

        '''Redraw the screen after selecting a node.'''

        pass # It is quite wrong to do an automatic redraw after select.
    #@-node:ekr.20081121105001.430:redraw_after_select
    #@+node:ekr.20081121105001.431:updateIcon
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
    #@-node:ekr.20081121105001.431:updateIcon
    #@-node:ekr.20081121105001.412:Drawing... (qtTree)
    #@+node:ekr.20081121105001.432:Event handlers... (qtTree)
    #@+node:ekr.20081121105001.433:Click Box...
    #@+node:ekr.20081121105001.434:onClickBoxClick
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
    #@-node:ekr.20081121105001.434:onClickBoxClick
    #@+node:ekr.20081121105001.435:onClickBoxRightClick
    def onClickBoxRightClick(self, event, p=None):
        #g.trace()
        return 'break'
    #@nonl
    #@-node:ekr.20081121105001.435:onClickBoxRightClick
    #@+node:ekr.20081121105001.436:onPlusBoxRightClick
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
    #@-node:ekr.20081121105001.436:onPlusBoxRightClick
    #@-node:ekr.20081121105001.433:Click Box...
    #@+node:ekr.20081121105001.437:findEditWidget
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
    #@-node:ekr.20081121105001.437:findEditWidget
    #@+node:ekr.20081121105001.438:Icon Box...
    #@+node:ekr.20081121105001.439:onIconBoxClick
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
    #@-node:ekr.20081121105001.439:onIconBoxClick
    #@+node:ekr.20081121105001.440:onIconBoxRightClick
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
    #@-node:ekr.20081121105001.440:onIconBoxRightClick
    #@+node:ekr.20081121105001.441:onIconBoxDoubleClick
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
    #@-node:ekr.20081121105001.441:onIconBoxDoubleClick
    #@-node:ekr.20081121105001.438:Icon Box...
    #@+node:ekr.20081121105001.161:onItemDoubleClicked
    def onItemDoubleClicked (self,item,col):

        c = self.c ; w = self.treeWidget
        w.setCurrentItem(item) # Must do this first.
        w.editItem(item)
        e = w.itemWidget(item,0)
        if not e:
            return g.trace('*** no e')
        p = self.itemsDict.get(item)
        if not p:
            return g.trace('*** no p')
        # Hook up the widget to Leo's core.
        e.connect(e,
            QtCore.SIGNAL("textEdited(QTreeWidgetItem*,int)"),
            self.onHeadChanged)
        self._editWidgetPosition = p.copy()
        self._editWidget = e
        self._editWidgetWrapper = leoQtHeadlineWidget(
            widget=e,name='head',c=c)
        e.setObjectName('headline')
    #@-node:ekr.20081121105001.161:onItemDoubleClicked
    #@+node:ekr.20081121105001.162:onTreeSelect
    def onTreeSelect(self):

        '''Select the proper position when a tree node is selected.'''

        trace = False ; verbose = False
        c = self.c ; w = self.treeWidget 

        if self.selecting:
            if trace: g.trace('already selecting')
            return
        if self.redrawing:
            if trace: g.trace('drawing')
            return

        item = w.currentItem()
        if trace and verbose: g.trace('item',item)
        p = self.itemsDict.get(item)
        if p:
            if trace: g.trace(p and p.headString())
            c.frame.tree.select(p) # The crucial hook.
            # g.trace(g.callers())
            c.outerUpdate()
        else:
            # An error: we are not redrawing.
            g.trace('no p for item: %s' % item,g.callers(4))
    #@nonl
    #@-node:ekr.20081121105001.162:onTreeSelect
    #@+node:ekr.20081121105001.442:setCurrentItem
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
    #@-node:ekr.20081121105001.442:setCurrentItem
    #@+node:ekr.20081121105001.443:sig_itemChanged
    def sig_itemChanged(self, item, col):

        '''Handle a change event in a headline.
        This only gets called when the user hits return.'''

        # Ignore changes when redrawing.
        if self.redrawing:
            return

        p = self.itemsDict.get(item)
        if p:
            # so far, col is always 0
            s = g.app.gui.toUnicode(item.text(col))
            p.setHeadString(s)
            # g.trace("changed: ",p.headString(),g.callers(4))

        # Make sure to end editing.
        self._editWidget = None
        self._editWidgetPosition = None
        self._editWidgetWrapper = None

    #@-node:ekr.20081121105001.443:sig_itemChanged
    #@+node:ekr.20081121105001.444:sig_itemCollapsed
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
    #@-node:ekr.20081121105001.444:sig_itemCollapsed
    #@+node:ekr.20081121105001.445:sig_itemExpanded
    def sig_itemExpanded (self,item):

        '''Handle and tree-expansion event.'''

        # The difficult case is when the user clicks the expansion box.

        trace = False ; verbose = True
        c = self.c ; p = c.currentPosition() ; w = self.treeWidget

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
            self.full_redraw()
        finally:
            self.expanding = False
            self.setCurrentItem()

        # try:
            # redraw = False
            # p2 = self.itemsDict.get(item)
            # if p2:
                # if trace: g.trace(p2)
                # if not p2.isExpanded():
                    # p2.expand()
                # c.setCurrentPosition(p2)
                # self.full_redraw()
                # redraw = True
            # else:
                # g.trace('Error no p2')

        # finally:
            # self.expanding = False
            # if redraw:
                # item = self.setCurrentItem()
    #@-node:ekr.20081121105001.445:sig_itemExpanded
    #@+node:ekr.20081121105001.446:tree.OnPopup & allies
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
    #@+node:ekr.20081121105001.447:OnPopupFocusLost
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
    #@-node:ekr.20081121105001.447:OnPopupFocusLost
    #@+node:ekr.20081121105001.448:createPopupMenu
    def createPopupMenu (self,event):

        c = self.c ; frame = c.frame

        # self.popupMenu = menu = Qt.Menu(g.app.root, tearoff=0)

        # # Add the Open With entries if they exist.
        # if g.app.openWithTable:
            # frame.menu.createOpenWithMenuItemsFromTable(menu,g.app.openWithTable)
            # table = (("-",None,None),)
            # frame.menu.createMenuEntries(menu,table)

        #@    << Create the menu table >>
        #@+node:ekr.20081121105001.449:<< Create the menu table >>
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
        #@-node:ekr.20081121105001.449:<< Create the menu table >>
        #@nl

        # # New in 4.4.  There is no need for a dontBind argument because
        # # Bindings from tables are ignored.
        # frame.menu.createMenuEntries(menu,table)
    #@-node:ekr.20081121105001.448:createPopupMenu
    #@+node:ekr.20081121105001.450:enablePopupMenuItems
    def enablePopupMenuItems (self,v,event):

        """Enable and disable items in the popup menu."""

        c = self.c 

        # menu = self.popupMenu

        #@    << set isAtRoot and isAtFile if v's tree contains @root or @file nodes >>
        #@+node:ekr.20081121105001.451:<< set isAtRoot and isAtFile if v's tree contains @root or @file nodes >>
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
        #@-node:ekr.20081121105001.451:<< set isAtRoot and isAtFile if v's tree contains @root or @file nodes >>
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
    #@-node:ekr.20081121105001.450:enablePopupMenuItems
    #@+node:ekr.20081121105001.452:showPopupMenu
    def showPopupMenu (self,event):

        """Show a popup menu."""

        # c = self.c ; menu = self.popupMenu

        # g.app.gui.postPopupMenu(c, menu, event.x_root, event.y_root)

        # self.popupMenu = None

        # # Set the focus immediately so we know when we lose it.
        # #c.widgetWantsFocus(menu)
    #@-node:ekr.20081121105001.452:showPopupMenu
    #@-node:ekr.20081121105001.446:tree.OnPopup & allies
    #@-node:ekr.20081121105001.432:Event handlers... (qtTree)
    #@+node:ekr.20081121105001.453:Focus (qtTree)
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
    #@-node:ekr.20081121105001.453:Focus (qtTree)
    #@+node:ekr.20081121105001.454:Selecting & editing... (qtTree)
    #@+node:ekr.20081124113700.11:editPosition
    def editPosition(self):

        p = self._editWidgetPosition

        return p
    #@-node:ekr.20081124113700.11:editPosition
    #@+node:ekr.20081121105001.160:edit_widget
    def edit_widget (self,p):

        """Returns the Qt.Edit widget for position p."""

        w = self._editWidgetWrapper

        if p and p == self._editWidgetPosition:
            return w
        else:
            return None

        # Decouple all of the core's headline code.
        # Except for over-ridden methods.
    #@-node:ekr.20081121105001.160:edit_widget
    #@+node:ekr.20081121105001.455:beforeSelectHint
    def beforeSelectHint (self,p,old_p):

        w = self.treeWidget ; trace = True

        if self.selecting:
            return g.trace('*** Error: already selecting',g.callers(4))

        if self.redrawing:
            if trace: g.trace('already redrawing')
            return

        if 0: # This is too soon: a unit test fails.
            # Make *sure* we don't access an invalid entry.
            self._editWidgetPosition = None
            self._editWidget = None
            self._editWidgetWrapper = None

        # Disable onTextChanged.
        self.selecting = True
    #@-node:ekr.20081121105001.455:beforeSelectHint
    #@+node:ekr.20081121105001.456:afterSelectHint
    def afterSelectHint (self,p,old_p):

        c = self.c ; w = self.treeWidget ; trace = False

        self.selecting = False

        if not p:
            return g.trace('Error: no p')
        if p != c.currentPosition():
            return g.trace('Error: p is not c.currentPosition()')
        if self.redrawing:
            return g.trace('Error: already redrawing')
        if trace:
            g.trace(p.headString(),g.callers(4))

        # setCurrentItem sets & clears .selecting ivar
        self.setCurrentItem()
        # item = w.currentItem()
        # if item:
        #    w.scrollToItem(item,
        #        QtGui.QAbstractItemView.PositionAtCenter)
    #@-node:ekr.20081121105001.456:afterSelectHint
    #@+node:ekr.20081121105001.457:setHeadline
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
    #@-node:ekr.20081121105001.457:setHeadline
    #@+node:ekr.20081121105001.156:editLabel (override)
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
    #@-node:ekr.20081121105001.156:editLabel (override)
    #@+node:ekr.20081121105001.458:editLabelHelper
    def editLabelHelper (self,item):

        '''A helper shared by editLabel and onItemDoubleClicked.'''
    #@-node:ekr.20081121105001.458:editLabelHelper
    #@+node:ekr.20081121105001.163:onHeadChanged
    # Tricky code: do not change without careful thought and testing.

    def onHeadChanged (self,p,undoType='Typing',s=None):

        '''Officially change a headline.'''

        trace = False ; verbose = True
        c = self.c ; u = c.undoer
        e = self._editWidget
        p = self._editWidgetPosition
        w = g.app.gui.get_focus()

        # These are not errors: sig_itemChanged may
        # have been called first.
        if trace and verbose:
            if not e:  g.trace('No e',g.callers(4))
            if e != w: g.trace('e != w',e,w,g.callers(4))
            if not p:  g.trace('No p')

        if e and e == w and p:
            s = e.text() ; len_s = len(s)
            s = g.app.gui.toUnicode(s)
            oldHead = p.headString()
            changed = s != oldHead
            if trace: g.trace('changed',changed,repr(s),g.callers(4))
            if changed:
                p.initHeadString(s)
                undoData = u.beforeChangeNodeContents(p,oldHead=oldHead)
                if not c.changed: c.setChanged(True)
                # New in Leo 4.4.5: we must recolor the body because
                # the headline may contain directives.
                c.frame.body.recolor(p,incremental=True)
                dirtyVnodeList = p.setDirty()
                u.afterChangeNodeContents(p,undoType,undoData,
                    dirtyVnodeList=dirtyVnodeList)

        # End the editing!
        self._editWidget = None
        self._editWidgetPosition = None
        self._editWidgetWrapper = None

        # This is a crucial shortcut.
        if g.unitTesting: return

        c.redraw(scroll=False)
        if self.stayInTree:
            c.treeWantsFocus()
        else:
            c.bodyWantsFocus()
    #@nonl
    #@-node:ekr.20081121105001.163:onHeadChanged
    #@-node:ekr.20081121105001.454:Selecting & editing... (qtTree)
    #@-others
#@-node:ekr.20081121105001.400:class leoQtTree
#@+node:ekr.20081121105001.459:class leoQtTreeTab
class leoQtTreeTab (leoFrame.leoTreeTab):

    '''A class representing a tabbed outline pane drawn with Qt.'''

    #@    @+others
    #@+node:ekr.20081121105001.460: Birth & death
    #@+node:ekr.20081121105001.461: ctor (leoTreeTab)
    def __init__ (self,c,parentFrame,chapterController):

        leoFrame.leoTreeTab.__init__ (self,c,chapterController,parentFrame)
            # Init the base class.  Sets self.c, self.cc and self.parentFrame.

        self.tabNames = [] # The list of tab names.  Changes when tabs are renamed.

        self.createControl()
    #@-node:ekr.20081121105001.461: ctor (leoTreeTab)
    #@+node:ekr.20081121105001.462:tt.createControl
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
    #@-node:ekr.20081121105001.462:tt.createControl
    #@-node:ekr.20081121105001.460: Birth & death
    #@+node:ekr.20081121105001.463:Tabs...
    #@+node:ekr.20081121105001.464:tt.createTab
    def createTab (self,tabName,select=True):

        tt = self

        # if tabName not in tt.tabNames:
            # tt.tabNames.append(tabName)
            # tt.setNames()
    #@-node:ekr.20081121105001.464:tt.createTab
    #@+node:ekr.20081121105001.465:tt.destroyTab
    def destroyTab (self,tabName):

        tt = self

        # if tabName in tt.tabNames:
            # tt.tabNames.remove(tabName)
            # tt.setNames()
    #@-node:ekr.20081121105001.465:tt.destroyTab
    #@+node:ekr.20081121105001.466:tt.selectTab
    def selectTab (self,tabName):

        tt = self

        # if tabName not in self.tabNames:
            # tt.createTab(tabName)

        # tt.cc.selectChapterByName(tabName)

        # self.c.redraw()
        # self.c.outerUpdate()
    #@-node:ekr.20081121105001.466:tt.selectTab
    #@+node:ekr.20081121105001.467:tt.setTabLabel
    def setTabLabel (self,tabName):

        tt = self
    #     tt.chapterVar.set(tabName)
    #@-node:ekr.20081121105001.467:tt.setTabLabel
    #@+node:ekr.20081121105001.468:tt.setNames
    def setNames (self):

        '''Recreate the list of items.'''

        # tt = self
        # names = tt.tabNames[:]
        # if 'main' in names: names.remove('main')
        # names.sort()
        # names.insert(0,'main')
        # tt.chapterMenu.setitems(names)
    #@-node:ekr.20081121105001.468:tt.setNames
    #@-node:ekr.20081121105001.463:Tabs...
    #@-others
#@nonl
#@-node:ekr.20081121105001.459:class leoQtTreeTab
#@+node:ekr.20081121105001.469:class qtMenuWrapper (QtMenu,leoQtMenu)
class qtMenuWrapper (QtGui.QMenu,leoQtMenu):

    def __init__ (self,c,frame,parent):

        assert c
        assert frame
        QtGui.QMenu.__init__(self,parent)
        leoQtMenu.__init__(self,frame)

    def __repr__(self):

        return '<qtMenuWrapper %s>' % self.leo_label or 'unlabeled'
#@-node:ekr.20081121105001.469:class qtMenuWrapper (QtMenu,leoQtMenu)
#@+node:ekr.20081121105001.470:class qtSearchWidget
class qtSearchWidget:

    """A dummy widget class to pass to Leo's core find code."""

    def __init__ (self):

        self.insertPoint = 0
        self.selection = 0,0
        self.bodyCtrl = self
        self.body = self
        self.text = None
#@nonl
#@-node:ekr.20081121105001.470:class qtSearchWidget
#@-node:ekr.20081121105001.194:Frame and component classes...
#@+node:ekr.20081121105001.471:Gui wrapper
#@+node:ekr.20081121105001.472:class leoQtGui
class leoQtGui(leoGui.leoGui):

    '''A class implementing Leo's Qt gui.'''

    #@    @+others
    #@+node:ekr.20081121105001.473:  Birth & death (qtGui)
    #@+node:ekr.20081121105001.474: qtGui.__init__
    def __init__ (self):

        # Initialize the base class.
        leoGui.leoGui.__init__(self,'qt')

        self.qtApp = QtGui.QApplication(sys.argv)

        self.bodyTextWidget  = leoQtBaseTextWidget
        self.plainTextWidget = leoQtBaseTextWidget

        self.iconimages = {} # Image cache set by getIconImage().

        self.mGuiName = 'qt'
    #@-node:ekr.20081121105001.474: qtGui.__init__
    #@+node:ekr.20081121105001.475:createKeyHandlerClass (qtGui)
    def createKeyHandlerClass (self,c,useGlobalKillbuffer=True,useGlobalRegisters=True):

        ### Use the base class
        return leoKeys.keyHandlerClass(c,useGlobalKillbuffer,useGlobalRegisters)

        ### return qtKeyHandlerClass(c,useGlobalKillbuffer,useGlobalRegisters)
    #@-node:ekr.20081121105001.475:createKeyHandlerClass (qtGui)
    #@+node:ekr.20081121105001.476:runMainLoop (qtGui)
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
    #@-node:ekr.20081121105001.476:runMainLoop (qtGui)
    #@+node:ekr.20081121105001.477:destroySelf
    def destroySelf (self):
        QtCore.pyqtRemoveInputHook()
        self.qtApp.exit()
    #@nonl
    #@-node:ekr.20081121105001.477:destroySelf
    #@-node:ekr.20081121105001.473:  Birth & death (qtGui)
    #@+node:ekr.20081121105001.183:Clipboard
    def replaceClipboardWith (self,s):

        '''Replace the clipboard with the string s.'''

        cb = self.qtApp.clipboard()
        if cb:
            cb.clear()
            s = g.app.gui.toUnicode(s)
            cb.setText(s)
            # g.trace(len(s),type(s))

    def getTextFromClipboard (self):

        '''Get a unicode string from the clipboard.'''

        cb = self.qtApp.clipboard()
        s = cb and cb.text() or ''
        s = g.app.gui.toUnicode(s)
        # g.trace (len(s),type(s))
        return s
    #@nonl
    #@-node:ekr.20081121105001.183:Clipboard
    #@+node:ekr.20081121105001.478:Do nothings
    def color (self,color):         return None

    def createRootWindow(self):     pass

    def killGui(self,exitFlag=True):
        """Destroy a gui and terminate Leo if exitFlag is True."""

    def recreateRootWindow(self):
        """Create the hidden root window of a gui
        after a previous gui has terminated with killGui(False)."""


    #@-node:ekr.20081121105001.478:Do nothings
    #@+node:ekr.20081121105001.479:Dialogs & panels
    #@+node:ekr.20081122170423.1:alert (qtGui)
    def alert (self,message):

        if g.unitTesting: return

        b = QtGui.QMessageBox
        d = b(None)
        d.setWindowTitle('Alert')
        d.setText(message)
        d.setIcon(b.Warning)
        yes = d.addButton('Ok',b.YesRole)
        d.exec_()
    #@nonl
    #@-node:ekr.20081122170423.1:alert (qtGui)
    #@+node:ekr.20081121105001.480:makeFilter
    def makeFilter (self,filetypes):

        '''Return the Qt-style dialog filter from filetypes list.'''

        filters = ['%s (%s)' % (z) for z in filetypes]

        return ';;'.join(filters)
    #@-node:ekr.20081121105001.480:makeFilter
    #@+node:ekr.20081121105001.481:not used
    def runAskOkCancelNumberDialog(self,c,title,message):

        """Create and run askOkCancelNumber dialog ."""

        if g.unitTesting: return None
        g.trace('not ready yet')

    def runAskOkCancelStringDialog(self,c,title,message):

        """Create and run askOkCancelString dialog ."""

        if g.unitTesting: return None
        g.trace('not ready yet')


    #@-node:ekr.20081121105001.481:not used
    #@+node:ekr.20081121105001.482:qtGui panels
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

    #@-node:ekr.20081121105001.482:qtGui panels
    #@+node:ekr.20081121105001.483:runAboutLeoDialog
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
    #@-node:ekr.20081121105001.483:runAboutLeoDialog
    #@+node:ekr.20081121105001.484:runAskLeoIDDialog
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
        return g.app.gui.toUnicode(s)
    #@nonl
    #@-node:ekr.20081121105001.484:runAskLeoIDDialog
    #@+node:ekr.20081121105001.485:runAskOkDialog
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

    #@-node:ekr.20081121105001.485:runAskOkDialog
    #@+node:ekr.20081121105001.486:runAskYesNoCancelDialog
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
    #@-node:ekr.20081121105001.486:runAskYesNoCancelDialog
    #@+node:ekr.20081121105001.487:runAskYesNoDialog
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

    #@-node:ekr.20081121105001.487:runAskYesNoDialog
    #@+node:ekr.20081121105001.488:runOpenFileDialog
    def runOpenFileDialog(self,title,filetypes,defaultextension,multiple=False):

        """Create and run an Qt open file dialog ."""

        parent = None
        filter = self.makeFilter(filetypes)
        s = QtGui.QFileDialog.getOpenFileName(parent,title,os.curdir,filter)
        s = g.app.gui.toUnicode(s)
        if multiple:
            return [s]
        else:
            return s
    #@nonl
    #@-node:ekr.20081121105001.488:runOpenFileDialog
    #@+node:ekr.20081121105001.489:runSaveFileDialog
    def runSaveFileDialog(self,initialfile,title,filetypes,defaultextension):

        """Create and run an Qt save file dialog ."""

        parent = None
        filter = self.makeFilter(filetypes)
        s = QtGui.QFileDialog.getSaveFileName(parent,title,os.curdir,filter)
        return g.app.gui.toUnicode(s)
    #@-node:ekr.20081121105001.489:runSaveFileDialog
    #@+node:ekr.20081121105001.490:runScrolledMessageDialog
    def runScrolledMessageDialog (self, title='Message', label= '', msg='', c=None, **kw):

        if g.unitTesting: return None

        def send(title=title, label=label, msg=msg, c=c, kw=kw):
            return g.doHook('scrolledMessage', title=title, label=label, msg=msg, c=c, **kw)

        if not c or not c.exists:
            #@        << no c error>>
            #@+node:leohag.20081205043707.12:<< no c error>>
            g.es_print_error("The qt plugin requires calls to g.app.gui.scrolledMessageDialog to include 'c' as a keyword argument.\n\t%s"% g,callers())
            #@nonl
            #@-node:leohag.20081205043707.12:<< no c error>>
            #@nl
        else:        
            retval = send()
            if retval: return retval
            #@        << load scrolledmessage plugin >>
            #@+node:leohag.20081205043707.14:<< load scrolledmessage plugin >>
            import leo.core.leoPlugins as leoPlugins
            sm = leoPlugins.getPluginModule('scrolledmessage')

            if not sm:
                sm = leoPlugins.loadOnePlugin('scrolledmessage',verbose=True)
                if sm:
                    g.es('scrolledmessage plugin loaded.', color='blue')
                    sm.onCreate('tag',{'c':c})
            #@-node:leohag.20081205043707.14:<< load scrolledmessage plugin >>
            #@nl
            retval = send()
            if retval: return retval
            #@        << no dialog error >>
            #@+node:leohag.20081205043707.11:<< no dialog error >>
            g.es_print_error('The handler for the "scrolledMessage" hook appears to be missing or not working.\n\t%s'%g.callers())
            #@nonl
            #@-node:leohag.20081205043707.11:<< no dialog error >>
            #@nl

        #@    << emergency fallback >>
        #@+node:leohag.20081205043707.13:<< emergency fallback >>

        b = QtGui.QMessageBox
        d = b(None) # c.frame.top)
        d.setWindowFlags(QtCore.Qt.Dialog) # That is, not a fixed size dialog.

        d.setWindowTitle(title)
        if msg: d.setText(msg)
        d.setIcon(b.Information)
        yes = d.addButton('Ok',b.YesRole)
        d.exec_()
        #@nonl
        #@-node:leohag.20081205043707.13:<< emergency fallback >>
        #@nl
    #@-node:ekr.20081121105001.490:runScrolledMessageDialog
    #@-node:ekr.20081121105001.479:Dialogs & panels
    #@+node:ekr.20081121105001.491:Focus (qtGui)
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
    #@-node:ekr.20081121105001.491:Focus (qtGui)
    #@+node:ekr.20081121105001.492:Font
    #@+node:ekr.20081121105001.493:qtGui.getFontFromParams
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
    #@-node:ekr.20081121105001.493:qtGui.getFontFromParams
    #@-node:ekr.20081121105001.492:Font
    #@+node:ekr.20081121105001.494:getFullVersion
    def getFullVersion (self,c):

        try:
            qtLevel = 'version %s' % QtCore.QT_VERSION
        except Exception:
            # g.es_exception()
            qtLevel = '<qtLevel>'

        return 'qt %s' % (qtLevel)
    #@-node:ekr.20081121105001.494:getFullVersion
    #@+node:ekr.20081121105001.495:Icons
    #@+node:ekr.20081121105001.496:attachLeoIcon
    def attachLeoIcon (self,window):

        """Attach a Leo icon to the window."""

        icon = self.getIconImage('leoApp.ico')

        window.setWindowIcon(icon)
    #@-node:ekr.20081121105001.496:attachLeoIcon
    #@+node:ekr.20081121105001.497:getIconImage
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
    #@-node:ekr.20081121105001.497:getIconImage
    #@+node:ekr.20081123003126.2:getTreeImage (test)
    def getTreeImage (self,c,path):

        image = QtGui.QPixmap(path)

        if image.height() > 0 and image.width() > 0:
            return image,image.height()
        else:
            return None,None
    #@-node:ekr.20081123003126.2:getTreeImage (test)
    #@-node:ekr.20081121105001.495:Icons
    #@+node:ekr.20081121105001.498:Idle Time (to do)
    #@+node:ekr.20081121105001.499:qtGui.setIdleTimeHook
    def setIdleTimeHook (self,idleTimeHookHandler):

        # if self.root:
            # self.root.after_idle(idleTimeHookHandler)

        pass
    #@nonl
    #@-node:ekr.20081121105001.499:qtGui.setIdleTimeHook
    #@+node:ekr.20081121105001.500:setIdleTimeHookAfterDelay
    def setIdleTimeHookAfterDelay (self,idleTimeHookHandler):

        pass

        # if self.root:
            # g.app.root.after(g.app.idleTimeDelay,idleTimeHookHandler)
    #@-node:ekr.20081121105001.500:setIdleTimeHookAfterDelay
    #@-node:ekr.20081121105001.498:Idle Time (to do)
    #@+node:ekr.20081121105001.501:isTextWidget
    def isTextWidget (self,w):

        '''Return True if w is a Text widget suitable for text-oriented commands.'''

        if not w: return False

        return (
            isinstance(w,leoFrame.baseTextWidget) or
            isinstance(w,leoQtBody) or
            isinstance(w,leoQtBaseTextWidget)
        )

    #@-node:ekr.20081121105001.501:isTextWidget
    #@+node:ekr.20081121105001.502:toUnicode
    def toUnicode (self,s):

        if g.isPython3:
            return str(s)
        else:
            if type(s) == type('a'):
                return g.toUnicode(s,'utf-8',reportErrors=True)
            else:
                return unicode(s)
    #@-node:ekr.20081121105001.502:toUnicode
    #@+node:ekr.20081121105001.503:widget_name (qtGui)
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
    #@-node:ekr.20081121105001.503:widget_name (qtGui)
    #@+node:ekr.20081121105001.504:makeScriptButton (to do)
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
        #@+node:ekr.20081121105001.505:<< create the button b >>
        iconBar = c.frame.getIconBarObject()
        b = iconBar.add(text=buttonText)
        #@-node:ekr.20081121105001.505:<< create the button b >>
        #@nl
        #@    << define the callbacks for b >>
        #@+node:ekr.20081121105001.506:<< define the callbacks for b >>
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
        #@-node:ekr.20081121105001.506:<< define the callbacks for b >>
        #@nl
        b.configure(command=executeScriptCallback)
        c.bind(b,'<3>',deleteButtonCallback)
        if shortcut:
            #@        << bind the shortcut to executeScriptCallback >>
            #@+node:ekr.20081121105001.507:<< bind the shortcut to executeScriptCallback >>
            func = executeScriptCallback
            shortcut = k.canonicalizeShortcut(shortcut)
            ok = k.bindKey ('button', shortcut,func,buttonText)
            if ok:
                g.es_print('bound @button',buttonText,'to',shortcut,color='blue')
            #@-node:ekr.20081121105001.507:<< bind the shortcut to executeScriptCallback >>
            #@nl
        #@    << create press-buttonText-button command >>
        #@+node:ekr.20081121105001.508:<< create press-buttonText-button command >>
        aList = [g.choose(ch.isalnum(),ch,'-') for ch in buttonText]

        buttonCommandName = ''.join(aList)
        buttonCommandName = buttonCommandName.replace('--','-')
        buttonCommandName = 'press-%s-button' % buttonCommandName.lower()

        # This will use any shortcut defined in an @shortcuts node.
        k.registerCommand(buttonCommandName,None,executeScriptCallback,pane='button',verbose=False)
        #@-node:ekr.20081121105001.508:<< create press-buttonText-button command >>
        #@nl
    #@-node:ekr.20081121105001.504:makeScriptButton (to do)
    #@-others
#@-node:ekr.20081121105001.472:class leoQtGui
#@-node:ekr.20081121105001.471:Gui wrapper
#@+node:ekr.20081121105001.509:Non-essential
#@+node:ekr.20081121105001.510:class LeoQuickSearchWidget
import qt_quicksearch

def install_qt_quicksearch_tab(c):
    tabw = c.frame.top.tabWidget
    wdg = LeoQuickSearchWidget(c,tabw)
    tabw.addTab(wdg, "QuickSearch")

g.insqs = install_qt_quicksearch_tab

class LeoQuickSearchWidget(QtGui.QWidget):
    """ Real-time search widget """
    #@    @+others
    #@+node:ekr.20081121105001.511:methods
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
        g.trace("New text", self.ui.lineEdit.text())
        idx = 0
        self.ui.tableWidget.clear()
        for p in self.match_headlines(
            g.app.gui.toUnicode(self.ui.lineEdit.text())
        ):
            it = QtGui.QTableWidgetItem(p.headString())
            self.ps[idx] = p.copy()
            self.ui.tableWidget.setItem(idx, 0, it)
            idx+=1

        self.ui.tableWidget.setRowCount(idx)

        g.trace("Matches",idx)

    def cellClicked (self, row, column ) :
        p = self.ps[row]
        g.trace("Go to pos",p)
        self.c.selectPosition(p)

    def match_headlines(self, pat):

        c = self.c
        pat = pat.lower()
        for p in c.allNodes_iter():
            if pat in p.headString():
                yield p
        return 
    #@-node:ekr.20081121105001.511:methods
    #@-others
#@-node:ekr.20081121105001.510:class LeoQuickSearchWidget
#@+node:ekr.20081121105001.512:quickheadlines
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

        g.trace("quickheadlines update")
        self.requested = False
        self.listWidget.clear()
        p = self.c.currentPosition()
        for n in p.children_iter():
            self.listWidget.addItem(n.headString())



#@-node:ekr.20081121105001.512:quickheadlines
#@-node:ekr.20081121105001.509:Non-essential
#@+node:ekr.20081121105001.513:Key handling
#@+node:ekr.20081121105001.514:class leoKeyEvent
class leoKeyEvent:

    '''A gui-independent wrapper for gui events.'''

    def __init__ (self,event,c,w,tkKey):

        # Last minute-munges to keysym.
        d = {
            '\r':'Return',
            '\n':'Return',
            '\t':'Tab',
        }

        # The main ivars.
        self.actualEvent = event
        self.c      = c
        self.char   = tkKey
        self.keysym = d.get(tkKey,tkKey)
        self.w = self.widget = w # A leoQtX object

        # Auxiliary info.
        self.x      = hasattr(event,'x') and event.x or 0
        self.y      = hasattr(event,'y') and event.y or 0
        # Support for fastGotoNode plugin
        self.x_root = hasattr(event,'x_root') and event.x_root or 0
        self.y_root = hasattr(event,'y_root') and event.y_root or 0

    def __repr__ (self):

        return 'qtGui.leoKeyEvent: char: %s, keysym: %s' % (repr(self.char),repr(self.keysym))
#@-node:ekr.20081121105001.514:class leoKeyEvent
#@+node:ekr.20081121105001.166:class leoQtEventFilter
class leoQtEventFilter(QtCore.QObject):

    #@    << about internal bindings >>
    #@+node:ekr.20081121105001.167:<< about internal bindings >>
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
    #@-node:ekr.20081121105001.167:<< about internal bindings >>
    #@nl

    #@    @+others
    #@+node:ekr.20081121105001.168:eventFilter
    def eventFilter(self, obj, event):

        c = self.c ; k = c.k 
        trace = False ; verbose = True
        eventType = event.type()
        ev = QtCore.QEvent
        kinds = (ev.ShortcutOverride,ev.KeyPress,ev.KeyRelease)

        if eventType in kinds:
            tkKey,ch,ignore = self.toTkKey(event)
            aList = c.k.masterGuiBindingsDict.get('<%s>' %tkKey,[])

            if ignore:
                override = False
            elif self.isSpecialOverride(tkKey,ch):
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
                leoEvent = leoKeyEvent(event,c,w,ch) # ch was stroke
                ret = k.masterKeyHandler(leoEvent,stroke=stroke)
                c.outerUpdate()
            else:
                if trace: g.trace(self.tag,'unbound',tkKey)

        if trace: self.traceEvent(obj,event,tkKey,override)

        return override
    #@-node:ekr.20081121105001.168:eventFilter
    #@+node:ekr.20081121105001.169:toStroke
    def toStroke (self,tkKey,ch):

        k = self.c.k ; s = tkKey ; trace = False

        special = ('Alt','Ctrl','Control',)
        isSpecial = [True for z in special if s.find(z) > -1]

        if not isSpecial:
            # Keep the Tk spellings for special keys.
            ch2 = k.guiBindNamesDict.get(ch) # was inverseDict
            if trace: g.trace('ch',repr(ch),'ch2',repr(ch2))
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

        if trace: g.trace('tkKey',tkKey,'-->',s)
        return s
    #@-node:ekr.20081121105001.169:toStroke
    #@+node:ekr.20081121105001.170:toTkKey
    def toTkKey (self,event):

        mods = self.qtMods(event)

        keynum,text,toString,ch = self.qtKey(event)

        tkKey,ch,ignore = self.tkKey(
            event,mods,keynum,text,toString,ch)

        return tkKey,ch,ignore
    #@+node:ekr.20081121105001.171:isFKey
    def isFKey(self,ch):

        return (
            ch and len(ch) in (2,3) and
            ch[0].lower() == 'f' and
            ch[1:].isdigit()
        )
    #@-node:ekr.20081121105001.171:isFKey
    #@+node:ekr.20081121105001.172:qtKey
    def qtKey (self,event):

        '''Return the components of a Qt key event.'''

        keynum = event.key()
        text   = event.text()
        toString = QtGui.QKeySequence(keynum).toString()
        try:
            ch = chr(keynum)
        except ValueError:
            ch = ''
        ch       = g.app.gui.toUnicode(ch)
        text     = g.app.gui.toUnicode(text)
        toString = g.app.gui.toUnicode(toString)

        return keynum,text,toString,ch


    #@-node:ekr.20081121105001.172:qtKey
    #@+node:ekr.20081121105001.173:qtMods
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
    #@-node:ekr.20081121105001.173:qtMods
    #@+node:ekr.20081121105001.174:tkKey & helpers
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

        ch = text or toString # was ch
        return tkKey,ch,ignore
    #@+node:ekr.20081121105001.175:keyboardUpper1
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

    #@-node:ekr.20081121105001.175:keyboardUpper1
    #@+node:ekr.20081121105001.176:keyboardUpperLong
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
            "parenleft":    "parenleft", # Bug fix: 2008/11/24
            "parenright":   "parenright", # Bug fix: 2008/11/24
        }
        # g.trace(ch,d.get(ch))
        return d.get(ch)
    #@-node:ekr.20081121105001.176:keyboardUpperLong
    #@+node:ekr.20081121105001.177:shifted
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
    #@-node:ekr.20081121105001.177:shifted
    #@-node:ekr.20081121105001.174:tkKey & helpers
    #@-node:ekr.20081121105001.170:toTkKey
    #@+node:ekr.20081121105001.179:traceEvent
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
                'c',c,
                'tag: %s, kind: %s, in-state: %s, key: %s, override: %s' % (
                self.tag,kind,repr(c.k.inState()),tkKey,override))
                return

        # if trace: g.trace(self.tag,
            # 'bound in state: %s, key: %s, returns: %s' % (
            # k.getState(),tkKey,ret))

        if False and eventType not in ignore:
            g.trace('%3s:%s' % (eventType,'unknown'))
    #@-node:ekr.20081121105001.179:traceEvent
    #@+node:ekr.20081121105001.180: ctor
    def __init__(self,c,w,tag=''):

        # Init the base class.
        QtCore.QObject.__init__(self)

        self.c = c
        self.w = w      # A leoQtX object, *not* a Qt object.
        self.tag = tag

        # Pretend there is a binding for these characters.
        close_flashers = c.config.getString('close_flash_brackets') or ''
        open_flashers  = c.config.getString('open_flash_brackets') or ''
        self.flashers = open_flashers + close_flashers


    #@-node:ekr.20081121105001.180: ctor
    #@+node:ekr.20081121105001.181:isDangerous
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

        # g.trace(tkKey,ch,val)
        return val
    #@-node:ekr.20081121105001.181:isDangerous
    #@+node:ekr.20081121105001.182:isSpecialOverride
    def isSpecialOverride (self,tkKey,ch):

        # g.trace(repr(tkKey),repr(ch))

        if tkKey == 'Tab':
            return True
        elif len(tkKey) == 1:
            return True # Must process all ascii keys.
        elif ch in self.flashers:
            return True
        else:
            return False
    #@-node:ekr.20081121105001.182:isSpecialOverride
    #@-others
#@-node:ekr.20081121105001.166:class leoQtEventFilter
#@-node:ekr.20081121105001.513:Key handling
#@+node:ekr.20081204090029.1:Syntax coloring
#@+node:ekr.20081205131308.15:leoQtColorizer
class leoQtColorizer:

    '''An adaptor class that interfaces QSyntaxHighligher
    and the threading_colorizer plugin.'''

    #@    @+others
    #@+node:ekr.20081205131308.16:ctor (leoQtColorizer)
    def __init__ (self,c,w):

        self.c = c
        self.w = w

        # g.trace(self,c,w)

        self.count = 0 # For unit testing.
        self.enabled = True

        self.highlighter = leoQtSyntaxHighlighter(c,w)
        self.colorer = self.highlighter.colorer
    #@-node:ekr.20081205131308.16:ctor (leoQtColorizer)
    #@+node:ekr.20081205131308.18:colorize
    def colorize(self,p,incremental=False,interruptable=True):

        '''The main colorizer entry point.'''

        self.count += 1 # For unit testing.

        if self.enabled:
            self.highlighter.rehighlight()

        return "ok" # For unit testing.
    #@-node:ekr.20081205131308.18:colorize
    #@+node:ekr.20081207061047.10:entry points
    def disable (self):
        self.colorer.enabled=False

    def enable (self):
        self.colorer.enabled=True

    def interrupt(self):
        pass

    def isSameColorState (self):
        return False

    def kill (self):
        pass

    def scanColorDirectives(self,p):
        return self.colorer.scanColorDirectives(p)

    def updateSyntaxColorer (self,p):
        return self.colorer.updateSyntaxColorer(p)

    def useSyntaxColoring (self,p):
        return self.colorer.useSyntaxColoring(p)
    #@-node:ekr.20081207061047.10:entry points
    #@-others

#@-node:ekr.20081205131308.15:leoQtColorizer
#@+node:ekr.20081205131308.27:leoQtSyntaxHighlighter
class leoQtSyntaxHighlighter (QtGui.QSyntaxHighlighter):

    #@    @+others
    #@+node:ekr.20081205131308.1:ctor (leoQtSyntaxHighlighter)
    def __init__ (self,c,w):

        self.c = c
        self.w = w

        # Init the base class.
        QtGui.QSyntaxHighlighter.__init__(self,w)

        self.colorer = jEditColorizer(
            c,highlighter=self,
            w=c.frame.body.bodyCtrl)
    #@-node:ekr.20081205131308.1:ctor (leoQtSyntaxHighlighter)
    #@+node:ekr.20081205131308.11:highlightBlock
    def highlightBlock (self,s):

        colorer = self.colorer
        s = unicode(s)
        # g.trace(s) # s does not include a newline.
        colorer.recolor(s)
    #@-node:ekr.20081205131308.11:highlightBlock
    #@+node:ekr.20081206062411.15:rehighlight
    def rehighlight (self):

        '''Override base rehighlight method'''

        # g.trace('*****')

        self.colorer.init()

        # Call the base class method.
        QtGui.QSyntaxHighlighter.rehighlight(self)

    #@-node:ekr.20081206062411.15:rehighlight
    #@-others
#@-node:ekr.20081205131308.27:leoQtSyntaxHighlighter
#@+node:ekr.20081205131308.48:class jeditColorizer
class jEditColorizer:

    #@    @+others
    #@+node:ekr.20081205131308.49: Birth
    #@+node:ekr.20081205131308.50:__init__ (threading colorizer)
    def __init__(self,c,highlighter,w):

        # Basic data...
        self.c = c
        self.highlighter = highlighter # a QSyntaxHighlighter
        self.p = None
        self.s = '' # The string being colorized.
        self.w = w
        assert(w == self.c.frame.body.bodyCtrl)

        # Used by recolor and helpers...
        self.actualColorDict = {} # Used only by setTag.
        self.global_i,self.global_j = 0,0 # The global bounds of colorizing.
        self.nextState = 1 # Dont use 0.
        self.stateDict = {} # Keys are state numbers, values are data.

        # Attributes dict ivars: defaults are as shown...
        self.default = 'null'
        self.digit_re = ''
        self.escape = ''
        self.highlight_digits = True
        self.ignore_case = True
        self.no_word_sep = ''
        # Config settings...
        self.comment_string = None # Set by scanColorDirectives on @comment
        self.showInvisibles = False # True: show "invisible" characters.
        self.underline_undefined = c.config.getBool("underline_undefined_section_names")
        self.use_hyperlinks = c.config.getBool("use_hyperlinks")
        self.enabled = c.config.getBool('use_syntax_coloring')
        # Debugging...
        self.count = 0 # For unit testing.
        self.allow_mark_prev = True # The new colorizer tolerates this nonsense :-)
        self.trace = False or c.config.getBool('trace_colorizer')
        self.trace_leo_matches = False
        self.trace_match_flag = False # (Useful) True: trace all matching methods.
        self.verbose = False
        # Mode data...
        self.comment_string = None # Can be set by @comment directive.
        self.defaultRulesList = []
        self.flag = True # True unless in range of @nocolor
        self.importedRulesets = {}
        self.language = 'python' # set by scanColorDirectives.
        self.prev = None # The previous token.
        self.fonts = {} # Keys are config names.  Values are actual fonts.
        self.keywords = {} # Keys are keywords, values are 0..5.
        self.modes = {} # Keys are languages, values are modes.
        self.mode = None # The mode object for the present language.
        self.modeBunch = None # A bunch fully describing a mode.
        self.modeStack = []
        self.rulesDict = {}
        # self.defineAndExtendForthWords()
        self.word_chars = [] # Inited by init_keywords().
        self.setFontFromConfig()
        self.tags = [
            "blank","comment","cwebName","docPart","keyword","leoKeyword",
            "latexModeBackground","latexModeKeyword",
            "latexBackground","latexKeyword",
            "link","name","nameBrackets","pp","string",
            "elide","bold","bolditalic","italic", # new for wiki styling.
            "tab",
            # Leo jEdit tags...
            '@color', '@nocolor', 'doc_part', 'section_ref',
            # jEdit tags.
            'bracketRange',
            'comment1','comment2','comment3','comment4',
            'function',
            'keyword1','keyword2','keyword3','keyword4',
            'label','literal1','literal2','literal3','literal4',
            'markup','operator',
        ]

        #@    << define leoKeywordsDict >>
        #@+node:ekr.20081205131308.35:<< define leoKeywordsDict >>
        self.leoKeywordsDict = {}

        for key in g.globalDirectiveList:
            self.leoKeywordsDict [key] = 'leoKeyword'
        #@nonl
        #@-node:ekr.20081205131308.35:<< define leoKeywordsDict >>
        #@nl
        #@    << define default_colors_dict >>
        #@+node:ekr.20081205131308.36:<< define default_colors_dict >>
        # These defaults are sure to exist.

        self.default_colors_dict = {
            # tag name       :(     option name,           default color),
            'comment'        :('comment_color',               'red'),
            'cwebName'       :('cweb_section_name_color',     'red'),
            'pp'             :('directive_color',             'blue'),
            'docPart'        :('doc_part_color',              'red'),
            'keyword'        :('keyword_color',               'blue'),
            'leoKeyword'     :('leo_keyword_color',           'blue'),
            'link'           :('section_name_color',          'red'),
            'nameBrackets'   :('section_name_brackets_color', 'blue'),
            'string'         :('string_color',                '#00aa00'), # Used by IDLE.
            'name'           :('undefined_section_name_color','red'),
            'latexBackground':('latex_background_color',      'white'),

            # Tags used by forth.
            'keyword5'       :('keyword5_color',              'blue'),
            'bracketRange'   :('bracket_range_color',         'orange'),
            # jEdit tags.

            'comment1'       :('comment1_color', 'red'),
            'comment2'       :('comment2_color', 'red'),
            'comment3'       :('comment3_color', 'red'),
            'comment4'       :('comment4_color', 'red'),
            'function'       :('function_color', 'black'),
            'keyword1'       :('keyword1_color', 'blue'),
            'keyword2'       :('keyword2_color', 'blue'),
            'keyword3'       :('keyword3_color', 'blue'),
            'keyword4'       :('keyword4_color', 'blue'),
            'label'          :('label_color',    'black'),
            'literal1'       :('literal1_color', '#00aa00'),
            'literal2'       :('literal2_color', '#00aa00'),
            'literal3'       :('literal3_color', '#00aa00'),
            'literal4'       :('literal4_color', '#00aa00'),
            'markup'         :('markup_color',   'red'),
            'null'           :('null_color',     'black'),
            'operator'       :('operator_color', 'black'),
            }
        #@-node:ekr.20081205131308.36:<< define default_colors_dict >>
        #@nl
        #@    << define default_font_dict >>
        #@+node:ekr.20081205131308.37:<< define default_font_dict >>
        self.default_font_dict = {
            # tag name      : option name
            'comment'       :'comment_font',
            'cwebName'      :'cweb_section_name_font',
            'pp'            :'directive_font',
            'docPart'       :'doc_part_font',
            'keyword'       :'keyword_font',
            'leoKeyword'    :'leo_keyword_font',
            'link'          :'section_name_font',
            'nameBrackets'  :'section_name_brackets_font',
            'string'        :'string_font',
            'name'          :'undefined_section_name_font',
            'latexBackground':'latex_background_font',

            # Tags used by forth.
            'bracketRange'   :'bracketRange_font',
            'keyword5'       :'keyword5_font',

             # jEdit tags.
            'comment1'      :'comment1_font',
            'comment2'      :'comment2_font',
            'comment3'      :'comment3_font',
            'comment4'      :'comment4_font',
            'function'      :'function_font',
            'keyword1'      :'keyword1_font',
            'keyword2'      :'keyword2_font',
            'keyword3'      :'keyword3_font',
            'keyword4'      :'keyword4_font',
            'keyword5'      :'keyword5_font',
            'label'         :'label_font',
            'literal1'      :'literal1_font',
            'literal2'      :'literal2_font',
            'literal3'      :'literal3_font',
            'literal4'      :'literal4_font',
            'markup'        :'markup_font',
            # 'nocolor' This tag is used, but never generates code.
            'null'          :'null_font',
            'operator'      :'operator_font',
            }
        #@-node:ekr.20081205131308.37:<< define default_font_dict >>
        #@nl

        # New in Leo 4.6: configure tags only once here.
        # Some changes will be needed for multiple body editors.
        self.configure_tags() # Must do this every time to support multiple editors.
    #@-node:ekr.20081205131308.50:__init__ (threading colorizer)
    #@+node:ekr.20081205131308.51:addImportedRules
    def addImportedRules (self,mode,rulesDict,rulesetName):

        '''Append any imported rules at the end of the rulesets specified in mode.importDict'''

        if self.importedRulesets.get(rulesetName):
            return
        else:
            self.importedRulesets [rulesetName] = True

        names = hasattr(mode,'importDict') and mode.importDict.get(rulesetName,[]) or []

        for name in names:
            savedBunch = self.modeBunch
            ok = self.init_mode(name)
            if ok:
                rulesDict2 = self.rulesDict
                for key in rulesDict2.keys():
                    aList = self.rulesDict.get(key,[])
                    aList2 = rulesDict2.get(key)
                    if aList2:
                        # Don't add the standard rules again.
                        rules = [z for z in aList2 if z not in aList]
                        if rules:
                            # g.trace([z.__name__ for z in rules])
                            aList.extend(rules)
                            self.rulesDict [key] = aList
            # g.trace('***** added rules for %s from %s' % (name,rulesetName))
            self.initModeFromBunch(savedBunch)
    #@nonl
    #@-node:ekr.20081205131308.51:addImportedRules
    #@+node:ekr.20081205131308.52:addLeoRules
    def addLeoRules (self,theDict):

        '''Put Leo-specific rules to theList.'''

        table = (
            # Rules added at front are added in **reverse** order.
            ('@',  self.match_leo_keywords,True), # Called after all other Leo matchers.
                # Debatable: Leo keywords override langauge keywords.
            ('@',  self.match_at_color,    True),
            ('@',  self.match_at_nocolor,  True),
            ('@',  self.match_doc_part,    True), 
            ('<',  self.match_section_ref, True), # Called **first**.
            # Rules added at back are added in normal order.
            (' ',  self.match_blanks,      False),
            ('\t', self.match_tabs,        False),
        )

        for ch, rule, atFront, in table:

            # Replace the bound method by an unbound method.
            rule = rule.im_func
            # g.trace(rule)

            theList = theDict.get(ch,[])
            if atFront:
                theList.insert(0,rule)
            else:
                theList.append(rule)
            theDict [ch] = theList

        # g.trace(g.listToString(theDict.get('@')))
    #@-node:ekr.20081205131308.52:addLeoRules
    #@+node:ekr.20081205131308.53:configure_tags
    def configure_tags (self):

        c = self.c ; w = self.w ; trace = False

        if w and hasattr(w,'start_tag_configure'):
            w.start_tag_configure()

        # Get the default body font.
        defaultBodyfont = self.fonts.get('default_body_font')
        if not defaultBodyfont:
            defaultBodyfont = c.config.getFontFromParams(
                "body_text_font_family", "body_text_font_size",
                "body_text_font_slant",  "body_text_font_weight",
                c.config.defaultBodyFontSize)
            self.fonts['default_body_font'] = defaultBodyfont

        # Configure fonts.
        keys = self.default_font_dict.keys() ; keys.sort()
        for key in keys:
            option_name = self.default_font_dict[key]
            # First, look for the language-specific setting, then the general setting.
            for name in ('%s_%s' % (self.language,option_name),(option_name)):
                font = self.fonts.get(name)
                if font:
                    if trace: g.trace('found',name,id(font))
                    w.tag_config(key,font=font)
                    break
                else:
                    family = c.config.get(name + '_family','family')
                    size   = c.config.get(name + '_size',  'size')   
                    slant  = c.config.get(name + '_slant', 'slant')
                    weight = c.config.get(name + '_weight','weight')
                    if family or slant or weight or size:
                        family = family or g.app.config.defaultFontFamily
                        size   = size or c.config.defaultBodyFontSize
                        slant  = slant or 'roman'
                        weight = weight or 'normal'
                        font = g.app.gui.getFontFromParams(family,size,slant,weight)
                        # Save a reference to the font so it 'sticks'.
                        self.fonts[name] = font 
                        if trace: g.trace(key,name,family,size,slant,weight,id(font))
                        w.tag_config(key,font=font)
                        break
            else: # Neither the general setting nor the language-specific setting exists.
                if self.fonts.keys(): # Restore the default font.
                    if trace: g.trace('default',key)
                    w.tag_config(key,font=defaultBodyfont)

        keys = self.default_colors_dict.keys() ; keys.sort()
        for name in keys:
            option_name,default_color = self.default_colors_dict[name]
            color = (
                c.config.getColor('%s_%s' % (self.language,option_name)) or
                c.config.getColor(option_name) or
                default_color
            )
            if trace: g.trace(option_name,color)

            # Must use foreground, not fg.
            try:
                w.tag_configure(name, foreground=color)
            except: # Recover after a user error.
                g.es_exception()
                w.tag_configure(name, foreground=default_color)

        # underline=var doesn't seem to work.
        if 0: # self.use_hyperlinks: # Use the same coloring, even when hyperlinks are in effect.
            w.tag_configure("link",underline=1) # defined
            w.tag_configure("name",underline=0) # undefined
        else:
            w.tag_configure("link",underline=0)
            if self.underline_undefined:
                w.tag_configure("name",underline=1)
            else:
                w.tag_configure("name",underline=0)

        self.configure_variable_tags()

        # Colors for latex characters.  Should be user options...

        if 1: # Alas, the selection doesn't show if a background color is specified.
            w.tag_configure("latexModeBackground",foreground="black")
            w.tag_configure("latexModeKeyword",foreground="blue")
            w.tag_configure("latexBackground",foreground="black")
            w.tag_configure("latexKeyword",foreground="blue")
        else: # Looks cool, and good for debugging.
            w.tag_configure("latexModeBackground",foreground="black",background="seashell1")
            w.tag_configure("latexModeKeyword",foreground="blue",background="seashell1")
            w.tag_configure("latexBackground",foreground="black",background="white")
            w.tag_configure("latexKeyword",foreground="blue",background="white")

        # Tags for wiki coloring.
        w.tag_configure("bold",font=self.bold_font)
        w.tag_configure("italic",font=self.italic_font)
        w.tag_configure("bolditalic",font=self.bolditalic_font)
        for name in self.color_tags_list:
            w.tag_configure(name,foreground=name)

        try:
            w.end_tag_configure()
        except AttributeError:
            pass
    #@-node:ekr.20081205131308.53:configure_tags
    #@+node:ekr.20081205131308.54:configure_variable_tags
    def configure_variable_tags (self):

        c = self.c ; w = self.w

        # g.trace()

        for name,option_name,default_color in (
            ("blank","show_invisibles_space_background_color","Gray90"),
            ("tab",  "show_invisibles_tab_background_color",  "Gray80"),
            ("elide", None,                                   "yellow"),
        ):
            if self.showInvisibles:
                color = option_name and c.config.getColor(option_name) or default_color
            else:
                option_name,default_color = self.default_colors_dict.get(name,(None,None),)
                color = option_name and c.config.getColor(option_name) or ''
            try:
                w.tag_configure(name,background=color)
            except: # A user error.
                w.tag_configure(name,background=default_color)

        # Special case:
        if not self.showInvisibles:
            w.tag_configure("elide",elide="1")
    #@-node:ekr.20081205131308.54:configure_variable_tags
    #@+node:ekr.20081205131308.55:init_mode & helpers
    def init_mode (self,name):

        '''Name may be a language name or a delegate name.'''

        if not name: return False
        language,rulesetName = self.nameToRulesetName(name)
        bunch = self.modes.get(rulesetName)
        if bunch:
            # g.trace('found',language,rulesetName)
            self.initModeFromBunch(bunch)
            return True
        else:
            # g.trace('****',language,rulesetName)
            path = g.os_path_join(g.app.loadDir,'..','modes')
            # Bug fix: 2008/2/10: Don't try to import a non-existent language.
            fileName = g.os_path_join(path,'%s.py' % (language))
            if g.os_path_exists(fileName):
                mode = g.importFromPath (language,path)
            else: mode = None

            if mode:
                # A hack to give modes/forth.py access to c.
                if hasattr(mode,'pre_init_mode'):
                    mode.pre_init_mode(self.c)
            else:
                # Create a dummy bunch to limit recursion.
                self.modes [rulesetName] = self.modeBunch = g.Bunch(
                    attributesDict  = {},
                    defaultColor    = None,
                    keywordsDict    = {},
                    language        = language,
                    mode            = mode,
                    properties      = {},
                    rulesDict       = {},
                    rulesetName     = rulesetName)
                # g.trace('No colorizer file: %s.py' % language)
                return False
            self.language = language
            self.rulesetName = rulesetName
            self.properties = hasattr(mode,'properties') and mode.properties or {}
            self.keywordsDict = hasattr(mode,'keywordsDictDict') and mode.keywordsDictDict.get(rulesetName,{}) or {}
            self.setKeywords()
            self.attributesDict = hasattr(mode,'attributesDictDict') and mode.attributesDictDict.get(rulesetName) or {}
            self.setModeAttributes()
            self.rulesDict = hasattr(mode,'rulesDictDict') and mode.rulesDictDict.get(rulesetName) or {}
            self.addLeoRules(self.rulesDict)

            self.defaultColor = 'null'
            self.mode = mode
            self.modes [rulesetName] = self.modeBunch = g.Bunch(
                attributesDict  = self.attributesDict,
                defaultColor    = self.defaultColor,
                keywordsDict    = self.keywordsDict,
                language        = self.language,
                mode            = self.mode,
                properties      = self.properties,
                rulesDict       = self.rulesDict,
                rulesetName     = self.rulesetName)
            # Do this after 'officially' initing the mode, to limit recursion.
            self.addImportedRules(mode,self.rulesDict,rulesetName)
            self.updateDelimsTables()

            initialDelegate = self.properties.get('initialModeDelegate')
            if initialDelegate:
                # g.trace('initialDelegate',initialDelegate)
                # Replace the original mode by the delegate mode.
                self.init_mode(initialDelegate)
                language2,rulesetName2 = self.nameToRulesetName(initialDelegate)
                self.modes[rulesetName] = self.modes.get(rulesetName2)
            return True
    #@+node:ekr.20081205131308.56:nameToRulesetName
    def nameToRulesetName (self,name):

        '''Compute language and rulesetName from name, which is either a language or a delegate name.'''

        if not name: return ''

        i = name.find('::')
        if i == -1:
            language = name
            rulesetName = '%s_main' % (language)
        else:
            language = name[:i]
            delegate = name[i+2:]
            rulesetName = self.munge('%s_%s' % (language,delegate))

        # g.trace(name,language,rulesetName)
        return language,rulesetName
    #@nonl
    #@-node:ekr.20081205131308.56:nameToRulesetName
    #@+node:ekr.20081205131308.57:setKeywords
    def setKeywords (self):

        '''Initialize the keywords for the present language.

         Set self.word_chars ivar to string.letters + string.digits
         plus any other character appearing in any keyword.'''

        # Add any new user keywords to leoKeywordsDict.
        d = self.keywordsDict
        keys = d.keys()
        for s in g.globalDirectiveList:
            key = '@' + s
            if key not in keys:
                d [key] = 'leoKeyword'

        # Create the word_chars list. 
        self.word_chars = [g.toUnicode(ch,encoding='UTF-8') for ch in (string.letters + string.digits)]

        for key in d.keys():
            for ch in key:
                # if ch == ' ': g.trace('blank in key: %s' % repr (key))
                if ch not in self.word_chars:
                    self.word_chars.append(g.toUnicode(ch,encoding='UTF-8'))

        # jEdit2Py now does this check, so this isn't really needed.
        # But it is needed for forth.py.
        for ch in (' ', '\t'):
            if ch in self.word_chars:
                # g.es_print('removing %s from word_chars' % (repr(ch)))
                self.word_chars.remove(ch)

        # g.trace(self.language,[str(z) for z in self.word_chars])
    #@nonl
    #@-node:ekr.20081205131308.57:setKeywords
    #@+node:ekr.20081205131308.58:setModeAttributes
    def setModeAttributes (self):

        '''Set the ivars from self.attributesDict,
        converting 'true'/'false' to True and False.'''

        d = self.attributesDict
        aList = (
            ('default',         'null'),
    	    ('digit_re',        ''),
            ('escape',          ''), # New in Leo 4.4.2.
    	    ('highlight_digits',True),
    	    ('ignore_case',     True),
    	    ('no_word_sep',     ''),
        )

        for key, default in aList:
            val = d.get(key,default)
            if val in ('true','True'): val = True
            if val in ('false','False'): val = False
            setattr(self,key,val)
            # g.trace(key,val)
    #@nonl
    #@-node:ekr.20081205131308.58:setModeAttributes
    #@+node:ekr.20081205131308.59:initModeFromBunch
    def initModeFromBunch (self,bunch):

        self.modeBunch = bunch
        self.attributesDict = bunch.attributesDict
        self.setModeAttributes()
        self.defaultColor   = bunch.defaultColor
        self.keywordsDict   = bunch.keywordsDict
        self.language       = bunch.language
        self.mode           = bunch.mode
        self.properties     = bunch.properties
        self.rulesDict      = bunch.rulesDict
        self.rulesetName    = bunch.rulesetName

        # g.trace(self.rulesetName)
    #@nonl
    #@-node:ekr.20081205131308.59:initModeFromBunch
    #@+node:ekr.20081205131308.60:updateDelimsTables
    def updateDelimsTables (self):

        '''Update g.app.language_delims_dict if no entry for the language exists.'''

        d = self.properties
        lineComment = d.get('lineComment')
        startComment = d.get('commentStart')
        endComment = d.get('commentEnd')

        if lineComment and startComment and endComment:
            delims = '%s %s %s' % (lineComment,startComment,endComment)
        elif startComment and endComment:
            delims = '%s %s' % (startComment,endComment)
        elif lineComment:
            delims = '%s' % lineComment
        else:
            delims = None

        if delims:
            d = g.app.language_delims_dict
            if not d.get(self.language):
                d [self.language] = delims
                # g.trace(self.language,'delims:',repr(delims))
    #@-node:ekr.20081205131308.60:updateDelimsTables
    #@-node:ekr.20081205131308.55:init_mode & helpers
    #@+node:ekr.20081205131308.106:munge
    def munge(self,s):

        '''Munge a mode name so that it is a valid python id.'''

        valid = string.ascii_letters + string.digits + '_'

        return ''.join([g.choose(ch in valid,ch.lower(),'_') for ch in s])
    #@nonl
    #@-node:ekr.20081205131308.106:munge
    #@+node:ekr.20081205131308.111:setFontFromConfig
    def setFontFromConfig (self):

        c = self.c
        # isQt = g.app.gui.guiName() == 'qt'

        self.bold_font = c.config.getFontFromParams(
            "body_text_font_family", "body_text_font_size",
            "body_text_font_slant",  "body_text_font_weight",
            c.config.defaultBodyFontSize) # , tag = "colorer bold")

        # if self.bold_font and not isQt:
            # self.bold_font.configure(weight="bold")

        self.italic_font = c.config.getFontFromParams(
            "body_text_font_family", "body_text_font_size",
            "body_text_font_slant",  "body_text_font_weight",
            c.config.defaultBodyFontSize) # , tag = "colorer italic")

        # if self.italic_font and not isQt:
            # self.italic_font.configure(slant="italic",weight="normal")

        self.bolditalic_font = c.config.getFontFromParams(
            "body_text_font_family", "body_text_font_size",
            "body_text_font_slant",  "body_text_font_weight",
            c.config.defaultBodyFontSize) # , tag = "colorer bold italic")

        # if self.bolditalic_font and not isQt:
            # self.bolditalic_font.configure(weight="bold",slant="italic")

        self.color_tags_list = []
        # self.image_references = []
    #@nonl
    #@-node:ekr.20081205131308.111:setFontFromConfig
    #@-node:ekr.20081205131308.49: Birth
    #@+node:ekr.20081206062411.13:colorRangeWithTag
    def colorRangeWithTag (self,s,i,j,tag,delegate='',exclude_match=False):

        '''Actually colorize the selected range.'''

        trace = False
        if not self.flag: return

        if delegate:
            if trace: g.trace('delegate',delegate,i,j,tag,g.callers(3))
            self.modeStack.append(self.modeBunch)
            self.init_mode(delegate)
            # Color everything now, using the same indices as the caller.
            while i < j:
                progress = i
                assert j >= 0, 'colorRangeWithTag: negative j'
                for f in self.rulesDict.get(s[i],[]):
                    n = f(self,s,i)
                    if n is None:
                        g.trace('Can not happen: delegate matcher returns None')
                    elif n > 0:
                        if trace: g.trace('delegate',delegate,i,n,f.__name__,repr(s[i:i+n]))
                        i += n ; break
                else:
                    # New in Leo 4.6: Use the default chars for everything else.
                    self.setTag(tag,i,i+1)
                    i += 1
                assert i > progress
            bunch = self.modeStack.pop()
            self.initModeFromBunch(bunch)
        elif not exclude_match:
            self.setTag(tag,i,j)
    #@nonl
    #@-node:ekr.20081206062411.13:colorRangeWithTag
    #@+node:ekr.20081205131308.74:init
    def init (self):

        self.p = self.c.currentPosition()
        self.s = self.w.getAllText()
        # g.trace(self.s)

        # State info.
        self.global_i,self.global_j = 0,0
        self.nextState = 1 # Dont use 0.
        self.stateDict = {}

        self.updateSyntaxColorer(self.p)
            # Sets self.flag and self.language.

        self.init_mode(self.language)

        # Used by matchers.
        self.prev = None

        # self.configure_tags() # Must do this every time to support multiple editors.
    #@-node:ekr.20081205131308.74:init
    #@+node:ekr.20081205131308.87:jEdit matchers
    #@+at
    # 
    # The following jEdit matcher methods return the length of the matched 
    # text if the
    # match succeeds, and zero otherwise.  In most cases, these methods 
    # colorize all the matched text.
    # 
    # The following arguments affect matching:
    # 
    # - at_line_start         True: sequence must start the line.
    # - at_whitespace_end     True: sequence must be first non-whitespace text 
    # of the line.
    # - at_word_start         True: sequence must start a word.
    # - hash_char             The first character that must match in a regular 
    # expression.
    # - no_escape:            True: ignore an 'end' string if it is preceded 
    # by the ruleset's escape character.
    # - no_line_break         True: the match will not succeed across line 
    # breaks.
    # - no_word_break:        True: the match will not cross word breaks.
    # 
    # The following arguments affect coloring when a match succeeds:
    # 
    # - delegate              A ruleset name. The matched text will be colored 
    # recursively by the indicated ruleset.
    # - exclude_match         If True, the actual text that matched will not 
    # be colored.
    # - kind                  The color tag to be applied to colored text.
    #@-at
    #@@c
    #@@color
    #@+node:ekr.20081205131308.105:dump
    def dump (self,s):

        if s.find('\n') == -1:
            return s
        else:
            return '\n' + s + '\n'
    #@nonl
    #@-node:ekr.20081205131308.105:dump
    #@+node:ekr.20081205131308.38:Leo rule functions
    #@+node:ekr.20081205131308.39:match_at_color
    def match_at_color (self,s,i):

        if self.trace_leo_matches: g.trace()

        seq = '@color'

        # Only matches at start of line.
        if i != 0 and s[i-1] != '\n': return 0

        if g.match_word(s,i,seq):
            self.flag = True # Enable coloring.
            j = i + len(seq)
            self.colorRangeWithTag(s,i,j,'leoKeyword')
            return j - i
        else:
            return 0
    #@nonl
    #@-node:ekr.20081205131308.39:match_at_color
    #@+node:ekr.20081205131308.40:match_at_nocolor
    def match_at_nocolor (self,s,i):

        if self.trace_leo_matches: g.trace()

        # Only matches at start of line.
        if i != 0 and s[i-1] != '\n':
            return 0
        if not g.match_word(s,i,'@nocolor'):
            return 0

        j = i + len('@nocolor')
        k = s.find('\n@color',j)
        if k == -1:
            # No later @color: don't color the @nocolor directive.
            self.flag = False # Disable coloring.
            return len(s) - j
        else:
            # A later @color: do color the @nocolor directive.
            self.colorRangeWithTag(s,i,j,'leoKeyword')
            self.flag = False # Disable coloring.
            return k+1-j

    #@-node:ekr.20081205131308.40:match_at_nocolor
    #@+node:ekr.20081205131308.45:match_blanks
    def match_blanks (self,s,i):

        # g.trace(self,s,i)

        j = i ; n = len(s)

        while j < n and s[j] == ' ':
            j += 1

        if j > i:
            # g.trace(i,j)
            if self.showInvisibles:
                self.colorRangeWithTag(s,i,j,'blank')
            return j - i
        else:
            return 0
    #@-node:ekr.20081205131308.45:match_blanks
    #@+node:ekr.20081205131308.41:match_doc_part
    def match_doc_part (self,s,i):

        # New in Leo 4.5: only matches at start of line.
        if i != 0 and s[i-1] != '\n':
            return 0

        if g.match_word(s,i,'@doc'):
            j = i+4
            self.colorRangeWithTag(s,i,j,'leoKeyword')
        elif g.match(s,i,'@') and (i+1 >= len(s) or s[i+1] in (' ','\t','\n')):
            j = i + 1
            self.colorRangeWithTag(s,i,j,'leoKeyword')
        else: return 0

        i = j ; n = len(s)
        while j < n:
            k = s.find('@c',j)
            if k == -1:
                # g.trace('i,len(s)',i,len(s))
                j = n+1 # Bug fix: 2007/12/14
                self.colorRangeWithTag(s,i,j,'docPart')
                return j - i
            if s[k-1] == '\n' and (g.match_word(s,k,'@c') or g.match_word(s,k,'@code')):
                j = k
                self.colorRangeWithTag(s,i,j,'docPart')
                return j - i
            else:
                j = k + 2
        j = n - 1
        return max(0,j - i) # Bug fix: 2008/2/10
    #@-node:ekr.20081205131308.41:match_doc_part
    #@+node:ekr.20081205131308.42:match_leo_keywords
    def match_leo_keywords(self,s,i):

        '''Succeed if s[i:] is a Leo keyword.'''

        # g.trace(i,g.get_line(s,i))

        # We must be at the start of a word.
        if i > 0 and s[i-1] in self.word_chars:
            return 0

        if s[i] != '@':
            return 0

        # Get the word as quickly as possible.
        j = i+1
        while j < len(s) and s[j] in self.word_chars:
            j += 1
        word = s[i+1:j] # Bug fix: 10/17/07: entries in leoKeywordsDict do not start with '@'

        if self.leoKeywordsDict.get(word):
            kind = 'leoKeyword'
            self.colorRangeWithTag(s,i,j,kind)
            self.prev = (i,j,kind)
            result = j-i
            self.trace_match(kind,s,i,j)
            return result
        else:
            return 0
    #@-node:ekr.20081205131308.42:match_leo_keywords
    #@+node:ekr.20081205131308.43:match_section_ref
    def match_section_ref (self,s,i):

        if self.trace_leo_matches: g.trace()
        c = self.c ; w = self.w

        if not g.match(s,i,'<<'):
            return 0
        k = g.find_on_line(s,i+2,'>>')
        if k is not None:
            j = k + 2
            self.colorRangeWithTag(s,i,i+2,'nameBrackets')
            ref = g.findReference(c,s[i:j],self.p)
            if ref:
                if self.use_hyperlinks:
                    #@                << set the hyperlink >>
                    #@+node:ekr.20081205131308.44:<< set the hyperlink >>
                    # Set the bindings to vnode callbacks.
                    # Create the tag.
                    # Create the tag name.
                    tagName = "hyper" + str(self.hyperCount)
                    self.hyperCount += 1
                    w.tag_delete(tagName)
                    self.tag(tagName,i+2,j)

                    ref.tagName = tagName
                    c.tag_bind(w,tagName,"<Control-1>",ref.OnHyperLinkControlClick)
                    c.tag_bind(w,tagName,"<Any-Enter>",ref.OnHyperLinkEnter)
                    c.tag_bind(w,tagName,"<Any-Leave>",ref.OnHyperLinkLeave)
                    #@nonl
                    #@-node:ekr.20081205131308.44:<< set the hyperlink >>
                    #@nl
                else:
                    self.colorRangeWithTag(s,i+2,k,'link')
            else:
                self.colorRangeWithTag(s,i+2,k,'name')
            self.colorRangeWithTag(s,k,j,'nameBrackets')
            return j - i
        else:
            return 0
    #@nonl
    #@-node:ekr.20081205131308.43:match_section_ref
    #@+node:ekr.20081205131308.46:match_tabs
    def match_tabs (self,s,i):

        if self.trace_leo_matches: g.trace()

        j = i ; n = len(s)

        while j < n and s[j] == '\t':
            j += 1

        if j > i:
            # g.trace(i,j)
            self.colorRangeWithTag(s,i,j,'tab')
            return j - i
        else:
            return 0
    #@nonl
    #@-node:ekr.20081205131308.46:match_tabs
    #@-node:ekr.20081205131308.38:Leo rule functions
    #@+node:ekr.20081205131308.88:match_eol_span
    def match_eol_span (self,s,i,
        kind=None,seq='',
        at_line_start=False,at_whitespace_end=False,at_word_start=False,
        delegate='',exclude_match=False):

        '''Succeed if seq matches s[i:]'''

        if self.verbose: g.trace(g.callers(1),i,repr(s[i:i+20]))

        if at_line_start and i != 0 and s[i-1] != '\n': return 0
        if at_whitespace_end and i != g.skip_ws(s,0): return 0
        if at_word_start and i > 0 and s[i-1] in self.word_chars: return 0 # 7/5/2008
        if at_word_start and i + len(seq) + 1 < len(s) and s[i+len(seq)] in self.word_chars:
            return 0 # 7/5/2008

        if g.match(s,i,seq):
            #j = g.skip_line(s,i) # Include the newline so we don't get a flash at the end of the line.
            j = self.skip_line(s,i)
            self.colorRangeWithTag(s,i,j,kind,delegate=delegate,exclude_match=exclude_match)
            self.prev = (i,j,kind)
            self.trace_match(kind,s,i,j)
            return j - i
        else:
            return 0
    #@-node:ekr.20081205131308.88:match_eol_span
    #@+node:ekr.20081205131308.89:match_eol_span_regexp
    def match_eol_span_regexp (self,s,i,
        kind='',regexp='',
        at_line_start=False,at_whitespace_end=False,at_word_start=False,
        delegate='',exclude_match=False):

        '''Succeed if the regular expression regex matches s[i:].'''

        if self.verbose: g.trace(g.callers(1),i,repr(s[i:i+20]))

        if at_line_start and i != 0 and s[i-1] != '\n': return 0
        if at_whitespace_end and i != g.skip_ws(s,0): return 0
        if at_word_start and i > 0 and s[i-1] in self.word_chars: return 0 # 7/5/2008

        n = self.match_regexp_helper(s,i,regexp)
        if n > 0:
            # j = g.skip_line(s,i) # Include the newline so we don't get a flash at the end of the line.
            j = self.skip_line(s,i)
            self.colorRangeWithTag(s,i,j,kind,delegate=delegate,exclude_match=exclude_match)
            self.prev = (i,j,kind)
            self.trace_match(kind,s,i,j)
            return j - i
        else:
            return 0
    #@nonl
    #@-node:ekr.20081205131308.89:match_eol_span_regexp
    #@+node:ekr.20081205131308.90:match_everything
    # def match_everything (self,s,i,kind,delegate):

        # '''A hack for phpsection mode: match the entire text and color with delegate.'''

        # j = len(s)

        # self.colorRangeWithTag(s,i,j,kind,delegate=delegate)

        # return j-i
    #@-node:ekr.20081205131308.90:match_everything
    #@+node:ekr.20081205131308.91:match_keywords
    # This is a time-critical method.
    def match_keywords (self,s,i):

        '''Succeed if s[i:] is a keyword.'''

        # We must be at the start of a word.
        if i > 0 and s[i-1] in self.word_chars:
            return 0

        # Get the word as quickly as possible.
        j = i ; n = len(s) ; chars = self.word_chars
        while j < n and s[j] in chars:
            j += 1

        word = s[i:j]
        if self.ignore_case: word = word.lower()
        kind = self.keywordsDict.get(word)
        if kind:
            self.colorRangeWithTag(s,i,j,kind)
            self.prev = (i,j,kind)
            result = j - i
            # g.trace('success',word,kind,j-i)
            # g.trace('word in self.keywordsDict.keys()',word in self.keywordsDict.keys())
            self.trace_match(kind,s,i,j)
            return result
        else:
            # g.trace('fail',word,kind)
            # g.trace('word in self.keywordsDict.keys()',word in self.keywordsDict.keys())
            return 0
    #@-node:ekr.20081205131308.91:match_keywords
    #@+node:ekr.20081205131308.92:match_mark_following & getNextToken
    def match_mark_following (self,s,i,
        kind='',pattern='',
        at_line_start=False,at_whitespace_end=False,at_word_start=False,
        exclude_match=False):

        '''Succeed if s[i:] matches pattern.'''

        if not self.allow_mark_prev: return 0

        if self.verbose: g.trace(g.callers(1),i,repr(s[i:i+20]))

        if at_line_start and i != 0 and s[i-1] != '\n': return 0
        if at_whitespace_end and i != g.skip_ws(s,0): return 0
        if at_word_start and i > 0 and s[i-1] in self.word_chars: return 0 # 7/5/2008
        if at_word_start and i + len(pattern) + 1 < len(s) and s[i+len(pattern)] in self.word_chars:
            return 0 # 7/5/2008

        if g.match(s,i,pattern):
            j = i + len(pattern)
            self.colorRangeWithTag(s,i,j,kind,exclude_match=exclude_match)
            k = self.getNextToken(s,j)
            if k > j:
                self.colorRangeWithTag(s,j,k,kind,exclude_match=False)
                j = k
            self.prev = (i,j,kind)
            self.trace_match(kind,s,i,j)
            return j - i
        else:
            return 0
    #@+node:ekr.20081205131308.93:getNextToken
    def getNextToken (self,s,i):

        '''Return the index of the end of the next token for match_mark_following.

        The jEdit docs are not clear about what a 'token' is, but experiments with jEdit
        show that token means a word, as defined by word_chars.'''

        while i < len(s) and s[i] in self.word_chars:
            i += 1

        return min(len(s),i+1)
    #@nonl
    #@-node:ekr.20081205131308.93:getNextToken
    #@-node:ekr.20081205131308.92:match_mark_following & getNextToken
    #@+node:ekr.20081205131308.94:match_mark_previous
    def match_mark_previous (self,s,i,
        kind='',pattern='',
        at_line_start=False,at_whitespace_end=False,at_word_start=False,
        exclude_match=False):

        '''Return the length of a matched SEQ or 0 if no match.

        'at_line_start':    True: sequence must start the line.
        'at_whitespace_end':True: sequence must be first non-whitespace text of the line.
        'at_word_start':    True: sequence must start a word.'''

        if not self.allow_mark_prev: return 0

        if self.verbose: g.trace(g.callers(1),i,repr(s[i:i+20]))

        if at_line_start and i != 0 and s[i-1] != '\n': return 0
        if at_whitespace_end and i != g.skip_ws(s,0): return 0
        if at_word_start and i > 0 and s[i-1] in self.word_chars: return 0 # 7/5/2008
        if at_word_start and i + len(pattern) + 1 < len(s) and s[i+len(pattern)] in self.word_chars:
            return 0 # 7/5/2008

        if g.match(s,i,pattern):
            j = i + len(pattern)
            # Color the previous token.
            if self.prev:
                i2,j2,kind2 = self.prev
                # g.trace(i2,j2,kind2)
                self.colorRangeWithTag(s,i2,j2,kind2,exclude_match=False)
            if not exclude_match:
                self.colorRangeWithTag(s,i,j,kind)
            self.prev = (i,j,kind)
            self.trace_match(kind,s,i,j)
            return j - i
        else:
            return 0
    #@-node:ekr.20081205131308.94:match_mark_previous
    #@+node:ekr.20081205131308.95:match_regexp_helper
    def match_regexp_helper (self,s,i,pattern):

        '''Return the length of the matching text if seq (a regular expression) matches the present position.'''

        if self.verbose: g.trace(g.callers(1),i,repr(s[i:i+20]),'pattern',pattern)
        trace = False

        try:
            flags = re.MULTILINE
            if self.ignore_case: flags|= re.IGNORECASE
            re_obj = re.compile(pattern,flags)
        except Exception:
            # Bug fix: 2007/11/07: do not call g.es here!
            g.trace('Invalid regular expression: %s' % (pattern))
            return 0

        # Match succeeds or fails more quickly than search.
        # g.trace('before')
        self.match_obj = mo = re_obj.match(s,i) # re_obj.search(s,i) 
        # g.trace('after')

        if mo is None:
            return 0
        else:
            start, end = mo.start(), mo.end()
            if start != i: # Bug fix 2007-12-18: no match at i
                return 0
            if trace:
                g.trace('pattern',pattern)
                g.trace('match: %d, %d, %s' % (start,end,repr(s[start: end])))
                g.trace('groups',mo.groups())
            return end - start
    #@-node:ekr.20081205131308.95:match_regexp_helper
    #@+node:ekr.20081205131308.96:match_seq
    def match_seq (self,s,i,
        kind='',seq='',
        at_line_start=False,at_whitespace_end=False,at_word_start=False,
        delegate=''):

        '''Succeed if s[:] mathces seq.'''

        if at_line_start and i != 0 and s[i-1] != '\n':
            j = i
        elif at_whitespace_end and i != g.skip_ws(s,0):
            j = i
        elif at_word_start and i > 0 and s[i-1] in self.word_chars:  # 7/5/2008
            j = i
        if at_word_start and i + len(seq) + 1 < len(s) and s[i+len(seq)] in self.word_chars:
            j = i # 7/5/2008
        elif g.match(s,i,seq):
            j = i + len(seq)
            self.colorRangeWithTag(s,i,j,kind,delegate=delegate)
            self.prev = (i,j,kind)
            self.trace_match(kind,s,i,j)
        else:
            j = i
        return j - i
    #@nonl
    #@-node:ekr.20081205131308.96:match_seq
    #@+node:ekr.20081205131308.97:match_seq_regexp
    def match_seq_regexp (self,s,i,
        kind='',regexp='',
        at_line_start=False,at_whitespace_end=False,at_word_start=False,
        delegate=''):

        '''Succeed if the regular expression regexp matches at s[i:].'''

        if self.verbose: g.trace(g.callers(1),i,repr(s[i:i+20]),'regexp',regexp)

        if at_line_start and i != 0 and s[i-1] != '\n': return 0
        if at_whitespace_end and i != g.skip_ws(s,0): return 0
        if at_word_start and i > 0 and s[i-1] in self.word_chars: return 0 # 7/5/2008

        # g.trace('before')
        n = self.match_regexp_helper(s,i,regexp)
        # g.trace('after')
        j = i + n # Bug fix: 2007-12-18
        assert (j-i == n)
        self.colorRangeWithTag(s,i,j,kind,delegate=delegate)
        self.prev = (i,j,kind)
        self.trace_match(kind,s,i,j)
        return j - i
    #@nonl
    #@-node:ekr.20081205131308.97:match_seq_regexp
    #@+node:ekr.20081205131308.98:match_span & helper
    def match_span (self,s,i,
        kind='',begin='',end='',
        at_line_start=False,at_whitespace_end=False,at_word_start=False,
        delegate='',exclude_match=False,
        no_escape=False,no_line_break=False,no_word_break=False):

        '''Succeed if s[i:] starts with 'begin' and contains a following 'end'.'''

        if at_line_start and i != 0 and s[i-1] != '\n':
            j = i
        elif at_whitespace_end and i != g.skip_ws(s,0):
            j = i
        elif at_word_start and i > 0 and s[i-1] in self.word_chars: # 7/5/2008
            j = i
        elif at_word_start and i + len(begin) + 1 < len(s) and s[i+len(begin)] in self.word_chars:
            j = i # 7/5/2008
        elif not g.match(s,i,begin):
            j = i
        else:
            j = self.match_span_helper(s,i+len(begin),end,no_escape,no_line_break,no_word_break=no_word_break)
            if j == -1:
                j = i
            else:
                i2 = i + len(begin) ; j2 = j + len(end)
                # g.trace(i,j,s[i:j2],kind)
                if delegate:
                    self.colorRangeWithTag(s,i,i2,kind,delegate=None,    exclude_match=exclude_match)
                    self.colorRangeWithTag(s,i2,j,kind,delegate=delegate,exclude_match=exclude_match)
                    self.colorRangeWithTag(s,j,j2,kind,delegate=None,    exclude_match=exclude_match)
                else: # avoid having to merge ranges in addTagsToList.
                    self.colorRangeWithTag(s,i,j2,kind,delegate=None,exclude_match=exclude_match)
                j = j2
                self.prev = (i,j,kind)

        self.trace_match(kind,s,i,j)
        return j - i
    #@+node:ekr.20081205131308.99:match_span_helper
    def match_span_helper (self,s,i,pattern,no_escape,no_line_break,no_word_break=False):

        '''Return n >= 0 if s[i] ends with a non-escaped 'end' string.'''

        esc = self.escape

        while 1:
            j = s.find(pattern,i)
            if j == -1:
                # Match to end of text if not found and no_line_break is False
                if no_line_break:
                    return -1
                else:
                    return len(s)
            elif no_word_break and j > 0 and s[j-1] in self.word_chars:
                return -1 # New in Leo 4.5.
            elif no_line_break and '\n' in s[i:j]:
                return -1
            elif esc and not no_escape:
                # Only an odd number of escapes is a 'real' escape.
                escapes = 0 ; k = 1
                while j-k >=0 and s[j-k] == esc:
                    escapes += 1 ; k += 1
                if (escapes % 2) == 1:
                    # Continue searching past the escaped pattern string.
                    i = j + len(pattern) # Bug fix: 7/25/07.
                    # g.trace('escapes',escapes,repr(s[i:]))
                else:
                    return j
            else:
                return j
    #@nonl
    #@-node:ekr.20081205131308.99:match_span_helper
    #@-node:ekr.20081205131308.98:match_span & helper
    #@+node:ekr.20081205131308.100:match_span_regexp
    def match_span_regexp (self,s,i,
        kind='',begin='',end='',
        at_line_start=False,at_whitespace_end=False,at_word_start=False,
        delegate='',exclude_match=False,
        no_escape=False,no_line_break=False, no_word_break=False,
    ):

        '''Succeed if s[i:] starts with 'begin' (a regular expression) and contains a following 'end'.'''

        if self.verbose: g.trace('begin',repr(begin),'end',repr(end),self.dump(s[i:]))

        if at_line_start and i != 0 and s[i-1] != '\n': return 0
        if at_whitespace_end and i != g.skip_ws(s,0): return 0
        if at_word_start and i > 0 and s[i-1] in self.word_chars: return 0 # 7/5/2008
        if at_word_start and i + len(begin) + 1 < len(s) and s[i+len(begin)] in self.word_chars:
            return 0 # 7/5/2008

        n = self.match_regexp_helper(s,i,begin)
        # We may have to allow $n here, in which case we must use a regex object?
        if n > 0:
            j = i + n
            j2 = s.find(end,j)
            if j2 == -1: return 0
            if self.escape and not no_escape:
                # Only an odd number of escapes is a 'real' escape.
                escapes = 0 ; k = 1
                while j-k >=0 and s[j-k] == self.escape:
                    escapes += 1 ; k += 1
                if (escapes % 2) == 1:
                    # An escaped end **aborts the entire match**:
                    # there is no way to 'restart' the regex.
                    return 0
            i2 = j2 - len(end)
            if delegate:
                self.colorRangeWithTag(s,i,j,kind, delegate=None,     exclude_match=exclude_match)
                self.colorRangeWithTag(s,j,i2,kind, delegate=delegate,exclude_match=False)
                self.colorRangeWithTag(s,i2,j2,kind,delegate=None,    exclude_match=exclude_match)
            else: # avoid having to merge ranges in addTagsToList.
                self.colorRangeWithTag(s,i,j2,kind,delegate=None,exclude_match=exclude_match)
            self.prev = (i,j,kind)
            self.trace_match(kind,s,i,j2)
            return j2 - i
        else: return 0
    #@-node:ekr.20081205131308.100:match_span_regexp
    #@+node:ekr.20081205131308.101:match_word_and_regexp
    def match_word_and_regexp (self,s,i,
        kind1='',word='',
        kind2='',pattern='',
        at_line_start=False,at_whitespace_end=False,at_word_start=False,
        exclude_match=False):

        '''Succeed if s[i:] matches pattern.'''

        if not self.allow_mark_prev: return 0

        if (False or self.verbose): g.trace(i,repr(s[i:i+20]))

        if at_line_start and i != 0 and s[i-1] != '\n': return 0
        if at_whitespace_end and i != g.skip_ws(s,0): return 0
        if at_word_start and i > 0 and s[i-1] in self.word_chars: return 0 # 7/5/2008
        if at_word_start and i + len(word) + 1 < len(s) and s[i+len(word)] in self.word_chars:
            j = i # 7/5/2008

        if not g.match(s,i,word):
            return 0

        j = i + len(word)
        n = self.match_regexp_helper(s,j,pattern)
        # g.trace(j,pattern,n)
        if n == 0:
            return 0
        self.colorRangeWithTag(s,i,j,kind1,exclude_match=exclude_match)
        k = j + n
        self.colorRangeWithTag(s,j,k,kind2,exclude_match=False)    
        self.prev = (j,k,kind2)
        self.trace_match(kind1,s,i,j)
        self.trace_match(kind2,s,j,k)
        return k - i
    #@-node:ekr.20081205131308.101:match_word_and_regexp
    #@+node:ekr.20081205131308.102:skip_line
    def skip_line (self,s,i):

        if self.escape:
            escape = self.escape + '\n'
            n = len(escape)
            while i < len(s):
                j = g.skip_line(s,i)
                if not g.match(s,j-n,escape):
                    return j
                # g.trace('escape',s[i:j])
                i = j
            return i
        else:
            return g.skip_line(s,i)
                # Include the newline so we don't get a flash at the end of the line.
    #@nonl
    #@-node:ekr.20081205131308.102:skip_line
    #@+node:ekr.20081205131308.112:trace_match
    def trace_match(self,kind,s,i,j):

        if j != i and self.trace_match_flag:
            g.trace(kind,i,j,g.callers(2),self.dump(s[i:j]))
    #@nonl
    #@-node:ekr.20081205131308.112:trace_match
    #@-node:ekr.20081205131308.87:jEdit matchers
    #@+node:ekr.20081206062411.12:recolor & helpers
    def recolor (self,s):

        '''Recolor the line s from i to j.'''

        trace = False ; verbose = False
        if not self.s: return # Must handle empty lines!

        bunch,len_s = self.getPrevState(),len(s)
        # offset is the index in self.s of the first character of s.
        offset = bunch.offset + bunch.len_s
        # Calculate the bounds of the scan.
        lastFunc,lastMatch = bunch.lastFunc,bunch.lastMatch
        i = g.choose(lastFunc,lastMatch,offset)
        j = offset + len_s
        j = min(j,len(self.s))
        self.global_i,self.global_j = offset,j

        if trace: g.trace(
            '%s offset: %3s, i:%3s, j:%3s, s: %s' % (
            self.language,offset,i,j,repr(self.s[i:j])))

        while i < j:
            progress = i
            functions = self.rulesDict.get(self.s[i],[])
            for f in functions:
                if trace and verbose: g.trace('i',i,'f',f)
                n = f(self,self.s,i)
                if n is None or n < 0:
                    g.trace('Can not happen' % (repr(n),repr(f)))
                    lastFunc,lastMatch = None,i
                    break
                elif n > 0:
                    lastFunc,lastMatch = f,i
                    i += n
                    break # Must break
            else:
                i += 1
                lastFunc,lastMatch = None,i
            assert i > progress

        # Add one for the missing newline.
        self.setCurrentState(offset,len_s+1,lastFunc,lastMatch)
    #@+node:ekr.20081206062411.17:getPrevState
    def getPrevState (self):

        h = self.highlighter
        state = h.previousBlockState()
        bunch = self.stateDict.get(state)

        # g.trace(bunch)

        if not bunch:
            bunch = g.bunch(
                offset=0,len_s=0,
                lastFunc=None,lastMatch=0)

        return bunch
    #@-node:ekr.20081206062411.17:getPrevState
    #@+node:ekr.20081206062411.18:setCurrentState
    def setCurrentState (self,offset,len_s,lastFunc,lastMatch):

        h = self.highlighter
        state = h.currentBlockState()

        if state == -1:
            # Allocate a new state
            state = self.nextState
            self.nextState += 1
            h.setCurrentBlockState(state)

        # Remember this info.
        self.stateDict[state] = g.bunch(
            offset=offset,
            len_s=len_s,
            lastFunc=lastFunc,
            lastMatch=lastMatch)
    #@-node:ekr.20081206062411.18:setCurrentState
    #@-node:ekr.20081206062411.12:recolor & helpers
    #@+node:ekr.20081206062411.14:setTag
    def setTag (self,tag,i,j):

        trace = False
        w = self.w
        colorName = w.configDict.get(tag)

        # Munch the color name.
        if not colorName or colorName == 'black':
            return
        if colorName[-1].isdigit() and colorName[0] != '#':
            colorName = colorName[:-1]

        # Get the actual color.
        color = self.actualColorDict.get(colorName)
        if not color:
            color = QtGui.QColor(colorName)
            if color.isValid():
                self.actualColorDict[colorName] = color
            else:
                return g.trace('unknown color name',colorName)

        # Clip the colorizing to the global bounds.
        offset = self.global_i
        lim_i,lim_j = self.global_i,self.global_j
        clip_i = max(i,lim_i)
        clip_j = min(j,lim_j)
        ok = clip_i < clip_j

        if trace:
            kind = g.choose(ok,' ','***')
            s2 = g.choose(ok,self.s[clip_i:clip_j],self.s[i:j])
            g.trace('%3s %3s %3s %3s %3s %3s %3s %s' % (
                kind,tag,offset,i,j,lim_i,lim_j,s2))

        if ok:
            self.highlighter.setFormat(clip_i-offset,clip_j-clip_i,color)
    #@nonl
    #@-node:ekr.20081206062411.14:setTag
    #@+node:ekr.20081205131308.24:updateSyntaxColorer & helpers
    def updateSyntaxColorer (self,p):

        p = p.copy()

        # self.flag is True unless an unambiguous @nocolor is seen.
        self.flag = self.useSyntaxColoring(p)
        self.scanColorDirectives(p)
    #@nonl
    #@+node:ekr.20081205131308.26:scanColorDirectives
    def scanColorDirectives(self,p):

        '''Scan position p and p's ancestors looking for @comment,
        @language and @root directives,
        setting corresponding colorizer ivars.'''

        c = self.c
        if not c: return # May be None for testing.

        table = (
            ('lang-dict',   g.scanAtCommentAndAtLanguageDirectives),
            ('root',        c.scanAtRootDirectives),
        )

        # Set d by scanning all directives.
        aList = g.get_directives_dict_list(p)
        d = {}
        for key,func in table:
            val = func(aList)
            if val: d[key]=val

        # Post process.
        lang_dict       = d.get('lang-dict')
        self.rootMode   = d.get('root') or None

        if lang_dict:
            self.language       = lang_dict.get('language')
            self.comment_string = lang_dict.get('comment')
        else:
            self.language       = c.target_language and c.target_language.lower()
            self.comment_string = None

        # g.trace('self.language',self.language)
        return self.language # For use by external routines.
    #@-node:ekr.20081205131308.26:scanColorDirectives
    #@+node:ekr.20081205131308.23:useSyntaxColoring
    def useSyntaxColoring (self,p):

        """Return True unless p is unambiguously under the control of @nocolor."""

        p = p.copy() ; first = p.copy()
        val = True ; self.killcolorFlag = False

        # New in Leo 4.6: @nocolor-node disables one node only.
        theDict = g.get_directives_dict(p)
        if 'nocolor-node' in theDict:
            # g.trace('nocolor-node',p.headString())
            return False

        for p in p.self_and_parents_iter():
            theDict = g.get_directives_dict(p)
            no_color = 'nocolor' in theDict
            color = 'color' in theDict
            kill_color = 'killcolor' in theDict
            # A killcolor anywhere disables coloring.
            if kill_color:
                val = False ; self.killcolorFlag = True ; break
            # A color anywhere in the target enables coloring.
            if color and p == first:
                val = True ; break
            # Otherwise, the @nocolor specification must be unambiguous.
            elif no_color and not color:
                val = False ; break
            elif color and not no_color:
                val = True ; break

        # g.trace(first.headString(),val)
        return val
    #@-node:ekr.20081205131308.23:useSyntaxColoring
    #@-node:ekr.20081205131308.24:updateSyntaxColorer & helpers
    #@-others
#@-node:ekr.20081205131308.48:class jeditColorizer
#@-node:ekr.20081204090029.1:Syntax coloring
#@+node:ekr.20081121105001.515:Text widget classes...
#@+node:ekr.20081121105001.516: class leoQtBaseTextWidget
class leoQtBaseTextWidget (leoFrame.baseTextWidget):

    #@    @+others
    #@+node:ekr.20081121105001.517: Birth
    #@+node:ekr.20081121105001.518:ctor (leoQtBaseTextWidget)
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
        self.configDict = {} # Keys are tags, values are colors (names or values).
        self.useScintilla = False # This is used!

        if not c: return ### Can happen.

        # Hook up qt events.
        self.ev_filter = leoQtEventFilter(c,w=self,tag='body')
        self.widget.installEventFilter(self.ev_filter)

        self.widget.connect(self.widget,
            QtCore.SIGNAL("textChanged()"),self.onTextChanged)

        self.injectIvars(c)
    #@-node:ekr.20081121105001.518:ctor (leoQtBaseTextWidget)
    #@+node:ekr.20081121105001.519:injectIvars
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
    #@-node:ekr.20081121105001.519:injectIvars
    #@-node:ekr.20081121105001.517: Birth
    #@+node:ekr.20081121105001.520: Do nothings
    def bind (self,stroke,command,**keys):
        pass # eventFilter handles all keys.
    #@-node:ekr.20081121105001.520: Do nothings
    #@+node:ekr.20081121105001.521: Must be defined in base class
    #@+node:ekr.20081121105001.522: Focus
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
    #@-node:ekr.20081121105001.522: Focus
    #@+node:ekr.20081121105001.523: Indices
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
            i = g.convertRowColToPythonIndex(s,row-1,col) # Bug fix: 2008/11/11
            # g.trace(index,row,col,i,g.callers(6))
            return i

    toGuiIndex = toPythonIndex
    #@-node:ekr.20081121105001.523: Indices
    #@+node:ekr.20081121105001.524: Text getters/settters
    #@+node:ekr.20081121105001.525:appendText
    def appendText(self,s):

        s2 = self.getAllText()
        self.setAllText(s2+s,insert=len(s2))

    #@-node:ekr.20081121105001.525:appendText
    #@+node:ekr.20081121105001.526:delete
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
    #@-node:ekr.20081121105001.526:delete
    #@+node:ekr.20081121105001.527:deleteTextSelection
    def deleteTextSelection (self):

        i,j = self.getSelectionRange()
        self.delete(i,j)
    #@-node:ekr.20081121105001.527:deleteTextSelection
    #@+node:ekr.20081121105001.528:get
    def get(self,i,j=None):

        w = self.widget
        s = self.getAllText()
        i = self.toGuiIndex(i)
        if j is None: j = i+1
        j = self.toGuiIndex(j)
        return s[i:j]
    #@-node:ekr.20081121105001.528:get
    #@+node:ekr.20081121105001.529:getLastPosition
    def getLastPosition(self):

        return len(self.getAllText())
    #@-node:ekr.20081121105001.529:getLastPosition
    #@+node:ekr.20081121105001.530:getSelectedText
    def getSelectedText(self):

        w = self.widget

        i,j = self.getSelectionRange()
        if i == j:
            return ''
        else:
            s = self.getAllText()
            # g.trace(repr(s[i:j]))
            return s[i:j]
    #@-node:ekr.20081121105001.530:getSelectedText
    #@+node:ekr.20081121105001.531:insert
    def insert(self,i,s):

        s2 = self.getAllText()
        i = self.toGuiIndex(i)
        self.setAllText(s2[:i] + s + s2[i:],insert=i+len(s))
        return i
    #@-node:ekr.20081121105001.531:insert
    #@+node:ekr.20081121105001.532:selectAllText
    def selectAllText(self,insert=None):

        w = self.widget
        w.selectAll()
        if insert is not None:
            self.setInsertPoint(insert)
        # g.trace('insert',insert)

    #@-node:ekr.20081121105001.532:selectAllText
    #@+node:ekr.20081121105001.533:setSelectionRange & dummy helper
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
    #@+node:ekr.20081121105001.534:setSelectionRangeHelper
    def setSelectionRangeHelper(self,i,j,insert):

        self.oops()
    #@-node:ekr.20081121105001.534:setSelectionRangeHelper
    #@-node:ekr.20081121105001.533:setSelectionRange & dummy helper
    #@-node:ekr.20081121105001.524: Text getters/settters
    #@+node:ekr.20081121105001.535:getName (baseTextWidget)
    def getName (self):

        # g.trace('leoQtBaseTextWidget',self.name,g.callers())

        return self.name
    #@-node:ekr.20081121105001.535:getName (baseTextWidget)
    #@+node:ekr.20081121105001.536:onTextChanged
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
        oldText = g.app.gui.toUnicode(p.v.t._bodyString)
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
    #@-node:ekr.20081121105001.536:onTextChanged
    #@+node:ekr.20081121105001.537:indexWarning
    warningsDict = {}

    def indexWarning (self,s):

        return

        # if s not in self.warningsDict:
            # g.es_print('warning: using dubious indices in %s' % (s),color='red')
            # g.es_print('callers',g.callers(5))
            # self.warningsDict[s] = True
    #@-node:ekr.20081121105001.537:indexWarning
    #@-node:ekr.20081121105001.521: Must be defined in base class
    #@+node:ekr.20081121105001.538: May be overridden in subclasses
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

    #@+node:ekr.20081121105001.539:Configuration
    # Configuration will be handled by style sheets.
    def cget(self,*args,**keys):            return None
    def configure (self,*args,**keys):      pass
    def setBackgroundColor(self,color):     pass
    def setEditorColors (self,bg,fg):       pass
    def setForegroundColor(self,color):     pass
    #@-node:ekr.20081121105001.539:Configuration
    #@+node:ekr.20081121105001.540:Idle time
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
    #@-node:ekr.20081121105001.540:Idle time
    #@+node:ekr.20081121105001.541:Coloring (baseTextWidget)
    def removeAllTags(self):
        s = self.getAllText()
        self.colorSelection(0,len(s),'black')

    def tag_names (self):
        return []
    #@+node:ekr.20081121105001.542:colorSelection
    def colorSelection (self,i,j,colorName):

        w = self.widget
        if not colorName: return
        if g.unitTesting: return

        # Unlike Tk names, Qt names don't end in a digit.
        if colorName[-1].isdigit() and colorName[0] != '#':
            color = QtGui.QColor(colorName[:-1])
        else:
            color = QtGui.QColor(colorName)

        if not color.isValid():
            # g.trace('unknown color name',colorName)
            return

        sb = w.verticalScrollBar()
        pos = sb.sliderPosition()
        old_i,old_j = self.getSelectionRange()
        old_ins = self.getInsertPoint()
        self.setSelectionRange(i,j)
        w.setTextColor(color)
        self.setSelectionRange(old_i,old_j,insert=old_ins)
        sb.setSliderPosition(pos)
    #@-node:ekr.20081121105001.542:colorSelection
    #@+node:ekr.20081124102726.10:tag_add
    def tag_add(self,tag,x1,x2):

        val = self.configDict.get(tag)
        if val:
            self.colorSelection(x1,x2,val)

        # elif tag == 'comment1':
            # self.colorSelection(x1,x2,'firebrick')
        # else:
            # g.trace(tag)
    #@-node:ekr.20081124102726.10:tag_add
    #@+node:ekr.20081124102726.11:tag_config/ure
    def tag_config (self,*args,**keys):

        if len(args) == 1:
            key = args[0]
            self.tags[key] = keys
            val = keys.get('foreground')
            if val:
                # g.trace(key,val)
                self.configDict [key] = val
        else:
            g.trace('oops',args,keys)

    tag_configure = tag_config
    #@nonl
    #@-node:ekr.20081124102726.11:tag_config/ure
    #@-node:ekr.20081121105001.541:Coloring (baseTextWidget)
    #@-node:ekr.20081121105001.538: May be overridden in subclasses
    #@+node:ekr.20081121105001.543: Must be overridden in subclasses
    def getAllText(self):                   self.oops()
    def getInsertPoint(self):               self.oops()
    def getSelectionRange(self,sort=True):  self.oops()
    def hasSelection(self):                 self.oops()
    def see(self,i):                        self.oops()
    def setAllText(self,s,insert=None):     self.oops()
    def setInsertPoint(self,i):             self.oops()
    #@-node:ekr.20081121105001.543: Must be overridden in subclasses
    #@-others
#@-node:ekr.20081121105001.516: class leoQtBaseTextWidget
#@+node:ekr.20081121105001.544: class leoQLineEditWidget
class leoQLineEditWidget (leoQtBaseTextWidget):

    #@    @+others
    #@+node:ekr.20081121105001.545:Birth
    #@+node:ekr.20081121105001.546:ctor
    def __init__ (self,widget,name,c=None):

        # Init the base class.
        leoQtBaseTextWidget.__init__(self,widget,name,c=c)

        self.baseClassName='leoQLineEditWidget'

        # g.trace('leoQLineEditWidget',id(widget),g.callers(4))

        self.setConfig()
        self.setFontFromConfig()
        self.setColorFromConfig()
    #@-node:ekr.20081121105001.546:ctor
    #@+node:ekr.20081121105001.547:setFontFromConfig
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
    #@-node:ekr.20081121105001.547:setFontFromConfig
    #@+node:ekr.20081121105001.548:setColorFromConfig
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
    #@-node:ekr.20081121105001.548:setColorFromConfig
    #@+node:ekr.20081121105001.549:setConfig
    def setConfig (self):
        pass
    #@nonl
    #@-node:ekr.20081121105001.549:setConfig
    #@-node:ekr.20081121105001.545:Birth
    #@+node:ekr.20081121105001.550:Widget-specific overrides (QLineEdit)
    #@+node:ekr.20081121105001.551:getAllText
    def getAllText(self):

        w = self.widget
        s = w.text()
        return g.app.gui.toUnicode(s)
    #@nonl
    #@-node:ekr.20081121105001.551:getAllText
    #@+node:ekr.20081121105001.552:getInsertPoint
    def getInsertPoint(self):

        i = self.widget.cursorPosition()
        # g.trace(i)
        return i
    #@-node:ekr.20081121105001.552:getInsertPoint
    #@+node:ekr.20081121105001.553:getSelectionRange
    def getSelectionRange(self,sort=True):

        w = self.widget

        if w.hasSelectedText():
            i = w.selectionStart()
            s = w.selectedText()
            s = g.app.gui.toUnicode(s)
            j = i + len(s)
        else:
            i = j = w.cursorPosition()

        # g.trace(i,j)
        return i,j
    #@-node:ekr.20081121105001.553:getSelectionRange
    #@+node:ekr.20081121105001.554:hasSelection
    def hasSelection(self):

        return self.widget.hasSelection()
    #@-node:ekr.20081121105001.554:hasSelection
    #@+node:ekr.20081121105001.555:see & seeInsertPoint
    def see(self,i):
        pass

    def seeInsertPoint (self):
        pass
    #@-node:ekr.20081121105001.555:see & seeInsertPoint
    #@+node:ekr.20081121105001.556:setAllText
    def setAllText(self,s,insert=None):

        w = self.widget
        i = g.choose(insert is None,0,insert)
        w.setText(s)
        if insert is not None:
            self.setSelectionRange(i,i,insert=i)

        # g.trace(i,repr(s))
    #@-node:ekr.20081121105001.556:setAllText
    #@+node:ekr.20081121105001.557:setInsertPoint
    def setInsertPoint(self,i):

        w = self.widget
        s = w.text()
        s = g.app.gui.toUnicode(s)
        i = max(0,min(i,len(s)))
        w.setCursorPosition(i)
    #@-node:ekr.20081121105001.557:setInsertPoint
    #@+node:ekr.20081121105001.558:setSelectionRangeHelper
    def setSelectionRangeHelper(self,i,j,insert):

        w = self.widget
        # g.trace('i',i,'j',j,'insert',insert,g.callers(4))
        if i > j: i,j = j,i
        s = w.text()
        s = g.app.gui.toUnicode(s)
        i = max(0,min(i,len(s)))
        j = max(0,min(j,len(s)))
        k = max(0,min(j-i,len(s)))
        if i == j:
            w.setCursorPosition(i)
        else:
            w.setSelection(i,k)
    #@-node:ekr.20081121105001.558:setSelectionRangeHelper
    #@-node:ekr.20081121105001.550:Widget-specific overrides (QLineEdit)
    #@-others
#@-node:ekr.20081121105001.544: class leoQLineEditWidget
#@+node:ekr.20081121105001.559: class leoQScintillaWidget
class leoQScintillaWidget (leoQtBaseTextWidget):

    #@    @+others
    #@+node:ekr.20081121105001.560:Birth
    #@+node:ekr.20081121105001.561:ctor
    def __init__ (self,widget,name,c=None):

        # Init the base class.
        leoQtBaseTextWidget.__init__(self,widget,name,c=c)

        self.baseClassName='leoQScintillaWidget'

        self.useScintilla = True
        self.setConfig()
    #@-node:ekr.20081121105001.561:ctor
    #@+node:ekr.20081121105001.562:setConfig
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
    #@-node:ekr.20081121105001.562:setConfig
    #@-node:ekr.20081121105001.560:Birth
    #@+node:ekr.20081121105001.563:Widget-specific overrides (QScintilla)
    #@+node:ekr.20081121105001.564:getAllText
    def getAllText(self):

        w = self.widget
        s = w.text()
        s = g.app.gui.toUnicode(s)
        return s
    #@-node:ekr.20081121105001.564:getAllText
    #@+node:ekr.20081121105001.565:getInsertPoint
    def getInsertPoint(self):

        w = self.widget
        s = self.getAllText()
        row,col = w.getCursorPosition()  
        i = g.convertRowColToPythonIndex(s, row, col)
        return i
    #@-node:ekr.20081121105001.565:getInsertPoint
    #@+node:ekr.20081121105001.566:getSelectionRange
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

    #@-node:ekr.20081121105001.566:getSelectionRange
    #@+node:ekr.20081121105001.567:hasSelection
    def hasSelection(self):

        return self.widget.hasSelectedText()
    #@-node:ekr.20081121105001.567:hasSelection
    #@+node:ekr.20081121105001.568:see
    def see(self,i):

        # Ok for now.  Using SCI_SETYCARETPOLICY might be better.
        w = self.widget
        s = self.getAllText()
        row,col = g.convertPythonIndexToRowCol(s,i)
        w.ensureLineVisible(row)

    # Use base-class method for seeInsertPoint.
    #@nonl
    #@-node:ekr.20081121105001.568:see
    #@+node:ekr.20081121105001.569:setAllText
    def setAllText(self,s,insert=None):

        '''Set the text of the widget.

        If insert is None, the insert point, selection range and scrollbars are initied.
        Otherwise, the scrollbars are preserved.'''

        w = self.widget
        w.setText(s)

    #@-node:ekr.20081121105001.569:setAllText
    #@+node:ekr.20081121105001.570:setInsertPoint
    def setInsertPoint(self,i):

        w = self.widget
        w.SendScintilla(w.SCI_SETCURRENTPOS,i)
        w.SendScintilla(w.SCI_SETANCHOR,i)
    #@-node:ekr.20081121105001.570:setInsertPoint
    #@+node:ekr.20081121105001.571:setSelectionRangeHelper
    def setSelectionRangeHelper(self,i,j,insert):

        w = self.widget

        # g.trace('i',i,'j',j,'insert',insert,g.callers(4))

        if insert in (j,None):
            self.setInsertPoint(j)
            w.SendScintilla(w.SCI_SETANCHOR,i)
        else:
            self.setInsertPoint(i)
            w.SendScintilla(w.SCI_SETANCHOR,j)
    #@-node:ekr.20081121105001.571:setSelectionRangeHelper
    #@-node:ekr.20081121105001.563:Widget-specific overrides (QScintilla)
    #@-others
#@-node:ekr.20081121105001.559: class leoQScintillaWidget
#@+node:ekr.20081121105001.572: class leoQTextEditWidget
class leoQTextEditWidget (leoQtBaseTextWidget):

    #@    @+others
    #@+node:ekr.20081121105001.573:Birth
    #@+node:ekr.20081121105001.574:ctor
    def __init__ (self,widget,name,c=None):

        # Init the base class.
        leoQtBaseTextWidget.__init__(self,widget,name,c=c)

        self.baseClassName='leoQTextEditWidget'

        widget.setUndoRedoEnabled(False)

        self.setConfig()
        self.setFontFromConfig()
        self.setColorFromConfig()
    #@-node:ekr.20081121105001.574:ctor
    #@+node:ekr.20081121105001.575:setFontFromConfig
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
    #@-node:ekr.20081121105001.575:setFontFromConfig
    #@+node:ekr.20081121105001.576:setColorFromConfig
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
    #@-node:ekr.20081121105001.576:setColorFromConfig
    #@+node:ekr.20081121105001.577:setConfig
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
    #@-node:ekr.20081121105001.577:setConfig
    #@-node:ekr.20081121105001.573:Birth
    #@+node:ekr.20081121105001.578:Widget-specific overrides (QTextEdit)
    #@+node:ekr.20081121105001.579:flashCharacter
    def flashCharacter(self,i,bg='white',fg='red',flashes=3,delay=75):

        # This causes problems during unit tests.
        # The selection point isn't restored in time.
        if g.app.unitTesting: return

        c = self.c ; w = self.widget

        # Reduce the flash time to the minimum.
        # flashes = max(1,min(2,flashes))
        # flashes = 1
        # delay = max(10,min(50,delay))

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

            if n > 0:
                self.setSelectionRange(i,i)
                after(addFlashCallback)
            else:
                w.blockSignals(False)
                w.setDisabled(False)
                i = self.afterFlashIndex
                self.setSelectionRange(i,i,insert=i)
                # g.trace('i',i)
                w.setFocus()

        self.flashCount = flashes
        self.flashIndex = i
        self.afterFlashIndex = self.getInsertPoint()
        w.setDisabled(True)
        w.blockSignals(True)
        addFlashCallback()
    #@-node:ekr.20081121105001.579:flashCharacter
    #@+node:ekr.20081121105001.580:getAllText
    def getAllText(self):

        w = self.widget
        s = w.toPlainText()
        return g.app.gui.toUnicode(s)
    #@nonl
    #@-node:ekr.20081121105001.580:getAllText
    #@+node:ekr.20081121105001.581:getInsertPoint
    def getInsertPoint(self):

        return self.widget.textCursor().position()
    #@-node:ekr.20081121105001.581:getInsertPoint
    #@+node:ekr.20081121105001.582:getSelectionRange
    def getSelectionRange(self,sort=True):

        w = self.widget
        tc = w.textCursor()
        i,j = tc.selectionStart(),tc.selectionEnd()
        # g.trace(i,j,g.callers(4))
        return i,j
    #@nonl
    #@-node:ekr.20081121105001.582:getSelectionRange
    #@+node:ekr.20081121105001.583:getYScrollPosition
    def getYScrollPosition(self):

        w = self.widget
        sb = w.verticalScrollBar()
        i = sb.sliderPosition()

        # Return a tuple, only the first of which is used.
        return i,i 
    #@-node:ekr.20081121105001.583:getYScrollPosition
    #@+node:ekr.20081121105001.584:hasSelection
    def hasSelection(self):

        return self.widget.textCursor().hasSelection()
    #@-node:ekr.20081121105001.584:hasSelection
    #@+node:ekr.20081121105001.585:see
    def see(self,i):

        self.widget.ensureCursorVisible()
    #@nonl
    #@-node:ekr.20081121105001.585:see
    #@+node:ekr.20081121105001.586:seeInsertPoint
    def seeInsertPoint (self):

        self.widget.ensureCursorVisible()
    #@-node:ekr.20081121105001.586:seeInsertPoint
    #@+node:ekr.20081121105001.587:setAllText
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
    #@-node:ekr.20081121105001.587:setAllText
    #@+node:ekr.20081121105001.588:setInsertPoint
    def setInsertPoint(self,i):

        w = self.widget
        s = w.toPlainText()
        cursor = w.textCursor()
        i = max(0,min(i,len(s)))
        cursor.setPosition(i)
        w.setTextCursor(cursor)
    #@-node:ekr.20081121105001.588:setInsertPoint
    #@+node:ekr.20081121105001.589:setSelectionRangeHelper & helper
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
    #@+node:ekr.20081121105001.590:lengthHelper
    def lengthHelper(self):

        '''Return the length of the text.'''

        w = self.widget
        cursor = w.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        n = cursor.position()
        return n

    #@-node:ekr.20081121105001.590:lengthHelper
    #@-node:ekr.20081121105001.589:setSelectionRangeHelper & helper
    #@+node:ekr.20081121105001.591:setYScrollPosition
    def setYScrollPosition(self,pos):

        w = self.widget
        sb = w.verticalScrollBar()
        if pos is None: pos = 0
        elif type(pos) == types.TupleType:
            pos = pos[0]
        sb.setSliderPosition(pos)
    #@-node:ekr.20081121105001.591:setYScrollPosition
    #@-node:ekr.20081121105001.578:Widget-specific overrides (QTextEdit)
    #@-others
#@-node:ekr.20081121105001.572: class leoQTextEditWidget
#@+node:ekr.20081121105001.592:class leoQtHeadlineWidget
class leoQtHeadlineWidget (leoQLineEditWidget):

    def __repr__ (self):
        return 'leoQLineEditWidget: %s' % id(self)
#@nonl
#@-node:ekr.20081121105001.592:class leoQtHeadlineWidget
#@+node:ekr.20081121105001.593:class findTextWrapper
class findTextWrapper (leoQLineEditWidget):

    '''A class representing the find/change edit widgets.'''

    pass
#@-node:ekr.20081121105001.593:class findTextWrapper
#@+node:ekr.20081121105001.594:class leoQtMinibuffer (leoQLineEditWidget)
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
#@-node:ekr.20081121105001.594:class leoQtMinibuffer (leoQLineEditWidget)
#@-node:ekr.20081121105001.515:Text widget classes...
#@-others
#@-node:ekr.20081121105001.188:@thin qtGui.py
#@-leo
