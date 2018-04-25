# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20140831085423.18598: * @file ../plugins/qt_text.py
#@@first
'''Text classes for the Qt version of Leo'''
import leo.core.leoGlobals as g
import time
from leo.core.leoQt import isQt5, QtCore, QtGui, Qsci, QtWidgets
#@+others
#@+node:ekr.20140901062324.18719: **   class QTextMixin
class QTextMixin(object):
    '''A minimal mixin class for QTextEditWrapper and QScintillaWrapper classes.'''
    #@+others
    #@+node:ekr.20140901062324.18732: *3* qtm.ctor & helper
    def __init__(self, c=None):
        '''Ctor for QTextMixin class'''
        self.c = c
        self.changingText = False # A lockout for onTextChanged.
        self.enabled = True
        self.supportsHighLevelInterface = True
            # A flag for k.masterKeyHandler and isTextWrapper.
        self.tags = {}
        self.permanent = True # False if selecting the minibuffer will make the widget go away.
        self.configDict = {} # Keys are tags, values are colors (names or values).
        self.configUnderlineDict = {} # Keys are tags, values are True
        # self.formatDict = {} # Keys are tags, values are actual QTextFormat objects.
        self.useScintilla = False # This is used!
        self.virtualInsertPoint = None
        if c:
            self.injectIvars(c)
    #@+node:ekr.20140901062324.18721: *4* qtm.injectIvars
    def injectIvars(self, name='1', parentFrame=None):
        '''Inject standard leo ivars into the QTextEdit or QsciScintilla widget.'''
        w = self
        p = self.c.currentPosition()
        if name == '1':
            w.leo_p = None # Will be set when the second editor is created.
        else:
            w.leo_p = p and p.copy()
        w.leo_active = True
        # New in Leo 4.4.4 final: inject the scrollbar items into the text widget.
        w.leo_bodyBar = None
        w.leo_bodyXBar = None
        w.leo_chapter = None
        w.leo_frame = None
        w.leo_name = name
        w.leo_label = None
        return w
    #@+node:ekr.20140901062324.18825: *3* qtm.getName
    def getName(self):
        return self.name # Essential.
    #@+node:ekr.20140901122110.18733: *3* qtm.Event handlers
    # These are independent of the kind of Qt widget.
    #@+node:ekr.20140901062324.18716: *4* qtm.onCursorPositionChanged
    def onCursorPositionChanged(self, event=None):
        c = self.c
        name = c.widget_name(self)
        # Apparently, this does not cause problems
        # because it generates no events in the body pane.
        if name.startswith('body'):
            if hasattr(c.frame, 'statusLine'):
                c.frame.statusLine.update()
    #@+node:ekr.20140901062324.18714: *4* qtm.onTextChanged
    def onTextChanged(self):
        '''
        Update Leo after the body has been changed.

        self.selecting is guaranteed to be True during
        the entire selection process.
        '''
        # Important: usually w.changingText is True.
        # This method very seldom does anything.
        trace = False and not g.unitTesting
        verbose = False
        w = self
        c = self.c; p = c.p
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
        # Get the previous values from the VNode.
        oldText = p.b
        if oldText == newText:
            # This can happen as the result of undo.
            # g.error('*** unexpected non-change')
            return
        # g.trace('**',len(newText),p.h,'\n',g.callers(8))
        # oldIns  = p.v.insertSpot
        i, j = p.v.selectionStart, p.v.selectionLength
        oldSel = (i, i + j)
        if trace: g.trace('oldSel', oldSel, 'newSel', newSel)
        oldYview = None
        undoType = 'Typing'
        c.undoer.setUndoTypingParams(p, undoType,
            oldText=oldText, newText=newText,
            oldSel=oldSel, newSel=newSel, oldYview=oldYview)
        # Update the VNode.
        p.v.setBodyString(newText)
        if True:
            p.v.insertSpot = newInsert
            i, j = newSel
            i, j = self.toPythonIndex(i), self.toPythonIndex(j)
            if i > j: i, j = j, i
            p.v.selectionStart, p.v.selectionLength = (i, j - i)
        # No need to redraw the screen.
        if not self.useScintilla:
            c.recolor()
        if g.app.qt_use_tabs:
            if trace: g.trace(c.frame.top)
        if not c.changed and c.frame.initComplete:
            c.setChanged(True)
        c.frame.body.updateEditors()
        c.frame.tree.updateIcon(p)
    #@+node:ekr.20140901122110.18734: *3* qtm.Generic high-level interface
    # These call only wrapper methods.
    #@+node:ekr.20140902181058.18645: *4* qtm.Enable/disable
    def disable(self):
        self.enabled = False

    def enable(self, enabled=True):
        self.enabled = enabled
    #@+node:ekr.20140902181058.18644: *4* qtm.Clipboard
    def clipboard_append(self, s):
        s1 = g.app.gui.getTextFromClipboard()
        g.app.gui.replaceClipboardWith(s1 + s)

    def clipboard_clear(self):
        g.app.gui.replaceClipboardWith('')
    #@+node:ekr.20140901062324.18698: *4* qtm.setFocus
    def setFocus(self):
        '''QTextMixin'''
        if 'focus' in g.app.debug:
            print('BaseQTextWrapper.setFocus', self.widget)
        # Call the base class
        assert isinstance(self.widget, (
            QtWidgets.QTextBrowser,
            QtWidgets.QLineEdit,
            QtWidgets.QTextEdit,
            Qsci and Qsci.QsciScintilla,
        )), self.widget
        QtWidgets.QTextBrowser.setFocus(self.widget)
    #@+node:ekr.20140901062324.18717: *4* qtm.Generic text
    #@+node:ekr.20140901062324.18703: *5* qtm.appendText
    def appendText(self, s):
        '''QTextMixin'''
        s2 = self.getAllText()
        self.setAllText(s2 + s)
        self.setInsertPoint(len(s2))
    #@+node:ekr.20140901141402.18706: *5* qtm.delete
    def delete(self, i, j=None):
        '''QTextMixin'''
        i = self.toPythonIndex(i)
        if j is None: j = i + 1
        j = self.toPythonIndex(j)
        # This allows subclasses to use this base class method.
        if i > j: i, j = j, i
        s = self.getAllText()
        self.setAllText(s[: i] + s[j:])
        # Bug fix: Significant in external tests.
        self.setSelectionRange(i, i, insert=i)
    #@+node:ekr.20140901062324.18827: *5* qtm.deleteTextSelection
    def deleteTextSelection(self):
        '''QTextMixin'''
        i, j = self.getSelectionRange()
        self.delete(i, j)
    #@+node:ekr.20110605121601.18102: *5* qtm.get
    def get(self, i, j=None):
        '''QTextMixin'''
        # 2012/04/12: fix the following two bugs by using the vanilla code:
        # https://bugs.launchpad.net/leo-editor/+bug/979142
        # https://bugs.launchpad.net/leo-editor/+bug/971166
        s = self.getAllText()
        i = self.toPythonIndex(i)
        j = self.toPythonIndex(j)
        return s[i: j]
    #@+node:ekr.20140901062324.18704: *5* qtm.getLastPosition & getLength
    def getLastPosition(self, s=None):
        '''QTextMixin'''
        return len(self.getAllText()) if s is None else len(s)

    def getLength(self, s=None):
        '''QTextMixin'''
        return len(self.getAllText()) if s is None else len(s)
    #@+node:ekr.20140901062324.18705: *5* qtm.getSelectedText
    def getSelectedText(self):
        '''QTextMixin'''
        i, j = self.getSelectionRange()
        if i == j:
            return ''
        else:
            s = self.getAllText()
            return s[i: j]
    #@+node:ekr.20140901141402.18702: *5* qtm.insert
    def insert(self, i, s):
        '''QTextMixin'''
        s2 = self.getAllText()
        i = self.toPythonIndex(i)
        self.setAllText(s2[: i] + s + s2[i:])
        self.setInsertPoint(i + len(s))
        return i
    #@+node:ekr.20140902084950.18634: *5* qtm.seeInsertPoint
    def seeInsertPoint(self):
        '''Ensure the insert point is visible.'''
        self.see(self.getInsertPoint())
            # getInsertPoint defined in client classes.
    #@+node:ekr.20140902135648.18668: *5* qtm.selectAllText
    def selectAllText(self, s=None):
        '''QTextMixin.'''
        self.setSelectionRange(0, self.getLength(s))
    #@+node:ekr.20140901141402.18710: *5* qtm.toPythonIndex
    def toPythonIndex(self, index, s=None):
        '''QTextMixin'''
        if s is None:
            s = self.getAllText()
        i = g.toPythonIndex(s, index)
        # g.trace(index,len(s),i,s[i:i+10])
        return i
    #@+node:ekr.20140901141402.18704: *5* qtm.toPythonIndexRowCol
    def toPythonIndexRowCol(self, index):
        '''QTextMixin'''
        s = self.getAllText()
        i = self.toPythonIndex(index)
        row, col = g.convertPythonIndexToRowCol(s, i)
        return i, row, col
    #@+node:ekr.20140901062324.18729: *4* qtm.rememberSelectionAndScroll
    def rememberSelectionAndScroll(self):
        trace = (False or g.trace_scroll) and not g.unitTesting
        w = self
        v = self.c.p.v # Always accurate.
        v.insertSpot = w.getInsertPoint()
        i, j = w.getSelectionRange()
        if i > j: i, j = j, i
        assert(i <= j)
        v.selectionStart = i
        v.selectionLength = j - i
        v.scrollBarSpot = spot = w.getYScrollPosition()
        if trace:
            g.trace(spot, v.h)
            # g.trace(id(v),id(w),i,j,ins,spot,v.h)
    #@+node:ekr.20140901062324.18712: *4* qtm.tag_configure
    def tag_configure(self, *args, **keys):
        trace = False and not g.unitTesting
        if trace: g.trace(args, keys)
        if len(args) == 1:
            key = args[0]
            self.tags[key] = keys
            val = keys.get('foreground')
            underline = keys.get('underline')
            if val:
                # if trace: g.trace(key,val)
                self.configDict[key] = val
            if underline:
                self.configUnderlineDict[key] = True
        else:
            g.trace('oops', args, keys)

    tag_config = tag_configure
    #@-others
