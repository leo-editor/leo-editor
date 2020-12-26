# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20031218072017.3093: * @file leoGlobals.py
#@@first
"""
Global constants, variables and utility functions used throughout Leo.

Important: This module imports no other Leo module.
"""
#@+<< imports >>
#@+node:ekr.20050208101229: ** << imports >> (leoGlobals)
#
# Don't import leoTest here: it messes up Leo's startup code.
    # from leo.core import leoTest

import inspect
import re
import sys
import time

# Transcrypt does not support these modules
# __pragma__ ('skip')

import binascii
import codecs
from functools import reduce
import glob
import io
import importlib
import operator
import os
#
# Do NOT import pdb here!  We shall define pdb as a _function_ below.
    # import pdb
import shlex
import shutil
import string
import subprocess
import tempfile
import traceback
import types
import unittest
import urllib
import urllib.parse as urlparse

try:
    import gc
except ImportError:
    gc = None
try:
    import gettext
except ImportError:  # does not exist in jython.
    gettext = None

StringIO = io.StringIO

# __pragma__ ('noskip')
#@-<< imports >>
in_bridge = False
    # Set to True in leoBridge.py just before importing leo.core.leoApp.
    # This tells leoApp to load a null Gui.
minimum_python_version = '3.6'  # #1215.
isPython3 = sys.version_info >= (3, 0, 0)
isMac = sys.platform.startswith('darwin')
isWindows = sys.platform.startswith('win')
#@+<< define g.globalDirectiveList >>
#@+node:EKR.20040610094819: ** << define g.globalDirectiveList >>
# Visible externally so plugins may add to the list of directives.
globalDirectiveList = [
    # Order does not matter.
    'all',
    'beautify',
    'colorcache', 'code', 'color', 'comment', 'c',
    'delims', 'doc',
    'encoding', 'end_raw',
    'first', 'header', 'ignore',
    'killbeautify', 'killcolor',
    'language', 'last', 'lineending',
    'markup',
    'nobeautify',
    'nocolor-node', 'nocolor', 'noheader', 'nowrap',
    'nopyflakes',  # Leo 6.1.
    'nosearch',  # Leo 5.3.
    'others', 'pagewidth', 'path', 'quiet',
    'raw', 'root-code', 'root-doc', 'root', 'silent',
    'tabwidth', 'terse',
    'unit', 'verbose', 'wrap',
]

directives_pat = None  # Set below.
#@-<< define g.globalDirectiveList >>
#@+<< define global decorator dicts >>
#@+node:ekr.20150510103918.1: ** << define global decorator dicts >> (leoGlobals.py)
#@@nobeautify
#@@language rest
#@+at
# The cmd_instance_dict supports per-class @cmd decorators. For example, the
# following appears in leo.commands.
#
#     def cmd(name):
#         """Command decorator for the abbrevCommands class."""
#         return g.new_cmd_decorator(name, ['c', 'abbrevCommands',])
#
# For commands based on functions, use the @g.command decorator.
#@@c
#@@language python

global_commands_dict = {}

cmd_instance_dict = {
    # Keys are class names, values are attribute chains.
    'AbbrevCommandsClass':      ['c', 'abbrevCommands'],
    'AtFile':                   ['c', 'atFileCommands'],
    'AutoCompleterClass':       ['c', 'k', 'autoCompleter'],
    'ChapterController':        ['c', 'chapterController'],
    'Commands':                 ['c'],
    'ControlCommandsClass':     ['c', 'controlCommands'],
    'DebugCommandsClass':       ['c', 'debugCommands'],
    'EditCommandsClass':        ['c', 'editCommands'],
    'EditFileCommandsClass':    ['c', 'editFileCommands'],
    'FileCommands':             ['c', 'fileCommands'],
    'HelpCommandsClass':        ['c', 'helpCommands'],
    'KeyHandlerClass':          ['c', 'k'],
    'KeyHandlerCommandsClass':  ['c', 'keyHandlerCommands'],
    'KillBufferCommandsClass':  ['c', 'killBufferCommands'],
    'LeoApp':                   ['g', 'app'],
    'LeoFind':                  ['c', 'findCommands'],
    'LeoImportCommands':        ['c', 'importCommands'],
    # 'MacroCommandsClass':       ['c', 'macroCommands'],
    'PrintingController':       ['c', 'printingController'],
    'RectangleCommandsClass':   ['c', 'rectangleCommands'],
    'RstCommands':              ['c', 'rstCommands'],
    'SpellCommandsClass':       ['c', 'spellCommands'],
    'Undoer':                   ['c', 'undoer'],
    'VimCommands':              ['c', 'vimCommands'],
}
#@-<< define global decorator dicts >>
#@+<< define g.decorators >>
#@+node:ekr.20150508165324.1: ** << define g.Decorators >>
#@+others
#@+node:ekr.20170219173203.1: *3* g.callback
def callback(func):
    """
    A global decorator that protects Leo against crashes in callbacks.

    This is the recommended way of defining all callback.

        @g.callback
        def a_callback(...):
            c = event.get('c')
            ...
    """

    def callback_wrapper(*args, **keys):
        """Callback for the @g.callback decorator."""
        try:
            return func(*args, **keys)
        except Exception:
            g.es_exception()

    return callback_wrapper
#@+node:ekr.20150510104148.1: *3* g.check_cmd_instance_dict
def check_cmd_instance_dict(c, g):
    """
    Check g.check_cmd_instance_dict.
    This is a permanent unit test, called from c.finishCreate.
    """
    d = cmd_instance_dict
    for key in d:
        ivars = d.get(key)
        obj = ivars2instance(c, g, ivars)
            # Produces warnings.
        if obj:
            name = obj.__class__.__name__
            if name != key:
                g.trace('class mismatch', key, name)
#@+node:ville.20090521164644.5924: *3* g.command (decorator)
class Command:
    """
    A global decorator for creating commands.

    This is the recommended way of defining all new commands, including
    commands that could befined inside a class. The typical usage is:

        @g.command('command-name')
        def A_Command(event):
            c = event.get('c')
            ...

    g can *not* be used anywhere in this class!
    """

    def __init__(self, name, **kwargs):
        """Ctor for command decorator class."""
        self.name = name

    def __call__(self, func):
        """Register command for all future commanders."""
        global_commands_dict[self.name] = func
        if app:
            for c in app.commanders():
                c.k.registerCommand(self.name, func)
        # Inject ivars for plugins_menu.py.
        func.__func_name__ = func.__name__ # For leoInteg.
        func.is_command = True
        func.command_name = self.name
        return func

command = Command
#@+node:ekr.20171124070654.1: *3* g.command_alias
def command_alias(alias, func):
    """Create an alias for the *already defined* method in the Commands class."""
    from leo.core import leoCommands
    assert hasattr(leoCommands.Commands, func.__name__)
    funcToMethod(func, leoCommands.Commands, alias)
#@+node:ekr.20171123095526.1: *3* g.commander_command (decorator)
class CommanderCommand:
    """
    A global decorator for creating commander commands, that is, commands
    that were formerly methods of the Commands class in leoCommands.py.
    
    Usage:

        @g.command('command-name')
        def command_name(self, *args, **kwargs):
            ...
        
    The decorator injects command_name into the Commander class and calls
    funcToMethod so the ivar will be injected in all future commanders.

    g can *not* be used anywhere in this class!
    """

    def __init__(self, name, **kwargs):
        """Ctor for command decorator class."""
        self.name = name

    def __call__(self, func):
        """Register command for all future commanders."""

        def commander_command_wrapper(event):
            c = event.get('c')
            method = getattr(c, func.__name__, None)
            method(event=event)

        # Inject ivars for plugins_menu.py.
        commander_command_wrapper.__func_name__ = func.__name__ # For leoInteg.
        commander_command_wrapper.__name__ = self.name
        commander_command_wrapper.__doc__ = func.__doc__
        global_commands_dict[self.name] = commander_command_wrapper
        if app:
            from leo.core import leoCommands
            funcToMethod(func, leoCommands.Commands)
            for c in app.commanders():
                c.k.registerCommand(self.name, func)
        # Inject ivars for plugins_menu.py.
        func.is_command = True
        func.command_name = self.name
        return func

commander_command = CommanderCommand
#@+node:ekr.20150508164812.1: *3* g.ivars2instance
def ivars2instance(c, g, ivars):
    """
    Return the instance of c given by ivars.
    ivars is a list of strings.
    A special case: ivars may be 'g', indicating the leoGlobals module.
    """
    if not ivars:
        g.trace('can not happen: no ivars')
        return None
    ivar = ivars[0]
    if ivar not in ('c', 'g'):
        g.trace('can not happen: unknown base', ivar)
        return None
    obj = c if ivar == 'c' else g
    for ivar in ivars[1:]:
        obj = getattr(obj, ivar, None)
        if not obj:
            g.trace('can not happen: unknown attribute', obj, ivar, ivars)
            break
    return obj
#@+node:ekr.20150508134046.1: *3* g.new_cmd_decorator (decorator)
def new_cmd_decorator(name, ivars):
    """
    Return a new decorator for a command with the given name.
    Compute the class *instance* using the ivar string or list.
    
    Don't even think about removing the @cmd decorators!
    See https://github.com/leo-editor/leo-editor/issues/325
    """

    def _decorator(func):

        def new_cmd_wrapper(event):
            c = event.c
            self = g.ivars2instance(c, g, ivars)
            try:
                func(self, event=event)
                    # Don't use a keyword for self.
                    # This allows the VimCommands class to use vc instead.
            except Exception:
                g.es_exception()

        new_cmd_wrapper.__func_name__ = func.__name__ # For leoInteg.
        new_cmd_wrapper.__name__ = name
        new_cmd_wrapper.__doc__ = func.__doc__
        global_commands_dict[name] = new_cmd_wrapper
            # Put the *wrapper* into the global dict.
        return func
            # The decorator must return the func itself.

    return _decorator
#@-others
#@-<< define g.decorators >>
#@+<< define regex's >>
#@+node:ekr.20200810093517.1: ** << define regex's >>
g_language_pat = re.compile(r'^@language\s+(\w+)+', re.MULTILINE)
    # Regex used by this module, and in leoColorizer.py.
#
# Patterns used only in this module...
g_is_directive_pattern = re.compile(r'^\s*@([\w-]+)\s*')
    # This pattern excludes @encoding.whatever and @encoding(whatever)
    # It must allow @language python, @nocolor-node, etc.
g_noweb_root = re.compile('<' + '<' + '*' + '>' + '>' + '=', re.MULTILINE)
g_pos_pattern = re.compile(r':(\d+),?(\d+)?,?([-\d]+)?,?(\d+)?$')
g_tabwidth_pat = re.compile(r'(^@tabwidth)', re.MULTILINE)
#@-<< define regex's >>
tree_popup_handlers = []  # Set later.
user_dict = {}
    # Non-persistent dictionary for free use by scripts and plugins.
# g = None
app = None  # The singleton app object. Set by runLeo.py.
# Global status vars.
inScript = False  # A synonym for app.inScript
unitTesting = False  # A synonym for app.unitTesting.
#@+others
#@+node:ekr.20201211182722.1: ** g.Backup
#@+node:ekr.20201211182659.1: *3* g.standard_timestamp
def standard_timestamp():
    """Return a reasonable timestamp."""
    return time.strftime("%Y%m%d-%H%M%S")
#@+node:ekr.20201211183100.1: *3* g.get_backup_directory
def get_backup_path(sub_directory):
    """
    Return the full path to the subdirectory of the main backup directory.
    
    The main backup directory is computed as follows:
        
    1. os.environ['LEO_BACKUP']
    2. ~/Backup
    """
    # Transcrypt does not support Python's pathlib module.
    # __pragma__ ('skip')

    from pathlib import Path
    # Compute the main backup directory.
    # First, try the LEO_BACKUP directory.
    backup = None
    try:
        backup = os.environ['LEO_BACKUP']
        if not os.path.exists(backup):
            backup = None
    except KeyError:
        pass
    except Exception:
        g.es_exception()
    # Second, try ~/Backup.
    if not backup:
        backup = os.path.join(str(Path.home()), 'Backup')
        if not os.path.exists(backup):
            backup = None
    if not backup:
        return None
    # Compute the path to backup/sub_directory
    directory = os.path.join(backup, sub_directory)
    return directory if os.path.exists(directory) else None
    
    # __pragma__ ('noskip')
#@+node:ekr.20140711071454.17644: ** g.Classes & class accessors
#@+node:ekr.20120123115816.10209: *3* class g.BindingInfo & isBindingInfo
class BindingInfo:
    """
    A class representing any kind of key binding line.

    This includes other information besides just the KeyStroke.
    """
    # Important: The startup code uses this class,
    # so it is convenient to define it in leoGlobals.py.
    #@+others
    #@+node:ekr.20120129040823.10254: *4* bi.__init__
    def __init__(
        self,
        kind,
        commandName='',
        func=None,
        nextMode=None,
        pane=None,
        stroke=None,
    ):
        if not g.isStrokeOrNone(stroke):
            g.trace('***** (BindingInfo) oops', repr(stroke))
        self.kind = kind
        self.commandName = commandName
        self.func = func
        self.nextMode = nextMode
        self.pane = pane
        self.stroke = stroke
            # The *caller* must canonicalize the shortcut.
    #@+node:ekr.20120203153754.10031: *4* bi.__hash__
    def __hash__(self):
        return self.stroke.__hash__() if self.stroke else 0
    #@+node:ekr.20120125045244.10188: *4* bi.__repr__ & ___str_& dump
    def __repr__(self):
        return self.dump()

    __str__ = __repr__

    def dump(self):
        result = [f"BindingInfo {self.kind:17}"]
        # Print all existing ivars.
        table = ('commandName', 'func', 'nextMode', 'pane', 'stroke')
        for ivar in table:
            if hasattr(self, ivar):
                val = getattr(self, ivar)
                if val not in (None, 'none', 'None', ''):
                    if ivar == 'func':
                        # pylint: disable=no-member
                        val = val.__name__
                    s = f"{ivar}: {val!r}"
                    result.append(s)
        # Clearer w/o f-string.
        return f"[%s]" % ' '.join(result).strip()
    #@+node:ekr.20120129040823.10226: *4* bi.isModeBinding
    def isModeBinding(self):
        return self.kind.startswith('*mode')
    #@-others
def isBindingInfo(obj):
    return isinstance(obj, BindingInfo)
#@+node:ekr.20031218072017.3098: *3* class g.Bunch (Python Cookbook)
#@@language rest
#@+at
# From The Python Cookbook:
#
# Create a Bunch whenever you want to group a few variables:
#
#     point = Bunch(datum=y, squared=y*y, coord=x)
#
# You can read/write the named attributes you just created, add others,
# del some of them, etc::
#
#     if point.squared > threshold:
#         point.isok = True
#@@c
#@@language python


class Bunch:
    """A class that represents a colection of things.

    Especially useful for representing a collection of related variables."""

    def __init__(self, **keywords):
        self.__dict__.update(keywords)

    def __repr__(self):
        return self.toString()

    def ivars(self):
        return sorted(self.__dict__)

    def keys(self):
        return sorted(self.__dict__)

    def toString(self):
        tag = self.__dict__.get('tag')
        entries = [
            f"{key}: {str(self.__dict__.get(key)) or repr(self.__dict__.get(key))}"
                for key in self.ivars() if key != 'tag'
        ]
        # Fail.
        result = [f'g.Bunch({tag or ""})']
        result.extend(entries)
        return '\n    '.join(result) + '\n'

    # Used by new undo code.

    def __setitem__(self, key, value):
        """Support aBunch[key] = val"""
        return operator.setitem(self.__dict__, key, value)

    def __getitem__(self, key):
        """Support aBunch[key]"""
        # g.pr('g.Bunch.__getitem__', key)
        return operator.getitem(self.__dict__, key)

    def get(self, key, theDefault=None):
        return self.__dict__.get(key, theDefault)

    def __contains__(self, key):  # New.
        # g.pr('g.Bunch.__contains__', key in self.__dict__, key)
        return key in self.__dict__

bunch = Bunch
#@+node:ekr.20120219154958.10492: *3* class g.EmergencyDialog
class EmergencyDialog:
    """A class that creates an tkinter dialog with a single OK button."""
    
    # Transcrypt does not support Python's tkinter module.
    # __pragma__ ('skip')
    
    #@+others
    #@+node:ekr.20120219154958.10493: *4* emergencyDialog.__init__
    def __init__(self, title, message):
        """Constructor for the leoTkinterDialog class."""
        self.answer = None  # Value returned from run()
        self.title = title
        self.message = message
        self.buttonsFrame = None  # Frame to hold typical dialog buttons.
        self.defaultButtonCommand = None
            # Command to call when user closes the window
            # by clicking the close box.
        self.frame = None  # The outermost frame.
        self.root = None  # Created in createTopFrame.
        self.top = None  # The toplevel Tk widget.
        self.createTopFrame()
        buttons = [{
            "text": "OK",
            "command": self.okButton,
            "default": True,
        }]
        self.createButtons(buttons)
        self.top.bind("<Key>", self.onKey)
    #@+node:ekr.20120219154958.10494: *4* emergencyDialog.createButtons
    def createButtons(self, buttons):
        """Create a row of buttons.

        buttons is a list of dictionaries containing
        the properties of each button.
        """
        import tkinter as Tk
        assert(self.frame)
        self.buttonsFrame = f = Tk.Frame(self.top)
        f.pack(side="top", padx=30)
        # Buttons is a list of dictionaries, with an empty dictionary
        # at the end if there is only one entry.
        buttonList = []
        for d in buttons:
            text = d.get("text", "<missing button name>")
            isDefault = d.get("default", False)
            underline = d.get("underline", 0)
            command = d.get("command", None)
            bd = 4 if isDefault else 2
            b = Tk.Button(f, width=6, text=text, bd=bd,
                underline=underline, command=command)
            b.pack(side="left", padx=5, pady=10)
            buttonList.append(b)
            if isDefault and command:
                self.defaultButtonCommand = command
        return buttonList
    #@+node:ekr.20120219154958.10495: *4* emergencyDialog.createTopFrame
    def createTopFrame(self):
        """Create the Tk.Toplevel widget for a leoTkinterDialog."""
        import tkinter as Tk
        self.root = Tk.Tk()
        self.top = Tk.Toplevel(self.root)
        self.top.title(self.title)
        self.root.withdraw()
        self.frame = Tk.Frame(self.top)
        self.frame.pack(side="top", expand=1, fill="both")
        label = Tk.Label(self.frame, text=self.message, bg='white')
        label.pack(pady=10)
    #@+node:ekr.20120219154958.10496: *4* emergencyDialog.okButton
    def okButton(self):
        """Do default click action in ok button."""
        self.top.destroy()
        self.top = None
    #@+node:ekr.20120219154958.10497: *4* emergencyDialog.onKey
    def onKey(self, event):
        """Handle Key events in askOk dialogs."""
        self.okButton()
    #@+node:ekr.20120219154958.10498: *4* emergencyDialog.run
    def run(self):
        """Run the modal emergency dialog."""
        # Suppress f-stringify.
        self.top.geometry(f"%dx%d%+d%+d" % (300, 200, 50, 50))
        self.top.lift()
        self.top.grab_set()  # Make the dialog a modal dialog.
        self.root.wait_window(self.top)
    #@-others

    # __pragma__ ('noskip')
#@+node:ekr.20040331083824.1: *3* class g.FileLikeObject
# Note: we could use StringIo for this.


class FileLikeObject:
    """Define a file-like object for redirecting writes to a string.

    The caller is responsible for handling newlines correctly."""
    #@+others
    #@+node:ekr.20050404151753: *4*  ctor (g.FileLikeObject)
    def __init__(self, encoding='utf-8', fromString=None):

        # New in 4.2.1: allow the file to be inited from string s.
        self.encoding = encoding or 'utf-8'
        if fromString:
            self.list = g.splitLines(fromString)  # Must preserve newlines!
        else:
            self.list = []
        self.ptr = 0
    # In CStringIO the buffer is read-only if the initial value (fromString) is non-empty.
    #@+node:ekr.20050404151753.1: *4* clear (g.FileLikeObject)
    def clear(self):
        self.list = []
    #@+node:ekr.20050404151753.2: *4* close (g.FileLikeObject)
    def close(self):
        pass
        # The StringIo version free's the memory buffer.
    #@+node:ekr.20050404151753.3: *4* flush (g.FileLikeObject)
    def flush(self):
        pass
    #@+node:ekr.20050404151753.4: *4* get & getvalue & read (g.FileLikeObject)
    def get(self):
        return ''.join(self.list)

    getvalue = get  # for compatibility with StringIo
    read = get  # for use by sax.
    #@+node:ekr.20050404151753.5: *4* readline (g.FileLikeObject)
    def readline(self):
        """Read the next line using at.list and at.ptr."""
        if self.ptr < len(self.list):
            line = self.list[self.ptr]
            self.ptr += 1
            return line
        return ''
    #@+node:ekr.20050404151753.6: *4* write (g.FileLikeObject)
    def write(self, s):
        if s:
            if isinstance(s, bytes):
                s = g.toUnicode(s, self.encoding)
            self.list.append(s)
    #@-others
fileLikeObject = FileLikeObject
    # For compatibility.
#@+node:ekr.20120123143207.10223: *3* class g.GeneralSetting
# Important: The startup code uses this class,
# so it is convenient to define it in leoGlobals.py.


class GeneralSetting:
    """A class representing any kind of setting except shortcuts."""

    def __init__(self, kind,
        encoding=None,
        ivar=None,
        setting=None,
        val=None,
        path=None,
        tag='setting',
        unl=None,
    ):
        self.encoding = encoding
        self.ivar = ivar
        self.kind = kind
        self.path = path
        self.unl = unl
        self.setting = setting
        self.val = val
        self.tag = tag

    def __repr__(self):
        # Better for g.printObj.
        val = str(self.val).replace('\n', ' ')
        return (
            f"GS: {g.shortFileName(self.path):20} "
            f"{self.kind:7} = {g.truncate(val, 50)}")

    dump = __repr__
    __str__ = __repr__
#@+node:ekr.20120201164453.10090: *3* class g.KeyStroke & isStroke/OrNone
class KeyStroke:
    """
    A class that represent any key stroke or binding.
    
    stroke.s is the "canonicalized" stroke.
    """
    #@+others
    #@+node:ekr.20180414195401.2: *4*  ks.__init__
    def __init__(self, binding):

        if binding:
            self.s = self.finalize_binding(binding)
        else:
            self.s = None
    #@+node:ekr.20120203053243.10117: *4* ks.__eq__, etc
    #@+at All these must be defined in order to say, for example:
    #     for key in sorted(d)
    # where the keys of d are KeyStroke objects.
    #@@c

    def __eq__(self, other):
        if not other:
            return False
        if hasattr(other, 's'):
            return self.s == other.s
        return self.s == other

    def __lt__(self, other):
        if not other:
            return False
        if hasattr(other, 's'):
            return self.s < other.s
        return self.s < other

    def __le__(self, other): return self.__lt__(other) or self.__eq__(other)

    def __ne__(self, other): return not self.__eq__(other)

    def __gt__(self, other): return not self.__lt__(other) and not self.__eq__(other)

    def __ge__(self, other): return not self.__lt__(other)
    #@+node:ekr.20120203053243.10118: *4* ks.__hash__
    # Allow KeyStroke objects to be keys in dictionaries.

    def __hash__(self):
        return self.s.__hash__() if self.s else 0
    #@+node:ekr.20120204061120.10067: *4* ks.__repr___ & __str__
    def __repr__(self):
        return f"<KeyStroke: {repr(self.s)}>"

    def __str__(self):
        return repr(self.s)
    #@+node:ekr.20180417160703.1: *4* ks.dump
    def dump(self):
        """Show results of printable chars."""
        for i in range(128):
            s = chr(i)
            stroke = g.KeyStroke(s)
            if stroke.s != s:
                print(f"{i:2} {s!r:10} {stroke.s!r}")
        for ch in ('backspace', 'linefeed', 'return', 'tab'):
            stroke = g.KeyStroke(ch)
            print(f'{"":2} {ch!r:10} {stroke.s!r}')
    #@+node:ekr.20180415082249.1: *4* ks.finalize_binding
    def finalize_binding(self, binding):

        trace = False and 'keys' in g.app.debug
            # This trace is good for devs only.
        self.mods = self.find_mods(binding)
        s = self.strip_mods(binding)
        s = self.finalize_char(s)
            # May change self.mods.
        mods = ''.join([f"{z.capitalize()}+" for z in self.mods])
        if trace and 'meta' in self.mods:
            g.trace(f"{binding:20}:{self.mods:>20} ==> {mods+s}")
        return mods + s
    #@+node:ekr.20180415083926.1: *4* ks.finalize_char & helper
    def finalize_char(self, s):
        """Perform very-last-minute translations on bindings."""
        #
        # Retain "bigger" spelling for gang-of-four bindings with modifiers.
        shift_d = {
            'bksp': 'BackSpace',
            'backspace': 'BackSpace',
            'backtab': 'Tab',  # The shift mod will convert to 'Shift+Tab',
            'linefeed': 'Return',
            '\r': 'Return',
            'return': 'Return',
            'tab': 'Tab',
        }
        if self.mods and s.lower() in shift_d:
            return shift_d.get(s.lower())
                # Returning '' breaks existing code.
        #
        # Make all other translations...
        #
        # This dict ensures proper capitalization.
        # It also translates legacy Tk binding names to ascii chars.
        translate_d = {
            #
            # The gang of four...
            'bksp': 'BackSpace',
            'backspace': 'BackSpace',
            'backtab': 'Tab',  # The shift mod will convert to 'Shift+Tab',
            'linefeed': '\n',
            '\r': '\n',
            'return': '\n',
            'tab': 'Tab',
            #
            # Special chars...
            'delete': 'Delete',
            'down': 'Down',
            'end': 'End',
            'enter': 'Enter',
            'escape': 'Escape',
            'home': 'Home',
            'insert': 'Insert',
            'left': 'Left',
            'next': 'Next',
            'prior': 'Prior',
            'right': 'Right',
            'up': 'Up',
            #
            # Qt key names...
            'del': 'Delete',
            'dnarrow': 'Down',
            'esc': 'Escape',
            'ins': 'Insert',
            'ltarrow': 'Left',
            'pagedn': 'Next',
            'pageup': 'Prior',
            'pgdown': 'Next',
            'pgup': 'Prior',
            'rtarrow': 'Right',
            'uparrow': 'Up',
            #
            # Legacy Tk binding names...
            "ampersand": "&",
            "asciicircum": "^",
            "asciitilde": "~",
            "asterisk": "*",
            "at": "@",
            "backslash": "\\",
            "bar": "|",
            "braceleft": "{",
            "braceright": "}",
            "bracketleft": "[",
            "bracketright": "]",
            "colon": ":",
            "comma": ",",
            "dollar": "$",
            "equal": "=",
            "exclam": "!",
            "greater": ">",
            "less": "<",
            "minus": "-",
            "numbersign": "#",
            "quotedbl": '"',
            "quoteright": "'",
            "parenleft": "(",
            "parenright": ")",
            "percent": "%",
            "period": ".",
            "plus": "+",
            "question": "?",
            "quoteleft": "`",
            "semicolon": ";",
            "slash": "/",
            "space": " ",
            "underscore": "_",
        }
        #
        # pylint: disable=undefined-loop-variable
            # Looks like a pylint bug.
        if s in (None, 'none', 'None'):
            return 'None'
        if s.lower() in translate_d:
            s = translate_d.get(s.lower())
            return self.strip_shift(s)
        if len(s) > 1 and s.find(' ') > -1:
            # #917: not a pure, but should be ignored.
            return ''
        if s.isalpha():
            if len(s) == 1:
                if 'shift' in self.mods:
                    if len(self.mods) == 1:
                        self.mods.remove('shift')
                        s = s.upper()
                    else:
                        s = s.lower()
                elif self.mods:
                    s = s.lower()
            else:
                # 917: Ignore multi-byte alphas not in the table.
                s = ''
                if 0:
                    # Make sure all special chars are in translate_d.
                    if g.app.gui:  # It may not exist yet.
                        if s.capitalize() in g.app.gui.specialChars:
                            s = s.capitalize()
            return s
        #
        # Translate shifted keys to their appropriate alternatives.
        return self.strip_shift(s)
    #@+node:ekr.20180502104829.1: *5* ks.strip_shift
    def strip_shift(self, s):
        """
        Handle supposedly shifted keys.
        
        User settings might specify an already-shifted key, which is not an error.
            
        The legacy Tk binding names have already been translated,
        so we don't have to worry about Shift-ampersand, etc.
        """
        #
        # The second entry in each line handles shifting an already-shifted character.
        # That's ok in user settings: the Shift modifier is just removed.
        shift_d = {
            # Top row of keyboard.
            "`": "~", "~": "~",
            "1": "!", "!": "!",
            "2": "@", "@": "@",
            "3": "#", "#": "#",
            "4": "$", "$": "$",
            "5": "%", "%": "%",
            "6": "^", "^": "^",
            "7": "&", "&": "&",
            "8": "*", "*": "*",
            "9": "(", "(": "(",
            "0": ")", ")": ")",
            "-": "_", "_": "_",
            "=": "+", "+": "+",
            # Second row of keyboard.
            "[": "{", "{": "{",
            "]": "}", "}": "}",
            "\\": '|', "|": "|",
            # Third row of keyboard.
            ";": ":", ":": ":",
            "'": '"', '"': '"',
            # Fourth row of keyboard.
            ".": "<", "<": "<",
            ",": ">", ">": ">",
            "//": "?", "?": "?",
        }
        if 'shift' in self.mods and s in shift_d:
            self.mods.remove('shift')
            s = shift_d.get(s)
        return s
    #@+node:ekr.20120203053243.10124: *4* ks.find, lower & startswith
    # These may go away later, but for now they make conversion of string strokes easier.

    def find(self, pattern):
        return self.s.find(pattern)

    def lower(self):
        return self.s.lower()

    def startswith(self, s):
        return self.s.startswith(s)
    #@+node:ekr.20180415081209.2: *4* ks.find_mods
    def find_mods(self, s):
        """Return the list of all modifiers seen in s."""
        s = s.lower()
        table = (
            ['alt',],
            ['command', 'cmd',],
            ['ctrl', 'control',],  # Use ctrl, not control.
            ['meta',],
            ['shift', 'shft',],
            ['keypad', 'key_pad', 'numpad', 'num_pad'],
                # 868: Allow alternative spellings.
        )
        result = []
        for aList in table:
            kind = aList[0]
            for mod in aList:
                for suffix in '+-':
                    if s.find(mod + suffix) > -1:
                        s = s.replace(mod + suffix, '')
                        result.append(kind)
                        break
        return result
    #@+node:ekr.20180417101435.1: *4* ks.isAltCtl
    def isAltCtrl(self):
        """Return True if this is an Alt-Ctrl character."""
        mods = self.find_mods(self.s)
        return 'alt' in mods and 'ctrl' in mods
    #@+node:ekr.20120203053243.10121: *4* ks.isFKey
    def isFKey(self):
        return self.s in g.app.gui.FKeys
    #@+node:ekr.20180417102341.1: *4* ks.isPlainKey (does not handle alt-ctrl chars)
    def isPlainKey(self):
        """
        Return True if self.s represents a plain key.
        
        A plain key is a key that can be inserted into text.
        
        **Note**: The caller is responsible for handling Alt-Ctrl keys.
        """
        s = self.s
        if s in g.app.gui.ignoreChars:
            # For unit tests.
            return False
        # #868:
        if s.find('Keypad+') > -1:
            # Enable bindings.
            return False
        if self.find_mods(s) or self.isFKey():
            return False
        if s in g.app.gui.specialChars:
            return False
        if s == 'BackSpace':
            return False
        return True
    #@+node:ekr.20180511092713.1: *4* ks.isNumPadKey, ks.isPlainNumPad & ks.removeNumPadModifier
    def isNumPadKey(self):
        return self.s.find('Keypad+') > -1

    def isPlainNumPad(self):
        return (
            self.isNumPadKey() and
            len(self.s.replace('Keypad+', '')) == 1
        )

    def removeNumPadModifier(self):

        self.s = self.s.replace('Keypad+', '')
    #@+node:ekr.20180419170934.1: *4* ks.prettyPrint
    def prettyPrint(self):

        s = self.s
        if not s:
            return '<None>'
        d = {' ': 'Space', '\t': 'Tab', '\n': 'Return', '\r': 'LineFeed'}
        ch = s[-1]
        return s[:-1] + d.get(ch, ch)
    #@+node:ekr.20180415124853.1: *4* ks.strip_mods
    def strip_mods(self, s):
        """Remove all modifiers from s, without changing the case of s."""
        table = (
            'alt',
            'cmd', 'command',
            'control', 'ctrl',
            'keypad', 'key_pad',  # 868:
            'meta',
            'shift', 'shft',
        )
        for mod in table:
            for suffix in '+-':
                target = mod + suffix
                i = s.lower().find(target)
                if i > -1:
                    s = s[:i] + s[i + len(target) :]
                    break
        return s
    #@+node:ekr.20120203053243.10125: *4* ks.toGuiChar
    def toGuiChar(self):
        """Replace special chars by the actual gui char."""
        # pylint: disable=undefined-loop-variable
        # looks like a pylint bug
        s = self.s.lower()
        if s in ('\n', 'return'): s = '\n'
        elif s in ('\t', 'tab'): s = '\t'
        elif s in ('\b', 'backspace'): s = '\b'
        elif s in ('.', 'period'): s = '.'
        return s
    #@+node:ekr.20180417100834.1: *4* ks.toInsertableChar
    def toInsertableChar(self):
        """Convert self to an (insertable) char."""
        # pylint: disable=len-as-condition
        s = self.s
        if not s or self.find_mods(s):
            return ''
        # Handle the "Gang of Four"
        d = {
            'BackSpace': '\b',
            'LineFeed': '\n',
            # 'Insert': '\n',
            'Return': '\n',
            'Tab': '\t',
        }
        if s in d:
            return d.get(s)
        return s if len(s) == 1 else ''
    #@-others

def isStroke(obj):
    return isinstance(obj, KeyStroke)

def isStrokeOrNone(obj):
    return obj is None or isinstance(obj, KeyStroke)
