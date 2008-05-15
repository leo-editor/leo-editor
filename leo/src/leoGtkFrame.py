# -*- coding: utf-8 -*-
#@+leo-ver=4-thin
#@+node:ekr.20080112145409.53:@thin leoGtkFrame.py
#@@first

#@@language python
#@@tabwidth -4
#@@pagewidth 80

#@<< imports >>
#@+node:ekr.20080112145409.54:<< imports >>
import leoGlobals as g

import leoChapters
import leoColor
import leoFrame
import leoKeys
import leoMenu
import leoNodes

import leoGtkMenu
import leoGtkTree

import gobject
import gtk
import cairo
import pango

import os
import string
import sys

#@-node:ekr.20080112145409.54:<< imports >>
#@nl

#@+others
#@+node:bob.20080114214548:class TestWindow
class TestWindow(gtk.DrawingArea):

    """A window with a cross, used for testing.

    The background and cross color can be set when
    it is created.

    """

    def __init__(self, bg=None, fg=None):

        """Construct a TestWindow.

        'bg': a named color indicating background color, defaults to 'white' if invalid.
        'fg': a named color indicating foreground color, defaults to 'black' if invalid.

        """

        super(TestWindow, self).__gobject_init__()


        self.set_size_request(10, 10)

        self.bg = leoColor.getCairo(bg, 'white')
        self.fg = leoColor.getCairo(fg, 'black')



    def do_expose_event(self, event):
        """Handle expose events for this window"""

        cr = self.window.cairo_create()

        w, h = self.window.get_size()


        cr.set_source_rgb(*self.bg)
        cr.rectangle(0, 0, w, h)
        cr.fill()

        cr.set_source_rgb(*self.fg)

        cr.move_to(0, 0)
        cr.line_to(w, h)
        cr.move_to(w, 0)
        cr.line_to(0, h)
        cr.stroke()

        return True

gobject.type_register(TestWindow)
#@-node:bob.20080114214548:class TestWindow
#@+node:bob.20080115155515:== paned widget classes ==
#@+node:bob.20080115155515.1:class panedMixin
class panedMixin:

    """Adds leo specific functionality to gtk.[VH]Paned widgets."""


    def __repr__(self):

        return '<%s: %s %s (%s)>' % (self.__class__.name, self.name, self.orientation, self.get_position)

    #@    @+others
    #@+node:bob.20080115205803:__init__
    def __init__(self, c, name, orientation, ratio=0.5):

        """Initialize the widget with leo specific parameters.

        'name' Sets the "name" property of the widget to the string specified by name.
               This will allow the widget to be referenced in a GTK resource file.

        'orientation' A string describing this widgets orientation ('horizontal' or 'vertical')

        """
        self.c = c
        self.set_name(name)
        self.orientation = orientation
        self.ratio = ratio

        self.connect('notify::position', self.onPositionChanged)






    #@-node:bob.20080115205803:__init__
    #@+node:bob.20080115205803.1:setSplitRatio
    def setSplitRatio(self, ratio):
        """Set the split ratio to 'ratio'.

        'ratio' should be a float in the range from 0.0 to 1.0 inclusive.

        """

        self.__ratio = ratio

        #check to see if containing window has been mapped
        #if not then leave it to onMap to set splitter position.
        if not self.window:
            return

        w, h = self.window.get_size()

        size = g.choose(self.orientation == 'horizontal', w, h)
        self.set_position(int(size * ratio))

        #g.trace(self, ratio, size)
    #@nonl
    #@-node:bob.20080115205803.1:setSplitRatio
    #@+node:bob.20080115205803.2:getSplitRatio
    def getSplitRatio(self):

        """Get the current split ratio.

        If the window is not mapped then this can not be calculated so the
        value stored in self.__ratio is used as this is the ratio that will
        be set when the widget is mapped.

        """

        if not self.window:
            return self.__ratio

        w, h = self.window.get_size()
        size = g.choose(self.orientation == 'horizontal', w, h)

        self.__ratio = self.get_position()*1.0/size

        return self.__ratio 
    #@-node:bob.20080115205803.2:getSplitRatio
    #@+node:bob.20080116235335:resetSplitRatio
    def resetSplitRatio(self):

        self.setSplitRatio(self.__ratio)
    #@-node:bob.20080116235335:resetSplitRatio
    #@+node:bob.20080115205803.3:onPositionChanged
    def onPositionChanged(self, *args):

        """Respond to changes in the widgets 'position' property"""

        self.__ratio = self.getSplitRatio()
    #@-node:bob.20080115205803.3:onPositionChanged
    #@+node:bob.20080115210426:Property: ratio
    ratio = property(getSplitRatio, setSplitRatio)
    #@nonl
    #@-node:bob.20080115210426:Property: ratio
    #@-others









#@-node:bob.20080115155515.1:class panedMixin
#@+node:bob.20080115155515.2:class VPaned (gtk.VPaned, panedMixin)
class VPaned(gtk.VPaned, panedMixin):
    """Subclass to add leo specific functionality to gtk.VPaned."""

    def __init__(self, c, name):

        gtk.VPaned.__gobject_init__(self)
        panedMixin.__init__(self, c, name, 'vertical')

gobject.type_register(VPaned)
#@-node:bob.20080115155515.2:class VPaned (gtk.VPaned, panedMixin)
#@+node:bob.20080115155515.3:class HPaned (gtk.HPaned, panedMixin)
class HPaned(gtk.HPaned, panedMixin):
    """Subclass to add leo specific functionality to gtk.HPaned."""

    def __init__(self, c, name):

        """Construct a new object"""

        gtk.VPaned.__gobject_init__(self)
        panedMixin.__init__(self, c, name, 'horizontal')

