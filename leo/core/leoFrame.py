#@+leo-ver=5-thin
#@+node:ekr.20031218072017.3655: * @file leoFrame.py
"""The base classes for all Leo Windows, their body, log and tree panes, key bindings and menus.

These classes should be overridden to create frames for a particular gui."""

#@@language python
#@@tabwidth -4
#@@pagewidth 70

#@+<< imports >>
#@+node:ekr.20120219194520.10464: ** << imports >> (leoFrame)
import leo.core.leoGlobals as g
import leo.core.leoMenu as leoMenu
import leo.core.leoNodes as leoNodes

#@-<< imports >>
#@+<< About handling events >>
#@+node:ekr.20031218072017.2410: ** << About handling events >>
#@+at Leo must handle events or commands that change the text in the outline
# or body panes. We must ensure that headline and body text corresponds
# to the vnode corresponding to presently selected outline, and vice
# versa. For example, when the user selects a new headline in the
# outline pane, we must ensure that:
# 
# 1) All vnodes have up-to-date information and
# 
# 2) the body pane is loaded with the correct data.
# 
# Early versions of Leo attempted to satisfy these conditions when the user
# switched outline nodes. Such attempts never worked well; there were too many
# special cases. Later versions of Leo use a much more direct approach: every
# keystroke in the body pane updates the presently selected vnode immediately.
# 
# The leoTree class contains all the event handlers for the tree pane, and the
# leoBody class contains the event handlers for the body pane. The following
# convenience methods exists:
# 
# - body.updateBody & tree.updateBody:
#     Called by k.masterCommand after any keystroke not handled by k.masterCommand.
#     These are suprising complex.
# 
# - body.bodyChanged & tree.headChanged:
#     Called by commands throughout Leo's core that change the body or headline.
#     These are thin wrappers for updateBody and updateTree.
#@-<< About handling events >>
#@+<< define class DummyHighLevelInterface >>
#@+node:ekr.20111118104929.10211: ** << define class DummyHighLevelInterface >>
class DummyHighLevelInterface (object):

    '''A class to support a do-nothing HighLevelInterface.'''

    # pylint: disable=R0923
    # Interface not implemented.

    def __init__(self,c):
        self.c = c

    # Mutable methods.
    def flashCharacter(self,i,bg='white',fg='red',flashes=3,delay=75):
        pass

    def toPythonIndex (self,index):                 return 0
    def toPythonIndexRowCol(self,index):            return 0,0,0

    # Immutable redirection methods.
    def appendText(self,s):                         pass
    def delete(self,i,j=None):                      pass
    def deleteTextSelection (self):                 pass
    def get(self,i,j):                              return ''
    def getAllText(self):                           return ''
    def getInsertPoint(self):                       return 0
    def getSelectedText(self):                      return ''
    def getSelectionRange (self):                   return 0,0
    def getYScrollPosition (self):                  return 0
    def hasSelection(self):                         return False
    def insert(self,i,s):                           pass    
    def replace (self,i,j,s):                       pass
    def see(self,i):                                pass
    def seeInsertPoint (self):                      pass
    def selectAllText (self,insert=None):           pass
    def setAllText (self,s):                        pass
    def setBackgroundColor(self,color):             pass
    def setFocus(self):                             pass
    def setForegroundColor(self,color):             pass
    def setInsertPoint(self,pos):                   pass
    def setSelectionRange (self,i,j,insert=None):   pass
    def setYScrollPosition (self,i):                pass
    def tag_configure (self,colorName,**keys):      pass

    # Other immutable methods.
    # These all use leoGlobals functions or leoGui methods.
    def clipboard_append(self,s):
        s1 = g.app.gui.getTextFromClipboard()
        g.app.gui.replaceClipboardWith(s1 + s)

    def clipboard_clear (self):
        g.app.gui.replaceClipboardWith('')

    def getFocus(self):
        return g.app.gui.get_focus(self.c)

    def rowColToGuiIndex (self,s,row,col):
        return g.convertRowColToPythonIndex(s,row,col)    

    set_focus = setFocus

#@-<< define class DummyHighLevelInterface >>
#@+<< define class HighLevelInterface >>
#@+node:ekr.20111114102224.9936: ** << define class HighLevelInterface >>
class HighLevelInterface(object):

    '''A class to specify Leo's high-level editing interface
    used throughout Leo's core.

    The interface has two parts:

    1. Standard (immutable) methods that will never be overridden.

    2. Other (mutable) methods that subclasses may override.
    '''

    #@+others
    #@+node:ekr.20111114102224.9950: *3* ctor (HighLevelInterface)
    def __init__ (self,c):

        self.c = c

        self.widget = None

        self.mutable_methods = (
            'flashCharacter',
            'toPythonIndex',
            'toPythonIndexRowCol',
            # 'toGuiIndex', # A synonym.
        )
    #@+node:ekr.20070302101344: *3* Must be defined in the base class (HighLevelInterface)

    def disable (self):

        self.enabled = False

    def enable (self,enabled=True):

        self.enabled = enabled

    #@+node:ekr.20111114102224.9935: *3* mutable methods (HighLevelInterface)
    #@+node:ekr.20111114102224.9946: *4* flashCharacter
    def flashCharacter(self,i,bg='white',fg='red',flashes=3,delay=75):
        pass

    #@+node:ekr.20111114102224.9943: *4* toPythonIndex (HighLevelInterface)
    def toPythonIndex (self,index):

        s = self.getAllText()
        return g.toPythonIndex(s,index)

    toGuiIndex = toPythonIndex
    #@+node:ekr.20111114102224.9945: *4* toPythonIndexRowCol (BaseTextWidget)
    def toPythonIndexRowCol(self,index):

        # This works, but is much slower that the leoQTextEditWidget method.
        s = self.getAllText()
        i = self.toPythonIndex(index)
        row,col = g.convertPythonIndexToRowCol(s,i)
        return i,row,col
    #@+node:ekr.20111114102224.9937: *3* immutable redirection methods (HighLevelInterface)
    def appendText(self,s):
        if self.widget: self.widget.appendText(s)
    def delete(self,i,j=None):
        if self.widget: self.widget.delete(i,j)
    def deleteTextSelection (self):
        if self.widget: self.widget.deleteTextSelection()
    def get(self,i,j):
        return self.widget and self.widget.get(i,j) or ''
    def getAllText(self):
        return self.widget and self.widget.getAllText() or ''
    def getInsertPoint(self):
        return self.widget and self.widget.getInsertPoint() or 0
    def getSelectedText(self):
        return self.widget and self.widget.getSelectedText() or ''
    def getSelectionRange (self):
        return self.widget and self.widget.getSelectionRange() or (0,0)
    def getYScrollPosition (self):
        return self.widget and self.widget.getYScrollPosition() or 0
    def hasSelection(self):
        # Take special care with this, for the benefit of LeoQuickSearchWidget.
        # This problem only happens with the qttabs gui.
        w = self.widget
        return bool(w and hasattr(w,'hasSelection') and w.hasSelection())
    def insert(self,i,s):
        if self.widget: self.widget.insert(i,s)    
    def replace (self,i,j,s):
        if self.widget: self.widget.replace(i,j,s)
    def see(self,i):
        if self.widget: self.widget.see(i)
    def seeInsertPoint (self):
        if self.widget: self.widget.seeInsertPoint()
    def selectAllText (self,insert=None):
        if self.widget: self.widget.selectAllText(insert)
    def setAllText (self,s):
        if self.widget: self.widget.setAllText(s)
    def setBackgroundColor(self,color):
        if self.widget: self.widget.setBackgroundColor(color)
    def setFocus(self):
        if self.widget: self.widget.setFocus()
    def setForegroundColor(self,color):
        if self.widget: self.widget.setForegroundColor(color)
    def setInsertPoint(self,pos):
        if self.widget: self.widget.setInsertPoint(pos)
    def setSelectionRange (self,i,j,insert=None):
        if self.widget: self.widget.setSelectionRange(i,j,insert=insert)
    def setYScrollPosition (self,i):
        if self.widget: self.widget.setYScrollPosition(i)
    def tag_configure (self,colorName,**keys):
        if self.widget: self.widget.tag_configure(colorName,**keys)
    #@+node:ekr.20111114102224.9940: *3* other immutable methods (HighLevelInterface)
    # These all use leoGlobals functions or leoGui methods.

    def clipboard_append(self,s):
        s1 = g.app.gui.getTextFromClipboard()
        g.app.gui.replaceClipboardWith(s1 + s)

    def clipboard_clear (self):
        g.app.gui.replaceClipboardWith('')

    def getFocus(self):
        return g.app.gui.get_focus(self.c)

    def rowColToGuiIndex (self,s,row,col):
        return g.convertRowColToPythonIndex(s,row,col)   

    # def rowColToGuiIndex (self,s,row,col):
        # return self.widget and self.widget.rowColToGuiIndex(s,row,col) or 0 

    set_focus = setFocus
    #@-others
