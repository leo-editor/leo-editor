# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20061031131434: * @file leoKeys.py
#@@first
"""Gui-independent keystroke handling for Leo."""
# pylint: disable=eval-used
# pylint: disable=deprecated-method
    # The new methods may not exist in Python 2.
#@+<< imports >>
#@+node:ekr.20061031131434.1: ** << imports >> (leoKeys)
import leo.core.leoGlobals as g
import leo.external.codewise as codewise
# import glob
import inspect
import os
import re
import string
import sys
import time
#@-<< imports >>
#@+<< Key bindings, an overview >>
#@+node:ekr.20130920121326.11281: ** << Key bindings, an overview >>
#@@nocolor-node
#@+at
# 
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
#    bindings are as expeced.
# 
# B. If k.getPaneBinding finds a command associated with the incoming
#    keystroke, k.masterKeyHandler calls k.masterCommand to execute the
#    command. k.masterCommand handles many complex. See the source code for
#    details.
# 
# C. If k.getPaneBinding fails to bind the incoming keystroke to a command,
#    k.masterKeyHandler calls k.handleUnboundKeys to handle the keystroke.
#    Depending on the widget, and settings, and the keystroke,
#    k.handleUnboundKeys may do nothing, or it may call k.masterCommand to
#    insert a plain key into the widget.
#@-<< Key bindings, an overview >>
#@+<< about 'internal' bindings >>
#@+node:ekr.20061031131434.2: ** << about 'internal' bindings >>
#@@nocolor
#@+at
# 
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
#@@nocolor
#@+at
# 
# ivar                    Keys                Values
# ----                    ----                ------
# c.commandsDict          command names (1)   functions
# k.bindingsDict          shortcuts           lists of BindingInfo objects
# k.masterBindingsDict    scope names (2)     Interior masterBindingDicts (3)
# k.masterGuiBindingsDict strokes             list of widgets in which stoke is bound
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
#@+node:ekr.20061031131434.4: ** class AutoCompleterClass
class AutoCompleterClass(object):
    '''A class that inserts autocompleted and calltip text in text widgets.
    This class shows alternatives in the tabbed log pane.

    The keyHandler class contains hooks to support these characters:
    invoke-autocompleter-character (default binding is '.')
    invoke-calltips-character (default binding is '(')
    '''
    #@+others
    #@+node:ekr.20150509035140.1: *3* ac.cmd (decorator)
    def cmd(name):
        '''Command decorator for the AutoCompleter class.'''
        # pylint: disable=no-self-argument
        return g.new_cmd_decorator(name, ['c', 'k', 'autoCompleter'])
    #@+node:ekr.20061031131434.5: *3* ac.ctor & reloadSettings
    def __init__(self, k):
        '''Ctor for AutoCompleterClass class.'''
        # Ivars...
        self.c = k.c
        self.k = k
        self.force = None
        self.language = None
        self.namespaces = []
            # additional namespaces to search for objects, other code
            # can append namespaces to this to extend scope of search
        self.qw = None
            # The object that supports qcompletion methods.
        self.tabName = None
            # The name of the main completion tab.
        self.verbose = False
            # True: print all members, regardless of how many there are.
        self.w = None
            # The widget that gets focus after autocomplete is done.
        self.warnings = {}
            # Keys are language names.
        # Codewise pre-computes...
        self.codewiseSelfList = []
            # The (global) completions for "self."
        self.completionsDict = {}
            # Keys are prefixes, values are completion lists.
        self.reloadSettings()
        
    def reloadSettings(self):
        c = self.c
        self.auto_tab = c.config.getBool('auto_tab_complete', False)
        self.forbid_invalid = c.config.getBool('forbid_invalid_completions', False)
        self.use_qcompleter = c.config.getBool('use_qcompleter', False)
            # True: show results in autocompleter tab.
            # False: show results in a QCompleter widget.
    #@+node:ekr.20061031131434.8: *3* ac.Top level
    #@+node:ekr.20061031131434.9: *4* ac.autoComplete
    @cmd('auto-complete')
    def autoComplete(self, event=None, force=False):
        '''An event handler for autocompletion.'''
        trace = False and not g.unitTesting
        c, k = self.c, self.k
        state = k.unboundKeyAction
        # pylint: disable=consider-using-ternary
        w = event and event.w or c.get_focus()
        self.force = force
        if state not in ('insert', 'overwrite'):
            if trace: g.trace('not in insert/overwrite mode')
            return
        # First, handle the invocation character as usual.
        if not force:
            # Ctrl-period does *not* insert a period.
            if trace: g.trace('not force')
            k.masterCommand(event=event)
        # Allow autocompletion only in the body pane.
        if not c.widget_name(w).lower().startswith('body'):
            if trace: g.trace('not body')
            return
        self.language = g.scanForAtLanguage(c, c.p)
        if w and (k.enable_autocompleter or force): # self.language == 'python':
            if trace: g.trace('starting')
            self.w = w
            self.start(event)
        else:
            if trace: g.trace('autocompletion not enabled')
    #@+node:ekr.20061031131434.10: *4* ac.autoCompleteForce
    @cmd('auto-complete-force')
    def autoCompleteForce(self, event=None):
        '''Show autocompletion, even if autocompletion is not presently enabled.'''
        return self.autoComplete(event, force=True)
    #@+node:ekr.20061031131434.12: *4* ac.enable/disable/toggleAutocompleter/Calltips
    @cmd('disable-autocompleter')
    def disableAutocompleter(self, event=None):
        '''Disable the autocompleter.'''
        self.k.enable_autocompleter = False
        self.showAutocompleterStatus()

    @cmd('disable-calltips')
    def disableCalltips(self, event=None):
        '''Disable calltips.'''
        self.k.enable_calltips = False
        self.showCalltipsStatus()

    @cmd('enable-autocompleter')
    def enableAutocompleter(self, event=None):
        '''Enable the autocompleter.'''
        self.k.enable_autocompleter = True
        self.showAutocompleterStatus()

    @cmd('enable-calltips')
    def enableCalltips(self, event=None):
        '''Enable calltips.'''
        self.k.enable_calltips = True
        self.showCalltipsStatus()

    @cmd('toggle-autocompleter')
    def toggleAutocompleter(self, event=None):
        '''Toggle whether the autocompleter is enabled.'''
        self.k.enable_autocompleter = not self.k.enable_autocompleter
        self.showAutocompleterStatus()

    @cmd('toggle-calltips')
    def toggleCalltips(self, event=None):
        '''Toggle whether calltips are enabled.'''
        self.k.enable_calltips = not self.k.enable_calltips
        self.showCalltipsStatus()
    #@+node:ekr.20061031131434.13: *4* ac.showCalltips
    @cmd('show-calltips')
    def showCalltips(self, event=None, force=False):
        '''Show the calltips at the cursor.'''
        c = self.c; k = c.k
        w = event and event.w
        if not w: return
        is_headline = c.widget_name(w).startswith('head')
        # Insert the calltip if possible, but not in headlines.
        if (k.enable_calltips or force) and not is_headline:
            self.w = w
            self.calltip()
        else:
            # Just insert the invocation character as usual.
            k.masterCommand(event=event)
    #@+node:ekr.20061031131434.14: *4* ac.showCalltipsForce
    @cmd('show-calltips-force')
    def showCalltipsForce(self, event=None):
        '''Show the calltips at the cursor, even if calltips are not presently enabled.'''
        return self.showCalltips(event, force=True)
    #@+node:ekr.20061031131434.15: *4* ac.showAutocompleter/CalltipsStatus
    def showAutocompleterStatus(self):
        '''Show the autocompleter status.'''
        k = self.k
        if not g.unitTesting:
            s = 'autocompleter %s' % (
                'On' if k.enable_autocompleter else 'Off')
            g.red(s)

    def showCalltipsStatus(self):
        '''Show the autocompleter status.'''
        k = self.k
        if not g.unitTesting:
            s = 'calltips %s' % 'On' if k.enable_calltips else 'Off'
            g.red(s)
    #@+node:ekr.20061031131434.16: *3* ac.Helpers
    #@+node:ekr.20110512212836.14469: *4* ac.exit
    def exit(self):
        trace = False and not g.unitTesting
        if trace: g.trace(g.callers())
        c = self.c
        w = self.w or c.frame.body.wrapper
        if trace: g.trace(g.callers())
        c.k.keyboardQuit()
        if self.use_qcompleter:
            if self.qw:
                self.qw.end_completer()
                self.qw = None # Bug fix: 2013/09/24.
        else:
            for name in (self.tabName, 'Modules', 'Info'):
                c.frame.log.deleteTab(name)
        # Restore the selection range that may have been destroyed by changing tabs.
        c.widgetWantsFocusNow(w)
        i, j = w.getSelectionRange()
        w.setSelectionRange(i, j, insert=j)
        # Was in finish.
        c.frame.body.onBodyChanged('Typing')
        c.recolor()

    finish = exit
    abort = exit
    #@+node:ekr.20061031131434.18: *4* ac.append/begin/popTabName
    def appendTabName(self, word):
        self.setTabName(self.tabName + '.' + word)

    def beginTabName(self, word):
        self.setTabName('AutoComplete ' + word)

    def clearTabName(self):
        self.setTabName('AutoComplete ')

    def popTabName(self):
        s = self.tabName
        i = s.rfind('.', 0, -1)
        if i > -1:
            self.setTabName(s[0: i])
    # Underscores are not valid in Pmw tab names!

    def setTabName(self, s):
        c = self.c
        if self.tabName:
            c.frame.log.deleteTab(self.tabName)
        self.tabName = s.replace('_', '') or ''
        c.frame.log.clearTab(self.tabName)
    #@+node:ekr.20110509064011.14556: *4* ac.attr_matches
    def attr_matches(self, s, namespace):
        """Compute matches when string s is of the form name.name....name.

        Evaluates s using eval(s,namespace)

        Assuming the text is of the form NAME.NAME....[NAME], and is evaluatable in
        the namespace, it will be evaluated and its attributes (as revealed by
        dir()) are used as possible completions.

        For class instances, class members are are also considered.)

        **Warning**: this can still invoke arbitrary C code, if an object
        with a __getattr__ hook is evaluated.

        """
        trace = False and not g.unitTesting
        verbose = False
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
        result = ["%s.%s" % (expr, w) for w in words if w[: n] == attr]
        if trace:
            if verbose:
                g.trace(s, result)
            else:
                g.trace(repr(s))
        return result
    #@+node:ekr.20061031131434.11: *4* ac.auto_completer_state_handler
    def auto_completer_state_handler(self, event):
        '''Handle all keys while autocompleting.'''
        trace = False and not g.app.unitTesting
        c, k, tag = self.c, self.k, 'auto-complete'
        state = k.getState(tag)
        ch = event.char if event else ''
        stroke = event.stroke if event else ''
        is_plain = k.isPlainKey(stroke)
        if trace: g.trace('state: %s, ch: %s, stroke: %s' % (
            state, repr(ch), repr(stroke)))
        if state == 0:
            c.frame.log.clearTab(self.tabName)
            common_prefix, prefix, tabList = self.compute_completion_list()
            if tabList:
                k.setState(tag, 1, handler=self.auto_completer_state_handler)
            else:
                if trace: g.trace('abort: not tabList')
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
            message = 'verbose completions %s' % (kind)
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
            if trace: g.trace('plain: %r' % (ch))
            self.insert_general_char(ch)
        else:
            if stroke == k.autoCompleteForceKey:
                # This is probably redundant because completions will exist.
                # However, it doesn't hurt, and it may be useful rarely.
                if trace: g.trace('auto-complete-force', repr(stroke))
                common_prefix, prefix, tabList = self.compute_completion_list()
                if tabList:
                    self.show_completion_list(common_prefix, prefix, tabList)
                else:
                    g.warning('No completions')
                    self.exit()
                return None
            else:
                if trace: g.trace('ignore non plain key', repr(stroke), g.callers())
                self.abort() # 2011/06/17.
                return 'do-standard-keys'
    #@+node:ekr.20061031131434.20: *4* ac.calltip & helpers
    def calltip(self):
        '''Show the calltips for the present prefix.
        ch is '(' if the user has just typed it.
        '''
        obj, prefix = self.get_object()
        if obj:
            self.calltip_success(prefix, obj)
        else:
            self.calltip_fail(prefix)
        self.exit()
    #@+node:ekr.20110512090917.14468: *5* ac.calltip_fail
    def calltip_fail(self, prefix):
        '''Evaluation of prefix failed.'''
        trace = False and not g.unitTesting
        if trace:
            g.es('eval failed for "%s"' % repr(prefix))
        self.insert_string('(')
    #@+node:ekr.20110512090917.14469: *5* ac.calltip_success
    def calltip_success(self, prefix, obj):
        trace = False and not g.unitTesting
        try:
            # Get the parenthesized argument list.
            s1, s2, s3, s4 = inspect.getargspec(obj)
            s = inspect.formatargspec(s1, s2, s3, s4)
            if trace: g.trace(obj, repr(s))
        except Exception:
            if trace: g.trace('inspect failed. obj: %s' % (obj))
            self.insert_string('(')
            return
        # Clean s and insert it: don't include the opening "(".
        if g.match(s, 1, 'self,'):
            s = s[6:].strip()
        elif g.match_word(s, 1, 'self'):
            s = s[5:].strip()
        else:
            s = s[1:].strip()
        self.insert_string("(", select=False)
        self.insert_string(s, select=True)
    #@+node:ekr.20061031131434.28: *4* ac.compute_completion_list & helper
    def compute_completion_list(self):
        '''Return the autocompleter completion list.'''
        trace = False and not g.unitTesting
        verbose = False
            # True: report hits and misses.
            # False: report misses.
        prefix = self.get_autocompleter_prefix()
        key, options = self.get_cached_options(prefix)
        if options:
            if trace and verbose: g.trace('**prefix hit: %s, %s' % (prefix, key))
        else:
            if trace: g.trace('**prefix miss: %s, %s' % (prefix, key))
            options = self.get_completions(prefix)
        tabList, common_prefix = g.itemsMatchingPrefixInList(
            prefix, options, matchEmptyPrefix=False)
        if not common_prefix:
            tabList, common_prefix = g.itemsMatchingPrefixInList(
                prefix, options, matchEmptyPrefix=True)
        if trace and verbose:
            g.trace('prefix: %s, common: %s, len(tabList): %s' % (
                repr(prefix), repr(common_prefix), len(tabList)))
            # if verbose: g.trace('options[:10]...\n',
                # g.listToString(options[:10],sort=True))
        if tabList:
            self.show_completion_list(common_prefix, prefix, tabList)
        return common_prefix, prefix, tabList
    #@+node:ekr.20110514051607.14524: *5* ac.get_cached_options
    def get_cached_options(self, prefix):
        trace = False and not g.unitTesting
        d = self.completionsDict
        # Search the completions Dict for shorter and shorter prefixes.
        i = len(prefix)
        while i > 0:
            key = prefix[: i]
            i -= 1
            # Make sure we report hits only of real objects.
            if key.endswith('.'):
                if trace: g.trace('== period: %s' % (key))
                return key, []
            options = d.get(key)
            if options:
                if trace: g.trace('== hit: %s len: %s' % (
                    key, len(options)))
                return key, options
            else:
                if trace: g.trace('== miss: %s' % (key))
        return None, []
    #@+node:ekr.20061031131434.29: *4* ac.do_backspace
    def do_backspace(self):
        '''Delete the character and recompute the completion list.'''
        c, w = self.c, self.w
        c.bodyWantsFocusNow()
        i = w.getInsertPoint()
        if i <= 0:
            self.exit()
            return
        w.delete(i - 1, i)
        w.setInsertPoint(i - 1)
        if i <= 1:
            self.exit()
        else:
            # Update the list. Abort if there is no prefix.
            common_prefix, prefix, tabList = self.compute_completion_list()
            if not prefix:
                self.exit()
    #@+node:ekr.20110510133719.14548: *4* ac.do_qcompleter_tab (not used)
    def do_qcompleter_tab(self, prefix, options):
        '''Return the longest common prefix of all the options.'''
        trace = False and not g.unitTesting
        matches, common_prefix = g.itemsMatchingPrefixInList(
            prefix, options, matchEmptyPrefix=False)
        if trace: g.trace(repr(common_prefix))
        return common_prefix
    #@+node:ekr.20110509064011.14561: *4* ac.get_autocompleter_prefix
    def get_autocompleter_prefix(self):
        trace = False and not g.unitTesting
        # Only the body pane supports auto-completion.
        w = self.c.frame.body.wrapper
        s = w.getAllText()
        if not s: return ''
        i = w.getInsertPoint() - 1
        i1 = i = j = max(0, i)
        while i >= 0 and (s[i].isalnum() or s[i] in '._'):
            i -= 1
        i += 1
        j += 1
        prefix = s[i: j]
        if trace: g.trace(repr(prefix), 'ins', s[i1:])
        return prefix
    #@+node:ekr.20110512212836.14471: *4* ac.get_completions & helpers
    def get_completions(self, prefix):
        trace = False and not g.unitTesting
        verbose = False # True: report hits and misses.  False: report misses.
        d = self.completionsDict
        # Precompute the codewise completions for '.self'.
        if not self.codewiseSelfList:
            aList = self.get_codewise_completions('self.')
            self.codewiseSelfList = [z[5:] for z in aList]
            d['self.'] = self.codewiseSelfList
        # Use the cached list if it exists.
        aList = d.get(prefix)
        if aList:
            if trace and verbose: g.trace('**cache hit: %s' % (prefix))
            return aList
        # elif self.use_codewise:
            # aList = self.get_codewise_completions(prefix)
        # else:
            # aList = self.get_leo_completions(prefix)
        # Always try the Leo completions first.
        # Fall back to the codewise completions.
        aList = (
            self.get_leo_completions(prefix) or
            self.get_codewise_completions(prefix)
        )
        if trace: g.trace('**cash miss: %s' % (prefix))
        d[prefix] = aList
        return aList
    #@+node:ekr.20110510120621.14539: *5* ac.get_codewise_completions & helpers
    def get_codewise_completions(self, prefix):
        '''Use codewise to generate a list of hits.'''
        trace = False and not g.unitTesting
        c = self.c
        m = re.match(r"(\S+(\.\w+)*)\.(\w*)$", prefix)
        if m:
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
        if 1: # A kludge: add the prefix to each hit.
            hits = ['%s.%s' % (varname, z) for z in hits]
        if trace:
            g.trace('kind', kind, 'varname', varname, 'ivar', ivar, 'prefix', prefix)
            # g.trace('prefix',prefix,'kind',kind,'varname',varname,'ivar',ivar,'len(hits)',len(hits))
            # g.trace('hits[:10]',g.listToString(hits[:10],sort=False))
        return hits
    #@+node:ekr.20110510120621.14540: *6* ac.clean
    def clean(self, hits):
        '''Clean up hits, a list of ctags patterns, for use in completion lists.'''
        trace = False and not g.unitTesting
        # Just take the function name: ignore the signature & file.
        aList = list(set([z[0] for z in hits]))
        aList.sort()
        if trace:
            g.trace('aList[:50]', g.listToString(aList[: 50]))
        return aList
    #@+node:ekr.20110512232915.14481: *6* ac.clean_for_display (not used)
    def clean_for_display(self, hits):
        '''Clean up hits, a list of ctags patterns, for display purposes.'''
        trace = False and not g.unitTesting
        aList = []
        for h in hits:
            s = h[0]
            # Display oriented: no good for completion list.
            fn = h[1].strip()
            if fn.startswith('/'):
                sig = fn[2: -4].strip()
            else:
                sig = fn
            aList.append('%s: %s' % (s, sig))
        aList = list(set(aList))
        aList.sort()
        if trace:
            # g.trace('hits[:50]',g.listToString(hits[:50])
            g.trace('aList[:50]', g.listToString(aList[: 50]))
        return aList
    #@+node:ekr.20110510120621.14542: *6* ac.guess_class
    def guess_class(self, c, varname):
        '''Return kind, class_list'''
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
                # pylint: disable=anomalous-backslash-in-string
                m = re.search('class\s+(\w+)', h)
                if m:
                    return 'class', [m.group(1)]
        if 1:
            aList = []
        else:
            # This is not needed now that we add the completions for 'self'.
            aList = ContextSniffer().get_classes(c.p.b, varname)
        return 'class', aList
    #@+node:ekr.20110510120621.14543: *6* ac.lookup_functions/methods/modules
    def lookup_functions(self, prefix):
        aList = codewise.cmd_functions([prefix])
        hits = [z.split(None, 1) for z in aList if z.strip()]
        return self.clean(hits)

    def lookup_methods(self, aList, prefix): # prefix not used, only aList[0] used.
        aList = codewise.cmd_members([aList[0]])
        hits = [z.split(None, 1) for z in aList if z.strip()]
        return self.clean(hits)

    def lookup_modules(self, aList, prefix): # prefix not used, only aList[0] used.
        aList = codewise.cmd_functions([aList[0]])
        hits = [z.split(None, 1) for z in aList if z.strip()]
        return self.clean(hits)
    #@+node:ekr.20110509064011.14557: *5* ac.get_leo_completions
    def get_leo_completions(self, prefix):
        '''Return completions in an environment defining c, g and p.'''
        trace = False and not g.unitTesting
        verbose = False
        aList = []
        for d in self.namespaces + [self.get_leo_namespace(prefix)]:
            if trace: g.trace(list(d.keys()))
            aList.extend(self.attr_matches(prefix, d))
        aList.sort()
        if trace:
            if verbose:
                g.trace('prefix', repr(prefix), 'aList...\n', g.listToString(aList))
            else:
                g.trace('len(aList): %3s, prefix: %s' % (len(aList), repr(prefix)))
        return aList
    #@+node:ekr.20110512090917.14466: *4* ac.get_leo_namespace
    def get_leo_namespace(self, prefix):
        '''
        Return an environment in which to evaluate prefix.
        Add some common standard library modules as needed.
        '''
        trace = False and not g.unitTesting
        k = self.k
        d = {'c': k.c, 'p': k.c.p, 'g': g}
        aList = prefix.split('.')
        if len(aList) > 1:
            name = aList[0]
            m = sys.modules.get(name)
            if m:
                d[name] = m
        if trace:
            g.trace('prefix', prefix, 'aList', aList)
            for key in sorted(d.keys()):
                g.trace(key, d.get(key))
        return d
    #@+node:ekr.20110512170111.14472: *4* ac.get_object
    def get_object(self):
        '''Return the object corresponding to the current prefix.'''
        trace = False and not g.unitTesting
        common_prefix, prefix1, aList = self.compute_completion_list()
        if not aList:
            if trace: g.trace('no completion list for: %s' % (prefix1))
            return None, prefix1
        elif len(aList) == 1:
            prefix = aList[0]
        else:
            prefix = common_prefix
        if prefix.endswith('.') and self.use_qcompleter:
            prefix += self.qcompleter.get_selection()
        if trace: g.trace(repr(prefix))
        safe_prefix = self.strip_brackets(prefix)
        for d in self.namespaces + [self.get_leo_namespace(prefix)]:
            try:
                obj = eval(safe_prefix, d)
                break # only reached if none of the exceptions below occur
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
    def info(self):
        '''Show the docstring for the present completion.'''
        c = self.c
        obj, prefix = self.get_object()
        c.frame.log.clearTab('Info', wrap='word')
        put = lambda s: self.put('', s, tabName='Info')
        put(prefix)
        try:
            argspec = inspect.getargspec(obj)
            # uses None instead of empty list
            argn = len(argspec.args or [])
            defn = len(argspec.defaults or [])
            put("args:")
            simple_args = argspec.args[: argn - defn]
            if not simple_args:
                put('    (none)')
            else:
                put('    ' + ', '.join(' ' + i for i in simple_args))
            put("keyword args:")
            if not argspec.defaults:
                put('    (none)')
            for i in range(defn):
                arg = argspec.args[-defn + i]
                put("    %s = %s" % (arg, repr(argspec.defaults[i])))
            if argspec.varargs:
                put("varargs: *" + argspec.varargs)
            if argspec.keywords:
                put("keywords: **" + argspec.keywords)
            put('\n') # separate docstring
        except TypeError:
            put('\n') # not a callable
        doc = inspect.getdoc(obj)
        put(doc if doc else "No docstring for " + repr(prefix))
    #@+node:ekr.20110510071925.14586: *4* ac.init_qcompleter
    def init_qcompleter(self, event=None):
        trace = False and not g.unitTesting
        # Compute the prefix and the list of options.
        prefix = self.get_autocompleter_prefix()
        options = self.get_completions(prefix)
        if trace: g.trace('prefix: %s, len(options): %s' % (repr(prefix), len(options)))
        w = self.c.frame.body.wrapper.widget
            # A LeoQTextBrowser.  May be none for unit tests.
        if w and options:
            self.qw = w
            self.qcompleter = w.init_completer(options)
            self.auto_completer_state_handler(event)
        else:
            if not g.unitTesting:
                g.warning('No completions')
            self.exit()
    #@+node:ekr.20110511133940.14552: *4* ac.init_tabcompleter
    def init_tabcompleter(self, event=None):
        # Compute the prefix and the list of options.
        prefix = self.get_autocompleter_prefix()
        options = self.get_completions(prefix)
        if options:
            self.clearTabName() # Creates the tabbed pane.
            self.auto_completer_state_handler(event)
        else:
            g.warning('No completions')
            self.exit()
    #@+node:ekr.20061031131434.39: *4* ac.insert_general_char
    def insert_general_char(self, ch):
        trace = False and not g.unitTesting
        k, w = self.k, self.w
        if trace: g.trace(repr(ch))
        if g.isWordChar(ch):
            self.insert_string(ch)
            common_prefix, prefix, aList = self.compute_completion_list()
            if trace: g.trace('ch', repr(ch), 'prefix', repr(prefix), 'len(aList)', len(aList))
            if not aList:
                if self.forbid_invalid: # 2011/06/17.
                    # Delete the character we just inserted.
                    self.do_backspace()
            elif self.auto_tab and len(common_prefix) > len(prefix):
                extend = common_prefix[len(prefix):]
                if trace: g.trace('*** extend', extend)
                ins = w.getInsertPoint()
                w.insert(ins, extend)
        else:
            if ch == '(' and k.enable_calltips:
                # This calls self.exit if the '(' is valid.
                self.calltip()
            else:
                if trace: g.trace('ch', repr(ch), 'calling exit')
                self.insert_string(ch)
                self.exit()
    #@+node:ekr.20061031131434.31: *4* ac.insert_string
    def insert_string(self, s, select=False):
        '''Insert s at the insertion point.'''
        c = self.c
        w = self.w
        if not g.isTextWrapper(w): # Bug fix: 2016/10/29.
            return
        c.widgetWantsFocusNow(w)
        i = w.getInsertPoint()
        w.insert(i, s)
        if select:
            j = i + len(s)
            w.setSelectionRange(i, j, insert=j)
        c.frame.body.onBodyChanged('Typing')
        if self.use_qcompleter:
            # g.trace(self.qw.leo_qc)
            if self.qw:
                c.widgetWantsFocusNow(self.qw.leo_qc)
    #@+node:ekr.20110314115639.14269: *4* ac.is_leo_source_file
    def is_leo_source_file(self):
        '''Return True if this is one of Leo's source files.'''
        c = self.c
        table = (z.lower() for z in (
            'leoDocs.leo',
            'LeoGui.leo', 'LeoGuiPluginsRef.leo',
            'leoPlugins.leo', 'leoPluginsRef.leo',
            'leoPy.leo', 'leoPyRef.leo',
            'myLeoSettings.leo', 'leoSettings.leo',
            'ekr.leo',
            # 'test.leo',
        ))
        return c.shortFileName().lower() in table
    #@+node:ekr.20101101175644.5891: *4* ac.put
    def put(self, *args, **keys):
        '''Put s to the given tab.

        May be overridden in subclasses.'''
        # print('autoCompleter.put',args,keys)
        if g.unitTesting:
            pass
        else:
            g.es(*args, **keys)
    #@+node:ekr.20110511133940.14561: *4* ac.show_completion_list & helpers
    def show_completion_list(self, common_prefix, prefix, tabList):
        c = self.c
        aList = common_prefix.split('.')
        header = '.'.join(aList[: -1])
        # g.trace(self.use_qcompleter,len(tabList))
        if self.verbose or self.use_qcompleter or len(tabList) < 20:
            tabList = self.clean_completion_list(header, tabList,)
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
    def clean_completion_list(self, header, tabList):
        '''Return aList with header removed from the start of each list item.'''
        return [
            z[len(header) + 1:] if z.startswith(header) else z
                for z in tabList]
    #@+node:ekr.20110513104728.14454: *5* ac.get_summary_list
    def get_summary_list(self, header, tabList):
        '''Show the possible starting letters,
        but only if there are more than one.
        '''
        d = {}
        for z in tabList:
            tail = z[len(header):] if z else ''
            if tail.startswith('.'): tail = tail[1:]
            ch = tail[0] if tail else ''
            if ch:
                n = d.get(ch, 0)
                d[ch] = n + 1
        aList = ['%s %d' % (ch2, d.get(ch2)) for ch2 in sorted(d)]
        if len(aList) > 1:
            tabList = aList
        else:
            tabList = self.clean_completion_list(header, tabList)
        return tabList
    #@+node:ekr.20061031131434.46: *4* ac.start
    def start(self, event):
        # We don't need to clear this now that we don't use ContextSniffer.
        # self.completionsDict = {}
        if self.use_qcompleter:
            self.init_qcompleter(event)
        else:
            self.init_tabcompleter(event)
    #@+node:ekr.20110512170111.14471: *4* ac.strip_brackets
    def strip_brackets(self, s):
        '''Return s with all brackets removed.

        This (mostly) ensures that eval will not execute function calls, etc.
        '''
        for ch in '[]{}()':
            s = s.replace(ch, '')
        return s
    #@-others
