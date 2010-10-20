# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20081121105001.188: * @thin qtGui.py
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

#@+<< qt imports >>
#@+node:ekr.20081121105001.189: **  << qt imports >>
import leo.core.leoGlobals as g

import leo.core.leoChapters as leoChapters
import leo.core.leoColor as leoColor
import leo.core.leoFrame as leoFrame
import leo.core.leoFind as leoFind
import leo.core.leoGui as leoGui
import leo.core.leoKeys as leoKeys
import leo.core.leoMenu as leoMenu
import leo.core.leoPlugins as leoPlugins
    # Uses leoPlugins.TryNext.

import leo.plugins.baseNativeTree as baseNativeTree

import re
import string

import os
import re # For colorizer
import string
import sys
import datetime

try:
    # import PyQt4.Qt as Qt # Loads all modules of Qt.
    # import qt_main # Contains Ui_MainWindow class
    import PyQt4.QtCore as QtCore
    import PyQt4.QtGui as QtGui
except ImportError:
    QtCore = None

if QtCore is None:
    try: # Attempt Python 3000 imports
        from PyQt4 import QtCore
    except ImportError:
        QtCore = None
        print('\nqtGui.py: can not import Qt\nUse "launchLeo.py --gui=tk" to force Tk')
        raise

# remove scintilla dep for now    
if 0:    
    try:
        from PyQt4 import Qsci
    except ImportError:
        QtCore = None
        print('\nqtGui.py: can not import scintilla for Qt')
        print('\nqtGui.py: qt-scintilla may be a separate package on your system')
        print('\nqtGui.py: e.g. "python-qscintilla2" or similar\n')

#@-<< qt imports >>
#@+<< define text widget classes >>
#@+node:ekr.20081121105001.515: **  << define text widget classes >>
# Order matters when defining base classes.

#@+<< define QTextBrowserSubclass >>
#@+node:ekr.20090629160050.3739: *3*  << define QTextBrowserSubclass >>
class QTextBrowserSubclass (QtGui.QTextBrowser):

    '''A subclass of QTextBrowser that overrides the mouse event handlers.'''

    def __init__(self,parent,c,wrapper):
        for attr in ('leo_c','leo_wrapper',):
            assert not hasattr(QtGui.QTextBrowser,attr),attr
        self.leo_c = c
        self.leo_wrapper = wrapper
        self.htmlFlag = True
        QtGui.QTextBrowser.__init__(self,parent)

    def leo_dumpButton(self,event,tag):
        trace = False and not g.unitTesting
        button = event.button()
        table = (
            (QtCore.Qt.NoButton,'no button'),
            (QtCore.Qt.LeftButton,'left-button'),
            (QtCore.Qt.RightButton,'right-button'),
            (QtCore.Qt.MidButton,'middle-button'),
        )
        for val,s in table:
            if button == val:
                kind = s; break
        else: kind = 'unknown: %s' % repr(button)
        if trace: g.trace(tag,kind)
        return kind

    def mousePressEvent (self,event):
        if 1:
            QtGui.QTextBrowser.mousePressEvent(self,event)
        else: # Not ready yet
            kind = self.leo_dumpButton(event,'press')
            if kind == 'right-button':
                event.leo_widget = self # inject the widget.
                result = self.leo_c.frame.OnBodyRClick(event=event)
                # g.trace('result of OnBodyRClick',repr(result))
                if result != 'break':
                    QtGui.QTextBrowser.mousePressEvent(self,event)
            elif kind == 'left-button':
                event.leo_widget = self # inject the widget.
                result = self.leo_c.frame.OnBodyClick(event=event)
                # g.trace('result of OnBodyClick',repr(result))
                if result != 'break':
                    QtGui.QTextBrowser.mousePressEvent(self,event)
            else:
                QtGui.QTextBrowser.mousePressEvent(self,event)

    # def mouseReleaseEvent(self,event):
        # kind = self.leo_dumpButton(event,'release')
        # QtGui.QTextBrowser.mouseReleaseEvent(self,event)
#@-<< define QTextBrowserSubclass >>
#@+<< define leoQtBaseTextWidget class >>
#@+node:ekr.20081121105001.516: *3*  << define leoQtBaseTextWidget class >>
class leoQtBaseTextWidget (leoFrame.baseTextWidget):

    #@+others
    #@+node:ekr.20081121105001.517: *4*  Birth
    #@+node:ekr.20081121105001.518: *5* ctor (leoQtBaseTextWidget)
    def __init__ (self,widget,name='leoQtBaseTextWidget',c=None):

        self.widget = widget
        self.c = c or self.widget.leo_c

        # g.trace('leoQtBaseTextWidget',name)

        # Init the base class.
        leoFrame.baseTextWidget.__init__(
            self,c,baseClassName='leoQtBaseTextWidget',
            name=name,
            widget=widget,
            highLevelInterface=True)

        # Init ivars.
        self.changingText = False # A lockout for onTextChanged.
        self.tags = {}
        self.permanent = True # False if selecting the minibuffer will make the widget go away.
        self.configDict = {} # Keys are tags, values are colors (names or values).
        self.configUnderlineDict = {} # Keys are tags, values are True
        self.useScintilla = False # This is used!

        if not c: return # Can happen.

        if name == 'body' or name.startswith('head'):
            # Hook up qt events.
            self.ev_filter = leoQtEventFilter(c,w=self,tag=name)
            self.widget.installEventFilter(self.ev_filter)

        if name == 'body':
            self.widget.connect(self.widget,
                QtCore.SIGNAL("textChanged()"),self.onTextChanged)

            self.widget.connect(self.widget,
                QtCore.SIGNAL("cursorPositionChanged()"),self.onClick)

        self.injectIvars(c)
    #@+node:ekr.20081121105001.519: *5* injectIvars
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
        w.leo_scrollBarSpot = None
        w.leo_insertSpot = None
        w.leo_selection = None

        return w
    #@+node:ekr.20081121105001.520: *4*  Do nothings
    def bind (self,stroke,command,**keys):
        pass # eventFilter handles all keys.
    #@+node:ekr.20090629160050.3737: *4* Mouse events
    # These are overrides of the base-class events.

    #@+node:ekr.20081208041503.499: *5* onClick (qtText)
    def onClick(self,event=None):

        trace = False and not g.unitTesting

        c = self.c
        name = c.widget_name(self)

        if trace: g.trace(self,name,g.callers(5))

        if name.startswith('body'):
            if hasattr(c.frame,'statusLine'):
                c.frame.statusLine.update()
    #@+node:ekr.20081121105001.521: *4*  Must be defined in base class
    #@+node:ekr.20081121105001.522: *5*  Focus (leoQtBaseTextWidget)
    def getFocus(self):

        # g.trace('leoQtBody',self.widget,g.callers(4))
        return g.app.gui.get_focus(self.c) # Bug fix: 2009/6/30

    findFocus = getFocus

    def hasFocus (self):

        val = self.widget == g.app.gui.get_focus(self.c)
        # g.trace('leoQtBody returns',val,self.widget,g.callers(4))
        return val

    def setFocus (self):

        # g.trace('leoQtBody',self.widget,g.callers(4))
        g.app.gui.set_focus(self.c,self.widget)
    #@+node:ekr.20081121105001.523: *5*  Indices
    #@+node:ekr.20090320101733.13: *6* toPythonIndex
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
    #@+node:ekr.20090320101733.14: *6* toPythonIndexToRowCol
    def toPythonIndexRowCol(self,index):
        """ Slow 'default' implementation """
        #g.trace('slow toPythonIndexRowCol', g.callers(5))
        w = self
        s = w.getAllText()
        i = w.toPythonIndex(index)
        row,col = g.convertPythonIndexToRowCol(s,i)
        return i,row,col
    #@+node:ekr.20081121105001.524: *5*  Text getters/settters
    #@+node:ekr.20081121105001.525: *6* appendText
    def appendText(self,s):

        s2 = self.getAllText()
        self.setAllText(s2+s,insert=len(s2))

    #@+node:ekr.20081121105001.526: *6* delete
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
    #@+node:ekr.20081121105001.527: *6* deleteTextSelection
    def deleteTextSelection (self):

        i,j = self.getSelectionRange()
        self.delete(i,j)
    #@+node:ekr.20081121105001.529: *6* getLastPosition
    def getLastPosition(self):

        return len(self.getAllText())
    #@+node:ekr.20081121105001.530: *6* getSelectedText
    def getSelectedText(self):

        w = self.widget

        i,j = self.getSelectionRange()
        if i == j:
            return ''
        else:
            s = self.getAllText()
            # g.trace(repr(s[i:j]))
            return s[i:j]
    #@+node:ville.20090324170325.73: *6* get
    def get(self,i,j=None):
        """ Slow implementation of get() - ok for QLineEdit """
        #g.trace('Slow get', g.callers(5))

        s = self.getAllText()
        i = self.toGuiIndex(i)

        if j is None: 
            j = i+1

        j = self.toGuiIndex(j)
        return s[i:j]
    #@+node:ekr.20081121105001.531: *6* insert
    def insert(self,i,s):

        s2 = self.getAllText()
        i = self.toGuiIndex(i)
        self.setAllText(s2[:i] + s + s2[i:],insert=i+len(s))
        return i
    #@+node:ekr.20081121105001.532: *6* selectAllText
    def selectAllText(self,insert=None):

        w = self.widget
        w.selectAll()
        if insert is not None:
            self.setInsertPoint(insert)
        # g.trace('insert',insert)

    #@+node:ekr.20081121105001.533: *6* setSelectionRange & dummy helper
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

        return self.setSelectionRangeHelper(i,j,insert)
    #@+node:ekr.20081121105001.534: *7* setSelectionRangeHelper
    def setSelectionRangeHelper(self,i,j,insert):

        self.oops()
    #@+node:ekr.20081121105001.535: *5* getName (baseTextWidget)
    def getName (self):

        # g.trace('leoQtBaseTextWidget',self.name,g.callers())

        return self.name
    #@+node:ekr.20081121105001.536: *5* onTextChanged (qtText)
    def onTextChanged (self):

        '''Update Leo after the body has been changed.

        self.selecting is guaranteed to be True during
        the entire selection process.'''

        # Important: usually w.changingText is True.
        # This method very seldom does anything.
        trace = False and not g.unitTesting
        verbose = True
        c = self.c ; p = c.p
        tree = c.frame.tree ; w = self

        if w.changingText: 
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
            if trace: g.trace('*** no p')
            return

        newInsert = w.getInsertPoint()
        newSel = w.getSelectionRange()
        newText = w.getAllText() # Converts to unicode.

        # Get the previous values from the vnode.
        oldText = p.b
        if oldText == newText:
            # This can happen as the result of undo.
            # g.trace('*** unexpected non-change',color="red")
            return

        # g.trace('**',len(newText),p.h,'\n',g.callers(8))

        oldIns  = p.v.insertSpot
        i,j = p.v.selectionStart,p.v.selectionLength
        oldSel  = (i,i+j)
        if trace: g.trace('oldSel',oldSel,'newSel',newSel)
        oldYview = None
        undoType = 'Typing'
        c.undoer.setUndoTypingParams(p,undoType,
            oldText=oldText,newText=newText,
            oldSel=oldSel,newSel=newSel,oldYview=oldYview)

        # Update the vnode.
        p.v.setBodyString(newText)
        if True:
            p.v.insertSpot = newInsert
            i,j = newSel
            i,j = self.toGuiIndex(i),self.toGuiIndex(j)
            if i > j: i,j = j,i
            p.v.selectionStart,p.v.selectionLength = (i,j-i)

        # No need to redraw the screen.
        if not self.useScintilla:
            c.recolor()

        if g.app.qt_use_tabs:
            if trace: g.trace(c.frame.top)

        if not c.changed and c.frame.initComplete:
            c.setChanged(True)

        c.frame.body.updateEditors()
        c.frame.tree.updateIcon(p)

        if 1: # This works, and is probably better.
            # Set a hook for the old jEdit colorer.
            colorer = c.frame.body.colorizer.highlighter.colorer
            colorer.initFlag = True
        else:
            # Allow incremental recoloring.
            c.incrementalRecolorFlag = True
            c.outerUpdate()
    #@+node:ekr.20081121105001.537: *5* indexWarning
    warningsDict = {}

    def indexWarning (self,s):

        return

        # if s not in self.warningsDict:
            # g.es_print('warning: using dubious indices in %s' % (s),color='red')
            # g.es_print('callers',g.callers(5))
            # self.warningsDict[s] = True
    #@+node:ekr.20081121105001.538: *4*  May be overridden in subclasses
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

    #@+node:ekr.20081121105001.539: *5* Configuration
    # Configuration will be handled by style sheets.
    def cget(self,*args,**keys):            return None
    def configure (self,*args,**keys):      pass
    def setBackgroundColor(self,color):     pass
    def setEditorColors (self,bg,fg):       pass
    def setForegroundColor(self,color):     pass
    #@+node:ekr.20081121105001.540: *5* Idle time
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
    #@+node:ekr.20081121105001.541: *5* Coloring (baseTextWidget)
    # These *are* used.

    def removeAllTags(self):
        s = self.getAllText()
        self.colorSelection(0,len(s),'black')

    def tag_names (self):
        return []
    #@+node:ekr.20081121105001.542: *6* colorSelection
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
    #@+node:ekr.20081124102726.10: *6* tag_add
    # This appears never to be called.

    def tag_add(self,tagName,i,j=None,*args):

        if j is None: j = i+1

        g.trace(tagName,i,j)

        val = self.configDict.get(tagName)
        if val:
            self.colorSelection(i,j,val)
    #@+node:ekr.20081124102726.11: *6* tag_config & tag_configure (baseTextWidget)
    def tag_config (self,*args,**keys):

        trace = False and not g.unitTesting
        if trace: g.trace(self,args,keys)

        if len(args) == 1:
            key = args[0]
            self.tags[key] = keys
            val = keys.get('foreground')
            underline = keys.get('underline')
            if val:
                # if trace: g.trace(key,val)
                self.configDict [key] = val
            if underline:
                self.configUnderlineDict [key] = True
        else:
            g.trace('oops',args,keys)

    tag_configure = tag_config
    #@+node:ekr.20081121105001.543: *4*  Must be overridden in subclasses
    # These methods avoid calls to setAllText.

    def getAllText(self):                   self.oops()
    def getInsertPoint(self):               self.oops()
    def getSelectionRange(self,sort=True):  self.oops()
    def hasSelection(self):                 self.oops()
    def see(self,i):                        self.oops()
    def setAllText(self,s,insert=None,new_p=None):
        self.oops()
    def setInsertPoint(self,i):             self.oops()
    #@-others
#@-<< define leoQtBaseTextWidget class >>
#@+<< define leoQLineEditWidget class >>
#@+node:ekr.20081121105001.544: *3*  << define leoQLineEditWidget class >>
class leoQLineEditWidget (leoQtBaseTextWidget):

    #@+others
    #@+node:ekr.20081121105001.545: *4* Birth
    #@+node:ekr.20081121105001.546: *5* ctor
    def __init__ (self,widget,name,c=None):

        # Init the base class.
        leoQtBaseTextWidget.__init__(self,widget,name,c=c)

        self.baseClassName='leoQLineEditWidget'

        # g.trace('leoQLineEditWidget',id(widget),g.callers(5))

        self.setConfig()
        self.setFontFromConfig()
        self.setColorFromConfig()
    #@+node:ekr.20081121105001.547: *5* setFontFromConfig
    def setFontFromConfig (self,w=None):

        '''Set the font in the widget w (a body editor).'''
    #@+node:ekr.20081121105001.548: *5* setColorFromConfig
    def setColorFromConfig (self,w=None):

        '''Set the font in the widget w (a body editor).'''
    #@+node:ekr.20081121105001.549: *5* setConfig
    def setConfig (self):

        pass
    #@+node:ekr.20081121105001.550: *4* Widget-specific overrides (QLineEdit)
    #@+node:ekr.20081121105001.551: *5* getAllText
    def getAllText(self):

        w = self.widget
        s = w.text()
        return g.u(s)
    #@+node:ekr.20081121105001.552: *5* getInsertPoint
    def getInsertPoint(self):

        i = self.widget.cursorPosition()
        # g.trace(i)
        return i
    #@+node:ekr.20081121105001.553: *5* getSelectionRange
    def getSelectionRange(self,sort=True):

        w = self.widget

        if w.hasSelectedText():
            i = w.selectionStart()
            s = w.selectedText()
            s = g.u(s)
            j = i + len(s)
        else:
            i = j = w.cursorPosition()

        # g.trace(i,j)
        return i,j
    #@+node:ekr.20081121105001.554: *5* hasSelection
    def hasSelection(self):

        return self.widget.hasSelection()
    #@+node:ekr.20081121105001.555: *5* see & seeInsertPoint
    def see(self,i):
        pass

    def seeInsertPoint (self):
        pass
    #@+node:ekr.20081121105001.556: *5* setAllText
    def setAllText(self,s,insert=None):

        w = self.widget
        i = g.choose(insert is None,0,insert)
        w.setText(s)
        if insert is not None:
            self.setSelectionRange(i,i,insert=i)
    #@+node:ekr.20081121105001.557: *5* setInsertPoint
    def setInsertPoint(self,i):

        w = self.widget
        s = w.text()
        s = g.u(s)
        i = w.toPythonIndex(i)
        i = max(0,min(i,len(s)))
        w.setCursorPosition(i)
    #@+node:ekr.20081121105001.558: *5* setSelectionRangeHelper (leoQLineEdit)
    def setSelectionRangeHelper(self,i,j,insert):

        w = self.widget
        # g.trace(i,j,insert,w)
        if i > j: i,j = j,i
        s = w.text()
        s = g.u(s)
        n = len(s)
        i = max(0,min(i,n))
        j = max(0,min(j,n))
        if j < i: i,j = j,i
        if insert is None: insert = j
        insert = max(0,min(insert,n))
        if i == j:
            w.setCursorPosition(i)
        else:
            length = j-i
            if insert < j:
                w.setSelection(j,-length)
            else:
                w.setSelection(i,length)
    #@-others
#@-<< define leoQLineEditWidget class >>
#@+<< define leoQTextEditWidget class >>
#@+node:ekr.20081121105001.572: *3*  << define leoQTextEditWidget class >>
class leoQTextEditWidget (leoQtBaseTextWidget):

    #@+others
    #@+node:ekr.20081121105001.573: *4* Birth
    #@+node:ekr.20081121105001.574: *5* ctor
    def __init__ (self,widget,name,c=None):

        # widget is a QTextEdit (or QTextBrowser).
        # g.trace('leoQTextEditWidget',widget)

        # Init the base class.
        leoQtBaseTextWidget.__init__(self,widget,name,c=c)

        self.baseClassName='leoQTextEditWidget'

        widget.setUndoRedoEnabled(False)

        self.setConfig()
        self.setFontFromConfig()
        self.setColorFromConfig()
    #@+node:ekr.20081121105001.575: *5* setFontFromConfig
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
    #@+node:ekr.20081121105001.576: *5* setColorFromConfig
    def setColorFromConfig (self,w=None):

        '''Set the font in the widget w (a body editor).'''
    #@+node:ekr.20081121105001.577: *5* setConfig
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
    #@+node:ekr.20100109082023.3734: *4* leoMoveCursorHelper (Qt)
    def leoMoveCursorHelper (self,kind,extend=False,linesPerPage=15):

        '''Move the cursor in a QTextEdit.'''

        trace = False and not g.unitTesting
        verbose = True
        w = self.widget
        if trace:
            g.trace(kind,'extend',extend)
            if verbose:
                g.trace(len(w.toPlainText()))

        tc = QtGui.QTextCursor
        d = {
            'exchange': True, # Dummy.
            'down':tc.Down,'end':tc.End,'end-line':tc.EndOfLine,
            'home':tc.Start,'left':tc.Left,'page-down':tc.Down,
            'page-up':tc.Up,'right':tc.Right,'start-line':tc.StartOfLine,
            'up':tc.Up,
        }
        kind = kind.lower()
        op = d.get(kind)
        mode = g.choose(extend,tc.KeepAnchor,tc.MoveAnchor)

        if not op:
            return g.trace('can not happen: bad kind: %s' % kind)

        if kind in ('page-down','page-up'):
            cursor = w.textCursor()
            cursor.movePosition(op,mode,linesPerPage)
            w.setTextCursor(cursor)
        elif kind == 'exchange': # exchange-point-and-mark
            cursor = w.textCursor()
            anchor = cursor.anchor()
            pos = cursor.position()
            cursor.setPosition(pos,tc.MoveAnchor)
            cursor.setPosition(anchor,tc.KeepAnchor)
            w.setTextCursor(cursor)
        else:
            if not extend:
                # Fix an annoyance. Make sure to clear the selection.
                cursor = w.textCursor()
                cursor.clearSelection()
                w.setTextCursor(cursor)
            w.moveCursor(op,mode)
    #@+node:ekr.20081121105001.578: *4* Widget-specific overrides (QTextEdit)
    #@+node:ekr.20090205153624.11: *5* delete (avoid call to setAllText)
    def delete(self,i,j=None):

        trace = False and not g.unitTesting
        c,w = self.c,self.widget
        colorer = c.frame.body.colorizer.highlighter.colorer
        n = colorer.recolorCount

        if trace: g.trace(self.getSelectionRange())

        i = self.toGuiIndex(i)
        if j is None: j = i+1
        j = self.toGuiIndex(j)
        if i > j: i,j = j,i

        if trace: g.trace(i,j)

        # Set a hook for the colorer.
        colorer.initFlag = True

        sb = w.verticalScrollBar()
        pos = sb.sliderPosition()
        cursor = w.textCursor()

        try:
            self.changingText = True # Disable onTextChanged

            old_i,old_j = self.getSelectionRange()
            if i == old_i and j == old_j:
                # Work around an apparent bug in cursor.movePosition.
                cursor.removeSelectedText()
            elif i == j:
                pass
            else:
                # g.trace('*** using dubious code')
                cursor.setPosition(i)
                moveCount = abs(j-i)
                cursor.movePosition(cursor.Right,cursor.KeepAnchor,moveCount)
                w.setTextCursor(cursor)  # Bug fix: 2010/01/27
                if trace:
                    i,j = self.getSelectionRange()
                    g.trace(i,j)
                cursor.removeSelectedText()
                if trace: g.trace(self.getSelectionRange())
        finally:
            self.changingText = False

        sb.setSliderPosition(pos)

        # g.trace('%s calls to recolor' % (colorer.recolorCount-n))
    #@+node:ekr.20081121105001.579: *5* flashCharacter (leoQTextEditWidget)
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
    #@+node:ekr.20081121105001.580: *5* getAllText (leoQTextEditWidget)
    def getAllText(self):

        w = self.widget

        s = g.u(w.toPlainText())

        return s
    #@+node:ekr.20081121105001.581: *5* getInsertPoint
    def getInsertPoint(self):

        return self.widget.textCursor().position()
    #@+node:ekr.20081121105001.582: *5* getSelectionRange
    def getSelectionRange(self,sort=True):

        trace = False and not g.unitTesting
        w = self.widget
        tc = w.textCursor()
        i,j = tc.selectionStart(),tc.selectionEnd()
        # s = tc.selectedText()
        # if s: n = len(s)
        # else: n = 0
        if trace: g.trace(i,j)
        return i,j
    #@+node:ekr.20081121105001.583: *5* getYScrollPosition
    def getYScrollPosition(self):

        w = self.widget
        sb = w.verticalScrollBar()
        i = sb.sliderPosition()

        # Return a tuple, only the first of which is used.
        return i,i 
    #@+node:ekr.20081121105001.584: *5* hasSelection
    def hasSelection(self):

        return self.widget.textCursor().hasSelection()
    #@+node:ekr.20090531084925.3773: *5* scrolling (QTextEdit)
    #@+node:ekr.20090531084925.3775: *6* indexIsVisible and linesPerPage
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
    #@+node:ekr.20090531084925.3776: *6* scrollDelegate (QTextEdit)
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
    #@+node:ekr.20090205153624.12: *5* insert (avoid call to setAllText)
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
        try:
            self.changingText = True # Disable onTextChanged.
            cursor.setPosition(i)
            cursor.insertText(s) # This cause an incremental call to recolor.
            w.setTextCursor(cursor) # Bug fix: 2010/01/27
        finally:
            self.changingText = False

        sb.setSliderPosition(pos)

        if trace:
            g.trace('%s calls to recolor' % (
                colorer.recolorCount-n))
    #@+node:ekr.20081121105001.585: *5* see
    def see(self,i):

        self.widget.ensureCursorVisible()
    #@+node:ekr.20081121105001.586: *5* seeInsertPoint
    def seeInsertPoint (self):

        self.widget.ensureCursorVisible()
    #@+node:ekr.20081121105001.587: *5* setAllText (leoQTextEditWidget) & helper
    def setAllText(self,s,insert=None,new_p=None):

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

        if trace: g.trace(new_p)
        if trace and verbose: t1 = g.getTime()
        try:
            self.changingText = True # Disable onTextChanged
            colorizer.changingText = True
            if w.htmlFlag and new_p and new_p.h.startswith('@html '):
                w.setReadOnly(False)
                w.setHtml(s)
                w.setReadOnly(True)
            elif w.htmlFlag and new_p and new_p.h.startswith('@image'):
                s2 = self.urlToImageHtml(new_p,s)
                w.setReadOnly(False)
                w.setHtml(s2)
                w.setReadOnly(True)
            else:
                w.setReadOnly(False)
                w.setPlainText(s)
        finally:
            self.changingText = False
            colorizer.changingText = False
        if trace and verbose: g.trace(g.timeSince(t1))

        self.setSelectionRange(i,i,insert=i)
        sb.setSliderPosition(pos)
    #@+node:ekr.20091117092146.3671: *6* urlToImageHtml
    def urlToImageHtml (self,p,s):

        '''Create html that will display an image whose url is in s or p.h.'''

        if not s.strip():
            assert p.h.startswith('@image')
            s = p.h[6:].strip()

        if s.startswith('file://'):
            s2 = s[7:]
            s2 = g.os_path_finalize_join(g.app.loadDir,s2)
            if g.os_path_exists(s2):
                # g.es(s2.replace('\\','/'))
                s = 'file:///' + s2
                # if s2.endswith('.html') or s2.endswith('.htm'):
                    # s = open(s2).read()
                    # return s
            else:
                g.es('not found',s2)
                return s # Don't render the image.

        s = s.replace('\\','/')
        s = s.strip("'").strip('"').strip()

        html = '''
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
    <head></head>
    <body bgcolor="#fffbdc">
    <img src="%s">
    </body>
    </html>
    ''' % (s)

        return html
    #@+node:ekr.20081121105001.588: *5* setInsertPoint
    def setInsertPoint(self,i):

        w = self.widget

        s = w.toPlainText()
        i = self.toPythonIndex(i)
        i = max(0,min(i,len(s)))
        cursor = w.textCursor()
        cursor.setPosition(i)
        w.setTextCursor(cursor)
    #@+node:ekr.20081121105001.589: *5* setSelectionRangeHelper & helper
    def setSelectionRangeHelper(self,i,j,insert):

        trace = False and not g.unitTesting
        w = self.widget
        i = self.toPythonIndex(i)
        j = self.toPythonIndex(j)

        n = self.lengthHelper()
        i = max(0,min(i,n))
        j = max(0,min(j,n))
        if insert is None:
            ins = max(i,j)
        else:
            ins = self.toPythonIndex(insert)
            ins = max(0,min(ins,n))

        if trace:g.trace('i',i,'j',j,'insert',insert)

        # 2010/02/02: Use only tc.setPosition here.
        # Using tc.movePosition doesn't work.
        tc = w.textCursor()
        if i == j:
            tc.setPosition(i)
        elif ins == j:
            # Put the insert point at j
            tc.setPosition(i)
            tc.setPosition(j,tc.KeepAnchor)
        else:
            # Put the insert point a i
            tc.setPosition(j)
            tc.setPosition(i,tc.KeepAnchor)

        w.setTextCursor(tc)
    #@+node:ekr.20081121105001.590: *6* lengthHelper
    def lengthHelper(self):

        '''Return the length of the text.'''

        w = self.widget
        tc = w.textCursor()
        tc.movePosition(QtGui.QTextCursor.End)
        n = tc.position()
        return n

    #@+node:ekr.20081121105001.591: *5* setYScrollPosition
    def setYScrollPosition(self,pos):

        # g.trace(pos,g.callers(3))

        w = self.widget
        sb = w.verticalScrollBar()
        if pos is None:
            pos = 0
        else:
            try:
                n1,n2 = pos
                pos = n1
            except TypeError:
                pass
        sb.setSliderPosition(pos)
    #@+node:ville.20090321082712.1: *5*  PythonIndex
    #@+node:ville.20090321082712.2: *6* toPythonIndex
    def toPythonIndex (self,index):

        w = self
        te = self.widget

        if index is None:
            return 0
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
    #@+node:ville.20090321082712.3: *6* toPythonIndexToRowCol (leoQTextEditWidget)
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
    #@+node:ville.20090324170325.63: *5* get
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
            s = g.u(bl.text())
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
    #@-others
