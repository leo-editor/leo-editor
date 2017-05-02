#@+leo-ver=5-thin
#@+node:ekr.20170419092835.1: * @file cursesGui2.py
'''A prototype text gui using the python curses library.'''
#@+<< cursesGui imports >>
#@+node:ekr.20170419172102.1: **  << cursesGui imports >>
import leo.core.leoGlobals as g
import logging
import logging.handlers
import sys
# import traceback
import leo.core.leoFrame as leoFrame
import leo.core.leoGui as leoGui
import leo.core.leoMenu as leoMenu
try:
    import curses
except ImportError:
    curses = None

npyscreen = g.importExtension(
    'npyscreen',
    pluginName=None,
    required=True,
    verbose=False,
)
#@-<< cursesGui imports >>
# pylint: disable=arguments-differ,logging-not-lazy
#@+others
#@+node:ekr.20170501043944.1: **  top-level
#@+node:ekr.20170419094705.1: *3* init (cursesGui2.py)
def init():
    '''
    top-level init for cursesGui2.py pseudo-plugin.
    This plugin should be loaded only from leoApp.py.
    '''
    if g.app.gui:
        if not g.app.unitTesting:
            s = "Can't install text gui: previous gui installed"
            g.es_print(s, color="red")
        return False
    else:
        return curses and not g.app.gui and not g.app.unitTesting
            # Not Ok for unit testing!
#@+node:ekr.20170501032705.1: *3* leoGlobals replacements
# CGui.init_logger monkey-patches leoGlobals with these functions.
#@+node:ekr.20170430112645.1: *4* es
def es(*args, **keys):
    '''Monkey-patch for g.es.'''
    d = {
        'color': None,
        'commas': False,
        'newline': True,
        'spaces': True,
        'tabName': 'Log',
    }
    d = g.doKeywordArgs(keys, d)
    color = d.get('color')
    s = g.translateArgs(args, d)
    if isinstance(g.app.gui, CursesGui):
        if g.app.gui.log_inited:
            g.app.gui.log.put(s, color=color)
        else:
            g.app.gui.wait_list.append((s, color),)
    # else: logging.info(' KILL: %r' % s)
#@+node:ekr.20170501043411.1: *4* pr
def pr(*args, **keys):
    '''Monkey-patch for g.pr.'''
    d = {'commas': False, 'newline': True, 'spaces': True}
    d = g.doKeywordArgs(keys, d)
    s = g.translateArgs(args, d)
    logging.info('   pr: %r' % s)
#@+node:ekr.20170429165242.1: *4* trace
def trace(*args, **keys):
    '''Monkey-patch for g.trace.'''
    d = {
        'align': 0,
        'before': '',
        'newline': True,
        'caller_level': 1,
        'noname': False,
    }
    d = g.doKeywordArgs(keys, d)
    align = d.get('align', 0)
    caller_level = d.get('caller_level', 1)
    # Compute the caller name.
    if d.get('noname'):
        name = ''
    else:
        try: # get the function name from the call stack.
            f1 = sys._getframe(caller_level) # The stack frame, one level up.
            code1 = f1.f_code # The code object
            name = code1.co_name # The code name
        except Exception:
            name = g.shortFileName(__file__)
        if name == '<module>':
            name = g.shortFileName(__file__)
        if name.endswith('.pyc'):
            name = name[: -1]
    # Pad the caller name.
    if align != 0 and len(name) < abs(align):
        pad = ' ' * (abs(align) - len(name))
        if align > 0: name = name + pad
        else: name = pad + name
    # Munge *args into s.
    result = [name] if name else []
    for arg in args:
        if g.isString(arg):
            pass
        elif g.isBytes(arg):
            arg = g.toUnicode(arg)
        else:
            arg = repr(arg)
        if result:
            result.append(" " + arg)
        else:
            result.append(arg)
    # s = d.get('before') + ''.join(result)
    s = ''.join(result)
    logging.info('trace: %r' % s)
