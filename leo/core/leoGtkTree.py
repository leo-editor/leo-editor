# -*- coding: utf-8 -*-
#@+leo-ver=4-thin
#@+node:ekr.20080112170946:@thin leoGtkTree.py
#@@first

'''Leo's Gtk Tree module.'''

#@@language python
#@@tabwidth -4
#@@pagewidth 80

#@<< imports >>
#@+node:ekr.20080112170946.1:<< imports >>
import leo.core.leoGlobals as g

# import leo.core.leoChapters as leoChapters
import leo.core.leoColor as leoColor
# import leo.core.leoKeys as leoKeys
#import leo.core.leoMenu as leoMenu
# import leo.core.leoNodes as leoNodes

import leo.core.leoFrame as leoFrame

import leo.core.leoGtkMenu as leoGtkMenu

import gtk
import gobject
import pango

import os
import string
import sys
#@-node:ekr.20080112170946.1:<< imports >>
#@nl

#@+others
#@+node:bob.20080117122525:class leoGtkTree (leoFrame.leoTree)
class leoGtkTree (leoFrame.leoTree):
    """Leo gtk tree class."""

    #@    @+others
    #@+node:ekr.20080112145409.319: Birth... (gtkTree)
    #@+node:ekr.20080112145409.320:__init__ (gtkTree)
    def __init__(self,c):

        #g.trace('>>', 'gtkTree', c)
        g.trace(g.callers())

        # Init the base class.
        leoFrame.leoTree.__init__(self,c.frame)

        #@    << set ivars >>
        #@+node:bob.20080117141402:<< set ivars >>



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
        self.use_chapters   = False and c.config.getBool('use_chapters') ###



        #@<< define drawing constants >>
        #@+node:ekr.20080112145409.321:<< define drawing constants >>
        self.box_padding = 5 # extra padding between box and icon
        self.box_width = 9 + self.box_padding
        self.icon_width = 20
        self.text_indent = 4 # extra padding between icon and tex

        self.hline_y = 7 # Vertical offset of horizontal line ??
        self.root_left = 7 + self.box_width
        self.root_top = 2

        self.default_line_height = 17 + 2 # default if can't set line_height from font.
        self.line_height = self.default_line_height
        #@-node:ekr.20080112145409.321:<< define drawing constants >>
        #@nl
        #@<< old ivars >>
        #@+node:ekr.20080112145409.322:<< old ivars >>
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
        #@-node:ekr.20080112145409.322:<< old ivars >>
        #@nl
        #@<< inject callbacks into the position class >>
        #@+node:ekr.20080112145409.323:<< inject callbacks into the position class >>
        # The new code injects 3 callbacks for the colorizer.

        if 0 and not leoGtkTree.callbacksInjected: # Class var. ###
            leoGtkTree.callbacksInjected = True
            self.injectCallbacks()
        #@-node:ekr.20080112145409.323:<< inject callbacks into the position class >>
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
            # Pre 4.4b2: Keys are vnodes, values are gtk.Text widgets.
            #     4.4b2: Keys are p.key(), values are gtk.Text widgets.
        self.visibleUserIcons = []

        # Lists of free, hidden widgets...
        self.freeBoxes = []
        self.freeClickBoxes = []
        self.freeIcons = []
        self.freeLines = []
        self.freeText = [] # New in 4.4b2: a list of free gtk.Text widgets

        self.freeUserIcons = []


        #@-node:bob.20080117141402:<< set ivars >>
        #@nl

        self.canvas = OutlineCanvasPanel(self, 'canvas')
    #@+node:bob.20080118160821:NewHeadline
    #@-node:bob.20080118160821:NewHeadline
    #@-node:ekr.20080112145409.320:__init__ (gtkTree)
    #@+node:ekr.20080112145409.324:gtkTtree.setBindings
    def setBindings (self):

        '''Create binding table for all canvas events.

        ??? I am not sure how best to emulate tk event system.
            I would be a happier using hitTest to determine where and
            what was it then hard coding the action sequence, that way
            we would know exactly what was happening and when.
        '''

        tree = self ; k = self.c.k ; canvas = self.canvas

        g.trace('leoGtkTree', tree, self.c, canvas)


        if 1:

            # g.trace('self',self,'canvas',canvas)

            #@        << create gtk mouse action table >>
            #@+node:bob.20080120095731:<< create gtk mouse action table  >>
            self.gtkMouseActionTable = {
                'clickBox': {
                    '<Button-1>': self.onClickBoxClick,
                },

                'iconBox': {
                    '<Button-1>': self.onIconBoxClick,
                    '<Double-1>': self.onIconBoxDoubleClick,
                    '<Button-3>': self.onIconBoxRightClick,
                    '<Double-3>': self.onIconBoxRightClick,
                    '<Any-ButtonRelease-1>': self.onEndDrag,
                },

                # these to be set later.
                'headline': {
                    '<Button-1>': None,
                    '<Double-1>': None,
                    '<Button-3>': None,
                    '<Double-3>': None,
                } 
            }
            #@-node:bob.20080120095731:<< create gtk mouse action table  >>
            #@nl
            #@        << add actions for headline mouse events >>
            #@+node:ekr.20080112145409.325:<< add actions for headline mouse events >>
            #self.bindingWidget = w = g.app.gui.plainTextWidget(
            #    self.canvas,name='bindingWidget')

            # c.bind(w,'<Key>',k.masterKeyHandler)

            table = (
                ('<Button-1>',  k.masterClickHandler,          tree.onHeadlineClick),
                ('<Button-3>',  k.masterClick3Handler,         tree.onHeadlineRightClick),
                ('<Double-1>',  k.masterDoubleClickHandler,    tree.onHeadlineClick),
                ('<Double-3>',  k.masterDoubleClick3Handler,   tree.onHeadlineRightClick),
            )

            actions = self.gtkMouseActionTable

            for a,handler,func in table:

                def treeBindingCallback(event,handler=handler,func=func):
                    g.trace('func',func, event.widget)
                    return handler(event,func)

                actions['headline'][a] = treeBindingCallback

            ### self.textBindings = w.bindtags()
            #@-node:ekr.20080112145409.325:<< add actions for headline mouse events >>
            #@nl

            #k.completeAllBindingsForWidget(canvas)

            #k.completeAllBindingsForWidget(self.bindingWidget)

    #@-node:ekr.20080112145409.324:gtkTtree.setBindings
    #@+node:ekr.20080112145409.326:gtkTree.setCanvasBindings
    def setCanvasBindings (self, canvas):

        NOTUSED()

        """Set binding for this canvas.

        In gtk this includes:

            setting self.mouseAtionTable to a dictionary of dictionaries.

            The top level dictionary keys are target names such as 'clickBox'
                the values are dictionareis whose keys represent event types
                and whose values are functions to call to handle that target
                event combination.

            e.g
                self.gtkMouseActionTable['clickBox']['<Button-1>']

        """

        k = self.c.k


        self.gtkMouseActionTable = {
            'plusBox': {
                '<Button-1>': self.onClickBoxClick,
            },

            'iconBox': {
                '<Button-1>': self.onIconBoxClick,
                '<Double-1>': self.onIconBoxDoubleClick,
                '<Button-3>': self.onIconBoxRightClick,
                '<Double-3>': self.onIconBoxRightClick,
                '<Any-ButtonRelease-1>': self.self.onEndDrag,
            }, 
        }


        if 0: ###

            c.bind(canvas,'<Key>',k.masterKeyHandler)
            c.bind(canvas,'<Button-1>',self.onTreeClick)

            #@        << make bindings for tagged items on the canvas >>
            #@+node:ekr.20080112145409.327:<< make bindings for tagged items on the canvas >>
            where = g.choose(self.expanded_click_area,'clickBox','plusBox')

            ###
            # table = (
                # (where,    '<Button-1>',self.onClickBoxClick),
                # ('iconBox','<Button-1>',self.onIconBoxClick),
                # ('iconBox','<Double-1>',self.onIconBoxDoubleClick),
                # ('iconBox','<Button-3>',self.onIconBoxRightClick),
                # ('iconBox','<Double-3>',self.onIconBoxRightClick),
                # ('iconBox','<B1-Motion>',self.onDrag),
                # ('iconBox','<Any-ButtonRelease-1>',self.onEndDrag),
            # )
            # for tag,event,callback in table:
                # c.tag_bind(canvas,tag,event,callback)
            #@-node:ekr.20080112145409.327:<< make bindings for tagged items on the canvas >>
            #@nl
            #@        << create baloon bindings for tagged items on the canvas >>
            #@+node:ekr.20080112145409.328:<< create baloon bindings for tagged items on the canvas >>
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
            #@-node:ekr.20080112145409.328:<< create baloon bindings for tagged items on the canvas >>
            #@nl
    #@-node:ekr.20080112145409.326:gtkTree.setCanvasBindings
    #@-node:ekr.20080112145409.319: Birth... (gtkTree)
    #@+node:bob.20080118170856:onOutlineCanvasEvent
    def onOutlineCanvasEvent(self, target, eventType, event, p):
        """Handle events recieved from the outline canvas widget.

        ??? We need a clear declaration of the event sequence for
            mouse events on the canvas

        At the moment there are three levels,

            headline item
            headline
            canvas

            events on a headline item will:
                invoke specific events handlers bound to that item
                invoke more general event handlers bound to the headline
                invoke events bound to the canvas

            events on a headline will:
                invoke more general event handlers bound to the headline
                invoke events bound to the canvas

            events on a canvas will:
                invoke events bound on the canvas

            if an event handler returns true at any stage, all event handling will halt.

        """

        try:
            method = self.gtkMouseActionTable[target][eventType]
        except KeyError:
            method = None
            g.pr('no binding', target, eventType)

        result = False
        if method:
            result = method(event)

        if not result and target not in ('canvas', 'headline'):
            target = 'headline'
            result =  self.onOutlineCanvasEvent(target, eventType, event, p)           

        self.canvas.update()
        return result


    #@-node:bob.20080118170856:onOutlineCanvasEvent
    #@+node:ekr.20080112145409.329:Allocation...(gtkTree)
    if 0:
        #TOEKR  can these be deleted?
        #@    @+others
        #@+node:ekr.20080112145409.330:newBox
        def newBox (self,p,x,y,image):

            canvas = self.canvas ; tag = "plusBox"

            if self.freeBoxes:
                theId = self.freeBoxes.pop(0)
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
        #@-node:ekr.20080112145409.330:newBox
        #@+node:ekr.20080112145409.331:newClickBox
        def newClickBox (self,p,x1,y1,x2,y2):

            canvas = self.canvas ; defaultColor = ""
            tag = g.choose(p.hasChildren(),'clickBox','selectBox')

            if self.freeClickBoxes:
                theId = self.freeClickBoxes.pop(0)
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
        #@-node:ekr.20080112145409.331:newClickBox
        #@+node:ekr.20080112145409.332:newIcon
        def newIcon (self,p,x,y,image):

            canvas = self.canvas ; tag = "iconBox"

            if self.freeIcons:
                theId = self.freeIcons.pop(0)
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
        #@-node:ekr.20080112145409.332:newIcon
        #@+node:ekr.20080112145409.333:newLine
        def newLine (self,p,x1,y1,x2,y2):

            canvas = self.canvas

            if self.freeLines:
                theId = self.freeLines.pop(0)
                canvas.coords(theId,x1,y1,x2,y2)
            else:
                theId = canvas.create_line(x1,y1,x2,y2,tag="lines",fill="gray50") # stipple="gray25")
                if self.trace_alloc: g.trace("%3d %s" % (theId,p and p.headString()),align=-20)

            if p:
                self.ids[theId] = p

            if theId not in self.visibleLines:
                self.visibleLines.append(theId)

            return theId
        #@-node:ekr.20080112145409.333:newLine
        #@+node:ekr.20080112145409.334:newText (gtkTree) and helper
        def newText (self,p,x,y):

            canvas = self.canvas ; tag = "textBox"
            c = self.c ;  k = c.k
            if self.freeText:
                w,theId = self.freeText.pop()
                canvas.coords(theId,x,y) # Make the window visible again.
                    # theId is the id of the *window* not the text.
            else:
                # Tags are not valid in gtk.Text widgets.
                self.textNumber += 1
                w = g.app.gui.plainTextWidget(
                    canvas,name='head-%d' % self.textNumber,
                    state="normal",font=self.font,bd=0,relief="flat",height=1)
                ### w.bindtags(self.textBindings) # Set the bindings for this widget.

                if 0: # Crashes on XP.
                    #@            << patch by Maciej Kalisiak to handle scroll-wheel events >>
                    #@+node:ekr.20080112145409.335:<< patch by Maciej Kalisiak  to handle scroll-wheel events >>
                    def PropagateButton4(e):
                        canvas.event_generate("<Button-4>")
                        return "break"

                    def PropagateButton5(e):
                        canvas.event_generate("<Button-5>")
                        return "break"

                    def PropagateMouseWheel(e):
                        canvas.event_generate("<MouseWheel>")
                        return "break"
                    #@-node:ekr.20080112145409.335:<< patch by Maciej Kalisiak  to handle scroll-wheel events >>
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
        #@+node:ekr.20080112145409.336:tree.setHeadlineText
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
        #@-node:ekr.20080112145409.336:tree.setHeadlineText
        #@-node:ekr.20080112145409.334:newText (gtkTree) and helper
        #@+node:ekr.20080112145409.337:recycleWidgets
        def recycleWidgets (self):

            canvas = self.canvas

            for theId in self.visibleBoxes:
                if theId not in self.freeBoxes:
                    self.freeBoxes.append(theId)
                canvas.coords(theId,-100,-100)
            self.visibleBoxes = []

            for theId in self.visibleClickBoxes:
                if theId not in self.freeClickBoxes:
                    self.freeClickBoxes.append(theId)
                canvas.coords(theId,-100,-100,-100,-100)
            self.visibleClickBoxes = []

            for theId in self.visibleIcons:
                if theId not in self.freeIcons:
                    self.freeIcons.append(theId)
                canvas.coords(theId,-100,-100)
            self.visibleIcons = []

            for theId in self.visibleLines:
                if theId not in self.freeLines:
                    self.freeLines.append(theId)
                canvas.coords(theId,-100,-100,-100,-100)
            self.visibleLines = []

            aList = self.visibleText.values()
            for data in aList:
                w,theId = data
                # assert theId == w.leo_window_id
                canvas.coords(theId,-100,-100)
                w.leo_position = None # Allow the position to be freed.
                if data not in self.freeText:
                    self.freeText.append(data)
            self.visibleText = {}

            for theId in self.visibleUserIcons:
                # The present code does not recycle user Icons.
                self.canvas.delete(theId)
            self.visibleUserIcons = []
        #@-node:ekr.20080112145409.337:recycleWidgets
        #@+node:ekr.20080112145409.338:destroyWidgets
        def destroyWidgets (self):

            self.ids = {}

            self.visibleBoxes = []
            self.visibleClickBoxes = []
            self.visibleIcons = []
            self.visibleLines = []
            self.visibleUserIcons = []

            self.visibleText = {}

            self.freeText = []
            self.freeBoxes = []
            self.freeClickBoxes = []
            self.freeIcons = []
            self.freeLines = []

            self.canvas.delete("all")
        #@-node:ekr.20080112145409.338:destroyWidgets
        #@+node:ekr.20080112145409.339:showStats
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
        #@-node:ekr.20080112145409.339:showStats
        #@-others
    #@nonl
    #@-node:ekr.20080112145409.329:Allocation...(gtkTree)
    #@+node:ekr.20080112145409.340:Config & Measuring...
    #@+node:ekr.20080112145409.341:tree.getFont,setFont,setFontFromConfig
    def getFont (self):

        return self.font

    def setFont (self,font=None, fontName=None):

        # ESSENTIAL: retain a link to font.
        if fontName:
            self.fontName = fontName
            self.font = gtkFont.Font(font=fontName)
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
    #@-node:ekr.20080112145409.341:tree.getFont,setFont,setFontFromConfig
    #@+node:ekr.20080112145409.342:headWidth & widthInPixels
    def headWidth(self,p=None,s=''):

        """Returns the proper width of the entry widget for the headline."""

        if p: s = p.headString()

        return self.font.measure(s)/self.font.measure('0')+1


    def widthInPixels(self,s):

        s = g.toEncodedString(s,g.app.tkEncoding)

        return self.font.measure(s)
    #@-node:ekr.20080112145409.342:headWidth & widthInPixels
    #@+node:ekr.20080112145409.343:setLineHeight
    def setLineHeight (self,font):

        pass ###

        # try:
            # metrics = font.metrics()
            # linespace = metrics ["linespace"]
            # self.line_height = linespace + 5 # Same as before for the default font on Windows.
            # # g.pr(metrics)
        # except:
            # self.line_height = self.default_line_height
            # g.es("exception setting outline line height")
            # g.es_exception()
    #@-node:ekr.20080112145409.343:setLineHeight
    #@-node:ekr.20080112145409.340:Config & Measuring...
    #@+node:ekr.20080112145409.344:Debugging...
    if 0:
        #@    @+others
        #@+node:ekr.20080112145409.345:textAddr
        def textAddr(self,w):

            """Return the address part of repr(gtk.Text)."""

            return repr(w)[-9:-1].lower()
        #@-node:ekr.20080112145409.345:textAddr
        #@+node:ekr.20080112145409.346:traceIds (Not used)
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
        #@-node:ekr.20080112145409.346:traceIds (Not used)
        #@-others
        #TOEKR delete these?
    #@nonl
    #@-node:ekr.20080112145409.344:Debugging...
    #@+node:ekr.20080112145409.347:Drawing... (gtkTree)
    #@+node:ekr.20080112145409.348:tree.begin/endUpdate
    def beginUpdate (self):

        self.updateCount += 1
        # g.trace('tree',id(self),self.updateCount,g.callers())

    def endUpdate (self,flag,scroll=False):

        self.updateCount -= 1
        # g.trace(self.updateCount,'scroll',scroll,g.callers())

        if self.updateCount <= 0:
            if flag:
                self.redraw_now(scroll=scroll)
            if self.updateCount < 0:
                g.trace("Can't happen: negative updateCount",g.callers())
    #@-node:ekr.20080112145409.348:tree.begin/endUpdate
    #@+node:ekr.20080112145409.349:tree.redraw_now & helper
    # New in 4.4b2: suppress scrolling by default.

    def redraw_now (self,scroll=False,forceDraw=False):

        '''Redraw immediately: used by Find so a redraw doesn't mess up selections in headlines.'''

        if g.app.quitting or self.frame not in g.app.windowList:
            return
        if self.drag_p and not forceDraw:
            return

        c = self.c

        # g.trace(g.callers())

        if not g.app.unitTesting:
            if self.gc_before_redraw:
                g.collectGarbage()
            if g.app.trace_gc_verbose:
                if (self.redrawCount % 5) == 0:
                    g.printGcSummary()
            if self.trace_redraw or self.trace_alloc:
                # g.trace(self.redrawCount,g.callers())
                # g.trace(c.rootPosition().headString(),'canvas:',id(self.canvas),g.callers())
                if self.trace_stats:
                    g.print_stats()
                    g.clear_stats()

        # New in 4.4b2: Call endEditLabel, but suppress the redraw.
        self.beginUpdate()
        try:
            self.endEditLabel()
        finally:
            self.endUpdate(False)

        # Do the actual redraw.
        self.expandAllAncestors(c.currentPosition())
        if self.idle_redraw:
            def idleRedrawCallback(event=None,self=self,scroll=scroll):
                self.redrawHelper(scroll=scroll)
            ### self.canvas.after_idle(idleRedrawCallback)
        else:
            self.redrawHelper(scroll=scroll)
        if g.app.unitTesting:
            self.canvas.update_idletasks() # Important for unit tests.
        c.masterFocusHandler()

    redraw = redraw_now # Compatibility
    #@+node:ekr.20080112145409.350:redrawHelper
    def redrawHelper (self,scroll=True,forceDraw=False):

        c = self.c

        if self.canvas:
            self.canvas.update()
        else:
            g.trace('No Canvas')

        ###

        # oldcursor = self.canvas['cursor']
        # self.canvas['cursor'] = "watch"

        # if not g.doHook("redraw-entire-outline",c=c):
            # c.setTopVnode(None)
            # self.setVisibleAreaToFullCanvas()
            # self.drawTopTree()
            # # Set up the scroll region after the tree has been redrawn.
            # bbox = self.canvas.bbox('all')
            # # g.trace('canvas',self.canvas,'bbox',bbox)
            # if bbox is None:
                # x0,y0,x1,y1 = 0,0,100,100
            # else:
                # x0, y0, x1, y1 = bbox
            # self.canvas.configure(scrollregion=(0, 0, x1, y1))
            # if scroll:
                # self.canvas.update_idletasks() # Essential.
                # self.scrollTo()

        g.doHook("after-redraw-outline",c=c)

        ### self.canvas['cursor'] = oldcursor
    #@-node:ekr.20080112145409.350:redrawHelper
    #@-node:ekr.20080112145409.349:tree.redraw_now & helper
    #@+node:ekr.20080112145409.351:idle_second_redraw
    def idle_second_redraw (self):

        c = self.c

        # Erase and redraw the entire tree the SECOND time.
        # This ensures that all visible nodes are allocated.
        c.setTopVnode(None)
        args = self.canvas.yview()
        self.setVisibleArea(args)

        if 0:
            self.deleteBindings()
            self.canvas.delete("all")

        self.drawTopTree()

        if self.trace:
            g.trace(self.redrawCount)
    #@-node:ekr.20080112145409.351:idle_second_redraw
    #@+node:ekr.20080112145409.352:drawX...
    ##
    #@nonl
    #@+node:ekr.20080112145409.353:drawBox
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
    #@-node:ekr.20080112145409.353:drawBox
    #@+node:ekr.20080112145409.354:drawClickBox
    def drawClickBox (self,p,y):

        h = self.line_height

        # Define a slighly larger rect to catch clicks.
        if self.expanded_click_area:
            self.newClickBox(p,0,y,1000,y+h-2)
    #@-node:ekr.20080112145409.354:drawClickBox
    #@+node:ekr.20080112145409.355:drawIcon
    def drawIcon(self,p,x=None,y=None):

        """Draws icon for position p at x,y, or at p.v.iconx,p.v.icony if x,y = None,None"""

        # if self.trace_gc: g.printNewObjects(tag='icon 1')

        c = self.c ; v = p.v
        #@    << compute x,y and iconVal >>
        #@+node:ekr.20080112145409.356:<< compute x,y and iconVal >>
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
        #@-node:ekr.20080112145409.356:<< compute x,y and iconVal >>
        #@nl
        v.iconVal = val

        if not g.doHook("draw-outline-icon",tree=self,c=c,p=p,v=p,x=x,y=y):

            # Get the image.
            imagename = "box%02d.GIF" % val
            image = self.getIconImage(imagename)
            self.newIcon(p,x,y+self.lineyoffset,image)

        return 0,self.icon_width # dummy icon height,width
    #@-node:ekr.20080112145409.355:drawIcon
    #@+node:ekr.20080112145409.357:drawLine
    def drawLine (self,p,x1,y1,x2,y2):

        theId = self.newLine(p,x1,y1,x2,y2)

        return theId
    #@-node:ekr.20080112145409.357:drawLine
    #@+node:ekr.20080112145409.358:drawNode & force_draw_node (good trace)
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
    #@+node:ekr.20080112145409.359:force_draw_node
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
    #@-node:ekr.20080112145409.359:force_draw_node
    #@-node:ekr.20080112145409.358:drawNode & force_draw_node (good trace)
    #@+node:ekr.20080112145409.360:drawText
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
    #@-node:ekr.20080112145409.360:drawText
    #@+node:ekr.20080112145409.361:drawUserIcons
    def drawUserIcons(self,p,where,x,y):

        """Draw any icons specified by p.v.t.unknownAttributes["icons"]."""

        h,w = 0,0 ; t = p.v.t

        if not hasattr(t,"unknownAttributes"):
            return h,w

        iconsList = t.unknownAttributes.get("icons")
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
    #@-node:ekr.20080112145409.361:drawUserIcons
    #@+node:ekr.20080112145409.362:drawUserIcon
    def drawUserIcon (self,p,where,x,y,w2,theDict):

        h,w = 0,0

        if where != theDict.get("where","beforeHeadline"):
            return h,w

        # if self.trace_gc: g.printNewObjects(tag='userIcon 1')

        # g.trace(where,x,y,theDict)

        #@    << set offsets and pads >>
        #@+node:ekr.20080112145409.363:<< set offsets and pads >>
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
        #@-node:ekr.20080112145409.363:<< set offsets and pads >>
        #@nl
        theType = theDict.get("type")
        if theType == "icon":
            if 0: # not ready yet.
                s = theDict.get("icon")
                #@            << draw the icon in string s >>
                #@+node:ekr.20080112145409.364:<< draw the icon in string s >>
                pass
                #@-node:ekr.20080112145409.364:<< draw the icon in string s >>
                #@nl
        elif theType == "file":
            theFile = theDict.get("file")
            #@        << draw the icon at file >>
            #@+node:ekr.20080112145409.365:<< draw the icon at file >>
            try:
                image = self.iconimages[theFile]
                # Get the image from the cache if possible.
            except KeyError:
                try:
                    fullname = g.os_path_join(g.app.loadDir,"..","Icons",theFile)
                    fullname = g.os_path_normpath(fullname)
                    image = gtk.PhotoImage(master=self.canvas,file=fullname)
                    self.iconimages[fullname] = image
                except:
                    #g.es("exception loading:",fullname)
                    #g.es_exception()
                    image = None

            if image:
                theId = self.canvas.create_image(
                    x+xoffset+w2,y+yoffset,
                    anchor="nw",image=image,tag="userIcon")
                self.ids[theId] = p
                # assert(theId not in self.visibleIcons)
                self.visibleUserIcons.append(theId)

                h = image.height() + yoffset + ypad
                w = image.width()  + xoffset + xpad
            #@-node:ekr.20080112145409.365:<< draw the icon at file >>
            #@nl
        elif theType == "url":
            ## url = theDict.get("url")
            #@        << draw the icon at url >>
            #@+node:ekr.20080112145409.366:<< draw the icon at url >>
            pass
            #@-node:ekr.20080112145409.366:<< draw the icon at url >>
            #@nl

        # Allow user to specify height, width explicitly.
        h = theDict.get("height",h)
        w = theDict.get("width",w)

        # if self.trace_gc: g.printNewObjects(tag='userIcon 2')

        return h,w
    #@-node:ekr.20080112145409.362:drawUserIcon
    #@+node:ekr.20080112145409.367:drawTopTree
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
        canvas.lift("textBox") # Not the gtk.Text widget: it should be low.
        canvas.lift("userIcon")
        canvas.lift("plusBox")
        canvas.lift("clickBox")
        canvas.lift("clickExpandBox")
        canvas.lift("iconBox") # Higest.

        self.redrawing = False
    #@-node:ekr.20080112145409.367:drawTopTree
    #@+node:ekr.20080112145409.368:drawTree
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
    #@-node:ekr.20080112145409.368:drawTree
    #@-node:ekr.20080112145409.352:drawX...
    #@+node:ekr.20080112145409.369:Helpers...
    #@+node:ekr.20080112145409.370:getIconImage
    def getIconImage (self, name):

        # Return the image from the cache if possible.
        if name in self.iconimages:
            return self.iconimages[name]

        # g.trace(name)

        try:
            fullname = g.os_path_join(g.app.loadDir,"..","Icons",name)
            fullname = g.os_path_normpath(fullname)
            image = gtk.PhotoImage(master=self.canvas,file=fullname)
            self.iconimages[name] = image
            return image
        except:
            g.es("exception loading:",fullname)
            g.es_exception()
            return None
    #@-node:ekr.20080112145409.370:getIconImage
    #@+node:ekr.20080112145409.371:inVisibleArea & inExpandedVisibleArea
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
    #@-node:ekr.20080112145409.371:inVisibleArea & inExpandedVisibleArea
    #@+node:ekr.20080112145409.372:numberOfVisibleNodes
    def numberOfVisibleNodes(self):

        c = self.c

        n = 0 ; p = self.c.rootPosition()
        while p:
            n += 1
            p.moveToVisNext(c)
        return n
    #@-node:ekr.20080112145409.372:numberOfVisibleNodes
    #@+node:ekr.20080112145409.373:scrollTo (gtkTree)
    def scrollTo(self,p=None):

        """Scrolls the canvas so that p is in view."""

        c = self.c ; frame = c.frame ; trace = True
        if not p or not c.positionExists(p):
            p = c.currentPosition()
        if not p or not c.positionExists(p):
            if trace: g.trace('current p does not exist',p)
            p = c.rootPosition()
        if not p or not c.positionExists(p):
            if trace: g.trace('no root position')
            return
        try:
            h1 = self.yoffset(p)
            if self.center_selected_tree_node: # New in Leo 4.4.3.
                #@            << compute frac0 >>
                #@+node:ekr.20080112145409.374:<< compute frac0 >>
                # frac0 attempt to put the 
                scrollRegion = self.canvas.cget('scrollregion')
                geom = self.canvas.winfo_geometry()

                if scrollRegion and geom:
                    scrollRegion = scrollRegion.split(' ')
                    # g.trace('scrollRegion',repr(scrollRegion))
                    htot = int(scrollRegion[3])
                    wh,junk,junk = geom.split('+')
                    junk,h = wh.split('x')
                    if h: wtot = int(h)
                    else: wtot = 500
                    # g.trace('geom',geom,'wtot',wtot)
                    if htot > 0.1:
                        frac0 = float(h1-wtot/2)/float(htot)
                        frac0 = max(min(frac0,1.0),0.0)
                    else:
                        frac0 = 0.0
                else:
                    frac0 = 0.0 ; htot = wtot = 0
                #@-node:ekr.20080112145409.374:<< compute frac0 >>
                #@nl
                delta = abs(self.prevMoveToFrac-frac0)
                # g.trace(delta)
                if delta > 0.0:
                    self.prevMoveToFrac = frac0
                    self.canvas.yview("moveto",frac0)
                    if trace: g.trace("frac0 %1.2f %3d %3d %3d" % (frac0,h1,htot,wtot))
            else:
                last = c.lastVisible()
                nextToLast = last.visBack(c)
                h2 = self.yoffset(last)
                #@            << compute approximate line height >>
                #@+node:ekr.20080112145409.375:<< compute approximate line height >>
                if nextToLast: # 2/2/03: compute approximate line height.
                    lineHeight = h2 - self.yoffset(nextToLast)
                else:
                    lineHeight = 20 # A reasonable default.
                #@-node:ekr.20080112145409.375:<< compute approximate line height >>
                #@nl
                #@            << Compute the fractions to scroll down/up >>
                #@+node:ekr.20080112145409.376:<< Compute the fractions to scroll down/up >>
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
                #@-node:ekr.20080112145409.376:<< Compute the fractions to scroll down/up >>
                #@nl
                if frac <= lo: # frac is for scrolling down.
                    if self.prevMoveToFrac != frac:
                        self.prevMoveToFrac = frac
                        self.canvas.yview("moveto",frac)
                        if trace: g.trace("frac  %1.2f %3d %3d %1.2f %1.2f" % (frac, h1,h2,lo,hi))
                elif frac2 + (hi - lo) >= hi: # frac2 is for scrolling up.
                    if self.prevMoveToFrac != frac2:
                        self.prevMoveToFrac = frac2
                        self.canvas.yview("moveto",frac2)
                        if trace: g.trace("frac2 1.2f %3d %3d %1.2f %1.2f" % (frac2,h1,h2,lo,hi))

            if self.allocateOnlyVisibleNodes:
                pass ### self.canvas.after_idle(self.idle_second_redraw)

            c.setTopVnode(p) # 1/30/04: remember a pseudo "top" node.

        except:
            g.es_exception()

    idle_scrollTo = scrollTo # For compatibility.
    #@nonl
    #@-node:ekr.20080112145409.373:scrollTo (gtkTree)
    #@+node:ekr.20080112145409.377:yoffset (gtkTree)
    #@+at 
    #@nonl
    # We can't just return icony because the tree hasn't been redrawn yet.
    # For the same reason we can't rely on any gtk canvas methods here.
    #@-at
    #@@c

    def yoffset(self,p1):
        # if not p1.isVisible(): g.pr("yoffset not visible:",p1)
        if not p1: return 0
        if c.hoistStack:
            bunch = c.hoistStack[-1]
            root = bunch.p.copy()
        else:
            root = self.c.rootPosition()
        if root:
            h,flag = self.yoffsetTree(root,p1)
            # flag can be False during initialization.
            # if not flag: g.pr("yoffset fails:",h,v1)
            return h
        else:
            return 0

    def yoffsetTree(self,p,p1):
        h = 0 ; trace = False
        if not self.c.positionExists(p):
            if trace: g.trace('does not exist',p.headString())
            return h,False # An extra precaution.
        p = p.copy()
        for p2 in p.self_and_siblings_iter():  # was p.siblings_iter
            g.pr("yoffsetTree:", p2)
            if p2 == p1:
                if trace: g.trace(p.headString(),p1.headString(),h)
                return h, True
            h += self.line_height
            if p2.isExpanded() and p2.hasChildren():
                child = p2.firstChild()
                h2, flag = self.yoffsetTree(child,p1)
                h += h2
                if flag:
                    if trace: g.trace(p.headString(),p1.headString(),h)
                    return h, True

        if trace: g.trace('not found',p.headString(),p1.headString())
        return h, False
    #@-node:ekr.20080112145409.377:yoffset (gtkTree)
    #@-node:ekr.20080112145409.369:Helpers...
    #@-node:ekr.20080112145409.347:Drawing... (gtkTree)
    #@+node:ekr.20080112145409.378:Event handlers (gtkTree)
    #@+node:ekr.20080112145409.379:Helpers
    #@+node:ekr.20080112145409.380:checkWidgetList
    def checkWidgetList (self,tag):

        return True # This will fail when the headline actually changes!

        for w in self.visibleText:

            p = w.leo_position
            if p:
                s = w.getAllText().strip()
                h = p.headString().strip()

                if h != s:
                    self.dumpWidgetList(tag)
                    return False
            else:
                self.dumpWidgetList(tag)
                return False

        return True
    #@-node:ekr.20080112145409.380:checkWidgetList
    #@+node:ekr.20080112145409.381:dumpWidgetList
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
    #@-node:ekr.20080112145409.381:dumpWidgetList
    #@+node:ekr.20080112145409.382:tree.edit_widget
    def edit_widget (self,p):

        """Returns the gtk.Edit widget for position p."""

        return self.findEditWidget(p)
    #@nonl
    #@-node:ekr.20080112145409.382:tree.edit_widget
    #@+node:ekr.20080112145409.383:eventToPosition
    def eventToPosition (self,event):

        p = event.p
        if p:
            return p.copy()



        # canvas = self.canvas
        # x,y = event.x,event.y
        # x = canvas.canvasx(x) 
        # y = canvas.canvasy(y)
        # if self.trace: g.trace(x,y)
        # item = canvas.find_overlapping(x,y,x,y)
        # if not item: return None

        # # Item may be a tuple, possibly empty.
        # try:    theId = item[0]
        # except: theId = item
        # if not theId: return None

        # p = self.ids.get(theId)

        # # A kludge: p will be None for vertical lines.
        # if not p:
            # item = canvas.find_overlapping(x+1,y,x+1,y)
            # try:    theId = item[0]
            # except: theId = item
            # if not theId:
                # g.es_print('oops:','eventToPosition','failed')
                # return None
            # p = self.ids.get(theId)
            # # g.trace("was vertical line",p)

        # if self.trace and self.verbose:
            # if p:
                # w = self.findEditWidget(p)
                # g.trace("%3d %3d %3d %d" % (theId,x,y,id(w)),p.headString())
            # else:
                # g.trace("%3d %3d %3d" % (theId,x,y),None)

        # # defensive programming: this copy is not needed.
        # if p: return p.copy() # Make _sure_ nobody changes this table!
        # else: return None
    #@-node:ekr.20080112145409.383:eventToPosition
    #@+node:ekr.20080112145409.384:findEditWidget
    def findEditWidget (self,p):

        """Return the gtk.Text item corresponding to p."""

        c = self.c

        if p and c:
            aTuple = self.visibleText.get(p.key())
            if aTuple:
                w,theId = aTuple
                # g.trace('%4d' % (theId),self.textAddr(w),p.headString())
                return w
            else:
                # g.trace('oops: not found',p)
                return None

        # g.trace(not found',p.headString())
        return None
    #@-node:ekr.20080112145409.384:findEditWidget
    #@+node:ekr.20080112145409.385:findVnodeWithIconId
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
    #@-node:ekr.20080112145409.385:findVnodeWithIconId
    #@-node:ekr.20080112145409.379:Helpers
    #@+node:ekr.20080112145409.386:Click Box...
    #@+node:ekr.20080112145409.387:onClickBoxClick
    def onClickBoxClick (self,event,p=None):
        """Respond to clicks on expand/contract button."""

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
    #@-node:ekr.20080112145409.387:onClickBoxClick
    #@-node:ekr.20080112145409.386:Click Box...
    #@+node:ekr.20080112145409.388:Dragging (gtkTree)
    #@+node:ekr.20080112145409.389:endDrag
    def endDrag (self,event):

        """The official helper of the onEndDrag event handler."""

        g.trace()
        return ###

        c = self.c ; p = self.drag_p
        c.setLog()
        canvas = self.canvas
        if not event: return

        #@    << set vdrag, childFlag >>
        #@+node:ekr.20080112145409.390:<< set vdrag, childFlag >>
        x,y = event.x,event.y
        canvas_x = canvas.canvasx(x)
        canvas_y = canvas.canvasy(y)

        theId = self.canvas.find_closest(canvas_x,canvas_y)
        # theId = self.canvas.find_overlapping(canvas_x,canvas_y,canvas_x,canvas_y)

        vdrag = self.findPositionWithIconId(theId)
        childFlag = vdrag and vdrag.hasChildren() and vdrag.isExpanded()
        #@-node:ekr.20080112145409.390:<< set vdrag, childFlag >>
        #@nl
        if self.allow_clone_drags:
            if not self.look_for_control_drag_on_mouse_down:
                self.controlDrag = c.frame.controlKeyIsDown

        redrawFlag = vdrag and vdrag.v.t != p.v.t
        if redrawFlag: # Disallow drag to joined node.
            #@        << drag p to vdrag >>
            #@+node:ekr.20080112145409.391:<< drag p to vdrag >>
            # g.trace("*** end drag   ***",theId,x,y,p.headString(),vdrag.headString())

            if self.controlDrag: # Clone p and move the clone.
                if childFlag:
                    c.dragCloneToNthChildOf(p,vdrag,0)
                else:
                    c.dragCloneAfter(p,vdrag)
            else: # Just drag p.
                if childFlag:
                    c.dragToNthChildOf(p,vdrag,0)
                else:
                    c.dragAfter(p,vdrag)
            #@-node:ekr.20080112145409.391:<< drag p to vdrag >>
            #@nl
        elif self.trace and self.verbose:
            g.trace("Cancel drag")

        # Reset the old cursor by brute force.
        self.canvas['cursor'] = "arrow"
        self.dragging = False
        self.drag_p = None
        # Must set self.drag_p = None first.
        if redrawFlag: c.redraw()
        c.recolor_now() # Dragging can affect coloring.
    #@-node:ekr.20080112145409.389:endDrag
    #@+node:ekr.20080112145409.392:startDrag
    # This precomputes numberOfVisibleNodes(), a significant optimization.
    # We also indicate where findPositionWithIconId() should start looking for tree id's.

    def startDrag (self,event,p=None):

        g.trace()
        return ###

        """The official helper of the onDrag event handler."""

        c = self.c ; canvas = self.canvas
        return ###

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
    #@-node:ekr.20080112145409.392:startDrag
    #@+node:ekr.20080112145409.393:onContinueDrag
    def onContinueDrag(self,event):

        g.trace()###
        return

        p = self.drag_p
        if not p: return

        try:
            canvas = self.canvas ; frame = self.c.frame
            if event:
                x,y = event.x,event.y
            else:
                x,y = frame.top.winfo_pointerx(),frame.top.winfo_pointery()
                # Stop the scrolling if we go outside the entire window.
                if x == -1 or y == -1: return 
            if self.dragging: # This gets cleared by onEndDrag()
                #@            << scroll the canvas as needed >>
                #@+node:ekr.20080112145409.394:<< scroll the canvas as needed >>
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
                        pass ### canvas.after_idle(self.onContinueDrag,None) # Don't propagate the event.
                #@-node:ekr.20080112145409.394:<< scroll the canvas as needed >>
                #@nl
        except:
            g.es_event_exception("continue drag")
    #@-node:ekr.20080112145409.393:onContinueDrag
    #@+node:ekr.20080112145409.395:onDrag
    def onDrag(self,event):

        g.trace()
        return ###

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
    #@-node:ekr.20080112145409.395:onDrag
    #@+node:ekr.20080112145409.396:onEndDrag
    def onEndDrag(self,event):

        g.trace()
        return ###

        """Tree end-of-drag handler called from vnode event handler."""

        c = self.c ; p = self.drag_p
        if not p: return

        c.setLog()

        if not g.doHook("enddrag1",c=c,p=p,v=p,event=event):
            self.endDrag(event)
        g.doHook("enddrag2",c=c,p=p,v=p,event=event)
    #@-node:ekr.20080112145409.396:onEndDrag
    #@-node:ekr.20080112145409.388:Dragging (gtkTree)
    #@+node:ekr.20080112145409.397:Icon Box...
    #@+node:ekr.20080112145409.398:onIconBoxClick
    def onIconBoxClick (self,event,p=None):

        c = self.c ; tree = self

        if not p: p = self.eventToPosition(event)
        if not p: return

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
    #@-node:ekr.20080112145409.398:onIconBoxClick
    #@+node:ekr.20080112145409.399:onIconBoxRightClick
    def onIconBoxRightClick (self,event,p=None):

        """Handle a right click in any outline widget."""

        c = self.c

        if not p: p = self.eventToPosition(event)
        if not p: return

        c.setLog()

        try:
            if not g.doHook("iconrclick1",c=c,p=p,v=p,event=event):
                self.OnActivateHeadline(p)
                self.endEditLabel()
                self.OnPopup(p,event)
            g.doHook("iconrclick2",c=c,p=p,v=p,event=event)
        except:
            g.es_event_exception("iconrclick")

        return 'break'
    #@-node:ekr.20080112145409.399:onIconBoxRightClick
    #@+node:ekr.20080112145409.400:onIconBoxDoubleClick
    def onIconBoxDoubleClick (self,event,p=None):

        c = self.c

        if not p: p = self.eventToPosition(event)
        if not p: return

        c.setLog()

        if self.trace and self.verbose: g.trace()

        try:
            if not g.doHook("icondclick1",c=c,p=p,v=p,event=event):
                self.endEditLabel() # Bug fix: 11/30/05
                self.OnIconDoubleClick(p) # Call the method in the base class.
            g.doHook("icondclick2",c=c,p=p,v=p,event=event)
        except:
            g.es_event_exception("icondclick")

        return 'break' # 11/19/06
    #@-node:ekr.20080112145409.400:onIconBoxDoubleClick
    #@-node:ekr.20080112145409.397:Icon Box...
    #@+node:ekr.20080112145409.401:OnActivateHeadline (gtkTree)
    def OnActivateHeadline (self,p,event=None):

        '''Handle common process when any part of a headline is clicked.'''

        # g.trace(p.headString())

        returnVal = 'break' # Default: do nothing more.
        trace = False

        try:
            c = self.c
            c.setLog()
            #@        << activate this window >>
            #@+node:ekr.20080112145409.402:<< activate this window >>
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
                c.treeWantsFocus()
                self.active = False
                returnVal = 'break'
            #@nonl
            #@-node:ekr.20080112145409.402:<< activate this window >>
            #@nl
        except:
            g.es_event_exception("activate tree")

        return returnVal
    #@-node:ekr.20080112145409.401:OnActivateHeadline (gtkTree)
    #@+node:ekr.20080112145409.403:Text Box...
    #@+node:ekr.20080112145409.404:configureTextState
    def configureTextState (self,p):

        c = self.c

        if not p: return

        # g.trace(p.headString(),self.c._currentPosition)

        if c.isCurrentPosition(p):
            if p == self.editPosition():
                self.setEditLabelState(p) # selected, editing.
            else:
                self.setSelectedLabelState(p) # selected, not editing.
        else:
            self.setUnselectedLabelState(p) # unselected
    #@-node:ekr.20080112145409.404:configureTextState
    #@+node:ekr.20080112145409.405:onCtontrolT
    # This works around an apparent gtk bug.

    def onControlT (self,event=None):

        # If we don't inhibit further processing the Tx.Text widget switches characters!
        return "break"
    #@-node:ekr.20080112145409.405:onCtontrolT
    #@+node:ekr.20080112145409.406:onHeadlineClick
    def onHeadlineClick (self,event,p=None):

        # g.trace('p',p)
        c = self.c ; w = event.widget

        if not p:
            try:
                p = w.leo_position
            except AttributeError:
                g.trace('*'*20,'oops')
        if not p: return 'break'

        # g.trace(g.app.gui.widget_name(w)) #p.headString())

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
    #@-node:ekr.20080112145409.406:onHeadlineClick
    #@+node:ekr.20080112145409.407:onHeadlineRightClick
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
                self.OnPopup(p,event)
            g.doHook("headrclick2",c=c,p=p,v=p,event=event)
        except:
            g.es_event_exception("headrclick")

        # 'continue' *is* correct here.
        # 'break' would make it impossible to unselect the headline text.
        return 'continue'
    #@-node:ekr.20080112145409.407:onHeadlineRightClick
    #@-node:ekr.20080112145409.403:Text Box...
    #@+node:ekr.20080112145409.408:tree.OnDeactivate
    def OnDeactivate (self,event=None):

        """Deactivate the tree pane, dimming any headline being edited."""

        tree = self ; c = self.c

        tree.endEditLabel()
        tree.dimEditLabel()
    #@-node:ekr.20080112145409.408:tree.OnDeactivate
    #@+node:ekr.20080112145409.409:tree.OnPopup & allies
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
    #@+node:ekr.20080112145409.410:OnPopupFocusLost
    #@+at 
    #@nonl
    # On Linux we must do something special to make the popup menu "unpost" if 
    # the mouse is clicked elsewhere.  So we have to catch the <FocusOut> 
    # event and explicitly unpost.  In order to process the <FocusOut> event, 
    # we need to be able to find the reference to the popup window again, so 
    # this needs to be an attribute of the tree object; hence, 
    # "self.popupMenu".
    # 
    # Aside: though gtk tries to be muli-platform, the interaction with 
    # different window managers does cause small differences that will need to 
    # be compensated by system specific application code. :-(
    #@-at
    #@@c

    # 20-SEP-2002 DTHEIN: This event handler is only needed for Linux.

    def OnPopupFocusLost(self,event=None):

        self.popupMenu.unpost()
    #@-node:ekr.20080112145409.410:OnPopupFocusLost
    #@+node:ekr.20080112145409.411:createPopupMenu
    def createPopupMenu (self,event):

        c = self.c ; frame = c.frame

        # If we are going to recreate it, we had better destroy it.
        if self.popupMenu:
            #self.popupMenu.destroy()
            self.popupMenu = None

        self.popupMenu = menu = frame.menu.getMenu()

        # Add the Open With entries if they exist.
        if g.app.openWithTable:
            frame.menu.createOpenWithMenuItemsFromTable(menu,g.app.openWithTable)
            table = (("-",None,None),)
            frame.menu.createMenuEntries(menu,table)

        #@    << Create the menu table >>
        #@+node:ekr.20080112145409.412:<< Create the menu table >>

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
        #@-node:ekr.20080112145409.412:<< Create the menu table >>
        #@nl

        # New in 4.4.  There is no need for a dontBind argument because
        # Bindings from tables are ignored.
        frame.menu.createMenuEntries(menu,table)
    #@-node:ekr.20080112145409.411:createPopupMenu
    #@+node:ekr.20080112145409.413:enablePopupMenuItems
    def enablePopupMenuItems (self,v,event):

        """Enable and disable items in the popup menu."""

        c = self.c ; menu = self.popupMenu

        #@    << set isAtRoot and isAtFile if v's tree contains @root or @file nodes >>
        #@+node:ekr.20080112145409.414:<< set isAtRoot and isAtFile if v's tree contains @root or @file nodes >>
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
        #@-node:ekr.20080112145409.414:<< set isAtRoot and isAtFile if v's tree contains @root or @file nodes >>
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
    #@-node:ekr.20080112145409.413:enablePopupMenuItems
    #@+node:ekr.20080112145409.415:showPopupMenu
    def showPopupMenu (self,event):

        """Show a popup menu."""

        g.trace()

        c = self.c ; menu = self.popupMenu

        menu.popup(None, None, None, event.button, event.time)

        # # Set the focus immediately so we know when we lose it.
        #c.widgetWantsFocus(menu)
    #@-node:ekr.20080112145409.415:showPopupMenu
    #@-node:ekr.20080112145409.409:tree.OnPopup & allies
    #@+node:ekr.20080112145409.416:onTreeClick
    def onTreeClick (self,event=None):

        '''Handle an event in the tree canvas, outside of any tree widget.'''

        c = self.c

        # New in Leo 4.4.2: a kludge: disable later event handling after a double-click.
        # This allows focus to stick in newly-opened files opened by double-clicking an @url node.
        if c.doubleClickFlag:
            c.doubleClickFlag = False
        else:
            c.treeWantsFocusNow()

        return 'break'
    #@-node:ekr.20080112145409.416:onTreeClick
    #@-node:ekr.20080112145409.378:Event handlers (gtkTree)
    #@+node:ekr.20080112145409.417:Incremental drawing...(gtkTree: not used)
    if 0:
        #@    @+others
        #@+node:ekr.20080112145409.418:allocateNodes
        def allocateNodes(self,where,lines):

            """Allocate gtk widgets in nodes that will become visible as the result of an upcoming scroll"""

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
        #@-node:ekr.20080112145409.418:allocateNodes
        #@+node:ekr.20080112145409.419:allocateNodesBeforeScrolling
        def allocateNodesBeforeScrolling (self, args):

            """Calculate the nodes that will become visible as the result of an upcoming scroll.

            args is the tuple passed to the gtk.Canvas.yview method"""

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
        #@-node:ekr.20080112145409.419:allocateNodesBeforeScrolling
        #@+node:ekr.20080112145409.420:updateNode
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
        #@-node:ekr.20080112145409.420:updateNode
        #@+node:ekr.20080112145409.421:setVisibleAreaToFullCanvas
        def setVisibleAreaToFullCanvas(self):

            if self.visibleArea:
                y1,y2 = self.visibleArea
                y2 = max(y2,y1 + self.canvas.winfo_height())
                self.visibleArea = y1,y2
        #@-node:ekr.20080112145409.421:setVisibleAreaToFullCanvas
        #@+node:ekr.20080112145409.422:setVisibleArea
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
        #@-node:ekr.20080112145409.422:setVisibleArea
        #@+node:ekr.20080112145409.423:tree.updateTree
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
        #@-node:ekr.20080112145409.423:tree.updateTree
        #@-others
    #@nonl
    #@-node:ekr.20080112145409.417:Incremental drawing...(gtkTree: not used)
    #@+node:ekr.20080112145409.424:Selecting & editing... (gtkTree)
    #@+node:ekr.20080112145409.425:dimEditLabel, undimEditLabel
    # Convenience methods so the caller doesn't have to know the present edit node.

    def dimEditLabel (self):

        p = self.c.currentPosition()
        self.setSelectedLabelState(p)

    def undimEditLabel (self):

        p = self.c.currentPosition()
        self.setSelectedLabelState(p)
    #@-node:ekr.20080112145409.425:dimEditLabel, undimEditLabel
    #@+node:ekr.20080112145409.426:tree.editLabel
    def editLabel (self,p,selectAll=False):

        """Start editing p's headline."""

        c = self.c
        trace = not g.app.unitTesting and (False or self.trace_edit)

        if p and p != self.editPosition():

            if trace:
                g.trace(p.headString(),g.choose(c.edit_widget(p),'','no edit widget'))

            self.endEditLabel()
            c.redraw()

        self.setEditPosition(p) # That is, self._editPosition = p

        if trace: g.trace(c.edit_widget(p))

        if p and c.edit_widget(p):
            self.revertHeadline = p.headString() # New in 4.4b2: helps undo.
            self.setEditLabelState(p,selectAll=selectAll) # Sets the focus immediately.
            c.headlineWantsFocus(p) # Make sure the focus sticks.
    #@-node:ekr.20080112145409.426:tree.editLabel
    #@+node:ekr.20080112145409.427:tree.set...LabelState
    #@+node:ekr.20080112145409.428:setEditLabelState
    def setEditLabelState (self,p,selectAll=False): # selected, editing

        c = self.c ; w = c.edit_widget(p)

        if p and w:
            # g.trace('*****',g.callers())
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
    #@-node:ekr.20080112145409.428:setEditLabelState
    #@+node:ekr.20080112145409.429:setSelectedLabelState
    def setSelectedLabelState (self,p): # selected, disabled

        # g.trace(p.headString(),g.callers())

        c = self.c

        if p and c.edit_widget(p):
            self.setDisabledHeadlineColors(p)
    #@-node:ekr.20080112145409.429:setSelectedLabelState
    #@+node:ekr.20080112145409.430:setUnselectedLabelState
    def setUnselectedLabelState (self,p): # not selected.

        c = self.c

        if p and c.edit_widget(p):
            self.setUnselectedHeadlineColors(p)
    #@-node:ekr.20080112145409.430:setUnselectedLabelState
    #@+node:ekr.20080112145409.431:setDisabledHeadlineColors
    def setDisabledHeadlineColors (self,p):

        c = self.c ; w = c.edit_widget(p)

        if self.trace and self.verbose:
            if not self.redrawing:
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
    #@-node:ekr.20080112145409.431:setDisabledHeadlineColors
    #@+node:ekr.20080112145409.432:setEditHeadlineColors
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
    #@-node:ekr.20080112145409.432:setEditHeadlineColors
    #@+node:ekr.20080112145409.433:setUnselectedHeadlineColors
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
    #@-node:ekr.20080112145409.433:setUnselectedHeadlineColors
    #@-node:ekr.20080112145409.427:tree.set...LabelState
    #@+node:ekr.20080112145409.434:tree.setHeadline (gtkTree)
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
    #@-node:ekr.20080112145409.434:tree.setHeadline (gtkTree)
    #@-node:ekr.20080112145409.424:Selecting & editing... (gtkTree)
    #@-others
