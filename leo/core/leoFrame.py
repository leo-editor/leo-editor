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
import leo.core.leoMenu as LeoMenu
import leo.core.leoNodes as leoNodes

import time
#@-<< imports >>
#@+<< About handling events >>
#@+node:ekr.20031218072017.2410: ** << About handling events >>
#@+at Leo must handle events or commands that change the text in the outline
# or body panes. We must ensure that headline and body text corresponds
# to the VNode corresponding to presently selected outline, and vice
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
# keystroke in the body pane updates the presently selected VNode immediately.
# 
# The LeoTree class contains all the event handlers for the tree pane, and the
# LeoBody class contains the event handlers for the body pane. The following
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
#@+<< define class BaseTextWrapper >>
#@+node:ekr.20070228074312: ** << define class BaseTextWrapper >>
class BaseTextWrapper(object):
    '''The base class for all wrapper classes for leo Text widgets.'''
    #@+others
    #@+node:ekr.20070228074312.1: *3* btw.Birth & special methods
    def __init__ (self,c,baseClassName,name,widget):
        '''Ctor for BaseTextWrapper class.'''
        # g.trace('(BaseTextWrapper)',widget)
        self.baseClassName = baseClassName
        self.c = c
        self.name = name
        self.virtualInsertPoint = None
        self.widget = widget # Used in base classes.

    def __repr__(self):
        return '%s: %s' % (self.baseClassName,id(self))
    #@+node:ekr.20070228074312.12: *3* btw.Clipboard
    # There is no need to override these in subclasses.

    def clipboard_clear (self):

        g.app.gui.replaceClipboardWith('')

    def clipboard_append(self,s):

        s1 = g.app.gui.getTextFromClipboard()

        g.app.gui.replaceClipboardWith(s1 + s)
    #@+node:ekr.20081031074455.13: *3* btw.Do-nothings
    # **Do not delete** 
    # The redirection methods of HighLevelInterface 
    # redirect calls from LeoBody & LeoLog to *this* class.

    def flashCharacter(self,i,bg='white',fg='red',flashes=3,delay=75):
        pass
    def getName(self):                          return self.name # Essential.
    def getYScrollPosition (self):              return 0
    def see(self,i):                            pass
    def seeInsertPoint(self):                   pass
    def setFocus(self):                         pass
    def setYScrollPosition (self,i):            pass
    def tag_configure (self,colorName,**keys):  pass
    #@+node:ekr.20111113141805.10060: *3* btw.Indices
    #@+node:ekr.20070228074312.7: *4* btw.toPythonIndex
    def toPythonIndex (self,index):

        return g.toPythonIndex(self.s,index)
    #@+node:ekr.20090320055710.4: *4* btw.toPythonIndexRowCol
    def toPythonIndexRowCol(self,index):

        s = self.getAllText()
        i = self.toPythonIndex(index)
        row,col = g.convertPythonIndexToRowCol(s,i)
        return i,row,col
    #@+node:ekr.20111113141805.10058: *3* btw.Insert point & selection Range
    #@+node:ekr.20070228074312.20: *4* btw.getInsertPoint
    def getInsertPoint(self):

        i = self.ins
        if i is None:
            if self.virtualInsertPoint is None:
                i = 0
            else:
                i = self.virtualInsertPoint

        self.virtualInsertPoint = i

        # g.trace('BaseTextWrapper): i:',i,'virtual',self.virtualInsertPoint)
        return i
    #@+node:ekr.20070228074312.22: *4* btw.getSelectionRange
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

    #@+node:ekr.20070228074312.25: *4* btw.hasSelection
    def hasSelection (self):

        i,j = self.getSelectionRange()
        return i != j
    #@+node:ekr.20070228074312.35: *4* btw.setInsertPoint
    def setInsertPoint (self,pos,s=None):

        self.virtualInsertPoint = i = self.toPythonIndex(pos)
        self.ins = i
        self.sel = i,i
    #@+node:ekr.20070228074312.36: *4* btw.setSelectionRange
    def setSelectionRange (self,i,j,insert=None):

        i1, j1, insert1 = i,j,insert
        i,j = self.toPythonIndex(i),self.toPythonIndex(j)

        self.sel = i,j
        self.ins = j

        if insert is not None and insert in (i,j):
            ins = self.toPythonIndex(insert)
            if ins in (i,j):
                self.virtualInsertPoint = ins
    #@+node:ekr.20070228074312.31: *4* btw.selectAllText
    def selectAllText (self,insert=None):

        '''Select all text of the widget.'''

        self.setSelectionRange(0,'end',insert=insert)
    #@+node:ekr.20070228074312.5: *3* btw.oops
    def oops (self):

        g.pr('BaseTextWrapper oops:',self,g.callers(4),
            'must be overridden in subclass')
    #@+node:ekr.20111113141805.10057: *3* btw.Text
    #@+node:ekr.20070228074312.10: *4* btw.appendText
    def appendText (self,s):

        self.s = self.s + s
        self.ins = len(self.s)
        self.sel = self.ins,self.ins
    #@+node:ekr.20070228074312.13: *4* btw.delete
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
    #@+node:ekr.20070228074312.14: *4* btw.deleteTextSelection
    def deleteTextSelection (self):

        i,j = self.getSelectionRange()
        self.delete(i,j)
    #@+node:ekr.20070228074312.18: *4* btw.get
    def get(self,i,j=None):

        i = self.toPythonIndex(i)
        if j is None: j = i+ 1
        j = self.toPythonIndex(j)
        s = self.s[i:j]
        return g.toUnicode(s)
    #@+node:ekr.20070228074312.19: *4* btw.getAllText
    def getAllText (self):

        s = self.s
        return g.toUnicode(s)
    #@+node:ekr.20070228074312.21: *4* btw.getSelectedText
    def getSelectedText (self):

        i,j = self.sel
        s = self.s[i:j]
        return g.toUnicode(s)
    #@+node:ekr.20070228074312.26: *4* btw.insert
    def insert(self,i,s):

        i = self.toPythonIndex(i)
        s1 = s
        self.s = self.s[:i] + s1 + self.s[i:]
        i += len(s1)
        self.ins = i
        self.sel = i,i
    #@+node:ekr.20070228074312.28: *4* btw.replace (not used)
    # def replace (self,i,j,s):

        # self.delete(i,j)
        # self.insert(i,s)
    #@+node:ekr.20070228074312.32: *4* btw.setAllText
    def setAllText (self,s):

        self.s = s
        i = len(self.s)
        self.ins = i
        self.sel = i,i
    #@-others