#@+node:ekr.20170420054211.1: ** class CursesApp (NPSApp)
class CursesApp(npyscreen.NPSApp):
    '''
    The anonymous npyscreen application object, created from
    CGui.runMainLoop.
    
    This is *not* g.app. There is no need for a reference to it.
    '''
    
    def __init__(self):
        g.trace('CursesApp')
        npyscreen.NPSApp.__init__(self)
            # Init the base class.

    #@+others
    #@+node:ekr.20170420090426.1: *3* CApp.main
    def main(self):
        '''Create and start Leo's singleton npyscreen window.
        '''
        g.app.gui.run()

    #@+node:ekr.20170501120748.1: *3* CApp.writeWaitingLog (do nothing)
    def writeWaitingLog(self, c):
        '''Write all waiting lines to the log.'''
        # Done in CApp.main.
    #@-others
#@+node:ekr.20170501024433.1: ** class CursesBody
#@+node:ekr.20170419105852.1: ** class CursesFrame (LeoFrame)
class CursesFrame (leoFrame.LeoFrame):
    '''
    The LeoFrame when --gui=curses is in effect.
    '''
    
    #@+others
    #@+node:ekr.20170501155347.1: *3* CFrame.birth
    def __init__ (self, c, title):
        
        g.trace('CursesFrame', c.shortFileName())
        leoFrame.LeoFrame.instances += 1 # Increment the class var.
        leoFrame.LeoFrame.__init__(self, c, gui=g.app.gui)
            # Init the base class.
        assert self.c == c
        self.log = CursesLog(c)
        g.app.gui.log = self.log
        self.title = title
        # Standard ivars.
        self.ratio = self.secondary_ratio = 0.0
        # Widgets
        self.body = None
        self.menu = CursesMenu(c)
        self.miniBufferWidget = None
        self.top = None
        self.tree = g.NullObject()
        
        # ===============
        # Official ivars...
        ### self.iconBar = None
        ### self.iconBarClass = None ### self.QtIconBarClass
        ### self.initComplete = False # Set by initCompleteHint().
        ### self.minibufferVisible = True
        ### self.statusLineClass = None ### self.QtStatusLineClass
        ###
            # Config settings.
            # self.trace_status_line = c.config.getBool('trace_status_line')
            # self.use_chapters = c.config.getBool('use_chapters')
            # self.use_chapter_tabs = c.config.getBool('use_chapter_tabs')
        ###
        ### self.set_ivars()
        ###
        # "Official ivars created in createLeoFrame and its allies.
        ### self.bar1 = None
        ### self.bar2 = None
        ### self.f1 = self.f2 = None
        ### self.findPanel = None # Inited when first opened.
        ### self.iconBarComponentName = 'iconBar'
        ### self.iconFrame = None
        ### self.canvas = None
        ### self.outerFrame = None
        ### self.statusFrame = None
        ### self.statusLineComponentName = 'statusLine'
        ### self.statusText = None
        ### self.statusLabel = None
        ### self.top = None # This will be a class Window object.
        # Used by event handlers...
        # self.controlKeyIsDown = False # For control-drags
        # self.isActive = True
        # self.redrawCount = 0
        # self.wantedWidget = None
        # self.wantedCallbackScheduled = False
        # self.scrollWay = None
    #@+node:ekr.20170420163932.1: *4* CFrame.finishCreate (To do)
    def finishCreate(self):
        g.trace('CursesFrame')
        g.app.windowList.append(self)
        ### Not yet.
            # c = self.c
            # assert c
            # self.top = g.app.gui.frameFactory.createFrame(self)
            # self.createIconBar() # A base class method.
            ### self.createSplitterComponents()
            # self.createStatusLine() # A base class method.
            # self.createFirstTreeNode() # Call the base-class method.
            ### self.menu = LeoQtMenu(c, self, label='top-level-menu')
            ### self.miniBufferWidget = qt_text.QMinibufferWrapper(c)
            ### c.bodyWantsFocus()
    #@+node:ekr.20170419111305.1: *3* CFrame.getShortCut
    def getShortCut(self, *args, **kwargs):
        return None
    #@+node:ekr.20170501161029.1: *3* CFrame.must be defined in subclasses
    def bringToFront(self):
        pass
        # self.lift()

    def deiconify(self):
        pass
        # if self.top and self.top.isMinimized(): # Bug fix: 400739.
            # self.lift()

    def getFocus(self):
        pass ### To do
        # return g.app.gui.get_focus(self.c) # Bug fix: 2009/6/30.

    def get_window_info(self):
        pass
        # if hasattr(self.top, 'leo_master') and self.top.leo_master:
            # f = self.top.leo_master
        # else:
            # f = self.top
        # rect = f.geometry()
        # topLeft = rect.topLeft()
        # x, y = topLeft.x(), topLeft.y()
        # w, h = rect.width(), rect.height()
        # return w, h, x, y

    def iconify(self):
        pass
        # if self.top: self.top.showMinimized()

    def lift(self):
        pass
        # if not self.top: return
        # if self.top.isMinimized(): # Bug 379141
            # self.top.showNormal()
        # self.top.activateWindow()
        # self.top.raise_()

    def getTitle(self):
        return self.c.title
        # # Fix https://bugs.launchpad.net/leo-editor/+bug/1194209
        # # When using tabs, leo_master (a LeoTabbedTopLevel) contains the QMainWindow.
        # w = self.top.leo_master if g.app.qt_use_tabs else self.top
        # s = g.u(w.windowTitle())
        # return s
        
    def resizePanesToRatio(self, ratio, secondary_ratio):
        '''Resize splitter1 and splitter2 using the given ratios.'''
        # g.trace('vertical: %5s, %0.2f %0.2f' % (
            # self.splitVerticalFlag, ratio, secondary_ratio))
        # self.divideLeoSplitter1(ratio)
        # self.divideLeoSplitter2(secondary_ratio)

    def setTitle(self, title):
        pass
        # if self.top:
            # # Fix https://bugs.launchpad.net/leo-editor/+bug/1194209
            # # When using tabs, leo_master (a LeoTabbedTopLevel) contains the QMainWindow.
            # w = self.top.leo_master if g.app.qt_use_tabs else self.top
            # w.setWindowTitle(title)

    def setTopGeometry(self, w, h, x, y, adjustSize=True):
        pass
        # self.top is a DynamicWindow.
        # if self.top:
            # self.top.setGeometry(QtCore.QRect(x, y, w, h))

    def update(self, *args, **keys):
        pass
        # self.top.update()
    #@+node:ekr.20170420170826.1: *3* CFrame.oops
    def oops(self):
        '''Ignore do-nothing methods.'''
        g.pr("CursesFrame oops:", g.callers(4), "should be overridden in subclass")
    #@-others