#@+node:ekr.20110312162243.14260: ** class ContextSniffer
class ContextSniffer(object):
    """ Class to analyze surrounding context and guess class

    For simple dynamic code completion engines.
    """

    def __init__(self):
        self.vars = {}
            # Keys are var names; values are list of classes
    #@+others
    #@+node:ekr.20110312162243.14261: *3* get_classes
    def get_classes(self, s, varname):
        '''Return a list of classes for string s.'''
        self.push_declarations(s)
        aList = self.vars.get(varname, [])
        return aList
    #@+node:ekr.20110312162243.14262: *3* set_small_context
    # def set_small_context(self, body):
        # """ Set immediate function """
        # self.push_declarations(body)
    #@+node:ekr.20110312162243.14263: *3* push_declarations & helper
    def push_declarations(self, s):
        for line in s.splitlines():
            line = line.lstrip()
            if line.startswith('#'):
                line = line.lstrip('#')
                parts = line.split(':')
                if len(parts) == 2:
                    a, b = parts
                    self.declare(a.strip(), b.strip())
    #@+node:ekr.20110312162243.14264: *4* declare
    def declare(self, var, klass):
        vars = self.vars.get(var, [])
        if not vars:
            self.vars[var] = vars
        vars.append(klass)
    #@-others
#@+node:ekr.20140813052702.18194: ** class FileNameChooser
class FileNameChooser(object):
    '''A class encapsulation file selection & completion logic.'''
    #@+others
    #@+node:ekr.20140813052702.18195: *3* fnc.__init__
    def __init__(self, c):
        '''Ctor for FileNameChooser class.'''
        # g.trace('(FileNameChooser)',c.shortFileName(),g.callers())
        self.c = c
        self.k = c.k
        assert c and c.k
        self.log = c.frame.log or g.NullObject()
        self.callback = None
        self.filterExt = None
        self.log = None # inited later.
        self.prompt = None
        self.tabName = None
    #@+node:ekr.20140813052702.18196: *3* fnc.compute_tab_list
    def compute_tab_list(self):
        '''Compute the list of completions.'''
        trace = False and not g.unitTesting
        path = self.get_label()
        # Fix bug 215: insert-file-name doesn't process ~
        # https://github.com/leo-editor/leo-editor/issues/215
        path = g.os_path_expanduser(path)
        sep = os.path.sep
        if g.os_path_exists(path):
            if trace: g.trace('existing directory', path)
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
            if trace: g.trace('does not exist', path)
            if path and path.endswith(sep):
                path = path[: -1]
            aList = g.glob_glob(path + '*')
            tabList = [z + sep if g.os_path_isdir(z) else z for z in aList]
        if self.filterExt:
            for ext in self.filterExt:
                tabList = [z for z in tabList if not z.endswith(ext)]
        tabList = [g.os_path_normslashes(z) for z in tabList]
        junk, common_prefix = g.itemsMatchingPrefixInList(path, tabList)
        if trace: g.trace('common_prefix', common_prefix)
        return common_prefix, tabList
    #@+node:ekr.20140813052702.18197: *3* fnc.do_back_space
    def do_back_space(self):
        '''Handle a back space.'''
        w = self.c.k.w
        if w and w.hasSelection():
            # s = w.getAllText()
            i, j = w.getSelectionRange()
            w.delete(i, j)
            s = self.get_label()
        else:
            s = self.get_label()
            if s:
                s = s[: -1]
            self.set_label(s)
        if s:
            common_prefix, tabList = self.compute_tab_list()
            # Do *not* extend the label to the common prefix.
        else:
            tabList = []
        self.show_tab_list(tabList)
    #@+node:ekr.20140813052702.18198: *3* fnc.do_char
    def do_char(self, char):
        '''Handle a non-special character.'''
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
            self.set_label(self.get_label()[: -1])
            self.extend_label(char)
    #@+node:ekr.20140813052702.18199: *3* fnc.do_tab
    def do_tab(self):
        '''Handle tab completion.'''
        old = self.get_label()
        common_prefix, tabList = self.compute_tab_list()
        self.show_tab_list(tabList)
        if len(tabList) == 1:
            common_prefix = tabList[0]
            self.set_label(common_prefix)
        elif len(common_prefix) > len(old):
            self.set_label(common_prefix)
    #@+node:ekr.20140813052702.18200: *3* fnc.get_file_name (entry)
    def get_file_name(self, event, callback, filterExt, prompt, tabName):
        '''Get a file name, supporting file completion.'''
        trace = False and not g.unitTesting
        c, k = self.c, self.c.k
        tag = 'get-file-name'
        state = k.getState(tag)
        char = event.char if event else ''
        if trace:
            g.trace('state', state, 'char', char or '<**no char**>')
        if state == 0:
            # Re-init all ivars.
            self.log = c.frame.log or g.NullObject()
            self.callback = callback
            self.filterExt = filterExt or ['.pyc', '.bin',]
            self.prompt = prompt
            self.tabName = tabName
            join = g.os_path_finalize_join
            finalize = g.os_path_finalize
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
    def extend_label(self, s):
        '''Extend the label by s.'''
        self.c.k.extendLabel(s, select=False, protect=False)

    def get_label(self):
        '''Return the label, not including the prompt.'''
        return self.c.k.getLabel(ignorePrompt=True)

    def set_label(self, s):
        '''Set the label after the prompt to s. The prompt never changes.'''
        self.c.k.setLabel(self.prompt, protect=True)
        self.c.k.extendLabel(s or '', select=False, protect=False)
    #@+node:ekr.20140813052702.18202: *3* fnc.show_tab_list
    def show_tab_list(self, tabList):
        '''Show the tab list in the log tab.'''
        self.log.clearTab(self.tabName)
        s = g.os_path_finalize(os.curdir) + os.sep
        es = []
        for path in tabList:
            theDir, fileName = g.os_path_split(path)
            s = theDir if path.endswith(os.sep) else fileName
            s = fileName or g.os_path_basename(theDir) + os.sep
            es.append(s)
        g.es('', '\n'.join(es), tabName=self.tabName)
    #@-others
