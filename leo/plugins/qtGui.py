# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20110605121601.18002: * @file ../plugins/qtGui.py
#@@first

'''qt gui plugin.'''

PYTHON_COLORER = False

#@@language python
#@@tabwidth -4
#@@pagewidth 80

# Define these to suppress pylint warnings...
__timing = None # For timing stats.
__qh = None # For quick headlines.

# A switch telling whether to use qt_main.ui and qt_main.py.
useUI = False # True: use qt_main.ui. False: use DynamicWindow.createMainWindow.
newFilter = True # True use qtGui.setFilter.

#@+<< imports >>
#@+node:ekr.20110605121601.18003: **  << imports >> (qtGui.py)
import leo.core.leoGlobals as g

import leo.core.leoColor as leoColor
import leo.core.leoFrame as leoFrame
import leo.core.leoFind as leoFind
import leo.core.leoGui as leoGui
import leo.core.leoMenu as leoMenu
import leo.core.leoPlugins as leoPlugins
    # Uses leoPlugins.TryNext.

import leo.plugins.baseNativeTree as baseNativeTree

if PYTHON_COLORER:
    import leo.core.qsyntaxhighlighter as qsh

import datetime
import os
import re # For colorizer
import string
import sys
# import tempfile
import platform
import time

# if g.isPython3:
    # import urllib.request as urllib
    # import urllib.parse as urlparse
# else:
    # import urllib2 as urllib
    # import urlparse

import PyQt4.QtCore as QtCore
import PyQt4.QtGui as QtGui

try:
    from PyQt4 import Qsci
except ImportError:
    Qsci = None

try:
    import leo.plugins.nested_splitter as nested_splitter
    splitter_class = nested_splitter.NestedSplitter
    # disable special behavior, turned back on by associated plugin,
    # if the plugin's loaded
    nested_splitter.NestedSplitter.enabled = False
except ImportError:
    print('Can not import nested_splitter')
    splitter_class = QtGui.QSplitter
#@-<< imports >>
#@+<< define text widget classes >>
#@+node:ekr.20110605121601.18004: **  << define text widget classes >>
# Order matters when defining base classes.

#@+<< define LeoQTextBrowser >>
#@+node:ekr.20110605121601.18005: *3*  << define LeoQTextBrowser >>
class LeoQTextBrowser (QtGui.QTextBrowser):

    '''A subclass of QTextBrowser that overrides the mouse event handlers.'''

    #@+others
    #@+node:ekr.20110605121601.18006: *4*   ctor (LeoQTextBrowser)
    def __init__(self,parent,c,wrapper):

        for attr in ('leo_c','leo_wrapper',):
            assert not hasattr(QtGui.QTextBrowser,attr),attr

        self.leo_c = c
        self.leo_wrapper = wrapper
        self.htmlFlag = True

        QtGui.QTextBrowser.__init__(self,parent)

        # This event handler is the easy way to keep track of the vertical scroll position.
        self.leo_vsb = vsb = self.verticalScrollBar()
        vsb.connect(vsb,QtCore.SIGNAL("valueChanged(int)"),
            self.onSliderChanged)

        # g.trace('(LeoQTextBrowser)',repr(self.leo_wrapper))

        # For QCompleter
        self.leo_q_completer = None
        self.leo_options = None
        self.leo_model = None
    #@+node:ekr.20110605121601.18007: *4*  __repr__ & __str__
    def __repr__ (self):

        return '(LeoQTextBrowser) %s' % id(self)

    __str__ = __repr__
    #@+node:ekr.20110605121601.18008: *4* Auto completion (LeoQTextBrowser)
    #@+node:ekr.20110605121601.18009: *5* class LeoQListWidget(QListWidget)
    class LeoQListWidget(QtGui.QListWidget):

        #@+others
        #@+node:ekr.20110605121601.18010: *6* ctor (LeoQListWidget)
        def __init__(self,c):


            QtGui.QListWidget.__init__(self)
            self.setWindowFlags(QtCore.Qt.Popup | self.windowFlags())
            # Make this window a modal window.
            # Calling this does not fix the Ubuntu-specific modal behavior.
            # self.setWindowModality(QtCore.Qt.NonModal) # WindowModal)

            if 0:
                # embed the window in a splitter.
                splitter2 = c.frame.top.splitter_2
                splitter2.insertWidget(1,self)

            # Inject the ivars
            self.leo_w = c.frame.body.bodyCtrl.widget
                # A LeoQTextBrowser, a subclass of QtGui.QTextBrowser.
            self.leo_c = c

            # A weird hack.
            self.leo_geom_set = False # When true, self.geom returns global coords!

            self.connect(self,QtCore.SIGNAL(
                "itemClicked(QListWidgetItem *)"),self.select_callback)
        #@+node:ekr.20110605121601.18011: *6* closeEvent
        def closeEvent(self,event):

            '''Kill completion and close the window.'''

            self.leo_c.k.autoCompleter.abort()
        #@+node:ekr.20110605121601.18012: *6* end_completer
        def end_completer(self):

            # g.trace('(LeoQListWidget)')

            c = self.leo_c
            c.in_qt_dialog = False

            # This is important: it clears the autocompletion state.
            c.k.keyboardQuit()
            c.bodyWantsFocusNow()

            self.deleteLater()
        #@+node:ekr.20110605121601.18013: *6* keyPressEvent (LeoQListWidget)
        def keyPressEvent(self,event):

            '''Handle a key event from QListWidget.'''

            trace = False and not g.unitTesting
            c = self.leo_c
            w = c.frame.body.bodyCtrl
            qt = QtCore.Qt
            key = event.key()

            if event.modifiers() != qt.NoModifier and not event.text():
                # A modifier key on it's own.
                pass
            elif key in (qt.Key_Up,qt.Key_Down):
                QtGui.QListWidget.keyPressEvent(self,event)
            elif key == qt.Key_Tab:
                if trace: g.trace('<tab>')
                self.tab_callback()
            elif key in (qt.Key_Enter,qt.Key_Return):
                if trace: g.trace('<return>')
                self.select_callback()
            else:
                # Pass all other keys to the autocompleter via the event filter.
                w.ev_filter.eventFilter(obj=self,event=event)
        #@+node:ekr.20110605121601.18014: *6* select_callback
        def select_callback(self):  

            '''Called when user selects an item in the QListWidget.'''

            trace = False and not g.unitTesting
            c = self.leo_c ; w = c.frame.body

            # Replace the tail of the prefix with the completion.
            completion = self.currentItem().text()
            prefix = c.k.autoCompleter.get_autocompleter_prefix()

            parts = prefix.split('.')
            if len(parts) > 1:
                tail = parts[-1]
            else:
                tail = prefix

            if trace: g.trace('prefix',repr(prefix),'tail',repr(tail),'completion',repr(completion))

            if tail != completion:
                j = w.getInsertPoint()
                i = j - len(tail)
                w.delete(i,j)
                w.insert(i,completion)
                j = i+len(completion)
                c.setChanged(True)
                w.setInsertPoint(j)
                c.frame.body.onBodyChanged('Typing')

            self.end_completer()
        #@+node:tbrown.20111011094944.27031: *6* tab_callback
        def tab_callback(self):  

            '''Called when user hits tab on an item in the QListWidget.'''

            trace = False and not g.unitTesting
            c = self.leo_c ; w = c.frame.body
            # Replace the tail of the prefix with the completion.
            completion = self.currentItem().text()
            prefix = c.k.autoCompleter.get_autocompleter_prefix()
            parts = prefix.split('.')
            if len(parts) < 2:
                return
            # var = parts[-2]
            if len(parts) > 1:
                tail = parts[-1]
            else:
                tail = prefix
            if trace: g.trace(
                'prefix',repr(prefix),'tail',repr(tail),
                'completion',repr(completion))
            w = c.k.autoCompleter.w
            i = j = w.getInsertPoint()
            s = w.getAllText()
            while (0 <= i < len(s) and s[i] != '.'):
                i -= 1
            i += 1
            if j > i:
                w.delete(i,j)
            w.setInsertPoint(i)
            c.k.autoCompleter.klass = completion
            c.k.autoCompleter.compute_completion_list()
        #@+node:ekr.20110605121601.18015: *6* set_position (LeoQListWidget)
        def set_position (self,c):

            trace = False and not g.unitTesting
            w = self.leo_w

            def glob(obj,pt):
                '''Convert pt from obj's local coordinates to global coordinates.'''
                return obj.mapToGlobal(pt)

            vp = self.viewport()
            r = w.cursorRect()
            geom = self.geometry() # In viewport coordinates.

            gr_topLeft = glob(w,r.topLeft())

            # As a workaround to the setGeometry bug,
            # The window is destroyed instead of being hidden.
            assert not self.leo_geom_set

            # This code illustrates the bug...
            # if self.leo_geom_set:
                # # Unbelievable: geom is now in *global* coords.
                # gg_topLeft = geom.topLeft()
            # else:
                # # Per documentation, geom in local (viewport) coords.
                # gg_topLeft = glob(vp,geom.topLeft())

            gg_topLeft = glob(vp,geom.topLeft())

            delta_x = gr_topLeft.x() - gg_topLeft.x() 
            delta_y = gr_topLeft.y() - gg_topLeft.y()

            # These offset are reasonable.
            # Perhaps they should depend on font size.
            x_offset,y_offset = 10,60

            # Compute the new geometry, setting the size by hand.
            geom2_topLeft = QtCore.QPoint(
                geom.x()+delta_x+x_offset,
                geom.y()+delta_y+y_offset)

            geom2_size = QtCore.QSize(400,100)

            geom2 = QtCore.QRect(geom2_topLeft,geom2_size)

            # These assert's fail once offsets are added.
            if x_offset == 0 and y_offset == 0:
                if self.leo_geom_set:
                    assert geom2.topLeft() == glob(w,r.topLeft()),'geom.topLeft: %s, geom2.topLeft: %s' % (
                        geom2.topLeft(),glob(w,r.topLeft()))
                else:
                    assert glob(vp,geom2.topLeft()) == glob(w,r.topLeft()),'geom.topLeft: %s, geom2.topLeft: %s' % (
                        glob(vp,geom2.topLeft()),glob(w,r.topLeft()))

            self.setGeometry(geom2)
            self.leo_geom_set = True

            if trace:
                g.trace(self,
                    # '\n viewport:',vp,
                    # '\n size:    ',geom.size(),
                    '\n delta_x',delta_x,
                    '\n delta_y',delta_y,
                    '\n r:     ',r.x(),r.y(),         glob(w,r.topLeft()),
                    '\n geom:  ',geom.x(),geom.y(),   glob(vp,geom.topLeft()),
                    '\n geom2: ',geom2.x(),geom2.y(), glob(vp,geom2.topLeft()),
                )
        #@+node:ekr.20110605121601.18016: *6* show_completions
        def show_completions(self,aList):

            '''Set the QListView contents to aList.'''

            # g.trace('(qc) len(aList)',len(aList))

            self.clear()
            self.addItems(aList)
            self.setCurrentRow(0)
            self.activateWindow()
            self.setFocus()
        #@-others
    #@+node:ekr.20110605121601.18017: *5* init_completer (LeoQTextBrowser)
    def init_completer(self,options):

        '''Connect a QCompleter.'''

        trace = False and not g.unitTesting
        c = self.leo_c
        if trace:
            g.trace('(LeoQTextBrowser) len(options): %s' % (len(options)))
        self.leo_qc = qc = self.LeoQListWidget(c)
        # Move the window near the body pane's cursor.
        qc.set_position(c)
        # Show the initial completions.
        c.in_qt_dialog = True
        qc.show()
        qc.activateWindow()
        c.widgetWantsFocusNow(qc)
        qc.show_completions(options)
        return qc
    #@+node:ekr.20110605121601.18018: *5* redirections to LeoQListWidget
    def end_completer(self):

        if hasattr(self,'leo_qc'):
            self.leo_qc.end_completer()
            delattr(self,'leo_qc')

    def show_completions(self,aList):

        if hasattr(self,'leo_qc'):
            self.leo_qc.show_completions(aList)
    #@+node:ekr.20110605121601.18019: *4* leo_dumpButton
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
    #@+node:ekr.20110605121601.18020: *4* url support (LeoQTextBrowser)
    #@+node:ekr.20110605121601.18021: *5* mousePress/ReleaseEvent (LeoQTextBrowser)
    # def mousePressEvent (self,event):
        # QtGui.QTextBrowser.mousePressEvent(self,event)

    def mouseReleaseEvent(self,*args,**keys):
        # g.trace('LeoQTextBrowser')
        # self.onMouseUp(event)
        # QtGui.QTextBrowser.mouseReleaseEvent(self,event)
        
        # Call the base class method.
        # 2012/04/10: Use the same pattern for mouseReleaseEvents
        # as in other parts of Leo's core.
        if len(args) == 1:
            event = args[0]
            self.onMouseUp(event)
            QtGui.QTextBrowser.mouseReleaseEvent(event) # widget is unbound.
        elif len(args) == 2:
            event = args[1]
            QtGui.QTextBrowser.mouseReleaseEvent(*args)
        else:
            g.trace('can not happen')
            return
    #@+node:ekr.20110605121601.18022: *5* onMouseUp (LeoQTextBrowser)
    def onMouseUp(self,event=None):

        # Open the url on a control-click.
        if QtCore.Qt.ControlModifier & event.modifiers():
            event = {'c':self.leo_c}
            g.openUrlOnClick(event)
    #@+node:ekr.20111002125540.7021: *4* get/setYScrollPosition (LeoQTextBrowser)
    def getYScrollPosition(self):

        trace = (False or g.trace_scroll) and not g.unitTesting

        w = self
        sb = w.verticalScrollBar()
        pos = sb.sliderPosition()
        if trace: g.trace(pos)
        return pos

    def setYScrollPosition(self,pos):

        trace = (False or g.trace_scroll) and not g.unitTesting
        w = self

        if g.no_scroll:
            if trace: g.trace('no scroll')
            return
        elif pos is None:
            if trace: g.trace('None')
        else:
            if trace: g.trace(pos,g.callers())
            sb = w.verticalScrollBar()
            sb.setSliderPosition(pos)

    #@+node:ekr.20120925061642.13506: *4* onSliderChanged (LeoQTextBrowser)
    def onSliderChanged(self,arg):

        trace = False and not g.unitTesting
        c = self.leo_c
        p = c.p

        # Careful: changing nodes changes the scrollbars.
        if hasattr(c.frame.tree,'tree_select_lockout'):
            if c.frame.tree.tree_select_lockout:
                if trace: g.trace('locked out: c.frame.tree.tree_select_lockout')
                return

        # Only scrolling in the body pane should set v.scrollBarSpot.
        if not c.frame.body or self != c.frame.body.bodyCtrl.widget:
            if trace: g.trace('**** wrong pane')
            return

        if p:
            if trace: g.trace(arg,c.p.v.h,g.callers())
            p.v.scrollBarSpot = arg
    #@+node:tbrown.20130411145310.18855: *4* wheelEvent
    def wheelEvent(self, event):
        
        if QtCore.Qt.ControlModifier & event.modifiers():
            
            if event.delta() < 0:
                zoom_out({'c': self.leo_c})
            else:
                zoom_in({'c': self.leo_c})
            
            event.accept()
            
            return
        
        QtGui.QTextBrowser.wheelEvent(self, event)
    #@-others
#@-<< define LeoQTextBrowser >>
#@+<< define leoQtBaseTextWidget class >>
#@+node:ekr.20110605121601.18023: *3*  << define leoQtBaseTextWidget class >>
class leoQtBaseTextWidget (leoFrame.baseTextWidget):

    #@+others
    #@+node:ekr.20110605121601.18024: *4*  Birth
    #@+node:ekr.20110605121601.18025: *5* ctor (leoQtBaseTextWidget)
    def __init__ (self,widget,name='leoQtBaseTextWidget',c=None):

        self.widget = widget
        self.c = c or self.widget.leo_c

        # g.trace('leoQtBaseTextWidget',name,self.widget)

        # Init the base class.
        leoFrame.baseTextWidget.__init__(
            self,c,baseClassName='leoQtBaseTextWidget',
            name=name,widget=widget,)

        # Init ivars.
        self.changingText = False # A lockout for onTextChanged.
        self.tags = {}
        self.permanent = True # False if selecting the minibuffer will make the widget go away.
        self.configDict = {} # Keys are tags, values are colors (names or values).
        self.configUnderlineDict = {} # Keys are tags, values are True
        self.useScintilla = False # This is used!

        if not c: return # Can happen.

        if name in ('body','rendering-pane-wrapper') or name.startswith('head'):
            # g.trace('hooking up qt events',name)
            # Hook up qt events.
            if newFilter:
                g.app.gui.setFilter(c,self.widget,self,tag=name)
            else:
                self.ev_filter = leoQtEventFilter(c,w=self,tag=name)
                self.widget.installEventFilter(self.ev_filter)

        if name == 'body':
            self.widget.connect(self.widget,
                QtCore.SIGNAL("textChanged()"),self.onTextChanged)

            self.widget.connect(self.widget,
                QtCore.SIGNAL("cursorPositionChanged()"),self.onCursorPositionChanged)

        if name in ('body','log'):
            # Monkey patch the event handler.
            #@+<< define mouseReleaseEvent >>
            #@+node:ekr.20110605121601.18026: *6* << define mouseReleaseEvent >> (leoQtBaseTextWidget)
            def mouseReleaseEvent (*args,**keys):

                '''Override QLineEdit.mouseReleaseEvent.

                Simulate alt-x if we are not in an input state.'''

                trace = False and not g.unitTesting
                
                # g.trace('(leoQtBaseTextWidget)')

                # Call the base class method.
                if len(args) == 1:
                    event = args[0]
                    QtGui.QTextBrowser.mouseReleaseEvent(widget,event) # widget is unbound.
                elif len(args) == 2:
                    event = args[1]
                    QtGui.QTextBrowser.mouseReleaseEvent(*args)
                else:
                    g.trace('can not happen')
                    return

                # Open the url on a control-click.
                if QtCore.Qt.ControlModifier & event.modifiers():
                    event = {'c':c}
                    g.openUrlOnClick(event)

                if name == 'body':
                    c.p.v.insertSpot = c.frame.body.getInsertPoint()
                    if trace: g.trace(c.p.v.insertSpot)

                # 2011/05/28: Do *not* change the focus!
                # This would rip focus away from tab panes.

                # 2012/09/25: Calling k.keyboardQuit calls k.showStateColors.
                # This used to call w.setStyleSheet, which caused unwanted scroll.
                # The solution to this problem is to color border by
                # coloring the innerBodyFrame using a QPainter.
                c.k.keyboardQuit(setFocus=False)
            #@-<< define mouseReleaseEvent >>
            self.widget.mouseReleaseEvent = mouseReleaseEvent

        self.injectIvars(c)
    #@+node:ekr.20110605121601.18027: *5* injectIvars (leoQtBaseTextWidget)
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
        return w
    #@+node:ekr.20110605121601.18029: *4* signals (leoQtBaseTextWidget)
    #@+node:ekr.20110605121601.18030: *5* onCursorPositionChanged (leoQtBaseTextWidget)
    def onCursorPositionChanged(self,event=None):

        c = self.c
        name = c.widget_name(self)

        # Apparently, this does not cause problems
        # because it generates no events in the body pane.
        if name.startswith('body'):
            if hasattr(c.frame,'statusLine'):
                c.frame.statusLine.update()
    #@+node:ekr.20111114013726.9968: *4* High-level interface (leoQtBaseTextWidget)
    #@+at
    # 
    # Important: leoQtBaseTextWidget is **not** a subclass of HighLevelInterface.
    # 
    # Indeed, the redirection methods of HighLevelInterface redirect calls
    # from leoBody & leoLog to *this* class.
    # 
    # Do not delete: HighLevelInterface calls these methods.
    #@+node:ekr.20110605121601.18032: *5* Focus (leoQtBaseTextWidget)
    def getFocus(self):

        # g.trace('leoQtBody',self.widget,g.callers(4))
        return g.app.gui.get_focus(self.c) # Bug fix: 2009/6/30

    findFocus = getFocus

    # def hasFocus (self):

        # val = self.widget == g.app.gui.get_focus(self.c)
        # # g.trace('leoQtBody returns',val,self.widget,g.callers(4))
        # return val

    def setFocus (self):

        trace = False and not g.unitTesting

        if trace: print('leoQtBaseTextWidget.setFocus',
            # g.app.gui.widget_name(self.widget),
            self.widget,g.callers(3))

        # Call the base class
        assert (
            isinstance(self.widget,QtGui.QTextBrowser) or
            isinstance(self.widget,QtGui.QLineEdit) or
            isinstance(self.widget,QtGui.QTextEdit)),self.widget
        QtGui.QTextBrowser.setFocus(self.widget)
    #@+node:ekr.20110605121601.18033: *5* Indices
    #@+node:ekr.20110605121601.18034: *6* toPythonIndex (leoQtBaseTextWidget)
    def toPythonIndex (self,index):

        s = self.getAllText()
        return g.toPythonIndex(s,index)

    toGuiIndex = toPythonIndex
    #@+node:ekr.20110605121601.18049: *6* indexWarning
    # warningsDict = {}

    def indexWarning (self,s):

        return
    #@+node:ekr.20110605121601.18036: *5* Text getters/settters
    #@+node:ekr.20110605121601.18037: *6* appendText (leoQtBaseTextWidget)
    def appendText(self,s):

        s2 = self.getAllText()
        self.setAllText(s2+s)
        self.setInsertPoint(len(s2))

    #@+node:ekr.20110605121601.18040: *6* getLastPosition
    def getLastPosition(self):

        return len(self.getAllText())
    #@+node:ekr.20110605121601.18041: *6* getSelectedText (leoQtBaseTextWidget)
    def getSelectedText(self):

        # w = self.widget
        # g.trace(w,self)
        i,j = self.getSelectionRange()
        if i == j:
            return ''
        else:
            s = self.getAllText()
            # g.trace(repr(s[i:j]))
            return s[i:j]
    #@+node:ekr.20110605121601.18042: *6* get (leoQtBaseTextWidget)
    def get(self,i,j=None):
        """ Slow implementation of get() - ok for QLineEdit """
        #g.trace('Slow get', g.callers(5))

        s = self.getAllText()
        i = self.toGuiIndex(i)

        if j is None: 
            j = i+1

        j = self.toGuiIndex(j)
        return s[i:j]
    #@+node:ekr.20110605121601.18043: *6* insert (leoQtBaseTextWidget)
    def insert(self,i,s):

        s2 = self.getAllText()
        i = self.toGuiIndex(i)
        self.setAllText(s2[:i] + s + s2[i:])
        self.setInsertPoint(i+len(s))
        return i
    #@+node:ekr.20110605121601.18044: *6* selectAllText (leoQtBaseTextWidget)
    def selectAllText(self,insert=None):

        w = self.widget
        w.selectAll()
        # if insert is not None:
            # self.setInsertPoint(insert)
        # Bug fix: 2012/03/25.
        self.setSelectionRange(0,'end',insert=insert)

    #@+node:ekr.20110605121601.18045: *6* setSelectionRange & dummy helper (leoQtBaseTextWidget)
    # Note: this is used by leoQTextEditWidget.

    def setSelectionRange (self,i,j,insert=None):

        i,j = self.toGuiIndex(i),self.toGuiIndex(j)

        return self.setSelectionRangeHelper(i,j,insert)
    #@+node:ekr.20110605121601.18046: *7* setSelectionRangeHelper
    def setSelectionRangeHelper(self,i,j,insert=None):

        self.oops()
    #@+node:ekr.20110605121601.18050: *5* HighLevelInterface (leoQtBaseTextWidget)
    # Do not delete.
    # The redirection methods of HighLevelInterface redirect calls
    # from leoBody & leoLog to *this* class.

    # Essential methods...
    def getName (self):
        return self.name

    # Optional methods...
    def flashCharacter(self,i,bg='white',fg='red',flashes=3,delay=75):
        pass

    def getYScrollPosition(self):           return None # A flag
    def seeInsertPoint (self):              self.see(self.getInsertPoint())
    def setBackgroundColor(self,color):     pass
    def setEditorColors (self,bg,fg):       pass
    def setForegroundColor(self,color):     pass
    def setYScrollPosition(self,pos):       pass

    # Must be defined in subclasses.
    def getAllText(self):                       self.oops()
    def getInsertPoint(self):                   self.oops()
    def getSelectionRange(self,sort=True):      self.oops()
    def hasSelection(self):                     self.oops()
    def see(self,i):                            self.oops()
    def setAllText(self,s):                     self.oops()
    def setInsertPoint(self,i):                 self.oops()
    #@+node:ekr.20110605121601.18056: *6* tag_configure (leoQtBaseTextWidget)
    def tag_configure (self,*args,**keys):

        trace = False and not g.unitTesting
        if trace: g.trace(args,keys)

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

    tag_config = tag_configure
    #@+node:ekr.20110605121601.18052: *5* Idle time (leoQtBaseTextWidget)
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
    #@+node:ekr.20110605121601.18048: *5* onTextChanged (leoQtBaseTextWidget)
    def onTextChanged (self):

        '''Update Leo after the body has been changed.

        self.selecting is guaranteed to be True during
        the entire selection process.'''

        # Important: usually w.changingText is True.
        # This method very seldom does anything.
        trace = False and not g.unitTesting
        verbose = False
        w = self
        c = self.c ; p = c.p
        tree = c.frame.tree
        
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
            # g.error('*** unexpected non-change')
            return
        # g.trace('**',len(newText),p.h,'\n',g.callers(8))
        # oldIns  = p.v.insertSpot
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
    #@+node:ekr.20120325032957.9730: *4* rememberSelectionAndScroll (leoQtBaseTextWidget)
    def rememberSelectionAndScroll(self):

        trace = (False or g.trace_scroll) and not g.unitTesting
        w = self
        v = self.c.p.v # Always accurate.
        v.insertSpot = w.getInsertPoint()
        i,j = w.getSelectionRange()
        if i > j: i,j = j,i
        assert(i<=j)
        v.selectionStart = i
        v.selectionLength = j-i
        v.scrollBarSpot = spot = w.getYScrollPosition()
        if trace:
            g.trace(spot,v.h)
            # g.trace(id(v),id(w),i,j,ins,spot,v.h)
    #@-others
#@-<< define leoQtBaseTextWidget class >>
#@+<< define leoQLineEditWidget class >>
#@+node:ekr.20110605121601.18058: *3*  << define leoQLineEditWidget class >>
class leoQLineEditWidget (leoQtBaseTextWidget):

    #@+others
    #@+node:ekr.20110605121601.18059: *4* Birth
    #@+node:ekr.20110605121601.18060: *5* ctor (leoQLineEditWidget)
    def __init__ (self,widget,name,c=None):

        # Init the base class.
        leoQtBaseTextWidget.__init__(self,widget,name,c=c)

        self.baseClassName='leoQLineEditWidget'

        # g.trace('(leoQLineEditWidget):widget',name,widget)
    #@+node:ekr.20110605121601.18061: *5* __repr__
    def __repr__ (self):

        return '<leoQLineEditWidget: widget: %s' % (self.widget)

    __str__ = __repr__
    #@+node:ekr.20110605121601.18062: *4* Widget-specific overrides (QLineEdit)
    #@+node:ekr.20110605121601.18063: *5* getAllText
    def getAllText(self):

        w = self.widget
        s = w.text()
        return g.u(s)
    #@+node:ekr.20110605121601.18064: *5* getInsertPoint
    def getInsertPoint(self):

        i = self.widget.cursorPosition()
        # g.trace(i)
        return i
    #@+node:ekr.20110605121601.18065: *5* getSelectionRange
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
    #@+node:ekr.20110605121601.18066: *5* hasSelection
    def hasSelection(self):

        # 2011/05/26: was hasSelection.
        return self.widget.hasSelectedText()
    #@+node:ekr.20110605121601.18067: *5* see & seeInsertPoint (QLineEdit)
    def see(self,i):
        pass

    def seeInsertPoint (self):
        pass
    #@+node:ekr.20110605121601.18068: *5* setAllText leoQLineEditWidget
    def setAllText(self,s):

        w = self.widget

        disabled = hasattr(w,'leo_disabled') and w.leo_disabled
        if disabled:
            w.setEnabled(True)

        w.setText(s)

        if disabled:
            w.setEnabled(False)
    #@+node:ekr.20110605121601.18069: *5* setInsertPoint (QLineEdit)
    def setInsertPoint(self,i):

        w = self.widget
        s = w.text()
        s = g.u(s)
        i = self.toPythonIndex(i) # 2010/10/22.
        i = max(0,min(i,len(s)))
        w.setCursorPosition(i)
    #@+node:ekr.20110605121601.18070: *5* setSelectionRangeHelper (leoQLineEdit)
    def setSelectionRangeHelper(self,i,j,insert=None):

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
#@+node:ekr.20110605121601.18071: *3*  << define leoQTextEditWidget class >>
class leoQTextEditWidget (leoQtBaseTextWidget):

    #@+others
    #@+node:ekr.20110605121601.18072: *4* Birth (leoQTextEditWidget)
    #@+node:ekr.20110605121601.18073: *5* ctor (leoQTextEditWidget)
    def __init__ (self,widget,name,c=None):

        # widget is a QTextEdit (or QTextBrowser).
        # g.trace('leoQTextEditWidget',widget)

        # Init the base class.
        leoQtBaseTextWidget.__init__(self,widget,name,c=c)

        self.baseClassName='leoQTextEditWidget'

        widget.setUndoRedoEnabled(False)

        self.setConfig()
        # self.setFontFromConfig()
        # self.setColorFromConfig()
    #@+node:ekr.20110605121601.18076: *5* setConfig
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
    #@+node:ekr.20110605121601.18077: *4* leoMoveCursorHelper & helper (leoQTextEditWidget)
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
            self.pageUpDown(op, mode)
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

        # 2012/03/25.  Add this common code.
        self.seeInsertPoint()
        self.rememberSelectionAndScroll()
        self.c.frame.updateStatusLine()
    #@+node:btheado.20120129145543.8180: *5* pageUpDown
    def pageUpDown (self, op, moveMode):

        '''The QTextEdit PageUp/PageDown functionality seems to be "baked-in"
           and not externally accessible.  Since Leo has its own keyhandling
           functionality, this code emulates the QTextEdit paging.  This is
           a straight port of the C++ code found in the pageUpDown method
           of gui/widgets/qtextedit.cpp'''

        control = self.widget
        cursor = control.textCursor()
        moved = False
        lastY = control.cursorRect(cursor).top()
        distance = 0
        # move using movePosition to keep the cursor's x
        while True:
            y = control.cursorRect(cursor).top()
            distance += abs(y - lastY)
            lastY = y
            moved = cursor.movePosition(op, moveMode)
            if (not moved or distance >= control.height()):
                break
        tc = QtGui.QTextCursor
        sb = control.verticalScrollBar()
        if moved:
            if (op == tc.Up):
                cursor.movePosition(tc.Down, moveMode)
                sb.triggerAction(QtGui.QAbstractSlider.SliderPageStepSub)
            else:
                cursor.movePosition(tc.Up, moveMode)
                sb.triggerAction(QtGui.QAbstractSlider.SliderPageStepAdd)
        control.setTextCursor(cursor)
    #@+node:ekr.20110605121601.18078: *4* Widget-specific overrides (leoQTextEditWidget)
    #@+node:ekr.20110605121601.18079: *5* delete (avoid call to setAllText) (leoQTextEditWidget)
    def delete(self,i,j=None):

        trace = False and not g.unitTesting
        c,w = self.c,self.widget
        colorer = c.frame.body.colorizer.highlighter.colorer
        # n = colorer.recolorCount
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
    #@+node:ekr.20110605121601.18080: *5* flashCharacter (leoQTextEditWidget)
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
    #@+node:ekr.20110605121601.18081: *5* getAllText (leoQTextEditWidget)
    def getAllText(self):

        w = self.widget

        s = g.u(w.toPlainText())

        return s
    #@+node:ekr.20110605121601.18082: *5* getInsertPoint
    def getInsertPoint(self):

        return self.widget.textCursor().position()
    #@+node:ekr.20110605121601.18083: *5* getSelectionRange (leoQTextEditWidget)
    def getSelectionRange(self,sort=True):

        w = self.widget
        tc = w.textCursor()
        i,j = tc.selectionStart(),tc.selectionEnd()

        return i,j
    #@+node:ekr.20110605121601.18084: *5* getYScrollPosition (leoQTextEditWidget)
    def getYScrollPosition(self):

        # **Important**: There is a Qt bug here: the scrollbar position
        # is valid only if cursor is visible.  Otherwise the *reported*
        # scrollbar position will be such that the cursor *is* visible.

        trace = False and g.trace_scroll and not g.unitTesting

        w = self.widget
        sb = w.verticalScrollBar()
        pos = sb.sliderPosition()
        if trace: g.trace(pos)
        return pos
    #@+node:ekr.20110605121601.18085: *5* hasSelection (leoQTextEditWidget)
    def hasSelection(self):

        # g.trace('self widget',self.widget)

        return self.widget.textCursor().hasSelection()
    #@+node:ekr.20110605121601.18086: *5* scrolling (QTextEditWidget)
    #@+node:ekr.20110605121601.18087: *6* indexIsVisible and linesPerPage
    def linesPerPage (self):

        '''Return the number of lines presently visible.'''

        w = self.widget
        h = w.size().height()
        lineSpacing = w.fontMetrics().lineSpacing()
        n = h/lineSpacing
        return n
    #@+node:ekr.20110605121601.18088: *6* scrollDelegate (QTextEdit)
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
        # g.trace(kind,n,h,lineSpacing,delta,val,g.callers())
        vScroll.setValue(val+(delta*lineSpacing))
        c.bodyWantsFocus()
    #@+node:ekr.20110605121601.18089: *5* insert (avoid call to setAllText) (leoQTextWidget)
    def insert(self,i,s):

        c,w = self.c,self.widget
        colorer = c.frame.body.colorizer.highlighter.colorer
        # n = colorer.recolorCount
        # Set a hook for the colorer.
        colorer.initFlag = True
        i = self.toGuiIndex(i)
        cursor = w.textCursor()
        try:
            self.changingText = True # Disable onTextChanged.
            cursor.setPosition(i)
            cursor.insertText(s) # This cause an incremental call to recolor.
            w.setTextCursor(cursor) # Bug fix: 2010/01/27
        finally:
            self.changingText = False
    #@+node:ekr.20110605121601.18090: *5* see & seeInsertPoint (leoQTextEditWidget)
    def see(self,i):

        trace = g.trace_see and not g.unitTesting

        if g.no_see:
            pass
        else:
            if trace: g.trace('*****',i,g.callers())
            self.widget.ensureCursorVisible()

    def seeInsertPoint (self):

        trace = g.trace_see and not g.unitTesting

        if g.no_see:
            pass
        else:
            if trace: g.trace('*****',g.callers())
            self.widget.ensureCursorVisible()
    #@+node:ekr.20110605121601.18092: *5* setAllText (leoQTextEditWidget) & helper (changed 4.10)
    def setAllText(self,s):

        '''Set the text of the widget.

        If insert is None, the insert point, selection range and scrollbars are initied.
        Otherwise, the scrollbars are preserved.'''

        trace = False and not g.unitTesting
        c,w = self.c,self.widget
        colorizer = c.frame.body.colorizer
        highlighter = colorizer.highlighter
        colorer = highlighter.colorer
        # Set a hook for the colorer.
        colorer.initFlag = True
        if trace:
            g.trace(w)
            t1 = g.getTime()
        try:
            self.changingText = True # Disable onTextChanged.
            colorizer.changingText = True # Disable colorizer.
            w.setReadOnly(False)
            w.setPlainText(s)
        finally:
            self.changingText = False
            colorizer.changingText = False
        if trace:
            g.trace(g.timeSince(t1))
    #@+node:ekr.20110605121601.18095: *5* setInsertPoint (leoQTextEditWidget)
    def setInsertPoint(self,i):

        # Fix bug 981849: incorrect body content shown.
        # Use the more careful code in setSelectionRangeHelper & lengthHelper.
        self.setSelectionRangeHelper(i=i,j=i,insert=i)
    #@+node:ekr.20110605121601.18096: *5* setSelectionRangeHelper & helper (leoQTextEditWidget)
    def setSelectionRangeHelper(self,i,j,insert=None):

        trace = (False or g.trace_scroll) and not g.unitTesting

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

        # Remember the values for v.restoreCursorAndScroll.
        v = self.c.p.v # Always accurate.
        v.insertSpot = ins
        if i > j: i,j = j,i
        assert(i<=j)
        v.selectionStart = i
        v.selectionLength = j-i
        v.scrollBarSpot = spot = w.verticalScrollBar().value()
        if trace:
            g.trace(spot,v.h)
            # g.trace('i: %s j: %s ins: %s spot: %s %s' % (i,j,ins,spot,v.h))
    #@+node:ekr.20110605121601.18097: *6* lengthHelper
    def lengthHelper(self):

        '''Return the length of the text.'''

        w = self.widget
        tc = w.textCursor()
        tc.movePosition(QtGui.QTextCursor.End)
        n = tc.position()
        return n

    #@+node:ekr.20110605121601.18098: *5* setYScrollPosition (leoQTextEditWidget)
    def setYScrollPosition(self,pos):

        trace = (False or g.trace_scroll) and not g.unitTesting
        w = self.widget

        if g.no_scroll:
            return
        elif pos is None:
            if trace: g.trace('None')
        else:
            if trace: g.trace(pos,g.callers())
            sb = w.verticalScrollBar()
            sb.setSliderPosition(pos)
    #@+node:ekr.20110605121601.18099: *5*  PythonIndex
    #@+node:ekr.20110605121601.18100: *6* toPythonIndex (leoQTextEditWidget) (Fast)
    def toPythonIndex (self,index):

        '''This is much faster than versions using g.toPythonIndex.'''

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
            doc = te.document()
            data = index.split('.')
            if len(data) == 2:
                row,col = data
                row,col = int(row),int(col)
                bl = doc.findBlockByNumber(row-1)
                return bl.position() + col
            else:
                g.trace('bad string index: %s' % index)
                return 0

    toGuiIndex = toPythonIndex
    #@+node:ekr.20110605121601.18101: *6* toPythonIndexRowCol (leoQTextEditWidget)
    def toPythonIndexRowCol(self,index):

        w = self 

        if index == '1.0':
            return 0, 0, 0
        if index == 'end':
            index = w.getLastPosition()

        te = self.widget
        doc = te.document()
        i = w.toPythonIndex(index)
        bl = doc.findBlock(i)
        row = bl.blockNumber()
        col = i - bl.position()

        return i,row,col
    #@+node:ekr.20110605121601.18102: *5* get (leoQTextEditWidget)
    def get(self,i,j=None):

        if 1:
            # 2012/04/12: fix the following two bugs by using the vanilla code:
            # https://bugs.launchpad.net/leo-editor/+bug/979142
            # https://bugs.launchpad.net/leo-editor/+bug/971166
            s = self.getAllText()
            i = self.toGuiIndex(i)
            j = self.toGuiIndex(j)
            return s[i:j]
        else:
            # This fails when getting text from the html-encoded log panes.
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

            # This is much slower, but will have to do        

            #g.trace('Slow get()', g.callers(5))
            s = self.getAllText()
            i = self.toGuiIndex(i)
            j = self.toGuiIndex(j)
            return s[i:j]
    #@-others