#@+node:ekr.20110605121601.18058: **  class QLineEditWrapper(QTextMixin)
class QLineEditWrapper(QTextMixin):
    '''
    A class to wrap QLineEdit widgets.

    The QHeadlineWrapper class is a subclass that merely
    redefines the do-nothing check method here.
    '''
    #@+others
    #@+node:ekr.20110605121601.18060: *3* qlew.Birth
    def __init__(self, widget, name, c=None):
        '''Ctor for QLineEditWrapper class.'''
        # g.trace('(QLineEditWrapper):widget',name,self.widget)
        QTextMixin.__init__(self, c)
            # Init the base class.
        self.widget = widget
        self.name = name
        self.baseClassName = 'QLineEditWrapper'

    def __repr__(self):
        return '<QLineEditWrapper: widget: %s' % (self.widget)

    __str__ = __repr__
    #@+node:ekr.20140901191541.18599: *3* qlew.check
    def check(self):
        '''
        QLineEditWrapper.
        '''
        return True
    #@+node:ekr.20110605121601.18118: *3* qlew.Widget-specific overrides
    #@+node:ekr.20110605121601.18120: *4* qlew.getAllText
    def getAllText(self):
        '''QHeadlineWrapper.'''
        if self.check():
            w = self.widget
            s = w.text()
            return g.u(s)
        else:
            return ''
    #@+node:ekr.20110605121601.18121: *4* qlew.getInsertPoint
    def getInsertPoint(self):
        '''QHeadlineWrapper.'''
        if self.check():
            i = self.widget.cursorPosition()
            return i
        else:
            return 0
    #@+node:ekr.20110605121601.18122: *4* qlew.getSelectionRange
    def getSelectionRange(self, sort=True):
        '''QHeadlineWrapper.'''
        w = self.widget
        if self.check():
            if w.hasSelectedText():
                i = w.selectionStart()
                s = w.selectedText()
                s = g.u(s)
                j = i + len(s)
            else:
                i = j = w.cursorPosition()
            return i, j
        else:
            return 0, 0
    #@+node:ekr.20110605121601.18123: *4* qlew.hasSelection
    def hasSelection(self):
        '''QHeadlineWrapper.'''
        if self.check():
            return self.widget.hasSelectedText()
        else:
            return False
    #@+node:ekr.20110605121601.18124: *4* qlew.see & seeInsertPoint
    def see(self, i):
        '''QHeadlineWrapper.'''
        pass

    def seeInsertPoint(self):
        '''QHeadlineWrapper.'''
        pass
    #@+node:ekr.20110605121601.18125: *4* qlew.setAllText
    def setAllText(self, s):
        '''Set all text of a Qt headline widget.'''
        if self.check():
            w = self.widget
            w.setText(s)
    #@+node:ekr.20110605121601.18128: *4* qlew.setFocus
    def setFocus(self):
        '''QHeadlineWrapper.'''
        if self.check():
            g.app.gui.set_focus(self.c, self.widget)
    #@+node:ekr.20110605121601.18129: *4* qlew.setInsertPoint
    def setInsertPoint(self, i, s=None):
        '''QHeadlineWrapper.'''
        if not self.check(): return
        w = self.widget
        if s is None:
            s = w.text()
            s = g.u(s)
        i = self.toPythonIndex(i)
        i = max(0, min(i, len(s)))
        w.setCursorPosition(i)
    #@+node:ekr.20110605121601.18130: *4* qlew.setSelectionRange
    def setSelectionRange(self, i, j, insert=None, s=None):
        '''QHeadlineWrapper.'''
        if not self.check(): return
        w = self.widget
        if i > j: i, j = j, i
        if s is None:
            s = w.text()
            s = g.u(s)
        n = len(s)
        i = self.toPythonIndex(i)
        j = self.toPythonIndex(j)
        i = max(0, min(i, n))
        j = max(0, min(j, n))
        if insert is None:
            insert = j
        else:
            insert = self.toPythonIndex(insert)
            insert = max(0, min(insert, n))
        if i == j:
            w.setCursorPosition(i)
        else:
            length = j - i
            # Set selection is a QLineEditMethod
            if insert < j:
                w.setSelection(j, -length)
            else:
                w.setSelection(i, length)
    # setSelectionRangeHelper = setSelectionRange
    #@-others
#@+node:ekr.20150403094619.1: ** class LeoLineTextWidget(QFrame)
class LeoLineTextWidget(QtWidgets.QFrame):
    '''A QFrame supporting gutter line numbers. This class *has* a QTextEdit.'''
    #@+others
    #@+node:ekr.20150403094706.9: *3* __init__(LeoLineTextWidget)
    def __init__(self, c, e, *args):
        '''Ctor for LineTextWidget.'''
        QtWidgets.QFrame.__init__(self, *args)
            # Init the base class.
        self.c = c
        self.setFrameStyle(self.StyledPanel | self.Sunken)
        self.edit = e # A QTextEdit
        e.setFrameStyle(self.NoFrame)
        # e.setAcceptRichText(False)
        self.number_bar = NumberBar(c, e)
        hbox = QtWidgets.QHBoxLayout(self)
        hbox.setSpacing(0)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(self.number_bar)
        hbox.addWidget(e)
        e.installEventFilter(self)
        e.viewport().installEventFilter(self)
    #@+node:ekr.20150403094706.10: *3* eventFilter
    def eventFilter(self, obj, event):
        '''
        Update the line numbers for all events on the text edit and the viewport.
        This is easier than connecting all necessary singals.
        '''
        if obj in (self.edit, self.edit.viewport()):
            self.number_bar.update()
            return False
        else:
            return QtWidgets.QFrame.eventFilter(obj, event)
    #@-others