#@+node:ekr.20140816165728.18940: ** class GetArg
class GetArg(object):
    '''
    A class encapsulating all k.getArg logic.

    k.getArg maps to ga.get_arg, which gets arguments in the minibuffer.

    For details, see the docstring for ga.get_arg
    '''
    #@+others
    #@+node:ekr.20140818052417.18241: *3* ga.birth
    #@+node:ekr.20140816165728.18952: *4* ga.__init__
    def __init__(self, c, prompt='full-command: ', tabName='Completion'):
        '''Ctor for GetArg class.'''
        # Common ivars.
        self.c = c
        self.k = c.k
        assert c
        assert c.k
        self.log = c.frame.log or g.NullObject()
        self.tabName = tabName
        # State vars.
        self.after_get_arg_state = None, None, None
        self.arg_completion = True
        self.handler = None
        self.tabList = []
        # Tab cycling ivars...
        self.cycling_prefix = None
        self.cycling_index = -1
        self.cycling_tabList = []
        # The following are k globals.
            # k.arg.
            # k.argSelectedText
            # k.oneCharacterArg
    #@+node:ekr.20140817110228.18321: *3* ga.compute_tab_list
    # Called from k.doTabCompletion: with tabList = list(c.commandsDict.keys())

    def compute_tab_list(self, tabList, backspace=False, allow_empty_completion=False):
        '''Compute and show the available completions.'''
        # Support vim-mode commands.
        command = self.get_label()
        # g.trace(len(tabList), self.is_command(command),command)
        if self.is_command(command):
            # if trace: g.trace('\n'.join(tabList))
            tabList, common_prefix = g.itemsMatchingPrefixInList(command, tabList)
            return common_prefix, tabList
                # note order.
        else:
            # For now, disallow further completions if something follows the command.
            command = self.get_command(command)
            return command, [command]
    #@+node:ekr.20140816165728.18965: *3* ga.do_back_space (entry)
    # Called from k.fullCommand: with defaultTabList = list(c.commandsDict.keys())

    def do_back_space(self, tabList, completion=True):
        '''Handle a backspace and update the completion list.'''
        trace = False and not g.unitTesting
        k = self.k
        self.tabList = tabList[:] if tabList else []
        if trace: g.trace('len(ga.tabList)', len(self.tabList))
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
            # Fix #323: https://github.com/leo-editor/leo-editor/issues/323
            common_prefix, tabList = self.compute_tab_list(tabList)
            self.show_tab_list(tabList)
            self.reset_tab_cycling()
    #@+node:ekr.20140817110228.18323: *3* ga.do_tab (entry) & helpers
    # Used by ga.get_arg and k.fullCommand.

    def do_tab(self, tabList, completion=True):
        '''Handle tab completion when the user hits a tab.'''
        trace = False and not g.unitTesting
        # g.trace('\n'+'\n'.join([z for z in tabList if z.startswith('@')]))
        c = self.c
        if completion:
            tabList = self.tabList = tabList[:] if tabList else []
            if trace: g.trace('len(ga.tabList)', len(tabList))
            # command = ga.get_label()
            common_prefix, tabList = self.compute_tab_list(tabList)
            if self.cycling_prefix and not self.cycling_prefix.startswith(common_prefix):
                self.cycling_prefix = common_prefix
            if trace:
                g.trace('len(tabList): %s common_prefix: %r cycling_prefix: %r' % (
                    len(tabList), common_prefix, self.cycling_prefix))
                g.printList(tabList)
            # No tab cycling for completed commands having
            # a 'tab_callback' attribute.
            if len(tabList) == 1 and self.do_tab_callback():
                return
            else:
                # Fix #323: https://github.com/leo-editor/leo-editor/issues/323
                # A big simplifcation: always call ga.do_tab_list
                self.do_tab_cycling(common_prefix, tabList)

        c.minibufferWantsFocus()
    #@+node:ekr.20140818145250.18235: *4* ga.do_tab_callback
    def do_tab_callback(self):
        '''
        If the command-name handler has a tab_callback,
        call handler.tab_callback() and return True.
        '''
        trace = False and not g.unitTesting
        c, k = self.c, self.k
        commandName, tail = k.getMinibufferCommandName()
        handler = c.commandsDict.get(commandName)
        if trace: g.trace(commandName, handler and handler.__name__ or 'None')
        if hasattr(handler, 'tab_callback'):
            self.reset_tab_cycling()
            k.functionTail = tail
                # For k.getFileName.
            handler.tab_callback()
            return True
        else:
            return False
    #@+node:ekr.20140819050118.18317: *4* ga.do_tab_cycling
    def do_tab_cycling(self, common_prefix, tabList):
        '''Put the next (or first) completion in the minibuffer.'''
        trace = False and not g.unitTesting
        s = self.get_label()
        if trace:
            g.trace('===== label: %r prefix: %r len(tabList): %s' % (
                s, self.cycling_prefix, len(tabList)))
        if not common_prefix:
            # Leave the minibuffer as it is.
            if trace: g.trace('0: NO COMMON PREFIX')
            self.show_tab_list(tabList)
        # Fix #323: https://github.com/leo-editor/leo-editor/issues/323
        elif (
            self.cycling_prefix and
            s.startswith(self.cycling_prefix) and
            sorted(self.cycling_tabList) == sorted(tabList) # Bug fix: 2016/10/14
        ):
            if trace: g.trace('1: CYCLE: %s %r: tabList[0]: %r' % (
                self.cycling_index, s, tabList and tabList[0] or '<none>'))
            n = self.cycling_index
            n = self.cycling_index = n + 1 if n + 1 < len(self.cycling_tabList) else 0
            self.set_label(self.cycling_tabList[n])
            self.show_tab_list(self.cycling_tabList)
        else:
            # Restart.
            if trace:
                g.trace('2: RESTART: %r:' % (s))
                g.printList(tabList)
            self.show_tab_list(tabList)
            self.cycling_tabList = tabList[:]
            self.cycling_prefix = common_prefix
            self.set_label(common_prefix)
            if tabList and common_prefix == tabList[0]:
                if trace: g.trace('select the first command.')
                self.cycling_index = 0
            else:
                if trace: g.trace('show common prefix.')
                self.cycling_index = -1
    #@+node:ekr.20140819050118.18318: *4* ga.reset_tab_cycling
    def reset_tab_cycling(self):
        '''Reset all tab cycling ivars.'''
        self.cycling_prefix = None
        self.cycling_index = -1
        self.cycling_tabList = []
    #@+node:ekr.20140816165728.18958: *3* ga.extend/get/set_label
    # Not useful because k.entendLabel doesn't handle selected text.
    if 0:

        def extend_label(self, s):
            '''Extend the label by s.'''
            self.c.k.extendLabel(s, select=False, protect=False)

    def get_label(self):
        '''Return the label, not including the prompt.'''
        return self.c.k.getLabel(ignorePrompt=True)

    def set_label(self, s):
        '''Set the label after the prompt to s. The prompt never changes.'''
        k = self.c.k
        # Using k.mb_prefix is simplest.  No ga.ivars need be inited.
        k.setLabel(k.mb_prefix, protect=True)
        k.extendLabel(s or '', select=False, protect=False)
    #@+node:ekr.20140816165728.18941: *3* ga.get_arg (entry) & helpers
    def get_arg(self, event,
        returnKind=None, returnState=None, handler=None,
        tabList=None, completion=True, oneCharacter=False,
        stroke=None, useMinibuffer=True
    ):
        #@+<< ga.get_arg docstring >>
        #@+node:ekr.20140822051549.18299: *4* << ga.get_arg docstring >>
        '''
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

        '''
        #@-<< ga.get_arg docstring >>
        if tabList is None: tabList = []
        c, k = self.c, self.k
        state = k.getState('getArg')
        c.check_event(event)
        c.minibufferWantsFocusNow()
        char = event.char if event else ''
        if state > 0:
            k.setLossage(char, stroke)
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
    def cancel_after_state(self):

        self.after_get_arg_state = None
    #@+node:ekr.20140816165728.18955: *4* ga.do_char
    def do_char(self, event, char):
        '''Handle a non-special character.'''
        k = self.k
        k.updateLabel(event)
        # Any plain key resets tab cycling.
        self.reset_tab_cycling()
    #@+node:ekr.20140817110228.18316: *4* ga.do_end
    def do_end(self, event, char, stroke):
        '''A return or escape has been seen.'''
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
    def do_state_zero(self, completion, event, handler, oneCharacter,
        returnKind, returnState, tabList, useMinibuffer
    ):
        '''Do state 0 processing.'''
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
        k.argSelectedText = c.frame.body.wrapper.getSelectedText()
        k.functionTail = None
        k.oneCharacterArg = oneCharacter
        #
        # Do *not* change the label here!
        # Enter the next state.
        c.widgetWantsFocus(c.frame.body.wrapper)
        k.setState('getArg', 1, k.getArg)
        # pylint: disable=consider-using-ternary
        k.afterArgWidget = event and event.widget or c.frame.body.wrapper
        if useMinibuffer: c.minibufferWantsFocus()
    #@+node:ekr.20140818103808.18234: *4* ga.should_end
    def should_end(self, char, stroke):
        '''Return True if ga.get_arg should return.'''
        k = self.k
        return (
            char in ('\n', 'Return',) or
            k.oneCharacterArg or
            stroke and stroke in k.getArgEscapes or
            char == '\t' and char in k.getArgEscapes
                # The Find Easter Egg.
        )
    #@+node:ekr.20140818103808.18235: *4* ga.trace_state
    def trace_state(self, char, completion, handler, state, stroke):
        '''Trace the vars and ivars.'''
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
    def get_command(self, s):
        '''Return the command part of a minibuffer contents s.'''
        trace = False and not g.unitTesting
        if s.startswith(':'):
            # A vim-like command.
            if len(s) == 1:
                if trace: g.trace(':x', s)
                return s
            elif s[1].isalpha():
                command = [':']
                for ch in s[1:]:
                    if ch.isalnum() or ch == '-':
                        command.append(ch)
                    else: break
                if trace: g.trace('alpha', ''.join(command))
                return ''.join(command)
            elif s.startswith(':%s'):
                if trace: g.trace(':%s', ''.join(command))
                return s[: 3]
            else:
                # Special case for :! and :% etc.
                if trace: g.trace(':...', ''.join(command))
                return s[: 2]
        else:
            command = []
            for ch in s:
                if ch.isalnum() or ch in '@_-':
                    command.append(ch)
                else: break
            if trace: g.trace('normal', ''.join(command))
            return ''.join(command)
    #@+node:ekr.20140818085719.18227: *3* ga.get_minibuffer_command_name
    def get_minibuffer_command_name(self):
        '''Return the command name in the minibuffer.'''
        s = self.get_label()
        command = self.get_command(s)
        tail = s[len(command):]
        # g.trace('command:',command,'tail:',tail)
        return command, tail
    #@+node:ekr.20140818074502.18221: *3* ga.is_command
    def is_command(self, s):
        '''Return False if something, even a blank, follows a command.'''
        if s.startswith('@'):
            return True
        elif s.startswith(':'):
            if len(s) == 1:
                return True
            elif s[1].isalpha():
                for ch in s[1:]:
                    if not ch.isalnum() and ch != '-':
                        return False
                return True
            else:
                # assert not s[1].isalpha()
                # Special case for :! and :% etc.
                return len(s) == 2
        else:
            for ch in s:
                if not ch.isalnum() and ch not in '_-':
                    return False
            return True
    #@+node:ekr.20140816165728.18959: *3* ga.show_tab_list & helper
    def show_tab_list(self, tabList):
        '''Show the tab list in the log tab.'''
        k = self.k
        self.log.clearTab(self.tabName)
        d = k.computeInverseBindingDict()
        data, legend, n = [], False, 0
        for commandName in tabList:
            dataList = d.get(commandName, [])
            if dataList:
                for z in dataList:
                    pane, key = z
                    s1a = '' if pane in ('all:', 'button:') else '%s ' % (pane)
                    s1b = k.prettyPrintKey(key)
                    s1 = s1a + s1b
                    s2 = self.command_source(commandName)
                    if s2 != ' ': legend = True
                    s3 = commandName
                    data.append((s1, s2, s3),)
                    n = max(n, len(s1))
            else:
                # Bug fix: 2017/03/26
                data.append(('',' ', commandName),)
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
    def command_source(self, commandName):
        '''
        Return the source legend of an @button/@command node.
        'G' leoSettings.leo
        'M' myLeoSettings.leo
        'L' local .leo File
        ' ' not an @command or @button node
        '''
        c = self.c
        if commandName.startswith('@'):
            d = c.commandsDict
            func = d.get(commandName)
            if hasattr(func, 'source_c'):
                c2 = func.source_c
                fn2 = c2.shortFileName().lower()
                if fn2.endswith('myleosettings.leo'):
                    return 'M'
                elif fn2.endswith('leosettings.leo'):
                    return 'G'
                else:
                    return 'L'
            else:
                return '?'
        else:
            return ' '
    #@-others
