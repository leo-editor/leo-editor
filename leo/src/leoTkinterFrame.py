# -*- coding: utf-8 -*-
#@+leo-ver=4-thin
#@+node:ekr.20031218072017.3939:@thin leoTkinterFrame.py
#@@first

#@@language python
#@@tabwidth -4
#@@pagewidth 80

#@<< imports >>
#@+node:ekr.20041221070525:<< imports >>
import leoGlobals as g

import leoChapters
import leoColor
import leoFrame
import leoNodes
import leoTkinterMenu
import leoTkinterTree

import Tkinter as Tk
import tkFont
import os
import string
import sys

Pmw = g.importExtension("Pmw",pluginName="leoTkinterFrame.py",verbose=False)
tkColorChooser = g.importExtension('tkColorChooser',pluginName=None,verbose=False)

# The following imports _are_ used.
# __pychecker__ = '--no-import'
import time
#@-node:ekr.20041221070525:<< imports >>
#@nl

#@+others
#@+node:ekr.20031218072017.3996:class leoTkinterBody
class leoTkinterBody (leoFrame.leoBody):

    """A class that represents the body pane of a Tkinter window."""

    #@    @+others
    #@+node:ekr.20031218072017.3997: Birth & death
    #@+node:ekr.20031218072017.2182:tkBody. __init__
    def __init__ (self,frame,parentFrame):

        # g.trace("leoTkinterBody")

        # Call the base class constructor.
        leoFrame.leoBody.__init__(self,frame,parentFrame)

        c = self.c ; p = c.currentPosition()
        self.editor_name = None
        self.editor_v = None

        self.trace_onBodyChanged = c.config.getBool('trace_onBodyChanged')
        self.bodyCtrl = self.createControl(parentFrame,p)
        self.colorizer = leoColor.colorizer(c)
    #@-node:ekr.20031218072017.2182:tkBody. __init__
    #@+node:ekr.20031218072017.838:tkBody.createBindings
    def createBindings (self,w=None):

        '''(tkBody) Create gui-dependent bindings.
        These are *not* made in nullBody instances.'''

        frame = self.frame ; c = self.c ; k = c.k
        if not w: w = self.bodyCtrl

        w.bind('<Key>', k.masterKeyHandler)

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

            w.bind(kind,bodyClickCallback)
    #@-node:ekr.20031218072017.838:tkBody.createBindings
    #@+node:ekr.20031218072017.3998:tkBody.createControl
    def createControl (self,parentFrame,p):

        c = self.c

        # New in 4.4.1: make the parent frame a Pmw.PanedWidget.
        self.numberOfEditors = 1 ; name = '1'
        self.totalNumberOfEditors = 1

        orient = c.config.getString('editor_orientation') or 'horizontal'
        if orient not in ('horizontal','vertical'): orient = 'horizontal'

        self.pb = pb = Pmw.PanedWidget(parentFrame,orient=orient)
        parentFrame = pb.add(name)
        pb.pack(expand=1,fill='both') # Must be done after the first page created.

        w = self.createTextWidget(parentFrame,p,name)
        self.editorWidgets[name] = w

        return w
    #@-node:ekr.20031218072017.3998:tkBody.createControl
    #@+node:ekr.20060528100747.3:tkBody.createTextWidget
    def createTextWidget (self,parentFrame,p,name):

        c = self.c

        parentFrame.configure(bg='LightSteelBlue1')

        wrap = c.config.getBool('body_pane_wraps')
        wrap = g.choose(wrap,"word","none")

        # Setgrid=1 cause severe problems with the font panel.
        body = w = leoTkTextWidget (parentFrame,name='body-pane',
            bd=2,bg="white",relief="flat",setgrid=0,wrap=wrap)

        bodyBar = Tk.Scrollbar(parentFrame,name='bodyBar')

        def yscrollCallback(x,y,bodyBar=bodyBar,w=w):
            # g.trace(x,y,g.callers())
            if hasattr(w,'leo_scrollBarSpot'):
                w.leo_scrollBarSpot = (x,y)
            return bodyBar.set(x,y)

        body['yscrollcommand'] = yscrollCallback # bodyBar.set

        bodyBar['command'] =  body.yview
        bodyBar.pack(side="right", fill="y")

        # Always create the horizontal bar.
        bodyXBar = Tk.Scrollbar(
            parentFrame,name='bodyXBar',orient="horizontal")
        body['xscrollcommand'] = bodyXBar.set
        bodyXBar['command'] = body.xview

        if wrap == "none":
            # g.trace(parentFrame)
            bodyXBar.pack(side="bottom", fill="x")

        body.pack(expand=1,fill="both")

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
    #@-node:ekr.20060528100747.3:tkBody.createTextWidget
    #@-node:ekr.20031218072017.3997: Birth & death
    #@+node:ekr.20041217135735.1:tkBody.setColorFromConfig
    def setColorFromConfig (self,w=None):

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
    #@-node:ekr.20041217135735.1:tkBody.setColorFromConfig
    #@+node:ekr.20031218072017.2183:tkBody.setFontFromConfig
    def setFontFromConfig (self,w=None):

        c = self.c

        if not w: w = self.bodyCtrl

        font = c.config.getFontFromParams(
            "body_text_font_family", "body_text_font_size",
            "body_text_font_slant",  "body_text_font_weight",
            c.config.defaultBodyFontSize)

        self.fontRef = font # ESSENTIAL: retain a link to font.
        w.configure(font=font)

        # g.trace("BODY",body.cget("font"),font.cget("family"),font.cget("weight"))
    #@-node:ekr.20031218072017.2183:tkBody.setFontFromConfig
    #@+node:ekr.20031218072017.4003:Focus (tkBody)
    def hasFocus (self):

        return self.bodyCtrl == self.frame.top.focus_displayof()

    def setFocus (self):

        self.c.widgetWantsFocus(self.bodyCtrl)
    #@-node:ekr.20031218072017.4003:Focus (tkBody)
    #@+node:ekr.20031218072017.3999:forceRecolor
    def forceFullRecolor (self):

        self.forceFullRecolorFlag = True
    #@-node:ekr.20031218072017.3999:forceRecolor
    #@+node:ekr.20031218072017.4000:Tk bindings (tkBody)
    #@+node:ekr.20031218072017.4002:Color tags (Tk spelling) (tkBody)
    def tag_add (self,tagName,index1,index2):
        self.bodyCtrl.tag_add(tagName,index1,index2)

    def tag_bind (self,tagName,event,callback):
        self.bodyCtrl.tag_bind(tagName,event,callback)

    def tag_configure (self,colorName,**keys):
        self.bodyCtrl.tag_configure(colorName,keys)

    def tag_delete(self,tagName):
        self.bodyCtrl.tag_delete(tagName)

    def tag_names(self,*args): # New in Leo 4.4.1.
        return self.bodyCtrl.tag_names(*args)

    def tag_remove (self,tagName,index1,index2):
        return self.bodyCtrl.tag_remove(tagName,index1,index2)
    #@-node:ekr.20031218072017.4002:Color tags (Tk spelling) (tkBody)
    #@+node:ekr.20031218072017.2184:Configuration (Tk spelling) (tkBody)
    def cget(self,*args,**keys):

        val = self.bodyCtrl.cget(*args,**keys)

        if g.app.trace:
            g.trace(val,args,keys)

        return val

    def configure (self,*args,**keys):

        # g.trace(args,keys)

        return self.bodyCtrl.configure(*args,**keys)
    #@-node:ekr.20031218072017.2184:Configuration (Tk spelling) (tkBody)
    #@+node:ekr.20031218072017.4004:Height & width
    def getBodyPaneHeight (self):

        return self.bodyCtrl.winfo_height()

    def getBodyPaneWidth (self):

        return self.bodyCtrl.winfo_width()
    #@-node:ekr.20031218072017.4004:Height & width
    #@+node:ekr.20031218072017.4005:Idle time...
    def scheduleIdleTimeRoutine (self,function,*args,**keys):

        if not g.app.unitTesting:
            self.bodyCtrl.after_idle(function,*args,**keys)
    #@-node:ekr.20031218072017.4005:Idle time...
    #@+node:ekr.20031218072017.4017:Menus
    def bind (self,*args,**keys):

        return self.bodyCtrl.bind(*args,**keys)
    #@-node:ekr.20031218072017.4017:Menus
    #@+node:ekr.20070228081242:Text (now in base class)
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
    #@-node:ekr.20070228081242:Text (now in base class)
    #@-node:ekr.20031218072017.4000:Tk bindings (tkBody)
    #@+node:ekr.20070424053629.2:Editors (tkBody)
    #@+node:ekr.20070424054235:createEditorFrame
    def createEditorFrame (self,pane):

        f = Tk.Frame(pane)
        f.pack(side='top',expand=1,fill='both')
        return f
    #@-node:ekr.20070424054235:createEditorFrame
    #@+node:ekr.20070424054810:packEditorLabelWidget
    def packEditorLabelWidget (self,w):

        '''Create a Tk label widget.'''

        if not hasattr(w,'leo_label') or not w.leo_label:
            # g.trace('w.leo_frame',id(w.leo_frame))
            w.pack_forget()
            w.leo_label = Tk.Label(w.leo_frame)
            w.leo_label.pack(side='top')
            w.pack(expand=1,fill='both')
    #@nonl
    #@-node:ekr.20070424054810:packEditorLabelWidget
    #@+node:ekr.20060606090542:setEditorColors
    def setEditorColors (self,bg,fg):

        c = self.c ; d = self.editorWidgets

        for key in d.keys():
            w2 = d.get(key)
            # g.trace(id(w2),bg,fg)
            try:
                w2.configure(bg=bg,fg=fg)
            except Exception:
                g.es_exception()
    #@-node:ekr.20060606090542:setEditorColors
    #@-node:ekr.20070424053629.2:Editors (tkBody)
    #@-others
