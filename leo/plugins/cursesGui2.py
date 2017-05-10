# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20170419092835.1: * @file cursesGui2.py
#@@first
'''A prototype text gui using the python curses library.'''
#@+<< cursesGui imports >>
#@+node:ekr.20170419172102.1: **  << cursesGui imports >>
import leo.core.leoGlobals as g
import logging
import logging.handlers
import sys
import weakref
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

if npyscreen:
    import npyscreen.utilNotify as utilNotify
    assert utilNotify
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
    for line in g.splitLines(s):
        logging.info('   pr: %s' % (line.rstrip()))
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
    logging.info('trace: %s' % s.rstrip())
#@+node:ekr.20170508085942.1: ** class  LeoTreeLine (npyscreen.TreeLine)
class LeoTreeLine(npyscreen.TreeLine):
    '''A editable TreeLine class.'''

    def __init__(self, *args, **kwargs):

        super(LeoTreeLine, self).__init__(*args, **kwargs)
        self.set_handlers()

    #@+others
    #@+node:ekr.20170508130016.1: *3* LeoTreeLine.handlers
    #@+node:ekr.20170508130946.1: *4* LeoTreeLine.h_cursor_beginning
    def h_cursor_beginning(self, ch):

        self.cursor_line = 0
    #@+node:ekr.20170508131043.1: *4* LeoTreeLine.h_cursor_end
    def h_cursor_end(self, ch):
        
        # self.value is a LeoTreeData.
        self.cursor_line = max(0, len(self.value.content)-1)
    #@+node:ekr.20170508130328.1: *4* LeoTreeLine.h_cursor_left
    def h_cursor_left(self, input):
        
        self.cursor_position = max(0, self.cursor_position -1)
    #@+node:ekr.20170508130339.1: *4* LeoTreeLine.h_cursor_right
    def h_cursor_right(self, input):

        self.cursor_position += 1

    #@+node:ekr.20170508130349.1: *4* LeoTreeLine.h_delete_left
    def h_delete_left(self, input):

        # self.value is a LeoTreeData.
        n = self.cursor_position
        s = self.value.content
        if 0 <= n <= len(s):
            self.value.content = s[:n] + s[n+1:]
            self.cursor_position -= 1
    #@+node:ekr.20170508125632.1: *4* LeoTreeLine.h_insert
    def h_insert(self, i):

        # self.value is a LeoTreeData.
        n = self.cursor_position + 1
        s = self.value.content
        self.value.content = s[:n] + chr(i) + s[n:]
        self.cursor_position += 1
    #@+node:ekr.20170508130025.1: *4* LeoTreeLine.set_handlers
    def set_handlers(self):

        def test(ch):
            return 32 <= ch <= 127

        self.complex_handlers.append((test, self.h_insert),)

        self.handlers.update({
            curses.KEY_HOME:      self.h_cursor_beginning,  # 262
            curses.KEY_END:       self.h_cursor_end,        # 358.
            curses.KEY_LEFT:        self.h_cursor_left,
            curses.KEY_RIGHT:       self.h_cursor_right,
            # curses.KEY_UP:        self.h_line_up,
            # curses.KEY_DOWN:      self.h_line_down,
            # curses.KEY_DC:        self.h_delete_right,
            # curses.ascii.DEL:     self.h_delete_left,
            curses.ascii.BS:        self.h_delete_left,
            curses.KEY_BACKSPACE:   self.h_delete_left,
        })
    #@-others
#@+node:ekr.20170420054211.1: ** class CursesApp (npyscreen.NPSApp)
class CursesApp(npyscreen.NPSApp):
    '''
    The *anonymous* npyscreen application object, created from
    CGui.runMainLoop. This is *not* g.app.
    '''
    
    if 0: # Not needed
        def __init__(self):
            g.trace('CursesApp')
            npyscreen.NPSApp.__init__(self)
                # Init the base class.

    def main(self):
        '''
        Called automatically from the ctor.
        Create and start Leo's singleton npyscreen window.
        '''
        g.app.gui.run()
#@+node:ekr.20170501024433.1: ** class CursesBody (leoFrame.LeoBody)
class CursesBody (leoFrame.LeoBody):
    '''
    A class that represents curses body pane.
    This is c.frame.body.
    '''
    
    def __init__(self, c):
        
        leoFrame.LeoBody.__init__(self,
            frame = g.NullObject(),
            parentFrame = None,
        )
            # Init the base class.
        self.c = c
        self.widget = None
        self.wrapper = None # Set in createCursesBody.
#@+node:ekr.20170419105852.1: ** class CursesFrame (leoFrame.LeoFrame)
class CursesFrame (leoFrame.LeoFrame):
    '''The LeoFrame when --gui=curses is in effect.'''
    
    #@+others
    #@+node:ekr.20170501155347.1: *3* CFrame.birth
    def __init__ (self, c, title):
        
        # g.trace('CursesFrame', c.shortFileName())
        leoFrame.LeoFrame.instances += 1 # Increment the class var.
        leoFrame.LeoFrame.__init__(self, c, gui=g.app.gui)
            # Init the base class.
        assert c and self.c == c
        self.log = CursesLog(c)
        g.app.gui.log = self.log
        self.title = title
        # Standard ivars.
        self.ratio = self.secondary_ratio = 0.0
        # Widgets
        self.body = CursesBody(c)
        self.menu = CursesMenu(c)
        self.miniBufferWidget = None
        self.top = CursesTopFrame(c)
        assert self.tree is None, self.tree
        self.tree = CursesTree(c)
        # npyscreen widgets.
        self.body_widget = None
        self.log_widget = None
        self.minibuffer_widget = None
        self.tree_widget = None
        
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
    #@+node:ekr.20170420163932.1: *4* CFrame.finishCreate (Finish)
    def finishCreate(self):
        # g.trace('CursesFrame', self.c.shortFileName())
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
    #@+node:ekr.20170501161029.1: *3* CFrame.must be defined in subclasses
    def bringToFront(self):
        pass

    def deiconify(self):
        pass
            
    def destroySelf(self):
        pass

    def getFocus(self):
        pass ### To do
        # return g.app.gui.get_focus(self.c)

    def get_window_info(self):
        return 0, 0, 0, 0

    def iconify(self):
        pass

    def lift(self):
        pass
        
    def getShortCut(self, *args, **kwargs):
        return None

    def getTitle(self):
        return self.title
        
    def oops(self):
        '''Ignore do-nothing methods.'''
        g.pr("CursesFrame oops:", g.callers(4), "should be overridden in subclass")

    def resizePanesToRatio(self, ratio, secondary_ratio):
        '''Resize splitter1 and splitter2 using the given ratios.'''
        # self.divideLeoSplitter1(ratio)
        # self.divideLeoSplitter2(secondary_ratio)
        
    def setInitialWindowGeometry(self):
        pass

    def setTitle(self, title):
        self.title = g.toUnicode(title)

    def setTopGeometry(self, w, h, x, y, adjustSize=True):
        pass
        
    def setWrap(self, p):
        pass

    def update(self, *args, **keys):
        pass
    #@-others