#@+node:ekr.20110605121601.18005: ** class LeoQTextBrowser (QtWidgets.QTextBrowser)
if QtWidgets:

    class LeoQTextBrowser(QtWidgets.QTextBrowser):
        '''A subclass of QTextBrowser that overrides the mouse event handlers.'''
        #@+others
        #@+node:ekr.20110605121601.18006: *3*  lqtb.ctor (** no longer instantiates leo_h)
        def __init__(self, parent, c, wrapper):
            '''ctor for LeoQTextBrowser class.'''
            # g.trace('(LeoQTextBrowser)',c.shortFileName(),parent,wrapper)
            for attr in ('leo_c', 'leo_wrapper',):
                assert not hasattr(QtWidgets.QTextBrowser, attr), attr
            self.leo_c = c
            self.leo_s = '' # The cached text.
            self.leo_wrapper = wrapper
            self.htmlFlag = True
            QtWidgets.QTextBrowser.__init__(self, parent)
            self.setCursorWidth(c.config.getInt('qt-cursor-width') or 1)
            # Connect event handlers...
            if 0: # Not a good idea: it will complicate delayed loading of body text.
                self.textChanged.connect(self.onTextChanged)
            # This event handler is the easy way to keep track of the vertical scroll position.
            self.leo_vsb = vsb = self.verticalScrollBar()
            vsb.valueChanged.connect(self.onSliderChanged)
            # For QCompleter
            self.leo_q_completer = None
            self.leo_options = None
            self.leo_model = None
        #@+node:ekr.20110605121601.18007: *3* lqtb. __repr__ & __str__
        def __repr__(self):
            return '(LeoQTextBrowser) %s' % id(self)

        __str__ = __repr__
        #@+node:ekr.20110605121601.18008: *3* lqtb.Auto completion
        #@+node:ekr.20110605121601.18009: *4* class LeoQListWidget(QListWidget)
        class LeoQListWidget(QtWidgets.QListWidget):
            #@+others
            #@+node:ekr.20110605121601.18010: *5* lqlw.ctor
            def __init__(self, c):
                '''ctor for LeoQListWidget class'''
                QtWidgets.QListWidget.__init__(self)
                self.setWindowFlags(QtCore.Qt.Popup | self.windowFlags())
                # Make this window a modal window.
                # Calling this does not fix the Ubuntu-specific modal behavior.
                # self.setWindowModality(QtCore.Qt.NonModal) # WindowModal)
                # Inject the ivars
                self.leo_w = c.frame.body.wrapper.widget
                    # A LeoQTextBrowser, a subclass of QtWidgets.QTextBrowser.
                self.leo_c = c
                # A weird hack.
                self.leo_geom_set = False # When true, self.geom returns global coords!
                self.itemClicked.connect(self.select_callback)
            #@+node:ekr.20110605121601.18011: *5* lqlw.closeEvent
            def closeEvent(self, event):
                '''Kill completion and close the window.'''
                self.leo_c.k.autoCompleter.abort()
            #@+node:ekr.20110605121601.18012: *5* lqlw.end_completer
            def end_completer(self):
                '''End completion.'''
                # g.trace('(LeoQListWidget)')
                c = self.leo_c
                c.in_qt_dialog = False
                # This is important: it clears the autocompletion state.
                c.k.keyboardQuit()
                c.bodyWantsFocusNow()
                try:
                    self.deleteLater()
                except RuntimeError:
                    # Avoid bug 1338773: Autocompleter error
                    pass
            #@+node:ekr.20141024170936.7: *5* lqlw.get_selection
            def get_selection(self):
                '''Return the presently selected item's text.'''
                return g.u(self.currentItem().text())
            #@+node:ekr.20110605121601.18013: *5* lqlw.keyPressEvent
            def keyPressEvent(self, event):
                '''Handle a key event from QListWidget.'''
                trace = False and not g.unitTesting
                c = self.leo_c
                w = c.frame.body.wrapper
                qt = QtCore.Qt
                key = event.key()
                if event.modifiers() != qt.NoModifier and not event.text():
                    # A modifier key on it's own.
                    pass
                elif key in (qt.Key_Up, qt.Key_Down):
                    QtWidgets.QListWidget.keyPressEvent(self, event)
                elif key == qt.Key_Tab:
                    if trace: g.trace('<tab>')
                    self.tab_callback()
                elif key in (qt.Key_Enter, qt.Key_Return):
                    if trace: g.trace('<return>')
                    self.select_callback()
                else:
                    # Pass all other keys to the autocompleter via the event filter.
                    w.ev_filter.eventFilter(obj=self, event=event)
            #@+node:ekr.20110605121601.18014: *5* lqlw.select_callback
            def select_callback(self):
                '''Called when user selects an item in the QListWidget.'''
                trace = False and not g.unitTesting
                c = self.leo_c
                w = c.k.autoCompleter.w or c.frame.body.wrapper # 2014/09/19
                # Replace the tail of the prefix with the completion.
                completion = self.currentItem().text()
                prefix = c.k.autoCompleter.get_autocompleter_prefix()
                parts = prefix.split('.')
                if len(parts) > 1:
                    tail = parts[-1]
                else:
                    tail = prefix
                if trace: g.trace('prefix', repr(prefix), 'tail', repr(tail), 'completion', repr(completion))
                if tail != completion:
                    j = w.getInsertPoint()
                    i = j - len(tail)
                    w.delete(i, j)
                    w.insert(i, completion)
                    j = i + len(completion)
                    c.setChanged(True)
                    w.setInsertPoint(j)
                    c.frame.body.onBodyChanged('Typing')
                self.end_completer()
            #@+node:tbrown.20111011094944.27031: *5* lqlw.tab_callback
            def tab_callback(self):
                '''Called when user hits tab on an item in the QListWidget.'''
                trace = False and not g.unitTesting
                c = self.leo_c
                w = c.k.autoCompleter.w or c.frame.body.wrapper # 2014/09/19
                if trace: g.trace(w)
                if w is None: return
                # Replace the tail of the prefix with the completion.
                completion = g.u(self.currentItem().text())
                prefix = c.k.autoCompleter.get_autocompleter_prefix()
                parts = prefix.split('.')
                if len(parts) < 2:
                    return
                if len(parts) > 1:
                    tail = parts[-1]
                else:
                    tail = prefix
                if trace: g.trace(
                    'prefix', repr(prefix), 'tail', repr(tail),
                    'completion', repr(completion))
                i = j = w.getInsertPoint()
                s = w.getAllText()
                while(0 <= i < len(s) and s[i] != '.'):
                    i -= 1
                i += 1
                if j > i:
                    w.delete(i, j)
                w.setInsertPoint(i)
                c.k.autoCompleter.compute_completion_list()
            #@+node:ekr.20110605121601.18015: *5* lqlw.set_position
            def set_position(self, c):
                '''Set the position of the QListWidget.'''
                trace = False and not g.unitTesting

                def glob(obj, pt):
                    '''Convert pt from obj's local coordinates to global coordinates.'''
                    return obj.mapToGlobal(pt)

                w = self.leo_w
                vp = self.viewport()
                r = w.cursorRect()
                geom = self.geometry() # In viewport coordinates.
                gr_topLeft = glob(w, r.topLeft())
                # As a workaround to the Qt setGeometry bug,
                # The window is destroyed instead of being hidden.
                if self.leo_geom_set:
                    g.trace('Error: leo_geom_set')
                    return
                # This code illustrates the Qt bug...
                    # if self.leo_geom_set:
                        # # Unbelievable: geom is now in *global* coords.
                        # gg_topLeft = geom.topLeft()
                    # else:
                        # # Per documentation, geom in local (viewport) coords.
                        # gg_topLeft = glob(vp,geom.topLeft())
                gg_topLeft = glob(vp, geom.topLeft())
                delta_x = gr_topLeft.x() - gg_topLeft.x()
                delta_y = gr_topLeft.y() - gg_topLeft.y()
                # These offset are reasonable. Perhaps they should depend on font size.
                x_offset, y_offset = 10, 60
                # Compute the new geometry, setting the size by hand.
                geom2_topLeft = QtCore.QPoint(
                    geom.x() + delta_x + x_offset,
                    geom.y() + delta_y + y_offset)
                geom2_size = QtCore.QSize(400, 100)
                geom2 = QtCore.QRect(geom2_topLeft, geom2_size)
                # These tests fail once offsets are added.
                if x_offset == 0 and y_offset == 0:
                    if self.leo_geom_set:
                        if geom2.topLeft() != glob(w, r.topLeft()):
                            g.trace('Error: geom.topLeft: %s, geom2.topLeft: %s' % (
                                geom2.topLeft(), glob(w, r.topLeft())))
                    else:
                        if glob(vp, geom2.topLeft()) != glob(w, r.topLeft()):
                            g.trace('Error 2: geom.topLeft: %s, geom2.topLeft: %s' % (
                                glob(vp, geom2.topLeft()), glob(w, r.topLeft())))
                self.setGeometry(geom2)
                self.leo_geom_set = True
                if trace:
                    g.trace(self,
                        # '\n viewport:',vp,
                        # '\n size:    ',geom.size(),
                        '\n delta_x', delta_x,
                        '\n delta_y', delta_y,
                        '\n r:     ', r.x(), r.y(), glob(w, r.topLeft()),
                        '\n geom:  ', geom.x(), geom.y(), glob(vp, geom.topLeft()),
                        '\n geom2: ', geom2.x(), geom2.y(), glob(vp, geom2.topLeft()),
                    )
            #@+node:ekr.20110605121601.18016: *5* lqlw.show_completions
            def show_completions(self, aList):
                '''Set the QListView contents to aList.'''
                # g.trace('(qc) len(aList)',len(aList))
                self.clear()
                self.addItems(aList)
                self.setCurrentRow(0)
                self.activateWindow()
                self.setFocus()
            #@-others
        #@+node:ekr.20110605121601.18017: *4* lqtb.lqtb.init_completer
        def init_completer(self, options):
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
        #@+node:ekr.20110605121601.18018: *4* lqtb.redirections to LeoQListWidget
        def end_completer(self):
            if hasattr(self, 'leo_qc'):
                self.leo_qc.end_completer()
                delattr(self, 'leo_qc')

        def show_completions(self, aList):
            if hasattr(self, 'leo_qc'):
                self.leo_qc.show_completions(aList)
        #@+node:ekr.20110605121601.18019: *3* lqtb.leo_dumpButton
        def leo_dumpButton(self, event, tag):
            trace = False and not g.unitTesting
            button = event.button()
            table = (
                (QtCore.Qt.NoButton, 'no button'),
                (QtCore.Qt.LeftButton, 'left-button'),
                (QtCore.Qt.RightButton, 'right-button'),
                (QtCore.Qt.MidButton, 'middle-button'),
            )
            for val, s in table:
                if button == val:
                    kind = s; break
            else: kind = 'unknown: %s' % repr(button)
            if trace: g.trace(tag, kind)
            return kind
        #@+node:ekr.20141103061944.31: *3* lqtb.get/setXScrollPosition
        def getXScrollPosition(self):
            '''Get the horizontal scrollbar position.'''
            trace = (False or g.trace_scroll) and not g.unitTesting
            w = self
            sb = w.horizontalScrollBar()
            pos = sb.sliderPosition()
            if trace: g.trace(pos)
            return pos

        def setXScrollPosition(self, pos):
            '''Set the position of the horizontal scrollbar.'''
            trace = (False or g.trace_scroll) and not g.unitTesting
            if pos is not None:
                w = self
                if trace: g.trace(pos)
                sb = w.horizontalScrollBar()
                sb.setSliderPosition(pos)
        #@+node:ekr.20111002125540.7021: *3* lqtb.get/setYScrollPosition
        def getYScrollPosition(self):
            '''Get the vertical scrollbar position.'''
            trace = (False or g.trace_scroll) and not g.unitTesting
            w = self
            sb = w.verticalScrollBar()
            pos = sb.sliderPosition()
            if trace: g.trace(pos)
            return pos

        def setYScrollPosition(self, pos):
            '''Set the position of the vertical scrollbar.'''
            trace = (False or g.trace_scroll) and not g.unitTesting
            w = self
            if pos is None: pos = 0
            if trace: g.trace(pos)
            sb = w.verticalScrollBar()
            sb.setSliderPosition(pos)
        #@+node:ekr.20120925061642.13506: *3* lqtb.onSliderChanged
        def onSliderChanged(self, arg):
            '''Handle a Qt onSliderChanged event.'''
            trace = False and not g.unitTesting
            c = self.leo_c
            p = c.p
            # Careful: changing nodes changes the scrollbars.
            if hasattr(c.frame.tree, 'tree_select_lockout'):
                if c.frame.tree.tree_select_lockout:
                    if trace: g.trace('locked out: c.frame.tree.tree_select_lockout')
                    return
            # Only scrolling in the body pane should set v.scrollBarSpot.
            if not c.frame.body or self != c.frame.body.wrapper.widget:
                if trace: g.trace('**** wrong pane')
                return
            if p:
                if trace: g.trace(arg, c.p.v.h, g.callers())
                p.v.scrollBarSpot = arg
        #@+node:tbrown.20130411145310.18855: *3* lqtb.wheelEvent
        def wheelEvent(self, event):
            '''Handle a wheel event.'''
            if QtCore.Qt.ControlModifier & event.modifiers():
                d = {'c': self.leo_c}
                if isQt5:
                    point = event.angleDelta()
                    delta = point.y() or point.x()
                else:
                    delta = event.delta()
                if delta < 0:
                    zoom_out(d)
                else:
                    zoom_in(d)
                event.accept()
                return
            QtWidgets.QTextBrowser.wheelEvent(self, event)
        #@-others