#@-node:ekr.20031218072017.3996:class leoTkinterBody
#@+node:ekr.20031218072017.3940:class leoTkinterFrame
class leoTkinterFrame (leoFrame.leoFrame):

    """A class that represents a Leo window rendered in Tk/tkinter."""

    #@    @+others
    #@+node:ekr.20031218072017.3941: Birth & Death (tkFrame)
    #@+node:ekr.20031218072017.1801:__init__ (tkFrame)
    def __init__(self,title,gui):

        # Init the base class.
        leoFrame.leoFrame.__init__(self,gui)

        self.title = title

        leoTkinterFrame.instances += 1

        self.c = None # Set in finishCreate.
        self.iconBarClass = self.tkIconBarClass
        self.statusLineClass = self.tkStatusLineClass
        self.iconBar = None

        self.trace_status_line = None # Set in finishCreate.

        #@    << set the leoTkinterFrame ivars >>
        #@+node:ekr.20031218072017.1802:<< set the leoTkinterFrame ivars >> (removed frame.bodyCtrl ivar)
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
        self.top = None
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
        #@-node:ekr.20031218072017.1802:<< set the leoTkinterFrame ivars >> (removed frame.bodyCtrl ivar)
        #@nl
    #@-node:ekr.20031218072017.1801:__init__ (tkFrame)
    #@+node:ekr.20031218072017.3942:__repr__ (tkFrame)
    def __repr__ (self):

        return "<leoTkinterFrame: %s>" % self.title
    #@-node:ekr.20031218072017.3942:__repr__ (tkFrame)
    #@+node:ekr.20031218072017.2176:tkFrame.finishCreate & helpers
    def finishCreate (self,c):

        f = self ; f.c = c
        # g.trace('tkFrame','c',c,g.callers())

        self.bigTree           = c.config.getBool('big_outline_pane')
        self.trace_status_line = c.config.getBool('trace_status_line')
        self.use_chapters      = c.config.getBool('use_chapters')
        self.use_chapter_tabs  = c.config.getBool('use_chapter_tabs')

        # This must be done after creating the commander.
        f.splitVerticalFlag,f.ratio,f.secondary_ratio = f.initialRatios()
        f.createOuterFrames()
        f.createIconBar()
        f.createLeoSplitters(f.outerFrame)
        f.createSplitterComponents()
        f.createStatusLine()
        f.createFirstTreeNode()
        f.menu = leoTkinterMenu.leoTkinterMenu(f)
            # c.finishCreate calls f.createMenuBar later.
        c.setLog()
        g.app.windowList.append(f)
        c.initVersion()
        c.signOnWithVersion()
        f.miniBufferWidget = f.createMiniBufferWidget()
        c.bodyWantsFocusNow()

        # f.enableTclTraces()
    #@+node:ekr.20051009044751:createOuterFrames
    def createOuterFrames (self):

        f = self ; c = f.c
        f.top = top = Tk.Toplevel()
        g.app.gui.attachLeoIcon(top)
        top.title(f.title)
        top.minsize(30,10) # In grid units.

        if g.os_path_exists(g.app.user_xresources_path):
            f.top.option_readfile(g.app.user_xresources_path)

        f.top.protocol("WM_DELETE_WINDOW", f.OnCloseLeoEvent)
        f.top.bind("<Button-1>", f.OnActivateLeoEvent)

        f.top.bind("<Control-KeyPress>",f.OnControlKeyDown)
        f.top.bind("<Control-KeyRelease>",f.OnControlKeyUp)

        # These don't work on Windows. Because of bugs in window managers,
        # there is NO WAY to know which window is on top!
        # f.top.bind("<Activate>",f.OnActivateLeoEvent)
        # f.top.bind("<Deactivate>",f.OnDeactivateLeoEvent)

        # Create the outer frame, the 'hull' component.
        f.outerFrame = Tk.Frame(top)
        f.outerFrame.pack(expand=1,fill="both")
    #@nonl
    #@-node:ekr.20051009044751:createOuterFrames
    #@+node:ekr.20051009045208:createSplitterComponents (tkFrame) (removed frame.bodyCtrl ivar)
    def createSplitterComponents (self):

        f = self ; c = f.c

        # Create the canvas, tree, log and body.
        if f.use_chapters:
            c.chapterController = cc = leoChapters.chapterController(c)

        # split1.pane1 is the secondary splitter.

        if self.bigTree: # Put outline in the main splitter.
            if self.use_chapters and self.use_chapter_tabs:
                cc.tt = leoTkinterTreeTab(c,f.split1Pane2,cc)
            f.canvas = f.createCanvas(f.split1Pane1)
            f.tree  = leoTkinterTree.leoTkinterTree(c,f,f.canvas)
            f.log   = leoTkinterLog(f,f.split2Pane2)
            f.body  = leoTkinterBody(f,f.split2Pane1)
        else:
            if self.use_chapters and self.use_chapter_tabs:
                cc.tt = leoTkinterTreeTab(c,f.split2Pane1,cc)
            f.canvas = f.createCanvas(f.split2Pane1)
            f.tree   = leoTkinterTree.leoTkinterTree(c,f,f.canvas)
            f.log    = leoTkinterLog(f,f.split2Pane2)
            f.body   = leoTkinterBody(f,f.split1Pane2)

        # Yes, this an "official" ivar: this is a kludge.
        # f.bodyCtrl = f.body.bodyCtrl

        # Configure.
        f.setTabWidth(c.tab_width)
        f.reconfigurePanes()
        f.body.setFontFromConfig()
        f.body.setColorFromConfig()
    #@-node:ekr.20051009045208:createSplitterComponents (tkFrame) (removed frame.bodyCtrl ivar)
    #@+node:ekr.20051009045404:createFirstTreeNode
    def createFirstTreeNode (self):

        f = self ; c = f.c

        t = leoNodes.tnode()
        v = leoNodes.vnode(t)
        p = leoNodes.position(v,[])
        v.initHeadString("NewHeadline")
        p.moveToRoot(oldRoot=None)
        c.setRootPosition(p) # New in 4.4.2.
        c.editPosition(p)
    #@-node:ekr.20051009045404:createFirstTreeNode
    #@+node:ekr.20051121092320:f.enableTclTraces
    def enableTclTraces (self):

        c = self.c
        # Put this in unit tests before the assert:
        # c.frame.bar1.unbind_all("<FocusIn>")
        # c.frame.bar1.unbind_all("<FocusOut>")

        # Any widget would do:
        w = c.frame.bar1
        if True:
            def focusIn (event):
                print("Focus in  %s (%s)" % (
                    event.widget,event.widget.winfo_class()))

            def focusOut (event):
                print("Focus out %s (%s)" % (
                    event.widget,event.widget.winfo_class()))

            w.bind_all("<FocusIn>", focusIn)
            w.bind_all("<FocusOut>", focusOut)
        else:
            def tracewidget(event):
                g.trace('enabling widget trace')
                Pmw.tracetk(event.widget, 1)

            def untracewidget(event):
                g.trace('disabling widget trace')
                Pmw.tracetk(event.widget,0)

            w.bind_all("<Control-1>", tracewidget)
            w.bind_all("<Control-Shift-1>", untracewidget)
    #@-node:ekr.20051121092320:f.enableTclTraces
    #@-node:ekr.20031218072017.2176:tkFrame.finishCreate & helpers
    #@+node:ekr.20031218072017.3944:tkFrame.createCanvas & helpers
    def createCanvas (self,parentFrame,pack=True):

        c = self.c

        scrolls = c.config.getBool('outline_pane_scrolls_horizontally')
        scrolls = g.choose(scrolls,1,0)
        canvas = self.createTkTreeCanvas(parentFrame,scrolls,pack)
        self.setCanvasColorFromConfig(canvas)

        return canvas
    #@nonl
    #@+node:ekr.20041221071131.1:f.createTkTreeCanvas & callbacks
    def createTkTreeCanvas (self,parentFrame,scrolls,pack):

        frame = self

        canvas = Tk.Canvas(parentFrame,name="canvas",
            bd=0,bg="white",relief="flat")

        treeBar = Tk.Scrollbar(parentFrame,name="treeBar")

        # New in Leo 4.4.3 b1: inject the ivar into the canvas.
        canvas.leo_treeBar = treeBar

        # Bind mouse wheel event to canvas
        if sys.platform != "win32": # Works on 98, crashes on XP.
            canvas.bind("<MouseWheel>", frame.OnMouseWheel)
            if 1: # New in 4.3.
                #@            << workaround for mouse-wheel problems >>
                #@+node:ekr.20050119210541:<< workaround for mouse-wheel problems >>
                # Handle mapping of mouse-wheel to buttons 4 and 5.

                def mapWheel(e):
                    if e.num == 4: # Button 4
                        e.delta = 120
                        return frame.OnMouseWheel(e)
                    elif e.num == 5: # Button 5
                        e.delta = -120
                        return frame.OnMouseWheel(e)

                canvas.bind("<ButtonPress>",mapWheel,add=1)
                #@-node:ekr.20050119210541:<< workaround for mouse-wheel problems >>
                #@nl

        canvas['yscrollcommand'] = self.setCallback
        treeBar['command']     = self.yviewCallback
        treeBar.pack(side="right", fill="y")
        if scrolls: 
            treeXBar = Tk.Scrollbar( 
                parentFrame,name='treeXBar',orient="horizontal") 
            canvas['xscrollcommand'] = treeXBar.set 
            treeXBar['command'] = canvas.xview 
            treeXBar.pack(side="bottom", fill="x")

        if pack:
            canvas.pack(expand=1,fill="both")

        canvas.bind("<Button-1>", frame.OnActivateTree)

        # Handle mouse wheel in the outline pane.
        if sys.platform == "linux2": # This crashes tcl83.dll
            canvas.bind("<MouseWheel>", frame.OnMouseWheel)

        # g.print_bindings("canvas",canvas)
        return canvas
    #@+node:ekr.20031218072017.998:Scrolling callbacks (tkFrame)
    def setCallback (self,*args,**keys):

        """Callback to adjust the scrollbar.

        Args is a tuple of two floats describing the fraction of the visible area."""

        #g.trace(self.tree.redrawCount,args,g.callers())

        apply(self.canvas.leo_treeBar.set,args,keys)

        if self.tree.allocateOnlyVisibleNodes:
            self.tree.setVisibleArea(args)

    def yviewCallback (self,*args,**keys):

        """Tell the canvas to scroll"""

        #g.trace(vyiewCallback,args,keys,g.callers())

        if self.tree.allocateOnlyVisibleNodes:
            self.tree.allocateNodesBeforeScrolling(args)

        apply(self.canvas.yview,args,keys)
    #@nonl
    #@-node:ekr.20031218072017.998:Scrolling callbacks (tkFrame)
    #@-node:ekr.20041221071131.1:f.createTkTreeCanvas & callbacks
    #@+node:ekr.20070327094252:f.setCanvasColorFromConfig
    def setCanvasColorFromConfig (self,canvas):

        c = self.c

        bg = c.config.getColor("outline_pane_background_color") or 'white'

        try:
            canvas.configure(bg=bg)
        except:
            g.es("exception setting outline pane background color")
            g.es_exception()
    #@-node:ekr.20070327094252:f.setCanvasColorFromConfig
    #@-node:ekr.20031218072017.3944:tkFrame.createCanvas & helpers
    #@+node:ekr.20041221123325:tkFrame.createLeoSplitters & helpers
    #@+at 
    #@nonl
    # The key invariants used throughout this code:
    # 
    # 1. self.splitVerticalFlag tells the alignment of the main splitter and
    # 2. not self.splitVerticalFlag tells the alignment of the secondary 
    # splitter.
    # 
    # Only the general-purpose divideAnySplitter routine doesn't know about 
    # these
    # invariants. So most of this code is specialized for Leo's window. OTOH, 
    # creating
    # a single splitter window would be much easier than this code.
    #@-at
    #@@c

    def createLeoSplitters (self,parentFrame):

        # Splitter 1 is the main splitter.
        f1,bar1,split1Pane1,split1Pane2 = self.createLeoTkSplitter(
            parentFrame,self.splitVerticalFlag,'splitter1')

        self.f1,self.bar1 = f1,bar1
        self.split1Pane1,self.split1Pane2 = split1Pane1,split1Pane2

        # ** new **
        split2parent = g.choose(self.bigTree,split1Pane2,split1Pane1)

        # Splitter 2 is the secondary splitter.
        f2,bar2,split2Pane1,split2Pane2 = self.createLeoTkSplitter(
            # split1Pane1,not self.splitVerticalFlag,'splitter2')
            split2parent,not self.splitVerticalFlag,'splitter2')

        self.f2,self.bar2 = f2,bar2
        self.split2Pane1,self.split2Pane2 = split2Pane1,split2Pane2
    #@+node:ekr.20041221073427.1:createLeoTkSplitter
    def createLeoTkSplitter (self,parent,verticalFlag,componentName):

        c = self.c

        # Create the frames.
        f = Tk.Frame(parent,bd=0,relief="flat")
        f.pack(expand=1,fill="both",pady=1)

        f1 = Tk.Frame(f)
        f2 = Tk.Frame(f)
        bar = Tk.Frame(f,bd=2,relief="raised",bg="LightSteelBlue2")

        # Configure and place the frames.
        self.configureBar(bar,verticalFlag)
        self.bindBar(bar,verticalFlag)
        self.placeSplitter(bar,f1,f2,verticalFlag)

        return f, bar, f1, f2
    #@nonl
    #@-node:ekr.20041221073427.1:createLeoTkSplitter
    #@+node:ekr.20031218072017.3947:bindBar
    def bindBar (self, bar, verticalFlag):

        if verticalFlag == self.splitVerticalFlag:
            bar.bind("<B1-Motion>", self.onDragMainSplitBar)

        else:
            bar.bind("<B1-Motion>", self.onDragSecondarySplitBar)
    #@-node:ekr.20031218072017.3947:bindBar
    #@+node:ekr.20031218072017.3949:divideAnySplitter
    # This is the general-purpose placer for splitters.
    # It is the only general-purpose splitter code in Leo.

    def divideAnySplitter (self, frac, verticalFlag, bar, pane1, pane2):

        # if self.bigTree:
            # pane1,pane2 = pane2,pane1

        if verticalFlag:
            # Panes arranged vertically; horizontal splitter bar
            bar.place(rely=frac)
            pane1.place(relheight=frac)
            pane2.place(relheight=1-frac)
        else:
            # Panes arranged horizontally; vertical splitter bar
            bar.place(relx=frac)
            pane1.place(relwidth=frac)
            pane2.place(relwidth=1-frac)
    #@-node:ekr.20031218072017.3949:divideAnySplitter
    #@+node:ekr.20031218072017.3950:divideLeoSplitter
    # Divides the main or secondary splitter, using the key invariant.
    def divideLeoSplitter (self, verticalFlag, frac):

        if self.splitVerticalFlag == verticalFlag:
            self.divideLeoSplitter1(frac,verticalFlag)
            self.ratio = frac # Ratio of body pane to tree pane.
        else:
            self.divideLeoSplitter2(frac,verticalFlag)
            self.secondary_ratio = frac # Ratio of tree pane to log pane.

    # Divides the main splitter.
    def divideLeoSplitter1 (self, frac, verticalFlag): 
        self.divideAnySplitter(frac, verticalFlag,
            self.bar1, self.split1Pane1, self.split1Pane2)

    # Divides the secondary splitter.
    def divideLeoSplitter2 (self, frac, verticalFlag): 
        self.divideAnySplitter (frac, verticalFlag,
            self.bar2, self.split2Pane1, self.split2Pane2)
    #@nonl
    #@-node:ekr.20031218072017.3950:divideLeoSplitter
    #@+node:ekr.20031218072017.3951:onDrag...
    def onDragMainSplitBar (self, event):
        self.onDragSplitterBar(event,self.splitVerticalFlag)

    def onDragSecondarySplitBar (self, event):
        self.onDragSplitterBar(event,not self.splitVerticalFlag)

    def onDragSplitterBar (self, event, verticalFlag):

        # x and y are the coordinates of the cursor relative to the bar, not the main window.
        bar = event.widget
        x = event.x
        y = event.y
        top = bar.winfo_toplevel()

        if verticalFlag:
            # Panes arranged vertically; horizontal splitter bar
            wRoot = top.winfo_rooty()
            barRoot = bar.winfo_rooty()
            wMax = top.winfo_height()
            offset = float(barRoot) + y - wRoot
        else:
            # Panes arranged horizontally; vertical splitter bar
            wRoot = top.winfo_rootx()
            barRoot = bar.winfo_rootx()
            wMax = top.winfo_width()
            offset = float(barRoot) + x - wRoot

        # Adjust the pixels, not the frac.
        if offset < 3: offset = 3
        if offset > wMax - 2: offset = wMax - 2
        # Redraw the splitter as the drag is occuring.
        frac = float(offset) / wMax
        # g.trace(frac)
        self.divideLeoSplitter(verticalFlag, frac)
    #@-node:ekr.20031218072017.3951:onDrag...
    #@+node:ekr.20031218072017.3952:placeSplitter
    def placeSplitter (self,bar,pane1,pane2,verticalFlag):

        # if self.bigTree:
            # pane1,pane2 = pane2,pane1

        if verticalFlag:
            # Panes arranged vertically; horizontal splitter bar
            pane1.place(relx=0.5, rely =   0, anchor="n", relwidth=1.0, relheight=0.5)
            pane2.place(relx=0.5, rely = 1.0, anchor="s", relwidth=1.0, relheight=0.5)
            bar.place  (relx=0.5, rely = 0.5, anchor="c", relwidth=1.0)
        else:
            # Panes arranged horizontally; vertical splitter bar
            # adj gives tree pane more room when tiling vertically.
            adj = g.choose(verticalFlag != self.splitVerticalFlag,0.65,0.5)
            pane1.place(rely=0.5, relx =   0, anchor="w", relheight=1.0, relwidth=adj)
            pane2.place(rely=0.5, relx = 1.0, anchor="e", relheight=1.0, relwidth=1.0-adj)
            bar.place  (rely=0.5, relx = adj, anchor="c", relheight=1.0)
    #@-node:ekr.20031218072017.3952:placeSplitter
    #@-node:ekr.20041221123325:tkFrame.createLeoSplitters & helpers
    #@+node:ekr.20031218072017.3964:Destroying the tkFrame
    #@+node:ekr.20031218072017.1975:destroyAllObjects
    def destroyAllObjects (self):

        """Clear all links to objects in a Leo window."""

        frame = self ; c = self.c ; tree = frame.tree ; body = self.body

        # g.printGcAll()

        # Do this first.
        #@    << clear all vnodes and tnodes in the tree >>
        #@+node:ekr.20031218072017.1976:<< clear all vnodes and tnodes in the tree>>
        # Using a dict here is essential for adequate speed.
        vList = [] ; tDict = {}

        for p in c.allNodes_iter():
            vList.append(p.v)
            if p.v.t:
                key = id(p.v.t)
                if not tDict.has_key(key):
                    tDict[key] = p.v.t

        for key in tDict.keys():
            g.clearAllIvars(tDict[key])

        for v in vList:
            g.clearAllIvars(v)

        vList = [] ; tDict = {} # Remove these references immediately.
        #@-node:ekr.20031218072017.1976:<< clear all vnodes and tnodes in the tree>>
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

    #@-node:ekr.20031218072017.1975:destroyAllObjects
    #@+node:ekr.20031218072017.3965:destroyAllPanels
    def destroyAllPanels (self):

        """Destroy all panels attached to this frame."""

        panels = (self.comparePanel, self.colorPanel, self.findPanel, self.fontPanel, self.prefsPanel)

        for panel in panels:
            if panel:
                panel.top.destroy()
    #@-node:ekr.20031218072017.3965:destroyAllPanels
    #@+node:ekr.20031218072017.1974:destroySelf (tkFrame)
    def destroySelf (self):

        # g.trace(self)

        # Remember these: we are about to destroy all of our ivars!
        top = self.top 
        c = self.c

        # Indicate that the commander is no longer valid.
        c.exists = False

        # New in Leo 4.4.8: Finish all window tasks before killing the window.
        top.update()

        # g.trace(self)

        # Important: this destroys all the objects of the commander too.
        self.destroyAllObjects()

        # New in Leo 4.4.8: Finish all window tasks before killing the window.
        top.update()

        c.exists = False # Make sure this one ivar has not been destroyed.

        top.destroy()
    #@-node:ekr.20031218072017.1974:destroySelf (tkFrame)
    #@-node:ekr.20031218072017.3964:Destroying the tkFrame
    #@-node:ekr.20031218072017.3941: Birth & Death (tkFrame)
    #@+node:ekr.20041223104933:class tkStatusLineClass (tkFrame)
    class tkStatusLineClass:

        '''A class representing the status line.'''

        #@    @+others
        #@+node:ekr.20031218072017.3961: ctor
        def __init__ (self,c,parentFrame):

            self.c = c
            self.colorTags = [] # list of color names used as tags.
            self.enabled = False
            self.isVisible = False
            self.lastRow = self.lastCol = 0
            self.log = c.frame.log
            #if 'black' not in self.log.colorTags:
            #    self.log.colorTags.append("black")
            self.parentFrame = parentFrame
            self.statusFrame = Tk.Frame(parentFrame,bd=2)
            text = "line 0, col 0"
            width = len(text) + 4
            self.labelWidget = Tk.Label(self.statusFrame,text=text,width=width,anchor="w")
            self.labelWidget.pack(side="left",padx=1)

            bg = self.statusFrame.cget("background")
            self.textWidget = w = g.app.gui.bodyTextWidget(
                self.statusFrame,
                height=1,state="disabled",bg=bg,relief="groove",name='status-line')
            self.textWidget.pack(side="left",expand=1,fill="x")
            w.bind("<Button-1>", self.onActivate)
            self.show()

            c.frame.statusFrame = self.statusFrame
            c.frame.statusLabel = self.labelWidget
            c.frame.statusText  = self.textWidget
        #@-node:ekr.20031218072017.3961: ctor
        #@+node:ekr.20031218072017.3962:clear
        def clear (self):

            w = self.textWidget
            if not w: return

            w.configure(state="normal")
            w.delete(0,"end")
            w.configure(state="disabled")
        #@-node:ekr.20031218072017.3962:clear
        #@+node:EKR.20040424153344:enable, disable & isEnabled
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
        #@-node:EKR.20040424153344:enable, disable & isEnabled
        #@+node:ekr.20041026132435:get
        def get (self):

            w = self.textWidget
            if w:
                return w.getAllText()
            else:
                return ""
        #@-node:ekr.20041026132435:get
        #@+node:ekr.20041223114744:getFrame
        def getFrame (self):

            return self.statusFrame
        #@-node:ekr.20041223114744:getFrame
        #@+node:ekr.20050120093555:onActivate
        def onActivate (self,event=None):

            # Don't change background as the result of simple mouse clicks.
            background = self.statusFrame.cget("background")
            self.enable(background=background)
        #@-node:ekr.20050120093555:onActivate
        #@+node:ekr.20041223111916:pack & show
        def pack (self):

            if not self.isVisible:
                self.isVisible = True
                self.statusFrame.pack(fill="x",pady=1)

        show = pack
        #@-node:ekr.20041223111916:pack & show
        #@+node:ekr.20031218072017.3963:put (leoTkinterFrame:statusLineClass)
        def put(self,s,color=None):

            # g.trace('tkStatusLine',self.textWidget,s)

            w = self.textWidget
            if not w:
                g.trace('tkStatusLine','***** disabled')
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
        #@-node:ekr.20031218072017.3963:put (leoTkinterFrame:statusLineClass)
        #@+node:ekr.20071215114822:setBindings (tkStatusLine)
        def setBindings (self):

            k = self.c.keyHandler ; w = self.textWidget

            w.bind('<Key>',k.masterKeyHandler)

            k.completeAllBindingsForWidget(w)
        #@-node:ekr.20071215114822:setBindings (tkStatusLine)
        #@+node:ekr.20041223111916.1:unpack & hide
        def unpack (self):

            if self.isVisible:
                self.isVisible = False
                self.statusFrame.pack_forget()

        hide = unpack
        #@-node:ekr.20041223111916.1:unpack & hide
        #@+node:ekr.20031218072017.1733:update (statusLine)
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

            # Important: this does not change the focus because labels never get focus.
            self.labelWidget.configure(text="line %d, col %d" % (row,col))
            self.lastRow = row
            self.lastCol = col
        #@-node:ekr.20031218072017.1733:update (statusLine)
        #@-others
    #@-node:ekr.20041223104933:class tkStatusLineClass (tkFrame)
    #@+node:ekr.20041223102225:class tkIconBarClass
    class tkIconBarClass:

        '''A class representing the singleton Icon bar'''

        #@    @+others
        #@+node:ekr.20041223102225.1: ctor
        def __init__ (self,c,parentFrame):

            self.c = c

            self.buttons = {}
            self.iconFrame = w = Tk.Frame(parentFrame,height="5m",bd=2,relief="groove")
            self.c.frame.iconFrame = self.iconFrame
            self.font = None
            self.parentFrame = parentFrame
            self.visible = False
            self.show()
        #@-node:ekr.20041223102225.1: ctor
        #@+node:ekr.20031218072017.3958:add
        def add(self,*args,**keys):

            """Add a button containing text or a picture to the icon bar.

            Pictures take precedence over text"""

            c = self.c ; f = self.iconFrame
            text = keys.get('text')
            imagefile = keys.get('imagefile')
            image = keys.get('image')
            command = keys.get('command')
            bg = keys.get('bg')

            if not imagefile and not image and not text: return

            # First define n.
            try:
                g.app.iconWidgetCount += 1
                n = g.app.iconWidgetCount
            except:
                n = g.app.iconWidgetCount = 1

            if not command:
                def commandCallback():
                    print "command for widget %s" % (n)
                command = commandCallback

            if imagefile or image:
                #@        << create a picture >>
                #@+node:ekr.20031218072017.3959:<< create a picture >>
                try:
                    if imagefile:
                        # Create the image.  Throws an exception if file not found
                        imagefile = g.os_path_join(g.app.loadDir,imagefile)
                        imagefile = g.os_path_normpath(imagefile)
                        image = Tk.PhotoImage(master=g.app.root,file=imagefile)

                        # Must keep a reference to the image!
                        try:
                            refs = g.app.iconImageRefs
                        except:
                            refs = g.app.iconImageRefs = []

                        refs.append((imagefile,image),)

                    if not bg:
                        bg = f.cget("bg")

                    b = Tk.Button(f,image=image,relief="flat",bd=0,command=command,bg=bg)
                    b.pack(side="left",fill="y")
                    return b

                except:
                    g.es_exception()
                    return None
                #@-node:ekr.20031218072017.3959:<< create a picture >>
                #@nl
            elif text:
                b = Tk.Button(f,text=text,relief="groove",bd=2,command=command)
                if not self.font:
                    self.font = c.config.getFontFromParams(
                        "button_text_font_family", "button_text_font_size",
                        "button_text_font_slant",  "button_text_font_weight",)
                b.configure(font=self.font)
                # elif sys.platform.startswith('win'):
                    # width = max(6,len(text))
                    # b.configure(width=width,font=('verdana',7,'bold'))
                if bg: b.configure(bg=bg)
                b.pack(side="left", fill="none")
                return b

            return None
        #@-node:ekr.20031218072017.3958:add
        #@+node:ekr.20031218072017.3956:clear
        def clear(self):

            """Destroy all the widgets in the icon bar"""

            f = self.iconFrame

            for slave in f.pack_slaves():
                slave.destroy()
            self.visible = False

            f.configure(height="5m") # The default height.
            g.app.iconWidgetCount = 0
            g.app.iconImageRefs = []
        #@-node:ekr.20031218072017.3956:clear
        #@+node:ekr.20061213091114.1:deleteButton (new in Leo 4.4.3)
        def deleteButton (self,w):

            w.pack_forget()
        #@-node:ekr.20061213091114.1:deleteButton (new in Leo 4.4.3)
        #@+node:ekr.20041223114821:getFrame
        def getFrame (self):

            return self.iconFrame
        #@-node:ekr.20041223114821:getFrame
        #@+node:ekr.20041223102225.2:pack (show)
        def pack (self):

            """Show the icon bar by repacking it"""

            if not self.visible:
                self.visible = True
                self.iconFrame.pack(fill="x",pady=2)

        show = pack
        #@-node:ekr.20041223102225.2:pack (show)
        #@+node:ekr.20061213092103:setCommandForButton (new in Leo 4.4.3)
        def setCommandForButton(self,b,command):

            b.configure(command=command)
        #@-node:ekr.20061213092103:setCommandForButton (new in Leo 4.4.3)
        #@+node:ekr.20031218072017.3955:unpack (hide)
        def unpack (self):

            """Hide the icon bar by unpacking it.

            A later call to show will repack it in a new location."""

            if self.visible:
                self.visible = False
                self.iconFrame.pack_forget()

        hide = unpack
        #@-node:ekr.20031218072017.3955:unpack (hide)
        #@-others
    #@-node:ekr.20041223102225:class tkIconBarClass
    #@+node:ekr.20051014154752:Minibuffer methods
    #@+node:ekr.20060203115311:showMinibuffer
    def showMinibuffer (self):

        '''Make the minibuffer visible.'''

        frame = self

        if not frame.minibufferVisible:
            frame.minibufferFrame.pack(side='bottom',fill='x')
            frame.minibufferVisible = True
    #@-node:ekr.20060203115311:showMinibuffer
    #@+node:ekr.20060203115311.1:hideMinibuffer
    def hideMinibuffer (self):

        '''Hide the minibuffer.'''

        frame = self
        if frame.minibufferVisible:
            frame.minibufferFrame.pack_forget()
            frame.minibufferVisible = False
    #@-node:ekr.20060203115311.1:hideMinibuffer
    #@+node:ekr.20050920094212:f.createMiniBufferWidget
    def createMiniBufferWidget (self):

        '''Create the minbuffer below the status line.'''

        frame = self ; c = frame.c

        frame.minibufferFrame = f = Tk.Frame(frame.outerFrame,relief='flat',borderwidth=0)
        if c.showMinibuffer:
            f.pack(side='bottom',fill='x')

        lab = Tk.Label(f,text='mini-buffer',justify='left',anchor='nw',foreground='blue')
        lab.pack(side='left')

        if c.useTextMinibuffer:
            label = g.app.gui.plainTextWidget(
                f,height=1,relief='groove',background='lightgrey',name='minibuffer')
            label.pack(side='left',fill='x',expand=1,padx=2,pady=1)
        else:
            label = Tk.Label(f,relief='groove',justify='left',anchor='w',name='minibuffer')
            label.pack(side='left',fill='both',expand=1,padx=2,pady=1)

        frame.minibufferVisible = c.showMinibuffer

        return label
    #@-node:ekr.20050920094212:f.createMiniBufferWidget
    #@+node:ekr.20060203114017:f.setMinibufferBindings
    def setMinibufferBindings (self):

        '''Create bindings for the minibuffer..'''

        f = self ; c = f.c ; k = c.k ; w = f.miniBufferWidget

        if not c.useTextMinibuffer: return

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
            w.bind(kind,callback)

        if 0:
            if sys.platform.startswith('win'):
                # Support Linux middle-button paste easter egg.
                w.bind("<Button-2>",f.OnPaste)
    #@-node:ekr.20060203114017:f.setMinibufferBindings
    #@-node:ekr.20051014154752:Minibuffer methods
    #@+node:ekr.20031218072017.3967:Configuration (tkFrame)
    #@+node:ekr.20031218072017.3968:configureBar (tkFrame)
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
    #@-node:ekr.20031218072017.3968:configureBar (tkFrame)
    #@+node:ekr.20031218072017.3969:configureBarsFromConfig (tkFrame)
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
    #@-node:ekr.20031218072017.3969:configureBarsFromConfig (tkFrame)
    #@+node:ekr.20031218072017.2246:reconfigureFromConfig (tkFrame)
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
    #@-node:ekr.20031218072017.2246:reconfigureFromConfig (tkFrame)
    #@+node:ekr.20031218072017.1625:setInitialWindowGeometry (tkFrame)
    def setInitialWindowGeometry(self):

        """Set the position and size of the frame to config params."""

        c = self.c

        h = c.config.getInt("initial_window_height") or 500
        w = c.config.getInt("initial_window_width") or 600
        x = c.config.getInt("initial_window_left") or 10
        y = c.config.getInt("initial_window_top") or 10

        if h and w and x and y:
            self.setTopGeometry(w,h,x,y)
    #@-node:ekr.20031218072017.1625:setInitialWindowGeometry (tkFrame)
    #@+node:ekr.20031218072017.722:setTabWidth (tkFrame)
    def setTabWidth (self, w):

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
    #@nonl
    #@-node:ekr.20031218072017.722:setTabWidth (tkFrame)
    #@+node:ekr.20031218072017.1540:setWrap (tkFrame)
    def setWrap (self,p):

        c = self.c
        theDict = g.scanDirectives(c,p)
        if not theDict: return

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
    #@-node:ekr.20031218072017.1540:setWrap (tkFrame)
    #@+node:ekr.20031218072017.2307:setTopGeometry (tkFrame)
    def setTopGeometry(self,w,h,x,y,adjustSize=True):

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
    #@-node:ekr.20031218072017.2307:setTopGeometry (tkFrame)
    #@+node:ekr.20031218072017.3970:reconfigurePanes (use config bar_width) (tkFrame)
    def reconfigurePanes (self):

        c = self.c

        border = c.config.getInt('additional_body_text_border')
        if border == None: border = 0

        # The body pane needs a _much_ bigger border when tiling horizontally.
        border = g.choose(self.splitVerticalFlag,2+border,6+border)
        self.body.bodyCtrl.configure(bd=border) # 2007/10/25

        # The log pane needs a slightly bigger border when tiling vertically.
        border = g.choose(self.splitVerticalFlag,4,2) 
        self.log.configureBorder(border)
    #@-node:ekr.20031218072017.3970:reconfigurePanes (use config bar_width) (tkFrame)
    #@+node:ekr.20060915124834:resizePanesToRatio (tkFrame)
    def resizePanesToRatio(self,ratio,ratio2):

        # g.trace(ratio,ratio2,g.callers())

        self.divideLeoSplitter(self.splitVerticalFlag,ratio)
        self.divideLeoSplitter(not self.splitVerticalFlag,ratio2)
    #@nonl
    #@-node:ekr.20060915124834:resizePanesToRatio (tkFrame)
    #@-node:ekr.20031218072017.3967:Configuration (tkFrame)
    #@+node:ekr.20031218072017.3971:Event handlers (tkFrame)
    #@+node:ekr.20031218072017.3972:frame.OnCloseLeoEvent
    # Called from quit logic and when user closes the window.
    # Returns True if the close happened.

    def OnCloseLeoEvent(self):

        f = self ; c = f.c

        if c.inCommand:
            # g.trace('requesting window close')
            c.requestCloseWindow = True
        else:
            g.app.closeLeoWindow(self)
    #@-node:ekr.20031218072017.3972:frame.OnCloseLeoEvent
    #@+node:ekr.20031218072017.3973:frame.OnControlKeyUp/Down
    def OnControlKeyDown (self,event=None):

        # __pychecker__ = '--no-argsused' # event not used.

        self.controlKeyIsDown = True

    def OnControlKeyUp (self,event=None):

        # __pychecker__ = '--no-argsused' # event not used.

        self.controlKeyIsDown = False
    #@-node:ekr.20031218072017.3973:frame.OnControlKeyUp/Down
    #@+node:ekr.20031218072017.3975:OnActivateBody (tkFrame)
    def OnActivateBody (self,event=None):

        # __pychecker__ = '--no-argsused' # event not used.

        try:
            frame = self ; c = frame.c
            c.setLog()
            w = c.get_focus()
            if w != c.frame.body.bodyCtrl:
                frame.tree.OnDeactivate()
            c.bodyWantsFocus()
        except:
            g.es_event_exception("activate body")

        return 'break'
    #@-node:ekr.20031218072017.3975:OnActivateBody (tkFrame)
    #@+node:ekr.20031218072017.2253:OnActivateLeoEvent, OnDeactivateLeoEvent
    def OnActivateLeoEvent(self,event=None):

        '''Handle a click anywhere in the Leo window.'''

        # __pychecker__ = '--no-argsused' # event.

        self.c.setLog()

    def OnDeactivateLeoEvent(self,event=None):

        pass # This causes problems on the Mac.
    #@-node:ekr.20031218072017.2253:OnActivateLeoEvent, OnDeactivateLeoEvent
    #@+node:ekr.20031218072017.3976:OnActivateTree
    def OnActivateTree (self,event=None):

        try:
            frame = self ; c = frame.c
            c.setLog()

            if 0: # Do NOT do this here!
                # OnActivateTree can get called when the tree gets DE-activated!!
                c.bodyWantsFocus()

        except:
            g.es_event_exception("activate tree")
    #@-node:ekr.20031218072017.3976:OnActivateTree
    #@+node:ekr.20031218072017.3977:OnBodyClick, OnBodyRClick (Events)
    def OnBodyClick (self,event=None):

        try:
            c = self.c ; p = c.currentPosition()
            if not g.doHook("bodyclick1",c=c,p=p,v=p,event=event):
                self.OnActivateBody(event=event)
            g.doHook("bodyclick2",c=c,p=p,v=p,event=event)
        except:
            g.es_event_exception("bodyclick")

    def OnBodyRClick(self,event=None):

        try:
            c = self.c ; p = c.currentPosition()
            if not g.doHook("bodyrclick1",c=c,p=p,v=p,event=event):
                pass # By default Leo does nothing.
            g.doHook("bodyrclick2",c=c,p=p,v=p,event=event)
        except:
            g.es_event_exception("iconrclick")
    #@-node:ekr.20031218072017.3977:OnBodyClick, OnBodyRClick (Events)
    #@+node:ekr.20031218072017.3978:OnBodyDoubleClick (Events)
    def OnBodyDoubleClick (self,event=None):

        try:
            c = self.c ; p = c.currentPosition()
            if event and not g.doHook("bodydclick1",c=c,p=p,v=p,event=event):
                c.editCommands.extendToWord(event) # Handles unicode properly.
            g.doHook("bodydclick2",c=c,p=p,v=p,event=event)
        except:
            g.es_event_exception("bodydclick")

        return "break" # Restore this to handle proper double-click logic.
    #@-node:ekr.20031218072017.3978:OnBodyDoubleClick (Events)
    #@+node:ekr.20031218072017.1803:OnMouseWheel (Tomaz Ficko)
    # Contributed by Tomaz Ficko.  This works on some systems.
    # On XP it causes a crash in tcl83.dll.  Clearly a Tk bug.

    def OnMouseWheel(self, event=None):

        try:
            if event.delta < 1:
                self.canvas.yview(Tk.SCROLL, 1, Tk.UNITS)
            else:
                self.canvas.yview(Tk.SCROLL, -1, Tk.UNITS)
        except:
            g.es_event_exception("scroll wheel")

        return "break"
    #@-node:ekr.20031218072017.1803:OnMouseWheel (Tomaz Ficko)
    #@-node:ekr.20031218072017.3971:Event handlers (tkFrame)
    #@+node:ekr.20031218072017.3979:Gui-dependent commands
    #@+node:ekr.20060209110128:Minibuffer commands... (tkFrame)

    #@+node:ekr.20060209110128.1:contractPane
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
    #@-node:ekr.20060209110128.1:contractPane
    #@+node:ekr.20060209110128.2:expandPane
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
    #@-node:ekr.20060209110128.2:expandPane
    #@+node:ekr.20060210123852:fullyExpandPane
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
    #@-node:ekr.20060210123852:fullyExpandPane
    #@+node:ekr.20060209143933:hidePane
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
    #@-node:ekr.20060209143933:hidePane
    #@+node:ekr.20060209110936:expand/contract/hide...Pane
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
    #@-node:ekr.20060209110936:expand/contract/hide...Pane
    #@+node:ekr.20060210123852.1:fullyExpand/hide...Pane
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
    #@-node:ekr.20060210123852.1:fullyExpand/hide...Pane
    #@-node:ekr.20060209110128:Minibuffer commands... (tkFrame)
    #@+node:ekr.20031218072017.3984:Window Menu...
    #@+node:ekr.20031218072017.3985:toggleActivePane (tkFrame)
    def toggleActivePane (self,event=None):

        '''Toggle the focus between the outline and body panes.'''

        frame = self ; c = frame.c

        if c.get_focus() == frame.body.bodyCtrl: # 2007/10/25
            c.treeWantsFocusNow()
        else:
            c.endEditing()
            c.bodyWantsFocusNow()
    #@-node:ekr.20031218072017.3985:toggleActivePane (tkFrame)
    #@+node:ekr.20031218072017.3986:cascade
    def cascade (self,event=None):

        '''Cascade all Leo windows.'''

        x,y,delta = 10,10,10
        for frame in g.app.windowList:
            top = frame.top

            # Compute w,h
            top.update_idletasks() # Required to get proper info.
            geom = top.geometry() # geom = "WidthxHeight+XOffset+YOffset"
            dim,junkx,junky = string.split(geom,'+')
            w,h = string.split(dim,'x')
            w,h = int(w),int(h)

            # Set new x,y and old w,h
            frame.setTopGeometry(w,h,x,y,adjustSize=False)

            # Compute the new offsets.
            x += 30 ; y += 30
            if x > 200:
                x = 10 + delta ; y = 40 + delta
                delta += 10
    #@-node:ekr.20031218072017.3986:cascade
    #@+node:ekr.20031218072017.3987:equalSizedPanes
    def equalSizedPanes (self,event=None):

        '''Make the outline and body panes have the same size.'''

        frame = self
        frame.resizePanesToRatio(0.5,frame.secondary_ratio)
    #@-node:ekr.20031218072017.3987:equalSizedPanes
    #@+node:ekr.20031218072017.3988:hideLogWindow
    def hideLogWindow (self,event=None):

        frame = self
        frame.divideLeoSplitter2(0.99, not frame.splitVerticalFlag)
    #@-node:ekr.20031218072017.3988:hideLogWindow
    #@+node:ekr.20031218072017.3989:minimizeAll
    def minimizeAll (self,event=None):

        '''Minimize all Leo's windows.'''

        self.minimize(g.app.pythonFrame)
        for frame in g.app.windowList:
            self.minimize(frame)
            self.minimize(frame.findPanel)

    def minimize(self,frame):

        if frame and frame.top.state() == "normal":
            frame.top.iconify()
    #@-node:ekr.20031218072017.3989:minimizeAll
    #@+node:ekr.20031218072017.3990:toggleSplitDirection (tkFrame)
    # The key invariant: self.splitVerticalFlag tells the alignment of the main splitter.

    def toggleSplitDirection (self,event=None):

        '''Toggle the split direction in the present Leo window.'''

        # Switch directions.
        c = self.c
        self.splitVerticalFlag = not self.splitVerticalFlag
        orientation = g.choose(self.splitVerticalFlag,"vertical","horizontal")
        c.config.set("initial_splitter_orientation","string",orientation)

        self.toggleTkSplitDirection(self.splitVerticalFlag)
    #@+node:ekr.20041221122440.2:toggleTkSplitDirection
    def toggleTkSplitDirection (self,verticalFlag):

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
    #@-node:ekr.20041221122440.2:toggleTkSplitDirection
    #@-node:ekr.20031218072017.3990:toggleSplitDirection (tkFrame)
    #@+node:EKR.20040422130619:resizeToScreen
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
    #@-node:EKR.20040422130619:resizeToScreen
    #@-node:ekr.20031218072017.3984:Window Menu...
    #@+node:ekr.20031218072017.3991:Help Menu...
    #@+node:ekr.20031218072017.3992:leoHelp
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
    #@+node:ekr.20031218072017.3993:showProgressBar
    def showProgressBar (self,count,size,total):

        # g.trace("count,size,total:",count,size,total)
        if self.scale == None:
            #@        << create the scale widget >>
            #@+node:ekr.20031218072017.3994:<< create the scale widget >>
            top = Tk.Toplevel()
            top.title("Download progress")
            self.scale = scale = Tk.Scale(top,state="normal",orient="horizontal",from_=0,to=total)
            scale.pack()
            top.lift()
            #@-node:ekr.20031218072017.3994:<< create the scale widget >>
            #@nl
        self.scale.set(count*size)
        self.scale.update_idletasks()
    #@-node:ekr.20031218072017.3993:showProgressBar
    #@-node:ekr.20031218072017.3992:leoHelp
    #@-node:ekr.20031218072017.3991:Help Menu...
    #@-node:ekr.20031218072017.3979:Gui-dependent commands
    #@+node:ekr.20050120083053:Delayed Focus (tkFrame)
    #@+at 
    #@nonl
    # New in 4.3. The proper way to change focus is to call 
    # c.frame.xWantsFocus.
    # 
    # Important: This code never calls select, so there can be no race 
    # condition here
    # that alters text improperly.
    #@-at
    #@-node:ekr.20050120083053:Delayed Focus (tkFrame)
    #@+node:ekr.20031218072017.3995:Tk bindings... (tkFrame)
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
        return self.top.title()

    def setTitle (self,title):
        return self.top.title(title)

    def get_window_info(self):
        return g.app.gui.get_window_info(self.top)

    def iconify(self):
        self.top.iconify()

    def deiconify (self):
        self.top.deiconify()

    def lift (self):
        self.top.lift()

    def update (self):
        self.top.update()
    #@-node:ekr.20031218072017.3995:Tk bindings... (tkFrame)
    #@-others