#@-<< define leoQTextEditWidget class >>

# Define all other text classes, in any order.

#@+others
#@+node:ekr.20110605121601.18103: *3* class leoQScintilla
class leoQScintillaWidget (leoQtBaseTextWidget):

    #@+others
    #@+node:ekr.20110605121601.18104: *4* Birth
    #@+node:ekr.20110605121601.18105: *5* ctor (leoQScintilla)
    def __init__ (self,widget,name,c=None):

        # Init the base class.
        leoQtBaseTextWidget.__init__(self,widget,name,c=c)

        self.baseClassName='leoQScintillaWidget'

        self.useScintilla = True
        self.setConfig()
    #@+node:ekr.20110605121601.18106: *5* setConfig
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
    #@+node:ekr.20110605121601.18107: *4* Widget-specific overrides (QScintilla)
    #@+node:ekr.20110605121601.18108: *5* getAllText
    def getAllText(self):

        w = self.widget
        s = w.text()
        s = g.u(s)
        return s
    #@+node:ekr.20110605121601.18109: *5* getInsertPoint
    def getInsertPoint(self):

        w = self.widget
        s = self.getAllText()
        row,col = w.getCursorPosition()  
        i = g.convertRowColToPythonIndex(s, row, col)
        return i
    #@+node:ekr.20110605121601.18110: *5* getSelectionRange
    def getSelectionRange(self,sort=True):

        w = self.widget

        if w.hasSelectedText():
            s = self.getAllText()
            row_i,col_i,row_j,col_j = w.getSelection()
            i = g.convertRowColToPythonIndex(s, row_i, col_i)
            j = g.convertRowColToPythonIndex(s, row_j, col_j)
            if sort and i > j:
                i,j = j,i # 2013/03/02: real bug fix.
        else:
            i = j = self.getInsertPoint()
        return i,j
    #@+node:ekr.20110605121601.18111: *5* hasSelection
    def hasSelection(self):

        return self.widget.hasSelectedText()
    #@+node:ekr.20110605121601.18112: *5* see (QScintilla)
    def see(self,i):

        # Ok for now.  Using SCI_SETYCARETPOLICY might be better.
        w = self.widget
        s = self.getAllText()
        row,col = g.convertPythonIndexToRowCol(s,i)
        w.ensureLineVisible(row)

    # Use base-class method for seeInsertPoint.
    #@+node:ekr.20110605121601.18113: *5* setAllText
    def setAllText(self,s):

        '''Set the text of the widget.

        If insert is None, the insert point, selection range and scrollbars are initied.
        Otherwise, the scrollbars are preserved.'''

        w = self.widget
        w.setText(s)

    #@+node:ekr.20110605121601.18114: *5* setInsertPoint
    def setInsertPoint(self,i):

        w = self.widget
        w.SendScintilla(w.SCI_SETCURRENTPOS,i)
        w.SendScintilla(w.SCI_SETANCHOR,i)
    #@+node:ekr.20110605121601.18115: *5* setSelectionRangeHelper (QScintilla)
    def setSelectionRangeHelper(self,i,j,insert=None):

        w = self.widget

        # g.trace('i',i,'j',j,'insert',insert,g.callers(4))

        if insert in (j,None):
            self.setInsertPoint(j)
            w.SendScintilla(w.SCI_SETANCHOR,i)
        else:
            self.setInsertPoint(i)
            w.SendScintilla(w.SCI_SETANCHOR,j)
    #@-others
#@+node:ekr.20110605121601.18116: *3* class leoQtHeadlineWidget
class leoQtHeadlineWidget (leoQtBaseTextWidget):
    '''A wrapper class for QLineEdit widgets in QTreeWidget's.

    This wrapper must appear to be a leoFrame.baseTextWidget to Leo's core.
    '''

    #@+others
    #@+node:ekr.20110605121601.18117: *4* Birth (leoQtHeadlineWidget)
    def __init__ (self,c,item,name,widget):

        # g.trace('(leoQtHeadlineWidget)',item,widget)

        # Init the base class.
        leoQtBaseTextWidget.__init__(self,widget,name,c)
        self.item=item
        self.permanent = False # Warn the minibuffer that we can go away.
        self.badFocusColors = []

    def __repr__ (self):
        return 'leoQtHeadlineWidget: %s' % id(self)
    #@+node:ekr.20110605121601.18118: *4* Widget-specific overrides (leoQtHeadlineWidget)
    # These are safe versions of QLineEdit methods.
    #@+node:ekr.20110605121601.18119: *5* check
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
    #@+node:ekr.20110605121601.18120: *5* getAllText
    def getAllText(self):

        if self.check():
            w = self.widget
            s = w.text()
            return g.u(s)
        else:
            return ''
    #@+node:ekr.20110605121601.18121: *5* getInsertPoint
    def getInsertPoint(self):

        if self.check():
            i = self.widget.cursorPosition()
            return i
        else:
            return 0
    #@+node:ekr.20110605121601.18122: *5* getSelectionRange
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
    #@+node:ekr.20110605121601.18123: *5* hasSelection
    def hasSelection(self):

        if self.check():
            return self.widget.hasSelectedText()
        else:
            return False
    #@+node:ekr.20110605121601.18124: *5* see & seeInsertPoint (leoQtHeadlineWidget)
    def see(self,i):
        pass

    def seeInsertPoint (self):
        pass
    #@+node:ekr.20110605121601.18125: *5* setAllText
    def setAllText(self,s):

        if not self.check(): return

        w = self.widget
        w.setText(s)
    #@+node:ekr.20110605121601.18126: *5* setEditorColors (leoQtHeadlineWidget)
    def setEditorColors(self,bg,fg):

        obj = self.widget # A QLineEdit

        # g.trace('(leoQtHeadlineWidget)',bg,fg)

        def check(color,kind,default):
            if not QtGui.QColor(color).isValid():
                if color not in self.badFocusColors:
                    self.badFocusColors.append(color)
                    g.warning('invalid head %s color: %s' % (kind,color))
                color = default
            return color

        bg = check(bg,'background','white')
        fg = check(fg,'foreground','black')

        # if hasattr(obj,'viewport'):
            # obj = obj.viewport()

        obj.setStyleSheet('background-color:%s; color: %s' % (bg,fg))
    #@+node:ekr.20110605121601.18128: *5* setFocus
    def setFocus (self):

        if self.check():
            g.app.gui.set_focus(self.c,self.widget)
    #@+node:ekr.20110605121601.18129: *5* setInsertPoint (leoQtHeadlineWidget)
    def setInsertPoint(self,i):

        if not self.check(): return

        w = self.widget
        s = w.text()
        s = g.u(s)
        i = self.toPythonIndex(i)
        i = max(0,min(i,len(s)))
        w.setCursorPosition(i)
    #@+node:ekr.20110605121601.18130: *5* setSelectionRangeHelper (leoQLineEdit)
    def setSelectionRangeHelper(self,i,j,insert=None):

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
#@+node:ekr.20110605121601.18131: *3* class leoQtMinibuffer (leoQLineEditWidget)
class leoQtMinibuffer (leoQLineEditWidget):

    def __init__ (self,c):
        self.c = c
        w = c.frame.top.leo_ui.lineEdit # QLineEdit
        # g.trace('(leoQtMinibuffer)',w)

        # Init the base class.
        leoQLineEditWidget.__init__(self,widget=w,name='minibuffer',c=c)
        if newFilter:
            g.app.gui.setFilter(c,w,self,tag='minibuffer')
        else:
            self.ev_filter = leoQtEventFilter(c,w=self,tag='minibuffer')
            w.installEventFilter(self.ev_filter)

        # Monkey-patch the event handlers
        #@+<< define mouseReleaseEvent >>
        #@+node:ekr.20110605121601.18132: *4* << define mouseReleaseEvent >> (leoQtMinibuffer)
        def mouseReleaseEvent (*args,**keys):

            '''Override QLineEdit.mouseReleaseEvent.

            Simulate alt-x if we are not in an input state.'''
            
            # g.trace('(leoQtMinibuffer)')

            # Important: c and w must be unbound here.
            k = c.k

            # Call the base class method.
            if len(args) == 1:
                event = args[0]
                QtGui.QLineEdit.mouseReleaseEvent(w,event)

            elif len(args) == 2:
                event = args[1]
                #QtGui.QTextBrowser.mouseReleaseEvent(*args)
                QtGui.QLineEdit.mouseReleaseEvent(*args)
            else:
                g.trace('can not happen')
                return

            # g.trace('state',k.state.kind,k.state.n)
            if not k.state.kind:
                event2 = g.app.gui.create_key_event(c,
                    char='',stroke='',w=c.frame.body.bodyCtrl)
                k.fullCommand(event2)
        #@-<< define mouseReleaseEvent >>
        w.mouseReleaseEvent = mouseReleaseEvent

    # Note: can only set one stylesheet at a time.
    def setBackgroundColor(self,color):
        self.widget.setStyleSheet('background-color:%s' % color)

    def setForegroundColor(self,color):
        self.widget.setStyleSheet('color:%s' % color)

    def setBothColors(self,background_color,foreground_color):
        self.widget.setStyleSheet('background-color:%s; color: %s' % (
            background_color,foreground_color))
#@-others
#@-<< define text widget classes >>

#@+others
#@+node:ekr.20110605121601.18133: **  Module level

#@+node:ekr.20110605121601.18134: *3* init (qtGui.py top level) (qtPdb)
def init():

    trace = (False or g.trace_startup) and not g.unitTesting
    if trace and g.trace_startup: print('qtGui.__init__')

    if g.app.unitTesting: # Not Ok for unit testing!
        return False

    if not QtCore:
        return False
    
    if g.app.gui:
        return g.app.gui.guiName() == 'qt'
    else:
        g.app.gui = leoQtGui()

        # Now done in g.pdb.
        # # Override g.pdb
        # def qtPdb(message=''):
            # if message: print(message)
            # import pdb
            # if not g.app.useIpython:
                # QtCore.pyqtRemoveInputHook()
            # pdb.set_trace()
        # g.pdb = qtPdb

        g.app.gui.finishCreate()
        g.plugin_signon(__name__)
        return True
#@+node:tbrown.20130411145310.18857: *3* zoom_in/out
@g.command("zoom-in")
def zoom_in(event=None, delta=1):
    """increase body font size by one
    
    requires that @font-size-body is being used in stylesheet
    """

    c = event['c']
    c.font_size_delta += delta
    ss = g.expand_css_constants(c.active_stylesheet, c.font_size_delta)
    c.frame.body.bodyCtrl.widget.setStyleSheet(ss)
    
@g.command("zoom-out")
def zoom_out(event=None):
    """decrease body font size by one
    
    requires that @font-size-body is being used in stylesheet
    """
    zoom_in(event=event, delta=-1)
#@+node:ekr.20110605121601.18136: ** Frame and component classes...
#@+node:ekr.20110605121601.18137: *3* class  DynamicWindow (QtGui.QMainWindow)
from PyQt4 import uic

class DynamicWindow(QtGui.QMainWindow):

    '''A class representing all parts of the main Qt window.
    
    **Important**: when using tabs, the LeoTabbedTopLevel widget
    is the top-level window, **not** this QMainWindow!

    c.frame.top is a DynamicWindow object.

    For --gui==qttabs:
        c.frame.top.parent is a TabbedFrameFactory
        c.frame.top.leo_master is a LeoTabbedTopLevel

    All leoQtX classes use the ivars of this Window class to
    support operations requested by Leo's core.
    '''

    #@+others
    #@+node:ekr.20110605121601.18138: *4*  ctor (DynamicWindow)
    # Called from leoQtFrame.finishCreate.

    def __init__(self,c,parent=None):

        '''Create Leo's main window, c.frame.top'''

        # For qttabs gui, parent is a LeoTabbedTopLevel.

        # g.trace('(DynamicWindow)',g.callers())
        QtGui.QMainWindow.__init__(self,parent)
        self.leo_c = c
        self.leo_master = None # Set in construct.
        self.leo_menubar = None # Set in createMenuBar.
        self.leo_ui = None # Set in construct.
        c.font_size_delta = 0  # for adjusting font sizes dynamically
        # g.trace('(DynamicWindow)',g.listToString(dir(self),sort=True))
    #@+node:ekr.20110605121601.18140: *4* closeEvent (DynamicWindow)
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
    #@+node:ekr.20110605121601.18139: *4* construct (DynamicWindow)
    def construct(self,master=None):
        """ Factor 'heavy duty' code out from ctor """

        c = self.leo_c
        # top = c.frame.top
        self.leo_master=master # A LeoTabbedTopLevel for tabbed windows.
        # g.trace('(DynamicWindow)',g.callers())
        # Init the base class.
        ui_file_name = c.config.getString('qt_ui_file_name')
        if not ui_file_name:
            ui_file_name = 'qt_main.ui'
        ui_description_file = g.app.loadDir + "/../plugins/" + ui_file_name
        # g.pr('DynamicWindw.__init__,ui_description_file)
        assert g.os_path_exists(ui_description_file)
        self.bigTree = c.config.getBool('big_outline_pane')
        if useUI:  
            self.leo_ui = uic.loadUi(ui_description_file, self)
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
        self.leo_menubar = self.menuBar()
        self.statusBar = QtGui.QStatusBar()
        self.setStatusBar(self.statusBar)
        orientation = c.config.getString('initial_split_orientation')
        self.setSplitDirection(orientation)
        self.setStyleSheets()
        
        # self.setLeoWindowIcon()
    #@+node:ekr.20110605121601.18141: *4* createMainWindow & helpers
    # Called instead of uic.loadUi(ui_description_file, self)

    def createMainWindow (self):

        '''Create the component ivars of the main window.

        Copied/adapted from qt_main.py'''

        MainWindow = self
        self.leo_ui = self

        self.setMainWindowOptions()
        self.createCentralWidget()
        self.createMainLayout(self.centralwidget)
            # Creates .verticalLayout, .splitter and .splitter_2.
        # g.trace(self.bigTree)
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
    #@+node:ekr.20110605121601.18142: *5* top-level
    #@+node:ekr.20110605121601.18143: *6* createBodyPane
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
    #@+node:ekr.20110605121601.18144: *6* createCentralWidget
    def createCentralWidget (self):

        MainWindow = self

        w = QtGui.QWidget(MainWindow)
        w.setObjectName("centralwidget")

        MainWindow.setCentralWidget(w)

        # Official ivars.
        self.centralwidget = w
    #@+node:ekr.20110605121601.18145: *6* createLogPane
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

        # 2011/10/01: Embed the Find tab in a QScrollArea.
        findScrollArea = QtGui.QScrollArea()
        findScrollArea.setObjectName('findScrollArea')
        findTab = QtGui.QWidget()
        findTab.setObjectName('findTab')
        tabWidget.addTab(findScrollArea,'Find')
        self.createFindTab(findTab,findScrollArea)
        findScrollArea.setWidget(findTab)

        spellTab = QtGui.QWidget()
        spellTab.setObjectName('spellTab')
        tabWidget.addTab(spellTab,'Spell')
        self.createSpellTab(spellTab)

        tabWidget.setCurrentIndex(1)

        # Official ivars
        self.tabWidget = tabWidget # Used by leoQtLog.
    #@+node:ekr.20110605121601.18146: *6* createMainLayout (DynamicWindow)
    def createMainLayout (self,parent):

        # c = self.leo_c
        vLayout = self.createVLayout(parent,'mainVLayout',margin=3)
        # Splitter two is the "main" splitter, containing splitter.
        splitter2 = splitter_class(parent)
        splitter2.setOrientation(QtCore.Qt.Vertical)
        splitter2.setObjectName("splitter_2")
        splitter2.connect(splitter2,
            QtCore.SIGNAL("splitterMoved(int,int)"),
            self.onSplitter2Moved)
        splitter = splitter_class(splitter2)
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
    #@+node:ekr.20110605121601.18147: *6* createMenuBar (DynamicWindow)
    def createMenuBar (self):

        MainWindow = self
        w = QtGui.QMenuBar(MainWindow)
        w.setGeometry(QtCore.QRect(0, 0, 957, 22))
        w.setObjectName("menubar")
        MainWindow.setMenuBar(w)
        # Official ivars.
        self.leo_menubar = w
    #@+node:ekr.20110605121601.18148: *6* createMiniBuffer
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
    #@+node:ekr.20110605121601.18149: *6* createOutlinePane
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

        return treeFrame
    #@+node:ekr.20110605121601.18150: *6* createStatusBar
    def createStatusBar (self,parent):

        w = QtGui.QStatusBar(parent)
        w.setObjectName("statusbar")
        parent.setStatusBar(w)

        # Official ivars.
        self.statusBar = w
    #@+node:ekr.20110605121601.18151: *6* setMainWindowOptions
    def setMainWindowOptions (self):

        MainWindow = self

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(691, 635)
        MainWindow.setDockNestingEnabled(False)
        MainWindow.setDockOptions(
            QtGui.QMainWindow.AllowTabbedDocks |
            QtGui.QMainWindow.AnimatedDocks)
    #@+node:ekr.20110605121601.18152: *5* widgets (DynamicWindow)
    #@+node:ekr.20110605121601.18153: *6* createButton
    def createButton (self,parent,name,label):

        w = QtGui.QPushButton(parent)
        w.setObjectName(name)
        w.setText(self.tr(label))
        return w
    #@+node:ekr.20110605121601.18154: *6* createCheckBox
    def createCheckBox (self,parent,name,label):

        w = QtGui.QCheckBox(parent)
        self.setName(w,name)
        w.setText(self.tr(label))
        return w
    #@+node:ekr.20110605121601.18155: *6* createFrame
    def createFrame (self,parent,name,
        hPolicy=None,vPolicy=None,
        lineWidth = 1,
        shadow = QtGui.QFrame.Plain,
        shape = QtGui.QFrame.NoFrame,
    ):

        if name == 'innerBodyFrame':
            class InnerBodyFrame(QtGui.QFrame):
                def paintEvent(self,event):
                    # A kludge.  g.app.gui.innerBodyFrameColor is set by paint_qframe.
                    if hasattr(g.app.gui,'innerBodyFrameColor'):
                        color = g.app.gui.innerBodyFrameColor
                        painter = QtGui.QPainter()
                        painter.begin(w)
                        painter.fillRect(w.rect(),QtGui.QColor(color))
                        painter.end()
            w = InnerBodyFrame(parent)
        else:
            w = QtGui.QFrame(parent)
        self.setSizePolicy(w,kind1=hPolicy,kind2=vPolicy)
        w.setFrameShape(shape)
        w.setFrameShadow(shadow)
        w.setLineWidth(lineWidth)
        self.setName(w,name)
        return w
    #@+node:ekr.20110605121601.18156: *6* createGrid (DynamicWindow)
    def createGrid (self,parent,name,margin=0,spacing=0):

        w = QtGui.QGridLayout(parent)
        w.setMargin(margin)
        w.setSpacing(spacing)
        self.setName(w,name)
        return w
    #@+node:ekr.20110605121601.18157: *6* createHLayout & createVLayout
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
    #@+node:ekr.20110605121601.18158: *6* createLabel
    def createLabel (self,parent,name,label):

        w = QtGui.QLabel(parent)
        self.setName(w,name)
        w.setText(self.tr(label))
        return w
    #@+node:ekr.20110605121601.18159: *6* createLineEdit
    def createLineEdit (self,parent,name,disabled=True):

        w = QtGui.QLineEdit(parent)
        w.setObjectName(name)
        w.leo_disabled = disabled # Inject the ivar.

        # g.trace(disabled,w,g.callers())
        return w
    #@+node:ekr.20110605121601.18160: *6* createRadioButton
    def createRadioButton (self,parent,name,label):

        w = QtGui.QRadioButton(parent)
        self.setName(w,name)
        w.setText(self.tr(label))
        return w
    #@+node:ekr.20110605121601.18161: *6* createStackedWidget
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
    #@+node:ekr.20110605121601.18162: *6* createTabWidget
    def createTabWidget (self,parent,name,hPolicy=None,vPolicy=None):

        w = QtGui.QTabWidget(parent)
        self.setSizePolicy(w,kind1=hPolicy,kind2=vPolicy)
        self.setName(w,name)
        return w
    #@+node:ekr.20110605121601.18163: *6* createText (DynamicWindow)
    def createText (self,parent,name,
        # hPolicy=None,vPolicy=None,
        lineWidth = 0,
        shadow = QtGui.QFrame.Plain,
        shape = QtGui.QFrame.NoFrame,
    ):

        # w = QtGui.QTextBrowser(parent)
        c = self.leo_c
        w = LeoQTextBrowser(parent,c,None)
        # self.setSizePolicy(w,kind1=hPolicy,kind2=vPolicy)
        w.setFrameShape(shape)
        w.setFrameShadow(shadow)
        w.setLineWidth(lineWidth)
        self.setName(w,name)
        return w
    #@+node:ekr.20110605121601.18164: *6* createTreeWidget (DynamicWindow)
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
    #@+node:ekr.20110605121601.18165: *5* log tabs (DynamicWindow)
    #@+node:ekr.20110605121601.18167: *6* createSpellTab (DynamicWindow)
    def createSpellTab (self,parent):

        # MainWindow = self
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
        self.leo_spell_widget = parent # 2013/09/20: To allow bindings to be set.
        self.leo_spell_listBox = listBox # Must exist
        self.leo_spell_label = lab # Must exist (!!)
    #@+node:ekr.20110605121601.18166: *6* createFindTab (DynamicWindow)
    def createFindTab (self,parent,tab_widget):

        c,dw = self.leo_c,self
        grid = self.createGrid(parent,'findGrid',margin=10,spacing=10)
        grid.setColumnStretch(0,100)
        grid.setColumnStretch(1,100)
        grid.setColumnStretch(2,10)
        grid.setColumnMinimumWidth(1,75)
        grid.setColumnMinimumWidth(2,175)
        grid.setColumnMinimumWidth(3,50)
        # Aliases for column numbers
        col_0,col_1,col_2 = 0,1,2
        span_1,span_2,span_3 = 1,2,3
        # Row 0: heading.
        heading_row = 0
        lab1 = self.createLabel(parent,'findHeading','Find/Change Settings...')
        grid.addWidget(lab1,heading_row,col_0,span_1,span_2,QtCore.Qt.AlignLeft) # AlignHCenter
        # Rows 1,2: the find/change boxes, now disabled.
        find_row = 1
        change_row = 2
        findPattern = self.createLineEdit(parent,'findPattern',disabled=True)
        findChange  = self.createLineEdit(parent,'findChange',disabled=True)
        lab2 = self.createLabel(parent,'findLabel','Find:')
        lab3 = self.createLabel(parent,'changeLabel','Change:')
        grid.addWidget(lab2,find_row,col_0)
        grid.addWidget(lab3,change_row,col_0)
        grid.addWidget(findPattern,find_row,col_1,span_1,span_2)
        grid.addWidget(findChange,change_row,col_1,span_1,span_2)
        # Check boxes and radio buttons.
        # Radio buttons are mutually exclusive because they have the same parent.
        def mungeName(name):
            # The value returned here is significant: it creates an ivar.
            return 'checkBox%s' % label.replace(' ','').replace('&','')
        # Rows 3 through 8...
        base_row = 3
        table = (
            ('box', 'Whole &Word',      0,0),
            ('rb',  '&Entire Outline',  0,1),
            ('box', '&Ignore Case',     1,0),
            ('rb',  '&Suboutline Only', 1,1),
            ('box', 'Wrap &Around',     2,0),
            ('rb',  '&Node Only',       2,1),
            ('box', 'Search &Headline', 3,1),
            ('box', 'Rege&xp',          3,0),
            ('box', 'Search &Body',     4,1),
            ('box', 'Mark &Finds',      4,0),
            ('box', 'Mark &Changes',    5,0))
            # a,b,c,e,f,h,i,n,rs,w
        for kind,label,row,col in table:
            name = mungeName(label)
            func = g.choose(kind=='box',
                self.createCheckBox,self.createRadioButton)
            w = func(parent,name,label)
            grid.addWidget(w,row+base_row,col)
            setattr(self,name,w)
        # Row 9: help row.
        help_row = 9
        w = self.createLabel(parent,'findHelp','For help: <alt-x>help-for-find-commands<return>')
        grid.addWidget(w,help_row,col_0,span_1,span_3)
        # Row 10: Widgets that take all additional vertical space.
        w = QtGui.QWidget()
        space_row = 10
        grid.addWidget(w,space_row,col_0)
        grid.addWidget(w,space_row,col_1)
        grid.addWidget(w,space_row,col_2)
        grid.setRowStretch(space_row,100)
        # Official ivars (in addition to setattr ivars).
        self.leo_find_widget = tab_widget # 2011/11/21: a scrollArea.
        self.findPattern = findPattern
        self.findChange = findChange
        # self.findLab = lab2
        # self.changeLab = lab3
    #@+node:ekr.20110605121601.18168: *5* utils
    #@+node:ekr.20110605121601.18169: *6* setName
    def setName (self,widget,name):

        if name:
            # if not name.startswith('leo_'):
                # name = 'leo_' + name
            widget.setObjectName(name)
    #@+node:ekr.20110605121601.18170: *6* setSizePolicy
    def setSizePolicy (self,widget,kind1=None,kind2=None):

        if kind1 is None: kind1 = QtGui.QSizePolicy.Ignored
        if kind2 is None: kind2 = QtGui.QSizePolicy.Ignored

        sizePolicy = QtGui.QSizePolicy(kind1,kind2)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)

        sizePolicy.setHeightForWidth(
            widget.sizePolicy().hasHeightForWidth())

        widget.setSizePolicy(sizePolicy)
    #@+node:ekr.20110605121601.18171: *6* tr
    def tr(self,s):

        return QtGui.QApplication.translate(
            'MainWindow',s,None,QtGui.QApplication.UnicodeUTF8)
    #@+node:ekr.20110605121601.18172: *4* do_leo_spell_btn_*
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
    #@+node:ekr.20110605121601.18173: *4* select (DynamicWindow)
    def select (self,c):

        '''Select the window or tab for c.'''

        # self is c.frame.top
        if self.leo_master:
            # A LeoTabbedTopLevel.
            self.leo_master.select(c)
        else:
            w = c.frame.body.bodyCtrl
            g.app.gui.set_focus(c,w)

    #@+node:ekr.20110605121601.18178: *4* setGeometry (DynamicWindow)
    def setGeometry (self,rect):

        '''Set the window geometry, but only once when using the qttabs gui.'''

        # g.trace('(DynamicWindow)',rect,g.callers())

        if g.app.qt_use_tabs:
            m = self.leo_master
            assert self.leo_master

            # Only set the geometry once, even for new files.
            if not hasattr(m,'leo_geom_inited'):
                m.leo_geom_inited = True
                self.leo_master.setGeometry(rect)
                QtGui.QMainWindow.setGeometry(self,rect)
        else:
            QtGui.QMainWindow.setGeometry(self,rect)
    #@+node:ekr.20110605121601.18177: *4* setLeoWindowIcon
    def setLeoWindowIcon(self):
        """ Set icon visible in title bar and task bar """
        # xxx do not use 
        self.setWindowIcon(QtGui.QIcon(g.app.leoDir + "/Icons/leoapp32.png"))
    #@+node:ekr.20110605121601.18174: *4* setSplitDirection (DynamicWindow)
    def setSplitDirection (self,orientation='vertical'):

        vert = orientation and orientation.lower().startswith('v')
        h,v = QtCore.Qt.Horizontal,QtCore.Qt.Vertical

        orientation1 = g.choose(vert,h,v)
        orientation2 = g.choose(vert,v,h)

        self.splitter.setOrientation(orientation1)
        self.splitter_2.setOrientation(orientation2)

        # g.trace('vert',vert)

    #@+node:ekr.20110605121601.18175: *4* setStyleSheets & helper (DynamicWindow)
    styleSheet_inited = False

    def setStyleSheets(self):

        trace = False
        c = self.leo_c

        sheet = c.config.getData('qt-gui-plugin-style-sheet')
        if sheet:
            if '\n' in sheet[0]:
                sheet = ''.join(sheet)
            else:
                sheet = '\n'.join(sheet)
            
            # store *before* expanding, so later expansions get new zoom
            c.active_stylesheet = sheet
            
            sheet = g.expand_css_constants(sheet, c.font_size_delta)
            
            if trace: g.trace(len(sheet))
            w = self.leo_ui
            if g.app.qt_use_tabs:
                w = g.app.gui.frameFactory.masterFrame
            a = w.setStyleSheet(sheet or self.default_sheet())
        else:
            if trace: g.trace('no style sheet')
    #@+node:ekr.20110605121601.18176: *5* defaultStyleSheet
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
    #@+node:ekr.20130804061744.12425: *4* setWindowTitle (DynamicWindow)
    if 0: # Override for debugging only.
        def setWindowTitle (self,s):
            g.trace('***(DynamicWindow)',s,self.parent())
            # Call the base class method.
            QtGui.QMainWindow.setWindowTitle(self,s)
    #@+node:ekr.20110605121601.18179: *4* splitter event handlers
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

