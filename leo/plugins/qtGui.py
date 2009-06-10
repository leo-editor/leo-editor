# -*- coding: utf-8 -*-
#@+leo-ver=4-thin
#@+node:ekr.20081121105001.188:@thin qtGui.py
#@@first

'''qt gui plugin.'''

#@@language python
#@@tabwidth -4
#@@pagewidth 80

# Define these to suppress pylint warnings...
__timing = None # For timing stats.
__qh = None # For quick headlines.

# A switch telling whether to use qt_main.ui and qt_main.py.
useUI = False # True: use qt_main.ui. False: use DynamicWindow.createMainWindow.

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
import leo.core.leoPlugins as leoPlugins

import leo.plugins.baseNativeTree as baseNativeTree

import re
import string

import os
import re # For colorizer
import string
import sys
import types

try:
    # import PyQt4.Qt as Qt # Loads all modules of Qt.
    # import qt_main # Contains Ui_MainWindow class
    import PyQt4.QtCore as QtCore
    import PyQt4.QtGui as QtGui
except ImportError:
    QtCore = None
    print('\nqtGui.py: can not import Qt\n')
try:
    from PyQt4 import Qsci
except ImportError:
    QtCore = None
    print('\nqtGui.py: can not import scintilla for Qt')
    print('\nqtGui.py: qt-scintilla may be a separate package on your system')
    print('\nqtGui.py: e.g. "python-qscintilla2" or similar\n')

#@-node:ekr.20081121105001.189: << qt imports >>
#@nl
#@<< define text widget classes >>
#@+node:ekr.20081121105001.515: << define text widget classes >>
# Order matters when defining base classes.

#@<< define leoQtBaseTextWidget class >>
#@+node:ekr.20081121105001.516: << define leoQtBaseTextWidget class >>
class leoQtBaseTextWidget (leoFrame.baseTextWidget):

    #@    @+others
    #@+node:ekr.20081121105001.517: Birth
    #@+node:ekr.20081121105001.518:ctor (leoQtBaseTextWidget)
    def __init__ (self,widget,name='leoQtBaseTextWidget',c=None):

        self.widget = widget
        self.c = c or self.widget.c

        # g.trace('leoQtBaseTextWidget',widget,g.callers(5))

        # Init the base class.
        leoFrame.baseTextWidget.__init__(
            self,c,baseClassName='leoQtBaseTextWidget',
            name=name,
            widget=widget,
            highLevelInterface=True)

        # Init ivars.
        self.changingText = False # A lockout for onTextChanged.
        self.tags = {}
        self.configDict = {} # Keys are tags, values are colors (names or values).
        self.useScintilla = False # This is used!

        if not c: return # Can happen.

        # Hook up qt events.
        self.ev_filter = leoQtEventFilter(c,w=self,tag='body')
        self.widget.installEventFilter(self.ev_filter)

        self.widget.connect(self.widget,
            QtCore.SIGNAL("textChanged()"),self.onTextChanged)

        self.widget.connect(self.widget,
            QtCore.SIGNAL("cursorPositionChanged()"),self.onClick)

        self.injectIvars(c)
    #@-node:ekr.20081121105001.518:ctor (leoQtBaseTextWidget)
    #@+node:ekr.20081121105001.519:injectIvars
    def injectIvars (self,name='1',parentFrame=None):

        w = self ; p = self.c.currentPosition()

        if name == '1':
            w.leo_p = None # Will be set when the second editor is created.
        else:
            w.leo_p = p.copy()

        w.leo_active = True

        # New in Leo 4.4.4 final: inject the scrollbar items into the text widget.
        w.leo_bodyBar = None
        w.leo_bodyXBar = None
        w.leo_chapter = None
        w.leo_frame = None
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
    #@+node:ekr.20090320101733.13:toPythonIndex
    def toPythonIndex (self,index):

        w = self
        #g.trace('slow toPythonIndex', g.callers(5))

        if type(index) == type(99):
            return index
        elif index == '1.0':
            return 0
        elif index == 'end':
            return w.getLastPosition()
        else:
            # g.trace(repr(index))
            s = w.getAllText()
            data = index.split('.')
            if len(data) == 2:
                row,col = data
                row,col = int(row),int(col)
                i = g.convertRowColToPythonIndex(s,row-1,col)
                # g.trace(index,row,col,i,g.callers(6))
                return i
            else:
                g.trace('bad string index: %s' % index)
                return 0

    toGuiIndex = toPythonIndex
    #@-node:ekr.20090320101733.13:toPythonIndex
    #@+node:ekr.20090320101733.14:toPythonIndexToRowCol
    def toPythonIndexRowCol(self,index):
        """ Slow 'default' implementation """
        #g.trace('slow toPythonIndexRowCol', g.callers(5))
        w = self
        s = w.getAllText()
        i = w.toPythonIndex(index)
        row,col = g.convertPythonIndexToRowCol(s,i)
        return i,row,col
    #@-node:ekr.20090320101733.14:toPythonIndexToRowCol
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
    #@+node:ville.20090324170325.73:get
    def get(self,i,j=None):
        """ Slow implementation of get() - ok for QLineEdit """
        #g.trace('Slow get', g.callers(5))

        s = self.getAllText()
        i = self.toGuiIndex(i)

        if j is None: 
            j = i+1

        j = self.toGuiIndex(j)
        return s[i:j]
    #@-node:ville.20090324170325.73:get
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

        ### if i > j: i,j = j,i

        return self.setSelectionRangeHelper(i,j,insert)
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
    #@+node:ekr.20081208041503.499:onClick (qtText)
    def onClick(self,event=None):

        trace = False and not g.unitTesting

        c = self.c
        name = c.widget_name(self)

        if trace: g.trace(name,c.p.h,self)

        if name.startswith('body'):
            if hasattr(c.frame,'statusLine'):
                c.frame.statusLine.update()
    #@-node:ekr.20081208041503.499:onClick (qtText)
    #@+node:ekr.20081121105001.536:onTextChanged (qtText)
    def onTextChanged (self):

        '''Update Leo after the body has been changed.

        self.selecting is guaranteed to be True during
        the entire selection process.'''

        trace = False and not g.unitTesting
        verbose = False
        c = self.c ; p = c.p
        tree = c.frame.tree ; w = self

        # The linux events are different from xp events.
        if w.changingText and not sys.platform.startswith('linux'):
            if trace and verbose: g.trace('already changing')
            return
        if tree.tree_select_lockout:
            if trace and verbose: g.trace('selecting lockout')
            return
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

        if trace: g.trace('**',len(newText),p.h,'\n',g.callers(8))

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
        # This will be called by onBodyChanged.
        # c.frame.tree.updateIcon(p)

        if 1: # This works, and is probably better.
            # Set a hook for the colorer.
            colorer = c.frame.body.colorizer.highlighter.colorer
            colorer.initFlag = True
        else:
            # Allow incremental recoloring.
            c.incrementalRecolorFlag = True
            c.outerUpdate()
    #@nonl
    #@-node:ekr.20081121105001.536:onTextChanged (qtText)
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
    # These *are* used.

    def removeAllTags(self):
        s = self.getAllText()
        self.colorSelection(0,len(s),'black')

    def tag_names (self):
        return []
    #@+node:ekr.20081121105001.542:colorSelection
    def colorSelection (self,i,j,colorName):

        g.trace()

        w = self.widget
        if not colorName: return
        if g.unitTesting: return

    #@+at
    #     # Unlike Tk names, Qt names don't end in a digit.
    #     if colorName[-1].isdigit() and colorName[0] != '#':
    #         color = QtGui.QColor(colorName[:-1])
    #     else:
    #         color = QtGui.QColor(colorName)
    #@-at
    #@@c
        color = QtGui.QColor(leoColor.getColor(colorName, 'black'))
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

        g.trace(tag)

        val = self.configDict.get(tag)
        if val:
            self.colorSelection(x1,x2,val)
    #@-node:ekr.20081124102726.10:tag_add
    #@+node:ekr.20081124102726.11:tag_config & tag_configure
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
    #@-node:ekr.20081124102726.11:tag_config & tag_configure
    #@-node:ekr.20081121105001.541:Coloring (baseTextWidget)
    #@-node:ekr.20081121105001.538: May be overridden in subclasses
    #@+node:ekr.20081121105001.543: Must be overridden in subclasses
    # These methods avoid calls to setAllText.

    # Allow the base-class method for headlines.
    # def delete(self,i,j=None):              self.oops()
    # def insert(self,i,s):                   self.oops()

    def getAllText(self):                   self.oops()
    def getInsertPoint(self):               self.oops()
    def getSelectionRange(self,sort=True):  self.oops()
    def hasSelection(self):                 self.oops()
    def see(self,i):                        self.oops()
    def setAllText(self,s,insert=None):     self.oops()
    def setInsertPoint(self,i):             self.oops()
    #@-node:ekr.20081121105001.543: Must be overridden in subclasses
    #@-others
#@-node:ekr.20081121105001.516: << define leoQtBaseTextWidget class >>
#@nl
#@<< define leoQLineEditWidget class >>
#@+node:ekr.20081121105001.544: << define leoQLineEditWidget class >>
class leoQLineEditWidget (leoQtBaseTextWidget):

    #@    @+others
    #@+node:ekr.20081121105001.545:Birth
    #@+node:ekr.20081121105001.546:ctor
    def __init__ (self,widget,name,c=None):

        # Init the base class.
        leoQtBaseTextWidget.__init__(self,widget,name,c=c)

        self.baseClassName='leoQLineEditWidget'

        # g.trace('leoQLineEditWidget',id(widget),g.callers(5))

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
    #@nonl
    #@-node:ekr.20081121105001.556:setAllText
    #@+node:ekr.20081121105001.557:setInsertPoint
    def setInsertPoint(self,i):

        w = self.widget
        s = w.text()
        s = g.app.gui.toUnicode(s)
        i = max(0,min(i,len(s)))
        w.setCursorPosition(i)
    #@-node:ekr.20081121105001.557:setInsertPoint
    #@+node:ekr.20081121105001.558:setSelectionRangeHelper (leoQLineEdit)
    def setSelectionRangeHelper(self,i,j,insert):

        w = self.widget
        # g.trace(i,j,insert,w)
        if i > j: i,j = j,i
        s = w.text()
        s = g.app.gui.toUnicode(s)
        n = len(s)
        i = max(0,min(i,n))
        j = max(0,min(j,n))
        insert = max(0,min(insert,n))
        if i == j:
            w.setCursorPosition(i)
        else:
            length = j-i
            if insert < j:
                w.setSelection(j,-length)
            else:
                w.setSelection(i,length)
    #@nonl
    #@-node:ekr.20081121105001.558:setSelectionRangeHelper (leoQLineEdit)
    #@-node:ekr.20081121105001.550:Widget-specific overrides (QLineEdit)
    #@-others
#@-node:ekr.20081121105001.544: << define leoQLineEditWidget class >>
#@nl
#@<< define leoQTextEditWidget class >>
#@+node:ekr.20081121105001.572: << define leoQTextEditWidget class >>
class leoQTextEditWidget (leoQtBaseTextWidget):

    #@    @+others
    #@+node:ekr.20081121105001.573:Birth
    #@+node:ekr.20081121105001.574:ctor
    def __init__ (self,widget,name,c=None):

        # widget is a QTextEdit.
        # g.trace('leoQTextEditWidget',widget)

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

        # tab stop in pixels - no config for this (yet)        
        w.setTabStopWidth(24)


    #@-node:ekr.20081121105001.577:setConfig
    #@-node:ekr.20081121105001.573:Birth
    #@+node:ekr.20081121105001.578:Widget-specific overrides (QTextEdit)
    #@+node:ekr.20090205153624.11:delete (avoid call to setAllText)
    def delete(self,i,j=None):

        trace = False and not g.unitTesting
        c,w = self.c,self.widget
        colorer = c.frame.body.colorizer.highlighter.colorer
        n = colorer.recolorCount

        i = self.toGuiIndex(i)
        if j is None: j = i+1
        j = self.toGuiIndex(j)

        # Set a hook for the colorer.
        colorer.initFlag = True

        sb = w.verticalScrollBar()
        pos = sb.sliderPosition()
        cursor = w.textCursor()
        cursor.setPosition(i)
        moveCount = abs(j-i)
        cursor.movePosition(cursor.Right,cursor.KeepAnchor,moveCount)
        cursor.removeSelectedText()
        sb.setSliderPosition(pos)

        if trace:
            g.trace('%s calls to recolor' % (
                colorer.recolorCount-n))
    #@-node:ekr.20090205153624.11:delete (avoid call to setAllText)
    #@+node:ekr.20081121105001.579:flashCharacter (leoQTextEditWidget)
    def flashCharacter(self,i,bg='white',fg='red',flashes=3,delay=75):

        # numbered color names don't work in Ubuntu 8.10, so...
        if bg[-1].isdigit() and bg[0] != '#':
            bg = bg[:-1]
        if fg[-1].isdigit() and fg[0] != '#':
            fg = fg[:-1]

        # This might causes problems during unit tests.
        # The selection point isn't restored in time.
        if g.app.unitTesting: return

        w = self.widget # A QTextEdit.
        e = QtGui.QTextCursor

        def after(func):
            QtCore.QTimer.singleShot(delay,func)

        def addFlashCallback(self=self,w=w):
            n,i = self.flashCount,self.flashIndex

            cursor = w.textCursor() # Must be the widget's cursor.
            cursor.setPosition(i)
            cursor.movePosition(e.Right,e.KeepAnchor,1)

            extra = w.ExtraSelection()
            extra.cursor = cursor
            if self.flashBg: extra.format.setBackground(QtGui.QColor(self.flashBg))
            if self.flashFg: extra.format.setForeground(QtGui.QColor(self.flashFg))
            self.extraSelList = [extra] # keep the reference.
            w.setExtraSelections(self.extraSelList)

            self.flashCount -= 1
            after(removeFlashCallback)

        def removeFlashCallback(self=self,w=w):
            w.setExtraSelections([])
            if self.flashCount > 0:
                after(addFlashCallback)
            else:
                w.setFocus()

        # g.trace(flashes,fg,bg)
        self.flashCount = flashes
        self.flashIndex = i
        self.flashBg = g.choose(bg.lower()=='same',None,bg)
        self.flashFg = g.choose(fg.lower()=='same',None,fg)

        addFlashCallback()
    #@-node:ekr.20081121105001.579:flashCharacter (leoQTextEditWidget)
    #@+node:ekr.20081121105001.580:getAllText (leoQTextEditWidget)
    def getAllText(self):

        #g.trace("getAllText", g.callers(5))
        w = self.widget
        s = unicode(w.toPlainText())

        # Doesn't work: gets only the line containing the cursor.
        # s = unicode(w.textCursor().block().text())

        # g.trace(repr(s))
        return s
    #@nonl
    #@-node:ekr.20081121105001.580:getAllText (leoQTextEditWidget)
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
    #@+node:ekr.20090531084925.3773:scrolling (QTextEdit)
    #@+node:ekr.20090531084925.3775:indexIsVisible and linesPerPage
    # This is not used if linesPerPage exists.
    def indexIsVisible (self,i):
        return False

    def linesPerPage (self):

        '''Return the number of lines presently visible.'''

        w = self.widget
        h = w.size().height()
        lineSpacing = w.fontMetrics().lineSpacing()
        n = h/lineSpacing
        # g.trace(n,h,lineSpacing)
        return n
    #@-node:ekr.20090531084925.3775:indexIsVisible and linesPerPage
    #@+node:ekr.20090531084925.3776:scrollDelegate (QTextEdit)
    def scrollDelegate(self,kind):

        '''Scroll a QTextEdit up or down one page.
        direction is in ('down-line','down-page','up-line','up-page')'''

        c = self.c ; w = self.widget
        vScroll = w.verticalScrollBar()
        h = w.size().height()
        lineSpacing = w.fontMetrics().lineSpacing()
        n = h/lineSpacing
        n = max(2,n-3)
        if   kind == 'down-half-page': delta = n/2
        elif kind == 'down-line':      delta = 1
        elif kind == 'down-page':      delta = n
        elif kind == 'up-half-page':   delta = -n/2
        elif kind == 'up-line':        delta = -1
        elif kind == 'up-page':        delta = -n
        else:
            delta = 0 ; g.trace('bad kind:',kind)
        val = vScroll.value()
        # g.trace(kind,n,h,lineSpacing,delta,val)
        vScroll.setValue(val+(delta*lineSpacing))
        c.bodyWantsFocus()
    #@-node:ekr.20090531084925.3776:scrollDelegate (QTextEdit)
    #@-node:ekr.20090531084925.3773:scrolling (QTextEdit)
    #@+node:ekr.20090205153624.12:insert (avoid call to setAllText)
    def insert(self,i,s):

        trace = False and not g.unitTesting
        c,w = self.c,self.widget
        colorer = c.frame.body.colorizer.highlighter.colorer
        n = colorer.recolorCount

        # Set a hook for the colorer.
        colorer.initFlag = True

        i = self.toGuiIndex(i)

        sb = w.verticalScrollBar()
        pos = sb.sliderPosition()
        cursor = w.textCursor()
        cursor.setPosition(i)
        cursor.insertText(s) # This cause an incremental call to recolor.
        sb.setSliderPosition(pos)

        if trace:
            g.trace('%s calls to recolor' % (
                colorer.recolorCount-n))
    #@-node:ekr.20090205153624.12:insert (avoid call to setAllText)
    #@+node:ekr.20081121105001.585:see
    def see(self,i):

        self.widget.ensureCursorVisible()
    #@nonl
    #@-node:ekr.20081121105001.585:see
    #@+node:ekr.20081121105001.586:seeInsertPoint
    def seeInsertPoint (self):

        self.widget.ensureCursorVisible()
    #@-node:ekr.20081121105001.586:seeInsertPoint
    #@+node:ekr.20081121105001.587:setAllText (leoQTextEditWidget)
    def setAllText(self,s,insert=None):

        '''Set the text of the widget.

        If insert is None, the insert point, selection range and scrollbars are initied.
        Otherwise, the scrollbars are preserved.'''

        trace = False and not g.unitTesting
        verbose = False
        c,w = self.c,self.widget
        colorizer = c.frame.body.colorizer
        highlighter = colorizer.highlighter
        colorer = highlighter.colorer

        # Set a hook for the colorer.
        colorer.initFlag = True

        sb = w.verticalScrollBar()
        if insert is None: i,pos = 0,0
        else: i,pos = insert,sb.sliderPosition()

        if trace: g.trace(id(w),len(s),c.p.h)
        if trace and verbose: t1 = g.getTime()
        try:
            self.changingText = True
            w.setPlainText(s)
        finally:
            self.changingText = False
        if trace and verbose: g.trace(g.timeSince(t1))

        self.setSelectionRange(i,i,insert=i)
        sb.setSliderPosition(pos)
    #@nonl
    #@-node:ekr.20081121105001.587:setAllText (leoQTextEditWidget)
    #@+node:ekr.20081121105001.588:setInsertPoint
    def setInsertPoint(self,i):

        w = self.widget

        s = w.toPlainText()
        i = max(0,min(i,len(s)))
        cursor = w.textCursor()

        # block = cursor.block()
        # i = max(0,min(i,block.length()))

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

        # g.trace('pos',pos)

        w = self.widget
        sb = w.verticalScrollBar()
        if pos is None: pos = 0
        elif type(pos) == types.TupleType:
            pos = pos[0]
        sb.setSliderPosition(pos)
    #@-node:ekr.20081121105001.591:setYScrollPosition
    #@+node:ville.20090321082712.1: PythonIndex
    #@+node:ville.20090321082712.2:toPythonIndex
    def toPythonIndex (self,index):

        w = self
        te = self.widget

        if type(index) == type(99):
            return index
        elif index == '1.0':
            return 0
        elif index == 'end':
            return w.getLastPosition()
        else:
            # g.trace(repr(index))
            #s = w.getAllText()
            doc = te.document()
            data = index.split('.')
            if len(data) == 2:
                row,col = data
                row,col = int(row),int(col)
                bl = doc.findBlockByNumber(row-1)
                return bl.position() + col


                #i = g.convertRowColToPythonIndex(s,row-1,col)

                # g.trace(index,row,col,i,g.callers(6))
                #return i
            else:
                g.trace('bad string index: %s' % index)
                return 0

    toGuiIndex = toPythonIndex
    #@-node:ville.20090321082712.2:toPythonIndex
    #@+node:ville.20090321082712.3:toPythonIndexToRowCol (leoQTextEditWidget)
    def toPythonIndexRowCol(self,index):
        #print "use idx",index

        w = self 

        if index == '1.0':
            return 0, 0, 0
        if index == 'end':
            index = w.getLastPosition()

        te = self.widget
        #print te
        doc = te.document()
        i = w.toPythonIndex(index)
        bl = doc.findBlock(i)
        row = bl.blockNumber()
        col = i - bl.position()

        #s = w.getAllText()
        #i = w.toPythonIndex(index)
        #row,col = g.convertPythonIndexToRowCol(s,i)
        #print "idx",i,row,col
        return i,row,col
    #@-node:ville.20090321082712.3:toPythonIndexToRowCol (leoQTextEditWidget)
    #@-node:ville.20090321082712.1: PythonIndex
    #@+node:ville.20090324170325.63:get
    def get(self,i,j=None):
        i = self.toGuiIndex(i)
        if j is None: 
            j = i+1
        else:
            j = self.toGuiIndex(j)
        te = self.widget
        doc = te.document()
        bl = doc.findBlock(i)
        #row = bl.blockNumber()
        #col = index - bl.position()

        # common case, e.g. one character    
        if bl.contains(j):
            s = unicode(bl.text())
            offset = i - bl.position()

            ret = s[ offset : offset + (j-i)]
            #print "fastget",ret
            return ret

        # the next implementation is much slower, but will have to do        

        #g.trace('Slow get()', g.callers(5))
        s = self.getAllText()
        i = self.toGuiIndex(i)

        j = self.toGuiIndex(j)
        return s[i:j]
    #@-node:ville.20090324170325.63:get
    #@-node:ekr.20081121105001.578:Widget-specific overrides (QTextEdit)
    #@-others