#@+node:ekr.20170419094731.1: ** class CursesGui (leoGui.LeoGui)
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
        self.curses_app = None
            # The singleton CursesApp instance.
        self.curses_form = None
            # The top-level curses Form instance.
            # Form.editw is the widget with focus.
        self.log = None
            # The present log. Used by g.es
        self.log_inited = False
            # True: don't use the wait_list.
        self.wait_list = []
            # Queued log messages.
        self.init_logger()
            # Do this as early as possible.
            # It monkey-patches g.pr and g.trace.
        # g.trace('CursesGui')
        self.top_form = None
            # The top-level form. Set in createCursesTop.
        self.key_handler = CursesKeyHandler()

    #@+others
    #@+node:ekr.20170504112655.1: *3* CGui.clipboard (to do)
    #@+node:ekr.20170504112744.2: *4* CGui.replaceClipboardWith (to do)
    def replaceClipboardWith(self, s):
        '''Replace the clipboard with the string s.'''
        pass
        ###
            # cb = self.qtApp.clipboard()
            # if cb:
                # s = g.toUnicode(s)
                # QtWidgets.QApplication.processEvents()
                # # Fix #241: QMimeData object error
                # cb.setText(QString(s))
                # QtWidgets.QApplication.processEvents()
                # # g.trace(len(s), type(s), s[: 25])
            # else:
                # g.trace('no clipboard!')
    #@+node:ekr.20170504112744.3: *4* CGui.getTextFromClipboard
    def getTextFromClipboard(self):
        '''Get a unicode string from the clipboard.'''
        return ''
        ###
            # cb = self.qtApp.clipboard()
            # if cb:
                # QtWidgets.QApplication.processEvents()
                # s = cb.text()
                # # g.trace(len(s), type(s), s[: 25])
                # # Fix bug 147: Python 3 clipboard encoding
                # s = g.u(s)
                    # # Don't call g.toUnicode here!
                    # # s is a QString, which isn't exactly a unicode string!
                # return s
            # else:
                # g.trace('no clipboard!')
                # return ''
    #@+node:ekr.20170504112744.4: *4* CGui.setClipboardSelection
    def setClipboardSelection(self, s):
        '''Set the clipboard selection to s.'''
        ###
            # if s:
                # # This code generates a harmless, but annoying warning on PyQt5.
                # cb = self.qtApp.clipboard()
                # cb.setText(QString(s), mode=cb.Selection)
    #@+node:ekr.20170502083158.1: *3* CGui.createCursesTop & helpers
    def createCursesTop(self):
        '''Create the top-level curses Form.'''
        trace = False and not g.unitTesting
        # Assert the key relationships required by the startup code.
        assert self == g.app.gui
        c = g.app.log.c
        assert c == g.app.windowList[0].c
        assert isinstance(c.frame, CursesFrame), repr(c.frame)
        if trace:
            g.trace('commanders in g.app.windowList')
            g.printList([z.c.shortFileName() for z in g.app.windowList])
        # Create the top-level form.
        self.curses_form = form = LeoForm(name = "Welcome to Leo")
            # This call clears the screen.
        self.createCursesLog(c, form)
        self.createCursesTree(c, form)
        self.createCursesBody(c, form)
        self.createCursesMinibuffer(c, form)
        g.es(form)
        return form
    #@+node:ekr.20170502084106.1: *4* CGui.createCursesBody
    def createCursesBody(self, c, form):
        '''
        Create the curses body widget in the given curses Form.
        Populate it with c.p.b.
        '''
        w = form.add(
            npyscreen.MultiLineEditableBoxed,
            max_height=8, # Subtract 4 lines
            name='Body Pane',
            footer="Press i or o to insert text", 
            values=g.splitLines(c.p.b), 
            slow_scroll=False,
        )
        assert hasattr(c.frame, 'body_widget')
        c.frame.body_widget = w
        c.frame.body.wrapper = CursesTextWrapper(c, 'body', w)
    #@+node:ekr.20170502083613.1: *4* CGui.createCursesLog
    def createCursesLog(self, c, form):
        '''
        Create the curses log widget in the given curses Form.
        Populate the widget with the queued log messages.
        '''
        w = form.add(
            npyscreen.MultiLineEditableBoxed,
            max_height=8, # Subtract 4 lines
            name='Log Pane',
            footer="Press i or o to insert text", 
            values=[s for s, color in self.wait_list], 
            slow_scroll=False,
        )
        # Clear the wait list and disable it.
        self.wait_list = []
        self.log_inited = True
        # Add links.
        self.log.w = w
        assert hasattr(c.frame, 'log_widget')
        c.frame.log_widget = w
    #@+node:ekr.20170502084249.1: *4* CGui.createCursesMinibuffer
    def createCursesMinibuffer(self, c, form):
        '''Create the curses minibuffer widget in the given curses Form.'''
        
        class MiniBufferBox(npyscreen.BoxTitle):
            '''An npyscreen class representing Leo's minibuffer, with binding.''' 
            _contained_widget = LeoMiniBuffer
        
        w = form.add(MiniBufferBox, name='Mini-buffer', max_height=3)
        # Link and check.
        mini_buffer = w._my_widgets[0]
        assert isinstance(mini_buffer, LeoMiniBuffer), repr(mini_buffer)
        mini_buffer.leo_c = c
        assert hasattr(c.frame, 'minibuffer_widget')
        c.frame.minibuffer_widget = mini_buffer
    #@+node:ekr.20170502083754.1: *4* CGui.createCursesTree
    def createCursesTree(self, c, form):
        '''Create the curses tree widget in the given curses Form.'''

        class BoxTitleTree(npyscreen.BoxTitle):
            # pylint: disable=used-before-assignment
            _contained_widget = LeoMLTree

        hidden_root_node = LeoTreeData(content='<HIDDEN>', ignore_root=True)
        for i in range(4):
            node = hidden_root_node.new_child(content='node %s' % (i))
            for j in range(2):
                child = node.new_child(content='child %s.%s' % (i, j))
                assert child

        w = form.add(
            BoxTitleTree,
            max_height=8, # Subtract 4 lines
            name='Tree Pane',
            footer="Press i or o to insert a node; Press h to edit headline",
            values=hidden_root_node, 
            slow_scroll=False,
        )
        # Link and check.
        assert isinstance(w, BoxTitleTree), w
        leo_tree = w._my_widgets[0]
        assert isinstance(leo_tree, LeoMLTree), repr(leo_tree)
        leo_tree.leo_c = c
        assert getattr(leo_tree, 'hidden_root_node') is None, leo_tree
        leo_tree.hidden_root_node = hidden_root_node
        assert hasattr(c.frame, 'tree_widget')
        c.frame.tree_widget = leo_tree # Bug fix: 2017/05/07
    #@+node:ekr.20170419110052.1: *3* CGui.createLeoFrame
    def createLeoFrame(self, c, title):
        '''
        Create a LeoFrame for the current gui.
        Called from Leo's core (c.initObjects).
        '''
        return CursesFrame(c, title)
    #@+node:ekr.20170502103338.1: *3* CGui.destroySelf
    def destroySelf(self):
        '''
        Terminate the curses gui application.
        Leo's core calls this only if the user agrees to terminate the app.
        '''
        sys.exit(0)
    #@+node:ekr.20170502021145.1: *3* CGui.dialogs (to do)
    def dialog_message(self, message):
        if not g.unitTesting:
            for s in g.splitLines(message):
                g.pr(s.rstrip())

    def runAboutLeoDialog(self, c, version, theCopyright, url, email):
        """Create and run Leo's About Leo dialog."""
        if not g.unitTesting:
            g.trace(version)

    def runAskLeoIDDialog(self):
        """Create and run a dialog to get g.app.LeoID."""
        if not g.unitTesting:
            g.trace('not ready yet')

    def runAskOkDialog(self, c, title,
        message=None,
        text="Ok",
    ):
        """Create and run an askOK dialog ."""
        # Potentially dangerous dialog.
        # self.dialog_message(message)
        if g.unitTesting:
            return False
        elif self.curses_app:
            val = utilNotify.notify_confirm(message=message,title=title)
            g.trace(repr(val))
            return val
        else:
            return False

    def runAskOkCancelNumberDialog(self, c, title, message,
        cancelButtonText=None,
        okButtonText=None,
    ):
        """Create and run askOkCancelNumber dialog ."""
        if g.unitTesting:
            return False
        elif self.curses_app:
            g.trace()
            self.dialog_message(message)
            val = utilNotify.notify_ok_cancel(message=message,title=title)
            g.trace(val)
            return val
        else:
            return False

    def runAskOkCancelStringDialog(self, c, title, message,
        cancelButtonText=None,
        okButtonText=None,
        default="",
        wide=False,
    ):
        """Create and run askOkCancelString dialog ."""
        if g.unitTesting:
            return False
        else:
            g.trace()
            self.dialog_message(message)
            val = utilNotify.notify_ok_cancel(message=message,title=title)
            g.trace(val)
            return val

    def runAskYesNoDialog(self, c, title,
        message=None,
        yes_all=False,
        no_all=False,
    ):
        """Create and run an askYesNo dialog."""
        if g.unitTesting:
            return False
        else:
            val = utilNotify.notify_ok_cancel(message=message,title=title)
            return 'yes' if val else 'no'

    def runAskYesNoCancelDialog(self, c, title,
        message=None,
        yesMessage="Yes",
        noMessage="No",
        yesToAllMessage=None,
        defaultButton="Yes",
        cancelMessage=None,
    ):
        """Create and run an askYesNoCancel dialog ."""
        if g.unitTesting:
            return False
        else:
            self.dialog_message(message)
        
    def runOpenFileDialog(self, c, title, filetypes, defaultextension, multiple=False, startpath=None):
        if not g.unitTesting:
            g.trace(title)

    def runPropertiesDialog(self,
        title='Properties',
        data=None,
        callback=None,
        buttons=None,
    ):
        """Dispay a modal TkPropertiesDialog"""
        if not g.unitTesting:
            g.trace(title)
        
    def runSaveFileDialog(self, c, initialfile, title, filetypes, defaultextension):
        if not g.unitTesting:
            g.trace(title)
    #@+node:ekr.20170430114709.1: *3* CGui.do_key
    def do_key(self, ch_i):
        
        return self.key_handler.do_key(ch_i)
    #@+node:ekr.20170502101347.1: *3* CGui.get/set_focus (to do)
    def get_focus(self, *args, **keys):
        
        # Careful during startup.
        return getattr(g.app.gui.curses_form, 'editw', None)

    def set_focus(self, *args, **keys):
        pass
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
    #@+node:ekr.20170504052119.1: *3* CGui.isTextWrapper
    def isTextWrapper(self, w):
        '''Return True if w is a Text widget suitable for text-oriented commands.'''
        return w and getattr(w, 'supportsHighLevelInterface', None)
    #@+node:ekr.20170504052042.1: *3* CGui.oops
    def oops(self):
        '''Ignore do-nothing methods.'''
        g.pr("CursesGui oops:", g.callers(4), "should be overridden in subclass")
    #@+node:ekr.20170502020354.1: *3* CGui.run
    def run(self):
        '''
        Create and run the top-level curses form.
        
        '''
        self.top_form = self.createCursesTop()
        self.top_form.edit()
    #@+node:ekr.20170419140914.1: *3* CGui.runMainLoop
    def runMainLoop(self):
        '''The curses gui main loop.'''
        # Do NOT change g.app!
        self.curses_app = CursesApp()
        self.curses_app.run()
            # run calls CApp.main(), which calls CGui.run().
        g.trace('DONE')
        # pylint: disable=no-member
        # endwin *does* exist.
        curses.endwin()
    #@+node:ekr.20170510074755.1: *3* CGui.test
    def test(self):
        '''A place to put preliminary tests.'''
    #@-others
