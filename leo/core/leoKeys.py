#@+leo-ver=5-thin
#@+node:ekr.20061031131434: * @file leoKeys.py
"""Gui-independent keystroke handling for Leo.""" 

#@@language python
#@@tabwidth -4
#@@pagewidth 70

#@+<< imports >>
#@+node:ekr.20061031131434.1: ** << imports >> (leoKeys)
import leo.core.leoGlobals as g

import leo.external.codewise as codewise

import glob
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
# 2. An instance of leoQtEventFilter should be attached to all visible panes
#    in Leo's main window. g.app.gui.setFilter does this.
#    
# 3. leoQtEventFilter.eventFilter calls k.masterKeyhandler for every
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
#    argument to setFilter can be either the same as obj, or a Leo wrapper
#    class the supports the HighLevelInterface protocol. **Important**: the
#    types of obj and w are not actually all that important, as discussed
#    next.
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
# !, Key-!,Key-exclam,exclam
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
# k.inverseCommandsDict   func.__name__       command names
# k.bindingsDict          shortcuts           lists of ShortcutInfo objects
# k.masterBindingsDict    scope names (2)     Interior masterBindingDicts (3)
# k.masterGuiBindingsDict strokes             list of widgets in which stoke is bound
# k.settingsNameDict (4)  settings.lower()    "Real" Tk specifiers
# inverseBindingDict (5)  command names       lists of tuples (pane,key)
# modeCommandsDict (6)    command name (7)    inner modeCommandsDicts (8)
# 
# Notes:
# 
# (1) Command names are minibuffer names (strings)
# (2) Scope names are 'all','text',etc.
# (3) Interior masterBindingDicts: Keys are strokes; values are ShortcutInfo objects.
# (4) k.settingsNameDict has no inverse.
# (5) inverseBindingDict is **not** an ivar: it is computed by k.computeInverseBindingDict.
# (6) A global dict: g.app.gui.modeCommandsDict
# (7) enter-x-command
# (8) Keys are command names, values are lists of ShortcutInfo objects.
#@-<< about key dicts >>

#@+others
#@+node:ekr.20061031131434.4: ** class AutoCompleterClass
class AutoCompleterClass:

    '''A class that inserts autocompleted and calltip text in text widgets.
    This class shows alternatives in the tabbed log pane.

    The keyHandler class contains hooks to support these characters:
    invoke-autocompleter-character (default binding is '.')
    invoke-calltips-character (default binding is '(')
    '''

    #@+others
    #@+node:ekr.20061031131434.5: *3*  ctor (autocompleter)
    def __init__ (self,k):

        # Ivars...
        self.c = c = k.c
        self.k = k
        self.force = None
        self.language = None
        self.qw = None # The object that supports qcompletion methods.
        self.tabName = None # The name of the main completion tab.
        self.verbose = False # True: print all members, regardless of how many there are.
        self.w = None # The widget that gets focus after autocomplete is done.
        self.warnings = {} # Keys are language names.
        self.klass = None

        # Codewise pre-computes...
        self.codewiseSelfList = []
            # The (global) completions for "self."
        self.completionsDict = {}
            # Keys are prefixes, values are completion lists.

        # Options...
        self.auto_tab       = c.config.getBool('auto_tab_complete',False)
        self.forbid_invalid = c.config.getBool('forbid_invalid_completions',False)
        self.use_qcompleter = c.config.getBool('use_qcompleter',False)
            # True: show results in autocompleter tab.
            # False: show results in a QCompleter widget.
    #@+node:ekr.20061031131434.8: *3* Top level (autocompleter)
    #@+node:ekr.20061031131434.9: *4* autoComplete
    def autoComplete (self,event=None,force=False):

        '''An event handler called from k.masterKeyHanderlerHelper.'''

        trace = False and not g.unitTesting
        c,k = self.c,self.k
        state = k.unboundKeyAction
        w = event and event.w or c.get_focus()
        self.force = force
        self.klass = None
        if not state in ('insert','overwrite'):
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

        self.language = g.scanForAtLanguage(c,c.p)
        if w and (k.enable_autocompleter or force): # self.language == 'python':
            if trace: g.trace('starting')
            self.w = w
            self.start(event)
        else:
            if trace: g.trace('autocompletion not enabled')
    #@+node:ekr.20061031131434.10: *4* autoCompleteForce
    def autoCompleteForce (self,event=None):

        '''Show autocompletion, even if autocompletion is not presently enabled.'''

        return self.autoComplete(event,force=True)
    #@+node:ekr.20061031131434.12: *4* enable/disable/toggleAutocompleter/Calltips
    def disableAutocompleter (self,event=None):
        '''Disable the autocompleter.'''
        self.k.enable_autocompleter = False
        self.showAutocompleterStatus()

    def disableCalltips (self,event=None):
        '''Disable calltips.'''
        self.k.enable_calltips = False
        self.showCalltipsStatus()

    def enableAutocompleter (self,event=None):
        '''Enable the autocompleter.'''
        self.k.enable_autocompleter = True
        self.showAutocompleterStatus()

    def enableCalltips (self,event=None):
        '''Enable calltips.'''
        self.k.enable_calltips = True
        self.showCalltipsStatus()

    def toggleAutocompleter (self,event=None):
        '''Toggle whether the autocompleter is enabled.'''
        self.k.enable_autocompleter = not self.k.enable_autocompleter
        self.showAutocompleterStatus()

    def toggleCalltips (self,event=None):
        '''Toggle whether calltips are enabled.'''
        self.k.enable_calltips = not self.k.enable_calltips
        self.showCalltipsStatus()
    #@+node:ekr.20061031131434.13: *4* showCalltips
    def showCalltips (self,event=None,force=False):

        '''Show the calltips at the cursor.'''

        c = self.c ; k = c.k
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
    #@+node:ekr.20061031131434.14: *4* showCalltipsForce
    def showCalltipsForce (self,event=None):

        '''Show the calltips at the cursor, even if calltips are not presently enabled.'''

        return self.showCalltips(event,force=True)
    #@+node:ekr.20061031131434.15: *4* showAutocompleter/CalltipsStatus
    def showAutocompleterStatus (self):
        '''Show the autocompleter status.'''

        k = self.k
        if not g.unitTesting:
            s = 'autocompleter %s' % (
                g.choose(k.enable_autocompleter,'On','Off'))
            g.red(s)

    def showCalltipsStatus (self):
        '''Show the autocompleter status.'''
        k = self.k
        if not g.unitTesting:
            s = 'calltips %s' % g.choose(k.enable_calltips,'On','Off')
            g.red(s)
    #@+node:ekr.20061031131434.16: *3* Helpers
    #@+node:ekr.20110512212836.14469: *4* exit
    def exit (self):

        trace = False and not g.unitTesting
        if trace: g.trace(g.callers())

        c = self.c
        w = self.w or c.frame.body.bodyCtrl

        if trace: g.trace(g.callers())

        c.k.keyboardQuit()

        if self.use_qcompleter:
            if self.qw:
                self.qw.end_completer()
                self.qw = None # Bug fix: 2013/09/24.
        else:
            for name in (self.tabName,'Modules','Info'):
                c.frame.log.deleteTab(name)

        # Restore the selection range that may have been destroyed by changing tabs.
        c.widgetWantsFocusNow(w)
        i,j = w.getSelectionRange()
        w.setSelectionRange(i,j,insert=j)

        # Was in finish.
        c.frame.body.onBodyChanged('Typing')
        c.recolor()

    finish = exit
    abort = exit
    #@+node:ekr.20061031131434.18: *4* append/begin/popTabName
    def appendTabName (self,word):

        self.setTabName(self.tabName + '.' + word)

    def beginTabName (self,word):

        self.setTabName('AutoComplete ' + word)

    def clearTabName (self):

        self.setTabName('AutoComplete ')

    def popTabName (self):

        s = self.tabName
        i = s.rfind('.',0,-1)
        if i > -1:
            self.setTabName(s[0:i])

    # Underscores are not valid in Pmw tab names!
    def setTabName (self,s):

        c = self.c
        if self.tabName:
            c.frame.log.deleteTab(self.tabName)
        self.tabName = s.replace('_','') or ''
        c.frame.log.clearTab(self.tabName)
    #@+node:ekr.20110509064011.14556: *4* attr_matches
    def attr_matches(self,s,namespace):

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
        m = re.match(r"(\S+(\.\w+)*)\.(\w*)$",s)
        if not m:
            return []

        expr,attr = m.group(1,3)

        try:
            safe_expr = self.strip_brackets(expr)
            obj = eval(safe_expr,namespace)
        except Exception:
            return []

        # Build the result.
        words = dir(obj)
        n = len(attr)
        result = ["%s.%s" % (expr,w) for w in words if w[:n] == attr]

        if trace:
            if verbose:
                g.trace(s,result)
            else:
                g.trace(repr(s))
        return result
    #@+node:ekr.20061031131434.11: *4* auto_completer_state_handler
    def auto_completer_state_handler (self,event):

        trace = False and not g.app.unitTesting
        c = self.c ; k = self.k
        tag = 'auto-complete' ; state = k.getState(tag)
        ch = event and event.char or ''
        stroke = event and event.stroke or None
        is_plain = k.isPlainKey(stroke)
        if trace: g.trace('state: %s, ch: %s, stroke: %s' % (
            state,repr(ch),repr(stroke)))

        if state == 0:
            c.frame.log.clearTab(self.tabName)
            common_prefix,prefix,tabList = self.compute_completion_list()
            if tabList:
                k.setState(tag,1,handler=self.auto_completer_state_handler)
            else:
                if trace: g.trace('abort: not tabList')
                self.exit()
        elif ch in ('\n','Return'):
            self.exit()
        elif ch == 'Escape':
            self.exit()
        elif ch in ('\t','Tab'):
            self.compute_completion_list()
            # k.doTabCompletion(tabList)
        elif ch in ('\b','BackSpace'):
            self.do_backspace()
        elif ch == '.':
            self.insert_string('.')
            self.compute_completion_list()
        elif ch == '?':
            self.info()
        elif ch == '!':
            # Toggle between verbose and brief listing.
            self.verbose = not self.verbose
            kind = g.choose(self.verbose,'ON','OFF')
            c.frame.putStatusLine('verbose completions %s' % (
                kind),color='red')
            self.compute_completion_list()
        # elif ch == 'Down' and hasattr(self,'onDown'):
            # self.onDown()
        # elif ch == 'Up' and hasattr(self,'onUp'):
            # self.onUp()
        elif is_plain and ch and ch in string.printable:
            self.insert_general_char(ch)
        else:
            if stroke == k.autoCompleteForceKey:
                # This is probably redundant because completions will exist.
                # However, it doesn't hurt, and it may be useful rarely.
                if trace: g.trace('auto-complete-force',repr(stroke))
                common_prefix,prefix,tabList = self.compute_completion_list()
                if tabList:
                    self.show_completion_list(common_prefix,prefix,tabList)
                else:
                    g.warning('No completions')
                    self.exit()
                return None
            else:
                if trace: g.trace('ignore non plain key',repr(stroke),g.callers())
                self.abort() # 2011/06/17.
                return 'do-standard-keys'
    #@+node:ekr.20061031131434.20: *4* calltip & helpers
    def calltip (self):

        '''Show the calltips for the present prefix.
        ch is '(' if the user has just typed it.
        '''

        obj,prefix = self.get_object()
        if obj:
            self.calltip_success(prefix,obj)
        else:
            self.calltip_fail(prefix)
        self.exit()
    #@+node:ekr.20110512090917.14468: *5* calltip_fail
    def calltip_fail(self,prefix):

        '''Evaluation of prefix failed.'''

        trace = False and not g.unitTesting

        if trace:
            g.es('eval failed for "%s"' % repr(prefix))

        self.insert_string('(')
    #@+node:ekr.20110512090917.14469: *5* calltip_success
    def calltip_success(self,prefix,obj):

        trace = False and not g.unitTesting

        try:
            # Get the parenthesized argument list.
            s1,s2,s3,s4 = inspect.getargspec(obj)
            s = inspect.formatargspec(s1,s2,s3,s4)
            if trace: g.trace(obj,repr(s))
        except Exception:
            if trace: g.trace('inspect failed. obj: %s' % (obj))
            self.insert_string('(')
            return

        # Clean s and insert it: don't include the opening "(".
        if g.match(s,1,'self,'):
            s = s[6:].strip()
        elif g.match_word(s,1,'self'):
            s = s[5:].strip()
        else:
            s = s[1:].strip()

        self.insert_string("(",select=False)
        self.insert_string(s,select=True)
    #@+node:ekr.20061031131434.28: *4* compute_completion_list & helper
    def compute_completion_list (self):

        trace = False and not g.unitTesting
        verbose = False
            # True: report hits and misses.
            # False: report misses.

        if self.klass:
            prefix = ''
            # something later on eats the first char, not sure what
            options = ['^'+i for i in self.lookup_methods([str(self.klass)],None)]
            g.es("%s: %d options" % (self.klass, len(options)))
            self.klass = None
        else:
            prefix = self.get_autocompleter_prefix()
            key,options = self.get_cached_options(prefix)
            if options:
                if trace and verbose: g.trace('**prefix hit: %s, %s' % (prefix,key))
            else:
                if trace: g.trace('**prefix miss: %s, %s' % (prefix,key))
                options = self.get_completions(prefix)

        tabList,common_prefix = g.itemsMatchingPrefixInList(
            prefix,options,matchEmptyPrefix=False)

        if not common_prefix:
            tabList,common_prefix = g.itemsMatchingPrefixInList(
                prefix,options,matchEmptyPrefix=True)

        if trace and verbose:
            g.trace('prefix: %s, common: %s, len(tabList): %s' % (
                repr(prefix),repr(common_prefix),len(tabList)))
            # if verbose: g.trace('options[:10]...\n',
                # g.listToString(options[:10],sort=True))

        if tabList:
            self.show_completion_list(common_prefix,prefix,tabList)

        return common_prefix,prefix,tabList
    #@+node:ekr.20110514051607.14524: *5* get_cached_options
    def get_cached_options(self,prefix):

        trace = False and not g.unitTesting
        d = self.completionsDict

        # Search the completions Dict for shorter and shorter prefixes.
        i = len(prefix)

        while i > 0:
            key = prefix[:i]
            i -= 1
            # Make sure we report hits only of real objects.
            if key.endswith('.'):
                if trace: g.trace('== period: %s' % (key))
                return key,[]
            options = d.get(key)
            if options:
                if trace: g.trace('== hit: %s len: %s' % (
                    key,len(options)))
                return key,options
            else:
                if trace: g.trace('== miss: %s' % (key))

        return None,[]
    #@+node:ekr.20061031131434.29: *4* do_backspace
    def do_backspace (self):

        '''Delete the character and recompute the completion list.'''

        c,w = self.c,self.w
        c.bodyWantsFocusNow()

        i = w.getInsertPoint()
        if i <= 0:
            self.exit()
            return

        w.delete(i-1,i)
        w.setInsertPoint(i-1)

        if i <= 1:
            self.exit()
        else:
            # Update the list. Abort if there is no prefix.
            common_prefix,prefix,tabList = self.compute_completion_list()
            if not prefix:
                self.exit()
    #@+node:ekr.20110510133719.14548: *4* do_qcompleter_tab
    def do_qcompleter_tab(self,prefix,options):

        '''Return the longest common prefix of all the options.'''

        trace = False and not g.unitTesting

        matches,common_prefix = g.itemsMatchingPrefixInList(
            prefix,options,matchEmptyPrefix=False)

        if trace: g.trace(repr(common_prefix))

        return common_prefix
    #@+node:ekr.20110509064011.14561: *4* get_autocompleter_prefix
    def get_autocompleter_prefix (self):

        trace = False and not g.unitTesting

        # Only the body pane supports auto-completion.
        w = self.c.frame.body
        s = w.getAllText()
        if not s: return ''
        i = w.getInsertPoint() - 1
        i1 = i = j = max(0,i)
        while i >= 0 and (s[i].isalnum() or s[i] in '._'):
            i -= 1
        i += 1
        j += 1
        prefix = s[i:j]
        if trace: g.trace(repr(prefix),'ins',s[i1:])
        return prefix
    #@+node:ekr.20110512212836.14471: *4* get_completions & helpers
    def get_completions(self,prefix):

        trace = False and not g.unitTesting
        verbose = False # True: report hits and misses.  False: report misses.
        d = self.completionsDict

        # Precompute the codewise completions for '.self'.
        if not self.codewiseSelfList:
            aList = self.get_codewise_completions('self.')
            self.codewiseSelfList = [z[5:] for z in aList]
            d ['self.'] = self.codewiseSelfList

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
        d [prefix] = aList
        return aList
    #@+node:ekr.20110510120621.14539: *5* get_codewise_completions & helpers
    def get_codewise_completions(self,prefix):

        '''Use codewise to generate a list of hits.'''

        trace = False and not g.unitTesting
        c = self.c

        m = re.match(r"(\S+(\.\w+)*)\.(\w*)$", prefix)
        if m:
            varname = m.group(1)
            ivar = m.group(3)
            kind,aList = self.guess_class(c,varname)
        else:
            kind,aList = 'none',[]
            varname,ivar = None,None

        if aList:
            if kind == 'class':
                hits = self.lookup_methods(aList,ivar)
                hits.extend(self.codewiseSelfList)
            elif kind == 'module':
                hits = self.lookup_modules(aList,ivar)
        else:
            aList2 = prefix.split('.')
            if aList2:
                func = aList2[-1]
                hits = self.lookup_functions(func)
            else:
                hits = []

        if 1: # A kludge: add the prefix to each hit.
            hits = ['%s.%s' % (varname,z) for z in hits]

        if trace:
            g.trace('kind',kind,'varname',varname,'ivar',ivar,'prefix',prefix)
            # g.trace('prefix',prefix,'kind',kind,'varname',varname,'ivar',ivar,'len(hits)',len(hits))
            # g.trace('hits[:10]',g.listToString(hits[:10],sort=False))

        return hits
    #@+node:ekr.20110510120621.14540: *6* clean
    def clean (self,hits):

        '''Clean up hits, a list of ctags patterns, for use in completion lists.'''

        trace = False and not g.unitTesting

        # Just take the function name: ignore the signature & file.
        aList = list(set([z[0] for z in hits]))
        aList.sort()

        if trace:
            # g.trace('hits[:50]',g.listToString(hits[:50],sort=False))
            g.trace('aList[:50]',g.listToString(aList[:50],sort=False))

        return aList
    #@+node:ekr.20110512232915.14481: *6* clean_for_display (not used)
    def clean_for_display(self,hits):

        '''Clean up hits, a list of ctags patterns, for display purposes.'''

        trace = False and not g.unitTesting
        aList = []
        for h in hits:
            s = h[0]
            # Display oriented: no good for completion list.
            fn = h[1].strip()
            if fn.startswith('/'):
                sig = fn[2:-4].strip()
            else:
                sig = fn
            aList.append('%s: %s' % (s,sig))

        aList = list(set(aList))
        aList.sort()
        if trace:
            # g.trace('hits[:50]',g.listToString(hits[:50],sort=False))
            g.trace('aList[:50]',g.listToString(aList[:50],sort=False))
        return aList
    #@+node:ekr.20110510120621.14542: *6* guess_class
    def guess_class(self,c,varname):

        '''Return kind, class_list'''

        # if varname == 'g':
            # return 'module',['leoGlobals']
        if varname == 'p':
            return 'class',['position']
        if varname == 'c':
            return 'class',['Commands']
        if varname == 'self':
            # Return the nearest enclosing class.
            for p in c.p.parents():
                h = p.h
                m = re.search('class\s+(\w+)', h)
                if m:
                    return 'class',[m.group(1)]

        if 1:
            aList = []
        else:
            # This is not needed now that we add the completions for 'self'.
            aList = ContextSniffer().get_classes(c.p.b,varname)

        return 'class',aList
    #@+node:ekr.20110510120621.14543: *6* lookup_functions/methods/modules
    def lookup_functions(self,prefix):

        aList = codewise.cmd_functions([prefix])
        hits = [z.split(None,1) for z in aList if z.strip()]
        return self.clean(hits)

    def lookup_methods(self,aList,prefix): # prefix not used, only aList[0] used.

        aList = codewise.cmd_members([aList[0]])
        hits = [z.split(None,1) for z in aList if z.strip()]
        return self.clean(hits)

    def lookup_modules (self,aList,prefix): # prefix not used, only aList[0] used.

        aList = codewise.cmd_functions([aList[0]])
        hits = [z.split(None,1) for z in aList if z.strip()]
        return self.clean(hits)
    #@+node:ekr.20110509064011.14557: *5* get_leo_completions
    def get_leo_completions(self,prefix):

        '''Return completions in an environment defining c, g and p.'''

        trace = False and not g.unitTesting
        verbose = False

        d = self.get_leo_namespace(prefix)
        if trace: g.trace(list(d.keys()))

        aList = self.attr_matches(prefix,d)
        aList.sort()

        if trace:
            if verbose:
                g.trace('prefix',repr(prefix),'aList...\n',g.listToString(aList))
            else:
                g.trace('len(aList): %3s, prefix: %s' % (len(aList),repr(prefix)))

        return aList
    #@+node:ekr.20110512090917.14466: *4* get_leo_namespace
    def get_leo_namespace (self,prefix):

        '''Return an environment in which to evaluate prefix.

        Add some common standard library modules as needed.'''


        k = self.k
        d = {'c':k.c, 'p':k.c.p, 'g':g}

        aList = prefix.split('.')
        if len(aList) > 1:
            name = aList[0]
            m = sys.modules.get(name)
            if m:
                d[name]= m

        # g.trace(list(d.keys()))
        return d
    #@+node:ekr.20110512170111.14472: *4* get_object
    def get_object (self):

        '''Return the object corresponding to the current prefix.'''

        trace = False and not g.unitTesting

        common_prefix,prefix1,aList = self.compute_completion_list()

        if len(aList) == 0:
            if trace: g.trace('no completion list for: %s' % (prefix1))
            return None,prefix1
        elif len(aList) == 1:
            prefix = aList[0]
        else:
            prefix = common_prefix

        if trace: g.trace(repr(prefix))

        try:
            d = self.get_leo_namespace(prefix)
            safe_prefix = self.strip_brackets(prefix)
            obj = eval(safe_prefix,d)
        except AttributeError:
            obj = None
        except NameError:
            obj = None
        except SyntaxError:
            obj = None
        except Exception:
            g.es_exception()
            obj = None

        return obj,prefix
    #@+node:ekr.20061031131434.38: *4* info
    def info (self):

        c = self.c

        obj,prefix = self.get_object()

        doc = inspect.getdoc(obj)

        if doc:
            c.frame.log.clearTab('Info',wrap='word')
            self.put('',doc,tabName='Info')
        else:
            g.warning('no docstring for',repr(prefix))
    #@+node:ekr.20110510071925.14586: *4* init_qcompleter
    def init_qcompleter (self,event=None):

        trace = False and not g.unitTesting

        # Compute the prefix and the list of options.
        prefix = self.get_autocompleter_prefix()
        options = self.get_completions(prefix)

        if trace: g.trace('prefix: %s, len(options): %s' % (repr(prefix),len(options)))

        w = self.c.frame.body.bodyCtrl.widget
            # A LeoQTextBrowser.  May be none for unit tests.

        if w and options:
            self.qw = w
            self.qcompleter = w.init_completer(options)
            self.auto_completer_state_handler(event)
        else:
            if not g.unitTesting:
                g.warning('No completions')
            self.exit()
    #@+node:ekr.20110511133940.14552: *4* init_tabcompleter
    def init_tabcompleter (self,event=None):

        # Compute the prefix and the list of options.
        prefix = self.get_autocompleter_prefix()
        options = self.get_completions(prefix)
        if options:
            self.clearTabName() # Creates the tabbed pane.
            self.auto_completer_state_handler(event)
        else:
            g.warning('No completions')
            self.exit()
    #@+node:ekr.20061031131434.39: *4* insert_general_char
    def insert_general_char (self,ch):

        trace = False and not g.unitTesting
        c,k = self.c,self.k ; w = self.w

        if trace: g.trace(repr(ch))

        if g.isWordChar(ch):
            self.insert_string(ch)
            common_prefix,prefix,aList = self.compute_completion_list()
            if trace: g.trace('ch',repr(ch),'prefix',repr(prefix),'len(aList)',len(aList))
            if not aList:
                if self.forbid_invalid: # 2011/06/17.
                    # Delete the character we just inserted.
                    self.do_backspace()
            elif self.auto_tab and len(common_prefix) > len(prefix):
                extend = common_prefix[len(prefix):]
                if trace: g.trace('*** extend',extend)
                ins = w.getInsertPoint()
                w.insert(ins,extend)
        else:
            if ch == '(' and k.enable_calltips:
                # This calls self.exit if the '(' is valid.
                self.calltip()
            else:
                if trace: g.trace('ch',repr(ch),'calling exit')
                self.insert_string(ch)
                self.exit()
    #@+node:ekr.20061031131434.31: *4* insert_string
    def insert_string (self,s,select=False):

        '''Insert s at the insertion point.'''

        c = self.c ; w = self.w

        c.widgetWantsFocusNow(w)
        i = w.getInsertPoint()
        w.insert(i,s)
        if select:
            j = i + len(s)
            w.setSelectionRange(i,j,insert=j)

        c.frame.body.onBodyChanged('Typing')

        if self.use_qcompleter:
            # g.trace(self.qw.leo_qc)
            if self.qw:
                c.widgetWantsFocusNow(self.qw.leo_qc)
    #@+node:ekr.20110314115639.14269: *4* is_leo_source_file
    def is_leo_source_file (self):

        '''Return True if this is one of Leo's source files.'''

        c = self.c

        table = (z.lower() for z in (
            'leoDocs.leo',
            'leoGui.leo',       'leoGuiPluginsRef.leo',
            'leoPlugins.leo',   'leoPluginsRef.leo',
            'leoPy.leo',        'leoPyRef.leo',
            'myLeoSettings.leo', 'leoSettings.leo',
            'ekr.leo',
            # 'test.leo',
        ))

        return c.shortFileName().lower() in table
    #@+node:ekr.20101101175644.5891: *4* put
    def put (self,*args,**keys):

        '''Put s to the given tab.

        May be overridden in subclasses.'''

        # print('autoCompleter.put',args,keys)

        if g.unitTesting:
            pass
        else:
            g.es(*args,**keys)
    #@+node:ekr.20110511133940.14561: *4* show_completion_list & helpers
    def show_completion_list (self,common_prefix,prefix,tabList):

        c = self.c

        aList = common_prefix.split('.')
        header = '.'.join(aList[:-1])

        # g.trace(self.use_qcompleter,len(tabList))

        if self.verbose or self.use_qcompleter or len(tabList) < 20:
            tabList = self.clean_completion_list(header,tabList,)
        else:
            tabList = self.get_summary_list(header,tabList)

        if self.use_qcompleter:
            # Put the completions in the QListView.
            if self.qw:
                self.qw.show_completions(tabList)
        else:
            # Update the tab name, creating the tab if necessary.
            c.widgetWantsFocus(self.w)
            c.frame.log.clearTab(self.tabName)
            self.beginTabName(g.choose(header,header+'.',''))
            s = '\n'.join(tabList)
            self.put('',s,tabName=self.tabName)
    #@+node:ekr.20110513104728.14453: *5* clean_completion_list
    def clean_completion_list(self,header,tabList):

        '''Return aList with header removed from the start of each list item.'''

        return [
            g.choose(z.startswith(header),z[len(header)+1:],z)
                for z in tabList]
    #@+node:ekr.20110513104728.14454: *5* get_summary_list
    def get_summary_list (self,header,tabList):

        '''Show the possible starting letters,
        but only if there are more than one.
        '''

        d = {}
        for z in tabList:
            tail = z and z[len(header):] or ''
            if tail.startswith('.'): tail = tail[1:]
            ch = tail and tail[0] or ''
            if ch:
                n = d.get(ch,0)
                d[ch] = n + 1
        aList = ['%s %d' % (ch,d.get(ch)) for ch in sorted(d)]
        if len(aList) > 1:
            tabList = aList
        else:
            tabList = self.clean_completion_list(header,tabList)
        return tabList
    #@+node:ekr.20061031131434.46: *4* start
    def start (self,event):

        # We don't need to clear this now that we don't use ContextSniffer.
        # self.completionsDict = {}

        if self.use_qcompleter:
            self.init_qcompleter(event)
        else:
            self.init_tabcompleter(event)
    #@+node:ekr.20110512170111.14471: *4* strip_brackets
    def strip_brackets(self,s):

        '''Return s with all brackets removed.

        This (mostly) ensures that eval will not execute function calls, etc.
        '''

        for ch in '[]{}()':
            s = s.replace(ch,'')

        return s
    #@-others