#@+node:ekr.20160119093947.1: *3* class g.MatchBrackets
class MatchBrackets:
    """
    A class implementing the match-brackets command.
    
    In the interest of speed, the code assumes that the user invokes the
    match-bracket command ouside of any string, comment or (for perl or
    javascript) regex.
    """
    #@+others
    #@+node:ekr.20160119104510.1: *4* mb.ctor
    def __init__(self, c, p, language):
        """Ctor for MatchBrackets class."""
        self.c = c
        self.p = p.copy()
        self.language = language
        # Constants.
        self.close_brackets = ")]}>"
        self.open_brackets = "([{<"
        self.brackets = self.open_brackets + self.close_brackets
        self.matching_brackets = self.close_brackets + self.open_brackets
        # Language dependent.
        d1, d2, d3 = g.set_delims_from_language(language)
        self.single_comment, self.start_comment, self.end_comment = d1, d2, d3
        # to track expanding selection
        c.user_dict.setdefault('_match_brackets', {'count': 0, 'range': (0, 0)})
    #@+node:ekr.20160121164723.1: *4* mb.bi-directional helpers
    #@+node:ekr.20160121112812.1: *5* mb.is_regex
    def is_regex(self, s, i):
        """Return true if there is another slash on the line."""
        if self.language in ('javascript', 'perl',):
            assert s[i] == '/'
            offset = 1 if self.forward else -1
            i += offset
            while 0 <= i < len(s) and s[i] != '\n':
                if s[i] == '/':
                    return True
                i += offset
            return False
        return False
    #@+node:ekr.20160121112536.1: *5* mb.scan_regex
    def scan_regex(self, s, i):
        """Scan a regex (or regex substitution for perl)."""
        assert s[i] == '/'
        offset = 1 if self.forward else -1
        i1 = i
        i += offset
        found = False
        while 0 <= i < len(s) and s[i] != '\n':
            ch = s[i]
            i2 = i - 1  # in case we have to look behind.
            i += offset
            if ch == '/':
                # Count the preceding backslashes.
                n = 0
                while 0 <= i2 < len(s) and s[i2] == '\\':
                    n += 1
                    i2 -= 1
                if (n % 2) == 0:
                    if self.language == 'perl' and found is None:
                        found = i
                    else:
                        found = i
                        break
        if found is None:
            self.oops('unmatched regex delim')
            return i1 + offset
        return found
    #@+node:ekr.20160121112303.1: *5* mb.scan_string
    def scan_string(self, s, i):
        """
        Scan the string starting at s[i] (forward or backward).
        Return the index of the next character.
        """
        # i1 = i if self.forward else i + 1
        delim = s[i]
        assert delim in "'\"", repr(delim)
        offset = 1 if self.forward else -1
        i += offset
        while 0 <= i < len(s):
            ch = s[i]
            i2 = i - 1  # in case we have to look behind.
            i += offset
            if ch == delim:
                # Count the preceding backslashes.
                n = 0
                while 0 <= i2 < len(s) and s[i2] == '\\':
                    n += 1
                    i2 -= 1
                if (n % 2) == 0:
                    return i
        # Annoying when matching brackets on the fly.
            # self.oops('unmatched string')
        return i + offset
    #@+node:tbrown.20180226113621.1: *4* mb.expand_range
    def expand_range(self, s, left, right, max_right, expand=False):
        """
        Find the bracket nearest the cursor searching outwards left and right.

        Expand the range (left, right) in string s until either s[left] or
        s[right] is a bracket.  right can not exceed max_right, and if expand is
        True, the new range must encompass the old range, in addition to s[left]
        or s[right] being a bracket.

        Returns
            new_left, new_right, bracket_char, index_of_bracket_char
        if expansion succeeds, otherwise
            None, None, None, None

        Note that only one of new_left and new_right will necessarily be a
        bracket, but index_of_bracket_char will definitely be a bracket.
        """
        expanded = False
        orig_left = left
        orig_right = right
        while (
            (s[left] not in self.brackets or expand and not expanded)
            and (s[right] not in self.brackets or expand and not expanded)
            and (left > 0 or right < max_right)
        ):
            expanded = False
            if left > 0:
                left -= 1
                if s[left] in self.brackets:
                    other = self.find_matching_bracket(s[left], s, left)
                    if other is not None and other >= orig_right:
                        expanded = 'left'
            if right < max_right:
                right += 1
                if s[right] in self.brackets:
                    other = self.find_matching_bracket(s[right], s, right)
                    if other is not None and other <= orig_left:
                        expanded = 'right'
        if s[left] in self.brackets and (not expand or expanded == 'left'):
            return left, right, s[left], left
        if s[right] in self.brackets and (not expand or expanded == 'right'):
            return left, right, s[right], right
        return None, None, None, None
    #@+node:ekr.20061113221414: *4* mb.find_matching_bracket
    def find_matching_bracket(self, ch1, s, i):
        """Find the bracket matching s[i] for self.language."""
        self.forward = ch1 in self.open_brackets
        # Find the character matching the initial bracket.
        for n in range(len(self.brackets)):
            if ch1 == self.brackets[n]:
                target = self.matching_brackets[n]
                break
        else:
            return None
        f = self.scan if self.forward else self.scan_back
        return f(ch1, target, s, i)
    #@+node:ekr.20160121164556.1: *4* mb.scan & helpers
    def scan(self, ch1, target, s, i):
        """Scan forward for target."""
        level = 0
        while 0 <= i < len(s):
            progress = i
            ch = s[i]
            if ch in '"\'':
                # Scan to the end/beginning of the string.
                i = self.scan_string(s, i)
            elif self.starts_comment(s, i):
                i = self.scan_comment(s, i)
            elif ch == '/' and self.is_regex(s, i):
                i = self.scan_regex(s, i)
            elif ch == ch1:
                level += 1
                i += 1
            elif ch == target:
                level -= 1
                if level <= 0:
                    return i
                i += 1
            else:
                i += 1
            assert i > progress
        # Not found
        return None
    #@+node:ekr.20160119090634.1: *5* mb.scan_comment
    def scan_comment(self, s, i):
        """Return the index of the character after a comment."""
        i1 = i
        start = self.start_comment if self.forward else self.end_comment
        end = self.end_comment if self.forward else self.start_comment
        offset = 1 if self.forward else -1
        if g.match(s, i, start):
            if not self.forward:
                i1 += len(end)
            i += offset
            while 0 <= i < len(s):
                if g.match(s, i, end):
                    i = i + len(end) if self.forward else i - 1
                    return i
                i += offset
            self.oops('unmatched multiline comment')
        elif self.forward:
            # Scan to the newline.
            target = '\n'
            while 0 <= i < len(s):
                if s[i] == '\n':
                    i += 1
                    return i
                i += 1
        else:
            # Careful: scan to the *first* target on the line
            target = self.single_comment
            found = None
            i -= 1
            while 0 <= i < len(s) and s[i] != '\n':
                if g.match(s, i, target):
                    found = i
                i -= 1
            if found is None:
                self.oops('can not happen: unterminated single-line comment')
                found = 0
            return found
        return i
    #@+node:ekr.20160119101851.1: *5* mb.starts_comment
    def starts_comment(self, s, i):
        """Return True if s[i] starts a comment."""
        assert 0 <= i < len(s)
        if self.forward:
            if self.single_comment and g.match(s, i, self.single_comment):
                return True
            return (
                self.start_comment and self.end_comment and
                g.match(s, i, self.start_comment)
            )
        if s[i] == '\n':
            if self.single_comment:
                # Scan backward for any single-comment delim.
                i -= 1
                while i >= 0 and s[i] != '\n':
                    if g.match(s, i, self.single_comment):
                        return True
                    i -= 1
            return False
        return (
            self.start_comment and self.end_comment and
            g.match(s, i, self.end_comment)
        )
    #@+node:ekr.20160119230141.1: *4* mb.scan_back & helpers
    def scan_back(self, ch1, target, s, i):
        """Scan backwards for delim."""
        level = 0
        while i >= 0:
            progress = i
            ch = s[i]
            if self.ends_comment(s, i):
                i = self.back_scan_comment(s, i)
            elif ch in '"\'':
                # Scan to the beginning of the string.
                i = self.scan_string(s, i)
            elif ch == '/' and self.is_regex(s, i):
                i = self.scan_regex(s, i)
            elif ch == ch1:
                level += 1
                i -= 1
            elif ch == target:
                level -= 1
                if level <= 0:
                    return i
                i -= 1
            else:
                i -= 1
            assert i < progress
        # Not found
        return None
    #@+node:ekr.20160119230141.2: *5* mb.back_scan_comment
    def back_scan_comment(self, s, i):
        """Return the index of the character after a comment."""
        i1 = i
        if g.match(s, i, self.end_comment):
            i1 += len(self.end_comment)  # For traces.
            i -= 1
            while i >= 0:
                if g.match(s, i, self.start_comment):
                    i -= 1
                    return i
                i -= 1
            self.oops('unmatched multiline comment')
            return i
        # Careful: scan to the *first* target on the line
        found = None
        i -= 1
        while i >= 0 and s[i] != '\n':
            if g.match(s, i, self.single_comment):
                found = i - 1
            i -= 1
        if found is None:
            self.oops('can not happen: unterminated single-line comment')
            found = 0
        return found
    #@+node:ekr.20160119230141.4: *5* mb.ends_comment
    def ends_comment(self, s, i):
        """
        Return True if s[i] ends a comment. This is called while scanning
        backward, so this is a bit of a guess.
        """
        if s[i] == '\n':
            # This is the hard (dubious) case.
            # Let w, x, y and z stand for any strings not containg // or quotes.
            # Case 1: w"x//y"z Assume // is inside a string.
            # Case 2: x//y"z Assume " is inside the comment.
            # Case 3: w//x"y"z Assume both quotes are inside the comment.
            #
            # That is, we assume (perhaps wrongly) that a quote terminates a
            # string if and *only* if the string starts *and* ends on the line.
            if self.single_comment:
                # Scan backward for single-line comment delims or quotes.
                quote = None
                i -= 1
                while i >= 0 and s[i] != '\n':
                    progress = i
                    if quote and s[i] == quote:
                        quote = None
                        i -= 1
                    elif s[i] in '"\'':
                        if not quote:
                            quote = s[i]
                        i -= 1
                    elif g.match(s, i, self.single_comment):
                        # Assume that there is a comment only if the comment delim
                        # isn't inside a string that begins and ends on *this* line.
                        if quote:
                            while i >= 0 and s[i] != 'n':
                                if s[i] == quote:
                                    return False
                                i -= 1
                        return True
                    else:
                        i -= 1
                    assert progress > i
            return False
        return (
            self.start_comment and
            self.end_comment and
            g.match(s, i, self.end_comment))
    #@+node:ekr.20160119104148.1: *4* mb.oops
    def oops(self, s):
        """Report an error in the match-brackets command."""
        g.es(s, color='red')
    #@+node:ekr.20160119094053.1: *4* mb.run
    #@@nobeautify

    def run(self):
        """The driver for the MatchBrackets class.

        With no selected range: find the nearest bracket and select from
        it to it's match, moving cursor to mathc.
        
        With selected range: the first time, move cursor back to other end of
        range. The second time, select enclosing range.
        """
        #
        # A partial fix for bug 127: Bracket matching is buggy.
        w = self.c.frame.body.wrapper
        s = w.getAllText()
        _mb = self.c.user_dict['_match_brackets']
        sel_range = w.getSelectionRange()
        if not w.hasSelection():
            _mb['count'] = 1
        if _mb['range'] == sel_range and _mb['count'] == 1:
            # haven't been to other end yet
            _mb['count'] += 1
            # move insert point to other end of selection
            insert = 1 if w.getInsertPoint() == sel_range[0] else 0
            w.setSelectionRange(
                sel_range[0], sel_range[1], insert=sel_range[insert])
            return

        # Find the bracket nearest the cursor.
        max_right = len(s) - 1 # insert point can be past last char.
        left = right = min(max_right, w.getInsertPoint())
        left, right, ch, index = self.expand_range(s, left, right, max_right)
        if left is None:
            g.es("Bracket not found")
            return
        index2 = self.find_matching_bracket(ch, s, index)
        if index2 is None:
            g.es("No matching bracket.")  # #1447.
            return

        # If this is the first time we've selected the range index-index2, do
        # nothing extra.  The second time, move cursor to other end (requires
        # no special action here), and the third time, try to expand the range
        # to any enclosing brackets
        minmax = (min(index, index2), max(index, index2)+1)
        # the range, +1 to match w.getSelectionRange()
        if _mb['range'] == minmax:  # count how many times this has been the answer
            _mb['count'] += 1
        else:
            _mb['count'] = 1
            _mb['range'] = minmax
        if _mb['count'] >= 3:  # try to expand range
            left, right, ch, index3 = self.expand_range(
                s,
                max(minmax[0], 0),
                min(minmax[1], max_right),
                max_right, expand=True
            )
            if index3 is not None:  # found nearest bracket outside range
                index4 = self.find_matching_bracket(ch, s, index3)
                if index4 is not None:  # found matching bracket, expand range
                    index, index2 = index3, index4
                    _mb['count'] = 1
                    _mb['range'] = (min(index3, index4), max(index3, index4)+1)

        if index2 is not None:
            if index2 < index:
                w.setSelectionRange(index2, index + 1, insert=index2)
            else:
                w.setSelectionRange(
                    index, index2 + 1, insert=min(len(s), index2 + 1))
            w.see(index2)
        else:
            g.es("unmatched", repr(ch))
    #@-others
#@+node:ekr.20090128083459.82: *3* class g.PosList (deprecated)
class PosList(list):
    #@+<< docstring for PosList >>
    #@+node:ekr.20090130114732.2: *4* << docstring for PosList >>
    """A subclass of list for creating and selecting lists of positions.

        This is deprecated, use leoNodes.PosList instead!

        aList = g.PosList(c)
            # Creates a PosList containing all positions in c.

        aList = g.PosList(c,aList2)
            # Creates a PosList from aList2.

        aList2 = aList.select(pattern,regex=False,removeClones=True)
            # Creates a PosList containing all positions p in aList
            # such that p.h matches the pattern.
            # The pattern is a regular expression if regex is True.
            # if removeClones is True, all positions p2 are removed
            # if a position p is already in the list and p2.v == p.v.

        aList.dump(sort=False,verbose=False)
            # Prints all positions in aList, sorted if sort is True.
            # Prints p.h, or repr(p) if verbose is True.
    """
    #@-<< docstring for PosList >>
    #@+others
    #@+node:ekr.20140531104908.17611: *4* PosList.ctor
    def __init__(self, c, aList=None):
        self.c = c
        super().__init__()
        if aList is None:
            for p in c.all_positions():
                self.append(p.copy())
        else:
            for p in aList:
                self.append(p.copy())
    #@+node:ekr.20140531104908.17612: *4* PosList.dump
    def dump(self, sort=False, verbose=False):
        if verbose:
            return g.listToString(self, sort=sort)
        return g.listToString([p.h for p in self], sort=sort)
    #@+node:ekr.20140531104908.17613: *4* PosList.select
    def select(self, pat, regex=False, removeClones=True):
        """
        Return a new PosList containing all positions
        in self that match the given pattern.
        """
        c = self.c; aList = []
        if regex:
            for p in self:
                if re.match(pat, p.h):
                    aList.append(p.copy())
        else:
            for p in self:
                if p.h.find(pat) != -1:
                    aList.append(p.copy())
        if removeClones:
            aList = self.removeClones(aList)
        return PosList(c, aList)
    #@+node:ekr.20140531104908.17614: *4* PosList.removeClones
    def removeClones(self, aList):
        seen = {}; aList2 = []
        for p in aList:
            if p.v not in seen:
                seen[p.v] = p.v
                aList2.append(p)
        return aList2
    #@-others
#@+node:EKR.20040612114220.4: *3* class g.ReadLinesClass
class ReadLinesClass:
    """A class whose next method provides a readline method for Python's tokenize module."""

    def __init__(self, s):
        self.lines = g.splitLines(s)
        self.i = 0

    def next(self):
        if self.i < len(self.lines):
            line = self.lines[self.i]
            self.i += 1
        else:
            line = ''
        return line

    __next__ = next
#@+node:ekr.20031218072017.3121: *3* class g.RedirectClass & convenience functions
class RedirectClass:
    """A class to redirect stdout and stderr to Leo's log pane."""
    #@+<< RedirectClass methods >>
    #@+node:ekr.20031218072017.1656: *4* << RedirectClass methods >>
    #@+others
    #@+node:ekr.20041012082437: *5* RedirectClass.__init__
    def __init__(self):
        self.old = None
        self.encoding = 'utf-8'  # 2019/03/29 For pdb.
    #@+node:ekr.20041012082437.1: *5* isRedirected
    def isRedirected(self):
        return self.old is not None
    #@+node:ekr.20041012082437.2: *5* flush
    # For LeoN: just for compatibility.

    def flush(self, *args):
        return
    #@+node:ekr.20041012091252: *5* rawPrint
    def rawPrint(self, s):
        if self.old:
            self.old.write(s + '\n')
        else:
            g.pr(s)
    #@+node:ekr.20041012082437.3: *5* redirect
    def redirect(self, stdout=1):
        if g.app.batchMode:
            # Redirection is futile in batch mode.
            return
        if not self.old:
            if stdout:
                self.old, sys.stdout = sys.stdout, self
            else:
                self.old, sys.stderr = sys.stderr, self
    #@+node:ekr.20041012082437.4: *5* undirect
    def undirect(self, stdout=1):
        if self.old:
            if stdout:
                sys.stdout, self.old = self.old, None
            else:
                sys.stderr, self.old = self.old, None
    #@+node:ekr.20041012082437.5: *5* write
    def write(self, s):

        if self.old:
            if app.log:
                app.log.put(s, from_redirect=True)
            else:
                self.old.write(s + '\n')
        else:
            # Can happen when g.batchMode is True.
            g.pr(s)
    #@-others
    #@-<< RedirectClass methods >>

# Create two redirection objects, one for each stream.

redirectStdErrObj = RedirectClass()
redirectStdOutObj = RedirectClass()
#@+<< define convenience methods for redirecting streams >>
#@+node:ekr.20031218072017.3122: *4* << define convenience methods for redirecting streams >>
#@+others
#@+node:ekr.20041012090942: *5* redirectStderr & redirectStdout
# Redirect streams to the current log window.

def redirectStderr():
    global redirectStdErrObj
    redirectStdErrObj.redirect(stdout=False)

def redirectStdout():
    global redirectStdOutObj
    redirectStdOutObj.redirect()
#@+node:ekr.20041012090942.1: *5* restoreStderr & restoreStdout
# Restore standard streams.

def restoreStderr():
    global redirectStdErrObj
    redirectStdErrObj.undirect(stdout=False)

def restoreStdout():
    global redirectStdOutObj
    redirectStdOutObj.undirect()
#@+node:ekr.20041012090942.2: *5* stdErrIsRedirected & stdOutIsRedirected
def stdErrIsRedirected():
    global redirectStdErrObj
    return redirectStdErrObj.isRedirected()

def stdOutIsRedirected():
    global redirectStdOutObj
    return redirectStdOutObj.isRedirected()
#@+node:ekr.20041012090942.3: *5* rawPrint
# Send output to original stdout.

def rawPrint(s):
    global redirectStdOutObj
    redirectStdOutObj.rawPrint(s)
#@-others
#@-<< define convenience methods for redirecting streams >>
#@+node:ekr.20121128031949.12605: *3* class g.SherlockTracer
class SherlockTracer:
    """
    A stand-alone tracer class with many of Sherlock's features.

    This class should work in any environment containing the re, os and sys modules.

    The arguments in the pattern lists determine which functions get traced
    or which stats get printed. Each pattern starts with "+", "-", "+:" or
    "-:", followed by a regular expression::

    "+x"  Enables tracing (or stats) for all functions/methods whose name
          matches the regular expression x.
    "-x"  Disables tracing for functions/methods.
    "+:x" Enables tracing for all functions in the **file** whose name matches x.
    "-:x" Disables tracing for an entire file.

    Enabling and disabling depends on the order of arguments in the pattern
    list. Consider the arguments for the Rope trace::

    patterns=['+.*','+:.*',
        '-:.*\\lib\\.*','+:.*rope.*','-:.*leoGlobals.py',
        '-:.*worder.py','-:.*prefs.py','-:.*resources.py',])

    This enables tracing for everything, then disables tracing for all
    library modules, except for all rope modules. Finally, it disables the
    tracing for Rope's worder, prefs and resources modules. Btw, this is
    one of the best uses for regular expressions that I know of.

    Being able to zero in on the code of interest can be a big help in
    studying other people's code. This is a non-invasive method: no tracing
    code needs to be inserted anywhere.
    
    Usage:
        
    g.SherlockTracer(patterns).run()
    """
    # Transcrypt does not support Python's os module.
    # __pragma__ ('skip')

    #@+others
    #@+node:ekr.20121128031949.12602: *4* __init__
    def __init__(
        self,
        patterns,
        dots=True,
        show_args=True,
        show_return=True,
        verbose=True,
    ):
        """SherlockTracer ctor."""
        self.bad_patterns = []  # List of bad patterns.
        self.dots = dots  # True: print level dots.
        self.contents_d = {}  # Keys are file names, values are file lines.
        self.n = 0  # The frame level on entry to run.
        self.stats = {}  # Keys are full file names, values are dicts.
        self.patterns = None  # A list of regex patterns to match.
        self.pattern_stack = []
        self.show_args = show_args  # True: show args for each function call.
        self.show_return = show_return  # True: show returns from each function.
        self.trace_lines = True  # True: trace lines in enabled functions.
        self.verbose = verbose  # True: print filename:func
        self.set_patterns(patterns)
        from leo.core.leoQt import QtCore
        if QtCore:
            # pylint: disable=no-member
            QtCore.pyqtRemoveInputHook()
    #@+node:ekr.20140326100337.16844: *4* __call__
    def __call__(self, frame, event, arg):
        """Exists so that self.dispatch can return self."""
        return self.dispatch(frame, event, arg)
    #@+node:ekr.20140326100337.16846: *4* sherlock.bad_pattern
    def bad_pattern(self, pattern):
        """Report a bad Sherlock pattern."""
        if pattern not in self.bad_patterns:
            self.bad_patterns.append(pattern)
            print(f"\nignoring bad pattern: {pattern}\n")
    #@+node:ekr.20140326100337.16847: *4* sherlock.check_pattern
    def check_pattern(self, pattern):
        """Give an error and return False for an invalid pattern."""
        try:
            for prefix in ('+:', '-:', '+', '-'):
                if pattern.startswith(prefix):
                    re.match(pattern[len(prefix) :], 'xyzzy')
                    return True
            self.bad_pattern(pattern)
            return False
        except Exception:
            self.bad_pattern(pattern)
            return False
    #@+node:ekr.20121128031949.12609: *4* sherlock.dispatch
    def dispatch(self, frame, event, arg):
        """The dispatch method."""
        if event == 'call':
            self.do_call(frame, arg)
        elif event == 'return' and self.show_return:
            self.do_return(frame, arg)
        elif True and event == 'line' and self.trace_lines:
            self.do_line(frame, arg)
        # Queue the SherlockTracer instance again.
        return self
    #@+node:ekr.20121128031949.12603: *4* sherlock.do_call & helper
    def do_call(self, frame, unused_arg):
        """Trace through a function call."""
        frame1 = frame
        code = frame.f_code
        file_name = code.co_filename
        locals_ = frame.f_locals
        function_name = code.co_name
        try:
            full_name = self.get_full_name(locals_, function_name)
        except Exception:
            full_name = function_name
        if not self.is_enabled(file_name, full_name, self.patterns):
            # 2020/09/09: Don't touch, for example, __ methods.
            return
        n = 0  # The number of callers of this def.
        while frame:
            frame = frame.f_back
            n += 1
        dots = '.' * max(0, n - self.n) if self.dots else ''
        path = f"{os.path.basename(file_name):>20}" if self.verbose else ''
        leadin = '+' if self.show_return else ''
        args = f"(%s)" % self.get_args(frame1) if self.show_args else ''
        print(f"{path}:{dots}{leadin}{full_name}{args}")
        # Always update stats.
        d = self.stats.get(file_name, {})
        d[full_name] = 1 + d.get(full_name, 0)
        self.stats[file_name] = d
    #@+node:ekr.20130111185820.10194: *5* sherlock.get_args
    def get_args(self, frame):
        """Return name=val for each arg in the function call."""
        code = frame.f_code
        locals_ = frame.f_locals
        name = code.co_name
        n = code.co_argcount
        if code.co_flags & 4: n = n + 1
        if code.co_flags & 8: n = n + 1
        result = []
        for i in range(n):
            name = code.co_varnames[i]
            if name != 'self':
                arg = locals_.get(name, '*undefined*')
                if arg:
                    if isinstance(arg, (list, tuple)):
                        # Clearer w/o f-string
                        val = f"[%s]" % ','.join(
                            [self.show(z) for z in arg if self.show(z)])
                    else:
                        val = self.show(arg)
                    if val:
                        result.append(f"{name}={val}")
        return ','.join(result)
    #@+node:ekr.20140402060647.16845: *4* sherlock.do_line (not used)
    bad_fns = []

    def do_line(self, frame, arg):
        """print each line of enabled functions."""
        if 1:
            return
        code = frame.f_code
        file_name = code.co_filename
        locals_ = frame.f_locals
        name = code.co_name
        full_name = self.get_full_name(locals_, name)
        if not self.is_enabled(file_name, full_name, self.patterns):
            return
        n = frame.f_lineno - 1  # Apparently, the first line is line 1.
        d = self.contents_d
        lines = d.get(file_name)
        if not lines:
            print(file_name)
            try:
                with open(file_name) as f:
                    s = f.read()
            except Exception:
                if file_name not in self.bad_fns:
                    self.bad_fns.append(file_name)
                    print(f"open({file_name}) failed")
                return
            lines = g.splitLines(s)
            d[file_name] = lines
        line = lines[n].rstrip() if n < len(lines) else '<EOF>'
        if 0:
            print(f"{name:3} {line}")
        else:
            print(f"{g.shortFileName(file_name)} {n} {full_name} {line}")
    #@+node:ekr.20130109154743.10172: *4* sherlock.do_return & helper
    def do_return(self, frame, arg):  # Arg *is* used below.
        """Trace a return statement."""
        code = frame.f_code
        fn = code.co_filename
        locals_ = frame.f_locals
        name = code.co_name
        full_name = self.get_full_name(locals_, name)
        if self.is_enabled(fn, full_name, self.patterns):
            n = 0
            while frame:
                frame = frame.f_back
                n += 1
            dots = '.' * max(0, n - self.n) if self.dots else ''
            path = f"{os.path.basename(fn):>20}" if self.verbose else ''
            if name and name == '__init__':
                try:
                    ret1 = locals_ and locals_.get('self', None)
                    ret = self.format_ret(ret1)
                except NameError:
                    ret = f"<{ret1.__class__.__name__}>"
            else:
                ret = self.format_ret(arg)
            print(f"{path}{dots}-{full_name}{ret}")
    #@+node:ekr.20130111120935.10192: *5* sherlock.format_ret
    def format_ret(self, arg):
        """Format arg, the value returned by a "return" statement."""
        try:
            if isinstance(arg, types.GeneratorType):
                ret = '<generator>'
            elif isinstance(arg, (tuple, list)):
                # Clearer w/o f-string.
                ret = f"[%s]" % ','.join([self.show(z) for z in arg])
                if len(ret) > 40:
                    # Clearer w/o f-string.
                    ret = f"[\n%s]" % ('\n,'.join([self.show(z) for z in arg]))
            elif arg:
                ret = self.show(arg)
                if len(ret) > 40:
                    ret = f"\n    {ret}"
            else:
                ret = '' if arg is None else repr(arg)
        except Exception:
            exctype, value = sys.exc_info()[:2]
            s = f"<**exception: {exctype.__name__}, {value} arg: {arg !r}**>"
            # Clearer w/o f-string.
            ret = f" ->\n    %s" % s if len(s) > 40 else f" -> {s}"
        return f" -> {ret}"
    #@+node:ekr.20121128111829.12185: *4* sherlock.fn_is_enabled (not used)
    def fn_is_enabled(self, func, patterns):
        """Return True if tracing for the given function is enabled."""
        if func in self.ignored_functions:
            return False
            
        def ignore_function():
            if func not in self.ignored_functions:
                self.ignored_functions.append(func)
                print(f"Ignore function: {func}")
        #
        # New in Leo 6.3. Never trace dangerous functions.
        table = (
            '_deepcopy.*',
            # Unicode primitives.
            'encode\b', 'decode\b',
            # System functions
            '.*__next\b',
            '<frozen>', '<genexpr>', '<listcomp>',
            # '<decorator-gen-.*>',
            'get\b', 
            # String primitives.
            'append\b', 'split\b', 'join\b', 
            # File primitives...
            'access_check\b', 'expanduser\b', 'exists\b', 'find_spec\b',
            'abspath\b', 'normcase\b', 'normpath\b', 'splitdrive\b',
        )
        g.trace('=====', func)
        for z in table:
            if re.match(z, func):
                ignore_function()
                return False
        #
        # Legacy code.  
        try:
            enabled, pattern = False, None
            for pattern in patterns:
                if pattern.startswith('+:'):
                    if re.match(pattern[2:], func):
                        enabled = True
                elif pattern.startswith('-:'):
                    if re.match(pattern[2:], func):
                        enabled = False
            return enabled
        except Exception:
            self.bad_pattern(pattern)
            return False
    #@+node:ekr.20130112093655.10195: *4* get_full_name
    def get_full_name(self, locals_, name):
        """Return class_name::name if possible."""
        full_name = name
        try:
            user_self = locals_ and locals_.get('self', None)
            if user_self:
                full_name = user_self.__class__.__name__ + '::' + name
        except Exception:
            pass
        return full_name
    #@+node:ekr.20121128111829.12183: *4* sherlock.is_enabled
    ignored_files = []
    ignored_functions = []

    def is_enabled(self, file_name, function_name, patterns=None):
        """Return True if tracing for function_name in the given file is enabled."""
        #
        # New in Leo 6.3. Never trace through some files.
        if not os:
            return False  # Shutting down.
        base_name = os.path.basename(file_name)
        if base_name in self.ignored_files:
            return False

        def ignore_file():
            if not base_name in self.ignored_files:
                self.ignored_files.append(base_name)
                # print(f"Ignore file: {base_name}")
                
        def ignore_function():
            if function_name not in self.ignored_functions:
                self.ignored_functions.append(function_name)
                # print(f"Ignore function: {function_name}")
                
        if f"{os.sep}lib{os.sep}" in file_name:
            ignore_file()
            return False
        if base_name.startswith('<') and base_name.endswith('>'):
            ignore_file()
            return False
        #
        # New in Leo 6.3. Never trace dangerous functions.
        table = (
            '_deepcopy.*',
            # Unicode primitives.
            'encode\b', 'decode\b',
            # System functions
            '.*__next\b',
            '<frozen>', '<genexpr>', '<listcomp>',
            # '<decorator-gen-.*>',
            'get\b', 
            # String primitives.
            'append\b', 'split\b', 'join\b', 
            # File primitives...
            'access_check\b', 'expanduser\b', 'exists\b', 'find_spec\b',
            'abspath\b', 'normcase\b', 'normpath\b', 'splitdrive\b',
        )
        for z in table:
            if re.match(z, function_name):
                ignore_function()
                return False
        #
        # Legacy code.
        enabled = False
        if patterns is None: patterns = self.patterns
        for pattern in patterns:
            try:
                if pattern.startswith('+:'):
                    if re.match(pattern[2:], file_name):
                        enabled = True
                elif pattern.startswith('-:'):
                    if re.match(pattern[2:], file_name):
                        enabled = False
                elif pattern.startswith('+'):
                    if re.match(pattern[1:], function_name):
                        enabled = True
                elif pattern.startswith('-'):
                    if re.match(pattern[1:], function_name):
                        enabled = False
                else:
                    self.bad_pattern(pattern)
            except Exception:
                self.bad_pattern(pattern)
        return enabled
    #@+node:ekr.20121128111829.12182: *4* print_stats
    def print_stats(self, patterns=None):
        """Print all accumulated statisitics."""
        print('\nSherlock statistics...')
        if not patterns: patterns = ['+.*', '+:.*',]
        for fn in sorted(self.stats.keys()):
            d = self.stats.get(fn)
            if self.fn_is_enabled(fn, patterns):
                result = sorted(d.keys())
            else:
                result = [key for key in sorted(d.keys())
                    if self.is_enabled(fn, key, patterns)]
            if result:
                print('')
                fn = fn.replace('\\', '/')
                parts = fn.split('/')
                print('/'.join(parts[-2:]))
                for key in result:
                    print(f"{d.get(key):4} {key}")
    #@+node:ekr.20121128031949.12614: *4* run
    # Modified from pdb.Pdb.set_trace.

    def run(self, frame=None):
        """Trace from the given frame or the caller's frame."""
        print(f"SherlockTracer.run:patterns:\n%s" % '\n'.join(self.patterns))
        if frame is None:
            frame = sys._getframe().f_back
        # Compute self.n, the number of frames to ignore.
        self.n = 0
        while frame:
            frame = frame.f_back
            self.n += 1
        # Pass self to sys.settrace to give easy access to all methods.
        sys.settrace(self)
    #@+node:ekr.20140322090829.16834: *4* push & pop
    def push(self, patterns):
        """Push the old patterns and set the new."""
        self.pattern_stack.append(self.patterns)
        self.set_patterns(patterns)
        print(f"SherlockTracer.push: {self.patterns}")

    def pop(self):
        """Restore the pushed patterns."""
        if self.pattern_stack:
            self.patterns = self.pattern_stack.pop()
            print(f"SherlockTracer.pop: {self.patterns}")
        else:
            print('SherlockTracer.pop: pattern stack underflow')
    #@+node:ekr.20140326100337.16845: *4* set_patterns
    def set_patterns(self, patterns):
        """Set the patterns in effect."""
        self.patterns = [z for z in patterns if self.check_pattern(z)]
    #@+node:ekr.20140322090829.16831: *4* show
    def show(self, item):
        """return the best representation of item."""
        if not item:
            return repr(item)
        if isinstance(item, dict):
            return 'dict'
        if isinstance(item, str):
            s = repr(item)
            if len(s) <= 20:
                return s
            return s[:17] + '...'
        return repr(item)
    #@+node:ekr.20121128093229.12616: *4* stop
    def stop(self):
        """Stop all tracing."""
        sys.settrace(None)
    #@-others

    # __pragma__ ('noskip')
#@+node:ekr.20191013145307.1: *3* class g.TkIDDialog (EmergencyDialog)
class TkIDDialog(EmergencyDialog):
    """A class that creates an tkinter dialog to get the Leo ID."""

    message = (
        "leoID.txt not found\n\n"
        "Please enter an id that identifies you uniquely.\n"
        "Your git/cvs/bzr login name is a good choice.\n\n"
        "Leo uses this id to uniquely identify nodes.\n\n"
        "Your id should contain only letters and numbers\n"
        "and must be at least 3 characters in length.")

    title = 'Enter Leo id'

    def __init__(self):
        super().__init__(self.title, self.message)
        self.val = ''
        
    # Transcrypt does not support Python's tkinter module.
    # __pragma__ ('skip')

    #@+others
    #@+node:ekr.20191013145710.1: *4* leo_id_dialog.onKey
    def onKey(self, event):
        """Handle Key events in askOk dialogs."""
        if event.char in '\n\r':
            self.okButton()
    #@+node:ekr.20191013145757.1: *4* leo_id_dialog.createTopFrame
    def createTopFrame(self):
        """Create the Tk.Toplevel widget for a leoTkinterDialog."""
        import tkinter as Tk
        self.root = Tk.Tk()
        self.top = Tk.Toplevel(self.root)
        self.top.title(self.title)
        self.root.withdraw()
        self.frame = Tk.Frame(self.top)
        self.frame.pack(side="top", expand=1, fill="both")
        label = Tk.Label(self.frame, text=self.message, bg='white')
        label.pack(pady=10)
        self.entry = Tk.Entry(self.frame)
        self.entry.pack()
        self.entry.focus_set()
    #@+node:ekr.20191013150158.1: *4* leo_id_dialog.okButton
    def okButton(self):
        """Do default click action in ok button."""
        self.val = self.entry.get()
            # Return is not possible.
        self.top.destroy()
        self.top = None
    #@-others

    # __pragma__ ('noskip')