#@+node:ekr.20150403094706.2: ** class NumberBar(QFrame)
class NumberBar(QtWidgets.QFrame):
    #@+others
    #@+node:ekr.20150403094706.3: *3* NumberBar.__init__& reloadSettings
    def __init__(self, c, e, *args):
        '''Ctor for NumberBar class.'''
        # g.trace('(NumberBar)')
        QtWidgets.QFrame.__init__(self, *args)
            # Init the base class.
        self.c = c
        self.edit = e
            # A QTextEdit.
        self.d = e.document()
            # A QTextDocument.
        self.fm = self.fontMetrics()
            # A QFontMetrics
        self.highest_line = 0
            # The highest line that is currently visibile.
        # Set the name to gutter so that the QFrame#gutter style sheet applies.
        self.setObjectName('gutter')
        self.reloadSettings()
        
    def reloadSettings(self):
        c = self.c
        c.registerReloadSettings(self)
        self.w_adjust = c.config.getInt('gutter-w-adjust') or 12
            # Extra width for column.
        self.y_adjust = c.config.getInt('gutter-y-adjust') or 10
            # The y offset of the first line of the gutter.
        
    #@+node:ekr.20150403094706.5: *3* NumberBar.update
    def update(self, *args):
        '''
        Updates the number bar to display the current set of numbers.
        Also, adjusts the width of the number bar if necessary.
        '''
        # w_adjust is used to compensate for the current line being bold.
        # Always allocate room for 2 columns
        width = self.fm.width(str(max(1000, self.highest_line))) + self.w_adjust
        if self.width() != width:
            self.setFixedWidth(width)
        QtWidgets.QWidget.update(self, *args)
    #@+node:ekr.20150403094706.6: *3* NumberBar.paintEvent
    def paintEvent(self, event):
        '''
        Enhance QFrame.paintEvent.
        Paint all visible text blocks in the editor's document.
        '''
        e = self.edit
        d = self.d
        layout = d.documentLayout()
        # Compute constants.
        current_block = d.findBlock(e.textCursor().position())
        scroll_y = e.verticalScrollBar().value()
        page_bottom = scroll_y + e.viewport().height()
        # Paint each visible block.
        painter = QtGui.QPainter(self)
        block = d.begin()
        n = i = 0
        c = self.c
        translation = c.user_dict.get('line_number_translation', [])
        while block.isValid():
            i = translation[n] if n < len(translation) else n + 1
            n += 1
            top_left = layout.blockBoundingRect(block).topLeft()
            if top_left.y() > page_bottom:
                break # Outside the visible area.
            bold = block == current_block
            self.paintBlock(bold, i, painter, top_left, scroll_y)
            block = block.next()
        self.highest_line = i
        painter.end()
        QtWidgets.QWidget.paintEvent(self, event)
            # Propagate the event.
    #@+node:ekr.20150403094706.7: *3* NumberBar.paintBlock
    def paintBlock(self, bold, n, painter, top_left, scroll_y):
        '''Paint n, right justified in the line number field.'''
        if bold:
            self.setBold(painter, True)
        s = str(n)
        pad = max(4, len(str(self.highest_line))) - len(s)
        s = ' '*pad + s
        # x = self.width() - self.fm.width(s) - self.w_adjust
        x = 0
        y = round(top_left.y()) - scroll_y + self.fm.ascent() + self.y_adjust
        painter.drawText(x, y, s)
        if bold:
            self.setBold(painter, False)
    #@+node:ekr.20150403094706.8: *3* NumberBar.setBold
    def setBold(self, painter, flag):
        '''Set or clear bold facing in the painter, depending on flag.'''
        font = painter.font()
        font.setBold(flag)
        painter.setFont(font)
    #@-others
#@+node:ekr.20140901141402.18700: ** class PlainTextWrapper(QTextMixin)
class PlainTextWrapper(QTextMixin):
    '''A Qt class for use by the find code.'''

    def __init__(self, widget):
        '''Ctor for the PlainTextWrapper class.'''
        QTextMixin.__init__(self)
        self.widget = widget