#@+node:ekr.20110312162243.14260: ** class ContextSniffer
class ContextSniffer:

    """ Class to analyze surrounding context and guess class

    For simple dynamic code completion engines.
    """

    def __init__(self):

        self.vars = {}
            # Keys are var names; values are list of classes

    #@+others
    #@+node:ekr.20110312162243.14261: *3* get_classes
    def get_classes (self,s,varname):

        '''Return a list of classes for string s.'''

        self.push_declarations(s)

        aList = self.vars.get(varname,[])   

        return aList
    #@+node:ekr.20110312162243.14262: *3* set_small_context
    # def set_small_context(self, body):

        # """ Set immediate function """

        # self.push_declarations(body)
    #@+node:ekr.20110312162243.14263: *3* push_declarations & helper
    def push_declarations(self,s):

        for line in s.splitlines():
            line = line.lstrip()
            if line.startswith('#'):
                line = line.lstrip('#')
                parts = line.split(':')
                if len(parts) == 2:
                    a,b = parts
                    self.declare(a.strip(),b.strip())
    #@+node:ekr.20110312162243.14264: *4* declare
    def declare(self, var, klass):

        # g.trace(var,klass) # Very large trace.

        vars = self.vars.get(var, [])
        if not vars:
            self.vars[var] = vars

        vars.append(klass)
    #@-others
