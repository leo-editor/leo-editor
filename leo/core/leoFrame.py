#@+leo-ver=4-thin
#@+node:ekr.20031218072017.3655:@thin leoFrame.py
"""The base classes for all Leo Windows, their body, log and tree panes, key bindings and menus.

These classes should be overridden to create frames for a particular gui."""

#@@language python
#@@tabwidth -4
#@@pagewidth 80

import leo.core.leoGlobals as g
import leo.core.leoColor as leoColor
import leo.core.leoMenu as leoMenu
import leo.core.leoNodes as leoNodes
import leo.core.leoUndo as leoUndo

import re

#@<< About handling events >>
#@+node:ekr.20031218072017.2410:<< About handling events >>
#@+at
# Leo must handle events or commands that change the text in the outline or 
# body
# panes. We must ensure that headline and body text corresponds to the vnode 
# and
# tnode corresponding to presently selected outline, and vice versa. For 
# example,
# when the user selects a new headline in the outline pane, we must ensure 
# that:
# 
# 1) All vnodes and tnodes have up-to-date information and
# 
# 2) the body pane is loaded with the correct data.
# 
# Early versions of Leo attempted to satisfy these conditions when the user
# switched outline nodes. Such attempts never worked well; there were too many
# special cases. Later versions of Leo use a much more direct approach: every
# keystroke in the body pane updates the presently selected tnode immediately.
# 
# The leoTree class contains all the event handlers for the tree pane, and the
# leoBody class contains the event handlers for the body pane. The following
# convenience methods exists:
# 
# - body.updateBody & tree.updateBody:
#     Called by k.masterCommand after any keystroke not handled by 
# k.masterCommand.
#     These are suprising complex.
# 
# - body.bodyChanged & tree.headChanged:
#     Called by commands throughout Leo's core that change the body or 
# headline.
#     These are thin wrappers for updateBody and updateTree.
#@-at
#@-node:ekr.20031218072017.2410:<< About handling events >>
#@nl
#@<< define text classes >>
#@+node:ekr.20070228074228:<< define text classes >>
#@+others
#@+node:ekr.20070228074312:class baseTextWidget
class baseTextWidget:

    '''The base class for all wrapper classes for leo Text widgets.'''

    #@    @+others
    #@+node:ekr.20070228074312.1:Birth & special methods (baseText)
    def __init__ (self,c,baseClassName,name,widget):

        self.baseClassName = baseClassName
        self.c = c
        self.name = name
        self.virtualInsertPoint = None
        self.widget = widget # Not used at present.

    def __repr__(self):
        return '%s: %s' % (self.baseClassName,id(self))

    #@-node:ekr.20070228074312.1:Birth & special methods (baseText)
    #@+node:ekr.20070228074312.2:baseTextWidget.onChar
    # Don't even think of using key up/down events.
    # They don't work reliably and don't support auto-repeat.

    def onChar (self, event):

        c = self.c
        keycode = event.GetKeyCode()
        event.leoWidget = self
        keysym = g.app.gui.eventKeysym(event)
        #g.trace('text: keycode %3s keysym %s' % (keycode,keysym))
        if keysym:
            c.k.masterKeyHandler(event,stroke=keysym)
            c.outerUpdate()
    #@nonl
    #@-node:ekr.20070228074312.2:baseTextWidget.onChar
    #@+node:ekr.20070228074312.3:Do-nothing
    def update (self,*args,**keys):             pass
    def update_idletasks (self,*args,**keys):   pass
    #@-node:ekr.20070228074312.3:Do-nothing
    #@+node:ekr.20070228074312.4:bindings (must be overridden in subclasses)
    # Define these here to keep pylint happy.

    def _appendText(self,s):            self.oops()
    def _get(self,i,j):                 self.oops() ; return ''
    def _getAllText(self):              self.oops() ; return ''
    def _getFocus(self):                self.oops() ; return None
    def _getInsertPoint(self):          self.oops() ; return 0
    def _getLastPosition(self):         self.oops() ; return 0
    def _getSelectedText(self):         self.oops() ; return ''
    def _getSelectionRange(self):       self.oops() ; return (0,0)
    def _getYScrollPosition(self):      self.oops() ; return None # A flag
    def _hitTest(self,pos):             self.oops()
    def _insertText(self,i,s):          self.oops()
    def _scrollLines(self,n):           self.oops()
    def _see(self,i):                   self.oops()
    def _setAllText(self,s):            self.oops()
    def _setBackgroundColor(self,color): self.oops()
    def _setForegroundColor(self,color): self.oops()
    def _setFocus(self):                self.oops()
    def _setInsertPoint(self,i):        self.oops()
    def _setSelectionRange(self,i,j):   self.oops()
    def _setYScrollPosition(self,i):    self.oops()

    _findFocus = _getFocus
    #@-node:ekr.20070228074312.4:bindings (must be overridden in subclasses)
    #@+node:ekr.20070228074312.5:oops
    def oops (self):

        g.pr('wxGui baseTextWidget oops:',self,g.callers(4),
            'must be overridden in subclass')
    #@-node:ekr.20070228074312.5:oops
    #@+node:ekr.20070228074312.6:Index conversion
    #@+node:ekr.20070228074312.7:w.toGuiIndex & toPythonIndex
    def toPythonIndex (self,index):

        w = self

        if type(index) == type(99):
            return index
        elif index == '1.0':
            return 0
        elif index == 'end':
            return w._getLastPosition()
        else:
            # g.trace(repr(index))
            s = w._getAllText()
            row,col = index.split('.')
            row,col = int(row),int(col)
            i = g.convertRowColToPythonIndex(s,row-1,col)
            # g.trace(index,row,col,i,g.callers(6))
            return i

    toGuiIndex = toPythonIndex
    #@nonl
    #@-node:ekr.20070228074312.7:w.toGuiIndex & toPythonIndex
    #@+node:ekr.20070228074312.8:w.rowColToGuiIndex
    # This method is called only from the colorizer.
    # It provides a huge speedup over naive code.

    def rowColToGuiIndex (self,s,row,col):

        return g.convertRowColToPythonIndex(s,row,col)    
    #@-node:ekr.20070228074312.8:w.rowColToGuiIndex
    #@-node:ekr.20070228074312.6:Index conversion
    #@+node:ekr.20070228074312.9:Wrapper methods (widget-independent)
    # These methods are widget-independent because they call the corresponding _xxx methods.
    #@nonl
    #@+node:ekr.20070228074312.10:appendText
    def appendText (self,s):

        w = self
        w._appendText(s)
    #@-node:ekr.20070228074312.10:appendText
    #@+node:ekr.20070228074312.11:bind
    def bind (self,kind,*args,**keys):

        w = self

        # g.trace('wxLeoText',kind,args[0].__name__)
    #@nonl
    #@-node:ekr.20070228074312.11:bind
    #@+node:ekr.20070228074312.12:clipboard_clear & clipboard_append
    def clipboard_clear (self):

        g.app.gui.replaceClipboardWith('')

    def clipboard_append(self,s):

        s1 = g.app.gui.getTextFromClipboard()

        g.app.gui.replaceClipboardWith(s1 + s)
    #@-node:ekr.20070228074312.12:clipboard_clear & clipboard_append
    #@+node:ekr.20070228074312.13:delete
    def delete(self,i,j=None):

        w = self
        i = w.toPythonIndex(i)
        if j is None: j = i+ 1
        j = w.toPythonIndex(j)

        # g.trace(i,j,len(s),repr(s[:20]))
        s = w.getAllText()
        w.setAllText(s[:i] + s[j:])
    #@-node:ekr.20070228074312.13:delete
    #@+node:ekr.20070228074312.14:deleteTextSelection
    def deleteTextSelection (self):

        w = self
        i,j = w._getSelectionRange()
        if i == j: return

        s = w._getAllText()
        s = s[i:] + s[j:]

        # g.trace(len(s),repr(s[:20]))
        w._setAllText(s)
    #@-node:ekr.20070228074312.14:deleteTextSelection
    #@+node:ekr.20070228074312.15:event_generate (baseTextWidget)
    def event_generate(self,stroke):

        w = self ; c = self.c ; char = stroke

        # Canonicalize the setting.
        stroke = c.k.shortcutFromSetting(stroke)

        # g.trace('baseTextWidget','char',char,'stroke',stroke)

        class eventGenerateEvent:
            def __init__ (self,c,w,char,keysym):
                self.c = c
                self.char = char
                self.keysym = keysym
                self.leoWidget = w
                self.widget = w

        event = eventGenerateEvent(c,w,char,stroke)
        c.k.masterKeyHandler(event,stroke=stroke)
        c.outerUpdate()
    #@-node:ekr.20070228074312.15:event_generate (baseTextWidget)
    #@+node:ekr.20070228074312.16:flashCharacter (to do)
    def flashCharacter(self,i,bg='white',fg='red',flashes=3,delay=75): # tkTextWidget.

        pass
    #@nonl
    #@-node:ekr.20070228074312.16:flashCharacter (to do)
    #@+node:ekr.20070228074312.17:getFocus (baseText)
    def getFocus (self):

        w = self
        w2 = w._getFocus()
        # g.trace('w',w,'focus',w2)
        return w2

    findFocus = getFocus
    #@-node:ekr.20070228074312.17:getFocus (baseText)
    #@+node:ekr.20070228074312.18:get
    def get(self,i,j=None):

        w = self

        i = w.toPythonIndex(i)
        if j is None: j = i+ 1
        j = w.toPythonIndex(j)

        s = w._get(i,j)
        return g.toUnicode(s,g.app.tkEncoding)
    #@-node:ekr.20070228074312.18:get
    #@+node:ekr.20070228074312.19:getAllText
    def getAllText (self):

        w = self

        s = w._getAllText()
        return g.toUnicode(s,g.app.tkEncoding)
    #@-node:ekr.20070228074312.19:getAllText
    #@+node:ekr.20070228074312.20:getInsertPoint (baseText)
    def getInsertPoint(self):

        w = self
        i = w._getInsertPoint()

        # g.trace(self,'baseWidget: i:',i,'virtual',w.virtualInsertPoint)

        if i is None:
            if w.virtualInsertPoint is None:
                i = 0
            else:
                i = w.virtualInsertPoint

        w.virtualInsertPoint = i

        return i
    #@-node:ekr.20070228074312.20:getInsertPoint (baseText)
    #@+node:ekr.20070228102413:getName & GetName
    def GetName(self):
        return self.name

    getName = GetName
    #@nonl
    #@-node:ekr.20070228102413:getName & GetName
    #@+node:ekr.20070228074312.21:getSelectedText
    def getSelectedText (self):

        w = self
        s = w._getSelectedText()
        return g.toUnicode(s,g.app.tkEncoding)
    #@-node:ekr.20070228074312.21:getSelectedText
    #@+node:ekr.20070228074312.22:getSelectionRange (baseText)
    def getSelectionRange (self,sort=True):

        """Return a tuple representing the selected range of the widget.

        Return a tuple giving the insertion point if no range of text is selected."""

        w = self

        sel = w._getSelectionRange() # wx.richtext.RichTextCtrl returns (-1,-1) on no selection.
        if len(sel) == 2 and sel[0] >= 0 and sel[1] >= 0:
            #g.trace(self,'baseWidget: sel',repr(sel),g.callers(6))
            i,j = sel
            if sort and i > j: sel = j,i # Bug fix: 10/5/07
            return sel
        else:
            # Return the insertion point if there is no selected text.
            i =  w._getInsertPoint()
            #g.trace(self,'baseWidget: i',i,g.callers(6))
            return i,i
    #@-node:ekr.20070228074312.22:getSelectionRange (baseText)
    #@+node:ekr.20070228074312.23:getYScrollPosition
    def getYScrollPosition (self):

        w = self
        return w._getYScrollPosition()
    #@-node:ekr.20070228074312.23:getYScrollPosition
    #@+node:ekr.20070228074312.24:getWidth
    def getWidth (self):

        '''Return the width of the widget.
        This is only called for headline widgets,
        and gui's may choose not to do anything here.'''

        w = self
        return 0
    #@-node:ekr.20070228074312.24:getWidth
    #@+node:ekr.20070228074312.25:hasSelection
    def hasSelection (self):

        w = self
        i,j = w.getSelectionRange()
        return i != j
    #@-node:ekr.20070228074312.25:hasSelection
    #@+node:ekr.20070228074312.26:insert
    # The signature is more restrictive than the Tk.Text.insert method.

    def insert(self,i,s):

        w = self
        i = w.toPythonIndex(i)
        # w._setInsertPoint(i)
        w._insertText(i,s)
    #@-node:ekr.20070228074312.26:insert
    #@+node:ekr.20070228074312.27:indexIsVisible
    def indexIsVisible (self,i):

        return False # Code will loop if this returns True forever.
    #@nonl
    #@-node:ekr.20070228074312.27:indexIsVisible
    #@+node:ekr.20070228074312.28:replace
    def replace (self,i,j,s):

        w = self
        w.delete(i,j)
        w.insert(i,s)
    #@-node:ekr.20070228074312.28:replace
    #@+node:ekr.20070228074312.29:scrollLines
    def scrollLines (self,n):

        w = self
        w._scrollLines(n)
    #@nonl
    #@-node:ekr.20070228074312.29:scrollLines
    #@+node:ekr.20070228074312.30:see & seeInsertPoint
    def see(self,index):

        w = self
        i = self.toPythonIndex(index)
        w._see(i)

    def seeInsertPoint(self):

        w = self
        i = w._getInsertPoint()
        w._see(i)
    #@-node:ekr.20070228074312.30:see & seeInsertPoint
    #@+node:ekr.20070228074312.31:selectAllText
    def selectAllText (self,insert=None):

        '''Select all text of the widget.'''

        w = self
        w.setSelectionRange(0,'end',insert=insert)
    #@-node:ekr.20070228074312.31:selectAllText
    #@+node:ekr.20070228074312.32:setAllText
    def setAllText (self,s):

        w = self
        w._setAllText(s)
    #@nonl
    #@-node:ekr.20070228074312.32:setAllText
    #@+node:ekr.20070228074312.33:setBackgroundColor
    def setBackgroundColor (self,color):

        w = self

        # Translate tk colors to wx colors.
        d = { 'lightgrey': 'light grey', 'lightblue': 'leo blue',}

        color = d.get(color,color)

        return w._setBackgroundColor(color)

    SetBackgroundColour = setBackgroundColor
    #@nonl
    #@-node:ekr.20070228074312.33:setBackgroundColor
    #@+node:ekr.20080510153327.3:setForegroundColor
    def setForegroundColor (self,color):

        w = self

        # Translate tk colors to wx colors.
        d = { 'lightgrey': 'light grey', 'lightblue': 'leo blue',}

        color = d.get(color,color)

        return w._setForegroundColor(color)

    SetForegroundColour = setForegroundColor
    #@nonl
    #@-node:ekr.20080510153327.3:setForegroundColor
    #@+node:ekr.20070228074312.34:setFocus (baseText)
    def setFocus (self):

        w = self
        # g.trace('baseText')
        return w._setFocus()

    SetFocus = setFocus
    #@-node:ekr.20070228074312.34:setFocus (baseText)
    #@+node:ekr.20070228074312.35:setInsertPoint (baseText)
    def setInsertPoint (self,pos):

        w = self
        w.virtualInsertPoint = i = w.toPythonIndex(pos)
        # g.trace(self,i)
        w._setInsertPoint(i)
    #@-node:ekr.20070228074312.35:setInsertPoint (baseText)
    #@+node:ekr.20070228074312.36:setSelectionRange (baseText)
    def setSelectionRange (self,i,j,insert=None):

        w = self
        i1, j1, insert1 = i,j,insert
        i,j = w.toPythonIndex(i),w.toPythonIndex(j)

        # g.trace(self,'baseWidget',repr(i1),'=',repr(i),repr(j1),'=',repr(j),repr(insert1),'=',repr(insert),g.callers(4))

        if i == j:
            w._setInsertPoint(j)
        else:
            w._setSelectionRange(i,j)

        if insert is not None and insert in (i,j):
            ins = w.toPythonIndex(insert)
            if ins in (i,j):
                self.virtualInsertPoint = ins
    #@-node:ekr.20070228074312.36:setSelectionRange (baseText)
    #@+node:ekr.20070228074312.37:setWidth
    def setWidth (self,width):

        '''Set the width of the widget.
        This is only called for headline widgets,
        and gui's may choose not to do anything here.'''

        w = self
    #@nonl
    #@-node:ekr.20070228074312.37:setWidth
    #@+node:ekr.20070228074312.38:setYScrollPosition
    def setYScrollPosition (self,i):

        w = self
        w._setYScrollPosition(i)
    #@nonl
    #@-node:ekr.20070228074312.38:setYScrollPosition
    #@+node:ekr.20070228074312.39:tags (to-do)
    #@+node:ekr.20070228074312.40:mark_set (to be removed)
    def mark_set(self,markName,i):

        w = self
        i = self.toPythonIndex(i)

        ### Tk.Text.mark_set(w,markName,i)
    #@-node:ekr.20070228074312.40:mark_set (to be removed)
    #@+node:ekr.20070228074312.41:tag_add
    # The signature is slightly different than the Tk.Text.insert method.

    def tag_add(self,tagName,i,j=None,*args):

        w = self
        i = self.toPythonIndex(i)
        if j is None: j = i + 1
        j = self.toPythonIndex(j)

        # Not ready yet.

        # if not hasattr(w,'leo_styles'):
            # w.leo_styles = {}

        # style = w.leo_styles.get(tagName)

        # if style is not None:
            # # g.trace(i,j,tagName)
            # w.textBaseClass.SetStyle(w,i,j,style)
    #@nonl
    #@-node:ekr.20070228074312.41:tag_add
    #@+node:ekr.20070228074312.42:tag_configure & helper
    def tag_configure (self,colorName,**keys):
        pass

    tag_config = tag_configure
    #@nonl
    #@-node:ekr.20070228074312.42:tag_configure & helper
    #@+node:ekr.20070228074312.44:tag_delete
    def tag_delete (self,tagName,*args,**keys):

        pass

        # g.trace(tagName,args,keys)
    #@-node:ekr.20070228074312.44:tag_delete
    #@+node:ekr.20070228074312.45:tag_names
    def tag_names (self, *args):

        return []
    #@-node:ekr.20070228074312.45:tag_names
    #@+node:ekr.20070228074312.46:tag_ranges
    def tag_ranges(self,tagName):

        return tuple()

        # w = self
        # aList = Tk.Text.tag_ranges(w,tagName)
        # aList = [w.toPythonIndex(z) for z in aList]
        # return tuple(aList)
    #@-node:ekr.20070228074312.46:tag_ranges
    #@+node:ekr.20070228074312.47:tag_remove
    def tag_remove(self,tagName,i,j=None,*args):

        w = self
        i = self.toPythonIndex(i)
        if j is None: j = i + 1
        j = self.toPythonIndex(j)

        ### Not ready yet.

        # if not hasattr(w,'leo_styles'):
            # w.leo_styles = {}

        # style = w.leo_styles.get(tagName)

        # if style is not None:
            # # g.trace(i,j,tagName)
            # w.textBaseClass.SetStyle(w,i,j,style)
    #@nonl
    #@-node:ekr.20070228074312.47:tag_remove
    #@+node:ekr.20070228074312.48:yview
    def yview (self,*args):

        '''w.yview('moveto',y) or w.yview()'''

        return 0,0
    #@nonl
    #@-node:ekr.20070228074312.48:yview
    #@-node:ekr.20070228074312.39:tags (to-do)
    #@+node:ekr.20070228074312.49:xyToGui/PythonIndex
    def xyToPythonIndex (self,x,y):
        return 0
    #@-node:ekr.20070228074312.49:xyToGui/PythonIndex
    #@-node:ekr.20070228074312.9:Wrapper methods (widget-independent)
    #@-others
