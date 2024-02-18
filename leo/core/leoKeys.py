#@+leo-ver=5-thin
#@+node:ekr.20061031131434: * @file leoKeys.py
"""Gui-independent keystroke handling for Leo."""
# pylint: disable=eval-used
# pylint: disable=deprecated-method
#@+<< leoKeys imports >>
#@+node:ekr.20061031131434.1: ** << leoKeys imports >>
from __future__ import annotations
from collections.abc import Callable
import inspect
import os
import re
import string
import sys
import textwrap
import time
from typing import Any, Optional, TYPE_CHECKING
from leo.core import leoGlobals as g
from leo.commands import gotoCommands
from leo.external import codewise
try:
    import jedi
except ImportError:
    jedi = None
#@-<< leoKeys imports >>
#@+<< leoKeys annotations >>
#@+node:ekr.20220414165644.1: ** << leoKeys annotations >>
if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position
    from leo.plugins.qt_text import QTextEditWrapper as Wrapper
    Event = Any  # Several kinds of events?
    Stroke = Any
#@-<< leoKeys annotations >>
#@+<< Key bindings, an overview >>
#@+node:ekr.20130920121326.11281: ** << Key bindings, an overview >>
#@@language rest
#@+at
# The big pictures of key bindings:
#
# 1. Code in leoKeys.py and in leoConfig.py converts user key settings to
#    various Python **binding dictionaries** defined in leoKeys.py.
#
# 2. An instance of LeoQtEventFilter should be attached to all visible panes
#    in Leo's main window. g.app.gui.setFilter does this.
#
# 3. LeoQtEventFilter.eventFilter calls k.masterKeyhandler for every
#    keystroke. eventFilter passes only just the event argument to
#    k.masterKeyHandler. The event arg gives both the widget in which the
#    event occurs and the keystroke.
#
# 4. k.masterKeyHandler and its helpers use the event argument and the
#    binding dictionaries to execute the Leo command (if any) associated with
#    the incoming keystroke.
#
# Important details:
#
# 1. g.app.gui.setFilter allows various traces and assertions to be made
#    uniformly. The obj argument to setFilter is a QWidget object; the w
#    argument to setFilter can be either the same as obj, or a Leo
#    wrapper class. **Important**: the types of obj and w are not
#    actually all that important, as discussed next.
#
# 2. The logic in k.masterKeyHandler and its helpers is long and involved:
#
# A. k.getPaneBinding associates a command with the incoming keystroke based
#    on a) the widget's name and b) whether the widget is a text widget
#    (which depends on the type of the widget).
#
#    To do this, k.getPaneBinding uses a **binding priority table**. This
#    table is defined within k.getPaneBinding itself. The table indicates
#    which of several possible bindings should have priority. For instance,
#    if the widget is a text widget, a user binding for a 'text' widget takes
#    priority over a default key binding. Similarly, if the widget is Leo's
#    tree widget, a 'tree' binding has top priority. There are many other
#    details encapsulated in the table. The exactly details of the binding
#    priority table are open to debate, but in practice the resulting
#    bindings are as expected.
#
# B. If k.getPaneBinding finds a command associated with the incoming
#    keystroke, k.masterKeyHandler executes the command.
#
# C. If k.getPaneBinding fails to bind the incoming keystroke to a command,
#    k.masterKeyHandler calls k.handleUnboundKeys to handle the keystroke.
#    Depending on the widget, and settings, and the keystroke,
#    k.handleUnboundKeys may do nothing, or it may call k.masterCommand to
#    insert a plain key into the widget.
#@-<< Key bindings, an overview >>
#@+<< about 'internal' bindings >>
#@+node:ekr.20061031131434.2: ** << about 'internal' bindings >>
#@@language rest
#@+at
# Here are the rules for translating key bindings (in leoSettings.leo)
# into keys for k.bindingsDict:
#
# 1. The case of plain letters is significant: a is not A.
#
# 2. The Shift- prefix can be applied *only* to letters. Leo will ignore
#    (with a warning) the shift prefix applied to any other binding,
#    e.g., Ctrl-Shift-(
#
# 3. The case of letters prefixed by Ctrl-, Alt-, Key- or Shift- is
#    *not* significant. Thus, the Shift- prefix is required if you want
#    an upper-case letter (with the exception of 'bare' uppercase
#    letters.)
#
# The following table illustrates these rules. In each row, the first
# entry is the key (for k.bindingsDict) and the other entries are
# equivalents that the user may specify in leoSettings.leo:
#
# a, Key-a, Key-A
# A, Shift-A
# Alt-a, Alt-A
# Alt-A, Alt-Shift-a, Alt-Shift-A
# Ctrl-a, Ctrl-A
# Ctrl-A, Ctrl-Shift-a, Ctrl-Shift-A
# , Key-!,Key-exclam,exclam
#
# This table is consistent with how Leo already works (because it is
# consistent with Tk's key-event specifiers). It is also, I think, the
# least confusing set of rules.
#@-<< about 'internal' bindings >>
#@+<< about key dicts >>
#@+node:ekr.20061031131434.3: ** << about key dicts >>
#@@language rest
#@+at
# ivar                    Keys                Values
# ----                    ----                ------
# c.commandsDict          command names (1)   functions
# k.bindingsDict          shortcuts           lists of BindingInfo objects
# k.masterBindingsDict    scope names (2)     Interior masterBindingDicts (3)
# k.masterGuiBindingsDict strokes             list of widgets in which stroke is bound
# inverseBindingDict (5)  command names       lists of tuples (pane,key)
# modeCommandsDict (6)    command name (7)    inner modeCommandsDicts (8)
#
# New in Leo 4.7:
# k.killedBindings is a list of command names for which bindings have been killed in local files.
#
# Notes:
#
# (1) Command names are minibuffer names (strings)
# (2) Scope names are 'all','text',etc.
# (3) Interior masterBindingDicts: Keys are strokes; values are BindingInfo objects.
# (5) inverseBindingDict is **not** an ivar: it is computed by k.computeInverseBindingDict.
# (6) A global dict: g.app.gui.modeCommandsDict
# (7) enter-x-command
# (8) Keys are command names, values are lists of BindingInfo objects.
#@-<< about key dicts >>
#@+others
#@+node:ekr.20150509035140.1: ** ac_cmd (decorator)
def ac_cmd(name: str) -> Callable:
    """Command decorator for the AutoCompleter class."""
    return g.new_cmd_decorator(name, ['c', 'k', 'autoCompleter'])
#@+node:ekr.20150509035028.1: ** cmd (decorator)
def cmd(name: str) -> Callable:
    """Command decorator for the leoKeys class."""
    return g.new_cmd_decorator(name, ['c', 'k',])