#@+node:ekr.20080531075119.1: *3* class g.Tracer
class Tracer:
    """A "debugger" that computes a call graph.

    To trace a function and its callers, put the following at the function's start:

    g.startTracer()
    """
    #@+others
    #@+node:ekr.20080531075119.2: *4*  __init__ (Tracer)
    def __init__(self, limit=0, trace=False, verbose=False):
        self.callDict = {}
            # Keys are function names.
            # Values are the number of times the function was called by the caller.
        self.calledDict = {}
            # Keys are function names.
            # Values are the total number of times the function was called.
        self.count = 0
        self.inited = False
        self.limit = limit  # 0: no limit, otherwise, limit trace to n entries deep.
        self.stack = []
        self.trace = trace
        self.verbose = verbose  # True: print returns as well as calls.
    #@+node:ekr.20080531075119.3: *4* computeName
    def computeName(self, frame):
        if not frame: return ''
        code = frame.f_code; result = []
        module = inspect.getmodule(code)
        if module:
            module_name = module.__name__
            if module_name == 'leo.core.leoGlobals':
                result.append('g')
            else:
                tag = 'leo.core.'
                if module_name.startswith(tag):
                    module_name = module_name[len(tag) :]
                result.append(module_name)
        try:
            # This can fail during startup.
            self_obj = frame.f_locals.get('self')
            if self_obj: result.append(self_obj.__class__.__name__)
        except Exception:
            pass
        result.append(code.co_name)
        return '.'.join(result)
    #@+node:ekr.20080531075119.4: *4* report
    def report(self):
        if 0:
            g.pr('\nstack')
            for z in self.stack:
                g.pr(z)
        g.pr('\ncallDict...')
        for key in sorted(self.callDict):
            # Print the calling function.
            g.pr(f"{self.calledDict.get(key,0):d}", key)
            # Print the called functions.
            d = self.callDict.get(key)
            for key2 in sorted(d):
                g.pr(f"{d.get(key2):8d}", key2)
    #@+node:ekr.20080531075119.5: *4* stop
    def stop(self):
        sys.settrace(None)
        self.report()
    #@+node:ekr.20080531075119.6: *4* tracer
    def tracer(self, frame, event, arg):
        """A function to be passed to sys.settrace."""
        n = len(self.stack)
        if event == 'return':
            n = max(0, n - 1)
        pad = '.' * n
        if event == 'call':
            if not self.inited:
                # Add an extra stack element for the routine containing the call to startTracer.
                self.inited = True
                name = self.computeName(frame.f_back)
                self.updateStats(name)
                self.stack.append(name)
            name = self.computeName(frame)
            if self.trace and (self.limit == 0 or len(self.stack) < self.limit):
                g.trace(f"{pad}call", name)
            self.updateStats(name)
            self.stack.append(name)
            return self.tracer
        if event == 'return':
            if self.stack:
                name = self.stack.pop()
                if (
                    self.trace and
                    self.verbose and
                    (self.limit == 0 or len(self.stack) < self.limit)
                ):
                    g.trace(f"{pad}ret ", name)
            else:
                g.trace('return underflow')
                self.stop()
                return None
            if self.stack:
                return self.tracer
            self.stop()
            return None
        return self.tracer
    #@+node:ekr.20080531075119.7: *4* updateStats
    def updateStats(self, name):
        if not self.stack:
            return
        caller = self.stack[-1]
        d = self.callDict.get(caller, {})
            # d is a dict reprenting the called functions.
            # Keys are called functions, values are counts.
        d[name] = 1 + d.get(name, 0)
        self.callDict[caller] = d
        # Update the total counts.
        self.calledDict[name] = 1 + self.calledDict.get(name, 0)
    #@-others

def startTracer(limit=0, trace=False, verbose=False):
    t = g.Tracer(limit=limit, trace=trace, verbose=verbose)
    sys.settrace(t.tracer)
    return t
#@+node:ekr.20031219074948.1: *3* class g.Tracing/NullObject & helpers
#@@nobeautify

tracing_tags = {}
    # Keys are id's, values are tags.
tracing_vars = {}
    # Keys are id's, values are names of ivars.
tracing_signatures = {}
    # Keys are signatures: '%s.%s:%s' % (tag, attr, callers). Values not important.

class NullObject:
    """An object that does nothing, and does it very well."""
    def __init__(self, ivars=None, *args, **kwargs):
        if isinstance(ivars, str):
            ivars = [ivars]
        tracing_vars [id(self)] = ivars or []
    def __call__(self, *args, **keys): return self
    def __repr__(self): return "NullObject"
    def __str__(self): return "NullObject"
    # Attribute access...
    def __delattr__(self, attr): return None
    def __getattr__(self, attr):
        if attr in tracing_vars.get(id(self), []):
            return getattr(self, attr, None)
        return self # Required.
    def __setattr__(self, attr, val):
        if attr in tracing_vars.get(id(self), []):
            object.__setattr__(self, attr, val)
    # Container methods..
    def __bool__(self): return False
    def __contains__(self, item): return False
    def __getitem__(self, key): raise KeyError
    def __setitem__(self, key, val): pass
    def __iter__(self): return self
    def __len__(self): return 0
    # Iteration methods:
    def __next__(self): raise StopIteration
    

class TracingNullObject:
    """Tracing NullObject."""
    def __init__(self, tag, ivars=None, *args, **kwargs):
        tracing_tags [id(self)] = tag
        if isinstance(ivars, str):
            ivars = [ivars]
        tracing_vars [id(self)] = ivars or []
        if 0:
            suppress = ('tree item',)
            if tag not in suppress:
                print('='*10, 'NullObject.__init__:', id(self), tag)
    def __call__(self, *args, **kwargs):
        if 0:
            suppress = ('PyQt5.QtGui.QIcon', 'LeoQtTree.onItemCollapsed',)
            for z in suppress:
                if z not in repr(args):
                    print(f"%30s"  % 'NullObject.__call__:', args, kwargs)
        return self
    def __repr__(self):
        return f'TracingNullObject: {tracing_tags.get(id(self), "<NO TAG>")}'
    def __str__(self):
        return f'TracingNullObject: {tracing_tags.get(id(self), "<NO TAG>")}'
    #
    # Attribute access...
    def __delattr__(self, attr):
        return self
    def __getattr__(self, attr):
        null_object_print_attr(id(self), attr)
        if attr in tracing_vars.get(id(self), []):
            return getattr(self, attr, None)
        return self # Required.
    def __setattr__(self, attr, val):
        g.null_object_print(id(self), '__setattr__', attr, val)
        if attr in tracing_vars.get(id(self), []):
            object.__setattr__(self, attr, val)
    #
    # All other methods...
    def __bool__(self):
        if 0: # To do: print only once.
            suppress = ('getShortcut','on_idle', 'setItemText')
            callers = g.callers(2)
            if not callers.endswith(suppress):
                g.null_object_print(id(self), '__bool__')
        return False
    def __contains__(self, item):
        g.null_object_print(id(self), '__contains__')
        return False
    def __getitem__(self, key):
        g.null_object_print(id(self), '__getitem__')
        # pylint doesn't like trailing return None.
        # return None
    def __iter__(self):
        g.null_object_print(id(self), '__iter__')
        return self
    def __len__(self):
        # g.null_object_print(id(self), '__len__')
        return 0
    def __next__(self):
        g.null_object_print(id(self), '__next__')
        raise StopIteration
    def __setitem__(self, key, val):
        g.null_object_print(id(self), '__setitem__')
        # pylint doesn't like trailing return None.
        # return None
#@+node:ekr.20190330062625.1: *4* g.null_object_print_attr
def null_object_print_attr(id_, attr):
    suppress = True
    if suppress:
        #@+<< define suppression lists >>
        #@+node:ekr.20190330072026.1: *5* << define suppression lists >>
        suppress_callers = (
            'drawNode', 'drawTopTree', 'drawTree',
            'contractItem', 'getCurrentItem',
            'declutter_node',
            'finishCreate',
            'initAfterLoad',
            'show_tips',
            'writeWaitingLog',
            # 'set_focus', 'show_tips',
        )
        suppress_attrs = (
            # Leo...
            'c.frame.body.wrapper',
            'c.frame.getIconBar.add',
            'c.frame.log.createTab',
            'c.frame.log.enable',
            'c.frame.log.finishCreate',
            'c.frame.menu.createMenuBar',
            'c.frame.menu.finishCreate',
            # 'c.frame.menu.getMenu',
            'currentItem',
            'dw.leo_master.windowTitle',
            # Pyzo...
            'pyzo.keyMapper.connect',
            'pyzo.keyMapper.keyMappingChanged',
            'pyzo.keyMapper.setShortcut',
        )
        #@-<< define suppression lists >>
    else:
        # Print everything.
        suppress_callers = []
        suppress_attrs = []

    tag = tracing_tags.get(id_, "<NO TAG>")
    callers = g.callers(3).split(',')
    callers = ','.join(callers[:-1])
    in_callers = any([z in callers for z in suppress_callers])
    s = f"{tag}.{attr}"
    if suppress:
        # Filter traces.
        if not in_callers and s not in suppress_attrs:
            g.pr(f"{s:40} {callers}")
    else:
        # Print each signature once.  No need to filter!
        signature = f"{tag}.{attr}:{callers}"
        if signature not in tracing_signatures:
            tracing_signatures[signature] = True
            g.pr(f"{s:40} {callers}")
#@+node:ekr.20190330072832.1: *4* g.null_object_print
def null_object_print(id_, kind, *args):
    tag = tracing_tags.get(id_, "<NO TAG>")
    callers = g.callers(3).split(',')
    callers = ','.join(callers[:-1])
    s = f"{kind}.{tag}"
    signature = f"{s}:{callers}"
    if 1:
        # Always print:
        if args:
            args = ', '.join([repr(z) for z in args])
            g.pr(f"{s:40} {callers}\n\t\t\targs: {args}")
        else:
            g.pr(f"{s:40} {callers}")
    elif signature not in tracing_signatures:
        # Print each signature once.
        tracing_signatures[signature] = True
        g.pr(f"{s:40} {callers}")
#@+node:ekr.20120129181245.10220: *3* class g.TypedDict
class TypedDict:
    """
    A class providing additional dictionary-related methods:
    
    __init__:     Specifies types and the dict's name.
    __repr__:     Compatible with g.printObj, based on g.objToString.
    __setitem__:  Type checks its arguments.
    __str__:      A concise summary of the inner dict.
    add_to_list:  A convenience method that adds a value to its key's list.
    name:         The dict's name.
    setName:      Sets the dict's name, for use by __repr__.
    
    Overrides the following standard methods:

    copy:         A thin wrapper for copy.deepcopy.
    get:          Returns self.d.get
    items:        Returns self.d.items
    keys:         Returns self.d.keys
    update:       Updates self.d from either a dict or a TypedDict.
    """

    def __init__(self, name, keyType, valType):
        self.d = {}
        self._name = name  # For __repr__ only.
        self.keyType = keyType
        self.valType = valType
    #@+others
    #@+node:ekr.20120205022040.17770: *4* td.__repr__ & __str__
    def __str__(self):
        """Concise: used by repr."""
        return (
            f"<TypedDict name:{self._name} "
            f"keys:{self.keyType.__name__} "
            f"values:{self.valType.__name__} "
            f"len(keys): {len(list(self.keys()))}>"
        )

    def __repr__(self):
        """Suitable for g.printObj"""
        return f"{g.dictToString(self.d)}\n{str(self)}\n"
    #@+node:ekr.20120205022040.17774: *4* td.__setitem__
    def __setitem__(self, key, val):
        """Allow d[key] = val"""
        if key is None:
            g.trace('TypeDict: None is not a valid key', g.callers())
            return
        self._checkKeyType(key)
        self._checkKeyType(key)
        try:
            for z in val:
                self._checkValType(z)
        except TypeError:
            self._checkValType(val)  # val is not iterable.
        self.d[key] = val
    #@+node:ekr.20190904052828.1: *4* td.add_to_list
    def add_to_list(self, key, val):
        """Update the *list*, self.d [key]"""
        if key is None:
            g.trace('TypeDict: None is not a valid key', g.callers())
            return
        self._checkKeyType(key)
        self._checkValType(val)
        aList = self.d.get(key, [])
        if val not in aList:
            aList.append(val)
            self.d[key] = aList
    #@+node:ekr.20120206134955.10150: *4* td.checking
    def _checkKeyType(self, key):
        if key and key.__class__ != self.keyType:
            self._reportTypeError(key, self.keyType)

    def _checkValType(self, val):
        if val.__class__ != self.valType:
            self._reportTypeError(val, self.valType)

    def _reportTypeError(self, obj, objType):
        # print(f"Type mismatch: obj: {obj.__class__}, objType: {objType}")
        return (
            f"{self._name}\n"
            f"expected: {obj.__class__.__name__}\n"
            f"     got: {objType.__name__}")
    #@+node:ekr.20120223062418.10422: *4* td.copy
    def copy(self, name=None):
        """Return a new dict with the same contents."""
        # Transcrypt does not support Python's copy module.
        # __pragma__ ('skip')

        import copy
        return copy.deepcopy(self)
        
        # __pragma__ ('noskip')
    #@+node:ekr.20120205022040.17771: *4* td.get & keys & values
    def get(self, key, default=None):
        return self.d.get(key, default)

    def items(self):
        return self.d.items()

    def keys(self):
        return self.d.keys()

    def values(self):
        return self.d.values()
    #@+node:ekr.20190903181030.1: *4* td.get_getting & get_string_setting
    def get_setting(self, key):
        key = key.replace('-', '').replace('_', '')
        gs = self.get(key)
        val = gs and gs.val
        return val

    def get_string_setting(self, key):
        val = self.get_setting(key)
        return val if val and isinstance(val, str) else None
    #@+node:ekr.20190904103552.1: *4* td.name & setName
    def name(self):
        return self._name

    def setName(self, name):
        self._name = name
    #@+node:ekr.20120205022040.17807: *4* td.update
    def update(self, d):
        """Update self.d from a the appropriate dict."""
        if isinstance(d, TypedDict):
            self.d.update(d.d)
        else:
            self.d.update(d)
    #@-others
#@+node:ville.20090827174345.9963: *3* class g.UiTypeException & g.assertui
class UiTypeException(Exception):
    pass

def assertUi(uitype):
    if not g.app.gui.guiName() == uitype:
        raise UiTypeException
#@+node:ekr.20200219071828.1: *3* class TestLeoGlobals
class TestLeoGlobals(unittest.TestCase):
    """Tests for leoGlobals.py."""
    #@+others
    #@+node:ekr.20200219071958.1: *4* test_comment_delims_from_extension
    def test_comment_delims_from_extension(self):

        # pylint: disable=import-self
        from leo.core import leoGlobals as leo_g
        from leo.core import leoApp
        leo_g.app = leoApp.LeoApp()
        assert leo_g.comment_delims_from_extension(".py") == ('#', '', '')
        assert leo_g.comment_delims_from_extension(".c") == ('//', '/*', '*/')
        assert leo_g.comment_delims_from_extension(".html") == ('', '<!--', '-->')
    #@+node:ekr.20200219072957.1: *4* test_is_sentinel
    def test_is_sentinel(self):

        # pylint: disable=import-self
        from leo.core import leoGlobals as leo_g
        # Python.
        py_delims = leo_g.comment_delims_from_extension('.py')
        assert leo_g.is_sentinel("#@+node", py_delims)
        assert not leo_g.is_sentinel("#comment", py_delims)
        # C.
        c_delims = leo_g.comment_delims_from_extension('.c')
        assert leo_g.is_sentinel("//@+node", c_delims)
        assert not g.is_sentinel("//comment", c_delims)
        # Html.
        html_delims = leo_g.comment_delims_from_extension('.html')
        assert leo_g.is_sentinel("<!--@+node-->", html_delims)
        assert not leo_g.is_sentinel("<!--comment-->", html_delims)
    #@-others
#@+node:ekr.20140904112935.18526: *3* g.isTextWrapper & isTextWidget
def isTextWidget(w):
    return g.app.gui.isTextWidget(w)

def isTextWrapper(w):
    return g.app.gui.isTextWrapper(w)
#@+node:ekr.20140711071454.17649: ** g.Debugging, GC, Stats & Timing
#@+node:ekr.20031218072017.3104: *3* g.Debugging
#@+node:ekr.20031218072017.3105: *4* g.alert (deprecated)
def alert(message, c=None):
    """Raise an alert.

    This method is deprecated: use c.alert instead.
    """
    # The unit tests just tests the args.
    if not g.unitTesting:
        g.es(message)
        g.app.gui.alert(c, message)
#@+node:ekr.20180415144534.1: *4* g.assert_is
def assert_is(obj, list_or_class, warn=True):

    if warn:
        ok = isinstance(obj, list_or_class)
        if not ok:
            g.es_print(
                f"can not happen. {obj !r}: "
                f"expected {list_or_class}, "
                f"got: {obj.__class__.__name__}")
            g.es_print(g.callers())
        return ok
    ok = isinstance(obj, list_or_class)
    assert ok, (obj, obj.__class__.__name__, g.callers())
    return ok
#@+node:ekr.20180420081530.1: *4* g._assert
def _assert(condition, show_callers=True):
    """A safer alternative to a bare assert."""
    if g.unitTesting:
        assert condition
        return True
    ok = bool(condition)
    if ok:
        return True
    g.es_print('\n===== g._assert failed =====\n')
    if show_callers:
        g.es_print(g.callers())
    return False
#@+node:ekr.20051023083258: *4* g.callers & g.caller & _callerName
def callers(n=4, count=0, excludeCaller=True, verbose=False):
    """
    Return a string containing a comma-separated list of the callers
    of the function that called g.callerList.

    excludeCaller: True (the default), g.callers itself is not on the list.
    
    If the `verbose` keyword is True, return a list separated by newlines.
    """
    # Be careful to call g._callerName with smaller values of i first:
    # sys._getframe throws ValueError if there are less than i entries.
    result = []
    i = 3 if excludeCaller else 2
    while 1:
        s = _callerName(n=i, verbose=verbose)
        if s:
            result.append(s)
        if not s or len(result) >= n:
            break
        i += 1
    result.reverse()
    if count > 0:
        result = result[:count]
    if verbose:
        return ''.join([f"\n  {z}" for z in result])
    return ','.join(result)
#@+node:ekr.20031218072017.3107: *5* g._callerName
def _callerName(n, verbose=False):
    try:
        # get the function name from the call stack.
        f1 = sys._getframe(n)  # The stack frame, n levels up.
        code1 = f1.f_code  # The code object
        sfn = shortFilename(code1.co_filename)  # The file name.
        locals_ = f1.f_locals  # The local namespace.
        name = code1.co_name
        line = code1.co_firstlineno
        if verbose:
            obj = locals_.get('self')
            full_name = f"{obj.__class__.__name__}.{name}" if obj else name
            return f"line {line:4} {sfn:>30} {full_name}"
        return name
    except ValueError:
        return ''
            # The stack is not deep enough OR
            # sys._getframe does not exist on this platform.
    except Exception:
        es_exception()
        return ''  # "<no caller name>"
#@+node:ekr.20180328170441.1: *5* g.caller
def caller(i=1):
    """Return the caller name i levels up the stack."""
    return g.callers(i + 1).split(',')[0]
#@+node:ekr.20031218072017.3109: *4* g.dump
def dump(s):
    out = ""
    for i in s:
        out += str(ord(i)) + ","
    return out

def oldDump(s):
    out = ""
    for i in s:
        if i == '\n':
            out += "["; out += "n"; out += "]"
        if i == '\t':
            out += "["; out += "t"; out += "]"
        elif i == ' ':
            out += "["; out += " "; out += "]"
        else: out += i
    return out
#@+node:ekr.20150227102835.8: *4* g.dump_encoded_string
def dump_encoded_string(encoding, s):
    """Dump s, assumed to be an encoded string."""
    # Can't use g.trace here: it calls this function!
    print(f"dump_encoded_string: {g.callers()}")
    print(f"dump_encoded_string: encoding {encoding}\n")
    print(s)
    in_comment = False
    for ch in s:
        if ch == '#':
            in_comment = True
        elif not in_comment:
            print(f"{ord(ch):02x} {repr(ch)}")
        elif ch == '\n':
            in_comment = False
#@+node:ekr.20031218072017.1317: *4* g.file/module/plugin_date
def module_date(mod, format=None):
    theFile = g.os_path_join(app.loadDir, mod.__file__)
    root, ext = g.os_path_splitext(theFile)
    return g.file_date(root + ".py", format=format)

def plugin_date(plugin_mod, format=None):
    theFile = g.os_path_join(app.loadDir, "..", "plugins", plugin_mod.__file__)
    root, ext = g.os_path_splitext(theFile)
    return g.file_date(root + ".py", format=format)

def file_date(theFile, format=None):
    if theFile and g.os_path_exists(theFile):
        try:
            n = g.os_path_getmtime(theFile)
            if format is None:
                format = "%m/%d/%y %H:%M:%S"
            return time.strftime(format, time.gmtime(n))
        except(ImportError, NameError):
            pass  # Time module is platform dependent.
    return ""
#@+node:ekr.20031218072017.3127: *4* g.get_line & get_line__after
# Very useful for tracing.

def get_line(s, i):
    nl = ""
    if g.is_nl(s, i):
        i = g.skip_nl(s, i)
        nl = "[nl]"
    j = g.find_line_start(s, i)
    k = g.skip_to_end_of_line(s, i)
    return nl + s[j:k]

# Important: getLine is a completely different function.
# getLine = get_line

def get_line_after(s, i):
    nl = ""
    if g.is_nl(s, i):
        i = g.skip_nl(s, i)
        nl = "[nl]"
    k = g.skip_to_end_of_line(s, i)
    return nl + s[i:k]

getLineAfter = get_line_after
#@+node:ekr.20080729142651.1: *4* g.getIvarsDict and checkUnchangedIvars
def getIvarsDict(obj):
    """Return a dictionary of ivars:values for non-methods of obj."""
    d = dict(
        [[key, getattr(obj, key)] for key in dir(obj)
            if not isinstance(getattr(obj, key), types.MethodType)])
    return d

def checkUnchangedIvars(obj, d, exceptions=None):
    if not exceptions: exceptions = []
    ok = True
    for key in d:
        if key not in exceptions:
            if getattr(obj, key) != d.get(key):
                g.trace(
                    f"changed ivar: {key} "
                    f"old: {repr(d.get(key))} "
                    f"new: {repr(getattr(obj, key))}")
                ok = False
    return ok
#@+node:ekr.20031218072017.3128: *4* g.pause
def pause(s):
    g.pr(s)
    i = 0
    while i < 1000 * 1000:
        i += 1
#@+node:ekr.20041105091148: *4* g.pdb
def pdb(message=''):
    """Fall into pdb."""
    # Transcrypt does not support Python's pdb or QtCore modules.
    # __pragma__ ('skip')

    import pdb  # Required: we have just defined pdb as a function!
    if app and not app.useIpython:
        # from leo.core.leoQt import QtCore
        # This is more portable.
        try:
            import PyQt5.QtCore as QtCore
        except ImportError:
            try:
                import PyQt4.QtCore as QtCore
            except ImportError:
                QtCore = None
        if QtCore:
            # pylint: disable=no-member
            QtCore.pyqtRemoveInputHook()
    if message:
        print(message)
    pdb.set_trace()
    
    # __pragma__ ('noskip')
#@+node:ekr.20041224080039: *4* g.dictToString
def dictToString(d, indent='', tag=None):
    """Pretty print a Python dict to a string."""
    # pylint: disable=unnecessary-lambda
    if not d:
        return '{}'
    result = ['{\n']
    indent2 = indent + ' ' * 4
    n = 2 + len(indent) + max([len(repr(z)) for z in d.keys()])
    for i, key in enumerate(sorted(d, key=lambda z: repr(z))):
        pad = ' ' * max(0, (n - len(repr(key))))
        result.append(f"{pad}{key}:")
        result.append(objToString(d.get(key), indent=indent2))
        if i + 1 < len(d.keys()):
            result.append(',')
        result.append('\n')
    result.append(indent + '}')
    s = ''.join(result)
    return f"{tag}...\n{s}\n" if tag else s
#@+node:ekr.20041126060136: *4* g.listToString
def listToString(obj, indent='', tag=None):
    """Pretty print a Python list to a string."""
    if not obj:
        return '[]'
    result = ['[']
    indent2 = indent + ' ' * 4
    # I prefer not to compress lists.
    for i, obj2 in enumerate(obj):
        result.append('\n' + indent2)
        result.append(objToString(obj2, indent=indent2))
        if i + 1 < len(obj) > 1:
            result.append(',')
        else:
            result.append('\n' + indent)
    result.append(']')
    s = ''.join(result)
    return f"{tag}...\n{s}\n" if tag else s
#@+node:ekr.20050819064157: *4* g.objToSTring & g.toString
def objToString(obj, indent='', printCaller=False, tag=None):
    """Pretty print any Python object to a string."""
    # pylint: disable=undefined-loop-variable
        # Looks like a a pylint bug.
    #
    # Compute s.
    if isinstance(obj, dict):
        s = dictToString(obj, indent=indent)
    elif isinstance(obj, list):
        s = listToString(obj, indent=indent)
    elif isinstance(obj, tuple):
        s = tupleToString(obj, indent=indent)
    elif isinstance(obj, str):
        # Print multi-line strings as lists.
        s = obj
        lines = g.splitLines(s)
        if len(lines) > 1:
            s = listToString(lines, indent=indent)
        else:
            s = repr(s)
    else:
        s = repr(obj)
    #
    # Compute the return value.
    if printCaller and tag:
        prefix = f"{g.caller()}: {tag}"
    elif printCaller or tag:
        prefix = g.caller() if printCaller else tag
    else:
        prefix = None
    if prefix:
        sep = '\n' if '\n' in s else ' '
        return f"{prefix}:{sep}{s}"
    return s

toString = objToString
#@+node:ekr.20140401054342.16844: *4* g.run_pylint
def run_pylint(fn, rc,
    dots=True,  # Show level dots in Sherlock traces.
    patterns=None,  # List of Sherlock trace patterns.
    sherlock=False,  # Enable Sherlock tracing.
    show_return=True,  # Show returns in Sherlock traces.
    stats_patterns=None,  # Patterns for Sherlock statistics.
    verbose=True,  # Show filenames in Sherlock traces.
):
    """
    Run pylint with the given args, with Sherlock tracing if requested.

    **Do not assume g.app exists.**

    run() in pylint-leo.py and PylintCommand.run_pylint *optionally* call this function.
    """
    #Transcrypt does not support Python's 'lint' module.
    # __pragma__ ('skip')

    try:
        from pylint import lint
    except ImportError:
        g.trace('can not import pylint')
        return
    if not g.os_path_exists(fn):
        g.trace('does not exist:', fn)
        return
    if not g.os_path_exists(rc):
        g.trace('does not exist', rc)
        return
    args = [f"--rcfile={rc}"]
    # Prints error number.
        # args.append('--msg-template={path}:{line}: [{msg_id}({symbol}), {obj}] {msg}')
    args.append(fn)
    if sherlock:
        sherlock = g.SherlockTracer(
                dots=dots,
                show_return=show_return,
                verbose=True,  # verbose: show filenames.
                patterns=patterns or [],
            )
        try:
            sherlock.run()
            lint.Run(args)
        finally:
            sherlock.stop()
            sherlock.print_stats(patterns=stats_patterns or [])
    else:
        # print('run_pylint: %s' % g.shortFileName(fn))
        try:
            lint.Run(args)  # does sys.exit
        finally:
            # Printing does not work well here.
            # When not waiting, printing from severl process can be interspersed.
            pass
            
    # __pragma__ ('noskip')
#@+node:ekr.20120912153732.10597: *4* g.wait
def sleep(n):
    """Wait about n milliseconds."""
    from time import sleep
    sleep(n)  #sleeps for 5 seconds
#@+node:ekr.20171023140544.1: *4* g.printObj & aliases
def printObj(obj, indent='', printCaller=False, tag=None):
    """Pretty print any Python object using g.pr."""
    g.pr(objToString(obj, indent=indent, printCaller=printCaller, tag=tag))

printDict = printObj
printList = printObj
printTuple = printObj
#@+node:ekr.20171023110057.1: *4* g.tupleToString
def tupleToString(obj, indent='', tag=None):
    """Pretty print a Python tuple to a string."""
    if not obj:
        return '(),'
    result = ['(']
    indent2 = indent + ' ' * 4
    for i, obj2 in enumerate(obj):
        if len(obj) > 1:
            result.append('\n' + indent2)
        result.append(objToString(obj2, indent=indent2))
        if len(obj) == 1 or i + 1 < len(obj):
            result.append(',')
        elif len(obj) > 1:
            result.append('\n' + indent)
    result.append(')')
    s = ''.join(result)
    return f"{tag}...\n{s}\n" if tag else s
#@+node:ekr.20031218072017.1588: *3* g.Garbage Collection
lastObjectCount = 0
lastObjectsDict = {}
lastTypesDict = {}
lastFunctionsDict = {}
#@+node:ekr.20031218072017.1589: *4* g.clearAllIvars
def clearAllIvars(o):
    """Clear all ivars of o, a member of some class."""
    if o:
        o.__dict__.clear()
#@+node:ekr.20031218072017.1590: *4* g.collectGarbage
def collectGarbage():
    try:
        gc.collect()
    except Exception:
        pass
#@+node:ekr.20060127162818: *4* g.enable_gc_debug
def enable_gc_debug(event=None):
    # pylint: disable=no-member
    if not gc:
        g.error('can not import gc module')
        return
    gc.set_debug(
        gc.DEBUG_STATS |  # prints statistics.
        gc.DEBUG_LEAK |  # Same as all below.
        gc.DEBUG_COLLECTABLE |
        gc.DEBUG_UNCOLLECTABLE |
        # gc.DEBUG_INSTANCES |
        # gc.DEBUG_OBJECTS |
        gc.DEBUG_SAVEALL)
#@+node:ekr.20190609113810.1: *4* g.GetRepresentativeObjects
def getRepresentativeLiveObjects():
    """
    Return a dict.
    Keys classes.
    Values are the first (representative) live object for each type.
    """
    d = {}  # Keys are types, values are the *first* instance.
    for obj in gc.get_objects():
        t = type(obj)
        if t not in d and hasattr(obj, '__class__'):
            d[t] = obj
    return d
#@+node:ekr.20031218072017.1592: *4* g.printGc
# Formerly called from unit tests.

def printGc(tag=None):
    tag = tag or g._callerName(n=2)
    printGcObjects(tag=tag)
    printGcRefs(tag=tag)
    printGcVerbose(tag=tag)
#@+node:ekr.20031218072017.1593: *5* g.printGcRefs
def printGcRefs(tag=''):
    verbose = False
    refs = gc.get_referrers(app.windowList[0])
    g.pr('-' * 30, tag)
    if verbose:
        g.pr("refs of", app.windowList[0])
        for ref in refs:
            g.pr(type(ref))
    else:
        g.pr(f"{len(refs):d} referers")
#@+node:ekr.20060202161935: *4* g.printGcAll
def printGcAll(full=False, sort_by_n=True):
    """Print a summary of all presently live objects."""
    if g.unitTesting:
        return
    t1 = time.process_time()
    objects = gc.get_objects()
    d = {}  # Keys are types, values are ints (number of instances).
    for obj in objects:
        t = type(obj)
        if hasattr(obj, '__class__'):
            d[t] = d.get(t, 0) + 1
    t2 = time.process_time()
    if full:
        if sort_by_n:  # Sort by n
            items = list(d.items())
            items.sort(key=lambda x: x[1])
            for z in reversed(items):
                print(f"{z[1]:8} {z[0]}")
        else:  # Sort by type
            g.printObj(d)
    #
    # Summarize
    print(
        f"\n"
        f"printGcAll: {len(objects):d} objects "
        f"in {t2-t1:5.2f} sec. ")
#@+node:ekr.20060127164729.1: *4* g.printGcObjects
def printGcObjects(tag=''):
    """Print newly allocated objects."""
    tag = tag or g._callerName(n=2)
    global lastObjectCount
    try:
        n = len(gc.garbage)
        n2 = len(gc.get_objects())
        delta = n2 - lastObjectCount
        if delta == 0: return
        lastObjectCount = n2
        #@+<< print number of each type of object >>
        #@+node:ekr.20040703054646: *5* << print number of each type of object >>
        global lastTypesDict
        typesDict = {}
        for obj in gc.get_objects():
            t = type(obj)
            # pylint: disable=no-member
            if t == 'instance' and t != types.UnicodeType:  # NOQA
                try: t = obj.__class__
                except Exception: pass
            if t != types.FrameType:  # NOQA
                r = repr(t)  # was type(obj) instead of repr(t)
                n = typesDict.get(r, 0)
                typesDict[r] = n + 1
        # Create the union of all the keys.
        keys = {}
        for key in lastTypesDict:
            if key not in typesDict:
                keys[key] = None
        empty = True
        for key in keys:
            n3 = lastTypesDict.get(key, 0)
            n4 = typesDict.get(key, 0)
            delta2 = n4 - n3
            if delta2 != 0:
                empty = False
                break
        if not empty:
            g.pr('-' * 30)
            g.pr(f"{tag}: garbage: {n}, objects: {n2}, delta: {delta}")
            if 0:
                for key in sorted(keys):
                    n1 = lastTypesDict.get(key, 0)
                    n2 = typesDict.get(key, 0)
                    delta2 = n2 - n1
                    if delta2 != 0:
                        g.pr(f"{delta2:6d} ={n2:7d} {key}")
        lastTypesDict = typesDict
        typesDict = {}
        #@-<< print number of each type of object >>
        if 0:
            #@+<< print added functions >>
            #@+node:ekr.20040703065638: *5* << print added functions >>
            global lastFunctionsDict
            funcDict = {}
            getspec = inspect.getfullargspec
            n = 0  # Don't print more than 50 objects.
            for obj in gc.get_objects():
                if isinstance(obj, types.FunctionType):
                    n += 1
                    key = repr(obj)  # Don't create a pointer to the object!
                    funcDict[key] = None
                    if n < 50 and key not in lastFunctionsDict:
                        g.pr(obj)
                        data = getspec(obj)
                        args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, annotations = data
                        g.pr("args", args)
                        if varargs: g.pr("varargs", varargs)
                        if varkw: g.pr("varkw", varkw)
                        if defaults:
                            g.pr("defaults...")
                            for s in defaults: g.pr(s)
            lastFunctionsDict = funcDict
            funcDict = {}
            #@-<< print added functions >>
    except Exception:
        traceback.print_exc()

printNewObjects = pno = printGcObjects
#@+node:ekr.20060205043324.1: *4* g.printGcSummary
def printGcSummary(tag=''):
    tag = tag or g._callerName(n=2)
    g.enable_gc_debug()
    try:
        n = len(gc.garbage)
        n2 = len(gc.get_objects())
        s = f"{tag}: printGCSummary: garbage: {n}, objects: {n2}"
        g.pr(s)
    except Exception:
        traceback.print_exc()