#@-<< define class HighLevelInterface >>
#@+<< define class baseTextWidget >>
#@+node:ekr.20070228074312: ** << define class baseTextWidget >>
class baseTextWidget(object):

    '''The base class for all wrapper classes for leo Text widgets.'''

    #@+others
    #@+node:ekr.20070228074312.1: *3* Birth & special methods (baseTextWidget)
    def __init__ (self,c,baseClassName,name,widget):

        self.baseClassName = baseClassName
        self.c = c
        self.name = name
        self.virtualInsertPoint = None
        self.widget = widget # Not used at present.

    def __repr__(self):
        return '%s: %s' % (self.baseClassName,id(self))
    #@+node:ekr.20070228074312.12: *3* Clipboard (baseTextWidget)
    # There is no need to override these in subclasses.

    def clipboard_clear (self):

        g.app.gui.replaceClipboardWith('')

    def clipboard_append(self,s):

        s1 = g.app.gui.getTextFromClipboard()

        g.app.gui.replaceClipboardWith(s1 + s)
    #@+node:ekr.20081031074455.13: *3* Do-nothings (baseTextWidget)
    # **Do not delete** 
    # The redirection methods of HighLevelInterface 
    # redirect calls from leoBody & leoLog to *this* class.

    def flashCharacter(self,i,bg='white',fg='red',flashes=3,delay=75):
        pass

    def getFocus(self):                         return None
    def getName(self):                          return self.name # Essential.
    def getYScrollPosition (self):              return 0
    def see(self,i):                            pass
    def seeInsertPoint(self):                   pass
    def setBackgroundColor(self,color):         pass  
    def setFocus(self):                         pass
    def setForegroundColor(self,color):         pass
    def setYScrollPosition (self,i):            pass
    def tag_configure (self,colorName,**keys):  pass

    set_focus = setFocus
    #@+node:ekr.20111113141805.10060: *3* Indices (baseTextWidget)
    #@+node:ekr.20070228074312.8: *4* rowColToGuiIndex (baseTextWidget)
    # This method is called only from the colorizer.
    # It provides a huge speedup over naive code.

    def rowColToGuiIndex (self,s,row,col):

        return g.convertRowColToPythonIndex(s,row,col)    
    #@+node:ekr.20070228074312.7: *4* toPythonIndex (baseTextWidget)
    def toPythonIndex (self,index):

        return g.toPythonIndex(self.s,index)

    toGuiIndex = toPythonIndex
    #@+node:ekr.20090320055710.4: *4* toPythonIndexRowCol (baseTextWidget)
    def toPythonIndexRowCol(self,index):

        s = self.getAllText()
        i = self.toPythonIndex(index)
        row,col = g.convertPythonIndexToRowCol(s,i)
        return i,row,col
    #@+node:ekr.20111113141805.10058: *3* Insert point & selection Range (baseTextWidget)
    #@+node:ekr.20070228074312.20: *4* getInsertPoint (baseTextWidget)
    def getInsertPoint(self):

        i = self.ins
        if i is None:
            if self.virtualInsertPoint is None:
                i = 0
            else:
                i = self.virtualInsertPoint

        self.virtualInsertPoint = i

        # g.trace('baseTextWidget): i:',i,'virtual',self.virtualInsertPoint)
        return i
    #@+node:ekr.20070228074312.22: *4* getSelectionRange (baseTextWidget)
    def getSelectionRange (self,sort=True):

        """Return a tuple representing the selected range of the widget.

        Return a tuple giving the insertion point if no range of text is selected."""

        sel = self.sel

        if len(sel) == 2 and sel[0] >= 0 and sel[1] >= 0:
            i,j = sel
            if sort and i > j: sel = j,i # Bug fix: 10/5/07
            return sel
        else:
            i = self.ins
            return i,i

    #@+node:ekr.20070228074312.25: *4* hasSelection
    def hasSelection (self):

        i,j = self.getSelectionRange()
        return i != j
    #@+node:ekr.20070228074312.35: *4* setInsertPoint (baseTextWidget)
    def setInsertPoint (self,pos):

        self.virtualInsertPoint = i = self.toPythonIndex(pos)
        self.ins = i
        self.sel = i,i
    #@+node:ekr.20070228074312.36: *4* setSelectionRange (baseTextWidget)
    def setSelectionRange (self,i,j,insert=None):

        i1, j1, insert1 = i,j,insert
        i,j = self.toPythonIndex(i),self.toPythonIndex(j)

        self.sel = i,j
        self.ins = j

        if insert is not None and insert in (i,j):
            ins = self.toPythonIndex(insert)
            if ins in (i,j):
                self.virtualInsertPoint = ins
    #@+node:ekr.20070228074312.31: *4* selectAllText (baseTextWidget)
    def selectAllText (self,insert=None):

        '''Select all text of the widget.'''

        self.setSelectionRange(0,'end',insert=insert)
    #@+node:ekr.20070228074312.5: *3* oops (baseTextWidget)
    def oops (self):

        g.pr('baseTextWidget oops:',self,g.callers(4),
            'must be overridden in subclass')
    #@+node:ekr.20111113141805.10057: *3* Text (baseTextWidget)
    #@+node:ekr.20070228074312.10: *4* appendText (baseTextWidget)
    def appendText (self,s):

        self.s = self.s + s
        self.ins = len(self.s)
        self.sel = self.ins,self.ins
    #@+node:ekr.20070228074312.13: *4* delete (baseTextWidget)
    def delete(self,i,j=None):

        i = self.toPythonIndex(i)
        if j is None: j = i+ 1
        j = self.toPythonIndex(j)

        # 2011/11/13: This allows subclasses to use this base class method.
        if i > j: i,j = j,i

        # g.trace(i,j,len(s),repr(s[:20]))
        s = self.getAllText()
        self.setAllText(s[:i] + s[j:])

        # Bug fix: 2011/11/13: Significant in external tests.
        self.setSelectionRange(i,i,insert=i)
    #@+node:ekr.20070228074312.14: *4* deleteTextSelection (baseTextWidget)
    def deleteTextSelection (self):

        i,j = self.getSelectionRange()
        self.delete(i,j)
    #@+node:ekr.20070228074312.18: *4* get (baseTextWidget)
    def get(self,i,j=None):

        i = self.toPythonIndex(i)
        if j is None: j = i+ 1
        j = self.toPythonIndex(j)
        s = self.s[i:j]
        return g.toUnicode(s)
    #@+node:ekr.20070228074312.19: *4* getAllText (baseTextWidget)
    def getAllText (self):

        s = self.s
        return g.toUnicode(s)
    #@+node:ekr.20070228074312.21: *4* getSelectedText (baseTextWidget)
    def getSelectedText (self):

        i,j = self.sel
        s = self.s[i:j]
        return g.toUnicode(s)
    #@+node:ekr.20070228074312.26: *4* insert (baseTextWidget)
    def insert(self,i,s):

        i = self.toPythonIndex(i)
        s1 = s
        self.s = self.s[:i] + s1 + self.s[i:]
        i += len(s1)
        self.ins = i
        self.sel = i,i
    #@+node:ekr.20070228074312.28: *4* replace (baseTextWidget)
    def replace (self,i,j,s):

        self.delete(i,j)
        self.insert(i,s)
    #@+node:ekr.20070228074312.32: *4* setAllText (baseTextWidget)
    def setAllText (self,s):

        self.s = s
        i = len(self.s)
        self.ins = i
        self.sel = i,i
    #@-others
#@-<< define class baseTextWidget >>
#@+<< define class stringTextWidget >>
#@+node:ekr.20070228074228.1: ** << define class stringTextWidget >>
class stringTextWidget (baseTextWidget):

    '''A class that represents text as a Python string.'''

    #@+others
    #@+node:ekr.20070228074228.2: *3* ctor (stringTextWidget)
    def __init__ (self,c,name):

        # Init the base class
        baseTextWidget.__init__ (self,c=c,
            baseClassName='stringTextWidget',name=name,widget=None)

        self.ins = 0
        self.sel = 0,0
        self.s = ''
        self.trace = False
    #@+node:ekr.20070228111853: *3* setSelectionRange (stringTextWidget)
    def setSelectionRange (self,i,j,insert=None):

        i1, j1, insert1 = i,j,insert
        i,j = self.toPythonIndex(i),self.toPythonIndex(j)

        self.sel = i,j

        if insert is not None: 
            self.ins = self.toPythonIndex(insert)
        else:
            self.ins = j

        if self.trace: g.trace('i',i,'j',j,'insert',repr(insert))
    #@-others
#@-<< define class stringTextWidget >>