#@+node:ekr.20170430114840.1: ** class CursesKeyHandler (object)
class CursesKeyHandler (object):

    #@+others
    #@+node:ekr.20170430114930.1: *3* CKey.do_key & helpers
    def do_key(self, ch_i):
        '''
        Handle a key event by calling k.masterKeyHandler.
        Return True if the event was completely handled.
        '''
        #  This is a rewrite of LeoQtEventFilter code.
        c = g.app.log and g.app.log.c
        if not c:
            return True # We are shutting down.
        elif self.is_key_event(ch_i):
            char, shortcut = self.to_key(ch_i)
            if shortcut:
                try:
                    w = c.frame.body.wrapper
                    event = self.create_key_event(c, w, char, shortcut)
                    c.k.masterKeyHandler(event)
                except Exception:
                    g.es_exception()
            return bool(shortcut)
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
        return self.tk_dict.get(ch, ch)
    #@+node:ekr.20170430115131.2: *4* CKey.create_key_event
    def create_key_event(self, c, w, ch, shortcut):
        trace = False
        # Last-minute adjustments...
        if shortcut == 'Return':
            ch = '\n' # Somehow Qt wants to return '\r'.
        elif shortcut == 'Escape':
            ch = 'Escape'
        # Switch the Shift modifier to handle the cap-lock key.
        if isinstance(ch, int):
            g.trace('can not happen: ch: %r shortcut: %r' % (ch, shortcut))
        elif (
            ch and len(ch) == 1 and
            shortcut and len(shortcut) == 1 and
            ch.isalpha() and shortcut.isalpha()
        ):
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
    def to_key(self, i):
        '''Convert int i to a char and shortcut.'''
        trace = False
        a = curses.ascii
        char, shortcut = '', ''
        s = a.unctrl(i)
        if i <= 32:
            d = {
                8:'Backspace',  9:'Tab',
                10:'Return',    13:'Linefeed',
                27:'Escape',    32: ' ',
            }
            shortcut = d.get(i, '')
            # All real ctrl keys lie between 1 and 26.
            if shortcut and shortcut != 'Escape':
                char = chr(i)
            elif len(s) >= 2 and s.startswith('^'):
                shortcut = 'Ctrl+' + self.char_to_tk_name(s[1:].lower())
        elif i == 127:
            pass
        elif i < 128:
            char = shortcut = chr(i)
            if char.isupper():
                shortcut = 'Shift+' + char
            else:
                shortcut = self.char_to_tk_name(char)
        elif 265 <= i <= 276:
            # Special case for F-keys
            shortcut = 'F%s' % (i-265+1)
        elif i == 351:
            shortcut = 'Shift+Tab'
        elif s.startswith('\\x'):
            pass
        elif len(s) >= 3 and s.startswith('!^'):
            shortcut = 'Alt+' + self.char_to_tk_name(s[2:])
        else:
            pass
        if trace: g.trace('i: %s s: %s char: %r shortcut: %r' % (i, s, char, shortcut))
        return char, shortcut
    #@-others