#@+node:ekr.20060127165509: *4* g.printGcVerbose
# WARNING: the id trick is not proper because newly allocated objects
#          can have the same address as old objets.

def printGcVerbose(tag=''):
    tag = tag or g._callerName(n=2)
    global lastObjectsDict
    objects = gc.get_objects()
    newObjects = [o for o in objects if id(o) not in lastObjectsDict]
    lastObjectsDict = {}
    for o in objects:
        lastObjectsDict[id(o)] = o
    dicts = 0; seqs = 0
    i = 0; n = len(newObjects)
    while i < 100 and i < n:
        o = newObjects[i]
        if isinstance(o, dict):
            dicts += 1
        elif isinstance(o, (list, tuple)):
            #g.pr(id(o),repr(o))
            seqs += 1
        #else:
        #    g.pr(o)
        i += 1
    g.pr('=' * 40)
    g.pr(f"dicts: {dicts}, sequences: {seqs}")
    g.pr(f"{tag}: {len(newObjects)} new, {len(objects)} total objects")
    g.pr('-' * 40)
#@+node:ekr.20180528151850.1: *3* g.printTimes
def printTimes(times):
    """
    Print the differences in the times array.
    
    times: an array of times (calls to time.process_time()).
    """
    for n, junk in enumerate(times[:-1]):
        t = times[n + 1] - times[n]
        if t > 0.1:
            g.trace(f"*** {n} {t:5.4f} sec.")
#@+node:ekr.20031218072017.3133: *3* g.Statistics
#@+node:ekr.20031218072017.3134: *4* g.clearStats
def clearStats():

    g.app.statsDict = {}
#@+node:ekr.20031218072017.3135: *4* g.printStats
@command('show-stats')
def printStats(event=None, name=None):
    """
    Print all gathered statistics.
    
    Here is the recommended code to gather stats for one method/function:
        
        if not g.app.statsLockout:
            g.app.statsLockout = True
            try:
                d = g.app.statsDict
                key = 'g.isUnicode:' + g.callers()
                d [key] = d.get(key, 0) + 1
            finally:
                g.app.statsLockout = False
    """
    if name:
        if not isString(name):
            name = repr(name)
    else:
        name = g._callerName(n=2)  # Get caller name 2 levels back.
    #
    # Print the stats, organized by number of calls.
    d = g.app.statsDict
    d2 = {val: key for key, val in d.iteritems()}
    for key in reversed(sorted(d2.keys())):
        print(f"{key:7} {d2.get(key)}")
#@+node:ekr.20031218072017.3136: *4* g.stat
def stat(name=None):
    """Increments the statistic for name in g.app.statsDict
    The caller's name is used by default.
    """
    d = g.app.statsDict
    if name:
        if not isString(name):
            name = repr(name)
    else:
        name = g._callerName(n=2)  # Get caller name 2 levels back.
    d[name] = 1 + d.get(name, 0)
#@+node:ekr.20031218072017.3137: *3* g.Timing
def getTime():
    return time.time()

def esDiffTime(message, start):
    delta = time.time() - start
    g.es('', f"{message} {delta:5.2f} sec.")
    return time.time()

def printDiffTime(message, start):
    delta = time.time() - start
    g.pr(f"{message} {delta:5.2f} sec.")
    return time.time()

def timeSince(start):
    return f"{time.time()-start:5.2f} sec."
#@+node:ekr.20031218072017.1380: ** g.Directives
# Weird pylint bug, activated by TestLeoGlobals class.
# Disabling this will be safe, because pyflakes will still warn about true redefinitions
# pylint: disable=function-redefined
#@+node:EKR.20040504150046.4: *3* g.comment_delims_from_extension
def comment_delims_from_extension(filename):
    """
    Return the comment delims corresponding to the filename's extension.
    """
    if filename.startswith('.'):
        root, ext = None, filename
    else:
        root, ext = os.path.splitext(filename)
    if ext == '.tmp':
        root, ext = os.path.splitext(root)
    language = g.app.extension_dict.get(ext[1:])
    if ext:
        return g.set_delims_from_language(language)
    g.trace(
        f"unknown extension: {ext!r}, "
        f"filename: {filename!r}, "
        f"root: {root!r}")
    return '', '', ''
#@+node:ekr.20170201150505.1: *3* g.findAllValidLanguageDirectives
def findAllValidLanguageDirectives(p):
    """Return list of all valid @language directives in p.b"""
    if not p:
        return []
    languages = set()
    for m in g.g_language_pat.finditer(p.b):
        language = m.group(1)
        if g.isValidLanguage(language):
            languages.add(language)
    return list(sorted(languages))
#@+node:ekr.20090214075058.8: *3* g.findAtTabWidthDirectives (must be fast)
def findTabWidthDirectives(c, p):
    """Return the language in effect at position p."""
    if c is None:
        return None  # c may be None for testing.
    w = None
    # 2009/10/02: no need for copy arg to iter
    for p in p.self_and_parents(copy=False):
        if w: break
        for s in p.h, p.b:
            if w: break
            anIter = g_tabwidth_pat.finditer(s)
            for m in anIter:
                word = m.group(0)
                i = m.start(0)
                j = g.skip_ws(s, i + len(word))
                junk, w = g.skip_long(s, j)
                if w == 0: w = None
    return w
#@+node:ekr.20170127142001.5: *3* g.findFirstAtLanguageDirective
def findFirstValidAtLanguageDirective(p):
    """Return the first *valid* @language directive in p.b."""
    if not p:
        return None
    for m in g.g_language_pat.finditer(p.b):
        language = m.group(1)
        if g.isValidLanguage(language):
            return language
    return None
#@+node:ekr.20090214075058.6: *3* g.findLanguageDirectives (must be fast)
def findLanguageDirectives(c, p):
    """Return the language in effect at position p."""
    if c is None or p is None:
        return None  # c may be None for testing.
        
    v0 = p.v
        
    def find_language(p_or_v):
        for s in p_or_v.h, p_or_v.b:
            for m in g_language_pat.finditer(s):
                language = m.group(1)
                if g.isValidLanguage(language):
                    return language
        return None

    # First, search up the tree.
    for p in p.self_and_parents(copy=False):
        language = find_language(p)
        if language:
            return language
    # #1625: Second, expand the search for cloned nodes.
    seen = [] # vnodes that have already been searched.
    parents = v0.parents[:] # vnodes whose ancestors are to be searched.
    while parents:
        parent_v = parents.pop()
        if parent_v in seen:
            continue
        seen.append(parent_v)
        language = find_language(parent_v)
        if language:
            return language
        for grand_parent_v in parent_v.parents:
            if grand_parent_v not in seen:
                parents.append(grand_parent_v)
    # Finally, fall back to the defaults.
    return c.target_language.lower() if c.target_language else 'python'
#@+node:ekr.20031218072017.1385: *3* g.findReference
# Called from the syntax coloring method that colorizes section references.
# Also called from write at.putRefAt.

def findReference(name, root):
    """Find the section definition for name.

    If a search of the descendants fails,
    and an ancestor is an @root node,
    search all the descendants of the @root node.
    """
    for p in root.subtree(copy=False):
        assert(p != root)
        if p.matchHeadline(name) and not p.isAtIgnoreNode():
            return p.copy()
    # New in Leo 4.7: expand the search for @root trees.
    for p in root.self_and_parents(copy=False):
        d = g.get_directives_dict(p)
        if 'root' in d:
            for p2 in p.subtree(copy=False):
                if p2.matchHeadline(name) and not p2.isAtIgnoreNode():
                    return p2.copy()
    return None
#@+node:ekr.20090214075058.9: *3* g.get_directives_dict (must be fast)
# The caller passes [root_node] or None as the second arg.
# This allows us to distinguish between None and [None].

def get_directives_dict(p, root=None):
    """
    Scan p for Leo directives found in globalDirectiveList.

    Returns a dict containing the stripped remainder of the line
    following the first occurrence of each recognized directive
    """
    if root:
        root_node = root[0]
    d = {}
    #
    # #1688:    legacy: Always compute the pattern.
    #           g.directives_pat is updated whenever loading a plugin.
    #
    # The headline has higher precedence because it is more visible.
    for kind, s in (('head', p.h), ('body', p.b)):
        anIter = g.directives_pat.finditer(s)
        for m in anIter:
            word = m.group(1).strip()
            i = m.start(1)
            if word in d: continue
            j = i + len(word)
            if j < len(s) and s[j] not in ' \t\n':
                continue
                    # Not a valid directive: just ignore it.
                    # A unit test tests that @path:any is invalid.
            k = g.skip_line(s, j)
            val = s[j:k].strip()
            if word in ('root-doc', 'root-code'):
                d['root'] = val  # in addition to optioned version
            d[word] = val
            # New in Leo 5.7.1: @path is allowed in body text.
            # This is very useful when doing recursive imports.
    if root:
        anIter = g_noweb_root.finditer(p.b)
        for m in anIter:
            if root_node:
                d["root"] = 0  # value not immportant
            else:
                g.es(f'{g.angleBrackets("*")} may only occur in a topmost node (i.e., without a parent)')
            break
    return d
#@+node:ekr.20080827175609.1: *3* g.get_directives_dict_list (must be fast)
def get_directives_dict_list(p):
    """Scans p and all its ancestors for directives.

    Returns a list of dicts containing pointers to
    the start of each directive"""
    result = []
    p1 = p.copy()
    for p in p1.self_and_parents(copy=False):
        root = None if p.hasParent() else [p]
            # No copy necessary: g.get_directives_dict does not change p.
        result.append(g.get_directives_dict(p, root=root))
    return result
#@+node:ekr.20111010082822.15545: *3* g.getLanguageFromAncestorAtFileNode
def getLanguageFromAncestorAtFileNode(p):
    """
    Return the language in effect from the nearest enclosing @<file> node:
    1. An unambiguous @language directive of the @<file> node.
    2. The file extension of the @<file> node.
    """
    v0 = p.v
        
    def find_language(p):
        # #1693: First, scan p.b for an *unambiguous* @language directive.
        if p.b.strip():
            languages = g.findAllValidLanguageDirectives(p)
            if len(languages) == 1:  # An unambiguous language
                language = languages[0]
                return language
        # Second: use the file's extension.
        if p.isAnyAtFileNode():
            name = p.anyAtFileNodeName()
            junk, ext = g.os_path_splitext(name)
            ext = ext[1:]  # strip the leading .
            language = g.app.extension_dict.get(ext)
            if g.isValidLanguage(language):
                return language
        return None

    # First, look at the direct parents.
    for p in p.self_and_parents(copy=False):
        language = find_language(p)
        if language:
            return language
    #
    # #1625: Expand the search for cloned nodes.
    seen = [] # vnodes that have already been searched.
    parents = v0.parents[:] # vnodes whose ancestors are to be searched.
    while parents:
        parent_v = parents.pop()
        if parent_v in seen:
            continue
        seen.append(parent_v)
        language = find_language(parent_v)
        if language:
            return language
        for grand_parent_v in parent_v.parents:
            if grand_parent_v not in seen:
                parents.append(grand_parent_v)
    return None
#@+node:ekr.20150325075144.1: *3* g.getLanguageFromPosition
def getLanguageAtPosition(c, p):
    """
    Return the language in effect at position p.
    This is always a lowercase language name, never None.
    """
    aList = g.get_directives_dict_list(p)
    d = g.scanAtCommentAndAtLanguageDirectives(aList)
    language = (
        d and d.get('language') or
        g.getLanguageFromAncestorAtFileNode(p) or
        c.config.getString('target-language') or
        'python'
    )
    return language.lower()
#@+node:ekr.20031218072017.1386: *3* g.getOutputNewline
def getOutputNewline(c=None, name=None):
    """Convert the name of a line ending to the line ending itself.

    Priority:
    - Use name if name given
    - Use c.config.output_newline if c given,
    - Otherwise use g.app.config.output_newline.
    """
    if name: s = name
    elif c: s = c.config.output_newline
    else: s = app.config.output_newline
    if not s: s = ''
    s = s.lower()
    # pylint: disable=undefined-loop-variable
    # looks like a pylint bug
    if s in ("nl", "lf"): s = '\n'
    elif s == "cr": s = '\r'
    elif s == "platform": s = os.linesep  # 12/2/03: emakital
    elif s == "crlf": s = "\r\n"
    else: s = '\n'  # Default for erroneous values.
    assert isinstance(s, str), repr(s)
    return s
#@+node:ekr.20200521075143.1: *3* g.inAtNosearch
def inAtNosearch(p):
    """Return True if p or p's ancestors contain an @nosearch directive."""
    for p in p.self_and_parents():
        if p.is_at_ignore() or re.search(r'(^@|\n@)nosearch\b', p.b):
            return True
    return False
#@+node:ekr.20131230090121.16528: *3* g.isDirective
def isDirective(s):
    """Return True if s starts with a directive."""
    m = g_is_directive_pattern.match(s)
    if m:
        s2 = s[m.end(1) :]
        if s2 and s2[0] in ".(":
            return False
        return bool(m.group(1) in g.globalDirectiveList)
    return False
#@+node:ekr.20200810074755.1: *3* g.isValidLanguage (new)
def isValidLanguage(language):
    """True if language exists in leo/modes."""
    # 2020/08/12: A hack for c++
    if language in ('c++', 'cpp'):
        language = 'cplusplus'
    fn = g.os_path_join(g.app.loadDir, '..', 'modes', f"{language}.py")
    return g.os_path_exists(fn)
#@+node:ekr.20080827175609.52: *3* g.scanAtCommentAndLanguageDirectives
def scanAtCommentAndAtLanguageDirectives(aList):
    """
    Scan aList for @comment and @language directives.

    @comment should follow @language if both appear in the same node.
    """
    lang = None
    for d in aList:
        comment = d.get('comment')
        language = d.get('language')
        # Important: assume @comment follows @language.
        if language:
            lang, delim1, delim2, delim3 = g.set_language(language, 0)
        if comment:
            delim1, delim2, delim3 = g.set_delims_from_string(comment)
        if comment or language:
            delims = delim1, delim2, delim3
            d = {'language': lang, 'comment': comment, 'delims': delims}
            return d
    return None
#@+node:ekr.20080827175609.32: *3* g.scanAtEncodingDirectives
def scanAtEncodingDirectives(aList):
    """Scan aList for @encoding directives."""
    for d in aList:
        encoding = d.get('encoding')
        if encoding and g.isValidEncoding(encoding):
            return encoding
        if encoding and not g.app.unitTesting:
            g.error("invalid @encoding:", encoding)
    return None
#@+node:ekr.20080827175609.53: *3* g.scanAtHeaderDirectives
def scanAtHeaderDirectives(aList):
    """scan aList for @header and @noheader directives."""
    for d in aList:
        if d.get('header') and d.get('noheader'):
            g.error("conflicting @header and @noheader directives")
#@+node:ekr.20080827175609.33: *3* g.scanAtLineendingDirectives
def scanAtLineendingDirectives(aList):
    """Scan aList for @lineending directives."""
    for d in aList:
        e = d.get('lineending')
        if e in ("cr", "crlf", "lf", "nl", "platform"):
            lineending = g.getOutputNewline(name=e)
            return lineending
        # else:
            # g.error("invalid @lineending directive:",e)
    return None
#@+node:ekr.20080827175609.34: *3* g.scanAtPagewidthDirectives
def scanAtPagewidthDirectives(aList, issue_error_flag=False):
    """Scan aList for @pagewidth directives."""
    for d in aList:
        s = d.get('pagewidth')
        if s is not None:
            i, val = g.skip_long(s, 0)
            if val is not None and val > 0:
                return val
            if issue_error_flag and not g.app.unitTesting:
                g.error("ignoring @pagewidth", s)
    return None
#@+node:ekr.20101022172109.6108: *3* g.scanAtPathDirectives scanAllAtPathDirectives
def scanAtPathDirectives(c, aList):
    path = c.scanAtPathDirectives(aList)
    return path

def scanAllAtPathDirectives(c, p):
    aList = g.get_directives_dict_list(p)
    path = c.scanAtPathDirectives(aList)
    return path
#@+node:ekr.20100507084415.5760: *3* g.scanAtRootDirectives
def scanAtRootDirectives(aList):
    """Scan aList for @root directives."""
    for d in aList:
        s = d.get('root')
        if s is not None:
            i, mode = g.scanAtRootOptions(s, 0)
            return mode
    return None
#@+node:ekr.20031218072017.3154: *3* g.scanAtRootOptions
def scanAtRootOptions(s, i, err_flag=False):
    # The @root has been eaten when called from tangle.scanAllDirectives.
    if g.match(s, i, "@root"):
        i += len("@root")
        i = g.skip_ws(s, i)
    mode = None
    while g.match(s, i, '-'):
        #@+<< scan another @root option >>
        #@+node:ekr.20031218072017.3155: *4* << scan another @root option >>
        i += 1; err = -1
        if g.match_word(s, i, "code"):  # Just match the prefix.
            if not mode: mode = "code"
            elif err_flag: g.es("modes conflict in:", g.get_line(s, i))
        elif g.match(s, i, "doc"):  # Just match the prefix.
            if not mode: mode = "doc"
            elif err_flag: g.es("modes conflict in:", g.get_line(s, i))
        else:
            err = i - 1
        # Scan to the next minus sign.
        while i < len(s) and s[i] not in (' ', '\t', '\n', '-'):
            i += 1
        if err > -1 and err_flag:
            z_opt = s[err:i]
            z_line = g.get_line(s, i)
            g.es("unknown option:", z_opt, "in", z_line)
        #@-<< scan another @root option >>
    if mode is None:
        doc = app.config.at_root_bodies_start_in_doc_mode
        mode = "doc" if doc else "code"
    return i, mode
#@+node:ekr.20080827175609.37: *3* g.scanAtTabwidthDirectives & scanAllTabWidthDirectives
def scanAtTabwidthDirectives(aList, issue_error_flag=False):
    """Scan aList for @tabwidth directives."""
    for d in aList:
        s = d.get('tabwidth')
        if s is not None:
            junk, val = g.skip_long(s, 0)
            if val not in (None, 0):
                return val
            if issue_error_flag and not g.app.unitTesting:
                g.error("ignoring @tabwidth", s)
    return None

def scanAllAtTabWidthDirectives(c, p):
    """Scan p and all ancestors looking for @tabwidth directives."""
    if c and p:
        aList = g.get_directives_dict_list(p)
        val = g.scanAtTabwidthDirectives(aList)
        ret = c.tab_width if val is None else val
    else:
        ret = None
    return ret
#@+node:ekr.20080831084419.4: *3* g.scanAtWrapDirectives & scanAllAtWrapDirectives
def scanAtWrapDirectives(aList, issue_error_flag=False):
    """Scan aList for @wrap and @nowrap directives."""
    for d in aList:
        if d.get('wrap') is not None:
            return True
        if d.get('nowrap') is not None:
            return False
    return None

def scanAllAtWrapDirectives(c, p):
    """Scan p and all ancestors looking for @wrap/@nowrap directives."""
    if c and p:
        default = c and c.config.getBool("body-pane-wraps")
        aList = g.get_directives_dict_list(p)
        val = g.scanAtWrapDirectives(aList)
        ret = default if val is None else val
    else:
        ret = None
    return ret
#@+node:ekr.20080901195858.4: *3* g.scanDirectives  (for compatibility only)
def scanDirectives(c, p=None):
    return c.scanAllDirectives(p)
#@+node:ekr.20040715155607: *3* g.scanForAtIgnore
def scanForAtIgnore(c, p):
    """Scan position p and its ancestors looking for @ignore directives."""
    if g.app.unitTesting:
        return False  # For unit tests.
    for p in p.self_and_parents(copy=False):
        d = g.get_directives_dict(p)
        if 'ignore' in d:
            return True
    return False
#@+node:ekr.20040712084911.1: *3* g.scanForAtLanguage
def scanForAtLanguage(c, p):
    """Scan position p and p's ancestors looking only for @language and @ignore directives.

    Returns the language found, or c.target_language."""
    # Unlike the code in x.scanAllDirectives, this code ignores @comment directives.
    if c and p:
        for p in p.self_and_parents(copy=False):
            d = g.get_directives_dict(p)
            if 'language' in d:
                z = d["language"]
                language, delim1, delim2, delim3 = g.set_language(z, 0)
                return language
    return c.target_language
#@+node:ekr.20041123094807: *3* g.scanForAtSettings
def scanForAtSettings(p):
    """Scan position p and its ancestors looking for @settings nodes."""
    for p in p.self_and_parents(copy=False):
        h = p.h
        h = g.app.config.canonicalizeSettingName(h)
        if h.startswith("@settings"):
            return True
    return False
#@+node:ekr.20031218072017.1382: *3* g.set_delims_from_language
def set_delims_from_language(language):
    """Return a tuple (single,start,end) of comment delims."""
    val = g.app.language_delims_dict.get(language)
    if val:
        delim1, delim2, delim3 = g.set_delims_from_string(val)
        if delim2 and not delim3:
            return '', delim1, delim2
        # 0,1 or 3 params.
        return delim1, delim2, delim3
    return '', '', ''
        # Indicate that no change should be made
#@+node:ekr.20031218072017.1383: *3* g.set_delims_from_string
def set_delims_from_string(s):
    """
    Return (delim1, delim2, delim2), the delims following the @comment
    directive.

    This code can be called from @language logic, in which case s can
    point at @comment
    """
    # Skip an optional @comment
    tag = "@comment"
    i = 0
    if g.match_word(s, i, tag):
        i += len(tag)
    count = 0; delims = ['', '', '']
    while count < 3 and i < len(s):
        i = j = g.skip_ws(s, i)
        while i < len(s) and not g.is_ws(s[i]) and not g.is_nl(s, i):
            i += 1
        if j == i: break
        delims[count] = s[j:i] or ''
        count += 1
    # 'rr 09/25/02
    if count == 2:  # delims[0] is always the single-line delim.
        delims[2] = delims[1]
        delims[1] = delims[0]
        delims[0] = ''
    for i in range(0, 3):
        if delims[i]:
            if delims[i].startswith("@0x"):
                # Allow delimiter definition as @0x + hexadecimal encoded delimiter
                # to avoid problems with duplicate delimiters on the @comment line.
                # If used, whole delimiter must be encoded.
                if len(delims[i]) == 3:
                    g.warning(f"'{delims[i]}' delimiter is invalid")
                    return None, None, None
                try:
                    delims[i] = binascii.unhexlify(delims[i][3:])
                    delims[i] = g.toUnicode(delims[i])
                except Exception as e:
                    g.warning(f"'{delims[i]}' delimiter is invalid: {e}")
                    return None, None, None
            else:
                # 7/8/02: The "REM hack": replace underscores by blanks.
                # 9/25/02: The "perlpod hack": replace double underscores by newlines.
                delims[i] = delims[i].replace("__", '\n').replace('_', ' ')
    return delims[0], delims[1], delims[2]
#@+node:ekr.20031218072017.1384: *3* g.set_language
def set_language(s, i, issue_errors_flag=False):
    """Scan the @language directive that appears at s[i:].

    The @language may have been stripped away.

    Returns (language, delim1, delim2, delim3)
    """
    tag = "@language"
    assert(i is not None)
    if g.match_word(s, i, tag):
        i += len(tag)
    # Get the argument.
    i = g.skip_ws(s, i)
    j = i; i = g.skip_c_id(s, i)
    # Allow tcl/tk.
    arg = s[j:i].lower()
    if app.language_delims_dict.get(arg):
        language = arg
        delim1, delim2, delim3 = g.set_delims_from_language(language)
        return language, delim1, delim2, delim3
    if issue_errors_flag:
        g.es("ignoring:", g.get_line(s, i))
    return None, None, None, None
#@+node:ekr.20081001062423.9: *3* g.setDefaultDirectory & helper
def setDefaultDirectory(c, p, importing=False):
    """ Return a default directory by scanning @path directives."""
    if p:
        name = p.anyAtFileNodeName()
        if name:
            # An absolute path overrides everything.
            d = g.os_path_dirname(name)
            if d and g.os_path_isabs(d):
                return d
        aList = g.get_directives_dict_list(p)
        path = c.scanAtPathDirectives(aList)
            # Returns g.getBaseDirectory(c) by default.
            # However, g.getBaseDirectory can return ''
    else:
        path = None
    if path:
        path = g.os_path_finalize(path)
    else:
        g.checkOpenDirectory(c)
        for d in (c.openDirectory, g.getBaseDirectory(c)):
            # Errors may result in relative or invalid path.
            if d and g.os_path_isabs(d):
                path = d
                break
        else:
            path = ''
    if not importing and not path:
        # This should never happen, but is not serious if it does.
        g.warning("No absolute directory specified anywhere.")
    return path
#@+node:ekr.20101022124309.6132: *4* g.checkOpenDirectory
def checkOpenDirectory(c):
    if c.openDirectory != c.frame.openDirectory:
        g.error(
            f"Error: c.openDirectory != c.frame.openDirectory\n"
            f"c.openDirectory: {c.openDirectory}\n"
            f"c.frame.openDirectory: {c.frame.openDirectory}")
    if not g.os_path_isabs(c.openDirectory):
        g.error(f"Error: relative c.openDirectory: {c.openDirectory}")
#@+node:ekr.20071109165315: *3* g.stripPathCruft
def stripPathCruft(path):
    """Strip cruft from a path name."""
    if not path:
        return path  # Retain empty paths for warnings.
    if len(path) > 2 and (
        (path[0] == '<' and path[-1] == '>') or
        (path[0] == '"' and path[-1] == '"') or
        (path[0] == "'" and path[-1] == "'")
    ):
        path = path[1:-1].strip()
    # We want a *relative* path, not an absolute path.
    return path
#@+node:ekr.20090214075058.10: *3* g.update_directives_pat (new)
def update_directives_pat():
    """Init/update g.directives_pat"""
    global globalDirectiveList, directives_pat
    # Use a pattern that guarantees word matches.
    aList = [
        fr"\b{z}\b" for z in globalDirectiveList if z != 'others'
    ]
    pat = f"^@(%s)" % "|".join(aList)
    directives_pat = re.compile(pat, re.MULTILINE)

# #1688: Initialize g.directives_pat
update_directives_pat()
#@+node:ekr.20031218072017.3116: ** g.Files & Directories
#@+node:ekr.20080606074139.2: *3* g.chdir
def chdir(path):
    if not g.os_path_isdir(path):
        path = g.os_path_dirname(path)
    if g.os_path_isdir(path) and g.os_path_exists(path):
        os.chdir(path)
#@+node:ekr.20120222084734.10287: *3* g.compute...Dir
# For compatibility with old code.

def computeGlobalConfigDir():
    return g.app.loadManager.computeGlobalConfigDir()

def computeHomeDir():
    return g.app.loadManager.computeHomeDir()

def computeLeoDir():
    return g.app.loadManager.computeLeoDir()

def computeLoadDir():
    return g.app.loadManager.computeLoadDir()

def computeMachineName():
    return g.app.loadManager.computeMachineName()

def computeStandardDirectories():
    return g.app.loadManager.computeStandardDirectories()
#@+node:ekr.20031218072017.3103: *3* g.computeWindowTitle
def computeWindowTitle(fileName):

    branch, commit = g.gitInfoForFile(fileName)  # #1616
    if not fileName:
        return branch + ": untitled" if branch else 'untitled'
    path, fn = g.os_path_split(fileName)
    if path:
        title = fn + " in " + path
    else:
        title = fn
    # Yet another fix for bug 1194209: regularize slashes.
    if os.sep in '/\\':
        title = title.replace('/', os.sep).replace('\\', os.sep)
    if branch:
        title = branch + ": " + title
    return title
#@+node:ekr.20031218072017.3117: *3* g.create_temp_file
def create_temp_file(textMode=False):
    """
    Return a tuple (theFile,theFileName)

    theFile: a file object open for writing.
    theFileName: the name of the temporary file.
    """
    try:
        # fd is an handle to an open file as would be returned by os.open()
        fd, theFileName = tempfile.mkstemp(text=textMode)
        mode = 'w' if textMode else 'wb'
        theFile = os.fdopen(fd, mode)
    except Exception:
        g.error('unexpected exception in g.create_temp_file')
        g.es_exception()
        theFile, theFileName = None, ''
    return theFile, theFileName
#@+node:vitalije.20170714085545.1: *3* g.defaultLeoFileExtension
def defaultLeoFileExtension(c=None):
    conf = c.config if c else g.app.config
    return conf.getString('default-leo-extension') or '.leo'
#@+node:ekr.20031218072017.3118: *3* g.ensure_extension
def ensure_extension(name, ext):

    theFile, old_ext = g.os_path_splitext(name)
    if not name:
        return name  # don't add to an empty name.
    if old_ext in ('.db', '.leo'):
        return name
    if old_ext and old_ext == ext:
        return name
    return name + ext
#@+node:ekr.20150403150655.1: *3* g.fullPath
def fullPath(c, p, simulate=False):
    """
    Return the full path (including fileName) in effect at p. Neither the
    path nor the fileName will be created if it does not exist.
    """
    # Search p and p's parents.
    for p in p.self_and_parents(copy=False):
        aList = g.get_directives_dict_list(p)
        path = c.scanAtPathDirectives(aList)
        fn = p.h if simulate else p.anyAtFileNodeName()
            # Use p.h for unit tests.
        if fn:
            # Fix #102: expand path expressions.
            fn = c.expand_path_expression(fn)  # #1341.
            return g.os_path_finalize_join(path, fn)  # #1341.
    return ''
#@+node:ekr.20190327192721.1: *3* g.get_files_in_directory
def get_files_in_directory(directory, kinds=None, recursive=True):
    """
    Return a list of all files of the given file extensions in the directory.
    Default kinds: ['*.py'].
    """
    files, sep = [], os.path.sep
    if not g.os.path.exists(directory):
        g.es_print('does not exist', directory)
        return files
    try:
        if kinds:
            kinds = [z if z.startswith('*') else '*' + z for z in kinds]
        else:
            kinds = ['*.py']
        if recursive:
            # Works for all versions of Python.
            
            # Transcrypt does not support Python's copy module.
            # __pragma__ ('skip')
        
            import fnmatch
            for root, dirnames, filenames in os.walk(directory):
                for kind in kinds:
                    for filename in fnmatch.filter(filenames, kind):
                        files.append(os.path.join(root, filename))

            # __pragma__ ('noskip')

        else:
            for kind in kinds:
                files.extend(glob.glob(directory + sep + kind))
        return list(set(sorted(files)))
    except Exception:
        g.es_exception()
        return []
#@+node:ekr.20031218072017.1264: *3* g.getBaseDirectory
# Handles the conventions applying to the "relative_path_base_directory" configuration option.

def getBaseDirectory(c):
    """Convert '!' or '.' to proper directory references."""
    base = app.config.relative_path_base_directory
    if base and base == "!":
        base = app.loadDir
    elif base and base == ".":
        base = c.openDirectory
    if base and g.os_path_isabs(base):
        # Set c.chdir_to_relative_path as needed.
        if not hasattr(c, 'chdir_to_relative_path'):
            c.chdir_to_relative_path = c.config.getBool('chdir-to-relative-path')
        # Call os.chdir if requested.
        if c.chdir_to_relative_path:
            os.chdir(base)
        return base  # base need not exist yet.
    return ""  # No relative base given.
#@+node:ekr.20170223093758.1: *3* g.getEncodingAt
def getEncodingAt(p, s=None):
    """
    Return the encoding in effect at p and/or for string s.

    Read logic:  s is not None.
    Write logic: s is None.
    """
    # A BOM overrides everything.
    if s:
        e, junk_s = g.stripBOM(s)
        if e:
            return e
    aList = g.get_directives_dict_list(p)
    e = g.scanAtEncodingDirectives(aList)
    if s and s.strip() and not e:
        e = 'utf-8'
    return e
#@+node:ville.20090701144325.14942: *3* g.guessExternalEditor
def guessExternalEditor(c=None):
    """ Return a 'sensible' external editor """
    editor = (
        os.environ.get("LEO_EDITOR") or
        os.environ.get("EDITOR") or
        g.app.db and g.app.db.get("LEO_EDITOR") or
        c and c.config.getString('external-editor'))
    if editor: return editor
    # fallbacks
    platform = sys.platform.lower()
    if platform.startswith('win'):
        return "notepad"
    if platform.startswith('linux'):
        return 'gedit'
    g.es(
        '''No editor set.
Please set LEO_EDITOR or EDITOR environment variable,
or do g.app.db['LEO_EDITOR'] = "gvim"''',
    )
    return None
#@+node:ekr.20160330204014.1: *3* g.init_dialog_folder
def init_dialog_folder(c, p, use_at_path=True):
    """Return the most convenient folder to open or save a file."""
    if c and p and use_at_path:
        path = g.fullPath(c, p)
        if path:
            dir_ = g.os_path_dirname(path)
            if dir_ and g.os_path_exists(dir_):
                return dir_
    table = (
        ('c.last_dir', c and c.last_dir),
        ('os.curdir', g.os_path_abspath(os.curdir)),
    )
    for kind, dir_ in table:
        if dir_ and g.os_path_exists(dir_):
            return dir_
    return ''
#@+node:ekr.20100329071036.5744: *3* g.is_binary_file/external_file/string
def is_binary_file(f):
    return f and isinstance(f, io.BufferedIOBase)

def is_binary_external_file(fileName):
    try:
        with open(fileName, 'rb') as f:
            s = f.read(1024)  # bytes, in Python 3.
        return g.is_binary_string(s)
    except IOError:
        return False
    except Exception:
        g.es_exception()
        return False

def is_binary_string(s):
    # http://stackoverflow.com/questions/898669
    # aList is a list of all non-binary characters.
    aList = [7, 8, 9, 10, 12, 13, 27] + list(range(0x20, 0x100))
    aList = bytes(aList)
    return bool(s.translate(None, aList))
#@+node:EKR.20040504154039: *3* g.is_sentinel
def is_sentinel(line, delims):
    """Return True if line starts with a sentinel comment."""
    delim1, delim2, delim3 = delims
    line = line.lstrip()
    if delim1:
        return line.startswith(delim1 + '@')
    if delim2 and delim3:
        i = line.find(delim2 + '@')
        j = line.find(delim3)
        return 0 == i < j
    g.error(f"is_sentinel: can not happen. delims: {repr(delims)}")
    return False
#@+node:ekr.20031218072017.3119: *3* g.makeAllNonExistentDirectories
def makeAllNonExistentDirectories(theDir):
    """
    A wrapper from os.makedirs.
    Attempt to make all non-existent directories.

    Return True if the directory exists or was created successfully.
    """
    # Return True if the directory already exists.
    theDir = g.os_path_normpath(theDir)
    ok = g.os_path_isdir(theDir) and g.os_path_exists(theDir)
    if ok:
        return theDir
    # #1450: Create the directory with os.makedirs.
    try:
        os.makedirs(theDir, mode=0o777, exist_ok=False)
        return theDir
    except Exception:
        return None
#@+node:ekr.20071114113736: *3* g.makePathRelativeTo
def makePathRelativeTo(fullPath, basePath):
    if fullPath.startswith(basePath):
        s = fullPath[len(basePath) :]
        if s.startswith(os.path.sep):
            s = s[len(os.path.sep) :]
        return s
    return fullPath