#@+others
#@+node:ekr.20031218072017.3656: ** class leoBody (HighLevelInterface)
class leoBody (HighLevelInterface):

    """The base class for the body pane in Leo windows."""

    #@+others
    #@+node:ekr.20031218072017.3657: *3* leoBody.__init__
    def __init__ (self,frame,parentFrame):

        c = frame.c

        HighLevelInterface.__init__(self,c)
            # Init the base class

        frame.body = self
        self.c = c
        self.editorWidgets = {} # keys are pane names, values are text widgets
        self.forceFullRecolorFlag = False
        self.frame = frame
        self.parentFrame = parentFrame # New in Leo 4.6.
        self.totalNumberOfEditors = 0

        # May be overridden in subclasses...
        self.widget = None # self.bodyCtrl is now a property.
        self.numberOfEditors = 1
        self.pb = None # paned body widget.
        self.use_chapters = c.config.getBool('use_chapters')

        # Must be overridden in subclasses...
        self.colorizer = None

    #@+node:ekr.20061109173122: *3* leoBody: must be defined in subclasses
    # Birth, death & config
    def createControl (self,parentFrame,p):         self.oops()
    def createTextWidget (self,parentFrame,p,name): self.oops() ; return None

    # Editor
    def createEditorFrame (self,w):             self.oops() ; return None
    def createEditorLabel (self,pane):          self.oops()
    def packEditorLabelWidget (self,w):         self.oops()
    def setEditorColors (self,bg,fg):           self.oops()

    # Events...
    def scheduleIdleTimeRoutine (self,function,*args,**keys): self.oops()
    #@+node:ekr.20061109173021: *3* leoBody: must be defined in the base class
    #@+node:ekr.20031218072017.3677: *4* Coloring (leoBody)
    def getColorizer(self):

        return self.colorizer

    def updateSyntaxColorer(self,p):

        return self.colorizer.updateSyntaxColorer(p.copy())

    def recolor(self,p,incremental=False):

        self.c.requestRecolorFlag = True
        self.c.incrementalRecolorFlag = incremental

    recolor_now = recolor
    #@+node:ekr.20060528100747: *4* Editors (leoBody)
    # This code uses self.pb, a paned body widget, created by tkBody.finishCreate.


    #@+node:ekr.20070424053629: *5* entries
    #@+node:ekr.20060528100747.1: *6* addEditor (leoBody)
    def addEditor (self,event=None):

        '''Add another editor to the body pane.'''

        c = self.c ; p = c.p

        self.totalNumberOfEditors += 1
        self.numberOfEditors += 1

        if self.numberOfEditors == 2:
            # Inject the ivars into the first editor.
            # Bug fix: Leo 4.4.8 rc1: The name of the last editor need not be '1'
            d = self.editorWidgets ; keys = list(d.keys())
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
        #@+<< create text widget w >>
        #@+node:ekr.20060528110922: *7* << create text widget w >> leoBody.addEditor
        w = self.createTextWidget(f,name=name,p=p)
        w.delete(0,'end')
        w.insert('end',p.b)
        w.see(0)

        # self.setFontFromConfig(w=w)
        # self.setColorFromConfig(w=w)
        # self.createBindings(w=w)
        c.k.completeAllBindingsForWidget(w)

        self.recolorWidget(p,w)
        #@-<< create text widget w >>
        self.editorWidgets[name] = w

        for pane in panes:
            self.pb.configurepane(pane,size=minSize)

        self.pb.updatelayout()
        c.frame.body.widget = w # bodyCtrl is now a property.

        self.updateInjectedIvars(w,p)
        self.selectLabel(w)
        self.selectEditor(w)
        self.updateEditors()
        c.bodyWantsFocus()
    #@+node:ekr.20060528132829: *6* assignPositionToEditor (leoBody)
    def assignPositionToEditor (self,p):

        '''Called *only* from tree.select to select the present body editor.'''

        c = self.c
        assert (c.frame.body.bodyCtrl == c.frame.body.widget)
        w = c.frame.body.widget
        self.updateInjectedIvars(w,p)
        self.selectLabel(w)
        # g.trace('===',id(w),w.leo_chapter.name,w.leo_p.h)
    #@+node:ekr.20060528170438: *6* cycleEditorFocus (leoBody)
    def cycleEditorFocus (self,event=None):

        '''Cycle keyboard focus between the body text editors.'''

        c = self.c
        d = self.editorWidgets
        w = c.frame.body.bodyCtrl
        values = list(d.values())
        if len(values) > 1:
            i = values.index(w) + 1
            if i == len(values): i = 0
            w2 = list(d.values())[i]
            assert(w!=w2)
            self.selectEditor(w2)
            c.frame.body.bodyCtrl = w2
    #@+node:ekr.20060528113806: *6* deleteEditor (leoBody)
    def deleteEditor (self,event=None):

        '''Delete the presently selected body text editor.'''

        c = self.c
        w = c.frame.body.bodyCtrl
        d = self.editorWidgets
        if len(list(d.keys())) == 1: return
        name = w.leo_name
        del d [name] 
        self.pb.delete(name)
        panes = self.pb.panes()
        minSize = float(1.0/float(len(panes)))
        for pane in panes:
            self.pb.configurepane(pane,size=minSize)

        # Select another editor.
        w = list(d.values())[0]
        # c.frame.body.bodyCtrl = w # Don't do this now?
        self.numberOfEditors -= 1
        self.selectEditor(w)
    #@+node:ekr.20070425180705: *6* findEditorForChapter (leoBody)
    def findEditorForChapter (self,chapter,p):

        '''Return an editor to be assigned to chapter.'''

        c = self.c ; d = self.editorWidgets ; values = list(d.values())

        # First, try to match both the chapter and position.
        if p:
            for w in values:
                if (
                    hasattr(w,'leo_chapter') and w.leo_chapter == chapter and
                    hasattr(w,'leo_p') and w.leo_p and w.leo_p == p
                ):
                    # g.trace('***',id(w),'match chapter and p',p.h)
                    return w

        # Next, try to match just the chapter.
        for w in values:
            if hasattr(w,'leo_chapter') and w.leo_chapter == chapter:
                # g.trace('***',id(w),'match only chapter',p.h)
                return w

        # As a last resort, return the present editor widget.
        # g.trace('***',id(self.bodyCtrl),'no match',p.h)
        return c.frame.body.bodyCtrl
    #@+node:ekr.20060530210057: *6* select/unselectLabel (leoBody)
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
    #@+node:ekr.20061017083312: *6* selectEditor & helpers (leoBody)
    selectEditorLockout = False

    def selectEditor(self,w):

        '''Select editor w and node w.leo_p.'''

        #  Called whenever w must be selected.
        c = self.c
        if self.selectEditorLockout:
            return
        if w and w == self.c.frame.body.bodyCtrl:
            if w.leo_p and w.leo_p != c.p:
                c.selectPosition(w.leo_p)
                c.bodyWantsFocus()
            return
        try:
            val = None
            self.selectEditorLockout = True
            val = self.selectEditorHelper(w)
        finally:
            self.selectEditorLockout = False
        return val # Don't put a return in a finally clause.
    #@+node:ekr.20070423102603: *7* selectEditorHelper (leoBody)
    def selectEditorHelper (self,w):

        c = self.c
        trace = False and not g.unitTesting
        if not w.leo_p:
            g.trace('no w.leo_p') 
            return
        if trace: g.trace('==1',id(w),
            hasattr(w,'leo_chapter') and w.leo_chapter and w.leo_chapter.name,
            hasattr(w,'leo_p') and w.leo_p and w.leo_p.h)
        self.deactivateActiveEditor(w)
        # The actual switch.
        c.frame.body.bodyCtrl = w
        w.leo_active = True
        self.switchToChapter(w)
        self.selectLabel(w)
        if not self.ensurePositionExists(w):
            g.trace('***** no position editor!')
            return
        if trace:
            g.trace('==2',id(w),
                hasattr(w,'leo_chapter') and w.leo_chapter and w.leo_chapter.name,
                hasattr(w,'leo_p') and w.leo_p and w.leo_p.h)
        # g.trace('expanding ancestors of ',w.leo_p.h,g.callers())
        p = w.leo_p
        c.redraw(p)
        c.recolor()
        c.bodyWantsFocus()
    #@+node:ekr.20060528131618: *6* updateEditors (leoBody)
    # Called from addEditor and assignPositionToEditor

    def updateEditors (self):

        c = self.c ; p = c.p
        d = self.editorWidgets
        if len(list(d.keys())) < 2: return # There is only the main widget.

        for key in d:
            w = d.get(key)
            v = w.leo_v
            if v and v == p.v and w != c.frame.body.bodyCtrl:
                w.delete(0,'end')
                w.insert('end',p.b)
                # g.trace('update',w,v)
                self.recolorWidget(p,w)
        c.bodyWantsFocus()
    #@+node:ekr.20070424053629.1: *5* utils
    #@+node:ekr.20070422093128: *6* computeLabel (leoBody)
    def computeLabel (self,w):

        s = w.leo_label_s

        if hasattr(w,'leo_chapter') and w.leo_chapter:
            s = '%s: %s' % (w.leo_chapter.name,s)

        return s
    #@+node:ekr.20070422094710: *6* createChapterIvar (leoBody)
    def createChapterIvar (self,w):

        c = self.c ; cc = c.chapterController

        if not hasattr(w,'leo_chapter') or not w.leo_chapter:
            if cc and self.use_chapters:
                w.leo_chapter = cc.getSelectedChapter()
            else:
                w.leo_chapter = None
    #@+node:ekr.20070424084651: *6* ensurePositionExists (leoBody)
    def ensurePositionExists(self,w):

        '''Return True if w.leo_p exists or can be reconstituted.'''

        c = self.c

        if c.positionExists(w.leo_p):
            return True
        else:
            g.trace('***** does not exist',w.leo_name)
            for p2 in c.all_unique_positions():
                if p2.v and p2.v == w.leo_v:
                    w.leo_p = p2.copy()
                    return True
            else:
                 # This *can* happen when selecting a deleted node.
                w.leo_p = c.p
                return False
    #@+node:ekr.20070424080640: *6* deactivateActiveEditor (leoBody)
    # Not used in Qt.

    def deactivateActiveEditor(self,w):

        '''Inactivate the previously active editor.'''

        d = self.editorWidgets

        # Don't capture ivars here! assignPositionToEditor keeps them up-to-date. (??)
        for key in d:
            w2 = d.get(key)
            if w2 != w and w2.leo_active:
                w2.leo_active = False
                self.unselectLabel(w2)
                return
    #@+node:ekr.20060530204135: *6* recolorWidget (leoBody)
    def recolorWidget (self,p,w):

        c = self.c ; old_w = c.frame.body.bodyCtrl

        # g.trace('w',id(w),p.h,len(w.getAllText()))

        # Save.
        c.frame.body.bodyCtrl = w
        try:
            c.frame.body.colorizer.colorize(p,incremental=False,interruptable=False)
        finally:
            # Restore.
            c.frame.body.bodyCtrl = old_w
    #@+node:ekr.20070424084012: *6* switchToChapter (leoBody)
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
                c.bodyWantsFocus()
    #@+node:ekr.20070424092855: *6* updateInjectedIvars (leoBody)
    # Called from addEditor and assignPositionToEditor.

    def updateInjectedIvars (self,w,p):

        c = self.c ; cc = c.chapterController

        # Was in ctor.
        use_chapters = c.config.getBool('use_chapters')

        if cc and use_chapters:
            w.leo_chapter = cc.getSelectedChapter()
        else:
            w.leo_chapter = None

        w.leo_p = p.copy()
        w.leo_v = w.leo_p.v
        w.leo_label_s = p.h

        # g.trace('   ===', id(w),w.leo_chapter and w.leo_chapter.name,p.h)
    #@+node:ekr.20031218072017.1329: *4* onBodyChanged (leoBody)
    # This is the only key handler for the body pane.
    def onBodyChanged (self,undoType,oldSel=None,oldText=None,oldYview=None):

        '''Update Leo after the body has been changed.'''

        trace = False and not g.unitTesting
        c = self.c
        body = self
        w = self.bodyCtrl
        p = c.p
        insert = w.getInsertPoint()
        ch = g.choose(insert==0,'',w.get(insert-1))
        ch = g.toUnicode(ch)
        newText = w.getAllText() # Note: getAllText converts to unicode.
        newSel = w.getSelectionRange()
        if not oldText:
            oldText = p.b ; changed = True
        else:
            changed = oldText != newText
        if not changed: return
        if trace:
            # g.trace(repr(ch),'changed:',changed,'newText:',len(newText),'w',w)
            g.trace('oldSel',oldSel,'newSel',newSel)
        c.undoer.setUndoTypingParams(p,undoType,
            oldText=oldText,newText=newText,oldSel=oldSel,newSel=newSel,oldYview=oldYview)
        p.v.setBodyString(newText)
        p.v.insertSpot = body.getInsertPoint()
        #@+<< recolor the body >>
        #@+node:ekr.20051026083733.6: *5* << recolor the body >>
        c.frame.scanForTabWidth(p)
        body.recolor(p,incremental=not self.forceFullRecolorFlag)
        self.forceFullRecolorFlag = False

        if g.app.unitTesting:
            g.app.unitTestDict['colorized'] = True
        #@-<< recolor the body >>
        if not c.changed: c.setChanged(True)
        self.updateEditors()
        p.v.contentModified()
        #@+<< update icons if necessary >>
        #@+node:ekr.20051026083733.7: *5* << update icons if necessary >>

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
            c.redraw_after_icons_changed()
        #@-<< update icons if necessary >>
    #@+node:ekr.20031218072017.3658: *4* oops
    def oops (self):

        g.trace("leoBody oops:", g.callers(4), "should be overridden in subclass")
    #@+node:ekr.20031218072017.4018: *4* Text (leoBody)
    #@+node:ekr.20031218072017.4030: *5* getInsertLines
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

        before = g.toUnicode(before)
        ins    = g.toUnicode(ins)
        after  = g.toUnicode(after)

        return before,ins,after
    #@+node:ekr.20031218072017.4031: *5* getSelectionAreas
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

        before = g.toUnicode(before)
        sel    = g.toUnicode(sel)
        after  = g.toUnicode(after)
        return before,sel,after
    #@+node:ekr.20031218072017.2377: *5* getSelectionLines
    def getSelectionLines (self):

        """Return before,sel,after where:

        before is the all lines before the selected text
        (or the text before the insert point if no selection)
        sel is the selected text (or "" if no selection)
        after is all lines after the selected text
        (or the text after the insert point if no selection)"""

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
        before = g.toUnicode(s[0:i])
        sel    = g.toUnicode(s[i:j])
        after  = g.toUnicode(s[j:len(s)])
        # g.trace(i,j,'sel',repr(s[i:j]),'after',repr(after))
        return before,sel,after # 3 strings.
    #@+node:ekr.20031218072017.4037: *5* setSelectionAreas (leoBody)
    def setSelectionAreas (self,before,sel,after):

        """Replace the body text by before + sel + after and
        set the selection so that the sel text is selected."""

        body = self ; w = body.bodyCtrl

        # 2012/02/05: save/restore Yscroll position.
        pos = w.getYScrollPosition()
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
        w.setYScrollPosition(pos)
        return i,j
    #@+node:ekr.20031218072017.4038: *5* get/setYScrollPosition (leoBody)
    def getYScrollPosition (self):

        i = self.bodyCtrl.getYScrollPosition()
        return i

    def setYScrollPosition (self,i):

        self.bodyCtrl.setYScrollPosition(i)
    #@+node:ekr.20081005065934.6: *3* leoBody: may be defined in subclasses
    # These are optional.
    def after_idle (self,idle_handler,thread_count):
        pass

    def forceFullRecolor (self):
        self.forceFullRecolorFlag = True

    def initAfterLoad (self):
        pass
    #@+node:ekr.20111115100829.9789: *3* body.bodyCtrl property
    def __get_bodyCtrl(self):

        return self.widget

    def __set_bodyCtrl(self,val):

        self.widget = val


    bodyCtrl = property(
        __get_bodyCtrl,
        __set_bodyCtrl,
        doc = "body.bodyCtrl property"
    )
    #@+node:ekr.20130303133655.10213: *3* leoBody.attribute_test
    def pyflake_test(self):
        
        # pylint: disable=E1101
        # Pylint correctly finds attribute errors: xyzzy22 and def_stack.
        print(self.xyzzy22)
        
        # pyflakes incorrectly complains that dn is not used.
        dn = self.def_stack[-1] # Add the code at the top of the stack.
        dn.code += 'abc'
    #@-others