#@-<< define leoQTextEditWidget class >>

# Define all other text classes, in any order.

#@+others
#@+node:ekr.20081121105001.593: *3* class findTextWrapper
class findTextWrapper (leoQLineEditWidget):

    '''A class representing the find/change edit widgets.'''

    def __init__ (self,widget,name,c=None):
        # Init the base class.
        leoQLineEditWidget.__init__(self,widget,name,c=c)
        self.tabWidget = None

    def setTabWidget (self,widget):
        self.tabWidget = widget
#@+node:ekr.20081121105001.559: *3* class leoQScintilla
class leoQScintillaWidget (leoQtBaseTextWidget):

    #@+others
    #@+node:ekr.20081121105001.560: *4* Birth
    #@+node:ekr.20081121105001.561: *5* ctor
    def __init__ (self,widget,name,c=None):

        # Init the base class.
        leoQtBaseTextWidget.__init__(self,widget,name,c=c)

        self.baseClassName='leoQScintillaWidget'

        self.useScintilla = True
        self.setConfig()
    #@+node:ekr.20081121105001.562: *5* setConfig
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
    #@+node:ekr.20081121105001.563: *4* Widget-specific overrides (QScintilla)
    #@+node:ekr.20081121105001.564: *5* getAllText
    def getAllText(self):

        w = self.widget
        s = w.text()
        s = g.u(s)
        return s
    #@+node:ekr.20081121105001.565: *5* getInsertPoint
    def getInsertPoint(self):

        w = self.widget
        s = self.getAllText()
        row,col = w.getCursorPosition()  
        i = g.convertRowColToPythonIndex(s, row, col)
        return i
    #@+node:ekr.20081121105001.566: *5* getSelectionRange
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

    #@+node:ekr.20081121105001.567: *5* hasSelection
    def hasSelection(self):

        return self.widget.hasSelectedText()
    #@+node:ekr.20081121105001.568: *5* see
    def see(self,i):

        # Ok for now.  Using SCI_SETYCARETPOLICY might be better.
        w = self.widget
        s = self.getAllText()
        row,col = g.convertPythonIndexToRowCol(s,i)
        w.ensureLineVisible(row)

    # Use base-class method for seeInsertPoint.
    #@+node:ekr.20081121105001.569: *5* setAllText
    def setAllText(self,s,insert=None,new_p=None):

        '''Set the text of the widget.

        If insert is None, the insert point, selection range and scrollbars are initied.
        Otherwise, the scrollbars are preserved.'''

        w = self.widget
        w.setText(s)

    #@+node:ekr.20081121105001.570: *5* setInsertPoint
    def setInsertPoint(self,i):

        w = self.widget
        w.SendScintilla(w.SCI_SETCURRENTPOS,i)
        w.SendScintilla(w.SCI_SETANCHOR,i)
    #@+node:ekr.20081121105001.571: *5* setSelectionRangeHelper
    def setSelectionRangeHelper(self,i,j,insert):

        w = self.widget

        # g.trace('i',i,'j',j,'insert',insert,g.callers(4))

        if insert in (j,None):
            self.setInsertPoint(j)
            w.SendScintilla(w.SCI_SETANCHOR,i)
        else:
            self.setInsertPoint(i)
            w.SendScintilla(w.SCI_SETANCHOR,j)
    #@-others
#@+node:ekr.20081121105001.592: *3* class leoQtHeadlineWidget
class leoQtHeadlineWidget (leoQtBaseTextWidget):
    '''A wrapper class for QLineEdit widgets in QTreeWidget's.

    This wrapper must appear to be a leoFrame.baseTextWidget to Leo's core.
    '''

    #@+others
    #@+node:ekr.20090603073641.3841: *4* Birth
    def __init__ (self,c,item,name,widget):

        # g.trace('(leoQtHeadlineWidget)',item,widget)

        # Init the base class.
        leoQtBaseTextWidget.__init__(self,widget,name,c)
        self.item=item
        self.permanent = False # Warn the minibuffer that we can go away.

    def __repr__ (self):
        return 'leoQtHeadlineWidget: %s' % id(self)
    #@+node:ekr.20090603073641.3851: *4* Widget-specific overrides (leoQtHeadlineWidget)
    # These are safe versions of QLineEdit methods.
    #@+node:ekr.20090603073641.3861: *5* check
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
    #@+node:ekr.20090603073641.3852: *5* getAllText
    def getAllText(self):

        if self.check():
            w = self.widget
            s = w.text()
            return g.u(s)
        else:
            return ''
    #@+node:ekr.20090603073641.3853: *5* getInsertPoint
    def getInsertPoint(self):

        if self.check():
            i = self.widget.cursorPosition()
            return i
        else:
            return 0
    #@+node:ekr.20090603073641.3854: *5* getSelectionRange
    def getSelectionRange(self,sort=True):

        w = self.widget

        if self.check():
            if w.hasSelectedText():
                i = w.selectionStart()
                s = w.selectedText()
                s = g.u(s)
                j = i + len(s)
            else:
                i = j = w.cursorPosition()
            return i,j
        else:
            return 0,0
    #@+node:ekr.20090603073641.3855: *5* hasSelection
    def hasSelection(self):

        if self.check():
            return self.widget.hasSelectedText()
        else:
            return False
    #@+node:ekr.20090603073641.3856: *5* see & seeInsertPoint
    def see(self,i):
        pass

    def seeInsertPoint (self):
        pass
    #@+node:ekr.20090603073641.3857: *5* setAllText
    def setAllText(self,s,insert=None):

        if not self.check(): return

        w = self.widget
        i = g.choose(insert is None,0,insert)
        w.setText(s)
        if insert is not None:
            self.setSelectionRange(i,i,insert=i)
    #@+node:ekr.20090603073641.3862: *5* setFocus
    def setFocus (self):

        if self.check():
            g.app.gui.set_focus(self.c,self.widget)
    #@+node:ekr.20090603073641.3858: *5* setInsertPoint
    def setInsertPoint(self,i):

        if not self.check(): return

        w = self.widget
        s = w.text()
        s = g.u(s)
        i = self.toPythonIndex(i)
        i = max(0,min(i,len(s)))
        w.setCursorPosition(i)
    #@+node:ekr.20090603073641.3859: *5* setSelectionRangeHelper (leoQLineEdit)
    def setSelectionRangeHelper(self,i,j,insert):

        if not self.check(): return
        w = self.widget
        # g.trace(i,j,insert,w)
        if i > j: i,j = j,i
        s = w.text()
        s = g.u(s)
        n = len(s)
        i = max(0,min(i,n))
        j = max(0,min(j,n))
        if insert is None:
            insert = j
        else:
            insert = self.toPythonIndex(insert)
            insert = max(0,min(insert,n))
        if i == j:
            w.setCursorPosition(i)
        else:
            length = j-i
            if insert < j:
                w.setSelection(j,-length)
            else:
                w.setSelection(i,length)
    #@-others
#@+node:ekr.20081121105001.594: *3* class leoQtMinibuffer (leoQLineEditWidget)
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
#@-others
#@-<< define text widget classes >>

#@+others
#@+node:ekr.20081121105001.190: **  Module level

#@+node:ekr.20081121105001.191: *3* init
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
            if message: print(message)
            import pdb
            if not g.app.useIpython:
                QtCore.pyqtRemoveInputHook()
            pdb.set_trace()
        g.pdb = qtPdb

        g.app.gui.finishCreate()
        g.plugin_signon(__name__)
        return True
#@+node:ekr.20081121105001.194: ** Frame and component classes...
#@+node:ekr.20081121105001.200: *3* class  DynamicWindow (QtGui.QMainWindow)
from PyQt4 import uic

class DynamicWindow(QtGui.QMainWindow):

    '''A class representing all parts of the main Qt window
    as created by Designer.

    c.frame.top is a DynamciWindow object.

    For --gui==qttabs:
        c.frame.top.parent is a TabbedFrameFactory
        c.frame.top.master is a LeoTabbedTopLevel

    All leoQtX classes use the ivars of this Window class to
    support operations requested by Leo's core.
    '''

    #@+others
    #@+node:ekr.20081121105001.201: *4*  ctor (DynamicWindow)
    # Called from leoQtFrame.finishCreate.

    def __init__(self,c,parent=None):

        '''Create Leo's main window, c.frame.top'''

        # g.trace('(DynamicWindow)','parent',parent)

        QtGui.QMainWindow.__init__(self,parent)

        self.leo_c = c
    #@+node:ville.20090806213440.3689: *4* construct (DynamicWindow)
    def construct(self,master=None):
        """ Factor 'heavy duty' code out from ctor """

        c = self.leo_c; top = c.frame.top
        self.master=master # A LeoTabbedTopLevel for tabbed windows.
        # print('DynamicWindow.__init__ %s' % c)

        # Init the base class.
        ui_file_name = c.config.getString('qt_ui_file_name')
        if not ui_file_name:
            ui_file_name = 'qt_main.ui'

        ui_description_file = g.app.loadDir + "/../plugins/" + ui_file_name
        # g.pr('DynamicWindw.__init__,ui_description_file)
        assert g.os_path_exists(ui_description_file)

        self.bigTree = c.config.getBool('big_outline_pane')

        if useUI:  
            self.ui = uic.loadUi(ui_description_file, self)
        else:
            self.createMainWindow()


        self.iconBar = self.addToolBar("IconBar")

        # Set orientation if requested.
        d = {
            'bottom':QtCore.Qt.BottomToolBarArea,
            'left':QtCore.Qt.LeftToolBarArea,
            'right':QtCore.Qt.RightToolBarArea,
            'top':QtCore.Qt.TopToolBarArea,
        }
        where = c.config.getString('qt-toolbar-location')
        if where:
            where = d.get(where)
            if where: self.addToolBar(where,self.iconBar)
        self.menubar = self.menuBar()
        self.statusBar = QtGui.QStatusBar()
        self.setStatusBar(self.statusBar)

        orientation = c.config.getString('initial_split_orientation')
        self.setSplitDirection(orientation)
        self.setStyleSheets()
        #self.setLeoWindowIcon()
    #@+node:ekr.20081121105001.202: *4* closeEvent (DynanicWindow)
    def closeEvent (self,event):

        trace = False and not g.unitTesting
        c = self.leo_c

        if not c.exists:
            # Fixes double-prompt bug on Linux.
            if trace: g.trace('destroyed')
            event.accept()
            return

        if c.inCommand:
            if trace: g.trace('in command')
            c.requestCloseWindow = True
        else:
            if trace: g.trace('closing')
            ok = g.app.closeLeoWindow(c.frame)
            if ok:
                event.accept()
            else:
                event.ignore()
    #@+node:ekr.20090423070717.14: *4* createMainWindow & helpers
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
        if self.bigTree:
            self.createBodyPane(self.splitter)
            self.createLogPane(self.splitter)
            treeFrame = self.createOutlinePane(self.splitter_2)
            self.splitter_2.addWidget(treeFrame)
            self.splitter_2.addWidget(self.splitter)
        else:
            self.createOutlinePane(self.splitter)
            self.createLogPane(self.splitter)
            self.createBodyPane(self.splitter_2)
        self.createMiniBuffer(self.centralwidget)
        self.createMenuBar()
        self.createStatusBar(MainWindow)

        # Signals
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
    #@+node:ekr.20090426183711.10: *5* top-level
    #@+node:ekr.20090424085523.43: *6* createBodyPane
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
        self.text_page = page2
        self.stackedWidget = sw # used by leoQtBody
        self.richTextEdit = body
        self.leo_body_frame = bodyFrame
        self.leo_body_inner_frame = innerFrame
        # self.leo_body_grid = grid
        # self.grid = innerGrid
        # self.page_2 = page2
        # self.verticalBodyLayout= vLayout
    #@+node:ekr.20090425072841.12: *6* createCentralWidget
    def createCentralWidget (self):

        MainWindow = self

        w = QtGui.QWidget(MainWindow)
        w.setObjectName("centralwidget")

        MainWindow.setCentralWidget(w)

        # Official ivars.
        self.centralwidget = w
    #@+node:ekr.20090424085523.42: *6* createLogPane
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
    #@+node:ekr.20090424085523.41: *6* createMainLayout (DynamicWindow)
    def createMainLayout (self,parent):

        c = self.leo_c

        vLayout = self.createVLayout(parent,'mainVLayout',margin=3)

        # Splitter two is the "main" splitter, containing splitter.
        splitter2 = QtGui.QSplitter(parent)
        splitter2.setOrientation(QtCore.Qt.Vertical)
        splitter2.setObjectName("splitter_2")

        splitter2.connect(splitter2,
            QtCore.SIGNAL("splitterMoved(int,int)"),
            self.onSplitter2Moved)

        splitter = QtGui.QSplitter(splitter2)
        splitter.setOrientation(QtCore.Qt.Horizontal)
        splitter.setObjectName("splitter")

        splitter.connect(splitter,
            QtCore.SIGNAL("splitterMoved(int,int)"),
            self.onSplitter1Moved)

        # g.trace('splitter %s splitter2 %s' % (id(splitter),id(splitter2)))

        # Official ivars
        self.verticalLayout = vLayout
        self.splitter = splitter
        self.splitter_2 = splitter2

        self.setSizePolicy(self.splitter)
        self.verticalLayout.addWidget(self.splitter_2)
    #@+node:ekr.20090424085523.45: *6* createMenuBar
    def createMenuBar (self):

        MainWindow = self

        w = QtGui.QMenuBar(MainWindow)
        w.setGeometry(QtCore.QRect(0, 0, 957, 22))
        w.setObjectName("menubar")

        MainWindow.setMenuBar(w)

        # Official ivars.
        self.menubar = w
    #@+node:ekr.20090424085523.44: *6* createMiniBuffer
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
    #@+node:ekr.20090424085523.47: *6* createOutlinePane
    def createOutlinePane (self,parent):

        # Create widgets.
        treeFrame = self.createFrame(parent,'outlineFrame',
            vPolicy = QtGui.QSizePolicy.Expanding)
        innerFrame = self.createFrame(treeFrame,'outlineInnerFrame',
            hPolicy = QtGui.QSizePolicy.Preferred)

        treeWidget = self.createTreeWidget(innerFrame,'treeWidget')

        grid = self.createGrid(treeFrame,'outlineGrid')
        grid.addWidget(innerFrame, 0, 0, 1, 1)
        innerGrid = self.createGrid(innerFrame,'outlineInnerGrid')
        innerGrid.addWidget(treeWidget, 0, 0, 1, 1)

        # Official ivars...
        self.treeWidget = treeWidget
        # self.leo_outline_frame = treeFrame
        # self.leo_outline_grid = grid
        # self.leo_outline_inner_frame = innerFrame

        return treeFrame
    #@+node:ekr.20090424085523.46: *6* createStatusBar
    def createStatusBar (self,parent):

        w = QtGui.QStatusBar(parent)
        w.setObjectName("statusbar")
        parent.setStatusBar(w)

        # Official ivars.
        self.statusBar = w
    #@+node:ekr.20090425072841.2: *6* setMainWindowOptions
    def setMainWindowOptions (self):

        MainWindow = self

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(691, 635)
        MainWindow.setDockNestingEnabled(False)
        MainWindow.setDockOptions(
            QtGui.QMainWindow.AllowTabbedDocks |
            QtGui.QMainWindow.AnimatedDocks)
    #@+node:ekr.20090426183711.11: *5* widgets
    #@+node:ekr.20090424085523.51: *6* createButton
    def createButton (self,parent,name,label):

        w = QtGui.QPushButton(parent)
        w.setObjectName(name)
        w.setText(self.tr(label))
        return w
    #@+node:ekr.20090424085523.39: *6* createCheckBox
    def createCheckBox (self,parent,name,label):

        w = QtGui.QCheckBox(parent)
        self.setName(w,name)
        w.setText(self.tr(label))
        return w
    #@+node:ekr.20090426083450.10: *6* createContainer (to do)
    def createContainer (self,parent):

        pass
    #@+node:ekr.20090426083450.11: *6* createFrame
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
    #@+node:ekr.20090426083450.12: *6* createGrid
    def createGrid (self,parent,name,margin=0,spacing=0):

        w = QtGui.QGridLayout(parent)
        w.setMargin(margin)
        w.setSpacing(spacing)
        self.setName(w,name)
        return w
    #@+node:ekr.20090426083450.19: *6* createHLayout & createVLayout
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
    #@+node:ekr.20090426083450.14: *6* createLabel
    def createLabel (self,parent,name,label):

        w = QtGui.QLabel(parent)
        self.setName(w,name)
        w.setText(self.tr(label))
        return w
    #@+node:ekr.20090424085523.40: *6* createLineEdit
    def createLineEdit (self,parent,name):

        w = QtGui.QLineEdit(parent)
        w.setObjectName(name)
        return w
    #@+node:ekr.20090427060355.11: *6* createRadioButton
    def createRadioButton (self,parent,name,label):

        w = QtGui.QRadioButton(parent)
        self.setName(w,name)
        w.setText(self.tr(label))
        return w
    #@+node:ekr.20090426083450.18: *6* createStackedWidget
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
    #@+node:ekr.20090426083450.17: *6* createTabWidget
    def createTabWidget (self,parent,name,hPolicy=None,vPolicy=None):

        w = QtGui.QTabWidget(parent)
        self.setSizePolicy(w,kind1=hPolicy,kind2=vPolicy)
        self.setName(w,name)
        return w
    #@+node:ekr.20090426083450.16: *6* createText
    def createText (self,parent,name,
        # hPolicy=None,vPolicy=None,
        lineWidth = 0,
        shadow = QtGui.QFrame.Plain,
        shape = QtGui.QFrame.NoFrame,
    ):

        # w = QtGui.QTextBrowser(parent)
        c = self.leo_c
        w = QTextBrowserSubclass(parent,c,None)
        # self.setSizePolicy(w,kind1=hPolicy,kind2=vPolicy)
        w.setFrameShape(shape)
        w.setFrameShadow(shadow)
        w.setLineWidth(lineWidth)
        self.setName(w,name)
        return w
    #@+node:ekr.20090426083450.15: *6* createTreeWidget (DynamicWindow)
    def createTreeWidget (self,parent,name):

        c = self.leo_c
        # w = QtGui.QTreeWidget(parent)
        w = LeoQTreeWidget(c,parent)
        self.setSizePolicy(w)

        # 12/01/07: add new config setting.
        multiple_selection = c.config.getBool('qt-tree-multiple-selection',default=True)
        if multiple_selection:
            w.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
            w.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        else:
            w.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
            w.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
        w.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        w.setHeaderHidden(False)
        self.setName(w,name)
        return w
    #@+node:ekr.20090426183711.12: *5* log tabs
    #@+node:ekr.20090424085523.38: *6* createFindTab
    def createFindTab (self,parent):

        grid = self.createGrid(parent,'findGrid',margin=10,spacing=2)

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
            ('rb',  '&Suboutline Only', 3,1),
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
    #@+node:ekr.20090424085523.50: *6* createSpellTab
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
    #@+node:ekr.20090426183711.13: *5* utils
    #@+node:ekr.20090426083450.13: *6* setName
    def setName (self,widget,name):

        if name:
            # if not name.startswith('leo_'):
                # name = 'leo_' + name
            widget.setObjectName(name)
    #@+node:ekr.20090425072841.14: *6* setSizePolicy
    def setSizePolicy (self,widget,kind1=None,kind2=None):

        if kind1 is None: kind1 = QtGui.QSizePolicy.Ignored
        if kind2 is None: kind2 = QtGui.QSizePolicy.Ignored

        sizePolicy = QtGui.QSizePolicy(kind1,kind2)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)

        sizePolicy.setHeightForWidth(
            widget.sizePolicy().hasHeightForWidth())

        widget.setSizePolicy(sizePolicy)
    #@+node:ekr.20090424085523.48: *6* tr
    def tr(self,s):

        return QtGui.QApplication.translate(
            'MainWindow',s,None,QtGui.QApplication.UnicodeUTF8)
    #@+node:leohag.20081203210510.17: *4* do_leo_spell_btn_*
    def doSpellBtn(self, btn):
        getattr(self.leo_c.spellCommands.handler.tab, btn)() 

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
    #@+node:edward.20081129091117.1: *4* setSplitDirection (dynamicWindow)
    def setSplitDirection (self,orientation='vertical'):

        vert = orientation and orientation.lower().startswith('v')
        h,v = QtCore.Qt.Horizontal,QtCore.Qt.Vertical

        orientation1 = g.choose(vert,h,v)
        orientation2 = g.choose(vert,v,h)

        self.splitter.setOrientation(orientation1)
        self.splitter_2.setOrientation(orientation2)

        # g.trace('vert',vert)

    #@+node:ekr.20081121105001.203: *4* setStyleSheets & helper
    styleSheet_inited = False

    def setStyleSheets(self):

        trace = False
        c = self.leo_c

        sheet = c.config.getData('qt-gui-plugin-style-sheet')
        if sheet:
            sheet = '\n'.join(sheet)
            if trace: g.trace(len(sheet))
            self.ui.setStyleSheet(sheet or self.default_sheet())
        else:
            if trace: g.trace('no style sheet')
    #@+node:ekr.20081121105001.204: *5* defaultStyleSheet
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
    #@+node:ville.20090702214819.4211: *4* setLeoWindowIcon
    def setLeoWindowIcon(self):
        """ Set icon visible in title bar and task bar """
        # xxx do not use 
        self.setWindowIcon(QtGui.QIcon(g.app.leoDir + "/Icons/leoapp32.png"))
    #@+node:ekr.20100111143038.3727: *4* splitter event handlers
    def onSplitter1Moved (self,pos,index):

        c = self.leo_c
        c.frame.secondary_ratio = self.splitterMovedHelper(
            self.splitter,pos,index)

    def onSplitter2Moved (self,pos,index):

        c = self.leo_c
        c.frame.ratio = self.splitterMovedHelper(
            self.splitter_2,pos,index)

    def splitterMovedHelper(self,splitter,pos,index):

        i,j = splitter.getRange(index)
        ratio = float(pos)/float(j-i)
        # g.trace(pos,j,ratio)
        return ratio
    #@-others