#@-node:ekr.20070228074312:class baseTextWidget
#@+node:ekr.20070228074228.1:class stringTextWidget (baseTextWidget)
class stringTextWidget (baseTextWidget):

    '''A class that represents text as a Python string.'''

    #@    @+others
    #@+node:ekr.20070228074228.2:ctor
    def __init__ (self,c,name):

        # Init the base class
        baseTextWidget.__init__ (self,c=c,
            baseClassName='stringTextWidget',name=name,widget=None)

        self.ins = 0
        self.sel = 0,0
        self.s = ''
        self.trace = False
    #@-node:ekr.20070228074228.2:ctor
    #@+node:ekr.20070228074228.3:Overrides
    def _appendText(self,s):
        #if self.trace: g.trace(self,'len(s)',len(s))
        if self.trace: g.trace(self,'ins',self.ins,'s',repr(s[-10:]),g.callers())
        # g.trace(repr(s),g.callers())
        self.s = self.s + s
        self.ins = len(self.s)
        self.sel = self.ins,self.ins
    def _get(self,i,j):                 return self.s[i:j]
    def _getAllText(self):              return self.s
    def _getFocus(self):                return self
    def _getInsertPoint(self):
        # if self.trace: g.trace(self,self.ins)
        return self.ins
    def _getLastPosition(self):         return len(self.s)
    def _getSelectedText(self):         i,j = self.sel ; return self.s[i:j]
    def _getSelectionRange(self):       return self.sel
    def _getYScrollPosition(self):      return None # A flag.
    def _hitTest(self,pos):             pass
    def _insertText(self,i,s):
        s1 = s
        self.s = self.s[:i] + s1 + self.s[i:]
        # if self.trace: g.trace(self,'s',repr(s),'self.s',repr(self.s))
        # if self.trace: g.trace(self,'i',i,'len(s)',len(s),g.callers())
        if self.trace: g.trace(self,'i',i,'s',repr(s[-10:]),g.callers())
        # g.trace(repr(s),g.callers())
        i += len(s1)
        self.ins = i
        self.sel = i,i
    def _scrollLines(self,n):           pass
    def _see(self,i):                   pass
    def _setAllText(self,s):
        if self.trace: g.trace(self,'len(s)',len(s),g.callers())
        if self.trace: g.trace(self,'s',repr(s[-10:]),g.callers())
        # g.trace(repr(s),g.callers())
        self.s = s
        i = len(self.s)
        self.ins = i
        self.sel = i,i
    def _setBackgroundColor(self,color): pass
    def _setForegroundColor(self,color): pass
    def _setFocus(self):                pass
    def _setInsertPoint(self,i):
        if self.trace: g.trace(self,'i',i)
        self.ins = i
        self.sel = i,i
    #@nonl
    #@-node:ekr.20070228074228.3:Overrides
    #@+node:ekr.20070228111853:setSelectionRange (stringText)
    def setSelectionRange (self,i,j,insert=None):

        w = self
        i1, j1, insert1 = i,j,insert
        i,j = w.toPythonIndex(i),w.toPythonIndex(j)

        self.sel = i,j

        if insert is not None: 
            self.ins = w.toPythonIndex(insert)
        else:
            self.ins = j

        if self.trace: g.trace('i',i,'j',j,'insert',repr(insert))
    #@nonl
    #@-node:ekr.20070228111853:setSelectionRange (stringText)
    #@-others
#@-node:ekr.20070228074228.1:class stringTextWidget (baseTextWidget)
#@-others
#@nonl
#@-node:ekr.20070228074228:<< define text classes >>
#@nl