#@+node:ekr.20061031131434.4: ** class AutoCompleterClass
class AutoCompleterClass:
    """A class that inserts autocompleted and calltip text in text widgets.
    This class shows alternatives in the tabbed log pane.

    The keyHandler class contains hooks to support these characters:
    invoke-autocompleter-character (default binding is '.')
    invoke-calltips-character (default binding is '(')
    """
    #@+others
    #@+node:ekr.20061031131434.5: *3* ac.ctor & reloadSettings
    def __init__(self, k: Any) -> None:
        """Ctor for AutoCompleterClass class."""
        # Ivars...
        self.c = k.c
        self.k = k
        self.language: str = ''
        # additional namespaces to search for objects, other code
        # can append namespaces to this to extend scope of search
        self.namespaces: list[dict] = []
        self.qw = None  # The object that supports qcompletion methods.
        self.tabName: str = None  # The name of the main completion tab.
        self.verbose = False  # True: print all members, regardless of how many there are.
        self.w = None  # The widget that gets focus after autocomplete is done.
        self.warnings: dict[str, str] = {}  # Keys are language names.
        # Codewise pre-computes...
        self.codewiseSelfList: list[str] = []  # The (global) completions for "self."
        self.completionsDict: dict[str, list[str]] = {}  # Keys are prefixes, values are completion lists.
        self.reloadSettings()

    def reloadSettings(self) -> None:
        c = self.c
        self.auto_tab = c.config.getBool('auto-tab-complete', True)
        self.forbid_invalid = c.config.getBool('forbid-invalid-completions', False)
        self.use_jedi = c.config.getBool('use-jedi', False)
        # True: show results in autocompleter tab.
        # False: show results in a QCompleter widget.
        self.use_qcompleter = c.config.getBool('use-qcompleter', False)
    #@+node:ekr.20061031131434.8: *3* ac.Top level
    #@+node:ekr.20061031131434.9: *4* ac.autoComplete
    @ac_cmd('auto-complete')
    def autoComplete(self, event: Event = None) -> None:
        """An event handler for autocompletion."""
        c, k = self.c, self.k
        # pylint: disable=consider-using-ternary
        w = event and event.w or c.get_focus()
        if k.unboundKeyAction not in ('insert', 'overwrite'):
            return
        c.insertCharFromEvent(event)
        if c.exists:
            c.frame.updateStatusLine()
        # Allow autocompletion only in the body pane.
        if not c.widget_name(w).lower().startswith('body'):
            return
        self.language = g.scanForAtLanguage(c, c.p)
        if w and k.enable_autocompleter:
            self.w = w
            self.start(event)
    #@+node:ekr.20061031131434.10: *4* ac.autoCompleteForce
    @ac_cmd('auto-complete-force')
    def autoCompleteForce(self, event: Event = None) -> None:
        """Show autocompletion, even if autocompletion is not presently enabled."""
        c, k = self.c, self.k
        # pylint: disable=consider-using-ternary
        w = event and event.w or c.get_focus()
        if k.unboundKeyAction not in ('insert', 'overwrite'):
            return
        if c.exists:
            c.frame.updateStatusLine()
        # Allow autocompletion only in the body pane.
        if not c.widget_name(w).lower().startswith('body'):
            return
        self.language = g.scanForAtLanguage(c, c.p)
        if w:
            self.w = w
            self.start(event)

    #@+node:ekr.20061031131434.12: *4* ac.enable/disable/toggleAutocompleter/Calltips
    @ac_cmd('disable-autocompleter')
    def disableAutocompleter(self, event: Event = None) -> None:
        """Disable the autocompleter."""
        self.k.enable_autocompleter = False
        self.showAutocompleterStatus()

    @ac_cmd('disable-calltips')
    def disableCalltips(self, event: Event = None) -> None:
        """Disable calltips."""
        self.k.enable_calltips = False
        self.showCalltipsStatus()

    @ac_cmd('enable-autocompleter')
    def enableAutocompleter(self, event: Event = None) -> None:
        """Enable the autocompleter."""
        self.k.enable_autocompleter = True
        self.showAutocompleterStatus()

    @ac_cmd('enable-calltips')
    def enableCalltips(self, event: Event = None) -> None:
        """Enable calltips."""
        self.k.enable_calltips = True
        self.showCalltipsStatus()

    @ac_cmd('toggle-autocompleter')
    def toggleAutocompleter(self, event: Event = None) -> None:
        """Toggle whether the autocompleter is enabled."""
        self.k.enable_autocompleter = not self.k.enable_autocompleter
        self.showAutocompleterStatus()

    @ac_cmd('toggle-calltips')
    def toggleCalltips(self, event: Event = None) -> None:
        """Toggle whether calltips are enabled."""
        self.k.enable_calltips = not self.k.enable_calltips
        self.showCalltipsStatus()
    #@+node:ekr.20061031131434.13: *4* ac.showCalltips
    @ac_cmd('show-calltips')
    def showCalltips(self, event: Event = None) -> None:
        """Show the calltips at the cursor."""
        c, k, w = self.c, self.c.k, event and event.w
        if not w:
            return
        is_headline = c.widget_name(w).startswith('head')
        if k.enable_calltips and not is_headline:
            self.w = w
            self.calltip()
        else:
            c.insertCharFromEvent(event)
    #@+node:ekr.20061031131434.14: *4* ac.showCalltipsForce
    @ac_cmd('show-calltips-force')
    def showCalltipsForce(self, event: Event = None) -> None:
        """Show the calltips at the cursor, even if calltips are not presently enabled."""
        c, w = self.c, event and event.w
        if not w:
            return
        is_headline = c.widget_name(w).startswith('head')
        if not is_headline:
            self.w = w
            self.calltip()
        else:
            c.insertCharFromEvent(event)
    #@+node:ekr.20061031131434.15: *4* ac.showAutocompleter/CalltipsStatus
    def showAutocompleterStatus(self) -> None:
        """Show the autocompleter status."""
        k = self.k
        if not g.unitTesting:
            s = f"autocompleter {'On' if k.enable_autocompleter else 'Off'}"
            g.red(s)

    def showCalltipsStatus(self) -> None:
        """Show the autocompleter status."""
        k = self.k
        if not g.unitTesting:
            s = f"calltips {'On' if k.enable_calltips else 'Off'}"
            g.red(s)
    #@+node:ekr.20061031131434.16: *3* ac.Helpers
    #@+node:ekr.20110512212836.14469: *4* ac.exit
    def exit(self) -> None:

        trace = all(z in g.app.debug for z in ('abbrev', 'verbose'))
        if trace:
            g.trace('(AutoCompleterClass)')
        c, p, u = self.c, self.c.p, self.c.undoer
        w = self.w or c.frame.body.wrapper
        c.k.keyboardQuit()  # #2927: Deletes completer tabs.
        if self.use_qcompleter:
            if self.qw:
                self.qw.end_completer()
                self.qw = None  # Bug fix: 2013/09/24.
        # Restore the selection range that may have been destroyed by changing tabs.
        c.widgetWantsFocusNow(w)
        i, j = w.getSelectionRange()
        w.setSelectionRange(i, j, insert=j)
        newText = w.getAllText()
        if p.b == newText:
            return
        bunch = u.beforeChangeBody(p)
        p.v.b = newText  # p.b would cause a redraw.
        u.afterChangeBody(p, 'auto-completer', bunch)

    finish = exit
    abort = exit
    #@+node:ekr.20061031131434.18: *4* ac.append/begin/popTabName
    def appendTabName(self, word: str) -> None:
        self.setTabName(self.tabName + '.' + word)

    def beginTabName(self, word: str) -> None:
        self.setTabName('AutoComplete ' + word)

    def clearTabName(self) -> None:
        self.setTabName('AutoComplete ')

    def popTabName(self) -> None:
        s = self.tabName
        i = s.rfind('.', 0, -1)
        if i > -1:
            self.setTabName(s[0:i])

    # Underscores are not valid in Pmw tab names!

    def setTabName(self, s: str) -> None:

        log = self.c.frame.log
        newTabName = s.replace('_', '') or ''
        if newTabName != self.tabName:
            # #2927: Rename the tab.
            log.renameTab(self.tabName, newTabName)
            self.tabName = newTabName
            log.clearTab(self.tabName)
    #@+node:ekr.20110509064011.14556: *4* ac.attr_matches
    def attr_matches(self, s: str, namespace: Any) -> Optional[list[str]]:
        """Compute matches when string s is of the form name.name....name.

        Evaluates s using eval(s,namespace)

        Assuming the text is of the form NAME.NAME....[NAME], and can be evaluated in
        the namespace, it will be evaluated and its attributes (as revealed by
        dir()) are used as possible completions.

        For class instances, class members are are also considered.)

        **Warning**: this can still invoke arbitrary C code, if an object
        with a __getattr__ hook is evaluated.

        """
        # Seems to work great. Catches things like ''.<tab>
        m = re.match(r"(\S+(\.\w+)*)\.(\w*)$", s)
        if not m:
            return []
        expr, attr = m.group(1, 3)
        try:
            safe_expr = self.strip_brackets(expr)
            obj = eval(safe_expr, namespace)
        except Exception:
            return []
        # Build the result.
        words = dir(obj)
        n = len(attr)
        result = [f"{expr}.{w}" for w in words if w[:n] == attr]
        return result
    #@+node:ekr.20061031131434.11: *4* ac.auto_completer_state_handler
    def auto_completer_state_handler(self, event: Event) -> Optional[str]:
        """Handle all keys while autocompleting."""
        c, k, tag = self.c, self.k, 'auto-complete'
        state = k.getState(tag)
        ch = event.char if event else ''
        stroke = event.stroke if event else ''
        is_plain = k.isPlainKey(stroke)
        if state == 0:
            c.frame.log.clearTab(self.tabName)
            common_prefix, prefix, tabList = self.compute_completion_list()
            if tabList:
                k.setState(tag, 1, handler=self.auto_completer_state_handler)
            else:
                self.exit()
        elif ch in ('\n', 'Return'):
            self.exit()
        elif ch == 'Escape':
            self.exit()
        elif ch in ('\t', 'Tab'):
            self.compute_completion_list()
        elif ch in ('\b', 'BackSpace'):
            self.do_backspace()
        elif ch == '.':
            self.insert_string('.')
            self.compute_completion_list()
        elif ch == '?':
            self.info()
        elif ch == '!':
            # Toggle between verbose and brief listing.
            self.verbose = not self.verbose
            kind = 'ON' if self.verbose else 'OFF'
            message = f"verbose completions {kind}"
            g.es_print(message)
            # This doesn't work because compute_completion_list clears the autocomplete tab.
            # self.put('', message, tabName=self.tabName)
            # This is almost invisible: the fg='red' is not honored.
            c.frame.putStatusLine(message, fg='red')
            self.compute_completion_list()
        # elif ch == 'Down' and hasattr(self,'onDown'):
            # self.onDown()
        # elif ch == 'Up' and hasattr(self,'onUp'):
            # self.onUp()
        elif is_plain and ch and ch in string.printable:
            self.insert_general_char(ch)
        elif stroke == k.autoCompleteForceKey:
            # This is probably redundant because completions will exist.
            # However, it doesn't hurt, and it may be useful rarely.
            common_prefix, prefix, tabList = self.compute_completion_list()
            if tabList:
                self.show_completion_list(common_prefix, prefix, tabList)
            else:
                g.warning('No completions')
                self.exit()
        else:
            self.abort()
            return 'do-standard-keys'
        return None
    #@+node:ekr.20061031131434.20: *4* ac.calltip & helpers
    def calltip(self) -> None:
        """Show the calltips for the present prefix.
        ch is '(' if the user has just typed it.
        """
        obj, prefix = self.get_object()
        if obj:
            self.calltip_success(prefix, obj)
        else:
            self.calltip_fail(prefix)
        self.exit()
    #@+node:ekr.20110512090917.14468: *5* ac.calltip_fail
    def calltip_fail(self, prefix: str) -> None:
        """Evaluation of prefix failed."""
        self.insert_string('(')
    #@+node:ekr.20110512090917.14469: *5* ac.calltip_success
    def calltip_success(self, prefix: str, obj: Any) -> None:

        try:
            s = str(inspect.signature(obj))
            self.insert_string(s, select=True)
        except Exception:
            # g.es_exception()
            pass
    #@+node:ekr.20061031131434.28: *4* ac.compute_completion_list & helper
    def compute_completion_list(self) -> tuple[str, str, list]:
        """Return the autocompleter completion list."""
        prefix = self.get_autocompleter_prefix()
        key, options = self.get_cached_options(prefix)
        if not options:
            options = self.get_completions(prefix)
        tabList, common_prefix = g.itemsMatchingPrefixInList(
            prefix, options, matchEmptyPrefix=False)
        if not common_prefix:
            tabList, common_prefix = g.itemsMatchingPrefixInList(
                prefix, options, matchEmptyPrefix=True)
        if tabList:
            self.show_completion_list(common_prefix, prefix, tabList)
        return common_prefix, prefix, tabList
    #@+node:ekr.20110514051607.14524: *5* ac.get_cached_options
    def get_cached_options(self, prefix: str) -> tuple[str, list[str]]:
        d = self.completionsDict
        # Search the completions dict for shorter and shorter prefixes.
        i = len(prefix)
        while i > 0:
            key = prefix[:i]
            i -= 1
            # Make sure we report hits only of real objects.
            if key.endswith('.'):
                return key, []
            options = d.get(key)
            if options:
                return key, options
        return None, []
    #@+node:ekr.20061031131434.29: *4* ac.do_backspace
    def do_backspace(self) -> None:
        """Delete the character and recompute the completion list."""
        c, w = self.c, self.w
        c.bodyWantsFocusNow()
        i = w.getInsertPoint()
        while i > 1:
            w.delete(i - 1, i)
            w.setInsertPoint(i - 1)
            i -= 1
            prefix = self.get_autocompleter_prefix()
            common_prefix, prefix2, tabList = self.compute_completion_list()
            if len(tabList) > 1 and prefix == common_prefix:
                return
        self.exit()
    #@+node:ekr.20110509064011.14561: *4* ac.get_autocompleter_prefix
    def get_autocompleter_prefix(self) -> str:
        # Only the body pane supports auto-completion.
        w = self.c.frame.body.wrapper
        s = w.getAllText()
        if not s:
            return ''
        i = w.getInsertPoint() - 1
        i = j = max(0, i)
        while i >= 0 and (s[i].isalnum() or s[i] in '._'):
            i -= 1
        i += 1
        j += 1
        prefix = s[i:j]
        return prefix
    #@+node:ekr.20110512212836.14471: *4* ac.get_completions & helpers
    jedi_warning = False

    def get_completions(self, prefix: str) -> list[str]:
        """Return jedi or codewise completions."""
        d = self.completionsDict
        if self.use_jedi:
            try:
                import jedi
            except ImportError:
                jedi = None
                if not self.jedi_warning:
                    self.jedi_warning = True
                    g.es_print('can not import jedi')
                    g.es_print('ignoring @bool use_jedi = True')
            if jedi:
                aList = (
                    # Prefer the jedi completions.
                    self.get_jedi_completions(prefix) or
                    self.get_leo_completions(prefix))
                d[prefix] = aList
                return aList
        #
        # Not jedi. Use codewise.
        # Precompute the codewise completions for '.self'.
        if not self.codewiseSelfList:
            aList = self.get_codewise_completions('self.')
            self.codewiseSelfList = [z[5:] for z in aList]
            d['self.'] = self.codewiseSelfList
        # Use the cached list if it exists.
        aList = d.get(prefix)
        if aList:
            return aList
        aList = (
            # Prefer the Leo completions.
            self.get_leo_completions(prefix) or
            self.get_codewise_completions(prefix)
        )
        d[prefix] = aList
        return aList
    #@+node:ekr.20110510120621.14539: *5* ac.get_codewise_completions & helpers
    def get_codewise_completions(self, prefix: str) -> list[str]:
        """Use codewise to generate a list of hits."""
        c = self.c
        if m := re.match(r"(\S+(\.\w+)*)\.(\w*)$", prefix):
            varname = m.group(1)
            ivar = m.group(3)
            kind, aList = self.guess_class(c, varname)
        else:
            kind, aList = 'none', []
            varname, ivar = None, None
        if aList:
            if kind == 'class':
                hits = self.lookup_methods(aList, ivar)
                hits.extend(self.codewiseSelfList)
            elif kind == 'module':
                hits = self.lookup_modules(aList, ivar)
        else:
            aList2 = prefix.split('.')
            if aList2:
                func = aList2[-1]
                hits = self.lookup_functions(func)
            else:
                hits = []
        if 1:  # A kludge: add the prefix to each hit.
            hits = [f"{varname}.{z}" for z in hits]
        return hits
    #@+node:ekr.20110510120621.14540: *6* ac.clean
    def clean(self, hits: list[list[str]]) -> list[str]:
        """Clean up hits, a list of ctags patterns, for use in completion lists."""
        # Just take the function name: ignore the signature & file.
        aList = list(set([z[0] for z in hits]))
        aList.sort()
        return aList
    #@+node:ekr.20110512232915.14481: *6* ac.clean_for_display (not used)
    def clean_for_display(self, hits: str) -> list[str]:
        """Clean up hits, a list of ctags patterns, for display purposes."""
        aList = []
        for h in hits:
            s = h[0]
            # Display oriented: no good for completion list.
            fn = h[1].strip()
            if fn.startswith('/'):
                sig = fn[2:-4].strip()
            else:
                sig = fn
            aList.append(f"{s}: {sig}")
        aList = list(set(aList))
        aList.sort()
        return aList
    #@+node:ekr.20110510120621.14542: *6* ac.guess_class
    def guess_class(self, c: Cmdr, varname: str) -> tuple[str, list[str]]:
        """Return kind, class_list"""
        # if varname == 'g':
            # return 'module',['leoGlobals']
        if varname == 'p':
            return 'class', ['position']
        if varname == 'c':
            return 'class', ['Commands']
        if varname == 'self':
            # Return the nearest enclosing class.
            for p in c.p.parents():
                h = p.h
                if m := re.search(r'class\s+(\w+)', h):
                    return 'class', [m.group(1)]
        # This is not needed now that we add the completions for 'self'.
            # aList = ContextSniffer().get_classes(c.p.b, varname)
        return 'class', []
    #@+node:ekr.20110510120621.14543: *6* ac.lookup_functions/methods/modules
    # Leo 6.6.2: These functions can fail if codewise has not been inited.

    def lookup_functions(self, prefix: str) -> list[str]:
        try:
            aList = codewise.cmd_functions([prefix])
            hits = [z.split(None, 1) for z in aList if z.strip()]
            return self.clean(hits)
        except Exception:
            return []

    def lookup_methods(self, aList: list[str], prefix: str) -> list[str]:
        # prefix not used, only aList[0] used.
        try:
            aList = codewise.cmd_members([aList[0]])
            hits = [z.split(None, 1) for z in aList if z.strip()]
            return self.clean(hits)
        except Exception:
            return []

    def lookup_modules(self, aList: list[str], prefix: str) -> list[str]:
        # prefix not used, only aList[0] used.
        try:
            aList = codewise.cmd_functions([aList[0]])
            hits = [z.split(None, 1) for z in aList if z.strip()]
            return self.clean(hits)
        except Exception:
            return []
    #@+node:ekr.20180519111302.1: *5* ac.get_jedi_completions & helper
    def get_jedi_completions(self, prefix: str) -> list[str]:

        c = self.c
        w = c.frame.body.wrapper
        i = w.getInsertPoint()
        p = c.p
        body_s = p.b
        #
        # Get the entire source for jedi.
        t1 = time.process_time()
        goto = gotoCommands.GoToCommands(c)
        root, fileName = goto.find_root(p)
        if root:
            source = goto.get_external_file_with_sentinels(root=root or p)
            n0 = goto.find_node_start(p=p, s=source)
            if n0 is None:
                n0 = 0
        else:
            source = body_s
            n0 = 0
        t2 = time.process_time()
        #
        # Get local line
        lines = g.splitLines(body_s)
        row, column = g.convertPythonIndexToRowCol(body_s, i)
        if row >= len(lines):  # 2020/11/27
            return []
        line = lines[row]
        #
        # Find the global line, and compute offsets.
        source_lines = g.splitLines(source)
        for jedi_line, g_line in enumerate(source_lines[n0:]):  # noqa: B007: jedi_line used below.
            if line.lstrip() == g_line.lstrip():
                # Adjust the column.
                indent1 = len(line) - len(line.lstrip())
                indent2 = len(g_line) - len(g_line.lstrip())
                if indent2 >= indent1:
                    local_column = column  # For traces.
                    column += abs(indent2 - indent1)
                    break
        else:
            completions = None
            jedi_line, indent1, indent2 = None, None, None
            if 0:  # This *can* happen.
                g.printObj(source_lines[n0 - 1 : n0 + 30])
                print(f"can not happen: not found: {line!r}")
        #
        # Get the jedi completions.
        if jedi and jedi_line is not None:
            try:
                # https://jedi.readthedocs.io/en/latest/docs/api.html#script
                script = jedi.Script(source, path=g.shortFileName(fileName))
                completions = script.complete(
                    line=1 + n0 + jedi_line,
                    column=column,
                )
                t3 = time.process_time()
            except Exception:
                t3 = time.process_time()
                completions = None
                g.printObj(source_lines[n0 - 1 : n0 + 30])
                print('ERROR', p.h)
        if not completions:
            return []
        # May be used in traces below.
        assert t3 >= t2 >= t1
        assert local_column is not None
        completions = [z.name for z in completions]
        completions = [self.add_prefix(prefix, z) for z in completions]
        # Retain these for now...
            # g.printObj(completions[:5])
            # head = line[:local_column]
            # ch = line[local_column:local_column+1]
            # g.trace(len(completions), repr(ch), head.strip())
        return completions
    #@+node:ekr.20180526211127.1: *6* ac.add_prefix
    def add_prefix(self, prefix: str, s: str) -> str:
        """A hack to match the callers expectations."""
        if prefix.find('.') > -1:
            aList = prefix.split('.')
            prefix = '.'.join(aList[:-1]) + '.'
        return s if s.startswith(prefix) else prefix + s
    #@+node:ekr.20110509064011.14557: *5* ac.get_leo_completions
    def get_leo_completions(self, prefix: str) -> list[str]:
        """Return completions in an environment defining c, g and p."""
        aList = []
        for d in self.namespaces + [self.get_leo_namespace(prefix)]:
            aList.extend(self.attr_matches(prefix, d))
        aList.sort()
        return aList
    #@+node:ekr.20110512090917.14466: *4* ac.get_leo_namespace
    def get_leo_namespace(self, prefix: str) -> dict[str, Any]:
        """
        Return an environment in which to evaluate prefix.
        Add some common standard library modules as needed.
        """
        k = self.k
        d = {'c': k.c, 'p': k.c.p, 'g': g}
        aList = prefix.split('.')
        if len(aList) > 1:
            name = aList[0]
            if m := sys.modules.get(name):
                d[name] = m
        return d
    #@+node:ekr.20110512170111.14472: *4* ac.get_object
    def get_object(self) -> tuple[Any, str]:
        """Return the object corresponding to the current prefix."""
        common_prefix, prefix1, aList = self.compute_completion_list()
        if not aList:
            return None, prefix1
        if len(aList) == 1:
            prefix = aList[0]
        else:
            prefix = common_prefix
        if prefix.endswith('.') and self.use_qcompleter:
            prefix += self.qcompleter.get_selection()
        safe_prefix = self.strip_brackets(prefix)
        for d in self.namespaces + [self.get_leo_namespace(prefix)]:
            try:
                obj = eval(safe_prefix, d)
                break  # only reached if none of the exceptions below occur
            except AttributeError:
                obj = None
            except NameError:
                obj = None
            except SyntaxError:
                obj = None
            except Exception:
                g.es_exception()
                obj = None
        return obj, prefix
    #@+node:ekr.20061031131434.38: *4* ac.info
    def info(self) -> None:
        """Show the signature and docstring for the present completion."""
        c = self.c
        obj, prefix = self.get_object()
        c.frame.log.clearTab('Info', wrap='word')

        def put(s: str) -> None:
            self.put('', s, tabName='Info')

        put(prefix)
        put(f"Signature: {inspect.signature(obj)!s}")
        doc = inspect.getdoc(obj)
        if doc:
            put(str(doc))
    #@+node:ekr.20110510071925.14586: *4* ac.init_qcompleter
    def init_qcompleter(self, event: Event = None) -> None:

        # Compute the prefix and the list of options.
        prefix = self.get_autocompleter_prefix()
        options = self.get_completions(prefix)
        w = self.c.frame.body.wrapper.widget  # A LeoQTextBrowser.  May be none for unit tests.
        if w and options:
            self.qw = w
            self.qcompleter = w.init_completer(options)
            self.auto_completer_state_handler(event)
        else:
            if not g.unitTesting:
                g.warning('No completions')
            self.exit()
    #@+node:ekr.20110511133940.14552: *4* ac.init_tabcompleter
    def init_tabcompleter(self, event: Event = None) -> None:
        # Compute the prefix and the list of options.
        prefix = self.get_autocompleter_prefix()
        options = self.get_completions(prefix)
        if options:
            self.clearTabName()  # Creates the tabbed pane.
            self.auto_completer_state_handler(event)
        else:
            g.warning('No completions')
            self.exit()
    #@+node:ekr.20061031131434.39: *4* ac.insert_general_char
    def insert_general_char(self, ch: str) -> None:

        trace = all(z in g.app.debug for z in ('abbrev', 'verbose'))
        k, w = self.k, self.w
        if g.isWordChar(ch):
            if trace:
                g.trace('ch', repr(ch))
            self.insert_string(ch)
            common_prefix, prefix, aList = self.compute_completion_list()
            if not aList:
                if self.forbid_invalid:
                    # Delete the character we just inserted.
                    self.do_backspace()
            #@verbatim
            # @bool auto_tab_complete is deprecated.
            # Auto-completion makes no sense if it is False.
            elif self.auto_tab and len(common_prefix) > len(prefix):
                extend = common_prefix[len(prefix) :]
                ins = w.getInsertPoint()
                if trace:
                    g.trace('extend', repr(extend))
                w.insert(ins, extend)
            return
        if ch == '(' and k.enable_calltips:
            # This calls self.exit if the '(' is valid.
            self.calltip()
        else:
            if trace:
                g.trace('ch', repr(ch))
            self.insert_string(ch)
            self.exit()
    #@+node:ekr.20061031131434.31: *4* ac.insert_string
    def insert_string(self, s: str, select: bool = False) -> None:
        """
        Insert an auto-completion string s at the insertion point.

        Leo 6.4. This *part* of auto-completion is no longer undoable.
        """
        c, w = self.c, self.w
        if not g.isTextWrapper(w):
            return
        c.widgetWantsFocusNow(w)
        #
        # Don't make this undoable.
            # oldText = w.getAllText()
            # oldSel = w.getSelectionRange()
            # bunch = u.beforeChangeBody(p)
        i = w.getInsertPoint()
        w.insert(i, s)
        if select:
            j = i + len(s)
            w.setSelectionRange(i, j, insert=j)
        else:
            w.setInsertPoint(i + len(s))
        #
        # Don't make this undoable.
            # if 0:
                # u.doTyping(p, 'Typing',
                    # oldSel=oldSel,
                    # oldText=oldText,
                    # newText=w.getAllText(),
                    # newInsert=w.getInsertPoint(),
                    # newSel=w.getSelectionRange())
            # else:
                # u.afterChangeBody(p, 'auto-complete', bunch)
        if self.use_qcompleter and self.qw:
            c.widgetWantsFocusNow(self.qw.leo_qc)
    #@+node:ekr.20110314115639.14269: *4* ac.is_leo_source_file
    def is_leo_source_file(self) -> bool:
        """Return True if this is one of Leo's source files."""
        c = self.c
        table = (z.lower() for z in (
            'leoDocs.leo',
            'LeoGui.leo', 'LeoGuiPluginsRef.leo',
            # 'leoPlugins.leo', 'leoPluginsRef.leo',
            'leoPy.leo', 'leoPyRef.leo',
            'myLeoSettings.leo', 'leoSettings.leo',
            'ekr.leo',
            # 'test.leo',
        ))
        return c.shortFileName().lower() in table
    #@+node:ekr.20101101175644.5891: *4* ac.put
    def put(self, *args: Any, **keys: Any) -> None:
        """Put s to the given tab.

        May be overridden in subclasses."""
        # print('autoCompleter.put',args,keys)
        if g.unitTesting:
            pass
        else:
            g.es(*args, **keys)
    #@+node:ekr.20110511133940.14561: *4* ac.show_completion_list & helpers
    def show_completion_list(self, common_prefix: str, prefix: str, tabList: list[str]) -> None:

        c = self.c
        aList = common_prefix.split('.')
        header = '.'.join(aList[:-1])
        # "!" toggles self.verbose.
        if self.verbose or self.use_qcompleter or len(tabList) < 20:
            tabList = self.clean_completion_list(header, tabList)
        else:
            tabList = self.get_summary_list(header, tabList)
        if self.use_qcompleter:
            # Put the completions in the QListView.
            if self.qw:
                self.qw.show_completions(tabList)
        else:
            # Update the tab name, creating the tab if necessary.
            c.widgetWantsFocus(self.w)
            c.frame.log.clearTab(self.tabName)
            self.beginTabName(header + '.' if header else '')
            s = '\n'.join(tabList)
            self.put('', s, tabName=self.tabName)
    #@+node:ekr.20110513104728.14453: *5* ac.clean_completion_list
    def clean_completion_list(self, header: str, tabList: list[str]) -> list[str]:
        """Return aList with header removed from the start of each list item."""
        return [
            z[len(header) + 1 :] if z.startswith(header) else z
                for z in tabList]
    #@+node:ekr.20110513104728.14454: *5* ac.get_summary_list
    def get_summary_list(self, header: str, tabList: list[str]) -> list[str]:
        """Show the possible starting letters,
        but only if there are more than one.
        """
        d: dict[str, int] = {}
        for z in tabList:
            tail = z[len(header) :] if z else ''
            if tail.startswith('.'):
                tail = tail[1:]
            ch = tail[0] if tail else ''
            if ch:
                n = d.get(ch, 0)
                d[ch] = n + 1
        aList = [f"{ch2} {d.get(ch2)}" for ch2 in sorted(d)]
        if len(aList) > 1:
            tabList = aList
        else:
            tabList = self.clean_completion_list(header, tabList)
        return tabList
    #@+node:ekr.20061031131434.46: *4* ac.start
    def start(self, event: Event) -> None:
        """Init the completer and start the state handler."""
        # We don't need to clear this now that we don't use ContextSniffer.
        c = self.c
        if c.config.getBool('use-jedi', default=True):
            self.completionsDict = {}
        if self.use_qcompleter:
            self.init_qcompleter(event)
        else:
            self.init_tabcompleter(event)
    #@+node:ekr.20110512170111.14471: *4* ac.strip_brackets
    def strip_brackets(self, s: str) -> str:
        """Return s with all brackets removed.

        This (mostly) ensures that eval will not execute function calls, etc.
        """
        for ch in '[]{}()':
            s = s.replace(ch, '')
        return s
    #@-others
#@+node:ekr.20110312162243.14260: ** class ContextSniffer
class ContextSniffer:
    """ Class to analyze surrounding context and guess class

    For simple dynamic code completion engines.
    """

    def __init__(self) -> None:
        self.vars: dict[str, list[Any]] = {}  # Keys are var names; values are list of classes
    #@+others
    #@+node:ekr.20110312162243.14261: *3* get_classes
    def get_classes(self, s: str, varname: str) -> list[str]:
        """Return a list of classes for string s."""
        self.push_declarations(s)
        aList = self.vars.get(varname, [])
        return aList
    #@+node:ekr.20110312162243.14262: *3* set_small_context
    # def set_small_context(self, body):
        # """ Set immediate function """
        # self.push_declarations(body)
    #@+node:ekr.20110312162243.14263: *3* push_declarations & helper
    def push_declarations(self, s: str) -> None:
        for line in s.splitlines():
            line = line.lstrip()
            if line.startswith('#'):
                line = line.lstrip('#')
                parts = line.split(':')
                if len(parts) == 2:
                    a, b = parts
                    self.declare(a.strip(), b.strip())
    #@+node:ekr.20110312162243.14264: *4* declare
    def declare(self, var: str, klass: str) -> None:
        vars = self.vars.get(var, [])
        if not vars:
            self.vars[var] = vars
        vars.append(klass)
    #@-others