#@+node:ekr.20081121105001.205: *3* class leoQtBody (leoBody)
class leoQtBody (leoFrame.leoBody):

    """A class that represents the body pane of a Qt window."""

    #@+others
    #@+node:ekr.20081121105001.206: *4*  Birth
    #@+node:ekr.20081121105001.207: *5*  ctor (qtBody)
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
            qtWidget = top.ui.richTextEdit # A QTextEdit or QTextBrowser.
            # g.trace(qtWidget)
            sw.setCurrentIndex(1)
            self.widget = w = leoQTextEditWidget(
                qtWidget,name = 'body',c=c)
            self.bodyCtrl = w # The widget as seen from Leo's core.

            # Hook up the QSyntaxHighlighter
            self.colorizer = leoQtColorizer(c,w.widget)
            qtWidget.setAcceptRichText(False)

        # Config stuff.
        self.trace_onBodyChanged = c.config.getBool('trace_onBodyChanged')
        self.setWrap(c.p)

        # For multiple body editors.
        self.editor_name = None
        self.editor_v = None
        self.numberOfEditors = 1
        self.totalNumberOfEditors = 1

        if trace: print('qtBody.__init__ %s' % self.widget)
    #@+node:ekr.20100101172327.3661: *6* setWrap (qtBody)
    def setWrap (self,p):

        if not p: return
        if self.useScintilla: return

        c = self.c
        w = c.frame.body.widget.widget
        if 1:
            # Quicker, more self-contained.
            wrap = g.scanAllAtWrapDirectives(c,p)
        else:
            d = c.scanAllDirectives(p)
            if d is None: return
            wrap = d.get('wrap')
        w.setWordWrapMode(
            g.choose(wrap,
                QtGui.QTextOption.WordWrap,
                QtGui.QTextOption.NoWrap))
    #@+node:ekr.20081121105001.208: *6* createBindings (qtBody)
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
    #@+node:ekr.20081121105001.209: *6* get_name
    def getName (self):

        return 'body-widget'
    #@+node:ekr.20081121105001.210: *4* Do-nothings (qtBody)
    def oops (self):
        g.trace('qtBody',g.callers(3))

    # Configuration will be handled by style sheets.
    def cget(self,*args,**keys):                return None
    def configure (self,*args,**keys):          pass
    #@+node:ekr.20081121105001.211: *4* High-level interface (qtBody)
    # Part 1: Corresponding to mustBeDefinedInSubclasses.
    def appendText (self,s):            return self.widget.appendText(s)
    def delete(self,i,j=None):          self.widget.delete(i,j)
    def insert(self,i,s):               return self.widget.insert(i,s)
    def get(self,i,j=None):             return self.widget.get(i,j)
    def getAllText (self):              return self.widget.getAllText()
    def getFocus (self):                return self.widget.getFocus()
    def getInsertPoint(self):           return self.widget.getInsertPoint()
    def getSelectedText (self):         return self.widget.getSelectedText()
    def getSelectionRange(self):        return self.widget.getSelectionRange()
    def getYScrollPosition (self):      return self.widget.getYScrollPosition()
    def hasSelection (self):            return self.widget.hasSelection()
    def scrollLines (self,n):           return self.widget.scrollLines(n)
    def see(self,index):                return self.widget.see(index)
    def seeInsertPoint(self):           return self.widget.seeInsertPoint()
    def setAllText (self,s,new_p=None): return self.widget.setAllText(s,new_p=new_p)
    def setBackgroundColor (self,color):return self.widget.setBackgroundColor(color)
    def setFocus (self):                return self.widget.setFocus()
    set_focus = setFocus
    def setForegroundColor (self,color):return self.widget.setForegroundColor(color)
    def setInsertPoint (self,pos):      return self.widget.setInsertPoint(pos)
    def setSelectionRange(self,*args,**keys):
        self.widget.setSelectionRange(*args,**keys)
    def setYScrollPosition (self,i):    return self.widget.setYScrollPosition(i)

    # Part 2: corresponding to mustBeDefinedInBaseClass.
    def clipboard_append(self,s):   return self.widget.clipboard_append(s)
    def clipboard_clear(self):      return self.widget.clipboard_append()
    def onChar (self, event):       return self.widget.onChar(event)

    # Part 3: do-nothings in mayBeDefinedInSubclasses.
    def bind (self,kind,*args,**keys):          return self.widget.bind(kind,*args,**keys)
    def event_generate(self,stroke):            pass
    def getWidth (self):                        return 0
    def mark_set(self,markName,i):              pass
    def setEditorColors (self,bg,fg):           pass
    def setWidth (self,width):                  pass
    def tag_add(self,tagName,i,j=None,*args):   pass
    def tag_config (self,colorName,**keys):     pass
    def tag_configure (self,colorName,**keys):  pass
    def tag_delete (self,tagName,*args,**keys): pass
    def tag_names (self, *args):                return []
    def tag_ranges(self,tagName):               return tuple()
    def tag_remove(self,tagName,i,j=None,*args):pass
    def update (self,*args,**keys):             pass
    def update_idletasks (self,*args,**keys):   pass
    def xyToPythonIndex (self,x,y):             return 0
    def yview (self,*args):                     return 0,0

    # Part 4: corresponding to mayBeDefinedInSubclasses.

    def deleteTextSelection (self): return self.widget.deleteTextSelection()

    def indexIsVisible(self,i):  # Added: 2009/7/9.
        return self.widget.indexIsVisible(i)

    def flashCharacter(self,i,bg='white',fg='red',flashes=3,delay=75):
        return self.widget(i,bg,fg,flashes,delay)

    def replace (self,i,j,s):               self.widget.replace (i,j,s)
    def rowColToGuiIndex (self,s,row,col):  return self.widget.rowColToGuiIndex(s,row,col)
    def selectAllText (self,insert=None):   self.widget.selectAllText(insert)
    def toPythonIndex (self,index):         return self.widget.toPythonIndex(index)
    toGuiIndex = toPythonIndex
    def toPythonIndexRowCol(self,index):    return self.widget.toPythonIndexRowCol(index)
    #@+node:vivainio.20091223153142.4072: *4* Completer (qtBody)
    def showCompleter(self, alternatives, selected_cb):
        """ Show 'autocompleter' widget in body

        For example::

            w.showCompleter(['hello', 'helloworld'], mycallback )

        Here, 'hello' and 'helloworld' are the presented options.

        selected_cb should typically insert the selected text (it receives as arg) to 
        the body

        """
        wdg = self.widget.widget

        # wdg:QTextEdit

        cpl = self.completer = QtGui.QCompleter(alternatives)
        cpl.setWidget(wdg)
        f = selected_cb
        cpl.connect(cpl, QtCore.SIGNAL("activated(QString)"), f)    
        cpl.complete()
        return cpl
    #@+node:ekr.20081121105001.212: *4* Editors (qtBody)
    #@+node:ekr.20081121105001.215: *5* entries
    #@+node:ekr.20081121105001.216: *6* addEditor & helper (qtBody)
    # An override of leoFrame.addEditor.

    def addEditor (self,event=None):

        '''Add another editor to the body pane.'''

        trace = False and not g.unitTesting
        bodyCtrl = self.c.frame.body.bodyCtrl # A leoQTextEditWidget
        self.editorWidgets['1'] = bodyCtrl
        c = self.c ; p = c.p
        self.totalNumberOfEditors += 1
        self.numberOfEditors += 1

        if self.totalNumberOfEditors == 2:
            # Pack the original body editor.
            w = bodyCtrl.widget
            self.packLabel(w,n=1)

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
            d = self.editorWidgets ; keys = list(d.keys())
            old_name = keys[0]
            old_wrapper = d.get(old_name)
            old_w = old_wrapper.widget
            self.injectIvars(f,old_name,p,old_wrapper)
            self.updateInjectedIvars (old_w,p)
            self.selectLabel(old_wrapper) # Immediately create the label in the old editor.

        # Switch editors.
        c.frame.body.bodyCtrl = wrapper
        self.selectLabel(wrapper)
        self.selectEditor(wrapper)
        self.updateEditors()
        c.bodyWantsFocusNow()
    #@+node:ekr.20081121105001.213: *7* createEditor
    def createEditor (self,name):

        c = self.c ; p = c.p
        f = c.frame.top.ui.leo_body_inner_frame
            # Valid regardless of qtGui.useUI
        n = self.numberOfEditors

        # Step 1: create the editor.
        # w = QtGui.QTextBrowser(f)
        w = QTextBrowserSubclass(f,c,self)
        w.setObjectName('richTextEdit') # Will be changed later.
        wrapper = leoQTextEditWidget(w,name='body',c=c)
        self.packLabel(w)

        # Step 2: inject ivars, set bindings, etc.
        self.injectIvars(f,name,p,wrapper)
        self.updateInjectedIvars(w,p)
        wrapper.setAllText(p.b)
        wrapper.see(0)
        self.createBindings(w=wrapper)
        c.k.completeAllBindingsForWidget(wrapper)
        self.recolorWidget(p,wrapper)

        return f,wrapper
    #@+node:ekr.20081121105001.218: *6* assignPositionToEditor
    def assignPositionToEditor (self,p):

        '''Called *only* from tree.select to select the present body editor.'''

        c = self.c ; cc = c.chapterController
        wrapper = c.frame.body.bodyCtrl
        w = wrapper.widget

        self.updateInjectedIvars(w,p)
        self.selectLabel(wrapper)

        # g.trace('===',id(w),w.leo_chapter.name,w.leo_p.h)
    #@+node:ekr.20081121105001.219: *6* cycleEditorFocus
    def cycleEditorFocus (self,event=None):

        '''Cycle keyboard focus between the body text editors.'''

        c = self.c ; d = self.editorWidgets
        w = c.frame.body.bodyCtrl
        values = list(d.values())
        if len(values) > 1:
            i = values.index(w) + 1
            if i == len(values): i = 0
            w2 = d.values()[i]
            assert(w!=w2)
            self.selectEditor(w2)
            c.frame.body.bodyCtrl = w2
            # g.trace('***',g.app.gui.widget_name(w2),id(w2))
    #@+node:ekr.20081121105001.220: *6* deleteEditor
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

        if len(list(d.keys())) <= 1: return

        # At present, can not delete the first column.
        if name == '1':
            g.es('can not delete leftmost editor',color='blue')
            return

        # Actually delete the widget.
        if trace: g.trace('**delete name %s id(wrapper) %s id(w) %s' % (
            name,id(wrapper),id(w)))

        del d [name]
        f = c.frame.top.ui.leo_body_inner_frame
        layout = f.layout()
        for z in (w,w.leo_label):
            self.unpackWidget(layout,z)

        # Select another editor.
        new_wrapper = list(d.values())[0]
        if trace: g.trace(wrapper,new_wrapper)
        self.numberOfEditors -= 1
        if self.numberOfEditors == 1:
            w = new_wrapper.widget
            self.unpackWidget(layout,w.leo_label)

        self.selectEditor(new_wrapper)
    #@+node:ekr.20081121105001.221: *6* findEditorForChapter (leoBody)
    def findEditorForChapter (self,chapter,p):

        '''Return an editor to be assigned to chapter.'''

        trace = False and not g.unitTesting
        c = self.c ; d = self.editorWidgets
        values = list(d.values())

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
    #@+node:ekr.20081121105001.222: *6* select/unselectLabel (leoBody)
    def unselectLabel (self,wrapper):

        pass
        # self.createChapterIvar(wrapper)

    def selectLabel (self,wrapper):

        c = self.c
        w = wrapper.widget
        lab = hasattr(w,'leo_label') and w.leo_label

        if lab:
            lab.setEnabled(True)
            lab.setText(c.p.h)
            lab.setEnabled(False)
    #@+node:ekr.20081121105001.223: *6* selectEditor & helpers
    selectEditorLockout = False

    def selectEditor(self,wrapper):

        '''Select editor w and node w.leo_p.'''

        trace = False and not g.unitTesting
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
    #@+node:ekr.20081121105001.224: *7* selectEditorHelper
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
        self.recolorWidget (w.leo_p,wrapper) # switches colorizers.
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
        #@+<< restore the selection, insertion point and the scrollbar >>
        #@+node:ekr.20081121105001.225: *8* << restore the selection, insertion point and the scrollbar >>
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
        #@-<< restore the selection, insertion point and the scrollbar >>
        c.bodyWantsFocusNow()
    #@+node:ekr.20081121105001.226: *6* updateEditors
    # Called from addEditor and assignPositionToEditor

    def updateEditors (self):

        c = self.c ; p = c.p ; body = p.b
        d = self.editorWidgets
        if len(list(d.keys())) < 2: return # There is only the main widget

        w0 = c.frame.body.bodyCtrl
        i,j = w0.getSelectionRange()
        ins = w0.getInsertPoint()
        sb0 = w0.widget.verticalScrollBar()
        pos0 = sb0.sliderPosition()
        for key in d:
            wrapper = d.get(key)
            w = wrapper.widget
            v = hasattr(w,'leo_p') and w.leo_p.v
            if v and v == p.v and w != w0:
                sb = w.verticalScrollBar()
                pos = sb.sliderPosition()
                wrapper.setAllText(body)
                self.recolorWidget(p,wrapper)
                sb.setSliderPosition(pos)

        c.bodyWantsFocusNow()
        w0.setSelectionRange(i,j,ins=ins)
        sb0.setSliderPosition(pos0)
    #@+node:ekr.20081121105001.227: *5* utils
    #@+node:ekr.20081121105001.228: *6* computeLabel
    def computeLabel (self,w):

        if hasattr(w,'leo_label'):
            s = w.leo_label.text()
        else:
            s = ''

        if hasattr(w,'leo_chapter') and w.leo_chapter:
            s = '%s: %s' % (w.leo_chapter.name,s)

        return s
    #@+node:ekr.20081121105001.229: *6* createChapterIvar
    def createChapterIvar (self,w):

        c = self.c ; cc = c.chapterController

        if hasattr(w,'leo_chapter') and w.leo_chapter:
            pass
        elif cc and self.use_chapters:
            w.leo_chapter = cc.getSelectedChapter()
        else:
            w.leo_chapter = None
    #@+node:ekr.20081121105001.231: *6* deactivateEditors
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
    #@+node:ekr.20081121105001.230: *6* ensurePositionExists
    def ensurePositionExists(self,w):

        '''Return True if w.leo_p exists or can be reconstituted.'''

        trace = True and not g.unitTesting
        c = self.c

        if c.positionExists(w.leo_p):
            return True
        else:
            if trace: g.trace('***** does not exist',w.leo_name)
            for p2 in c.all_unique_positions():
                if p2.v and p2.v == w.leo_p.v:
                    if trace: g.trace(p2.h)
                    w.leo_p = p2.copy()
                    return True
            else:
                # This *can* happen when selecting a deleted node.
                if trace: g.trace(p2.h)
                w.leo_p = c.p.copy()
                return False
    #@+node:ekr.20090318091009.14: *6* injectIvars
    def injectIvars (self,parentFrame,name,p,wrapper):

        trace = False and not g.unitTesting

        w = wrapper.widget
        assert isinstance(wrapper,leoQTextEditWidget),wrapper
        assert isinstance(w,QtGui.QTextEdit),w

        if trace: g.trace(w)

        # Inject ivars
        if name == '1':
            w.leo_p = None # Will be set when the second editor is created.
        else:
            w.leo_p = p.copy()

        w.leo_active = True
        w.leo_bodyBar = None
        w.leo_bodyXBar = None
        w.leo_chapter = None
        # w.leo_colorizer = None # Set in leoQtColorizer ctor.
        w.leo_frame = parentFrame
        w.leo_insertSpot = None
        # w.leo_label = None # Injected by packLabel.
        w.leo_name = name
        # w.leo_on_focus_in = onFocusInCallback
        w.leo_scrollBarSpot = None
        w.leo_selection = None
        w.leo_wrapper = wrapper
    #@+node:ekr.20090613111747.3633: *6* packLabel
    def packLabel (self,w,n=None):

        c = self.c
        f = c.frame.top.ui.leo_body_inner_frame
            # Valid regardless of qtGui.useUI

        if n is None:n = self.numberOfEditors
        layout = f.layout()
        f.setObjectName('editorFrame')

        # Create the text: to do: use stylesheet to set font, height.
        lab = QtGui.QLineEdit(f)
        lab.setObjectName('editorLabel')
        lab.setText(c.p.h)

        # Pack the label and the text widget.
        # layout.setHorizontalSpacing(4)
        layout.addWidget(lab,0,max(0,n-1),QtCore.Qt.AlignVCenter)
        layout.addWidget(w,1,max(0,n-1))
        layout.setRowStretch(0,0)
        layout.setRowStretch(1,1) # Give row 1 as much as possible.

        w.leo_label = lab # Inject the ivar.
    #@+node:ekr.20081121105001.232: *6* recolorWidget
    def recolorWidget (self,p,wrapper):

        trace = False and not g.unitTesting
        c = self.c

        # Save.
        old_wrapper = c.frame.body.bodyCtrl
        c.frame.body.bodyCtrl = wrapper
        w = wrapper.widget

        if not hasattr(w,'leo_colorizer'):
            if trace: g.trace('*** creating colorizer for',w)
            leoQtColorizer(c,w) # injects w.leo_colorizer
            assert hasattr(w,'leo_colorizer'),w

        c.frame.body.colorizer = w.leo_colorizer
        if trace: g.trace(w,c.frame.body.colorizer)

        try:
            # c.recolor_now(interruptable=False) # Force a complete recoloring.
            c.frame.body.colorizer.colorize(p,incremental=False,interruptable=False)
        finally:
            # Restore.
            c.frame.body.bodyCtrl = old_wrapper
    #@+node:ekr.20081121105001.233: *6* switchToChapter (leoBody)
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
    #@+node:ekr.20081121105001.234: *6* updateInjectedIvars
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
    #@+node:ekr.20090614060655.3660: *6* unpackWidget
    def unpackWidget (self,layout,w):

        index = layout.indexOf(w)
        item = layout.itemAt(index)
        item.setGeometry(QtCore.QRect(0,0,0,0))
        layout.removeItem(item)
    #@+node:ekr.20090406071640.13: *4* Event handlers (qtBody)
    def onFocusIn (self,obj):

        '''Handle a focus-in event in the body pane.'''

        trace = False and not g.unitTesting

        c = self.c
        if trace: g.trace(c.p.h) # obj,obj.objectName())

        # 2010/08/01: Update the history only on focus in events.
        c.nodeHistory.update(c.p)

        if obj.objectName() == 'richTextEdit':
            wrapper = hasattr(obj,'leo_wrapper') and obj.leo_wrapper
            if wrapper and wrapper != self.bodyCtrl:
                self.selectEditor(wrapper)
            self.onFocusColorHelper('focus-in',obj)
            obj.setReadOnly(False)
            obj.setFocus() # Weird, but apparently necessary.

    def onFocusOut (self,obj):

        '''Handle a focus-out event in the body pane.'''

        if obj.objectName() == 'richTextEdit':
            self.onFocusColorHelper('focus-out',obj)
            obj.setReadOnly(True)
    #@+node:ekr.20090608052916.3810: *5* onFocusColorHelper
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
    #@-others