#@+others
#@+node:ekr.20031218072017.3656:class leoBody
class leoBody:

    """The base class for the body pane in Leo windows."""

    #@    @+others
    #@+node:ekr.20031218072017.3657:leoBody.__init__
    def __init__ (self,frame,parentFrame):

        frame.body = self
        self.c = c = frame.c
        self.editorWidgets = {} # keys are pane names, values are text widgets
        self.forceFullRecolorFlag = False
        self.frame = frame
        self.totalNumberOfEditors = 0

        # May be overridden in subclasses...
        self.bodyCtrl = self.widget = None
        self.numberOfEditors = 1
        self.pb = None # paned body widget.

        self.use_chapters = c.config.getBool('use_chapters')

        # Must be overridden in subclasses...
        self.colorizer = None
    #@+node:ekr.20081005065934.9:leoBody.mustBeDefined
    # List of methods that must be defined either in the base class or a subclass.

    mustBeDefined = (
        'initAfterLoad',
    )
    #@nonl
    #@-node:ekr.20081005065934.9:leoBody.mustBeDefined
    #@+node:ekr.20031218072017.3660:leoBody.mustBeDefinedInSubclasses
    mustBeDefinedInSubclasses = (
        # Birth, death & config.
        '__init__',
        'createBindings',
        'createControl',
        'setColorFromConfig',
        'setFontFromConfig'
        # Editors
        'createEditorLabel',
        'setEditorColors',
        # Events...
        'scheduleIdleTimeRoutine',
        # Low-level gui...(May be deleted)
        'getBodyPaneHeight',
        'getBodyPaneWidth',
        'hasFocus',
        'setFocus',
        # 'tag_add',
        # 'tag_bind',
        # 'tag_configure',
        # 'tag_delete',
        # 'tag_remove',
    )
    #@-node:ekr.20031218072017.3660:leoBody.mustBeDefinedInSubclasses
    #@+node:ekr.20061109102912:define leoBody.mustBeDefinedOnlyInBaseClass
    mustBeDefinedOnlyInBaseClass = (
        'getAllText',
        'getColorizer',
        'getInsertLines',
        'getInsertPoint',
        'getSelectedText',
        'getSelectionAreas',
        'getSelectionLines',
        'getYScrollPosition',
        'hasTextSelection',
        'oops',
        'onBodyChanged',
        'onClick',
        'recolor',
        'recolor_now',
        'see',
        'seeInsertPoint',
        'selectAllText',
        'setInsertPoint',
        'setSelectionRange',
        'setYScrollPosition',
        'setSelectionAreas',
        'setYScrollPosition',
        'updateSyntaxColorer',
        # Editors... (These may be overridden)
        # 'addEditor',
        # 'cycleEditorFocus',
        # 'deleteEditor',
        # 'selectEditor',
        # 'selectLabel',
        # 'unselectLabel',
        # 'updateEditors',
    )
    #@-node:ekr.20061109102912:define leoBody.mustBeDefinedOnlyInBaseClass
    #@-node:ekr.20031218072017.3657:leoBody.__init__
    #@+node:ekr.20081005065934.5:leoBody.mustBeDefined
    # List of methods that must be defined either in the base class or a subclass.

    mustBeDefined = (
        'initAfterLoad',
    )
    #@nonl
    #@-node:ekr.20081005065934.5:leoBody.mustBeDefined
    #@+node:ekr.20061109173122:leoBody: must be defined in subclasses
    # Birth, death & config
    def createBindings (self,w=None):               self.oops()
    def createControl (self,parentFrame,p):         self.oops()
    def createTextWidget (self,parentFrame,p,name): self.oops() ; return None
    def setColorFromConfig (self,w=None):           self.oops()
    def setFontFromConfig (self,w=None):            self.oops()

    # Editor
    def createEditorFrame (self,w):             self.oops() ; return None
    def createEditorLabel (self,pane):          self.oops()
    def packEditorLabelWidget (self,w):         self.oops()
    def setEditorColors (self,bg,fg):           self.oops()

    # Events...
    def scheduleIdleTimeRoutine (self,function,*args,**keys): self.oops()
    #@-node:ekr.20061109173122:leoBody: must be defined in subclasses
    #@+node:ekr.20061109173021:leoBody: must be defined in the base class
    #@+node:ekr.20031218072017.3677:Coloring (leoBody)
    def getColorizer(self):

        return self.colorizer

    def updateSyntaxColorer(self,p):

        return self.colorizer.updateSyntaxColorer(p.copy())

    def recolor(self,p,incremental=False):
        self.c.requestRecolorFlag = True
        self.c.incrementalRecolorFlag = incremental

    recolor_now = recolor


    #@-node:ekr.20031218072017.3677:Coloring (leoBody)
    #@+node:ekr.20060528100747:Editors (leoBody)
    # This code uses self.pb, a paned body widget, created by tkBody.finishCreate.


    #@+node:ekr.20070424053629:entries
    #@+node:ekr.20060528100747.1:addEditor
    def addEditor (self,event=None):

        '''Add another editor to the body pane.'''

        c = self.c ; p = c.currentPosition()

        self.totalNumberOfEditors += 1
        self.numberOfEditors += 1

        if self.numberOfEditors == 2:
            # Inject the ivars into the first editor.
            # Bug fix: Leo 4.4.8 rc1: The name of the last editor need not be '1'
            d = self.editorWidgets ; keys = d.keys()
            if len(keys) == 1:
                w_old = d.get(keys[0])
                self.updateInjectedIvars(w_old,p)
                self.selectLabel(w_old) # Immediately create the label in the old editor.
            else:
                g.trace('can not happen: unexpected editorWidgets',d)

        name = '%d' % self.totalNumberOfEditors
        pane = self.pb.add(name)
        panes = self.pb.panes()
        minSize = float(1.0/float(len(panes)))

        f = self.createEditorFrame(pane)
        #@    << create text widget w >>
        #@+node:ekr.20060528110922:<< create text widget w >>
        w = self.createTextWidget(f,name=name,p=p)
        w.delete(0,'end')
        w.insert('end',p.bodyString())
        w.see(0)

        self.setFontFromConfig(w=w)
        self.setColorFromConfig(w=w)
        self.createBindings(w=w)
        c.k.completeAllBindingsForWidget(w)

        self.recolorWidget(p,w)
        #@nonl
        #@-node:ekr.20060528110922:<< create text widget w >>
        #@nl
        self.editorWidgets[name] = w

        for pane in panes:
            self.pb.configurepane(pane,size=minSize)

        self.pb.updatelayout()
        c.frame.body.bodyCtrl = w

        self.updateInjectedIvars(w,p)
        self.selectLabel(w)
        self.selectEditor(w)
        self.updateEditors()
        c.bodyWantsFocusNow()
    #@-node:ekr.20060528100747.1:addEditor
    #@+node:ekr.20060528132829:assignPositionToEditor
    def assignPositionToEditor (self,p):

        '''Called *only* from tree.select to select the present body editor.'''

        c = self.c ; cc = c.chapterController ; w = c.frame.body.bodyCtrl

        self.updateInjectedIvars(w,p)
        self.selectLabel(w)

        # g.trace('===',id(w),w.leo_chapter.name,w.leo_p.headString())
    #@-node:ekr.20060528132829:assignPositionToEditor
    #@+node:ekr.20060528170438:cycleEditorFocus
    def cycleEditorFocus (self,event=None):

        '''Cycle keyboard focus between the body text editors.'''

        c = self.c ; d = self.editorWidgets ; w = c.frame.body.bodyCtrl
        values = d.values()
        if len(values) > 1:
            i = values.index(w) + 1
            if i == len(values): i = 0
            w2 = d.values()[i]
            assert(w!=w2)
            self.selectEditor(w2)
            c.frame.body.bodyCtrl = w2
            # g.pr('***',g.app.gui.widget_name(w2),id(w2))

        return 'break'
    #@-node:ekr.20060528170438:cycleEditorFocus
    #@+node:ekr.20060528113806:deleteEditor
    def deleteEditor (self,event=None):

        '''Delete the presently selected body text editor.'''

        c = self.c ; w = c.frame.body.bodyCtrl ; d = self.editorWidgets

        if len(d.keys()) == 1: return

        name = w.leo_name

        del d [name] 
        self.pb.delete(name)
        panes = self.pb.panes()
        minSize = float(1.0/float(len(panes)))

        for pane in panes:
            self.pb.configurepane(pane,size=minSize)

        # Select another editor.
        w = d.values()[0]
        # c.frame.body.bodyCtrl = w # Don't do this now?
        self.numberOfEditors -= 1
        self.selectEditor(w)
    #@-node:ekr.20060528113806:deleteEditor
    #@+node:ekr.20070425180705:findEditorForChapter (leoBody)
    def findEditorForChapter (self,chapter,p):

        '''Return an editor to be assigned to chapter.'''

        c = self.c ; d = self.editorWidgets ; values = d.values()

        # First, try to match both the chapter and position.
        if p:
            for w in values:
                if (
                    hasattr(w,'leo_chapter') and w.leo_chapter == chapter and
                    hasattr(w,'leo_p') and w.leo_p and w.leo_p == p
                ):
                    # g.trace('***',id(w),'match chapter and p',p.headString())
                    return w

        # Next, try to match just the chapter.
        for w in values:
            if hasattr(w,'leo_chapter') and w.leo_chapter == chapter:
                # g.trace('***',id(w),'match only chapter',p.headString())
                return w

        # As a last resort, return the present editor widget.
        # g.trace('***',id(self.bodyCtrl),'no match',p.headString())
        return c.frame.body.bodyCtrl
    #@-node:ekr.20070425180705:findEditorForChapter (leoBody)
    #@+node:ekr.20060530210057:select/unselectLabel
    def unselectLabel (self,w):

        self.createChapterIvar(w)
        self.packEditorLabelWidget(w)
        s = self.computeLabel(w)
        w.leo_label.configure(text=s,bg='LightSteelBlue1')

    def selectLabel (self,w):

        if self.numberOfEditors > 1:
            self.createChapterIvar(w)
            self.packEditorLabelWidget(w)
            s = self.computeLabel(w)
            # g.trace(s,g.callers())
            w.leo_label.configure(text=s,bg='white')
        elif w.leo_label:
            w.leo_label.pack_forget()
            w.leo_label = None
    #@nonl
    #@-node:ekr.20060530210057:select/unselectLabel
    #@+node:ekr.20061017083312:selectEditor & helpers
    selectEditorLockout = False

    def selectEditor(self,w):

        '''Select editor w and node w.leo_p.'''

        #  Called by body.onClick and whenever w must be selected.
        trace = False
        c = self.c

        if self.selectEditorLockout:
            return

        if w and w == self.c.frame.body.bodyCtrl:
            if w.leo_p and w.leo_p != c.currentPosition():
                c.selectPosition(w.leo_p)
                c.bodyWantsFocusNow()
            return

        try:
            val = None
            self.selectEditorLockout = True
            val = self.selectEditorHelper(w)
        finally:
            self.selectEditorLockout = False

        return val # Don't put a return in a finally clause.
    #@+node:ekr.20070423102603:selectEditorHelper
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
        flag = c.frame.tree.expandAllAncestors(w.leo_p)
        if flag: c.redraw_after_expand()
        c.selectPosition(w.leo_p) # Calls assignPositionToEditor.
        ### c.redraw()
        c.redraw_after_select()

        c.recolor_now()
        #@    << restore the selection, insertion point and the scrollbar >>
        #@+node:ekr.20061017083312.1:<< restore the selection, insertion point and the scrollbar >>
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
        #@-node:ekr.20061017083312.1:<< restore the selection, insertion point and the scrollbar >>
        #@nl
        c.bodyWantsFocusNow()
        return 'break'
    #@-node:ekr.20070423102603:selectEditorHelper
    #@-node:ekr.20061017083312:selectEditor & helpers
    #@+node:ekr.20060528131618:updateEditors
    # Called from addEditor and assignPositionToEditor

    def updateEditors (self):

        c = self.c ; p = c.currentPosition()
        d = self.editorWidgets
        if len(d.keys()) < 2: return # There is only the main widget.

        for key in d:
            w = d.get(key)
            v = w.leo_v
            if v and v == p.v and w != c.frame.body.bodyCtrl:
                w.delete(0,'end')
                w.insert('end',p.bodyString())
                # g.trace('update',w,v)
                self.recolorWidget(p,w)
        c.bodyWantsFocus()
    #@-node:ekr.20060528131618:updateEditors
    #@-node:ekr.20070424053629:entries
    #@+node:ekr.20070424053629.1:utils
    #@+node:ekr.20070422093128:computeLabel
    def computeLabel (self,w):

        s = w.leo_label_s

        if hasattr(w,'leo_chapter') and w.leo_chapter:
            s = '%s: %s' % (w.leo_chapter.name,s)

        return s
    #@-node:ekr.20070422093128:computeLabel
    #@+node:ekr.20070422094710:createChapterIvar
    def createChapterIvar (self,w):

        c = self.c ; cc = c.chapterController

        if not hasattr(w,'leo_chapter') or not w.leo_chapter:
            if cc and self.use_chapters:
                w.leo_chapter = cc.getSelectedChapter()
            else:
                w.leo_chapter = None
    #@-node:ekr.20070422094710:createChapterIvar
    #@+node:ekr.20070424084651:ensurePositionExists
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
    #@-node:ekr.20070424084651:ensurePositionExists
    #@+node:ekr.20070424080640:inactivateActiveEditor
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
    #@-node:ekr.20070424080640:inactivateActiveEditor
    #@+node:ekr.20060530204135:recolorWidget
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
    #@-node:ekr.20060530204135:recolorWidget
    #@+node:ekr.20070424084012:switchToChapter (leoBody)
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
    #@-node:ekr.20070424084012:switchToChapter (leoBody)
    #@+node:ekr.20070424092855:updateInjectedIvars
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
    #@-node:ekr.20070424092855:updateInjectedIvars
    #@-node:ekr.20070424053629.1:utils
    #@-node:ekr.20060528100747:Editors (leoBody)
    #@+node:ekr.20031218072017.1329:onBodyChanged (leoBody)
    # This is the only key handler for the body pane.
    def onBodyChanged (self,undoType,oldSel=None,oldText=None,oldYview=None):

        '''Update Leo after the body has been changed.'''

        trace = False
        body = self ; c = self.c
        bodyCtrl = w = body.bodyCtrl
        p = c.currentPosition()
        insert = w.getInsertPoint()
        ch = g.choose(insert==0,'',w.get(insert-1))
        ch = g.toUnicode(ch,g.app.tkEncoding)
        newText = w.getAllText() # Note: getAllText converts to unicode.
        if trace: g.trace('w',w,'newText',repr(newText),g.callers())
        newSel = w.getSelectionRange()
        if not oldText:
            oldText = p.bodyString() ; changed = True
        else:
            changed = oldText != newText
        if trace: g.trace(repr(ch),'changed:',changed,'newText:',repr(newText))
        if not changed: return
        c.undoer.setUndoTypingParams(p,undoType,
            oldText=oldText,newText=newText,oldSel=oldSel,newSel=newSel,oldYview=oldYview)
        p.v.setBodyString(newText)
        p.v.t.insertSpot = body.getInsertPoint()
        #@    << recolor the body >>
        #@+node:ekr.20051026083733.6:<< recolor the body >>
        body.colorizer.interrupt()
        c.frame.scanForTabWidth(p)
        body.recolor_now(p,incremental=not self.forceFullRecolorFlag)
        self.forceFullRecolorFlag = False

        if g.app.unitTesting:
            g.app.unitTestDict['colorized'] = True
        #@-node:ekr.20051026083733.6:<< recolor the body >>
        #@nl
        if not c.changed: c.setChanged(True)
        self.updateEditors()
        #@    << redraw the screen if necessary >>
        #@+node:ekr.20051026083733.7:<< redraw the screen if necessary >>

        redraw_flag = False
        # Update dirty bits.
        # p.setDirty() sets all cloned and @file dirty bits.
        if not p.isDirty() and p.setDirty():
            redraw_flag = True

        # Update icons. p.v.iconVal may not exist during unit tests.
        val = p.computeIcon()
        # g.trace('new val:',val,'old val:',hasattr(p.v,'iconVal') and p.v.iconVal or '<None>')
        if not hasattr(p.v,"iconVal") or val != p.v.iconVal:
            p.v.iconVal = val
            redraw_flag = True
        if redraw_flag: c.redraw()
        #@-node:ekr.20051026083733.7:<< redraw the screen if necessary >>
        #@nl
    #@-node:ekr.20031218072017.1329:onBodyChanged (leoBody)
    #@+node:ekr.20061109095450.8:onClick
    def onClick (self,event):

        c = self.c ; k = c.k ; w = event and event.widget
        wname = c.widget_name(w)

        if not c.currentPosition(): return

        if wname.startswith('body'):
            # A hack to support middle-button pastes: remember the previous selection.
            k.previousSelection = w.getSelectionRange()
            x,y = g.app.gui.eventXY(event)
            i = w.xyToPythonIndex(x,y)
            # g.trace(x,y,repr(i))
            w.setSelectionRange(i,i,insert=i)
            c.editCommands.setMoveCol(w,i)
            c.frame.updateStatusLine()
            self.selectEditor(w)
        else:
            g.trace('can not happen')
    #@-node:ekr.20061109095450.8:onClick
    #@+node:ekr.20031218072017.3658:oops
    def oops (self):

        g.trace("leoBody oops:", g.callers(4), "should be overridden in subclass")
    #@-node:ekr.20031218072017.3658:oops
    #@+node:ekr.20031218072017.4018:Text (leoBody)
    #@+node:ekr.20031218072017.4030:getInsertLines
    def getInsertLines (self):

        """Return before,after where:

        before is all the lines before the line containing the insert point.
        sel is the line containing the insert point.
        after is all the lines after the line containing the insert point.

        All lines end in a newline, except possibly the last line."""

        body = self ; w = body.bodyCtrl
        s = w.getAllText()
        insert = w.getInsertPoint()
        i,j = g.getLine(s,insert)
        before = s[0:i]
        ins = s[i:j]
        after = s[j:]

        before = g.toUnicode(before,g.app.tkEncoding)
        ins    = g.toUnicode(ins,   g.app.tkEncoding)
        after  = g.toUnicode(after ,g.app.tkEncoding)

        return before,ins,after
    #@-node:ekr.20031218072017.4030:getInsertLines
    #@+node:ekr.20031218072017.4031:getSelectionAreas
    def getSelectionAreas (self):

        """Return before,sel,after where:

        before is the text before the selected text
        (or the text before the insert point if no selection)
        sel is the selected text (or "" if no selection)
        after is the text after the selected text
        (or the text after the insert point if no selection)"""

        body = self ; w = body.bodyCtrl
        s = w.getAllText()
        i,j = w.getSelectionRange()
        if i == j: j = i + 1

        before = s[0:i]
        sel    = s[i:j]
        after  = s[j:]

        before = g.toUnicode(before,g.app.tkEncoding)
        sel    = g.toUnicode(sel,   g.app.tkEncoding)
        after  = g.toUnicode(after ,g.app.tkEncoding)
        return before,sel,after
    #@nonl
    #@-node:ekr.20031218072017.4031:getSelectionAreas
    #@+node:ekr.20031218072017.2377:getSelectionLines
    def getSelectionLines (self):

        """Return before,sel,after where:

        before is the all lines before the selected text
        (or the text before the insert point if no selection)
        sel is the selected text (or "" if no selection)
        after is all lines after the selected text
        (or the text after the insert point if no selection)"""

        c = self.c

        if g.app.batchMode:
            return '','',''

        # At present, called only by c.getBodyLines.
        body = self ; w = body.bodyCtrl
        s = w.getAllText()
        i,j = w.getSelectionRange()
        if i == j:
            i,j = g.getLine(s,i)
        else:
            i,junk = g.getLine(s,i)
            junk,j = g.getLine(s,j)


        before = g.toUnicode(s[0:i],g.app.tkEncoding)
        sel    = g.toUnicode(s[i:j],g.app.tkEncoding)
        after  = g.toUnicode(s[j:len(s)],g.app.tkEncoding)

        # g.trace(i,j,'sel',repr(s[i:j]),'after',repr(after))
        return before,sel,after # 3 strings.
    #@-node:ekr.20031218072017.2377:getSelectionLines
    #@+node:ekr.20031218072017.4037:setSelectionAreas
    def setSelectionAreas (self,before,sel,after):

        """Replace the body text by before + sel + after and
        set the selection so that the sel text is selected."""

        body = self ; w = body.bodyCtrl
        s = w.getAllText()
        before = before or ''
        sel = sel or ''
        after = after or ''
        w.delete(0,len(s))
        w.insert(0,before+sel+after)
        i = len(before)
        j = max(i,len(before)+len(sel)-1)
        # g.trace(i,j,repr(sel))
        w.setSelectionRange(i,j,insert=j)
        return i,j
    #@-node:ekr.20031218072017.4037:setSelectionAreas
    #@+node:ekr.20031218072017.4038:get/setYScrollPosition
    def getYScrollPosition (self):
        return self.bodyCtrl.getYScrollPosition()

    def setYScrollPosition (self,scrollPosition):
        if len(scrollPosition) == 2:
            first,last = scrollPosition
        else:
            first = scrollPosition
        self.bodyCtrl.setYScrollPosition(first)
    #@-node:ekr.20031218072017.4038:get/setYScrollPosition
    #@-node:ekr.20031218072017.4018:Text (leoBody)
    #@+node:ekr.20070228080627:Text Wrappers (base class)
    def getAllText (self):                  return self.bodyCtrl.getAllText()
    def getInsertPoint(self):               return self.bodyCtrl.getInsertPoint()
    def getSelectedText (self):             return self.bodyCtrl.getSelectedText()
    def getSelectionRange (self,sort=True): return self.bodyCtrl.getSelectionRange(sort)
    def hasTextSelection (self):            return self.bodyCtrl.hasSelection()
    # def scrollDown (self):                g.app.gui.yscroll(self.bodyCtrl,1,'units')
    # def scrollUp (self):                  g.app.gui.yscroll(self.bodyCtrl,-1,'units')
    def see (self,index):                   self.bodyCtrl.see(index)
    def seeInsertPoint (self):              self.bodyCtrl.seeInsertPoint()
    def selectAllText (self,event=None): # This is a command.
        return self.bodyCtrl.selectAllText()
        # w = g.app.gui.eventWidget(event) or self.bodyCtrl
        # return w.selectAllText()
    def setInsertPoint (self,pos):          return self.bodyCtrl.setInsertPoint(pos) # was getInsertPoint.
    def setFocus(self):                     return self.bodyCtrl.setFocus()
    def setSelectionRange (self,sel):       i,j = sel ; self.bodyCtrl.setSelectionRange(i,j)
    #@-node:ekr.20070228080627:Text Wrappers (base class)
    #@-node:ekr.20061109173021:leoBody: must be defined in the base class
    #@+node:ekr.20081005065934.6:leoBody: may be defined in subclasses
    def initAfterLoad (self):
        pass
    #@nonl
    #@-node:ekr.20081005065934.6:leoBody: may be defined in subclasses
    #@-others