#@-node:ekr.20031218072017.3940:class leoTkinterFrame
#@+node:ekr.20031218072017.4039:class leoTkinterLog
class leoTkinterLog (leoFrame.leoLog):

    """A class that represents the log pane of a Tkinter window."""

    #@    @+others
    #@+node:ekr.20051016095907:tkLog Birth
    #@+node:ekr.20031218072017.4040:tkLog.__init__
    def __init__ (self,frame,parentFrame):

        # g.trace("leoTkinterLog")

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



    #@-node:ekr.20031218072017.4040:tkLog.__init__
    #@+node:ekr.20031218072017.4042:tkLog.createControl
    def createControl (self,parentFrame):

        c = self.c

        self.nb = Pmw.NoteBook(parentFrame,
            borderwidth = 1, pagemargin = 0,
            raisecommand = self.raiseTab,
            lowercommand = self.lowerTab,
            arrownavigation = 0,
        )

        menu = self.makeTabMenu(tabName=None)

        def hullMenuCallback(event):
            return self.onRightClick(event,menu)

        self.nb.bind('<Button-3>',hullMenuCallback)

        self.nb.pack(fill='both',expand=1)
        self.selectTab('Log') # Create and activate the default tabs.

        return self.logCtrl
    #@-node:ekr.20031218072017.4042:tkLog.createControl
    #@+node:ekr.20070114070939:tkLog.finishCreate
    def finishCreate (self):

        # g.trace('tkLog')

        c = self.c ; log = self

        c.searchCommands.openFindTab(show=False)
        c.spellCommands.openSpellTab()
        log.selectTab('Log')
    #@-node:ekr.20070114070939:tkLog.finishCreate
    #@+node:ekr.20071002143627:tkLog.createCanvasWidget
    def createCanvasWidget (self,parentFrame):

        self.logNumber += 1

        w = Tk.Canvas(parentFrame)

        logBar = Tk.Scrollbar(parentFrame,name="logBar")
        w['yscrollcommand'] = logBar.set
        logBar['command'] = w.yview
        logBar.pack(side="right", fill="y")

        logXBar = Tk.Scrollbar(parentFrame,name='logXBar',orient="horizontal") 
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
    #@-node:ekr.20071002143627:tkLog.createCanvasWidget
    #@+node:ekr.20051016103459:tkLog.createTextWidget
    def createTextWidget (self,parentFrame):

        self.logNumber += 1
        log = g.app.gui.plainTextWidget(
            parentFrame,name="log-%d" % self.logNumber,
            setgrid=0,wrap=self.wrap,bd=2,bg="white",relief="flat")

        logBar = Tk.Scrollbar(parentFrame,name="logBar")

        log['yscrollcommand'] = logBar.set
        logBar['command'] = log.yview

        logBar.pack(side="right", fill="y")
        # rr 8/14/02 added horizontal elevator 
        if self.wrap == "none": 
            logXBar = Tk.Scrollbar( 
                parentFrame,name='logXBar',orient="horizontal") 
            log['xscrollcommand'] = logXBar.set 
            logXBar['command'] = log.xview 
            logXBar.pack(side="bottom", fill="x")
        log.pack(expand=1, fill="both")

        return log
    #@-node:ekr.20051016103459:tkLog.createTextWidget
    #@+node:ekr.20051019134106.1:tkLog.makeTabMenu
    def makeTabMenu (self,tabName=None,allowRename=True):

        '''Create a tab popup menu.'''

        # g.trace(tabName,g.callers())

        c = self.c
        hull = self.nb.component('hull') # A Tk.Canvas.

        menu = Tk.Menu(hull,tearoff=0)
        menu.add_command(label='New Tab',command=self.newTabFromMenu)
        menu.add_command(label='New CanvasTab',command=self.newCanvasTabFromMenu)

        if tabName:
            # Important: tabName is the name when the tab is created.
            # It is not affected by renaming, so we don't have to keep
            # track of the correspondence between this name and what is in the label.
            def deleteTabCallback():
                return self.deleteTab(tabName)

            label = g.choose(
                tabName in ('Find','Spell'),'Hide This Tab','Delete This Tab')
            menu.add_command(label=label,command=deleteTabCallback)

            def renameTabCallback():
                return self.renameTabFromMenu(tabName)

            if allowRename:
                menu.add_command(label='Rename This Tab',command=renameTabCallback)

        return menu
    #@-node:ekr.20051019134106.1:tkLog.makeTabMenu
    #@-node:ekr.20051016095907:tkLog Birth
    #@+node:ekr.20051016095907.1:Config & get/saveState
    #@+node:ekr.20031218072017.4041:tkLog.configureBorder & configureFont
    def configureBorder(self,border):

        self.logCtrl.configure(bd=border)

    def configureFont(self,font):

        self.logCtrl.configure(font=font)
    #@-node:ekr.20031218072017.4041:tkLog.configureBorder & configureFont
    #@+node:ekr.20031218072017.4043:tkLog.getFontConfig
    def getFontConfig (self):

        font = self.logCtrl.cget("font")
        # g.trace(font)
        return font
    #@-node:ekr.20031218072017.4043:tkLog.getFontConfig
    #@+node:ekr.20041222043017:tkLog.restoreAllState
    def restoreAllState (self,d):

        '''Restore the log from a dict created by saveAllState.'''

        logCtrl = self.logCtrl

        # Restore the text.
        text = d.get('text')
        logCtrl.insert('end',text)

        # Restore all colors.
        colors = d.get('colors')
        for color in colors.keys():
            if color not in self.colorTags:
                self.colorTags.append(color)
                logCtrl.tag_config(color,foreground=color)
            items = list(colors.get(color))
            while items:
                start,stop = items[0],items[1]
                items = items[2:]
                logCtrl.tag_add(color,start,stop)
    #@-node:ekr.20041222043017:tkLog.restoreAllState
    #@+node:ekr.20041222043017.1:tkLog.saveAllState
    def saveAllState (self):

        '''Return a dict containing all data needed to recreate the log in another widget.'''

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
    #@-node:ekr.20041222043017.1:tkLog.saveAllState
    #@+node:ekr.20041217135735.2:tkLog.setColorFromConfig
    def setColorFromConfig (self):

        c = self.c

        bg = c.config.getColor("log_pane_background_color") or 'white'

        try:
            self.logCtrl.configure(bg=bg)
        except:
            g.es("exception setting log pane background color")
            g.es_exception()
    #@-node:ekr.20041217135735.2:tkLog.setColorFromConfig
    #@+node:ekr.20031218072017.4046:tkLog.setFontFromConfig
    def SetWidgetFontFromConfig (self,logCtrl=None):

        c = self.c

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
    #@-node:ekr.20031218072017.4046:tkLog.setFontFromConfig
    #@-node:ekr.20051016095907.1:Config & get/saveState
    #@+node:ekr.20051016095907.2:Focus & update (tkLog)
    #@+node:ekr.20031218072017.4045:tkLog.onActivateLog
    def onActivateLog (self,event=None):

        try:
            self.c.setLog()
            self.frame.tree.OnDeactivate()
            self.c.logWantsFocus()
        except:
            g.es_event_exception("activate log")
    #@-node:ekr.20031218072017.4045:tkLog.onActivateLog
    #@+node:ekr.20031218072017.4044:tkLog.hasFocus
    def hasFocus (self):

        return self.c.get_focus() == self.logCtrl
    #@-node:ekr.20031218072017.4044:tkLog.hasFocus
    #@+node:ekr.20050208133438:forceLogUpdate
    def forceLogUpdate (self,s):

        if sys.platform == "darwin": # Does not work on MacOS X.
            try:
                print s, # Don't add a newline.
            except UnicodeError:
                # g.app may not be inited during scripts!
                print g.toEncodedString(s,'utf-8')
        else:
            self.logCtrl.update_idletasks()
    #@-node:ekr.20050208133438:forceLogUpdate
    #@-node:ekr.20051016095907.2:Focus & update (tkLog)
    #@+node:ekr.20051016101927:put & putnl (tkLog)
    #@+at 
    #@nonl
    # Printing uses self.logCtrl, so this code need not concern itself
    # with which tab is active.
    # 
    # Also, selectTab switches the contents of colorTags, so that is not 
    # concern.
    # It may be that Pmw will allow us to dispense with the colorTags logic...
    #@-at
    #@+node:ekr.20031218072017.1473:put
    # All output to the log stream eventually comes here.
    def put (self,s,color=None,tabName='Log'):

        c = self.c

        # print 'tkLog.put',s
        # print 'tkLog.put',len(s),g.callers()

        if g.app.quitting or not c or not c.exists:
            return

        if tabName:
            self.selectTab(tabName)

        # Note: this must be done after the call to selectTab.
        w = self.logCtrl
        if w:
            #@        << put s to log control >>
            #@+node:EKR.20040423082910:<< put s to log control >>
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
            #@-node:EKR.20040423082910:<< put s to log control >>
            #@nl
            self.logCtrl.update_idletasks()
        else:
            #@        << put s to logWaiting and print s >>
            #@+node:EKR.20040423082910.1:<< put s to logWaiting and print s >>
            g.app.logWaiting.append((s,color),)

            print "Null tkinter log"

            if type(s) == type(u""):
                s = g.toEncodedString(s,"ascii")

            print s
            #@-node:EKR.20040423082910.1:<< put s to logWaiting and print s >>
            #@nl
    #@-node:ekr.20031218072017.1473:put
    #@+node:ekr.20051016101927.1:putnl
    def putnl (self,tabName='Log'):

        if g.app.quitting:
            return

        # print 'tkLog.putnl' # ,g.callers()

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
            print "Null tkinter log"
            print
    #@-node:ekr.20051016101927.1:putnl
    #@-node:ekr.20051016101927:put & putnl (tkLog)
    #@+node:ekr.20051018061932:Tab (TkLog)
    #@+node:ekr.20051017212057:clearTab
    def clearTab (self,tabName,wrap='none'):

        self.selectTab(tabName,wrap=wrap)
        w = self.logCtrl
        if w: w.delete(0,'end')
    #@-node:ekr.20051017212057:clearTab
    #@+node:ekr.20071002143627.1:createCanvas
    def createCanvas (self,tabName=None):

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
    #@-node:ekr.20071002143627.1:createCanvas
    #@+node:ekr.20051024173701:createTab
    def createTab (self,tabName,createText=True,wrap='none'):

        # g.trace(tabName,wrap)

        c = self.c ; k = c.k
        tabFrame = self.nb.add(tabName)
        self.menu = self.makeTabMenu(tabName)
        if createText:
            #@        << Create the tab's text widget >>
            #@+node:ekr.20051018072306:<< Create the tab's text widget >>
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
            #@-node:ekr.20051018072306:<< Create the tab's text widget >>
            #@nl
        else:
            self.canvasDict [tabName] = None
            self.textDict [tabName] = None
            self.frameDict [tabName] = tabFrame

        if tabName != 'Log':
            # c.k doesn't exist when the log pane is created.
            # k.makeAllBindings will call setTabBindings('Log')
            self.setTabBindings(tabName)
    #@-node:ekr.20051024173701:createTab
    #@+node:ekr.20060613131217:cycleTabFocus
    def cycleTabFocus (self,event=None,stop_w = None):

        '''Cycle keyboard focus between the tabs in the log pane.'''

        c = self.c ; d = self.frameDict # Keys are page names. Values are Tk.Frames.
        w = d.get(self.tabName)
        # g.trace(self.tabName,w)
        values = d.values()
        if self.numberOfVisibleTabs() > 1:
            i = i2 = values.index(w) + 1
            if i == len(values): i = 0
            tabName = d.keys()[i]
            self.selectTab(tabName)
            return 
    #@nonl
    #@-node:ekr.20060613131217:cycleTabFocus
    #@+node:ekr.20051018102027:deleteTab
    def deleteTab (self,tabName,force=False):

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
    #@-node:ekr.20051018102027:deleteTab
    #@+node:ekr.20060204124347:hideTab
    def hideTab (self,tabName):

        # __pychecker__ = '--no-argsused' # tabName

        self.selectTab('Log')
    #@-node:ekr.20060204124347:hideTab
    #@+node:ekr.20051027114433:getSelectedTab
    def getSelectedTab (self):

        return self.tabName
    #@-node:ekr.20051027114433:getSelectedTab
    #@+node:ekr.20051018061932.1:lower/raiseTab
    def lowerTab (self,tabName):

        if tabName:
            b = self.nb.tab(tabName) # b is a Tk.Button.
            b.config(bg='grey80')
        self.c.invalidateFocus()
        self.c.bodyWantsFocus()

    def raiseTab (self,tabName):

        if tabName:
            b = self.nb.tab(tabName) # b is a Tk.Button.
            b.config(bg='LightSteelBlue1')
        self.c.invalidateFocus()
        self.c.bodyWantsFocus()
    #@-node:ekr.20051018061932.1:lower/raiseTab
    #@+node:ekr.20060613131345:numberOfVisibleTabs
    def numberOfVisibleTabs (self):

        return len([val for val in self.frameDict.values() if val != None])
    #@-node:ekr.20060613131345:numberOfVisibleTabs
    #@+node:ekr.20051019170806:renameTab
    def renameTab (self,oldName,newName):

        # g.trace('newName',newName)

        label = self.nb.tab(oldName)
        label.configure(text=newName)
    #@-node:ekr.20051019170806:renameTab
    #@+node:ekr.20051016101724.1:selectTab
    def selectTab (self,tabName,createText=True,wrap='none'):

        '''Create the tab if necessary and make it active.'''

        c = self.c

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
    #@-node:ekr.20051016101724.1:selectTab
    #@+node:ekr.20051022162730:setTabBindings
    def setTabBindings (self,tabName):

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
            w.bind(kind,handler)

        # Clicks in the tab area are harmless: use the old code.
        def tabMenuRightClickCallback(event,menu=self.menu):
            return self.onRightClick(event,menu)

        def tabMenuClickCallback(event,tabName=tabName):
            return self.onClick(event,tabName)

        tab.bind('<Button-1>',tabMenuClickCallback)
        tab.bind('<Button-3>',tabMenuRightClickCallback)

        k.completeAllBindingsForWidget(w)
    #@-node:ekr.20051022162730:setTabBindings
    #@+node:bobjack.20080401113759.3:onLogTextRightClick
    def onLogTextRightClick(self, event):

        g.doHook('rclick-popup', c=self.c, event=event, context_menu='log')
    #@-node:bobjack.20080401113759.3:onLogTextRightClick
    #@+node:ekr.20071003090546:setCanvasTabBindings
    def setCanvasTabBindings (self,tabName,menu):

        c = self.c ; tab = self.nb.tab(tabName)

        def tabMenuRightClickCallback(event,menu=menu):
            return self.onRightClick(event,menu)

        def tabMenuClickCallback(event,tabName=tabName):
            return self.onClick(event,tabName)

        tab.bind('<Button-1>',tabMenuClickCallback)
        tab.bind('<Button-3>',tabMenuRightClickCallback)

    #@-node:ekr.20071003090546:setCanvasTabBindings
    #@+node:ekr.20051019134106:Tab menu callbacks & helpers
    #@+node:ekr.20051019134422:onRightClick & onClick
    def onRightClick (self,event,menu):

        c = self.c
        menu.post(event.x_root,event.y_root)


    def onClick (self,event,tabName):

        self.selectTab(tabName)
    #@-node:ekr.20051019134422:onRightClick & onClick
    #@+node:ekr.20051019140004.1:newTabFromMenu & newCanvasTabFromMenu
    def newTabFromMenu (self,tabName='Log'):

        self.selectTab(tabName)

        # This is called by getTabName.
        def selectTabCallback (newName):
            return self.selectTab(newName)

        self.getTabName(selectTabCallback)

    def newCanvasTabFromMenu (self):

        self.createCanvas()
    #@-node:ekr.20051019140004.1:newTabFromMenu & newCanvasTabFromMenu
    #@+node:ekr.20051019165401:renameTabFromMenu
    def renameTabFromMenu (self,tabName):

        if tabName in ('Log','Completions'):
            g.es('can not rename',tabName,'tab',color='blue')
        else:
            def renameTabCallback (newName):
                return self.renameTab(tabName,newName)

            self.getTabName(renameTabCallback)
    #@-node:ekr.20051019165401:renameTabFromMenu
    #@+node:ekr.20051019172811:getTabName
    def getTabName (self,exitCallback):

        canvas = self.nb.component('hull')

        # Overlay what is there!
        c = self.c
        f = Tk.Frame(canvas)
        f.pack(side='top',fill='both',expand=1)

        row1 = Tk.Frame(f)
        row1.pack(side='top',expand=0,fill='x',pady=10)
        row2 = Tk.Frame(f)
        row2.pack(side='top',expand=0,fill='x')

        Tk.Label(row1,text='Tab name').pack(side='left')

        e = Tk.Entry(row1,background='white')
        e.pack(side='left')

        def getNameCallback (event=None):
            s = e.get().strip()
            f.pack_forget()
            if s: exitCallback(s)

        def closeTabNameCallback (event=None):
            f.pack_forget()

        b = Tk.Button(row2,text='Ok',width=6,command=getNameCallback)
        b.pack(side='left',padx=10)

        b = Tk.Button(row2,text='Cancel',width=6,command=closeTabNameCallback)
        b.pack(side='left')

        g.app.gui.set_focus(c,e)
        e.bind('<Return>',getNameCallback)
    #@-node:ekr.20051019172811:getTabName
    #@-node:ekr.20051019134106:Tab menu callbacks & helpers
    #@-node:ekr.20051018061932:Tab (TkLog)
    #@+node:ekr.20051019183105.3:tkLog color tab stuff
    def createColorPicker (self,tabName):

        log = self

        #@    << define colors >>
        #@+node:ekr.20051019183105.2:<< define colors >>
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
        #@-node:ekr.20051019183105.2:<< define colors >>
        #@nl

        parent = log.frameDict.get(tabName)
        w = log.textDict.get(tabName)
        w.pack_forget()

        colors = list(colors)
        bg = parent.cget('background')

        outer = Tk.Frame(parent,background=bg)
        outer.pack(side='top',fill='both',expand=1,pady=10)

        f = Tk.Frame(outer)
        f.pack(side='top',expand=0,fill='x')
        f1 = Tk.Frame(f) ; f1.pack(side='top',expand=0,fill='x')
        f2 = Tk.Frame(f) ; f2.pack(side='top',expand=1,fill='x')
        f3 = Tk.Frame(f) ; f3.pack(side='top',expand=1,fill='x')

        label = g.app.gui.plainTextWidget(f1,height=1,width=20)
        label.insert('1.0','Color name or value...')
        label.pack(side='left',pady=6)

        #@    << create optionMenu and callback >>
        #@+node:ekr.20051019183105.4:<< create optionMenu and callback >>
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
        #@-node:ekr.20051019183105.4:<< create optionMenu and callback >>
        #@nl
        #@    << create picker button and callback >>
        #@+node:ekr.20051019183105.5:<< create picker button and callback >>
        def pickerCallback ():
            rgb,val = tkColorChooser.askcolor(parent=parent,initialcolor=f.cget('background'))
            if rgb or val:
                # label.configure(text=val)
                label.delete('1.0','end')
                label.insert('1.0',val)
                for theFrame in (parent,outer,f,f1,f2,f3):
                    theFrame.configure(background=val)

        b = Tk.Button(f3,text="Color Picker...",
            command=pickerCallback,background=bg)
        b.pack(side='left',pady=4)
        #@-node:ekr.20051019183105.5:<< create picker button and callback >>
        #@nl
    #@-node:ekr.20051019183105.3:tkLog color tab stuff
    #@+node:ekr.20070212102521:tkLog font tab stuff
    #@+node:ekr.20051019201809.1:createFontPicker
    def createFontPicker (self,tabName):

        log = self
        parent = log.frameDict.get(tabName)
        w = log.textDict.get(tabName)
        w.pack_forget()

        bg = parent.cget('background')
        font = self.getFont()
        #@    << create the frames >>
        #@+node:ekr.20051019202139:<< create the frames >>
        f = Tk.Frame(parent,background=bg) ; f.pack (side='top',expand=0,fill='both')
        f1 = Tk.Frame(f,background=bg)     ; f1.pack(side='top',expand=1,fill='x')
        f2 = Tk.Frame(f,background=bg)     ; f2.pack(side='top',expand=1,fill='x')
        f3 = Tk.Frame(f,background=bg)     ; f3.pack(side='top',expand=1,fill='x')
        f4 = Tk.Frame(f,background=bg)     ; f4.pack(side='top',expand=1,fill='x')
        #@-node:ekr.20051019202139:<< create the frames >>
        #@nl
        #@    << create the family combo box >>
        #@+node:ekr.20051019201809.2:<< create the family combo box >>
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
        #@-node:ekr.20051019201809.2:<< create the family combo box >>
        #@nl
        #@    << create the size entry >>
        #@+node:ekr.20051019201809.3:<< create the size entry >>
        Tk.Label(f2,text="Size:",width=10,background=bg).pack(side="left")

        sizeEntry = Tk.Entry(f2,width=4)
        sizeEntry.insert(0,'12')
        sizeEntry.pack(side="left",padx=2,pady=2)
        #@-node:ekr.20051019201809.3:<< create the size entry >>
        #@nl
        #@    << create the weight combo box >>
        #@+node:ekr.20051019201809.4:<< create the weight combo box >>
        weightBox = Pmw.ComboBox(f3,
            labelpos="we",label_text="Weight:",label_width=10,
            label_background=bg,
            arrowbutton_background=bg,
            scrolledlist_items=['normal','bold'])

        weightBox.selectitem(0)
        weightBox.pack(side="left",padx=2,pady=2)
        #@-node:ekr.20051019201809.4:<< create the weight combo box >>
        #@nl
        #@    << create the slant combo box >>
        #@+node:ekr.20051019201809.5:<< create the slant combo box>>
        slantBox = Pmw.ComboBox(f4,
            labelpos="we",label_text="Slant:",label_width=10,
            label_background=bg,
            arrowbutton_background=bg,
            scrolledlist_items=['roman','italic'])

        slantBox.selectitem(0)
        slantBox.pack(side="left",padx=2,pady=2)
        #@-node:ekr.20051019201809.5:<< create the slant combo box>>
        #@nl
        #@    << create the sample text widget >>
        #@+node:ekr.20051019202139.1:<< create the sample text widget >>
        self.sampleWidget = sample = g.app.gui.plainTextWidget(f,height=20,width=80,font=font)
        sample.pack(side='left')

        s = 'The quick brown fox\njumped over the lazy dog.\n0123456789'
        sample.insert(0,s)
        #@-node:ekr.20051019202139.1:<< create the sample text widget >>
        #@nl
        #@    << create and bind the callbacks >>
        #@+node:ekr.20051019202328:<< create and bind the callbacks >>
        def fontCallback(event=None):
            self.setFont(familyBox,sizeEntry,slantBox,weightBox,sample)

        for w in (familyBox,slantBox,weightBox):
            w.configure(selectioncommand=fontCallback)

        sizeEntry.bind('<Return>',fontCallback)
        #@-node:ekr.20051019202328:<< create and bind the callbacks >>
        #@nl
        self.createBindings()
    #@-node:ekr.20051019201809.1:createFontPicker
    #@+node:ekr.20060726133852:createBindings (fontPicker)
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
            w.bind(event,callback)

        k.completeAllBindingsForWidget(w)
    #@-node:ekr.20060726133852:createBindings (fontPicker)
    #@+node:ekr.20051019201809.6:getFont
    def getFont(self,family=None,size=12,slant='roman',weight='normal'):

        try:
            return tkFont.Font(family=family,size=size,slant=slant,weight=weight)
        except Exception:
            g.es("exception setting font")
            g.es('','family,size,slant,weight:','',family,'',size,'',slant,'',weight)
            # g.es_exception() # This just confuses people.
            return g.app.config.defaultFont
    #@-node:ekr.20051019201809.6:getFont
    #@+node:ekr.20051019201809.7:setFont
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
    #@-node:ekr.20051019201809.7:setFont
    #@+node:ekr.20060726134339:hideFontTab
    def hideFontTab (self,event=None):

        c = self.c
        c.frame.log.selectTab('Log')
        c.bodyWantsFocus()
    #@-node:ekr.20060726134339:hideFontTab
    #@-node:ekr.20070212102521:tkLog font tab stuff
    #@-others