gobject.type_register(HPaned)
#@-node:bob.20080115155515.3:class HPaned (gtk.HPaned, panedMixin)
#@-node:bob.20080115155515:== paned widget classes ==
#@+node:ekr.20080112145409.55:class leoGtkFrame
class leoGtkFrame (leoFrame.leoFrame):

    #@    @+others
    #@+node:ekr.20080112145409.56: Birth & Death (gtkFrame)
    #@+node:ekr.20080112145409.57:__init__ (gtkFrame)
    def __init__(self,title,gui):

        #g.trace('gtkFrame',g.callers(20))

        # Init the base class.
        leoFrame.leoFrame.__init__(self,gui)

        self.use_chapters = False ###

        self.title = title

        leoGtkFrame.instances += 1

        self.c = None # Set in finishCreate.
        self.iconBarClass = self.gtkIconBarClass
        self.statusLineClass = self.gtkStatusLineClass
        #self.minibufferClass = self.gtkMinibufferClass

        self.iconBar = None

        self.trace_status_line = None # Set in finishCreate.

        #@    << set the leoGtkFrame ivars >>
        #@+node:ekr.20080112145409.58:<< set the leoGtkFrame ivars >> (removed frame.bodyCtrl ivar)
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
        #@-node:ekr.20080112145409.58:<< set the leoGtkFrame ivars >> (removed frame.bodyCtrl ivar)
        #@nl
    #@-node:ekr.20080112145409.57:__init__ (gtkFrame)
    #@+node:ekr.20080112145409.59:__repr__ (gtkFrame)
    def __repr__ (self):

        return "<leoGtkFrame: %s>" % self.title
    #@-node:ekr.20080112145409.59:__repr__ (gtkFrame)
    #@+node:ekr.20080112145409.60:gtkFrame.finishCreate & helpers
    def finishCreate (self,c):
        """Finish creating leoGtkFrame."""

        f = self ; f.c = c
        #g.trace('gtkFrame')

        self.trace_status_line = c.config.getBool('trace_status_line')
        self.use_chapters = False and c.config.getBool('use_chapters') ###
        self.use_chapter_tabs  = False and c.config.getBool('use_chapter_tabs') ###

        # This must be done after creating the commander.
        f.splitVerticalFlag,f.ratio,f.secondary_ratio = f.initialRatios()

        f.createOuterFrames()

        ### f.createIconBar()

        f.createSplitterComponents()

        ### f.createStatusLine()

        f.createFirstTreeNode()
        f.menu = leoGtkMenu.leoGtkMenu(f)

            # c.finishCreate calls f.createMenuBar later. Why?

        c.setLog()
        g.app.windowList.append(f)

        c.initVersion()
        c.signOnWithVersion()

        f.miniBufferWidget = f.createMiniBufferWidget()

        def cbResetSplitRatio(f=f):
            if not f:
                g.trace('no frame')
            f and f.f1 and f.f1.resetSplitRatio()
            f and f.f2 and f.f2.resetSplitRatio()
            return True

        gobject.timeout_add(300, cbResetSplitRatio)

        c.bodyWantsFocusNow()

    #@+node:ekr.20080112145409.61:createOuterFrames
    def createOuterFrames (self):

        """Create the main window."""

        f = self ; c = f.c

        w = gtk.Window(gtk.WINDOW_TOPLEVEL)
        w.set_title("gtkLeo Demo")

        w.set_size_request(10, 10)
        #w.resize(400, 300)

        # mainVbox is the vertical box where all the componets are pack
        # starting with the menu and ending with the minibuffer.

        f.mainVBox = gtk.VBox()
        w.add(f.mainVBox)

        f.top = w

        def destroy_callback(widget,data=None):
            gtk.main_quit()  ### should call g.app.closeLeoWindow.

        w.connect(
            "destroy",
             destroy_callback
        )

        w.connect(
            'key-press-event', lambda w, event, self=f: self.toggleSplitDirection()
        )

        w.show_all()

    #@-node:ekr.20080112145409.61:createOuterFrames
    #@+node:ekr.20080112145409.62:createSplitterComponents (removed frame.bodyCtrl ivar)
    def createSplitterComponents (self):
        """Create the splitters and populate them with tree, body and log panels.""" 

        f = self ; c = f.c

        #g.trace()

        f.mainSplitterPanel = gtk.HBox()
        f.menuHolderPanel = gtk.VBox()

        f.mainVBox.pack_start(f.menuHolderPanel, False, False, 0)
        f.mainVBox.add(f.mainSplitterPanel)

        f.body = leoGtkBody(f,f.top)
        f.tree = leoGtkTree.leoGtkTree(c)
        f.log  = leoGtkLog(f,f.top)

        self.createLeoSplitters(f)

        # Configure.
        f.setTabWidth(c.tab_width)
        f.reconfigurePanes()
        f.body.setFontFromConfig()
        f.body.setColorFromConfig()

        f.top.show_all()
    #@-node:ekr.20080112145409.62:createSplitterComponents (removed frame.bodyCtrl ivar)
    #@+node:ekr.20080112145409.63:createFirstTreeNode
    def createFirstTreeNode (self):

        f = self ; c = f.c

        v = leoNodes.vnode(context=c)
        p = leoNodes.position(v)
        v.initHeadString("NewHeadline")
        # New in Leo 4.5: p.moveToRoot would be wrong: the node hasn't been linked yet.
        p._linkAsRoot(oldRoot=None)
        c.setRootPosition(p) # New in 4.4.2.
        c.editPosition(p)
    #@-node:ekr.20080112145409.63:createFirstTreeNode
    #@-node:ekr.20080112145409.60:gtkFrame.finishCreate & helpers
    #@+node:bob.20080117142603:ignore
    if 0:
        #@    @+others
        #@+node:ekr.20080112145409.64:gtkFrame.createCanvas & helpers
        def createCanvas (self,parentFrame,pack=True):

            #g.trace()

            c = self.c

            scrolls = c.config.getBool('outline_pane_scrolls_horizontally')
            scrolls = g.choose(scrolls,1,0)
            canvas = self.createGtkTreeCanvas(parentFrame,scrolls,pack)
            self.setCanvasColorFromConfig(canvas)

            return canvas
        #@+node:ekr.20080112145409.65:f.createGtkTreeCanvas & callbacks
        def createGtkTreeCanvas (self,parentFrame,scrolls,pack):
            #g.trace()

            return self.tree.canvas

        #@-node:ekr.20080112145409.65:f.createGtkTreeCanvas & callbacks
        #@+node:ekr.20080112145409.69:f.setCanvasColorFromConfig
        def setCanvasColorFromConfig (self,canvas):

            c = self.c

            bg = c.config.getColor("outline_pane_background_color") or 'white'

            canvas.setBackgroundColor(bg)

        #@-node:ekr.20080112145409.69:f.setCanvasColorFromConfig
        #@-node:ekr.20080112145409.64:gtkFrame.createCanvas & helpers
        #@-others
    #@nonl
    #@-node:bob.20080117142603:ignore
    #@+node:ekr.20080112145409.70:gtkFrame.createLeoSplitters & helpers
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

    def createLeoSplitters (self,parentFrame=None):

        """Create leo's main and secondary splitters and pack into mainSplitterPanel.

        f1 (splitter1) is the main splitter containing splitter2 and the body pane.
        f2 (splitter2) is the secondary splitter containing the tree and log panes.

        'parentFrame' is not used in gtk.

        """

        f= parentFrame
        c = f.c

        vertical = self.splitVerticalFlag

        f.f1 = self.createLeoGtkSplitter(f, vertical, 'splitter1')
        f.f2 = self.createLeoGtkSplitter(f, not vertical, 'splitter2')

        #f.f2.pack1(TestWindow('leo yellow', 'red'))
        #g.trace(f.tree.canvas.top)
        #f.f2.pack1(TestWindow('leo yellow', 'red'))

        f.f2.pack1(self.tree.canvas.top)
        #f.f2.pack2(TestWindow('leo pink', 'yellow'))

        f.f2.pack2(self.log.nb)
        f.f1.pack1(f.f2)

        #f.f1.pack2(TestWindow('leo blue', 'light green'))
        f.f1.pack2(self.body.bodyCtrl.widget)

        f.mainSplitterPanel.add(f.f1)

    #@+node:bob.20080115172351.2:createLeoGtkSplitter
    def createLeoGtkSplitter (self,parent,verticalFlag,componentName):
        """Create gtk spitter component."""

        paned = g.choose(verticalFlag, VPaned, HPaned)
        return paned(parent.c, componentName)

    #@-node:bob.20080115172351.2:createLeoGtkSplitter
    #@+node:ekr.20080112145409.72:bindBar
    def bindBar (self, bar, verticalFlag):

        NOTUSED()
    #@-node:ekr.20080112145409.72:bindBar
    #@+node:ekr.20080112145409.73:divideAnySplitter
    # This is the general-purpose placer for splitters.
    # It is the only general-purpose splitter code in Leo.

    def divideAnySplitter (self, frac, verticalFlag, bar, pane1, pane2):

        NOTUSED()
    #@-node:ekr.20080112145409.73:divideAnySplitter
    #@+node:bob.20080115172351.5:divideLeoSplitter
    # Divides the main or secondary splitter, using the key invariant.

    def divideLeoSplitter (self, verticalFlag, frac):
        """Divides the main or secondary splitter."""

        if self.splitVerticalFlag == verticalFlag:
            self.divideLeoSplitter1(frac)
            self.ratio = frac # Ratio of body pane to tree pane.
        else:
            self.divideLeoSplitter2(frac)
            self.secondary_ratio = frac # Ratio of tree pane to log pane.

    # Divides the main splitter.

    def divideLeoSplitter1 (self, frac, verticalFlag=None):
        """Divide the (tree/log)/body splitter."""
        self.f1.setSplitRatio(frac)

    # Divides the secondary splitter.

    def divideLeoSplitter2 (self, frac, verticalFlag=None):
        """Divide the tree/log splitter."""    
        self.f2.setSplitRatio(frac)

    #@-node:bob.20080115172351.5:divideLeoSplitter
    #@+node:ekr.20080112145409.75:onDrag...
    def onDragMainSplitBar (self, event):
        self.onDragSplitterBar(event,self.splitVerticalFlag)

    def onDragSecondarySplitBar (self, event):
        self.onDragSplitterBar(event,not self.splitVerticalFlag)

    def onDragSplitterBar (self, event, verticalFlag):

        NOTUSED()
    #@-node:ekr.20080112145409.75:onDrag...
    #@+node:bob.20080115172351.7:placeSplitter
    def placeSplitter (self,bar,pane1,pane2,verticalFlag):

        NOTUSED()

    #@-node:bob.20080115172351.7:placeSplitter
    #@-node:ekr.20080112145409.70:gtkFrame.createLeoSplitters & helpers
    #@+node:ekr.20080112145409.77:Destroying the gtkFrame
    #@+node:ekr.20080112145409.78:destroyAllObjects
    def destroyAllObjects (self):

        """Clear all links to objects in a Leo window."""

        frame = self ; c = self.c ; tree = frame.tree ; body = self.body

        # g.printGcAll()

        # Do this first.
        #@    << clear all vnodes and tnodes in the tree >>
        #@+node:ekr.20080112145409.79:<< clear all vnodes and tnodes in the tree>>
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
        #@-node:ekr.20080112145409.79:<< clear all vnodes and tnodes in the tree>>
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

    #@-node:ekr.20080112145409.78:destroyAllObjects
    #@+node:ekr.20080112145409.80:destroyAllPanels
    def destroyAllPanels (self):

        """Destroy all panels attached to this frame."""

        panels = (self.comparePanel, self.colorPanel, self.findPanel, self.fontPanel, self.prefsPanel)

        for panel in panels:
            if panel:
                panel.top.destroy()
    #@-node:ekr.20080112145409.80:destroyAllPanels
    #@+node:ekr.20080112145409.81:destroySelf (gtkFrame)
    def destroySelf (self):

        # Remember these: we are about to destroy all of our ivars!
        top = self.top 
        c = self.c

        # Indicate that the commander is no longer valid.
        c.exists = False 

        # g.trace(self)

        # Important: this destroys all the objects of the commander too.
        self.destroyAllObjects()

        c.exists = False # Make sure this one ivar has not been destroyed.

        top.destroy()
    #@-node:ekr.20080112145409.81:destroySelf (gtkFrame)
    #@-node:ekr.20080112145409.77:Destroying the gtkFrame
    #@-node:ekr.20080112145409.56: Birth & Death (gtkFrame)
    #@+node:ekr.20080112145409.82:class gtkStatusLineClass
    class gtkStatusLineClass:

        '''A class representing the status line.'''

        #@    @+others
        #@+node:ekr.20080112145409.83: ctor
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
            self.statusFrame = gtk.Frame(parentFrame,bd=2)
            text = "line 0, col 0"
            width = len(text) + 4
            self.labelWidget = gtk.Label(self.statusFrame,text=text,width=width,anchor="w")
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
        #@-node:ekr.20080112145409.83: ctor
        #@+node:ekr.20080112145409.84:clear
        def clear (self):

            w = self.textWidget
            if not w: return

            w.configure(state="normal")
            w.delete(0,"end")
            w.configure(state="disabled")
        #@-node:ekr.20080112145409.84:clear
        #@+node:ekr.20080112145409.85:enable, disable & isEnabled
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
        #@-node:ekr.20080112145409.85:enable, disable & isEnabled
        #@+node:ekr.20080112145409.86:get
        def get (self):

            w = self.textWidget
            if w:
                return w.getAllText()
            else:
                return ""
        #@-node:ekr.20080112145409.86:get
        #@+node:ekr.20080112145409.87:getFrame
        def getFrame (self):

            return self.statusFrame
        #@-node:ekr.20080112145409.87:getFrame
        #@+node:ekr.20080112145409.88:onActivate
        def onActivate (self,event=None):

            # Don't change background as the result of simple mouse clicks.
            background = self.statusFrame.cget("background")
            self.enable(background=background)
        #@-node:ekr.20080112145409.88:onActivate
        #@+node:ekr.20080112145409.89:pack & show
        def pack (self):

            if not self.isVisible:
                self.isVisible = True
                self.statusFrame.pack(fill="x",pady=1)

        show = pack
        #@-node:ekr.20080112145409.89:pack & show
        #@+node:ekr.20080112145409.90:put (leoGtkFrame:statusLineClass)
        def put(self,s,color=None):

            # g.trace('gtkStatusLine',self.textWidget,s)

            w = self.textWidget
            if not w:
                g.trace('gtkStatusLine','***** disabled')
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
        #@-node:ekr.20080112145409.90:put (leoGtkFrame:statusLineClass)
        #@+node:ekr.20080112145409.91:unpack & hide
        def unpack (self):

            if self.isVisible:
                self.isVisible = False
                self.statusFrame.pack_forget()

        hide = unpack
        #@-node:ekr.20080112145409.91:unpack & hide
        #@+node:ekr.20080112145409.92:update (statusLine)
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
        #@-node:ekr.20080112145409.92:update (statusLine)
        #@-others
    #@-node:ekr.20080112145409.82:class gtkStatusLineClass
    #@+node:ekr.20080112145409.93:class gtkIconBarClass
    class gtkIconBarClass:

        '''A class representing the singleton Icon bar'''

        #@    @+others
        #@+node:ekr.20080112145409.94: ctor
        def __init__ (self,c,parentFrame):

            self.c = c

            self.buttons = {}
            self.iconFrame = w = gtk.Frame(parentFrame,height="5m",bd=2,relief="groove")
            self.c.frame.iconFrame = self.iconFrame
            self.font = None
            self.parentFrame = parentFrame
            self.visible = False
            self.show()
        #@-node:ekr.20080112145409.94: ctor
        #@+node:ekr.20080112145409.95:add
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
                def command():
                    print "command for widget %s" % (n)

            if imagefile or image:
                #@        << create a picture >>
                #@+node:ekr.20080112145409.96:<< create a picture >>
                try:
                    if imagefile:
                        # Create the image.  Throws an exception if file not found
                        imagefile = g.os_path_join(g.app.loadDir,imagefile)
                        imagefile = g.os_path_normpath(imagefile)
                        image = gtk.PhotoImage(master=g.app.root,file=imagefile)

                        # Must keep a reference to the image!
                        try:
                            refs = g.app.iconImageRefs
                        except:
                            refs = g.app.iconImageRefs = []

                        refs.append((imagefile,image),)

                    if not bg:
                        bg = f.cget("bg")

                    b = gtk.Button(f,image=image,relief="flat",bd=0,command=command,bg=bg)
                    b.pack(side="left",fill="y")
                    return b

                except:
                    g.es_exception()
                    return None
                #@-node:ekr.20080112145409.96:<< create a picture >>
                #@nl
            elif text:
                b = gtk.Button(f,text=text,relief="groove",bd=2,command=command)
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
        #@-node:ekr.20080112145409.95:add
        #@+node:ekr.20080112145409.97:clear
        def clear(self):

            """Destroy all the widgets in the icon bar"""

            f = self.iconFrame

            for slave in f.pack_slaves():
                slave.destroy()
            self.visible = False

            f.configure(height="5m") # The default height.
            g.app.iconWidgetCount = 0
            g.app.iconImageRefs = []
        #@-node:ekr.20080112145409.97:clear
        #@+node:ekr.20080112145409.98:deleteButton (new in Leo 4.4.3)
        def deleteButton (self,w):

            w.pack_forget()
        #@-node:ekr.20080112145409.98:deleteButton (new in Leo 4.4.3)
        #@+node:ekr.20080112145409.99:getFrame
        def getFrame (self):

            return self.iconFrame
        #@-node:ekr.20080112145409.99:getFrame
        #@+node:ekr.20080112145409.100:pack (show)
        def pack (self):

            """Show the icon bar by repacking it"""

            if not self.visible:
                self.visible = True
                self.iconFrame.pack(fill="x",pady=2)

        show = pack
        #@-node:ekr.20080112145409.100:pack (show)
        #@+node:ekr.20080112145409.101:setCommandForButton (new in Leo 4.4.3)
        def setCommandForButton(self,b,command):

            b.configure(command=command)
        #@-node:ekr.20080112145409.101:setCommandForButton (new in Leo 4.4.3)
        #@+node:ekr.20080112145409.102:unpack (hide)
        def unpack (self):

            """Hide the icon bar by unpacking it.

            A later call to show will repack it in a new location."""

            if self.visible:
                self.visible = False
                self.iconFrame.pack_forget()

        hide = unpack
        #@-node:ekr.20080112145409.102:unpack (hide)
        #@-others
    #@-node:ekr.20080112145409.93:class gtkIconBarClass
    #@+node:ekr.20080112145409.103:Minibuffer methods
    #@+node:ekr.20080112145409.104:showMinibuffer
    def showMinibuffer (self):

        '''Make the minibuffer visible.'''

        frame = self

        if not frame.minibufferVisible:
            frame.minibufferFrame.pack(side='bottom',fill='x')
            frame.minibufferVisible = True
    #@-node:ekr.20080112145409.104:showMinibuffer
    #@+node:ekr.20080112145409.105:hideMinibuffer
    def hideMinibuffer (self):

        '''Hide the minibuffer.'''

        frame = self
        if frame.minibufferVisible:
            frame.minibufferFrame.pack_forget()
            frame.minibufferVisible = False
    #@-node:ekr.20080112145409.105:hideMinibuffer
    #@+node:ekr.20080112145409.106:f.createMiniBufferWidget
    def createMiniBufferWidget (self):

        '''Create the minbuffer below the status line.'''

        frame = self ; c = frame.c

        # frame.minibufferFrame = f = gtk.Frame(frame.outerFrame,relief='flat',borderwidth=0)
        # if c.showMinibuffer:
            # f.pack(side='bottom',fill='x')

        # lab = gtk.Label(f,text='mini-buffer',justify='left',anchor='nw',foreground='blue')
        # lab.pack(side='left')

        # if c.useTextMinibuffer:
            # label = g.app.gui.plainTextWidget(
                # f,height=1,relief='groove',background='lightgrey',name='minibuffer')
            # label.pack(side='left',fill='x',expand=1,padx=2,pady=1)
        # else:
            # label = gtk.Label(f,relief='groove',justify='left',anchor='w',name='minibuffer')
            # label.pack(side='left',fill='both',expand=1,padx=2,pady=1)

        # frame.minibufferVisible = c.showMinibuffer

        # return label
    #@-node:ekr.20080112145409.106:f.createMiniBufferWidget
    #@+node:ekr.20080112145409.107:f.setMinibufferBindings
    def setMinibufferBindings (self):

        '''Create bindings for the minibuffer..'''

        f = self ; c = f.c ; k = c.k ; w = f.miniBufferWidget

        if not c.useTextMinibuffer: return

        # for kind,callback in (
            # ('<Key>',           k.masterKeyHandler),
            # ('<Button-1>',      k.masterClickHandler),
            # ('<Button-3>',      k.masterClick3Handler),
            # ('<Double-1>',      k.masterDoubleClickHandler),
            # ('<Double-3>',      k.masterDoubleClick3Handler),
        # ):
            # c.bind(w,kind,callback)

        # if 0:
            # if sys.platform.startswith('win'):
                # # Support Linux middle-button paste easter egg.
                # c.bind(w,"<Button-2>",frame.OnPaste)
    #@-node:ekr.20080112145409.107:f.setMinibufferBindings
    #@-node:ekr.20080112145409.103:Minibuffer methods
    #@+node:ekr.20080112145409.108:Configuration (gtkFrame)
    #@+node:ekr.20080112145409.111:reconfigureFromConfig (gtkFrame)
    def reconfigureFromConfig (self):

        frame = self ; c = frame.c

        frame.tree.setFontFromConfig()
        ### frame.tree.setColorFromConfig()

        frame.configureBarsFromConfig()

        frame.body.setFontFromConfig()
        frame.body.setColorFromConfig()

        frame.setTabWidth(c.tab_width)
        frame.log.setFontFromConfig()
        frame.log.setColorFromConfig()

        c.redraw_now()
    #@-node:ekr.20080112145409.111:reconfigureFromConfig (gtkFrame)
    #@+node:ekr.20080112145409.112:setInitialWindowGeometry (gtkFrame)
    def setInitialWindowGeometry(self):

        """Set the position and size of the frame to config params."""

        c = self.c

        h = c.config.getInt("initial_window_height") or 500
        w = c.config.getInt("initial_window_width") or 600
        x = c.config.getInt("initial_window_left") or 10
        y = c.config.getInt("initial_window_top") or 10

        if h and w and x and y:
            self.setTopGeometry(w,h,x,y)
    #@-node:ekr.20080112145409.112:setInitialWindowGeometry (gtkFrame)
    #@+node:ekr.20080112145409.114:setWrap (gtkFrame)
    def setWrap (self,p):

        c = self.c ; w = c.frame.body.bodyCtrl

        theDict = g.scanDirectives(c,p)
        if not theDict: return

        wrap = theDict.get("wrap")

        ### if self.body.wrapState == wrap: return

        self.body.wrapState = wrap
        # g.trace(wrap)

        ### Rewrite for gtk.
    #@nonl
    #@-node:ekr.20080112145409.114:setWrap (gtkFrame)
    #@+node:ekr.20080112145409.115:setTopGeometry (gtkFrame)
    def setTopGeometry(self,w,h,x,y,adjustSize=True):

        # Put the top-left corner on the screen.
        x = max(10,x) ; y = max(10,y)

        if adjustSize:
            top = self.top
            sw = gtk.gdk.screen_width()
            sh = gtk.gdk.screen_height()

            # Adjust the size so the whole window fits on the screen.
            w = min(sw-10,w)
            h = min(sh-10,h)

            # Adjust position so the whole window fits on the screen.
            if x + w > sw: x = 10
            if y + h > sh: y = 10

        self.top.resize(w,h)
        self.top.move(x,y)
    #@-node:ekr.20080112145409.115:setTopGeometry (gtkFrame)
    #@+node:ekr.20080112145409.116:reconfigurePanes (use config bar_width) (gtkFrame)
    def reconfigurePanes (self):

        c = self.c

        border = c.config.getInt('additional_body_text_border')
        if border == None: border = 0

        # The body pane needs a _much_ bigger border when tiling horizontally.
        border = g.choose(self.splitVerticalFlag,2+border,6+border)
        ### self.bodyCtrl.configure(bd=border)

        # The log pane needs a slightly bigger border when tiling vertically.
        border = g.choose(self.splitVerticalFlag,4,2) 
        ### self.log.configureBorder(border)
    #@-node:ekr.20080112145409.116:reconfigurePanes (use config bar_width) (gtkFrame)
    #@+node:ekr.20080112145409.117:resizePanesToRatio (gtkFrame)
    def resizePanesToRatio(self,ratio,ratio2):

        # g.trace(ratio,ratio2,g.callers())

        self.divideLeoSplitter(self.splitVerticalFlag,ratio)
        self.divideLeoSplitter(not self.splitVerticalFlag,ratio2)
    #@nonl
    #@-node:ekr.20080112145409.117:resizePanesToRatio (gtkFrame)
    #@-node:ekr.20080112145409.108:Configuration (gtkFrame)
    #@+node:ekr.20080112145409.118:Event handlers (gtkFrame)
    #@+node:ekr.20080112145409.119:frame.OnCloseLeoEvent
    # Called from quit logic and when user closes the window.
    # Returns True if the close happened.

    def OnCloseLeoEvent(self):

        f = self ; c = f.c

        if c.inCommand:
            # g.trace('requesting window close')
            c.requestCloseWindow = True
        else:
            g.app.closeLeoWindow(self)
    #@-node:ekr.20080112145409.119:frame.OnCloseLeoEvent
    #@+node:ekr.20080112145409.120:frame.OnControlKeyUp/Down
    def OnControlKeyDown (self,event=None):

        # __pychecker__ = '--no-argsused' # event not used.

        self.controlKeyIsDown = True

    def OnControlKeyUp (self,event=None):

        # __pychecker__ = '--no-argsused' # event not used.

        self.controlKeyIsDown = False
    #@-node:ekr.20080112145409.120:frame.OnControlKeyUp/Down
    #@+node:ekr.20080112145409.121:OnActivateBody (gtkFrame)
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
    #@-node:ekr.20080112145409.121:OnActivateBody (gtkFrame)
    #@+node:ekr.20080112145409.122:OnActivateLeoEvent, OnDeactivateLeoEvent
    def OnActivateLeoEvent(self,event=None):

        '''Handle a click anywhere in the Leo window.'''

        # __pychecker__ = '--no-argsused' # event.

        self.c.setLog()

    def OnDeactivateLeoEvent(self,event=None):

        pass # This causes problems on the Mac.
    #@-node:ekr.20080112145409.122:OnActivateLeoEvent, OnDeactivateLeoEvent
    #@+node:ekr.20080112145409.123:OnActivateTree
    def OnActivateTree (self,event=None):

        try:
            frame = self ; c = frame.c
            c.setLog()

            if 0: # Do NOT do this here!
                # OnActivateTree can get called when the tree gets DE-activated!!
                c.bodyWantsFocus()

        except:
            g.es_event_exception("activate tree")
    #@-node:ekr.20080112145409.123:OnActivateTree
    #@+node:ekr.20080112145409.124:OnBodyClick, OnBodyRClick (Events)
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
    #@-node:ekr.20080112145409.124:OnBodyClick, OnBodyRClick (Events)
    #@+node:ekr.20080112145409.125:OnBodyDoubleClick (Events)
    def OnBodyDoubleClick (self,event=None):

        try:
            c = self.c ; p = c.currentPosition()
            if event and not g.doHook("bodydclick1",c=c,p=p,v=p,event=event):
                c.editCommands.extendToWord(event) # Handles unicode properly.
            g.doHook("bodydclick2",c=c,p=p,v=p,event=event)
        except:
            g.es_event_exception("bodydclick")

        return "break" # Restore this to handle proper double-click logic.
    #@-node:ekr.20080112145409.125:OnBodyDoubleClick (Events)
    #@+node:ekr.20080112145409.126:OnMouseWheel (Tomaz Ficko)
    # Contributed by Tomaz Ficko.  This works on some systems.
    # On XP it causes a crash in tcl83.dll.  Clearly a Tk bug.

    def OnMouseWheel(self, event=None):

        # try:
            # if event.delta < 1:
                # self.canvas.yview(Tk.SCROLL, 1, Tk.UNITS)
            # else:
                # self.canvas.yview(Tk.SCROLL, -1, Tk.UNITS)
        # except:
            # g.es_event_exception("scroll wheel")

        return "break"
    #@-node:ekr.20080112145409.126:OnMouseWheel (Tomaz Ficko)
    #@-node:ekr.20080112145409.118:Event handlers (gtkFrame)
    #@+node:ekr.20080112145409.127:Gui-dependent commands
    #@+node:ekr.20080112145409.128:Minibuffer commands... (gtkFrame)

    #@+node:ekr.20080112145409.129:contractPane
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
    #@-node:ekr.20080112145409.129:contractPane
    #@+node:ekr.20080112145409.130:expandPane
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
    #@-node:ekr.20080112145409.130:expandPane
    #@+node:ekr.20080112145409.131:fullyExpandPane
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
    #@-node:ekr.20080112145409.131:fullyExpandPane
    #@+node:ekr.20080112145409.132:hidePane
    def hidePane (self,event=None):

        '''Completely contract the selected pane.'''

        f = self ; c = f.c

        w = c.get_requested_focus()
        wname = c.widget_name(w)

        #g.trace(wname)
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
    #@-node:ekr.20080112145409.132:hidePane
    #@+node:ekr.20080112145409.133:expand/contract/hide...Pane
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
    #@-node:ekr.20080112145409.133:expand/contract/hide...Pane
    #@+node:ekr.20080112145409.134:fullyExpand/hide...Pane
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
    #@-node:ekr.20080112145409.134:fullyExpand/hide...Pane
    #@-node:ekr.20080112145409.128:Minibuffer commands... (gtkFrame)
    #@+node:ekr.20080112145409.135:Window Menu...
    #@+node:ekr.20080112145409.136:toggleActivePane
    def toggleActivePane (self,event=None):

        '''Toggle the focus between the outline and body panes.'''

        frame = self ; c = frame.c

        if c.get_focus() == frame.body.bodyCtrl: # 2007:10/25
            c.treeWantsFocusNow()
        else:
            c.endEditing()
            c.bodyWantsFocusNow()
    #@-node:ekr.20080112145409.136:toggleActivePane
    #@+node:ekr.20080112145409.137:cascade
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
    #@-node:ekr.20080112145409.137:cascade
    #@+node:ekr.20080112145409.138:equalSizedPanes
    def equalSizedPanes (self,event=None):

        '''Make the outline and body panes have the same size.'''

        frame = self
        frame.f1.ratio = 0.5
    #@-node:ekr.20080112145409.138:equalSizedPanes
    #@+node:ekr.20080112145409.139:hideLogWindow
    def hideLogWindow (self,event=None):

        frame = self
        frame.divideLeoSplitter2(0.99, not frame.splitVerticalFlag)
    #@-node:ekr.20080112145409.139:hideLogWindow
    #@+node:ekr.20080112145409.140:minimizeAll
    def minimizeAll (self,event=None):

        '''Minimize all Leo's windows.'''

        self.minimize(g.app.pythonFrame)
        for frame in g.app.windowList:
            self.minimize(frame)
            self.minimize(frame.findPanel)

    def minimize(self,frame):

        if frame:
            frame.top.iconify()
    #@-node:ekr.20080112145409.140:minimizeAll
    #@+node:ekr.20080112145409.141:toggleSplitDirection (gtkFrame)
    # The key invariant: self.splitVerticalFlag tells the alignment of the main splitter.

    def toggleSplitDirection (self,event=None):

        f = self

        #g.trace(f, f.f1, f.f2)

        '''Toggle the split direction in the present Leo window.'''

        # Switch directions.
        c = self.c
        self.splitVerticalFlag = not self.splitVerticalFlag

        orientation = g.choose(self.splitVerticalFlag,"vertical","horizontal")

        c.config.set("initial_splitter_orientation","string",orientation)

        self.toggleGtkSplitDirection(self.splitVerticalFlag)
    #@+node:ekr.20080112145409.142:toggleGtkSplitDirection
    def toggleGtkSplitDirection (self,verticalFlag=None):
        """Strip the splitters and create new ones in the desired orientation.

        'verticalFlag' is not used in gtkGui.

        """

        f = self

        f.mainSplitterPanel.remove(f.f1)

        tree = f.f2.get_child1()
        f.f2.remove(tree)

        log = f.f2.get_child2()
        f.f2.remove(log)

        body = f.f1.get_child2()
        f.f1.remove(body)

        f.f1.remove(f.f2)

        f.f1 = f.f2 = None

        self.createLeoSplitters(f)

        f.f2.pack1(tree)
        f.f2.pack2(log)
        f.f1.pack1(f.f2)

        f.f1.pack2(body)

        f.top.show_all()

    #@-node:ekr.20080112145409.142:toggleGtkSplitDirection
    #@-node:ekr.20080112145409.141:toggleSplitDirection (gtkFrame)
    #@+node:ekr.20080112145409.143:resizeToScreen
    def resizeToScreen (self,event=None):

        '''Resize the Leo window so it fills the entire screen.'''

        self.top.maximize()
    #@-node:ekr.20080112145409.143:resizeToScreen
    #@-node:ekr.20080112145409.135:Window Menu...
    #@+node:ekr.20080112145409.144:Help Menu...
    #@+node:ekr.20080112145409.145:leoHelp
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
    #@+node:ekr.20080112145409.146:showProgressBar
    def showProgressBar (self,count,size,total):

        # g.trace("count,size,total:",count,size,total)
        if self.scale == None:
            #@        << create the scale widget >>
            #@+node:ekr.20080112145409.147:<< create the scale widget >>
            top = gtk.Window() # Tk.Toplevel()
            top.title("Download progress")
            # self.scale = scale = Tk.Scale(top,state="normal",orient="horizontal",from_=0,to=total)
            # scale.pack()
            top.lift()
            #@-node:ekr.20080112145409.147:<< create the scale widget >>
            #@nl
        self.scale.set(count*size)
        self.scale.update_idletasks()
    #@-node:ekr.20080112145409.146:showProgressBar
    #@-node:ekr.20080112145409.145:leoHelp
    #@-node:ekr.20080112145409.144:Help Menu...
    #@-node:ekr.20080112145409.127:Gui-dependent commands
    #@+node:ekr.20080112145409.149:Gtk bindings... (gtkFrame)
    def bringToFront (self):
        self.top.present()


    def getFocus(self):
        """Returns the widget that has focus, or body if None."""
        g.trace()
        # try:
            # # This method is unreliable while focus is changing.
            # # The call to update_idletasks may help.  Or not.
            # self.top.update_idletasks()
            # f = self.top.focus_displayof()
        # except Exception:
            # f = None
        # if f:
            # return f
        # else:
            # return self.body.bodyCtrl

    def getTitle (self):
        return self.top and self.top.get_title() or '<no title>'

    def setTitle (self,title):
        return self.top.set_title(title)

    def get_window_info(self):
        g.trace()
        # return g.app.gui.get_window_info(self.top)

    def iconify(self):
        self.top.iconify()

    def deiconify (self):
        self.top.deiconify()

    def lift (self):
        self.top.present()

    def update (self):
        g.trace() # self.top.update()
    #@-node:ekr.20080112145409.149:Gtk bindings... (gtkFrame)
    #@+node:bob.20080116222005:not used
    #@+node:ekr.20080112145409.109:configureBar (gtkFrame)
    def configureBar (self,bar,verticalFlag):

        return
    #@nonl
    #@-node:ekr.20080112145409.109:configureBar (gtkFrame)
    #@+node:ekr.20080112145409.110:configureBarsFromConfig (gtkFrame)
    def configureBarsFromConfig (self):

        return
    #@-node:ekr.20080112145409.110:configureBarsFromConfig (gtkFrame)
    #@+node:ekr.20080112145409.113:setTabWidth (gtkFrame)
    def setTabWidth (self, w):

        pass

        # try: # This can fail when called from scripts
            # # Use the present font for computations.
            # font = self.bodyCtrl.cget("font")
            # root = g.app.root # 4/3/03: must specify root so idle window will work properly.
            # font = gtkFont.Font(root=root,font=font)
            # tabw = font.measure(" " * abs(w)) # 7/2/02
            # self.bodyCtrl.configure(tabs=tabw)
            # self.tab_width = w
            # # g.trace(w,tabw)
        # except:
            # g.es_exception()
            # pass
    #@-node:ekr.20080112145409.113:setTabWidth (gtkFrame)
    #@+node:ekr.20080112145409.148:Delayed Focus (gtkFrame)
    #@+at 
    #@nonl
    # New in 4.3. The proper way to change focus is to call 
    # c.frame.xWantsFocus.
    # 
    # Important: This code never calls select, so there can be no race 
    # condition here
    # that alters text improperly.
    #@-at
    #@-node:ekr.20080112145409.148:Delayed Focus (gtkFrame)
    #@-node:bob.20080116222005:not used
    #@-others