#@+node:ekr.20031218072017.3678: ** class leoFrame
class leoFrame:

    """The base class for all Leo windows."""

    instances = 0

    #@+others
    #@+node:ekr.20031218072017.3679: *3*   leoFrame.__init__
    def __init__ (self,c,gui):

        self.c = c
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
    #@+node:ekr.20051009045404: *4* frame.createFirstTreeNode
    def createFirstTreeNode (self):

        f = self ; c = f.c

        v = leoNodes.vnode(context=c)
        p = leoNodes.position(v)
        v.initHeadString("NewHeadline")
        # New in Leo 4.5: p.moveToRoot would be wrong: the node hasn't been linked yet.
        p._linkAsRoot(oldRoot=None)
        # c.setRootPosition() # New in 4.4.2.
    #@+node:ekr.20061109125528.1: *3* Must be defined in base class
    #@+node:ekr.20031218072017.3689: *4* initialRatios (leoFrame)
    def initialRatios (self):

        c = self.c

        s = c.config.get("initial_split_orientation","string")
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
    #@+node:ekr.20031218072017.3690: *4* longFileName & shortFileName
    def longFileName (self):

        return self.c.mFileName

    def shortFileName (self):

        return g.shortFileName(self.c.mFileName)
    #@+node:ekr.20031218072017.3691: *4* oops
    def oops(self):

        g.pr("leoFrame oops:", g.callers(4), "should be overridden in subclass")
    #@+node:ekr.20031218072017.3692: *4* promptForSave (leoFrame)
    def promptForSave (self):

        """Prompt the user to save changes.

        Return True if the user vetos the quit or save operation."""

        c = self.c
        theType = g.choose(g.app.quitting, "quitting?", "closing?")

        # See if we are in quick edit/save mode.
        root = c.rootPosition()
        quick_save = not c.mFileName and not root.next() and root.isAtEditNode()
        if quick_save:
            name = g.shortFileName(root.atEditNodeName())
        else:
            name = g.choose(c.mFileName,c.mFileName,self.title)
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
                root = c.rootPosition()
                if not root.next() and root.isAtEditNode():
                    # There is only a single @edit node in the outline.
                    # A hack to allow "quick edit" of non-Leo files.
                    # See https://bugs.launchpad.net/leo-editor/+bug/381527
                    # Write the @edit node if needed.
                    if root.isDirty():
                        c.atFileCommands.writeOneAtEditNode(root,
                            toString=False,force=True)
                    return False # Don't save and don't veto.
                else:
                    c.mFileName = g.app.gui.runSaveFileDialog(
                        initialfile = '',
                        title="Save",
                        filetypes=[("Leo files", "*.leo")],
                        defaultextension=".leo")
                    c.bringToFront()
            if c.mFileName:
                ok = c.fileCommands.save(c.mFileName)
                return not ok # New in 4.2: Veto if the save did not succeed.
            else:
                return True # Veto.
    #@+node:ekr.20031218072017.1375: *4* frame.scanForTabWidth (must be fast)
    def scanForTabWidth (self,p):

        c = self.c ; w = c.tab_width
        w = g.findTabWidthDirectives(c,p)
        if w is None: w = c.tab_width
        c.frame.setTabWidth(w)
        c.tab_width = w # 2011/10/24
        # g.trace(w)
    #@+node:ekr.20061119120006: *4* Icon area convenience methods
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
    #@+node:ekr.20041223105114.1: *4* Status line convenience methods
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
    #@+node:ekr.20070130115927.4: *4* Cut/Copy/Paste (leoFrame)
    #@+node:ekr.20070130115927.5: *5* copyText (leoFrame)
    def copyText (self,event=None):

        '''Copy the selected text from the widget to the clipboard.'''

        trace = False and not g.unitTesting
        f = self ; c = f.c
        w = event and event.widget
        wname = (w and c.widget_name(w)) or '<no widget>'
        if trace: g.trace(g.app.gui.isTextWidget(w),wname,w)
        if not w or not g.app.gui.isTextWidget(w): return

        # Set the clipboard text.
        i,j = w.getSelectionRange()
        if i != j:
            s = w.get(i,j)
            g.app.gui.replaceClipboardWith(s)

    OnCopyFromMenu = copyText
    #@+node:ekr.20070130115927.6: *5* leoFrame.cutText
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
            # 2011/11/14: Not used at present.
            # width = f.tree.headWidth(p=None,s=s)
            # w.setWidth(width)
        else: pass

    OnCutFromMenu = cutText
    #@+node:ekr.20070130115927.7: *5* leoFrame.pasteText
    def pasteText (self,event=None,middleButton=False):

        '''Paste the clipboard into a widget.
        If middleButton is True, support x-windows middle-mouse-button easter-egg.'''

        trace = False and not g.unitTesting
        f = self ; c = f.c
        w = event and event.widget
        wname = (w and c.widget_name(w)) or '<no widget>'
        if trace: g.trace(g.app.gui.isTextWidget(w),w)
        if not w or not g.app.gui.isTextWidget(w): return

        i,j = oldSel = w.getSelectionRange()  # Returns insert point if no selection.
        oldText = w.getAllText()

        if middleButton and c.k.previousSelection is not None:
            start,end = c.k.previousSelection
            s = w.getAllText()
            s = s[start:end]
            c.k.previousSelection = None
        else:
            s = g.app.gui.getTextFromClipboard()
        s = g.toUnicode(s)
        # g.trace('pasteText','wname',wname,'s',s,g.callers())
        singleLine = wname.startswith('head') or wname.startswith('minibuffer')
        if singleLine:
            # Strip trailing newlines so the truncation doesn't cause confusion.
            while s and s [ -1] in ('\n','\r'):
                s = s [: -1]

        # Update the widget.
        if i != j:
            w.delete(i,j)
        w.insert(i,s)
        w.see(i+len(s) + 2) # 2011/06/01

        if wname.startswith('body'):
            c.frame.body.forceFullRecolor()
            c.frame.body.onBodyChanged('Paste',oldSel=oldSel,oldText=oldText)
        elif singleLine:
            s = w.getAllText()
            while s and s [ -1] in ('\n','\r'):
                s = s [: -1]
            # 2011/11/14: headline width methods do nothing at present.
            # if wname.startswith('head'):
                # The headline is not officially changed yet.
                # p.initHeadString(s)
                # width = f.tree.headWidth(p=None,s=s)
                # w.setWidth(width)
        else: pass

    OnPasteFromMenu = pasteText
    #@+node:ekr.20061016071937: *5* OnPaste (To support middle-button paste)
    def OnPaste (self,event=None):

        return self.pasteText(event=event,middleButton=True)
    #@+node:ekr.20031218072017.3980: *4* Edit Menu... (leoFrame)
    #@+node:ekr.20031218072017.3981: *5* abortEditLabelCommand (leoFrame)
    def abortEditLabelCommand (self,event=None):

        '''End editing of a headline and revert to its previous value.'''

        frame = self ; c = frame.c ; tree = frame.tree
        p = c.p

        if g.app.batchMode:
            c.notValidInBatchMode("Abort Edit Headline")
            return

        # Revert the headline text.
        # Calling c.setHeadString is required.
        # Otherwise c.redraw would undo the change!
        c.setHeadString(p,tree.revertHeadline)
        c.redraw(p)
    #@+node:ekr.20031218072017.3982: *5* frame.endEditLabelCommand
    def endEditLabelCommand (self,event=None,p=None):

        '''End editing of a headline and move focus to the body pane.'''

        frame = self ; c = frame.c ; k = c.k
        if g.app.batchMode:
            c.notValidInBatchMode("End Edit Headline")
        else:
            c.endEditing()
            c.treeEditFocusHelper()

            if k and not c.stayInTreeAfterEdit:
                k.setDefaultInputState()
                # Recolor the *body* text, **not** the headline.
                k.showStateAndMode(w=c.frame.body.bodyCtrl)
    #@+node:ekr.20031218072017.3983: *5* insertHeadlineTime
    def insertHeadlineTime (self,event=None):

        '''Insert a date/time stamp in the headline of the selected node.'''

        frame = self ; c = frame.c ; p = c.p

        if g.app.batchMode:
            c.notValidInBatchMode("Insert Headline Time")
            return

        c.endEditing()

        time = c.getTime(body=False)
        s = p.h.rstrip()
        if s:
            p.h = ' '.join([s, time])
        else:
            p.h = time
        
        c.redrawAndEdit(p,selectAll=True)
    #@+node:ekr.20031218072017.3680: *3* Must be defined in subclasses
    #@+node:ekr.20031218072017.3683: *4* Config...
    def resizePanesToRatio (self,ratio,secondary_ratio):    self.oops()
    def setInitialWindowGeometry (self):                    self.oops()
    def setTopGeometry (self,w,h,x,y,adjustSize=True):      self.oops()
    #@+node:ekr.20031218072017.3681: *4* Gui-dependent commands (leoFrame)
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
    #@+node:ekr.20031218072017.3682: *4* Window...
    # Important: nothing would be gained by calling gui versions of these methods:
    #            they can be defined in a gui-dependent way in a subclass.

    def bringToFront (self):    self.oops()
    def deiconify (self):       self.oops()
    def get_window_info(self):  self.oops()
    def lift (self):            self.oops()

    #@+node:ekr.20061109125528: *3* May be defined in subclasses
    #@+node:ekr.20071027150501: *4* event handlers (leoFrame)
    def OnBodyClick (self,event=None):
        pass

    def OnBodyRClick(self,event=None):
        pass
    #@+node:ekr.20031218072017.3688: *4* getTitle & setTitle (leoFrame)
    def getTitle (self):
        return self.title

    def setTitle (self,title):
        # g.trace('**(leoFrame)',title)
        self.title = title
    #@+node:ekr.20081005065934.3: *4* initAfterLoad  & initCompleteHint (leoFrame)
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
    #@+node:ekr.20031218072017.3687: *4* setTabWidth (leoFrame)
    def setTabWidth (self,w):

        # Subclasses may override this to affect drawing.
        self.tab_width = w
    #@+node:ekr.20060206093313: *3* Focus (leoFrame)
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
    #@-others