#@+node:ekr.20090520055433.5945: *3* g.openWithFileName
def openWithFileName(fileName, old_c=None, gui=None):
    """Create a Leo Frame for the indicated fileName if the file exists.

    returns the commander of the newly-opened outline.
    """
    return g.app.loadManager.loadLocalFile(fileName, gui, old_c)
#@+node:ekr.20150306035851.7: *3* g.readFileIntoEncodedString
def readFileIntoEncodedString(fn, silent=False):
    """Return the raw contents of the file whose full path is fn."""
    try:
        with open(fn, 'rb') as f:
            return f.read()
    except IOError:
        if not silent:
            g.error('can not open', fn)
    except Exception:
        if not silent:
            g.error(f"readFileIntoEncodedString: exception reading {fn}")
            g.es_exception()
    return None
#@+node:ekr.20100125073206.8710: *3* g.readFileIntoString
def readFileIntoString(fileName,
    encoding='utf-8',  # BOM may override this.
    kind=None,  # @file, @edit, ...
    verbose=True,
):
    """
    Return the contents of the file whose full path is fileName.

    Return (s,e)
    s is the string, converted to unicode, or None if there was an error.
    e is the encoding of s, computed in the following order:
    - The BOM encoding if the file starts with a BOM mark.
    - The encoding given in the # -*- coding: utf-8 -*- line for python files.
    - The encoding given by the 'encoding' keyword arg.
    - None, which typically means 'utf-8'.
    """
    if not fileName:
        if verbose: g.trace('no fileName arg given')
        return None, None
    if g.os_path_isdir(fileName):
        if verbose: g.trace('not a file:', fileName)
        return None, None
    if not g.os_path_exists(fileName):
        if verbose: g.error('file not found:', fileName)
        return None, None
    try:
        e = None
        with open(fileName, 'rb') as f:
            s = f.read()
        # Fix #391.
        if not s:
            return '', None
        # New in Leo 4.11: check for unicode BOM first.
        e, s = g.stripBOM(s)
        if not e:
            # Python's encoding comments override everything else.
            junk, ext = g.os_path_splitext(fileName)
            if ext == '.py':
                e = g.getPythonEncodingFromString(s)
        s = g.toUnicode(s, encoding=e or encoding)
        return s, e
    except IOError:
        # Translate 'can not open' and kind, but not fileName.
        if verbose:
            g.error('can not open', '', (kind or ''), fileName)
    except Exception:
        g.error(f"readFileIntoString: unexpected exception reading {fileName}")
        g.es_exception()
    return None, None
#@+node:ekr.20160504062833.1: *3* g.readFileToUnicodeString
def readFileIntoUnicodeString(fn, encoding=None, silent=False):
    """Return the raw contents of the file whose full path is fn."""
    try:
        with open(fn, 'rb') as f:
            s = f.read()
        return g.toUnicode(s, encoding=encoding)
    except IOError:
        if not silent:
            g.error('can not open', fn)
    except Exception:
        g.error(f"readFileIntoUnicodeString: unexpected exception reading {fn}")
        g.es_exception()
    return None
#@+node:ekr.20031218072017.3120: *3* g.readlineForceUnixNewline
#@+at Stephen P. Schaefer 9/7/2002
#
# The Unix readline() routine delivers "\r\n" line end strings verbatim,
# while the windows versions force the string to use the Unix convention
# of using only "\n". This routine causes the Unix readline to do the
# same.
#@@c

def readlineForceUnixNewline(f, fileName=None):
    try:
        s = f.readline()
    except UnicodeDecodeError:
        g.trace(f"UnicodeDecodeError: {fileName}", f, g.callers())
        s = ''
    if len(s) >= 2 and s[-2] == "\r" and s[-1] == "\n":
        s = s[0:-2] + "\n"
    return s
#@+node:ekr.20031218072017.3124: *3* g.sanitize_filename
def sanitize_filename(s):
    """
    Prepares string s to be a valid file name:

    - substitute '_' for whitespace and special path characters.
    - eliminate all other non-alphabetic characters.
    - convert double quotes to single quotes.
    - strip leading and trailing whitespace.
    - return at most 128 characters.
    """
    result = []
    for ch in s:
        if ch in string.ascii_letters:
            result.append(ch)
        elif ch == '\t':
            result.append(' ')
        elif ch == '"':
            result.append("'")
        elif ch in '\\/:|<>*:._':
            result.append('_')
    s = ''.join(result).strip()
    while len(s) > 1:
        n = len(s)
        s = s.replace('__', '_')
        if len(s) == n:
            break
    return s[:128]
#@+node:ekr.20060328150113: *3* g.setGlobalOpenDir
def setGlobalOpenDir(fileName):
    if fileName:
        g.app.globalOpenDir = g.os_path_dirname(fileName)
        # g.es('current directory:',g.app.globalOpenDir)
#@+node:ekr.20031218072017.3125: *3* g.shortFileName & shortFilename
def shortFileName(fileName, n=None):
    """Return the base name of a path."""
    if n is not None:
        g.trace('"n" keyword argument is no longer used')
    return g.os_path_basename(fileName) if fileName else ''

shortFilename = shortFileName
#@+node:ekr.20150610125813.1: *3* g.splitLongFileName
def splitLongFileName(fn, limit=40):
    """Return fn, split into lines at slash characters."""
    aList = fn.replace('\\', '/').split('/')
    n, result = 0, []
    for i, s in enumerate(aList):
        n += len(s)
        result.append(s)
        if i + 1 < len(aList):
            result.append('/')
            n += 1
        if n > limit:
            result.append('\n')
            n = 0
    return ''.join(result)
#@+node:ekr.20050104135720: *3* g.Used by tangle code & leoFileCommands
#@+node:ekr.20050104123726.3: *4* g.utils_remove
def utils_remove(fileName, verbose=True):
    try:
        os.remove(fileName)
        return True
    except Exception:
        if verbose:
            g.es("exception removing:", fileName)
            g.es_exception()
        return False
#@+node:ekr.20031218072017.1263: *4* g.utils_rename
def utils_rename(c, src, dst, verbose=True):
    """Platform independent rename."""
    # Don't call g.makeAllNonExistentDirectories here!
    try:
        shutil.move(src, dst)
        return True
    except Exception:
        if verbose:
            g.error('exception renaming', src, 'to', dst)
            g.es_exception(full=False)
        return False
#@+node:ekr.20050104124903: *4* g.utils_chmod
def utils_chmod(fileName, mode, verbose=True):
    if mode is None:
        return
    try:
        os.chmod(fileName, mode)
    except Exception:
        if verbose:
            g.es("exception in os.chmod", fileName)
            g.es_exception()
#@+node:ekr.20050104123726.4: *4* g.utils_stat
def utils_stat(fileName):
    """Return the access mode of named file, removing any setuid, setgid, and sticky bits."""
    try:
        mode = (os.stat(fileName))[0] & (7 * 8 * 8 + 7 * 8 + 7)  # 0777
    except Exception:
        mode = None
    return mode
#@+node:ekr.20190114061452.26: *3* g.writeFile
def writeFile(contents, encoding, fileName):
    """Create a file with the given contents."""
    try:
        if g.isUnicode(contents):
            contents = g.toEncodedString(contents, encoding=encoding)
        # 'wb' preserves line endings.
        with open(fileName, 'wb') as f:
            f.write(contents)
        return True
    except Exception as e:
        print(f"exception writing: {fileName}:\n{e}")
        # g.trace(g.callers())
        # g.es_exception()
        return False
#@+node:ekr.20031218072017.3151: ** g.Finding & Scanning
#@+node:ekr.20140602083643.17659: *3* g.find_word
def find_word(s, word, i=0):
    """
    Return the index of the first occurance of word in s, or -1 if not found.

    g.find_word is *not* the same as s.find(i,word);
    g.find_word ensures that only word-matches are reported.
    """
    while i < len(s):
        progress = i
        i = s.find(word, i)
        if i == -1:
            return -1
        # Make sure we are at the start of a word.
        if i > 0:
            ch = s[i - 1]
            if ch == '_' or ch.isalnum():
                i += len(word)
                continue
        if g.match_word(s, i, word):
            return i
        i += len(word)
        assert progress < i
    return -1
#@+node:ekr.20170220103251.1: *3* g.findRootsWithPredicate
def findRootsWithPredicate(c, root, predicate=None):
    """
    Commands often want to find one or more **roots**, given a position p.
    A root is the position of any node matching a predicate.

    This function formalizes the search order used by the black,
    pylint, pyflakes and the rst3 commands, returning a list of zero
    or more found roots.
    """
    seen = []
    roots = []
    if predicate is None:

        # A useful default predicate for python.
        # pylint: disable=function-redefined

        def predicate(p):
            return p.isAnyAtFileNode() and p.h.strip().endswith('.py')

    # 1. Search p's tree.
    for p in root.self_and_subtree(copy=False):
        if predicate(p) and p.v not in seen:
            seen.append(p.v)
            roots.append(p.copy())
    if roots:
        return roots
    # 2. Look up the tree.
    for p in root.parents():
        if predicate(p):
            return [p.copy()]
    # 3. Expand the search if root is a clone.
    clones = []
    for p in root.self_and_parents(copy=False):
        if p.isCloned():
            clones.append(p.v)
    if clones:
        for p in c.all_positions(copy=False):
            if predicate(p):
                # Match if any node in p's tree matches any clone.
                for p2 in p.self_and_subtree():
                    if p2.v in clones:
                        return [p.copy()]
    return []
#@+node:tbrown.20140311095634.15188: *3* g.recursiveUNLSearch & helper
def recursiveUNLSearch(unlList, c, depth=0, p=None, maxdepth=0, maxp=None,
                       soft_idx=False, hard_idx=False):
    """try and move to unl in the commander c

    All parameters passed on to recursiveUNLFind(), see that for docs.

    NOTE: maxdepth is max depth seen in recursion so far, not a limit on
          how far we will recurse.  So it should default to 0 (zero).
    """
    if g.unitTesting:
        g.app.unitTestDict['g.recursiveUNLSearch'] = True
        return True, maxdepth, maxp

    def moveToP(c, p, unlList):
        # Process events, to calculate new sizes.
        g.app.gui.qtApp.processEvents()
        c.expandAllAncestors(p)
        c.selectPosition(p)
        nth_sib, nth_same, nth_line_no, nth_col_no = recursiveUNLParts(unlList[-1])
        if nth_line_no:
            if nth_line_no < 0:
                c.goToLineNumber(-nth_line_no)
                if nth_col_no:
                    pos = c.frame.body.wrapper.getInsertPoint() + nth_col_no
                    c.frame.body.wrapper.setInsertPoint(pos)
            else:
                pos = sum(len(i) + 1 for i in p.b.split('\n')[: nth_line_no - 1])
                if nth_col_no:
                    pos += nth_col_no
                c.frame.body.wrapper.setInsertPoint(pos)
        if p.hasChildren():
            p.expand()
        c.redraw()
        c.frame.bringToFront()
        c.bodyWantsFocusNow()
    
    found, maxdepth, maxp = recursiveUNLFind(
        unlList, c, depth, p, maxdepth, maxp, soft_idx=soft_idx, hard_idx=hard_idx)
    if maxp:
        moveToP(c, maxp, unlList)
    return found, maxdepth, maxp
#@+node:ekr.20140711071454.17654: *4* g.recursiveUNLFind
def recursiveUNLFind(unlList, c, depth=0, p=None, maxdepth=0, maxp=None,
                     soft_idx=False, hard_idx=False):
    """
    Internal part of recursiveUNLSearch which doesn't change the
    selected position or call c.frame.bringToFront()

    returns found, depth, p, where:

        - found is True if a full match was found
        - depth is the depth of the best match
        - p is the position of the best match

    NOTE: maxdepth is max depth seen in recursion so far, not a limit on
          how far we will recurse.  So it should default to 0 (zero).

    - `unlList`: list of 'headline', 'headline:N', or 'headline:N,M'
      elements, where N is the node's position index and M the zero based
      count of like named nodes, eg. 'foo:2', 'foo:4,1', 'foo:12,3'
    - `c`: outline
    - `soft_idx`: use index when matching name not found
    - `hard_idx`: use only indexes, ignore node names
    - `depth`: part of recursion, don't set explicitly
    - `p`: part of recursion, don't set explicitly
    - `maxdepth`: part of recursion, don't set explicitly
    - `maxp`: part of recursion, don't set explicitly
    """
    if depth == 0:
        nds = list(c.rootPosition().self_and_siblings())
        unlList = [i.replace('--%3E', '-->') for i in unlList if i.strip()]
        # drop empty parts so "-->node name" works
    else:
        nds = list(p.children())
    heads = [i.h for i in nds]
    # work out order in which to try nodes
    order = []
    nth_sib = nth_same = nth_line_no = nth_col_no = None
    try:
        target = unlList[depth]
    except IndexError:
        target = ''
    try:
        target = g_pos_pattern.sub('', unlList[depth])
        nth_sib, nth_same, nth_line_no, nth_col_no = recursiveUNLParts(unlList[depth])
        pos = nth_sib is not None
    except IndexError:
        # #36.
        pos = False
    if pos:
        use_idx_mode = True  # ok to use hard/soft_idx
        target = re.sub(g_pos_pattern, "", target).replace('--%3E', '-->')
        if hard_idx:
            if nth_sib < len(heads):
                order.append(nth_sib)
        else:
            # First we try the nth node with same header
            if nth_same:
                nths = [n for n, i in enumerate(heads) if i == target]
                if nth_same < len(nths) and heads[nths[nth_same]] == target:
                    order.append(nths[nth_same])
            # Then we try *all* other nodes with same header
            order += [n for n, s in enumerate(heads)
                        if n not in order and s == target]
            # Then position based, if requested
            if soft_idx and nth_sib < len(heads):
                order.append(nth_sib)
    elif hard_idx:
        pass  # hard_idx mode with no idx in unl, go with empty order list
    else:
        order = range(len(nds))
        target = target.replace('--%3E', '-->')
        use_idx_mode = False  # not ok to use hard/soft_idx
        # note, the above also fixes calling with soft_idx=True and an old UNL

    for ndi in order:
        nd = nds[ndi]
        if (
            target == nd.h or
            (use_idx_mode and (soft_idx or hard_idx) and ndi == nth_sib)
        ):
            if depth + 1 == len(unlList):  # found it
                return True, maxdepth, nd
            if maxdepth < depth + 1:
                maxdepth = depth + 1
                maxp = nd.copy()
            found, maxdepth, maxp = g.recursiveUNLFind(
                unlList, c, depth + 1, nd,
                maxdepth, maxp, soft_idx=soft_idx, hard_idx=hard_idx)
            if found:
                return found, maxdepth, maxp
            # else keep looking through nds
    if depth == 0 and maxp:  # inexact match
        g.es('Partial UNL match')
    if soft_idx and depth + 2 < len(unlList):
        aList = []
        for p in c.all_unique_positions():
            if any([p.h.replace('--%3E', '-->') in unl for unl in unlList]):
                aList.append((p.copy(), p.get_UNL(False, False, True)))
        maxcount = 0
        singleMatch = True
        for iter_unl in aList:
            count = 0
            compare_list = unlList[:]
            for header in reversed(iter_unl[1].split('-->')):
                if (re.sub(g_pos_pattern, "", header).replace('--%3E', '-->') ==
                     compare_list[-1]
                ):
                    count = count + 1
                    compare_list.pop(-1)
                else:
                    break
            if count > maxcount:
                p = iter_unl[0]
                singleMatch = True
            elif count == maxcount:
                singleMatch = False
        if maxcount and singleMatch:
            maxp = p
            maxdepth = p.level()
    return False, maxdepth, maxp
#@+node:tbrown.20171221094755.1: *4* g.recursiveUNLParts
def recursiveUNLParts(text):
    """recursiveUNLParts - return index, occurence, line_number, col_number
    from an UNL fragment.  line_number is allowed to be negative to indicate
    a "global" line number within the file.

    :param str text: the fragment, foo or foo:2 or foo:2,0,4,10
    :return: index, occurence, line_number, col_number
    :rtype: (int, int, int, int) or (None, None, None, None)
    """
    pos = re.findall(g_pos_pattern, text)
    if pos:
        return tuple(int(i) if i else 0 for i in pos[0])
    return (None, None, None, None)
#@+node:ekr.20031218072017.3156: *3* g.scanError
# It is dubious to bump the Tangle error count here, but it really doesn't hurt.

def scanError(s):
    """Bump the error count in the tangle command."""
    # New in Leo 4.4b1: just set this global.
    g.app.scanErrors += 1
    g.es('', s)
#@+node:ekr.20031218072017.3157: *3* g.scanf
# A quick and dirty sscanf.  Understands only %s and %d.

def scanf(s, pat):
    count = pat.count("%s") + pat.count("%d")
    pat = pat.replace("%s", r"(\S+)")
    pat = pat.replace("%d", r"(\d+)")
    parts = re.split(pat, s)
    result = []
    for part in parts:
        if part and len(result) < count:
            result.append(part)
    return result
#@+node:ekr.20201127143342.1: *3* g.see_more_lines
def see_more_lines(s, ins, n=4):
    """
    Extend index i within string s to include n more lines.
    """
    # Show more lines, if they exist.
    if n > 0:
        for z in range(n):
            if ins >= len(s):
                break
            i, j = g.getLine(s, ins)
            ins = j
    return max(0, min(ins, len(s)))
#@+node:ekr.20031218072017.3195: *3* g.splitLines & g.joinLines
def splitLines(s):
    """Split s into lines, preserving the number of lines and
    the endings of all lines, including the last line."""
    # g.stat()
    if s:
        return s.splitlines(True)
            # This is a Python string function!
    return []

splitlines = splitLines

def joinLines(aList):
    return ''.join(aList)

joinlines = joinLines
#@+node:ekr.20031218072017.3158: *3* Scanners: calling scanError
#@+at These scanners all call g.scanError() directly or indirectly, so they
# will call g.es if they find an error. g.scanError() also bumps
# c.tangleCommands.errors, which is harmless if we aren't tangling, and
# useful if we are.
#
# These routines are called by the Import routines and the Tangle routines.
#@+node:ekr.20031218072017.3159: *4* skip_block_comment
# Scans past a block comment (an old_style C comment).

def skip_block_comment(s, i):
    assert(g.match(s, i, "/*"))
    j = i; i += 2; n = len(s)
    k = s.find("*/", i)
    if k == -1:
        g.scanError("Run on block comment: " + s[j:i])
        return n
    return k + 2
#@+node:ekr.20031218072017.3160: *4* skip_braces
#@+at This code is called only from the import logic, so we are allowed to
# try some tricks. In particular, we assume all braces are matched in
# if blocks.
#@@c

def skip_braces(s, i):
    """
    Skips from the opening to the matching brace.

    If no matching is found i is set to len(s)
    """
    # start = g.get_line(s,i)
    assert(g.match(s, i, '{'))
    level = 0; n = len(s)
    while i < n:
        c = s[i]
        if c == '{':
            level += 1; i += 1
        elif c == '}':
            level -= 1
            if level <= 0: return i
            i += 1
        elif c == '\'' or c == '"': i = g.skip_string(s, i)
        elif g.match(s, i, '//'): i = g.skip_to_end_of_line(s, i)
        elif g.match(s, i, '/*'): i = g.skip_block_comment(s, i)
        # 7/29/02: be more careful handling conditional code.
        elif (
            g.match_word(s, i, "#if") or
            g.match_word(s, i, "#ifdef") or
            g.match_word(s, i, "#ifndef")
        ):
            i, delta = g.skip_pp_if(s, i)
            level += delta
        else: i += 1
    return i
#@+node:ekr.20031218072017.3162: *4* skip_parens
def skip_parens(s, i):
    """
    Skips from the opening ( to the matching ).

    If no matching is found i is set to len(s).
    """
    level = 0; n = len(s)
    assert g.match(s, i, '('), repr(s[i])
    while i < n:
        c = s[i]
        if c == '(':
            level += 1; i += 1
        elif c == ')':
            level -= 1
            if level <= 0: return i
            i += 1
        elif c == '\'' or c == '"': i = g.skip_string(s, i)
        elif g.match(s, i, "//"): i = g.skip_to_end_of_line(s, i)
        elif g.match(s, i, "/*"): i = g.skip_block_comment(s, i)
        else: i += 1
    return i
#@+node:ekr.20031218072017.3163: *4* skip_pascal_begin_end
def skip_pascal_begin_end(s, i):
    """
    Skips from begin to matching end.
    If found, i points to the end. Otherwise, i >= len(s)
    The end keyword matches begin, case, class, record, and try.
    """
    assert(g.match_c_word(s, i, "begin"))
    level = 1; i = g.skip_c_id(s, i)  # Skip the opening begin.
    while i < len(s):
        ch = s[i]
        if ch == '{':
            i = g.skip_pascal_braces(s, i)
        elif ch == '"' or ch == '\'':
            i = g.skip_pascal_string(s, i)
        elif g.match(s, i, "//"):
            i = g.skip_line(s, i)
        elif g.match(s, i, "(*"):
            i = g.skip_pascal_block_comment(s, i)
        elif g.match_c_word(s, i, "end"):
            level -= 1
            if level == 0:
                return i
            i = g.skip_c_id(s, i)
        elif g.is_c_id(ch):
            j = i; i = g.skip_c_id(s, i); name = s[j:i]
            if name in ["begin", "case", "class", "record", "try"]:
                level += 1
        else:
            i += 1
    return i
#@+node:ekr.20031218072017.3164: *4* skip_pascal_block_comment
# Scans past a pascal comment delimited by (* and *).

def skip_pascal_block_comment(s, i):
    j = i
    assert(g.match(s, i, "(*"))
    i = s.find("*)", i)
    if i > -1:
        return i + 2
    g.scanError("Run on comment" + s[j:i])
    return len(s)
#@+node:ekr.20031218072017.3165: *4* skip_pascal_string : called by tangle
def skip_pascal_string(s, i):
    j = i; delim = s[i]; i += 1
    assert(delim == '"' or delim == '\'')
    while i < len(s):
        if s[i] == delim:
            return i + 1
        i += 1
    g.scanError("Run on string: " + s[j:i])
    return i
#@+node:ekr.20031218072017.3166: *4* skip_heredoc_string : called by php import (Dave Hein)
#@+at 08-SEP-2002 DTHEIN:  added function skip_heredoc_string
# A heredoc string in PHP looks like:
#
#   <<<EOS
#   This is my string.
#   It is mine. I own it.
#   No one else has it.
#   EOS
#
# It begins with <<< plus a token (naming same as PHP variable names).
# It ends with the token on a line by itself (must start in first position.
#@@c

def skip_heredoc_string(s, i):
    j = i
    assert(g.match(s, i, "<<<"))
    m = re.match(r"\<\<\<([a-zA-Z_\x7f-\xff][a-zA-Z0-9_\x7f-\xff]*)", s[i:])
    if m is None:
        i += 3
        return i
    # 14-SEP-2002 DTHEIN: needed to add \n to find word, not just string
    delim = m.group(1) + '\n'
    i = g.skip_line(s, i)  # 14-SEP-2002 DTHEIN: look after \n, not before
    n = len(s)
    while i < n and not g.match(s, i, delim):
        i = g.skip_line(s, i)  # 14-SEP-2002 DTHEIN: move past \n
    if i >= n:
        g.scanError("Run on string: " + s[j:i])
    elif g.match(s, i, delim):
        i += len(delim)
    return i
#@+node:ekr.20031218072017.3167: *4* skip_pp_directive
# Now handles continuation lines and block comments.

def skip_pp_directive(s, i):
    while i < len(s):
        if g.is_nl(s, i):
            if g.escaped(s, i): i = g.skip_nl(s, i)
            else: break
        elif g.match(s, i, "//"): i = g.skip_to_end_of_line(s, i)
        elif g.match(s, i, "/*"): i = g.skip_block_comment(s, i)
        else: i += 1
    return i
#@+node:ekr.20031218072017.3168: *4* skip_pp_if
# Skips an entire if or if def statement, including any nested statements.

def skip_pp_if(s, i):
    start_line = g.get_line(s, i)  # used for error messages.
    assert(
        g.match_word(s, i, "#if") or
        g.match_word(s, i, "#ifdef") or
        g.match_word(s, i, "#ifndef"))
    i = g.skip_line(s, i)
    i, delta1 = g.skip_pp_part(s, i)
    i = g.skip_ws(s, i)
    if g.match_word(s, i, "#else"):
        i = g.skip_line(s, i)
        i = g.skip_ws(s, i)
        i, delta2 = g.skip_pp_part(s, i)
        if delta1 != delta2:
            g.es("#if and #else parts have different braces:", start_line)
    i = g.skip_ws(s, i)
    if g.match_word(s, i, "#endif"):
        i = g.skip_line(s, i)
    else:
        g.es("no matching #endif:", start_line)
    return i, delta1
#@+node:ekr.20031218072017.3169: *4* skip_pp_part
# Skip to an #else or #endif.  The caller has eaten the #if, #ifdef, #ifndef or #else

def skip_pp_part(s, i):

    delta = 0
    while i < len(s):
        c = s[i]
        if (
            g.match_word(s, i, "#if") or
            g.match_word(s, i, "#ifdef") or
            g.match_word(s, i, "#ifndef")
        ):
            i, delta1 = g.skip_pp_if(s, i)
            delta += delta1
        elif g.match_word(s, i, "#else") or g.match_word(s, i, "#endif"):
            return i, delta
        elif c == '\'' or c == '"': i = g.skip_string(s, i)
        elif c == '{':
            delta += 1; i += 1
        elif c == '}':
            delta -= 1; i += 1
        elif g.match(s, i, "//"): i = g.skip_line(s, i)
        elif g.match(s, i, "/*"): i = g.skip_block_comment(s, i)
        else: i += 1
    return i, delta
#@+node:ekr.20031218072017.3170: *4* skip_python_string
def skip_python_string(s, i, verbose=True):
    if g.match(s, i, "'''") or g.match(s, i, '"""'):
        j = i; delim = s[i] * 3; i += 3
        k = s.find(delim, i)
        if k > -1: return k + 3
        if verbose:
            g.scanError("Run on triple quoted string: " + s[j:i])
        return len(s)
    # 2013/09/08: honor the verbose argument.
    return g.skip_string(s, i, verbose=verbose)
#@+node:ekr.20031218072017.2369: *4* skip_string (leoGlobals)
def skip_string(s, i, verbose=True):
    """
    Scan forward to the end of a string.
    New in Leo 4.4.2 final: give error only if verbose is True.
    """
    j = i; delim = s[i]; i += 1
    assert(delim == '"' or delim == '\'')
    n = len(s)
    while i < n and s[i] != delim:
        if s[i] == '\\': i += 2
        else: i += 1
    if i >= n:
        if verbose:
            g.scanError("Run on string: " + s[j:i])
    elif s[i] == delim:
        i += 1
    return i
#@+node:ekr.20031218072017.3171: *4* skip_to_semicolon
# Skips to the next semicolon that is not in a comment or a string.

def skip_to_semicolon(s, i):
    n = len(s)
    while i < n:
        c = s[i]
        if c == ';':
            return i
        if c == '\'' or c == '"':
            i = g.skip_string(s, i)
        elif g.match(s, i, "//"):
            i = g.skip_to_end_of_line(s, i)
        elif g.match(s, i, "/*"):
            i = g.skip_block_comment(s, i)
        else:
            i += 1
    return i
#@+node:ekr.20031218072017.3172: *4* skip_typedef
def skip_typedef(s, i):
    n = len(s)
    while i < n and g.is_c_id(s[i]):
        i = g.skip_c_id(s, i)
        i = g.skip_ws_and_nl(s, i)
    if g.match(s, i, '{'):
        i = g.skip_braces(s, i)
        i = g.skip_to_semicolon(s, i)
    return i
#@+node:ekr.20031218072017.3173: *3* Scanners: no error messages
#@+node:ekr.20031218072017.3174: *4* escaped
# Returns True if s[i] is preceded by an odd number of backslashes.

def escaped(s, i):
    count = 0
    while i - 1 >= 0 and s[i - 1] == '\\':
        count += 1
        i -= 1
    return (count % 2) == 1
#@+node:ekr.20031218072017.3175: *4* find_line_start
def find_line_start(s, i):
    """Return the index in s of the start of the line containing s[i]."""
    if i < 0:
        return 0  # New in Leo 4.4.5: add this defensive code.
    # bug fix: 11/2/02: change i to i+1 in rfind
    i = s.rfind('\n', 0, i + 1)  # Finds the highest index in the range.
    return 0 if i == -1 else i + 1
    # if i == -1: return 0
    # else: return i + 1
#@+node:ekr.20031218072017.3176: *4* find_on_line
def find_on_line(s, i, pattern):
    j = s.find('\n', i)
    if j == -1: j = len(s)
    k = s.find(pattern, i, j)
    return k
#@+node:ekr.20031218072017.3177: *4* is_c_id
def is_c_id(ch):
    return g.isWordChar(ch)
#@+node:ekr.20031218072017.3178: *4* is_nl
def is_nl(s, i):
    return i < len(s) and (s[i] == '\n' or s[i] == '\r')
#@+node:ekr.20031218072017.3179: *4* g.is_special
def is_special(s, directive):
    """Return True if the body text contains the @ directive."""
    assert(directive and directive[0] == '@')
    lws = directive in ("@others", "@all")
        # Most directives must start the line.
    pattern = r'^\s*(%s\b)' if lws else r'^(%s\b)'
    pattern = re.compile(pattern % directive, re.MULTILINE)
    m = re.search(pattern, s)
    if m:
        return True, m.start(1)
    return False, -1
#@+node:ekr.20031218072017.3180: *4* is_ws & is_ws_or_nl
def is_ws(c):
    return c == '\t' or c == ' '

def is_ws_or_nl(s, i):
    return g.is_nl(s, i) or (i < len(s) and g.is_ws(s[i]))
#@+node:ekr.20031218072017.3181: *4* match
# Warning: this code makes no assumptions about what follows pattern.

def match(s, i, pattern):
    return s and pattern and s.find(pattern, i, i + len(pattern)) == i
#@+node:ekr.20031218072017.3182: *4* match_c_word
def match_c_word(s, i, name):
    n = len(name)
    return (
        name and
        name == s[i : i + n] and
        (i + n == len(s) or not g.is_c_id(s[i + n]))
    )
#@+node:ekr.20031218072017.3183: *4* match_ignoring_case
def match_ignoring_case(s1, s2):
    return s1 and s2 and s1.lower() == s2.lower()
#@+node:ekr.20031218072017.3184: *4* g.match_word
def match_word(s, i, pattern):

    # Using a regex is surprisingly tricky.
    if pattern is None:
        return False
    if i > 0 and g.isWordChar(s[i - 1]):  # Bug fix: 2017/06/01.
        return False
    j = len(pattern)
    if j == 0:
        return False
    if s.find(pattern, i, i + j) != i:
        return False
    if i + j >= len(s):
        return True
    ch = s[i + j]
    return not g.isWordChar(ch)
#@+node:ekr.20031218072017.3185: *4* skip_blank_lines
# This routine differs from skip_ws_and_nl in that
# it does not advance over whitespace at the start
# of a non-empty or non-nl terminated line

def skip_blank_lines(s, i):
    while i < len(s):
        if g.is_nl(s, i):
            i = g.skip_nl(s, i)
        elif g.is_ws(s[i]):
            j = g.skip_ws(s, i)
            if g.is_nl(s, j):
                i = j
            else: break
        else: break
    return i
#@+node:ekr.20031218072017.3186: *4* skip_c_id
def skip_c_id(s, i):
    n = len(s)
    while i < n and g.isWordChar(s[i]):
        i += 1
    return i
#@+node:ekr.20040705195048: *4* skip_id
def skip_id(s, i, chars=None):
    chars = g.toUnicode(chars) if chars else ''
    n = len(s)
    while i < n and (g.isWordChar(s[i]) or s[i] in chars):
        i += 1
    return i
#@+node:ekr.20031218072017.3187: *4* skip_line, skip_to_start/end_of_line
#@+at These methods skip to the next newline, regardless of whether the
# newline may be preceeded by a backslash. Consequently, they should be
# used only when we know that we are not in a preprocessor directive or
# string.
#@@c

def skip_line(s, i):
    if i >= len(s):
        return len(s)
    if i < 0: i = 0
    i = s.find('\n', i)
    if i == -1:
        return len(s)
    return i + 1

def skip_to_end_of_line(s, i):
    if i >= len(s):
        return len(s)
    if i < 0: i = 0
    i = s.find('\n', i)
    if i == -1:
        return len(s)
    return i

def skip_to_start_of_line(s, i):
    if i >= len(s):
        return len(s)
    if i <= 0:
        return 0
    # Don't find s[i], so it doesn't matter if s[i] is a newline.
    i = s.rfind('\n', 0, i)
    if i == -1:
        return 0
    return i + 1
#@+node:ekr.20031218072017.3188: *4* skip_long
def skip_long(s, i):
    """
    Scan s[i:] for a valid int.
    Return (i, val) or (i, None) if s[i] does not point at a number.
    """
    val = 0
    i = g.skip_ws(s, i)
    n = len(s)
    if i >= n or (not s[i].isdigit() and s[i] not in '+-'):
        return i, None
    j = i
    if s[i] in '+-':  # Allow sign before the first digit
        i += 1
    while i < n and s[i].isdigit():
        i += 1
    try:  # There may be no digits.
        val = int(s[j:i])
        return i, val
    except Exception:
        return i, None
#@+node:ekr.20031218072017.3190: *4* skip_nl
# We need this function because different systems have different end-of-line conventions.

def skip_nl(s, i):
    """Skips a single "logical" end-of-line character."""
    if g.match(s, i, "\r\n"):
        return i + 2
    if g.match(s, i, '\n') or g.match(s, i, '\r'):
        return i + 1
    return i
#@+node:ekr.20031218072017.3191: *4* skip_non_ws
def skip_non_ws(s, i):
    n = len(s)
    while i < n and not g.is_ws(s[i]):
        i += 1
    return i
#@+node:ekr.20031218072017.3192: *4* skip_pascal_braces
# Skips from the opening { to the matching }.

def skip_pascal_braces(s, i):
    # No constructs are recognized inside Pascal block comments!
    if i == -1:
        return len(s)
    return s.find('}', i)
#@+node:ekr.20031218072017.3193: *4* skip_to_char
def skip_to_char(s, i, ch):
    j = s.find(ch, i)
    if j == -1:
        return len(s), s[i:]
    return j, s[i:j]
#@+node:ekr.20031218072017.3194: *4* skip_ws, skip_ws_and_nl
def skip_ws(s, i):
    n = len(s)
    while i < n and g.is_ws(s[i]):
        i += 1
    return i

def skip_ws_and_nl(s, i):
    n = len(s)
    while i < n and (g.is_ws(s[i]) or g.is_nl(s, i)):
        i += 1
    return i
#@+node:ekr.20170414034616.1: ** g.Git
#@+node:ekr.20180325025502.1: *3* g.backupGitIssues
def backupGitIssues(c, base_url=None):
    """Get a list of issues from Leo's GitHub site."""
    if base_url is None:
        base_url = 'https://api.github.com/repos/leo-editor/leo-editor/issues'

    root = c.lastTopLevel().insertAfter()
    root.h = f'Backup of issues: {time.strftime("%Y/%m/%d")}'
    label_list = []
    GitIssueController().backup_issues(base_url, c, label_list, root)
    root.expand()
    c.selectPosition(root)
    c.redraw()
    g.trace('done')
