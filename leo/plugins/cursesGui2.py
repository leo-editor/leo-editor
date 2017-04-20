#@+leo-ver=5-thin
#@+node:ekr.20170419092835.1: * @file cursesGui2.py
'''A prototype text gui using the python curses library.'''
#@+<< cursesGui imports >>
#@+node:ekr.20170419172102.1: ** << cursesGui imports >>
import sys
import leo.core.leoGlobals as g
# import leo.core.leoFrame as leoFrame
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
        self.log = CursesLog(c)
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
        self.consoleOnly = False # Required attribute.
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
        if 1:
            print('CG.runMainLoop')
            # print accumulated traces.
        else:
            w = curses.initscr()
            w.addstr('enter characters: x quits')
            while 1:
                i = w.getch() # Returns an int.
                ch = chr(i)
                if ch == 'x': break
        sys.exit(0)
    #@-others
#@+node:ekr.20170419143731.1: ** class CursesLog
class CursesLog: ### (leoFrame.LeoLog):
   '''A class that represents curses log pane.'''
   #@+others
   #@+node:ekr.20170419143731.2: *3* CLog.cmd (decorator)
   def cmd(name):
       '''Command decorator for the c.frame.log class.'''
       # pylint: disable=no-self-argument
       return g.new_cmd_decorator(name, ['c', 'frame', 'log'])
   #@+node:ekr.20170419143731.4: *3* CLog.__init__
   def __init__(self, c): ### frame, parentFrame):
       '''Ctor for CLog class.'''
       self.c = c
       self.enabled = True
       self.isNull = False
       
       ### from LeoQtLog
           # leoFrame.LeoLog.__init__(self, frame, parentFrame)
               # # Init the base class. Calls createControl.
           # assert self.logCtrl is None, self.logCtrl # Set in finishCreate.
               # # Important: depeding on the log *tab*,
               # # logCtrl may be either a wrapper or a widget.
           # self.c = frame.c # Also set in the base constructor, but we need it here.
       
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
   #@+node:ekr.20170419143731.7: *3* CLog.Commands
   @cmd('clear-log')
   def clearLog(self, event=None):
       '''Clear the log pane.'''
       # w = self.logCtrl.widget # w is a QTextBrowser
       # if w:
           # w.clear()
   #@+node:ekr.20170420040818.1: *3* CLog.Entries
   #@+node:ekr.20170420035717.1: *4* CLog.enable/disable
   def disable(self):
       self.enabled = False

   def enable(self, enabled=True):
       self.enabled = enabled
   #@+node:ekr.20170420041119.1: *4* CLog.finishCreate
   def finishCreate(self):
       '''CursesLog.finishCreate.'''
       pass
   #@+node:ekr.20170419143731.15: *4* CLog.put
   def put(self, s, color=None, tabName='Log', from_redirect=False):
       '''All output to the log stream eventually comes here.'''
       c = self.c
       if g.app.quitting or not c or not c.exists:
           print('CLog.log.put fails', repr(s))
           return
       g.trace(repr(s))
       # trace = False and not g.unitTesting
       # trace_s = False
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
       # This is not called normally.
       # print('CLog.put: %s' % g.callers())
       if g.app.quitting:
           return
       g.trace('=====', g.callers())
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