#@-node:bob.20080117122525:class leoGtkTree (leoFrame.leoTree)
#@+node:bob.20080117122525.1:== Outline Canvas Widget ==
#@+node:bob.20080120105719:class FakeEvent
class FakeEvent(object):

    def __init__(self, widget, rawEvent, p):

        self.widget = widget
        self.rawEvent = rawEvent
        self.p = p

#@-node:bob.20080120105719:class FakeEvent
#@+node:bob.20080117104816:class OutlineCanvasPanel

class OutlineCanvasPanel(gobject.GObject):
    """A widget to display and manipulate a leo outline.

    This class provides the public interface for the outline widget
    and handles the scroll bar interface.

    The actual drawing handled by OutlineCanvas.

    The actual base gui component is a gtk.Table which can be found
    in self.top

    NOTE: This class is a subclass of GObject because it offers
    the possibility of using custom events and gobject properties that 
    can issue custom events when they are changed.

    """

    #@    << gobject properties >>
    #@+node:bob.20080117104816.3:<< gobject properties >>
    #@+at
    # This is where we declare out custom properties.
    # 
    # Remember that ALL children of this node are entries in a list
    # that initializes a dictionary.
    #@-at
    #@@c


    def do_get_property(self, property):

        return getattr(self, 'property_' + property.name.replace('-','_'))


    def do_set_property(self, property, value):

       setattr(self, 'property_' + property.name.replace('-','_'), value)



    __gproperties__ = {

        #@    @+others
        #@+node:bob.20080117104816.4:canvas height
        'canvas-height' : (
            gobject.TYPE_PYOBJECT,
            'canvas height',
            'The height of the tree in its currently expanded state',
            gobject.PARAM_READWRITE
        ),

        #@-node:bob.20080117104816.4:canvas height
        #@-others

    }

    #@-node:bob.20080117104816.3:<< gobject properties >>
    #@nl
    #@    << gobject signals >>
    #@+node:bob.20080117104816.5:<< gobject signals >>
    #@-node:bob.20080117104816.5:<< gobject signals >>
    #@nl

    #@    @+others
    #@+node:bob.20080118065903:onButtonPress
    def onButtonPress(self, w, event, *args):
        """Convert mouse button events into tk style events and pass up to leoTree.

        The outline canvas widget handles NO mouse events.

        """

        g.trace(event.x, event.y)

        codes = {
            gtk.gdk.BUTTON_PRESS: 'Button',
            gtk.gdk._2BUTTON_PRESS: 'Double',
            gtk.gdk._3BUTTON_PRESS: 'Triple',
            gtk.gdk.BUTTON_RELEASE: 'Any-ButtonRelease'
        }

        sp, target = self._canvas.hitTest(event.x, event.y)

        eventType = '<%s-%s>' % (codes[event.type], event.button)

        fakeEvent = FakeEvent(self, event, sp)

        self.leo_position = sp and sp.copy()

        self._leoTree.onOutlineCanvasEvent(target, eventType, fakeEvent, self.leo_position)

        return True

    #@-node:bob.20080118065903:onButtonPress
    #@+node:bob.20080117104816.1:__init__

    def __init__(self, leoTree, name):
        """Create an OutlineCanvasPanel instance."""

        gobject.GObject.__init__(self)

        g.trace('OutlineCanvasPanel', leoTree, name)

        self._leoTree = leoTree
        self.c = leoTree.c

        self._canvas = canvas = OutlineCanvas(self)
        self._canvas.connect('button_press_event', self.onButtonPress)

        self._table = self.top = gtk.Table(2,2)

        self._hscrollbar = gtk.HScrollbar()
        self._vscrollbar = gtk.VScrollbar()

        self._hadj = h = self._hscrollbar.get_adjustment()
        self._vadj = v = self._vscrollbar.get_adjustment()

        self._hscrollbar.set_range(0, 10)
        self._vscrollbar.set_range(0, 20)


        v.connect('value-changed', self.onScrollVertical)
        h.connect('value-changed', self.onScrollHorizontal)

        self._table.attach(self._hscrollbar, 0, 1, 1, 2, yoptions=0)
        self._table.attach(self._vscrollbar, 1, 2, 0, 1, xoptions=0)


        options = gtk.SHRINK | gtk.FILL | gtk.EXPAND
        self._table.attach(self._canvas, 0, 1, 0, 1, options, options)

        self._canvas.set_events(gtk.gdk.ALL_EVENTS_MASK)

        #@    << gproperty ivars >>
        #@+node:bob.20080117104816.2:<< gproperty ivars >>
        self.property_canvas_height = 0
        #@nonl
        #@-node:bob.20080117104816.2:<< gproperty ivars >>
        #@nl


        #self._entry = wx.TextCtrl(self._canvas,
        #    style = wx.SIMPLE_BORDER | wx.WANTS_CHARS
        #)

        #self._entry._virtualTop = -1000
        #self._entry.Hide()
        #self._canvas._widgets.append(self._entry)

        #self._canvas.update()


        # self.Bind(wx.EVT_SIZE, self.onSize)


        #self.SetBackgroundColour(self._leoTree.outline_pane_background_color)

        #self.Bind(wx.EVT_CHAR,
        #    lambda event, self=self._leoTree: onGlobalChar(self, event)
        #)

        #self.onScroll(wx.HORIZONTAL, 0)

    #@-node:bob.20080117104816.1:__init__
    #@+node:bob.20080117104816.6:showEntry
    showcount = 0
    def showEntry(self):

        # self.showcount +=1

        # g.trace(self.showcount, g.callers(20))

        entry = self._entry
        canvas = self._canvas

        ep = self._leoTree.editPosition()

        if not ep:
            return self.hideEntry()


        for sp in canvas._positions:
            if ep == sp:
                break
        else:
            return self.hideEntry()

        x, y, width, height = sp._textBoxRect
        #g.pr('	', x, y, width , height)

        entry._virtualTop = canvas._virtualTop + y -2

        entry.MoveXY(x - 2, y -2)
        entry.SetSize((max(width + 4, 100), -1))

        tw = self._leoTree.headlineTextWidget

        range = tw.getSelectionRange()
        tw.setInsertPoint(0)
        #tw.setInsertPoint(len(sp.headString()))
        tw.setSelectionRange(*range)
        entry.Show()
    #@-node:bob.20080117104816.6:showEntry
    #@+node:bob.20080117104816.7:hideEntry

    def hideEntry(self):

        entry = self._entry
        entry._virtualTop = -1000
        entry.MoveXY(0, -1000)

        entry.Hide()
    #@-node:bob.20080117104816.7:hideEntry
    #@+node:bob.20080117104816.8:getPositions

    def getPositions(self):
        return self._canvas._positions[:]
    #@nonl
    #@-node:bob.20080117104816.8:getPositions
    #@+node:bob.20080117104816.9:onScrollVertical
    def onScrollVertical(self, adjustment):
        """Handle changes in the position of the value of the vertical adustment."""

        self._canvas.vscrollTo(int(adjustment.value))
    #@nonl
    #@-node:bob.20080117104816.9:onScrollVertical
    #@+node:bob.20080117104816.10:onScrollHorizontal
    def onScrollHorizontal(self, adjustment):
        """Handle changes in the position of the value of the horizontal adustment."""

        self._canvas.hscrollTo(int(adjustment.value))
    #@-node:bob.20080117104816.10:onScrollHorizontal
    #@+node:bob.20080117104816.12:vscrollUpdate

    def vscrollUpdate(self):
        """Set the vertical scroll bar to match current conditions."""

        canvas = self._canvas

        oldtop = top = canvas._virtualTop
        canvasHeight = canvas.get_allocation().height
        treeHeight = canvas._treeHeight

        if (treeHeight - top) < canvasHeight:
            top = treeHeight - canvasHeight

        if top < 0 :
            top = 0

        if oldtop != top:
            canvas._virtualTop = top
            canvas.redraw()
            top = canvas._virtualTop

        #self.showEntry()

        self._vadj.set_all(
            top, #value
            0, #lower
            treeHeight, #upper
            canvasHeight * 0.1, #step_increment
            canvasHeight * 0.9, #page_increment
            canvasHeight #page-size
        )


    #@-node:bob.20080117104816.12:vscrollUpdate
    #@+node:bob.20080117104816.13:hscrollUpdate

    def hscrollUpdate(self):
        """Set the horizontal scroll bar to match current conditions."""

        canvas = self._canvas

        oldleft = left = canvas._virtualLeft
        canvasWidth = canvas.get_allocation().width
        treeWidth = canvas._treeWidth

        if (treeWidth - left) < canvasWidth:
            left = treeWidth - canvasWidth

        if left < 0 :
            left = 0

        if oldleft != left:
            canvas._virtualLeft = left
            canvas.redraw()
            left = canvas._virtualLeft

        #self.showEntry()

        self._hadj.set_all(
            left, #value
            0, #lower
            treeWidth, #upper
            canvasWidth * 0.1, #step_increment
            canvasWidth * 0.9, #page_increment
            canvasWidth #page-size
        )

    #@-node:bob.20080117104816.13:hscrollUpdate
    #@+node:bob.20080117104816.14:update

    def update(self):
        self._canvas.update()


    #@-node:bob.20080117104816.14:update
    #@+node:bob.20080117104816.15:redraw

    def redraw(self):
        self._canvas.redraw()
    #@nonl
    #@-node:bob.20080117104816.15:redraw
    #@+node:bob.20080117104816.16:refresh
    def refresh(self):
        self._canvas.refresh()
    #@nonl
    #@-node:bob.20080117104816.16:refresh
    #@+node:bob.20080117104816.17:GetName
    def GetName(self):
        return 'canvas'

    getName = GetName
    #@nonl
    #@-node:bob.20080117104816.17:GetName
    #@-others