#@-node:ekr.20031218072017.4039:class leoTkinterLog
#@+node:ekr.20070317073627.3:class leoTkinterTreeTab
class leoTkinterTreeTab (leoFrame.leoTreeTab):

    '''A class representing a tabbed outline pane drawn with Tkinter.'''

    #@    @+others
    #@+node:ekr.20070320090557.1: Birth & death
    #@+node:ekr.20070317073819.1: ctor (leoTreeTab)
    def __init__ (self,c,parentFrame,chapterController):

        leoFrame.leoTreeTab.__init__ (self,c,chapterController,parentFrame)
            # Init the base class.  Sets self.c, self.cc and self.parentFrame.

        self.tabNames = [] # The list of tab names.  Changes when tabs are renamed.

        self.createControl()
    #@-node:ekr.20070317073819.1: ctor (leoTreeTab)
    #@+node:ekr.20070317073819.2:tt.createControl
    def createControl (self):

        tt = self ; c = tt.c

        # Create the main container.
        tt.frame = Tk.Frame(c.frame.iconFrame)
        tt.frame.pack(side="left")

        # Create the chapter menu.
        self.chapterVar = var = Tk.StringVar()
        var.set('main')

        tt.chapterMenu = menu = Pmw.OptionMenu(tt.frame,
            labelpos = 'w', label_text = 'chapter',
            menubutton_textvariable = var,
            items = [],
            command = tt.selectTab,
        )
        menu.pack(side='left',padx=5)
    #@nonl
    #@-node:ekr.20070317073819.2:tt.createControl
    #@-node:ekr.20070320090557.1: Birth & death
    #@+node:ekr.20070320093038:Tabs...
    #@+node:ekr.20070317074824:tt.createTab
    def createTab (self,tabName,select=True):

        tt = self

        if tabName not in tt.tabNames:
            tt.tabNames.append(tabName)
            tt.setNames()
    #@-node:ekr.20070317074824:tt.createTab
    #@+node:ekr.20070317074824.1:tt.destroyTab
    def destroyTab (self,tabName):

        tt = self

        if tabName in tt.tabNames:
            tt.tabNames.remove(tabName)
            tt.setNames()
    #@-node:ekr.20070317074824.1:tt.destroyTab
    #@+node:ekr.20070317074824.3:tt.selectTab
    def selectTab (self,tabName):

        tt = self

        if tabName not in self.tabNames:
            tt.createTab(tabName)

        tt.cc.selectChapterByName(tabName)
    #@-node:ekr.20070317074824.3:tt.selectTab
    #@+node:ekr.20070604192627:tt.setTabLabel
    def setTabLabel (self,tabName):

        tt = self
        tt.chapterVar.set(tabName)
    #@-node:ekr.20070604192627:tt.setTabLabel
    #@+node:ekr.20070604210618:tt.setNames
    def setNames (self):

        '''Recreate the list of items.'''

        tt = self
        names = tt.tabNames[:]
        if 'main' in names: names.remove('main')
        names.sort()
        names.insert(0,'main')
        tt.chapterMenu.setitems(names)
    #@-node:ekr.20070604210618:tt.setNames
    #@-node:ekr.20070320093038:Tabs...
    #@-others