#@+node:ekr.20031218072017.3694: ** class leoLog (HighLevelInterface)
class leoLog (HighLevelInterface):

    """The base class for the log pane in Leo windows."""

    #@+others
    #@+node:ekr.20031218072017.3695: *3*  ctor (leoLog)
    def __init__ (self,frame,parentFrame):

        self.frame = frame
        self.c = c = frame and frame.c or None

        HighLevelInterface.__init__(self,c)
            # Init the base class

        self.enabled = True
        self.newlines = 0
        self.isNull = False

        # Official status variables.  Can be used by client code.
        self.canvasCtrl = None # Set below. Same as self.canvasDict.get(self.tabName)
        self.widget = None # Set below. Same as self.textDict.get(self.tabName)
        self.tabName = None # The name of the active tab.
        self.tabFrame = None # Same as self.frameDict.get(self.tabName)

        self.canvasDict = {} # Keys are page names.  Values are Tk.Canvas's.
        self.frameDict = {}  # Keys are page names. Values are Tk.Frames.
        self.logNumber = 0 # To create unique name fields for text widgets.
        self.newTabCount = 0 # Number of new tabs created.
        self.textDict = {}  # Keys are page names. Values are logCtrl's (text widgets).
    #@+node:ekr.20070302101023: *3* May be overridden (HighLevelInterface)
    def createControl (self,parentFrame):           pass
    def createCanvas (self,tabName):                pass
    def createTextWidget (self,parentFrame):        return None
    def finishCreate (self):                        pass
    def initAfterLoad (self):                       pass
    #@+node:ekr.20070302094848.1: *4* clearTab
    def clearTab (self,tabName,wrap='none'):

        self.selectTab(tabName,wrap=wrap)
        w = self.logCtrl
        if w: w.delete(0,'end')
    #@+node:ekr.20070302094848.2: *4* createTab (leoLog)
    def createTab (self,tabName,createText=True,widget=None,wrap='none'):

        if createText:
            w = self.createTextWidget(self.tabFrame)
            self.canvasDict [tabName] = None
            self.textDict [tabName] = w
        else:
            self.canvasDict [tabName] = None
            self.textDict [tabName] = None
            self.frameDict [tabName] = tabName # tabFrame


    #@+node:ekr.20070302094848.4: *4* cycleTabFocus (leoLog)
    def cycleTabFocus (self,event=None):

        '''Cycle keyboard focus between the tabs in the log pane.'''

        d = self.frameDict # Keys are page names. Values are Tk.Frames.
        w = d.get(self.tabName)
        values = list(d.values())
        if self.numberOfVisibleTabs() > 1:
            i = values.index(w) + 1
            if i == len(values): i = 0
            tabName = list(d.keys())[i]
            self.selectTab(tabName)
            return i
    #@+node:ekr.20070302094848.5: *4* deleteTab
    def deleteTab (self,tabName,force=False):

        c = self.c
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
        c.invalidateFocus()
        c.bodyWantsFocus()
    #@+node:ekr.20070302094848.7: *4* getSelectedTab
    def getSelectedTab (self):

        return self.tabName
    #@+node:ekr.20070302094848.6: *4* hideTab
    def hideTab (self,tabName):

        self.selectTab('Log')
    #@+node:ekr.20070302094848.8: *4* lower/raiseTab
    def lowerTab (self,tabName):

        self.c.invalidateFocus()
        self.c.bodyWantsFocus()

    def raiseTab (self,tabName):

        self.c.invalidateFocus()
        self.c.bodyWantsFocus()
    #@+node:ekr.20111122080923.10184: *4* orderedTabNames (leoLog)
    def orderedTabNames (self,leoLog):

        return list(self.frameDict.values())
    #@+node:ekr.20070302094848.9: *4* numberOfVisibleTabs (leoLog)
    def numberOfVisibleTabs (self):

        return len([val for val in list(self.frameDict.values()) if val != None])

    #@+node:ekr.20070302101304: *4* put & putnl (leoLog)
    # All output to the log stream eventually comes here.

    def put (self,s,color=None,tabName='Log',from_redirect=False):
        print (s)

    def putnl (self,tabName='Log'):
        pass # print ('')
    #@+node:ekr.20070302094848.10: *4* renameTab
    def renameTab (self,oldName,newName):
        pass
    #@+node:ekr.20070302094848.11: *4* selectTab (leoLog)
    def selectTab (self,tabName,createText=True,widget=None,wrap='none'):
        # widget unused.

        '''Create the tab if necessary and make it active.'''

        c = self.c
        tabFrame = self.frameDict.get(tabName)
        if not tabFrame:
            self.createTab(tabName,createText=createText)

        # Update the status vars.
        self.tabName = tabName
        self.canvasCtrl = self.canvasDict.get(tabName)
        self.widget = self.textDict.get(tabName)
            # logCtrl is now a property.
        self.tabFrame = self.frameDict.get(tabName)

        if 0:
            # Absolutely do not do this here!
            # It is a cause of the 'sticky focus' problem.
            c.widgetWantsFocusNow(self.logCtrl)

        return tabFrame
    #@+node:ekr.20031218072017.3700: *3* leoLog.oops
    def oops (self):

        g.pr("leoLog oops:", g.callers(4), "should be overridden in subclass")
    #@+node:ekr.20111115100829.9785: *3* log.logCtrl property
    def __get_logCtrl(self):

        return self.widget

    def __set_logCtrl(self,val):

        self.widget = val


    logCtrl = property(
        __get_logCtrl,
        __set_logCtrl,
        doc = "log.logCtrl property"
    )
    #@-others
