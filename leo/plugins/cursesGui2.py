#@+leo-ver=5-thin
#@+node:ekr.20170419092835.1: * @file cursesGui2.py
'''A prototype text gui using the python curses library.'''
#@+<< cursesGui imports >>
#@+node:ekr.20170419172102.1: ** << cursesGui imports >>
import sys
import leo.core.leoGlobals as g
import leo.core.leoFrame as leoFrame
import leo.core.leoGui as leoGui
try:
    import curses
except ImportError:
    curses = None
#@-<< cursesGui imports >>
#@+others
#@+node:ekr.20170419094705.1: ** init (cursesGui2.py)
def init():

    ok = curses and not g.app.gui and not g.app.unitTesting
        # Not Ok for unit testing!
    if ok:
        g.app.gui = CursesGui()
        g.app.root = g.app.gui.createRootWindow()
        g.app.gui.finishCreate()
        g.plugin_signon(__name__)
    elif g.app.gui and not g.app.unitTesting:
        s = "Can't install text gui: previous gui installed"
        g.es_print(s, color="red")
    return ok
#@+node:ekr.20170419105852.1: ** class CursesFrame
class CursesFrame:
    
    def __init__ (self, c, title):
        self.c = c
        self.d = {}
        self.title = title
        self.menu = CursesMenu(c)
        
    #@+others
    #@+node:ekr.20170419111214.1: *3* CF.__getattr__
    # https://docs.python.org/2/reference/datamodel.html#object.__getattr__
    def __getattr__(self, name):
        aList = self.d.get(name, [])
        callers = g.callers(4)
        if callers not in aList:
            aList.append(callers)
            self.d[name] = aList
            g.trace('%30s' % ('CursesFrame.' + name), callers)
        return g.NullObject()
            # Or just raise AttributeError.
    #@+node:ekr.20170419111305.1: *3* CF.getShortCut
    def getShortCut(self, *args, **kwargs):
        return None
    #@-others
    
#@+node:ekr.20170419094731.1: ** class CursesGui
class CursesGui(leoGui.LeoGui):
    '''A do-nothing curses gui template.'''

    def __init__(self):
        self.consoleOnly = True # Affects g.es, etc.
        self.d = {}
            # Keys are names, values of lists of g.callers values.
            
    #@+others
    #@+node:ekr.20170419110330.1: *3* CG.__getattr__
    # https://docs.python.org/2/reference/datamodel.html#object.__getattr__
    def __getattr__(self, name):
        aList = self.d.get(name, [])
        callers = g.callers(4)
        if callers not in aList:
            aList.append(callers)
            self.d[name] = aList
            g.trace('%30s' % ('CursesGui.' + name), callers)
        return g.NullObject()
            # Or just raise AttributeError.
    #@+node:ekr.20170419110052.1: *3* CG.createLeoFrame
    def createLeoFrame(self, c, title):
        
        return CursesFrame(c, title)
    #@+node:ekr.20170419111744.1: *3* CG.Focus...
    def get_focus(self, *args, **keys):
        return None
    #@+node:ekr.20170419140914.1: *3* CG.runMainLoop
    def runMainLoop(self):
        '''The curses gui main loop.'''
        w = curses.initscr()
        w.addstr('enter characters: x quits')
        while 1:
            i = w.getch() # Returns an int.
            ch = chr(i)
            if ch == 'x': break
        sys.exit(0)
    #@-others