#@-node:ekr.20080112145409.55:class leoGtkFrame
#@+node:ekr.20080112145409.150:class leoGtkBody
class leoGtkBody (leoFrame.leoBody):

    ###

    # def __init__ (self,frame,parentFrame):
        # # g.trace('leoGtkBody')
        # leoFrame.leoBody.__init__(self,frame,parentFrame) # Init the base class.

    # # Birth, death & config...
    # def createBindings (self,w=None):         pass
    # def createControl (self,parentFrame,p):   pass
    # def setColorFromConfig (self,w=None):     pass
    # def setFontFromConfig (self,w=None):      pass

    # # Editor...
    # def createEditorLabel (self,pane):  pass
    # def setEditorColors (self,bg,fg):   pass

    # # Events...
    # def scheduleIdleTimeRoutine (self,function,*args,**keys): pass

    #@    @+others
    #@+node:ekr.20080112145409.151: Birth & death
    #@+node:ekr.20080112145409.152:gtkBody. __init__
    def __init__ (self,frame,parentFrame):

        #g.trace('leoGtkBody')

        # Call the base class constructor.
        leoFrame.leoBody.__init__(self,frame,parentFrame)

        c = self.c ; p = c.currentPosition()
        self.editor_name = None
        self.editor_v = None

        self.trace_onBodyChanged = c.config.getBool('trace_onBodyChanged')
        self.bodyCtrl = self.createControl(parentFrame,p)
        self.colorizer = leoColor.colorizer(c)
    #@-node:ekr.20080112145409.152:gtkBody. __init__
    #@+node:ekr.20080112145409.153:gtkBody.createBindings
    def createBindings (self,w=None):

        '''(gtkBody) Create gui-dependent bindings.
        These are *not* made in nullBody instances.'''

        frame = self.frame ; c = self.c ; k = c.k
        if not w: w = self.bodyCtrl

        # c.bind(w,'<Key>', k.masterKeyHandler)

        # for kind,func,handler in (
            # ('<Button-1>',  frame.OnBodyClick,          k.masterClickHandler),
            # ('<Button-3>',  frame.OnBodyRClick,         k.masterClick3Handler),
            # ('<Double-1>',  frame.OnBodyDoubleClick,    k.masterDoubleClickHandler),
            # ('<Double-3>',  None,                       k.masterDoubleClick3Handler),
            # ('<Button-2>',  frame.OnPaste,              k.masterClickHandler),
        # ):
            # def bodyClickCallback(event,handler=handler,func=func):
                # return handler(event,func)

            # c.bind(w,kind,bodyClickCallback)
    #@nonl
    #@-node:ekr.20080112145409.153:gtkBody.createBindings
    #@+node:ekr.20080112145409.154:gtkBody.createControl
    def createControl (self,parentFrame,p):

        c = self.c

        g.trace('gtkBody')

        # New in 4.4.1: make the parent frame a PanedWidget.
        self.numberOfEditors = 1 ; name = '1'
        self.totalNumberOfEditors = 1

        orient = c.config.getString('editor_orientation') or 'horizontal'
        if orient not in ('horizontal','vertical'): orient = 'horizontal'

        # self.pb = pb = Pmw.PanedWidget(parentFrame,orient=orient)
        # parentFrame = pb.add(name)
        # pb.pack(expand=1,fill='both') # Must be done after the first page created.

        w = self.createTextWidget(parentFrame,p,name)
        self.editorWidgets[name] = w

        return w
    #@-node:ekr.20080112145409.154:gtkBody.createControl
    #@+node:ekr.20080112145409.155:gtkBody.createTextWidget
    def createTextWidget (self,parentFrame,p,name):

        c = self.c

        # parentFrame.configure(bg='LightSteelBlue1')

        wrap = c.config.getBool('body_pane_wraps')
        wrap = g.choose(wrap,"word","none")

        # # Setgrid=1 cause severe problems with the font panel.
        body = w = leoGtkTextWidget (c, name='body-pane',
            bd=2,bg="white",relief="flat",setgrid=0,wrap=wrap)

        bodyBar = None ###
        bodyXBar = None ###
        # bodyBar = Tk.Scrollbar(parentFrame,name='bodyBar')

        # def yscrollCallback(x,y,bodyBar=bodyBar,w=w):
            # # g.trace(x,y,g.callers())
            # if hasattr(w,'leo_scrollBarSpot'):
                # w.leo_scrollBarSpot = (x,y)
            # return bodyBar.set(x,y)

        # body['yscrollcommand'] = yscrollCallback # bodyBar.set

        # bodyBar['command'] =  body.yview
        # bodyBar.pack(side="right", fill="y")

        # # Always create the horizontal bar.
        # bodyXBar = Tk.Scrollbar(
            # parentFrame,name='bodyXBar',orient="horizontal")
        # body['xscrollcommand'] = bodyXBar.set
        # bodyXBar['command'] = body.xview

        # if wrap == "none":
            # # g.trace(parentFrame)
            # bodyXBar.pack(side="bottom", fill="x")

        # body.pack(expand=1,fill="both")

        # self.wrapState = wrap

        # if 0: # Causes the cursor not to blink.
            # body.configure(insertofftime=0)

        # # Inject ivars
        if name == '1':
            w.leo_p = w.leo_v = None # Will be set when the second editor is created.
        else:
            w.leo_p = p.copy()
            w.leo_v = w.leo_p.v
                # pychecker complains body.leo_p does not exist.
        w.leo_active = True
        w.leo_bodyBar = bodyBar
        w.leo_bodyXBar = bodyXBar
        w.leo_chapter = None
        w.leo_frame = parentFrame
        w.leo_name = name
        w.leo_label = None
        w.leo_label_s = None
        w.leo_scrollBarSpot = None
        w.leo_insertSpot = None
        w.leo_selection = None

        return w
    #@-node:ekr.20080112145409.155:gtkBody.createTextWidget
    #@-node:ekr.20080112145409.151: Birth & death
    #@+node:ekr.20080112145409.156:gtkBody.setColorFromConfig
    def setColorFromConfig (self,w=None):

        c = self.c
        if w is None: w = self.bodyCtrl

        return ###

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
    #@-node:ekr.20080112145409.156:gtkBody.setColorFromConfig
    #@+node:ekr.20080112145409.157:gtkBody.setFontFromConfig
    def setFontFromConfig (self,w=None):

        c = self.c

        if not w: w = self.bodyCtrl

        font = c.config.getFontFromParams(
            "body_text_font_family", "body_text_font_size",
            "body_text_font_slant",  "body_text_font_weight",
            c.config.defaultBodyFontSize)

        self.fontRef = font # ESSENTIAL: retain a link to font.
        ### w.configure(font=font)

        # g.trace("BODY",body.cget("font"),font.cget("family"),font.cget("weight"))
    #@-node:ekr.20080112145409.157:gtkBody.setFontFromConfig
    #@+node:ekr.20080112145409.158:Focus (gtkBody)
    def hasFocus (self):

        return self.bodyCtrl == self.frame.top.focus_displayof()

    def setFocus (self):

        self.c.widgetWantsFocus(self.bodyCtrl)
    #@-node:ekr.20080112145409.158:Focus (gtkBody)
    #@+node:ekr.20080112145409.159:forceRecolor
    def forceFullRecolor (self):

        self.forceFullRecolorFlag = True
    #@-node:ekr.20080112145409.159:forceRecolor
    #@+node:ekr.20080112145409.160:Tk bindings (gtkBbody)
    #@+node:ekr.20080112145409.161:bind (new)
    def bind (self,*args,**keys):

        pass
    #@-node:ekr.20080112145409.161:bind (new)
    #@+node:ekr.20080112145409.162:Tags (Tk spelling) (gtkBody)
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
    #@-node:ekr.20080112145409.162:Tags (Tk spelling) (gtkBody)
    #@+node:ekr.20080112145409.163:Configuration (Tk spelling) (gtkBody)
    def cget(self,*args,**keys):

        body = self ; w = self.bodyCtrl
        val = w.cget(*args,**keys)

        if g.app.trace:
            g.trace(val,args,keys)

        return val

    def configure (self,*args,**keys):

        # g.trace(args,keys)

        body = self ; w = body.bodyCtrl
        return w.configure(*args,**keys)
    #@-node:ekr.20080112145409.163:Configuration (Tk spelling) (gtkBody)
    #@+node:ekr.20080112145409.164:Height & width (gtkBody)
    def getBodyPaneHeight (self):

        return self.bodyCtrl.winfo_height()

    def getBodyPaneWidth (self):

        return self.bodyCtrl.winfo_width()
    #@-node:ekr.20080112145409.164:Height & width (gtkBody)
    #@+node:ekr.20080112145409.165:Idle time... (gtkBody)
    def scheduleIdleTimeRoutine (self,function,*args,**keys):

        pass ### self.bodyCtrl.after_idle(function,*args,**keys)
    #@-node:ekr.20080112145409.165:Idle time... (gtkBody)
    #@+node:ekr.20080112145409.166:Menus (gtkBody)
    def bind (self,*args,**keys):

        pass ### return self.bodyCtrl.bind(*args,**keys)
    #@-node:ekr.20080112145409.166:Menus (gtkBody)
    #@+node:ekr.20080112145409.167:Text (now in base class) (gtkBody)
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
    #@-node:ekr.20080112145409.167:Text (now in base class) (gtkBody)
    #@-node:ekr.20080112145409.160:Tk bindings (gtkBbody)
    #@+node:ekr.20080112145409.168:Editors (gtkBody)
    #@+node:ekr.20080112145409.169:createEditorFrame
    def createEditorFrame (self,pane):

        f = gtk.Frame(pane)
        f.pack(side='top',expand=1,fill='both')
        return f
    #@-node:ekr.20080112145409.169:createEditorFrame
    #@+node:ekr.20080112145409.170:packEditorLabelWidget
    def packEditorLabelWidget (self,w):

        '''Create a gtk label widget.'''

        if not hasattr(w,'leo_label') or not w.leo_label:
            # g.trace('w.leo_frame',id(w.leo_frame))
            w.pack_forget()
            w.leo_label = gtk.Label(w.leo_frame)
            w.leo_label.pack(side='top')
            w.pack(expand=1,fill='both')
    #@nonl
    #@-node:ekr.20080112145409.170:packEditorLabelWidget
    #@+node:ekr.20080112145409.171:setEditorColors
    def setEditorColors (self,bg,fg):

        c = self.c ; d = self.editorWidgets

        ###

        # for key in d.keys():
            # w2 = d.get(key)
            # # g.trace(id(w2),bg,fg)
            # try:
                # w2.configure(bg=bg,fg=fg)
            # except Exception:
                # g.es_exception()
                # pass
    #@-node:ekr.20080112145409.171:setEditorColors
    #@-node:ekr.20080112145409.168:Editors (gtkBody)
    #@-others
