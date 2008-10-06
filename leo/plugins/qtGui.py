# -*- coding: utf-8 -*-
#@+leo-ver=4-thin
#@+node:ekr.20081004102201.619:@thin qtGui.py
#@@first

'''qt gui plugin.'''

#@@language python
#@@tabwidth -4
#@@pagewidth 80

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
import leo.core.leoNodes as leoNodes

import os
import sys
import time

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
        g.app.gui.finishCreate()
        g.plugin_signon(__name__)
        return True
#@-node:ekr.20081004102201.621:init
#@+node:ekr.20081004102201.627:embed_ipython
def embed_ipython():

    import IPython.ipapi

    sys.argv = ['ipython', '-p' , 'sh']
    ses = IPython.ipapi.make_session(dict(w = window))
    ip = ses.IP.getapi()
    ip.load('ipy_leo')
    ses.mainloop()
#@nonl
#@-node:ekr.20081004102201.627:embed_ipython
#@+node:ekr.20081004102201.626:tstart & tstop
def tstart():
    global __timing
    __timing = time.time()

def tstop():
    print ("Time: %1.2fsec" % (time.time() - __timing))
#@-node:ekr.20081004102201.626:tstart & tstop
#@-node:ekr.20081004102201.623: Module level
#@+node:ekr.20081004102201.629:class  Window (QMainWindow,Ui_MainWindow)
class Window(QtGui.QMainWindow, qt_main.Ui_MainWindow):

    '''A class representing all parts of the main Qt window
    as created by Designer

    All leoQtX classes use the ivars of this Window class to
    support operations requested by Leo's core.
    '''

    #@    @+others
    #@+node:ekr.20081004172422.884: ctor (Window)
    def __init__(self, c,parent = None):

        self.c = c
        QtGui.QWidget.__init__(self, parent)
        signal = QtCore.SIGNAL
        self.setupUi(self)
        self.connect(self.treeWidget,signal("itemSelectionChanged()"), self.tree_select )
        if 0:
            self.connect(self.actionOpen,signal("activated()"),self.open_file)
            self.connect(self.actionSave,signal("activated()"),self.save_file)
            #self.connect(self.searchButton,signal("clicked()"), self.search)
            #self.connect(self.actionIPython,signal("activated()"),self.embed_ipython)
        self.connect(self.textEdit, signal("textChanged()"),self.text_changed)
        self.connect(self.lineEdit,  signal("returnPressed()"),  self.minibuffer_run)
        self.selecting = True
        self.widget_dirty = False
        # XXX todo. this just makes the text editor a bit friendlier for
        # python. Eventually, it will be configurable the leo way
        lexer = Qsci.QsciLexerPython(self.textEdit)
        self.textEdit.setLexer(lexer)
        self.textEdit.setIndentationWidth(4)
        self.textEdit.setIndentationsUseTabs(False)
        self.textEdit.setAutoIndent(True)

        self.ev_filt = leoQtEventFilter()
        self.ev_filt.bindings['Ctrl+H'] = self.edit_current_headline
        self.textEdit.installEventFilter(self.ev_filt)
        self.treeWidget.installEventFilter(self.ev_filt)
        path = g.os_path_join(g.app.loadDir,"..","Icons") 
        self.icon_std = QtGui.QIcon(path + '/box00.GIF')
        self.icon_dirty = QtGui.QIcon(path + '/box01.GIF')

        # The following ivars (and more) are inherited from UiMainWindow:
            # self.lineEdit = QtGui.QLineEdit(self.centralwidget)
            # self.menubar = QtGui.QMenuBar(MainWindow)
            # self.tabWidget = QtGui.QTabWidget(self.splitter)
            # self.textEdit = Qsci.QsciScintilla(self.splitter_2)
            # self.treeWidget = QtGui.QTreeWidget(self.splitter)
    #@-node:ekr.20081004172422.884: ctor (Window)
    #@+node:ekr.20081004172422.888:clear_model
    def clear_model(self):

        c = self.c
        self.treeWidget.clear()
        self.items = {}
        self.treeitems = {}
        if c:
            c.close()
            c = None

    #@-node:ekr.20081004172422.888:clear_model
    #@+node:ekr.20081004172422.889:populate_tree
    def populate_tree(self, parent=None):

        """ Render vnodes in tree """

        c = self.c
        self.items = {}
        self.treeitems = {}
        self.treeWidget.clear()
        for p in c.allNodes_iter():
            parent = self.items.get(p.parent().v,self.treeWidget)
            it = QtGui.QTreeWidgetItem(parent)
            it.setIcon(0, self.icon_std)
            it.setFlags(it.flags() | QtCore.Qt.ItemIsEditable)
            self.items[p.v] = it
            self.treeitems[id(it)] = p.t
            it.setText(0, p.headString())

    def minibuffer_run(self):

        c = self.c
        cmd = str(self.lineEdit.text())
        print "minibuffer run:", cmd
        c.executeMinibufferCommand(cmd)

    #@-node:ekr.20081004172422.889:populate_tree
    #@+node:ekr.20081004172422.890:flush_current_tnode
    def flush_current_tnode(self):

        text = str(self.textEdit.text())
        self.cur_tnode.setBodyString(text)

    #@-node:ekr.20081004172422.890:flush_current_tnode
    #@+node:ekr.20081004172422.891:tree_select
    def tree_select(self):
        #print "tree selected!"
        self.selecting = True

        if self.widget_dirty:
            self.flush_current_tnode()

        self.cur_tnode = self.treeitems[id(self.treeWidget.currentItem())]
        self.textEdit.setText(self.cur_tnode.bodyString())
        self.selecting = False
        self.widget_dirty = False

    #@-node:ekr.20081004172422.891:tree_select
    #@+node:ekr.20081004172422.892:text_changed
    def text_changed(self):
        if self.selecting:
            return
        #print "text changed"
        if not self.widget_dirty:
            self.treeWidget.currentItem().setIcon(0,self.icon_dirty)
        self.widget_dirty = True

    #@-node:ekr.20081004172422.892:text_changed
    #@+node:ekr.20081004172422.894:edit_current_headline
    def edit_current_headline(self):
        #self.treeWidget.openPersistentEditor(self.treeWidget.currentItem())
        self.treeWidget.editItem(self.treeWidget.currentItem())
    #@nonl
    #@-node:ekr.20081004172422.894:edit_current_headline
    #@-others

#@-node:ekr.20081004102201.629:class  Window (QMainWindow,Ui_MainWindow)
#@+node:ekr.20081004172422.502:class leoQtBody (leoBody) (not used yet)
class leoQtBody (leoFrame.leoBody):

    """A class that represents the body pane of a Qt window."""

    #@    @+others
    #@+node:ekr.20081004172422.503: Birth & death
    #@+node:ekr.20081004172422.504:qtBody. __init__
    def __init__ (self,frame,parentFrame):

        g.trace("***** leoQtBody")

        # Call the base class constructor.
        leoFrame.leoBody.__init__(self,frame,parentFrame)

        c = self.c ; p = c.currentPosition()

        self.bodyCtrl = None ###
        self.editor_name = None
        self.editor_v = None

        self.trace_onBodyChanged = c.config.getBool('trace_onBodyChanged')

        self.numberOfEditors = 1
        self.totalNumberOfEditors = 1

        # self.bodyCtrl = self.createControl(parentFrame,p)
        # self.colorizer = leoColor.colorizer(c)
    #@-node:ekr.20081004172422.504:qtBody. __init__
    #@+node:ekr.20081004172422.505:qtBody.createBindings
    def createBindings (self,w=None):

        '''(qtBody) Create gui-dependent bindings.
        These are *not* made in nullBody instances.'''

        frame = self.frame ; c = self.c ; k = c.k
        if not w: w = self.bodyCtrl

        return ### 

        c.bind(w,'<Key>', k.masterKeyHandler)

        def onFocusOut(event,c=c):
            # This interferes with inserting new nodes.
                # c.k.setDefaultInputState()
            self.setEditorColors(
                bg=c.k.unselected_body_bg_color,
                fg=c.k.unselected_body_fg_color)
            # This is required, for example, when typing Alt-Shift-anyArrow in insert mode.
            # But we suppress coloring in the widget.
            oldState = k.unboundKeyAction
            k.unboundKeyAction = k.defaultUnboundKeyAction
            c.k.showStateAndMode(w=g.app.gui.get_focus(c))
            k.unboundKeyAction = oldState

        def onFocusIn(event,c=c):
            # g.trace('callback')
            c.k.setDefaultInputState()
            c.k.showStateAndMode()  # TNB - fix color when window manager returns focus to Leo

        c.bind(w,'<FocusOut>', onFocusOut)
        c.bind(w,'<FocusIn>', onFocusIn)

        table = [
            ('<Button-1>',  frame.OnBodyClick,          k.masterClickHandler),
            ('<Button-3>',  frame.OnBodyRClick,         k.masterClick3Handler),
            ('<Double-1>',  frame.OnBodyDoubleClick,    k.masterDoubleClickHandler),
            ('<Double-3>',  None,                       k.masterDoubleClick3Handler),
            ('<Button-2>',  frame.OnPaste,              k.masterClickHandler),
        ]

        table2 = (
            ('<Button-2>',  frame.OnPaste,              k.masterClickHandler),
        )

        if c.config.getBool('allow_middle_button_paste'):
            table.extend(table2)

        for kind,func,handler in table:
            def bodyClickCallback(event,handler=handler,func=func):
                return handler(event,func)

            c.bind(w,kind,bodyClickCallback)
    #@-node:ekr.20081004172422.505:qtBody.createBindings
    #@+node:ekr.20081004172422.506:qtBody.createControl
    def createControl (self,parentFrame,p):

        return ###

        c = self.c

        # New in 4.4.1: make the parent frame a Pmw.PanedWidget.
        # self.numberOfEditors = 1 ; name = '1'
        # self.totalNumberOfEditors = 1

        orient = c.config.getString('editor_orientation') or 'horizontal'
        if orient not in ('horizontal','vertical'): orient = 'horizontal'

        self.pb = pb = Pmw.PanedWidget(parentFrame,orient=orient)
        parentFrame = pb.add(name)
        pb.pack(expand=1,fill='both') # Must be done after the first page created.

        w = self.createTextWidget(parentFrame,p,name)
        self.editorWidgets[name] = w

        return w
    #@-node:ekr.20081004172422.506:qtBody.createControl
    #@+node:ekr.20081004172422.507:qtBody.createTextWidget
    def createTextWidget (self,parentFrame,p,name):

        c = self.c

        parentFrame.configure(bg='LightSteelBlue1')

        wrap = c.config.getBool('body_pane_wraps')
        wrap = g.choose(wrap,"word","none")

        # Setgrid=1 cause severe problems with the font panel.
        body = w = leoQtTextWidget (parentFrame,name='body-pane',
            bd=2,bg="white",relief="flat",setgrid=0,wrap=wrap)

        # bodyBar = qt.Scrollbar(parentFrame,name='bodyBar')

        # def yscrollCallback(x,y,bodyBar=bodyBar,w=w):
            # # g.trace(x,y,g.callers())
            # if hasattr(w,'leo_scrollBarSpot'):
                # w.leo_scrollBarSpot = (x,y)
            # return bodyBar.set(x,y)

        # body['yscrollcommand'] = yscrollCallback # bodyBar.set

        # bodyBar['command'] =  body.yview
        # bodyBar.pack(side="right", fill="y")

        # # Always create the horizontal bar.
        # bodyXBar = qt.Scrollbar(
            # parentFrame,name='bodyXBar',orient="horizontal")
        # body['xscrollcommand'] = bodyXBar.set
        # bodyXBar['command'] = body.xview

        # if wrap == "none":
            # # g.trace(parentFrame)
            # bodyXBar.pack(side="bottom", fill="x")

        # body.pack(expand=1,fill="both")

        self.wrapState = wrap

        if 0: # Causes the cursor not to blink.
            body.configure(insertofftime=0)

        # Inject ivars
        if name == '1':
            w.leo_p = w.leo_v = None # Will be set when the second editor is created.
        else:
            w.leo_p = p.copy()
            w.leo_v = w.leo_p.v

        w.leo_active = True
        # New in Leo 4.4.4 final: inject the scrollbar items into the text widget.
        w.leo_bodyBar = bodyBar # 2007/10/31
        w.leo_bodyXBar = bodyXBar # 2007/10/31
        w.leo_chapter = None
        w.leo_frame = parentFrame
        w.leo_name = name
        w.leo_label = None
        w.leo_label_s = None
        w.leo_scrollBarSpot = None
        w.leo_insertSpot = None
        w.leo_selection = None

        return w
    #@nonl
    #@-node:ekr.20081004172422.507:qtBody.createTextWidget
    #@-node:ekr.20081004172422.503: Birth & death
    #@+node:ekr.20081004172422.508:qtBody.setColorFromConfig
    def setColorFromConfig (self,w=None):

        return ###

        c = self.c
        if w is None: w = self.bodyCtrl

        bg = c.config.getColor("body_text_background_color") or 'white'
        # g.trace(id(w),bg)

        try: w.configure(bg=bg)
        except:
            g.es("exception setting body text background color")
            g.es_exception()

        fg = c.config.getColor("body_text_foreground_color") or 'black'
        try: w.configure(fg=fg)
        except:
            g.es("exception setting body textforeground color")
            g.es_exception()

        bg = c.config.getColor("body_insertion_cursor_color")
        if bg:
            try: w.configure(insertbackground=bg)
            except:
                g.es("exception setting body pane cursor color")
                g.es_exception()

        sel_bg = c.config.getColor('body_text_selection_background_color') or 'Gray80'
        try: w.configure(selectbackground=sel_bg)
        except Exception:
            g.es("exception setting body pane text selection background color")
            g.es_exception()

        sel_fg = c.config.getColor('body_text_selection_foreground_color') or 'white'
        try: w.configure(selectforeground=sel_fg)
        except Exception:
            g.es("exception setting body pane text selection foreground color")
            g.es_exception()

        if sys.platform != "win32": # Maybe a Windows bug.
            fg = c.config.getColor("body_cursor_foreground_color")
            bg = c.config.getColor("body_cursor_background_color")
            if fg and bg:
                cursor="xterm" + " " + fg + " " + bg
                try: w.configure(cursor=cursor)
                except:
                    import traceback ; traceback.print_exc()
    #@-node:ekr.20081004172422.508:qtBody.setColorFromConfig
    #@+node:ekr.20081004172422.509:qtBody.setFontFromConfig
    def setFontFromConfig (self,w=None):

        return ###

        c = self.c

        if not w: w = self.bodyCtrl

        font = c.config.getFontFromParams(
            "body_text_font_family", "body_text_font_size",
            "body_text_font_slant",  "body_text_font_weight",
            c.config.defaultBodyFontSize)

        self.fontRef = font # ESSENTIAL: retain a link to font.
        w.configure(font=font)

        # g.trace("BODY",body.cget("font"),font.cget("family"),font.cget("weight"))
    #@-node:ekr.20081004172422.509:qtBody.setFontFromConfig
    #@+node:ekr.20081004172422.510:Focus (qtBody)
    def hasFocus (self):

        # return self.bodyCtrl == self.frame.top.focus_displayof()
        return None

    def setFocus (self):

        self.c.widgetWantsFocus(self.bodyCtrl)
    #@-node:ekr.20081004172422.510:Focus (qtBody)
    #@+node:ekr.20081004172422.511:forceRecolor
    def forceFullRecolor (self):

        self.forceFullRecolorFlag = True
    #@-node:ekr.20081004172422.511:forceRecolor
    #@+node:ekr.20081004172422.512:Qt bindings (qtBody) (TO DO)
    #@+node:ekr.20081004172422.513:Color tags (Qt spelling) (qtBody)
    def tag_add (self,tagName,index1,index2):
        pass # self.bodyCtrl.tag_add(tagName,index1,index2)

    def tag_bind (self,tagName,event,callback):
        pass # self.c.tag_bind(self.bodyCtrl,tagName,event,callback)

    def tag_configure (self,colorName,**keys):
        pass # self.bodyCtrl.tag_configure(colorName,keys)

    def tag_delete(self,tagName):
        pass # self.bodyCtrl.tag_delete(tagName)

    def tag_names(self,*args): # New in Leo 4.4.1.
        pass # return self.bodyCtrl.tag_names(*args)

    def tag_remove (self,tagName,index1,index2):
        pass # return self.bodyCtrl.tag_remove(tagName,index1,index2)
    #@-node:ekr.20081004172422.513:Color tags (Qt spelling) (qtBody)
    #@+node:ekr.20081004172422.514:Configuration (Qt spelling) (qtBody)
    def cget(self,*args,**keys):

        return None
        # val = self.bodyCtrl.cget(*args,**keys)
        # return val

    def configure (self,*args,**keys):

        pass
        # return self.bodyCtrl.configure(*args,**keys)
    #@-node:ekr.20081004172422.514:Configuration (Qt spelling) (qtBody)
    #@+node:ekr.20081004172422.515:Height & width
    def getBodyPaneHeight (self):

        # return self.bodyCtrl.winfo_height()
        return 0

    def getBodyPaneWidth (self):

        # return self.bodyCtrl.winfo_width()
        return 0
    #@-node:ekr.20081004172422.515:Height & width
    #@+node:ekr.20081004172422.516:Idle time...
    def scheduleIdleTimeRoutine (self,function,*args,**keys):

        pass
        # if not g.app.unitTesting:
            # self.bodyCtrl.after_idle(function,*args,**keys)
    #@-node:ekr.20081004172422.516:Idle time...
    #@+node:ekr.20081004172422.517:Menus (qtBody) (May cause problems)
    def bind (self,*args,**keys):

        pass
        # g.trace(args,keys)
        # c = self.c
        # return self.bodyCtrl.bind(*args,**keys)
    #@-node:ekr.20081004172422.517:Menus (qtBody) (May cause problems)
    #@+node:ekr.20081004172422.518:Text (now in base class)
    # def getAllText (self):              return self.bodyCtrl.getAllText()
    # def getInsertPoint(self):           return self.bodyCtrl.getInsertPoint()
    # def getSelectedText (self):         return self.bodyCtrl.getSelectedText()
    # def getSelectionRange (self,sort=True): return self.bodyCtrl.getSelectionRange(sort)
    # def hasTextSelection (self):        return self.bodyCtrl.hasSelection()
    # # def scrollDown (self):            g.app.gui.yscroll(self.bodyCtrl,1,'units')
    # # def scrollUp (self):              g.app.gui.yscroll(self.bodyCtrl,-1,'units')
    # def see (self,index):               self.bodyCtrl.see(index)
    # def seeInsertPoint (self):          self.bodyCtrl.seeInsertPoint()
    # def selectAllText (self,event=None):
        # w = g.app.gui.eventWidget(event) or self.bodyCtrl
        # return w.selectAllText()
    # def setInsertPoint (self,pos):      return self.bodyCtrl.getInsertPoint(pos)
    # def setSelectionRange (self,sel):
        # i,j = sel
        # self.bodyCtrl.setSelectionRange(i,j)
    #@nonl
    #@-node:ekr.20081004172422.518:Text (now in base class)
    #@-node:ekr.20081004172422.512:Qt bindings (qtBody) (TO DO)
    #@+node:ekr.20081004172422.519:Editors (qtBody) (TO DO)
    #@+node:ekr.20081004172422.520:createEditorFrame
    def createEditorFrame (self,pane):

        f = qt.Frame(pane)
        f.pack(side='top',expand=1,fill='both')
        return f
    #@-node:ekr.20081004172422.520:createEditorFrame
    #@+node:ekr.20081004172422.521:packEditorLabelWidget
    def packEditorLabelWidget (self,w):

        '''Create a Qt label widget.'''

        if not hasattr(w,'leo_label') or not w.leo_label:
            # g.trace('w.leo_frame',id(w.leo_frame))
            w.pack_forget()
            w.leo_label = Qt.Label(w.leo_frame)
            w.leo_label.pack(side='top')
            w.pack(expand=1,fill='both')
    #@nonl
    #@-node:ekr.20081004172422.521:packEditorLabelWidget
    #@+node:ekr.20081004172422.522:setEditorColors
    def setEditorColors (self,bg,fg):

        c = self.c ; d = self.editorWidgets

        for key in d:
            w2 = d.get(key)
            # g.trace(id(w2),bg,fg)
            try:
                w2.configure(bg=bg,fg=fg)
            except Exception:
                g.es_exception()
    #@-node:ekr.20081004172422.522:setEditorColors
    #@-node:ekr.20081004172422.519:Editors (qtBody) (TO DO)
    #@-others
#@-node:ekr.20081004172422.502:class leoQtBody (leoBody) (not used yet)
#@+node:ekr.20081004102201.628:class leoQtEventFilter
class leoQtEventFilter(QtCore.QObject):

    def __init__(self):
        QtCore.QObject.__init__(self)
        self.bindings = {}

    def eventFilter(self, obj, event):

        if event.type() == QtCore.QEvent.KeyPress:
            return self.key_pressed(obj, event)
        else:
            return False

    #@    @+others
    #@+node:ekr.20081004172422.897:key_pressed
    def key_pressed(self, obj, event):
        """ Handle key presses (on any window) """

        trace = True ; verbose = False

        keynum = event.key()
        try:
            char = chr(keynum)
        except ValueError:
            char = "<unknown>"

        mods = []
        if event.modifiers() & QtCore.Qt.AltModifier:
            mods.append("Alt")
        if event.modifiers() & QtCore.Qt.ControlModifier:
            mods.append("Ctrl")
        if event.modifiers() & QtCore.Qt.ShiftModifier:
            mods.append("Shift")
        txt = "+".join(mods) + (mods and "+" or "") + char

        if trace:
            print "Keypress: [%s]" % (txt)
            # print , event.text(),obj, event.key(), event.modifiers()

        # key was not consumed
        cmd = self.bindings.get(txt, None)
        if cmd: cmd()
        return cmd is not None
    #@-node:ekr.20081004172422.897:key_pressed
    #@-others