#@+node:ekr.20170616102324.1: *3* g.execGitCommand
def execGitCommand(command, directory=None):
    """Execute the given git command in the given directory."""
    git_dir = g.os_path_finalize_join(directory, '.git')
    if not g.os_path_exists(git_dir):
        g.trace('not found:', git_dir, g.callers())
        return []
    if '\n' in command:
        g.trace('removing newline from', command)
        command = command.replace('\n', '')
    # #1777: Save/restore os.curdir
    old_dir = os.path.normpath(os.path.abspath(os.curdir))
    if directory:
        os.chdir(directory)
    try:
        p = subprocess.Popen(
            shlex.split(command),
            stdout=subprocess.PIPE,
            stderr=None,  # Shows error traces.
            shell=False,
        )
        out, err = p.communicate()
        lines = [g.toUnicode(z) for z in g.splitLines(out or [])]
    finally:
        os.chdir(old_dir)
    return lines
#@+node:ekr.20180126043905.1: *3* g.getGitIssues
def getGitIssues(c,
    base_url=None,
    label_list=None,
    milestone=None,
    state=None,  # in (None, 'closed', 'open')
):
    """Get a list of issues from Leo's GitHub site."""
    if base_url is None:
        base_url = 'https://api.github.com/repos/leo-editor/leo-editor/issues'
    if isinstance(label_list, (list, tuple)):
        root = c.lastTopLevel().insertAfter()
        root.h = 'Issues for ' + milestone if milestone else 'Backup'
        GitIssueController().backup_issues(base_url, c, label_list, root)
        root.expand()
        c.selectPosition(root)
        c.redraw()
        g.trace('done')
    else:
        g.trace('label_list must be a list or tuple', repr(label_list))
#@+node:ekr.20180126044602.1: *4* class GitIssueController
class GitIssueController:
    """
    A class encapsulating the retrieval of GitHub issues.
    
    The GitHub api: https://developer.github.com/v3/issues/
    """
    #@+others
    #@+node:ekr.20180325023336.1: *5* git.backup_issues
    def backup_issues(self, base_url, c, label_list, root, state=None):

        self.base_url = base_url
        self.root = root
        self.milestone = None
        if label_list:
            for state in ('closed', 'open'):
                for label in label_list:
                    self.get_one_issue(label, state)
        elif state is None:
            for state in ('closed', 'open'):
                organizer = root.insertAsLastChild()
                organizer.h = f"{state} issues..."
                self.get_all_issues(label_list, organizer, state)
        elif state in ('closed', 'open'):
            self.get_all_issues(label_list, root, state)
        else:
            g.es_print('state must be in (None, "open", "closed")')
    #@+node:ekr.20180325024334.1: *5* git.get_all_issues
    def get_all_issues(self, label_list, root, state, limit=100):
        """Get all issues for the base url."""
        # Transcrypt does not support Python's 'requests' module.
        # __pragma__ ('skip')
        import requests
        label = None
        assert state in ('open', 'closed')
        page_url = self.base_url + '?&state=%s&page=%s'
        page, total = 1, 0
        while True:
            url = page_url % (state, page)
            r = requests.get(url)
            try:
                done, n = self.get_one_page(label, page, r, root)
                # Do not remove this trace. It's reassuring.
                g.trace(f"done: {done:5} page: {page:3} found: {n} label: {label}")
            except AttributeError:
                g.trace('Possible rate limit')
                self.print_header(r)
                g.es_exception()
                break
            total += n
            if done:
                break
            page += 1
            if page > limit:
                g.trace('too many pages')
                break
        # __pragma__ ('noskip')
    #@+node:ekr.20180126044850.1: *5* git.get_issues
    def get_issues(self, base_url, label_list, milestone, root, state):
        """Create a list of issues for each label in label_list."""
        self.base_url = base_url
        self.milestone = milestone
        self.root = root
        for label in label_list:
            self.get_one_issue(label, state)
    #@+node:ekr.20180126043719.3: *5* git.get_one_issue
    def get_one_issue(self, label, state, limit=20):
        """Create a list of issues with the given label."""
        import requests
        root = self.root.insertAsLastChild()
        page, total = 1, 0
        page_url = self.base_url + '?labels=%s&state=%s&page=%s'
        while True:
            url = page_url % (label, state, page)
            r = requests.get(url)
            try:
                done, n = self.get_one_page(label, page, r, root)
                # Do not remove this trace. It's reassuring.
                g.trace(f"done: {done:5} page: {page:3} found: {n:3} label: {label}")
            except AttributeError:
                g.trace('Possible rate limit')
                self.print_header(r)
                g.es_exception()
                break
            total += n
            if done:
                break
            page += 1
            if page > limit:
                g.trace('too many pages')
                break
        state = state.capitalize()
        if self.milestone:
            root.h = f"{total} {state} {label} issues for milestone {self.milestone}"
        else:
            root.h = f"{total} {state} {label} issues"
    #@+node:ekr.20180126043719.4: *5* git.get_one_page
    def get_one_page(self, label, page, r, root):

        if self.milestone:
            aList = [
                z for z in r.json()
                    if z.get('milestone') is not None and
                        self.milestone == z.get('milestone').get('title')
            ]
        else:
            aList = [z for z in r.json()]
        for d in aList:
            n, title = d.get('number'), d.get('title')
            html_url = d.get('html_url') or self.base_url
            p = root.insertAsNthChild(0)
            p.h = f"#{n}: {title}"
            p.b = f"{html_url}\n\n"
            p.b += d.get('body').strip()
        link = r.headers.get('Link')
        done = not link or link.find('rel="next"') == -1
        return done, len(aList)
    #@+node:ekr.20180127092201.1: *5* git.print_header
    def print_header(self, r):

        # r.headers is a CaseInsensitiveDict
        # so g.printObj(r.headers) is just repr(r.headers)
        if 0:
            print('Link', r.headers.get('Link'))
        else:
            for key in r.headers:
                print(f"{key:35}: {r.headers.get(key)}")
    #@-others
#@+node:ekr.20190428173354.1: *3* g.getGitVersion
def getGitVersion(directory=None):
    """Return a tuple (author, build, date) from the git log, or None."""
    #
    # -n: Get only the last log.
    trace = 'git' in g.app.debug
    try:
        s = subprocess.check_output(
            'git log -n 1 --date=iso',
            cwd=directory or g.app.loadDir,
            stderr=subprocess.DEVNULL,
            shell=True,
        )
        if trace:
            g.trace(s)
    # #1209.
    except subprocess.CalledProcessError as e:
        s = e.output
        if trace:
            g.trace('return code', e.returncode)
            g.trace('value', repr(s))
            g.es_print('Exception in g.getGitVersion')
            g.es_exception()
        s = g.toUnicode(s)
        if not isinstance(s, str):
            return '', '', ''
    except Exception:
        if trace:
            g.es_print('Exception in g.getGitVersion')
            g.es_exception()
        return '', '', ''

    info = [g.toUnicode(z) for z in s.splitlines()]

    def find(kind):
        """Return the given type of log line."""
        for z in info:
            if z.startswith(kind):
                return z.lstrip(kind).lstrip(':').strip()
        return ''

    return find('Author'), find('commit')[:10], find('Date')
#@+node:ekr.20170414034616.2: *3* g.gitBranchName
def gitBranchName(path=None):
    """
    Return the git branch name associated with path/.git, or the empty
    string if path/.git does not exist. If path is None, use the leo-editor
    directory.
    """
    branch, commit = g.gitInfo(path)
    return branch
#@+node:ekr.20170414034616.4: *3* g.gitCommitNumber
def gitCommitNumber(path=None):
    """
    Return the git commit number associated with path/.git, or the empty
    string if path/.git does not exist. If path is None, use the leo-editor
    directory.
    """
    branch, commit = g.gitInfo(path)
    return commit
#@+node:ekr.20200724132432.1: *3* g.gitInfoForFile
def gitInfoForFile(filename):
    """
    Return the git (branch, commit) info associated for the given file.
    """
    # g.gitInfo and g.gitHeadPath now do all the work.
    return g.gitInfo(filename)
#@+node:ekr.20200724133754.1: *3* g.gitInfoForOutline
def gitInfoForOutline(c):
    """
    Return the git (branch, commit) info associated for commander c.
    """
    return g.gitInfoForFile(c.fileName())
#@+node:maphew.20171112205129.1: *3* g.gitDescribe
def gitDescribe(path=None):
    """
    Return the Git tag, distance-from-tag, and commit hash for the
    associated path. If path is None, use the leo-editor directory.
    
    Given `git describe` cmd line output: `x-leo-v5.6-55-ge1129da\n`
    This function returns ('x-leo-v5.6', '55', 'e1129da')
    """
    describe = g.execGitCommand('git describe --tags --long', path)
    tag, distance, commit = describe[0].rsplit('-', 2)
        # rsplit not split, as '-' might be in tag name
    if 'g' in commit[0:]: commit = commit[1:]
        # leading 'g' isn't part of the commit hash
    commit = commit.rstrip()
    return tag, distance, commit
#@+node:ekr.20170414034616.6: *3* g.gitHeadPath
def gitHeadPath(path):
    """
    Compute the path to .git/HEAD given the path.
    """
    #Transcrypt does not support Python's pathlib module.
    # __pragma__ ('skip')
    from pathlib import Path
    path = Path(path)
    # #1780: Look up the directory tree, looking the .git directory.
    while os.path.exists(path):
        head = os.path.join(path, '.git', 'HEAD')
        if os.path.exists(head):
            return head
        if path == path.parent:
            break
        path = path.parent
    # __pragma__ ('noskip')

    return None
#@+node:ekr.20170414034616.3: *3* g.gitInfo
def gitInfo(path=None):
    """
    Path may be a directory or file.

    Return the branch and commit number or ('', '').
    """
    branch, commit = '', ''  # Set defaults.
    if path is None:
        # Default to leo/core.
        path = os.path.dirname(__file__)
    if not os.path.isdir(path):
        path = os.path.dirname(path)
    # Does path/../ref exist?
    path = g.gitHeadPath(path)
    if not path:
        return branch, commit
    try:
        with open(path) as f:
            s = f.read()
            if not s.startswith('ref'):
                branch = 'None'
                commit = s[:7]
                return branch, commit
        # On a proper branch
        pointer = s.split()[1]
        dirs = pointer.split('/')
        branch = dirs[-1]
    except IOError:
        g.trace('can not open:', path)
        return branch, commit
    # Try to get a better commit number.
    git_dir = g.os_path_finalize_join(path, '..')
    try:
        path = g.os_path_finalize_join(git_dir, pointer)
        with open(path) as f:
            s = f.read()
        commit = s.strip()[0:12]
        # shorten the hash to a unique shortname
    except IOError:
        try:
            path = g.os_path_finalize_join(git_dir, 'packed-refs')
            with open(path) as f:
                for line in f:
                    if line.strip().endswith(' ' + pointer):
                        commit = line.split()[0][0:12]
                        break
        except IOError:
            pass
    return branch, commit
#@+node:ekr.20031218072017.3139: ** g.Hooks & Plugins
#@+node:ekr.20101028131948.5860: *3* g.act_on_node
def dummy_act_on_node(c, p, event):
    pass

# This dummy definition keeps pylint happy.
# Plugins can change this.

act_on_node = dummy_act_on_node
#@+node:ville.20120502221057.7500: *3* g.childrenModifiedSet, g.contentModifiedSet
childrenModifiedSet = set()
contentModifiedSet = set()
#@+node:ekr.20031218072017.1596: *3* g.doHook
def doHook(tag, *args, **keywords):
    """
    This global function calls a hook routine. Hooks are identified by the
    tag param.

    Returns the value returned by the hook routine, or None if the there is
    an exception.

    We look for a hook routine in three places:
    1. c.hookFunction
    2. app.hookFunction
    3. leoPlugins.doPlugins()

    Set app.hookError on all exceptions.
    Scripts may reset app.hookError to try again.
    """
    if g.app.killed or g.app.hookError:
        return None
    if args:
        # A minor error in Leo's core.
        g.pr(f"***ignoring args param.  tag = {tag}")
    if not g.app.config.use_plugins:
        if tag in ('open0', 'start1'):
            g.warning("Plugins disabled: use_plugins is 0 in a leoSettings.leo file.")
        return None
    # Get the hook handler function.  Usually this is doPlugins.
    c = keywords.get("c")
    # pylint: disable=consider-using-ternary
    f = (c and c.hookFunction) or g.app.hookFunction
    if not f:
        g.app.hookFunction = f = g.app.pluginsController.doPlugins
    try:
        # Pass the hook to the hook handler.
        # g.pr('doHook',f.__name__,keywords.get('c'))
        return f(tag, keywords)
    except Exception:
        g.es_exception()
        g.app.hookError = True  # Supress this function.
        g.app.idle_time_hooks_enabled = False
        return None
#@+node:ekr.20100910075900.5950: *3* g.Wrappers for g.app.pluginController methods
# Important: we can not define g.pc here!
#@+node:ekr.20100910075900.5951: *4* g.Loading & registration
def loadOnePlugin(pluginName, verbose=False):
    pc = g.app.pluginsController
    return pc.loadOnePlugin(pluginName, verbose=verbose)

def registerExclusiveHandler(tags, fn):
    pc = g.app.pluginsController
    return pc.registerExclusiveHandler(tags, fn)

def registerHandler(tags, fn):
    pc = g.app.pluginsController
    return pc.registerHandler(tags, fn)

def plugin_signon(module_name, verbose=False):
    pc = g.app.pluginsController
    return pc.plugin_signon(module_name, verbose)

def unloadOnePlugin(moduleOrFileName, verbose=False):
    pc = g.app.pluginsController
    return pc.unloadOnePlugin(moduleOrFileName, verbose)

def unregisterHandler(tags, fn):
    pc = g.app.pluginsController
    return pc.unregisterHandler(tags, fn)
#@+node:ekr.20100910075900.5952: *4* g.Information
def getHandlersForTag(tags):
    pc = g.app.pluginsController
    return pc.getHandlersForTag(tags)

def getLoadedPlugins():
    pc = g.app.pluginsController
    return pc.getLoadedPlugins()

def getPluginModule(moduleName):
    pc = g.app.pluginsController
    return pc.getPluginModule(moduleName)

def pluginIsLoaded(fn):
    pc = g.app.pluginsController
    return pc.isLoaded(fn)
#@+node:ekr.20031218072017.1315: ** g.Idle time functions
#@+node:EKR.20040602125018.1: *3* g.disableIdleTimeHook
def disableIdleTimeHook():
    """Disable the global idle-time hook."""
    g.app.idle_time_hooks_enabled = False
#@+node:EKR.20040602125018: *3* g.enableIdleTimeHook
def enableIdleTimeHook(*args, **keys):
    """Enable idle-time processing."""
    g.app.idle_time_hooks_enabled = True
#@+node:ekr.20140825042850.18410: *3* g.IdleTime
def IdleTime(handler, delay=500, tag=None):
    """
    A thin wrapper for the LeoQtGui.IdleTime class.

    The IdleTime class executes a handler with a given delay at idle time.
    The handler takes a single argument, the IdleTime instance::

        def handler(timer):
            '''IdleTime handler.  timer is an IdleTime instance.'''
            delta_t = timer.time-timer.starting_time
            g.trace(timer.count, '%2.4f' % (delta_t))
            if timer.count >= 5:
                g.trace('done')
                timer.stop()

        # Execute handler every 500 msec. at idle time.
        timer = g.IdleTime(handler,delay=500)
        if timer: timer.start()

    Timer instances are completely independent::

        def handler1(timer):
            delta_t = timer.time-timer.starting_time
            g.trace('%2s %2.4f' % (timer.count,delta_t))
            if timer.count >= 5:
                g.trace('done')
                timer.stop()

        def handler2(timer):
            delta_t = timer.time-timer.starting_time
            g.trace('%2s %2.4f' % (timer.count,delta_t))
            if timer.count >= 10:
                g.trace('done')
                timer.stop()

        timer1 = g.IdleTime(handler1,delay=500)
        timer2 = g.IdleTime(handler2,delay=1000)
        if timer1 and timer2:
            timer1.start()
            timer2.start()
    """
    try:
        return g.app.gui.idleTimeClass(handler, delay, tag)
    except Exception:
        return None
#@+node:ekr.20161027205025.1: *3* g.idleTimeHookHandler (stub)
def idleTimeHookHandler(timer):
    """This function exists for compatibility."""
    g.es_print('Replaced by IdleTimeManager.on_idle')
    g.trace(g.callers())
#@+node:ekr.20041219095213: ** g.Importing
#@+node:ekr.20040917061619: *3* g.cantImport
def cantImport(moduleName, pluginName=None, verbose=True):
    """Print a "Can't Import" message and return None."""
    s = f"Can not import {moduleName}"
    if pluginName: s = s + f" from {pluginName}"
    if not g.app or not g.app.gui:
        print(s)
    elif g.unitTesting:
        # print s
        return
    else:
        g.warning('', s)
#@+node:ekr.20191220044128.1: *3* g.import_module
def import_module(name, package=None):
    """
    A thin wrapper over importlib.import_module.
    """
    trace = True or 'plugins' in g.app.debug
    exceptions = []
    try:
        m = importlib.import_module(name, package=package)
    except Exception as e:
        m = None
        if trace:
            t, v, tb = sys.exc_info()
            del tb  # don't need the traceback
            v = v or str(t)
                # # in case v is empty, we'll at least have the execption type
            if v not in exceptions:
                exceptions.append(v)
                g.trace(f"Can not import {name}: {e}")
    return m
#@+node:ekr.20140711071454.17650: ** g.Indices, Strings, Unicode & Whitespace
#@+node:ekr.20140711071454.17647: *3* g.Indices
#@+node:ekr.20050314140957: *4* g.convertPythonIndexToRowCol
def convertPythonIndexToRowCol(s, i):
    """Convert index i into string s into zero-based row/col indices."""
    if not s or i <= 0:
        return 0, 0
    i = min(i, len(s))
    # works regardless of what s[i] is
    row = s.count('\n', 0, i)  # Don't include i
    if row == 0:
        return row, i
    prevNL = s.rfind('\n', 0, i)  # Don't include i
    return row, i - prevNL - 1
#@+node:ekr.20050315071727: *4* g.convertRowColToPythonIndex
def convertRowColToPythonIndex(s, row, col, lines=None):
    """Convert zero-based row/col indices into a python index into string s."""
    if row < 0: return 0
    if lines is None:
        lines = g.splitLines(s)
    if row >= len(lines):
        return len(s)
    col = min(col, len(lines[row]))
    # A big bottleneck
    prev = 0
    for line in lines[:row]:
        prev += len(line)
    return prev + col
#@+node:ekr.20061031102333.2: *4* g.getWord & getLine
def getWord(s, i):
    """Return i,j such that s[i:j] is the word surrounding s[i]."""
    if i >= len(s): i = len(s) - 1
    if i < 0: i = 0
    # Scan backwards.
    while 0 <= i < len(s) and g.isWordChar(s[i]):
        i -= 1
    i += 1
    # Scan forwards.
    j = i
    while 0 <= j < len(s) and g.isWordChar(s[j]):
        j += 1
    return i, j

def getLine(s, i):
    """
    Return i,j such that s[i:j] is the line surrounding s[i].
    s[i] is a newline only if the line is empty.
    s[j] is a newline unless there is no trailing newline.
    """
    if i > len(s): i = len(s) - 1
    if i < 0: i = 0
    # A newline *ends* the line, so look to the left of a newline.
    j = s.rfind('\n', 0, i)
    if j == -1: j = 0
    else: j += 1
    k = s.find('\n', i)
    if k == -1: k = len(s)
    else: k = k + 1
    return j, k
#@+node:ekr.20111114151846.9847: *4* g.toPythonIndex
def toPythonIndex(s, index):
    """
    Convert index to a Python int.

    index may be a Tk index (x.y) or 'end'.
    """
    if index is None:
        return 0
    if isinstance(index, int):
        return index
    if index == '1.0':
        return 0
    if index == 'end':
        return len(s)
    data = index.split('.')
    if len(data) == 2:
        row, col = data
        row, col = int(row), int(col)
        i = g.convertRowColToPythonIndex(s, row - 1, col)
        return i
    g.trace(f"bad string index: {index}")
    return 0
#@+node:ekr.20150722051946.1: *3* g.List composition (deprecated)
# These functions are deprecated.
# The LeoTidy class in leoBeautify.py shows a much better way.
#@+node:ekr.20150722051946.2: *4* g.flatten_list
def flatten_list(obj):
    """A generator yielding a flattened (concatenated) version of obj."""
    # pylint: disable=no-else-return
    if isinstance(obj, dict) and obj.get('_join_list'):
        # join_list created obj, and ensured that all args are strings.
        indent = obj.get('indent') or ''
        leading = obj.get('leading') or ''
        sep = obj.get('sep') or ''
        trailing = obj.get('trailing') or ''
        aList = obj.get('aList')
        for i, item in enumerate(aList):
            if leading: yield leading
            for s in flatten_list(item):
                if indent and s.startswith('\n'):
                    yield '\n' + indent + s[1:]
                else:
                    yield s
            if sep and i < len(aList) - 1: yield sep
            if trailing: yield trailing
    elif isinstance(obj, (list, tuple)):
        for obj2 in obj:
            for s in flatten_list(obj2):
                yield s
    elif obj:
        if isinstance(obj, str):
            yield obj
        else:
            yield repr(obj)  # Not likely to be useful.
    else:
        pass  # Allow None and empty containers.
#@+node:ekr.20150722051946.3: *4* g.join_list
def join_list(aList, indent='', leading='', sep='', trailing=''):
    """
    Create a dict representing the concatenation of the
    strings in aList, formatted per the keyword args.
    See the HTMLReportTraverser class for many examples.
    """
    if not aList:
        return None
    # These asserts are reasonable.
    assert isinstance(indent, str), indent
    assert isinstance(leading, str), leading
    assert isinstance(sep, str), sep
    assert isinstance(trailing, str), trailing
    if indent or leading or sep or trailing:
        return {
            '_join_list': True,  # Indicate that join_list created this dict.
            'aList': aList,
            'indent': indent, 'leading': leading, 'sep': sep, 'trailing': trailing,
        }
    return aList
#@+node:ekr.20150722051946.4: *4* g.list_to_string
def list_to_string(obj):
    """
    Convert obj (a list of lists) to a single string.

    This function stresses the gc; it will usually be better to
    work with the much smaller strings generated by flatten_list.

    Use this function only in special circumstances, for example,
    when it is known that the resulting string will be small.
    """
    return ''.join([z for z in flatten_list(obj)])
#@+node:ekr.20140526144610.17601: *3* g.Strings
#@+node:ekr.20190503145501.1: *4* g.isascii
def isascii(s):
    # s.isascii() is defined in Python 3.7.
    return all(ord(ch) < 128 for ch in s)
#@+node:ekr.20031218072017.3106: *4* g.angleBrackets & virtual_event_name
def angleBrackets(s):
    """Returns < < s > >"""
    lt = "<<"
    rt = ">>"
    return lt + s + rt

virtual_event_name = angleBrackets
#@+node:ekr.20090516135452.5777: *4* g.ensureLeading/TrailingNewlines
def ensureLeadingNewlines(s, n):
    s = g.removeLeading(s, '\t\n\r ')
    return ('\n' * n) + s

def ensureTrailingNewlines(s, n):
    s = g.removeTrailing(s, '\t\n\r ')
    return s + '\n' * n
#@+node:ekr.20050920084036.4: *4* g.longestCommonPrefix & g.itemsMatchingPrefixInList
def longestCommonPrefix(s1, s2):
    """Find the longest prefix common to strings s1 and s2."""
    prefix = ''
    for ch in s1:
        if s2.startswith(prefix + ch):
            prefix = prefix + ch
        else:
            return prefix
    return prefix

def itemsMatchingPrefixInList(s, aList, matchEmptyPrefix=False):
    """This method returns a sorted list items of aList whose prefix is s.

    It also returns the longest common prefix of all the matches.
    """
    if s:
        pmatches = [a for a in aList if a.startswith(s)]
    elif matchEmptyPrefix:
        pmatches = aList[:]
    else: pmatches = []
    if pmatches:
        pmatches.sort()
        common_prefix = reduce(g.longestCommonPrefix, pmatches)
    else:
        common_prefix = ''
    return pmatches, common_prefix
#@+node:ekr.20090516135452.5776: *4* g.removeLeading/Trailing
# Warning: g.removeTrailingWs already exists.
# Do not change it!

def removeLeading(s, chars):
    """Remove all characters in chars from the front of s."""
    i = 0
    while i < len(s) and s[i] in chars:
        i += 1
    return s[i:]

def removeTrailing(s, chars):
    """Remove all characters in chars from the end of s."""
    i = len(s) - 1
    while i >= 0 and s[i] in chars:
        i -= 1
    i += 1
    return s[:i]
#@+node:ekr.20060410112600: *4* g.stripBrackets
def stripBrackets(s):
    """Strip leading and trailing angle brackets."""
    if s.startswith('<'):
        s = s[1:]
    if s.endswith('>'):
        s = s[:-1]
    return s
#@+node:ekr.20170317101100.1: *4* g.unCamel
def unCamel(s):
    """Return a list of sub-words in camelCased string s."""
    result, word = [], []
    for ch in s:
        if ch.isalpha() and ch.isupper():
            if word: result.append(''.join(word))
            word = [ch]
        elif ch.isalpha():
            word.append(ch)
        elif word:
            result.append(''.join(word))
            word = []
    if word: result.append(''.join(word))
    return result
#@+node:ekr.20031218072017.1498: *3* g.Unicode
#@+node:ekr.20190505052756.1: *4* g.checkUnicode
checkUnicode_dict = {}

def checkUnicode(s, encoding=None):
    """
    Warn when converting bytes. Report *all* errors.
    
    This method is meant to document defensive programming. We don't expect
    these errors, but they might arise as the result of problems in
    user-defined plugins or scripts.
    """
    if isinstance(s, str):
        return s
    tag = 'g.checkUnicode'
    if not isinstance(s, bytes):
        g.error(f"{tag}: unexpected argument: {s!r}")
        return ''
    #
    # Report the unexpected conversion.
    callers = g.callers(1)
    if callers not in checkUnicode_dict:
        g.trace(g.callers())
        g.error(f"\n{tag}: expected unicode. got: {s!r}\n")
        checkUnicode_dict[callers] = True
    #
    # Convert to unicode, reporting all errors.
    if not encoding:
        encoding = 'utf-8'
    try:
        s = s.decode(encoding, 'strict')
    except(UnicodeDecodeError, UnicodeError):
        # https://wiki.python.org/moin/UnicodeDecodeError
        s = s.decode(encoding, 'replace')
        g.trace(g.callers())
        g.error(f"{tag}: unicode error. encoding: {encoding!r}, s:\n{s!r}")
    except Exception:
        g.trace(g.callers())
        g.es_excption()
        g.error(f"{tag}: unexpected error! encoding: {encoding!r}, s:\n{s!r}")
    return s
#@+node:ekr.20100125073206.8709: *4* g.getPythonEncodingFromString
def getPythonEncodingFromString(s):
    """Return the encoding given by Python's encoding line.
    s is the entire file.
    """
    encoding = None
    tag, tag2 = '# -*- coding:', '-*-'
    n1, n2 = len(tag), len(tag2)
    if s:
        # For Python 3.x we must convert to unicode before calling startswith.
        # The encoding doesn't matter: we only look at the first line, and if
        # the first line is an encoding line, it will contain only ascii characters.
        s = g.toUnicode(s, encoding='ascii', reportErrors=False)
        lines = g.splitLines(s)
        line1 = lines[0].strip()
        if line1.startswith(tag) and line1.endswith(tag2):
            e = line1[n1 : -n2].strip()
            if e and g.isValidEncoding(e):
                encoding = e
        elif g.match_word(line1, 0, '@first'):  # 2011/10/21.
            line1 = line1[len('@first') :].strip()
            if line1.startswith(tag) and line1.endswith(tag2):
                e = line1[n1 : -n2].strip()
                if e and g.isValidEncoding(e):
                    encoding = e
    return encoding
#@+node:ekr.20160229070349.2: *4* g.isBytes (deprecated)
def isBytes(s):
    """Return True if s is a bytes type."""
    return isinstance(s, bytes)
#@+node:ekr.20160229070349.3: *4* g.isCallable (deprecated)
def isCallable(obj):
    return hasattr(obj, '__call__')
#@+node:ekr.20160229070429.1: *4* g.isInt (deprecated)
def isInt(obj):
    """Return True if obj is an int or a long."""
    return isinstance(obj, int)
#@+node:ekr.20161223082445.1: *4* g.isList (deprecated)
def isList(s):
    """Return True if s is a list."""
    return isinstance(s, list)
#@+node:ekr.20160229070349.5: *4* g.isString (deprecated)
def isString(s):
    """Return True if s is any string, but not bytes."""
    return isinstance(s, str)
#@+node:ekr.20160229070349.6: *4* g.isUnicode (deprecated)
def isUnicode(s):
    """Return True if s is a unicode string."""
    return isinstance(s, str)
#@+node:ekr.20031218072017.1500: *4* g.isValidEncoding
def isValidEncoding(encoding):
    """Return True if the encooding is valid."""
    if not encoding:
        return False
    if sys.platform == 'cli':
        return True
        
    #Transcrypt does not support Python's codecs module.
    # __pragma__ ('skip')

    try:
        codecs.lookup(encoding)
        return True
    except LookupError:  # Windows
        return False
    except AttributeError:  # Linux
        return False
    except Exception:
        # UnicodeEncodeError
        g.es_print('Please report the following error')
        g.es_exception()
        return False

    # __pragma__ ('noskip')
#@+node:ekr.20061006152327: *4* g.isWordChar & g.isWordChar1
def isWordChar(ch):
    """Return True if ch should be considered a letter."""
    return ch and (ch.isalnum() or ch == '_')

def isWordChar1(ch):
    return ch and (ch.isalpha() or ch == '_')
#@+node:ekr.20130910044521.11304: *4* g.stripBOM
def stripBOM(s):
    """
    If there is a BOM, return (e,s2) where e is the encoding
    implied by the BOM and s2 is the s stripped of the BOM.

    If there is no BOM, return (None,s)

    s must be the contents of a file (a string) read in binary mode.
    """
    table = (
        # Important: test longer bom's first.
        (4, 'utf-32', codecs.BOM_UTF32_BE),
        (4, 'utf-32', codecs.BOM_UTF32_LE),
        (3, 'utf-8', codecs.BOM_UTF8),
        (2, 'utf-16', codecs.BOM_UTF16_BE),
        (2, 'utf-16', codecs.BOM_UTF16_LE),
    )
    if s:
        for n, e, bom in table:
            assert len(bom) == n
            if bom == s[: len(bom)]:
                return e, s[len(bom) :]
    return None, s
#@+node:ekr.20050208093800: *4* g.toEncodedString
def toEncodedString(s, encoding='utf-8', reportErrors=False):
    """Convert unicode string to an encoded string."""
    if not g.isUnicode(s):
        return s
    if not encoding:
        encoding = 'utf-8'
    # These are the only significant calls to s.encode in Leo.
    try:
        s = s.encode(encoding, "strict")
    except UnicodeError:
        s = s.encode(encoding, "replace")
        if reportErrors:
            g.error(f"Error converting {s} from unicode to {encoding} encoding")
    # Tracing these calls directly yields thousands of calls.
    # Never call g.trace here!
        # g.dump_encoded_string(encoding,s)
    return s
#@+node:ekr.20050208093800.1: *4* g.toUnicode
unicode_warnings = {}  # Keys are g.callers.

def toUnicode(s, encoding=None, reportErrors=False):
    """Convert bytes to unicode if necessary."""
    if isinstance(s, str):
        return s
    tag = 'g.toUnicode'
    if not isinstance(s, bytes):
        if not isinstance(s, (NullObject, TracingNullObject)):
            callers = g.callers()
            if callers not in unicode_warnings:
                unicode_warnings[callers] = True
                g.error(f"{tag}: unexpected argument of type {s.__class__.__name__}")
                g.trace(callers)
        return ''
    if not encoding:
        encoding = 'utf-8'
    try:
        s = s.decode(encoding, 'strict')
    except(UnicodeDecodeError, UnicodeError):
        # https://wiki.python.org/moin/UnicodeDecodeError
        s = s.decode(encoding, 'replace')
        if reportErrors:
            g.error(f"{tag}: unicode error. encoding: {encoding!r}, s:\n{s!r}")
            g.trace(g.callers())
    except Exception:
        g.es_exception()
        g.error(f"{tag}: unexpected error! encoding: {encoding!r}, s:\n{s!r}")
        g.trace(g.callers())
    return s
#@+node:ekr.20091206161352.6232: *4* g.u (deprecated)
def u(s):
    """
    Return s, converted to unicode from Qt widgets.
    
    leoQt.py uses this as a stand-in for QString, but all other calls
    to g.u can and should be removed.
    
    Neither Leo's core nor any of Leo's official plugins call this
    method directly.
    """
    return s
#@+node:ekr.20031218072017.3197: *3* g.Whitespace
#@+node:ekr.20031218072017.3198: *4* g.computeLeadingWhitespace
# Returns optimized whitespace corresponding to width with the indicated tab_width.

def computeLeadingWhitespace(width, tab_width):
    if width <= 0:
        return ""
    if tab_width > 1:
        tabs = int(width / tab_width)
        blanks = int(width % tab_width)
        return ('\t' * tabs) + (' ' * blanks)
    # Negative tab width always gets converted to blanks.
    return (' ' * width)
#@+node:ekr.20120605172139.10263: *4* g.computeLeadingWhitespaceWidth
# Returns optimized whitespace corresponding to width with the indicated tab_width.

def computeLeadingWhitespaceWidth(s, tab_width):
    w = 0
    for ch in s:
        if ch == ' ':
            w += 1
        elif ch == '\t':
            w += (abs(tab_width) - (w % abs(tab_width)))
        else:
            break
    return w
#@+node:ekr.20031218072017.3199: *4* g.computeWidth
# Returns the width of s, assuming s starts a line, with indicated tab_width.

def computeWidth(s, tab_width):
    w = 0
    for ch in s:
        if ch == '\t':
            w += (abs(tab_width) - (w % abs(tab_width)))
        elif ch == '\n':  # Bug fix: 2012/06/05.
            break
        else:
            w += 1
    return w
#@+node:ekr.20051014175117: *4* g.adjustTripleString
def adjustTripleString(s, tab_width):
    """Remove leading indentation from a triple-quoted string.

    This works around the fact that Leo nodes can't represent underindented strings.
    """
    # Compute the minimum leading whitespace of all non-blank lines.
    lines = g.splitLines(s)
    first, w = True, 0
    for line in lines:
        if line.strip():
            lws = g.get_leading_ws(line)
            # The sign of w2 does not matter.
            w2 = abs(g.computeWidth(lws, tab_width))
            if w2 == 0:
                return s
            if first or w2 < w:
                w = w2
                first = False
    if w == 0:
        return s
    # Remove the leading whitespace.
    result = [g.removeLeadingWhitespace(line, w, tab_width) for line in lines]
    result = ''.join(result)
    return result