#@+node:ekr.20031218072017.3704: ** class leoTree
# This would be useful if we removed all the tree redirection routines.
# However, those routines are pretty ingrained into Leo...

class leoTree:

    """The base class for the outline pane in Leo windows."""

    #@+others
    #@+node:ekr.20031218072017.3705: *3*   tree.__init__ (base class)
    def __init__ (self,frame):

        self.frame = frame

        self.c = frame.c

        self.edit_text_dict = {}
            # New in 3.12: keys vnodes, values are edit_widgets.
            # New in 4.2: keys are vnodes, values are pairs (p,edit widgets).

        # "public" ivars: correspond to setters & getters.
        self.drag_p = None
        self._editPosition = None
        self.redrawCount = 0 # For traces
        self.revertHeadline = None
        self.use_chapters = False # May be overridden in subclasses.

        # Define these here to keep pylint happy.
        self.canvas = None
        self.trace_select = None
    #@+node:ekr.20031218072017.3706: *3*  Must be defined in subclasses (leoTree)
    # Drawing & scrolling.
    def drawIcon(self,p):                                       self.oops()
    def redraw(self,p=None,scroll=True,forceDraw=False):        self.oops()
    def redraw_now(self,p=None,scroll=True,forceDraw=False):    self.oops()
    def scrollTo(self,p):                                       self.oops()
    idle_scrollTo = scrollTo # For compatibility.
    # Headlines.
    def editLabel(self,v,selectAll=False,selection=None):       self.oops()
    def edit_widget (self,p):                                   self.oops()
    #@+node:ekr.20061109165848: *3* Must be defined in base class
    #@+node:ekr.20031218072017.3716: *4* Getters/Setters (tree)
    def getEditTextDict(self,v):
        # New in 4.2: the default is an empty list.
        return self.edit_text_dict.get(v,[])

    def editPosition(self):
        return self._editPosition

    def setEditPosition(self,p):
        self._editPosition = p
    #@+node:ekr.20040803072955.90: *4* head key handlers (leoTree)
    #@+node:ekr.20040803072955.91: *5* onHeadChanged (leoTree Not used: see nativeTree)
    # Tricky code: do not change without careful thought and testing.
    # Important: This code *is* used.  See also, nativeTree.onHeadChanged.

    def onHeadChanged (self,p,undoType='Typing',s=None,e=None): # e used in baseNativeTree.

        '''Officially change a headline.
        Set the old undo text to the previous revert point.'''

        trace = False and not g.unitTesting
        c = self.c ; u = c.undoer
        w = self.edit_widget(p)
        if c.suppressHeadChanged:
            if trace: g.trace('c.suppressHeadChanged')
            return
        if not w:
            if trace: g.trace('****** no w for p: %s',repr(p))
            return
        ch = '\n' # New in 4.4: we only report the final keystroke.
        if g.doHook("headkey1",c=c,p=p,v=p,ch=ch):
            return # The hook claims to have handled the event.
        if s is None: s = w.getAllText()
        if trace:
            g.trace('*** leoTree',g.callers(5))
            g.trace(p and p.h,'w',repr(w),'s',repr(s))
        #@+<< truncate s if it has multiple lines >>
        #@+node:ekr.20040803072955.94: *6* << truncate s if it has multiple lines >>
        # Remove one or two trailing newlines before warning of truncation.
        # for i in (0,1):
            # if s and s[-1] == '\n':
                # if len(s) > 1: s = s[:-1]
                # else: s = ''
        while s and s[-1] == '\n':
            s = s[:-1]

        # Warn if there are multiple lines.
        i = s.find('\n')
        if i > -1:
            # g.trace(i,len(s),repr(s))
            g.warning("truncating headline to one line")
            s = s[:i]

        limit = 1000
        if len(s) > limit:
            g.warning("truncating headline to",limit,"characters")
            s = s[:limit]

        s = g.toUnicode(s or '')
        #@-<< truncate s if it has multiple lines >>
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
                dirtyVnodeList=dirtyVnodeList,inHead=True)
        if changed:
            c.redraw_after_head_changed()
            c.treeEditFocusHelper()
        g.doHook("headkey2",c=c,p=p,v=p,ch=ch)
    #@+node:ekr.20040803072955.88: *5* onHeadlineKey
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

        return # (for Tk) 'break' # Required
    #@+node:ekr.20051026083544.2: *5* updateHead
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
            s = s[:-1]

        # 2011/11/14: Not used at present.
        # w.setWidth(self.headWidth(s=s))

        if ch in ('\n','\r'):
            self.endEditLabel() # Now calls self.onHeadChanged.
    #@+node:ekr.20040803072955.126: *5* endEditLabel
    def endEditLabel (self):

        '''End editing of a headline and update p.h.'''

        trace = False and not g.unitTesting
        c = self.c ; k = c.k ; p = c.p
        if trace: g.trace('leoTree',p and p.h,g.callers(4))
        self.setEditPosition(None) # That is, self._editPosition = None
        # Important: this will redraw if necessary.
        self.onHeadChanged(p)
        if 0: # Can't call setDefaultUnboundKeyAction here: it might put us in ignore mode!
            k.setDefaultInputState()
            k.showStateAndMode()

        if 0: # This interferes with the find command and interferes with focus generally!
            c.bodyWantsFocus()
    #@+node:ekr.20040803072955.21: *4* tree.injectCallbacks
    def injectCallbacks(self):

        c = self.c

        #@+<< define callbacks to be injected in the position class >>
        #@+node:ekr.20040803072955.22: *5* << define callbacks to be injected in the position class >>
        # N.B. These vnode methods are entitled to know about details of the leoTkinterTree class.

        #@+others
        #@+node:ekr.20040803072955.23: *6* OnHyperLinkControlClick
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
        #@+node:ekr.20040803072955.24: *6* OnHyperLinkEnter
        def OnHyperLinkEnter (self,event=None,c=c):

            """Callback injected into position class."""

            try:
                p = self
                g.doHook("hyperenter1",c=c,p=p,v=p,event=event)
                g.doHook("hyperenter2",c=c,p=p,v=p,event=event)
            except:
                g.es_event_exception("hyperenter")
        #@+node:ekr.20040803072955.25: *6* OnHyperLinkLeave
        def OnHyperLinkLeave (self,event=None,c=c):

            """Callback injected into position class."""

            try:
                p = self
                g.doHook("hyperleave1",c=c,p=p,v=p,event=event)
                g.doHook("hyperleave2",c=c,p=p,v=p,event=event)
            except:
                g.es_event_exception("hyperleave")
        #@-others
        #@-<< define callbacks to be injected in the position class >>

        for f in (OnHyperLinkControlClick,OnHyperLinkEnter,OnHyperLinkLeave):

            g.funcToMethod(f,leoNodes.position)
    #@+node:ekr.20031218072017.2312: *4* tree.OnIconDoubleClick
    def OnIconDoubleClick (self,p):

        if 0: g.trace(p and p.h)
    #@+node:ekr.20120314064059.9739: *4* tree.OnIconCtrlClick (@url)
    def OnIconCtrlClick (self,p):

        g.openUrl(p)
    #@+node:ekr.20081005065934.8: *3* May be defined in subclasses
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
    def redraw_after_clone(self):           self.c.redraw()
    def redraw_after_contract(self,p=None): self.c.redraw()
    def redraw_after_expand(self,p=None):   self.c.redraw()
    def redraw_after_head_changed(self):    self.c.redraw()
    def redraw_after_icons_changed(self):   self.c.redraw()
    def redraw_after_select(self,p=None):   self.c.redraw()
    #@+node:ekr.20040803072955.128: *3* leoTree.select & helpers
    tree_select_lockout = False

    def select (self,p,scroll=True):

        '''Select a node.
        Never redraws outline, but may change coloring of individual headlines.
        The scroll argument is used by the gui to suppress scrolling while dragging.'''

        if g.app.killed or self.tree_select_lockout:
            return None
        traceTime = False and not g.unitTesting
        if traceTime:
            import time
            t1 = time.time()
        try:
            c = self.c ; old_p = c.p
            val = 'break'
            self.tree_select_lockout = True
            c.frame.tree.beforeSelectHint(p,old_p)
            val = self.selectHelper(p,scroll=scroll)
        finally:
            self.tree_select_lockout = False
            c.frame.tree.afterSelectHint(p,old_p)
        if traceTime:
            g.trace('%2.3f sec' % (time.time()-t1))
        return val  # Don't put a return in a finally clause.
    #@+node:ekr.20070423101911: *4* selectHelper (leoTree) (changed 4.10)
    # Do **not** try to "optimize" this by returning if p==c.p.
    # 2011/11/06: *event handlers* are called only if p != c.p.

    def selectHelper (self,p,scroll):

        # trace = False and not g.unitTesting
        c = self.c
        w = c.frame.body.bodyCtrl
        if not w: return # Defensive.
        old_p = c.p
        call_event_handlers = p != old_p
        if p:
            # 2009/10/10: selecting a foreign position
            # will not be pretty.
            assert p.v.context == c
        else:
            # Do *not* test c.positionExists(p) here.
            # We may be in the process of changing roots.
            return None # Not an error.

        # Part 1: Unselect.
        if call_event_handlers:
            unselect = not g.doHook("unselect1",c=c,new_p=p,old_p=old_p,new_v=p,old_v=old_p)
        else:
            unselect = True
        if unselect:
            #@+<< unselect the old node >>
            #@+node:ekr.20120325072403.7771: *5* << unselect the old node >> (selectHelper)
            if old_p != p:
                self.endEditLabel() # sets editPosition = None
                colorizer = c.frame.body.colorizer
                if (
                    colorizer
                    and hasattr(colorizer,'colorCacheFlag')
                    and colorizer.colorCacheFlag
                    and hasattr(colorizer,'write_colorizer_cache')
                ):
                    colorizer.write_colorizer_cache(old_p)
            #@-<< unselect the old node >>
        if call_event_handlers:
            g.doHook("unselect2",c=c,new_p=p,old_p=old_p,new_v=p,old_v=old_p)
        
        # Part 2a: Start selecting:
        if call_event_handlers:
            select = not g.doHook("select1",c=c,new_p=p,old_p=old_p,new_v=p,old_v=old_p)
        else:
            select = True  
        if select:
            self.selectNewNode(p,old_p)
            c.nodeHistory.update(p) # Remember this position.
            
        # Part 2b: Finish selecting.
        c.setCurrentPosition(p)
        #@+<< set the current node >>
        #@+node:ekr.20040803072955.133: *5* << set the current node >> (selectHelper)
        c.frame.scanForTabWidth(p)
            #GS I believe this should also get into the select1 hook

        # Was in ctor.
        use_chapters = c.config.getBool('use_chapters')

        if use_chapters:
            cc = c.chapterController
            theChapter = cc and cc.getSelectedChapter()
            if theChapter:
                theChapter.p = p.copy()
                # g.trace('tkTree',theChapter.name,'v',id(p.v),p.h)

        c.treeFocusHelper() # 2010/12/14
        c.undoer.onSelect(old_p,p)
        #@-<< set the current node >>
        p.restoreCursorAndScroll()
            # Was in setBodyTextAfterSelect (in <select the new node>)
        c.frame.body.assignPositionToEditor(p) # New in Leo 4.4.1.
        c.frame.updateStatusLine() # New in Leo 4.4.1.

        # if trace and (verbose or call_event_handlers):
            # g.trace('**** after old: %s new %s' % (
                # old_p and len(old_p.b),len(p.b)))

        # what UNL.py used to do
        c.frame.clearStatusLine()
        verbose = getattr(c, 'status_line_unl_mode', '') == 'canonical'
        c.frame.putStatusLine(p.get_UNL(with_proto=verbose))
        if call_event_handlers: # 2011/11/06
            g.doHook("select2",c=c,new_p=p,old_p=old_p,new_v=p,old_v=old_p)
            g.doHook("select3",c=c,new_p=p,old_p=old_p,new_v=p,old_v=old_p)
    #@+node:ekr.20120325072403.7767: *4* leoTree.selectNewNode
    def selectNewNode(self,p,old_p):

        # Bug fix: we must always set this, even if we never edit the node.
        frame = self.c.frame
        self.revertHeadline = p.h
        frame.setWrap(p)
        self.setBodyTextAfterSelect(p,old_p)
    #@+node:ekr.20090608081524.6109: *4* leoTree.setBodyTextAfterSelect
    def setBodyTextAfterSelect (self,p,old_p):

        trace = False and not g.unitTesting

        # Always do this.  Otherwise there can be problems with trailing newlines.
        c = self.c ; w = c.frame.body.bodyCtrl
        s = p.v.b # Guaranteed to be unicode.
        old_s = w.getAllText()

        if p and p == old_p and s == old_s:
            if trace: g.trace('*pass',p.h,old_p.h)
        else:
            # w.setAllText destroys all color tags, so do a full recolor.
            if trace: g.trace('*reload',p.h,old_p and old_p.h)
            w.setAllText(s)
            colorizer = c.frame.body.colorizer
            if hasattr(colorizer,'setHighlighter'):
                colorizer.setHighlighter(p)
            self.frame.body.recolor(p)

        # This is now done after c.p has been changed.
            # p.restoreCursorAndScroll()
    #@+node:ekr.20031218072017.3718: *3* oops
    def oops(self):

        g.pr("leoTree oops:", g.callers(4), "should be overridden in subclass")
    #@-others