#@+node:ekr.20140813052702.18194: ** class FileNameChooser
class FileNameChooser:
    """A class encapsulation file selection & completion logic."""
    #@+others
    #@+node:ekr.20140813052702.18195: *3* fnc.__init__
    def __init__(self, c: Cmdr) -> None:
        """Ctor for FileNameChooser class."""
        self.c = c
        self.k = c.k
        assert c and c.k
        self.log: Any = c.frame.log or g.NullObject()  # A Union.
        self.callback: Callable = None
        self.filterExt: list[str] = None
        self.prompt: str = None
        self.tabName: str = None
    #@+node:ekr.20140813052702.18196: *3* fnc.compute_tab_list
    def compute_tab_list(self) -> tuple[str, list[str]]:
        """Compute the list of completions."""
        path = self.get_label()
        # #215: insert-file-name doesn't process ~
        path = g.finalize(path)
        sep = os.path.sep
        if g.os_path_exists(path):
            if g.os_path_isdir(path):
                if path.endswith(os.sep):
                    aList = g.glob_glob(path + '*')
                else:
                    aList = g.glob_glob(path + sep + '*')
                tabList = [z + sep if g.os_path_isdir(z) else z for z in aList]
            else:
                # An existing file.
                tabList = [path]
        else:
            if path and path.endswith(sep):
                path = path[:-1]
            aList = g.glob_glob(path + '*')
            tabList = [z + sep if g.os_path_isdir(z) else z for z in aList]
        if self.filterExt:
            for ext in self.filterExt:
                tabList = [z for z in tabList if not z.endswith(ext)]
        tabList = [g.os_path_normslashes(z) for z in tabList]
        junk, common_prefix = g.itemsMatchingPrefixInList(path, tabList)
        return common_prefix, tabList
    #@+node:ekr.20140813052702.18197: *3* fnc.do_back_space
    def do_back_space(self) -> None:
        """Handle a back space."""
        w = self.c.k.w
        if w and w.hasSelection():
            # s = w.getAllText()
            i, j = w.getSelectionRange()
            w.delete(i, j)
            s = self.get_label()
        else:
            s = self.get_label()
            if s:
                s = s[:-1]
            self.set_label(s)
        if s:
            common_prefix, tabList = self.compute_tab_list()
            # Do *not* extend the label to the common prefix.
        else:
            tabList = []
        self.show_tab_list(tabList)
    #@+node:ekr.20140813052702.18198: *3* fnc.do_char
    def do_char(self, char: str) -> None:
        """Handle a non-special character."""
        w = self.c.k.w
        if w and w.hasSelection:
            # s = w.getAllText()
            i, j = w.getSelectionRange()
            w.delete(i, j)
            w.setInsertPoint(i)
            w.insert(i, char)
        else:
            self.extend_label(char)
        common_prefix, tabList = self.compute_tab_list()
        self.show_tab_list(tabList)
        if common_prefix:
            if 0:
                # This is a bit *too* helpful.
                # It's too easy to type ahead by mistake.
                # Instead, completion should happen only when the user types <tab>.
                self.set_label(common_prefix)
            # Recompute the tab list.
            common_prefix, tabList = self.compute_tab_list()
            self.show_tab_list(tabList)
            if len(tabList) == 1:
                # Automatically complete the typing only if there is only one item in the list.
                self.set_label(common_prefix)
        else:
            # Restore everything.
            self.set_label(self.get_label()[:-1])
            self.extend_label(char)
    #@+node:ekr.20140813052702.18199: *3* fnc.do_tab
    def do_tab(self) -> None:
        """Handle tab completion."""
        old = self.get_label()
        common_prefix, tabList = self.compute_tab_list()
        self.show_tab_list(tabList)
        if len(tabList) == 1:
            common_prefix = tabList[0]
            self.set_label(common_prefix)
        elif len(common_prefix) > len(old):
            self.set_label(common_prefix)
    #@+node:ekr.20140813052702.18200: *3* fnc.get_file_name (entry)
    def get_file_name(self,
        event: Event,
        callback: Callable,
        filterExt: list[str],
        prompt: str,
        tabName: str,
    ) -> None:
        """Get a file name, supporting file completion."""
        c, k = self.c, self.c.k
        tag = 'get-file-name'
        state = k.getState(tag)
        char = event.char if event else ''
        if state == 0:
            # Re-init all ivars.
            self.log = c.frame.log or g.NullObject()
            self.callback = callback
            self.filterExt = filterExt or ['.pyc', '.bin',]
            self.prompt = prompt
            self.tabName = tabName
            join = g.finalize_join
            finalize = g.finalize
            normslashes = g.os_path_normslashes
            # #467: Add setting for preferred directory.
            directory = c.config.getString('initial-chooser-directory')
            if directory:
                directory = finalize(directory)
                if not g.os_path_exists(directory):
                    g.es_print('@string initial-chooser-directory not found',
                        normslashes(directory))
                    directory = None
            if not directory:
                directory = finalize(os.curdir)
            # Init the label and state.
            tail = k.functionTail and k.functionTail.strip()
            label = join(directory, tail) if tail else directory + os.sep
            self.set_label(normslashes(label))
            k.setState(tag, 1, self.get_file_name)
            self.log.selectTab(self.tabName)
            junk, tabList = self.compute_tab_list()
            self.show_tab_list(tabList)
            c.minibufferWantsFocus()
        elif char == 'Escape':
            k.keyboardQuit()
        elif char in ('\n', 'Return'):
            self.log.deleteTab(self.tabName)
            path = self.get_label()
            k.keyboardQuit()
            if self.callback:
                # pylint: disable=not-callable
                self.callback(path)
            else:
                g.trace('no callback')
        elif char in ('\t', 'Tab'):
            self.do_tab()
            c.minibufferWantsFocus()
        elif char in ('\b', 'BackSpace'):
            self.do_back_space()
            c.minibufferWantsFocus()
        elif k.isPlainKey(char):
            self.do_char(char)
        else:
            pass
    #@+node:ekr.20140813052702.18201: *3* fnc.extend/get/set_label
    def extend_label(self, s: str) -> None:
        """Extend the label by s."""
        self.c.k.extendLabel(s, select=False, protect=False)

    def get_label(self) -> str:
        """Return the label, not including the prompt."""
        return self.c.k.getLabel(ignorePrompt=True)

    def set_label(self, s: str) -> None:
        """Set the label after the prompt to s. The prompt never changes."""
        self.c.k.setLabel(self.prompt, protect=True)
        self.c.k.extendLabel(s or '', select=False, protect=False)
    #@+node:ekr.20140813052702.18202: *3* fnc.show_tab_list
    def show_tab_list(self, tabList: list[str]) -> None:
        """Show the tab list in the log tab."""
        self.log.clearTab(self.tabName)
        s = g.finalize(os.curdir) + os.sep
        es = []
        for path in tabList:
            theDir, fileName = g.os_path_split(path)
            s = theDir if path.endswith(os.sep) else fileName
            s = fileName or g.os_path_basename(theDir) + os.sep
            es.append(s)
        g.es('', '\n'.join(es), tabName=self.tabName)
    #@-others
#@+node:ekr.20140816165728.18940: ** class GetArg
class GetArg:
    """
    A class encapsulating all k.getArg logic.

    k.getArg maps to ga.get_arg, which gets arguments in the minibuffer.

    For details, see the docstring for ga.get_arg
    """
    #@+others
    #@+node:ekr.20140818052417.18241: *3* ga.birth
    #@+node:ekr.20140816165728.18952: *4* ga.__init__
    def __init__(self,
        c: Cmdr,
        prompt: str = 'full-command: ',
        tabName: str = 'Completion',
    ) -> None:
        """Ctor for GetArg class."""
        # Common ivars.
        self.c = c
        self.k = c.k
        assert c
        assert c.k
        self.log = c.frame.log or g.NullObject()
        self.functionTail: str = ''
        self.tabName = tabName
        # State vars.
        self.after_get_arg_state: tuple[str, int, Callable] = None
        self.arg_completion = True
        self.handler: Callable = None
        self.tabList: list[str] = []
        # Tab cycling ivars...
        self.cycling_prefix: str = None
        self.cycling_index = -1
        self.cycling_tabList: list[str] = []
        # The following are k globals.
            # k.arg.
            # k.argSelectedText
            # k.oneCharacterArg
    #@+node:ekr.20140817110228.18321: *3* ga.compute_tab_list
    # Called from k.doTabCompletion: with tabList = list(c.commandsDict.keys())

    def compute_tab_list(self, tabList: list[str]) -> tuple[str, list[str]]:
        """Compute and show the available completions."""
        # Support vim-mode commands.
        command = self.get_label()
        if self.is_command(command):
            tabList, common_prefix = g.itemsMatchingPrefixInList(command, tabList)
            return common_prefix, tabList
        #
        # For now, disallow further completions if something follows the command.
        command = self.get_command(command)
        return command, [command]
    #@+node:ekr.20140816165728.18965: *3* ga.do_back_space (entry)
    # Called from k.fullCommand: with defaultTabList = list(c.commandsDict.keys())

    def do_back_space(self, tabList: list[str], completion: bool = True) -> None:
        """Handle a backspace and update the completion list."""
        k = self.k
        self.tabList = tabList[:] if tabList else []
        # Update the label.
        w = k.w
        i, j = w.getSelectionRange()
        ins = w.getInsertPoint()
        if ins > len(k.mb_prefix):
            # Step 1: actually delete the character.
            i, j = w.getSelectionRange()
            if i == j:
                ins -= 1
                w.delete(ins)
                w.setSelectionRange(ins, ins, insert=ins)
            else:
                ins = i
                w.delete(i, j)
                w.setSelectionRange(i, i, insert=ins)
        if w.getAllText().strip():
            junk, tabList = self.compute_tab_list(self.tabList)
            # Do *not* extend the label to the common prefix.
        else:
            tabList = []
        if completion:
            # #323.
            common_prefix, tabList = self.compute_tab_list(tabList)
            self.show_tab_list(tabList)
            self.reset_tab_cycling()
    #@+node:ekr.20140817110228.18323: *3* ga.do_tab (entry) & helpers
    # Used by ga.get_arg and k.fullCommand.

    def do_tab(self, tabList: list[str], completion: bool = True) -> None:
        """Handle tab completion when the user hits a tab."""
        c = self.c
        if completion:
            tabList = self.tabList = tabList[:] if tabList else []
            common_prefix, tabList = self.compute_tab_list(tabList)
            if self.cycling_prefix and not self.cycling_prefix.startswith(common_prefix):
                self.cycling_prefix = common_prefix
            #
            # No tab cycling for completed commands having
            # a 'tab_callback' attribute.
            if len(tabList) == 1 and self.do_tab_callback():
                return
            # #323: *Always* call ga.do_tab_list.
            self.do_tab_cycling(common_prefix, tabList)
        c.minibufferWantsFocus()
    #@+node:ekr.20140818145250.18235: *4* ga.do_tab_callback
    def do_tab_callback(self) -> bool:
        """
        If the command-name handler has a tab_callback,
        call handler.tab_callback() and return True.
        """
        c, k = self.c, self.k
        commandName, tail = k.getMinibufferCommandName()
        handler = c.commandsDict.get(commandName)
        if hasattr(handler, 'tab_callback'):
            self.reset_tab_cycling()
            k.functionTail = tail  # For k.getFileName.
            handler.tab_callback()
            return True
        return False
    #@+node:ekr.20140819050118.18317: *4* ga.do_tab_cycling
    def do_tab_cycling(self, common_prefix: str, tabList: list[str]) -> None:
        """Put the next (or first) completion in the minibuffer."""
        s = self.get_label()
        if not common_prefix:
            # Leave the minibuffer as it is.
            self.show_tab_list(tabList)
        # #323.
        elif (
            self.cycling_prefix and
            s.startswith(self.cycling_prefix) and
            sorted(self.cycling_tabList) == sorted(tabList)  # Bug fix: 2016/10/14
        ):
            n = self.cycling_index
            n = self.cycling_index = n + 1 if n + 1 < len(self.cycling_tabList) else 0
            self.set_label(self.cycling_tabList[n])
            self.show_tab_list(self.cycling_tabList)
        else:
            # Restart.
            self.show_tab_list(tabList)
            self.cycling_tabList = tabList[:]
            self.cycling_prefix = common_prefix
            self.set_label(common_prefix)
            if tabList and common_prefix == tabList[0]:
                self.cycling_index = 0
            else:
                self.cycling_index = -1
    #@+node:ekr.20140819050118.18318: *4* ga.reset_tab_cycling
    def reset_tab_cycling(self) -> None:
        """Reset all tab cycling ivars."""
        self.cycling_prefix = None
        self.cycling_index = -1
        self.cycling_tabList = []
    #@+node:ekr.20140816165728.18958: *3* ga.extend/get/set_label
    # Not useful because k.entendLabel doesn't handle selected text.

    if 0:

        def extend_label(self, s: str) -> None:
            """Extend the label by s."""
            self.c.k.extendLabel(s, select=False, protect=False)

    def get_label(self) -> str:
        """Return the label, not including the prompt."""
        return self.c.k.getLabel(ignorePrompt=True)

    def set_label(self, s: str) -> None:
        """Set the label after the prompt to s. The prompt never changes."""
        k = self.c.k
        # Using k.mb_prefix is simplest.  No ga.ivars need be inited.
        k.setLabel(k.mb_prefix, protect=True)
        k.extendLabel(s or '', select=False, protect=False)
    #@+node:ekr.20140816165728.18941: *3* ga.get_arg (entry) & helpers
    def get_arg(
        self,
        event: Event,
        returnKind: str = None,
        returnState: int = None,
        handler: Callable = None,
        tabList: list[str] = None,
        completion: bool = True,
        oneCharacter: bool = False,
        stroke: Stroke = None,
        useMinibuffer: bool = True,
    ) -> None:
        #@+<< ga.get_arg docstring >>
        #@+node:ekr.20140822051549.18299: *4* << ga.get_arg docstring >>
        """
        Accumulate an argument. Enter the given return state when done.

        Ctrl-G will abort this processing at any time.

        All commands needing user input call k.getArg, which just calls ga.get_arg.

        The arguments to ga.get_arg are as follows:

        event:              The event passed to the command.

        returnKind=None:    A string.
        returnState=None,   An int.
        handler=None,       A function.

            When the argument is complete, ga.do_end does::

                if kind: k.setState(kind,n,handler)

        tabList=[]:         A list of possible completions.

        completion=True:    True if completions are enabled.

        oneCharacter=False: True if k.arg should be a single character.

        stroke=None:        The incoming key stroke.

        useMinibuffer=True: True: put focus in the minibuffer while accumulating arguments.
                            False allows sort-lines, for example, to show the selection range.

        """
        #@-<< ga.get_arg docstring >>
        if tabList is None:
            tabList = []
        c, k = self.c, self.k
        state = k.getState('getArg')
        c.check_event(event)
        c.minibufferWantsFocusNow()
        char = event.char if event else ''
        if state == 0:
            self.do_state_zero(completion, event, handler, oneCharacter,
                returnKind, returnState, tabList, useMinibuffer)
            return
        if char == 'Escape':
            k.keyboardQuit()
        elif self.should_end(char, stroke):
            self.do_end(event, char, stroke)
        elif char in ('\t', 'Tab'):
            self.do_tab(self.tabList, self.arg_completion)
        elif char in ('\b', 'BackSpace'):
            self.do_back_space(self.tabList, self.arg_completion)
            c.minibufferWantsFocus()
        elif k.isFKey(stroke):
            # Ignore only F-keys. Ignoring all except plain keys would kill unicode searches.
            pass
        else:
            self.do_char(event, char)
    #@+node:ekr.20161019060054.1: *4* ga.cancel_after_state
    def cancel_after_state(self) -> None:

        self.after_get_arg_state = None
    #@+node:ekr.20140816165728.18955: *4* ga.do_char
    def do_char(self, event: Event, char: str) -> None:
        """Handle a non-special character."""
        k = self.k
        k.updateLabel(event)
        # Any plain key resets tab cycling.
        self.reset_tab_cycling()
    #@+node:ekr.20140817110228.18316: *4* ga.do_end
    def do_end(self, event: Event, char: str, stroke: Stroke) -> None:
        """A return or escape has been seen."""
        k = self.k
        if char == '\t' and char in k.getArgEscapes:
            k.getArgEscapeFlag = True
        if stroke and stroke in k.getArgEscapes:
            k.getArgEscapeFlag = True
        # Get the value.
        gui_arg = getattr(g.app.gui, 'curses_gui_arg', None)
        if k.oneCharacterArg:
            k.arg = char
        else:
            # A hack to support the curses gui.
            k.arg = gui_arg or self.get_label()
        kind, n, handler = self.after_get_arg_state
        if kind:
            k.setState(kind, n, handler)
        self.log.deleteTab('Completion')
        self.reset_tab_cycling()
        if handler:
            # pylint: disable=not-callable
            handler(event)
    #@+node:ekr.20140817110228.18317: *4* ga.do_state_zero
    def do_state_zero(
        self,
        completion: bool,
        event: Event,
        handler: Callable,
        oneCharacter: bool,
        returnKind: str,
        returnState: int,
        tabList: list[str],
        useMinibuffer: bool,
    ) -> None:
        """Do state 0 processing."""
        c, k = self.c, self.k
        #
        # Set the ga globals...
        k.getArgEscapeFlag = False
        self.after_get_arg_state = returnKind, returnState, handler
        self.arg_completion = completion
        self.cycling_prefix = None
        self.handler = handler
        self.tabList = tabList[:] if tabList else []
        #
        # Set the k globals...
        k.functionTail = ''
        k.oneCharacterArg = oneCharacter
        #
        # Do *not* change the label here!
        # Enter the next state.
        c.widgetWantsFocus(c.frame.body.wrapper)
        k.setState('getArg', 1, k.getArg)
        # pylint: disable=consider-using-ternary
        k.afterArgWidget = event and event.widget or c.frame.body.wrapper
        if useMinibuffer:
            c.minibufferWantsFocus()
    #@+node:ekr.20140818103808.18234: *4* ga.should_end
    def should_end(self, char: str, stroke: Stroke) -> bool:
        """Return True if ga.get_arg should return."""
        k = self.k
        return (
            char in ('\n', 'Return',) or
            k.oneCharacterArg or
            stroke and stroke in k.getArgEscapes or
            char == '\t' and char in k.getArgEscapes  # The Find Easter Egg.
        )
    #@+node:ekr.20140818103808.18235: *4* ga.trace_state
    def trace_state(self,
        char: str,
        completion: str,
        handler: Callable,
        state: str,
        stroke: Stroke,
    ) -> None:
        """Trace the vars and ivars."""
        k = self.c.k
        g.trace(
            'state', state, 'char', repr(char), 'stroke', repr(stroke),
            # 'isPlain',k.isPlainKey(stroke),
            '\n',
            'escapes', k.getArgEscapes,
            'completion', self.arg_completion,
            'handler', self.handler and self.handler.__name__ or 'None',
        )
    #@+node:ekr.20140818074502.18222: *3* ga.get_command
    def get_command(self, s: str) -> str:
        """Return the command part of a minibuffer contents s."""
        # #1121.
        if ' ' in s:
            return s[: s.find(' ')].strip()
        return s
    #@+node:ekr.20140818085719.18227: *3* ga.get_minibuffer_command_name
    def get_minibuffer_command_name(self) -> tuple[str, str]:
        """Return the command name in the minibuffer."""
        s = self.get_label()
        command = self.get_command(s)
        tail = s[len(command) :]
        return command, tail
    #@+node:ekr.20140818074502.18221: *3* ga.is_command
    def is_command(self, s: str) -> bool:
        """Return False if something, even a blank, follows a command."""
        # #1121: only ascii space terminates a command.
        return ' ' not in s
    #@+node:ekr.20140816165728.18959: *3* ga.show_tab_list & helper
    def show_tab_list(self, tabList: list[str]) -> None:
        """Show the tab list in the log tab."""
        k = self.k
        self.log.clearTab(self.tabName)
        d = k.computeInverseBindingDict()
        data, legend, n = [], False, 0
        for commandName in tabList:
            dataList = d.get(commandName, [])
            if dataList:
                for z in dataList:
                    pane, stroke = z
                    pane_s = '' if pane == 'all' else pane
                    key = k.prettyPrintKey(stroke)
                    pane_key = f"{pane_s} {key}"
                    source = self.command_source(commandName)
                    if source != ' ':
                        legend = True
                    data.append((pane_key, source, commandName))
                    n = max(n, len(pane_key))
            else:
                # Bug fix: 2017/03/26
                data.append(('', ' ', commandName),)
        aList = ['%*s %s %s' % (-n, z1, z2, z3) for z1, z2, z3 in data]
        if legend:
            aList.extend([
                '',
                'legend:',
                'G leoSettings.leo',
                'M myLeoSettings.leo',
                'L local .leo File',
            ])
        g.es('', '\n'.join(aList), tabName=self.tabName)
    #@+node:ekr.20150402034643.1: *4* ga.command_source
    def command_source(self, commandName: str) -> str:
        """
        Return the source legend of an @button/@command node.
        'G' leoSettings.leo
        'M' myLeoSettings.leo
        'L' local .leo File
        ' ' not an @command or @button node
        """
        c = self.c
        if commandName.startswith('@'):
            d = c.commandsDict
            func = d.get(commandName)
            if hasattr(func, 'source_c'):
                c2 = func.source_c
                fn2 = c2.shortFileName().lower()
                if fn2.endswith('myleosettings.leo'):
                    return 'M'
                if fn2.endswith('leosettings.leo'):
                    return 'G'
                return 'L'
            return '?'
        return ' '
    #@-others