#@+node:ekr.20110605121601.18180: *3* class leoQtBody (subclass of leoBody)
class leoQtBody (leoFrame.leoBody):

    """A class that represents the body pane of a Qt window."""

    # pylint: disable=R0923
    # R0923:leoQtBody: Interface not implemented

    #@+others
    #@+node:ekr.20110605121601.18181: *4*  Birth
    #@+node:ekr.20110605121601.18182: *5*  ctor (qtBody)
    def __init__ (self,frame,parentFrame):

        trace = False and not g.unitTesting
        # Call the base class constructor.
        leoFrame.leoBody.__init__(self,frame,parentFrame)
        c = self.c
        assert c.frame == frame and frame.c == c
        self.useScintilla = c.config.getBool('qt-use-scintilla')
        self.unselectedBackgroundColor = c.config.getColor(
            # 'unselected-background-color')
            'unselected_body_bg_color')
        # 2011/03/14
        self.unselectedForegroundColor = c.config.getColor(
            'unselected_body_fg_color')
        # Set the actual gui widget.
        if self.useScintilla:
            self.widget = w = leoQScintillaWidget(
                c.frame.top.textEdit,
                name='body',c=c)
            self.bodyCtrl = w # The widget as seen from Leo's core.
            self.colorizer = leoFrame.nullColorizer(c) # 2011/02/07
        else:
            top = c.frame.top
            sw = top.leo_ui.stackedWidget
            qtWidget = top.leo_ui.richTextEdit # A LeoQTextBrowser
            sw.setCurrentIndex(1)
            self.widget = w = leoQTextEditWidget(qtWidget,name='body',c=c)
                # Sets w.widget = qtWidget.
            self.bodyCtrl = w # The widget as seen from Leo's core.
            # Hook up the QSyntaxHighlighter
            self.colorizer = leoQtColorizer(c,w.widget)
            qtWidget.setAcceptRichText(False)
            if 0: # xxx test: disable foreground color change for selected text.
                palette = qtWidget.palette()
                highlight_foreground_brush = palette.brush(palette.Active,palette.HighlightedText) # white.
                highlight_background_brush = palette.brush(palette.Active,palette.Highlight) # dark blue
                # normal_brush = palette.brush(palette.Active,palette.Text)
                g.trace('foreground',highlight_foreground_brush.color().name())
                g.trace('background',highlight_background_brush.color().name())
                highlight_foreground_brush.setColor(QtGui.QColor('red'))
                g.trace('foreground',highlight_foreground_brush.color().name())
                palette.setBrush(palette.HighlightedText,highlight_foreground_brush)
        # Config stuff.
        self.trace_onBodyChanged = c.config.getBool('trace_onBodyChanged')
        self.setWrap(c.p)
        # For multiple body editors.
        self.editor_name = None
        self.editor_v = None
        self.numberOfEditors = 1
        self.totalNumberOfEditors = 1
        # For renderer panes.
        self.canvasRenderer = None
        self.canvasRendererLabel = None
        self.canvasRendererVisible = False
        self.textRenderer = None
        self.textRendererLabel = None
        self.textRendererVisible = False
        self.textRendererWrapper = None
        if trace: g.trace('(qtBody)',self.widget)
    #@+node:ekr.20110605121601.18183: *6* setWrap (qtBody)
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

        # g.trace(wrap,w.verticalScrollBar())

        option,qt = QtGui.QTextOption,QtCore.Qt
        w.setHorizontalScrollBarPolicy(qt.ScrollBarAlwaysOff if wrap else qt.ScrollBarAsNeeded)
        w.setWordWrapMode(option.WordWrap if wrap else option.NoWrap)
    #@+node:ekr.20110605121601.18185: *6* get_name
    def getName (self):

        return 'body-widget'
    #@+node:ekr.20110605121601.18187: *4* setEditorColors (qtBody)
    def setEditorColors (self,bg,fg):
        
        if 0: # handled by stylesheet
            trace = False and not g.unitTesting
            c = self.c
            if c.use_focus_border:
                return
            # Deprecated.  This can cause unwanted scrolling.
            obj = self.bodyCtrl.widget # A QTextEditor or QTextBrowser.
            class_name = obj.__class__.__name__
            if  class_name != 'LeoQTextBrowser':
                if trace: g.trace('unexpected object',obj)
                return
            def check(color,kind,default):
                if color in ('none','None',None):
                    return default
                if QtGui.QColor(color).isValid():
                    return color
                if color not in self.badFocusColors:
                    self.badFocusColors.append(color)
                    g.warning('invalid body %s color: %s' % (kind,color))
                return default
            bg = check(bg,'background','white')
            fg = check(fg,'foreground','black')
            if trace: g.trace(bg,fg,obj)
            # Set the stylesheet only for the QTextBrowser itself,
            # *not* the other child widgets:
            # See: http://stackoverflow.com/questions/9554435/qtextedit-background-color-change-also-the-color-of-scrollbar
            sheet = 'background-color: %s; color: %s' % (bg,fg)
            g.app.gui.update_style_sheet(obj,'colors',sheet,selector='LeoQTextBrowser')
    #@+node:ekr.20110605121601.18190: *4* oops (qtBody)
    def oops (self):
        g.trace('qtBody',g.callers(3))
    #@+node:ekr.20110605121601.18191: *4* High-level interface (qtBody)
    # The required high-level interface.
    def appendText (self,s):                return self.widget.appendText(s)
    def clipboard_append(self,s):           return self.widget.clipboard_append(s)
    def clipboard_clear(self):              return self.widget.clipboard_append()
    def delete(self,i,j=None):              self.widget.delete(i,j)
    def deleteTextSelection (self):         return self.widget.deleteTextSelection()
    def flashCharacter(self,i,
        bg='white',fg='red',
        flashes=3,delay=75):                return self.widget(i,bg,fg,flashes,delay)
    def get(self,i,j=None):                 return self.widget.get(i,j)
    def getAllText (self):                  return self.widget.getAllText()
    def getFocus (self):                    return self.widget.getFocus()
    def getInsertPoint(self):               return self.widget.getInsertPoint()
    def getSelectedText (self):             return self.widget.getSelectedText()
    def getSelectionRange(self):            return self.widget.getSelectionRange()
    def getYScrollPosition (self):          return self.widget.getYScrollPosition()
    def hasSelection (self):                return self.widget.hasSelection()
    def insert(self,i,s):                   return self.widget.insert(i,s)
    def replace (self,i,j,s):               self.widget.replace (i,j,s)
    def rowColToGuiIndex (self,s,row,col):  return self.widget.rowColToGuiIndex(s,row,col)
    def see(self,index):                    return self.widget.see(index)
    def seeInsertPoint(self):               return self.widget.seeInsertPoint()
    def selectAllText (self,insert=None):   self.widget.selectAllText(insert)
    # def setAllText (self,s,new_p=None):     return self.widget.setAllText(s,new_p=new_p)
    def setAllText(self,s):                 return self.widget.setAllText(s)
    def setBackgroundColor (self,color):    return self.widget.setBackgroundColor(color)
    def setFocus (self):                    return self.widget.setFocus()
    def setForegroundColor (self,color):    return self.widget.setForegroundColor(color)
    def setInsertPoint (self,pos):          return self.widget.setInsertPoint(pos)
    def setSelectionRange (self,i,j,insert=None):
        self.widget.setSelectionRange(i,j,insert=insert)
    def setYScrollPosition (self,i):        return self.widget.setYScrollPosition(i)
    def tag_configure(self,colorName,**keys):pass
    def toPythonIndex(self,index):          return self.widget.toPythonIndex(index)
    def toPythonIndexRowCol(self,index):    return self.widget.toPythonIndexRowCol(index)

    set_focus = setFocus
    toGuiIndex = toPythonIndex
    #@+node:ekr.20110605121601.18192: *4* hasFocus (qtBody)
    # def hasFocus(self):

        # '''Return True if the body has focus.'''

        # # Always returning True is good enough for leoMenu.updateEditMenu.
        # return True

        # # Doesn't work: the focus is already in the menu!
        # # w = g.app.gui.get_focus()
        # # g.trace(w,self.widget.widget)
        # # return w == self.widget.widget
    #@+node:ekr.20110605121601.18193: *4* Editors (qtBody)
    #@+node:ekr.20110605121601.18194: *5* entries
    #@+node:ekr.20110605121601.18195: *6* addEditor & helper (qtBody)
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
        c.bodyWantsFocus()
    #@+node:ekr.20110605121601.18196: *7* createEditor (qtBody)
    def createEditor (self,name):

        c = self.c ; p = c.p
        f = c.frame.top.leo_ui.leo_body_inner_frame
            # Valid regardless of qtGui.useUI
        # Step 1: create the editor.
        # w = QtGui.QTextBrowser(f)
        w = LeoQTextBrowser(f,c,self)
        w.setObjectName('richTextEdit') # Will be changed later.
        wrapper = leoQTextEditWidget(w,name='body',c=c)
        self.packLabel(w)
        # Step 2: inject ivars, set bindings, etc.
        self.injectIvars(f,name,p,wrapper)
        self.updateInjectedIvars(w,p)
        wrapper.setAllText(p.b)
        wrapper.see(0)
        # self.createBindings(w=wrapper)
        c.k.completeAllBindingsForWidget(wrapper)
        self.recolorWidget(p,wrapper)
        return f,wrapper
    #@+node:ekr.20110605121601.18197: *6* assignPositionToEditor (qtBody)
    def assignPositionToEditor (self,p):

        '''Called *only* from tree.select to select the present body editor.'''

        c = self.c
        wrapper = c.frame.body.bodyCtrl
        w = wrapper.widget
        self.updateInjectedIvars(w,p)
        self.selectLabel(wrapper)
        # g.trace('===',id(w),w.leo_chapter,w.leo_p.h)
    #@+node:ekr.20110605121601.18198: *6* cycleEditorFocus (qtBody)
    # Use the base class method.

    # def cycleEditorFocus (self,event=None):

        # '''Cycle keyboard focus between the body text editors.'''

        # c = self.c ; d = self.editorWidgets
        # w = c.frame.body.bodyCtrl
        # values = list(d.values())
        # if len(values) > 1:
            # i = values.index(w) + 1
            # if i == len(values): i = 0
            # w2 = list(d.values())[i]
            # assert(w!=w2)
            # self.selectEditor(w2)
            # c.frame.body.bodyCtrl = w2

    #@+node:ekr.20110605121601.18199: *6* deleteEditor (qtBody)
    def deleteEditor (self,event=None):

        '''Delete the presently selected body text editor.'''

        trace = False and not g.unitTesting
        c = self.c ; d = self.editorWidgets
        wrapper = c.frame.body.bodyCtrl
        w = wrapper.widget
        # This seems not to be a valid assertion.
        # assert wrapper == d.get(name),'wrong wrapper'
        assert isinstance(wrapper,leoQTextEditWidget),wrapper
        assert isinstance(w,QtGui.QTextEdit),w
        name = w.leo_name
        assert name

        if len(list(d.keys())) <= 1: return

        # At present, can not delete the first column.
        if name == '1':
            g.warning('can not delete leftmost editor')
            return

        # Actually delete the widget.
        if trace: g.trace('**delete name %s id(wrapper) %s id(w) %s' % (
            name,id(wrapper),id(w)))

        del d [name]
        f = c.frame.top.leo_ui.leo_body_inner_frame
        layout = f.layout()
        for z in (w,w.leo_label):
            if z: # 2011/11/12
                self.unpackWidget(layout,z)
        w.leo_label = None # 2011/11/12

        # Select another editor.
        new_wrapper = list(d.values())[0]
        if trace: g.trace(wrapper,new_wrapper)
        self.numberOfEditors -= 1
        if self.numberOfEditors == 1:
            w = new_wrapper.widget
            if w.leo_label: # 2011/11/12
                self.unpackWidget(layout,w.leo_label)
                w.leo_label = None # 2011/11/12

        self.selectEditor(new_wrapper)
    #@+node:ekr.20110605121601.18200: *6* findEditorForChapter (qtBody)
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
    #@+node:ekr.20110605121601.18201: *6* select/unselectLabel (qtBody)
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
    #@+node:ekr.20110605121601.18202: *6* selectEditor & helpers
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
        # g.trace('widget',w)
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
                c.bodyWantsFocus()
            elif trace and verbose: report('no change')
            return

        try:
            val = None
            self.selectEditorLockout = True
            val = self.selectEditorHelper(wrapper)
        finally:
            self.selectEditorLockout = False

        return val # Don't put a return in a finally clause.
    #@+node:ekr.20110605121601.18203: *7* selectEditorHelper (qtBody)
    def selectEditorHelper (self,wrapper):

        trace = False and not g.unitTesting
        c = self.c
        assert isinstance(wrapper,leoQTextEditWidget),wrapper
        w = wrapper.widget
        assert isinstance(w,QtGui.QTextEdit),w
        if not w.leo_p:
            g.trace('no w.leo_p') 
            return 'break'
        # The actual switch.
        self.deactivateEditors(wrapper)
        self.recolorWidget (w.leo_p,wrapper) # switches colorizers.
        # g.trace('c.frame.body',c.frame.body)
        # g.trace('c.frame.body.bodyCtrl',c.frame.body.bodyCtrl)
        # g.trace('wrapper',wrapper)
        c.frame.body.bodyCtrl = wrapper
        c.frame.body.widget = wrapper # Major bug fix: 2011/04/06
        w.leo_active = True
        self.switchToChapter(wrapper)
        self.selectLabel(wrapper)
        if not self.ensurePositionExists(w):
            return g.trace('***** no position editor!')
        if not (hasattr(w,'leo_p') and w.leo_p):
            return g.trace('***** no w.leo_p',w)
        p = w.leo_p
        assert p,p
        if trace: g.trace('wrapper %s old %s p %s' % (
            id(wrapper),c.p.h,p.h))
        c.expandAllAncestors(p)
        c.selectPosition(p)
            # Calls assignPositionToEditor.
            # Calls p.v.restoreCursorAndScroll.
        c.redraw()
        c.recolor_now()
        c.bodyWantsFocus()
    #@+node:ekr.20110605121601.18205: *6* updateEditors (qtBody)
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

        c.bodyWantsFocus()
        w0.setSelectionRange(i,j,insert=ins)
            # 2011/11/21: bug fix: was ins=ins
        # g.trace(pos0)
        sb0.setSliderPosition(pos0)
    #@+node:ekr.20110605121601.18206: *5* utils
    #@+node:ekr.20110605121601.18207: *6* computeLabel (qtBody)
    def computeLabel (self,w):

        if hasattr(w,'leo_label') and w.leo_label: # 2011/11/12
            s = w.leo_label.text()
        else:
            s = ''

        if hasattr(w,'leo_chapter') and w.leo_chapter:
            s = '%s: %s' % (w.leo_chapter,s)

        return s
    #@+node:ekr.20110605121601.18208: *6* createChapterIvar (qtBody)
    def createChapterIvar (self,w):

        c = self.c ; cc = c.chapterController

        if hasattr(w,'leo_chapter') and w.leo_chapter:
            pass
        elif cc and self.use_chapters:
            w.leo_chapter = cc.getSelectedChapter()
        else:
            w.leo_chapter = None
    #@+node:ekr.20110605121601.18209: *6* deactivateEditors (qtBody)
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
                if trace: g.trace(w2)
                self.onFocusOut(w2)
    #@+node:ekr.20110605121601.18210: *6* ensurePositionExists (qtBody)
    def ensurePositionExists(self,w):

        '''Return True if w.leo_p exists or can be reconstituted.'''

        trace = False and not g.unitTesting
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
                w.leo_p = c.p.copy()
                return False
    #@+node:ekr.20110605121601.18211: *6* injectIvars (qtBody)
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
        # w.leo_label = None # Injected by packLabel.
        w.leo_name = name
        w.leo_wrapper = wrapper
    #@+node:ekr.20110605121601.18212: *6* packLabel (qtBody)
    def packLabel (self,w,n=None):

        trace = False and not g.unitTesting
        c = self.c
        f = c.frame.top.leo_ui.leo_body_inner_frame
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
        if trace: g.trace('w.leo_label',w,lab)
    #@+node:ekr.20110605121601.18213: *6* recolorWidget (qtBody)
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
    #@+node:ekr.20110605121601.18214: *6* switchToChapter (qtBody)
    def switchToChapter (self,w):

        '''select w.leo_chapter.'''

        trace = False and not g.unitTesting
        c = self.c ; cc = c.chapterController

        if hasattr(w,'leo_chapter') and w.leo_chapter:
            chapter = w.leo_chapter
            name = chapter and chapter.name
            oldChapter = cc.getSelectedChapter()
            if chapter != oldChapter:
                if trace: g.trace('***old',oldChapter.name,'new',name,w.leo_p)
                cc.selectChapterByName(name)
                c.bodyWantsFocus()
    #@+node:ekr.20110605121601.18215: *6* updateInjectedIvars (qtBody)
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
    #@+node:ekr.20110605121601.18216: *6* unpackWidget (qtBody)
    def unpackWidget (self,layout,w):

        trace = False and not g.unitTesting

        if trace: g.trace(w)

        index = layout.indexOf(w)
        item = layout.itemAt(index)
        item.setGeometry(QtCore.QRect(0,0,0,0))
        layout.removeItem(item)


    #@+node:ekr.20110605121601.18217: *4* Renderer panes (qtBody)
    #@+node:ekr.20110605121601.18218: *5* hideCanvasRenderer (qtBody)
    def hideCanvasRenderer (self,event=None):

        '''Hide canvas pane.'''

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
            g.warning('can not delete leftmost editor')
            return

        # Actually delete the widget.
        if trace: g.trace('**delete name %s id(wrapper) %s id(w) %s' % (
            name,id(wrapper),id(w)))

        del d [name]
        f = c.frame.top.leo_ui.leo_body_inner_frame
        layout = f.layout()
        for z in (w,w.leo_label):
            if z: # 2011/11/12
                self.unpackWidget(layout,z)
        w.leo_label = None # 2011/11/12

        # Select another editor.
        new_wrapper = list(d.values())[0]
        if trace: g.trace(wrapper,new_wrapper)
        self.numberOfEditors -= 1
        if self.numberOfEditors == 1:
            w = new_wrapper.widget
            if w.leo_label: # 2011/11/12
                self.unpackWidget(layout,w.leo_label)
                w.leo_label = None # 2011/11/12

        self.selectEditor(new_wrapper)
    #@+node:ekr.20110605121601.18219: *5* hideTextRenderer (qtBody)
    def hideCanvas (self,event=None):

        '''Hide canvas pane.'''

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
            g.warning('can not delete leftmost editor')
            return

        # Actually delete the widget.
        if trace: g.trace('**delete name %s id(wrapper) %s id(w) %s' % (
            name,id(wrapper),id(w)))

        del d [name]
        f = c.frame.top.leo_ui.leo_body_inner_frame
        layout = f.layout()
        for z in (w,w.leo_label):
            if z: # 2011/11/12
                self.unpackWidget(layout,z)
        w.leo_label = None  # 2011/11/12

        # Select another editor.
        new_wrapper = list(d.values())[0]
        if trace: g.trace(wrapper,new_wrapper)
        self.numberOfEditors -= 1
        if self.numberOfEditors == 1:
            w = new_wrapper.widget
            if w.leo_label:  # 2011/11/12
                self.unpackWidget(layout,w.leo_label)
                w.leo_label = None # 2011/11/12

        self.selectEditor(new_wrapper)
    #@+node:ekr.20110605121601.18220: *5* packRenderer (qtBody)
    def packRenderer (self,f,name,w):

        n = max(1,self.numberOfEditors)
        assert isinstance(f,QtGui.QFrame),f
        layout = f.layout()
        f.setObjectName('%s Frame' % name)
        # Create the text: to do: use stylesheet to set font, height.
        lab = QtGui.QLineEdit(f)
        lab.setObjectName('%s Label' % name)
        lab.setText(name)
        # Pack the label and the widget.
        layout.addWidget(lab,0,max(0,n-1),QtCore.Qt.AlignVCenter)
        layout.addWidget(w,1,max(0,n-1))
        layout.setRowStretch(0,0)
        layout.setRowStretch(1,1) # Give row 1 as much as possible.
        return lab
    #@+node:ekr.20110605121601.18221: *5* showCanvasRenderer (qtBody)
    # An override of leoFrame.addEditor.

    def showCanvasRenderer (self,event=None):

        '''Show the canvas area in the body pane, creating it if necessary.'''

        # bodyCtrl = self.c.frame.body.bodyCtrl # A leoQTextEditWidget
        c = self.c
        f = c.frame.top.leo_ui.leo_body_inner_frame
        assert isinstance(f,QtGui.QFrame),f
        if not self.canvasRenderer:
            name = 'Graphics Renderer'
            self.canvasRenderer = w = QtGui.QGraphicsView(f)
            w.setObjectName(name)
        if not self.canvasRendererVisible:
            self.canvasRendererLabel = self.packRenderer(f,name,w)
            self.canvasRendererVisible = True
    #@+node:ekr.20110605121601.18222: *5* showTextRenderer (qtBody)
    # An override of leoFrame.addEditor.

    def showTextRenderer (self,event=None):

        '''Show the canvas area in the body pane, creating it if necessary.'''

        c = self.c
        f = c.frame.top.leo_ui.leo_body_inner_frame
        assert isinstance(f,QtGui.QFrame),f

        if not self.textRenderer:
            name = 'Text Renderer'
            self.textRenderer = w = LeoQTextBrowser(f,c,self)
            w.setObjectName(name)
            self.textRendererWrapper = leoQTextEditWidget(
                w,name='text-renderer',c=c)

        if not self.textRendererVisible:
            self.textRendererLabel = self.packRenderer(f,name,w)
            self.textRendererVisible = True
    #@+node:ekr.20110605121601.18223: *4* Event handlers (qtBody)
    #@+node:ekr.20110930174206.15472: *5* onFocusIn (qtBody)
    def onFocusIn (self,obj):

        '''Handle a focus-in event in the body pane.'''

        trace = False and not g.unitTesting
        if trace: g.trace(str(obj.objectName()))

        # 2010/08/01: Update the history only on focus in events.
        # 2011/04/02: Update history only in leoframe.tree.select.
        # c.nodeHistory.update(c.p)
        if obj.objectName() == 'richTextEdit':
            wrapper = hasattr(obj,'leo_wrapper') and obj.leo_wrapper
            if wrapper and wrapper != self.bodyCtrl:
                self.selectEditor(wrapper)
            self.onFocusColorHelper('focus-in',obj)
            obj.setReadOnly(False)
            obj.setFocus() # Weird, but apparently necessary.
    #@+node:ekr.20110930174206.15473: *5* onFocusOut (qtBody)
    def onFocusOut (self,obj):

        '''Handle a focus-out event in the body pane.'''

        trace = False and not g.unitTesting

        if trace: g.trace(str(obj.objectName()))

        # Apparently benign.
        if obj.objectName() == 'richTextEdit':
            self.onFocusColorHelper('focus-out',obj)
            obj.setReadOnly(True)

    #@+node:ekr.20110605121601.18224: *5* onFocusColorHelper (qtBody)
    badFocusColors = []

    def onFocusColorHelper(self,kind,obj):

        trace = False and not g.unitTesting
        c = self.c
        if trace: g.trace(kind)
        if kind == 'focus-in':
            # if trace: g.trace('%9s' % (kind),'calling c.k.showStateColors()')
            c.k.showStateColors(inOutline=False,w=self.widget)
        else:
            bg = self.unselectedBackgroundColor
            fg = self.unselectedForegroundColor
            c.frame.body.setEditorColors(bg,fg)
    #@-others