#@+node:ekr.20070317073627: ** class leoTreeTab
class leoTreeTab:

    '''A class representing a tabbed outline pane.'''

    #@+others
    #@+node:ekr.20070317073627.1: *3*  ctor (leoTreeTab)
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
    #@+node:ekr.20070317073755: *3* Must be defined in subclasses
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
    #@+node:ekr.20070317083104: *3* oops
    def oops(self):

        g.pr("leoTreeTree oops:", g.callers(4), "should be overridden in subclass")
    #@-others
#@+node:ekr.20031218072017.2191: ** class nullBody (leoBody:HighLevelInterface)
class nullBody (leoBody):
    # LeoBody is a subclass of HighLevelInterface.

    # pylint: disable=R0923
    # Interface not implemented.

    #@+others
    #@+node:ekr.20031218072017.2192: *3*  nullBody.__init__
    def __init__ (self,frame,parentFrame):

        # g.trace('nullBody','frame',frame,g.callers())

        leoBody.__init__ (self,frame,parentFrame) # Init the base class.

        self.insertPoint = 0
        self.selection = 0,0
        self.s = "" # The body text

        w = stringTextWidget(c=self.c,name='body')
        self.bodyCtrl = self.widget = w
        self.editorWidgets['1'] = w
        self.colorizer = nullColorizer(self.c)
    #@+node:ekr.20031218072017.2193: *3* Utils (internal use)
    #@+node:ekr.20031218072017.2194: *4* findStartOfLine
    def findStartOfLine (self,lineNumber):

        lines = g.splitLines(self.s)
        i = 0 ; index = 0
        for line in lines:
            if i == lineNumber: break
            i += 1
            index += len(line)
        return index
    #@+node:ekr.20031218072017.2195: *4* scanToStartOfLine
    def scanToStartOfLine (self,i):

        if i <= 0:
            return 0

        assert(self.s[i] != '\n')

        while i >= 0:
            if self.s[i] == '\n':
                return i + 1

        return 0
    #@+node:ekr.20031218072017.2196: *4* scanToEndOfLine
    def scanToEndOfLine (self,i):

        if i >= len(self.s):
            return len(self.s)

        assert(self.s[i] != '\n')

        while i < len(self.s):
            if self.s[i] == '\n':
                return i - 1

        return i
    #@+node:ekr.20031218072017.2197: *3* nullBody: leoBody interface
    # Birth, death...
    def createControl (self,parentFrame,p):     pass
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
    # def hasFocus (self):                        pass
    def setFocus (self):                        pass
    #@-others
#@+node:ekr.20031218072017.2218: ** class nullColorizer
class nullColorizer:

    """A do-nothing colorer class"""

    #@+others
    #@+node:ekr.20031218072017.2219: *3* __init__ (nullColorizer)
    def __init__ (self,c):

        self.c = c
        self.count = 0
        self.enabled = False
        self.full_recolor_count = 0

    #@+node:ekr.20031218072017.2220: *3* entry points
    def colorize(self,p,incremental=False,interruptable=True):
        self.count += 1 # Used by unit tests.
        return 'ok' # Used by unit tests.

    def disable(self): pass

    def enable(self): pass

    def scanColorDirectives(self,p): pass

    def updateSyntaxColorer (self,p): pass

    def useSyntaxColoring(self,p):
        return None
    #@-others