#@+node:ekr.20110605121601.18116: ** class QHeadlineWrapper (QLineEditWrapper)
class QHeadlineWrapper(QLineEditWrapper):
    '''
    A wrapper class for QLineEdit widgets in QTreeWidget's.
    This class just redefines the check method.
    '''
    #@+others
    #@+node:ekr.20110605121601.18117: *3* qhw.Birth
    def __init__(self, c, item, name, widget):
        '''The ctor for the QHeadlineWrapper class.'''
        # g.trace('(QHeadlineWrapper)',item,widget)
        assert isinstance(widget, QtWidgets.QLineEdit), widget
        QLineEditWrapper.__init__(self, widget, name, c)
            # Init the base class.
        # Set ivars.
        self.c = c
        self.item = item
        self.name = name
        self.permanent = False # Warn the minibuffer that we can go away.
        self.widget = widget
        # Set the signal.
        g.app.gui.setFilter(c, self.widget, self, tag=name)

    def __repr__(self):
        return 'QHeadlineWrapper: %s' % id(self)
    #@+node:ekr.20110605121601.18119: *3* qhw.check
    def check(self):
        '''Return True if the tree item exists and it's edit widget exists.'''
        trace = False and not g.unitTesting
        tree = self.c.frame.tree
        try:
            e = tree.treeWidget.itemWidget(self.item, 0)
        except RuntimeError:
            return False
        valid = tree.isValidItem(self.item)
        result = valid and e == self.widget
        if trace: g.trace('result %s self.widget %s itemWidget %s' % (
            result, self.widget, e))
        return result
    #@-others
#@+node:ekr.20110605121601.18131: ** class QMinibufferWrapper (QLineEditWrapper)
class QMinibufferWrapper(QLineEditWrapper):

    def __init__(self, c):
        '''Ctor for QMinibufferWrapper class.'''
        self.c = c
        w = c.frame.top.leo_ui.lineEdit # QLineEdit
        # g.trace('(QMinibufferWrapper)',w)
        QLineEditWrapper.__init__(self, widget=w, name='minibuffer', c=c)
            # Init the base class.
        assert self.widget
        g.app.gui.setFilter(c, w, self, tag='minibuffer')
        # Monkey-patch the event handlers
        #@+<< define mouseReleaseEvent >>
        #@+node:ekr.20110605121601.18132: *3* << define mouseReleaseEvent >> (QMinibufferWrapper)
        def mouseReleaseEvent(event, self=self):
            '''Override QLineEdit.mouseReleaseEvent.

            Simulate alt-x if we are not in an input state.
            '''
            trace = False and not g.unitTesting
            if trace: g.trace('(QMinibufferWrapper)', event)
            assert isinstance(self, QMinibufferWrapper), self
            assert isinstance(self.widget, QtWidgets.QLineEdit), self.widget
            c, k = self.c, self.c.k
            if not k.state.kind:
                # c.widgetWantsFocusNow(w) # Doesn't work.
                event2 = g.app.gui.create_key_event(c, w=c.frame.body.wrapper)
                k.fullCommand(event2)
                # c.outerUpdate() # Doesn't work.
        #@-<< define mouseReleaseEvent >>
        w.mouseReleaseEvent = mouseReleaseEvent

    def setStyleClass(self, style_class):
        self.widget.setProperty('style_class', style_class)
        # to get the appearance to change because of a property
        # change, unlike a focus or hover change, we need to
        # re-apply the stylesheet.  But re-applying at the top level
        # is too CPU hungry, so apply just to this widget instead.
        # It may lag a bit when the style's edited, but the new top
        # level sheet will get pushed down quite frequently.
        self.widget.setStyleSheet(self.c.frame.top.styleSheet())

    def setSelectionRange(self, i, j, insert=None, s=None):
        QLineEditWrapper.setSelectionRange(self, i, j, insert, s)
        insert = j if insert is None else insert
        if self.widget:
            self.widget._sel_and_insert = (i, j, insert)