#@+node:ekr.20061031131434.74: ** class keyHandlerClass
class keyHandlerClass:

    '''A class to support emacs-style commands.'''

    #@+others
    #@+node:ekr.20061031131434.75: *3*  k.Birth
    #@+node:ekr.20061031131434.76: *4* k.__init__
    def __init__ (self,c):

        '''Create a key handler for c.'''

        trace = (False or g.trace_startup) and not g.unitTesting
        if trace: print('k.__init__')

        self.c = c
        self.dispatchEvent = None
        self.inited = False         # Set at end of finishCreate.
        self.swap_mac_keys = False  #### How to init this ????
        self.w = None
                # Note: will be None for nullGui.

        # Generalize...
        self.x_hasNumeric = ['sort-lines','sort-fields']

        self.altX_prompt = 'full-command: '

        # Access to data types defined in leoKeys.py
        self.KeyStroke = g.KeyStroke

        # Define all ivars...
        self.defineExternallyVisibleIvars()
        self.defineInternalIvars()
        self.defineSettingsIvars()

        if g.new_modes:
            self.modeController = ModeController(c)

        self.defineTkNames()
        self.defineSpecialKeys()
        self.defineSingleLineCommands()
        self.defineMultiLineCommands()
        self.autoCompleter = AutoCompleterClass(self)
        self.qcompleter = None # Set by AutoCompleter.start.

        self.setDefaultUnboundKeyAction()
        self.setDefaultEditingAction() # 2011/02/09
    #@+node:ekr.20061031131434.78: *4* k.defineExternallyVisibleIvars
    def defineExternallyVisibleIvars(self):

        self.abbrevOn = False
            # True: abbreviations are on.
        self.arg = ''
            # The value returned by k.getArg.
        self.argSelectedText = '' # The selected text in state 0.
        self.commandName = None # The name of the command being executed.
        self.funcReturn = None # For k.simulateCommand
        self.getArgEscape = None # A signal that the user escaped getArg in an unusual way.
        self.givenArgs = [] # New in Leo 4.4.8: arguments specified after the command name in k.simulateCommand.
        self.inputModeBindings = {}
        self.inputModeName = '' # The name of the input mode, or None.
        self.inverseCommandsDict = {}
            # Completed in k.finishCreate, but leoCommands.getPublicCommands adds entries first.
        self.modePrompt = '' # The mode promopt.
        self.negativeArg = False
        self.newMinibufferWidget = None # Usually the minibuffer restores focus.  This overrides this default.
        # self.regx = g.bunch(iter=None,key=None)
        self.repeatCount = None
        self.state = g.bunch(kind=None,n=None,handler=None)
    #@+node:ekr.20061031131434.79: *4* k.defineInternalIvars
    def defineInternalIvars(self):

        self.abbreviationsDict = {}
            # Abbreviations created by @alias nodes.

        # Previously defined bindings...
        self.bindingsDict = {}
            # Keys are Tk key names, values are lists of ShortcutInfo's.
        # Previously defined binding tags.
        self.bindtagsDict = {}
            # Keys are strings (the tag), values are 'True'
        self.masterBindingsDict = {}
            # Keys are scope names: 'all','text',etc. or mode names.
            # Values are dicts: keys are strokes, values are ShortcutInfo's.
        self.masterGuiBindingsDict = {}
            # Keys are strokes; value is True;

        # Special bindings for k.fullCommand...
        self.mb_copyKey = None
        self.mb_pasteKey = None
        self.mb_cutKey = None
        self.mb_help = False

        # Keys whose bindings are computed by initSpecialIvars...
        self.abortAllModesKey = None
        self.autoCompleteForceKey = None
        self.fullCommandKey = None
        self.universalArgKey = None

        # Keepting track of the characters in the mini-buffer...
        self.arg_completion = True
        self.mb_event = None
        self.mb_history = []
        self.mb_prefix = ''
        self.mb_tabListPrefix = ''
        self.mb_tabList = []
        self.mb_tabListIndex = -1
        self.mb_prompt = ''

        self.func = None
        self.previous = []
        self.stroke = None

        # For onIdleTime...
        self.idleCount = 0

        # For modes...
        self.afterGetArgState = None
        self.argTabList = []
        self.getArgEscapes = []
        self.modeBindingsDict = {}
        self.modeWidget = None
        self.silentMode = False
    #@+node:ekr.20080509064108.7: *4* k.defineMultiLineCommands
    def defineMultiLineCommands (self):

        k = self

        k.multiLineCommandList = [
            # editCommandsClass
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
            # keyHandlerCommandsClass
            'repeat-complex-command',
            # killBufferCommandsClass
            'backward-kill-sentence',
            'kill-sentence',
            'kill-region',
            'kill-region-save',
            # queryReplaceCommandsClass
            'query-replace',
            'query-replace-regex',
            # rectangleCommandsClass
            'clear-rectangle',
            'close-rectangle',
            'delete-rectangle',
            'kill-rectangle',
            'open-rectangle',
            'string-rectangle',
            'yank-rectangle',
            # registerCommandsClass
            'jump-to-register',
            'point-to-register',
            # searchCommandsClass
            'change',
            'change-then-find',
            'find-next',
            'find-prev',
        ]
    #@+node:ekr.20120217070122.10479: *4* k.defineSettingIvars
    def defineSettingsIvars(self):

        # Part 1: These were in the ctor.
        c = self.c
        getBool  = c.config.getBool
        getColor = c.config.getColor
        self.enable_autocompleter           = getBool('enable_autocompleter_initially')
        self.enable_calltips                = getBool('enable_calltips_initially')
        self.ignore_caps_lock               = getBool('ignore_caps_lock')
        self.ignore_unbound_non_ascii_keys  = getBool('ignore_unbound_non_ascii_keys')
        self.minibuffer_background_color    = getColor('minibuffer_background_color') or 'lightblue'
        self.minibuffer_foreground_color    = getColor('minibuffer_foreground_color') or 'black'
        self.minibuffer_warning_color       = getColor('minibuffer_warning_color') or 'lightgrey'
        self.minibuffer_error_color         = getColor('minibuffer_error_color') or 'red'
        self.swap_mac_keys                  = getBool('swap_mac_keys')

        self.warn_about_redefined_shortcuts = getBool('warn_about_redefined_shortcuts')
        # Has to be disabled (default) for AltGr support on Windows
        self.enable_alt_ctrl_bindings       = c.config.getBool('enable_alt_ctrl_bindings')

        # Part 2: These were in finishCreate.

        # Set mode colors used by k.setInputState.
        bg = c.config.getColor('body_text_background_color') or 'white'
        fg = c.config.getColor('body_text_foreground_color') or 'black'

        self.command_mode_bg_color    = getColor('command_mode_bg_color') or bg
        self.command_mode_fg_color    = getColor('command_mode_fg_color') or fg
        self.insert_mode_bg_color     = getColor('insert_mode_bg_color') or bg
        self.insert_mode_fg_color     = getColor('insert_mode_fg_color') or fg
        self.overwrite_mode_bg_color  = getColor('overwrite_mode_bg_color') or bg
        self.overwrite_mode_fg_color  = getColor('overwrite_mode_fg_color') or fg
        self.unselected_body_bg_color = getColor('unselected_body_bg_color') or bg
        self.unselected_body_fg_color = getColor('unselected_body_fg_color') or bg

        # g.trace(self.c.shortFileName())
    #@+node:ekr.20080509064108.6: *4* k.defineSingleLineCommands
    def defineSingleLineCommands (self):

        k = self

        # These commands can be executed in the minibuffer.
        k.singleLineCommandList = [
            # editCommandsClass
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
            # keyHandlerCommandsClass
            # 'auto-complete',
            'negative-argument',
            'number-command',
            'number-command-0',
            'number-command-1',
            'number-command-2',
            'number-command-3',
            'number-command-4',
            'number-command-5',
            'number-command-6',
            'number-command-7',
            'number-command-8',
            'universal-argument',
            # killBufferCommandsClass
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
            # macroCommandsClass
            'call-last-kbd-macro',
            # search commands
            # 'replace-string', # A special case so Shift-Ctrl-r will work after Ctrl-f.
            'set-find-everywhere',              # 2011/06/07
            'set-find-node-only',               # 2011/06/07
            'set-find-suboutline-only',         # 2011/06/07
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
            # registerCommandsClass
            'append-to-register',
            'copy-to-register',
            'insert-register',
            'prepend-to-register',
        ]
    #@+node:ekr.20070123085931: *4* k.defineSpecialKeys
    def defineSpecialKeys (self):

        '''Define k.guiBindNamesDict and k.guiBindNamesInverseDict.

        Important: all gui's use these dictionaries because bindings in
        leoSettings.leo use these representations.'''

        k = self

        # These are defined at http://tcl.activestate.com/man/tcl8.4/TkCmd/keysyms.htm.
        # Important: only the inverse dict is actually used in the new key binding scheme.
        # Tk may return the *values* of this dict in event.keysym fields.
        # Leo will warn if it gets a event whose keysym not in values of this table.
        k.guiBindNamesDict = {
            "&" : "ampersand",
            "^" : "asciicircum",
            "~" : "asciitilde",
            "*" : "asterisk",
            "@" : "at",
            "\\": "backslash",
            "|" : "bar",
            "{" : "braceleft",
            "}" : "braceright",
            "[" : "bracketleft",
            "]" : "bracketright",
            ":" : "colon",      # removed from code.
            "," : "comma",
            "$" : "dollar",
            "=" : "equal",
            "!" : "exclam",     # removed from code.
            ">" : "greater",
            "<" : "less",
            "-" : "minus",
            "#" : "numbersign",
            '"' : "quotedbl",
            "'" : "quoteright",
            "(" : "parenleft",
            ")" : "parenright", # removed from code.
            "%" : "percent",
            "." : "period",     # removed from code.
            "+" : "plus",
            "?" : "question",
            "`" : "quoteleft",
            ";" : "semicolon",
            "/" : "slash",
            " " : "space",      # removed from code.
            "_" : "underscore",
        }

        # No translation.
        for s in k.tkNamesList:
            k.guiBindNamesDict[s] = s

        # Create the inverse dict.
        k.guiBindNamesInverseDict = {}
        for key in k.guiBindNamesDict:
            k.guiBindNamesInverseDict [k.guiBindNamesDict.get(key)] = key
    #@+node:ekr.20070123143428: *4* k.defineTkNames
    def defineTkNames (self):

        k = self

        # These are the key names used in Leo's core *regardless* of the gui actually in effect.
        # The gui is responsible for translating gui-dependent keycodes into these values.
        k.tkNamesList = (
            # Arrow keys.
            'Left','Right','Up','Down',
            # Page up/down keys.
            'Next','Prior',
            # Home end keys.
            'Home','End'
            # Modifier keys.
            'Caps_Lock','Num_Lock',
            # F-keys.
            'F1','F2','F3','F4','F5','F6','F7','F8','F9','F10','F11','F12',
            # All others.
            'Begin','Break','Clear','Delete','Escape',
            # Dubious: these are ascii characters!
            # But there is no harm in retaining these in Leo's core.
            'BackSpace','Linefeed','Return','Tab',
        )

        # These keys settings that may be specied in leoSettings.leo.
        # Keys are lowercase, so that case is not significant *for these items only* in leoSettings.leo.
        k.settingsNameDict = {
            'bksp'    : 'BackSpace', # Dubious: should be '\b'
            'dnarrow' : 'Down',
            'esc'     : 'Escape',
            'ltarrow' : 'Left',
            'pageup'  : 'Prior',
            'pagedn'  : 'Next',
            'rtarrow' : 'Right',
            'uparrow' : 'Up',
        }

        # Add lowercase version of special keys.
        for s in k.tkNamesList:
            k.settingsNameDict [s.lower()] = s

    #@+at
    # The following are not translated, so what appears in the menu is the
    # same as what is passed to the gui. Case is significant. Note: the Tk
    # documentation states that not all of these may be available on all
    # platforms.
    # 
    # Num_Lock, Pause, Scroll_Lock, Sys_Req,
    # KP_Add, KP_Decimal, KP_Divide, KP_Enter, KP_Equal,
    # KP_Multiply, KP_Separator,KP_Space, KP_Subtract, KP_Tab,
    # KP_F1,KP_F2,KP_F3,KP_F4,
    # KP_0,KP_1,KP_2,KP_3,KP_4,KP_5,KP_6,KP_7,KP_8,KP_9,
    # Insert
    #@+node:ekr.20061031131434.80: *4* k.finishCreate & helpers
    def finishCreate (self):

        '''Complete the construction of the keyHandler class.
        c.commandsDict has been created when this is called.'''

        trace = (False or g.trace_startup) and not g.unitTesting
        if trace: print('k.finishCreate')

        k = self ; c = k.c
        self.w = c.frame.miniBufferWidget
            # Will be None for nullGui.

        k.createInverseCommandsDict()
        k.makeAllBindings()
        self.inited = True

        k.setDefaultInputState()
        k.resetLabel()
    #@+node:ekr.20061031131434.81: *5* createInverseCommandsDict
    def createInverseCommandsDict (self):

        '''Add entries to k.inverseCommandsDict using c.commandDict.

        c.commandsDict:        keys are command names, values are funcions f.
        k.inverseCommandsDict: keys are f.__name__, values are minibuffer command names.
        '''

        k = self ; c = k.c

        for name in c.commandsDict:
            f = c.commandsDict.get(name)
            try:
                k.inverseCommandsDict [f.__name__] = name
                # g.trace('%24s = %s' % (f.__name__,name))

            except Exception:
                g.es_exception()
                g.trace(repr(name),repr(f),g.callers())
    #@+node:ekr.20061101071425: *4* oops
    def oops (self):

        g.trace('Should be defined in subclass:',g.callers(4))
    #@+node:ekr.20110209093958.15413: *4* setDefaultEditingKeyAction (New)
    def setDefaultEditingAction (self):

        k = self ; c = k.c

        action = c.config.getString('default_editing_state') or 'insert'
        action.lower()

        if action not in ('command','insert','overwrite'):
            g.trace('ignoring default_editing_state: %s' % (action))
            action = 'insert'

        self.defaultEditingAction = action
    #@+node:ekr.20061031131434.82: *4* setDefaultUnboundKeyAction
    def setDefaultUnboundKeyAction (self,allowCommandState=True):

        k = self ; c = k.c

        # g.trace(g.callers())

        defaultAction = c.config.getString('top_level_unbound_key_action') or 'insert'
        defaultAction.lower()

        if defaultAction == 'command' and not allowCommandState:
            self.unboundKeyAction = 'insert'
        elif defaultAction in ('command','insert','overwrite'):
            self.unboundKeyAction = defaultAction
        else:
            g.trace('ignoring top_level_unbound_key_action setting: %s' % (defaultAction))
            self.unboundKeyAction = 'insert'

        # g.trace(self.unboundKeyAction)

        self.defaultUnboundKeyAction = self.unboundKeyAction

        k.setInputState(self.defaultUnboundKeyAction)
    #@+node:ekr.20061031131434.88: *3* k.Binding
    #@+node:ekr.20061031131434.89: *4* k.bindKey & helpers
    def bindKey (self,pane,shortcut,callback,commandName,modeFlag=False,tag=None):

        '''Bind the indicated shortcut (a Tk keystroke) to the callback.

        No actual gui bindings are made: only entries in k.masterBindingsDict.

        tag gives the source of the binding.

        '''

        trace = False and not g.unitTesting
        k = self
        if not k.check_bind_key(commandName,pane,shortcut):
            return False
        aList = k.bindingsDict.get(shortcut,[])
        if trace: #  or shortcut == 'Ctrl+q':
            g.trace('%7s %20s %17s %s' % (pane,shortcut,tag,commandName))
        try:
            if not shortcut:
                stroke = None
            elif g.isStroke(shortcut):
                stroke = shortcut
                assert stroke.s,stroke
            else:
                stroke = k.strokeFromSetting(shortcut)

            si = g.ShortcutInfo(kind=tag,pane=pane,
                func=callback,commandName=commandName,stroke=stroke)

            if shortcut: #####
                k.bindKeyToDict(pane,shortcut,si)
            if shortcut and not modeFlag:
                aList = k.remove_conflicting_definitions(
                    aList,commandName,pane,shortcut)
                # 2013/03/02: a real bug fix.
            aList.append(si)
            if shortcut:
                assert stroke
                k.bindingsDict [stroke] = aList
                if trace: g.trace(shortcut,aList)
            return True
        except Exception: # Could be a user error.
            if g.unitTesting or not g.app.menuWarningsGiven:
                g.es_print('exception binding',shortcut,'to',commandName)
                g.es_print_exception()
                g.app.menuWarningsGiven = True
            return False

    bindShortcut = bindKey # For compatibility
    #@+node:ekr.20120130074511.10228: *5* k.check_bind_key
    def check_bind_key(self,commandName,pane,shortcut):

         #k = self
        if not shortcut:
            return False
        assert g.isStroke(shortcut)

        # Give warning and return if we try to bind to Enter or Leave.
        for s in ('enter','leave'):
            if shortcut.lower().find(s) > -1:
                g.warning('ignoring invalid key binding:','%s = %s' % (
                    commandName,shortcut))
                return False
        if pane.endswith('-mode'):
            g.trace('oops: ignoring mode binding',shortcut,commandName,g.callers())
            return False
        else:
            return True
    #@+node:ekr.20120130074511.10227: *5* k.kill_one_shortcut
    def kill_one_shortcut (self,stroke):

        '''Update the dicts so that c.config.getShortcut(name) will return None
        for all names *presently* bound to the stroke.'''

        k = self ; c = k.c
        lm = g.app.loadManager
        # A crucial shortcut: inverting and uninverting dictionaries is slow.
        # Important: the comparison is valid regardless of the type of stroke.
        if stroke in (None,'None','none'):
            return
        assert g.isStroke(stroke),stroke
        d = c.config.shortcutsDict
        if d is None:
            d = g.TypedDictOfLists(
                name='empty shortcuts dict',
                keyType=type('commandName'),
                valType=g.ShortcutInfo)
        inv_d = lm.invert(d)
        # aList = inv_d.get(stroke,[])
        inv_d[stroke] = []
        c.config.shortcutsDict = lm.uninvert(inv_d)
    #@+node:ekr.20061031131434.92: *5* k.remove_conflicting_definitions
    def remove_conflicting_definitions (self,aList,commandName,pane,shortcut):

        trace = False and not g.unitTesting
        k = self
        result = []
        for si in aList:
            assert g.isShortcutInfo(si),si
            if pane in ('button','all',si.pane):
                if trace:
                    # This is too annoying to report here. See bug 951921.
                    g.es_print('c for %s in %s' % (
                        si.stroke,k.c.shortFileName()))
                    g.es_print('previous: %s new: %s' % (si.commandName,commandName))
                k.kill_one_shortcut(shortcut)
            else:
                result.append(si)
        return result
    #@+node:ekr.20061031131434.93: *5* k.bindKeyToDict
    def bindKeyToDict (self,pane,stroke,si):

        '''Update k.masterBindingsDict for the stroke.'''

        # New in Leo 4.4.1: Allow redefintions.
        k = self
        assert g.isStroke(stroke),stroke
        d = k.masterBindingsDict.get(pane,{})
        d[stroke] = si
        k.masterBindingsDict [pane] = d
    #@+node:ekr.20061031131434.94: *5* k.bindOpenWith
    def bindOpenWith (self,d):

        '''Register an open-with command.'''

        k = self ; c = k.c

        shortcut = d.get('shortcut')
        name = d.get('name')

        # g.trace(d)

        # The first parameter must be event, and it must default to None.
        def openWithCallback(event=None,c=c,d=d):
            return c.openWith(d=d)

        # Use k.registerCommand to set the shortcuts in the various binding dicts.
        commandName = 'open-with-%s' % name.lower()
        k.registerCommand(commandName,shortcut,openWithCallback,pane='all',verbose=False)
    #@+node:ekr.20061031131434.95: *4* k.checkBindings
    def checkBindings (self):

        '''Print warnings if commands do not have any @shortcut entry.
        The entry may be `None`, of course.'''

        k = self ; c = k.c

        if not c.config.getBool('warn_about_missing_settings'): return

        for name in sorted(c.commandsDict):
            abbrev = k.abbreviationsDict.get(name)
            key = c.frame.menu.canonicalizeMenuName(abbrev or name)
            key = key.replace('&','')
            if not c.config.exists(key,'shortcut'):
                if abbrev:
                    g.trace('No shortcut for abbrev %s -> %s = %s' % (
                        name,abbrev,key))
                else:
                    g.trace('No shortcut for %s = %s' % (name,key))
    #@+node:ekr.20061031131434.97: *4* k.completeAllBindings
    def completeAllBindings (self,w=None):

        '''New in 4.4b3: make an actual binding in *all* the standard places.

        The event will go to k.masterKeyHandler as always, so nothing really changes.
        except that k.masterKeyHandler will know the proper stroke.'''

        # g.trace(w)

        k = self
        for stroke in k.bindingsDict:
            assert g.isStroke(stroke),repr(stroke)
            k.makeMasterGuiBinding(stroke,w=w)
    #@+node:ekr.20061031131434.96: *4* k.completeAllBindingsForWidget
    def completeAllBindingsForWidget (self,w):
        
        '''Make all a master gui binding for widget w.'''

        k = self
        for stroke in k.bindingsDict:
            assert g.isStroke(stroke),repr(stroke)
            k.makeMasterGuiBinding(stroke,w=w)
    #@+node:ekr.20070218130238: *4* k.dumpMasterBindingsDict
    def dumpMasterBindingsDict (self):
        
        '''Dump k.masterBindingsDict.'''

        k = self ; d = k.masterBindingsDict

        g.pr('\nk.masterBindingsDict...\n')

        for key in sorted(d):
            g.pr(key, '-' * 40)
            d2 = d.get(key)
            for key2 in sorted(d2):
                si = d2.get(key2)
                assert g.isShortcutInfo(si),si
                g.pr('%20s %s' % (key2,si.commandName))
    #@+node:ekr.20061031131434.99: *4* k.initAbbrev & helper
    def initAbbrev (self):

        k = self ; c = k.c ; d = c.config.getAbbrevDict()
        if d:
            for key in d:
                commandName = d.get(key)
                if commandName.startswith('press-') and commandName.endswith('-button'):
                    pass # Must be done later in k.registerCommand.
                else:
                    self.initOneAbbrev(commandName,key)

    #@+node:ekr.20130924035029.12741: *5* k.initOneAbbrev
    def initOneAbbrev (self,commandName,key):
        
        '''Enter key as an abbreviation for commandName in c.commandsDict.'''

        c,k = self.c,self
        if c.commandsDict.get(key):
            g.trace('ignoring duplicate abbrev: %s',key)
        else:
            func = c.commandsDict.get(commandName)
            if func:
                # g.trace(key,commandName,func.__name__)
                c.commandsDict [key] = func
                # k.inverseCommandsDict[func.__name__] = key
            else:
                g.warning('bad abbrev:',key,'unknown command name:',commandName)
    #@+node:ekr.20061031131434.101: *4* k.initSpecialIvars
    def initSpecialIvars (self):

        '''Set ivars for special keystrokes from previously-existing bindings.'''

        k = self ; c = k.c
        trace = False or c.config.getBool('trace_bindings_verbose')
        warn  = c.config.getBool('warn_about_missing_settings')

        for ivar,commandName in (
            ('fullCommandKey',  'full-command'),
            ('abortAllModesKey','keyboard-quit'),
            ('universalArgKey', 'universal-argument'),
            ('autoCompleteForceKey','auto-complete-force'),
        ):
            junk, aList = c.config.getShortcut(commandName)
            aList,found = aList or [], False
            for pane in ('text','all'):
                for si in aList:
                    assert g.isShortcutInfo(si),si
                    if si.pane == pane:
                        if trace: g.trace(commandName,si.stroke)
                        setattr(k,ivar,si.stroke)
                        found = True; break
            if not found and warn:
                g.trace('no setting for %s' % commandName)
    #@+node:ekr.20061031131434.98: *4* k.makeAllBindings
    def makeAllBindings (self):
        
        '''Make all key bindings in all of Leo's panes.'''

        k = self ; c = k.c
        k.bindingsDict = {}
        if g.new_modes:
            k.modeController.addModeCommands()
        else:
            k.addModeCommands() 
        k.makeBindingsFromCommandsDict()
        k.initSpecialIvars()
        k.initAbbrev()
        k.completeAllBindings()
        k.checkBindings()
    #@+node:ekr.20061031131434.102: *4* k.makeBindingsFromCommandsDict & helper
    def makeBindingsFromCommandsDict (self):

        '''Add bindings for all entries in c.commandDict.'''

        trace = False and not g.unitTesting
        k = self ; c = k.c

        if trace:
            g.trace('makeBindingsFromCommandsDict entry')
            t1 = time.time()

        # Step 1: Create d2.
        # Keys are strokes. Values are lists of si with si.stroke == stroke.
        d = c.commandsDict
        d2 = g.TypedDictOfLists(
            name='makeBindingsFromCommandsDict helper dict',
            keyType=g.KeyStroke,valType=g.ShortcutInfo)

        for commandName in sorted(d.keys()):
            command = d.get(commandName)
            key, aList = c.config.getShortcut(commandName)
            for si in aList:
                assert isinstance(si,g.ShortcutInfo)
                # Important: si.stroke is already canonicalized.
                stroke = si.stroke
                si.commandName = commandName
                if stroke:
                    assert g.isStroke(stroke)
                    d2.add(stroke,si)

        # Step 2: make the bindings.
        if trace: t2 = time.time()

        for stroke in sorted(d2.keys()):
            aList2 = d2.get(stroke)
            for si in aList2:
                assert isinstance(si,g.ShortcutInfo)
                commandName = si.commandName
                command = c.commandsDict.get(commandName)
                tag = si.kind
                pane = si.pane
                if stroke and not pane.endswith('-mode'):
                    k.bindKey(pane,stroke,command,commandName,tag=tag)

        if trace:
            t3 = time.time()
            g.trace('%0.2fsec' % (t2-t1))
            g.trace('%0.2fsec' % (t3-t2))
    #@+node:ekr.20061031131434.103: *4* k.makeMasterGuiBinding
    def makeMasterGuiBinding (self,stroke,w=None):

        '''Make a master gui binding for stroke in pane w, or in all the standard widgets.'''

        k = self ; c = k.c ; f = c.frame
        if w:
            widgets = [w]
        else:
            # New in Leo 4.5: we *must* make the binding in the binding widget.
            bindingWidget = f.tree and hasattr(f.tree,'bindingWidget') and f.tree.bindingWidget or None
            bodyCtrl = f.body and hasattr(f.body,'bodyCtrl') and f.body.bodyCtrl or None
            canvas = f.tree and hasattr(f.tree,'canvas') and f.tree.canvas   or None
            widgets = (c.miniBufferWidget,bodyCtrl,canvas,bindingWidget)

        for w in widgets:
            if not w: continue
            # Make the binding only if no binding for the stroke exists in the widget.
            aList = k.masterGuiBindingsDict.get(stroke,[])
            if w not in aList:
                aList.append(w)
                k.masterGuiBindingsDict [stroke] = aList
    #@+node:ekr.20061031131434.104: *3* k.Dispatching
    #@+node:ekr.20061031131434.111: *4* fullCommand (alt-x) & helper
    def fullCommand (self,event,specialStroke=None,specialFunc=None,help=False,helpHandler=None):

        '''Handle 'full-command' (alt-x) mode.'''

        trace = False and not g.unitTesting
        verbose = True
        k = self ; c = k.c
        recording = c.macroCommands.recordingMacro
        state = k.getState('full-command')
        helpPrompt = 'Help for command: '
        c.check_event(event)
        ch = char = event and event.char or ''
        stroke = event and event.stroke or None
        if trace: g.trace('recording',recording,'state',state,char)
        if recording:
            c.macroCommands.startRecordingMacro(event)
        if state > 0:
            k.setLossage(char,stroke)
        if state == 0:
            k.mb_event = event # Save the full event for later.
            k.setState('full-command',1,handler=k.fullCommand)
            prompt = g.choose(help,helpPrompt,k.altX_prompt)
            k.setLabelBlue('%s' % (prompt),protect=True)
            # Init mb_ ivars. This prevents problems with an initial backspace.
            k.mb_prompt = k.mb_tabListPrefix = k.mb_prefix = prompt
            k.mb_tabList = [] ; k.mb_tabListIndex = -1
            k.mb_help = help
            k.mb_helpHandler = helpHandler
            c.minibufferWantsFocus()
        elif char == 'Ins' or k.isFKey(char):
            pass
        elif char == 'Escape':
            k.keyboardQuit()
        elif char in ('\n','Return'):
            if trace and verbose: g.trace('***Return')
            c.frame.log.deleteTab('Completion')
            if k.mb_help:
                s = k.getLabel()
                commandName = s[len(helpPrompt):].strip()
                k.clearState()
                k.resetLabel()
                if k.mb_helpHandler: k.mb_helpHandler(commandName)
            else:
                k.callAltXFunction(k.mb_event)
        elif char in ('\t','Tab'):
            if trace and verbose: g.trace('***Tab')
            k.doTabCompletion(list(c.commandsDict.keys()),allow_empty_completion=True)
            c.minibufferWantsFocus()
        elif char in ('\b','BackSpace'):
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
    #@+node:ekr.20061031131434.112: *5* callAltXFunction
    def callAltXFunction (self,event):

        trace = False and not g.unitTesting
        k = self ; c = k.c ; s = k.getLabel()
        k.mb_tabList = []
        commandName = s[len(k.mb_prefix):].strip()
        func = c.commandsDict.get(commandName)
        k.newMinibufferWidget = None

        # g.trace(func and func.__name__,'mb_event',event and event.widget.widgetName)
        if func:
            # These must be done *after* getting the command.
            k.clearState()
            k.resetLabel()
            if commandName != 'repeat-complex-command':
                k.mb_history.insert(0,commandName)
            w = event and event.widget
            if hasattr(w,'permanent') and not w.permanent:
                g.es('Can not execute commands from headlines')
            else:
                c.widgetWantsFocusNow(event and event.widget) # Important, so cut-text works, e.g.
                func(event)
            k.endCommand(commandName)
        else:
            if 1: # Useful.
                if trace: g.trace('*** tab completion')
                k.doTabCompletion(list(c.commandsDict.keys()))
            else: # Annoying.
                k.keyboardQuit()
                k.setLabel('Command does not exist: %s' % commandName)
                c.bodyWantsFocus()
    #@+node:ekr.20061031131434.113: *4* k.endCommand
    def endCommand (self,commandName):

        '''Make sure Leo updates the widget following a command.

        Never changes the minibuffer label: individual commands must do that.
        '''

        k = self ; c = k.c
        # The command may have closed the window.
        if g.app.quitting or not c.exists: return

        # Set the best possible undoType: prefer explicit commandName to k.commandName.
        commandName = commandName or k.commandName or ''
        k.commandName = k.commandName or commandName or ''
        if commandName:
            if not k.inState():
                k.commandName = None
                c.editCommandsManager.initAllEditCommanders()
            if 0: # Do *not* call this by default.  It interferes with undo.
                c.frame.body.onBodyChanged(undoType='Typing')
            if k.newMinibufferWidget:
                c.widgetWantsFocusNow(k.newMinibufferWidget)
                # g.pr('endCommand', g.app.gui.widget_name(k.newMinibufferWidget),g.callers())
                k.newMinibufferWidget = None
    #@+node:ekr.20061031131434.114: *3* k.Externally visible commands
    #@+node:ekr.20061031131434.115: *4* digitArgument & universalArgument
    def universalArgument (self,event):

        '''Prompt for a universal argument.'''
        k = self
        k.setLabelBlue('Universal Argument: ',protect=True)
        k.universalDispatcher(event)

    def digitArgument (self,event):

        '''Prompt for a digit argument.'''
        k = self
        k.setLabelBlue('Digit Argument: ',protect=True)
        k.universalDispatcher(event)
    #@+node:ekr.20070613133500: *4* k.menuCommandKey
    def menuCommandKey (self,event=None):

        # This method must exist, but it never gets called.
        pass 
    #@+node:ekr.20061031131434.117: *4* negativeArgument (redo?)
    def negativeArgument (self,event):

        '''Prompt for a negative digit argument.'''

        g.trace('not ready yet')

        # k = self ; state = k.getState('neg-arg')

        # if state == 0:
            # k.setLabelBlue('Negative Argument: ',protect=True)
            # k.setState('neg-arg',1,k.negativeArgument)
        # else:
            # k.clearState()
            # k.resetLabel()
            # func = k.negArgFunctions.get(k.stroke)
            # if func:
                # func(event)
    #@+node:ekr.20061031131434.118: *4* numberCommand
    def numberCommand (self,event,stroke,number):

        '''Enter a number prefix for commands.'''

        k = self ; c = self.c
        k.stroke = stroke
        w = event and event.widget
        k.universalDispatcher(event)
        g.app.gui.event_generate(c,chr(number),chr(number),w)
        return

    def numberCommand0 (self,event):
        '''Execute command number 0.'''
        return self.numberCommand (event,None,0)

    def numberCommand1 (self,event):
        '''Execute command number 1.'''
        return self.numberCommand (event,None,1)

    def numberCommand2 (self,event):
        '''Execute command number 2.'''
        return self.numberCommand (event,None,2)

    def numberCommand3 (self,event):
        '''Execute command number 3.'''
        return self.numberCommand (event,None,3)

    def numberCommand4 (self,event):
        '''Execute command number 4.'''
        return self.numberCommand (event,None,4)

    def numberCommand5 (self,event):
        '''Execute command number 5.'''
        return self.numberCommand (event,None,5)

    def numberCommand6 (self,event):
        '''Execute command number 6.'''
        return self.numberCommand (event,None,6)

    def numberCommand7 (self,event):
        '''Execute command number 7.'''
        return self.numberCommand (event,None,7)

    def numberCommand8 (self,event):
        '''Execute command number 8.'''
        return self.numberCommand (event,None,8)

    def numberCommand9 (self,event):
        '''Execute command number 9.'''
        return self.numberCommand (event,None,9)
    #@+node:ekr.20061031131434.119: *4* k.printBindings & helper
    def printBindings (self,event=None):

        '''Print all the bindings presently in effect.'''

        k = self ; c = k.c
        d = k.bindingsDict ; tabName = 'Bindings'
        c.frame.log.clearTab(tabName)
        legend = '''\
    legend:
    [ ] leoSettings.leo
    [D] default binding
    [F] loaded .leo File
    [M] myLeoSettings.leo
    [@] mode

    '''

        if not d: return g.es('no bindings')
        legend = g.adjustTripleString(legend,c.tab_width)
        data = []
        for stroke in sorted(d):
            assert g.isStroke(stroke),stroke
            aList = d.get(stroke,[])
            for si in aList:
                assert g.isShortcutInfo(si),si
                s1 = '' if si.pane=='all' else si.pane
                s2 = k.prettyPrintKey(stroke)
                s3 = si.commandName
                s4 = si.kind or '<no hash>'
                data.append((s1,s2,s3,s4),)

        # Print keys by type:
        result = []
        result.append('\n'+legend)
        for prefix in (
            'Alt+Ctrl+Shift','Alt+Ctrl','Alt+Shift','Alt', # 'Alt+Key': done by Alt.
            'Ctrl+Meta+Shift','Ctrl+Meta','Ctrl+Shift','Ctrl', # Ctrl+Key: done by Ctrl.
            'Meta+Key','Meta+Shift','Meta',
            'Shift',
            # Careful: longer prefixes must come before shorter prefixes.
        ):
            data2 = []
            for item in data:
                s1,s2,s3,s4 = item
                if s2.startswith(prefix):
                    data2.append(item)
            result.append('***** %s...\n' % prefix)
            self.printBindingsHelper(result,data2,prefix=prefix)
            # Remove all the items in data2 from data.
            # This must be done outside the iterator on data.
            for item in data2:
                data.remove(item)
        # Print all plain bindings.
        result.append('***** Plain Keys...\n')
        self.printBindingsHelper(result,data,prefix=None)
        if not g.unitTesting:
            g.es('',''.join(result),tabName=tabName)
        k.showStateAndMode()
        return result # for unit test.
    #@+node:ekr.20061031131434.120: *5* printBindingsHelper
    def printBindingsHelper (self,result,data,prefix):

        lm = g.app.loadManager

        data.sort(key=lambda x: x[1])

        data2,n = [],0
        for pane,key,commandName,kind in data:
            key = key.replace('+Key','')
            # g.trace(key,kind)
            letter = lm.computeBindingLetter(kind)
            pane = '%s: ' % (pane) if pane else ''
            left = pane+key # pane and shortcut fields
            n = max(n,len(left))
            data2.append((letter,left,commandName),)

        for z in data2:
            letter,left,commandName = z
            result.append('%s %*s %s\n' % (letter,-n,left,commandName))

        if data:
            result.append('\n')
    #@+node:ekr.20120520174745.9867: *4* k.printButtons
    def printButtons (self,event=None):

        '''Print all @button and @command commands, their bindings and their source.'''

        k = self ; c = k.c
        tabName = '@buttons && @commands'
        c.frame.log.clearTab(tabName)

        def put(s):
            g.es('',s,tabName=tabName)

        data = []
        for aList in [c.config.getButtons(),c.config.getCommands()]:
            for z in aList:
                p,script = z
                c = p.v.context
                tag = 'M' if c.shortFileName().endswith('myLeoSettings.leo') else 'G'
                data.append((p.h,tag),)

        for aList in [g.app.config.atLocalButtonsList,g.app.config.atLocalCommandsList]:
            for p in aList:
                data.append((p.h,'L'),)

        result = ['%s %s' % (z[1],z[0]) for z in sorted(data)]
        put('\n'.join(result))

        legend = '''\

    legend:
    G leoSettings.leo
    L local .leo File
    M myLeoSettings.leo
    '''
        legend = g.adjustTripleString(legend,c.tab_width)
        put(''.join(legend))
    #@+node:ekr.20061031131434.121: *4* k.printCommands
    def printCommands (self,event=None):

        '''Print all the known commands and their bindings, if any.'''

        k = self ; c = k.c ; tabName = 'Commands'

        c.frame.log.clearTab(tabName)

        inverseBindingDict = k.computeInverseBindingDict()
        data,n = [],0
        for commandName in sorted(c.commandsDict):
            dataList = inverseBindingDict.get(commandName,[('',''),])
            for z in dataList:
                pane, key = z
                pane = '%s ' % (pane) if pane != 'all:' else ''
                key = k.prettyPrintKey(key).replace('+Key','')
                s1 = pane + key
                s2 = commandName
                n = max(n,len(s1))
                data.append((s1,s2),)

        # This isn't perfect in variable-width fonts.
        lines = ['%*s %s\n' % (-n,s1,s2) for s1,s2 in data]
        g.es('',''.join(lines),tabName=tabName)
    #@+node:ekr.20061031131434.122: *4* k.repeatComplexCommand & helper
    def repeatComplexCommand (self,event):

        '''Repeat the previously executed minibuffer command.'''
        k = self
        if k.mb_history:
            k.setState('last-full-command',1,handler=k.repeatComplexCommandHelper)
            k.setLabelBlue("Redo: %s" % str(k.mb_history[0]))
        else:
            g.warning('no previous command')

    #@+node:ekr.20131017100903.16689: *5* repeatComplexCommandHelper
    def repeatComplexCommandHelper (self,event):

        k = self ; c = k.c
        char = event and event.char or ''
        if char in ('\n','Return') and k.mb_history:
            last = k.mb_history [0]
            k.resetLabel()
            k.clearState() # Bug fix.
            c.commandsDict [last](event)
        else:
            # g.trace('oops')
            return k.keyboardQuit()
    #@+node:ekr.20061031131434.123: *4* set-xxx-State
    def setCommandState (self,event):
        '''Enter the 'command' editing state.'''
        # g.trace(g.callers())
        k = self
        k.setInputState('command',set_border=True)
        # This command is also valid in headlines.
        # k.c.bodyWantsFocus()
        k.showStateAndMode()

    def setInsertState (self,event):
        '''Enter the 'insert' editing state.'''
        # g.trace(g.callers())
        k = self
        k.setInputState('insert',set_border=True)
        # This command is also valid in headlines.
        # k.c.bodyWantsFocus()
        k.showStateAndMode()

    def setOverwriteState (self,event):
        '''Enter the 'overwrite' editing state.'''
        # g.trace(g.callers())
        k = self
        k.setInputState('overwrite',set_border=True)
        # This command is also valid in headlines.
        # k.c.bodyWantsFocus()
        k.showStateAndMode()
    #@+node:ekr.20061031131434.124: *4* toggle-input-state
    def toggleInputState (self,event=None):

        '''The toggle-input-state command.'''

        k = self ; c = k.c
        default = c.config.getString('top_level_unbound_key_action') or 'insert'
        state = k.unboundKeyAction

        if default == 'insert':
            state = g.choose(state=='insert','command','insert')
        elif default == 'overwrite':
            state = g.choose(state=='overwrite','command','overwrite')
        else:
            state = g.choose(state=='command','insert','command') # prefer insert to overwrite.

        k.setInputState(state)
        k.showStateAndMode()
    #@+node:ekr.20061031131434.125: *3* k.Externally visible helpers
    #@+node:ekr.20061031131434.128: *4* k.getArg
    def getArg (self,event,
        returnKind=None,returnState=None,handler=None,
        prefix=None,tabList=[],completion=True,oneCharacter=False,
        stroke=None, # New in 4.4.1.
        useMinibuffer=True # New in 4.4.1
    ):

        '''Accumulate an argument until the user hits return (or control-g).
        Enter the given return state when done.
        The prefix does not form the arg.  The prefix defaults to the k.getLabel().
        '''

        k = self ; c = k.c
        trace = False and not g.app.unitTesting
        state = k.getState('getArg')
        c.check_event(event)

        # 2011/06/06: remember these events also.
        if c.macroCommands.recordingMacro and state > 0:
            c.macroCommands.startRecordingMacro(event)

        char = event and event.char or ''
        if state > 0:
            k.setLossage(char,stroke)
        if trace: g.trace(
            'state',state,'char',repr(char),'stroke',repr(stroke),
            'isPlain',k.isPlainKey(stroke),
            'escapes',k.getArgEscapes,
            'completion',state==0 and completion or state!=0 and k.arg_completion)
        if state == 0:
            k.arg = ''
            #@+<< init altX vars >>
            #@+node:ekr.20061031131434.129: *5* << init altX vars >>
            k.argSelectedText = c.frame.body.bodyCtrl.getSelectedText()
                # 2010/09/01: remember the selected text for abbreviations.
            k.argTabList = tabList and tabList[:] or []
            k.arg_completion = completion
            # g.trace('completion',completion,'tabList',tabList)

            k.mb_prefix = prefix or k.getLabel()
            k.mb_prompt = prefix or ''
            k.mb_tabList = []

            # Clear the list: any non-tab indicates that a new prefix is in effect.
            k.mb_tabListPrefix = k.getLabel()
            k.oneCharacterArg = oneCharacter
            #@-<< init altX vars >>
            # Set the states.
            bodyCtrl = c.frame.body.bodyCtrl
            c.widgetWantsFocus(bodyCtrl)
            k.afterGetArgState=returnKind,returnState,handler
            k.setState('getArg',1,k.getArg)
            k.afterArgWidget = event and event.widget or c.frame.body.bodyCtrl
            if useMinibuffer: c.minibufferWantsFocus()
        elif char == 'Escape':
            k.keyboardQuit()
        elif char in ('\n','Return',) or k.oneCharacterArg or (stroke and stroke in k.getArgEscapes):
            if stroke and stroke in k.getArgEscapes:
                k.getArgEscape = stroke
            if k.oneCharacterArg:
                k.arg = char ##
            else:
                k.arg = k.getLabel(ignorePrompt=True)
            kind,n,handler = k.afterGetArgState
            if kind: k.setState(kind,n,handler)
            c.frame.log.deleteTab('Completion')
            if trace: g.trace('kind',kind,'n',n,'handler',handler and handler.__name__)
            if handler: handler(event)
        elif char in('\t','Tab'):
            k.doTabCompletion(k.argTabList,k.arg_completion)
        elif char in ('\b','BackSpace'):
            k.doBackSpace(k.argTabList,k.arg_completion)
            c.minibufferWantsFocus()
        elif k.isFKey(stroke):
            pass
            # 2011/03/01: ignore F-keys. Ignoring all except plain keys would kill unicode searches.
        else:
            # Clear the list, any other character besides tab indicates that a new prefix is in effect.
            k.mb_tabList = []
            k.updateLabel(event)
            k.mb_tabListPrefix = k.getLabel()
    #@+node:ekr.20061031131434.130: *4* k.keyboardQuit
    def keyboardQuit (self,event=None,setFocus=True,mouseClick=False):

        '''This method clears the state and the minibuffer label.

        k.endCommand handles all other end-of-command chores.'''

        trace = False and not g.unitTesting
        k = self ; c = k.c
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
        # This was what caused the unwanted scrolling.
        k.showStateAndMode(setFocus=setFocus)
    #@+node:ekr.20061031131434.126: *4* k.manufactureKeyPressForCommandName (changed)
    def manufactureKeyPressForCommandName (self,w,commandName):

        '''Implement a command by passing a keypress to the gui.'''

        trace = False and not g.unitTesting
        k = self ; c = k.c

        stroke = k.getShortcutForCommandName(commandName)
        if not stroke:
            shortcut = None
        elif g.isStroke(stroke):
            shortcut = stroke.s
        else:
            stroke = k.strokeFromSetting(stroke)
            shortcut = stroke.s

        assert g.isString(shortcut)

        if trace and shortcut: g.trace(
            'shortcut',repr(shortcut),'commandName',commandName)

        if shortcut and w:
            # g.trace(stroke)
            g.app.gui.set_focus(c,w)
            g.app.gui.event_generate(c,None,shortcut,w)
        else:
            message = 'no shortcut for %s' % (commandName)
            if g.app.unitTesting:
                raise AttributeError(message)
            else:
                g.error(message)
    #@+node:ekr.20071212104050: *4* k.overrideCommand
    def overrideCommand (self,commandName,func):

        # Override entries in c.k.masterBindingsDict
        k = self
        d = k.masterBindingsDict
        for key in d:
            d2 = d.get(key)
            for key2 in d2:
                si = d2.get(key2)
                assert g.isShortcutInfo(si),si
                if si.commandName == commandName:
                    si.func=func
                    d2[key2] = si
    #@+node:ekr.20061031131434.131: *4* k.registerCommand
    def registerCommand (self,commandName,shortcut,func,
        pane='all',verbose=False, wrap=True):

        '''Make the function available as a minibuffer command,
        and optionally attempt to bind a shortcut.

        You can wrap any method in a callback function, so the
        restriction to functions is not significant.

        If wrap is True then func will be wrapped with c.universalCallback.

        '''

        trace = False and not g.unitTesting ; verbose = False
        k = self ; c = k.c

        if trace: g.trace(commandName,shortcut)

        if wrap:
            func = c.universalCallback(func)
        f = c.commandsDict.get(commandName)

        if f and f.__name__ != 'dummyCallback' and trace and verbose:
            g.error('redefining',commandName)

        assert not g.isStroke(shortcut)

        c.commandsDict [commandName] = func
        fname = func.__name__
        k.inverseCommandsDict [fname] = commandName
        if trace and fname != 'minibufferCallback':
            g.trace('leoCommands %24s = %s' % (fname,commandName))

        if shortcut:
            if trace: g.trace('shortcut',shortcut)
            stroke = k.strokeFromSetting(shortcut)
        elif commandName.lower() == 'shortcut': # Causes problems.
            stroke = None
        else:
            # Try to get a stroke from leoSettings.leo.
            stroke = None
            junk,aList = c.config.getShortcut(commandName)
            for si in aList:
                assert g.isShortcutInfo(si),si
                assert g.isStrokeOrNone(si.stroke)
                if si.stroke and not si.pane.endswith('-mode'):
                    # if trace: g.trace('*** found',si)
                    stroke = si.stroke
                    break

        if stroke:
            if trace: g.trace('stroke',stroke,'pane',pane,commandName)
            ok = k.bindKey (pane,stroke,func,commandName,tag='register-command') # Must be a stroke.
            k.makeMasterGuiBinding(stroke) # Must be a stroke.
            if trace and verbose and ok and not g.app.silentMode:
                g.blue('','@command: %s = %s' % (
                    commandName,k.prettyPrintKey(stroke)))
                if 0:
                    d = k.masterBindingsDict.get('button',{})
                    g.print_dict(d)
        elif trace and verbose and not g.app.silentMode:
            g.blue('','@command: %s' % (commandName))

        # Fixup any previous abbreviation to press-x-button commands.
        if commandName.startswith('press-') and commandName.endswith('-button'):
            d = c.config.getAbbrevDict()
                # Keys are full command names, values are abbreviations.
            if commandName in list(d.values()):
                for key in d:
                    if d.get(key) == commandName:
                        c.commandsDict [key] = c.commandsDict.get(commandName)
                        break
    #@+node:ekr.20061031131434.127: *4* k.simulateCommand
    def simulateCommand (self,commandName):

        k = self ; c = k.c

        commandName = commandName.strip()
        if not commandName: return

        aList = commandName.split(None)
        if len(aList) == 1:
            k.givenArgs = []
        else:
            commandName = aList[0]
            k.givenArgs = aList[1:]

        # g.trace(commandName,k.givenArgs)
        func = c.commandsDict.get(commandName)

        if func:
            # g.trace(commandName,func.__name__)
            if commandName.startswith('specialCallback'):
                event = None # A legacy function.
            else: # Create a dummy event as a signal.
                event = g.app.gui.create_key_event(c,None,None,None)

            k.masterCommand(event=event,func=func)
            if c.exists:
                return k.funcReturn
            else:
                return None
        else:
            if g.app.unitTesting:
                raise AttributeError
            else:
                g.error('simulateCommand: no command for %s' % (commandName))
                return None
    #@+node:ekr.20061031131434.145: *3* k.Master event handlers
    #@+node:ekr.20061031131434.105: *4* k.masterCommand & helpers
    def masterCommand (self,commandName=None,event=None,func=None,stroke=None):

        '''This is the central dispatching method.
        All commands and keystrokes pass through here.
        This returns None, but may set k.funcReturn.
        '''

        k = self ; c = k.c
        trace = (False or g.trace_masterCommand) and not g.unitTesting
        traceGC = False
        if traceGC: g.printNewObjects('masterCom 1')
        if event: c.check_event(event)
        c.setLog()
        c.startRedrawCount = c.frame.tree.redrawCount
        k.stroke = stroke # Set this global for general use.
        char = ch = event and event.char or ''
        # 2011/10/28: compute func if not given.
        if commandName and not func:
            func = c.commandsDict.get(commandName)
        # Important: it is *not* an error for func to be None.
        k.func = func
        commandName = commandName or func and func.__name__ or '<no function>'
        k.funcReturn = None # For unit testing.
        #@+<< define specialKeysyms >>
        #@+node:ekr.20061031131434.106: *5* << define specialKeysyms >>
        specialKeysyms = (
            'Alt_L','Alt_R',
            'Meta_L','Meta_R', # Meta support.
            'Caps_Lock','Control_L','Control_R',
            'Num_Lock',
            'Shift_L','Shift_R',
        )
        #@-<< define specialKeysyms >>
        special = char in specialKeysyms
        inserted = not special
        if trace: # Useful.
            g.trace('stroke: %s ch: %s func: %s' % (
                stroke,repr(ch),func and func.__name__))
        if inserted:
            k.setLossage(ch,stroke)
        # We *must not* interfere with the global state in the macro class.
        if c.macroCommands.recordingMacro:
            c.macroCommands.startRecordingMacro(event)
            # 2011/06/06: Show the key, if possible.
        if k.abortAllModesKey and stroke == k.abortAllModesKey: # 'Control-g'
            k.keyboardQuit()
            k.endCommand(commandName)
            return
        if special: # Don't pass these on.
            return
        # if k.regx.iter:
            # try:
                # k.regXKey = char
                # k.regx.iter.next() # EKR: next() may throw StopIteration.
            # except StopIteration:
                # pass
            # return
        if k.abbrevOn:
            expanded = c.abbrevCommands.expandAbbrev(event,stroke)
            if expanded: return
        if func: # Func is an argument.
            if commandName.startswith('specialCallback'):
                # The callback function will call c.doCommand
                if trace: g.trace('calling specialCallback for',commandName)
                # if commandName != 'repeat-complex-command': # 2010/01/11
                    # k.mb_history.insert(0,commandName)
                val = func(event)
                # k.simulateCommand uses k.funcReturn.
                k.funcReturn = k.funcReturn or val # For unit tests.
            else:
                # Call c.doCommand directly
                if trace: g.trace('calling command directly',commandName)
                c.doCommand(func,commandName,event=event)
            if c.exists:
                k.endCommand(commandName)
                c.frame.updateStatusLine()
            if traceGC: g.printNewObjects('masterCom 2')
        elif k.inState():
            pass #Ignore unbound keys in a state.
        else:
            if traceGC: g.printNewObjects('masterCom 3')
            k.handleDefaultChar(event,stroke)
            if c.exists:
                c.frame.updateStatusLine()
            if traceGC: g.printNewObjects('masterCom 4')
    #@+node:ekr.20061031131434.110: *5* k.handleDefaultChar
    def handleDefaultChar(self,event,stroke):

        k = self ; c = k.c
        w = event and event.widget
        name = c.widget_name(w)
        trace = False and not g.unitTesting
        verbose = False
        if trace and verbose:
            g.trace('widget_name',name,'stroke',stroke,
            'enable alt-ctrl',self.enable_alt_ctrl_bindings)
        if (stroke and
            not stroke.startswith('Alt+Ctrl') and
            # not k.enable_alt_ctrl_bindings and # Old code: this isn't an alt-ctrl key!
            k.ignore_unbound_non_ascii_keys and # Bug fix: 2011/11/23
            (stroke.find('Ctrl') > -1 or stroke.find('Alt') > -1)
        ):
            if trace: g.trace('*** ignoring unbound ctrl/alt key:',stroke)
            g.app.unitTestDict['handleUnboundChar-ignore-alt-or-ctrl'] = True
        elif name.startswith('body'):
            action = k.unboundKeyAction
            if action in ('insert','overwrite'):
                c.editCommands.selfInsertCommand(event,action=action)
            else: # Ignore the key
                if trace: g.trace('ignoring',stroke)
        elif name.startswith('head'):
            c.frame.tree.onHeadlineKey(event)
        elif name.startswith('canvas'):
            if not stroke: # Not exactly right, but it seems to be good enough.
                c.onCanvasKey(event) # New in Leo 4.4.2
        elif name.startswith('log'):
            # Bug fix: 2011/11/21: Because of universal bindings
            # we may not be able to insert anything into w.
            import leo.core.leoFrame as leoFrame
            if issubclass(w.__class__,leoFrame.HighLevelInterface):
                i = w.logCtrl.getInsertPoint()
                if not stroke:
                    stroke = event and event.stroke
                if stroke:
                    s = stroke.toGuiChar()
                    w.logCtrl.insert(i,s)
            elif trace: g.trace('Not a HighLevelInterface object',w)
        else:
            pass # Ignore the event
    #@+node:ekr.20061031131434.146: *4* k.masterKeyHandler & helpers
    master_key_count = 0

    def masterKeyHandler (self,event):

        '''This is the handler for almost all key bindings.'''

        trace = (False or g.trace_masterKeyHandler) and not g.app.unitTesting
        traceGC = g.trace_masterKeyHandlerGC and not g.app.unitTesting
        verbose = False
        k,c = self,self.c
        c.check_event(event)
        #@+<< define vars >>
        #@+node:ekr.20061031131434.147: *5* << define vars >>
        w = event and event.widget
        char = event and event.char or ''
        stroke = event and event.stroke or None
        # w_name = c.widget_name(w)
        state = k.state.kind
        special_keys = (
            'Alt_L','Alt_R',
            'Caps_Lock','Control_L','Control_R',
            'Meta_L','Meta_R', # Meta support.
            'Num_Lock',
            'Shift_L','Shift_R',
            'Win_L','Win_R',
        )

        self.master_key_count += 1
        isPlain =  k.isPlainKey(stroke)
        #@-<< define vars >>
        assert g.isStrokeOrNone(stroke)
        if char in special_keys:
            if trace and verbose: g.trace('char',char)
            return None

        if traceGC: g.printNewObjects('masterKey 1')
        if trace and verbose: g.trace('stroke:',repr(stroke),'char:',
            repr(event and event.char),
            'ch:',repr(event and event.char),
            'state',state,'state2',k.unboundKeyAction)

        # Handle keyboard-quit first.
        if k.abortAllModesKey and stroke == k.abortAllModesKey:
            if hasattr(c,'screenCastController') and c.screenCastController:
                c.screenCastController.quit()
            if c.macroCommands.recordingMacro:
                c.macroCommands.endMacro()
            else:
                k.masterCommand(commandName='keyboard-quit',
                    event=event,func=k.keyboardQuit,stroke=stroke)
            return
        if k.inState():
            if trace: g.trace('   state %-15s %s' % (state,stroke))
            done = k.doMode(event,state,stroke)
            if done: return

        if traceGC: g.printNewObjects('masterKey 2')

        # 2011/02/08: An important simplification.
        if isPlain and k.unboundKeyAction != 'command':
            if self.isAutoCompleteChar(stroke):
                if trace: g.trace('autocomplete key',stroke)
            else:
                if trace: g.trace('inserted %-10s (insert/overwrite mode)' % (stroke))
                k.handleUnboundKeys(event,char,stroke)
                return

        # 2011/02/08: Use getPandBindings for *all* keys.
        si = k.getPaneBinding(stroke,w)
        if si:
            assert g.isShortcutInfo(si),si
            if traceGC: g.printNewObjects('masterKey 3')
            if trace: g.trace('   bound',stroke,si.func.__name__)
            k.masterCommand(event=event,
                commandName=si.commandName,func=si.func,stroke=si.stroke)
        else:
            if traceGC: g.printNewObjects('masterKey 4')
            if trace: g.trace(' unbound',stroke)
            k.handleUnboundKeys(event,char,stroke)
    #@+node:ekr.20061031131434.108: *5* callStateFunction
    def callStateFunction (self,event):

        trace = False and not g.unitTesting
        k = self ; val = None 
        ch = event and event.char or ''
        stroke = event and event.stroke or ''

        if trace: g.trace(k.state.kind,'ch',ch,'stroke',stroke,
            'ignore_unbound_non_ascii_keys',k.ignore_unbound_non_ascii_keys)

        if k.state.kind == 'auto-complete':
            # 2011/06/17.
            # k.auto_completer_state_handler returns 'do-standard-keys' for control keys.
            val = k.state.handler(event)
            if trace: g.trace('auto-complete returns',repr(val))
            return val
        elif k.state.kind:
            if (
                k.ignore_unbound_non_ascii_keys and
                len(ch) == 1 and # 2011/04/01
                ch and ch not in ('\b','\n','\r','\t') and
                (ord(ch) < 32 or ord(ch) > 128)
            ):
                # g.trace('non-ascii',ord(ch))
                pass
            elif k.state.handler:
                val = k.state.handler(event)
                if val != 'continue':
                    k.endCommand(k.commandName)
            else:
                g.error('callStateFunction: no state function for',k.state.kind)

        return val
    #@+node:ekr.20091230094319.6244: *5* doMode
    def doMode (self,event,state,stroke):

        trace = False and not g.unitTesting
        k = self

        # First, honor minibuffer bindings for all except user modes.
        if state in ('getArg','getFileName','full-command','auto-complete'):
            if k.handleMiniBindings(event,state,stroke):
                return True

        # Second, honor general modes.
        if state == 'getArg':
            k.getArg(event,stroke=stroke)
            return True
        elif state == 'getFileName':
            k.getFileName(event)
            return True
        elif state in ('full-command','auto-complete'):
            # Do the default state action.
            if trace: g.trace('calling state function',k.state.kind)
            val = k.callStateFunction(event) # Calls end-command.
            if trace: g.trace('state function returns',repr(val))
            return val != 'do-standard-keys'

        # Third, pass keys to user modes.
        d =  k.masterBindingsDict.get(state)
        if d:
            assert g.isStrokeOrNone(stroke)
            si = d.get(stroke)
            if si:
                assert g.isShortcutInfo(si),si
                if trace: g.trace('calling generalModeHandler',stroke)
                k.generalModeHandler (event,
                    commandName=si.commandName,func=si.func,
                    modeName=state,nextMode=si.nextMode)
                return True
            else:
                # New in Leo 4.5: unbound keys end mode.
                # if trace: g.trace('unbound key ends mode',stroke,state)
                if 0: # 2012/05/20: I dislike this warning.
                    g.warning('unbound key ends mode',stroke) # 2011/02/02
                k.endMode()
                return False
        else:
            # New in 4.4b4.
            handler = k.getStateHandler()
            if handler:
                if trace: g.trace('handler',handler)
                handler(event)
            else:
                if trace: g.trace('No state handler for %s' % state)
            return True
    #@+node:ekr.20091230094319.6240: *5* getPaneBinding
    def getPaneBinding (self,stroke,w):

        trace = False and not g.unitTesting
        verbose = False
        k = self ; w_name = k.c.widget_name(w)
        # keyStatesTuple = ('command','insert','overwrite')
        state = k.unboundKeyAction

        assert g.isStroke(stroke)

        if trace: g.trace('w_name',repr(w_name),'stroke',stroke,'w',w,
            'isTextWidget(w)',g.app.gui.isTextWidget(w))

        for key,name in (
            # Order here is similar to bindtags order.
            ('command',None),
            ('insert',None),
            ('overwrite',None),
            ('button',None),
            ('body','body'),
            ('text','head'), # Important: text bindings in head before tree bindings.
            ('tree','head'),
            ('tree','canvas'),
            ('log', 'log'),
            ('text','log'),
            ('text',None),
            ('all',None),
        ):
            if (
                # key in keyStatesTuple and isPlain and k.unboundKeyAction == key or
                name and w_name.startswith(name) or
                key in ('command','insert','overwrite') and state == key or # 2010/02/09
                key in ('text','all') and g.app.gui.isTextWidget(w) or
                key in ('button','all')
            ):
                d = k.masterBindingsDict.get(key,{})
                if trace and verbose:
                    # g.trace('key',key,'name',name,'stroke',stroke,'stroke in d.keys',stroke in d)
                    g.trace('key: %7s name: %6s stroke: %10s in keys: %s' %
                        (key,name,stroke,stroke in d))
                    # g.trace(key,'keys',g.listToString(list(d.keys()),sort=True)) # [:5])
                if d:
                    si = d.get(stroke)
                    if si:
                        assert si.stroke == stroke,'si: %s stroke: %s' % (si,stroke)
                            # masterBindingsDict: keys are KeyStrokes
                        assert g.isShortcutInfo(si),si
                        table = ('previous-line','next-line',)
                        if key == 'text' and name == 'head' and si.commandName in table:
                            if trace: g.trace('***** special case',si.commandName)
                        else:
                            if trace: g.trace('key: %7s name: %6s  found %s = %s' % (
                                key,name,repr(si.stroke),si.commandName))
                            return si

        return None
    #@+node:ekr.20061031131434.152: *5* handleMiniBindings
    def handleMiniBindings (self,event,state,stroke):

        k = self ; c = k.c
        trace = (False or g.trace_masterKeyHandler) and not g.app.unitTesting

        # Special case for bindings handled in k.getArg:

        assert g.isStroke(stroke),repr(stroke)

        if state in ('getArg','full-command'):
            if stroke in ('\b','BackSpace','\r','Linefeed','\n','Return','\t','Tab','Escape',):
                return False
            if k.isFKey(stroke):
                return False

        if not state.startswith('auto-'):
            # New in Leo 4.5: ignore plain key binding in the minibuffer.
            if not stroke or k.isPlainKey(stroke):
                if trace: g.trace('plain key',stroke)
                return False
            # New in Leo 4.5: The minibuffer inherits 'text' and 'all' bindings
            # for all single-line editing commands.
            for pane in ('mini','all','text'):
                d = k.masterBindingsDict.get(pane)
                if d:
                    si = d.get(stroke)
                    if si:
                        assert si.stroke == stroke,'si: %s stroke: %s' % (si,stroke)
                            # masterBindingsDict: keys are KeyStrokes
                        assert g.isShortcutInfo(si),si
                        if si.commandName == 'replace-string' and state == 'getArg':
                            if trace: g.trace('%s binding for replace-string' % (pane),stroke)
                            return False # Let getArg handle it.
                        elif si.commandName not in k.singleLineCommandList:
                            if trace: g.trace('%s binding terminates minibuffer' % (
                                pane),si.commandName,stroke)
                            k.keyboardQuit()
                        else:
                            if trace: g.trace(repr(stroke),'mini binding',si.commandName)
                            c.minibufferWantsFocus() # New in Leo 4.5.
                        # Pass this on for macro recording.
                        k.masterCommand(commandName=si.commandName,event=event,func=si.func,stroke=stroke)
                        # Careful: the command could exit.
                        if c.exists and not k.silentMode:
                            c.minibufferWantsFocus()
                        return True

        return False
    #@+node:ekr.20110209083917.16004: *5* isAutoCompleteChar
    def isAutoCompleteChar (self,stroke):

        '''Return True if stroke is bound to the auto-complete in
        the insert or overwrite state.'''

        k = self ; state = k.unboundKeyAction

        assert g.isStrokeOrNone(stroke)

        if stroke and state in ('insert','overwrite'):
            for key in (state,'body','log','text','all'):
                d = k.masterBindingsDict.get(key,{})
                if d:
                    si = d.get(stroke)
                    if si:
                        assert si.stroke == stroke,'si: %s stroke: %s' % (si,stroke)
                        assert g.isShortcutInfo(si),si
                        if si.commandName == 'auto-complete':
                            return True
        return False
    #@+node:ekr.20080510095819.1: *5* k.handleUnboundKeys
    def handleUnboundKeys (self,event,char,stroke):

        trace = False and not g.unitTesting
        verbose = True
        k = self ; c = k.c
        modesTuple = ('insert','overwrite')
        # g.trace('self.enable_alt_ctrl_bindings',self.enable_alt_ctrl_bindings)
        assert g.isStroke(stroke)
        if trace and verbose: g.trace('ch: %s, stroke %s' % (
            repr(event and event.char),repr(stroke)))
        # g.trace('stroke',repr(stroke),'isFKey',k.isFKey(stroke))
        if k.unboundKeyAction == 'command':
            # Ignore all unbound characters in command mode.
            w = g.app.gui.get_focus(c)
            if w and g.app.gui.widget_name(w).lower().startswith('canvas'):
                c.onCanvasKey(event)
            if trace: g.trace('ignoring unbound character in command mode',stroke)
            return
        elif stroke.isFKey():
            if trace: g.trace('ignoring F-key',stroke)
            return
        elif stroke and k.isPlainKey(stroke) and k.unboundKeyAction in modesTuple:
            # insert/overwrite normal character.  <Return> is *not* a normal character.
            if trace: g.trace('plain key in insert mode',repr(stroke))
            k.masterCommand(event=event,stroke=stroke)
            return
        elif (not self.enable_alt_ctrl_bindings and
            (stroke.find('Alt+') > -1 or stroke.find('Ctrl+') > -1)
        ):
            # 2011/02/11: Always ignore unbound Alt/Ctrl keys.
            if trace: g.trace('ignoring unbound Alt/Ctrl key',
                repr(char),repr(stroke))
            return
        elif k.ignore_unbound_non_ascii_keys and (
            len(char) > 1 or
            char not in string.printable # 2011/06/10: risky test?
        ):
            if trace: g.trace('ignoring unbound non-ascii key',
                repr(char),repr(stroke))
            return
        elif (
            stroke and stroke.find('Escape') != -1 or
            stroke and stroke.find('Insert') != -1
        ):
            # Never insert escape or insert characters.
            if trace: g.trace('ignore Escape/Ignore',stroke)
            return
        else:
            if trace: g.trace('no func',repr(char),repr(stroke))
            k.masterCommand(event=event,stroke=stroke)
            return
    #@+node:ekr.20061031170011.3: *3* k.Minibuffer
    # These may be overridden, but this code is now gui-independent.
    #@+node:ekr.20061031131434.135: *4* k.minibufferWantsFocus
    # def minibufferWantsFocus(self):

        # c = self.c
        # c.widgetWantsFocus(c.miniBufferWidget)
    #@+node:ekr.20061031170011.5: *4* k.getLabel
    def getLabel (self,ignorePrompt=False):

        k = self ; w = self.w
        if not w: return ''

        s = w.getAllText()

        if ignorePrompt:
            return s[len(k.mb_prefix):]
        else:
            return s or ''
    #@+node:ekr.20080408060320.791: *4* k.killLine
    def killLine (self,protect=True):

        k = self
        w = k.w
        s = w.getAllText()
        s = s[:len(k.mb_prefix)]
        w.setAllText(s)
        n = len(s)
        w.setSelectionRange(n,n,insert=n)
        if protect:
            k.mb_prefix = s
    #@+node:ekr.20061031170011.6: *4* k.protectLabel
    def protectLabel (self):

        k = self ; w = self.w
        if not w: return

        k.mb_prefix = w.getAllText()

    #@+node:ekr.20061031170011.7: *4* k.resetLabel
    def resetLabel (self):

        k = self ; w = self.w
        k.setLabelGrey('')
        k.mb_prefix = ''

        if w:    
            w.setSelectionRange(0,0,insert=0)
            state = k.unboundKeyAction
            k.setLabelBlue(label='%s State' % (state.capitalize()),protect=True)
    #@+node:ekr.20061031170011.8: *4* k.setLabel
    def setLabel (self,s,protect=False):

        trace = (False or g.trace_minibuffer) and not g.app.unitTesting
        k = self
        w = k.w
        if not w: return

        if trace: g.trace(repr(s),w)
        w.setAllText(s)
        n = len(s)
        w.setSelectionRange(n,n,insert=n)
        if protect:
            k.mb_prefix = s
    #@+node:ekr.20061031170011.9: *4* k.extendLabel
    def extendLabel(self,s,select=False,protect=False):

        trace = False and not g.unitTesting

        k = self ; c = k.c ; w = self.w
        if not (w and s): return

        if trace: g.trace(s)

        c.widgetWantsFocusNow(w)

        w.insert('end',s)

        if select:
            i,j = k.getEditableTextRange()
            w.setSelectionRange(i,j,insert=j)

        if protect:
            k.protectLabel()
    #@+node:ekr.20080408060320.790: *4* k.selectAll
    def selectAll (self):

        '''Select all the user-editable text of the minibuffer.'''

        w = self.w
        i,j = self.getEditableTextRange()
        w.setSelectionRange(i,j,insert=j)


    #@+node:ekr.20061031170011.10: *4* k.setLabelBlue
    def setLabelBlue (self,label=None,protect=False):

        k = self ; w = k.w
        if not w: return

        # w.setBackgroundColor(self.minibuffer_background_color) # 'lightblue')

        w.setBothColors(
            self.minibuffer_background_color,
            self.minibuffer_foreground_color)

        if label is not None:
            k.setLabel(label,protect)
    #@+node:ekr.20061031170011.11: *4* k.setLabelGrey
    def setLabelGrey (self,label=None):

        k = self ; w = self.w
        if not w: return

        w.setBackgroundColor(self.minibuffer_warning_color) # 'lightgrey')

        if label is not None:
            k.setLabel(label)

    setLabelGray = setLabelGrey
    #@+node:ekr.20080510153327.2: *4* k.setLabelRed
    def setLabelRed (self,label=None,protect=False):

        k = self ; w = self.w
        if not w: return

        w.setBothColors(
            self.minibuffer_warning_color,
            self.minibuffer_error_color)

        if label is not None:
            k.setLabel(label,protect)
    #@+node:ekr.20061031170011.12: *4* k.updateLabel
    def updateLabel (self,event):

        '''Mimic what would happen with the keyboard and a Text editor
        instead of plain accumalation.'''

        trace = False or g.trace_minibuffer and not g.app.unitTesting
        k = self ; c = k.c ; w = self.w
        ch = (event and event.char) or ''
        if trace: g.trace('ch',ch,'k.stroke',k.stroke)

        if ch and ch not in ('\n','\r'):
            c.widgetWantsFocusNow(w)
            i,j = w.getSelectionRange()
            ins = w.getInsertPoint()
            # g.trace(i,j,ins)
            if i != j:
                w.delete(i,j)
            if ch == '\b':
                s = w.getAllText()
                if len(s) > len(k.mb_prefix):
                    w.delete(i-1)
                    i-=1
            else:
                w.insert(ins,ch)
                i = ins+1
    #@+node:ekr.20061031170011.13: *4* k.getEditableTextRange
    def getEditableTextRange (self):

        k = self ; w = self.w
        s = w.getAllText()
        i = len(k.mb_prefix)
        j = len(s)
        return i,j
    #@+node:ekr.20120208064440.10190: *3* k.Modes (no change)
    #@+node:ekr.20061031131434.100: *4* k.addModeCommands (enterModeCallback)
    def addModeCommands (self):

        '''Add commands created by @mode settings to c.commandsDict and k.inverseCommandsDict.'''

        trace = False and not g.unitTesting

        if trace: g.trace('(k)')

        k = self ; c = k.c
        d = g.app.config.modeCommandsDict # Keys are command names: enter-x-mode.

        # Create the callback functions and update c.commandsDict and k.inverseCommandsDict.
        for key in d.keys():

            def enterModeCallback (event=None,name=key):
                k.enterNamedMode(event,name)

            c.commandsDict[key] = f = enterModeCallback
            k.inverseCommandsDict [f.__name__] = key
            if trace: g.trace(f.__name__,key,'len(c.commandsDict.keys())',len(list(c.commandsDict.keys())))
    #@+node:ekr.20061031131434.157: *4* k.badMode
    def badMode(self,modeName):

        k = self

        k.clearState()
        if modeName.endswith('-mode'): modeName = modeName[:-5]
        k.setLabelGrey('@mode %s is not defined (or is empty)' % modeName)
    #@+node:ekr.20061031131434.158: *4* k.createModeBindings
    def createModeBindings (self,modeName,d,w):

        '''Create mode bindings for the named mode using dictionary d for w, a text widget.'''

        trace = False and not g.unitTesting
        k = self ; c = k.c
        assert d.name().endswith('-mode')
        for commandName in d.keys():
            if commandName in ('*entry-commands*','*command-prompt*'):
                # These are special-purpose dictionary entries.
                continue
            func = c.commandsDict.get(commandName)
            if not func:
                g.es_print('no such command:',commandName,'Referenced from',modeName)
                continue
            aList = d.get(commandName,[])
            for si in aList:
                assert g.isShortcutInfo(si),si
                stroke = si.stroke
                # Important: si.val is canonicalized.
                if stroke and stroke not in ('None','none',None):
                    if trace:
                        g.trace(
                            g.app.gui.widget_name(w), modeName,
                            '%10s' % (stroke),
                            '%20s' % (commandName),
                            si.nextMode)

                    assert g.isStroke(stroke)

                    k.makeMasterGuiBinding(stroke)

                    # Create the entry for the mode in k.masterBindingsDict.
                    # Important: this is similar, but not the same as k.bindKeyToDict.
                    # Thus, we should **not** call k.bindKey here!
                    d2 = k.masterBindingsDict.get(modeName,{})
                    d2 [stroke] = g.ShortcutInfo(
                        kind = 'mode<%s>' % (modeName), # 2012/01/23
                        commandName=commandName,
                        func=func,
                        nextMode=si.nextMode,
                        stroke=stroke)
                    k.masterBindingsDict [ modeName ] = d2
    #@+node:ekr.20120208064440.10179: *4* k.endMode
    def endMode(self):

        k = self ; c = k.c

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
    def enterNamedMode (self,event,commandName):

        k = self ; c = k.c
        modeName = commandName[6:]
        c.inCommand = False # Allow inner commands in the mode.
        k.generalModeHandler(event,modeName=modeName)
    #@+node:ekr.20061031131434.161: *4* k.exitNamedMode
    def exitNamedMode (self,event=None):

        '''Exit an input mode.'''

        k = self

        if k.inState():
            k.endMode()

        k.showStateAndMode()
    #@+node:ekr.20061031131434.165: *4* k.modeHelp & helper (revise helper)
    def modeHelp (self,event):

        '''The mode-help command.

        A possible convention would be to bind <Tab> to this command in most modes,
        by analogy with tab completion.'''

        k = self ; c = k.c
        c.endEditing()
        # g.trace(k.inputModeName)
        if k.inputModeName:
            d = g.app.config.modeCommandsDict.get('enter-'+k.inputModeName)
            k.modeHelpHelper(d)
        if not k.silentMode:
            c.minibufferWantsFocus()
    #@+node:ekr.20061031131434.166: *5* modeHelpHelper
    def modeHelpHelper (self,d):

        k = self ; c = k.c ; tabName = 'Mode'
        c.frame.log.clearTab(tabName)
        data,n = [],0
        for key in sorted(d.keys()):
            if key in ('*entry-commands*','*command-prompt*'):
                pass
            else:
                aList = d.get(key)
                for si in aList:
                    assert g.isShortcutInfo(si),si
                    stroke = si.stroke
                    if stroke not in (None,'None'):
                        s1 = key
                        s2 = k.prettyPrintKey(stroke)
                        n = max(n,len(s1))
                        data.append((s1,s2),)

        data.sort()
        modeName = k.inputModeName.replace('-',' ')
        if modeName.endswith('mode'):
            modeName = modeName[:-4].strip()

        prompt = d.get('*command-prompt*')
        if prompt:
            g.es('','%s\n\n' % (prompt.kind.strip()),tabName=tabName)
        else:
            g.es('','%s mode\n\n' % modeName,tabName=tabName)

        # This isn't perfect in variable-width fonts.
        for s1,s2 in data:
            g.es('','%*s %s' % (n,s1,s2),tabName=tabName)
    #@+node:ekr.20061031131434.164: *4* k.reinitMode (call k.createModeBindings???)
    def reinitMode (self,modeName):

        k = self
        d = k.modeBindingsDict
        k.inputModeName = modeName
        w = g.choose(k.silentMode,k.modeWidget,k.w)
        k.createModeBindings(modeName,d,w)
        if k.silentMode:
            k.showStateAndMode()
        else:
            # Do not set the status line here.
            k.setLabelBlue(modeName+': ',protect=True)
    #@+node:ekr.20120208064440.10199: *4* k.generalModeHandler (OLD)
    def generalModeHandler (self,event,
        commandName=None,func=None,modeName=None,nextMode=None,prompt=None):

        '''Handle a mode defined by an @mode node in leoSettings.leo.'''

        k = self ; c = k.c
        state = k.getState(modeName)
        trace = (False or g.trace_modes) and not g.unitTesting

        if trace: g.trace(modeName,'state',state)

        if state == 0:
            k.inputModeName = modeName
            k.modePrompt = prompt or modeName
            k.modeWidget = event and event.widget
            k.setState(modeName,1,handler=k.generalModeHandler)
            self.initMode(event,modeName)
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
                if trace or c.config.getBool('trace_doCommand'): g.trace(func.__name__)
                # New in 4.4.1 b1: pass an event describing the original widget.
                if event:
                    event.w = event.widget = k.modeWidget
                else:
                    event = g.app.gui.create_key_event(c,None,None,k.modeWidget)
                if trace: g.trace(modeName,'state',state,commandName,'nextMode',nextMode)
                func(event)
                if g.app.quitting or not c.exists:
                    pass
                elif nextMode in (None,'none'):
                    # Do *not* clear k.inputModeName or the focus here.
                    # func may have put us in *another* mode.
                    pass
                elif nextMode == 'same':
                    silent = k.silentMode
                    k.setState(modeName,1,handler=k.generalModeHandler)
                    self.reinitMode(modeName) # Re-enter this mode.
                    k.silentMode = silent
                else:
                    k.silentMode = False # All silent modes must do --> set-silent-mode.
                    self.initMode(event,nextMode) # Enter another mode.
    #@+node:ekr.20061031131434.156: *3* k.Modes (changed)
    #@+node:ekr.20061031131434.163: *4* k.initMode (changed)
    def initMode (self,event,modeName):

        k = self ; c = k.c
        trace = (False or g.trace_modes) and not g.unitTesting

        if not modeName:
            g.trace('oops: no modeName')
            return

        if g.new_modes:
            mode = k.modeController.getMode(modeName)
            if mode:
                mode.initMode()
            else:
                g.trace('***** oops: no mode',modeName)
        else:
            d = g.app.config.modeCommandsDict.get('enter-'+modeName)
            if not d:
                self.badMode(modeName)
                return
            else:
                k.modeBindingsDict = d
                si = d.get('*command-prompt*')
                if si:
                    prompt = si.kind # A kludge.
                else:
                    prompt = modeName
                if trace: g.trace('modeName: %s prompt: %s d.keys(): %s' % (
                    modeName,prompt,sorted(list(d.keys()))))

            k.inputModeName = modeName
            k.silentMode = False

            aList = d.get('*entry-commands*',[])
            if aList:
                for si in aList:
                    assert g.isShortcutInfo(si),si
                    commandName = si.commandName
                    if trace: g.trace('entry command:',commandName)
                    k.simulateCommand(commandName)
                    # Careful, the command can kill the commander.
                    if g.app.quitting or not c.exists: return
                    # New in Leo 4.5: a startup command can immediately transfer to another mode.
                    if commandName.startswith('enter-'):
                        if trace: g.trace('redirect to mode',commandName)
                        return

            # Create bindings after we know whether we are in silent mode.
            w = g.choose(k.silentMode,k.modeWidget,k.w)
            k.createModeBindings(modeName,d,w)
            k.showStateAndMode(prompt=prompt)
    #@+node:ekr.20120208064440.10201: *4* k.NEWgeneralModeHandler (NEW MODES)
    def NEWgeneralModeHandler (self,event,
        commandName=None,func=None,modeName=None,nextMode=None,prompt=None):

        '''Handle a mode defined by an @mode node in leoSettings.leo.'''

        k = self ; c = k.c
        state = k.getState(modeName)
        trace = (False or g.trace_modes) and not g.unitTesting
        if trace: g.trace(modeName,'state',state)

        if state == 0:
            k.inputModeName = modeName
            k.modePrompt = prompt or modeName
            k.modeWidget = event and event.widget
            k.setState(modeName,1,handler=k.generalModeHandler)
            self.initMode(event,modeName)
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
                if trace or c.config.getBool('trace_doCommand'): g.trace(func.__name__)
                # New in 4.4.1 b1: pass an event describing the original widget.
                if event:
                    event.w = event.widget = k.modeWidget
                else:
                    event = g.app.gui.create_key_event(c,None,None,k.modeWidget)
                if trace: g.trace(modeName,'state',state,commandName,'nextMode',nextMode)
                func(event)
                if g.app.quitting or not c.exists:
                    pass
                elif nextMode in (None,'none'):
                    # Do *not* clear k.inputModeName or the focus here.
                    # func may have put us in *another* mode.
                    pass
                elif nextMode == 'same':
                    silent = k.silentMode
                    k.setState(modeName,1,handler=k.generalModeHandler)
                    self.reinitMode(modeName) # Re-enter this mode.
                    k.silentMode = silent
                else:
                    k.silentMode = False # All silent modes must do --> set-silent-mode.
                    self.initMode(event,nextMode) # Enter another mode.
                    # Careful: k.initMode can execute commands that will destroy a commander.
                    # if g.app.quitting or not c.exists: return
    #@+node:ekr.20061031131434.167: *3* k.Shared helpers
    #@+node:ekr.20061031131434.175: *4* k.computeCompletionList
    # Important: this code must not change mb_tabListPrefix.  Only doBackSpace should do that.

    def computeCompletionList (self,defaultTabList,backspace,allow_empty_completion=False):

        trace = False and not g.unitTesting
        k = self ; c = k.c ; s = k.getLabel() ; tabName = 'Completion'
        command = s [len(k.mb_prompt):]
            # s always includes prefix, so command is well defined.

        k.mb_tabList,common_prefix = g.itemsMatchingPrefixInList(command,defaultTabList)
        c.frame.log.clearTab(tabName)

        if trace:
            g.trace('command',command)
            g.trace('common_prefix',common_prefix)
            g.trace('k.mb_tabList',k.mb_tabList)

        if not k.mb_tabList and allow_empty_completion:
            if command:
                # 2012/05/20: Put up an *empty* list as a visual cue.
                k.mb_tabList = []
                g.es('','\n',tabName=tabName)
            else:
                # 2012/05/20: Return *all* completions if the command is empty.
                k.mb_tabList = sorted(defaultTabList)
                common_prefix = ''

        if k.mb_tabList:
            k.mb_tabListIndex = -1 # The next item will be item 0.
            if not backspace:
                k.setLabel(k.mb_prompt + common_prefix)

            inverseBindingDict = k.computeInverseBindingDict()
            data,n = [],0
            for commandName in k.mb_tabList:
                dataList = inverseBindingDict.get(commandName,[('',''),])
                for z in dataList:
                    pane,key = z
                    s1a = '%s ' % (pane) if pane != 'all:' else ''
                    s1b = k.prettyPrintKey(key)
                    s1 = s1a + s1b
                    s2 = commandName
                    data.append((s1,s2),)
                    n = max(n,len(s1))
            aList = ['%*s %s' % (-n,s1,s2) for s1,s2 in data]
            g.es('','\n'.join(aList),tabName=tabName)
        c.bodyWantsFocus()
    #@+node:ekr.20061031131434.177: *4* k.doBackSpace
    # Used by getArg and fullCommand.

    def doBackSpace (self,defaultCompletionList,completion=True):

        '''Cut back to previous prefix and update prefix.'''

        trace = False and not g.unitTesting
        k = self
        w = self.w
        ins = w.getInsertPoint()
        if trace: g.trace(
            'ins',ins,'k.mb_prefix',repr(k.mb_prefix),'w',w)
        if ins <= len(k.mb_prefix):
            # g.trace('at start')
            return
            
        # Step 1: actually delete the character.
        i,j = w.getSelectionRange()
        if i == j:
            ins -= 1
            w.delete(ins)
            w.setSelectionRange(ins,ins,insert=ins)
        else:
            ins = i
            w.delete(i,j)
            w.setSelectionRange(i,i,insert=ins)

        # Step 2: compute completions.
        if not completion: return
        k.mb_tabListPrefix = w.getAllText()
        k.computeCompletionList(defaultCompletionList,backspace=True)
    #@+node:ekr.20061031131434.178: *4* k.doTabCompletion
    # Used by getArg and fullCommand.

    def doTabCompletion (self,defaultTabList,redraw=True,allow_empty_completion=False):

        '''Handle tab completion when the user hits a tab.'''

        trace = False and not g.unitTesting
        k = self ; c = k.c ; s = k.getLabel().strip()

        if k.mb_tabList and s.startswith(k.mb_tabListPrefix):
            if trace: g.trace('cycle',repr(s))
            # Set the label to the next item on the tab list.
            k.mb_tabListIndex +=1
            if k.mb_tabListIndex >= len(k.mb_tabList):
                k.mb_tabListIndex = 0
            k.setLabel(k.mb_prompt + k.mb_tabList [k.mb_tabListIndex])
        else:
            if redraw:
                if trace: g.trace('** recomputing default completions')
                k.computeCompletionList(defaultTabList,
                    backspace=False,
                    allow_empty_completion=allow_empty_completion)

        c.minibufferWantsFocus()
    #@+node:ekr.20061031131434.168: *4* k.getFileName & helpers
    def getFileName (self,event=None,handler=None,prefix='',filterExt='.leo'):

        '''Similar to k.getArg, but uses completion to indicate files on the file system.'''

        k = self ; c = k.c
        tag = 'getFileName' ; state = k.getState(tag)
        tabName = 'Completion'

        char = event and event.char or ''
        # g.trace('state',state,'char',char)

        if state == 0:
            k.arg = ''
            #@+<< init altX vars >>
            #@+node:ekr.20061031131434.169: *5* << init altX vars >>
            k.filterExt = filterExt
            k.mb_prefix = (prefix or k.getLabel())
            k.mb_prompt = prefix or k.getLabel()
            k.mb_tabList = []

            # Clear the list: any non-tab indicates that a new prefix is in effect.
            theDir = g.os_path_finalize(os.curdir)
            k.extendLabel(theDir,select=False,protect=False)

            k.mb_tabListPrefix = k.getLabel()
            #@-<< init altX vars >>
            # Set the states.
            k.getFileNameHandler = handler
            k.setState(tag,1,k.getFileName)
            k.afterArgWidget = event and event.widget or c.frame.body.bodyCtrl
            c.frame.log.clearTab(tabName)
            c.minibufferWantsFocus()
        elif char in ('\n','Return'):
            k.arg = k.getLabel(ignorePrompt=True)
            handler = k.getFileNameHandler
            c.frame.log.deleteTab(tabName)
            if handler: handler(event)
        elif char in ('\t','Tab'):
            k.doFileNameTab()
            c.minibufferWantsFocus()
        elif char in ('\b','BackSpace'):
            k.doFileNameBackSpace() 
            c.minibufferWantsFocus()
        else:
            k.doFileNameChar(event)
    #@+node:ekr.20061031131434.170: *5* k.doFileNameBackSpace
    def doFileNameBackSpace (self):

        '''Cut back to previous prefix and update prefix.'''

        k = self
        if 0:
            g.trace(
                len(k.mb_tabListPrefix) > len(k.mb_prefix),
                repr(k.mb_tabListPrefix),repr(k.mb_prefix))

        if len(k.mb_tabListPrefix) > len(k.mb_prefix):
            k.mb_tabListPrefix = k.mb_tabListPrefix [:-1]
            k.setLabel(k.mb_tabListPrefix)
    #@+node:ekr.20061031131434.171: *5* k.doFileNameChar
    def doFileNameChar (self,event):

        k = self

        # Clear the list, any other character besides tab indicates that a new prefix is in effect.
        k.mb_tabList = []
        k.updateLabel(event)
        k.mb_tabListPrefix = k.getLabel()

        common_prefix = k.computeFileNameCompletionList()

        if k.mb_tabList:
            k.setLabel(k.mb_prompt + common_prefix)
        else:
            # Restore everything.
            old = k.getLabel(ignorePrompt=True)[:-1]
            k.setLabel(k.mb_prompt + old)
    #@+node:ekr.20061031131434.172: *5* k.doFileNameTab
    def doFileNameTab (self):

        k = self
        common_prefix = k.computeFileNameCompletionList()

        if k.mb_tabList:
            k.setLabel(k.mb_prompt + common_prefix)
    #@+node:ekr.20061031131434.173: *5* k.computeFileNameCompletionList
    # This code must not change mb_tabListPrefix.
    def computeFileNameCompletionList (self):

        k = self ; c = k.c ; tabName = 'Completion'
        path = k.getLabel(ignorePrompt=True)
        sep = os.path.sep
        tabList = []
        for f in glob.glob(path+'*'):
            if g.os_path_isdir(f):
                tabList.append(f + sep)
            else:
                junk,ext = g.os_path_splitext(f)
                if not ext or ext == k.filterExt:
                    tabList.append(f)
        k.mb_tabList = tabList
        junk,common_prefix = g.itemsMatchingPrefixInList(path,tabList)
        if tabList:
            c.frame.log.clearTab(tabName)
            k.showFileNameTabList()
        return common_prefix
    #@+node:ekr.20061031131434.174: *5* k.showFileNameTabList
    def showFileNameTabList (self):

        k = self ; tabName = 'Completion'

        for path in k.mb_tabList:
            theDir,fileName = g.os_path_split(path)
            s = g.choose(path.endswith('\\'),theDir,fileName)
            s = fileName or g.os_path_basename(theDir) + '\\'
            g.es('',s,tabName=tabName)
    #@+node:ekr.20110609161752.16459: *4* k.setLossage
    def setLossage (self,ch,stroke):

        trace = False and not g.unitTesting
        # k = self
        if trace: g.trace(repr(stroke),g.callers())
        if ch or stroke:
            if len(g.app.lossage) > 99:
                g.app.lossage.pop()
        # This looks like a memory leak, but isn't.
        g.app.lossage.insert(0,(ch,stroke),)
    #@+node:ekr.20061031131434.180: *4* k.traceBinding (not used)
    def traceBinding (self,si,shortcut,w):

        k = self ; c = k.c ; gui = g.app.gui
        if not c.config.getBool('trace_bindings'): return

        theFilter = c.config.getString('trace_bindings_filter') or ''
        if theFilter and shortcut.lower().find(theFilter.lower()) == -1: return

        pane_filter = c.config.getString('trace_bindings_pane_filter')
        if not pane_filter or pane_filter.lower() == si.pane:
            g.trace(si.pane,shortcut,si.commandName,gui.widget_name(w))
    #@+node:ekr.20061031131434.181: *3* k.Shortcuts & bindings
    #@+node:ekr.20061031131434.176: *4* k.computeInverseBindingDict
    def computeInverseBindingDict (self):

        k = self ; d = {}

        # keys are minibuffer command names, values are shortcuts.
        for stroke in k.bindingsDict.keys():
            assert g.isStroke(stroke),repr(stroke)
            aList = k.bindingsDict.get(stroke,[])
            for si in aList:
                assert g.isShortcutInfo(si),si
                shortcutList = d.get(si.commandName,[])

                # The shortcutList consists of tuples (pane,stroke).
                # k.inverseBindingDict has values consisting of these tuples.
                aList = k.bindingsDict.get(stroke,g.ShortcutInfo(kind='dummy',pane='all'))
                        # Important: only si.pane is required below.
                for si in aList:
                    assert g.isShortcutInfo(si),si
                    pane = '%s:' % (si.pane)
                    data = (pane,stroke)
                    if data not in shortcutList:
                        shortcutList.append(data)

                d [si.commandName] = shortcutList

        return d
    #@+node:ekr.20061031131434.179: *4* k.getShortcutForCommand/Name
    def getShortcutForCommandName (self,commandName):

        k = self ; c = k.c
        command = c.commandsDict.get(commandName)
        if command:
            for stroke in k.bindingsDict:
                assert g.isStroke(stroke),repr(stroke)
                aList = k.bindingsDict.get(stroke,[])
                for si in aList:
                    assert g.isShortcutInfo(si),si
                    if si.commandName == commandName:
                        return stroke
        return None

    def getShortcutForCommand (self,command):

        k = self
        if command:
            for stroke in k.bindingsDict:
                assert g.isStroke(stroke),repr(stroke)
                aList = k.bindingsDict.get(stroke,[])
                for si in aList:
                    assert g.isShortcutInfo(si),si
                    if si.commandName == command.__name__:
                        return stroke
        return None
    #@+node:ekr.20090518072506.8494: *4* k.isFKey
    def isFKey (self,stroke):

        # k = self
        if not stroke: return False
        assert g.isString(stroke) or g.isStroke(stroke)
        s = stroke.s if g.isStroke(stroke) else stroke
        s = s.lower()
        return s.startswith('f') and len(s) <= 3 and s[1:].isdigit()
    #@+node:ekr.20061031131434.182: *4* k.isPlainKey
    def isPlainKey (self,stroke):

        '''Return true if the shortcut refers to a plain (non-Alt,non-Ctl) key.'''

        k = self
        if not stroke: return False

        assert g.isString(stroke) or g.isStroke(stroke)
        shortcut = stroke.s if g.isStroke(stroke) else stroke

        # altgr combos (Alt+Ctrl) are always plain keys
        if shortcut.startswith('Alt+Ctrl+') and not self.enable_alt_ctrl_bindings:
            return True

        for z in ('Alt','Ctrl','Command','Meta'):
            if shortcut.find(z) != -1:            
                return False
        else:
            # Careful, allow bare angle brackets for unit tests.
            if shortcut.startswith('<') and shortcut.endswith('>'):
                shortcut = shortcut[1:-1]

            isPlain = (
                len(shortcut) == 1 or
                len(k.guiBindNamesInverseDict.get(shortcut,'')) == 1 or
                # A hack: allow Return to be bound to command.
                shortcut in ('Tab','\t')
            )

            # g.trace(isPlain,repr(shortcut))
            return isPlain and not self.isFKey(shortcut)
    #@+node:ekr.20061031131434.191: *4* k.prettyPrintKey
    def prettyPrintKey (self,stroke,brief=False):

        trace = False and not g.unitTesting
        k = self
        if not stroke:
            s = ''
        elif g.isStroke(stroke):
            s = stroke.s
        else:
            s = stroke

        if not s: return ''

        shift = s.find("shift") >= 0 or s.find("shft") >= 0

        # Replace all minus signs by plus signs, except a trailing minus:
        if s.endswith('-'): s = s[:-1].replace('-','+') + '-'
        else:               s = s.replace('-','+')
        fields = s.split('+')
        last = fields and fields[-1]
        if trace: g.trace('fields',fields)
        if last and len(last) == 1:
            prev = s[:-1]
            if last.isalpha():
                if last.isupper():
                    if not shift:
                        s = prev + 'Shift+' + last
                elif last.islower():
                    if not prev:
                        s = last.upper()
                    else:
                        s = prev + last.upper()
        else:
            last = k.guiBindNamesInverseDict.get(last,last)
            if fields and fields[:-1]:
                s = '%s+%s' % ('+'.join(fields[:-1]),last)
            else:
                s = last
        if s.endswith(' '):
            s = s[:-1]+'Space' # 2010/11/06

        return s
    #@+node:ekr.20061031131434.184: *4* k.strokeFromSetting
    def strokeFromSetting (self,setting,addKey=True):

        k = self

        trace = False and not g.unitTesting # and setting.lower().find('ctrl-x') > -1
        verbose = False
        if not setting:
            return None

        assert g.isString(setting)

        s = g.stripBrackets(setting.strip())
        #@+<< define cmd, ctrl, alt, shift >>
        #@+node:ekr.20061031131434.185: *5* << define cmd, ctrl, alt, shift >>
        s2 = s.lower()

        cmd   = s2.find("cmd") >= 0     or s2.find("command") >= 0
        ctrl  = s2.find("control") >= 0 or s2.find("ctrl") >= 0
        alt   = s2.find("alt") >= 0
        shift = s2.find("shift") >= 0   or s2.find("shft") >= 0
        meta  = s2.find("meta") >= 0
        #@-<< define cmd, ctrl, alt, shift >>
        if k.swap_mac_keys and sys.platform == "darwin":
            #@+<< swap cmd and ctrl keys >>
            #@+node:ekr.20061031131434.186: *5* << swap cmd and ctrl keys >>
            if ctrl and not cmd:
                cmd = True ; ctrl = False
            if alt and not ctrl:
                ctrl = True ; alt = False
            #@-<< swap cmd and ctrl keys >>
        #@+<< convert minus signs to plus signs >>
        #@+node:ekr.20061031131434.187: *5* << convert minus signs to plus signs >>
        # Replace all minus signs by plus signs, except a trailing minus:
        if s.endswith('-'):
            s = s[:-1].replace('-','+') + '-'
        else:
            s = s.replace('-','+')
        #@-<< convert minus signs to plus signs >>
        #@+<< compute the last field >>
        #@+node:ekr.20061031131434.188: *5* << compute the last field >>
        if s.endswith('+'):
            last = '+'
        else:
            fields = s.split('+') # Don't lower this field.
            last = fields and fields[-1]
            if not last:
                if not g.app.menuWarningsGiven:
                    g.pr("bad shortcut specifier:", repr(s),repr(setting))
                    g.trace(g.callers())
                return None

        if len(last) == 1:
            last2 = k.guiBindNamesDict.get(last) # Fix new bug introduced in 4.4b2.
            if last2:
                last = last2
            else:
                if last.isalpha():
                    if shift:
                        last = last.upper()
                        shift = False # It is Ctrl-A, not Ctrl-Shift-A.
                    else:
                        last = last.lower()
                # New in Leo 4.4.2: Alt-2 is not a key event!
                if addKey and last.isdigit():
                    last = 'Key-' + last
        else:
            # Translate from a made-up (or lowercase) name to 'official' Tk binding name.
            # This is a *one-way* translation, done only here.
            d = k.settingsNameDict
            last = d.get(last.lower(),last)
        #@-<< compute the last field >>
        #@+<< compute shortcut >>
        #@+node:ekr.20061031131434.189: *5* << compute shortcut >>
        table = (
            (alt, 'Alt+'),
            (ctrl,'Ctrl+'),
            (cmd, 'Command+'),
            (meta,'Meta+'),
            (shift,'Shift+'),
            (True, last),
        )

        # new in 4.4b3: convert all characters to unicode first.
        shortcut = ''.join([g.toUnicode(val) for flag,val in table if flag])
        #@-<< compute shortcut >>

        if trace and verbose:
            g.trace('%20s %s' % (setting,shortcut),g.callers())

        return g.KeyStroke(shortcut) if shortcut else None

    canonicalizeShortcut = strokeFromSetting # For compatibility.
    ### strokeFromSetting = shortcutFromSetting
    #@+node:ekr.20110606004638.16929: *4* k.stroke2char
    def stroke2char (self,stroke):

        '''Convert a stroke to an (insertable) char.

        This method allows Leo to use strokes everywhere.'''

        trace = False and not g.unitTesting
        k = self

        if not stroke: return ''
        s = stroke.s

        # Allow bare angle brackets for unit tests.
        if s.startswith('<') and s.endswith('>'):
            s = s[1:-1]

        if len(s) == 0: return ''
        if len(s) == 1: return s

        for z in ('Alt','Ctrl','Command','Meta'):
            if s.find(z) != -1:            
                return ''
                # This is not accurate: leoQtEventFilter retains
                # the spelling of Alt-Ctrl keys because of the
                # @bool enable_alt_ctrl_bindings setting.

        # Special case the gang of four, plus 'Escape',
        d = {
            'BackSpace':'\b',
            'Escape':'Escape',
            'Linefeed':'\r',
            'Return':'\n',
            'Tab':'\t',
        }
        ch = d.get(s)
        if ch: return ch

        # First, do the common translations.
        ch = k.guiBindNamesInverseDict.get(s)
        if ch:
            if trace: g.trace(repr(stroke),repr(ch))
            return ch

        # A much-simplified form of code in k.strokeFromSetting.
        shift = s.find('Shift+') > -1 or s.find('Shift-') > -1
        s = s.replace('Shift+','').replace('Shift-','')

        last = s #  Everything should have been stripped.

        if len(s) == 1 and s.isalpha():
            if shift:
                s = last.upper()
            else:
                s = last.lower()

        val = g.choose(len(s)==1,s,'')

        if trace: g.trace(repr(stroke),repr(val)) # 'shift',shift,
        return val
    #@+node:ekr.20061031131434.193: *3* k.States
    #@+node:ekr.20061031131434.194: *4* clearState
    def clearState (self):

        k = self
        k.state.kind = None
        k.state.n = None
        k.state.handler = None
    #@+node:ekr.20061031131434.196: *4* getState
    def getState (self,kind):

        k = self
        val = g.choose(k.state.kind == kind,k.state.n,0)
        # g.trace(state,'returns',val)
        return val
    #@+node:ekr.20061031131434.195: *4* getStateHandler
    def getStateHandler (self):

        return self.state.handler
    #@+node:ekr.20061031131434.197: *4* getStateKind
    def getStateKind (self):

        return self.state.kind
    #@+node:ekr.20061031131434.198: *4* inState
    def inState (self,kind=None):

        k = self

        if kind:
            return k.state.kind == kind and k.state.n != None
        else:
            return k.state.kind and k.state.n != None
    #@+node:ekr.20080511122507.4: *4* setDefaultInputState
    def setDefaultInputState (self):

        k = self ; state = k.defaultUnboundKeyAction

        # g.trace(state)

        k.setInputState(state)
    #@+node:ekr.20110209093958.15411: *4* setEditingState
    def setEditingState (self):

        k = self ; state = k.defaultEditingAction

        # g.trace(state)

        k.setInputState(state)
    #@+node:ekr.20061031131434.133: *4* setInputState
    def setInputState (self,state,set_border=False):

        c,k = self.c,self
        k.unboundKeyAction = state

        if set_border and c.frame and c.frame.body:
            w = c.frame.body.bodyCtrl
            if hasattr(w,'widget'):
                g.app.gui.add_border(c,w.widget)
    #@+node:ekr.20061031131434.199: *4* setState
    def setState (self,kind,n,handler=None):

        trace = False and not g.unitTesting
        k = self

        if kind and n != None:
            if trace: g.trace('**** setting %s %s %s' % (
                kind,n,handler and handler.__name__),g.callers())
            k.state.kind = kind
            k.state.n = n
            if handler:
                k.state.handler = handler
        else:
            if trace: g.trace('clearing')
            k.clearState()

        # k.showStateAndMode()
    #@+node:ekr.20061031131434.192: *4* k.showStateAndMode
    def showStateAndMode(self,w=None,prompt=None,setFocus=True):

        trace = False and not g.unitTesting
        k = self ; c = k.c
        state = k.unboundKeyAction
        mode = k.getStateKind()
        inOutline = False
        if not g.app.gui: return
        if not w:
            w = g.app.gui.get_focus(c)
            if not w: return

        isText = g.app.gui.isTextWidget(w)

        # This fixes a problem with the tk gui plugin.
        if mode and mode.lower().startswith('isearch'):
            return

        wname = g.app.gui.widget_name(w).lower()

        # 2011/02/12: get the wrapper for the headline widget.
        if wname.startswith('head'):
            if hasattr(c.frame.tree,'getWrapper'):
                if hasattr(w,'widget'): w2 = w.widget
                else: w2 = w
                w = c.frame.tree.getWrapper(w2,item=None)
                isText = bool(w) # A benign hack.

        if trace: g.trace('state: %s, text?: %s, w: %s' % (
            state,isText,w))

        if mode:
            if mode in ('getArg','getFileName','full-command'):
                s = None
            elif prompt:
                s = prompt
            else:
                mode = mode.strip()
                if mode.endswith('-mode'):
                    mode = mode[:-5]
                s = '%s Mode' % mode.capitalize()
        else:
            s = '%s State' % state.capitalize()
            if c.editCommands.extendMode:
                s = s + ' (Extend Mode)'

        if trace: g.trace('w',w,'s',s)

        if s:
            k.setLabelBlue(label=s,protect=True)
        if w and isText:
            k.showStateColors(inOutline,w)
            k.showStateCursor(state,w)
    #@+node:ekr.20080512115455.1: *4* k.showStateColors (changed)
    def showStateColors (self,inOutline,w):

        trace = False and not g.unitTesting
        k = self ; c = k.c
        if c.use_focus_border:
            return

        # This is now deprecated.
        state = k.unboundKeyAction
        if state not in ('insert','command','overwrite'):
            g.trace('bad input state',state)

        w_name = g.app.gui.widget_name(w)

        if w_name.startswith('body'):
            w = c.frame.body
        elif w_name.startswith('head'):
            pass
        else:
            # Don't recolor the minibuffer, log panes, etc.
            if trace: g.trace('not body or head')
            return
        if state == 'insert':
            bg = k.insert_mode_bg_color
            fg = k.insert_mode_fg_color
        elif state == 'command':
            bg = k.command_mode_bg_color
            fg = k.command_mode_fg_color
        elif state == 'overwrite':
            bg = k.overwrite_mode_bg_color
            fg = k.overwrite_mode_fg_color
        else:
            bg = fg = 'red'

        if hasattr(w,'setEditorColors'):
            # Note: fg color has no effect on Qt at present.
            w.setEditorColors(bg=bg,fg=fg)
        else:
            try:
                w.configure(bg=bg,fg=fg)
            except Exception:
                pass # g.es_exception()
    #@+node:ekr.20110202111105.15439: *4* showStateCursor
    def showStateCursor (self,state,w):

        # g.trace(state,w)

        pass


    #@+node:ekr.20061031131434.200: *3* k.universalDispatcher & helpers
    def universalDispatcher (self,event):

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
        c,k = self.c,self
        state = k.getState('u-arg')
        stroke = event and event.stroke or None

        if state == 0:
            k.dispatchEvent = event
            # The call should set the label.
            k.setState('u-arg',1,k.universalDispatcher)
            k.repeatCount = 1
        elif state == 1:
            # stroke = k.stroke # Warning: k.stroke is always Alt-u
            char = event and event.char or ''
            # g.trace(state,char)
            if char == 'Escape':
                k.keyboardQuit()
            elif char == k.universalArgKey:
                k.repeatCount = k.repeatCount * 4
            elif char.isdigit() or char == '-':
                k.updateLabel(event)
            elif char in (
                'Alt_L','Alt_R',
                'Control_L','Control_R',
                'Meta_L','Meta_R',
                'Shift_L','Shift_R',
            ):
                k.updateLabel(event)
            else:
                # *Anything* other than C-u, '-' or a numeral is taken to be a command.
                val = k.getLabel(ignorePrompt=True)
                try:                n = int(val) * k.repeatCount
                except ValueError:  n = 1
                k.clearState()
                event = k.dispatchEvent
                k.executeNTimes(event,n)
                k.keyboardQuit()
        elif state == 2:
            k.doControlU(event,stroke)
    #@+node:ekr.20061031131434.202: *4* k.executeNTimes
    def executeNTimes (self,event,n):

        trace = False and not g.unitTesting
        c,k = self.c,self

        w = event and event.widget

        stroke = event and event.stroke or None
        if not stroke: return

        if stroke == k.fullCommandKey:
            for z in range(n):
                k.fullCommand(event)
        else:
            si = k.getPaneBinding(stroke,event and event.widget)
            if si:
                assert g.isShortcutInfo(si),si
                if trace: g.trace('repeat',n,'method',si.func.__name__,
                    'stroke',stroke,'widget',w)
                for z in range(n):
                    event = g.app.gui.create_key_event(c,None,event,stroke,w)
                    k.masterCommand(commandName=None,event=event,func=si.func,stroke=stroke)
            else:
                for z in range(n):
                    k.masterKeyHandler(event)
    #@+node:ekr.20061031131434.203: *4* doControlU
    def doControlU (self,event,stroke):

        k = self ; c = k.c

        ch = event and event.char or ''

        k.setLabelBlue('Control-u %s' % g.stripBrackets(stroke))

        if ch == '(':
            k.clearState()
            k.resetLabel()
            c.macroCommands.startKbdMacro(event)
            c.macroCommands.callLastKeyboardMacro(event)
    #@-others