#@-node:ekr.20080112145409.150:class leoGtkBody
#@+node:bob.20080119081548:== Leo Log (gtk) ==
#@+node:bob.20080119074840:class LogTab
class LogTab(gtk.VBox):

    """A window used as pages in the gtkLogNotebook


    This window also manages a label wiget which can be used in
    gtk.Notebook tabs.

    """

    #@    @+others
    #@+node:bob.20080119081548.1:__init__ (LogTab)
    def __init__(self, c,
         tabName,
         labelWidget=None,
         frameWidget=None
    ):

        """Construct a LogWindow based on a gtk.VBox widget

        tabName is the name to be used to identify this widget.

        labelWidget is the widget used as a label in notebook tabs.
            If this is None a gtk.Label widget will be used with
            its text set to tabName.

        frame widget is the initial widget to be packed into
            this VBox and may be None.

        """

        super(LogTab, self).__gobject_init__()

        self.c = c
        self.nb = None 

        self.set_size_request(10, 10)

        if frameWidget:
            self.add(frameWidget)

        self.tabName = tabName

        if not labelWidget:
            labelWidget = gtk.Label(tabName)

        self.labelWidget = labelWidget

        self.show_all()
    #@-node:bob.20080119081548.1:__init__ (LogTab)
    #@-others