#@+node:ekr.20170419143731.1: ** class CursesLog (LeoLog) (disabled)
if 0:
    class CursesLog(leoFrame.LeoLog):
        '''A class that represents cursese log pane.'''
        #@+others
        #@+node:ekr.20170419143731.2: *3* CLog.cmd (decorator)
        def cmd(name):
            '''Command decorator for the c.frame.log class.'''
            # pylint: disable=no-self-argument
            return g.new_cmd_decorator(name, ['c', 'frame', 'log'])
        #@+node:ekr.20170419144232.1: *3* CLog.__getattr__
        # https://docs.python.org/2/reference/datamodel.html#object.__getattr__
        def __getattr__(self, name):
            aList = self.d.get(name, [])
            callers = g.callers(4)
            if callers not in aList:
                aList.append(callers)
                self.d[name] = aList
                g.trace('%30s' % ('CursesLog.' + name), callers)
            return g.NullObject()
                # Or just raise AttributeError.
        #@+node:ekr.20170419143731.3: *3* CLog.Birth
        #@+node:ekr.20170419143731.4: *4* CLog.__init__
        def __init__(self, frame, parentFrame):
            '''Ctor for CLog class.'''
            # g.trace('(CLog)',frame,parentFrame)
            leoFrame.LeoLog.__init__(self, frame, parentFrame)
                # Init the base class. Calls createControl.
            assert self.logCtrl is None, self.logCtrl # Set in finishCreate.
                # Important: depeding on the log *tab*,
                # logCtrl may be either a wrapper or a widget.
            self.c = frame.c # Also set in the base constructor, but we need it here.
            
            
            # if 0:
                # self.contentsDict = {} # Keys are tab names.  Values are widgets.
                # self.eventFilters = [] # Apparently needed to make filters work!
                # self.logDict = {} # Keys are tab names text widgets.  Values are the widgets.
                # self.logWidget = None # Set in finishCreate.
                # self.menu = None # A menu that pops up on right clicks in the hull or in tabs.
                # self.tabWidget = tw = c.frame.top.leo_ui.tabWidget
                    # # The Qt.QTabWidget that holds all the tabs.
                # # Fixes bug 917814: Switching Log Pane tabs is done incompletely.
                # tw.currentChanged.connect(self.onCurrentChanged)
                # self.wrap = bool(c.config.getBool('log_pane_wraps'))
                # if 0: # Not needed to make onActivateEvent work.
                    # # Works only for .tabWidget, *not* the individual tabs!
                    # theFilter = qt_events.LeoQtEventFilter(c, w=tw, tag='tabWidget')
                    # tw.installEventFilter(theFilter)
                # # 2013/11/15: Partial fix for bug 1251755: Log-pane refinements
                # tw.setMovable(True)
        #@+node:ekr.20170419143731.5: *4* CLog.finishCreate
        def finishCreate(self):
            '''Finish creating the CLog class.'''
            # c = self.c; log = self
            # w = self.tabWidget
            # # Remove unneeded tabs.
            # for name in ('Tab 1', 'Page'):
                # for i in range(w.count()):
                    # if name == w.tabText(i):
                        # w.removeTab(i)
                        # break
            # # Rename the 'Tab 2' tab to 'Find'.
            # for i in range(w.count()):
                # if w.tabText(i) in ('Find', 'Tab 2'):
                    # w.setTabText(i, 'Find')
                    # self.contentsDict['Find'] = w.currentWidget()
                    # break
            # # Create the log tab as the leftmost tab.
            # # log.selectTab('Log')
            # log.createTab('Log')
            # logWidget = self.contentsDict.get('Log')
            # option = QtGui.QTextOption
            # logWidget.setWordWrapMode(
                # option.WordWrap if self.wrap else option.NoWrap)
            # for i in range(w.count()):
                # if w.tabText(i) == 'Log':
                    # w.removeTab(i)
            # w.insertTab(0, logWidget, 'Log')
            # c.spellCommands.openSpellTab()
        #@+node:ekr.20170419143731.6: *4* CLog.getName
        def getName(self):
            return 'log' # Required for proper pane bindings.
        #@+node:ekr.20170419143731.7: *3* CLog.Commands
        @cmd('clear-log')
        def clearLog(self, event=None):
            '''Clear the log pane.'''
            # w = self.logCtrl.widget # w is a QTextBrowser
            # if w:
                # w.clear()
        #@+node:ekr.20170419143731.8: *3* CLog.color tab stuff
        def createColorPicker(self, tabName):
            g.warning('color picker not ready for curses gui')
        #@+node:ekr.20170419143731.9: *3* CLog.font tab stuff
        #@+node:ekr.20170419143731.10: *4* CLog.createFontPicker
        # def createFontPicker(self, tabName):
            # # log = self
            # QFont = QtGui.QFont
            # font, ok = QtWidgets.QFontDialog.getFont()
            # if not (font and ok): return
            # style = font.style()
            # table = (
                # (QFont.StyleNormal, 'normal'),
                # (QFont.StyleItalic, 'italic'),
                # (QFont.StyleOblique, 'oblique'))
            # for val, name in table:
                # if style == val:
                    # style = name
                    # break
            # else:
                # style = ''
            # weight = font.weight()
            # table = (
                # (QFont.Light, 'light'),
                # (QFont.Normal, 'normal'),
                # (QFont.DemiBold, 'demibold'),
                # (QFont.Bold, 'bold'),
                # (QFont.Black, 'black'))
            # for val, name in table:
                # if weight == val:
                    # weight = name
                    # break
            # else:
                # weight = ''
            # table = (
                # ('family', str(font.family())),
                # ('size  ', font.pointSize()),
                # ('style ', style),
                # ('weight', weight),
            # )
            # for key, val in table:
                # if val: g.es(key, val, tabName='Fonts')
        #@+node:ekr.20170419143731.11: *4* CLog.hideFontTab
        # def hideFontTab(self, event=None):
            # c = self.c
            # c.frame.log.selectTab('Log')
            # c.bodyWantsFocus()
        #@+node:ekr.20170419143731.12: *3* CLog.isLogWidget
        # def isLogWidget(self, w):
            # val = w == self or w in list(self.contentsDict.values())
            # # g.trace(val,w)
            # return val
        #@+node:ekr.20170419143731.13: *3* CLog.onCurrentChanged
        # def onCurrentChanged(self, idx):
        #    
            # trace = False and not g.unitTesting
            # tabw = self.tabWidget
            # w = tabw.widget(idx)
            # # Fixes bug 917814: Switching Log Pane tabs is done incompletely
            # wrapper = hasattr(w, 'leo_log_wrapper') and w.leo_log_wrapper
            # if wrapper:
                # self.logCtrl = wrapper
            # if trace: g.trace(idx, tabw.tabText(idx), self.c.frame.title) # wrapper and wrapper.widget)
        #@+node:ekr.20170419143731.14: *3* CLog.put & putnl
        #@+node:ekr.20170419143731.15: *4* CLog.put
        def put(self, s, color=None, tabName='Log', from_redirect=False):
            '''All output to the log stream eventually comes here.'''
            g.trace(s)
            # trace = False and not g.unitTesting
            # trace_s = False
            # c = self.c
            # if g.app.quitting or not c or not c.exists:
                # print('CLog.log.put fails', repr(s))
                # return
            # if color:
                # color = leoColor.getColor(color, 'black')
            # else:
                # color = leoColor.getColor('black')
            # self.selectTab(tabName or 'Log')
            # # Must be done after the call to selectTab.
            # w = self.logCtrl.widget # w is a QTextBrowser
            # if w:
                # if trace:
                    # g.trace(id(self.logCtrl), c.shortFileName())
                # sb = w.horizontalScrollBar()
                # s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                # if not self.wrap: # 2010/02/21: Use &nbsp; only when not wrapping!
                    # s = s.replace(' ', '&nbsp;')
                # if from_redirect:
                    # s = s.replace('\n', '<br>')
                # else:
                    # s = s.rstrip().replace('\n', '<br>')
                # s = '<font color="%s">%s</font>' % (color, s)
                # if trace and trace_s:
                    # # print('CLog.put: %4s redirect: %5s\n  %s' % (
                        # # len(s), from_redirect, s))
                    # print('CLog.put: %r' % (s))
                # if from_redirect:
                    # w.insertHtml(s)
                # else:
                    # # w.append(s)
                        # # w.append is a QTextBrowser method.
                        # # This works.
                    # # This also works.  Use it to see if it fixes #301:
                    # # Log window doesn't get line separators
                    # w.insertHtml(s+'<br>')
                # w.moveCursor(QtGui.QTextCursor.End)
                # sb.setSliderPosition(0) # Force the slider to the initial position.
            # else:
                # # put s to logWaiting and print s
                # g.app.logWaiting.append((s, color),)
                # if g.isUnicode(s):
                    # s = g.toEncodedString(s, "ascii")
                # print(s)
        #@+node:ekr.20170419143731.16: *4* CLog.putnl
        def putnl(self, tabName='Log'):
            '''Put a newline to the Qt log.'''
            g.trace()
            # This is not called normally.
            # print('CLog.put: %s' % g.callers())
            # if g.app.quitting:
                # return
            # if tabName:
                # self.selectTab(tabName)
            # w = self.logCtrl.widget
            # if w:
                # sb = w.horizontalScrollBar()
                # pos = sb.sliderPosition()
                # # Not needed!
                    # # contents = w.toHtml()
                    # # w.setHtml(contents + '\n')
                # w.moveCursor(QtGui.QTextCursor.End)
                # sb.setSliderPosition(pos)
                # w.repaint() # Slow, but essential.
            # else:
                # # put s to logWaiting and print  a newline
                # g.app.logWaiting.append(('\n', 'black'),)
        #@+node:ekr.20170419143731.17: *4* CLog.scrollToEnd
        def scrollToEnd(self, tabName='Log'):
            '''Scroll the log to the end.'''
            # if g.app.quitting:
                # return
            # if tabName:
                # self.selectTab(tabName)
            # w = self.logCtrl.widget
            # if w:
                # sb = w.horizontalScrollBar()
                # pos = sb.sliderPosition()
                # w.moveCursor(QtGui.QTextCursor.End)
                # sb.setSliderPosition(pos)
                # w.repaint() # Slow, but essential.
        #@+node:ekr.20170419143731.19: *3* CLog.Tab (disabled)
        if 0:
            #@+others
            #@+node:ekr.20170419143731.20: *4* CLog.clearTab
            def clearTab(self, tabName, wrap='none'):
                w = self.logDict.get(tabName)
                if w:
                    w.clear() # w is a QTextBrowser.
            #@+node:ekr.20170419143731.21: *4* CLog.createTab
            def createTab(self, tabName, createText=True, widget=None, wrap='none'):
                """
                Create a new tab in tab widget
                if widget is None, Create a QTextBrowser,
                suitable for log functionality.
                """
                # trace = False and not g.unitTesting
                # c = self.c
                # if trace: g.trace(tabName, widget and g.app.gui.widget_name(widget) or '<no widget>')
                # if widget is None:
                    # widget = qt_text.LeoQTextBrowser(parent=None, c=c, wrapper=self)
                        # # widget is subclass of QTextBrowser.
                    # contents = qt_text.QTextEditWrapper(widget=widget, name='log', c=c)
                        # # contents a wrapper.
                    # widget.leo_log_wrapper = contents
                        # # Inject an ivar into the QTextBrowser that points to the wrapper.
                    # if trace: g.trace('** creating', tabName, 'widget', widget, 'wrapper', contents)
                    # option = QtGui.QTextOption
                    # widget.setWordWrapMode(option.WordWrap if self.wrap else option.NoWrap)
                    # widget.setReadOnly(False) # Allow edits.
                    # self.logDict[tabName] = widget
                    # if tabName == 'Log':
                        # self.logCtrl = contents
                        # widget.setObjectName('log-widget')
                    # # Set binding on all log pane widgets.
                    # g.app.gui.setFilter(c, widget, self, tag='log')
                    # self.contentsDict[tabName] = widget
                    # self.tabWidget.addTab(widget, tabName)
                # else:
                    # contents = widget
                        # # Unlike text widgets, contents is the actual widget.
                    # widget.leo_log_wrapper = contents
                        # # The leo_log_wrapper is the widget itself.
                    # if trace: g.trace('** using', tabName, widget)
                    # g.app.gui.setFilter(c, widget, contents, 'tabWidget')
                    # self.contentsDict[tabName] = contents
                    # self.tabWidget.addTab(contents, tabName)
                # return contents
            #@+node:ekr.20170419143731.22: *4* CLog.cycleTabFocus
            def cycleTabFocus(self, event=None):
                '''Cycle keyboard focus between the tabs in the log pane.'''
                trace = False and not g.unitTesting
                w = self.tabWidget
                i = w.currentIndex()
                i += 1
                if i >= w.count():
                    i = 0
                tabName = w.tabText(i)
                self.selectTab(tabName, createText=False)
                if trace: g.trace('(CLog)', i, w, w.count(), w.currentIndex(), g.u(tabName))
                return i
            #@+node:ekr.20170419143731.23: *4* CLog.deleteTab
            def deleteTab(self, tabName, force=False):
                '''Delete the tab if it exists.  Otherwise do *nothing*.'''
                c = self.c
                w = self.tabWidget
                if force or tabName not in ('Log', 'Find', 'Spell'):
                    for i in range(w.count()):
                        if tabName == w.tabText(i):
                            w.removeTab(i)
                            self.selectTab('Log')
                            c.invalidateFocus()
                            c.bodyWantsFocus()
                            return
            #@+node:ekr.20170419143731.24: *4* CLog.hideTab
            def hideTab(self, tabName):
                self.selectTab('Log')
            #@+node:ekr.20170419143731.25: *4* CLog.orderedTabNames
            def orderedTabNames(self, LeoLog=None): # Unused: LeoLog
                '''Return a list of tab names in the order in which they appear in the QTabbedWidget.'''
                w = self.tabWidget
                return [w.tabText(i) for i in range(w.count())]
            #@+node:ekr.20170419143731.26: *4* CLog.numberOfVisibleTabs
            def numberOfVisibleTabs(self):
                return len([val for val in self.contentsDict.values() if val is not None])
                    # **Note**: the base-class version of this uses frameDict.
            #@+node:ekr.20170419143731.27: *4* CLog.selectTab & helper
            # createText is used by LeoLog.selectTab.

            def selectTab(self, tabName, createText=True, widget=None, wrap='none'):
                '''Create the tab if necessary and make it active.'''
                if not self.selectHelper(tabName):
                    self.createTab(tabName, widget=widget, wrap=wrap)
                    self.selectHelper(tabName)
            #@+node:ekr.20170419143731.28: *5* CLog.selectHelper
            def selectHelper(self, tabName):
                trace = False and not g.unitTesting
                c, w = self.c, self.tabWidget
                for i in range(w.count()):
                    if tabName == w.tabText(i):
                        w.setCurrentIndex(i)
                        widget = w.widget(i)
                        # 2011/11/21: Set the .widget ivar only if there is a wrapper.
                        wrapper = hasattr(widget, 'leo_log_wrapper') and widget.leo_log_wrapper
                        if wrapper: self.logCtrl = wrapper
                        if trace: g.trace(tabName, 'widget', widget, 'wrapper', wrapper)
                        # Do *not* set focus here!
                            # c.widgetWantsFocus(tab_widget)
                        if tabName == 'Find':
                            # Fix bug 1254861: Ctrl-f doesn't ensure find input field visible.
                            if c.config.getBool('auto-scroll-find-tab', default=True):
                                # This is the cause of unwanted scrolling.
                                findbox = c.findCommands.ftm.find_findbox
                                if hasattr(widget, 'ensureWidgetVisible'):
                                    widget.ensureWidgetVisible(findbox)
                                else:
                                    findbox.setFocus()
                        elif tabName == 'Spell':
                            # the base class uses this as a flag to see if
                            # the spell system needs initing
                            self.frameDict['Spell'] = widget
                        self.tabName = tabName # 2011/11/20
                        return True
                # General case.
                self.tabName = None # 2011/11/20
                if trace: g.trace('** not found', tabName)
                return False
            #@-others
        #@-others
#@+node:ekr.20170419111515.1: ** class CursesMenu
class CursesMenu:
    
    def __init__ (self, c):
        self.c = c
        self.d = {}
        
    #@+others
    #@+node:ekr.20170419111555.1: *3* CM.__getattr__
    # https://docs.python.org/2/reference/datamodel.html#object.__getattr__
    def __getattr__(self, name):
        aList = self.d.get(name, [])
        callers = g.callers(4)
        if callers not in aList:
            aList.append(callers)
            self.d[name] = aList
            g.trace('%30s' % ('CursesMenu.' + name), callers)
        return g.NullObject()
            # Or just raise AttributeError.
    #@-others
#@-others
#@@language python
#@@tabwidth -3
#@-leo