#@-node:ekr.20081004102201.628:class leoQtEventFilter
#@+node:ekr.20081004172422.523:class leoQtFrame (c.frame.top is a Window object)
class leoQtFrame (leoFrame.leoFrame):

    """A class that represents a Leo window rendered in qt."""

    #@    @+others
    #@+node:ekr.20081004172422.524: Birth & Death (qtFrame)
    #@+node:ekr.20081004172422.525:__init__ (qtFrame)
    def __init__(self,title,gui):

        # Init the base class.
        leoFrame.leoFrame.__init__(self,gui)

        self.title = title

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
    #@-node:ekr.20081004172422.525:__init__ (qtFrame)
    #@+node:ekr.20081004172422.527:__repr__ (qtFrame)
    def __repr__ (self):

        return "<leoQtFrame: %s>" % self.title
    #@-node:ekr.20081004172422.527:__repr__ (qtFrame)
    #@+node:ekr.20081004172422.537:f.setCanvasColorFromConfig
    def setCanvasColorFromConfig (self,canvas):

        g.trace(canvas)
        return ###

        c = self.c

        bg = c.config.getColor("outline_pane_background_color") or 'white'

        try:
            canvas.configure(bg=bg)
        except:
            g.es("exception setting outline pane background color")
            g.es_exception()
    #@-node:ekr.20081004172422.537:f.setCanvasColorFromConfig
    #@+node:ekr.20081004172422.528:qtFrame.finishCreate & helpers
    def finishCreate (self,c):

        f = self ; f.c = c

        self.bigTree           = c.config.getBool('big_outline_pane')
        self.trace_status_line = c.config.getBool('trace_status_line')
        self.use_chapters      = c.config.getBool('use_chapters')
        self.use_chapter_tabs  = c.config.getBool('use_chapter_tabs')

        f.top = Window(c)
        f.top.show()

        # This must be done after creating the commander.
        f.splitVerticalFlag,f.ratio,f.secondary_ratio = f.initialRatios()
        # # f.createOuterFrames()
        # # f.createIconBar()
        # # f.createLeoSplitters(f.outerFrame)
        f.createSplitterComponents()
        # # f.createStatusLine()
        # # f.createFirstTreeNode()
        f.menu = leoQtMenu(f)
        c.setLog()
        g.app.windowList.append(f)
        c.initVersion()
        c.signOnWithVersion()
        f.miniBufferWidget = f.createMiniBufferWidget()
        c.bodyWantsFocusNow()
    #@+node:ekr.20081004172422.530:createSplitterComponents (qtFrame)
    def createSplitterComponents (self):

        f = self ; c = f.c

        f.tree  = leoQtTree(c,f)
        f.log   = leoQtLog(f,None)
        ###  Use base class components
        # f.log   = leoFrame.leoQtLog(f,None)
        f.body  = leoFrame.leoBody(f,None)

        return ###

        # Create the canvas, tree, log and body.
        if f.use_chapters:
            c.chapterController = cc = leoChapters.chapterController(c)

        # split1.pane1 is the secondary splitter.

        if self.bigTree: # Put outline in the main splitter.
            if self.use_chapters and self.use_chapter_tabs:
                cc.tt = leoQtTreeTab(c,f.split1Pane2,cc)
            f.canvas = f.createCanvas(f.split1Pane1)
            f.tree  = leoQtTree(c,f,f.canvas)
            f.log   = leoQtLog(f,f.split2Pane2)
            f.body  = leoQtBody(f,f.split2Pane1)
        else:
            if self.use_chapters and self.use_chapter_tabs:
                cc.tt = leoQtTreeTab(c,f.split2Pane1,cc)
            f.canvas = f.createCanvas(f.split2Pane1)
            f.tree   = leoQtTree(c,f,f.canvas)
            f.log    = leoQtLog(f,f.split2Pane2)
            f.body   = leoQtBody(f,f.split1Pane2)

        # Yes, this an "official" ivar: this is a kludge.
        # f.bodyCtrl = f.body.bodyCtrl

        # Configure.
        f.setTabWidth(c.tab_width)
        f.reconfigurePanes()
        f.body.setFontFromConfig()
        f.body.setColorFromConfig()
    #@-node:ekr.20081004172422.530:createSplitterComponents (qtFrame)
    #@-node:ekr.20081004172422.528:qtFrame.finishCreate & helpers
    #@+node:ekr.20081004172422.545:Destroying the qtFrame
    #@+node:ekr.20081004172422.546:destroyAllObjects
    def destroyAllObjects (self):

        """Clear all links to objects in a Leo window."""

        frame = self ; c = self.c ; tree = frame.tree ; body = self.body

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
        g.clearAllIvars(body.colorizer)
        g.clearAllIvars(body)
        g.clearAllIvars(tree)

        # This must be done last.
        frame.destroyAllPanels()
        g.clearAllIvars(frame)

    #@-node:ekr.20081004172422.546:destroyAllObjects
    #@+node:ekr.20081004172422.548:destroyAllPanels
    def destroyAllPanels (self):

        """Destroy all panels attached to this frame."""

        panels = (self.comparePanel, self.colorPanel, self.findPanel, self.fontPanel, self.prefsPanel)

        for panel in panels:
            if panel:
                panel.top.destroy()
    #@-node:ekr.20081004172422.548:destroyAllPanels
    #@+node:ekr.20081004172422.549:destroySelf (qtFrame)
    def destroySelf (self):

        # Remember these: we are about to destroy all of our ivars!
        c,top = self.c,self.top 

        # Indicate that the commander is no longer valid.
        c.exists = False

        # Important: this destroys all the objects of the commander too.
        if 0:
            self.destroyAllObjects()

        c.exists = False # Make sure this one ivar has not been destroyed.

        top.destroy()
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
            self.colorTags = [] # list of color names used as tags.
            self.enabled = False
            self.isVisible = False
            self.lastRow = self.lastCol = 0
            self.log = c.frame.log

            return ###

            #if 'black' not in self.log.colorTags:
            #    self.log.colorTags.append("black")
            self.parentFrame = parentFrame
            self.statusFrame = qt.Frame(parentFrame,bd=2)
            text = "line 0, col 0, fcol 0"
            width = len(text) + 4
            self.labelWidget = qt.Label(self.statusFrame,text=text,width=width,anchor="w")
            self.labelWidget.pack(side="left",padx=1)

            bg = self.statusFrame.cget("background")
            self.textWidget = w = g.app.gui.bodyTextWidget(
                self.statusFrame,
                height=1,state="disabled",bg=bg,relief="groove",name='status-line')
            self.textWidget.pack(side="left",expand=1,fill="x")
            c.bind(w,"<Button-1>", self.onActivate)
            self.show()

            c.frame.statusFrame = self.statusFrame
            c.frame.statusLabel = self.labelWidget
            c.frame.statusText  = self.textWidget
        #@-node:ekr.20081004172422.551:ctor
        #@+node:ekr.20081004172422.552:clear
        def clear (self):

            w = self.textWidget
            if not w: return

            w.configure(state="normal")
            w.delete(0,"end")
            w.configure(state="disabled")
        #@-node:ekr.20081004172422.552:clear
        #@+node:ekr.20081004172422.553:enable, disable & isEnabled
        def disable (self,background=None):

            c = self.c ; w = self.textWidget
            if w:
                if not background:
                    background = self.statusFrame.cget("background")
                w.configure(state="disabled",background=background)
            self.enabled = False
            c.bodyWantsFocus()

        def enable (self,background="white"):

            # g.trace()
            c = self.c ; w = self.textWidget
            if w:
                w.configure(state="normal",background=background)
                c.widgetWantsFocus(w)
            self.enabled = True

        def isEnabled(self):
            return self.enabled
        #@nonl
        #@-node:ekr.20081004172422.553:enable, disable & isEnabled
        #@+node:ekr.20081004172422.554:get
        def get (self):

            w = self.textWidget
            if w:
                return w.getAllText()
            else:
                return ""
        #@-node:ekr.20081004172422.554:get
        #@+node:ekr.20081004172422.555:getFrame
        def getFrame (self):

            return self.statusFrame
        #@-node:ekr.20081004172422.555:getFrame
        #@+node:ekr.20081004172422.556:onActivate
        def onActivate (self,event=None):

            # Don't change background as the result of simple mouse clicks.
            background = self.statusFrame.cget("background")
            self.enable(background=background)
        #@-node:ekr.20081004172422.556:onActivate
        #@+node:ekr.20081004172422.557:pack & show
        def pack (self):

            if not self.isVisible:
                self.isVisible = True
                self.statusFrame.pack(fill="x",pady=1)

        show = pack
        #@-node:ekr.20081004172422.557:pack & show
        #@+node:ekr.20081004172422.558:put (leoQtFrame:statusLineClass)
        def put(self,s,color=None):

            # g.trace('qtStatusLine',self.textWidget,s)

            w = self.textWidget
            if not w:
                g.trace('qtStatusLine','***** disabled')
                return

            w.configure(state="normal")
            w.insert("end",s)

            if color:
                if color not in self.colorTags:
                    self.colorTags.append(color)
                    w.tag_config(color,foreground=color)
                w.tag_add(color,"end-%dc" % (len(s)+1),"end-1c")
                w.tag_config("black",foreground="black")
                w.tag_add("black","end")

            w.configure(state="disabled")
        #@-node:ekr.20081004172422.558:put (leoQtFrame:statusLineClass)
        #@+node:ekr.20081004172422.559:setBindings (qtStatusLine)
        def setBindings (self):

            return ###

            c = self.c ; k = c.keyHandler ; w = self.textWidget

            c.bind(w,'<Key>',k.masterKeyHandler)

            k.completeAllBindingsForWidget(w)
        #@-node:ekr.20081004172422.559:setBindings (qtStatusLine)
        #@+node:ekr.20081004172422.560:unpack & hide
        def unpack (self):

            if self.isVisible:
                self.isVisible = False
                self.statusFrame.pack_forget()

        hide = unpack
        #@-node:ekr.20081004172422.560:unpack & hide
        #@+node:ekr.20081004172422.561:update (statusLine)
        def update (self):

            c = self.c ; bodyCtrl = c.frame.body.bodyCtrl

            if g.app.killed or not self.isVisible:
                return

            s = bodyCtrl.getAllText()    
            index = bodyCtrl.getInsertPoint()
            row,col = g.convertPythonIndexToRowCol(s,index)
            if col > 0:
                s2 = s[index-col:index]
                s2 = g.toUnicode(s2,g.app.tkEncoding)
                col = g.computeWidth (s2,c.tab_width)
            p = c.currentPosition()
            fcol = col + p.textOffset()

            # Important: this does not change the focus because labels never get focus.
            self.labelWidget.configure(text="line %d, col %d, fcol %d" % (row,col,fcol))
            self.lastRow = row
            self.lastCol = col
            self.lastFcol = fcol
        #@-node:ekr.20081004172422.561:update (statusLine)
        #@-others
    #@-node:ekr.20081004172422.550:class qtStatusLineClass (qtFrame)
    #@+node:ekr.20081004172422.562:class qtIconBarClass
    class qtIconBarClass:

        '''A class representing the singleton Icon bar'''

        #@    @+others
        #@+node:ekr.20081004172422.563: ctor
        def __init__ (self,c,parentFrame):

            self.c = c


            self.buttons = {}

            # Create a parent frame that will never be unpacked.
            # This allows us to pack and unpack the container frame without it moving.
            self.iconFrameParentFrame = None ### qt.Frame(parentFrame)
            ### self.iconFrameParentFrame.pack(fill="x",pady=0)

            # Create a container frame to hold individual row frames.
            # We hide all icons by doing pack_forget on this one frame.
            self.iconFrameContainerFrame = None ### qt.Frame(self.iconFrameParentFrame)
                # Packed in self.show()

            self.addRow()
            self.font = None
            self.parentFrame = parentFrame
            self.visible = False
            self.widgets_per_row = c.config.getInt('icon_bar_widgets_per_row') or 10
            self.show() # pack the container frame.
        #@-node:ekr.20081004172422.563: ctor
        #@+node:ekr.20081004172422.564:add
        def add(self,*args,**keys):

            """Add a button containing text or a picture to the icon bar.

            Pictures take precedence over text"""

            c = self.c
            text = keys.get('text')
            imagefile = keys.get('imagefile')
            image = keys.get('image')
            command = keys.get('command')
            bg = keys.get('bg')

            if not imagefile and not image and not text: return

            self.addRowIfNeeded()
            f = self.iconFrame # Bind this after possibly creating a new row.

            if command:
                def commandCallBack(c=c,command=command):
                    val = command()
                    if c.exists:
                        c.bodyWantsFocus()
                        c.outerUpdate()
                    return val
            else:
                def commandCallback(n=g.app.iconWidgetCount):
                    g.pr("command for widget %s" % (n))
                command = commandCallback

            if imagefile or image:
                #@        << create a picture >>
                #@+node:ekr.20081004172422.565:<< create a picture >>
                try:
                    if imagefile:
                        # Create the image.  Throws an exception if file not found
                        imagefile = g.os_path_join(g.app.loadDir,imagefile)
                        imagefile = g.os_path_normpath(imagefile)
                        image = qt.PhotoImage(master=g.app.root,file=imagefile)
                        g.trace(image,imagefile)

                        # Must keep a reference to the image!
                        try:
                            refs = g.app.iconImageRefs
                        except:
                            refs = g.app.iconImageRefs = []

                        refs.append((imagefile,image),)

                    if not bg:
                        bg = f.cget("bg")

                    try:
                        b = qt.Button(f,image=image,relief="flat",bd=0,command=command,bg=bg)
                    except Exception:
                        g.es_print('image does not exist',image,color='blue')
                        b = qt.Button(f,relief='flat',bd=0,command=command,bg=bg)
                    b.pack(side="left",fill="y")
                    return b

                except:
                    g.es_exception()
                    return None
                #@-node:ekr.20081004172422.565:<< create a picture >>
                #@nl
            elif text:
                b = qt.Button(f,text=text,relief="groove",bd=2,command=command)
                if not self.font:
                    self.font = c.config.getFontFromParams(
                        "button_text_font_family", "button_text_font_size",
                        "button_text_font_slant",  "button_text_font_weight",)
                b.configure(font=self.font)
                if bg: b.configure(bg=bg)
                b.pack(side="left", fill="none")
                return b

            return None
        #@-node:ekr.20081004172422.564:add
        #@+node:ekr.20081004172422.566:addRow
        def addRow(self,height=None):

            if height is None:
                height = '5m'

            ### w = qt.Frame(self.iconFrameContainerFrame,height=height,bd=2,relief="groove")
            ### w.pack(fill="x",pady=2)
            w = None ###
            self.iconFrame = w
            self.c.frame.iconFrame = w
            return w
        #@-node:ekr.20081004172422.566:addRow
        #@+node:ekr.20081004172422.567:addRowIfNeeded
        def addRowIfNeeded (self):

            '''Add a new icon row if there are too many widgets.'''

            try:
                n = g.app.iconWidgetCount
            except:
                n = g.app.iconWidgetCount = 0

            if n >= self.widgets_per_row:
                g.app.iconWidgetCount = 0
                self.addRow()

            g.app.iconWidgetCount += 1
        #@-node:ekr.20081004172422.567:addRowIfNeeded
        #@+node:ekr.20081004172422.568:addWidget
        def addWidget (self,w):

            self.addRowIfNeeded()
            w.pack(side="left", fill="none")


        #@-node:ekr.20081004172422.568:addWidget
        #@+node:ekr.20081004172422.569:clear
        def clear(self):

            """Destroy all the widgets in the icon bar"""

            f = self.iconFrameContainerFrame

            for slave in f.pack_slaves():
                slave.pack_forget()
            f.pack_forget()

            self.addRow(height='0m')

            self.visible = False

            g.app.iconWidgetCount = 0
            g.app.iconImageRefs = []
        #@-node:ekr.20081004172422.569:clear
        #@+node:ekr.20081004172422.570:deleteButton (new in Leo 4.4.3)
        def deleteButton (self,w):

            w.pack_forget()
            self.c.bodyWantsFocus()
            self.c.outerUpdate()
        #@-node:ekr.20081004172422.570:deleteButton (new in Leo 4.4.3)
        #@+node:ekr.20081004172422.571:getFrame & getNewFrame
        def getFrame (self):

            return self.iconFrame

        def getNewFrame (self):

            return None ###

            # Pre-check that there is room in the row, but don't bump the count.
            self.addRowIfNeeded()
            g.app.iconWidgetCount -= 1

            # Allocate the frame in the possibly new row.
            frame = qt.Frame(self.iconFrame)
            return frame

        #@-node:ekr.20081004172422.571:getFrame & getNewFrame
        #@+node:ekr.20081004172422.572:pack (show)
        def pack (self):

            """Show the icon bar by repacking it"""

            # if not self.visible:
                # self.visible = True
                # self.iconFrameContainerFrame.pack(fill='x',pady=2)

        show = pack
        #@-node:ekr.20081004172422.572:pack (show)
        #@+node:ekr.20081004172422.573:setCommandForButton (new in Leo 4.4.3)
        def setCommandForButton(self,b,command):

            b.configure(command=command)
        #@-node:ekr.20081004172422.573:setCommandForButton (new in Leo 4.4.3)
        #@+node:ekr.20081004172422.574:unpack (hide)
        def unpack (self):

            """Hide the icon bar by unpacking it."""

            # if self.visible:
                # self.visible = False
                # w = self.iconFrameContainerFrame
                # w.pack_forget()

        hide = unpack
        #@-node:ekr.20081004172422.574:unpack (hide)
        #@-others
    #@-node:ekr.20081004172422.562:class qtIconBarClass
    #@+node:ekr.20081004172422.575:Minibuffer methods
    #@+node:ekr.20081004172422.576:showMinibuffer
    def showMinibuffer (self):

        '''Make the minibuffer visible.'''

        frame = self

        if not frame.minibufferVisible:
            frame.minibufferFrame.pack(side='bottom',fill='x')
            frame.minibufferVisible = True
    #@-node:ekr.20081004172422.576:showMinibuffer
    #@+node:ekr.20081004172422.577:hideMinibuffer
    def hideMinibuffer (self):

        '''Hide the minibuffer.'''

        frame = self
        if frame.minibufferVisible:
            frame.minibufferFrame.pack_forget()
            frame.minibufferVisible = False
    #@-node:ekr.20081004172422.577:hideMinibuffer
    #@+node:ekr.20081004172422.578:f.createMiniBufferWidget
    def createMiniBufferWidget (self):

        '''Create the minbuffer below the status line.'''

        frame = self ; c = frame.c

        return None ###

        frame.minibufferFrame = f = qt.Frame(frame.outerFrame,relief='flat',borderwidth=0)
        if c.showMinibuffer:
            f.pack(side='bottom',fill='x')

        lab = qt.Label(f,text='mini-buffer',justify='left',anchor='nw',foreground='blue')
        lab.pack(side='left')

        label = g.app.gui.plainTextWidget(
            f,height=1,relief='groove',background='lightgrey',name='minibuffer')
        label.pack(side='left',fill='x',expand=1,padx=2,pady=1)

        frame.minibufferVisible = c.showMinibuffer

        return label
    #@-node:ekr.20081004172422.578:f.createMiniBufferWidget
    #@+node:ekr.20081004172422.579:f.setMinibufferBindings
    def setMinibufferBindings (self):

        '''Create bindings for the minibuffer..'''

        return ###

        f = self ; c = f.c ; k = c.k ; w = f.miniBufferWidget

        table = [
            ('<Key>',           k.masterKeyHandler),
            ('<Button-1>',      k.masterClickHandler),
            ('<Button-3>',      k.masterClick3Handler),
            ('<Double-1>',      k.masterDoubleClickHandler),
            ('<Double-3>',      k.masterDoubleClick3Handler),
        ]

        table2 = (
            ('<Button-2>',      k.masterClickHandler),
        )

        if c.config.getBool('allow_middle_button_paste'):
            table.extend(table2)

        for kind,callback in table:
            c.bind(w,kind,callback)

        if 0:
            if sys.platform.startswith('win'):
                # Support Linux middle-button paste easter egg.
                c.bind(w,"<Button-2>",f.OnPaste)
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

        return ###

        try: # This can fail when called from scripts
            # Use the present font for computations.
            font = self.body.bodyCtrl.cget("font") # 2007/10/27
            root = g.app.root # 4/3/03: must specify root so idle window will work properly.
            font = tkFont.Font(root=root,font=font)
            tabw = font.measure(" " * abs(w)) # 7/2/02
            self.body.bodyCtrl.configure(tabs=tabw)
            self.tab_width = w
            # g.trace(w,tabw)
        except:
            g.es_exception()
    #@-node:ekr.20081004172422.585:setTabWidth (qtFrame)
    #@+node:ekr.20081004172422.586:setWrap (qtFrame)
    def setWrap (self,p):

        c = self.c
        theDict = c.scanAllDirectives(p)
        if not theDict: return

        return ###

        wrap = theDict.get("wrap")
        if self.body.wrapState == wrap: return

        self.body.wrapState = wrap
        w = self.body.bodyCtrl

        # g.trace(wrap)
        if wrap:
            w.configure(wrap="word") # 2007/10/25
            w.leo_bodyXBar.pack_forget() # 2007/10/31
        else:
            w.configure(wrap="none")
            # Bug fix: 3/10/05: We must unpack the text area to make the scrollbar visible.
            w.pack_forget()  # 2007/10/25
            w.leo_bodyXBar.pack(side="bottom", fill="x") # 2007/10/31
            w.pack(expand=1,fill="both")  # 2007/10/25
    #@-node:ekr.20081004172422.586:setWrap (qtFrame)
    #@+node:ekr.20081004172422.587:setTopGeometry (qtFrame)
    def setTopGeometry(self,w,h,x,y,adjustSize=True):

        return ###

        # Put the top-left corner on the screen.
        x = max(10,x) ; y = max(10,y)

        if adjustSize:
            top = self.top
            sw = top.winfo_screenwidth()
            sh = top.winfo_screenheight()

            # Adjust the size so the whole window fits on the screen.
            w = min(sw-10,w)
            h = min(sh-10,h)

            # Adjust position so the whole window fits on the screen.
            if x + w > sw: x = 10
            if y + h > sh: y = 10

        geom = "%dx%d%+d%+d" % (w,h,x,y)

        self.top.geometry(geom)
    #@-node:ekr.20081004172422.587:setTopGeometry (qtFrame)
    #@+node:ekr.20081004172422.588:reconfigurePanes (use config bar_width) (qtFrame)
    def reconfigurePanes (self):

        return ###

        c = self.c

        border = c.config.getInt('additional_body_text_border')
        if border == None: border = 0

        # The body pane needs a _much_ bigger border when tiling horizontally.
        border = g.choose(self.splitVerticalFlag,2+border,6+border)
        self.body.bodyCtrl.configure(bd=border) # 2007/10/25

        # The log pane needs a slightly bigger border when tiling vertically.
        border = g.choose(self.splitVerticalFlag,4,2) 
        self.log.configureBorder(border)
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

        try:
            frame = self ; c = frame.c
            c.setLog()
            w = c.get_focus()
            if w != c.frame.body.bodyCtrl:
                frame.tree.OnDeactivate()
            c.bodyWantsFocusNow()
        except:
            g.es_event_exception("activate body")

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
    #@+node:ekr.20081004172422.598:OnMouseWheel (Tomaz Ficko)
    # Contributed by Tomaz Ficko.  This works on some systems.
    # On XP it causes a crash in tcl83.dll.  Clearly a qt bug.

    def OnMouseWheel(self, event=None):

        try:
            if event.delta < 1:
                self.canvas.yview(qt.SCROLL, 1, qt.UNITS)
            else:
                self.canvas.yview(qt.SCROLL, -1, qt.UNITS)
        except:
            g.es_event_exception("scroll wheel")

        return "break"
    #@-node:ekr.20081004172422.598:OnMouseWheel (Tomaz Ficko)
    #@-node:ekr.20081004172422.590:Event handlers (qtFrame)
    #@+node:ekr.20081004172422.599:Gui-dependent commands
    #@+node:ekr.20081004172422.600:Minibuffer commands... (qtFrame)

    #@+node:ekr.20081004172422.601:contractPane
    def contractPane (self,event=None):

        '''Contract the selected pane.'''

        f = self ; c = f.c
        w = c.get_requested_focus()
        wname = c.widget_name(w)

        # g.trace(wname)
        if not w: return

        if wname.startswith('body'):
            f.contractBodyPane()
        elif wname.startswith('log'):
            f.contractLogPane()
        elif wname.startswith('head') or wname.startswith('canvas'):
            f.contractOutlinePane()
    #@-node:ekr.20081004172422.601:contractPane
    #@+node:ekr.20081004172422.602:expandPane
    def expandPane (self,event=None):

        '''Expand the selected pane.'''

        f = self ; c = f.c

        w = c.get_requested_focus()
        wname = c.widget_name(w)

        # g.trace(wname)
        if not w: return

        if wname.startswith('body'):
            f.expandBodyPane()
        elif wname.startswith('log'):
            f.expandLogPane()
        elif wname.startswith('head') or wname.startswith('canvas'):
            f.expandOutlinePane()
    #@-node:ekr.20081004172422.602:expandPane
    #@+node:ekr.20081004172422.603:fullyExpandPane
    def fullyExpandPane (self,event=None):

        '''Fully expand the selected pane.'''

        f = self ; c = f.c

        w = c.get_requested_focus()
        wname = c.widget_name(w)

        # g.trace(wname)
        if not w: return

        if wname.startswith('body'):
            f.fullyExpandBodyPane()
        elif wname.startswith('log'):
            f.fullyExpandLogPane()
        elif wname.startswith('head') or wname.startswith('canvas'):
            f.fullyExpandOutlinePane()
    #@-node:ekr.20081004172422.603:fullyExpandPane
    #@+node:ekr.20081004172422.604:hidePane
    def hidePane (self,event=None):

        '''Completely contract the selected pane.'''

        f = self ; c = f.c

        w = c.get_requested_focus()
        wname = c.widget_name(w)

        g.trace(wname)
        if not w: return

        if wname.startswith('body'):
            f.hideBodyPane()
            c.treeWantsFocusNow()
        elif wname.startswith('log'):
            f.hideLogPane()
            c.bodyWantsFocusNow()
        elif wname.startswith('head') or wname.startswith('canvas'):
            f.hideOutlinePane()
            c.bodyWantsFocusNow()
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
        f = self ; r = min(1.0,f.ratio+0.1)
        f.divideLeoSplitter(f.splitVerticalFlag,r)

    def contractLogPane (self,event=None):
        '''Contract the log pane.'''
        f = self ; r = min(1.0,f.ratio+0.1)
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
        f = self ; r = max(0.0,f.ratio-0.1)
        f.divideLeoSplitter(not f.splitVerticalFlag,r)

    def expandOutlinePane (self,event=None):
        '''Expand the outline pane.'''
        self.contractBodyPane()
    #@-node:ekr.20081004172422.605:expand/contract/hide...Pane
    #@+node:ekr.20081004172422.606:fullyExpand/hide...Pane
    def fullyExpandBodyPane (self,event=None):
        '''Fully expand the body pane.'''
        f = self ; f.divideLeoSplitter(f.splitVerticalFlag,0.0)

    def fullyExpandLogPane (self,event=None):
        '''Fully expand the log pane.'''
        f = self ; f.divideLeoSplitter(not f.splitVerticalFlag,0.0)

    def fullyExpandOutlinePane (self,event=None):
        '''Fully expand the outline pane.'''
        f = self ; f.divideLeoSplitter(f.splitVerticalFlag,1.0)

    def hideBodyPane (self,event=None):
        '''Completely contract the body pane.'''
        f = self ; f.divideLeoSplitter(f.splitVerticalFlag,1.0)

    def hideLogPane (self,event=None):
        '''Completely contract the log pane.'''
        f = self ; f.divideLeoSplitter(not f.splitVerticalFlag,1.0)

    def hideOutlinePane (self,event=None):
        '''Completely contract the outline pane.'''
        f = self ; f.divideLeoSplitter(f.splitVerticalFlag,0.0)
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

        x,y,delta = 10,10,10
        for frame in g.app.windowList:
            top = frame.top

            # Compute w,h
            top.update_idletasks() # Required to get proper info.
            geom = top.geometry() # geom = "WidthxHeight+XOffset+YOffset"
            dim,junkx,junky = geom.split('+')
            w,h = dim.split('x')
            w,h = int(w),int(h)

            # Set new x,y and old w,h
            frame.setTopGeometry(w,h,x,y,adjustSize=False)

            # Compute the new offsets.
            x += 30 ; y += 30
            if x > 200:
                x = 10 + delta ; y = 40 + delta
                delta += 10
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
        frame.divideLeoSplitter2(0.99, not frame.splitVerticalFlag)
    #@-node:ekr.20081004172422.611:hideLogWindow
    #@+node:ekr.20081004172422.612:minimizeAll
    def minimizeAll (self,event=None):

        '''Minimize all Leo's windows.'''

        self.minimize(g.app.pythonFrame)
        for frame in g.app.windowList:
            self.minimize(frame)
            self.minimize(frame.findPanel)

    def minimize(self,frame):

        if frame and frame.top.state() == "normal":
            frame.top.iconify()
    #@-node:ekr.20081004172422.612:minimizeAll
    #@+node:ekr.20081004172422.613:toggleSplitDirection (qtFrame)
    # The key invariant: self.splitVerticalFlag tells the alignment of the main splitter.

    def toggleSplitDirection (self,event=None):

        '''Toggle the split direction in the present Leo window.'''

        # Switch directions.
        c = self.c
        self.splitVerticalFlag = not self.splitVerticalFlag
        orientation = g.choose(self.splitVerticalFlag,"vertical","horizontal")
        c.config.set("initial_splitter_orientation","string",orientation)

        self.toggleQtSplitDirection(self.splitVerticalFlag)
    #@+node:ekr.20081004172422.614:toggleQtSplitDirection
    def toggleQtSplitDirection (self,verticalFlag):

        # Abbreviations.
        frame = self
        bar1 = self.bar1 ; bar2 = self.bar2
        split1Pane1,split1Pane2 = self.split1Pane1,self.split1Pane2
        split2Pane1,split2Pane2 = self.split2Pane1,self.split2Pane2
        # Reconfigure the bars.
        bar1.place_forget()
        bar2.place_forget()
        self.configureBar(bar1,verticalFlag)
        self.configureBar(bar2,not verticalFlag)
        # Make the initial placements again.
        self.placeSplitter(bar1,split1Pane1,split1Pane2,verticalFlag)
        self.placeSplitter(bar2,split2Pane1,split2Pane2,not verticalFlag)
        # Adjust the log and body panes to give more room around the bars.
        self.reconfigurePanes()
        # Redraw with an appropriate ratio.
        vflag,ratio,secondary_ratio = frame.initialRatios()
        self.resizePanesToRatio(ratio,secondary_ratio)
    #@-node:ekr.20081004172422.614:toggleQtSplitDirection
    #@-node:ekr.20081004172422.613:toggleSplitDirection (qtFrame)
    #@+node:ekr.20081004172422.615:resizeToScreen
    def resizeToScreen (self,event=None):

        '''Resize the Leo window so it fill the entire screen.'''

        top = self.top

        w = top.winfo_screenwidth()
        h = top.winfo_screenheight()

        if sys.platform.startswith('win'):
            top.state('zoomed')
        elif sys.platform == 'darwin':
            # Must leave room to get at very small resizing area.
            geom = "%dx%d%+d%+d" % (w-20,h-55,10,25)
            top.geometry(geom)
        else:
            # Fill almost the entire screen.
            # Works on Windows. YMMV for other platforms.
            geom = "%dx%d%+d%+d" % (w-8,h-46,0,0)
            top.geometry(geom)
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
            #@        << create the scale widget >>
            #@+node:ekr.20081004172422.619:<< create the scale widget >>
            top = qt.Toplevel()
            top.title("Download progress")
            self.scale = scale = qt.Scale(top,state="normal",orient="horizontal",from_=0,to=total)
            scale.pack()
            top.lift()
            #@-node:ekr.20081004172422.619:<< create the scale widget >>
            #@nl
        self.scale.set(count*size)
        self.scale.update_idletasks()
    #@-node:ekr.20081004172422.618:showProgressBar
    #@-node:ekr.20081004172422.617:leoHelp
    #@-node:ekr.20081004172422.616:Help Menu...
    #@-node:ekr.20081004172422.599:Gui-dependent commands
    #@+node:ekr.20081004172422.620:Delayed Focus (qtFrame)
    #@+at 
    #@nonl
    # New in 4.3. The proper way to change focus is to call 
    # c.frame.xWantsFocus.
    # 
    # Important: This code never calls select, so there can be no race 
    # condition here
    # that alters text improperly.
    #@-at
    #@-node:ekr.20081004172422.620:Delayed Focus (qtFrame)
    #@+node:ekr.20081004172422.621:Qt bindings... (qtFrame)
    def bringToFront (self):
        # g.trace(g.callers())
        self.top.deiconify()
        self.top.lift()

    def getFocus(self):
        """Returns the widget that has focus, or body if None."""
        try:
            # This method is unreliable while focus is changing.
            # The call to update_idletasks may help.  Or not.
            self.top.update_idletasks()
            f = self.top.focus_displayof()
        except Exception:
            f = None
        if f:
            return f
        else:
            return self.body.bodyCtrl # 2007/10/25

    def getTitle (self):
        return '<frame title>'
        ### return self.top.title()

    def setTitle (self,title):
        return '<frame title>'
        ### return self.top.title(title)

    def get_window_info(self):
        return 0,0,0,0
        ### return g.app.gui.get_window_info(self.top)

    def iconify(self):
        pass
        ### self.top.iconify()

    def deiconify (self):
        pass
        ### self.top.deiconify()

    def lift (self):
        pass
        ### self.top.lift()

    def update (self):
        pass
        ### self.top.update()
    #@-node:ekr.20081004172422.621:Qt bindings... (qtFrame)
    #@-others
