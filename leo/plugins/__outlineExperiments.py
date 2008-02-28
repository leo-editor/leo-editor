#@+leo-ver=4-thin
#@+node:ekr.20040723100651:@thin __outlineExperiments.py
"""Override outline drawing code to test optimized drawing"""

"""This class implements a tree control similar to Windows explorer.

The code is based on code found in Python's IDLE program."""

#@@language python
#@@tabwidth -4

import leoGlobals as g

import leoTkinterTree
import leoFrame
import leoNodes
import Tkinter as Tk
import tkFont
import sys

#@<< about drawing >>
#@+node:ekr.20040723173301.1:<< About drawing >>
#@+at
# 
# Leo must update the outline pane with minimum flicker.  Leo assumes that all 
# code that changes the outline pane will be enclosed in matching calls to the 
# c.beginUpdate and c.endUpdate  methods of the Commands class. 
# c.beginUpdate() inhibits drawing until the matching c.endUpdate().  These 
# calls may be nested; only the outermost call to c.endUpdate() calls 
# c.redraw() to force a redraw of the outline pane.  Calls to c.endUpdate may 
# contain an optional flag argument.  Leo redraws the screen only if flag is 
# True.  This allows code to suppress redrawing entirely when needed.  For an 
# example, see idle_body_key.
# 
# c.redraw and its allies in this class redraw all icons automatically.   
# v.computeIcon method tells what the icon should be.  The v.iconVal tells 
# what the present icon is. The body key handler simply compares these two 
# values and sets redraw_flag if they don't match.
#@-at
#@nonl
#@-node:ekr.20040723173301.1:<< About drawing >>
#@nl