gobject.type_register(LogTab)
#@-node:bob.20080119074840:class LogTab
#@+node:bob.20080119070534.1:class _gtkLogNotebook (gtk.Notebook)
class _gtkLogNotebook (gtk.Notebook):

    """This is a wrapper around gtk.Notebook.

    The purpose of this wrapper is to provide leo specific
    additions and modifications to the native Notebook object.

    Although little is being done with this at the moment, future
    enhancement may include the ability to hide tabs, to drag
    them from one notebook to another, and to pop the tabs out
    of the notebook into there own frame.

    """

    #@    @+others
    #@+node:bob.20080119070534.2:__init__ (_gtkLogNotebook)
    def __init__ (self, c):

        """Create and wrap a gtk.Notebok. Do leo specific initailization."""

        gtk.Notebook.__gobject_init__(self)

        self.c = c
        self.tabNames = {}
    #@-node:bob.20080119070534.2:__init__ (_gtkLogNotebook)
    #@+node:bob.20080119074425.2:selectPage
    def selectpage(self, tabName):
        """Select the page in the notebook with name 'tabName'.

        A KeyError exception is raised if the tabName is not known.

        """

        tabCtrl = self.tabNames[tabName]

        self.set_current_page(self.page_num(tabCtrl))






    #@-node:bob.20080119074425.2:selectPage
    #@+node:bob.20080119074425.3:add
    def add(self, tab):
        """Add a tab as the last page in the notebook.

        'tab' may be an instance of LogTab or basestring.

        if 'tab' is a string a default LogTab will be constructed and returned
            with tab used as a tabName.

        if 'tab is a LogTab it must have tab.tabName set. If labelWidget is not
            set a gtk.Label will be used with its text set to tabName.

        either tab or a new instance of LogTab will be returned.

        """

        if isinstance(tab, basestring):
            tab = LogTab(self.c, tab)

        assert isinstance(tab, LogTab)

        tabName = tab.tabName

        tab.nb = self

        if not tab.labelWidget:
            tab.labelWidget = gtk.Label(tab.tabName)

        self.tabNames[tabName] = tab
        self.append_page(tab, tab.labelWidget)

        return tab




    #@-node:bob.20080119074425.3:add
    #@+node:bob.20080119085509:pageNames
    def pagenames(self):
        """Return a list of pagenames managed by this notebook."""

        return self.tabNames.keys()
    #@-node:bob.20080119085509:pageNames
    #@-others