#@-node:ekr.20081121105001.572: << define leoQTextEditWidget class >>
#@nl

# Define all other text classes, in any order.

#@+others
#@+node:ekr.20081121105001.593:class findTextWrapper
class findTextWrapper (leoQLineEditWidget):

    '''A class representing the find/change edit widgets.'''

    pass
#@-node:ekr.20081121105001.593:class findTextWrapper
#@+node:ekr.20081121105001.559:class leoQScintilla
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
#@-node:ekr.20081121105001.559:class leoQScintilla
#@+node:ekr.20081121105001.592:class leoQtHeadlineWidget
class leoQtHeadlineWidget (leoQtBaseTextWidget):
    '''A wrapper class for QLineEdit widgets in QTreeWidget's.

    This wrapper must appear to be a leoFrame.baseTextWidget to Leo's core.
    '''

    #@    @+others
    #@+node:ekr.20090603073641.3841:Birth
    def __init__ (self,c,item,name,widget):

        # g.trace('leoQtHeadlineWidget',item,widget)

        # Init the base class.
        leoQtBaseTextWidget.__init__(self,widget,name,c)
        self.item=item

    def __repr__ (self):
        return 'leoQtHeadlineWidget: %s' % id(self)
    #@-node:ekr.20090603073641.3841:Birth
    #@+node:ekr.20090603073641.3851:Widget-specific overrides (leoQtHeadlineWidget)
    # These are safe versions of QLineEdit methods.
    #@+node:ekr.20090603073641.3861:check
    def check (self):

        '''Return True if the tree item exists and it's edit widget exists.'''

        trace = False and not g.unitTesting
        tree = self.c.frame.tree
        e = tree.treeWidget.itemWidget(self.item,0)
        valid = tree.isValidItem(self.item)
        result = valid and e == self.widget
        if trace: g.trace('result %s self.widget %s itemWidget %s' % (
            result,self.widget,e))

        return result
    #@nonl
    #@-node:ekr.20090603073641.3861:check
    #@+node:ekr.20090603073641.3852:getAllText
    def getAllText(self):

        if self.check():
            w = self.widget
            s = w.text()
            return g.app.gui.toUnicode(s)
        else:
            return ''
    #@nonl
    #@-node:ekr.20090603073641.3852:getAllText
    #@+node:ekr.20090603073641.3853:getInsertPoint
    def getInsertPoint(self):

        if self.check():
            i = self.widget.cursorPosition()
            return i
        else:
            return 0
    #@-node:ekr.20090603073641.3853:getInsertPoint
    #@+node:ekr.20090603073641.3854:getSelectionRange
    def getSelectionRange(self,sort=True):

        w = self.widget

        if self.check():
            if w.hasSelectedText():
                i = w.selectionStart()
                s = w.selectedText()
                s = g.app.gui.toUnicode(s)
                j = i + len(s)
            else:
                i = j = w.cursorPosition()
            return i,j
        else:
            return 0,0
    #@-node:ekr.20090603073641.3854:getSelectionRange
    #@+node:ekr.20090603073641.3855:hasSelection
    def hasSelection(self):

        if self.check():
            return self.widget.hasSelection()
        else:
            return False
    #@-node:ekr.20090603073641.3855:hasSelection
    #@+node:ekr.20090603073641.3856:see & seeInsertPoint
    def see(self,i):
        pass

    def seeInsertPoint (self):
        pass
    #@-node:ekr.20090603073641.3856:see & seeInsertPoint
    #@+node:ekr.20090603073641.3857:setAllText
    def setAllText(self,s,insert=None):

        if not self.check(): return

        w = self.widget
        i = g.choose(insert is None,0,insert)
        w.setText(s)
        if insert is not None:
            self.setSelectionRange(i,i,insert=i)
    #@-node:ekr.20090603073641.3857:setAllText
    #@+node:ekr.20090603073641.3862:setFocus
    def setFocus (self):

        if self.check():
            g.app.gui.set_focus(self.c,self.widget)
    #@-node:ekr.20090603073641.3862:setFocus
    #@+node:ekr.20090603073641.3858:setInsertPoint
    def setInsertPoint(self,i):

        if not self.check(): return

        w = self.widget
        s = w.text()
        s = g.app.gui.toUnicode(s)
        i = max(0,min(i,len(s)))
        w.setCursorPosition(i)
    #@-node:ekr.20090603073641.3858:setInsertPoint
    #@+node:ekr.20090603073641.3859:setSelectionRangeHelper (leoQLineEdit)
    def setSelectionRangeHelper(self,i,j,insert):

        if not self.check(): return
        w = self.widget
        # g.trace(i,j,insert,w)
        if i > j: i,j = j,i
        s = w.text()
        s = g.app.gui.toUnicode(s)
        n = len(s)
        i = max(0,min(i,n))
        j = max(0,min(j,n))
        insert = max(0,min(insert,n))
        if i == j:
            w.setCursorPosition(i)
        else:
            length = j-i
            if insert < j:
                w.setSelection(j,-length)
            else:
                w.setSelection(i,length)
    #@nonl
    #@-node:ekr.20090603073641.3859:setSelectionRangeHelper (leoQLineEdit)
    #@-node:ekr.20090603073641.3851:Widget-specific overrides (leoQtHeadlineWidget)
    #@-others
#@nonl
#@-node:ekr.20081121105001.592:class leoQtHeadlineWidget
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
#@-others
#@nonl
#@-node:ekr.20081121105001.515: << define text widget classes >>
#@nl

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
        def qtPdb(message=''):
            if message: print message
            import pdb
            if not g.app.useIpython:
                QtCore.pyqtRemoveInputHook()
            pdb.set_trace()
        g.pdb = qtPdb

        # if False: # This will be done, if at all, in leoQtBody.
            # def qtHandleDefaultChar(self,event,stroke):
                # # This is an error.
                # g.trace(stroke,g.callers())
                # return False
            # if safe_mode: # Override handleDefaultChar method.
                # h = leoKeys.keyHandlerClass
                # g.funcToMethod(qtHandleDefaultChar,h,"handleDefaultChar")

        g.app.gui.finishCreate()
        g.plugin_signon(__name__)
        return True
#@-node:ekr.20081121105001.191:init
#@-node:ekr.20081121105001.190: Module level
#@+node:ekr.20081121105001.194:Frame and component classes...
#@+node:ekr.20081121105001.200:class  DynamicWindow (QtGui.QMainWindow)
from PyQt4 import uic

class DynamicWindow(QtGui.QMainWindow):

    '''A class representing all parts of the main Qt window
    as created by Designer.

    c.frame.top is a DynamciWindow object.

    All leoQtX classes use the ivars of this Window class to
    support operations requested by Leo's core.
    '''

    #@    @+others
    #@+node:ekr.20081121105001.201: ctor (DynamicWindow)
    # Called from leoQtFrame.finishCreate.

    def __init__(self,c,parent=None):

        '''Create Leo's main window, c.frame.top'''

        self.c = c ; top = c.frame.top
        # print('DynamicWindow.__init__ %s' % c)

        # Init the base class.
        ui_file_name = c.config.getString('qt_ui_file_name')
        if not ui_file_name:
            ui_file_name = 'qt_main.ui'

        ui_description_file = g.app.loadDir + "/../plugins/" + ui_file_name
        # g.pr('DynamicWindw.__init__,ui_description_file)
        assert g.os_path_exists(ui_description_file)

        QtGui.QMainWindow.__init__(self,parent)

        if useUI:  
            self.ui = uic.loadUi(ui_description_file, self)
        else:
            self.createMainWindow()

        self.iconBar = self.addToolBar("IconBar")
        self.menubar = self.menuBar()
        self.statusBar = QtGui.QStatusBar()
        self.setStatusBar(self.statusBar)

        orientation = c.config.getString('initial_split_orientation')
        self.setSplitDirection(orientation)
        self.setStyleSheets()
    #@-node:ekr.20081121105001.201: ctor (DynamicWindow)
    #@+node:ekr.20081121105001.202:closeEvent (DynanicWindow)
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
    #@-node:ekr.20081121105001.202:closeEvent (DynanicWindow)
    #@+node:ekr.20090423070717.14:createMainWindow & helpers
    # Called instead of uic.loadUi(ui_description_file, self)

    def createMainWindow (self):

        '''Create the component ivars of the main window.

        Copied/adapted from qt_main.py'''

        MainWindow = self
        self.ui = self

        self.setMainWindowOptions()
        self.createCentralWidget()
        self.createMainLayout(self.centralwidget)
            # Creates .verticalLayout, .splitter and .splitter_2.
        self.createOutlinePane(self.splitter)
        self.createLogPane(self.splitter)
        self.createBodyPane(self.splitter_2)
        self.createMiniBuffer(self.centralwidget)
        self.createMenuBar()
        self.createStatusBar(MainWindow)

        # Signals
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
    #@+node:ekr.20090426183711.10:top-level
    #@+node:ekr.20090424085523.43:createBodyPane
    def createBodyPane (self,parent):

        # Create widgets.
        bodyFrame = self.createFrame(parent,'bodyFrame')
        innerFrame = self.createFrame(bodyFrame,'innerBodyFrame',
            hPolicy=QtGui.QSizePolicy.Expanding)
        sw = self.createStackedWidget(innerFrame,'bodyStackedWidget')
        page2 = QtGui.QWidget()
        self.setName(page2,'bodyPage2')
        body = self.createText(page2,'richTextEdit')

        # Pack.
        vLayout = self.createVLayout(page2,'bodyVLayout',spacing=6)
        grid = self.createGrid(bodyFrame,'bodyGrid')
        innerGrid = self.createGrid(innerFrame,'bodyInnerGrid')
        vLayout.addWidget(body)
        sw.addWidget(page2)
        innerGrid.addWidget(sw, 0, 0, 1, 1)
        grid.addWidget(innerFrame, 0, 0, 1, 1)
        self.verticalLayout.addWidget(parent)

        # Official ivars
        self.stackedWidget = sw # used by leoQtBody
        self.richTextEdit = body
        self.leo_body_frame = bodyFrame
        self.leo_body_inner_frame = innerFrame
        # self.leo_body_grid = grid
        # self.grid = innerGrid
        # self.page_2 = page2
        # self.verticalBodyLayout= vLayout
    #@-node:ekr.20090424085523.43:createBodyPane
    #@+node:ekr.20090425072841.12:createCentralWidget
    def createCentralWidget (self):

        MainWindow = self

        w = QtGui.QWidget(MainWindow)
        w.setObjectName("centralwidget")

        MainWindow.setCentralWidget(w)

        # Official ivars.
        self.centralwidget = w
    #@-node:ekr.20090425072841.12:createCentralWidget
    #@+node:ekr.20090424085523.42:createLogPane
    def createLogPane (self,parent):

        # Create widgets.
        logFrame = self.createFrame(parent,'logFrame',
            vPolicy = QtGui.QSizePolicy.Minimum)
        innerFrame = self.createFrame(logFrame,'logInnerFrame',
            hPolicy=QtGui.QSizePolicy.Preferred,
            vPolicy=QtGui.QSizePolicy.Expanding)
        tabWidget = self.createTabWidget(innerFrame,'logTabWidget')

        # Pack.
        innerGrid = self.createGrid(innerFrame,'logInnerGrid')
        innerGrid.addWidget(tabWidget, 0, 0, 1, 1)
        outerGrid = self.createGrid(logFrame,'logGrid')
        outerGrid.addWidget(innerFrame, 0, 0, 1, 1)

        findTab = QtGui.QWidget()
        findTab.setObjectName('findTab')
        tabWidget.addTab(findTab,'Find')
        self.createFindTab(findTab)

        spellTab = QtGui.QWidget()
        spellTab.setObjectName('spellTab')
        tabWidget.addTab(spellTab,'Spell')
        self.createSpellTab(spellTab)

        tabWidget.setCurrentIndex(1)

        # Official ivars
        self.tabWidget = tabWidget # Used by leoQtLog.
        # self.leo_log_frame = logFrame
        # self.leo_log_grid = outerGrid
        # self.findTab = findTab
        # self.spellTab = spellTab
        # self.leo_log_inner_frame = innerFrame
        # self.leo_log_inner_grid = innerGrid
    #@-node:ekr.20090424085523.42:createLogPane
    #@+node:ekr.20090424085523.41:createMainLayout
    def createMainLayout (self,parent):

        vLayout = self.createVLayout(parent,'mainVLayout',margin=3)

        splitter2 = QtGui.QSplitter(parent)
        splitter2.setOrientation(QtCore.Qt.Vertical)
        splitter2.setObjectName("splitter_2")

        splitter = QtGui.QSplitter(splitter2)
        splitter.setOrientation(QtCore.Qt.Horizontal)
        splitter.setObjectName("splitter")

        self.setSizePolicy(splitter)
        vLayout.addWidget(splitter2)

        # Official ivars
        self.verticalLayout = vLayout
        self.splitter = splitter
        self.splitter_2 = splitter2
    #@-node:ekr.20090424085523.41:createMainLayout
    #@+node:ekr.20090424085523.45:createMenuBar
    def createMenuBar (self):

        MainWindow = self

        w = QtGui.QMenuBar(MainWindow)
        w.setGeometry(QtCore.QRect(0, 0, 957, 22))
        w.setObjectName("menubar")

        MainWindow.setMenuBar(w)

        # Official ivars.
        self.menubar = w
    #@-node:ekr.20090424085523.45:createMenuBar
    #@+node:ekr.20090424085523.44:createMiniBuffer
    def createMiniBuffer (self,parent):

        # Create widgets.
        frame = self.createFrame(self.centralwidget,'minibufferFrame',
            hPolicy = QtGui.QSizePolicy.MinimumExpanding,
            vPolicy = QtGui.QSizePolicy.Fixed)
        frame.setMinimumSize(QtCore.QSize(100, 0))
        label = self.createLabel(frame,'minibufferLabel','Minibuffer:')
        lineEdit = QtGui.QLineEdit(frame)
        lineEdit.setObjectName('lineEdit') # name important.

        # Pack.
        hLayout = self.createHLayout(frame,'minibufferHLayout',spacing=4)
        hLayout.setContentsMargins(3, 2, 2, 0)
        hLayout.addWidget(label)
        hLayout.addWidget(lineEdit)
        self.verticalLayout.addWidget(frame)
        label.setBuddy(lineEdit)

        # Official ivars.
        self.lineEdit = lineEdit
        # self.leo_minibuffer_frame = frame
        # self.leo_minibuffer_layout = layout
    #@-node:ekr.20090424085523.44:createMiniBuffer
    #@+node:ekr.20090424085523.47:createOutlinePane
    def createOutlinePane (self,parent):

        # Create widgets.
        treeFrame = self.createFrame(parent,'outlineFrame',
            vPolicy = QtGui.QSizePolicy.Expanding)
        innerFrame = self.createFrame(treeFrame,'outlineInnerFrame',
            hPolicy = QtGui.QSizePolicy.Preferred)
        treeWidget = self.createTreeWidget(innerFrame,'treeWidget')

        # Pack.
        grid = self.createGrid(treeFrame,'outlineGrid')
        grid.addWidget(innerFrame, 0, 0, 1, 1)
        innerGrid = self.createGrid(innerFrame,'outlineInnerGrid')
        innerGrid.addWidget(treeWidget, 0, 0, 1, 1)

        # Signals.
        if False: # Ville's bug fix.  Crashes with or without this.
            QtCore.QObject.connect(treeWidget,
                QtCore.SIGNAL("itemSelectionChanged()"),self.showNormal)

        # Official ivars...
        self.treeWidget = treeWidget
        # self.leo_outline_frame = treeFrame
        # self.leo_outline_grid = grid
        # self.leo_outline_inner_frame = innerFrame
    #@-node:ekr.20090424085523.47:createOutlinePane
    #@+node:ekr.20090424085523.46:createStatusBar
    def createStatusBar (self,parent):

        w = QtGui.QStatusBar(parent)
        w.setObjectName("statusbar")
        parent.setStatusBar(w)

        # Official ivars.
        self.statusBar = w
    #@-node:ekr.20090424085523.46:createStatusBar
    #@+node:ekr.20090425072841.2:setMainWindowOptions
    def setMainWindowOptions (self):

        MainWindow = self

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(691, 635)
        MainWindow.setDockNestingEnabled(False)
        MainWindow.setDockOptions(
            QtGui.QMainWindow.AllowTabbedDocks |
            QtGui.QMainWindow.AnimatedDocks)
    #@-node:ekr.20090425072841.2:setMainWindowOptions
    #@-node:ekr.20090426183711.10:top-level
    #@+node:ekr.20090426183711.11:widgets
    #@+node:ekr.20090424085523.51:createButton
    def createButton (self,parent,name,label):

        w = QtGui.QPushButton(parent)
        w.setObjectName(name)
        w.setText(self.tr(label))
        return w
    #@nonl
    #@-node:ekr.20090424085523.51:createButton
    #@+node:ekr.20090424085523.39:createCheckBox
    def createCheckBox (self,parent,name,label):

        w = QtGui.QCheckBox(parent)
        self.setName(w,name)
        w.setText(self.tr(label))
        return w
    #@nonl
    #@-node:ekr.20090424085523.39:createCheckBox
    #@+node:ekr.20090426083450.10:createContainer (to do)
    def createContainer (self,parent):

        pass
    #@nonl
    #@-node:ekr.20090426083450.10:createContainer (to do)
    #@+node:ekr.20090426083450.11:createFrame
    def createFrame (self,parent,name,
        hPolicy=None,vPolicy=None,
        lineWidth = 1,
        shadow = QtGui.QFrame.Plain,
        shape = QtGui.QFrame.NoFrame,
    ):

        w = QtGui.QFrame(parent)
        self.setSizePolicy(w,kind1=hPolicy,kind2=vPolicy)
        w.setFrameShape(shape)
        w.setFrameShadow(shadow)
        w.setLineWidth(lineWidth)
        self.setName(w,name)
        return w
    #@-node:ekr.20090426083450.11:createFrame
    #@+node:ekr.20090426083450.12:createGrid
    def createGrid (self,parent,name,margin=0,spacing=0):

        w = QtGui.QGridLayout(parent)
        w.setMargin(margin)
        w.setSpacing(spacing)
        self.setName(w,name)
        return w
    #@nonl
    #@-node:ekr.20090426083450.12:createGrid
    #@+node:ekr.20090426083450.19:createHLayout & createVLayout
    def createHLayout (self,parent,name,margin=0,spacing=0):

        hLayout = QtGui.QHBoxLayout(parent)
        hLayout.setSpacing(spacing)
        hLayout.setMargin(margin)
        self.setName(hLayout,name)
        return hLayout

    def createVLayout (self,parent,name,margin=0,spacing=0):

        vLayout = QtGui.QVBoxLayout(parent)
        vLayout.setSpacing(spacing)
        vLayout.setMargin(margin)
        self.setName(vLayout,name)
        return vLayout
    #@-node:ekr.20090426083450.19:createHLayout & createVLayout
    #@+node:ekr.20090426083450.14:createLabel
    def createLabel (self,parent,name,label):

        w = QtGui.QLabel(parent)
        self.setName(w,name)
        w.setText(self.tr(label))
        return w
    #@-node:ekr.20090426083450.14:createLabel
    #@+node:ekr.20090424085523.40:createLineEdit
    def createLineEdit (self,parent,name):

        w = QtGui.QLineEdit(parent)
        w.setObjectName(name)
        return w
    #@-node:ekr.20090424085523.40:createLineEdit
    #@+node:ekr.20090427060355.11:createRadioButton
    def createRadioButton (self,parent,name,label):

        w = QtGui.QRadioButton(parent)
        self.setName(w,name)
        w.setText(self.tr(label))
        return w
    #@nonl
    #@-node:ekr.20090427060355.11:createRadioButton
    #@+node:ekr.20090426083450.18:createStackedWidget
    def createStackedWidget (self,parent,name,
        lineWidth = 1,
        hPolicy=None,vPolicy=None,
    ):

        w = QtGui.QStackedWidget(parent)
        self.setSizePolicy(w,kind1=hPolicy,kind2=vPolicy)
        w.setAcceptDrops(True)
        w.setLineWidth(1)
        self.setName(w,name)
        return w
    #@-node:ekr.20090426083450.18:createStackedWidget
    #@+node:ekr.20090426083450.17:createTabWidget
    def createTabWidget (self,parent,name,hPolicy=None,vPolicy=None):

        w = QtGui.QTabWidget(parent)
        self.setSizePolicy(w,kind1=hPolicy,kind2=vPolicy)
        self.setName(w,name)
        return w
    #@-node:ekr.20090426083450.17:createTabWidget
    #@+node:ekr.20090426083450.16:createText
    def createText (self,parent,name,
        # hPolicy=None,vPolicy=None,
        lineWidth = 0,
        shadow = QtGui.QFrame.Plain,
        shape = QtGui.QFrame.NoFrame,
    ):

        w = QtGui.QTextEdit(parent)
        # self.setSizePolicy(w,kind1=hPolicy,kind2=vPolicy)
        w.setFrameShape(shape)
        w.setFrameShadow(shadow)
        w.setLineWidth(lineWidth)
        self.setName(w,name)
        return w
    #@-node:ekr.20090426083450.16:createText
    #@+node:ekr.20090426083450.15:createTreeWidget
    def createTreeWidget (self,parent,name):

        w = QtGui.QTreeWidget(parent)
        self.setSizePolicy(w)
        w.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        w.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        w.setHeaderHidden(False)
        self.setName(w,name)
        return w
    #@-node:ekr.20090426083450.15:createTreeWidget
    #@-node:ekr.20090426183711.11:widgets
    #@+node:ekr.20090426183711.12:log tabs
    #@+node:ekr.20090424085523.38:createFindTab
    def createFindTab (self,parent):

        grid = self.createGrid(parent,'findGrid',margin=10,spacing=15)

        # Labels.
        lab2 = self.createLabel(parent,'findLabel','Find:')
        lab3 = self.createLabel(parent,'changeLabel','Change:')
        grid.addWidget(lab2,0,0)
        grid.addWidget(lab3,1,0)

        # Text areas.
        findPattern = self.createLineEdit(parent,'findPattern')
        findChange  = self.createLineEdit(parent,'findChange')
        grid.addWidget(findPattern,0,1)
        grid.addWidget(findChange,1,1)

        # Check boxes and radio buttons.
        # Radio buttons are mutually exclusive because they have the same parent.
        def mungeName(name):
            # The value returned here is significant: it creates an ivar.
            return 'checkBox%s' % label.replace(' ','').replace('&','')

        table = (
            ('box', 'Whole &Word',      2,0),
            ('rb',  '&Entire Outline',  2,1),
            ('box', '&Ignore Case',     3,0),
            ('rb',  '&Subroutine Only', 3,1),
            ('box', 'Wrap &Around',     4,0),
            ('rb',  '&Node Only',       4,1),
            ('box', '&Reverse',         5,0),
            ('box', 'Search &Headline', 5,1),
            ('box', 'Rege&xp',          6,0),
            ('box', 'Search &Body',     6,1),
            ('box', 'Mark &Finds',      7,0),
            ('box', 'Mark &Changes',    7,1))
            # a,b,c,e,f,h,i,n,rs,w

        for kind,label,row,col in table:
            name = mungeName(label)
            func = g.choose(kind=='box',
                self.createCheckBox,self.createRadioButton)
            w = func(parent,name,label)
            grid.addWidget(w,row,col)
            setattr(self,name,w)

        # Official ivars (in addition to setattr ivars).
        self.findPattern = findPattern
        self.findChange = findChange
    #@-node:ekr.20090424085523.38:createFindTab
    #@+node:ekr.20090424085523.50:createSpellTab
    def createSpellTab (self,parent):

        MainWindow = self

        vLayout = self.createVLayout(parent,'spellVLayout',margin=2)
        spellFrame = self.createFrame(parent,'spellFrame')
        vLayout2 = self.createVLayout(spellFrame,'spellVLayout')
        grid = self.createGrid(None,'spellGrid',spacing=2)

        table = (
            ('Add',     'Add',          2,1),
            ('Find',    'Find',         2,0),
            ('Change',  'Change',       3,0),
            ('FindChange','Change,Find',3,1),
            ('Ignore',  'Ignore',       4,0),
            ('Hide',    'Hide',         4,1),
        )
        for (ivar,label,row,col) in table:
            name = 'spell_%s_button' % label
            button = self.createButton(spellFrame,name,label)
            grid.addWidget(button,row,col)
            func = getattr(self,'do_leo_spell_btn_%s' % ivar)
            QtCore.QObject.connect(button,QtCore.SIGNAL("clicked()"),func)
            # This name is significant.
            setattr(self,'leo_spell_btn_%s' % (ivar),button)

        self.leo_spell_btn_Hide.setCheckable(False)

        spacerItem = QtGui.QSpacerItem(20, 40,
            QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)

        grid.addItem(spacerItem, 5, 0, 1, 1)

        listBox = QtGui.QListWidget(spellFrame)
        self.setSizePolicy(listBox,
            kind1 = QtGui.QSizePolicy.MinimumExpanding,
            kind2 = QtGui.QSizePolicy.Expanding)
        listBox.setMinimumSize(QtCore.QSize(0, 0))
        listBox.setMaximumSize(QtCore.QSize(150, 150))
        listBox.setObjectName("leo_spell_listBox")

        grid.addWidget(listBox, 1, 0, 1, 2)

        spacerItem1 = QtGui.QSpacerItem(40, 20,
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        grid.addItem(spacerItem1, 2, 2, 1, 1)

        lab = self.createLabel(spellFrame,'spellLabel','spellLabel')

        grid.addWidget(lab, 0, 0, 1, 2)
        vLayout2.addLayout(grid)
        vLayout.addWidget(spellFrame)

        QtCore.QObject.connect(listBox,
            QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem*)"),
            self.do_leo_spell_btn_FindChange)

        # Official ivars.
        self.spellFrame = spellFrame
        self.spellGrid = grid
        self.leo_spell_listBox = listBox # Must exist
        self.leo_spell_label = lab # Must exist (!!)
    #@-node:ekr.20090424085523.50:createSpellTab
    #@-node:ekr.20090426183711.12:log tabs
    #@+node:ekr.20090426183711.13:utils
    #@+node:ekr.20090426083450.13:setName
    def setName (self,widget,name):

        if name:
            # if not name.startswith('leo_'):
                # name = 'leo_' + name
            widget.setObjectName(name)
    #@-node:ekr.20090426083450.13:setName
    #@+node:ekr.20090425072841.14:setSizePolicy
    def setSizePolicy (self,widget,kind1=None,kind2=None):

        if kind1 is None: kind1 = QtGui.QSizePolicy.Ignored
        if kind2 is None: kind2 = QtGui.QSizePolicy.Ignored

        sizePolicy = QtGui.QSizePolicy(kind1,kind2)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)

        sizePolicy.setHeightForWidth(
            widget.sizePolicy().hasHeightForWidth())

        widget.setSizePolicy(sizePolicy)
    #@-node:ekr.20090425072841.14:setSizePolicy
    #@+node:ekr.20090424085523.48:tr
    def tr(self,s):

        return QtGui.QApplication.translate(
            'MainWindow',s,None,QtGui.QApplication.UnicodeUTF8)
    #@nonl
    #@-node:ekr.20090424085523.48:tr
    #@-node:ekr.20090426183711.13:utils
    #@-node:ekr.20090423070717.14:createMainWindow & helpers
    #@+node:leohag.20081203210510.17:do_leo_spell_btn_*
    def doSpellBtn(self, btn):
        getattr(self.c.spellCommands.handler.tab, btn)() 

    def do_leo_spell_btn_Add(self):
        self.doSpellBtn('onAddButton')

    def do_leo_spell_btn_Change(self):
        self.doSpellBtn('onChangeButton')

    def do_leo_spell_btn_Find(self):
        self.doSpellBtn('onFindButton')

    def do_leo_spell_btn_FindChange(self):
        self.doSpellBtn('onChangeThenFindButton')

    def do_leo_spell_btn_Hide(self):
        self.doSpellBtn('onHideButton')

    def do_leo_spell_btn_Ignore(self):
        self.doSpellBtn('onIgnoreButton')
    #@-node:leohag.20081203210510.17:do_leo_spell_btn_*
    #@+node:edward.20081129091117.1:setSplitDirection (dynamicWindow)
    def setSplitDirection (self,orientation='vertical'):

        vert = orientation and orientation.lower().startswith('v')
        h,v = QtCore.Qt.Horizontal,QtCore.Qt.Vertical

        orientation1 = g.choose(vert,h,v)
        orientation2 = g.choose(vert,v,h)

        self.splitter.setOrientation(orientation1)
        self.splitter_2.setOrientation(orientation2)

        # g.trace('vert',vert)

    #@-node:edward.20081129091117.1:setSplitDirection (dynamicWindow)
    #@+node:ekr.20081121105001.203:setStyleSheets & helper
    styleSheet_inited = False

    def setStyleSheets(self):

        trace = False
        c = self.c

        sheet = c.config.getData('qt-gui-plugin-style-sheet')
        if sheet:
            sheet = '\n'.join(sheet)
            if trace: g.trace(len(sheet))
            self.ui.setStyleSheet(sheet or self.default_sheet())
        else:
            if trace: g.trace('no style sheet')
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