#@+node:ekr.20081121105001.235: *3* class leoQtFindTab (findTab)
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

    #@+others
    #@+node:ekr.20081121105001.236: *4*  Birth: called from leoFind ctor
    # leoFind.__init__ calls initGui, createFrame, createBindings & init, in that order.
    #@+node:ekr.20081121105001.237: *5* initGui
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
    #@+node:ekr.20081121105001.238: *5* init (qtFindTab) & helpers
    def init (self,c):

        '''Init the widgets of the 'Find' tab.'''

        # g.trace('leoQtFindTab.init')

        self.createIvars()
        self.initIvars()
        self.initTextWidgets()
        self.initCheckBoxes()
        self.initRadioButtons()
    #@+node:ekr.20081121105001.239: *6* createIvars (qtFindTab)
    def createIvars (self):

        c = self.c ; w = c.frame.top.ui # A Window ui object.

        # Bind boxes to Window objects.
        self.widgetsDict = {} # Keys are ivars, values are Qt widgets.
        findWrapper   = findTextWrapper(w.findPattern,'find-widget',c)
        changeWrapper = findTextWrapper(w.findChange,'change-widget',c)
        if 0: # Not yet.
            findWrapper.setTabWidget(changeWrapper)
            findWrapper.setReturnCommand = None
            changeWrapper.setTabWidget(findWrapper)
        data = (
            ('find_ctrl',       findWrapper),
            ('change_ctrl',     changeWrapper),
            ('whole_word',      w.checkBoxWholeWord),
            ('ignore_case',     w.checkBoxIgnoreCase),
            ('wrap',            w.checkBoxWrapAround),
            ('reverse',         w.checkBoxReverse),
            ('pattern_match',   w.checkBoxRegexp),
            ('mark_finds',      w.checkBoxMarkFinds),
            ('entire_outline',  w.checkBoxEntireOutline),
            ('suboutline_only', w.checkBoxSuboutlineOnly),  
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
    #@+node:ekr.20081121105001.240: *6* initIvars
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
    #@+node:ekr.20081121105001.241: *6* initTextWidgets
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
    #@+node:ekr.20081121105001.242: *6* initCheckBoxes
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
    #@+node:ekr.20081121105001.243: *6* initRadioButtons
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
    #@+node:ekr.20081121105001.244: *4* class svar
    class svar:
        '''A class like Tk's IntVar and StringVar classes.'''

        #@+others
        #@+node:ekr.20090427112929.10: *5* svar.ctor
        def __init__(self,owner,ivar):

            self.ivar = ivar
            self.owner = owner
            self.radioButtons = ['node_only','suboutline_only','entire_outline']
            self.trace = False
            self.val = None
            self.w = None

        def __repr__(self):
            return '<svar %s>' % self.ivar
        #@+node:ekr.20090427112929.12: *5* get
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
        #@+node:ekr.20090427112929.13: *5* init
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
        #@+node:ekr.20090427112929.17: *5* set
        def set (self,val):

            '''Init the svar and update the radio buttons.'''

            trace = False and not g.unitTesting
            if trace: g.trace(val)

            self.init(val)

            if self.ivar in self.radioButtons:
                self.owner.initRadioButtons()
            elif self.ivar == 'radio-search-scope':
                self.setRadioScope(val)


        #@+node:ekr.20090427112929.18: *5* setRadioScope
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
        #@+node:ekr.20090427112929.15: *5* setWidget
        def setWidget(self,w):

            self.w = w
        #@-others

    #@+node:ekr.20081121105001.245: *4* Support for minibufferFind class (qtFindTab)
    # This is the same as the Tk code because we simulate Tk svars.
    #@+node:ekr.20081121105001.246: *5* getOption
    def getOption (self,ivar):

        var = self.svarDict.get(ivar)

        if var:
            val = var.get()
            # g.trace('ivar %s = %s' % (ivar,val))
            return val
        else:
            # g.trace('bad ivar name: %s' % ivar)
            return None
    #@+node:ekr.20081121105001.247: *5* setOption
    def setOption (self,ivar,val):

        trace = True and not g.unitTesting
        if trace: g.trace(ivar,val)

        if ivar in self.intKeys:
            if val is not None:
                svar = self.svarDict.get(ivar)
                svar.set(val)
                if trace: g.trace('qtFindTab: ivar %s = %s' % (
                    ivar,val))

        elif not g.app.unitTesting:
            g.trace('oops: bad find ivar %s' % ivar)
    #@+node:ekr.20081121105001.248: *5* toggleOption
    def toggleOption (self,ivar):

        if ivar in self.intKeys:
            var = self.svarDict.get(ivar)
            val = not var.get()
            var.set(val)
            # g.trace('%s = %s' % (ivar,val),var)
        else:
            g.trace('oops: bad find ivar %s' % ivar)
    #@-others
#@+node:ekr.20081121105001.249: *3* class leoQtFrame
class leoQtFrame (leoFrame.leoFrame):

    """A class that represents a Leo window rendered in qt."""

    #@+others
    #@+node:ekr.20081121105001.250: *4*  Birth & Death (qtFrame)
    #@+node:ekr.20081121105001.251: *5* __init__ (qtFrame)
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

        #@+<< set the leoQtFrame ivars >>
        #@+node:ekr.20081121105001.252: *6* << set the leoQtFrame ivars >> (removed frame.bodyCtrl ivar)
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
        #@-<< set the leoQtFrame ivars >>

        self.minibufferVisible = True
    #@+node:ekr.20081121105001.253: *5* __repr__ (qtFrame)
    def __repr__ (self):

        return "<leoQtFrame: %s>" % self.title
    #@+node:ekr.20081121105001.254: *5* qtFrame.finishCreate & helpers
    def finishCreate (self,c):

        f = self ; f.c = c

        # g.trace('(qtFrame)')

        # self.bigTree         = c.config.getBool('big_outline_pane')
        self.trace_status_line = c.config.getBool('trace_status_line')
        self.use_chapters      = c.config.getBool('use_chapters')
        self.use_chapter_tabs  = c.config.getBool('use_chapter_tabs')

        # returns DynamicWindow
        f.top = g.app.gui.frameFactory.createFrame(f)
        # g.trace('(leoQtFrame)',f.top)

        # hiding would remove flicker, but doesn't work with all
        # window managers

        f.createIconBar() # A base class method.
        f.createSplitterComponents()
        cc = c.chapterController
        # g.trace(cc,cc.findChaptersNode())
        if 0: # 2010/06/17: Now done in cc.createChaptersNode.
            if f.use_chapters and f.use_chapter_tabs: # and cc and cc.findChaptersNode():
                cc.tt = leoQtTreeTab(c,f.iconBar)
        f.createStatusLine() # A base class method.
        f.createFirstTreeNode() # Call the base-class method.
        f.menu = leoQtMenu(f)
        c.setLog()
        g.app.windowList.append(f)
        f.miniBufferWidget = leoQtMinibuffer(c)
        c.bodyWantsFocusNow()
    #@+node:ekr.20081121105001.255: *6* createSplitterComponents (qtFrame)
    def createSplitterComponents (self):

        f = self ; c = f.c

        f.tree  = leoQtTree(c,f)
        f.log   = leoQtLog(f,None)
        f.body  = leoQtBody(f,None)

        if f.use_chapters:
            c.chapterController = cc = leoChapters.chapterController(c)

        f.splitVerticalFlag,f.ratio,f.secondary_ratio = f.initialRatios()
        f.resizePanesToRatio(f.ratio,f.secondary_ratio)
    #@+node:ekr.20081121105001.256: *5* initCompleteHint
    def initCompleteHint (self):

        '''A kludge: called to enable text changed events.'''

        self.initComplete = True
        # g.trace(self.c)
    #@+node:ekr.20081121105001.257: *5* Destroying the qtFrame
    #@+node:ekr.20081121105001.258: *6* destroyAllObjects
    def destroyAllObjects (self):

        """Clear all links to objects in a Leo window."""

        frame = self ; c = self.c

        # g.printGcAll()

        # Do this first.
        #@+<< clear all vnodes in the tree >>
        #@+node:ekr.20081121105001.259: *7* << clear all vnodes in the tree>>
        vList = [z for z in c.all_unique_nodes()]

        for v in vList:
            g.clearAllIvars(v)

        vList = [] # Remove these references immediately.
        #@-<< clear all vnodes in the tree >>

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

    #@+node:ekr.20081121105001.260: *6* destroySelf (qtFrame)
    def destroySelf (self):

        # Remember these: we are about to destroy all of our ivars!
        c,top = self.c,self.top 

        g.app.gui.frameFactory.deleteFrame(top)
        # Indicate that the commander is no longer valid.
        c.exists = False

        if 0: # We can't do this unless we unhook the event filter.
            # Destroys all the objects of the commander.
            self.destroyAllObjects()

        c.exists = False # Make sure this one ivar has not been destroyed.

        # g.trace('qtFrame',c,g.callers(4))
        top.close()


    #@+node:ekr.20081121105001.261: *4* class qtStatusLineClass (qtFrame)
    class qtStatusLineClass:

        '''A class representing the status line.'''

        #@+others
        #@+node:ekr.20081121105001.262: *5* ctor
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
        #@+node:ekr.20081121105001.263: *5*  do-nothings
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

        #@+node:ekr.20081121105001.264: *5* clear, get & put/1
        def clear (self):
            self.put('')

        def get (self):
            return self.textWidget2.text()

        def put(self,s,color=None):
            self.put_helper(s,self.textWidget2)

        def put1(self,s,color=None):
            self.put_helper(s,self.textWidget1)

        def put_helper(self,s,w):
            w.setText(s)
        #@+node:ekr.20081121105001.265: *5* update
        def update (self):
            if g.app.killed: return

            c = self.c ; body = c.frame.body

            # te is a QTextEdit.
            # 2010/02/19: Fix bug 525090
            # An added editor window doesn't display line/col
            if not hasattr(body.bodyCtrl,'widget'): return
            te = body.bodyCtrl.widget # was body.widget.widget
            cr = te.textCursor()
            bl = cr.block()

            col = cr.columnNumber()
            row = bl.blockNumber() + 1
            line = bl.text()

            if col > 0:
                s2 = line[0:col]        
                col = g.computeWidth (s2,c.tab_width)
            fcol = col + c.currentPosition().textOffset()

            # g.trace('fcol',fcol,'te',id(te),g.callers(2))
            # g.trace('c.frame.body.bodyCtrl',body.bodyCtrl)

            self.put1(
                "line: %d, col: %d, fcol: %d" % (row,col,fcol))
            self.lastRow = row
            self.lastCol = col
            self.lastFcol = fcol
        #@-others
    #@+node:ekr.20081121105001.266: *4* class qtIconBarClass
    class qtIconBarClass:

        '''A class representing the singleton Icon bar'''

        #@+others
        #@+node:ekr.20081121105001.267: *5*  ctor
        def __init__ (self,c,parentFrame):

            # g.trace('(qtIconBarClass)')

            self.c = c
            self.chapterController = None
            self.parentFrame = parentFrame
            self.toolbar = self
            self.w = c.frame.top.iconBar # A QToolBar.
            self.actions = []

            # Options
            self.buttonColor = c.config.getString('qt-button-color')

            # g.app.iconWidgetCount = 0
        #@+node:ekr.20081121105001.268: *5*  do-nothings
        def addRow(self,height=None):   pass
        def getFrame (self):            return None
        def getNewFrame (self):         return None
        def pack (self):                pass
        def unpack (self):              pass

        hide = unpack
        show = pack
        #@+node:ekr.20081121105001.269: *5* add
        def add(self,*args,**keys):

            '''Add a button to the icon bar.'''

            c = self.c
            command = keys.get('command')
            text = keys.get('text')
            # able to specify low-level QAction directly (QPushButton not forced)
            qaction = keys.get('qaction')

            if not text and not qaction:
                g.es('bad toolbar item')

            bg = keys.get('bg') or self.toolbar.buttonColor

            # imagefile = keys.get('imagefile')
            # image = keys.get('image')

            class leoIconBarButton (QtGui.QWidgetAction):
                def __init__ (self,parent,text,toolbar):
                    QtGui.QWidgetAction.__init__(self,parent)
                    self.button = None # set below
                    self.text = text
                    self.toolbar = toolbar
                def createWidget (self,parent):
                    # g.trace('leoIconBarButton',self.toolbar.buttonColor)
                    self.button = b = QtGui.QPushButton(self.text,parent)
                    g.app.gui.setWidgetColor(b,
                        widgetKind='QPushButton',
                        selector='background-color',
                        colorName = bg)
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
                    # g.trace('command',command.__name__)
                    val = command()
                    if c.exists:
                        # c.bodyWantsFocus()
                        c.outerUpdate()
                    return val

                self.w.connect(b,
                    QtCore.SIGNAL("clicked()"),
                    button_callback)

            return action
        #@+node:ekr.20081121105001.270: *5* addRowIfNeeded
        def addRowIfNeeded (self):

            '''Add a new icon row if there are too many widgets.'''

            # n = g.app.iconWidgetCount

            # if n >= self.widgets_per_row:
                # g.app.iconWidgetCount = 0
                # self.addRow()

            # g.app.iconWidgetCount += 1
        #@+node:ekr.20081121105001.271: *5* addWidget
        def addWidget (self,w):

            self.w.addWidget(w)
        #@+node:ekr.20081121105001.272: *5* clear
        def clear(self):

            """Destroy all the widgets in the icon bar"""

            self.w.clear()
            self.actions = []

            g.app.iconWidgetCount = 0
        #@+node:ekr.20100618162506.3716: *5* createChaptersIcon
        def createChaptersIcon(self):

            # g.trace('(qtIconBarClass)')

            c = self.c
            cc = c.chapterController
            f = c.frame

            if f.use_chapters and f.use_chapter_tabs: # and cc and cc.findChaptersNode():
                cc.tt = leoQtTreeTab(c,f.iconBar)
        #@+node:ekr.20081121105001.273: *5* deleteButton
        def deleteButton (self,w):
            """ w is button """

            #g.trace(w, '##')    

            self.w.removeAction(w)

            self.c.bodyWantsFocus()
            self.c.outerUpdate()
        #@+node:ekr.20081121105001.274: *5* setCommandForButton
        def setCommandForButton(self,button,command):

            if command:
                # button is a leoIconBarButton.
                QtCore.QObject.connect(button.button,
                    QtCore.SIGNAL("clicked()"),command)

                if not hasattr(command, 'p'):
                    # can get here from @buttons in the current outline, in which
                    # case p exists, or from @buttons in @settings elsewhere, in
                    # which case it doesn't

                    return

                # 20100518 - TNB command is instance of callable class with
                #   a c and p attribute, so we can add a context menu item...
                def goto_command(command = command):
                    command.c.selectPosition(command.p)
                    command.c.redraw()
                b = button.button
                b.goto_script = gts = QtGui.QAction('Goto Script', b)
                b.addAction(gts)
                gts.connect(gts, QtCore.SIGNAL("triggered()"), goto_command)

                # 20100519 - TNB also, scan @button's following sibs and childs
                #   for @rclick nodes
                rclicks = []
                if '@others' not in command.p.b:
                    rclicks.extend([i.copy() for i in command.p.children()
                      if i.h.startswith('@rclick ')])
                for i in command.p.following_siblings():
                    if i.h.startswith('@rclick '):
                        rclicks.append(i.copy())
                    else:
                        break

                if rclicks:
                    b.setText(unicode(b.text())+(command.c.config.getString('mod_scripting_subtext') or ''))

                for rclick in rclicks:

                    def cb(event=None, ctrl=command.controller, p=rclick, 
                           c=command.c, b=command.b, t=rclick.h[8:]):
                        ctrl.executeScriptFromButton(p,b,t)
                        if c.exists:
                            c.outerUpdate()

                    rc = QtGui.QAction(rclick.h[8:], b)
                    rc.connect(rc, QtCore.SIGNAL("triggered()"), cb)
                    b.insertAction(b.actions()[-2], rc)  # insert rc before Remove Button

                    # k.registerCommand(buttonText.lower(),
                    #   shortcut=shortcut,func=atButtonCallback,
                    #   pane='button',verbose=verbose)
        #@-others
    #@+node:ekr.20081121105001.275: *4* Minibuffer methods
    #@+node:ekr.20081121105001.276: *5* showMinibuffer
    def showMinibuffer (self):

        '''Make the minibuffer visible.'''

        # frame = self

        # if not frame.minibufferVisible:
            # frame.minibufferFrame.pack(side='bottom',fill='x')
            # frame.minibufferVisible = True
    #@+node:ekr.20081121105001.277: *5* hideMinibuffer
    def hideMinibuffer (self):

        '''Hide the minibuffer.'''

        # frame = self

        # if frame.minibufferVisible:
            # frame.minibufferFrame.pack_forget()
            # frame.minibufferVisible = False
    #@+node:ekr.20081121105001.278: *5* f.setMinibufferBindings
    def setMinibufferBindings (self):

        '''Create bindings for the minibuffer..'''

        pass
    #@+node:ekr.20081121105001.279: *4* Configuration (qtFrame)
    #@+node:ekr.20081121105001.280: *5* configureBar (qtFrame)
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
    #@+node:ekr.20081121105001.281: *5* configureBarsFromConfig (qtFrame)
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
    #@+node:ekr.20081121105001.282: *5* reconfigureFromConfig (qtFrame)
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
    #@+node:ekr.20081121105001.283: *5* setInitialWindowGeometry (qtFrame)
    def setInitialWindowGeometry(self):

        """Set the position and size of the frame to config params."""

        c = self.c

        h = c.config.getInt("initial_window_height") or 500
        w = c.config.getInt("initial_window_width") or 600
        x = c.config.getInt("initial_window_left") or 10
        y = c.config.getInt("initial_window_top") or 10

        if h and w and x and y:
            self.setTopGeometry(w,h,x,y)
    #@+node:ekr.20081121105001.284: *5* setTabWidth (qtFrame)
    def setTabWidth (self, w):

        # A do-nothing because tab width is set automatically.
        pass

    #@+node:ekr.20081121105001.285: *5* setWrap (qtFrame)
    def setWrap (self,p):

        self.c.frame.body.setWrap(p)
    #@+node:ekr.20081121105001.286: *5* reconfigurePanes (qtFrame)
    def reconfigurePanes (self):

        f = self ; c = f.c

        if f.splitVerticalFlag:
            r = c.config.getRatio("initial_vertical_ratio")
            if r == None or r < 0.0 or r > 1.0: r = 0.5
            r2 = c.config.getRatio("initial_vertical_secondary_ratio")
            if r2 == None or r2 < 0.0 or r2 > 1.0: r2 = 0.8
        else:
            r = c.config.getRatio("initial_horizontal_ratio")
            if r == None or r < 0.0 or r > 1.0: r = 0.3
            r2 = c.config.getRatio("initial_horizontal_secondary_ratio")
            if r2 == None or r2 < 0.0 or r2 > 1.0: r2 = 0.8

        f.ratio,f.secondary_ratio = r,r2
        f.resizePanesToRatio(r,r2)
    #@+node:ekr.20081121105001.287: *5* resizePanesToRatio (qtFrame)
    def resizePanesToRatio(self,ratio,ratio2):

        trace = False and not g.unitTesting

        f = self ; c = self.c

        if trace: g.trace('%5s, %0.2f %0.2f' % (
            self.splitVerticalFlag,ratio,ratio2),g.callers(4))

        f.divideLeoSplitter(self.splitVerticalFlag,ratio)
        f.divideLeoSplitter(not self.splitVerticalFlag,ratio2)

        # g.trace(ratio,c)
    #@+node:leohag.20081208130321.12: *5* divideLeoSplitter
    # Divides the main or secondary splitter, using the key invariant.
    def divideLeoSplitter (self, verticalFlag, frac):

        # g.trace(verticalFlag,frac)

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

    #@+node:leohag.20081208130321.13: *5* divideAnySplitter
    # This is the general-purpose placer for splitters.
    # It is the only general-purpose splitter code in Leo.

    def divideAnySplitter (self,frac,splitter):

        sizes = splitter.sizes()

        if len(sizes)!=2:
            g.trace('%s widget(s) in %s' % (len(sizes),id(splitter)))

        if frac > 1 or frac < 0:
            g.trace('split ratio [%s] out of range 0 <= frac <= 1'%frac)

        s1, s2 = sizes
        s = s1+s2
        s1 = int(s * frac + 0.5)
        s2 = s - s1 

        splitter.setSizes([s1,s2])
    #@+node:ekr.20081121105001.288: *4* Event handlers (qtFrame)
    #@+node:ekr.20081121105001.289: *5* frame.OnCloseLeoEvent
    # Called from quit logic and when user closes the window.
    # Returns True if the close happened.

    def OnCloseLeoEvent(self):

        f = self ; c = f.c

        if c.inCommand:
            # g.trace('requesting window close')
            c.requestCloseWindow = True
        else:
            g.app.closeLeoWindow(self)
    #@+node:ekr.20081121105001.290: *5* frame.OnControlKeyUp/Down
    def OnControlKeyDown (self,event=None):

        self.controlKeyIsDown = True

    def OnControlKeyUp (self,event=None):

        self.controlKeyIsDown = False
    #@+node:ekr.20081121105001.291: *5* OnActivateBody (qtFrame)
    def OnActivateBody (self,event=None):

        pass
    #@+node:ekr.20081121105001.292: *5* OnActivateLeoEvent, OnDeactivateLeoEvent
    def OnActivateLeoEvent(self,event=None):

        '''Handle a click anywhere in the Leo window.'''

        self.c.setLog()

    def OnDeactivateLeoEvent(self,event=None):

        pass # This causes problems on the Mac.
    #@+node:ekr.20081121105001.293: *5* OnActivateTree
    def OnActivateTree (self,event=None):

        pass
    #@+node:ekr.20081121105001.294: *5* OnBodyClick, OnBodyRClick (not used)
    # At present, these are not called,
    # but they could be called by QTextBrowserSubclass.

    def OnBodyClick (self,event=None):

        try:
            c = self.c ; p = c.currentPosition()
            if g.doHook("bodyclick1",c=c,p=p,v=p,event=event):
                g.doHook("bodyclick2",c=c,p=p,v=p,event=event)
                return 'break'
            else:
                self.OnActivateBody(event=event)
                c.k.showStateAndMode(w=c.frame.body.bodyCtrl)
                g.doHook("bodyclick2",c=c,p=p,v=p,event=event)
        except:
            g.es_event_exception("bodyclick")

    def OnBodyRClick(self,event=None):

        try:
            c = self.c ; p = c.currentPosition()
            if g.doHook("bodyrclick1",c=c,p=p,v=p,event=event):
                g.doHook("bodyrclick2",c=c,p=p,v=p,event=event)
                return 'break'
            else:
                c.k.showStateAndMode(w=c.frame.body.bodyCtrl)
                g.doHook("bodyrclick2",c=c,p=p,v=p,event=event)
        except:
            g.es_event_exception("iconrclick")
    #@+node:ekr.20081121105001.295: *5* OnBodyDoubleClick (Events) (not used)
    # Not called

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
    #@+node:ekr.20081121105001.296: *4* Gui-dependent commands
    #@+node:ekr.20081121105001.297: *5* Minibuffer commands... (qtFrame)
    #@+node:ekr.20081121105001.298: *6* contractPane
    def contractPane (self,event=None):

        '''Contract the selected pane.'''

        f = self ; c = f.c

        w = c.get_requested_focus() or g.app.gui.get_focus(c)
        wname = c.widget_name(w)

        # g.trace(wname)
        if not w: return

        if wname.startswith('body'):
            f.contractBodyPane()
            c.bodyWantsFocusNow()
        elif wname.startswith('log'):
            f.contractLogPane()
            c.logWantsFocusNow()
        else:
            for z in ('head','canvas','tree'):
                if wname.startswith(z):
                    f.contractOutlinePane()
                    c.treeWantsFocusNow()
                    break
    #@+node:ekr.20081121105001.299: *6* expandPane
    def expandPane (self,event=None):

        '''Expand the selected pane.'''

        f = self ; c = f.c

        w = c.get_requested_focus() or g.app.gui.get_focus(c)
        wname = c.widget_name(w)

        # g.trace(wname)
        if not w: return

        if wname.startswith('body'):
            f.expandBodyPane()
            c.bodyWantsFocusNow()
        elif wname.startswith('log'):
            f.expandLogPane()
            c.logWantsFocusNow()
        else:
            for z in ('head','canvas','tree'):
                if wname.startswith(z):
                    f.expandOutlinePane()
                    c.treeWantsFocusNow()
                    break
    #@+node:ekr.20081121105001.300: *6* fullyExpandPane
    def fullyExpandPane (self,event=None):

        '''Fully expand the selected pane.'''

        f = self ; c = f.c

        w = c.get_requested_focus() or g.app.gui.get_focus(c)
        wname = c.widget_name(w)

        # g.trace(wname)
        if not w: return

        if wname.startswith('body'):
            f.fullyExpandBodyPane()
            c.treeWantsFocusNow()
        elif wname.startswith('log'):
            f.fullyExpandLogPane()
            c.bodyWantsFocusNow()
        else:
            for z in ('head','canvas','tree'):
                if wname.startswith(z):
                    f.fullyExpandOutlinePane()
                    c.bodyWantsFocusNow()
                    break
    #@+node:ekr.20081121105001.301: *6* hidePane
    def hidePane (self,event=None):

        '''Completely contract the selected pane.'''

        f = self ; c = f.c

        w = c.get_requested_focus() or g.app.gui.get_focus(c)
        wname = c.widget_name(w)

        # g.trace(wname)
        if not w: return

        if wname.startswith('body'):
            f.hideBodyPane()
            c.treeWantsFocusNow()
        elif wname.startswith('log'):
            f.hideLogPane()
            c.bodyWantsFocusNow()
        else:
            for z in ('head','canvas','tree'):
                if wname.startswith(z):
                    f.hideOutlinePane()
                    c.bodyWantsFocusNow()
                    break
    #@+node:ekr.20081121105001.302: *6* expand/contract/hide...Pane
    #@+at The first arg to divideLeoSplitter means the following:
    # 
    #     f.splitVerticalFlag: use the primary   (tree/body) ratio.
    # not f.splitVerticalFlag: use the secondary (tree/log) ratio.
    #@@c

    def contractBodyPane (self,event=None):
        '''Contract the body pane.'''
        f = self ; r = min(1.0,f.ratio+0.1)
        f.divideLeoSplitter(f.splitVerticalFlag,r)

    def contractLogPane (self,event=None):
        '''Contract the log pane.'''
        f = self ; r = min(1.0,f.secondary_ratio+0.1) # 2010/02/23: was f.ratio
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
        f = self ; r = max(0.0,f.secondary_ratio-0.1) # 2010/02/23: was f.ratio
        f.divideLeoSplitter(not f.splitVerticalFlag,r)

    def expandOutlinePane (self,event=None):
        '''Expand the outline pane.'''
        self.contractBodyPane()
    #@+node:ekr.20081121105001.303: *6* fullyExpand/hide...Pane
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
    #@+node:ekr.20081121105001.304: *5* Window Menu...
    #@+node:ekr.20081121105001.305: *6* toggleActivePane (qtFrame)
    def toggleActivePane (self,event=None):

        '''Toggle the focus between the outline and body panes.'''

        frame = self ; c = frame.c
        w = c.get_focus()

        # g.trace(w,c.frame.body.bodyCtrl.widget)

        if w == frame.body.bodyCtrl.widget:
            c.treeWantsFocusNow()
        else:
            c.endEditing()
            c.bodyWantsFocusNow()
    #@+node:ekr.20081121105001.306: *6* cascade
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
    #@+node:ekr.20081121105001.307: *6* equalSizedPanes
    def equalSizedPanes (self,event=None):

        '''Make the outline and body panes have the same size.'''

        frame = self
        frame.resizePanesToRatio(0.5,frame.secondary_ratio)
    #@+node:ekr.20081121105001.308: *6* hideLogWindow
    def hideLogWindow (self,event=None):

        frame = self

        frame.divideLeoSplitter2(0.99, not frame.splitVerticalFlag)
    #@+node:ekr.20081121105001.309: *6* minimizeAll
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
    #@+node:ekr.20081121105001.310: *6* toggleSplitDirection (qtFrame)
    def toggleSplitDirection (self,event=None):

        '''Toggle the split direction in the present Leo window.'''

        f = self ; top = f.top

        for w in (top.splitter,top.splitter_2):
            w.setOrientation(
                g.choose(w.orientation() == QtCore.Qt.Horizontal,
                    QtCore.Qt.Vertical,QtCore.Qt.Horizontal))

        # The key invariant: self.splitVerticalFlag
        # tells the alignment of the main splitter.
        f.splitVerticalFlag = not f.splitVerticalFlag
        f.reconfigurePanes()
    #@+node:ekr.20081121105001.312: *6* resizeToScreen
    def resizeToScreen (self,event=None):

        '''Resize the Leo window so it fill the entire screen.'''

        top = self.top
    #@+node:ekr.20081121105001.313: *5* Help Menu...
    #@+node:ekr.20081121105001.314: *6* leoHelp
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
                    url = "http://prdownloads.sourceforge.net/leo/sbooks.chm?download"
                    import webbrowser
                    os.chdir(g.app.loadDir)
                    webbrowser.open_new(url)
                except:
                    if 0:
                        g.es("exception downloading","sbooks.chm")
                        g.es_exception()
    #@+node:ekr.20081121105001.317: *4* Qt bindings... (qtFrame)
    def bringToFront (self):
        self.lift()
    def deiconify (self):
        if self.top.isMinimized(): # Bug fix: 400739.
            self.lift()
    def getFocus(self):
        return g.app.gui.get_focus(self.c) # Bug fix: 2009/6/30.
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
        # g.trace(self.c,'\n',g.callers(9))
        if self.top.isMinimized(): # Bug 379141
            self.top.showNormal()
        self.top.activateWindow()
        self.top.raise_()
    def update (self):
        pass
    def getTitle (self):
        s = g.u(self.top.windowTitle())
        # g.trace('qtFrame',repr(s))
        return s
    def setTitle (self,s):
        # g.trace('qtFrame',repr(s))
        self.top.setWindowTitle(s)
    def setTopGeometry(self,w,h,x,y,adjustSize=True):
        # g.trace(x,y,w,y,g.callers(5))
        self.top.setGeometry(QtCore.QRect(x,y,w,h))
    #@-others
#@+node:ekr.20081121105001.318: *3* class leoQtLog
class leoQtLog (leoFrame.leoLog):

    """A class that represents the log pane of a Qt window."""

    #@+others
    #@+node:ekr.20081121105001.319: *4* qtLog Birth
    #@+node:ekr.20081121105001.320: *5* qtLog.__init__
    def __init__ (self,frame,parentFrame):

        # g.trace("leoQtLog")

        # Call the base class constructor and calls createControl.
        leoFrame.leoLog.__init__(self,frame,parentFrame)

        self.c = c = frame.c # Also set in the base constructor, but we need it here.
        self.logCtrl = None # The text area for log messages.

        self.contentsDict = {} # Keys are tab names.  Values are widgets.
        self.eventFilters = [] # Apparently needed to make filters work!
        self.logDict = {} # Keys are tab names text widgets.  Values are the widgets.
        self.menu = None # A menu that pops up on right clicks in the hull or in tabs.

        self.tabWidget = tw = c.frame.top.ui.tabWidget
            # The Qt.TabWidget that holds all the tabs.
        self.wrap = g.choose(c.config.getBool('log_pane_wraps'),True,False)

        # g.trace('qtLog.__init__',self.tabWidget)

        if 0: # Not needed to make onActivateEvent work.
            # Works only for .tabWidget, *not* the individual tabs!
            theFilter = leoQtEventFilter(c,w=tw,tag='tabWidget')
            tw.installEventFilter(theFilter)

        self.setFontFromConfig()
        self.setColorFromConfig()
    #@+node:ekr.20081121105001.321: *5* qtLog.finishCreate
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
        # log.selectTab('Log')
        log.createTab('Log')
        logWidget = self.contentsDict.get('Log')
        logWidget.setWordWrapMode(
            g.choose(self.wrap,
                QtGui.QTextOption.WordWrap,
                QtGui.QTextOption.NoWrap))

        for i in range(w.count()):
            if w.tabText(i) == 'Log':
                w.removeTab(i)
        w.insertTab(0,logWidget,'Log')

        c.searchCommands.openFindTab(show=False)
        c.spellCommands.openSpellTab()
    #@+node:ekr.20090627090950.3716: *5* qtLog.getName
    def getName (self):
        return 'log' # Required for proper pane bindings.
    #@+node:ekr.20081121105001.322: *4* Do nothings (logCtrl)
    #@+node:ekr.20081121105001.323: *5* Config
    # These will probably be replaced by style sheets.

    def configureBorder(self,border):               pass
    def configureFont(self,font):                   pass
    def getFontConfig (self):                       pass
    def setColorFromConfig (self):                  pass
    def SetWidgetFontFromConfig (self,logCtrl=None): pass
    def saveAllState (self):                        pass
    def restoreAllState (self,d):                   pass
    #@+node:ekr.20081121105001.324: *5* Focus & update
    def onActivateLog (self,event=None):    pass
    def hasFocus (self):                    return None
    def forceLogUpdate (self,s):            pass
    #@+node:ekr.20090627090950.3717: *4* High-level interface (qtLog)
    # Part 1: Corresponding to mustBeDefinedInSubclasses.
    def appendText(self,s):             self.logCtrl.appendText(s)
    def delete(self,i,j=None):          self.logCtrl.delete(i,j)
    def insert(self,i,s):               self.logCtrl.insert(i,s)
    def get(self,i,j):                  return self.logCtrl.get(i,j)
    def getAllText(self):               return self.logCtrl.getAllText()
    def getFocus(self):                 return self.logCtrl.getFocus()
    def getInsertPoint(self):           return self.logCtrl.getInsertPoint()
    def getSelectedText(self):          return self.logCtrl.getSelectedText()
    def getSelectionRange (self):       return self.logCtrl.getSelectionRange()
    def getYScrollPosition (self):      return self.logCtrl.getYScrollPosition()
    def hasSelection(self):             return self.logCtrl.hasSelection()
    def scrollLines(self,n):            self.logCtrl.scrollLines(n)
    def see(self,i):                    self.logCtrl.see(i)
    def seeInsertPoint (self):          self.logCtrl.seeInsertPoint()
    def setAllText (self,s):            self.logCtrl.setAllText(s)
    def setBackgroundColor(self,color): self.logCtrl.setBackgroundColor(color)
    def setFocus(self):                 self.logCtrl.setFocus()
    set_focus = setFocus
    def setForegroundColor(self,color): self.logCtrl.setForegroundColor(color)
    def setInsertPoint(self,pos):       self.logCtrl.setInsertPoint(pos)
    def setSelectionRange(self,*args,**keys):
        self.logCtrl.setSelectionRange(*args,**keys)
    def setYScrollPosition (self,i):    self.logCtrl.setYScrollPosition(i)

    # Part 2: corresponding to mustBeDefinedInBaseClass.
    def clipboard_append(self,s):       self.logCtrl.clipboard_append(s)
    def clipboard_clear (self):         self.logCtrl.clipboard_clear()
    def onChar (self,event):            self.logCtrl.onChar(event)

    # Part 3: do-nothings in mayBeDefinedInSubclasses.
    def bind (self,kind,*args,**keys):          pass
    def getWidth (self):                        return 0
    def flashCharacter(self,i,bg='white',fg='red',flashes=3,delay=75):
        pass
    def indexIsVisible (self,i):                return False
        # Code will loop if this returns True forever.
    def mark_set(self,markName,i):              pass
    def setWidth (self,width):                  pass
    def tag_add(self,tagName,i,j=None,*args):   pass
    def tag_config (self,colorName,**keys):     pass
    def tag_configure (self,colorName,**keys):  pass
    def tag_delete (self,tagName,*args,**keys): pass
    def tag_names (self, *args):                return []
    def tag_ranges(self,tagName):               return tuple()
    def tag_remove(self,tagName,i,j=None,*args):pass
    def update (self,*args,**keys):             pass
    def update_idletasks (self,*args,**keys):   pass
    def xyToPythonIndex (self,x,y):             return 0
    def yview (self,*args):                     return 0,0

    # Part 4: corresponding to mayBeDefinedInSubclasses.
    def deleteTextSelection (self):         self.logCtrl.deleteTextSelection ()
    def event_generate(self,stroke):        pass
    def replace (self,i,j,s):               self.logCtrl.replace (i,j,s)
    def rowColToGuiIndex (self,s,row,col):  return self.logCtrl.rowColToGuiIndex(s,row,col)
    def selectAllText (self,insert=None):   self.logCtrl.selectAllText(insert)
    def toPythonIndex (self,index):         return self.logCtrl.toPythonIndex(index)
    toGuiIndex = toPythonIndex
    def toPythonIndexRowCol(self,index):    return self.logCtrl.toPythonIndexRowCol(index)
    #@+node:ekr.20081121105001.325: *4* put & putnl (qtLog)
    #@+node:ekr.20081121105001.326: *5* put (qtLog)
    # All output to the log stream eventually comes here.
    def put (self,s,color=None,tabName='Log'):

        c = self.c
        if g.app.quitting or not c or not c.exists:
            return

        if color:
            color = leoColor.getColor(color,'black')
        else:
            color = leoColor.getColor('black')

        self.selectTab(tabName or 'Log')
        # print('qtLog.put',tabName,'%3s' % (len(s)),self.logCtrl)

        # Note: this must be done after the call to selectTab.
        w = self.logCtrl.widget # w is a QTextBrowser

        if w:
            sb = w.horizontalScrollBar()
            pos = sb.sliderPosition()
            s=s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            if not self.wrap: # 2010/02/21: Use &nbsp; only when not wrapping!
                s = s.replace(' ','&nbsp;')
            s = s.rstrip().replace('\n','<br>')
            s = '<font color="%s">%s</font>' % (color,s)
            w.append(s)
            w.moveCursor(QtGui.QTextCursor.End)
            sb.setSliderPosition(pos)
        else:
            # put s to logWaiting and print s
            g.app.logWaiting.append((s,color),)
            if g.isUnicode(s):
                s = g.toEncodedString(s,"ascii")
            print(s)
    #@+node:ekr.20081121105001.327: *5* putnl
    def putnl (self,tabName='Log'):

        if g.app.quitting:
            return

        if tabName:
            self.selectTab(tabName)

        w = self.logCtrl.widget
        if w:
            sb = w.horizontalScrollBar()
            pos = sb.sliderPosition()
            # Not needed!
                # contents = w.toHtml()
                # w.setHtml(contents + '\n')
            w.moveCursor(QtGui.QTextCursor.End)
            sb.setSliderPosition(pos)
            w.repaint() # Slow, but essential.
        else:
            # put s to logWaiting and print  a newline
            g.app.logWaiting.append(('\n','black'),)
    #@+node:ekr.20081121105001.328: *4* Tab (qtLog)
    #@+node:ekr.20081121105001.329: *5* clearTab
    def clearTab (self,tabName,wrap='none'):

        w = self.logDict.get(tabName)
        if w:
            w.clear() # w is a QTextBrowser.
    #@+node:ekr.20081121105001.330: *5* createTab
    def createTab (self,tabName,widget=None,wrap='none'):
        """ Create a new tab in tab widget

        if widget is None, Create a QTextBrowser,
        suitable for log functionality.
        """

        trace = False and not g.unitTesting
        if trace: g.trace(tabName,g.callers(4))

        c = self.c ; w = self.tabWidget

        # Important. Not called during startup.

        if widget is None:
            # widget = QtGui.QTextBrowser()
            widget = QTextBrowserSubclass(parent=None,c=c,wrapper=self)
            contents = leoQTextEditWidget(widget=widget,name='log',c=c)
            widget.leo_log_wrapper = contents # Inject an ivar.
            if trace: g.trace('** creating',tabName,contents,widget,'\n',g.callers(9))
            # widget.setWordWrapMode(QtGui.QTextOption.NoWrap)
            widget.setWordWrapMode(
                g.choose(self.wrap,
                    QtGui.QTextOption.WordWrap,
                    QtGui.QTextOption.NoWrap))

            widget.setReadOnly(False) # Allow edits.
            self.logDict[tabName] = widget
            if tabName == 'Log':
                self.logCtrl = contents
                widget.setObjectName('log-widget')
                theFilter = leoQtEventFilter(c,w=self,tag='log')
                self.eventFilters.append(theFilter) # Needed!
                widget.installEventFilter(theFilter)
            self.contentsDict[tabName] = widget
            w.addTab(widget,tabName)
        else:
            contents = widget
            # Bug fix: 2009/10/06
            widget.leo_log_wrapper = contents # Inject an ivar.
            # if trace: g.trace('** using',tabName,contents)
            self.contentsDict[tabName] = contents
            w.addTab(contents,tabName)

        return contents
    #@+node:ekr.20081121105001.331: *5* cycleTabFocus (to do)
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
        if log: self.logCtrl = log.leo_log_wrapper

    #@+node:ekr.20081121105001.332: *5* deleteTab
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
    #@+node:ekr.20081121105001.333: *5* hideTab
    def hideTab (self,tabName):

        self.selectTab('Log')
    #@+node:ekr.20081121105001.334: *5* numberOfVisibleTabs
    def numberOfVisibleTabs (self):

        return len([val for val in self.frameDict.values() if val != None])
    #@+node:ekr.20081121105001.335: *5* selectTab & helper
    def selectTab (self,tabName,createText=True,widget=None,wrap='none'):

        '''Create the tab if necessary and make it active.'''

        c = self.c ; w = self.tabWidget ; trace = False

        ok = self.selectHelper(tabName,createText)
        if ok: return

        self.createTab(tabName,widget=widget,wrap=wrap)
        self.selectHelper(tabName,createText)

    #@+node:ekr.20081121105001.336: *6* selectHelper
    def selectHelper (self,tabName,createText):

        w = self.tabWidget

        for i in range(w.count()):
            if tabName == w.tabText(i):
                w.setCurrentIndex(i)
                if createText and tabName not in ('Spell','Find',):
                    self.logCtrl = w.widget(i).leo_log_wrapper
                    # g.trace('**setting',self.logCtrl)
                if tabName == 'Spell':
                    # the base class uses this as a flag to see if
                    # the spell system needs initing
                    self.frameDict['Spell'] = w.widget(i)
                return True
        else:
            return False
    #@+node:ekr.20081121105001.337: *4* qtLog color tab stuff
    def createColorPicker (self,tabName):

        g.es('color picker not ready for qt',color='blue')
    #@+node:ekr.20081121105001.341: *4* qtLog font tab stuff
    #@+node:ekr.20081121105001.342: *5* createFontPicker
    def createFontPicker (self,tabName):

        log = self
        QFont = QtGui.QFont
        font,ok = QtGui.QFontDialog.getFont()
        if not (font and ok): return

        style = font.style()
        table = (
            (QFont.StyleNormal,'normal'),
            (QFont.StyleItalic,'italic'),
            (QFont.StyleOblique,'oblique'))
        for val,name in table:
            if style == val:
                style = name ; break
        else: style = ''

        weight = font.weight()
        table = (
            (QFont.Light,'light'),
            (QFont.Normal,'normal'),
            (QFont.DemiBold,'demibold'),
            (QFont.Bold	,'bold'),
            (QFont.Black,'black'))
        for val,name in table:
            if weight == val:
                weight = name ; break
        else: weight = ''

        table = (
            ('family',str(font.family())),
            ('size  ',font.pointSize()),
            ('style ',style),
            ('weight',weight),
        )

        for key,val in table:
            if val:
                g.es(key,val,tabName='Fonts')
    #@+node:ekr.20081121105001.350: *5* createBindings (fontPicker)
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
    #@+node:ekr.20081121105001.351: *5* getFont
    def getFont(self,family=None,size=12,slant='roman',weight='normal'):

        return g.app.config.defaultFont
    #@+node:ekr.20081121105001.352: *5* setFont
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
    #@+node:ekr.20081121105001.353: *5* hideFontTab
    def hideFontTab (self,event=None):

        c = self.c
        c.frame.log.selectTab('Log')
        c.bodyWantsFocus()
    #@-others
#@+node:ekr.20081121105001.354: *3* class leoQtMenu (leoMenu)
class leoQtMenu (leoMenu.leoMenu):

    #@+others
    #@+node:ekr.20081121105001.355: *4* leoQtMenu.__init__
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
    #@+node:ekr.20081121105001.359: *4* Tkinter menu bindings
    # See the Tk docs for what these routines are to do
    #@+node:ekr.20081121105001.360: *5* Methods with Tk spellings
    #@+node:ekr.20081121105001.361: *6* add_cascade
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
    #@+node:ekr.20081121105001.362: *6* add_command (qt)
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
                # g.trace(command)
                return command()

            QtCore.QObject.connect(action,
                QtCore.SIGNAL("triggered()"),add_command_callback)
    #@+node:ekr.20081121105001.363: *6* add_separator
    def add_separator(self,menu):

        """Wrapper for the Tkinter add_separator menu method."""

        if menu:
            menu.addSeparator()
    #@+node:ekr.20081121105001.364: *6* delete
    def delete (self,menu,realItemName='<no name>'):

        """Wrapper for the Tkinter delete menu method."""

        # g.trace(menu)

        # if menu:
            # return menu.delete(realItemName)
    #@+node:ekr.20081121105001.365: *6* delete_range (leoQtMenu)
    def delete_range (self,menu,n1,n2):

        """Wrapper for the Tkinter delete menu method."""

        # Menu is a subclass of QMenu and leoQtMenu.

        # g.trace(menu,n1,n2,g.callers(4))

        for z in menu.actions()[n1:n2]:
            menu.removeAction(z)
    #@+node:ekr.20081121105001.366: *6* destroy
    def destroy (self,menu):

        """Wrapper for the Tkinter destroy menu method."""

        # if menu:
            # return menu.destroy()
    #@+node:ekr.20090603123442.3785: *6* index (leoQtMenu)
    def index (self,label):

        '''Return the index of the menu with the given label.'''
        # g.trace(label)

        return 0
    #@+node:ekr.20081121105001.367: *6* insert
    def insert (self,menuName,position,label,command,underline=None):

        # g.trace(menuName,position,label,command,underline)

        menu = self.getMenu(menuName)
        if menu and label:
            n = underline or 0
            if -1 > n > len(label):
                label = label[:n] + '&' + label[n:]
            action = menu.addAction(label)
            if command:
                def insert_callback(label=label,command=command):
                    command()
                QtCore.QObject.connect(
                    action,QtCore.SIGNAL("triggered()"),insert_callback)
    #@+node:ekr.20081121105001.368: *6* insert_cascade
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
    #@+node:ekr.20081121105001.369: *6* new_menu (qt)
    def new_menu(self,parent,tearoff=False,label=''): # label is for debugging.

        """Wrapper for the Tkinter new_menu menu method."""

        c = self.c ; leoFrame = self.frame

        # g.trace(parent,label)

        # Parent can be None, in which case it will be added to the menuBar.
        menu = qtMenuWrapper(c,leoFrame,parent)

        return menu
    #@+node:ekr.20081121105001.370: *5* Methods with other spellings (Qtmenu)
    #@+node:ekr.20081121105001.371: *6* clearAccel
    def clearAccel(self,menu,name):

        pass

        # if not menu:
            # return

        # realName = self.getRealMenuName(name)
        # realName = realName.replace("&","")

        # menu.entryconfig(realName,accelerator='')
    #@+node:ekr.20081121105001.372: *6* createMenuBar (Qtmenu)
    def createMenuBar(self,frame):

        '''Create all top-level menus.
        The menuBar itself has already been created.'''

        self.createMenusFromTables()
    #@+node:ekr.20081121105001.373: *6* createOpenWithMenu (QtMenu)
    def createOpenWithMenu(self,parent,label,index,amp_index):

        '''Create the File:Open With submenu.

        This is called from leoMenu.createOpenWithMenuFromTable.'''

        # Use the existing Open With menu if possible.
        menu = self.getMenu('openwith')

        if not menu:
            menu = self.new_menu(parent,tearoff=False,label=label)
            menu.insert_cascade(parent,index,
                label,menu,underline=amp_index)

        return menu
    #@+node:ekr.20081121105001.374: *6* disableMenu
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
    #@+node:ekr.20081121105001.375: *6* enableMenu
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
    #@+node:ekr.20081121105001.376: *6* getMenuLabel
    def getMenuLabel (self,menu,name):

        '''Return the index of the menu item whose name (or offset) is given.
        Return None if there is no such menu item.'''

        # At present, it is valid to always return None.

        # g.trace('menu',menu,'name',name)

        # actions = menu.actions()
        # for action in actions:
            # g.trace(action)
    #@+node:ekr.20081121105001.377: *6* setMenuLabel
    def setMenuLabel (self,menu,name,label,underline=-1):

        def munge(s):
            return g.u(s or '').replace('&','')

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
    #@+node:ekr.20081121105001.356: *4* Activate menu commands
    def activateMenu (self,menuName):

        '''Activate the menu with the given name'''

        c = self.c
        menu = self.getMenu(menuName)
        if menu:
            top = c.frame.top.ui
            pos = menu.pos() # Doesn't do any good.
            r = top.geometry()
            pt = QtCore.QPoint(r.x()+pos.x(),r.y())
            menu.exec_(pt)
    #@+node:ekr.20081121105001.378: *4* getMacHelpMenu
    def getMacHelpMenu (self,table):

        return None
    #@-others
#@+node:ekr.20100830205422.3714: *3* class LeoQTreeWidget
class LeoQTreeWidget(QtGui.QTreeWidget):

    # To do: Generate @auto or @thin nodes when appropriate.

    def __init__(self,c,parent):

        QtGui.QTreeWidget.__init__(self, parent)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.c = c
        self.trace = False

    def dragMoveEvent(self,ev):
        pass

    #@+others
    #@+node:ekr.20100830205422.3715: *4* dragEnter
    def dragEnterEvent(self,ev):

        '''Export c.p's tree as a Leo mime-data.'''

        trace = False and not g.unitTesting
        c = self.c ; tree = c.frame.tree
        if not ev:
            g.trace('no event!')
            return

        md = ev.mimeData()
        if not md:
            g.trace('No mimeData!') ; return

        c.endEditing()
        if g.app.dragging:
            if trace or self.trace: g.trace('** already dragging')
        else:
            g.app.dragging = True
            if self.trace: g.trace('set g.app.dragging')
            self.setText(md)
            if self.trace: self.dump(ev,c.p,'enter')

        # Always accept the drag, even if we are already dragging.
        ev.accept()
    #@+node:ekr.20100830205422.3716: *4* dropEvent & helpers
    def dropEvent(self,ev):

        trace = False and not g.unitTesting
        if not ev: return
        c = self.c ; tree = c.frame.tree ; u = c.undoer

        # Always clear the dragging flag, no matter what happens.
        g.app.dragging = False
        if self.trace: g.trace('clear g.app.dragging')

        # Set p to the target of the drop.
        item = self.itemAt(ev.pos())
        if not item: return
        itemHash = tree.itemHash(item)
        p = tree.item2positionDict.get(itemHash)
        if not p:
            if trace or self.trace: g.trace('no p!')
            return

        md = ev.mimeData()
        if not md:
            g.trace('no mimeData!') ; return

        ev.setDropAction(QtCore.Qt.IgnoreAction)
        ev.accept()

        if trace or self.trace: self.dump(ev,p,'drop ')

        if md.hasUrls():
            self.urlDrop(ev,p)
        else:
            self.outlineDrop(ev,p)
    #@+node:ekr.20100830205422.3720: *5* outlineDrop & helpers
    def outlineDrop (self,ev,p):

        trace = False and not g.unitTesting
        c = self.c ; tree = c.frame.tree
        mods = ev.keyboardModifiers()
        md = ev.mimeData()

        fn,s = self.parseText(md)
        if not s or not fn:
            if trace or self.trace: g.trace('no fn or no s')
            return

        if fn == self.fileName():
            if p and p == c.p:
                if trace or self.trace: g.trace('same node')
            else:
                cloneDrag = (int(mods) & QtCore.Qt.ControlModifier) != 0
                self.intraFileDrop(cloneDrag,fn,c.p,p)
        else:
            # Clone dragging between files is not allowed.
            self.interFileDrop(fn,p,s)
    #@+node:ekr.20100830205422.3718: *6* interFileDrop
    def interFileDrop (self,fn,p,s):

        '''Paste the mime data after (or as the first child of) p.'''

        c = self.c ; tree = c.frame.tree
        u = c.undoer ; undoType = 'Drag Outline'

        isLeo = g.match(s,0,g.app.prolog_prefix_string)
        if not isLeo: return

        c.selectPosition(p)
        pasted = c.fileCommands.getLeoOutlineFromClipboard(
            s,reassignIndices=True)
        if not pasted: return

        undoData = u.beforeInsertNode(p,
            pasteAsClone=False,copiedBunchList=[])
        c.validateOutline()
        c.selectPosition(pasted)
        pasted.setDirty()
        c.setChanged(True)
        back = pasted.back()
        if back and back.isExpanded():
            pasted.moveToNthChildOf(back,0)
        c.setRootPosition(c.findRootPosition(pasted))

        u.afterInsertNode(pasted,undoType,undoData)
        c.redraw_now(pasted)
        c.recolor()
    #@+node:ekr.20100830205422.3719: *6* intraFileDrop
    def intraFileDrop (self,cloneDrag,fn,p1,p2):

        '''Move p1 after (or as the first child of) p2.'''

        c = self.c ; u = c.undoer
        c.selectPosition(p1)

        if p2.hasChildren() and p2.isExpanded():
            # Attempt to move p1 to the first child of p2.
            parent = p2
            def move(p1,p2):
                if cloneDrag: p1 = p1.clone()
                p1.moveToNthChildOf(p2,0)
                return p1
        else:
            # Attempt to move p1 after p2.
            parent = p2.parent()
            def move(p1,p2):
                if cloneDrag: p1 = p1.clone()
                p1.moveAfter(p2)
                return p1

        ok = c.checkMoveWithParentWithWarning(p1,parent,True)
        if ok:
            undoData = u.beforeMoveNode(p1)
            dirtyVnodeList = p1.setAllAncestorAtFileNodesDirty()
            p1 = move(p1,p2)
            if cloneDrag:
                # Set dirty bits for ancestors of *all* cloned nodes.
                # Note: the setDescendentsDirty flag does not do what we want.
                for z in p1.self_and_subtree():
                    z.setAllAncestorAtFileNodesDirty(
                        setDescendentsDirty=False)
            c.setChanged(True)
            u.afterMoveNode(p1,'Drag',undoData,dirtyVnodeList)
            c.redraw_now(p1)
        else:
            g.trace('** move failed')
    #@+node:ekr.20100830205422.3721: *5* urlDrop & helpers
    def urlDrop (self,ev,p):

        c = self.c ; u = c.undoer ; undoType = 'Drag Urls'
        md = ev.mimeData()
        urls = md.urls()
        if not urls: return

        c.undoer.beforeChangeGroup(c.p,undoType)

        changed = False
        for z in urls:
            url = QtCore.QUrl(z)
            scheme = url.scheme()
            if scheme == 'file':
                changed |= self.doFileUrl(p,url)
            elif scheme in ('http',): # 'ftp','mailto',
                changed |= self.doHttpUrl(p,url)
            # else: g.trace(url.scheme(),url)

        if changed:
            c.setChanged(True)
            u.afterChangeGroup(c.p,undoType,reportFlag=False,dirtyVnodeList=[])
            c.redraw_now()
    #@+node:ekr.20100830205422.3722: *6* doFileUrl & helper
    def doFileUrl (self,p,url):

        fn = str(url.path())
        if sys.platform.lower().startswith('win'):
            if fn.startswith('/'):
                fn = fn[1:]

        changed = False
        if g.os_path_exists(fn):
            try:
                f = open(fn,'r')
            except IOError:
                f = None
            if f:
                s = f.read()
                f.close()
                self.doFileUrlHelper(fn,p,s)
                return True

        g.es_print('not found: %s' % (fn))
        return False
    #@+node:ekr.20100830205422.3723: *7* doFileUrlHelper & helper
    def doFileUrlHelper (self,fn,p,s):

        '''Insert s in an @thin, @auto or @edit node after p.'''

        c = self.c ; u = c.undoer ; undoType = 'Drag File'

        undoData = u.beforeInsertNode(p,pasteAsClone=False,copiedBunchList=[])

        if p.hasChildren() and p.isExpanded():
            p2 = p.insertAsNthChild(0)
        else:
            p2 = p.insertAfter()

        self.createAtFileNode(fn,p2,s)

        u.afterInsertNode(p2,undoType,undoData)

        c.selectPosition(p2)
    #@+node:ekr.20100902095952.3740: *8* createAtFileNode & helpers
    def createAtFileNode (self,fn,p,s):

        '''Set p's headline, body text and possibly descendants
        based on the file's name fn and contents s.

        If the file is an thin file, create an @thin tree.
        Othewise, create an @auto tree.
        If all else fails, create an @auto node.

        Give a warning if a node with the same headline already exists.
        '''

        c = self.c ; d = c.importCommands.importDispatchDict
        if self.isThinFile(fn,s):
            self.createAtThinTree(fn,p,s)
        elif self.isAutoFile(fn,s):
            self.createAtAutoTree(fn,p,s)
        else:
            self.createAtEditNode(fn,p,s)
        self.warnIfNodeExists(p)
    #@+node:ekr.20100902095952.3744: *9* createAtAutoTree
    def createAtAutoTree (self,fn,p,s):

        '''Make p an @auto node and create the tree using
        s, the file's contents.
        '''

        c = self.c ; at = c.atFileCommands

        p.h = '@auto %s' % (fn)

        at.readOneAtAutoNode(fn,p)

        # No error recovery should be needed here.

        p.clearDirty() # Don't automatically rewrite this node.
    #@+node:ekr.20100902165040.3738: *9* createAtEditNode
    def createAtEditNode(self,fn,p,s):

        c = self.c ; at = c.atFileCommands

        # Use the full @edit logic, so dragging will be
        # exactly the same as reading.
        at.readOneAtEditNode(fn,p)
        p.h = '@edit %s' % (fn)
        p.clearDirty() # Don't automatically rewrite this node.
    #@+node:ekr.20100902095952.3743: *9* createAtThinTree
    def createAtThinTree (self,fn,p,s):

        '''Make p an @thin node and create the tree using
        s, the file's contents.
        '''

        c = self.c ; at = c.atFileCommands

        p.h = '@thin %s' % (fn)

        # Read the file into p.
        ok = at.read(root=p.copy(),
            importFileName=None,
            fromString=s,
            atShadow=False,
            force=True) # Disable caching.

        if not ok:
            g.es_print('Error reading',fn,color='red')
            p.b = '' # Safe: will not cause a write later.
            p.clearDirty() # Don't automatically rewrite this node.
    #@+node:ekr.20100902095952.3741: *9* isThinFile
    def isThinFile (self,fn,s):

        '''Return true if the file whose contents is s
        was created from an @thin tree.'''

        c = self. c ; at = c.atFileCommands

        # Skip lines before the @+leo line.
        i = s.find('@+leo')
        if i == -1:
            return False
        else:
            # Like at.isFileLike.
            j,k = g.getLine(s,i)
            line = s[j:k]
            valid,new_df,start,end,isThin = at.parseLeoSentinel(line)
            # g.trace('valid',valid,'new_df',new_df,'isThin',isThin)
            return valid and new_df and isThin
    #@+node:ekr.20100902095952.3742: *9* isAutoFile
    def isAutoFile (self,fn,unused_s):

        '''Return true if the file whose name is fn
        can be parsed with an @auto parser.
        '''

        c = self.c
        d = c.importCommands.importDispatchDict
        junk,ext = g.os_path_splitext(fn)
        return d.get(ext)
    #@+node:ekr.20100902095952.3745: *9* warnIfNodeExists
    def warnIfNodeExists (self,p):

        c = self.c ; h = p.h
        for p2 in c.all_unique_positions():
            if p2.h == h and p2 != p:
                g.es('Warning: duplicate node:',h,color='blue')
                break
    #@+node:ekr.20100830205422.3724: *6* doHttpUrl
    def doHttpUrl (self,p,url):

        '''Insert the url in an @url node after p.'''

        c = self.c ; u = c.undoer ; undoType = 'Drag Url'

        s = str(url.toString()).strip()
        if not s: return False

        undoData = u.beforeInsertNode(p,pasteAsClone=False,copiedBunchList=[])

        if p.hasChildren() and p.isExpanded():
            p2 = p.insertAsNthChild(0)
        else:
            p2 = p.insertAfter()

        # p2.h,p2.b = '@url %s' % (s),''
        p2.h = '@url'
        p2.b = s
        p2.clearDirty() # Don't automatically rewrite this node.

        u.afterInsertNode(p2,undoType,undoData)
        return True
    #@+node:ekr.20100902190250.3743: *4* utils...
    #@+node:ekr.20100902190250.3741: *5* dump
    def dump (self,ev,p,tag):

        if ev:
            md = ev.mimeData()
            assert md,'dump: no md'
            fn,s = self.parseText(md)
            if fn:
                g.trace('',tag,'fn',repr(g.shortFileName(fn)),
                    'len(s)',len(s),p and p.h)
            else:
                g.trace('',tag,'no fn! s:',repr(s))
        else:
            g.trace('',tag,'** no event!')
    #@+node:ekr.20100902190250.3740: *5* parseText
    def parseText (self,md):

        '''Parse md.text() into (fn,s)'''

        fn = ''
        s = str(md.text()) # Safe: md.text() is a QString.

        if s:
            i = s.find(',')
            if i == -1:
                pass
            else:
                fn = s[:i]
                s = s[i+1:]

        return fn,s
    #@+node:ekr.20100902190250.3742: *5* setText & fileName
    def fileName (self):

        return self.c.fileName() or '<unsaved file>'

    def setText (self,md):

        c = self.c
        fn = self.fileName()
        s = c.fileCommands.putLeoOutline()
        md.setText('%s,%s' % (fn,s))
    #@-others
#@+node:ekr.20081121105001.379: *3* class leoQtSpellTab
class leoQtSpellTab:

    #@+others
    #@+node:ekr.20081121105001.380: *4* leoQtSpellTab.__init__
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
    #@+node:ekr.20081121105001.381: *4* createBindings TO DO
    def createBindings (self):
        pass
    #@+node:ekr.20081121105001.382: *4* createFrame (to be done in Qt designer)
    def createFrame (self):
        pass

    #@+node:ekr.20081121105001.386: *4* Event handlers
    #@+node:ekr.20081121105001.387: *5* onAddButton
    def onAddButton(self):
        """Handle a click in the Add button in the Check Spelling dialog."""

        self.handler.add()
    #@+node:ekr.20081121105001.388: *5* onChangeButton & onChangeThenFindButton
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
    #@+node:ekr.20081121105001.389: *5* onFindButton
    def onFindButton(self):

        """Handle a click in the Find button in the Spell tab."""

        c = self.c
        self.handler.find()
        self.updateButtons()
        c.invalidateFocus()
        c.bodyWantsFocusNow()
    #@+node:ekr.20081121105001.390: *5* onHideButton
    def onHideButton(self):

        """Handle a click in the Hide button in the Spell tab."""

        self.handler.hide()
    #@+node:ekr.20081121105001.391: *5* onIgnoreButton
    def onIgnoreButton(self,event=None):

        """Handle a click in the Ignore button in the Check Spelling dialog."""

        self.handler.ignore()
    #@+node:ekr.20081121105001.392: *5* onMap
    def onMap (self, event=None):
        """Respond to a Tk <Map> event."""

        self.update(show= False, fill= False)
    #@+node:ekr.20081121105001.393: *5* onSelectListBox
    def onSelectListBox(self, event=None):
        """Respond to a click in the selection listBox."""

        c = self.c
        self.updateButtons()
        c.bodyWantsFocus()
    #@+node:ekr.20081121105001.394: *4* Helpers
    #@+node:ekr.20081121105001.395: *5* bringToFront
    def bringToFront (self):

        self.c.frame.log.selectTab('Spell')
    #@+node:ekr.20081121105001.396: *5* fillbox
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
    #@+node:ekr.20081121105001.397: *5* getSuggestion
    def getSuggestion(self):
        """Return the selected suggestion from the listBox."""

        idx = self.listBox.currentRow()
        value = self.suggestions[idx]
        return value
    #@+node:ekr.20081121105001.398: *5* update
    def update(self,show=True,fill=False):

        """Update the Spell Check dialog."""

        c = self.c

        if fill:
            self.fillbox([])

        self.updateButtons()

        if show:
            self.bringToFront()
            c.bodyWantsFocus()
    #@+node:ekr.20081121105001.399: *5* updateButtons (spellTab)
    def updateButtons (self):

        """Enable or disable buttons in the Check Spelling dialog."""

        c = self.c

        ui = c.frame.top.ui

        w = c.frame.body.bodyCtrl
        state = self.suggestions and w.hasSelection()

        ui.leo_spell_btn_Change.setDisabled(not state)
        ui.leo_spell_btn_FindChange.setDisabled(not state)

        return state
    #@-others
#@+node:ekr.20081121105001.400: *3* class leoQtTree (baseNativeTree)
class leoQtTree (baseNativeTree.baseNativeTreeWidget):

    """Leo qt tree class, a subclass of baseNativeTreeWidget."""

    callbacksInjected = False # A class var.

    #@+others
    #@+node:ekr.20090124174652.118: *4*  Birth (leoQtTree)
    #@+node:ekr.20090124174652.119: *5* ctor
    def __init__(self,c,frame):

        # Init the base class.
        baseNativeTree.baseNativeTreeWidget.__init__(self,c,frame)

        # Components.
        self.headlineWrapper = leoQtHeadlineWidget # This is a class.
        self.treeWidget = w = frame.top.ui.treeWidget # An internal ivar.

        # g.trace('leoQtTree',w)

        if 0: # Drag and drop
            w.setDragEnabled(True)
            w.viewport().setAcceptDrops(True)
            w.showDropIndicator = True
            w.setAcceptDrops(True)
            w.setDragDropMode(w.InternalMove)

            if 1: # Does not work
                def dropMimeData(self,data,action,row,col,parent):
                    g.trace()
                # w.dropMimeData = dropMimeData

                def mimeData(self,indexes):
                   g.trace()

        # Early inits...
        try: w.headerItem().setHidden(True)
        except Exception: pass

        w.setIconSize(QtCore.QSize(160,16))
    #@+node:ekr.20090124174652.120: *5* qtTree.initAfterLoad
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
                "itemClicked(QTreeWidgetItem*, int)"),
            self.onItemClicked)

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

        w.connect(self.treeWidget, QtCore.SIGNAL(
                "customContextMenuRequested(QPoint)"),
            self.onContextMenu)    

        self.ev_filter = leoQtEventFilter(c,w=self,tag='tree')
        tw.installEventFilter(self.ev_filter)

        # 2010/01/24: Do not set this here.
        # The read logic sets c.changed to indicate nodes have changed.
        # c.setChanged(False)
    #@+node:ekr.20090124174652.102: *4* Widget-dependent helpers (leoQtTree)
    #@+node:ekr.20090126120517.11: *5* Drawing
    def clear (self):
        '''Clear all widgets in the tree.'''
        w = self.treeWidget
        w.clear()

    def repaint (self):
        '''Repaint the widget.'''
        w = self.treeWidget
        w.repaint()
        w.resizeColumnToContents(0) # 2009/12/22
    #@+node:ekr.20090124174652.109: *5* Icons (qtTree)
    #@+node:ekr.20090124174652.110: *6* drawIcon
    def drawIcon (self,p):

        '''Redraw the icon at p.'''

        w = self.treeWidget
        itemOrTree = self.position2item(p) or w
        item = QtGui.QTreeWidgetItem(itemOrTree)
        icon = self.getIcon(p)
        self.setItemIcon(item,icon)

    #@+node:ekr.20090124174652.111: *6* getIcon & helper (qtTree)
    def getIcon(self,p):

        '''Return the proper icon for position p.'''

        p.v.iconVal = val = p.v.computeIcon()
        return self.getCompositeIconImage(p,val)
    #@+node:ekr.20090701122113.3736: *7* getCompositeIconImage
    def getCompositeIconImage(self,p,val):

        trace = False and not g.unitTesting
        userIcons = self.c.editCommands.getIconList(p)
        if not userIcons:
            return self.getStatusIconImage(p)

        hash = [i['file'] for i in userIcons if i['where'] == 'beforeIcon']
        hash.append(str(val))
        hash.extend([i['file'] for i in userIcons if i['where'] == 'beforeHeadline'])
        hash = ':'.join(hash)

        if hash in g.app.gui.iconimages:
            icon = g.app.gui.iconimages[hash]
            if trace: g.trace('cached %s' % (icon))
            return icon

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

        icon = QtGui.QIcon(pix)
        g.app.gui.iconimages[hash] = icon
        if trace: g.trace('new %s' % (icon))
        return icon
    #@+node:ekr.20090124174652.112: *6* setItemIconHelper (qtTree)
    def setItemIconHelper (self,item,icon):

        # Generates an item-changed event.
        # g.trace(id(icon))
        if item:
            item.setIcon(0,icon)
    #@+node:ekr.20090124174652.115: *5* Items
    #@+node:ekr.20090124174652.67: *6* childIndexOfItem
    def childIndexOfItem (self,item):

        parent = item and item.parent()

        if parent:
            n = parent.indexOfChild(item)
        else:
            w = self.treeWidget
            n = w.indexOfTopLevelItem(item)

        return n

    #@+node:ekr.20090124174652.66: *6* childItems
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
    #@+node:ekr.20090303095630.15: *6* closeEditorHelper (leoQtTree)
    def closeEditorHelper (self,e,item):

        w = self.treeWidget

        if e:
            # g.trace(g.callers(5))
            w.closeEditor(e,QtGui.QAbstractItemDelegate.NoHint)
            w.setCurrentItem(item)
    #@+node:ekr.20090322190318.10: *6* connectEditorWidget & helper
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
    #@+node:ekr.20090124174652.18: *6* contractItem & expandItem
    def contractItem (self,item):

        # g.trace(g.callers(4))

        self.treeWidget.collapseItem(item)

    def expandItem (self,item):

        # g.trace(g.callers(4))

        self.treeWidget.expandItem(item)
    #@+node:ekr.20090124174652.104: *6* createTreeEditorForItem (leoQtTree)
    def createTreeEditorForItem(self,item):

        trace = False and not g.unitTesting

        w = self.treeWidget
        w.setCurrentItem(item) # Must do this first.
        w.editItem(item)
        e = w.itemWidget(item,0)
        e.setObjectName('headline')
        self.connectEditorWidget(e,item)

        return e
    #@+node:ekr.20090124174652.103: *6* createTreeItem
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
    #@+node:ekr.20090129062500.13: *6* editLabelHelper (leoQtTree)
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
            if s == 'newHeadline': selectAll=True
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
    #@+node:ekr.20090124174652.105: *6* getCurrentItem
    def getCurrentItem (self):

        w = self.treeWidget
        return w.currentItem()
    #@+node:ekr.20090126120517.22: *6* getItemText
    def getItemText (self,item):

        '''Return the text of the item.'''

        if item:
            return g.u(item.text(0))
        else:
            return '<no item>'
    #@+node:ekr.20090126120517.19: *6* getParentItem
    def getParentItem(self,item):

        return item and item.parent()
    #@+node:ville.20090525205736.3927: *6* getSelectedItems
    def getSelectedItems(self):
        w = self.treeWidget    
        return w.selectedItems()
    #@+node:ekr.20090124174652.106: *6* getTreeEditorForItem (leoQtTree)
    def getTreeEditorForItem(self,item):

        '''Return the edit widget if it exists.
        Do *not* create one if it does not exist.'''

        w = self.treeWidget
        e = w.itemWidget(item,0)
        return e
    #@+node:ekr.20090602083443.3817: *6* getWrapper (leoQtTree)
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
    #@+node:ekr.20090124174652.69: *6* nthChildItem
    def nthChildItem (self,n,parent_item):

        children = self.childItems(parent_item)

        if n < len(children):
            item = children[n]
        else:
            # This is **not* an error.
            # It simply means that we need to redraw the tree.
            item = None

        return item
    #@+node:ekr.20090201080444.12: *6* scrollToItem
    def scrollToItem (self,item):

        w = self.treeWidget

        # g.trace(self.traceItem(item),g.callers(4))

        hPos,vPos = self.getScroll()

        w.scrollToItem(item,w.PositionAtCenter)

        self.setHScroll(0)
    #@+node:ekr.20090124174652.107: *6* setCurrentItemHelper (leoQtTree)
    def setCurrentItemHelper(self,item):

        w = self.treeWidget
        w.setCurrentItem(item)
    #@+node:ekr.20090124174652.108: *6* setItemText
    def setItemText (self,item,s):

        if item:
            item.setText(0,s)
    #@+node:ekr.20090124174652.122: *5* Scroll bars (leoQtTree)
    #@+node:ekr.20090531084925.3779: *6* getSCroll
    def getScroll (self):

        '''Return the hPos,vPos for the tree's scrollbars.'''

        w = self.treeWidget
        hScroll = w.horizontalScrollBar()
        vScroll = w.verticalScrollBar()
        hPos = hScroll.sliderPosition()
        vPos = vScroll.sliderPosition()
        return hPos,vPos
    #@+node:ekr.20090531084925.3780: *6* setH/VScroll
    def setHScroll (self,hPos):
        w = self.treeWidget
        hScroll = w.horizontalScrollBar()
        hScroll.setValue(hPos)

    def setVScroll (self,vPos):
        # g.trace(vPos)
        w = self.treeWidget
        vScroll = w.verticalScrollBar()
        vScroll.setValue(vPos)
    #@+node:ekr.20090531084925.3774: *6* scrollDelegate (leoQtTree)
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
    #@+node:ville.20090630151546.3969: *5* onContextMenu (leoQtTree)
    def onContextMenu(self, point):
        c = self.c
        w = self.treeWidget
        handlers = g.tree_popup_handlers    
        menu = QtGui.QMenu()
        menuPos = w.mapToGlobal(point)
        if not handlers:
            menu.addAction("No popup handlers")

        p = c.currentPosition().copy()
        done = set()
        for h in handlers:
            # every handler has to add it's QActions by itself
            if h in done:
                # do not run the same handler twice
                continue
            h(c,p,menu)

        a = menu.popup(menuPos)
        self._contextmenu = menu
    #@-others