#@-node:ekr.20031218072017.3656:class leoBody
#@+node:ekr.20031218072017.3678:class leoFrame
class leoFrame:

    """The base class for all Leo windows."""

    instances = 0

    #@    @+others
    #@+node:ekr.20031218072017.3679:  leoFrame.__init__
    def __init__ (self,gui):

        self.c = None # Must be created by subclasses.
        self.gui = gui
        self.iconBarClass = nullIconBarClass
        self.statusLineClass = nullStatusLineClass
        self.title = None # Must be created by subclasses.

        # Objects attached to this frame.
        self.body = None
        self.colorPanel = None 
        self.comparePanel = None
        self.findPanel = None
        self.fontPanel = None
        self.iconBar = None
        self.isNullFrame = False
        self.keys = None
        self.log = None
        self.menu = None
        self.miniBufferWidget = None
        self.outerFrame = None
        self.prefsPanel = None
        self.statusLine = None
        self.tree = None
        self.useMiniBufferWidget = False

        # Gui-independent data
        self.componentsDict = {} # Keys are names, values are componentClass instances.
        self.es_newlines = 0 # newline count for this log stream
        self.openDirectory = ""
        self.saved=False # True if ever saved
        self.splitVerticalFlag,self.ratio, self.secondary_ratio = True,0.5,0.5 # Set by initialRatios later.
        self.startupWindow=False # True if initially opened window
        self.stylesheet = None # The contents of <?xml-stylesheet...?> line.
        self.tab_width = 0 # The tab width in effect in this pane.
    #@nonl
    #@+node:ekr.20080429051644.1:leoFrame.mustBeDefined
    # List of methods that must be defined either in the base class or a subclass.

    mustBeDefined = (

        # Icon bar convenience methods.    
        'addIconButton',
        'addIconRow',
        'clearIconBar',
        'createIconBar',
        'getIconBar',
        'getIconBarObject',
        'getNewIconFrame',
        'hideIconBar',
        'initAfterLoad',
        'initCompleteHint',
        'showIconBar',
    )
    #@nonl
    #@-node:ekr.20080429051644.1:leoFrame.mustBeDefined
    #@+node:ekr.20061109120726:leoFrame.mustBeDefinedOnlyInBaseClass
    mustBeDefinedOnlyInBaseClass = (

        'createFirstTreeNode', # New in Leo 4.6: was defined in tkTree.
        'initialRatios',
        'longFileName',
        'oops',
        'promptForSave',
        'scanForTabWidth',
        'shortFileName',

        # Headline editing.
        'abortEditLabelCommand',
        'endEditLabelCommand',
        'insertHeadlineTime',

        # Cut/Copy/Paste.
        'OnPaste',
        'OnPasteFromMenu',
        'copyText',
        'cutText',
        'pasteText',

        # Status line convenience methods.
        'createStatusLine',
        'clearStatusLine',
        'disableStatusLine',
        'enableStatusLine',
        'getStatusLine',
        'getStatusObject',
        'putStatusLine',
        'setFocusStatusLine',
        'statusLineIsEnabled',
        'updateStatusLine',
    )
    #@nonl
    #@-node:ekr.20061109120726:leoFrame.mustBeDefinedOnlyInBaseClass
    #@+node:ekr.20061109120704:leoFrame.mustBeDefinedInSubclasses
    mustBeDefinedInSubclasses = (
        #Gui-dependent commands.
        'cascade',
        'contractBodyPane',
        'contractLogPane',
        'contractOutlinePane',
        'contractPane',
        'equalSizedPanes',
        'expandLogPane',
        'expandPane',
        'fullyExpandBodyPane',
        'fullyExpandLogPane',
        'fullyExpandOutlinePane',
        'fullyExpandPane',
        'hideBodyPane',
        'hideLogPane',
        'hideLogWindow',
        'hideOutlinePane',
        'hidePane',
        'leoHelp',
        'minimizeAll',
        'resizeToScreen',
        'toggleActivePane',
        'toggleSplitDirection',
        # Windowutilities...
        'bringToFront',
        'deiconify',
        'get_window_info',
        'lift',
        'update',
        # Config...
        'resizePanesToRatio',
        'setInitialWindowGeometry',
        'setTopGeometry',
    )
    #@nonl
    #@-node:ekr.20061109120704:leoFrame.mustBeDefinedInSubclasses
    #@+node:ekr.20051009045404:createFirstTreeNode
    def createFirstTreeNode (self):

        f = self ; c = f.c

        v = leoNodes.vnode(context=c)
        p = leoNodes.position(v)
        v.initHeadString("NewHeadline")
        # New in Leo 4.5: p.moveToRoot would be wrong: the node hasn't been linked yet.
        p._linkAsRoot(oldRoot=None)
        c.setRootPosition(p) # New in 4.4.2.
        c.editPosition(p)
    #@-node:ekr.20051009045404:createFirstTreeNode
    #@-node:ekr.20031218072017.3679:  leoFrame.__init__
    #@+node:ekr.20061109125528.1:Must be defined in base class
    #@+node:ekr.20031218072017.3689:initialRatios
    def initialRatios (self):

        c = self.c

        s = c.config.get("initial_splitter_orientation","string")
        verticalFlag = s == None or (s != "h" and s != "horizontal")

        if verticalFlag:
            r = c.config.getRatio("initial_vertical_ratio")
            if r == None or r < 0.0 or r > 1.0: r = 0.5
            r2 = c.config.getRatio("initial_vertical_secondary_ratio")
            if r2 == None or r2 < 0.0 or r2 > 1.0: r2 = 0.8
        else:
            r = c.config.getRatio("initial_horizontal_ratio")
            if r == None or r < 0.0 or r > 1.0: r = 0.3
            r2 = c.config.getRatio("initial_horizontal_secondary_ratio")
            if r2 == None or r2 < 0.0 or r2 > 1.0: r2 = 0.8

        # g.trace(r,r2)
        return verticalFlag,r,r2
    #@-node:ekr.20031218072017.3689:initialRatios
    #@+node:ekr.20031218072017.3690:longFileName & shortFileName
    def longFileName (self):

        return self.c.mFileName

    def shortFileName (self):

        return g.shortFileName(self.c.mFileName)
    #@-node:ekr.20031218072017.3690:longFileName & shortFileName
    #@+node:ekr.20031218072017.3691:oops
    def oops(self):

        g.pr("leoFrame oops:", g.callers(4), "should be overridden in subclass")
    #@-node:ekr.20031218072017.3691:oops
    #@+node:ekr.20031218072017.3692:promptForSave
    def promptForSave (self):

        """Prompt the user to save changes.

        Return True if the user vetos the quit or save operation."""

        c = self.c
        name = g.choose(c.mFileName,c.mFileName,self.title)
        theType = g.choose(g.app.quitting, "quitting?", "closing?")

        answer = g.app.gui.runAskYesNoCancelDialog(c,
            "Confirm",
            'Save changes to %s before %s' % (name,theType))

        # g.pr(answer)
        if answer == "cancel":
            return True # Veto.
        elif answer == "no":
            return False # Don't save and don't veto.
        else:
            if not c.mFileName:
                #@            << Put up a file save dialog to set mFileName >>
                #@+node:ekr.20031218072017.3693:<< Put up a file save dialog to set mFileName >>
                # Make sure we never pass None to the ctor.
                if not c.mFileName:
                    c.mFileName = ""

                c.mFileName = g.app.gui.runSaveFileDialog(
                    initialfile = c.mFileName,
                    title="Save",
                    filetypes=[("Leo files", "*.leo")],
                    defaultextension=".leo")
                c.bringToFront()
                #@-node:ekr.20031218072017.3693:<< Put up a file save dialog to set mFileName >>
                #@nl
            if c.mFileName:
                ok = c.fileCommands.save(c.mFileName)
                return not ok # New in 4.2: Veto if the save did not succeed.
            else:
                return True # Veto.
    #@-node:ekr.20031218072017.3692:promptForSave
    #@+node:ekr.20031218072017.1375:frame.scanForTabWidth
    def scanForTabWidth (self,p):

        c = self.c ; w = c.tab_width

        aList = g.get_directives_dict_list(p)
        w = g.scanAtTabwidthDirectives(aList)
        c.frame.setTabWidth(w or c.tab_width)
    #@-node:ekr.20031218072017.1375:frame.scanForTabWidth
    #@+node:ekr.20061119120006:Icon area convenience methods
    def addIconButton (self,*args,**keys):
        if self.iconBar: return self.iconBar.add(*args,**keys)
        else: return None

    def addIconRow(self):
        if self.iconBar: return self.iconBar.addRow()

    def addIconWidget(self,w):
        if self.iconBar: return self.iconBar.addWidget(w)

    def clearIconBar (self):
        if self.iconBar: self.iconBar.clear()

    def createIconBar (self):
        if not self.iconBar:
            self.iconBar = self.iconBarClass(self.c,self.outerFrame)
        return self.iconBar

    def getIconBar(self):
        if not self.iconBar:
            self.iconBar = self.iconBarClass(self.c,self.outerFrame)
        return self.iconBar

    getIconBarObject = getIconBar

    def getNewIconFrame (self):
        if not self.iconBar:
            self.iconBar = self.iconBarClass(self.c,self.outerFrame)
        return self.iconBar.getNewFrame()

    def hideIconBar (self):
        if self.iconBar: self.iconBar.hide()

    def showIconBar (self):
        if self.iconBar: self.iconBar.show()
    #@-node:ekr.20061119120006:Icon area convenience methods
    #@+node:ekr.20041223105114.1:Status line convenience methods
    def createStatusLine (self):
        if not self.statusLine:
            self.statusLine = self.statusLineClass(self.c,self.outerFrame)
        return self.statusLine

    def clearStatusLine (self):
        if self.statusLine: self.statusLine.clear()

    def disableStatusLine (self,background=None):
        if self.statusLine: self.statusLine.disable(background)

    def enableStatusLine (self,background="white"):
        if self.statusLine: self.statusLine.enable(background)

    def getStatusLine (self):
        return self.statusLine

    getStatusObject = getStatusLine

    def putStatusLine (self,s,color=None):
        if self.statusLine: self.statusLine.put(s,color)

    def setFocusStatusLine (self):
        if self.statusLine: self.statusLine.setFocus()

    def statusLineIsEnabled(self):
        if self.statusLine: return self.statusLine.isEnabled()
        else: return False

    def updateStatusLine(self):
        if self.statusLine: self.statusLine.update()
    #@nonl
    #@-node:ekr.20041223105114.1:Status line convenience methods
    #@+node:ekr.20070130115927.4:Cut/Copy/Paste (leoFrame)
    #@+node:ekr.20070130115927.5:copyText
    def copyText (self,event=None):

        '''Copy the selected text from the widget to the clipboard.'''

        f = self ; c = f.c ; w = event and event.widget
        if not w or not g.app.gui.isTextWidget(w): return

        # Set the clipboard text.
        i,j = w.getSelectionRange()
        if i != j:
            s = w.get(i,j)
            g.app.gui.replaceClipboardWith(s)

    OnCopyFromMenu = copyText
    #@-node:ekr.20070130115927.5:copyText
    #@+node:ekr.20070130115927.6:leoFrame.cutText
    def cutText (self,event=None):

        '''Invoked from the mini-buffer and from shortcuts.'''

        f = self ; c = f.c ; w = event and event.widget
        if not w or not g.app.gui.isTextWidget(w): return

        name = c.widget_name(w)
        oldSel = w.getSelectionRange()
        oldText = w.getAllText()
        i,j = w.getSelectionRange()

        # Update the widget and set the clipboard text.
        s = w.get(i,j)
        if i != j:
            w.delete(i,j)
            g.app.gui.replaceClipboardWith(s)

        if name.startswith('body'):
            c.frame.body.forceFullRecolor()
            c.frame.body.onBodyChanged('Cut',oldSel=oldSel,oldText=oldText)
        elif name.startswith('head'):
            # The headline is not officially changed yet.
            # p.initHeadString(s)
            s = w.getAllText()
            width = f.tree.headWidth(p=None,s=s)
            w.setWidth(width)
        else: pass

    OnCutFromMenu = cutText
    #@-node:ekr.20070130115927.6:leoFrame.cutText
    #@+node:ekr.20070130115927.7:leoFrame.pasteText
    def pasteText (self,event=None,middleButton=False):

        '''Paste the clipboard into a widget.
        If middleButton is True, support x-windows middle-mouse-button easter-egg.'''

        f = self ; c = f.c ; w = event and event.widget
        # g.trace('isText',g.app.gui.isTextWidget(w),w)
        if not w or not g.app.gui.isTextWidget(w): return

        wname = c.widget_name(w)
        i,j = oldSel = w.getSelectionRange()  # Returns insert point if no selection.
        oldText = w.getAllText()

        if middleButton and c.k.previousSelection is not None:
            start,end = c.k.previousSelection
            s = w.getAllText()
            s = s[start:end]
            c.k.previousSelection = None
        else:
            s = s1 = g.app.gui.getTextFromClipboard()

        s = g.toUnicode(s,encoding=g.app.tkEncoding)

        # g.trace('pasteText','wname',wname,'s',s,g.callers())

        singleLine = wname.startswith('head') or wname.startswith('minibuffer')

        if singleLine:
            # Strip trailing newlines so the truncation doesn't cause confusion.
            while s and s [ -1] in ('\n','\r'):
                s = s [: -1]

        try:
            # Update the widget.
            if i != j:
                w.delete(i,j)
            w.insert(i,s)

            if wname.startswith('body'):
                c.frame.body.forceFullRecolor()
                c.frame.body.onBodyChanged('Paste',oldSel=oldSel,oldText=oldText)
            elif singleLine:
                s = w.getAllText()
                while s and s [ -1] in ('\n','\r'):
                    s = s [: -1]
                if wname.startswith('head'):
                    # The headline is not officially changed yet.
                    # p.initHeadString(s)
                    width = f.tree.headWidth(p=None,s=s)
                    w.setWidth(width)
            else: pass
        except Exception:
            pass # Tk sometimes throws weird exceptions here.

        return 'break' # Essential

    OnPasteFromMenu = pasteText
    #@-node:ekr.20070130115927.7:leoFrame.pasteText
    #@+node:ekr.20061016071937:OnPaste (To support middle-button paste)
    def OnPaste (self,event=None):

        return self.pasteText(event=event,middleButton=True)
    #@nonl
    #@-node:ekr.20061016071937:OnPaste (To support middle-button paste)
    #@-node:ekr.20070130115927.4:Cut/Copy/Paste (leoFrame)
    #@+node:ekr.20031218072017.3980:Edit Menu... (leoFrame)
    #@+node:ekr.20031218072017.3981:abortEditLabelCommand (leoFrame)
    def abortEditLabelCommand (self,event=None):

        '''End editing of a headline and revert to its previous value.'''

        frame = self ; c = frame.c ; tree = frame.tree
        p = c.currentPosition() ; w = c.edit_widget(p)

        if g.app.batchMode:
            c.notValidInBatchMode("Abort Edit Headline")
            return

        # g.trace('isEditing',p == tree.editPosition(),'revertHeadline',repr(tree.revertHeadline))

        if w and p == tree.editPosition():
            # Revert the headline text.
            w.delete(0,"end")
            w.insert("end",tree.revertHeadline)
            p.initHeadString(tree.revertHeadline)
            c.endEditing()
            c.selectPosition(p)
            c.redraw()
    #@-node:ekr.20031218072017.3981:abortEditLabelCommand (leoFrame)
    #@+node:ekr.20031218072017.3982:frame.endEditLabelCommand
    def endEditLabelCommand (self,event=None):

        '''End editing of a headline and move focus to the body pane.'''

        frame = self ; c = frame.c ; k = c.k
        if g.app.batchMode:
            c.notValidInBatchMode("End Edit Headline")
        else:
            c.endEditing()
            # g.trace('setting focus')
            if c.config.getBool('stayInTreeAfterEditHeadline'):
                c.treeWantsFocusNow()
            else:
                c.bodyWantsFocusNow()

                if k:
                    k.setDefaultInputState()
                    # Recolor the *body* text, **not** the headline.
                    k.showStateAndMode(w=c.frame.body.bodyCtrl)
    #@-node:ekr.20031218072017.3982:frame.endEditLabelCommand
    #@+node:ekr.20031218072017.3983:insertHeadlineTime
    def insertHeadlineTime (self,event=None):

        '''Insert a date/time stamp in the headline of the selected node.'''

        frame = self ; c = frame.c ; p = c.currentPosition()

        if g.app.batchMode:
            c.notValidInBatchMode("Insert Headline Time")
            return

        c.editPosition(p)
        c.frame.tree.setEditLabelState(p)
        w = c.edit_widget(p)
        if w:
            time = c.getTime(body=False)
            if 1: # We can't know if we were already editing, so insert at end.
                w.setSelectionRange('end','end')
                w.insert('end',time)
            else:
                i, j = w.getSelectionRange()
                if i != j: w.delete(i,j)
                w.insert("insert",time)
            c.frame.tree.onHeadChanged(p,'Insert Headline Time')
    #@-node:ekr.20031218072017.3983:insertHeadlineTime
    #@-node:ekr.20031218072017.3980:Edit Menu... (leoFrame)
    #@-node:ekr.20061109125528.1:Must be defined in base class
    #@+node:ekr.20031218072017.3680:Must be defined in subclasses
    #@+node:ekr.20031218072017.3683:Config...
    def resizePanesToRatio (self,ratio,secondary_ratio):    self.oops()
    def setInitialWindowGeometry (self):                    self.oops()
    def setTopGeometry (self,w,h,x,y,adjustSize=True):      self.oops()
    #@-node:ekr.20031218072017.3683:Config...
    #@+node:ekr.20031218072017.3681:Gui-dependent commands
    # In the Edit menu...

    def OnCopy  (self,event=None): self.oops()
    def OnCut   (self,event=None): self.oops()

    #def OnCutFromMenu  (self,event=None):     self.oops()
    #def OnCopyFromMenu (self,event=None):     self.oops()

    # Expanding and contracting panes.
    def contractPane         (self,event=None): self.oops()
    def expandPane           (self,event=None): self.oops()
    def contractBodyPane     (self,event=None): self.oops()
    def contractLogPane      (self,event=None): self.oops()
    def contractOutlinePane  (self,event=None): self.oops()
    def expandBodyPane       (self,event=None): self.oops()
    def expandLogPane        (self,event=None): self.oops()
    def expandOutlinePane    (self,event=None): self.oops()
    def fullyExpandBodyPane  (self,event=None): self.oops()
    def fullyExpandLogPane   (self,event=None): self.oops()
    def fullyExpandPane      (self,event=None): self.oops()
    def fullyExpandOutlinePane (self,event=None): self.oops()
    def hideBodyPane         (self,event=None): self.oops()
    def hideLogPane          (self,event=None): self.oops()
    def hidePane             (self,event=None): self.oops()
    def hideOutlinePane      (self,event=None): self.oops()

    # In the Window menu...
    def cascade              (self,event=None): self.oops()
    def equalSizedPanes      (self,event=None): self.oops()
    def hideLogWindow        (self,event=None): self.oops()
    def minimizeAll          (self,event=None): self.oops()
    def resizeToScreen       (self,event=None): self.oops()
    def toggleActivePane     (self,event=None): self.oops()
    def toggleSplitDirection (self,event=None): self.oops()

    # In help menu...
    def leoHelp (self,event=None): self.oops()
    #@-node:ekr.20031218072017.3681:Gui-dependent commands
    #@+node:ekr.20031218072017.3682:Window...
    # Important: nothing would be gained by calling gui versions of these methods:
    #            they can be defined in a gui-dependent way in a subclass.

    def bringToFront (self):    self.oops()
    def deiconify (self):       self.oops()
    def get_window_info(self):  self.oops()
    def lift (self):            self.oops()
    def update (self):          self.oops()
    #@-node:ekr.20031218072017.3682:Window...
    #@-node:ekr.20031218072017.3680:Must be defined in subclasses
    #@+node:ekr.20061109125528:May be defined in subclasses
    #@+node:ekr.20071027150501:event handlers (leoFrame)
    def OnBodyClick (self,event=None):
        pass

    def OnBodyRClick(self,event=None):
        pass
    #@nonl
    #@-node:ekr.20071027150501:event handlers (leoFrame)
    #@+node:ekr.20031218072017.3688:getTitle & setTitle
    def getTitle (self):
        return self.title

    def setTitle (self,title):
        self.title = title
    #@-node:ekr.20031218072017.3688:getTitle & setTitle
    #@+node:ekr.20081005065934.3:initAfterLoad  & initCompleteHint (leoFrame)
    def initAfterLoad (self):

        '''Provide offical hooks for late inits of components of Leo frames.'''

        frame = self

        frame.body.initAfterLoad()
        frame.log.initAfterLoad()
        frame.menu.initAfterLoad()
        # if frame.miniBufferWidget: frame.miniBufferWidget.initAfterLoad()
        frame.tree.initAfterLoad()

    def initCompleteHint (self):
        pass
    #@nonl
    #@-node:ekr.20081005065934.3:initAfterLoad  & initCompleteHint (leoFrame)
    #@+node:ekr.20031218072017.3687:setTabWidth (leoFrame)
    def setTabWidth (self,w):

        # Subclasses may override this to affect drawing.
        self.tab_width = w
    #@-node:ekr.20031218072017.3687:setTabWidth (leoFrame)
    #@-node:ekr.20061109125528:May be defined in subclasses
    #@+node:ekr.20060206093313:Focus (leoFrame)
    # For compatibility with old scripts.
    # Using the commander methods directly is recommended.

    def getFocus(self):
        return g.app.gui.get_focus(self.c) # Used by wxGui plugin.

    def bodyWantsFocus(self):
        return self.c.bodyWantsFocus()

    def headlineWantsFocus(self,p):
        return self.c.headlineWantsFocus(p)

    def logWantsFocus(self):
        return self.c.logWantsFocus()

    def minibufferWantsFocus(self):
        return self.c.minibufferWantsFocus()
    #@-node:ekr.20060206093313:Focus (leoFrame)
    #@-others