#@+node:ekr.20110605121601.18103: ** class QScintillaWrapper(QTextMixin)
class QScintillaWrapper(QTextMixin):
    '''A wrapper for QsciScintilla supporting the high-level interface.

    This widget will likely always be less capable the QTextEditWrapper.
    To do:
    - Fix all Scintilla unit-test failures.
    - Add support for all scintilla lexers.
    '''
    #@+others
    #@+node:ekr.20110605121601.18105: *3* qsciw.ctor
    def __init__(self, widget, c, name=None):
        '''Ctor for the QScintillaWrapper class.'''
        # g.trace('(QScintillaWrapper)',c.shortFileName(),name,g.callers())
        QTextMixin.__init__(self, c)
            # init the base class.
        self.baseClassName = 'QScintillaWrapper'
        self.c = c
        self.name = name
        self.useScintilla = True
        self.widget = widget
        # Complete the init.
        self.set_config()
        # Set the signal.
        g.app.gui.setFilter(c, widget, self, tag=name)
    #@+node:ekr.20110605121601.18106: *3* qsciw.set_config
    def set_config(self):
        '''Set QScintillaWrapper configuration options.'''
        c, w = self.c, self.widget
        n = c.config.getInt('qt-scintilla-zoom-in')
        if n not in (None, 1, 0):
            w.zoomIn(n)
        # g.trace(dir(w.BraceMatch))
        w.setUtf8(True) # Important.
        if 1:
            w.setBraceMatching(2) # Sloppy
        else:
            w.setBraceMatching(0) # wrapper.flashCharacter creates big problems.
        if 0:
            w.setMarginWidth(1, 40)
            w.setMarginLineNumbers(1, True)
        w.setIndentationWidth(4)
        w.setIndentationsUseTabs(False)
        w.setAutoIndent(True)
    #@+node:ekr.20110605121601.18107: *3* qsciw.WidgetAPI
    #@+node:ekr.20140901062324.18593: *4* qsciw.delete
    def delete(self, i, j=None):
        '''Delete s[i:j]'''
        w = self.widget
        i = self.toPythonIndex(i)
        if j is None: j = i + 1
        j = self.toPythonIndex(j)
        self.setSelectionRange(i, j)
        try:
            self.changingText = True # Disable onTextChanged
            w.replaceSelectedText('')
        finally:
            self.changingText = False
    #@+node:ekr.20140901062324.18594: *4* qsciw.flashCharacter (disabled)
    def flashCharacter(self, i, bg='white', fg='red', flashes=2, delay=50):
        '''Flash the character at position i.'''
        if 0: # This causes a lot of problems: Better to use Scintilla matching.
            # This causes problems during unit tests:
            # The selection point isn't restored in time.
            if g.app.unitTesting:
                return
            #@+others
            #@+node:ekr.20140902084950.18635: *5* after
            def after(func, delay=delay):
                '''Run func after the given delay.'''
                QtCore.QTimer.singleShot(delay, func)
            #@+node:ekr.20140902084950.18636: *5* addFlashCallback
            def addFlashCallback(self=self):
                i = self.flashIndex
                w = self.widget
                self.setSelectionRange(i, i + 1)
                if self.flashBg:
                    w.setSelectionBackgroundColor(QtGui.QColor(self.flashBg))
                if self.flashFg:
                    w.setSelectionForegroundColor(QtGui.QColor(self.flashFg))
                self.flashCount -= 1
                after(removeFlashCallback)
            #@+node:ekr.20140902084950.18637: *5* removeFlashCallback
            def removeFlashCallback(self=self):
                '''Remove the extra selections.'''
                self.setInsertPoint(self.flashIndex)
                w = self.widget
                if self.flashCount > 0:
                    after(addFlashCallback)
                else:
                    w.resetSelectionBackgroundColor()
                    self.setInsertPoint(self.flashIndex1)
                    w.setFocus()
            #@-others
            # Numbered color names don't work in Ubuntu 8.10, so...
            if bg and bg[-1].isdigit() and bg[0] != '#': bg = bg[: -1]
            if fg and fg[-1].isdigit() and fg[0] != '#': fg = fg[: -1]
            # w = self.widget # A QsciScintilla widget.
            self.flashCount = flashes
            self.flashIndex1 = self.getInsertPoint()
            self.flashIndex = self.toPythonIndex(i)
            self.flashBg = None if bg.lower() == 'same' else bg
            self.flashFg = None if fg.lower() == 'same' else fg
            # g.trace(self.flashBg,self.flashFg)
            addFlashCallback()
    #@+node:ekr.20140901062324.18595: *4* qsciw.get
    def get(self, i, j=None):
        # Fix the following two bugs by using vanilla code:
        # https://bugs.launchpad.net/leo-editor/+bug/979142
        # https://bugs.launchpad.net/leo-editor/+bug/971166
        s = self.getAllText()
        i = self.toPythonIndex(i)
        j = self.toPythonIndex(j)
        return s[i: j]
    #@+node:ekr.20110605121601.18108: *4* qsciw.getAllText
    def getAllText(self):
        '''Get all text from a QsciScintilla widget.'''
        w = self.widget
        s = w.text()
        s = g.u(s)
        return s
    #@+node:ekr.20110605121601.18109: *4* qsciw.getInsertPoint
    def getInsertPoint(self):
        '''Get the insertion point from a QsciScintilla widget.'''
        w = self.widget
        i = int(w.SendScintilla(w.SCI_GETCURRENTPOS))
        return i
    #@+node:ekr.20110605121601.18110: *4* qsciw.getSelectionRange
    def getSelectionRange(self, sort=True):
        '''Get the selection range from a QsciScintilla widget.'''
        w = self.widget
        i = int(w.SendScintilla(w.SCI_GETCURRENTPOS))
        j = int(w.SendScintilla(w.SCI_GETANCHOR))
        if sort and i > j: i, j = j, i
        return i, j
    #@+node:ekr.20140901062324.18599: *4* qsciw.getX/YScrollPosition (to do)
    def getXScrollPosition(self):
        # w = self.widget
        return 0 # Not ready yet.

    def getYScrollPosition(self):
        # w = self.widget
        return 0 # Not ready yet.
    #@+node:ekr.20110605121601.18111: *4* qsciw.hasSelection
    def hasSelection(self):
        '''Return True if a QsciScintilla widget has a selection range.'''
        return self.widget.hasSelectedText()
    #@+node:ekr.20140901062324.18601: *4* qsciw.insert
    def insert(self, i, s):
        '''Insert s at position i.'''
        w = self.widget
        i = self.toPythonIndex(i)
        w.SendScintilla(w.SCI_SETSEL, i, i)
        w.SendScintilla(w.SCI_ADDTEXT, len(s), g.toEncodedString(s))
        i += len(s)
        w.SendScintilla(w.SCI_SETSEL, i, i)
        return i
    #@+node:ekr.20140901062324.18603: *4* qsciw.linesPerPage
    def linesPerPage(self):
        '''Return the number of lines presently visible.'''
        # Not used in Leo's core. Not tested.
        w = self.widget
        return int(w.SendScintilla(w.SCI_LINESONSCREEN))
    #@+node:ekr.20140901062324.18604: *4* qsciw.scrollDelegate (maybe)
    if 0: # Not yet.

        def scrollDelegate(self, kind):
            '''
            Scroll a QTextEdit up or down one page.
            direction is in ('down-line','down-page','up-line','up-page')
            '''
            c = self.c
            w = self.widget
            vScroll = w.verticalScrollBar()
            h = w.size().height()
            lineSpacing = w.fontMetrics().lineSpacing()
            n = h / lineSpacing
            n = max(2, n - 3)
            if kind == 'down-half-page': delta = n / 2
            elif kind == 'down-line': delta = 1
            elif kind == 'down-page': delta = n
            elif kind == 'up-half-page': delta = -n / 2
            elif kind == 'up-line': delta = -1
            elif kind == 'up-page': delta = -n
            else:
                delta = 0; g.trace('bad kind:', kind)
            val = vScroll.value()
            # g.trace(kind,n,h,lineSpacing,delta,val,g.callers())
            vScroll.setValue(val + (delta * lineSpacing))
            c.bodyWantsFocus()
    #@+node:ekr.20110605121601.18112: *4* qsciw.see
    def see(self, i):
        '''Ensure insert point i is visible in a QsciScintilla widget.'''
        # Ok for now.  Using SCI_SETYCARETPOLICY might be better.
        w = self.widget
        s = self.getAllText()
        i = self.toPythonIndex(i)
        row, col = g.convertPythonIndexToRowCol(s, i)
        w.ensureLineVisible(row)
    #@+node:ekr.20110605121601.18113: *4* qsciw.setAllText
    def setAllText(self, s):
        '''Set the text of a QScintilla widget.'''
        w = self.widget
        assert isinstance(w, Qsci.QsciScintilla), w
        if g.isPython3:
            w.setText(s)
        else:
            w.setText(g.toEncodedString(s))
        # w.update()
    #@+node:ekr.20110605121601.18114: *4* qsciw.setInsertPoint
    def setInsertPoint(self, i, s=None):
        '''Set the insertion point in a QsciScintilla widget.'''
        w = self.widget
        i = self.toPythonIndex(i)
        # w.SendScintilla(w.SCI_SETCURRENTPOS,i)
        # w.SendScintilla(w.SCI_SETANCHOR,i)
        w.SendScintilla(w.SCI_SETSEL, i, i)
    #@+node:ekr.20110605121601.18115: *4* qsciw.setSelectionRange
    def setSelectionRange(self, i, j, insert=None, s=None):
        '''Set the selection range in a QsciScintilla widget.'''
        w = self.widget
        i = self.toPythonIndex(i)
        j = self.toPythonIndex(j)
        insert = j if insert is None else self.toPythonIndex(insert)
        # g.trace('i',i,'j',j,'insert',insert,g.callers())
        if insert >= i:
            w.SendScintilla(w.SCI_SETSEL, i, j)
        else:
            w.SendScintilla(w.SCI_SETSEL, j, i)
    #@+node:ekr.20140901062324.18609: *4* qsciw.setX/YScrollPosition (to do)
    def setXScrollPosition(self, pos):
        '''Set the position of the horizontal scrollbar.'''
        # g.trace(pos)

    def setYScrollPosition(self, pos):
        '''Set the position of the vertical scrollbar.'''
        # g.trace(pos)
    #@-others