#@+node:ekr.20110605121601.18225: *3* class leoQtFindTab (findTab)
class leoQtFindTab (leoFind.findTab):

    '''A subclass of the findTab class containing all Qt Gui code.'''

    if 0: # We can use the base-class ctor.
        def __init__ (self,c,parentFrame):
            leoFind.findTab.__init__(self,c,parentFrame)
                # Init the base class.
                # Calls initGui, createFrame and init(c), in that order.

    #@+others
    #@+node:ekr.20110605121601.18226: *4*  Birth: called from leoFind ctor
    # leoFind.__init__ calls initGui, createFrame and init, in that order.
    #@+node:ekr.20110605121601.18227: *5* initGui
    def initGui (self):

        owner = self

        self.svarDict = {}
            # Keys are ivar names, values are svar objects.

        # Keys are option names; values are <svars>.
        for ivar in self.intKeys:
            self.svarDict[ivar] = self.svar(owner,ivar)

        # g.trace(self.svarDict)

        # Add a hack for 'entire_outline' radio button.
        ivar = 'entire_outline'
        self.svarDict[ivar] = self.svar(owner,ivar)

        for ivar in self.newStringKeys:
            # "radio-find-type", "radio-search-scope"
            self.svarDict[ivar] = self.svar(owner,ivar)
    #@+node:ekr.20110605121601.18228: *5* init (qtFindTab) & helpers
    def init (self,c):

        '''Init the widgets of the 'Find' tab.'''

        # g.trace('leoQtFindTab.init')
        self.createIvars()
        self.initIvars()
        self.initTextWidgets()
        self.initCheckBoxes()
        self.initRadioButtons()
    #@+node:ekr.20110605121601.18229: *6* createIvars (qtFindTab)
    def createIvars (self):

        c = self.c ; w = c.frame.top.leo_ui # A Window ui object.

        # Bind boxes to Window objects.
        self.widgetsDict = {} # Keys are ivars, values are Qt widgets.
        findWidget   = leoQLineEditWidget(w.findPattern,'find-widget',c)
        changeWidget = leoQLineEditWidget(w.findChange,'change-widget',c)
        data = (
            ('find_ctrl',       findWidget),
            ('change_ctrl',     changeWidget),
            ('whole_word',      w.checkBoxWholeWord),
            ('ignore_case',     w.checkBoxIgnoreCase),
            ('wrap',            w.checkBoxWrapAround),
            ## ('reverse',         w.checkBoxReverse),
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
    #@+node:ekr.20110605121601.18230: *6* initIvars
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
    #@+node:ekr.20110605121601.18231: *6* initTextWidgets (qtFindTab)
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
    #@+node:ekr.20110605121601.18232: *6* initCheckBoxes
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
            'pattern_match',
            # 'reverse',
            'search_body','search_headline',
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
    #@+node:ekr.20110605121601.18233: *6* initRadioButtons
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
    #@+node:ekr.20110605121601.18234: *4* class svar (qtFindTab)
    class svar:
        '''A class like Tk's IntVar and StringVar classes.'''

        #@+others
        #@+node:ekr.20110605121601.18235: *5* svar.ctor
        def __init__(self,owner,ivar):

            self.ivar = ivar
            self.owner = owner
            self.radioButtons = ['node_only','suboutline_only','entire_outline']
            self.trace = False
            self.val = None
            self.w = None

        def __repr__(self):
            return '<svar %s>' % self.ivar
        #@+node:ekr.20110605121601.18236: *5* get
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
        #@+node:ekr.20110605121601.18237: *5* init
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
        #@+node:ekr.20110605121601.18238: *5* set
        def set (self,val):

            '''Init the svar and update the radio buttons.'''

            trace = False and not g.unitTesting
            if trace: g.trace(val)

            self.init(val)

            if self.ivar in self.radioButtons:
                self.owner.initRadioButtons()
            elif self.ivar == 'radio-search-scope':
                self.setRadioScope(val)


        #@+node:ekr.20110605121601.18239: *5* setRadioScope
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
        #@+node:ekr.20110605121601.18240: *5* setWidget
        def setWidget(self,w):

            self.w = w
        #@-others
    #@+node:ekr.20110605121601.18241: *4* Support for minibufferFind class (qtFindTab)
    # This is the same as the Tk code because we simulate Tk svars.
    #@+node:ekr.20110605121601.18242: *5* getOption
    def getOption (self,ivar):

        var = self.svarDict.get(ivar)

        if var:
            val = var.get()
            # g.trace('ivar %s = %s' % (ivar,val))
            return val
        else:
            # g.trace('bad ivar name: %s' % ivar)
            return None
    #@+node:ekr.20110605121601.18243: *5* setOption (findTab)
    def setOption (self,ivar,val):

        trace = False and not g.unitTesting
        if trace: g.trace(ivar,val)

        if ivar in self.intKeys:
            if val is not None:
                svar = self.svarDict.get(ivar)
                svar.set(val)
                if trace: g.trace('qtFindTab: ivar %s = %s' % (
                    ivar,val))

        elif not g.app.unitTesting:
            g.trace('oops: bad find ivar %s' % ivar)
    #@+node:ekr.20110605121601.18244: *5* toggleOption
    def toggleOption (self,ivar):

        if ivar in self.intKeys:
            var = self.svarDict.get(ivar)
            val = not var.get()
            var.set(val)
            # g.trace('%s = %s' % (ivar,val),var)
        else:
            g.trace('oops: bad find ivar %s' % ivar)
    #@-others
#@+node:ekr.20110605121601.18245: *3* class leoQtFrame
class leoQtFrame (leoFrame.leoFrame):

    """A class that represents a Leo window rendered in qt."""

    #@+others
    #@+node:ekr.20110605121601.18246: *4*  Birth & Death (qtFrame)
    #@+node:ekr.20110605121601.18247: *5* __init__ (qtFrame)
    def __init__(self,c,title,gui):


        # Init the base class.
        leoFrame.leoFrame.__init__(self,c,gui)

        assert self.c == c
        leoFrame.leoFrame.instances += 1 # Increment the class var.

        # Official ivars...
        self.iconBar = None
        self.iconBarClass = self.qtIconBarClass
        self.initComplete = False # Set by initCompleteHint().
        self.minibufferVisible = True
        self.statusLineClass = self.qtStatusLineClass
        self.title = title

        # Config settings.
        self.trace_status_line = c.config.getBool('trace_status_line')
        self.use_chapters      = c.config.getBool('use_chapters')
        self.use_chapter_tabs  = c.config.getBool('use_chapter_tabs')

        self.setIvars()

    #@+node:ekr.20110605121601.18248: *6* setIvars (qtFrame)
    def setIvars(self):

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

        # Used by event handlers...
        self.controlKeyIsDown = False # For control-drags
        self.isActive = True
        self.redrawCount = 0
        self.wantedWidget = None
        self.wantedCallbackScheduled = False
        self.scrollWay = None
    #@+node:ekr.20110605121601.18249: *5* __repr__ (qtFrame)
    def __repr__ (self):

        return "<leoQtFrame: %s>" % self.title
    #@+node:ekr.20110605121601.18250: *5* qtFrame.finishCreate & helpers
    def finishCreate (self):

        trace = (False or g.trace_startup) and not g.unitTesting
        if trace: print('qtFrame.finishCreate')

        f = self
        c = self.c
        assert c

        # returns DynamicWindow
        f.top = g.app.gui.frameFactory.createFrame(f)

        f.createIconBar() # A base class method.
        f.createSplitterComponents()
        f.createStatusLine() # A base class method.
        f.createFirstTreeNode() # Call the base-class method.

        f.menu = leoQtMenu(f,label='top-level-menu')
        g.app.windowList.append(f)
        f.miniBufferWidget = leoQtMinibuffer(c)

        c.bodyWantsFocus()
    #@+node:ekr.20110605121601.18251: *6* createSplitterComponents (qtFrame)
    def createSplitterComponents (self):

        f = self ; c = f.c

        f.tree  = leoQtTree(c,f)
        f.log   = leoQtLog(f,None)
        f.body  = leoQtBody(f,None)

        f.splitVerticalFlag,f.ratio,f.secondary_ratio = f.initialRatios()
        f.resizePanesToRatio(f.ratio,f.secondary_ratio)
    #@+node:ekr.20110605121601.18252: *5* initCompleteHint
    def initCompleteHint (self):

        '''A kludge: called to enable text changed events.'''

        self.initComplete = True
        # g.trace(self.c)
    #@+node:ekr.20110605121601.18253: *5* Destroying the qtFrame
    #@+node:ekr.20110605121601.18254: *6* destroyAllObjects
    def destroyAllObjects (self):

        """Clear all links to objects in a Leo window."""

        frame = self ; c = self.c

        # g.printGcAll()

        # Do this first.
        #@+<< clear all vnodes in the tree >>
        #@+node:ekr.20110605121601.18255: *7* << clear all vnodes in the tree>>
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

    #@+node:ekr.20110605121601.18256: *6* destroySelf (qtFrame)
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


    #@+node:ekr.20110605121601.18257: *4* class qtStatusLineClass (qtFrame)
    class qtStatusLineClass:

        '''A class representing the status line.'''

        #@+others
        #@+node:ekr.20110605121601.18258: *5* ctor (qtFrame)
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
            splitter = QtGui.QSplitter()
            self.statusBar.addWidget(splitter, True)
            
            sizes = c.config.getString('status_line_split_sizes') or '1 2'
            sizes = [int(i) for i in sizes.replace(',', ' ').split()]
            for n, i in enumerate(sizes):
                w = [w1, w2][n]
                policy = w.sizePolicy()
                policy.setHorizontalStretch(i)
                policy.setHorizontalPolicy(policy.Minimum)
                w.setSizePolicy(policy)

            splitter.addWidget(w1)
            splitter.addWidget(w2)

            c.status_line_unl_mode = 'original'
            def cycle_unl_mode():
                if c.status_line_unl_mode == 'original':
                    c.status_line_unl_mode = 'canonical'
                else:
                    c.status_line_unl_mode = 'original'
                verbose = c.status_line_unl_mode=='canonical'
                w2.setText(c.p.get_UNL(with_proto=verbose))

            def add_item(event, w2=w2):
                menu = w2.createStandardContextMenu()
                menu.addSeparator()
                menu.addAction("Toggle UNL mode", cycle_unl_mode)
                menu.exec_(event.globalPos())

            w2.contextMenuEvent = add_item

            self.put('')
            self.update()
            c.frame.top.setStyleSheets()
        #@+node:ekr.20110605121601.18260: *5* clear, get & put/1
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
        #@+node:ekr.20110605121601.18261: *5* update (qtStatusLineClass)
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
            # g.trace(row,col,fcol)

            self.put1(
                "line: %d, col: %d, fcol: %d" % (row,col,fcol))
            self.lastRow = row
            self.lastCol = col
            self.lastFcol = fcol
        #@-others
    #@+node:ekr.20110605121601.18262: *4* class qtIconBarClass
    class qtIconBarClass:

        '''A class representing the singleton Icon bar'''

        #@+others
        #@+node:ekr.20110605121601.18263: *5*  ctor (qtIconBarClass)
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
        #@+node:ekr.20110605121601.18264: *5*  do-nothings (qtIconBarClass)
        # These *are* called from Leo's core.

        def addRow(self,height=None):
            pass # To do.
            
        def getNewFrame (self): 
            return None # To do
        #@+node:ekr.20110605121601.18265: *5* add (qtIconBarClass)
        def add(self,*args,**keys):

            '''Add a button to the icon bar.'''

            trace = False and not g.unitTesting
            c = self.c
            if not self.w: return
            command = keys.get('command')
            text = keys.get('text')
            # able to specify low-level QAction directly (QPushButton not forced)
            qaction = keys.get('qaction')

            if not text and not qaction:
                g.es('bad toolbar item')

            kind = keys.get('kind') or 'generic-button'

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
                    
                    self.button.setProperty('button_kind', kind)  # for styling
                    
                    return b

            if qaction is None:
                action = leoIconBarButton(parent=self.w,text=text,toolbar=self)
                button_name = text
            else:
                action = qaction
                button_name = action.text()

            self.w.addAction(action)
            self.actions.append(action)
            b = self.w.widgetForAction(action)

            # Set the button's object name so we can use the stylesheet to color it.
            if not button_name: button_name = 'unnamed'
            button_name = button_name + '-button'
            b.setObjectName(button_name)
            if trace: g.trace(button_name)

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
        #@+node:ekr.20110605121601.18266: *5* addRowIfNeeded
        def addRowIfNeeded (self):

            '''Add a new icon row if there are too many widgets.'''

            # n = g.app.iconWidgetCount

            # if n >= self.widgets_per_row:
                # g.app.iconWidgetCount = 0
                # self.addRow()

            # g.app.iconWidgetCount += 1
        #@+node:ekr.20110605121601.18267: *5* addWidget
        def addWidget (self,w):

            self.w.addWidget(w)
        #@+node:ekr.20110605121601.18268: *5* clear
        def clear(self):

            """Destroy all the widgets in the icon bar"""

            self.w.clear()
            self.actions = []

            g.app.iconWidgetCount = 0
        #@+node:ekr.20110605121601.18269: *5* createChaptersIcon
        def createChaptersIcon(self):

            # g.trace('(qtIconBarClass)')
            c = self.c
            f = c.frame
            if f.use_chapters and f.use_chapter_tabs:
                return leoQtTreeTab(c,f.iconBar)
            else:
                return None
        #@+node:ekr.20110605121601.18270: *5* deleteButton
        def deleteButton (self,w):
            """ w is button """

            self.w.removeAction(w)

            self.c.bodyWantsFocus()
            self.c.outerUpdate()
        #@+node:ekr.20110605121601.18271: *5* qtIconBarClass.setCommandForButton (@rclick nodes)
        def setCommandForButton(self,button,command):

            # EKR 2013/09/12: fix bug 1193819: Script buttons cant "go to script" after outline changes.
            # The command object now has a gnx ivar instead of a p ivar.
            # The code below uses command.controller.find_gnx to determine the proper position.
            if command:
                # button is a leoIconBarButton.
                QtCore.QObject.connect(button.button,
                    QtCore.SIGNAL("clicked()"),command)
                # can get here from @buttons in the current outline, in which
                # case p exists, or from @buttons in @settings elsewhere, in
                # which case it doesn't
                if not hasattr(command,'gnx'):
                    return
                command_p = command.controller.find_gnx(command.gnx)
                if not command_p:
                    return
                # 20100518 - TNB command is instance of callable class with
                #   c and gnx attributes, so we can add a context menu item...
                def goto_command(command = command):
                    c = command.c
                    p = command.controller.find_gnx(command.gnx)
                    if p:
                        c.selectPosition(p)
                        c.redraw()
                b = button.button
                docstring = g.getDocString(command_p.b)
                if docstring:
                    b.setToolTip(docstring)
                b.goto_script = gts = QtGui.QAction('Goto Script', b)
                b.addAction(gts)
                gts.connect(gts, QtCore.SIGNAL("triggered()"), goto_command)
                # 20100519 - TNB also, scan @button's following sibs and childs
                #   for @rclick nodes
                rclicks = []
                if '@others' not in command_p.b:
                    rclicks.extend([i.copy() for i in command_p.children()
                      if i.h.startswith('@rclick ')])
                for i in command_p.following_siblings():
                    if i.h.startswith('@rclick '):
                        rclicks.append(i.copy())
                    else:
                        break
                if rclicks:
                    b.setText(g.u(b.text())+(command.c.config.getString('mod_scripting_subtext') or ''))
                for rclick in rclicks:
                    headline = rclick.h[8:]
                    rc = QtGui.QAction(headline.strip(),b)
                    if '---' in headline and headline.strip().strip('-') == '':
                        rc.setSeparator(True)
                    else:
                        def cb(event=None, ctrl=command.controller, p=rclick, 
                               c=command.c, b=command.b, t=rclick.h[8:]):
                            ctrl.executeScriptFromButton(b,t,p.gnx)
                            if c.exists:
                                c.outerUpdate()
                        rc.connect(rc, QtCore.SIGNAL("triggered()"), cb)
                    # This code has no effect.
                    # docstring = g.getDocString(rclick.b).strip()
                    # if docstring:
                        # rc.setToolTip(docstring)
                    b.insertAction(b.actions()[-2],rc)  # insert rc before Remove Button
                if rclicks:
                    rc = QtGui.QAction('---',b)
                    rc.setSeparator(True)
                    b.insertAction(b.actions()[-2],rc)
        #@-others
    #@+node:ekr.20110605121601.18274: *4* Configuration (qtFrame)
    #@+node:ekr.20110605121601.18275: *5* configureBar (qtFrame)
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
    #@+node:ekr.20110605121601.18276: *5* configureBarsFromConfig (qtFrame)
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
    #@+node:ekr.20110605121601.18277: *5* reconfigureFromConfig (qtFrame)
    def reconfigureFromConfig (self):

        frame = self ; c = frame.c

        # frame.tree.setFontFromConfig()
        frame.configureBarsFromConfig()

        # frame.body.setFontFromConfig()
        # frame.body.setColorFromConfig()

        frame.setTabWidth(c.tab_width)
        # frame.log.setFontFromConfig()
        # frame.log.setColorFromConfig()

        c.redraw()
    #@+node:ekr.20110605121601.18278: *5* setInitialWindowGeometry (qtFrame)
    def setInitialWindowGeometry(self):

        """Set the position and size of the frame to config params."""

        c = self.c

        h = c.config.getInt("initial_window_height") or 500
        w = c.config.getInt("initial_window_width") or 600
        x = c.config.getInt("initial_window_left") or 10
        y = c.config.getInt("initial_window_top") or 10

        # g.trace(h,w,x,y)

        if h and w and x and y:
            self.setTopGeometry(w,h,x,y)
    #@+node:ekr.20110605121601.18279: *5* setTabWidth (qtFrame)
    def setTabWidth (self, w):

        # A do-nothing because tab width is set automatically.
        # It *is* called from Leo's core.
        pass

    #@+node:ekr.20110605121601.18280: *5* setWrap (qtFrame)
    def setWrap (self,p):

        self.c.frame.body.setWrap(p)
    #@+node:ekr.20110605121601.18281: *5* reconfigurePanes (qtFrame)
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
    #@+node:ekr.20110605121601.18282: *5* resizePanesToRatio (qtFrame)
    def resizePanesToRatio(self,ratio,ratio2):

        trace = False and not g.unitTesting

        f = self
        if trace: g.trace('%5s, %0.2f %0.2f' % (
            self.splitVerticalFlag,ratio,ratio2),g.callers(4))
        f.divideLeoSplitter(self.splitVerticalFlag,ratio)
        f.divideLeoSplitter(not self.splitVerticalFlag,ratio2)
    #@+node:ekr.20110605121601.18283: *5* divideLeoSplitter
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
        self.divideAnySplitter (frac, self.top.leo_ui.splitter)

    #@+node:ekr.20110605121601.18284: *5* divideAnySplitter
    # This is the general-purpose placer for splitters.
    # It is the only general-purpose splitter code in Leo.

    def divideAnySplitter (self,frac,splitter):

        sizes = splitter.sizes()

        if len(sizes)!=2:
            g.trace('%s widget(s) in %s' % (len(sizes),id(splitter)))
            return

        if frac > 1 or frac < 0:
            g.trace('split ratio [%s] out of range 0 <= frac <= 1'%frac)

        s1, s2 = sizes
        s = s1+s2
        s1 = int(s * frac + 0.5)
        s2 = s - s1 

        splitter.setSizes([s1,s2])
    #@+node:ekr.20110605121601.18285: *4* Event handlers (qtFrame)
    #@+node:ekr.20110605121601.18286: *5* frame.OnCloseLeoEvent
    # Called from quit logic and when user closes the window.
    # Returns True if the close happened.

    def OnCloseLeoEvent(self):

        f = self ; c = f.c

        if c.inCommand:
            # g.trace('requesting window close')
            c.requestCloseWindow = True
        else:
            g.app.closeLeoWindow(self)
    #@+node:ekr.20110605121601.18287: *5* frame.OnControlKeyUp/Down
    def OnControlKeyDown (self,event=None):

        self.controlKeyIsDown = True

    def OnControlKeyUp (self,event=None):

        self.controlKeyIsDown = False
    #@+node:ekr.20110605121601.18290: *5* OnActivateTree
    def OnActivateTree (self,event=None):

        pass
    #@+node:ekr.20110605121601.18291: *5* OnBodyClick, OnBodyRClick (not used)
    # At present, these are not called,
    # but they could be called by LeoQTextBrowser.

    def OnBodyClick (self,event=None):

        g.trace()

        try:
            c = self.c ; p = c.currentPosition()
            if g.doHook("bodyclick1",c=c,p=p,v=p,event=event):
                g.doHook("bodyclick2",c=c,p=p,v=p,event=event)
                return
            else:
                c.k.showStateAndMode(w=c.frame.body.bodyCtrl)
                g.doHook("bodyclick2",c=c,p=p,v=p,event=event)
        except:
            g.es_event_exception("bodyclick")

    def OnBodyRClick(self,event=None):

        try:
            c = self.c ; p = c.currentPosition()
            if g.doHook("bodyrclick1",c=c,p=p,v=p,event=event):
                g.doHook("bodyrclick2",c=c,p=p,v=p,event=event)
                return
            else:
                c.k.showStateAndMode(w=c.frame.body.bodyCtrl)
                g.doHook("bodyrclick2",c=c,p=p,v=p,event=event)
        except:
            g.es_event_exception("iconrclick")
    #@+node:ekr.20110605121601.18292: *5* OnBodyDoubleClick (Events) (not used)
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
    #@+node:ekr.20110605121601.18293: *4* Gui-dependent commands
    #@+node:ekr.20110605121601.18294: *5* Minibuffer commands... (qtFrame)
    #@+node:ekr.20110605121601.18295: *6* contractPane
    def contractPane (self,event=None):

        '''Contract the selected pane.'''

        f = self ; c = f.c

        w = c.get_requested_focus() or g.app.gui.get_focus(c)
        wname = c.widget_name(w)

        # g.trace(wname)
        if not w: return

        if wname.startswith('body'):
            f.contractBodyPane()
            c.bodyWantsFocus()
        elif wname.startswith('log'):
            f.contractLogPane()
            c.logWantsFocus()
        else:
            for z in ('head','canvas','tree'):
                if wname.startswith(z):
                    f.contractOutlinePane()
                    c.treeWantsFocus()
                    break
    #@+node:ekr.20110605121601.18296: *6* expandPane
    def expandPane (self,event=None):

        '''Expand the selected pane.'''

        f = self ; c = f.c

        w = c.get_requested_focus() or g.app.gui.get_focus(c)
        wname = c.widget_name(w)

        # g.trace(wname)
        if not w: return

        if wname.startswith('body'):
            f.expandBodyPane()
            c.bodyWantsFocus()
        elif wname.startswith('log'):
            f.expandLogPane()
            c.logWantsFocus()
        else:
            for z in ('head','canvas','tree'):
                if wname.startswith(z):
                    f.expandOutlinePane()
                    c.treeWantsFocus()
                    break
    #@+node:ekr.20110605121601.18297: *6* fullyExpandPane
    def fullyExpandPane (self,event=None):

        '''Fully expand the selected pane.'''

        f = self ; c = f.c

        w = c.get_requested_focus() or g.app.gui.get_focus(c)
        wname = c.widget_name(w)

        # g.trace(wname)
        if not w: return

        if wname.startswith('body'):
            f.fullyExpandBodyPane()
            c.treeWantsFocus()
        elif wname.startswith('log'):
            f.fullyExpandLogPane()
            c.bodyWantsFocus()
        else:
            for z in ('head','canvas','tree'):
                if wname.startswith(z):
                    f.fullyExpandOutlinePane()
                    c.bodyWantsFocus()
                    break
    #@+node:ekr.20110605121601.18298: *6* hidePane
    def hidePane (self,event=None):

        '''Completely contract the selected pane.'''

        f = self ; c = f.c

        w = c.get_requested_focus() or g.app.gui.get_focus(c)
        wname = c.widget_name(w)

        # g.trace(wname)
        if not w: return

        if wname.startswith('body'):
            f.hideBodyPane()
            c.treeWantsFocus()
        elif wname.startswith('log'):
            f.hideLogPane()
            c.bodyWantsFocus()
        else:
            for z in ('head','canvas','tree'):
                if wname.startswith(z):
                    f.hideOutlinePane()
                    c.bodyWantsFocus()
                    break
    #@+node:ekr.20110605121601.18299: *6* expand/contract/hide...Pane
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
    #@+node:ekr.20110605121601.18300: *6* fullyExpand/hide...Pane
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
    #@+node:ekr.20110605121601.18301: *5* Window Menu...
    #@+node:ekr.20110605121601.18302: *6* toggleActivePane (qtFrame)
    def toggleActivePane (self,event=None):

        '''Toggle the focus between the outline and body panes.'''

        frame = self ; c = frame.c
        w = c.get_focus()
        w_name = g.app.gui.widget_name(w)

        # g.trace(w,w_name)

        if w_name in ('canvas','tree','treeWidget'):
            c.endEditing()
            c.bodyWantsFocus()
        else:
            c.treeWantsFocus()
    #@+node:ekr.20110605121601.18303: *6* cascade
    def cascade (self,event=None):

        '''Cascade all Leo windows.'''

        x,y,delta = 50,50,50
        for frame in g.app.windowList:

            w = frame and frame.top
            if w:
                r = w.geometry() # a Qt.Rect
                # 2011/10/26: Fix bug 823601: cascade-windows fails.
                w.setGeometry(QtCore.QRect(x,y,r.width(),r.height()))

                # Compute the new offsets.
                x += 30 ; y += 30
                if x > 200:
                    x = 10 + delta ; y = 40 + delta
                    delta += 10
    #@+node:ekr.20110605121601.18304: *6* equalSizedPanes
    def equalSizedPanes (self,event=None):

        '''Make the outline and body panes have the same size.'''

        frame = self
        frame.resizePanesToRatio(0.5,frame.secondary_ratio)
    #@+node:ekr.20110605121601.18305: *6* hideLogWindow
    def hideLogWindow (self,event=None):

        frame = self

        frame.divideLeoSplitter2(0.99, not frame.splitVerticalFlag)
    #@+node:ekr.20110605121601.18306: *6* minimizeAll (qtFrame)
    def minimizeAll (self,event=None):

        '''Minimize all Leo's windows.'''

        for frame in g.app.windowList:
            self.minimize(frame)

    def minimize(self,frame):

        # This unit test will fail when run externally.

        if frame and frame.top:

            # For --gui=qttabs, frame.top.leo_master is a LeoTabbedTopLevel.
            # For --gui=qt,     frame.top is a DynamicWindow.
            w = frame.top.leo_master or frame.top
            if g.unitTesting:
                g.app.unitTestDict['minimize-all'] = True
                assert hasattr(w,'setWindowState'),w
            else:
                w.setWindowState(QtCore.Qt.WindowMinimized)
    #@+node:ekr.20110605121601.18307: *6* toggleSplitDirection (qtFrame)
    def toggleSplitDirection (self,event=None):

        '''Toggle the split direction in the present Leo window.'''

        trace = False and not g.unitTesting
        c,f = self.c,self

        if trace: g.trace('*'*20)

        def getRatio(w):
            sizes = w.sizes()
            if len(sizes) == 2:
                size1,size2 = sizes
                ratio = float(size1)/float(size1+size2)
                if trace: g.trace(
                    '   ratio: %0.2f, size1: %3s, size2: %3s, total: %4s, w: %s' % (
                    ratio,size1,size2,size1+size2,w))
                return ratio
            else:
                if trace: g.trace('oops: len(sizes)',len(sizes),'default 0.5')
                return float(0.5)

        def getNewSizes(sizes,ratio):
            size1,size2 = sizes
            total = size1+size2
            size1 = int(float(ratio)*float(total))
            size2 = total - size1
            if trace: g.trace(
                'ratio: %0.2f, size1: %3s, size2: %3s, total: %4s' % (
                ratio,size1,size2,total))
            return [size1,size2]

        # Compute the actual ratios before reorienting.
        w1,w2 = f.top.splitter, f.top.splitter_2
        r1 = getRatio(w1)
        r2 = getRatio(w2)
        f.ratio,f.secondary_ratio = r1,r2

        # Remember the sizes before reorienting.
        sizes1 = w1.sizes()
        sizes2 = w2.sizes()

        # Reorient the splitters.
        for w in (f.top.splitter,f.top.splitter_2):
            w.setOrientation(
                g.choose(w.orientation() == QtCore.Qt.Horizontal,
                    QtCore.Qt.Vertical,QtCore.Qt.Horizontal))

        # Fix bug 580328: toggleSplitDirection doesn't preserve existing ratio.
        if len(sizes1) == 2 and len(sizes2) == 2:
            w1.setSizes(getNewSizes(sizes1,r1))
            w2.setSizes(getNewSizes(sizes2,r2))

        # Maintain the key invariant: self.splitVerticalFlag
        # tells the alignment of the main splitter.
        f.splitVerticalFlag = not f.splitVerticalFlag

        # Fix bug 581031: Scrollbar position is not preserved.
        # This is better than adjust the scroll value directy.
        c.frame.tree.setItemForCurrentPosition(scroll=True)
        c.frame.body.seeInsertPoint()
    #@+node:ekr.20110605121601.18308: *6* resizeToScreen (qtFrame)
    def resizeToScreen (self,event=None):

        '''Resize the Leo window so it fill the entire screen.'''

        frame = self

        # This unit test will fail when run externally.

        if frame and frame.top:

            # For --gui=qttabs, frame.top.leo_master is a LeoTabbedTopLevel.
            # For --gui=qt,     frame.top is a DynamicWindow.
            w = frame.top.leo_master or frame.top
            if g.unitTesting:
                g.app.unitTestDict['resize-to-screen'] = True
                assert hasattr(w,'setWindowState'),w
            else:
                w.setWindowState(QtCore.Qt.WindowMaximized)
    #@+node:ekr.20110605121601.18309: *5* Help Menu...
    #@+node:ekr.20110605121601.18310: *6* leoHelp
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
    #@+node:ekr.20110605121601.18311: *4* Qt bindings... (qtFrame)
    def bringToFront (self):
        self.lift()
    def deiconify (self):
        if self.top and self.top.isMinimized(): # Bug fix: 400739.
            self.lift()
    def getFocus(self):
        return g.app.gui.get_focus(self.c) # Bug fix: 2009/6/30.
    def get_window_info(self):
        if hasattr(self.top,'leo_master') and self.top.leo_master:
            f = self.top.leo_master
        else:
            f = self.top
        rect = f.geometry()
        topLeft = rect.topLeft()
        x,y = topLeft.x(),topLeft.y()
        w,h = rect.width(),rect.height()
        # g.trace(w,h,x,y)
        return w,h,x,y
    def iconify(self):
        if self.top: self.top.showMinimized()
    def lift (self):
        # g.trace(self.c,'\n',g.callers(9))
        if not self.top: return
        if self.top.isMinimized(): # Bug 379141
            self.top.showNormal()
        self.top.activateWindow()
        self.top.raise_()
    def getTitle (self):
        # Fix https://bugs.launchpad.net/leo-editor/+bug/1194209
        # When using tabs, leo_master (a LeoTabbedTopLevel) contains the QMainWindow.
        w = self.top.leo_master if g.app.qt_use_tabs else self.top
        s = g.u(w.windowTitle())
        return s
    def setTitle (self,s):
        # g.trace('**(qtFrame)',repr(s))
        if self.top:
            # Fix https://bugs.launchpad.net/leo-editor/+bug/1194209
            # When using tabs, leo_master (a LeoTabbedTopLevel) contains the QMainWindow.
            w = self.top.leo_master if g.app.qt_use_tabs else self.top
            w.setWindowTitle(s)
    def setTopGeometry(self,w,h,x,y,adjustSize=True):
        # self.top is a DynamicWindow.
        # g.trace('(qtFrame)',x,y,w,h,self.top,g.callers())
        if self.top:
            self.top.setGeometry(QtCore.QRect(x,y,w,h))
    def update(self,*args,**keys):
        self.top.update()
    #@-others
#@+node:ekr.20110605121601.18312: *3* class leoQtLog (leoLog)
class leoQtLog (leoFrame.leoLog):

    """A class that represents the log pane of a Qt window."""

    # pylint: disable=R0923
    # R0923:leoQtLog: Interface not implemented

    #@+others
    #@+node:ekr.20110605121601.18313: *4* leoQtLog Birth
    #@+node:ekr.20110605121601.18314: *5* leoQtLog.__init__
    def __init__ (self,frame,parentFrame):

        # g.trace('(leoQtLog)',frame,parentFrame)

        # Call the base class constructor and calls createControl.
        leoFrame.leoLog.__init__(self,frame,parentFrame)

        self.c = c = frame.c # Also set in the base constructor, but we need it here.
        # self.logCtrl = None # The text area for log messages.
            # logCtrl is now a property of the base leoLog class.

        self.contentsDict = {} # Keys are tab names.  Values are widgets.
        self.eventFilters = [] # Apparently needed to make filters work!
        self.logDict = {} # Keys are tab names text widgets.  Values are the widgets.
        self.menu = None # A menu that pops up on right clicks in the hull or in tabs.

        self.tabWidget = tw = c.frame.top.leo_ui.tabWidget
            # The Qt.QTabWidget that holds all the tabs.

        # Fixes bug 917814: Switching Log Pane tabs is done incompletely.
        tw.connect(tw,QtCore.SIGNAL('currentChanged(int)'),self.onCurrentChanged)

        self.wrap = g.choose(c.config.getBool('log_pane_wraps'),True,False)

        if 0: # Not needed to make onActivateEvent work.
            # Works only for .tabWidget, *not* the individual tabs!
            theFilter = leoQtEventFilter(c,w=tw,tag='tabWidget')
            tw.installEventFilter(theFilter)

        # self.setFontFromConfig()
        # self.setColorFromConfig()
    #@+node:ekr.20110605121601.18315: *5* leoQtLog.finishCreate
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
    #@+node:ekr.20110605121601.18316: *5* leoQtLog.getName
    def getName (self):
        return 'log' # Required for proper pane bindings.
    #@+node:ekr.20120304214900.9940: *4* Event handler (leoQtLog)
    def onCurrentChanged(self,idx):

        trace = False and not g.unitTesting

        tabw = self.tabWidget
        w = tabw.widget(idx)

        # Fixes bug 917814: Switching Log Pane tabs is done incompletely
        wrapper = hasattr(w,'leo_log_wrapper') and w.leo_log_wrapper
        if wrapper:
            self.widget = wrapper

        if trace: g.trace(idx,tabw.tabText(idx),self.c.frame.title) # wrapper and wrapper.widget)
    #@+node:ekr.20111120124732.10184: *4* isLogWidget (leoQtLog)
    def isLogWidget(self,w):

        val = w == self or w in list(self.contentsDict.values())
        # g.trace(val,w)
        return val
    #@+node:ekr.20110605121601.18321: *4* put & putnl (leoQtLog)
    #@+node:ekr.20110605121601.18322: *5* put (leoQtLog)
    # All output to the log stream eventually comes here.
    def put (self,s,color=None,tabName='Log',from_redirect=False):

        trace = False and not g.unitTesting
        c = self.c
        if g.app.quitting or not c or not c.exists:
            print('qtGui.log.put fails',repr(s))
            return
        if color:
            color = leoColor.getColor(color,'black')
        else:
            color = leoColor.getColor('black')
        self.selectTab(tabName or 'Log')

        # Note: this must be done after the call to selectTab.
        w = self.logCtrl.widget # w is a QTextBrowser
        if w:
            sb = w.horizontalScrollBar()
            # pos = sb.sliderPosition()
            # g.trace(pos,sb,g.callers())
            s=s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            if not self.wrap: # 2010/02/21: Use &nbsp; only when not wrapping!
                s = s.replace(' ','&nbsp;')
            if from_redirect:
                s = s.replace('\n','<br>')
            else:
                s = s.rstrip().replace('\n','<br>')
            s = '<font color="%s">%s</font>' % (color,s)
            if trace: print('leoQtLog.put',type(s),len(s),s[:40],w)
            if from_redirect:
                w.insertHtml(s)
            else:
                w.append(s) # w.append is a QTextBrowser method.
                # w.insertHtml(s+'<br>') # Also works.
            w.moveCursor(QtGui.QTextCursor.End)
            sb.setSliderPosition(0) # Force the slider to the initial position.
        else:
            # put s to logWaiting and print s
            g.app.logWaiting.append((s,color),)
            if g.isUnicode(s):
                s = g.toEncodedString(s,"ascii")
            print(s)
    #@+node:ekr.20110605121601.18323: *5* putnl (leoQtLog)
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
    #@+node:ekr.20120913110135.10613: *4* putImage (leoQtLog)
    #@+node:ekr.20110605121601.18324: *4* Tab (leoQtLog)
    #@+node:ekr.20110605121601.18325: *5* clearTab
    def clearTab (self,tabName,wrap='none'):

        w = self.logDict.get(tabName)
        if w:
            w.clear() # w is a QTextBrowser.
    #@+node:ekr.20110605121601.18326: *5* createTab (leoQtLog)
    def createTab (self,tabName,createText=True,widget=None,wrap='none'):
        """
        Create a new tab in tab widget
        if widget is None, Create a QTextBrowser,
        suitable for log functionality.
        """
        trace = False and not g.unitTesting
        c = self.c
        if trace: g.trace(tabName,widget and g.app.gui.widget_name(widget) or '<no widget>')
        if widget is None:
            widget = LeoQTextBrowser(parent=None,c=c,wrapper=self)
                # widget is subclass of QTextBrowser.
            contents = leoQTextEditWidget(widget=widget,name='log',c=c)
                # contents a wrapper.
            widget.leo_log_wrapper = contents
                # Inject an ivar into the QTextBrowser that points to the wrapper.
            if trace: g.trace('** creating',tabName,'self.widget',contents,'wrapper',widget)
            option = QtGui.QTextOption
            widget.setWordWrapMode(option.WordWrap if self.wrap else option.NoWrap)
            widget.setReadOnly(False) # Allow edits.
            self.logDict[tabName] = widget
            if tabName == 'Log':
                self.widget = contents # widget is an alias for logCtrl.
                widget.setObjectName('log-widget')
            # Set binding on all log pane widgets.
            if newFilter:
                g.app.gui.setFilter(c,widget,self,tag='log')
            else:
                theFilter = leoQtEventFilter(c,w=self,tag='log')
                self.eventFilters.append(theFilter) # Needed!
                widget.installEventFilter(theFilter)
            # A bad hack.  Set the standard bindings in the Find and Spell tabs here.
            if tabName == 'Log':
                assert c.frame.top.__class__.__name__ == 'DynamicWindow'
                find_widget = c.frame.top.leo_find_widget
                # 2011/11/21: A hack: add an event filter.
                if newFilter:
                    g.app.gui.setFilter(c,find_widget,widget,'find-widget')
                else:
                    find_widget.leo_event_filter = leoQtEventFilter(c,w=widget,tag='find-widget')
                    find_widget.installEventFilter(find_widget.leo_event_filter)
                if trace: g.trace('** Adding event filter for Find',find_widget)
                # 2011/11/21: A hack: make the find_widget an official log widget.
                self.contentsDict['Find']=find_widget
                # 2013/09/20:
                if hasattr(c.frame.top,'leo_spell_widget'):
                    spell_widget = c.frame.top.leo_spell_widget
                    if trace: g.trace('** Adding event filter for Spell',find_widget)
                    if newFilter:
                        g.app.gui.setFilter(c,spell_widget,widget,'spell-widget')
                    else:
                        spell_widget.leo_event_filter = leoQtEventFilter(c,w=widget,tag='spell-widget')
                        spell_widget.installEventFilter(spell_widget.leo_event_filter)
            self.contentsDict[tabName] = widget
            self.tabWidget.addTab(widget,tabName)
        else:
            contents = widget
                # Unlike text widgets, contents is the actual widget.
            widget.leo_log_wrapper = contents
                # The leo_log_wrapper is the widget itself.
            if trace: g.trace('** using',tabName,widget)
            if newFilter:
                g.app.gui.setFilter(c,widget,contents,'tabWidget')
            else:
                theFilter = leoQtEventFilter(c,w=contents,tag='tabWidget')
                self.eventFilters.append(theFilter) # Needed!
                widget.installEventFilter(theFilter)
            self.contentsDict[tabName] = contents
            self.tabWidget.addTab(contents,tabName)
        return contents
    #@+node:ekr.20110605121601.18327: *5* cycleTabFocus (leoQtLog)
    def cycleTabFocus (self,event=None):

        '''Cycle keyboard focus between the tabs in the log pane.'''

        trace = False and not g.unitTesting
        w = self.tabWidget
        i = w.currentIndex()
        i += 1
        if i >= w.count():
            i = 0
        tabName = w.tabText(i)
        self.selectTab(tabName,createText=False)
        if trace: g.trace('(leoQtLog)',i,w,w.count(),w.currentIndex(),g.u(tabName))
        return i
    #@+node:ekr.20110605121601.18328: *5* deleteTab
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
    #@+node:ekr.20110605121601.18329: *5* hideTab
    def hideTab (self,tabName):

        self.selectTab('Log')
    #@+node:ekr.20111122080923.10185: *5* orderedTabNames (leoQtLog)
    def orderedTabNames (self,leoLog=None): # Unused: leoLog

        '''Return a list of tab names in the order in which they appear in the QTabbedWidget.'''

        w = self.tabWidget

        return [w.tabText(i) for i in range(w.count())]

    #@+node:ekr.20110605121601.18330: *5* numberOfVisibleTabs (leoQtLog)
    def numberOfVisibleTabs (self):

        return len([val for val in self.contentsDict.values() if val != None])
            # **Note**: the base-class version of this uses frameDict.
    #@+node:ekr.20110605121601.18331: *5* selectTab & helper (leoQtLog)
    # createText is used by leoLog.selectTab.

    def selectTab (self,tabName,createText=True,widget=None,wrap='none'):

        '''Create the tab if necessary and make it active.'''

        if not self.selectHelper(tabName):
            self.createTab(tabName,widget=widget,wrap=wrap)
            self.selectHelper(tabName)
    #@+node:ekr.20110605121601.18332: *6* selectHelper (leoQtLog)
    def selectHelper (self,tabName):

        trace = False and not g.unitTesting
        c,w = self.c,self.tabWidget

        for i in range(w.count()):
            if tabName == w.tabText(i):
                w.setCurrentIndex(i)

                widget = w.widget(i)

                # 2011/11/21: Set the .widget ivar only if there is a wrapper.
                wrapper = hasattr(widget,'leo_log_wrapper') and widget.leo_log_wrapper
                if wrapper:
                    self.widget = wrapper
                if trace: g.trace(tabName,'widget',widget,'wrapper',wrapper)

                # Do *not* set focus here!
                    # c.widgetWantsFocus(tab_widget)

                if tabName == 'Spell':
                    # the base class uses this as a flag to see if
                    # the spell system needs initing
                    self.frameDict['Spell'] = widget

                self.tabName = tabName # 2011/11/20
                return True
        else:
            self.tabName = None # 2011/11/20
            if trace: g.trace('** not found',tabName)
            return False
    #@+node:ekr.20110605121601.18333: *4* leoQtLog color tab stuff
    def createColorPicker (self,tabName):

        g.warning('color picker not ready for qt')
    #@+node:ekr.20110605121601.18334: *4* leoQtLog font tab stuff
    #@+node:ekr.20110605121601.18335: *5* createFontPicker
    def createFontPicker (self,tabName):

        # log = self
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
                style = name
                break
        else:
            style = ''
        weight = font.weight()
        table = (
            (QFont.Light,'light'),
            (QFont.Normal,'normal'),
            (QFont.DemiBold,'demibold'),
            (QFont.Bold	,'bold'),
            (QFont.Black,'black'))
        for val,name in table:
            if weight == val:
                weight = name
                break
        else:
            weight = ''
        table = (
            ('family',str(font.family())),
            ('size  ',font.pointSize()),
            ('style ',style),
            ('weight',weight),
        )
        for key,val in table:
            if val: g.es(key,val,tabName='Fonts')
    #@+node:ekr.20110605121601.18339: *5* hideFontTab
    def hideFontTab (self,event=None):

        c = self.c
        c.frame.log.selectTab('Log')
        c.bodyWantsFocus()
    #@-others
#@+node:ekr.20110605121601.18340: *3* class leoQtMenu (leoMenu)
class leoQtMenu (leoMenu.leoMenu):

    #@+others
    #@+node:ekr.20110605121601.18341: *4* leoQtMenu.__init__
    def __init__ (self,frame,label):

        assert frame
        assert frame.c

        # Init the base class.
        leoMenu.leoMenu.__init__(self,frame)

        self.leo_menu_label = label.replace('&','').lower()

        # called from createMenuFromConfigList,createNewMenu,new_menu,qtMenuWrapper.ctor.
        # g.trace('(leoQtMenu) %s' % (self.leo_menu_label or '<no label!>'))

        self.frame = frame
        self.c = c = frame.c

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
    #@+node:ekr.20120306130648.9848: *4* leoQtMenu.__repr__
    def __repr__ (self):

        return '<leoQtMenu: %s>' % self.leo_menu_label

    __str__ = __repr__
    #@+node:ekr.20110605121601.18342: *4* Tkinter menu bindings
    # See the Tk docs for what these routines are to do
    #@+node:ekr.20110605121601.18343: *5* Methods with Tk spellings
    #@+node:ekr.20110605121601.18344: *6* add_cascade (leoQtMenu)
    def add_cascade (self,parent,label,menu,underline):

        """Wrapper for the Tkinter add_cascade menu method.

        Adds a submenu to the parent menu, or the menubar."""

        # menu and parent are a qtMenuWrappers, subclasses of  QMenu.
        n = underline
        if -1 < n < len(label):
            label = label[:n] + '&' + label[n:]
        menu.setTitle(label)
        if parent:
            parent.addMenu(menu) # QMenu.addMenu.
        else:
            self.menuBar.addMenu(menu)
        label = label.replace('&','').lower()
        menu.leo_menu_label = label
        return menu
    #@+node:ekr.20110605121601.18345: *6* add_command (leoQtMenu) (Called by createMenuEntries)
    def add_command (self,**keys):

        """Wrapper for the Tkinter add_command menu method."""

        trace = False and not g.unitTesting # and label.startswith('Paste')
        accel = keys.get('accelerator') or ''
        command = keys.get('command')
        commandName = keys.get('commandName')
        label = keys.get('label')
        n = keys.get('underline')
        menu = keys.get('menu') or self
        if not label: return
        if trace: g.trace(label)
            # command is always add_commandCallback,
            # defined in c.add_command.
        if -1 < n < len(label):
            label = label[:n] + '&' + label[n:]
        if accel:
            label = '%s\t%s' % (label,accel)
        action = menu.addAction(label)

        # 2012/01/20: Inject the command name into the action
        # so that it can be enabled/disabled dynamically.
        action.leo_command_name = commandName
        if command:
            def qt_add_command_callback(label=label,command=command):
                # g.trace(command)
                return command()
            QtCore.QObject.connect(action,
                QtCore.SIGNAL("triggered()"),qt_add_command_callback)
    #@+node:ekr.20110605121601.18346: *6* add_separator (leoQtMenu)
    def add_separator(self,menu):

        """Wrapper for the Tkinter add_separator menu method."""

        if menu:
            action = menu.addSeparator()
            action.leo_menu_label = '*seperator*'
    #@+node:ekr.20110605121601.18347: *6* delete (leoQtMenu)
    def delete (self,menu,realItemName='<no name>'):

        """Wrapper for the Tkinter delete menu method."""

        # g.trace(menu)

        # if menu:
            # return menu.delete(realItemName)
    #@+node:ekr.20110605121601.18348: *6* delete_range (leoQtMenu)
    def delete_range (self,menu,n1,n2):

        """Wrapper for the Tkinter delete menu method."""

        # Menu is a subclass of QMenu and leoQtMenu.

        # g.trace(menu,n1,n2,g.callers(4))

        for z in menu.actions()[n1:n2]:
            menu.removeAction(z)
    #@+node:ekr.20110605121601.18349: *6* destroy (leoQtMenu)
    def destroy (self,menu):

        """Wrapper for the Tkinter destroy menu method."""

        # Fixed bug https://bugs.launchpad.net/leo-editor/+bug/1193870
        if menu:
            menu.menuBar.removeAction(menu.menuAction())
    #@+node:ekr.20110605121601.18350: *6* index (leoQtMenu)
    def index (self,label):

        '''Return the index of the menu with the given label.'''
        # g.trace(label)

        return 0
    #@+node:ekr.20110605121601.18351: *6* insert (leoQtMenu)
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
    #@+node:ekr.20110605121601.18352: *6* insert_cascade (leoQtMenu)
    def insert_cascade (self,parent,index,label,menu,underline):

        """Wrapper for the Tkinter insert_cascade menu method."""

        menu.setTitle(label)

        label.replace('&','').lower()
        menu.leo_menu_label = label # was leo_label

        if parent:
            parent.addMenu(menu)
        else:
            self.menuBar.addMenu(menu)

        action = menu.menuAction()
        if action:
            action.leo_menu_label = label
        else:
            g.trace('no action for menu',label)

        return menu
    #@+node:ekr.20110605121601.18353: *6* new_menu (leoQtMenu)
    def new_menu(self,parent,tearoff=False,label=''): # label is for debugging.

        """Wrapper for the Tkinter new_menu menu method."""

        c = self.c ; leoFrame = self.frame

        # g.trace(parent,label)

        # Parent can be None, in which case it will be added to the menuBar.
        menu = qtMenuWrapper(c,leoFrame,parent,label)

        return menu
    #@+node:ekr.20110605121601.18354: *5* Methods with other spellings (leoQtmenu)
    #@+node:ekr.20110605121601.18355: *6* clearAccel
    def clearAccel(self,menu,name):

        pass

        # if not menu:
            # return

        # realName = self.getRealMenuName(name)
        # realName = realName.replace("&","")

        # menu.entryconfig(realName,accelerator='')
    #@+node:ekr.20110605121601.18356: *6* createMenuBar (leoQtmenu)
    def createMenuBar(self,frame):

        '''Create all top-level menus.
        The menuBar itself has already been created.'''

        self.createMenusFromTables()
    #@+node:ekr.20110605121601.18357: *6* createOpenWithMenu (leoQtMenu)
    def createOpenWithMenu(self,parent,label,index,amp_index):

        '''Create the File:Open With submenu.

        This is called from leoMenu.createOpenWithMenuFromTable.'''

        # Use the existing Open With menu if possible.
        # g.trace(parent,label,index)

        menu = self.getMenu('openwith')

        if not menu:
            menu = self.new_menu(parent,tearoff=False,label=label)
            menu.insert_cascade(parent,index,
                label,menu,underline=amp_index)

        return menu
    #@+node:ekr.20110605121601.18358: *6* disable/enableMenu (leoQtMenu) (not used)
    def disableMenu (self,menu,name):
        self.enableMenu(menu,name,False)

    def enableMenu (self,menu,name,val):

        '''Enable or disable the item in the menu with the given name.'''

        trace = False and name.startswith('Paste') and not g.unitTesting

        if trace: g.trace(val,name,menu)

        if menu and name:
            val = bool(val)
            # g.trace('%5s %s %s' % (val,name,menu))
            for action in menu.actions():
                s = g.toUnicode(action.text()).replace('&','')
                if s.startswith(name):
                    action.setEnabled(val)
                    break
            else:
                if trace: g.trace('not found:',name)
    #@+node:ekr.20110605121601.18359: *6* getMenuLabel
    def getMenuLabel (self,menu,name):

        '''Return the index of the menu item whose name (or offset) is given.
        Return None if there is no such menu item.'''

        # At present, it is valid to always return None.
    #@+node:ekr.20110605121601.18360: *6* setMenuLabel
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
    #@+node:ekr.20110605121601.18361: *4* leoQtMenu.activateMenu & helper
    def activateMenu (self,menuName):

        '''Activate the menu with the given name'''

        menu = self.getMenu(menuName)
            # Menu is a qtMenuWrapper, a subclass of both QMenu and leoQtMenu.
        g.trace(menu)
        if menu:
            self.activateAllParentMenus(menu)
        else:       
            g.trace('No such menu: %s' % (menuName))
    #@+node:ekr.20120922041923.10607: *5* activateAllParentMenus
    def activateAllParentMenus (self,menu):

        '''menu is a qtMenuWrapper.  Activate it and all parent menus.'''

        parent = menu.parent()
        action = menu.menuAction()
        # g.trace(parent,action)
        if action:
            if parent and isinstance(parent,QtGui.QMenuBar):
                parent.setActiveAction(action)
            elif parent:
                self.activateAllParentMenus(parent)
                parent.setActiveAction(action)
            else:
                g.trace('can not happen: no parent for %s' % (menu))
        else:
            g.trace('can not happen: no action for %s' % (menu))
    #@+node:ekr.20120922041923.10613: *4* leoQtMenu.deactivateMenuBar
    # def deactivateMenuBar (self):

        # '''Activate the menu with the given name'''

        # menubar = self.c.frame.top.leo_menubar
        # menubar.setActiveAction(None)
        # menubar.repaint()
    #@+node:ekr.20110605121601.18362: *4* getMacHelpMenu
    def getMacHelpMenu (self,table):

        return None
    #@-others
#@+node:ekr.20110605121601.18363: *3* class LeoQTreeWidget (QTreeWidget)
class LeoQTreeWidget(QtGui.QTreeWidget):

    # To do: Generate @auto or @file nodes when appropriate.

    def __init__(self,c,parent):

        QtGui.QTreeWidget.__init__(self, parent)
        self.setAcceptDrops(True)
        enable_drag = c.config.getBool('enable-tree-dragging')
        # g.trace(enable_drag,c)
        self.setDragEnabled(enable_drag)
        self.c = c
        self.trace = False

    def __repr__(self):
        return 'LeoQTreeWidget: %s' % id(self)

    __str__ = __repr__

    # This is called during drags.
    def dragMoveEvent(self,ev):
        pass

    #@+others
    #@+node:ekr.20111022222228.16980: *4* Event handlers (LeoQTreeWidget)
    #@+node:ekr.20110605121601.18364: *5* dragEnterEvent
    def dragEnterEvent(self,ev):

        '''Export c.p's tree as a Leo mime-data.'''

        trace = False and not g.unitTesting
        c = self.c
        if not ev:
            g.trace('no event!')
            return
        md = ev.mimeData()
        if not md:
            g.trace('No mimeData!')
            return
        c.endEditing()
        # if g.app.dragging:
            # if trace or self.trace: g.trace('** already dragging')
        # g.app.dragging = True
        g.app.drag_source = c, c.p
        # if self.trace: g.trace('set g.app.dragging')
        self.setText(md)
        if self.trace: self.dump(ev,c.p,'enter')
        # Always accept the drag, even if we are already dragging.
        ev.accept()
    #@+node:ekr.20110605121601.18365: *5* dropEvent & helpers
    def dropEvent(self,ev):

        trace = False and not g.unitTesting
        if not ev: return
        c = self.c ; tree = c.frame.tree
        # Always clear the dragging flag, no matter what happens.
        # g.app.dragging = False
        # if self.trace: g.trace('clear g.app.dragging')
        # Set p to the target of the drop.
        item = self.itemAt(ev.pos())
        if not item: return
        itemHash = tree.itemHash(item)
        p = tree.item2positionDict.get(itemHash)
        if not p:
            if trace or self.trace: g.trace('no p!')
            return
        md = ev.mimeData()
        #print "drop md",mdl
        if not md:
            g.trace('no mimeData!') ; return
        # g.trace("t",str(md.text()))
        # g.trace("h", str(md.html()))
        formats = set(str(f) for f in md.formats())
        ev.setDropAction(QtCore.Qt.IgnoreAction)
        ev.accept()
        hookres = g.doHook("outlinedrop",c=c,p=p,dropevent=ev,formats=formats)
        if hookres:
            # True => plugins handled the drop already
            return
        if trace or self.trace: self.dump(ev,p,'drop ')
        if md.hasUrls():
            self.urlDrop(ev,p)
        else:
            self.outlineDrop(ev,p)
    #@+node:ekr.20110605121601.18366: *6* outlineDrop & helpers
    def outlineDrop (self,ev,p):

        trace = False and not g.unitTesting
        c = self.c
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
                as_child = (int(mods) & QtCore.Qt.AltModifier) != 0
                self.intraFileDrop(cloneDrag,fn,c.p,p,as_child)
        else:
            # Clone dragging between files is not allowed.
            self.interFileDrop(fn,p,s)
    #@+node:ekr.20110605121601.18367: *7* interFileDrop
    def interFileDrop (self,fn,p,s):

        '''Paste the mime data after (or as the first child of) p.'''

        trace = False and not g.unitTesting
        c = self.c
        u = c.undoer
        undoType = 'Drag Outline'
        isLeo = g.match(s,0,g.app.prolog_prefix_string)
        if not isLeo: return
        c.selectPosition(p)
        pasted = c.fileCommands.getLeoOutlineFromClipboard(
            s,reassignIndices=True)
        if not pasted:
            if trace: g.trace('not pasted!')
            return
        if trace: g.trace('pasting...')
        if c.config.getBool('inter_outline_drag_moves'):
            src_c, src_p = g.app.drag_source
            if src_p.hasVisNext(src_c):
                nxt = src_p.getVisNext(src_c).v
            elif src_p.hasVisBack(src_c):
                nxt = src_p.getVisBack(src_c).v
            else:
                nxt = None
            if nxt is not None:
                src_p.doDelete()
                src_c.selectPosition(src_c.vnode2position(nxt))
                src_c.setChanged(True)
                src_c.redraw()
            else:
                g.es("Can't move last node out of outline")
        undoData = u.beforeInsertNode(p,
            pasteAsClone=False,copiedBunchList=[])
        c.validateOutline()
        c.selectPosition(pasted)
        pasted.setDirty()
        pasted.setAllAncestorAtFileNodesDirty() # 2011/02/27: Fix bug 690467.
        c.setChanged(True)
        back = pasted.back()
        if back and back.isExpanded():
            pasted.moveToNthChildOf(back,0)
        # c.setRootPosition(c.findRootPosition(pasted))
        u.afterInsertNode(pasted,undoType,undoData)
        c.redraw_now(pasted)
        c.recolor()
    #@+node:ekr.20110605121601.18368: *7* intraFileDrop
    def intraFileDrop (self,cloneDrag,fn,p1,p2,as_child=False):

        '''Move p1 after (or as the first child of) p2.'''

        c = self.c ; u = c.undoer
        c.selectPosition(p1)
        if as_child or p2.hasChildren() and p2.isExpanded():
            # Attempt to move p1 to the first child of p2.
            # parent = p2
            def move(p1,p2):
                if cloneDrag: p1 = p1.clone()
                p1.moveToNthChildOf(p2,0)
                p1.setDirty()
                p1.setAllAncestorAtFileNodesDirty() # 2011/02/27: Fix bug 690467.
                return p1
        else:
            # Attempt to move p1 after p2.
            # parent = p2.parent()
            def move(p1,p2):
                if cloneDrag: p1 = p1.clone()
                p1.moveAfter(p2)
                p1.setDirty()
                p1.setAllAncestorAtFileNodesDirty() # 2011/02/27: Fix bug 690467.
                return p1
        ok = (
            # 2011/10/03: Major bug fix.
            c.checkDrag(p1,p2) and
            c.checkMoveWithParentWithWarning(p1,p2,True))
        # g.trace(ok,cloneDrag)
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
        elif not g.unitTesting:
            g.trace('** move failed')
    #@+node:ekr.20110605121601.18369: *6* urlDrop & helpers
    def urlDrop (self,ev,p):

        c = self.c ; u = c.undoer ; undoType = 'Drag Urls'
        md = ev.mimeData()
        urls = md.urls()
        if not urls:
            return
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
    #@+node:ekr.20110605121601.18370: *7* doFileUrl & helper
    def doFileUrl (self,p,url):

        fn = str(url.path())
        if sys.platform.lower().startswith('win'):
            if fn.startswith('/'):
                fn = fn[1:]
        if os.path.isdir(fn):
            self.doPathUrlHelper(fn,p)
            return True
        if g.os_path_exists(fn):
            try:
                f = open(fn,'rb') # 2012/03/09: use 'rb'
            except IOError:
                f = None
            if f:
                s = f.read()
                s = g.toUnicode(s)
                f.close()
                self.doFileUrlHelper(fn,p,s)
                return True
        g.es_print('not found: %s' % (fn))
        return False
    #@+node:ekr.20110605121601.18371: *8* doFileUrlHelper & helper
    def doFileUrlHelper (self,fn,p,s):

        '''Insert s in an @file, @auto or @edit node after p.'''

        c = self.c
        u,undoType = c.undoer,'Drag File'
        undoData = u.beforeInsertNode(p,pasteAsClone=False,copiedBunchList=[])
        if p.hasChildren() and p.isExpanded():
            p2 = p.insertAsNthChild(0)
        else:
            p2 = p.insertAfter()
        self.createAtFileNode(fn,p2,s)
        u.afterInsertNode(p2,undoType,undoData)
        c.selectPosition(p2)
    #@+node:ekr.20110605121601.18372: *9* createAtFileNode & helpers
    def createAtFileNode (self,fn,p,s):

        '''Set p's headline, body text and possibly descendants
        based on the file's name fn and contents s.

        If the file is an thin file, create an @file tree.
        Othewise, create an @auto tree.
        If all else fails, create an @auto node.

        Give a warning if a node with the same headline already exists.
        '''

        c = self.c
        c.init_error_dialogs()
        if self.isThinFile(fn,s):
            self.createAtFileTree(fn,p,s)
        elif self.isAutoFile(fn):
            self.createAtAutoTree(fn,p)
        elif self.isBinaryFile(fn):
            self.createUrlForBinaryFile(fn,p)
        else:
            self.createAtEditNode(fn,p)
        self.warnIfNodeExists(p)
        c.raise_error_dialogs(kind='read')
    #@+node:ekr.20110605121601.18373: *10* createAtAutoTree
    def createAtAutoTree (self,fn,p):

        '''Make p an @auto node and create the tree using
        s, the file's contents.
        '''

        c = self.c ; at = c.atFileCommands

        p.h = '@auto %s' % (fn)

        at.readOneAtAutoNode(fn,p)

        # No error recovery should be needed here.

        p.clearDirty() # Don't automatically rewrite this node.
    #@+node:ekr.20110605121601.18374: *10* createAtEditNode
    def createAtEditNode(self,fn,p):

        c = self.c ; at = c.atFileCommands

        # Use the full @edit logic, so dragging will be
        # exactly the same as reading.
        at.readOneAtEditNode(fn,p)
        p.h = '@edit %s' % (fn)
        p.clearDirty() # Don't automatically rewrite this node.
    #@+node:ekr.20110605121601.18375: *10* createAtFileTree
    def createAtFileTree (self,fn,p,s):

        '''Make p an @file node and create the tree using
        s, the file's contents.
        '''

        c = self.c ; at = c.atFileCommands

        p.h = '@file %s' % (fn)

        # Read the file into p.
        ok = at.read(root=p.copy(),
            importFileName=None,
            fromString=s,
            atShadow=False,
            force=True) # Disable caching.

        if not ok:
            g.error('Error reading',fn)
            p.b = '' # Safe: will not cause a write later.
            p.clearDirty() # Don't automatically rewrite this node.
    #@+node:ekr.20120309075544.9882: *10* createUrlForBinaryFile
    def createUrlForBinaryFile(self,fn,p):

        # Fix bug 1028986: create relative urls when dragging binary files to Leo.
        c = self.c
        base_fn = g.os_path_normcase(g.os_path_abspath(c.mFileName))
        abs_fn  = g.os_path_normcase(g.os_path_abspath(fn))
        prefix = os.path.commonprefix([abs_fn,base_fn])
        if prefix and len(prefix) > 3: # Don't just strip off c:\.
            p.h = abs_fn[len(prefix):].strip()
        else:
            p.h = '@url file://%s' % fn
        
    #@+node:ekr.20110605121601.18377: *10* isAutoFile
    def isAutoFile (self,fn):

        '''Return true if the file whose name is fn
        can be parsed with an @auto parser.
        '''

        c = self.c
        d = c.importCommands.importDispatchDict
        junk,ext = g.os_path_splitext(fn)
        return d.get(ext)
    #@+node:ekr.20120309075544.9881: *10* isBinaryFile
    def isBinaryFile(self,fn):

        # The default for unknown files is True. Not great, but safe.
        junk,ext = g.os_path_splitext(fn)
        ext = ext.lower()
        if not ext:
            val = False
        elif ext.startswith('~'):
            val = False
        elif ext in ('.css','.htm','.html','.leo','.txt'):
            val = False
        # elif ext in ('.bmp','gif','ico',):
            # val = True
        else:
            keys = (z.lower() for z in g.app.extension_dict.keys())
            val = ext not in keys

        # g.trace('binary',ext,val)
        return val
    #@+node:ekr.20110605121601.18376: *10* isThinFile
    def isThinFile (self,fn,s):

        '''Return true if the file whose contents is s
        was created from an @thin or @file tree.'''

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
    #@+node:ekr.20110605121601.18378: *10* warnIfNodeExists
    def warnIfNodeExists (self,p):

        c = self.c ; h = p.h
        for p2 in c.all_unique_positions():
            if p2.h == h and p2 != p:
                g.warning('Warning: duplicate node:',h)
                break
    #@+node:ekr.20110605121601.18379: *8* doPathUrlHelper
    def doPathUrlHelper (self,fn,p):

        '''Insert fn as an @path node after p.'''
        
        c = self.c
        u,undoType = c.undoer,'Drag Directory'
        undoData = u.beforeInsertNode(p,pasteAsClone=False,copiedBunchList=[])
        if p.hasChildren() and p.isExpanded():
            p2 = p.insertAsNthChild(0)
        else:
            p2 = p.insertAfter()
        p2.h = '@path ' + fn
        u.afterInsertNode(p2,undoType,undoData)
        c.selectPosition(p2)
    #@+node:ekr.20110605121601.18380: *7* doHttpUrl
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
    #@+node:ekr.20110605121601.18381: *4* utils...
    #@+node:ekr.20110605121601.18382: *5* dump
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
    #@+node:ekr.20110605121601.18383: *5* parseText
    def parseText (self,md):

        '''Parse md.text() into (fn,s)'''

        fn = ''
        # Fix bug 1046195: character encoding changes when dragging outline between leo files
        s = g.toUnicode(md.text(),'utf-8')
        if s:
            i = s.find(',')
            if i == -1:
                pass
            else:
                fn = s[:i]
                s = s[i+1:]
        return fn,s
    #@+node:ekr.20110605121601.18384: *5* setText & fileName
    def fileName (self):

        return self.c.fileName() or '<unsaved file>'

    def setText (self,md):

        c = self.c
        fn = self.fileName()
        s = c.fileCommands.putLeoOutline()
        if not g.isPython3:
            s = g.toEncodedString(s,encoding='utf-8',reportErrors=True)
            fn = g.toEncodedString(fn,encoding='utf-8', reportErrors=True)
        md.setText('%s,%s' % (fn,s))
    #@-others
#@+node:ekr.20110605121601.18385: *3* class leoQtSpellTab
class leoQtSpellTab:

    #@+others
    #@+node:ekr.20110605121601.18386: *4* leoQtSpellTab.__init__
    def __init__ (self,c,handler,tabName):

        # g.trace('(leoQtSpellTab)')
        self.c = c
        self.handler = handler
        # hack:
        handler.workCtrl = leoFrame.stringTextWidget(c, 'spell-workctrl')
        self.tabName = tabName
        ui = c.frame.top.leo_ui
        # self.createFrame()
        if not hasattr(ui, 'leo_spell_label'):
            self.handler.loaded = False
            return
        self.wordLabel = ui.leo_spell_label
        self.listBox = ui.leo_spell_listBox
        self.fillbox([])
    #@+node:ekr.20110605121601.18389: *4* Event handlers
    #@+node:ekr.20110605121601.18390: *5* onAddButton
    def onAddButton(self):
        """Handle a click in the Add button in the Check Spelling dialog."""

        self.handler.add()
    #@+node:ekr.20110605121601.18391: *5* onChangeButton & onChangeThenFindButton
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
    #@+node:ekr.20110605121601.18392: *5* onFindButton
    def onFindButton(self):

        """Handle a click in the Find button in the Spell tab."""

        c = self.c
        self.handler.find()
        self.updateButtons()
        c.invalidateFocus()
        c.bodyWantsFocus()
    #@+node:ekr.20110605121601.18393: *5* onHideButton
    def onHideButton(self):

        """Handle a click in the Hide button in the Spell tab."""

        self.handler.hide()
    #@+node:ekr.20110605121601.18394: *5* onIgnoreButton
    def onIgnoreButton(self,event=None):

        """Handle a click in the Ignore button in the Check Spelling dialog."""

        self.handler.ignore()
    #@+node:ekr.20110605121601.18395: *5* onMap
    def onMap (self, event=None):
        """Respond to a Tk <Map> event."""

        self.update(show= False, fill= False)
    #@+node:ekr.20110605121601.18396: *5* onSelectListBox
    def onSelectListBox(self, event=None):
        """Respond to a click in the selection listBox."""

        c = self.c
        self.updateButtons()
        c.bodyWantsFocus()
    #@+node:ekr.20110605121601.18397: *4* Helpers
    #@+node:ekr.20110605121601.18398: *5* bringToFront
    def bringToFront (self):

        self.c.frame.log.selectTab('Spell')
    #@+node:ekr.20110605121601.18399: *5* fillbox
    def fillbox(self, alts, word=None):
        """Update the suggestions listBox in the Check Spelling dialog."""

        # ui = self.c.frame.top.leo_ui
        self.suggestions = alts
        if not word: word = ""
        self.wordLabel.setText("Suggestions for: " + word)
        self.listBox.clear()
        if len(self.suggestions):
            self.listBox.addItems(self.suggestions)
            self.listBox.setCurrentRow(0)
    #@+node:ekr.20110605121601.18400: *5* getSuggestion
    def getSuggestion(self):
        """Return the selected suggestion from the listBox."""

        idx = self.listBox.currentRow()
        value = self.suggestions[idx]
        return value
    #@+node:ekr.20110605121601.18401: *5* update (leoQtSpellTab)
    def update(self,show=True,fill=False):

        """Update the Spell Check dialog."""

        c = self.c

        if fill:
            self.fillbox([])

        self.updateButtons()

        if show:
            self.bringToFront()
            c.bodyWantsFocus()
    #@+node:ekr.20110605121601.18402: *5* updateButtons (spellTab)
    def updateButtons (self):

        """Enable or disable buttons in the Check Spelling dialog."""

        c = self.c

        ui = c.frame.top.leo_ui

        w = c.frame.body.bodyCtrl
        state = self.suggestions and w.hasSelection()

        ui.leo_spell_btn_Change.setDisabled(not state)
        ui.leo_spell_btn_FindChange.setDisabled(not state)

        return state
    #@-others
#@+node:ekr.20110605121601.18403: *3* class leoQtTree (baseNativeTree)
class leoQtTree (baseNativeTree.baseNativeTreeWidget):

    """Leo qt tree class, a subclass of baseNativeTreeWidget."""

    callbacksInjected = False # A class var.

    #@+others
    #@+node:ekr.20110605121601.18404: *4*  Birth (leoQtTree)
    #@+node:ekr.20110605121601.18405: *5* ctor (leoQtTree)
    def __init__(self,c,frame):

        # Init the base class.
        baseNativeTree.baseNativeTreeWidget.__init__(self,c,frame)

        # Components.
        self.headlineWrapper = leoQtHeadlineWidget # This is a class.
        self.treeWidget = w = frame.top.leo_ui.treeWidget # An internal ivar.
            # w is a LeoQTreeWidget, a subclass of QTreeWidget.
            
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
    #@+node:ekr.20110605121601.18406: *5* qtTree.initAfterLoad
    def initAfterLoad (self):

        '''Do late-state inits.'''

        # Called by Leo's core.
        c = self.c
        w = c.frame.top
        tw = self.treeWidget

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

        if newFilter:
            g.app.gui.setFilter(c,tw,self,tag='tree')
        else:
            self.ev_filter = leoQtEventFilter(c,w=self,tag='tree')
            tw.installEventFilter(self.ev_filter)
        # 2010/01/24: Do not set this here.
        # The read logic sets c.changed to indicate nodes have changed.
        # c.setChanged(False)
    #@+node:ekr.20110605121601.18407: *4* Widget-dependent helpers (leoQtTree)
    #@+node:ekr.20110605121601.18408: *5* Drawing
    def clear (self):
        '''Clear all widgets in the tree.'''
        w = self.treeWidget
        w.clear()

    def repaint (self):
        '''Repaint the widget.'''
        w = self.treeWidget
        w.repaint()
        w.resizeColumnToContents(0) # 2009/12/22
    #@+node:ekr.20110605121601.18409: *5* Icons (qtTree)
    #@+node:ekr.20110605121601.18410: *6* drawIcon
    def drawIcon (self,p):

        '''Redraw the icon at p.'''

        w = self.treeWidget
        itemOrTree = self.position2item(p) or w
        item = QtGui.QTreeWidgetItem(itemOrTree)
        icon = self.getIcon(p)
        self.setItemIcon(item,icon)

    #@+node:ekr.20110605121601.18411: *6* getIcon & helper (qtTree)
    def getIcon(self,p):

        '''Return the proper icon for position p.'''

        p.v.iconVal = val = p.v.computeIcon()
        return self.getCompositeIconImage(p,val)
    #@+node:ekr.20110605121601.18412: *7* getCompositeIconImage
    def getCompositeIconImage(self,p,val):

        trace = False and not g.unitTesting
        userIcons = self.c.editCommands.getIconList(p)
        
        # don't take this shortcut - not theme aware, see getImageImage()
        # which is called below - TNB 20130313
        # if not userIcons:
        #     # if trace: g.trace('no userIcons')
        #     return self.getStatusIconImage(p)

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
        pix.fill(QtGui.QColor(None))  # transparent fill, default it random noise
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
    #@+node:ekr.20110605121601.18413: *6* setItemIconHelper (qtTree)
    def setItemIconHelper (self,item,icon):

        # Generates an item-changed event.
        # g.trace(id(icon))
        if item:
            item.setIcon(0,icon)
    #@+node:ekr.20110605121601.18414: *5* Items
    #@+node:ekr.20110605121601.18415: *6* childIndexOfItem
    def childIndexOfItem (self,item):

        parent = item and item.parent()

        if parent:
            n = parent.indexOfChild(item)
        else:
            w = self.treeWidget
            n = w.indexOfTopLevelItem(item)

        return n

    #@+node:ekr.20110605121601.18416: *6* childItems
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
    #@+node:ekr.20110605121601.18417: *6* closeEditorHelper (leoQtTree)
    def closeEditorHelper (self,e,item):

        w = self.treeWidget

        if e:
            # g.trace(g.callers(5))
            w.closeEditor(e,QtGui.QAbstractItemDelegate.NoHint)
            w.setCurrentItem(item)
    #@+node:ekr.20110605121601.18418: *6* connectEditorWidget & helper
    def connectEditorWidget(self,e,item):

        if not e: return g.trace('can not happen: no e')

        # Hook up the widget.
        wrapper = self.getWrapper(e,item)

        def editingFinishedCallback(e=e,item=item,self=self,wrapper=wrapper):
            # g.trace(wrapper,g.callers(5))
            c = self.c
            w = self.treeWidget
            self.onHeadChanged(p=c.p,e=e)
            w.setCurrentItem(item)

        e.connect(e,QtCore.SIGNAL(
            "editingFinished()"),
            editingFinishedCallback)
        return wrapper # 2011/02/12
    #@+node:ekr.20110605121601.18419: *6* contractItem & expandItem
    def contractItem (self,item):

        # g.trace(g.callers(4))

        self.treeWidget.collapseItem(item)

    def expandItem (self,item):

        # g.trace(g.callers(4))

        self.treeWidget.expandItem(item)
    #@+node:ekr.20110605121601.18420: *6* createTreeEditorForItem (leoQtTree)
    def createTreeEditorForItem(self,item):

        trace = False and not g.unitTesting

        w = self.treeWidget
        w.setCurrentItem(item) # Must do this first.
        w.editItem(item)
        e = w.itemWidget(item,0)
        e.setObjectName('headline')
        wrapper = self.connectEditorWidget(e,item)

        if trace: g.trace(e,wrapper)

        return e,wrapper
    #@+node:ekr.20110605121601.18421: *6* createTreeItem
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
    #@+node:ekr.20110605121601.18422: *6* editLabelHelper (leoQtTree)
    def editLabelHelper (self,item,selectAll=False,selection=None):

        '''Called by nativeTree.editLabel to do
        gui-specific stuff.'''

        trace = False and not g.unitTesting
        w = self.treeWidget
        w.setCurrentItem(item)
            # Must do this first.
            # This generates a call to onTreeSelect.
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
            wrapper = self.connectEditorWidget(e,item) # Hook up the widget.
        if trace: g.trace(e,wrapper)
        return e,wrapper # 2011/02/11
    #@+node:ekr.20110605121601.18423: *6* getCurrentItem
    def getCurrentItem (self):

        w = self.treeWidget
        return w.currentItem()
    #@+node:ekr.20110605121601.18424: *6* getItemText
    def getItemText (self,item):

        '''Return the text of the item.'''

        if item:
            return g.u(item.text(0))
        else:
            return '<no item>'
    #@+node:ekr.20110605121601.18425: *6* getParentItem
    def getParentItem(self,item):

        return item and item.parent()
    #@+node:ekr.20110605121601.18426: *6* getSelectedItems
    def getSelectedItems(self):
        w = self.treeWidget    
        return w.selectedItems()
    #@+node:ekr.20110605121601.18427: *6* getTreeEditorForItem (leoQtTree)
    def getTreeEditorForItem(self,item):

        '''Return the edit widget if it exists.
        Do *not* create one if it does not exist.'''

        trace = False and not g.unitTesting
        w = self.treeWidget
        e = w.itemWidget(item,0)
        if trace and e: g.trace(e.__class__.__name__)
        return e
    #@+node:ekr.20110605121601.18428: *6* getWrapper (leoQtTree)
    def getWrapper (self,e,item):

        '''Return headlineWrapper that wraps e (a QLineEdit).'''

        trace = False and not g.unitTesting
        verbose = True
        c = self.c

        if e:
            wrapper = self.editWidgetsDict.get(e)
            if wrapper:
                if trace and verbose: g.trace('old wrapper',e,wrapper)
            else:
                if item:
                    # 2011/02/12: item can be None.
                    wrapper = self.headlineWrapper(c,item,name='head',widget=e)
                    if trace: g.trace('new wrapper',e,wrapper,g.callers())
                    self.editWidgetsDict[e] = wrapper
                else:
                    if trace: g.trace('no item and no wrapper',
                        e,self.editWidgetsDict)
            return wrapper
        else:
            g.trace('no e')
            return None
    #@+node:ekr.20110605121601.18429: *6* nthChildItem
    def nthChildItem (self,n,parent_item):

        children = self.childItems(parent_item)

        if n < len(children):
            item = children[n]
        else:
            # This is **not* an error.
            # It simply means that we need to redraw the tree.
            item = None

        return item
    #@+node:ekr.20110605121601.18430: *6* scrollToItem (leoQtTree)
    def scrollToItem (self,item):

        w = self.treeWidget

        # g.trace(self.traceItem(item),g.callers(4))

        hPos,vPos = self.getScroll()

        w.scrollToItem(item,w.PositionAtCenter)

        self.setHScroll(0)
    #@+node:ekr.20110605121601.18431: *6* setCurrentItemHelper (leoQtTree)
    def setCurrentItemHelper(self,item):

        w = self.treeWidget
        w.setCurrentItem(item)
    #@+node:ekr.20110605121601.18432: *6* setItemText
    def setItemText (self,item,s):

        if item:
            item.setText(0,s)
    #@+node:ekr.20110605121601.18433: *5* Scroll bars (leoQtTree)
    #@+node:ekr.20110605121601.18434: *6* getSCroll
    def getScroll (self):

        '''Return the hPos,vPos for the tree's scrollbars.'''

        w = self.treeWidget
        hScroll = w.horizontalScrollBar()
        vScroll = w.verticalScrollBar()
        hPos = hScroll.sliderPosition()
        vPos = vScroll.sliderPosition()
        return hPos,vPos
    #@+node:ekr.20110605121601.18435: *6* setH/VScroll
    def setHScroll (self,hPos):
        w = self.treeWidget
        hScroll = w.horizontalScrollBar()
        hScroll.setValue(hPos)

    def setVScroll (self,vPos):
        # g.trace(vPos)
        w = self.treeWidget
        vScroll = w.verticalScrollBar()
        vScroll.setValue(vPos)
    #@+node:btheado.20111110215920.7164: *6* scrollDelegate (leoQtTree)
    def scrollDelegate (self,kind):

        '''Scroll a QTreeWidget up or down or right or left.
        kind is in ('down-line','down-page','up-line','up-page', 'right', 'left')
        '''
        c = self.c ; w = self.treeWidget
        if kind in ('left', 'right'):
            hScroll = w.horizontalScrollBar()
            if kind == 'right':
                delta = hScroll.pageStep()
            else: 
                delta = -hScroll.pageStep()
            hScroll.setValue(hScroll.value() + delta)
        else:
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
    #@+node:ekr.20110605121601.18437: *5* onContextMenu (leoQtTree)
    def onContextMenu(self, point):
        c = self.c
        w = self.treeWidget
        handlers = g.tree_popup_handlers    
        menu = QtGui.QMenu()
        menuPos = w.mapToGlobal(point)
        if not handlers:
            menu.addAction("No popup handlers")
        p = c.p.copy()
        done = set()
        for h in handlers:
            # every handler has to add it's QActions by itself
            if h in done:
                # do not run the same handler twice
                continue
            h(c,p,menu)
        menu.popup(menuPos)
        self._contextmenu = menu
    #@-others
#@+node:ekr.20110605121601.18438: *3* class leoQtTreeTab
class leoQtTreeTab:

    '''A class representing a so-called tree-tab.

    Actually, it represents a combo box'''

    #@+others
    #@+node:ekr.20110605121601.18439: *4*  Birth & death
    #@+node:ekr.20110605121601.18440: *5*  ctor (leoTreeTab)
    def __init__ (self,c,iconBar):

        # g.trace('(leoTreeTab)',g.callers(4))

        self.c = c
        self.cc = c.chapterController
        assert self.cc
        self.iconBar = iconBar
        self.lockout = False # True: do not redraw.
        self.tabNames = []
            # The list of tab names. Changes when tabs are renamed.
        self.w = None # The QComboBox

        self.createControl()
    #@+node:ekr.20110605121601.18441: *5* tt.createControl (defines class LeoQComboBox)
    def createControl (self):
        
        class LeoQComboBox(QtGui.QComboBox):
            '''Create a subclass in order to handle focusInEvents.'''
            def __init__(self,tt):
                self.leo_tt = tt
                QtGui.QComboBox.__init__(self) # Init the base class.
            def focusInEvent(self,event):
                self.leo_tt.setNames()
                QtGui.QComboBox.focusInEvent(self,event) # Call the base class

        tt = self
        frame = QtGui.QLabel('Chapters: ')
        tt.iconBar.addWidget(frame)
        tt.w = w = LeoQComboBox(tt)
        tt.setNames()
        tt.iconBar.addWidget(w)
        def onIndexChanged(s,tt=tt):
            if s:
                tt.cc.selectChapterLockout = True
                try:
                    s = g.u(s)
                    tt.selectTab(s)
                finally:
                    tt.cc.selectChapterLockout = False
        w.connect(w,QtCore.SIGNAL("currentIndexChanged(QString)"),
            onIndexChanged)
    #@+node:ekr.20110605121601.18442: *4* Tabs...
    #@+node:ekr.20110605121601.18443: *5* tt.createTab
    def createTab (self,tabName,select=True):

        tt = self
        # Avoid a glitch during initing.
        if tabName != 'main' and tabName not in tt.tabNames:
            tt.tabNames.append(tabName)
            tt.setNames()
    #@+node:ekr.20110605121601.18444: *5* tt.destroyTab
    def destroyTab (self,tabName):

        tt = self
        if tabName in tt.tabNames:
            tt.tabNames.remove(tabName)
            tt.setNames()
    #@+node:ekr.20110605121601.18445: *5* tt.selectTab
    def selectTab (self,tabName):

        tt,c,cc = self,self.c,self.cc
        exists = tabName in self.tabNames
        if not exists:
            tt.createTab(tabName) # Calls tt.setNames()
        if not tt.lockout:
            cc.selectChapterByName(tabName)
            c.redraw()
            c.outerUpdate()
    #@+node:ekr.20110605121601.18446: *5* tt.setTabLabel
    def setTabLabel (self,tabName):

        tt,w = self,self.w
        i = w.findText (tabName)
        if i > -1:
            w.setCurrentIndex(i)
    #@+node:ekr.20110605121601.18447: *5* tt.setNames
    def setNames (self):

        '''Recreate the list of items.'''

        tt,w = self,self.w
        names = self.cc.setAllChapterNames()
        w.clear()
        w.insertItems(0,names)
    #@-others
#@+node:ekr.20110605121601.18448: *3* class LeoTabbedTopLevel (QtGui.QTabWidget)
class LeoTabbedTopLevel(QtGui.QTabWidget):
    """ Toplevel frame for tabbed ui """

    #@+others
    #@+node:ekr.20110605121601.18449: *4* __init__ (LeoTabbedTopLevel)
    def __init__(self, *args, **kwargs):

        self.factory = kwargs['factory']
        del kwargs['factory']
        QtGui.QTabWidget.__init__(self)
        self.detached = []
        self.setMovable(True)
        def tabContextMenu(point):
            index = self.tabBar().tabAt(point)
            if index < 0 or (self.count() < 2 and not self.detached):
                return
            menu = QtGui.QMenu()
            if self.count() > 1:
                a = menu.addAction("Detach")
                a.connect(a, QtCore.SIGNAL("triggered()"),
                    lambda: self.detach(index))
                a = menu.addAction("Horizontal tile")
                a.connect(a, QtCore.SIGNAL("triggered()"),
                    lambda: self.tile(index, orientation='H'))
                a = menu.addAction("Vertical tile")
                a.connect(a, QtCore.SIGNAL("triggered()"),
                    lambda: self.tile(index, orientation='V'))
            if self.detached:
                a = menu.addAction("Re-attach All")
                a.connect(a, QtCore.SIGNAL("triggered()"), self.reattach_all)
            menu.exec_(self.mapToGlobal(point))
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.connect(self,
            QtCore.SIGNAL("customContextMenuRequested(QPoint)"), tabContextMenu)
    #@+node:ekr.20110605121601.18450: *4* detach
    def detach(self, index):
        """detach tab (from tab's context menu)"""
        w = self.widget(index)
        name = self.tabText(index)
        self.detached.append((name, w))
        self.factory.detachTab(w)
        
        icon = g.app.gui.getImageImageFinder("application-x-leo-outline.png")
        icon = QtGui.QIcon(icon)
        
        w.window().setWindowIcon(icon)
        
        c = w.leo_c
       
        sheet = c.config.getData('qt-gui-plugin-style-sheet')
        
        if sheet:
            if '\n' in sheet[0]:
                sheet = ''.join(sheet)
            else:
                sheet = '\n'.join(sheet)
            c.active_stylesheet = sheet
            sheet = g.expand_css_constants(sheet, c.font_size_delta)
            w.setStyleSheet(sheet)
        else:
            main = g.app.gui.frameFactory.masterFrame
            w.setStyleSheet(main.styleSheet())
            
        def reattach(event, w=w, name=name, tabManager=self):
            tabManager.detached = [i for i in tabManager.detached
                                   if i[1] != w]
            w.closeEvent = w.defaultClose
            tabManager.addTab(w, name)
            tabManager.factory.leoFrames[w] = w.leo_c.frame
            event.ignore()

        w.defaultClose = w.closeEvent
        w.closeEvent = reattach
        if platform.system() == 'Windows':
            w.move(20, 20)  # Windows (XP and 7) conspire to place the windows title bar off screen
            
        return w
    #@+node:tbrown.20120112093714.27963: *4* tile
    def tile(self, index, orientation='V'):
        """detach tab and tile with parent window"""
        w = self.widget(index)
        window = w.window()
        # window.showMaximized()
        # this doesn't happen until we've returned to main even loop
        # user needs to do it before using this function
        fg = window.frameGeometry()
        geom = window.geometry()
        x,y,fw,fh = fg.x(),fg.y(),fg.width(),fg.height()
        ww, wh = geom.width(), geom.height()
        w = self.detach(index)
        if window.isMaximized():
            window.showNormal()
        if orientation == 'V':
            # follow MS Windows convention for which way is horizontal/vertical
            window.resize(ww/2, wh)
            window.move(x, y)
            w.resize(ww/2, wh)
            w.move(x+fw/2, y)
        else:
            window.resize(ww, wh/2)
            window.move(x, y)
            w.resize(ww, wh/2)
            w.move(x, y+fh/2)
    #@+node:ekr.20110605121601.18451: *4* reattach_all
    def reattach_all(self):
        """reattach all detached tabs"""
        for name, w in self.detached:
            self.addTab(w, name)
            self.factory.leoFrames[w] = w.leo_c.frame
        self.detached = []
    #@+node:ekr.20110605121601.18452: *4* delete (LeoTabbedTopLevel)
    def delete(self, w):
        """called by TabbedFrameFactory to tell us a detached tab
        has been deleted"""
        self.detached = [i for i in self.detached if i[1] != w]
    #@+node:ekr.20110605121601.18453: *4* setChanged (LeoTabbedTopLevel)
    def setChanged (self,c,changed):

        # 2011/03/01: Find the tab corresponding to c.
        trace = False and not g.unitTesting
        dw = c.frame.top # A DynamicWindow
        i = self.indexOf(dw)
        if i < 0: return
        s = self.tabText(i)
        s = g.u(s)
        # g.trace('LeoTabbedTopLevel',changed,repr(s),g.callers())
        if len(s) > 2:
            if changed:
                if not s.startswith('* '):
                    title = "* " + s
                    self.setTabText(i,title)
                    if trace: g.trace(title)
            else:
                if s.startswith('* '):
                    title = s[2:]
                    self.setTabText(i,title)
                    if trace: g.trace(title)
    #@+node:ekr.20110605121601.18454: *4* setTabName (LeoTabbedTopLevel)
    def setTabName (self,c,fileName):

        '''Set the tab name for c's tab to fileName.'''

        # Find the tab corresponding to c.
        dw = c.frame.top # A DynamicWindow
        i = self.indexOf(dw)
        if i > -1:
            self.setTabText(i,g.shortFileName(fileName))
    #@+node:ekr.20110605121601.18455: *4* closeEvent (leoTabbedTopLevel)
    def closeEvent(self, event):

        noclose = False

        # g.trace('(leoTabbedTopLevel)',g.callers())

        if g.app.save_session and g.app.sessionManager:
            g.app.sessionManager.save_snapshot()

        for c in g.app.commanders():
            res = c.exists and g.app.closeLeoWindow(c.frame)
            if not res:
                noclose = True

        if noclose:
            event.ignore()
        else:            
            event.accept()
    #@+node:ekr.20110605121601.18456: *4* select (leoTabbedTopLevel)
    def select (self,c):

        '''Select the tab for c.'''

        # g.trace(c.frame.title,g.callers())
        dw = c.frame.top # A DynamicWindow
        i = self.indexOf(dw)
        self.setCurrentIndex(i)
        # Fix bug 844953: tell Unity which menu to use.
        c.enableMenuBar()
    #@-others
#@+node:ekr.20110605121601.18458: *3* class qtMenuWrapper (QMenu,leoQtMenu)
class qtMenuWrapper (QtGui.QMenu,leoQtMenu):

    #@+others
    #@+node:ekr.20110605121601.18459: *4* ctor and __repr__(qtMenuWrapper)
    def __init__ (self,c,frame,parent,label):

        assert c
        assert frame

        if parent is None:
            parent = c.frame.top.menuBar()

        # g.trace('(qtMenuWrapper) label: %s parent: %s' % (label,parent))

        QtGui.QMenu.__init__(self,parent)
        leoQtMenu.__init__(self,frame,label)

        label = label.replace('&','').lower()
        self.leo_menu_label = label

        action = self.menuAction()
        if action:
            action.leo_menu_label = label

        # g.trace('(qtMenuWrappter)',label)

        self.connect(self,QtCore.SIGNAL(
            "aboutToShow ()"),self.onAboutToShow)

    def __repr__(self):

        return '<qtMenuWrapper %s>' % self.leo_menu_label
    #@+node:ekr.20110605121601.18460: *4* onAboutToShow & helpers (qtMenuWrapper)
    def onAboutToShow(self,*args,**keys):

        trace = False and not g.unitTesting
        name = self.leo_menu_label
        if not name: return
        for action in self.actions():
            commandName = hasattr(action,'leo_command_name') and action.leo_command_name
            if commandName:
                if trace: g.trace(commandName)
                self.leo_update_shortcut(action,commandName)
                self.leo_enable_menu_item(action,commandName)
                self.leo_update_menu_label(action,commandName)

    #@+node:ekr.20120120095156.10261: *5* leo_enable_menu_item
    def leo_enable_menu_item (self,action,commandName):

        func = self.c.frame.menu.enable_dict.get(commandName)

        if action and func:
            val = func()
            # g.trace('%5s %20s %s' % (val,commandName,val))
            action.setEnabled(bool(val))

    #@+node:ekr.20120124115444.10190: *5* leo_update_menu_label
    def leo_update_menu_label(self,action,commandName):

        c = self.c

        if action and commandName == 'mark':
            action.setText('UnMark' if c.p.isMarked() else 'Mark')
            self.leo_update_shortcut(action,commandName)
                # Set the proper shortcut.
    #@+node:ekr.20120120095156.10260: *5* leo_update_shortcut
    def leo_update_shortcut(self,action,commandName):

        trace = False and not g.unitTesting
        c = self.c ; k = c.k

        if action:
            s = action.text()
            parts = s.split('\t')
            if len(parts) >= 2: s = parts[0]
            key,aList = c.config.getShortcut(commandName)
            if aList:
                result = []
                for si in aList:
                    assert g.isShortcutInfo(si),si
                    # Don't show mode-related bindings.
                    if not si.isModeBinding():
                        accel = k.prettyPrintKey(si.stroke)
                        if trace: g.trace('%20s %s' % (accel,si.dump()))
                        result.append(accel)
                        # Break here if we want to show only one accerator.
                action.setText('%s\t%s' % (s,', '.join(result)))
            else:
                action.setText(s)
        else:
            g.trace('can not happen: no action for %s' % (commandName))
    #@-others
#@+node:ekr.20110605121601.18461: *3* class qtSearchWidget
class qtSearchWidget:

    """A dummy widget class to pass to Leo's core find code."""

    def __init__ (self):

        self.insertPoint = 0
        self.selection = 0,0
        self.bodyCtrl = self
        self.body = self
        self.text = None
#@+node:ekr.20110605121601.18462: *3* class SDIFrameFactory
class SDIFrameFactory:
    """ 'Toplevel' frame builder 

    This only deals with Qt level widgets, not Leo wrappers
    """

    #@+others
    #@+node:ekr.20110605121601.18463: *4* createFrame (SDIFrameFactory)
    def createFrame(self, leoFrame):

        c = leoFrame.c
        dw = DynamicWindow(c)    
        dw.construct()
        g.app.gui.attachLeoIcon(dw)
        dw.setWindowTitle(leoFrame.title)
        if newFilter:
            g.app.gui.setFilter(c,dw,dw,tag='sdi-frame')
        else:
            # g.trace('(SDIFrameFactory)',g.callers())
            dw.ev_filter = leoQtEventFilter(c,w=dw,tag='sdi-frame')
            dw.installEventFilter(dw.ev_filter)
        if g.app.start_minimized:
            dw.showMinimized()
        elif g.app.start_maximized:
            dw.showMaximized()
        elif g.app.start_fullscreen:
            dw.showFullScreen()
        else:
            dw.show()
        return dw

    def deleteFrame(self, wdg):
        # Do not delete.  Called from destroySelf.
        pass
    #@-others
#@+node:ekr.20110605121601.18464: *3* class TabbedFrameFactory
class TabbedFrameFactory:
    """ 'Toplevel' frame builder for tabbed toplevel interface

    This causes Leo to maintain only one toplevel window,
    with multiple tabs for documents
    """

    #@+others
    #@+node:ekr.20110605121601.18466: *4* createFrame (TabbedFrameFactory)
    def createFrame(self, leoFrame):

        # g.trace('*** (TabbedFrameFactory)')
        c = leoFrame.c
        if self.masterFrame is None:
            self.createMaster()
        tabw = self.masterFrame
        dw = DynamicWindow(c,tabw)
        self.leoFrames[dw] = leoFrame
        # Shorten the title.
        title = os.path.basename(c.mFileName) if c.mFileName else leoFrame.title
        tip = leoFrame.title
        dw.setWindowTitle(tip) # 2010/1/1
        idx = tabw.addTab(dw, title)
        if tip: tabw.setTabToolTip(idx, tip)
        dw.construct(master=tabw)
        tabw.setCurrentIndex(idx)
        if newFilter:
            g.app.gui.setFilter(c,dw,dw,tag='tabbed-frame')
        else:
            # g.trace('(TabbedFrameFactor) adding bindings')
            dw.ev_filter = leoQtEventFilter(c,w=dw,tag='tabbed-frame')
            dw.installEventFilter(dw.ev_filter)
        # Work around the problem with missing dirty indicator
        # by always showing the tab.
        tabw.tabBar().setVisible(self.alwaysShowTabs or tabw.count() > 1)
        dw.show()
        tabw.show()
        return dw
    #@+node:ekr.20110605121601.18468: *4* createMaster (TabbedFrameFactory)
    def createMaster(self):
        mf = self.masterFrame = LeoTabbedTopLevel(factory=self)
        #g.trace('(TabbedFrameFactory) (sets tabbed geom)')
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
        if g.app.start_minimized:
            mf.showMinimized()
        elif g.app.start_maximized:
            mf.showMaximized()
        elif g.app.start_fullscreen:
            mf.showFullScreen()
        else:
            mf.show()
    #@+node:ekr.20110605121601.18472: *4* createTabCommands (TabbedFrameFactory)
    def detachTab(self, wdg):
        """ Detach specified tab as individual toplevel window """

        del self.leoFrames[wdg]
        wdg.setParent(None)
        wdg.show()

    def createTabCommands(self):
        #@+<< Commands for tabs >>
        #@+node:ekr.20110605121601.18473: *5* << Commands for tabs >>
        @g.command('tab-detach')
        def tab_detach(event):
            """ Detach current tab from tab bar """
            if len(self.leoFrames) < 2:
                g.es_print_error("Can't detach last tab")
                return

            c = event['c']
            f = c.frame
            tabwidget = g.app.gui.frameFactory.masterFrame
            tabwidget.detach(tabwidget.indexOf(f.top))
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
            # g.es("cur: %s, count: %s, offset: %s" % (cur,count,offset))
            cur += offset
            if cur < 0:
                cur = count -1
            elif cur >= count:
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
    #@+node:ekr.20110605121601.18465: *4* ctor (TabbedFrameFactory)
    def __init__(self):

        # will be created when first frame appears 

        # DynamicWindow => Leo frame map
        self.alwaysShowTabs = True
            # Set to true to workaround a problem
            # setting the window title when tabs are shown.
        self.leoFrames = {}
            # Keys are DynamicWindows, values are frames.
        self.masterFrame = None
        self.createTabCommands()

        # g.trace('(TabbedFrameFactory)',g.callers())
    #@+node:ekr.20110605121601.18467: *4* deleteFrame (TabbedFrameFactory)
    def deleteFrame(self, wdg):

        trace = False and not g.unitTesting
        if not wdg: return
        if wdg not in self.leoFrames:
            # probably detached tab
            self.masterFrame.delete(wdg)
            return
        if trace: g.trace('old',wdg.leo_c.frame.title)
            # wdg is a DynamicWindow.
        tabw = self.masterFrame
        idx = tabw.indexOf(wdg)
        tabw.removeTab(idx)
        del self.leoFrames[wdg]
        wdg2 = tabw.currentWidget()
        if wdg2:
            if trace: g.trace('new',wdg2 and wdg2.leo_c.frame.title)
            g.app.selectLeoWindow(wdg2.leo_c)
        tabw.tabBar().setVisible(self.alwaysShowTabs or tabw.count() > 1)
    #@+node:ekr.20110605121601.18471: *4* focusCurrentBody (TabbedFrameFactory)
    def focusCurrentBody(self):
        """ Focus body control of current tab """
        tabw = self.masterFrame
        w = tabw.currentWidget()
        w.setFocus()
        f = self.leoFrames[w]
        c = f.c
        c.bodyWantsFocusNow()

        # Fix bug 690260: correct the log.
        g.app.log = f.log
    #@+node:ekr.20110605121601.18469: *4* setTabForCommander (TabbedFrameFactory)
    def setTabForCommander (self,c):

        tabw = self.masterFrame # a QTabWidget

        for dw in self.leoFrames: # A dict whose keys are DynamicWindows.
            if dw.leo_c == c:
                for i in range(tabw.count()):
                    if tabw.widget(i) == dw:
                        tabw.setCurrentIndex(i)
                        break
                break

    #@+node:ekr.20110605121601.18470: *4* signal handlers (TabbedFrameFactory)
    def slotCloseRequest(self,idx):

        trace = False and not g.unitTesting
        tabw = self.masterFrame
        w = tabw.widget(idx)
        f = self.leoFrames[w]
        c = f.c
        if trace: g.trace(f.title)
        c.close(new_c=None)
            # 2012/03/04: Don't set the frame here.
            # Wait until the next slotCurrentChanged event.
            # This keeps the log and the QTabbedWidget in sync.

    def slotCurrentChanged(self, idx):

        # Two events are generated, one for the tab losing focus,
        # and another event for the tab gaining focus.
        trace = False and not g.unitTesting
        tabw = self.masterFrame
        w = tabw.widget(idx)
        f = self.leoFrames.get(w)
        if f:
            if trace: g.trace(f.title)
            tabw.setWindowTitle(f.title)
            g.app.selectLeoWindow(f.c)
                # 2012/03/04: Set the frame now.
    #@-others
#@+node:ekr.20110605121601.18474: ** Gui wrapper
#@+node:ekr.20110605121601.18475: *3* class leoQtGui
class leoQtGui(leoGui.leoGui):

    '''A class implementing Leo's Qt gui.'''

    #@+others
    #@+node:ekr.20110605121601.18476: *4*   Birth & death (qtGui)
    #@+node:ekr.20110605121601.18477: *5*  qtGui.__init__ (qtGui)
    def __init__ (self):

        # Initialize the base class.
        leoGui.leoGui.__init__(self,'qt')
        # g.trace('(qtGui)',g.callers())
        self.qtApp = QtGui.QApplication(sys.argv)
        self.bodyTextWidget  = leoQtBaseTextWidget
        self.iconimages = {}
        self.insert_char_flag = False # A flag for eventFilter.
        self.plainTextWidget = leoQtBaseTextWidget
        self.mGuiName = 'qt'
        self.color_theme = g.app.config and g.app.config.getString('color_theme') or None
        # Communication between idle_focus_helper and activate/deactivate events.
        self.active = True
        # Put up the splash screen()
        if (g.app.use_splash_screen and
            not g.app.batchMode and
            not g.app.silentMode and
            not g.unitTesting
        ):
            self.splashScreen = self.createSplashScreen()
        if g.app.qt_use_tabs:    
            self.frameFactory = TabbedFrameFactory()
        else:
            self.frameFactory = SDIFrameFactory()
    #@+node:ekr.20110605121601.18483: *5* runMainLoop & runWithIpythonKernel (qtGui)
    #@+node:ekr.20130930062914.16000: *6* qtGui.runMainLoop
    def runMainLoop(self):

        '''Start the Qt main loop.'''

        g.app.gui.dismiss_splash_screen()
        if self.script:
            log = g.app.log
            if log:
                g.pr('Start of batch script...\n')
                log.c.executeScript(script=self.script)
                g.pr('End of batch script')
            else:
                g.pr('no log, no commander for executeScript in qtGui.runMainLoop')
        elif g.app.useIpython:
            self.runWithIpythonKernel()
        else:
            # This can be alarming when using Python's -i option.                           
            sys.exit(self.qtApp.exec_())
    #@+node:ekr.20130930062914.16001: *6* qtGui.runWithIpythonKernel & helper
    def runWithIpythonKernel(self):
        '''Init Leo to run in an IPython shell.'''
        import leo.core.leoIPython as leoIPython
        if not leoIPython.IPKernelApp:
            return # leoIPython.py gives an error message.
        try:
            g.app.ipk = ipk = leoIPython.InternalIPKernel()
            ipk.new_qt_console(event=None)
                # ipk.ipkernel is an IPKernelApp.
        except Exception:
            g.es_exception()
            print('can not init leo.core.leoIPython.py')
            self.runMainLoop()

        @g.command("ipython-new")
        def qtshell_f(event):            
            """ Launch new ipython shell window, associated with the same ipython kernel """
            g.app.ipk.new_qt_console(event=event)

        @g.command("ipython-exec")
        def ipython_exec_f(event):
            """ Execute script in current node in ipython namespace """
            self.exec_helper(event)

        # blocks forever, equivalent of QApplication.exec_()
        ipk.ipkernel.start()
    #@+node:ekr.20130930062914.16010: *7* exec_helper
    def exec_helper(self,event):
        '''This helper is required because an unqualified "exec"
        may not appear in a nested function.
        
        '''
        c = event and event.get('c')
        ipk = g.app.ipk
        ns = ipk.namespace # The actual IPython namespace.
        ipkernel = ipk.ipkernel # IPKernelApp
        shell = ipkernel.shell # ZMQInteractiveShell
        if c and ns is not None:
            try:
                script = g.getScript(c,c.p)
                if 1:
                    code = compile(script,c.p.h,'exec')
                    shell.run_code(code) # Run using IPython.
                else:
                    exec(script,ns) # Run in Leo in the IPython namespace.
            except Exception:
                g.es_exception()
            finally:
                sys.stdout.flush()
                # sys.stderr.flush()
    #@+node:ekr.20110605121601.18484: *5* destroySelf (qtGui)
    def destroySelf (self):
        QtCore.pyqtRemoveInputHook()
        self.qtApp.exit()
    #@+node:ekr.20111022215436.16685: *4* Borders (qtGui)
    #@+node:ekr.20120927164343.10092: *5* add_border (qtGui)
    def add_border(self,c,w):

        state = c.k and c.k.unboundKeyAction

        if state and c.use_focus_border:
        
            d = {
                'command':  c.focus_border_command_state_color,
                'insert':   c.focus_border_color,
                'overwrite':c.focus_border_overwrite_state_color,
            }
            color = d.get(state,c.focus_border_color)
            name = g.u(w.objectName())
            if name =='richTextEdit':
                w = c.frame.top.leo_body_inner_frame
                self.paint_qframe(w,color)
            elif name.startswith('head'):
                pass
            else:
                # Always use the default border color for the tree.
                color = c.focus_border_color
                sheet = "border: %spx solid %s" % (c.focus_border_width,color)
                self.update_style_sheet(w,'border',sheet,selector=w.__class__.__name__)
    #@+node:ekr.20120927164343.10093: *5* remove_border (qtGui)
    def remove_border(self,c,w):

        if not c.use_focus_border:
            return

        name = g.u(w.objectName())
        width = c.focus_border_width
        if w.objectName()=='richTextEdit':
            w = c.frame.top.leo_body_inner_frame
            self.paint_qframe(w,'white')
        elif name.startswith('head'):
            pass
        else:
            sheet = "border: %spx solid white" % width
            self.update_style_sheet(w,'border',sheet,selector=w.__class__.__name__)
    #@+node:ekr.20120927164343.10094: *5* paint_qframe (qtGui)
    def paint_qframe (self,w,color):

        assert isinstance(w,QtGui.QFrame)

        # How's this for a kludge.
        # Set this ivar for InnerBodyFrame.paintEvent.
        g.app.gui.innerBodyFrameColor = color
    #@+node:ekr.20110605121601.18485: *4* Clipboard (qtGui)
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
            if trace: g.trace(len(s),type(s),s[:25])
        else:
            g.trace('no clipboard!')

    def getTextFromClipboard (self):

        '''Get a unicode string from the clipboard.'''

        trace = False and not g.unitTesting
        cb = self.qtApp.clipboard()
        if cb:
            QtGui.QApplication.processEvents()
            s = cb.text()
            if trace: g.trace (len(s),type(s),s[:25])
            s = g.app.gui.toUnicode(s)
                # Same as g.u(s), but with error handling.
            return s
        else:
            g.trace('no clipboard!')
            return ''
    #@+node:ekr.20110605121601.18487: *4* Dialogs & panels (qtGui)
    #@+node:ekr.20110605121601.18488: *5* alert (qtGui)
    def alert (self,c,message):

        if g.unitTesting: return

        b = QtGui.QMessageBox
        d = b(None)
        d.setWindowTitle('Alert')
        d.setText(message)
        d.setIcon(b.Warning)
        d.addButton('Ok',b.YesRole)
        c.in_qt_dialog = True
        d.exec_()
        c.in_qt_dialog = False
    #@+node:ekr.20110605121601.18489: *5* makeFilter
    def makeFilter (self,filetypes):

        '''Return the Qt-style dialog filter from filetypes list.'''

        filters = ['%s (%s)' % (z) for z in filetypes]

        return ';;'.join(filters)
    #@+node:ekr.20110605121601.18492: *5* qtGui panels
    def createComparePanel(self,c):

        """Create a qt color picker panel."""
        return None # This window is optional.
        # return leoQtComparePanel(c)

    def createFindTab (self,c,parentFrame):
        """Create a qt find tab in the indicated frame."""
        return leoQtFindTab(c,parentFrame)

    def createLeoFrame(self,c,title):
        """Create a new Leo frame."""
        gui = self
        return leoQtFrame(c,title,gui)

    def createSpellTab(self,c,spellHandler,tabName):
        return leoQtSpellTab(c,spellHandler,tabName)

    #@+node:ekr.20110605121601.18493: *5* runAboutLeoDialog
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
        c.in_qt_dialog = True
        d.exec_()
        c.in_qt_dialog = False
    #@+node:ekr.20110605121601.18496: *5* runAskDateTimeDialog
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
                    | QtGui.QDialogButtonBox.Cancel)
                layout.addWidget(buttonBox)

                self.connect(buttonBox, QtCore.SIGNAL("accepted()"),
                    self, QtCore.SLOT("accept()"))
                self.connect(buttonBox, QtCore.SIGNAL("rejected()"),
                    self, QtCore.SLOT("reject()"))

        if g.unitTesting: return None

        b = Calendar
        if not init:
            init = datetime.datetime.now()
        d = b(c.frame.top, message=message, init=init, step_min=step_min)

        d.setWindowTitle(title)

        c.in_qt_dialog = True
        val = d.exec_()
        c.in_qt_dialog = False

        if val != d.Accepted:
            return None
        else:
            return d.dt.dateTime().toPyDateTime()
    #@+node:ekr.20110605121601.18494: *5* runAskLeoIDDialog
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
    #@+node:ekr.20110605121601.18491: *5* runAskOkCancelNumberDialog (changed)
    def runAskOkCancelNumberDialog(self,c,title,message,cancelButtonText=None,okButtonText=None):

        """Create and run askOkCancelNumber dialog ."""

        if g.unitTesting: return None

        # n,ok = QtGui.QInputDialog.getDouble(None,title,message)
        d = QtGui.QInputDialog()
        d.setWindowTitle(title)
        d.setLabelText(message)
        if cancelButtonText:
            d.setCancelButtonText(cancelButtonText)
        if okButtonText:
            d.setOkButtonText(okButtonText)
        ok = d.exec_()
        n = d.textValue()
        try:
            n = float(n)
        except ValueError:
            n = None
        return n if ok else None
    #@+node:ekr.20110605121601.18490: *5* runAskOkCancelStringDialog (changed)
    def runAskOkCancelStringDialog(self,c,title,message,cancelButtonText=None,
                                   okButtonText=None,default=""):

        """Create and run askOkCancelString dialog ."""

        if g.unitTesting: return None

        d = QtGui.QInputDialog()
        d.setWindowTitle(title)
        d.setLabelText(message)
        d.setTextValue(default)
        if cancelButtonText:
            d.setCancelButtonText(cancelButtonText)
        if okButtonText:
            d.setOkButtonText(okButtonText)
        ok = d.exec_()
        return str(d.textValue()) if ok else None
    #@+node:ekr.20110605121601.18495: *5* runAskOkDialog
    def runAskOkDialog(self,c,title,message=None,text="Ok"):

        """Create and run a qt askOK dialog ."""

        if g.unitTesting: return None
        b = QtGui.QMessageBox
        d = b(c.frame.top)
        d.setWindowTitle(title)
        if message: d.setText(message)
        d.setIcon(b.Information)
        d.addButton(text,b.YesRole)
        c.in_qt_dialog = True
        d.exec_()
        c.in_qt_dialog = False
    #@+node:ekr.20110605121601.18497: *5* runAskYesNoCancelDialog
    def runAskYesNoCancelDialog(self,c,title,
        message=None,
        yesMessage="&Yes",
        noMessage="&No",
        yesToAllMessage=None,
        defaultButton="Yes"
    ):

        """Create and run an askYesNo dialog."""

        if g.unitTesting:
            return None
        b = QtGui.QMessageBox
        d = b(c.frame.top)
        if message: d.setText(message)
        d.setIcon(b.Warning)
        d.setWindowTitle(title)
        yes      = d.addButton(yesMessage,b.YesRole)
        no       = d.addButton(noMessage,b.NoRole)
        yesToAll = d.addButton(yesToAllMessage,b.YesRole) if yesToAllMessage else None
        cancel = d.addButton(b.Cancel)
        if   defaultButton == "Yes": d.setDefaultButton(yes)
        elif defaultButton == "No": d.setDefaultButton(no)
        else: d.setDefaultButton(cancel)
        c.in_qt_dialog = True
        val = d.exec_()
        c.in_qt_dialog = False
        if   val == 0: val = 'yes'
        elif val == 1: val = 'no'
        elif yesToAll and val == 2: val = 'yes-to-all'
        else: val = 'cancel'
        return val
    #@+node:ekr.20110605121601.18498: *5* runAskYesNoDialog
    def runAskYesNoDialog(self,c,title,message=None):

        """Create and run an askYesNo dialog."""

        if g.unitTesting: return None
        b = QtGui.QMessageBox
        d = b(c.frame.top)
        d.setWindowTitle(title)
        if message: d.setText(message)
        d.setIcon(b.Information)
        yes = d.addButton('&Yes',b.YesRole)
        d.addButton('&No',b.NoRole)
        d.setDefaultButton(yes)
        c.in_qt_dialog = True
        val = d.exec_()
        c.in_qt_dialog = False
        return 'yes' if val == 0 else 'no'
    #@+node:ekr.20110605121601.18499: *5* runOpenDirectoryDialog (qtGui)
    def runOpenDirectoryDialog(self,title,startdir):

        """Create and run an Qt open directory dialog ."""

        parent = None
        s = QtGui.QFileDialog.getExistingDirectory (parent,title,startdir)
        return g.u(s)
    #@+node:ekr.20110605121601.18500: *5* runOpenFileDialog (qtGui)
    def runOpenFileDialog(self,title,filetypes,defaultextension='',multiple=False,startpath=None):

        """Create and run an Qt open file dialog ."""

        if g.unitTesting:
            return ''
        else:
            if startpath is None:
                startpath = os.curdir

            parent = None
            filter = self.makeFilter(filetypes)

            if multiple:
                lst = QtGui.QFileDialog.getOpenFileNames(parent,title,startpath,filter)
                return [g.u(s) for s in lst]
            else:
                s = QtGui.QFileDialog.getOpenFileName(parent,title,startpath,filter)
                return g.u(s)
    #@+node:ekr.20110605121601.18501: *5* runPropertiesDialog (qtGui)
    def runPropertiesDialog(self,
        title='Properties',data={}, callback=None, buttons=None):

        """Dispay a modal TkPropertiesDialog"""

        # g.trace(data)
        g.warning('Properties menu not supported for Qt gui')
        result = 'Cancel'
        return result,data
    #@+node:ekr.20110605121601.18502: *5* runSaveFileDialog (qtGui)
    def runSaveFileDialog(self,initialfile='',title='Save',filetypes=[],defaultextension=''):

        """Create and run an Qt save file dialog ."""

        if g.unitTesting:
            return ''
        else:
            parent = None
            filter_ = self.makeFilter(filetypes)
            s = QtGui.QFileDialog.getSaveFileName(parent,title,os.curdir,filter_)
            return g.u(s)
    #@+node:ekr.20110605121601.18503: *5* runScrolledMessageDialog (qtGui)
    def runScrolledMessageDialog (self,
        short_title= '',
        title='Message',
        label= '',
        msg='',
        c=None,**kw
    ):

        if g.unitTesting: return None

        def send(title=title, label=label, msg=msg, c=c, kw=kw):
            return g.doHook('scrolledMessage',
                short_title=short_title,title=title,
                label=label, msg=msg,c=c, **kw)

        if not c or not c.exists:
            #@+<< no c error>>
            #@+node:ekr.20110605121601.18504: *6* << no c error>>
            g.es_print_error('%s\n%s\n\t%s' % (
                "The qt plugin requires calls to g.app.gui.scrolledMessageDialog to include 'c'",
                "as a keyword argument",
                g.callers()
            ))
            #@-<< no c error>>
        else:        
            retval = send()
            if retval: return retval
            #@+<< load viewrendered plugin >>
            #@+node:ekr.20110605121601.18505: *6* << load viewrendered plugin >>
            pc = g.app.pluginsController
            # 2011/10/20: load viewrendered (and call vr.onCreate)
            # *only* if not already loaded.
            if not pc.isLoaded('viewrendered.py'):
                vr = pc.loadOnePlugin('viewrendered.py')
                if vr:
                    g.blue('viewrendered plugin loaded.')
                    vr.onCreate('tag',{'c':c})
            #@-<< load viewrendered plugin >>
            retval = send()
            if retval: return retval
            #@+<< no dialog error >>
            #@+node:ekr.20110605121601.18506: *6* << no dialog error >>
            g.es_print_error(
                'No handler for the "scrolledMessage" hook.\n\t%s' % (
                    g.callers()))
            #@-<< no dialog error >>
        #@+<< emergency fallback >>
        #@+node:ekr.20110605121601.18507: *6* << emergency fallback >>
        b = QtGui.QMessageBox
        d = b(None) # c.frame.top)
        d.setWindowFlags(QtCore.Qt.Dialog)
            # That is, not a fixed size dialog.
        d.setWindowTitle(title)
        if msg: d.setText(msg)
        d.setIcon(b.Information)
        d.addButton('Ok',b.YesRole)
        c.in_qt_dialog = True
        d.exec_()
        c.in_qt_dialog = False
        #@-<< emergency fallback >>
    #@+node:ekr.20110607182447.16456: *4* Event handlers (qtGui)
    #@+node:ekr.20110605121601.18480: *5* onActivateEvent (qtGui)
    # Called from eventFilter

    def onActivateEvent (self,event,c,obj,tag):

        '''Put the focus in the body pane when the Leo window is
        activated, say as the result of an Alt-tab or click.'''

        # This is called several times for each window activation.
        # We only need to set the focus once.

        trace = False and not g.unitTesting

        if trace: g.trace(tag)

        if c.exists and tag == 'body':
            self.active = True
            # Retain the focus that existed when the deactivate event happened.
                # c.bodyWantsFocusNow()
            if c.p.v:
                c.p.v.restoreCursorAndScroll()
            g.doHook('activate',c=c,p=c.p,v=c.p,event=event)
    #@+node:ekr.20110605121601.18481: *5* onDeactiveEvent (qtGui)
    def onDeactivateEvent (self,event,c,obj,tag):

        '''Put the focus in the body pane when the Leo window is
        activated, say as the result of an Alt-tab or click.'''

        trace = False and not g.unitTesting

        # This is called several times for each window activation.
        # Save the headline only once.

        if c.exists and tag.startswith('tree'):
            self.active = False
            if trace: g.trace()
            c.k.keyboardQuit(setFocus=False)
                # 2011/06/13.
                # 2011/09/29. Don't change the tab in the log pane.
            # c.endEditing()
            g.doHook('deactivate',c=c,p=c.p,v=c.p,event=event)
    #@+node:ekr.20110605121601.18508: *4* Focus (qtGui)
    def get_focus(self,c=None):

        """Returns the widget that has focus."""

        trace = False and not g.unitTesting
        app = QtGui.QApplication
        w = app.focusWidget()
        if w and isinstance(w,LeoQTextBrowser):
            has_w = hasattr(w,'leo_wrapper') and w.leo_wrapper
            if has_w:
                if trace: g.trace(w)
            elif c:
                # Kludge: DynamicWindow creates the body pane
                # with wrapper = None, so return the leoQtBody.
                w = c.frame.body
        if trace: g.trace('(qtGui)',w,g.callers())
        return w

    def set_focus(self,c,w):

        """Put the focus on the widget."""

        trace = False and not g.unitTesting
        gui = self
        if w:
            if trace: g.trace('(qtGui)',w,g.callers())
            w.setFocus()

    def ensure_commander_visible(self, c1):
        """Check to see if c.frame is in a tabbed ui, and if so, make sure
        the tab is visible"""

        # START: copy from Code-->Startup & external files-->@file runLeo.py -->run & helpers-->doPostPluginsInit & helpers (runLeo.py)
        # For qttabs gui, select the first-loaded tab.
        if hasattr(g.app.gui,'frameFactory'):
            factory = g.app.gui.frameFactory
            if factory and hasattr(factory,'setTabForCommander'):
                c = c1
                factory.setTabForCommander(c)
                c.bodyWantsFocusNow()
        # END: copy
    #@+node:ekr.20110605121601.18509: *4* Font
    #@+node:ekr.20110605121601.18510: *5* qtGui.getFontFromParams
    def getFontFromParams(self,family,size,slant,weight,defaultSize=12):

        trace = False and not g.unitTesting

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
            if trace: g.trace(family,size,g.callers())
            return font
        except:
            g.es("exception setting font",g.callers(4))
            g.es("","family,size,slant,weight:","",family,"",size,"",slant,"",weight)
            # g.es_exception() # This just confuses people.
            return g.app.config.defaultFont
    #@+node:ekr.20110605121601.18511: *4* getFullVersion
    def getFullVersion (self,c=None):

        try:
            qtLevel = 'version %s' % QtCore.QT_VERSION_STR
        except Exception:
            # g.es_exception()
            qtLevel = '<qtLevel>'

        return 'qt %s' % (qtLevel)
    #@+node:ekr.20110605121601.18514: *4* Icons
    #@+node:ekr.20110605121601.18515: *5* attachLeoIcon (qtGui)
    def attachLeoIcon (self,window):

        """Attach a Leo icon to the window."""

        #icon = self.getIconImage('leoApp.ico')

        #window.setWindowIcon(icon)
        window.setWindowIcon(QtGui.QIcon(g.app.leoDir + "/Icons/leoapp32.png"))    
        #window.setLeoWindowIcon()
    #@+node:ekr.20110605121601.18516: *5* getIconImage (qtGui)
    def getIconImage (self,name):

        '''Load the icon and return it.'''

        trace = False and not g.unitTesting
        verbose = False

        # Return the image from the cache if possible.
        if name in self.iconimages:
            image = self.iconimages.get(name)
            if trace and verbose: # and not name.startswith('box'):
                g.trace('cached',id(image),name,image)
            return image
        try:
            iconsDir = g.os_path_join(g.app.loadDir,"..","Icons")
            homeIconsDir = g.os_path_join(g.app.homeLeoDir,"Icons")
            for theDir in (homeIconsDir,iconsDir):
                fullname = g.os_path_finalize_join(theDir,name)
                if g.os_path_exists(fullname):
                    if 0: # Not needed: use QTreeWidget.setIconsize.
                        pixmap = QtGui.QPixmap()
                        pixmap.load(fullname)
                        image = QtGui.QIcon(pixmap)
                    else:
                        image = QtGui.QIcon(fullname)
                        if trace: g.trace('name',fullname,'image',image)

                    self.iconimages[name] = image
                    if trace: g.trace('new',id(image),theDir,name)
                    return image
                elif trace: g.trace('Directory not found',theDir)
            else:
                if trace: g.trace('Not found',name)
                return None

        except Exception:
            g.es_print("exception loading:",fullname)
            g.es_exception()
            return None
    #@+node:ekr.20110605121601.18517: *5* getImageImage
    def getImageImage (self, name):
        '''Load the image in file named `name` and return it.
        
        If self.color_theme, set from @settings -> @string color_theme is set,
        
         - look first in $HOME/.leo/themes/<theme_name>/Icons,
         - then in .../leo/themes/<theme_name>/Icons,
         - then in .../leo/Icons,
         - as well as trying absolute path
        '''

        fullname = self.getImageImageFinder(name)

        try:
            pixmap = QtGui.QPixmap()
            pixmap.load(fullname)

            return pixmap

        except Exception:
            g.es("exception loading:",name)
            g.es_exception()
            return None

    #@+node:tbrown.20130316075512.28478: *5* getImageImageFinder
    def getImageImageFinder(self, name):
        '''Theme aware image (icon) path searching
        
        If self.color_theme, set from @settings -> @string color_theme is set,
        
         - look first in $HOME/.leo/themes/<theme_name>/Icons,
         - then in .../leo/themes/<theme_name>/Icons,
         - then in .../leo/Icons,
         - as well as trying absolute path
        '''

        if self.color_theme:
            
            # normal, unthemed path to image
            pathname = g.os_path_finalize_join(g.app.loadDir,"..","Icons")
            pathname = g.os_path_normpath(g.os_path_realpath(pathname))
            
            if g.os_path_isabs(name):
                testname = g.os_path_normpath(g.os_path_realpath(name))
            else:
                testname = name
                
            #D print(name, self.color_theme)
            #D print('pathname', pathname)
            #D print('testname', testname)
            
            if testname.startswith(pathname):
                # try after removing icons dir from path
                namepart = testname.replace(pathname, '').strip('\\/')
            else:
                namepart = testname
                
            # home dir first
            fullname = g.os_path_finalize_join(
                g.app.homeLeoDir, 'themes',
                self.color_theme, 'Icons', namepart)
                
            #D print('namepart', namepart)
            #D print('fullname', fullname)
            
            if g.os_path_exists(fullname):
                return fullname
                
            # then load dir
            fullname = g.os_path_finalize_join(
                g.app.loadDir, "..", 'themes',
                self.color_theme, 'Icons', namepart)
            
            #D print('fullname', fullname)
            
            if g.os_path_exists(fullname):
                return fullname

        # original behavior, if name is absolute this will just return it
        #D print(g.os_path_finalize_join(g.app.loadDir,"..","Icons",name))
        return g.os_path_finalize_join(g.app.loadDir,"..","Icons",name)
    #@+node:ekr.20110605121601.18518: *5* getTreeImage (test)
    def getTreeImage (self,c,path):

        image = QtGui.QPixmap(path)

        if image.height() > 0 and image.width() > 0:
            return image,image.height()
        else:
            return None,None
    #@+node:ekr.20110605121601.18519: *4* Idle Time (qtGui)
    #@+node:ekr.20110605121601.18520: *5* qtGui.setIdleTimeHook & setIdleTimeHookAfterDelay
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
    #@+node:ekr.20110605121601.18521: *5* qtGui.runAtIdle
    def runAtIdle (self,aFunc):

        '''This can not be called in some contexts.'''

        timer = QtCore.QTimer()
        timer.setSingleShot(True)

        # print('runAtIdle',aFunc)

        def atIdleCallback(aFunc=aFunc):
            print('atIdleCallBack',aFunc)
            aFunc()

        timer.connect(timer,QtCore.SIGNAL("timeout()"),atIdleCallback)

        # To make your application perform idle processing, use a QTimer with 0 timeout.
        timer.start(0)
    #@+node:ekr.20131007055150.17608: *4* insertKeyEvent (qtGui) (New in 4.11)
    def insertKeyEvent (self,event,i):
        
        '''Insert the key given by event in location i of widget event.w.'''
        
        import leo.core.leoGui as leoGui
        assert isinstance(event,leoGui.leoKeyEvent)
        qevent = event.event
        assert isinstance(qevent,QtGui.QKeyEvent)
        qw = hasattr(event.w,'widget') and event.w.widget or None
        if qw and isinstance(qw,QtGui.QTextEdit):
            g.trace(i,qevent.modifiers(),g.u(qevent.text()))
            if 1:
                # Assume that qevent.text() *is* the desired text.
                # This means we don't have to hack eventFilter.
                qw.insertPlainText(qevent.text())
            else:
                # Make no such assumption.
                # We would like to use qevent to insert the character,
                # but this would invoke eventFilter again!
                # So set this flag for eventFilter, which will
                # return False, indicating that the widget must handle
                # qevent, which *presumably* is the best that can be done.
                g.app.gui.insert_char_flag = True
    #@+node:ekr.20110605121601.18522: *4* isTextWidget (qtGui)
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

    #@+node:ekr.20110605121601.18528: *4* makeScriptButton (to do)
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
        #@+node:ekr.20110605121601.18529: *5* << create the button b >>
        iconBar = c.frame.getIconBarObject()
        b = iconBar.add(text=buttonText)
        #@-<< create the button b >>
        #@+<< define the callbacks for b >>
        #@+node:ekr.20110605121601.18530: *5* << define the callbacks for b >>
        def deleteButtonCallback(event=None,b=b,c=c):
            if b: b.pack_forget()
            c.bodyWantsFocus()

        def executeScriptCallback (event=None,
            b=b,c=c,buttonText=buttonText,p=p and p.copy(),script=script):

            if c.disableCommandsMessage:
                g.blue('',c.disableCommandsMessage)
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
        if shortcut:
            #@+<< bind the shortcut to executeScriptCallback >>
            #@+node:ekr.20110605121601.18531: *5* << bind the shortcut to executeScriptCallback >>
            func = executeScriptCallback
            shortcut = k.canonicalizeShortcut(shortcut)
            ok = k.bindKey ('button', shortcut,func,buttonText)
            if ok:
                g.blue('bound @button',buttonText,'to',shortcut)
            #@-<< bind the shortcut to executeScriptCallback >>
        #@+<< create press-buttonText-button command >>
        #@+node:ekr.20110605121601.18532: *5* << create press-buttonText-button command >>
        aList = [g.choose(ch.isalnum(),ch,'-') for ch in buttonText]

        buttonCommandName = ''.join(aList)
        buttonCommandName = buttonCommandName.replace('--','-')
        buttonCommandName = 'press-%s-button' % buttonCommandName.lower()

        # This will use any shortcut defined in an @shortcuts node.
        k.registerCommand(buttonCommandName,None,executeScriptCallback,pane='button',verbose=False)
        #@-<< create press-buttonText-button command >>
    #@+node:ekr.20111215193352.10220: *4* Splash Screen (qtGui)
    #@+node:ekr.20110605121601.18479: *5* createSplashScreen (qtGui)
    def createSplashScreen (self):

        qt = QtCore.Qt
        splash = None
        for name in (
            'SplashScreen.jpg','SplashScreen.png','SplashScreen.ico',
        ):
            fn = g.os_path_finalize_join(g.app.loadDir,'..','Icons',name)
            if g.os_path_exists(fn):
                pm = QtGui.QPixmap(fn)
                splash = QtGui.QSplashScreen(pm,(qt.SplashScreen | qt.WindowStaysOnTopHint))
                splash.show()
                # splash.repaint()
                # self.qtApp.processEvents()
                break
        return splash
    #@+node:ekr.20110613103140.16424: *5* dismiss_splash_screen (qtGui)
    def dismiss_splash_screen (self):

        # g.trace(g.callers())

        gui = self

        # Warning: closing the splash screen must be done in the main thread!
        if g.unitTesting:
            return

        if gui.splashScreen:
            gui.splashScreen.hide()
            # gui.splashScreen.deleteLater()
            gui.splashScreen = None
    #@+node:ekr.20110605121601.18523: *4* Style Sheets
    #@+node:ekr.20110605121601.18524: *5* setStyleSetting (qtGui)
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
    #@+node:ekr.20110605121601.18525: *5* setWidgetColor (qtGui)
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
            g.warning('bad widget color %s for %s' % (colorName,widgetKind))
    #@+node:ekr.20111026115337.16528: *5* update_style_sheet (qtGui)
    def update_style_sheet (self,w,key,value,selector=None):
        
        # NOT USED / DON'T USE - interferes with styles, zooming etc.

        trace = False and not g.unitTesting

        # Step one: update the dict.
        d = hasattr(w,'leo_styles_dict') and w.leo_styles_dict or {}
        d[key] = value
        aList = [d.get(z) for z in list(d.keys())]
        w.leo_styles_dict = d

        # Step two: update the stylesheet.
        s = '; '.join(aList)
        if selector:
            s = '%s { %s }' % (selector,s)
        old = str(w.styleSheet())
        if old == s:
            # if trace: g.trace('no change')
            return
        if trace:
            # g.trace('old: %s\nnew: %s' % (str(w.styleSheet()),s))
            g.trace(s)
        # This call is responsible for the unwanted scrolling!
        # To avoid problems, we now set the color of the innerBodyFrame without using style sheets.
        w.setStyleSheet(s)
    #@+node:ekr.20110605121601.18526: *4* toUnicode (qtGui)
    def toUnicode (self,s):

        try:
            s = g.u(s)
            return s
        except Exception:
            g.trace('*** Unicode Error: bugs possible')
            # The mass update omitted the encoding param.
            return g.toUnicode(s,reportErrors='replace')
    #@+node:ekr.20110605121601.18527: *4* widget_name (qtGui)
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
    #@+node:ekr.20111027083744.16532: *4* enableSignalDebugging (qtGui)
    # enableSignalDebugging(emitCall=foo) and spy your signals until you're sick to your stomach.

    _oldConnect     = QtCore.QObject.connect
    _oldDisconnect  = QtCore.QObject.disconnect
    _oldEmit        = QtCore.QObject.emit

    def _wrapConnect(self,callableObject):
        """Returns a wrapped call to the old version of QtCore.QObject.connect"""
        @staticmethod
        def call(*args):
            callableObject(*args)
            self._oldConnect(*args)
        return call

    def _wrapDisconnect(self,callableObject):
        """Returns a wrapped call to the old version of QtCore.QObject.disconnect"""
        @staticmethod
        def call(*args):
            callableObject(*args)
            self._oldDisconnect(*args)
        return call

    def enableSignalDebugging(self,**kwargs):

        """Call this to enable Qt Signal debugging. This will trap all
        connect, and disconnect calls."""

        f = lambda *args: None
        connectCall     = kwargs.get('connectCall', f)
        disconnectCall  = kwargs.get('disconnectCall', f)
        emitCall        = kwargs.get('emitCall', f)

        def printIt(msg):
            def call(*args):
                print(msg,args)
            return call

        # Monkey-patch.
        QtCore.QObject.connect    = self._wrapConnect(connectCall)
        QtCore.QObject.disconnect = self._wrapDisconnect(disconnectCall)

        def new_emit(self, *args):
            emitCall(self, *args)
            self._oldEmit(self, *args)

        QtCore.QObject.emit = new_emit
    #@+node:ekr.20130921043420.21175: *4* setFilter (qtGui)
    if newFilter:
        
        # ??? What do these types have in common???

        # w's type is in (DynamicWindow,,leoQtMinibuffer,leoQtLog,leoQtTree,
        # leoQTextEditWidget,LeoQTextBrowser,LeoQuickSearchWidget,cleoQtUI)

        def setFilter(self,c,obj,w,tag):
            
            '''Create an event filter in obj.
            w is a wrapper object, not necessarily a QWidget.'''
            if 0:
                g.trace(isinstance(w,QtGui.QWidget),
                    hasattr(w,'getName') and w.getName() or None,
                    w.__class__.__name__)
            if 0:
                g.trace('obj: %4s %20s w: %5s %s' % (
                    isinstance(obj,QtGui.QWidget),obj.__class__.__name__,
                    isinstance(w,QtGui.QWidget),w.__class__.__name__))
            assert isinstance(obj,QtGui.QWidget),obj
            gui = self
            theFilter = leoQtEventFilter(c,w=w,tag=tag)
            obj.installEventFilter(theFilter)
            w.ev_filter = theFilter
                # Set the official ivar in w.



    #@-others