#@+node:ekr.20061031131434.74: ** class KeyHandlerClass
class KeyHandlerClass(object):
    '''
    A class to support emacs-style commands.
    c.k is an instance of this class.
    '''
    #@+others
    #@+node:ekr.20061031131434.75: *3*  k.Birth
    #@+node:ekr.20061031131434.76: *4* k.__init__& helpers
    def __init__(self, c):
        '''Create a key handler for c.'''
        trace = False and not g.unitTesting
        if trace: g.trace('(k)')
        self.c = c
        self.dispatchEvent = None
        self.fnc = None
            # A singleton defined in k.finishCreate.
        self.getArgInstance = None
            # A singleton defined in k.finishCreate.
        self.inited = False
            # Set at end of finishCreate.
        self.killedBindings = []
            # A list of commands whose bindings have been set to None in the local file.
        self.swap_mac_keys = False
            # How to init this??
        self.w = None
            # Note: will be None for NullGui.
        # Generalize...
        self.x_hasNumeric = ['sort-lines', 'sort-fields']
        self.altX_prompt = 'full-command: '
        # Access to data types defined in leoKeys.py
        self.KeyStroke = g.KeyStroke
        # Define all ivars...
        self.defineExternallyVisibleIvars()
        self.defineInternalIvars()
        self.reloadSettings()
        ### self.defineTkNames()
        ### self.defineSpecialKeys()
        self.defineSingleLineCommands()
        self.defineMultiLineCommands()
        self.autoCompleter = AutoCompleterClass(self)
        self.qcompleter = None # Set by AutoCompleter.start.
        self.setDefaultUnboundKeyAction()
        self.setDefaultEditingAction()
    #@+node:ekr.20061031131434.78: *5* k.defineExternallyVisibleIvars
    def defineExternallyVisibleIvars(self):
        self.abbrevOn = False
            # True: abbreviations are on.
        self.arg = ''
            # The value returned by k.getArg.
        self.argSelectedText = '' # The selected text in state 0.
        self.commandName = None # The name of the command being executed.
        self.funcReturn = None # For k.simulateCommand
        self.functionTail = None # For commands that take minibuffer arguments.
        # These are true globals
        self.getArgEscapes = []
        self.getArgEscapeFlag = False # A signal that the user escaped getArg in an unusual way.
        self.givenArgs = [] # New in Leo 4.4.8: arguments specified after the command name in k.simulateCommand.
        self.inputModeBindings = {}
        self.inputModeName = '' # The name of the input mode, or None.
        self.modePrompt = '' # The mode promopt.
        self.negativeArg = False
        self.newMinibufferWidget = None # Usually the minibuffer restores focus.  This overrides this default.
        # self.regx = g.bunch(iter=None,key=None)
        self.repeatCount = None
        self.state = g.bunch(kind=None, n=None, handler=None)
    #@+node:ekr.20061031131434.79: *5* k.defineInternalIvars
    def defineInternalIvars(self):
        '''Define internal ivars of the KeyHandlerClass class.'''
        self.abbreviationsDict = {}
            # Abbreviations created by @alias nodes.
        # Previously defined bindings...
        self.bindingsDict = {}
            # Keys are Tk key names, values are lists of BindingInfo objects.
        # Previously defined binding tags.
        self.bindtagsDict = {}
            # Keys are strings (the tag), values are 'True'
        self.commandHistory = []
        self.commandIndex = 0
            # List/stack of previously executed commands.
            # Up arrow will select commandHistory[commandIndex]
        self.masterBindingsDict = {}
            # Keys are scope names: 'all','text',etc. or mode names.
            # Values are dicts: keys are strokes, values are BindingInfo objects.
        self.masterGuiBindingsDict = {}
            # Keys are strokes; value is True;
        # Special bindings for k.fullCommand...
        self.mb_copyKey = None
        self.mb_pasteKey = None
        self.mb_cutKey = None
        # Keys whose bindings are computed by initSpecialIvars...
        self.abortAllModesKey = None
        self.autoCompleteForceKey = None
        self.demoNextKey = None # New support for the demo.py plugin.
        self.demoPrevKey = None # New support for the demo.py plugin.
        self.fullCommandKey = None
        self.universalArgKey = None
        # Used by k.masterKeyHandler...
        self.stroke = None
        self.mb_event = None
        self.mb_history = []
        self.mb_help = False
        self.mb_helpHandler = None
        # Important: these are defined in k.defineExternallyVisibleIvars...
            # self.getArgEscapes = []
            # self.getArgEscapeFlag
        # For onIdleTime...
        self.idleCount = 0
        # For modes...
        self.modeBindingsDict = {}
        self.modeWidget = None
        self.silentMode = False
    #@+node:ekr.20080509064108.7: *5* k.defineMultiLineCommands
    def defineMultiLineCommands(self):
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
            # SearchCommandsClass
            'change',
            'change-then-find',
            'find-next',
            'find-prev',
        ]
    #@+node:ekr.20080509064108.6: *5* k.defineSingleLineCommands
    def defineSingleLineCommands(self):
        k = self
        # These commands can be executed in the minibuffer.
        k.singleLineCommandList = [
            # EditCommandsClass
            'back-to-indentation',
            'back-to-home', # 2010/02/01
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
            # KeyHandlerCommandsClass
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
            'set-find-everywhere', # 2011/06/07
            'set-find-node-only', # 2011/06/07
            'set-find-suboutline-only', # 2011/06/07
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
    #@+node:ekr.20150509035028.1: *4* k.cmd (decorator)
    def cmd(name):
        '''Command decorator for the leoKeys class.'''
        # pylint: disable=no-self-argument
        return g.new_cmd_decorator(name, ['c', 'k',])
    #@+node:ekr.20061031131434.80: *4* k.finishCreate & helpers
    def finishCreate(self):
        '''
        Complete the construction of the keyHandler class.
        c.commandsDict has been created when this is called.
        '''
        trace = False and not g.unitTesting
        if trace: g.trace('(k)', self.c)
        c, k = self.c, self
        k.w = c.frame.miniBufferWidget
            # Will be None for NullGui.
        k.fnc = FileNameChooser(c)
            # A singleton. Defined here so that c.k will exist.
        k.getArgInstance = GetArg(c)
            # a singleton. Defined here so that c.k will exist.
        k.makeAllBindings()
            # Important: This must be called this now,
            # even though LM.laod calls g.app.makeAllBindings later.
        k.initCommandHistory()
        k.inited = True
        k.setDefaultInputState()
        k.resetLabel()
    #@+node:ekr.20061101071425: *4* k.oops
    def oops(self):
        g.trace('Should be defined in subclass:', g.callers(4))
    #@+node:ekr.20120217070122.10479: *4* k.reloadSettings
    def reloadSettings(self):
        # Part 1: These were in the ctor.
        c = self.c
        getBool = c.config.getBool
        getColor = c.config.getColor
        self.enable_autocompleter = getBool('enable_autocompleter_initially')
        self.enable_calltips = getBool('enable_calltips_initially')
        self.ignore_caps_lock = getBool('ignore_caps_lock')
        self.ignore_unbound_non_ascii_keys = getBool('ignore_unbound_non_ascii_keys')
        self.minibuffer_background_color = getColor('minibuffer_background_color') or 'lightblue'
        self.minibuffer_foreground_color = getColor('minibuffer_foreground_color') or 'black'
        self.minibuffer_warning_color = getColor('minibuffer_warning_color') or 'lightgrey'
        self.minibuffer_error_color = getColor('minibuffer_error_color') or 'red'
        self.swap_mac_keys = getBool('swap_mac_keys')
        self.warn_about_redefined_shortcuts = getBool('warn_about_redefined_shortcuts')
        # Has to be disabled (default) for AltGr support on Windows
        self.enable_alt_ctrl_bindings = c.config.getBool('enable_alt_ctrl_bindings')
        # Part 2: These were in finishCreate.
        # Set mode colors used by k.setInputState.
        bg = c.config.getColor('body_text_background_color') or 'white'
        fg = c.config.getColor('body_text_foreground_color') or 'black'
        self.command_mode_bg_color = getColor('command_mode_bg_color') or bg
        self.command_mode_fg_color = getColor('command_mode_fg_color') or fg
        self.insert_mode_bg_color = getColor('insert_mode_bg_color') or bg
        self.insert_mode_fg_color = getColor('insert_mode_fg_color') or fg
        self.overwrite_mode_bg_color = getColor('overwrite_mode_bg_color') or bg
        self.overwrite_mode_fg_color = getColor('overwrite_mode_fg_color') or fg
        self.unselected_body_bg_color = getColor('unselected_body_bg_color') or bg
        self.unselected_body_fg_color = getColor('unselected_body_fg_color') or bg
        # g.trace(self.c.shortFileName())
    #@+node:ekr.20110209093958.15413: *4* k.setDefaultEditingKeyAction (New)
    def setDefaultEditingAction(self):
        k = self; c = k.c
        action = c.config.getString('default_editing_state') or 'insert'
        action.lower()
        if action not in ('command', 'insert', 'overwrite'):
            g.trace('ignoring default_editing_state: %s' % (action))
            action = 'insert'
        self.defaultEditingAction = action
    #@+node:ekr.20061031131434.82: *4* k.setDefaultUnboundKeyAction
    def setDefaultUnboundKeyAction(self, allowCommandState=True):
        k = self; c = k.c
        # g.trace(g.callers())
        defaultAction = c.config.getString('top_level_unbound_key_action') or 'insert'
        defaultAction.lower()
        if defaultAction == 'command' and not allowCommandState:
            self.unboundKeyAction = 'insert'
        elif defaultAction in ('command', 'insert', 'overwrite'):
            self.unboundKeyAction = defaultAction
        else:
            g.trace('ignoring top_level_unbound_key_action setting: %s' % (defaultAction))
            self.unboundKeyAction = 'insert'
        # g.trace(self.unboundKeyAction)
        self.defaultUnboundKeyAction = self.unboundKeyAction
        k.setInputState(self.defaultUnboundKeyAction)
    #@+node:ekr.20061031131434.88: *3* k.Binding
    #@+node:ekr.20061031131434.89: *4* k.bindKey & helpers
    def bindKey(self, pane, shortcut, callback, commandName, modeFlag=False, tag=None):
        '''
        Bind the indicated shortcut (a Tk keystroke) to the callback.

        No actual gui bindings are made: only entries in k.masterBindingsDict
        and k.bindingsDict.

        tag gives the source of the binding.
        
        Return True if the binding was made successfully.
        '''
        trace = False and not g.unitTesting
        trace_list = False
        k = self
        if not shortcut:
            # Don't use this method to undo bindings.
            return False
        if not k.check_bind_key(commandName, pane, shortcut):
            return False
        aList = k.bindingsDict.get(shortcut, [])
        try:
            if not shortcut:
                stroke = None
            elif g.isStroke(shortcut):
                stroke = shortcut
                assert stroke.s, stroke
            else:
                assert shortcut, g.callers()
                stroke = g.KeyStroke(binding=shortcut)
            if trace:
                tag = tag.split(' ')[-1]
                g.trace('%7s %25r %17s %s' % (pane, stroke and stroke.s, tag, commandName))
                g.trace(g.callers())
            bi = g.BindingInfo(
                kind=tag,
                pane=pane,
                func=callback,
                commandName=commandName,
                stroke=stroke)
            if shortcut:
                k.bindKeyToDict(pane, shortcut, bi)
                    # Updates k.masterBindingsDict
            if shortcut and not modeFlag:
                aList = k.remove_conflicting_definitions(
                    aList, commandName, pane, shortcut)
                # 2013/03/02: a real bug fix.
            aList.append(bi)
            if shortcut:
                assert stroke
                k.bindingsDict[stroke] = aList
                if trace and trace_list: g.trace(shortcut, aList)
            return True
        except Exception: # Could be a user error.
            if g.unitTesting or not g.app.menuWarningsGiven:
                g.es_print('exception binding', shortcut, 'to', commandName)
                g.es_print_exception()
                g.app.menuWarningsGiven = True
            return False

    bindShortcut = bindKey # For compatibility
    #@+node:ekr.20120130074511.10228: *5* k.check_bind_key
    def check_bind_key(self, commandName, pane, stroke):
        '''
        Return True if the binding of stroke to commandName for the given
        pane can be made.
        '''
        # k = self
        assert g.isStroke(stroke)
        # Give warning and return if we try to bind to Enter or Leave.
        for s in ('enter', 'leave'):
            if stroke.lower().find(s) > -1:
                g.warning('ignoring invalid key binding:', '%s = %s' % (
                    commandName, stroke))
                return False
        if pane.endswith('-mode'):
            g.trace('oops: ignoring mode binding', stroke, commandName, g.callers())
            return False
        else:
            return True
    #@+node:ekr.20120130074511.10227: *5* k.kill_one_shortcut
    def kill_one_shortcut(self, stroke):
        '''
        Update the *configuration* dicts so that c.config.getShortcut(name)
        will return None for all names *presently* bound to the stroke.
        '''
        k = self; c = k.c
        lm = g.app.loadManager
        if 0:
            # This does not fix 327: Create a way to unbind bindings
            assert stroke in (None, 'None', 'none') or g.isStroke(stroke), repr(stroke)
        else:
            # A crucial shortcut: inverting and uninverting dictionaries is slow.
            # Important: the comparison is valid regardless of the type of stroke.
            if stroke in (None, 'None', 'none'):
                return
            assert g.isStroke(stroke), stroke
        d = c.config.shortcutsDict
        if d is None:
            d = g.TypedDictOfLists(
                name='empty shortcuts dict',
                keyType=type('commandName'),
                valType=g.BindingInfo)
        inv_d = lm.invert(d)
        # g.trace('1', stroke, stroke in c.config.shortcutsDict.d)
        inv_d[stroke] = []
        c.config.shortcutsDict = lm.uninvert(inv_d)
        # g.trace('2', stroke, stroke in c.config.shortcutsDict.d)
        # g.trace('3', c.config.shortcutsDict.d.get('help'))
    #@+node:ekr.20061031131434.92: *5* k.remove_conflicting_definitions
    def remove_conflicting_definitions(self, aList, commandName, pane, shortcut):
        trace = False and not g.unitTesting
        k = self
        result = []
        for bi in aList:
            if pane in ('button', 'all', bi.pane):
                if trace:
                    # This is too annoying to report here. See bug 951921.
                    g.es_print('c for %s in %s' % (
                        bi.stroke, k.c.shortFileName()))
                    g.es_print('previous: %s new: %s' % (
                        bi.commandName, commandName))
                k.kill_one_shortcut(shortcut)
            else:
                result.append(bi)
        return result
    #@+node:ekr.20061031131434.93: *5* k.bindKeyToDict
    def bindKeyToDict(self, pane, stroke, bi):
        '''Update k.masterBindingsDict for the stroke.'''
        # New in Leo 4.4.1: Allow redefintions.
        # Called from makeBindingsFromCommandsDict.
        trace = False and not g.unitTesting
        k = self
        assert g.isStroke(stroke), stroke
        d = k.masterBindingsDict.get(pane, {})
        d[stroke] = bi
        k.masterBindingsDict[pane] = d
        if trace and bi.commandName.startswith('goto-next-visible'):
            g.trace(
                '%4s %10s' % (pane, stroke.s),
                bi.commandName,
                bi.func.__name__)
    #@+node:ekr.20061031131434.94: *5* k.bindOpenWith
    def bindOpenWith(self, d):
        '''Register an open-with command.'''
        k = self; c = k.c
        shortcut = d.get('shortcut') or ''
        name = d.get('name')
        # The first parameter must be event, and it must default to None.

        def openWithCallback(event=None, c=c, d=d):
            return c.openWith(d=d)

        # Use k.registerCommand to set the shortcuts in the various binding dicts.
        commandName = 'open-with-%s' % name.lower()
        k.registerCommand(
            allowBinding=True,
            commandName=commandName,
            func=openWithCallback,
            pane='all',
            shortcut=shortcut,
        )
    #@+node:ekr.20061031131434.95: *4* k.checkBindings
    def checkBindings(self):
        '''Print warnings if commands do not have any @shortcut entry.
        The entry may be `None`, of course.'''
        k = self; c = k.c
        if not c.config.getBool('warn_about_missing_settings'): return
        for name in sorted(c.commandsDict):
            abbrev = k.abbreviationsDict.get(name)
            key = c.frame.menu.canonicalizeMenuName(abbrev or name)
            key = key.replace('&', '')
            if not c.config.exists(key, 'shortcut'):
                if abbrev:
                    g.trace('No shortcut for abbrev %s -> %s = %s' % (
                        name, abbrev, key))
                else:
                    g.trace('No shortcut for %s = %s' % (name, key))
    #@+node:ekr.20061031131434.97: *4* k.completeAllBindings
    def completeAllBindings(self, w=None):
        '''New in 4.4b3: make an actual binding in *all* the standard places.

        The event will go to k.masterKeyHandler as always, so nothing really changes.
        except that k.masterKeyHandler will know the proper stroke.'''
        # g.trace(w)
        k = self
        for stroke in k.bindingsDict:
            assert g.isStroke(stroke), repr(stroke)
            k.makeMasterGuiBinding(stroke, w=w)
    #@+node:ekr.20061031131434.96: *4* k.completeAllBindingsForWidget
    def completeAllBindingsForWidget(self, w):
        '''Make all a master gui binding for widget w.'''
        k = self
        for stroke in k.bindingsDict:
            assert g.isStroke(stroke), repr(stroke)
            k.makeMasterGuiBinding(stroke, w=w)
    #@+node:ekr.20070218130238: *4* k.dumpMasterBindingsDict
    def dumpMasterBindingsDict(self):
        '''Dump k.masterBindingsDict.'''
        k = self; d = k.masterBindingsDict
        g.pr('\nk.masterBindingsDict...\n')
        for key in sorted(d):
            g.pr(key, '-' * 40)
            d2 = d.get(key)
            for key2 in sorted(d2):
                bi = d2.get(key2)
                g.pr('%20s %s' % (key2, bi.commandName))
    #@+node:ekr.20061031131434.99: *4* k.initAbbrev & helper
    def initAbbrev(self):
        k = self; c = k.c; d = c.config.getAbbrevDict()
        if d:
            for key in d:
                commandName = d.get(key)
                if commandName.startswith('press-') and commandName.endswith('-button'):
                    pass # Must be done later in k.registerCommand.
                else:
                    self.initOneAbbrev(commandName, key)
    #@+node:ekr.20130924035029.12741: *5* k.initOneAbbrev
    def initOneAbbrev(self, commandName, key):
        '''Enter key as an abbreviation for commandName in c.commandsDict.'''
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
    def initSpecialIvars(self):
        '''Set ivars for special keystrokes from previously-existing bindings.'''
        c, k = self.c, self
        warn = c.config.getBool('warn_about_missing_settings')
        for ivar, commandName in (
            ('fullCommandKey', 'full-command'),
            ('abortAllModesKey', 'keyboard-quit'),
            ('universalArgKey', 'universal-argument'),
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
                        found = True; break
            if not found and warn:
                g.trace('no setting for %s' % commandName)
    #@+node:ekr.20061031131434.98: *4* k.makeAllBindings
    def makeAllBindings(self):
        '''Make all key bindings in all of Leo's panes.'''
        trace = False and not g.unitTesting
        if trace: t1 = time.clock()
        k = self
        k.bindingsDict = {}
        k.addModeCommands()
        k.makeBindingsFromCommandsDict()
        k.initSpecialIvars()
        k.initAbbrev()
        k.completeAllBindings()
        k.checkBindings()
        if trace: g.trace('%4.2f sec.' % (time.clock()-t1))
    #@+node:ekr.20061031131434.102: *4* k.makeBindingsFromCommandsDict
    def makeBindingsFromCommandsDict(self):
        '''Add bindings for all entries in c.commandsDict.'''
        trace = False and not g.unitTesting
        c, k = self.c, self
        d = c.commandsDict
        t1 = time.time()
        # Step 1: Create d2.
        # Keys are strokes. Values are lists of bi with bi.stroke == stroke.
        d2 = g.TypedDictOfLists(
            name='makeBindingsFromCommandsDict helper dict',
            keyType=g.KeyStroke,
            valType=g.BindingInfo)
        for commandName in sorted(d):
            command = d.get(commandName)
            key, aList = c.config.getShortcut(commandName)
            for bi in aList:
                if trace and commandName == 'help':
                    g.trace(key, repr(bi.stroke), aList)
                # Important: bi.stroke is already canonicalized.
                stroke = bi.stroke
                bi.commandName = commandName
                if stroke:
                    assert g.isStroke(stroke)
                    d2.add(stroke, bi)
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
        t2 = time.time()
        if trace:
            g.trace('%0.2f sec %s' % ((t2 - t1), c.shortFileName()))
    #@+node:ekr.20061031131434.103: *4* k.makeMasterGuiBinding
    def makeMasterGuiBinding(self, stroke, w=None, trace=False):
        '''Make a master gui binding for stroke in pane w, or in all the standard widgets.'''
        trace = False and not g.unitTesting
        k = self; c = k.c; f = c.frame
        if w:
            widgets = [w]
        else:
            # New in Leo 4.5: we *must* make the binding in the binding widget.
            bindingWidget = f.tree and hasattr(f.tree, 'bindingWidget') and f.tree.bindingWidget or None
            wrapper = f.body and hasattr(f.body, 'wrapper') and f.body.wrapper or None
            canvas = f.tree and hasattr(f.tree, 'canvas') and f.tree.canvas or None
            widgets = (c.miniBufferWidget, wrapper, canvas, bindingWidget)
        for w in widgets:
            if not w: continue
            # Make the binding only if no binding for the stroke exists in the widget.
            aList = k.masterGuiBindingsDict.get(stroke, [])
            if w not in aList:
                aList.append(w)
                k.masterGuiBindingsDict[stroke] = aList
        if trace: g.trace(len(aList), stroke)
    #@+node:ekr.20150402111403.1: *3* k.Command history
    #@+node:ekr.20150402111413.1: *4* k.addToCommandHistory
    def addToCommandHistory(self, commandName):
        '''Add a name to the command history.'''
        k = self
        h = k.commandHistory
        if commandName in h:
            h.remove(commandName)
        h.append(commandName)
        k.commandIndex = None
        # g.trace(commandName,h)
    #@+node:ekr.20150402165918.1: *4* k.commandHistoryDown
    def commandHistoryFwd(self):
        '''
        Move down the Command History - fall off the bottom (return empty string)
        if necessary
        '''
        k = self
        h, i = k.commandHistory, k.commandIndex
        if h:
            commandName = ''
            if i == len(h) -1:
                # fall off the bottom
                i = None
            elif i != None:
                # move to next down in list
                i += 1
                commandName = h[i]
            # (else i == None; no change to index, command == '')
            # g.trace(i,h)
            k.commandIndex = i
            k.setLabel(k.mb_prefix + commandName)
    #@+node:ekr.20150402171131.1: *4* k.commandHistoryUp
    def commandHistoryBackwd(self):
        '''
        Return the previous entry in the Command History - stay at the top
        if we are there
        '''
        k = self
        h, i = k.commandHistory, k.commandIndex
        if h:
            if i == None:
                # first time in - set to last entry
                i = len(h) -1
            elif i > 0:
                i -= 1
            commandName = h[i]
            k.commandIndex = i
            # g.trace(i,h)
            k.setLabel(k.mb_prefix + commandName)
    #@+node:ekr.20150425143043.1: *4* k.initCommandHistory
    def initCommandHistory(self):
        '''Init command history from @data command-history nodes.'''
        k, c = self, self.c
        aList = c.config.getData('history-list') or []
        for command in reversed(aList):
            k.addToCommandHistory(command)

    def resetCommandHistory(self):
        ''' reset the command history index to indicate that
            we are pointing 'past' the last entry
        '''
        self.commandIndex = None
        #
    #@+node:ekr.20150402111935.1: *4* k.sortCommandHistory
    def sortCommandHistory(self):
        '''Sort the command history.'''
        k = self
        k.commandHistory.sort()
        k.commandIndex = None
    #@+node:ekr.20061031131434.104: *3* k.Dispatching
    #@+node:ekr.20061031131434.111: *4* k.fullCommand (alt-x) & helper
    @cmd('full-command')
    def fullCommand(self, event, specialStroke=None, specialFunc=None, help=False, helpHandler=None):
        '''Handle 'full-command' (alt-x) mode.'''
        trace = False and not g.unitTesting
        verbose = False
        try:
            k = self; c = k.c
            state = k.getState('full-command')
            helpPrompt = 'Help for command: '
            c.check_event(event)
            ch = char = event.char if event else ''
            stroke = event.stroke if event else ''
            ### g.trace('char', repr(char), 'stroke', repr(stroke))
            if trace: g.trace('state', state, repr(char))
            if state > 0:
                k.setLossage(char, stroke)
            if state == 0:
                k.mb_event = event # Save the full event for later.
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
                if trace and verbose: g.trace('***Return')
                # if trace and trace_event:
                    # g.trace('hasSelection %r' % (
                        # k.mb_event and k.mb_event.w and k.mb_event.w.hasSelection()))
                # Fix bug 157: save and restore the selection.
                w = k.mb_event and k.mb_event.w
                if w and hasattr(w, 'hasSelection') and w.hasSelection():
                    sel1, sel2 = w.getSelectionRange()
                    ins = w.getInsertPoint()
                    c.frame.log.deleteTab('Completion')
                    w.setSelectionRange(sel1, sel2, insert=ins)
                else:
                    c.frame.log.deleteTab('Completion')
                        # 2016/04/27
                if k.mb_help:
                    s = k.getLabel()
                    commandName = s[len(helpPrompt):].strip()
                    k.clearState()
                    k.resetLabel()
                    if k.mb_helpHandler: k.mb_helpHandler(commandName)
                else:
                    s = k.getLabel(ignorePrompt=True)
                    commandName = s.strip()
                    ok = k.callAltXFunction(k.mb_event)
                    if ok:
                        k.addToCommandHistory(commandName)
            elif char in ('\t', 'Tab'):
                if trace and verbose: g.trace('***Tab')
                k.doTabCompletion(list(c.commandsDict.keys()))
                c.minibufferWantsFocus()
            elif char in ('\b', 'BackSpace'):
                if trace and verbose: g.trace('***BackSpace')
                k.doBackSpace(list(c.commandsDict.keys()))
                c.minibufferWantsFocus()
            elif k.ignore_unbound_non_ascii_keys and len(ch) > 1:
                # g.trace('non-ascii')
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
                # g.trace('new prefix',k.mb_tabListPrefix)
        except Exception:
            g.es_exception()
            self.keyboardQuit()
    #@+node:ekr.20061031131434.112: *5* k.callAltXFunction
    def callAltXFunction(self, event):
        '''Call the function whose name is in the minibuffer.'''
        trace = False and not g.unitTesting
        c, k = self.c, self
        k.mb_tabList = []
        commandName, tail = k.getMinibufferCommandName()
        if trace: g.trace('command:', commandName, 'tail:', tail)
        k.functionTail = tail
        if commandName and commandName.isdigit():
            # The line number Easter Egg.
            def func(event=None):
                c.gotoCommands.find_file_line(n=int(commandName))
        else:
            func = c.commandsDict.get(commandName)
        k.newMinibufferWidget = None
        # g.trace(func and func.__name__,'mb_event',event and event.widget.widgetName)
        if func:
            # These must be done *after* getting the command.
            k.clearState()
            k.resetLabel()
            if commandName != 'repeat-complex-command':
                k.mb_history.insert(0, commandName)
            w = event and event.widget
            if hasattr(w, 'permanent') and not w.permanent:
                # In a headline that is being edited.
                # g.es('Can not execute commands from headlines')
                c.endEditing()
                c.bodyWantsFocusNow()
                # Change the event widget so we don't refer to the to-be-deleted headline widget.
                event.w = event.widget = c.frame.body.wrapper.widget
                c.executeAnyCommand(func, event)
            else:
                c.widgetWantsFocusNow(event and event.widget)
                    # Important, so cut-text works, e.g.
                c.executeAnyCommand(func, event)
            k.endCommand(commandName)
            return True
        else:
            # Show possible completions if the command does not exist.
            if 1: # Useful.
                if trace: g.trace('*** tab completion')
                k.doTabCompletion(list(c.commandsDict.keys()))
            else: # Annoying.
                k.keyboardQuit()
                k.setStatusLabel('Command does not exist: %s' % commandName)
                c.bodyWantsFocus()
            return False
    #@+node:ekr.20061031131434.113: *4* k.endCommand
    def endCommand(self, commandName):
        '''Make sure Leo updates the widget following a command.

        Never changes the minibuffer label: individual commands must do that.
        '''
        k = self; c = k.c
        # The command may have closed the window.
        if g.app.quitting or not c.exists: return
        # Set the best possible undoType: prefer explicit commandName to k.commandName.
        commandName = commandName or k.commandName or ''
        k.commandName = k.commandName or commandName or ''
        if commandName:
            if not k.inState():
                k.commandName = None
            if 0: # Do *not* call this by default.  It interferes with undo.
                c.frame.body.onBodyChanged(undoType='Typing')
            if k.newMinibufferWidget:
                c.widgetWantsFocusNow(k.newMinibufferWidget)
                # g.pr('endCommand', g.app.gui.widget_name(k.newMinibufferWidget),g.callers())
                k.newMinibufferWidget = None
    #@+node:ekr.20061031131434.114: *3* k.Externally visible commands
    #@+node:ekr.20070613133500: *4* k.menuCommandKey
    def menuCommandKey(self, event=None):
        # This method must exist, but it never gets called.
        pass
    #@+node:ekr.20061031131434.119: *4* k.printBindings & helper
    @cmd('print-bindings')
    def printBindings(self, event=None):
        '''Print all the bindings presently in effect.'''
        k = self; c = k.c
        d = k.bindingsDict; tabName = 'Bindings'
        c.frame.log.clearTab(tabName)
        legend = '''\
    legend:
    [ ] leoSettings.leo
    [D] default binding
    [F] loaded .leo File
    [M] myLeoSettings.leo
    [@] @mode, @button, @command

    '''
        if not d: return g.es('no bindings')
        legend = g.adjustTripleString(legend, c.tab_width)
        data = []
        for stroke in sorted(d):
            assert g.isStroke(stroke), stroke
            aList = d.get(stroke, [])
            for bi in aList:
                s1 = '' if bi.pane == 'all' else bi.pane
                s2 = k.prettyPrintKey(stroke)
                s3 = bi.commandName
                s4 = bi.kind or '<no hash>'
                data.append((s1, s2, s3, s4),)
        # Print keys by type:
        result = []
        result.append('\n' + legend)
        for prefix in (
            'Alt+Ctrl+Shift', 'Alt+Ctrl', 'Alt+Shift', 'Alt', # 'Alt+Key': done by Alt.
            'Ctrl+Meta+Shift', 'Ctrl+Meta', 'Ctrl+Shift', 'Ctrl', # Ctrl+Key: done by Ctrl.
            'Meta+Key', 'Meta+Shift', 'Meta',
            'Shift',
            # Careful: longer prefixes must come before shorter prefixes.
        ):
            data2 = []
            for item in data:
                s1, s2, s3, s4 = item
                if s2.startswith(prefix):
                    data2.append(item)
            result.append('***** %s...\n' % prefix)
            self.printBindingsHelper(result, data2, prefix=prefix)
            # Remove all the items in data2 from data.
            # This must be done outside the iterator on data.
            for item in data2:
                data.remove(item)
        # Print all plain bindings.
        result.append('***** Plain Keys...\n')
        self.printBindingsHelper(result, data, prefix=None)
        if not g.unitTesting:
            g.es_print('', ''.join(result), tabName=tabName)
        k.showStateAndMode()
        return result # for unit test.
    #@+node:ekr.20061031131434.120: *5* printBindingsHelper
    def printBindingsHelper(self, result, data, prefix):
        lm = g.app.loadManager
        data.sort(key=lambda x: x[1])
        data2, n = [], 0
        for pane, key, commandName, kind in data:
            key = key.replace('+Key', '')
            # g.trace('%10s %s' % (key, repr(kind)))
            letter = lm.computeBindingLetter(kind)
            pane = '%4s: ' % (pane if pane else 'all')
            left = pane + key # pane and shortcut fields
            n = max(n, len(left))
            data2.append((letter, left, commandName),)
        for z in data2:
            letter, left, commandName = z
            result.append('%s %*s %s\n' % (letter, -n, left, commandName))
        if data:
            result.append('\n')
    #@+node:ekr.20120520174745.9867: *4* k.printButtons
    @cmd('print-buttons')
    def printButtons(self, event=None):
        '''Print all @button and @command commands, their bindings and their source.'''
        k = self; c = k.c
        tabName = '@buttons && @commands'
        c.frame.log.clearTab(tabName)

        def put(s):
            g.es('', s, tabName=tabName)

        data = []
        for aList in [c.config.getButtons(), c.config.getCommands()]:
            for z in aList:
                p, script = z
                c = p.v.context
                tag = 'M' if c.shortFileName().endswith('myLeoSettings.leo') else 'G'
                data.append((p.h, tag),)
        for aList in [g.app.config.atLocalButtonsList, g.app.config.atLocalCommandsList]:
            for p in aList:
                data.append((p.h, 'L'),)
        result = ['%s %s' % (z[1], z[0]) for z in sorted(data)]
        result.extend([
            '',
            'legend:',
            'G leoSettings.leo',
            'L local .leo File',
            'M myLeoSettings.leo',
        ])
        put('\n'.join(result))
    #@+node:ekr.20061031131434.121: *4* k.printCommands
    @cmd('print-commands')
    def printCommands(self, event=None):
        '''Print all the known commands and their bindings, if any.'''
        k = self; c = k.c; tabName = 'Commands'
        c.frame.log.clearTab(tabName)
        inverseBindingDict = k.computeInverseBindingDict()
        data, n = [], 0
        for commandName in sorted(c.commandsDict):
            dataList = inverseBindingDict.get(commandName, [('', ''),])
            for z in dataList:
                pane, key = z
                pane = '%s ' % (pane) if pane != 'all:' else ''
                key = k.prettyPrintKey(key).replace('+Key', '')
                s1 = pane + key
                s2 = commandName
                n = max(n, len(s1))
                data.append((s1, s2),)
        # This isn't perfect in variable-width fonts.
        lines = ['%*s %s\n' % (-n, z1, z2) for z1, z2 in data]
        g.es_print('', ''.join(lines), tabName=tabName)
    #@+node:ekr.20061031131434.122: *4* k.repeatComplexCommand & helper
    @cmd('repeat-complex-command')
    def repeatComplexCommand(self, event):
        '''Repeat the previously executed minibuffer command.'''
        k = self
        if k.mb_history:
            k.setState('last-full-command', 1, handler=k.repeatComplexCommandHelper)
            k.setLabelBlue("Redo: %s" % str(k.mb_history[0]))
        else:
            g.warning('no previous command')
    #@+node:ekr.20131017100903.16689: *5* repeatComplexCommandHelper
    def repeatComplexCommandHelper(self, event):
        k = self; c = k.c
        char = event.char if event else ''
        if char in ('\n', 'Return') and k.mb_history:
            last = k.mb_history[0]
            k.resetLabel()
            k.clearState() # Bug fix.
            c.commandsDict[last](event)
        else:
            # g.trace('oops')
            return k.keyboardQuit()
    #@+node:ekr.20061031131434.123: *4* k.set-xxx-State
    @cmd('set-command-state')
    def setCommandState(self, event):
        '''Enter the 'command' editing state.'''
        # g.trace(g.callers())
        k = self
        k.setInputState('command', set_border=True)
        # This command is also valid in headlines.
        # k.c.bodyWantsFocus()
        k.showStateAndMode()

    @cmd('set-insert-state')
    def setInsertState(self, event):
        '''Enter the 'insert' editing state.'''
        # g.trace(g.callers())
        k = self
        k.setInputState('insert', set_border=True)
        # This command is also valid in headlines.
        # k.c.bodyWantsFocus()
        k.showStateAndMode()

    @cmd('set-overwrite-state')
    def setOverwriteState(self, event):
        '''Enter the 'overwrite' editing state.'''
        # g.trace(g.callers())
        k = self
        k.setInputState('overwrite', set_border=True)
        # This command is also valid in headlines.
        # k.c.bodyWantsFocus()
        k.showStateAndMode()
    #@+node:ekr.20061031131434.124: *4* k.toggle-input-state
    @cmd('toggle-input-state')
    def toggleInputState(self, event=None):
        '''The toggle-input-state command.'''
        k = self; c = k.c
        default = c.config.getString('top_level_unbound_key_action') or 'insert'
        state = k.unboundKeyAction
        if default == 'insert':
            state = 'command' if state == 'insert' else 'insert'
        elif default == 'overwrite':
            state = 'command' if state == 'overwrite' else 'overwrite'
        else:
            state = 'insert' if state == 'command' else 'command' # prefer insert to overwrite.
        k.setInputState(state)
        k.showStateAndMode()
    #@+node:ekr.20061031131434.125: *3* k.Externally visible helpers
    #@+node:ekr.20140816165728.18968: *4* Wrappers for GetArg methods
    # New in Leo 5.4
    def getNextArg(self, handler):
        '''
        Get the next arg.  For example, after a Tab in the find commands.
        See the docstring for k.get1Arg for examples of its use.
        '''
        # Replace the current handler.
        self.getArgInstance.after_get_arg_state = ('getarg', 1, handler)
        self.c.minibufferWantsFocusNow()

    # New in Leo 5.4
    def get1Arg(self, event, handler,
        # returnKind=None, returnState=None,
        prefix=None, tabList=None, completion=True, oneCharacter=False,
        stroke=None, useMinibuffer=True
    ):
        #@+<< docstring for k.get1arg >>
        #@+node:ekr.20161020031633.1: *5* << docstring for k.get1arg >>
        '''
        k.get1Arg: Handle the next character the user types when accumulating
        a user argument from the minibuffer. Ctrl-G will abort this processing
        at any time.

        Commands should use k.get1Arg to get the first minibuffer argument and
        k.getNextArg to get all other arguments.

        Before going into the many details, let's look at some examples. This
        code will work in any class having a 'c' ivar bound to a commander.

        Example 1: get one argument from the user:

            @g.command('my-command')
            def myCommand(self, event):
                k = self.c.k
                k.setLabelBlue('prompt: ')
                k.get1Arg(event, handler=self.myCommand1)

            def myCommand1(self, event):
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
            def myCommand(self, event):
                k = self.c.k
                k.setLabelBlue('first prompt: ')
                k.get1Arg(event, handler=self.myCommand1)

            def myCommand1(self, event):
                k = self.c.k
                self.arg1 = k.arg
                k.extendLabel(' second prompt: ', select=False, protect=True)
                k.getNextArg(handler=self.myCommand2)

            def myCommand2(self, event):
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

        '''
        #@-<< docstring for k.get1arg >>
        returnKind, returnState = None, None
        assert handler, g.callers()
        self.getArgInstance.get_arg(event, returnKind, returnState, handler,
            tabList, completion, oneCharacter, stroke, useMinibuffer)

    def getArg(self, event,
        returnKind=None, returnState=None, handler=None,
        prefix=None, tabList=None, completion=True, oneCharacter=False,
        stroke=None, useMinibuffer=True
    ):
        '''Convenience method mapping k.getArg to ga.get_arg.'''
        self.getArgInstance.get_arg(event, returnKind, returnState, handler,
            tabList, completion, oneCharacter, stroke, useMinibuffer)

    def doBackSpace(self, tabList, completion=True):
        '''Convenience method mapping k.doBackSpace to ga.do_back_space.'''
        self.getArgInstance.do_back_space(tabList, completion)

    def doTabCompletion(self, tabList):
        '''Convenience method mapping k.doTabCompletion to ga.do_tab.'''
        self.getArgInstance.do_tab(tabList)

    def getMinibufferCommandName(self):
        '''
        Convenience method mapping k.getMinibufferCommandName to
        ga.get_minibuffer_command_name.
        '''
        return self.getArgInstance.get_minibuffer_command_name()
    #@+node:ekr.20061031131434.130: *4* k.keyboardQuit
    @cmd('keyboard-quit')
    def keyboardQuit(self, event=None, setFocus=True, mouseClick=False):
        '''
        This method clears the state and the minibuffer label.

        k.endCommand handles all other end-of-command chores.
        '''
        trace = False and not g.unitTesting
        k = self; c = k.c
        if trace: g.trace(g.callers())
        if g.app.quitting:
            return
        # 2011/05/30: We may be called from Qt event handlers.
        # Make sure to end editing!
        c.endEditing()
        # Completely clear the mode.
        if setFocus:
            c.frame.log.deleteTab('Mode')
            c.frame.log.hideTab('Completion')
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
    #@+node:ekr.20061031131434.126: *4* k.manufactureKeyPressForCommandName
    def manufactureKeyPressForCommandName(self, w, commandName):
        '''
        Implement a command by passing a keypress to the gui.
        
        **Only unit tests use this method.**
        '''
        trace = False and not g.unitTesting
        c, k = self.c, self
        stroke = k.getStrokeForCommandName(commandName)
        assert g.isStroke(stroke), stroke.__class__.__name__
        shortcut = stroke.s
        assert g.isString(shortcut)
        if trace and shortcut: g.trace(
            'shortcut', repr(shortcut), 'commandName', commandName)
        if shortcut and w:
            g.app.gui.set_focus(c, w)
            g.app.gui.event_generate(c, None, shortcut, w)
        else:
            message = 'no shortcut for %s' % (commandName)
            if trace: g.trace(message)
            if g.app.unitTesting:
                raise AttributeError(message)
            else:
                g.error(message)
    #@+node:ekr.20071212104050: *4* k.overrideCommand
    def overrideCommand(self, commandName, func):
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
    def registerCommand(self, commandName, func,
        allowBinding=False,
        pane='all',
        shortcut=None, # Must be None unless allowBindings is True.
        **kwargs
    ):
        '''
        Make the function available as a minibuffer command.
        
        You can wrap any method in a callback function, so the
        restriction to functions is not significant.
        
        Ignore the 'shortcut' arg unless 'allowBinding' is True.
        
        Only k.bindOpenWith and the mod_scripting.py plugin should set
        allowBinding.
        '''
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
                g.es_print('The "%s" keyword arg to k.registerCommand is deprecated' % arg)
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
    def registerCommandShortcut(self, commandName, func, pane, shortcut):
        '''
        Register a shortcut for the a command.
        
        **Important**: Bindings created here from plugins can not be overridden.
        This includes @command and @button bindings created by mod_scripting.py.
        '''
        trace = False and not g.unitTesting and not g.app.silentMode
        c, k = self.c, self
        is_local = c.shortFileName() not in ('myLeoSettings.leo', 'leoSettings.leo')
        assert not g.isStroke(shortcut)
        if shortcut:
            stroke = g.KeyStroke(binding=shortcut) if shortcut else None
        elif commandName.lower() == 'shortcut': # Causes problems.
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
                    pane = bi.pane # 2015/05/11.
                    break
        if stroke:
            k.bindKey(pane, stroke, func, commandName, tag='register-command')
                # Must be a stroke.
            k.makeMasterGuiBinding(stroke, trace=trace) # Must be a stroke.
        if trace:
            # pretty_stroke = k.prettyPrintKey(stroke) if stroke else 'None'
            g.trace('@command %-45s' % (commandName), g.callers(2))
        # Fixup any previous abbreviation to press-x-button commands.
        if commandName.startswith('press-') and commandName.endswith('-button'):
            d = c.config.getAbbrevDict()
                # Keys are full command names, values are abbreviations.
            if commandName in list(d.values()):
                for key in d:
                    if d.get(key) == commandName:
                        c.commandsDict[key] = c.commandsDict.get(commandName)
                        break
    #@+node:ekr.20061031131434.127: *4* k.simulateCommand & k.commandExists
    def simulateCommand(self, commandName, event=None):
        '''Execute a Leo command by name.'''
        trace = False and not g.unitTesting
        c, k = self.c, self
        func = self.commandExists(commandName)
        if func:
            # Support @g.commander_command
            c_func = getattr(c, func.__name__, None)
            if c_func:
                if trace:
                    g.trace('@g.commander_command(%s): %s' % (commandName,func.__name__))
                return c_func(event=event)
            if event:
                pass
            elif commandName.startswith('specialCallback'):
                event = None # A legacy function.
            else: # Create a dummy event as a signal.
                event = g.app.gui.create_key_event(c)
            if trace: g.trace(event)
            k.masterCommand(event=event, func=func)
            if c.exists:
                return k.funcReturn
            else:
                return None
        elif g.app.unitTesting:
            raise AttributeError
        else:
            g.error('simulateCommand: no command for %s' % (commandName))
            return None
    #@+node:ekr.20170324143353.1: *5* k.commandExists
    def commandExists(self, commandName):
        '''Return the command handler for the given command name, or None.'''
        c, k = self.c, self
        commandName = commandName.strip()
        if commandName:
            aList = commandName.split(None)
            if len(aList) == 1:
                k.givenArgs = []
            else:
                commandName = aList[0]
                k.givenArgs = aList[1:]
            # g.trace(commandName,k.givenArgs)
            func = c.commandsDict.get(commandName)
            return func
        else:
            return None
    #@+node:ekr.20140813052702.18203: *4* k.getFileName
    def getFileName(self, event, callback=None,
        filterExt=None, prompt='Enter File Name: ', tabName='Dired'
    ):
        '''Get a file name from the minibuffer.'''
        k = self
        k.fnc.get_file_name(event, callback, filterExt, prompt, tabName)
    #@+node:ekr.20061031131434.145: *3* k.Master event handlers
    #@+node:ekr.20061031131434.146: *4* k.masterKeyHandler & helpers
    def masterKeyHandler(self, event):
        '''The master key handler for almost all key bindings.'''
        k = self
        # Setup...
        if 'keys' in g.app.debug:
            g.trace(repr(event.char), event.stroke)
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
        if k.doUnboundPlainKey(event):
            return
        k.doBinding(event)
        
    #@+node:ekr.20180418040158.1: *5* k.checkKeyEvent
    def checkKeyEvent(self, event):
        '''Perform sanity checks on the incoming event.'''
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
            assert event.stroke.s not in g.app.gui.ignoreChars, repr(event.stroke.s)
                # A continuous unit test, better than "@test k.isPlainKey".

    #@+node:ekr.20180418033838.1: *5* k.doBinding
    def doBinding(self, event):
        '''
        The last phase of k.masertKeyHandler.
        Execute the command associated with stroke's binding.
        Call k.handleUnboundKeys for killed or non-existent bindings.
        '''
        c, k = self.c, self
        char, stroke, w = event.char, event.stroke, event.widget
        #
        # Use getPaneBindings for *all* keys.
        #
        bi = k.getPaneBinding(stroke, w)
        #
        # Call k.handleUnboudKeys for all killed bindings.
        #
        if bi and bi.commandName in k.killedBindings:
            #327: ignore killed bindings.
            k.handleUnboundKeys(event)
            return
        #
        # Call k.masterCommandHandler if the binding exists.
        #
        if bi:
            k.masterCommand(
                event=event,
                commandName=bi.commandName,
                func=bi.func,
                stroke=bi.stroke)
            return
        #
        # Handle unbound keys in the tree (not headlines).
        # 
        if c.widget_name(w).startswith('canvas'):
            k.searchTree(char)
            return
        #
        # No binding exists. Call k.handleUnboundKey.
        #
        k.handleUnboundKeys(event)
    #@+node:ekr.20180418023827.1: *5* k.doDemo
    def doDemo(self, event):
        '''
        Support the demo.py plugin.
        Return True if k.masterKeyHandler should return.
        '''
        k = self
        stroke = event.stroke
        demo = getattr(g.app, 'demo', None)
        if not demo:
            return False
        #
        # Shortcut everything so that demo-next or demo-prev won't alter of our ivars.
        if k.demoNextKey and stroke == k.demoNextKey:
            if demo.trace: g.trace('demo-next', stroke)
            demo.next_command()
            return True
        if k.demoPrevKey and stroke == k.demoPrevKey:
            if demo.trace: g.trace('demo-prev', stroke)
            demo.prev_command()
            return True
        return False
    #@+node:ekr.20061031131434.108: *5* k.callStateFunction
    def callStateFunction(self, event):
        '''Call the state handler associated with this event.'''
        k = self
        ch = event.char
        #
        # Defensive programming
        #
        if not k.state.kind:
            return None
        if not k.state.handler:
            g.error('callStateFunction: no state function for', k.state.kind)
            return None
        #
        # Handle auto-completion before checking for unbound keys.
        #
        if k.state.kind == 'auto-complete':
            # k.auto_completer_state_handler returns 'do-standard-keys' for control keys.
            val = k.state.handler(event)
            return val
        #
        # Ignore unbound non-ascii keys.
        #
        if (
            k.ignore_unbound_non_ascii_keys and
            len(ch) == 1 and
            ch and ch not in ('\b', '\n', '\r', '\t') and
            (ord(ch) < 32 or ord(ch) > 128)
        ):
            return None
        #
        # Call the state handler.
        #
        val = k.state.handler(event)
        if val != 'continue':
            k.endCommand(k.commandName)
        return val
    #@+node:ekr.20180418025702.1: *5* k.doUnboundPlainKey & helper
    def doUnboundPlainKey(self, event):
        '''
        Handle unbound plain keys.
        Return True if k.masterKeyHandler should return.
        '''
        c, k = self.c, self
        stroke, w = event.stroke, event.widget
        #
        # Ignore non-plain keys.
        if not k.isPlainKey(stroke):
            return False
        #
        # Ignore any keys in the background tree widget.
        if c.widget_name(w).startswith('canvas'):
            return False
        #
        # Ignore the char if it is bound to the auto-complete command.
        if self.isAutoCompleteChar(stroke):
            return False
        #
        # Handle the unbound key.
        k.handleUnboundKeys(event)
        return True
    #@+node:ekr.20110209083917.16004: *6* k.isAutoCompleteChar
    def isAutoCompleteChar(self, stroke):
        '''
        Return True if stroke is bound to the auto-complete in
        the insert or overwrite state.
        '''
        k = self; state = k.unboundKeyAction
        assert g.isStrokeOrNone(stroke)
        if stroke and state in ('insert', 'overwrite'):
            for key in (state, 'body', 'log', 'text', 'all'):
                d = k.masterBindingsDict.get(key, {})
                if d:
                    bi = d.get(stroke)
                    if bi:
                        assert bi.stroke == stroke, 'bi: %s stroke: %s' % (bi, stroke)
                        if bi.commandName == 'auto-complete':
                            return True
        return False
    #@+node:ekr.20180418025241.1: *5* k.doVim
    def doVim(self, event):
        '''
        Handle vim mode.
        Return True if k.masterKeyHandler should return.
        '''
        trace = False and not g.unitTesting
        c = self.c
        if c.vim_mode and c.vimCommands:
            ok = c.vimCommands.do_key(event)
            if trace: g.trace('vc.do_key returns', ok)
            return ok
        return False
    #@+node:ekr.20091230094319.6244: *5* k.doMode
    def doMode(self, event):
        '''
        Handle mode bindings.
        Return True if k.masterKeyHandler should return.
        '''
        k = self
        state = k.state.kind
        stroke = event.stroke
        if not k.inState():
            return False
        #
        # First, honor minibuffer bindings for all except user modes.
        if state == 'input-shortcut':
            k.handleInputShortcut(event, stroke)
            return True
        if state in ('getArg', 'getFileName', 'full-command', 'auto-complete', 'vim-mode'):
            if k.handleMiniBindings(event, state, stroke):
                return True
        #
        # Second, honor general modes.
        #
        if state == 'getArg':
            k.getArg(event, stroke=stroke)
            return True
        if state in ('getFileName', 'get-file-name'):
            k.getFileName(event)
            return True
        if state in ('full-command', 'auto-complete'):
            val = k.callStateFunction(event)
                # Do the default state action.
                # Calls end-command.
            return val != 'do-standard-keys'
        #
        # Third, pass keys to user modes.
        #
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
                return True
            else:
                # Unbound keys end mode.
                k.endMode()
                return False
        #
        # Fourth, call the state handler.
        #
        handler = k.getStateHandler()
        if handler:
            handler(event)
        return True
    #@+node:ekr.20091230094319.6240: *5* k.getPaneBinding & helper
    def getPaneBinding(self, stroke, w):
       
        k = self
        if not g.assert_is(stroke, g.KeyStroke):
            return None
        for key, name in (
            # Order here is similar to bindtags order.
            ('command', None),
            ('insert', None),
            ('overwrite', None),
            ('button', None),
            ('body', 'body'),
            ('text', 'head'), # Important: text bindings in head before tree bindings.
            ('tree', 'head'),
            ('tree', 'canvas'),
            ('log', 'log'),
            ('text', 'log'),
            ('text', None),
            ('all', None),
        ):
            val = k.getBindingHelper(key, name, stroke, w)
            if val:
                return val
        return None
    #@+node:ekr.20180418105228.1: *6* getPaneBindingHelper
    def getBindingHelper(self, key, name, stroke, w):
        '''Find a binding for the widget with the given name.'''
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
    #@+node:ekr.20061031131434.110: *5* k.handleDefaultChar
    def handleDefaultChar(self, event, stroke):
        '''
        Handle an unbound key, based on the event's widget.
        Do not assume that stroke exists.
        '''
        c, k, w = self.c, self, event.widget
        name = c.widget_name(w)
        #
        # Ignore unbound alt-ctrl key
        if stroke and stroke.isAltCtrl() and k.ignore_unbound_non_ascii_keys:
            g.app.unitTestDict['handleUnboundChar-ignore-alt-or-ctrl'] = True
            return
        #
        # Handle events in the body pane.
        if name.startswith('body'):
            action = k.unboundKeyAction
            if action in ('insert', 'overwrite'):
                c.editCommands.selfInsertCommand(event, action=action)
            else:
                pass # Ignore the key
            return
        #
        # Handle events in headlines.
        if name.startswith('head'):
            c.frame.tree.onHeadlineKey(event)
            return
        #
        # Handle events in the background tree.
        if name.startswith('canvas'):
            if not stroke: # Not exactly right, but it seems to be good enough.
                c.onCanvasKey(event)
            return
        #
        # Handle events in the log pane.
        if name.startswith('log'):
            # Make sure we can insert into w.
            log_w = event.widget
            if not hasattr(log_w, 'supportsHighLevelInterface'):
                return
            # Send the event to the text widget, not the LeoLog instance.
            if not stroke:
                stroke = event.stroke
            if stroke:
                i = log_w.getInsertPoint()
                s = stroke.toGuiChar()
                log_w.insert(i, s)
            return
        #
        # Ignore all other events.
    #@+node:vitalije.20170708161511.1: *5* k.handleInputShortcut
    def handleInputShortcut(self, event, stroke):
        c, k, p = self.c, self, self.c.p
        k.clearState()
        if p.h.startswith(('@shortcuts', '@mode')):
            # line of text in body
            w = c.frame.body
            before, sel, after = w.getInsertLines()
            m = k._cmd_handle_input_pattern.search(sel)
            assert m # edit-shortcut was invoked on a malformed body line
            sel = g.u('%s %s\n')%(m.group(0), stroke.s)
            udata = c.undoer.beforeChangeNodeContents(p)
            w.setSelectionAreas(before, sel, after)
            c.undoer.afterChangeNodeContents(p, 'change shortcut', udata)
            w.onBodyChanged('change shortcut')
            cmdname = m.group(0).rstrip('= ')
            k.editShortcut_do_bind_helper(stroke, cmdname)
            return
        elif p.h.startswith(('@command', '@button')):
            udata = c.undoer.beforeChangeNodeContents(p)
            cmd = p.h.split(g.u('@key'),1)[0]
            p.h = g.u('%s @key=%s')%(cmd, stroke.s)
            c.undoer.afterChangeNodeContents(p, 'change shortcut', udata)
            try:
                cmdname = cmd.split(' ', 1)[1].strip()
                k.editShortcut_do_bind_helper(stroke, cmdname)
            except IndexError:
                pass
            return
        else:
            # this should never happen
            g.error('not in settings node shortcut')
    #@+node:vitalije.20170709151653.1: *6* k.isInShortcutBodyLine
    _cmd_handle_input_pattern = re.compile(g.u('[A-Za-z0-9_\\-]+\\s*='))

    def isInShortcutBodyLine(self):
        k = self; c = k.c; p = c.p
        if p.h.startswith(('@shortcuts', '@mode')):
            # line of text in body
            w = c.frame.body
            before, sel, after = w.getInsertLines()
            m = k._cmd_handle_input_pattern.search(sel)
            return bool(m)
        return p.h.startswith(('@command', '@button'))
    #@+node:vitalije.20170709151658.1: *6* k.isEditShortcutSensible
    def isEditShortcutSensible(self):
        k = self; c = k.c; p = c.p
        return p.h.startswith(('@command', '@button')) or k.isInShortcutBodyLine()
    #@+node:vitalije.20170709202924.1: *6* k.editShortcut_do_bind_helper
    def editShortcut_do_bind_helper(self, stroke, cmdname):
        k = self; c = k.c
        cmdfunc = c.commandsDict.get(cmdname)
        if cmdfunc:
            k.bindKey('all', stroke, cmdfunc, cmdname)
            g.es('bound', stroke, 'to command', cmdname)
    #@+node:ekr.20061031131434.152: *5* k.handleMiniBindings
    def handleMiniBindings(self, event, state, stroke):
        '''Find and execute commands bound to the event.'''
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
                return False # Let getArg handle it.
            if result == 'found':
                return True
        #
        # No binding exists.
        return False
    #@+node:ekr.20180418114300.1: *6* k.handleMinibufferHelper
    def handleMinibufferHelper(self, event, pane, state, stroke):
        '''
        Execute a pane binding in the minibuffer.
        
        Return 'continue', 'ignore', 'found'
        '''
        c, k = self.c, self
        d = k.masterBindingsDict.get(pane)
        if not d:
            return 'continue'
        bi = d.get(stroke)
        if not bi:
            return 'continue'
        assert bi.stroke == stroke, 'bi: %s stroke: %s' % (bi, stroke)
        #
        # Special case the replace-string command in the minibuffer.
        #
        if bi.commandName == 'replace-string' and state == 'getArg':
            return 'ignore'
        #
        # Execute this command.
        #
        if bi.commandName not in k.singleLineCommandList:
            k.keyboardQuit()
        else:
            c.minibufferWantsFocus() # New in Leo 4.5.
        # Pass this on for macro recording.
        k.masterCommand(
            commandName=bi.commandName,
            event=event,
            func=bi.func,
            stroke=stroke)
        # Careful: the command could exit.
        if c.exists and not k.silentMode:
            c.minibufferWantsFocus()
        return 'found'
    #@+node:ekr.20180418031118.1: *5* k.isSpecialKey
    def isSpecialKey(self, event):
        '''Return True if char is a special key.'''
        if not event:
            # An empty event is not an error.
            return False
        return event.char in g.app.gui.ignoreChars
    #@+node:ekr.20180418024449.1: *5* k.keyboardQuit
    def doKeyboardQuit(self, event):
        '''
        Handle keyboard-quit logic.
        return True if k.masterKeyHandler should return.
        '''
        c, k = self.c, self
        stroke = event.stroke
        if k.abortAllModesKey and stroke == k.abortAllModesKey:
            if getattr(c, 'screenCastController', None):
                c.screenCastController.quit()
            k.masterCommand(
                commandName='keyboard-quit',
                event=event,
                func=k.keyboardQuit,
                stroke=stroke)
            return True
        return False
    #@+node:ekr.20080510095819.1: *5* k.handleUnboundKeys
    def handleUnboundKeys(self, event):
       
        c, k = self.c, self
        char, stroke = event.char, event.stroke
        if not g.assert_is(stroke, g.KeyStroke):
            return
        #
        # Ignore all unbound characters in command mode.
        if k.unboundKeyAction == 'command':
            w = g.app.gui.get_focus(c)
            if w and g.app.gui.widget_name(w).lower().startswith('canvas'):
                c.onCanvasKey(event)
            return
        #
        # Ignore unbound F-keys.
        if stroke.isFKey():
            return
        #
        #  Handle a normal character in insert/overwrite.
        # <Return> is *not* a normal character.
        if stroke and k.isPlainKey(stroke) and k.unboundKeyAction in ('insert', 'overwrite'):
            k.masterCommand(event=event, stroke=stroke)
            return
        #
        # Always ignore unbound Alt/Ctrl keys.
        if stroke.isAltCtrl() and not self.enable_alt_ctrl_bindings:
            return
        #
        # Ignore unbound non-ascii character.
        if (
            k.ignore_unbound_non_ascii_keys and
            (len(char) > 1 or char not in string.printable)
                ### k.isPlainKey (same as stroke.isPlainKey) should be better.
        ):
            return
        #
        # Never insert escape or insert characters.
        if (
            stroke and stroke.find('Escape') != -1 or
            stroke and stroke.find('Insert') != -1
        ):
            return
        #
        # Let k.masterCommand handle the unbound character.
        k.masterCommand(event=event, stroke=stroke)
    #@+node:ekr.20061031131434.105: *5* k.masterCommand
    def masterCommand(self, commandName=None, event=None, func=None, stroke=None):
        '''
        This is the central dispatching method.
        All commands and keystrokes pass through here.
        This returns None, but may set k.funcReturn.
        '''
        c, k = self.c, self
        if event: c.check_event(event)
        c.setLog()
        k.stroke = stroke # Set this global for general use.
        ch = event.char if event else ''
        #
        # Ignore all special keys.
        if k.isSpecialKey(event):
            return
        #
        # Compute func if not given.
        # It is *not* an error for func to be None.
        if commandName and not func:
            func = c.commandsDict.get(commandName.replace('&', ''))
            if not func:
                return
        commandName = commandName or func and func.__name__ or '<no function>'
        k.funcReturn = None # For unit testing.
        #
        # Remember the key.
        k.setLossage(ch, stroke)
        #
        # Handle keyboard-quit.
        if k.abortAllModesKey and stroke == k.abortAllModesKey:
            k.keyboardQuit()
            k.endCommand(commandName)
            return
        #
        # Ignore abbreviations.
        if k.abbrevOn and c.abbrevCommands.expandAbbrev(event, stroke):
            return
        #
        # Handle the func argument, if given.
        if func:
            if commandName.startswith('specialCallback'):
                # The callback function will call c.doCommand.
                val = func(event)
                # Set k.funcReturn for k.simulateCommand..
                k.funcReturn = k.funcReturn or val
            else:
                # Call c.doCommand directly.
                c.doCommand(func, commandName, event=event)
            if c.exists:
                k.endCommand(commandName)
                c.frame.updateStatusLine()
            return
        #
        # Ignore unbound keys in a state.
        if k.inState():
            return
        #
        # Finally, call k.handleDefaultChar.
        k.handleDefaultChar(event, stroke)
        if c.exists:
            c.frame.updateStatusLine()
        
    #@+node:ekr.20180418034305.1: *5* k.setEventWidget
    def setEventWidget(self, event):
        '''
        A hack: redirect the event to the text part of the log.
        '''
        c = self.c
        w = event.widget
        w_name = c.widget_name(w)
        if w_name.startswith('log'):
            event.widget = c.frame.log.logCtrl
    #@+node:ekr.20180418031417.1: *5* k.traceVars
    def traceVars(self, event):
        
        trace = False and not g.unitTesting
        traceGC = False
        verbose = False
        k = self
        if not trace:
            return
        if traceGC:
            g.printNewObjects('masterKey 1')
        if verbose:
            char = event.char
            state = k.state.kind
            stroke = event.stroke
            g.trace('stroke: %r, char: %r, state: %s, state2: %s' % (
                stroke, char, state, k.unboundKeyAction))
    #@+node:ekr.20160409035115.1: *5* k.searchTree
    def searchTree(self, char):
        '''Search all visible nodes for a headline starting with stroke.'''
        if not char: return
        c = self.c
        if not c.config.getBool('plain-key-outline-search'):
            return

        def match(p):
            '''Return True if p contains char.'''
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
                else:
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
    def extendLabel(self, s, select=False, protect=False):
        trace = False and not g.unitTesting
        k = self; c = k.c; w = self.w
        if not (w and s): return
        if trace: g.trace(s)
        c.widgetWantsFocusNow(w)
        w.insert('end', s)
        if select:
            i, j = k.getEditableTextRange()
            w.setSelectionRange(i, j, insert=j)
        if protect:
            k.protectLabel()
    #@+node:ekr.20061031170011.13: *4* k.getEditableTextRange
    def getEditableTextRange(self):
        k = self; w = self.w
        s = w.getAllText()
        i = len(k.mb_prefix)
        j = len(s)
        return i, j
    #@+node:ekr.20061031170011.5: *4* k.getLabel
    def getLabel(self, ignorePrompt=False):
        k = self; w = self.w
        if not w: return ''
        s = w.getAllText()
        if ignorePrompt:
            return s[len(k.mb_prefix):]
        else:
            return s or ''
    #@+node:ekr.20080408060320.791: *4* k.killLine
    def killLine(self, protect=True):
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
    def protectLabel(self):
        k = self; w = self.w
        if not w: return
        k.mb_prefix = w.getAllText()
    #@+node:ekr.20061031170011.7: *4* k.resetLabel
    def resetLabel(self):
        '''Reset the minibuffer label.'''
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
                k.setLabelBlue(label='%s State' % (state.capitalize()))
    #@+node:ekr.20080408060320.790: *4* k.selectAll
    def selectAll(self):
        '''Select all the user-editable text of the minibuffer.'''
        w = self.w
        i, j = self.getEditableTextRange()
        w.setSelectionRange(i, j, insert=j)
    #@+node:ekr.20061031170011.8: *4* k.setLabel
    def setLabel(self, s, protect=False):
        '''Set the label of the minibuffer.'''
        trace = False and not g.app.unitTesting
        c, k, w = self.c, self, self.w
        if w:
            if trace: g.trace(s)
            # Support for the curses gui.
            if hasattr(g.app.gui, 'set_minibuffer_label'):
                g.app.gui.set_minibuffer_label(c, s)
            w.setAllText(s)
            n = len(s)
            w.setSelectionRange(n, n, insert=n)
            if protect:
                k.mb_prefix = s
        elif trace:
            g.trace('*** no w ***')
    #@+node:ekr.20061031170011.10: *4* k.setLabelBlue
    def setLabelBlue(self, label, protect=True):
        '''Set the minibuffer label.'''
        trace = False and not g.unitTesting
        k, w = self, self.w
        if trace: g.trace('label:', label)
        if hasattr(g.app.gui, 'set_minibuffer_label'):
            g.app.gui.set_minibuffer_label(self.c, label)
        elif w:
            w.setStyleClass('') # normal state, not warning or error
            if label is not None:
                k.setLabel(label, protect=protect)
        elif trace:
            g.trace('*** no w ***')
    #@+node:ekr.20061031170011.11: *4* k.setLabelGrey
    def setLabelGrey(self, label=None):
        k = self; w = self.w
        if not w: return
        w.setStyleClass('minibuffer_warning')
        if label is not None:
            k.setLabel(label)

    setLabelGray = setLabelGrey
    #@+node:ekr.20080510153327.2: *4* k.setLabelRed
    def setLabelRed(self, label=None, protect=False):
        k = self; w = self.w
        if not w: return
        w.setStyleClass('minibuffer_error')
        if label is not None:
            k.setLabel(label, protect)
    #@+node:ekr.20140822051549.18298: *4* k.setStatusLabel
    def setStatusLabel(self, s):
        '''
        Set the label to s.

        Use k.setStatusLabel, not k.setLael, to report the status of a Leo
        command. This allows the option to use g.es instead of the minibuffer
        to report status.
        '''
        k = self
        k.setLabel(s, protect=False)
    #@+node:ekr.20061031170011.12: *4* k.updateLabel
    def updateLabel(self, event):
        '''Mimic what would happen with the keyboard and a Text editor
        instead of plain accumulation.'''
        trace = False and not g.app.unitTesting
        k = self; c = k.c; w = self.w
        ch = event.char if event else ''
        if trace: g.trace('ch', ch, 'k.stroke', k.stroke)
        if ch and ch not in ('\n', '\r'):
            c.widgetWantsFocusNow(w)
            i, j = w.getSelectionRange()
            ins = w.getInsertPoint()
            # g.trace(i,j,ins)
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
    #@+node:ekr.20120208064440.10190: *3* k.Modes (no change)
    #@+node:ekr.20061031131434.100: *4* k.addModeCommands (enterModeCallback)
    def addModeCommands(self):
        '''Add commands created by @mode settings to c.commandsDict.'''
        trace = False and not g.unitTesting
        if trace: g.trace('(k)')
        k = self; c = k.c
        d = g.app.config.modeCommandsDict # Keys are command names: enter-x-mode.
        # Create the callback functions and update c.commandsDict.
        for key in d.keys():
            # pylint: disable=cell-var-from-loop

            def enterModeCallback(event=None, name=key):
                k.enterNamedMode(event, name)

            c.commandsDict[key] = f = enterModeCallback
            if trace: g.trace(f.__name__, key,
                'len(c.commandsDict.keys())', len(list(c.commandsDict.keys())))
    #@+node:ekr.20061031131434.157: *4* k.badMode
    def badMode(self, modeName):
        k = self
        k.clearState()
        if modeName.endswith('-mode'): modeName = modeName[: -5]
        k.setLabelGrey('@mode %s is not defined (or is empty)' % modeName)
    #@+node:ekr.20061031131434.158: *4* k.createModeBindings
    def createModeBindings(self, modeName, d, w):
        '''Create mode bindings for the named mode using dictionary d for w, a text widget.'''
        trace = False and not g.unitTesting
        k = self; c = k.c
        assert d.name().endswith('-mode')
        for commandName in d.keys():
            if commandName in ('*entry-commands*', '*command-prompt*'):
                # These are special-purpose dictionary entries.
                continue
            func = c.commandsDict.get(commandName)
            if not func:
                g.es_print('no such command:', commandName, 'Referenced from', modeName)
                continue
            aList = d.get(commandName, [])
            for bi in aList:
                stroke = bi.stroke
                # Important: bi.val is canonicalized.
                if stroke and stroke not in ('None', 'none', None):
                    if trace:
                        g.trace(
                            g.app.gui.widget_name(w), modeName,
                            '%10s' % (stroke),
                            '%20s' % (commandName),
                            bi.nextMode)
                    assert g.isStroke(stroke)
                    k.makeMasterGuiBinding(stroke)
                    # Create the entry for the mode in k.masterBindingsDict.
                    # Important: this is similar, but not the same as k.bindKeyToDict.
                    # Thus, we should **not** call k.bindKey here!
                    d2 = k.masterBindingsDict.get(modeName, {})
                    d2[stroke] = g.BindingInfo(
                        kind='mode<%s>' % (modeName), # 2012/01/23
                        commandName=commandName,
                        func=func,
                        nextMode=bi.nextMode,
                        stroke=stroke)
                    k.masterBindingsDict[modeName] = d2
    #@+node:ekr.20120208064440.10179: *4* k.endMode
    def endMode(self):
        k = self; c = k.c
        w = g.app.gui.get_focus(c)
        if w:
            c.frame.log.deleteTab('Mode') # Changes focus to the body pane
        k.endCommand(k.stroke)
        k.inputModeName = None
        k.clearState()
        k.resetLabel()
        k.showStateAndMode() # Restores focus.
        if w:
            c.widgetWantsFocusNow(w)
    #@+node:ekr.20061031131434.160: *4* k.enterNamedMode
    def enterNamedMode(self, event, commandName):
        k = self; c = k.c
        modeName = commandName[6:]
        c.inCommand = False # Allow inner commands in the mode.
        k.generalModeHandler(event, modeName=modeName)
    #@+node:ekr.20061031131434.161: *4* k.exitNamedMode
    @cmd('exit-named-mode')
    def exitNamedMode(self, event=None):
        '''Exit an input mode.'''
        k = self
        if k.inState():
            k.endMode()
        k.showStateAndMode()
    #@+node:ekr.20061031131434.165: *4* k.modeHelp & helper (revise helper)
    @cmd('mode-help')
    def modeHelp(self, event):
        '''The mode-help command.

        A possible convention would be to bind <Tab> to this command in most modes,
        by analogy with tab completion.'''
        k = self; c = k.c
        c.endEditing()
        # g.trace(k.inputModeName)
        if k.inputModeName:
            d = g.app.config.modeCommandsDict.get('enter-' + k.inputModeName)
            k.modeHelpHelper(d)
        if not k.silentMode:
            c.minibufferWantsFocus()
    #@+node:ekr.20061031131434.166: *5* modeHelpHelper
    def modeHelpHelper(self, d):
        k = self; c = k.c; tabName = 'Mode'
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
            modeName = modeName[: -4].strip()
        prompt = d.get('*command-prompt*')
        if prompt:
            g.es('', '%s\n\n' % (prompt.kind.strip()), tabName=tabName)
        else:
            g.es('', '%s mode\n\n' % modeName, tabName=tabName)
        # This isn't perfect in variable-width fonts.
        for s1, s2 in data:
            g.es('', '%*s %s' % (n, s1, s2), tabName=tabName)
    #@+node:ekr.20061031131434.164: *4* k.reinitMode (call k.createModeBindings???)
    def reinitMode(self, modeName):
        k = self
        d = k.modeBindingsDict
        k.inputModeName = modeName
        w = k.modeWidget if k.silentMode else k.w
        k.createModeBindings(modeName, d, w)
        if k.silentMode:
            k.showStateAndMode()
        else:
            # Do not set the status line here.
            k.setLabelBlue(modeName + ': ') # ,protect=True)
    #@+node:ekr.20120208064440.10199: *4* k.generalModeHandler (OLD)
    def generalModeHandler(self, event,
        commandName=None,
        func=None,
        modeName=None,
        nextMode=None,
        prompt=None
    ):
        '''Handle a mode defined by an @mode node in leoSettings.leo.'''
        k = self; c = k.c
        state = k.getState(modeName)
        if state == 0:
            k.inputModeName = modeName
            k.modePrompt = prompt or modeName
            k.modeWidget = event and event.widget
            k.setState(modeName, 1, handler=k.generalModeHandler)
            self.initMode(event, modeName)
            # Careful: k.initMode can execute commands that will destroy a commander.
            if g.app.quitting or not c.exists: return
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
                    self.reinitMode(modeName) # Re-enter this mode.
                    k.silentMode = silent
                else:
                    k.silentMode = False # All silent modes must do --> set-silent-mode.
                    self.initMode(event, nextMode) # Enter another mode.
    #@+node:ekr.20061031131434.156: *3* k.Modes (changed)
    #@+node:ekr.20061031131434.163: *4* k.initMode (changed)
    def initMode(self, event, modeName):
        k = self; c = k.c
        trace = False and not g.unitTesting
        if not modeName:
            g.trace('oops: no modeName')
            return
        d = g.app.config.modeCommandsDict.get('enter-' + modeName)
        if not d:
            self.badMode(modeName)
            return
        else:
            k.modeBindingsDict = d
            bi = d.get('*command-prompt*')
            if bi:
                prompt = bi.kind # A kludge.
            else:
                prompt = modeName
            if trace: g.trace('modeName: %s prompt: %s d.keys(): %s' % (
                modeName, prompt, sorted(list(d.keys()))))
        k.inputModeName = modeName
        k.silentMode = False
        aList = d.get('*entry-commands*', [])
        if aList:
            for bi in aList:
                commandName = bi.commandName
                if trace: g.trace('entry command:', commandName)
                k.simulateCommand(commandName)
                # Careful, the command can kill the commander.
                if g.app.quitting or not c.exists: return
                # New in Leo 4.5: a startup command can immediately transfer to another mode.
                if commandName.startswith('enter-'):
                    if trace: g.trace('redirect to mode', commandName)
                    return
        # Create bindings after we know whether we are in silent mode.
        w = k.modeWidget if k.silentMode else k.w
        k.createModeBindings(modeName, d, w)
        k.showStateAndMode(prompt=prompt)
    #@+node:ekr.20120208064440.10201: *4* k.NEWgeneralModeHandler (NEW MODES)
    def NEWgeneralModeHandler(self, event,
        commandName=None,
        func=None,
        modeName=None,
        nextMode=None,
        prompt=None
    ):
        '''Handle a mode defined by an @mode node in leoSettings.leo.'''
        k = self; c = k.c
        state = k.getState(modeName)
        if state == 0:
            k.inputModeName = modeName
            k.modePrompt = prompt or modeName
            k.modeWidget = event and event.widget
            k.setState(modeName, 1, handler=k.generalModeHandler)
            self.initMode(event, modeName)
            # Careful: k.initMode can execute commands that will destroy a commander.
            if g.app.quitting or not c.exists: return
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
                    self.reinitMode(modeName) # Re-enter this mode.
                    k.silentMode = silent
                else:
                    k.silentMode = False # All silent modes must do --> set-silent-mode.
                    self.initMode(event, nextMode) # Enter another mode.
                    # Careful: k.initMode can execute commands that will destroy a commander.
                    # if g.app.quitting or not c.exists: return
    #@+node:ekr.20061031131434.181: *3* k.Shortcuts & bindings
    #@+node:ekr.20061031131434.176: *4* k.computeInverseBindingDict
    def computeInverseBindingDict(self):
        k = self
        d = {}
            # keys are minibuffer command names, values are shortcuts.
        for stroke in k.bindingsDict:
            assert g.isStroke(stroke), repr(stroke)
            aList = k.bindingsDict.get(stroke, [])
            for bi in aList:
                shortcutList = k.bindingsDict.get(bi.commandName, [])
                    # Bug fix: 2017/03/26.
                bi_list = k.bindingsDict.get(stroke, g.BindingInfo(kind='dummy', pane='all'))
                    # Important: only bi.pane is required below.
                for bi in bi_list:
                    pane = '%s:' % (bi.pane)
                    data = (pane, stroke)
                    if data not in shortcutList:
                        shortcutList.append(data)
                d[bi.commandName] = shortcutList
        return d
    #@+node:ekr.20061031131434.179: *4* k.getShortcutForCommand/Name
    def getStrokeForCommandName(self, commandName):
        k = self; c = k.c
        command = c.commandsDict.get(commandName)
        if command:
            for stroke, aList in k.bindingsDict.items():
                for bi in aList:
                    if bi.commandName == commandName:
                        return stroke
        return None
    #@+node:ekr.20090518072506.8494: *4* k.isFKey
    def isFKey(self, stroke):
        # k = self
        if not stroke: return False
        assert g.isString(stroke) or g.isStroke(stroke)
        s = stroke.s if g.isStroke(stroke) else stroke
        s = s.lower()
        return s.startswith('f') and len(s) <= 3 and s[1:].isdigit()
    #@+node:ekr.20061031131434.182: *4* k.isPlainKey
    def isPlainKey(self, stroke):
        '''Return true if the shortcut refers to a plain (non-Alt,non-Ctl) key.'''
        if not stroke:
            return False
        if not g.isStroke(stroke):
            # Happens during unit tests.
            # g.trace('=====', repr(stroke), g.callers())
            stroke = g.KeyStroke(stroke)
        #
        # altgr combos (Alt+Ctrl) are always plain keys
        # g.KeyStroke does not handle this, because it has no "c" ivar.
        #
        if stroke.isAltCtrl() and not self.enable_alt_ctrl_bindings:
            return True
        return stroke.isPlainKey()
    #@+node:ekr.20061031131434.191: *4* k.prettyPrintKey
    def prettyPrintKey(self, stroke, brief=False):
        
        if not stroke:
            return ''
        if not g.assert_is(stroke, g.KeyStroke):
            return stroke
        return stroke.prettyPrint()
    #@+node:ekr.20110609161752.16459: *4* k.setLossage
    def setLossage(self, ch, stroke):
        trace = False and not g.unitTesting
        # k = self
        if trace: g.trace(repr(stroke), g.callers())
        if ch or stroke:
            if len(g.app.lossage) > 99:
                g.app.lossage.pop()
        # This looks like a memory leak, but isn't.
        g.app.lossage.insert(0, (ch, stroke),)
    #@+node:ekr.20110606004638.16929: *4* k.stroke2char
    def stroke2char(self, stroke):
        '''
        Convert a stroke to an (insertable) char.
        This method allows Leo to use strokes everywhere.
        '''
        if not stroke:
            return ''
        if not g.isStroke(stroke):
            # vim commands pass a plain key.
            stroke = g.KeyStroke(stroke)
        return stroke.toInsertableChar()
    #@+node:ekr.20061031131434.193: *3* k.States
    #@+node:ekr.20061031131434.194: *4* k.clearState
    def clearState(self):
        '''Clear the key handler state.'''
        k = self
        k.state.kind = None
        k.state.n = None
        k.state.handler = None
    #@+node:ekr.20061031131434.196: *4* k.getState
    def getState(self, kind):
        k = self
        val = k.state.n if k.state.kind == kind else 0
        # g.trace(state,'returns',val)
        return val
    #@+node:ekr.20061031131434.195: *4* k.getStateHandler
    def getStateHandler(self):
        return self.state.handler
    #@+node:ekr.20061031131434.197: *4* k.getStateKind
    def getStateKind(self):
        return self.state.kind
    #@+node:ekr.20061031131434.198: *4* k.inState
    def inState(self, kind=None):
        k = self
        if kind:
            return k.state.kind == kind and k.state.n is not None
        else:
            return k.state.kind and k.state.n is not None
    #@+node:ekr.20080511122507.4: *4* k.setDefaultInputState
    def setDefaultInputState(self):
        k = self; state = k.defaultUnboundKeyAction
        # g.trace(state)
        k.setInputState(state)
    #@+node:ekr.20110209093958.15411: *4* k.setEditingState
    def setEditingState(self):
        k = self; state = k.defaultEditingAction
        # g.trace(state)
        k.setInputState(state)
    #@+node:ekr.20061031131434.133: *4* k.setInputState
    def setInputState(self, state, set_border=False):
        k = self
        k.unboundKeyAction = state
    #@+node:ekr.20061031131434.199: *4* k.setState
    def setState(self, kind, n, handler=None):
        trace = False and not g.unitTesting
        k = self
        if kind and n is not None:
            if trace: g.trace('**** setting %s %s %s' % (
                kind, n, handler and handler.__name__), g.callers())
            k.state.kind = kind
            k.state.n = n
            if handler:
                k.state.handler = handler
        else:
            if trace: g.trace('clearing')
            k.clearState()
        # k.showStateAndMode()
    #@+node:ekr.20061031131434.192: *4* k.showStateAndMode
    def showStateAndMode(self, w=None, prompt=None, setFocus=True):
        '''Show the state and mode at the start of the minibuffer.'''
        trace = False and not g.unitTesting
        c, k = self.c, self
        state = k.unboundKeyAction
        mode = k.getStateKind()
        if not g.app.gui:
            if trace: g.trace('no gui')
            return
        if not w:
            if hasattr(g.app.gui, 'set_minibuffer_label'):
                pass # we don't need w
            else:
                w = g.app.gui.get_focus(c)
                if not w:
                    if trace: g.trace('no focus')
                    return
        isText = g.isTextWrapper(w)
        # This fixes a problem with the tk gui plugin.
        if mode and mode.lower().startswith('isearch'):
            if trace: g.trace('isearch')
            return
        wname = g.app.gui.widget_name(w).lower()
        # Get the wrapper for the headline widget.
        if wname.startswith('head'):
            if hasattr(c.frame.tree, 'getWrapper'):
                if hasattr(w, 'widget'): w2 = w.widget
                else: w2 = w
                w = c.frame.tree.getWrapper(w2, item=None)
                isText = bool(w) # A benign hack.
        if mode:
            if mode in ('getArg', 'getFileName', 'full-command'):
                s = None
            elif prompt:
                s = prompt
            else:
                mode = mode.strip()
                if mode.endswith('-mode'):
                    mode = mode[: -5]
                s = '%s Mode' % mode.capitalize()
        elif c.vim_mode and c.vimCommands:
            if trace: g.trace('vim')
            c.vimCommands.show_status()
            return
        else:
            s = '%s State' % state.capitalize()
            if c.editCommands.extendMode:
                s = s + ' (Extend Mode)'
        if trace:
            # g.trace('state: %s, text?: %s, w: %s' % (state, isText, w))
            g.trace(repr(s))
        if s:
            k.setLabelBlue(s)
        if w and isText:
            # k.showStateColors(inOutline,w)
            k.showStateCursor(state, w)
        # 2015/07/11: reset the status line.
        if hasattr(c.frame.tree, 'set_status_line'):
            c.frame.tree.set_status_line(c.p)
    #@+node:ekr.20110202111105.15439: *4* k.showStateCursor
    def showStateCursor(self, state, w):
        # g.trace(state,w)
        pass
    #@+node:ekr.20061031131434.200: *3* k.universalDispatcher & helpers
    def universalDispatcher(self, event):
        '''Handle accumulation of universal argument.'''
        #@+<< about repeat counts >>
        #@+node:ekr.20061031131434.201: *4* << about repeat counts >>
        #@@nocolor
        #@+at  Any Emacs command can be given a numeric argument. Some commands interpret the
        # argument as a repetition count. For example, giving an argument of ten to the
        # key C-f (the command forward-char, move forward one character) moves forward ten
        # characters. With these commands, no argument is equivalent to an argument of
        # one. Negative arguments are allowed. Often they tell a command to move or act
        # backwards.
        # 
        # If your keyboard has a META key, the easiest way to specify a numeric argument
        # is to type digits and/or a minus sign while holding down the the META key. For
        # example,
        # 
        # M-5 C-n
        # 
        # moves down five lines. The characters Meta-1, Meta-2, and so on, as well as
        # Meta--, do this because they are keys bound to commands (digit-argument and
        # negative-argument) that are defined to contribute to an argument for the next
        # command.
        # 
        # Another way of specifying an argument is to use the C-u (universal-argument)
        # command followed by the digits of the argument. With C-u, you can type the
        # argument digits without holding down shift keys. To type a negative argument,
        # start with a minus sign. Just a minus sign normally means -1. C-u works on all
        # terminals.
        # 
        # C-u followed by a character which is neither a digit nor a minus sign has the
        # special meaning of "multiply by four". It multiplies the argument for the next
        # command by four. C-u twice multiplies it by sixteen. Thus, C-u C-u C-f moves
        # forward sixteen characters. This is a good way to move forward "fast", since it
        # moves about 1/5 of a line in the usual size screen. Other useful combinations
        # are C-u C-n, C-u C-u C-n (move down a good fraction of a screen), C-u C-u C-o
        # (make "a lot" of blank lines), and C-u C-k (kill four lines).
        # 
        # Some commands care only about whether there is an argument and not about its
        # value. For example, the command M-q (fill-paragraph) with no argument fills
        # text; with an argument, it justifies the text as well. (See section Filling
        # Text, for more information on M-q.) Just C-u is a handy way of providing an
        # argument for such commands.
        # 
        # Some commands use the value of the argument as a repeat count, but do something
        # peculiar when there is no argument. For example, the command C-k (kill-line)
        # with argument n kills n lines, including their terminating newlines. But C-k
        # with no argument is special: it kills the text up to the next newline, or, if
        # point is right at the end of the line, it kills the newline itself. Thus, two
        # C-k commands with no arguments can kill a non-blank line, just like C-k with an
        # argument of one. (See section Deletion and Killing, for more information on
        # C-k.)
        # 
        # A few commands treat a plain C-u differently from an ordinary argument. A few
        # others may treat an argument of just a minus sign differently from an argument
        # of -1. These unusual cases will be described when they come up; they are always
        # to make the individual command more convenient to use.
        #@-<< about repeat counts >>
        k = self
        state = k.getState('u-arg')
        stroke = event.stroke if event else ''
        if state == 0:
            k.dispatchEvent = event
            # The call should set the label.
            k.setState('u-arg', 1, k.universalDispatcher)
            k.repeatCount = 1
        elif state == 1:
            char = event.char if event else ''
            if char == 'Escape':
                k.keyboardQuit()
            elif char == k.universalArgKey:
                k.repeatCount = k.repeatCount * 4
            elif char.isdigit() or char == '-':
                k.updateLabel(event)
            elif char in (
                'Alt_L', 'Alt_R',
                'Control_L', 'Control_R',
                'Meta_L', 'Meta_R',
                'Shift_L', 'Shift_R',
            ):
                k.updateLabel(event)
            else:
                # *Anything* other than C-u, '-' or a numeral is taken to be a command.
                val = k.getLabel(ignorePrompt=True)
                try: n = int(val) * k.repeatCount
                except ValueError: n = 1
                k.clearState()
                event = k.dispatchEvent
                k.executeNTimes(event, n)
                k.keyboardQuit()
        elif state == 2:
            k.doControlU(event, stroke)
    #@+node:ekr.20061031131434.202: *4* k.executeNTimes
    def executeNTimes(self, event, n):
        trace = False and not g.unitTesting
        c, k = self.c, self
        w = event and event.widget
        stroke = event.stroke if event else ''
        if not stroke: return
        if stroke == k.fullCommandKey:
            for z in range(n):
                k.fullCommand(event)
        else:
            bi = k.getPaneBinding(stroke, event and event.widget)
            if bi:
                if trace: g.trace('repeat: %s, func: %s, stroke: %s, widget: %s' % (
                    n, bi.func.__name__, stroke, w))
                for z in range(n):
                    event = g.app.gui.create_key_event(c, event=event, w=w)
                    k.masterCommand(
                        commandName=None,
                        event=event,
                        func=bi.func,
                        stroke=stroke)
            else:
                for z in range(n):
                    k.masterKeyHandler(event)
    #@+node:ekr.20061031131434.203: *4* doControlU
    def doControlU(self, event, stroke):
        k = self
        ch = event.char if event else ''
        k.setLabelBlue('Control-u %s' % g.stripBrackets(stroke))
        if ch == '(':
            k.clearState()
            k.resetLabel()
    #@-others
#@+node:ekr.20120208064440.10150: ** class ModeInfo
class ModeInfo(object):

    def __repr__(self):
        return '<ModeInfo %s>' % self.name

    __str__ = __repr__
    #@+others
    #@+node:ekr.20120208064440.10193: *3* mode_i. ctor
    def __init__(self, c, name, aList):
        g.trace(name, aList)
        self.c = c
        self.d = {} # The bindings in effect for this mode.
            # Keys are names of (valid) command names, values are BindingInfo objects.
        self.entryCommands = []
            # A list of BindingInfo objects.
        self.k = c.k
        self.name = self.computeModeName(name)
        self.prompt = self.computeModePrompt(self.name)
        self.init(name, aList)
    #@+node:ekr.20120208064440.10152: *3* mode_i.computeModeName
    def computeModeName(self, name):
        s = name.strip().lower()
        j = s.find(' ')
        if j > -1: s = s[: j]
        if s.endswith('mode'):
            s = s[: -4].strip()
        if s.endswith('-'):
            s = s[: -1]
        i = s.find('::')
        if i > -1:
            # The actual mode name is everything up to the "::"
            # The prompt is everything after the prompt.
            s = s[: i]
        return s + '-mode'
    #@+node:ekr.20120208064440.10156: *3* mode_i.computeModePrompt
    def computeModePrompt(self, name):
        assert name == self.name
        s = 'enter-' + name.replace(' ', '-')
        i = s.find('::')
        if i > -1:
            # The prompt is everything after the '::'
            prompt = s[i + 2:].strip()
        else:
            prompt = s
        return prompt
    #@+node:ekr.20120208064440.10160: *3* mode_i.createModeBindings
    def createModeBindings(self, w):
        '''Create mode bindings for w, a text widget.'''
        trace = False and not g.unitTesting
        c, d, k, modeName = self.c, self.d, self.k, self.name
        for commandName in d:
            func = c.commandsDict.get(commandName)
            if not func:
                g.es_print('no such command: %s Referenced from %s' % (
                    commandName, modeName))
                continue
            aList = d.get(commandName, [])
            for bi in aList:
                if trace: g.trace(bi)
                stroke = bi.stroke
                # Important: bi.val is canonicalized.
                if stroke and stroke not in ('None', 'none', None):
                    if trace:
                        g.trace(
                            g.app.gui.widget_name(w), modeName,
                            '%10s' % (stroke),
                            '%20s' % (commandName),
                            bi.nextMode)
                    assert g.isStroke(stroke)
                    k.makeMasterGuiBinding(stroke)
                    # Create the entry for the mode in k.masterBindingsDict.
                    # Important: this is similar, but not the same as k.bindKeyToDict.
                    # Thus, we should **not** call k.bindKey here!
                    d2 = k.masterBindingsDict.get(modeName, {})
                    d2[stroke] = g.BindingInfo(
                        kind='mode<%s>' % (modeName), # 2012/01/23
                        commandName=commandName,
                        func=func,
                        nextMode=bi.nextMode,
                        stroke=stroke)
                    k.masterBindingsDict[modeName] = d2
                    if trace: g.trace(modeName, d2)
    #@+node:ekr.20120208064440.10195: *3* mode_i.createModeCommand
    def createModeCommand(self):
        c = self.c
        key = 'enter-' + self.name.replace(' ', '-')

        def enterModeCallback(event=None, self=self):
            self.enterMode()

        c.commandsDict[key] = f = enterModeCallback
        g.trace('(ModeInfo)', f.__name__, key,
            'len(c.commandsDict.keys())', len(list(c.commandsDict.keys())))
    #@+node:ekr.20120208064440.10180: *3* mode_i.enterMode
    def enterMode(self):
        g.trace('(ModeInfo)')
        c, k = self.c, self.k
        c.inCommand = False
            # Allow inner commands in the mode.
        event = None
        k.generalModeHandler(event, modeName=self.name)
    #@+node:ekr.20120208064440.10153: *3* mode_i.init
    def init(self, name, dataList):
        '''aList is a list of tuples (commandName,bi).'''
        trace = False and not g.unitTesting
        c, d, modeName = self.c, self.d, self.name
        for name, bi in dataList:
            if not name:
                if trace: g.trace('entry command', bi)
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
                    if trace: g.trace('inheriting', [bi.val for bi in aList3])
                    aList.extend(aList3)
                aList.append(bi)
                d[name] = aList
    #@+node:ekr.20120208064440.10158: *3* mode_i.initMode
    def initMode(self):
        trace = False and not g.unitTesting
        c, k = self.c, self.c.k
        k.inputModeName = self.name
        k.silentMode = False
        for bi in self.entryCommands:
            commandName = bi.commandName
            if trace: g.trace('entry command:', commandName)
            k.simulateCommand(commandName)
            # Careful, the command can kill the commander.
            if g.app.quitting or not c.exists: return
            # New in Leo 4.5: a startup command can immediately transfer to another mode.
            if commandName.startswith('enter-'):
                if trace: g.trace('redirect to mode', commandName)
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