#@+node:ekr.20170419094731.1: ** class CursesGui (LeoGui)
class CursesGui(leoGui.LeoGui):
    '''
    Leo's curses gui wrapper.
    This is g.app.gui, when --gui=curses.
    '''

    def __init__(self):
        '''Ctor for the CursesGui class.'''
        leoGui.LeoGui.__init__(self, 'curses')
            # Init the base class.
        self.consoleOnly = False
            # Required attribute.
        self.log = None
            # The present log. Used by g.es
        self.log_inited = False
            # True: don't use the wait_list.
        self.wait_list = []
            # Queued log messages.
        self.init_logger()
            # Do this as early as possible.
            # It monkey-patches g.pr and g.trace.
        g.trace('CursesGui')
        self.key_handler = CursesKeyHandler()

    #@+others
    #@+node:ekr.20170419110052.1: *3* CGui.createLeoFrame
    def createLeoFrame(self, c, title):
        '''
        Create a LeoFrame for the current gui.
        Called from Leo's core (c.initObjects).
        '''
        return CursesFrame(c, title)
    #@+node:ekr.20170502021145.1: *3* CGui.dialogs (to do)
    def runAboutLeoDialog(self, c, version, theCopyright, url, email):
        """Create and run Leo's About Leo dialog."""
        g.trace('not ready yet')

    def runAskLeoIDDialog(self):
        """Create and run a dialog to get g.app.LeoID."""
        g.trace('not ready yet')

    def runAskOkDialog(self, c, title,
        message=None,
        text="Ok",
    ):
        """Create and run an askOK dialog ."""
        g.trace('not ready yet')

    def runAskOkCancelNumberDialog(self, c, title, message,
        cancelButtonText=None,
        okButtonText=None,
    ):
        """Create and run askOkCancelNumber dialog ."""
        g.trace('not ready yet')

    def runAskOkCancelStringDialog(self, c, title, message,
        cancelButtonText=None,
        okButtonText=None,
        default="",
        wide=False,
    ):
        """Create and run askOkCancelString dialog ."""
        g.trace('not ready yet')

    def runAskYesNoDialog(self, c, title,
        message=None,
        yes_all=False,
        no_all=False,
    ):
        """Create and run an askYesNo dialog."""
        g.trace('not ready yet')

    def runAskYesNoCancelDialog(self, c, title,
        message=None,
        yesMessage="Yes",
        noMessage="No",
        yesToAllMessage=None,
        defaultButton="Yes",
        cancelMessage=None,
    ):
        """Create and run an askYesNoCancel dialog ."""
        g.trace('not ready yet')

    def runPropertiesDialog(self,
        title='Properties',
        data=None,
        callback=None,
        buttons=None,
    ):
        """Dispay a modal TkPropertiesDialog"""
        g.trace('not ready yet')
    #@+node:ekr.20170502020354.1: *3* CGui.run
    def run(self):
        '''Create and run Leo's singleton npyscreen window.'''
        assert self == g.app.gui
        # Transfer queued log messages to the log pane.
        values = [s for s, color in self.wait_list]
        self.wait_list = []
        self.log_inited = True
        F = npyscreen.Form(name = "Welcome to Leo")
            # This call clears the screen.
        w = F.add(
            npyscreen.MultiLineEditableBoxed,
            max_height=20,
            name='Log Pane',
            footer="Press i or o to insert text", 
            values=values, 
            slow_scroll=False,
        )
        self.log.w = w
        # F.add_widget(npyscreen.TreeLineAnnotated, name='Outline')
        F.add_widget(npyscreen.TitleText, name="Minibuffer")
        # g.trace('CGui: g.app.windowList', g.app.windowList)
        # g.trace('CGui: before F.edit()')
        F.edit()
    #@+node:ekr.20170430114709.1: *3* CGui.do_key
    def do_key(self, ch_i):
        
        self.key_handler.do_key(ch_i)
    #@+node:ekr.20170419111744.1: *3* CGui.Focus...
    def get_focus(self, *args, **keys):
        return None
    #@+node:ekr.20170501032447.1: *3* CGui.init_logger
    def init_logger(self):

        self.rootLogger = logging.getLogger('')
        self.rootLogger.setLevel(logging.DEBUG)
        socketHandler = logging.handlers.SocketHandler(
            'localhost',
            logging.handlers.DEFAULT_TCP_LOGGING_PORT,
        )
        self.rootLogger.addHandler(socketHandler)
        logging.info('-' * 20)
        # Monkey-patch leoGlobals functions.
        g.es = es
        g.pr = pr # Most ouput goes through here, including g.es_exception.
        g.trace = trace
    #@+node:ekr.20170501165746.1: *3* CGui.oops
    def oops(self):
        '''Ignore do-nothing methods.'''
        g.pr("CursesGui oops:", g.callers(4), "should be overridden in subclass")
    #@+node:ekr.20170419140914.1: *3* CGui.runMainLoop
    def runMainLoop(self):
        '''The curses gui main loop.'''
        # Do NOT change g.app!
        CursesApp().run()
            # run calls CApp.main(), which calls CGui.run().
        g.trace('DONE')
    #@-others