#@+node:ekr.20170419143731.1: ** class CursesLog (leoFrame.LeoLog)
class CursesLog (leoFrame.LeoLog):
    '''
    A class that represents curses log pane.
    This is c.frame.log.
    '''
    
    #@+others
    #@+node:ekr.20170419143731.4: *3* CLog.__init__
    def __init__(self, c):
        '''Ctor for CLog class.'''
        # g.trace('CursesLog')
        leoFrame.LeoLog.__init__(self,
            frame = g.NullObject(),
            parentFrame = None,
        )
            # Init the base class.
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
    #@+node:ekr.20170419143731.2: *3*  CLog.cmd (decorator)
    def cmd(name):
        '''Command decorator for the c.frame.log class.'''
        # pylint: disable=no-self-argument
        return g.new_cmd_decorator(name, ['c', 'frame', 'log'])
    #@+node:ekr.20170419143731.7: *3* CLog.clearLog
    @cmd('clear-log')
    def clearLog(self, event=None):
        '''Clear the log pane.'''
        # w = self.logCtrl.widget # w is a QTextBrowser
        # if w:
            # w.clear()
    #@+node:ekr.20170420035717.1: *3* CLog.enable/disable
    def disable(self):
        self.enabled = False

    def enable(self, enabled=True):
        self.enabled = enabled
    #@+node:ekr.20170420041119.1: *3* CLog.finishCreate
    def finishCreate(self):
        '''CursesLog.finishCreate.'''
        pass
    #@+node:ekr.20170419143731.15: *3* CLog.put
    def put(self, s, color=None, tabName='Log', from_redirect=False):
        '''All output to the log stream eventually comes here.'''
        c, w = self.c, self.w
        if not c or not c.exists:
            # logging.info('CLog.put: no c: %r' % s)
            pass
        elif self.w:
            values = w.get_values()
            values.append(s)
            w.set_values(values)
            w.update()
        else:
            pass
            # logging.info('CLog.put no w: %r' % s)
    #@+node:ekr.20170419143731.16: *3* CLog.putnl
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
#@+node:ekr.20170419111515.1: ** class CursesMenu (leoMenu.LeoMenu)
class CursesMenu (leoMenu.LeoMenu):

    def __init__ (self, c):
        
        dummy_frame = g.Bunch(c=c)
        leoMenu.LeoMenu.__init__(self, dummy_frame)
        self.c = c
        self.d = {}

    def oops(self):
        '''Ignore do-nothing methods.'''
        # g.pr("CursesMenu oops:", g.callers(4), "should be overridden in subclass")

        