#@+node:ekr.20050211120242.2: *4* g.removeExtraLws
def removeExtraLws(s, tab_width):
    """
    Remove extra indentation from one or more lines.

    Warning: used by getScript. This is *not* the same as g.adjustTripleString.
    """
    lines = g.splitLines(s)
    # Find the first non-blank line and compute w, the width of its leading whitespace.
    for line in lines:
        if line.strip():
            lws = g.get_leading_ws(line)
            w = g.computeWidth(lws, tab_width)
            break
    else: return s
    # Remove the leading whitespace.
    result = [g.removeLeadingWhitespace(line, w, tab_width) for line in lines]
    result = ''.join(result)
    return result
#@+node:ekr.20110727091744.15083: *4* g.wrap_lines (newer)
#@@language rest
#@+at
# Important note: this routine need not deal with leading whitespace.
#
# Instead, the caller should simply reduce pageWidth by the width of
# leading whitespace wanted, then add that whitespace to the lines
# returned here.
#
# The key to this code is the invarient that line never ends in whitespace.
#@@c
#@@language python

def wrap_lines(lines, pageWidth, firstLineWidth=None):
    """Returns a list of lines, consisting of the input lines wrapped to the given pageWidth."""
    if pageWidth < 10:
        pageWidth = 10
    # First line is special
    if not firstLineWidth:
        firstLineWidth = pageWidth
    if firstLineWidth < 10:
        firstLineWidth = 10
    outputLineWidth = firstLineWidth
    # Sentence spacing
    # This should be determined by some setting, and can only be either 1 or 2
    sentenceSpacingWidth = 1
    assert(0 < sentenceSpacingWidth < 3)
    result = []  # The lines of the result.
    line = ""  # The line being formed.  It never ends in whitespace.
    for s in lines:
        i = 0
        while i < len(s):
            assert(len(line) <= outputLineWidth)  # DTHEIN 18-JAN-2004
            j = g.skip_ws(s, i)  # ;   ws = s[i:j]
            k = g.skip_non_ws(s, j); word = s[j:k]
            assert(k > i)
            i = k
            # DTHEIN 18-JAN-2004: wrap at exactly the text width,
            # not one character less
            #
            wordLen = len(word)
            if line.endswith('.') or line.endswith('?') or line.endswith('!'):
                space = ' ' * sentenceSpacingWidth
            else:
                space = ' '
            if line and wordLen > 0: wordLen += len(space)
            if wordLen + len(line) <= outputLineWidth:
                if wordLen > 0:
                    #@+<< place blank and word on the present line >>
                    #@+node:ekr.20110727091744.15084: *5* << place blank and word on the present line >>
                    if line:
                        # Add the word, preceeded by a blank.
                        line = space.join((line, word))
                    else:
                        # Just add the word to the start of the line.
                        line = word
                    #@-<< place blank and word on the present line >>
                else: pass  # discard the trailing whitespace.
            else:
                #@+<< place word on a new line >>
                #@+node:ekr.20110727091744.15085: *5* << place word on a new line >>
                # End the previous line.
                if line:
                    result.append(line)
                    outputLineWidth = pageWidth  # DTHEIN 3-NOV-2002: width for remaining lines
                # Discard the whitespace and put the word on a new line.
                line = word
                # Careful: the word may be longer than pageWidth.
                if len(line) > pageWidth:  # DTHEIN 18-JAN-2004: line can equal pagewidth
                    result.append(line)
                    outputLineWidth = pageWidth  # DTHEIN 3-NOV-2002: width for remaining lines
                    line = ""
                #@-<< place word on a new line >>
    if line:
        result.append(line)
    return result
#@+node:ekr.20031218072017.3200: *4* g.get_leading_ws
def get_leading_ws(s):
    """Returns the leading whitespace of 's'."""
    i = 0; n = len(s)
    while i < n and s[i] in (' ', '\t'):
        i += 1
    return s[0:i]
#@+node:ekr.20031218072017.3201: *4* g.optimizeLeadingWhitespace
# Optimize leading whitespace in s with the given tab_width.

def optimizeLeadingWhitespace(line, tab_width):
    i, width = g.skip_leading_ws_with_indent(line, 0, tab_width)
    s = g.computeLeadingWhitespace(width, tab_width) + line[i:]
    return s
#@+node:ekr.20040723093558: *4* g.regularizeTrailingNewlines
#@+at The caller should call g.stripBlankLines before calling this routine
# if desired.
#
# This routine does _not_ simply call rstrip(): that would delete all
# trailing whitespace-only lines, and in some cases that would change
# the meaning of program or data.
#@@c

def regularizeTrailingNewlines(s, kind):
    """Kind is 'asis', 'zero' or 'one'."""
    pass
#@+node:ekr.20091229090857.11698: *4* g.removeBlankLines
def removeBlankLines(s):
    lines = g.splitLines(s)
    lines = [z for z in lines if z.strip()]
    return ''.join(lines)
#@+node:ekr.20091229075924.6235: *4* g.removeLeadingBlankLines
def removeLeadingBlankLines(s):
    lines = g.splitLines(s)
    result = []; remove = True
    for line in lines:
        if remove and not line.strip():
            pass
        else:
            remove = False
            result.append(line)
    return ''.join(result)
#@+node:ekr.20031218072017.3202: *4* g.removeLeadingWhitespace
# Remove whitespace up to first_ws wide in s, given tab_width, the width of a tab.

def removeLeadingWhitespace(s, first_ws, tab_width):
    j = 0; ws = 0; first_ws = abs(first_ws)
    for ch in s:
        if ws >= first_ws:
            break
        elif ch == ' ':
            j += 1; ws += 1
        elif ch == '\t':
            j += 1; ws += (abs(tab_width) - (ws % abs(tab_width)))
        else: break
    if j > 0:
        s = s[j:]
    return s
#@+node:ekr.20031218072017.3203: *4* g.removeTrailingWs
# Warning: string.rstrip also removes newlines!

def removeTrailingWs(s):
    j = len(s) - 1
    while j >= 0 and (s[j] == ' ' or s[j] == '\t'):
        j -= 1
    return s[: j + 1]
#@+node:ekr.20031218072017.3204: *4* g.skip_leading_ws
# Skips leading up to width leading whitespace.

def skip_leading_ws(s, i, ws, tab_width):
    count = 0
    while count < ws and i < len(s):
        ch = s[i]
        if ch == ' ':
            count += 1
            i += 1
        elif ch == '\t':
            count += (abs(tab_width) - (count % abs(tab_width)))
            i += 1
        else: break
    return i
#@+node:ekr.20031218072017.3205: *4* g.skip_leading_ws_with_indent
def skip_leading_ws_with_indent(s, i, tab_width):
    """Skips leading whitespace and returns (i, indent),

    - i points after the whitespace
    - indent is the width of the whitespace, assuming tab_width wide tabs."""
    count = 0; n = len(s)
    while i < n:
        ch = s[i]
        if ch == ' ':
            count += 1
            i += 1
        elif ch == '\t':
            count += (abs(tab_width) - (count % abs(tab_width)))
            i += 1
        else: break
    return i, count
#@+node:ekr.20040723093558.1: *4* g.stripBlankLines
def stripBlankLines(s):
    lines = g.splitLines(s)
    for i, line in enumerate(lines):
        j = g.skip_ws(line, 0)
        if j >= len(line):
            lines[i] = ''
        elif line[j] == '\n':
            lines[i] = '\n'
    return ''.join(lines)
#@+node:ekr.20031218072017.3108: ** g.Logging & Printing
# g.es and related print to the Log window.
# g.pr prints to the console.
# g.es_print and related print to both the Log window and the console.
#@+node:ekr.20080821073134.2: *3* g.doKeywordArgs
def doKeywordArgs(keys, d=None):
    """
    Return a result dict that is a copy of the keys dict
    with missing items replaced by defaults in d dict.
    """
    if d is None: d = {}
    result = {}
    for key, default_val in d.items():
        isBool = default_val in (True, False)
        val = keys.get(key)
        if isBool and val in (True, 'True', 'true'):
            result[key] = True
        elif isBool and val in (False, 'False', 'false'):
            result[key] = False
        elif val is None:
            result[key] = default_val
        else:
            result[key] = val
    return result
#@+node:ekr.20031218072017.1474: *3* g.enl, ecnl & ecnls
def ecnl(tabName='Log'):
    g.ecnls(1, tabName)

def ecnls(n, tabName='Log'):
    log = app.log
    if log and not log.isNull:
        while log.newlines < n:
            g.enl(tabName)

def enl(tabName='Log'):
    log = app.log
    if log and not log.isNull:
        log.newlines += 1
        log.putnl(tabName)
#@+node:ekr.20100914094836.5892: *3* g.error, g.note, g.warning, g.red, g.blue
def blue(*args, **keys):
    g.es_print(color='blue', *args, **keys)

def error(*args, **keys):
    g.es_print(color='error', *args, **keys)

def note(*args, **keys):
    g.es_print(color='note', *args, **keys)

def red(*args, **keys):
    g.es_print(color='red', *args, **keys)

def warning(*args, **keys):
    g.es_print(color='warning', *args, **keys)
#@+node:ekr.20070626132332: *3* g.es
def es(*args, **keys):
    """Put all non-keyword args to the log pane.
    The first, third, fifth, etc. arg translated by g.translateString.
    Supports color, comma, newline, spaces and tabName keyword arguments.
    """
    if not app or app.killed:
        return
    if app.gui and app.gui.consoleOnly:
        return
    log = app.log
    # Compute the effective args.
    d = {
        'color': None,
        'commas': False,
        'newline': True,
        'spaces': True,
        'tabName': 'Log',
        'nodeLink': None,
    }
    d = g.doKeywordArgs(keys, d)
    color = d.get('color')
    if color == 'suppress':
        return  # New in 4.3.
    color = g.actualColor(color)
    tabName = d.get('tabName') or 'Log'
    newline = d.get('newline')
    s = g.translateArgs(args, d)
    # Do not call g.es, g.es_print, g.pr or g.trace here!
        # sys.__stdout__.write('\n===== g.es: %r\n' % s)
    if app.batchMode:
        if app.log:
            app.log.put(s)
    elif g.unitTesting:
        if log and not log.isNull:
            # This makes the output of unit tests match the output of scripts.
            g.pr(s, newline=newline)
    elif log and app.logInited:
        if newline:
            s += '\n'
        log.put(s, color=color, tabName=tabName, nodeLink=d['nodeLink'])
        # Count the number of *trailing* newlines.
        for ch in s:
            if ch == '\n': log.newlines += 1
            else: log.newlines = 0
    else:
        app.logWaiting.append((s, color, newline, d),)

log = es
#@+node:ekr.20190608090856.1: *3* g.es_clickable_link
def es_clickable_link(c, p, line_number, message):
    """Write a clickable message to the given line number of p.b."""
    log = c.frame.log
    unl = p.get_UNL(with_proto=True, with_count=True)
    if unl:
        nodeLink = f"{unl},{line_number}"
        log.put(message, nodeLink=nodeLink)
    else:
        log.put(message)
#@+node:ekr.20141107085700.4: *3* g.es_debug
def es_debug(*args, **keys):
    """
    Print all non-keyword args, and put them to the log pane in orange.

    The first, third, fifth, etc. arg translated by g.translateString.
    Supports color, comma, newline, spaces and tabName keyword arguments.
    """
    keys['color'] = 'blue'
    try:  # get the function name from the call stack.
        f1 = sys._getframe(1)  # The stack frame, one level up.
        code1 = f1.f_code  # The code object
        name = code1.co_name  # The code name
    except Exception:
        name = g.shortFileName(__file__)
    if name == '<module>':
        name = g.shortFileName(__file__)
    if name.endswith('.pyc'):
        name = name[:-1]
    g.pr(name, *args, **keys)
    if not g.app.unitTesting:
        g.es(name, *args, **keys)
#@+node:ekr.20060917120951: *3* g.es_dump
def es_dump(s, n=30, title=None):
    if title:
        g.es_print('', title)
    i = 0
    while i < len(s):
        aList = ''.join([f"{ord(ch):2x} " for ch in s[i : i + n]])
        g.es_print('', aList)
        i += n
#@+node:ekr.20031218072017.3110: *3* g.es_error & es_print_error
def es_error(*args, **keys):
    color = keys.get('color')
    if color is None and g.app.config:
        keys['color'] = g.app.config.getColor("log-error-color") or 'red'
    g.es(*args, **keys)

def es_print_error(*args, **keys):
    color = keys.get('color')
    if color is None and g.app.config:
        keys['color'] = g.app.config.getColor("log-error-color") or 'red'
    g.es_print(*args, **keys)
#@+node:ekr.20031218072017.3111: *3* g.es_event_exception
def es_event_exception(eventName, full=False):
    g.es("exception handling ", eventName, "event")
    typ, val, tb = sys.exc_info()
    if full:
        errList = traceback.format_exception(typ, val, tb)
    else:
        errList = traceback.format_exception_only(typ, val)
    for i in errList:
        g.es('', i)
    if not g.stdErrIsRedirected():  # 2/16/04
        traceback.print_exc()
#@+node:ekr.20031218072017.3112: *3* g.es_exception
def es_exception(full=True, c=None, color="red"):
    typ, val, tb = sys.exc_info()
    # val is the second argument to the raise statement.
    if full:
        lines = traceback.format_exception(typ, val, tb)
    else:
        lines = traceback.format_exception_only(typ, val)
    for line in lines:
        g.es_print_error(line, color=color)
    fileName, n = g.getLastTracebackFileAndLineNumber()
    return fileName, n
#@+node:ekr.20061015090538: *3* g.es_exception_type
def es_exception_type(c=None, color="red"):
    # exctype is a Exception class object; value is the error message.
    exctype, value = sys.exc_info()[:2]
    g.es_print('', f"{exctype.__name__}, {value}", color=color)
#@+node:ekr.20050707064040: *3* g.es_print
# see: http://www.diveintopython.org/xml_processing/unicode.html

def es_print(*args, **keys):
    """
    Print all non-keyword args, and put them to the log pane.

    The first, third, fifth, etc. arg translated by g.translateString.
    Supports color, comma, newline, spaces and tabName keyword arguments.
    """
    g.pr(*args, **keys)
    if g.app and not g.app.unitTesting:
        g.es(*args, **keys)
#@+node:ekr.20111107181638.9741: *3* g.es_print_exception
def es_print_exception(full=True, c=None, color="red"):
    """Print exception info about the last exception."""
    typ, val, tb = sys.exc_info()
        # val is the second argument to the raise statement.
    if full:
        lines = traceback.format_exception(typ, val, tb)
    else:
        lines = traceback.format_exception_only(typ, val)
    print(''.join(lines))
    try:
        fileName, n = g.getLastTracebackFileAndLineNumber()
        return fileName, n
    except Exception:
        return "<no file>", 0
#@+node:ekr.20050707065530: *3* g.es_trace
def es_trace(*args, **keys):
    if args:
        try:
            s = args[0]
            g.trace(g.toEncodedString(s, 'ascii'))
        except Exception:
            pass
    g.es(*args, **keys)
#@+node:ekr.20040731204831: *3* g.getLastTracebackFileAndLineNumber
def getLastTracebackFileAndLineNumber():
    typ, val, tb = sys.exc_info()
    if typ == SyntaxError:
        # IndentationError is a subclass of SyntaxError.
        return val.filename, val.lineno
    #
    # Data is a list of tuples, one per stack entry.
    # Tupls have the form (filename,lineNumber,functionName,text).
    data = traceback.extract_tb(tb)
    if data:
        item = data[-1]  # Get the item at the top of the stack.
        filename, n, functionName, text = item
        return filename, n
    # Should never happen.
    return '<string>', 0
#@+node:ekr.20150621095017.1: *3* g.goto_last_exception
def goto_last_exception(c):
    """Go to the line given by sys.last_traceback."""
    typ, val, tb = sys.exc_info()
    if tb:
        file_name, line_number = g.getLastTracebackFileAndLineNumber()
        line_number = max(0, line_number - 1)
            # Convert to zero-based.
        if file_name.endswith('scriptFile.py'):
            # A script.
            c.goToScriptLineNumber(line_number, c.p)
        else:
            for p in c.all_nodes():
                if p.isAnyAtFileNode() and p.h.endswith(file_name):
                    c.goToLineNumber(line_number, p)
                    return
    else:
        g.trace('No previous exception')
#@+node:ekr.20100126062623.6240: *3* g.internalError
def internalError(*args):
    """Report a serious interal error in Leo."""
    callers = g.callers(20).split(',')
    caller = callers[-1]
    g.error('\nInternal Leo error in', caller)
    g.es_print(*args)
    g.es_print('Called from', ', '.join(callers[:-1]))
    g.es_print('Please report this error to Leo\'s developers', color='red')
#@+node:ekr.20150127060254.5: *3* g.log_to_file
def log_to_file(s, fn=None):
    """Write a message to ~/test/leo_log.txt."""
    if fn is None:
        fn = g.os_path_expanduser('~/test/leo_log.txt')
    if not s.endswith('\n'):
        s = s + '\n'
    try:
        with open(fn, 'a') as f:
            f.write(s)
    except Exception:
        g.es_exception()
#@+node:ekr.20080710101653.1: *3* g.pr
# see: http://www.diveintopython.org/xml_processing/unicode.html

def pr(*args, **keys):
    """
    Print all non-keyword args. This is a wrapper for the print statement.

    The first, third, fifth, etc. arg translated by g.translateString.
    Supports color, comma, newline, spaces and tabName keyword arguments.
    """
    # Compute the effective args.
    d = {'commas': False, 'newline': True, 'spaces': True}
    d = doKeywordArgs(keys, d)
    newline = d.get('newline')
    stdout = sys.stdout if sys.stdout and g.unitTesting else sys.__stdout__
        # Unit tests require sys.stdout.
    if not stdout:
        # #541.
        return
    if sys.platform.lower().startswith('win'):
        encoding = 'ascii'  # 2011/11/9.
    elif getattr(stdout, 'encoding', None):
        # sys.stdout is a TextIOWrapper with a particular encoding.
        encoding = stdout.encoding
    else:
        encoding = 'utf-8'
    s = translateArgs(args, d)
        # Translates everything to unicode.
    s = g.toUnicode(s, encoding=encoding, reportErrors=False)
    if newline:
        s += '\n'
    #
    # Python's print statement *can* handle unicode, but
    # sitecustomize.py must have sys.setdefaultencoding('utf-8')
    try:
        # #783: print-* commands fail under pythonw.
        stdout.write(s)
    except Exception:
        pass
#@+node:ekr.20060221083356: *3* g.prettyPrintType
def prettyPrintType(obj):
    if isinstance(obj, str):
        return 'string'
    t = type(obj)
    if t in (types.BuiltinFunctionType, types.FunctionType):
        return 'function'
    if t == types.ModuleType:
        return 'module'
    if t in [types.MethodType, types.BuiltinMethodType]:
        return 'method'
    # Fall back to a hack.
    t = str(type(obj))
    if t.startswith("<type '"): t = t[7:]
    if t.endswith("'>"): t = t[:-2]
    return t
#@+node:ekr.20031218072017.3113: *3* g.printBindings
def print_bindings(name, window):
    bindings = window.bind()
    g.pr("\nBindings for", name)
    for b in bindings:
        g.pr(b)
#@+node:ekr.20070510074941: *3* g.printEntireTree
def printEntireTree(c, tag=''):
    g.pr('printEntireTree', '=' * 50)
    g.pr('printEntireTree', tag, 'root', c.rootPosition())
    for p in c.all_positions():
        g.pr('..' * p.level(), p.v)
#@+node:ekr.20031218072017.3114: *3* g.printGlobals
def printGlobals(message=None):
    # Get the list of globals.
    globs = list(globals())
    globs.sort()
    # Print the list.
    if message:
        leader = "-" * 10
        g.pr(leader, ' ', message, ' ', leader)
    for name in globs:
        g.pr(name)
#@+node:ekr.20031218072017.3115: *3* g.printLeoModules
def printLeoModules(message=None):
    # Create the list.
    mods = []
    for name in sys.modules:
        if name and name[0:3] == "leo":
            mods.append(name)
    # Print the list.
    if message:
        leader = "-" * 10
        g.pr(leader, ' ', message, ' ', leader)
    mods.sort()
    for m in mods:
        g.pr(m, newline=False)
    g.pr('')
#@+node:ekr.20041122153823: *3* g.printStack
def printStack():
    traceback.print_stack()
#@+node:ekr.20031218072017.2317: *3* g.trace
def trace(*args, **keys):
    """Print a tracing message."""
    # Don't use g here: in standalone mode g is a NullObject!
    # Compute the effective args.
    d = {'align': 0, 'before': '', 'newline': True, 'caller_level': 1, 'noname': False}
    d = doKeywordArgs(keys, d)
    newline = d.get('newline')
    align = d.get('align', 0)
    caller_level = d.get('caller_level', 1)
    noname = d.get('noname')
    # Compute the caller name.
    if noname:
        name = ''
    else:
        try:  # get the function name from the call stack.
            f1 = sys._getframe(caller_level)  # The stack frame, one level up.
            code1 = f1.f_code  # The code object
            name = code1.co_name  # The code name
        except Exception:
            name = g.shortFileName(__file__)
        if name == '<module>':
            name = g.shortFileName(__file__)
        if name.endswith('.pyc'):
            name = name[:-1]
    # Pad the caller name.
    if align != 0 and len(name) < abs(align):
        pad = ' ' * (abs(align) - len(name))
        if align > 0: name = name + pad
        else: name = pad + name
    # Munge *args into s.
    result = [name] if name else []
    #
    # Put leading newlines into the prefix.
    if isinstance(args, tuple):
        args = list(args)
    if args and isString(args[0]):
        prefix = ''
        while args[0].startswith('\n'):
            prefix += '\n'
            args[0] = args[0][1:]
    else:
        prefix = ''
    for arg in args:
        if isString(arg):
            pass
        elif isBytes(arg):
            arg = toUnicode(arg)
        else:
            arg = repr(arg)
        if result:
            result.append(" " + arg)
        else:
            result.append(arg)
    s = d.get('before') + ''.join(result)
    if prefix:
        prefix = prefix[1:]  # One less newline.
        pr(prefix)
    pr(s, newline=newline)
#@+node:ekr.20080220111323: *3* g.translateArgs
console_encoding = None

def translateArgs(args, d):
    """
    Return the concatenation of s and all args, with odd args translated.
    """
    global console_encoding
    if not console_encoding:
        e = sys.getdefaultencoding()
        console_encoding = e if isValidEncoding(e) else 'utf-8'
        # print 'translateArgs',console_encoding
    result = []; n = 0; spaces = d.get('spaces')
    for arg in args:
        n += 1
        # First, convert to unicode.
        if isinstance(arg, str):
            arg = toUnicode(arg, console_encoding)
        # Now translate.
        if not isString(arg):
            arg = repr(arg)
        elif (n % 2) == 1:
            arg = translateString(arg)
        else:
            pass  # The arg is an untranslated string.
        if arg:
            if result and spaces: result.append(' ')
            result.append(arg)
    return ''.join(result)
#@+node:ekr.20060810095921: *3* g.translateString & tr
def translateString(s):
    """Return the translated text of s."""
    # pylint: disable=undefined-loop-variable
    # looks like a pylint bug
    upper = app and getattr(app, 'translateToUpperCase', None)
    if not isinstance(s, str):
        s = str(s, 'utf-8')
    if upper:
        s = s.upper()
    else:
        s = gettext.gettext(s)
    return s

tr = translateString
#@+node:EKR.20040612114220: ** g.Miscellaneous
#@+node:ekr.20120928142052.10116: *3* g.actualColor
def actualColor(color):
    """Return the actual color corresponding to the requested color."""
    c = g.app.log and g.app.log.c
    # Careful: c.config may not yet exist.
    if not c or not c.config:
        return color
    # Don't change absolute colors.
    if color and color.startswith('#'):
        return color
    # #788: Translate colors to theme-defined colors.
    if color is None:
        # Prefer text_foreground_color'
        color2 = c.config.getColor('log-text-foreground-color')
        if color2: return color2
        # Fall back to log_black_color.
        color2 = c.config.getColor('log-black-color')
        return color2 or 'black'
    if color == 'black':
        # Prefer log_black_color.
        color2 = c.config.getColor('log-black-color')
        if color2: return color2
        # Fall back to log_text_foreground_color.
        color2 = c.config.getColor('log-text-foreground-color')
        return color2 or 'black'
    color2 = c.config.getColor(f"log_{color}_color")
    return color2 or color
#@+node:ekr.20060921100435: *3* g.CheckVersion & helpers
# Simplified version by EKR: stringCompare not used.

def CheckVersion(s1, s2, condition=">=", stringCompare=None, delimiter='.', trace=False):
    # CheckVersion is called early in the startup process.
    vals1 = [g.CheckVersionToInt(s) for s in s1.split(delimiter)]; n1 = len(vals1)
    vals2 = [g.CheckVersionToInt(s) for s in s2.split(delimiter)]; n2 = len(vals2)
    n = max(n1, n2)
    if n1 < n: vals1.extend([0 for i in range(n - n1)])
    if n2 < n: vals2.extend([0 for i in range(n - n2)])
    for cond, val in (
        ('==', vals1 == vals2), ('!=', vals1 != vals2),
        ('<', vals1 < vals2), ('<=', vals1 <= vals2),
        ('>', vals1 > vals2), ('>=', vals1 >= vals2),
    ):
        if condition == cond:
            result = val; break
    else:
        raise EnvironmentError(
            "condition must be one of '>=', '>', '==', '!=', '<', or '<='.")
    return result
#@+node:ekr.20070120123930: *4* g.CheckVersionToInt
def CheckVersionToInt(s):
    try:
        return int(s)
    except ValueError:
        aList = []
        for ch in s:
            if ch.isdigit(): aList.append(ch)
            else: break
        if aList:
            s = ''.join(aList)
            return int(s)
        return 0
#@+node:ekr.20031218072017.3147: *3* g.choose (deprecated)
# This can and should be replaced by Python's ternary operator.

def choose(cond, a, b):  # warning: evaluates all arguments
    """(Deprecated) simulate `a if cond else b`."""
    if cond:
        return a
    return b
#@+node:ekr.20111103205308.9657: *3* g.cls
@command('cls')
def cls(event=None):
    """Clear the screen."""
    if sys.platform.lower().startswith('win'):
        os.system('cls')
#@+node:ekr.20131114124839.16665: *3* g.createScratchCommander
def createScratchCommander(fileName=None):
    c = g.app.newCommander(fileName)
    frame = c.frame
    frame.createFirstTreeNode()
    assert c.rootPosition()
    frame.setInitialWindowGeometry()
    frame.resizePanesToRatio(frame.ratio, frame.secondary_ratio)
#@+node:ekr.20031218072017.3126: *3* g.funcToMethod (Python Cookbook)
def funcToMethod(f, theClass, name=None):
    """
    From the Python Cookbook...

    The following method allows you to add a function as a method of
    any class. That is, it converts the function to a method of the
    class. The method just added is available instantly to all
    existing instances of the class, and to all instances created in
    the future.
    
    The function's first argument should be self.
    
    The newly created method has the same name as the function unless
    the optional name argument is supplied, in which case that name is
    used as the method name.
    """
    setattr(theClass, name or f.__name__, f)
#@+node:ekr.20060913090832.1: *3* g.init_zodb
init_zodb_import_failed = False
init_zodb_failed = {}  # Keys are paths, values are True.
init_zodb_db = {}  # Keys are paths, values are ZODB.DB instances.

def init_zodb(pathToZodbStorage, verbose=True):
    """
    Return an ZODB.DB instance from the given path.
    return None on any error.
    """
    global init_zodb_db, init_zodb_failed, init_zodb_import_failed
    db = init_zodb_db.get(pathToZodbStorage)
    if db: return db
    if init_zodb_import_failed: return None
    failed = init_zodb_failed.get(pathToZodbStorage)
    if failed: return None
    
    #Transcrypt does not support Python's ZODB module.
    # __pragma__ ('skip')
    try:
        import ZODB
    except ImportError:
        if verbose:
            g.es('g.init_zodb: can not import ZODB')
            g.es_exception()
        init_zodb_import_failed = True
        return None
    # __pragma__ ('noskip')

    try:
        storage = ZODB.FileStorage.FileStorage(pathToZodbStorage)
        init_zodb_db[pathToZodbStorage] = db = ZODB.DB(storage)
        return db
    except Exception:
        if verbose:
            g.es('g.init_zodb: exception creating ZODB.DB instance')
            g.es_exception()
        init_zodb_failed[pathToZodbStorage] = True
        return None
#@+node:ekr.20170206080908.1: *3* g.input_
# Transcrypt does not support Qt.
# __pragma__ ('skip')

def input_(message='', c=None):
    """
    Safely execute python's input statement.

    c.executeScriptHelper binds 'input' to be a wrapper that calls g.input_
    with c and handler bound properly.
    """
    if app.gui.isNullGui:
        return ''
    # Prompt for input from the console, assuming there is one.
    # pylint: disable=no-member
    from leo.core.leoQt import QtCore
    QtCore.pyqtRemoveInputHook()
    return input(message)

# __pragma__ ('noskip')
#@+node:ekr.20110609125359.16493: *3* g.isMacOS
def isMacOS():
    return sys.platform == 'darwin'
#@+node:ekr.20181027133311.1: *3* g.issueSecurityWarning
def issueSecurityWarning(setting):
    g.es('Security warning! Ignoring...', color='red')
    g.es(setting, color='red')
    g.es('This setting can be set only in')
    g.es('leoSettings.leo or myLeoSettings.leo')
#@+node:ekr.20031218072017.3144: *3* g.makeDict (Python Cookbook)
# From the Python cookbook.

def makeDict(**keys):
    """Returns a Python dictionary from using the optional keyword arguments."""
    return keys
#@+node:ekr.20140528065727.17963: *3* g.pep8_class_name
def pep8_class_name(s):
    """Return the proper class name for s."""
    # Warning: s.capitalize() does not work.
    # It lower cases all but the first letter!
    return ''.join([z[0].upper() + z[1:] for z in s.split('_') if z])

if 0:  # Testing:
    cls()
    aList = (
        '_',
        '__',
        '_abc',
        'abc_',
        'abc',
        'abc_xyz',
        'AbcPdQ',
    )
    for s in aList:
        print(pep8_class_name(s))
#@+node:ekr.20160417174224.1: *3* g.plural
def plural(obj):
    """Return "s" or "" depending on n."""
    if isinstance(obj, (list, tuple, str)):
        n = len(obj)
    else:
        n = obj
    return '' if n == 1 else 's'
#@+node:ekr.20160331194701.1: *3* g.truncate
def truncate(s, n):
    """Return s truncated to n characters."""
    if len(s) <= n:
        return s
    # Fail: weird ws.
    s2 = s[: n - 3] + f"...({len(s)})"
    if s.endswith('\n'):
        return s2 + '\n'
    return s2
#@+node:ekr.20031218072017.3150: *3* g.windows
def windows():
    return app and app.windowList
#@+node:ekr.20031218072017.2145: ** g.os_path_ Wrappers
#@+at Note: all these methods return Unicode strings. It is up to the user to
# convert to an encoded string as needed, say when opening a file.
#@+node:ekr.20180314120442.1: *3* g.glob_glob
def glob_glob(pattern):
    """Return the regularized glob.glob(pattern)"""
    aList = glob.glob(pattern)
    if g.isWindows:
        aList = [z.replace('\\', '/') for z in aList]
    return aList
#@+node:ekr.20031218072017.2146: *3* g.os_path_abspath
def os_path_abspath(path):
    """Convert a path to an absolute path."""
    path = g.toUnicodeFileEncoding(path)
    path = path.replace('\x00', '')  # Fix Pytyon 3 bug on Windows 10.
    path = os.path.abspath(path)
    path = g.toUnicodeFileEncoding(path)
    if g.isWindows:
        path = path.replace('\\', '/')
    return path
#@+node:ekr.20031218072017.2147: *3* g.os_path_basename
def os_path_basename(path):
    """Return the second half of the pair returned by split(path)."""
    path = g.toUnicodeFileEncoding(path)
    path = os.path.basename(path)
    path = g.toUnicodeFileEncoding(path)
    if g.isWindows:
        path = path.replace('\\', '/')
    return path
#@+node:ekr.20031218072017.2148: *3* g.os_path_dirname
def os_path_dirname(path):
    """Return the first half of the pair returned by split(path)."""
    path = g.toUnicodeFileEncoding(path)
    path = os.path.dirname(path)
    path = g.toUnicodeFileEncoding(path)
    if g.isWindows:
        path = path.replace('\\', '/')
    return path
#@+node:ekr.20031218072017.2149: *3* g.os_path_exists
def os_path_exists(path):
    """Return True if path exists."""
    path = g.toUnicodeFileEncoding(path)
    path = path.replace('\x00', '')  # Fix Pytyon 3 bug on Windows 10.
    return os.path.exists(path)
#@+node:ekr.20080922124033.6: *3* g.os_path_expandExpression & helper (deprecated)
deprecated_messages = []

def os_path_expandExpression(s, **keys):
    """
    Expand all {{anExpression}} in c's context.
    
    Deprecated: use c.expand_path_expression(s) instead.
    """

    c = keys.get('c')
    if not c:
        g.trace('can not happen: no c', g.callers())
        return s
    callers = g.callers(2)
    if callers not in deprecated_messages:
        deprecated_messages.append(callers)
        g.es_print(f"\nos_path_expandExpression is deprecated. called from: {callers}")
    return c.expand_path_expression(s)
#@+node:ekr.20080921060401.13: *3* g.os_path_expanduser
def os_path_expanduser(path):
    """wrap os.path.expanduser"""
    path = g.toUnicodeFileEncoding(path)
    result = os.path.normpath(os.path.expanduser(path))
    if g.isWindows:
        path = path.replace('\\', '/')
    return result
#@+node:ekr.20080921060401.14: *3* g.os_path_finalize
def os_path_finalize(path):
    """
    Expand '~', then return os.path.normpath, os.path.abspath of the path.
    There is no corresponding os.path method
    """
    path = path.replace('\x00', '')  # Fix Pytyon 3 bug on Windows 10.
    path = os.path.expanduser(path)  # #1383.
    path = os.path.abspath(path)
    path = os.path.normpath(path)
    if g.isWindows:
        path = path.replace('\\', '/')
    # calling os.path.realpath here would cause problems in some situations.
    return path
#@+node:ekr.20140917154740.19483: *3* g.os_path_finalize_join
def os_path_finalize_join(*args, **keys):
    """
    Join and finalize.
    
    **keys may contain a 'c' kwarg, used by c.os_path_join.
    """
    # Old code
        # path = os.path.normpath(os.path.abspath(g.os_path_join(*args, **keys)))
        # if g.isWindows:
            # path = path.replace('\\','/')
    #
    # #1383: Call both wrappers, to ensure ~ is always expanded.
    #        This is significant change, to undo previous mistakes.
    #        Revs cbbf5e8b and 6e461196 in devel were the likely culprits.
    path = g.os_path_join(*args, **keys)
    path = g.os_path_finalize(path)
    return path
#@+node:ekr.20031218072017.2150: *3* g.os_path_getmtime
def os_path_getmtime(path):
    """Return the modification time of path."""
    path = g.toUnicodeFileEncoding(path)
    try:
        return os.path.getmtime(path)
    except Exception:
        return 0