#@+node:ekr.20031218072017.2222: ** class nullFrame
class nullFrame (leoFrame):

    """A null frame class for tests and batch execution."""

    #@+others
    #@+node:ekr.20040327105706: *3*  ctor (nullFrame)
    def __init__ (self,c,title,gui):

        # g.trace('nullFrame')

        leoFrame.__init__(self,c,gui) # Init the base class.

        assert self.c

        self.bodyCtrl = None
        self.iconBar = nullIconBarClass(self.c,self)
        self.isNullFrame = True
        self.outerFrame = None
        self.statusLineClass = nullStatusLineClass
        self.title = title
        self.top = None # Always None.

        # Create the component objects.
        self.body = nullBody(frame=self,parentFrame=None)
        self.log  = nullLog (frame=self,parentFrame=None)
        self.menu = leoMenu.nullMenu(frame=self)
        self.tree = nullTree(frame=self)

        # Default window position.
        self.w = 600
        self.h = 500
        self.x = 40
        self.y = 40
    #@+node:ekr.20041120073824: *3* destroySelf (nullFrame)
    def destroySelf (self):

        pass
    #@+node:ekr.20040327105706.2: *3* finishCreate (nullFrame)
    def finishCreate(self):
        # This may be overridden in subclasses.
        pass
    #@+node:ekr.20061109124552: *3* Overrides
    #@+node:ekr.20061109123828: *4* Config...
    def resizePanesToRatio (self,ratio,secondary_ratio):    pass
    def setInitialWindowGeometry (self):                    pass

    #@+node:ekr.20041130065718.1: *5* setTopGeometry
    def setTopGeometry (self,w,h,x,y,adjustSize=True):

        self.w = w
        self.h = h
        self.x = x
        self.y = y
    #@+node:ekr.20061109124129: *4* Gui-dependent commands (nullFrame)
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
    #@+node:ekr.20041130065921: *4* Window...
    def bringToFront (self):    pass
    def deiconify (self):       pass
    def get_window_info(self):
        # Set w,h,x,y to a reasonable size and position.
        return 600,500,20,20
    def lift (self):            pass
    def setWrap (self,flag):    pass
    def update(self):           pass

    #@-others
#@+node:ekr.20070301164543: ** class nullIconBarClass
class nullIconBarClass:

    '''A class representing the singleton Icon bar'''

    #@+others
    #@+node:ekr.20070301164543.1: *3*  ctor (nullIconBarClass)
    def __init__ (self,c,parentFrame):

        self.c = c
        self.iconFrame = None
        self.parentFrame = parentFrame
        self.w = g.nullObject()
    #@+node:ekr.20070301164543.2: *3* add
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

        b = nullButtonWidget(self.c,command,name,text)
        return b
    #@+node:ekr.20070301165343: *3* do nothing
    def addRow(self,height=None):
        pass
    def addWidget (self,w):
        pass
    def clear(self):
        g.app.iconWidgetCount = 0
        g.app.iconImageRefs = []
    def deleteButton (self,w):
        pass
    def getNewFrame (self):
        return None
    def hide(self):
        pass
    def setCommandForButton(self,b,command):
        b.command = command
    def show(self):
        pass
    #@-others
#@+node:ekr.20031218072017.2232: ** class nullLog (leoLog)
class nullLog (leoLog):

    # pylint: disable=R0923
    # Interface not implemented.

    #@+others
    #@+node:ekr.20070302095500: *3* Birth
    #@+node:ekr.20041012083237: *4* nullLog.__init__
    def __init__ (self,frame=None,parentFrame=None):

        # Init the base class.
        leoLog.__init__(self,frame,parentFrame)

        self.isNull = True
        self.logNumber = 0
        self.widget = self.createControl(parentFrame)
            # self.logCtrl is now a property of the base leoLog class.
    #@+node:ekr.20120216123546.10951: *4* finishCreate (nullLog)
    def finishCreate(self):
        pass
    #@+node:ekr.20041012083237.1: *4* createControl
    def createControl (self,parentFrame):

        return self.createTextWidget(parentFrame)
    #@+node:ekr.20070302095121: *4* createTextWidget (nullLog)
    def createTextWidget (self,parentFrame):

        self.logNumber += 1
        c = self.c
        log = stringTextWidget(c=c,name="log-%d" % self.logNumber)
        return log
    #@+node:ekr.20111119145033.10186: *3* isLogWidget (nullLog)
    def isLogWidget(self,w):
        return False
    #@+node:ekr.20041012083237.2: *3* oops
    def oops(self):

        g.trace("nullLog:", g.callers(4))
    #@+node:ekr.20041012083237.3: *3* put and putnl (nullLog)
    def put (self,s,color=None,tabName='Log',from_redirect=False):
        # print('(nullGui) print',repr(s))
        if self.enabled:
            try:
                g.pr(s,newline=False)
            except UnicodeError:
                s = s.encode('ascii','replace')
                g.pr(s,newline=False)

    def putnl (self,tabName='Log'):
        if self.enabled:
            g.pr('')
    #@+node:ekr.20060124085830: *3* tabs (nullLog)
    def clearTab        (self,tabName,wrap='none'):             pass
    def createCanvas    (self,tabName):                         pass
    def createTab (self,tabName,createText=True,widget=None,wrap='none'):   pass
    def deleteTab       (self,tabName,force=False):             pass
    def getSelectedTab  (self):                                 return None
    def lowerTab        (self,tabName):                         pass
    def raiseTab        (self,tabName):                         pass
    def renameTab (self,oldName,newName):                       pass
    def selectTab (self,tabName,createText=True,widget=None,wrap='none'):   pass

    #@-others
#@+node:ekr.20070302171509: ** class nullStatusLineClass
class nullStatusLineClass:

    '''A do-nothing status line.'''

    #@+others
    #@+node:ekr.20070302171509.2: *3*  nullStatusLineClass.ctor
    def __init__ (self,c,parentFrame):

        self.c = c
        self.enabled = False
        self.parentFrame = parentFrame
        self.textWidget = stringTextWidget(c,name='status-line')

        # Set the official ivars.
        c.frame.statusFrame = None
        c.frame.statusLabel = None
        c.frame.statusText  = self.textWidget
    #@+node:ekr.20070302171917: *3* methods
    def disable (self,background=None):
        self.enabled = False
        self.c.bodyWantsFocus()

    def enable (self,background="white"):
        self.c.widgetWantsFocus(self.textWidget)
        self.enabled = True

    def clear (self):                   self.textWidget.delete(0,'end')
    def get (self):                     return self.textWidget.getAllText()
    def isEnabled(self):                return self.enabled
    def put(self,s,color=None):         self.textWidget.insert('end',s)
    def setFocus (self):                pass
    def update(self):                   pass
    #@-others
#@+node:ekr.20031218072017.2233: ** class nullTree
class nullTree (leoTree):

    #@+others
    #@+node:ekr.20031218072017.2234: *3*  nullTree.__init__
    def __init__ (self,frame):

        leoTree.__init__(self,frame) # Init the base class.

        assert(self.frame)

        self.editWidgetsDict = {} # Keys are tnodes, values are stringTextWidgets.
        self.font = None
        self.fontName = None
        self.canvas = None
        self.redrawCount = 0
        self.trace_edit = False
        self.trace_select = False
        self.updateCount = 0
    #@+node:ekr.20070228173611: *3* printWidgets
    def printWidgets(self):

        d = self.editWidgetsDict

        for key in d:
            # keys are vnodes, values are stringTextWidgets.
            w = d.get(key)
            g.pr('w',w,'v.h:',key.headString,'s:',repr(w.s))

    #@+node:ekr.20031218072017.2236: *3* Overrides
    #@+node:ekr.20070228163350.1: *4* Drawing & scrolling (nullTree)
    def drawIcon(self,p):
        pass

    def redraw(self,p=None,scroll=True,forceDraw=False):
        self.redrawCount += 1

    def redraw_now(self,p=None,scroll=True,forceDraw=False):
        self.redrawCount += 1

    def redraw_after_contract(self,p=None): self.redraw()
    def redraw_after_expand(self,p=None):   self.redraw()
    def redraw_after_head_changed(self):    self.redraw()
    def redraw_after_icons_changed(self):   self.redraw()
    def redraw_after_select(self,p=None):   self.redraw()

    def scrollTo(self,p):
        pass
    #@+node:ekr.20070228163350.2: *4* edit_widget (nullTree)
    def edit_widget (self,p):
        d = self.editWidgetsDict
        if not p.v:
            return None
        w = d.get(p.v)
        if not w:
            d[p.v] = w = stringTextWidget(
                c=self.c,
                name='head-%d' % (1 + len(list(d.keys()))))
            w.setAllText(p.h)
        return w
    #@+node:ekr.20070228164730: *5* editLabel (nullTree)
    def editLabel (self,p,selectAll=False,selection=None):

        """Start editing p's headline."""

        self.endEditLabel()
        self.setEditPosition(p)
            # That is, self._editPosition = p
        if p:
            self.revertHeadline = p.h
                # New in 4.4b2: helps undo.
    #@+node:ekr.20070228160345: *5* setHeadline (nullTree)
    def setHeadline (self,p,s):

        '''Set the actual text of the headline widget.

        This is called from the undo/redo logic to change the text before redrawing.'''

        # g.trace('p',p.h,'s',repr(s),g.callers())

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
    #@-others
#@-others
#@-leo