#@+node:ekr.20170504034655.1: ** class CursesTextWrapper (object)
class CursesTextWrapper(object):
    '''
    A Wrapper class for Curses edit widgets classes.
    This is c.frame.body.wrapper or c.frame.log.wrapper.
    '''
    #@+others
    #@+node:ekr.20170504034655.2: *3* cw.ctor & helper
    def __init__(self, c, name, w):
        '''Ctor for QTextMixin class'''
        self.c = c
        self.changingText = False # A lockout for onTextChanged.
        self.enabled = True
        self.name = name
        self.supportsHighLevelInterface = True
            # A flag for k.masterKeyHandler and isTextWrapper.
        self.w = self.widget = w
        self.injectIvars(c)
            # These are used by Leo's core.
    #@+node:ekr.20170504034655.3: *4* cw.injectIvars
    def injectIvars(self, name='1', parentFrame=None):
        '''Inject standard leo ivars into the QTextEdit or QsciScintilla widget.'''
        p = self.c.currentPosition()
        if name == '1':
            self.leo_p = None # Will be set when the second editor is created.
        else:
            self.leo_p = p and p.copy()
        self.leo_active = True
        # New in Leo 4.4.4 final: inject the scrollbar items into the text widget.
        self.leo_bodyBar = None
        self.leo_bodyXBar = None
        self.leo_chapter = None
        self.leo_frame = None
        self.leo_name = name
        self.leo_label = None
    #@+node:ekr.20170504034655.5: *3* cw.Event handlers (To do)
    # These are independent of the kind of Qt widget.
    #@+node:ekr.20170504034655.6: *4* cw.onCursorPositionChanged
    def onCursorPositionChanged(self, event=None):
        c = self.c
        name = c.widget_name(self)
        # Apparently, this does not cause problems
        # because it generates no events in the body pane.
        if name.startswith('body'):
            if hasattr(c.frame, 'statusLine'):
                c.frame.statusLine.update()
    #@+node:ekr.20170504034655.7: *4* cw.onTextChanged
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
        c.recolor()
        if g.app.qt_use_tabs:
            if trace: g.trace(c.frame.top)
        if not c.changed and c.frame.initComplete:
            c.setChanged(True)
        c.frame.body.updateEditors()
        c.frame.tree.updateIcon(p)
    #@+node:ekr.20170504034655.8: *3* cw.High-level interface
    #@+node:ekr.20170504035808.1: *4* curses-specific (To do)
    #@+node:ekr.20170504040309.2: *5* cw.delete (uses getAllText)
    def delete(self, i, j=None):
        
        # Generic
        i = self.toPythonIndex(i)
        if j is None: j = i + 1
        j = self.toPythonIndex(j)
        # This allows subclasses to use this base class method.
        if i > j: i, j = j, i
        s = self.getAllText()
        self.setAllText(s[: i] + s[j:])
        self.setSelectionRange(i, i, insert=i)
        ###
            # Avoid calls to setAllText
            # w = self.widget
            # if trace: g.trace(self.getSelectionRange())
            # i = self.toPythonIndex(i)
            # if j is None: j = i + 1
            # j = self.toPythonIndex(j)
            # if i > j: i, j = j, i
            # if trace: g.trace(i, j)
            # sb = w.verticalScrollBar()
            # pos = sb.sliderPosition()
            # cursor = w.textCursor()
            # try:
                # self.changingText = True # Disable onTextChanged
                # old_i, old_j = self.getSelectionRange()
                # if i == old_i and j == old_j:
                    # # Work around an apparent bug in cursor.movePosition.
                    # cursor.removeSelectedText()
                # elif i == j:
                    # pass
                # else:
                    # # g.trace('*** using dubious code')
                    # cursor.setPosition(i)
                    # moveCount = abs(j - i)
                    # cursor.movePosition(cursor.Right, cursor.KeepAnchor, moveCount)
                    # w.setTextCursor(cursor) # Bug fix: 2010/01/27
                    # if trace:
                        # i, j = self.getSelectionRange()
                        # g.trace(i, j)
                    # cursor.removeSelectedText()
                    # if trace: g.trace(self.getSelectionRange())
            # finally:
                # self.changingText = False
            # sb.setSliderPosition(pos)
    #@+node:ekr.20170504040309.3: *5* cw.flashCharacter (To do)
    def flashCharacter(self, i,
        bg='white',
        fg='red',
        flashes=3,
        delay=75,
    ):
        pass
        ###
            # # numbered color names don't work in Ubuntu 8.10, so...
            # if bg[-1].isdigit() and bg[0] != '#':
                # bg = bg[: -1]
            # if fg[-1].isdigit() and fg[0] != '#':
                # fg = fg[: -1]
            # # This might causes problems during unit tests.
            # # The selection point isn't restored in time.
            
            # if g.app.unitTesting:
                # return
            # w = self.widget # A QTextEdit.
            # e = QtGui.QTextCursor
        
            # def after(func):
                # QtCore.QTimer.singleShot(delay, func)
        
            # def addFlashCallback(self=self, w=w):
                # i = self.flashIndex
                # cursor = w.textCursor() # Must be the widget's cursor.
                # cursor.setPosition(i)
                # cursor.movePosition(e.Right, e.KeepAnchor, 1)
                # extra = w.ExtraSelection()
                # extra.cursor = cursor
                # if self.flashBg: extra.format.setBackground(QtGui.QColor(self.flashBg))
                # if self.flashFg: extra.format.setForeground(QtGui.QColor(self.flashFg))
                # self.extraSelList = [extra] # keep the reference.
                # w.setExtraSelections(self.extraSelList)
                # self.flashCount -= 1
                # after(removeFlashCallback)
        
            # def removeFlashCallback(self=self, w=w):
                # w.setExtraSelections([])
                # if self.flashCount > 0:
                    # after(addFlashCallback)
                # else:
                    # w.setFocus()
        
            # self.flashCount = flashes
            # self.flashIndex = i
            # self.flashBg = None if bg.lower() == 'same' else bg
            # self.flashFg = None if fg.lower() == 'same' else fg
            # addFlashCallback()
    #@+node:ekr.20170504035640.1: *5* cw.getAllText (To do)
    def getAllText(self):

        return ''
        ###
            # w = self.widget
            # s = g.u(w.toPlainText())
            # return s
    #@+node:ekr.20170504040026.1: *5* cw.getInsertPoint (To do)
    def getInsertPoint(self):
        
        return 0
        ###
            # return self.widget.textCursor().position()
    #@+node:ekr.20170504040221.1: *5* cw.getSelectionRange (To do)
    def getSelectionRange(self, sort=True):
        
        return 0, 0
        ###
            # w = self.widget
            # tc = w.textCursor()
            # i, j = tc.selectionStart(), tc.selectionEnd()
            # return i, j
    #@+node:ekr.20170504040309.7: *5* cw.getX/YScrollPosition (To do)
    def getXScrollPosition(self):

        return 0
        ###
            # w = self.widget
            # sb = w.horizontalScrollBar()
            # return sb.sliderPosition()


    def getYScrollPosition(self):

        return 0
        ###
            # w = self.widget
            # sb = w.verticalScrollBar()
            # return sb.sliderPosition()
        
    #@+node:ekr.20170504040309.8: *5* cw.hasSelection (To do)
    def hasSelection(self):
        
        return False
        ###
            # return self.widget.textCursor().hasSelection()
    #@+node:ekr.20170504040309.9: *5* cw.insert (uses setAllText)
    def insert(self, i, s):
        
        s2 = self.getAllText()
        i = self.toPythonIndex(i)
        self.setAllText(s2[: i] + s + s2[i:])
        self.setInsertPoint(i + len(s))
        return i
        ### Avoid call to getAllText
            # w = self.widget
            # i = self.toPythonIndex(i)
            # cursor = w.textCursor()
            # try:
                # self.changingText = True # Disable onTextChanged.
                # cursor.setPosition(i)
                # cursor.insertText(s)
                # w.setTextCursor(cursor) # Bug fix: 2010/01/27
            # finally:
                # self.changingText = False
    #@+node:ekr.20170504040309.14: *5* cw.see & seeInsertPoint (to do)
    def see(self, i):
        '''Make sure position i is visible.'''
        pass
        ###
            # trace = False and not g.unitTesting
            # w = self.widget
            # if trace:
                # cursor = w.textCursor()
                # g.trace('i', i, 'pos', cursor.position())
                    # # 'getInsertPoint',self.getInsertPoint())
            # w.ensureCursorVisible()

    def seeInsertPoint(self):
        '''Make sure the insert point is visible.'''
        pass
        ###
            # trace = False and not g.unitTesting
            # if trace: g.trace(self.getInsertPoint())
            # self.widget.ensureCursorVisible()
    #@+node:ekr.20170504034655.21: *5* cw.selectAllText (to do)
    def selectAllText(self, s=None):
        
        pass
        ###
            # self.setSelectionRange(0, self.getLength(s))
    #@+node:ekr.20170504040309.15: *5* cw.setAllText (to do)
    def setAllText(self, s):
        '''Set the text of body pane.'''
        pass
        ###
        # trace = False and not g.unitTesting
        # trace_time = True
        # c, w = self.c, self.widget
        # h = c.p.h if c.p else '<no p>'
        # if trace and not trace_time: g.trace(len(s), h)
        # try:
            # if trace and trace_time:
                # t1 = time.time()
            # self.changingText = True # Disable onTextChanged.
            # w.setReadOnly(False)
            # w.setPlainText(s)
            # if trace and trace_time:
                # delta_t = time.time() - t1
                # g.trace('%4.2f sec. %6s chars %s' % (delta_t, len(s), h))
        # finally:
            # self.changingText = False
    #@+node:ekr.20170504034655.11: *5* cw.setFocus (to do)
    def setFocus(self):
        
        pass
        ###
            # # Call the base class
            # assert isinstance(self.widget, (
                # QtWidgets.QTextBrowser,
                # QtWidgets.QLineEdit,
                # QtWidgets.QTextEdit,
                # Qsci and Qsci.QsciScintilla,
            # )), self.widget
            # QtWidgets.QTextBrowser.setFocus(self.widget)
    #@+node:ekr.20170504040309.17: *5* cw.setSelectionRange (to do)
    def setSelectionRange(self, i, j, insert=None, s=None):
        '''Set the selection range and the insert point.'''
        pass
        ###
            # trace = False and not g.unitTesting
            # traceTime = False and not g.unitTesting
            # # Part 1
            # if traceTime: t1 = time.time()
            # w = self.widget
            # i = self.toPythonIndex(i)
            # j = self.toPythonIndex(j)
            # if s is None:
                # s = self.getAllText()
            # n = len(s)
            # i = max(0, min(i, n))
            # j = max(0, min(j, n))
            # if insert is None:
                # ins = max(i, j)
            # else:
                # ins = self.toPythonIndex(insert)
                # ins = max(0, min(ins, n))
            # if traceTime:
                # delta_t = time.time() - t1
                # if delta_t > 0.1: g.trace('part1: %2.3f sec' % (delta_t))
            # # Part 2:
            # if traceTime: t2 = time.time()
            # # 2010/02/02: Use only tc.setPosition here.
            # # Using tc.movePosition doesn't work.
            # tc = w.textCursor()
            # if i == j:
                # tc.setPosition(i)
            # elif ins == j:
                # # Put the insert point at j
                # tc.setPosition(i)
                # tc.setPosition(j, tc.KeepAnchor)
            # elif ins == i:
                # # Put the insert point at i
                # tc.setPosition(j)
                # tc.setPosition(i, tc.KeepAnchor)
            # else:
                # # 2014/08/21: It doesn't seem possible to put the insert point somewhere else!
                # tc.setPosition(j)
                # tc.setPosition(i, tc.KeepAnchor)
            # w.setTextCursor(tc)
            # # Fix bug 218: https://github.com/leo-editor/leo-editor/issues/218
            # if hasattr(g.app.gui, 'setClipboardSelection'):
                # g.app.gui.setClipboardSelection(s[i:j])
            # # Remember the values for v.restoreCursorAndScroll.
            # v = self.c.p.v # Always accurate.
            # v.insertSpot = ins
            # if i > j: i, j = j, i
            # assert(i <= j)
            # v.selectionStart = i
            # v.selectionLength = j - i
            # v.scrollBarSpot = spot = w.verticalScrollBar().value()
            # if trace: g.trace('i: %s j: %s ins: %s spot: %s %s' % (i, j, ins, spot, v.h))
            # if traceTime:
                # delta_t = time.time() - t2
                # tot_t = time.time() - t1
                # if delta_t > 0.1: g.trace('part2: %2.3f sec' % (delta_t))
                # if tot_t > 0.1: g.trace('total: %2.3f sec' % (tot_t))

    setSelectionRangeHelper = setSelectionRange
    #@+node:ekr.20170504040309.18: *5* cw.setXScrollPosition (to do)
    def setXScrollPosition(self, pos):
        '''Set the position of the horizonatl scrollbar.'''
        pass
        ###
            # if pos is not None:
                # w = self.widget
                # sb = w.horizontalScrollBar()
                # sb.setSliderPosition(pos)
    #@+node:ekr.20170504040309.19: *5* cw.setYScrollPosition (to do)
    def setYScrollPosition(self, pos):
        '''Set the vertical scrollbar position.'''
        pass
        ###
            # if pos is not None:
                # w = self.widget
                # sb = w.verticalScrollBar()
                # sb.setSliderPosition(pos)
    #@+node:ekr.20170504035742.1: *4* generic (no changes)
    # These call only wrapper methods.
    #@+node:ekr.20170504034655.13: *5* cw.appendText
    def appendText(self, s):

        s2 = self.getAllText()
        self.setAllText(s2 + s)
        self.setInsertPoint(len(s2))
    #@+node:ekr.20170504034655.10: *5* cw.clipboard_append & clipboard_clear
    def clipboard_append(self, s):
        s1 = g.app.gui.getTextFromClipboard()
        g.app.gui.replaceClipboardWith(s1 + s)

    def clipboard_clear(self):
        g.app.gui.replaceClipboardWith('')
    #@+node:ekr.20170504034655.15: *5* cw.deleteTextSelection
    def deleteTextSelection(self):

        i, j = self.getSelectionRange()
        self.delete(i, j)
    #@+node:ekr.20170504034655.9: *5* cw.enable/disable
    def disable(self):
        self.enabled = False

    def enable(self, enabled=True):
        self.enabled = enabled
    #@+node:ekr.20170504034655.16: *5* cw.get
    def get(self, i, j=None):

        # 2012/04/12: fix the following two bugs by using the vanilla code:
        # https://bugs.launchpad.net/leo-editor/+bug/979142
        # https://bugs.launchpad.net/leo-editor/+bug/971166
        s = self.getAllText()
        i = self.toPythonIndex(i)
        j = self.toPythonIndex(j)
        return s[i: j]
    #@+node:ekr.20170504034655.17: *5* cw.getLastPosition & getLength
    def getLastPosition(self, s=None):

        return len(self.getAllText()) if s is None else len(s)

    def getLength(self, s=None):

        return len(self.getAllText()) if s is None else len(s)
    #@+node:ekr.20170504034655.4: *5* cw.getName
    def getName(self):
        return self.name # Essential.
    #@+node:ekr.20170504034655.18: *5* cw.getSelectedText
    def getSelectedText(self):

        i, j = self.getSelectionRange()
        if i == j:
            return ''
        else:
            s = self.getAllText()
            return s[i: j]
    #@+node:ekr.20170504034655.24: *5* cw.rememberSelectionAndScroll
    def rememberSelectionAndScroll(self):
        
        w = self
        v = self.c.p.v # Always accurate.
        v.insertSpot = w.getInsertPoint()
        i, j = w.getSelectionRange()
        if i > j: i, j = j, i
        assert(i <= j)
        v.selectionStart = i
        v.selectionLength = j - i
        v.scrollBarSpot = w.getYScrollPosition()
    #@+node:ekr.20170504040309.16: *5* cw.setInsertPoint
    def setInsertPoint(self, i, s=None):

        # Fix bug 981849: incorrect body content shown.
        # Use the more careful code in setSelectionRange.
        self.setSelectionRange(i=i, j=i, insert=i, s=s)
    #@+node:ekr.20170504034655.22: *5* cw.toPythonIndex
    def toPythonIndex(self, index, s=None):

        if s is None:
            s = self.getAllText()
        i = g.toPythonIndex(s, index)
        return i
    #@+node:ekr.20170504034655.23: *5* cw.toPythonIndexRowCol
    def toPythonIndexRowCol(self, index):

        s = self.getAllText()
        i = self.toPythonIndex(index)
        row, col = g.convertPythonIndexToRowCol(s, i)
        return i, row, col
    #@-others
