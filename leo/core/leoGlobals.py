#@+leo-ver=5-thin
#@+node:ekr.20031218072017.3093: * @file leoGlobals.py
"""
Global constants, variables and utility functions used throughout Leo.

Important: This module imports no other Leo module.
"""
#@+<< leoGlobals imports >>
#@+node:ekr.20050208101229: ** << leoGlobals imports >>
from __future__ import annotations
import binascii
from collections.abc import Callable
import codecs
import copy
import fnmatch
from functools import reduce
import gc
import gettext
import glob
import importlib
import inspect
import io
import operator
import os
from pathlib import Path
# import pdb  # Do NOT import pdb here! g.pdb is a *function*
import pprint
import re
import shlex
import string
import sys
import subprocess
import tempfile
import textwrap
import time
import traceback
import types
from typing import Any, Generator, Iterable, Optional, Sequence, Union, TYPE_CHECKING
import unittest
import urllib
import urllib.parse as urlparse

# Leo never imports any other Leo module.

# Third-party tools.
import webbrowser
try:
    import tkinter as Tk
except Exception:
    Tk = None
#
# Abbreviations...
StringIO = io.StringIO
#@-<< leoGlobals imports >>
#@+<< leoGlobals annotations >>
#@+node:ekr.20220824084642.1: ** << leoGlobals annotations >>
if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoGui
    from leo.core.leoNodes import Position, VNode
    Event = Any
#@-<< leoGlobals annotations >>
in_bridge = False  # True: leoApp object loads a null Gui.
in_vs_code = False  # #2098.
minimum_python_version = '3.9'
isPython3 = sys.version_info >= (3, 0, 0)  # Not used in Leo's core.
isMac = sys.platform.startswith('darwin')
isWindows = sys.platform.startswith('win')
#@+<< define g.globalDirectiveList >>
#@+node:EKR.20040610094819: ** << define g.globalDirectiveList >>
# Visible externally so plugins may add to the list of directives.
# The atFile write logic uses this, but not the atFile read logic.
globalDirectiveList = [
    # Order does not matter.
    'all',
    'beautify',
    'colorcache', 'code', 'color', 'comment', 'c',
    'delims', 'doc',
    'encoding',
    # 'end_raw',  # #2276.
    'first', 'header', 'ignore',
    'killbeautify', 'killcolor',
    'language', 'last', 'lineending',
    'markup',
    'nobeautify',
    'nocolor-node', 'nocolor', 'noheader', 'nowrap',
    'nopyflakes',  # Leo 6.1.
    'nosearch',  # Leo 5.3.
    'others', 'pagewidth', 'path', 'quiet',
    # 'raw',  # #2276.
    'section-delims',  # Leo 6.6. #2276.
    'silent',
    'tabwidth',
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
#     def cmd(name: Any) -> Any:
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
#@+<< define global error regexes >>
#@+node:ekr.20220412193109.1: ** << define global error regexes >> (leoGlobals.py)
# Most code need only know about the *existence* of these patterns.

# For all *present* patterns, m.group(1) is the filename and m.group(2) is the line number.

# See link_table above LeoLog.put_html_links.

flake8_pat = re.compile(r'(.+?):([0-9]+):[0-9]+:.*$')
mypy_pat = re.compile(r'^(.+?):([0-9]+):\s*(error|note)\s*(.*)\s*$')
pyflakes_pat = re.compile(r'^(.*):([0-9]+):[0-9]+ .*?$')
pylint_pat = re.compile(r'^(.*):\s*([0-9]+)[,:]\s*[0-9]+:.*?\(.*\)\s*$')
python_pat = re.compile(r'^\s*File\s+"(.*?)",\s*line\s*([0-9]+)\s*$')
#@-<< define global error regexes >>
#@+<< define g.decorators >>
#@+node:ekr.20150508165324.1: ** << define g.Decorators >>
#@+others
#@+node:ekr.20150510104148.1: *3* g.check_cmd_instance_dict
def check_cmd_instance_dict(c: Cmdr, g: Any) -> None:
    """
    Check g.check_cmd_instance_dict.
    This is a permanent unit test, called from c.finishCreate.
    """
    d = cmd_instance_dict
    for key in d:
        ivars = d.get(key)
        # Produces warnings.
        obj = ivars2instance(c, g, ivars)  # type:ignore
        if obj:
            name = obj.__class__.__name__
            if name != key:
                g.trace('class mismatch', key, name)
#@+node:ville.20090521164644.5924: *3* g.command (decorator)
class Command:
    """
    A global decorator for creating commands.

    This is the recommended way of defining all new commands, including
    commands that could be defined inside a class. The typical usage is:

        @g.command('command-name')
        def A_Command(event):
            c = event.get('c')
            ...

    g can *not* be used anywhere in this class!
    """

    def __init__(self, name: str, **kwargs: Any) -> None:
        """Ctor for command decorator class."""
        self.name = name

    def __call__(self, func: Callable) -> Callable:
        """Register command for all future commanders."""
        global_commands_dict[self.name] = func
        if app:
            for c in app.commanders():
                c.k.registerCommand(self.name, func)
        # Inject ivars for plugins_menu.py.
        func.__func_name__ = func.__name__  # For leoInteg.
        func.is_command = True
        func.command_name = self.name
        return func

command = Command
#@+node:ekr.20171124070654.1: *3* g.command_alias
def command_alias(alias: str, func: Callable) -> None:
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

    def __init__(self, name: str, **kwargs: Any) -> None:
        """Ctor for command decorator class."""
        self.name = name

    def __call__(self, func: Callable) -> Callable:
        """Register command for all future commanders."""

        def commander_command_wrapper(event: Any) -> None:
            c = event.get('c')
            method = getattr(c, func.__name__, None)
            method(event=event)

        # Inject ivars for plugins_menu.py.
        commander_command_wrapper.__func_name__ = func.__name__  # For leoInteg.
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
def ivars2instance(c: Cmdr, g: Any, ivars: list[str]) -> Any:
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
def new_cmd_decorator(name: str, ivars: list[str]) -> Callable:
    """
    Return a new decorator for a command with the given name.
    Compute the class *instance* using the ivar string or list.

    Don't even think about removing the @cmd decorators!
    See https://github.com/leo-editor/leo-editor/issues/325
    """

    def _decorator(func: Callable) -> Callable:

        def new_cmd_wrapper(event: Any) -> None:
            if isinstance(event, dict):
                c = event.get('c')
            else:
                c = event.c
            self = g.ivars2instance(c, g, ivars)
            try:
                # Don't use a keyword for self.
                # This allows the VimCommands class to use vc instead.
                func(self, event=event)
            except Exception:
                g.es_exception()

        new_cmd_wrapper.__func_name__ = func.__name__  # For leoInteg.
        new_cmd_wrapper.__name__ = name
        new_cmd_wrapper.__doc__ = func.__doc__
        # Put the *wrapper* into the global dict.
        global_commands_dict[name] = new_cmd_wrapper
        return func  # The decorator must return the func itself.

    return _decorator
#@-others
#@-<< define g.decorators >>
#@+<< define regexes >>
#@+node:ekr.20200810093517.1: ** << define regexes >> (leoGlobals.py)
# Regex used by this module, and in leoColorizer.py.
g_language_pat = re.compile(r'^@language\s+(\w+)+', re.MULTILINE)

# g_is_directive_pattern excludes @encoding.whatever and @encoding(whatever)
# It must allow @language python, @nocolor-node, etc.
g_is_directive_pattern = re.compile(r'^\s*@([\w-]+)\s*')
g_tabwidth_pat = re.compile(r'(^@tabwidth)', re.MULTILINE)

# #2267: Support for @section-delims.
g_section_delims_pat = re.compile(r'^@section-delims[ \t]+([^ \w\n\t]+)[ \t]+([^ \w\n\t]+)[ \t]*$')

# Patterns used by the colorizer...

# New in Leo 6.6.4: gnxs must start with 'gnx:'
gnx_char = r"""[^.,"'\s]"""  # LeoApp.cleanLeoID() removes these characters.
gnx_id = fr"{gnx_char}{{3,}}"  # id's must have at least three characters.
gnx_regex = re.compile(fr"\bgnx:{gnx_id}\.[0-9]+\.[0-9]+")

# Unls end with quotes.
unl_regex = re.compile(r"""\bunl:[^`'"]+""")

# Urls end at space or quotes.
url_leadins = 'fghmnptw'
url_kinds = '(file|ftp|gopher|http|https|mailto|news|nntp|prospero|telnet|wais)'
url_regex = re.compile(fr"""\b{url_kinds}://[^\s'"]+""")
#@-<< define regexes >>
tree_popup_handlers: list[Callable] = []  # Set later.
user_dict: dict[Any, Any] = {}  # Non-persistent dictionary for scripts and plugins.
app: Any = None  # The singleton app object. Set by runLeo.py.
# Global status vars.
inScript = False  # A synonym for app.inScript
unitTesting = False  # A synonym for app.unitTesting.
#@+others
#@+node:ekr.20201211182722.1: ** g.Backup
#@+node:ekr.20201211182659.1: *3* g.standard_timestamp
def standard_timestamp() -> str:
    """Return a reasonable timestamp."""
    return time.strftime("%Y%m%d-%H%M%S")
#@+node:ekr.20201211183100.1: *3* g.get_backup_directory
def get_backup_path(sub_directory: str) -> Optional[str]:
    """
    Return the full path to the subdirectory of the main backup directory.

    The main backup directory is computed as follows:

    1. os.environ['LEO_BACKUP']
    2. ~/Backup
    """
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
        kind: str,
        commandName: str = '',
        func: Callable = None,
        nextMode: str = None,
        pane: str = None,
        stroke: "KeyStroke" = None,
    ) -> None:
        if not g.isStrokeOrNone(stroke):
            g.trace('***** (BindingInfo) oops', repr(stroke))
        self.kind = kind
        self.commandName = commandName
        self.func = func
        self.nextMode = nextMode
        self.pane = pane
        self.stroke = stroke  # The *caller* must canonicalize the shortcut.
    #@+node:ekr.20120203153754.10031: *4* bi.__hash__
    def __hash__(self) -> Any:
        return self.stroke.__hash__() if self.stroke else 0
    #@+node:ekr.20120125045244.10188: *4* bi.__repr__ & ___str_& dump
    def __repr__(self) -> str:
        return self.dump()

    __str__ = __repr__

    def dump(self) -> str:
        result = [f"BindingInfo kind: {self.kind}"]
        # Print all existing ivars.
        table = ('pane', 'commandName', 'func', 'stroke')  # 'nextMode',
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
        return "<%s>" % ' '.join(result).strip()
    #@+node:ekr.20120129040823.10226: *4* bi.isModeBinding
    def isModeBinding(self) -> bool:
        return self.kind.startswith('*mode')
    #@-others

def isBindingInfo(obj: Any) -> bool:
    return isinstance(obj, BindingInfo)
#@+node:ekr.20031218072017.3098: *3* class g.Bunch (Python Cookbook)
class Bunch:
    """
    From The Python Cookbook:

        Create a Bunch whenever you want to group a few variables:

            point = Bunch(datum=y, squared=y*y, coord=x)

        You can read/write the named attributes you just created, add others,
        del some of them, etc::

            if point.squared > threshold:
                point.isok = True
    """

    def __init__(self, **keywords: Any) -> None:
        self.__dict__.update(keywords)

    def __repr__(self) -> str:
        return self.toString()

    def ivars(self) -> list:
        return sorted(self.__dict__)

    def keys(self) -> list:
        return sorted(self.__dict__)

    def toString(self) -> str:
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

    def __setitem__(self, key: str, value: Any) -> Any:
        """Support aBunch[key] = val"""
        return operator.setitem(self.__dict__, key, value)

    def __getitem__(self, key: str) -> Any:
        """Support aBunch[key]"""
        # g.pr('g.Bunch.__getitem__', key)
        return operator.getitem(self.__dict__, key)

    def get(self, key: str, theDefault: Any = None) -> Any:
        return self.__dict__.get(key, theDefault)

    def __contains__(self, key: str) -> bool:  # New.
        # g.pr('g.Bunch.__contains__', key in self.__dict__, key)
        return key in self.__dict__

bunch = Bunch
#@+node:ekr.20120219154958.10492: *3* class g.EmergencyDialog
class EmergencyDialog:
    """
    A class that creates an tkinter dialog with a single OK button.

    If tkinter doesn't exist (#2512), this class just prints the message
    passed to the ctor.

    """
    #@+others
    #@+node:ekr.20120219154958.10493: *4* emergencyDialog.__init__
    def __init__(self, title: str, message: str) -> None:
        """Constructor for the leoTkinterDialog class."""
        self.answer = None  # Value returned from run()
        self.title = title
        self.message = message
        self.buttonsFrame = None  # Frame to hold typical dialog buttons.
        # Command to call when user click's the window's close box.
        self.defaultButtonCommand = None
        self.frame = None  # The outermost frame.
        self.root = None  # Created in createTopFrame.
        self.top = None  # The toplevel Tk widget.
        if Tk:  # #2512.
            self.createTopFrame()
            buttons = [{
                "text": "OK",
                "command": self.okButton,
                "default": True,
            }]
            self.createButtons(buttons)
            self.top.bind("<Key>", self.onKey)
        else:
            print(message.rstrip() + '\n')
    #@+node:ekr.20120219154958.10494: *4* emergencyDialog.createButtons
    def createButtons(self, buttons: list[dict[str, Any]]) -> list[Any]:
        """Create a row of buttons.

        buttons is a list of dictionaries containing
        the properties of each button.
        """
        assert self.frame
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
    def createTopFrame(self) -> None:
        """Create the Tk.Toplevel widget for a leoTkinterDialog."""
        self.root = Tk.Tk()  # type:ignore
        self.top = Tk.Toplevel(self.root)  # type:ignore
        self.top.title(self.title)
        self.root.withdraw()  # This root window should *never* be shown.
        self.frame = Tk.Frame(self.top)  # type:ignore
        self.frame.pack(side="top", expand=1, fill="both")
        label = Tk.Label(self.frame, text=self.message, bg='white')
        label.pack(pady=10)
    #@+node:ekr.20120219154958.10496: *4* emergencyDialog.okButton
    def okButton(self) -> None:
        """Do default click action in ok button."""
        self.top.destroy()
        self.top = None
    #@+node:ekr.20120219154958.10497: *4* emergencyDialog.onKey
    def onKey(self, event: Any) -> None:
        """Handle Key events in askOk dialogs."""
        self.okButton()
    #@+node:ekr.20120219154958.10498: *4* emergencyDialog.run
    def run(self) -> None:
        """Run the modal emergency dialog."""
        # Suppress f-stringify.
        self.top.geometry("%dx%d%+d%+d" % (300, 200, 50, 50))
        self.top.lift()
        self.top.grab_set()  # Make the dialog a modal dialog.
        self.root.wait_window(self.top)
    #@-others