#@-<< define class BaseTextWrapper >>
#@+<< define class StringTextWrapper >>
#@+node:ekr.20070228074228.1: ** << define class StringTextWrapper >>
class StringTextWrapper (BaseTextWrapper):
    '''A class that represents text as a Python string.'''
    #@+others
    #@+node:ekr.20070228074228.2: *3* stw.ctor
    def __init__ (self,c,name):
        '''Ctor for the StringTextWrapper class.'''
        # Init the base class
        BaseTextWrapper.__init__ (self,c=c,
            baseClassName='StringTextWrapper',name=name,widget=None)
        self.ins = 0
        self.sel = 0,0
        self.s = ''
        self.trace = False
    #@+node:ekr.20070228111853: *3* stw.setSelectionRange
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
#@-<< define class StringTextWrapper >>

#@+others
#@+node:ekr.20031218072017.3656: ** class LeoBody
class LeoBody:
    '''The base class for the body pane in Leo windows.'''
    #@+others
    #@+node:ekr.20031218072017.3657: *3* LeoBody.__init__
    def __init__ (self,frame,parentFrame):
        '''Ctor for LeoBody class.'''
        c = frame.c
        frame.body = self
        self.c = c
        self.editorWidgets = {} # keys are pane names, values are text widgets
        self.forceFullRecolorFlag = False
        self.frame = frame
        self.parentFrame = parentFrame # New in Leo 4.6.
        self.totalNumberOfEditors = 0
        # May be overridden in subclasses...
        self.wrapper = None # set in LeoQtBody.setWidget.
            # self.bodyCtrl is deprecated synonum for self.wrapper
            # It is implemented as a property.
            # self.widget no longer exists.
        self.numberOfEditors = 1
        self.pb = None # paned body widget.
        self.use_chapters = c.config.getBool('use_chapters')
        # Must be overridden in subclasses...
        self.colorizer = None
    #@+node:ekr.20031218072017.3677: *3* LeoBody.Coloring
    def forceFullRecolor (self):
        self.forceFullRecolorFlag = True

    def getColorizer(self):
        return self.colorizer

    def updateSyntaxColorer(self,p):
        return self.colorizer.updateSyntaxColorer(p.copy())

    def recolor(self,p,incremental=False):
        self.c.requestRecolorFlag = True
        self.c.incrementalRecolorFlag = incremental

    recolor_now = recolor
    #@+node:ekr.20140903103455.18574: *3* LeoBody.Defined in subclasses
    # Methods of this class call the following methods of subclasses (LeoQtBody)
    # Fail loudly if these methods are not defined.
    def oops (self):
        '''Say that a required method in a subclass is missing.'''
        g.trace("(LeoBody) %s should be overridden in a subclass", g.callers())

    def createEditorFrame (self,w):
        self.oops()

    def createTextWidget (self,parentFrame,p,name):
        self.oops()

    def getInsertPoint(self):
        self.oops()

    def packEditorLabelWidget (self,w):
        self.oops()
    #@+node:ekr.20060528100747: *3* LeoBody.Editors
    # This code uses self.pb, a paned body widget, created by tkBody.finishCreate.


    #@+node:ekr.20070424053629: *4* LeoBody.entries
    #@+node:ekr.20060528100747.1: *5* LeoBody.addEditor
    def addEditor (self,event=None):

        '''Add another editor to the body pane.'''

        c = self.c ; p = c.p

        self.totalNumberOfEditors += 1
        self.numberOfEditors += 1

        if self.numberOfEditors == 2:
            # Inject the ivars into the first editor.
            # Bug fix: Leo 4.4.8 rc1: The name of the last editor need not be '1'
            d = self.editorWidgets
            keys = list(d.keys())
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
        # Create the text wrapper.
        f = self.createEditorFrame(pane)
        wrapper = self.createTextWidget(f,name=name,p=p)
        wrapper.delete(0,'end')
        wrapper.insert('end',p.b)
        wrapper.see(0)
        c.k.completeAllBindingsForWidget(wrapper)
        self.recolorWidget(p,wrapper)
        self.editorWidgets[name] = wrapper
        for pane in panes:
            self.pb.configurepane(pane,size=minSize)
        self.pb.updatelayout()
        c.frame.body.wrapper = wrapper
        # Finish...
        self.updateInjectedIvars(wrapper,p)
        self.selectLabel(wrapper)
        self.selectEditor(wrapper)
        self.updateEditors()
        c.bodyWantsFocus()
    #@+node:ekr.20060528132829: *5* LeoBody.assignPositionToEditor
    def assignPositionToEditor (self,p):
        '''Called *only* from tree.select to select the present body editor.'''
        c = self.c
        w = c.frame.body.widget ### wrapper?
        self.updateInjectedIvars(w,p)
        self.selectLabel(w)
        # g.trace('===',id(w),w.leo_chapter.name,w.leo_p.h)
    #@+node:ekr.20060528170438: *5* LeoBody.cycleEditorFocus
    def cycleEditorFocus (self,event=None):

        '''Cycle keyboard focus between the body text editors.'''

        c = self.c
        d = self.editorWidgets
        w = c.frame.body.wrapper
        values = list(d.values())
        if len(values) > 1:
            i = values.index(w) + 1
            if i == len(values): i = 0
            w2 = list(d.values())[i]
            assert(w!=w2)
            self.selectEditor(w2)
            c.frame.body.wrapper = w2
    #@+node:ekr.20060528113806: *5* LeoBody.deleteEditor
    def deleteEditor (self,event=None):

        '''Delete the presently selected body text editor.'''

        c = self.c
        w = c.frame.body.wapper
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
        # c.frame.body.wrapper = w # Don't do this now?
        self.numberOfEditors -= 1
        self.selectEditor(w)
    #@+node:ekr.20070425180705: *5* LeoBody.findEditorForChapter
    def findEditorForChapter (self,chapter,p):
        '''Return an editor to be assigned to chapter.'''
        c = self.c
        d = self.editorWidgets
        values = list(d.values())
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
        # g.trace('***',id(self.wrapper),'no match',p.h)
        return c.frame.body.wrapper
    #@+node:ekr.20060530210057: *5* LeoBody.select/unselectLabel
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
    #@+node:ekr.20061017083312: *5* LeoBody.selectEditor & helpers
    selectEditorLockout = False

    def selectEditor(self,w):
        '''Select the editor give by w and node w.leo_p.'''
        #  Called whenever wrapper must be selected.
        c = self.c
        if self.selectEditorLockout:
            return
        if w and w == self.c.frame.body.widget:
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
    #@+node:ekr.20070423102603: *6* LeoBody.selectEditorHelper
    def selectEditorHelper (self,wrapper):
        '''Select the editor whose widget is given.'''
        c = self.c
        trace = False and not g.unitTesting
        if not wrapper.leo_p:
            g.trace('no wrapper.leo_p') 
            return
        if trace: g.trace('==1',id(wrapper),
            hasattr(wrapper,'leo_chapter') and wrapper.leo_chapter and wrapper.leo_chapter.name,
            hasattr(wrapper,'leo_p') and wrapper.leo_p and wrapper.leo_p.h)
        self.deactivateActiveEditor(wrapper)
        # The actual switch.
        c.frame.body.wrapper = wrapper
        wrapper.leo_active = True
        self.switchToChapter(wrapper)
        self.selectLabel(wrapper)
        if not self.ensurePositionExists(wrapper):
            g.trace('***** no position editor!')
            return
        if trace:
            g.trace('==2',id(wrapper),
                hasattr(wrapper,'leo_chapter') and wrapper.leo_chapter and wrapper.leo_chapter.name,
                hasattr(wrapper,'leo_p') and wrapper.leo_p and wrapper.leo_p.h)
        # g.trace('expanding ancestors of ',wrapper.leo_p.h,g.callers())
        p = wrapper.leo_p
        c.redraw(p)
        c.recolor()
        c.bodyWantsFocus()
    #@+node:ekr.20060528131618: *5* LeoBody.updateEditors
    # Called from addEditor and assignPositionToEditor

    def updateEditors (self):

        c = self.c ; p = c.p
        d = self.editorWidgets
        if len(list(d.keys())) < 2: return # There is only the main widget.

        for key in d:
            wrapper = d.get(key)
            v = wrapper.leo_v
            if v and v == p.v and wrapper != c.frame.body.wrapper:
                wrapper.delete(0,'end')
                wrapper.insert('end',p.b)
                # g.trace('update',wrapper,v)
                self.recolorWidget(p,wrapper)
        c.bodyWantsFocus()
    #@+node:ekr.20070424053629.1: *4* LeoBody.utils
    #@+node:ekr.20070422093128: *5* LeoBody.computeLabel
    def computeLabel (self,w):

        s = w.leo_label_s

        if hasattr(w,'leo_chapter') and w.leo_chapter:
            s = '%s: %s' % (w.leo_chapter.name,s)

        return s
    #@+node:ekr.20070422094710: *5* LeoBody.createChapterIvar
    def createChapterIvar (self,w):

        c = self.c
        cc = c.chapterController
        if not hasattr(w,'leo_chapter') or not w.leo_chapter:
            if cc and self.use_chapters:
                w.leo_chapter = cc.getSelectedChapter()
            else:
                w.leo_chapter = None
    #@+node:ekr.20070424084651: *5* LeoBody.ensurePositionExists
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
            # This *can* happen when selecting a deleted node.
            w.leo_p = c.p
            return False
    #@+node:ekr.20070424080640: *5* LeoBody.deactivateActiveEditor
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
    #@+node:ekr.20060530204135: *5* LeoBody.recolorWidget
    def recolorWidget (self,p,w):

        c = self.c
        old_wrapper = c.frame.body.wrapper
        # Save.
        c.frame.body.wrapper = w
        try:
            c.frame.body.colorizer.colorize(p,incremental=False,interruptable=False)
        finally:
            # Restore.
            c.frame.body.wrapper = old_wrapper
    #@+node:ekr.20070424084012: *5* LeoBody.switchToChapter
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
    #@+node:ekr.20070424092855: *5* LeoBody.updateInjectedIvars
    # Called from addEditor and assignPositionToEditor.

    def updateInjectedIvars (self,w,p):
        '''Inject updated ivars in w, a gui widget.'''
        c = self.c
        cc = c.chapterController
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
    #@+node:ekr.20031218072017.4018: *3* LeoBody.Text
    #@+node:ekr.20031218072017.4038: *4* LeoBody.get/setYScrollPosition (deleted)
    # def getYScrollPosition (self):

        # i = self.wrapper.getYScrollPosition()
        # return i

    # def setYScrollPosition (self,i):

        # self.wrapper.setYScrollPosition(i)
    #@+node:ekr.20031218072017.4030: *4* LeoBody.getInsertLines
    def getInsertLines (self):
        """
        Return before,after where:

        before is all the lines before the line containing the insert point.
        sel is the line containing the insert point.
        after is all the lines after the line containing the insert point.

        All lines end in a newline, except possibly the last line.
        """
        body = self
        w = body.wrapper
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
    #@+node:ekr.20031218072017.4031: *4* LeoBody.getSelectionAreas
    def getSelectionAreas (self):
        """
        Return before,sel,after where:

        before is the text before the selected text
        (or the text before the insert point if no selection)
        sel is the selected text (or "" if no selection)
        after is the text after the selected text
        (or the text after the insert point if no selection)
        """
        body = self
        w = body.wrapper
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
    #@+node:ekr.20031218072017.2377: *4* LeoBody.getSelectionLines
    def getSelectionLines (self):
        """
        Return before,sel,after where:

        before is the all lines before the selected text
        (or the text before the insert point if no selection)
        sel is the selected text (or "" if no selection)
        after is all lines after the selected text
        (or the text after the insert point if no selection)
        """
        if g.app.batchMode:
            return '','',''
        # At present, called only by c.getBodyLines.
        body = self
        w = body.wrapper
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
    #@+node:ekr.20031218072017.1329: *4* LeoBody.onBodyChanged
    # This is the only key handler for the body pane.
    def onBodyChanged (self,undoType,oldSel=None,oldText=None,oldYview=None):
        '''Update Leo after the body has been changed.'''
        trace = False and not g.unitTesting
        c = self.c
        body,w = self,self.wrapper
        p = c.p
        insert = w.getInsertPoint()
        ch = '' if insert==0 else w.get(insert-1)
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
        p.v.insertSpot = w.getInsertPoint()
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
        if not hasattr(p.v,"iconVal") or val != p.v.iconVal:
            p.v.iconVal = val
            redraw_flag = True
        if redraw_flag:
            c.redraw_after_icons_changed()
        #@-<< update icons if necessary >>
    #@+node:ekr.20031218072017.4037: *4* LeoBody.setSelectionAreas
    def setSelectionAreas (self,before,sel,after):

        """Replace the body text by before + sel + after and
        set the selection so that the sel text is selected."""

        body = self
        w = body.wrapper
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
    #@-others