#@+node:ekr.20170502093200.1: ** class CursesTopFrame (object)
class CursesTopFrame (object):
    '''A representation of c.frame.top.'''
    
    def __init__(self, c):
        self.c = c
        
    def select(self, *args, **kwargs):
        pass # g.trace(args, kwargs)
        
    def findChild(self, *args, **kwargs):
        return g.NullObject()

    def finishCreateLogPane(self, *args, **kwargs):
        pass # g.trace(args, kwargs)
#@+node:ekr.20170501024424.1: ** class CursesTree (leoFrame.LeoTree)
class CursesTree (leoFrame.LeoTree):
    '''A class that represents curses tree pane.'''
    
    class DummyFrame:
        def __init__(self, c):
            self.c = c
    
    def __init__(self, c):

        dummy_frame = self.DummyFrame(c)
        leoFrame.LeoTree.__init__(self, dummy_frame)
            # Init the base class.
        assert self.c
        
    #@+others
    #@+node:ekr.20170502094839.1: *3* CTree.must be defined in sublasses
    def drawIcon(self, p):
        pass
        
    def editLabel(self, p, selectAll=False, selection=None):
        pass

    def edit_widget(self, p):
        return None

    def redraw(self, p=None, scroll=True, forceDraw=False):
        pass

    def redraw_now(self, p=None, scroll=True, forceDraw=False):
        pass

    def scrollTo(self, p):
        pass

    def setHeadline(self, p, s):
        pass
    #@-others
