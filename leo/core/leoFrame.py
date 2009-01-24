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
    def __init__ (self,c,baseClassName,name,widget,highLevelInterface=False):

        self.baseClassName = baseClassName
        self.c = c
        self.highLevelInterface = highLevelInterface
        self.name = name
        self.virtualInsertPoint = None
        self.widget = widget # Not used at present.

        # For unit testing.
        aList = g.choose(highLevelInterface,
            self.mustBeDefinedInHighLevelSubclasses,
            self.mustBeDefinedInLowLevelSubclasses)
        self.mustBeDefinedInSubclasses.extend(aList)
        # g.trace(g.listToString(self.mustBeDefinedInSubclasses))

    def __repr__(self):
        return '%s: %s' % (self.baseClassName,id(self))
    #@+node:ekr.20081031074455.3:baseTextWidget: must be defined in base class
    mustBeDefinedOnlyInBaseClass = (
        'clipboard_append', # uses g.app.gui method.
        'clipboard_clear', # usesg.app.gui method.
        'onChar',
    )
    #@nonl
    #@-node:ekr.20081031074455.3:baseTextWidget: must be defined in base class
    #@+node:ekr.20081031074455.4:baseTextWidget: must be defined in subclasses
    #@+at
    # The subclass must implement all high-level wrappers or all low-level 
    # wrappers,
    # depending on the highLevelWrapper ivar. The ctor extends 
    # .mustBeDefinedInSubclasses
    # by one of the following lists:
    #@-at
    #@@c

    mustBeDefinedInSubclasses = [
    ]

    mustBeDefinedInHighLevelSubclasses = (
        'appendText',
        'get',
        'getAllText',
        'getFocus',
        'getInsertPoint',
        'getSelectedText',
        'getSelectionRange',
        'getYScrollPosition',
        'insert',
        'scrollLines',
        'see',
        'seeInsertPoint',
        'setAllText',
        'setBackgroundColor',
        'setForegroundColor',
        'setFocus',
        'setInsertPoint',
        'setSelectionRange',
        'setYScrollPosition',
    )

    mustBeDefinedInLowLevelSubclasses = (
        '_appendText',
        '_get',
        '_getAllText',
        '_getFocus',
        '_getInsertPoint',
        '_getLastPosition',
        '_getSelectedText',
        '_getSelectionRange',
        '_getYScrollPosition',
        '_hitTest',
        '_insertText',
        '_scrollLines',
        '_see',
        '_setAllText',
        '_setBackgroundColor',
        '_setFocus',
        '_setForegroundColor',
        '_setInsertPoint',
        '_setSelectionRange',
        '_setYScrollPosition',
    )
    #@nonl
    #@-node:ekr.20081031074455.4:baseTextWidget: must be defined in subclasses
    #@+node:ekr.20081031074455.5:baseTextWidget: mustBeDefined

    mustBeDefined = (
        'bind',
        'flashCharacter',
        'deleteTextSelection',
    )
    #@-node:ekr.20081031074455.5:baseTextWidget: mustBeDefined
    #@-node:ekr.20070228074312.1:Birth & special methods (baseText)
    #@+node:ekr.20081031074455.6:must be defined in base class
    #@+node:ekr.20070228074312.2:onChar
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
    #@-node:ekr.20070228074312.2:onChar
    #@+node:ekr.20070228074312.12:clipboard_clear & clipboard_append
    def clipboard_clear (self):

        g.app.gui.replaceClipboardWith('')

    def clipboard_append(self,s):

        s1 = g.app.gui.getTextFromClipboard()

        g.app.gui.replaceClipboardWith(s1 + s)
    #@-node:ekr.20070228074312.12:clipboard_clear & clipboard_append
    #@-node:ekr.20081031074455.6:must be defined in base class
    #@+node:ekr.20081031074455.8:May be defined in subclasses
    # These are high-level interface methods that do not call low-level methods.
    #@nonl
    #@+node:ekr.20081031074455.13: do-nothings
    def bind (self,kind,*args,**keys):          pass
    def getWidth (self):                        return 0
    def flashCharacter(self,i,bg='white',fg='red',flashes=3,delay=75):
        pass
    def indexIsVisible (self,i):                return False
        # Code will loop if this returns True forever.
    def mark_set(self,markName,i):              pass
    def setWidth (self,width):                  pass
    def tag_add(self,tagName,i,j=None,*args):   pass
    def tag_configure (self,colorName,**keys):  pass
    def tag_delete (self,tagName,*args,**keys): pass
    def tag_names (self, *args):                return []
    def tag_ranges(self,tagName):               return tuple()
    def tag_remove(self,tagName,i,j=None,*args):pass
    def update (self,*args,**keys):             pass
    def update_idletasks (self,*args,**keys):   pass
    def xyToPythonIndex (self,x,y):             return 0
    def yview (self,*args):                     return 0,0

    tag_config = tag_configure
    #@nonl
    #@-node:ekr.20081031074455.13: do-nothings
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

        i,j = self.getSelectionRange()
        self.delete(i,j)
    #@-node:ekr.20070228074312.14:deleteTextSelection
    #@+node:ekr.20070228074312.15:event_generate (baseTextWidget)
    def event_generate(self,stroke):

        trace = False
        w = self ; c = self.c ; char = stroke

        # Canonicalize the setting.
        stroke = c.k.shortcutFromSetting(stroke)

        if trace: g.trace('baseTextWidget','char',char,'stroke',stroke,'w',w)

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
    #@+node:ekr.20070228102413:getName & GetName
    def GetName(self):

        return self.name

    getName = GetName
    #@nonl
    #@-node:ekr.20070228102413:getName & GetName
    #@+node:ekr.20070228074312.25:hasSelection
    def hasSelection (self):

        w = self
        i,j = w.getSelectionRange()
        return i != j
    #@-node:ekr.20070228074312.25:hasSelection
    #@+node:ekr.20070228074312.5:oops
    def oops (self):

        g.pr('baseTextWidget oops:',self,g.callers(4),
            'must be overridden in subclass')
    #@-node:ekr.20070228074312.5:oops
    #@+node:ekr.20070228074312.28:replace
    def replace (self,i,j,s):

        w = self
        w.delete(i,j)
        w.insert(i,s)
    #@-node:ekr.20070228074312.28:replace
    #@+node:ekr.20070228074312.31:selectAllText
    def selectAllText (self,insert=None):

        '''Select all text of the widget.'''

        w = self
        w.setSelectionRange(0,'end',insert=insert)
    #@-node:ekr.20070228074312.31:selectAllText
    #@+node:ekr.20070228074312.8:w.rowColToGuiIndex
    # This method is called only from the colorizer.
    # It provides a huge speedup over naive code.

    def rowColToGuiIndex (self,s,row,col):

        return g.convertRowColToPythonIndex(s,row,col)    
    #@-node:ekr.20070228074312.8:w.rowColToGuiIndex
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
    #@-node:ekr.20081031074455.8:May be defined in subclasses
    #@+node:ekr.20081031074455.9:Must be defined in subclasses (low-level interface)
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
    #@-node:ekr.20081031074455.9:Must be defined in subclasses (low-level interface)
    #@+node:ekr.20081031074455.2:Must be defined in subclasses (high-level interface)
    # These methods are widget-independent because they call the corresponding _xxx methods.
    #@nonl
    #@+node:ekr.20070228074312.10:appendText
    def appendText (self,s):

        w = self
        w._appendText(s)
    #@-node:ekr.20070228074312.10:appendText
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
    #@+node:ekr.20070228074312.17:getFocus
    def getFocus (self):

        w = self
        w2 = w._getFocus()
        # g.trace('w',w,'focus',w2)
        return w2

    findFocus = getFocus
    #@-node:ekr.20070228074312.17:getFocus
    #@+node:ekr.20070228074312.20:getInsertPoint
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
    #@-node:ekr.20070228074312.20:getInsertPoint
    #@+node:ekr.20070228074312.21:getSelectedText
    def getSelectedText (self):

        w = self
        s = w._getSelectedText()
        return g.toUnicode(s,g.app.tkEncoding)
    #@-node:ekr.20070228074312.21:getSelectedText
    #@+node:ekr.20070228074312.22:getSelectionRange
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
    #@-node:ekr.20070228074312.22:getSelectionRange
    #@+node:ekr.20070228074312.23:getYScrollPosition
    def getYScrollPosition (self):

        w = self
        return w._getYScrollPosition()
    #@-node:ekr.20070228074312.23:getYScrollPosition
    #@+node:ekr.20070228074312.26:insert
    # The signature is more restrictive than the Tk.Text.insert method.

    def insert(self,i,s):

        w = self
        i = w.toPythonIndex(i)
        # w._setInsertPoint(i)
        w._insertText(i,s)
    #@-node:ekr.20070228074312.26:insert
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
    #@+node:ekr.20070228074312.34:setFocus
    def setFocus (self):

        w = self
        # g.trace('baseText')
        return w._setFocus()

    SetFocus = setFocus
    #@-node:ekr.20070228074312.34:setFocus
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
    #@+node:ekr.20070228074312.35:setInsertPoint
    def setInsertPoint (self,pos):

        w = self
        w.virtualInsertPoint = i = w.toPythonIndex(pos)
        # g.trace(self,i)
        w._setInsertPoint(i)
    #@-node:ekr.20070228074312.35:setInsertPoint
    #@+node:ekr.20070228074312.36:setSelectionRange
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
    #@-node:ekr.20070228074312.36:setSelectionRange
    #@+node:ekr.20070228074312.38:setYScrollPosition
    def setYScrollPosition (self,i):

        w = self
        w._setYScrollPosition(i)
    #@nonl
    #@-node:ekr.20070228074312.38:setYScrollPosition
    #@-node:ekr.20081031074455.2:Must be defined in subclasses (high-level interface)
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
        'after_idle',
        'forceFullRecolor', # The base-class method is usually good enough.
        'initAfterLoad',
        'tag_add',
        'tag_bind',
        'tag_config',
        'tag_configure',
        'tag_delete',
        'tag_names',
        'tag_remove',
    )
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
    # All of these are optional.
    def after_idle (self,idle_handler,thread_count):
        pass

    def tag_add (self,tagName,index1,index2):
        pass

    def tag_bind (self,tagName,event,callback):
        pass

    def tag_config (self,colorName,**keys):
        pass

    def tag_configure (self,colorName,**keys):
        pass

    def tag_delete(self,tagName):
        pass

    def tag_names(self,*args):
        return []

    def tag_remove (self,tagName,index1,index2):
        pass
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
        if hasattr(w,'leo_label') and w.leo_label:
            w.leo_label.configure(text=s,bg='LightSteelBlue1')

    def selectLabel (self,w):

        if self.numberOfEditors > 1:
            self.createChapterIvar(w)
            self.packEditorLabelWidget(w)
            s = self.computeLabel(w)
            # g.trace(s,g.callers())
            if hasattr(w,'leo_label') and w.leo_label:
                w.leo_label.configure(text=s,bg='white')
        elif hasattr(w,'leo_label') and w.leo_label:
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
        c.redraw(w.leo_p)
        c.recolor()
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
        newSel = w.getSelectionRange()
        if not oldText:
            oldText = p.bodyString() ; changed = True
        else:
            changed = oldText != newText
        if trace: g.trace(repr(ch),'changed:',changed,'newText:',len(newText),'w',w)
        if not changed: return
        c.undoer.setUndoTypingParams(p,undoType,
            oldText=oldText,newText=newText,oldSel=oldSel,newSel=newSel,oldYview=oldYview)
        p.v.setBodyString(newText)
        p.v.t.insertSpot = body.getInsertPoint()
        #@    << recolor the body >>
        #@+node:ekr.20051026083733.6:<< recolor the body >>
        body.colorizer.interrupt()
        c.frame.scanForTabWidth(p)
        body.recolor(p,incremental=not self.forceFullRecolorFlag)
        self.forceFullRecolorFlag = False

        if g.app.unitTesting:
            g.app.unitTestDict['colorized'] = True
        #@-node:ekr.20051026083733.6:<< recolor the body >>
        #@nl
        if not c.changed: c.setChanged(True)
        self.updateEditors()
        #@    << update icons if necessary >>
        #@+node:ekr.20051026083733.7:<< update icons if necessary >>

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

        if redraw_flag:
            c.redraw_after_icons_changed(all=False)
        #@-node:ekr.20051026083733.7:<< update icons if necessary >>
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
    def forceFullRecolor (self):
        self.forceFullRecolorFlag = True

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
    #@+node:ekr.20031218072017.3692:promptForSave (leoFrame)
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
    #@-node:ekr.20031218072017.3692:promptForSave (leoFrame)
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

        trace = False
        f = self ; c = f.c ; w = event and event.widget
        if trace: g.trace(w)
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
        p = c.currentPosition()

        if g.app.batchMode:
            c.notValidInBatchMode("Abort Edit Headline")
            return

        # Revert the headline text.
        # Calling c.setHeadString is required.
        # Otherwise c.redraw would undo the change!
        c.setHeadString(p,tree.revertHeadline)
        c.redraw(p)
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

        c.endEditing()
        time = c.getTime(body=False)
        s = p.headString().rstrip()
        c.setHeadString(p,'%s %s' % (s,time))
        c.redrawAndEdit(p,selectAll=True)
    #@nonl
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
        # 'expandAllAncestors', # Now defined in Commands class.
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
        # 'setEditLabelState',
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
    def drawIcon(self,p):                                       self.oops()
    def redraw(self,p=None,scroll=True,forceDraw=False):        self.oops()
    def redraw_now(self,p=None,scroll=True,forceDraw=False):    self.oops()
    def scrollTo(self,p):                                       self.oops()
    idle_scrollTo = scrollTo # For compatibility.

    # Headlines.
    def editLabel(self,v,selectAll=False,selection=None): self.oops()
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
    #@+node:ekr.20040803072955.91:onHeadChanged (leoTree)
    # Tricky code: do not change without careful thought and testing.

    def onHeadChanged (self,p,undoType='Typing',s=None):

        '''Officially change a headline.
        Set the old undo text to the previous revert point.'''

        trace = False and g.unitTesting
        c = self.c ; u = c.undoer
        w = self.edit_widget(p)

        if c.suppressHeadChanged: return
        if not w:
            if trace: g.trace('****** no w for p: %s',repr(p))
            return

        ch = '\n' # New in 4.4: we only report the final keystroke.
        if g.doHook("headkey1",c=c,p=p,v=p,ch=ch):
            return # The hook claims to have handled the event.

        if s is None: s = w.getAllText()
        if trace: g.trace('w',repr(w),'s',repr(s))
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
        if trace: g.trace('changed',changed,'new',repr(s))
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
            c.redraw_after_head_changed()
            if self.stayInTree:
                c.treeWantsFocus()
            else:
                c.bodyWantsFocus()
        else:
            c.frame.tree.setSelectedLabelState(p)

        g.doHook("headkey2",c=c,p=p,v=p,ch=ch)
    #@-node:ekr.20040803072955.91:onHeadChanged (leoTree)
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

        trace = False and g.unitTesting
        c = self.c ; k = c.k ; p = c.currentPosition()

        if trace: g.trace('leoTree',p and p.headString(),g.callers(4))

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

    def afterSelectHint(self,p,old_p):
        '''Called at end of tree.select.'''
        pass

    def beforeSelectHint (self,p,old_p):
        '''Called at start of tree.select.'''
        pass

    # These are hints for optimization.
    # The proper default is c.redraw()
    def redraw_after_icons_changed(self,all=False): self.c.redraw()
    def redraw_after_clone(self):                   self.c.redraw()
    def redraw_after_contract(self,p=None):         self.c.redraw()
    def redraw_after_expand(self,p=None):           self.c.redraw()
    def redraw_after_select(self,p=None):           self.c.redraw()
    #@-node:ekr.20081005065934.8:May be defined in subclasses
    #@+node:ekr.20040803072955.128:leoTree.select & helper
    tree_select_lockout = False

    def select (self,p,scroll=True):

        '''Select a node.
        Never redraws outline, but may change coloring of individual headlines.
        The scroll argument is used by tk to suppress scrolling while dragging.'''

        if g.app.killed or self.tree_select_lockout: return None

        try:
            c = self.c ; old_p = c.currentPosition()
            val = 'break'
            self.tree_select_lockout = True
            c.frame.tree.beforeSelectHint(p,old_p)
            val = self.treeSelectHelper(p,scroll=scroll)
        finally:
            self.tree_select_lockout = False
            c.frame.tree.afterSelectHint(p,old_p)

        return val  # Don't put a return in a finally clause.
    #@+node:ekr.20070423101911:treeSelectHelper
    #  Do **not** try to "optimize" this by returning if p==tree.currentPosition.

    def treeSelectHelper (self,p,scroll):

        c = self.c ; frame = c.frame ; trace = False
        body = w = frame.body.bodyCtrl
        if not w: return # Defensive.

        old_p = c.currentPosition()

        if not p:
            # Do *not* test c.positionExists(p) here.
            # We may be in the process of changing roots.
            return None # Not an error.

        if trace: g.trace(
            '\nold:',old_p and old_p.headString(),
            '\nnew:',p and p.headString())

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
                    yview,insertSpot = None,0

                if old_p != p:
                    self.endEditLabel() # sets editPosition = None
                    self.setUnselectedLabelState(old_p)

                if old_p:
                    old_p.v.t.scrollBarSpot = yview
                    old_p.v.t.insertSpot = insertSpot
                #@-node:ekr.20040803072955.129:<< unselect the old node >>
                #@nl

        g.doHook("unselect2",c=c,new_p=p,old_p=old_p,new_v=p,old_v=old_p)

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
                self.frame.body.recolor(p) # recolor now uses p.copy(), so this is safe.

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
    def forceFullRecolor (self):                pass
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
            def bind(self,*args,**keys):
                pass
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
    # def beginUpdate (self):
        # self.updateCount += 1

    # def endUpdate (self,flag):
        # self.updateCount -= 1
        # if flag and self.updateCount <= 0:
            # self.redraw_now()

    def drawIcon(self,p):
        pass

    def redraw(self,p=None,scroll=True,forceDraw=False):
        self.redrawCount += 1
        # g.trace('nullTree')

    def redraw_now(self,p=None,scroll=True,forceDraw=False):
        self.redrawCount += 1
        # g.trace('nullTree')

    def scrollTo(self,p):
        pass
    #@-node:ekr.20070228163350.1:Drawing & scrolling
    #@+node:ekr.20070228163350.2:Headlines (nullTree)
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
    #@+node:ekr.20070228164730:editLabel (nullTree)
    def editLabel (self,p,selectAll=False,selection=None):

        """Start editing p's headline."""

        c = self.c

        self.endEditLabel()
        self.setEditPosition(p)
            # That is, self._editPosition = p

        if p:
            self.revertHeadline = p.headString()
                # New in 4.4b2: helps undo.
    #@nonl
    #@-node:ekr.20070228164730:editLabel (nullTree)
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
    #@-node:ekr.20070228163350.2:Headlines (nullTree)
    #@-node:ekr.20031218072017.2236:Overrides
    #@-others