#@-node:ekr.20081004172422.523:class leoQtFrame (c.frame.top is a Window object)
#@+node:ekr.20081004102201.631:class leoQtGui
class leoQtGui(leoGui.leoGui):

    '''A class implementing Leo's Qt gui.'''

    #@    @+others
    #@+node:ekr.20081004102201.632:qtGui birth & death
    #@+node:ekr.20081004102201.633: qtGui.__init__
    def __init__ (self):

        # Initialize the base class.
        leoGui.leoGui.__init__(self,'qt')

        self.qtApp = QtGui.QApplication(sys.argv)

        self.bodyTextWidget  = leoQtTextWidget
        self.plainTextWidget = leoQtTextWidget
        self.loadIcons()

        win32clipboard = None

        ### self.qtClipboard = qt.Clipboard()
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
    #@+node:ekr.20081004102201.636:Do nothings
    # These methods must be defined in subclasses, but they need not do anything.

    def createRootWindow(self):
        pass

    def destroySelf (self):
        pass

    def killGui(self,exitFlag=True):
        """Destroy a gui and terminate Leo if exitFlag is True."""
        pass

    def recreateRootWindow(self):
        """A do-nothing base class to create the hidden root window of a gui
        after a previous gui has terminated with killGui(False)."""
        pass

    #@-node:ekr.20081004102201.636:Do nothings
    #@+node:ekr.20081004102201.637:Not used
    # The tkinter gui ctor calls these methods.
    # They are included here for reference.

    if 0:
        #@    @+others
        #@+node:ekr.20081004102201.638:qtGui.setDefaultIcon
        def setDefaultIcon(self):

            """Set the icon to be used in all Leo windows.

            This code does nothing for Tk versions before 8.4.3."""

            gui = self

            try:
                version = gui.root.getvar("tk_patchLevel")
                # g.trace(repr(version),g.CheckVersion(version,"8.4.3"))
                if g.CheckVersion(version,"8.4.3") and sys.platform == "win32":

                    path = g.os_path_join(g.app.loadDir,"..","Icons")
                    if g.os_path_exists(path):
                        theFile = g.os_path_join(path,"LeoApp16.ico")
                        if g.os_path_exists(path):
                            self.bitmap = QtGui.BitmapImage(theFile)
                        else:
                            g.es("","LeoApp16.ico","not in Icons directory",color="red")
                    else:
                        g.es("","Icons","directory not found:",path, color="red")
            except:
                g.pr("exception setting bitmap")
                import traceback ; traceback.print_exc()
        #@-node:ekr.20081004102201.638:qtGui.setDefaultIcon
        #@+node:ekr.20081004102201.639:qtGui.getDefaultConfigFont
        def getDefaultConfigFont(self,config):

            """Get the default font from a new text widget."""

            if not self.defaultFontFamily:
                # WARNING: retain NO references to widgets or fonts here!
                w = g.app.gui.plainTextWidget()
                fn = w.cget("font")
                font = qtFont.Font(font=fn) 
                family = font.cget("family")
                self.defaultFontFamily = family[:]
                # g.pr('***** getDefaultConfigFont',repr(family))

            config.defaultFont = None
            config.defaultFontFamily = self.defaultFontFamily
        #@-node:ekr.20081004102201.639:qtGui.getDefaultConfigFont
        #@-others
    #@-node:ekr.20081004102201.637:Not used
    #@-node:ekr.20081004102201.632:qtGui birth & death
    #@+node:ekr.20081004102201.640:qtGui dialogs & panels (test)
    def runAboutLeoDialog(self,c,version,theCopyright,url,email):
        """Create and run a qt About Leo dialog."""
        d = qtAboutLeo(c,version,theCopyright,url,email)
        return d.run(modal=False)

    def runAskLeoIDDialog(self):
        """Create and run a dialog to get g.app.LeoID."""
        d = qtAskLeoID()
        return d.run(modal=True)

    def runAskOkDialog(self,c,title,message=None,text="Ok"):
        """Create and run a qt an askOK dialog ."""
        d = qtAskOk(c,title,message,text)
        return d.run(modal=True)

    def runAskOkCancelNumberDialog(self,c,title,message):
        """Create and run askOkCancelNumber dialog ."""
        d = qtAskOkCancelNumber(c,title,message)
        return d.run(modal=True)

    def runAskOkCancelStringDialog(self,c,title,message):
        """Create and run askOkCancelString dialog ."""
        d = qtAskOkCancelString(c,title,message)
        return d.run(modal=True)

    def runAskYesNoDialog(self,c,title,message=None):
        """Create and run an askYesNo dialog."""
        d = qtAskYesNo(c,title,message)
        return d.run(modal=True)

    def runAskYesNoCancelDialog(self,c,title,
        message=None,yesMessage="Yes",noMessage="No",defaultButton="Yes"):
        """Create and run an askYesNoCancel dialog ."""
        d = qtAskYesNoCancel(
            c,title,message,yesMessage,noMessage,defaultButton)
        return d.run(modal=True)

    # The compare panel has no run dialog.

    # def runCompareDialog(self,c):
        # """Create and run an askYesNo dialog."""
        # if not g.app.unitTesting:
            # leoGtkCompareDialog(c)
    #@+node:ekr.20081004102201.641:qtGui.createSpellTab
    def createSpellTab(self,c,spellHandler,tabName):

        return qtSpellTab(c,spellHandler,tabName)
    #@-node:ekr.20081004102201.641:qtGui.createSpellTab
    #@+node:ekr.20081004102201.642:qtGui file dialogs
    #@+node:ekr.20081004102201.643:runFileDialog
    def runFileDialog(self,
        title='Open File',
        filetypes=None,
        action='open',
        multiple=False,
        initialFile=None
    ):

        g.trace()

        """Display an open or save file dialog.

        'title': The title to be shown in the dialog window.

        'filetypes': A list of (name, pattern) tuples.

        'action': Should be either 'save' or 'open'.

        'multiple': True if multiple files may be selected.

        'initialDir': The directory in which the chooser starts.

        'initialFile': The initial filename for a save dialog.

        """

        initialdir=g.app.globalOpenDir or g.os_path_finalize(os.getcwd())

        if action == 'open':
            btns = (
                QtCore.STOCK_CANCEL, QtCore.RESPONSE_CANCEL,
                QtCore.TOCK_OPEN, QtCore.RESPONSE_OK
            )
        else:
            btns = (
                QtCore.STOCK_CANCEL, QtCore.RESPONSE_CANCEL,
                QtCore.STOCK_SAVE, QtCore.RESPONSE_OK
            )

        qtaction = g.choose(
            action == 'save',
            QtCore.FILE_CHOOSER_ACTION_SAVE, 
            QtCore.FILE_CHOOSER_ACTION_OPEN
        )

        dialog = QtGui.FileChooserDialog(title,None,qtaction,btns)

        try:

            dialog.set_default_response(QtCore.RESPONSE_OK)
            dialog.set_do_overwrite_confirmation(True)
            dialog.set_select_multiple(multiple)
            if initialdir:
                dialog.set_current_folder(initialdir)

            if filetypes:

                for name, patern in filetypes:
                    filter = QtGui.FileFilter()
                    filter.set_name(name)
                    filter.add_pattern(patern)
                    dialog.add_filter(filter)

            response = dialog.run()
            g.pr('dialog response' , response)

            if response == QtCore.RESPONSE_OK:

                if multiple:
                    result = dialog.get_filenames()
                else:
                    result = dialog.get_filename()

            elif response == QtCore.RESPONSE_CANCEL:
                result = None

        finally:

            dialog.destroy()

        g.trace('dialog result' , result)

        return result
    #@-node:ekr.20081004102201.643:runFileDialog
    #@+node:ekr.20081004102201.644:runOpenFileDialog
    def runOpenFileDialog(self,title,filetypes,defaultextension,multiple=False):

        """Create and run an Qt open file dialog ."""

        fd = QFileDialog(self)
        fname = fd.getOpenFileName()
        g.trace(fname)
        return fname

        # self.load_file(fname)

        # return self.runFileDialog(
            # title=title,
            # filetypes=filetypes,
            # action='open',
            # multiple=multiple,
        # )
    #@-node:ekr.20081004102201.644:runOpenFileDialog
    #@+node:ekr.20081004102201.645:runSaveFileDialog
    def runSaveFileDialog(self,initialfile,title,filetypes,defaultextension):

        """Create and run an Qt save file dialog ."""

        # return self.runFileDialog(
            # title=title,
            # filetypes=filetypes,
            # action='save',
            # initialfile=initialfile
        # )
    #@nonl
    #@-node:ekr.20081004102201.645:runSaveFileDialog
    #@-node:ekr.20081004102201.642:qtGui file dialogs
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
    #@-node:ekr.20081004102201.646:qtGui panels
    #@-node:ekr.20081004102201.640:qtGui dialogs & panels (test)
    #@+node:ekr.20081004102201.647:qtGui utils (to do)
    #@+node:ekr.20081004102201.648:Clipboard (qtGui)
    #@+node:ekr.20081004102201.649:replaceClipboardWith
    def replaceClipboardWith (self,s):

        # g.app.gui.win32clipboard is always None.
        wcb = g.app.gui.win32clipboard

        if wcb:
            try:
                wcb.OpenClipboard(0)
                wcb.EmptyClipboard()
                wcb.SetClipboardText(s)
                wcb.CloseClipboard()
            except:
                g.es_exception()
        else:
            self.root.clipboard_clear()
            self.root.clipboard_append(s)
    #@-node:ekr.20081004102201.649:replaceClipboardWith
    #@+node:ekr.20081004102201.650:getTextFromClipboard
    def getTextFromClipboard (self):

        return None ###

        # g.app.gui.win32clipboard is always None.
        wcb = g.app.gui.win32clipboard

        if wcb:
            try:
                wcb.OpenClipboard(0)
                data = wcb.GetClipboardData()
                wcb.CloseClipboard()
                # g.trace(data)
                return data
            except TypeError:
                # g.trace(None)
                return None
            except:
                g.es_exception()
                return None
        else:
            try:
                s = self.root.selection_get(selection="CLIPBOARD")
                return s
            except:
                return None
    #@-node:ekr.20081004102201.650:getTextFromClipboard
    #@-node:ekr.20081004102201.648:Clipboard (qtGui)
    #@+node:ekr.20081004102201.651:color (to do)
    # g.es calls gui.color to do the translation,
    # so most code in Leo's core can simply use Tk color names.

    def color (self,color):
        '''Return the gui-specific color corresponding to the qt color name.'''
        return leoColor.getco

    #@-node:ekr.20081004102201.651:color (to do)
    #@+node:ekr.20081004102201.652:Dialog (these are optional)
    #@+node:ekr.20081004102201.653:get_window_info
    # WARNING: Call this routine _after_ creating a dialog.
    # (This routine inhibits the grid and pack geometry managers.)

    def get_window_info (self,top):

        return ###

        top.update_idletasks() # Required to get proper info.

        # Get the information about top and the screen.
        geom = top.geometry() # geom = "WidthxHeight+XOffset+YOffset"
        dim,x,y = geom.split('+')
        w,h = dim.split('x')
        w,h,x,y = int(w),int(h),int(x),int(y)

        return w,h,x,y
    #@-node:ekr.20081004102201.653:get_window_info
    #@+node:ekr.20081004102201.654:center_dialog
    def center_dialog(self,top):

        """Center the dialog on the screen.

        WARNING: Call this routine _after_ creating a dialog.
        (This routine inhibits the grid and pack geometry managers.)"""

        return ###

        sw = top.winfo_screenwidth()
        sh = top.winfo_screenheight()
        w,h,x,y = self.get_window_info(top)

        # Set the new window coordinates, leaving w and h unchanged.
        x = (sw - w)/2
        y = (sh - h)/2
        top.geometry("%dx%d%+d%+d" % (w,h,x,y))

        return w,h,x,y
    #@-node:ekr.20081004102201.654:center_dialog
    #@+node:ekr.20081004102201.655:create_labeled_frame
    # Returns frames w and f.
    # Typically the caller would pack w into other frames, and pack content into f.

    def create_labeled_frame (self,parent,
        caption=None,relief="groove",bd=2,padx=0,pady=0):

        return ###

        # Create w, the master frame.
        w = qt.Frame(parent)
        w.grid(sticky="news")

        # Configure w as a grid with 5 rows and columns.
        # The middle of this grid will contain f, the expandable content area.
        w.columnconfigure(1,minsize=bd)
        w.columnconfigure(2,minsize=padx)
        w.columnconfigure(3,weight=1)
        w.columnconfigure(4,minsize=padx)
        w.columnconfigure(5,minsize=bd)

        w.rowconfigure(1,minsize=bd)
        w.rowconfigure(2,minsize=pady)
        w.rowconfigure(3,weight=1)
        w.rowconfigure(4,minsize=pady)
        w.rowconfigure(5,minsize=bd)

        # Create the border spanning all rows and columns.
        border = qt.Frame(w,bd=bd,relief=relief) # padx=padx,pady=pady)
        border.grid(row=1,column=1,rowspan=5,columnspan=5,sticky="news")

        # Create the content frame, f, in the center of the grid.
        f = qt.Frame(w,bd=bd)
        f.grid(row=3,column=3,sticky="news")

        # Add the caption.
        if caption and len(caption) > 0:
            caption = qt.Label(parent,text=caption,highlightthickness=0,bd=0)
            # caption.tkraise(w)
            caption.grid(in_=w,row=0,column=2,rowspan=2,columnspan=3,padx=4,sticky="w")

        return w,f
    #@-node:ekr.20081004102201.655:create_labeled_frame
    #@-node:ekr.20081004102201.652:Dialog (these are optional)
    #@+node:ekr.20081004102201.656:Events (qtGui) (to do)
    def event_generate(self,w,kind,*args,**keys):
        '''Generate an event.'''
        return w.event_generate(kind,*args,**keys)

    def eventChar (self,event,c=None):
        '''Return the char field of an event.'''
        return event and event.char or ''

    def eventKeysym (self,event,c=None):
        '''Return the keysym value of an event.'''
        return event and event.keysym

    def eventWidget (self,event,c=None):
        '''Return the widget field of an event.'''   
        return event and event.widget

    def eventXY (self,event,c=None):
        if event:
            return event.x,event.y
        else:
            return 0,0
    #@nonl
    #@-node:ekr.20081004102201.656:Events (qtGui) (to do)
    #@+node:ekr.20081004102201.657:Focus (to do)
    #@+node:ekr.20081004102201.658:qtGui.get_focus
    def get_focus(self,c):

        """Returns the widget that has focus, or body if None."""

        return None ###

        return c.frame.top.focus_displayof()
    #@-node:ekr.20081004102201.658:qtGui.get_focus
    #@+node:ekr.20081004102201.659:qtGui.set_focus
    set_focus_count = 0

    def set_focus(self,c,w):

        """Put the focus on the widget."""

        return None ###

        if not g.app.unitTesting and c and c.config.getBool('trace_g.app.gui.set_focus'):
            self.set_focus_count += 1
            # Do not call trace here: that might affect focus!
            g.pr('gui.set_focus: %4d %10s %s' % (
                self.set_focus_count,c and c.shortFileName(),
                c and c.widget_name(w)), g.callers(5))

        if w:
            try:
                # It's possible that the widget doesn't exist now.
                w.focus_set()
                return True
            except Exception:
                # g.es_exception()
                return False
    #@-node:ekr.20081004102201.659:qtGui.set_focus
    #@-node:ekr.20081004102201.657:Focus (to do)
    #@+node:ekr.20081004102201.660:Font (to do)
    #@+node:ekr.20081004102201.661:qtGui.getFontFromParams
    def getFontFromParams(self,family,size,slant,weight,defaultSize=12):

        family_name = family

        try:
            font = qtFont.Font(family=family,size=size or defaultSize,slant=slant,weight=weight)
            return font
        except:
            g.es("exception setting font from","",family_name)
            g.es("","family,size,slant,weight:","",family,"",size,"",slant,"",weight)
            # g.es_exception() # This just confuses people.
            return g.app.config.defaultFont
    #@-node:ekr.20081004102201.661:qtGui.getFontFromParams
    #@-node:ekr.20081004102201.660:Font (to do)
    #@+node:ekr.20081004102201.662:getFullVersion
    def getFullVersion (self,c):

        try:
            qtLevel = 'version %s' % QtCore.QT_VERSION
        except Exception:
            # g.es_exception()
            qtLevel = '<qtLevel>'

        return 'qt %s' % (qtLevel)
    #@-node:ekr.20081004102201.662:getFullVersion
    #@+node:ekr.20081004102201.663:Icons (to do)
    #@+node:ekr.20081004102201.664:attachLeoIcon
    def attachLeoIcon (self,w):

        """Attach a Leo icon to the Leo Window."""

        # if self.bitmap != None:
            # # We don't need PIL or tkicon: this is gtk 8.3.4 or greater.
            # try:
                # w.wm_iconbitmap(self.bitmap)
            # except:
                # self.bitmap = None

        # if self.bitmap == None:
            # try:
                # < < try to use the PIL and tkIcon packages to draw the icon > >
            # except:
                # # import traceback ; traceback.print_exc()
                # # g.es_exception()
                # self.leoIcon = None
    #@+node:ekr.20081004102201.665:try to use the PIL and tkIcon packages to draw the icon
    #@+at 
    #@nonl
    # This code requires Fredrik Lundh's PIL and tkIcon packages:
    # 
    # Download PIL    from http://www.pythonware.com/downloads/index.htm#pil
    # Download tkIcon from http://www.effbot.org/downloads/#tkIcon
    # 
    # Many thanks to Jonathan M. Gilligan for suggesting this code.
    #@-at
    #@@c

    # import Image
    # import tkIcon # pychecker complains, but this *is* used.

    # # Wait until the window has been drawn once before attaching the icon in OnVisiblity.
    # def visibilityCallback(event,self=self,w=w):
        # try: self.leoIcon.attach(w.winfo_id())
        # except: pass
    # c.bind(w,"<Visibility>",visibilityCallback)

    # if not self.leoIcon:
        # # Load a 16 by 16 gif.  Using .gif rather than an .ico allows us to specify transparency.
        # icon_file_name = g.os_path_join(g.app.loadDir,'..','Icons','LeoWin.gif')
        # icon_file_name = g.os_path_normpath(icon_file_name)
        # icon_image = Image.open(icon_file_name)
        # if 1: # Doesn't resize.
            # self.leoIcon = self.createLeoIcon(icon_image)
        # else: # Assumes 64x64
            # self.leoIcon = tkIcon.Icon(icon_image)
    #@-node:ekr.20081004102201.665:try to use the PIL and tkIcon packages to draw the icon
    #@+node:ekr.20081004102201.666:createLeoIcon (a helper)
    # This code is adapted from tkIcon.__init__
    # Unlike the tkIcon code, this code does _not_ resize the icon file.

    # def createLeoIcon (self,icon):

        # try:
            # import Image,_tkicon

            # i = icon ; m = None
            # # create transparency mask
            # if i.mode == "P":
                # try:
                    # t = i.info["transparency"]
                    # m = i.point(lambda i, t=t: i==t, "1")
                # except KeyError: pass
            # elif i.mode == "RGBA":
                # # get transparency layer
                # m = i.split()[3].point(lambda i: i == 0, "1")
            # if not m:
                # m = Image.new("1", i.size, 0) # opaque
            # # clear unused parts of the original image
            # i = i.convert("RGB")
            # i.paste((0, 0, 0), (0, 0), m)
            # # create icon
            # m = m.tostring("raw", ("1", 0, 1))
            # c = i.tostring("raw", ("BGRX", 0, -1))
            # return _tkicon.new(i.size, c, m)
        # except:
            # return None
    #@-node:ekr.20081004102201.666:createLeoIcon (a helper)
    #@-node:ekr.20081004102201.664:attachLeoIcon
    #@-node:ekr.20081004102201.663:Icons (to do)
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

        return w and isinstance(w,leoFrame.baseTextWidget)
    #@-node:ekr.20081004102201.670:isTextWidget
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
    #@-node:ekr.20081004102201.647:qtGui utils (to do)
    #@+node:ekr.20081004102201.676:class leoKeyEvent
    class leoKeyEvent:

        '''A gui-independent wrapper for gui events.'''

        def __init__ (self,event,c):

            # g.trace('leoKeyEvent(qtGui)')
            self.actualEvent = event
            self.c      = c # Required to access c.k tables.
            self.char   = hasattr(event,'char') and event.char or ''
            self.keysym = hasattr(event,'keysym') and event.keysym or ''
            self.w      = hasattr(event,'widget') and event.widget or None
            self.x      = hasattr(event,'x') and event.x or 0
            self.y      = hasattr(event,'y') and event.y or 0
            # Support for fastGotoNode plugin
            self.x_root = hasattr(event,'x_root') and event.x_root or 0
            self.y_root = hasattr(event,'y_root') and event.y_root or 0

            if self.keysym and c.k:
                # Translate keysyms for ascii characters to the character itself.
                self.keysym = c.k.guiBindNamesInverseDict.get(self.keysym,self.keysym)

            self.widget = self.w

        def __repr__ (self):

            return 'qtGui.leoKeyEvent: char: %s, keysym: %s' % (repr(self.char),repr(self.keysym))
    #@nonl
    #@-node:ekr.20081004102201.676:class leoKeyEvent
    #@+node:ekr.20081004102201.677:loadIcon
    def loadIcon(self, fname):

        if 0: g.trace('fname',fname)

        # try:
            # icon = qt.gdk.pixbuf_new_from_file(fname)
        # except:
            # icon = None

        # if icon and icon.get_width()>0:
            # return icon

        # g.trace( 'Can not load icon from', fname)
    #@-node:ekr.20081004102201.677:loadIcon
    #@+node:ekr.20081004102201.678:loadIcons
    def loadIcons(self):
        """Load icons and images and set up module level variables."""

        self.treeIcons = icons = []
        self.namedIcons = namedIcons = {}

        path = g.os_path_finalize_join(g.app.loadDir, '..', 'Icons')
        if g.os_path_exists(g.os_path_join(path, 'box01.GIF')):
            ext = '.GIF'
        else:
            ext = '.gif'

        for i in range(16):
            icon = self.loadIcon(g.os_path_join(path, 'box%02d'%i + ext))
            icons.append(icon)

        for name, ext in (
            ('lt_arrow_enabled', '.gif'),
            ('rt_arrow_enabled', '.gif'),
            ('lt_arrow_disabled', '.gif'),
            ('rt_arrow_disabled', '.gif'),
            ('plusnode', '.gif'),
            ('minusnode', '.gif'),
            ('Leoapp', '.GIF')
        ):
            icon = self.loadIcon(g.os_path_join(path, name + ext))
            namedIcons[name] = icon

        self.plusBoxIcon = namedIcons.get('plusnode')
        self.minusBoxIcon = namedIcons.get('minusnode')
        self.appIcon = namedIcons.get('Leoapp')

        self.globalImages = {}

    #@-node:ekr.20081004102201.678:loadIcons
    #@-others