#@+node:ekr.20170507194035.1: ** class LeoForm (npyscreen.Form)
class LeoForm (npyscreen.Form):
    
    OK_BUTTON_TEXT = 'Quit Leo'
#@+node:edward.20170428174322.1: ** class LeoKeyEvent (object)
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
#@+node:ekr.20170510092721.1: ** class LeoMiniBuffer (npyscreen.Textfield)
class LeoMiniBuffer(npyscreen.Textfield):
    '''An npyscreen class representing Leo's minibuffer, with binding.''' 
    
    def __init__(self, *args, **kwargs):
        super(LeoMiniBuffer, self).__init__(*args, **kwargs)
        self.leo_c = None # Set later
        self.set_handlers()

    #@+others
    #@+node:ekr.20170510095136.2: *3* LeoMiniBuffer.h_cursor_beginning
    def h_cursor_beginning(self, ch):

        g.trace('LeoMiniBuffer', repr(ch))
        self.cursor_position = 0
    #@+node:ekr.20170510095136.3: *3* LeoMiniBuffer.h_cursor_end
    def h_cursor_end(self, ch):
        
        g.trace('LeoMiniBuffer', repr(ch))
        self.cursor_position = len(self.value)
    #@+node:ekr.20170510095136.4: *3* LeoMiniBuffer.h_cursor_left
    def h_cursor_left(self, ch):
        
        g.trace('LeoMiniBuffer', repr(ch))
        self.cursor_position = max(0, self.cursor_position -1)
    #@+node:ekr.20170510095136.5: *3* LeoMiniBuffer.h_cursor_right
    def h_cursor_right(self, ch):

        g.trace('LeoMiniBuffer', repr(ch))
        self.cursor_position = min(len(self.value), self.cursor_position+1)


    #@+node:ekr.20170510095136.6: *3* LeoMiniBuffer.h_delete_left
    def h_delete_left(self, ch):

        g.trace('LeoMiniBuffer', repr(ch))
        n = self.cursor_position
        s = self.value
        if 0 <= n <= len(s):
            self.value = s[:n] + s[n+1:]
            self.cursor_position -= 1
    #@+node:ekr.20170510095136.7: *3* LeoMiniBuffer.h_insert
    def h_insert(self, ch):

        g.trace('LeoMiniBuffer', ch, self.value)
        n = self.cursor_position + 1
        s = self.value
        self.value = s[:n] + chr(ch) + s[n:]
        self.cursor_position += 1
    #@+node:ekr.20170510100003.1: *3* LeoMiniBuffer.h_return (executes command)
    def h_return (self, ch):
        '''
        Handle the return key in the minibuffer.
        Send the contents to k.masterKeyHandler.
        '''
        c = self.leo_c
        k = c.k
        g.trace('LeoMiniBuffer', repr(ch), repr(self.value))
        k.masterCommand(
            commandName=self.value.strip(),
            event=LeoKeyEvent(c,char='',event='',shortcut='',w=self),
            func=None,
            stroke=None,
        )
    #@+node:ekr.20170510094104.1: *3* LeoMiniBuffer.set_handlers
    def set_handlers(self):
        
        g.trace('LeoMiniBuffer', g.callers())

        def test(ch):
            return 32 <= ch <= 127
        
        # Override all other complex handlers.
        self.complex_handlers = [
            (test, self.h_insert),
        ]
        self.handlers.update({
            # All other keys are passed on.
                # curses.ascii.TAB:    self.h_exit_down,
                # curses.KEY_BTAB:     self.h_exit_up,
            curses.ascii.NL:        self.h_return,
            curses.ascii.CR:        self.h_return,
            curses.KEY_HOME:        self.h_cursor_beginning,  # 262
            curses.KEY_END:         self.h_cursor_end,        # 358.
            curses.KEY_LEFT:        self.h_cursor_left,
            curses.KEY_RIGHT:       self.h_cursor_right,
            curses.ascii.BS:        self.h_delete_left,
            curses.KEY_BACKSPACE:   self.h_delete_left,
        })
    #@-others