#@+node:ekr.20110605121601.18071: ** class QTextEditWrapper(QTextMixin)
class QTextEditWrapper(QTextMixin):
    '''A wrapper for a QTextEdit/QTextBrowser supporting the high-level interface.'''
    #@+others
    #@+node:ekr.20110605121601.18073: *3* qtew.ctor & helpers
    def __init__(self, widget, name, c=None):
        '''Ctor for QTextEditWrapper class. widget is a QTextEdit/QTextBrowser.'''
        QTextMixin.__init__(self, c)
            # Init the base class.
        # Make sure all ivars are set.
        self.baseClassName = 'QTextEditWrapper'
        self.c = c
        self.name = name
        self.widget = widget
        self.useScintilla = False
        # Complete the init.
        if c and widget:
            self.widget.setUndoRedoEnabled(False)
            self.set_config()
            self.set_signals()
    #@+node:ekr.20110605121601.18076: *4* qtew.set_config
    def set_config(self):
        '''Set configuration options for QTextEdit.'''
        c = self.c
        w = self.widget
        w.setWordWrapMode(QtGui.QTextOption.NoWrap)
        if 0: # This only works when there is no style sheet.
            n = c.config.getInt('qt-rich-text-zoom-in')
            if n not in (None, 0):
                w.zoomIn(n)
                w.updateMicroFocus()
        # tab stop in pixels - no config for this (yet)
        w.setTabStopWidth(24)
    #@+node:ekr.20140901062324.18566: *4* qtew.set_signals (should be distributed?)
    def set_signals(self):
        '''Set up signals.'''
        c, name = self.c, self.name
        if name in ('body', 'rendering-pane-wrapper') or name.startswith('head'):
            # g.trace('hooking up qt events',name)
            # Hook up qt events.
            g.app.gui.setFilter(c, self.widget, self, tag=name)
        if name == 'body':
            w = self.widget
            w.textChanged.connect(self.onTextChanged)
            w.cursorPositionChanged.connect(self.onCursorPositionChanged)
        if name in ('body', 'log'):
            # Monkey patch the event handler.
            #@+others
            #@+node:ekr.20140901062324.18565: *5* mouseReleaseEvent (monkey-patch) QTextEditWrapper
            def mouseReleaseEvent(event, self=self):
                '''
                Monkey patch for self.widget (QTextEditWrapper) mouseReleaseEvent.
                '''
                trace = False and not g.unitTesting
                assert isinstance(self, QTextEditWrapper), self
                assert isinstance(self.widget, QtWidgets.QTextEdit), self.widget
                QtWidgets.QTextEdit.mouseReleaseEvent(self.widget, event)
                    # Call the base class.
                c = self.c
                setattr(event, 'c', c)
                # Open the url on a control-click.
                if QtCore.Qt.ControlModifier & event.modifiers():
                    if trace: g.trace('(QTextEditWrapper) control-click', event)
                    g.openUrlOnClick(event)
                else:
                    if trace: g.trace('(QTextEditWrapper) click', event)
                    if name == 'body':
                        c.p.v.insertSpot = c.frame.body.wrapper.getInsertPoint()
                        if trace: g.trace('body: insertSpot:', c.p.v.insertSpot)
                    g.doHook("bodyclick2", c=c, p=c.p, v=c.p)
                    # Do *not* change the focus! This would rip focus away from tab panes.
                    c.k.keyboardQuit(setFocus=False)
            #@-others
            self.widget.mouseReleaseEvent = mouseReleaseEvent
    #@+node:ekr.20110605121601.18078: *3* qtew.High-level interface
    # These are all widget-dependent
    #@+node:ekr.20110605121601.18079: *4* qtew.delete (avoid call to setAllText)
    def delete(self, i, j=None):
        '''QTextEditWrapper.'''
        trace = False and not g.unitTesting
        w = self.widget
        if trace: g.trace(self.getSelectionRange())
        i = self.toPythonIndex(i)
        if j is None: j = i + 1
        j = self.toPythonIndex(j)
        if i > j: i, j = j, i
        if trace: g.trace(i, j)
        sb = w.verticalScrollBar()
        pos = sb.sliderPosition()
        cursor = w.textCursor()
        try:
            self.changingText = True # Disable onTextChanged
            old_i, old_j = self.getSelectionRange()
            if i == old_i and j == old_j:
                # Work around an apparent bug in cursor.movePosition.
                cursor.removeSelectedText()
            elif i == j:
                pass
            else:
                # g.trace('*** using dubious code')
                cursor.setPosition(i)
                moveCount = abs(j - i)
                cursor.movePosition(cursor.Right, cursor.KeepAnchor, moveCount)
                w.setTextCursor(cursor) # Bug fix: 2010/01/27
                if trace:
                    i, j = self.getSelectionRange()
                    g.trace(i, j)
                cursor.removeSelectedText()
                if trace: g.trace(self.getSelectionRange())
        finally:
            self.changingText = False
        sb.setSliderPosition(pos)
    #@+node:ekr.20110605121601.18080: *4* qtew.flashCharacter
    def flashCharacter(self, i, bg='white', fg='red', flashes=3, delay=75):
        '''QTextEditWrapper.'''
        # numbered color names don't work in Ubuntu 8.10, so...
        if bg[-1].isdigit() and bg[0] != '#':
            bg = bg[: -1]
        if fg[-1].isdigit() and fg[0] != '#':
            fg = fg[: -1]
        # This might causes problems during unit tests.
        # The selection point isn't restored in time.
        if g.app.unitTesting:
            return
        w = self.widget # A QTextEdit.
        e = QtGui.QTextCursor

        def after(func):
            QtCore.QTimer.singleShot(delay, func)

        def addFlashCallback(self=self, w=w):
            i = self.flashIndex
            cursor = w.textCursor() # Must be the widget's cursor.
            cursor.setPosition(i)
            cursor.movePosition(e.Right, e.KeepAnchor, 1)
            extra = w.ExtraSelection()
            extra.cursor = cursor
            if self.flashBg: extra.format.setBackground(QtGui.QColor(self.flashBg))
            if self.flashFg: extra.format.setForeground(QtGui.QColor(self.flashFg))
            self.extraSelList = [extra] # keep the reference.
            w.setExtraSelections(self.extraSelList)
            self.flashCount -= 1
            after(removeFlashCallback)

        def removeFlashCallback(self=self, w=w):
            w.setExtraSelections([])
            if self.flashCount > 0:
                after(addFlashCallback)
            else:
                w.setFocus()

        self.flashCount = flashes
        self.flashIndex = i
        self.flashBg = None if bg.lower() == 'same' else bg
        self.flashFg = None if fg.lower() == 'same' else fg
        addFlashCallback()
    #@+node:ekr.20110605121601.18081: *4* qtew.getAllText
    def getAllText(self):
        '''QTextEditWrapper.'''
        w = self.widget
        s = g.u(w.toPlainText())
        return s
    #@+node:ekr.20110605121601.18082: *4* qtew.getInsertPoint
    def getInsertPoint(self):
        '''QTextEditWrapper.'''
        return self.widget.textCursor().position()
    #@+node:ekr.20110605121601.18083: *4* qtew.getSelectionRange
    def getSelectionRange(self, sort=True):
        '''QTextEditWrapper.'''
        w = self.widget
        tc = w.textCursor()
        i, j = tc.selectionStart(), tc.selectionEnd()
        return i, j
    #@+node:ekr.20110605121601.18084: *4* qtew.getX/YScrollPosition
    # **Important**: There is a Qt bug here: the scrollbar position
    # is valid only if cursor is visible.  Otherwise the *reported*
    # scrollbar position will be such that the cursor *is* visible.

    def getXScrollPosition(self):
        '''QTextEditWrapper: Get the horizontal scrollbar position.'''
        trace = (False or g.trace_scroll) and not g.unitTesting
        w = self.widget
        sb = w.horizontalScrollBar()
        pos = sb.sliderPosition()
        if trace: g.trace(pos)
        return pos

    def getYScrollPosition(self):
        '''QTextEditWrapper: Get the vertical scrollbar position.'''
        trace = (False or g.trace_scroll) and not g.unitTesting
        w = self.widget
        sb = w.verticalScrollBar()
        pos = sb.sliderPosition()
        if trace: g.trace(pos)
        return pos
    #@+node:ekr.20110605121601.18085: *4* qtew.hasSelection
    def hasSelection(self):
        '''QTextEditWrapper.'''
        return self.widget.textCursor().hasSelection()
    #@+node:ekr.20110605121601.18089: *4* qtew.insert (avoid call to setAllText)
    def insert(self, i, s):
        '''QTextEditWrapper.'''
        w = self.widget
        i = self.toPythonIndex(i)
        cursor = w.textCursor()
        try:
            self.changingText = True # Disable onTextChanged.
            cursor.setPosition(i)
            cursor.insertText(s)
            w.setTextCursor(cursor) # Bug fix: 2010/01/27
        finally:
            self.changingText = False
    #@+node:ekr.20110605121601.18077: *4* qtew.leoMoveCursorHelper & helper
    def leoMoveCursorHelper(self, kind, extend=False, linesPerPage=15):
        '''QTextEditWrapper.'''
        trace = False and not g.unitTesting
        w = self.widget
        tc = QtGui.QTextCursor
        d = {
            'begin-line': tc.StartOfLine, # Was start-line
            'down': tc.Down,
            'end': tc.End,
            'end-line': tc.EndOfLine, # Not used.
            'exchange': True, # Dummy.
            'home': tc.Start,
            'left': tc.Left,
            'page-down': tc.Down,
            'page-up': tc.Up,
            'right': tc.Right,
            'up': tc.Up,
        }
        kind = kind.lower()
        op = d.get(kind)
        mode = tc.KeepAnchor if extend else tc.MoveAnchor
        if not op:
            return g.trace('can not happen: bad kind: %s' % kind)
        if kind in ('page-down', 'page-up'):
            self.pageUpDown(op, mode)
        elif kind == 'exchange': # exchange-point-and-mark
            cursor = w.textCursor()
            anchor = cursor.anchor()
            pos = cursor.position()
            cursor.setPosition(pos, tc.MoveAnchor)
            cursor.setPosition(anchor, tc.KeepAnchor)
            w.setTextCursor(cursor)
        else:
            if not extend:
                # Fix an annoyance. Make sure to clear the selection.
                cursor = w.textCursor()
                cursor.clearSelection()
                w.setTextCursor(cursor)
            w.moveCursor(op, mode)
        # 2012/03/25.  Add this common code.
        self.seeInsertPoint()
        if trace: g.trace(kind, 'extend', extend, 'yscroll', w.getYScrollPosition())
        self.rememberSelectionAndScroll()
        # Fix bug 218: https://github.com/leo-editor/leo-editor/issues/218
        cursor = w.textCursor()
        sel = cursor.selection().toPlainText()
        if sel and hasattr(g.app.gui, 'setClipboardSelection'):
            g.app.gui.setClipboardSelection(sel)
        self.c.frame.updateStatusLine()
    #@+node:btheado.20120129145543.8180: *5* qtew.pageUpDown
    def pageUpDown(self, op, moveMode):
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
                sb.triggerAction(QtWidgets.QAbstractSlider.SliderPageStepSub)
            else:
                cursor.movePosition(tc.Up, moveMode)
                sb.triggerAction(QtWidgets.QAbstractSlider.SliderPageStepAdd)
        control.setTextCursor(cursor)
    #@+node:ekr.20110605121601.18087: *4* qtew.linesPerPage
    def linesPerPage(self):
        '''QTextEditWrapper.'''
        # Not used in Leo's core.
        w = self.widget
        h = w.size().height()
        lineSpacing = w.fontMetrics().lineSpacing()
        n = h / lineSpacing
        return n
    #@+node:ekr.20110605121601.18088: *4* qtew.scrollDelegate
    def scrollDelegate(self, kind):
        '''
        Scroll a QTextEdit up or down one page.
        direction is in ('down-line','down-page','up-line','up-page')
        '''
        c = self.c
        w = self.widget
        vScroll = w.verticalScrollBar()
        h = w.size().height()
        lineSpacing = w.fontMetrics().lineSpacing()
        n = h / lineSpacing
        n = max(2, n - 3)
        if kind == 'down-half-page': delta = n / 2
        elif kind == 'down-line': delta = 1
        elif kind == 'down-page': delta = n
        elif kind == 'up-half-page': delta = -n / 2
        elif kind == 'up-line': delta = -1
        elif kind == 'up-page': delta = -n
        else:
            delta = 0; g.trace('bad kind:', kind)
        val = vScroll.value()
        # g.trace(kind,n,h,lineSpacing,delta,val,g.callers())
        vScroll.setValue(val + (delta * lineSpacing))
        c.bodyWantsFocus()
    #@+node:ekr.20110605121601.18090: *4* qtew.see & seeInsertPoint
    def see(self, i):
        '''Make sure position i is visible.'''
        trace = False and not g.unitTesting
        w = self.widget
        if trace:
            cursor = w.textCursor()
            g.trace('i', i, 'pos', cursor.position())
                # 'getInsertPoint',self.getInsertPoint())
        w.ensureCursorVisible()

    def seeInsertPoint(self):
        '''Make sure the insert point is visible.'''
        trace = False and not g.unitTesting
        if trace: g.trace(self.getInsertPoint())
        self.widget.ensureCursorVisible()
    #@+node:ekr.20110605121601.18092: *4* qtew.setAllText
    def setAllText(self, s):
        '''Set the text of body pane.'''
        trace = False and not g.unitTesting
        trace_time = True
        c, w = self.c, self.widget
        h = c.p.h if c.p else '<no p>'
        if trace and not trace_time: g.trace(len(s), h)
        try:
            if trace and trace_time:
                t1 = time.time()
            self.changingText = True # Disable onTextChanged.
            w.setReadOnly(False)
            w.setPlainText(s)
            if trace and trace_time:
                delta_t = time.time() - t1
                g.trace('%4.2f sec. %6s chars %s' % (delta_t, len(s), h))
        finally:
            self.changingText = False
    #@+node:ekr.20110605121601.18095: *4* qtew.setInsertPoint
    def setInsertPoint(self, i, s=None):
        # Fix bug 981849: incorrect body content shown.
        # Use the more careful code in setSelectionRange.
        self.setSelectionRange(i=i, j=i, insert=i, s=s)
    #@+node:ekr.20110605121601.18096: *4* qtew.setSelectionRange
    def setSelectionRange(self, i, j, insert=None, s=None):
        '''Set the selection range and the insert point.'''
        trace = False and not g.unitTesting
        traceTime = False and not g.unitTesting
        # Part 1
        if traceTime: t1 = time.time()
        w = self.widget
        i = self.toPythonIndex(i)
        j = self.toPythonIndex(j)
        if s is None:
            s = self.getAllText()
        n = len(s)
        i = max(0, min(i, n))
        j = max(0, min(j, n))
        if insert is None:
            ins = max(i, j)
        else:
            ins = self.toPythonIndex(insert)
            ins = max(0, min(ins, n))
        if traceTime:
            delta_t = time.time() - t1
            if delta_t > 0.1: g.trace('part1: %2.3f sec' % (delta_t))
        # Part 2:
        if traceTime: t2 = time.time()
        # 2010/02/02: Use only tc.setPosition here.
        # Using tc.movePosition doesn't work.
        tc = w.textCursor()
        if i == j:
            tc.setPosition(i)
        elif ins == j:
            # Put the insert point at j
            tc.setPosition(i)
            tc.setPosition(j, tc.KeepAnchor)
        elif ins == i:
            # Put the insert point at i
            tc.setPosition(j)
            tc.setPosition(i, tc.KeepAnchor)
        else:
            # 2014/08/21: It doesn't seem possible to put the insert point somewhere else!
            tc.setPosition(j)
            tc.setPosition(i, tc.KeepAnchor)
        w.setTextCursor(tc)
        # Fix bug 218: https://github.com/leo-editor/leo-editor/issues/218
        if hasattr(g.app.gui, 'setClipboardSelection'):
            g.app.gui.setClipboardSelection(s[i:j])
        # Remember the values for v.restoreCursorAndScroll.
        v = self.c.p.v # Always accurate.
        v.insertSpot = ins
        if i > j: i, j = j, i
        assert(i <= j)
        v.selectionStart = i
        v.selectionLength = j - i
        v.scrollBarSpot = spot = w.verticalScrollBar().value()
        if trace: g.trace('i: %s j: %s ins: %s spot: %s %s' % (i, j, ins, spot, v.h))
        if traceTime:
            delta_t = time.time() - t2
            tot_t = time.time() - t1
            if delta_t > 0.1: g.trace('part2: %2.3f sec' % (delta_t))
            if tot_t > 0.1: g.trace('total: %2.3f sec' % (tot_t))
    # setSelectionRangeHelper = setSelectionRange
    #@+node:ekr.20141103061944.40: *4* qtew.setXScrollPosition
    def setXScrollPosition(self, pos):
        '''Set the position of the horizonatl scrollbar.'''
        trace = (False or g.trace_scroll) and not g.unitTesting
        if pos is not None:
            w = self.widget
            if trace: g.trace(pos, g.callers())
            sb = w.horizontalScrollBar()
            sb.setSliderPosition(pos)
    #@+node:ekr.20110605121601.18098: *4* qtew.setYScrollPosition
    def setYScrollPosition(self, pos):
        '''Set the vertical scrollbar position.'''
        trace = (False or g.trace_scroll) and not g.unitTesting
        if pos is not None:
            w = self.widget
            if trace: g.trace(pos)
            sb = w.verticalScrollBar()
            sb.setSliderPosition(pos)
    #@+node:ekr.20110605121601.18100: *4* qtew.toPythonIndex
    def toPythonIndex(self, index, s=None):
        '''This is much faster than versions using g.toPythonIndex.'''
        w = self
        te = self.widget
        if index is None:
            return 0
        elif g.isInt(index):
            return index
        elif index == '1.0':
            return 0
        elif index == 'end':
            # g.trace('===== slow =====',repr(index))
            return w.getLastPosition()
        else:
            # g.trace('===== slow =====',repr(index))
            doc = te.document()
            data = index.split('.')
            if len(data) == 2:
                row, col = data
                row, col = int(row), int(col)
                bl = doc.findBlockByNumber(row - 1)
                return bl.position() + col
            else:
                g.trace('bad string index: %s' % index)
                return 0
    #@+node:ekr.20110605121601.18101: *4* qtew.toPythonIndexRowCol
    def toPythonIndexRowCol(self, index):
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
        return i, row, col
    #@-others
#@+node:tbrown.20130411145310.18857: ** zoom_in & zoom_out commands (qt_text.py)
@g.command("zoom-in")
def zoom_in(event=None, delta=1):
    """increase body font size by one

    requires that @font-size-body is being used in stylesheet
    """
    c = event.get('c')
    if c:
        c._style_deltas['font-size-body'] += delta
        ssm = c.styleSheetManager
        # for performance, don't c.styleSheetManager.reload_style_sheets()
        sheet = ssm.expand_css_constants(c.active_stylesheet)
        # and apply to body widget directly
        c.frame.body.wrapper.widget.setStyleSheet(sheet)

@g.command("zoom-out")
def zoom_out(event=None):
    """decrease body font size by one

    requires that @font-size-body is being used in stylesheet
    """
    zoom_in(event=event, delta=-1)
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