#@+node:ekr.20031218072017.3678: ** class LeoFrame
class LeoFrame:

    """The base class for all Leo windows."""

    instances = 0

    #@+others
    #@+node:ekr.20031218072017.3679: *3*   LeoFrame.__init__
    def __init__ (self,c,gui):

        self.c = c
        self.gui = gui
        self.iconBarClass = NullIconBarClass
        self.statusLineClass = NullStatusLineClass
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

        v = leoNodes.VNode(context=c)
        p = leoNodes.Position(v)
        v.initHeadString("NewHeadline")
        # New in Leo 4.5: p.moveToRoot would be wrong: the node hasn't been linked yet.
        p._linkAsRoot(oldRoot=None)
        # c.setRootPosition() # New in 4.4.2.
    #@+node:ekr.20061109125528.1: *3* Must be defined in base class
    #@+node:ekr.20031218072017.3689: *4* initialRatios (LeoFrame)
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

        g.pr("LeoFrame oops:", g.callers(4), "should be overridden in subclass")
    #@+node:ekr.20031218072017.3692: *4* promptForSave (LeoFrame)
    def promptForSave (self):

        """Prompt the user to save changes.

        Return True if the user vetos the quit or save operation."""

        c = self.c
        theType = "quitting?" if g.app.quitting else "closing?"

        # See if we are in quick edit/save mode.
        root = c.rootPosition()
        quick_save = not c.mFileName and not root.next() and root.isAtEditNode()
        if quick_save:
            name = g.shortFileName(root.atEditNodeName())
        else:
            name = c.mFileName if c.mFileName else self.title
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
    #@+node:ekr.20070130115927.4: *4* Cut/Copy/Paste (LeoFrame)
    #@+node:ekr.20070130115927.5: *5* copyText (LeoFrame)
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
    #@+node:ekr.20070130115927.6: *5* LeoFrame.cutText
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
    #@+node:ekr.20070130115927.7: *5* LeoFrame.pasteText
    def pasteText (self,event=None,middleButton=False):
        '''
        Paste the clipboard into a widget.
        If middleButton is True, support x-windows middle-mouse-button easter-egg.
        '''
        trace = False and not g.unitTesting
        f = self ; c = f.c
        w = event and event.widget
        wname = (w and c.widget_name(w)) or '<no widget>'
        # if trace: g.trace(g.app.gui.isTextWidget(w),w)
        if not w or not g.app.gui.isTextWidget(w):
            if trace: g.trace('not a text widget',w)
            return
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
    #@+node:ekr.20031218072017.3980: *4* Edit Menu... (LeoFrame)
    #@+node:ekr.20031218072017.3981: *5* abortEditLabelCommand (LeoFrame)
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
            w = c.get_focus()
            w_name = g.app.gui.widget_name(w)
            if w_name.startswith('head'):
                c.endEditing()
                c.treeWantsFocus()
            else:
                # c.endEditing()
                c.bodyWantsFocus()
                k.setDefaultInputState()
                # Recolor the *body* text, **not** the headline.
                k.showStateAndMode(w=c.frame.body.wrapper)
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
    #@+node:ekr.20031218072017.3681: *4* Gui-dependent commands (LeoFrame)
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
    #@+node:ekr.20071027150501: *4* event handlers (LeoFrame)
    def OnBodyClick (self,event=None):
        pass

    def OnBodyRClick(self,event=None):
        pass
    #@+node:ekr.20031218072017.3688: *4* getTitle & setTitle (LeoFrame)
    def getTitle (self):
        return self.title

    def setTitle (self,title):
        # g.trace('**(LeoFrame)',title)
        self.title = title
    #@+node:ekr.20081005065934.3: *4* initAfterLoad  & initCompleteHint (LeoFrame)
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
    #@+node:ekr.20031218072017.3687: *4* setTabWidth (LeoFrame)
    def setTabWidth (self,w):

        # Subclasses may override this to affect drawing.
        self.tab_width = w
    #@-others