gobject.type_register(_gtkLogNotebook)
#@-node:bob.20080119070534.1:class _gtkLogNotebook (gtk.Notebook)
#@+node:ekr.20080112145409.205:class leoGtkLog
class leoGtkLog (leoFrame.leoLog):

    """A class that represents the log pane of a gtk window."""

    #@    @+others
    #@+node:ekr.20080112145409.206:gtkLog Birth
    #@+node:ekr.20080112145409.207:gtkLog.__init__
    def __init__ (self,frame,parentFrame):
        """Create an instance of the leoGtkLog Adaptor class.

        All access to the funtions of this class should be via c.frame.log
        or the global methods provided.

        At the moment legCtrl is the notebook control but it should not be assumed
        that this is so 

        """

        g.trace("leoGtkLog")

        # Call the base class constructor and calls createControl.
        leoFrame.leoLog.__init__(self,frame,parentFrame)

        self.c = c = frame.c # Also set in the base constructor, but we need it here.

        self.wrap = g.choose(c.config.getBool('log_pane_wraps'),"word","none")


        self.nb = None      # _gtkLogNotebook that holds all the tabs.
        self.colorTagsDict = {} # Keys are page names.  Values are saved colorTags lists.
        self.menu = None # A menu that pops up on right clicks in the hull or in tabs.

        self.createControl(parentFrame)
        #self.setFontFromConfig()
        #self.setColorFromConfig()

    #@+at
    # #==
    #     self.c = c
    # 
    #     self.nb = gtk.Notebook()
    # 
    #     self.isNull = False
    #     self.logCtrl = None
    #     self.newlines = 0
    #     self.frameDict = {} # Keys are log names, values are None or 
    # wx.Frames.
    #     self.textDict = {}  # Keys are log names, values are None or Text 
    # controls.
    # 
    #     self.createInitialTabs()
    #     self.setFontFromConfig()
    # 
    # 
    #@-at
    #@-node:ekr.20080112145409.207:gtkLog.__init__
    #@+node:ekr.20080112145409.208:gtkLog.createControl
    def createControl (self,parentFrame):

        """Create the base gtkLog control.

        """

        c = self.c

        self.nb = _gtkLogNotebook(c)

        # menu = self.makeTabMenu(tabName=None)

        # def hullMenuCallback(event):
            # return self.onRightClick(event,menu)

        # c.bind(self.nb,'<Button-3>',hullMenuCallback)

        # self.nb.pack(fill='both',expand=1)

        # Create and activate the default tabs.
        return self.selectTab('Log')
    #@-node:ekr.20080112145409.208:gtkLog.createControl
    #@+node:ekr.20080112145409.209:gtkLog.finishCreate
    def finishCreate (self):

        # g.trace('gtkLog')

        c = self.c ; log = self

        #'c.searchCommands.openFindTab(show=False)
        #'c.spellCommands.openSpellTab()
        log.selectTab('Log')
    #@-node:ekr.20080112145409.209:gtkLog.finishCreate
    #@+node:ekr.20080112145409.210:gtkLog.createTextWidget
    def createTextWidget (self,parentFrame):

        c = self.c

        self.logNumber += 1

        log = g.app.gui.plainTextWidget(c,
            name="log-%d" % self.logNumber,
            setgrid=0,wrap=self.wrap,bd=2,bg="white",relief="flat"
        )

        # logBar = gtk.Scrollbar(parentFrame,name="logBar")

        # log['yscrollcommand'] = logBar.set
        # logBar['command'] = log.yview

        # logBar.pack(side="right", fill="y")
        # # rr 8/14/02 added horizontal elevator 
        # if self.wrap == "none": 
            # logXBar = gtk.Scrollbar( 
                # parentFrame,name='logXBar',orient="horizontal") 
            # log['xscrollcommand'] = logXBar.set 
            # logXBar['command'] = log.xview 
            # logXBar.pack(side="bottom", fill="x")
        # log.pack(expand=1, fill="both")

        return log
    #@-node:ekr.20080112145409.210:gtkLog.createTextWidget
    #@+node:ekr.20080112145409.211:gtkLog.makeTabMenu
    def makeTabMenu (self,tabName=None):

        '''Create a tab popup menu.'''

        # g.trace(tabName,g.callers())

        c = self.c
        # hull = self.nb.component('hull') # A Tk.Canvas.

        # menu = Tk.Menu(hull,tearoff=0)
        # menu.add_command(label='New Tab',command=self.newTabFromMenu)

        # if tabName:
            # # Important: tabName is the name when the tab is created.
            # # It is not affected by renaming, so we don't have to keep
            # # track of the correspondence between this name and what is in the label.
            # def deleteTabCallback():
                # return self.deleteTab(tabName)

            # label = g.choose(
                # tabName in ('Find','Spell'),'Hide This Tab','Delete This Tab')
            # menu.add_command(label=label,command=deleteTabCallback)

            # def renameTabCallback():
                # return self.renameTabFromMenu(tabName)

            # menu.add_command(label='Rename This Tab',command=renameTabCallback)

        # return menu
    #@-node:ekr.20080112145409.211:gtkLog.makeTabMenu
    #@-node:ekr.20080112145409.206:gtkLog Birth
    #@+node:ekr.20080112145409.212:Config & get/saveState
    #@+node:ekr.20080112145409.213:gtkLog.configureBorder & configureFont
    def configureBorder(self,border):

        self.logCtrl.configure(bd=border)

    def configureFont(self,font):

        self.logCtrl.configure(font=font)
    #@-node:ekr.20080112145409.213:gtkLog.configureBorder & configureFont
    #@+node:ekr.20080112145409.214:gtkLog.getFontConfig
    def getFontConfig (self):

        font = self.logCtrl.cget("font")
        # g.trace(font)
        return font
    #@-node:ekr.20080112145409.214:gtkLog.getFontConfig
    #@+node:ekr.20080112145409.215:gtkLog.restoreAllState
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
    #@-node:ekr.20080112145409.215:gtkLog.restoreAllState
    #@+node:ekr.20080112145409.216:gtkLog.saveAllState
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
    #@-node:ekr.20080112145409.216:gtkLog.saveAllState
    #@+node:ekr.20080112145409.217:gtkLog.setColorFromConfig
    def setColorFromConfig (self):

        c = self.c

        bg = c.config.getColor("log_pane_background_color") or 'white'

        try:
            self.logCtrl.configure(bg=bg)
        except:
            g.es("exception setting log pane background color")
            g.es_exception()
    #@-node:ekr.20080112145409.217:gtkLog.setColorFromConfig
    #@+node:ekr.20080112145409.218:gtkLog.setFontFromConfig
    def SetWidgetFontFromConfig (self,logCtrl=None):

        c = self.c

        if not logCtrl: logCtrl = self.logCtrl

        font = c.config.getFontFromParams(
            "log_text_font_family", "log_text_font_size",
            "log_text_font_slant", "log_text_font_weight",
            c.config.defaultLogFontSize)

        self.fontRef = font # ESSENTIAL: retain a link to font.
        ### logCtrl.configure(font=font)

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
    #@-node:ekr.20080112145409.218:gtkLog.setFontFromConfig
    #@-node:ekr.20080112145409.212:Config & get/saveState
    #@+node:ekr.20080112145409.219:Focus & update (gtkLog)
    #@+node:ekr.20080112145409.220:gtkLog.onActivateLog
    def onActivateLog (self,event=None):

        try:
            self.c.setLog()
            self.frame.tree.OnDeactivate()
            self.c.logWantsFocus()
        except:
            g.es_event_exception("activate log")
    #@-node:ekr.20080112145409.220:gtkLog.onActivateLog
    #@+node:ekr.20080112145409.221:gtkLog.hasFocus
    def hasFocus (self):

        return self.c.get_focus() == self.logCtrl
    #@-node:ekr.20080112145409.221:gtkLog.hasFocus
    #@+node:ekr.20080112145409.222:forceLogUpdate
    def forceLogUpdate (self,s):

        if sys.platform == "darwin": # Does not work on MacOS X.
            try:
                print s, # Don't add a newline.
            except UnicodeError:
                # g.app may not be inited during scripts!
                print g.toEncodedString(s,'utf-8')
        else:
            self.logCtrl.update_idletasks()
    #@-node:ekr.20080112145409.222:forceLogUpdate
    #@-node:ekr.20080112145409.219:Focus & update (gtkLog)
    #@+node:ekr.20080112145409.223:put & putnl (gtkLog)
    #@+at 
    #@nonl
    # Printing uses self.logCtrl, so this code need not concern itself
    # with which tab is active.
    # 
    # Also, selectTab switches the contents of colorTags, so that is not 
    # concern.
    # It may be that Pmw will allow us to dispense with the colorTags logic...
    #@-at
    #@+node:ekr.20080112145409.224:put
    # All output to the log stream eventually comes here.
    def put (self,s,color=None,tabName='Log'):

        c = self.c

        #print 'gtkLog.put', s, color, tabName #self.c.shortFileName(),tabName,g.callers()

        if g.app.quitting or not c or not c.exists:
            return

        if tabName:
            self.selectTab(tabName)

        if self.logCtrl:
            #@        << put s to log control >>
            #@+node:ekr.20080112145409.225:<< put s to log control >>
            # if color:
                # if color not in self.colorTags:
                    # self.colorTags.append(color)
                    # self.logCtrl.tag_config(color,foreground=color)
                # self.logCtrl.insert("end",s)
                # self.logCtrl.tag_add(color,"end-%dc" % (len(s)+1),"end-1c")
                # self.logCtrl.tag_add("black","end")
            # else:
                # self.logCtrl.insert("end",s)

            self.logCtrl.insert("end",s)
            self.logCtrl.see('end')
            #self.forceLogUpdate(s)
            #@-node:ekr.20080112145409.225:<< put s to log control >>
            #@nl
            # self.logCtrl.update_idletasks()
        # else:
            # 
            #@nonl
            #@<< put s to logWaiting and print s >>
            #@+node:ekr.20080112145409.226:<< put s to logWaiting and print s >>
            # g.app.logWaiting.append((s,color),)

            # print "Null gtk log"

            # if type(s) == type(u""):
                # s = g.toEncodedString(s,"ascii")

            # print s
            #@-node:ekr.20080112145409.226:<< put s to logWaiting and print s >>
            #@nl
    #@-node:ekr.20080112145409.224:put
    #@+node:ekr.20080112145409.227:putnl
    def putnl (self,tabName='Log'):


        if g.app.quitting:
            return

        if tabName:
            self.selectTab(tabName)

        if self.logCtrl:
            self.logCtrl.insert("end",'\n')
            self.logCtrl.see('end')
            # self.forceLogUpdate('\n')
        # else:
            # # Put a newline to logWaiting and print newline
            # g.app.logWaiting.append(('\n',"black"),)
            # print "Null gtk log"
            # print
    #@-node:ekr.20080112145409.227:putnl
    #@-node:ekr.20080112145409.223:put & putnl (gtkLog)
    #@+node:ekr.20080112145409.228:Tab (GtkLog)
    #@+node:ekr.20080112145409.229:clearTab
    def clearTab (self,tabName,wrap='none'):

        self.selectTab(tabName,wrap=wrap)
        w = self.logCtrl
        w and w.delete(0,'end')
    #@-node:ekr.20080112145409.229:clearTab
    #@+node:ekr.20080112145409.230:createTab
    def createTab (self,tabName,createText=True,wrap='none'):

        g.trace(tabName,wrap)

        c = self.c ; k = c.k

        tabFrame = self.nb.add(tabName)

        #widget = TestWindow('leo pink', 'yellow')
        #tabFrame.add(widget)

        #self.textDict [tabName] = None
        #self.frameDict [tabName] = tabFrame

        # self.menu = self.makeTabMenu(tabName)
        if createText:
            #@        << Create the tab's text widget >>
            #@+node:ekr.20080112145409.231:<< Create the tab's text widget >>
            w = self.createTextWidget(tabFrame)

            # # Set the background color.
            # configName = 'log_pane_%s_tab_background_color' % tabName
            # bg = c.config.getColor(configName) or 'MistyRose1'

            # if wrap not in ('none','char','word'): wrap = 'none'
            # try: w.configure(bg=bg,wrap=wrap)
            # except Exception: pass # Could be a user error.

            # self.SetWidgetFontFromConfig(logCtrl=w)

            self.frameDict [tabName] = tabFrame
            self.textDict [tabName] = w
            tabFrame.add(w.widget)
            tabFrame.show_all()

            # # Switch to a new colorTags list.
            # if self.tabName:
                # self.colorTagsDict [self.tabName] = self.colorTags [:]

            #self.colorTags = ['black']
            #self.colorTagsDict [tabName] = self.colorTags
            #@-node:ekr.20080112145409.231:<< Create the tab's text widget >>
            #@nl
            # if tabName != 'Log':
                # # c.k doesn't exist when the log pane is created.
                # # k.makeAllBindings will call setTabBindings('Log')
                # self.setTabBindings(tabName)
        else:
            self.textDict [tabName] = None
            self.frameDict [tabName] = tabFrame


    #@-node:ekr.20080112145409.230:createTab
    #@+node:ekr.20080112145409.232:cycleTabFocus
    def cycleTabFocus (self,event=None,stop_w = None):

        '''Cycle keyboard focus between the tabs in the log pane.'''

        c = self.c ; d = self.frameDict # Keys are page names. Values are gtk.Frames.
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
    #@-node:ekr.20080112145409.232:cycleTabFocus
    #@+node:ekr.20080112145409.233:deleteTab
    def deleteTab (self,tabName,force=False):

        if tabName == 'Log':
            pass

        elif tabName in ('Find','Spell') and not force:
            self.selectTab('Log')

        elif tabName in self.nb.pagenames():
            # # g.trace(tabName,force)
            self.nb.delete(tabName)
            # self.colorTagsDict [tabName] = []
            self.textDict [tabName] = None
            self.frameDict [tabName] = None
            self.tabName = None
            self.selectTab('Log')

        # New in Leo 4.4b1.
        self.c.invalidateFocus()
        self.c.bodyWantsFocus()
    #@-node:ekr.20080112145409.233:deleteTab
    #@+node:ekr.20080112145409.234:hideTab
    def hideTab (self,tabName):

        # __pychecker__ = '--no-argsused' # tabName

        self.selectTab('Log')
    #@-node:ekr.20080112145409.234:hideTab
    #@+node:ekr.20080112145409.235:getSelectedTab
    def getSelectedTab (self):

        return self.tabName
    #@-node:ekr.20080112145409.235:getSelectedTab
    #@+node:ekr.20080112145409.236:lower/raiseTab
    def lowerTab (self,tabName):

        # if tabName:
            # b = self.nb.tab(tabName) # b is a gtk.Button.
            # b.config(bg='grey80')
        self.c.invalidateFocus()
        self.c.bodyWantsFocus()

    def raiseTab (self,tabName):

        # if tabName:
            # b = self.nb.tab(tabName) # b is a gtk.Button.
            # b.config(bg='LightSteelBlue1')
        self.c.invalidateFocus()
        self.c.bodyWantsFocus()
    #@-node:ekr.20080112145409.236:lower/raiseTab
    #@+node:ekr.20080112145409.237:numberOfVisibleTabs
    def numberOfVisibleTabs (self):

        return len([val for val in self.frameDict.values() if val != None])
    #@-node:ekr.20080112145409.237:numberOfVisibleTabs
    #@+node:ekr.20080112145409.238:renameTab
    def renameTab (self,oldName,newName):

        # g.trace('newName',newName)

        # label = self.nb.tab(oldName)
        # label.configure(text=newName)

        pass
    #@-node:ekr.20080112145409.238:renameTab
    #@+node:ekr.20080112145409.239:selectTab
    def selectTab (self,tabName,createText=True,wrap='none'):

        '''Create the tab if necessary and make it active.'''

        c = self.c

        tabFrame = self.frameDict.get(tabName)
        logCtrl = self.textDict.get(tabName)

        #g.trace(tabFrame, logCtrl)

        if not tabFrame or not logCtrl:
            self.createTab(tabName,createText=createText,wrap=wrap)

        self.nb.selectpage(tabName)

        # # Update the status vars.
        self.tabName = tabName
        self.logCtrl = self.textDict.get(tabName)
        self.tabFrame = self.frameDict.get(tabName)

        # if 0: # Absolutely do not do this here!  It is a cause of the 'sticky focus' problem.
            # c.widgetWantsFocusNow(self.logCtrl)
        return tabFrame
    #@-node:ekr.20080112145409.239:selectTab
    #@+node:ekr.20080112145409.240:setTabBindings
    def setTabBindings (self,tabName):

        c = self.c ; k = c.k
        # tab = self.nb.tab(tabName)
        # w = self.textDict.get(tabName)

        # # Send all event in the text area to the master handlers.
        # for kind,handler in (
            # ('<Key>',       k.masterKeyHandler),
            # ('<Button-1>',  k.masterClickHandler),
            # ('<Button-3>',  k.masterClick3Handler),
        # ):
            # c.bind(w,kind,handler)

        # # Clicks in the tab area are harmless: use the old code.
        # def tabMenuRightClickCallback(event,menu=self.menu):
            # return self.onRightClick(event,menu)

        # def tabMenuClickCallback(event,tabName=tabName):
            # return self.onClick(event,tabName)

        # c.bind(tab,'<Button-1>',tabMenuClickCallback)
        # c.bind(tab,'<Button-3>',tabMenuRightClickCallback)

        # k.completeAllBindingsForWidget(w)
    #@-node:ekr.20080112145409.240:setTabBindings
    #@+node:ekr.20080112145409.241:Tab menu callbacks & helpers
    #@+node:ekr.20080112145409.242:onRightClick & onClick
    def onRightClick (self,event,menu):

        c = self.c
        menu.post(event.x_root,event.y_root)


    def onClick (self,event,tabName):

        self.selectTab(tabName)
    #@-node:ekr.20080112145409.242:onRightClick & onClick
    #@+node:ekr.20080112145409.243:newTabFromMenu
    def newTabFromMenu (self,tabName='Log'):

        self.selectTab(tabName)

        # This is called by getTabName.
        def selectTabCallback (newName):
            return self.selectTab(newName)

        self.getTabName(selectTabCallback)
    #@-node:ekr.20080112145409.243:newTabFromMenu
    #@+node:ekr.20080112145409.244:renameTabFromMenu
    def renameTabFromMenu (self,tabName):

        if tabName in ('Log','Completions'):
            g.es('can not rename',tabName,'tab',color='blue')
        else:
            def renameTabCallback (newName):
                return self.renameTab(tabName,newName)

            self.getTabName(renameTabCallback)
    #@-node:ekr.20080112145409.244:renameTabFromMenu
    #@+node:ekr.20080112145409.245:getTabName
    def getTabName (self,exitCallback):

        canvas = self.nb.component('hull')

        # Overlay what is there!
        c = self.c
        f = gtk.Frame(canvas)
        f.pack(side='top',fill='both',expand=1)

        row1 = gtk.Frame(f)
        row1.pack(side='top',expand=0,fill='x',pady=10)
        row2 = gtk.Frame(f)
        row2.pack(side='top',expand=0,fill='x')

        gtk.Label(row1,text='Tab name').pack(side='left')

        e = gtk.Entry(row1,background='white')
        e.pack(side='left')

        def getNameCallback (event=None):
            s = e.get().strip()
            f.pack_forget()
            if s: exitCallback(s)

        def closeTabNameCallback (event=None):
            f.pack_forget()

        b = gtk.Button(row2,text='Ok',width=6,command=getNameCallback)
        b.pack(side='left',padx=10)

        b = gtk.Button(row2,text='Cancel',width=6,command=closeTabNameCallback)
        b.pack(side='left')

        g.app.gui.set_focus(c,e)
        c.bind(e,'<Return>',getNameCallback)
    #@-node:ekr.20080112145409.245:getTabName
    #@-node:ekr.20080112145409.241:Tab menu callbacks & helpers
    #@-node:ekr.20080112145409.228:Tab (GtkLog)
    #@+node:ekr.20080112145409.246:gtkLog color tab stuff
    def createColorPicker (self,tabName):

        log = self

        #@    << define colors >>
        #@+node:ekr.20080112145409.247:<< define colors >>
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
        #@-node:ekr.20080112145409.247:<< define colors >>
        #@nl

        parent = log.frameDict.get(tabName)
        w = log.textDict.get(tabName)
        w.pack_forget()

        colors = list(colors)
        bg = parent.cget('background')

        outer = gtk.Frame(parent,background=bg)
        outer.pack(side='top',fill='both',expand=1,pady=10)

        f = gtk.Frame(outer)
        f.pack(side='top',expand=0,fill='x')
        f1 = gtk.Frame(f) ; f1.pack(side='top',expand=0,fill='x')
        f2 = gtk.Frame(f) ; f2.pack(side='top',expand=1,fill='x')
        f3 = gtk.Frame(f) ; f3.pack(side='top',expand=1,fill='x')

        label = g.app.gui.plainTextWidget(f1,height=1,width=20)
        label.insert('1.0','Color name or value...')
        label.pack(side='left',pady=6)

        #@    << create optionMenu and callback >>
        #@+node:ekr.20080112145409.248:<< create optionMenu and callback >>
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
        #@-node:ekr.20080112145409.248:<< create optionMenu and callback >>
        #@nl
        #@    << create picker button and callback >>
        #@+node:ekr.20080112145409.249:<< create picker button and callback >>
        def pickerCallback ():
            rgb,val = gtkColorChooser.askcolor(parent=parent,initialcolor=f.cget('background'))
            if rgb or val:
                # label.configure(text=val)
                label.delete('1.0','end')
                label.insert('1.0',val)
                for theFrame in (parent,outer,f,f1,f2,f3):
                    theFrame.configure(background=val)

        b = gtk.Button(f3,text="Color Picker...",
            command=pickerCallback,background=bg)
        b.pack(side='left',pady=4)
        #@-node:ekr.20080112145409.249:<< create picker button and callback >>
        #@nl
    #@-node:ekr.20080112145409.246:gtkLog color tab stuff
    #@+node:ekr.20080112145409.250:gtkLog font tab stuff
    #@+node:ekr.20080112145409.251:createFontPicker
    def createFontPicker (self,tabName):

        log = self ; c = self.c
        parent = log.frameDict.get(tabName)
        w = log.textDict.get(tabName)
        w.pack_forget()

        bg = parent.cget('background')
        font = self.getFont()
        #@    << create the frames >>
        #@+node:ekr.20080112145409.252:<< create the frames >>
        f = gtk.Frame(parent,background=bg) ; f.pack (side='top',expand=0,fill='both')
        f1 = gtk.Frame(f,background=bg)     ; f1.pack(side='top',expand=1,fill='x')
        f2 = gtk.Frame(f,background=bg)     ; f2.pack(side='top',expand=1,fill='x')
        f3 = gtk.Frame(f,background=bg)     ; f3.pack(side='top',expand=1,fill='x')
        f4 = gtk.Frame(f,background=bg)     ; f4.pack(side='top',expand=1,fill='x')
        #@-node:ekr.20080112145409.252:<< create the frames >>
        #@nl
        #@    << create the family combo box >>
        #@+node:ekr.20080112145409.253:<< create the family combo box >>
        names = gtkFont.families()
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
        #@-node:ekr.20080112145409.253:<< create the family combo box >>
        #@nl
        #@    << create the size entry >>
        #@+node:ekr.20080112145409.254:<< create the size entry >>
        gtk.Label(f2,text="Size:",width=10,background=bg).pack(side="left")

        sizeEntry = gtk.Entry(f2,width=4)
        sizeEntry.insert(0,'12')
        sizeEntry.pack(side="left",padx=2,pady=2)
        #@-node:ekr.20080112145409.254:<< create the size entry >>
        #@nl
        #@    << create the weight combo box >>
        #@+node:ekr.20080112145409.255:<< create the weight combo box >>
        weightBox = Pmw.ComboBox(f3,
            labelpos="we",label_text="Weight:",label_width=10,
            label_background=bg,
            arrowbutton_background=bg,
            scrolledlist_items=['normal','bold'])

        weightBox.selectitem(0)
        weightBox.pack(side="left",padx=2,pady=2)
        #@-node:ekr.20080112145409.255:<< create the weight combo box >>
        #@nl
        #@    << create the slant combo box >>
        #@+node:ekr.20080112145409.256:<< create the slant combo box>>
        slantBox = Pmw.ComboBox(f4,
            labelpos="we",label_text="Slant:",label_width=10,
            label_background=bg,
            arrowbutton_background=bg,
            scrolledlist_items=['roman','italic'])

        slantBox.selectitem(0)
        slantBox.pack(side="left",padx=2,pady=2)
        #@-node:ekr.20080112145409.256:<< create the slant combo box>>
        #@nl
        #@    << create the sample text widget >>
        #@+node:ekr.20080112145409.257:<< create the sample text widget >>
        self.sampleWidget = sample = g.app.gui.plainTextWidget(f,height=20,width=80,font=font)
        sample.pack(side='left')

        s = 'The quick brown fox\njumped over the lazy dog.\n0123456789'
        sample.insert(0,s)
        #@-node:ekr.20080112145409.257:<< create the sample text widget >>
        #@nl
        #@    << create and bind the callbacks >>
        #@+node:ekr.20080112145409.258:<< create and bind the callbacks >>
        def fontCallback(event=None):
            self.setFont(familyBox,sizeEntry,slantBox,weightBox,sample)

        for w in (familyBox,slantBox,weightBox):
            w.configure(selectioncommand=fontCallback)

        c.bind(sizeEntry,'<Return>',fontCallback)
        #@-node:ekr.20080112145409.258:<< create and bind the callbacks >>
        #@nl
        self.createBindings()
    #@-node:ekr.20080112145409.251:createFontPicker
    #@+node:ekr.20080112145409.259:createBindings (fontPicker)
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
    #@-node:ekr.20080112145409.259:createBindings (fontPicker)
    #@+node:ekr.20080112145409.260:getFont
    def getFont(self,family=None,size=12,slant='roman',weight='normal'):

        try:
            return gtkFont.Font(family=family,size=size,slant=slant,weight=weight)
        except Exception:
            g.es("exception setting font")
            g.es("","family,size,slant,weight:","",family,"",size,"",slant,"",weight)
            # g.es_exception() # This just confuses people.
            return g.app.config.defaultFont
    #@-node:ekr.20080112145409.260:getFont
    #@+node:ekr.20080112145409.261:setFont
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
    #@-node:ekr.20080112145409.261:setFont
    #@+node:ekr.20080112145409.262:hideFontTab
    def hideFontTab (self,event=None):

        c = self.c
        c.frame.log.selectTab('Log')
        c.bodyWantsFocus()
    #@-node:ekr.20080112145409.262:hideFontTab
    #@-node:ekr.20080112145409.250:gtkLog font tab stuff
    #@-others