if not g.app.unitTesting:
    
    print '*' * 20, " overriding leoTkinterTree class "

    # class leoTkinterTree (leoFrame.leoTree):
    class myLeoTkinterTree(leoFrame.leoTree):
    
        callbacksInjected = False
        
        #@        @+others
        #@+node:ekr.20040729143503.1:Notes
        #@@killcolor
        #@nonl
        #@+node:ekr.20040725173253:Changes made since first update
        #@+at
        # 
        # - disabled drawing of user icons.  They weren't being hidden, which 
        # messed up scrolling.
        # 
        # - Expanded clickBox so all clicks fall inside it.
        # 
        # - Added binding for plugBox so it doesn't interfere with the 
        # clickBox.  Another weirdness.
        # 
        # - Setting self.useBindtags = True also seems to work.
        # 
        # - Re-enabled code in drawText that sets the headline state.
        # 
        # - Clear self.ids dict on each redraw so "invisible" id's don't 
        # confuse eventToPosition.
        #     This effectively disables a check on id's, but that can't be 
        # helped.
        # 
        # - eventToPosition now returns p.copy, which means that nobody can 
        # change the list.
        # 
        # - Likewise, clear self.iconIds so old icon id's don't confuse 
        # findVnodeWithIconId.
        # 
        # - All drawing methods must do p = p.copy() at the beginning if they 
        # make any changes to p.
        #     - This ensures neither they nor their allies can change the 
        # caller's position.
        #     - In fact, though, only drawTree changes position.
        # 
        # - Fixed the race conditions that caused drawing sometimes to fail.  
        # The essential idea is that we must not call w.config if we are about 
        # to do a redraw.  For full details, see the Notes node in the Race 
        # Conditions section.
        #@-at
        #@nonl
        #@-node:ekr.20040725173253:Changes made since first update
        #@+node:ekr.20040726152305:Changes made since second update
        #@+at
        # 
        # - Removed code in leoTkinterFrame.OnActivateTree:
        #     self.tree.undimEditLabel()
        # 
        # I have no idea why this was originally there.  It seems to be pure 
        # duplication.
        # 
        # - Removed code from self.OnActivate:
        #     self.undimEditLabel()
        # 
        # Again, needless duplication.  The OnActivate logic might be 
        # simplified further...
        # 
        # - Removed duplicate code in tree.select.  The following code was 
        # being called twice (!!):
        #     self.endEditLabel()
        #     self.setUnselectedLabelState(old_p)
        # 
        # - Add p.copy() instead of p when inserting nodes into data 
        # structures in select.
        # 
        # - Fixed a _major_ bug in Leo's core.  c.setCurrentPosition must COPY 
        # the position given to it!  It's _not_ enough to return a copy of 
        # position: it may already have changed!!
        # 
        # - Fixed a another (lesser??) bug in Leo's core.  handleUserClick 
        # should also make a copy.
        # 
        # - Fixed bug in mod_scripting.py.  The callback was failing if the 
        # script was empty.
        # 
        # - Put in the self.recycle ivar AND THE CODE STILL FAILS.
        #     It seems to me that this shows there is a bug in my code 
        # somewhere, but where ???????????????????
        #@-at
        #@nonl
        #@-node:ekr.20040726152305:Changes made since second update
        #@+node:ekr.20040728143724:Most recent changes
        #@+at
        # 
        # - Added generation count.
        #     - Incremented on each redraw.
        #     - Potentially a barrior to race conditions, but it never seemed 
        # to do anything.
        #     - This code is a candidate for elimination.
        # 
        # - Used vnodes rather than positions in several places.
        #     - I actually don't think this was involved in the real problem, 
        # and it doesn't hurt.
        # 
        # - Added much better traces: the beginning of the end for the bugs 
        # :-)
        #     - Added self.verbose option.
        #     - Added align keyword option to g.trace.
        #     - Separate each set of traces by a blank line.
        #         - This makes clear the grouping of id's.
        # 
        # - Defensive code: Disable dragging at start of redraw code.
        #     - This protects against race conditions.
        # 
        # - Fixed blunder 1: Fixed a number of bugs in the dragging code.
        #     - I had never looked at this code!
        #     - Eliminating false drags greatly simplifies matters.
        #     - One of the blunders was the confusion between self.dragging 
        # and self._dragging.
        #         - self.setDragging sets self._dragging.
        #         - self._dragging is TOTALLY USELESS!!
        # 
        # - Fixed blunder 2: Added the following to eventToPosition:
        #         x = canvas.canvasx(x)
        #         y = canvas.canvasy(y)
        #     - Apparently this was the cause of false associations between 
        # icons and id's.
        #     - It's amazing that the code didn't fail earlier without these!
        # 
        # - Converted all module-level constants to ivars.
        # 
        # - Lines no longer interfere with eventToPosition.
        #     - The problem was that find_nearest or find_overlapping don't 
        # depend on stacking order!
        #     - Added p param to horizontal lines, but not vertical lines.
        #     - EventToPosition adds 1 to the x coordinate of vertical lines, 
        # then recomputes the id.
        # 
        # - Compute indentation only in forceDrawNode.  Removed child_indent 
        # constant.
        # 
        # - Simplified drawTree to use indentation returned from 
        # forceDrawNode.
        # 
        # - setText now ensures that state is "normal" before attempting to 
        # set the text.
        #     - This is the robust way.
        # 
        # 7/31/04: newText must call setText for all nodes allocated, even if 
        # p matches.
        #@-at
        #@nonl
        #@-node:ekr.20040728143724:Most recent changes
        #@-node:ekr.20040729143503.1:Notes
        #@+node:ekr.20040723183449.1:Allocation...
        #@+node:ekr.20040723184305:newBox
        def newBox (self,p,x,y,image):
            
            canvas = self.canvas ; tag = "plugBox"
        
            if self.freeBoxes:
                id = self.freeBoxes.pop(0)
                canvas.coords(id,x,y)
                canvas.itemconfigure(id,image=image)
            else:
                id = canvas.create_image(x,y,image=image,tag=tag)
                
            if self.trace and self.verbose:
                g.trace("%3d %3d %3d %8s" % (id,x,y,' '),p.headString(),align=-20)
        
            assert(id not in self.visibleBoxes)
            self.visibleBoxes.append(id)
        
            assert(not self.ids.get(id))
            assert(p)
            self.ids[id] = p.copy()
        
            return id
        #@nonl
        #@-node:ekr.20040723184305:newBox
        #@+node:ekr.20040724072523.1:newClickBox
        def newClickBox (self,p,x1,y1,x2,y2):
            
            canvas = self.canvas ; defaultColor = "" ; tag="clickBox" 
        
            if self.freeClickBoxes:
                id = self.freeClickBoxes.pop(0)
                canvas.coords(id,x1,y1,x2,y2)
            else:
                # Was this the bug ?? was (x1,y2**,x2,y2)
                id = self.canvas.create_rectangle(x1,y1,x2,y2,tag=tag)
                canvas.itemconfig(id,fill=defaultColor,outline=defaultColor)
                
            if self.trace and self.verbose:
                g.trace("%3d %3d %3d %3d %3d" % (id,x1,y1,x2,y2),p.headString(),align=-20)
        
            assert(id not in self.visibleClickBoxes)
            self.visibleClickBoxes.append(id)
            
            assert(p)
            assert(not self.ids.get(id))
            self.ids[id] = p.copy()
            
            return id
        #@nonl
        #@-node:ekr.20040724072523.1:newClickBox
        #@+node:ekr.20040723184305.1:newIcon
        def newIcon (self,p,x,y,image):
            
            canvas = self.canvas ; tag = "iconBox"
        
            if self.freeIcons:
                id = self.freeIcons.pop(0)
                canvas.itemconfigure(id,image=image)
                canvas.coords(id,x,y)
            else:
                id = canvas.create_image(x,y,image=image,anchor="nw",tag=tag)
                assert(not self.ids.get(id))
                
            if self.trace and self.verbose:
                g.trace("%3d %3d %3d %8s" % (id,x,y,' '),p.headString(),align=-20)
                
            assert(id not in self.visibleIcons)
            self.visibleIcons.append(id)
            
            assert(p)
            p = p.copy()
            assert(not self.iconIds.get(id))
            assert(not self.ids.get(id))
            data = p,self.generation
            self.iconIds[id] = data # Remember which vnode belongs to the icon.
            self.ids[id] = p
        
            return id
        #@nonl
        #@-node:ekr.20040723184305.1:newIcon
        #@+node:ekr.20040723184305.2:newLine
        def newLine (self,p,x1,y1,x2,y2):
            
            canvas = self.canvas
            
            if self.freeLines:
                id = self.freeLines.pop(0)
                canvas.coords(id,x1,y1,x2,y2)
            else:
                id = canvas.create_line(x1,y1,x2,y2,tag="lines",fill="gray50") # stipple="gray25")
                assert(not self.ids.get(id))
        
            assert(not self.ids.get(id))
            self.ids[id] = p
                
            self.visibleLines.append(id)
        
            return id
        #@nonl
        #@-node:ekr.20040723184305.2:newLine
        #@+node:ekr.20040723184305.4:newText
        def newText (self,p,x,y):
            
            canvas = self.canvas ; tag = "textBox"
            
            d = self.freeText
            key = p.v ; assert key
            pList = d.get(key,[])
            
            # Return only Tk.Text widgets with an exact match with p.
            found = False
            for i in xrange(len(pList)):
                p2,t,id = pList[i]
                if p2 == p:
                    # if self.trace: g.trace("allocating from freeText")
                    del pList[i]
                    id = t.leo_window_id
                    assert(id)
                    assert(t.leo_position == p2)
                    canvas.coords(id,x,y)
                    found = True ; break
                    
            if not found:
                # Tags are not valid in Tk.Text widgets.
                t = Tk.Text(canvas,state="normal",font=self.font,bd=0,relief="flat",height=1)
            
                if self.useBindtags:
                    t.bindtags(self.textBindings)
                else:
                    t.bind("<Button-1>", self.onHeadlineClick)
                    t.bind("<Button-3>", self.onHeadlineRightClick)
                    t.bind("<Key>",      self.onHeadlineKey)
                    t.bind("<Control-t>",self.onControlT)
            
                id = canvas.create_window(x,y,anchor="nw",window=t,tag=tag)
                t.leo_window_id = id # Never changes.
                
            if self.trace and self.verbose:
                g.trace("%3d %3d %3d %8s" % (id,x,y,' '),p.headString(),self.textAddr(t),align=-20)
        
            # Common configuration.
            # Bug fix 7/31/04:  We must call setText even if p matches: p's text may have changed!
            self.setText(t,p.headString(),tag="newText")
            t.configure(width=self.headWidth(p.copy()))
            t.leo_position = p.copy() # Never changes.
            t.leo_generation = self.generation
        
            assert(id == t.leo_window_id)
            assert(not self.ids.get(id))
            self.ids[id] = p.copy()
            
            # New in 4.2 b3: entries are pairs (p,t,id) indexed by v.
            key = p.v ; assert key
            pList = self.visibleText.get(key,[])
            pList.append((p,t,id),)
            self.visibleText[key] = pList
        
            return t
        #@nonl
        #@-node:ekr.20040723184305.4:newText
        #@+node:ekr.20040723194802:recycleWidgets
        def recycleWidgets (self):
            
            # if self.trace: g.trace()
            
            canvas = self.canvas
            
            for id in self.visibleBoxes:
                assert(id not in self.freeBoxes)
                self.freeBoxes.append(id)
                canvas.coords(id,-100,-100)
            self.visibleBoxes = []
        
            for id in self.visibleClickBoxes:
                assert(id not in self.freeClickBoxes)
                self.freeClickBoxes.append(id)
                canvas.coords(id,-100,-100,-100,-100)
            self.visibleClickBoxes = []
            
            for id in self.visibleIcons:
                assert(id not in self.freeIcons)
                self.freeIcons.append(id)
                canvas.coords(id,-100,-100)
            self.visibleIcons = []
                
            for id in self.visibleLines:
                assert(id not in self.freeLines)
                self.freeLines.append(id)
                canvas.coords(id,-100,-100,-100,-100)
            self.visibleLines = []
            
            for key in self.visibleText.keys():
                visList = self.visibleText.get(key,[])
                freeList = self.freeText.get(key,[])
                for data in visList:
                    p,t,id = data
                    assert p  == t.leo_position
                    assert id == t.leo_window_id
                    canvas.coords(id,-100,-100)
                    freeList.append(data)
                self.freeText[key] = freeList
            self.visibleText = {}
            
            for id in self.visibleUserIcons:
                # The present code does not recycle user Icons.
                self.canvas.delete(id)
            self.visibleUserIcons = []
        #@nonl
        #@-node:ekr.20040723194802:recycleWidgets
        #@+node:ekr.20040726233715:destroyWidgets (not used)
        # This was a desparation measure.  It would leak bindings bigtime.
        
        def destroyWidgets (self):
            
            g.trace('*' * 20)
        
            self.canvas.delete("all")
            
            self.visibleBoxes = []
            self.visibleClickBoxes = []
            self.visibleIcons = []
            self.visibleLines = []
            self.visibleText  = []
        #@nonl
        #@-node:ekr.20040726233715:destroyWidgets (not used)
        #@+node:ekr.20040725072304:getTextStats
        def getTextStats (self):
            
            # Count the number of individual items in each list in freeText.
            free = 0
            for val in self.freeText.values():
                free += len(val)
                
            visible = len(self.visibleText)
            
            return "%3d %3d tot: %4d" % (visible,free,visible+free)
        #@nonl
        #@-node:ekr.20040725072304:getTextStats
        #@-node:ekr.20040723183449.1:Allocation...
        #@+node:ekr.20040723173301.2:Birth...
        #@+node:ekr.20040723171712:__init__
        def __init__(self,c,frame,canvas):
            
            # Init the base class.
            leoFrame.leoTree.__init__(self,frame)
        
            # Objects associated with this tree.
            self.canvas = canvas
            
            #@    << define drawing constants >>
            #@+node:ekr.20040723101548:<< define drawing constants >>
            self.box_padding = 5 # extra padding between box and icon
            self.box_width = 9 + self.box_padding
            self.icon_width = 20
            self.text_indent = 4 # extra padding between icon and tex
            
            self.hline_y = 7 # Vertical offset of horizontal line
            self.root_left = 7 + self.box_width
            self.root_top = 2
            
            self.default_line_height = 17 + 2 # default if can't set line_height from font.
            self.line_height = self.default_line_height
            #@nonl
            #@-node:ekr.20040723101548:<< define drawing constants >>
            #@nl
            #@    << old ivars >>
            #@+node:ekr.20040723171712.1:<< old ivars >>
            # Miscellaneous info.
            self.iconimages = {} # Image cache set by getIconImage().
            self.active = False # True if tree is active
            self._editPosition = None # Returned by leoTree.editPosition()
            self.lineyoffset = 0 # y offset for this headline.
            self.disableRedraw = False # True: reschedule a redraw for later.
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
            self.prevMoveToFrac = None
            self.visibleArea = None
            self.expandedVisibleArea = None
            
            if self.allocateOnlyVisibleNodes:
                self.frame.bar1.bind("<B1-ButtonRelease>", self.redraw)
            #@nonl
            #@-node:ekr.20040723171712.1:<< old ivars >>
            #@nl
            #@    << inject callbacks into the position class >>
            #@+node:ekr.20040725051437:<< inject callbacks into the position class >>
            # The new code injects 3 callbacks for the colorizer.
            
            if not myLeoTkinterTree.callbacksInjected: # Class var.
                leoTkinterTree.callbacksInjected = True
                self.injectCallbacks()
            #@nonl
            #@-node:ekr.20040725051437:<< inject callbacks into the position class >>
            #@nl
            
            self.redrawing = False # Used only to disable traces.
            self.trace = False
            self.verbose = True
            self.useBindtags = True
            self.generation = 0
            self.dragging = False
            
            self.createPermanentBindings()
            self.setEditPosition(None) # Set positions returned by leoTree.editPosition()
            
            # Keys are id's, values are unchanging positions...
            self.ids = {}
            self.iconIds = {}
        
            # Lists of visible (in-use) widgets...
            self.visibleBoxes = []
            self.visibleClickBoxes = []
            self.visibleIcons = []
            self.visibleLines = []
            self.visibleText  = {} # Keys are vnodes, values are Tk.Text widgets
            self.visibleUserIcons = []
        
            # Lists of free, hidden widgets...
            self.freeBoxes = []
            self.freeClickBoxes = []
            self.freeIcons = []
            self.freeLines = []
            self.freeText = {} # Keys are vnodes, values are Tk.Text widgets
            self.freeUserIcons = []
        #@nonl
        #@-node:ekr.20040723171712:__init__
        #@+node:ekr.20040723102245.2:createPermanentBindings
        def createPermanentBindings (self):
            
            canvas = self.canvas
            
            canvas.tag_bind('clickBox','<Button-1>',   self.onClickBoxClick)
        
            canvas.tag_bind('iconBox','<Button-1>', self.onIconBoxClick)
            canvas.tag_bind('iconBox','<Double-1>', self.onIconBoxDoubleClick)
            canvas.tag_bind('iconBox','<Button-3>', self.onIconBoxRightClick)
            
            canvas.tag_bind('iconBox','<B1-Motion>',            self.onDrag)
            canvas.tag_bind('iconBox','<Any-ButtonRelease-1>',  self.onEndDrag)
            
            canvas.tag_bind('plusBox','<Button-1>',   self.onClickBoxClick)
        
            if self.useBindtags: # Create a dummy widget to hold all bindings.
                t = Tk.Text(canvas) # This _must_ be a Text widget attached to the canvas!
                if 1: # Either way works properly.
                    t.bind("<Button-1>", self.onHeadlineClick)
                    t.bind("<Button-3>", self.onHeadlineRightClick)
                    t.bind("<Key>",      self.onHeadlineKey)
                else:
                    t.bind("<Button-1>", self.onHeadlineClick, '+')
                    t.bind("<Button-3>", self.onHeadlineRightClick, '+')
                    t.bind("<Key>",      self.onHeadlineKey, '+')
                t.bind("<Control-t>",self.onControlT)
            
                # newText() attaches these bindings to all headlines.
                self.textBindings = t.bindtags()
        #@nonl
        #@-node:ekr.20040723102245.2:createPermanentBindings
        #@+node:ekr.20040725050101:injectCallbacks
        def injectCallbacks(self):
            
            import leoNodes
            
            #@    << define tkinter callbacks to be injected in the position class >>
            #@+node:ekr.20040725050101.1:<< define tkinter callbacks to be injected in the position class >>
            # N.B. These vnode methods are entitled to know about details of the leoTkinterTree class.
            
            #@+others
            #@+node:ekr.20040725050101.6:onHyperLinkControlClick
            def OnHyperLinkControlClick (self,event):
                
                """Callback injected into position class."""
            
                #g.trace(self)
                try:
                    p = self ; c = p.c
                    if not g.doHook("hypercclick1",c=c,p=p,event=event):
                        # New in recycled nodes code:
                        # Call self.redraw to inhibit calls to setLabelState.
                        self.redraw()
                        c.beginUpdate()
                        c.selectVnode(p)
                        c.endUpdate()
                        c.frame.bodyCtrl.mark_set("insert","1.0")
                    g.doHook("hypercclick2",c=c,p=p,event=event)
                except:
                    g.es_event_exception("hypercclick")
                    
            onHyperLinkControlClick = OnHyperLinkControlClick
            #@nonl
            #@-node:ekr.20040725050101.6:onHyperLinkControlClick
            #@+node:ekr.20040725050101.8:onHyperLinkEnter
            def OnHyperLinkEnter (self,event=None):
                
                """Callback injected into position class."""
            
                # g.trace(self)
                try:
                    p = self ; c = p.c
                    if not g.doHook("hyperenter1",c=c,p=p,event=event):
                        if 0: # This works, and isn't very useful.
                            c.frame.bodyCtrl.tag_config(p.tagName,background="green")
                    g.doHook("hyperenter2",c=c,p=p,event=event)
                except:
                    g.es_event_exception("hyperenter")
                    
            onHyperLinkEnter = OnHyperLinkEnter
            #@nonl
            #@-node:ekr.20040725050101.8:onHyperLinkEnter
            #@+node:ekr.20040725050101.9:onHyperLinkLeave
            def OnHyperLinkLeave (self,event=None):
                
                """Callback injected into position class."""
            
                #g.trace(self)
                try:
                    p = self ; c = p.c
                    if not g.doHook("hyperleave1",c=c,p=p,event=event):
                        if 0: # This works, and isn't very useful.
                            c.frame.bodyCtrl.tag_config(p.tagName,background="white")
                    g.doHook("hyperleave2",c=c,p=p,event=event)
                except:
                    g.es_event_exception("hyperleave")
                    
            onHyperLinkLeave = OnHyperLinkLeave
            #@nonl
            #@-node:ekr.20040725050101.9:onHyperLinkLeave
            #@-others
            
            #@-node:ekr.20040725050101.1:<< define tkinter callbacks to be injected in the position class >>
            #@nl
        
            for f in (OnHyperLinkControlClick,OnHyperLinkEnter,OnHyperLinkLeave):
                
                g.funcToMethod(f,leoNodes.position)
        #@nonl
        #@-node:ekr.20040725050101:injectCallbacks
        #@-node:ekr.20040723173301.2:Birth...
        #@+node:ekr.20040723173919:Config & Measuring...
        #@+node:ekr.20040723173919.1:tree.getFont,setFont,setFontFromConfig
        def getFont (self):
        
            return self.font
                
        # Called by leoFontPanel.
        def setFont (self, font=None, fontName=None):
            
            if fontName:
                self.fontName = fontName
                self.font = tkFont.Font(font=fontName)
            else:
                self.fontName = None
                self.font = font
                
            self.setLineHeight(self.font)
            
        # Called by ctor and when config params are reloaded.
        def setFontFromConfig (self):
        
            font = g.app.config.getFontFromParams(
                "headline_text_font_family", "headline_text_font_size",
                "headline_text_font_slant",  "headline_text_font_weight",
                g.app.config.defaultTreeFontSize)
        
            self.setFont(font)
        #@nonl
        #@-node:ekr.20040723173919.1:tree.getFont,setFont,setFontFromConfig
        #@+node:ekr.20040723173919.2:headWidth & widthInPixels
        def headWidth(self,v):
        
            """Returns the proper width of the entry widget for the headline."""
        
            return max(10,5 + len(v.headString()))
            
        def widthInPixels(self,s):
        
            s = g.toEncodedString(s,g.app.tkEncoding)
            
            width = self.font.measure(s)
            
            # g.trace(width,s)
            
            return width
        #@nonl
        #@-node:ekr.20040723173919.2:headWidth & widthInPixels
        #@+node:ekr.20040723173919.3:setLineHeight
        def setLineHeight (self,font):
            
            try:
                metrics = font.metrics()
                linespace = metrics ["linespace"]
                self.line_height = linespace + 5 # Same as before for the default font on Windows.
                # print metrics
            except:
                self.line_height = self.default_line_height
                g.es("exception setting outline line height")
                g.es_exception()
        #@nonl
        #@-node:ekr.20040723173919.3:setLineHeight
        #@+node:ekr.20040723173919.4:setTreeColorsFromConfig
        def setTreeColorsFromConfig (self):
        
            bg = g.app.config.getWindowPref("outline_pane_background_color")
            if bg:
                try: self.canvas.configure(bg=bg)
                except: pass
        #@-node:ekr.20040723173919.4:setTreeColorsFromConfig
        #@-node:ekr.20040723173919:Config & Measuring...
        #@+node:ekr.20040726071801:Debugging...
        #@+node:ekr.20040725114147:setText
        def setText (self,t,s,tag="",isHeadline=True):
            
            """All changes to text widgets should come here."""
            
            if 0: # A good trace to have...
                if isHeadline:
                    g.trace(self.textAddr(t),tag,s)
                else:
                    g.trace(self.textAddr(t),tag,len(s))
                    
            state = t.cget("state")
            if state != "normal":
                t.configure(state="normal")
            t.delete("1.0","end")
            t.insert("end",s)
            if state != "normal":
                t.configure(state=state)
        #@-node:ekr.20040725114147:setText
        #@+node:ekr.20040724161900:textAddr
        def textAddr(self,t):
            
            """Return the address part of repr(Tk.Text)."""
            
            return repr(t)[-9:-1].lower()
        #@nonl
        #@-node:ekr.20040724161900:textAddr
        #@+node:ekr.20040726071801.1:traceIds (Not used)
        # Verbose tracing is much more useful than this because we can see the recent past.
        
        def traceIds (self,full=False):
            
            tree = self
            
            for dict,tag,flag in ((tree.ids,"ids",True),(tree.iconIds,"icon ids",False)):
                print '=' * 60
                print ; print "%s..." % tag
                keys = dict.keys()
                keys.sort()
                for key in keys:
                    p = tree.ids.get(key)
                    if p is None: # For lines.
                        print "%3d None" % key
                    else:
                        print "%3d" % key,p.headString()
                if flag and full:
                    print '-' * 40
                    values = dict.values()
                    values.sort()
                    seenValues = []
                    for value in values:
                        if value not in seenValues:
                            seenValues.append(value)
                            for item in dict.items():
                                key,val = item
                                if val and val == value:
                                    print "%3d" % key,val.headString()  
        #@nonl
        #@-node:ekr.20040726071801.1:traceIds (Not used)
        #@-node:ekr.20040726071801:Debugging...
        #@+node:ekr.20040723101121.2:Drawing...
        #@+node:ekr.20040723101121.4:drawBox
        def drawBox (self,p,x,y):
        
            tree = self ; canvas = self.canvas
            y += 7 # draw the box at x, y+7
            
            id = g.doHook("draw-outline-box",tree=tree,p=p,v=p.v,x=x,y=y)
                
            if id is None:
                iconname = g.choose(p.isExpanded(),"minusnode.gif", "plusnode.gif")
                image = self.getIconImage(iconname)
                id = self.newBox(p,x,y+self.lineyoffset,image)
                return id
            else:
                return id
        #@nonl
        #@-node:ekr.20040723101121.4:drawBox
        #@+node:ekr.20040723101121.24:drawClickBox
        def drawClickBox (self,p,y):
        
            canvas = self.canvas ; h = self.line_height
            
            # Define a slighly larger rect to catch clicks.
            id = self.newClickBox(p,0,y,1000,y+h-2)
            
            if 0: # A major change to the user interface.
                #@        << change the appearance of headlines >>
                #@+node:ekr.20040724072523:<< change the appearance of headlines >>
                
                # Define a slighly smaller rect to colorize.
                color_rect = self.canvas.create_rectangle(0,y,1000,y+h-4,tag="colorBox")
                self.canvas.itemconfig(color_rect,fill=defaultColor,outline=defaultColor)
                
                # Color the click box or the headline
                def enterRect(event,id=color_rect,p=p,t=self.lastText):
                    if 1: # Color or underline the headline
                        t2 = self.lastColoredText
                        if t2: # decolor the old headline.
                            if 1: # deunderline
                                t2.tag_delete('underline')
                            else: # decolor
                                t2.configure(background="white")
                        if t and p != self.editPosition():
                            if 1: # underline
                                t.tag_add('underline','1.0','end')
                                t.tag_configure('underline',underline=True)
                            else: # color
                                t.configure(background="LightSteelBlue1")
                            self.lastColoredText = t
                        else: self.lastColoredText = None
                    else: # Color the click box.
                        if self.lastClickFrameId:
                            self.canvas.itemconfig(self.lastClickFrameId,fill=defaultColor,outline=defaultColor)
                        self.lastClickFrameId = id
                        color = "LightSteelBlue1"
                        self.canvas.itemconfig(id,fill=color,outline=color)
                
                bind_id = self.canvas.tag_bind(click_rect, "<Enter>", enterRect) # , '+')
                self.tagBindings.append((click_rect,bind_id,"<Enter>"),)
                #@nonl
                #@-node:ekr.20040724072523:<< change the appearance of headlines >>
                #@nl
        #@nonl
        #@-node:ekr.20040723101121.24:drawClickBox
        #@+node:ekr.20040723101121.5:drawIcon
        def drawIcon(self,p,x=None,y=None):
            
            """Draws icon for position p at x,y, or at p.v.iconx,p.v.icony if x,y = None,None"""
        
            canvas = self.canvas
            #@    << compute x,y and iconVal >>
            #@+node:ekr.20040723101121.6:<< compute x,y and iconVal >>
            v = p.v
            
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
            val = v.iconVal = v.computeIcon()
            assert(0 <= val <= 15)
            #@nonl
            #@-node:ekr.20040723101121.6:<< compute x,y and iconVal >>
            #@nl
        
            if not g.doHook("draw-outline-icon",tree=self,p=p,v=p.v,x=x,y=y):
        
                # Get the image.
                imagename = "box%02d.GIF" % val
                image = self.getIconImage(imagename)
                id = self.newIcon(p,x,y+self.lineyoffset,image)
                
            return 0,self.icon_width # dummy icon height,width
        #@nonl
        #@-node:ekr.20040723101121.5:drawIcon
        #@+node:ekr.20040723190945:drawLine
        def drawLine (self,p,x1,y1,x2,y2):
            
            id = self.newLine(p,x1,y1,x2,y2)
            
            return id
        #@-node:ekr.20040723190945:drawLine
        #@+node:ekr.20040723101121.7:drawNode & force_draw_node (good trace)
        def drawNode(self,p,x,y):
            
            canvas = self.canvas
            
            data = g.doHook("draw-outline-node",tree=self,p=p,v=p.v,x=x,y=y)
            if data is not None: return data
            
            if self.trace and self.verbose:
                print # Helps format traces
        
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
        #@nonl
        #@+node:ekr.20040730043511:force_draw_node
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
        #@nonl
        #@-node:ekr.20040730043511:force_draw_node
        #@-node:ekr.20040723101121.7:drawNode & force_draw_node (good trace)
        #@+node:ekr.20040723101121.10:drawText
        def drawText(self,p,x,y):
            
            """draw text for position p at nominal coordinates x,y."""
            
            assert(p)
        
            c = self.c ; canvas = self.canvas
            h = self.line_height
            x += self.text_indent
            
            data = g.doHook("draw-outline-text-box",tree=self,p=p,v=p.v,x=x,y=y)
            if data is not None: return data
            
            t = self.newText(p,x,y+self.lineyoffset)
        
            if 0: # old, experimental code.
                #@        << highlight text widget on enter events >>
                #@+node:ekr.20040723101121.12:<< highlight text widget on enter events >>
                if 0: # Define a rect to colorize.
                
                    color_rect = self.canvas.create_rectangle(0,y,1000,y+h-4,tag="colorBox")
                    self.canvas.itemconfig(color_rect,fill="",outline="")
                
                    def enterRect(event,id=color_rect):
                        if self.lastClickFrameId:
                            self.canvas.itemconfig(self.lastClickFrameId,fill="",outline="")
                        self.lastClickFrameId = id
                        color = "LightSteelBlue1"
                        self.canvas.itemconfig(id,fill=color,outline=color)
                    
                    bind_enter = t.bind( '<Enter>', enterRect, '+' )
                    self.bindings.append((t,bind_enter,"<Enter>"),)
                    
                if 0: # Colorize only the headline.
                
                    def enterRect(event,p=p,t=t):
                        t2 = self.lastColoredText
                        if t2:
                            if 1: # deunderline
                                t2.tag_delete('underline')
                            else: # color
                                t2.configure(background="white")
                        if p == self.editPosition():
                            self.lastColoredText = None
                        else:
                            self.lastColoredText = t
                            if 1: # underline
                                t.tag_add('underline','1.0', 'end')
                                t.tag_configure('underline',underline = True)
                            else: #color
                                t.configure(background="LightSteelBlue1")
                    
                    bind_enter = t.bind( '<Enter>', enterRect, '+' )
                    self.bindings.append((t,bind_enter,"<Enter>"),)
                #@nonl
                #@-node:ekr.20040723101121.12:<< highlight text widget on enter events >>
                #@nl
           
            self.configureTextState(p)
        
            return self.line_height
        #@nonl
        #@-node:ekr.20040723101121.10:drawText
        #@+node:ekr.20040723101121.22:drawUserIcons
        def drawUserIcons(self,p,where,x,y):
            
            """Draw any icons specified by p.v.t.unknownAttributes["icons"]."""
            
            h,w = 0,0 ; t = p.v.t
            
            if not hasattr(t,"unknownAttributes"):
                return h,w
            
            iconsList = t.unknownAttributes.get("icons")
            if not iconsList:
                return h,w
            
            try:
                for dict in iconsList:
                    h2,w2 = self.drawUserIcon(p,where,x,y,w,dict)
                    h = max(h,h2) ; w += w2
            except:
                g.es_exception()
                
            # g.trace(where,h,w)
        
            return h,w
        #@nonl
        #@-node:ekr.20040723101121.22:drawUserIcons
        #@+node:ekr.20040723101121.17:drawUserIcon
        def drawUserIcon (self,p,where,x,y,w2,dict):
            
            h,w = 0,0
        
            if where != dict.get("where","beforeHeadline"):
                return h,w
                
            # g.trace(where,x,y,dict)
            
            #@    << set offsets and pads >>
            #@+node:ekr.20040723101121.18:<< set offsets and pads >>
            xoffset = dict.get("xoffset")
            try:    xoffset = int(xoffset)
            except: xoffset = 0
            
            yoffset = dict.get("yoffset")
            try:    yoffset = int(yoffset)
            except: yoffset = 0
            
            xpad = dict.get("xpad")
            try:    xpad = int(xpad)
            except: xpad = 0
            
            ypad = dict.get("ypad")
            try:    ypad = int(ypad)
            except: ypad = 0
            #@nonl
            #@-node:ekr.20040723101121.18:<< set offsets and pads >>
            #@nl
            type = dict.get("type")
            if type == "icon":
                s = dict.get("icon")
                #@        << draw the icon in string s >>
                #@+node:ekr.20040723101121.19:<< draw the icon in string s >>
                pass
                #@nonl
                #@-node:ekr.20040723101121.19:<< draw the icon in string s >>
                #@nl
            elif type == "file":
                file = dict.get("file")
                #@        << draw the icon at file >>
                #@+node:ekr.20040723101121.21:<< draw the icon at file >>
                try:
                    image = self.iconimages[file]
                    # Get the image from the cache if possible.
                except KeyError:
                    try:
                        fullname = g.os_path_join(g.app.loadDir,"..","Icons",file)
                        fullname = g.os_path_normpath(fullname)
                        image = Tk.PhotoImage(master=self.canvas,file=fullname)
                        self.iconimages[fullname] = image
                    except:
                        #g.es("Exception loading: " + fullname)
                        #g.es_exception()
                        image = None
                        
                if image:
                    id = self.canvas.create_image(x+xoffset+w2,y+yoffset,anchor="nw",image=image,tag="userIcon")
                    self.ids[id] = p
                
                    assert(id not in self.visibleIcons)
                    self.visibleUserIcons.append(id)
                
                    h = image.height() + yoffset + ypad
                    w = image.width()  + xoffset + xpad
                #@-node:ekr.20040723101121.21:<< draw the icon at file >>
                #@nl
            elif type == "url":
                url = dict.get("url")
                #@        << draw the icon at url >>
                #@+node:ekr.20040723101121.20:<< draw the icon at url >>
                pass
                #@nonl
                #@-node:ekr.20040723101121.20:<< draw the icon at url >>
                #@nl
                
            # Allow user to specify height, width explicitly.
            h = dict.get("height",h)
            w = dict.get("width",w)
        
            return h,w
        #@nonl
        #@-node:ekr.20040723101121.17:drawUserIcon
        #@+node:ekr.20040723101121.13:drawTopTree
        def drawTopTree (self):
            
            """Draws the top-level tree, taking into account the hoist state."""
            
            c = self.c ; canvas = self.canvas
            
            if 0:
                try: self.redrawCount += 1
                except: self.radrawCount = 1
                g.trace(self.redrawCount)
                
            # g.trace("begin %s" % self.getTextStats())
            self.redrawing = True
            
            # Recycle all widgets.
            self.recycleWidgets()
            # Clear all ids so invisible id's don't confuse eventToPosition & findPositionWithIconId
            self.ids = {}
            self.iconIds = {}
            self.generation += 1
            self.drag_p = None # Disable drags across redraws.
            self.dragging = False
            if self.trace:
                print ; print
                g.trace("**** generation: %3d ***" % self.generation)
            
            if c.hoistStack:
                p,junk = c.hoistStack[-1]
                self.drawTree(p.copy(),self.root_left,self.root_top,0,0,hoistFlag=True)
            else:
                self.drawTree(c.rootPosition(),self.root_left,self.root_top,0,0)
            
            canvas.lower("lines")  # Lowest.
            canvas.lift("textBox") # Not the Tk.Text widget: it should be low.
            canvas.lift("userIcon")
            canvas.lift("plusBox") 
            canvas.lift("clickBox")
            canvas.lift("iconBox") # Higest.
        
            # g.trace("end   %s" % self.getTextStats())
            self.redrawing = False
        #@nonl
        #@-node:ekr.20040723101121.13:drawTopTree
        #@+node:ekr.20040723101121.15:drawTree
        def drawTree(self,p,x,y,h,level,hoistFlag=False):
        
            tree = self ; v = p.v
            yfirst = ylast = y
            h1 = None
            
            data = g.doHook("draw-sub-outline",tree=tree,p=p,v=v,x=x,y=y,h=h,level=level,hoistFlag=hoistFlag)
            if data is not None: return data
            
            p = p.copy() # Make _sure_ we never change the caller's position.
            
            while p: # Do not use iterator.
                h,indent = self.drawNode(p,x,y)
                if h1 is None: h1 = h
                y += h ; ylast = y
                if p.isExpanded() and p.hasFirstChild():
                    # Must make an additional copy here by calling firstChild.
                    y = self.drawTree(p.firstChild(),x+indent,y,h,level+1)
                if hoistFlag: break
                else:         p = p.next()
                
            # Draw the vertical line.
            if level==0: # Special case to get exposed first line exactly right.
                self.drawLine(None,x,yfirst+(h1-1)/2,x,ylast+self.hline_y-h)
            else:
                self.drawLine(None,x,yfirst-h1/2-1,x,ylast+self.hline_y-h)
            return y
        #@nonl
        #@-node:ekr.20040723101121.15:drawTree
        #@+node:ekr.20040726072127:Top level...
        #@+node:ekr.20040723141518.1:tree.redraw
        # Calling redraw inside c.beginUpdate()/c.endUpdate() does nothing.
        # This _is_ useful when a flag is passed to c.endUpdate.
        
        def redraw (self,event=None):
            
            # g.trace(self.updateCount,self.redrawScheduled)
            
            if self.updateCount == 0 and not self.redrawScheduled:
                self.redrawScheduled = True
                self.canvas.after_idle(self.idle_redraw)
        #@nonl
        #@-node:ekr.20040723141518.1:tree.redraw
        #@+node:ekr.20040723141518.2:tkTree.redrawAfterException
        #@+at 
        #@nonl
        # This is called only from doCommand.  The implicit assumption is that 
        # doCommand itself is not contained in a beginUpdate/endUpdate pair.
        #@-at
        #@@c
        
        def redrawAfterException (self):
            
            """Make sure drawing is enabled following an exception."""
                
            if not self.redrawScheduled:
                self.redrawScheduled = True
                self.canvas.after_idle(self.idle_redraw)
                self.updateCount = 0 # would not work if we are in a beginUpdate/endUpdate pair.
        #@nonl
        #@-node:ekr.20040723141518.2:tkTree.redrawAfterException
        #@+node:ekr.20040723141518.3:force_redraw
        # Schedules a redraw even if inside beginUpdate/endUpdate
        def force_redraw (self):
            
            if self.trace: g.trace(self.redrawScheduled)
            # import traceback ; traceback.print_stack()
        
            if not self.redrawScheduled:
                self.redrawScheduled = True
                self.canvas.after_idle(self.idle_redraw)
        #@nonl
        #@-node:ekr.20040723141518.3:force_redraw
        #@+node:ekr.20040723141518.4:redraw_now
        # Redraws immediately: used by Find so a redraw doesn't mess up selections in headlines.
        
        def redraw_now (self,scroll=True):
            
            # g.trace()
            
            # Bug fix: 4/24/04: cancel any pending redraw "by hand".
            # Make _sure_ that no other redraws take place after this.
            self.disableRedraw = True
            self.canvas.update_idletasks()
            self.disableRedraw = False
                
            # Now do the actual redraw.
            self.idle_redraw(scroll=scroll)
        #@nonl
        #@-node:ekr.20040723141518.4:redraw_now
        #@+node:ekr.20040723141518.5:idle_redraw
        def idle_redraw (self,scroll=True):
            
            c = self.c ; frame = c.frame
        
            self.redrawScheduled = False # Always do this here.
        
            #@    << return if disabled, or quitting or dragging >>
            #@+node:ekr.20040723141518.6:<< return if disabled, or quitting or dragging >>
            if self.disableRedraw:
                # We have been called as the result of an update_idletasks in the log pane.
                # Don't do anything now.
                return
            
            if frame not in g.app.windowList or g.app.quitting:
                # g.trace("no frame")
                return
            
            if self.drag_p:
                # g.trace("dragging",self.drag_p)
                return
            #@-node:ekr.20040723141518.6:<< return if disabled, or quitting or dragging >>
            #@nl
        
            # g.print_bindings("canvas",self.canvas)
        
            self.expandAllAncestors(c.currentPosition())
        
            oldcursor = self.canvas['cursor']
            self.canvas['cursor'] = "watch"
        
            if not g.doHook("redraw-entire-outline",c=self.c):
                c.setTopVnode(None)
                self.setVisibleAreaToFullCanvas()
                self.drawTopTree()
                # Set up the scroll region after the tree has been redrawn.
                x0, y0, x1, y1 = self.canvas.bbox("all")
                self.canvas.configure(scrollregion=(0, 0, x1, y1))
                # Do a scrolling operation after the scrollbar is redrawn
                if scroll:
                    self.canvas.after_idle(self.idle_scrollTo)
                if 0:
                    self.redrawCount += 1
                    print "idle_redraw allocated:",self.redrawCount
            g.doHook("after-redraw-outline",c=self.c)
        
            self.canvas['cursor'] = oldcursor
        #@nonl
        #@-node:ekr.20040723141518.5:idle_redraw
        #@+node:ekr.20040723141518.8:idle_second_redraw
        def idle_second_redraw (self):
            
            c = self.c
            
            g.trace()
                
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
                print "idle_second_redraw allocated:",self.redrawCount
        #@nonl
        #@-node:ekr.20040723141518.8:idle_second_redraw
        #@-node:ekr.20040726072127:Top level...
        #@+node:ekr.20040723102245:Unchanged...
        #@+node:ekr.20040723101121.23:inVisibleArea & inExpandedVisibleArea
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
        #@nonl
        #@-node:ekr.20040723101121.23:inVisibleArea & inExpandedVisibleArea
        #@+node:ekr.20040723101121.25:getIconImage
        def getIconImage (self, name):
        
            # Return the image from the cache if possible.
            if self.iconimages.has_key(name):
                return self.iconimages[name]
                
            try:
                fullname = g.os_path_join(g.app.loadDir,"..","Icons",name)
                fullname = g.os_path_normpath(fullname)
                image = Tk.PhotoImage(master=self.canvas,file=fullname)
                self.iconimages[name] = image
                return image
            except:
                g.es("Exception loading: " + fullname)
                g.es_exception()
                return None
        #@nonl
        #@-node:ekr.20040723101121.25:getIconImage
        #@+node:ekr.20040723101121.26:idle_scrollTo
        def idle_scrollTo(self,p=None):
        
            """Scrolls the canvas so that v is in view.
            
            This is done at idle time after a redraw so that treeBar.get() will return proper values."""
        
            c = self.c ; frame = c.frame
            if not p: p = self.c.currentPosition()
            if not p: p = self.c.rootPosition() # 4/8/04.
            try:
                last = p.lastVisible()
                nextToLast = last.visBack()
                h1 = self.yoffset(p)
                h2 = self.yoffset(last)
                #@        << compute approximate line height >>
                #@+node:ekr.20040723101121.27:<< compute approximate line height >>
                if nextToLast: # 2/2/03: compute approximate line height.
                    lineHeight = h2 - self.yoffset(nextToLast)
                else:
                    lineHeight = 20 # A reasonable default.
                #@nonl
                #@-node:ekr.20040723101121.27:<< compute approximate line height >>
                #@nl
                #@        << Compute the fractions to scroll down/up >>
                #@+node:ekr.20040723101121.28:<< Compute the fractions to scroll down/up >>
                data = frame.treeBar.get()
                try: lo, hi = data
                except: lo,hi = 0.0,1.0
                if h2 > 0.1:
                    frac = float(h1)/float(h2) # For scrolling down.
                    frac2 = float(h1+lineHeight/2)/float(h2) # For scrolling up.
                    frac2 = frac2 - (hi - lo)
                else:
                    frac = frac2 = 0.0 # probably any value would work here.
                    
                frac =  max(min(frac,1.0),0.0)
                frac2 = max(min(frac2,1.0),0.0)
                #@nonl
                #@-node:ekr.20040723101121.28:<< Compute the fractions to scroll down/up >>
                #@nl
                if frac <= lo:
                    if self.prevMoveToFrac != frac:
                        self.prevMoveToFrac = frac
                        self.canvas.yview("moveto",frac)
                elif frac2 + (hi - lo) >= hi:
                    if self.prevMoveToFrac != frac2:
                        self.prevMoveToFrac = frac2
                        self.canvas.yview("moveto",frac2)
        
                if self.allocateOnlyVisibleNodes:
                    self.canvas.after_idle(self.idle_second_redraw)
                    
                c.setTopVnode(p) # 1/30/04: remember a pseudo "top" node.
                # g.trace("%3d %3d %1.3f %1.3f %1.3f %1.3f" % (h1,h2,frac,frac2,lo,hi))
            except:
                g.es_exception()
        #@nonl
        #@-node:ekr.20040723101121.26:idle_scrollTo
        #@+node:ekr.20040723101121.29:numberOfVisibleNodes
        def numberOfVisibleNodes(self):
            
            n = 0 ; p = self.c.rootPosition()
            while p:
                n += 1
                p.moveToVisNext()
            return n
        #@nonl
        #@-node:ekr.20040723101121.29:numberOfVisibleNodes
        #@+node:ekr.20040723101121.30:scrollTo
        def scrollTo (self,p):
            
            def scrollToCallback(event=None,self=self,p=p):
                g.trace(event,self,p)
                self.idle_scrollTo(p)
            
            self.canvas.after_idle(scrollToCallback)
        #@nonl
        #@-node:ekr.20040723101121.30:scrollTo
        #@+node:ekr.20040723101121.31:yoffset
        #@+at 
        #@nonl
        # We can't just return icony because the tree hasn't been redrawn 
        # yet.  For the same reason we can't rely on any TK canvas methods 
        # here.
        #@-at
        #@@c
        
        def yoffset(self, v1):
        
            # if not v1.isVisible(): print "yoffset not visible:",v1
            root = self.c.rootPosition()
            h, flag = self.yoffsetTree(root,v1)
            # flag can be False during initialization.
            # if not flag: print "yoffset fails:",h,v1
            return h
        
        # Returns the visible height of the tree and all sibling trees, stopping at p1
        
        def yoffsetTree(self,p,p1):
        
            h = 0
            p = p.copy()
            for p in p.siblings_iter():
                # print "yoffsetTree:", p
                if p == p1:
                    return h, True
                h += self.line_height
                if p.isExpanded() and p.hasChildren():
                    child = p.firstChild()
                    h2, flag = self.yoffsetTree(child,p1)
                    h += h2
                    if flag: return h, True
            
            return h, False
        #@nonl
        #@-node:ekr.20040723101121.31:yoffset
        #@-node:ekr.20040723102245:Unchanged...
        #@-node:ekr.20040723101121.2:Drawing...
        #@+node:ekr.20040723103515:Event handlers...
        #@+node:ekr.20040725060102:checkWidgetList
        def checkWidgetList (self,tag):
            
            return True # This will fail when the headline actually changes!
            
            for t in self.visibleText:
                
                p = t.leo_position
                if p:
                    s = t.get("1.0","end").strip()
                    h = p.headString().strip()
                    
                    if h != s:
                        self.dumpWidgetList(tag)
                        return False
                else:
                    self.dumpWidgetList(tag)
                    return False
                    
            return True
        #@nonl
        #@-node:ekr.20040725060102:checkWidgetList
        #@+node:ekr.20040725055657:dumpWidgetList
        def dumpWidgetList (self,tag):
            
            print
            print "checkWidgetList: %s" % tag
            
            for t in self.visibleText:
                
                p = t.leo_position
                if p:
                    s = t.get("1.0","end").strip()
                    h = p.headString().strip()
            
                    addr = self.textAddr(t)
                    print "p:",addr,h
                    if h != s:
                        print "t:",'*' * len(addr),s
                else:
                    print "t.leo_position == None",t
        #@nonl
        #@-node:ekr.20040725055657:dumpWidgetList
        #@+node:ekr.20040723141142:eventToPosition
        def eventToPosition (self,event):
        
            canvas = self.canvas
            x,y = event.x,event.y
            # 7/28/04: Not doing this translation was the real bug.
            x = canvas.canvasx(x) 
            y = canvas.canvasy(y)
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
                if not theId: return None
                p = self.ids.get(theId)
                # g.trace("was vertical line",p)
            
            if self.trace:
                if p:
                    w = self.findEditWidget(p)
                    g.trace("%3d %3d %3d %d" % (theId,x,y,id(w)),p.headString())
                else:
                    g.trace("%3d %3d %3d" % (theId,x,y),None)
                
            if p: return p.copy() # Make _sure_ nobody changes this table!
            else: return None
        #@nonl
        #@-node:ekr.20040723141142:eventToPosition
        #@+node:ekr.20040724125005:edit_text
        def edit_text (self,p):
            
            if self.editPosition:
                return self.findEditWidget(p,tag="tree:edit_text")
            else:
                return None
        #@nonl
        #@-node:ekr.20040724125005:edit_text
        #@+node:ekr.20040724102927:findEditWidget
        # Search the widget list for widget t with t.leo_position == p.
        
        def findEditWidget (self,p,tag=""):
            
            """Return the Tk.Text item corresponding to p."""
        
            c = self.c
            
            if c:
                # New in 4.2: the dictionary is a list of pairs(p,v)
                pairs = self.visibleText.get(p.v,[])
                for p2,t2,id2 in pairs:
                    assert t2.leo_window_id == id2
                    assert t2.leo_position == p2
                    if p.equal(p2):
                        # g.trace("found",t2)
                        return t2
                return None
            else:
                return None
                
            if 0:
                #@        << buggy code >>
                #@+node:ekr.20040728070808:<< buggy code >>
                
                if not p: return None
                
                n = len(self.visibleText)
                
                for i in xrange(n):
                    t = self.visibleText[i]
                    assert(t.leo_position)
                    if t.leo_position == p:
                        if t.leo_generation != self.generation:
                            g.trace("***** generation mismatch *****")
                            return None
                        if 1: # Report any other potential matches.  Might cause problems.
                            count = 0; i += 1
                            for j in xrange(i+1,n):
                                if self.visibleText[j].leo_position == p:
                                    count += 1
                            if count:
                                g.trace("***** %d other matches for p *****" % (count,p.headString()))
                        g.trace(self.textAddr(t),p)
                        return t
                
                return None
                #@nonl
                #@-node:ekr.20040728070808:<< buggy code >>
                #@nl
        #@nonl
        #@-node:ekr.20040724102927:findEditWidget
        #@+node:ekr.20040723142710.3:Click Box...
        #@+node:ekr.20040723104637:onClickBoxClick
        def onClickBoxClick (self,event):
            
            c = self.c ; gui = g.app.gui
            
            if self.trace: g.trace()
            
            p = self.eventToPosition(event)
            
            if p:
                if p.isExpanded(): p.contract()
                else:              p.expand()
            
                self.active = True
                # Schedule the redraw _before_ calling select.
                # This disables any call that would configure old text widgets.
                self.redraw()
                self.select(p)
                g.app.findFrame.handleUserClick(p)
                gui.set_focus(c,c.frame.bodyCtrl)
        #@nonl
        #@-node:ekr.20040723104637:onClickBoxClick
        #@-node:ekr.20040723142710.3:Click Box...
        #@+node:ekr.20040723142710:Icon Box...
        #@+node:ekr.20040723104427.33:onIconBoxClick
        def onIconBoxClick (self,event):
            
            c = self.c ; gui = g.app.gui
            tree = self ; canvas = tree.canvas
            
            if self.trace: g.trace()
            
            p = self.eventToPosition(event)
            if not p: return
        
            if event:
                self.onDrag(event)
        
            tree.select(p)
            g.app.findFrame.handleUserClick(p) # 4/3/04
            return "break" # disable expanded box handling.
        #@nonl
        #@-node:ekr.20040723104427.33:onIconBoxClick
        #@+node:ekr.20040723142710.1:onIconBoxDoubleClick
        def onIconBoxDoubleClick (self,event):
            
            c = self.c
        
            p = self.eventToPosition(event)
            if not p: return
            
            try:
                if not g.doHook("icondclick1",c=c,p=p,event=event):
                    self.OnIconDoubleClick(p) # Call the method in the base class.
                g.doHook("icondclick2",c=c,p=p,event=event)
            except:
                g.es_event_exception("icondclick")
        #@-node:ekr.20040723142710.1:onIconBoxDoubleClick
        #@+node:ekr.20040723142710.2:onIconBoxRightClick
        def onIconBoxRightClick (self,event):
        
            p = self.eventToPosition(event)
            
            if p:
                self.select(p)
                g.app.findFrame.handleUserClick(p)
        
            return "break" # disable expanded box handling.
        #@nonl
        #@-node:ekr.20040723142710.2:onIconBoxRightClick
        #@-node:ekr.20040723142710:Icon Box...
        #@+node:ekr.20040723142845:Text Box...
        #@+node:ekr.20040724083359:configureTextState
        def configureTextState (self,p):
            
            c = self.c
            
            if not p:
                g.trace("Can't happen")
                return
            
            if p == c.currentPosition():
                if p == self.editPosition():
                    self.setNormalLabelState(p)
                else:
                    self.setDisabledLabelState(p) # selected, disabled
            else:
                self.setUnselectedLabelState(p) # unselected
        #@nonl
        #@-node:ekr.20040724083359:configureTextState
        #@+node:ekr.20040723104427.5:onCtontrolT
        # This works around an apparent Tk bug.
        
        def onControlT (self,event=None):
        
            # If we don't inhibit further processing the Tx.Text widget switches characters!
            return "break"
        #@nonl
        #@-node:ekr.20040723104427.5:onCtontrolT
        #@+node:ekr.20040723142710.4:onHeadlineClick
        def onHeadlineClick (self,event):
            
            c = self.c ; w = event.widget
            
            try:
                p = w.leo_position
            except AttributeError:
                return "continue"
                
            if self.trace: g.trace(p)
            
            try:
                if not g.doHook("headclick1",c=c,p=p,event=event):
                    self.OnActivate(p)
                g.doHook("headclick2",c=c,p=p,event=event)
            except:
                g.es_event_exception("headclick")
                
            return "continue"
        #@nonl
        #@-node:ekr.20040723142710.4:onHeadlineClick
        #@+node:ekr.20040723142710.6:onHeadlineKey
        def onHeadlineKey (self,event):
            
            """Handle a key event in a headline."""
            
            w = event.widget ; ch = event.char
        
            try:
                p = w.leo_position
            except AttributeError:
                return "continue"
        
            self.c.frame.bodyCtrl.after_idle(self.idle_head_key,p,ch)
            
            # return "continue"
        #@nonl
        #@-node:ekr.20040723142710.6:onHeadlineKey
        #@+node:ekr.20040723142710.5:onHeadlineRightClick
        def onHeadlineRightClick (self,event):
        
            c = self.c ; w = event.widget
            
            try:
                p = w.leo_position
            except AttributeError:
                return "continue"
        
            try:
                if not g.doHook("headrclick1",c=c,p=p,event=event):
                    self.OnActivate(p)
                    self.OnPopup(p,event)
                g.doHook("headrclick2",c=c,p=p,event=event)
            except:
                g.es_event_exception("headrclick")
                
            return "continue"
        #@nonl
        #@-node:ekr.20040723142710.5:onHeadlineRightClick
        #@+node:ekr.20040724100003:virtual event handlers: called from core
        #@+node:ekr.20040723104427.18:idle_head_key
        def idle_head_key (self,p,ch=None):
            
            """Update headline text at idle time."""
            
            c = self.c
        
            if not p or p != c.currentPosition():
                return "break"
                
            edit_text = self.edit_text(p)
            index = edit_text.index("insert")
        
            if g.doHook("headkey1",c=c,p=p,ch=ch):
                return "break" # The hook claims to have handled the event.
                
            #@    << set head to vnode text >>
            #@+node:ekr.20040723104427.19:<< set head to vnode text >>
            head = p.headString()
            if head == None:
                head = u""
            head = g.toUnicode(head,"utf-8")
            #@nonl
            #@-node:ekr.20040723104427.19:<< set head to vnode text >>
            #@nl
            done = ch in ('\r','\n')
            if done:
                #@        << set the widget text to head >>
                #@+node:ekr.20040723104427.20:<< set the widget text to head >>
                self.setText(edit_text,head,tag="idle_head_key")
                edit_text.mark_set("insert",index)
                #@nonl
                #@-node:ekr.20040723104427.20:<< set the widget text to head >>
                #@nl
            #@    << set s to the widget text >>
            #@+node:ekr.20040723104427.21:<< set s to the widget text >>
            s = edit_text.get("1.0","end")
            
            # Don't truncate if the user is hitting return.
            # That should just end editing.
            if 1:
                # Truncate headline text to workaround Tk problems...
                # Another kludge: remove one or two trailing newlines before warning of truncation.
                if s and s[-1] == '\n': s = s[:-1]
                if s and s[-1] == '\n': s = s[:-1]
                i = s.find('\n')
                if i > -1:
                    # g.trace(i,len(s),repr(s))
                    g.es("Truncating headline to one line",color="blue")
                    s = s[:i]
                if len(s) > 250:
                    g.es("Truncating headline to 250 characters",color="blue")
                    s = s[:250]
            
            s = g.toUnicode(s,g.app.tkEncoding)
            
            if not s:
                s = u""
                
            if 0: # 6/10/04: No longer needed.  This was stressing Tk needlessly.
                s = s.replace('\n','')
                s = s.replace('\r','')
            #@nonl
            #@-node:ekr.20040723104427.21:<< set s to the widget text >>
            #@nl
            changed = s != head
            if changed:
                c.undoer.setUndoParams("Change Headline",p,newText=s,oldText=head)
                #@        << update p >>
                #@+node:ekr.20040723104427.22:<< update p >>
                c.beginUpdate()
                if 1: # update...
                    # Update changed bit.
                    if not c.changed:
                        c.setChanged(True)
                    # Update all dirty bits.
                    # Bug fix 8/2/04: must call p.setDirty even if p is dirty!
                    p.setDirty()
                    # Update p.
                    p.initHeadString(s)
                    self.setText(edit_text,s,tag="idle_head_key2")
                    edit_text.mark_set("insert",index)
                c.endUpdate(False) # do not redraw now.
                #@nonl
                #@-node:ekr.20040723104427.22:<< update p >>
                #@nl
            if done or changed:
                #@        << reconfigure p and all nodes joined to p >>
                #@+node:ekr.20040723104427.23:<< reconfigure p and all nodes joined to p >>
                # Reconfigure p's headline.
                if done:
                    self.setDisabledLabelState(p)
                
                edit_text.configure(width=self.headWidth(p))
                #@nonl
                #@-node:ekr.20040723104427.23:<< reconfigure p and all nodes joined to p >>
                #@nl
                #@        << update the screen >>
                #@+node:ekr.20040723104427.24:<< update the screen >>
                if done:
                    # g.trace("done")
                    c.beginUpdate()
                    self.endEditLabel()
                    c.endUpdate()
                
                elif changed:
                    # g.trace("changed")
                    # Update p immediately.  Joined nodes are redrawn later by endEditLabel.
                    # Redrawing the whole screen now messes up the cursor in the headline.
                    self.drawIcon(p) # just redraw the icon.
                #@nonl
                #@-node:ekr.20040723104427.24:<< update the screen >>
                #@nl
        
            g.doHook("headkey2",c=c,p=p,ch=ch)
            return "break"
        #@nonl
        #@-node:ekr.20040723104427.18:idle_head_key
        #@+node:ekr.20040723104427.16:onHeadChanged
        # The <Key> event generates the event before the headline text is changed!
        # We register an idle-event handler to do the work later.
        
        def onHeadChanged (self,p):
        
            """Handle a change to headline text."""
            
            g.trace()
            
            self.c.frame.bodyCtrl.after_idle(self.idle_head_key,p)
        #@nonl
        #@-node:ekr.20040723104427.16:onHeadChanged
        #@-node:ekr.20040724100003:virtual event handlers: called from core
        #@-node:ekr.20040723142845:Text Box...
        #@+node:ekr.20040723104427.8:Dragging
        #@+node:ekr.20040723104427.9:tree.onContinueDrag
        def onContinueDrag(self,event):
            
            canvas = self.canvas ; frame = self.c.frame
        
            p = self.drag_p
            if not p: return
        
            try:
                if event:
                    x,y = event.x,event.y
                else:
                    x,y = frame.top.winfo_pointerx(),frame.top.winfo_pointery()
                    # Stop the scrolling if we go outside the entire window.
                    if x == -1 or y == -1: return 
        
                if self.dragging: # This gets cleared by onEndDrag()
                    #@            << scroll the canvas as needed >>
                    #@+node:ekr.20040723104427.11:<< scroll the canvas as needed >>
                    # Scroll the screen up or down one line if the cursor (y) is outside the canvas.
                    h = canvas.winfo_height()
                    
                    if y < 0 or y > h:
                        lo, hi = frame.treeBar.get()
                        n = self.savedNumberOfVisibleNodes
                        line_frac = 1.0 / float(n)
                        frac = g.choose(y < 0, lo - line_frac, lo + line_frac)
                        frac = min(frac,1.0)
                        frac = max(frac,0.0)
                        # g.es("lo,hi,frac:",lo,hi,frac)
                        canvas.yview("moveto", frac)
                        
                        # Queue up another event to keep scrolling while the cursor is outside the canvas.
                        lo, hi = frame.treeBar.get()
                        if (y < 0 and lo > 0.1) or (y > h and hi < 0.9):
                            canvas.after_idle(self.onContinueDrag,None) # Don't propagate the event.
                    #@nonl
                    #@-node:ekr.20040723104427.11:<< scroll the canvas as needed >>
                    #@nl
            except:
                g.es_event_exception("continue drag")
        #@nonl
        #@-node:ekr.20040723104427.9:tree.onContinueDrag
        #@+node:ekr.20040723104427.12:tree.onDrag
        # This precomputes numberOfVisibleNodes(), a significant optimization.
        # We also indicate where findPositionWithIconId() should start looking for tree id's.
        
        def onDrag(self,event):
        
            # Note: "drag" hooks handled by vnode callback routine.
            
            c = self.c ; canvas = self.canvas
            if not event: return
         
            if not self.dragging:
                assert(not self.drag_p)
                x = canvas.canvasx(event.x)
                y = canvas.canvasy(event.y)
                id = canvas.find_closest(x,y)
                # id = canvas.find_overlapping(canvas_x,canvas_y,canvas_x,canvas_y)
                if id is None: return
                try: id = id[0]
                except: pass
                p = self.ids.get(id)
                if not p: return
                self.drag_p = p.copy()
                self.dragging = True
                if self.trace: g.trace("*** start drag ***",id,self.drag_p.headString())
                windowPref = g.app.config.getBoolWindowPref
                # Only do this once: greatly speeds drags.
                self.savedNumberOfVisibleNodes = self.numberOfVisibleNodes()
                if windowPref("allow_clone_drags"):
                    self.controlDrag = c.frame.controlKeyIsDown
                    if windowPref("look_for_control_drag_on_mouse_down"):
                        if windowPref("enable_drag_messages"):
                            if self.controlDrag:
                                g.es("dragged node will be cloned")
                            else:
                                g.es("dragged node will be moved")
                else: self.controlDrag = False
                self.canvas['cursor'] = "hand2" # "center_ptr"
        
            self.onContinueDrag(event)
        #@nonl
        #@-node:ekr.20040723104427.12:tree.onDrag
        #@+node:ekr.20040723104427.13:tree.onEndDrag
        def onEndDrag(self,event):
            
            """Tree end-of-drag handler called from vnode event handler."""
            
            c = self.c ; canvas = self.canvas ; config = g.app.config
            if not self.dragging: return
            p = self.drag_p
            if not p: return
            
            if event:
                
                #@        << set vdrag, childFlag >>
                #@+node:ekr.20040723104427.14:<< set vdrag, childFlag >>
                x,y = event.x,event.y
                canvas_x = canvas.canvasx(x)
                canvas_y = canvas.canvasy(y)
                
                id = self.canvas.find_closest(canvas_x,canvas_y)
                # id = self.canvas.find_overlapping(canvas_x,canvas_y,canvas_x,canvas_y)
                
                vdrag = self.findPositionWithIconId(id)
                childFlag = vdrag and vdrag.hasChildren() and vdrag.isExpanded()
                #@nonl
                #@-node:ekr.20040723104427.14:<< set vdrag, childFlag >>
                #@nl
                if config.getBoolWindowPref("allow_clone_drags"):
                    if not config.getBoolWindowPref("look_for_control_drag_on_mouse_down"):
                        self.controlDrag = c.frame.controlKeyIsDown
        
                if vdrag and vdrag.v.t != p.v.t: # 6/22/04: Disallow drag to joined node.
                    if self.trace: g.trace("*** end drag   ***",id,x,y,p.headString(),vdrag.headString())
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
                else:
                    if self.trace: g.trace("Cancel drag")
            
            # Reset the old cursor by brute force.
            self.canvas['cursor'] = "arrow"
            self.dragging = False
            self.drag_p = None
        #@nonl
        #@-node:ekr.20040723104427.13:tree.onEndDrag
        #@-node:ekr.20040723104427.8:Dragging
        #@+node:ekr.20040723104427.2:OnActivate
        def OnActivate (self,p,event=None):
        
            try:
                c = self.c ; gui = g.app.gui
                #@        << activate this window >>
                #@+node:ekr.20040723104427.3:<< activate this window >>
                current = c.currentPosition()
                
                if p == current:
                    # g.trace("is current")
                    if self.active:
                        self.editLabel(p)
                    else:
                        # self.undimEditLabel()
                        gui.set_focus(c,self.canvas) # Essential for proper editing.
                else:
                    # g.trace("not current")
                    self.select(p)
                    g.app.findFrame.handleUserClick(p) # 4/3/04
                    if p.v.t.insertSpot != None: # 9/1/02
                        c.frame.bodyCtrl.mark_set("insert",p.v.t.insertSpot)
                        c.frame.bodyCtrl.see(p.v.t.insertSpot)
                    else:
                        c.frame.bodyCtrl.mark_set("insert","1.0")
                    gui.set_focus(c,c.frame.bodyCtrl)
                
                self.active = True
                #@nonl
                #@-node:ekr.20040723104427.3:<< activate this window >>
                #@nl
            except:
                g.es_event_exception("activate tree")
        #@nonl
        #@-node:ekr.20040723104427.2:OnActivate
        #@+node:ekr.20040723104427.1:Unchanged Event handers
        #@+at 
        #@nonl
        # Important note: most hooks are created in the vnode callback 
        # routines, _not_ here.
        #@-at
        #@+node:ekr.20040723104427.6:tree.OnDeactivate (caused double-click problem)
        def OnDeactivate (self,event=None):
            
            """Deactivate the tree pane, dimming any headline being edited."""
        
            tree = self ; c = self.c
            focus = g.app.gui.get_focus(c.frame)
        
            # Bug fix: 7/13/03: Only do this as needed.
            # Doing this on every click would interfere with the double-clicking.
            if not c.frame.log.hasFocus() and focus != c.frame.bodyCtrl:
                try:
                    if self.trace: g.trace(focus)
                    tree.endEditLabel()
                    tree.dimEditLabel()
                except:
                    g.es_event_exception("deactivate tree")
        #@nonl
        #@-node:ekr.20040723104427.6:tree.OnDeactivate (caused double-click problem)
        #@+node:ekr.20040723104427.7:tree.findVnodeWithIconId
        def findPositionWithIconId (self,id):
            
            # Due to an old bug, id may be a tuple.
            try:
                data = self.iconIds.get(id[0])
            except:
                data = self.iconIds.get(id)
                
            if data:
                p,generation = data
                if generation==self.generation:
                    if self.trace: g.trace(id,p.headString())
                    return p
                else:
                    g.trace("*** wrong generation: %d ***" % id)
                    return None
            else:
                g.trace(id,None)
                return None
                
            
        #@nonl
        #@-node:ekr.20040723104427.7:tree.findVnodeWithIconId
        #@+node:ekr.20040723104427.26:tree.OnPopup & allies
        def OnPopup (self,p,event):
            
            """Handle right-clicks in the outline."""
            
            # Note: "headrclick" hooks handled by vnode callback routine.
        
            if event != None:
                c = self.c
                if not g.doHook("create-popup-menu",c=c,p=p,event=event):
                    self.createPopupMenu(event)
                if not g.doHook("enable-popup-menu-items",c=c,p=p,event=event):
                    self.enablePopupMenuItems(p,event)
                if not g.doHook("show-popup-menu",c=c,p=p,event=event):
                    self.showPopupMenu(event)
        
            return "break"
        #@nonl
        #@+node:ekr.20040723104427.27:OnPopupFocusLost
        #@+at 
        #@nonl
        # On Linux we must do something special to make the popup menu 
        # "unpost" if the mouse is clicked elsewhere.  So we have to catch the 
        # <FocusOut> event and explicitly unpost.  In order to process the 
        # <FocusOut> event, we need to be able to find the reference to the 
        # popup window again, so this needs to be an attribute of the tree 
        # object; hence, "self.popupMenu".
        # 
        # Aside: though Tk tries to be muli-platform, the interaction with 
        # different window managers does cause small differences that will 
        # need to be compensated by system specific application code. :-(
        #@-at
        #@@c
        
        # 20-SEP-2002 DTHEIN: This event handler is only needed for Linux.
        
        def OnPopupFocusLost(self,event=None):
        
            self.popupMenu.unpost()
            
        #@-node:ekr.20040723104427.27:OnPopupFocusLost
        #@+node:ekr.20040723104427.28:createPopupMenu
        def createPopupMenu (self,event):
            
            c = self.c ; frame = c.frame
            
            # If we are going to recreate it, we had better destroy it.
            if self.popupMenu:
                self.popupMenu.destroy()
                self.popupMenu = None
            
            self.popupMenu = menu = Tk.Menu(g.app.root, tearoff=0)
            
            # Add the Open With entries if they exist.
            if g.app.openWithTable:
                frame.menu.createMenuEntries(menu,g.app.openWithTable,openWith=1)
                table = (("-",None,None),)
                frame.menu.createMenuEntries(menu,table)
                
            #@    << Create the menu table >>
            #@+node:ekr.20040723104427.29:<< Create the menu table >>
            table = (
                ("&Read @file Nodes",None,c.readAtFileNodes),
                ("&Write @file Nodes",None,c.fileCommands.writeAtFileNodes),
                ("-",None,None),
                ("&Tangle","Shift+Ctrl+T",c.tangle),
                ("&Untangle","Shift+Ctrl+U",c.untangle),
                ("-",None,None),
                # 2/16/04: Remove shortcut for Toggle Angle Brackets command.
                ("Toggle Angle &Brackets",None,c.toggleAngleBrackets),
                ("-",None,None),
                ("Cut Node","Shift+Ctrl+X",c.cutOutline),
                ("Copy Node","Shift+Ctrl+C",c.copyOutline),
                ("&Paste Node","Shift+Ctrl+V",c.pasteOutline),
                ("&Delete Node","Shift+Ctrl+BkSp",c.deleteOutline),
                ("-",None,None),
                ("&Insert Node","Ctrl+I",c.insertHeadline),
                ("&Clone Node","Ctrl+`",c.clone),
                ("Sort C&hildren",None,c.sortChildren),
                ("&Sort Siblings","Alt-A",c.sortSiblings),
                ("-",None,None),
                ("Contract Parent","Alt+0",c.contractParent))
            #@nonl
            #@-node:ekr.20040723104427.29:<< Create the menu table >>
            #@nl
            
            # 11/27/03: Don't actually set binding: it would conflict with previous.
            frame.menu.createMenuEntries(menu,table,dontBind=True)
        #@nonl
        #@-node:ekr.20040723104427.28:createPopupMenu
        #@+node:ekr.20040723104427.30:enablePopupMenuItems
        def enablePopupMenuItems (self,v,event):
            
            """Enable and disable items in the popup menu."""
            
            c = self.c ; menu = self.popupMenu
        
            #@    << set isAtRoot and isAtFile if v's tree contains @root or @file nodes >>
            #@+node:ekr.20040723104427.31:<< set isAtRoot and isAtFile if v's tree contains @root or @file nodes >>
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
            #@nonl
            #@-node:ekr.20040723104427.31:<< set isAtRoot and isAtFile if v's tree contains @root or @file nodes >>
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
        #@nonl
        #@-node:ekr.20040723104427.30:enablePopupMenuItems
        #@+node:ekr.20040723104427.32:showPopupMenu
        def showPopupMenu (self,event):
            
            """Show a popup menu."""
            
            c = self.c ; menu = self.popupMenu ; gui = g.app.gui
        
            if sys.platform == "linux2": # 20-SEP-2002 DTHEIN: not needed for Windows
                menu.bind("<FocusOut>",self.OnPopupFocusLost)
            
            menu.post(event.x_root, event.y_root)
        
            # Make certain we have focus so we know when we lose it.
            # I think this is OK for all OSes.
            gui.set_focus(c,menu)
        #@nonl
        #@-node:ekr.20040723104427.32:showPopupMenu
        #@-node:ekr.20040723104427.26:tree.OnPopup & allies
        #@+node:ekr.20040723173301.19:tree.moveUpDown
        def OnUpKey   (self,event=None): return self.moveUpDown("up")
        def OnDownKey (self,event=None): return self.moveUpDown("down")
        
        def moveUpDown (self,upOrDown):
            c = self.c ; body = c.frame.bodyCtrl
            # Make the insertion cursor visible so bbox won't return an empty list.
            body.see("insert")
            # Find the coordinates of the cursor and set the new height.
            # There may be roundoff errors because character postions may not match exactly.
            ins =  body.index("insert")
            lines,char = g.scanf(ins,"%d.%d")
            x,y,junk,textH = body.bbox("insert")
            bodyW,bodyH = body.winfo_width(),body.winfo_height()
            junk,maxy,junk,junk = body.bbox("@%d,%d" % (bodyW,bodyH))
            # Make sure y is within text boundaries.
            if upOrDown == "up":
                if y <= textH:
                    body.yview("scroll",-1,"units")
                else: y = max(y-textH,0)
            else:
                if y >= maxy:
                    body.yview("scroll",1,"units")
                else: y = min(y+textH,maxy)
            # Position the cursor on the proper side of the characters.
            newx,newy,width,junk = body.bbox("@%d,%d" % (x,y))
            if x > newx + width/2:
                x = newx + width + 1
            result = body.index("@%d,%d" % (x,y))
            body.mark_set("insert",result)
            # g.trace("entry:  %s.%s" % (lines,char))
            # g.trace("result:",result)
            # g.trace("insert:",body.index("insert"))
            return "break" # Inhibit further bindings.
        #@nonl
        #@-node:ekr.20040723173301.19:tree.moveUpDown
        #@-node:ekr.20040723104427.1:Unchanged Event handers
        #@-node:ekr.20040723103515:Event handlers...
        #@+node:ekr.20040723174025:Incremental drawing...
        #@+node:ekr.20040723174025.1:allocateNodes
        def allocateNodes(self,where,lines):
            
            """Allocate Tk widgets in nodes that will become visible as the result of an upcoming scroll"""
            
            assert(where in ("above","below"))
        
            # print "allocateNodes: %d lines %s visible area" % (lines,where)
            
            # Expand the visible area: a little extra delta is safer.
            delta = lines * (self.line_height + 4)
            y1,y2 = self.visibleArea
        
            if where == "below":
                y2 += delta
            else:
                y1 = max(0.0,y1-delta)
        
            self.expandedVisibleArea=y1,y2
            # print "expandedArea:   %5.1f %5.1f" % (y1,y2)
            
            # Allocate all nodes in expanded visible area.
            self.updatedNodeCount = 0
            self.updateTree(self.c.rootPosition(),self.root_left,self.root_top,0,0)
            # if self.updatedNodeCount: print "updatedNodeCount:", self.updatedNodeCount
        #@-node:ekr.20040723174025.1:allocateNodes
        #@+node:ekr.20040723174025.2:allocateNodesBeforeScrolling
        def allocateNodesBeforeScrolling (self, args):
            
            """Calculate the nodes that will become visible as the result of an upcoming scroll.
        
            args is the tuple passed to the Tk.Canvas.yview method"""
        
            if not self.allocateOnlyVisibleNodes: return
        
            # print "allocateNodesBeforeScrolling:",self.redrawCount,args
        
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
        #@nonl
        #@-node:ekr.20040723174025.2:allocateNodesBeforeScrolling
        #@+node:ekr.20040723174025.3:updateNode
        def updateNode (self,v,x,y):
            
            """Draw a node that may have become visible as a result of a scrolling operation"""
        
            if self.inExpandedVisibleArea(y):
                # This check is a major optimization.
                if not v.edit_text():
                    return self.force_draw_node(v,x,y)
                else:
                    return self.line_height
        
            return self.line_height
        #@nonl
        #@-node:ekr.20040723174025.3:updateNode
        #@+node:ekr.20040723174025.4:setVisibleAreaToFullCanvas
        def setVisibleAreaToFullCanvas(self):
            
            if self.visibleArea:
                y1,y2 = self.visibleArea
                y2 = max(y2,y1 + self.canvas.winfo_height())
                self.visibleArea = y1,y2
        #@nonl
        #@-node:ekr.20040723174025.4:setVisibleAreaToFullCanvas
        #@+node:ekr.20040723174025.5:setVisibleArea
        def setVisibleArea (self,args):
        
            r1,r2 = args
            r1,r2 = float(r1),float(r2)
            # print "scroll ratios:",r1,r2
        
            try:
                s = self.canvas.cget("scrollregion")
                x1,y1,x2,y2 = g.scanf(s,"%d %d %d %d")
                x1,y1,x2,y2 = int(x1),int(y1),int(x2),int(y2)
            except:
                self.visibleArea = None
                return
                
            scroll_h = y2-y1
            # print "height of scrollregion:", scroll_h
        
            vy1 = y1 + (scroll_h*r1)
            vy2 = y1 + (scroll_h*r2)
            self.visibleArea = vy1,vy2
            # print "setVisibleArea: %5.1f %5.1f" % (vy1,vy2)
        #@-node:ekr.20040723174025.5:setVisibleArea
        #@+node:ekr.20040723174025.6:tree.updateTree
        def updateTree (self,v,x,y,h,level):
        
            yfirst = ylast = y
            if level==0: yfirst += 10
            while v:
                # g.trace(x,y,v)
                h,indent = self.updateNode(v,x,y)
                y += h ; ylast = y
                if v.isExpanded() and v.firstChild():
                    y = self.updateTree(v.firstChild(),x+indent,y,h,level+1)
                v = v.next()
            return y
        #@-node:ekr.20040723174025.6:tree.updateTree
        #@-node:ekr.20040723174025:Incremental drawing...
        #@+node:ekr.20040723173301.3:Selecting & editing...
        #@+node:ekr.20040725053107.1:endEditLabel
        def endEditLabel (self):
            
            """End editing for self.editText."""
        
            c = self.c ; gui = g.app.gui
            
            p = self.editPosition()
        
            if p and p.edit_text():
                if 0: # New in recycled widgets scheme: this could cause a race condition.
                    # This will be done in the redraw code becaused editPosition will be None.
                    self.setUnselectedLabelState(p)
        
                self.setEditPosition(None)
        
                # force a redraw of joined and ancestor headlines.
                self.force_redraw() 
        
            gui.set_focus(c,c.frame.bodyCtrl) # 10/14/02
        #@nonl
        #@-node:ekr.20040725053107.1:endEditLabel
        #@+node:ekr.20040725052914:editLabel
        def editLabel (self,p):
            
            """Start editing p.edit_text."""
            
            # g.trace(p)
        
            if self.editPosition() and p != self.editPosition():
                self.endEditLabel()
                self.frame.revertHeadline = None
                
            self.setEditPosition(p)
        
            # Start editing
            if p and p.edit_text():
                self.setNormalLabelState(p)
                self.frame.revertHeadline = p.headString()
                self.setEditPosition(p)
        #@nonl
        #@-node:ekr.20040725052914:editLabel
        #@+node:ekr.20040725052452:tree.select
        # Warning: do not try to "optimize" this by returning if v==tree.currentVnode.
        
        def select (self,p,updateBeadList=True):
            
            c = self.c ; frame = c.frame ; body = frame.bodyCtrl
            old_p = c.currentPosition()
        
            if not p: return
            
            if self.trace: g.trace(p.headString())
        
            if not g.doHook("unselect1",c=c,new_v=p,old_v=old_p):
                #@        << unselect the old node >>
                #@+node:ekr.20040725052452.2:<< unselect the old node >> (changed in 4.2)
                # Remember the position of the scrollbar before making any changes.
                yview=body.yview()
                insertSpot = c.frame.body.getInsertionPoint()
                
                if old_p and old_p != p:
                    if self.trace: g.trace("unselect:",old_p.headString())
                    self.endEditLabel() # sets editPosition = None
                    self.setUnselectedLabelState(old_p)
                
                if old_p and old_p.edit_text():
                    old_p.v.t.scrollBarSpot = yview
                    old_p.v.t.insertSpot = insertSpot
                #@nonl
                #@-node:ekr.20040725052452.2:<< unselect the old node >> (changed in 4.2)
                #@nl
        
            g.doHook("unselect2",c=c,new_v=p,old_v=old_p)
            
            if not g.doHook("select1",c=c,new_v=p,old_v=old_p):
                #@        << select the new node >>
                #@+node:ekr.20040725052452.3:<< select the new node >>
                frame.setWrap(p)
                
                # 6/14/04: Always do this.  Otherwise there can be problems with trailing hewlines.
                s = g.toUnicode(p.v.t.bodyString,"utf-8")
                self.setText(body,s,tag="select:set body",isHeadline=False)
                
                # We must do a full recoloring: we may be changing context!
                self.frame.body.recolor_now(p) # recolor now uses p.copy(), so this is safe.
                
                if p.v and p.v.t.scrollBarSpot != None:
                    first,last = p.v.t.scrollBarSpot
                    body.yview("moveto",first)
                
                if p.v.t.insertSpot != None: # 9/21/02: moved from c.selectVnode
                    c.frame.bodyCtrl.mark_set("insert",p.v.t.insertSpot)
                    c.frame.bodyCtrl.see(p.v.t.insertSpot)
                else:
                    c.frame.bodyCtrl.mark_set("insert","1.0")
                #@nonl
                #@-node:ekr.20040725052452.3:<< select the new node >>
                #@nl
                if p and p != old_p: # 3/26/03: Suppress duplicate call.
                    try: # may fail during initialization
                        self.idle_scrollTo(p)
                    except: pass
                #@        << update c.beadList or c.beadPointer >>
                #@+node:ekr.20040725052452.4:<< update c.beadList or c.beadPointer >>
                if updateBeadList:
                    
                    if c.beadPointer > -1:
                        present_p = c.beadList[c.beadPointer]
                    else:
                        present_p = c.nullPosition()
                    
                    if p != present_p:
                        # Replace the tail of c.beadList by c and make c the present node.
                        # print "updating c.beadList"
                        c.beadPointer += 1
                        c.beadList[c.beadPointer:] = []
                        c.beadList.append(p.copy())
                        
                    # g.trace(c.beadPointer,p,present_p)
                #@nonl
                #@-node:ekr.20040725052452.4:<< update c.beadList or c.beadPointer >>
                #@nl
                #@        << update c.visitedList >>
                #@+node:ekr.20040725052452.5:<< update c.visitedList >>
                # Make p the most recently visited position on the list.
                if p in c.visitedList:
                    c.visitedList.remove(p)
                
                c.visitedList.insert(0,p.copy())
                #@nonl
                #@-node:ekr.20040725052452.5:<< update c.visitedList >>
                #@nl
        
            #@    << set the current node >>
            #@+node:ekr.20040725052452.6:<< set the current node >>
            self.c.setCurrentPosition(p.copy())
            if p != old_p:
                self.setSelectedLabelState(p)
            self.frame.scanForTabWidth(p) #GS I believe this should also get into the select1 hook
            g.app.gui.set_focus(c,c.frame.bodyCtrl)
            #@nonl
            #@-node:ekr.20040725052452.6:<< set the current node >>
            #@nl
            
            g.doHook("select2",c=c,new_v=p,old_v=old_p)
            g.doHook("select3",c=c,new_v=p,old_v=old_p)
            
            # g.printGc()
        #@nonl
        #@-node:ekr.20040725052452:tree.select
        #@+node:ekr.20040725052606:tree.set...LabelState
        #@+node:ekr.20040725133545.1:setNormalLabelState
        def setNormalLabelState (self,p): # selected, editing
        
            # Do nothing if a redraw is already sheduled.
            # This prevents race conditions.
            if self.redrawScheduled: return 
            
            if p and p.edit_text():
                self.setEditHeadlineColors(p)
                p.edit_text().tag_remove("sel","1.0","end")
                p.edit_text().tag_add("sel","1.0","end")
                g.app.gui.set_focus(self.c,p.edit_text())
        #@nonl
        #@-node:ekr.20040725133545.1:setNormalLabelState
        #@+node:ekr.20040725133545.2:setDisabledLabelState
        def setDisabledLabelState (self,p): # selected, disabled
        
            # Do nothing if a redraw is already sheduled.
            # This prevents race conditions.
            if self.redrawScheduled: return
        
            if p and p.edit_text():
                self.setDisabledHeadlineColors(p)
        #@nonl
        #@-node:ekr.20040725133545.2:setDisabledLabelState
        #@+node:ekr.20040725133545.3:setSelectedLabelState
        def setSelectedLabelState (self,p): # selected, not editing
        
            # Do nothing if a redraw is already sheduled.
            # This prevents race conditions.
            if self.redrawScheduled: return 
        
            # g.trace(p)
            self.setDisabledLabelState(p)
        
        #@-node:ekr.20040725133545.3:setSelectedLabelState
        #@+node:ekr.20040725133545.4:setUnselectedLabelState
        def setUnselectedLabelState (self,p): # not selected.
        
            # Do nothing if a redraw is already sheduled.
            # This prevents race conditions.
            if self.redrawScheduled: return 
        
            if p and p.edit_text():
                self.setUnselectedHeadlineColors(p)
        #@nonl
        #@-node:ekr.20040725133545.4:setUnselectedLabelState
        #@+node:ekr.20040723173301.17:setDisabledHeadlineColors
        def setDisabledHeadlineColors (self,p):
        
            config = g.app.config ; w = p.edit_text()
            
            if self.trace:
                if not self.redrawing:
                    print "%10s %d %s" % ("disabled",id(w),p.headString())
                    # import traceback ; traceback.print_stack(limit=6)
        
            fg = config.getWindowPref("headline_text_selected_foreground_color")
            bg = config.getWindowPref("headline_text_selected_background_color")
            
            if not fg or not bg:
                fg,bg = "black","gray80"
            
            try:
                w.configure(state="disabled",highlightthickness=0,fg=fg,bg=bg)
            except:
                g.es_exception()
        #@nonl
        #@-node:ekr.20040723173301.17:setDisabledHeadlineColors
        #@+node:ekr.20040723173301.16:setEditHeadlineColors
        def setEditHeadlineColors (self,p):
        
            config = g.app.config ; w = p.edit_text()
            
            if self.trace:
                if not self.redrawing:
                    print "%10s %d %s" % ("edit",id(2),p.headString())
            
            fg   = config.getWindowPref("headline_text_editing_foreground_color")
            bg   = config.getWindowPref("headline_text_editing_background_color")
            selfg = config.getWindowPref("headline_text_editing_selection_foreground_color")
            selbg = config.getWindowPref("headline_text_editing_selection_background_color")
            
            if not fg or not bg:
                fg,bg = "black","white"
            
            try:
                if selfg and selbg:
                    w.configure(
                        selectforeground=selfg,selectbackground=selbg,
                        state="normal",highlightthickness=1,fg=fg,bg=bg)
                else:
                    w.configure(
                        state="normal",highlightthickness=1,fg=fg,bg=bg)
            except:
                g.es_exception()
        #@nonl
        #@-node:ekr.20040723173301.16:setEditHeadlineColors
        #@+node:ekr.20040723173301.18:setUnselectedHeadlineColors
        def setUnselectedHeadlineColors (self,p):
            
            config = g.app.config ; w = p.edit_text()
            
            if self.trace:
                if not self.redrawing:
                    print "%10s %d %s" % ("unselect",id(w),p.headString())
                    # import traceback ; traceback.print_stack(limit=6)
            
            fg = config.getWindowPref("headline_text_unselected_foreground_color")
            bg = config.getWindowPref("headline_text_unselected_background_color")
            
            if not fg or not bg:
                fg,bg = "black","white"
            
            try:
                w.configure(state="disabled",highlightthickness=0,fg=fg,bg=bg)
            except:
                g.es_exception()
        #@nonl
        #@-node:ekr.20040723173301.18:setUnselectedHeadlineColors
        #@-node:ekr.20040725052606:tree.set...LabelState
        #@+node:ekr.20040723173301.4:dimEditLabel, undimEditLabel
        # Convenience methods so the caller doesn't have to know the present edit node.
        
        def dimEditLabel (self):
            
            p = self.c.currentPosition()
            self.setDisabledLabelState(p)
        
        def undimEditLabel (self):
        
            p = self.c.currentPosition()
            self.setSelectedLabelState(p)
        #@nonl
        #@-node:ekr.20040723173301.4:dimEditLabel, undimEditLabel
        #@+node:ekr.20040723173301.7:tree.expandAllAncestors
        def expandAllAncestors (self,p):
            
            redraw_flag = False
        
            for p in p.parents_iter():
                if not p.isExpanded():
                    p.expand()
                    redraw_flag = True
        
            return redraw_flag
        
        #@-node:ekr.20040723173301.7:tree.expandAllAncestors
        #@-node:ekr.20040723173301.3:Selecting & editing...
        #@-others
    
    leoTkinterTree.leoTkinterTree = myLeoTkinterTree
#@nonl
#@-node:ekr.20040723100651:@thin __outlineExperiments.py
#@-leo