#@nonl
#@-node:ekr.20070317073627.3:class leoTkinterTreeTab
#@+node:ekr.20061113151148.1:class leoTkTextWidget (Tk.Text)
class leoTkTextWidget (Tk.Text):

    '''A class to wrap the Tk.Text widget.
    Translates Python (integer) indices to and from Tk (string) indices.

    This class inherits almost all tkText methods: you call use them as usual.'''

    # The signatures of tag_add and insert are different from the Tk.Text signatures.
    # __pychecker__ = '--no-override' # suppress warning about changed signature.

    def __repr__(self):
        name = hasattr(self,'_name') and self._name or '<no name>'
        return 'leoTkTextWidget id: %s name: %s' % (id(self),name)

    #@    @+others
    #@+node:ekr.20070213170937:bindings (not used)
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
    # def _setFocus(self):                return self.widget.focus_set()
    # def _setInsertPoint(self,i):        return self.widget.mark_set('insert',i)
    # def _setSelectionRange(self,i,j):   return self.widget.SetSelection(i,j)
    #@-node:ekr.20070213170937:bindings (not used)
    #@+node:ekr.20061113151148.2:Index conversion (leoTextWidget)
    #@+node:ekr.20061117085824:w.toGuiIndex
    def toGuiIndex (self,i,s=None):
        '''Convert a Python index to a Tk index as needed.'''
        w = self
        if i is None:
            g.trace('can not happen: i is None',g.callers())
            return '1.0'
        elif type(i) == type(99):
            # The 's' arg supports the threaded colorizer.
            if s is None:
                # This *must* be 'end-1c', even if other code must change.
                s = Tk.Text.get(w,'1.0','end-1c')
            row,col = g.convertPythonIndexToRowCol(s,i)
            i = '%s.%s' % (row+1,col)
            # g.trace(len(s),i,repr(s))
        else:
            try:
                i = Tk.Text.index(w,i)
            except Exception:
                # g.es_exception()
                g.trace('Tk.Text.index failed:',repr(i),g.callers())
                i = '1.0'
        return i
    #@nonl
    #@-node:ekr.20061117085824:w.toGuiIndex
    #@+node:ekr.20061117085824.1:w.toPythonIndex
    def toPythonIndex (self,i):
        '''Convert a Tk index to a Python index as needed.'''
        w =self
        if i is None:
            g.trace('can not happen: i is None')
            return 0
        elif type(i) in (type('a'),type(u'a')):
            s = Tk.Text.get(w,'1.0','end') # end-1c does not work.
            i = Tk.Text.index(w,i) # Convert to row/column form.
            row,col = i.split('.')
            row,col = int(row),int(col)
            row -= 1
            i = g.convertRowColToPythonIndex(s,row,col)
            #g.es_print('',i)
        return i
    #@-node:ekr.20061117085824.1:w.toPythonIndex
    #@+node:ekr.20061117085824.2:w.rowColToGuiIndex
    # This method is called only from the colorizer.
    # It provides a huge speedup over naive code.

    def rowColToGuiIndex (self,s,row,col):

        return '%s.%s' % (row+1,col)
    #@nonl
    #@-node:ekr.20061117085824.2:w.rowColToGuiIndex
    #@-node:ekr.20061113151148.2:Index conversion (leoTextWidget)
    #@+node:ekr.20061113151148.3:Wrapper methods (leoTextWidget)
    #@+node:ekr.20061113151148.4:delete
    def delete(self,i,j=None):

        w = self
        i = w.toGuiIndex(i)

        if j is None:
            Tk.Text.delete(w,i)
        else:
            j = w.toGuiIndex(j)
            Tk.Text.delete(w,i,j)
    #@-node:ekr.20061113151148.4:delete
    #@+node:ekr.20061113151148.12:flashCharacter
    def flashCharacter(self,i,bg='white',fg='red',flashes=3,delay=75): # tkTextWidget.

        w = self

        def addFlashCallback(w,count,index):
            # g.trace(count,index)
            i,j = w.toGuiIndex(index),w.toGuiIndex(index+1)
            Tk.Text.tag_add(w,'flash',i,j)
            Tk.Text.after(w,delay,removeFlashCallback,w,count-1,index)

        def removeFlashCallback(w,count,index):
            # g.trace(count,index)
            Tk.Text.tag_remove(w,'flash','1.0','end')
            if count > 0:
                Tk.Text.after(w,delay,addFlashCallback,w,count,index)

        try:
            Tk.Text.tag_configure(w,'flash',foreground=fg,background=bg)
            addFlashCallback(w,flashes,i)
        except Exception:
            pass # g.es_exception()
    #@nonl
    #@-node:ekr.20061113151148.12:flashCharacter
    #@+node:ekr.20061113151148.5:get
    def get(self,i,j=None):

        w = self
        i = w.toGuiIndex(i)

        if j is None:
            return Tk.Text.get(w,i)
        else:
            j = w.toGuiIndex(j)
            return Tk.Text.get(w,i,j)
    #@-node:ekr.20061113151148.5:get
    #@+node:ekr.20061113151148.13:getAllText
    def getAllText (self): # tkTextWidget.

        """Return all the text of Tk.Text widget w converted to unicode."""

        w = self
        s = Tk.Text.get(w,"1.0","end-1c") # New in 4.4.1: use end-1c.

        if s is None:
            return u""
        else:
            return g.toUnicode(s,g.app.tkEncoding)
    #@-node:ekr.20061113151148.13:getAllText
    #@+node:ekr.20061113151148.14:getInsertPoint
    def getInsertPoint(self): # tkTextWidget.

        w = self
        i = Tk.Text.index(w,'insert')
        i = w.toPythonIndex(i)
        return i
    #@-node:ekr.20061113151148.14:getInsertPoint
    #@+node:ekr.20061117160129:getName
    def getName (self):

        w = self
        return hasattr(w,'_name') and w._name or repr(w)
    #@nonl
    #@-node:ekr.20061117160129:getName
    #@+node:ekr.20061113151148.15:getSelectedText
    def getSelectedText (self): # tkTextWidget.

        w = self
        i,j = w.getSelectionRange()
        if i != j:
            i,j = w.toGuiIndex(i),w.toGuiIndex(j)
            s = Tk.Text.get(w,i,j)
            return g.toUnicode(s,g.app.tkEncoding)
        else:
            return u""
    #@-node:ekr.20061113151148.15:getSelectedText
    #@+node:ekr.20061113151148.16:getSelectionRange
    def getSelectionRange (self,sort=True): # tkTextWidget.

        """Return a tuple representing the selected range.

        Return a tuple giving the insertion point if no range of text is selected."""

        w = self
        sel = Tk.Text.tag_ranges(w,"sel")
        if len(sel) == 2:
            i,j = sel
        else:
            i = j = Tk.Text.index(w,"insert")

        i,j = w.toPythonIndex(i),w.toPythonIndex(j)  
        if sort and i > j: i,j = j,i
        return i,j
    #@nonl
    #@-node:ekr.20061113151148.16:getSelectionRange
    #@+node:ekr.20070212204016:getWidth
    def getWidth (self):

        '''Return the width of the widget.
        This is only called for headline widgets,
        and gui's may choose not to do anything here.'''

        w = self
        return w.cget('width')
    #@-node:ekr.20070212204016:getWidth
    #@+node:ekr.20070211185433.1:getYScrollPosition
    def getYScrollPosition (self):

        w = self
        return w.yview()
    #@-node:ekr.20070211185433.1:getYScrollPosition
    #@+node:ekr.20061113151148.17:hasSelection
    def hasSelection (self):

        w = self
        i,j = w.getSelectionRange()
        return i != j
    #@-node:ekr.20061113151148.17:hasSelection
    #@+node:ekr.20070213104858.1:indexIsVisible
    def indexIsVisible (self,i):

        w = self

        return w.dlineinfo(i)
    #@nonl
    #@-node:ekr.20070213104858.1:indexIsVisible
    #@+node:ekr.20061113151148.6:insert
    # The signature is more restrictive than the Tk.Text.insert method.

    def insert(self,i,s):

        w = self
        i = w.toGuiIndex(i)
        Tk.Text.insert(w,i,s)

    #@-node:ekr.20061113151148.6:insert
    #@+node:ekr.20061113151148.7:mark_set NO LONGER USED
    # def mark_set(self,markName,i):

        # w = self
        # i = w.toGuiIndex(i)
        # Tk.Text.mark_set(w,markName,i)
    #@-node:ekr.20061113151148.7:mark_set NO LONGER USED
    #@+node:ekr.20061113151148.18:replace
    def replace (self,i,j,s): # tkTextWidget

        w = self
        i,j = w.toGuiIndex(i),w.toGuiIndex(j)

        Tk.Text.delete(w,i,j)
        Tk.Text.insert(w,i,s)
    #@-node:ekr.20061113151148.18:replace
    #@+node:ekr.20061113180616:see
    def see (self,i): # tkTextWidget.

        w = self
        i = w.toGuiIndex(i)
        Tk.Text.see(w,i)
    #@-node:ekr.20061113180616:see
    #@+node:ekr.20061113175002:seeInsertPoint
    def seeInsertPoint (self): # tkTextWidget.

        w = self
        Tk.Text.see(w,'insert')
    #@-node:ekr.20061113175002:seeInsertPoint
    #@+node:ekr.20061113151148.19:selectAllText
    def selectAllText (self,insert=None): # tkTextWidget

        '''Select all text of the widget, *not* including the extra newline.'''

        w = self ; s = w.getAllText()
        if insert is None: insert = len(s)
        w.setSelectionRange(0,len(s),insert=insert)
    #@-node:ekr.20061113151148.19:selectAllText
    #@+node:ekr.20061113151148.20:setAllText
    def setAllText (self,s): # tkTextWidget

        w = self

        state = Tk.Text.cget(w,"state")
        Tk.Text.configure(w,state="normal")

        Tk.Text.delete(w,'1.0','end')
        if s: Tk.Text.insert(w,'1.0',s) # The 'if s:' is a workaround for a fedora bug.

        Tk.Text.configure(w,state=state)
    #@-node:ekr.20061113151148.20:setAllText
    #@+node:ekr.20070218122857:setBackgroundColor
    def setBackgroundColor (self,color):

        w = self
        w.configure(background=color)
    #@nonl
    #@-node:ekr.20070218122857:setBackgroundColor
    #@+node:ekr.20061113151148.21:setInsertPoint
    def setInsertPoint (self,i): # tkTextWidget.

        w = self
        i = w.toGuiIndex(i)
        # g.trace(i,g.callers())
        Tk.Text.mark_set(w,'insert',i)
    #@-node:ekr.20061113151148.21:setInsertPoint
    #@+node:ekr.20061113151148.22:setSelectionRange
    def setSelectionRange (self,i,j,insert=None): # tkTextWidget

        w = self

        i,j = w.toGuiIndex(i),w.toGuiIndex(j)

        # g.trace('i,j,insert',repr(i),repr(j),repr(insert),g.callers())

        # g.trace('i,j,insert',i,j,repr(insert))
        if Tk.Text.compare(w,i, ">", j): i,j = j,i
        Tk.Text.tag_remove(w,"sel","1.0",i)
        Tk.Text.tag_add(w,"sel",i,j)
        Tk.Text.tag_remove(w,"sel",j,"end")

        if insert is not None:
            w.setInsertPoint(insert)
    #@-node:ekr.20061113151148.22:setSelectionRange
    #@+node:ekr.20070212081121:setWidth
    def setWidth (self,width):

        '''Set the width of the widget.
        This is only called for headline widgets,
        and gui's may choose not to do anything here.'''

        w = self
        w.configure(width=width)
    #@-node:ekr.20070212081121:setWidth
    #@+node:ekr.20070211185433:setYScrollPosition
    def setYScrollPosition (self,i):

        w = self
        w.yview('moveto',i)
    #@nonl
    #@-node:ekr.20070211185433:setYScrollPosition
    #@+node:ekr.20061113151148.8:tag_add
    # The signature is slightly different than the Tk.Text.insert method.

    def tag_add(self,tagName,i,j=None,*args):

        w = self
        i = w.toGuiIndex(i)

        if j is None:
            Tk.Text.tag_add(w,tagName,i,*args)
        else:
            j = w.toGuiIndex(j)
            Tk.Text.tag_add(w,tagName,i,j,*args)

    #@-node:ekr.20061113151148.8:tag_add
    #@+node:ekr.20061113151148.9:tag_ranges
    def tag_ranges(self,tagName):

        w = self
        aList = Tk.Text.tag_ranges(w,tagName)
        aList = [w.toPythonIndex(z) for z in aList]
        return tuple(aList)
    #@-node:ekr.20061113151148.9:tag_ranges
    #@+node:ekr.20070116073907:tag_remove
    # The signature is slightly different than the Tk.Text.insert method.

    def tag_remove (self,tagName,i,j=None,*args):

        w = self
        i = w.toGuiIndex(i)

        if j is None:
            Tk.Text.tag_remove(w,tagName,i,*args)
        else:
            j = w.toGuiIndex(j)
            Tk.Text.tag_remove(w,tagName,i,j,*args)


    #@-node:ekr.20070116073907:tag_remove
    #@+node:ekr.20061113151148.11:w.deleteTextSelection
    def deleteTextSelection (self): # tkTextWidget

        w = self
        sel = Tk.Text.tag_ranges(w,"sel")
        if len(sel) == 2:
            start,end = sel
            if Tk.Text.compare(w,start,"!=",end):
                Tk.Text.delete(w,start,end)
    #@-node:ekr.20061113151148.11:w.deleteTextSelection
    #@+node:ekr.20061113151148.23:xyToGui/PythonIndex
    def xyToGuiIndex (self,x,y): # tkTextWidget

        w = self
        return Tk.Text.index(w,"@%d,%d" % (x,y))

    def xyToPythonIndex(self,x,y): # tkTextWidget

        w = self
        i = Tk.Text.index(w,"@%d,%d" % (x,y))
        i = w.toPythonIndex(i)
        return i
    #@-node:ekr.20061113151148.23:xyToGui/PythonIndex
    #@-node:ekr.20061113151148.3:Wrapper methods (leoTextWidget)
    #@-others
#@nonl
#@-node:ekr.20061113151148.1:class leoTkTextWidget (Tk.Text)
#@-others
#@-node:ekr.20031218072017.3939:@thin leoTkinterFrame.py
#@-leo