#@+node:ekr.20110605121601.18533: ** Non-essential
#@+node:ekr.20110605121601.18534: *3* quickheadlines
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



#@+node:ekr.20110605121601.18537: ** class leoQtEventFilter
class leoQtEventFilter(QtCore.QObject):

    #@+<< about internal bindings >>
    #@+node:ekr.20110605121601.18538: *3* << about internal bindings >>
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
    #@+node:ekr.20110605121601.18539: *3*  ctor (leoQtEventFilter)
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

        # Support for ctagscompleter.py plugin.
        self.ctagscompleter_active = False
        self.ctagscompleter_onKey = None
    #@+node:ekr.20110605121601.18540: *3* eventFilter
    def eventFilter(self, obj, event):

        trace = (False or g.trace_masterKeyHandler) and not g.unitTesting
        verbose = False
        traceEvent = False # True: call self.traceEvent.
        traceKey = (True or g.trace_masterKeyHandler)
        c = self.c ; k = c.k
        eventType = event.type()
        ev = QtCore.QEvent
        gui = g.app.gui
        aList = []

        kinds = [ev.ShortcutOverride,ev.KeyPress,ev.KeyRelease]

        # Hack: QLineEdit generates ev.KeyRelease only on Windows,Ubuntu
        lineEditKeyKinds = [ev.KeyPress,ev.KeyRelease]

        # Important:
        # QLineEdit: ignore all key events except keyRelease events.
        # QTextEdit: ignore all key events except keyPress events.
        if eventType in lineEditKeyKinds:
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
            if self.tag in ('body','tree','log'):
                g.app.gui.remove_border(c,obj)
        elif eventType in kinds:
            tkKey,ch,ignore = self.toTkKey(event)
            aList = c.k.masterGuiBindingsDict.get('<%s>' %tkKey,[])
            # g.trace('instate',k.inState(),'tkKey',tkKey,'ignore',ignore,'len(aList)',len(aList))
            if ignore: override = False
            # This is extremely bad.
            # At present, it is needed to handle tab properly.
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
                    g.app.gui.add_border(c,obj)
                    c.frame.body.onFocusIn(obj)
                elif eventType == ev.FocusOut:
                    g.app.gui.remove_border(c,obj)
                    c.frame.body.onFocusOut(obj)
            elif self.tag in ('log','tree'):
                if eventType == ev.FocusIn:
                    g.app.gui.add_border(c,obj)
                elif eventType == ev.FocusOut:
                    g.app.gui.remove_border(c,obj)

        if self.keyIsActive:
            shortcut = self.toStroke(tkKey,ch) # ch is unused.
            if override:
                # Essentially *all* keys get passed to masterKeyHandler.
                if trace and traceKey:
                    g.trace('ignore',ignore,'bound',repr(shortcut),repr(aList))
                w = self.w # Pass the wrapper class, not the wrapped widget.
                qevent = event
                event = self.create_key_event(event,c,w,ch,tkKey,shortcut)
                k.masterKeyHandler(event)
                if g.app.gui.insert_char_flag:
                    # if trace and traceKey: g.trace('*** insert_char_flag',event.text())
                    g.trace('*** insert_char_flag',qevent.text())
                    g.app.gui.insert_char_flag = False
                    override = False # *Do* pass the character back to the widget!
                c.outerUpdate()
            else:
                if trace and traceKey and verbose:
                    g.trace(self.tag,'unbound',tkKey,shortcut)
            if trace and traceEvent:
                # Trace key events.
                self.traceEvent(obj,event,tkKey,override)
        elif trace and traceEvent:
            # Trace non-key events.
            self.traceEvent(obj,event,tkKey,override)
        return override
    #@+node:ekr.20110605195119.16937: *3* create_key_event (leoQtEventFilter)
    def create_key_event (self,event,c,w,ch,tkKey,shortcut):

        trace = False and not g.unitTesting ; verbose = False

        if trace and verbose: g.trace('ch: %s, tkKey: %s, shortcut: %s' % (
            repr(ch),repr(tkKey),repr(shortcut)))

        # Last-minute adjustments...
        if shortcut == 'Return':
            ch = '\n' # Somehow Qt wants to return '\r'.
        elif shortcut == 'Escape':
            ch = 'Escape'

        # Switch the Shift modifier to handle the cap-lock key.
        if len(ch) == 1 and len(shortcut) == 1 and ch.isalpha() and shortcut.isalpha():
            if ch != shortcut:
                if trace and verbose: g.trace('caps-lock')
                shortcut = ch

        # Patch provided by resi147.
        # See the thread: special characters in MacOSX, like '@'.
        if sys.platform.startswith('darwin'):
            darwinmap = {
                'Alt-Key-5': '[',
                'Alt-Key-6': ']',
                'Alt-Key-7': '|',
                'Alt-slash': '\\',
                'Alt-Key-8': '{',
                'Alt-Key-9': '}',
                'Alt-e': '€',
                'Alt-l': '@',
            }
            if tkKey in darwinmap:
                shortcut = darwinmap[tkKey]

        char = ch
        # Auxiliary info.
        x      = hasattr(event,'x') and event.x or 0
        y      = hasattr(event,'y') and event.y or 0
        # Support for fastGotoNode plugin
        x_root = hasattr(event,'x_root') and event.x_root or 0
        y_root = hasattr(event,'y_root') and event.y_root or 0

        if trace and verbose: g.trace('ch: %s, shortcut: %s printable: %s' % (
            repr(ch),repr(shortcut),ch in string.printable))

        return leoGui.leoKeyEvent(c,char,event,shortcut,w,x,y,x_root,y_root)
    #@+node:ekr.20120204061120.10088: *3* Key construction (leoQtEventFilter)
    #@+node:ekr.20110605121601.18543: *4* toTkKey & helpers (must not change!)
    def toTkKey (self,event):

        '''Return tkKey,ch,ignore:

        tkKey: the Tk spelling of the event used to look up
               bindings in k.masterGuiBindingsDict.
               **This must not ever change!**

        ch:    the insertable key, or ''.

        ignore: True if the key should be ignored.
                This is **not** the same as 'not ch'.
        '''

        mods = self.qtMods(event)

        keynum,text,toString,ch = self.qtKey(event)

        tkKey,ch,ignore = self.tkKey(
            event,mods,keynum,text,toString,ch)

        return tkKey,ch,ignore
    #@+node:ekr.20110605121601.18546: *5* tkKey & helper
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
            # 2011/05/17: Fix bug 681797.
            # There is nothing 'dubious' about these provided that they are bound.
            # If they are not bound, then weird characters will be inserted.
            'Delete','Ins','Backspace',
            'F1','F2','F3','F4','F5','F6','F7','F8','F9','F10','F11','F12',
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
    #@+node:ekr.20110605121601.18547: *6* char2tkName
    char2tkNameDict = {
        # Part 1: same as g.app.guiBindNamesDict
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
        'Tab':'Tab',
        # 'Tab':'\t', # A hack for QLineEdit.
        # Unused: Break, Caps_Lock,Linefeed,Num_lock
    }

    # Called only by tkKey.

    def char2tkName (self,ch):
        val = self.char2tkNameDict.get(ch)
        # g.trace(repr(ch),repr(val))
        return val
    #@+node:ekr.20120204061120.10087: *4* Common key construction helpers
    #@+node:ekr.20110605121601.18541: *5* isSpecialOverride
    def isSpecialOverride (self,tkKey,ch):

        '''Return True if tkKey is a special Tk key name.
        '''

        return tkKey or ch in self.flashers
    #@+node:ekr.20110605121601.18542: *5* toStroke (leoQtEventFilter)
    def toStroke (self,tkKey,ch):  # ch is unused

        '''Convert the official tkKey name to a stroke.'''

        trace = False and not g.unitTesting
        s = tkKey
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
    #@+node:ekr.20110605121601.18544: *5* qtKey
    def qtKey (self,event):

        '''Return the components of a Qt key event.

        Modifiers are handled separately.

        Return keynum,text,toString,ch

        keynum: event.key()
        ch:     g.u(chr(keynum)) or '' if there is an exception.
        toString:
            For special keys: made-up spelling that become part of the setting.
            For all others:   QtGui.QKeySequence(keynum).toString()
        text:   event.text()
        '''

        trace = False and not g.unitTesting
        keynum = event.key()
        text   = event.text() # This is the unicode text.

        qt = QtCore.Qt
        d = {
            qt.Key_Shift:   'Key_Shift',
            qt.Key_Control: 'Key_Control',  # MacOS: Command key
            qt.Key_Meta:	'Key_Meta',     # MacOS: Control key, Alt-Key on Microsoft keyboard on MacOs.
            qt.Key_Alt:	    'Key_Alt',	 
            qt.Key_AltGr:	'Key_AltGr',
                # On Windows, when the KeyDown event for this key is sent,
                # the Ctrl+Alt modifiers are also set.
        }

        if d.get(keynum):
            toString = d.get(keynum)
        else:
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

        if trace and self.keyIsActive:
            mods = '+'.join(self.qtMods(event))
            g.trace(
                'keynum %7x ch %3s toString %s %s' % (
                keynum,repr(ch),mods,repr(toString)))

        return keynum,text,toString,ch
    #@+node:ekr.20120204061120.10084: *5* qtMods
    def qtMods (self,event):

        '''Return the text version of the modifiers of the key event.'''

        modifiers = event.modifiers()

        # The order of this table must match the order created by k.strokeFromSetting.
        # When g.new_keys is True, k.strokeFromSetting will canonicalize the setting.

        qt = QtCore.Qt

        if sys.platform.startswith('darwin'):
            # Yet another MacOS hack:
            table = (
                (qt.AltModifier,     'Alt'), # For Apple keyboard.
                (qt.MetaModifier,    'Alt'), # For Microsoft keyboard.
                (qt.ControlModifier, 'Control'),
                # No way to generate Meta.
                (qt.ShiftModifier,   'Shift'),
            )

        else:
            table = (
                (qt.AltModifier,     'Alt'),
                (qt.ControlModifier, 'Control'),
                (qt.MetaModifier,    'Meta'),
                (qt.ShiftModifier,   'Shift'),
            )

        mods = [b for a,b in table if (modifiers & a)]
        return mods
    #@+node:ekr.20110605121601.18548: *3* traceEvent
    def traceEvent (self,obj,event,tkKey,override):

        if g.unitTesting: return

        traceFocus = False
        traceKey   = True
        traceLayout = False
        traceMouse = False

        c,e = self.c,QtCore.QEvent
        eventType = event.type()

        show = []

        ignore = [
            e.MetaCall, # 43
            e.Timer, # 1
            e.ToolTip, # 110
        ]

        focus_events = (
            (e.Enter,'enter'),
            (e.Leave,'leave'),
            (e.FocusIn,'focus-in'),
            (e.FocusOut,'focus-out'),
            (e.Hide,'hide'), # 18
            (e.HideToParent, 'hide-to-parent'), # 27
            (e.HoverEnter, 'hover-enter'), # 127
            (e.HoverLeave,'hover-leave'), # 128
            (e.HoverMove,'hover-move'), # 129
            (e.Show,'show'), # 17
            (e.ShowToParent,'show-to-parent'), # 26
            (e.WindowActivate,'window-activate'), # 24
            (e.WindowBlocked,'window-blocked'), # 103
            (e.WindowUnblocked,'window-unblocked'), # 104
            (e.WindowDeactivate,'window-deactivate'), # 25
        )
        key_events = (
            (e.KeyPress,'key-press'),
            (e.KeyRelease,'key-release'),
            (e.ShortcutOverride,'shortcut-override'),
        )
        layout_events = (
            (e.ChildPolished,'child-polished'), # 69
            #(e.CloseSoftwareInputPanel,'close-sip'), # 200
                # Event does not exist on MacOS.
            (e.ChildAdded,'child-added'), # 68
            (e.DynamicPropertyChange,'dynamic-property-change'), # 170
            (e.FontChange,'font-change'),# 97
            (e.LayoutRequest,'layout-request'),
            (e.Move,'move'), # 13 widget's position changed.
            (e.PaletteChange,'palette-change'),# 39
            (e.ParentChange,'parent-change'), # 21
            (e.Paint,'paint'), # 12
            (e.Polish,'polish'), # 75
            (e.PolishRequest,'polish-request'), # 74
            # (e.RequestSoftwareInputPanel,'sip'), # 199
                # Event does not exist on MacOS.
            (e.Resize,'resize'), # 14
            (e.StyleChange,'style-change'), # 100
            (e.ZOrderChange,'z-order-change'), # 126
        )
        mouse_events = (
            (e.MouseMove,'mouse-move'), # 155
            (e.MouseButtonPress,'mouse-press'), # 2
            (e.MouseButtonRelease,'mouse-release'), # 3
            (e.Wheel,'mouse-wheel'), # 31
        )

        option_table = (
            (traceFocus,focus_events),
            (traceKey,key_events),
            (traceLayout,layout_events),
            (traceMouse,mouse_events),
        )

        for option,table in option_table:
            if option:
                show.extend(table)
            else:
                for n,tag in table:
                    ignore.append(n)

        for val,kind in show:
            if eventType == val:
                g.trace(
                    '%5s %18s in-state: %5s key: %s override: %s: obj: %s' % (
                    self.tag,kind,repr(c.k and c.k.inState()),tkKey,override,obj))
                return

        if eventType not in ignore:
            g.trace('%3s:%s obj:%s' % (eventType,'unknown',obj))
    #@-others
