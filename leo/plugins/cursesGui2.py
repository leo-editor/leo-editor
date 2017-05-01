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
gGui = None # Set in LeoApp.createCursesGui.
gLog = None # Set in CursesFrame.ctor
# pylint: disable=arguments-differ
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
    global gLog
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
    # s = ''.join(args)
    if isinstance(g.app.gui, CursesGui):
        if g.app.gui.log_inited:
            gLog.put(s, color=color)
        else:
            g.app.gui.wait_list.append((s, color),)
    elif 1:
        logging.info(' KILL: %r' % s)
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
    
    def __init__(self, c):
        g.trace('CursesApp')
        npyscreen.NPSApp.__init__(self)
            # Init the base class.
        self.leo_c = c
        self.leo_log = None ### was c.frame.log
        self.leo_log_waiting = []
        self.leo_minibuffer = None
        self.leo_tree = None
        assert not hasattr(self, 'gui')
        self.gui = None # Set in runMainLoop.

    #@+others
    #@+node:ekr.20170420090426.1: *3* CApp.main
    def main(self):
        '''Create the main screen.'''
        global gLog
        # Transfer queued log messages to the log pane.
        values = [s for s, color in g.app.gui.wait_list]
        g.app.gui.wait_list = []
        g.app.gui.log_inited = True
        # The next call clears the screen.
        F = npyscreen.Form(name = "Welcome to Leo")
        w = F.add(
            npyscreen.MultiLineEditableBoxed,
            max_height=20,
            name='Log Pane',
            footer="Press i or o to insert text", 
            values=values, 
            slow_scroll=False,
        )
        gLog.w = w
        # self.leo_tree = F.add_widget(npyscreen.TreeLineAnnotated, name='Outline')
        self.leo_minibuffer = F.add_widget(npyscreen.TitleText, name="Minibuffer")
        g.es('g.es test')
        g.trace('before F.edit()')
        F.edit()
    #@+node:ekr.20170501120748.1: *3* CApp.writeWaitingLog
    def writeWaitingLog(self, c):
        '''Write all waiting lines to the log.'''
        trace = True
        app = self
        if trace:
            # Do not call g.es, g.es_print, g.pr or g.trace here!
            logging.info('CApp.writeWaitingLog')
            for s, color in g.app.gui.wait_list:
                logging.info('wait2 %r' % s)
            return
        return ####
        if not c or not c.exists:
            return
        # if g.unitTesting:
            # app.printWaiting = []
            # app.logWaiting = []
            # g.app.setLog(None) # Prepare to requeue for other commanders.
            # return
        table = [
            ('Leo Log Window', 'red'),
            (app.signon, None),
            (app.signon1, None),
            (app.signon2, None)
        ]
        table.reverse()
        c.setLog()
        app.logInited = True # Prevent recursive call.
        if not app.signon_printed:
            app.signon_printed = True
            if not app.silentMode:
                print('')
                print('** isPython3: %s' % g.isPython3)
                if not g.enableDB:
                    print('** caching disabled')
                print(app.signon)
                if app.signon1:
                    print(app.signon1)
                print(app.signon2)
        if not app.silentMode:
            for s in app.printWaiting:
                print(s)
        app.printWaiting = []
        if not app.silentMode:
            for s, color in table:
                if s:
                    app.logWaiting.insert(0, (s + '\n', color),)
            for s, color in app.logWaiting:
                g.es('', s, color=color, newline=0)
                    # The caller must write the newlines.
            if hasattr(c.frame.log, 'scrollToEnd'):
                g.app.gui.runAtIdle(c.frame.log.scrollToEnd)
        app.logWaiting = []
        # Essential when opening multiple files...
        g.app.setLog(None)
    #@-others
#@+node:ekr.20170501024433.1: ** class CursesBody
#@+node:ekr.20170419105852.1: ** class CursesFrame
class CursesFrame (leoFrame.LeoFrame):

    def __init__ (self, c, title):

        global gLog
        g.trace('CursesFrame', c.shortFileName())
        leoFrame.LeoFrame.__init__(self, c, gui=g.app.gui)
        self.c = c
        self.d = {}
        self.log = gLog = CursesLog(c)
        self.title = title
        # Standard ivars.
        self.ratio = self.secondary_ratio = 0.0
        # Widgets
        self.body = None
        self.menu = CursesMenu(c)
        self.miniBufferWidget = None
        self.top = None
        self.tree = g.NullObject()

    #@+others
    #@+node:ekr.20170420170826.1: *3* CF.oops
    def oops(self):
        '''Ignore do-nothing methods.'''
        # g.pr("CursesFrame oops:", g.callers(4), "should be overridden in subclass")
    #@+node:ekr.20170420163932.1: *3* CF.finishCreate
    def finishCreate(self):
        g.trace('CursesFrame')
    #@+node:ekr.20170419111305.1: *3* CF.getShortCut
    def getShortCut(self, *args, **kwargs):
        return None
    #@-others

#@+node:ekr.20170419094731.1: ** class CursesGui (LeoGui)
class CursesGui(leoGui.LeoGui):
    '''Leo's curses gui wrapper.'''

    def __init__(self):
        '''Ctor for the CursesGui class.'''
        self.wait_list = []
        self.log_inited = False
        self.init_logger()
            # Do this as early as possible.
            # It monkey-patches g.pr and g.trace.
        g.trace('CursesGui')
        leoGui.LeoGui.__init__(self, 'curses')
         # Init the base class.
        self.app = None
            # set in self.runMainLoop.
        self.consoleOnly = False # Required attribute.
        self.d = {}
            # Keys are names, values of lists of g.callers values.
        self.key_handler = CursesKeyHandler()
            
    def oops(self):
        '''Ignore do-nothing methods.'''
        # g.pr("CursesFrame oops:", g.callers(4), "should be overridden in subclass")

    #@+others
    #@+node:ekr.20170419110052.1: *3* CGui.createLeoFrame
    def createLeoFrame(self, c, title):

        return CursesFrame(c, title)
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
    #@+node:ekr.20170419140914.1: *3* CGui.runMainLoop
    def runMainLoop(self):
        '''The curses gui main loop.'''
        global gGui # Set earlier in LeoApp.createCursesGui.
        assert gGui
        c = g.app.log.c
        assert c
        g.app = self.app = CursesApp(c)
        g.app.gui = gGui
        self.app.run()
            # Inits/clears the screen.
            # Calls CursesApp.main()
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