#@-node:ekr.20031218072017.2233:class nullTree
#@-others

#@<< define headlineWrapper >>
#@+node:ekr.20090124111416.18:<< define headlineWrapper >>
class headlineWrapper (baseTextWidget):

    #@    @+others
    #@-others

    pass ####
#@-node:ekr.20090124111416.18:<< define headlineWrapper >>
#@nl
#@<< define baseNativeTreeWidget >>
#@+node:ekr.20090124101342.1:<< define baseNativeTreeWidget >>
class nativeTreeWidget (leoTree):

    """The base class for native tree widgets."""

    callbacksInjected = False # A class var.

    #@    @+others
    #@+node:ekr.20090124101342.2: Birth... (nativeTree)
    #@+node:ekr.20090124101342.3:__init__ (nativeTree)
    def __init__(self,c,frame):

        # Init the base class.
        leoTree.__init__(self,frame)

        # Components.
        self.c = c
        self.canvas = self # An official ivar used by Leo's core.
        #### self.treeWidget = w = frame.top.ui.treeWidget # An internal ivar.
        self.treeWidget = None

        #### 
        # try:
            # w.headerItem().setHidden(True)
        # except Exception:
            # pass

        # w.setIconSize(QtCore.QSize(20,11))
        #### w.setIconSize(QtCore.QSize(160,16))
        # w.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        # Status ivars.
        self.dragging = False
        self.expanding = False
        self.prev_p = None
        self.redrawing = False
        self.redrawingIcons = False
        self.redrawCount = 0 # Count for debugging.
        self.revertHeadline = None # Previous headline text for abortEditLabel.
        self.selecting = False

        # Debugging.
        self.nodeDrawCount = 0

        # Associating items with vnodes...
        self.item2vnodeDict = {}
        self.tnode2itemsDict = {} # values are lists of items.
        self.vnode2itemsDict = {} # values are lists of items.

        self.setConfigIvars()
        self.setEditPosition(None) # Set positions returned by leoTree.editPosition()
    #@-node:ekr.20090124101342.3:__init__ (nativeTree)
    #@+node:ekr.20090124101342.4:qtTree.initAfterLoad
    def initAfterLoad (self):

        c = self.c
        c.setChanged(False)

        # c = self.c ; frame = c.frame
        # w = c.frame.top ; tw = self.treeWidget

        # if not leoQtTree.callbacksInjected:
            # leoQtTree.callbacksInjected = True
            # self.injectCallbacks() # A base class method.

        # w.connect(self.treeWidget,QtCore.SIGNAL(
                # "itemDoubleClicked(QTreeWidgetItem*, int)"),
            # self.onItemDoubleClicked)

        # w.connect(self.treeWidget,QtCore.SIGNAL(
                # "itemSelectionChanged()"),
            # self.onTreeSelect)

        # w.connect(self.treeWidget,QtCore.SIGNAL(
                # "itemChanged(QTreeWidgetItem*, int)"),
            # self.onItemChanged)

        # w.connect(self.treeWidget,QtCore.SIGNAL(
                # "itemCollapsed(QTreeWidgetItem*)"),
            # self.onItemCollapsed)

        # w.connect(self.treeWidget,QtCore.SIGNAL(
                # "itemExpanded(QTreeWidgetItem*)"),
            # self.onItemExpanded)

        # self.ev_filter = leoQtEventFilter(c,w=self,tag='tree')
        # tw.installEventFilter(self.ev_filter)

        # c.setChanged(False)
    #@-node:ekr.20090124101342.4:qtTree.initAfterLoad
    #@+node:ekr.20090124101342.5:qtTree.setBindings & helper
    # def setBindings (self):

        # '''Create master bindings for all headlines.'''

        # pass
    #@+node:ekr.20090124101342.6:qtTree.setBindingsHelper
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
    #@-node:ekr.20090124101342.6:qtTree.setBindingsHelper
    #@-node:ekr.20090124101342.5:qtTree.setBindings & helper
    #@+node:ekr.20090124101342.7:qtTree.setCanvasBindings
    # def setCanvasBindings (self,canvas):

        # pass
    #@nonl
    #@-node:ekr.20090124101342.7:qtTree.setCanvasBindings
    #@+node:ekr.20090124101342.8:get_name (nativeTree)
    def getName (self):

        name = 'canvas(tree)' # Must start with canvas.

        return name
    #@-node:ekr.20090124101342.8:get_name (nativeTree)
    #@-node:ekr.20090124101342.2: Birth... (nativeTree)
    #@+node:ekr.20090124101342.9:Config... (nativeTree)
    #@+node:ekr.20090124101342.10:do-nothin config methods
    # These can be over-ridden if desired,
    # but they do not have to be over-ridden.

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
    #@-node:ekr.20090124101342.10:do-nothin config methods
    #@+node:ekr.20090124101342.11:setConfigIvars
    def setConfigIvars (self):

        c = self.c

        self.allow_clone_drags    = c.config.getBool('allow_clone_drags')
        self.enable_drag_messages = c.config.getBool("enable_drag_messages")

        # self.center_selected_tree_node = c.config.getBool('center_selected_tree_node')

        # self.expanded_click_area  = c.config.getBool('expanded_click_area')
        # self.gc_before_redraw     = c.config.getBool('gc_before_redraw')

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

        # self.initialClickExpandsOrContractsNode = c.config.getBool(
            # 'initialClickExpandsOrContractsNode')
        # self.look_for_control_drag_on_mouse_down = c.config.getBool(
            # 'look_for_control_drag_on_mouse_down')

        self.select_all_text_when_editing_headlines = c.config.getBool(
            'select_all_text_when_editing_headlines')

        self.stayInTree     = c.config.getBool('stayInTreeAfterSelect')
        self.use_chapters   = c.config.getBool('use_chapters')
    #@-node:ekr.20090124101342.11:setConfigIvars
    #@-node:ekr.20090124101342.9:Config... (nativeTree)
    #@+node:ekr.20090124101342.12:Drawing... (nativeTree)

    #@+node:ekr.20090124101342.13:Entry points (nativeTree)
    #@+node:ekr.20090124101342.14:full_redraw & helpers (to do)
    # forceDraw not used. It is used in the Tk code.

    def full_redraw (self,p=None,scroll=True,forceDraw=False):

        '''Redraw all visible nodes of the tree.

        Preserve the vertical scrolling unless scroll is True.'''

        trace = False
        c = self.c ; w = self.treeWidget
        if not w: return
        if self.redrawing:
            g.trace('***** already drawing',g.callers(5))
            return

        if p is None:
            p = c.currentPosition()
        else:
            c.setCurrentPosition(p)

        self.redrawCount += 1

        ####
        # if trace:
            # # g.trace(self.redrawCount,g.callers())
            # tstart()

        # Init the data structures.
        self.initData()
        self.nodeDrawCount = 0
        self.redrawing = True
        try:
            hScroll = w.horizontalScrollBar()
            vScroll = w.verticalScrollBar()
            hPos = hScroll.sliderPosition()
            vPos = vScroll.sliderPosition()
            # g.trace(hPos,vPos)
            w.clear()
            # Draw all top-level nodes and their visible descendants.
            if c.hoistStack:
                bunch = c.hoistStack[-1]
                p = bunch.p ; h = p.headString()
                if len(c.hoistStack) == 1 and h.startswith('@chapter') and p.hasChildren():
                    p = p.firstChild()
                    while p:
                        self.drawTree(p)
                        p.moveToNext()
                else:
                    self.drawTree(p)
            else:
                p = c.rootPosition()
                while p:
                    self.drawTree(p)
                    p.moveToNext()
        finally:
            if not self.selecting:
                self.setCurrentItem()
            hScroll.setSliderPosition(hPos)
            if not scroll:
                vScroll.setSliderPosition(vPos)

            # Necessary to get the tree drawn initially.
            w.repaint()

            c.requestRedrawFlag= False
            self.redrawing = False
            if trace:
                #### theTime = tstop()
                theTime = '?? sec'
                if True and not g.app.unitTesting:
                    g.trace('%s: scroll: %s, drew %3s nodes in %s' % (
                        self.redrawCount,scroll,self.nodeDrawCount,theTime),
                        g.callers(4))

    # Compatibility
    redraw = full_redraw 
    redraw_now = full_redraw
    #@+node:ekr.20090124101342.15:contractItem & expandItem
    def contractItem (self,item):

        self.treeWidget.collapseItem(item)

    def expandItem (self,item):

        self.treeWidget.expandItem(item)
    #@-node:ekr.20090124101342.15:contractItem & expandItem
    #@+node:ekr.20090124101342.16:drawChildren
    def drawChildren (self,p,parent_item):

        if not p:
            return g.trace('can not happen: no p')

        if p.hasChildren():
            if p.isExpanded():
                self.expandItem(parent_item)
                child = p.firstChild()
                while child:
                    self.drawTree(child,parent_item)
                    child.moveToNext()
            else:
                # Draw the hidden children.
                child = p.firstChild()
                while child:
                    self.drawNode(child,parent_item)
                    child.moveToNext()
                self.contractItem(parent_item)
        else:
            self.contractItem(parent_item)
    #@-node:ekr.20090124101342.16:drawChildren
    #@+node:ekr.20090124101342.17:drawNode (changed)
    def drawNode (self,p,parent_item):

        c = self.c 
        self.nodeDrawCount += 1

        # Allocate the item.
        item = self.createTreeItem(p,parent_item) #### 

        # Do this now, so self.isValidItem will be true in setItemIcon.
        self.rememberItem(p,item)

        # Set the headline and maybe the icon.
        self.setItemText(p.headString()) ####
        if p:
            self.drawItemIcon(p,item) ####

        return item
    #@-node:ekr.20090124101342.17:drawNode (changed)
    #@+node:ekr.20090124101342.18:drawTree
    def drawTree (self,p,parent_item=None):

        # Draw the (visible) parent node.
        item = self.drawNode(p,parent_item)

        # Draw all the visible children.
        self.drawChildren(p,parent_item=item)


    #@-node:ekr.20090124101342.18:drawTree
    #@+node:ekr.20090124101342.19:initData
    def initData (self):

        self.item2vnodeDict = {}
        self.tnode2itemsDict = {}
        self.vnode2itemsDict = {}
    #@-node:ekr.20090124101342.19:initData
    #@+node:ekr.20090124101342.20:rememberItem & rememberVnodeItem
    def rememberItem (self,p,item):

        self.rememberVnodeItem(p.v,item)

    def rememberVnodeItem (self,v,item):

        # Update item2vnodeDict.
        self.item2vnodeDict[item] = v

        # Update tnode2itemsDict & vnode2itemsDict.
        table = (
            (self.tnode2itemsDict,v.t),
            (self.vnode2itemsDict,v))

        for d,key in table:
            aList = d.get(key,[])
            if item in aList:
                g.trace('*** ERROR *** item already in list: %s, %s' % (item,aList))
            else:
                aList.append(item)
            d[key] = aList
    #@-node:ekr.20090124101342.20:rememberItem & rememberVnodeItem
    #@-node:ekr.20090124101342.14:full_redraw & helpers (to do)
    #@+node:ekr.20090124101342.21:redraw_after_contract
    def redraw_after_contract (self,p=None):

        if self.redrawing:
            return

        item = self.position2item(p)

        if item:
            self.contractItem(item)
        else:
            # This is not an error.
            # We may have contracted a node that was not, in fact, visible.
            self.full_redraw()
    #@-node:ekr.20090124101342.21:redraw_after_contract
    #@+node:ekr.20090124101342.22:redraw_after_expand
    def redraw_after_expand (self,p=None):

        self.full_redraw (p,scroll=False)
    #@-node:ekr.20090124101342.22:redraw_after_expand
    #@+node:ekr.20090124101342.23:redraw_after_head_changed
    def redraw_after_head_changed (self):

        # g.trace(g.callers(4))

        c = self.c ; p = c.currentPosition()

        if p:
            h = p.headString()
            for item in self.tnode2items(p.v.t):
                if self.isValidItem(item):
                    self.setItemText(h)
    #@nonl
    #@-node:ekr.20090124101342.23:redraw_after_head_changed
    #@+node:ekr.20090124101342.24:redraw_after_icons_changed
    def redraw_after_icons_changed (self,all=False):

        if self.redrawing: return

        self.redrawCount += 1 # To keep a unit test happy.

        c = self.c

        # Suppress call to setHeadString in onItemChanged!
        self.redrawing = True
        try:
            if all:
                for p in c.rootPosition().self_and_siblings_iter():
                    self.updateVisibleIcons(p)
            else:
                p = c.currentPosition()
                self.updateIcon(p,force=True)
        finally:
            self.redrawing = False

    #@-node:ekr.20090124101342.24:redraw_after_icons_changed
    #@+node:ekr.20090124101342.25:redraw_after_select
    # Important: this can not replace before/afterSelectHint.

    def redraw_after_select (self,p=None):

        if self.redrawing: return

        # g.trace(p.headString())

        # Don't set self.redrawing here.
        # It will be set by self.afterSelectHint.

        item = self.position2item(p)

        # It is not an error for position2item to fail.
        if not item:
            self.full_redraw(p)

        # c.redraw_after_select calls tree.select indirectly.
        # Do not call it again here.
    #@nonl
    #@-node:ekr.20090124101342.25:redraw_after_select
    #@-node:ekr.20090124101342.13:Entry points (nativeTree)
    #@-node:ekr.20090124101342.12:Drawing... (nativeTree)
    #@+node:ekr.20090124101342.42:Event handlers... (nativeTree)
    #@+node:ekr.20090124101342.43:Click Box...
    #@+node:ekr.20090124101342.44:onClickBoxClick
    def onClickBoxClick (self,event,p=None):

        c = self.c
        if self.redrawing or self.selecting: return

        g.doHook("boxclick1",c=c,p=p,v=p,event=event)
        g.doHook("boxclick2",c=c,p=p,v=p,event=event)

        c.outerUpdate()
    #@-node:ekr.20090124101342.44:onClickBoxClick
    #@+node:ekr.20090124101342.45:onClickBoxRightClick
    def onClickBoxRightClick(self, event, p=None):

        c = self.c
        if self.redrawing or self.selecting: return

        g.doHook("boxrclick1",c=c,p=p,v=p,event=event)
        g.doHook("boxrclick2",c=c,p=p,v=p,event=event)

        c.outerUpdate()
    #@-node:ekr.20090124101342.45:onClickBoxRightClick
    #@+node:ekr.20090124101342.46:onPlusBoxRightClick
    def onPlusBoxRightClick (self,event,p=None):

        c = self.c
        if self.redrawing or self.selecting: return

        g.doHook('rclick-popup',c=c,p=p,event=event,context_menu='plusbox')

        c.outerUpdate()
    #@-node:ekr.20090124101342.46:onPlusBoxRightClick
    #@-node:ekr.20090124101342.43:Click Box...
    #@+node:ekr.20090124101342.47:findEditWidget
    def findEditWidget (self,p):

        """Return the tree text item corresponding to p."""

        # g.trace(p,g.callers(4))

        return None

    #@-node:ekr.20090124101342.47:findEditWidget
    #@+node:ekr.20090124101342.48:Icon Box...
    #@+node:ekr.20090124101342.49:onIconBoxClick
    def onIconBoxClick (self,event,p=None):

        c = self.c
        if self.redrawing or self.selecting: return

        g.doHook("iconclick1",c=c,p=p,v=p,event=event)
        g.doHook("iconclick2",c=c,p=p,v=p,event=event)

        c.outerUpdate()
    #@-node:ekr.20090124101342.49:onIconBoxClick
    #@+node:ekr.20090124101342.50:onIconBoxRightClick
    def onIconBoxRightClick (self,event,p=None):

        """Handle a right click in any outline widget."""

        c = self.c
        if self.redrawing or self.selecting: return

        g.doHook("iconrclick1",c=c,p=p,v=p,event=event)
        g.doHook("iconrclick2",c=c,p=p,v=p,event=event)

        c.outerUpdate()
    #@-node:ekr.20090124101342.50:onIconBoxRightClick
    #@+node:ekr.20090124101342.51:onIconBoxDoubleClick
    def onIconBoxDoubleClick (self,event,p=None):

        c = self.c
        if self.redrawing or self.selecting: return

        g.doHook("icondclick1",c=c,p=p,v=p,event=event)
        g.doHook("icondclick2",c=c,p=p,v=p,event=event)

        c.outerUpdate()
    #@-node:ekr.20090124101342.51:onIconBoxDoubleClick
    #@-node:ekr.20090124101342.48:Icon Box...
    #@+node:ekr.20090124101342.52:onItemChanged
    def onItemChanged(self, item, col):

        '''Handle a change event in a headline.
        This only gets called when the user hits return.'''

        c = self.c

        # Ignore changes when redrawing.
        if self.redrawing:
            return
        if self.redrawingIcons:
            return

        p = self.item2position(item)
        if p:
            # so far, col is always 0
            s = g.app.gui.toUnicode(item.text(col))
            p.setHeadString(s)
            p.setDirty()
            self.redraw_after_icons_changed(all=False)

        c.outerUpdate()
    #@-node:ekr.20090124101342.52:onItemChanged
    #@+node:ekr.20090124101342.53:onItemCollapsed
    def onItemCollapsed (self,item):

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

        p2 = self.item2position(item)
        if p2:
            p2.contract()
            c.frame.tree.select(p2)
            item = self.setCurrentItem()
        else:
            g.trace('Error: no p2')

        c.outerUpdate()
    #@-node:ekr.20090124101342.53:onItemCollapsed
    #@+node:ekr.20090124101342.54:onItemDoubleClicked
    def onItemDoubleClicked (self,item,col):

        c = self.c ; w = self.treeWidget
        if self.redrawing or self.selecting: return

        e = self.createTreeEditorForItem(item) ####
        if not e: g.trace('*** no e')

        p = self.item2position(item)
        if not p: g.trace('*** no p')

        c.outerUpdate()
    #@-node:ekr.20090124101342.54:onItemDoubleClicked
    #@+node:ekr.20090124101342.55:onItemExpanded
    def onItemExpanded (self,item):

        '''Handle and tree-expansion event.'''

        # The difficult case is when the user clicks the expansion box.

        trace = False ; verbose = False
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

        try:
            self.expanding = True
            p2 = self.item2position(item)
            if p2:
                if not p2.isExpanded():
                    p2.expand()
                c.frame.tree.select(p2) # same as self.select.
                self.full_redraw()
            else:
                g.trace('Error no p2')
        finally:
            self.expanding = False
            self.setCurrentItem()
            c.outerUpdate()
    #@nonl
    #@-node:ekr.20090124101342.55:onItemExpanded
    #@+node:ekr.20090124101342.56:onTreeSelect
    def onTreeSelect(self):

        '''Select the proper position when a tree node is selected.'''

        trace = False ; verbose = False
        c = self.c ; p = c.currentPosition()
        w = self.treeWidget 

        if self.selecting:
            if trace: g.trace('already selecting',p and p.headString())
            return
        if self.redrawing:
            if trace: g.trace('already drawing',p and p.headString())
            return

        item = w.currentItem()
        p = self.item2position(item)

        if p:
            if trace: g.trace(p and p.headString())
            c.frame.tree.select(p)
                # The crucial hook. Calls before/AfterSelectHint.
        else: # An error.
            g.trace('no p for item: %s' % item,g.callers(4))

        c.outerUpdate()
    #@nonl
    #@-node:ekr.20090124101342.56:onTreeSelect
    #@+node:ekr.20090124101342.57:setCurrentItem
    def setCurrentItem (self):

        trace = False ; verbose = False
        c = self.c ; p = c.currentPosition()

        if self.expanding:
            if trace: g.trace('already expanding')
            return None
        if self.selecting:
            if trace: g.trace('already selecting')
            return None
        if not p:
            if trace: g.trace('** no p')
            return None

        item = self.position2item(p)

        if item:
            if trace: g.trace(p and p.headString())
        else:
            # This is not necessarily an error.
            # We often attempt to select an item before redrawing it.
            if trace: g.trace('** no item for',p)
            return None

        item2 = self.getCurrentItem() ####
        if item != item2:
            if trace and verbose: g.trace('item',item,'old item',item2)
            self.selecting = True
            try:
                self.setCurrentItemHelper(item) ####
            finally:
                self.selecting = False
        return item
    #@-node:ekr.20090124101342.57:setCurrentItem
    #@+node:ekr.20090124101342.58:tree.OnPopup & allies
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
    #@+node:ekr.20090124101342.59:OnPopupFocusLost
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
    #@-node:ekr.20090124101342.59:OnPopupFocusLost
    #@+node:ekr.20090124101342.60:createPopupMenu
    def createPopupMenu (self,event):

        c = self.c ; frame = c.frame

        # self.popupMenu = menu = Qt.Menu(g.app.root, tearoff=0)

        # # Add the Open With entries if they exist.
        # if g.app.openWithTable:
            # frame.menu.createOpenWithMenuItemsFromTable(menu,g.app.openWithTable)
            # table = (("-",None,None),)
            # frame.menu.createMenuEntries(menu,table)

        #@    << Create the menu table >>
        #@+node:ekr.20090124101342.61:<< Create the menu table >>
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
        #@-node:ekr.20090124101342.61:<< Create the menu table >>
        #@nl

        # # New in 4.4.  There is no need for a dontBind argument because
        # # Bindings from tables are ignored.
        # frame.menu.createMenuEntries(menu,table)
    #@-node:ekr.20090124101342.60:createPopupMenu
    #@+node:ekr.20090124101342.62:enablePopupMenuItems
    def enablePopupMenuItems (self,v,event):

        """Enable and disable items in the popup menu."""

        c = self.c 

        # menu = self.popupMenu

        #@    << set isAtRoot and isAtFile if v's tree contains @root or @file nodes >>
        #@+node:ekr.20090124101342.63:<< set isAtRoot and isAtFile if v's tree contains @root or @file nodes >>
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
        #@-node:ekr.20090124101342.63:<< set isAtRoot and isAtFile if v's tree contains @root or @file nodes >>
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
    #@-node:ekr.20090124101342.62:enablePopupMenuItems
    #@+node:ekr.20090124101342.64:showPopupMenu
    def showPopupMenu (self,event):

        """Show a popup menu."""

        # c = self.c ; menu = self.popupMenu

        # g.app.gui.postPopupMenu(c, menu, event.x_root, event.y_root)

        # self.popupMenu = None

        # # Set the focus immediately so we know when we lose it.
        # #c.widgetWantsFocus(menu)
    #@-node:ekr.20090124101342.64:showPopupMenu
    #@-node:ekr.20090124101342.58:tree.OnPopup & allies
    #@-node:ekr.20090124101342.42:Event handlers... (nativeTree)
    #@+node:ekr.20090124101342.67:Selecting & editing... (nativeTree)
    #@+node:ekr.20090124101342.68:afterSelectHint
    def afterSelectHint (self,p,old_p):

        trace = False
        c = self.c

        self.selecting = False

        if not p:
            return g.trace('Error: no p')
        if p != c.currentPosition():
            return g.trace('Error: p is not c.currentPosition()')
        if self.redrawing:
            return g.trace('Error: already redrawing')

        if trace: g.trace(p and p.headString(),g.callers(4))

        c.outerUpdate() # Bring the tree up to date.

        # setCurrentItem sets & clears .selecting ivar
        self.setCurrentItem()
    #@-node:ekr.20090124101342.68:afterSelectHint
    #@+node:ekr.20090124101342.69:beforeSelectHint
    def beforeSelectHint (self,p,old_p):

        trace = False

        if self.selecting:
            return g.trace('*** Error: already selecting',g.callers(4))
        if self.redrawing:
            if trace: g.trace('already redrawing')
            return

        if trace: g.trace(p and p.headString())

        # Disable onTextChanged.
        self.selecting = True
    #@nonl
    #@-node:ekr.20090124101342.69:beforeSelectHint
    #@+node:ekr.20090124101342.70:edit_widget
    def edit_widget (self,p):

        """Returns the edit widget for position p."""

        trace = False
        c = self.c
        item = self.position2item(p)
        if item:
            e = self.getTreeEditorForItem(item) ####
            if e:
                # Create a wrapper widget for Leo's core.
                #### w = leoQtHeadlineWidget(widget=e,name='head',c=c)
                w = headlineWrapper(widget=e,name='head',c=c)
                if trace: g.trace(w,p and p.headString())
                return w
            else:
                # This is not an error
                if trace: g.trace('no e for %s' % (p),g.callers(4))
                return None
        else:
            if trace: g.trace('no item for %s' % (p),g.callers(4))
            return None
    #@nonl
    #@-node:ekr.20090124101342.70:edit_widget
    #@+node:ekr.20090124101342.71:editLabel (override)
    def editLabel (self,p,selectAll=False,selection=None):

        """Start editing p's headline."""

        trace = False ; verbose = False
        c = self.c ; w = self.treeWidget

        if self.redrawing:
            if trace and verbose: g.trace('redrawing')
            return
        if trace: g.trace('***',p and p.headString(),g.callers(4))

        c.outerUpdate()
            # Do any scheduled redraw.
            # This won't do anything in the new redraw scheme.

        item = self.position2item(p)

        if item:
            w.setCurrentItem(item) # Must do this first.
            w.editItem(item)
                # Generates focus-in event that tree doesn't report.
            e = w.itemWidget(item,0) # A QLineEdit
            if e:
                s = e.text() ; len_s = len(s)
                if selection:
                    i,j,ins = selection
                    start,n = i,abs(i-j)
                        # Not right for backward searches.
                elif selectAll: start,n,ins = 0,len_s,len_s
                else:           start,n,ins = len_s,0,len_s
                e.setObjectName('headline')
                e.setSelection(start,n)
                # e.setCursorPosition(ins) # Does not work.
                e.setFocus()
            else: self.oops('no edit widget')
        else:
            e = None
            self.oops('no item: %s' % p)

        # A nice hack: just set the focus request.
        if e: c.requestedFocusWidget = e
    #@-node:ekr.20090124101342.71:editLabel (override)
    #@+node:ekr.20090124101342.72:editPosition
    def editPosition(self):

        c = self.c ; p = c.currentPosition()
        ew = self.edit_widget(p)
        return ew and p or None
    #@-node:ekr.20090124101342.72:editPosition
    #@+node:ekr.20090124101342.73:endEditLabel
    def endEditLabel (self):

        '''Override leoTree.endEditLabel.

        End editing of the presently-selected headline.'''

        c = self.c ; p = c.currentPosition()

        ew = self.edit_widget(p)
        e = ew and ew.widget

        if e:
            s = e.text()
            if s != p.headString():
                self.onHeadChanged(p)
    #@-node:ekr.20090124101342.73:endEditLabel
    #@+node:ekr.20090124101342.74:onHeadChanged (nativeTree)
    # Tricky code: do not change without careful thought and testing.

    def onHeadChanged (self,p,undoType='Typing',s=None):

        '''Officially change a headline.'''

        trace = False ; verbose = True
        c = self.c ; u = c.undoer
        ew = self.edit_widget(p)
        if ew: e = ew.widget
        item = self.position2item(p)

        w = g.app.gui.get_focus()

        # These are not errors: onItemChanged may
        # have been called first.
        if trace and verbose:
            if not e:  g.trace('No e',g.callers(4))
            if e != w: g.trace('e != w',e,w,g.callers(4))
            if not p:  g.trace('No p')

        if e and e == w and item and p:
            s = e.text() ; len_s = len(s)
            s = g.app.gui.toUnicode(s)
            oldHead = p.headString()
            changed = s != oldHead
            if trace: g.trace('changed',changed,repr(s),g.callers(4))
            if changed:
                p.initHeadString(s)
                item.setText(0,s) # Required to avoid full redraw.
                undoData = u.beforeChangeNodeContents(p,oldHead=oldHead)
                if not c.changed: c.setChanged(True)
                # New in Leo 4.4.5: we must recolor the body because
                # the headline may contain directives.
                c.frame.body.recolor(p,incremental=True)
                dirtyVnodeList = p.setDirty()
                u.afterChangeNodeContents(p,undoType,undoData,
                    dirtyVnodeList=dirtyVnodeList)

        # This is a crucial shortcut.
        if g.unitTesting: return

        self.redraw_after_head_changed()

        if self.stayInTree:
            c.treeWantsFocus()
        else:
            c.bodyWantsFocus()
        c.outerUpdate()
    #@-node:ekr.20090124101342.74:onHeadChanged (nativeTree)
    #@+node:ekr.20090124101342.75:setHeadline (nativeTree)
    def setHeadline (self,p,s):

        '''Set the actual text of the headline widget.

        This is called from unit tests to change the text before redrawing.'''

        p.setHeadString(s)
        w = self.edit_widget(p)
        if w:
            w.setAllText(s)
    #@-node:ekr.20090124101342.75:setHeadline (nativeTree)
    #@+node:ekr.20090124101342.76:traceSelect
    def traceSelect (self):

        if 0:
            g.trace(self.selecting,g.callers(5))
    #@-node:ekr.20090124101342.76:traceSelect
    #@-node:ekr.20090124101342.67:Selecting & editing... (nativeTree)
    #@+node:ekr.20090124111416.1:Widget-independent helpers
    #@+node:ekr.20090124111416.9:Associating items and positions
    #@+node:ekr.20090124101342.28:item dict getters
    def item2tnode (self,item):
        v = self.item2vnodeDict.get(item)
        return v and v.t

    def item2vnode (self,item):
        return self.item2vnodeDict.get(item)

    def tnode2items(self,t):
        return self.tnode2itemsDict.get(t,[])

    def vnode2items(self,v):
        return self.vnode2itemsDict.get(v,[])

    def isValidItem (self,item):
        return item in self.item2vnodeDict
    #@-node:ekr.20090124101342.28:item dict getters
    #@+node:ekr.20090124101342.29:item2position & position2item & helpers
    #@@nocolor-node
    #@+at
    # 
    # These two methods allow the drawing code to avoid storing any positions,
    # a crucial simplification. Indeed, without the burden of keeping position
    # up-to-date, or worse, recalculating them all whenever the outline 
    # changes,
    # the tree code becomes straightforward.
    #@-at
    #@nonl
    #@+node:ekr.20090124101342.30:childItems
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
    #@-node:ekr.20090124101342.30:childItems
    #@+node:ekr.20090124101342.31:childIndexOfItem
    def childIndexOfItem (self,item):

        parent = item.parent()

        if parent:
            n = parent.indexOfChild(item)
        else:
            w = self.treeWidget
            n = w.indexOfTopLevelItem(item)

        return n

    #@-node:ekr.20090124101342.31:childIndexOfItem
    #@+node:ekr.20090124101342.32:item2position
    def item2position (self,item):

        '''Reconstitute a position given an item.'''

        stack = []
        childIndex = self.childIndexOfItem(item)
        v = self.item2vnode(item)

        item = item.parent()
        while item:
            n2 = self.childIndexOfItem(item)
            v2 = self.item2vnode(item)
            data = v2,n2
            stack.insert(0,data)
            item = item.parent()

        p = leoNodes.position(v,childIndex,stack)

        if not p:
            self.oops('item2position failed. p: %s, v: %s, childIndex: %s stack: %s' % (
                p,v,childIndex,stack))

        return p
    #@-node:ekr.20090124101342.32:item2position
    #@+node:ekr.20090124101342.33:nthChildItem
    def nthChildItem (self,n,parent_item):

        children = self.childItems(parent_item)

        if n < len(children):
            item = children[n]
        else:
            # self.oops('itemCount: %s, n: %s' % (len(children),n))

            # This is **not* an error.
            # It simply means that we need to redraw the tree.
            item = None

        return item
    #@-node:ekr.20090124101342.33:nthChildItem
    #@+node:ekr.20090124101342.34:position2item
    def position2item (self,p):

        '''Return the unique tree item associated with position p.

        Return None if there no such tree item.  This is *not* an error.'''

        parent_item = None

        for v,n in p.stack:
            parent_item = self.nthChildItem(n,parent_item)

        item = self.nthChildItem(p.childIndex(),parent_item)

        return item
    #@-node:ekr.20090124101342.34:position2item
    #@-node:ekr.20090124101342.29:item2position & position2item & helpers
    #@-node:ekr.20090124111416.9:Associating items and positions
    #@+node:ekr.20090124101342.65:Focus
    def getFocus(self):

        return g.app.gui.get_focus()

    findFocus = getFocus

    def hasFocus (self):

        val = self.treeWidget == g.app.gui.get_focus(self.c)
        return val

    def setFocus (self):

        g.app.gui.set_focus(self.c,self.treeWidget)
    #@-node:ekr.20090124101342.65:Focus
    #@+node:ekr.20090124111416.10:Icons
    #@+node:ekr.20090124101342.37:drawItemIcon
    def drawItemIcon (self,p,item):

        '''Set the item's icon to p's icon.'''

        icon = self.getIcon(p)
        if icon:
            self.setItemIcon(item,icon)
    #@nonl
    #@-node:ekr.20090124101342.37:drawItemIcon
    #@+node:ekr.20090124111416.3:getIconImage
    def getIconImage(self,val):

        return g.app.gui.getIconImage(
            "box%02d.GIF" % val)
    #@nonl
    #@-node:ekr.20090124111416.3:getIconImage
    #@+node:ekr.20090124111416.4:getVnodeIcon
    def getVnodeIcon(self,p):

        '''Return the proper icon for position p.'''

        p.v.iconVal = val = p.v.computeIcon()
        return self.getIconImage(val)
    #@-node:ekr.20090124111416.4:getVnodeIcon
    #@+node:ekr.20090124101342.39:setItemIcon
    def setItemIcon (self,item,icon):

        trace = True

        valid = item and self.isValidItem(item)

        if icon and valid:
            try:
                # Suppress onItemChanged.
                self.redrawingIcons = True
                self.setItemIconHelper(item,icon)
            except Exception:
                self.redrawingIcons = False
        elif trace:
            # Apparently, icon can be None due to recent icon changes.
            if icon:
                g.trace('** item %s, valid: %s, icon: %s' % (
                    item and id(item) or '<no item>',valid,icon),
                    g.callers(4))
    #@-node:ekr.20090124101342.39:setItemIcon
    #@-node:ekr.20090124111416.10:Icons
    #@+node:ekr.20090124101342.66:oops
    def oops(self):

        g.pr("leoTree oops: should be overridden in subclass",
            g.callers(4))
    #@-node:ekr.20090124101342.66:oops
    #@-node:ekr.20090124111416.1:Widget-independent helpers
    #@+node:ekr.20090124111416.2:Widget-dependent helpers
    # These must be overridden in subclasses.
    #@nonl
    #@+node:ekr.20090124111416.6:createTreeItem
    def createTreeItem(self,p,parentItem):

        self.oops()

        # w = self.treeWidget
        # itemOrTree = parent_item or w
        # item = QtGui.QTreeWidgetItem(itemOrTree)
        # item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
    #@-node:ekr.20090124111416.6:createTreeItem
    #@+node:ekr.20090124111416.12:createTreeEditorForItem
    def createTreeEditorForItem(self,item):

        self.oops()

        # w.setCurrentItem(item) # Must do this first.
        # w.editItem(item)
        # e = w.itemWidget(item,0)


        # Hook up the widget.
        # e.connect(e,QtCore.SIGNAL(
            # "textEdited(QTreeWidgetItem*,int)"),
            # self.onHeadChanged)
        # e.setObjectName('headline')

        # return e
    #@-node:ekr.20090124111416.12:createTreeEditorForItem
    #@+node:ekr.20090124111416.20:getCurrentItem
    def getCurrentItem (self):

        self.oops()

        # w = self.treeWidget
        # return w.currentItem()
    #@-node:ekr.20090124111416.20:getCurrentItem
    #@+node:ekr.20090124111416.13:getTreeEditorForItem
    def getTreeEditorForItem(self,item):

        '''Return the edit widget if it exists.
        Do *not* create one if it does not exist.'''

        self.oops()

        # w = self.treeWidget
        # e = w.itemWidget(item,0)
        # return e
    #@-node:ekr.20090124111416.13:getTreeEditorForItem
    #@+node:ekr.20090124111416.14:setCurrentItemHelper
    def setCurrentItemHelper(self,item):

        self.oops()

        # w = self.treeWidget
        # w.setCurrentItem(item)
    #@-node:ekr.20090124111416.14:setCurrentItemHelper
    #@+node:ekr.20090124111416.7:setItemText
    def setItemText (self,item,s):

        self.oops()

        # item.setText(0,s)
    #@-node:ekr.20090124111416.7:setItemText
    #@+node:ekr.20090124101342.35:Icons
    #@+node:ekr.20090124101342.36:drawIcon
    def drawIcon (self,p):

        '''Redraw the icon at p.'''

        self.oops()

        # w = self.treeWidget
        # itemOrTree = self.position2item(p) or w
        # item = QtGui.QTreeWidgetItem(itemOrTree)
        # icon = self.getIcon(p)
        # self.setItemIcon(item,icon)
    #@-node:ekr.20090124101342.36:drawIcon
    #@+node:ekr.20090124101342.38:getIcon
    def getIcon(self,p):

        '''Return the proper icon for position p.'''

        self.oops()

        # p.v.iconVal = val = p.v.computeIcon()
        # return self.getCompositeIconImage(p, val)

    # def getCompositeIconImage(self, p, val):

        # userIcons = self.c.editCommands.getIconList(p)
        # statusIcon = self.getIconImage(val)

        # if not userIcons:
            # return statusIcon

        # hash = [i['file'] for i in userIcons if i['where'] == 'beforeIcon']
        # hash.append(str(val))
        # hash.extend([i['file'] for i in userIcons if i['where'] == 'beforeHeadline'])
        # hash = ':'.join(hash)

        # if hash in g.app.gui.iconimages:
            # return g.app.gui.iconimages[hash]

        # images = [g.app.gui.getImageImage(i['file']) for i in userIcons
                 # if i['where'] == 'beforeIcon']
        # images.append(g.app.gui.getImageImage("box%02d.GIF" % val))
        # images.extend([g.app.gui.getImageImage(i['file']) for i in userIcons
                      # if i['where'] == 'beforeHeadline'])
        # width = sum([i.width() for i in images])
        # height = max([i.height() for i in images])

        # pix = QtGui.QPixmap(width,height)
        # pix.fill()
        # pix.setAlphaChannel(pix)
        # painter = QtGui.QPainter(pix)
        # x = 0
        # for i in images:
            # painter.drawPixmap(x,(height-i.height())//2,i)
            # x += i.width()
        # painter.end()

        # g.app.gui.iconimages[hash] = QtGui.QIcon(pix)

        # return g.app.gui.iconimages[hash]
    #@-node:ekr.20090124101342.38:getIcon
    #@+node:ekr.20090124111416.11:setItemIconHelper
    def setItemIconHelper (self,item,icon):

        self.oops()

        # item.setIcon(0,icon)
    #@-node:ekr.20090124111416.11:setItemIconHelper
    #@+node:ekr.20090124101342.40:updateIcon
    def updateIcon (self,p,force=False):

        '''Update p's icon.'''

        if not p: return

        val = p.v.computeIcon()

        # The force arg is needed:
        # Leo's core may have updated p.v.iconVal.
        if p.v.iconVal == val and not force:
            return

        p.v.iconVal = val
        icon = self.getIconImage(val)
        # Update all cloned/joined items.
        items = self.tnode2items(p.v.t)
        for item in items:
            self.setItemIcon(item,icon)
    #@nonl
    #@-node:ekr.20090124101342.40:updateIcon
    #@+node:ekr.20090124101342.41:updateVisibleIcons
    def updateVisibleIcons (self,p):

        '''Update the icon for p and the icons
        for all visible descendants of p.'''

        self.updateIcon(p,force=True)

        if p.hasChildren() and p.isExpanded():
            for child in p.children_iter():
                self.updateVisibleIcons(child)
    #@-node:ekr.20090124101342.41:updateVisibleIcons
    #@-node:ekr.20090124101342.35:Icons
    #@-node:ekr.20090124111416.2:Widget-dependent helpers
    #@-others
#@-node:ekr.20090124101342.1:<< define baseNativeTreeWidget >>
#@nl
#@-node:ekr.20031218072017.3655:@thin leoFrame.py
#@-leo