#@-node:ekr.20031218072017.3678:class leoFrame
#@+node:ekr.20031218072017.3694:class leoLog
class leoLog:

    """The base class for the log pane in Leo windows."""

    #@    @+others
    #@+node:ekr.20031218072017.3695: ctor (leoLog)
    def __init__ (self,frame,parentFrame):

        self.frame = frame
        if frame: # 7/16/05: Allow no commander for Null logs.
            self.c = frame.c
        else:
            self.c = None
        self.enabled = True
        self.newlines = 0
        self.isNull = False

        # Official status variables.  Can be used by client code.
        self.canvasCtrl = None # Set below. Same as self.canvasDict.get(self.tabName)
        self.logCtrl = None # Set below. Same as self.textDict.get(self.tabName)
        self.tabName = None # The name of the active tab.
        self.tabFrame = None # Same as self.frameDict.get(self.tabName)

        self.canvasDict = {} # Keys are page names.  Values are Tk.Canvas's.
        self.frameDict = {}  # Keys are page names. Values are Tk.Frames.
        self.logNumber = 0 # To create unique name fields for text widgets.
        self.newTabCount = 0 # Number of new tabs created.
        self.textDict = {}  # Keys are page names. Values are logCtrl's (text widgets).


    #@-node:ekr.20031218072017.3695: ctor (leoLog)
    #@+node:ekr.20070302101344:Must be defined in the base class
    def onActivateLog (self,event=None):

        self.c.setLog()

    def disable (self):

        self.enabled = False

    def enable (self,enabled=True):

        self.enabled = enabled

    #@-node:ekr.20070302101344:Must be defined in the base class
    #@+node:ekr.20070302101023:May be overridden
    def configure (self,*args,**keys):              pass
    def configureBorder(self,border):               pass
    def createControl (self,parentFrame):           pass
    def createCanvas (self,tabName):                pass
    def createTextWidget (self,parentFrame):        return None
    def finishCreate (self):                        pass
    def initAfterLoad (self):                       pass
    def setColorFromConfig (self):                  pass
    def setFontFromConfig (self):                   pass
    def setTabBindings  (self,tabName):             pass
    #@+node:ekr.20070302094848.1:clearTab
    def clearTab (self,tabName,wrap='none'):

        self.selectTab(tabName,wrap=wrap)
        w = self.logCtrl
        if w: w.delete(0,'end')
    #@-node:ekr.20070302094848.1:clearTab
    #@+node:ekr.20070302094848.2:createTab
    def createTab (self,tabName,createText=True,wrap='none'):

        # g.trace(tabName,wrap)

        c = self.c ; k = c.k

        if createText:
            w = self.createTextWidget(self.tabFrame)
            self.canvasDict [tabName] = None
            self.textDict [tabName] = w
        else:
            self.canvasDict [tabName] = None
            self.textDict [tabName] = None
            self.frameDict [tabName] = tabName # tabFrame


    #@-node:ekr.20070302094848.2:createTab
    #@+node:ekr.20070302094848.4:cycleTabFocus
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
    #@-node:ekr.20070302094848.4:cycleTabFocus
    #@+node:ekr.20070302094848.5:deleteTab
    def deleteTab (self,tabName,force=False):

        if tabName == 'Log':
            pass
        elif tabName in ('Find','Spell') and not force:
            self.selectTab('Log')
        else:
            for d in (self.canvasDict,self.textDict,self.frameDict):
                if tabName in d:
                    del d[tabName]
            self.tabName = None
            self.selectTab('Log')

        self.c.invalidateFocus()
        self.c.bodyWantsFocus()
    #@-node:ekr.20070302094848.5:deleteTab
    #@+node:ekr.20070302094848.6:hideTab
    def hideTab (self,tabName):

        self.selectTab('Log')
    #@-node:ekr.20070302094848.6:hideTab
    #@+node:ekr.20070302094848.7:getSelectedTab
    def getSelectedTab (self):

        return self.tabName
    #@-node:ekr.20070302094848.7:getSelectedTab
    #@+node:ekr.20070302094848.8:lower/raiseTab
    def lowerTab (self,tabName):

        self.c.invalidateFocus()
        self.c.bodyWantsFocus()

    def raiseTab (self,tabName):

        self.c.invalidateFocus()
        self.c.bodyWantsFocus()
    #@-node:ekr.20070302094848.8:lower/raiseTab
    #@+node:ekr.20070302094848.9:numberOfVisibleTabs
    def numberOfVisibleTabs (self):

        return len([val for val in self.frameDict.values() if val != None])
    #@-node:ekr.20070302094848.9:numberOfVisibleTabs
    #@+node:ekr.20070302094848.10:renameTab
    def renameTab (self,oldName,newName):
        pass
    #@-node:ekr.20070302094848.10:renameTab
    #@+node:ekr.20070302094848.11:selectTab
    def selectTab (self,tabName,createText=True,wrap='none'):

        '''Create the tab if necessary and make it active.'''

        c = self.c
        tabFrame = self.frameDict.get(tabName)
        if not tabFrame:
            self.createTab(tabName,createText=createText)

        # Update the status vars.
        self.tabName = tabName
        self.canvasCtrl = self.canvasDict.get(tabName)
        self.logCtrl = self.textDict.get(tabName)
        self.tabFrame = self.frameDict.get(tabName)

        if 0:
            # Absolutely do not do this here!
            # It is a cause of the 'sticky focus' problem.
            c.widgetWantsFocusNow(self.logCtrl)

        return tabFrame
    #@-node:ekr.20070302094848.11:selectTab
    #@-node:ekr.20070302101023:May be overridden
    #@+node:ekr.20070302101304:Must be overridden
    # All output to the log stream eventually comes here.

    def put (self,s,color=None,tabName='Log'):
        print (s)

    def putnl (self,tabName='Log'):
        pass # print ('')
    #@-node:ekr.20070302101304:Must be overridden
    #@+node:ekr.20031218072017.3700:leoLog.oops
    def oops (self):

        g.pr("leoLog oops:", g.callers(4), "should be overridden in subclass")
    #@-node:ekr.20031218072017.3700:leoLog.oops
    #@-others