gobject.type_register(OutlineCanvasPanel)
#@-node:bob.20080117104816:class OutlineCanvasPanel
#@+node:bob.20080117104810:class OutlineCanvas
class OutlineCanvas(gtk.DrawingArea):
    """Implements a virtual view of a leo outline tree.

    The class uses an off-screen buffer for drawing which it
    blits to the window during paint calls for expose events, etc,

    A redraw is only required when the size of the canvas changes,
    a scroll event occurs, or if the outline changes.

    """

    #@    @+others
    #@+node:bob.20080117104810.1:__init__
    def __init__(self, parent):
        """Create an OutlineCanvas instance."""

        #g.trace('OutlineCanvas')

        self.c = c = parent.c

        self._parent = parent
        #self.leoTree = parent.leoTree


        #@    << define ivars >>
        #@+node:bob.20080117104810.2:<< define ivars >>
        #self._icons = icons

        self._widgets = []

        self.drag_p = None

        self._size =  [1000, 1000]

        self._virtualTop = 0
        self._virtualLeft = 0

        self._textIndent = 30

        self._xPad = 30
        self._yPad = 2

        self._treeHeight = 500
        self._treeWidth = 500

        self._positions = []

        self._fontHeight = None
        self._iconSize = [20, 11]

        self._clickBoxSize = None
        self._lineHeight =  10
        self._requestedLineHeight = 10

        self._yTextOffset = None
        self._yIconOffset = None

        self._clickBoxCenterOffset = None

        self._clickBoxOffset = None


        #@-node:bob.20080117104810.2:<< define ivars >>
        #@nl

        gtk.DrawingArea.__init__(self)
        self._pangoLayout = self.create_pango_layout("Wq")


        # g.trace()


        self._font = pango.FontDescription('Sans 12')

        self._pangoLayout.set_font_description(self._font)


        self._buffer = None

        self.contextChanged()

        self.connect('map-event', self.onMap)


        # ??? diable keys for the time being
        self.connect('key-press-event', lambda *args: True)
        self.connect('key-release-event', lambda *args: True)


        #for o in (self, parent):
        #    
        #@nonl
        #@<< create  bindings >>
        #@+node:bob.20080117104810.3:<< create bindings >>
        # onmouse = self._leoTree.onMouse

        # for e, s in (
           # ( wx.EVT_LEFT_DOWN,     'LeftDown'),
           # ( wx.EVT_LEFT_UP,       'LeftUp'),
           # ( wx.EVT_LEFT_DCLICK,   'LeftDoubleClick'),
           # ( wx.EVT_MIDDLE_DOWN,   'MiddleDown'),
           # ( wx.EVT_MIDDLE_UP,     'MiddleUp'),
           # ( wx.EVT_MIDDLE_DCLICK, 'MiddleDoubleClick'),
           # ( wx.EVT_RIGHT_DOWN,    'RightDown'),
           # ( wx.EVT_RIGHT_UP,      'RightUp'),
           # ( wx.EVT_RIGHT_DCLICK,  'RightDoubleClick'),
           # ( wx.EVT_MOTION,        'Motion')
        # ):
            # o.Bind(e, lambda event, type=s: onmouse(event, type))



        # #self.Bind(wx.EVT_KEY_UP, self._leoTree.onChar)
        # #self.Bind(wx.EVT_KEY_DOWN, lambda event: self._leoTree.onKeyDown(event))

        # self.Bind(wx.EVT_CHAR,
            # lambda event, self=self._leoTree: onGlobalChar(self, event)
        # )

        #@-node:bob.20080117104810.3:<< create bindings >>
        #@nl

    #@+at
    # self.box_padding = 5 # extra padding between box and icon
    # self.box_width = 9 + self.box_padding
    # self.icon_width = 20
    # self.text_indent = 4 # extra padding between icon and tex
    # 
    # self.hline_y = 7 # Vertical offset of horizontal line
    # self.root_left = 7 + self.box_width
    # self.root_top = 2
    # 
    # self.default_line_height = 17 + 2 # default if can't set line_height 
    # from font.
    # self.line_height = self.default_line_height
    # 
    #@-at
    #@-node:bob.20080117104810.1:__init__
    #@+node:bob.20080117104810.4:hitTest
    def hitTest(self, xx, yy):
        """Trace for hitTest

        Rename folowwing hitTest to _hitTest, to enable trace.
        """
        result = self._hitTest(point)
        g.trace(result)
        return result

    def hitTest(self, xx, yy):
        """Returns a (position, item) tuple indecating where the hit occured.

        position indicates which headline was hit

        item indicates which portion of the headline that was hit.

        item is a string which can take the following values:

            + 'clickBox'
            + 'iconBox'
            + 'textBox'
            + 'beforeText-*'  (* is an number indicating which beforeText icon was hit)
            + 'headline' ( if on a headline but non of the others was hit.)
            + 'canvas'   ( The canvas was hit but there is no headline there.)




        """

        for sp in self._positions:

            if yy < (sp._top + self._lineHeight):

                x, y, w, h = sp._clickBoxRect
                if xx > x  and xx < (x + w) and yy > y and yy < (y + h):
                    return sp, 'clickBox'

                x, y, w, h = sp._iconBoxRect
                if xx > x  and xx < (x + w) and yy > y and yy < (y + h):
                    return sp, 'iconBox'

                x, y, w, h = sp._textBoxRect
                if xx > x  and xx < (x + w) and yy > y and yy < (y + h): 
                    return sp, 'textBox'

                if hasattr(sp, '_headStringIcons'):
                    i = -1
                    for x, y, w, h in sp._headStringIcons:
                        i += 1
                        if xx > x  and xx < (x + w) and yy > y and yy <(y + h):
                           return sp, 'beforeText-%s'%i

                return sp, 'headline'

        return None, 'canvas'

    #@-node:bob.20080117104810.4:hitTest
    #@+node:bob.20080117104810.5:_createNewBuffer
    def _createNewBuffer(self):
        """Create a new buffer for drawing."""


        if not self.window:
            g.trace('no window !!!!!!!!!!!!!!!!')
            g.trace(g.callers())
            return


        x, y, w, h = self.allocation

        # guard against negative or zero values at start up
        w = max(w, 1)
        h = max(h, 1)

        #g.trace('request new buffe:',w, h)


        if self._buffer:
            bw, bh = self._buffer.get_size()

            # only create a new buffer if the old one is too small
            if bw >= w and bh >= h:
                return

            # create a bigger buffer than requested to reduce the
            # number of requests when the splitter is being dragged slowly

            w = w + 100
            h = h + 100

        #g.trace('grant new buffer:', w, h)
        self._buffer = gtk.gdk.Pixmap(self.window, w, h)





    #@-node:bob.20080117104810.5:_createNewBuffer
    #@+node:bob.20080117104810.6:vscrollTo

    def vscrollTo(self, pos):
        """Scroll the canvas vertically to the specified position."""

        canvasHeight = self.get_allocation().height
        if (self._treeHeight - canvasHeight) < pos :
            pos = self._treeHeight - canvasHeight

        pos = max(0, pos)

        self._virtualTop = pos

        self.redraw()
    #@-node:bob.20080117104810.6:vscrollTo
    #@+node:bob.20080117104810.7:hscrollTo
    def hscrollTo(self, pos):
        """Scroll the canvas vertically to the specified position."""

        canvasWidth = self.get_allocation().width

        #g.trace(pos)

        if (self._treeWidth - canvasWidth) < pos :
            pos = min(0, self._treeWidth - canvasWidth)

        pos = max( 0, pos)

        self._virtualLeft = pos

        self.redraw()
    #@-node:bob.20080117104810.7:hscrollTo
    #@+node:bob.20080117104810.8:resize

    def resize(self):
        """Resize the outline canvas and, if required, create and draw on a new buffer."""

        c = self.c

        self._createNewBuffer()
        #self._parent.hscrollUpdate()
        self.draw()
        self.refresh()

        return True





    #@-node:bob.20080117104810.8:resize
    #@+node:bob.20080117104810.9:redraw
    def redraw(self):
        self.draw()
        self.refresh()
    #@-node:bob.20080117104810.9:redraw
    #@+node:bob.20080117104810.10:update

    def update(self):
        """Do a full update assuming the tree has been changed."""

        c = self.c

        canvasHeight = self.get_allocation().height

        hoistFlag = bool(self.c.hoistStack)

        if hoistFlag:
            stk = [self.c.hoistStack[-1].p]
        else:
            stk = [self.c.rootPosition()]

        #@    << find height of tree and position of currentNode >>
        #@+node:bob.20080117104810.11:<< find height of tree and position of currentNode >>

        # Find the number of visible nodes in the outline.

        cp = c.currentPosition().copy()
        cpCount = None

        count = 0
        while stk:

            p = stk.pop()

            while p:


                if stk or not hoistFlag:
                    newp = p.next()
                else:
                    newp = None

                if cp and cp == p:
                    cpCount = count
                    cp = False

                count += 1

                #@        << if p.isExpanded() and p.hasFirstChild():>>
                #@+node:bob.20080117104810.12:<< if p.isExpanded() and p.hasFirstChild():>>
                v=p.v
                if v.statusBits & v.expandedBit and v.hasChildren():
                #@nonl
                #@-node:bob.20080117104810.12:<< if p.isExpanded() and p.hasFirstChild():>>
                #@nl
                    stk.append(newp)
                    p = p.firstChild()
                    continue

                p = newp

        lineHeight = self._lineHeight

        self._treeHeight = count * lineHeight

        self._parent.set_property('canvas-height', self._treeHeight)


        if cpCount is not None:
            cpTop = cpCount * lineHeight

            if cpTop < self._virtualTop:
                self._virtualTop = cpTop

            elif cpTop + lineHeight > self._virtualTop + canvasHeight:
                self._virtualTop += (cpTop + lineHeight) - (self._virtualTop + canvasHeight)



        #@-node:bob.20080117104810.11:<< find height of tree and position of currentNode >>
        #@nl

        if (self._treeHeight - self._virtualTop) < canvasHeight:
            self._virtualTop = self._treeHeight - canvasHeight

        # if (self._treeHeight - self._virtualTop) < canvasHeight:
            # self._virtualTop = self._treeHeight - canvasHeight

        self.contextChanged()

        self.redraw()
        self._parent.vscrollUpdate()
        self._parent.hscrollUpdate()


    #@-node:bob.20080117104810.10:update
    #@+node:bob.20080117104810.13:onPaint

    def onPaint(self, *args):
        """Renders the off-screen buffer to the outline canvas."""



        if not self._buffer:
            return

        # w, h are needed because the buffer may be bigger than the window.
        w, h = self.window.get_size()

        #g.trace('size', w, h)

        # We use self.style.black_gc only because we need a gc, it has no relavence.

        self.window.draw_drawable(self.style.black_gc ,self._buffer, 0, 0, 0, 0, w, h)
    #@-node:bob.20080117104810.13:onPaint
    #@+node:bob.20080117104810.14:onMap
    def onMap(self, *args):
        self._createNewBuffer()
        self.update()
        self.connect('expose-event', self.onPaint)
        self.connect("size-allocate", self.onSize)
    #@-node:bob.20080117104810.14:onMap
    #@+node:bob.20080117104810.15:onSize
    def onSize(self, *args):
        """React to changes in the size of the outlines display area."""

        c = self.c

        self.resize()
        self._parent.vscrollUpdate()
        self._parent.hscrollUpdate()


    #@-node:bob.20080117104810.15:onSize
    #@+node:bob.20080117104810.16:refresh

    #def refresh(self):
        # """Renders the offscreen buffer to the outline canvas."""
        # return

        # #g.pr('refresh')
        # wx.ClientDC(self).BlitPointSize((0,0), self._size, self._buffer, (0, 0))

    refresh = onPaint
    #@nonl
    #@-node:bob.20080117104810.16:refresh
    #@+node:bob.20080117104810.17:contextChanged
    def contextChanged(self):
        """Adjust canvas attributes after a change in context.

        This should be called after setting or changing fonts or icon size or
        anything that effects the tree display.

        """

        self._pangoLayout.set_text('Wy')
        self._fontHeight = self._pangoLayout.get_pixel_size()[1]
        self._iconSize = (20, 11) #(icons[0].GetWidth(), icons[0].GetHeight())

        self._clickBoxSize = (9, 9) #(plusBoxIcon.GetWidth(), plusBoxIcon.GetHeight())

        self._lineHeight = max(
            self._fontHeight,
            self._iconSize[1],
            self._requestedLineHeight
        ) + 2 * self._yPad

        # y offsets

        self._yTextOffset = (self._lineHeight - self._fontHeight)//2

        self._yIconOffset = (self._lineHeight - self._iconSize[1])//2

        self._clickBoxCenterOffset = (
            -self._textIndent*2 + self._iconSize[0]//2,
            self._lineHeight//2
        )

        self._clickBoxOffset = (
            self._clickBoxCenterOffset[0] - self._clickBoxSize[0]//2,
            (self._lineHeight  - self._clickBoxSize[1])//2
        )


    #@-node:bob.20080117104810.17:contextChanged
    #@+node:bob.20080117104810.18:requestLineHeight
    def requestLineHeight(height):
        """Request a minimum height for lines."""

        assert int(height) and height < 200
        self.requestedHeight = height
        self.beginUpdate()
        self.endUpdate()
    #@-node:bob.20080117104810.18:requestLineHeight
    #@+node:bob.20080117104810.19:def draw

    def draw(self, *args):
        """Draw the outline on the off-screen buffer.

        This method needs to be as fast as possible.

        A lot of the original need for speed has gone now we
        are drawing off screen but it's still important to be fast.

        """
        c = self.c

        # Its not an error to have no buffer
        if self._buffer is None:
            g.trace('no buffer yet')
            return

        #@    << setup local variables >>
        #@+node:bob.20080118085835:<< setup local variables >>
        # these are set to improve efficiancey


        outlineBackgroundCairoColor = leoColor.getCairo('leo yellow')
        selectedBackgroundCairoColor = leoColor.getCairo('grey90')
        headlineTextCairoColor = leoColor.getCairo('black')

        canvasWidth, canvasHeight = self.window.get_size()


        pangoLayout = self._pangoLayout


        top = self._virtualTop
        if top < 0:
            self._virtualTop = top = 0

        left = self._virtualLeft
        if left < 0:
            self._virtualLeft = left = 0   


        bottom = top + canvasHeight


        textIndent = self._textIndent
        treeWidth = self._treeWidth

        yPad = self._yPad
        xPad = self._xPad - left

        yIconOffset = self._yIconOffset

        yTextOffset = self._yTextOffset

        clickBoxOffset_x, clickBoxOffset_y = self._clickBoxOffset

        clickBoxCenterOffset_x, clickBoxCenterOffset_y = \
            self._clickBoxCenterOffset

        clickBoxSize_w, clickBoxSize_h = self._clickBoxSize

        iconSize_w, iconSize_h = self._iconSize

        lineHeight = self._lineHeight
        halfLineHeight = lineHeight//2


        # images
        gui = g.app.gui

        icons = gui.treeIcons
        globalImages = gui.globalImages
        plusBoxIcon = gui.plusBoxIcon
        minusBoxIcon = gui.minusBoxIcon

        currentPosition = c.currentPosition()

        #@-node:bob.20080118085835:<< setup local variables >>
        #@nl

        cr = self._buffer.cairo_create()


        cr.rectangle(0, 0, canvasWidth, canvasHeight)
        cr.clip()


        #@    << draw background >>
        #@+node:bob.20080118085835.1:<< draw background >>
        cr.set_source_rgb(*outlineBackgroundCairoColor)
        cr.rectangle(0, 0, canvasWidth, canvasHeight)
        cr.fill()
        #@-node:bob.20080118085835.1:<< draw background >>
        #@nl

        #@    << draw tree >>
        #@+node:bob.20080117104810.20:<< draw tree >>
        y = 0

        hoistFlag = bool(c.hoistStack)

        if hoistFlag:
            stk = [c.hoistStack[-1].p]
        else:
            stk = [c.rootPosition()]

        self._positions = positions = []

        #@+at
        # My original reason for writing the loop this way was to make it as 
        # fast as
        # possible. Perhaps I was being a bit too paranoid and we should 
        # change back to
        # more conventional iterations, on the other hand if it ain't broke 
        # don't fix it.
        #@-at
        #@@c


        while stk:

            p = stk.pop()

            while p:

                if stk or not hoistFlag:
                    newp = p.next()
                else:
                    newp = None

                mytop = y
                y = y + lineHeight

                if mytop > bottom:
                    # no need to draw any more
                    stk = []
                    p = None
                    break

                if y > top:

                    #this position is visible

                    sp = p.copy()

                    #@            << setup object >>
                    #@+node:bob.20080117104810.21:<< set up object >>
                    # depth: the depth of indentation relative to the current hoist.
                    sp._depth = len(stk)


                    # _virtualTop: top of this line in virtual canvas coordinates
                    sp._virtualTop =  mytop

                    # _top: top of this line in real canvas coordinates
                    sp._top = mytop - top

                    # ??? maybe give each position it own pangoLayout?
                    pangoLayout.set_text(sp.headString())

                    textSize_w, textSize_h = pangoLayout.get_pixel_size()


                    # this should be _virtualLeft
                    xTextOffset = ((sp._depth +1) * textIndent) + xPad

                    textPos_x = xTextOffset
                    textPos_y =  sp._top + yTextOffset

                    iconPos_x = textPos_x - textIndent
                    iconPos_y = textPos_y + yIconOffset

                    clickBoxPos_x = textPos_x + clickBoxOffset_x
                    clickBoxPos_y = textPos_y + clickBoxOffset_y

                    sp._clickBoxCenter_x = clickBoxPos_x + clickBoxCenterOffset_x
                    sp._clickBoxCenter_y = clickBoxPos_y + clickBoxCenterOffset_y

                    sp._textBoxRect = [textPos_x, textPos_y, textSize_w, textSize_h]
                    sp._iconBoxRect = [iconPos_x, iconPos_y, iconSize_w, iconSize_h]
                    sp._clickBoxRect = [clickBoxPos_x, clickBoxPos_y, clickBoxSize_w, clickBoxSize_h]

                    sp._icon = icons[p.v.computeIcon()]


                    if sp.hasFirstChild():
                        sp._clickBoxIcon = plusBoxIcon
                        if sp.isExpanded():
                            sp._clickBoxIcon = minusBoxIcon
                    else:
                        sp._clickBoxIcon = None


                    if sp == currentPosition:
                        sp._current = True
                        #@    << set self._currentHighlightRect >>
                        #@+node:bob.20080118085835.2:<< set self._currentHighlightRect >>
                        tx, ty, tw, th = sp._textBoxRect

                        sp._currentHighlightRect = [tx, ty-2, tw+6, th+4]
                        sp._textBoxRect[0] += 3
                        #@nonl
                        #@-node:bob.20080118085835.2:<< set self._currentHighlightRect >>
                        #@nl
                    else:
                        sp._current = False
                    #@-node:bob.20080117104810.21:<< set up object >>
                    #@nl

                    positions.append(sp)

                    treeWidth = max(
                        treeWidth,
                        textSize_w + xTextOffset + left
                    )

                #@        << if p.isExpanded() and p.hasFirstChild():>>
                #@+node:bob.20080117104810.12:<< if p.isExpanded() and p.hasFirstChild():>>
                v=p.v
                if v.statusBits & v.expandedBit and v.hasChildren():
                #@nonl
                #@-node:bob.20080117104810.12:<< if p.isExpanded() and p.hasFirstChild():>>
                #@nl
                    stk.append(newp)
                    p = p.firstChild()
                    continue

                p = newp

        if treeWidth > self._treeWidth:
            # theoretically this could be recursive ???
            # but its unlikely ...
            self._treeWidth = treeWidth
            self._parent.hscrollUpdate()

        if not positions:
            #g.trace('No positions!')
            return

        self._virtualTop =  positions[0]._virtualTop


        # try:
            # result = self._leoTree.drawTreeHook(self)
            # g.pr('result =', result)
        # except:
            # result = False
            # g.pr('result is False')

        # if hasattr(self._leoTree, 'drawTreeHook'):
            # try:
                # result = self._leoTree.drawTreeHook(self)
            # except:
                # result = False
        # else:
            # #g.pr('drawTreeHook not known')
            # result = None

        # if not result:

        #@<< draw headline icons and text >>
        #@+node:bob.20080117104810.22:<< draw headline icons and text >>

        cr.update_layout(pangoLayout)

        for sp in positions:

            if 0: 
                #@        << draw before text icons >>
                #@+node:bob.20080117104810.23:<< draw before text icons >>

                try:
                    headStringIcons = sp.v.t.unknownAttributes.get('icons', [])
                except:
                    headStringIcons = None

                sp._headStringIcons = hsi = []

                if headStringIcons:

                    x, y, w, h = sp._textBoxRect

                    for headStringIcon in headStringIcons:
                        try:
                            path = headStringIcon['relPath']

                            try:
                                image = globalImages[path]
                            except KeyError:
                                image = getImage(path)

                        except KeyError:
                            image = None

                        if image:

                            hsi.append((x, y, image.get_width(), image.get_height()))       

                            cr.set_source_pixbuf(image, x, y)
                            cr.paint()

                            x = x + image.get_width() + 5

                    # shift position of text and hightlight box to accomodate icons 
                    sp._currentPositionHighlightRect[0] = x - 3
                    sp._textBoxRect[0] = x
                #@-node:bob.20080117104810.23:<< draw before text icons >>
                #@nl

            pangoLayout.set_text(sp.headString())

            if sp._current:

                cr.set_source_rgb(*selectedBackgroundCairoColor)
                cr.rectangle(*sp._currentHighlightRect)
                cr.fill()

            cr.set_source_rgb(*headlineTextCairoColor)
            x, y, w, h = sp._textBoxRect 

            #g.trace(x, y, w, h, sp.headString())

            cr.move_to(x, y)
            cr.show_layout(pangoLayout)

            #< < draw after text icons >>


        #@-node:bob.20080117104810.22:<< draw headline icons and text >>
        #@nl
        #@<< draw lines >>
        #@+node:bob.20080117104810.24:<< draw lines >>
        #@-node:bob.20080117104810.24:<< draw lines >>
        #@nl
        #@<< draw bitmaps >>
        #@+node:bob.20080117104810.25:<< draw bitmaps >>

        for sp in positions:

            x, y, w, h = sp._iconBoxRect

            cr.set_source_pixbuf(sp._icon,x,y)
            cr.paint()
            #cr.stroke()

            if sp._clickBoxIcon:
                x, y, w, h = sp._clickBoxRect
                cr.set_source_pixbuf(sp._clickBoxIcon, x, y)
                cr.paint()
        #@-node:bob.20080117104810.25:<< draw bitmaps >>
        #@nl

        #@<< draw focus >>
        #@+node:bob.20080117104810.26:<< draw focus >>
        if 0:
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            if self._leoTree.hasFocus():
                dc.SetPen(wx.BLACK_PEN)
            #else:
            #    dc.SetPen(wx.GREEN_PEN)
                dc.DrawRectanglePointSize( (0,0), self.GetSize())
        #@nonl
        #@-node:bob.20080117104810.26:<< draw focus >>
        #@nl




        #@-node:bob.20080117104810.20:<< draw tree >>
        #@nl

        #self._parent.showEntry()

        return True






    #@-node:bob.20080117104810.19:def draw
    #@-others
#@-node:bob.20080117104810:class OutlineCanvas
#@-node:bob.20080117122525.1:== Outline Canvas Widget ==
#@-others

#@-node:ekr.20080112170946:@thin leoGtkTree.py
#@-leo