#@+node:ekr.20110605121601.18550: ** Syntax coloring
#@+node:ekr.20110605121601.18551: *3* leoQtColorizer
# This is c.frame.body.colorizer

class leoQtColorizer:

    '''An adaptor class that interfaces Leo's core to two class:

    1. a subclass of QSyntaxHighlighter,

    2. the jEditColorizer class that contains the
       pattern-matchin code from the threading colorizer plugin.'''

    #@+others
    #@+node:ekr.20110605121601.18552: *4*  ctor (leoQtColorizer)
    def __init__ (self,c,w):

        # g.trace('(leoQtColorizer)',w)

        self.c = c
        self.w = w

        # Step 1: create the ivars.
        self.changingText = False
        self.count = 0 # For unit testing.
        self.colorCacheFlag = False
        self.enabled = c.config.getBool('use_syntax_coloring')
        self.error = False # Set if there is an error in jeditColorizer.recolor
        self.flag = True # Per-node enable/disable flag.
        self.full_recolor_count = 0 # For unit testing.
        self.killColorFlag = False
        self.language = 'python' # set by scanColorDirectives.
        self.languageList = [] # List of color directives in the node the determines it.
        self.max_chars_to_colorize = c.config.getInt('qt_max_colorized_chars') or 0
        self.oldLanguageList = []
        self.oldV = None
        self.showInvisibles = False # 2010/1/2

        # Step 2: create the highlighter.
        if PYTHON_COLORER:
            self.highlighter = LeoSyntaxHighlighter(c,w,colorizer=self)
        else:
            self.highlighter = leoQtSyntaxHighlighter(c,w,colorizer=self)
        self.colorer = self.highlighter.colorer
        w.leo_colorizer = self

        # Step 3: finish enabling.
        if self.enabled:
            self.enabled = hasattr(self.highlighter,'currentBlock')
    #@+node:ekr.20110605121601.18553: *4* colorize (leoQtColorizer) & helper
    def colorize(self,p,incremental=False,interruptable=True):

        '''The main colorizer entry point.'''

        trace = False and not g.unitTesting ; verbose = True

        self.count += 1 # For unit testing.
        if not incremental:
            self.full_recolor_count += 1

        if len(p.b) > self.max_chars_to_colorize > 0:
            self.flag = False
        elif self.enabled:
            oldFlag = self.flag
            self.updateSyntaxColorer(p)
                # sets self.flag and self.language and self.languageList.
            if trace and verbose:
                g.trace('old: %s, new: %s, %s' % (
                    self.oldLanguageList,self.languageList,repr(p.h)))

            # fullRecolor is True if we can not do an incremental recolor.
            fullRecolor = (
                oldFlag != self.flag or
                self.oldV != p.v or
                self.oldLanguageList != self.languageList or
                not incremental
            )

            # 2012/03/09: Determine the present language from the insertion
            # point if there are more than one @language directives in effect
            # and we are about to do an incremental recolor.
            if len(self.languageList) > 0 and not fullRecolor:
                language = self.scanColorByPosition(p) # May reset self.language
                if language != self.colorer.language_name:
                    if trace: g.trace('** must rescan',self.c.frame.title,language)
                    fullRecolor = True
                    self.language = language

            if fullRecolor:
                if trace: g.trace('** calling rehighlight',g.callers())
                self.oldLanguageList = self.languageList[:]
                self.oldV = p.v
                self.highlighter.rehighlight(p)

        return "ok" # For unit testing.
    #@+node:ekr.20120309075544.9888: *5* scanColorByPosition (leoQtColorizer)
    def scanColorByPosition(self,p):

        c = self.c
        w = c.frame.body.bodyCtrl
        i = w.getInsertPoint()
        s = w.getAllText()

        i1,i2 = g.getLine(s,i)
        tag = '@language'
        language = self.language
        for s in g.splitLines(s[:i1]):
            if s.startswith(tag):
                language = s[len(tag):].strip()

        return language

    #@+node:ekr.20110605121601.18554: *4* enable/disable
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
    #@+node:ekr.20110605121601.18556: *4* scanColorDirectives (leoQtColorizer) & helper
    def scanColorDirectives(self,p):

        '''Set self.language based on the directives in p's tree.'''

        trace = False and not g.unitTesting
        c = self.c
        if c == None: return None # self.c may be None for testing.
        root = p.copy()
        self.colorCacheFlag = False
        self.language = None
        self.rootMode = None # None, "code" or "doc"
        for p in root.self_and_parents():
            theDict = g.get_directives_dict(p)
            # if trace: g.trace(p.h,theDict)
            #@+<< Test for @colorcache >>
            #@+node:ekr.20121003152523.10126: *5* << Test for @colorcache >>
            # The @colorcache directive is a per-node directive.
            if p == root:
                self.colorCacheFlag = 'colorcache' in theDict
                # g.trace('colorCacheFlag: %s' % self.colorCacheFlag)
            #@-<< Test for @colorcache >>
            #@+<< Test for @language >>
            #@+node:ekr.20110605121601.18557: *5* << Test for @language >>
            if 'language' in theDict:
                s = theDict["language"]
                aList = self.findLanguageDirectives(p)
                # In the root node, we use the first (valid) @language directive,
                # no matter how many @language directives the root node contains.
                # In ancestor nodes, only unambiguous @language directives
                # set self.language.
                if p == root or len(aList) == 1:
                    self.languageList = aList
                    self.language = aList and aList[0] or []
                    break
            #@-<< Test for @language >>
            #@+<< Test for @root, @root-doc or @root-code >>
            #@+node:ekr.20110605121601.18558: *5* << Test for @root, @root-doc or @root-code >>
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
        # 2011/05/28: If no language, get the language from any @<file> node.
        if self.language:
            if trace: g.trace('found @language %s %s' % (self.language,self.languageList))
            return self.language
        #  Attempt to get the language from the nearest enclosing @<file> node.
        self.language = g.getLanguageFromAncestorAtFileNode(root)
        if not self.language:
            if trace: g.trace('using default',c.target_language)
            self.language = c.target_language
        return self.language # For use by external routines.
    #@+node:ekr.20110605121601.18559: *5* findLanguageDirectives
    def findLanguageDirectives (self,p):

        '''Scan p's body text for *valid* @language directives.

        Return a list of languages.'''

        # Speed not very important: called only for nodes containing @language directives.
        trace = False and not g.unitTesting
        aList = []
        for s in g.splitLines(p.b):
            if g.match_word(s,0,'@language'):
                i = len('@language')
                i = g.skip_ws(s,i)
                j = g.skip_id(s,i)
                if j > i:
                    word = s[i:j]
                    if self.isValidLanguage(word):
                        aList.append(word)
                    else:
                        if trace:g.trace('invalid',word)

        if trace: g.trace(aList)
        return aList
    #@+node:ekr.20110605121601.18560: *5* isValidLanguage
    def isValidLanguage (self,language):

        fn = g.os_path_join(g.app.loadDir,'..','modes','%s.py' % (language))
        return g.os_path_exists(fn)
    #@+node:ekr.20110605121601.18561: *4* setHighlighter
    # Called *only* from leoTree.setBodyTextAfterSelect

    # def setHighlighter (self,p):

        # trace = False and not g.unitTesting
        # if self.enabled:
            # self.flag = self.updateSyntaxColorer(p)
            # if self.flag:
                # # Do a full recolor, but only if we aren't changing nodes.
                # if self.c.currentPosition() == p:
                    # self.highlighter.rehighlight(p)
            # else:
                # self.highlighter.rehighlight(p) # Do a full recolor (to black)
        # else:
            # self.highlighter.rehighlight(p) # Do a full recolor (to black)

        # if trace: g.trace('enabled: %s flag: %s %s' % (
            # self.enabled,self.flag,p.h),g.callers())
            
    def setHighlighter (self,p):

        if self.enabled:
            self.flag = self.updateSyntaxColorer(p)
    #@+node:ekr.20110605121601.18562: *4* updateSyntaxColorer
    def updateSyntaxColorer (self,p):

        trace = False and not g.unitTesting
        p = p.copy()

        if len(p.b) > self.max_chars_to_colorize > 0:
            self.flag = False
        else:
            # self.flag is True unless an unambiguous @nocolor is seen.
            self.flag = self.useSyntaxColoring(p)
            self.scanColorDirectives(p) # Sets self.language

        if trace: g.trace(self.flag,len(p.b),self.language,p.h,g.callers(5))
        return self.flag
    #@+node:ekr.20110605121601.18563: *4* useSyntaxColoring & helper
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
    #@+node:ekr.20110605121601.18564: *5* findColorDirectives
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
    #@+node:ekr.20121003051050.10198: *4* write_colorizer_cache (leoQtColorizer)
    # Used info from qt/src/gui/text/qsyntaxhighlighter.cpp

    def write_colorizer_cache (self,p):

        trace = False and not g.unitTesting
        if not p: return
        c = self.c
        w = c.frame.body.bodyCtrl.widget # a subclass of QTextBrowser
        doc = w.document()
        if trace:
            t1 = time.time()
        aList = []
        for i in range(doc.blockCount()):
            b = doc.findBlockByNumber(i)
            s = g.u(b.text())
            layout = b.layout()
            ranges = list(layout.additionalFormats()) # A list of FormatRange objects.
            if ranges:
                aList.append(g.bunch(i=i,ranges=ranges,s=s))
                # Apparently not necessary.
                    # ranges2 = []
                    # for r in ranges:
                        # # Hold the format in memory by copying it.
                        # r.format = QtGui.QTextCharFormat(r.format)
                        # ranges2.append(r)
                    # aList.append(g.bunch(i=i,ranges=ranges2,s=s))

        p.v.colorCache = g.bunch(aList=aList,n=doc.blockCount(),v=p.v)
        if trace:
            g.trace('%2.3f sec len(aList): %s v: %s' % (
                time.time()-t1,len(aList),c.p.v.h,))
    #@-others