#@+node:ekr.20170430114840.1: ** class CursesKeyHandler
class CursesKeyHandler:

    #@+others
    #@+node:ekr.20170430114930.1: *3* CKey.do_key & helpers
    def do_key(self, ch_i):
        '''
        Handle a key event by calling k.masterKeyHandler.
        Return True if the event was completely handled.
        '''
        #  This is a complete rewrite of the LeoQtEventFilter code.
        if self.is_key_event(ch_i):
            c = g.app.log and g.app.log.c
            assert c, g.callers()
            w = None ### c.frame.body.wrapper
            char, shortcut = self.to_key(ch_i)
            event = self.create_key_event(c, w, char, shortcut)
            g.trace(event.stroke)
            try:
                c.k.masterKeyHandler(event)
            except Exception:
                g.es_exception()
            return True
        else:
            return False
    #@+node:ekr.20170430115131.4: *4* CKey.char_to_tk_name
    tk_dict = {
        # Part 1: same as g.app.guiBindNamesDict
        "&": "ampersand",
        "^": "asciicircum",
        "~": "asciitilde",
        "*": "asterisk",
        "@": "at",
        "\\": "backslash",
        "|": "bar",
        "{": "braceleft",
        "}": "braceright",
        "[": "bracketleft",
        "]": "bracketright",
        ":": "colon",
        ",": "comma",
        "$": "dollar",
        "=": "equal",
        "!": "exclam",
        ">": "greater",
        "<": "less",
        "-": "minus",
        "#": "numbersign",
        '"': "quotedbl",
        "'": "quoteright",
        "(": "parenleft",
        ")": "parenright",
        "%": "percent",
        ".": "period",
        "+": "plus",
        "?": "question",
        "`": "quoteleft",
        ";": "semicolon",
        "/": "slash",
        " ": "space",
        "_": "underscore",
        # Curses.
        ### Qt
            # # Part 2: special Qt translations.
            # 'Backspace': 'BackSpace',
            # 'Backtab': 'Tab', # The shift mod will convert to 'Shift+Tab',
            # 'Esc': 'Escape',
            # 'Del': 'Delete',
            # 'Ins': 'Insert', # was 'Return',
            # # Comment these out to pass the key to the QTextWidget.
            # # Use these to enable Leo's page-up/down commands.
            # 'PgDown': 'Next',
            # 'PgUp': 'Prior',
            # # New entries.  These simplify code.
            # 'Down': 'Down', 'Left': 'Left', 'Right': 'Right', 'Up': 'Up',
            # 'End': 'End',
            # 'F1': 'F1', 'F2': 'F2', 'F3': 'F3', 'F4': 'F4', 'F5': 'F5',
            # 'F6': 'F6', 'F7': 'F7', 'F8': 'F8', 'F9': 'F9',
            # 'F10': 'F10', 'F11': 'F11', 'F12': 'F12',
            # 'Home': 'Home',
            # # 'Insert':'Insert',
            # 'Return': 'Return',
            # 'Tab': 'Tab',
            # # 'Tab':'\t', # A hack for QLineEdit.
            # # Unused: Break, Caps_Lock,Linefeed,Num_lock
    }

    def char_to_tk_name(self, ch):
        val = self.tk_dict.get(ch)
        return val
    #@+node:ekr.20170430115131.2: *4* CKey.create_key_event
    def create_key_event(self, c, w, ch, shortcut):
        trace = True
        # Last-minute adjustments...
        if shortcut == 'Return':
            ch = '\n' # Somehow Qt wants to return '\r'.
        elif shortcut == 'Escape':
            ch = 'Escape'
        # Switch the Shift modifier to handle the cap-lock key.
        if len(ch) == 1 and len(shortcut) == 1 and ch.isalpha() and shortcut.isalpha():
            if ch != shortcut:
                if trace: g.trace('caps-lock')
                shortcut = ch
        # Patch provided by resi147.
        # See the thread: special characters in MacOSX, like '@'.
        ### Alt keys apparently never generated.
            # if sys.platform.startswith('darwin'):
                # darwinmap = {
                    # 'Alt-Key-5': '[',
                    # 'Alt-Key-6': ']',
                    # 'Alt-Key-7': '|',
                    # 'Alt-slash': '\\',
                    # 'Alt-Key-8': '{',
                    # 'Alt-Key-9': '}',
                    # 'Alt-e': '€',
                    # 'Alt-l': '@',
                # }
                # if tkKey in darwinmap:
                    # shortcut = darwinmap[tkKey]
        if trace: g.trace('ch: %r, shortcut: %r' % (ch, shortcut))
        import leo.core.leoGui as leoGui
        return leoGui.LeoKeyEvent(
            c=c,
            char=ch,
            event={'c': c, 'w': w},
            shortcut=shortcut,
            w=w, x=0, y=0, x_root=0, y_root=0,
        )
    #@+node:ekr.20170430115030.1: *4* CKey.is_key_event
    def is_key_event(self, ch_i):
        # pylint: disable=no-member
        return ch_i not in (curses.KEY_MOUSE,)
    #@+node:ekr.20170430115131.3: *4* CKey.to_key
    def to_key(self, ch_i):
        '''Convert ch_i to a char and shortcut.'''
        trace = True
        a = curses.ascii
        if trace: g.trace(ch_i, a.iscntrl(ch_i))
        if a.iscntrl(ch_i):
            val = ch_i - 1 + ord('a')
            char = chr(val)
            shortcut = 'Ctrl+%s' % char
        else:
            char = a.ascii(ch_i)
            shortcut = self.char_to_tk_name(char)
        if trace: g.trace('ch_i: %s char: %r shortcut: %r' % (ch_i, char, shortcut))
        return char, shortcut

        
    #@-others