#@-node:ekr.20031218072017.3694:class leoLog
#@+node:ekr.20031218072017.3704:class leoTree
# This would be useful if we removed all the tree redirection routines.
# However, those routines are pretty ingrained into Leo...

class leoTree:

    """The base class for the outline pane in Leo windows."""

    #@    @+others
    #@+node:ekr.20031218072017.3705:  tree.__init__ (base class)
    def __init__ (self,frame):

        self.frame = frame
        self.c = frame.c

        self.edit_text_dict = {}
            # New in 3.12: keys vnodes, values are edit_widget (Tk.Text widgets)
            # New in 4.2: keys are vnodes, values are pairs (p,Tk.Text).

        # "public" ivars: correspond to setters & getters.
        self._editPosition = None
        self.redrawCount = 0 # For traces
        self.revertHeadline = None
        self.use_chapters = False # May be overridden in subclasses.

        # Define these here to keep pylint happy.
        self.canvas = None
        self.stayInTree = True
        self.trace_select = None
    #@+node:ekr.20081005065934.7:leoTree.mustBeDefined
    # List of methods that must be defined either in the base class or a subclass.

    mustBeDefined = (
        'initAfterLoad', # New in Leo 4.6.
        'treeSelectHint', # New in Leo 4.6.
    )
    #@nonl
    #@-node:ekr.20081005065934.7:leoTree.mustBeDefined
    #@+node:ekr.20061109164512:leoTree.mustBeDefinedOnlyInBaseClass
    mustBeDefinedOnlyInBaseClass = (
        # Getters & setters.
        'editPosition',
        'getEditTextDict',
        'setEditPosition',
        # Others.
        'endEditLabel',
        'expandAllAncestors',
        'injectCallbacks',
        'OnIconDoubleClick',
        'onHeadChanged',
        'onHeadlineKey',
        'updateHead',
        'oops',
    )
    #@nonl
    #@-node:ekr.20061109164512:leoTree.mustBeDefinedOnlyInBaseClass
    #@+node:ekr.20061109164610:leoTree.mustBeDefinedInSubclasses
    mustBeDefinedInSubclasses = (
        # Colors & fonts.
        'getFont',
        'setFont',
        'setFontFromConfig ',
        # Drawing & scrolling.
        'drawIcon',
        'redraw_now',
        'scrollTo',
        # Headlines.
        'editLabel',
        'setEditLabelState',
        # Selecting.
        # 'select', # Defined in base class, may be overridden in do-nothing subclasses.
    )
    #@-node:ekr.20061109164610:leoTree.mustBeDefinedInSubclasses
    #@-node:ekr.20031218072017.3705:  tree.__init__ (base class)
    #@+node:ekr.20031218072017.3706: Must be defined in subclasses
    # Bidings.
    def setBindings (self):                         self.oops()

    # Fonts.
    def getFont(self):                              self.oops()
    def setFont(self,font=None,fontName=None):      self.oops()
    def setFontFromConfig (self):                   self.oops()

    # Drawing & scrolling.
    def drawIcon(self,v,x=None,y=None):             self.oops()
    def redraw_now(self,scroll=True,forceDraw=False):   self.oops()
    def scrollTo(self,p):                           self.oops()
    idle_scrollTo = scrollTo # For compatibility.

    # Headlines.
    def editLabel(self,v,selectAll=False):          self.oops()
    def edit_widget (self,p):                       self.oops() ; return None
    def headWidth(self,p=None,s=''):                self.oops() ; return 0
    def setEditLabelState(self,v,selectAll=False):  self.oops()
    def setSelectedLabelState(self,p):              self.oops()
    def setUnselectedLabelState(self,p):            self.oops()
    #@nonl
    #@-node:ekr.20031218072017.3706: Must be defined in subclasses
    #@+node:ekr.20061109165848:Must be defined in base class
    #@+node:ekr.20031218072017.3716:Getters/Setters (tree)
    def getEditTextDict(self,v):
        # New in 4.2: the default is an empty list.
        return self.edit_text_dict.get(v,[])

    def editPosition(self):
        return self._editPosition

    def setEditPosition(self,p):
        self._editPosition = p
    #@-node:ekr.20031218072017.3716:Getters/Setters (tree)
    #@+node:ekr.20040803072955.90:head key handlers (leoTree)
    #@+node:ekr.20040803072955.91:onHeadChanged
    # Tricky code: do not change without careful thought and testing.

    def onHeadChanged (self,p,undoType='Typing',s=None):

        '''Officially change a headline.
        Set the old undo text to the previous revert point.'''

        c = self.c ; u = c.undoer ; w = c.edit_widget(p)
        if c.suppressHeadChanged: return
        if not w: return

        ch = '\n' # New in 4.4: we only report the final keystroke.
        if g.doHook("headkey1",c=c,p=p,v=p,ch=ch):
            return # The hook claims to have handled the event.

        if s is None: s = w.getAllText()
        #@    << truncate s if it has multiple lines >>
        #@+node:ekr.20040803072955.94:<< truncate s if it has multiple lines >>
        # Remove one or two trailing newlines before warning of truncation.
        for i in (0,1):
            if s and s[-1] == '\n':
                if len(s) > 1: s = s[:-1]
                else: s = ''

        # Warn if there are multiple lines.
        i = s.find('\n')
        if i > -1:
            # g.trace(i,len(s),repr(s))
            g.es("truncating headline to one line",color="blue")
            s = s[:i]

        limit = 1000
        if len(s) > limit:
            g.es("truncating headline to",limit,"characters",color="blue")
            s = s[:limit]

        s = g.toUnicode(s or '',g.app.tkEncoding)
        #@-node:ekr.20040803072955.94:<< truncate s if it has multiple lines >>
        #@nl
        # Make the change official, but undo to the *old* revert point.
        oldRevert = self.revertHeadline
        changed = s != oldRevert
        self.revertHeadline = s
        p.initHeadString(s)
        # g.trace('changed',changed,'old',repr(oldRevert),'new',repr(s))
        # g.trace(g.callers())
        if changed:
            undoData = u.beforeChangeNodeContents(p,oldHead=oldRevert)
            if not c.changed: c.setChanged(True)
            # New in Leo 4.4.5: we must recolor the body because
            # the headline may contain directives.
            c.frame.scanForTabWidth(p)
            c.frame.body.recolor(p,incremental=True)
            dirtyVnodeList = p.setDirty()
            u.afterChangeNodeContents(p,undoType,undoData,
                dirtyVnodeList=dirtyVnodeList)
        if changed:
            c.redraw(scroll=False)
            if self.stayInTree:
                c.treeWantsFocus()
            else:
                c.bodyWantsFocus()
        else:
            c.frame.tree.setSelectedLabelState(p)

        g.doHook("headkey2",c=c,p=p,v=p,ch=ch)
    #@-node:ekr.20040803072955.91:onHeadChanged
    #@+node:ekr.20040803072955.88:onHeadlineKey
    def onHeadlineKey (self,event):

        '''Handle a key event in a headline.'''

        w = event and event.widget or None
        ch = event and event.char or ''

        # g.trace(repr(ch),g.callers())

        # Testing for ch here prevents flashing in the headline
        # when the control key is held down.
        if ch:
            # g.trace(repr(ch),g.callers())
            self.updateHead(event,w)

        return 'break' # Required
    #@-node:ekr.20040803072955.88:onHeadlineKey
    #@+node:ekr.20051026083544.2:updateHead
    def updateHead (self,event,w):

        '''Update a headline from an event.

        The headline officially changes only when editing ends.'''

        c = self.c ; k = c.k
        ch = event and event.char or ''
        i,j = w.getSelectionRange()
        ins = w.getInsertPoint()
        if i != j: ins = i

        # g.trace('w',w,'ch',repr(ch),g.callers())

        if ch == '\b':
            if i != j:  w.delete(i,j)
            else:       w.delete(ins-1)
            w.setSelectionRange(i-1,i-1,insert=i-1)
        elif ch and ch not in ('\n','\r'):
            if i != j:                              w.delete(i,j)
            elif k.unboundKeyAction == 'overwrite': w.delete(i,i+1)
            w.insert(ins,ch)
            w.setSelectionRange(ins+1,ins+1,insert=ins+1)

        s = w.getAllText()
        if s.endswith('\n'):
            # g.trace('can not happen: trailing newline')
            s = s[:-1]
        w.setWidth(self.headWidth(s=s))

        if ch in ('\n','\r'):
            self.endEditLabel() # Now calls self.onHeadChanged.
    #@-node:ekr.20051026083544.2:updateHead
    #@+node:ekr.20040803072955.126:endEditLabel
    def endEditLabel (self):

        '''End editing of a headline and update p.headString().'''

        c = self.c ; k = c.k ; p = c.currentPosition()

        self.setEditPosition(None) # That is, self._editPosition = None

        # Important: this will redraw if necessary.
        self.onHeadChanged(p)

        if 0: # Can't call setDefaultUnboundKeyAction here: it might put us in ignore mode!
            k.setDefaultInputState()
            k.showStateAndMode()

        if 0: # This interferes with the find command and interferes with focus generally!
            c.bodyWantsFocus()
    #@-node:ekr.20040803072955.126:endEditLabel
    #@-node:ekr.20040803072955.90:head key handlers (leoTree)
    #@+node:ekr.20040803072955.143:tree.expandAllAncestors
    def expandAllAncestors (self,p):

        '''Expand all ancestors without redrawing.

        Return a flag telling whether a redraw is needed.'''

        c = self.c ; cc = c.chapterController ; redraw_flag = False
        # inChapter = cc and cc.inChapter()

        for p in p.parents_iter():
            # g.trace('testing',p)
            if cc and p.headString().startswith('@chapter'):
                break
            if not p.isExpanded():
                # g.trace('inChapter',inChapter,'p',p,g.callers())
                p.expand()
                redraw_flag = True

        return redraw_flag
    #@-node:ekr.20040803072955.143:tree.expandAllAncestors
    #@+node:ekr.20040803072955.21:tree.injectCallbacks
    def injectCallbacks(self):

        c = self.c

        #@    << define callbacks to be injected in the position class >>
        #@+node:ekr.20040803072955.22:<< define callbacks to be injected in the position class >>
        # N.B. These vnode methods are entitled to know about details of the leoTkinterTree class.

        #@+others
        #@+node:ekr.20040803072955.23:OnHyperLinkControlClick
        def OnHyperLinkControlClick (self,event=None,c=c):

            """Callback injected into position class."""

            p = self
            if not c or not c.exists:
                return

            try:
                if not g.doHook("hypercclick1",c=c,p=p,v=p,event=event):
                    c.selectPosition(p)
                    c.redraw()
                    c.frame.body.bodyCtrl.setInsertPoint(0) # 2007/10/27
                g.doHook("hypercclick2",c=c,p=p,v=p,event=event)
            except:
                g.es_event_exception("hypercclick")
        #@-node:ekr.20040803072955.23:OnHyperLinkControlClick
        #@+node:ekr.20040803072955.24:OnHyperLinkEnter
        def OnHyperLinkEnter (self,event=None,c=c):

            """Callback injected into position class."""

            try:
                p = self
                if not g.doHook("hyperenter1",c=c,p=p,v=p,event=event):
                    if 0: # This works, and isn't very useful.
                        c.frame.body.bodyCtrl.tag_config(p.tagName,background="green") # 10/27/07
                g.doHook("hyperenter2",c=c,p=p,v=p,event=event)
            except:
                g.es_event_exception("hyperenter")
        #@-node:ekr.20040803072955.24:OnHyperLinkEnter
        #@+node:ekr.20040803072955.25:OnHyperLinkLeave
        def OnHyperLinkLeave (self,event=None,c=c):

            """Callback injected into position class."""

            try:
                p = self
                if not g.doHook("hyperleave1",c=c,p=p,v=p,event=event):
                    if 0: # This works, and isn't very useful.
                        c.frame.body.bodyCtrl.tag_config(p.tagName,background="white") # 2007/20/25

                g.doHook("hyperleave2",c=c,p=p,v=p,event=event)
            except:
                g.es_event_exception("hyperleave")
        #@-node:ekr.20040803072955.25:OnHyperLinkLeave
        #@-others
        #@-node:ekr.20040803072955.22:<< define callbacks to be injected in the position class >>
        #@nl

        for f in (OnHyperLinkControlClick,OnHyperLinkEnter,OnHyperLinkLeave):

            g.funcToMethod(f,leoNodes.position)
    #@nonl
    #@-node:ekr.20040803072955.21:tree.injectCallbacks
    #@+node:ekr.20031218072017.2312:tree.OnIconDoubleClick (@url) & helper
    def OnIconDoubleClick (self,p):

        # Note: "icondclick" hooks handled by vnode callback routine.

        c = self.c
        s = p.headString().strip()
        if g.match_word(s,0,"@url"):
            url = s[4:].strip()
            if url.lstrip().startswith('--'):
                # Get the url from the first body line.
                lines = p.bodyString().split('\n')
                url = lines and lines[0] or ''
            else:
                #@            << stop the url after any whitespace >>
                #@+node:ekr.20031218072017.2313:<< stop the url after any whitespace  >>
                # For safety, the URL string should end at the first whitespace, unless quoted.
                # This logic is also found in the UNL plugin so we don't have to change the 'unl1' hook.

                url = url.replace('\t',' ')

                # Strip quotes.
                i = -1
                if url and url[0] in ('"',"'"):
                    i = url.find(url[0],1)
                    if i > -1:
                        url = url[1:i]

                if i == -1:
                    # Not quoted or no matching quote.
                    i = url.find(' ')
                    if i > -1:
                        if 0: # No need for a warning.  Assume everything else is a comment.
                            z_url = url[i:]
                            g.es("ignoring characters after space in url:",z_url)
                            g.es("use %20 instead of spaces")
                        url = url[:i]
                #@-node:ekr.20031218072017.2313:<< stop the url after any whitespace  >>
                #@nl
            if not g.doHook("@url1",c=c,p=p,v=p,url=url):
                self.handleUrlInUrlNode(url)
            g.doHook("@url2",c=c,p=p,v=p)

        return 'break' # 11/19/06
    #@nonl
    #@+node:ekr.20061030161842:handleUrlInUrlNode
    def handleUrlInUrlNode(self,url):

        # Note: the UNL plugin has its own notion of what a good url is.

        c = self.c
        # g.trace(url)
        #@    << check the url; return if bad >>
        #@+node:ekr.20031218072017.2314:<< check the url; return if bad >>
        #@+at 
        #@nonl
        # A valid url is (according to D.T.Hein):
        # 
        # 3 or more lowercase alphas, followed by,
        # one ':', followed by,
        # one or more of: (excludes !"#;<>[\]^`|)
        #   $%&'()*+,-./0-9:=?@A-Z_a-z{}~
        # followed by one of: (same as above, except no minus sign or comma).
        #   $%&'()*+/0-9:=?@A-Z_a-z}~
        #@-at
        #@@c

        urlPattern = "[a-z]{3,}:[\$-:=?-Z_a-z{}~]+[\$-+\/-:=?-Z_a-z}~]"

        if not url or len(url) == 0:
            g.es("no url following @url")
            return

        # Add http:// if required.
        if not re.match('^([a-z]{3,}:)',url):
            url = 'http://' + url
        if not re.match(urlPattern,url):
            g.es("invalid url:",url)
            return
        #@nonl
        #@-node:ekr.20031218072017.2314:<< check the url; return if bad >>
        #@nl
        #@    << pass the url to the web browser >>
        #@+node:ekr.20031218072017.2315:<< pass the url to the web browser >>
        #@+at 
        #@nonl
        # Most browsers should handle the following urls:
        #   ftp://ftp.uu.net/public/whatever.
        #   http://localhost/MySiteUnderDevelopment/index.html
        #   file://home/me/todolist.html
        #@-at
        #@@c

        try:
            import os
            os.chdir(g.app.loadDir)
            if g.match(url,0,"file:") and url[-4:]==".leo":
                ok,frame = g.openWithFileName(url[5:],c)
            else:
                import webbrowser
                # Mozilla throws a weird exception, then opens the file!
                try: webbrowser.open(url)
                except: pass
        except:
            g.es("exception opening",url)
            g.es_exception()
        #@-node:ekr.20031218072017.2315:<< pass the url to the web browser >>
        #@nl
    #@-node:ekr.20061030161842:handleUrlInUrlNode
    #@-node:ekr.20031218072017.2312:tree.OnIconDoubleClick (@url) & helper
    #@-node:ekr.20061109165848:Must be defined in base class
    #@+node:ekr.20081005065934.8:May be defined in subclasses
    # These are new in Leo 4.6.

    def initAfterLoad (self):
        '''Do late initialization.
        Called in g.openWithFileName after a successful load.'''

    def selectHint (self,p,old_p):
        '''Called at end of tree.select, just after calling c.selectPosition(p).'''

    # These are hints for optimization.
    # The proper default is c.redraw()
    def redraw_after_icons_changed(self,all=False): self.c.redraw()
    def redraw_after_clone(self):                   self.c.redraw()
    def redraw_after_contract(self):                self.c.redraw()
    def redraw_after_delete(self):                  self.c.redraw()
    def redraw_after_expand(self):                  self.c.redraw()
    def redraw_after_insert(self):                  self.c.redraw()
    def redraw_after_move_down(self):               self.c.redraw()
    def redraw_after_move_left(self):               self.c.redraw()
    def redraw_after_move_right(self):              self.c.redraw()
    def redraw_after_move_up(self):                 self.c.redraw()
    def redraw_after_select(self):                  self.c.redraw()


    #@-node:ekr.20081005065934.8:May be defined in subclasses
    #@+node:ekr.20040803072955.128:leoTree.select & helper
    tree_select_lockout = False

    def select (self,p,scroll=True):

        '''Select a node.  Never redraws outline, but may change coloring of individual headlines.'''

        if g.app.killed or self.tree_select_lockout: return None

        try:
            val = 'break'
            self.tree_select_lockout = True
            val = self.treeSelectHelper(p,scroll)
        finally:
            self.tree_select_lockout = False

        return val  # Don't put a return in a finally clause.
    #@+node:ekr.20070423101911:treeSelectHelper
    #  Do **not** try to "optimize" this by returning if p==tree.currentPosition.

    def treeSelectHelper (self,p,scroll):

        c = self.c ; frame = c.frame
        body = w = frame.body.bodyCtrl
        if not w: return # Defensive.
        old_p = c.currentPosition()

        if not p:
            # Do *not* test c.positionExists(p) here.
            # We may be in the process of changing roots.
            return None # Not an error.

        # g.trace('      ===',id(w),p and p.headString())
        if self.trace_select and not g.app.unitTesting: g.trace('tree',g.callers())

        if not g.doHook("unselect1",c=c,new_p=p,old_p=old_p,new_v=p,old_v=old_p):
            if old_p:
                #@            << unselect the old node >>
                #@+node:ekr.20040803072955.129:<< unselect the old node >>
                # Remember the position of the scrollbar before making any changes.
                if body:
                    yview = body.getYScrollPosition()
                    insertSpot = c.frame.body.getInsertPoint()
                else:
                    g.trace('no body!','c.frame',c.frame,'old_p',old_p)
                    yview,insertSpot = 0,0

                if old_p != p:
                    self.endEditLabel() # sets editPosition = None
                    self.setUnselectedLabelState(old_p) # 12/17/04

                if c.edit_widget(old_p):
                    old_p.v.t.scrollBarSpot = yview
                    old_p.v.t.insertSpot = insertSpot
                #@-node:ekr.20040803072955.129:<< unselect the old node >>
                #@nl

        g.doHook("unselect2",c=c,new_p=p,old_p=old_p,new_v=p,old_v=old_p)

        c.frame.tree.selectHint(p,old_p)
            # New in Leo 4.6: warn that the position is about to change.

        if not g.doHook("select1",c=c,new_p=p,old_p=old_p,new_v=p,old_v=old_p):
            #@        << select the new node >>
            #@+node:ekr.20040803072955.130:<< select the new node >>
            # Bug fix: we must always set this, even if we never edit the node.
            self.revertHeadline = p.headString()
            frame.setWrap(p)

            # Always do this.  Otherwise there can be problems with trailing newlines.

            s = g.toUnicode(p.v.t._bodyString,"utf-8")
            old_s = w.getAllText()

            if p and p == old_p and c.frame.body.colorizer.isSameColorState() and s == old_s:
                pass
            else:
                # This destroys all color tags, so do a full recolor.
                w.setAllText(s)
                self.frame.body.recolor_now(p) # recolor now uses p.copy(), so this is safe.

            if p.v and p.v.t.scrollBarSpot != None:
                first,last = p.v.t.scrollBarSpot
                w.setYScrollPosition(first)

            if p.v and p.v.t.insertSpot != None:
                spot = p.v.t.insertSpot
                w.setInsertPoint(spot)
                w.see(spot)
            else:
                w.setInsertPoint(0)

            # g.trace("select:",p.headString())
            #@-node:ekr.20040803072955.130:<< select the new node >>
            #@nl
            if p and p != old_p: # Suppress duplicate call.
                try: # may fail during initialization.
                    # p is NOT c.currentPosition() here!
                    if 0: # Interferes with new colorizer.
                        self.canvas.update_idletasks()
                        self.scrollTo(p)
                    if scroll and g.app.gui.guiName() == 'tkinter':
                        def scrollCallback(self=self,p=p):
                            self.scrollTo(p)
                        self.canvas.after(100,scrollCallback)
                except Exception: pass
            c.nodeHistory.update(p) # Remember this position.
        c.setCurrentPosition(p)
        #@    << set the current node >>
        #@+node:ekr.20040803072955.133:<< set the current node >>
        # g.trace('selecting',p,'edit_widget',c.edit_widget(p))
        self.setSelectedLabelState(p)

        frame.scanForTabWidth(p) #GS I believe this should also get into the select1 hook

        if self.use_chapters:
            cc = c.chapterController
            theChapter = cc and cc.getSelectedChapter()
            if theChapter:
                theChapter.p = p.copy()
                # g.trace('tkTree',theChapter.name,'v',id(p.v),p.headString())

        if self.stayInTree:
            c.treeWantsFocus()
        else:
            c.bodyWantsFocus()
        #@-node:ekr.20040803072955.133:<< set the current node >>
        #@nl
        c.frame.body.assignPositionToEditor(p) # New in Leo 4.4.1.
        c.frame.updateStatusLine() # New in Leo 4.4.1.

        g.doHook("select2",c=c,new_p=p,old_p=old_p,new_v=p,old_v=old_p)
        g.doHook("select3",c=c,new_p=p,old_p=old_p,new_v=p,old_v=old_p)

        return 'break' # Supresses unwanted selection.
    #@-node:ekr.20070423101911:treeSelectHelper
    #@-node:ekr.20040803072955.128:leoTree.select & helper
    #@+node:ekr.20031218072017.3718:oops
    def oops(self):

        g.pr("leoTree oops:", g.callers(4), "should be overridden in subclass")
    #@-node:ekr.20031218072017.3718:oops
    #@-others