#@+node:ekr.20031218072017.3694: ** class LeoLog
class LeoLog:
    """The base class for the log pane in Leo windows."""
    #@+others
    #@+node:ekr.20031218072017.3695: *3*  LeoLog.ctor
    def __init__ (self,frame,parentFrame):
        '''Ctor for LeoLog class.'''
        self.frame = frame
        self.c = c = frame and frame.c or None
        self.enabled = True
        self.newlines = 0
        self.isNull = False
        # Official ivars...
        self.canvasCtrl = None # Set below. Same as self.canvasDict.get(self.tabName)
        self.logCtrl = None # Set below. Same as self.textDict.get(self.tabName)
        self.tabName = None # The name of the active tab.
        self.tabFrame = None # Same as self.frameDict.get(self.tabName)
        self.canvasDict = {} # Keys are page names.  Values are Tk.Canvas's.
        self.frameDict = {}  # Keys are page names. Values are Tk.Frames.
        self.logNumber = 0 # To create unique name fields for text widgets.
        self.newTabCount = 0 # Number of new tabs created.
        self.textDict = {}  # Keys are page names. Values are logCtrl's (text widgets).
    #@+node:ekr.20070302094848.1: *3* LeoLog.clearTab
    def clearTab (self,tabName,wrap='none'):

        self.selectTab(tabName,wrap=wrap)
        w = self.logCtrl
        if w: w.delete(0,'end')
    #@+node:ekr.20070302094848.2: *3* LeoLog.createTab
    def createTab (self,tabName,createText=True,widget=None,wrap='none'):

        if createText:
            w = self.createTextWidget(self.tabFrame)
            self.canvasDict [tabName] = None
            self.textDict [tabName] = w
        else:
            self.canvasDict [tabName] = None
            self.textDict [tabName] = None
            self.frameDict [tabName] = tabName # tabFrame


    #@+node:ekr.20140903143741.18550: *3* LeoLog.LeoLog.createTextWidget
    def createTextWidget(self,parentFrame):
        return None
    #@+node:ekr.20070302094848.4: *3* LeoLog.cycleTabFocus
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
    #@+node:ekr.20070302094848.5: *3* LeoLog.deleteTab
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
    #@+node:ekr.20140903143741.18549: *3* LeoLog.enable/disable
    def disable (self):
        self.enabled = False
        
    def enable (self,enabled=True):
        self.enabled = enabled
    #@+node:ekr.20070302094848.7: *3* LeoLog.getSelectedTab
    def getSelectedTab (self):

        return self.tabName
    #@+node:ekr.20070302094848.6: *3* LeoLog.hideTab
    def hideTab (self,tabName):

        self.selectTab('Log')
    #@+node:ekr.20070302094848.8: *3* LeoLog.lower/raiseTab
    def lowerTab (self,tabName):

        self.c.invalidateFocus()
        self.c.bodyWantsFocus()

    def raiseTab (self,tabName):

        self.c.invalidateFocus()
        self.c.bodyWantsFocus()
    #@+node:ekr.20111122080923.10184: *3* LeoLog.orderedTabNames
    def orderedTabNames (self,LeoLog):

        return list(self.frameDict.values())
    #@+node:ekr.20070302094848.9: *3* LeoLog.numberOfVisibleTabs
    def numberOfVisibleTabs (self):

        return len([val for val in list(self.frameDict.values()) if val != None])

    #@+node:ekr.20070302101304: *3* LeoLog.put & putnl
    # All output to the log stream eventually comes here.

    def put (self,s,color=None,tabName='Log',from_redirect=False):
        print (s)

    def putnl (self,tabName='Log'):
        pass # print ('')
    #@+node:ekr.20070302094848.10: *3* LeoLog.renameTab
    def renameTab (self,oldName,newName):
        pass
    #@+node:ekr.20070302094848.11: *3* LeoLog.selectTab
    def selectTab (self,tabName,createText=True,widget=None,wrap='none'):# widget unused.
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
    #@-others