#@+node:ekr.20100111202913.3765: *3* class leoQtTreeTab
class leoQtTreeTab:

    '''A class representing a so-called tree-tab.

    Actually, it represents a combo box'''

    #@+others
    #@+node:ekr.20100111202913.3766: *4*  Birth & death
    #@+node:ekr.20100111202913.3767: *5*  ctor (leoTreeTab)
    def __init__ (self,c,iconBar):

        # g.trace('(leoTreeTab)',g.callers(4))

        self.c = c
        self.cc = c.chapterController
        assert self.cc
        self.iconBar = iconBar
        self.tabNames = []
            # The list of tab names. Changes when tabs are renamed.
        self.w = None # The QComboBox

        self.createControl()
    #@+node:ekr.20100111202913.3768: *5* tt.createControl
    def createControl (self):

        tt = self
        frame = QtGui.QLabel('Chapters: ')
        tt.iconBar.addWidget(frame)
        tt.w = w = QtGui.QComboBox()
        tt.setNames()
        tt.iconBar.addWidget(w)

        def onIndexChanged(s,tt=tt):
            if not s: return
            s = g.u(s)
            # g.trace(s)
            tt.selectTab(s)

        w.connect(w,
            QtCore.SIGNAL("currentIndexChanged(QString)"),
                onIndexChanged)
    #@+node:ekr.20100111202913.3769: *4* Tabs...
    #@+node:ekr.20100111202913.3770: *5* tt.createTab
    def createTab (self,tabName,select=True):

        # g.trace(tabName,g.callers(4))

        tt = self

        # Avoid a glitch during initing.
        if tabName == 'main': return

        if tabName not in tt.tabNames:
            tt.tabNames.append(tabName)
            tt.setNames()
    #@+node:ekr.20100111202913.3771: *5* tt.destroyTab
    def destroyTab (self,tabName):

        tt = self

        if tabName in tt.tabNames:
            tt.tabNames.remove(tabName)
            tt.setNames()
    #@+node:ekr.20100111202913.3772: *5* tt.selectTab
    def selectTab (self,tabName):

        tt = self

        # g.trace(tabName)

        if tabName not in self.tabNames:
            tt.createTab(tabName)

        tt.cc.selectChapterByName(tabName)

        self.c.redraw()
        self.c.outerUpdate()
    #@+node:ekr.20100111202913.3773: *5* tt.setTabLabel
    def setTabLabel (self,tabName):

        tt = self ; w = tt.w
        # g.trace(tabName)
        i = w.findText (tabName)
        if i > -1:
            w.setCurrentIndex(i)
    #@+node:ekr.20100111202913.3774: *5* tt.setNames
    def setNames (self):

        '''Recreate the list of items.'''

        tt = self ; w = tt.w
        names = tt.tabNames[:]
        if 'main' in names: names.remove('main')
        names.sort()
        names.insert(0,'main')
        w.clear()
        w.insertItems(0,names)
    #@-others