#@-node:ekr.20081004102201.631:class leoQtGui
#@+node:ekr.20081004172422.622:class leoQtLog
class leoQtLog (leoFrame.leoLog):

    """A class that represents the log pane of a Qt window."""

    #@    @+others
    #@+node:ekr.20081004172422.623:qtLog Birth
    #@+node:ekr.20081004172422.624:qtLog.__init__
    def __init__ (self,frame,parentFrame):

        g.trace("leoQtLog")

        # Call the base class constructor and calls createControl.
        leoFrame.leoLog.__init__(self,frame,parentFrame)

        self.c = c = frame.c # Also set in the base constructor, but we need it here.

        self.colorTags = []
            # The list of color names used as tags in present tab.
            # This gest switched by selectTab.

        self.wrap = g.choose(c.config.getBool('log_pane_wraps'),"word","none")

        # New in 4.4a2: The log pane is a Pmw.Notebook...

        self.nb = None      # The Pmw.Notebook that holds all the tabs.
        self.colorTagsDict = {} # Keys are page names.  Values are saved colorTags lists.
        self.menu = None # A menu that pops up on right clicks in the hull or in tabs.

        self.logCtrl = self.createControl(parentFrame)
        self.setFontFromConfig()
        self.setColorFromConfig()
    #@-node:ekr.20081004172422.624:qtLog.__init__
    #@+node:ekr.20081004172422.625:qtLog.createControl
    def createControl (self,parentFrame):

        c = self.c

        return None ###

        self.nb = Pmw.NoteBook(parentFrame,
            borderwidth = 1, pagemargin = 0,
            raisecommand = self.raiseTab,
            lowercommand = self.lowerTab,
            arrownavigation = 0,
        )

        menu = self.makeTabMenu(tabName=None)

        def hullMenuCallback(event):
            return self.onRightClick(event,menu)

        c.bind(self.nb,'<Button-3>',hullMenuCallback)

        self.nb.pack(fill='both',expand=1)
        self.selectTab('Log') # Create and activate the default tabs.

        return self.logCtrl
    #@-node:ekr.20081004172422.625:qtLog.createControl
    #@+node:ekr.20081004172422.626:qtLog.finishCreate
    def finishCreate (self):

        # g.trace('qtLog')

        c = self.c ; log = self

        return ###

        c.searchCommands.openFindTab(show=False)
        c.spellCommands.openSpellTab()
        log.selectTab('Log')
    #@-node:ekr.20081004172422.626:qtLog.finishCreate
    #@+node:ekr.20081004172422.627:qtLog.createCanvasWidget
    def createCanvasWidget (self,parentFrame):

        return ###

        self.logNumber += 1

        w = qt.Canvas(parentFrame)

        logBar = qt.Scrollbar(parentFrame,name="logBar")
        w['yscrollcommand'] = logBar.set
        logBar['command'] = w.yview
        logBar.pack(side="right", fill="y")

        logXBar = qt.Scrollbar(parentFrame,name='logXBar',orient="horizontal") 
        w['xscrollcommand'] = logXBar.set 
        logXBar['command'] = w.xview 
        logXBar.pack(side="bottom", fill="x")

        w.pack(expand=1, fill="both")

        # Set the background color.
        configName = 'log_canvas_pane_tab_background_color'
        bg = self.c.config.getColor(configName) or 'MistyRose1'
        try: w.configure(bg=bg)
        except Exception: pass # Could be a user error.

        return w
    #@-node:ekr.20081004172422.627:qtLog.createCanvasWidget
    #@+node:ekr.20081004172422.628:qtLog.createTextWidget
    def createTextWidget (self,parentFrame):

        return None ###

        self.logNumber += 1
        log = g.app.gui.plainTextWidget(
            parentFrame,name="log-%d" % self.logNumber,
            setgrid=0,wrap=self.wrap,bd=2,bg="white",relief="flat")

        logBar = qt.Scrollbar(parentFrame,name="logBar")

        log['yscrollcommand'] = logBar.set
        logBar['command'] = log.yview

        logBar.pack(side="right", fill="y")
        # rr 8/14/02 added horizontal elevator 
        if self.wrap == "none": 
            logXBar = qt.Scrollbar( 
                parentFrame,name='logXBar',orient="horizontal") 
            log['xscrollcommand'] = logXBar.set 
            logXBar['command'] = log.xview 
            logXBar.pack(side="bottom", fill="x")
        log.pack(expand=1, fill="both")

        return log
    #@-node:ekr.20081004172422.628:qtLog.createTextWidget
    #@+node:ekr.20081004172422.629:qtLog.makeTabMenu
    def makeTabMenu (self,tabName=None,allowRename=True):

        '''Create a tab popup menu.'''

        # g.trace(tabName,g.callers())

        return ###

        c = self.c
        hull = self.nb.component('hull') # A qt.Canvas.

        menu = qt.Menu(hull,tearoff=0)
        c.add_command(menu,label='New Tab',command=self.newTabFromMenu)
        c.add_command(menu,label='New CanvasTab',command=self.newCanvasTabFromMenu)

        if tabName:
            # Important: tabName is the name when the tab is created.
            # It is not affected by renaming, so we don't have to keep
            # track of the correspondence between this name and what is in the label.
            def deleteTabCallback():
                return self.deleteTab(tabName)

            label = g.choose(
                tabName in ('Find','Spell'),'Hide This Tab','Delete This Tab')
            c.add_command(menu,label=label,command=deleteTabCallback)

            def renameTabCallback():
                return self.renameTabFromMenu(tabName)

            if allowRename:
                c.add_command(menu,label='Rename This Tab',command=renameTabCallback)

        return menu
    #@-node:ekr.20081004172422.629:qtLog.makeTabMenu
    #@-node:ekr.20081004172422.623:qtLog Birth
    #@+node:ekr.20081004172422.630:Config & get/saveState
    #@+node:ekr.20081004172422.631:qtLog.configureBorder & configureFont
    def configureBorder(self,border):

        ### self.logCtrl.configure(bd=border)
        pass

    def configureFont(self,font):

        ### self.logCtrl.configure(font=font)
        pass
    #@-node:ekr.20081004172422.631:qtLog.configureBorder & configureFont
    #@+node:ekr.20081004172422.632:qtLog.getFontConfig
    def getFontConfig (self):

        return None

        # font = self.logCtrl.cget("font")
        # # g.trace(font)
        # return font
    #@-node:ekr.20081004172422.632:qtLog.getFontConfig
    #@+node:ekr.20081004172422.633:qtLog.restoreAllState
    def restoreAllState (self,d):

        '''Restore the log from a dict created by saveAllState.'''

        return ###

        logCtrl = self.logCtrl

        # Restore the text.
        text = d.get('text')
        logCtrl.insert('end',text)

        # Restore all colors.
        colors = d.get('colors')
        for color in colors:
            if color not in self.colorTags:
                self.colorTags.append(color)
                logCtrl.tag_config(color,foreground=color)
            items = list(colors.get(color))
            while items:
                start,stop = items[0],items[1]
                items = items[2:]
                logCtrl.tag_add(color,start,stop)
    #@-node:ekr.20081004172422.633:qtLog.restoreAllState
    #@+node:ekr.20081004172422.634:qtLog.saveAllState
    def saveAllState (self):

        '''Return a dict containing all data needed to recreate the log in another widget.'''

        return ###

        logCtrl = self.logCtrl ; colors = {}

        # Save the text
        text = logCtrl.getAllText()

        # Save color tags.
        tag_names = logCtrl.tag_names()
        for tag in tag_names:
            if tag in self.colorTags:
                colors[tag] = logCtrl.tag_ranges(tag)

        d = {'text':text,'colors': colors}
        # g.trace('\n',g.dictToString(d))
        return d
    #@-node:ekr.20081004172422.634:qtLog.saveAllState
    #@+node:ekr.20081004172422.635:qtLog.setColorFromConfig
    def setColorFromConfig (self):

        c = self.c

        bg = c.config.getColor("log_pane_background_color") or 'white'

        return ###

        try:
            self.logCtrl.configure(bg=bg)
        except:
            g.es("exception setting log pane background color")
            g.es_exception()
    #@-node:ekr.20081004172422.635:qtLog.setColorFromConfig
    #@+node:ekr.20081004172422.636:qtLog.setFontFromConfig
    def SetWidgetFontFromConfig (self,logCtrl=None):

        c = self.c

        return ###

        if not logCtrl: logCtrl = self.logCtrl

        font = c.config.getFontFromParams(
            "log_text_font_family", "log_text_font_size",
            "log_text_font_slant", "log_text_font_weight",
            c.config.defaultLogFontSize)

        self.fontRef = font # ESSENTIAL: retain a link to font.
        logCtrl.configure(font=font)

        # g.trace("LOG",logCtrl.cget("font"),font.cget("family"),font.cget("weight"))

        bg = c.config.getColor("log_text_background_color")
        if bg:
            try: logCtrl.configure(bg=bg)
            except: pass

        fg = c.config.getColor("log_text_foreground_color")
        if fg:
            try: logCtrl.configure(fg=fg)
            except: pass

    setFontFromConfig = SetWidgetFontFromConfig # Renaming supresses a pychecker warning.
    #@-node:ekr.20081004172422.636:qtLog.setFontFromConfig
    #@-node:ekr.20081004172422.630:Config & get/saveState
    #@+node:ekr.20081004172422.637:Focus & update (qtLog)
    #@+node:ekr.20081004172422.638:qtLog.onActivateLog
    def onActivateLog (self,event=None):

        return ###

        try:
            self.c.setLog()
            self.frame.tree.OnDeactivate()
            self.c.logWantsFocus()
        except:
            g.es_event_exception("activate log")
    #@-node:ekr.20081004172422.638:qtLog.onActivateLog
    #@+node:ekr.20081004172422.639:qtLog.hasFocus
    def hasFocus (self):

        return None

        ### return self.c.get_focus() == self.logCtrl
    #@-node:ekr.20081004172422.639:qtLog.hasFocus
    #@+node:ekr.20081004172422.640:forceLogUpdate
    def forceLogUpdate (self,s):

        return ###

        if sys.platform == "darwin": # Does not work on MacOS X.
            try:
                g.pr(s,newline=False) # Don't add a newline.
            except UnicodeError:
                # g.app may not be inited during scripts!
                g.pr(g.toEncodedString(s,'utf-8'))
        else:
            self.logCtrl.update_idletasks()
    #@-node:ekr.20081004172422.640:forceLogUpdate
    #@-node:ekr.20081004172422.637:Focus & update (qtLog)
    #@+node:ekr.20081004172422.641:put & putnl (qtLog)
    #@+node:ekr.20081004172422.642:put
    # All output to the log stream eventually comes here.
    def put (self,s,color=None,tabName='Log'):

        print s ###
        return ###

        c = self.c

        # g.pr('qtLog.put',s)
        # g.pr('qtLog.put',len(s),g.callers())

        if g.app.quitting or not c or not c.exists:
            return

        if tabName:
            self.selectTab(tabName)

        # Note: this must be done after the call to selectTab.
        w = self.logCtrl
        if w:
            #@        << put s to log control >>
            #@+node:ekr.20081004172422.643:<< put s to log control >>
            if color:
                if color not in self.colorTags:
                    self.colorTags.append(color)
                    w.tag_config(color,foreground=color)
                w.insert("end",s)
                w.tag_add(color,"end-%dc" % (len(s)+1),"end-1c")
                w.tag_add("black","end")
            else:
                w.insert("end",s)

            w.see('end')
            self.forceLogUpdate(s)
            #@-node:ekr.20081004172422.643:<< put s to log control >>
            #@nl
            self.logCtrl.update_idletasks()
        else:
            #@        << put s to logWaiting and print s >>
            #@+node:ekr.20081004172422.644:<< put s to logWaiting and print s >>
            g.app.logWaiting.append((s,color),)

            g.pr("Null qt log")

            if type(s) == type(u""):
                s = g.toEncodedString(s,"ascii")

            g.pr(s)
            #@-node:ekr.20081004172422.644:<< put s to logWaiting and print s >>
            #@nl
    #@-node:ekr.20081004172422.642:put
    #@+node:ekr.20081004172422.645:putnl
    def putnl (self,tabName='Log'):

        ### print ###
        return ###

        if g.app.quitting:
            return

        # g.pr('qtLog.putnl' # ,g.callers())

        if tabName:
            self.selectTab(tabName)

        w = self.logCtrl

        if w:
            w.insert("end",'\n')
            w.see('end')
            self.forceLogUpdate('\n')
        else:
            # Put a newline to logWaiting and print newline
            g.app.logWaiting.append(('\n',"black"),)
            g.pr("Null qt log")
    #@-node:ekr.20081004172422.645:putnl
    #@-node:ekr.20081004172422.641:put & putnl (qtLog)
    #@+node:ekr.20081004172422.646:Tab (QtLog)
    #@+node:ekr.20081004172422.647:clearTab
    def clearTab (self,tabName,wrap='none'):

        return ###

        self.selectTab(tabName,wrap=wrap)
        w = self.logCtrl
        if w: w.delete(0,'end')
    #@-node:ekr.20081004172422.647:clearTab
    #@+node:ekr.20081004172422.648:createCanvas
    def createCanvas (self,tabName=None):

        return ###

        c = self.c ; k = c.k

        if tabName is None:
            self.logNumber += 1
            tabName = 'Canvas %d' % self.logNumber

        tabFrame = self.nb.add(tabName)
        menu = self.makeTabMenu(tabName,allowRename=False)

        w = self.createCanvasWidget(tabFrame)

        self.canvasDict [tabName ] = w
        self.textDict [tabName] = None
        self.frameDict [tabName] = tabFrame

        self.setCanvasTabBindings(tabName,menu)

        return w
    #@-node:ekr.20081004172422.648:createCanvas
    #@+node:ekr.20081004172422.649:createTab
    def createTab (self,tabName,createText=True,wrap='none'):

        return ###

        # g.trace(tabName,wrap)

        c = self.c ; k = c.k
        tabFrame = self.nb.add(tabName)
        self.menu = self.makeTabMenu(tabName)
        if createText:
            #@        << Create the tab's text widget >>
            #@+node:ekr.20081004172422.650:<< Create the tab's text widget >>
            w = self.createTextWidget(tabFrame)

            # Set the background color.
            configName = 'log_pane_%s_tab_background_color' % tabName
            bg = c.config.getColor(configName) or 'MistyRose1'

            if wrap not in ('none','char','word'): wrap = 'none'
            try: w.configure(bg=bg,wrap=wrap)
            except Exception: pass # Could be a user error.

            self.SetWidgetFontFromConfig(logCtrl=w)

            self.canvasDict [tabName ] = None
            self.frameDict [tabName] = tabFrame
            self.textDict [tabName] = w

            # Switch to a new colorTags list.
            if self.tabName:
                self.colorTagsDict [self.tabName] = self.colorTags [:]

            self.colorTags = ['black']
            self.colorTagsDict [tabName] = self.colorTags
            #@-node:ekr.20081004172422.650:<< Create the tab's text widget >>
            #@nl
        else:
            self.canvasDict [tabName] = None
            self.textDict [tabName] = None
            self.frameDict [tabName] = tabFrame

        if tabName != 'Log':
            # c.k doesn't exist when the log pane is created.
            # k.makeAllBindings will call setTabBindings('Log')
            self.setTabBindings(tabName)
    #@-node:ekr.20081004172422.649:createTab
    #@+node:ekr.20081004172422.651:cycleTabFocus
    def cycleTabFocus (self,event=None,stop_w = None):

        '''Cycle keyboard focus between the tabs in the log pane.'''

        return ###

        c = self.c ; d = self.frameDict # Keys are page names. Values are qt.Frames.
        w = d.get(self.tabName)
        # g.trace(self.tabName,w)
        values = d.values()
        if self.numberOfVisibleTabs() > 1:
            i = i2 = values.index(w) + 1
            if i == len(values): i = 0
            tabName = d.keys()[i]
            self.selectTab(tabName)
            return 
    #@-node:ekr.20081004172422.651:cycleTabFocus
    #@+node:ekr.20081004172422.652:deleteTab
    def deleteTab (self,tabName,force=False):

        return ###

        if tabName == 'Log':
            pass

        elif tabName in ('Find','Spell') and not force:
            self.selectTab('Log')

        elif tabName in self.nb.pagenames():
            # g.trace(tabName,force)
            self.nb.delete(tabName)
            self.colorTagsDict [tabName] = []
            self.canvasDict [tabName ] = None
            self.textDict [tabName] = None
            self.frameDict [tabName] = None
            self.tabName = None
            self.selectTab('Log')

        # New in Leo 4.4b1.
        self.c.invalidateFocus()
        self.c.bodyWantsFocus()
    #@-node:ekr.20081004172422.652:deleteTab
    #@+node:ekr.20081004172422.653:hideTab
    def hideTab (self,tabName):

        self.selectTab('Log')
    #@-node:ekr.20081004172422.653:hideTab
    #@+node:ekr.20081004172422.654:getSelectedTab
    def getSelectedTab (self):

        return self.tabName
    #@-node:ekr.20081004172422.654:getSelectedTab
    #@+node:ekr.20081004172422.655:lower/raiseTab
    def lowerTab (self,tabName):

        # if tabName:
            # b = self.nb.tab(tabName) # b is a qt.Button.
            # b.config(bg='grey80')
        self.c.invalidateFocus()
        self.c.bodyWantsFocus()

    def raiseTab (self,tabName):

        # if tabName:
            # b = self.nb.tab(tabName) # b is a qt.Button.
            # b.config(bg='LightSteelBlue1')
        self.c.invalidateFocus()
        self.c.bodyWantsFocus()
    #@-node:ekr.20081004172422.655:lower/raiseTab
    #@+node:ekr.20081004172422.656:numberOfVisibleTabs
    def numberOfVisibleTabs (self):

        return len([val for val in self.frameDict.values() if val != None])
    #@-node:ekr.20081004172422.656:numberOfVisibleTabs
    #@+node:ekr.20081004172422.657:renameTab
    def renameTab (self,oldName,newName):

        pass

        # g.trace('newName',newName)

        # label = self.nb.tab(oldName)
        # label.configure(text=newName)
    #@-node:ekr.20081004172422.657:renameTab
    #@+node:ekr.20081004172422.658:selectTab
    def selectTab (self,tabName,createText=True,wrap='none'):

        '''Create the tab if necessary and make it active.'''

        c = self.c

        return ###

        tabFrame = self.frameDict.get(tabName)
        logCtrl = self.textDict.get(tabName)

        if tabFrame and logCtrl:
            # Switch to a new colorTags list.
            newColorTags = self.colorTagsDict.get(tabName)
            self.colorTagsDict [self.tabName] = self.colorTags [:]
            self.colorTags = newColorTags
        elif not tabFrame:
            self.createTab(tabName,createText=createText,wrap=wrap)

        self.nb.selectpage(tabName)
        # Update the status vars.
        self.tabName = tabName
        w = self.textDict.get(tabName)
        if w: self.logCtrl = w
        self.tabFrame = self.frameDict.get(tabName)

        if 0: # Absolutely do not do this here!  It is a cause of the 'sticky focus' problem.
            c.widgetWantsFocusNow(self.logCtrl)
        return tabFrame
    #@-node:ekr.20081004172422.658:selectTab
    #@+node:ekr.20081004172422.659:setTabBindings
    def setTabBindings (self,tabName):

        return ###

        c = self.c ; k = c.k
        tab = self.nb.tab(tabName)
        w = self.textDict.get(tabName) or self.frameDict.get(tabName)

        def logTextRightClickCallback(event):
            return c.k.masterClick3Handler(event,self.onLogTextRightClick)


        # Send all event in the text area to the master handlers.
        for kind,handler in (
            ('<Key>',       k.masterKeyHandler),
            ('<Button-1>',  k.masterClickHandler),
            ('<Button-3>',  logTextRightClickCallback),
        ):
            c.bind(w,kind,handler)

        # Clicks in the tab area are harmless: use the old code.
        def tabMenuRightClickCallback(event,menu=self.menu):
            return self.onRightClick(event,menu)

        def tabMenuClickCallback(event,tabName=tabName):
            return self.onClick(event,tabName)

        c.bind(tab,'<Button-1>',tabMenuClickCallback)
        c.bind(tab,'<Button-3>',tabMenuRightClickCallback)

        k.completeAllBindingsForWidget(w)
    #@-node:ekr.20081004172422.659:setTabBindings
    #@+node:ekr.20081004172422.660:onLogTextRightClick
    def onLogTextRightClick(self, event):

        g.doHook('rclick-popup', c=self.c, event=event, context_menu='log')
    #@-node:ekr.20081004172422.660:onLogTextRightClick
    #@+node:ekr.20081004172422.661:setCanvasTabBindings
    def setCanvasTabBindings (self,tabName,menu):

        return ###

        c = self.c ; tab = self.nb.tab(tabName)

        def tabMenuRightClickCallback(event,menu=menu):
            return self.onRightClick(event,menu)

        def tabMenuClickCallback(event,tabName=tabName):
            return self.onClick(event,tabName)

        c.bind(tab,'<Button-1>',tabMenuClickCallback)
        c.bind(tab,'<Button-3>',tabMenuRightClickCallback)

    #@-node:ekr.20081004172422.661:setCanvasTabBindings
    #@+node:ekr.20081004172422.662:Tab menu callbacks & helpers
    #@+node:ekr.20081004172422.663:onRightClick & onClick
    def onRightClick (self,event,menu):

        c = self.c
        # menu.post(event.x_root,event.y_root)


    def onClick (self,event,tabName):

        self.selectTab(tabName)
    #@-node:ekr.20081004172422.663:onRightClick & onClick
    #@+node:ekr.20081004172422.664:newTabFromMenu & newCanvasTabFromMenu
    def newTabFromMenu (self,tabName='Log'):

        self.selectTab(tabName)

        # This is called by getTabName.
        def selectTabCallback (newName):
            return self.selectTab(newName)

        # self.getTabName(selectTabCallback)

    def newCanvasTabFromMenu (self):

        # self.createCanvas()
        pass
    #@-node:ekr.20081004172422.664:newTabFromMenu & newCanvasTabFromMenu
    #@+node:ekr.20081004172422.665:renameTabFromMenu
    def renameTabFromMenu (self,tabName):

        if tabName in ('Log','Completions'):
            g.es('can not rename',tabName,'tab',color='blue')
        else:
            def renameTabCallback (newName):
                return self.renameTab(tabName,newName)

            self.getTabName(renameTabCallback)
    #@-node:ekr.20081004172422.665:renameTabFromMenu
    #@+node:ekr.20081004172422.666:getTabName
    def getTabName (self,exitCallback):

        return ###

        canvas = self.nb.component('hull')

        # Overlay what is there!
        c = self.c
        f = qt.Frame(canvas)
        f.pack(side='top',fill='both',expand=1)

        row1 = qt.Frame(f)
        row1.pack(side='top',expand=0,fill='x',pady=10)
        row2 = qt.Frame(f)
        row2.pack(side='top',expand=0,fill='x')

        qt.Label(row1,text='Tab name').pack(side='left')

        e = qt.Entry(row1,background='white')
        e.pack(side='left')

        def getNameCallback (event=None):
            s = e.get().strip()
            f.pack_forget()
            if s: exitCallback(s)

        def closeTabNameCallback (event=None):
            f.pack_forget()

        b = qt.Button(row2,text='Ok',width=6,command=getNameCallback)
        b.pack(side='left',padx=10)

        b = qt.Button(row2,text='Cancel',width=6,command=closeTabNameCallback)
        b.pack(side='left')

        g.app.gui.set_focus(c,e)
        c.bind(e,'<Return>',getNameCallback)
    #@-node:ekr.20081004172422.666:getTabName
    #@-node:ekr.20081004172422.662:Tab menu callbacks & helpers
    #@-node:ekr.20081004172422.646:Tab (QtLog)
    #@+node:ekr.20081004172422.667:qtLog color tab stuff
    def createColorPicker (self,tabName):

        return ###

        log = self

        #@    << define colors >>
        #@+node:ekr.20081004172422.668:<< define colors >>
        colors = (
            "gray60", "gray70", "gray80", "gray85", "gray90", "gray95",
            "snow1", "snow2", "snow3", "snow4", "seashell1", "seashell2",
            "seashell3", "seashell4", "AntiqueWhite1", "AntiqueWhite2", "AntiqueWhite3",
            "AntiqueWhite4", "bisque1", "bisque2", "bisque3", "bisque4", "PeachPuff1",
            "PeachPuff2", "PeachPuff3", "PeachPuff4", "NavajoWhite1", "NavajoWhite2",
            "NavajoWhite3", "NavajoWhite4", "LemonChiffon1", "LemonChiffon2",
            "LemonChiffon3", "LemonChiffon4", "cornsilk1", "cornsilk2", "cornsilk3",
            "cornsilk4", "ivory1", "ivory2", "ivory3", "ivory4", "honeydew1", "honeydew2",
            "honeydew3", "honeydew4", "LavenderBlush1", "LavenderBlush2",
            "LavenderBlush3", "LavenderBlush4", "MistyRose1", "MistyRose2",
            "MistyRose3", "MistyRose4", "azure1", "azure2", "azure3", "azure4",
            "SlateBlue1", "SlateBlue2", "SlateBlue3", "SlateBlue4", "RoyalBlue1",
            "RoyalBlue2", "RoyalBlue3", "RoyalBlue4", "blue1", "blue2", "blue3", "blue4",
            "DodgerBlue1", "DodgerBlue2", "DodgerBlue3", "DodgerBlue4", "SteelBlue1",
            "SteelBlue2", "SteelBlue3", "SteelBlue4", "DeepSkyBlue1", "DeepSkyBlue2",
            "DeepSkyBlue3", "DeepSkyBlue4", "SkyBlue1", "SkyBlue2", "SkyBlue3",
            "SkyBlue4", "LightSkyBlue1", "LightSkyBlue2", "LightSkyBlue3",
            "LightSkyBlue4", "SlateGray1", "SlateGray2", "SlateGray3", "SlateGray4",
            "LightSteelBlue1", "LightSteelBlue2", "LightSteelBlue3",
            "LightSteelBlue4", "LightBlue1", "LightBlue2", "LightBlue3",
            "LightBlue4", "LightCyan1", "LightCyan2", "LightCyan3", "LightCyan4",
            "PaleTurquoise1", "PaleTurquoise2", "PaleTurquoise3", "PaleTurquoise4",
            "CadetBlue1", "CadetBlue2", "CadetBlue3", "CadetBlue4", "turquoise1",
            "turquoise2", "turquoise3", "turquoise4", "cyan1", "cyan2", "cyan3", "cyan4",
            "DarkSlateGray1", "DarkSlateGray2", "DarkSlateGray3",
            "DarkSlateGray4", "aquamarine1", "aquamarine2", "aquamarine3",
            "aquamarine4", "DarkSeaGreen1", "DarkSeaGreen2", "DarkSeaGreen3",
            "DarkSeaGreen4", "SeaGreen1", "SeaGreen2", "SeaGreen3", "SeaGreen4",
            "PaleGreen1", "PaleGreen2", "PaleGreen3", "PaleGreen4", "SpringGreen1",
            "SpringGreen2", "SpringGreen3", "SpringGreen4", "green1", "green2",
            "green3", "green4", "chartreuse1", "chartreuse2", "chartreuse3",
            "chartreuse4", "OliveDrab1", "OliveDrab2", "OliveDrab3", "OliveDrab4",
            "DarkOliveGreen1", "DarkOliveGreen2", "DarkOliveGreen3",
            "DarkOliveGreen4", "khaki1", "khaki2", "khaki3", "khaki4",
            "LightGoldenrod1", "LightGoldenrod2", "LightGoldenrod3",
            "LightGoldenrod4", "LightYellow1", "LightYellow2", "LightYellow3",
            "LightYellow4", "yellow1", "yellow2", "yellow3", "yellow4", "gold1", "gold2",
            "gold3", "gold4", "goldenrod1", "goldenrod2", "goldenrod3", "goldenrod4",
            "DarkGoldenrod1", "DarkGoldenrod2", "DarkGoldenrod3", "DarkGoldenrod4",
            "RosyBrown1", "RosyBrown2", "RosyBrown3", "RosyBrown4", "IndianRed1",
            "IndianRed2", "IndianRed3", "IndianRed4", "sienna1", "sienna2", "sienna3",
            "sienna4", "burlywood1", "burlywood2", "burlywood3", "burlywood4", "wheat1",
            "wheat2", "wheat3", "wheat4", "tan1", "tan2", "tan3", "tan4", "chocolate1",
            "chocolate2", "chocolate3", "chocolate4", "firebrick1", "firebrick2",
            "firebrick3", "firebrick4", "brown1", "brown2", "brown3", "brown4", "salmon1",
            "salmon2", "salmon3", "salmon4", "LightSalmon1", "LightSalmon2",
            "LightSalmon3", "LightSalmon4", "orange1", "orange2", "orange3", "orange4",
            "DarkOrange1", "DarkOrange2", "DarkOrange3", "DarkOrange4", "coral1",
            "coral2", "coral3", "coral4", "tomato1", "tomato2", "tomato3", "tomato4",
            "OrangeRed1", "OrangeRed2", "OrangeRed3", "OrangeRed4", "red1", "red2", "red3",
            "red4", "DeepPink1", "DeepPink2", "DeepPink3", "DeepPink4", "HotPink1",
            "HotPink2", "HotPink3", "HotPink4", "pink1", "pink2", "pink3", "pink4",
            "LightPink1", "LightPink2", "LightPink3", "LightPink4", "PaleVioletRed1",
            "PaleVioletRed2", "PaleVioletRed3", "PaleVioletRed4", "maroon1",
            "maroon2", "maroon3", "maroon4", "VioletRed1", "VioletRed2", "VioletRed3",
            "VioletRed4", "magenta1", "magenta2", "magenta3", "magenta4", "orchid1",
            "orchid2", "orchid3", "orchid4", "plum1", "plum2", "plum3", "plum4",
            "MediumOrchid1", "MediumOrchid2", "MediumOrchid3", "MediumOrchid4",
            "DarkOrchid1", "DarkOrchid2", "DarkOrchid3", "DarkOrchid4", "purple1",
            "purple2", "purple3", "purple4", "MediumPurple1", "MediumPurple2",
            "MediumPurple3", "MediumPurple4", "thistle1", "thistle2", "thistle3",
            "thistle4" )
        #@-node:ekr.20081004172422.668:<< define colors >>
        #@nl

        parent = log.frameDict.get(tabName)
        w = log.textDict.get(tabName)
        w.pack_forget()

        colors = list(colors)
        bg = parent.cget('background')

        outer = qt.Frame(parent,background=bg)
        outer.pack(side='top',fill='both',expand=1,pady=10)

        f = qt.Frame(outer)
        f.pack(side='top',expand=0,fill='x')
        f1 = qt.Frame(f) ; f1.pack(side='top',expand=0,fill='x')
        f2 = qt.Frame(f) ; f2.pack(side='top',expand=1,fill='x')
        f3 = qt.Frame(f) ; f3.pack(side='top',expand=1,fill='x')

        label = g.app.gui.plainTextWidget(f1,height=1,width=20)
        label.insert('1.0','Color name or value...')
        label.pack(side='left',pady=6)

        #@    << create optionMenu and callback >>
        #@+node:ekr.20081004172422.669:<< create optionMenu and callback >>
        colorBox = Pmw.ComboBox(f2,scrolledlist_items=colors)
        colorBox.pack(side='left',pady=4)

        def colorCallback (newName): 
            label.delete('1.0','end')
            label.insert('1.0',newName)
            try:
                for theFrame in (parent,outer,f,f1,f2,f3):
                    theFrame.configure(background=newName)
            except: pass # Ignore invalid names.

        colorBox.configure(selectioncommand=colorCallback)
        #@-node:ekr.20081004172422.669:<< create optionMenu and callback >>
        #@nl
        #@    << create picker button and callback >>
        #@+node:ekr.20081004172422.670:<< create picker button and callback >>
        def pickerCallback ():

            return ###

            rgb,val = tkColorChooser.askcolor(parent=parent,initialcolor=f.cget('background'))
            if rgb or val:
                # label.configure(text=val)
                label.delete('1.0','end')
                label.insert('1.0',val)
                for theFrame in (parent,outer,f,f1,f2,f3):
                    theFrame.configure(background=val)

        b = qt.Button(f3,text="Color Picker...",
            command=pickerCallback,background=bg)
        b.pack(side='left',pady=4)
        #@-node:ekr.20081004172422.670:<< create picker button and callback >>
        #@nl
    #@-node:ekr.20081004172422.667:qtLog color tab stuff
    #@+node:ekr.20081004172422.671:qtLog font tab stuff
    #@+node:ekr.20081004172422.672:createFontPicker
    def createFontPicker (self,tabName):

        return ###

        log = self ; c = self.c
        parent = log.frameDict.get(tabName)
        w = log.textDict.get(tabName)
        w.pack_forget()

        bg = parent.cget('background')
        font = self.getFont()
        #@    << create the frames >>
        #@+node:ekr.20081004172422.673:<< create the frames >>
        f = qt.Frame(parent,background=bg) ; f.pack (side='top',expand=0,fill='both')
        f1 = qt.Frame(f,background=bg)     ; f1.pack(side='top',expand=1,fill='x')
        f2 = qt.Frame(f,background=bg)     ; f2.pack(side='top',expand=1,fill='x')
        f3 = qt.Frame(f,background=bg)     ; f3.pack(side='top',expand=1,fill='x')
        f4 = qt.Frame(f,background=bg)     ; f4.pack(side='top',expand=1,fill='x')
        #@-node:ekr.20081004172422.673:<< create the frames >>
        #@nl
        #@    << create the family combo box >>
        #@+node:ekr.20081004172422.674:<< create the family combo box >>
        names = tkFont.families()
        names = list(names)
        names.sort()
        names.insert(0,'<None>')

        self.familyBox = familyBox = Pmw.ComboBox(f1,
            labelpos="we",label_text='Family:',label_width=10,
            label_background=bg,
            arrowbutton_background=bg,
            scrolledlist_items=names)

        familyBox.selectitem(0)
        familyBox.pack(side="left",padx=2,pady=2)
        #@-node:ekr.20081004172422.674:<< create the family combo box >>
        #@nl
        #@    << create the size entry >>
        #@+node:ekr.20081004172422.675:<< create the size entry >>
        qt.Label(f2,text="Size:",width=10,background=bg).pack(side="left")

        sizeEntry = qt.Entry(f2,width=4)
        sizeEntry.insert(0,'12')
        sizeEntry.pack(side="left",padx=2,pady=2)
        #@-node:ekr.20081004172422.675:<< create the size entry >>
        #@nl
        #@    << create the weight combo box >>
        #@+node:ekr.20081004172422.676:<< create the weight combo box >>
        weightBox = Pmw.ComboBox(f3,
            labelpos="we",label_text="Weight:",label_width=10,
            label_background=bg,
            arrowbutton_background=bg,
            scrolledlist_items=['normal','bold'])

        weightBox.selectitem(0)
        weightBox.pack(side="left",padx=2,pady=2)
        #@-node:ekr.20081004172422.676:<< create the weight combo box >>
        #@nl
        #@    << create the slant combo box >>
        #@+node:ekr.20081004172422.677:<< create the slant combo box>>
        slantBox = Pmw.ComboBox(f4,
            labelpos="we",label_text="Slant:",label_width=10,
            label_background=bg,
            arrowbutton_background=bg,
            scrolledlist_items=['roman','italic'])

        slantBox.selectitem(0)
        slantBox.pack(side="left",padx=2,pady=2)
        #@-node:ekr.20081004172422.677:<< create the slant combo box>>
        #@nl
        #@    << create the sample text widget >>
        #@+node:ekr.20081004172422.678:<< create the sample text widget >>
        self.sampleWidget = sample = g.app.gui.plainTextWidget(f,height=20,width=80,font=font)
        sample.pack(side='left')

        s = 'The quick brown fox\njumped over the lazy dog.\n0123456789'
        sample.insert(0,s)
        #@-node:ekr.20081004172422.678:<< create the sample text widget >>
        #@nl
        #@    << create and bind the callbacks >>
        #@+node:ekr.20081004172422.679:<< create and bind the callbacks >>
        def fontCallback(event=None):
            self.setFont(familyBox,sizeEntry,slantBox,weightBox,sample)

        for w in (familyBox,slantBox,weightBox):
            w.configure(selectioncommand=fontCallback)

        c.bind(sizeEntry,'<Return>',fontCallback)
        #@-node:ekr.20081004172422.679:<< create and bind the callbacks >>
        #@nl
        self.createBindings()
    #@-node:ekr.20081004172422.672:createFontPicker
    #@+node:ekr.20081004172422.680:createBindings (fontPicker)
    def createBindings (self):

        c = self.c ; k = c.k

        table = (
            ('<Button-1>',  k.masterClickHandler),
            ('<Double-1>',  k.masterClickHandler),
            ('<Button-3>',  k.masterClickHandler),
            ('<Double-3>',  k.masterClickHandler),
            ('<Key>',       k.masterKeyHandler),
            ("<Escape>",    self.hideFontTab),
        )

        w = self.sampleWidget
        for event, callback in table:
            c.bind(w,event,callback)

        k.completeAllBindingsForWidget(w)
    #@-node:ekr.20081004172422.680:createBindings (fontPicker)
    #@+node:ekr.20081004172422.681:getFont
    def getFont(self,family=None,size=12,slant='roman',weight='normal'):

        return g.app.config.defaultFont ###

        try:
            return tkFont.Font(family=family,size=size,slant=slant,weight=weight)
        except Exception:
            g.es("exception setting font")
            g.es('','family,size,slant,weight:','',family,'',size,'',slant,'',weight)
            # g.es_exception() # This just confuses people.
            return g.app.config.defaultFont
    #@-node:ekr.20081004172422.681:getFont
    #@+node:ekr.20081004172422.682:setFont
    def setFont(self,familyBox,sizeEntry,slantBox,weightBox,label):

        d = {}
        for box,key in (
            (familyBox, 'family'),
            (None,      'size'),
            (slantBox,  'slant'),
            (weightBox, 'weight'),
        ):
            if box: val = box.get()
            else:
                val = sizeEntry.get().strip() or ''
                try: int(val)
                except ValueError: val = None
            if val and val.lower() not in ('none','<none>',):
                d[key] = val

        family=d.get('family',None)
        size=d.get('size',12)
        weight=d.get('weight','normal')
        slant=d.get('slant','roman')
        font = self.getFont(family,size,slant,weight)
        label.configure(font=font)
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
#@+node:ekr.20081004172422.856:class leoQtMenu
class leoQtMenu (leoMenu.leoMenu):

    #@    @+others
    #@+node:ekr.20081004172422.858:leoQtMenu.__init__
    def __init__ (self,frame):

        assert frame
        assert frame.c

        # Init the base class.
        leoMenu.leoMenu.__init__(self,frame)

        self.frame = frame
        self.c = c = frame.c
        self.leo_label = '<no leo_label>'

        self.menuBar = c.frame.top.menubar
        assert self.menuBar

        # if not wrapper: self.menuBar.addMenu('File')

        if 0:
            self.font = c.config.getFontFromParams(
                'menu_text_font_family', 'menu_text_font_size',
                'menu_text_font_slant',  'menu_text_font_weight',
                c.config.defaultMenuFontSize)
    #@-node:ekr.20081004172422.858:leoQtMenu.__init__
    #@+node:ekr.20081006073635.35:leoQtMenu.__repr__
    #@-node:ekr.20081006073635.35:leoQtMenu.__repr__
    #@+node:ekr.20081004172422.859:Activate menu commands
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
    #@-node:ekr.20081004172422.859:Activate menu commands
    #@+node:ekr.20081004172422.862:Tkinter menu bindings
    # See the Tk docs for what these routines are to do
    #@+node:ekr.20081004172422.863:Methods with Tk spellings
    #@+node:ekr.20081004172422.864:add_cascade
    def add_cascade (self,parent,label,menu,underline):

        """Wrapper for the Tkinter add_cascade menu method.

        Adds a submenu to the parent menu, or the menubar."""

        c = self.c ; leoFrame = c.frame

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

        label = keys.get('label')
        command = keys.get('command')
        underline = keys.get('underline')

        menu = keys.get('menu') or self

        if label:
            action = menu.addAction(label)
            if command:
                def add_command_callback(label=label,command=command):
                    g.trace(label,command)
                    command()

                QtCore.QObject.connect(
                    action,QtCore.SIGNAL("triggered()"),add_command_callback)
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

        #g.trace(menuName,position,label,command)

        menu = self.getMenu(menuName)
        if menu and label:
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

        # try:
            # index = menu.index(name)
        # except:
            # index = None

        # return index
    #@-node:ekr.20081004172422.880:getMenuLabel
    #@+node:ekr.20081004172422.881:setMenuLabel
    def setMenuLabel (self,menu,name,label,underline=-1):

        if not menu:
            return

        # try:
            # if type(name) == type(0):
                # # "name" is actually an index into the menu.
                # menu.entryconfig(name,label=label,underline=underline)
            # else:
                # # Bug fix: 2/16/03: use translated name.
                # realName = self.getRealMenuName(name)
                # realName = realName.replace("&","")
                # # Bug fix: 3/25/03" use tranlasted label.
                # label = self.getRealMenuName(label)
                # label = label.replace("&","")
                # menu.entryconfig(realName,label=label,underline=underline)
        # except:
            # if not g.app.unitTesting:
                # g.pr("setMenuLabel menu,name,label:",menu,name,label)
                # g.es_exception()
    #@-node:ekr.20081004172422.881:setMenuLabel
    #@-node:ekr.20081004172422.874:Methods with other spellings (Qtmenu)
    #@-node:ekr.20081004172422.862:Tkinter menu bindings
    #@+node:ekr.20081004172422.882:getMacHelpMenu
    def getMacHelpMenu (self,table):

        return None ###

        defaultTable = [
                # &: a,b,c,d,e,f,h,l,m,n,o,p,r,s,t,u
                ('&About Leo...',           'about-leo'),
                ('Online &Home Page',       'open-online-home'),
                '*open-online-&tutorial',
                '*open-&users-guide',
                '-',
                ('Open Leo&Docs.leo',       'open-leoDocs-leo'),
                ('Open Leo&Plugins.leo',    'open-leoPlugins-leo'),
                ('Open Leo&Settings.leo',   'open-leoSettings-leo'),
                ('Open &myLeoSettings.leo', 'open-myLeoSettings-leo'),
                ('Open scr&ipts.leo',       'open-scripts-leo'),
                '-',
                '*he&lp-for-minibuffer',
                '*help-for-&command',
                '-',
                '*&apropos-autocompletion',
                '*apropos-&bindings',
                '*apropos-&debugging-commands',
                '*apropos-&find-commands',
                '-',
                '*pri&nt-bindings',
                '*print-c&ommands',
            ]

        try:
            topMenu = self.getMenu('top')
            # Use the name argument to create the special Macintosh Help menu.
            helpMenu = Tk.Menu(topMenu,name='help',tearoff=0)
            self.add_cascade(topMenu,label='Help',menu=helpMenu,underline=0)
            self.createMenuEntries(helpMenu,table or defaultTable)
            return helpMenu

        except Exception:
            g.trace('Can not get MacOS Help menu')
            g.es_exception()
            return None
    #@-node:ekr.20081004172422.882:getMacHelpMenu
    #@-others