#@+node:ekr.20061031131434.74: ** class KeyHandlerClass
class KeyHandlerClass:
    """
    A class to support emacs-style commands.
    c.k is an instance of this class.
    """
    #@+others
    #@+node:ekr.20061031131434.75: *3*  k.Birth
    #@+node:ekr.20061031131434.76: *4* k.__init__& helpers
    def __init__(self, c: Cmdr) -> None:
        """Create a key handler for c."""
        self.c = c
        self.dispatchEvent = None
        self.fnc: FileNameChooser = None  # A singleton defined in k.finishCreate.
        self.getArgInstance: GetArg = None  # A singleton defined in k.finishCreate.
        self.inited = False  # Set at end of finishCreate.
        # A list of commands whose bindings have been set to None in the local file.
        self.killedBindings: list[Any] = []
        self.replace_meta_with_alt = False  # True: (Mac only) swap Meta and Alt keys.
        self.w = None  # Will be None for NullGui.
        # Generalize...
        self.x_hasNumeric = ['sort-lines', 'sort-fields']
        self.altX_prompt = 'full-command: '
        # Access to data types defined in leoKeys.py
        self.KeyStroke = g.KeyStroke
        # Define all ivars...
        self.defineExternallyVisibleIvars()
        self.defineInternalIvars()
        self.reloadSettings()
        self.defineSingleLineCommands()
        self.defineMultiLineCommands()
        self.autoCompleter = AutoCompleterClass(self)
        self.qcompleter = None  # Set by AutoCompleter.start.
        self.setDefaultUnboundKeyAction()
        self.setDefaultEditingAction()
    #@+node:ekr.20061031131434.78: *5* k.defineExternallyVisibleIvars
    def defineExternallyVisibleIvars(self) -> None:

        self.abbrevOn = False  # True: abbreviations are on.
        self.arg = ''  # The value returned by k.getArg.
        self.getArgEscapeFlag = False  # True: the user escaped getArg in an unusual way.
        self.getArgEscapes: list[str] = []
        self.functionTail = ''  # For vim commands that take minibuffer arguments.
        self.inputModeName = ''  # The name of the input mode, or None.
        self.modePrompt = ''  # The mode prompt.
        self.state = g.bunch(kind=None, n=None, handler=None)
    #@+node:ekr.20061031131434.79: *5* k.defineInternalIvars
    def defineInternalIvars(self) -> None:
        """Define internal ivars of the KeyHandlerClass class."""
        self.abbreviationsDict: dict = {}  # Abbreviations created by @alias nodes.
        # Previously defined bindings...
        self.bindingsDict: dict[str, Any] = {}  # Keys are Tk key names, values are lists of BindingInfo objects.
        # Previously defined binding tags.
        self.bindtagsDict: dict[str, bool] = {}  # Keys are strings (the tag), values are 'True'
        self.commandHistory: list[str] = []
        # Up arrow will select commandHistory[commandIndex]
        self.commandIndex = 0  # List/stack of previously executed commands.
        # Keys are scope names: 'all','text',etc. or mode names.
        # Values are dicts: keys are strokes, values are BindingInfo objects.
        self.masterBindingsDict: dict = {}
        # Keys are strokes; value is list of Widgets in which the strokes are bound.
        self.masterGuiBindingsDict: dict[Stroke, list[Wrapper]] = {}
        # Special bindings for k.fullCommand...
        self.mb_copyKey = None
        self.mb_pasteKey = None
        self.mb_cutKey = None
        # Keys whose bindings are computed by initSpecialIvars...
        self.abortAllModesKey = None
        self.autoCompleteForceKey = None
        self.demoNextKey = None  # New support for the demo.py plugin.
        self.demoPrevKey = None  # New support for the demo.py plugin.
        # Used by k.masterKeyHandler...
        self.stroke: Stroke = None
        self.mb_event: Event = None
        self.mb_history: list[str] = []
        self.mb_help: bool = False
        self.mb_helpHandler: Callable = None
        # Important: these are defined in k.defineExternallyVisibleIvars...
            # self.getArgEscapes = []
            # self.getArgEscapeFlag
        # For onIdleTime...
        self.idleCount = 0
        # For modes...
        self.modeBindingsDict: dict = {}
        self.modeWidget = None
        self.silentMode = False
    #@+node:ekr.20080509064108.7: *5* k.defineMultiLineCommands
    def defineMultiLineCommands(self) -> None:
        k = self
        k.multiLineCommandList = [
            # EditCommandsClass
            'add-space-to-lines',
            'add-tab-to-lines',
            'back-page',
            'back-page-extend-selection',
            'back-paragraph',
            'back-paragraph-extend-selection',
            'back-sentence',
            'back-sentence-extend-selection',
            'backward-kill-paragraph',
            'beginning-of-buffer',
            'beginning-of-buffer-extend-selection',
            'center-line',
            'center-region',
            'clean-all-lines',
            'clean-lines',
            'downcase-region',
            'end-of-buffer',
            'end-of-buffer-extend-selection',
            'extend-to-paragraph',
            'extend-to-sentence',
            'fill-paragraph',
            'fill-region',
            'fill-region-as-paragraph',
            'flush-lines',
            'forward-page',
            'forward-page-extend-selection',
            'forward-paragraph',
            'forward-paragraph-extend-selection',
            'forward-sentence',
            'forward-sentence-extend-selection',
            'indent-relative',
            'indent-rigidly',
            'indent-to-comment-column',
            'move-lines-down',
            'move-lines-up',
            'next-line',
            'next-line-extend-selection',
            'previous-line',
            'previous-line-extend-selection',
            'remove-blank-lines',
            'remove-space-from-lines',
            'remove-tab-from-lines',
            'reverse-region',
            'reverse-sort-lines',
            'reverse-sort-lines-ignoring-case',
            'scroll-down-half-page',
            'scroll-down-line',
            'scroll-down-page',
            'scroll-up-half-page',
            'scroll-up-line',
            'scroll-up-page',
            'simulate-begin-drag',
            'simulate-end-drag',
            'sort-columns',
            'sort-fields',
            'sort-lines',
            'sort-lines-ignoring-case',
            'split-line',
            'tabify',
            'transpose-lines',
            'untabify',
            'upcase-region',
            # KeyHandlerCommandsClass
            'repeat-complex-command',
            # KillBufferCommandsClass
            'backward-kill-sentence',
            'kill-sentence',
            'kill-region',
            'kill-region-save',
            # QueryReplaceCommandsClass
            'query-replace',
            'query-replace-regex',
            # RectangleCommandsClass
            'clear-rectangle',
            'close-rectangle',
            'delete-rectangle',
            'kill-rectangle',
            'open-rectangle',
            'string-rectangle',
            'yank-rectangle',
            'change',
            'change-then-find',
            'find-next',
            'find-prev',
        ]
    #@+node:ekr.20080509064108.6: *5* k.defineSingleLineCommands
    def defineSingleLineCommands(self) -> None:
        k = self
        # These commands can be executed in the minibuffer.
        k.singleLineCommandList = [
            # EditCommandsClass
            'back-to-indentation',
            'back-to-home',  # 2010/02/01
            'back-char',
            'back-char-extend-selection',
            'back-word',
            'back-word-extend-selection',
            'backward-delete-char',
            'backward-find-character',
            'backward-find-character-extend-selection',
            'beginning-of-line',
            'beginning-of-line-extend-selection',
            'capitalize-word',
            'delete-char',
            'delete-indentation',
            'delete-spaces',
            'downcase-word',
            'end-of-line',
            'end-of-line-extend-selection',
            'escape',
            'exchange-point-mark',
            'extend-to-line',
            'extend-to-word',
            'find-character',
            'find-character-extend-selection',
            'find-word',
            'find-word-in-line',
            'forward-char',
            'forward-char-extend-selection',
            'forward-end-word',
            'forward-end-word-extend-selection',
            'forward-word',
            'forward-word-extend-selection',
            'insert-newline',
            'insert-parentheses',
            'move-past-close',
            'move-past-close-extend-selection',
            'newline-and-indent',
            'select-all',
            'transpose-chars',
            'transpose-words',
            'upcase-word',
            # LeoFind class.
            'start-search',  # #2041.
            # KeyHandlerCommandsClass
            'full-command',  # #2041.
            # 'auto-complete',
                # 'negative-argument',
                # 'number-command',
                # 'number-command-0',
                # 'number-command-1',
                # 'number-command-2',
                # 'number-command-3',
                # 'number-command-4',
                # 'number-command-5',
                # 'number-command-6',
                # 'number-command-7',
                # 'number-command-8',
                # 'universal-argument',
            # KillBufferCommandsClass
            'backward-kill-word',
            'kill-line',
            'kill-word',
            'kill-ws',
            'yank',
            'yank-pop',
            'zap-to-character',
            # leoCommands
            'cut-text',
            'copy-text',
            'paste-text',
            # MacroCommandsClass
            'call-last-kbd-macro',
            # search commands
            # 'replace-string', # A special case so Shift-Ctrl-r will work after Ctrl-f.
            'set-find-everywhere',  # 2011/06/07
            'set-find-node-only',  # 2011/06/07
            'set-find-suboutline-only',  # 2011/06/07
            'toggle-find-collapses_nodes',
            'toggle-find-ignore-case-option',
            'toggle-find-in-body-option',
            'toggle-find-in-headline-option',
            'toggle-find-mark-changes-option',
            'toggle-find-mark-finds-option',
            'toggle-find-regex-option',
            'toggle-find-reverse-option',
            'toggle-find-word-option',
            'toggle-find-wrap-around-option',
        ]
    #@+node:ekr.20061031131434.80: *4* k.finishCreate
    def finishCreate(self) -> None:
        """
        Complete the construction of the keyHandler class.
        c.commandsDict has been created when this is called.
        """
        c, k = self.c, self
        k.w = c.frame.miniBufferWidget  # Will be None for NullGui.
        k.fnc = FileNameChooser(c)  # A singleton. Defined here so that c.k will exist.
        k.getArgInstance = GetArg(c)  # A singleton. Defined here so that c.k will exist.
        # Important: This must be called this now,
        # even though LM.load calls g.app.makeAllBindings later.
        k.makeAllBindings()
        k.initCommandHistory()
        k.inited = True
        k.setDefaultInputState()
        k.resetLabel()
    #@+node:ekr.20120217070122.10479: *4* k.reloadSettings
    def reloadSettings(self) -> None:
        # Part 1: These were in the ctor.
        c = self.c
        getBool = c.config.getBool
        getColor = c.config.getColor
        self.enable_autocompleter = getBool('enable-autocompleter-initially')
        self.enable_calltips = getBool('enable-calltips-initially')
        self.ignore_unbound_non_ascii_keys = getBool('ignore-unbound-non-ascii-keys')
        self.minibuffer_background_color = getColor(
            'minibuffer-background-color') or 'lightblue'
        self.minibuffer_foreground_color = getColor(
            'minibuffer-foreground-color') or 'black'
        self.minibuffer_warning_color = getColor(
            'minibuffer-warning-color') or 'lightgrey'
        self.minibuffer_error_color = getColor('minibuffer-error-color') or 'red'
        self.replace_meta_with_alt = getBool('replace-meta-with-alt')
        self.warn_about_redefined_shortcuts = getBool('warn-about-redefined-shortcuts')
        # Has to be disabled (default) for AltGr support on Windows
        self.enable_alt_ctrl_bindings = c.config.getBool('enable-alt-ctrl-bindings')
        # Part 2: These were in finishCreate.
        # Set mode colors used by k.setInputState.
        bg = c.config.getColor('body-text-background-color') or 'white'
        fg = c.config.getColor('body-text-foreground-color') or 'black'
        self.command_mode_bg_color = getColor('command-mode-bg-color') or bg
        self.command_mode_fg_color = getColor('command-mode-fg-color') or fg
        self.insert_mode_bg_color = getColor('insert-mode-bg-color') or bg
        self.insert_mode_fg_color = getColor('insert-mode-fg-color') or fg
        self.overwrite_mode_bg_color = getColor('overwrite-mode-bg-color') or bg
        self.overwrite_mode_fg_color = getColor('overwrite-mode-fg-color') or fg
        self.unselected_body_bg_color = getColor('unselected-body-bg-color') or bg
        self.unselected_body_fg_color = getColor('unselected-body-fg-color') or bg
    #@+node:ekr.20110209093958.15413: *4* k.setDefaultEditingKeyAction
    def setDefaultEditingAction(self) -> None:
        c = self.c
        action = c.config.getString('default-editing-state') or 'insert'
        action.lower()
        if action not in ('command', 'insert', 'overwrite'):
            g.trace(f"ignoring default_editing_state: {action}")
            action = 'insert'
        self.defaultEditingAction = action
    #@+node:ekr.20061031131434.82: *4* k.setDefaultUnboundKeyAction
    def setDefaultUnboundKeyAction(self, allowCommandState: bool = True) -> None:
        c, k = self.c, self
        defaultAction = c.config.getString('top-level-unbound-key-action') or 'insert'
        defaultAction.lower()
        if defaultAction == 'command' and not allowCommandState:
            self.unboundKeyAction = 'insert'
        elif defaultAction in ('command', 'insert', 'overwrite'):
            self.unboundKeyAction = defaultAction
        else:
            g.trace(f"ignoring top_level_unbound_key_action setting: {defaultAction}")
            self.unboundKeyAction = 'insert'
        self.defaultUnboundKeyAction = self.unboundKeyAction
        k.setInputState(self.defaultUnboundKeyAction)
    #@+node:ekr.20061031131434.88: *3* k.Binding
    #@+node:ekr.20061031131434.89: *4* k.bindKey & helpers
    def bindKey(self,
        pane: str,
        shortcut: str,
        callback: Callable,
        commandName: str,
        modeFlag: bool = False,
        tag: str = None,
    ) -> bool:
        """
        Bind the indicated shortcut (a Tk keystroke) to the callback.

        No actual gui bindings are made: only entries in k.masterBindingsDict
        and k.bindingsDict.

        tag gives the source of the binding.

        Return True if the binding was made successfully.
        """
        k = self
        if not shortcut:
            # Don't use this method to undo bindings.
            return False
        if not k.check_bind_key(commandName, pane, shortcut):
            return False
        aList = k.bindingsDict.get(shortcut, [])
        stroke: Stroke
        try:
            if not shortcut:
                stroke = None
            elif g.isStroke(shortcut):
                stroke = shortcut
                assert stroke.s, stroke
            else:
                assert shortcut, g.callers()
                stroke = g.KeyStroke(binding=shortcut)
            bi = g.BindingInfo(
                kind=tag,
                pane=pane,
                func=callback,
                commandName=commandName,
                stroke=stroke)
            if shortcut:
                k.bindKeyToDict(pane, shortcut, bi)  # Updates k.masterBindingsDict
            if shortcut and not modeFlag:
                aList = k.remove_conflicting_definitions(
                    aList, commandName, pane, shortcut)
            else:
                aList = []
                # 2013/03/02: a real bug fix.
            aList.append(bi)
            if shortcut:
                assert stroke
                k.bindingsDict[stroke] = aList
            return True
        except Exception:  # Could be a user error.
            if g.unitTesting or not g.app.menuWarningsGiven:
                g.es_print('exception binding', shortcut, 'to', commandName)
                g.print_exception()
                g.app.menuWarningsGiven = True
            return False

    bindShortcut = bindKey  # For compatibility
    #@+node:ekr.20120130074511.10228: *5* k.check_bind_key
    def check_bind_key(self, commandName: str, pane: str, stroke: Stroke) -> bool:
        """
        Return True if the binding of stroke to commandName for the given
        pane can be made.
        """
        # k = self
        assert g.isStroke(stroke)
        # Give warning and return if we try to bind to Enter or Leave.
        for s in ('enter', 'leave'):
            if stroke.lower().find(s) > -1:
                g.warning('ignoring invalid key binding:', f"{commandName} = {stroke}")
                return False
        if pane.endswith('-mode'):
            g.trace('oops: ignoring mode binding', stroke, commandName, g.callers())
            return False
        return True
    #@+node:ekr.20120130074511.10227: *5* k.kill_one_shortcut
    def kill_one_shortcut(self, stroke: Stroke) -> None:
        """
        Update the *configuration* dicts so that c.config.getShortcut(name)
        will return None for all names *presently* bound to the stroke.
        """
        c = self.c
        lm = g.app.loadManager
        # A crucial shortcut: inverting and uninverting dictionaries is slow.
        # Important: the comparison is valid regardless of the type of stroke.
        if stroke in (None, 'None', 'none'):
            return
        assert g.isStroke(stroke), stroke
        inv_d = lm.invert(c.config.shortcutsDict)
        inv_d[stroke] = []
        c.config.shortcutsDict = lm.uninvert(inv_d)
    #@+node:ekr.20061031131434.92: *5* k.remove_conflicting_definitions
    def remove_conflicting_definitions(self,
        aList: list[str],
        commandName: str,
        pane: str,
        shortcut: str,
    ) -> list:

        k = self
        result = []
        for bi in aList:
            if pane in ('button', 'all', bi.pane):
                k.kill_one_shortcut(shortcut)
            else:
                result.append(bi)
        return result
    #@+node:ekr.20061031131434.93: *5* k.bindKeyToDict
    def bindKeyToDict(self, pane: str, stroke: Stroke, bi: Any) -> None:
        """Update k.masterBindingsDict for the stroke."""
        # New in Leo 4.4.1: Allow redefinitions.
        # Called from makeBindingsFromCommandsDict.
        k = self
        assert g.isStroke(stroke), stroke
        d = k.masterBindingsDict.get(pane, {})
        d[stroke] = bi
        k.masterBindingsDict[pane] = d
    #@+node:ekr.20061031131434.94: *5* k.bindOpenWith
    def bindOpenWith(self, d: dict[str, str]) -> None:
        """Register an open-with command."""
        c, k = self.c, self
        shortcut = d.get('shortcut') or ''
        name = d.get('name')
        # The first parameter must be event, and it must default to None.

        def openWithCallback(event: Event = None, c: Cmdr = c, d: dict = d) -> None:
            return c.openWith(d=d)

        # Use k.registerCommand to set the shortcuts in the various binding dicts.

        commandName = f"open-with-{name.lower()}"
        k.registerCommand(
            allowBinding=True,
            commandName=commandName,
            func=openWithCallback,
            pane='all',
            shortcut=shortcut,
        )
    #@+node:ekr.20061031131434.95: *4* k.checkBindings
    def checkBindings(self) -> None:
        """
        Print warnings if commands do not have any @shortcut entry.
        The entry may be `None`, of course."""
        c, k = self.c, self
        if not c.config.getBool('warn-about-missing-settings'):
            return
        for name in sorted(c.commandsDict):
            abbrev = k.abbreviationsDict.get(name)
            key = c.frame.menu.canonicalizeMenuName(abbrev or name)
            key = key.replace('&', '')
            if not c.config.exists(key, 'shortcut'):
                if abbrev:
                    g.trace(f"No shortcut for abbrev {name} -> {abbrev} = {key}")
                else:
                    g.trace(f"No shortcut for {name} = {key}")
    #@+node:ekr.20061031131434.97: *4* k.completeAllBindings
    def completeAllBindings(self, w: Wrapper = None) -> None:
        """
        Make an actual binding in *all* the standard places.

        The event will go to k.masterKeyHandler as always, so nothing really changes.
        except that k.masterKeyHandler will know the proper stroke.
        """
        k = self
        for stroke in k.bindingsDict:
            assert g.isStroke(stroke), repr(stroke)
            k.makeMasterGuiBinding(stroke, w=w)
    #@+node:ekr.20061031131434.96: *4* k.completeAllBindingsForWidget
    def completeAllBindingsForWidget(self, w: Wrapper) -> None:
        """Make all a master gui binding for widget w."""
        k = self
        for stroke in k.bindingsDict:
            assert g.isStroke(stroke), repr(stroke)
            k.makeMasterGuiBinding(stroke, w=w)
    #@+node:ekr.20070218130238: *4* k.dumpMasterBindingsDict
    def dumpMasterBindingsDict(self) -> None:
        """Dump k.masterBindingsDict."""
        k = self
        d = k.masterBindingsDict
        g.pr('\nk.masterBindingsDict...\n')
        for key in sorted(d):
            g.pr(key, '-' * 40)
            d2 = d.get(key)
            for key2 in sorted(d2):
                bi = d2.get(key2)
                g.pr(f"{key2:20} {bi.commandName}")
    #@+node:ekr.20061031131434.99: *4* k.initAbbrev & helper
    def initAbbrev(self) -> None:
        c = self.c
        d = c.config.getAbbrevDict()
        if d:
            for key in d:
                commandName = d.get(key)
                if commandName.startswith('press-') and commandName.endswith('-button'):
                    pass  # Must be done later in k.registerCommand.
                else:
                    self.initOneAbbrev(commandName, key)
    #@+node:ekr.20130924035029.12741: *5* k.initOneAbbrev
    def initOneAbbrev(self, commandName: str, key: str) -> None:
        """Enter key as an abbreviation for commandName in c.commandsDict."""
        c = self.c
        if c.commandsDict.get(key):
            g.trace('ignoring duplicate abbrev: %s', key)
        else:
            func = c.commandsDict.get(commandName)
            if func:
                c.commandsDict[key] = func
            else:
                g.warning('bad abbrev:', key, 'unknown command name:', commandName)
    #@+node:ekr.20061031131434.101: *4* k.initSpecialIvars
    def initSpecialIvars(self) -> None:
        """Set ivars for special keystrokes from previously-existing bindings."""
        c, k = self.c, self
        warn = c.config.getBool('warn-about-missing-settings')
        for ivar, commandName in (
            ('abortAllModesKey', 'keyboard-quit'),
            ('autoCompleteForceKey', 'auto-complete-force'),
            ('demoNextKey', 'demo-next'),
            ('demoPrevKey', 'demo-prev'),
        ):
            junk, aList = c.config.getShortcut(commandName)
            aList, found = aList or [], False
            for pane in ('text', 'all'):
                for bi in aList:
                    if bi.pane == pane:
                        setattr(k, ivar, bi.stroke)
                        found = True
                        break
            if not found and warn:
                g.trace(f"no setting for {commandName}")
    #@+node:ekr.20061031131434.98: *4* k.makeAllBindings
    def makeAllBindings(self) -> None:
        """Make all key bindings in all of Leo's panes."""
        k = self
        k.bindingsDict = {}
        k.addModeCommands()
        k.makeBindingsFromCommandsDict()
        k.initSpecialIvars()
        k.initAbbrev()
        k.completeAllBindings()
        k.checkBindings()
    #@+node:ekr.20061031131434.102: *4* k.makeBindingsFromCommandsDict
    def makeBindingsFromCommandsDict(self) -> None:
        """Add bindings for all entries in c.commandsDict."""
        c, k = self.c, self
        d = c.commandsDict
        # Step 1: Create d2.
        # Keys are strokes. Values are lists of bi with bi.stroke == stroke.
        d2: dict[g.KeyStroke, list[g.BindingInfo]] = g.SettingsDict('binding helper dict')
        for commandName in sorted(d):
            command = d.get(commandName)
            key, aList = c.config.getShortcut(commandName)
            for bi in aList:
                # Important: bi.stroke is already canonicalized.
                stroke = bi.stroke
                bi.commandName = commandName
                if stroke:
                    assert g.isStroke(stroke)
                    d2.add_to_list(stroke, bi)
        # Step 2: make the bindings.
        for stroke in sorted(d2.keys()):
            aList2 = d2.get(stroke)
            for bi in aList2:
                commandName = bi.commandName
                command = c.commandsDict.get(commandName)
                tag = bi.kind
                pane = bi.pane
                if stroke and not pane.endswith('-mode'):
                    k.bindKey(pane, stroke, command, commandName, tag=tag)
    #@+node:ekr.20061031131434.103: *4* k.makeMasterGuiBinding
    def makeMasterGuiBinding(self, stroke: Stroke, w: Wrapper = None) -> None:
        """Make a master gui binding for stroke in pane w, or in all the standard widgets."""
        c, k = self.c, self
        f = c.frame
        if w:
            widgets = [w]
        else:
            # New in Leo 4.5: we *must* make the binding in the binding widget.
            bindingWidget = (
                f.tree
                and hasattr(f.tree, 'bindingWidget')
                and f.tree.bindingWidget
                or None)
            wrapper = f.body and hasattr(f.body, 'wrapper') and f.body.wrapper or None
            canvas = f.tree and hasattr(f.tree, 'canvas') and f.tree.canvas or None
            widgets = [c.miniBufferWidget, wrapper, canvas, bindingWidget]
        aList: list
        for w in widgets:
            if not w:
                continue
            # Make the binding only if no binding for the stroke exists in the widget.
            aList = k.masterGuiBindingsDict.get(stroke, [])
            if w not in aList:
                aList.append(w)
                k.masterGuiBindingsDict[stroke] = aList
    #@+node:ekr.20150402111403.1: *3* k.Command history
    #@+node:ekr.20150402111413.1: *4* k.addToCommandHistory
    def addToCommandHistory(self, commandName: str) -> None:
        """Add a name to the command history."""
        k = self
        h = k.commandHistory
        if commandName in h:
            h.remove(commandName)
        h.append(commandName)
        k.commandIndex = None
    #@+node:ekr.20150402165918.1: *4* k.commandHistoryDown
    def commandHistoryFwd(self) -> None:
        """
        Move down the Command History - fall off the bottom (return empty string)
        if necessary
        """
        k = self
        h, i = k.commandHistory, k.commandIndex
        if h:
            commandName = ''
            if i == len(h) - 1:
                # fall off the bottom
                i = None
            elif i is not None:
                # move to next down in list
                i += 1
                commandName = h[i]
            k.commandIndex = i
            k.setLabel(k.mb_prefix + commandName)
    #@+node:ekr.20150402171131.1: *4* k.commandHistoryUp
    def commandHistoryBackwd(self) -> None:
        """
        Return the previous entry in the Command History - stay at the top
        if we are there
        """
        k = self
        h, i = k.commandHistory, k.commandIndex
        if h:
            if i is None:
                # first time in - set to last entry
                i = len(h) - 1
            elif i > 0:
                i -= 1
            commandName = h[i]
            k.commandIndex = i
            k.setLabel(k.mb_prefix + commandName)
    #@+node:ekr.20150425143043.1: *4* k.initCommandHistory
    def initCommandHistory(self) -> None:
        """Init command history from @data command-history nodes."""
        k, c = self, self.c
        aList = c.config.getData('history-list') or []
        for command in reversed(aList):
            k.addToCommandHistory(command)

    def resetCommandHistory(self) -> None:
        """ reset the command history index to indicate that
            we are pointing 'past' the last entry
        """
        self.commandIndex = None
    #@+node:ekr.20150402111935.1: *4* k.sortCommandHistory
    def sortCommandHistory(self) -> None:
        """Sort the command history."""
        k = self
        k.commandHistory.sort()
        k.commandIndex = None
    #@+node:ekr.20061031131434.104: *3* k.Dispatching
    #@+node:ekr.20061031131434.111: *4* k.fullCommand (alt-x) & helper
    @cmd('full-command')
    def fullCommand(
        self,
        event: Event,
        specialStroke: Stroke = None,
        specialFunc: Callable = None,
        help: bool = False,
        helpHandler: Callable = None,
    ) -> None:
        """Handle 'full-command' (alt-x) mode."""
        try:
            c, k = self.c, self
            state = k.getState('full-command')
            helpPrompt = 'Help for command: '
            c.check_event(event)
            ch = char = event.char if event else ''
            if state == 0:
                k.mb_event = event  # Save the full event for later.
                k.setState('full-command', 1, handler=k.fullCommand)
                prompt = helpPrompt if help else k.altX_prompt
                k.setLabelBlue(prompt)
                k.mb_help = help
                k.mb_helpHandler = helpHandler
                c.minibufferWantsFocus()
            elif char == 'Ins' or k.isFKey(char):
                pass
            elif char == 'Escape':
                k.keyboardQuit()
            elif char == 'Down':
                k.commandHistoryFwd()
            elif char == 'Up':
                k.commandHistoryBackwd()
            elif char in ('\n', 'Return'):
                # Fix bug 157: save and restore the selection.
                w = k.mb_event and k.mb_event.w
                if w and hasattr(w, 'hasSelection') and w.hasSelection():
                    sel1, sel2 = w.getSelectionRange()
                    ins = w.getInsertPoint()
                    c.frame.log.deleteTab('Completion')
                    w.setSelectionRange(sel1, sel2, insert=ins)
                else:
                    c.frame.log.deleteTab('Completion')  # 2016/04/27
                if k.mb_help:
                    s = k.getLabel()
                    commandName = s[len(helpPrompt) :].strip()
                    k.clearState()
                    k.resetLabel()
                    if k.mb_helpHandler:
                        k.mb_helpHandler(commandName)
                else:
                    s = k.getLabel(ignorePrompt=True)
                    commandName = s.strip()
                    ok = k.callAltXFunction(k.mb_event)
                    if ok:
                        k.addToCommandHistory(commandName)
            elif char in ('\t', 'Tab'):
                k.doTabCompletion(list(c.commandsDict.keys()))
                c.minibufferWantsFocus()
            elif char in ('\b', 'BackSpace'):
                k.doBackSpace(list(c.commandsDict.keys()))
                c.minibufferWantsFocus()
            elif k.ignore_unbound_non_ascii_keys and len(ch) > 1:
                if specialStroke:
                    g.trace(specialStroke)
                    specialFunc()
                c.minibufferWantsFocus()
            else:
                # Clear the list, any other character besides tab indicates that a new prefix is in effect.
                k.mb_tabList = []
                k.updateLabel(event)
                k.mb_tabListPrefix = k.getLabel()
                c.minibufferWantsFocus()
        except Exception:
            g.es_exception()
            self.keyboardQuit()
    #@+node:ekr.20061031131434.112: *5* k.callAltXFunction
    def callAltXFunction(self, event: Event) -> bool:
        """Call the function whose name is in the minibuffer."""
        c, k = self.c, self
        k.mb_tabList = []
        commandName, tail = k.getMinibufferCommandName()
        k.functionTail = tail
        if commandName and commandName.isdigit():
            # The line number Easter Egg.

            def func(event: Event = None) -> None:
                c.gotoCommands.find_file_line(n=int(commandName))

        else:
            func = c.commandsDict.get(commandName)
        if func:
            # These must be done *after* getting the command.
            k.clearState()
            k.resetLabel()
            if commandName != 'repeat-complex-command':
                k.mb_history.insert(0, commandName)
            w = event and event.widget
            if hasattr(w, 'permanent') and not w.permanent:
                # In a headline that is being edited.
                c.endEditing()
                c.bodyWantsFocusNow()
                # Change the event widget so we don't refer to the to-be-deleted headline widget.
                event.w = event.widget = c.frame.body.wrapper.widget
            else:
                c.widgetWantsFocusNow(event and event.widget)  # So cut-text works, e.g.
            try:
                func(event)
            except Exception:
                g.es_exception()
            return True
        # Show possible completions if the command does not exist.
        k.doTabCompletion(list(c.commandsDict.keys()))
        return False
    #@+node:ekr.20061031131434.114: *3* k.Externally visible commands
    #@+node:ekr.20070613133500: *4* k.menuCommandKey
    def menuCommandKey(self, event: Event = None) -> None:
        # This method must exist, but it never gets called.
        pass
    #@+node:ekr.20061031131434.119: *4* k.showBindings & helper
    @cmd('show-bindings')
    def showBindings(self, event: Event = None) -> list[str]:
        """Print all the bindings presently in effect."""
        c, k = self.c, self
        d = k.masterBindingsDict
        tabName = 'Bindings'
        c.frame.log.clearTab(tabName)
        legend = '''\
    legend:
    [ ] leoSettings.leo
    [D] default binding
    [F] loaded .leo File
    [M] myLeoSettings.leo
    [@] @mode, @button, @command

    '''
        if not d:
            g.es('no bindings')
            return None
        legend = textwrap.dedent(legend)
        data = []
        # d: keys are scope names. values are interior masterBindingDicts
        for scope in sorted(d):
            # d2: Keys are strokes; values are BindingInfo objects.
            d2 = d.get(scope, {})
            for stroke in d2:
                assert g.isStroke(stroke), stroke
                bi = d2.get(stroke)
                assert isinstance(bi, g.BindingInfo), repr(bi)
                # #2899: Adjust scope for @command and @button.
                if bi.commandName.startswith(('@button-', '@command-')):
                    scope = 'all'
                data.append((scope, k.prettyPrintKey(stroke), bi.commandName, bi.kind))
        # Print keys by type.
        result = []
        result.append('\n' + legend)
        for prefix in (
            'Alt+Ctrl+Shift', 'Alt+Ctrl', 'Alt+Shift', 'Alt',  # 'Alt+Key': done by Alt.
            'Ctrl+Meta+Shift', 'Ctrl+Meta', 'Ctrl+Shift', 'Ctrl',  # Ctrl+Key: done by Ctrl.
            'Meta+Key', 'Meta+Shift', 'Meta',
            'Shift',
            'F',  # #1972
            # Careful: longer prefixes must come before shorter prefixes.
        ):
            data2 = []
            for item in data:
                scope, stroke, commandName, kind = item
                if stroke.startswith(prefix):
                    data2.append(item)
            result.append(f"{prefix} keys...\n")
            self.printBindingsHelper(result, data2, prefix)
            # Remove all the items in data2 from data.
            # This must be done outside the iterator on data.
            for item in data2:
                data.remove(item)
        # Print all plain bindings.
        result.append('Plain keys...\n')
        self.printBindingsHelper(result, data, prefix=None)
        if not g.unitTesting:
            g.es_print('', ''.join(result), tabName=tabName)
        k.showStateAndMode()
        return result  # for unit test.
    #@+node:ekr.20061031131434.120: *5* printBindingsHelper
    def printBindingsHelper(self, result: list[str], data: list[Any], prefix: str) -> None:
        """Helper for k.showBindings"""
        c, lm = self.c, g.app.loadManager
        data.sort(key=lambda x: x[1])
        data2, n = [], 0
        for scope, key, commandName, kind in data:
            key = key.replace('+Key', '')
            letter = lm.computeBindingLetter(c, kind)
            pane = f"{scope if scope else 'all':>7}: "
            left = pane + key  # pane and shortcut fields
            n = max(n, len(left))
            data2.append((letter, left, commandName),)
        for z in data2:
            letter, left, commandName = z
            result.append('%s %*s %s\n' % (letter, -n, left, commandName))
        if data:
            result.append('\n')
    #@+node:ekr.20120520174745.9867: *4* k.printButtons
    @cmd('show-buttons')
    def printButtons(self, event: Event = None) -> None:
        """Print all @button and @command commands, their bindings and their source."""
        c = self.c
        tabName = '@buttons && @commands'
        c.frame.log.clearTab(tabName)

        def put(s: str) -> None:
            g.es('', s, tabName=tabName)

        data = []
        for aList in [c.config.getButtons(), c.config.getCommands()]:
            for z in aList:
                try:  # #2536.
                    p, script = z  # getCommands created the tuple.
                except ValueError:
                    p, script, rclicks = z  # getButtons created the tuple.
                c = p.v.context
                tag = 'M' if c.shortFileName().endswith('myLeoSettings.leo') else 'G'
                data.append((p.h, tag),)
        for aList in [g.app.config.atLocalButtonsList, g.app.config.atLocalCommandsList]:
            for p in aList:
                data.append((p.h, 'L'),)
        result = [f"{z[1]} {z[0]}" for z in sorted(data)]
        result.extend([
            '',
            'legend:',
            'G leoSettings.leo',
            'L local .leo File',
            'M myLeoSettings.leo',
        ])
        put('\n'.join(result))
    #@+node:ekr.20061031131434.121: *4* k.printCommands
    @cmd('show-commands')
    def printCommands(self, event: Event = None) -> None:
        """Print all the known commands and their bindings, if any."""
        c, k = self.c, self
        tabName = 'Commands'
        c.frame.log.clearTab(tabName)
        inverseBindingDict = k.computeInverseBindingDict()
        data, n = [], 0
        dataList: list[tuple[str, str]]
        for commandName in sorted(c.commandsDict):
            dataList = inverseBindingDict.get(commandName, [('', ''),])
            for z in dataList:
                pane, stroke = z
                pane_s = ' ' * 8 if pane in ('', 'all') else f"{pane:>7}:"
                key = k.prettyPrintKey(stroke).replace('+Key', '')
                pane_key = f"{pane_s}{key}"
                n = max(n, len(pane_key))
                data.append((pane_key, commandName))
        # This isn't perfect in variable-width fonts.
        lines = ['%*s %s\n' % (-n, z1, z2) for z1, z2 in data]
        g.es_print('', ''.join(lines), tabName=tabName)
    #@+node:tom.20220320235059.1: *4* k.printCommandsWithDocs
    @cmd('show-commands-with-docs')
    def printCommandsWithDocs(self, event: Event = None) -> None:
        """Show all the known commands and their bindings, if any."""
        c, k = self.c, self
        tabName = 'List'
        c.frame.log.clearTab(tabName)
        inverseBindingDict = k.computeInverseBindingDict()
        data = []
        key: str
        dataList: list[tuple[str, str]]
        for commandName in sorted(c.commandsDict):
            dataList = inverseBindingDict.get(commandName, [('', ''),])
            for pane, key in dataList:
                key = k.prettyPrintKey(key)
                binding = pane + key
                cmd = commandName.strip()
                doc = f'{c.commandsDict.get(commandName).__doc__}' or ''
                if doc == 'None':
                    doc = ''
                # Formatting for multi-line docstring
                if doc.count('\n') > 0:
                    doc = f'\n{doc}\n'
                else:
                    doc = f'   {doc}'
                if doc.startswith('\n'):
                    doc.replace('\n', '', 1)
                toolong = doc.count('\n') > 5
                manylines = False
                if toolong:
                    lines = doc.split('\n')[:4]
                    lines[-1] += ' ...\n'
                    doc = '\n'.join(lines)
                    manylines = True
                n = min(2, len(binding))
                if manylines:
                    doc = textwrap.fill(doc, width=50, initial_indent=' ' * 4,
                            subsequent_indent=' ' * 4)
                data.append((binding, cmd, doc))
        lines = ['[%*s] %s%s\n' % (-n, binding, cmd, doc) for binding, cmd, doc in data]
        g.es(''.join(lines), tabName=tabName)
    #@+node:ekr.20061031131434.122: *4* k.repeatComplexCommand
    @cmd('repeat-complex-command')
    def repeatComplexCommand(self, event: Event) -> None:
        """Repeat the previously executed minibuffer command."""
        k = self
        # #2286: Always call k.fullCommand.
        k.setState('getArg', 0, handler=k.fullCommand)
        k.fullCommand(event)  # #2334
        if not k.mb_history:
            k.mb_history = list(reversed(k.commandHistory))
        command = k.mb_history[0] if k.mb_history else ''
        k.setLabelBlue(f"{k.altX_prompt}", protect=True)
        k.extendLabel(command, select=False, protect=False)
    #@+node:ekr.20061031131434.123: *4* k.set-xxx-State
    @cmd('set-command-state')
    def setCommandState(self, event: Event) -> None:
        """Enter the 'command' editing state."""
        k = self
        k.setInputState('command', set_border=True)
        # This command is also valid in headlines.
            # k.c.bodyWantsFocus()
        k.showStateAndMode()

    @cmd('set-insert-state')
    def setInsertState(self, event: Event) -> None:
        """Enter the 'insert' editing state."""
        k = self
        k.setInputState('insert', set_border=True)
        # This command is also valid in headlines.
            # k.c.bodyWantsFocus()
        k.showStateAndMode()

    @cmd('set-overwrite-state')
    def setOverwriteState(self, event: Event) -> None:
        """Enter the 'overwrite' editing state."""
        k = self
        k.setInputState('overwrite', set_border=True)
        # This command is also valid in headlines.
            # k.c.bodyWantsFocus()
        k.showStateAndMode()
    #@+node:ekr.20061031131434.124: *4* k.toggle-input-state
    @cmd('toggle-input-state')
    def toggleInputState(self, event: Event = None) -> None:
        """The toggle-input-state command."""
        c, k = self.c, self
        default = c.config.getString('top-level-unbound-key-action') or 'insert'
        state = k.unboundKeyAction
        if default == 'insert':
            state = 'command' if state == 'insert' else 'insert'
        elif default == 'overwrite':
            state = 'command' if state == 'overwrite' else 'overwrite'
        else:
            state = 'insert' if state == 'command' else 'command'  # prefer insert to overwrite.
        k.setInputState(state)
        k.showStateAndMode()
    #@+node:ekr.20061031131434.125: *3* k.Externally visible helpers
    #@+node:ekr.20140816165728.18968: *4* Wrappers for GetArg methods
    # New in Leo 5.4

    def getNextArg(self, handler: Callable) -> None:
        """
        Get the next arg.  For example, after a Tab in the find commands.
        See the docstring for k.get1Arg for examples of its use.
        """
        # Replace the current handler.
        self.getArgInstance.after_get_arg_state = ('getarg', 1, handler)
        self.c.minibufferWantsFocusNow()

    # New in Leo 5.4

    def get1Arg(
        self,
        event: Event,
        handler: Callable,
        prefix: str = None,
        tabList: list[str] = None,
        completion: bool = True,
        oneCharacter: bool = False,
        stroke: Stroke = None,
        useMinibuffer: bool = True,
    ) -> None:
        #@+<< docstring for k.get1arg >>
        #@+node:ekr.20161020031633.1: *5* << docstring for k.get1arg >>
        """
        k.get1Arg: Handle the next character the user types when accumulating
        a user argument from the minibuffer. Ctrl-G will abort this processing
        at any time.

        Commands should use k.get1Arg to get the first minibuffer argument and
        k.getNextArg to get all other arguments.

        Before going into the many details, let's look at some examples. This
        code will work in any class having a 'c' ivar bound to a commander.

        Example 1: get one argument from the user:

            @g.command('my-command')
            def myCommand(self, event: Event) -> None:
                k = self.c.k
                k.setLabelBlue('prompt: ')
                k.get1Arg(event, handler=self.myCommand1)

            def myCommand1(self, event: Event) -> None:
                k = self.c.k
                # k.arg contains the argument.
                # Finish the command.
                ...
                # Reset the minibuffer.
                k.clearState()
                k.resetLabel()
                k.showStateAndMode()

        Example 2: get two arguments from the user:

            @g.command('my-command')
            def myCommand(self, event: Event) -> None:
                k = self.c.k
                k.setLabelBlue('first prompt: ')
                k.get1Arg(event, handler=self.myCommand1)

            def myCommand1(self, event: Event) -> None:
                k = self.c.k
                self.arg1 = k.arg
                k.extendLabel(' second prompt: ', select=False, protect=True)
                k.getNextArg(handler=self.myCommand2)

            def myCommand2(self, event: Event) -> None:
                k = self.c.k
                # k.arg contains second argument.
                # Finish the command, using self.arg1 and k.arg.
                ...
                # Reset the minibuffer.
                k.clearState()
                k.resetLabel()
                k.showStateAndMode()

        k.get1Arg and k.getNextArg are a convenience methods. They simply pass
        their arguments to the get_arg method of the singleton GetArg
        instance. This docstring describes k.get1arg and k.getNextArg as if
        they were the corresponding methods of the GetArg class.

        k.get1Arg is a state machine. Logically, states are tuples (kind, n,
        handler) though they aren't represented that way. When the state
        machine in the GetArg class is active, the kind is 'getArg'. This
        constant has special meaning to Leo's key-handling code.

        The arguments to k.get1Arg are as follows:

        event:              The event passed to the command.

        handler=None,       An executable. k.get1arg calls handler(event)
                            when the user completes the argument by typing
                            <Return> or (sometimes) <tab>.

        tabList=[]:         A list of possible completions.

        completion=True:    True if completions are enabled.

        oneCharacter=False: True if k.arg should be a single character.

        stroke=None:        The incoming key stroke.

        useMinibuffer=True: True: put focus in the minibuffer while accumulating arguments.
                            False allows sort-lines, for example, to show the selection range.

        """
        #@-<< docstring for k.get1arg >>
        returnKind, returnState = None, None
        assert handler, g.callers()
        self.getArgInstance.get_arg(event, returnKind, returnState, handler,
            tabList, completion, oneCharacter, stroke, useMinibuffer)

    def getArg(
        self,
        event: Event,
        returnKind: str = None,
        returnState: int = None,
        handler: Callable = None,
        prefix: str = None,
        tabList: list[str] = None,
        completion: bool = True,
        oneCharacter: bool = False,
        stroke: Stroke = None,
        useMinibuffer: bool = True,
    ) -> None:
        """Convenience method mapping k.getArg to ga.get_arg."""
        self.getArgInstance.get_arg(event, returnKind, returnState, handler,
            tabList, completion, oneCharacter, stroke, useMinibuffer)

    def doBackSpace(self, tabList: list[str], completion: bool = True) -> None:
        """Convenience method mapping k.doBackSpace to ga.do_back_space."""
        self.getArgInstance.do_back_space(tabList, completion)

    def doTabCompletion(self, tabList: list[str]) -> None:
        """Convenience method mapping k.doTabCompletion to ga.do_tab."""
        self.getArgInstance.do_tab(tabList)

    def getMinibufferCommandName(self) -> tuple[str, str]:
        """
        Convenience method mapping k.getMinibufferCommandName to
        ga.get_minibuffer_command_name.
        """
        return self.getArgInstance.get_minibuffer_command_name()
    #@+node:ekr.20061031131434.130: *4* k.keyboardQuit
    @cmd('keyboard-quit')
    def keyboardQuit(self, event: Event = None, setFocus: bool = True) -> None:
        """Clears the state and the minibuffer label."""
        c, k = self.c, self
        ac = k.autoCompleter
        if g.app.quitting:
            return
        c.endEditing()
        # Completely clear the mode.
        if setFocus:
            c.frame.log.deleteTab('Mode')
            c.frame.log.hideTab('Completion')
            if ac:
                c.frame.log.deleteTab(ac.tabName)
        if k.inputModeName:
            k.endMode()
        # Complete clear the state.
        k.state.kind = None
        k.state.n = None
        k.clearState()
        k.resetLabel()
        if setFocus:
            c.bodyWantsFocus()
        # At present, only the auto-completer suppresses this.
        k.setDefaultInputState()
        if c.vim_mode and c.vimCommands:
            c.vimCommands.reset(setFocus=setFocus)
        else:
            # This was what caused the unwanted scrolling.
            k.showStateAndMode(setFocus=setFocus)
        k.resetCommandHistory()
    #@+node:ekr.20061031131434.126: *4* k.manufactureKeyPressForCommandName (only for unit tests!)
    def manufactureKeyPressForCommandName(self, w: Wrapper, commandName: str) -> None:
        """
        Implement a command by passing a keypress to the gui.

        **Only unit tests use this method.**
        """
        c, k = self.c, self
        # Unit tests do not ordinarily read settings files.
        stroke = k.getStrokeForCommandName(commandName)
        if stroke is None:
            # Create the stroke and binding info data.
            stroke = g.KeyStroke('Ctrl+F1')
            bi = g.BindingInfo(
                kind='manufactured-binding',
                commandName=commandName,
                func=None,
                pane='all',
                stroke=stroke,
            )
            # Make the binding!
            # k.masterBindingsDict keys: scope names; values: masterBindingDicts (3)
            # Interior masterBindingDicts: Keys are strokes; values are BindingInfo objects.
            d = k.masterBindingsDict
            d2 = d.get('all', {})
            d2[stroke] = bi
            d['all'] = d2
        assert g.isStroke(stroke), (commandName, stroke.__class__.__name__)
        shortcut = stroke.s
        shortcut = g.checkUnicode(shortcut)
        if shortcut and w:
            g.app.gui.set_focus(c, w)
            g.app.gui.event_generate(c, None, shortcut, w)
        else:
            message = f"no shortcut for {commandName}"
            if g.unitTesting:
                raise AttributeError(message)
            g.error(message)
    #@+node:ekr.20071212104050: *4* k.overrideCommand
    def overrideCommand(self, commandName: str, func: Callable) -> None:
        # Override entries in c.k.masterBindingsDict
        k = self
        d = k.masterBindingsDict
        for key in d:
            d2 = d.get(key)
            for key2 in d2:
                bi = d2.get(key2)
                if bi.commandName == commandName:
                    bi.func = func
                    d2[key2] = bi
    #@+node:ekr.20061031131434.131: *4* k.registerCommand
    def registerCommand(
        self,
        commandName: str,
        func: Callable,
        allowBinding: bool = False,
        pane: str = 'all',
        shortcut: str = None,  # Must be None unless allowBindings is True.
        **kwargs: Any,  # Used only to warn about deprecated kwargs.
    ) -> None:
        """
        Make the function available as a minibuffer command.

        You can wrap any method in a callback function, so the
        restriction to functions is not significant.

        Ignore the 'shortcut' arg unless 'allowBinding' is True.

        Only k.bindOpenWith and the mod_scripting.py plugin should set
        allowBinding.
        """
        c, k = self.c, self
        if not func:
            g.es_print('Null func passed to k.registerCommand\n', commandName)
            return
        f = c.commandsDict.get(commandName)
        if f and f.__name__ != func.__name__:
            g.trace('redefining', commandName, f, '->', func)
        c.commandsDict[commandName] = func
        # Warn about deprecated arguments.
        if shortcut and not allowBinding:
            g.es_print('The "shortcut" keyword arg to k.registerCommand will be ignored')
            g.es_print('Called from', g.callers())
            shortcut = None
        for arg, val in kwargs.items():
            if val is not None:
                g.es_print(f'The "{arg}" keyword arg to k.registerCommand is deprecated')
                g.es_print('Called from', g.callers())
        # Make requested bindings, even if a warning has been given.
        # This maintains strict compatibility with existing plugins and scripts.
        k.registerCommandShortcut(
            commandName=commandName,
            func=func,
            pane=pane,
            shortcut=shortcut,
        )
    #@+node:ekr.20171124043747.1: *4* k.registerCommandShortcut
    def registerCommandShortcut(self,
        commandName: str,
        func: Callable,
        pane: str,
        shortcut: str,
    ) -> None:
        """
        Register a shortcut for the a command.

        **Important**: Bindings created here from plugins can not be overridden.
        This includes @command and @button bindings created by mod_scripting.py.
        """
        c, k = self.c, self
        is_local = c.shortFileName() not in ('myLeoSettings.leo', 'leoSettings.leo')
        assert not g.isStroke(shortcut)
        stroke: Stroke
        if shortcut:
            stroke = g.KeyStroke(binding=shortcut) if shortcut else None
        elif commandName.lower() == 'shortcut':  # Causes problems.
            stroke = None
        elif is_local:
            # 327: Don't get defaults when handling a local file.
            stroke = None
        else:
            # Try to get a stroke from leoSettings.leo.
            stroke = None
            junk, aList = c.config.getShortcut(commandName)
            for bi in aList:
                if bi.stroke and not bi.pane.endswith('-mode'):
                    stroke = bi.stroke
                    pane = bi.pane  # 2015/05/11.
                    break
        if stroke:
            k.bindKey(pane, stroke, func, commandName, tag=f"register-command:{c.shortFileName()}")
            k.makeMasterGuiBinding(stroke)  # Must be a stroke.
        # Fixup any previous abbreviation to press-x-button commands.
        if commandName.startswith('press-') and commandName.endswith('-button'):
            d = c.config.getAbbrevDict()  # Keys are full command names, values are abbreviations.
            if commandName in list(d.values()):
                for key in d:
                    if d.get(key) == commandName:
                        c.commandsDict[key] = c.commandsDict.get(commandName)
                        break
    #@+node:ekr.20061031131434.127: *4* k.simulateCommand
    def simulateCommand(self, commandName: str, event: Event = None) -> Any:
        """
        Execute a Leo command by name.

        This method is deprecated: Use c.doCommandByName instead.

        This method will be retained for compatibility with existing scripts.
        """
        c = self.c
        return c.doCommandByName(commandName, event)
    #@+node:ekr.20140813052702.18203: *4* k.getFileName
    def getFileName(
        self,
        event: Event,
        callback: Callable = None,
        filterExt: list[str] = None,
        prompt: str = 'Enter File Name: ',
        tabName: str = 'Dired',
    ) -> None:
        """Get a file name from the minibuffer."""
        k = self
        k.fnc.get_file_name(event, callback, filterExt, prompt, tabName)
    #@+node:ekr.20061031131434.145: *3* k.Master event handlers
    #@+node:ekr.20061031131434.146: *4* k.masterKeyHandler & helpers
    def masterKeyHandler(self, event: Event) -> None:
        """The master key handler for almost all key bindings."""
        trace = 'keys' in g.app.debug
        c, k = self.c, self
        # Setup...
        if trace:
            handler_s = f"{k.state.handler.__name__}" if k.state.handler else 'No handler'
            g.trace(
                f"char: {event.char!r} stroke: {event.stroke!r} "
                f"state.kind: {k.state.kind!r}, state.handler: {handler_s}")
        k.checkKeyEvent(event)
        k.setEventWidget(event)
        k.traceVars(event)
        # Order is very important here...
        if k.isSpecialKey(event):
            return
        if k.doKeyboardQuit(event):
            return
        if k.doDemo(event):
            return
        if k.doMode(event):
            return
        if k.doVim(event):
            return
        if k.doBinding(event):
            return
        # Handle abbreviations.
        if k.abbrevOn and c.abbrevCommands.expandAbbrev(event, event.stroke):
            return
        # Handle the character given by event *without*
        # executing any command that might be bound to it.
        c.insertCharFromEvent(event)
    #@+node:ekr.20200524151214.1: *5* Setup...
    #@+node:ekr.20180418040158.1: *6* k.checkKeyEvent
    def checkKeyEvent(self, event: Event) -> None:
        """Perform sanity checks on the incoming event."""
        # These assert's should be safe, because eventFilter
        # calls k.masterKeyHandler inside a try/except block.
        c = self.c
        assert event is not None
        c.check_event(event)
        assert hasattr(event, 'char')
        assert hasattr(event, 'stroke')
        if not hasattr(event, 'widget'):
            event.widget = None
        assert g.isStrokeOrNone(event.stroke)
        if event:
            # A continuous unit test, better than "@test k.isPlainKey".
            assert event.stroke.s not in g.app.gui.ignoreChars, repr(event.stroke.s)
    #@+node:ekr.20180418034305.1: *6* k.setEventWidget
    def setEventWidget(self, event: Event) -> None:
        """
        A hack: redirect the event to the text part of the log.
        """
        c = self.c
        w = event.widget
        w_name = c.widget_name(w)
        if w_name.startswith('log'):
            event.widget = c.frame.log.logCtrl
    #@+node:ekr.20180418031417.1: *6* k.traceVars
    def traceVars(self, event: Event) -> None:

        trace = False and not g.unitTesting
        if not trace:
            return
        k = self
        char = event.char
        state = k.state.kind
        stroke = event.stroke
        g.trace(
            f"stroke: {stroke!r}, "
            f"char: {char!r}, "
            f"state: {state}, "
            f"state2: {k.unboundKeyAction}")
    #@+node:ekr.20180418031118.1: *5* 1. k.isSpecialKey
    def isSpecialKey(self, event: Event) -> bool:
        """Return True if char is a special key."""
        if not event:
            # An empty event is not an error.
            return False
        # Fix #917.
        if len(event.char) > 1 and not event.stroke.s:
            # stroke.s was cleared, but not event.char.
            return True
        return event.char in g.app.gui.ignoreChars
    #@+node:ekr.20180418024449.1: *5* 2. k.doKeyboardQuit
    def doKeyboardQuit(self, event: Event) -> bool:
        """
        A helper for k.masterKeyHandler: Handle keyboard-quit logic.

        return True if k.masterKeyHandler should return.
        """
        c, k = self.c, self
        stroke = getattr(event, 'stroke', None)
        if k.abortAllModesKey and stroke and stroke == k.abortAllModesKey:
            if getattr(c, 'screenCastController', None):
                c.screenCastController.quit()
            c.doCommandByName('keyboard-quit', event)
            return True
        return False
    #@+node:ekr.20180418023827.1: *5* 3. k.doDemo
    def doDemo(self, event: Event) -> bool:
        """
        Support the demo.py plugin.
        Return True if k.masterKeyHandler should return.
        """
        k = self
        stroke = event.stroke
        demo = getattr(g.app, 'demo', None)
        if not demo:
            return False
        #
        # Shortcut everything so that demo-next or demo-prev won't alter of our ivars.
        if k.demoNextKey and stroke == k.demoNextKey:
            if demo.trace:
                g.trace('demo-next', stroke)
            demo.next_command()
            return True
        if k.demoPrevKey and stroke == k.demoPrevKey:
            if demo.trace:
                g.trace('demo-prev', stroke)
            demo.prev_command()
            return True
        return False
    #@+node:ekr.20091230094319.6244: *5* 4. k.doMode & helpers
    def doMode(self, event: Event) -> bool:
        """
        Handle mode bindings.
        Return True if k.masterKeyHandler should return.
        """
        # #1757: Leo's default vim bindings make heavy use of modes.
        #        Retain these traces!
        trace = 'keys' in g.app.debug
        k = self
        state = k.state.kind
        stroke = event.stroke
        if not k.inState():
            return False
        # First, honor minibuffer bindings for all except user modes.
        if state == 'input-shortcut':
            k.handleInputShortcut(event, stroke)
            if trace:
                g.trace(state, 'k.handleInputShortcut', stroke)
            return True
        if state in (
            'getArg', 'getFileName', 'full-command', 'auto-complete', 'vim-mode'
        ):
            if k.handleMiniBindings(event, state, stroke):
                if trace:
                    g.trace(state, 'k.handleMiniBindings', stroke)
                return True
        # Second, honor general modes.
        if state == 'getArg':
            # New in Leo 5.8: Only call k.getArg for keys it can handle.
            if k.isPlainKey(stroke):
                k.getArg(event, stroke=stroke)
                if trace:
                    g.trace(state, 'k.isPlain: getArg', stroke)
                return True
            if stroke.s in ('Escape', 'Tab', 'BackSpace'):
                k.getArg(event, stroke=stroke)
                if trace:
                    g.trace(state, f"{stroke.s!r}: getArg", stroke)
                return True
            return False
        if state in ('getFileName', 'get-file-name'):
            k.getFileName(event)
            if trace:
                g.trace(state, 'k.getFileName', stroke)
            return True
        if state in ('full-command', 'auto-complete'):
            # Do the default state action. Calls end-command.
            val = k.callStateFunction(event)
            if val != 'do-standard-keys':
                handler = k.state.handler and k.state.handler.__name__ or '<no handler>'
                if trace:
                    g.trace(state, 'k.callStateFunction:', handler, stroke)
                return True
            return False
        # Third, pass keys to user modes.
        d = k.masterBindingsDict.get(state)
        if d:
            assert g.isStrokeOrNone(stroke)
            bi = d.get(stroke)
            if bi:
                # Bound keys continue the mode.
                k.generalModeHandler(event,
                    commandName=bi.commandName,
                    func=bi.func,
                    modeName=state,
                    nextMode=bi.nextMode)
                if trace:
                    g.trace(state, 'k.generalModeHandler', stroke)
                return True
            # Unbound keys end mode.
            if trace:
                g.trace(state, stroke, 'no binding')
            k.endMode()
            return False
        # Fourth, call the state handler.
        handler = k.getStateHandler()
        if handler:
            handler(event)
        if trace:
            handler_name = handler and handler.__name__ or '<no handler>'
            g.trace(state, 'handler:', handler_name, stroke)
        return True
    #@+node:ekr.20061031131434.108: *6* k.callStateFunction
    def callStateFunction(self, event: Event) -> Any:
        """Call the state handler associated with this event."""
        k = self
        ch = event.char
        #
        # Defensive programming
        if not k.state.kind:
            return None
        if not k.state.handler:
            g.error('callStateFunction: no state function for', k.state.kind)
            return None
        #
        # Handle auto-completion before checking for unbound keys.
        if k.state.kind == 'auto-complete':
            # k.auto_completer_state_handler returns 'do-standard-keys' for control keys.
            val = k.state.handler(event)
            return val
        #
        # Ignore unbound non-ascii keys.
        if (
            k.ignore_unbound_non_ascii_keys and
            len(ch) == 1 and
            ch and ch not in ('\b', '\n', '\r', '\t') and
            (ord(ch) < 32 or ord(ch) > 128)
        ):
            return None
        #
        # Call the state handler.
        val = k.state.handler(event)
        return val
    #@+node:ekr.20061031131434.152: *6* k.handleMiniBindings
    def handleMiniBindings(self, event: Event, state: str, stroke: Stroke) -> bool:
        """Find and execute commands bound to the event."""
        k = self
        #
        # Special case for bindings handled in k.getArg:
        if state == 'full-command' and stroke in ('Up', 'Down'):
            return False
        #
        # Ignore other special keys in the minibuffer.
        if state in ('getArg', 'full-command'):
            if stroke in (
                '\b', 'BackSpace',
                '\r', 'Linefeed',
                '\n', 'Return',
                '\t', 'Tab',
                'Escape',
            ):
                return False
            if k.isFKey(stroke):
                return False
        #
        # Ignore autocompletion state.
        if state.startswith('auto-'):
            return False
        #
        # Ignore plain key binding in the minibuffer.
        if not stroke or k.isPlainKey(stroke):
            return False
        #
        # Get the command, based on the pane.
        for pane in ('mini', 'all', 'text'):
            result = k.handleMinibufferHelper(event, pane, state, stroke)
            assert result in ('continue', 'found', 'ignore')
            if result == 'ignore':
                return False  # Let getArg handle it.
            if result == 'found':
                # Do not call k.keyboardQuit here!
                return True
        #
        # No binding exists.
        return False
    #@+node:ekr.20180418114300.1: *7* k.handleMinibufferHelper
    def handleMinibufferHelper(self, event: Event, pane: str, state: str, stroke: Stroke) -> str:
        """
        Execute a pane binding in the minibuffer.
        Return 'continue', 'ignore', 'found'
        """
        c, k = self.c, self
        d = k.masterBindingsDict.get(pane)
        if not d:
            return 'continue'
        bi = d.get(stroke)
        if not bi:
            return 'continue'
        assert bi.stroke == stroke, f"bi: {bi} stroke: {stroke}"
        # Ignore the replace-string command in the minibuffer.
        if bi.commandName == 'replace-string' and state == 'getArg':
            return 'ignore'
        # Execute this command.
        if bi.commandName not in k.singleLineCommandList:
            k.keyboardQuit()
        else:
            c.minibufferWantsFocus()
            c.doCommandByName(bi.commandName, event)
        # Careful: the command could exit.
        if c.exists and not k.silentMode:
            # Use the state *after* executing the command.
            if k.state.kind:
                c.minibufferWantsFocus()
            else:
                c.bodyWantsFocus()
        return 'found'
    #@+node:vitalije.20170708161511.1: *6* k.handleInputShortcut
    def handleInputShortcut(self, event: Event, stroke: Stroke) -> None:
        c, k, p, u = self.c, self, self.c.p, self.c.undoer
        k.clearState()
        if p.h.startswith(('@shortcuts', '@mode')):
            # line of text in body
            w = c.frame.body.wrapper
            before, sel, after = w.getInsertLines()
            m = k._cmd_handle_input_pattern.search(sel)
            assert m  # edit-shortcut was invoked on a malformed body line
            sel = f"{m.group(0)} {stroke.s}"
            udata = u.beforeChangeNodeContents(p)
            pos = w.getYScrollPosition()
            i = len(before)
            j = max(i, len(before) + len(sel) - 1)
            w.setAllText(before + sel + after)
            w.setSelectionRange(i, j, insert=j)
            w.setYScrollPosition(pos)
            u.afterChangeNodeContents(p, 'change shortcut', udata)
            cmdname = m.group(0).rstrip('= ')
            k.editShortcut_do_bind_helper(stroke, cmdname)
            return
        if p.h.startswith(('@command', '@button')):
            udata = u.beforeChangeNodeContents(p)
            cmd = p.h.split('@key', 1)[0]
            p.h = f"{cmd} @key={stroke.s}"
            u.afterChangeNodeContents(p, 'change shortcut', udata)
            try:
                cmdname = cmd.split(' ', 1)[1].strip()
                k.editShortcut_do_bind_helper(stroke, cmdname)
            except IndexError:
                pass
            return
        # this should never happen
        g.error('not in settings node shortcut')
    #@+node:vitalije.20170709151653.1: *7* k.isInShortcutBodyLine
    _cmd_handle_input_pattern = re.compile(r'[A-Za-z0-9_\-]+\s*=')

    def isInShortcutBodyLine(self) -> bool:
        c, k = self.c, self
        p = c.p
        if p.h.startswith(('@shortcuts', '@mode')):
            # line of text in body
            w = c.frame.body
            before, sel, after = w.getInsertLines()
            m = k._cmd_handle_input_pattern.search(sel)
            return bool(m)
        return p.h.startswith(('@command', '@button'))
    #@+node:vitalije.20170709151658.1: *7* k.isEditShortcutSensible
    def isEditShortcutSensible(self) -> bool:
        c, k = self.c, self
        p = c.p
        return p.h.startswith(('@command', '@button')) or k.isInShortcutBodyLine()
    #@+node:vitalije.20170709202924.1: *7* k.editShortcut_do_bind_helper
    def editShortcut_do_bind_helper(self, stroke: Stroke, cmdname: str) -> None:
        c, k = self.c, self
        cmdfunc = c.commandsDict.get(cmdname)
        if cmdfunc:
            k.bindKey('all', stroke, cmdfunc, cmdname)
            g.es('bound', stroke, 'to command', cmdname)
    #@+node:ekr.20180418025241.1: *5* 5. k.doVim
    def doVim(self, event: Event) -> bool:
        """
        Handle vim mode.
        Return True if k.masterKeyHandler should return.
        """
        trace = all(z in g.app.debug for z in ('keys', 'verbose'))
        c = self.c
        if c.vim_mode and c.vimCommands:
            # The "acceptance methods" in leoVim.py return True
            # if vim node has completely handled the key.
            # Otherwise, processing in k.masterKeyHandler continues.
            ok = c.vimCommands.do_key(event)
            if trace:
                g.trace('do_key returns', ok, repr(event and event.stroke))
            return ok
        return False
    #@+node:ekr.20180418033838.1: *5* 6. k.doBinding & helpers
    def doBinding(self, event: Event) -> bool:
        """
        Attempt to find a binding for the event's stroke.
        If found, execute the command and return True
        Otherwise, return False
        """
        trace = 'keys' in g.app.debug
        c, k = self.c, self
        #
        # Experimental special case:
        # Inserting a '.' always invokes the auto-completer.
        # The auto-completer just inserts a '.' if it isn't enabled.
        stroke = event.stroke
        if (
            stroke.s == '.'
            and k.isPlainKey(stroke)
            and self.unboundKeyAction in ('insert', 'overwrite')
        ):
            c.doCommandByName('auto-complete', event)
            return True
        #
        # Use getPaneBindings for *all* keys.
        bi = k.getPaneBinding(event)
        #
        # #327: Ignore killed bindings.
        if bi and bi.commandName in k.killedBindings:
            if trace:
                g.trace(f"{event.stroke!s} {bi.commandName}: in killed bindings")
            return False
        #
        # Execute the command if the binding exists.
        if bi:
            # A superb trace. !s gives shorter trace.
            if trace:
                g.trace(f"{event.stroke!s} {bi.commandName}")
            c.doCommandByName(bi.commandName, event)
            return True
        #
        # No binding exists.
        if trace:
            g.trace(f"{event.stroke!s} {bi.commandName}: no binding")
        return False
    #@+node:ekr.20091230094319.6240: *6* k.getPaneBinding & helper
    def getPaneBinding(self, event: Event) -> Any:
        c, k, state = self.c, self, self.unboundKeyAction
        stroke, w = event.stroke, event.w
        if not g.assert_is(stroke, g.KeyStroke):
            return None
        # #1757: Always insert plain keys in the body.
        #        Valid because mode bindings have already been handled.
        if (
            k.isPlainKey(stroke)
            and w == c.frame.body.widget
            and state in ('insert', 'overwrite')
        ):
            return None
        for key, name in (
            # Order here is similar to bindtags order.
            ('command', None),
            ('insert', None),
            ('overwrite', None),
            ('button', None),
            ('body', 'body'),
            ('text', 'head'),  # Important: text bindings in head before tree bindings.
            ('tree', 'head'),
            ('tree', 'canvas'),
            ('log', 'log'),
            ('text', 'log'),
            ('text', None),
            ('all', None),
        ):
            bi = k.getBindingHelper(key, name, stroke, w)
            if bi:
                return bi
        return None
    #@+node:ekr.20180418105228.1: *7* getPaneBindingHelper
    def getBindingHelper(self, key: str, name: str, stroke: Stroke, w: Wrapper) -> Any:
        """Find a binding for the widget with the given name."""
        c, k = self.c, self
        #
        # Return if the pane's name doesn't match the event's widget.
        state = k.unboundKeyAction
        w_name = c.widget_name(w)
        pane_matches = (
            name and w_name.startswith(name) or
            key in ('command', 'insert', 'overwrite') and state == key or
            key in ('text', 'all') and g.isTextWrapper(w) or
            key in ('button', 'all')
        )
        if not pane_matches:
            return None
        #
        # Return if there is no binding at all.
        d = k.masterBindingsDict.get(key, {})
        if not d:
            return None
        bi = d.get(stroke)
        if not bi:
            return None
        #
        # Ignore previous/next-line commands while editing headlines.
        if (
            key == 'text' and
            name == 'head' and
            bi.commandName in ('previous-line', 'next-line')
        ):
            return None
        #
        # The binding has been found.
        return bi
    #@+node:ekr.20160409035115.1: *6* k.searchTree
    def searchTree(self, char: str) -> None:
        """Search all visible nodes for a headline starting with stroke."""
        if not char:
            return
        c = self.c
        if not c.config.getBool('plain-key-outline-search'):
            return

        def match(p: Position) -> bool:
            """Return True if p contains char."""
            s = p.h.lower() if char.islower() else p.h
            return s.find(char) > -1

        # Start at c.p, then retry everywhere.

        for p in (c.p, c.rootPosition()):
            p = p.copy()
            if p == c.p and match(p):
                p.moveToVisNext(c)
            while p:
                if match(p):
                    c.selectPosition(p)
                    c.redraw()
                    return
                p.moveToVisNext(c)

        # Too confusing for the user.
        # re_pat = re.compile(r'^@(\w)+[ \t](.+)')

        # def match(p, pattern):
            # s = p.h.lower()
            # if pattern:
                # m = pattern.search(s)
                # found = (s.startswith(char) or
                    # m and m.group(2).lower().startswith(char))
            # else:
                # found = s.find(char) > -1
            # if found:
                # c.selectPosition(p)
                # c.redraw()
            # return found
    #@+node:ekr.20061031170011.3: *3* k.Minibuffer
    # These may be overridden, but this code is now gui-independent.
    #@+node:ekr.20061031170011.9: *4* k.extendLabel
    def extendLabel(self, s: str, select: bool = False, protect: bool = False) -> None:

        c, k, w = self.c, self, self.w
        if not (w and s):
            return
        c.widgetWantsFocusNow(w)
        w.insert(w.getLastIndex(), s)
        if select:
            i, j = k.getEditableTextRange()
            w.setSelectionRange(i, j, insert=j)
        if protect:
            k.protectLabel()
    #@+node:ekr.20061031170011.13: *4* k.getEditableTextRange
    def getEditableTextRange(self) -> tuple[int, int]:
        k, w = self, self.w
        s = w.getAllText()
        i = len(k.mb_prefix)
        j = len(s)
        return i, j
    #@+node:ekr.20061031170011.5: *4* k.getLabel
    def getLabel(self, ignorePrompt: bool = False) -> str:
        k, w = self, self.w
        if not w:
            return ''
        s = w.getAllText()
        if ignorePrompt:
            return s[len(k.mb_prefix) :]
        return s or ''
    #@+node:ekr.20080408060320.791: *4* k.killLine
    def killLine(self, protect: bool = True) -> None:
        k = self
        w = k.w
        s = w.getAllText()
        s = s[: len(k.mb_prefix)]
        w.setAllText(s)
        n = len(s)
        w.setSelectionRange(n, n, insert=n)
        if protect:
            k.mb_prefix = s
    #@+node:ekr.20061031131434.135: *4* k.minibufferWantsFocus
    # def minibufferWantsFocus(self):
        # c = self.c
        # c.widgetWantsFocus(c.miniBufferWidget)
    #@+node:ekr.20061031170011.6: *4* k.protectLabel
    def protectLabel(self) -> None:
        k, w = self, self.w
        if not w:
            return
        k.mb_prefix = w.getAllText()
    #@+node:ekr.20061031170011.7: *4* k.resetLabel
    def resetLabel(self) -> None:
        """Reset the minibuffer label."""
        k = self
        c, w = k.c, k.w
        k.setLabelGrey('')
        k.mb_prefix = ''
        if w:
            w.setSelectionRange(0, 0, insert=0)
            state = k.unboundKeyAction
            if c.vim_mode and c.vimCommands:
                c.vimCommands.show_status()
            else:
                k.setLabelBlue(label=f"{state.capitalize()} State")
    #@+node:ekr.20080408060320.790: *4* k.selectAll
    def selectAll(self) -> None:
        """Select all the user-editable text of the minibuffer."""
        w = self.w
        i, j = self.getEditableTextRange()
        w.setSelectionRange(i, j, insert=j)
    #@+node:ekr.20061031170011.8: *4* k.setLabel
    def setLabel(self, s: str, protect: bool = False) -> None:
        """Set the label of the minibuffer."""
        c, k, w = self.c, self, self.w
        if w:
            # Support for the curses gui.
            if hasattr(g.app.gui, 'set_minibuffer_label'):
                g.app.gui.set_minibuffer_label(c, s)
            w.setAllText(s)
            n = len(s)
            w.setSelectionRange(n, n, insert=n)
            if protect:
                k.mb_prefix = s
    #@+node:ekr.20061031170011.10: *4* k.setLabelBlue
    def setLabelBlue(self, label: str, protect: bool = True) -> None:
        """Set the minibuffer label."""
        k, w = self, self.w
        if hasattr(g.app.gui, 'set_minibuffer_label'):
            g.app.gui.set_minibuffer_label(self.c, label)
        elif w:
            w.setStyleClass('')  # normal state, not warning or error
            if label is not None:
                k.setLabel(label, protect=protect)
    #@+node:ekr.20061031170011.11: *4* k.setLabelGrey
    def setLabelGrey(self, label: str = None) -> None:
        k, w = self, self.w
        if not w:
            return
        w.setStyleClass('minibuffer_warning')
        if label is not None:
            k.setLabel(label)

    setLabelGray = setLabelGrey
    #@+node:ekr.20080510153327.2: *4* k.setLabelRed
    def setLabelRed(self, label: str = None, protect: bool = False) -> None:
        k, w = self, self.w
        if not w:
            return
        w.setStyleClass('minibuffer_error')
        if label is not None:
            k.setLabel(label, protect)
    #@+node:ekr.20140822051549.18298: *4* k.setStatusLabel
    def setStatusLabel(self, s: str) -> None:
        """
        Set the label to s.

        Use k.setStatusLabel, not k.setLabel, to report the status of a Leo
        command. This allows the option to use g.es instead of the minibuffer
        to report status.
        """
        k = self
        k.setLabel(s, protect=False)
    #@+node:ekr.20061031170011.12: *4* k.updateLabel
    def updateLabel(self, event: Event) -> None:
        """
        Mimic what would happen with the keyboard and a Text editor
        instead of plain accumulation.
        """
        c, k, w = self.c, self, self.w
        if not event:
            return
        ch, stroke = event.char, event.stroke
        if ch in "\n\r":
            return
        if ch != '\b' and stroke and not k.isPlainKey(stroke):
            return  # #2041.
        c.widgetWantsFocusNow(w)
        i, j = w.getSelectionRange()
        ins = w.getInsertPoint()
        if i != j:
            w.delete(i, j)
        if ch == '\b':
            s = w.getAllText()
            if len(s) > len(k.mb_prefix):
                w.delete(i - 1)
                i -= 1
        else:
            w.insert(ins, ch)
            i = ins + 1
    #@+node:ekr.20120208064440.10190: *3* k.Modes
    #@+node:ekr.20061031131434.100: *4* k.addModeCommands (enterModeCallback)
    def addModeCommands(self) -> None:
        """Add commands created by @mode settings to c.commandsDict."""
        c, k = self.c, self
        d = g.app.config.modeCommandsDict  # Keys are command names: enter-x-mode.
        # Create the callback functions and update c.commandsDict.
        for key in d.keys():
            # pylint: disable=cell-var-from-loop

            def enterModeCallback(event: Event = None, name: str = key) -> None:
                k.enterNamedMode(event, name)

            c.commandsDict[key] = enterModeCallback
    #@+node:ekr.20061031131434.157: *4* k.badMode
    def badMode(self, modeName: str) -> None:
        k = self
        k.clearState()
        if modeName.endswith('-mode'):
            modeName = modeName[:-5]
        k.setLabelGrey(f"@mode {modeName} is not defined (or is empty)")
    #@+node:ekr.20061031131434.158: *4* k.createModeBindings
    def createModeBindings(self, modeName: str, d: dict[str, list], w: Wrapper) -> None:
        """Create mode bindings for the named mode using dictionary d for w, a text widget."""
        c, k = self.c, self
        assert d.name().endswith('-mode')
        for commandName in d.keys():
            if commandName in ('*entry-commands*', '*command-prompt*'):
                # These are special-purpose dictionary entries.
                continue
            func = c.commandsDict.get(commandName)
            if not func:
                g.es_print('no such command:', commandName, 'Referenced from', modeName)
                continue
            aList: list = d.get(commandName, [])
            stroke: Stroke
            for bi in aList:
                stroke = bi.stroke
                # Important: bi.val is canonicalized.
                if stroke and stroke not in ('None', 'none', None):
                    assert g.isStroke(stroke)
                    k.makeMasterGuiBinding(stroke)
                    # Create the entry for the mode in k.masterBindingsDict.
                    # Important: this is similar, but not the same as k.bindKeyToDict.
                    # Thus, we should **not** call k.bindKey here!
                    d2 = k.masterBindingsDict.get(modeName, {})
                    d2[stroke] = g.BindingInfo(
                        kind=f"mode<{modeName}>",
                        commandName=commandName,
                        func=func,
                        nextMode=bi.nextMode,
                        stroke=stroke)
                    k.masterBindingsDict[modeName] = d2
    #@+node:ekr.20120208064440.10179: *4* k.endMode
    def endMode(self) -> None:
        c, k = self.c, self
        w = g.app.gui.get_focus(c)
        if w:
            c.frame.log.deleteTab('Mode')  # Changes focus to the body pane
        k.inputModeName = None
        k.clearState()
        k.resetLabel()
        k.showStateAndMode()  # Restores focus.
        if w:
            c.widgetWantsFocusNow(w)
    #@+node:ekr.20061031131434.160: *4* k.enterNamedMode
    def enterNamedMode(self, event: Event, commandName: str) -> None:
        c, k = self.c, self
        modeName = commandName[6:]
        c.inCommand = False  # Allow inner commands in the mode.
        k.generalModeHandler(event, modeName=modeName)
    #@+node:ekr.20061031131434.161: *4* k.exitNamedMode
    @cmd('exit-named-mode')
    def exitNamedMode(self, event: Event = None) -> None:
        """Exit an input mode."""
        k = self
        if k.inState():
            k.endMode()
        k.showStateAndMode()
    #@+node:ekr.20120208064440.10199: *4* k.generalModeHandler
    def generalModeHandler(
        self,
        event: Event,
        commandName: str = None,
        func: Callable = None,
        modeName: str = None,
        nextMode: str = None,
        prompt: str = None,
    ) -> None:
        """Handle a mode defined by an @mode node in leoSettings.leo."""
        c, k = self.c, self
        state = k.getState(modeName)
        if state == 0:
            k.inputModeName = modeName
            k.modePrompt = prompt or modeName
            k.modeWidget = event and event.widget
            k.setState(modeName, 1, handler=k.generalModeHandler)
            self.initMode(event, modeName)
            # Careful: k.initMode can execute commands that will destroy a commander.
            if g.app.quitting or not c.exists:
                return
            if not k.silentMode:
                if c.config.getBool('showHelpWhenEnteringModes'):
                    k.modeHelp(event)
                else:
                    c.frame.log.hideTab('Mode')
        elif not func:
            g.trace('No func: improper key binding')
        else:
            if commandName == 'mode-help':
                func(event)
            else:
                self.endMode()
                # New in 4.4.1 b1: pass an event describing the original widget.
                if event:
                    event.w = event.widget = k.modeWidget
                else:
                    event = g.app.gui.create_key_event(c, w=k.modeWidget)
                func(event)
                if g.app.quitting or not c.exists:
                    pass
                elif nextMode in (None, 'none'):
                    # Do *not* clear k.inputModeName or the focus here.
                    # func may have put us in *another* mode.
                    pass
                elif nextMode == 'same':
                    silent = k.silentMode
                    k.setState(modeName, 1, handler=k.generalModeHandler)
                    self.reinitMode(modeName)  # Re-enter this mode.
                    k.silentMode = silent
                else:
                    k.silentMode = False  # All silent modes must do --> set-silent-mode.
                    self.initMode(event, nextMode)  # Enter another mode.
    #@+node:ekr.20061031131434.163: *4* k.initMode
    def initMode(self, event: Event, modeName: str) -> None:

        c, k = self.c, self
        if not modeName:
            g.trace('oops: no modeName')
            return
        d = g.app.config.modeCommandsDict.get('enter-' + modeName)
        if not d:
            self.badMode(modeName)
            return
        k.modeBindingsDict = d
        bi = d.get('*command-prompt*')
        prompt = bi.kind if bi else modeName
        k.inputModeName = modeName
        k.silentMode = False
        aList = d.get('*entry-commands*', [])
        if aList:
            for bi in aList:
                commandName = bi.commandName
                k.simulateCommand(commandName)
                # Careful, the command can kill the commander.
                if g.app.quitting or not c.exists:
                    return
                # New in Leo 4.5: a startup command can immediately transfer to another mode.
                if commandName.startswith('enter-'):
                    return
        # Create bindings after we know whether we are in silent mode.
        w = k.modeWidget if k.silentMode else k.w
        k.createModeBindings(modeName, d, w)
        k.showStateAndMode(prompt=prompt)
    #@+node:ekr.20061031131434.165: *4* k.modeHelp & helper
    @cmd('mode-help')
    def modeHelp(self, event: Event) -> None:
        """
        The mode-help command.

        A possible convention would be to bind <Tab> to this command in most modes,
        by analogy with tab completion.
        """
        c, k = self.c, self
        c.endEditing()
        if k.inputModeName:
            d = g.app.config.modeCommandsDict.get('enter-' + k.inputModeName)
            k.modeHelpHelper(d)
        if not k.silentMode:
            c.minibufferWantsFocus()
    #@+node:ekr.20061031131434.166: *5* modeHelpHelper
    def modeHelpHelper(self, d: dict[str, str]) -> None:
        c, k = self.c, self
        tabName = 'Mode'
        c.frame.log.clearTab(tabName)
        data, n = [], 0
        for key in sorted(d.keys()):
            if key in ('*entry-commands*', '*command-prompt*'):
                pass
            else:
                aList = d.get(key)
                for bi in aList:
                    stroke = bi.stroke
                    if stroke not in (None, 'None'):
                        s1 = key
                        s2 = k.prettyPrintKey(stroke)
                        n = max(n, len(s1))
                        data.append((s1, s2),)
        data.sort()
        modeName = k.inputModeName.replace('-', ' ')
        if modeName.endswith('mode'):
            modeName = modeName[:-4].strip()
        prompt = d.get('*command-prompt*')
        if prompt:
            g.es('', f"{prompt.kind.strip()}\n\n", tabName=tabName)
        else:
            g.es('', f"{modeName} mode\n\n", tabName=tabName)
        # This isn't perfect in variable-width fonts.
        for s1, s2 in data:
            g.es('', '%*s %s' % (n, s1, s2), tabName=tabName)
    #@+node:ekr.20061031131434.164: *4* k.reinitMode
    def reinitMode(self, modeName: str) -> None:
        k = self
        d = k.modeBindingsDict
        k.inputModeName = modeName
        w = k.modeWidget if k.silentMode else k.w
        k.createModeBindings(modeName, d, w)
        if k.silentMode:
            k.showStateAndMode()
        else:
            # Do not set the status line here.
            k.setLabelBlue(modeName + ': ')  # ,protect=True)
    #@+node:ekr.20061031131434.181: *3* k.Shortcuts & bindings
    #@+node:ekr.20061031131434.176: *4* k.computeInverseBindingDict
    def computeInverseBindingDict(self) -> dict[str, list[tuple[str, Any]]]:
        """
        Return a dictionary whose keys are command names,
        values are lists of tuples(pane, stroke).
        """
        k = self
        d = k.masterBindingsDict  # Dict[scope, g.BindingInfo]
        result_d: dict[str, list[tuple[str, Any]]] = {}  # Dict[command-name, tuple[pane, stroke]]
        for scope in sorted(d):
            d2 = d.get(scope, {})  # Dict[stroke, g.BindingInfo]
            for stroke in d2:
                assert g.isStroke(stroke), stroke
                bi = d2.get(stroke)
                assert isinstance(bi, g.BindingInfo), repr(bi)
                aList: list[Any] = result_d.get(bi.commandName, [])
                data = (bi.pane, stroke)
                if data not in aList:
                    aList.append(data)
                    result_d[bi.commandName] = aList
        return result_d
    #@+node:ekr.20061031131434.179: *4* k.getShortcutForCommandName
    def getStrokeForCommandName(self, commandName: str) -> Optional[Stroke]:
        c, k = self.c, self
        command = c.commandsDict.get(commandName)
        if command:
            for stroke, aList in k.bindingsDict.items():
                for bi in aList:
                    if bi.commandName == commandName:
                        return stroke
        return None
    #@+node:ekr.20090518072506.8494: *4* k.isFKey
    def isFKey(self, stroke: Stroke) -> bool:
        # k = self
        if not stroke:
            return False
        assert isinstance(stroke, str) or g.isStroke(stroke)
        s = stroke.s if g.isStroke(stroke) else stroke
        s = s.lower()
        return s.startswith('f') and len(s) <= 3 and s[1:].isdigit()
    #@+node:ekr.20061031131434.182: *4* k.isPlainKey
    def isPlainKey(self, stroke: Stroke) -> bool:
        """Return true if the shortcut refers to a plain (non-Alt,non-Ctl) key."""
        if not stroke:
            return False
        if not g.isStroke(stroke):
            # Happens during unit tests.
            stroke = g.KeyStroke(stroke)
        #
        # altgr combos (Alt+Ctrl) are always plain keys
        # g.KeyStroke does not handle this, because it has no "c" ivar.
        #
        if stroke.isAltCtrl() and not self.enable_alt_ctrl_bindings:
            return True
        return stroke.isPlainKey()
    #@+node:ekr.20061031131434.191: *4* k.prettyPrintKey
    def prettyPrintKey(self, stroke: Stroke, brief: bool = False) -> str:

        if not stroke:
            return ''
        if not g.assert_is(stroke, g.KeyStroke):
            return stroke
        return stroke.prettyPrint()
    #@+node:ekr.20110606004638.16929: *4* k.stroke2char
    def stroke2char(self, stroke: Stroke) -> Stroke:
        """
        Convert a stroke to an (insertable) char.
        This method allows Leo to use strokes everywhere.
        """
        if not stroke:
            return ''
        if not g.isStroke(stroke):
            # vim commands pass a plain key.
            stroke = g.KeyStroke(stroke)
        return stroke.toInsertableChar()
    #@+node:ekr.20061031131434.193: *3* k.States
    #@+node:ekr.20061031131434.194: *4* k.clearState
    def clearState(self) -> None:
        """Clear the key handler state."""
        k = self
        k.state.kind = None
        k.state.n = None
        k.state.handler = None
    #@+node:ekr.20061031131434.196: *4* k.getState
    def getState(self, kind: str) -> int:
        k = self
        val = k.state.n if k.state.kind == kind else 0
        return val
    #@+node:ekr.20061031131434.195: *4* k.getStateHandler
    def getStateHandler(self) -> Callable:
        return self.state.handler
    #@+node:ekr.20061031131434.197: *4* k.getStateKind
    def getStateKind(self) -> str:
        return self.state.kind
    #@+node:ekr.20061031131434.198: *4* k.inState
    def inState(self, kind: str = None) -> bool:
        k = self
        if kind:
            return k.state.kind == kind and k.state.n is not None
        return k.state.kind and k.state.n is not None
    #@+node:ekr.20080511122507.4: *4* k.setDefaultInputState
    def setDefaultInputState(self) -> None:
        k = self
        state = k.defaultUnboundKeyAction
        k.setInputState(state)
    #@+node:ekr.20110209093958.15411: *4* k.setEditingState
    def setEditingState(self) -> None:
        k = self
        state = k.defaultEditingAction
        k.setInputState(state)
    #@+node:ekr.20061031131434.133: *4* k.setInputState
    def setInputState(self, state: str, set_border: bool = False) -> None:
        k = self
        k.unboundKeyAction = state
    #@+node:ekr.20061031131434.199: *4* k.setState
    def setState(self, kind: str, n: int, handler: Callable = None) -> None:

        k = self
        if kind and n is not None:
            k.state.kind = kind
            k.state.n = n
            if handler:
                k.state.handler = handler
        else:
            k.clearState()
        # k.showStateAndMode()
    #@+node:ekr.20061031131434.192: *4* k.showStateAndMode
    def showStateAndMode(self, w: Wrapper = None, prompt: str = None, setFocus: bool = True) -> None:
        """Show the state and mode at the start of the minibuffer."""
        c, k = self.c, self
        state = k.unboundKeyAction
        mode = k.getStateKind()
        if not g.app.gui:
            return
        if not w:
            if hasattr(g.app.gui, 'set_minibuffer_label'):
                pass  # we don't need w
            else:
                w = g.app.gui.get_focus(c)
                if not w:
                    return
        isText = g.isTextWrapper(w)
        # This fixes a problem with the tk gui plugin.
        if mode and mode.lower().startswith('isearch'):
            return
        wname = g.app.gui.widget_name(w).lower()
        # Get the wrapper for the headline widget.
        if wname.startswith('head'):
            if hasattr(c.frame.tree, 'getWrapper'):
                if hasattr(w, 'widget'):
                    w2 = w.widget
                else:
                    w2 = w
                w = c.frame.tree.getWrapper(w2, item=None)
                isText = bool(w)  # A benign hack.
        if mode:
            if mode in ('getArg', 'getFileName', 'full-command'):
                s = None
            elif prompt:
                s = prompt
            else:
                mode = mode.strip()
                if mode.endswith('-mode'):
                    mode = mode[:-5]
                s = f"{mode.capitalize()} Mode"
        elif c.vim_mode and c.vimCommands:
            c.vimCommands.show_status()
            return
        else:
            s = f"{state.capitalize()} State"
            if c.editCommands.extendMode:
                s = s + ' (Extend Mode)'
        if s:
            k.setLabelBlue(s)
        if w and isText:
            # k.showStateColors(inOutline,w)
            k.showStateCursor(state, w)
        # 2015/07/11: reset the status line.
        if hasattr(c.frame.tree, 'set_status_line'):
            c.frame.tree.set_status_line(c.p)
    #@+node:ekr.20110202111105.15439: *4* k.showStateCursor
    def showStateCursor(self, state: str, w: Wrapper) -> None:
        pass
    #@-others