#@+node:ekr.20110605121601.18565: *3* leoQtSyntaxHighlighter (QtGui.QSyntaxHighlighter)
# This is c.frame.body.colorizer.highlighter

class leoQtSyntaxHighlighter(QtGui.QSyntaxHighlighter):

    '''A subclass of QSyntaxHighlighter that overrides
    the highlightBlock and rehighlight methods.

    All actual syntax coloring is done in the jeditColorer class.'''

    #@+others
    #@+node:ekr.20110605121601.18566: *4* ctor (leoQtSyntaxHighlighter)
    def __init__ (self,c,w,colorizer):

        self.c = c
        self.w = w # w is a LeoQTextBrowser.

        # print('leoQtSyntaxHighlighter.__init__',w,self.setDocument)

        # Not all versions of Qt have the crucial currentBlock method.
        self.hasCurrentBlock = hasattr(self,'currentBlock')

        # Init the base class.
        QtGui.QSyntaxHighlighter.__init__(self,w)

        self.colorizer = colorizer

        self.colorer = jEditColorizer(c,
            colorizer=colorizer,
            highlighter=self,
            w=c.frame.body.bodyCtrl)
    #@+node:ekr.20110605121601.18567: *4* highlightBlock (leoQtSyntaxHighlighter)
    def highlightBlock (self,s):
        """ Called by QSyntaxHiglighter """

        trace = False and not g.unitTesting

        if self.hasCurrentBlock and not self.colorizer.killColorFlag:
            if g.isPython3:
                s = str(s)
            else:
                s = unicode(s)

            self.colorer.recolor(s)

            v = self.c.p.v
            if hasattr(v,'colorCache') and v.colorCache and not self.colorizer.changingText:
                if trace: g.trace('clearing cache',g.callers())
                self.c.p.v.colorCache = None # Kill the color caching.
    #@+node:ekr.20110605121601.18568: *4* rehighlight  (leoQtSyntaxhighligher) & helper
    def rehighlight (self,p):

        '''Override base rehighlight method'''

        trace = False and not g.unitTesting
        c = self.c ; tree = c.frame.tree
        self.w = c.frame.body.bodyCtrl.widget

        if trace:
            t1 = time.time()

        # Call the base class method, but *only*
        # if the crucial 'currentBlock' method exists.
        n = self.colorer.recolorCount
        if self.colorizer.enabled and self.hasCurrentBlock:
            # Lock out onTextChanged.
            old_selecting = tree.selecting
            try:
                tree.selecting = True
                if (
                    self.colorizer.colorCacheFlag
                    and hasattr(p.v,'colorCache') and p.v.colorCache
                    and not g.unitTesting
                ):
                    # Should be no need to init the colorizer.
                    self.rehighlight_with_cache(p.v.colorCache)
                else:
                    self.colorer.init(p,p.b)
                    QtGui.QSyntaxHighlighter.rehighlight(self)
            finally:
                tree.selecting = old_selecting

        if trace:
            g.trace('recolors: %4s %2.3f sec' % (
                self.colorer.recolorCount-n,time.time()-t1))
    #@+node:ekr.20121003051050.10201: *5* rehighlight_with_cache (leoQtSyntaxHighlighter)
    def rehighlight_with_cache (self,bunch):

        '''Rehighlight the block from bunch, without calling QSH.rehighlight.

        - bunch.aList: a list of bunch2 objects.
        - bunch.n: a block (line) number.
        - bunch.v: the vnode.
            - bunch2.i: the index of the block.
            - bunch2.s: the contents of the block.
            - bunch2.ranges: a list of QTextLayout.FormatRange objects.
        '''

        trace = False and not g.unitTesting
        w = self.c.frame.body.bodyCtrl.widget # a subclass of QTextEdit.
        doc = w.document()
        if bunch.n != doc.blockCount():
            return g.trace('bad block count: expected %s got %s' % (
                bunch.n,doc.blockCount()))
        if trace:
            t1 = time.time()
        for i,bunch2 in enumerate(bunch.aList):
            b = doc.findBlockByNumber(bunch2.i) # a QTextBlock
            layout = b.layout() # a QTextLayout.
            if bunch2.s == g.u(b.text()):
                layout.setAdditionalFormats(bunch2.ranges)
            else:
                return g.trace('bad line: i: %s\nexpected %s\ngot     %s' % (
                    i,bunch2.s,g.u(b.text())))
        if trace:
            g.trace('%2.3f sec %s' % (time.time()-t1))
    #@-others
#@+node:ekr.20130702040231.12633: *3* LeoSyntaxHighlighter(qsh.LeoSyntaxHighlighter) NEW
# This is c.frame.body.colorizer.highlighter

if PYTHON_COLORER:

    class LeoSyntaxHighlighter(qsh.LeoSyntaxHighlighter):
    
        '''A subclass of qsh.LeoSyntaxHighlighter that overrides
        the highlightBlock and rehighlight methods.
    
        All actual syntax coloring is done in the jeditColorer class.'''
    
        #@+others
        #@+node:ekr.20130702040231.12634: *4* ctor (LeoSyntaxHighlighter)
        def __init__ (self,c,w,colorizer):

            self.c = c
            self.w = w # w is a LeoQTextBrowser.
            assert isinstance(w,LeoQTextBrowser),w

            # print('leoQtSyntaxHighlighter.__init__',w)

            # Not all versions of Qt have the crucial currentBlock method.
            self.hasCurrentBlock = hasattr(self,'currentBlock')

            # Init the base class.
            qsh.LeoSyntaxHighlighter.__init__(self,c,w)

            self.colorizer = colorizer

            self.colorer = jEditColorizer(c,
                colorizer=colorizer,
                highlighter=self,
                w=c.frame.body.bodyCtrl)
        #@+node:ekr.20130702040231.12635: *4* highlightBlock (LeoSyntaxHighlighter)
        def highlightBlock (self,s):
            """ Called by QSyntaxHiglighter """

            trace = True and not g.unitTesting

            if self.hasCurrentBlock and not self.colorizer.killColorFlag:
                if g.isPython3:
                    s = str(s)
                else:
                    s = unicode(s)
                self.colorer.recolor(s)
                v = self.c.p.v
                if hasattr(v,'colorCache') and v.colorCache and not self.colorizer.changingText:
                    if trace: g.trace('clearing cache',g.callers())
                    self.c.p.v.colorCache = None # Kill the color caching.
        #@+node:ekr.20130702040231.12636: *4* rehighlight  (LeoSyntaxHighligher) & helper
        def rehighlight (self,p):
            '''Override base rehighlight method'''
            # pylint: disable=W0221
            # Arguments number differ from overridden method.
            trace = False and not g.unitTesting
            c = self.c ; tree = c.frame.tree
            self.w = c.frame.body.bodyCtrl.widget
            if trace: t1 = time.time()
            # g.trace('(LeoSyntaxHighlighter)',g.callers())

            # Call the base class method, but *only*
            # if the crucial 'currentBlock' method exists.
            n = self.colorer.recolorCount
            if self.colorizer.enabled and self.hasCurrentBlock:
                # Lock out onTextChanged.
                old_selecting = tree.selecting
                try:
                    tree.selecting = True
                    if False and (
                        self.colorizer.colorCacheFlag
                        and hasattr(p.v,'colorCache') and p.v.colorCache
                        and not g.unitTesting
                    ):
                        # Should be no need to init the colorizer.
                        self.rehighlight_with_cache(p.v.colorCache)
                    else:
                        self.colorer.init(p,p.b)
                        qsh.LeoSyntaxHighlighter.rehighlight(self)
                finally:
                    tree.selecting = old_selecting
            if trace:
                g.trace('recolors: %4s %2.3f sec' % (
                    self.colorer.recolorCount-n,time.time()-t1))
        #@+node:ekr.20130702040231.12637: *5* rehighlight_with_cache (leoSyntaxHighlighter)
        def rehighlight_with_cache (self,bunch):

            '''Rehighlight the block from bunch, without calling QSH.rehighlight.

            - bunch.aList: a list of bunch2 objects.
            - bunch.n: a block (line) number.
            - bunch.v: the vnode.
                - bunch2.i: the index of the block.
                - bunch2.s: the contents of the block.
                - bunch2.ranges: a list of QTextLayout.FormatRange objects.
            '''

            trace = False and not g.unitTesting
            w = self.c.frame.body.bodyCtrl.widget # a subclass of QTextEdit.
            doc = w.document()
            if bunch.n != doc.blockCount():
                return g.trace('bad block count: expected %s got %s' % (
                    bunch.n,doc.blockCount()))
            if trace:
                t1 = time.time()
            for i,bunch2 in enumerate(bunch.aList):
                b = doc.findBlockByNumber(bunch2.i) # a QTextBlock
                layout = b.layout() # a QTextLayout.
                if bunch2.s == g.u(b.text()):
                    layout.setAdditionalFormats(bunch2.ranges)
                else:
                    return g.trace('bad line: i: %s\nexpected %s\ngot     %s' % (
                        i,bunch2.s,g.u(b.text())))
            if trace:
                g.trace('%2.3f sec %s' % (time.time()-t1))
        #@-others