#@-node:ekr.20081004172422.856:class leoQtMenu
#@+node:ekr.20081004172422.694:class leoQtTextWidget
class leoQtTextWidget:

    '''A class to wrap the qt text widget.'''

    def __repr__(self):
        name = hasattr(self,'_name') and self._name or '<no name>'
        return 'leoQtTextWidget id: %s name: %s' % (id(self),name)

    #@    @+others
    #@+node:ekr.20081004172422.695:bindings (not used)
    # Specify the names of widget-specific methods.
    # These particular names are the names of wx.TextCtrl methods.

    # def _appendText(self,s):            return self.widget.insert(s)
    # def _get(self,i,j):                 return self.widget.get(i,j)
    # def _getAllText(self):              return self.widget.get('1.0','end')
    # def _getFocus(self):                return self.widget.focus_get()
    # def _getInsertPoint(self):          return self.widget.index('insert')
    # def _getLastPosition(self):         return self.widget.index('end')
    # def _getSelectedText(self):         return self.widget.get('sel.start','sel.end')
    # def _getSelectionRange(self):       return self.widget.index('sel.start'),self.widget.index('sel.end')
    # def _hitTest(self,pos):             pass
    # def _insertText(self,i,s):          return self.widget.insert(i,s)
    # def _scrollLines(self,n):           pass
    # def _see(self,i):                   return self.widget.see(i)
    # def _setAllText(self,s):            self.widget.delete('1.0','end') ; self.widget.insert('1.0',s)
    # def _setBackgroundColor(self,color): return self.widget.configure(background=color)
    # def _setForegroundColor(self,color): return self.widget.configure(background=color)
    # def _setFocus(self):                return self.widget.focus_set()
    # def _setInsertPoint(self,i):        return self.widget.mark_set('insert',i)
    # def _setSelectionRange(self,i,j):   return self.widget.SetSelection(i,j)
    #@-node:ekr.20081004172422.695:bindings (not used)
    #@+node:ekr.20081004172422.696:Index conversion (leoTextWidget)
    #@+node:ekr.20081004172422.697:w.toGuiIndex
    def toGuiIndex (self,i,s=None):

        '''Convert a Python index to a Qt index.'''

        return i


        # w = self
        # if i is None:
            # g.trace('can not happen: i is None',g.callers())
            # return '1.0'
        # elif type(i) == type(99):
            # # The 's' arg supports the threaded colorizer.
            # if s is None:
                # # This *must* be 'end-1c', even if other code must change.
                # s = Tk.Text.get(w,'1.0','end-1c')
            # row,col = g.convertPythonIndexToRowCol(s,i)
            # i = '%s.%s' % (row+1,col)
            # # g.trace(len(s),i,repr(s))
        # else:
            # try:
                # i = Tk.Text.index(w,i)
            # except Exception:
                # # g.es_exception()
                # g.trace('Tk.Text.index failed:',repr(i),g.callers())
                # i = '1.0'
        # return i
    #@-node:ekr.20081004172422.697:w.toGuiIndex
    #@+node:ekr.20081004172422.698:w.toPythonIndex
    def toPythonIndex (self,i):

        '''Convert a Qt index to a Python index.'''

        return i

        # w =self
        # if i is None:
            # g.trace('can not happen: i is None')
            # return 0

        # elif type(i) in (type('a'),type(u'a')):
            # s = Tk.Text.get(w,'1.0','end') # end-1c does not work.
            # i = Tk.Text.index(w,i) # Convert to row/column form.
            # row,col = i.split('.')
            # row,col = int(row),int(col)
            # row -= 1
            # i = g.convertRowColToPythonIndex(s,row,col)
            # #g.es_print('',i)
        # return i
    #@-node:ekr.20081004172422.698:w.toPythonIndex
    #@+node:ekr.20081004172422.699:w.rowColToGuiIndex
    # This method is called only from the colorizer.
    # It provides a huge speedup over naive code.

    def rowColToGuiIndex (self,s,row,col):

        return '%s.%s' % (row+1,col)
    #@nonl
    #@-node:ekr.20081004172422.699:w.rowColToGuiIndex
    #@-node:ekr.20081004172422.696:Index conversion (leoTextWidget)
    #@+node:ekr.20081004172422.700:Wrapper methods (leoTextWidget)
    #@+node:ekr.20081004172422.701:delete
    def delete(self,i,j=None):

        w = self
        i = w.toGuiIndex(i)

        if j is None:
            qt.Text.delete(w,i)
        else:
            j = w.toGuiIndex(j)
            qt.Text.delete(w,i,j)
    #@-node:ekr.20081004172422.701:delete
    #@+node:ekr.20081004172422.702:flashCharacter
    def flashCharacter(self,i,bg='white',fg='red',flashes=3,delay=75): # qtTextWidget.

        w = self

        def addFlashCallback(w,count,index):
            # g.trace(count,index)
            i,j = w.toGuiIndex(index),w.toGuiIndex(index+1)
            qt.Text.tag_add(w,'flash',i,j)
            qt.Text.after(w,delay,removeFlashCallback,w,count-1,index)

        def removeFlashCallback(w,count,index):
            # g.trace(count,index)
            qt.Text.tag_remove(w,'flash','1.0','end')
            if count > 0:
                qt.Text.after(w,delay,addFlashCallback,w,count,index)

        try:
            qt.Text.tag_configure(w,'flash',foreground=fg,background=bg)
            addFlashCallback(w,flashes,i)
        except Exception:
            pass # g.es_exception()
    #@nonl
    #@-node:ekr.20081004172422.702:flashCharacter
    #@+node:ekr.20081004172422.703:get
    def get(self,i,j=None):

        w = self
        i = w.toGuiIndex(i)

        if j is None:
            return qt.Text.get(w,i)
        else:
            j = w.toGuiIndex(j)
            return qt.Text.get(w,i,j)
    #@-node:ekr.20081004172422.703:get
    #@+node:ekr.20081004172422.704:getAllText
    def getAllText (self): # qtTextWidget.

        """Return all the text of qt.Text widget w converted to unicode."""

        w = self
        s = qt.Text.get(w,"1.0","end-1c") # New in 4.4.1: use end-1c.

        if s is None:
            return u""
        else:
            return g.toUnicode(s,g.app.tkEncoding)
    #@-node:ekr.20081004172422.704:getAllText
    #@+node:ekr.20081004172422.705:getInsertPoint
    def getInsertPoint(self): # qtTextWidget.

        w = self
        i = qt.Text.index(w,'insert')
        i = w.toPythonIndex(i)
        return i
    #@-node:ekr.20081004172422.705:getInsertPoint
    #@+node:ekr.20081004172422.706:getName
    def getName (self):

        w = self
        return hasattr(w,'_name') and w._name or repr(w)
    #@nonl
    #@-node:ekr.20081004172422.706:getName
    #@+node:ekr.20081004172422.707:getSelectedText
    def getSelectedText (self): # qtTextWidget.

        w = self
        i,j = w.getSelectionRange()
        if i != j:
            i,j = w.toGuiIndex(i),w.toGuiIndex(j)
            s = qt.Text.get(w,i,j)
            return g.toUnicode(s,g.app.tkEncoding)
        else:
            return u""
    #@-node:ekr.20081004172422.707:getSelectedText
    #@+node:ekr.20081004172422.708:getSelectionRange
    def getSelectionRange (self,sort=True): # qtTextWidget.

        """Return a tuple representing the selected range.

        Return a tuple giving the insertion point if no range of text is selected."""

        w = self
        sel = qt.Text.tag_ranges(w,"sel")
        if len(sel) == 2:
            i,j = sel
        else:
            i = j = qt.Text.index(w,"insert")

        i,j = w.toPythonIndex(i),w.toPythonIndex(j)  
        if sort and i > j: i,j = j,i
        return i,j
    #@nonl
    #@-node:ekr.20081004172422.708:getSelectionRange
    #@+node:ekr.20081004172422.709:getWidth
    def getWidth (self):

        '''Return the width of the widget.
        This is only called for headline widgets,
        and gui's may choose not to do anything here.'''

        w = self
        return w.cget('width')
    #@-node:ekr.20081004172422.709:getWidth
    #@+node:ekr.20081004172422.710:getYScrollPosition
    def getYScrollPosition (self):

        w = self
        return w.yview()
    #@-node:ekr.20081004172422.710:getYScrollPosition
    #@+node:ekr.20081004172422.711:hasSelection
    def hasSelection (self):

        w = self
        i,j = w.getSelectionRange()
        return i != j
    #@-node:ekr.20081004172422.711:hasSelection
    #@+node:ekr.20081004172422.712:indexIsVisible
    def indexIsVisible (self,i):

        w = self

        return w.dlineinfo(i)
    #@nonl
    #@-node:ekr.20081004172422.712:indexIsVisible
    #@+node:ekr.20081004172422.713:insert
    # The signature is more restrictive than the qt.Text.insert method.

    def insert(self,i,s):

        w = self
        i = w.toGuiIndex(i)
        qt.Text.insert(w,i,s)

    #@-node:ekr.20081004172422.713:insert
    #@+node:ekr.20081004172422.714:mark_set NO LONGER USED
    # def mark_set(self,markName,i):

        # w = self
        # i = w.toGuiIndex(i)
        # qt.Text.mark_set(w,markName,i)
    #@-node:ekr.20081004172422.714:mark_set NO LONGER USED
    #@+node:ekr.20081004172422.715:replace
    def replace (self,i,j,s): # qtTextWidget

        w = self
        i,j = w.toGuiIndex(i),w.toGuiIndex(j)

        qt.Text.delete(w,i,j)
        qt.Text.insert(w,i,s)
    #@-node:ekr.20081004172422.715:replace
    #@+node:ekr.20081004172422.716:see
    def see (self,i): # qtTextWidget.

        w = self
        i = w.toGuiIndex(i)
        qt.Text.see(w,i)
    #@-node:ekr.20081004172422.716:see
    #@+node:ekr.20081004172422.717:seeInsertPoint
    def seeInsertPoint (self): # qtTextWidget.

        w = self
        qt.Text.see(w,'insert')
    #@-node:ekr.20081004172422.717:seeInsertPoint
    #@+node:ekr.20081004172422.718:selectAllText
    def selectAllText (self,insert=None): # qtTextWidget

        '''Select all text of the widget, *not* including the extra newline.'''

        w = self ; s = w.getAllText()
        if insert is None: insert = len(s)
        w.setSelectionRange(0,len(s),insert=insert)
    #@-node:ekr.20081004172422.718:selectAllText
    #@+node:ekr.20081004172422.719:setAllText
    def setAllText (self,s): # qtTextWidget

        w = self

        state = qt.Text.cget(w,"state")
        qt.Text.configure(w,state="normal")

        qt.Text.delete(w,'1.0','end')
        if s: qt.Text.insert(w,'1.0',s) # The 'if s:' is a workaround for a fedora bug.

        qt.Text.configure(w,state=state)
    #@-node:ekr.20081004172422.719:setAllText
    #@+node:ekr.20081004172422.720:setBackgroundColor & setForegroundColor
    def setBackgroundColor (self,color):

        w = self
        w.configure(background=color)

    def setForegroundColor (self,color):

        w = self
        w.configure(foreground=color)
    #@nonl
    #@-node:ekr.20081004172422.720:setBackgroundColor & setForegroundColor
    #@+node:ekr.20081004172422.721:setInsertPoint
    def setInsertPoint (self,i): # qtTextWidget.

        w = self
        i = w.toGuiIndex(i)
        # g.trace(i,g.callers())
        qt.Text.mark_set(w,'insert',i)
    #@-node:ekr.20081004172422.721:setInsertPoint
    #@+node:ekr.20081004172422.722:setSelectionRange
    def setSelectionRange (self,i,j,insert=None): # qtTextWidget

        w = self

        i,j = w.toGuiIndex(i),w.toGuiIndex(j)

        # g.trace('i,j,insert',repr(i),repr(j),repr(insert),g.callers())

        # g.trace('i,j,insert',i,j,repr(insert))
        if qt.Text.compare(w,i, ">", j): i,j = j,i
        qt.Text.tag_remove(w,"sel","1.0",i)
        qt.Text.tag_add(w,"sel",i,j)
        qt.Text.tag_remove(w,"sel",j,"end")

        if insert is not None:
            w.setInsertPoint(insert)
    #@-node:ekr.20081004172422.722:setSelectionRange
    #@+node:ekr.20081004172422.723:setWidth
    def setWidth (self,width):

        '''Set the width of the widget.
        This is only called for headline widgets,
        and gui's may choose not to do anything here.'''

        w = self
        w.configure(width=width)
    #@-node:ekr.20081004172422.723:setWidth
    #@+node:ekr.20081004172422.724:setYScrollPosition
    def setYScrollPosition (self,i):

        w = self
        w.yview('moveto',i)
    #@nonl
    #@-node:ekr.20081004172422.724:setYScrollPosition
    #@+node:ekr.20081004172422.725:tag_add
    # The signature is slightly different than the qt.Text.insert method.

    def tag_add(self,tagName,i,j=None,*args):

        w = self
        i = w.toGuiIndex(i)

        if j is None:
            qt.Text.tag_add(w,tagName,i,*args)
        else:
            j = w.toGuiIndex(j)
            qt.Text.tag_add(w,tagName,i,j,*args)

    #@-node:ekr.20081004172422.725:tag_add
    #@+node:ekr.20081004172422.726:tag_ranges
    def tag_ranges(self,tagName):

        w = self
        aList = qt.Text.tag_ranges(w,tagName)
        aList = [w.toPythonIndex(z) for z in aList]
        return tuple(aList)
    #@-node:ekr.20081004172422.726:tag_ranges
    #@+node:ekr.20081004172422.727:tag_remove
    # The signature is slightly different than the qt.Text.insert method.

    def tag_remove (self,tagName,i,j=None,*args):

        w = self
        i = w.toGuiIndex(i)

        if j is None:
            qt.Text.tag_remove(w,tagName,i,*args)
        else:
            j = w.toGuiIndex(j)
            qt.Text.tag_remove(w,tagName,i,j,*args)


    #@-node:ekr.20081004172422.727:tag_remove
    #@+node:ekr.20081004172422.728:w.deleteTextSelection
    def deleteTextSelection (self): # qtTextWidget

        w = self
        sel = qt.Text.tag_ranges(w,"sel")
        if len(sel) == 2:
            start,end = sel
            if qt.Text.compare(w,start,"!=",end):
                qt.Text.delete(w,start,end)
    #@-node:ekr.20081004172422.728:w.deleteTextSelection
    #@+node:ekr.20081004172422.729:xyToGui/PythonIndex
    def xyToGuiIndex (self,x,y): # qtTextWidget

        w = self
        return qt.Text.index(w,"@%d,%d" % (x,y))

    def xyToPythonIndex(self,x,y): # qtTextWidget

        w = self
        i = qt.Text.index(w,"@%d,%d" % (x,y))
        i = w.toPythonIndex(i)
        return i
    #@-node:ekr.20081004172422.729:xyToGui/PythonIndex
    #@-node:ekr.20081004172422.700:Wrapper methods (leoTextWidget)
    #@-others