#@-node:ekr.20080112145409.205:class leoGtkLog
#@-node:bob.20080119081548:== Leo Log (gtk) ==
#@+node:ekr.20080112145409.263:class leoGtkTreeTab
class leoGtkTreeTab (leoFrame.leoTreeTab):

    '''A class representing a tabbed outline pane drawn with gtk.'''

    #@    @+others
    #@+node:ekr.20080112145409.264: Birth & death
    #@+node:ekr.20080112145409.265: ctor (leoTreeTab)
    def __init__ (self,c,parentFrame,chapterController):

        leoFrame.leoTreeTab.__init__ (self,c,chapterController,parentFrame)
            # Init the base class.  Sets self.c, self.cc and self.parentFrame.

        self.tabNames = [] # The list of tab names.  Changes when tabs are renamed.

        self.createControl()
    #@-node:ekr.20080112145409.265: ctor (leoTreeTab)
    #@+node:ekr.20080112145409.266:tt.createControl
    def createControl (self):

        tt = self ; c = tt.c

        # Create the main container.
        tt.frame = gtk.Frame(c.frame.iconFrame)
        tt.frame.pack(side="left")

        # Create the chapter menu.
        self.chapterVar = var = gtk.StringVar()
        var.set('main')

        tt.chapterMenu = menu = Pmw.OptionMenu(tt.frame,
            labelpos = 'w', label_text = 'chapter',
            menubutton_textvariable = var,
            items = [],
            command = tt.selectTab,
        )
        menu.pack(side='left',padx=5)
    #@nonl
    #@-node:ekr.20080112145409.266:tt.createControl
    #@-node:ekr.20080112145409.264: Birth & death
    #@+node:ekr.20080112145409.267:Tabs...
    #@+node:ekr.20080112145409.268:tt.createTab
    def createTab (self,tabName,select=True):

        tt = self

        if tabName not in tt.tabNames:
            tt.tabNames.append(tabName)
            tt.setNames()
    #@-node:ekr.20080112145409.268:tt.createTab
    #@+node:ekr.20080112145409.269:tt.destroyTab
    def destroyTab (self,tabName):

        tt = self

        if tabName in tt.tabNames:
            tt.tabNames.remove(tabName)
            tt.setNames()
    #@-node:ekr.20080112145409.269:tt.destroyTab
    #@+node:ekr.20080112145409.270:tt.selectTab
    def selectTab (self,tabName):

        tt = self

        if tabName not in self.tabNames:
            tt.createTab(tabName)

        tt.cc.selectChapterByName(tabName)
    #@-node:ekr.20080112145409.270:tt.selectTab
    #@+node:ekr.20080112145409.271:tt.setTabLabel
    def setTabLabel (self,tabName):

        tt = self
        tt.chapterVar.set(tabName)
    #@-node:ekr.20080112145409.271:tt.setTabLabel
    #@+node:ekr.20080112145409.272:tt.setNames
    def setNames (self):

        '''Recreate the list of items.'''

        tt = self
        names = tt.tabNames[:]
        if 'main' in names: names.remove('main')
        names.sort()
        names.insert(0,'main')
        tt.chapterMenu.setitems(names)
    #@-node:ekr.20080112145409.272:tt.setNames
    #@-node:ekr.20080112145409.267:Tabs...
    #@-others
#@nonl
#@-node:ekr.20080112145409.263:class leoGtkTreeTab
#@+node:bob.20080119110204:== Leo Text Widget (gtk) ==
#@+node:bob.20080119110204.1:class _gtkText
class _gtkText (gtk.TextView):

    """This is a wrapper around gtk.Notebook.

    The purpose of this wrapper is to provide leo specific
    additions and modifications to the native Notebook object.

    """

    #@    @+others
    #@+node:bob.20080119110204.2:__init__ (_gtkText)
    def __init__ (self, c, *args, **kw):

        """Create and wrap a gtk.TextView. Do leo specific initailization."""

        gtk.TextView.__gobject_init__(self)
        self.c = c
    #@nonl
    #@-node:bob.20080119110204.2:__init__ (_gtkText)
    #@-others