#@+node:ekr.20080729142651.2: *3* g.os_path_getsize
def os_path_getsize(path):
    """Return the size of path."""
    path = g.toUnicodeFileEncoding(path)
    return os.path.getsize(path)
#@+node:ekr.20031218072017.2151: *3* g.os_path_isabs
def os_path_isabs(path):
    """Return True if path is an absolute path."""
    path = g.toUnicodeFileEncoding(path)
    return os.path.isabs(path)
#@+node:ekr.20031218072017.2152: *3* g.os_path_isdir
def os_path_isdir(path):
    """Return True if the path is a directory."""
    path = g.toUnicodeFileEncoding(path)
    return os.path.isdir(path)
#@+node:ekr.20031218072017.2153: *3* g.os_path_isfile
def os_path_isfile(path):
    """Return True if path is a file."""
    path = g.toUnicodeFileEncoding(path)
    return os.path.isfile(path)
#@+node:ekr.20031218072017.2154: *3* g.os_path_join
def os_path_join(*args, **keys):
    """
    Join paths, like os.path.join, with enhancements:
    
    A '!!' arg prepends g.app.loadDir to the list of paths.
    A '.'  arg prepends c.openDirectory to the list of paths,
           provided there is a 'c' kwarg.
    """
    c = keys.get('c')
    uargs = [g.toUnicodeFileEncoding(arg) for arg in args]
    # Note:  This is exactly the same convention as used by getBaseDirectory.
    if uargs and uargs[0] == '!!':
        uargs[0] = g.app.loadDir
    elif uargs and uargs[0] == '.':
        c = keys.get('c')
        if c and c.openDirectory:
            uargs[0] = c.openDirectory
    if uargs:
        try:
            path = os.path.join(*uargs)
        except TypeError:
            g.trace(uargs, args, keys, g.callers())
            raise
    else:
        path = ''
    # May not be needed on some Pythons.
    path = g.toUnicodeFileEncoding(path)
    path = path.replace('\x00', '')  # Fix Pytyon 3 bug on Windows 10.
    if g.isWindows:
        path = path.replace('\\', '/')
    return path
#@+node:ekr.20031218072017.2156: *3* g.os_path_normcase
def os_path_normcase(path):
    """Normalize the path's case."""
    path = g.toUnicodeFileEncoding(path)
    path = os.path.normcase(path)
    path = g.toUnicodeFileEncoding(path)
    if g.isWindows:
        path = path.replace('\\', '/')
    return path
#@+node:ekr.20031218072017.2157: *3* g.os_path_normpath
def os_path_normpath(path):
    """Normalize the path."""
    path = g.toUnicodeFileEncoding(path)
    path = os.path.normpath(path)
    path = g.toUnicodeFileEncoding(path)
    if g.isWindows:
        path = path.replace('\\', '/')
    return path
#@+node:ekr.20180314081254.1: *3* g.os_path_normslashes
def os_path_normslashes(path):
    if g.isWindows and path:
        path = path.replace('\\', '/')
    return path
#@+node:ekr.20080605064555.2: *3* g.os_path_realpath
def os_path_realpath(path):
    """Return the canonical path of the specified filename, eliminating any
    symbolic links encountered in the path (if they are supported by the
    operating system).
    """
    path = g.toUnicodeFileEncoding(path)
    path = os.path.realpath(path)
    path = g.toUnicodeFileEncoding(path)
    if g.isWindows:
        path = path.replace('\\', '/')
    return path
#@+node:ekr.20031218072017.2158: *3* g.os_path_split
def os_path_split(path):
    path = g.toUnicodeFileEncoding(path)
    head, tail = os.path.split(path)
    head = g.toUnicodeFileEncoding(head)
    tail = g.toUnicodeFileEncoding(tail)
    return head, tail
#@+node:ekr.20031218072017.2159: *3* g.os_path_splitext
def os_path_splitext(path):
    path = g.toUnicodeFileEncoding(path)
    head, tail = os.path.splitext(path)
    head = g.toUnicodeFileEncoding(head)
    tail = g.toUnicodeFileEncoding(tail)
    return head, tail
#@+node:ekr.20090829140232.6036: *3* g.os_startfile
def os_startfile(fname):
    #@+others
    #@+node:bob.20170516112250.1: *4* stderr2log()
    def stderr2log(g, ree, fname):
        """ Display stderr output in the Leo-Editor log pane

        Arguments:
            g:  Leo-Editor globals
            ree:  Read file descriptor for stderr
            fname:  file pathname

        Returns:
            None
        """

        while True:
            emsg = ree.read().decode('utf-8')
            if emsg:
                g.es_print_error(f"xdg-open {fname} caused output to stderr:\n{emsg}")
            else:
                break
    #@+node:bob.20170516112304.1: *4* itPoll()
    def itPoll(fname, ree, subPopen, g, ito):
        """ Poll for subprocess done

        Arguments:
            fname:  File name
            ree:  stderr read file descriptor
            subPopen:  URL open subprocess object
            g: Leo-Editor globals
            ito: Idle time object for itPoll()

        Returns:
            None
        """

        stderr2log(g, ree, fname)
        rc = subPopen.poll()
        if not rc is None:
            ito.stop()
            ito.destroy_self()
            if rc != 0:
                g.es_print(f"xdg-open {fname} failed with exit code {rc}")
            stderr2log(g, ree, fname)
            ree.close()
    #@-others
    if fname.find('"') > -1:
        quoted_fname = f"'{fname}'"
    else:
        quoted_fname = f'"{fname}"'
    if sys.platform.startswith('win'):
        # pylint: disable=no-member
        os.startfile(quoted_fname)
            # Exists only on Windows.
    elif sys.platform == 'darwin':
        # From Marc-Antoine Parent.
        try:
            # Fix bug 1226358: File URL's are broken on MacOS:
            # use fname, not quoted_fname, as the argument to subprocess.call.
            subprocess.call(['open', fname])
        except OSError:
            pass  # There may be a spurious "Interrupted system call"
        except ImportError:
            os.system(f"open {quoted_fname}")
    else:
        try:
            ree = None
            wre = tempfile.NamedTemporaryFile()
            ree = io.open(wre.name, 'rb', buffering=0)
        except IOError:
            g.trace(f"error opening temp file for {fname!r}")
            if ree: ree.close()
            return
        try:
            subPopen = subprocess.Popen(['xdg-open', fname], stderr=wre, shell=False)
        except Exception:
            g.es_print(f"error opening {fname!r}")
            g.es_exception()
        try:
            itoPoll = g.IdleTime(
                (lambda ito: itPoll(fname, ree, subPopen, g, ito)),
                delay=1000,
            )
            itoPoll.start()
            # Let the Leo-Editor process run
            # so that Leo-Editor is usable while the file is open.
        except Exception:
            g.es_exception(f"exception executing g.startfile for {fname!r}")
#@+node:ekr.20031218072017.2160: *3* g.toUnicodeFileEncoding
def toUnicodeFileEncoding(path):
    # Fix bug 735938: file association crash
    if path and isinstance(path, str):
        path = path.replace('\\', os.sep)
        # Yes, this is correct.  All os_path_x functions return Unicode strings.
        return g.toUnicode(path)
    return ''
#@+node:ekr.20111115155710.9859: ** g.Parsing & Tokenizing
#@+node:ekr.20031218072017.822: *3* g.createTopologyList
def createTopologyList(c, root=None, useHeadlines=False):
    """Creates a list describing a node and all its descendents"""
    if not root: root = c.rootPosition()
    v = root
    if useHeadlines:
        aList = [(v.numberOfChildren(), v.headString()),]
    else:
        aList = [v.numberOfChildren()]
    child = v.firstChild()
    while child:
        aList.append(g.createTopologyList(c, child, useHeadlines))
        child = child.next()
    return aList
#@+node:ekr.20111017204736.15898: *3* g.getDocString
def getDocString(s):
    """Return the text of the first docstring found in s."""
    tags = ('"""', "'''")
    tag1, tag2 = tags
    i1, i2 = s.find(tag1), s.find(tag2)
    if i1 == -1 and i2 == -1:
        return ''
    if i1 > -1 and i2 > -1:
        i = min(i1, i2)
    else:
        i = max(i1, i2)
    tag = s[i : i + 3]
    assert tag in tags
    j = s.find(tag, i + 3)
    if j > -1:
        return s[i + 3 : j]
    return ''
#@+node:ekr.20111017211256.15905: *3* g.getDocStringForFunction
def getDocStringForFunction(func):
    """Return the docstring for a function that creates a Leo command."""

    def name(func):
        return func.__name__ if hasattr(func, '__name__') else '<no __name__>'

    def get_defaults(func, i):
        defaults = inspect.getfullargspec(func)[3]
        return defaults[i]

    # Fix bug 1251252: https://bugs.launchpad.net/leo-editor/+bug/1251252
    # Minibuffer commands created by mod_scripting.py have no docstrings.
    # Do special cases first.

    s = ''
    if name(func) == 'minibufferCallback':
        func = get_defaults(func, 0)
        if hasattr(func, 'func.__doc__') and func.__doc__.strip():
            s = func.__doc__
    if not s and name(func) == 'commonCommandCallback':
        script = get_defaults(func, 1)
        s = g.getDocString(script)
            # Do a text scan for the function.
    # Now the general cases.  Prefer __doc__ to docstring()
    if not s and hasattr(func, '__doc__'):
        s = func.__doc__
    if not s and hasattr(func, 'docstring'):
        s = func.docstring
    return s
#@+node:ekr.20111115155710.9814: *3* g.python_tokenize
def python_tokenize(s, line_numbers=True):
    """
    Tokenize string s and return a list of tokens (kind,value,line_number)

    where kind is in ('comment,'id','nl','other','string','ws').
    """
    result, i, line_number = [], 0, 0
    while i < len(s):
        progress = j = i
        ch = s[i]
        if ch == '\n':
            kind, i = 'nl', i + 1
        elif ch in ' \t':
            kind = 'ws'
            while i < len(s) and s[i] in ' \t':
                i += 1
        elif ch == '#':
            kind, i = 'comment', g.skip_to_end_of_line(s, i)
        elif ch in '"\'':
            kind, i = 'string', g.skip_python_string(s, i, verbose=False)
        elif ch == '_' or ch.isalpha():
            kind, i = 'id', g.skip_id(s, i)
        else:
            kind, i = 'other', i + 1
        assert progress < i and j == progress
        val = s[j:i]
        assert val
        if line_numbers:
            line_number += val.count('\n')  # A comment.
            result.append((kind, val, line_number),)
        else:
            result.append((kind, val),)
    return result
#@+node:ekr.20040327103735.2: ** g.Scripting
#@+node:ekr.20161223090721.1: *3* g.exec_file
def exec_file(path, d, script=None):
    """Simulate python's execfile statement for python 3."""
    if script is None:
        with open(path) as f:
            script = f.read()
    exec(compile(script, path, 'exec'), d)
#@+node:ekr.20131016032805.16721: *3* g.execute_shell_commands
def execute_shell_commands(commands, trace=False):
    """
    Execute each shell command in a separate process.
    Wait for each command to complete, except those starting with '&'
    """
    if isinstance(commands, str):
        commands = [commands]
    for command in commands:
        wait = not command.startswith('&')
        if trace: g.trace(command)
        if command.startswith('&'):
            command = command[1:].strip()
        proc = subprocess.Popen(command, shell=True)
        if wait:
            proc.communicate()
        else:
            if trace: print('Start:', proc)
            # #1489: call proc.poll at idle time.

            def proc_poller(timer, proc=proc):
                val = proc.poll()
                if val is not None:
                    # This trace can be disruptive.
                    if trace: print('  End:', proc, val)
                    timer.stop()

            g.IdleTime(proc_poller, delay=0).start()
#@+node:ekr.20180217113719.1: *3* g.execute_shell_commands_with_options & helpers
def execute_shell_commands_with_options(
    base_dir=None,
    c=None,
    command_setting=None,
    commands=None,
    path_setting=None,
    trace=False,
    warning=None,
):
    """
    A helper for prototype commands or any other code that
    runs programs in a separate process.
    
    base_dir:           Base directory to use if no config path given.
    commands:           A list of commands, for g.execute_shell_commands.
    commands_setting:   Name of @data setting for commands.
    path_setting:       Name of @string setting for the base directory.
    warning:            A warning to be printed before executing the commands.
    """
    base_dir = g.computeBaseDir(c, base_dir, path_setting, trace)
    if not base_dir:
        return
    commands = g.computeCommands(c, commands, command_setting, trace)
    if not commands:
        return
    if warning:
        g.es_print(warning)
    os.chdir(base_dir)  # Can't do this in the commands list.
    g.execute_shell_commands(commands)
#@+node:ekr.20180217152624.1: *4* g.computeBaseDir
def computeBaseDir(c, base_dir, path_setting, trace=False):
    """
    Compute a base_directory.
    If given, @string path_setting takes precedence.
    """
    # Prefer the path setting to the base_dir argument.
    if path_setting:
        if not c:
            return g.es_print('@string path_setting requires valid c arg')
        # It's not an error for the setting to be empty.
        base_dir2 = c.config.getString(path_setting)
        if base_dir2:
            base_dir2 = base_dir2.replace('\\', '/')
            if g.os_path_exists(base_dir2):
                return base_dir2
            return g.es_print(f"@string {path_setting} not found: {base_dir2!r}")
    # Fall back to given base_dir.
    if base_dir:
        base_dir = base_dir.replace('\\', '/')
        if g.os_path_exists(base_dir):
            return base_dir
        return g.es_print(f"base_dir not found: {base_dir!r}")
    return g.es_print(f"Please use @string {path_setting}")
#@+node:ekr.20180217153459.1: *4* g.computeCommands
def computeCommands(c, commands, command_setting, trace=False):
    """
    Get the list of commands.
    If given, @data command_setting takes precedence.
    """
    if not commands and not command_setting:
        g.es_print('Please use commands, command_setting or both')
        return []
    # Prefer the setting to the static commands.
    if command_setting:
        if c:
            aList = c.config.getData(command_setting)
            # It's not an error for the setting to be empty.
            # Fall back to the commands.
            return aList or commands
        g.es_print('@data command_setting requires valid c arg')
        return []
    return commands
#@+node:ekr.20050503112513.7: *3* g.executeFile
def executeFile(filename, options=''):
    if not os.access(filename, os.R_OK): return
    fdir, fname = g.os_path_split(filename)
    # New in Leo 4.10: alway use subprocess.

    def subprocess_wrapper(cmdlst):

        p = subprocess.Popen(cmdlst, cwd=fdir,
            universal_newlines=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdo, stde = p.communicate()
        return p.wait(), stdo, stde

    rc, so, se = subprocess_wrapper(f"{sys.executable} {fname} {options}")
    if rc: g.pr('return code', rc)
    g.pr(so, se)
#@+node:ekr.20040321065415: *3* g.findNode... &,findTopLevelNode
def findNodeInChildren(c, p, headline, exact=True):
    """Search for a node in v's tree matching the given headline."""
    p1 = p.copy()
    h = headline.strip()
    for p in p1.children():
        if p.h.strip() == h:
            return p.copy()
    if not exact:
        for p in p1.children():
            if p.h.strip().startswith(h):
                return p.copy()
    return None

def findNodeInTree(c, p, headline, exact=True):
    """Search for a node in v's tree matching the given headline."""
    h = headline.strip()
    p1 = p.copy()
    for p in p1.subtree():
        if p.h.strip() == h:
            return p.copy()
    if not exact:
        for p in p1.subtree():
            if p.h.strip().startswith(h):
                return p.copy()
    return None

def findNodeAnywhere(c, headline, exact=True):
    h = headline.strip()
    for p in c.all_unique_positions(copy=False):
        if p.h.strip() == h:
            return p.copy()
    if not exact:
        for p in c.all_unique_positions(copy=False):
            if p.h.strip().startswith(h):
                return p.copy()
    return None

def findTopLevelNode(c, headline, exact=True):
    h = headline.strip()
    for p in c.rootPosition().self_and_siblings(copy=False):
        if p.h.strip() == h:
            return p.copy()
    if not exact:
        for p in c.rootPosition().self_and_siblings(copy=False):
            if p.h.strip().startswith(h):
                return p.copy()
    return None
#@+node:EKR.20040614071102.1: *3* g.getScript & helpers
def getScript(c, p,
    useSelectedText=True,
    forcePythonSentinels=True,
    useSentinels=True,
):
    """
    Return the expansion of the selected text of node p.
    Return the expansion of all of node p's body text if
    p is not the current node or if there is no text selection.
    """
    w = c.frame.body.wrapper
    if not p: p = c.p
    try:
        if g.app.inBridge:
            s = p.b
        elif w and p == c.p and useSelectedText and w.hasSelection():
            s = w.getSelectedText()
        else:
            s = p.b
        # Remove extra leading whitespace so the user may execute indented code.
        s = g.removeExtraLws(s, c.tab_width)
        s = g.extractExecutableString(c, p, s)
        script = g.composeScript(c, p, s,
                    forcePythonSentinels=forcePythonSentinels,
                    useSentinels=useSentinels)
    except Exception:
        g.es_print("unexpected exception in g.getScript")
        g.es_exception()
        script = ''
    return script
#@+node:ekr.20170228082641.1: *4* g.composeScript
def composeScript(c, p, s, forcePythonSentinels=True, useSentinels=True):
    """Compose a script from p.b."""
    # This causes too many special cases.
        # if not g.unitTesting and forceEncoding:
            # aList = g.get_directives_dict_list(p)
            # encoding = scanAtEncodingDirectives(aList) or 'utf-8'
            # s = g.insertCodingLine(encoding,s)
    if not s.strip():
        return ''
    at = c.atFileCommands
    old_in_script = g.app.inScript
    try:
        # #1297: set inScript flags.
        g.app.inScript = g.inScript = True
        g.app.scriptDict["script1"] = s
        # Important: converts unicode to utf-8 encoded strings.
        script = at.stringToString(p.copy(), s,
            forcePythonSentinels=forcePythonSentinels,
            sentinels=useSentinels)
        script = script.replace("\r\n", "\n")  # Use brute force.
            # Important, the script is an **encoded string**, not a unicode string.
        g.app.scriptDict["script2"] = script
    finally:
        g.app.inScript = g.inScript = old_in_script
    return script
#@+node:ekr.20170123074946.1: *4* g.extractExecutableString
def extractExecutableString(c, p, s):
    """
    Return all lines for the given @language directive.

    Ignore all lines under control of any other @language directive.
    """
    #
    # Rewritten to fix #1071.
    if g.unitTesting:
        return s  # Regretable, but necessary.
    #
    # Return s if no @language in effect. Should never happen.
    language = g.scanForAtLanguage(c, p)
    if not language:
        return s
    #
    # Return s if @language is unambiguous.
    pattern = r'^@language\s+(\w+)'
    matches = list(re.finditer(pattern, s, re.MULTILINE))
    if len(matches) < 2:
        return s
    #
    # Scan the lines, extracting only the valid lines.
    extracting, result = False, []
    for i, line in enumerate(g.splitLines(s)):
        m = re.match(pattern, line)
        if m:
            # g.trace(language, m.group(1))
            extracting = m.group(1) == language
        elif extracting:
            result.append(line)
    return ''.join(result)
#@+node:ekr.20060624085200: *3* g.handleScriptException
def handleScriptException(c, p, script, script1):
    g.warning("exception executing script")
    full = c.config.getBool('show-full-tracebacks-in-scripts')
    fileName, n = g.es_exception(full=full)
    # Careful: this test is no longer guaranteed.
    if p.v.context == c:
        try:
            c.goToScriptLineNumber(n, p)
            #@+<< dump the lines near the error >>
            #@+node:EKR.20040612215018: *4* << dump the lines near the error >>
            if g.os_path_exists(fileName):
                with open(fileName) as f:
                    lines = f.readlines()
            else:
                lines = g.splitLines(script)
            s = '-' * 20
            g.es_print('', s)
            # Print surrounding lines.
            i = max(0, n - 2)
            j = min(n + 2, len(lines))
            while i < j:
                ch = '*' if i == n - 1 else ' '
                s = f"{ch} line {i+1:d}: {lines[i]}"
                g.es('', s, newline=False)
                i += 1
            #@-<< dump the lines near the error >>
        except Exception:
            g.es_print('Unexpected exception in g.handleScriptException')
            g.es_exception()
#@+node:ekr.20140209065845.16767: *3* g.insertCodingLine
def insertCodingLine(encoding, script):
    """
    Insert a coding line at the start of script s if no such line exists.
    The coding line must start with @first because it will be passed to
    at.stringToString.
    """
    if script:
        tag = '@first # -*- coding:'
        lines = g.splitLines(script)
        for s in lines:
            if s.startswith(tag):
                break
        else:
            lines.insert(0, f"{tag} {encoding} -*-\n")
            script = ''.join(lines)
    return script
#@+node:ekr.20070524083513: ** g.Unit Tests
#@+node:ekr.20100812172650.5909: *3* g.findTestScript
def findTestScript(c, h, where=None, warn=True):
    if where:
        p = g.findNodeAnywhere(c, where)
        if p:
            p = g.findNodeInTree(c, p, h)
    else:
        p = g.findNodeAnywhere(c, h)
    if p:
        return g.getScript(c, p)
    if warn: g.trace('Not found', h)
    return None
#@+node:ekr.20070619173330: *3* g.getTestVars
def getTestVars():
    d = g.app.unitTestDict
    c = d.get('c')
    p = d.get('p')
    # Indicate that getTestVars has run.
    # This is an indirect test that some unit test has run.
    d['getTestVars'] = True
    return c, p and p.copy()
#@+node:ekr.20200221050038.1: *3* g.run_unit_test_in_separate_process
def run_unit_test_in_separate_process(command):
    """
    A script to be run from unitTest.leo.
    
    Run the unit testing command (say `python -m leo.core.leoAst`) in a separate process.
    
    Fail (in leoTest.leo) if that fails.
    """
    leo_editor_dir = os.path.join(g.app.loadDir, '..', '..')
    os.chdir(leo_editor_dir)
    p = subprocess.Popen(
        shlex.split(command),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=sys.platform.startswith('win'),
    )
    out, err = p.communicate()
    err = g.toUnicode(err)
    out = g.toUnicode(out)
    print('')
    print(command)
    if out.strip():
        # print('traces...')
        print(out.rstrip())
    print(err.rstrip())
    # There may be skipped tests...
    err_lines = g.splitLines(err.rstrip())
    assert err_lines[-1].startswith('OK')
#@+node:ekr.20080919065433.2: *3* g.toEncodedStringWithErrorCode (for unit testing)
def toEncodedStringWithErrorCode(s, encoding, reportErrors=False):
    """For unit testing: convert s to an encoded string and return (s,ok)."""
    ok = True
    if g.isUnicode(s):
        try:
            s = s.encode(encoding, "strict")
        except UnicodeError:
            s = s.encode(encoding, "replace")
            if reportErrors:
                g.error(f"Error converting {s} from unicode to {encoding} encoding")
            ok = False
    return s, ok
#@+node:ekr.20080919065433.1: *3* g.toUnicodeWithErrorCode (for unit testing)
def toUnicodeWithErrorCode(s, encoding, reportErrors=False):
    """For unit testing: convert s to unicode and return (s,ok)."""
    if s is None:
        return '', True
    if isinstance(s, str):
        return s, True
    try:
        s = str(s, encoding, 'strict')
        return s, True
    except UnicodeError:
        s = str(s, encoding, 'replace')
        if reportErrors:
            g.error(f"Error converting {s} from {encoding} encoding to unicode")
        return s, False
#@+node:ekr.20120311151914.9916: ** g.Urls
unl_regex = re.compile(r'\bunl:.*$')

kinds = '(file|ftp|gopher|http|https|mailto|news|nntp|prospero|telnet|wais)'
url_regex = re.compile(fr"""{kinds}://[^\s'"]+[\w=/]""")
#@+node:ekr.20170226093349.1: *3* g.unquoteUrl
def unquoteUrl(url):
    """Replace special characters (especially %20, by their equivalent)."""
    return urllib.parse.unquote(url)
#@+node:ekr.20120320053907.9776: *3* g.computeFileUrl
def computeFileUrl(fn, c=None, p=None):
    """
    Compute finalized url for filename fn.
    """
    # First, replace special characters (especially %20, by their equivalent).
    url = urllib.parse.unquote(fn)
    # Finalize the path *before* parsing the url.
    i = url.find('~')
    if i > -1:
        # Expand '~'.
        path = url[i:]
        path = g.os_path_expanduser(path)
        # #1338: This is way too dangerous, and a serious security violation.
            # path = g.os_path_expandExpression(path, c=c)
        path = g.os_path_finalize(path)
        url = url[:i] + path
    else:
        tag = 'file://'
        tag2 = 'file:///'
        if sys.platform.startswith('win') and url.startswith(tag2):
            path = url[len(tag2) :].lstrip()
        elif url.startswith(tag):
            path = url[len(tag) :].lstrip()
        else:
            path = url
        # #1338: This is way too dangerous, and a serious security violation.
            # path = g.os_path_expandExpression(path, c=c)
        # Handle ancestor @path directives.
        if c and c.openDirectory:
            base = c.getNodePath(p)
            path = g.os_path_finalize_join(c.openDirectory, base, path)
        else:
            path = g.os_path_finalize(path)
        url = f"{tag}{path}"
    return url
#@+node:ekr.20120311151914.9917: *3* g.getUrlFromNode
def getUrlFromNode(p):
    """
    Get an url from node p:
    1. Use the headline if it contains a valid url.
    2. Otherwise, look *only* at the first line of the body.
    """
    if not p: return None
    c = p.v.context
    assert c
    table = [p.h, g.splitLines(p.b)[0] if p.b else '']
    table = [s[4:] if g.match_word(s, 0, '@url') else s for s in table]
    table = [s.strip() for s in table if s.strip()]
    # First, check for url's with an explicit scheme.
    for s in table:
        if g.isValidUrl(s):
            return s
    # Next check for existing file and add a file:// scheme.
    for s in table:
        tag = 'file://'
        url = computeFileUrl(s, c=c, p=p)
        if url.startswith(tag):
            fn = url[len(tag) :].lstrip()
            fn = fn.split('#', 1)[0]
            if g.os_path_isfile(fn):
                # Return the *original* url, with a file:// scheme.
                # g.handleUrl will call computeFileUrl again.
                return 'file://' + s
    # Finally, check for local url's.
    for s in table:
        if s.startswith("#"):
            return s
    return None
#@+node:tbrown.20090219095555.63: *3* g.handleUrl & helpers
def handleUrl(url, c=None, p=None):
    """Open a url or a unl."""
    if c and not p:
        p = c.p
    urll = url.lower()
    if urll.startswith('@url'):
        url = url[4:].lstrip()
    if (
        urll.startswith('unl:' + '//') or
        urll.startswith('file://') and url.find('-->') > -1 or
        urll.startswith('#')
    ):
        return g.handleUnl(url, c)
    try:
        return g.handleUrlHelper(url, c, p)
    except Exception:
        g.es_print("exception opening", repr(url))
        g.es_exception()
        return None
#@+node:ekr.20170226054459.1: *4* g.handleUrlHelper
def handleUrlHelper(url, c, p):
    """Open a url.  Most browsers should handle:
        ftp://ftp.uu.net/public/whatever
        http://localhost/MySiteUnderDevelopment/index.html
        file:///home/me/todolist.html
    """
    tag = 'file://'
    original_url = url
    if url.startswith(tag) and not url.startswith(tag + '#'):
        # Finalize the path *before* parsing the url.
        url = g.computeFileUrl(url, c=c, p=p)
    parsed = urlparse.urlparse(url)
    if parsed.netloc:
        leo_path = os.path.join(parsed.netloc, parsed.path)
        # "readme.txt" gets parsed into .netloc...
    else:
        leo_path = parsed.path
    if leo_path.endswith('\\'): leo_path = leo_path[:-1]
    if leo_path.endswith('/'): leo_path = leo_path[:-1]
    if parsed.scheme == 'file' and leo_path.endswith('.leo'):
        g.handleUnl(original_url, c)
    elif parsed.scheme in ('', 'file'):
        unquote_path = g.unquoteUrl(leo_path)
        if g.unitTesting:
            g.app.unitTestDict['os_startfile'] = unquote_path
        elif g.os_path_exists(leo_path):
            g.os_startfile(unquote_path)
        else:
            g.es(f"File '{leo_path}' does not exist")
    else:
        #Transcrypt does not support Python's webbrowser module.
        # __pragma__ ('skip')

        import webbrowser
        if g.unitTesting:
            g.app.unitTestDict['browser'] = url
        else:
            # Mozilla throws a weird exception, then opens the file!
            try:
                webbrowser.open(url)
            except Exception:
                pass

        # __pragma__ ('noskip')
#@+node:ekr.20170226060816.1: *4* g.traceUrl
def traceUrl(c, path, parsed, url):

    print()
    g.trace('url          ', url)
    g.trace('c.frame.title', c.frame.title)
    g.trace('path         ', path)
    g.trace('parsed.fragment', parsed.fragment)
    g.trace('parsed.netloc', parsed.netloc)
    g.trace('parsed.path  ', parsed.path)
    g.trace('parsed.scheme', repr(parsed.scheme))
#@+node:ekr.20170221063527.1: *3* g.handleUnl
def handleUnl(unl, c):
    """Handle a Leo UNL. This must *never* open a browser."""
    if not unl:
        return None
    unll = unl.lower()
    if unll.startswith('unl:' + '//'):
        unl = unl[6:]
    elif unll.startswith('file://'):
        unl = unl[7:]
    unl = unl.strip()
    if not unl:
        return None
    unl = g.unquoteUrl(unl)
    # Compute path and unl.
    if unl.find('#') == -1 and unl.find('-->') == -1:
        # The path is the entire unl.
        path, unl = unl, None
    elif unl.find('#') == -1:
        # The path is empty.
        # Move to the unl in *this* commander.
        g.recursiveUNLSearch(unl.split("-->"), c, soft_idx=True)
        return c
    else:
        path, unl = unl.split('#', 1)
    if not path:
        # Move to the unl in *this* commander.
        g.recursiveUNLSearch(unl.split("-->"), c, soft_idx=True)
        return c
    if c:
        base = g.os_path_dirname(c.fileName())
        c_path = g.os_path_finalize_join(base, path)
    else:
        c_path = None
    # Look for the file in various places.
    table = (
        c_path,
        g.os_path_finalize_join(g.app.loadDir, '..', path),
        g.os_path_finalize_join(g.app.loadDir, '..', '..', path),
        g.os_path_finalize_join(g.app.loadDir, '..', 'core', path),
        g.os_path_finalize_join(g.app.loadDir, '..', 'config', path),
        g.os_path_finalize_join(g.app.loadDir, '..', 'dist', path),
        g.os_path_finalize_join(g.app.loadDir, '..', 'doc', path),
        g.os_path_finalize_join(g.app.loadDir, '..', 'test', path),
        g.app.loadDir,
        g.app.homeDir,
    )
    for path2 in table:
        if path2 and path2.lower().endswith('.leo') and os.path.exists(path2):
            path = path2
            break
    else:
        g.es_print('path not found', repr(path))
        return None
    # End editing in *this* outline, so typing in the new outline works.
    c.endEditing()
    c.redraw()
    if g.unitTesting:
        g.app.unitTestDict['g.recursiveUNLSearch'] = path
    else:
        c2 = g.openWithFileName(path, old_c=c)
        if unl:
            g.recursiveUNLSearch(unl.split("-->"), c2 or c, soft_idx=True)
        if c2:
            c2.bringToFront()
            return c2
    return None
#@+node:ekr.20120311151914.9918: *3* g.isValidUrl
def isValidUrl(url):
    """Return true if url *looks* like a valid url."""
    table = (
        'file', 'ftp', 'gopher', 'hdl', 'http', 'https', 'imap',
        'mailto', 'mms', 'news', 'nntp', 'prospero', 'rsync', 'rtsp', 'rtspu',
        'sftp', 'shttp', 'sip', 'sips', 'snews', 'svn', 'svn+ssh', 'telnet', 'wais',
    )
    if url.lower().startswith('unl:' + '//') or url.startswith('#'):
        # All Leo UNL's.
        return True
    if url.startswith('@'):
        return False
    parsed = urlparse.urlparse(url)
    scheme = parsed.scheme
    for s in table:
        if scheme.startswith(s):
            return True
    return False
#@+node:ekr.20120315062642.9744: *3* g.openUrl
def openUrl(p):
    """
    Open the url of node p.
    Use the headline if it contains a valid url.
    Otherwise, look *only* at the first line of the body.
    """
    if p:
        url = g.getUrlFromNode(p)
        if url:
            c = p.v.context
            if not g.doHook("@url1", c=c, p=p, url=url):
                g.handleUrl(url, c=c, p=p)
            g.doHook("@url2", c=c, p=p, url=url)
#@+node:ekr.20110605121601.18135: *3* g.openUrlOnClick (open-url-under-cursor)
def openUrlOnClick(event, url=None):
    """Open the URL under the cursor.  Return it for unit testing."""
    # This can be called outside Leo's command logic, so catch all exceptions.
    try:
        return openUrlHelper(event, url)
    except Exception:
        g.es_exception()
        return None
#@+node:ekr.20170216091704.1: *4* g.openUrlHelper
def openUrlHelper(event, url=None):
    """Open the UNL or URL under the cursor.  Return it for unit testing."""
    c = getattr(event, 'c', None)
    if not c:
        return None
    w = getattr(event, 'w', c.frame.body.wrapper)
    if not g.app.gui.isTextWrapper(w):
        g.internalError('must be a text wrapper', w)
        return None
    setattr(event, 'widget', w)
    # Part 1: get the url.
    if url is None:
        s = w.getAllText()
        ins = w.getInsertPoint()
        i, j = w.getSelectionRange()
        if i != j:
            return None  # So find doesn't open the url.
        row, col = g.convertPythonIndexToRowCol(s, ins)
        i, j = g.getLine(s, ins)
        line = s[i:j]
        # Find the url on the line.
        for match in g.url_regex.finditer(line):
            # Don't open if we click after the url.
            if match.start() <= col < match.end():
                url = match.group()
                if g.isValidUrl(url):
                    break
        else:
            # Look for the unl:
            for match in g.unl_regex.finditer(line):
                # Don't open if we click after the unl.
                if match.start() <= col < match.end():
                    unl = match.group()
                    g.handleUnl(unl, c)
                    return None
    elif not isinstance(url, str):
        url = url.toString()
        url = g.toUnicode(url)
            # Fix #571
    if url and g.isValidUrl(url):
        # Part 2: handle the url
        p = c.p
        if not g.doHook("@url1", c=c, p=p, url=url):
            g.handleUrl(url, c=c, p=p)
        g.doHook("@url2", c=c, p=p)
        return url
    # Part 3: call find-def.
    if not w.hasSelection():
        c.editCommands.extendToWord(event, select=True)
    word = w.getSelectedText().strip()
    if word:
        c.findCommands.findDef(event)
    return None
#@-others
# set g when the import is about to complete.
g = sys.modules.get('leo.core.leoGlobals')
assert g, sorted(sys.modules.keys())

if __name__ == '__main__':
    unittest.main()
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