#@+node:ekr.20120123143207.10223: *3* class g.GeneralSetting
class GeneralSetting:
    """A class representing any kind of setting except shortcuts."""
    # Important: The startup code uses this class,
    # so it is convenient to define it in leoGlobals.py.

    def __init__(
        self,
        kind: str,
        encoding: str = None,
        ivar: str = None,
        source: str = None,
        val: Any = None,
        path: str = None,
        tag: str = 'setting',
        unl: str = None,
    ) -> None:
        self.encoding = encoding
        self.ivar = ivar
        self.kind = kind
        self.path = path
        self.unl = unl
        self.source = source  # Only @font sets this.
        self.val = val
        self.tag = tag

    def __repr__(self) -> str:
        # Better for g.printObj.
        val = str(self.val).replace('\n', ' ')
        return (
            f"GS: path: {g.shortFileName(self.path or '')} "
            f"source: {self.source or ''} "
            f"kind: {self.kind:} val: {val}")

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
    def __init__(self, binding: str) -> None:

        self.s: str
        if binding:
            self.s = self.finalize_binding(binding)
        else:
            self.s = None
    #@+node:ekr.20120203053243.10117: *4* ks.__eq__, etc
    #@+at All these must be defined in order to say, for example:
    #     for key in sorted(d)
    # where the keys of d are KeyStroke objects.
    #@@c

    def __eq__(self, other: Any) -> bool:
        if not other:
            return False
        if hasattr(other, 's'):
            return self.s == other.s
        return self.s == other

    def __lt__(self, other: Any) -> bool:
        if not other:
            return False
        if hasattr(other, 's'):
            return self.s < other.s
        return self.s < other

    def __le__(self, other: Any) -> bool:
        return self.__lt__(other) or self.__eq__(other)

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __gt__(self, other: Any) -> bool:
        return not self.__lt__(other) and not self.__eq__(other)

    def __ge__(self, other: Any) -> bool:
        return not self.__lt__(other)
    #@+node:ekr.20120203053243.10118: *4* ks.__hash__
    # Allow KeyStroke objects to be keys in dictionaries.

    def __hash__(self) -> Any:
        return self.s.__hash__() if self.s else 0
    #@+node:ekr.20120204061120.10067: *4* ks.__repr___ & __str__
    def __repr__(self) -> str:
        return f"<KeyStroke: {repr(self.s)}>"

    def __str__(self) -> str:
        return repr(self.s)
    #@+node:ekr.20180417160703.1: *4* ks.dump
    def dump(self) -> None:
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
    def finalize_binding(self, binding: str) -> str:

        # This trace is good for devs only.
        trace = False and 'keys' in g.app.debug
        self.mods = self.find_mods(binding)
        s = self.strip_mods(binding)
        s = self.finalize_char(s)  # May change self.mods.
        mods = ''.join([f"{z.capitalize()}+" for z in self.mods])
        if trace and 'meta' in self.mods:
            g.trace(f"{binding:20}:{self.mods:>20} ==> {mods+s}")
        return mods + s
    #@+node:ekr.20180415083926.1: *4* ks.finalize_char & helper
    def finalize_char(self, s: str) -> str:
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
            # Returning '' breaks existing code.
            return shift_d.get(s.lower())
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
            return self.strip_shift(s)  # type:ignore
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
    def strip_shift(self, s: str) -> str:
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

    def find(self, pattern: str) -> int:
        return self.s.find(pattern)

    def lower(self) -> str:
        return self.s.lower()

    def startswith(self, s: str) -> bool:
        return self.s.startswith(s)
    #@+node:ekr.20180415081209.2: *4* ks.find_mods
    def find_mods(self, s: str) -> list[str]:
        """Return the list of all modifiers seen in s."""
        s = s.lower()
        table = (
            ['alt',],
            ['command', 'cmd',],
            ['ctrl', 'control',],  # Use ctrl, not control.
            ['meta',],
            ['shift', 'shft',],
            # 868: Allow alternative spellings.
            ['keypad', 'key_pad', 'numpad', 'num_pad'],
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
    def isAltCtrl(self) -> bool:
        """Return True if this is an Alt-Ctrl character."""
        mods = self.find_mods(self.s)
        return 'alt' in mods and 'ctrl' in mods
    #@+node:ekr.20120203053243.10121: *4* ks.isFKey
    def isFKey(self) -> bool:
        return self.s in g.app.gui.FKeys
    #@+node:ekr.20180417102341.1: *4* ks.isPlainKey (does not handle alt-ctrl chars)
    def isPlainKey(self) -> bool:
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
    def isNumPadKey(self) -> bool:
        return self.s.find('Keypad+') > -1

    def isPlainNumPad(self) -> bool:
        return (
            self.isNumPadKey() and
            len(self.s.replace('Keypad+', '')) == 1
        )

    def removeNumPadModifier(self) -> None:
        self.s = self.s.replace('Keypad+', '')
    #@+node:ekr.20180419170934.1: *4* ks.prettyPrint
    def prettyPrint(self) -> str:

        s = self.s
        if not s:
            return '<None>'
        d = {' ': 'Space', '\t': 'Tab', '\n': 'Return', '\r': 'LineFeed'}
        ch = s[-1]
        return s[:-1] + d.get(ch, ch)
    #@+node:ekr.20180415124853.1: *4* ks.strip_mods
    def strip_mods(self, s: str) -> str:
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
    def toGuiChar(self) -> str:
        """Replace special chars by the actual gui char."""
        s = self.s.lower()
        if s in ('\n', 'return'):
            s = '\n'
        elif s in ('\t', 'tab'):
            s = '\t'
        elif s in ('\b', 'backspace'):
            s = '\b'
        elif s in ('.', 'period'):
            s = '.'
        return s
    #@+node:ekr.20180417100834.1: *4* ks.toInsertableChar
    def toInsertableChar(self) -> str:
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

def isStroke(obj: Any) -> bool:
    return isinstance(obj, KeyStroke)

def isStrokeOrNone(obj: Any) -> bool:
    return obj is None or isinstance(obj, KeyStroke)
#@+node:ekr.20160119093947.1: *3* class g.MatchBrackets
class MatchBrackets:
    """
    A class implementing the match-brackets command.

    In the interest of speed, the code assumes that the user invokes the
    match-bracket command outside of any string, comment or (for perl or
    javascript) regex.
    """
    #@+others
    #@+node:ekr.20160119104510.1: *4* mb.ctor
    def __init__(self, c: Cmdr, p: Position, language: str) -> None:
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
    def is_regex(self, s: str, i: int) -> bool:
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
    def scan_regex(self, s: str, i: int) -> int:
        """Scan a regex (or regex substitution for perl)."""
        assert s[i] == '/'
        offset = 1 if self.forward else -1
        i1 = i
        i += offset
        found: Union[int, bool] = False
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
    def scan_string(self, s: str, i: int) -> int:
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
    def expand_range(
        self,
        s: str,
        left: int,
        right: int,
        max_right: int,
        expand: bool = False,
    ) -> tuple[Any, Any, Any, Any]:
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
        expanded: Union[bool, str] = False
        left = max(0, min(left, len(s)))  # #2240
        right = max(0, min(right, len(s)))  # #2240
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
    def find_matching_bracket(self, ch1: str, s: str, i: int) -> Any:
        """Find the bracket matching s[i] for self.language."""
        self.forward = ch1 in self.open_brackets
        # Find the character matching the initial bracket.
        for n in range(len(self.brackets)):  # pylint: disable=consider-using-enumerate
            if ch1 == self.brackets[n]:
                target = self.matching_brackets[n]
                break
        else:
            return None
        f = self.scan if self.forward else self.scan_back
        return f(ch1, target, s, i)
    #@+node:ekr.20160121164556.1: *4* mb.scan & helpers
    def scan(self, ch1: str, target: str, s: str, i: int) -> Optional[int]:
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
    def scan_comment(self, s: str, i: int) -> Optional[int]:
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
    def starts_comment(self, s: str, i: int) -> bool:
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
    def scan_back(self, ch1: str, target: str, s: str, i: int) -> Optional[int]:
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
    def back_scan_comment(self, s: str, i: int) -> int:
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
    def ends_comment(self, s: str, i: int) -> bool:
        """
        Return True if s[i] ends a comment. This is called while scanning
        backward, so this is a bit of a guess.
        """
        if s[i] == '\n':
            # This is the hard (dubious) case.
            # Let w, x, y and z stand for any strings not containing // or quotes.
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
    def oops(self, s: str) -> None:
        """Report an error in the match-brackets command."""
        g.es(s, color='red')
    #@+node:ekr.20160119094053.1: *4* mb.run
    #@@nobeautify

    def run(self) -> None:
        """The driver for the MatchBrackets class.

        With no selected range: find the nearest bracket and select from
        it to it's match, moving cursor to match.

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
#@+node:ekr.20230616134732.1: *3* class g.OptionsUtils
class OptionsUtils:
    """
    A stateless class for handling command-line options.

    This class *calculates* valid options from the usage message.
    """

    def __init__(self, usage: str, obsolete_options: list[str] = None) -> None:
        # This class is essentially stateless because these ivars never change.
        self.usage = usage
        self.obsolete_options = obsolete_options
        self.valid_options = self.compute_valid_options()
        self.check_options()

    #@+others
    #@+node:ekr.20230615034937.1: *4* OptionsUtils.check_options
    def check_options(self) -> None:
        """Make sure all command-line options pass sanity checks."""
        option_prefixes = [z[:-1] for z in self.valid_options if z.endswith('=')]
        for arg in sys.argv:
            if arg in self.obsolete_options:
                print(f"Ignoring obsolete option: {arg!r}")
            elif arg.startswith('-'):
                for option in self.valid_options:
                    if arg.startswith(option) and not arg.endswith('='):
                        break
                else:
                    for prefix in option_prefixes:
                        if arg.startswith(prefix):
                            self.option_error(arg, 'Missing value')
                    self.option_error(arg, 'Unknown option')
            else:
                # Do a simple check for file arguments.
                if any(z in arg for z in ',='):
                    self.option_error(arg, 'Invalid file arg')
    #@+node:ekr.20230615062610.1: *4* OptionsUtils.compute_valid_options
    def compute_valid_options(self) -> list[str]:
        """
        Return a list of valid options by parsing the given usage message.
        Options requiring an argument end with '='.
        """
        # Abbreviations (-whatever) must appear before full options (--whatever).
        option_pattern = re.compile(r'\s*(-\w)?,?\s*(--[\w-]+=?)')
        valid = ['-?']
        for line in g.splitLines(self.usage):
            m = option_pattern.match(line)
            if m:
                if m.group(1):
                    valid.append(m.group(1))
                if m.group(2):
                    valid.append(m.group(2))
        return sorted(list(set(valid)))
    #@+node:ekr.20230615084117.1: *4* OptionsUtils.find_complex_option
    def find_complex_option(self, regex: str) -> Optional[re.Match]:
        """
        Check arguments that take an argument.

        Exit if the option exists but contains argument.
        """
        assert '=' in regex, repr(regex)
        prefix = regex.split('=')[0]
        for arg in sys.argv:
            if arg.split('=')[0] == prefix:
                m = re.match(regex, arg)
                if m:
                    return m
                self.option_error(arg, 'Missing or erroneous value')
        return None
    #@+node:ekr.20230616075049.1: *4* OptionsUtils.option_error
    def option_error(self, arg: str, message: str) -> None:
        """Print an error message and help message, then exit."""
        g.trace(g.callers(6))
        message2 = f"Invalid {arg!r} option: {message}"
        print(message2)
        print(self.usage)
        print(message2)
        sys.exit(1)
    #@-others
#@+node:EKR.20040612114220.4: *3* class g.ReadLinesClass
class ReadLinesClass:
    """A class whose next method provides a readline method for Python's tokenize module."""

    def __init__(self, s: str) -> None:
        self.lines = g.splitLines(s)
        self.i = 0

    def next(self) -> str:
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
    def __init__(self) -> None:
        self.old = None
        self.encoding = 'utf-8'  # 2019/03/29 For pdb.
    #@+node:ekr.20041012082437.1: *5* isRedirected
    def isRedirected(self) -> bool:
        return self.old is not None
    #@+node:ekr.20041012082437.2: *5* flush
    # For LeoN: just for compatibility.

    def flush(self, *args: Any) -> None:
        return
    #@+node:ekr.20041012091252: *5* rawPrint
    def rawPrint(self, s: str) -> None:
        if self.old:
            self.old.write(s + '\n')
        else:
            g.pr(s)
    #@+node:ekr.20041012082437.3: *5* redirect
    def redirect(self, stdout: bool = True) -> None:
        if g.app.batchMode:
            # Redirection is futile in batch mode.
            return
        if not self.old:
            if stdout:
                self.old, sys.stdout = sys.stdout, self  # type:ignore
            else:
                self.old, sys.stderr = sys.stderr, self  # type:ignore
    #@+node:ekr.20041012082437.4: *5* undirect
    def undirect(self, stdout: bool = True) -> None:
        if self.old:
            if stdout:
                sys.stdout, self.old = self.old, None
            else:
                sys.stderr, self.old = self.old, None
    #@+node:ekr.20041012082437.5: *5* write
    def write(self, s: str) -> None:

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

def redirectStderr() -> None:
    global redirectStdErrObj
    redirectStdErrObj.redirect(stdout=False)

def redirectStdout() -> None:
    global redirectStdOutObj
    redirectStdOutObj.redirect()
#@+node:ekr.20041012090942.1: *5* restoreStderr & restoreStdout
# Restore standard streams.

def restoreStderr() -> None:
    global redirectStdErrObj
    redirectStdErrObj.undirect(stdout=False)

def restoreStdout() -> None:
    global redirectStdOutObj
    redirectStdOutObj.undirect()
#@+node:ekr.20041012090942.2: *5* stdErrIsRedirected & stdOutIsRedirected
def stdErrIsRedirected() -> bool:
    global redirectStdErrObj
    return redirectStdErrObj.isRedirected()

def stdOutIsRedirected() -> bool:
    global redirectStdOutObj
    return redirectStdOutObj.isRedirected()
#@+node:ekr.20041012090942.3: *5* rawPrint
# Send output to original stdout.

def rawPrint(s: str) -> None:
    global redirectStdOutObj
    redirectStdOutObj.rawPrint(s)
#@-others
#@-<< define convenience methods for redirecting streams >>
#@+node:ekr.20120129181245.10220: *3* class g.SettingsDict(dict)
class SettingsDict(dict):
    """A subclass of dict providing settings-related methods."""

    def __init__(self, name: str) -> None:
        super().__init__()
        self._name = name  # For __repr__ only.

    def __repr__(self) -> str:
        return f"<SettingsDict name:{self._name} "

    __str__ = __repr__

    #@+others
    #@+node:ekr.20120223062418.10422: *4* td.copy
    def copy(self, name: str = None) -> Any:
        """Return a new dict with the same contents."""
        # The result is a g.SettingsDict.
        return copy.deepcopy(self)
    #@+node:ekr.20190904052828.1: *4* td.add_to_list
    def add_to_list(self, key: str, val: Any) -> None:
        """Update the *list*, self.d [key]"""
        if key is None:
            g.trace('TypeDict: None is not a valid key', g.callers())
            return
        aList = self.get(key, [])
        if val not in aList:
            aList.append(val)
            self[key] = aList
    #@+node:ekr.20190903181030.1: *4* td.get_setting & get_string_setting
    def get_setting(self, key: str) -> Any:
        """Return the canonical setting name."""
        key = key.replace('-', '').replace('_', '')
        gs = self.get(key)
        val = gs and gs.val
        return val

    def get_string_setting(self, key: str) -> Optional[str]:
        val = self.get_setting(key)
        return val if val and isinstance(val, str) else None
    #@+node:ekr.20190904103552.1: *4* td.name & setName
    def name(self) -> str:
        return self._name

    def setName(self, name: str) -> None:
        self._name = name
    #@-others
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
    tracing for Rope's worder, prefs and resources modules.

    Being able to zero in on the code of interest can be a big help in
    studying other people's code. This is a non-invasive method: no tracing
    code needs to be inserted anywhere.

    Usage:

    g.SherlockTracer(patterns).run()
    """
    #@+others
    #@+node:ekr.20121128031949.12602: *4* sherlock.__init__
    def __init__(
        self,
        patterns: list[Any],
        indent: bool = True,
        show_args: bool = True,
        show_return: bool = True,
        verbose: bool = True,
    ) -> None:
        """SherlockTracer ctor."""
        self.bad_patterns: list[str] = []  # List of bad patterns.
        self.indent = indent  # True: indent calls and returns.
        self.contents_d: dict[str, list] = {}  # Keys are file names, values are file lines.
        self.n = 0  # The frame level on entry to run.
        self.stats: dict[str, dict] = {}  # Keys are full file names, values are dicts.
        self.patterns: list[Any] = None  # A list of regex patterns to match.
        self.pattern_stack: list[str] = []
        self.show_args = show_args  # True: show args for each function call.
        self.show_return = show_return  # True: show returns from each function.
        self.trace_lines = True  # True: trace lines in enabled functions.
        self.verbose = verbose  # True: print filename:func
        self.set_patterns(patterns)
        try:  # Don't assume g.app exists.
            from leo.core.leoQt import QtCore
            if QtCore:
                # pylint: disable=no-member
                QtCore.pyqtRemoveInputHook()
        except Exception:
            pass
    #@+node:ekr.20140326100337.16844: *4* sherlock.__call__
    def __call__(self, frame: Any, event: Any, arg: Any) -> Any:
        """Exists so that self.dispatch can return self."""
        return self.dispatch(frame, event, arg)
    #@+node:ekr.20140326100337.16846: *4* sherlock.bad_pattern
    def bad_pattern(self, pattern: Any) -> None:
        """Report a bad Sherlock pattern."""
        if pattern not in self.bad_patterns:
            self.bad_patterns.append(pattern)
            print(f"\nignoring bad pattern: {pattern}\n")
    #@+node:ekr.20140326100337.16847: *4* sherlock.check_pattern
    def check_pattern(self, pattern: str) -> bool:
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
    def dispatch(self, frame: Any, event: Any, arg: Any) -> Any:
        """The dispatch method."""
        if event == 'call':
            self.do_call(frame, arg)
        elif event == 'return' and self.show_return:
            self.do_return(frame, arg)
        elif event == 'line' and self.trace_lines:
            self.do_line(frame, arg)
        # Queue the SherlockTracer instance again.
        return self
    #@+node:ekr.20121128031949.12603: *4* sherlock.do_call & helper
    def do_call(self, frame: Any, unused_arg: Any) -> None:
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
        indent = ' ' * max(0, n - self.n) if self.indent else ''
        path = f"{os.path.basename(file_name):>20}" if self.verbose else ''
        leadin = '+' if self.show_return else ''
        args_list = self.get_args(frame1)
        if self.show_args and args_list:
            args_s = ','.join(args_list)
            args_s2 = f"({args_s})"
            if len(args_s2) > 100:
                print(f"{path}:{indent}{leadin}{full_name}")
                g.printObj(args_list, indent=len(indent) + 22)
            else:
                print(f"{path}:{indent}{leadin}{full_name}{args_s2}")
        else:
            print(f"{path}:{indent}{leadin}{full_name}")
        # Always update stats.
        d = self.stats.get(file_name, {})
        d[full_name] = 1 + d.get(full_name, 0)
        self.stats[file_name] = d
    #@+node:ekr.20130111185820.10194: *5* sherlock.get_args
    def get_args(self, frame: Any) -> list[str]:
        """Return a list of string "name=val" for each arg in the function call."""
        code = frame.f_code
        locals_ = frame.f_locals
        name = code.co_name
        n = code.co_argcount
        if code.co_flags & 4:
            n = n + 1
        if code.co_flags & 8:
            n = n + 1
        result = []
        for i in range(n):
            name = code.co_varnames[i]
            if name != 'self':
                arg = locals_.get(name, '*undefined*')
                if arg:
                    if isinstance(arg, (list, tuple)):
                        val_s = ','.join([self.show(z) for z in arg if self.show(z)])
                        val = f"[{val_s}]"
                    elif isinstance(arg, str):
                        val = arg
                    else:
                        val = self.show(arg)
                    if val:
                        result.append(f"{name}={val}")
        return result
    #@+node:ekr.20140402060647.16845: *4* sherlock.do_line (not used)
    bad_fns: list[str] = []

    def do_line(self, frame: Any, arg: Any) -> None:
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
    def do_return(self, frame: Any, arg: Any) -> None:  # Arg *is* used below.
        """Trace a return statement."""
        code = frame.f_code
        fn = code.co_filename
        locals_ = frame.f_locals
        name = code.co_name
        self.full_name = self.get_full_name(locals_, name)
        if not self.is_enabled(fn, self.full_name, self.patterns):
            return
        n = 0
        while frame:
            frame = frame.f_back
            n += 1
        path = f"{os.path.basename(fn):>20}" if self.verbose else ''
        if name and name == '__init__':
            try:
                ret1 = locals_ and locals_.get('self', None)
                self.put_ret(ret1, n, path)
            except NameError:
                self.put_ret(f"<{ret1.__class__.__name__}>", n, path)
        else:
            self.put_ret(arg, n, path)
    #@+node:ekr.20220605141445.1: *5* sherlock.put_ret
    def put_ret(self, arg: Any, n: int, path: str) -> None:
        """Print arg, the value returned by a "return" statement."""
        indent = ' ' * max(0, n - self.n + 1) if self.indent else ''
        try:
            if isinstance(arg, types.GeneratorType):
                ret = '<generator>'
            elif isinstance(arg, (tuple, list)):
                ret_s = ','.join([self.show(z) for z in arg])
                if len(ret_s) > 40:
                    g.printObj(arg, indent=len(indent))
                    ret = ''
                else:
                    ret = f"[{ret_s}]"
            elif arg:
                ret = self.show(arg)
                if len(ret) > 100:
                    ret = f"\n    {ret}"
            else:
                ret = '' if arg is None else repr(arg)
            print(f"{path}:{indent}-{self.full_name} -> {ret}")
        except Exception:
            exctype, value = sys.exc_info()[:2]
            try:  # Be extra careful.
                arg_s = f"arg: {arg!r}"
            except Exception:
                arg_s = ''  # arg.__class__.__name__
            print(
                f"{path}:{indent}-{self.full_name} -> "
                f"{exctype.__name__}, {value} {arg_s}"
            )
    #@+node:ekr.20121128111829.12185: *4* sherlock.fn_is_enabled
    def fn_is_enabled(self, func: Any, patterns: list[str]) -> bool:
        """Return True if tracing for the given function is enabled."""
        if func in self.ignored_functions:
            return False

        def ignore_function() -> None:
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
    #@+node:ekr.20130112093655.10195: *4* sherlock.get_full_name
    def get_full_name(self, locals_: Any, name: str) -> str:
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
    ignored_files: list[str] = []  # List of files.
    ignored_functions: list[str] = []  # List of files.

    def is_enabled(
        self,
        file_name: str,
        function_name: str,
        patterns: list[str] = None,
    ) -> bool:
        """Return True if tracing for function_name in the given file is enabled."""
        #
        # New in Leo 6.3. Never trace through some files.
        if not os:
            return False  # Shutting down.
        base_name = os.path.basename(file_name)
        if base_name in self.ignored_files:
            return False

        def ignore_file() -> None:
            if base_name not in self.ignored_files:
                self.ignored_files.append(base_name)

        def ignore_function() -> None:
            if function_name not in self.ignored_functions:
                self.ignored_functions.append(function_name)

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
        if patterns is None:
            patterns = self.patterns
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
    #@+node:ekr.20121128111829.12182: *4* sherlock.print_stats
    def print_stats(self, patterns: list[str] = None) -> None:
        """Print all accumulated statisitics."""
        print('\nSherlock statistics...')
        if not patterns:
            patterns = ['+.*', '+:.*',]
        for fn in sorted(self.stats.keys()):
            d = self.stats.get(fn)
            if self.fn_is_enabled(fn, patterns):
                result = sorted(d.keys())  # type:ignore
            else:
                result = [key for key in sorted(d.keys())  # type:ignore
                    if self.is_enabled(fn, key, patterns)]
            if result:
                print('')
                fn = fn.replace('\\', '/')
                parts = fn.split('/')
                print('/'.join(parts[-2:]))
                for key in result:
                    print(f"{d.get(key):4} {key}")
    #@+node:ekr.20121128031949.12614: *4* sherlock.run
    # Modified from pdb.Pdb.set_trace.

    def run(self, frame: Any = None) -> None:
        """Trace from the given frame or the caller's frame."""
        print("SherlockTracer.run:patterns:\n%s" % '\n'.join(self.patterns))
        if frame is None:
            frame = sys._getframe().f_back
        # Compute self.n, the number of frames to ignore.
        self.n = 0
        while frame:
            frame = frame.f_back
            self.n += 1
        # Pass self to sys.settrace to give easy access to all methods.
        sys.settrace(self)
    #@+node:ekr.20140322090829.16834: *4* sherlock.push & pop
    def push(self, patterns: list[str]) -> None:
        """Push the old patterns and set the new."""
        self.pattern_stack.append(self.patterns)  # type:ignore
        self.set_patterns(patterns)
        print(f"SherlockTracer.push: {self.patterns}")

    def pop(self) -> None:
        """Restore the pushed patterns."""
        if self.pattern_stack:
            self.patterns = self.pattern_stack.pop()  # type:ignore
            print(f"SherlockTracer.pop: {self.patterns}")
        else:
            print('SherlockTracer.pop: pattern stack underflow')
    #@+node:ekr.20140326100337.16845: *4* sherlock.set_patterns
    def set_patterns(self, patterns: list[str]) -> None:
        """Set the patterns in effect."""
        self.patterns = [z for z in patterns if self.check_pattern(z)]
    #@+node:ekr.20140322090829.16831: *4* sherlock.show
    def show(self, item: Any) -> str:
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
        s = repr(item)
        # A Hack for mypy:
        if s.startswith("<object object"):
            s = "_dummy"
        return s
    #@+node:ekr.20121128093229.12616: *4* sherlock.stop
    def stop(self) -> None:
        """Stop all tracing."""
        sys.settrace(None)
    #@-others
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

    def __init__(self) -> None:
        super().__init__(self.title, self.message)
        self.val = ''

    #@+others
    #@+node:ekr.20191013145710.1: *4* leo_id_dialog.onKey
    def onKey(self, event: Any) -> None:
        """Handle Key events in askOk dialogs."""
        if event.char in '\n\r':
            self.okButton()
    #@+node:ekr.20191013145757.1: *4* leo_id_dialog.createTopFrame
    def createTopFrame(self) -> None:
        """Create the Tk.Toplevel widget for a leoTkinterDialog."""
        self.root = Tk.Tk()  # type:ignore
        self.top = Tk.Toplevel(self.root)  # type:ignore
        self.top.title(self.title)
        self.root.withdraw()
        self.frame = Tk.Frame(self.top)  # type:ignore
        self.frame.pack(side="top", expand=1, fill="both")
        label = Tk.Label(self.frame, text=self.message, bg='white')
        label.pack(pady=10)
        self.entry = Tk.Entry(self.frame)
        self.entry.pack()
        self.entry.focus_set()
    #@+node:ekr.20191013150158.1: *4* leo_id_dialog.okButton
    def okButton(self) -> None:
        """Do default click action in ok button."""
        self.val = self.entry.get()  # Return is not possible.
        self.top.destroy()
        self.top = None
    #@-others
#@+node:ekr.20080531075119.1: *3* class g.Tracer
class Tracer:
    """A "debugger" that computes a call graph.

    To trace a function and its callers, put the following at the function's start:

    g.startTracer()
    """
    #@+others
    #@+node:ekr.20080531075119.2: *4*  __init__ (Tracer)
    def __init__(self, limit: int = 0, trace: bool = False, verbose: bool = False) -> None:
        # Keys are function names.
        # Values are the number of times the function was called by the caller.
        self.callDict: dict[str, Any] = {}
        # Keys are function names.
        # Values are the total number of times the function was called.
        self.calledDict: dict[str, int] = {}
        self.count = 0
        self.inited = False
        self.limit = limit  # 0: no limit, otherwise, limit trace to n entries deep.
        self.stack: list[str] = []
        self.trace = trace
        self.verbose = verbose  # True: print returns as well as calls.
    #@+node:ekr.20080531075119.3: *4* computeName
    def computeName(self, frame: Any) -> str:
        if not frame:
            return ''
        code = frame.f_code
        result = []
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
            if self_obj:
                result.append(self_obj.__class__.__name__)
        except Exception:
            pass
        result.append(code.co_name)
        return '.'.join(result)
    #@+node:ekr.20080531075119.4: *4* report
    def report(self) -> None:
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
            for key2 in sorted(d):  # type:ignore
                g.pr(f"{d.get(key2):8d}", key2)  # type:ignore
    #@+node:ekr.20080531075119.5: *4* stop
    def stop(self) -> None:
        sys.settrace(None)
        self.report()
    #@+node:ekr.20080531075119.6: *4* tracer
    def tracer(self, frame: Any, event: Any, arg: Any) -> Optional[Callable]:
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
    def updateStats(self, name: str) -> None:
        if not self.stack:
            return
        caller = self.stack[-1]
        # d is a dict representing the called functions.
        # Keys are called functions, values are counts.
        d: dict[str, int] = self.callDict.get(caller, {})
        d[name] = 1 + d.get(name, 0)
        self.callDict[caller] = d
        # Update the total counts.
        self.calledDict[name] = 1 + self.calledDict.get(name, 0)
    #@-others

def startTracer(limit: int = 0, trace: bool = False, verbose: bool = False) -> Callable:
    t = g.Tracer(limit=limit, trace=trace, verbose=verbose)
    sys.settrace(t.tracer)
    return t
#@+node:ekr.20031219074948.1: *3* class g.Tracing/NullObject & helpers
#@@nobeautify

tracing_tags: dict[int, str] = {}  # Keys are id's, values are tags.
tracing_vars: dict[int, list] = {}  # Keys are id's, values are names of ivars.
# Keys are signatures: '%s.%s:%s' % (tag, attr, callers). Values not important.
tracing_signatures: dict[str, Any] = {}

class NullObject:
    """An object that does nothing, and does it very well."""
    def __init__(self, ivars: list[str]=None, *args: Any, **kwargs: Any) -> None:
        if isinstance(ivars, str):
            ivars = [ivars]
        tracing_vars [id(self)] = ivars or []
    def __call__(self, *args: Any, **keys: Any) -> "NullObject":
        return self
    def __repr__(self) -> str:
        return "NullObject"
    def __str__(self) -> str:
        return "NullObject"
    # Attribute access...
    def __delattr__(self, attr: str) -> None:
        return None
    def __getattr__(self, attr: str) -> Any:
        if attr in tracing_vars.get(id(self), []):
            return getattr(self, attr, None)
        return self # Required.
    def __setattr__(self, attr: str, val: Any) -> None:
        if attr in tracing_vars.get(id(self), []):
            object.__setattr__(self, attr, val)
    # Container methods..
    def __bool__(self) -> bool:
        return False
    def __contains__(self, item: Any) -> bool:
        return False
    def __getitem__(self, key: str) -> None:
        raise KeyError
    def __setitem__(self, key: str, val: Any) -> None:
        pass
    def __iter__(self) -> "NullObject":
        return self
    def __len__(self) -> int:
        return 0
    # Iteration methods:
    def __next__(self) -> None:
        raise StopIteration


class TracingNullObject:
    """Tracing NullObject."""
    def __init__(self, tag: str, ivars: list[Any]=None, *args: Any, **kwargs: Any) -> None:
        tracing_tags [id(self)] = tag
        if isinstance(ivars, str):
            ivars = [ivars]
        tracing_vars [id(self)] = ivars or []
    def __call__(self, *args: Any, **kwargs: Any) -> "TracingNullObject":
        return self
    def __repr__(self) -> str:
        return f'TracingNullObject: {tracing_tags.get(id(self), "<NO TAG>")}'
    def __str__(self) -> str:
        return f'TracingNullObject: {tracing_tags.get(id(self), "<NO TAG>")}'
    #
    # Attribute access...
    def __delattr__(self, attr: str) -> None:
        return None
    def __getattr__(self, attr: str) -> "TracingNullObject":
        null_object_print_attr(id(self), attr)
        if attr in tracing_vars.get(id(self), []):
            return getattr(self, attr, None)
        return self # Required.
    def __setattr__(self, attr: str, val: Any) -> None:
        g.null_object_print(id(self), '__setattr__', attr, val)
        if attr in tracing_vars.get(id(self), []):
            object.__setattr__(self, attr, val)
    #
    # All other methods...
    def __bool__(self) -> bool:
        if 0: # To do: print only once.
            suppress = ('getShortcut','on_idle', 'setItemText')
            callers = g.callers(2)
            if not callers.endswith(suppress):
                g.null_object_print(id(self), '__bool__')
        return False
    def __contains__(self, item: Any) -> bool:
        g.null_object_print(id(self), '__contains__')
        return False
    def __getitem__(self, key: str) -> None:
        g.null_object_print(id(self), '__getitem__')
        # pylint doesn't like trailing return None.
    def __iter__(self) -> "TracingNullObject":
        g.null_object_print(id(self), '__iter__')
        return self
    def __len__(self) -> int:
        # g.null_object_print(id(self), '__len__')
        return 0
    def __next__(self) -> None:
        g.null_object_print(id(self), '__next__')
        raise StopIteration
    def __setitem__(self, key: str, val: Any) -> None:
        g.null_object_print(id(self), '__setitem__')
        # pylint doesn't like trailing return None.
#@+node:ekr.20190330062625.1: *4* g.null_object_print_attr
def null_object_print_attr(id_: int, attr: str) -> None:
    suppress = True
    suppress_callers: list[str] = []
    suppress_attrs: list[str] = []
    if suppress:
        #@+<< define suppression lists >>
        #@+node:ekr.20190330072026.1: *5* << define suppression lists >>
        suppress_callers = [
            'drawNode', 'drawTopTree', 'drawTree',
            'contractItem', 'getCurrentItem',
            'declutter_node',
            'finishCreate',
            'initAfterLoad',
            'show_tips',
            'writeWaitingLog',
            # 'set_focus', 'show_tips',
        ]
        suppress_attrs = [
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
        ]
        #@-<< define suppression lists >>
    tag = tracing_tags.get(id_, "<NO TAG>")
    callers = g.callers(3).split(',')
    callers = ','.join(callers[:-1])
    in_callers = any(z in callers for z in suppress_callers)
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
def null_object_print(id_: int, kind: Any, *args: Any) -> None:
    tag = tracing_tags.get(id_, "<NO TAG>")
    callers = g.callers(3).split(',')
    callers = ','.join(callers[:-1])
    s = f"{kind}.{tag}"
    signature = f"{s}:{callers}"
    if 1:
        # Always print:
        if args:
            args_s = ', '.join([repr(z) for z in args])
            g.pr(f"{s:40} {callers}\n\t\t\targs: {args_s}")
        else:
            g.pr(f"{s:40} {callers}")
    elif signature not in tracing_signatures:
        # Print each signature once.
        tracing_signatures[signature] = True
        g.pr(f"{s:40} {callers}")
#@+node:ville.20090827174345.9963: *3* class g.UiTypeException & g.assertui
class UiTypeException(Exception):
    pass

def assertUi(uitype: Any) -> None:
    if not g.app.gui.guiName() == uitype:
        raise UiTypeException
#@+node:ekr.20200219071828.1: *3* class TestLeoGlobals (leoGlobals.py)
class TestLeoGlobals(unittest.TestCase):
    """Tests for leoGlobals.py."""
    #@+others
    #@+node:ekr.20200219071958.1: *4* TestLeoGlobals.test_comment_delims_from_extension
    def test_comment_delims_from_extension(self) -> None:

        # pylint: disable=import-self
        from leo.core import leoGlobals as leo_g
        from leo.core import leoApp
        leo_g.app = leoApp.LeoApp()
        assert leo_g.comment_delims_from_extension(".py") == ('#', '', '')
        assert leo_g.comment_delims_from_extension(".c") == ('//', '/*', '*/')
        assert leo_g.comment_delims_from_extension(".html") == ('', '<!--', '-->')
    #@+node:ekr.20200219072957.1: *4* TestLeoGlobals.test_is_sentinel
    def test_is_sentinel(self) -> None:

        # pylint: disable=import-self
        from leo.core import leoGlobals as leo_g
        # Python. Test regular and blackened sentinels.
        py_delims = leo_g.comment_delims_from_extension('.py')
        assert leo_g.is_sentinel("#@+node", py_delims)
        assert leo_g.is_sentinel("# @+node", py_delims)
        assert not leo_g.is_sentinel("#comment", py_delims)
        assert not leo_g.is_sentinel("# comment", py_delims)
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
def isTextWidget(w: Any) -> bool:
    return g.app.gui.isTextWidget(w)

def isTextWrapper(w: Any) -> bool:
    return g.app.gui.isTextWrapper(w)
#@+node:ekr.20140711071454.17649: ** g.Debugging, GC, Stats & Timing
#@+node:ekr.20031218072017.3104: *3* g.Debugging
#@+node:ekr.20180415144534.1: *4* g.assert_is
def assert_is(obj: Any, list_or_class: Any, warn: bool = True) -> bool:

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
def _assert(condition: Any, show_callers: bool = True) -> bool:
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
#@+node:ekr.20051023083258: *4* g.callers, caller,  _callerName, callers_list
#@+node:ekr.20230128025911.1: *5* g.callers
def callers(n: int = 4) -> str:
    """
    Return a string containing a comma-separated list of the calling
    function's callers.
    """
    # Be careful to call g._callerName with smaller values of i first:
    # sys._getframe throws ValueError if there are less than i entries.
    i, result = 3, []
    while 1:
        s = _callerName(n=i)
        if s:
            result.append(s)
        if not s or len(result) >= n:
            break
        i += 1
    return ','.join(reversed(result))
#@+node:ekr.20230128030346.1: *5* g.callers_list
def callers_list(n: int = 4) -> list[str]:
    """
    Return a string containing a comma-separated list of the calling
    function's callers.
    """
    # Be careful to call g._callerName with smaller values of i first:
    # sys._getframe throws ValueError if there are less than i entries.
    i, result = 3, []
    while 1:
        s = _callerName(n=i)
        if s:
            result.append(s)
        if not s or len(result) >= n:
            break
        i += 1
    return list(reversed(result))
#@+node:ekr.20031218072017.3107: *5* g._callerName
def _callerName(n: int) -> str:
    try:
        # get the function name from the call stack.
        f1 = sys._getframe(n)  # The stack frame, n levels up.
        code1 = f1.f_code  # The code object
        locals_ = f1.f_locals  # The local namespace.
        name = code1.co_name
        # sfn = shortFilename(code1.co_filename)  # The file name.
        # line = code1.co_firstlineno
        obj = locals_.get('self')
        if obj and name == '__init__':
            return f"{obj.__class__.__name__}.{name}"
        return name
    except ValueError:
        # The stack is not deep enough OR
        # sys._getframe does not exist on this platform.
        return ''
    except Exception:
        es_exception()
        return ''  # "<no caller name>"
#@+node:ekr.20180328170441.1: *5* g.caller
def caller(i: int = 1) -> str:
    """Return the caller name i levels up the stack."""
    return g.callers(i + 1).split(',')[0]
#@+node:ekr.20031218072017.3109: *4* g.dump
def dump(s: str) -> str:
    out = ""
    for i in s:
        out += str(ord(i)) + ","
    return out

def oldDump(s: str) -> str:
    out = ""
    for i in s:
        if i == '\n':
            out += "["
            out += "n"
            out += "]"
        if i == '\t':
            out += "["
            out += "t"
            out += "]"
        elif i == ' ':
            out += "["
            out += " "
            out += "]"
        else:
            out += i
    return out
#@+node:ekr.20210904114446.1: *4* g.dump_tree & g.tree_to_string
def dump_tree(c: Cmdr, dump_body: bool = False, msg: str = None) -> None:
    if msg:
        print(msg.rstrip())
    else:
        print('')
    for p in c.all_positions():
        print(f"clone? {int(p.isCloned())} {' '*p.level()} {p.h}")
        if dump_body:
            for z in g.splitLines(p.b):
                print(z.rstrip())

def tree_to_string(c: Cmdr, dump_body: bool = False, msg: str = None) -> str:
    result = ['\n']
    if msg:
        result.append(msg)
    for p in c.all_positions():
        result.append(f"clone? {int(p.isCloned())} {' '*p.level()} {p.h}")
        if dump_body:
            for z in g.splitLines(p.b):
                result.append(z.rstrip())
    return '\n'.join(result)
#@+node:ekr.20150227102835.8: *4* g.dump_encoded_string
def dump_encoded_string(encoding: str, s: str) -> None:
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
def module_date(mod: Any, format: str = None) -> str:
    theFile = g.os_path_join(app.loadDir, mod.__file__)
    root, ext = g.os_path_splitext(theFile)
    return g.file_date(root + ".py", format=format)

def plugin_date(plugin_mod: Any, format: str = None) -> str:
    theFile = g.os_path_join(app.loadDir, "..", "plugins", plugin_mod.__file__)
    root, ext = g.os_path_splitext(theFile)
    return g.file_date(root + ".py", format=str)

def file_date(theFile: Any, format: str = None) -> str:
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

def get_line(s: str, i: int) -> str:
    nl = ""
    if g.is_nl(s, i):
        i = g.skip_nl(s, i)
        nl = "[nl]"
    j = g.find_line_start(s, i)
    k = g.skip_to_end_of_line(s, i)
    return nl + s[j:k]

# Important: getLine is a completely different function.
# getLine = get_line

def get_line_after(s: str, i: int) -> str:
    nl = ""
    if g.is_nl(s, i):
        i = g.skip_nl(s, i)
        nl = "[nl]"
    k = g.skip_to_end_of_line(s, i)
    return nl + s[i:k]

getLineAfter = get_line_after
#@+node:ekr.20080729142651.1: *4* g.getIvarsDict and checkUnchangedIvars
def getIvarsDict(obj: Any) -> dict[str, Any]:
    """Return a dictionary of ivars:values for non-methods of obj."""
    d: dict[str, Any] = dict(
        [[key, getattr(obj, key)] for key in dir(obj)
            if not isinstance(getattr(obj, key), types.MethodType)])
    return d

def checkUnchangedIvars(
    obj: Any,
    d: dict[str, Any],
    exceptions: Sequence[str] = None,
) -> bool:
    if not exceptions:
        exceptions = []
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
def pause(s: str) -> None:
    g.pr(s)
    i = 0
    while i < 1000 * 1000:
        i += 1
#@+node:ekr.20041105091148: *4* g.pdb
def pdb(message: str = '') -> None:
    """Fall into pdb."""
    if app and not app.useIpython:
        try:
            from leo.core.leoQt import QtCore
            QtCore.pyqtRemoveInputHook()
        except Exception:
            pass
    if message:
        print(message)
    # pylint: disable=forgotten-debug-statement
    breakpoint()  # New in Python 3.7.
#@+node:ekr.20050819064157: *4* g.objToString & aliases
def objToString(obj: Any, *, indent: int = 0, tag: str = None, width: int = 120) -> str:
    """Pretty print any Python object to a string."""
    if isinstance(obj, dict):
        result_list = ['{\n']
        pad = max([len(key) for key in obj])
        for key in sorted(obj):
            pad_s = ' ' * max(0, pad - len(key))
            result_list.append(f"  {pad_s}{key}: {obj.get(key)}\n")
        result_list.append('}')
        result = ''.join(result_list)
    elif isinstance(obj, (list, tuple)):
        # Return the enumerated lines of the list.
        result_list = ['[\n' if isinstance(obj, list) else '(\n']
        for i, z in enumerate(obj):
            result_list.append(f"  {i:4}: {z!r}\n")
        result_list.append(']\n' if isinstance(obj, list) else ')\n')
        result = ''.join(result_list)
    elif not isinstance(obj, str):
        result = pprint.pformat(obj, indent=indent, width=width)
        # Put opening/closing delims on separate lines.
        if result.count('\n') > 0 and result[0] in '([{' and result[-1] in ')]}':
            result = f"{result[0]}\n{result[1:-2]}\n{result[-1]}"
    elif '\n' not in obj:
        result = repr(obj)
    else:
        # Return the enumerated lines of the string.
        lines = ''.join([
            f"  {i:4}: {z!r}\n" for i, z in enumerate(g.splitLines(obj))
        ])
        result = f"[\n{lines}]\n"
    return f"{tag.strip()}: {result}" if tag and tag.strip() else result

toString = objToString
dictToString = objToString
listToString = objToString
tupleToString = objToString
#@+node:ekr.20120912153732.10597: *4* g.wait
def sleep(n: float) -> None:
    """Wait about n milliseconds."""
    from time import sleep  # type:ignore
    sleep(n)  # type:ignore
#@+node:ekr.20171023140544.1: *4* g.printObj & aliases
def printObj(obj: Any, tag: str = None, indent: int = 0) -> None:
    """Pretty print any Python object using g.pr."""
    g.pr(objToString(obj, indent=indent, tag=tag))

printDict = printObj
printList = printObj
printTuple = printObj
#@+node:ekr.20031218072017.1588: *3* g.Garbage Collection
#@+node:ekr.20031218072017.1589: *4* g.clearAllIvars
def clearAllIvars(o: Any) -> None:
    """Clear all ivars of o, a member of some class."""
    if o:
        o.__dict__.clear()
#@+node:ekr.20060127162818: *4* g.enable_gc_debug
def enable_gc_debug() -> None:

    gc.set_debug(
        gc.DEBUG_STATS |  # prints statistics.
        gc.DEBUG_LEAK |  # Same as all below.
        gc.DEBUG_COLLECTABLE |
        gc.DEBUG_UNCOLLECTABLE |
        # gc.DEBUG_INSTANCES |
        # gc.DEBUG_OBJECTS |
        gc.DEBUG_SAVEALL)
#@+node:ekr.20031218072017.1592: *4* g.printGc
# Formerly called from unit tests.

def printGc() -> None:
    """Called from trace_gc_plugin."""
    g.printGcSummary()
    g.printGcObjects()
    g.printGcRefs()
#@+node:ekr.20060127164729.1: *4* g.printGcObjects
lastObjectCount = 0

def printGcObjects() -> int:
    """Print a summary of GC statistics."""
    global lastObjectCount
    n = len(gc.garbage)
    n2 = len(gc.get_objects())
    delta = n2 - lastObjectCount
    print('-' * 30)
    print(f"garbage: {n}")
    print(f"{delta:6d} = {n2:7d} totals")
    # print number of each type of object.
    d: dict[str, int] = {}
    count = 0
    for obj in gc.get_objects():
        key = str(type(obj))
        n = d.get(key, 0)
        d[key] = n + 1
        count += 1
    print(f"{count:7} objects...")
    # Invert the dict.
    d2: dict[Any, Any] = {v: k for k, v in d.items()}
    for key in reversed(sorted(d2.keys())):
        val = d2.get(key)
        print(f"{key:7} {val}")
    lastObjectCount = count
    return delta
#@+node:ekr.20031218072017.1593: *4* g.printGcRefs
def printGcRefs() -> None:

    refs = gc.get_referrers(app.windowList[0])
    print(f"{len(refs):d} referrers")
#@+node:ekr.20060205043324.1: *4* g.printGcSummary
def printGcSummary() -> None:

    g.enable_gc_debug()
    try:
        n = len(gc.garbage)
        n2 = len(gc.get_objects())
        s = f"printGCSummary: garbage: {n}, objects: {n2}"
        print(s)
    except Exception:
        traceback.print_exc()
#@+node:ekr.20180528151850.1: *3* g.printTimes
def printTimes(times: list) -> None:
    """
    Print the differences in the times array.

    times: an array of times (calls to time.process_time()).
    """
    for n, _junk in enumerate(times[:-1]):
        t = times[n + 1] - times[n]
        if t > 0.1:
            g.trace(f"*** {n} {t:5.4f} sec.")
#@+node:ekr.20031218072017.3133: *3* g.Statistics
#@+node:ekr.20031218072017.3134: *4* g.clearStats
def clearStats() -> None:

    g.app.statsDict = {}
#@+node:ekr.20031218072017.3135: *4* g.printStats
@command('show-stats')
def printStats(event: Event = None, name: str = None) -> None:
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
        if not isinstance(name, str):
            name = repr(name)
    else:
        # Get caller name 2 levels back.
        name = g._callerName(n=2)
    # Print the stats, organized by number of calls.
    d = g.app.statsDict
    print('g.app.statsDict...')
    for key in reversed(sorted(d)):
        print(f"{key:7} {d.get(key)}")
#@+node:ekr.20031218072017.3136: *4* g.stat
def stat(name: str = None) -> None:
    """Increments the statistic for name in g.app.statsDict
    The caller's name is used by default.
    """
    d = g.app.statsDict
    if name:
        if not isinstance(name, str):
            name = repr(name)
    else:
        name = g._callerName(n=2)  # Get caller name 2 levels back.
    d[name] = 1 + d.get(name, 0)
#@+node:ekr.20031218072017.3137: *3* g.Timing
def getTime() -> float:
    return time.time()

def esDiffTime(message: str, start: float) -> float:
    delta = time.time() - start
    g.es('', f"{message} {delta:5.2f} sec.")
    return time.time()

def printDiffTime(message: str, start: float) -> float:
    delta = time.time() - start
    g.pr(f"{message} {delta:5.2f} sec.")
    return time.time()

def timeSince(start: float) -> str:
    return f"{time.time()-start:5.2f} sec."
#@+node:ekr.20031218072017.1380: ** g.Directives
# Weird pylint bug, activated by TestLeoGlobals class.
# Disabling this will be safe, because pyflakes will still warn about true redefinitions
# pylint: disable=function-redefined
#@+node:EKR.20040504150046.4: *3* g.comment_delims_from_extension
def comment_delims_from_extension(filename: str) -> tuple[str, str, str]:
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
def findAllValidLanguageDirectives(s: str) -> list:
    """
    Return list of all languages for which there is a valid @language
    directive in s.
    """
    if not s.strip():
        return []
    languages = set()
    for m in g.g_language_pat.finditer(s):
        language = m.group(1)
        if g.isValidLanguage(language):
            languages.add(language)
    return list(sorted(languages))
#@+node:ekr.20090214075058.8: *3* g.findAtTabWidthDirectives (must be fast)
def findTabWidthDirectives(c: Cmdr, p: Position) -> Optional[str]:
    """Return the tab width in effect at position p."""
    if c is None:
        return None  # c may be None for testing.
    w = None
    # 2009/10/02: no need for copy arg to iter
    for p in p.self_and_parents(copy=False):
        if w:
            break
        for s in p.h, p.b:
            if w:
                break
            anIter = g_tabwidth_pat.finditer(s)
            for m in anIter:
                word = m.group(0)
                i = m.start(0)
                j = g.skip_ws(s, i + len(word))
                junk, w = g.skip_long(s, j)
                if w == 0:
                    w = None
    return w
#@+node:ekr.20170127142001.5: *3* g.findFirstAtLanguageDirective
def findFirstValidAtLanguageDirective(s: str) -> Optional[str]:
    """
    Return the first language for which there is a valid @language
    directive in s.
    """
    if not s.strip():
        return None
    for m in g.g_language_pat.finditer(s):
        language = m.group(1)
        if g.isValidLanguage(language):
            return language
    return None
#@+node:ekr.20090214075058.6: *3* g.findLanguageDirectives (must be fast)
def findLanguageDirectives(c: Cmdr, p: Position) -> Optional[str]:
    """Return the language in effect at position p."""
    if c is None or p is None:
        return None  # c may be None for testing.

    v0 = p.v

    def find_language(p_or_v: Any) -> Optional[str]:
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
    seen = []  # vnodes that have already been searched.
    parents = v0.parents[:]  # vnodes whose ancestors are to be searched.
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

def findReference(name: str, root: Position) -> Optional[Position]:
    """Return the position containing the section definition for name."""
    for p in root.subtree(copy=False):
        assert p != root
        if p.matchHeadline(name) and not p.isAtIgnoreNode():
            return p.copy()
    return None
#@+node:ekr.20090214075058.9: *3* g.get_directives_dict (must be fast)
def get_directives_dict(p: Position) -> dict[str, str]:
    """
    Scan p for Leo directives found in globalDirectiveList.

    Returns a dict containing the stripped remainder of the line
    following the first occurrence of each recognized directive.
    """
    d = {}
    # The headline has higher precedence because it is more visible.
    for s in (p.h, p.b):
        anIter = g.directives_pat.finditer(s)
        for m in anIter:
            word = m.group(1).strip()
            i = m.start(1)
            if word in d:
                continue
            j = i + len(word)
            if j < len(s) and s[j] not in ' \t\n':
                # Not a valid directive: just ignore it.
                continue
            k = g.skip_line(s, j)
            val = s[j:k].strip()
            d[word] = val
    return d
#@+node:ekr.20080827175609.1: *3* g.get_directives_dict_list (must be fast)
def get_directives_dict_list(p: Position) -> list[dict]:
    """Scans p and all its ancestors for directives.

    Returns a list of dicts containing pointers to
    the start of each directive"""
    result = []
    p1 = p.copy()
    for p in p1.self_and_parents(copy=False):
        # No copy necessary: g.get_directives_dict does not change p.
        result.append(g.get_directives_dict(p))
    return result
#@+node:ekr.20111010082822.15545: *3* g.getLanguageFromAncestorAtFileNode
def getLanguageFromAncestorAtFileNode(p: Position) -> Optional[str]:
    """
    Return the language in effect at node p.

    1. Use an unambiguous @language directive in p itself.
    2. Search p's "extended parents" for an @<file> node.
    3. Search p's "extended parents" for an unambiguous @language directive.
    """
    v0 = p.v
    seen: set[VNode]

    # The same generator as in v.setAllAncestorAtFileNodesDirty.
    # Original idea by Виталије Милошевић (Vitalije Milosevic).
    # Modified by EKR.

    def v_and_parents(v: VNode) -> Generator:
        if v in seen:
            return
        seen.add(v)
        yield v
        for parent_v in v.parents:
            if parent_v not in seen:
                yield from v_and_parents(parent_v)

    def find_language(v: VNode, phase: int) -> Optional[str]:
        """
        A helper for all searches.
        Phase one searches only @<file> nodes.
        """
        if phase == 1 and not v.isAnyAtFileNode():
            return None
        # #1693: Scan v.b for an *unambiguous* @language directive.
        languages = g.findAllValidLanguageDirectives(v.b)
        if len(languages) == 1:  # An unambiguous language
            return languages[0]
        if v.isAnyAtFileNode():
            # Use the file's extension.
            name = v.anyAtFileNodeName()
            junk, ext = g.os_path_splitext(name)
            ext = ext[1:]  # strip the leading period.
            language = g.app.extension_dict.get(ext)
            if g.isValidLanguage(language):
                return language
        return None

    # First, see if p contains any @language directive.
    language = g.findFirstValidAtLanguageDirective(p.b)
    if language:
        return language
    #
    # Phase 1: search only @<file> nodes: #2308.
    # Phase 2: search all nodes.
    for phase in (1, 2):
        # Search direct parents.
        for p2 in p.self_and_parents(copy=False):
            language = find_language(p2.v, phase)
            if language:
                return language
        # Search all extended parents.
        seen = set([v0.context.hiddenRootNode])
        for v in v_and_parents(v0):
            language = find_language(v, phase)
            if language:
                return language
    return None
#@+node:ekr.20150325075144.1: *3* g.getLanguageFromPosition
def getLanguageAtPosition(c: Cmdr, p: Position) -> str:
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
def getOutputNewline(c: Cmdr = None, name: str = None) -> str:
    """Convert the name of a line ending to the line ending itself.

    Priority:
    - Use name if name given
    - Use c.config.output_newline if c given,
    - Otherwise use g.app.config.output_newline.
    """
    if name:
        s = name
    elif c:
        s = c.config.getString('output-newline')
    else:
        s = 'nl'  # Legacy value. Perhaps dubious.
    if not s:
        s = ''
    s = s.lower()
    if s in ("nl", "lf"):
        s = '\n'
    elif s == "cr":
        s = '\r'
    elif s == "platform":
        s = os.linesep  # 12/2/03: emakital
    elif s == "crlf":
        s = "\r\n"
    else:
        s = '\n'  # Default for erroneous values.
    assert isinstance(s, str), repr(s)
    return s
#@+node:ekr.20200521075143.1: *3* g.inAtNosearch
def inAtNosearch(p: Position) -> bool:
    """Return True if p or p's ancestors contain an @nosearch directive."""
    if not p:
        return False  # #2288.
    for p in p.self_and_parents():
        if p.is_at_ignore() or re.search(r'(^@|\n@)nosearch\b', p.b):
            return True
    return False
#@+node:ekr.20131230090121.16528: *3* g.isDirective
def isDirective(s: str) -> bool:
    """Return True if s starts with a directive."""
    m = g_is_directive_pattern.match(s)
    if m:
        s2 = s[m.end(1) :]
        if s2 and s2[0] in ".(":
            return False
        return bool(m.group(1) in g.globalDirectiveList)
    return False
#@+node:ekr.20200810074755.1: *3* g.isValidLanguage
def isValidLanguage(language: str) -> bool:
    """True if the given language may be used as an external file."""
    return bool(language and language in g.app.language_delims_dict)
#@+node:ekr.20080827175609.52: *3* g.scanAtCommentAndLanguageDirectives
def scanAtCommentAndAtLanguageDirectives(aList: list) -> Optional[dict[str, str]]:
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
def scanAtEncodingDirectives(aList: list) -> Optional[str]:
    """Scan aList for @encoding directives."""
    for d in aList:
        encoding = d.get('encoding')
        if encoding and g.isValidEncoding(encoding):
            return encoding
        if encoding and not g.unitTesting:
            g.error("invalid @encoding:", encoding)
    return None
#@+node:ekr.20080827175609.53: *3* g.scanAtHeaderDirectives
def scanAtHeaderDirectives(aList: list) -> None:
    """scan aList for @header and @noheader directives."""
    for d in aList:
        if d.get('header') and d.get('noheader'):
            g.error("conflicting @header and @noheader directives")
#@+node:ekr.20080827175609.33: *3* g.scanAtLineendingDirectives
def scanAtLineendingDirectives(aList: list) -> Optional[str]:
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
def scanAtPagewidthDirectives(aList: list, issue_error_flag: bool = False) -> Optional[int]:
    """Scan aList for @pagewidth directives. Return the page width or None"""
    for d in aList:
        s = d.get('pagewidth')
        if s is not None:
            i, val = g.skip_long(s, 0)
            if val is not None and val > 0:
                return val
            if issue_error_flag and not g.unitTesting:
                g.error("ignoring @pagewidth", s)
    return None
#@+node:ekr.20101022172109.6108: *3* g.scanAtPathDirectives
def scanAtPathDirectives(c: Cmdr, aList: list) -> str:
    path = c.scanAtPathDirectives(aList)
    return path

def scanAllAtPathDirectives(c: Cmdr, p: Position) -> str:
    aList = g.get_directives_dict_list(p)
    path = c.scanAtPathDirectives(aList)
    return path
#@+node:ekr.20080827175609.37: *3* g.scanAtTabwidthDirectives
def scanAtTabwidthDirectives(aList: list, issue_error_flag: bool = False) -> Optional[int]:
    """Scan aList for @tabwidth directives."""
    for d in aList:
        s = d.get('tabwidth')
        if s is not None:
            junk, val = g.skip_long(s, 0)
            if val not in (None, 0):
                return val
            if issue_error_flag and not g.unitTesting:
                g.error("ignoring @tabwidth", s)
    return None

def scanAllAtTabWidthDirectives(c: Cmdr, p: Position) -> Optional[int]:
    """Scan p and all ancestors looking for @tabwidth directives."""
    if c and p:
        aList = g.get_directives_dict_list(p)
        val = g.scanAtTabwidthDirectives(aList)
        ret = c.tab_width if val is None else val
    else:
        ret = None
    return ret
#@+node:ekr.20080831084419.4: *3* g.scanAtWrapDirectives
def scanAtWrapDirectives(aList: list, issue_error_flag: bool = False) -> Optional[bool]:
    """Scan aList for @wrap and @nowrap directives."""
    for d in aList:
        if d.get('wrap') is not None:
            return True
        if d.get('nowrap') is not None:
            return False
    return None

def scanAllAtWrapDirectives(c: Cmdr, p: Position) -> Optional[bool]:
    """Scan p and all ancestors looking for @wrap/@nowrap directives."""
    if c and p:
        default = bool(c and c.config.getBool("body-pane-wraps"))
        aList = g.get_directives_dict_list(p)
        val = g.scanAtWrapDirectives(aList)
        ret = default if val is None else val
    else:
        ret = None
    return ret
#@+node:ekr.20040715155607: *3* g.scanForAtIgnore
def scanForAtIgnore(c: Cmdr, p: Position) -> bool:
    """Scan position p and its ancestors looking for @ignore directives."""
    if g.unitTesting:
        return False  # For unit tests.
    for p in p.self_and_parents(copy=False):
        d = g.get_directives_dict(p)
        if 'ignore' in d:
            return True
    return False
#@+node:ekr.20040712084911.1: *3* g.scanForAtLanguage
def scanForAtLanguage(c: Cmdr, p: Position) -> str:
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
def scanForAtSettings(p: Position) -> bool:
    """Scan position p and its ancestors looking for @settings nodes."""
    for p in p.self_and_parents(copy=False):
        h = p.h
        h = g.app.config.canonicalizeSettingName(h)
        if h.startswith("@settings"):
            return True
    return False
#@+node:ekr.20031218072017.1382: *3* g.set_delims_from_language
def set_delims_from_language(language: str) -> tuple[str, str, str]:
    """Return a tuple (single,start,end) of comment delims."""
    val = g.app.language_delims_dict.get(language)
    if val:
        delim1, delim2, delim3 = g.set_delims_from_string(val)
        if delim2 and not delim3:
            return '', delim1, delim2
        # 0,1 or 3 params.
        return delim1, delim2, delim3
    return '', '', ''  # Indicate that no change should be made
#@+node:ekr.20031218072017.1383: *3* g.set_delims_from_string
def set_delims_from_string(s: str) -> tuple[str, str, str]:
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
    count = 0
    delims = ['', '', '']
    while count < 3 and i < len(s):
        i = j = g.skip_ws(s, i)
        while i < len(s) and not g.is_ws(s[i]) and not g.is_nl(s, i):
            i += 1
        if j == i:
            break
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
                    delims[i] = binascii.unhexlify(delims[i][3:])  # type:ignore
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
def set_language(s: str, i: int, issue_errors_flag: bool = False) -> tuple:
    """Scan the @language directive that appears at s[i:].

    The @language may have been stripped away.

    Returns (language, delim1, delim2, delim3)
    """
    tag = "@language"
    assert i is not None
    if g.match_word(s, i, tag):
        i += len(tag)
    # Get the argument.
    i = g.skip_ws(s, i)
    j = i
    i = g.skip_c_id(s, i)
    # Allow tcl/tk.
    arg = s[j:i].lower()
    if app.language_delims_dict.get(arg):
        language = arg
        delim1, delim2, delim3 = g.set_delims_from_language(language)
        return language, delim1, delim2, delim3
    if issue_errors_flag:
        g.es("ignoring:", g.get_line(s, i))
    return None, None, None, None
#@+node:ekr.20071109165315: *3* g.stripPathCruft
def stripPathCruft(path: str) -> str:
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
#@+node:ekr.20090214075058.10: *3* g.update_directives_pat
def update_directives_pat() -> None:
    """Init/update g.directives_pat"""
    global globalDirectiveList, directives_pat
    # Use a pattern that guarantees word matches.
    aList = [
        fr"\b{z}\b" for z in globalDirectiveList if z != 'others'
    ]
    pat = "^@(%s)" % "|".join(aList)
    directives_pat = re.compile(pat, re.MULTILINE)

# #1688: Initialize g.directives_pat
update_directives_pat()
#@+node:ekr.20031218072017.3116: ** g.Files & Directories
#@+node:ekr.20080606074139.2: *3* g.chdir
def chdir(path: str) -> None:
    if not g.os_path_isdir(path):
        path = g.os_path_dirname(path)
    if g.os_path_isdir(path) and g.os_path_exists(path):
        os.chdir(path)
#@+node:ekr.20120222084734.10287: *3* g.compute...Dir
# For compatibility with old code.

def computeGlobalConfigDir() -> str:
    return g.app.loadManager.computeGlobalConfigDir()

def computeHomeDir() -> str:
    return g.app.loadManager.computeHomeDir()

def computeLeoDir() -> str:
    return g.app.loadManager.computeLeoDir()

def computeLoadDir() -> str:
    return g.app.loadManager.computeLoadDir()

def computeMachineName() -> str:
    return g.app.loadManager.computeMachineName()

def computeStandardDirectories() -> str:
    return g.app.loadManager.computeStandardDirectories()
#@+node:ekr.20031218072017.3103: *3* g.computeWindowTitle
def computeWindowTitle(fileName: str) -> str:

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
def create_temp_file(textMode: bool = False) -> tuple[Any, str]:
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
#@+node:ekr.20210307060731.1: *3* g.createHiddenCommander
def createHiddenCommander(fn: str) -> Cmdr:
    """Read the file into a hidden commander (Similar to g.openWithFileName)."""
    from leo.core.leoCommands import Commands
    c = Commands(fn, gui=g.app.nullGui)
    theFile = g.app.loadManager.openAnyLeoFile(fn)
    if theFile:
        c.fileCommands.openLeoFile(theFile, fn, readAtFileNodesFlag=True, silent=True)
        return c
    return None
#@+node:vitalije.20170714085545.1: *3* g.defaultLeoFileExtension
def defaultLeoFileExtension(c: Cmdr = None) -> str:
    conf = c.config if c else g.app.config
    return conf.getString('default-leo-extension') or '.leo'
#@+node:ekr.20031218072017.3118: *3* g.ensure_extension
def ensure_extension(name: str, ext: str) -> str:

    theFile, old_ext = g.os_path_splitext(name)
    if not name:
        return name  # don't add to an empty name.
    if old_ext in ('.db', '.leo', '.leojs'):
        return name
    if old_ext and old_ext == ext:
        return name
    return name + ext
#@+node:ekr.20150403150655.1: *3* g.fullPath (deprecated)
def fullPath(c: Cmdr, p: Position, simulate: bool = False) -> str:
    """
    Return the full path (including fileName) in effect at p.

    Create neither the path nor the fileName.

    This function is deprecated. Use c.fullPath(p) instead.
    """
    return c.fullPath(p, simulate)
#@+node:ekr.20190327192721.1: *3* g.get_files_in_directory
def get_files_in_directory(directory: str, kinds: list = None, recursive: bool = True) -> list[str]:
    """
    Return a list of all files of the given file extensions in the directory.
    Default kinds: ['*.py'].
    """
    files: list[str] = []
    sep = os.path.sep
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
            for root, _dirnames, filenames in os.walk(directory):
                for kind in kinds:
                    for filename in fnmatch.filter(filenames, kind):
                        files.append(os.path.join(root, filename))
        else:
            for kind in kinds:
                files.extend(glob.glob(directory + sep + kind))
        return list(set(sorted(files)))
    except Exception:
        g.es_exception()
        return []
#@+node:ekr.20031218072017.1264: *3* g.getBaseDirectory
def getBaseDirectory(c: Cmdr) -> str:
    """
    This function is deprectated.

    Previously it convert '!' or '.' to proper directory references using
    @string relative-path-base-directory.
    """
    return ''
#@+node:ekr.20170223093758.1: *3* g.getEncodingAt
def getEncodingAt(p: Position, b: bytes = None) -> str:
    """
    Return the encoding in effect at p and/or for string s.

    Read logic:  s is not None.
    Write logic: s is None.
    """
    # A BOM overrides everything.
    if b:
        e, junk_s = g.stripBOM(b)
        if e:
            return e
    aList = g.get_directives_dict_list(p)
    e = g.scanAtEncodingDirectives(aList)
    if b and b.strip() and not e:
        e = 'utf-8'
    return e
#@+node:ville.20090701144325.14942: *3* g.guessExternalEditor
def guessExternalEditor(c: Cmdr = None) -> Optional[str]:
    """ Return a 'sensible' external editor """
    editor = (
        c and c.config.getString('external-editor') or
        os.environ.get("LEO_EDITOR") or
        os.environ.get("EDITOR") or
        g.app.db and g.app.db.get("LEO_EDITOR")
        )
    if editor:
        return editor
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
def init_dialog_folder(c: Cmdr, p: Position, use_at_path: bool = True) -> str:
    """Return the most convenient folder to open or save a file."""
    if c and p and use_at_path:
        path = c.fullPath(p)
        if path:
            dir_ = g.os_path_dirname(path)
            if dir_ and g.os_path_exists(dir_):
                return dir_
    table = (
        c and c.last_dir,
        g.os_path_abspath(os.curdir),
    )
    for dir_ in table:
        if dir_ and g.os_path_exists(dir_):
            return dir_
    return ''
#@+node:ekr.20100329071036.5744: *3* g.is_binary_file/external_file/string
def is_binary_file(f: Any) -> bool:
    return f and isinstance(f, io.BufferedIOBase)

def is_binary_external_file(fileName: str) -> bool:
    try:
        with open(fileName, 'rb') as f:
            s = f.read(1024)  # bytes, in Python 3.
        return g.is_binary_string(s)
    except IOError:
        return False
    except Exception:
        g.es_exception()
        return False

def is_binary_string(s: str) -> bool:
    # http://stackoverflow.com/questions/898669
    # aList is a list of all non-binary characters.
    aList = [7, 8, 9, 10, 12, 13, 27] + list(range(0x20, 0x100))
    return bool(s.translate(None, bytes(aList)))  # type:ignore
#@+node:EKR.20040504154039: *3* g.is_sentinel
def is_sentinel(line: str, delims: Sequence) -> bool:
    """
    Return True if line starts with a sentinel comment.

    Leo 6.7.2: Support blackened sentinels.
    """
    delim1, delim2, delim3 = delims
    # Defensive code. Make *sure* delim has no trailing space.
    if delim1:
        delim1 = delim1.rstrip()
    line = line.lstrip()
    if delim1:
        sentinel1 = delim1 + '@'
        sentinel2 = delim1 + ' @'
        return line.startswith((sentinel1, sentinel2))
    if delim2 and delim3:
        sentinel1 = delim2 + '@'
        sentinel2 = delim2 + ' @'
        if sentinel1 in line:
            i = line.find(sentinel1)
            j = line.find(delim3)
            return 0 == i < j
        if sentinel2 in line:
            i = line.find(sentinel2)
            j = line.find(delim3)
            return 0 == i < j
    g.error(f"is_sentinel: can not happen. delims: {repr(delims)}")
    return False
#@+node:ekr.20031218072017.3119: *3* g.makeAllNonExistentDirectories
def makeAllNonExistentDirectories(theDir: str) -> Optional[str]:
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
def makePathRelativeTo(fullPath: str, basePath: str) -> str:
    if fullPath.startswith(basePath):
        s = fullPath[len(basePath) :]
        if s.startswith(os.path.sep):
            s = s[len(os.path.sep) :]
        return s
    return fullPath
#@+node:ekr.20090520055433.5945: *3* g.openWithFileName
def openWithFileName(fileName: str, old_c: Cmdr = None, gui: LeoGui = None) -> Cmdr:
    """
    Create a Leo Frame for the indicated fileName if the file exists.

    Return the commander of the newly-opened outline.
    """
    return g.app.loadManager.loadLocalFile(fileName, gui, old_c)
#@+node:ekr.20150306035851.7: *3* g.readFileIntoEncodedString
def readFileIntoEncodedString(fn: str, silent: bool = False) -> bytes:
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
def readFileIntoString(
    fileName: str,
    encoding: str = 'utf-8',  # BOM may override this.
    kind: str = None,  # @file, @edit, ...
    verbose: bool = True,
) -> tuple[Any, Any]:
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
        if verbose:
            g.trace('no fileName arg given')
        return None, None
    if g.os_path_isdir(fileName):
        if verbose:
            g.trace('not a file:', fileName)
        return None, None
    if not g.os_path_exists(fileName):
        if verbose:
            g.error('file not found:', fileName)
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
def readFileIntoUnicodeString(
    fn: str,
    encoding: Optional[str] = None,
    silent: bool = False,
) -> Optional[str]:
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

def readlineForceUnixNewline(f: Any, fileName: Optional[str] = None) -> str:
    try:
        s = f.readline()
    except UnicodeDecodeError:
        g.trace(f"UnicodeDecodeError: {fileName}", f, g.callers())
        s = ''
    if len(s) >= 2 and s[-2] == "\r" and s[-1] == "\n":
        s = s[0:-2] + "\n"
    return s
#@+node:ekr.20031218072017.3124: *3* g.sanitize_filename
def sanitize_filename(s: str) -> str:
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
def setGlobalOpenDir(fileName: str) -> None:
    if fileName:
        g.app.globalOpenDir = g.os_path_dirname(fileName)
        # g.es('current directory:',g.app.globalOpenDir)
#@+node:ekr.20031218072017.3125: *3* g.shortFileName & shortFilename
def shortFileName(fileName: str, n: int = None) -> str:
    """Return the base name of a path."""
    if n is not None:
        g.trace('"n" keyword argument is no longer used')
    return g.os_path_basename(fileName) if fileName else ''

shortFilename = shortFileName
#@+node:ekr.20150610125813.1: *3* g.splitLongFileName
def splitLongFileName(fn: str, limit: int = 40) -> str:
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
#@+node:ekr.20190114061452.26: *3* g.writeFile
def writeFile(contents: Union[bytes, str], encoding: str, fileName: str) -> bool:
    """Create a file with the given contents."""
    try:
        if isinstance(contents, str):
            contents = g.toEncodedString(contents, encoding=encoding)
        # 'wb' preserves line endings.
        with open(fileName, 'wb') as f:
            f.write(contents)  # type:ignore
        return True
    except Exception as e:
        print(f"exception writing: {fileName}:\n{e}")
        # g.trace(g.callers())
        # g.es_exception()
        return False
#@+node:ekr.20230113043029.1: *3* g.write_file_if_changed
def write_file_if_changed(fn: str, s: str, encoding: str = 'utf-8') -> bool:
    """
    Replace file whose filename is give with s, but *only* if file's
    context has changed (or the file does not exist).

    Return True if the file was written.
    """
    try:
        encoded_s = g.toEncodedString(s, encoding=encoding, reportErrors=True)
        if os.path.exists(fn):
            with open(fn, 'rb') as f:
                contents = f.read()
            if contents == encoded_s:
                return False
        with open(fn, 'wb') as f:
            f.write(encoded_s)
        return True
    except Exception:
        g.es_print(f"Exception writing {fn}")
        g.es_exception()
        return False
#@+node:ekr.20031218072017.3151: ** g.Finding & Scanning
#@+node:ekr.20140602083643.17659: *3* g.find_word
def find_word(s: str, word: str, i: int = 0) -> int:
    """
    Return the index of the first occurrence of word in s, or -1 if not found.

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
#@+node:ekr.20211029090118.1: *3* g.findAncestorVnodeByPredicate
def findAncestorVnodeByPredicate(p: Position, v_predicate: Any) -> Optional[VNode]:
    """
    Return first ancestor vnode matching the predicate.

    The predicate must must be a function of a single vnode argument.
    """
    if not p:
        return None
    # First, look up the tree.
    for p2 in p.self_and_parents():
        if v_predicate(p2.v):
            return p2.v
    # Look at parents of all cloned nodes.
    if not p.isCloned():
        return None
    seen = []  # vnodes that have already been searched.
    parents = p.v.parents[:]  # vnodes to be searched.
    while parents:
        parent_v = parents.pop()
        if parent_v in seen:
            continue
        seen.append(parent_v)
        if v_predicate(parent_v):
            return parent_v
        for grand_parent_v in parent_v.parents:
            if grand_parent_v not in seen:
                parents.append(grand_parent_v)
    return None
#@+node:ekr.20170220103251.1: *3* g.findRootsWithPredicate
def findRootsWithPredicate(c: Cmdr, root: Position, predicate: Callable = None) -> list[Position]:
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

        def predicate(p: Position) -> bool:
            headline = p.h.strip()
            is_python = headline.endswith(('py', 'pyw'))
            return p.isAnyAtFileNode() and is_python

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
#@+node:ekr.20031218072017.3156: *3* g.scanError
# It is dubious to bump the Tangle error count here, but it really doesn't hurt.

def scanError(s: str) -> None:
    """Bump the error count in the tangle command."""
    # New in Leo 4.4b1: just set this global.
    g.app.scanErrors += 1
    g.es('', s)
#@+node:ekr.20031218072017.3157: *3* g.scanf
# A quick and dirty sscanf.  Understands only %s and %d.

def scanf(s: str, pat: str) -> list[str]:
    count = pat.count("%s") + pat.count("%d")
    pat = pat.replace("%s", r"(\S+)")
    pat = pat.replace("%d", r"(\d+)")
    parts = re.split(pat, s)
    result: list[str] = []
    for part in parts:
        if part and len(result) < count:
            result.append(part)
    return result
#@+node:ekr.20031218072017.3158: *3* g.Scanners: calling scanError
#@+at These scanners all call g.scanError() directly or indirectly, so they
# will call g.es if they find an error. g.scanError() also bumps
# c.tangleCommands.errors, which is harmless if we aren't tangling, and
# useful if we are.
#
# These routines are called by the Import routines and the Tangle routines.
#@+node:ekr.20031218072017.3159: *4* g.skip_block_comment
# Scans past a block comment (an old_style C comment).

def skip_block_comment(s: str, i: int) -> int:
    assert g.match(s, i, "/*")
    j = i
    i += 2
    n = len(s)
    k = s.find("*/", i)
    if k == -1:
        g.scanError("Run on block comment: " + s[j:i])
        return n
    return k + 2
#@+node:ekr.20031218072017.3160: *4* g.skip_braces
#@+at This code is called only from the import logic, so we are allowed to
# try some tricks. In particular, we assume all braces are matched in
# if blocks.
#@@c

def skip_braces(s: str, i: int) -> int:
    """
    Skips from the opening to the matching brace.

    If no matching is found i is set to len(s)
    """
    # start = g.get_line(s,i)
    assert g.match(s, i, '{')
    level = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c == '{':
            level += 1
            i += 1
        elif c == '}':
            level -= 1
            if level <= 0:
                return i
            i += 1
        elif c == '\'' or c == '"':
            i = g.skip_string(s, i)
        elif g.match(s, i, '//'):
            i = g.skip_to_end_of_line(s, i)
        elif g.match(s, i, '/*'):
            i = g.skip_block_comment(s, i)
        # 7/29/02: be more careful handling conditional code.
        elif (
            g.match_word(s, i, "#if") or
            g.match_word(s, i, "#ifdef") or
            g.match_word(s, i, "#ifndef")
        ):
            i, delta = g.skip_pp_if(s, i)
            level += delta
        else:
            i += 1
    return i
#@+node:ekr.20031218072017.3162: *4* g.skip_parens
def skip_parens(s: str, i: int) -> int:
    """
    Skips from the opening ( to the matching ).

    If no matching is found i is set to len(s).
    """
    level = 0
    n = len(s)
    assert g.match(s, i, '('), repr(s[i])
    while i < n:
        c = s[i]
        if c == '(':
            level += 1
            i += 1
        elif c == ')':
            level -= 1
            if level <= 0:
                return i
            i += 1
        elif c == '\'' or c == '"':
            i = g.skip_string(s, i)
        elif g.match(s, i, "//"):
            i = g.skip_to_end_of_line(s, i)
        elif g.match(s, i, "/*"):
            i = g.skip_block_comment(s, i)
        else:
            i += 1
    return i
#@+node:ekr.20031218072017.3163: *4* g.skip_pascal_begin_end
def skip_pascal_begin_end(s: str, i: int) -> int:
    """
    Skips from begin to matching end.
    If found, i points to the end. Otherwise, i >= len(s)
    The end keyword matches begin, case, class, record, and try.
    """
    assert g.match_c_word(s, i, "begin")
    level = 1
    i = g.skip_c_id(s, i)  # Skip the opening begin.
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
            j = i
            i = g.skip_c_id(s, i)
            name = s[j:i]
            if name in ["begin", "case", "class", "record", "try"]:
                level += 1
        else:
            i += 1
    return i
#@+node:ekr.20031218072017.3164: *4* g.skip_pascal_block_comment
def skip_pascal_block_comment(s: str, i: int) -> int:
    """Scan past a pascal comment delimited by (* and *)."""
    j = i
    assert g.match(s, i, "(*")
    i = s.find("*)", i)
    if i > -1:
        return i + 2
    g.scanError("Run on comment" + s[j:i])
    return len(s)
#@+node:ekr.20031218072017.3165: *4* g.skip_pascal_string
def skip_pascal_string(s: str, i: int) -> int:
    j = i
    delim = s[i]
    i += 1
    assert delim == '"' or delim == '\''
    while i < len(s):
        if s[i] == delim:
            return i + 1
        i += 1
    g.scanError("Run on string: " + s[j:i])
    return i
#@+node:ekr.20031218072017.3166: *4* g.skip_heredoc_string
def skip_heredoc_string(s: str, i: int) -> int:
    """
    08-SEP-2002 DTHEIN.
    A heredoc string in PHP looks like:

      <<<EOS
      This is my string.
      It is mine. I own it.
      No one else has it.
      EOS

    It begins with <<< plus a token (naming same as PHP variable names).
    It ends with the token on a line by itself (must start in first position.
    """
    j = i
    assert g.match(s, i, "<<<")
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
#@+node:ekr.20031218072017.3167: *4* g.skip_pp_directive
def skip_pp_directive(s: str, i: int) -> int:
    """Now handles continuation lines and block comments."""
    while i < len(s):
        if g.is_nl(s, i):
            if g.escaped(s, i):
                i = g.skip_nl(s, i)
            else:
                break
        elif g.match(s, i, "//"):
            i = g.skip_to_end_of_line(s, i)
        elif g.match(s, i, "/*"):
            i = g.skip_block_comment(s, i)
        else:
            i += 1
    return i
#@+node:ekr.20031218072017.3168: *4* g.skip_pp_if
# Skips an entire if or if def statement, including any nested statements.

def skip_pp_if(s: str, i: int) -> tuple[int, int]:
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
#@+node:ekr.20031218072017.3169: *4* g.skip_pp_part
# Skip to an #else or #endif.  The caller has eaten the #if, #ifdef, #ifndef or #else

def skip_pp_part(s: str, i: int) -> tuple[int, int]:

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
        elif c == '\'' or c == '"':
            i = g.skip_string(s, i)
        elif c == '{':
            delta += 1
            i += 1
        elif c == '}':
            delta -= 1
            i += 1
        elif g.match(s, i, "//"):
            i = g.skip_line(s, i)
        elif g.match(s, i, "/*"):
            i = g.skip_block_comment(s, i)
        else:
            i += 1
    return i, delta
#@+node:ekr.20031218072017.3171: *4* g.skip_to_semicolon
# Skips to the next semicolon that is not in a comment or a string.

def skip_to_semicolon(s: str, i: int) -> int:
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
#@+node:ekr.20031218072017.3172: *4* g.skip_typedef
def skip_typedef(s: str, i: int) -> int:
    n = len(s)
    while i < n and g.is_c_id(s[i]):
        i = g.skip_c_id(s, i)
        i = g.skip_ws_and_nl(s, i)
    if g.match(s, i, '{'):
        i = g.skip_braces(s, i)
        i = g.skip_to_semicolon(s, i)
    return i
#@+node:ekr.20201127143342.1: *3* g.see_more_lines
def see_more_lines(s: str, ins: int, n: int = 4) -> int:
    """
    Extend index i within string s to include n more lines.
    """
    # Show more lines, if they exist.
    if n > 0:
        for _z in range(n):
            if ins >= len(s):
                break
            i, j = g.getLine(s, ins)
            ins = j
    return max(0, min(ins, len(s)))
#@+node:ekr.20031218072017.3195: *3* g.splitLines
def splitLines(s: str) -> list[str]:
    """
    Split s into lines, preserving the number of lines and
    the endings of all lines, including the last line.
    """
    # The guard protects only against s == None.
    return s.splitlines(True) if s else []  # This is a Python string function!

splitlines = splitLines
#@+node:ekr.20031218072017.3173: *3* Scanners: no error messages
#@+node:ekr.20031218072017.3174: *4* g.escaped
# Returns True if s[i] is preceded by an odd number of backslashes.

def escaped(s: str, i: int) -> bool:
    count = 0
    while i - 1 >= 0 and s[i - 1] == '\\':
        count += 1
        i -= 1
    return (count % 2) == 1
#@+node:ekr.20031218072017.3175: *4* g.find_line_start
def find_line_start(s: str, i: int) -> int:
    """Return the index in s of the start of the line containing s[i]."""
    if i < 0:
        return 0  # New in Leo 4.4.5: add this defensive code.
    # bug fix: 11/2/02: change i to i+1 in rfind
    i = s.rfind('\n', 0, i + 1)  # Finds the highest index in the range.
    return 0 if i == -1 else i + 1
#@+node:ekr.20031218072017.3176: *4* g.find_on_line
def find_on_line(s: str, i: int, pattern: str) -> int:
    j = s.find('\n', i)
    if j == -1:
        j = len(s)
    k = s.find(pattern, i, j)
    return k
#@+node:ekr.20031218072017.3179: *4* g.is_special
def is_special(s: str, directive: str) -> tuple[bool, int]:
    """Return True if the body text contains the @ directive."""
    assert(directive and directive[0] == '@')
    # Most directives must start the line.
    lws = directive in ("@others", "@all")
    pattern_s = r'^\s*(%s\b)' if lws else r'^(%s\b)'
    pattern = re.compile(pattern_s % directive, re.MULTILINE)
    m = re.search(pattern, s)
    if m:
        return True, m.start(1)
    return False, -1
#@+node:ekr.20031218072017.3177: *4* g.is_c_id
def is_c_id(ch: str) -> bool:
    return g.isWordChar(ch)
#@+node:ekr.20031218072017.3178: *4* g.is_nl
def is_nl(s: str, i: int) -> bool:
    return i < len(s) and (s[i] == '\n' or s[i] == '\r')
#@+node:ekr.20031218072017.3180: *4* g.is_ws & is_ws_or_nl
def is_ws(ch: str) -> bool:
    return ch == '\t' or ch == ' '

def is_ws_or_nl(s: str, i: int) -> bool:
    return g.is_nl(s, i) or (i < len(s) and g.is_ws(s[i]))
#@+node:ekr.20031218072017.3181: *4* g.match
# Warning: this code makes no assumptions about what follows pattern.

def match(s: str, i: int, pattern: str) -> bool:
    return bool(s and pattern and s.find(pattern, i, i + len(pattern)) == i)
#@+node:ekr.20031218072017.3182: *4* g.match_c_word
def match_c_word(s: str, i: int, name: str) -> bool:
    n = len(name)
    return bool(
        name and
        name == s[i : i + n] and
        (i + n == len(s) or not g.is_c_id(s[i + n]))
    )
#@+node:ekr.20031218072017.3183: *4* g.match_ignoring_case
def match_ignoring_case(s1: str, s2: str) -> bool:
    return bool(s1 and s2 and s1.lower() == s2.lower())
#@+node:ekr.20031218072017.3184: *4* g.match_word & g.match_words
def match_word(s: str, i: int, pattern: str) -> bool:

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

def match_words(s: str, i: int, patterns: Sequence[str]) -> bool:
    return any(g.match_word(s, i, pattern) for pattern in patterns)
#@+node:ekr.20031218072017.3185: *4* g.skip_blank_lines
# This routine differs from skip_ws_and_nl in that
# it does not advance over whitespace at the start
# of a non-empty or non-nl terminated line

def skip_blank_lines(s: str, i: int) -> int:
    while i < len(s):
        if g.is_nl(s, i):
            i = g.skip_nl(s, i)
        elif g.is_ws(s[i]):
            j = g.skip_ws(s, i)
            if g.is_nl(s, j):
                i = j
            else:
                break
        else:
            break
    return i
#@+node:ekr.20031218072017.3186: *4* g.skip_c_id
def skip_c_id(s: str, i: int) -> int:
    n = len(s)
    while i < n and g.isWordChar(s[i]):
        i += 1
    return i
#@+node:ekr.20040705195048: *4* g.skip_id
def skip_id(s: str, i: int, chars: str = None) -> int:
    chars = g.toUnicode(chars) if chars else ''
    n = len(s)
    while i < n and (g.isWordChar(s[i]) or s[i] in chars):
        i += 1
    return i
#@+node:ekr.20031218072017.3187: *4* g.skip_line, skip_to_start/end_of_line
#@+at These methods skip to the next newline, regardless of whether the
# newline may be preceded by a backslash. Consequently, they should be
# used only when we know that we are not in a preprocessor directive or
# string.
#@@c

def skip_line(s: str, i: int) -> int:
    if i >= len(s):
        return len(s)
    if i < 0:
        i = 0
    i = s.find('\n', i)
    if i == -1:
        return len(s)
    return i + 1

def skip_to_end_of_line(s: str, i: int) -> int:
    if i >= len(s):
        return len(s)
    if i < 0:
        i = 0
    i = s.find('\n', i)
    if i == -1:
        return len(s)
    return i

def skip_to_start_of_line(s: str, i: int) -> int:
    if i >= len(s):
        return len(s)
    if i <= 0:
        return 0
    # Don't find s[i], so it doesn't matter if s[i] is a newline.
    i = s.rfind('\n', 0, i)
    if i == -1:
        return 0
    return i + 1
#@+node:ekr.20031218072017.3188: *4* g.skip_long
def skip_long(s: str, i: int) -> tuple[int, Optional[int]]:
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
#@+node:ekr.20031218072017.3190: *4* g.skip_nl
# We need this function because different systems have different end-of-line conventions.

def skip_nl(s: str, i: int) -> int:
    """Skips a single "logical" end-of-line character."""
    if g.match(s, i, "\r\n"):
        return i + 2
    if g.match(s, i, '\n') or g.match(s, i, '\r'):
        return i + 1
    return i
#@+node:ekr.20031218072017.3191: *4* g.skip_non_ws
def skip_non_ws(s: str, i: int) -> int:
    n = len(s)
    while i < n and not g.is_ws(s[i]):
        i += 1
    return i
#@+node:ekr.20031218072017.3192: *4* g.skip_pascal_braces
# Skips from the opening { to the matching }.

def skip_pascal_braces(s: str, i: int) -> int:
    # No constructs are recognized inside Pascal block comments!
    if i == -1:
        return len(s)
    return s.find('}', i)
#@+node:ekr.20031218072017.3170: *4* g.skip_python_string
def skip_python_string(s: str, i: int) -> int:
    if g.match(s, i, "'''") or g.match(s, i, '"""'):
        delim = s[i] * 3
        i += 3
        k = s.find(delim, i)
        if k > -1:
            return k + 3
        return len(s)
    return g.skip_string(s, i)
#@+node:ekr.20031218072017.2369: *4* g.skip_string
def skip_string(s: str, i: int) -> int:
    """Scan forward to the end of a string."""
    delim = s[i]
    i += 1
    assert delim in '\'"', (repr(delim), repr(s))
    n = len(s)
    while i < n and s[i] != delim:
        if s[i] == '\\':
            i += 2
        else:
            i += 1
    if i >= n:
        pass
    elif s[i] == delim:
        i += 1
    return i
#@+node:ekr.20031218072017.3193: *4* g.skip_to_char
def skip_to_char(s: str, i: int, ch: str) -> tuple[int, str]:
    j = s.find(ch, i)
    if j == -1:
        return len(s), s[i:]
    return j, s[i:j]
#@+node:ekr.20031218072017.3194: *4* g.skip_ws, skip_ws_and_nl
def skip_ws(s: str, i: int) -> int:
    n = len(s)
    while i < n and g.is_ws(s[i]):
        i += 1
    return i

def skip_ws_and_nl(s: str, i: int) -> int:
    n = len(s)
    while i < n and (g.is_ws(s[i]) or g.is_nl(s, i)):
        i += 1
    return i
#@+node:ekr.20170414034616.1: ** g.Git
#@+node:ekr.20180325025502.1: *3* g.backupGitIssues
def backupGitIssues(c: Cmdr, base_url: str = None) -> None:
    """Get a list of issues from Leo's GitHub site."""
    if base_url is None:
        base_url = 'https://api.github.com/repos/leo-editor/leo-editor/issues'

    root = c.lastTopLevel().insertAfter()
    root.h = f'Backup of issues: {time.strftime("%Y/%m/%d")}'
    label_list: list[str] = []
    GitIssueController().backup_issues(base_url, c, label_list, root)
    root.expand()
    c.selectPosition(root)
    c.redraw()
    g.trace('done')
#@+node:ekr.20170616102324.1: *3* g.execGitCommand
def execGitCommand(command: str, directory: str) -> list[str]:
    """
    Execute the given git command in the given directory.

    Return a list of lines, with newlines stripped off.
    """
    git_dir = g.finalize_join(directory, '.git')
    if not g.os_path_exists(git_dir):
        g.trace('.git directory not found:', git_dir, g.callers())
        return []
    if '\n' in command:
        g.trace('removing newline from', command)
        command = command.replace('\n', '')
    # #1777: Save/restore os.curdir
    old_dir = os.getcwd()
    if directory:
        # g.trace(f"os.chdir({directory})")
        os.chdir(directory)
    try:
        p = subprocess.Popen(
            shlex.split(command),
            stdout=subprocess.PIPE,
            stderr=None,  # Shows error traces.
            # stderr=subprocess.PIPE,
            shell=False,
        )
        out, err = p.communicate()
        lines = [g.toUnicode(z) for z in g.splitLines(out or [])]
    finally:
        os.chdir(old_dir)
    return lines
#@+node:ekr.20180126043905.1: *3* g.getGitIssues
def getGitIssues(c: Cmdr,
    base_url: str = None,
    label_list: list = None,
    milestone: str = None,
    state: Optional[str] = None,  # in (None, 'closed', 'open')
) -> None:
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
    def backup_issues(self,
        base_url: str,
        c: Cmdr,
        label_list: list[str],
        root: Position,
        state: str = None,
    ) -> None:

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
    def get_all_issues(self, label_list: list, root: Position, state: Any, limit: int = 100) -> None:
        """Get all issues for the base url."""
        try:
            import requests
        except Exception:
            g.trace('requests not found: `pip install requests`')
            return
        label = None
        assert state in ('open', 'closed')
        page_url = self.base_url + '?&state=%s&page=%s'
        page, total = 1, 0
        while True:
            url = page_url % (state, page)
            r = requests.get(url, timeout=2.0)
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
    #@+node:ekr.20180126044850.1: *5* git.get_issues
    def get_issues(self, base_url: str, label_list: list, milestone: Any, root: Position, state: Any) -> None:
        """Create a list of issues for each label in label_list."""
        self.base_url = base_url
        self.milestone = milestone
        self.root = root
        for label in label_list:
            self.get_one_issue(label, state)
    #@+node:ekr.20180126043719.3: *5* git.get_one_issue
    def get_one_issue(self, label: str, state: Any, limit: int = 20) -> None:
        """Create a list of issues with the given label."""
        try:
            import requests
        except Exception:
            g.trace('requests not found: `pip install requests`')
            return
        root = self.root.insertAsLastChild()
        page, total = 1, 0
        page_url = self.base_url + '?labels=%s&state=%s&page=%s'
        while True:
            url = page_url % (label, state, page)
            r = requests.get(url, timeout=2.0)
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
    def get_one_page(self, label: str, page: int, r: Any, root: Position) -> tuple[bool, int]:

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
    def print_header(self, r: Any) -> None:

        # r.headers is a CaseInsensitiveDict
        # so g.printObj(r.headers) is just repr(r.headers)
        if 0:
            print('Link', r.headers.get('Link'))
        else:
            for key in r.headers:
                print(f"{key:35}: {r.headers.get(key)}")
    #@-others
#@+node:ekr.20190428173354.1: *3* g.getGitVersion
def getGitVersion(directory: str = None) -> tuple[str, str, str]:
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

    def find(kind: str) -> str:
        """Return the given type of log line."""
        for z in info:
            if z.startswith(kind):
                return z.lstrip(kind).lstrip(':').strip()
        return ''

    return find('Author'), find('commit')[:10], find('Date')
#@+node:ekr.20170414034616.2: *3* g.gitBranchName
def gitBranchName(path: str = None) -> str:
    """
    Return the git branch name associated with path/.git, or the empty
    string if path/.git does not exist. If path is None, use the leo-editor
    directory.
    """
    branch, commit = g.gitInfo(path)
    return branch
#@+node:ekr.20170414034616.4: *3* g.gitCommitNumber
def gitCommitNumber(path: str = None) -> str:
    """
    Return the git commit number associated with path/.git, or the empty
    string if path/.git does not exist. If path is None, use the leo-editor
    directory.
    """
    branch, commit = g.gitInfo(path)
    return commit
#@+node:ekr.20200724132432.1: *3* g.gitInfoForFile
def gitInfoForFile(filename: str) -> tuple[str, str]:
    """
    Return the git (branch, commit) info associated for the given file.
    """
    # g.gitInfo and g.gitHeadPath now do all the work.
    return g.gitInfo(filename)
#@+node:ekr.20200724133754.1: *3* g.gitInfoForOutline
def gitInfoForOutline(c: Cmdr) -> tuple[str, str]:
    """
    Return the git (branch, commit) info associated for commander c.
    """
    return g.gitInfoForFile(c.fileName())
#@+node:maphew.20171112205129.1: *3* g.gitDescribe
def gitDescribe(path: str = None) -> tuple[str, str, str]:
    """
    Return the Git tag, distance-from-tag, and commit hash for the
    associated path. If path is None, use the leo-editor directory.

    Given `git describe` cmd line output: `x-leo-v5.6-55-ge1129da\n`
    This function returns ('x-leo-v5.6', '55', 'e1129da')
    """
    describe = g.execGitCommand('git describe --tags --long', path)
    # rsplit not split, as '-' might be in tag name.
    tag, distance, commit = describe[0].rsplit('-', 2)
    if 'g' in commit[0:]:
        # leading 'g' isn't part of the commit hash.
        commit = commit[1:]
    commit = commit.rstrip()
    return tag, distance, commit
#@+node:ekr.20170414034616.6: *3* g.gitHeadPath
def gitHeadPath(path_s: str) -> Optional[str]:
    """
    Compute the path to .git/HEAD given the path.
    """
    path = Path(path_s)
    # #1780: Look up the directory tree, looking the .git directory.
    while os.path.exists(path):
        head = os.path.join(path, '.git', 'HEAD')
        if os.path.exists(head):
            return head
        if path == path.parent:
            break
        path = path.parent
    return None
#@+node:ekr.20170414034616.3: *3* g.gitInfo
def gitInfo(path: str = None) -> tuple[str, str]:
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
    git_dir = g.finalize_join(path, '..')
    try:
        path = g.finalize_join(git_dir, pointer)
        with open(path) as f:
            s = f.read()
        commit = s.strip()[0:12]
        # shorten the hash to a unique shortname
    except IOError:
        try:
            path = g.finalize_join(git_dir, 'packed-refs')
            with open(path) as f:  # type:ignore
                for line in f:
                    if line.strip().endswith(' ' + pointer):
                        commit = line.split()[0][0:12]
                        break
        except IOError:
            pass
    return branch, commit
#@+node:ekr.20031218072017.3139: ** g.Hooks & Plugins
#@+node:ekr.20101028131948.5860: *3* g.act_on_node
def dummy_act_on_node(c: Cmdr, p: Position, event: Any) -> None:
    pass

# This dummy definition keeps pylint happy.
# Plugins can change this.

act_on_node = dummy_act_on_node
#@+node:ville.20120502221057.7500: *3* g.childrenModifiedSet, g.contentModifiedSet
childrenModifiedSet: set[VNode] = set()
contentModifiedSet: set[VNode] = set()
#@+node:ekr.20031218072017.1596: *3* g.doHook
def doHook(tag: str, *args: Any, **keywords: Any) -> Any:
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
    if not g.app.enablePlugins:
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
        g.app.hookError = True  # Suppress this function.
        g.app.idle_time_hooks_enabled = False
        return None
#@+node:ekr.20100910075900.5950: *3* g.Wrappers for g.app.pluginController methods
# Important: we can not define g.pc here!
#@+node:ekr.20100910075900.5951: *4* g.Loading & registration
def loadOnePlugin(pluginName: str, verbose: bool = False) -> Any:
    pc = g.app.pluginsController
    return pc.loadOnePlugin(pluginName, verbose=verbose)

def registerExclusiveHandler(tags: list[str], fn: str) -> Any:
    pc = g.app.pluginsController
    return pc.registerExclusiveHandler(tags, fn)

def registerHandler(tags: Any, fn: Any) -> Any:
    pc = g.app.pluginsController
    return pc.registerHandler(tags, fn)

def plugin_signon(module_name: str, verbose: bool = False) -> Any:
    pc = g.app.pluginsController
    return pc.plugin_signon(module_name, verbose)

def unloadOnePlugin(moduleOrFileName: str, verbose: bool = False) -> Any:
    pc = g.app.pluginsController
    return pc.unloadOnePlugin(moduleOrFileName, verbose)

def unregisterHandler(tags: Any, fn: Any) -> Any:
    pc = g.app.pluginsController
    return pc.unregisterHandler(tags, fn)
#@+node:ekr.20100910075900.5952: *4* g.Information
def getHandlersForTag(tags: list[str]) -> list:
    pc = g.app.pluginsController
    return pc.getHandlersForTag(tags)

def getLoadedPlugins() -> list:
    pc = g.app.pluginsController
    return pc.getLoadedPlugins()

def getPluginModule(moduleName: str) -> Any:
    pc = g.app.pluginsController
    return pc.getPluginModule(moduleName)

def pluginIsLoaded(fn: str) -> bool:
    pc = g.app.pluginsController
    return pc.isLoaded(fn)
#@+node:ekr.20031218072017.1315: ** g.Idle time functions
#@+node:EKR.20040602125018.1: *3* g.disableIdleTimeHook
def disableIdleTimeHook() -> None:
    """Disable the global idle-time hook."""
    g.app.idle_time_hooks_enabled = False
#@+node:EKR.20040602125018: *3* g.enableIdleTimeHook
def enableIdleTimeHook(*args: Any, **keys: Any) -> None:
    """Enable idle-time processing."""
    g.app.idle_time_hooks_enabled = True
#@+node:ekr.20140825042850.18410: *3* g.IdleTime
def IdleTime(handler: Any, delay: int = 500, tag: str = None) -> Any:
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

        timer1 = g.IdleTime(handler1, delay=500)
        timer2 = g.IdleTime(handler2, delay=1000)
        if timer1 and timer2:
            timer1.start()
            timer2.start()
    """
    try:
        return g.app.gui.idleTimeClass(handler, delay, tag)
    except Exception:
        return None
#@+node:ekr.20161027205025.1: *3* g.idleTimeHookHandler (stub)
def idleTimeHookHandler(timer: Any) -> None:
    """This function exists for compatibility."""
    g.es_print('Replaced by IdleTimeManager.on_idle')
    g.trace(g.callers())
#@+node:ekr.20041219095213: ** g.Importing
#@+node:ekr.20040917061619: *3* g.cantImport
def cantImport(moduleName: str, pluginName: str = None, verbose: bool = True) -> None:
    """Print a "Can't Import" message and return None."""
    s = f"Can not import {moduleName}"
    if pluginName:
        s = s + f" from {pluginName}"
    if not g.app or not g.app.gui:
        print(s)
    elif g.unitTesting:
        return
    else:
        g.warning('', s)
#@+node:ekr.20191220044128.1: *3* g.import_module
def import_module(name: str, package: str = None) -> Any:
    """
    A thin wrapper over importlib.import_module.
    """
    trace = 'plugins' in g.app.debug and not g.unitTesting
    exceptions = []
    try:
        m = importlib.import_module(name, package=package)
    except Exception as e:
        m = None
        if trace:
            t, v, tb = sys.exc_info()
            del tb  # don't need the traceback
            # In case v is empty, we'll at least have the exception type
            v = v or str(t)  # type:ignore
            if v not in exceptions:
                exceptions.append(v)
                g.trace(f"Can not import {name}: {e}")
    return m
#@+node:ekr.20140711071454.17650: ** g.Indices, Strings, Unicode & Whitespace
#@+node:ekr.20140711071454.17647: *3* g.Indices
#@+node:ekr.20050314140957: *4* g.convertPythonIndexToRowCol
def convertPythonIndexToRowCol(s: str, i: int) -> tuple[int, int]:
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
def convertRowColToPythonIndex(s: str, row: int, col: int, lines: list[str] = None) -> int:
    """Convert zero-based row/col indices into a python index into string s."""
    if row < 0:
        return 0
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
def getWord(s: str, i: int) -> tuple[int, int]:
    """Return i,j such that s[i:j] is the word surrounding s[i]."""
    if i >= len(s):
        i = len(s) - 1
    if i < 0:
        i = 0
    # Scan backwards.
    while 0 <= i < len(s) and g.isWordChar(s[i]):
        i -= 1
    i += 1
    # Scan forwards.
    j = i
    while 0 <= j < len(s) and g.isWordChar(s[j]):
        j += 1
    return i, j

def getLine(s: str, i: int) -> tuple[int, int]:
    """
    Return i,j such that s[i:j] is the line surrounding s[i].
    s[i] is a newline only if the line is empty.
    s[j] is a newline unless there is no trailing newline.
    """
    if i > len(s):
        i = len(s) - 1
    if i < 0:
        i = 0
    # A newline *ends* the line, so look to the left of a newline.
    j = s.rfind('\n', 0, i)
    if j == -1:
        j = 0
    else:
        j += 1
    k = s.find('\n', i)
    if k == -1:
        k = len(s)
    else:
        k = k + 1
    return j, k
#@+node:ekr.20111114151846.9847: *4* g.toPythonIndex
def toPythonIndex(s: str, index: str) -> int:
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
        row1, col1 = data
        row, col = int(row1), int(col1)
        i = g.convertRowColToPythonIndex(s, row - 1, col)
        return i
    g.trace(f"bad string index: {index}")
    return 0
#@+node:ekr.20140526144610.17601: *3* g.Strings
#@+node:ekr.20031218072017.3106: *4* g.angleBrackets & virtual_event_name
def angleBrackets(s: str) -> str:
    """Returns < < s > >"""
    lt = "<<"
    rt = ">>"
    return lt + s + rt

virtual_event_name = angleBrackets
#@+node:ekr.20090516135452.5777: *4* g.ensureLeading/TrailingNewlines
def ensureLeadingNewlines(s: str, n: int) -> str:
    s = g.removeLeading(s, '\t\n\r ')
    return ('\n' * n) + s

def ensureTrailingNewlines(s: str, n: int) -> str:
    s = g.removeTrailing(s, '\t\n\r ')
    return s + '\n' * n
#@+node:ekr.20190503145501.1: *4* g.isascii
def isascii(s: str) -> bool:
    # s.isascii() is defined in Python 3.7.
    return all(ord(ch) < 128 for ch in s)
#@+node:ekr.20050920084036.4: *4* g.longestCommonPrefix & g.itemsMatchingPrefixInList
def longestCommonPrefix(s1: str, s2: str) -> str:
    """Find the longest prefix common to strings s1 and s2."""
    prefix = ''
    for ch in s1:
        if s2.startswith(prefix + ch):
            prefix = prefix + ch
        else:
            return prefix
    return prefix

def itemsMatchingPrefixInList(s: str, aList: list[str], matchEmptyPrefix: bool = False) -> tuple[list, str]:
    """This method returns a sorted list items of aList whose prefix is s.

    It also returns the longest common prefix of all the matches.
    """
    if s:
        pmatches = [a for a in aList if a.startswith(s)]
    elif matchEmptyPrefix:
        pmatches = aList[:]
    else:
        pmatches = []
    if pmatches:
        pmatches.sort()
        common_prefix = reduce(g.longestCommonPrefix, pmatches)
    else:
        common_prefix = ''
    return pmatches, common_prefix
#@+node:ekr.20230704030847.1: *4* g.pad
def pad(s: str, width: int) -> str:
    """Return a string of blanks to pad string s to the given width."""
    return ' ' * max(0, width - len(s))
#@+node:ekr.20090516135452.5776: *4* g.removeLeading/Trailing
# Warning: g.removeTrailingWs already exists.
# Do not change it!

def removeLeading(s: str, chars: str) -> str:
    """Remove all characters in chars from the front of s."""
    i = 0
    while i < len(s) and s[i] in chars:
        i += 1
    return s[i:]

def removeTrailing(s: str, chars: str) -> str:
    """Remove all characters in chars from the end of s."""
    i = len(s) - 1
    while i >= 0 and s[i] in chars:
        i -= 1
    i += 1
    return s[:i]
#@+node:ekr.20060410112600: *4* g.stripBrackets
def stripBrackets(s: str) -> str:
    """Strip leading and trailing angle brackets."""
    if s.startswith('<'):
        s = s[1:]
    if s.endswith('>'):
        s = s[:-1]
    return s
#@+node:ekr.20170317101100.1: *4* g.unCamel
def unCamel(s: str) -> list[str]:
    """Return a list of sub-words in camelCased string s."""
    result: list[str] = []
    word: list[str] = []
    for ch in s:
        if ch.isalpha() and ch.isupper():
            if word:
                result.append(''.join(word))
            word = [ch]
        elif ch.isalpha():
            word.append(ch)
        elif word:
            result.append(''.join(word))
            word = []
    if word:
        result.append(''.join(word))
    return result
#@+node:ekr.20031218072017.1498: *3* g.Unicode
#@+node:ekr.20190505052756.1: *4* g.checkUnicode
checkUnicode_dict: dict[str, bool] = {}

def checkUnicode(s: str, encoding: str = None) -> str:
    """
    Warn when converting bytes. Report *all* errors.

    This method is meant to document defensive programming. We don't expect
    these errors, but they might arise as the result of problems in
    user-defined plugins or scripts.
    """
    tag = 'g.checkUnicode'
    if s is None and g.unitTesting:
        return ''
    if isinstance(s, str):
        return s
    if not isinstance(s, bytes):
        g.error(f"{tag}: unexpected argument: {s!r}")
        g.trace('callers:', g.callers())
        return ''
    #
    # Report the unexpected conversion.
    callers = g.callers(1)
    if callers not in checkUnicode_dict:
        g.error(f"\n{tag}: expected unicode. got: {s!r}\n")
        g.trace(g.callers())
        checkUnicode_dict[callers] = True
    #
    # Convert to unicode, reporting all errors.
    if not encoding:
        encoding = 'utf-8'
    try:
        s = s.decode(encoding, 'strict')
    except(UnicodeDecodeError, UnicodeError):  # noqa
        # https://wiki.python.org/moin/UnicodeDecodeError
        s = s.decode(encoding, 'replace')
        g.trace(g.callers())
        g.error(f"{tag}: unicode error. encoding: {encoding!r}, s:\n{s!r}")
    except Exception:
        g.trace(g.callers())
        g.es_exception()
        g.error(f"{tag}: unexpected error! encoding: {encoding!r}, s:\n{s!r}")
    return s
#@+node:ekr.20100125073206.8709: *4* g.getPythonEncodingFromString
def getPythonEncodingFromString(s: str) -> str:
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
#@+node:ekr.20031218072017.1500: *4* g.isValidEncoding
def isValidEncoding(encoding: str) -> bool:
    """Return True if the encoding is valid."""
    if not encoding:
        return False
    if sys.platform == 'cli':
        return True
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
#@+node:ekr.20061006152327: *4* g.isWordChar & g.isWordChar1
def isWordChar(ch: str) -> bool:
    """Return True if ch should be considered a letter."""
    return bool(ch and (ch.isalnum() or ch == '_'))

def isWordChar1(ch: str) -> bool:
    return bool(ch and (ch.isalpha() or ch == '_'))
#@+node:ekr.20130910044521.11304: *4* g.stripBOM
def stripBOM(s_bytes: bytes) -> tuple[str, bytes]:
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
    if s_bytes:
        for n, e, bom in table:
            assert len(bom) == n
            if bom == s_bytes[: len(bom)]:
                return e, s_bytes[len(bom) :]
    return None, s_bytes
#@+node:ekr.20050208093800: *4* g.toEncodedString
def toEncodedString(s: str, encoding: str = 'utf-8', reportErrors: bool = False) -> bytes:
    """Convert unicode string to an encoded string."""
    if not isinstance(s, str):
        return s
    if not encoding:
        encoding = 'utf-8'
    # These are the only significant calls to s.encode in Leo.
    try:
        s = s.encode(encoding, "strict")  # type:ignore
    except UnicodeError:
        s = s.encode(encoding, "replace")  # type:ignore
        if reportErrors:
            g.error(f"Error converting {s} from unicode to {encoding} encoding")
    # Tracing these calls directly yields thousands of calls.
    return s  # type:ignore
#@+node:ekr.20050208093800.1: *4* g.toUnicode
unicode_warnings: dict[str, bool] = {}  # Keys are g.callers.

def toUnicode(s: Any, encoding: str = None, reportErrors: bool = False) -> str:
    """Convert bytes to unicode if necessary."""
    if isinstance(s, str):
        return s
    tag = 'g.toUnicode'
    if not isinstance(s, bytes):
        if reportErrors and not isinstance(s, (NullObject, TracingNullObject)):
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
    except(UnicodeDecodeError, UnicodeError):  # noqa
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
#@+node:ekr.20031218072017.3197: *3* g.Whitespace
#@+node:ekr.20031218072017.3198: *4* g.computeLeadingWhitespace
# Returns optimized whitespace corresponding to width with the indicated tab_width.

def computeLeadingWhitespace(width: int, tab_width: int) -> str:
    if width <= 0:
        return ""
    if tab_width > 1:
        tabs = int(width / tab_width)
        blanks = int(width % tab_width)
        return ('\t' * tabs) + (' ' * blanks)
    # Negative tab width always gets converted to blanks.
    return ' ' * width
#@+node:ekr.20120605172139.10263: *4* g.computeLeadingWhitespaceWidth
# Returns optimized whitespace corresponding to width with the indicated tab_width.

def computeLeadingWhitespaceWidth(s: str, tab_width: int) -> int:
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

def computeWidth(s: str, tab_width: int) -> int:
    w = 0
    for ch in s:
        if ch == '\t':
            w += (abs(tab_width) - (w % abs(tab_width)))
        elif ch == '\n':  # Bug fix: 2012/06/05.
            break
        else:
            w += 1
    return w
#@+node:ekr.20110727091744.15083: *4* g.wrap_lines (newer)
#@@language rest
#@+at
# Important note: this routine need not deal with leading whitespace.
#
# Instead, the caller should simply reduce pageWidth by the width of
# leading whitespace wanted, then add that whitespace to the lines
# returned here.
#
# The key to this code is the invariant that line never ends in whitespace.
#@@c
#@@language python

def wrap_lines(lines: list[str], pageWidth: int, firstLineWidth: int = None) -> list[str]:
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
    assert 0 < sentenceSpacingWidth < 3
    result = []  # The lines of the result.
    line = ""  # The line being formed.  It never ends in whitespace.
    for s in lines:
        i = 0
        while i < len(s):
            assert len(line) <= outputLineWidth  # DTHEIN 18-JAN-2004
            j = g.skip_ws(s, i)
            k = g.skip_non_ws(s, j)
            word = s[j:k]
            assert k > i
            i = k
            # DTHEIN 18-JAN-2004: wrap at exactly the text width,
            # not one character less
            #
            wordLen = len(word)
            if line.endswith('.') or line.endswith('?') or line.endswith('!'):
                space = ' ' * sentenceSpacingWidth
            else:
                space = ' '
            if line and wordLen > 0:
                wordLen += len(space)
            if wordLen + len(line) <= outputLineWidth:
                if wordLen > 0:
                    #@+<< place blank and word on the present line >>
                    #@+node:ekr.20110727091744.15084: *5* << place blank and word on the present line >>
                    if line:
                        # Add the word, preceded by a blank.
                        line = space.join((line, word))
                    else:
                        # Just add the word to the start of the line.
                        line = word
                    #@-<< place blank and word on the present line >>
                else:
                    pass  # discard the trailing whitespace.
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
def get_leading_ws(s: str) -> str:
    """Returns the leading whitespace of 's'."""
    i = 0
    n = len(s)
    while i < n and s[i] in (' ', '\t'):
        i += 1
    return s[0:i]
#@+node:ekr.20031218072017.3201: *4* g.optimizeLeadingWhitespace
# Optimize leading whitespace in s with the given tab_width.

def optimizeLeadingWhitespace(line: str, tab_width: int) -> str:
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

def regularizeTrailingNewlines(s: str, kind: str) -> None:
    """Kind is 'asis', 'zero' or 'one'."""
    pass
#@+node:ekr.20091229090857.11698: *4* g.removeBlankLines
def removeBlankLines(s: str) -> str:
    lines = g.splitLines(s)
    lines = [z for z in lines if z.strip()]
    return ''.join(lines)
#@+node:ekr.20091229075924.6235: *4* g.removeLeadingBlankLines
def removeLeadingBlankLines(s: str) -> str:
    lines = g.splitLines(s)
    result = []
    remove = True
    for line in lines:
        if remove and not line.strip():
            pass
        else:
            remove = False
            result.append(line)
    return ''.join(result)
#@+node:ekr.20031218072017.3202: *4* g.removeLeadingWhitespace
# Remove whitespace up to first_ws wide in s, given tab_width, the width of a tab.

def removeLeadingWhitespace(s: str, first_ws: int, tab_width: int) -> str:
    j = 0
    ws = 0
    first_ws = abs(first_ws)
    for ch in s:
        if ws >= first_ws:
            break
        elif ch == ' ':
            j += 1
            ws += 1
        elif ch == '\t':
            j += 1
            ws += (abs(tab_width) - (ws % abs(tab_width)))
        else:
            break
    if j > 0:
        s = s[j:]
    return s
#@+node:ekr.20031218072017.3203: *4* g.removeTrailingWs
# Warning: string.rstrip also removes newlines!

def removeTrailingWs(s: str) -> str:
    j = len(s) - 1
    while j >= 0 and (s[j] == ' ' or s[j] == '\t'):
        j -= 1
    return s[: j + 1]
#@+node:ekr.20031218072017.3204: *4* g.skip_leading_ws
# Skips leading up to width leading whitespace.

def skip_leading_ws(s: str, i: int, ws: int, tab_width: int) -> int:
    count = 0
    while count < ws and i < len(s):
        ch = s[i]
        if ch == ' ':
            count += 1
            i += 1
        elif ch == '\t':
            count += (abs(tab_width) - (count % abs(tab_width)))
            i += 1
        else:
            break
    return i
#@+node:ekr.20031218072017.3205: *4* g.skip_leading_ws_with_indent
def skip_leading_ws_with_indent(s: str, i: int, tab_width: int) -> tuple[int, int]:
    """Skips leading whitespace and returns (i, indent),

    - i points after the whitespace
    - indent is the width of the whitespace, assuming tab_width wide tabs."""
    count = 0
    n = len(s)
    while i < n:
        ch = s[i]
        if ch == ' ':
            count += 1
            i += 1
        elif ch == '\t':
            count += (abs(tab_width) - (count % abs(tab_width)))
            i += 1
        else:
            break
    return i, count
#@+node:ekr.20040723093558.1: *4* g.stripBlankLines
def stripBlankLines(s: str) -> str:
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
def doKeywordArgs(keys: dict, d: dict = None) -> dict:
    """
    Return a result dict that is a copy of the keys dict
    with missing items replaced by defaults in d dict.
    """
    if d is None:
        d = {}
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
def ecnl(tabName: str = 'Log') -> None:
    g.ecnls(1, tabName)

def ecnls(n: int, tabName: str = 'Log') -> None:
    log = app.log
    if log and not log.isNull:
        while log.newlines < n:
            g.enl(tabName)

def enl(tabName: str = 'Log') -> None:
    log = app.log
    if log and not log.isNull:
        log.newlines += 1
        log.putnl(tabName)
#@+node:ekr.20100914094836.5892: *3* g.error, g.note, g.warning, g.red, g.blue
def blue(*args: Any, **keys: Any) -> None:
    g.es_print(color='blue', *args, **keys)

def error(*args: Any, **keys: Any) -> None:
    g.es_print(color='error', *args, **keys)

def note(*args: Any, **keys: Any) -> None:
    g.es_print(color='note', *args, **keys)

def red(*args: Any, **keys: Any) -> None:
    g.es_print(color='red', *args, **keys)

def warning(*args: Any, **keys: Any) -> None:
    g.es_print(color='warning', *args, **keys)
#@+node:ekr.20070626132332: *3* g.es
def es(*args: Any, **keys: Any) -> None:
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
            if ch == '\n':
                log.newlines += 1
            else:
                log.newlines = 0
    else:
        app.logWaiting.append((s, color, newline, d),)

log = es
#@+node:ekr.20060917120951: *3* g.es_dump
def es_dump(s: str, n: int = 30, title: str = None) -> None:
    if title:
        g.es_print('', title)
    i = 0
    while i < len(s):
        aList = ''.join([f"{ord(ch):2x} " for ch in s[i : i + n]])
        g.es_print('', aList)
        i += n
#@+node:ekr.20031218072017.3110: *3* g.es_error & es_print_error
def es_error(*args: Any, **keys: Any) -> None:
    color = keys.get('color')
    if color is None and g.app.config:
        keys['color'] = g.app.config.getColor("log-error-color") or 'red'
    g.es(*args, **keys)

def es_print_error(*args: Any, **keys: Any) -> None:
    color = keys.get('color')
    if color is None and g.app.config:
        keys['color'] = g.app.config.getColor("log-error-color") or 'red'
    g.es_print(*args, **keys)
#@+node:ekr.20031218072017.3111: *3* g.es_event_exception
def es_event_exception(eventName: str, full: bool = False) -> None:
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
def es_exception(*args: Sequence, **kwargs: Sequence) -> None:
    """Print the last exception."""
    # val is the second argument to the raise statement.
    typ, val, tb = sys.exc_info()
    for line in traceback.format_exception(typ, val, tb):
        g.es_print_error(line)
#@+node:ekr.20061015090538: *3* g.es_exception_type
def es_exception_type(c: Cmdr = None, color: str = "red") -> None:
    # exctype is a Exception class object; value is the error message.
    exctype, value = sys.exc_info()[:2]
    g.es_print('', f"{exctype.__name__}, {value}", color=color)
#@+node:ekr.20050707064040: *3* g.es_print
# see: http://www.diveintopython.org/xml_processing/unicode.html

def es_print(*args: Any, **keys: Any) -> None:
    """
    Print all non-keyword args, and put them to the log pane.

    The first, third, fifth, etc. arg translated by g.translateString.
    Supports color, comma, newline, spaces and tabName keyword arguments.
    """
    g.pr(*args, **keys)
    if g.app and not g.unitTesting:
        g.es(*args, **keys)
#@+node:ekr.20050707065530: *3* g.es_trace
def es_trace(*args: Any, **keys: Any) -> None:
    if args:
        try:
            s = args[0]
            g.trace(g.toEncodedString(s, 'ascii'))
        except Exception:
            pass
    g.es(*args, **keys)
#@+node:ekr.20220820050145.1: *3* g.function_name
def function_name() -> str:
    """Return the name of function or method that called this function."""
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
    return name
#@+node:ekr.20230129093329.1: *3* g.get_ctor_name
def get_ctor_name(self: Any, file_name: str, width: int = 25) -> str:
    """
    Return <module-name>.<class-name>:>width.

    self: Any object.
    """
    class_name = self.__class__.__name__
    module_name = shortFileName(file_name).replace(".py", "")
    combined_name = f"{module_name}.{class_name}"
    padding = " " * max(0, 25 - len(combined_name))
    return f"{padding}{combined_name}"
#@+node:ekr.20040731204831: *3* g.getLastTracebackFileAndLineNumber
def getLastTracebackFileAndLineNumber() -> tuple[str, int]:
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
def goto_last_exception(c: Cmdr) -> None:
    """Go to the line given by sys.last_traceback."""
    typ, val, tb = sys.exc_info()
    if tb:
        file_name, line_number = g.getLastTracebackFileAndLineNumber()
        line_number = max(0, line_number - 1)  # Convert to zero-based.
        if file_name.endswith('scriptFile.py'):
            # A script.
            c.goToScriptLineNumber(line_number, c.p)
        else:
            for p in c.all_nodes():
                if p.isAnyAtFileNode() and p.h.endswith(file_name):
                    c.goToLineNumber(line_number)
                    return
    else:
        g.trace('No previous exception')
#@+node:ekr.20100126062623.6240: *3* g.internalError
def internalError(*args: Any) -> None:
    """Report a serious interal error in Leo."""
    callers = g.callers(20).split(',')
    caller = callers[-1]
    g.error('\nInternal Leo error in', caller)
    g.es_print(*args)
    g.es_print('Called from', ', '.join(callers[:-1]))
    g.es_print('Please report this error to Leo\'s developers', color='red')
#@+node:ekr.20150127060254.5: *3* g.log_to_file
def log_to_file(s: str, fn: str = None) -> None:
    """Write a message to ~/test/leo_log.txt."""
    if fn is None:
        fn = g.finalize('~/test/leo_log.txt')
    if not s.endswith('\n'):
        s = s + '\n'
    try:
        with open(fn, 'a') as f:
            f.write(s)
    except Exception:
        g.es_exception()
#@+node:ekr.20080710101653.1: *3* g.pr
# see: http://www.diveintopython.org/xml_processing/unicode.html

def pr(*args: Any, **keys: Any) -> None:
    """
    Print all non-keyword args. This is a wrapper for the print statement.

    The first, third, fifth, etc. arg translated by g.translateString.
    Supports color, comma, newline, spaces and tabName keyword arguments.
    """
    # Compute the effective args.
    d = {'commas': False, 'newline': True, 'spaces': True}
    d = doKeywordArgs(keys, d)
    newline = d.get('newline')
    # Unit tests require sys.stdout.
    stdout = sys.stdout if sys.stdout and g.unitTesting else sys.__stdout__
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
    s = translateArgs(args, d)  # Translates everything to unicode.
    s = g.toUnicode(s, encoding=encoding, reportErrors=False)
    if newline:
        s += '\n'
    # Python's print statement *can* handle unicode, but
    # sitecustomize.py must have sys.setdefaultencoding('utf-8')
    try:
        # #783: print-* commands fail under pythonw.
        stdout.write(s)
    except Exception:
        pass
#@+node:ekr.20060221083356: *3* g.prettyPrintType
def prettyPrintType(obj: Any) -> str:
    if isinstance(obj, str):
        return 'string'
    t: Any = type(obj)
    if t in (types.BuiltinFunctionType, types.FunctionType):
        return 'function'
    if t == types.ModuleType:  # noqa
        return 'module'
    if t in [types.MethodType, types.BuiltinMethodType]:
        return 'method'
    # Fall back to a hack.
    t = str(type(obj))  # type:ignore
    if t.startswith("<type '"):
        t = t[7:]
    if t.endswith("'>"):
        t = t[:-2]
    return t
#@+node:ekr.20111107181638.9741: *3* g.print_exception
def print_exception(
    full: bool = True,
    c: Cmdr = None,
    flush: bool = False,
    color: str = "red",
) -> tuple[str, int]:
    """Print exception info about the last exception."""
    # val is the second argument to the raise statement.
    typ, val, tb = sys.exc_info()
    if full:
        lines = traceback.format_exception(typ, val, tb)
    else:
        lines = traceback.format_exception_only(typ, val)
    print(''.join(lines), flush=flush)
    try:
        fileName, n = g.getLastTracebackFileAndLineNumber()
        return fileName, n
    except Exception:
        return "<no file>", 0
#@+node:ekr.20031218072017.3113: *3* g.printBindings
def print_bindings(name: str, window: Any) -> None:
    bindings = window.bind()
    g.pr("\nBindings for", name)
    for b in bindings:
        g.pr(b)
#@+node:ekr.20070510074941: *3* g.printEntireTree
def printEntireTree(c: Cmdr, tag: str = '') -> None:
    g.pr('printEntireTree', '=' * 50)
    g.pr('printEntireTree', tag, 'root', c.rootPosition())
    for p in c.all_positions():
        g.pr('..' * p.level(), p.v)
#@+node:ekr.20031218072017.3114: *3* g.printGlobals
def printGlobals(message: str = None) -> None:
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
def printLeoModules(message: str = None) -> None:
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
def printStack() -> None:
    traceback.print_stack()
#@+node:ekr.20031218072017.2317: *3* g.trace
def trace(*args: Any, **keys: Any) -> None:
    """Print the name of the calling function followed by all the args."""
    name = g._callerName(2)
    if name.endswith(".pyc"):
        name = name[:-1]
    g.pr(name, *args)
#@+node:ekr.20080220111323: *3* g.translateArgs
console_encoding = None

def translateArgs(args: Iterable[Any], d: dict[str, Any]) -> str:
    """
    Return the concatenation of s and all args, with odd args translated.
    """
    global console_encoding
    if not console_encoding:
        e = sys.getdefaultencoding()
        console_encoding = e if isValidEncoding(e) else 'utf-8'
    result: list[str] = []
    n, spaces = 0, d.get('spaces')
    for arg in args:
        n += 1
        # First, convert to unicode.
        if isinstance(arg, str):
            arg = toUnicode(arg, console_encoding)
        # Now translate.
        if not isinstance(arg, str):
            arg = repr(arg)
        elif (n % 2) == 1:
            arg = translateString(arg)
        else:
            pass  # The arg is an untranslated string.
        if arg:
            if result and spaces:
                result.append(' ')
            result.append(arg)
    return ''.join(result)
#@+node:ekr.20060810095921: *3* g.translateString & tr
def translateString(s: str) -> str:
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
def actualColor(color: str) -> str:
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
        if color2:
            return color2
        # Fall back to log_black_color.
        color2 = c.config.getColor('log-black-color')
        return color2 or 'black'
    if color == 'black':
        # Prefer log_black_color.
        color2 = c.config.getColor('log-black-color')
        if color2:
            return color2
        # Fall back to log_text_foreground_color.
        color2 = c.config.getColor('log-text-foreground-color')
        return color2 or 'black'
    color2 = c.config.getColor(f"log_{color}_color")
    return color2 or color
#@+node:ekr.20060921100435: *3* g.CheckVersion & helpers
# Simplified version by EKR: stringCompare not used.

def CheckVersion(
    s1: str,
    s2: str,
    condition: str = ">=",
    stringCompare: bool = None,
    delimiter: str = '.',
    trace: bool = False,
) -> bool:
    # CheckVersion is called early in the startup process.
    vals1 = [g.CheckVersionToInt(s) for s in s1.split(delimiter)]
    n1 = len(vals1)
    vals2 = [g.CheckVersionToInt(s) for s in s2.split(delimiter)]
    n2 = len(vals2)
    n = max(n1, n2)
    if n1 < n:
        vals1.extend([0 for _i in range(n - n1)])
    if n2 < n:
        vals2.extend([0 for _i in range(n - n2)])
    for cond, val in (
        ('==', vals1 == vals2), ('!=', vals1 != vals2),
        ('<', vals1 < vals2), ('<=', vals1 <= vals2),
        ('>', vals1 > vals2), ('>=', vals1 >= vals2),
    ):
        if condition == cond:
            result = val
            break
    else:
        raise EnvironmentError(
            "condition must be one of '>=', '>', '==', '!=', '<', or '<='.")
    return result
#@+node:ekr.20070120123930: *4* g.CheckVersionToInt
def CheckVersionToInt(s: str) -> int:
    try:
        return int(s)
    except ValueError:
        aList = []
        for ch in s:
            if ch.isdigit():
                aList.append(ch)
            else:
                break
        if aList:
            s = ''.join(aList)
            return int(s)
        return 0
#@+node:ekr.20111103205308.9657: *3* g.cls
@command('cls')
def cls(event: Event = None) -> None:
    """Clear the screen."""
    if sys.platform.lower().startswith('win'):
        os.system('cls')
#@+node:ekr.20131114124839.16665: *3* g.createScratchCommander
def createScratchCommander(fileName: str = None) -> None:
    c = g.app.newCommander(fileName)
    frame = c.frame
    frame.createFirstTreeNode()
    assert c.rootPosition()
    frame.setInitialWindowGeometry()
    frame.resizePanesToRatio(frame.ratio, frame.secondary_ratio)
#@+node:ekr.20031218072017.3126: *3* g.funcToMethod (Python Cookbook)
def funcToMethod(f: Any, theClass: Any, name: str = None) -> None:
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
init_zodb_failed: dict[str, bool] = {}  # Keys are paths, values are True.
init_zodb_db: dict[str, Any] = {}  # Keys are paths, values are ZODB.DB instances.

def init_zodb(pathToZodbStorage: str, verbose: bool = True) -> Any:
    """
    Return an ZODB.DB instance from the given path.
    return None on any error.
    """
    global init_zodb_db, init_zodb_failed, init_zodb_import_failed
    db = init_zodb_db.get(pathToZodbStorage)
    if db:
        return db
    if init_zodb_import_failed:
        return None
    failed = init_zodb_failed.get(pathToZodbStorage)
    if failed:
        return None
    try:
        import ZODB  # type:ignore
    except ImportError:
        if verbose:
            g.es('g.init_zodb: can not import ZODB')
            g.es_exception()
        init_zodb_import_failed = True
        return None
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
def input_(message: str = '', c: Cmdr = None) -> str:
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
#@+node:ekr.20110609125359.16493: *3* g.isMacOS
def isMacOS() -> bool:
    return sys.platform == 'darwin'
#@+node:ekr.20181027133311.1: *3* g.issueSecurityWarning
def issueSecurityWarning(setting: str) -> None:
    g.es('Security warning! Ignoring...', color='red')
    g.es(setting, color='red')
    g.es('This setting can be set only in')
    g.es('leoSettings.leo or myLeoSettings.leo')
#@+node:ekr.20031218072017.3144: *3* g.makeDict (Python Cookbook)
# From the Python cookbook.

def makeDict(**keys: Any) -> dict:
    """Returns a Python dictionary from using the optional keyword arguments."""
    return keys
#@+node:ekr.20140528065727.17963: *3* g.pep8_class_name
def pep8_class_name(s: str) -> str:
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
def plural(obj: Any) -> str:
    """Return "s" or "" depending on n."""
    if isinstance(obj, (list, tuple, str)):
        n = len(obj)
    else:
        n = obj
    return '' if n == 1 else 's'
#@+node:ekr.20160331194701.1: *3* g.truncate
def truncate(s: str, n: int) -> str:
    """Return s truncated to n characters."""
    if len(s) <= n:
        return s
    # Fail: weird ws.
    s2 = s[: n - 3] + f"...({len(s)})"
    if s.endswith('\n'):
        return s2 + '\n'
    return s2
#@+node:ekr.20031218072017.3150: *3* g.windows
def windows() -> Optional[list]:
    return app and app.windowList
#@+node:ekr.20031218072017.2145: ** g.os_path_ Wrappers
#@+at Note: all these methods return Unicode strings. It is up to the user to
# convert to an encoded string as needed, say when opening a file.
#@+node:ekr.20230410134119.1: *3* g.finalize
def finalize(path: str) -> str:
    """
    Finalize the path. Do not call os.path.realpath.

    - Call os.path.expanduser and  os.path.expandvars.
    - Convert to an absolute path, relative to os.getwd().
    - On Windows, convert backslashes to forward slashes.
    """
    if not path:
        return ''
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)

    # Convert to an absolute path, similar to os.path.normpath(os.getcwd(), path)
    path = os.path.abspath(path)
    path = os.path.normpath(path)

    # Convert backslashes to forward slashes, regradless of platform.
    path = g.os_path_normslashes(path)
    return path

os_path_finalize = finalize  # Compatibility.
#@+node:ekr.20230410133838.1: *3* g.finalize_join
def finalize_join(*args: Any) -> str:
    """
    Join and finalize. Do not call os.path.realpath.

    - Return an empty string if all of the args are empty.
    - Call os.path.expanduser and  os.path.expandvars for each arg.
    - Call os.path.join on the resulting list of expanded arguments.
    - Convert to an absolute path, relative to os.getwd().
    - On Windows, convert backslashes to forward slashes.
    """
    uargs = [z for z in args if z]
    if not uargs:
        return ''
    # Expand everything before joining.
    uargs2 = [os.path.expandvars(os.path.expanduser(z)) for z in uargs]

    # Join the paths.
    path = os.path.join(*uargs2)

    # Convert to an absolute path, similar to os.path.normpath(os.getcwd(), path)
    path = os.path.abspath(path)
    path = os.path.normpath(path)

    # Convert backslashes to forward slashes, regradless of platform.
    path = g.os_path_normslashes(path)
    return path

os_path_finalize_join = finalize_join  # Compatibility.
#@+node:ekr.20180314120442.1: *3* g.glob_glob
def glob_glob(pattern: str) -> list:
    """Return the regularized glob.glob(pattern)"""
    aList = glob.glob(pattern)
    # os.path.normpath does the *reverse* of what we want.
    if g.isWindows:
        aList = [z.replace('\\', '/') for z in aList]
    return aList
#@+node:ekr.20031218072017.2146: *3* g.os_path_abspath
def os_path_abspath(path: str) -> str:
    """Convert a path to an absolute path."""
    if not path:
        return ''
    path = os.path.abspath(path)
    path = g.os_path_normslashes(path)
    return path
#@+node:ekr.20031218072017.2147: *3* g.os_path_basename
def os_path_basename(path: str) -> str:
    """Return the second half of the pair returned by split(path)."""
    if not path:
        return ''
    path = os.path.basename(path)
    path = g.os_path_normslashes(path)
    return path
#@+node:ekr.20031218072017.2148: *3* g.os_path_dirname
def os_path_dirname(path: str) -> str:
    """Return the first half of the pair returned by split(path)."""
    if not path:
        return ''
    path = os.path.dirname(path)
    path = g.os_path_normslashes(path)
    return path
#@+node:ekr.20230418102243.1: *3* g.os_path_expanduser
def os_path_expanduser(path: str) -> str:
    """Wrap both os.path.expanduser and os.path.expandvars."""
    if not path:
        return ''
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)
    path = os.path.normpath(path)
    return path
#@+node:ekr.20031218072017.2149: *3* g.os_path_exists
def os_path_exists(path: str) -> bool:
    """Return True if path exists."""
    return os.path.exists(path) if path else False
#@+node:ekr.20031218072017.2150: *3* g.os_path_getmtime
def os_path_getmtime(path: str) -> float:
    """Return the modification time of path."""
    if not path:
        return 0
    try:
        return os.path.getmtime(path)
    except Exception:
        return 0
#@+node:ekr.20080729142651.2: *3* g.os_path_getsize
def os_path_getsize(path: str) -> int:
    """Return the size of path."""
    return os.path.getsize(path) if path else 0
#@+node:ekr.20031218072017.2151: *3* g.os_path_isabs
def os_path_isabs(path: str) -> bool:
    """Return True if path is an absolute path."""
    return os.path.isabs(path) if path else False
#@+node:ekr.20031218072017.2152: *3* g.os_path_isdir
def os_path_isdir(path: str) -> bool:
    """Return True if the path is a directory."""
    return os.path.isdir(path) if path else False
#@+node:ekr.20031218072017.2153: *3* g.os_path_isfile
def os_path_isfile(path: str) -> bool:
    """Return True if path is a file."""
    return os.path.isfile(path) if path else False
#@+node:ekr.20031218072017.2154: *3* g.os_path_join
def os_path_join(*args: Any, **keys: Any) -> str:
    """
    Wrap os.path.join, *without* finalizing the result.
    """
    uargs = [z for z in args if z]
    if not uargs:
        return ''
    path = os.path.join(*uargs)
    path = g.os_path_normslashes(path)
    return path

#@+node:ekr.20031218072017.2156: *3* g.os_path_normcase
def os_path_normcase(path: str) -> str:
    """Normalize the path's case."""
    if not path:
        return ''
    path = os.path.normcase(path)
    path = g.os_path_normslashes(path)
    return path

#@+node:ekr.20031218072017.2157: *3* g.os_path_normpath
def os_path_normpath(path: str) -> str:
    """Normalize the path."""
    if not path:
        return ''
    path = os.path.normpath(path)
    path = g.os_path_normslashes(path)
    return path
#@+node:ekr.20180314081254.1: *3* g.os_path_normslashes
def os_path_normslashes(path: str) -> str:
    """
    Convert backslashes to forward slashes (Windows only).

    In effect, this convert Windows paths to POSIX paths.
    """
    if not path:
        return ''
    return path.replace('\\', '/') if g.isWindows else path
#@+node:ekr.20080605064555.2: *3* g.os_path_realpath
def os_path_realpath(path: str) -> str:
    """Return the canonical path of the specified filename, eliminating any
    symbolic links encountered in the path (if they are supported by the
    operating system).
    """
    if not path:
        return ''
    path = os.path.realpath(path)
    path = g.os_path_normslashes(path)
    return path
#@+node:ekr.20031218072017.2158: *3* g.os_path_split
def os_path_split(path: str) -> tuple[str, str]:
    if not path:
        return '', ''
    head, tail = os.path.split(path)
    return head, tail
#@+node:ekr.20031218072017.2159: *3* g.os_path_splitext
def os_path_splitext(path: str) -> tuple[str, str]:

    if not path:
        return '', ''
    head, tail = os.path.splitext(path)
    return head, tail
#@+node:ekr.20090829140232.6036: *3* g.os_startfile
def os_startfile(fname: str) -> None:
    #@+others
    #@+node:bob.20170516112250.1: *4* stderr2log()
    def stderr2log(g: Any, ree: Any, fname: str) -> None:
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
    def itPoll(fname: str, ree: Any, subPopen: Any, g: Any, ito: Any) -> None:
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
        if rc is not None:
            ito.stop()
            ito.destroy_self()
            if rc != 0:
                g.es_print(f"xdg-open {fname} failed with exit code {rc}")
            stderr2log(g, ree, fname)
            ree.close()
    #@-others
    # pylint: disable=used-before-assignment
    if fname.find('"') > -1:
        quoted_fname = f"'{fname}'"
    else:
        quoted_fname = f'"{fname}"'
    if sys.platform.startswith('win'):
        # pylint: disable=no-member
        os.startfile(quoted_fname)  # Exists only on Windows.
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
            if ree:
                ree.close()
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
#@+node:ekr.20111115155710.9859: ** g.Parsing & Tokenizing
#@+node:ekr.20031218072017.822: *3* g.createTopologyList
def createTopologyList(c: Cmdr, root: Position = None, useHeadlines: bool = False) -> list:
    """Creates a list describing a node and all its descendents"""
    if not root:
        root = c.rootPosition()
    v = root
    if useHeadlines:
        aList = [(v.numberOfChildren(), v.headString()),]  # type: ignore
    else:
        aList = [v.numberOfChildren()]  # type: ignore
    child = v.firstChild()
    while child:
        aList.append(g.createTopologyList(c, child, useHeadlines))  # type: ignore
        child = child.next()
    return aList
#@+node:ekr.20111017204736.15898: *3* g.getDocString
def getDocString(s: str) -> str:
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
def getDocStringForFunction(func: Any) -> str:
    """Return the docstring for a function that creates a Leo command."""

    def name(func: Any) -> str:
        return func.__name__ if hasattr(func, '__name__') else '<no __name__>'

    def get_defaults(func: str, i: int) -> Any:
        defaults = inspect.getfullargspec(func)[3]
        return defaults[i]

    # Fix bug 1251252: https://bugs.launchpad.net/leo-editor/+bug/1251252
    # Minibuffer commands created by mod_scripting.py have no docstrings.
    # Do special cases first.

    s = ''
    if name(func) == 'minibufferCallback':
        func = get_defaults(func, 0)
        if hasattr(func, '__doc__') and func.__doc__.strip():
            s = func.__doc__
    if not s and name(func) == 'commonCommandCallback':
        script = get_defaults(func, 1)
        s = g.getDocString(script)  # Do a text scan for the function.
    # Now the general cases.  Prefer __doc__ to docstring()
    if not s and hasattr(func, '__doc__'):
        s = func.__doc__
    if not s and hasattr(func, 'docstring'):
        s = func.docstring
    return s
#@+node:ekr.20111115155710.9814: *3* g.python_tokenize (not used)
def python_tokenize(s: str) -> list:
    """
    Tokenize string s and return a list of tokens (kind, value, line_number)

    where kind is in ('comment,'id','nl','other','string','ws').
    """
    result: list[tuple[str, str, int]] = []
    i, line_number = 0, 0
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
            kind, i = 'string', g.skip_python_string(s, i)
        elif ch == '_' or ch.isalpha():
            kind, i = 'id', g.skip_id(s, i)
        else:
            kind, i = 'other', i + 1
        assert progress < i and j == progress
        val = s[j:i]
        assert val
        line_number += val.count('\n')  # A comment.
        result.append((kind, val, line_number),)
    return result
#@+node:ekr.20040327103735.2: ** g.Scripting
#@+node:ekr.20161223090721.1: *3* g.exec_file
def exec_file(path: str, d: dict[str, Any], script: str = None) -> None:
    """Simulate python's execfile statement for python 3."""
    if script is None:
        with open(path) as f:
            script = f.read()
    exec(compile(script, path, 'exec'), d)
#@+node:ekr.20131016032805.16721: *3* g.execute_shell_commands
def execute_shell_commands(commands: Any, trace: bool = False) -> None:
    """
    Execute each shell command in a separate process.
    Wait for each command to complete, except those starting with '&'
    """
    if isinstance(commands, str):
        commands = [commands]
    for command in commands:
        wait = not command.startswith('&')
        if trace:
            g.trace(command)
        if command.startswith('&'):
            command = command[1:].strip()
        proc = subprocess.Popen(command, shell=True)
        if wait:
            proc.communicate()
#@+node:ekr.20180217113719.1: *3* g.execute_shell_commands_with_options & helpers
def execute_shell_commands_with_options(
    base_dir: str = None,
    c: Cmdr = None,
    command_setting: str = None,
    commands: list = None,
    path_setting: str = None,
    trace: bool = False,
    warning: str = None,
) -> None:
    """
    A helper for prototype commands or any other code that
    runs programs in a separate process.

    base_dir:           Base directory to use if no config path given.
    commands:           A list of commands, for g.execute_shell_commands.
    commands_setting:   Name of @data setting for commands.
    path_setting:       Name of @string setting for the base directory.
    warning:            A warning to be printed before executing the commands.
    """
    base_dir = g.computeBaseDir(c, base_dir, path_setting)
    if not base_dir:
        return
    commands = g.computeCommands(c, commands, command_setting)
    if not commands:
        return
    if warning:
        g.es_print(warning)
    os.chdir(base_dir)  # Can't do this in the commands list.
    g.execute_shell_commands(commands, trace=trace)
#@+node:ekr.20180217152624.1: *4* g.computeBaseDir
def computeBaseDir(c: Cmdr, base_dir: str, path_setting: str) -> Optional[str]:
    """
    Compute a base_directory.
    If given, @string path_setting takes precedence.
    """
    # Prefer the path setting to the base_dir argument.
    if path_setting:
        if not c:
            g.es_print('@string path_setting requires valid c arg')
            return None
        # It's not an error for the setting to be empty.
        base_dir2 = c.config.getString(path_setting)
        if base_dir2:
            base_dir2 = base_dir2.replace('\\', '/')
            if g.os_path_exists(base_dir2):
                return base_dir2
            g.es_print(f"@string {path_setting} not found: {base_dir2!r}")
            return None
    # Fall back to given base_dir.
    if base_dir:
        base_dir = base_dir.replace('\\', '/')
        if g.os_path_exists(base_dir):
            return base_dir
        g.es_print(f"base_dir not found: {base_dir!r}")
        return None
    g.es_print(f"Please use @string {path_setting}")
    return None
#@+node:ekr.20180217153459.1: *4* g.computeCommands
def computeCommands(c: Cmdr, commands: list[str], command_setting: str) -> list[str]:
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
def executeFile(filename: str, options: str = '') -> None:
    if not os.access(filename, os.R_OK):
        return
    fdir, fname = g.os_path_split(filename)
    # New in Leo 4.10: alway use subprocess.

    def subprocess_wrapper(cmdlst: str) -> tuple:

        p = subprocess.Popen(cmdlst, cwd=fdir,
            universal_newlines=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdo, stde = p.communicate()
        return p.wait(), stdo, stde

    rc, so, se = subprocess_wrapper(f"{sys.executable} {fname} {options}")
    if rc:
        g.pr('return code', rc)
    g.pr(so, se)
#@+node:ekr.20040321065415: *3* g.find*Node*
#@+others
#@+node:ekr.20210303123423.3: *4* g.findNodeAnywhere
def findNodeAnywhere(c: Cmdr, headline: str, exact: bool = True) -> Optional[Position]:
    h = headline.strip()
    for p in c.all_unique_positions(copy=False):
        if p.h.strip() == h:
            return p.copy()
    if not exact:
        for p in c.all_unique_positions(copy=False):
            if p.h.strip().startswith(h):
                return p.copy()
    return None
#@+node:ekr.20210303123525.1: *4* g.findNodeByPath
def findNodeByPath(c: Cmdr, path: str) -> Optional[Position]:
    """Return the first @<file> node in Cmdr c whose path is given."""
    if not os.path.isabs(path):  # #2049. Only absolute paths could possibly work.
        g.trace(f"path not absolute: {repr(path)}")
        return None
    path = g.os_path_normpath(path)  # #2049. Do *not* use os.path.normpath.
    for p in c.all_positions():
        if p.isAnyAtFileNode():
            # #2049. Do *not* use os.path.normpath.
            if path == g.os_path_normpath(c.fullPath(p)):
                return p
    return None
#@+node:ekr.20210303123423.1: *4* g.findNodeInChildren
def findNodeInChildren(c: Cmdr, p: Position, headline: str, exact: bool = True) -> Optional[Position]:
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
#@+node:ekr.20210303123423.2: *4* g.findNodeInTree
def findNodeInTree(c: Cmdr, p: Position, headline: str, exact: bool = True) -> Optional[Position]:
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
#@+node:ekr.20210303123423.4: *4* g.findTopLevelNode
def findTopLevelNode(c: Cmdr, headline: str, exact: bool = True) -> Optional[Position]:
    h = headline.strip()
    for p in c.rootPosition().self_and_siblings(copy=False):
        if p.h.strip() == h:
            return p.copy()
    if not exact:
        for p in c.rootPosition().self_and_siblings(copy=False):
            if p.h.strip().startswith(h):
                return p.copy()
    return None
#@-others
#@+node:EKR.20040614071102.1: *3* g.getScript & helpers
def getScript(
    c: Cmdr,
    p: Position,
    useSelectedText: bool = True,
    forcePythonSentinels: bool = True,
    useSentinels: bool = True,
) -> str:
    """
    Return the expansion of the selected text of node p.
    Return the expansion of all of node p's body text if
    p is not the current node or if there is no text selection.
    """
    w = c.frame.body.wrapper
    if not p:
        p = c.p
    try:
        if g.app.inBridge:
            s = p.b
        elif w and p == c.p and useSelectedText and w.hasSelection():
            s = w.getSelectedText()
        else:
            s = p.b
        # Remove extra leading whitespace so the user may execute indented code.
        s = textwrap.dedent(s)
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
def composeScript(
    c: Cmdr,
    p: Position,
    s: str,
    forcePythonSentinels: bool = True,
    useSentinels: bool = True,
) -> str:
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
        # Important, the script is an **encoded string**, not a unicode string.
        script = script.replace("\r\n", "\n")  # Use brute force.
        g.app.scriptDict["script2"] = script
    finally:
        g.app.inScript = g.inScript = old_in_script
    return script
#@+node:ekr.20170123074946.1: *4* g.extractExecutableString
def extractExecutableString(c: Cmdr, p: Position, s: str) -> str:
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
    for line in g.splitLines(s):
        m = re.match(pattern, line)
        if m:
            extracting = m.group(1) == language
        elif extracting:
            result.append(line)
    return ''.join(result)
#@+node:ekr.20060624085200: *3* g.handleScriptException
def handleScriptException(
    c: Cmdr,
    p: Position,
    script: str = None,  # No longer used.
    script1: str = None,  # No longer used.
) -> None:
    g.warning("exception executing script")
    g.es_exception()

    # Careful: this test is no longer guaranteed.
    if p.v.context != c:
        return
    fileName, n = g.getLastTracebackFileAndLineNumber()
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
def insertCodingLine(encoding: str, script: str) -> str:
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
#@+node:ekr.20210901071523.1: *3* g.run_coverage_tests
def run_coverage_tests(module: str = '', filename: str = '') -> None:
    """
    Run the coverage tests given by the module and filename strings.
    """
    unittests_dir = g.finalize_join(g.app.loadDir, '..', 'unittests')
    assert os.path.exists(unittests_dir)
    os.chdir(unittests_dir)
    prefix = r"python -m pytest --cov-report html --cov-report term-missing --cov "
    command = f"{prefix} {module} {filename}"
    g.execute_shell_commands(command)
#@+node:ekr.20210901065224.1: *3* g.run_unit_tests
def run_unit_tests(tests: str = None, verbose: bool = False) -> None:
    """
    Run the unit tests given by the "tests" string.

    Run *all* unit tests if "tests" is not given.
    """
    if 'site-packages' in __file__:
        # Add site-packages to sys.path.
        parent_dir = os.path.normpath(os.path.join(g.app.loadDir, '..', '..'))
        if parent_dir.endswith('site-packages'):
            if parent_dir not in sys.path:
                g.trace(f"Append {parent_dir!r} to sys.path")
                sys.path.insert(0, parent_dir)
        else:
            g.trace('Can not happen: wrong parent directory', parent_dir)
            return
        # Run tests in site-packages/leo
        os.chdir(os.path.normpath(os.path.join(g.app.loadDir, '..')))
    else:
        # Run tests in leo-editor.
        os.chdir(os.path.normpath(os.path.join(g.app.loadDir, '..', '..')))
    verbosity = '-v' if verbose else ''
    command = f"{sys.executable} -m unittest {verbosity} {tests or ''} "
    g.execute_shell_commands(command)
#@+node:ekr.20120311151914.9916: ** g.Urls & UNLs
#@+<< About clickable links >>
#@+node:ekr.20230624100622.1: *3* << About clickable links >>
#@@language rest
#@@wrap
#@+at
# Clickable links have four forms:
#
# 1. Error messages produced by flake8, mypy, pyflakes, pylint, python:
#
#    Some of these tools produce clickable links in the log pane when run
#    *within* Leo. Some do not.
#
#    When running these tools *outside of* Leo, copying an error message from
#    the *console* to Leo's log pane will create clickable links in the log
#    pane. Control-clicking these links will select the proper node and line
#    provided the outline contains an `@<file>` node for file mentioned in
#    the error message.
#
# 2. New in Leo 6.7.4: UNLs based on gnx's (global node indices):
#
#    Links of the form `unl:gnx:` + `//{outline}#{gnx}` open the given
#    outline and select the first outline node with the given gnx. These UNLs
#    will work as long as the node exists anywhere in the outline.
#
#    For example, the link: `unl:gnx://#ekr.20031218072017.2406` refers to this
#    outline's "Code" node. Try it. The link works in this outline.
#
#    *Note*: `{outline}` is optional. It can be an absolute path name or a relative
#    path name resolved using `@data unl-path-prefixes`.
#
# 3. Leo's headline-based UNLs, as shown in the status pane:
#
#    Headline-based UNLs consist of `unl://` + `//{outline}#{headline_list}`
#    where headline_list is list of headlines separated by `-->`.
#
#    This link works: `unl://#Code-->About this file`.
#
#    *Note*: `{outline}` is optional. It can be an absolute path name or a relative
#    path name resolved using `@data unl-path-prefixes`.
#
# 4. Web URLs: file, ftp, gopher, http, https, mailto, news, nntp, prospero, telnet, wais.
#
#    For example, Leo's forum: https://leo-editor.github.io/leo-editor/
#@-<< About clickable links >>
#@+node:ekr.20120320053907.9776: *3* g.computeFileUrl
def computeFileUrl(fn: str, c: Cmdr = None, p: Position = None) -> str:
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
        path = g.finalize(path)
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
        # Handle ancestor @path directives.
        if c and c.openDirectory:
            base = c.getNodePath(p)
            path = g.finalize_join(c.openDirectory, base, path)
        else:
            path = g.finalize(path)
        url = f"{tag}{path}"
    return url
#@+node:ekr.20190608090856.1: *3* g.es_clickable_link (not used)
def es_clickable_link(c: Cmdr, p: Position, line_number: int, message: str) -> None:  # pragma: no cover
    """
    Write a clickable message to the given line number of p.b.

    Negative line numbers indicate global lines.

    """
    # Not used in Leo's core.
    unl = p.get_UNL()
    c.frame.log.put(message.strip() + '\n', nodeLink=f"{unl}::{line_number}")
#@+node:ekr.20230628072620.1: *3* g.findAnyUnl
def findAnyUnl(unl_s: str, c: Cmdr) -> Optional[Position]:
    """
    Find the Position corresponding to an UNL.

    The UNL may be either a legacy (path-based) or new (gnx-based) unl.
    """
    unl = unl_s
    if unl.startswith('unl:gnx:'):
        # Resolve a gnx-based unl.
        unl = unl[8:]
        file_part = g.getUNLFilePart(unl)
        c2 = g.openUNLFile(c, file_part)
        if not c2:
            return None
        tail = unl[3 + len(file_part) :]  # 3: Skip the '//' and '#'
        return g.findGnx(tail, c2)
    # Resolve a file-based unl.
    for prefix in ('unl:', 'file:'):
        if unl.startswith(prefix):
            unl = unl[len(prefix) :]
            break
    else:
        print(f"Bad unl: {unl_s}")
        return None
    file_part = g.getUNLFilePart(unl)
    c2 = g.openUNLFile(c, file_part)
    if not c2:
        return None
    tail = unl[3 + len(file_part) :]  # 3: Skip the '//' and '#'
    unlList = tail.split('-->')
    return g.findUnl(unlList, c2)
#@+node:ekr.20230624015529.1: *3* g.findGnx (new unls)
find_gnx_pat = re.compile(r'^(.*)::([-\d]+)?$')

def findGnx(gnx: str, c: Cmdr) -> Optional[Position]:
    """
    gnx: the gnx part of a gnx-based unl.

    The gnx part may be the actual gnx or <actual-gnx>::<line-number>

    Return the first position in c with the actual gnx.
    """
    # Get the actual gnx and line number.
    n: int = 0  # The line number.
    m = find_gnx_pat.match(gnx)
    if m:
        # Get the actual gnx and line number.
        gnx = m.group(1)
        try:
            n = int(m.group(2))
        except(TypeError, ValueError):
            pass
    for p in c.all_unique_positions():
        if p.gnx == gnx:
            if n is None:
                return p
            p2, offset = c.gotoCommands.find_file_line(-n, p)
            return p2 or p
    return None
#@+node:tbrown.20140311095634.15188: *3* g.findUnl & helpers (legacy unls)
def findUnl(unlList1: list[str], c: Cmdr) -> Optional[Position]:
    """
    g.findUnl: support for legacy UNLs.
    unlList is a list of headlines.

    This method must remain for compatibility with plugins.

    Find and move to the unl given by the unlList in the commander c.
    Return the found position, or None.
    """
    # Define two *optional* unl patterns.

    # old_pat: ':' followed by a list of node indices.
    #          Deprecated and probably does not work.
    #          This pattern will remain for compatibility.
    old_pat = re.compile(r'^(.*):(\d+),?(\d+)?,?([-\d]+)?,?(\d+)?$')

    # new_pat: '::' followed by a line number.
    #          Negative line numbers denote global line numbers.
    new_pat = re.compile(r'^(.*?)(::)([-\d]+)?$')

    #@+others  # Define helper functions
    #@+node:ekr.20230626064652.2: *4* function: convert_unl_list
    def convert_unl_list(aList: list[str]) -> list[str]:
        """
        Convert old-style UNLs to new UNLs, retaining line numbers if possible.
        """
        result = []
        for s in aList:
            # Try to get the line number.
            for m, line_group in (
                (old_pat.match(s), 4),
                (new_pat.match(s), 3),
            ):
                if m:
                    try:
                        n = int(m.group(line_group))
                        result.append(f"{m.group(1)}::{n}")
                        continue
                    except Exception:
                        pass
            # Finally, just add the whole UNL.
            result.append(s)
        # Do *not* remove duplicates!
        return result
    #@+node:ekr.20230626064652.3: *4* function: full_match
    def full_match(p: Position) -> bool:
        """Return True if the stripped headlines of p and all p's parents match unlList."""
        # Careful: make copies.
        aList: list[str] = unlList[:]
        p1 = p.copy()
        while aList and p1:
            m = new_pat.match(aList[-1])
            if m and m.group(1).strip() != p1.h.strip():
                return False
            if not m and aList[-1].strip() != p1.h.strip():
                return False
            aList.pop()
            p1.moveToParent()
        return not aList
    #@-others

    unlList = convert_unl_list(unlList1)
    if not unlList:
        return None
    # Find all target headlines.
    targets = []
    m = new_pat.match(unlList[-1])
    target = m and m.group(1) or unlList[-1]
    targets.append(target.strip())
    targets.extend(unlList[:-1])
    # Find all target positions. Prefer later positions.
    positions = list(reversed(list(z for z in c.all_positions() if z.h.strip() in targets)))
    while unlList:
        for p in positions:
            p1 = p.copy()
            if full_match(p):
                assert p == p1, (p, p1)
                n = 0  # The default line number.
                # Parse the last target.
                m = new_pat.match(unlList[-1])
                if m:
                    line = m.group(3)
                    try:
                        n = int(line)
                    except(TypeError, ValueError):
                        g.trace('bad line number', line)
                if n < 0:
                    p2, offset = c.gotoCommands.find_file_line(-n, p)  # Calls c.redraw().
                    if not p2:
                        g.trace(f"{p.h}: global line {n} not found")
                return p
        # Not found. Pop the first parent from unlList.
        unlList.pop(0)
    return None

findUNL = findUnl  # Compatibility.
#@+node:ekr.20120311151914.9917: *3* g.getUrlFromNode
def getUrlFromNode(p: Position) -> Optional[str]:
    """
    Get an url from node p:
    1. Use the headline if it contains a valid url.
    2. Otherwise, look *only* at the first line of the body.
    """
    if not p:
        return None
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
#@+node:ekr.20170221063527.1: *3* g.handleUnl
def handleUnl(unl_s: str, c: Cmdr) -> Optional[Cmdr]:
    """
    Select the node given by any kind of unl.
    This must *never* open a browser.
    """
    if not unl_s:
        return None
    unl = unl_s.strip()
    if not unl:
        return None
    p = g.findAnyUnl(unl, c)
    if not p:
        print(f"Not found: {unl!r}")
        return None
    # Do not assume that p is in c.
    c2 = p.v.context
    if c2 != c:
        g.app.selectLeoWindow(c2)  # Switch outlines.
    c2.redraw(p)
    return c2
#@+node:tbrown.20090219095555.63: *3* g.handleUrl & helpers
def handleUrl(url: str, c: Cmdr = None, p: Position = None) -> Any:
    """Open a url or a unl."""
    if c and not p:
        p = c.p
    # These two special cases should match the hacks in jedit.match_any_url.
    if url.endswith('.'):
        url = url[:-1]
    if '(' not in url and url.endswith(')'):
        url = url[:-1]
    # Lower the url.
    urll = url.lower()
    if urll.startswith('@url'):
        url = url[4:].lstrip()
    if (
        urll.startswith(('#', 'unl://', 'unl:gnx:')) or
        urll.startswith('file://') and '-->' in urll
    ):
        return g.handleUnl(url, c)
    try:
        g.handleUrlHelper(url, c, p)
        return urll  # For unit tests.
    except Exception:
        g.es_print("g.handleUrl: exception opening", repr(url))
        g.es_exception()
        return None
#@+node:ekr.20170226054459.1: *4* g.handleUrlHelper
def handleUrlHelper(url: str, c: Cmdr, p: Position) -> None:  # pragma: no cover
    """Open a url.  Most browsers should handle:
        ftp://ftp.uu.net/public/whatever
        http://localhost/MySiteUnderDevelopment/index.html
        file:///home/me/todolist.html
    """
    if g.unitTesting:
        return
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
    if leo_path.endswith('\\'):
        leo_path = leo_path[:-1]
    if leo_path.endswith('/'):
        leo_path = leo_path[:-1]
    if parsed.scheme == 'file' and leo_path.endswith('.leo'):
        g.handleUnl(original_url, c)
    elif parsed.scheme in ('', 'file'):
        unquote_path = g.unquoteUrl(leo_path)
        if g.os_path_exists(leo_path):
            g.os_startfile(unquote_path)
        else:
            g.es(f"File '{leo_path}' does not exist")
    else:
        # Mozilla throws a weird exception, then opens the file!
        try:
            webbrowser.open(url)
        except Exception:
            pass
#@+node:ekr.20170226060816.1: *4* g.traceUrl
def traceUrl(c: Cmdr, path: str, parsed: Any, url: str) -> None:  # pragma: no cover

    print()
    g.trace('url          ', url)
    g.trace('c.frame.title', c.frame.title)
    g.trace('path         ', path)
    g.trace('parsed.fragment', parsed.fragment)
    g.trace('parsed.netloc', parsed.netloc)
    g.trace('parsed.path  ', parsed.path)
    g.trace('parsed.scheme', repr(parsed.scheme))
#@+node:ekr.20230628072109.1: *3* g.isValidUnl
# unls must contain a (possible empty) file part followed by something else.
valid_unl_pattern = re.compile(r"(unl:gnx|unl|file)://(.*?)#.+")

def isValidUnl(unl_s: str) -> bool:
    """Return true if the given unl is valid."""
    return bool(valid_unl_pattern.match(unl_s))
#@+node:ekr.20120311151914.9918: *3* g.isValidUrl
def isValidUrl(url: str) -> bool:
    """Return true if url *looks* like a valid url."""
    table = (
        'file', 'ftp', 'gopher', 'hdl', 'http', 'https', 'imap',
        'mailto', 'mms', 'news', 'nntp', 'prospero', 'rsync', 'rtsp', 'rtspu',
        'sftp', 'shttp', 'sip', 'sips', 'snews', 'svn', 'svn+ssh', 'telnet', 'wais',
    )
    if not url:
        return False  # pragma: no cover (defensive)
    if g.isValidUnl(url):
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
def openUrl(p: Position) -> None:  # pragma: no cover
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
def openUrlOnClick(event: Any, url: str = None) -> Optional[str]:  # pragma: no cover
    """Open the URL under the cursor.  Return it for unit testing."""
    # QTextEditWrapper.mouseReleaseEvent calls this outside Leo's command logic.
    # Make sure to catch all exceptions!
    try:
        return openUrlHelper(event, url)
    except Exception:
        g.es_exception()
        return None
#@+node:ekr.20170216091704.1: *4* g.openUrlHelper
def openUrlHelper(event: Any, url: str = None) -> Optional[str]:
    """Open the unl, url or gnx under the cursor.  Return it for unit testing."""
    c = getattr(event, 'c', None)
    if not c:
        return None
    w = getattr(event, 'w', c.frame.body.wrapper)
    if not g.app.gui.isTextWrapper(w):
        g.internalError('must be a text wrapper', w)
        return None
    if event:
        event.widget = w
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
        # Order is important.
        #@+<< look for section ref >>
        #@+node:tom.20220328141455.1: *5* << look for section ref >>
        # Navigate to section reference if one was clicked.
        l_ = line.strip()
        if l_.endswith('>>') and l_.startswith('<<'):
            p = c.p
            px = None
            for p1 in p.subtree():
                if p1.h.strip() == l_:
                    px = p1
                    break
            if px:
                c.selectPosition(px)
                c.redraw()
            return None
        #@-<< look for section ref >>
        url = unl = None
        #@+<< look for url >>
        #@+node:tom.20220328141544.1: *5* << look for url  >>
        # Find the url on the line.
        for match in g.url_regex.finditer(line):
            # Don't open if we click after the url.
            if match.start() <= col < match.end():
                url = match.group(0)
                if g.isValidUrl(url):
                    break
        #@-<< look for url >>
        if not url:
            #@+<< look for unl >>
            #@+node:ekr.20220704211851.1: *5* << look for unl >>
            for match in g.unl_regex.finditer(line):
                # Don't open if we click after the unl.
                if match.start() <= col < match.end():
                    unl = match.group()
                    g.handleUnl(unl, c)
                    return None
            #@-<< look for unl >>
            if not unl:
                #@+<< look for gnx >>
                #@+node:tom.20220328142302.1: *5* << look for gnx >>
                target = None
                for match in gnx_regex.finditer(line):
                    # Don't open if we click after the gnx.
                    if match.start() <= col < match.end():
                        target = match.group(0)[4:]  # Strip the leading 'gnx:'
                        break

                if target:
                    found_gnx = False
                    if c.p.gnx == target:
                        return target
                    for p in c.all_unique_positions():
                        if p.v.gnx == target:
                            found_gnx = True
                            break
                    if found_gnx:
                        c.selectPosition(p)
                        c.redraw()
                    return target
                #@-<< look for gnx >>
    elif not isinstance(url, str):
        url = url.toString()
        url = g.toUnicode(url)  # #571
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
    if not word:
        return None
    p, pos, newpos = c.findCommands.find_def(event)
    if p:
        return None
    #@+<< look for filename or import>>
    #@+node:tom.20230130102836.1: *5* << look for filename or import >>
    # Part 4: #2546: look for a file name.
    s = w.getAllText()
    i, j = w.getSelectionRange()
    m = re.match(r'(\w+)\.(\w){1,4}\b', s[i:])
    filename, filename_w = '', ''
    if m:
        filename = m.group(0)
    # Part 5: #3112: look for import statement
    else:
        FROMre = r'^from [\./\\]*([^\s/\\].+)\s+import'
        IMPORTre = r'^import\s+[\./\\]*([^\s/\\].+)'
        IMPORTSre = FROMre + '|' + IMPORTre

        m = re.match(IMPORTSre, s[i:], re.MULTILINE)
        module = m and (m[2] or m[1])
        if module:
            filename = module + '.py'
            filename_w = module + '.pyw'

    if filename:
        # Navigate to the first node whose headline ends with the filename.
        effective_filename = ''
        for p in c.all_unique_positions():
            headline = p.h.strip()
            if headline.endswith(filename):
                effective_filename = filename
            elif filename_w and headline.endswith(filename_w):
                effective_filename = filename_w
            if effective_filename:
                # Set the find text.
                c.findCommands.ftm.set_find_text(effective_filename)
                # Select.
                c.redraw(p)
                break
    #@-<< look for filename or import>>
    return None
#@+node:ekr.20170226093349.1: *3* g.unquoteUrl
def unquoteUrl(url: str) -> str:  # pragma: no cover
    """Replace escaped characters (especially %20, by their equivalent)."""
    return urllib.parse.unquote(url)
#@+node:ekr.20230627143007.1: *3* g: file part utils

#@+node:ekr.20230630132339.1: *4* g.getUNLFilePart
file_part_pattern = re.compile(r'//(.*?)#.+')

def getUNLFilePart(s: str) -> str:
    """Return the file part of a unl, that is, everything *between* '//' and '#'."""
    # Strip the prefix if it exists.
    for prefix in ('unl:gnx:', 'unl:', 'file:'):
        if s.startswith(prefix):
            s = s[len(prefix) :]
            break
    m = file_part_pattern.match(s)
    return m.group(1) if m else ''
#@+node:ekr.20230630132340.1: *4* g.openUNLFile
def openUNLFile(c: Cmdr, s: str) -> Cmdr:
    """
    Open the commander for filename s, the file part of an unl.

    Return None if the file can not be found.
    """
    base = os.path.basename
    norm = os.path.normpath
    c_name = c.fileName()

    def standard(path: str) -> str:
        """Standardize the path for easy comparison."""
        return norm(path).lower()

    if not s.strip():
        return None
    if s.startswith('//') and s.endswith('#'):
        s = s[2:-1]
    if not s.strip():
        return None
    # Always match within the present file.
    if os.path.isabs(s) and standard(s) == standard(c_name):
        return c
    if not os.path.isabs(s) and standard(s) == standard(base(c_name)):
        return c
    if os.path.isabs(s):
        path = standard(s)
    else:
        # Values of d should be directories.
        d = g.parsePathData(c)
        base_s = base(s)
        directory = d.get(base_s)
        if not directory:
            return None
        if not os.path.exists(directory):
            return None
        path = standard(os.path.join(directory, base_s))
    if path == standard(c_name):
        return c
    # Search all open commanders.
    # This is a good shortcut, and it helps unit tests.
    for c2 in g.app.commanders():
        if path == standard(c2.fileName()):
            return c2
    # Open the file if possible.
    if not os.path.exists(path):
        return None
    return g.openWithFileName(path)
#@+node:ekr.20230630132341.1: *4* g.parsePathData
path_data_pattern = re.compile(r'(.+?):\s*(.+)')

def parsePathData(c: Cmdr) -> dict[str, str]:
    """
    Return a dict giving path prefixes for the files given in @data
    unl-path-prefixes.
    """
    lines = c.config.getData('unl-path-prefixes')
    d: dict[str, str] = {}
    for line in lines:
        m = path_data_pattern.match(line)
        if m:
            key, path = m.group(1), m.group(2)
            if key in d:
                g.trace(f"Ignoring duplicate key: {line!r}")  # pragma: no cover
            else:
                d[key] = os.path.normpath(path)
        else:
            g.trace(f"Ignoring line: {line!r}")  # pragma: no cover
    return d
#@-others
# set g when the import is about to complete.
g = sys.modules.get('leo.core.leoGlobals')
assert g, sorted(sys.modules.keys())
if __name__ == '__main__':
    unittest.main()  # pragma: no cover

#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