#@+node:ekr.20170506035146.1: ** class LeoMLTree (npyscreen.MLTree)
class LeoMLTree(npyscreen.MLTree):

    _contained_widgets = LeoTreeLine
    ###
        # CHECK_VALUE             = True
        # ALLOW_CONTINUE_EDITING  = True
        # CONTINUE_EDITING_AFTER_EDITING_ONE_LINE = True
        
    def set_up_handlers(self):
        super(LeoMLTree, self).set_up_handlers()
        assert not hasattr(self, 'hidden_root_node'), repr(self)
        self.leo_c = None # Set later.
        self.hidden_root_node = None
        self.set_handlers()

    #@+others
    #@+node:ekr.20170506045346.1: *3*  LeoMLTree.Handlers
    #@+node:ekr.20170506044733.12: *4* LeoMLTree.h_delete_line_value (from MultiLineEdit)
    def h_delete_line_value(self, ch):
        self.delete_line_value()

    #@+node:ekr.20170506044733.10: *4* LeoMLTree.h_edit_cursor_line_value
    def h_edit_cursor_line_value(self, ch):
        
        if 1:
            self._continue_editing()
        else:
            continue_line = self.edit_cursor_line_value()
            if continue_line: ### and self.CONTINUE_EDITING_AFTER_EDITING_ONE_LINE:
                self._continue_editing()
            
    #@+node:ekr.20170506044733.9: *4* LeoMLTree.h_insert_next_line
    def h_insert_next_line(self, ch):
        
        # pylint: disable=len-as-condition
        if len(self.values) == self.cursor_line - 1 or len(self.values) == 0:
            self.values.append(self.get_new_value())
            self.cursor_line += 1
            self.display()
            cont = self.edit_cursor_line_value()
            if cont: ### and self.ALLOW_CONTINUE_EDITING:
                self._continue_editing()
        else:
            self.cursor_line += 1
            self.insert_line_value()

    #@+node:ekr.20170506044733.11: *4* LeoMLTree.h_insert_value
    def h_insert_value(self, ch):
        return self.insert_line_value()

    #@+node:ekr.20170506035413.1: *4* LeoMLTree.h_left
    def h_left(self, ch):
        
        node = self.values[self.cursor_line]
        if self._has_children(node) and node.expanded:
            self.h_collapse_tree(ch)
        else:
            self.h_cursor_line_up(ch)
    #@+node:ekr.20170506035419.1: *4* LeoMLTree.h_right
    def h_right(self, ch):
        
        node = self.values[self.cursor_line]
        if self._has_children(node):
            if node.expanded:
                self.h_cursor_line_down(ch)
            else:
                self.h_expand_tree(ch)
        else:
            self.h_cursor_line_down(ch)
    #@+node:ekr.20170507175304.1: *4* LeoMLTree.set_handlers
    def set_handlers(self):
        
        # pylint: disable=no-member
        d = {
            curses.KEY_LEFT:    self.h_left,
            curses.KEY_RIGHT:   self.h_right,
            # From MultiLineEditable.
            ord('h'):               self.h_edit_cursor_line_value,
            ord('i'):               self.h_insert_value,
            ord('o'):               self.h_insert_next_line,
            # curses.ascii.CR:        self.h_edit_cursor_line_value,
            # curses.ascii.NL:        self.h_edit_cursor_line_value,
            # curses.ascii.SP:        self.h_edit_cursor_line_value,
            # curses.ascii.DEL:       self.h_delete_line_value,
            # curses.ascii.BS:        self.h_delete_line_value,
            # curses.KEY_BACKSPACE:   self.h_delete_line_value,
        }
        self.handlers.update(d)
    #@+node:ekr.20170506044733.7: *3* _continue_editing (REVISE)
    def _continue_editing(self):
        
        trace = True
        active_line = self._my_widgets[(self.cursor_line-self.start_display_at)]
        assert isinstance(active_line, npyscreen.TreeLine)
        code = getattr(active_line, 'how_exited', None)
        if trace: self.dump_code(code)
        if hasattr(active_line, 'how_exited'):
            self.values.insert(self.cursor_line+1, self.get_new_value())
            self.cursor_line += 1
            self.display()
            self.edit_cursor_line_value()
            # active_line = self._my_widgets[(self.cursor_line-self.start_display_at)]
    #@+node:ekr.20170506044733.6: *3* delete_line_value (REVISE)
    def delete_line_value(self):

        trace = True
        if trace:
            g.trace('cursor_line:', repr(self.cursor_line))
            self.dump_values
        if self.values:
            del self.values[self.cursor_line]
            self.display()
    #@+node:ekr.20170507171518.1: *3* dump_code/values/widgets (new)
    def dump_code(self, code):
        d = {
            -2: 'left', -1: 'up', 1: 'down', 2: 'right',
            127: 'escape', 130: 'mouse',
        }
        return d.get(code) or 'unknown how_exited: %r' % code

    def dump_values(self):
        def info(z):
            return '%15s: %s' % (z._parent.get_content(), z.get_content())
        g.printList([info(z) for z in self.values])
        
    def dump_widgets(self):
        def info(z):
            return '%s.%s' % (id(z), z.__class__.__name__)
        g.printList([info(z) for z in self._my_widgets])
    #@+node:ekr.20170506044733.4: *3* edit_cursor_line_value (no change)
    def edit_cursor_line_value(self):

        trace = True
        if not self.values:
            if trace: g.trace('no values')
            self.insert_line_value()
            return False
        try:
            # g.trace('cursor_line: %r, start_display_at: %r = %r' % (
                # self.cursor_line, self.start_display_at,
                # self.cursor_line-self.start_display_at))
            active_line = self._my_widgets[(self.cursor_line-self.start_display_at)]
            g.trace('active_line: %r' % active_line)
        except IndexError:
            # pylint: disable=pointless-statement
            self._my_widgets[0]
                # Does this have something to do with weakrefs?
            self.cursor_line = 0
            self.insert_line_value()
            return True
        active_line.highlight = False
        active_line.edit()
        try:
            self.values[self.cursor_line] = active_line.value
        except IndexError:
            self.values.append(active_line.value)
            if not self.cursor_line:
                self.cursor_line = 0
            self.cursor_line = len(self.values) - 1
        self.reset_display_cache()
        # if self.CHECK_VALUE:
        # if not self.check_line_value(self.values[self.cursor_line]):
        # if not self.values[self.cursor_line]
            # self.delete_line_value()
            # return False
        self.display()
        return True
    #@+node:ekr.20170506044733.2: *3* get_new_value (rewritten)
    def get_new_value(self):
        '''
        Insert a new outline TreeData widget at the current line.
        As with Leo, insert as the first child of the current line if
        the current line is expanded. Otherwise insert after the current line.
        '''
        trace = True
        trace_values = False
        node = self.values[self.cursor_line]
        if trace and trace_values:
            g.trace(node)
            self.dump_values()
        headline = 'New headline'
        if node.has_children() and node.expanded:
            node = node.new_child_at(index=0, content=headline)
        elif node.get_parent():
            parent = node.get_parent()
            node = parent.new_child(content=headline)
        else:
            parent = self.hidden_root_node
            index = parent._children.index(node)
            node = parent.new_child_at(index=index, content=headline)
        if trace: g.trace('%3s %s' % (self.cursor_line, headline))
        return node
    #@+node:ekr.20170506044733.5: *3* insert_line_value (changed)
    def insert_line_value(self):
        
        trace = True
        trace_values = False
        if trace:
            g.trace('cursor_line:', repr(self.cursor_line))
            if trace_values: self.dump_values()
        if self.cursor_line is None:
            self.cursor_line = 0
        # Revised
        self.values.insert(self.cursor_line+1, self.get_new_value())
        self.cursor_line += 1
        self.display()
        cont = self.edit_cursor_line_value()
        if cont: ### and self.ALLOW_CONTINUE_EDITING:
            self._continue_editing()
    #@-others
#@+node:ekr.20170507184329.1: ** class LeoTreeData (npyscreen.TreeData)
class LeoTreeData(npyscreen.TreeData):
    '''A TreeData class that has a len and new_first_child methods.'''

    def __len__(self):
        return len(self.content)
        
    def new_child_at(self, index, *args, **keywords):
        '''Same as new_child, with insert(index, c) instead of append(c)'''
        if self.CHILDCLASS:
            cld = self.CHILDCLASS
        else:
            cld = type(self)
        c = cld(parent=self, *args, **keywords)
        self._children.insert(index, c)
        return weakref.proxy(c)
#@-others
#@@language python
#@@tabwidth -4
#@-leo