#@+node:ekr.20031218072017.3704: ** class LeoTree
# This would be useful if we removed all the tree redirection routines.
# However, those routines are pretty ingrained into Leo...

class LeoTree:

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
    #@+node:ekr.20031218072017.3706: *3*  Must be defined in subclasses (LeoTree)
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
    #@+node:ekr.20040803072955.90: *4* head key handlers (LeoTree)
    #@+node:ekr.20040803072955.91: *5* onHeadChanged (LeoTree Not used: see nativeTree)
    # Tricky code: do not change without careful thought and testing.
    # Important: This code *is* used by the leoBridge module.
    # See also, nativeTree.onHeadChanged.
    def onHeadChanged (self,p,undoType='Typing',s=None,e=None): # e used in baseNativeTree.
        '''
        Officially change a headline.
        Set the old undo text to the previous revert point.
        '''
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
            g.trace('*** LeoTree',g.callers(5))
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
            # Fix bug 1280689: don't call the non-existent c.treeEditFocusHelper
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
        if trace: g.trace('LeoTree',p and p.h,g.callers(4))
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
        # N.B. These VNode methods are entitled to know about details of the leoTkinterTree class.

        #@+others
        #@+node:ekr.20040803072955.23: *6* OnHyperLinkControlClick
        def OnHyperLinkControlClick (self,event=None,c=c):
            """Callback injected into position class."""
            p = self
            if c and c.exists:
                try:
                    if not g.doHook("hypercclick1",c=c,p=p,v=p,event=event):
                        c.selectPosition(p)
                        c.redraw()
                        c.frame.body.wrapper.setInsertPoint(0)
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
    #@+node:ekr.20040803072955.128: *3* LeoTree.select & helpers
    tree_select_lockout = False

    def select (self,p,scroll=True):
        '''
        Select a node.
        Never redraws outline, but may change coloring of individual headlines.
        The scroll argument is used by the gui to suppress scrolling while dragging.
        '''
        if g.app.killed or self.tree_select_lockout:
            return None
        traceTime = False and not g.unitTesting
        if traceTime:
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
            delta_t = time.time()-t1
            if False or delta_t > 0.1:
                print('%20s: %2.3f sec' % ('tree-select:outer',delta_t))
        return val  # Don't put a return in a finally clause.
    #@+node:ekr.20070423101911: *4* selectHelper (LeoTree) & helpers
    def selectHelper (self,p,scroll):
        '''
        A helper function for leoTree.select.
        Do **not** "optimize" this by returning if p==c.p!
        '''
        traceTime = False and not g.unitTesting
        if traceTime:
            t1 = time.time()
        if not p:
            # This is not an error! We may be changing roots.
            # Do *not* test c.positionExists(p) here!
            return
        c = self.c
        if not c.frame.body.wrapper:
            return # Defensive.
        assert p.v.context == c
            # Selecting a foreign position will not be pretty.
        old_p = c.p
        call_event_handlers = p != old_p
        # Order is important...
        self.unselect_helper(old_p,p,traceTime)
        self.select_new_node(old_p,p,traceTime)
        self.change_current_position(old_p,p,traceTime)
        self.scroll_cursor(p,traceTime)
        self.set_status_line(p,traceTime)
        if call_event_handlers:
            g.doHook("select2",c=c,new_p=p,old_p=old_p,new_v=p,old_v=old_p)
            g.doHook("select3",c=c,new_p=p,old_p=old_p,new_v=p,old_v=old_p)
        if traceTime:
            delta_t = time.time()-t1
            if False or delta_t > 0.1:
                print('%20s: %2.3f sec' % ('tree-select:total',delta_t))
    #@+node:ekr.20140829172618.20682: *5* LeoTree.is_big_text
    def is_big_text(self,p):
        '''True if p.b is large and the text widgets supports big text buttons.'''
        c = self.c
        if 1:
            return False # Disable the big-text feature.
        else:
            w = c.frame.body and c.frame.body.widget
            return (
                w and hasattr(w,'leo_load_button') and
                len(p.b) > c.max_pre_loaded_body_chars)
    #@+node:ekr.20140831085423.18637: *5* LeoTree.is_qt_body
    def is_qt_body(self):
        '''Return True if the body widget is a QTextEdit.'''
        c = self.c
        return c.frame.body and c.frame.body.widget
            # c.frame.body.widget is a LeoQTextBrowser.
            # Note: c.frame.body.wrapper is a BaseTextWrapper.
    #@+node:ekr.20140829053801.18453: *5* 1. LeoTree.unselect_helper & helpers
    def unselect_helper(self,old_p,p,traceTime):
        '''Unselect the old node, calling the unselect hooks.'''
        if traceTime:
            t1 = time.time()
        c = self.c
        call_event_handlers = p != old_p
        if call_event_handlers:
            unselect = not g.doHook("unselect1",c=c,new_p=p,old_p=old_p,new_v=p,old_v=old_p)
        else:
            unselect = True
        if unselect and old_p != p:
            # Actually unselect the old node.
            self.endEditLabel() # sets editPosition = None
            self.stop_colorizer(old_p)
            self.remove_big_text_buttons(old_p)
        if call_event_handlers:
            g.doHook("unselect2",c=c,new_p=p,old_p=old_p,new_v=p,old_v=old_p)
        if traceTime:
            delta_t = time.time()-t1
            if False or delta_t > 0.1:
                print('%20s: %2.3f sec' % ('tree-select:unselect',delta_t))
    #@+node:ekr.20140829172618.18477: *6* LeoTree.remove_big_text_buttons
    def remove_big_text_buttons(self,old_p):
        '''Remove the load and paste buttons created for large text.'''
        c = self.c
        if self.is_qt_body():
            w = c.frame.body.widget
            if old_p and hasattr(w,'leo_big_text') and w.leo_big_text:
                s = w.leo_big_text
                w.leo_big_text = None
                if old_p and old_p.b != s:
                    g.trace('===== restoring big text',len(s),old_p.h)
                    old_p.b = s
                    if hasattr(c.frame.tree,'updateIcon'):
                        c.frame.tree.updateIcon(old_p,force=True)
            if hasattr(w,'leo_copy_button') and w.leo_copy_button:
                w.leo_copy_button.deleteLater()
                w.leo_copy_button = None
            if hasattr(w,'leo_load_button') and w.leo_load_button:
                w.leo_load_button.deleteLater()
                w.leo_load_button = None
    #@+node:ekr.20140829172618.18476: *6* LeoTree.stop_colorizer
    def stop_colorizer(self,old_p):
        '''Stop colorizing the present node.'''
        c = self.c
        colorizer = c.frame.body.colorizer
        if colorizer:
            if hasattr(colorizer,'kill'):
                colorizer.kill()
            if (hasattr(colorizer,'colorCacheFlag') and
                colorizer.colorCacheFlag and
                hasattr(colorizer,'write_colorizer_cache')
            ):
                colorizer.write_colorizer_cache(old_p)
    #@+node:ekr.20140829053801.18455: *5* 2. LeoTree.select_new_node & helper
    def select_new_node(self,old_p,p,traceTime):
        '''Select the new node, part 1.'''
        if traceTime:
            t1 = time.time()
        c = self.c
        call_event_handlers = p != old_p
        if call_event_handlers:
            select = not g.doHook("select1",c=c,new_p=p,old_p=old_p,new_v=p,old_v=old_p)
        else:
            select = True  
        if select:
            self.revertHeadline = p.h
            c.frame.setWrap(p)
            if self.is_big_text(p):
                self.set_not_loaded_text(p)
                self.add_big_text_buttons(old_p,p,traceTime)
            else:
                self.set_body_text_after_select(p,old_p,traceTime)
            c.NodeHistory.update(p) # Remember this position.
        if traceTime:
            delta_t = time.time()-t1
            if False or delta_t > 0.1:
                print('%20s: %2.3f sec' % ('tree-select:select1',delta_t))
    #@+node:ekr.20140829172618.18478: *6* LeoTree.add_big_text_buttons
    def add_big_text_buttons(self,old_p,p,traceTime):
        '''Add the load and copy buttons.'''
        from leo.core.leoQt import QtGui
        c = self.c
        if c.undoer.undoing:
            g.trace('undoing')
            return
        if self.is_qt_body() and not g.app.unitTesting:
            w = c.frame.body.widget.widget
            frame = w.parent() # A QWidget
            layout = frame.layout()
            s = p.b
            w.leo_copy_button = b1 = QtGui.QPushButton('Copy body to clipboard: %s' % (p.h))
            w.leo_load_button = b2 = QtGui.QPushButton('Load Text: %s' % (p.h))
            b1.setObjectName('big-text-copy-button')
            b2.setObjectName('big-text-load-button')
            self.add_load_button(layout,old_p,p,s,traceTime,w)
            self.add_copy_button(layout,s,w)
            layout.removeWidget(w)
                # Evenly space the buttons in the body pane.
    #@+node:ekr.20140829172618.19888: *7* add_load_button
    def add_load_button(self,layout,old_p,p,s,traceTime,w):
        '''Create a 'load' button in the body text area.'''
        def onClicked(arg,c=self.c,p=p.copy()):
            if c.positionExists(p):
                # Recreate the entire select code.
                self.set_body_text_after_select(p,old_p,traceTime)
                self.scroll_cursor(p,traceTime)
            layout.addWidget(w)
            layout.removeWidget(w.leo_copy_button)
            layout.removeWidget(w.leo_load_button)
            w.leo_copy_button.deleteLater()
            w.leo_load_button.deleteLater()
            w.leo_copy_button = None
            w.leo_load_button = None
            c.bodyWantsFocusNow()
            c.recolor_now()
                # Unlike set_body_text_after_select, we can call
                # c.recolor_now because the new node has been inited.
        w.leo_load_button.clicked.connect(onClicked)
        layout.addWidget(w.leo_load_button)
    #@+node:ekr.20140829172618.19890: *7* add_copy_button
    def add_copy_button(self,layout,s,w):
        '''Create a 'copy to clipboard' button in the body area.'''
        def onClicked(checked=False):
            g.app.gui.replaceClipboardWith(s)
        w.leo_copy_button.clicked.connect(onClicked)
        layout.addWidget(w.leo_copy_button)
    #@+node:ekr.20090608081524.6109: *6* LeoTree.set_body_text_after_select
    def set_body_text_after_select (self,p,old_p,traceTime):
        '''Set the text after selecting a node.'''
        trace = False and not g.unitTesting
        if traceTime: t1 = time.time()
        # Always do this.  Otherwise there can be problems with trailing newlines.
        c = self.c
        w = c.frame.body.wrapper
        s = p.v.b # Guaranteed to be unicode.
        old_s = w.getAllText()
        if p and p == old_p and s == old_s:
            if trace: g.trace('*pass',p.h,old_p.h)
        else:
            # w.setAllText destroys all color tags, so do a full recolor.
            if trace: g.trace('*reload',p.h,old_p and old_p.h)
            w.setAllText(s) # ***** Very slow
            if traceTime:
                delta_t = time.time()-t1
                if delta_t > 0.1: g.trace('part1: %2.3f sec' % (delta_t))
            # Part 2:
            if traceTime: t2 = time.time()
            # We can't call c.recolor_now here.
            colorizer = c.frame.body.colorizer
            if hasattr(colorizer,'setHighlighter'):
                if colorizer.setHighlighter(p):
                    self.frame.body.recolor(p)
            else:
                self.frame.body.recolor(p)
            if traceTime:
                delta_t = time.time()-t2
                tot_t = time.time()-t1
                if delta_t > 0.1: g.trace('part2: %2.3f sec' % (delta_t))
                if tot_t > 0.1:   g.trace('total: %2.3f sec' % (tot_t))
        # This is now done after c.p has been changed.
            # p.restoreCursorAndScroll()
    #@+node:ekr.20140829172618.18479: *6* LeoTree.set_not_loaded_text
    def set_not_loaded_text(self,p):
        '''Set the body text to a "not loaded" message.'''
        c = self.c
        if self.is_qt_body():
            w = c.frame.body.wrapper.widget
            wrapper = c.frame and c.frame.body and c.frame.body.wrapper
            s = p.b
            w.leo_big_text = p.b # Save the original text
            wrapper.setAllText("To load the body text, click the 'load' button.")
            assert p.b == s
                # There will be data loss if this assert fails.
    #@+node:ekr.20140829053801.18458: *5* 3. LeoTree.change_current_position
    def change_current_position(self,old_p,p,traceTime):
        '''Select the new node, part 2.'''
        if traceTime:
            t1 = time.time()
        c = self.c
        c.setCurrentPosition(p)
        c.frame.scanForTabWidth(p)
            #GS I believe this should also get into the select1 hook
        use_chapters = c.config.getBool('use_chapters')
        if use_chapters:
            cc = c.chapterController
            theChapter = cc and cc.getSelectedChapter()
            if theChapter:
                theChapter.p = p.copy()
        c.treeFocusHelper()
        c.undoer.onSelect(old_p,p)
        if traceTime:
            delta_t = time.time()-t1
            if False or delta_t > 0.1:
                print('%20s: %2.3f sec' % ('tree-select:select2',delta_t))
    #@+node:ekr.20140829053801.18459: *5* 4. LeoTree.scroll_cursor
    def scroll_cursor(self,p,traceTime):
        '''Scroll the cursor. It deserves separate timing stats.'''
        if traceTime:
            t1 = time.time()
        c = self.c
        if not self.is_big_text(p):
            p.restoreCursorAndScroll()
                # Was in setBodyTextAfterSelect
        if traceTime:
            delta_t = time.time()-t1
            if False or delta_t > 0.1:
                print('%20s: %2.3f sec' % ('tree-select:scroll',delta_t))
    #@+node:ekr.20140829053801.18460: *5* 5. LeoTree.set_status_line
    def set_status_line(self,p,traceTime):
        '''Update the status line.'''
        if traceTime:
            t1 = time.time()
        c = self.c
        c.frame.body.assignPositionToEditor(p)
            # New in Leo 4.4.1.
        c.frame.updateStatusLine()
            # New in Leo 4.4.1.
        c.frame.clearStatusLine()
        verbose = getattr(c, 'status_line_unl_mode', '') == 'canonical'
        c.frame.putStatusLine(p.get_UNL(with_proto=verbose, with_index=verbose))
        if traceTime:
            delta_t = time.time()-t1
            if False or delta_t > 0.1:
                print('%20s: %2.3f sec' % ('tree-select:status',delta_t))
    #@+node:ekr.20031218072017.3718: *3* oops
    def oops(self):

        g.pr("LeoTree oops:", g.callers(4), "should be overridden in subclass")
    #@-others