#@nonl
#@-node:ekr.20081004172422.694:class leoQtTextWidget
#@+node:ekr.20081004172422.732:class leoQtTree
class leoQtTree (leoFrame.leoTree):

    """Leo qt tree class."""

    callbacksInjected = False

    #@    @+others
    #@+node:ekr.20081004172422.737: Birth... (qt Tree)
    #@+node:ekr.20081004172422.738:__init__ (qtTree)
    def __init__(self,c,frame): # ,canvas):

        # Init the base class.
        leoFrame.leoTree.__init__(self,frame)

        # Configuration and debugging settings.
        # These must be defined here to eliminate memory leaks.
        self.allow_clone_drags          = c.config.getBool('allow_clone_drags')
        self.center_selected_tree_node  = c.config.getBool('center_selected_tree_node')
        self.enable_drag_messages       = c.config.getBool("enable_drag_messages")
        self.expanded_click_area        = c.config.getBool('expanded_click_area')
        self.gc_before_redraw           = c.config.getBool('gc_before_redraw')

        self.headline_text_editing_foreground_color = c.config.getColor(
            'headline_text_editing_foreground_color')
        self.headline_text_editing_background_color = c.config.getColor(
            'headline_text_editing_background_color')
        self.headline_text_editing_selection_foreground_color = c.config.getColor(
            'headline_text_editing_selection_foreground_color')
        self.headline_text_editing_selection_background_color = c.config.getColor(
            'headline_text_editing_selection_background_color')
        self.headline_text_selected_foreground_color = c.config.getColor(
            "headline_text_selected_foreground_color")
        self.headline_text_selected_background_color = c.config.getColor(
            "headline_text_selected_background_color")
        self.headline_text_editing_selection_foreground_color = c.config.getColor(
            "headline_text_editing_selection_foreground_color")
        self.headline_text_editing_selection_background_color = c.config.getColor(
            "headline_text_editing_selection_background_color")
        self.headline_text_unselected_foreground_color = c.config.getColor(
            'headline_text_unselected_foreground_color')
        self.headline_text_unselected_background_color = c.config.getColor(
            'headline_text_unselected_background_color')

        self.idle_redraw = c.config.getBool('idle_redraw')
        self.initialClickExpandsOrContractsNode = c.config.getBool(
            'initialClickExpandsOrContractsNode')
        self.look_for_control_drag_on_mouse_down = c.config.getBool(
            'look_for_control_drag_on_mouse_down')
        self.select_all_text_when_editing_headlines = c.config.getBool(
            'select_all_text_when_editing_headlines')

        self.stayInTree     = c.config.getBool('stayInTreeAfterSelect')
        self.trace          = c.config.getBool('trace_tree')
        self.trace_alloc    = c.config.getBool('trace_tree_alloc')
        self.trace_chapters = c.config.getBool('trace_chapters')
        self.trace_edit     = c.config.getBool('trace_tree_edit')
        self.trace_gc       = c.config.getBool('trace_tree_gc')
        self.trace_redraw   = c.config.getBool('trace_tree_redraw')
        self.trace_select   = c.config.getBool('trace_select')
        self.trace_stats    = c.config.getBool('show_tree_stats')
        self.use_chapters   = c.config.getBool('use_chapters')

        return ###

        # Objects associated with this tree.
        self.canvas = canvas

        #@    << define drawing constants >>
        #@+node:ekr.20081004172422.739:<< define drawing constants >>
        self.box_padding = 5 # extra padding between box and icon
        self.box_width = 9 + self.box_padding
        self.icon_width = 20
        self.text_indent = 4 # extra padding between icon and tex

        self.hline_y = 7 # Vertical offset of horizontal line
        self.root_left = 7 + self.box_width
        self.root_top = 2

        self.default_line_height = 17 + 2 # default if can't set line_height from font.
        self.line_height = self.default_line_height
        #@-node:ekr.20081004172422.739:<< define drawing constants >>
        #@nl
        #@    << old ivars >>
        #@+node:ekr.20081004172422.740:<< old ivars >>
        # Miscellaneous info.
        self.iconimages = {} # Image cache set by getIconImage().
        self.active = False # True if present headline is active
        self._editPosition = None # Returned by leoTree.editPosition()
        self.lineyoffset = 0 # y offset for this headline.
        self.lastClickFrameId = None # id of last entered clickBox.
        self.lastColoredText = None # last colored text widget.

        # Set self.font and self.fontName.
        self.setFontFromConfig()

        # Drag and drop
        self.drag_p = None
        self.controlDrag = False # True: control was down when drag started.

        # Keep track of popup menu so we can handle behavior better on Linux Context menu
        self.popupMenu = None

        # Incremental redraws:
        self.allocateOnlyVisibleNodes = False # True: enable incremental redraws.
        self.prevMoveToFrac = 0.0
        self.visibleArea = None
        self.expandedVisibleArea = None

        if self.allocateOnlyVisibleNodes:
            c.bind(self.frame.bar1,"<Button-1-ButtonRelease>", self.redraw_now)
        #@-node:ekr.20081004172422.740:<< old ivars >>
        #@nl
        #@    << inject callbacks into the position class >>
        #@+node:ekr.20081004172422.741:<< inject callbacks into the position class >>
        # The new code injects 3 callbacks for the colorizer.

        if not leoQtinterTree.callbacksInjected: # Class var.
            leoQtinterTree.callbacksInjected = True
            self.injectCallbacks()
        #@-node:ekr.20081004172422.741:<< inject callbacks into the position class >>
        #@nl

        self.dragging = False
        self.generation = 0
        self.prevPositions = 0
        self.redrawing = False # Used only to disable traces.
        self.redrawCount = 0 # Count for debugging.
        self.revertHeadline = None # Previous headline text for abortEditLabel.

        # New in 4.4: We should stay in the tree to use per-pane bindings.
        self.textBindings = [] # Set in setBindings.
        self.textNumber = 0 # To make names unique.
        self.updateCount = 0 # Drawing is enabled only if self.updateCount <= 0
        self.verbose = True

        self.setEditPosition(None) # Set positions returned by leoTree.editPosition()

        # Keys are id's, values are positions...
        self.ids = {}
        self.iconIds = {}

        # Lists of visible (in-use) widgets...
        self.visibleBoxes = []
        self.visibleClickBoxes = []
        self.visibleIcons = []
        self.visibleLines = []
        self.visibleText  = {}
            # Pre 4.4b2: Keys are vnodes, values are Qt.Text widgets.
            #     4.4b2: Keys are p.key(), values are Qt.Text widgets.
        self.visibleUserIcons = []

        # Dictionaries of free, hidden widgets...
        # Keys are id's, values are widgets.
        self.freeBoxes = {}
        self.freeClickBoxes = {}
        self.freeIcons = {}
        self.freeLines = {}
        self.freeText = {} # New in 4.4b2: a list of free Qt.Text widgets

        self.freeUserIcons = {}

        self._block_canvas_menu = False
    #@-node:ekr.20081004172422.738:__init__ (qtTree)
    #@+node:ekr.20081004172422.742:qtTtree.setBindings & helper
    def setBindings (self):

        '''Create master bindings for all headlines.'''

        return ###

        tree = self ; k = self.c.k

        # g.trace('self',self,'canvas',self.canvas)

        tree.setBindingsHelper()

        tree.setCanvasBindings(self.canvas)

        k.completeAllBindingsForWidget(self.canvas)

        k.completeAllBindingsForWidget(self.bindingWidget)

    #@+node:ekr.20081004172422.743:qtTree.setBindingsHelper
    def setBindingsHelper (self):

        tree = self ; c = tree.c ; k = c.k

        self.bindingWidget = w = g.app.gui.plainTextWidget(
            self.canvas,name='bindingWidget')

        c.bind(w,'<Key>',k.masterKeyHandler)

        table = [
            ('<Button-1>',       k.masterClickHandler,          tree.onHeadlineClick),
            ('<Button-3>',       k.masterClick3Handler,         tree.onHeadlineRightClick),
            ('<Double-Button-1>',k.masterDoubleClickHandler,    tree.onHeadlineClick),
            ('<Double-Button-3>',k.masterDoubleClick3Handler,   tree.onHeadlineRightClick),
        ]

        for a,handler,func in table:
            def treeBindingCallback(event,handler=handler,func=func):
                # g.trace('func',func)
                return handler(event,func)
            c.bind(w,a,treeBindingCallback)

        self.textBindings = w.bindtags()
    #@-node:ekr.20081004172422.743:qtTree.setBindingsHelper
    #@-node:ekr.20081004172422.742:qtTtree.setBindings & helper
    #@+node:ekr.20081004172422.744:qtTree.setCanvasBindings
    def setCanvasBindings (self,canvas):

        c = self.c ; k = c.k

        return ###

        c.bind(canvas,'<Key>',k.masterKeyHandler)
        c.bind(canvas,'<Button-1>',self.onTreeClick)
        c.bind(canvas,'<Button-3>',self.onTreeRightClick)
        # c.bind(canvas,'<FocusIn>',self.onFocusIn)

        #@    << make bindings for tagged items on the canvas >>
        #@+node:ekr.20081004172422.745:<< make bindings for tagged items on the canvas >>
        where = g.choose(self.expanded_click_area,'clickBox','plusBox')

        table = (
            (where,    '<Button-1>',self.onClickBoxClick),
            ('iconBox','<Button-1>',self.onIconBoxClick),
            ('iconBox','<Double-1>',self.onIconBoxDoubleClick),
            ('iconBox','<Button-3>',self.onIconBoxRightClick),
            ('iconBox','<Double-3>',self.onIconBoxRightClick),
            ('iconBox','<B1-Motion>',self.onDrag),
            ('iconBox','<Any-ButtonRelease-1>',self.onEndDrag),

            ('plusBox','<Button-3>', self.onPlusBoxRightClick),
            ('plusBox','<Button-1>', self.onClickBoxClick),
            ('clickBox','<Button-3>',  self.onClickBoxRightClick),
        )
        for tag,event_kind,callback in table:
            c.tag_bind(canvas,tag,event_kind,callback)
        #@-node:ekr.20081004172422.745:<< make bindings for tagged items on the canvas >>
        #@nl
        #@    << create baloon bindings for tagged items on the canvas >>
        #@+node:ekr.20081004172422.746:<< create baloon bindings for tagged items on the canvas >>
        if 0: # I find these very irritating.
            for tag,text in (
                # ('plusBox','plusBox'),
                ('iconBox','Icon Box'),
                ('selectBox','Click to select'),
                ('clickBox','Click to expand or contract'),
                # ('textBox','Headline'),
            ):
                # A fairly long wait is best.
                balloon = Pmw.Balloon(self.canvas,initwait=700)
                balloon.tagbind(self.canvas,tag,balloonHelp=text)
        #@-node:ekr.20081004172422.746:<< create baloon bindings for tagged items on the canvas >>
        #@nl
    #@-node:ekr.20081004172422.744:qtTree.setCanvasBindings
    #@+node:ekr.20081005065934.10:qtTree.initAfterLoad
    def initAfterLoad (self):

        frame = self.c.frame
        frame.top.populate_tree(parent=None)
    #@-node:ekr.20081005065934.10:qtTree.initAfterLoad
    #@-node:ekr.20081004172422.737: Birth... (qt Tree)
    #@+node:ekr.20081004172422.767:tree.redraw_now
    def redraw_now (self,scroll=False,forceDraw=False):

        '''Redraw immediately: used by Find so a redraw doesn't mess up selections in headlines.'''

        pass

    redraw = redraw_now # Compatibility
    #@-node:ekr.20081004172422.767:tree.redraw_now
    #@+node:ekr.20081004172422.758:Config & Measuring...
    #@+node:ekr.20081004172422.759:tree.getFont,setFont,setFontFromConfig
    def getFont (self):

        return self.font

    def setFont (self,font=None, fontName=None):

        return ###

        # ESSENTIAL: retain a link to font.
        if fontName:
            self.fontName = fontName
            self.font = tkFont.Font(font=fontName)
        else:
            self.fontName = None
            self.font = font

        self.setLineHeight(self.font)

    # Called by ctor and when config params are reloaded.
    def setFontFromConfig (self):
        c = self.c
        # g.trace()
        font = c.config.getFontFromParams(
            "headline_text_font_family", "headline_text_font_size",
            "headline_text_font_slant",  "headline_text_font_weight",
            c.config.defaultTreeFontSize)

        self.setFont(font)
    #@-node:ekr.20081004172422.759:tree.getFont,setFont,setFontFromConfig
    #@+node:ekr.20081004172422.760:headWidth & widthInPixels
    def headWidth(self,p=None,s=''):

        """Returns the proper width of the entry widget for the headline."""

        if p: s = p.headString()

        return self.font.measure(s)/self.font.measure('0')+1


    def widthInPixels(self,s):

        s = g.toEncodedString(s,g.app.tkEncoding)

        return self.font.measure(s)
    #@-node:ekr.20081004172422.760:headWidth & widthInPixels
    #@+node:ekr.20081004172422.761:setLineHeight
    def setLineHeight (self,font):

        try:
            metrics = font.metrics()
            linespace = metrics ["linespace"]
            self.line_height = linespace + 5 # Same as before for the default font on Windows.
            # g.pr(metrics)
        except:
            self.line_height = self.default_line_height
            g.es("exception setting outline line height")
            g.es_exception()
    #@-node:ekr.20081004172422.761:setLineHeight
    #@-node:ekr.20081004172422.758:Config & Measuring...
    #@+node:ekr.20081004172422.844:Selecting & editing... (qtTree)
    #@+node:ekr.20081004172422.845:dimEditLabel, undimEditLabel
    # Convenience methods so the caller doesn't have to know the present edit node.

    def dimEditLabel (self):

        p = self.c.currentPosition()
        self.setSelectedLabelState(p)

    def undimEditLabel (self):

        p = self.c.currentPosition()
        self.setSelectedLabelState(p)
    #@-node:ekr.20081004172422.845:dimEditLabel, undimEditLabel
    #@+node:ekr.20081004172422.846:tree.editLabel
    def editLabel (self,p,selectAll=False):

        """Start editing p's headline."""

        c = self.c
        trace = (False or self.trace_edit)

        if p and p != self.editPosition():

            if trace:
                g.trace(p.headString(),g.choose(c.edit_widget(p),'','no edit widget'))

            self.endEditLabel()
            # This redraw *is* required so the c.edit_widget(p) will exist.
            c.redraw()
            c.outerUpdate()

        self.setEditPosition(p) # That is, self._editPosition = p
        w = c.edit_widget(p)

        if trace: g.trace('1','w',w,'focus',g.app.gui.get_focus(c))

        if p and w:
            self.revertHeadline = p.headString() # New in 4.4b2: helps undo.
            self.setEditLabelState(p,selectAll=selectAll) # Sets the focus immediately.
            c.headlineWantsFocus(p) # Make sure the focus sticks.
            c.k.showStateAndMode(w)

        if trace: g.trace('w',w,'focus',g.app.gui.get_focus(c))
    #@-node:ekr.20081004172422.846:tree.editLabel
    #@+node:ekr.20081004172422.847:tree.set...LabelState
    #@+node:ekr.20081004172422.848:setEditLabelState
    def setEditLabelState (self,p,selectAll=False): # selected, editing

        c = self.c ; w = c.edit_widget(p)

        if p and w:
            c.widgetWantsFocusNow(w)
            self.setEditHeadlineColors(p)
            selectAll = selectAll or self.select_all_text_when_editing_headlines
            if selectAll:
                w.setSelectionRange(0,'end',insert='end')
            else:
                w.setInsertPoint('end') # Clears insert point.
        else:
            g.trace('no edit_widget')

    setNormalLabelState = setEditLabelState # For compatibility.
    #@-node:ekr.20081004172422.848:setEditLabelState
    #@+node:ekr.20081004172422.849:setSelectedLabelState
    trace_n = 0

    def setSelectedLabelState (self,p): # selected, disabled

        c = self.c

        # g.trace(p,c.edit_widget(p))


        if p and c.edit_widget(p):

            if 0:
                g.trace(self.trace_n,c.edit_widget(p),p)
                # g.trace(g.callers(6))
                self.trace_n += 1

            self.setDisabledHeadlineColors(p)
    #@-node:ekr.20081004172422.849:setSelectedLabelState
    #@+node:ekr.20081004172422.850:setUnselectedLabelState
    def setUnselectedLabelState (self,p): # not selected.

        c = self.c

        if p and c.edit_widget(p):
            self.setUnselectedHeadlineColors(p)
    #@-node:ekr.20081004172422.850:setUnselectedLabelState
    #@+node:ekr.20081004172422.851:setDisabledHeadlineColors
    def setDisabledHeadlineColors (self,p):

        c = self.c ; w = c.edit_widget(p)

        if False or (self.trace and self.verbose):
            g.trace("%10s %d %s" % ("disabled",id(w),p.headString()))
            # import traceback ; traceback.print_stack(limit=6)

        fg = self.headline_text_selected_foreground_color or 'black'
        bg = self.headline_text_selected_background_color or 'grey80'
        selfg = self.headline_text_editing_selection_foreground_color
        selbg = self.headline_text_editing_selection_background_color

        try:
            w.configure(state="disabled",highlightthickness=0,fg=fg,bg=bg,
                selectbackground=bg,selectforeground=fg,highlightbackground=bg)
        except:
            g.es_exception()
    #@-node:ekr.20081004172422.851:setDisabledHeadlineColors
    #@+node:ekr.20081004172422.852:setEditHeadlineColors
    def setEditHeadlineColors (self,p):

        c = self.c ; w = c.edit_widget(p)

        if self.trace and self.verbose:
            if not self.redrawing:
                g.pr("%10s %d %s" % ("edit",id(2),p.headString()))

        fg    = self.headline_text_editing_foreground_color or 'black'
        bg    = self.headline_text_editing_background_color or 'white'
        selfg = self.headline_text_editing_selection_foreground_color or 'white'
        selbg = self.headline_text_editing_selection_background_color or 'black'

        try: # Use system defaults for selection foreground/background
            w.configure(state="normal",highlightthickness=1,
            fg=fg,bg=bg,selectforeground=selfg,selectbackground=selbg)
        except:
            g.es_exception()
    #@-node:ekr.20081004172422.852:setEditHeadlineColors
    #@+node:ekr.20081004172422.853:setUnselectedHeadlineColors
    def setUnselectedHeadlineColors (self,p):

        c = self.c ; w = c.edit_widget(p)

        if self.trace and self.verbose:
            if not self.redrawing:
                g.pr("%10s %d %s" % ("unselect",id(w),p.headString()))
                # import traceback ; traceback.print_stack(limit=6)

        fg = self.headline_text_unselected_foreground_color or 'black'
        bg = self.headline_text_unselected_background_color or 'white'

        try:
            w.configure(state="disabled",highlightthickness=0,fg=fg,bg=bg,
                selectbackground=bg,selectforeground=fg,highlightbackground=bg)
        except:
            g.es_exception()
    #@-node:ekr.20081004172422.853:setUnselectedHeadlineColors
    #@-node:ekr.20081004172422.847:tree.set...LabelState
    #@+node:ekr.20081004172422.854:tree.setHeadline (qtTree)
    def setHeadline (self,p,s):

        '''Set the actual text of the headline widget.

        This is called from the undo/redo logic to change the text before redrawing.'''

        w = self.edit_widget(p)
        if w:
            w.configure(state='normal')
            w.delete(0,'end')
            if s.endswith('\n') or s.endswith('\r'):
                s = s[:-1]
            w.insert(0,s)
            self.revertHeadline = s
            # g.trace(repr(s),w.getAllText())
        else:
            g.trace('-'*20,'oops')
    #@-node:ekr.20081004172422.854:tree.setHeadline (qtTree)
    #@-node:ekr.20081004172422.844:Selecting & editing... (qtTree)
    #@+node:ekr.20081004172422.795:Event handlers (qtTree)
    #@+node:ekr.20081004172422.796:Helpers
    #@+node:ekr.20081004172422.797:checkWidgetList
    def checkWidgetList (self,tag):

        return True # This will fail when the headline actually changes!
    #@-node:ekr.20081004172422.797:checkWidgetList
    #@+node:ekr.20081004172422.798:dumpWidgetList
    def dumpWidgetList (self,tag):

        g.pr("\ncheckWidgetList: %s" % tag)

        for w in self.visibleText:

            p = w.leo_position
            if p:
                s = w.getAllText().strip()
                h = p.headString().strip()

                addr = self.textAddr(w)
                g.pr("p:",addr,h)
                if h != s:
                    g.pr("w:",'*' * len(addr),s)
            else:
                g.pr("w.leo_position == None",w)
    #@-node:ekr.20081004172422.798:dumpWidgetList
    #@+node:ekr.20081004172422.799:tree.edit_widget
    def edit_widget (self,p):

        """Returns the Qt.Edit widget for position p."""

        return self.findEditWidget(p)
    #@nonl
    #@-node:ekr.20081004172422.799:tree.edit_widget
    #@+node:ekr.20081004172422.800:eventToPosition
    def eventToPosition (self,event):

        canvas = self.canvas
        x,y = event.x,event.y
        x = canvas.canvasx(x) 
        y = canvas.canvasy(y)
        if self.trace: g.trace(x,y)
        item = canvas.find_overlapping(x,y,x,y)
        if not item: return None

        # Item may be a tuple, possibly empty.
        try:    theId = item[0]
        except: theId = item
        if not theId: return None

        p = self.ids.get(theId)

        # A kludge: p will be None for vertical lines.
        if not p:
            item = canvas.find_overlapping(x+1,y,x+1,y)
            try:    theId = item[0]
            except: theId = item
            if not theId:
                g.es_print('oops:','eventToPosition','failed')
                return None
            p = self.ids.get(theId)
            # g.trace("was vertical line",p)

        if self.trace and self.verbose:
            if p:
                w = self.findEditWidget(p)
                g.trace("%3d %3d %3d %d" % (theId,x,y,id(w)),p.headString())
            else:
                g.trace("%3d %3d %3d" % (theId,x,y),None)

        # defensive programming: this copy is not needed.
        if p: return p.copy() # Make _sure_ nobody changes this table!
        else: return None
    #@-node:ekr.20081004172422.800:eventToPosition
    #@+node:ekr.20081004172422.801:findEditWidget (qtTree)
    def findEditWidget (self,p):

        """Return the Qt.Text item corresponding to p."""

        return None

        c = self.c ; trace = False

        # if trace: g.trace(g.callers())

        if p and c:
            # if trace: g.trace('h',p.headString(),'key',p.key())
            aTuple = self.visibleText.get(p.key())
            if aTuple:
                w,theId = aTuple
                # if trace: g.trace('id(p.v):',id(p.v),'%4d' % (theId),self.textAddr(w),p.headString())
                return w
            else:
                if trace: g.trace('oops: not found',p,g.callers())
                return None

        if trace: g.trace('not found',p and p.headString())
        return None
    #@-node:ekr.20081004172422.801:findEditWidget (qtTree)
    #@+node:ekr.20081004172422.802:findVnodeWithIconId
    def findPositionWithIconId (self,theId):

        # Due to an old bug, theId may be a tuple.
        try:
            data = self.iconIds.get(theId[0])
        except:
            data = self.iconIds.get(theId)

        if data:
            p,generation = data
            if generation==self.generation:
                if self.trace and self.verbose:
                    g.trace(theId,p.headString())
                return p
            else:
                if self.trace and self.verbose:
                    g.trace("*** wrong generation: %d ***" % theId)
                return None
        else:
            if self.trace and self.verbose: g.trace(theId,None)
            return None
    #@-node:ekr.20081004172422.802:findVnodeWithIconId
    #@-node:ekr.20081004172422.796:Helpers
    #@+node:ekr.20081004172422.803:Click Box...
    #@+node:ekr.20081004172422.804:onClickBoxClick
    def onClickBoxClick (self,event,p=None):

        c = self.c ; p1 = c.currentPosition()

        if not p: p = self.eventToPosition(event)
        if not p: return

        c.setLog()

        if p and not g.doHook("boxclick1",c=c,p=p,v=p,event=event):
            c.endEditing()
            if p == p1 or self.initialClickExpandsOrContractsNode:
                if p.isExpanded(): p.contract()
                else:              p.expand()
            self.select(p)
            if c.frame.findPanel:
                c.frame.findPanel.handleUserClick(p)
            if self.stayInTree:
                c.treeWantsFocus()
            else:
                c.bodyWantsFocus()
        g.doHook("boxclick2",c=c,p=p,v=p,event=event)
        c.redraw()

        c.outerUpdate()
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

        self._block_canvas_menu = True

        if not p: p = self.eventToPosition(event)
        if not p: return

        self.OnActivateHeadline(p)
        self.endEditLabel()

        g.doHook('rclick-popup',c=c,p=p,event=event,context_menu='plusbox')

        c.outerUpdate()

        return 'break'
    #@-node:ekr.20081004172422.806:onPlusBoxRightClick
    #@-node:ekr.20081004172422.803:Click Box...
    #@+node:ekr.20081004172422.807:Dragging (qtTree)
    #@+node:ekr.20081004172422.808:endDrag
    def endDrag (self,event):

        """The official helper of the onEndDrag event handler."""

        c = self.c ; p = self.drag_p
        c.setLog()
        canvas = self.canvas
        if not event: return

        #@    << set vdrag, childFlag >>
        #@+node:ekr.20081004172422.809:<< set vdrag, childFlag >>
        x,y = event.x,event.y
        canvas_x = canvas.canvasx(x)
        canvas_y = canvas.canvasy(y)

        theId = self.canvas.find_closest(canvas_x,canvas_y)
        # theId = self.canvas.find_overlapping(canvas_x,canvas_y,canvas_x,canvas_y)

        vdrag = self.findPositionWithIconId(theId)
        childFlag = vdrag and vdrag.hasChildren() and vdrag.isExpanded()
        #@-node:ekr.20081004172422.809:<< set vdrag, childFlag >>
        #@nl
        if self.allow_clone_drags:
            if not self.look_for_control_drag_on_mouse_down:
                self.controlDrag = c.frame.controlKeyIsDown

        redrawFlag = vdrag and vdrag.v.t != p.v.t
        if redrawFlag: # Disallow drag to joined node.
            #@        << drag p to vdrag >>
            #@+node:ekr.20081004172422.810:<< drag p to vdrag >>
            # g.trace("*** end drag   ***",theId,x,y,p.headString(),vdrag.headString())

            if self.controlDrag: # Clone p and move the clone.
                if childFlag:
                    c.dragCloneToNthChildOf(p,vdrag,0)
                else:
                    c.dragCloneAfter(p,vdrag)
            else: # Just drag p.
                if childFlag:
                    p = c.dragToNthChildOf(p,vdrag,0)
                else:
                    p = c.dragAfter(p,vdrag)
            #@-node:ekr.20081004172422.810:<< drag p to vdrag >>
            #@nl
        elif self.trace and self.verbose:
            g.trace("Cancel drag")

        # Reset the old cursor by brute force.
        self.canvas['cursor'] = "arrow"
        self.dragging = False
        self.drag_p = None

        # Must set self.drag_p = None first.
        if redrawFlag:
            c.redraw_now()
        c.recolor_now() # Dragging can affect coloring.

        # g.trace(redrawFlag)
    #@-node:ekr.20081004172422.808:endDrag
    #@+node:ekr.20081004172422.811:startDrag
    # This precomputes numberOfVisibleNodes(), a significant optimization.
    # We also indicate where findPositionWithIconId() should start looking for tree id's.

    def startDrag (self,event,p=None):

        """The official helper of the onDrag event handler."""

        c = self.c ; canvas = self.canvas

        if not p:
            assert(not self.drag_p)
            x = canvas.canvasx(event.x)
            y = canvas.canvasy(event.y)
            theId = canvas.find_closest(x,y)
            # theId = canvas.find_overlapping(canvas_x,canvas_y,canvas_x,canvas_y)
            if theId is None: return
            try: theId = theId[0]
            except: pass
            p = self.ids.get(theId)
        if not p: return
        c.setLog()
        self.drag_p = p.copy() # defensive programming: not needed.
        self.dragging = True
        # g.trace("*** start drag ***",theId,self.drag_p.headString())
        # Only do this once: greatly speeds drags.
        self.savedNumberOfVisibleNodes = self.numberOfVisibleNodes()
        # g.trace('self.controlDrag',self.controlDrag)
        if self.allow_clone_drags:
            self.controlDrag = c.frame.controlKeyIsDown
            if self.look_for_control_drag_on_mouse_down:
                if self.enable_drag_messages:
                    if self.controlDrag:
                        g.es("dragged node will be cloned")
                    else:
                        g.es("dragged node will be moved")
        else: self.controlDrag = False
        self.canvas['cursor'] = "hand2" # "center_ptr"
    #@-node:ekr.20081004172422.811:startDrag
    #@+node:ekr.20081004172422.812:onContinueDrag
    def onContinueDrag(self,event):

        c = self.c ; p = self.drag_p
        if not p: return

        try:
            canvas = self.canvas ; frame = c.frame
            if event:
                x,y = event.x,event.y
            else:
                x,y = frame.top.winfo_pointerx(),frame.top.winfo_pointery()
                # Stop the scrolling if we go outside the entire window.
                if x == -1 or y == -1: return 
            if self.dragging: # This gets cleared by onEndDrag()
                #@            << scroll the canvas as needed >>
                #@+node:ekr.20081004172422.813:<< scroll the canvas as needed >>
                # Scroll the screen up or down one line if the cursor (y) is outside the canvas.
                h = canvas.winfo_height()

                if y < 0 or y > h:
                    lo, hi = frame.canvas.leo_treeBar.get()
                    n = self.savedNumberOfVisibleNodes
                    line_frac = 1.0 / float(n)
                    frac = g.choose(y < 0, lo - line_frac, lo + line_frac)
                    frac = min(frac,1.0)
                    frac = max(frac,0.0)
                    canvas.yview("moveto", frac)

                    # Queue up another event to keep scrolling while the cursor is outside the canvas.
                    lo, hi = frame.canvas.leo_treeBar.get()
                    if (y < 0 and lo > 0.1) or (y > h and hi < 0.9):
                        canvas.after_idle(self.onContinueDrag,None) # Don't propagate the event.
                #@-node:ekr.20081004172422.813:<< scroll the canvas as needed >>
                #@nl
        except:
            g.es_event_exception("continue drag")
    #@-node:ekr.20081004172422.812:onContinueDrag
    #@+node:ekr.20081004172422.814:onDrag
    def onDrag(self,event):

        c = self.c ; p = self.drag_p
        if not event: return

        c.setLog()

        if not self.dragging:
            if not g.doHook("drag1",c=c,p=p,v=p,event=event):
                self.startDrag(event)
            g.doHook("drag2",c=c,p=p,v=p,event=event)

        if not g.doHook("dragging1",c=c,p=p,v=p,event=event):
            self.onContinueDrag(event)
        g.doHook("dragging2",c=c,p=p,v=p,event=event)
    #@-node:ekr.20081004172422.814:onDrag
    #@+node:ekr.20081004172422.815:onEndDrag
    def onEndDrag(self,event):

        """Tree end-of-drag handler called from vnode event handler."""

        c = self.c ; p = self.drag_p
        if not p: return

        c.setLog()

        if not g.doHook("enddrag1",c=c,p=p,v=p,event=event):
            self.endDrag(event)
        g.doHook("enddrag2",c=c,p=p,v=p,event=event)
    #@-node:ekr.20081004172422.815:onEndDrag
    #@-node:ekr.20081004172422.807:Dragging (qtTree)
    #@+node:ekr.20081004172422.816:Icon Box...
    #@+node:ekr.20081004172422.817:onIconBoxClick
    def onIconBoxClick (self,event,p=None):

        c = self.c ; tree = self

        if not p: p = self.eventToPosition(event)
        if not p:
            return

        c.setLog()

        if self.trace and self.verbose: g.trace()

        if not g.doHook("iconclick1",c=c,p=p,v=p,event=event):
            if event:
                self.onDrag(event)
            tree.endEditLabel()
            tree.select(p,scroll=False)
            if c.frame.findPanel:
                c.frame.findPanel.handleUserClick(p)
        g.doHook("iconclick2",c=c,p=p,v=p,event=event)

        return "break" # disable expanded box handling.
    #@-node:ekr.20081004172422.817:onIconBoxClick
    #@+node:ekr.20081004172422.818:onIconBoxRightClick
    def onIconBoxRightClick (self,event,p=None):

        """Handle a right click in any outline widget."""

        #g.trace()

        c = self.c

        if not p: p = self.eventToPosition(event)
        if not p:
            c.outerUpdate()
            return

        c.setLog()

        try:
            if not g.doHook("iconrclick1",c=c,p=p,v=p,event=event):
                self.OnActivateHeadline(p)
                self.endEditLabel()
                if not g.doHook('rclick-popup', c=c, p=p, event=event, context_menu='iconbox'):
                    self.OnPopup(p,event)
            g.doHook("iconrclick2",c=c,p=p,v=p,event=event)
        except:
            g.es_event_exception("iconrclick")

        self._block_canvas_menu = True

        c.outerUpdate()
        return 'break'
    #@-node:ekr.20081004172422.818:onIconBoxRightClick
    #@+node:ekr.20081004172422.819:onIconBoxDoubleClick
    def onIconBoxDoubleClick (self,event,p=None):

        c = self.c

        if not p: p = self.eventToPosition(event)
        if not p:
            c.outerUpdate()
            return

        c.setLog()

        if self.trace and self.verbose: g.trace()

        try:
            if not g.doHook("icondclick1",c=c,p=p,v=p,event=event):
                self.endEditLabel() # Bug fix: 11/30/05
                self.OnIconDoubleClick(p) # Call the method in the base class.
            g.doHook("icondclick2",c=c,p=p,v=p,event=event)
        except:
            g.es_event_exception("icondclick")

        c.outerUpdate()
        return 'break'
    #@-node:ekr.20081004172422.819:onIconBoxDoubleClick
    #@-node:ekr.20081004172422.816:Icon Box...
    #@+node:ekr.20081004172422.820:OnActivateHeadline (qtTree)
    def OnActivateHeadline (self,p,event=None):

        '''Handle common process when any part of a headline is clicked.'''

        # g.trace(p.headString())

        returnVal = 'break' # Default: do nothing more.
        trace = False

        try:
            c = self.c
            c.setLog()
            #@        << activate this window >>
            #@+node:ekr.20081004172422.821:<< activate this window >>
            if p == c.currentPosition():

                if trace: g.trace('current','active',self.active)
                self.editLabel(p) # sets focus.
                # If we are active, pass the event along so the click gets handled.
                # Otherwise, do *not* pass the event along so the focus stays the same.
                returnVal = g.choose(self.active,'continue','break')
                self.active = True
            else:
                if trace: g.trace("not current")
                self.select(p,scroll=False)
                w  = c.frame.body.bodyCtrl
                if c.frame.findPanel:
                    c.frame.findPanel.handleUserClick(p)
                if p.v.t.insertSpot != None:
                    spot = p.v.t.insertSpot
                    w.setInsertPoint(spot)
                    w.see(spot)
                else:
                    w.setInsertPoint(0)
                # An important detail.
                # The *canvas* (not the headline) gets the focus so that
                # tree bindings take priority over text bindings.
                c.treeWantsFocusNow() # Now. New in Leo 4.5.
                c.outerUpdate()
                self.active = False
                returnVal = 'break'
            #@nonl
            #@-node:ekr.20081004172422.821:<< activate this window >>
            #@nl
        except:
            g.es_event_exception("activate tree")

        return returnVal
    #@-node:ekr.20081004172422.820:OnActivateHeadline (qtTree)
    #@+node:ekr.20081004172422.822:Text Box...
    #@+node:ekr.20081004172422.823:configureTextState
    def configureTextState (self,p):

        c = self.c

        if not p: return

        # g.trace(c.isCurrentPosition(p),self.c._currentPosition,p)

        if c.isCurrentPosition(p):
            if p == self.editPosition():
                self.setEditLabelState(p) # selected, editing.
            else:
                self.setSelectedLabelState(p) # selected, not editing.
        else:
            self.setUnselectedLabelState(p) # unselected
    #@-node:ekr.20081004172422.823:configureTextState
    #@+node:ekr.20081004172422.824:onCtontrolT
    # This works around an apparent Qt bug.

    def onControlT (self,event=None):

        # If we don't inhibit further processing the Tx.Text widget switches characters!
        return "break"
    #@-node:ekr.20081004172422.824:onCtontrolT
    #@+node:ekr.20081004172422.825:onHeadlineClick
    def onHeadlineClick (self,event,p=None):

        # g.trace('p',p)
        c = self.c ; w = event.widget

        if not p:
            try:
                p = w.leo_position
            except AttributeError:
                g.trace('*'*20,'oops')
        if not p: return 'break'

        # g.trace(g.app.gui.widget_name(w),p and p.headString())

        c.setLog()

        try:
            if not g.doHook("headclick1",c=c,p=p,v=p,event=event):
                returnVal = self.OnActivateHeadline(p)
            g.doHook("headclick2",c=c,p=p,v=p,event=event)
        except:
            returnVal = 'break'
            g.es_event_exception("headclick")

        # 'continue' is sometimes correct here.
        # 'break' would make it impossible to unselect the headline text.
        # g.trace('returnVal',returnVal,'stayInTree',self.stayInTree)
        return returnVal
    #@-node:ekr.20081004172422.825:onHeadlineClick
    #@+node:ekr.20081004172422.826:onHeadlineRightClick
    def onHeadlineRightClick (self,event):

        """Handle a right click in any outline widget."""

        c = self.c ; w = event.widget

        try:
            p = w.leo_position
        except AttributeError:
            g.trace('*'*20,'oops')
            return 'break'

        c.setLog()

        try:
            if not g.doHook("headrclick1",c=c,p=p,v=p,event=event):
                self.OnActivateHeadline(p)
                self.endEditLabel()
                if not g.doHook('rclick-popup', c=c, p=p, event=event, context_menu='headline'):
                    self.OnPopup(p,event)
            g.doHook("headrclick2",c=c,p=p,v=p,event=event)
        except:
            g.es_event_exception("headrclick")

        # 'continue' *is* correct here.
        # 'break' would make it impossible to unselect the headline text.

        return 'continue'
    #@-node:ekr.20081004172422.826:onHeadlineRightClick
    #@-node:ekr.20081004172422.822:Text Box...
    #@+node:ekr.20081004172422.827:tree.OnDeactivate
    def OnDeactivate (self,event=None):

        """Deactivate the tree pane, dimming any headline being edited."""

        tree = self ; c = self.c

        tree.endEditLabel()
        tree.dimEditLabel()
        c.outerUpdate()
    #@-node:ekr.20081004172422.827:tree.OnDeactivate
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

        self.popupMenu.unpost()
    #@-node:ekr.20081004172422.829:OnPopupFocusLost
    #@+node:ekr.20081004172422.830:createPopupMenu
    def createPopupMenu (self,event):

        c = self.c ; frame = c.frame


        self.popupMenu = menu = Qt.Menu(g.app.root, tearoff=0)

        # Add the Open With entries if they exist.
        if g.app.openWithTable:
            frame.menu.createOpenWithMenuItemsFromTable(menu,g.app.openWithTable)
            table = (("-",None,None),)
            frame.menu.createMenuEntries(menu,table)

        #@    << Create the menu table >>
        #@+node:ekr.20081004172422.831:<< Create the menu table >>
        table = (
            ("&Read @file Nodes",c.readAtFileNodes),
            ("&Write @file Nodes",c.fileCommands.writeAtFileNodes),
            ("-",None),
            ("&Tangle",c.tangle),
            ("&Untangle",c.untangle),
            ("-",None),
            ("Toggle Angle &Brackets",c.toggleAngleBrackets),
            ("-",None),
            ("Cut Node",c.cutOutline),
            ("Copy Node",c.copyOutline),
            ("&Paste Node",c.pasteOutline),
            ("&Delete Node",c.deleteOutline),
            ("-",None),
            ("&Insert Node",c.insertHeadline),
            ("&Clone Node",c.clone),
            ("Sort C&hildren",c.sortChildren),
            ("&Sort Siblings",c.sortSiblings),
            ("-",None),
            ("Contract Parent",c.contractParent),
        )
        #@-node:ekr.20081004172422.831:<< Create the menu table >>
        #@nl

        # New in 4.4.  There is no need for a dontBind argument because
        # Bindings from tables are ignored.
        frame.menu.createMenuEntries(menu,table)
    #@-node:ekr.20081004172422.830:createPopupMenu
    #@+node:ekr.20081004172422.832:enablePopupMenuItems
    def enablePopupMenuItems (self,v,event):

        """Enable and disable items in the popup menu."""

        c = self.c ; menu = self.popupMenu

        #@    << set isAtRoot and isAtFile if v's tree contains @root or @file nodes >>
        #@+node:ekr.20081004172422.833:<< set isAtRoot and isAtFile if v's tree contains @root or @file nodes >>
        isAtFile = False
        isAtRoot = False

        for v2 in v.self_and_subtree_iter():
            if isAtFile and isAtRoot:
                break
            if (v2.isAtFileNode() or
                v2.isAtNorefFileNode() or
                v2.isAtAsisFileNode() or
                v2.isAtNoSentFileNode()
            ):
                isAtFile = True

            isRoot,junk = g.is_special(v2.bodyString(),0,"@root")
            if isRoot:
                isAtRoot = True
        #@-node:ekr.20081004172422.833:<< set isAtRoot and isAtFile if v's tree contains @root or @file nodes >>
        #@nl
        isAtFile = g.choose(isAtFile,1,0)
        isAtRoot = g.choose(isAtRoot,1,0)
        canContract = v.parent() != None
        canContract = g.choose(canContract,1,0)

        enable = self.frame.menu.enableMenu

        for name in ("Read @file Nodes", "Write @file Nodes"):
            enable(menu,name,isAtFile)
        for name in ("Tangle", "Untangle"):
            enable(menu,name,isAtRoot)

        enable(menu,"Cut Node",c.canCutOutline())
        enable(menu,"Delete Node",c.canDeleteHeadline())
        enable(menu,"Paste Node",c.canPasteOutline())
        enable(menu,"Sort Children",c.canSortChildren())
        enable(menu,"Sort Siblings",c.canSortSiblings())
        enable(menu,"Contract Parent",c.canContractParent())
    #@-node:ekr.20081004172422.832:enablePopupMenuItems
    #@+node:ekr.20081004172422.834:showPopupMenu
    def showPopupMenu (self,event):

        """Show a popup menu."""

        c = self.c ; menu = self.popupMenu

        g.app.gui.postPopupMenu(c, menu, event.x_root, event.y_root)

        self.popupMenu = None

        # Set the focus immediately so we know when we lose it.
        #c.widgetWantsFocus(menu)
    #@-node:ekr.20081004172422.834:showPopupMenu
    #@-node:ekr.20081004172422.828:tree.OnPopup & allies
    #@+node:ekr.20081004172422.835:onTreeClick
    def onTreeClick (self,event=None):

        '''Handle an event in the tree canvas, outside of any tree widget.'''

        c = self.c

        # New in Leo 4.4.2: a kludge: disable later event handling after a double-click.
        # This allows focus to stick in newly-opened files opened by double-clicking an @url node.
        if c.doubleClickFlag:
            c.doubleClickFlag = False
        else:
            c.treeWantsFocusNow()

        g.app.gui.killPopupMenu()
        c.outerUpdate()

        return 'break'
    #@-node:ekr.20081004172422.835:onTreeClick
    #@+node:ekr.20081004172422.836:onTreeRightClick
    def onTreeRightClick (self,event=None):

        c = self.c

        if not c.exists: return

        if self._block_canvas_menu:
            self._block_canvas_menu = False
            return 'break'

        g.doHook('rclick-popup',c=c,event=event,context_menu='canvas')

        c.outerUpdate()
        return 'break'
    #@-node:ekr.20081004172422.836:onTreeRightClick
    #@-node:ekr.20081004172422.795:Event handlers (qtTree)
    #@+node:ekr.20081004172422.899:To be deleted
    if 0:

        #@    @+others
        #@+node:ekr.20081004172422.747:Allocation...
        #@+node:ekr.20081004172422.748:newBox
        def newBox (self,p,x,y,image):

            canvas = self.canvas ; tag = "plusBox"

            if self.freeBoxes:
                # theId = self.freeBoxes.pop(0)
                d = self.freeBoxes ; theId = d.keys()[0] ; del d[theId]
                canvas.coords(theId,x,y)
                canvas.itemconfigure(theId,image=image)
            else:
                theId = canvas.create_image(x,y,image=image,tag=tag)
                if self.trace_alloc: g.trace("%3d %s" % (theId,p and p.headString()),align=-20)

            if theId not in self.visibleBoxes: 
                self.visibleBoxes.append(theId)

            if p:
                self.ids[theId] = p

            return theId
        #@-node:ekr.20081004172422.748:newBox
        #@+node:ekr.20081004172422.749:newClickBox
        def newClickBox (self,p,x1,y1,x2,y2):

            canvas = self.canvas ; defaultColor = ""
            tag = g.choose(p.hasChildren(),'clickBox','selectBox')

            if self.freeClickBoxes:
                # theId = self.freeClickBoxes.pop(0)
                d = self.freeClickBoxes ; theId = d.keys()[0] ; del d[theId]
                canvas.coords(theId,x1,y1,x2,y2)
                canvas.itemconfig(theId,tag=tag)
            else:
                theId = self.canvas.create_rectangle(x1,y1,x2,y2,tag=tag)
                canvas.itemconfig(theId,fill=defaultColor,outline=defaultColor)
                if self.trace_alloc: g.trace("%3d %s" % (theId,p and p.headString()),align=-20)

            if theId not in self.visibleClickBoxes:
                self.visibleClickBoxes.append(theId)
            if p:
                self.ids[theId] = p

            return theId
        #@-node:ekr.20081004172422.749:newClickBox
        #@+node:ekr.20081004172422.750:newIcon
        def newIcon (self,p,x,y,image):

            canvas = self.canvas ; tag = "iconBox"

            if self.freeIcons:
                # theId = self.freeIcons.pop(0)
                d = self.freeIcons ; theId = d.keys()[0] ; del d[theId]
                canvas.itemconfigure(theId,image=image)
                canvas.coords(theId,x,y)
            else:
                theId = canvas.create_image(x,y,image=image,anchor="nw",tag=tag)
                if self.trace_alloc: g.trace("%3d %s" % (theId,p and p.headString()),align=-20)

            if theId not in self.visibleIcons:
                self.visibleIcons.append(theId)

            if p:
                data = p,self.generation
                self.iconIds[theId] = data # Remember which vnode belongs to the icon.
                self.ids[theId] = p

            return theId
        #@-node:ekr.20081004172422.750:newIcon
        #@+node:ekr.20081004172422.751:newLine
        def newLine (self,p,x1,y1,x2,y2):

            canvas = self.canvas

            if self.freeLines:
                # theId = self.freeLines.pop(0)
                d = self.freeLines ; theId = d.keys()[0] ; del d[theId]
                canvas.coords(theId,x1,y1,x2,y2)
            else:
                theId = canvas.create_line(x1,y1,x2,y2,tag="lines",fill="gray50") # stipple="gray25")
                if self.trace_alloc: g.trace("%3d %s" % (theId,p and p.headString()),align=-20)

            if p:
                self.ids[theId] = p

            if theId not in self.visibleLines:
                self.visibleLines.append(theId)

            return theId
        #@-node:ekr.20081004172422.751:newLine
        #@+node:ekr.20081004172422.752:newText (qtTree) and helper
        def newText (self,p,x,y):

            canvas = self.canvas ; tag = "textBox"
            c = self.c ;  k = c.k
            if self.freeText:
                # w,theId = self.freeText.pop()
                d = self.freeText ; data = d.keys()[0] ; w,theId = data ; del d[data]
                canvas.coords(theId,x,y) # Make the window visible again.
                    # theId is the id of the *window* not the text.
            else:
                # Tags are not valid in Qt.Text widgets.
                self.textNumber += 1
                w = g.app.gui.plainTextWidget(
                    canvas,name='head-%d' % self.textNumber,
                    state="normal",font=self.font,bd=0,relief="flat",height=1)
                w.bindtags(self.textBindings) # Set the bindings for this widget.

                if 0: # Crashes on XP.
                    #@            << patch by Maciej Kalisiak to handle scroll-wheel events >>
                    #@+node:ekr.20081004172422.753:<< patch by Maciej Kalisiak  to handle scroll-wheel events >>
                    def PropagateButton4(e):
                        canvas.event_generate("<Button-4>")
                        return "break"

                    def PropagateButton5(e):
                        canvas.event_generate("<Button-5>")
                        return "break"

                    def PropagateMouseWheel(e):
                        canvas.event_generate("<MouseWheel>")
                        return "break"

                    instance_tag = w.bindtags()[0]
                    w.bind_class(instance_tag, "<Button-4>", PropagateButton4)
                    w.bind_class(instance_tag, "<Button-5>", PropagateButton5)
                    w.bind_class(instance_tag, "<MouseWheel>",PropagateMouseWheel)
                    #@-node:ekr.20081004172422.753:<< patch by Maciej Kalisiak  to handle scroll-wheel events >>
                    #@nl

                theId = canvas.create_window(x,y,anchor="nw",window=w,tag=tag)
                w.leo_window_id = theId # Never changes.

                if self.trace_alloc: g.trace('%3d %6s' % (theId,id(w)),align=-20)

            # Common configuration.
            if 0: # Doesn't seem to work.
                balloon = Pmw.Balloon(canvas,initwait=700)
                balloon.tagbind(canvas,theId,balloonHelp='Headline')

            if p:
                self.ids[theId] = p # Add the id of the *window*
                self.setHeadlineText(theId,w,p.headString())
                w.configure(width=self.headWidth(p=p))
                w.leo_position = p # This p never changes.
                    # *Required*: onHeadlineClick uses w.leo_position to get p.

                # Keys are p.key().  Entries are (w,theId)
                self.visibleText [p.key()] = w,theId
            else:
                g.trace('**** can not happen.  No p')

            return w
        #@+node:ekr.20081004172422.754:tree.setHeadlineText
        def setHeadlineText (self,theId,w,s):

            """All changes to text widgets should come here."""

            # if self.trace_alloc: g.trace('%4d %6s %s' % (theId,self.textAddr(w),s),align=-20)

            state = w.cget("state")
            if state != "normal":
                w.configure(state="normal")
            w.delete(0,"end")
            # Important: do not allow newlines in headlines.
            while s.endswith('\n') or s.endswith('\r'):
                s = s[:-1]
            w.insert("end",s)
            # g.trace(repr(s))
            if state != "normal":
                w.configure(state=state)
        #@-node:ekr.20081004172422.754:tree.setHeadlineText
        #@-node:ekr.20081004172422.752:newText (qtTree) and helper
        #@+node:ekr.20081004172422.755:recycleWidgets
        def recycleWidgets (self):

            canvas = self.canvas

            for theId in self.visibleBoxes:
                # if theId not in self.freeBoxes:
                    # self.freeBoxes.append(theId)
                self.freeBoxes[theId] = theId
                canvas.coords(theId,-100,-100)
            self.visibleBoxes = []

            for theId in self.visibleClickBoxes:
                # if theId not in self.freeClickBoxes:
                    # self.freeClickBoxes.append(theId)
                self.freeClickBoxes[theId] = theId
                canvas.coords(theId,-100,-100,-100,-100)
            self.visibleClickBoxes = []

            for theId in self.visibleIcons:
                # if theId not in self.freeIcons:
                    # self.freeIcons.append(theId)
                self.freeIcons[theId] = theId
                canvas.coords(theId,-100,-100)
            self.visibleIcons = []

            for theId in self.visibleLines:
                # if theId not in self.freeLines:
                    # self.freeLines.append(theId)
                self.freeLines[theId] = theId
                canvas.coords(theId,-100,-100,-100,-100)
            self.visibleLines = []

            aList = self.visibleText.values()
            for data in aList:
                w,theId = data
                # assert theId == w.leo_window_id
                canvas.coords(theId,-100,-100)
                w.leo_position = None # Allow the position to be freed.
                # if data not in self.freeText:
                    # self.freeText.append(data)
                self.freeText[data] = data
            self.visibleText = {}

            # g.trace('deleting visible user icons!')
            for theId in self.visibleUserIcons:
                # The present code does not recycle user Icons.
                self.canvas.delete(theId)
            self.visibleUserIcons = []
        #@-node:ekr.20081004172422.755:recycleWidgets
        #@+node:ekr.20081004172422.756:destroyWidgets
        def destroyWidgets (self):

            self.ids = {}

            self.visibleBoxes = []
            self.visibleClickBoxes = []
            self.visibleIcons = []
            self.visibleLines = []
            self.visibleUserIcons = []

            self.visibleText = {}

            self.freeText = {}
            self.freeBoxes = {}
            self.freeClickBoxes = {}
            self.freeIcons = {}
            self.freeLines = {}

            self.canvas.delete("all")
        #@-node:ekr.20081004172422.756:destroyWidgets
        #@+node:ekr.20081004172422.757:showStats
        def showStats (self):

            z = []
            for kind,a,b in (
                ('boxes',self.visibleBoxes,self.freeBoxes),
                ('clickBoxes',self.visibleClickBoxes,self.freeClickBoxes),
                ('icons',self.visibleIcons,self.freeIcons),
                ('lines',self.visibleLines,self.freeLines),
                ('tesxt',self.visibleText.values(),self.freeText),
            ):
                z.append('%10s used: %4d free: %4d' % (kind,len(a),len(b)))

            s = '\n' + '\n'.join(z)
            g.es_print('',s)
        #@-node:ekr.20081004172422.757:showStats
        #@-node:ekr.20081004172422.747:Allocation...
        #@+node:ekr.20081004172422.762:Debugging...
        #@+node:ekr.20081004172422.763:textAddr
        def textAddr(self,w):

            """Return the address part of repr(Qt.Text)."""

            s = repr(w)
            i = s.find('id: ')
            if i != -1:
                return s[i+4:i+12].lower()
            else:
                return s
        #@-node:ekr.20081004172422.763:textAddr
        #@+node:ekr.20081004172422.764:traceIds (Not used)
        # Verbose tracing is much more useful than this because we can see the recent past.

        def traceIds (self,full=False):

            tree = self

            for theDict,tag,flag in ((tree.ids,"ids",True),(tree.iconIds,"icon ids",False)):
                g.pr('=' * 60)
                g.pr("\n%s..." % tag)
                for key in sorted(theDict):
                    p = tree.ids.get(key)
                    if p is None: # For lines.
                        g.pr("%3d None" % key)
                    else:
                        g.pr("%3d" % key,p.headString())
                if flag and full:
                    g.pr('-' * 40)
                    seenValues = {}
                    for key in sorted(theDict):
                        value = theDict.get(key)
                        if value not in seenValues:
                            seenValues[value]=True
                            for item in theDict.items():
                                key,val = item
                                if val and val == value:
                                    g.pr("%3d" % key,val.headString())
        #@-node:ekr.20081004172422.764:traceIds (Not used)
        #@-node:ekr.20081004172422.762:Debugging...
        #@+node:ekr.20081004172422.765:Drawing... (qtTree)
        #@+node:ekr.20081004172422.766:tree.begin/endUpdate
        def beginUpdate (self):
            g.trace('should not be called')

        def endUpdate (self,flag,scroll=False):

            g.trace('should not be called')
        #@-node:ekr.20081004172422.766:tree.begin/endUpdate
        #@+node:ekr.20081004172422.768:redrawHelper
        def redrawHelper (self,scroll=True,forceDraw=False):

            # This can be called at idle time, so there are shutdown issues.
            if g.app.quitting or self.frame not in g.app.windowList:
                return
            if self.drag_p and not forceDraw:
                return
            if not hasattr(self,'c'):
                return

            c = self.c ; trace = False
            oldcursor = self.canvas['cursor']
            self.canvas['cursor'] = "watch"

            if not g.doHook("redraw-entire-outline",c=c):

                c.setTopVnode(None)
                self.setVisibleAreaToFullCanvas()
                self.drawTopTree()
                # Set up the scroll region after the tree has been redrawn.
                bbox = self.canvas.bbox('all')
                if trace: g.trace('bbox',bbox,g.callers())
                if bbox is None:
                    x0,y0,x1,y1 = 0,0,100,100
                else:
                    x0, y0, x1, y1 = bbox
                self.canvas.configure(scrollregion=(0, 0, x1, y1))
                if scroll:
                    self.canvas.update_idletasks() # Essential.
                    self.scrollTo()

            g.doHook("after-redraw-outline",c=c)

            self.canvas['cursor'] = oldcursor
        #@-node:ekr.20081004172422.768:redrawHelper
        #@+node:ekr.20081004172422.769:idle_second_redraw
        def idle_second_redraw (self):

            c = self.c

            # Erase and redraw the entire tree the SECOND time.
            # This ensures that all visible nodes are allocated.
            c.setTopVnode(None)
            args = self.canvas.yview()
            self.setVisibleArea(args)

            if 0:
                self.canvas.delete("all")

            self.drawTopTree()

            if self.trace:
                g.trace(self.redrawCount)
        #@-node:ekr.20081004172422.769:idle_second_redraw
        #@+node:ekr.20081004172422.770:drawX...
        #@+node:ekr.20081004172422.771:drawBox
        def drawBox (self,p,x,y):

            tree = self ; c = self.c
            y += 7 # draw the box at x, y+7

            theId = g.doHook("draw-outline-box",tree=tree,c=c,p=p,v=p,x=x,y=y)

            if theId is None:
                # if self.trace_gc: g.printNewObjects(tag='box 1')
                iconname = g.choose(p.isExpanded(),"minusnode.gif", "plusnode.gif")
                image = self.getIconImage(iconname)
                theId = self.newBox(p,x,y+self.lineyoffset,image)
                # if self.trace_gc: g.printNewObjects(tag='box 2')
                return theId
            else:
                return theId
        #@-node:ekr.20081004172422.771:drawBox
        #@+node:ekr.20081004172422.772:drawClickBox
        def drawClickBox (self,p,y):

            h = self.line_height

            # Define a slighly larger rect to catch clicks.
            if self.expanded_click_area:
                self.newClickBox(p,0,y,1000,y+h-2)
        #@-node:ekr.20081004172422.772:drawClickBox
        #@+node:ekr.20081004172422.773:drawIcon
        def drawIcon(self,p,x=None,y=None):

            """Draws icon for position p at x,y, or at p.v.iconx,p.v.icony if x,y = None,None"""

            # if self.trace_gc: g.printNewObjects(tag='icon 1')

            c = self.c ; v = p.v
            #@    << compute x,y and iconVal >>
            #@+node:ekr.20081004172422.774:<< compute x,y and iconVal >>
            if x is None and y is None:
                try:
                    x,y = v.iconx, v.icony
                except:
                    # Inject the ivars.
                    x,y = v.iconx, v.icony = 0,0
            else:
                # Inject the ivars.
                v.iconx, v.icony = x,y

            y += 2 # draw icon at y + 2

            # Always recompute v.iconVal.
            # This is an important drawing optimization.
            val = v.computeIcon()
            assert(0 <= val <= 15)
            # g.trace(v,val)
            #@nonl
            #@-node:ekr.20081004172422.774:<< compute x,y and iconVal >>
            #@nl
            v.iconVal = val

            if not g.doHook("draw-outline-icon",tree=self,c=c,p=p,v=p,x=x,y=y):

                # Get the image.
                imagename = "box%02d.GIF" % val
                image = self.getIconImage(imagename)
                self.newIcon(p,x,y+self.lineyoffset,image)

            return 0,self.icon_width # dummy icon height,width
        #@-node:ekr.20081004172422.773:drawIcon
        #@+node:ekr.20081004172422.775:drawLine
        def drawLine (self,p,x1,y1,x2,y2):

            theId = self.newLine(p,x1,y1,x2,y2)

            return theId
        #@-node:ekr.20081004172422.775:drawLine
        #@+node:ekr.20081004172422.776:drawNode & force_draw_node (good trace)
        def drawNode(self,p,x,y):

            c = self.c

            # g.trace(x,y,p,id(self.canvas))

            data = g.doHook("draw-outline-node",tree=self,c=c,p=p,v=p,x=x,y=y)
            if data is not None: return data

            if 1:
                self.lineyoffset = 0
            else:
                if hasattr(p.v.t,"unknownAttributes"):
                    self.lineyoffset = p.v.t.unknownAttributes.get("lineYOffset",0)
                else:
                    self.lineyoffset = 0

            # Draw the horizontal line.
            self.drawLine(p,
                x,y+7+self.lineyoffset,
                x+self.box_width,y+7+self.lineyoffset)

            if self.inVisibleArea(y):
                return self.force_draw_node(p,x,y)
            else:
                return self.line_height,0
        #@+node:ekr.20081004172422.777:force_draw_node
        def force_draw_node(self,p,x,y):

            h = 0 # The total height of the line.
            indent = 0 # The amount to indent this line.

            h2,w2 = self.drawUserIcons(p,"beforeBox",x,y)
            h = max(h,h2) ; x += w2 ; indent += w2

            if p.hasChildren():
                self.drawBox(p,x,y)

            indent += self.box_width
            x += self.box_width # even if box isn't drawn.

            h2,w2 = self.drawUserIcons(p,"beforeIcon",x,y)
            h = max(h,h2) ; x += w2 ; indent += w2

            h2,w2 = self.drawIcon(p,x,y)
            h = max(h,h2) ; x += w2 ; indent += w2/2

            # Nothing after here affects indentation.
            h2,w2 = self.drawUserIcons(p,"beforeHeadline",x,y)
            h = max(h,h2) ; x += w2

            h2 = self.drawText(p,x,y)
            h = max(h,h2)
            x += self.widthInPixels(p.headString())

            h2,w2 = self.drawUserIcons(p,"afterHeadline",x,y)
            h = max(h,h2)

            self.drawClickBox(p,y)

            return h,indent
        #@-node:ekr.20081004172422.777:force_draw_node
        #@-node:ekr.20081004172422.776:drawNode & force_draw_node (good trace)
        #@+node:ekr.20081004172422.778:drawText
        def drawText(self,p,x,y):

            """draw text for position p at nominal coordinates x,y."""

            assert(p)

            c = self.c
            x += self.text_indent

            data = g.doHook("draw-outline-text-box",tree=self,c=c,p=p,v=p,x=x,y=y)
            if data is not None: return data

            self.newText(p,x,y+self.lineyoffset)

            self.configureTextState(p)

            return self.line_height
        #@-node:ekr.20081004172422.778:drawText
        #@+node:ekr.20081004172422.779:drawUserIcons & helper
        def drawUserIcons(self,p,where,x,y):

            """Draw any icons specified by p.v.t.unknownAttributes["icons"]."""

            h,w = 0,0 ; t = p.v.t

            com = self.c.editCommands
            iconsList = com.getIconList(p)
            if not iconsList:
                return h,w

            try:
                for theDict in iconsList:
                    h2,w2 = self.drawUserIcon(p,where,x,y,w,theDict)
                    h = max(h,h2) ; w += w2
            except:
                g.es_exception()

            # g.trace(where,h,w)

            return h,w
        #@+node:ekr.20081004172422.780:drawUserIcon
        def drawUserIcon (self,p,where,x,y,w2,theDict):

            c = self.c ; h,w = 0,0

            if where != theDict.get("where","beforeHeadline"):
                return h,w

            # if self.trace_gc: g.printNewObjects(tag='userIcon 1')

            # g.trace(where,x,y,theDict)

            #@    << set offsets and pads >>
            #@+node:ekr.20081004172422.781:<< set offsets and pads >>
            xoffset = theDict.get("xoffset")
            try:    xoffset = int(xoffset)
            except: xoffset = 0

            yoffset = theDict.get("yoffset")
            try:    yoffset = int(yoffset)
            except: yoffset = 0

            xpad = theDict.get("xpad")
            try:    xpad = int(xpad)
            except: xpad = 0

            ypad = theDict.get("ypad")
            try:    ypad = int(ypad)
            except: ypad = 0
            #@-node:ekr.20081004172422.781:<< set offsets and pads >>
            #@nl
            theType = theDict.get("type")
            if theType == "icon":
                ### not ready yet.
                # s = theDict.get("icon")
                pass
            elif theType == "file":
                theFile = theDict.get("file")
                relPath = theDict.get('relPath')
                #@        << draw the icon at file >>
                #@+node:ekr.20081004172422.782:<< draw the icon at file >>
                if relPath:
                    fullname = g.os_path_join(g.app.loadDir,"..","Icons",relPath)
                else:
                    fullname = g.os_path_join(g.app.loadDir,"..","Icons",theFile)
                fullname = g.os_path_normpath(fullname)

                # Bug fix: the key must include distinguish nodes.
                key = (fullname,p.v.t)
                image = self.iconimages.get(key)

                if not image:
                    try:
                        from PIL import Image, ImageTk
                        image1 = Image.open(fullname)
                        image = ImageTk.PhotoImage(image1)
                        self.iconimages[key] = image
                    except Exception:
                        #g.es_exception()
                        image = None

                if not image:
                    try:
                        image = Tk.PhotoImage(master=self.canvas,file=fullname)
                        self.iconimages[key] = image
                    except Exception:
                        #g.es_exception()
                        image = None

                if image:
                    theId = self.canvas.create_image(
                        x+xoffset+w2,y+yoffset,
                        anchor="nw",image=image)

                    tag='userIcon-%s' % theId
                    self.canvas.itemconfigure(theId,tag=(tag,'userIcon')) #BJ
                    self.ids[theId] = p.copy()

                    def deleteButtonCallback(event=None,c=c,p=p,fullname=fullname,relPath=relPath):
                        #g.trace()
                        c.editCommands.deleteIconByName(p,fullname,relPath)
                        self._block_canvas_menu = True
                        return 'break'

                    c.tag_bind(self.canvas,tag,'<3>',deleteButtonCallback)

                    # assert(theId not in self.visibleIcons)
                    self.visibleUserIcons.append(theId)

                    h = image.height() + yoffset + ypad
                    w = image.width()  + xoffset + xpad
                #@-node:ekr.20081004172422.782:<< draw the icon at file >>
                #@nl
            elif theType == "url":
                ## url = theDict.get("url")
                #@        << draw the icon at url >>
                #@+node:ekr.20081004172422.783:<< draw the icon at url >>
                pass
                #@-node:ekr.20081004172422.783:<< draw the icon at url >>
                #@nl

            # Allow user to specify height, width explicitly.
            h = theDict.get("height",h)
            w = theDict.get("width",w)

            # if self.trace_gc: g.printNewObjects(tag='userIcon 2')

            return h,w
        #@-node:ekr.20081004172422.780:drawUserIcon
        #@-node:ekr.20081004172422.779:drawUserIcons & helper
        #@+node:ekr.20081004172422.784:drawTopTree
        def drawTopTree (self):

            """Draws the top-level tree, taking into account the hoist state."""

            c = self.c ; canvas = self.canvas
            trace = False or self.trace or self.trace_redraw

            self.redrawing = True

            # Recycle all widgets and clear all widget lists.
            self.recycleWidgets()
            # Clear all ids so invisible id's don't confuse eventToPosition & findPositionWithIconId
            self.ids = {}
            self.iconIds = {}
            self.generation += 1
            self.redrawCount += 1
            self.drag_p = None # Disable drags across redraws.
            self.dragging = False
            if trace:
                g.trace('redrawCount',self.redrawCount,g.callers()) # 'len(c.hoistStack)',len(c.hoistStack))
                if 0:
                    delta = g.app.positions - self.prevPositions
                    g.trace("**** gen: %-3d positions: %5d +%4d" % (
                        self.generation,g.app.positions,delta),g.callers())

            self.prevPositions = g.app.positions
            if self.trace_gc: g.printNewObjects(tag='top 1')

            hoistFlag = c.hoistStack
            if c.hoistStack:
                bunch = c.hoistStack[-1] ; p = bunch.p
                h = p.headString()
                if len(c.hoistStack) == 1 and h.startswith('@chapter') and p.hasChildren():
                    p = p.firstChild()
                    hoistFlag = False
            else:
                p = c.rootPosition()

            self.drawTree(p,self.root_left,self.root_top,0,0,hoistFlag=hoistFlag)

            if self.trace_gc: g.printNewObjects(tag='top 2')
            if self.trace_stats: self.showStats()

            canvas.lower("lines")  # Lowest.
            canvas.lift("textBox") # Not the Qt.Text widget: it should be low.

            canvas.lift("clickBox")
            canvas.lift("clickExpandBox")
            canvas.lift("iconBox") # Higest. BJ:Not now
            canvas.lift("plusBox")
            canvas.lift("userIcon")
            self.redrawing = False
        #@-node:ekr.20081004172422.784:drawTopTree
        #@+node:ekr.20081004172422.785:drawTree
        def drawTree(self,p,x,y,h,level,hoistFlag=False):

            tree = self ; c = self.c
            yfirst = ylast = y ; h1 = None
            data = g.doHook("draw-sub-outline",tree=tree,
                c=c,p=p,v=p,x=x,y=y,h=h,level=level,hoistFlag=hoistFlag)
            if data is not None: return data

            while p: # Do not use iterator.
                # This is the ONLY copy of p that needs to be made;
                # no other drawing routine calls any p.moveTo method.
                const_p = p.copy()
                h,indent = self.drawNode(const_p,x,y)
                if h1 is None: h1 = h # Set h1 *after* calling drawNode.
                y += h ; ylast = y
                if p.isExpanded() and p.hasFirstChild():
                    # Must make an additional copy here by calling firstChild.
                    y = self.drawTree(p.firstChild(),x+indent,y,h,level+1)
                if hoistFlag: break
                else:         p = p.next()
            # Draw the vertical line.
            if h1 is None: h1 = h
            y2 = g.choose(level==0,yfirst+(h1-1)/2,yfirst-h1/2-1)
            self.drawLine(None,x,y2,x,ylast+self.hline_y-h)
            return y
        #@-node:ekr.20081004172422.785:drawTree
        #@-node:ekr.20081004172422.770:drawX...
        #@+node:ekr.20081004172422.786:Helpers...
        #@+node:ekr.20081004172422.787:getIconImage
        def getIconImage (self, name):

            # Return the image from the cache if possible.
            if name in self.iconimages:
                return self.iconimages[name]

            # g.trace(name)

            try:
                fullname = g.os_path_join(g.app.loadDir,"..","Icons",name)
                fullname = g.os_path_normpath(fullname)
                image = Qt.PhotoImage(master=self.canvas,file=fullname)
                self.iconimages[name] = image
                return image
            except:
                g.es("exception loading:",fullname)
                g.es_exception()
                return None
        #@-node:ekr.20081004172422.787:getIconImage
        #@+node:ekr.20081004172422.788:inVisibleArea & inExpandedVisibleArea
        def inVisibleArea (self,y1):

            if self.allocateOnlyVisibleNodes:
                if self.visibleArea:
                    vis1,vis2 = self.visibleArea
                    y2 = y1 + self.line_height
                    return y2 >= vis1 and y1 <= vis2
                else: return False
            else:
                return True # This forces all nodes to be allocated on all redraws.

        def inExpandedVisibleArea (self,y1):

            if self.expandedVisibleArea:
                vis1,vis2 = self.expandedVisibleArea
                y2 = y1 + self.line_height
                return y2 >= vis1 and y1 <= vis2
            else:
                return False
        #@-node:ekr.20081004172422.788:inVisibleArea & inExpandedVisibleArea
        #@+node:ekr.20081004172422.789:numberOfVisibleNodes
        def numberOfVisibleNodes(self):

            c = self.c

            n = 0 ; p = self.c.rootPosition()
            while p:
                n += 1
                p.moveToVisNext(c)
            return n
        #@-node:ekr.20081004172422.789:numberOfVisibleNodes
        #@+node:ekr.20081004172422.790:scrollTo
        def scrollTo(self,p=None):

            """Scrolls the canvas so that p is in view."""

            # This can be called at idle time, so there are shutdown issues.
            if g.app.quitting or self.drag_p or self.frame not in g.app.windowList:
                return
            if not hasattr(self,'c'):
                return

            c = self.c ; frame = c.frame ; trace = False
            if not p or not c.positionExists(p):
                p = c.currentPosition()
                if trace: g.trace('*** current position',p,p.stack)
            if not p or not c.positionExists(p):
                if trace: g.trace('current p does not exist',p)
                p = c.rootPosition()
            if not p or not c.positionExists(p):
                if trace: g.trace('no position')
                return
            try:
                if trace: g.trace('***',p,p.stack,'exists',c.positionExists(p))
                h1 = self.yoffset(p)
                if self.center_selected_tree_node: # New in Leo 4.4.3.
                    #@            << compute frac0 >>
                    #@+node:ekr.20081004172422.791:<< compute frac0 >>
                    # frac0 attempt to put the 
                    scrollRegion = self.canvas.cget('scrollregion')
                    geom = self.canvas.winfo_geometry()

                    if scrollRegion and geom:
                        scrollRegion = scrollRegion.split(' ')
                        # if trace: g.trace('scrollRegion',repr(scrollRegion))
                        htot = int(scrollRegion[3])
                        wh,junk,junk = geom.split('+')
                        junk,h = wh.split('x')
                        if h: wtot = int(h)
                        else: wtot = 500
                        # if trace: g.trace('geom',geom,'wtot',wtot,'htot',htot)
                        if htot > 0.1:
                            frac0 = float(h1-wtot/2)/float(htot)
                            frac0 = max(min(frac0,1.0),0.0)
                        else:
                            frac0 = 0.0
                    else:
                        frac0 = 0.0 ; htot = wtot = 0
                    #@-node:ekr.20081004172422.791:<< compute frac0 >>
                    #@nl
                    delta = abs(self.prevMoveToFrac-frac0)
                    if trace: g.trace('delta',delta)
                    if delta > 0.0:
                        self.prevMoveToFrac = frac0
                        self.canvas.yview("moveto",frac0)
                        if trace: g.trace("frac0 %1.2f h1 %3d htot %3d wtot %3d" % (
                            frac0,h1,htot,wtot),g.callers())
                else:
                    last = c.lastVisible()
                    nextToLast = last.visBack(c)
                    h2 = self.yoffset(last)
                    #@            << compute approximate line height >>
                    #@+node:ekr.20081004172422.792:<< compute approximate line height >>
                    if nextToLast: # 2/2/03: compute approximate line height.
                        lineHeight = h2 - self.yoffset(nextToLast)
                    else:
                        lineHeight = 20 # A reasonable default.
                    #@-node:ekr.20081004172422.792:<< compute approximate line height >>
                    #@nl
                    #@            << Compute the fractions to scroll down/up >>
                    #@+node:ekr.20081004172422.793:<< Compute the fractions to scroll down/up >>
                    data = frame.canvas.leo_treeBar.get() # Get the previous values of the scrollbar.
                    try: lo, hi = data
                    except: lo,hi = 0.0,1.0

                    # h1 and h2 are the y offsets of the present and last nodes.
                    if h2 > 0.1:
                        frac = float(h1)/float(h2) # For scrolling down.
                        frac2 = float(h1+lineHeight/2)/float(h2) # For scrolling up.
                        frac2 = frac2 - (hi - lo)
                    else:
                        frac = frac2 = 0.0 # probably any value would work here.

                    frac =  max(min(frac,1.0),0.0)
                    frac2 = max(min(frac2,1.0),0.0)
                    #@nonl
                    #@-node:ekr.20081004172422.793:<< Compute the fractions to scroll down/up >>
                    #@nl
                    if frac <= lo: # frac is for scrolling down.
                        if self.prevMoveToFrac != frac:
                            self.prevMoveToFrac = frac
                            self.canvas.yview("moveto",frac)
                            if trace: g.trace("frac  %1.2f h1 %3d h2 %3d lo %1.2f hi %1.2f" % (
                                frac, h1,h2,lo,hi),g.callers())
                    elif frac2 + (hi - lo) >= hi: # frac2 is for scrolling up.
                        if self.prevMoveToFrac != frac2:
                            self.prevMoveToFrac = frac2
                            self.canvas.yview("moveto",frac2)
                            if trace: g.trace("frac2 %1.2f h1 %3d h2 %3d lo %1.2f hi %1.2f" % (
                                frac2,h1,h2,lo,hi),g.callers())

                if self.allocateOnlyVisibleNodes:
                    self.canvas.after_idle(self.idle_second_redraw)

                c.setTopVnode(p) # 1/30/04: remember a pseudo "top" node.

            except:
                g.es_exception()

        idle_scrollTo = scrollTo # For compatibility.
        #@-node:ekr.20081004172422.790:scrollTo
        #@+node:ekr.20081004172422.794:yoffset (qtTree)
        #@+at 
        #@nonl
        # We can't just return icony because the tree hasn't been redrawn yet.
        # For the same reason we can't rely on any TK canvas methods here.
        #@-at
        #@@c

        def yoffset(self,p1):
            # if not p1.isVisible(): g.pr("yoffset not visible:",p1)
            if not p1: return 0
            c = self.c
            if c.hoistStack:
                bunch = c.hoistStack[-1]
                root = bunch.p.copy()
            else:
                root = self.c.rootPosition()
            if root:
                h,flag = self.yoffsetTree(root,p1,isTop=True)
                # flag can be False during initialization.
                # if not flag: g.pr("*** yoffset fails:",'root',root,'p1',p1,'returns',h)
                return h
            else:
                return 0

        def yoffsetTree(self,p,p1,isTop):
            c = self.c ; h = 0 ; trace = False ; verbose = True
            if trace: g.trace('entry','root',p,p.stack,'target',p1,p1.stack)
            if not c.positionExists(p):
                if trace: g.trace('*** does not exist',p.headString())
                return h,False # An extra precaution.
            p = p.copy()
            if trace and verbose and isTop and c.hoistStack:
                g.trace('c.hoistStack',c.hoistStack[-1].p.headString())
            if isTop and c.hoistStack:
                if p.firstChild():  theIter = [p.firstChild()]
                else:               theIter = []
            else:
                theIter = p.self_and_siblings_iter() # Bug fix 10/27/07: was p.siblings_iter()

            for p2 in theIter:
                if trace and p1.headString() == p2.headString():
                    g.trace('loop',p1,p2)
                    g.trace(p1.stack,p2.stack)
                if p2 == p1:
                    if trace and verbose: g.trace('returns',h,p1.headString())
                    return h, True
                h += self.line_height
                if p2.isExpanded() and p2.hasChildren():
                    child = p2.firstChild()
                    if trace and verbose: g.trace('recursive call')
                    h2, flag = self.yoffsetTree(child,p1,isTop=False)
                    h += h2
                    if flag:
                        if trace and verbose: g.trace('returns',h,p1.headString())
                        return h, True

            if trace: g.trace('not found',h,p1.headString())
            return h, False
        #@-node:ekr.20081004172422.794:yoffset (qtTree)
        #@-node:ekr.20081004172422.786:Helpers...
        #@-node:ekr.20081004172422.765:Drawing... (qtTree)
        #@+node:ekr.20081004172422.837:Incremental drawing...
        #@+node:ekr.20081004172422.838:allocateNodes
        def allocateNodes(self,where,lines):

            """Allocate Qt widgets in nodes that will become visible as the result of an upcoming scroll"""

            assert(where in ("above","below"))

            # g.pr("allocateNodes: %d lines %s visible area" % (lines,where))

            # Expand the visible area: a little extra delta is safer.
            delta = lines * (self.line_height + 4)
            y1,y2 = self.visibleArea

            if where == "below":
                y2 += delta
            else:
                y1 = max(0.0,y1-delta)

            self.expandedVisibleArea=y1,y2
            # g.pr("expandedArea:   %5.1f %5.1f" % (y1,y2))

            # Allocate all nodes in expanded visible area.
            self.updatedNodeCount = 0
            self.updateTree(self.c.rootPosition(),self.root_left,self.root_top,0,0)
            # if self.updatedNodeCount: g.pr("updatedNodeCount:", self.updatedNodeCount)
        #@-node:ekr.20081004172422.838:allocateNodes
        #@+node:ekr.20081004172422.839:allocateNodesBeforeScrolling
        def allocateNodesBeforeScrolling (self, args):

            """Calculate the nodes that will become visible as the result of an upcoming scroll.

            args is the tuple passed to the Qt.Canvas.yview method"""

            if not self.allocateOnlyVisibleNodes: return

            # g.pr("allocateNodesBeforeScrolling:",self.redrawCount,args)

            assert(self.visibleArea)
            assert(len(args)==2 or len(args)==3)
            kind = args[0] ; n = args[1]
            lines = 2 # Update by 2 lines to account for rounding.
            if len(args) == 2:
                assert(kind=="moveto")
                frac1,frac2 = args
                if float(n) != frac1:
                    where = g.choose(n<frac1,"above","below")
                    self.allocateNodes(where=where,lines=lines)
            else:
                assert(kind=="scroll")
                linesPerPage = self.canvas.winfo_height()/self.line_height + 2
                n = int(n) ; assert(abs(n)==1)
                where = g.choose(n == 1,"below","above")
                lines = g.choose(args[2] == "pages",linesPerPage,lines)
                self.allocateNodes(where=where,lines=lines)
        #@-node:ekr.20081004172422.839:allocateNodesBeforeScrolling
        #@+node:ekr.20081004172422.840:updateNode
        def updateNode (self,p,x,y):

            """Draw a node that may have become visible as a result of a scrolling operation"""

            c = self.c

            if self.inExpandedVisibleArea(y):
                # This check is a major optimization.
                if not c.edit_widget(p):
                    return self.force_draw_node(p,x,y)
                else:
                    return self.line_height

            return self.line_height
        #@-node:ekr.20081004172422.840:updateNode
        #@+node:ekr.20081004172422.841:setVisibleAreaToFullCanvas
        def setVisibleAreaToFullCanvas(self):

            if self.visibleArea:
                y1,y2 = self.visibleArea
                y2 = max(y2,y1 + self.canvas.winfo_height())
                self.visibleArea = y1,y2
        #@-node:ekr.20081004172422.841:setVisibleAreaToFullCanvas
        #@+node:ekr.20081004172422.842:setVisibleArea
        def setVisibleArea (self,args):

            r1,r2 = args
            r1,r2 = float(r1),float(r2)
            # g.pr("scroll ratios:",r1,r2)

            try:
                s = self.canvas.cget("scrollregion")
                x1,y1,x2,y2 = g.scanf(s,"%d %d %d %d")
                x1,y1,x2,y2 = int(x1),int(y1),int(x2),int(y2)
            except:
                self.visibleArea = None
                return

            scroll_h = y2-y1
            # g.pr("height of scrollregion:", scroll_h)

            vy1 = y1 + (scroll_h*r1)
            vy2 = y1 + (scroll_h*r2)
            self.visibleArea = vy1,vy2
            # g.pr("setVisibleArea: %5.1f %5.1f" % (vy1,vy2))
        #@-node:ekr.20081004172422.842:setVisibleArea
        #@+node:ekr.20081004172422.843:tree.updateTree
        def updateTree (self,v,x,y,h,level):

            yfirst = y
            if level==0: yfirst += 10
            while v:
                # g.trace(x,y,v)
                h,indent = self.updateNode(v,x,y)
                y += h
                if v.isExpanded() and v.firstChild():
                    y = self.updateTree(v.firstChild(),x+indent,y,h,level+1)
                v = v.next()
            return y
        #@-node:ekr.20081004172422.843:tree.updateTree
        #@-node:ekr.20081004172422.837:Incremental drawing...
        #@-others
    #@-node:ekr.20081004172422.899:To be deleted
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

        return None ###

        tt = self ; c = tt.c

        # Create the main container, possibly in a new row.
        tt.frame = c.frame.getNewIconFrame()

        # Create the chapter menu.
        self.chapterVar = var = qt.StringVar()
        var.set('main')

        tt.chapterMenu = menu = Pmw.OptionMenu(tt.frame,
            labelpos = 'w', label_text = 'chapter',
            menubutton_textvariable = var,
            items = [],
            command = tt.selectTab,
        )
        menu.pack(side='left',padx=5)

        # Actually add tt.frame to the icon row.
        c.frame.addIconWidget(tt.frame)
    #@-node:ekr.20081004172422.687:tt.createControl
    #@-node:ekr.20081004172422.685: Birth & death
    #@+node:ekr.20081004172422.688:Tabs...
    #@+node:ekr.20081004172422.689:tt.createTab
    def createTab (self,tabName,select=True):

        tt = self

        if tabName not in tt.tabNames:
            tt.tabNames.append(tabName)
            tt.setNames()
    #@-node:ekr.20081004172422.689:tt.createTab
    #@+node:ekr.20081004172422.690:tt.destroyTab
    def destroyTab (self,tabName):

        tt = self

        if tabName in tt.tabNames:
            tt.tabNames.remove(tabName)
            tt.setNames()
    #@-node:ekr.20081004172422.690:tt.destroyTab
    #@+node:ekr.20081004172422.691:tt.selectTab
    def selectTab (self,tabName):

        tt = self

        if tabName not in self.tabNames:
            tt.createTab(tabName)

        tt.cc.selectChapterByName(tabName)

        self.c.redraw()
        self.c.outerUpdate()
    #@-node:ekr.20081004172422.691:tt.selectTab
    #@+node:ekr.20081004172422.692:tt.setTabLabel
    def setTabLabel (self,tabName):

        tt = self
        tt.chapterVar.set(tabName)
    #@-node:ekr.20081004172422.692:tt.setTabLabel
    #@+node:ekr.20081004172422.693:tt.setNames
    def setNames (self):

        '''Recreate the list of items.'''

        tt = self
        names = tt.tabNames[:]
        if 'main' in names: names.remove('main')
        names.sort()
        names.insert(0,'main')
        tt.chapterMenu.setitems(names)
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
#@-others
#@-node:ekr.20081004102201.619:@thin qtGui.py
#@-leo