#@-node:ekr.20081121105001.200:class  DynamicWindow (QtGui.QMainWindow)
#@+node:ekr.20081121105001.205:class leoQtBody (leoBody)
class leoQtBody (leoFrame.leoBody):

    """A class that represents the body pane of a Qt window."""

    #@    @+others
    #@+node:ekr.20081121105001.206: Birth
    #@+node:ekr.20081121105001.207: ctor (qtBody)
    def __init__ (self,frame,parentFrame):

        trace = False and not g.unitTesting

        # Call the base class constructor.
        leoFrame.leoBody.__init__(self,frame,parentFrame)

        c = self.c
        assert c.frame == frame and frame.c == c

        self.useScintilla = c.config.getBool('qt-use-scintilla')
        self.selectedBackgroundColor = c.config.getString('selected-background-color')
        self.unselectedBackgroundColor = c.config.getString('unselected-background-color')

        # Set the actual gui widget.
        if self.useScintilla:
            self.widget = w = leoQScintillaWidget(
                c.frame.top.textEdit,
                name='body',c=c)
            self.bodyCtrl = w # The widget as seen from Leo's core.
            self.colorizer = leoColor.nullColorizer(c)
        else:
            top = c.frame.top
            sw = top.ui.stackedWidget
            qtWidget = top.ui.richTextEdit # A QTextEdit.
            sw.setCurrentIndex(1)
            self.widget = w = leoQTextEditWidget(
            #self.widget = w = leoQBodyTextEditWidget(
                qtWidget,name = 'body',c=c)
            self.bodyCtrl = w # The widget as seen from Leo's core.

            # Hook up the QSyntaxHighlighter
            self.colorizer = leoQtColorizer(c,w.widget)
            w.acceptRichText = False

        # Config stuff.
        self.trace_onBodyChanged = c.config.getBool('trace_onBodyChanged')
        wrap = c.config.getBool('body_pane_wraps')
        # g.trace('wrap',wrap,self.widget.widget)
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

        if trace: print('qtBody.__init__ %s' % self.widget)
    #@-node:ekr.20081121105001.207: ctor (qtBody)
    #@+node:ekr.20081121105001.208:createBindings (qtBody)
    def createBindings (self,w=None):

        '''(qtBody) Create gui-dependent bindings.
        These are *not* made in nullBody instances.'''

        # frame = self.frame ; c = self.c ; k = c.k
        # if not w: w = self.widget

        # c.bind(w,'<Key>', k.masterKeyHandler)

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
    #@+node:ekr.20081121105001.214:packEditorLabelWidget
    def packEditorLabelWidget (self,w):

        '''Create a qt label widget.'''

        # if not hasattr(w,'leo_label') or not w.leo_label:
            # # g.trace('w.leo_frame',id(w.leo_frame))
            # w.pack_forget()
            # w.leo_label = Tk.Label(w.leo_frame)
            # w.leo_label.pack(side='top')
            # w.pack(expand=1,fill='both')
    #@nonl
    #@-node:ekr.20081121105001.214:packEditorLabelWidget
    #@+node:ekr.20081121105001.215:entries
    #@+node:ekr.20081121105001.216:addEditor & helper (qtBody)
    # An override of leoFrame.addEditor.

    def addEditor (self,event=None):

        '''Add another editor to the body pane.'''

        trace = False and not g.unitTesting
        bodyCtrl = self.c.frame.body.bodyCtrl # A leoQTextEditWidget
        self.editorWidgets['1'] = bodyCtrl
        c = self.c ; p = c.p
        self.totalNumberOfEditors += 1
        self.numberOfEditors += 1

        name = '%d' % self.totalNumberOfEditors
        f,wrapper = self.createEditor(name)
        w = wrapper.widget
        assert isinstance(wrapper,leoQTextEditWidget),wrapper
        assert isinstance(w,QtGui.QTextEdit),w
        assert isinstance(f,QtGui.QFrame),f
        self.editorWidgets[name] = wrapper

        if trace: g.trace('name %s wrapper %s w %s' % (
            name,id(wrapper),id(w)))

        if self.numberOfEditors == 2:
            # Inject the ivars into the first editor.
            # The name of the last editor need not be '1'
            d = self.editorWidgets ; keys = d.keys()
            old_name = keys[0]
            old_wrapper = d.get(old_name)
            old_w = old_wrapper.widget
            self.injectIvars(f,old_name,p,old_wrapper)
            self.updateInjectedIvars (old_w,p)
            self.selectLabel(old_wrapper) # Immediately create the label in the old editor.

        # Switch editors.
        c.frame.body.bodyCtrl = wrapper
        ##### self.updateInjectedIvars(w,p)
        self.selectLabel(wrapper)
        self.selectEditor(wrapper)
        self.updateEditors()
        c.bodyWantsFocusNow()
    #@+node:ekr.20081121105001.213:createEditor
    def createEditor (self,name):

        c = self.c ; p = c.p
        f = c.frame.top.ui.leo_body_inner_frame
            # Valid regardless of qtGui.useUI

        # Step 1: create the editor.
        w = QtGui.QTextEdit(f)
        w.setObjectName('richTextEdit') # Will be changed later.
        wrapper = leoQTextEditWidget(w,name='body',c=c)
        f.layout().addWidget(w,0,self.numberOfEditors-1)

        # Step 2: inject ivars, set bindings, etc.
        self.injectIvars(f,name,p,wrapper)
        self.updateInjectedIvars(w,p)
        wrapper.setAllText(p.b)
        wrapper.see(0)
        self.createBindings(w=wrapper)
        c.k.completeAllBindingsForWidget(wrapper)
        self.recolorWidget(p,wrapper)

        return f,wrapper
    #@-node:ekr.20081121105001.213:createEditor
    #@-node:ekr.20081121105001.216:addEditor & helper (qtBody)
    #@+node:ekr.20081121105001.218:assignPositionToEditor
    def assignPositionToEditor (self,p):

        '''Called *only* from tree.select to select the present body editor.'''

        c = self.c ; cc = c.chapterController
        wrapper = c.frame.body.bodyCtrl
        w = wrapper.widget

        self.updateInjectedIvars(w,p)
        self.selectLabel(wrapper)

        # g.trace('===',id(w),w.leo_chapter.name,w.leo_p.h)
    #@nonl
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

        trace = False and not g.unitTesting
        c = self.c ; d = self.editorWidgets
        wrapper = c.frame.body.bodyCtrl
        w = wrapper.widget
        name = w.leo_name
        assert name
        assert wrapper == d.get(name),'wrong wrapper'
        assert isinstance(wrapper,leoQTextEditWidget),wrapper
        assert isinstance(w,QtGui.QTextEdit),w
        if len(d.keys()) <= 1: return

        # Actually delete the widget.
        if trace: g.trace('**delete name %s id(wrapper) %s id(w) %s' % (
            name,id(wrapper),id(w)))

        del d [name]
        f = c.frame.top.ui.leo_body_inner_frame
        layout = f.layout()
        index = layout.indexOf(w)
        item = layout.itemAt(index)
        item.setGeometry(QtCore.QRect(0,0,0,0))
        layout.removeItem(item)

        # Select another editor.
        new_wrapper = d.values()[0]
        if trace: g.trace(wrapper,new_wrapper)
        self.numberOfEditors -= 1
        self.selectEditor(new_wrapper)
    #@-node:ekr.20081121105001.220:deleteEditor
    #@+node:ekr.20081121105001.221:findEditorForChapter (leoBody)
    def findEditorForChapter (self,chapter,p):

        '''Return an editor to be assigned to chapter.'''

        trace = False and not g.unitTesting
        c = self.c ; d = self.editorWidgets
        values = d.values()

        # First, try to match both the chapter and position.
        if p:
            for w in values:
                if (
                    hasattr(w,'leo_chapter') and w.leo_chapter == chapter and
                    hasattr(w,'leo_p') and w.leo_p and w.leo_p == p
                ):
                    if trace: g.trace('***',id(w),'match chapter and p',p.h)
                    return w

        # Next, try to match just the chapter.
        for w in values:
            if hasattr(w,'leo_chapter') and w.leo_chapter == chapter:
                if trace: g.trace('***',id(w),'match only chapter',p.h)
                return w

        # As a last resort, return the present editor widget.
        if trace: g.trace('***',id(self.bodyCtrl),'no match',p.h)
        return c.frame.body.bodyCtrl
    #@-node:ekr.20081121105001.221:findEditorForChapter (leoBody)
    #@+node:ekr.20081121105001.222:select/unselectLabel (leoBody)
    def unselectLabel (self,wrapper):

        pass

        # self.createChapterIvar(wrapper)
        # self.packEditorLabelWidget(wrapper)
        # s = self.computeLabel(wrapper)
        # w = wrapper.widget
        # if hasattr(w,'leo_label') and w.leo_label:
            # w.leo_label.configure(text=s,bg='LightSteelBlue1')

    def selectLabel (self,wrapper):

        w = wrapper.widget

        # if self.numberOfEditors > 1:
            # self.createChapterIvar(wrapper)
            # self.packEditorLabelWidget(wrapper)
            # s = self.computeLabel(wrapper)
            # w = wrapper.widget
            # # g.trace(s,g.callers())
            # if hasattr(w,'leo_label') and w.leo_label:
                # w.leo_label.configure(text=s,bg='white')
        # elif hasattr(w,'leo_label') and w.leo_label:
            # # w.leo_label.pack_forget()
            # w.leo_label = None
    #@-node:ekr.20081121105001.222:select/unselectLabel (leoBody)
    #@+node:ekr.20081121105001.223:selectEditor & helpers
    selectEditorLockout = False

    def selectEditor(self,wrapper):

        '''Select editor w and node w.leo_p.'''

        #  Called by body.onClick and whenever w must be selected.
        trace = True and not g.unitTesting
        verbose = False
        c = self.c ; bodyCtrl = c.frame.body.bodyCtrl

        if not wrapper: return bodyCtrl
        if self.selectEditorLockout:
            if trace: g.trace('**busy')
            return

        w = wrapper.widget
        assert isinstance(wrapper,leoQTextEditWidget),wrapper
        assert isinstance(w,QtGui.QTextEdit),w

        def report(s):
             g.trace('*** %9s wrapper %s w %s %s' % (
                s,id(wrapper),id(w),c.p.h))

        if wrapper and wrapper == bodyCtrl:
            self.deactivateEditors(wrapper)
            if hasattr(w,'leo_p') and w.leo_p and w.leo_p != c.p:
                if trace: report('select')
                c.selectPosition(w.leo_p)
                c.bodyWantsFocusNow()
            elif trace and verbose: report('no change')
            return

        try:
            val = None
            self.selectEditorLockout = True
            val = self.selectEditorHelper(wrapper)
        finally:
            self.selectEditorLockout = False

        return val # Don't put a return in a finally clause.
    #@+node:ekr.20081121105001.224:selectEditorHelper
    def selectEditorHelper (self,wrapper):

        trace = False and not g.unitTesting
        c = self.c ; cc = c.chapterController
        d = self.editorWidgets
        assert isinstance(wrapper,leoQTextEditWidget),wrapper
        w = wrapper.widget
        assert isinstance(w,QtGui.QTextEdit),w

        if not w.leo_p:
            g.trace('no w.leo_p') 
            return 'break'

        # The actual switch.
        self.deactivateEditors(wrapper)
        c.frame.body.bodyCtrl = wrapper
        w.leo_active = True

        self.switchToChapter(wrapper)
        self.selectLabel(wrapper)

        if not self.ensurePositionExists(w):
            return g.trace('***** no position editor!')
        if not (hasattr(w,'leo_p') and w.leo_p):
            return g.trace('***** no w.leo_p',w)
        if not (hasattr(w,'leo_chapter') and w.leo_chapter.name):
            return g.trace('***** no w.leo_chapter',w)

        p = w.leo_p
        assert p,p

        if trace: g.trace('wrapper %s chapter %s old %s p %s' % (
            id(wrapper),w.leo_chapter.name,c.p.h,p.h))

        c.expandAllAncestors(p)
        c.selectPosition(p) # Calls assignPositionToEditor.
        c.redraw()
        c.recolor_now()
        #@    << restore the selection, insertion point and the scrollbar >>
        #@+node:ekr.20081121105001.225:<< restore the selection, insertion point and the scrollbar >>
        # g.trace('active:',id(w),'scroll',w.leo_scrollBarSpot,'ins',w.leo_insertSpot)

        if hasattr(w,'leo_insertSpot') and w.leo_insertSpot:
            wrapper.setInsertPoint(w.leo_insertSpot)
        else:
            wrapper.setInsertPoint(0)

        if hasattr(w,'leo_scrollBarSpot') and w.leo_scrollBarSpot is not None:
            first,last = w.leo_scrollBarSpot
            wrapper.see(first)
        else:
            wrapper.seeInsertPoint()

        if hasattr(w,'leo_selection') and w.leo_selection:
            try:
                start,end = w.leo_selection
                wrapper.setSelectionRange(start,end)
            except Exception:
                pass
        #@-node:ekr.20081121105001.225:<< restore the selection, insertion point and the scrollbar >>
        #@nl
        c.bodyWantsFocusNow()
    #@-node:ekr.20081121105001.224:selectEditorHelper
    #@-node:ekr.20081121105001.223:selectEditor & helpers
    #@+node:ekr.20081121105001.226:updateEditors
    # Called from addEditor and assignPositionToEditor

    def updateEditors (self):

        c = self.c ; p = c.p
        d = self.editorWidgets
        if len(d.keys()) < 2: return # There is only the main widget.

        for key in d:
            wrapper = d.get(key)
            w = wrapper.widget
            v = hasattr(w,'leo_p') and w.leo_p.v
            if v and v == p.v and w != c.frame.body.bodyCtrl:
                ### wrapper.setAllText(p.b)
                self.recolorWidget(p,wrapper)

        c.bodyWantsFocus()
    #@-node:ekr.20081121105001.226:updateEditors
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

        if hasattr(w,'leo_chapter') and w.leo_chapter:
            pass
        elif cc and self.use_chapters:
            w.leo_chapter = cc.getSelectedChapter()
        else:
            w.leo_chapter = None
    #@-node:ekr.20081121105001.229:createChapterIvar
    #@+node:ekr.20081121105001.231:deactivateEditors
    def deactivateEditors(self,wrapper):

        '''Deactivate all editors except wrapper's editor.'''

        trace = False and not g.unitTesting
        d = self.editorWidgets

        # Don't capture ivars here! assignPositionToEditor keeps them up-to-date. (??)
        for key in d:
            wrapper2 = d.get(key)
            w2 = wrapper2.widget
            if hasattr(w2,'leo_active'):
                active = w2.leo_active
            else:
                active = True
            if wrapper2 != wrapper and active:
                w2.leo_active = False
                self.unselectLabel(wrapper2)
                w2.leo_scrollBarSpot = wrapper2.getYScrollPosition()
                w2.leo_insertSpot = wrapper2.getInsertPoint()
                w2.leo_selection = wrapper2.getSelectionRange()
                if trace: g.trace('**deactivate wrapper %s w %s' % (
                    id(wrapper2),id(w2)))
                self.onFocusOut(w2)
    #@nonl
    #@-node:ekr.20081121105001.231:deactivateEditors
    #@+node:ekr.20081121105001.230:ensurePositionExists
    def ensurePositionExists(self,w):

        '''Return True if w.leo_p exists or can be reconstituted.'''

        trace = True and not g.unitTesting
        c = self.c

        if c.positionExists(w.leo_p):
            return True
        else:
            if trace: g.trace('***** does not exist',w.leo_name)
            for p2 in c.all_positions_with_unique_vnodes_iter():
                if p2.v and p2.v == w.leo_p.v:
                    if trace: g.trace(p2.h)
                    w.leo_p = p2.copy()
                    return True
            else:
                # This *can* happen when selecting a deleted node.
                if trace: g.trace(p2.h)
                w.leo_p = c.p.copy()
                return False
    #@-node:ekr.20081121105001.230:ensurePositionExists
    #@+node:ekr.20090318091009.14:injectIvars
    def injectIvars (self,parentFrame,name,p,wrapper):

        trace = False and not g.unitTesting

        w = wrapper.widget
        assert isinstance(wrapper,leoQTextEditWidget),wrapper
        assert isinstance(w,QtGui.QTextEdit),w

        if trace: g.trace(name,id(w),p.h)

        # Inject ivars
        if name == '1':
            w.leo_p = None # Will be set when the second editor is created.
        else:
            w.leo_p = p.copy()

        w.leo_active = True
        w.leo_bodyBar = None
        w.leo_bodyXBar = None
        w.leo_chapter = None
        w.leo_frame = parentFrame
        w.leo_insertSpot = None
        w.leo_label = None
        w.leo_label_s = None
        w.leo_name = name
        # w.leo_on_focus_in = onFocusInCallback
        w.leo_scrollBarSpot = None
        w.leo_selection = None
        w.leo_wrapper = wrapper
    #@-node:ekr.20090318091009.14:injectIvars
    #@+node:ekr.20081121105001.232:recolorWidget
    def recolorWidget (self,p,wrapper):

        return ###

        c = self.c ; old_wrapper = c.frame.body.bodyCtrl

        # g.trace('wrapper',id(wrapper),p.h,len(wrapper.getAllText()))

        # Save.
        c.frame.body.bodyCtrl = wrapper
        try:
            # c.recolor_now(interruptable=False) # Force a complete recoloring.
            c.frame.body.colorizer.colorize(p,incremental=False,interruptable=False)
        finally:
            # Restore.
            c.frame.body.bodyCtrl = old_wrapper
    #@-node:ekr.20081121105001.232:recolorWidget
    #@+node:ekr.20081121105001.233:switchToChapter (leoBody)
    def switchToChapter (self,w):

        '''select w.leo_chapter.'''

        trace = True and not g.unitTesting
        c = self.c ; cc = c.chapterController

        if hasattr(w,'leo_chapter') and w.leo_chapter:
            chapter = w.leo_chapter
            name = chapter and chapter.name
            oldChapter = cc.getSelectedChapter()
            if chapter != oldChapter:
                if trace: g.trace('***old',oldChapter.name,'new',name,w.leo_p)
                cc.selectChapterByName(name)
                c.bodyWantsFocusNow()
    #@-node:ekr.20081121105001.233:switchToChapter (leoBody)
    #@+node:ekr.20081121105001.234:updateInjectedIvars
    def updateInjectedIvars (self,w,p):

        trace = False and not g.unitTesting
        if trace: g.trace('w %s len(p.b) %s %s' % (
            id(w),len(p.b),p.h),g.callers(5))

        c = self.c ; cc = c.chapterController
        assert isinstance(w,QtGui.QTextEdit),w

        if cc and self.use_chapters:
            w.leo_chapter = cc.getSelectedChapter()
        else:
            w.leo_chapter = None

        w.leo_p = p.copy()
        w.leo_label_s = p.h
    #@nonl
    #@-node:ekr.20081121105001.234:updateInjectedIvars
    #@-node:ekr.20081121105001.227:utils
    #@-node:ekr.20081121105001.212:Editors (qtBody)
    #@+node:ekr.20090406071640.13:Event handlers called from eventFilter (qtBody)
    def onFocusIn (self,obj):

        '''Handle a focus-in event in the body pane.'''

        if obj.objectName() == 'richTextEdit':
            wrapper = hasattr(obj,'leo_wrapper') and obj.leo_wrapper
            if wrapper and wrapper != self.bodyCtrl:
                self.selectEditor(wrapper)
            self.onFocusColorHelper('focus-in',obj)
            obj.setReadOnly(False)

    def onFocusOut (self,obj):

        '''Handle a focus-out event in the body pane.'''

        if obj.objectName() == 'richTextEdit':
            self.onFocusColorHelper('focus-out',obj)
            obj.setReadOnly(True)
    #@+node:ekr.20090608052916.3810:onFocusColorHelper
    badFocusColors = []

    def onFocusColorHelper(self,kind,obj):

        trace = False and not g.unitTesting

        colorName = g.choose(kind=='focus-in',
            self.selectedBackgroundColor,
            self.unselectedBackgroundColor)

        if not colorName: return

        if trace: g.trace(id(obj),'%9s' % (kind),str(obj.objectName()))

        styleSheet = 'QTextEdit#richTextEdit { background-color: %s; }' % (
            colorName)

        if QtGui.QColor(colorName).isValid():
            obj.setStyleSheet(styleSheet)
        elif colorName not in self.badFocusColors:
            self.badFocusColors.append(colorName)
            g.es_print('invalid body background color: %s' % (colorName),color='blue')
    #@-node:ekr.20090608052916.3810:onFocusColorHelper
    #@-node:ekr.20090406071640.13:Event handlers called from eventFilter (qtBody)
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

        owner = self

        self.svarDict = {}
            # Keys are ivar names, values are svar objects.

        for ivar in self.intKeys:
            self.svarDict[ivar] = self.svar(owner,ivar)

        # Add a hack for 'entire_outline' radio button.
        ivar = 'entire_outline'
        self.svarDict[ivar] = self.svar(owner,ivar)

        for ivar in self.newStringKeys:
            # "radio-find-type", "radio-search-scope"
            self.svarDict[ivar] = self.svar(owner,ivar)
    #@-node:ekr.20081121105001.237:initGui
    #@+node:ekr.20081121105001.238:init (qtFindTab) & helpers
    def init (self,c):

        '''Init the widgets of the 'Find' tab.'''

        # g.trace('leoQtFindTab.init')

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
            ('whole_word',      w.checkBoxWholeWord),
            ('ignore_case',     w.checkBoxIgnoreCase),
            ('wrap',            w.checkBoxWrapAround),
            ('reverse',         w.checkBoxReverse),
            ('pattern_match',   w.checkBoxRegexp),
            ('mark_finds',      w.checkBoxMarkFinds),
            ('entire_outline',  w.checkBoxEntireOutline),
            ('suboutline_only', w.checkBoxSubroutineOnly),  
            ('node_only',       w.checkBoxNodeOnly),
            ('search_headline', w.checkBoxSearchHeadline),
            ('search_body',     w.checkBoxSearchBody),
            ('mark_changes',    w.checkBoxMarkChanges),
            ('batch', None),
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
        for ivar in self.intKeys:
            # Get ivars from @settings.
            val = c.config.getBool(ivar)
            setattr(self,ivar,val)
            val = g.choose(val,1,0)
            svar = self.svarDict.get(ivar)
            if svar:
                svar.set(val)

            # g.trace(ivar,val)
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
            'whole_word','wrap',
            'node_only','suboutline_only','entire_outline',
        )

        for ivar in aList:
            svar = self.svarDict.get(ivar)
            if svar:
                # w is a QCheckBox or a QRadioButton.
                w = self.widgetsDict.get(ivar)
                if w:
                    val = svar.get()
                    svar.setWidget(w)
                    svar.set(val)
                    if isinstance(w,QtGui.QCheckBox):
                        def checkBoxCallback(val,svar=svar):
                            svar.set(val)
                        w.connect(w,
                            QtCore.SIGNAL("stateChanged(int)"),
                            checkBoxCallback)
                    else:
                        def radioButtonCallback(val,svar=svar):
                            svar.set(val)
                        w.connect(w,
                            QtCore.SIGNAL("clicked(bool)"),
                            radioButtonCallback)
                else: g.trace('*** no w',ivar)
            else: g.trace('*** no svar',ivar)
    #@-node:ekr.20081121105001.242:initCheckBoxes
    #@+node:ekr.20081121105001.243:initRadioButtons
    def initRadioButtons (self):

        scopeSvar = self.svarDict.get('radio-search-scope')

        table = (
            ("suboutline_only","suboutline-only"),
            ("node_only","node-only"))

        for ivar,key in table:
            svar = self.svarDict.get(ivar)
            if svar:
                val = svar.get()
                if val:
                    scopeSvar.init(key)
                    break
        else:
            scopeSvar.init('entire-outline')
            self.svarDict.get('entire_outline').init(True)

        w = self.widgetsDict.get(key)
        if w: w.setChecked(True)

        # g.trace(scopeSvar.get())
    #@-node:ekr.20081121105001.243:initRadioButtons
    #@-node:ekr.20081121105001.238:init (qtFindTab) & helpers
    #@-node:ekr.20081121105001.236: Birth: called from leoFind ctor
    #@+node:ekr.20081121105001.244:class svar
    class svar:
        '''A class like Tk's IntVar and StringVar classes.'''

        #@    @+others
        #@+node:ekr.20090427112929.10:svar.ctor
        def __init__(self,owner,ivar):

            self.ivar = ivar
            self.owner = owner
            self.radioButtons = ['node_only','suboutline_only','entire_outline']
            self.trace = False
            self.val = None
            self.w = None

        def __repr__(self):
            return '<svar %s>' % self.ivar
        #@nonl
        #@-node:ekr.20090427112929.10:svar.ctor
        #@+node:ekr.20090427112929.12:get
        def get (self):

            trace = False and not g.unitTesting

            if self.w:
                val = self.w.isChecked()
                if trace:
                    g.trace('qt svar %15s = %s' % (
                        self.ivar,val),g.callers(5))        
            else:
                val = self.val
            return val
        #@-node:ekr.20090427112929.12:get
        #@+node:ekr.20090427112929.13:init
        def init (self,val):

            '''Init the svar, but do *not* init radio buttons.
            (This is called from initRadioButtons).'''

            trace = False and not g.unitTesting

            if val in (0,1):
                self.val = bool(val)
            else:
                self.val = val # Don't contain the scope values!

            if self.w:
                self.w.setChecked(bool(val))

            if trace: g.trace('qt svar %15s = %s' % (
                self.ivar,val),g.callers(5))
        #@-node:ekr.20090427112929.13:init
        #@+node:ekr.20090427112929.17:set
        def set (self,val):

            '''Init the svar and update the radio buttons.'''

            self.init(val)

            if self.ivar in self.radioButtons:
                self.owner.initRadioButtons()
            elif self.ivar == 'radio-search-scope':
                self.setRadioScope(val)


        #@-node:ekr.20090427112929.17:set
        #@+node:ekr.20090427112929.18:setRadioScope
        def setRadioScope (self,val):

            '''Update the svars corresponding to the scope value.'''

            table = (
                ("suboutline_only","suboutline-only"),
                ("node_only","node-only"),
                ("entire_outline","entire-outline"))

            for ivar,val2 in table:
                if val == val2:
                    svar = self.owner.svarDict.get(ivar)
                    val = svar.get()
                    svar.init(True)
        #@-node:ekr.20090427112929.18:setRadioScope
        #@+node:ekr.20090427112929.15:setWidget
        def setWidget(self,w):

            self.w = w
        #@-node:ekr.20090427112929.15:setWidget
        #@-others

    #@-node:ekr.20081121105001.244:class svar
    #@+node:ekr.20081121105001.245:Support for minibufferFind class (qtFindTab)
    # This is the same as the Tk code because we simulate Tk svars.
    #@nonl
    #@+node:ekr.20081121105001.246:getOption
    def getOption (self,ivar):

        var = self.svarDict.get(ivar)

        if var:
            val = var.get()
            # g.trace('ivar %s = %s' % (ivar,val))
            return val
        else:
            # g.trace('bad ivar name: %s' % ivar)
            return None
    #@-node:ekr.20081121105001.246:getOption
    #@+node:ekr.20081121105001.247:setOption
    def setOption (self,ivar,val):

        trace = False and not g.unitTesting

        if ivar in self.intKeys:
            if val is not None:
                svar = self.svarDict.get(ivar)
                svar.set(val)
                if trace: g.trace('qtFindTab: ivar %s = %s' % (
                    ivar,val))

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
        leoFrame.leoFrame.instances += 1 # Increment the class var.

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
            if sys.platform.startswith('linux'):
                # Work around an apparent Qt bug.
                s = g.toEncodedString(s,'ascii',reportErrors=False)
            w.setText(s)
            # w.setEnabled(False)
        #@-node:ekr.20081121105001.264:clear, get & put/1
        #@+node:ekr.20081121105001.265:update
        def update (self):
            if g.app.killed: return

            c = self.c ; body = c.frame.body

            # QTextEdit
            te = body.widget.widget
            cr = te.textCursor()
            bl = cr.block()

            col = cr.columnNumber()
            row = bl.blockNumber() + 1
            line = bl.text()

            if col > 0:
                s2 = line[0:col]        
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
            self.actions = []

            # Options
            self.buttonColor = c.config.getString('qt-button-color')

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
            # able to specify low-level QAction directly (QPushButton not forced)
            qaction = keys.get('qaction')

            if not text and not qaction:
                g.es('bad toolbar item')


            # imagefile = keys.get('imagefile')
            # image = keys.get('image')

            class leoIconBarButton (QtGui.QWidgetAction):
                def __init__ (self,parent,text,toolbar):
                    QtGui.QWidgetAction.__init__(self,parent)
                    self.button = None # set below
                    self.text = text
                    self.toolbar = toolbar
                def createWidget (self,parent):
                    self.button = b = QtGui.QPushButton(self.text,parent)
                    g.app.gui.setWidgetColor(b,
                        widgetKind='QPushButton',
                        selector='background-color',
                        colorName = self.toolbar.buttonColor)
                    return b

            if qaction is None:
                action = leoIconBarButton(parent=self.w,text=text,toolbar=self)
            else:
                action = qaction

            self.w.addAction(action)

            self.actions.append(action)
            b = self.w.widgetForAction(action)

            b.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)

            def delete_callback(action=action,):
                self.w.removeAction(action)

            b.leo_removeAction = rb = QtGui.QAction('Remove Button' ,b)

            b.addAction(rb)
            rb.connect(rb, QtCore.SIGNAL("triggered()"), delete_callback)

            if command:
                def button_callback(c=c,command=command):
                    g.trace('command',command.__name__)
                    val = command()
                    if c.exists:
                        c.bodyWantsFocus()
                        c.outerUpdate()
                    return val

                self.w.connect(b,
                    QtCore.SIGNAL("clicked()"),
                    button_callback)

            return action
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
            self.actions = []

            g.app.iconWidgetCount = 0
        #@-node:ekr.20081121105001.272:clear
        #@+node:ekr.20081121105001.273:deleteButton
        def deleteButton (self,w):
            """ w is button """

            #g.trace(w, '##')    

            self.w.removeAction(w)

            self.c.bodyWantsFocus()
            self.c.outerUpdate()
        #@-node:ekr.20081121105001.273:deleteButton
        #@+node:ekr.20081121105001.274:setCommandForButton
        def setCommandForButton(self,button,command):

            if command:
                # button is a leoIconBarButton.
                QtCore.QObject.connect(button.button,
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

        pass
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

        c.redraw()
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

        #g.trace(ratio,ratio2,g.callers())

        self.divideLeoSplitter(self.splitVerticalFlag,ratio)
        self.divideLeoSplitter(not self.splitVerticalFlag,ratio2)
    #@-node:ekr.20081121105001.287:resizePanesToRatio (qtFrame)
    #@+node:leohag.20081208130321.12:divideLeoSplitter
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
        self.divideAnySplitter(frac, self.top.splitter_2 )

    # Divides the secondary splitter.
    def divideLeoSplitter2 (self, frac, verticalFlag): 
        self.divideAnySplitter (frac, self.top.ui.splitter)

    #@-node:leohag.20081208130321.12:divideLeoSplitter
    #@+node:leohag.20081208130321.13:divideAnySplitter
    # This is the general-purpose placer for splitters.
    # It is the only general-purpose splitter code in Leo.

    def divideAnySplitter (self, frac, splitter ):#verticalFlag, bar, pane1, pane2):

        sizes = splitter.sizes()

        if len(sizes)!=2:
            g.trace('there must be two and only two widgets in the splitter')

        if frac > 1 or frac < 0:
            g.trace('split ratio [%s] out of range 0 <= frac <= 1'%frac)

        s1, s2 = sizes
        s = s1+s2
        s1 = int(s * frac + 0.5)
        s2 = s - s1 

        splitter.setSizes([s1,s2])

    #@+at
    #     # if self.bigTree:
    #         # pane1,pane2 = pane2,pane1
    # 
    #     if verticalFlag:
    #         # Panes arranged vertically; horizontal splitter bar
    #         bar.place(rely=frac)
    #         pane1.place(relheight=frac)
    #         pane2.place(relheight=1-frac)
    #     else:
    #         # Panes arranged horizontally; vertical splitter bar
    #         bar.place(relx=frac)
    #         pane1.place(relwidth=frac)
    #         pane2.place(relwidth=1-frac)
    #@-at
    #@-node:leohag.20081208130321.13:divideAnySplitter
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

        trace = False and not g.unitTesting
        if trace: g.trace()

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
    #@-node:ekr.20081121105001.302:expand/contract/hide...Pane
    #@+node:ekr.20081121105001.303:fullyExpand/hide...Pane
    def fullyExpandBodyPane (self,event=None):
        '''Fully expand the body pane.'''
        f = self
        f.divideLeoSplitter(f.splitVerticalFlag,0.0)

    def fullyExpandLogPane (self,event=None):
        '''Fully expand the log pane.'''
        f = self
        f.divideLeoSplitter(not f.splitVerticalFlag,0.0)

    def fullyExpandOutlinePane (self,event=None):
        '''Fully expand the outline pane.'''
        f = self
        f.divideLeoSplitter(f.splitVerticalFlag,1.0)

    def hideBodyPane (self,event=None):
        '''Completely contract the body pane.'''
        f = self
        f.divideLeoSplitter(f.splitVerticalFlag,1.0)

    def hideLogPane (self,event=None):
        '''Completely contract the log pane.'''
        f = self
        f.divideLeoSplitter(not f.splitVerticalFlag,1.0)

    def hideOutlinePane (self,event=None):
        '''Completely contract the outline pane.'''
        f = self
        f.divideLeoSplitter(f.splitVerticalFlag,0.0)
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

        frame.divideLeoSplitter2(0.99, not frame.splitVerticalFlag)
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
        self.lift()
    def deiconify (self):
        self.lift()
    def getFocus(self):
        return g.app.gui.get_focus() 
    def get_window_info(self):
        rect = self.top.geometry()
        topLeft = rect.topLeft()
        x,y = topLeft.x(),topLeft.y()
        w,h = rect.width(),rect.height()
        # g.trace(w,h,x,y)
        return w,h,x,y
    def iconify(self):
        self.top.showMinimized()
    def lift (self):
        self.top.showNormal()
        self.top.activateWindow()
        self.top.raise_()
    def update (self):
        pass
    def getTitle (self):
        return g.app.gui.toUnicode(self.top.windowTitle())
    def setTitle (self,s):
        self.top.setWindowTitle(s)
    def setTopGeometry(self,w,h,x,y,adjustSize=True):
        # g.trace(x,y,w,y,g.callers(5))
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

        self.tabWidget = tw = c.frame.top.ui.tabWidget
            # The Qt.TabWidget that holds all the tabs.
        self.wrap = g.choose(c.config.getBool('log_pane_wraps'),"word","none")

        # g.trace('qtLog.__init__',self.tabWidget)

        if 0: # Not needed to make onActivateEvent work.
            # Works only for .tabWidget, *not* the individual tabs!
            theFilter = leoQtEventFilter(c,w=tw,tag='tabWidget')
            tw.installEventFilter(theFilter)

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
            if w.tabText(i) in ('Find','Tab 2'):
                w.setTabText(i,'Find')
                self.contentsDict['Find'] = w.currentWidget()
                break

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

        if color:
            color = leoColor.getColor(color, 'black')

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
    def createTab (self,tabName,widget=None,wrap='none'):
        """ Create a new tab in tab widget

        if widget is None, Create a QTextBrowser,
        suitable for log functionality.
        """
        c = self.c ; w = self.tabWidget

        if widget is None:
            contents = QtGui.QTextBrowser()
            contents.setWordWrapMode(QtGui.QTextOption.NoWrap)
            self.logDict[tabName] = contents
            if tabName == 'Log': self.logCtrl = contents
            theFilter = leoQtEventFilter(c,w=contents,tag='tab')
            contents.installEventFilter(theFilter)
        else:
            contents = widget

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

        if force or tabName not in ('Log','Find','Spell'):
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

        self.createTab(tabName,widget= None,wrap = wrap)
        self.selectHelper(tabName,createText)

    #@+node:ekr.20081121105001.336:selectHelper
    def selectHelper (self,tabName,createText):

        w = self.tabWidget

        for i in range(w.count()):
            if tabName == w.tabText(i):
                w.setCurrentIndex(i)
                if createText and tabName not in ('Spell','Find',):
                    self.logCtrl = w.widget(i)
                if tabName == 'Spell':
                    # the base class uses this as a flag to see if
                    # the spell system needs initing
                    self.frameDict['Spell'] = w.widget(i)
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

        # g.pr('leoQtMenu.__init__',g.callers(4))

        self.frame = frame
        self.c = c = frame.c
        self.leo_label = '<no leo_label>'

        self.menuBar = c.frame.top.menuBar()
        assert self.menuBar is not None

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
    #@+node:ekr.20081121105001.362:add_command (qt)
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

        if menu.leo_label == 'File': g.trace(label,g.callers(4))

        action = menu.addAction(label)

        if command:
            def add_command_callback(label=label,command=command):
                return command()

            QtCore.QObject.connect(action,
                QtCore.SIGNAL("triggered()"),add_command_callback)
    #@-node:ekr.20081121105001.362:add_command (qt)
    #@+node:ekr.20081121105001.363:add_separator
    def add_separator(self,menu):

        """Wrapper for the Tkinter add_separator menu method."""

        if menu:
            menu.addSeparator()
    #@-node:ekr.20081121105001.363:add_separator
    #@+node:ekr.20081121105001.364:delete TODO
    def delete (self,menu,realItemName='<no name>'):

        """Wrapper for the Tkinter delete menu method."""

        # g.trace(menu)

        # if menu:
            # return menu.delete(realItemName)
    #@-node:ekr.20081121105001.364:delete TODO
    #@+node:ekr.20081121105001.365:delete_range (leoQtMenu)
    def delete_range (self,menu,n1,n2):

        """Wrapper for the Tkinter delete menu method."""

        # Menu is a subclass of QMenu and leoQtMenu.

        # g.trace(menu,n1,n2,g.callers(4))

        for z in menu.actions()[n1:n2]:
            menu.removeAction(z)
    #@-node:ekr.20081121105001.365:delete_range (leoQtMenu)
    #@+node:ekr.20081121105001.366:destroy
    def destroy (self,menu):

        """Wrapper for the Tkinter destroy menu method."""

        # if menu:
            # return menu.destroy()
    #@-node:ekr.20081121105001.366:destroy
    #@+node:ekr.20090603123442.3785:index (leoQtMenu) TODO
    def index (self,label):

        '''Return the index of the menu with the given label.'''
        # g.trace(label)

        return 0 ###
    #@-node:ekr.20090603123442.3785:index (leoQtMenu) TODO
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

        # g.trace(label,menu)

        menu.setTitle(label)
        menu.leo_label = label

        if parent:
            parent.addMenu(menu)
        else:
            self.menuBar.addMenu(menu)

        return menu
    #@-node:ekr.20081121105001.368:insert_cascade
    #@+node:ekr.20081121105001.369:new_menu (qt)
    def new_menu(self,parent,tearoff=False,label=''): # label is for debugging.

        """Wrapper for the Tkinter new_menu menu method."""

        c = self.c ; leoFrame = self.frame

        # g.trace(parent,label)

        # Parent can be None, in which case it will be added to the menuBar.
        menu = qtMenuWrapper(c,leoFrame,parent)

        return menu
    #@nonl
    #@-node:ekr.20081121105001.369:new_menu (qt)
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
    #@+node:ekr.20081121105001.373:createOpenWithMenu (QtMenu)
    def createOpenWithMenu(self,parent,label,index,amp_index):

        '''Create the File:Open With submenu.

        This is called from leoMenu.createOpenWithMenuFromTable.'''

        trace = False and not g.unitTesting
        c = self.c ; leoFrame = c.frame
        if trace: g.trace(parent,repr(label),repr(index),repr(amp_index))

        menu = self.new_menu(parent,tearoff=False,label=label)
            # Menu inherits from both QMenu and leoQtMenu.
        if menu:
            menu.insert_cascade(parent,index,label,menu,underline=amp_index)

        return menu
    #@-node:ekr.20081121105001.373:createOpenWithMenu (QtMenu)
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

        # hack:
        handler.workCtrl = leoFrame.stringTextWidget(c, 'spell-workctrl')

        self.tabName = tabName

        ui = c.frame.top.ui

        # self.createFrame()

        if not hasattr(ui, 'leo_spell_label'):
            self.handler.loaded = False
            return

        self.wordLabel = ui.leo_spell_label
        self.listBox = ui.leo_spell_listBox

        #self.createBindings()

        self.fillbox([])
    #@-node:ekr.20081121105001.380:leoQtSpellTab.__init__
    #@+node:ekr.20081121105001.381:createBindings TO DO
    def createBindings (self):
        pass
    #@-node:ekr.20081121105001.381:createBindings TO DO
    #@+node:ekr.20081121105001.382:createFrame (to be done in Qt designer)
    def createFrame (self):
        pass

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

        state = self.updateButtons()
        if state:
            self.handler.change()
        self.updateButtons()

    def onChangeThenFindButton(self,event=None):

        """Handle a click in the "Change, Find" button in the Spell tab."""

        state = self.updateButtons()
        if state:
            self.handler.change()
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

        ui = self.c.frame.top.ui

        self.suggestions = alts

        if not word:
            word = ""

        self.wordLabel.setText("Suggestions for: " + word)
        self.listBox.clear()
        if len(self.suggestions):
            self.listBox.addItems(self.suggestions)
            self.listBox.setCurrentRow(0)
    #@-node:ekr.20081121105001.396:fillbox
    #@+node:ekr.20081121105001.397:getSuggestion
    def getSuggestion(self):
        """Return the selected suggestion from the listBox."""

        idx = self.listBox.currentRow()
        value = self.suggestions[idx]
        return value
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

        c = self.c

        ui = c.frame.top.ui

        w = c.frame.body.bodyCtrl
        state = self.suggestions and w.hasSelection()

        ui.leo_spell_btn_Change.setDisabled(not state)
        ui.leo_spell_btn_FindChange.setDisabled(not state)

        # # state = g.choose(self.c.undoer.canRedo(),"normal","disabled")
        # # self.redoButton.configure(state=state)
        # # state = g.choose(self.c.undoer.canUndo(),"normal","disabled")
        # # self.undoButton.configure(state=state)

        # self.addButton.configure(state='normal')
        # self.ignoreButton.configure(state='normal')

        return state
    #@nonl
    #@-node:ekr.20081121105001.399:updateButtons (spellTab)
    #@-node:ekr.20081121105001.394:Helpers
    #@-others
#@-node:ekr.20081121105001.379:class leoQtSpellTab
#@+node:ekr.20081121105001.400:class leoQtTree (baseNativeTree)
class leoQtTree (baseNativeTree.baseNativeTreeWidget):

    """Leo qt tree class, a subclass of baseNativeTreeWidget."""

    callbacksInjected = False # A class var.

    #@    @+others
    #@+node:ekr.20090124174652.118: Birth (leoQtTree)
    #@+node:ekr.20090124174652.119:ctor
    def __init__(self,c,frame):

        # Init the base class.
        baseNativeTree.baseNativeTreeWidget.__init__(self,c,frame)

        # Components.
        self.headlineWrapper = leoQtHeadlineWidget # This is a class.
        self.treeWidget = w = frame.top.ui.treeWidget # An internal ivar.

        # Early inits...
        try: w.headerItem().setHidden(True)
        except Exception: pass

        w.setIconSize(QtCore.QSize(160,16))
    #@-node:ekr.20090124174652.119:ctor
    #@+node:ekr.20090124174652.120:qtTree.initAfterLoad
    def initAfterLoad (self):

        '''Do late-state inits.'''

        # Called by Leo's core.

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

        # We don't need this.  Hooray!
        # w.connect(self.treeWidget,QtCore.SIGNAL(
                # "itemChanged(QTreeWidgetItem*, int)"),
            # self.onItemChanged)

        w.connect(self.treeWidget,QtCore.SIGNAL(
                "itemCollapsed(QTreeWidgetItem*)"),
            self.onItemCollapsed)

        w.connect(self.treeWidget,QtCore.SIGNAL(
                "itemExpanded(QTreeWidgetItem*)"),
            self.onItemExpanded)

        self.ev_filter = leoQtEventFilter(c,w=self,tag='tree')
        tw.installEventFilter(self.ev_filter)

        c.setChanged(False)
    #@-node:ekr.20090124174652.120:qtTree.initAfterLoad
    #@-node:ekr.20090124174652.118: Birth (leoQtTree)
    #@+node:ekr.20090124174652.102:Widget-dependent helpers (leoQtTree)
    #@+node:ekr.20090126120517.11:Drawing
    def clear (self):
        '''Clear all widgets in the tree.'''
        w = self.treeWidget
        w.clear()

    def repaint (self):
        '''Repaint the widget.'''
        w = self.treeWidget
        w.repaint()
    #@nonl
    #@-node:ekr.20090126120517.11:Drawing
    #@+node:ekr.20090124174652.109:Icons
    #@+node:ekr.20090124174652.110:drawIcon
    def drawIcon (self,p):

        '''Redraw the icon at p.'''

        w = self.treeWidget
        itemOrTree = self.position2item(p) or w
        item = QtGui.QTreeWidgetItem(itemOrTree)
        icon = self.getIcon(p)
        self.setItemIcon(item,icon)

    #@-node:ekr.20090124174652.110:drawIcon
    #@+node:ekr.20090124174652.111:getIcon
    def getIcon(self,p):

        '''Return the proper icon for position p.'''

        p.v.iconVal = val = p.v.computeIcon()
        return self.getCompositeIconImage(p, val)

    def getCompositeIconImage(self, p, val):

        userIcons = self.c.editCommands.getIconList(p)
        statusIcon = self.getIconImage(val)

        if not userIcons:
            return statusIcon

        hash = [i['file'] for i in userIcons if i['where'] == 'beforeIcon']
        hash.append(str(val))
        hash.extend([i['file'] for i in userIcons if i['where'] == 'beforeHeadline'])
        hash = ':'.join(hash)

        if hash in g.app.gui.iconimages:
            return g.app.gui.iconimages[hash]

        images = [g.app.gui.getImageImage(i['file']) for i in userIcons
                 if i['where'] == 'beforeIcon']
        images.append(g.app.gui.getImageImage("box%02d.GIF" % val))
        images.extend([g.app.gui.getImageImage(i['file']) for i in userIcons
                      if i['where'] == 'beforeHeadline'])
        width = sum([i.width() for i in images])
        height = max([i.height() for i in images])

        pix = QtGui.QPixmap(width,height)
        pix.fill()
        pix.setAlphaChannel(pix)
        painter = QtGui.QPainter(pix)
        x = 0
        for i in images:
            painter.drawPixmap(x,(height-i.height())//2,i)
            x += i.width()
        painter.end()

        g.app.gui.iconimages[hash] = QtGui.QIcon(pix)

        return g.app.gui.iconimages[hash]
    #@-node:ekr.20090124174652.111:getIcon
    #@+node:ekr.20090124174652.112:setItemIconHelper (qtTree)
    def setItemIconHelper (self,item,icon):

        # Generates an item-changed event.
        if item:
            item.setIcon(0,icon)
    #@-node:ekr.20090124174652.112:setItemIconHelper (qtTree)
    #@-node:ekr.20090124174652.109:Icons
    #@+node:ekr.20090124174652.115:Items
    #@+node:ekr.20090124174652.67:childIndexOfItem
    def childIndexOfItem (self,item):

        parent = item and item.parent()

        if parent:
            n = parent.indexOfChild(item)
        else:
            w = self.treeWidget
            n = w.indexOfTopLevelItem(item)

        return n

    #@-node:ekr.20090124174652.67:childIndexOfItem
    #@+node:ekr.20090124174652.66:childItems
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
    #@-node:ekr.20090124174652.66:childItems
    #@+node:ekr.20090303095630.15:closeEditorHelper (leoQtTree)
    def closeEditorHelper (self,e,item):

        w = self.treeWidget

        if e:
            w.closeEditor(e,QtGui.QAbstractItemDelegate.NoHint)
            w.setCurrentItem(item)
    #@-node:ekr.20090303095630.15:closeEditorHelper (leoQtTree)
    #@+node:ekr.20090322190318.10:connectEditorWidget & helper
    def connectEditorWidget(self,e,item):

        c = self.c ; w = self.treeWidget

        if not e: return g.trace('can not happen: no e')

        wrapper = self.getWrapper(e,item)

        # Hook up the widget.
        def editingFinishedCallback(e=e,item=item,self=self,wrapper=wrapper):
            # g.trace(wrapper,g.callers(5))
            c = self.c ; w = self.treeWidget
            self.onHeadChanged(p=c.p,e=e)
            w.setCurrentItem(item)

        e.connect(e,QtCore.SIGNAL(
            "editingFinished()"),
            editingFinishedCallback)
    #@nonl
    #@-node:ekr.20090322190318.10:connectEditorWidget & helper
    #@+node:ekr.20090124174652.18:contractItem & expandItem
    def contractItem (self,item):

        # g.trace(g.callers(4))

        self.treeWidget.collapseItem(item)

    def expandItem (self,item):

        # g.trace(g.callers(4))

        self.treeWidget.expandItem(item)
    #@-node:ekr.20090124174652.18:contractItem & expandItem
    #@+node:ekr.20090124174652.104:createTreeEditorForItem (leoQtTree)
    def createTreeEditorForItem(self,item):

        trace = False and not g.unitTesting

        w = self.treeWidget
        w.setCurrentItem(item) # Must do this first.
        w.editItem(item)
        e = w.itemWidget(item,0)
        e.setObjectName('headline')
        self.connectEditorWidget(e,item)

        return e
    #@nonl
    #@-node:ekr.20090124174652.104:createTreeEditorForItem (leoQtTree)
    #@+node:ekr.20090124174652.103:createTreeItem
    def createTreeItem(self,p,parent_item):

        trace = False and not g.unitTesting

        w = self.treeWidget
        itemOrTree = parent_item or w
        item = QtGui.QTreeWidgetItem(itemOrTree)
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)

        if trace: g.trace(id(item),p.h,g.callers(4))
        try:
            g.visit_tree_item(self.c, p, item)
        except leoPlugins.TryNext:
            pass
        #print "item",item
        return item
    #@-node:ekr.20090124174652.103:createTreeItem
    #@+node:ekr.20090129062500.13:editLabelHelper (leoQtTree)
    def editLabelHelper (self,item,selectAll=False,selection=None):

        '''Called by nativeTree.editLabel to do
        gui-specific stuff.'''

        w = self.treeWidget
        w.setCurrentItem(item) # Must do this first.
        w.editItem(item)
            # Generates focus-in event that tree doesn't report.
        e = w.itemWidget(item,0) # A QLineEdit.

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
            self.connectEditorWidget(e,item) # Hook up the widget.

        return e
    #@-node:ekr.20090129062500.13:editLabelHelper (leoQtTree)
    #@+node:ekr.20090124174652.105:getCurrentItem
    def getCurrentItem (self):

        w = self.treeWidget
        return w.currentItem()
    #@-node:ekr.20090124174652.105:getCurrentItem
    #@+node:ekr.20090126120517.22:getItemText
    def getItemText (self,item):

        '''Return the text of the item.'''

        if item:
            return unicode(item.text(0))
        else:
            return '<no item>'
    #@nonl
    #@-node:ekr.20090126120517.22:getItemText
    #@+node:ekr.20090126120517.19:getParentItem
    def getParentItem(self,item):

        return item and item.parent()
    #@nonl
    #@-node:ekr.20090126120517.19:getParentItem
    #@+node:ville.20090525205736.3927:getSelectedItems
    def getSelectedItems(self):
        w = self.treeWidget    
        return w.selectedItems()
    #@nonl
    #@-node:ville.20090525205736.3927:getSelectedItems
    #@+node:ekr.20090124174652.106:getTreeEditorForItem (leoQtTree)
    def getTreeEditorForItem(self,item):

        '''Return the edit widget if it exists.
        Do *not* create one if it does not exist.'''

        w = self.treeWidget
        e = w.itemWidget(item,0)
        return e
    #@-node:ekr.20090124174652.106:getTreeEditorForItem (leoQtTree)
    #@+node:ekr.20090602083443.3817:getWrapper (leoQtTree)
    def getWrapper (self,e,item):

        '''Return headlineWrapper that wraps e (a QLineEdit).'''

        c = self.c

        if e:
            wrapper = self.editWidgetsDict.get(e)
            if not wrapper:
                wrapper = self.headlineWrapper(c,item,name='head',widget=e)
                self.editWidgetsDict[e] = wrapper

            return wrapper
        else:
            return None
    #@-node:ekr.20090602083443.3817:getWrapper (leoQtTree)
    #@+node:ekr.20090124174652.69:nthChildItem
    def nthChildItem (self,n,parent_item):

        children = self.childItems(parent_item)

        if n < len(children):
            item = children[n]
        else:
            # This is **not* an error.
            # It simply means that we need to redraw the tree.
            item = None

        return item
    #@-node:ekr.20090124174652.69:nthChildItem
    #@+node:ekr.20090201080444.12:scrollToItem
    def scrollToItem (self,item):

        w = self.treeWidget

        # g.trace(self.traceItem(item),g.callers(4))

        hPos,vPos = self.getScroll()

        w.scrollToItem(item,w.PositionAtCenter)

        self.setHScroll(0)
    #@-node:ekr.20090201080444.12:scrollToItem
    #@+node:ekr.20090124174652.107:setCurrentItemHelper (leoQtTree)
    def setCurrentItemHelper(self,item):

        w = self.treeWidget
        w.setCurrentItem(item)
    #@-node:ekr.20090124174652.107:setCurrentItemHelper (leoQtTree)
    #@+node:ekr.20090124174652.108:setItemText
    def setItemText (self,item,s):

        if item:
            item.setText(0,s)
    #@-node:ekr.20090124174652.108:setItemText
    #@-node:ekr.20090124174652.115:Items
    #@+node:ekr.20090124174652.122:Scroll bars (leoQtTree)
    #@+node:ekr.20090531084925.3779:getSCroll
    def getScroll (self):

        '''Return the hPos,vPos for the tree's scrollbars.'''

        w = self.treeWidget
        hScroll = w.horizontalScrollBar()
        vScroll = w.verticalScrollBar()
        hPos = hScroll.sliderPosition()
        vPos = vScroll.sliderPosition()
        return hPos,vPos
    #@-node:ekr.20090531084925.3779:getSCroll
    #@+node:ekr.20090531084925.3780:setH/VScroll
    def setHScroll (self,hPos):
        w = self.treeWidget
        hScroll = w.horizontalScrollBar()
        hScroll.setValue(hPos)

    def setVScroll (self,vPos):
        # g.trace(vPos)
        w = self.treeWidget
        vScroll = w.verticalScrollBar()
        vScroll.setValue(vPos)
    #@nonl
    #@-node:ekr.20090531084925.3780:setH/VScroll
    #@+node:ekr.20090531084925.3774:scrollDelegate (leoQtTree)
    def scrollDelegate (self,kind):

        '''Scroll a QTreeWidget up or down.
        kind is in ('down-line','down-page','up-line','up-page')
        '''
        c = self.c ; w = self.treeWidget
        vScroll = w.verticalScrollBar()
        h = w.size().height()
        lineSpacing = w.fontMetrics().lineSpacing()
        n = h/lineSpacing
        if   kind == 'down-half-page': delta = n/2
        elif kind == 'down-line':      delta = 1
        elif kind == 'down-page':      delta = n
        elif kind == 'up-half-page':   delta = -n/2
        elif kind == 'up-line':        delta = -1
        elif kind == 'up-page':        delta = -n
        else:
            delta = 0 ; g.trace('bad kind:',kind)
        val = vScroll.value()
        # g.trace(kind,n,h,lineSpacing,delta,val)
        vScroll.setValue(val+delta)
        c.treeWantsFocus()
    #@-node:ekr.20090531084925.3774:scrollDelegate (leoQtTree)
    #@-node:ekr.20090124174652.122:Scroll bars (leoQtTree)
    #@-node:ekr.20090124174652.102:Widget-dependent helpers (leoQtTree)
    #@-others
#@-node:ekr.20081121105001.400:class leoQtTree (baseNativeTree)
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
#@+node:ekr.20081121105001.469:class qtMenuWrapper (QMenu,leoQtMenu)
class qtMenuWrapper (QtGui.QMenu,leoQtMenu):

    def __init__ (self,c,frame,parent):

        assert c
        assert frame
        QtGui.QMenu.__init__(self,parent)
        leoQtMenu.__init__(self,frame)

    def __repr__(self):

        return '<qtMenuWrapper %s>' % self.leo_label or 'unlabeled'
#@-node:ekr.20081121105001.469:class qtMenuWrapper (QMenu,leoQtMenu)
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

        self.qtApp = app = QtGui.QApplication(sys.argv)

        self.bodyTextWidget  = leoQtBaseTextWidget
        self.plainTextWidget = leoQtBaseTextWidget

        self.iconimages = {} # Image cache set by getIconImage().

        self.mGuiName = 'qt'
    #@-node:ekr.20081121105001.474: qtGui.__init__
    #@+node:ekr.20081121105001.475:createKeyHandlerClass (qtGui)
    def createKeyHandlerClass (self,c,useGlobalKillbuffer=True,useGlobalRegisters=True):

        # Use the base class
        return leoKeys.keyHandlerClass(c,useGlobalKillbuffer,useGlobalRegisters)
    #@-node:ekr.20081121105001.475:createKeyHandlerClass (qtGui)
    #@+node:ekr.20090123150451.11:onActivateEvent (qtGui)
    def onActivateEvent (self,event,c,obj,tag):

        '''Put the focus in the body pane when the Leo window is
        activated, say as the result of an Alt-tab or click.'''

        trace = False and not g.unitTesting

        # This is called several times for each window activation.
        # We only need to set the focus once.

        if trace: g.trace(tag)

        if c.exists and tag == 'body':
            ### Possible bug fix.  Some claim that this redraw is irritating.
            ### c.redraw_now()
            c.bodyWantsFocusNow()
            c.outerUpdate() # Required because this is an event handler.
    #@-node:ekr.20090123150451.11:onActivateEvent (qtGui)
    #@+node:ekr.20090320101733.16:onDeactiveEvent (qtGui)
    def onDeactivateEvent (self,event,c,obj,tag):

        '''Put the focus in the body pane when the Leo window is
        activated, say as the result of an Alt-tab or click.'''

        trace = False and not g.unitTesting

        # This is called several times for each window activation.
        # Save the headline only once.

        if c.exists and tag.startswith('tree'):
            if trace: g.trace(tag,c.p)
            c.endEditing()
    #@nonl
    #@-node:ekr.20090320101733.16:onDeactiveEvent (qtGui)
    #@+node:ville.20090314101331.2:IPython embedding & mainloop
    def embed_ipython(self):
        import IPython.ipapi

        oargv = sys.argv
        # no c
        #args = c.config.getString('ipython_argv')
        args = None
        if args is None:
            argv = ['leo.py', '-p', 'sh']   
        sys.argv = argv         
        ses = IPython.ipapi.make_session()
        sys.argv = oargv
        # Does not return until IPython closes! IPython runs the leo mainloop
        ses.mainloop()    
    #@-node:ville.20090314101331.2:IPython embedding & mainloop
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
            if g.app.useIpython:
                self.embed_ipython()
                sys.exit(0)

            sys.exit(self.qtApp.exec_())
    #@-node:ekr.20081121105001.476:runMainLoop (qtGui)
    #@+node:ekr.20081121105001.477:destroySelf
    def destroySelf (self):
        QtCore.pyqtRemoveInputHook()
        self.qtApp.exit()
    #@nonl
    #@-node:ekr.20081121105001.477:destroySelf
    #@-node:ekr.20081121105001.473:  Birth & death (qtGui)
    #@+node:ekr.20081121105001.183:Clipboard (qtGui)
    def replaceClipboardWith (self,s):

        '''Replace the clipboard with the string s.'''

        trace = False and not g.unitTesting
        cb = self.qtApp.clipboard()
        if cb:
            # cb.clear()  # unnecessary, breaks on some Qt versions
            if type(s) == type(''):
                s = g.app.gui.toUnicode(s)

            QtGui.QApplication.processEvents()
            cb.setText(s)
            QtGui.QApplication.processEvents()
            if trace: g.trace(len(s),type(s))
        else:
            g.trace('no clipboard!')

    def getTextFromClipboard (self):

        '''Get a unicode string from the clipboard.'''

        trace = False and not g.unitTesting
        cb = self.qtApp.clipboard()
        if cb:
            QtGui.QApplication.processEvents()
            s = cb.text()
            if trace: g.trace (len(s),type(s))
            s = g.app.gui.toUnicode(s)
            return s
        else:
            g.trace('no clipboard!')
            return ''
    #@-node:ekr.20081121105001.183:Clipboard (qtGui)
    #@+node:ekr.20081121105001.478:Do nothings
    def color (self,color):
        return None

    def createRootWindow(self):
        pass

    def killGui(self,exitFlag=True):
        """Destroy a gui and terminate Leo if exitFlag is True."""

    def killPopupMenu(self):
        pass

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
    def runSaveFileDialog(self,initialfile='',title='Save',filetypes=[],defaultextension=''):

        """Create and run an Qt save file dialog ."""

        parent = None
        filter_ = self.makeFilter(filetypes)
        s = QtGui.QFileDialog.getSaveFileName(parent,title,os.curdir,filter_)
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
            g.es_print_error('%s\n%s\n\t%s' % (
                "The qt plugin requires calls to g.app.gui.scrolledMessageDialog to include 'c'",
                "as a keyword argument",
                g.callers()
            ))
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

        trace = False and not g.unitTesting

        if w:
            if trace: g.trace('leoQtGui',w,g.callers(4))
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
    #@+node:tbrown.20081229204443.10:getImageImage
    def getImageImage (self,name):

        '''Load the image and return it.'''

        try:
            fullname = g.os_path_finalize_join(g.app.loadDir,"..","Icons",name)

            pixmap = QtGui.QPixmap()
            pixmap.load(fullname)

            return pixmap

        except Exception:
            g.es("exception loading:",fullname)
            g.es_exception()
            return None
    #@-node:tbrown.20081229204443.10:getImageImage
    #@+node:ekr.20081123003126.2:getTreeImage (test)
    def getTreeImage (self,c,path):

        image = QtGui.QPixmap(path)

        if image.height() > 0 and image.width() > 0:
            return image,image.height()
        else:
            return None,None
    #@-node:ekr.20081123003126.2:getTreeImage (test)
    #@-node:ekr.20081121105001.495:Icons
    #@+node:ekr.20081121105001.498:Idle Time
    #@+node:ekr.20081121105001.499:qtGui.setIdleTimeHook & setIdleTimeHookAfterDelay
    timer = None

    def setIdleTimeHook (self,idleTimeHookHandler):

        # if self.root:
            # self.root.after_idle(idleTimeHookHandler)

        if not self.timer:
            self.timer = timer = QtCore.QTimer()

            def timerCallBack(self=self,handler=idleTimeHookHandler):
                # g.trace(self,idleTimeHookHandler)
                idleTimeHookHandler()

            timer.connect(timer,QtCore.SIGNAL("timeout()"),timerCallBack)

            # To make your application perform idle processing, use a QTimer with 0 timeout.
            # More advanced idle processing schemes can be achieved using processEvents().
            timer.start(1000)

    setIdleTimeHookAfterDelay = setIdleTimeHook
    #@-node:ekr.20081121105001.499:qtGui.setIdleTimeHook & setIdleTimeHookAfterDelay
    #@-node:ekr.20081121105001.498:Idle Time
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
    #@+node:ekr.20090406111739.14:Style Sheets
    #@+node:ekr.20090406111739.13:setStyleSetting (qtGui)
    def setStyleSetting(self,w,widgetKind,selector,val):

        '''Set the styleSheet for w to
           "%s { %s: %s; }  % (widgetKind,selector,val)"
        '''

        s = '%s { %s: %s; }' % (widgetKind,selector,val)

        try:
            w.setStyleSheet(s)
        except Exception:
            g.es_print('bad style sheet: %s' % s)
            g.es_exception()
    #@-node:ekr.20090406111739.13:setStyleSetting (qtGui)
    #@+node:ekr.20090406111739.12:setWidgetColor (qtGui)
    badWidgetColors = []

    def setWidgetColor (self,w,widgetKind,selector,colorName):

        if not colorName: return

        if QtGui.QColor(colorName).isValid():
            g.app.gui.setStyleSetting(w,widgetKind,selector,colorName)
        elif colorName not in self.badWidgetColors:
            self.badWidgetColors.append(colorName)
            g.es_print('bad widget color %s for %s' % (
                colorName,widgetKind),color='blue')
    #@-node:ekr.20090406111739.12:setWidgetColor (qtGui)
    #@-node:ekr.20090406111739.14:Style Sheets
    #@+node:ekr.20081121105001.502:toUnicode (qtGui)
    def toUnicode (self,s,encoding='utf-8',reportErrors=True):

        try:
            return unicode(s)
        except Exception:
            return ''
    #@nonl
    #@-node:ekr.20081121105001.502:toUnicode (qtGui)
    #@+node:ekr.20081121105001.503:widget_name (qtGui)
    def widget_name (self,w):

        # First try the widget's getName method.
        if not 'w':
            name = '<no widget>'
        elif hasattr(w,'getName'):
            name = w.getName()
        elif hasattr(w,'objectName'):
            name = str(w.objectName())
        elif hasattr(w,'_name'):
            name = w._name
        else:
            name = repr(w)

        # g.trace(id(w),name)
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
        if p and not buttonText: buttonText = p.h.strip()
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
            self.listWidget.addItem(n.h)



#@-node:ekr.20081121105001.512:quickheadlines
#@-node:ekr.20081121105001.509:Non-essential
#@+node:ekr.20081121105001.513:Key handling
#@+node:ekr.20081121105001.514:class leoKeyEvent
class leoKeyEvent:

    '''A wrapper for wrapper for qt events.

    This does *not* override leoGui.leoKeyevent because
    it is a separate class, not member of leoQtGui.'''

    def __init__ (self,event,c,w,ch,tkKey,stroke):

        # g.trace('ch: %s, tkKey: %s' % (repr(ch),repr(tkKey)))

        # Last minute-munges to keysym.
        if tkKey in ('Return','Tab','Escape'):
            ch = tkKey

        # The main ivars.
        self.actualEvent = event
        self.c      = c
        self.char   = ch
        self.keysym = ch
        self.stroke = stroke
        self.w = self.widget = w # A leoQtX object

        # Auxiliary info.
        self.x      = hasattr(event,'x') and event.x or 0
        self.y      = hasattr(event,'y') and event.y or 0
        # Support for fastGotoNode plugin
        self.x_root = hasattr(event,'x_root') and event.x_root or 0
        self.y_root = hasattr(event,'y_root') and event.y_root or 0

        # g.trace('qt.leoKeyEvent: %s' % repr(self))

    def __repr__ (self):

        return 'qtGui.leoKeyEvent: stroke: %s' % (repr(self.stroke))

        # return 'qtGui.leoKeyEvent: stroke: %s, char: %s, keysym: %s' % (
            # repr(self.stroke),repr(self.char),repr(self.keysym))
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
    #@+node:ekr.20081121105001.180: ctor
    def __init__(self,c,w,tag=''):

        # Init the base class.
        QtCore.QObject.__init__(self)

        self.c = c
        self.w = w      # A leoQtX object, *not* a Qt object.
        self.tag = tag

        # Debugging.
        self.keyIsActive = False

        # Pretend there is a binding for these characters.
        close_flashers = c.config.getString('close_flash_brackets') or ''
        open_flashers  = c.config.getString('open_flash_brackets') or ''
        self.flashers = open_flashers + close_flashers


    #@-node:ekr.20081121105001.180: ctor
    #@+node:ekr.20090407101640.10:char2tkName
    char2tkNameDict = {
        # Part 1: same as k.guiBindNamesDict
        "&" : "ampersand",
        "^" : "asciicircum",
        "~" : "asciitilde",
        "*" : "asterisk",
        "@" : "at",
        "\\": "backslash",
        "|" : "bar",
        "{" : "braceleft",
        "}" : "braceright",
        "[" : "bracketleft",
        "]" : "bracketright",
        ":" : "colon",  
        "," : "comma",
        "$" : "dollar",
        "=" : "equal",
        "!" : "exclam",
        ">" : "greater",
        "<" : "less",
        "-" : "minus",
        "#" : "numbersign",
        '"' : "quotedbl",
        "'" : "quoteright",
        "(" : "parenleft",
        ")" : "parenright", 
        "%" : "percent",
        "." : "period",     
        "+" : "plus",
        "?" : "question",
        "`" : "quoteleft",
        ";" : "semicolon",
        "/" : "slash",
        " " : "space",      
        "_" : "underscore",
        # Part 2: special Qt translations.
        'Backspace':'BackSpace',
        'Backtab':  'Tab', # The shift mod will convert to 'Shift+Tab',
        'Esc':      'Escape',
        'Del':      'Delete',
        'Ins':      'Return',
        # Comment these out to pass the key to the QTextWidget.
        # Use these to enable Leo's page-up/down commands.
        'PgDown':    'Next',
        'PgUp':      'Prior',
        # New entries.  These simplify code.
        'Down':'Down','Left':'Left','Right':'Right','Up':'Up',
        'End':'End',
        'F1':'F1','F2':'F2','F3':'F3','F4':'F4','F5':'F5',
        'F6':'F6','F7':'F7','F8':'F8','F9':'F9',
        'F10':'F10','F11':'F11','F12':'F12',
        'Home':'Home',
        'Return':'Return',
        # 'Tab':'Tab',
        'Tab':'\t', # A hack for QLineEdit.
        # Unused: Break, Caps_Lock,Linefeed,Num_lock
    }

    def char2tkName (self,ch):
        val = self.char2tkNameDict.get(ch)
        # g.trace(repr(ch),repr(val))
        return val
    #@-node:ekr.20090407101640.10:char2tkName
    #@+node:ekr.20081121105001.168:eventFilter
    def eventFilter(self, obj, event):

        trace = False and not g.unitTesting
        verbose = False
        traceEvent = False
        traceKey = False
        traceFocus = True
        c = self.c ; k = c.k
        eventType = event.type()
        ev = QtCore.QEvent
        gui = g.app.gui
        aList = []
        kinds = [ev.ShortcutOverride,ev.KeyPress,ev.KeyRelease]

        if trace and traceFocus: self.traceFocus(eventType,obj)

        # A hack. QLineEdit generates ev.KeyRelease only.
        if eventType in (ev.KeyPress,ev.KeyRelease):
            p = c.currentPosition()
            isEditWidget = obj == c.frame.tree.edit_widget(p)
            self.keyIsActive = g.choose(
                isEditWidget,
                eventType == ev.KeyRelease,
                eventType == ev.KeyPress)
        else:
            self.keyIsActive = False

        if eventType == ev.WindowActivate:
            gui.onActivateEvent(event,c,obj,self.tag)
            override = False ; tkKey = None
        elif eventType == ev.WindowDeactivate:
            gui.onDeactivateEvent(event,c,obj,self.tag)
            override = False ; tkKey = None
        elif eventType in kinds:
            tkKey,ch,ignore = self.toTkKey(event)
            aList = c.k.masterGuiBindingsDict.get('<%s>' %tkKey,[])
            if ignore:
                override = False
            elif self.isSpecialOverride(tkKey,ch):
                override = True
            elif k.inState():
                override = not ignore # allow all keystrokes.
            else:
                override = len(aList) > 0
        else:
            override = False ; tkKey = '<no key>'
            if self.tag == 'body':
                if eventType == ev.FocusIn:
                    c.frame.body.onFocusIn(obj)
                elif eventType == ev.FocusOut:
                    c.frame.body.onFocusOut(obj)
        if self.keyIsActive:
            stroke = self.toStroke(tkKey,ch)
            if override:
                if trace and traceKey and not ignore:
                    g.trace('bound',repr(stroke)) # repr(aList))
                w = self.w # Pass the wrapper class, not the wrapped widget.
                leoEvent = leoKeyEvent(event,c,w,ch,tkKey,stroke)
                ret = k.masterKeyHandler(leoEvent,stroke=stroke)
                c.outerUpdate()
            else:
                if trace and traceKey and verbose: g.trace(self.tag,'unbound',tkKey,stroke)

        if trace and traceEvent: self.traceEvent(obj,event,tkKey,override)

        return override
    #@-node:ekr.20081121105001.168:eventFilter
    #@+node:ekr.20081121105001.182:isSpecialOverride (simplified)
    def isSpecialOverride (self,tkKey,ch):

        '''Return True if tkKey is a special Tk key name.
        '''

        return tkKey or ch in self.flashers
    #@-node:ekr.20081121105001.182:isSpecialOverride (simplified)
    #@+node:ekr.20081121105001.172:qtKey
    def qtKey (self,event):

        '''Return the components of a Qt key event.'''

        trace = False and not g.unitTesting
        keynum = event.key()
        text   = event.text() # This is the unicode text.
        toString = QtGui.QKeySequence(keynum).toString()
        toUnicode = unicode

        try:
            ch1 = chr(keynum)
        except ValueError:
            ch1 = ''

        try:
            ch = toUnicode(ch1)
        except UnicodeError:
            ch = ch1

        text     = toUnicode(text)
        toString = toUnicode(toString)

        if trace and self.keyIsActive: g.trace(
            'keynum %s ch %s ch1 %s toString %s' % (
                repr(keynum),repr(ch),repr(ch1),repr(toString)))

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
    #@+node:ekr.20081121105001.174:tkKey
    def tkKey (self,event,mods,keynum,text,toString,ch):

        '''Carefully convert the Qt key to a 
        Tk-style binding compatible with Leo's core
        binding dictionaries.'''

        trace = False and not g.unitTesting
        ch1 = ch # For tracing.

        # Convert '&' to 'ampersand', etc.
        # *Do* allow shift-bracketleft, etc.
        ch2 = self.char2tkName(ch or toString)
        if ch2: ch = ch2 
        if not ch: ch = ''

        if 'Shift' in mods:
            if len(ch) == 1 and ch.isalpha():
                mods.remove('Shift')
                ch = ch.upper()
        elif len(ch) == 1:
            ch = ch.lower()

        if ('Alt' in mods or 'Control' in mods) and ch and ch in string.digits:
            mods.append('Key')

        # *Do* allow bare mod keys, so they won't be passed on.
        tkKey = '%s%s%s' % ('-'.join(mods),mods and '-' or '',ch)

        if trace: g.trace(
            'text: %s toString: %s ch1: %s ch: %s' % (
            repr(text),repr(toString),repr(ch1),repr(ch)))

        ignore = not ch # Essential
        ch = text or toString
        return tkKey,ch,ignore
    #@-node:ekr.20081121105001.174:tkKey
    #@+node:ekr.20081121105001.169:toStroke
    def toStroke (self,tkKey,ch):

        trace = False and not g.unitTesting
        k = self.c.k ; s = tkKey

        special = ('Alt','Ctrl','Control',)
        isSpecial = [True for z in special if s.find(z) > -1]

        if 0:
            if isSpecial:
                pass # s = s.replace('Key-','')
            else:
                # Keep the Tk spellings for special keys.
                ch2 = k.guiBindNamesDict.get(ch)
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
                if override:
                    g.trace(
                        'tag: %s, kind: %s, in-state: %s, key: %s, override: %s' % (
                        self.tag,kind,repr(c.k.inState()),tkKey,override))
                return

        # if trace: g.trace(self.tag,
            # 'bound in state: %s, key: %s, returns: %s' % (
            # k.getState(),tkKey,ret))

        if False and eventType not in ignore:
            g.trace('%3s:%s' % (eventType,'unknown'))
    #@-node:ekr.20081121105001.179:traceEvent
    #@+node:ekr.20090407080217.1:traceFocus
    def traceFocus (self,eventType,obj):

        ev = QtCore.QEvent

        table = (
            (ev.FocusIn,        'focus-in'),
            (ev.FocusOut,       'focus-out'),
            (ev.WindowActivate, 'activate'),
            (ev.WindowDeactivate,'deactivate'),
        )

        for evKind,kind in table:
            if eventType == evKind:
                g.trace('%11s %s %s %s' % (
                    (kind,id(obj),
                    # event.reason(),
                    obj.objectName(),obj)))
                    # g.app.gui.widget_name(obj) or obj)))

        # else: g.trace('unknown kind: %s' % eventType)
    #@-node:ekr.20090407080217.1:traceFocus
    #@-others
#@-node:ekr.20081121105001.166:class leoQtEventFilter
#@-node:ekr.20081121105001.513:Key handling
#@+node:ekr.20081204090029.1:Syntax coloring
#@+node:ekr.20081205131308.15:leoQtColorizer
# This is c.frame.body.colorizer

class leoQtColorizer:

    '''An adaptor class that interfaces Leo's core to two class:

    1. a subclass of QSyntaxHighlighter,

    2. the jEditColorizer class that contains the
       pattern-matchin code from the threading colorizer plugin.'''

    #@    @+others
    #@+node:ekr.20081205131308.16: ctor (leoQtColorizer)
    def __init__ (self,c,w):

        # g.pr('leoQtColorizer.__init__',c,w,g.callers(4))

        self.c = c
        self.w = w

        # Step 1: create the ivars.
        self.count = 0 # For unit testing.
        self.enabled = c.config.getBool('use_syntax_coloring')
        self.error = False # Set if there is an error in jeditColorizer.recolor
        self.flag = True # Per-node enable/disable flag.
        self.killColorFlag = False
        self.language = 'python' # set by scanColorDirectives.

        # Step 2: create the highlighter.
        self.highlighter = leoQtSyntaxHighlighter(c,w,colorizer=self)
        self.colorer = self.highlighter.colorer

        # Step 3: finish enabling.
        if self.enabled:
            self.enabled = hasattr(self.highlighter,'currentBlock')
    #@-node:ekr.20081205131308.16: ctor (leoQtColorizer)
    #@+node:ekr.20081205131308.18:colorize (leoQtColorizer)
    def colorize(self,p,incremental=False,interruptable=True):

        '''The main colorizer entry point.'''

        trace = False and not g.unitTesting
        if trace: g.trace(p.h)

        self.count += 1 # For unit testing.

        if self.enabled:
            oldLanguage = self.language
            self.updateSyntaxColorer(p) # sets self.flag.
            if self.flag and (oldLanguage != self.language or not incremental):
                self.highlighter.rehighlight(p)

        return "ok" # For unit testing.
    #@-node:ekr.20081205131308.18:colorize (leoQtColorizer)
    #@+node:ekr.20090302125215.10:enable/disable
    def disable (self,p):

        g.trace(g.callers(4))

        if self.enabled:
            self.flag = False
            self.enabled = False
            self.highlighter.rehighlight(p) # Do a full recolor (to black)

    def enable (self,p):

        g.trace(g.callers(4))

        if not self.enabled:
            self.enabled = True
            self.flag = True
            # Do a full recolor, but only if we aren't changing nodes.
            if self.c.currentPosition() == p:
                self.highlighter.rehighlight(p)
    #@-node:ekr.20090302125215.10:enable/disable
    #@+node:ekr.20081207061047.10:minor entry points
    def interrupt(self):
        pass

    def isSameColorState (self):
        return True # Disable some logic in leoTree.select.

    def kill (self):
        pass
    #@-node:ekr.20081207061047.10:minor entry points
    #@+node:ekr.20090226105328.12:scanColorDirectives (leoQtColorizer)
    def scanColorDirectives(self,p):

        trace = False and not g.unitTesting

        p = p.copy() ; c = self.c
        if c == None: return # self.c may be None for testing.

        self.language = language = c.target_language
        self.rootMode = None # None, "code" or "doc"

        for p in p.self_and_parents_iter():
            theDict = g.get_directives_dict(p)
            #@        << Test for @language >>
            #@+node:ekr.20090226105328.13:<< Test for @language >>
            if 'language' in theDict:
                s = theDict["language"]
                i = g.skip_ws(s,0)
                j = g.skip_c_id(s,i)
                self.language = s[i:j].lower()
                break
            #@-node:ekr.20090226105328.13:<< Test for @language >>
            #@nl
            #@        << Test for @root, @root-doc or @root-code >>
            #@+node:ekr.20090226105328.14:<< Test for @root, @root-doc or @root-code >>
            if 'root' in theDict and not self.rootMode:

                s = theDict["root"]
                if g.match_word(s,0,"@root-code"):
                    self.rootMode = "code"
                elif g.match_word(s,0,"@root-doc"):
                    self.rootMode = "doc"
                else:
                    doc = c.config.at_root_bodies_start_in_doc_mode
                    self.rootMode = g.choose(doc,"doc","code")
            #@nonl
            #@-node:ekr.20090226105328.14:<< Test for @root, @root-doc or @root-code >>
            #@nl

        if trace: g.trace(self.language,g.callers(4))

        return self.language # For use by external routines.
    #@-node:ekr.20090226105328.12:scanColorDirectives (leoQtColorizer)
    #@+node:ekr.20090216070256.11:setHighlighter
    def setHighlighter (self,p):

        trace = False and not g.unitTesting
        if trace: g.trace(p.h,g.callers(4))

        c = self.c

        if self.enabled:
            self.flag = self.updateSyntaxColorer(p)
            if self.flag:
                # Do a full recolor, but only if we aren't changing nodes.
                if self.c.currentPosition() == p:
                    self.highlighter.rehighlight(p)
            else:
                self.highlighter.rehighlight(p) # Do a full recolor (to black)
        else:
            self.highlighter.rehighlight(p) # Do a full recolor (to black)

        # g.trace(flag,p.h)
    #@-node:ekr.20090216070256.11:setHighlighter
    #@+node:ekr.20081205131308.24:updateSyntaxColorer
    def updateSyntaxColorer (self,p):

        trace = False and not g.unitTesting
        p = p.copy()

        # self.flag is True unless an unambiguous @nocolor is seen.
        self.flag = self.useSyntaxColoring(p)
        self.scanColorDirectives(p)

        if trace: g.trace(self.flag,self.language,p.h)
        return self.flag
    #@-node:ekr.20081205131308.24:updateSyntaxColorer
    #@+node:ekr.20081205131308.23:useSyntaxColoring & helper
    def useSyntaxColoring (self,p):

        """Return True unless p is unambiguously under the control of @nocolor."""

        if self.checkStartKillColor():
            return False

        trace = False and not g.unitTesting
        if not p:
            if trace: g.trace('no p',repr(p))
            return False

        p = p.copy()
        first = True ; kind = None ; val = True
        self.killColorFlag = False
        for p in p.self_and_parents_iter():
            d = self.findColorDirectives(p)
            color,no_color = 'color' in d,'nocolor' in d
            # An @nocolor-node in the first node disabled coloring.
            if first and 'nocolor-node' in d:
                kind = '@nocolor-node'
                self.killColorFlag = True
                val = False ; break
            # A killcolor anywhere disables coloring.
            elif 'killcolor' in d:
                kind = '@killcolor %s' % p.h
                self.killColorFlag = True
                val = False ; break
            # A color anywhere in the target enables coloring.
            elif color and first:
                kind = 'color %s' % p.h
                val = True ; break
            # Otherwise, the @nocolor specification must be unambiguous.
            elif no_color and not color:
                kind = '@nocolor %s' % p.h
                val = False ; break
            elif color and not no_color:
                kind = '@color %s' % p.h
                val = True ; break
            first = False

        if trace: g.trace(val,kind)
        return val
    #@+node:ekr.20090214075058.12:findColorDirectives
    color_directives_pat = re.compile(
        # Order is important: put longest matches first.
        r'(^@color|^@killcolor|^@nocolor-node|^@nocolor)'
        ,re.MULTILINE)

    def findColorDirectives (self,p):

        '''Scan p for @color, @killcolor, @nocolor and @nocolor-node directives.

        Return a dict containing pointers to the start of each directive.'''

        trace = False and not g.unitTesting

        d = {}
        anIter = self.color_directives_pat.finditer(p.b)
        for m in anIter:
            # Remove leading '@' for compatibility with
            # functions in leoGlobals.py.
            word = m.group(0)[1:]
            d[word] = word

        if trace: g.trace(d)
        return d
    #@-node:ekr.20090214075058.12:findColorDirectives
    #@-node:ekr.20081205131308.23:useSyntaxColoring & helper
    #@+node:ville.20090319181106.135:checkStartKillColor
    def checkStartKillColor(self):
        # note that we avoid the slow getAllText at all cost
        doc = self.w.document()
        fb = doc.begin() 
        firstline = unicode(fb.text())
        if firstline.startswith('@killcolor'):
            #g.trace('have @killcolor')
            self.killColorFlag = True
            return True

        return False

    #@-node:ville.20090319181106.135:checkStartKillColor
    #@-others

#@-node:ekr.20081205131308.15:leoQtColorizer
#@+node:ekr.20081205131308.27:leoQtSyntaxHighlighter
# This is c.frame.body.colorizer.highlighter

class leoQtSyntaxHighlighter(QtGui.QSyntaxHighlighter):

    '''A subclass of QSyntaxHighlighter that overrides
    the highlightBlock and rehighlight methods.

    All actual syntax coloring is done in the jeditColorer class.'''

    #@    @+others
    #@+node:ekr.20081205131308.1:ctor (leoQtSyntaxHighlighter)
    def __init__ (self,c,w,colorizer):

        self.c = c
        self.w = w

        # print('leoQtSyntaxHighlighter.__init__',w)

        # Not all versions of Qt have the crucial currentBlock method.
        self.hasCurrentBlock = hasattr(self,'currentBlock')

        # Init the base class.
        QtGui.QSyntaxHighlighter.__init__(self,w)

        self.colorizer = colorizer

        self.colorer = jEditColorizer(c,
            colorizer=colorizer,
            highlighter=self,
            w=c.frame.body.bodyCtrl)
    #@-node:ekr.20081205131308.1:ctor (leoQtSyntaxHighlighter)
    #@+node:ekr.20090216070256.10:enable/disable & disabledRehighlight
    # def enable (self,p):

        # if not self.enabled:
            # self.enabled = True
            # self.colorer.flag = True
            # # Do a full recolor, but only if we aren't changing nodes.
            # if self.c.currentPosition() == p:
                # self.rehighlight(p)

    # def disable (self,p):

        # if self.enabled:
            # self.enabled = False
            # self.colorer.flag = False
            # self.rehighlight(p) # Do a full recolor (to black)
    #@nonl
    #@-node:ekr.20090216070256.10:enable/disable & disabledRehighlight
    #@+node:ekr.20081205131308.11:highlightBlock
    def highlightBlock (self,s):
        """ Called by QSyntaxHiglighter """

        if self.hasCurrentBlock and not self.colorizer.killColorFlag:
            colorer = self.colorer
            s = unicode(s)
            colorer.recolor(s)
    #@-node:ekr.20081205131308.11:highlightBlock
    #@+node:ekr.20081206062411.15:rehighlight
    def rehighlight (self,p):

        '''Override base rehighlight method'''

        trace = False and not g.unitTesting
        verbose = False

        c = self.c ; tree = c.frame.tree
        self.w = c.frame.body.bodyCtrl.widget
        s = p.b
        self.colorer.init(p,s)
        n = self.colorer.recolorCount
        if trace: g.trace(p.h)

        # Call the base class method, but *only*
        # if the crucial 'currentBlock' method exists.
        if self.colorizer.enabled and self.hasCurrentBlock:
            # Lock out onTextChanged.
            old_selecting = c.frame.tree.selecting
            try:
                c.frame.tree.selecting = True
                QtGui.QSyntaxHighlighter.rehighlight(self)
            finally:
                c.frame.tree.selecting = old_selecting

        if trace and verbose:
            g.trace('%s calls to recolor' % (
                self.colorer.recolorCount-n))
    #@-node:ekr.20081206062411.15:rehighlight
    #@-others
#@-node:ekr.20081205131308.27:leoQtSyntaxHighlighter
#@+node:ekr.20081205131308.48:class jeditColorizer
# This is c.frame.body.colorizer.highlighter.colorer

class jEditColorizer:

    '''This class contains the pattern matching code
    from the threading_colorizer plugin, adapted for
    use with QSyntaxHighlighter.'''

    #@    @+others
    #@+node:ekr.20081205131308.49: Birth & init
    #@+node:ekr.20081205131308.50:__init__ (jeditColorizer)
    def __init__(self,c,colorizer,highlighter,w):

        # Basic data...
        self.c = c
        self.colorizer = colorizer
        self.highlighter = highlighter # a QSyntaxHighlighter
        self.p = None
        self.w = w
        assert(w == self.c.frame.body.bodyCtrl)

        # Used by recolor and helpers...
        self.all_s = '' # The cached string to be colored.
        self.actualColorDict = {} # Used only by setTag.
        self.global_i,self.global_j = 0,0 # The global bounds of colorizing.
        self.global_offset = 0
        self.hyperCount = 0
        self.initFlag = False # True if recolor must reload self.all_s.
        self.defaultState = u'default-state:' # The name of the default state.
        self.minimalMatch = ''
        self.nextState = 1 # Dont use 0.
        self.stateDict = {} # Keys are state numbers, values state names.
        self.stateNameDict = {} # Keys are state names, values are state numbers.

        # Attributes dict ivars: defaults are as shown...
        self.default = 'null'
        self.digit_re = ''
        self.escape = ''
        self.highlight_digits = True
        self.ignore_case = True
        self.no_word_sep = ''
        # Config settings...
        self.showInvisibles = False # True: show "invisible" characters.
        self.underline_undefined = c.config.getBool("underline_undefined_section_names")
        self.use_hyperlinks = c.config.getBool("use_hyperlinks")
        # Debugging...
        self.count = 0 # For unit testing.
        self.allow_mark_prev = True # The new colorizer tolerates this nonsense :-)
        self.tagCount = 0
        self.trace = False or c.config.getBool('trace_colorizer')
        self.trace_leo_matches = False
        self.trace_match_flag = False # (Useful) True: trace all matching methods.
        self.verbose = False
        # Profiling...
        self.recolorCount = 0 # Total calls to recolor
        self.stateCount = 0 # Total calls to setCurrentState
        self.totalChars = 0 # The total number of characters examined by recolor.
        self.totalStates = 0
        self.maxStateNumber = 0
        self.totalKeywordsCalls = 0
        self.totalLeoKeywordsCalls = 0
        # Mode data...
        self.defaultRulesList = []
        self.importedRulesets = {}
        self.prev = None # The previous token.
        self.fonts = {} # Keys are config names.  Values are actual fonts.
        self.keywords = {} # Keys are keywords, values are 0..5.
        self.modes = {} # Keys are languages, values are modes.
        self.mode = None # The mode object for the present language.
        self.modeBunch = None # A bunch fully describing a mode.
        self.modeStack = []
        self.rulesDict = {}
        # self.defineAndExtendForthWords()
        self.word_chars = {} # Inited by init_keywords().
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
    #@-node:ekr.20081205131308.50:__init__ (jeditColorizer)
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
            ('@',  self.match_at_killcolor,True),
            ('@',  self.match_at_nocolor,  True),
            ('@',  self.match_at_nocolor_node,True),
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
            if rule not in theList:
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
            for name in ('%s_%s' % (self.colorizer.language,option_name),(option_name)):
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
                c.config.getColor('%s_%s' % (self.colorizer.language,option_name)) or
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
    #@+node:ekr.20081205131308.74:init (jeditColorizer)
    def init (self,p,s):

        trace = False and not g.unitTesting

        if p: self.p = p.copy()
        self.all_s = s or ''

        if trace: g.trace('***',p and p.h,len(self.all_s),g.callers(4))

        # State info.
        self.all_s = s
        self.global_i,self.global_j = 0,0
        self.global_offset = 0
        self.initFlag = False
        self.nextState = 1 # Dont use 0.
        self.stateDict = {}
        self.stateNameDict = {}
        self.init_mode(self.colorizer.language)

        # Used by matchers.
        self.prev = None

        ####
        # self.configure_tags() # Must do this every time to support multiple editors.
    #@-node:ekr.20081205131308.74:init (jeditColorizer)
    #@+node:ekr.20081205131308.55:init_mode & helpers
    def init_mode (self,name):

        '''Name may be a language name or a delegate name.'''

        trace = False and not g.unitTesting

        if not name: return False
        language,rulesetName = self.nameToRulesetName(name)
        bunch = self.modes.get(rulesetName)
        if bunch:
            if trace: g.trace('found',language,rulesetName)
            self.initModeFromBunch(bunch)
            return True
        else:
            if trace: g.trace('****',language,rulesetName)
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
            self.colorizer.language = language
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
                language        = self.colorizer.language,
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

        # Create a temporary chars list.  It will be converted to a dict later.
        chars = [g.toUnicode(ch,encoding='UTF-8')
            for ch in (string.letters + string.digits)]

        for key in d.keys():
            for ch in key:
                if ch not in chars:
                    chars.append(g.toUnicode(ch,encoding='UTF-8'))

        # jEdit2Py now does this check, so this isn't really needed.
        # But it is needed for forth.py.
        for ch in (' ', '\t'):
            if ch in chars:
                # g.es_print('removing %s from word_chars' % (repr(ch)))
                chars.remove(ch)

        # g.trace(self.colorizer.language,[str(z) for z in chars])

        # Convert chars to a dict for faster access.
        self.word_chars = {}
        for z in chars:
            self.word_chars[z] = z
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
        self.colorizer.language = bunch.language
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
            if not d.get(self.colorizer.language):
                d [self.colorizer.language] = delims
                # g.trace(self.colorizer.language,'delims:',repr(delims))
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
    #@-node:ekr.20081205131308.49: Birth & init
    #@+node:ekr.20081206062411.13:colorRangeWithTag
    def colorRangeWithTag (self,s,i,j,tag,delegate='',exclude_match=False):

        '''Actually colorize the selected range.

        This is called whenever a pattern matcher succeed.'''

        trace = False
        if self.colorizer.killColorFlag or not self.colorizer.flag: return

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
                    self.setTag(tag,s,i,i+1)
                    i += 1
                assert i > progress
            bunch = self.modeStack.pop()
            self.initModeFromBunch(bunch)
        elif not exclude_match:
            self.setTag(tag,s,i,j)
    #@nonl
    #@-node:ekr.20081206062411.13:colorRangeWithTag
    #@+node:ekr.20081205131308.87:pattern matchers
    #@@nocolor-node
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
            self.colorizer.flag = True # Enable coloring.
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
        if g.match(s,i,'@nocolor-'):
            return 0
        if not g.match_word(s,i,'@nocolor'):
            return 0

        j = i + len('@nocolor')
        k = s.find('\n@color',j)
        if k == -1:
            # No later @color: don't color the @nocolor directive.
            self.colorizer.flag = False # Disable coloring.
            return len(s) - j
        else:
            # A later @color: do color the @nocolor directive.
            self.colorRangeWithTag(s,i,j,'leoKeyword')
            self.colorizer.flag = False # Disable coloring.
            return k+2-j

    #@-node:ekr.20081205131308.40:match_at_nocolor
    #@+node:ekr.20090308163450.10:match_at_killcolor (NEW)
    def match_at_killcolor (self,s,i):

        if self.trace_leo_matches: g.trace()

        # Only matches at start of line.
        if i != 0 and s[i-1] != '\n':
            return 0

        tag = '@killcolor'

        if g.match_word(s,i,tag):
            j = i + len(tag)
            self.colorizer.flag = False # Disable coloring.
            self.colorizer.killColorFlag = True
            self.minimalMatch = tag
            return len(s) - j # Match everything.
        else:
            return 0

    #@-node:ekr.20090308163450.10:match_at_killcolor (NEW)
    #@+node:ekr.20090308163450.11:match_at_nocolor_node (NEW)
    def match_at_nocolor_node (self,s,i):

        if self.trace_leo_matches: g.trace()

        # Only matches at start of line.
        if i != 0 and s[i-1] != '\n':
            return 0

        tag = '@nocolor-node'

        if g.match_word(s,i,tag):
            j = i + len(tag)
            self.colorizer.flag = False # Disable coloring.
            self.colorizer.killColorFlag = True
            self.minimalMatch = tag
            return len(s) - j # Match everything.
        else:
            return 0
    #@-node:ekr.20090308163450.11:match_at_nocolor_node (NEW)
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
            self.minimalMatch = '@doc'
            self.colorRangeWithTag(s,i,j,'leoKeyword')
        elif g.match(s,i,'@') and (i+1 >= len(s) or s[i+1] in (' ','\t','\n')):
            j = i + 1
            self.minimalMatch = '@'
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

        self.totalLeoKeywordsCalls += 1

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
            result = j-i+1 # Bug fix: skip the last character.
            self.trace_match(kind,s,i,j)
            return result
        else:
            return -(j-i+1) # An important optimization.
    #@-node:ekr.20081205131308.42:match_leo_keywords
    #@+node:ekr.20081205131308.43:match_section_ref
    def match_section_ref (self,s,i):

        if self.trace_leo_matches: g.trace()
        c = self.c ; p = c.currentPosition()
        w = self.w

        if not g.match(s,i,'<<'):
            return 0
        k = g.find_on_line(s,i+2,'>>')
        if k is not None:
            j = k + 2
            self.colorRangeWithTag(s,i,i+2,'nameBrackets')
            ref = g.findReference(c,s[i:j],p)
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
                    w.tag_add(tagName,i+2,j)

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
            self.minimalMatch = seq
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
            self.minimalMatch = s[i:i+n] # Bug fix: 2009/3/2.
            return j - i
        else:
            return 0
    #@nonl
    #@-node:ekr.20081205131308.89:match_eol_span_regexp
    #@+node:ekr.20081205131308.91:match_keywords
    # This is a time-critical method.
    def match_keywords (self,s,i):

        '''Succeed if s[i:] is a keyword.'''

        self.totalKeywordsCalls += 1

        # Important.  Return -len(word) for failure greatly reduces
        # the number of times this method is called.

        # We must be at the start of a word.
        if i > 0 and s[i-1] in self.word_chars:
            return 0

        trace = False

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
            if trace: g.trace('success',word,kind,j-i)
            # g.trace('word in self.keywordsDict.keys()',word in self.keywordsDict.keys())
            self.trace_match(kind,s,i,j)
            return result
        else:
            if trace: g.trace('fail',word,kind)
            # g.trace('word in self.keywordsDict.keys()',word in self.keywordsDict.keys())
            return -len(word) # An important new optimization.
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
            self.minimalMatch = pattern
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
            self.minimalMatch = pattern
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
            self.minimalMatch = seq
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
                self.minimalMatch = begin

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
    #@-node:ekr.20081205131308.87:pattern matchers
    #@+node:ekr.20081206062411.12:recolor & helpers
    def recolor (self,s):

        '''Recolor line s.'''

        trace = False and not g.unitTesting
        verbose = False ; traceMatch = False

        # Reload all_s if the widget's text is known to have changed.
        if self.initFlag:
            self.initFlag = False
            if self.colorizer.checkStartKillColor():
                self.all_s = None
                return

            self.all_s = self.w.getAllText()
            if trace:
                g.trace('**** set all_s: %s %s' % (
                    self.colorizer.language,len(self.all_s)),g.callers(5))

        all_s = self.all_s
        if not all_s: return

        # Update the counts.
        self.recolorCount += 1
        self.totalChars += len(s)

        # Init values that do not depend on all_s.
        offset = self.highlighter.currentBlock().position()
        b = self.getPrevState()
        lastFunc,lastMatch = b.lastFunc,b.lastMatch
        lastN,minimalMatch = 0,'' # Not used until there is a match.
        lastFlag = b.lastFlag
        if lastFlag is not None:
            # g.trace('***** set flag',lastFlag)
            self.colorizer.flag = lastFlag
        if trace and verbose and lastFunc: g.trace('prevState',b)
        i = g.choose(lastFunc,lastMatch,offset)

        # Make sure we are in synch with all_s.
        # Reload all_s if we are not.
        if not self.checkRecolor(offset,s):
            return g.trace('**** resych failure',s)

        # Set the values that depend on all_s.
        all_s = self.all_s
        j = min(offset + len(s),len(all_s))
        self.global_i,self.global_j = offset,j

        if trace:
            g.trace('%3s %5s %-40s %s' % (
                self.recolorCount,self.colorizer.flag,b.stateName,s))

        # The main colorizing loop.
        self.prev = None
        while i < j:
            loopFlag = self.colorizer.flag
            assert 0 <= i < len(all_s)
            progress = i
            functions = self.rulesDict.get(all_s[i],[])
            self.minimalMatch = ''
            for f in functions:
                n = f(self,all_s,i)
                if n is None:
                    g.trace('Can not happen' % (repr(n),repr(f)))
                    break
                elif n > 0: # Success.
                    if trace and traceMatch:
                        g.trace('match: offset %3s, i %3s, n %3s, f %s %s' % (
                            offset,i,n,f.__name__,repr(s[i:i+n])))
                    lastFunc,lastMatch,lastN,minimalMatch = f,i,n,self.minimalMatch
                    i += n
                    break # Stop searching the functions.
                elif n < 0: # Fail and skip n chars.
                    # match_keyword now sets n < 0 on first failure.
                    i += -n # Don't set lastMatch on failure!
                    break # Stop searching the functions.
                else: # Fail.  Go on to the next f in functions.
                    pass # Do not break or change i!
            else:
                i += 1 # Don't set lastMatch on failure!
            assert i > progress

        self.setCurrentState(s,offset,len(s)+1,
            lastFunc,lastMatch,lastN,minimalMatch)
    #@+node:ekr.20090213102946.10:checkRecolor
    def checkRecolor (self,offset,s):

        '''Return True if s can be synched with self.all_s.'''

        trace = False and not g.unitTesting

        all_s = self.all_s
        j = min(offset + len(s),len(all_s))
        s2 = all_s[offset:j]

        # The first check is allowed to fail.
        if s == s2: return True

        if trace: g.trace('**resynch**')

        # Assume we should have re-inited all_s
        self.all_s = all_s = self.w.getAllText()
        j = min(offset + len(s),len(all_s))
        s2 = all_s[offset:j]

        # Check again. This should never fail.
        if s != s2:
            g.trace('**** mismatch! offset %s len %s %s\n%s\n%s' % (
               offset,len(all_s),g.callers(5),repr(s),repr(s2)))
        return s == s2
    #@-node:ekr.20090213102946.10:checkRecolor
    #@+node:ekr.20090427163556.11:computeColorStateName
    def computeColorStateName (self):

        if self.colorizer.killColorFlag:
            color = 'killcolor.'
        elif self.colorizer.flag in (True,None):
            color = ''
        else:
            color = 'nocolor.'

        return color

    #@-node:ekr.20090427163556.11:computeColorStateName
    #@+node:ekr.20090427163556.14:computeDefaultStateName
    def computeDefaultStateName (self):

        languageState = self.computeLanguageStateName()
        colorState = self.computeColorStateName()

        return '%s%s%s' % (languageState,colorState,self.defaultState)
    #@-node:ekr.20090427163556.14:computeDefaultStateName
    #@+node:ekr.20090427163556.13:computeLanguageStateName
    def computeLanguageStateName (self):

        language = self.colorizer.language or ''

        return g.choose(language, '%s.' % language,'')
    #@-node:ekr.20090427163556.13:computeLanguageStateName
    #@+node:ekr.20090211072718.14:computeStateName
    def computeStateName (self,lastFunc,lastMatch,lastN,minimalMatch):

        if lastFunc:
            languageState = self.computeLanguageStateName()
            colorState = self.computeColorStateName()

            matchString = g.choose(minimalMatch,
                minimalMatch,
                self.all_s[lastMatch:lastMatch+lastN])

            name = '%s%s%s:%s' % (
                languageState,colorState,lastFunc.__name__,matchString)
        else:
            name = self.computeDefaultStateName()

        return name
    #@-node:ekr.20090211072718.14:computeStateName
    #@+node:ekr.20090211072718.2:getPrevState
    def getPrevState (self):

        h = self.highlighter
        n = h.previousBlockState()

        if n == -1:
            return g.Bunch(
                lastKillColorFlag=None,
                lastFlag=None,
                lastFunc=None,
                lastMatch=0,
                lastN=0,
                stateName = self.computeDefaultStateName())
        else:
            bunch = self.stateDict.get(n)
            assert bunch,'n=%s' % (n)
            return bunch
    #@-node:ekr.20090211072718.2:getPrevState
    #@+node:ekr.20090211072718.3:setCurrentState
    def setCurrentState (self,s,offset,limit,
        lastFunc,lastMatch,lastN,minimalMatch):

        trace = False and not g.unitTesting
        verbose = True
        h = self.highlighter
        flag = self.colorizer.flag
        killColorFlag = self.colorizer.killColorFlag

        self.stateCount += 1
        oldN = h.currentBlockState()
        active = bool(
            killColorFlag or flag is False or 
            (lastFunc and lastMatch + lastN > offset + limit))

        if active:
            b = self.stateDict.get(oldN)
            if b:
                changeState = (
                    b.lastFlag != flag or
                    b.lastKillColorFlag != killColorFlag or
                    b.lastFunc != lastFunc or
                    b.lastN != lastN)
            else:
                changeState = True
        else:
            flag,lastFunc,lastMatch,lastN,minimalMatch = None,None,None,None,None
            changeState = oldN != -1 

        stateName = self.computeStateName(
            lastFunc,lastMatch,lastN,minimalMatch)

        if trace and (changeState or active or verbose):
            g.trace('%2d ** active %5s changed %5s %-20s %s' % (
                self.stateCount,active,changeState,stateName,s))

        if not changeState:
            return

        n = self.stateNameDict.get(stateName)
        if n is None:
            n = self.nextState
            self.nextState += 1
            self.totalStates += 1
            self.maxStateNumber = max(n,self.maxStateNumber)

        state = g.bunch(
            lastKillColorFlag = killColorFlag,
            lastFlag=flag,
            lastFunc=lastFunc,
            lastMatch=lastMatch,
            lastN=lastN,
            stateName=stateName,)

        self.stateNameDict[stateName] = n
        self.stateDict[n] = state

        h.setCurrentBlockState(n)
    #@-node:ekr.20090211072718.3:setCurrentState
    #@+node:ekr.20081206062411.14:setTag
    def setTag (self,tag,s,i,j):

        trace = False and not g.unitTesting
        verbose = False
        w = self.w
        colorName = w.configDict.get(tag)

        if not self.colorizer.flag:
            # We are under the influence of @nocolor
            if trace: g.trace('in range of @nocolor',tag)
            return

        # Munch the color name.
        if not colorName:
            if trace: g.trace('no color for %s' % tag)
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
            self.tagCount += 1
            # kind = g.choose(ok,' ','***')
            s2 = g.choose(ok,s[clip_i:clip_j],self.all_s[i:j])

            if verbose:
                g.trace('%3s %3s %3s %3s %3s %3s %3s %s' % (
                    self.tagCount,tag,offset,i,j,lim_i,lim_j,s2),
                    g.callers(4))
            else:
                g.trace('%3s %7s %s' % (self.tagCount,tag,s2))

        if ok:
            self.highlighter.setFormat(clip_i-offset,clip_j-clip_i,color)
    #@-node:ekr.20081206062411.14:setTag
    #@-node:ekr.20081206062411.12:recolor & helpers
    #@-others
#@-node:ekr.20081205131308.48:class jeditColorizer
#@-node:ekr.20081204090029.1:Syntax coloring
#@-others
#@nonl
#@-node:ekr.20081121105001.188:@thin qtGui.py
#@-leo