#@+node:ekr.20070317073627: ** class LeoTreeTab
class LeoTreeTab:

    '''A class representing a tabbed outline pane.'''

    #@+others
    #@+node:ekr.20070317073627.1: *3*  ctor (LeoTreeTab)
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

        g.pr("LeoTreeTree oops:", g.callers(4), "should be overridden in subclass")
    #@-others
#@+node:ekr.20031218072017.2191: ** class NullBody (LeoBody)
class NullBody (LeoBody):
    # pylint: disable=R0923
    # Interface not implemented.
    #@+others
    #@+node:ekr.20031218072017.2192: *3*  NullBody.__init__
    def __init__ (self,frame,parentFrame):
        '''Ctor for NullBody class.'''
        # g.trace('NullBody','frame',frame,g.callers())
        LeoBody.__init__ (self,frame,parentFrame)
            # Init the base class.
        self.insertPoint = 0
        self.selection = 0,0
        self.s = "" # The body text
        self.widget = None
        self.wrapper = wrapper = StringTextWrapper(c=self.c,name='body')
        self.editorWidgets['1'] = wrapper
        self.colorizer = NullColorizer(self.c)
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
    #@+node:ekr.20031218072017.2197: *3* NullBody: LeoBody interface
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
    def setFocus (self):                        pass
    #@-others