#@+node:ekr.20120208064440.10150: ** class ModeInfo
class ModeInfo:

    def __repr__(self) -> str:
        return f"<ModeInfo {self.name}>"

    __str__ = __repr__
    #@+others
    #@+node:ekr.20120208064440.10193: *3* mode_i. ctor
    def __init__(self, c: Cmdr, name: str, aList: list) -> None:

        self.c = c
        # The bindings in effect for this mode.
        # Keys are names of (valid) command names, values are BindingInfo objects.
        self.d: dict[str, Any] = {}
        self.entryCommands: list[Any] = []  # A list of BindingInfo objects.
        self.k = c.k
        self.name: str = self.computeModeName(name)
        self.prompt: str = self.computeModePrompt(self.name)
        self.init(name, aList)
    #@+node:ekr.20120208064440.10152: *3* mode_i.computeModeName
    def computeModeName(self, name: str) -> str:
        s = name.strip().lower()
        j = s.find(' ')
        if j > -1:
            s = s[:j]
        if s.endswith('mode'):
            s = s[:-4].strip()
        if s.endswith('-'):
            s = s[:-1]
        i = s.find('::')
        if i > -1:
            # The actual mode name is everything up to the "::"
            # The prompt is everything after the prompt.
            s = s[:i]
        return s + '-mode'
    #@+node:ekr.20120208064440.10156: *3* mode_i.computeModePrompt
    def computeModePrompt(self, name: str) -> str:
        assert name == self.name
        s = 'enter-' + name.replace(' ', '-')
        i = s.find('::')
        if i > -1:
            # The prompt is everything after the '::'
            prompt = s[i + 2 :].strip()
        else:
            prompt = s
        return prompt
    #@+node:ekr.20120208064440.10160: *3* mode_i.createModeBindings
    def createModeBindings(self, w: Wrapper) -> None:
        """Create mode bindings for w, a text widget."""
        c, d, k, modeName = self.c, self.d, self.k, self.name
        for commandName in d:
            func = c.commandsDict.get(commandName)
            if not func:
                g.es_print(f"no such command: {commandName} Referenced from {modeName}")
                continue
            aList = d.get(commandName, [])
            for bi in aList:
                stroke = bi.stroke
                # Important: bi.val is canonicalized.
                if stroke and stroke not in ('None', 'none', None):
                    assert g.isStroke(stroke)
                    k.makeMasterGuiBinding(stroke)
                    # Create the entry for the mode in k.masterBindingsDict.
                    # Important: this is similar, but not the same as k.bindKeyToDict.
                    # Thus, we should **not** call k.bindKey here!
                    d2 = k.masterBindingsDict.get(modeName, {})
                    d2[stroke] = g.BindingInfo(
                        kind=f"mode<{modeName}>",
                        commandName=commandName,
                        func=func,
                        nextMode=bi.nextMode,
                        stroke=stroke)
                    k.masterBindingsDict[modeName] = d2
    #@+node:ekr.20120208064440.10195: *3* mode_i.createModeCommand
    def createModeCommand(self) -> None:
        c = self.c
        key = 'enter-' + self.name.replace(' ', '-')

        def enterModeCallback(event: Event = None, self: Any = self) -> None:
            self.enterMode()

        c.commandsDict[key] = f = enterModeCallback
        g.trace('(ModeInfo)', f.__name__, key,
            'len(c.commandsDict.keys())', len(list(c.commandsDict.keys())))
    #@+node:ekr.20120208064440.10180: *3* mode_i.enterMode
    def enterMode(self) -> None:

        c, k = self.c, self.k
        c.inCommand = False  # Allow inner commands in the mode.
        event = None
        k.generalModeHandler(event, modeName=self.name)
    #@+node:ekr.20120208064440.10153: *3* mode_i.init
    def init(self, name: str, dataList: list[tuple[str, Any]]) -> None:
        """aList is a list of tuples (commandName,bi)."""
        c, d, modeName = self.c, self.d, self.name
        for name, bi in dataList:
            if not name:
                # An entry command: put it in the special *entry-commands* key.
                self.entryCommands.append(bi)
            elif bi is not None:
                # A regular shortcut.
                bi.pane = modeName
                aList = d.get(name, [])
                # Important: use previous bindings if possible.
                key2, aList2 = c.config.getShortcut(name)
                aList3 = [z for z in aList2 if z.pane != modeName]
                if aList3:
                    aList.extend(aList3)
                aList.append(bi)
                d[name] = aList
    #@+node:ekr.20120208064440.10158: *3* mode_i.initMode
    def initMode(self) -> None:

        c, k = self.c, self.c.k
        k.inputModeName = self.name
        k.silentMode = False
        for bi in self.entryCommands:
            commandName = bi.commandName
            k.simulateCommand(commandName)
            # Careful, the command can kill the commander.
            if g.app.quitting or not c.exists:
                return
            # New in Leo 4.5: a startup command can immediately transfer to another mode.
            if commandName.startswith('enter-'):
                return
        # Create bindings after we know whether we are in silent mode.
        w = k.modeWidget if k.silentMode else k.w
        k.createModeBindings(self.name, self.d, w)
        k.showStateAndMode(prompt=self.name)
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