#@-node:ekr.20031218072017.3704:class leoTree
#@+node:ekr.20070317073627:class leoTreeTab
class leoTreeTab:

    '''A class representing a tabbed outline pane.'''

    #@    @+others
    #@+node:ekr.20070317073627.1: ctor (leoTreeTab)
    def __init__ (self,c,chapterController,parentFrame):

        self.c = c
        self.cc = chapterController
        self.nb = None # Created in createControl.
        self.parentFrame = parentFrame

        self.selectedTabBackgroundColor = c.config.getColor(
            'selected_chapter_tab_background_color') or 'LightSteelBlue2'

        self.selectedTabForegroundColor = c.config.getColor(
            'selected_chapter_tab_foreground_color') or 'black'

        self.unselectedTabBackgroundColor = c.config.getColor(
            'unselected_chapter_tab_background_color') or 'lightgrey'

        self.unselectedTabForegroundColor = c.config.getColor(
            'unselected_chapter_tab_foreground_color') or 'black'
    #@-node:ekr.20070317073627.1: ctor (leoTreeTab)
    #@+node:ekr.20070317073755:Must be defined in subclasses
    def createControl (self):
        self.oops()

    def createTab (self,tabName,select=True):
        self.oops()

    def destroyTab (self,tabName):
        self.oops()

    def selectTab (self,tabName):
        self.oops()

    def setTabLabel(self,tabName):
        self.oops()
    #@nonl
    #@-node:ekr.20070317073755:Must be defined in subclasses
    #@+node:ekr.20070317083104:oops
    def oops(self):

        g.pr("leoTreeTree oops:", g.callers(4), "should be overridden in subclass")
    #@-node:ekr.20070317083104:oops
    #@-others
#@nonl
#@-node:ekr.20070317073627:class leoTreeTab
#@+node:ekr.20031218072017.2191:class nullBody (leoBody)
class nullBody (leoBody):

    #@    @+others
    #@+node:ekr.20031218072017.2192: nullBody.__init__
    def __init__ (self,frame,parentFrame):

        # g.trace('nullBody','frame',frame,g.callers())

        leoBody.__init__ (self,frame,parentFrame) # Init the base class.

        self.insertPoint = 0
        self.selection = 0,0
        self.s = "" # The body text

        w = stringTextWidget(c=self.c,name='body')
        self.bodyCtrl = self.widget = w
        self.editorWidgets['1'] = w
        self.colorizer = leoColor.nullColorizer(self.c)
    #@-node:ekr.20031218072017.2192: nullBody.__init__
    #@+node:ekr.20031218072017.2193:Utils (internal use)
    #@+node:ekr.20031218072017.2194:findStartOfLine
    def findStartOfLine (self,lineNumber):

        lines = g.splitLines(self.s)
        i = 0 ; index = 0
        for line in lines:
            if i == lineNumber: break
            i += 1
            index += len(line)
        return index
    #@-node:ekr.20031218072017.2194:findStartOfLine
    #@+node:ekr.20031218072017.2195:scanToStartOfLine
    def scanToStartOfLine (self,i):

        if i <= 0:
            return 0

        assert(self.s[i] != '\n')

        while i >= 0:
            if self.s[i] == '\n':
                return i + 1

        return 0
    #@-node:ekr.20031218072017.2195:scanToStartOfLine
    #@+node:ekr.20031218072017.2196:scanToEndOfLine
    def scanToEndOfLine (self,i):

        if i >= len(self.s):
            return len(self.s)

        assert(self.s[i] != '\n')

        while i < len(self.s):
            if self.s[i] == '\n':
                return i - 1

        return i
    #@-node:ekr.20031218072017.2196:scanToEndOfLine
    #@-node:ekr.20031218072017.2193:Utils (internal use)
    #@+node:ekr.20031218072017.2197:nullBody: leoBody interface
    # Birth, death & config
    def bind(self,*args,**keys):                pass
    def createBindings (self,w=None):           pass
    def createControl (self,parentFrame,p):     pass
    def setColorFromConfig (self,w=None):       pass
    def setFontFromConfig (self,w=None):        pass
    # Editors...
    def addEditor (self,event=None):            pass
    def assignPositionToEditor (self,p):        pass
    def createEditorFrame (self,w):             return None
    def cycleEditorFocus (self,event=None):     pass
    def deleteEditor (self,event=None):         pass
    def selectEditor(self,w):                   pass
    def selectLabel (self,w):                   pass
    def setEditorColors (self,bg,fg):           pass
    def unselectLabel (self,w):                 pass
    def updateEditors (self):                   pass
    # Events...
    def forceFullRecolor (self,*args,**keys):   pass
    def scheduleIdleTimeRoutine (self,function,*args,**keys): pass
    # Low-level gui...
    def hasFocus (self):                        pass
    def setFocus (self):                        pass
    def tag_add (self,tagName,index1,index2):   pass
    def tag_bind (self,tagName,event,callback): pass
    def tag_configure (self,colorName,**keys):  pass
    def tag_delete(self,tagName):               pass
    def tag_remove (self,tagName,index1,index2):pass
    #@-node:ekr.20031218072017.2197:nullBody: leoBody interface
    #@-others
