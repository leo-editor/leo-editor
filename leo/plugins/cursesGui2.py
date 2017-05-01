#@+leo-ver=5-thin
#@+node:ekr.20170419092835.1: * @file cursesGui2.py
'''A prototype text gui using the python curses library.'''
use_npyscreen = True
gApp = None
gC = None
#@+<< cursesGui imports >>
#@+node:ekr.20170419172102.1: **  << cursesGui imports >>
import leo.core.leoGlobals as g
import logging
import logging.handlers
import sys
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
# pylint: disable=arguments-differ
#@+others
#@+node:ekr.20170501032705.1: ** top-level
#@+node:ekr.20170419094705.1: *3*  init (cursesGui2.py)
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
#@+node:ekr.20170430112645.1: *3* es
def es(*args, **keys):
    '''Put all non-keyword args to the log pane.
    The first, third, fifth, etc. arg translated by g.translateString.
    Supports color, comma, newline, spaces and tabName keyword arguments.
    '''
    # Compute the effective args.
    d = {
        'color': None,
        'commas': False,
        'newline': True,
        'spaces': True,
        'tabName': 'Log',
    }
    d = g.doKeywordArgs(keys, d)
    s = g.translateArgs(args, d)
    if g.app.log and g.app.logInited:
        g.app.log.put(s)
    else:
        logging.info(s.rstrip())
#@+node:ekr.20170429165242.1: *3* trace
def trace(*args, **keys):
    '''Print a tracing message.'''
    # Don't use g here: in standalone mode g is a NullObject!
    # Compute the effective args.
    d = {'align': 0, 'before': '', 'newline': True, 'caller_level': 1, 'noname': False}
    d = g.doKeywordArgs(keys, d)
    # newline = d.get('newline')
    align = d.get('align', 0)
    caller_level = d.get('caller_level', 1)
    noname = d.get('noname')
    # Compute the caller name.
    if noname:
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
    # print ('g.trace:args...')
    # for z in args: print (g.isString(z),repr(z))
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
    s = d.get('before') + ''.join(result)
    # pr(s, newline=newline)
    logging.info(s.rstrip())
#@+node:ekr.20170420054211.1: ** class CursesApp (NPSApp)
class CursesApp(npyscreen.NPSApp):
    
    def __init__(self, c):
        global gC
        gC = c ### To be deleted.
        g.trace('CursesApp')
        self.leo_c = c
        self.leo_log = c.frame.log
        self.leo_minibuffer = None
        self.leo_tree = None
        npyscreen.NPSApp.__init__(self)
            # Init the base class.

    #@+others
    #@+node:ekr.20170420090426.1: *3* CApp.main
    def main(self):
        '''Create the main screen.'''
        g.trace('CursesApp.main')
        F  = npyscreen.Form(name = "Welcome to Leo",)
        # Transfer queued log messages to the log pane.
        waiting_list = self.leo_log.waiting_list[:]
        self.leo_log.waiting_list = []
        # Set the log widget.
        self.leo_log.w = F.add(
            npyscreen.MultiLineEditableBoxed,
            max_height=20,
            name='Log Pane',
            footer="Press i or o to insert text", 
            values=waiting_list, 
            slow_scroll=False,
        )
        # self.leo_tree = F.add_widget(npyscreen.TreeLineAnnotated, name='Outline')
        self.leo_minibuffer = F.add_widget(npyscreen.TitleText, name="Minibuffer")
        g.trace('before F.edit()')
        F.edit()
    #@-others

#@+node:ekr.20170501024433.1: ** class CursesBody
#@+node:ekr.20170419105852.1: ** class CursesFrame
class CursesFrame (leoFrame.LeoFrame):

    def __init__ (self, c, title):

        g.trace('CursesFrame')
        leoFrame.LeoFrame.__init__(self, c, gui=g.app.gui)
        self.c = c
        self.d = {}
        self.log = CursesLog(c)
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

#@+node:ekr.20170419094731.1: ** class CursesGui
class CursesGui(leoGui.LeoGui):
    '''Leo's curses gui wrapper.'''

    def __init__(self):
        '''Ctor for the CursesGui class.'''
        leoGui.LeoGui.__init__(self, 'curses')
         # Init the base class.
        self.consoleOnly = False # Required attribute.
        self.d = {}
            # Keys are names, values of lists of g.callers values.
        self.init_logger()
            # Do this as early as possible.
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
    #@+node:ekr.20170501032447.1: *3* CGUI.init_logger
    def init_logger(self):

        self.rootLogger = logging.getLogger('')
        self.rootLogger.setLevel(logging.DEBUG)
        socketHandler = logging.handlers.SocketHandler(
            'localhost',
            logging.handlers.DEFAULT_TCP_LOGGING_PORT,
        )
        self.rootLogger.addHandler(socketHandler)
        # Monkey-patch g.trace and g.es.
        # This allows us to see startup data and tracebacks.
        g.trace = trace
        g.es = es
    #@+node:ekr.20170419140914.1: *3* CGui.runMainLoop (sets gApp)
    def runMainLoop(self):
        '''The curses gui main loop.'''
        global gApp
        c = g.app.log.c
        assert c
        gApp = CursesApp(c)
        gApp.run()
            # Calls CursesGui.main()
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
            c = gC
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
        self.c = c
        self.enabled = True
            # Required by Leo's core.
        self.isNull = False
            # Required by Leo's core.
        self.w = None
            # The npyscreen log widget. Queue all output until set.
        self.waiting_list = []
            # The queued log text.
        
        ### from LeoQtLog
            # leoFrame.LeoLog.__init__(self, frame, parentFrame)
                # # Init the base class. Calls createControl.
            # assert self.logCtrl is None, self.logCtrl # Set in finishCreate.
                # # Important: depeding on the log *tab*,
                # # logCtrl may be either a wrapper or a widget.
            # self.c = frame.c # Also set in the base constructor, but we need it here.
        
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
        if g.app.quitting or not c or not c.exists:
            print('CLog.log.put fails', repr(s))
            return
        if self.w:
            values = w.get_values()
            values.append(s)
            w.set_values(values)
            w.update()
        else:
            self.waiting_list.append(s)
                ### To do: remember color
                
        ### Old code.
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