#@+node:ekr.20170419143731.1: ** class CursesLog
class CursesLog:
    '''A class that represents curses log pane.'''
    #@+others
    #@+node:ekr.20170419143731.4: *3* CLog.__init__
    def __init__(self, c):
        '''Ctor for CLog class.'''
        g.trace('CursesLog')
        self.c = c
        self.enabled = True
            # Required by Leo's core.
        self.isNull = False
            # Required by Leo's core.
        self.w = None
            # The npyscreen log widget. Queue all output until set.
            # Set in CApp.main.
        
        ### Old code:
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
    #@+node:ekr.20170419143731.2: *3* CLog.cmd (decorator)
    def cmd(name):
        '''Command decorator for the c.frame.log class.'''
        # pylint: disable=no-self-argument
        return g.new_cmd_decorator(name, ['c', 'frame', 'log'])
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
        c, w = self.c, self.w
        if not c or not c.exists:
            logging.info('CLog.put: no c: %r' % s)
            return
        if self.w:
            values = w.get_values()
            values.append(s)
            w.set_values(values)
            w.update()
        else:
            logging.info('CLog.put no w: %r' % s)
    #@+node:ekr.20170419143731.16: *4* CLog.putnl
    def putnl(self, tabName='Log'):
        '''Put a newline to the Qt log.'''
        # This is not called normally.
        # print('CLog.put: %s' % g.callers())
        if g.app.quitting:
            return
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
class CursesMenu (leoMenu.LeoMenu):

    def __init__ (self, c):
        
        dummy_frame = g.Bunch(c=c)
        leoMenu.LeoMenu.__init__(self, dummy_frame)
        self.c = c
        self.d = {}

    def oops(self):
        '''Ignore do-nothing methods.'''
        # g.pr("CursesMenu oops:", g.callers(4), "should be overridden in subclass")

        