gobject.type_register(_gtkText)
#@-node:bob.20080119110204.1:class _gtkText
#@+node:ekr.20080112145409.273:class leoGtkTextWidget
class leoGtkTextWidget(leoFrame.baseTextWidget):

    '''A class to wrap the gtk.Text widget.'''

    def __repr__(self):
        name = hasattr(self,'_name') and self._name or '<no name>'
        return 'gtkTextWidget id: %s name: %s' % (id(self),name)

    #@    @+others
    #@+node:ekr.20080112145409.274:gtkTextWidget.__init__

    def __init__ (self, c, *args,**keys):

        self.c = c

        # Create the actual gui widget.
        self.widget = w = gtk.ScrolledWindow()
        w.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        self.textView = _gtkText(c, *args, **keys)
        self.textBuffer = buf = self.textView.get_buffer()

        w.add(self.textView)
        w.show_all()

        #create a mark with left gravity for our use
        self.iMark = buf.create_mark('iMark', buf.get_start_iter(), False)

        #create a mark with right gravity
        self.jMark = buf.create_mark('jMark', buf.get_end_iter(), True)

        ### To do: how an where to pack widget

        # Init the base class.
        name = keys.get('name') or '<unknown gtkTextWidget>'
        leoFrame.baseTextWidget.__init__(self,c=c,
            baseClassName='gtkTextWidget',name=name,widget=self.widget
        )

        # self.defaultFont = font = wx.Font(pointSize=10,
            # family = wx.FONTFAMILY_TELETYPE, # wx.FONTFAMILY_ROMAN,
            # style  = wx.FONTSTYLE_NORMAL,
            # weight = wx.FONTWEIGHT_NORMAL,)
    #@-node:ekr.20080112145409.274:gtkTextWidget.__init__
    #@+node:ekr.20080112145409.275:bindings (not used)
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
    # def _hitTest(self,pos):             pass ###
    # def _insertText(self,i,s):          return self.widget.insert(i,s)
    # def _scrollLines(self,n):           pass ###
    # def _see(self,i):                   return self.widget.see(i)
    # def _setAllText(self,s):            self.widget.delete('1.0','end') ; self.widget.insert('1.0',s)
    # def _setBackgroundColor(self,color): return self.widget.configure(background=color)
    # def _setForegroundColor(self,color): return self.widget.configure(background=color)
    # def _setFocus(self):                return self.widget.focus_set()
    # def _setInsertPoint(self,i):        return self.widget.mark_set('insert',i)
    # def _setSelectionRange(self,i,j):   return self.widget.SetSelection(i,j)
    #@-node:ekr.20080112145409.275:bindings (not used)
    #@+node:ekr.20080112145409.276:Index conversion (gtkTextWidget)
    #@+node:ekr.20080112145409.277:w.toGuiIndex

    def toGuiIndex (self,i,s=None):
        '''Convert a Python index to a tk index as needed.'''

        w = self
        if i is None:
            g.trace('can not happen: i is None',g.callers())
            return '1.0'
        elif type(i) == type(99):
            # The 's' arg supports the threaded colorizer.
            if s is None:
                # This *must* be 'end-1c', even if other code must change.
                s = '' ### s = gtk.Text.get(w,'1.0','end-1c')
            row,col = g.convertPythonIndexToRowCol(s,i)
            i = '%s.%s' % (row+1,col)
            # g.trace(len(s),i,repr(s))
        else:
            try:
                i = 0 ### i = gtk.Text.index(w,i)
            except Exception:
                # g.es_exception()
                g.trace('tk.Text.index failed:',repr(i),g.callers())
                i = '1.0'
        return i
    #@-node:ekr.20080112145409.277:w.toGuiIndex
    #@+node:bob.20080119200654:toGtkIter
    def toGtkIter (self,i):
        '''Convert a tk index to gtk.TextIter as needed.'''

        try:
            i = int(i)
            return self.textBuffer.get_iter_at_offset(i)
        except ValueError:
            pass

        if i == 'end':
            return self.textBuffer.get_end_iter()


        if i is None:
            g.trace('can not happen: i is None')
            pos = 0

        elif isinstance(i, basestring):
            g.trace(i)
            s = self.getAllText()
            #i = '1.0' ### i = gtk.Text.index(w,i) # Convert to row/column form.
            row,col = i.split('.')
            row,col = int(row),int(col)
            row -= 1
            pos = g.convertRowColToPythonIndex(s,row,col)
            #g.es_print(i)

        return self.textBuffer.get_iter_at_offset(i)
    #@-node:bob.20080119200654:toGtkIter
    #@+node:ekr.20080112145409.278:w.toPythonIndex
    def toPythonIndex (self,i):
        '''Convert a tk inde iter to a Python index as needed.'''

        w =self
        if i is None:
            g.trace('can not happen: i is None')
            return 0
        elif type(i) in (type('a'),type(u'a')):
            s = '' ### s = gtk.Text.get(w,'1.0','end') # end-1c does not work.
            i = '1.0' ### i = gtk.Text.index(w,i) # Convert to row/column form.
            row,col = i.split('.')
            row,col = int(row),int(col)
            row -= 1
            i = g.convertRowColToPythonIndex(s,row,col)
            #g.es_print(i)
        return i
    #@-node:ekr.20080112145409.278:w.toPythonIndex
    #@+node:ekr.20080112145409.279:w.rowColToGuiIndex
    # This method is called only from the colorizer.
    # It provides a huge speedup over naive code.

    def rowColToGuiIndex (self,s,row,col):

        return '%s.%s' % (row+1,col)
    #@nonl
    #@-node:ekr.20080112145409.279:w.rowColToGuiIndex
    #@-node:ekr.20080112145409.276:Index conversion (gtkTextWidget)
    #@+node:ekr.20080112145409.280:getName (gtkText)
    def getName (self):

        w = self
        return hasattr(w,'_name') and w._name or repr(w)
    #@nonl
    #@-node:ekr.20080112145409.280:getName (gtkText)
    #@+node:ekr.20080112145409.281:_setSelectionRange
    if 0:
        def _setSelectionRange (self,i,j,insert=None):

            w = self.widget

            i,j = w.toGuiIndex(i),w.toGuiIndex(j)

            # g.trace('i,j,insert',repr(i),repr(j),repr(insert),g.callers())

            # g.trace('i,j,insert',i,j,repr(insert))
            if w.compare(w,i, ">", j): i,j = j,i
            w.tag_remove(w,"sel","1.0",i)
            w.tag_add(w,"sel",i,j)
            w.tag_remove(w,"sel",j,"end")

            if insert is not None:
                w.setInsertPoint(insert)
    #@-node:ekr.20080112145409.281:_setSelectionRange
    #@+node:ekr.20080112145409.282:Wrapper methods (gtkTextWidget)
    #@+node:ekr.20080112145409.283:after_idle (new)
    def after_idle(self,*args,**keys):

        pass
    #@-node:ekr.20080112145409.283:after_idle (new)
    #@+node:ekr.20080112145409.284:bind (new)
    def bind (self,*args,**keys):

        pass
    #@-node:ekr.20080112145409.284:bind (new)
    #@+node:ekr.20080112145409.285:delete
    def delete(self,i,j=None):
        """Delete chars between i and j or single char at i if j is None."""

        b = self.textBuffer

        i = self.toGtkIter(i)

        if j is None:
            j = i + 1
        else:
            j = self.toGtkIter(j)

        self.textBuffer.delete(i, j)

    #@-node:ekr.20080112145409.285:delete
    #@+node:ekr.20080112145409.286:flashCharacter
    def flashCharacter(self,i,bg='white',fg='red',flashes=3,delay=75): # gtkTextWidget.

        w = self

        # def addFlashCallback(w,count,index):
            # # g.trace(count,index)
            # i,j = w.toGuiIndex(index),w.toGuiIndex(index+1)
            # gtk.Text.tag_add(w,'flash',i,j)
            # gtk.Text.after(w,delay,removeFlashCallback,w,count-1,index)

        # def removeFlashCallback(w,count,index):
            # # g.trace(count,index)
            # gtk.Text.tag_remove(w,'flash','1.0','end')
            # if count > 0:
                # gtk.Text.after(w,delay,addFlashCallback,w,count,index)

        # try:
            # gtk.Text.tag_configure(w,'flash',foreground=fg,background=bg)
            # addFlashCallback(w,flashes,i)
        # except Exception:
            # pass ; g.es_exception()
    #@nonl
    #@-node:ekr.20080112145409.286:flashCharacter
    #@+node:ekr.20080112145409.287:get
    def get(self,i,j=None):
        """Get a range of text from i to j or just the char at i if j is None."""

        buf = self.textBuffer

        i = self.toGtkIter(i)


        if j is None:
            j = i + 1
        else:
            j = self.toGtkIter(j)

        return buf.get_text(i, j)
    #@-node:ekr.20080112145409.287:get
    #@+node:ekr.20080112145409.288:getAllText
    def getAllText (self):
        """Return all the text from the currently selected text buffer."""

        buf = self.textBuffer

        return buf.get_text(buf.get_start_iter(), buf.get_end_iter())


    #@-node:ekr.20080112145409.288:getAllText
    #@+node:ekr.20080112145409.289:getInsertPoint
    def getInsertPoint(self): # gtkTextWidget.

        buf = self.textBuffer

        return buf.get_iter_at_mark(buf.get_insert()).get_offset()
    #@-node:ekr.20080112145409.289:getInsertPoint
    #@+node:ekr.20080112145409.290:getSelectedText
    def getSelectedText (self): # gtkTextWidget.

        buf = self.textBuffer

        if not buf.get_has_selection():
            return u''

        i, j = buf.get_selection_bounds()

        return buf.get_text(i, j)
    #@nonl
    #@-node:ekr.20080112145409.290:getSelectedText
    #@+node:ekr.20080112145409.291:getSelectionRange
    def getSelectionRange (self,sort=True): # gtkTextWidget.

        """Return a tuple representing the selected range.

        Return a tuple giving the insertion point if no range of text is selected."""


        buf = self.textBuffer

        if buf.get_has_selection():

            i, j = buf.get_selection_bounds()
            i, j = i.get_offset(), j.get_offset()

        else:
            i = j = self.getInsertionPoint()

        if sort and i > j:
            i,j = j,i

        return self.toGuiIndex(i), self.toGuiIndex(j)
    #@-node:ekr.20080112145409.291:getSelectionRange
    #@+node:ekr.20080112145409.292:getYScrollPosition
    def getYScrollPosition (self):

         w = self
         return 0 ### return w.yview()
    #@-node:ekr.20080112145409.292:getYScrollPosition
    #@+node:ekr.20080112145409.293:getWidth
    def getWidth (self):

        '''Return the width of the widget.
        This is only called for headline widgets,
        and gui's may choose not to do anything here.'''

        w = self
        return 0 ### return w.cget('width')
    #@-node:ekr.20080112145409.293:getWidth
    #@+node:ekr.20080112145409.294:hasSelection
    def hasSelection (self):

        return self.textBuffer.get_has_selection()
    #@-node:ekr.20080112145409.294:hasSelection
    #@+node:ekr.20080112145409.295:insert

    def insert(self,i,s):
        """Insert a string s at position i."""

        i = self.toGtkIter(i)

        self.textBuffer.insert(i, s)

    #@-node:ekr.20080112145409.295:insert
    #@+node:ekr.20080112145409.296:indexIsVisible
    def indexIsVisible (self,i):

        w = self

        return True ### return w.dlineinfo(i)
    #@nonl
    #@-node:ekr.20080112145409.296:indexIsVisible
    #@+node:ekr.20080112145409.297:mark_set NO LONGER USED
    # def mark_set(self,markName,i):

        # w = self
        # i = w.toGuiIndex(i)
        # gtk.Text.mark_set(w,markName,i)
    #@-node:ekr.20080112145409.297:mark_set NO LONGER USED
    #@+node:ekr.20080112145409.298:replace
    def replace (self,i,j,s): # gtkTextWidget

        """ replace text between i an j with string s.

        i and j could be in 'r.c' form

        """
        w = self
        buf = w.textBuffer

        i = w.toGtkIter(i)

        if j is None:
            j = i + 1
        else:
            j = w.toGtkIter(j)

        buf.delete(i, j)
        buf.insert(i, s)


    #@-node:ekr.20080112145409.298:replace
    #@+node:ekr.20080112145409.299:see
    def see (self,i): # gtkTextWidget.
        """Scrolls the textview the minimum distance to place the position i onscreen."""

        w = self

        i = self.toGtkIter(i)

        w.textBuffer.move_mark(w.iMark, i)
        w.textView.scroll_mark_onscreen(w.iMark)
    #@-node:ekr.20080112145409.299:see
    #@+node:ekr.20080112145409.300:seeInsertPoint
    def seeInsertPoint (self): # gtkTextWidget.

        buf = self.textBuffer

        self.textView.scroll_mark_onscreen(buf.get_insert())
    #@-node:ekr.20080112145409.300:seeInsertPoint
    #@+node:ekr.20080112145409.301:selectAllText
    def selectAllText (self,insert=None): # gtkTextWidget

        '''Select all text of the widget, *not* including the extra newline.

        ??? what to do about insert, i don't know how to set the selection range
            without setting the insertion point.
        '''

        w = self

        buf = w.textBuffer

        start = buf.get_start_iter()
        end = buf.get_end_iter()

        end.backward_char()

        buf.select_range(start, end)


    #@-node:ekr.20080112145409.301:selectAllText
    #@+node:ekr.20080112145409.302:setAllText
    def setAllText (self,s): # gtkTextWidget

        self.textBuffer.set_text(s)

        # state = gtk.Text.cget(w,"state")
        # gtk.Text.configure(w,state="normal")

        # gtk.Text.delete(w,'1.0','end')
        # gtk.Text.insert(w,'1.0',s)

        # gtk.Text.configure(w,state=state)
    #@-node:ekr.20080112145409.302:setAllText
    #@+node:ekr.20080112145409.303:setBackgroundColor
    def setBackgroundColor (self,color):

        w = self
        w.configure(background=color)
    #@nonl
    #@-node:ekr.20080112145409.303:setBackgroundColor
    #@+node:ekr.20080112145409.304:setInsertPoint
    def setInsertPoint (self,i): # gtkTextWidget.
        """Set the insertion point.

        i is a python index.

        """
        w = self

        i = w.toGtkIter(i)
        w.textBuffer.place_cursor(i)

        # g.trace(i,g.callers())
        ### gtk.Text.mark_set(w,'insert',i)
    #@-node:ekr.20080112145409.304:setInsertPoint
    #@+node:ekr.20080112145409.305:setSelectionRange
    def setSelectionRange (self,i,j,insert=None): # gtkTextWidget

        """Select a range in the text buffer.

        i, j are pyton indexes

        ??? This uses the insertion point which can not be set seperatly.

        """
        w = self

        i = w.toGtkIter(i)
        j = w.toGtkIter(j)

        w.textBuffer.select_range(i, j)

        # g.trace('i,j,insert',repr(i),repr(j),repr(insert),g.callers())

        # g.trace('i,j,insert',i,j,repr(insert))

        ###
        # if gtk.Text.compare(w,i, ">", j): i,j = j,i
        # gtk.Text.tag_remove(w,"sel","1.0",i)
        # gtk.Text.tag_add(w,"sel",i,j)
        # gtk.Text.tag_remove(w,"sel",j,"end")

        # if insert is not None:
            # w.setInsertPoint(insert)
    #@-node:ekr.20080112145409.305:setSelectionRange
    #@+node:ekr.20080112145409.306:setYScrollPosition
    def setYScrollPosition (self,i):

         w = self
         w.yview('moveto',i)
    #@nonl
    #@-node:ekr.20080112145409.306:setYScrollPosition
    #@+node:ekr.20080112145409.307:setWidth
    def setWidth (self,width):

        '''Set the width of the widget.
        This is only called for headline widgets,
        and gui's may choose not to do anything here.'''

        w = self
        #w.configure(width=width)
    #@-node:ekr.20080112145409.307:setWidth
    #@+node:ekr.20080112145409.308:tag_add
    # The signature is slightly different than the gtk.Text.insert method.

    def tag_add(self,tagName,i,j=None,*args):

        w = self
        i = w.toGuiIndex(i)

        # if j is None:
            # gtk.Text.tag_add(w,tagName,i,*args)
        # else:
            # j = w.toGuiIndex(j)
            # gtk.Text.tag_add(w,tagName,i,j,*args)

    #@-node:ekr.20080112145409.308:tag_add
    #@+node:ekr.20080112145409.309:tag_configure (NEW)
    def tag_configure (self,*args,**keys):

        pass

    tag_config = tag_configure
    #@-node:ekr.20080112145409.309:tag_configure (NEW)
    #@+node:ekr.20080112145409.310:tag_ranges
    def tag_ranges(self,tagName):

        w = self
        aList = [] ### aList = gtk.Text.tag_ranges(w,tagName)
        aList = [w.toPythonIndex(z) for z in aList]
        return tuple(aList)
    #@-node:ekr.20080112145409.310:tag_ranges
    #@+node:ekr.20080112145409.311:tag_remove
    def tag_remove (self,tagName,i,j=None,*args):

        w = self
        i = w.toGuiIndex(i)

        if j is None:
            pass ### gtk.Text.tag_remove(w,tagName,i,*args)
        else:
            j = w.toGuiIndex(j)
            ### gtk.Text.tag_remove(w,tagName,i,j,*args)


    #@-node:ekr.20080112145409.311:tag_remove
    #@+node:ekr.20080112145409.312:w.deleteTextSelection
    def deleteTextSelection (self): # gtkTextWidget


        self.textBuffer.delete_selection(False, False)


        # sel = gtk.Text.tag_ranges(w,"sel")
        # if len(sel) == 2:
            # start,end = sel
            # if gtk.Text.compare(w,start,"!=",end):
                # gtk.Text.delete(w,start,end)
    #@-node:ekr.20080112145409.312:w.deleteTextSelection
    #@+node:ekr.20080112145409.313:xyToGui/PythonIndex
    def xyToGuiIndex (self,x,y): # gtkTextWidget

        w = self
        return 0 ### return gtk.Text.index(w,"@%d,%d" % (x,y))

    def xyToPythonIndex(self,x,y): # gtkTextWidget

        w = self
        i = 0 ### i = gtk.Text.index(w,"@%d,%d" % (x,y))
        i = w.toPythonIndex(i)
        return i
    #@-node:ekr.20080112145409.313:xyToGui/PythonIndex
    #@-node:ekr.20080112145409.282:Wrapper methods (gtkTextWidget)
    #@-others
#@nonl
#@-node:ekr.20080112145409.273:class leoGtkTextWidget
#@-node:bob.20080119110204:== Leo Text Widget (gtk) ==
#@-others
#@-node:ekr.20080112145409.53:@thin leoGtkFrame.py
#@-leo