#@+node:ville.20090804182114.8400: *3* class LeoTabbedTopLevel (QtGui.QTabWidget)
class LeoTabbedTopLevel(QtGui.QTabWidget):
    """ Toplevel frame for tabbed ui """

    #@+others
    #@+node:ekr.20100101104934.3662: *4* setChanged
    def setChanged (self,c,changed):

        i = self.currentIndex()
        if i < 0: return

        s = self.tabText(i)
        s = g.u(s)
        # g.trace('LeoTabbedTopLevel',changed,repr(s),g.callers(5))

        if len(s) > 2:
            if changed:
                if not s.startswith('* '):
                    title = "* " + s
                    self.setTabText(i,title)
            else:
                if s.startswith('* '):
                    title = s[2:]
                    self.setTabText(i,title)
    #@+node:ekr.20100119113742.3714: *4* setTabName (LeoTabbedTopLevel)
    def setTabName (self,c,fileName):

        '''Set the tab name for c's tab to fileName.'''

        tabw = self # self is a LeoTabbedTopLevel
        dw = c.frame.top # A DynamicWindow

        # Find the tab in tabw corresponding to dw.
        i = tabw.indexOf(dw)
        if i > -1:
            tabw.setTabText(i,g.shortFileName(fileName))
    #@+node:ville.20090804182114.8401: *4* closeEvent (leoTabbedTopLevel)
    def closeEvent(self, event):

        noclose = False
        for c in g.app.commanders():
            res = c.exists and g.app.closeLeoWindow(c.frame)
            if not res:
                noclose = True

        if noclose:
            event.ignore()
        else:            
            event.accept()
    #@-others




#@+node:ekr.20081121105001.469: *3* class qtMenuWrapper (QMenu,leoQtMenu)
class qtMenuWrapper (QtGui.QMenu,leoQtMenu):

    def __init__ (self,c,frame,parent):

        assert c
        assert frame
        QtGui.QMenu.__init__(self,parent)
        leoQtMenu.__init__(self,frame)

    def __repr__(self):

        return '<qtMenuWrapper %s>' % self.leo_label or 'unlabeled'
#@+node:ekr.20081121105001.470: *3* class qtSearchWidget
class qtSearchWidget:

    """A dummy widget class to pass to Leo's core find code."""

    def __init__ (self):

        self.insertPoint = 0
        self.selection = 0,0
        self.bodyCtrl = self
        self.body = self
        self.text = None
#@+node:ville.20090803130409.3679: *3* class SDIFrameFactory
class SDIFrameFactory:
    """ 'Toplevel' frame builder 

    This only deals with Qt level widgets, not Leo wrappers
    """

    #@+others
    #@+node:ville.20090803130409.3680: *4* frame creation & null deletion
    def createFrame(self, leoFrame):

        c = leoFrame.c
        dw = DynamicWindow(c)    
        dw.construct()
        g.app.gui.attachLeoIcon(dw)
        dw.setWindowTitle(leoFrame.title)
        dw.show()
        return dw

    def deleteFrame(self, wdg):
        pass

    #@-others
#@+node:ville.20090803130409.3685: *3* class TabbedFrameFactory
class TabbedFrameFactory:
    """ 'Toplevel' frame builder for tabbed toplevel interface

    This causes Leo to maintain only one toplevel window,
    with multiple tabs for documents
    """

    #@+others
    #@+node:ville.20090803132402.3685: *4* ctor
    def __init__(self):

        # will be created when first frame appears 

        # DynamicWindow => Leo frame map
        self.alwaysShowTabs = True
            # Set to true to workaround a problem
            # setting the window title when tabs are shown.
        self.leoFrames = {} 
        self.masterFrame = None
        self.createTabCommands()
    #@+node:ekr.20100101104934.3658: *4* createFrame
    def createFrame(self, leoFrame):

        c = leoFrame.c
        if self.masterFrame is None:
            self.createMaster()
        tabw = self.masterFrame
        dw = DynamicWindow(c,tabw)
        self.leoFrames[dw] = leoFrame

        # Shorten the title.
        fname = c.mFileName
        if fname:
            title = os.path.basename(fname)
        else:
            title = leoFrame.title
        tip = leoFrame.title

        # g.trace('TabbedFrameFactory: title',title,'tip',tip)

        dw.setWindowTitle(tip) # 2010/1/1
        idx = tabw.addTab(dw, title)
        if tip: tabw.setTabToolTip(idx, tip)

        dw.construct(master=tabw)
        tabw.setCurrentIndex(idx)            

        # Work around the problem with missing dirty indicator
        # by always showing the tab.
        tabw.tabBar().setVisible(
            self.alwaysShowTabs or tabw.count() > 1)

        dw.show()
        tabw.show()
        return dw
    #@+node:ekr.20100101104934.3659: *4* deleteFrame
    def deleteFrame(self, wdg):
        if wdg not in self.leoFrames:
            # probably detached tab
            return
        tabw = self.masterFrame
        idx = tabw.indexOf(wdg)
        tabw.removeTab(idx)
        del self.leoFrames[wdg]
        tabw.tabBar().setVisible(
            self.alwaysShowTabs or tabw.count() > 1)
    #@+node:ville.20090803132402.3684: *4* createMaster
    def createMaster(self):
        mf = self.masterFrame = LeoTabbedTopLevel()
        mf.resize(1000, 700)
        g.app.gui.attachLeoIcon(mf)
        tabbar = mf.tabBar()

        try:
            tabbar.setTabsClosable(True)
            tabbar.connect(tabbar,
                QtCore.SIGNAL('tabCloseRequested(int)'),
                self.slotCloseRequest)
        except AttributeError:
            pass # Qt 4.4 does not support setTabsClosable

        mf.connect(mf,
            QtCore.SIGNAL('currentChanged(int)'),
            self.slotCurrentChanged)
        mf.show()
    #@+node:ekr.20100101104934.3660: *4* signal handlers
    def slotCloseRequest(self,idx):
        tabw = self.masterFrame
        w = tabw.widget(idx)
        f = self.leoFrames[w]
        c = f.c
        c.close()

    def slotCurrentChanged(self, idx):
        tabw = self.masterFrame
        w = tabw.widget(idx)
        f = self.leoFrames.get(w)
        if f:
            # g.trace(f and f.title or '<no frame>')
            tabw.setWindowTitle(f.title)
    #@+node:ville.20090803201708.3694: *4* utilities
    def focusCurrentBody(self):
        """ Focus body control of current tab """
        tabw = self.masterFrame
        w = tabw.currentWidget()
        w.setFocus()

        f = self.leoFrames[w]
        c = f.c
        c.bodyWantsFocusNow()
    #@+node:ville.20090803164510.3688: *4* createTabCommands
    def detachTab(self, wdg):
        """ Detach specified tab as individual toplevel window """

        del self.leoFrames[wdg]
        wdg.setParent(None)
        wdg.show()

    def createTabCommands(self):
        #@+<< Commands for tabs >>
        #@+node:ville.20090803184912.3685: *5* << Commands for tabs >>
        @g.command('tab-detach')
        def tab_detach(event):
            """ Detach current tab from tab bar """
            if len(self.leoFrames) < 2:
                g.es_print_error("Can't detach last tab")
                return

            c = event['c']
            f = c.frame
            self.detachTab(f.top)
            f.top.setWindowTitle(f.title + ' [D]')

        # this is actually not tab-specific, move elsewhere?
        @g.command('close-others')
        def close_others(event):
            myc = event['c']
            for c in g.app.commanders():
                if c is not myc:
                    c.close()

        def tab_cycle(offset):
            tabw = self.masterFrame
            cur = tabw.currentIndex()
            count = tabw.count()
            cur += offset
            if cur < 0:
                cur = count -1
            if cur == count:
                cur = 0
            tabw.setCurrentIndex(cur)
            self.focusCurrentBody()

        @g.command('tab-cycle-next')
        def tab_cycle_next(event):
            """ Cycle to next tab """
            tab_cycle(1)

        @g.command('tab-cycle-previous')
        def tab_cycle_previous(event):
            """ Cycle to next tab """
            tab_cycle(-1)
        #@-<< Commands for tabs >>




    #@-others
#@+node:ekr.20081121105001.471: ** Gui wrapper
#@+node:ekr.20081121105001.472: *3* class leoQtGui
class leoQtGui(leoGui.leoGui):

    '''A class implementing Leo's Qt gui.'''

    #@+others
    #@+node:ekr.20081121105001.473: *4*   Birth & death (qtGui)
    #@+node:ekr.20081121105001.474: *5*  qtGui.__init__
    def __init__ (self):

        # Initialize the base class.
        leoGui.leoGui.__init__(self,'qt')

        self.qtApp = app = QtGui.QApplication(sys.argv)
        self.bodyTextWidget  = leoQtBaseTextWidget
        self.plainTextWidget = leoQtBaseTextWidget
        self.iconimages = {} # Image cache set by getIconImage().
        self.mGuiName = 'qt'  

        if g.app.qt_use_tabs:    
            self.frameFactory = TabbedFrameFactory()
        else:
            self.frameFactory = SDIFrameFactory()
    #@+node:ekr.20081121105001.475: *5* createKeyHandlerClass (qtGui)
    def createKeyHandlerClass (self,c,useGlobalKillbuffer=True,useGlobalRegisters=True):

        # Use the base class
        return leoKeys.keyHandlerClass(c,useGlobalKillbuffer,useGlobalRegisters)
    #@+node:ekr.20090123150451.11: *5* onActivateEvent (qtGui)
    # Called from eventFilter

    def onActivateEvent (self,event,c,obj,tag):

        '''Put the focus in the body pane when the Leo window is
        activated, say as the result of an Alt-tab or click.'''

        # This is called several times for each window activation.
        # We only need to set the focus once.

        trace = False and not g.unitTesting

        if c.exists and tag == 'body':
            if trace: g.trace(tag,c)
            c.bodyWantsFocusNow()
            c.outerUpdate() # Required because this is an event handler.
            g.doHook('activate',c=c,p=c.p,v=c.p,event=event)
    #@+node:ekr.20090320101733.16: *5* onDeactiveEvent (qtGui)
    def onDeactivateEvent (self,event,c,obj,tag):

        '''Put the focus in the body pane when the Leo window is
        activated, say as the result of an Alt-tab or click.'''

        trace = False and not g.unitTesting

        # This is called several times for each window activation.
        # Save the headline only once.

        if c.exists and tag.startswith('tree'):
            if trace: g.trace(tag,c)
            c.endEditing()
            g.doHook('deactivate',c=c,p=c.p,v=c.p,event=event)
    #@+node:ville.20090314101331.2: *5* IPython embedding & mainloop
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
    #@+node:ekr.20081121105001.476: *5* runMainLoop (qtGui)
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
    #@+node:ekr.20081121105001.477: *5* destroySelf
    def destroySelf (self):
        QtCore.pyqtRemoveInputHook()
        self.qtApp.exit()
    #@+node:ekr.20081121105001.183: *4* Clipboard (qtGui)
    def replaceClipboardWith (self,s):

        '''Replace the clipboard with the string s.'''

        trace = False and not g.unitTesting
        cb = self.qtApp.clipboard()
        if cb:
            # cb.clear()  # unnecessary, breaks on some Qt versions
            s = g.toUnicode(s)
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
                # Same as g.u(s), but with error handling.
            return s
        else:
            g.trace('no clipboard!')
            return ''
    #@+node:ekr.20081121105001.478: *4* Do nothings
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


    #@+node:ekr.20081121105001.479: *4* Dialogs & panels (qtGui)
    #@+node:ekr.20081122170423.1: *5* alert (qtGui)
    def alert (self,message):

        if g.unitTesting: return

        b = QtGui.QMessageBox
        d = b(None)
        d.setWindowTitle('Alert')
        d.setText(message)
        d.setIcon(b.Warning)
        yes = d.addButton('Ok',b.YesRole)
        d.exec_()
    #@+node:ekr.20081121105001.480: *5* makeFilter
    def makeFilter (self,filetypes):

        '''Return the Qt-style dialog filter from filetypes list.'''

        filters = ['%s (%s)' % (z) for z in filetypes]

        return ';;'.join(filters)
    #@+node:tbrown.20100421115534.17325: *5* runAskOkCancelStringDialog
    def runAskOkCancelStringDialog(self,c,title,message):

        """Create and run askOkCancelString dialog ."""

        if g.unitTesting: return None

        txt,ok = QtGui.QInputDialog.getText(None, title, message)
        if not ok:
            return None

        return txt
    #@+node:tbrown.20100421115534.17324: *5* runAskOkCancelNumberDialog
    def runAskOkCancelNumberDialog(self,c,title,message):

        """Create and run askOkCancelNumber dialog ."""

        if g.unitTesting: return None

        n,ok = QtGui.QInputDialog.getDouble(None, title, message)
        if not ok:
            return None

        return n
    #@+node:ekr.20081121105001.482: *5* qtGui panels
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

    #@+node:ekr.20081121105001.483: *5* runAboutLeoDialog
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
    #@+node:ekr.20081121105001.484: *5* runAskLeoIDDialog
    def runAskLeoIDDialog(self):

        """Create and run a dialog to get g.app.LeoID."""

        if g.unitTesting: return None

        message = (
            "leoID.txt not found\n\n" +
            "Please enter an id that identifies you uniquely.\n" +
            "Your cvs/bzr login name is a good choice.\n\n" +
            "Leo uses this id to uniquely identify nodes.\n\n" +
            "Your id must contain only letters and numbers\n" +
            "and must be at least 3 characters in length.")
        parent = None
        title = 'Enter Leo id'
        s,ok = QtGui.QInputDialog.getText(parent,title,message)
        return g.u(s)
    #@+node:ekr.20081121105001.485: *5* runAskOkDialog
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

    #@+node:tbrown.20100912184720.12469: *5* runAskDateTimeDialog
    def runAskDateTimeDialog(self, c, title, 
        message='Select Date/Time', init=None, step_min={}):
        """Create and run a qt date/time selection dialog.

        init - a datetime, default now
        step_min - a dict, keys are QtGui.QDateTimeEdit Sections, like
          QtGui.QDateTimeEdit.MinuteSection, and values are integers,
          the minimum amount that section of the date/time changes
          when you roll the mouse wheel.

        E.g. (5 minute increments in minute field):

            print g.app.gui.runAskDateTimeDialog(c, 'When?',
              message="When is it?",
              step_min={QtGui.QDateTimeEdit.MinuteSection: 5})

        """

        class DateTimeEditStepped(QtGui.QDateTimeEdit):
            """QDateTimeEdit which allows you to set minimum steps on fields, e.g.
              DateTimeEditStepped(parent, {QtGui.QDateTimeEdit.MinuteSection: 5})
            for a minimum 5 minute increment on the minute field.
            """
            def __init__(self, parent=None, init=None, step_min={}):

                self.step_min = step_min
                if init:
                    QtGui.QDateTimeEdit.__init__(self, init, parent)
                else:
                    QtGui.QDateTimeEdit.__init__(self, parent)

            def stepBy(self, step):
                cs = self.currentSection()
                if cs in self.step_min and abs(step) < self.step_min[cs]:
                    step = self.step_min[cs] if step > 0 else -self.step_min[cs]
                QtGui.QDateTimeEdit.stepBy(self, step)

        class Calendar(QtGui.QDialog):
            def __init__(self, parent=None, message='Select Date/Time',
                init=None, step_min={}):
                QtGui.QDialog.__init__(self, parent)

                layout = QtGui.QVBoxLayout()
                self.setLayout(layout)

                layout.addWidget(QtGui.QLabel(message))

                self.dt = DateTimeEditStepped(init=init, step_min=step_min)
                self.dt.setCalendarPopup(True)
                layout.addWidget(self.dt)

                buttonBox = QtGui.QDialogButtonBox(
                QtGui.QDialogButtonBox.Ok
                    | QtGui.QDialogButtonBox.Cancel);
                layout.addWidget(buttonBox)

                self.connect(buttonBox, QtCore.SIGNAL("accepted()"),
                    self, QtCore.SLOT("accept()"));
                self.connect(buttonBox, QtCore.SIGNAL("rejected()"),
                    self, QtCore.SLOT("reject()"));

        if g.unitTesting: return None

        b = Calendar
        if not init:
            init = datetime.datetime.now()
        d = b(c.frame.top, message=message, init=init, step_min=step_min)

        d.setWindowTitle(title)

        if d.exec_() != d.Accepted:
            return None
        else:
            return d.dt.dateTime().toPyDateTime()
    #@+node:ekr.20081121105001.486: *5* runAskYesNoCancelDialog
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
    #@+node:ekr.20081121105001.487: *5* runAskYesNoDialog
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

    #@+node:ekr.20081121105001.488: *5* runOpenFileDialog
    def runOpenFileDialog(self,title,filetypes,defaultextension,multiple=False):

        """Create and run an Qt open file dialog ."""

        parent = None
        filter = self.makeFilter(filetypes)

        if multiple:
            lst = QtGui.QFileDialog.getOpenFileNames(parent,title,os.curdir,filter)
            return [g.u(s) for s in lst]
        else:
            s = QtGui.QFileDialog.getOpenFileName(parent,title,os.curdir,filter)
            return g.u(s)
    #@+node:ekr.20090722094828.3653: *5* runPropertiesDialog (qtGui)
    def runPropertiesDialog(self,
        title='Properties',data={}, callback=None, buttons=None):

        """Dispay a modal TkPropertiesDialog"""

        # g.trace(data)
        g.es_print('Properties menu not supported for Qt gui',color='blue')
        result = 'Cancel'
        return result,data

        # d = propertiesDialog(title,data)
        # result = d.run()
        # return result
    #@+node:ekr.20081121105001.489: *5* runSaveFileDialog
    def runSaveFileDialog(self,initialfile='',title='Save',filetypes=[],defaultextension=''):

        """Create and run an Qt save file dialog ."""

        parent = None
        filter_ = self.makeFilter(filetypes)
        s = QtGui.QFileDialog.getSaveFileName(parent,title,os.curdir,filter_)
        return g.u(s)
    #@+node:ekr.20081121105001.490: *5* runScrolledMessageDialog
    def runScrolledMessageDialog (self, title='Message', label= '', msg='', c=None, **kw):

        if g.unitTesting: return None

        def send(title=title, label=label, msg=msg, c=c, kw=kw):
            return g.doHook('scrolledMessage', title=title, label=label, msg=msg, c=c, **kw)

        if not c or not c.exists:
            #@+<< no c error>>
            #@+node:leohag.20081205043707.12: *6* << no c error>>
            g.es_print_error('%s\n%s\n\t%s' % (
                "The qt plugin requires calls to g.app.gui.scrolledMessageDialog to include 'c'",
                "as a keyword argument",
                g.callers()
            ))
            #@-<< no c error>>
        else:        
            retval = send()
            if retval: return retval
            #@+<< load scrolledmessage plugin >>
            #@+node:leohag.20081205043707.14: *6* << load scrolledmessage plugin >>
            pc = g.app.pluginsController
            sm = pc.getPluginModule('scrolledmessage')

            if not sm:
                sm = pc.loadOnePlugin('leo.plugins.scrolledmessage',verbose=True)
                if sm:
                    g.es('scrolledmessage plugin loaded.', color='blue')
                    sm.onCreate('tag',{'c':c})
            #@-<< load scrolledmessage plugin >>
            retval = send()
            if retval: return retval
            #@+<< no dialog error >>
            #@+node:leohag.20081205043707.11: *6* << no dialog error >>
            g.es_print_error(
                'No handler for the "scrolledMessage" hook.\n\t%s' % (
                    g.callers()))
            #@-<< no dialog error >>

        #@+<< emergency fallback >>
        #@+node:leohag.20081205043707.13: *6* << emergency fallback >>
        b = QtGui.QMessageBox
        d = b(None) # c.frame.top)
        d.setWindowFlags(QtCore.Qt.Dialog) # That is, not a fixed size dialog.

        d.setWindowTitle(title)
        if msg: d.setText(msg)
        d.setIcon(b.Information)
        yes = d.addButton('Ok',b.YesRole)
        d.exec_()
        #@-<< emergency fallback >>
    #@+node:ekr.20081121105001.491: *4* Focus (qtGui)
    def get_focus(self,c=None):

        """Returns the widget that has focus."""

        w = QtGui.QApplication.focusWidget()
        if isinstance(w,QTextBrowserSubclass):
            w = w.leo_wrapper
            if c and not w:
                # Kludge: DynamicWindow creates the body pane
                # with wrapper = None, so return the leoQtBody.
                w = c.frame.body
        # g.trace('leoQtGui',w,c,g.callers(5))
        return w

    def set_focus(self,c,w):

        """Put the focus on the widget."""

        trace = False and not g.unitTesting

        if w:
            if trace: g.trace('leoQtGui',w,g.callers(4))
            w.setFocus()
    #@+node:ekr.20081121105001.492: *4* Font
    #@+node:ekr.20081121105001.493: *5* qtGui.getFontFromParams
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

        if not family:
            family = g.app.config.defaultFontFamily
        if not family:
            family = 'DejaVu Sans Mono'

        try:
            font = QtGui.QFont(family,size,weight_val,italic)
            # g.trace(family,size,slant,weight,'returns',font)
            return font
        except:
            g.es("exception setting font",g.callers(4))
            g.es("","family,size,slant,weight:","",family,"",size,"",slant,"",weight)
            # g.es_exception() # This just confuses people.
            return g.app.config.defaultFont
    #@+node:ekr.20081121105001.494: *4* getFullVersion
    def getFullVersion (self):

        try:
            qtLevel = 'version %s' % QtCore.QT_VERSION_STR
        except Exception:
            # g.es_exception()
            qtLevel = '<qtLevel>'

        return 'qt %s' % (qtLevel)
    #@+node:ekr.20081121105001.495: *4* Icons
    #@+node:ekr.20081121105001.496: *5* attachLeoIcon (qtGui)
    def attachLeoIcon (self,window):

        """Attach a Leo icon to the window."""

        #icon = self.getIconImage('leoApp.ico')

        #window.setWindowIcon(icon)
        window.setWindowIcon(QtGui.QIcon(g.app.leoDir + "/Icons/leoapp32.png"))    
        #window.setLeoWindowIcon()
    #@+node:ekr.20081121105001.497: *5* getIconImage (qtGui)
    def getIconImage (self,name):

        '''Load the icon and return it.'''

        trace = False and not g.unitTesting

        # Return the image from the cache if possible.
        if name in self.iconimages:
            image = self.iconimages.get(name)
            if trace and not name.startswith('box'):
                g.trace('cached',id(image),name)
            return image
        try:
            fullname = g.os_path_finalize_join(g.app.loadDir,"..","Icons",name)

            if 0: # Not needed: use QTreeWidget.setIconsize.
                pixmap = QtGui.QPixmap()
                pixmap.load(fullname)
                image = QtGui.QIcon(pixmap)
            else:
                image = QtGui.QIcon(fullname)

            self.iconimages[name] = image
            if trace: g.trace('new',id(image),name)
            return image

        except Exception:
            g.es("exception loading:",fullname)
            g.es_exception()
            return None
    #@+node:tbrown.20081229204443.10: *5* getImageImage
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
    #@+node:ekr.20081123003126.2: *5* getTreeImage (test)
    def getTreeImage (self,c,path):

        image = QtGui.QPixmap(path)

        if image.height() > 0 and image.width() > 0:
            return image,image.height()
        else:
            return None,None
    #@+node:ekr.20081121105001.498: *4* Idle Time
    #@+node:ekr.20081121105001.499: *5* qtGui.setIdleTimeHook & setIdleTimeHookAfterDelay
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
    #@+node:ekr.20081121105001.501: *4* isTextWidget
    def isTextWidget (self,w):

        '''Return True if w is a Text widget suitable for text-oriented commands.'''

        if not w: return False

        val = (
            isinstance(w,leoFrame.baseTextWidget) or
            isinstance(w,leoQtBody) or
            isinstance(w,leoQtLog) or
            isinstance(w,leoQtBaseTextWidget)
        )

        # g.trace(val,w)

        return val

    #@+node:ekr.20090406111739.14: *4* Style Sheets
    #@+node:ekr.20090406111739.13: *5* setStyleSetting (qtGui)
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
    #@+node:ekr.20090406111739.12: *5* setWidgetColor (qtGui)
    badWidgetColors = []

    def setWidgetColor (self,w,widgetKind,selector,colorName):

        if not colorName: return

        # g.trace(widgetKind,selector,colorName,g.callers(4))

        # A bit of a hack: Qt color names do not end with a digit.
        # Remove them to avoid annoying qt color warnings.
        if colorName[-1].isdigit():
            colorName = colorName[:-1]

        if colorName in self.badWidgetColors:
            pass
        elif QtGui.QColor(colorName).isValid():
            g.app.gui.setStyleSetting(w,widgetKind,selector,colorName)
        else:
            self.badWidgetColors.append(colorName)
            g.es_print('bad widget color %s for %s' % (
                colorName,widgetKind),color='blue')
    #@+node:ekr.20081121105001.502: *4* toUnicode (qtGui)
    def toUnicode (self,s):

        try:
            s = g.u(s)
            return s
        except Exception:
            g.trace('*** Unicode Error: bugs possible')
            # The mass update omitted the encoding param.
            return g.toUnicode(s,reportErrors='replace')
    #@+node:ekr.20081121105001.503: *4* widget_name (qtGui)
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
    #@+node:ekr.20081121105001.504: *4* makeScriptButton (to do)
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
        #@+<< create the button b >>
        #@+node:ekr.20081121105001.505: *5* << create the button b >>
        iconBar = c.frame.getIconBarObject()
        b = iconBar.add(text=buttonText)
        #@-<< create the button b >>
        #@+<< define the callbacks for b >>
        #@+node:ekr.20081121105001.506: *5* << define the callbacks for b >>
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
        #@-<< define the callbacks for b >>
        b.configure(command=executeScriptCallback)
        c.bind(b,'<3>',deleteButtonCallback)
        if shortcut:
            #@+<< bind the shortcut to executeScriptCallback >>
            #@+node:ekr.20081121105001.507: *5* << bind the shortcut to executeScriptCallback >>
            func = executeScriptCallback
            shortcut = k.canonicalizeShortcut(shortcut)
            ok = k.bindKey ('button', shortcut,func,buttonText)
            if ok:
                g.es_print('bound @button',buttonText,'to',shortcut,color='blue')
            #@-<< bind the shortcut to executeScriptCallback >>
        #@+<< create press-buttonText-button command >>
        #@+node:ekr.20081121105001.508: *5* << create press-buttonText-button command >>
        aList = [g.choose(ch.isalnum(),ch,'-') for ch in buttonText]

        buttonCommandName = ''.join(aList)
        buttonCommandName = buttonCommandName.replace('--','-')
        buttonCommandName = 'press-%s-button' % buttonCommandName.lower()

        # This will use any shortcut defined in an @shortcuts node.
        k.registerCommand(buttonCommandName,None,executeScriptCallback,pane='button',verbose=False)
        #@-<< create press-buttonText-button command >>
    #@-others