#@+node:ekr.20170501024424.1: ** class CursesTree
#@+node:edward.20170428174322.1: ** class LeoKeyEvent
class LeoKeyEvent(object):
    '''A gui-independent wrapper for gui events.'''
    #@+others
    #@+node:edward.20170428174322.2: *3* LeoKeyEvent.__init__
    def __init__(self, c, char, event, shortcut, w,
        x=None,
        y=None,
        x_root=None,
        y_root=None,
    ):
        '''Ctor for LeoKeyEvent class.'''
        trace = True
        assert not g.isStroke(shortcut), g.callers()
        stroke = g.KeyStroke(shortcut) if shortcut else None
        if trace: g.trace('LeoKeyEvent: stroke', stroke)
        self.c = c
        self.char = char or ''
        self.event = event
        self.stroke = stroke
        self.w = self.widget = w
        # Optional ivars
        self.x = x
        self.y = y
        # Support for fastGotoNode plugin
        self.x_root = x_root
        self.y_root = y_root
    #@+node:edward.20170428174322.3: *3* LeoKeyEvent.__repr__
    def __repr__(self):
        return 'LeoKeyEvent: stroke: %s, char: %s, w: %s' % (
            repr(self.stroke), repr(self.char), repr(self.w))
    #@+node:edward.20170428174322.4: *3* LeoKeyEvent.get & __getitem__
    def get(self, attr):
        '''Compatibility with g.bunch: return an attr.'''
        return getattr(self, attr, None)

    def __getitem__(self, attr):
        '''Compatibility with g.bunch: return an attr.'''
        return getattr(self, attr, None)
    #@+node:edward.20170428174322.5: *3* LeoKeyEvent.type
    def type(self):
        return 'LeoKeyEvent'
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