#@+node:ekr.20120208064440.10148: ** class ModeController
class ModeController:

    def __init__ (self,c):
        self.c = c
        self.d = {} # Keys are command names, values are modes.
        self.k = c.k
        g.trace(self)

    def __repr__(self):
        return '<ModeController %s>' % self.c.shortFileName()

    __str__ = __repr__

    #@+others
    #@+node:ekr.20120208064440.10161: *3* addModeCommands (ModeController)
    def addModeCommands(self):

        g.trace(self,self.d)

        for mode in self.d.values():
            mode.createModeCommand()
    #@+node:ekr.20120208064440.10163: *3* getMode (ModeController)
    def getMode (self,modeName):

        g.trace(self)

        mode = self.d.get(modeName)
        g.trace(modeName,mode)
        return mode

    #@+node:ekr.20120208064440.10164: *3* makeMode (ModeController)
    def makeMode (self,name,aList):


        mode = ModeInfo(self.c,name,aList)

        g.trace(self,mode.name,mode)
        self.d[mode.name] = mode

    #@-others
#@+node:ekr.20120208064440.10150: ** class ModeInfo
class ModeInfo:

    def __repr__(self):
        return '<ModeInfo %s>' % self.name

    __str__ = __repr__

    #@+others
    #@+node:ekr.20120208064440.10193: *3*  ctor (ModeInfo)
    def __init__ (self,c,name,aList):

        g.trace(name,aList)

        self.c = c
        self.d = {} # The bindings in effect for this mode.
            # Keys are names of (valid) command names, values are ShortcutInfo objects.
        self.entryCommands = []
            # A list of ShortcutInfo objects.
        self.k = c.k
        self.name = self.computeModeName(name)
        self.prompt = self.computeModePrompt(self.name)

        self.init(name,aList)
    #@+node:ekr.20120208064440.10152: *3* computeModeName (ModeInfo)
    def computeModeName (self,name):

        s = name.strip().lower()
        j = s.find(' ')
        if j > -1: s = s[:j]
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
    #@+node:ekr.20120208064440.10156: *3* computeModePrompt (ModeInfo)
    def computeModePrompt (self,name):

        assert name == self.name
        s = 'enter-' + name.replace(' ','-')
        i = s.find('::')
        if i > -1:
            # The prompt is everything after the '::'
            prompt = s[i+2:].strip()
        else:
            prompt = s

        return prompt
    #@+node:ekr.20120208064440.10160: *3* createModeBindings (ModeInfo) (NOT USED)
    ##### k.createModeBindings is used instead????

    def createModeBindings (self,w):

        '''Create mode bindings for w, a text widget.'''

        trace = False and not g.unitTesting
        c,d,k,modeName = self.c,self.d,self.k,self.name
        for commandName in d.keys():
            func = c.commandsDict.get(commandName)
            if not func:
                g.es_print('no such command: %s Referenced from %s' % (
                    commandName,modeName))
                continue
            aList = d.get(commandName,[])
            for si in aList:
                assert g.isShortcutInfo(si),si
                if trace: g.trace(si)
                stroke = si.stroke
                # Important: si.val is canonicalized.
                if stroke and stroke not in ('None','none',None):
                    if trace:
                        g.trace(
                            g.app.gui.widget_name(w), modeName,
                            '%10s' % (stroke),
                            '%20s' % (commandName),
                            si.nextMode)

                    assert g.isStroke(stroke)
                    k.makeMasterGuiBinding(stroke)

                    # Create the entry for the mode in k.masterBindingsDict.
                    # Important: this is similar, but not the same as k.bindKeyToDict.
                    # Thus, we should **not** call k.bindKey here!
                    d2 = k.masterBindingsDict.get(modeName,{})
                    d2 [stroke] = g.ShortcutInfo(
                        kind = 'mode<%s>' % (modeName), # 2012/01/23
                        commandName=commandName,
                        func=func,
                        nextMode=si.nextMode,
                        stroke=stroke)
                    k.masterBindingsDict[modeName] = d2
                    if trace: g.trace(modeName,d2)
    #@+node:ekr.20120208064440.10195: *3* createModeCommand (ModeInfo)
    def createModeCommand (self):

        g.trace(self)

        c,k = self.c,self.k
        key = 'enter-' + self.name.replace(' ','-')

        def enterModeCallback (event=None,self=self):
            self.enterMode()

        c.commandsDict[key] = f = enterModeCallback
        k.inverseCommandsDict [f.__name__] = key

        g.trace('(ModeInfo)',f.__name__,key,'len(c.commandsDict.keys())',len(list(c.commandsDict.keys())))
    #@+node:ekr.20120208064440.10180: *3* enterMode (ModeInfo)
    def enterMode (self):

        g.trace('(ModeInfo)')

        c,k = self.c,self.k
        c.inCommand = False
            # Allow inner commands in the mode.
        event=None ####
        k.generalModeHandler(event,modeName=self.name)
    #@+node:ekr.20120208064440.10153: *3* init (ModeInfo) (Can we check command names here??)
    def init (self,name,dataList):

        '''aList is a list of tuples (commandName,si).'''

        trace = False and not g.unitTesting
        c,d,k,modeName = self.c,self.d,self.c.k,self.name
        for name,si in dataList:

            assert g.isShortcutInfo(si),si
            if not name:
                if trace: g.trace('entry command',si)
                #### An entry command: put it in the special *entry-commands* key.
                #### d.add('*entry-commands*',si)
                self.entryCommands.append(si)
            elif si is not None:
                # A regular shortcut.
                si.pane = modeName
                aList = d.get(name,[])
                for z in aList:
                    assert g.isShortcutInfo(z),z
                # Important: use previous bindings if possible.
                key2,aList2 = c.config.getShortcut(name)
                for z in aList2:
                    assert g.isShortcutInfo(z),z
                aList3 = [z for z in aList2 if z.pane != modeName]
                if aList3:
                    if trace: g.trace('inheriting',[si.val for si in aList3])
                    aList.extend(aList3)
                aList.append(si)
                d[name] = aList
    #@+node:ekr.20120208064440.10158: *3* initMode (ModeInfo)
    def initMode (self):

        trace = False and not g.unitTesting
        c,k = self.c,self.c.k

        ####
        # d = g.app.config.modeCommandsDict.get('enter-'+modeName)
        # if not d:
            # self.badMode(modeName)
            # return
        # else:
            # k.modeBindingsDict = d
            # si = d.get('*command-prompt*')
            # if si:
                # prompt = si.kind # A kludge.
            # else:
                # prompt = modeName
            # if trace: g.trace('modeName',modeName,prompt,'d.keys()',list(d.keys()))

        k.inputModeName = self.name
        k.silentMode = False

        #### aList = d.get('*entry-commands*',[])
        for si in self.entryCommands:
            assert g.isShortcutInfo(si),si
            commandName = si.commandName
            if trace: g.trace('entry command:',commandName)
            k.simulateCommand(commandName)
            # Careful, the command can kill the commander.
            if g.app.quitting or not c.exists: return
            # New in Leo 4.5: a startup command can immediately transfer to another mode.
            if commandName.startswith('enter-'):
                if trace: g.trace('redirect to mode',commandName)
                return

        # Create bindings after we know whether we are in silent mode.
        # w = g.choose(k.silentMode,k.modeWidget,k.w)
        w = k.modeWidget if k.silentMode else k.w
        k.createModeBindings(self.name,self.d,w)
        #### self.createModeBindings(w)
        k.showStateAndMode(prompt=self.name)
    #@-others

#@-others
#@-leo