#@+node:ekr.20081121105001.509: ** Non-essential
#@+node:ekr.20081121105001.512: *3* quickheadlines
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
        for n in p.children():
            self.listWidget.addItem(n.h)



#@+node:ekr.20081121105001.513: ** Key handling
#@+node:ekr.20081121105001.514: *3* class leoKeyEvent
class leoKeyEvent:

    '''A wrapper for wrapper for qt events.

    This does *not* override leoGui.leoKeyevent because
    it is a separate class, not member of leoQtGui.'''

    def __init__ (self,event,c,w,ch,tkKey,stroke):

        trace = False and not g.unitTesting

        if trace: print(
            'leoKeyEvent.__init__: ch: %s, tkKey: %s, stroke: %s' % (
                repr(ch),repr(tkKey),repr(stroke)))

        # Last minute-munges to keysym.
        if tkKey in ('Return','Tab','Escape'):
            ch = tkKey
        stroke = stroke.replace('\t','Tab')
        tkKey = tkKey.replace('\t','Tab')

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
#@+node:ekr.20081121105001.166: *3* class leoQtEventFilter
class leoQtEventFilter(QtCore.QObject):

    #@+<< about internal bindings >>
    #@+node:ekr.20081121105001.167: *4* << about internal bindings >>
    #@@nocolor-node
    #@+at
    # 
    # Here are the rules for translating key bindings (in leoSettings.leo) into keys
    # for k.bindingsDict:
    # 
    # 1.  The case of plain letters is significant:  a is not A.
    # 
    # 2. The Shift- prefix can be applied *only* to letters. Leo will ignore (with a
    # warning) the shift prefix applied to any other binding, e.g., Ctrl-Shift-(
    # 
    # 3. The case of letters prefixed by Ctrl-, Alt-, Key- or Shift- is *not*
    # significant. Thus, the Shift- prefix is required if you want an upper-case
    # letter (with the exception of 'bare' uppercase letters.)
    # 
    # The following table illustrates these rules. In each row, the first entry is the
    # key (for k.bindingsDict) and the other entries are equivalents that the user may
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
    # This table is consistent with how Leo already works (because it is consistent
    # with Tk's key-event specifiers). It is also, I think, the least confusing set of
    # rules.
    #@-<< about internal bindings >>

    #@+others
    #@+node:ekr.20081121105001.180: *4*  ctor
    def __init__(self,c,w,tag=''):

        # g.trace('leoQtEventFilter',tag,w)

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


    #@+node:ekr.20090407101640.10: *4* char2tkName
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
        'Ins':      'Insert', # was 'Return',
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
        # 'Insert':'Insert',
        'Return':'Return',
        # 'Tab':'Tab',
        'Tab':'\t', # A hack for QLineEdit.
        # Unused: Break, Caps_Lock,Linefeed,Num_lock
    }

    def char2tkName (self,ch):
        val = self.char2tkNameDict.get(ch)
        # g.trace(repr(ch),repr(val))
        return val
    #@+node:ekr.20081121105001.168: *4* eventFilter
    def eventFilter(self, obj, event):

        trace = False and not g.unitTesting
        verbose = False
        traceEvent = False
        traceKey = True
        traceFocus = False
        c = self.c ; k = c.k
        eventType = event.type()
        ev = QtCore.QEvent
        gui = g.app.gui
        aList = []

        # if trace and verbose: g.trace('*****',eventType)

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
            ### This is extremely bad.  At present, it is needed to handle tab properly.
            elif self.isSpecialOverride(tkKey,ch):
                override = True
            elif k.inState():
                override = not ignore # allow all keystrokes.
            else:
                override = len(aList) > 0
            if trace and verbose: g.trace(
                tkKey,len(aList),'ignore',ignore,'override',override)
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
                if trace and traceKey and verbose:
                    g.trace(self.tag,'unbound',tkKey,stroke)

        if trace and traceEvent: self.traceEvent(obj,event,tkKey,override)

        return override
    #@+node:ekr.20081121105001.182: *4* isSpecialOverride (simplified)
    def isSpecialOverride (self,tkKey,ch):

        '''Return True if tkKey is a special Tk key name.
        '''

        return tkKey or ch in self.flashers
    #@+node:ekr.20081121105001.172: *4* qtKey
    def qtKey (self,event):

        '''Return the components of a Qt key event.'''

        trace = False and not g.unitTesting
        keynum = event.key()
        text   = event.text() # This is the unicode text.
        toString = QtGui.QKeySequence(keynum).toString()

        try:
            ch1 = chr(keynum)
        except ValueError:
            ch1 = ''

        try:
            ch = g.u(ch1)
        except UnicodeError:
            ch = ch1

        text     = g.u(text)
        toString = g.u(toString)

        if trace and self.keyIsActive: g.trace(
            'keynum %s ch %s ch1 %s toString %s' % (
                repr(keynum),repr(ch),repr(ch1),repr(toString)))

        return keynum,text,toString,ch
    #@+node:ekr.20081121105001.173: *4* qtMods
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
    #@+node:ekr.20081121105001.174: *4* tkKey
    def tkKey (self,event,mods,keynum,text,toString,ch):

        '''Carefully convert the Qt key to a 
        Tk-style binding compatible with Leo's core
        binding dictionaries.'''

        trace = False and not g.unitTesting
        ch1 = ch # For tracing.
        use_shift = (
            'Home','End','Tab',
            'Up','Down','Left','Right',
            'Next','Prior', # 2010/01/10: Allow Shift-PageUp and Shift-PageDn.
            # Dubious...
            # 'Backspace','Delete','Ins',
            # 'F1',...'F12',
        )

        # Convert '&' to 'ampersand', etc.
        # *Do* allow shift-bracketleft, etc.
        ch2 = self.char2tkName(ch or toString)
        if ch2: ch = ch2 
        if not ch: ch = ''

        if 'Shift' in mods:
            if trace: g.trace(repr(ch))
            if len(ch) == 1 and ch.isalpha():
                mods.remove('Shift')
                ch = ch.upper()
            elif len(ch) > 1 and ch not in use_shift:
                # Experimental!
                mods.remove('Shift')
            # 2009/12/19: Speculative.
            # if ch in ('parenright','parenleft','braceright','braceleft'):
                # mods.remove('Shift')
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
    #@+node:ekr.20081121105001.169: *4* toStroke
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
    #@+node:ekr.20081121105001.170: *4* toTkKey
    def toTkKey (self,event):

        mods = self.qtMods(event)

        keynum,text,toString,ch = self.qtKey(event)

        tkKey,ch,ignore = self.tkKey(
            event,mods,keynum,text,toString,ch)

        return tkKey,ch,ignore
    #@+node:ekr.20081121105001.179: *4* traceEvent
    def traceEvent (self,obj,event,tkKey,override):

        if g.unitTesting: return

        c = self.c ; e = QtCore.QEvent
        keys = True ; traceAll = True 
        eventType = event.type()

        show = [
            # (e.Enter,'enter'),(e.Leave,'leave'),
            (e.FocusIn,'focus-in'),(e.FocusOut,'focus-out'),
            # (e.MouseMove,'mouse-move'),
            (e.MouseButtonPress,'mouse-dn'),
            (e.MouseButtonRelease,'mouse-up'),
        ]

        if keys:
            show2 = [
                (e.KeyPress,'key-press'),
                (e.KeyRelease,'key-release'),
                (e.ShortcutOverride,'shortcut-override'),
            ]
            show.extend(show2)

        ignore = (
            1,16,67,70,
            e.ChildPolished,
            e.DeferredDelete,
            e.DynamicPropertyChange,
            e.Enter,e.Leave,
            e.FocusIn,e.FocusOut,
            e.FontChange,
            e.Hide,e.HideToParent,
            e.HoverEnter,e.HoverLeave,e.HoverMove,
            e.LayoutRequest,
            e.MetaCall,e.Move,e.Paint,e.Resize,
            # e.MouseMove,e.MouseButtonPress,e.MouseButtonRelease,
            e.PaletteChange,
            e.ParentChange,
            e.Polish,e.PolishRequest,
            e.Show,e.ShowToParent,
            e.StyleChange,
            e.ToolTip,
            e.WindowActivate,e.WindowDeactivate,
            e.WindowBlocked,e.WindowUnblocked,
            e.ZOrderChange,
        )

        for val,kind in show:
            if eventType == val:
                g.trace(
                    '%5s %18s in-state: %5s key: %s override: %s' % (
                    self.tag,kind,repr(c.k.inState()),tkKey,override))
                return

        if traceAll and eventType not in ignore:
            g.trace('%3s:%s' % (eventType,'unknown'))
    #@+node:ekr.20090407080217.1: *4* traceFocus
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
    #@-others
#@+node:ekr.20081204090029.1: ** Syntax coloring
#@+node:ekr.20081205131308.15: *3* leoQtColorizer
# This is c.frame.body.colorizer

class leoQtColorizer:

    '''An adaptor class that interfaces Leo's core to two class:

    1. a subclass of QSyntaxHighlighter,

    2. the jEditColorizer class that contains the
       pattern-matchin code from the threading colorizer plugin.'''

    #@+others
    #@+node:ekr.20081205131308.16: *4*  ctor (leoQtColorizer)
    def __init__ (self,c,w):

        # g.trace('(leoQtColorizer)',w)

        self.c = c
        self.w = w

        # Step 1: create the ivars.
        self.changingText = False
        self.count = 0 # For unit testing.
        self.enabled = c.config.getBool('use_syntax_coloring')
        self.error = False # Set if there is an error in jeditColorizer.recolor
        self.flag = True # Per-node enable/disable flag.
        self.killColorFlag = False
        self.language = 'python' # set by scanColorDirectives.
        self.max_chars_to_colorize = c.config.getInt('qt_max_colorized_chars') or 0
        self.showInvisibles = False # 2010/1/2

        # Step 2: create the highlighter.
        self.highlighter = leoQtSyntaxHighlighter(c,w,colorizer=self)
        self.colorer = self.highlighter.colorer
        w.leo_colorizer = self

        # Step 3: finish enabling.
        if self.enabled:
            self.enabled = hasattr(self.highlighter,'currentBlock')
    #@+node:ekr.20081205131308.18: *4* colorize (leoQtColorizer)
    def colorize(self,p,incremental=False,interruptable=True):

        '''The main colorizer entry point.'''

        trace = False and not g.unitTesting

        self.count += 1 # For unit testing.

        if len(p.b) > self.max_chars_to_colorize > 0:
            self.flag = False
        elif self.enabled:
            oldLanguage = self.language
            oldFlag = self.flag
            self.updateSyntaxColorer(p) # sets self.flag.
            if trace: g.trace(self.flag,p.h)
            # if self.flag and (oldLanguage != self.language or not incremental):
            if oldFlag != self.flag or oldLanguage != self.language or not incremental:
                self.highlighter.rehighlight(p)

        return "ok" # For unit testing.
    #@+node:ekr.20090302125215.10: *4* enable/disable
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
    #@+node:ekr.20081207061047.10: *4* minor entry points
    def interrupt(self):
        pass

    def isSameColorState (self):
        return True # Disable some logic in leoTree.select.

    def kill (self):
        pass
    #@+node:ekr.20090226105328.12: *4* scanColorDirectives (leoQtColorizer)
    def scanColorDirectives(self,p):

        trace = False and not g.unitTesting

        p = p.copy() ; c = self.c
        if c == None: return # self.c may be None for testing.

        self.language = language = c.target_language
        self.rootMode = None # None, "code" or "doc"

        for p in p.self_and_parents():
            theDict = g.get_directives_dict(p)
            #@+<< Test for @language >>
            #@+node:ekr.20090226105328.13: *5* << Test for @language >>
            if 'language' in theDict:
                s = theDict["language"]
                i = g.skip_ws(s,0)
                j = g.skip_c_id(s,i)
                self.language = s[i:j].lower()
                break
            #@-<< Test for @language >>
            #@+<< Test for @root, @root-doc or @root-code >>
            #@+node:ekr.20090226105328.14: *5* << Test for @root, @root-doc or @root-code >>
            if 'root' in theDict and not self.rootMode:

                s = theDict["root"]
                if g.match_word(s,0,"@root-code"):
                    self.rootMode = "code"
                elif g.match_word(s,0,"@root-doc"):
                    self.rootMode = "doc"
                else:
                    doc = c.config.at_root_bodies_start_in_doc_mode
                    self.rootMode = g.choose(doc,"doc","code")
            #@-<< Test for @root, @root-doc or @root-code >>

        if trace: g.trace(self.language,g.callers(4))

        return self.language # For use by external routines.
    #@+node:ekr.20090216070256.11: *4* setHighlighter
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
    #@+node:ekr.20081205131308.24: *4* updateSyntaxColorer
    def updateSyntaxColorer (self,p):

        trace = False and not g.unitTesting
        p = p.copy()

        if len(p.b) > self.max_chars_to_colorize > 0:
            self.flag = False
        else:
            # self.flag is True unless an unambiguous @nocolor is seen.
            self.flag = self.useSyntaxColoring(p)
            self.scanColorDirectives(p)

        if trace: g.trace(self.flag,len(p.b),self.language,p.h,g.callers(5))
        return self.flag
    #@+node:ekr.20081205131308.23: *4* useSyntaxColoring & helper
    def useSyntaxColoring (self,p):

        """Return True unless p is unambiguously under the control of @nocolor."""

        trace = False and not g.unitTesting
        if not p:
            if trace: g.trace('no p',repr(p))
            return False

        p = p.copy()
        first = True ; kind = None ; val = True
        self.killColorFlag = False
        for p in p.self_and_parents():
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
    #@+node:ekr.20090214075058.12: *5* findColorDirectives
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
    #@-others

#@+node:ekr.20081205131308.27: *3* leoQtSyntaxHighlighter
# This is c.frame.body.colorizer.highlighter

class leoQtSyntaxHighlighter(QtGui.QSyntaxHighlighter):

    '''A subclass of QSyntaxHighlighter that overrides
    the highlightBlock and rehighlight methods.

    All actual syntax coloring is done in the jeditColorer class.'''

    #@+others
    #@+node:ekr.20081205131308.1: *4* ctor (leoQtSyntaxHighlighter)
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
    #@+node:ekr.20081205131308.11: *4* highlightBlock
    def highlightBlock (self,s):
        """ Called by QSyntaxHiglighter """

        if self.hasCurrentBlock and not self.colorizer.killColorFlag:
            if g.isPython3:
                s = str(s)
            else:
                s = unicode(s)
            self.colorer.recolor(s)

    #@+node:ekr.20081206062411.15: *4* rehighlight
    def rehighlight (self,p):

        '''Override base rehighlight method'''

        trace = False and not g.unitTesting
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

        if trace:
            g.trace('%s calls to recolor' % (
                self.colorer.recolorCount-n))
    #@-others
#@+node:ekr.20090614134853.3637: *3* class jeditColorizer
# This is c.frame.body.colorizer.highlighter.colorer

