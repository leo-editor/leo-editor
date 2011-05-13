#@+leo-ver=5-thin
#@+node:ekr.20061031131434: * @file leoKeys.py
"""Gui-independent keystroke handling for Leo.""" 

#@@language python
#@@tabwidth -4
#@@pagewidth 70

#@+<< imports >>
#@+node:ekr.20061031131434.1: ** << imports >>
import leo.core.leoGlobals as g
import leo.core.leoFrame as leoFrame # to access stringTextWidget class.
import leo.external.codewise as codewise

# This creates a circular dependency.
# We break this by doing the import in k.endCommand.
# import leo.core.leoEditCommands as leoEditCommands

import glob
import inspect
import os
import re
import string
import sys
import time
import types
#@-<< imports >>
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
# ivars:
# 
# c.commandsDict:
#     Keys are emacs command names; values are functions f.
# 
# k.inverseCommandsDict:
#     Keys are f.__name__; values are emacs command names.
# 
# k.bindingsDict:
#     Keys are shortcuts; values are *lists* of g.bunch(func,name,warningGiven)
# 
# k.masterBindingsDict:
#     Keys are scope names: 'all','text',etc. or mode names.
#     Values are dicts:  keys are strokes, values are g.Bunch(commandName,func,pane,stroke)
# 
# k.masterGuiBindingsDict:
#     Keys are strokes; value is a list of widgets for which stroke is bound.
# 
# k.settingsNameDict:
#     Keys are lowercase settings; values are 'real' Tk key specifiers.
#     Important: this table has no inverse.
# 
# not an ivar (computed by k.computeInverseBindingDict):
# 
# inverseBindingDict
#     Keys are emacs command names; values are *lists* of shortcuts.
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
        self.tabName = None # The name of the main completion tab.
        self.verbose = False # True: print all members, regardless of how many there are.
        self.w = None # The widget that gets focus after autocomplete is done.
        
        # Codewise pre-computes...
        self.codewiseSelfList = []
            # The (global) completions for "self."
        self.codewiseDict = {}
            # Keys are prefixes, values are completion lists.
            # This is cleared by start, so that it relates to the current postition.
        
        # Options...
        self.auto_tab       = c.config.getBool('auto_tab_complete',False)
        self.use_codewise   = c.config.getBool('use_codewise',False) and not self.is_leo_source_file()
        self.use_qcompleter = c.config.getBool('use_qcompleter',False)
            # True: show results in autocompleter tab.
            # False: show results in a QCompleter widget.
    #@+node:ekr.20061031131434.8: *3* Top level (autocompleter)
    #@+node:ekr.20061031131434.9: *4* autoComplete
    def autoComplete (self,event=None,force=False):

        '''An event handler called from k.masterKeyHanderlerHelper.'''

        trace = False and not g.unitTesting
        c = self.c ; k = self.k ; state = k.unboundKeyAction
        gui = g.app.gui
        w = gui.eventWidget(event) or c.get_focus()

        self.force = force
        
        if not state in ('insert','overwrite'):
            if trace: g.trace('not in insert/overwrite mode')
            return 'break'

        # First, handle the invocation character as usual.
        if not force:
            # Ctrl-period does *not* insert a period.
            if trace: g.trace('not force')
            k.masterCommand(event,func=None,stroke=None,commandName=None)

        # Allow autocompletion only in the body pane.
        if not c.widget_name(w).lower().startswith('body'):
            if trace: g.trace('not body')
            return 'break'

        self.language = g.scanForAtLanguage(c,c.p)
        if w and self.language == 'python' and (k.enable_autocompleter or force):
            if trace: g.trace('starting')
            self.w = w
            self.start(event)
        else:
            if trace: g.trace('not enabled')

        return 'break'
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
        w = g.app.gui.eventWidget(event)
        if not w: return
        is_headline = c.widget_name(w).startswith('head')

        # Insert the calltip if possible, but not in headlines.
        if (k.enable_calltips or force) and not is_headline:
            self.w = w
            self.calltip()
        else:
            # Just insert the invocation character as usual.
            k.masterCommand(event,func=None,stroke=None,commandName=None)

        return 'break'
    #@+node:ekr.20061031131434.14: *4* showCalltipsForce
    def showCalltipsForce (self,event=None):

        '''Show the calltips at the cursor, even if calltips are not presently enabled.'''

        return self.showCalltips(event,force=True)
    #@+node:ekr.20061031131434.15: *4* showAutocompleter/CalltipsStatus
    def showAutocompleterStatus (self):
        '''Show the autocompleter status.'''

        k = self.k
        if not g.unitTesting:
            s = '%sautocompleter %s' % (
                g.choose(self.use_codewise,'codewise ',''),
                g.choose(k.enable_autocompleter,'On','Off'))
            g.es(s,color='red')

    def showCalltipsStatus (self):
        '''Show the autocompleter status.'''
        k = self.k
        if not g.unitTesting:
            s = 'calltips %s' % g.choose(k.enable_calltips,'On','Off')
            g.es(s,color='red')
    #@+node:ekr.20061031131434.16: *3* Helpers
    #@+node:ekr.20110512212836.14469: *4* abort, exit & finish
    #@+node:ekr.20061031131434.17: *5* abort
    def abort (self):

        k = self.k
        k.keyboardQuit(event=None,setDefaultStatus=False)
            # Stay in the present input state.
        self.exit(restore=True)
    #@+node:ekr.20110512212836.14470: *5* exit
    def exit (self,restore=False): # Called from keyboard-quit.

        trace = False and not g.unitTesting
        if trace: g.trace('restore: %s' % (restore),g.callers())

        k = self ; c = k.c 
        w = self.w or c.frame.body.bodyCtrl
        for name in (self.tabName,'Modules','Info'):
            c.frame.log.deleteTab(name)
            
        # Restore the selection range that may have been destroyed by changing tabs.
        c.widgetWantsFocusNow(w)
        i,j = w.getSelectionRange()
        w.setSelectionRange(j,j,insert=j)
    #@+node:ekr.20061031131434.34: *5* finish
    def finish (self):

        c = self.c ; k = c.k

        k.keyboardQuit(event=None,setDefaultStatus=False)
            # Stay in the present input state.

        for name in (self.tabName,'Modules','Info'):
            c.frame.log.deleteTab(name)

        c.frame.body.onBodyChanged('Typing')
        c.recolor()
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
        c = self.c ; k = self.k ; gui = g.app.gui
        tag = 'auto-complete' ; state = k.getState(tag)
        ch = gui.eventChar(event)
        keysym = gui.eventKeysym(event)

        if trace: g.trace('state: %s, ch: %s, keysym: %s' % (
            state,repr(ch),repr(keysym)))

        if state == 0:
            c.frame.log.clearTab(self.tabName)
            common_prefix,prefix,tabList = self.compute_completion_list()
            if tabList:
                k.setState(tag,1,handler=self.auto_completer_state_handler)
            else:
                self.abort()
        elif keysym in (' ','Return'):
            self.finish()
        elif keysym == 'Escape':
            self.abort()
        elif keysym == 'Tab':
            self.doTabCompletion()
        elif keysym in ('\b','BackSpace'):
            self.do_backspace()
        elif keysym == '.':
            self.insert_string('.')
            self.compute_completion_list()
        elif keysym == '?':
            self.info()
        elif keysym == '!':
            # Toggle between verbose and brief listing.
            self.verbose = not self.verbose
            kind = g.choose(self.verbose,'ON','OFF')
            c.frame.putStatusLine('verbose completions %s' % (
                kind),color='red')
            self.compute_completion_list()
        elif ch == 'Down' and hasattr(self,'onDown'):
            self.onDown()
        elif ch == 'Up' and hasattr(self,'onUp'):
            self.onUp()
        elif ch and ch in string.printable:
            self.insert_general_char(ch,keysym)
        else:
            # if trace: g.trace('ignore',repr(ch))
            return 'do-standard-keys'
    #@+node:ekr.20061031131434.20: *4* calltip & helpers
    def calltip (self):
        
        '''Show the calltips for the present prefix.
        ch is '(' if the user has just typed it.
        '''

        trace = False and not g.unitTesting

        c = self.c
        obj,prefix = self.get_object()
        
        if obj:
            self.calltip_success(prefix,obj)
        else:
            self.calltip_fail(prefix)
            
        self.finish()
        c.frame.clearStatusLine()
        c.widgetWantsFocusNow(self.w)
    #@+node:ekr.20110512090917.14468: *5* calltip_fail
    def calltip_fail(self,prefix):
        
        '''Evaluation of prefix failed.'''
        
       
        if not g.unitTesting:
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

        # Clean s and insert it.
        if g.match(s,1,'self,'):
            s = s[0] + s[6:].strip()
        elif g.match_word(s,1,'self'):
            s = s[0] + s[5:].strip()

        self.insert_string(s)
    #@+node:ekr.20061031131434.28: *4* compute_completion_list
    def compute_completion_list (self):

        trace = False and not g.unitTesting
        verbose = False
        
        prefix = self.get_autocompleter_prefix()
        options = self.get_completions(prefix)
        
        tabList,common_prefix = g.itemsMatchingPrefixInList(
            prefix,options,matchEmptyPrefix=False)

        if not common_prefix:
            tabList,common_prefix = g.itemsMatchingPrefixInList(
                prefix,options,matchEmptyPrefix=True)
                
        if trace:
            g.trace('prefix: %s, common: %s, len(tabList): %s' % (
                repr(prefix),repr(common_prefix),len(tabList)))
            if verbose: g.trace('options[:10]...\n',
                g.listToString(options[:10],sort=True))
            
        if tabList:
            self.show_completion_list(common_prefix,prefix,tabList)
        
        return common_prefix,prefix,tabList
    #@+node:ekr.20061031131434.29: *4* do_backspace
    def do_backspace (self):

        '''Delete the character and recompute the completion list.'''
        
        c,w = self.c,self.w
        c.bodyWantsFocusNow()
        
        i = w.getInsertPoint()
        if i <= 0:
            self.abort()
            return

        w.delete(i-1,i)
        w.setInsertPoint(i-1)
        
        if i <= 1:
            self.abort()
        else:
            # Update the list, but do not abort here.
            common_prefix,prefix,tabList = self.compute_completion_list()
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
        
        if self.use_codewise:
            
            d = self.codewiseDict
            
            if not self.codewiseSelfList:
                # Get the completions for '.self'
                # Strip the leading '.self' from all entries.
                aList = self.get_codewise_completions('self.')
                self.codewiseSelfList = [z[5:] for z in aList]
                d ['self.'] = self.codewiseSelfList
                # g.trace(g.listToString(self.codewiseSelfList[:50]))

            # Use the cached list if it exists.
            # This speeds the handling of backspace.
            aList = d.get(prefix)
            if not aList:
                aList = self.get_codewise_completions(prefix)
                d [prefix] = aList
            return aList
        else:
            return self.get_leo_completions(prefix)
    #@+node:ekr.20110510120621.14539: *5* get_codewise_completions & helpers
    def get_codewise_completions(self,prefix):
        
        '''Use codewise to generate a list of hits.'''

        trace = False and not g.unitTesting
        c = self.c

        m = re.match(r"(\S+(\.\w+)*)\.(\w*)$", prefix) ### was head.lstrip())
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
                hits = self.lookup_functions(func) ### Was s
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
            return 'class',['baseCommands']
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

    def lookup_methods(self,aList,prefix): ### prefix not used, only aList[0] used.
        
        aList = codewise.cmd_members([aList[0]])
        hits = [z.split(None,1) for z in aList if z.strip()]
        return self.clean(hits)

    def lookup_modules (self,aList,prefix): ### prefix not used, only aList[0] used.
        
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
            g.es('no docstring for',word,color='blue')
    #@+node:ekr.20110510071925.14586: *4* init_qcompleter
    def init_qcompleter (self):
        
        trace = False and not g.unitTesting

        # Compute the prefix and the list of options.
        prefix = self.get_autocompleter_prefix()
        options = self.get_completions(prefix)

        if trace: g.trace('prefix: %s, len(options): %s' % (repr(prefix),len(options)))

        if options:
            w = self.c.frame.body.bodyCtrl.widget # A LeoQTextBrowser.
            self.qcompleter = w.initCompleter(prefix,options)
        else:
            g.es('No completions',color='blue')
            self.abort()
    #@+node:ekr.20110511133940.14552: *4* init_tabcompleter
    def init_tabcompleter (self,event=None):
        
        trace = False and not g.unitTesting
            
        # Compute the prefix and the list of options.
        prefix = self.get_autocompleter_prefix()
        options = self.get_completions(prefix)

        if options:
            self.clearTabName() # Creates the tabbed pane.
            self.auto_completer_state_handler(event)
        else:
            g.es('No completions',color='blue')
            self.abort()
    #@+node:ekr.20061031131434.39: *4* insert_general_char
    def insert_general_char (self,ch,keysym):

        trace = False and not g.unitTesting
        k = self.k ; w = self.w
        
        if trace: g.trace(repr(ch))

        if g.isWordChar(ch):
            self.insert_string(ch)
            common_prefix,prefix,aList = self.compute_completion_list()
            if not aList:
                if 0: # Annoying. Let the user type "by hand".
                    # Delete the character we just inserted.
                    self.do_backspace()
            elif self.auto_tab and len(common_prefix) > len(prefix):
                extend = common_prefix[len(prefix):]
                if trace: g.trace('*** extend',extend)
                ins = w.getInsertPoint()
                w.insert(ins,extend)
        else:
            if ch == '(' and k.enable_calltips:
                # This calls self.finish if the '(' is valid.
                self.calltip()
            else:
                self.insert_string(ch)
                self.finish()
    #@+node:ekr.20061031131434.31: *4* insert_string
    def insert_string (self,s):

        '''Insert s at the insertion point.'''

        c = self.c ; w = self.w
        
        c.widgetWantsFocusNow(w)
        j = w.getInsertPoint()
        w.insert(j,s)
       
        c.frame.body.onBodyChanged('Typing')
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

        g.es(*args,**keys)
    #@+node:ekr.20110511133940.14561: *4* show_completion_list
    def show_completion_list (self,common_prefix,prefix,tabList):
        
        c = self.c
        
        def clean(aList,header):
            return [
                g.choose(z.startswith(header),z[len(header)+1:],z)
                for z in tabList]
        
        c.widgetWantsFocus(self.w)
        aList = common_prefix.split('.')
        header = '.'.join(aList[:-1])
        # g.trace('header',header)

        if not self.verbose and len(tabList) > 20:
            # Show the possible starting letters,
            # but only if there are more than one.
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
                tabList.append('\ncommon prefix: %s' % (common_prefix))
            else:
                tabList = clean(tabList,header)
                if len(tabList) > 10:
                    tabList.append('\ncommon prefix: %s' % (common_prefix))
        else:
            tabList = clean(tabList,header)

        c.frame.log.clearTab(self.tabName)
            # Creates the tab if necessary.
            
        s = '\n'.join(tabList)
        self.put('',s,tabName=self.tabName)
    #@+node:ekr.20061031131434.46: *4* start
    def start (self,event):
        
        self.codewiseDict = {}

        if self.use_qcompleter:
            self.init_qcompleter()
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
#@+node:ekr.20061031131434.74: ** class keyHandlerClass
class keyHandlerClass:

    '''A class to support emacs-style commands.'''

    # Gui-independent class vars.

    global_killbuffer = []
        # Used only if useGlobalKillbuffer arg to Emacs ctor is True.
        # Otherwise, each Emacs instance has its own local kill buffer.

    global_registers = {}
        # Used only if useGlobalRegisters arg to Emacs ctor is True.
        # Otherwise each Emacs instance has its own set of registers.

    lossage = []
        # A case could be made for per-instance lossage, but this is not supported.

    #@+others
    #@+node:ekr.20061031131434.75: *3*  k.Birth
    #@+node:ekr.20061031131434.76: *4*  ctor (keyHandler)
    def __init__ (self,c,useGlobalKillbuffer=False,useGlobalRegisters=False):

        '''Create a key handler for c.
        c.frame.miniBufferWidget is a Tk.Label.

        useGlobalRegisters and useGlobalKillbuffer indicate whether to use
        global (class vars) or per-instance (ivars) for kill buffers and registers.'''

        self.c = c
        self.dispatchEvent = None
        self.inited = False # Set at end of finishCreate.
        self.w = c.frame.miniBufferWidget
        self.new_bindings = True
        self.useGlobalKillbuffer = useGlobalKillbuffer
        self.useGlobalRegisters = useGlobalRegisters

        # Generalize...
        self.x_hasNumeric = ['sort-lines','sort-fields']

        self.altX_prompt = 'full-command: '

        # These must be defined here to avoid memory leaks.
        getBool = c.config.getBool
        getColor = c.config.getColor
        self.enable_autocompleter           = getBool('enable_autocompleter_initially')
        self.enable_calltips                = getBool('enable_calltips_initially')
        self.ignore_caps_lock               = getBool('ignore_caps_lock')
        self.ignore_unbound_non_ascii_keys  = getBool('ignore_unbound_non_ascii_keys')
        self.minibuffer_background_color    = getColor('minibuffer_background_color') or 'lightblue'
        self.minibuffer_warning_color       = getColor('minibuffer_warning_color') or 'lightgrey'
        self.minibuffer_error_color         = getColor('minibuffer_error_color') or 'red'
        self.swap_mac_keys                  = getBool('swap_mac_keys')
        self.trace_bind_key_exceptions      = getBool('trace_bind_key_exceptions')
        self.trace_masterClickHandler       = getBool('trace_masterClickHandler')
        self.traceMasterCommand             = getBool('trace_masterCommand')
        self.trace_masterKeyHandler         = getBool('trace_masterKeyHandler')
        self.trace_masterKeyHandlerGC       = getBool('trace_masterKeyHandlerGC')
        self.trace_key_event                = getBool('trace_key_event')
        self.trace_minibuffer               = getBool('trace_minibuffer')
        self.warn_about_redefined_shortcuts = getBool('warn_about_redefined_shortcuts')
        # Has to be disabled (default) for AltGr support on Windows
        self.enable_alt_ctrl_bindings       = c.config.getBool('enable_alt_ctrl_bindings')
        #@+<< define externally visible ivars >>
        #@+node:ekr.20061031131434.78: *5* << define externally visible ivars >>
        self.abbrevOn = False # True: abbreviations are on.
        self.arg = '' # The value returned by k.getArg.
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
        self.regx = g.bunch(iter=None,key=None)
        self.repeatCount = None
        self.previousSelection = None # A hack for middle-button paste: set by masterClickHandler, used by pasteText.
        self.state = g.bunch(kind=None,n=None,handler=None)
        #@-<< define externally visible ivars >>
        #@+<< define internal ivars >>
        #@+node:ekr.20061031131434.79: *5* << define internal ivars >>
        self.abbreviationsDict = {} # Abbreviations created by @alias nodes.

        # Previously defined bindings.
        self.bindingsDict = {}
            # Keys are Tk key names, values are lists of g.bunch(pane,func,commandName)
        # Previously defined binding tags.
        self.bindtagsDict = {}
            # Keys are strings (the tag), values are 'True'
        self.masterBindingsDict = {}
            # Keys are scope names: 'all','text',etc. or mode names.
            # Values are dicts: keys are strokes, values are g.bunch(commandName,func,pane,stroke)
        self.masterGuiBindingsDict = {}
            # Keys are strokes; value is True;

        # Special bindings for k.fullCommand.
        self.mb_copyKey = None
        self.mb_pasteKey = None
        self.mb_cutKey = None
        self.mb_help = False

        self.abortAllModesKey = None
        self.fullCommandKey = None
        self.universalArgKey = None

        # Keepting track of the characters in the mini-buffer.
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

        # For onIdleTime
        self.idleCount = 0

        # For modes
        self.afterGetArgState = None
        self.argTabList = []
        self.getArgEscapes = []
        self.modeBindingsDict = {}
        self.modeWidget = None
        self.silentMode = False

        # The actual values are set later in k.finishCreate.
        self.command_mode_bg_color = 'white'
        self.command_mode_fg_color = 'black'
        self.insert_mode_bg_color = 'white'
        self.insert_mode_fg_color = 'black'
        self.overwrite_mode_bg_color = 'white'
        self.overwrite_mode_fg_color = 'black'
        #@-<< define internal ivars >>

        self.defineTkNames()
        self.defineSpecialKeys()
        self.defineSingleLineCommands()
        self.defineMultiLineCommands()
        fn = c.shortFileName()
        self.autoCompleter = AutoCompleterClass(self)
        self.qcompleter = None # Set by AutoCompleter.start.
        self.setDefaultUnboundKeyAction()
        self.setDefaultEditingAction() # 2011/02/09
    #@+node:ekr.20061031131434.80: *4* k.finishCreate & helpers
    def finishCreate (self):

        '''Complete the construction of the keyHandler class.
        c.commandsDict has been created when this is called.'''

        k = self ; c = k.c
        # g.trace('keyHandler')
        k.createInverseCommandsDict()

        # Important: bindings exist even if c.showMiniBuffer is False.
        k.makeAllBindings()

        # Set mode colors used by k.setInputState.
        bg = c.config.getColor('body_text_background_color') or 'white'
        fg = c.config.getColor('body_text_foreground_color') or 'black'

        k.command_mode_bg_color = c.config.getColor('command_mode_bg_color') or bg
        k.command_mode_fg_color = c.config.getColor('command_mode_fg_color') or fg
        k.insert_mode_bg_color = c.config.getColor('insert_mode_bg_color') or bg
        k.insert_mode_fg_color = c.config.getColor('insert_mode_fg_color') or fg
        k.overwrite_mode_bg_color = c.config.getColor('overwrite_mode_bg_color') or bg
        k.overwrite_mode_fg_color = c.config.getColor('overwrite_mode_fg_color') or fg
        k.unselected_body_bg_color = c.config.getColor('unselected_body_bg_color') or bg
        k.unselected_body_fg_color = c.config.getColor('unselected_body_fg_color') or bg    

        # g.trace(k.insert_mode_bg_color,k.insert_mode_fg_color)

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
    #@+node:ekr.20110209093958.15413: *4* setDefaultEditingKeyAction (New)
    def setDefaultEditingAction (self):

        k = self ; c = k.c

        action = c.config.getString('default_editing_state') or 'insert'
        action.lower()

        if action not in ('command','insert','overwrite'):
            g.trace('ignoring default_editing_state: %s' % (action))
            action = 'insert'

        self.defaultEditingAction = action
    #@+node:ekr.20070123143428: *4* k.defineTkNames
    def defineTkNames (self):

        k = self

        # These names are used in Leo's core *regardless* of the gui actually in effect.
        # The gui is responsible for translating gui-dependent keycodes into these values.
        k.tkNamesList = (
            'BackSpace','Begin','Break',
            'Caps_Lock','Clear',
            'Delete','Down',
            'End','Escape',
            'F1','F2','F3','F4','F5','F6','F7','F8','F9','F10','F11','F12',
            'Home',
            'Left','Linefeed',
            'Next','Num_Lock',
            'Prior',
            'Return','Right',
            'Tab',
            'Up',
            # 'space',
        )

        # These keys settings that may be specied in leoSettings.leo.
        # Keys are lowercase, so that case is not significant *for these items only* in leoSettings.leo.
        k.settingsNameDict = {
            'bksp'    : 'BackSpace',
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
    # same as what is passed to Tk. Case is significant. Note: the Tk
    # documentation states that not all of these may be available on all
    # platforms.
    # 
    # Num_Lock, Pause, Scroll_Lock, Sys_Req,
    # KP_Add, KP_Decimal, KP_Divide, KP_Enter, KP_Equal,
    # KP_Multiply, KP_Separator,KP_Space, KP_Subtract, KP_Tab,
    # KP_F1,KP_F2,KP_F3,KP_F4,
    # KP_0,KP_1,KP_2,KP_3,KP_4,KP_5,KP_6,KP_7,KP_8,KP_9,
    # Insert
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
    #@+node:ekr.20070123085931: *4* k.defineSpecialKeys
    def defineSpecialKeys (self):

        '''Define k.guiBindNamesDict and k.guiBindNamesInverseDict.

        Important: all gui's use these dictionaries because bindings in
        leoSettings.leo use these representations.'''

        k = self

        # g.trace('base keyHandler')

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

    #@+node:ekr.20061101071425: *4* oops
    def oops (self):

        g.trace('Should be defined in subclass:',g.callers(4))
    #@+node:ekr.20061031131434.88: *3* k.Binding
    #@+node:ekr.20061031131434.89: *4* bindKey
    def bindKey (self,pane,shortcut,callback,commandName,_hash=None,modeFlag=False):

        '''Bind the indicated shortcut (a Tk keystroke) to the callback.

        No actual gui bindings are made: only entries in k.masterBindingsDict.
        
        _hash gives the source of the binding.
        
        '''

        trace = False and not g.unitTesting
        k = self ; c = k.c

        if not shortcut:
            # g.trace('No shortcut for %s' % commandName)
            return False
        #@+<< give warning and return if we try to bind to Enter or Leave >>
        #@+node:ekr.20061031131434.90: *5* << give warning and return if we try to bind to Enter or Leave >>
        if shortcut:
            for s in ('enter','leave'):
                if -1 != shortcut.lower().find(s):
                    g.es_print('ignoring invalid key binding:','%s = %s' % (
                        commandName,shortcut),color='blue')
                    return
        #@-<< give warning and return if we try to bind to Enter or Leave >>
        if pane.endswith('-mode'):
            g.trace('oops: ignoring mode binding',shortcut,commandName,g.callers())
            return False
        bunchList = k.bindingsDict.get(shortcut,[])
        if trace: #  or shortcut == 'Ctrl+q':
            g.trace('%7s %20s %30s %s' % (pane,shortcut,commandName,_hash))
            g.trace(g.callers())
        try:
            k.bindKeyToDict(pane,shortcut,callback,commandName)
            b = g.bunch(pane=pane,func=callback,commandName=commandName,_hash=_hash)
            #@+<< remove previous conflicting definitions from bunchList >>
            #@+node:ekr.20061031131434.92: *5* << remove previous conflicting definitions from bunchList >>
            # b is the bunch for the new binding.

            ### This warning should never happen with the new code in makeBindingsFromCommandsDict.

            if not modeFlag and self.warn_about_redefined_shortcuts:
                
                redefs = [b2 for b2 in bunchList
                    if b2.commandName != commandName and
                        # pane != b2.pane and # 2011/02/11: don't give warning for straight substitution.
                        pane in ('button','all',b2.pane)
                        and not b2.pane.endswith('-mode')]

                if redefs:
                    def pr(commandName,pane,theHash):
                        g.es_print('%30s in %5s from %s' % (commandName,pane,theHash))
                
                    g.warning('shortcut conflict for %s' % c.k.prettyPrintKey(shortcut))
                    pr(commandName,pane,_hash)
                    for z in redefs:
                        pr(z.commandName,z.pane,z._hash)

            if not modeFlag:
                bunchList = [b2 for b2 in bunchList if pane not in ('button','all',b2.pane)]
            #@-<< remove previous conflicting definitions from bunchList >>
            bunchList.append(b)
            shortcut = g.stripBrackets(shortcut.strip())
            k.bindingsDict [shortcut] = bunchList
            return True
        except Exception: # Could be a user error.
            if not g.app.menuWarningsGiven:
                g.es_print('exception binding',shortcut,'to',commandName)
                g.es_exception()
                g.app.menuWarningsGiven = True
            return False

    bindShortcut = bindKey # For compatibility
    #@+node:ekr.20061031131434.93: *4* bindKeyToDict
    def bindKeyToDict (self,pane,stroke,func,commandName):

        k = self
        d =  k.masterBindingsDict.get(pane,{})

        stroke = g.stripBrackets(stroke)

        # if commandName == 'full-command':
            # g.trace('%-4s %-18s %-40s %s' % (
                # pane,repr(stroke),commandName,func and func.__name__),g.callers())

        # New in Leo 4.4.1: Allow redefintions.
        d [stroke] = g.Bunch(commandName=commandName,func=func,pane=pane,stroke=stroke)
        k.masterBindingsDict [pane] = d
    #@+node:ekr.20061031131434.94: *4* bindOpenWith
    def bindOpenWith (self,shortcut,name,data):

        '''Register an open-with command.'''

        k = self ; c = k.c

        # The first parameter must be event, and it must default to None.
        def openWithCallback(event=None,c=c,data=data):
            return c.openWith(data=data)

        # Use k.registerCommand to set the shortcuts in the various binding dicts.
        commandName = 'open-with-%s' % name.lower()
        k.registerCommand(commandName,shortcut,openWithCallback,pane='all',verbose=False)
    #@+node:ekr.20061031131434.95: *4* checkBindings
    def checkBindings (self):

        '''Print warnings if commands do not have any @shortcut entry.
        The entry may be `None`, of course.'''

        k = self ; c = k.c

        if not c.config.getBool('warn_about_missing_settings'): return

        for name in sorted(c.commandsDict):
            abbrev = k.abbreviationsDict.get(name)
            key = c.frame.menu.canonicalizeMenuName(abbrev or name)
            key = key.replace('&','')
            if not g.app.config.exists(c,key,'shortcut'):
                if abbrev:
                     g.trace('No shortcut for abbrev %s -> %s = %s' % (
                        name,abbrev,key))
                else:
                    g.trace('No shortcut for %s = %s' % (name,key))
    #@+node:ekr.20070218130238: *4* dumpMasterBindingsDict
    def dumpMasterBindingsDict (self):

        k = self ; d = k.masterBindingsDict

        g.pr('\nk.masterBindingsDict...\n')

        for key in sorted(d):
            g.pr(key, '-' * 40)
            d2 = d.get(key)
            for key2 in sorted(d2):
                b = d2.get(key2)
                g.pr('%20s %s' % (key2,b.commandName))
    #@+node:ekr.20061031131434.96: *4* k.completeAllBindingsForWidget
    def completeAllBindingsForWidget (self,w):

        k = self ; d = k.bindingsDict

        # g.trace('w',w,'Alt+Key-4' in d)

        for stroke in d:
            k.makeMasterGuiBinding(stroke,w=w)
    #@+node:ekr.20061031131434.97: *4* k.completeAllBindings
    def completeAllBindings (self,w=None):

        '''New in 4.4b3: make an actual binding in *all* the standard places.

        The event will go to k.masterKeyHandler as always, so nothing really changes.
        except that k.masterKeyHandler will know the proper stroke.'''

        # g.trace(w)

        k = self
        for stroke in k.bindingsDict:
            k.makeMasterGuiBinding(stroke,w=w)
    #@+node:ekr.20061031131434.98: *4* k.makeAllBindings
    def makeAllBindings (self):

        k = self ; c = k.c

        # g.trace(c.fileName(),g.callers())

        k.bindingsDict = {}
        k.addModeCommands() 
        k.makeBindingsFromCommandsDict()
        k.initSpecialIvars()
        k.initAbbrev()
        c.frame.body.createBindings()
        c.frame.log.setTabBindings('Log')
        if c.frame.statusLine: c.frame.statusLine.setBindings()
        c.frame.tree.setBindings()
        c.frame.setMinibufferBindings()
        k.completeAllBindings()
        k.checkBindings()
    #@+node:ekr.20061031131434.99: *4* k.initAbbrev
    def initAbbrev (self):

        k = self ; c = k.c ; d = c.config.getAbbrevDict()
        if d:
            for key in d:
                commandName = d.get(key)
                if commandName.startswith('press-') and commandName.endswith('-button'):
                    pass # Must be done later in k.registerCommand.
                else:
                    self.initOneAbbrev(commandName,key)

    def initOneAbbrev (self,commandName,key):
        k = self ; c = k.c
        if c.commandsDict.get(key):
            g.trace('ignoring duplicate abbrev: %s',key)
        else:
            func = c.commandsDict.get(commandName)
            if func:
                # g.trace(key,commandName,func.__name__)
                c.commandsDict [key] = func
                # k.inverseCommandsDict[func.__name__] = key
            else:
                g.es_print('bad abbrev:',key,'unknown command name:',commandName,color='blue')
    #@+node:ekr.20061031131434.100: *4* addModeCommands (enterModeCallback)
    def addModeCommands (self):

        '''Add commands created by @mode settings to c.commandsDict and k.inverseCommandsDict.'''

        k = self ; c = k.c
        d = g.app.config.modeCommandsDict # Keys are command names: enter-x-mode.

        # Create the callback functions and update c.commandsDict and k.inverseCommandsDict.
        for key in d:

            def enterModeCallback (event=None,name=key):
                k.enterNamedMode(event,name)

            c.commandsDict[key] = f = enterModeCallback
            k.inverseCommandsDict [f.__name__] = key
            # g.trace(f.__name__,key)
    #@+node:ekr.20061031131434.101: *4* initSpecialIvars
    def initSpecialIvars (self):

        '''Set ivars for special keystrokes from previously-existing bindings.'''

        k = self ; c = k.c
        trace = False or c.config.getBool('trace_bindings_verbose')
        warn  = c.config.getBool('warn_about_missing_settings')

        for ivar,commandName in (
            ('fullCommandKey',  'full-command'),
            ('abortAllModesKey','keyboard-quit'),
            ('universalArgKey', 'universal-argument'),
        ):
            junk, bunchList = c.config.getShortcut(commandName)
            bunchList = bunchList or [] ; found = False
            for pane in ('text','all'):
                for bunch in bunchList:
                    if bunch.pane == pane:
                        stroke = k.strokeFromSetting(bunch.val)
                        if trace: g.trace(commandName,stroke)
                        setattr(k,ivar,stroke) ; found = True ;break
            if not found and warn:
                g.trace('no setting for %s' % commandName)
    #@+node:ekr.20061031131434.102: *4* makeBindingsFromCommandsDict & helper
    def makeBindingsFromCommandsDict (self):

        '''Add bindings for all entries in c.commandDict.'''

        trace = False and not g.unitTesting
        k = self ; c = k.c
        
        # Step 1: Create d2.
        # Keys are strokes. Values are lists of bunches b with b.val equal to the stroke.
        d = c.commandsDict ; d2 = {} 
        for commandName in sorted(d):
            command = d.get(commandName)
            key, bunchList = c.config.getShortcut(commandName)
            # if commandName == 'move-outline-down': g.trace(bunchList)
            for b in bunchList:
                # Important: regularize the binding value here.
                val = k.shortcutFromSetting(b.val)
                b.commandName = commandName
                aList = d2.get(val,[])
                aList.append(b)
                d2[val] = aList

        # g.trace(list(d2.keys()))
        
        # Step 2: Remove overridden entries from the bunchlist for each stroke.
        if self.new_bindings:
            for stroke in sorted(d2):
                aList = d2.get(stroke)
                aList = self.mergeShortcutList(aList,stroke)
                d2 [stroke] = aList

        # Step 3: make the bindings.
        if 1: # New code
            for stroke in sorted(d2):
                aList = d2.get(stroke)
                # if stroke == 'Ctrl+q': g.trace('***',stroke,aList)
                for bunch in aList:
                    commandName = bunch.commandName
                    command = c.commandsDict.get(commandName)
                    _hash = bunch.get('_hash') # 2011/02/10
                    pane = bunch.pane
                    if trace and not _hash:
                        g.trace('**** no hash for',commandName)
                    if stroke and not pane.endswith('-mode'):
                        k.bindKey(pane,stroke,command,commandName,_hash=_hash)
        else: ### old code
            d = c.commandsDict
            for commandName in sorted(d):
                command = d.get(commandName)
                key, bunchList = c.config.getShortcut(commandName)
                # if commandName in ('full-command'): g.trace(key,bunchList)
                for bunch in bunchList:
                    accel = bunch.val ; pane = bunch.pane
                    _hash = bunch.get('_hash') # 2011/02/10
                    if trace and not _hash: g.trace('**** no hash for',commandName)
                    # if pane.endswith('-mode'): g.trace('skipping',shortcut,commandName)
                    if accel and not pane.endswith('-mode'):
                        shortcut = k.shortcutFromSetting(accel)
                        k.bindKey(pane,shortcut,command,commandName,_hash=_hash)

        # g.trace(g.listToString(sorted(k.bindingsDict))
        # g.trace('Ctrl+g',k.bindingsDict.get('Ctrl+g'))
    #@+node:ekr.20110211094454.15414: *5* mergeShortcutList
    def mergeShortcutList (self,aList,stroke): # stroke is for debugging.

        '''aList is a list of binding bunches for stroke.
        
        Return a new list consisting only of bindings from the highest priority .leo file.'''
        
        # Find the higest priority hash.
        trace = False and not g.unitTesting
        verbose = False
        k = self.c.k
        sList,mList,fList = [],[],[]
        # if stroke == 'Alt-F4': g.pdb()
        for b in aList:
            _hash = b.get('_hash','<no hash>')
            if _hash.endswith('myleosettings.leo'):
                mList.append(b)
            elif _hash.endswith('leosettings.leo'):
                sList.append(b)
            elif _hash.endswith('.leo'):
                fList.append(b)

        result = fList or mList or sList or aList
                
        if trace:
            def pr(stroke,message,aList):
                print('mergeShortcutList: %15s %s %s' % (stroke,message,
                    '...\n'.join(['%15s %5s %s' % (k.shortcutFromSetting(z.val),z.pane,z.commandName) for z in aList])))
            if fList and mList:
                pr(stroke,'ignoring  mList',mList)
                pr(stroke,'retaining fList',fList)
            if fList and sList:
                pr(stroke,'ignoring  sList',sList)
                pr(stroke,'retaining fList',fList)
            elif mList and sList:
                pr(stroke,'ignoring  sList',sList)
                pr(stroke,'retaining mList',mList)

        if trace and verbose and len(result) > 1: g.trace(stroke,result)
        return result
    #@+node:ekr.20061031131434.103: *4* k.makeMasterGuiBinding
    def makeMasterGuiBinding (self,stroke,w=None):

        '''Make a master gui binding for stroke in pane w, or in all the standard widgets.'''

        trace = True and not g.unitTesting
        k = self ; c = k.c ; f = c.frame

        bindStroke = k.tkbindingFromStroke(stroke)

        if stroke.lower().startswith('key'):
            g.trace('stroke',repr(stroke),'bindStroke',repr(bindStroke),g.callers(5))

        if w:
            widgets = [w]
        else:
            # New in Leo 4.5: we *must* make the binding in the binding widget.
            bindingWidget = f.tree and hasattr(f.tree,'bindingWidget') and f.tree.bindingWidget or None
            bodyCtrl = f.body and hasattr(f.body,'bodyCtrl') and f.body.bodyCtrl or None
            canvas = f.tree and hasattr(f.tree,'canvas') and f.tree.canvas   or None
            if 0: # Canvas and bindingWidget bindings are now set in tree.setBindings.
                widgets = (c.miniBufferWidget,bodyCtrl)
            else:
                widgets = (c.miniBufferWidget,bodyCtrl,canvas,bindingWidget)

        # This is the only real key callback.
        def masterBindKeyCallback (event,k=k,stroke=stroke):
            # g.trace(stroke,event.w)
            return k.masterKeyHandler(event,stroke=stroke)

        if 0:
            if stroke.lower().endswith('+s') or stroke.lower().endswith('-s'):
                g.trace(sroke,widgets)
            if stroke in ('s','S'):
                g.trace(stroke,widgets)

        for w in widgets:
            if not w: continue
            # Make the binding only if no binding for the stroke exists in the widget.
            aList = k.masterGuiBindingsDict.get(bindStroke,[])
            if w not in aList:
                aList.append(w)
                k.masterGuiBindingsDict [bindStroke] = aList
                try:
                    c.bind(w,bindStroke,masterBindKeyCallback)
                    # g.trace(stroke,bindStroke,g.app.gui.widget_name(w))
                except Exception:
                    if self.trace_bind_key_exceptions:
                        g.es_exception()
                    g.es_print('exception binding',bindStroke,'to',c.widget_name(w),color='blue')

                    if g.app.unitTesting: raise
    #@+node:ekr.20061031131434.104: *3* k.Dispatching
    #@+node:ekr.20061031131434.105: *4* masterCommand & helpers
    def masterCommand (self,event,func,stroke,commandName=None):

        '''This is the central dispatching method.
        All commands and keystrokes pass through here.'''

        k = self ; c = k.c ; gui = g.app.gui
        trace = (False or k.traceMasterCommand) and not g.unitTesting
        verbose = False
        traceGC = False
        if traceGC: g.printNewObjects('masterCom 1')

        c.setLog()
        c.startRedrawCount = c.frame.tree.redrawCount
        k.stroke = stroke # Set this global for general use.
        keysym = gui.eventKeysym(event)
        ch = gui.eventChar(event)
        w = gui.eventWidget(event)
        state = event and hasattr(event,'state') and event.state or 0
        k.func = func
        k.funcReturn = None # For unit testing.
        commandName = commandName or func and func.__name__ or '<no function>'
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
        special = keysym in specialKeysyms
        interesting = func is not None
        inserted = not special

        if trace: #  and interesting:
            g.trace(
                'stroke: ',stroke,'state:','%x' % state,'ch:',repr(ch),'keysym:',repr(keysym),
                'w:',w and c.widget_name(w),'func:',func and func.__name__
            )

        if inserted:
            # g.trace(stroke,keysym)
            #@+<< add character to history >>
            #@+node:ekr.20061031131434.107: *5* << add character to history >>
            if stroke or len(ch) > 0:
                if len(keyHandlerClass.lossage) > 99:
                    keyHandlerClass.lossage.pop()

                # This looks like a memory leak, but isn't.
                keyHandlerClass.lossage.insert(0,(ch,stroke),)
            #@-<< add character to history >>

        # We *must not* interfere with the global state in the macro class.
        if c.macroCommands.recordingMacro:
            c.macroCommands.startKbdMacro(event)
            return 'break'

        # g.trace(stroke,k.abortAllModesKey)

        if k.abortAllModesKey and stroke == k.abortAllModesKey: # 'Control-g'
            k.keyboardQuit(event)
            k.endCommand(event,commandName)
            return 'break'

        if special: # Don't pass these on.
            return 'break' 

        if 0: # *** This is now handled by k.masterKeyHandler.
            if k.inState():
                val = k.callStateFunction(event) # Calls end-command.
                if val != 'do-func': return 'break'
                g.trace('Executing key outside of mode')

        if k.regx.iter:
            try:
                k.regXKey = keysym
                k.regx.iter.next() # EKR: next() may throw StopIteration.
            except StopIteration:
                pass
            return 'break'

        if k.abbrevOn and ch == ' ':
            expanded = c.abbrevCommands.expandAbbrev(event)
            if expanded: return 'break'

        if func: # Func is an argument.
            if commandName == 'propagate-key-event':
                # Do *nothing* with the event.
                return k.propagateKeyEvent(event)
            elif commandName.startswith('specialCallback'):
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
                # if commandName != 'repeat-complex-command': # 2010/01/11
                    # k.mb_history.insert(0,commandName)
                # if commandName == 'select-all': g.pdb()
                c.doCommand(func,commandName,event=event)
            if c.exists:
                k.endCommand(event,commandName)
                c.frame.updateStatusLine()
            if traceGC: g.printNewObjects('masterCom 2')
            return 'break'
        elif k.inState():
            return 'break' #Ignore unbound keys in a state.
        else:
            if traceGC: g.printNewObjects('masterCom 3')
            val = k.handleDefaultChar(event,stroke)
            if c.exists:
                c.frame.updateStatusLine()
            if traceGC: g.printNewObjects('masterCom 4')
            return val
    #@+node:ekr.20061031131434.109: *5* callKeystrokeFunction (not used)
    def callKeystrokeFunction (self,event):

        '''Handle a quick keystroke function.
        Return the function or None.'''

        k = self
        numberOfArgs, func = k.keystrokeFunctionDict [k.stroke]

        if func:
            func(event)
            commandName = k.inverseCommandsDict.get(func) # Get the emacs command name.
            k.endCommand(event,commandName)

        return func
    #@+node:ekr.20061031131434.110: *5* k.handleDefaultChar
    def handleDefaultChar(self,event,stroke):
        k = self ; c = k.c
        w = event and event.widget
        name = c.widget_name(w)
        trace = False and not g.unitTesting

        if trace: g.trace('widget_name',name,'stroke',stroke)

        if (stroke and
            not stroke.startswith('Alt+Ctrl') and
            not self.enable_alt_ctrl_bindings and
            (stroke.find('Ctrl') > -1 or stroke.find('Alt') > -1)
        ):
            if trace: g.trace('*** ignoring unbound ctrl/alt key:',stroke)
            return 'break'

        if name.startswith('body'):
            action = k.unboundKeyAction
            if action in ('insert','overwrite'):
                c.editCommands.selfInsertCommand(event,action=action)
            else: # Ignore the key
                if trace: g.trace('ignoring',stroke)
            return 'break'
        elif name.startswith('head'):
            c.frame.tree.onHeadlineKey(event)
            return 'break'
        elif name.startswith('canvas'):
            if not stroke: # Not exactly right, but it seems to be good enough.
                c.onCanvasKey(event) # New in Leo 4.4.2
            return 'break'
        elif name.startswith('log'):
            if g.app.gui.guiName() == 'tkinter':
                return None
            else:
                i = w.logCtrl.getInsertPoint()
                if not stroke:
                    stroke = event.stroke # 2010/05/04.
                if stroke.lower() == 'return': stroke = '\n'
                elif stroke.lower() == 'tab': stroke = '\t'
                elif stroke.lower() == 'backspace': stroke = '\b'
                elif stroke.lower() == 'period': stroke = '.'
                w.logCtrl.insert(i,stroke)

                return None
        else:
            # Let the widget handle the event.
            # ch = event and event.char ; g.trace('to tk:',name,repr(stroke))
            return None
    #@+node:ekr.20061031131434.111: *4* fullCommand (alt-x) & helper
    def fullCommand (self,event,specialStroke=None,specialFunc=None,help=False,helpHandler=None):

        '''Handle 'full-command' (alt-x) mode.'''

        k = self ; c = k.c ; gui = g.app.gui
        state = k.getState('full-command')
        helpPrompt = 'Help for command: '
        keysym = gui.eventKeysym(event) ; ch = gui.eventChar(event)
        trace = False or c.config.getBool('trace_modes') ; verbose = True
        if trace: g.trace('state',state,keysym)
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
        elif keysym == 'Ins' or k.isFKey(keysym):
            pass
        elif keysym == 'Escape':
            k.keyboardQuit(event)
        elif keysym == 'Return':
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
        elif keysym in ('Tab','\t'):
            if trace and verbose: g.trace('***Tab')
            k.doTabCompletion(list(c.commandsDict.keys()))
            c.minibufferWantsFocus()
        elif keysym == 'BackSpace':
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

        return 'break'
    #@+node:ekr.20061031131434.112: *5* callAltXFunction
    def callAltXFunction (self,event):

        trace = False and not g.unitTesting
        k = self ; c = k.c ; s = k.getLabel()
        k.mb_tabList = []
        commandName = s[len(k.mb_prefix):].strip()
        func = c.commandsDict.get(commandName)
        k.newMinibufferWidget = None

        # g.trace(func and func.__name__,'mb_event',event.widget.widgetName)
        if func:
            # These must be done *after* getting the command.
            k.clearState()
            k.resetLabel()
            if commandName != 'repeat-complex-command':
                k.mb_history.insert(0,commandName)
            w = event.widget
            if hasattr(w,'permanent') and not w.permanent:
                g.es('Can not execute commands from headlines')
            else:
                c.widgetWantsFocusNow(event.widget) # Important, so cut-text works, e.g.
                func(event)
            k.endCommand(event,commandName)
        else:
            if 1: # Useful.
                if trace: g.trace('*** tab completion')
                k.doTabCompletion(list(c.commandsDict.keys()))
            else: # Annoying.
                k.keyboardQuit(event)
                k.setLabel('Command does not exist: %s' % commandName)
                c.bodyWantsFocus()
    #@+node:ekr.20061031131434.113: *4* k.endCommand
    def endCommand (self,event,commandName):

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
            bodyCtrl = c.frame.body.bodyCtrl
            if not k.inState():
                k.commandName = None

                # Do the import here to break a circular dependency at the top level.
                import leo.core.leoEditCommands as leoEditCommands
                leoEditCommands.initAllEditCommanders(c)
                try:
                    bodyCtrl.tag_delete('color')
                    bodyCtrl.tag_delete('color1')
                except Exception:
                    pass
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
    #@+node:ekr.20061031131434.116: *4* k.show/hide/toggleMinibuffer
    def hideMinibuffer (self,event):
        '''Hide the minibuffer.'''
        k = self ; c = k.c
        c.frame.hideMinibuffer()
        g.es('minibuffer hidden',color='red')
        for commandName in ('show-mini-buffer','toggle-mini-buffer'):
            shortcut = k.getShortcutForCommandName(commandName)
            if shortcut:
                g.es('',commandName,'is bound to:',shortcut)

    def showMinibuffer (self,event):
        '''Show the minibuffer.'''
        k = self ; c = k.c
        c.frame.showMinibuffer()

    def toggleMinibuffer (self,event):
        '''Show or hide the minibuffer.'''
        k = self ; c = k.c
        if c.frame.minibufferVisible:
            k.hideMinibuffer(event)
        else:
            k.showMinibuffer(event)
    #@+node:ekr.20070613133500: *4* k.menuCommandKey
    def menuCommandKey (self,event=None):

        # This method must exist, but it never gets called.
        pass 
    #@+node:ekr.20070613190936: *4* k.propagateKeyEvent
    def propagateKeyEvent (self,event):

        self.oops() # Should be overridden.
    #@+node:ekr.20061031131434.117: *4* negativeArgument (redo?)
    def negativeArgument (self,event):

        '''Prompt for a negative digit argument.'''

        k = self ; state = k.getState('neg-arg')

        if state == 0:
            k.setLabelBlue('Negative Argument: ',protect=True)
            k.setState('neg-arg',1,k.negativeArgument)
        else:
            k.clearState()
            k.resetLabel()
            func = k.negArgFunctions.get(k.stroke)
            if func:
                func(event)

        return 'break'
    #@+node:ekr.20061031131434.118: *4* numberCommand
    def numberCommand (self,event,stroke,number):

        k = self ; k.stroke = stroke ; w = event.widget
        k.universalDispatcher(event)
        g.app.gui.event_generate(w,'<Key>',keysym=number)
        return 'break'

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
    [S] leoSettings.leo
    [ ] default binding
    [F] loaded .leo File
    [M] myLeoSettings.leo
    [@] mode
    '''
        legend = g.adjustTripleString(legend,c.tab_width)

        data = [] ; n1 = 4 ; n2 = 20
        if not d: return g.es('no bindings')
        for key in sorted(d):
            bunchList = d.get(key,[])
            for b in bunchList:
                pane = g.choose(b.pane=='all','',' %s:' % (b.pane))
                s1 = pane
                s2 = k.prettyPrintKey(key,brief=True)
                s3 = b.commandName
                s4 = b.get('_hash','<no hash>')
                n1 = max(n1,len(s1))
                n2 = max(n2,len(s2))
                data.append((s1,s2,s3,s4),)

        # Print keys by type:
        result = []
        result.append('\n'+legend)
        sep = '-' * n1
        for prefix in (
            'Alt+Ctrl+Shift', 'Alt+Shift', 'Alt+Ctrl', 'Alt+Key','Alt',
            'Ctrl+Shift', 'Ctrl', 'Shift',
            'Meta+Ctrl+Shift', 'Meta+Shift', 'Meta+Ctrl', 'Meta+Key','Meta',
            # Meta support
        ):
            data2 = []
            for item in data:
                s1,s2,s3,s4 = item
                if s2.startswith(prefix):
                    data2.append(item)
            # g.es('','%s %s' % (sep, prefix),tabName=tabName)
            result.append('%s %s\n' % (sep, prefix))
            self.printBindingsHelper(result,data2,n1,n2,prefix=prefix)
            # Remove all the items in data2 from data.
            # This must be done outside the iterator on data.
            for item in data2:
                data.remove(item)
        # Print all plain bindings.
        result.append('%s %s\n' % (sep, 'Plain Keys'))
        self.printBindingsHelper(result,data,n1,n2,prefix=None)
        if not g.unitTesting:
            g.es('',''.join(result),tabName=tabName)
        state = k.unboundKeyAction 
        k.showStateAndMode()
        return result # for unit test.
    #@+node:ekr.20061031131434.120: *5* printBindingsHelper
    def printBindingsHelper (self,result,data,n1,n2,prefix):

        n = prefix and len(prefix)+1 or 0 # Add 1 for the '+' after the prefix.

        data1 = [z for z in data if z and z[1] and len(z[1][n:]) == 1]
            # The list of all items with only one character following the prefix.

        data2 = [z for z in data if z and z[1] and len(z[1][n:]) >  1]
            # The list of all other items.

        # This isn't perfect in variable-width fonts.
        for data in (data1,data2):
            data.sort(key=lambda x: x[1])
                # key is a function that extracts args.
            for s1,s2,s3,s4 in data:
                
                # 2011/02/10: Print the source of the binding: s4 is the _hash.
                s4 = s4.lower()
                if s4.endswith('myleosettings.leo'):
                    letter = 'M'
                elif s4.endswith('leosettings.leo'):
                    letter = 'S'
                elif s4.endswith('.leo'):
                    letter = 'F'
                elif s4.find('mode') != -1:
                    letter = '@' # the full mode.
                else:
                    letter = ' '
                
                # g.es('','%*s %*s %s' % (-n1,s1,-(min(12,n2)),s2,s3),tabName='Bindings')
                result.append('%s %*s %*s %s\n' % (letter,-n1,s1,-(min(12,n2)),s2,s3))
    #@+node:ekr.20061031131434.121: *4* printCommands
    def printCommands (self,event=None):

        '''Print all the known commands and their bindings, if any.'''

        k = self ; c = k.c ; tabName = 'Commands'

        c.frame.log.clearTab(tabName)

        inverseBindingDict = k.computeInverseBindingDict()

        data = [] ; n1 = 4 ; n2 = 20
        for commandName in sorted(c.commandsDict):
            dataList = inverseBindingDict.get(commandName,[('',''),])
            for z in dataList:
                pane, key = z
                s1 = pane
                s2 = k.prettyPrintKey(key,brief=True)
                s3 = commandName
                n1 = max(n1,len(s1))
                n2 = max(n2,len(s2))
                data.append((s1,s2,s3),)

        # This isn't perfect in variable-width fonts.
        lines = ['%*s %*s %s\n' % (-n1,s1,-(min(12,n2)),s2,s3) for s1,s2,s3 in data]
        g.es('',''.join(lines),tabName=tabName)
    #@+node:ekr.20061031131434.122: *4* repeatComplexCommand & helper
    def repeatComplexCommand (self,event):

        '''Repeat the previously executed minibuffer command.'''
        k = self
        if k.mb_history:
            k.setState('last-full-command',1,handler=k.repeatComplexCommandHelper)
            k.setLabelBlue("Redo: %s" % str(k.mb_history[0]))
        else:
            g.es('no previous command',color='blue')
        return 'break'

    def repeatComplexCommandHelper (self,event):

        k = self ; c = k.c ; gui = g.app.gui

        keysym = gui.eventKeysym(event)
        # g.trace('state',k.state.kind,'event',repr(event),g.callers())
        if keysym == 'Return' and k.mb_history:
        # if k.mb_history:
            last = k.mb_history [0]
            k.resetLabel()
            k.clearState() # Bug fix.
            c.commandsDict [last](event)
            return 'break'
        else:
            # g.trace('oops')
            return k.keyboardQuit(event)
    #@+node:ekr.20061031131434.123: *4* set-xxx-State
    def setCommandState (self,event):
        '''Enter the 'command' editing state.'''
        # g.trace(g.callers())
        k = self
        k.setInputState('command')
        # This command is also valid in headlines.
        # k.c.bodyWantsFocus()
        k.showStateAndMode()

    def setInsertState (self,event):
        '''Enter the 'insert' editing state.'''
        # g.trace(g.callers())
        k = self
        k.setInputState('insert')
        # This command is also valid in headlines.
        # k.c.bodyWantsFocus()
        k.showStateAndMode()

    def setOverwriteState (self,event):
        '''Enter the 'overwrite' editing state.'''
        # g.trace(g.callers())
        k = self
        k.setInputState('overwrite')
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
    #@+node:ekr.20061031131434.126: *4* manufactureKeyPressForCommandName
    def manufactureKeyPressForCommandName (self,w,commandName):

        '''Implement a command by passing a keypress to the gui.'''

        k = self ; c = k.c

        stroke = k.getShortcutForCommandName(commandName)

        # g.trace('stroke',repr(stroke),'commandName',commandName,'w',w,g.callers())

        if stroke and w:
            # g.trace(stroke)
            g.app.gui.set_focus(c,w)
            g.app.gui.event_generate(w,stroke)
        else:
            message = 'no shortcut for %s' % (commandName)
            if g.app.unitTesting:
                raise AttributeError(message)
            else:
                g.trace(message,color='red')
    #@+node:ekr.20061031131434.127: *4* simulateCommand
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
            stroke = None
            if commandName.startswith('specialCallback'):
                event = None # A legacy function.
            else: # Create a dummy event as a signal.
                event = g.bunch(c=c,keysym='',char='',widget=None)
            k.masterCommand(event,func,stroke)
            if c.exists:
                return k.funcReturn
            else:
                return None
        else:
            g.trace('no command for %s' % (commandName),color='red')
            if g.app.unitTesting:
                raise AttributeError
            else:
                return None
    #@+node:ekr.20061031131434.128: *4* getArg
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

        k = self ; c = k.c ; gui  = g.app.gui
        trace = (False or (c.config.getBool('trace_modes')) and not g.app.unitTesting)
        state = k.getState('getArg')
        keysym = gui.eventKeysym(event)
        if trace: g.trace(
            'state',state,'keysym',repr(keysym),'stroke',repr(stroke),
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
        elif keysym == 'Escape':
            k.keyboardQuit(event)
        elif keysym == 'Return' or k.oneCharacterArg or (stroke and stroke in k.getArgEscapes):
            if stroke and stroke in k.getArgEscapes: k.getArgEscape = stroke
            if k.oneCharacterArg:
                k.arg = event.char
            else:
                k.arg = k.getLabel(ignorePrompt=True)
            kind,n,handler = k.afterGetArgState
            if kind: k.setState(kind,n,handler)
            c.frame.log.deleteTab('Completion')
            trace and g.trace('kind',kind,'n',n,'handler',handler and handler.__name__)
            if handler: handler(event)
        elif keysym in('Tab','\t'):
            k.doTabCompletion(k.argTabList,k.arg_completion)
        elif keysym in('BackSpace','\b'): # 2010/02/20: Test for \b also.
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
        return 'break'
    #@+node:ekr.20061031131434.130: *4* keyboardQuit
    def keyboardQuit (self,event,hideTabs=True,setDefaultStatus=True):

        '''This method clears the state and the minibuffer label.

        k.endCommand handles all other end-of-command chores.'''

        k = self ; c = k.c

        if g.app.quitting:
            return

        if hideTabs:
            k.autoCompleter.exit()
            c.frame.log.deleteTab('Mode')
            c.frame.log.hideTab('Completion')

        # Completely clear the mode.
        if k.inputModeName:
            k.endMode(event)

        # Complete clear the state.
        k.state.kind = None
        k.state.n = None

        k.clearState()
        k.resetLabel()

        c.endEditing()
        c.bodyWantsFocus()

        if setDefaultStatus:
            # At present, only the auto-completer suppresses this.
            k.setDefaultInputState()
            k.showStateAndMode()
    #@+node:ekr.20061031131434.131: *4* k.registerCommand
    def registerCommand (self,commandName,shortcut,func,
        pane='all',verbose=False, wrap=True):

        '''Make the function available as a minibuffer command,
        and optionally attempt to bind a shortcut.

        You can wrap any method in a callback function, so the
        restriction to functions is not significant.

        If wrap is True then func will be wrapped with c.universalCallback.

        '''

        trace = False and not g.unitTesting
        k = self ; c = k.c

        if wrap:
            func = c.universalCallback(func)

        f = c.commandsDict.get(commandName)
        verbose = (False or verbose) and not g.app.unitTesting
        if f and f.__name__ != 'dummyCallback' and verbose:
            g.es_print('redefining',commandName, color='red')

        # if commandName == 'full-command': g.trace(commandName,func.__name__)
        c.commandsDict [commandName] = func
        k.inverseCommandsDict [func.__name__] = commandName
        if trace: g.trace('leoCommands %24s = %s' % (func.__name__,commandName))

        if shortcut:
            stroke = k.shortcutFromSetting(shortcut)
        elif commandName.lower() == 'shortcut': # Causes problems.
            stroke = None
        else:
            # Try to get a shortcut from leoSettings.leo.
            junk,bunchList = c.config.getShortcut(commandName)
            for bunch in bunchList:
                accel2 = bunch.val ; pane2 = bunch.pane
                if accel2 and not pane2.endswith('-mode'):
                    shortcut2 = accel2
                    stroke = k.shortcutFromSetting(shortcut2)
                    if stroke: break
            else: stroke = None

        if stroke:
            if trace: g.trace('stroke',stroke,'pane',pane,commandName,g.callers(4))
            ok = k.bindKey (pane,stroke,func,commandName,_hash='register-command') # Must be a stroke.
            k.makeMasterGuiBinding(stroke) # Must be a stroke.
            if verbose and ok and not g.app.silentMode:
                # g.trace(g.callers())
                g.es_print('','@command: %s = %s' % (
                    commandName,k.prettyPrintKey(stroke)),color='blue')
                if 0:
                    d = k.masterBindingsDict.get('button',{})
                    g.print_dict(d)
            c.frame.tree.setBindings()
        elif trace and verbose and not g.app.silentMode:
            g.trace(g.callers())
            g.es_print('','@command: %s' % (commandName),color='blue')

        # Fixup any previous abbreviation to press-x-button commands.
        if commandName.startswith('press-') and commandName.endswith('-button'):
            d = c.config.getAbbrevDict()
                # Keys are full command names, values are abbreviations.
            if commandName in list(d.values()):
                for key in d:
                    if d.get(key) == commandName:
                        c.commandsDict [key] = c.commandsDict.get(commandName)
                        break
    #@+node:ekr.20071212104050: *4* k.overrideCommand
    def overrideCommand (self,commandName,func):

        # Override entries in c.k.masterBindingsDict
        k = self
        d = k.masterBindingsDict
        for key in d:
            d2 = d.get(key)
            for key2 in d2:
                b = d2.get(key2)
                if b.commandName == commandName:
                    b.func=func
                    d2[key2] = b
    #@+node:ekr.20061031131434.145: *3* k.Master event handlers
    #@+node:ekr.20061031131434.146: *4* masterKeyHandler & helpers
    master_key_count = 0

    def masterKeyHandler (self,event,stroke=None):

        '''This is the handler for almost all key bindings.'''

        #@+<< define vars >>
        #@+node:ekr.20061031131434.147: *5* << define vars >>
        k = self ; c = k.c ; gui = g.app.gui

        if event:
            # This is a leoGui base class event.
            event = gui.leoKeyEvent(event,c,stroke=stroke)

        w = event.widget
        char = event.char
        keysym = event.keysym
        stroke = event.stroke ### 2010/10/18
        if stroke and not keysym:
            event.keysym = keysym = stroke

        w_name = c.widget_name(w)
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
        trace = (False or self.trace_masterKeyHandler) and not g.app.unitTesting
        traceGC = self.trace_masterKeyHandlerGC and not g.app.unitTesting
        verbose = True

        if keysym in special_keys:
            if trace and verbose: g.trace('keysym',keysym)
            return None
        if traceGC: g.printNewObjects('masterKey 1')
        if trace and verbose: g.trace('stroke:',repr(stroke),'keysym:',
            repr(event.keysym),'ch:',repr(event.char),'state',state,'state2',k.unboundKeyAction)

        # Handle keyboard-quit first.
        if k.abortAllModesKey and stroke == k.abortAllModesKey:
            if c.macroCommands.recordingMacro:
                c.macroCommands.endKbdMacro()
                return 'break'
            else:
                return k.masterCommand(event,k.keyboardQuit,stroke,'keyboard-quit')
                
        # if stroke == 'Tab': g.pdb()

        if k.inState():
            if trace: g.trace('   state %-10s %s' % (stroke,state))
            done,val = k.doMode(event,state,stroke)
            if done: return val

        if traceGC: g.printNewObjects('masterKey 2')
                
        # 2011/02/08: An important simplification.
        if isPlain and k.unboundKeyAction != 'command':
            if self.isAutoCompleteChar(stroke):
                if trace: g.trace('autocomplete key',stroke)
            else:
                if trace: g.trace('inserted %-10s (insert/overwrite mode)' % (stroke))
                return k.handleUnboundKeys(event,char,keysym,stroke)

        # 2011/02/08: Use getPandBindings for *all* keys.
        b = k.getPaneBinding(stroke,w)
        if b:
            if traceGC: g.printNewObjects('masterKey 3')
            if trace: g.trace('   bound',stroke)
            return k.masterCommand(event,b.func,b.stroke,b.commandName)
        else:
            if traceGC: g.printNewObjects('masterKey 4')
            if trace: g.trace(' unbound',stroke)
            return k.handleUnboundKeys(event,char,keysym,stroke)
    #@+node:ekr.20061031131434.108: *5* callStateFunction
    def callStateFunction (self,event):

        k = self ; val = None ; ch = g.app.gui.eventChar(event)

        # g.trace(k.state.kind,'ch',ch,'ignore-non-ascii',k.ignore_unbound_non_ascii_keys)

        if k.state.kind:
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
                    k.endCommand(event,k.commandName)
            else:
                g.es_print('no state function for',k.state.kind,color='red')

        return val
    #@+node:ekr.20091230094319.6244: *5* doMode
    def doMode (self,event,state,stroke):

        trace = False and not g.unitTesting
        k = self

        # First, honor minibuffer bindings for all except user modes.
        if state in ('getArg','getFileName','full-command','auto-complete'):
            if k.handleMiniBindings(event,state,stroke):
                return True,'break'

        # Second, honor general modes.
        if state == 'getArg':
            return True,k.getArg(event,stroke=stroke)
        elif state == 'getFileName':
            return True,k.getFileName(event)
        elif state in ('full-command','auto-complete'):
            # Do the default state action.
            if trace: g.trace('calling state function',k.state.kind)
            val = k.callStateFunction(event) # Calls end-command.
            if val != 'do-standard-keys':
                return True,'break'

        # Third, pass keys to user modes.
        d =  k.masterBindingsDict.get(state)
        if d:
            b = d.get(stroke)
            if b:
                if trace: g.trace('calling generalModeHandler',stroke)
                k.generalModeHandler (event,
                    commandName=b.commandName,func=b.func,
                    modeName=state,nextMode=b.nextMode)
                return True,'break'
            else:
                # New in Leo 4.5: unbound keys end mode.
                # if trace: g.trace('unbound key ends mode',stroke,state)
                g.warning('unbound key ends mode',stroke) # 2011/02/02
                k.endMode(event)
                return False,None
        else:
            # New in 4.4b4.
            handler = k.getStateHandler()
            if handler:
                if trace: g.trace('handler',handler)
                handler(event)
            else:
                if trace: g.trace('No state handler for %s' % state)
            return True,'break'
    #@+node:ekr.20091230094319.6240: *5* getPaneBinding
    def getPaneBinding (self,stroke,w):

        trace = False and not g.unitTesting
        verbose = True
        k = self ; w_name = k.c.widget_name(w)
        # keyStatesTuple = ('command','insert','overwrite')
        state = k.unboundKeyAction

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
                    g.trace('key: %7s name: %6s key: %10s in keys: %s' %
                        (key,name,stroke,stroke in d))
                    # g.trace(key,'keys',g.listToString(list(d.keys()),sort=True)) # [:5])
                if d:
                    b = d.get(stroke)
                    if b:
                        if trace: g.trace('%s found %s = %s' % (key,repr(b.stroke),b.commandName))
                        return b
    #@+node:ekr.20061031131434.152: *5* handleMiniBindings
    def handleMiniBindings (self,event,state,stroke):

        k = self ; c = k.c
        trace = (False or self.trace_masterKeyHandler) and not g.app.unitTesting

        # Special case for bindings handled in k.getArg:
        if state in ('getArg','full-command'):
            if stroke in ('BackSpace','Return','Tab','\t','Escape',):
                return False
            if k.isFKey(stroke): # 2010/10/23.
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
                    b = d.get(stroke)
                    if b:
                        if b.commandName == 'replace-string' and state == 'getArg':
                            if trace: g.trace('%s binding for replace-string' % (pane),stroke)
                            return False # Let getArg handle it.
                        elif b.commandName not in k.singleLineCommandList:
                            if trace: g.trace('%s binding terminates minibuffer' % (pane),b.commandName,stroke)
                            k.keyboardQuit(event,hideTabs=True)
                        else:
                            if trace: g.trace(repr(stroke),'mini binding',b.commandName)
                            c.minibufferWantsFocus() # New in Leo 4.5.
                        # Pass this on for macro recording.
                        k.masterCommand(event,b.func,stroke,b.commandName)
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
        
        if stroke and state in ('insert','overwrite'):
            for key in (state,'body','log','text','all'):
                d = k.masterBindingsDict.get(key,{})
                if d:
                    b = d.get(stroke)
                    if b and b.commandName == 'auto-complete':
                        return True
        return False
    #@+node:ekr.20080510095819.1: *5* k.handleUnboundKeys
    def handleUnboundKeys (self,event,char,keysym,stroke):

        trace = False and not g.unitTesting
        verbose = False
        k = self ; c = k.c
        modesTuple = ('insert','overwrite')
        
        # g.trace('self.enable_alt_ctrl_bindings',self.enable_alt_ctrl_bindings)

        if trace and verbose: g.trace('ch: %s keysym: %s stroke %s' % (
            repr(event.char),repr(event.keysym),repr(stroke)))

        # g.trace('stroke',repr(stroke),'isFKey',k.isFKey(stroke))

        if k.unboundKeyAction == 'command':
            # Ignore all unbound characters in command mode.
            w = g.app.gui.get_focus(c)
            if w and g.app.gui.widget_name(w).lower().startswith('canvas'):
                c.onCanvasKey(event)
            if trace: g.trace('ignoring unbound character in command mode',stroke)
            return 'break'

        elif k.isFKey(stroke):
            if trace: g.trace('ignoring F-key',stroke)
            return 'break'

        elif stroke and k.isPlainKey(stroke) and k.unboundKeyAction in modesTuple:
            # insert/overwrite normal character.  <Return> is *not* a normal character.
            if trace: g.trace('plain key in insert mode',repr(stroke))
            return k.masterCommand(event,func=None,stroke=stroke,commandName=None)

        elif (not self.enable_alt_ctrl_bindings and
            (stroke.find('Alt+') > -1 or stroke.find('Ctrl+') > -1)
        ):
            # 2011/02/11: Always ignore unbound Alt/Ctrl keys.
            if trace: g.trace('ignoring unbound Alt/Ctrl key',stroke,keysym)
            return 'break'

        elif k.ignore_unbound_non_ascii_keys and len(char) > 1:
            if trace: g.trace('ignoring unbound non-ascii key',repr(stroke))
            return 'break'

        elif (
            keysym and keysym.find('Escape') != -1 or
            stroke and stroke.find('Insert') != -1
        ):
            # Never insert escape or insert characters.
            if trace: g.trace('ignore Escape/Ignore',stroke)
            return 'break'

        else:
            if trace: g.trace('no func',stroke)
            return k.masterCommand(event,func=None,stroke=stroke,commandName=None)
    #@+node:ekr.20061031131434.153: *4* masterClickHandler
    def masterClickHandler (self,event,func=None):

        g.app.gui.killPopupMenu()

        k = self ; c = k.c ; gui = g.app.gui
        if not event: return
        w = event.widget ; wname = c.widget_name(w)
        trace = not g.app.unitTesting and (False or k.trace_masterClickHandler)

        if trace: g.trace(wname,func and func.__name__)
        # c.frame.body.colorizer.interrupt() # New in 4.4.1

        # A click outside the minibuffer terminates any state.
        if k.inState() and w != c.frame.miniBufferWidget:
            if not c.widget_name(w).startswith('log'):
                k.keyboardQuit(event,hideTabs=False)
                # k.endMode(event) # Less drastic than keyboard-quit.
                w and c.widgetWantsFocusNow(w)
                if trace: g.trace('inState: break')
                return 'break'

        # Update the selection point immediately for updateStatusLine.
        k.previousSelection = None
        if wname.startswith('body'):
            c.frame.body.onClick(event) # New in Leo 4.4.2.
        elif wname.startswith('mini'):
            x,y = gui.eventXY(event)
            x = w.xyToPythonIndex(x,y)
            i,j = k.getEditableTextRange()
            if i <= x <= j:
                w.setSelectionRange(x,x,insert=x)
            else:
                if trace: g.trace('2: break')
                return 'break'
        if event and func:
            if trace: g.trace(func.__name__)
            val = func(event) # Don't even *think* of overriding this.
            if trace: g.trace('val:',val,g.callers())
            return val
        else:
            # All tree callbacks have a func, so we can't be in the tree.
            # g.trace('*'*20,'auto-deactivate tree: %s' % wname)
            c.frame.tree.OnDeactivate()
            c.widgetWantsFocusNow(w)
            if trace: g.trace('end: None')
            return None

    masterClick3Handler = masterClickHandler
    masterDoubleClick3Handler = masterClickHandler
    #@+node:ekr.20061031131434.154: *4* masterDoubleClickHandler
    def masterDoubleClickHandler (self,event,func=None):

        k = self ; c = k.c ; w = event and event.widget

        if c.config.getBool('trace_masterClickHandler'):
            g.trace(c.widget_name(w),func and func.__name__)

        if event and func:
            # Don't event *think* of overriding this.
            return func(event)
        else:
            gui = g.app.gui
            x,y = gui.eventXY(event)
            i = w.xyToPythonIndex(x,y)
            s = w.getAllText()
            start,end = g.getWord(s,i)
            w.setSelectionRange(start,end)
            return 'break'
    #@+node:ekr.20061031131434.155: *4* masterMenuHandler
    def masterMenuHandler (self,stroke,func,commandName):

        k = self ; c = k.c
        w = c.frame.getFocus()

        # g.trace('focus',w)
        # g.trace('stroke',stroke,'func',func and func.__name__,commandName,g.callers())

        # Create a minimal event for commands that require them.
        event = g.Bunch(c=c,char='',keysym='',widget=w)

        if stroke:
            return k.masterKeyHandler(event,stroke=stroke)
        else:
            return k.masterCommand(event,func,stroke,commandName)
    #@+node:ekr.20061031170011.3: *3* k.Minibuffer
    # These may be overridden, but this code is now gui-independent.
    #@+node:ekr.20061031131434.135: *4* k.minibufferWantsFocus
    # def minibufferWantsFocus(self):

        # c = self.c
        # c.widgetWantsFocus(c.miniBufferWidget)
    #@+node:ekr.20061031170011.5: *4* getLabel
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

        k = self ; c = self.c
        w = self.w
        s = w.getAllText()
        s = s[:len(k.mb_prefix)]

        w.setAllText(s)
        n = len(s)
        w.setSelectionRange(n,n,insert=n)

        if protect:
            k.mb_prefix = s
    #@+node:ekr.20061031170011.6: *4* protectLabel
    def protectLabel (self):

        k = self ; w = self.w
        if not w: return

        k.mb_prefix = w.getAllText()

    #@+node:ekr.20061031170011.7: *4* resetLabel
    def resetLabel (self):

        k = self ; w = self.w
        k.setLabelGrey('')
        k.mb_prefix = ''

        if w:    
            w.setSelectionRange(0,0,insert=0)
            state = k.unboundKeyAction
            k.setLabelBlue(label='%s State' % (state.capitalize()),protect=True)
    #@+node:ekr.20061031170011.8: *4* setLabel
    def setLabel (self,s,protect=False):

        trace = (False or self.trace_minibuffer) and not g.app.unitTesting
        k = self ; c = k.c ; w = self.w
        if not w: return

        if trace: g.trace(repr(s),g.callers(4))

        w.setAllText(s)
        n = len(s)
        w.setSelectionRange(n,n,insert=n)

        if protect:
            k.mb_prefix = s
    #@+node:ekr.20061031170011.9: *4* extendLabel
    def extendLabel(self,s,select=False,protect=False):

        k = self ; c = k.c ; w = self.w
        if not w: return
        trace = self.trace_minibuffer and not g.app.unitTesting

        trace and g.trace('len(s)',len(s))
        if not s: return

        c.widgetWantsFocusNow(w)
        w.insert('end',s)

        if select:
            i,j = k.getEditableTextRange()
            w.setSelectionRange(i,j,insert=j)

        if protect:
            k.protectLabel()
    #@+node:ekr.20080408060320.790: *4* selectAll
    def selectAll (self):

        '''Select all the user-editable text of the minibuffer.'''

        w = self.w
        i,j = self.getEditableTextRange()
        w.setSelectionRange(i,j,insert=j)


    #@+node:ekr.20061031170011.10: *4* setLabelBlue
    def setLabelBlue (self,label=None,protect=False):

        k = self ; w = k.w
        if not w: return

        w.setBackgroundColor(self.minibuffer_background_color) # 'lightblue')

        if label is not None:
            k.setLabel(label,protect)
    #@+node:ekr.20061031170011.11: *4* setLabelGrey
    def setLabelGrey (self,label=None):

        k = self ; w = self.w
        if not w: return

        w.setBackgroundColor(self.minibuffer_warning_color) # 'lightgrey')

        if label is not None:
            k.setLabel(label)

    setLabelGray = setLabelGrey
    #@+node:ekr.20080510153327.2: *4* setLabelRed
    def setLabelRed (self,label=None,protect=False):

        k = self ; w = self.w
        if not w: return

        w.setForegroundColor(self.minibuffer_error_color) # 'red')

        if label is not None:
            k.setLabel(label,protect)
    #@+node:ekr.20061031170011.12: *4* updateLabel
    def updateLabel (self,event):

        '''Mimic what would happen with the keyboard and a Text editor
        instead of plain accumalation.'''

        trace = False or self.trace_minibuffer and not g.app.unitTesting
        k = self ; c = k.c ; w = self.w
        ch = (event and event.char) or ''
        keysym = (event and event.keysym) or ''

        trace and g.trace('ch',ch,'keysym',keysym,'k.stroke',k.stroke)
        # g.trace(g.callers())

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
    #@+node:ekr.20061031170011.13: *4* getEditableTextRange
    def getEditableTextRange (self):

        k = self ; w = self.w
        trace = self.trace_minibuffer and not g.app.unitTesting

        s = w.getAllText()
        # g.trace(len(s),repr(s))

        i = len(k.mb_prefix)
        j = len(s)

        trace and g.trace(i,j)
        return i,j
    #@+node:ekr.20061031131434.156: *3* k.Modes
    #@+node:ekr.20061031131434.157: *4* badMode
    def badMode(self,modeName):

        k = self

        k.clearState()
        if modeName.endswith('-mode'): modeName = modeName[:-5]
        k.setLabelGrey('@mode %s is not defined (or is empty)' % modeName)
    #@+node:ekr.20061031131434.158: *4* createModeBindings
    def createModeBindings (self,modeName,d,w):

        '''Create mode bindings for the named mode using dictionary d for w, a text widget.'''

        trace = True and not g.unitTesting
        k = self ; c = k.c

        for commandName in d:
            if commandName in ('*entry-commands*','*command-prompt*','_hash'):
                # These are special-purpose dictionary entries.
                continue
            func = c.commandsDict.get(commandName)
            if not func:
                g.es_print('no such command:',commandName,'Referenced from',modeName)
                continue
            bunchList = d.get(commandName,[])
            for bunch in bunchList:
                stroke = bunch.val
                # Important: bunch.val is a stroke returned from k.strokeFromSetting.
                # Do not call k.strokeFromSetting again here!
                if stroke and stroke not in ('None','none',None):
                    if trace:
                        g.trace(
                            g.app.gui.widget_name(w), modeName,
                            '%10s' % (stroke),
                            '%20s' % (commandName),
                            bunch.nextMode)

                    k.makeMasterGuiBinding(stroke)

                    # Create the entry for the mode in k.masterBindingsDict.
                    # Important: this is similar, but not the same as k.bindKeyToDict.
                    # Thus, we should **not** call k.bindKey here!
                    d2 = k.masterBindingsDict.get(modeName,{})
                    d2 [stroke] = g.Bunch(
                        commandName=commandName,
                        func=func,
                        nextMode=bunch.nextMode,
                        stroke=stroke)
                    k.masterBindingsDict [ modeName ] = d2
    #@+node:ekr.20061031131434.159: *4* endMode
    def endMode(self,event):

        k = self ; c = k.c

        w = g.app.gui.get_focus(c)
        if w:
            c.frame.log.deleteTab('Mode') # Changes focus to the body pane

        k.endCommand(event,k.stroke)
        k.inputModeName = None
        k.clearState()
        k.resetLabel()
        k.showStateAndMode() # Restores focus.

        if w:
            c.widgetWantsFocusNow(w)
    #@+node:ekr.20061031131434.160: *4* enterNamedMode
    def enterNamedMode (self,event,commandName):

        k = self ; c = k.c
        modeName = commandName[6:]
        c.inCommand = False # Allow inner commands in the mode.
        k.generalModeHandler(event,modeName=modeName)
    #@+node:ekr.20061031131434.161: *4* exitNamedMode
    def exitNamedMode (self,event):

        k = self

        if k.inState():
            k.endMode(event)

        k.showStateAndMode()
    #@+node:ekr.20061031131434.162: *4* generalModeHandler
    def generalModeHandler (self,event,
        commandName=None,func=None,modeName=None,nextMode=None,prompt=None):

        '''Handle a mode defined by an @mode node in leoSettings.leo.'''

        k = self ; c = k.c
        state = k.getState(modeName)
        trace = False or c.config.getBool('trace_modes')

        if trace: g.trace(modeName,'state',state)

        if state == 0:
            k.inputModeName = modeName
            k.modePrompt = prompt or modeName
            k.modeWidget = event and event.widget
            k.setState(modeName,1,handler=k.generalModeHandler)
            self.initMode(event,modeName)
            # Careful: k.initMode can execute commands that will destroy a commander.
            if g.app.quitting or not c.exists: return 'break'
            if not k.silentMode:
                if c.config.getBool('showHelpWhenEnteringModes'):
                    k.modeHelp(event)
                else:
                    c.frame.log.hideTab('Mode')
        elif not func:
            g.trace('No func: improper key binding')
            return 'break'
        else:
            if commandName == 'mode-help':
                func(event)
            else:
                savedModeName = k.inputModeName # Remember this: it may be cleared.
                self.endMode(event)
                if trace or c.config.getBool('trace_doCommand'): g.trace(func.__name__)
                # New in 4.4.1 b1: pass an event describing the original widget.
                if event:
                    event.widget = k.modeWidget
                else:
                    event = g.Bunch(widget = k.modeWidget)
                if trace: g.trace(modeName,'state',state,commandName,'nextMode',nextMode)
                func(event)
                if g.app.quitting or not c.exists:
                    return 'break'
                if nextMode in (None,'none'):
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
                    if g.app.quitting or not c.exists: return 'break'

        return 'break'
    #@+node:ekr.20061031131434.163: *4* initMode
    def initMode (self,event,modeName):

        k = self ; c = k.c
        trace = c.config.getBool('trace_modes')

        if not modeName:
            g.trace('oops: no modeName')
            return

        d = g.app.config.modeCommandsDict.get('enter-'+modeName)
        if not d:
            self.badMode(modeName)
            return
        else:
            k.modeBindingsDict = d
            prompt = d.get('*command-prompt*') or modeName
            if trace: g.trace('modeName',modeName,prompt,'d.keys()',list(d.keys()))

        k.inputModeName = modeName
        k.silentMode = False

        entryCommands = d.get('*entry-commands*',[])
        if entryCommands:
            for commandName in entryCommands:
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
    #@+node:ekr.20061031131434.164: *4* reinitMode
    def reinitMode (self,modeName):

        k = self ; c = k.c

        d = k.modeBindingsDict

        k.inputModeName = modeName
        w = g.choose(k.silentMode,k.modeWidget,k.w)
        k.createModeBindings(modeName,d,w)

        if k.silentMode:
            k.showStateAndMode()
        else:
            # Do not set the status line here.
            k.setLabelBlue(modeName+': ',protect=True)

    #@+node:ekr.20061031131434.165: *4* modeHelp & helper
    def modeHelp (self,event):

        '''The mode-help command.

        A possible convention would be to bind <Tab> to this command in most modes,
        by analogy with tab completion.'''

        k = self ; c = k.c

        c.endEditing()

        g.trace(k.inputModeName)

        if k.inputModeName:
            d = g.app.config.modeCommandsDict.get('enter-'+k.inputModeName)
            k.modeHelpHelper(d)

        if not k.silentMode:
            c.minibufferWantsFocus()

        return 'break'
    #@+node:ekr.20061031131434.166: *5* modeHelpHelper
    def modeHelpHelper (self,d):

        k = self ; c = k.c ; tabName = 'Mode'
        c.frame.log.clearTab(tabName)
        data = [] ; n = 20
        for key in sorted(d):
            if key not in ( '*entry-commands*','*command-prompt*'):
                bunchList = d.get(key)
                for bunch in bunchList:
                    shortcut = bunch.val
                    if shortcut not in (None,'None'):
                        s1 = key ; s2 = k.prettyPrintKey(shortcut,brief=True)
                        n = max(n,len(s1))
                        data.append((s1,s2),)

        data.sort()

        modeName = k.inputModeName.replace('-',' ')
        if modeName.endswith('mode'): modeName = modeName[:-4].strip()

        g.es('','%s mode\n\n' % modeName,tabName=tabName)

        # This isn't perfect in variable-width fonts.
        for s1,s2 in data:
            g.es('','%*s %s' % (n,s1,s2),tabName=tabName)
    #@+node:ekr.20061031131434.167: *3* k.Shared helpers
    #@+node:ekr.20061031131434.175: *4* k.computeCompletionList
    # Important: this code must not change mb_tabListPrefix.  Only doBackSpace should do that.

    def computeCompletionList (self,defaultTabList,backspace):

        k = self ; c = k.c ; s = k.getLabel() ; tabName = 'Completion'
        command = s [len(k.mb_prompt):]
            # s always includes prefix, so command is well defined.

        k.mb_tabList,common_prefix = g.itemsMatchingPrefixInList(command,defaultTabList)
        c.frame.log.clearTab(tabName)

        if k.mb_tabList:
            k.mb_tabListIndex = -1 # The next item will be item 0.

            if not backspace:
                k.setLabel(k.mb_prompt + common_prefix)

            inverseBindingDict = k.computeInverseBindingDict()
            data = [] ; n1 = 20; n2 = 4
            for commandName in k.mb_tabList:
                dataList = inverseBindingDict.get(commandName,[('',''),])
                for z in dataList:
                    pane,key = z
                    s1 = commandName
                    s2 = pane
                    s3 = k.prettyPrintKey(key)
                    n1 = max(n1,len(s1))
                    n2 = max(n2,len(s2))
                    data.append((s1,s2,s3),)
            aList = '\n'.join(
                ['%*s %*s %s' % (-(min(20,n1)),s1,n2,s2,s3)
                    for s1,s2,s3 in data])
            g.es('',aList,tabName=tabName)
        c.bodyWantsFocus()
    #@+node:ekr.20061031131434.176: *4* computeInverseBindingDict
    def computeInverseBindingDict (self):

        k = self ; d = {}

        # keys are minibuffer command names, values are shortcuts.
        for shortcut in k.bindingsDict:
            bunchList = k.bindingsDict.get(shortcut,[])
            for b in bunchList:
                shortcutList = d.get(b.commandName,[])
                bunchList = k.bindingsDict.get(shortcut,[g.Bunch(pane='all')])
                for b in bunchList:
                    #pane = g.choose(b.pane=='all','','%s:' % (b.pane))
                    pane = '%s:' % (b.pane)
                    data = (pane,shortcut)
                    if data not in shortcutList:
                        shortcutList.append(data)

                d [b.commandName] = shortcutList

        return d
    #@+node:ekr.20061031131434.168: *4* getFileName & helpers
    def getFileName (self,event=None,handler=None,prefix='',filterExt='.leo'):

        '''Similar to k.getArg, but uses completion to indicate files on the file system.'''

        k = self ; c = k.c ; gui = g.app.gui
        tag = 'getFileName' ; state = k.getState(tag)
        tabName = 'Completion'
        keysym = gui.eventKeysym(event)
        # g.trace('state',state,'keysym',keysym)
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
        elif keysym == 'Return':
            k.arg = k.getLabel(ignorePrompt=True)
            handler = k.getFileNameHandler
            c.frame.log.deleteTab(tabName)
            if handler: handler(event)
        elif keysym in ('Tab','\t'):
            k.doFileNameTab()
            c.minibufferWantsFocus()
        elif keysym == 'BackSpace':
            k.doFileNameBackSpace() 
            c.minibufferWantsFocus()
        else:
            k.doFileNameChar(event)
        return 'break'
    #@+node:ekr.20061031131434.170: *5* k.doFileNameBackSpace
    def doFileNameBackSpace (self):

        '''Cut back to previous prefix and update prefix.'''

        k = self ; c = k.c

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

        k = self ; c = k.c ; s = k.getLabel() ; tabName = 'Completion'
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
    #@+node:ekr.20061031131434.179: *4* getShortcutForCommand/Name (should return lists)
    def getShortcutForCommandName (self,commandName):

        k = self ; c = k.c

        command = c.commandsDict.get(commandName)

        if command:
            for key in k.bindingsDict:
                bunchList = k.bindingsDict.get(key,[])
                for b in bunchList:
                    if b.commandName == commandName:
                        return k.tkbindingFromStroke(key)
        return ''

    def getShortcutForCommand (self,command):

        k = self ; c = k.c

        if command:
            for key in k.bindingsDict:
                bunchList = k.bindingsDict.get(key,[])
                for b in bunchList:
                    if b.commandName == command.__name__:
                         return k.tkbindingFromStroke(key)
        return ''
    #@+node:ekr.20061031131434.177: *4* k.doBackSpace (minibuffer)
    # Used by getArg and fullCommand.

    def doBackSpace (self,defaultCompletionList,completion=True):

        '''Cut back to previous prefix and update prefix.'''

        trace = False and not g.unitTesting
        k = self ; c = k.c ; w = self.w

        # Step 1: actually delete the character.
        ins = w.getInsertPoint()
        s = w.getAllText()

        if trace: g.trace('ins',ins,'k.mb_prefix',repr(k.mb_prefix),
            'w',w)

        if ins <= len(k.mb_prefix):
            # g.trace('at start')
            return
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

    def doTabCompletion (self,defaultTabList,redraw=True):

        '''Handle tab completion when the user hits a tab.'''

        k = self ; c = k.c ; s = k.getLabel().strip()

        if k.mb_tabList and s.startswith(k.mb_tabListPrefix):
            # g.trace('cycle',repr(s))
            # Set the label to the next item on the tab list.
            k.mb_tabListIndex +=1
            if k.mb_tabListIndex >= len(k.mb_tabList):
                k.mb_tabListIndex = 0
            k.setLabel(k.mb_prompt + k.mb_tabList [k.mb_tabListIndex])
        else:
            if redraw:
                k.computeCompletionList(defaultTabList,backspace=False)

        c.minibufferWantsFocus()
    #@+node:ekr.20061031131434.180: *4* traceBinding
    def traceBinding (self,bunch,shortcut,w):

        k = self ; c = k.c ; gui = g.app.gui

        if not c.config.getBool('trace_bindings'): return

        theFilter = c.config.getString('trace_bindings_filter') or ''
        if theFilter and shortcut.lower().find(theFilter.lower()) == -1: return

        pane_filter = c.config.getString('trace_bindings_pane_filter')

        if not pane_filter or pane_filter.lower() == bunch.pane:
             g.trace(bunch.pane,shortcut,bunch.commandName,gui.widget_name(w))
    #@+node:ekr.20061031131434.181: *3* k.Shortcuts
    #@+node:ekr.20090518072506.8494: *4* isFKey
    def isFKey (self,shortcut):


        if not shortcut: return False

        s = shortcut.lower()

        return s.startswith('f') and len(s) <= 3 and s[1:].isdigit()
    #@+node:ekr.20061031131434.182: *4* isPlainKey
    def isPlainKey (self,shortcut):

        '''Return true if the shortcut refers to a plain (non-Alt,non-Ctl) key.'''

        k = self ; shortcut = shortcut or ''

        # altgr combos (Alt+Ctrl) are always plain keys
        if shortcut.startswith('Alt+Ctrl+') and not self.enable_alt_ctrl_bindings:
            return True

        for s in ('Alt','Ctrl','Command','Meta'):
            if shortcut.find(s) != -1:            
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
    #@+node:ekr.20061031131434.184: *4* shortcutFromSetting (uses k.guiBindNamesDict)
    def shortcutFromSetting (self,setting,addKey=True):

        k = self

        trace = False and not g.unitTesting
        if not setting:return None

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
                    g.pr("bad shortcut specifier:", s)
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
        if trace: g.trace('%20s %s' % (setting,shortcut))
        return shortcut

    canonicalizeShortcut = shortcutFromSetting # For compatibility.
    strokeFromSetting = shortcutFromSetting
    #@+node:ekr.20061031131434.190: *4* k.tkbindingFromStroke
    def tkbindingFromStroke (self,stroke):

        '''Convert a stroke (key to k.bindingsDict) to an actual Tk binding.'''

        stroke = g.stripBrackets(stroke)

        for a,b in (
            ('Alt+','Alt-'),
            ('Ctrl-','Control-'),
            ('Ctrl+','Control-'), # New in Leo 4.5.
            ('Meta+','Meta-'), # New in Leo 4.6
            ('Shift+','Shift-'),
            ('Command+','Command-'),
            ('DnArrow','Down'), # New in Leo 4.5.
            ('LtArrow','Left'), # New in Leo 4.5.
            ('RtArrow','Right'),# New in Leo 4.5.
            ('UpArrow','Up'),   # New in Leo 4.5.
        ):
            stroke = stroke.replace(a,b)

        # g.trace('<%s>' % stroke)
        return '<%s>' % stroke
    #@+node:ekr.20061031131434.191: *4* k.prettyPrintKey
    def prettyPrintKey (self,stroke,brief=False,trace=False):

        k = self
        s = stroke and g.stripBrackets(stroke.strip())
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
                    if not prev and not brief:
                        # g.trace('*'*10,s,g.callers())
                        s = 'Key+' + last.upper()
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
        # g.trace(stroke,s)
        return g.choose(brief,s,'<%s>' % s)
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
    def setInputState (self,state):

        k = self
        k.unboundKeyAction = state



    #@+node:ekr.20061031131434.199: *4* setState
    def setState (self,kind,n,handler=None):

        k = self
        if kind and n != None:
            k.state.kind = kind
            k.state.n = n
            if handler:
                k.state.handler = handler
        else:
            k.clearState()

        # k.showStateAndMode()
    #@+node:ekr.20061031131434.192: *4* showStateAndMode
    def showStateAndMode(self,w=None,prompt=None):

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

        if trace: g.trace('state: %s text?: %s w: %s' % (
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

        if s:
            # g.trace(s,w,g.callers(4))
            k.setLabelBlue(label=s,protect=True)

        if w and isText:
            k.showStateColors(inOutline,w)
            k.showStateCursor(state,w)
    #@+node:ekr.20080512115455.1: *4* showStateColors
    def showStateColors (self,inOutline,w):

        trace = False and not g.unitTesting
        k = self ; c = k.c ; state = k.unboundKeyAction

        # body = c.frame.body ; bodyCtrl = body.bodyCtrl
        w_name = g.app.gui.widget_name(w)

        if state not in ('insert','command','overwrite'):
            g.trace('bad input state',state)

        if trace: g.trace('%9s' % (state),w_name)
        
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
            w.setEditorColors(bg=bg,fg=fg) ### Was body.
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

        k = self ; gui = g.app.gui
        state = k.getState('u-arg')

        if state == 0:
            k.dispatchEvent = event
            # The call should set the label.
            k.setState('u-arg',1,k.universalDispatcher)
            k.repeatCount = 1
        elif state == 1:
            # stroke = k.stroke # Warning: k.stroke is always Alt-u
            keysym = gui.eventKeysym(event)
            # g.trace(state,keysym)
            if keysym == 'Escape':
                k.keyboardQuit(event)
            elif keysym == k.universalArgKey:
                k.repeatCount = k.repeatCount * 4
            elif keysym.isdigit() or keysym == '-':
                k.updateLabel(event)
            elif keysym in (
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
                k.executeNTimes(event,n,stroke=keysym)
                k.keyboardQuit(event)
                # k.clearState()
                # k.setLabelGrey()
                if 0: # Not ready yet.
                    # This takes us to macro state.
                    # For example Control-u Control-x ( will execute the last macro and begin editing of it.
                    if stroke == '<Control-x>':
                        k.setState('uC',2,k.universalDispatcher)
                        return k.doControlU(event,stroke)
        elif state == 2:
            k.doControlU(event,stroke)

        return 'break'
    #@+node:ekr.20061031131434.202: *4* executeNTimes
    def executeNTimes (self,event,n,stroke):

        trace = False and not g.unitTesting
        k = self

        if stroke == k.fullCommandKey:
            for z in range(n):
                k.fullCommand()
        else:
            stroke = g.stripBrackets(stroke)
            b = k.getPaneBinding(stroke,event.widget)
            if b:
                if trace: g.trace('repeat',n,'method',b.func.__name__,
                    'stroke',stroke,'widget',event.widget)
                for z in range(n):
                    # event = g.Bunch(
                        # c = self.c,
                        # widget = event.widget,
                        # keysym = event.keysym,
                        # stroke = event.stroke,
                        # char = event.char,
                    # )
                    k.masterCommand(event,b.func,'<%s>' % stroke)
            else:
                # This does nothing for Qt gui.
                w = event.widget
                for z in range(n):
                    g.app.gui.event_generate(w,'<Key>',keysym=event.keysym)
    #@+node:ekr.20061031131434.203: *4* doControlU
    def doControlU (self,event,stroke):

        k = self ; c = k.c
        ch = g.app.gui.eventChar(event)

        k.setLabelBlue('Control-u %s' % g.stripBrackets(stroke))

        if ch == '(':
            k.clearState()
            k.resetLabel()
            c.macroCommands.startKbdMacro(event)
            c.macroCommands.callLastKeyboardMacro(event)
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
#@-others
#@-leo