#@+node:ekr.20031218072017.2218: ** class NullColorizer
class NullColorizer:

    """A do-nothing colorer class"""

    #@+others
    #@+node:ekr.20031218072017.2219: *3* __init__ (NullColorizer)
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

    def showInvisibles(self): pass

    def updateSyntaxColorer (self,p): pass

    def useSyntaxColoring(self,p):
        return None
    #@-others
#@+node:ekr.20031218072017.2222: ** class NullFrame
class NullFrame (LeoFrame):

    """A null frame class for tests and batch execution."""

    #@+others
    #@+node:ekr.20040327105706: *3*  ctor (NullFrame)
    def __init__ (self,c,title,gui):
        '''Ctor for the NullFrame class.'''
        # g.trace('NullFrame')
        LeoFrame.__init__(self,c,gui)
            # Init the base class.
        assert self.c
        self.wrapper = None
        self.iconBar = NullIconBarClass(self.c,self)
        self.isNullFrame = True
        self.outerFrame = None
        self.statusLineClass = NullStatusLineClass
        self.title = title
        self.top = None # Always None.
        # Create the component objects.
        self.body = NullBody(frame=self,parentFrame=None)
        self.log  = NullLog (frame=self,parentFrame=None)
        self.menu = LeoMenu.NullMenu(frame=self)
        self.tree = NullTree(frame=self)
        # Default window position.
        self.w = 600
        self.h = 500
        self.x = 40
        self.y = 40
    #@+node:ekr.20041120073824: *3* destroySelf (NullFrame)
    def destroySelf (self):

        pass
    #@+node:ekr.20040327105706.2: *3* finishCreate (NullFrame)
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
    #@+node:ekr.20061109124129: *4* Gui-dependent commands (NullFrame)
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
#@+node:ekr.20070301164543: ** class NullIconBarClass
class NullIconBarClass:

    '''A class representing the singleton Icon bar'''

    #@+others
    #@+node:ekr.20070301164543.1: *3*  ctor (NullIconBarClass)
    def __init__ (self,c,parentFrame):

        self.c = c
        self.iconFrame = None
        self.parentFrame = parentFrame
        self.w = g.NullObject()
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
#@+node:ekr.20031218072017.2232: ** class NullLog (LeoLog)
class NullLog (LeoLog):
    # py--lint: disable=interface-not-implemented
    #@+others
    #@+node:ekr.20070302095500: *3* Birth
    #@+node:ekr.20041012083237: *4* NullLog.__init__
    def __init__ (self,frame=None,parentFrame=None):

        # Init the base class.
        LeoLog.__init__(self,frame,parentFrame)

        self.isNull = True
        self.logNumber = 0
        self.widget = self.createControl(parentFrame)
            # self.logCtrl is now a property of the base LeoLog class.
    #@+node:ekr.20120216123546.10951: *4* finishCreate (NullLog)
    def finishCreate(self):
        pass
    #@+node:ekr.20041012083237.1: *4* createControl
    def createControl (self,parentFrame):

        return self.createTextWidget(parentFrame)
    #@+node:ekr.20070302095121: *4* createTextWidget (NullLog)
    def createTextWidget (self,parentFrame):

        self.logNumber += 1
        c = self.c
        log = StringTextWrapper(c=c,name="log-%d" % self.logNumber)
        return log
    #@+node:ekr.20111119145033.10186: *3* isLogWidget (NullLog)
    def isLogWidget(self,w):
        return False
    #@+node:ekr.20041012083237.2: *3* oops
    def oops(self):

        g.trace("NullLog:", g.callers(4))
    #@+node:ekr.20041012083237.3: *3* put and putnl (NullLog)
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
    #@+node:ekr.20060124085830: *3* tabs (NullLog)
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
#@+node:ekr.20070302171509: ** class NullStatusLineClass
class NullStatusLineClass:

    '''A do-nothing status line.'''

    #@+others
    #@+node:ekr.20070302171509.2: *3*  NullStatusLineClass.ctor
    def __init__ (self,c,parentFrame):

        self.c = c
        self.enabled = False
        self.parentFrame = parentFrame
        self.textWidget = StringTextWrapper(c,name='status-line')

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
#@+node:ekr.20031218072017.2233: ** class NullTree
class NullTree (LeoTree):

    #@+others
    #@+node:ekr.20031218072017.2234: *3*  NullTree.__init__
    def __init__ (self,frame):

        LeoTree.__init__(self,frame) # Init the base class.

        assert(self.frame)

        self.editWidgetsDict = {} # Keys are tnodes, values are StringTextWidgets.
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
            # keys are vnodes, values are StringTextWidgets.
            w = d.get(key)
            g.pr('w',w,'v.h:',key.headString,'s:',repr(w.s))

    #@+node:ekr.20031218072017.2236: *3* Overrides
    #@+node:ekr.20070228163350.1: *4* Drawing & scrolling (NullTree)
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
    #@+node:ekr.20070228163350.2: *4* edit_widget (NullTree)
    def edit_widget (self,p):
        d = self.editWidgetsDict
        if not p.v:
            return None
        w = d.get(p.v)
        if not w:
            d[p.v] = w = StringTextWrapper(
                c=self.c,
                name='head-%d' % (1 + len(list(d.keys()))))
            w.setAllText(p.h)
        return w
    #@+node:ekr.20070228164730: *5* editLabel (NullTree)
    def editLabel (self,p,selectAll=False,selection=None):

        """Start editing p's headline."""

        self.endEditLabel()
        self.setEditPosition(p)
            # That is, self._editPosition = p
        if p:
            self.revertHeadline = p.h
                # New in 4.4b2: helps undo.
    #@+node:ekr.20070228160345: *5* setHeadline (NullTree)
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
#@+node:ekr.20140903025053.18631: ** class WrapperAPI class
class WrapperAPI(object):
    '''A class specifying the wrapper api used throughout Leo's core.'''
    def __init__ (self,c): pass
    def appendText(self,s): pass
    def clipboard_append(self,s): pass
    def clipboard_clear (self): pass
    def delete(self,i,j=None): pass
    def deleteTextSelection (self): pass
    def disable (self): pass
    def enable (self,enabled=True): pass
    def flashCharacter(self,i,bg='white',fg='red',flashes=3,delay=75): pass
    def get(self,i,j): return ''
    def getAllText(self): return ''
    def getInsertPoint(self): return 0
    def getSelectedText(self): return ''
    def getSelectionRange (self): return (0,0)
    def getYScrollPosition (self): return 0
    def hasSelection(self): return False
    def insert(self,i,s): pass
    def see(self,i): pass
    def seeInsertPoint (self): pass
    def selectAllText (self,insert=None): pass
    def setAllText (self,s): pass
    def setFocus(self): pass # Required: sets the focus to wrapper.widget.
    def setInsertPoint(self,pos,s=None): pass
    def setSelectionRange (self,i,j,insert=None): pass
    def setYScrollPosition (self,i): pass
    def tag_configure (self,colorName,**keys): pass
    def toPythonIndex (self,index): return 0
    def toPythonIndexRowCol(self,index): return (0,0,0)
#@-others
#@-leo