#@+node:ekr.20110605121601.18569: *3* class jeditColorizer
# This is c.frame.body.colorizer.highlighter.colorer

class jEditColorizer:

    '''This class contains jEdit pattern matchers adapted
    for use with QSyntaxHighlighter.'''

    #@+<< about the line-oriented jEdit colorizer >>
    #@+node:ekr.20110605121601.18570: *4* << about the line-oriented jEdit colorizer >>
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
    # restarters for continued strings, and both flavors of continued triple-quoted
    # strings. For python, these turn out to be three separate lambda bindings for
    # restart_match_span.
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
    #@+node:ekr.20110605121601.18571: *4*  Birth & init
    #@+node:ekr.20110605121601.18572: *5* __init__ (jeditColorizer)
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
        self.trace_match_flag = False
            # True: trace all matching methods.
            # This isn't so useful now that colorRangeWithTag shows g.callers(2).
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
        self.language_name = None # The name of the language for the current mode.
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

            # To be removed...

                # Used only by the old colorizer.
                # 'bracketRange',
                # "comment",
                # "cwebName"
                # "keyword",
                # "latexBackground","latexKeyword","latexModeKeyword",
                # "pp",
                # "string",

                # Wiki styling.  These were never user options.
                # "bold","bolditalic","elide","italic",

                # Marked as Leo jEdit tags, but not used.
                # '@color', '@nocolor','doc_part', 'section_ref',

            # 8 Leo-specific tags.
            "blank",  # show_invisibles_space_color
            "docpart",
            "leokeyword",
            "link",
            "name",
            "namebrackets",
            "tab", # show_invisibles_space_color
            "url",

            # jEdit tags.
            'comment1','comment2','comment3','comment4',
            # default, # exists, but never generated.
            'function',
            'keyword1','keyword2','keyword3','keyword4',
            'label','literal1','literal2','literal3','literal4',
            'markup','operator',
        ]

        self.defineLeoKeywordsDict()
        self.defineDefaultColorsDict()
        self.defineDefaultFontDict()
    #@+node:ekr.20110605121601.18573: *6* defineLeoKeywordsDict
    def defineLeoKeywordsDict(self):

        self.leoKeywordsDict = {}

        for key in g.globalDirectiveList:
            self.leoKeywordsDict [key] = 'leokeyword'
    #@+node:ekr.20110605121601.18574: *6* defineDefaultColorsDict
    def defineDefaultColorsDict (self):

        # These defaults are sure to exist.
        self.default_colors_dict = {

            # Used in Leo rules...

            # tag name      :( option name,                  default color),
            'blank'         :('show_invisibles_space_color', '#E5E5E5'), # gray90
            'docpart'       :('doc_part_color',              'red'),
            'leokeyword'    :('leo_keyword_color',           'blue'),
            'link'          :('section_name_color',          'red'),
            'name'          :('undefined_section_name_color','red'),
            'namebrackets'  :('section_name_brackets_color', 'blue'),
            'tab'           :('show_invisibles_tab_color',   '#CCCCCC'), # gray80
            'url'           :('url_color',                   'purple'),

            # Used by the old colorizer: to be removed.

            # 'bracketRange'   :('bracket_range_color',     'orange'), # Forth.
            # 'comment'        :('comment_color',           'red'),
            # 'cwebName'       :('cweb_section_name_color', 'red'),
            # 'keyword'        :('keyword_color',           'blue'),
            # 'latexBackground':('latex_background_color',  'white'),
            # 'pp'             :('directive_color',         'blue'),
            # 'string'         :('string_color',            '#00aa00'), # Used by IDLE.

            # jEdit tags.
            # tag name  :( option name,     default color),
            'comment1'  :('comment1_color', 'red'),
            'comment2'  :('comment2_color', 'red'),
            'comment3'  :('comment3_color', 'red'),
            'comment4'  :('comment4_color', 'red'),
            'function'  :('function_color', 'black'),
            'keyword1'  :('keyword1_color', 'blue'),
            'keyword2'  :('keyword2_color', 'blue'),
            'keyword3'  :('keyword3_color', 'blue'),
            'keyword4'  :('keyword4_color', 'blue'),
            'keyword5'  :('keyword5_color', 'blue'),
            'label'     :('label_color',    'black'),
            'literal1'  :('literal1_color', '#00aa00'),
            'literal2'  :('literal2_color', '#00aa00'),
            'literal3'  :('literal3_color', '#00aa00'),
            'literal4'  :('literal4_color', '#00aa00'),
            'markup'    :('markup_color',   'red'),
            'null'      :('null_color',     None), #'black'),
            'operator'  :('operator_color', None), #'black'),
        }
    #@+node:ekr.20110605121601.18575: *6* defineDefaultFontDict
    def defineDefaultFontDict (self):

        self.default_font_dict = {

            # Used in Leo rules...

                # tag name      : option name
                'blank'         :'show_invisibles_space_font', # 2011/10/24.
                'docpart'       :'doc_part_font',
                'leokeyword'    :'leo_keyword_font',
                'link'          :'section_name_font',
                'name'          :'undefined_section_name_font',
                'namebrackets'  :'section_name_brackets_font',
                'tab'           : 'show_invisibles_tab_font', # 2011/10/24.
                'url'           : 'url_font',

            # Used by old colorizer.

                # 'bracketRange'   :'bracketRange_font', # Forth.
                # 'comment'       :'comment_font',
                # 'cwebName'      :'cweb_section_name_font',
                # 'keyword'       :'keyword_font',
                # 'latexBackground':'latex_background_font',
                # 'pp'            :'directive_font',
                # 'string'        :'string_font',

             # jEdit tags.

                 # tag name     : option name
                'comment1'      :'comment1_font',
                'comment2'      :'comment2_font',
                'comment3'      :'comment3_font',
                'comment4'      :'comment4_font',
                #'default'       :'default_font',
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
    #@+node:ekr.20110605121601.18576: *5* addImportedRules
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
    #@+node:ekr.20110605121601.18577: *5* addLeoRules
    def addLeoRules (self,theDict):

        '''Put Leo-specific rules to theList.'''

        table = (
            # Rules added at front are added in **reverse** order.
            ('@',  self.match_leo_keywords,True), # Called after all other Leo matchers.
                # Debatable: Leo keywords override langauge keywords.
            ('@',  self.match_at_color,    True),
            ('@',  self.match_at_killcolor,True),
            ('@',  self.match_at_language, True), # 2011/01/17
            ('@',  self.match_at_nocolor,  True),
            ('@',  self.match_at_nocolor_node,True),
            ('@',  self.match_doc_part,    True),
            ('f',  self.match_url_f,       True),
            ('g',  self.match_url_g,       True),
            ('h',  self.match_url_h,       True),
            ('m',  self.match_url_m,       True),
            ('n',  self.match_url_n,       True),
            ('p',  self.match_url_p,       True),
            ('t',  self.match_url_t,       True),
            ('w',  self.match_url_w,       True),
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
    #@+node:ekr.20111024091133.16702: *5* configure_hard_tab_width
    def configure_hard_tab_width (self):

        # The stated default is 40, but apparently it must be set explicitly.

        trace = False and not g.unitTesting
        c,w = self.c,self.w

        if 0:
            # No longer used: c.config.getInt('qt-tab-width')
            hard_tab_width = abs(10*c.tab_width)
            if trace: g.trace('hard_tab_width',hard_tab_width,self.w)
        else:
            # For some reason, the size is not accurate.
            font = w.widget.currentFont()
            info = QtGui.QFontInfo(font)
            size = info.pointSizeF()
            pixels_per_point = 1.0 # 0.9
            hard_tab_width = abs(int(pixels_per_point*size*c.tab_width))

            if trace: g.trace(
                'family',font.family(),'point size',size,
                'tab_width',c.tab_width,
                'hard_tab_width',hard_tab_width) # ,self.w)

        w.widget.setTabStopWidth(hard_tab_width)
    #@+node:ekr.20110605121601.18578: *5* configure_tags
    def configure_tags (self):

        trace = False and not g.unitTesting
        traceColors = False
        traceFonts = False
        c = self.c ; w = self.w
        isQt = g.app.gui.guiName().startswith('qt')

        if trace: g.trace(self.colorizer.language)

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
        if trace and traceFonts: g.trace('*'*10,'configuring fonts')
        keys = list(self.default_font_dict.keys()) ; keys.sort()
        for key in keys:
            option_name = self.default_font_dict[key]
            # First, look for the language-specific setting, then the general setting.
            for name in ('%s_%s' % (self.colorizer.language,option_name),(option_name)):
                if trace and traceFonts: g.trace(name)
                font = self.fonts.get(name)
                if font:
                    if trace and traceFonts:
                        g.trace('**found',name,id(font))
                    w.tag_configure(key,font=font)
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
                        w.tag_configure(key,font=font)
                        break

            else: # Neither the general setting nor the language-specific setting exists.
                if list(self.fonts.keys()): # Restore the default font.
                    if trace and traceFonts:
                        g.trace('default',key,font)
                    self.fonts[key] = font # 2010/02/19: Essential
                    w.tag_configure(key,font=defaultBodyfont)
                else:
                    if trace and traceFonts:
                        g.trace('no fonts')

            if isQt and key == 'url' and font:
                font.setUnderline(True) # 2011/03/04

        if trace and traceColors: g.trace('*'*10,'configuring colors')
        keys = list(self.default_colors_dict.keys()) ; keys.sort()
        for name in keys:
            # if name == 'operator': g.pdb()
            option_name,default_color = self.default_colors_dict[name]
            color = (
                c.config.getColor('%s_%s' % (self.colorizer.language,option_name)) or
                c.config.getColor(option_name) or
                default_color
            )
            if trace and traceColors: g.trace(option_name,color)

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

        try:
            w.end_tag_configure()
        except AttributeError:
            pass
    #@+node:ekr.20110605121601.18579: *5* configure_variable_tags
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
    #@+node:ekr.20110605121601.18580: *5* init (jeditColorizer)
    def init (self,p,s):

        trace = False and not g.unitTesting

        if p: self.p = p.copy()
        self.all_s = s or ''

        if trace: g.trace('='*20,
            'tabwidth',self.c.tab_width,
            self.colorizer.language) #,g.callers(4))

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

        self.configure_hard_tab_width() # 2011/10/04
    #@+node:ekr.20110605121601.18581: *5* init_mode & helpers
    def init_mode (self,name):

        '''Name may be a language name or a delegate name.'''

        trace = False and not g.unitTesting
        if not name: return False
        language,rulesetName = self.nameToRulesetName(name)
        bunch = self.modes.get(rulesetName)
        if bunch:
            if bunch.language == 'unknown-language':
                if trace: g.trace('found unknown language')
                return False
            else:
                if trace: g.trace('found',language,rulesetName)
                self.initModeFromBunch(bunch)
                self.language_name = language # 2011/05/30
                return True
        else:
            if trace: g.trace(language,rulesetName)
            path = g.os_path_join(g.app.loadDir,'..','modes')
            # Bug fix: 2008/2/10: Don't try to import a non-existent language.
            fileName = g.os_path_join(path,'%s.py' % (language))
            if g.os_path_exists(fileName):
                mode = g.importFromPath (language,path)
            else:
                mode = None
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
                    language        = 'unknown-language',
                    mode            = mode,
                    properties      = {},
                    rulesDict       = {},
                    rulesetName     = rulesetName,
                    word_chars      = self.word_chars, # 2011/05/21
                )
                if trace: g.trace('***** No colorizer file: %s.py' % language)
                self.rulesetName = rulesetName
                self.language_name = 'unknown-language'
                return False
            self.colorizer.language = language
            self.rulesetName = rulesetName
            self.properties = hasattr(mode,'properties') and mode.properties or {}
            self.keywordsDict = hasattr(mode,'keywordsDictDict') and mode.keywordsDictDict.get(rulesetName,{}) or {}
            self.setKeywords()
            self.attributesDict = hasattr(mode,'attributesDictDict') and mode.attributesDictDict.get(rulesetName) or {}
            # if trace: g.trace(rulesetName,self.attributesDict)
            self.setModeAttributes()
            self.rulesDict = hasattr(mode,'rulesDictDict') and mode.rulesDictDict.get(rulesetName) or {}
            # if trace: g.trace(self.rulesDict)
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
                word_chars      = self.word_chars, # 2011/05/21
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
                self.language_name = language2  # 2011/05/30
            else:
                self.language_name = language  # 2011/05/30
            return True
    #@+node:ekr.20110605121601.18582: *6* nameToRulesetName
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
    #@+node:ekr.20110605121601.18583: *6* setKeywords
    def setKeywords (self):

        '''Initialize the keywords for the present language.

         Set self.word_chars ivar to string.letters + string.digits
         plus any other character appearing in any keyword.
         '''
        # Add any new user keywords to leoKeywordsDict.
        d = self.keywordsDict
        keys = list(d.keys())
        for s in g.globalDirectiveList:
            key = '@' + s
            if key not in keys:
                d [key] = 'leokeyword'
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
        # g.trace(sorted(self.word_chars.keys()))
    #@+node:ekr.20110605121601.18584: *6* setModeAttributes
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
    #@+node:ekr.20110605121601.18585: *6* initModeFromBunch
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
        self.word_chars     = bunch.word_chars # 2011/05/21
    #@+node:ekr.20110605121601.18586: *6* updateDelimsTables
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
    #@+node:ekr.20110605121601.18587: *5* munge
    def munge(self,s):

        '''Munge a mode name so that it is a valid python id.'''

        valid = string.ascii_letters + string.digits + '_'

        return ''.join([g.choose(ch in valid,ch.lower(),'_') for ch in s])
    #@+node:ekr.20110605121601.18588: *5* setFontFromConfig (jeditColorizer)
    def setFontFromConfig (self):

        c = self.c

        self.bold_font = c.config.getFontFromParams(
            "body_text_font_family", "body_text_font_size",
            "body_text_font_slant",  "body_text_font_weight",
            c.config.defaultBodyFontSize)

        self.italic_font = c.config.getFontFromParams(
            "body_text_font_family", "body_text_font_size",
            "body_text_font_slant",  "body_text_font_weight",
            c.config.defaultBodyFontSize)

        self.bolditalic_font = c.config.getFontFromParams(
            "body_text_font_family", "body_text_font_size",
            "body_text_font_slant",  "body_text_font_weight",
            c.config.defaultBodyFontSize)

        self.color_tags_list = []
    #@+node:ekr.20110605121601.18589: *4*  Pattern matchers
    #@+node:ekr.20110605121601.18590: *5*  About the pattern matchers
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
    #@+node:ekr.20110605121601.18591: *5* dump
    def dump (self,s):

        if s.find('\n') == -1:
            return s
        else:
            return '\n' + s + '\n'
    #@+node:ekr.20110605121601.18592: *5* Leo rule functions
    #@+node:ekr.20110605121601.18593: *6* match_at_color
    def match_at_color (self,s,i):

        if self.trace_leo_matches: g.trace()

        seq = '@color'

        # Only matches at start of line.
        if i != 0: return 0

        if g.match_word(s,i,seq):
            self.colorizer.flag = True # Enable coloring.
            j = i + len(seq)
            self.colorRangeWithTag(s,i,j,'leokeyword')
            self.clearState()
            return j - i
        else:
            return 0
    #@+node:ekr.20110605121601.18594: *6* match_at_language
    def match_at_language (self,s,i):

        trace = (False or self.trace_leo_matches) and not g.unitTesting
        if trace: g.trace(i,repr(s))

        seq = '@language'

        # Only matches at start of line.
        if i != 0: return 0

        if g.match_word(s,i,seq):
            j = i + len(seq)
            j = g.skip_ws(s,j)
            k = g.skip_c_id(s,j)
            name = s[j:k]
            ok = self.init_mode(name)
            if trace: g.trace(ok,name,self.language_name)
            if ok:
                self.colorRangeWithTag(s,i,k,'leokeyword')
            self.clearState()
            return k - i
        else:
            return 0
    #@+node:ekr.20110605121601.18595: *6* match_at_nocolor & restarter
    def match_at_nocolor (self,s,i):

        if self.trace_leo_matches: g.trace(i,repr(s))

        # Only matches at start of line.
        if i == 0 and not g.match(s,i,'@nocolor-') and g.match_word(s,i,'@nocolor'):
            self.setRestart(self.restartNoColor)
            return len(s) # Match everything.
        else:
            return 0
    #@+node:ekr.20110605121601.18596: *7* restartNoColor
    def restartNoColor (self,s):

        if self.trace_leo_matches: g.trace(repr(s))

        if g.match_word(s,0,'@color'):
            self.clearState()
        else:
            self.setRestart(self.restartNoColor)

        return len(s) # Always match everything.
    #@+node:ekr.20110605121601.18597: *6* match_at_killcolor & restarter
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

    #@+node:ekr.20110605121601.18598: *7* restartKillColor
    def restartKillColor(self,s):

        self.setRestart(self.restartKillColor)
        return len(s)+1
    #@+node:ekr.20110605121601.18599: *6* match_at_nocolor_node & restarter
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
    #@+node:ekr.20110605121601.18600: *7* restartNoColorNode
    def restartNoColorNode(self,s):

        self.setRestart(self.restartNoColorNode)
        return len(s)+1
    #@+node:ekr.20110605121601.18601: *6* match_blanks
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
    #@+node:ekr.20110605121601.18602: *6* match_doc_part & restarter
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

        self.colorRangeWithTag(s,i,j,'leokeyword')
        self.colorRangeWithTag(s,j,len(s),'docpart')
        self.setRestart(self.restartDocPart)

        return len(s)
    #@+node:ekr.20110605121601.18603: *7* restartDocPart
    def restartDocPart (self,s):

        for tag in ('@c','@code'):
            if g.match_word(s,0,tag):
                j = len(tag)
                self.colorRangeWithTag(s,0,j,'leokeyword') # 'docpart')
                self.clearState()
                return j
        else:
            self.setRestart(self.restartDocPart)
            self.colorRangeWithTag(s,0,len(s),'docpart')

            return len(s)
    #@+node:ekr.20110605121601.18604: *6* match_leo_keywords
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
            kind = 'leokeyword'
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
    #@+node:ekr.20110605121601.18605: *6* match_section_ref
    def match_section_ref (self,s,i):

        if self.trace_leo_matches: g.trace()
        c = self.c ; p = c.p
        if not g.match(s,i,'<<'):
            return 0
        k = g.find_on_line(s,i+2,'>>')
        if k is not None:
            j = k + 2
            self.colorRangeWithTag(s,i,i+2,'namebrackets')
            ref = g.findReference(c,s[i:j],p)
            if ref:
                if self.use_hyperlinks:
                    #@+<< set the hyperlink >>
                    #@+node:ekr.20110605121601.18606: *7* << set the hyperlink >>
                    # Set the bindings to vnode callbacks.
                    tagName = "hyper" + str(self.hyperCount)
                    self.hyperCount += 1
                    ref.tagName = tagName
                    #@-<< set the hyperlink >>
                else:
                    self.colorRangeWithTag(s,i+2,k,'link')
            else:
                self.colorRangeWithTag(s,i+2,k,'name')
            self.colorRangeWithTag(s,k,j,'namebrackets')
            return j - i
        else:
            return 0
    #@+node:ekr.20110605121601.18607: *6* match_tabs
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
    #@+node:ekr.20110605121601.18608: *6* match_url_any/f/h  (new)
    # Fix bug 893230: URL coloring does not work for many Internet protocols.
    # Added support for: gopher, mailto, news, nntp, prospero, telnet, wais
    url_regex_f = re.compile(  r"""(file|ftp)://[^\s'"]+[\w=/]""")
    url_regex_g = re.compile(      r"""gopher://[^\s'"]+[\w=/]""")
    url_regex_h = re.compile(r"""(http|https)://[^\s'"]+[\w=/]""")
    url_regex_m = re.compile(      r"""mailto://[^\s'"]+[\w=/]""")
    url_regex_n = re.compile( r"""(news|nntp)://[^\s'"]+[\w=/]""")
    url_regex_p = re.compile(    r"""prospero://[^\s'"]+[\w=/]""")
    url_regex_t = re.compile(      r"""telnet://[^\s'"]+[\w=/]""")
    url_regex_w = re.compile(        r"""wais://[^\s'"]+[\w=/]""")

    kinds = '(file|ftp|gopher|http|https|mailto|news|nntp|prospero|telnet|wais)'
    # url_regex   = re.compile(r"""(file|ftp|http|https)://[^\s'"]+[\w=/]""")
    url_regex   = re.compile(r"""%s://[^\s'"]+[\w=/]""" % (kinds))

    def match_any_url(self,s,i):
        return self.match_compiled_regexp(s,i,kind='url',regexp=self.url_regex)

    def match_url_f(self,s,i):
        return self.match_compiled_regexp(s,i,kind='url',regexp=self.url_regex_f)

    def match_url_g(self,s,i):
        return self.match_compiled_regexp(s,i,kind='url',regexp=self.url_regex_g)

    def match_url_h(self,s,i):
        return self.match_compiled_regexp(s,i,kind='url',regexp=self.url_regex_h)

    def match_url_m(self,s,i):
        return self.match_compiled_regexp(s,i,kind='url',regexp=self.url_regex_m)

    def match_url_n(self,s,i):
        return self.match_compiled_regexp(s,i,kind='url',regexp=self.url_regex_n)

    def match_url_p(self,s,i):
        return self.match_compiled_regexp(s,i,kind='url',regexp=self.url_regex_p)

    def match_url_t(self,s,i):
        return self.match_compiled_regexp(s,i,kind='url',regexp=self.url_regex_t)

    def match_url_w(self,s,i):
        return self.match_compiled_regexp(s,i,kind='url',regexp=self.url_regex_w)
    #@+node:ekr.20110605121601.18609: *5* match_compiled_regexp (new)
    def match_compiled_regexp (self,s,i,kind,regexp,delegate=''):

        '''Succeed if the compiled regular expression regexp matches at s[i:].'''

        if self.verbose: g.trace(g.callers(1),i,repr(s[i:i+20]),'regexp',regexp)

        # if at_line_start and i != 0 and s[i-1] != '\n': return 0
        # if at_whitespace_end and i != g.skip_ws(s,0): return 0
        # if at_word_start and i > 0 and s[i-1] in self.word_chars: return 0

        n = self.match_compiled_regexp_helper(s,i,regexp)
        if n > 0:
            j = i + n
            assert (j-i == n)
            self.colorRangeWithTag(s,i,j,kind,delegate=delegate)
            self.prev = (i,j,kind)
            self.trace_match(kind,s,i,j)
            return j - i
        else:
            return 0
    #@+node:ekr.20110605121601.18610: *6* match_compiled_regexp_helper
    def match_compiled_regexp_helper (self,s,i,regex):

        '''Return the length of the matching text if seq (a regular expression) matches the present position.'''

        # Match succeeds or fails more quickly than search.
        self.match_obj = mo = regex.match(s,i) # re_obj.search(s,i) 

        if mo is None:
            return 0
        start, end = mo.start(), mo.end()
        if start != i:
            return 0
        # if trace:
            # g.trace('pattern',pattern)
            # g.trace('match: %d, %d, %s' % (start,end,repr(s[start: end])))
            # g.trace('groups',mo.groups())
        return end - start
    #@+node:ekr.20110605121601.18611: *5* match_eol_span
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
            # g.trace(s[i:j])
            return j # (was j-1) With a delegate, this could clear state.
        else:
            return 0
    #@+node:ekr.20110605121601.18612: *5* match_eol_span_regexp
    def match_eol_span_regexp (self,s,i,
        kind='',regexp='',
        at_line_start=False,at_whitespace_end=False,at_word_start=False,
        delegate='',exclude_match=False
    ):
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
    #@+node:ekr.20110605121601.18613: *5* match_everything
    # def match_everything (self,s,i,kind=None,delegate='',exclude_match=False):

        # '''Match the entire rest of the string.'''

        # j = len(s)
        # self.colorRangeWithTag(s,i,j,kind,delegate=delegate)

        # return j
    #@+node:ekr.20110605121601.18614: *5* match_keywords
    # This is a time-critical method.
    def match_keywords (self,s,i):
        '''
        Succeed if s[i:] is a keyword.
        Returning -len(word) for failure greatly reduces the number of times this
        method is called.
        '''
        trace = False and not g.unitTesting
        traceFail = True
        self.totalKeywordsCalls += 1
        # g.trace(i,repr(s[i:]))
        # We must be at the start of a word.
        if i > 0 and s[i-1] in self.word_chars:
            # if trace: g.trace('not at word start',s[i-1])
            return 0
        # Get the word as quickly as possible.
        j = i ; n = len(s)
        chars = self.word_chars
        # 2013/11/04: A kludge just for Haskell:
        if self.language_name == 'haskell':
            chars["'"] = "'"
        while j < n and s[j] in chars:
            j += 1
        word = s[i:j]
        if not word:
            g.trace('can not happen',repr(s[i:max(j,i+1)]),repr(s[i:i+10]),g.callers())
            return 0
        if self.ignore_case: word = word.lower()
        kind = self.keywordsDict.get(word)
        if kind:
            self.colorRangeWithTag(s,i,j,kind)
            self.prev = (i,j,kind)
            result = j - i
            if trace: g.trace('success',word,kind,result)
            self.trace_match(kind,s,i,j)
            return result
        else:
            if trace and traceFail: g.trace('fail',word,kind)
            return -len(word) # An important new optimization.
    #@+node:ekr.20110605121601.18615: *5* match_line
    def match_line (self,s,i,kind=None,delegate='',exclude_match=False):

        '''Match the rest of the line.'''

        j = g.skip_to_end_of_line(s,i)

        self.colorRangeWithTag(s,i,j,kind,delegate=delegate)

        return j-i
    #@+node:ekr.20110605121601.18616: *5* match_mark_following & getNextToken
    def match_mark_following (self,s,i,
        kind='',pattern='',
        at_line_start=False,at_whitespace_end=False,at_word_start=False,
        exclude_match=False):

        '''Succeed if s[i:] matches pattern.'''

        if not self.allow_mark_prev: return 0
        # g.trace(g.callers(1),i,repr(s[i:i+20]))
        if at_line_start and i != 0 and s[i-1] != '\n': return 0
        if at_whitespace_end and i != g.skip_ws(s,0): return 0
        if at_word_start and i > 0 and s[i-1] in self.word_chars: return 0 # 7/5/2008
        if at_word_start and i + len(pattern) + 1 < len(s) and s[i+len(pattern)] in self.word_chars:
            return 0 # 7/5/2008
        if g.match(s,i,pattern):
            j = i + len(pattern)
            # self.colorRangeWithTag(s,i,j,kind,exclude_match=exclude_match)
            k = self.getNextToken(s,j)
            # 2011/05/31: Do not match *anything* unless there is a token following.
            if k > j:
                self.colorRangeWithTag(s,i,j,kind,exclude_match=exclude_match)
                self.colorRangeWithTag(s,j,k,kind,exclude_match=False)
                j = k
                self.prev = (i,j,kind)
                self.trace_match(kind,s,i,j)
                return j - i
            else:
                return 0
        else:
            return 0
    #@+node:ekr.20110605121601.18617: *6* getNextToken
    def getNextToken (self,s,i):

        '''Return the index of the end of the next token for match_mark_following.

        The jEdit docs are not clear about what a 'token' is, but experiments with jEdit
        show that token means a word, as defined by word_chars.'''

        # 2011/05/31: Might we extend the concept of token?
        # If s[i] is not a word char, should we return just it?

        while i < len(s) and s[i] in self.word_chars:
            i += 1

        # 2011/05/31: was i+1
        return min(len(s),i)
    #@+node:ekr.20110605121601.18618: *5* match_mark_previous
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
    #@+node:ekr.20110605121601.18619: *5* match_regexp_helper
    def match_regexp_helper (self,s,i,pattern):

        '''Return the length of the matching text if seq (a regular expression) matches the present position.'''

        trace = False and not g.unitTesting
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
    #@+node:ekr.20110605121601.18620: *5* match_seq
    def match_seq (self,s,i,
        kind='',seq='',
        at_line_start=False,
        at_whitespace_end=False,
        at_word_start=False,
        delegate=''
    ):
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
    #@+node:ekr.20110605121601.18621: *5* match_seq_regexp
    def match_seq_regexp (self,s,i,
        kind='',regexp='',
        at_line_start=False,at_whitespace_end=False,at_word_start=False,
        delegate=''
    ):
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
    #@+node:ekr.20110605121601.18622: *5* match_span & helper & restarter
    def match_span (self,s,i,
        kind='',begin='',end='',
        at_line_start=False,at_whitespace_end=False,at_word_start=False,
        delegate='',exclude_match=False,
        no_escape=False,no_line_break=False,no_word_break=False
    ):
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
                # These must be keyword args.
                delegate=delegate,end=end,
                exclude_match=exclude_match,
                kind=kind,
                no_escape=no_escape,
                no_line_break=no_line_break,
                no_word_break=no_word_break)
            if trace: g.trace('***Continuing',kind,i,j,len(s),s[i:j])
        elif j != i:
            if trace: g.trace('***Ending',kind,i,j,s[i:j])
            self.clearState()
        return j - i # Correct, whatever j is.
    #@+node:ekr.20110605121601.18623: *6* match_span_helper
    def match_span_helper (self,s,i,pattern,no_escape,no_line_break,no_word_break):
        '''
        Return n >= 0 if s[i] ends with a non-escaped 'end' string.
        '''
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
                    assert s[j-1] == esc
                    i += 1 # 2013/08/26: just advance past the *one* escaped character.
                    # g.trace('escapes',escapes,repr(s[i:]))
                else:
                    return j
            else:
                return j
    #@+node:ekr.20110605121601.18624: *6* restart_match_span
    def restart_match_span (self,s,
        delegate,end,exclude_match,kind,
        no_escape,no_line_break,no_word_break
    ):
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
            self.colorRangeWithTag(s,j,j2,kind,delegate=None,exclude_match=exclude_match)
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
            if trace: g.trace('***Re-continuing',i,j,len(s),s)
        else:
            if trace: g.trace('***ending',i,j,len(s),s)
            self.clearState()
        return j # Return the new i, *not* the length of the match.
    #@+node:ekr.20110605121601.18625: *5* match_span_regexp
    def match_span_regexp (self,s,i,
        kind='',begin='',end='',
        at_line_start=False,at_whitespace_end=False,at_word_start=False,
        delegate='',exclude_match=False,
        no_escape=False,no_line_break=False, no_word_break=False,
    ):
        '''Succeed if s[i:] starts with 'begin' (a regular expression) and
        contains a following 'end'.
        '''
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
    #@+node:ekr.20110605121601.18626: *5* match_word_and_regexp
    def match_word_and_regexp (self,s,i,
        kind1='',word='',
        kind2='',pattern='',
        at_line_start=False,at_whitespace_end=False,at_word_start=False,
        exclude_match=False
    ):
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
    #@+node:ekr.20110605121601.18627: *5* skip_line
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
    #@+node:ekr.20110605121601.18628: *5* trace_match
    def trace_match(self,kind,s,i,j):

        if j != i and self.trace_match_flag:
            g.trace(kind,i,j,g.callers(2),self.dump(s[i:j]))
    #@+node:ekr.20110605121601.18629: *4*  State methods
    #@+node:ekr.20110605121601.18630: *5* clearState
    def clearState (self):

        self.setState(-1)
    #@+node:ekr.20110605121601.18631: *5* computeState
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
    #@+node:ekr.20110605121601.18632: *5* currentState and prevState
    def currentState(self):

        return self.highlighter.currentBlockState()

    def prevState(self):

        return self.highlighter.previousBlockState()
    #@+node:ekr.20110605121601.18633: *5* setRestart
    def setRestart (self,f,**keys):

        n = self.computeState(f,keys)
        self.setState(n)
    #@+node:ekr.20110605121601.18634: *5* setState
    def setState (self,n):

        trace = False and not g.unitTesting

        self.highlighter.setCurrentBlockState(n)

        if trace:
            stateName = self.showState(n)
            g.trace(stateName,g.callers(4))
    #@+node:ekr.20110605121601.18635: *5* showState & showCurrentState
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
    #@+node:ekr.20110605121601.18636: *5* stateNameToStateNumber
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
    #@+node:ekr.20110605121601.18637: *4* colorRangeWithTag
    def colorRangeWithTag (self,s,i,j,tag,delegate='',exclude_match=False):

        '''Actually colorize the selected range.

        This is called whenever a pattern matcher succeed.'''

        trace = False and not g.unitTesting
            # A superb trace: enable this first to see what gets colored.

        # Pattern matcher may set the .flag ivar.
        if self.colorizer.killColorFlag or not self.colorizer.flag:
            if trace: g.trace('disabled')
            return

        if delegate:
            if trace:
                s2 = g.choose(len(repr(s[i:j])) <= 20,repr(s[i:j]),repr(s[i:i+17-2]+'...'))
                g.trace('%25s %3s %3s %-20s %s' % (
                    ('%s.%s' % (delegate,tag)),i,j,s2,g.callers(2)))
            # self.setTag(tag,s,i,j) # 2011/05/31: Do the initial color.
            self.modeStack.append(self.modeBunch)
            self.init_mode(delegate)
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
            if trace:
                s2 = g.choose(len(repr(s[i:j])) <= 20,repr(s[i:j]),repr(s[i:i+17-2]+'...'))
                g.trace('%25s %3s %3s %-20s %s' % (
                    ('%s.%s' % (self.language_name,tag)),i,j,s2,g.callers(2)))
            self.setTag(tag,s,i,j)

        if tag != 'url':
            # Allow URL's *everywhere*.
            j = min(j,len(s))
            while i < j:
                if s[i].lower() in 'fh': # file|ftp|http|https
                    n = self.match_any_url(s,i)
                    i += max(1,n)
                else:
                    i += 1
    #@+node:ekr.20110605121601.18638: *4* mainLoop & restart
    def mainLoop(self,n,s):

        '''Colorize a *single* line s, starting in state n.'''

        trace = False and not g.unitTesting
        traceMatch = True
        traceFail = True
        traceState = True
        traceEndState = True
        if trace:
            if traceState:
                g.trace('%s %-30s' % (self.language_name,
                    '** start: %s' % self.showState(n)),repr(s))
            else:
                g.trace(self.language_name,repr(s)) # Called from recolor.
        i = 0
        if n > -1:
            i = self.restart(n,s,trace and traceMatch)
        if i == 0:
            self.setState(self.prevState())

        if False and trace:
            aList = self.rulesDict.get('<')
            for f in aList:
                g.trace(f.__name__)
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
                        g.trace('%-30s' % ('   match: %s' % (f.__name__,)),
                            repr(s[i:i+n]))
                    # The match has already been colored.
                    i += n
                    break # Stop searching the functions.
                elif n < 0: # Fail and skip n chars.
                    if trace and traceFail:
                        g.trace('fail: n: %s %-30s %s' % (
                            n,f.__name__,repr(s[i:i+n])))
                    i += -n
                    break # Stop searching the functions.
                else: # Fail. Try the next function.
                    pass # Do not break or change i!
            else:
                i += 1
            assert i > progress
        # Don't even *think* about clearing state here.
        # We remain in the starting state unless a match happens.
        if trace and traceEndState:
            g.trace('%-30s' % ('** end:   %s' % self.showCurrentState()),repr(s))
    #@+node:ekr.20110605121601.18639: *5* restart
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
    #@+node:ekr.20110605121601.18640: *4* recolor
    def recolor (self,s):

        '''Recolor a *single* line, s.'''

        trace = False and not g.unitTesting
        callers = False ; line = True ; state = False
        returns = False

        # Update the counts.
        self.recolorCount += 1
        self.totalChars += len(s)

        if self.colorizer.changingText:
            if trace and returns: g.trace('changingText')
            return
        if not self.colorizer.flag:
            if trace and returns: g.trace('not flag')
            return

        # Get the previous state.
        n = self.prevState() # The state at the end of the previous line.
        if trace:
            if line and state:
                g.trace('%2s %s %s' % (n,self.showState(n),repr(s)))
            elif line:
                g.trace('%2s %s' % (n,repr(s)))
            if callers:
                # Called from colorize:rehightlight,highlightBlock
                g.trace(g.callers())

        if s.strip() or self.showInvisibles:
            self.mainLoop(n,s)
        else:
            self.setState(n) # Required
    #@+node:ekr.20110605121601.18641: *4* setTag
    def setTag (self,tag,s,i,j):

        trace = False and not g.unitTesting

        if i == j:
            if trace: g.trace('empty range')
            return

        w = self.w # A leoQTextEditWidget
        tag = tag.lower() # 2011/10/28
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
                return g.trace('unknown color name',colorName,g.callers())

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