class jEditColorizer:

    '''This class contains jEdit pattern matchers adapted
    for use with QSyntaxHighlighter.'''

    #@+<< about the line-oriented jEdit colorizer >>
    #@+node:ekr.20090624080405.3856: *4* << about the line-oriented jEdit colorizer >>
    #@@nocolor-node
    #@+at
    # 
    # The aha behind the line-oriented jEdit colorizer is that we can define one or
    # more *restarter* methods for each pattern matcher that could possibly match
    # across line boundaries. I say "one or more" because we need a separate restarter
    # method for all combinations of arguments that can be passed to the jEdit pattern
    # matchers. In effect, these restarters are lambda bindings for the generic
    # restarter methods.
    # 
    # In actuality, very few restarters are needed. For example, for Python, we need
    # restarters for that look for continued strings, and both flavors of continued
    # triple-quoted strings. For python, these turn out to be three separate lambda
    # bindings for restart_match_span.
    # 
    # When a jEdit pattern matcher partially succeeds, it creates the lambda binding
    # for its restarter and calls setRestart to set the ending state of the present
    # line to an integer representing the bound restarter. setRestart calls
    # computeState to create a *string* representing the lambda binding of the
    # restarter. setRestart then calls stateNameToStateNumber to convert that string
    # to an integer state number that then gets passed to Qt's setCurrentBlockState.
    # The string is useful for debugging; Qt only uses the corresponding number.
    #@-<< about the line-oriented jEdit colorizer >>

    #@+others
    #@+node:ekr.20090614134853.3696: *4*  Birth & init
    #@+node:ekr.20090614134853.3697: *5* __init__ (jeditColorizer)
    def __init__(self,c,colorizer,highlighter,w):

        # Basic data...
        self.c = c
        self.colorizer = colorizer
        self.highlighter = highlighter # a QSyntaxHighlighter
        self.p = None
        self.w = w
        assert(w == self.c.frame.body.bodyCtrl)

        # Used by recolor and helpers...
        self.actualColorDict = {} # Used only by setTag.
        self.hyperCount = 0
        self.defaultState = 'default-state:' # The name of the default state.
        self.nextState = 1 # Dont use 0.
        self.restartDict = {} # Keys are state numbers, values are restart functions.
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
        self.showInvisibles = c.config.getBool("show_invisibles_by_default")
        self.colorizer.showInvisibles = self.showInvisibles
        # g.trace(self.showInvisibles)
            # Also set in init().
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
        self.last_language = None # The language for which configuration tags are valid.
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

        self.defineLeoKeywordsDict()
        self.defineDefaultColorsDict()
        self.defineDefaultFontDict()
    #@+node:ekr.20090614134853.3698: *6* defineLeoKeywordsDict
    def defineLeoKeywordsDict(self):

        self.leoKeywordsDict = {}

        for key in g.globalDirectiveList:
            self.leoKeywordsDict [key] = 'leoKeyword'
    #@+node:ekr.20090614134853.3699: *6* defineDefaultColorsDict
    def defineDefaultColorsDict (self):

        # These defaults are sure to exist.
        self.default_colors_dict = {
            # tag name       :(     option name,           default color),
            'blank'          :('blank_color',                 'black'), # 2010/1/2
            'tab'            :('tab_color',                   'black'), # 2010/1/2
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
            'bracketRange'   :('bracket_range_color','orange'),

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
            'keyword5'       :('keyword5_color', 'blue'),
            'label'          :('label_color',    'black'),
            'literal1'       :('literal1_color', '#00aa00'),
            'literal2'       :('literal2_color', '#00aa00'),
            'literal3'       :('literal3_color', '#00aa00'),
            'literal4'       :('literal4_color', '#00aa00'),
            'markup'         :('markup_color',   'red'),
            'null'           :('null_color',     'black'),
            'operator'       :('operator_color', 'black'),
        }
    #@+node:ekr.20090614134853.3700: *6* defineDefaultFontDict
    def defineDefaultFontDict (self):

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
            'tab'           : 'tab_font',

            # Tags used by forth.
            'bracketRange'   :'bracketRange_font',

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
    #@+node:ekr.20090614134853.3701: *5* addImportedRules
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
    #@+node:ekr.20090614134853.3702: *5* addLeoRules
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

            if g.isPython3:
                rule = rule.__func__
            else:
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
    #@+node:ekr.20090614134853.3703: *5* configure_tags
    def configure_tags (self):

        trace = False and not g.unitTesting
        verbose = False
        traceColor = False
        traceFonts = True
        c = self.c ; w = self.w

        if trace: g.trace(self.colorizer.language,g.callers(5))

        # The stated default is 40, but apparently it must be set explicitly.
        tabWidth = c.config.getInt('qt-tab-width') or 40
        w.widget.setTabStopWidth(tabWidth)

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
        keys = list(self.default_font_dict.keys()) ; keys.sort()
        for key in keys:
            option_name = self.default_font_dict[key]
            # First, look for the language-specific setting, then the general setting.
            for name in ('%s_%s' % (self.colorizer.language,option_name),(option_name)):
                font = self.fonts.get(name)
                if font:
                    if trace and traceFonts:
                        g.trace('**found',name,id(font))
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
                        self.fonts[key] = font
                        if trace and traceFonts:
                            g.trace('**found',key,name,family,size,slant,weight,id(font))
                        w.tag_config(key,font=font)
                        break

            else: # Neither the general setting nor the language-specific setting exists.
                if list(self.fonts.keys()): # Restore the default font.
                    if trace and traceFonts:
                        g.trace('default',key,)
                    self.fonts[key] = font # 2010/02/19: Essential
                    w.tag_config(key,font=defaultBodyfont)
                else:
                    if trace and traceFonts:
                        g.trace('no fonts')

        keys = list(self.default_colors_dict.keys()) ; keys.sort()
        for name in keys:
            option_name,default_color = self.default_colors_dict[name]
            color = (
                c.config.getColor('%s_%s' % (self.colorizer.language,option_name)) or
                c.config.getColor(option_name) or
                default_color
            )
            if trace and traceColor: g.trace(option_name,color)

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
    #@+node:ekr.20090614134853.3704: *5* configure_variable_tags
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
    #@+node:ekr.20090614134853.3705: *5* init (jeditColorizer)
    def init (self,p,s):

        trace = False and not g.unitTesting

        if p: self.p = p.copy()
        self.all_s = s or ''

        if trace: g.trace('='*20,self.colorizer.language) #,g.callers(4))

        # State info.
        self.all_s = s
        self.global_i,self.global_j = 0,0
        self.global_offset = 0

        # These *must* be recomputed.
        self.nextState = 1 # Dont use 0.
        self.stateDict = {}
        self.stateNameDict = {}
        self.restartDict = {}
        self.init_mode(self.colorizer.language)
        self.clearState()
        self.showInvisibles = self.colorizer.showInvisibles
            # The show/hide-invisible commands changes this.

        # Used by matchers.
        self.prev = None
        if self.last_language != self.colorizer.language:
            # Must be done to support per-language @font/@color settings.
            self.configure_tags()
            self.last_language = self.colorizer.language
    #@+node:ekr.20090614134853.3706: *5* init_mode & helpers
    def init_mode (self,name):

        '''Name may be a language name or a delegate name.'''

        trace = False and not g.unitTesting
        if not name: return False
        h = self.highlighter
        language,rulesetName = self.nameToRulesetName(name)
        # if trace: g.trace(name,list(self.modes.keys()))
        bunch = self.modes.get(rulesetName)
        if bunch:
            if trace: g.trace('found',language,rulesetName,g.callers(2))
            self.initModeFromBunch(bunch)
            return True
        else:
            if trace: g.trace(language,rulesetName)
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
                    rulesetName     = rulesetName,
                )
                if trace: g.trace('***** No colorizer file: %s.py' % language)
                self.rulesetName = rulesetName
                return False
            self.colorizer.language = language
            self.rulesetName = rulesetName
            self.properties = hasattr(mode,'properties') and mode.properties or {}
            self.keywordsDict = hasattr(mode,'keywordsDictDict') and mode.keywordsDictDict.get(rulesetName,{}) or {}
            self.setKeywords()
            self.attributesDict = hasattr(mode,'attributesDictDict') and mode.attributesDictDict.get(rulesetName) or {}
            # g.trace('*******',rulesetName,self.attributesDict)
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
                rulesetName     = self.rulesetName,
            )
            # Do this after 'officially' initing the mode, to limit recursion.
            self.addImportedRules(mode,self.rulesDict,rulesetName)
            self.updateDelimsTables()
            initialDelegate = self.properties.get('initialModeDelegate')
            if initialDelegate:
                if trace: g.trace('initialDelegate',initialDelegate)
                # Replace the original mode by the delegate mode.
                self.init_mode(initialDelegate)
                language2,rulesetName2 = self.nameToRulesetName(initialDelegate)
                self.modes[rulesetName] = self.modes.get(rulesetName2)
            return True
    #@+node:ekr.20090614134853.3707: *6* nameToRulesetName
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

        # if rulesetName == 'php_main': rulesetName = 'php_php'

        # g.trace(name,language,rulesetName)
        return language,rulesetName
    #@+node:ekr.20090614134853.3708: *6* setKeywords
    def setKeywords (self):

        '''Initialize the keywords for the present language.

         Set self.word_chars ivar to string.letters + string.digits
         plus any other character appearing in any keyword.'''

        # Add any new user keywords to leoKeywordsDict.
        d = self.keywordsDict
        keys = list(d.keys())
        for s in g.globalDirectiveList:
            key = '@' + s
            if key not in keys:
                d [key] = 'leoKeyword'

        # Create a temporary chars list.  It will be converted to a dict later.
        chars = [g.toUnicode(ch) for ch in (string.ascii_letters + string.digits)]

        for key in list(d.keys()):
            for ch in key:
                if ch not in chars:
                    chars.append(g.toUnicode(ch))

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
    #@+node:ekr.20090614134853.3709: *6* setModeAttributes
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

        # g.trace(d)

        for key, default in aList:
            val = d.get(key,default)
            if val in ('true','True'): val = True
            if val in ('false','False'): val = False
            setattr(self,key,val)
            # g.trace(key,val)
    #@+node:ekr.20090614134853.3710: *6* initModeFromBunch
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

        # State stuff.
        # h = self.highlighter
        # h.setCurrentBlockState(bunch.currentState)
        # self.nextState      = bunch.nextState
        # self.restartDict    = bunch.restartDict
        # self.stateDict      = bunch.stateDict
        # self.stateNameDict  = bunch.stateNameDict

        # self.clearState()

        # g.trace(self.rulesetName)

    #@+node:ekr.20090614134853.3711: *6* updateDelimsTables
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
    #@+node:ekr.20090614134853.3712: *5* munge
    def munge(self,s):

        '''Munge a mode name so that it is a valid python id.'''

        valid = string.ascii_letters + string.digits + '_'

        return ''.join([g.choose(ch in valid,ch.lower(),'_') for ch in s])
    #@+node:ekr.20090614134853.3713: *5* setFontFromConfig
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
    #@+node:ekr.20090614134853.3715: *4*  Pattern matchers
    #@+node:ekr.20090614134853.3816: *5*  About the pattern matchers
    #@@nocolor-node
    #@+at
    # 
    # The following jEdit matcher methods return the length of the matched text if the
    # match succeeds, and zero otherwise. In most cases, these methods colorize all
    # the matched text.
    # 
    # The following arguments affect matching:
    # 
    # - at_line_start         True: sequence must start the line.
    # - at_whitespace_end     True: sequence must be first non-whitespace text of the line.
    # - at_word_start         True: sequence must start a word.
    # - hash_char             The first character that must match in a regular expression.
    # - no_escape:            True: ignore an 'end' string if it is preceded by
    #                         the ruleset's escape character.
    # - no_line_break         True: the match will not succeed across line breaks.
    # - no_word_break:        True: the match will not cross word breaks.
    # 
    # The following arguments affect coloring when a match succeeds:
    # 
    # - delegate              A ruleset name. The matched text will be colored recursively
    #                         by the indicated ruleset.
    # - exclude_match         If True, the actual text that matched will not be colored.
    # - kind                  The color tag to be applied to colored text.
    #@+node:ekr.20090614134853.3716: *5* dump
    def dump (self,s):

        if s.find('\n') == -1:
            return s
        else:
            return '\n' + s + '\n'
    #@+node:ekr.20090614134853.3717: *5* Leo rule functions
    #@+node:ekr.20090614134853.3718: *6* match_at_color
    def match_at_color (self,s,i):

        if self.trace_leo_matches: g.trace()

        seq = '@color'

        # Only matches at start of line.
        if i != 0: return 0

        if g.match_word(s,i,seq):
            self.colorizer.flag = True # Enable coloring.
            j = i + len(seq)
            self.colorRangeWithTag(s,i,j,'leoKeyword')
            self.clearState()
            return j - i
        else:
            return 0
    #@+node:ekr.20090614134853.3719: *6* match_at_nocolor & restarter
    def match_at_nocolor (self,s,i):

        if self.trace_leo_matches: g.trace(i,repr(s))

        # Only matches at start of line.
        if i == 0 and not g.match(s,i,'@nocolor-') and g.match_word(s,i,'@nocolor'):
            self.setRestart(self.restartNoColor)
            return len(s) # Match everything.
        else:
            return 0
    #@+node:ekr.20090614213243.3838: *7* restartNoColor
    def restartNoColor (self,s):

        if self.trace_leo_matches: g.trace(repr(s))

        if g.match_word(s,0,'@color'):
            self.clearState()
        else:
            self.setRestart(self.restartNoColor)

        return len(s) # Always match everything.
    #@+node:ekr.20090614134853.3720: *6* match_at_killcolor & restarter
    def match_at_killcolor (self,s,i):

        if self.trace_leo_matches: g.trace(i,repr(s))

        # Only matches at start of line.
        if i != 0 and s[i-1] != '\n':
            return 0

        tag = '@killcolor'

        if g.match_word(s,i,tag):
            self.setRestart(self.restartKillColor)
            return len(s) # Match everything.
        else:
            return 0

    #@+node:ekr.20090614190437.3833: *7* restartKillColor
    def restartKillColor(self,s):

        self.setRestart(self.restartKillColor)
        return len(s)+1
    #@+node:ekr.20090614134853.3721: *6* match_at_nocolor_node & restarter
    def match_at_nocolor_node (self,s,i):

        if self.trace_leo_matches: g.trace()

        # Only matches at start of line.
        if i != 0 and s[i-1] != '\n':
            return 0

        tag = '@nocolor-node'

        if g.match_word(s,i,tag):
            self.setRestart(self.restartNoColorNode)
            return len(s) # Match everything.
        else:
            return 0
    #@+node:ekr.20090614213243.3836: *7* restartNoColorNode
    def restartNoColorNode(self,s):

        self.setRestart(self.restartNoColorNode)
        return len(s)+1
    #@+node:ekr.20090614134853.3722: *6* match_blanks
    def match_blanks (self,s,i):

        if not self.showInvisibles:
            return 0

        j = i ; n = len(s)

        while j < n and s[j] == ' ':
            j += 1

        if j > i:
            self.colorRangeWithTag(s,i,j,'blank')
            return j - i
        else:
            return 0
    #@+node:ekr.20090614134853.3723: *6* match_doc_part & restarter
    def match_doc_part (self,s,i):

        # New in Leo 4.5: only matches at start of line.
        if i != 0:
            return 0
        elif g.match_word(s,i,'@doc'):
            j = i + 4
        elif g.match(s,i,'@') and (i+1 >= len(s) or s[i+1] in (' ','\t','\n')):
            j = i + 1
        else:
            return 0

        self.colorRangeWithTag(s,i,j,'leoKeyword')
        self.colorRangeWithTag(s,j,len(s),'docPart')
        self.setRestart(self.restartDocPart)
        return len(s)
    #@+node:ekr.20090614213243.3837: *7* restartDocPart
    def restartDocPart (self,s):

        for tag in ('@c','@code'):
            if g.match_word(s,0,tag):
                j = len(tag)
                self.colorRangeWithTag(s,0,j,'leoKeyword') # 'docPart')
                self.clearState()
                return j
        else:
            self.setRestart(self.restartDocPart)
            self.colorRangeWithTag(s,0,len(s),'docPart')
            return len(s)
    #@+node:ekr.20090614134853.3724: *6* match_leo_keywords
    def match_leo_keywords(self,s,i):

        '''Succeed if s[i:] is a Leo keyword.'''

        # g.trace(i,g.get_line(s,i))

        self.totalLeoKeywordsCalls += 1

        if s[i] != '@':
            return 0

        # fail if something besides whitespace precedes the word on the line.
        i2 = i-1
        while i2 >= 0:
            ch = s[i2]
            if ch == '\n':
                break
            elif ch in (' ','\t'):
                i2 -= 1
            else:
                # g.trace('not a word 1',repr(ch))
                return 0

        # Get the word as quickly as possible.
        j = i+1
        while j < len(s) and s[j] in self.word_chars:
            j += 1
        word = s[i+1:j] # entries in leoKeywordsDict do not start with '@'.

        if j < len(s) and s[j] not in (' ','\t','\n'):
            # g.trace('not a word 2',repr(word))
            return 0 # Fail, but allow a rescan, as in objective_c.

        if self.leoKeywordsDict.get(word):
            kind = 'leoKeyword'
            self.colorRangeWithTag(s,i,j,kind)
            self.prev = (i,j,kind)
            result = j-i+1 # Bug fix: skip the last character.
            self.trace_match(kind,s,i,j)
            # g.trace('*** match',repr(s))
            return result
        else:
            # 2010/10/20: also check the keywords dict here.
            # This allows for objective_c keywords starting with '@'
            # This will not slow down Leo, because it is called
            # for things that look like Leo directives.
            word = '@' + word
            kind = self.keywordsDict.get(word)
            if kind:
                self.colorRangeWithTag(s,i,j,kind)
                self.prev = (i,j,kind)
                self.trace_match(kind,s,i,j)
                # g.trace('found',word)
                return j-i
            else:
                # g.trace('fail',repr(word),repr(self.word_chars))
                return -(j-i+1) # An important optimization.
    #@+node:ekr.20090614134853.3725: *6* match_section_ref
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
                    #@+<< set the hyperlink >>
                    #@+node:ekr.20090614134853.3726: *7* << set the hyperlink >>
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
                    #@-<< set the hyperlink >>
                else:
                    self.colorRangeWithTag(s,i+2,k,'link')
            else:
                self.colorRangeWithTag(s,i+2,k,'name')
            self.colorRangeWithTag(s,k,j,'nameBrackets')
            return j - i
        else:
            return 0
    #@+node:ekr.20090614134853.3727: *6* match_tabs
    def match_tabs (self,s,i):

        if not self.showInvisibles:
            return 0

        if self.trace_leo_matches: g.trace()

        j = i ; n = len(s)

        while j < n and s[j] == '\t':
            j += 1

        if j > i:
            self.colorRangeWithTag(s,i,j,'tab')
            return j - i
        else:
            return 0
    #@+node:ekr.20090614134853.3728: *5* match_eol_span
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
            return 0

        if g.match(s,i,seq):
            j = len(s)
            self.colorRangeWithTag(s,i,j,kind,delegate=delegate,exclude_match=exclude_match)
            self.prev = (i,j,kind)
            self.trace_match(kind,s,i,j)
            return j # (was j-1) With a delegate, this could clear state.
        else:
            return 0
    #@+node:ekr.20090614134853.3729: *5* match_eol_span_regexp
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
            j = len(s)
            self.colorRangeWithTag(s,i,j,kind,delegate=delegate,exclude_match=exclude_match)
            self.prev = (i,j,kind)
            self.trace_match(kind,s,i,j)
            return j - i
        else:
            return 0
    #@+node:ekr.20100330091222.3702: *5* match_everything
    # def match_everything (self,s,i,kind=None,delegate='',exclude_match=False):

        # '''Match the entire rest of the string.'''

        # j = len(s)
        # self.colorRangeWithTag(s,i,j,kind,delegate=delegate)

        # return j
    #@+node:ekr.20090614134853.3730: *5* match_keywords
    # This is a time-critical method.
    def match_keywords (self,s,i):

        '''Succeed if s[i:] is a keyword.'''

        # trace = False
        self.totalKeywordsCalls += 1

        # Important.  Return -len(word) for failure greatly reduces
        # the number of times this method is called.

        # We must be at the start of a word.
        if i > 0 and s[i-1] in self.word_chars:
            # if trace: g.trace('not at word start',s[i-1])
            return 0

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
            # if trace: g.trace('success',word,kind,j-i)
            self.trace_match(kind,s,i,j)
            return result
        else:
            # if trace: g.trace('fail',word,kind)
            return -len(word) # An important new optimization.
    #@+node:ekr.20090614134853.3731: *5* match_mark_following & getNextToken
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
            return j - i
        else:
            return 0
    #@+node:ekr.20090614134853.3732: *6* getNextToken
    def getNextToken (self,s,i):

        '''Return the index of the end of the next token for match_mark_following.

        The jEdit docs are not clear about what a 'token' is, but experiments with jEdit
        show that token means a word, as defined by word_chars.'''

        while i < len(s) and s[i] in self.word_chars:
            i += 1

        return min(len(s),i+1)
    #@+node:ekr.20090614134853.3733: *5* match_mark_previous
    def match_mark_previous (self,s,i,
        kind='',pattern='',
        at_line_start=False,at_whitespace_end=False,at_word_start=False,
        exclude_match=False):

        '''Return the length of a matched SEQ or 0 if no match.

        'at_line_start':    True: sequence must start the line.
        'at_whitespace_end':True: sequence must be first non-whitespace text of the line.
        'at_word_start':    True: sequence must start a word.'''

        # This match was causing most of the syntax-color problems.
        return 0 # 2009/6/23
    #@+node:ekr.20090614134853.3734: *5* match_regexp_helper
    def match_regexp_helper (self,s,i,pattern):

        '''Return the length of the matching text if seq (a regular expression) matches the present position.'''

        trace = True and not g.unitTesting
        if trace: g.trace('%-10s %-20s %s' % (
            self.colorizer.language,pattern,s)) # g.callers(1)

        try:
            flags = re.MULTILINE
            if self.ignore_case: flags|= re.IGNORECASE
            re_obj = re.compile(pattern,flags)
        except Exception:
            # Do not call g.es here!
            g.trace('Invalid regular expression: %s' % (pattern))
            return 0

        # Match succeeds or fails more quickly than search.
        self.match_obj = mo = re_obj.match(s,i) # re_obj.search(s,i) 

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
    #@+node:ekr.20090614134853.3735: *5* match_seq
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
        else:
            j = i
        return j - i
    #@+node:ekr.20090614134853.3736: *5* match_seq_regexp
    def match_seq_regexp (self,s,i,
        kind='',regexp='',
        at_line_start=False,at_whitespace_end=False,at_word_start=False,
        delegate=''):

        '''Succeed if the regular expression regexp matches at s[i:].'''

        if self.verbose: g.trace(g.callers(1),i,repr(s[i:i+20]),'regexp',regexp)

        if at_line_start and i != 0 and s[i-1] != '\n': return 0
        if at_whitespace_end and i != g.skip_ws(s,0): return 0
        if at_word_start and i > 0 and s[i-1] in self.word_chars: return 0

        n = self.match_regexp_helper(s,i,regexp)
        j = i + n
        assert (j-i == n)
        self.colorRangeWithTag(s,i,j,kind,delegate=delegate)
        self.prev = (i,j,kind)
        self.trace_match(kind,s,i,j)
        return j - i
    #@+node:ekr.20090614134853.3737: *5* match_span & helper & restarter
    def match_span (self,s,i,
        kind='',begin='',end='',
        at_line_start=False,at_whitespace_end=False,at_word_start=False,
        delegate='',exclude_match=False,
        no_escape=False,no_line_break=False,no_word_break=False):

        '''Succeed if s[i:] starts with 'begin' and contains a following 'end'.'''

        trace = False and not g.unitTesting
        if i >= len(s): return 0

        # g.trace(begin,end,no_escape,no_line_break,no_word_break)

        if at_line_start and i != 0 and s[i-1] != '\n':
            j = i
        elif at_whitespace_end and i != g.skip_ws(s,0):
            j = i
        elif at_word_start and i > 0 and s[i-1] in self.word_chars:
            j = i
        elif at_word_start and i + len(begin) + 1 < len(s) and s[i+len(begin)] in self.word_chars:
            j = i
        elif not g.match(s,i,begin):
            j = i
        else:
            # We have matched the start of the span.
            j = self.match_span_helper(s,i+len(begin),end,
                no_escape,no_line_break,no_word_break=no_word_break)
            # g.trace('** helper returns',j,len(s))
            if j == -1:
                j = i # A real failure.
            else:
                # A match
                i2 = i + len(begin) ; j2 = j + len(end)
                if delegate:
                    self.colorRangeWithTag(s,i,i2,kind,delegate=None,    exclude_match=exclude_match)
                    self.colorRangeWithTag(s,i2,j,kind,delegate=delegate,exclude_match=exclude_match)
                    self.colorRangeWithTag(s,j,j2,kind,delegate=None,    exclude_match=exclude_match)
                else:
                    self.colorRangeWithTag(s,i,j2,kind,delegate=None,exclude_match=exclude_match)
                j = j2
                self.prev = (i,j,kind)

        self.trace_match(kind,s,i,j)

        if j > len(s):
            j = len(s) + 1
            def boundRestartMatchSpan(s):
                # Note: bindings are frozen by this def.
                return self.restart_match_span(s,
                    # Positional args, in alpha order
                    delegate,end,exclude_match,kind,
                    no_escape,no_line_break,no_word_break)

            self.setRestart(boundRestartMatchSpan,
                # These must be keywords args.
                delegate=delegate,end=end,
                exclude_match=exclude_match,
                kind=kind,
                no_escape=no_escape,
                no_line_break=no_line_break,
                no_word_break=no_word_break)

            if trace: g.trace('***Continuing',kind,i,j,len(s))
        elif j != i:
            if trace: g.trace('***Ending',kind,i,j,s[i:j])
            self.clearState()

        return j - i # Correct, whatever j is.
    #@+node:ekr.20090614134853.3738: *6* match_span_helper
    def match_span_helper (self,s,i,pattern,no_escape,no_line_break,no_word_break):

        '''Return n >= 0 if s[i] ends with a non-escaped 'end' string.'''

        esc = self.escape

        while 1:
            j = s.find(pattern,i)
            # g.trace(no_line_break,j,len(s))
            if j == -1:
                # Match to end of text if not found and no_line_break is False
                if no_line_break:
                    return -1
                else:
                    return len(s)+1
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
    #@+node:ekr.20090614134853.3821: *6* restart_match_span
    def restart_match_span (self,s,
        delegate,end,exclude_match,kind,
        no_escape,no_line_break,no_word_break):

        '''Remain in this state until 'end' is seen.'''

        trace = False and not g.unitTesting

        i = 0
        j = self.match_span_helper(s,i,end,no_escape,no_line_break,no_word_break)
        if j == -1:
            j2 = len(s)+1
        elif j > len(s):
            j2 = j
        else:
            j2 = j + len(end)

        if delegate:
            self.colorRangeWithTag(s,i,j,kind,delegate=delegate,exclude_match=exclude_match)
            self.colorRangeWithTag(s,j,j2,kind,delegate=None,    exclude_match=exclude_match)
        else: # avoid having to merge ranges in addTagsToList.
            self.colorRangeWithTag(s,i,j2,kind,delegate=None,exclude_match=exclude_match)
        j = j2

        self.trace_match(kind,s,i,j)

        if j > len(s):
            def boundRestartMatchSpan(s):
                return self.restart_match_span(s,
                    # Positional args, in alpha order
                    delegate,end,exclude_match,kind,
                    no_escape,no_line_break,no_word_break)

            self.setRestart(boundRestartMatchSpan,
                # These must be keywords args.
                delegate=delegate,end=end,kind=kind,
                no_escape=no_escape,
                no_line_break=no_line_break,
                no_word_break=no_word_break)

            if trace: g.trace('***Re-continuing',i,j,len(s),s,g.callers(5))
        else:
            if trace: g.trace('***ending',i,j,len(s),s)
            self.clearState()

        return j # Return the new i, *not* the length of the match.
    #@+node:ekr.20090614134853.3739: *5* match_span_regexp
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
    #@+node:ekr.20090614134853.3740: *5* match_word_and_regexp
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
        if at_word_start and i > 0 and s[i-1] in self.word_chars: return 0
        if at_word_start and i + len(word) + 1 < len(s) and s[i+len(word)] in self.word_chars:
            j = i

        if not g.match(s,i,word):
            return 0

        j = i + len(word)
        n = self.match_regexp_helper(s,j,pattern)
        if n == 0:
            return 0
        self.colorRangeWithTag(s,i,j,kind1,exclude_match=exclude_match)
        k = j + n
        self.colorRangeWithTag(s,j,k,kind2,exclude_match=False)    
        self.prev = (j,k,kind2)
        self.trace_match(kind1,s,i,j)
        self.trace_match(kind2,s,j,k)
        return k - i
    #@+node:ekr.20090614134853.3741: *5* skip_line
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
    #@+node:ekr.20090614134853.3742: *5* trace_match
    def trace_match(self,kind,s,i,j):

        if j != i and self.trace_match_flag:
            g.trace(kind,i,j,g.callers(2),self.dump(s[i:j]))
    #@+node:ekr.20090614134853.3828: *4*  State methods
    #@+node:ekr.20090625061310.3860: *5* clearState
    def clearState (self):

        self.setState(-1)
    #@+node:ekr.20090614134853.3825: *5* computeState
    def computeState (self,f,keys):

        '''Compute the state name associated with f and all the keys.

        Return a unique int n representing that state.'''

        # Abbreviate arg names.
        d = {
            'delegate':'del:',
            'end':'end',
            'at_line_start':'line-start',
            'at_whitespace_end':'ws-end',
            'exclude_match':'exc-match',
            'no_escape':'no-esc',
            'no_line_break':'no-brk',
            'no_word_break':'no-word-brk',
        }
        result = [
            f.__name__,
            self.colorizer.language,
            self.rulesetName]
        for key in keys:
            keyVal = keys.get(key)
            val = d.get(key)
            if val is None:
                val = keys.get(key)
                result.append('%s=%s' % (key,val))
            elif keyVal is True:
                result.append('%s' % val)
            elif keyVal is False:
                pass
            elif keyVal not in (None,''):
                result.append('%s=%s' % (key,keyVal))
        state = ';'.join(result)

        n = self.stateNameToStateNumber(f,state)
        return n
    #@+node:ekr.20090625061310.3863: *5* currentState and prevState
    def currentState(self):

        return self.highlighter.currentBlockState()

    def prevState(self):

        return self.highlighter.previousBlockState()
    #@+node:ekr.20090614134853.3824: *5* setRestart
    def setRestart (self,f,**keys):

        n = self.computeState(f,keys)
        self.setState(n)
    #@+node:ekr.20090625061310.3861: *5* setState
    def setState (self,n):

        trace = False and not g.unitTesting

        self.highlighter.setCurrentBlockState(n)

        if trace:
            stateName = self.showState(n)
            g.trace(stateName,g.callers(4))
    #@+node:ekr.20090625061310.3862: *5* showState & showCurrentState
    def showState (self,n):

        if n == -1: 
            return 'default-state'
        else:
            return self.stateDict.get(n,'<no state>')

    def showCurrentState(self):

        n = self.currentState()
        return self.showState(n)

    def showPrevState(self):

        n = self.prevState()
        return self.showState(n)
    #@+node:ekr.20090614134853.3826: *5* stateNameToStateNumber
    def stateNameToStateNumber (self,f,stateName):

        # stateDict:     Keys are state numbers, values state names.
        # stateNameDict: Keys are state names, values are state numbers.
        # restartDict:   Keys are state numbers, values are restart functions

        n = self.stateNameDict.get(stateName)
        if n is None:
            n = self.nextState
            self.stateNameDict[stateName] = n
            self.stateDict[n] = stateName
            self.restartDict[n] = f
            self.nextState += 1
            # g.trace('========',n,stateName)

        return n
    #@+node:ekr.20090614134853.3714: *4* colorRangeWithTag
    def colorRangeWithTag (self,s,i,j,tag,delegate='',exclude_match=False):

        '''Actually colorize the selected range.

        This is called whenever a pattern matcher succeed.'''

        trace = False and not g.unitTesting

        # Pattern matcher may set the .flag ivar.
        if self.colorizer.killColorFlag or not self.colorizer.flag:
            if trace: g.trace('disabled')
            return

        if delegate:
            if trace: g.trace('delegate %-12s %3s %3s %10s %s' % (
                delegate,i,j,tag,s[i:j])) # ,g.callers(2))
            self.modeStack.append(self.modeBunch)
            self.init_mode(delegate)
            # Color everything now, using the same indices as the caller.
            while 0 <= i < j and i < len(s):
                progress = i
                assert j >= 0,j
                for f in self.rulesDict.get(s[i],[]):
                    n = f(self,s,i)
                    if n is None:
                        g.trace('Can not happen: delegate matcher returns None')
                    elif n > 0:
                        # if trace: g.trace('delegate',delegate,i,n,f.__name__,repr(s[i:i+n]))
                        i += n ; break
                else:
                    # New in Leo 4.6: Use the default chars for everything else.
                    # New in Leo 4.8 devel: use the *delegate's* default characters if possible.
                    default_tag = self.attributesDict.get('default')
                    # g.trace(default_tag)
                    self.setTag(default_tag or tag,s,i,i+1)
                    i += 1
                assert i > progress
            bunch = self.modeStack.pop()
            self.initModeFromBunch(bunch)
        elif not exclude_match:
            self.setTag(tag,s,i,j)
    #@+node:ekr.20090614134853.3754: *4* mainLoop & restart
    def mainLoop(self,n,s):

        '''Colorize string s, starting in state n.'''

        trace = False and not g.unitTesting
        traceMatch = True ; traceState = True ; verbose = True

        if trace and traceState: g.trace('** start',self.showState(n),s)

        i = 0
        if n > -1:
            i = self.restart(n,s,trace and traceMatch)
        if i == 0:
            self.setState(self.prevState())

        while i < len(s):
            progress = i
            functions = self.rulesDict.get(s[i],[])
            for f in functions:
                n = f(self,s,i)
                if n is None:
                    g.trace('Can not happen: n is None',repr(f))
                    break
                elif n > 0: # Success.
                    if trace and traceMatch and f.__name__!='match_blanks':
                        g.trace('match: %20s %s' % (
                            f.__name__,s[i:i+n]))
                    i += n
                    break # Stop searching the functions.
                elif n < 0: # Fail and skip n chars.
                    if trace and traceMatch and verbose:
                        g.trace('fail: %20s %s' % (
                            f.__name__,s[i:i+n]))
                    i += -n
                    break # Stop searching the functions.
                else: # Fail. Try the next function.
                    pass # Do not break or change i!
            else:
                i += 1
            assert i > progress

        # Don't even *think* about clearing state here.
        # We remain in the starting state unless a match happens.
        if trace and traceState:
            g.trace('** end',self.showCurrentState(),s)
    #@+node:ekr.20090625061310.3864: *5* restart
    def restart (self,n,s,traceMatch):

        f = self.restartDict.get(n)
        if f:
            i = f(s)
            fname = f.__name__
            if traceMatch:
                if i > 0:
                    g.trace('** restart match',fname,s[:i])
                else:
                    g.trace('** restart fail',fname,s)
        else:
            g.trace('**** no restart f')
            i = 0

        return i
    #@+node:ekr.20090614134853.3753: *4* recolor
    def recolor (self,s):

        '''Recolor line s.'''

        trace = False and not g.unitTesting
        callers = False ; line = True ; state = False

        # Update the counts.
        self.recolorCount += 1
        self.totalChars += len(s)

        if self.colorizer.changingText:
            return
        if not self.colorizer.flag:
            return

        # Get the previous state.
        n = self.prevState() # The state at the end of the previous line.
        if trace:
            if line and state:
                g.trace('%2s %-50s %s' % (n,self.showState(n),s))
            elif line:
                g.trace('%2s %s' % (n,s))
            if callers: g.trace(g.callers())

        if s.strip():
            self.mainLoop(n,s)
        else:
            self.setState(n) # Required
    #@+node:ekr.20090614134853.3813: *4* setTag
    def setTag (self,tag,s,i,j):

        trace = False and not g.unitTesting

        if i == j:
            if trace: g.trace('empty range')
            return

        w = self.w
        colorName = w.configDict.get(tag)

        # Munge the color name.
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

        underline = w.configUnderlineDict.get(tag)

        format = QtGui.QTextCharFormat()

        font = self.fonts.get(tag)
        if font:
            format.setFont(font)

        if trace:
            self.tagCount += 1
            g.trace(
                '%3s %3s %3s %9s %7s' % (i,j,len(s),font and id(font) or '<no font>',colorName),
                '%-10s %-25s' % (tag,s[i:j]),g.callers(2))

        if tag in ('blank','tab'):
            if tag == 'tab' or colorName == 'black':
                format.setFontUnderline(True)
            if colorName != 'black':
                format.setBackground(color)
        elif underline:
            format.setForeground(color)
            format.setFontUnderline(True)
        else:
            format.setForeground(color)

        self.highlighter.setFormat (i,j-i,format)

    #@-others
#@-others
#@-leo