#@-node:ekr.20031218072017.2191:class nullBody (leoBody)
#@+node:ekr.20031218072017.2222:class nullFrame
class nullFrame (leoFrame):

    """A null frame class for tests and batch execution."""

    #@    @+others
    #@+node:ekr.20040327105706: ctor
    def __init__ (self,title,gui,useNullUndoer=False):

        # g.trace('nullFrame')

        leoFrame.__init__(self,gui) # Init the base class.
        assert(self.c is None)

        self.body = None
        self.bodyCtrl = None
        self.iconBar = nullIconBarClass(self.c,self)
        self.isNullFrame = True
        self.outerFrame = None
        self.statusLineClass = nullStatusLineClass
        self.title = title
        self.tree = nullTree(frame=self) # New in Leo 4.4.4 b3.
        self.useNullUndoer = useNullUndoer

        # Default window position.
        self.w = 600
        self.h = 500
        self.x = 40
        self.y = 40
    #@-node:ekr.20040327105706: ctor
    #@+node:ekr.20041120073824:destroySelf
    def destroySelf (self):

        pass
    #@-node:ekr.20041120073824:destroySelf
    #@+node:ekr.20040327105706.2:finishCreate  (Removed nullFrame.bodyCtrl)
    def finishCreate(self,c):

        self.c = c

        # g.pr('nullFrame')

        # Create do-nothing component objects.
        self.tree = nullTree(frame=self)
        self.body = nullBody(frame=self,parentFrame=None)
        self.log  = nullLog (frame=self,parentFrame=None)
        self.menu = leoMenu.nullMenu(frame=self)

        c.setLog()

        assert(c.undoer)
        if self.useNullUndoer:
            c.undoer = leoUndo.nullUndoer(c)


    #@-node:ekr.20040327105706.2:finishCreate  (Removed nullFrame.bodyCtrl)
    #@+node:ekr.20061109124552:Overrides
    #@+node:ekr.20061109123828:Config...
    def resizePanesToRatio (self,ratio,secondary_ratio):    pass
    def setInitialWindowGeometry (self):                    pass
    def setMinibufferBindings(self):                        pass
    #@+node:ekr.20041130065718.1:setTopGeometry
    def setTopGeometry (self,w,h,x,y,adjustSize=True):

        self.w = w
        self.h = h
        self.x = x
        self.y = y
    #@-node:ekr.20041130065718.1:setTopGeometry
    #@-node:ekr.20061109123828:Config...
    #@+node:ekr.20061109124129:Gui-dependent commands
    # Expanding and contracting panes.
    def contractPane         (self,event=None): pass
    def expandPane           (self,event=None): pass
    def contractBodyPane     (self,event=None): pass
    def contractLogPane      (self,event=None): pass
    def contractOutlinePane  (self,event=None): pass
    def expandBodyPane       (self,event=None): pass
    def expandLogPane        (self,event=None): pass
    def expandOutlinePane    (self,event=None): pass
    def fullyExpandBodyPane  (self,event=None): pass
    def fullyExpandLogPane   (self,event=None): pass
    def fullyExpandPane      (self,event=None): pass
    def fullyExpandOutlinePane (self,event=None): pass
    def hideBodyPane         (self,event=None): pass
    def hideLogPane          (self,event=None): pass
    def hidePane             (self,event=None): pass
    def hideOutlinePane      (self,event=None): pass

    # In the Window menu...
    def cascade              (self,event=None): pass
    def equalSizedPanes      (self,event=None): pass
    def hideLogWindow        (self,event=None): pass
    def minimizeAll          (self,event=None): pass
    def resizeToScreen       (self,event=None): pass
    def toggleActivePane     (self,event=None): pass
    def toggleSplitDirection (self,event=None): pass

    # In help menu...
    def leoHelp (self,event=None): pass
    #@nonl
    #@-node:ekr.20061109124129:Gui-dependent commands
    #@+node:ekr.20041130065921:Window...
    def bringToFront (self):    pass
    def deiconify (self):       pass
    def get_window_info(self):
        # Set w,h,x,y to a reasonable size and position.
        return 600,500,20,20
    def lift (self):            pass
    def setWrap (self,flag):    pass
    def update (self):          pass
    #@-node:ekr.20041130065921:Window...
    #@-node:ekr.20061109124552:Overrides
    #@-others
#@-node:ekr.20031218072017.2222:class nullFrame
#@+node:ekr.20070301164543:class nullIconBarClass
class nullIconBarClass:

    '''A class representing the singleton Icon bar'''

    #@    @+others
    #@+node:ekr.20070301164543.1: ctor
    def __init__ (self,c,parentFrame):

        self.c = c
        self.parentFrame = parentFrame
    #@nonl
    #@-node:ekr.20070301164543.1: ctor
    #@+node:ekr.20070301164543.2:add
    def add(self,*args,**keys):

        '''Add a (virtual) button to the (virtual) icon bar.'''

        command = keys.get('command')
        text = keys.get('text')
        try:    g.app.iconWidgetCount += 1
        except: g.app.iconWidgetCount = 1
        n = g.app.iconWidgetCount
        name = 'nullButtonWidget %d' % n

        if not command:
            def commandCallback(name=name):
                g.pr("command for %s" % (name))
            command = commandCallback

        class nullButtonWidget:
            def __init__ (self,c,command,name,text):
                self.c = c
                self.command = command
                self.name = name
                self.text = text
            def __repr__ (self):
                return self.name
            def cget(self,*args,**keys):
                pass
            def configure (self,*args,**keys):
                pass
            def pack (self,*args,**keys):
                pass

        b = nullButtonWidget(self.c,command,name,text)
        return b
    #@-node:ekr.20070301164543.2:add
    #@+node:ekr.20070301165343:do nothing
    def addRow(self,height=None):
        pass

    def addWidget (self,w):
        pass

    def clear(self):
        g.app.iconWidgetCount = 0
        g.app.iconImageRefs = []

    def deleteButton (self,w):
        pass

    def getFrame (self):
        return None

    def getNewFrame (self):
        return None

    def pack (self):
        pass

    def setCommandForButton(self,b,command):
        b.command = command

    def unpack (self):
        pass

    hide = unpack
    show = pack
    #@-node:ekr.20070301165343:do nothing
    #@-others
#@-node:ekr.20070301164543:class nullIconBarClass
#@+node:ekr.20031218072017.2232:class nullLog
class nullLog (leoLog):

    #@    @+others
    #@+node:ekr.20070302095500:Birth
    #@+node:ekr.20041012083237:nullLog.__init__
    def __init__ (self,frame=None,parentFrame=None):

        # Init the base class.
        leoLog.__init__(self,frame,parentFrame)

        self.isNull = True
        self.logCtrl = self.createControl(parentFrame)
    #@-node:ekr.20041012083237:nullLog.__init__
    #@+node:ekr.20041012083237.1:createControl
    def createControl (self,parentFrame):

        return self.createTextWidget(parentFrame)
    #@-node:ekr.20041012083237.1:createControl
    #@+node:ekr.20070302095121:createTextWidget
    def createTextWidget (self,parentFrame):

        self.logNumber += 1

        c = self.c

        gui = c and c.frame and c.frame.gui or g.app.gui

        log = gui.plainTextWidget(
            c = self.c,
            name="log-%d" % self.logNumber,
        )

        return log
    #@-node:ekr.20070302095121:createTextWidget
    #@-node:ekr.20070302095500:Birth
    #@+node:ekr.20041012083237.2:oops
    def oops(self):

        g.trace("nullLog:", g.callers(4))
    #@-node:ekr.20041012083237.2:oops
    #@+node:ekr.20041012083237.3:put and putnl (nullLog)
    def put (self,s,color=None,tabName='Log'):
        if self.enabled:
            # g.rawPrint(s)
            try:
                g.pr(s,newline=False)
            except UnicodeError:
                s = s.encode('ascii','replace')
                g.pr(s,newline=False)

    def putnl (self,tabName='Log'):
        if self.enabled:
            # g.rawPrint("")
            g.pr('')
    #@-node:ekr.20041012083237.3:put and putnl (nullLog)
    #@+node:ekr.20060124085830:tabs
    def clearTab        (self,tabName,wrap='none'):             pass
    def createCanvas    (self,tabName):                         pass
    def createTab (self,tabName,createText=True,wrap='none'):   pass
    def deleteTab       (self,tabName,force=False):             pass
    def getSelectedTab  (self):                                 return None
    def lowerTab        (self,tabName):                         pass
    def raiseTab        (self,tabName):                         pass
    def renameTab (self,oldName,newName):                       pass
    def selectTab (self,tabName,createText=True,wrap='none'):   pass
    def setTabBindings  (self,tabName):                         pass
    #@-node:ekr.20060124085830:tabs
    #@-others
#@-node:ekr.20031218072017.2232:class nullLog
#@+node:ekr.20070302171509:class nullStatusLineClass
class nullStatusLineClass:

    '''A do-nothing status line.'''

    #@    @+others
    #@+node:ekr.20070302171509.2: nullStatusLineClass.ctor
    def __init__ (self,c,parentFrame):

        self.c = c
        self.enabled = False
        self.parentFrame = parentFrame

        gui = c and c.frame and c.frame.gui or g.app.gui

        self.textWidget = w = gui.plainTextWidget(c,name='status-line')

        # Set the official ivars.
        c.frame.statusFrame = None
        c.frame.statusLabel = None
        c.frame.statusText  = self.textWidget
    #@-node:ekr.20070302171509.2: nullStatusLineClass.ctor
    #@+node:ekr.20070302171917:methods
    def disable (self,background=None):
        self.enabled = False
        self.c.bodyWantsFocus()

    def enable (self,background="white"):
        self.c.widgetWantsFocus(self.textWidget)
        self.enabled = True

    def clear (self):                   self.textWidget.delete(0,'end')
    def get (self):                     return self.textWidget.getAllText()
    def isEnabled(self):                return self.enabled
    def getFrame (self):                return None
    def onActivate (self,event=None):   pass 
    def pack (self):                    pass
    def put(self,s,color=None):         self.textWidget.insert('end',s)
    def setFocus (self):                pass
    def unpack (self):                  pass
    def update (self):                  pass

    hide = unpack
    show = pack
    #@-node:ekr.20070302171917:methods
    #@-others
#@nonl
#@-node:ekr.20070302171509:class nullStatusLineClass
#@+node:ekr.20031218072017.2233:class nullTree
class nullTree (leoTree):

    #@    @+others
    #@+node:ekr.20031218072017.2234: nullTree.__init__
    def __init__ (self,frame):

        leoTree.__init__(self,frame) # Init the base class.

        assert(self.frame)

        self.editWidgetsDict = {} # Keys are tnodes, values are stringTextWidgets.
        self.font = None
        self.fontName = None
        self.canvas = None
        self.stayInTree = True
        self.trace_edit = False
        self.trace_select = False
        self.updateCount = 0
    #@-node:ekr.20031218072017.2234: nullTree.__init__
    #@+node:ekr.20070228173611:printWidgets
    def printWidgets(self):

        d = self.editWidgetsDict

        for key in d:
            # keys are tnodes, values are stringTextWidgets.
            w = d.get(key)
            g.pr('w',w,'t._headString:',key.headString,'s:',repr(w.s))

    #@-node:ekr.20070228173611:printWidgets
    #@+node:ekr.20031218072017.2236:Overrides
    def select (self,p,scroll=True):
        pass
    #@nonl
    #@+node:ekr.20070228163350:Colors & fonts
    def getFont(self):
        return self.font

    # def setColorFromConfig (self):
        # pass

    def setBindings (self):
        pass

    def setFont(self,font=None,fontName=None):
        self.font,self.fontName = font,fontName

    def setFontFromConfig (self):
        pass
    #@-node:ekr.20070228163350:Colors & fonts
    #@+node:ekr.20070228163350.1:Drawing & scrolling
    def beginUpdate (self):
        self.updateCount += 1

    def endUpdate (self,flag,scroll=False):
        self.updateCount -= 1
        if flag and self.updateCount <= 0:
            self.redraw_now()

    def drawIcon(self,v,x=None,y=None):
        pass

    def redraw_now(self,scroll=True,forceDraw=False):
        self.redrawCount += 1
        # g.trace('nullTree')

    def scrollTo(self,p):
        pass
    #@-node:ekr.20070228163350.1:Drawing & scrolling
    #@+node:ekr.20070228163350.2:Headlines
    def edit_widget (self,p):
        d = self.editWidgetsDict ; w = d.get(p.v.t)
        if not w:
            d[p.v.t] = w = stringTextWidget(
                c=self.c,
                name='head-%d' % (1 + len(d.keys())))
            w.setAllText(p.headString())
        # g.trace('w',w,'p',p.headString())
        return w

    def headWidth(self,p=None,s=''):
        return len(s)

    def setEditLabelState(self,v,selectAll=False):
        pass

    def setSelectedLabelState(self,p):
        pass

    def setUnselectedLabelState(self,p):
        pass
    #@+node:ekr.20070228164730:editLabel (nullTree) same as tkTree)
    def editLabel (self,p,selectAll=False):

        """Start editing p's headline."""

        c = self.c

        if self.editPosition() and p != self.editPosition():
            self.endEditLabel()

        self.setEditPosition(p) # That is, self._editPosition = p

        if self.trace_edit and not g.app.unitTesting:
            g.trace(p.headString(),g.choose(c.edit_widget(p),'','no edit widget'))

        if p and c.edit_widget(p):
            # g.trace('selectAll',selectAll,g.callers())
            self.revertHeadline = p.headString() # New in 4.4b2: helps undo.
            self.setEditLabelState(p,selectAll=selectAll) # Sets the focus immediately.
            c.headlineWantsFocus(p) # Make sure the focus sticks.
    #@-node:ekr.20070228164730:editLabel (nullTree) same as tkTree)
    #@+node:ekr.20070228160345:setHeadline (nullTree)
    def setHeadline (self,p,s):

        '''Set the actual text of the headline widget.

        This is called from the undo/redo logic to change the text before redrawing.'''

        # g.trace('p',p.headString(),'s',repr(s),g.callers())

        w = self.edit_widget(p)
        if w:
            w.delete(0,'end')
            if s.endswith('\n') or s.endswith('\r'):
                s = s[:-1]
            w.insert(0,s)
            self.revertHeadline = s
            # g.trace(repr(s),w.getAllText())
        else:
            g.trace('-'*20,'oops')
    #@-node:ekr.20070228160345:setHeadline (nullTree)
    #@-node:ekr.20070228163350.2:Headlines
    #@-node:ekr.20031218072017.2236:Overrides
    #@-others
#@-node:ekr.20031218072017.2233:class nullTree
#@-others
#@-node:ekr.20031218072017.3655:@thin leoFrame.py
#@-leo
