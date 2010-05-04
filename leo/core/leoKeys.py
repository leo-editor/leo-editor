#@+leo-ver=4-thin
#@+node:ekr.20061031131434:@thin leoKeys.py
"""Gui-independent keystroke handling for Leo.""" 

#@@language python
#@@tabwidth -4
#@@pagewidth 70

#@<< imports >>
#@+node:ekr.20061031131434.1:<< imports >>
import leo.core.leoGlobals as g
import leo.core.leoFrame as leoFrame # to access stringTextWidget class.

# This creates a circular dependency.
# We break this by doing the import in k.endCommand.
# import leo.core.leoEditCommands as leoEditCommands

import glob
import inspect
import os
import re
import string
import sys
import types
#@-node:ekr.20061031131434.1:<< imports >>
#@nl
#@<< about 'internal' bindings >>
#@+node:ekr.20061031131434.2:<< about 'internal' bindings >>
#@@nocolor
#@+at
# 
# Here are the rules for translating key bindings (in 
# leoSettings.leo) into keys for k.bindingsDict:
# 
# 1.  The case of plain letters is significant:  a is not A.
# 
# 2. The Shift- prefix can be applied *only* to letters. Leo will 
# ignore (with a
# warning) the shift prefix applied to any other binding, e.g., 
# Ctrl-Shift-(
# 
# 3. The case of letters prefixed by Ctrl-, Alt-, Key- or Shift- is 
# *not*
# significant. Thus, the Shift- prefix is required if you want an 
# upper-case
# letter (with the exception of 'bare' uppercase letters.)
# 
# The following table illustrates these rules. In each row, the 
# first entry is the
# key (for k.bindingsDict) and the other entries are equivalents 
# that the user may
# specify in leoSettings.leo:
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
# consistent
# with Tk's key-event specifiers). It is also, I think, the least 
# confusing set of
# rules.
#@-at
#@nonl
#@-node:ekr.20061031131434.2:<< about 'internal' bindings >>
#@nl
#@<< about key dicts >>
#@+node:ekr.20061031131434.3:<< about key dicts >>
#@@nocolor
#@+at
# 
# ivars:
# 
# c.commandsDict:
#     Keys are emacs command names; values are functions f.
# 
# k.inverseCommandsDict:
#     Keys are f.__name__; values are emacs command names.
# 
# k.bindingsDict:
#     Keys are shortcuts; values are *lists* of 
# g.bunch(func,name,warningGiven)
# 
# k.masterBindingsDict:
#     Keys are scope names: 'all','text',etc. or mode names.
#     Values are dicts:  keys are strokes, values are 
# g.Bunch(commandName,func,pane,stroke)
# 
# k.masterGuiBindingsDict:
#     Keys are strokes; value is a list of widgets for which stroke 
# is bound.
# 
# k.settingsNameDict:
#     Keys are lowercase settings; values are 'real' Tk key 
# specifiers.
#     Important: this table has no inverse.
# 
# not an ivar (computed by k.computeInverseBindingDict):
# 
# inverseBindingDict
#     Keys are emacs command names; values are *lists* of shortcuts.
#@-at
#@-node:ekr.20061031131434.3:<< about key dicts >>
#@nl

#@+others
#@+node:ekr.20061031131434.4:class autoCompleterClass
class autoCompleterClass:

    '''A class that inserts autocompleted and calltip text in text widgets.
    This class shows alternatives in the tabbed log pane.

    The keyHandler class contains hooks to support these characters:
    invoke-autocompleter-character (default binding is '.')
    invoke-calltips-character (default binding is '(')
    '''

    #@    @+others
    #@+node:ekr.20061031131434.5: ctor (autocompleter)
    def __init__ (self,k):

        self.c = c = k.c
        self.k = k
        self.allClassesDict = {} # Will be completed after more classes exist.
        self.attrDictDict = {}  # Keys are languages (strings); values are anonymous attrDicts.
            # attrDicts: keys are strings; values are list of strings (attributes).
        self.calltips = {} # Keys are language, values are dicts: keys are ids, values are signatures.
        self.classScanner = self.classScannerClass(c)
        self.forgivingParser = self.forgivingParserClass(c)
        self.globalPythonFunctionsDict = {}
        self.language = None
        self.leadinWord = None
        self.membersList = None
        self.objectDict = {} # Created on first use of the autocompleter.
        self.selection = None # The selection range on entry to autocompleter or calltips.
        self.selectedText = None # The selected text on entry to autocompleter or calltips.
        self.selfClassName = None
        self.selfObjectsDict = {} # Keys are classNames, values are real proxy objects.
        self.selfVnodesDict = {} # Keys are tnodes, values are real proxy objects.
        self.prefix = None
        self.prevObjects = []
        self.tabList = []
        self.tabListIndex = -1
        self.tabName = None # The name of the main completion tab.
        self.theObject = None # The previously found object, for . chaining.
        self.trace = c.config.getBool('trace_autocompleter')
        self.useTabs = True # True: show results in autocompleter tab.
        self.verbose = False # True: print all members.
        self.watchwords = {} # Keys are ids, values are lists of ids that can follow a id dot.
        self.widget = None # The widget that should get focus after autocomplete is done.
    #@+node:ekr.20061031131434.6:defineClassesDict
    def defineClassesDict (self):

        trace = False ; verbose = True

        self.allClassesDict = {}

        # gc may not exist.
        try:
            import gc
            # if trace: g.trace(gc)
        except ImportError:
            if trace: g.trace('no gc')
            return

        if g.isPython3:
            count = 0
            for z in gc.get_objects():
                try:
                    name = z.__class__.__name__
                    if not self.allClassesDict.get(name):
                        self.allClassesDict [name] = z
                        count += 1
                except ReferenceError:
                    pass
            if trace:
                g.trace('%s keys in allClassesDict' % (count))
                if verbose:
                    keys = list(self.allClassesDict.keys())
                    keys.sort()
                    for z in keys:
                        print(z)
        else:
            for z in gc.get_objects():
                t = type(z)
                if t == types.ClassType:
                    name = z.__name__
                elif t == types.InstanceType:
                    name = z.__class__.__name__
                elif repr(t).startswith('<class'): # A wretched kludge.
                    name = z.__class__.__name__
                elif t == types.TypeType:
                    name = z.__name__
                else:
                    name = None
                if name:
                    # if name == 'position': g.trace(t,z)
                    self.allClassesDict [name] = z

        # g.printList(list(self.allClassesDict.keys()),tag='Classes',sort=True)
        # g.trace(len(list(self.allClassesDict.keys())))
        # g.trace('position:',self.allClassesDict.get('position'))
    #@-node:ekr.20061031131434.6:defineClassesDict
    #@+node:ekr.20061031131434.7:defineObjectDict
    def defineObjectDict (self,table=None):

        trace = False

        c = self.c ; k = c.k ; p = c.p

        if trace: g.trace(g.callers(4))

        if table is None: table = [
            # Python globals...
            (['aList','bList'],     'python','list'),
            (['aString'],           'object','aString'), # An actual string object.
            (['cc'],                'object',c.chapterController),
            (['c','old_c','new_c'], 'object',c),            
            (['d','d1','d2'],       'python','dict'),
            (['f'],                 'object',c.frame), 
            (['g'],                 'object',g),       
            (['gui'],               'object',g.app.gui),
            (['k'],                 'object',k),
            (['p','p1','p2'],       'object',p.copy()), # 2009/12/21
            (['s','s1','s2','ch'],  'object','aString'),
            (['string'],            'object',string), # Python's string module.
            # (['t','t1','t2'],       'object',p.v.t),  
            (['v','v1','v2'],       'object',p.v),
            (['w','widget'],        'object',c.frame.body.bodyCtrl),
        ]

        if 0: # Not useful at this point.
            for key in __builtins__.keys():
                obj = __builtins__.get(key)
                if obj in (True,False,None): continue
                data = [key],'object',obj
                table.append(data)

        d = {'dict':{},'int':1,'list':[],'string':''}

        for idList,kind,nameOrObject in table:
            if kind == 'object':
                # Works, but hard to generalize for settings.
                obj = nameOrObject
            elif kind == 'python':
                className = nameOrObject
                o = d.get(className)
                obj = o is not None and o.__class__
            else:
                module = g.importModule (kind,verbose=True)
                if not module:
                    g.trace('Can not import ',nameOrObject)
                    continue
                self.appendToKnownObjects(module)
                if nameOrObject:
                    className = nameOrObject
                    obj = hasattr(module,className) and getattr(module,className) or None
                    if not obj:
                        g.trace('%s module has no class %s' % (kind,nameOrObject))
                    else:
                        self.appendToKnownObjects(getattr(module,className))
                else:
                    obj = module
            for z in idList:
                if trace: g.trace(z,obj)
                if obj:
                    self.objectDict[z]=obj
    #@-node:ekr.20061031131434.7:defineObjectDict
    #@-node:ekr.20061031131434.5: ctor (autocompleter)
    #@+node:ekr.20061031131434.8:Top level
    #@+node:ekr.20061031131434.9:autoComplete
    def autoComplete (self,event=None,force=False):

        '''An event handler called from k.masterKeyHanderlerHelper.'''

        c = self.c ; k = self.k ; gui = g.app.gui
        w = gui.eventWidget(event) or c.get_focus()

        # First, handle the invocation character as usual.
        k.masterCommand(event,func=None,stroke=None,commandName=None)

        # Allow autocompletion only in the body pane.
        if not c.widget_name(w).lower().startswith('body'):
            return 'break'

        self.language = g.scanForAtLanguage(c,c.p)
        if w and self.language == 'python' and (k.enable_autocompleter or force):
            self.start(event=event,w=w)

        return 'break'
    #@-node:ekr.20061031131434.9:autoComplete
    #@+node:ekr.20061031131434.10:autoCompleteForce
    def autoCompleteForce (self,event=None):

        '''Show autocompletion, even if autocompletion is not presently enabled.'''

        return self.autoComplete(event,force=True)
    #@-node:ekr.20061031131434.10:autoCompleteForce
    #@+node:ekr.20061031131434.11:autoCompleterStateHandler
    def autoCompleterStateHandler (self,event):

        trace = (False or self.trace) and not g.app.unitTesting
        c = self.c ; k = self.k ; gui = g.app.gui
        tag = 'auto-complete' ; state = k.getState(tag)
        ch = gui.eventChar(event)
        keysym = gui.eventKeysym(event)

        if trace: g.trace(repr(ch),repr(keysym),state)

        if state == 0:
            c.frame.log.clearTab(self.tabName)
            self.computeCompletionList()
            k.setState(tag,1,handler=self.autoCompleterStateHandler) 
        elif keysym in (' ','Return'):
            self.finish()
        elif keysym == 'Escape':
            self.abort()
        elif keysym == 'Tab':
            self.doTabCompletion()
        elif keysym in ('\b','BackSpace'): # Horrible hack for qt plugin.
            self.doBackSpace()
        elif keysym == '.':
            self.chain()
        elif keysym == '?':
            self.info()
        elif keysym == '!':
            # Toggle between verbose and brief listing.
            self.verbose = not self.verbose
            if type(self.theObject) == types.DictType:
                self.membersList = list(self.theObject.keys())
            elif type(self.theObject) in (type((),),type([])):
                self.membersList = self.theObject
            self.computeCompletionList(verbose=self.verbose)
        elif ch and ch in string.printable:
            self.insertNormalChar(ch,keysym)
        else:
            # if trace: g.trace('ignore',repr(ch))
            return 'do-standard-keys'
    #@-node:ekr.20061031131434.11:autoCompleterStateHandler
    #@+node:ekr.20080924032842.3:getExternalCompletions
    def getExternalCompletions (self,s,p=None,language='python'):

        '''Return the completions possible at the end of string 's'.
        Return (theObject,completions):
        - theObject is None unless the last character is 's' is a period.
        - completions is the list of valid completions.'''

        c = self.c ; k = c.k
        if not p: p = c.p

        # Use a separate widget containing just s.
        self.widget = w = leoFrame.stringTextWidget(c,'compute-completions-widget')
        w.setAllText(s)

        # A big kludge: scan back for the first period.
        i = len(s)-1
        while i > 0 and s[i] != '.':
            i -= 1
        if s[i] == '.': i += 1
        prefix = s[i:].strip()

        # Remember the prefix, but put the insert before the period.
        w.setSelectionRange(i, len(s)-1, insert=i)

        # Init the ivars...
        self.language = p and g.scanForAtLanguage(c,p) or language
        self.tabName = ''
        old_enable = c.k.enable_autocompleter

        # Get the completions.
        try:
            c.k.enable_autocompleter = True
            self.useTabs = False
            self.start(prefix=prefix)
        finally:
            c.k.enable_autocompleter = old_enable
            self.useTabs = True

        theObject,tabList = self.theObject,self.tabList
        self.abort()
        return theObject,tabList
    #@-node:ekr.20080924032842.3:getExternalCompletions
    #@+node:ekr.20061031131434.12:enable/disable/toggleAutocompleter/Calltips
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
    #@-node:ekr.20061031131434.12:enable/disable/toggleAutocompleter/Calltips
    #@+node:ekr.20061031131434.13:showCalltips
    def showCalltips (self,event=None,force=False):

        '''Show the calltips at the cursor.'''

        c = self.c ; k = c.k ; w = g.app.gui.eventWidget(event)
        if not w: return

        # Insert the calltip if possible, but not in headlines.
        if (k.enable_calltips or force) and not c.widget_name(w).startswith('head'):
            self.widget = w
            self.prefix = ''
            self.selection = w.getSelectionRange()
            self.selectedText = w.getSelectedText()
            self.leadinWord = self.findCalltipWord(w)
            # g.trace(self.leadinWord)
            self.theObject = None
            self.membersList = None
            self.calltip()
        else:
            # Just insert the invocation character as usual.
            k.masterCommand(event,func=None,stroke=None,commandName=None)

        return 'break'
    #@-node:ekr.20061031131434.13:showCalltips
    #@+node:ekr.20061031131434.14:showCalltipsForce
    def showCalltipsForce (self,event=None):

        '''Show the calltips at the cursor, even if calltips are not presently enabled.'''

        return self.showCalltips(event,force=True)
    #@-node:ekr.20061031131434.14:showCalltipsForce
    #@+node:ekr.20061031131434.15:showAutocompleter/CalltipsStatus
    def showAutocompleterStatus (self):
        '''Show the autocompleter status on the status line.'''

        k = self.k
        if not g.unitTesting:
            s = 'autocompleter %s' % g.choose(k.enable_autocompleter,'On','Off')
            g.es(s,color='red')

    def showCalltipsStatus (self):
        '''Show the autocompleter status on the status line.'''
        k = self.k
        if not g.unitTesting:
            s = 'calltips %s' % g.choose(k.enable_calltips,'On','Off')
            g.es(s,color='red')
    #@nonl
    #@-node:ekr.20061031131434.15:showAutocompleter/CalltipsStatus
    #@-node:ekr.20061031131434.8:Top level
    #@+node:ekr.20061031131434.16:Helpers
    #@+node:ekr.20061031131434.17:.abort & exit (autocompleter) (test)
    def abort (self):

        k = self.k
        k.keyboardQuit(event=None,setDefaultStatus=False)
            # Stay in the present input state.
        self.exit(restore=True)

    def exit (self,restore=False): # Called from keyboard-quit.

        k = self ; c = self.c 
        w = self.widget or c.frame.body.bodyCtrl
        for name in (self.tabName,'Modules','Info'):
            c.frame.log.deleteTab(name)
        c.widgetWantsFocusNow(w)
        i,j = w.getSelectionRange()
        if restore:
            if i != j: w.delete(i,j)
            w.insert(i,self.selectedText)
        w.setSelectionRange(j,j,insert=j)

        self.clear()
        self.theObject = None
    #@-node:ekr.20061031131434.17:.abort & exit (autocompleter) (test)
    #@+node:ekr.20061031131434.18:append/begin/popTabName
    def appendTabName (self,word):

        self.setTabName(self.tabName + word + '.')

    def beginTabName (self,word):

        # g.trace(word,g.callers())
        if word == 'self' and self.selfClassName:
            word = '%s (%s)' % (word,self.selfClassName)
        self.setTabName('AutoComplete ' + word + '.')

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
        if self.useTabs:
            if self.tabName:
                c.frame.log.deleteTab(self.tabName)
            self.tabName = s.replace('_','') or ''
            c.frame.log.clearTab(self.tabName)
    #@-node:ekr.20061031131434.18:append/begin/popTabName
    #@+node:ekr.20061031131434.19:appendToKnownObjects
    def appendToKnownObjects (self,obj):

        if 0:
            if type(obj) in (types.InstanceType,types.ModuleType,types):
                if hasattr(obj,'__name__'):
                    self.knownObjects[obj.__name__] = obj
                    # g.trace('adding',obj.__name__)
    #@-node:ekr.20061031131434.19:appendToKnownObjects
    #@+node:ekr.20061031131434.20:calltip
    def calltip (self,obj=None):

        c = self.c
        w = self.widget
        isStringMethod = False ; s = None
        # g.trace(self.leadinWord,obj)

        if self.leadinWord and (not obj or type(obj) == types.BuiltinFunctionType):
            #@        << try to set s from a Python global function >>
            #@+node:ekr.20061031131434.21:<< try to set s from a Python global function >>
            # The first line of the docstring is good enough, except for classes.
            f = __builtins__.get(self.leadinWord)
            doc = f and type(f) != types.ClassType and f.__doc__
            if doc:
                # g.trace(doc)
                s = g.splitLines(doc)
                s = args = s and s [0] or ''
                i = s.find('(')
                if i > -1: s = s [i:]
                else: s = '(' + s
                s = s and s.strip() or ''
            #@-node:ekr.20061031131434.21:<< try to set s from a Python global function >>
            #@nl

        if not s:
            #@        << get s using inspect >>
            #@+node:ekr.20061031131434.22:<< get s using inspect >>
            isStringMethod = (
                self.prevObjects and
                # type(self.prevObjects[-1]) == types.StringType
                g.isString(self.prevObjects[-1]))

            # g.trace(self.prevObjects)

            if isStringMethod and hasattr(string,obj.__name__):
                # A hack. String functions are builtins, and getargspec doesn't handle them.
                # Get the corresponding string function instead, and remove the s arg later.
                obj = getattr(string,obj.__name__)

            try:
                s1,s2,s3,s4 = inspect.getargspec(obj)
            except:
                self.extendSelection('(')
                self.finish()
                return # Not a function.  Just '('.

            s = args = inspect.formatargspec(s1,s2,s3,s4)
            #@-node:ekr.20061031131434.22:<< get s using inspect >>
            #@nl

        #@    << remove 'self' from s, but not from args >>
        #@+node:ekr.20061031131434.23:<< remove 'self' from s, but not from args >>
        if g.match(s,1,'self,'):
            s = s[0] + s[6:].strip()
        elif g.match_word(s,1,'self'):
            s = s[0] + s[5:].strip()
        #@-node:ekr.20061031131434.23:<< remove 'self' from s, but not from args >>
        #@nl
        if isStringMethod:
            #@        << remove 's' from s *and* args >>
            #@+node:ekr.20061031131434.24:<< remove 's' from s *and* args >>
            if g.match(s,1,'s,'):
                s = s[0] + s[3:]
                args = args[0] + args[3:]
            elif g.match_word(s,1,'s'):
                s = s[0] + s[2:]
                args = args[0] + args[2:]
            #@-node:ekr.20061031131434.24:<< remove 's' from s *and* args >>
            #@nl

        # s = s.rstrip(')') # Not so convenient.
        #@    << insert the text and set j1 and j2 >>
        #@+node:ekr.20061031131434.25:<< insert the text and set j1 and j2 >>
        junk,j = w.getSelectionRange() # Returns insert point if no selection.
        w.insert(j,s)
        c.frame.body.onBodyChanged('Typing')
        j1 = j + 1 ; j2 = j + len(s)
        #@-node:ekr.20061031131434.25:<< insert the text and set j1 and j2 >>
        #@nl

        # End autocompletion mode, putting the insertion point after the suggested calltip.
        self.finish()
        c.widgetWantsFocusNow(w)
        if 1: # Seems to be more useful.
            w.setSelectionRange(j1,j2,insert=j2)
        else:
            w.setInsertPoint(j2)
        #@    << put the status line >>
        #@+node:ekr.20061031131434.26:<< put the status line >>
        c.frame.clearStatusLine()
        if obj:
            name = hasattr(obj,'__name__') and obj.__name__ or repr(obj)
        else:
            name = self.leadinWord
        c.frame.putStatusLine('%s %s' % (name,args))
        #@-node:ekr.20061031131434.26:<< put the status line >>
        #@nl
    #@-node:ekr.20061031131434.20:calltip
    #@+node:ekr.20061031131434.27:chain
    def chain (self):

        c = self.c ; w = self.widget
        word = w.getSelectedText()
        old_obj = self.theObject

        if word and old_obj and type(old_obj) == type([]) and old_obj == sys.modules:
            obj = old_obj.get(word)
            if obj:
                self.theObject = obj
                self.clearTabName()
        elif word and old_obj and self.hasAttr(old_obj,word):
            self.push(old_obj)
            self.theObject = obj = self.getAttr(old_obj,word)
        else: obj = None

        if obj:
            self.appendToKnownObjects(obj)
            self.leadinWord = word
            self.membersList = self.getMembersList(obj)
            self.appendTabName(word)
            self.extendSelection('.')
            i = w.getInsertPoint()
            w.setSelectionRange(i,i,insert=i)
            # g.trace('chaining to',word,self.theObject)
            # Similar to start logic.
            self.prefix = ''
            self.selection = w.getSelectionRange()
            self.selectedText = w.getSelectedText()
            if self.membersList:
                # self.autoCompleterStateHandler(event=None)
                self.computeCompletionList()
                return
        self.extendSelection('.')
        self.finish()
    #@-node:ekr.20061031131434.27:chain
    #@+node:ekr.20061031131434.28:computeCompletionList
    def computeCompletionList (self,verbose=False):

        c = self.c ; w = self.widget
        c.widgetWantsFocus(w)
        s = w.getSelectedText()
        self.tabList,common_prefix = g.itemsMatchingPrefixInList(
            s,self.membersList,matchEmptyPrefix=True)

        if not common_prefix:
            if verbose or len(self.tabList) < 25 or not self.useTabs:
                self.tabList,common_prefix = g.itemsMatchingPrefixInList(
                    s,self.membersList,matchEmptyPrefix=True)
            else: # Show the possible starting letters.
                d = {}
                for z in self.tabList:
                    ch = z and z[0] or ''
                    if ch:
                        n = d.get(ch,0)
                        d[ch] = n + 1
                aList = [ch+'...%d' % (d.get(ch)) for ch in sorted(d)]
                self.tabList = aList

        if self.useTabs:
            c.frame.log.clearTab(self.tabName) # Creates the tab if necessary.
            if self.tabList:
                self.tabListIndex = -1 # The next item will be item 0.
                self.setSelection(common_prefix)
            g.es('','\n'.join(self.tabList),tabName=self.tabName)
    #@-node:ekr.20061031131434.28:computeCompletionList
    #@+node:ekr.20061031131434.29:doBackSpace (autocompleter)
    def doBackSpace (self):

        '''Cut back to previous prefix.'''

        trace = False and not g.unitTesting
        if trace: g.trace('(autocompleter)',
            self.prefix,self.theObject,self.prevObjects)

        c = self.c
        if self.prefix:
            self.prefix = self.prefix[:-1]
            self.setSelection(self.prefix)
            self.computeCompletionList()
        elif self.theObject:
            if self.prevObjects:
                obj = self.pop()
            else:
                obj = self.theObject
            # g.trace(self.theObject,obj)
            w = self.widget
            s = w.getAllText()
            i,junk = w.getSelectionRange()
            ch = 0 <= i-1 < len(s) and s[i-1] or ''
            # g.trace(ch)
            if ch == '.':
                self.theObject = obj
                w.delete(i-1)
                c.frame.body.onBodyChanged(undoType='Typing')
                i,j = g.getWord(s,i-2)
                word = s[i:j]
                # g.trace(i,j,repr(word))
                w.setSelectionRange(i,j,insert=j)
                self.prefix = word
                self.popTabName()
                self.membersList = self.getMembersList(obj)
                # g.trace(len(self.membersList))
                if self.membersList:
                    self.computeCompletionList()
                else:
                    self.abort()
            else:
                self.abort() # should not happen.
        else:
            self.abort()            
    #@-node:ekr.20061031131434.29:doBackSpace (autocompleter)
    #@+node:ekr.20061031131434.30:doTabCompletion (autocompleter)
    def doTabCompletion (self):

        '''Handle tab completion when the user hits a tab.'''

        c = self.c ; w = self.widget
        s = w.getSelectedText()

        if s.startswith(self.prefix) and self.tabList:
            # g.trace('cycle','prefix',repr(self.prefix),len(self.tabList),repr(s))
            # Set the label to the next item on the tab list.
            self.tabListIndex +=1
            if self.tabListIndex >= len(self.tabList):
               self.tabListIndex = 0
            self.setSelection(self.tabList[self.tabListIndex])
        else:
            self.computeCompletionList()

        c.widgetWantsFocusNow(w)
    #@-node:ekr.20061031131434.30:doTabCompletion (autocompleter)
    #@+node:ekr.20061031131434.31:extendSelection
    def extendSelection (self,s):

        '''Append s to the presently selected text.'''

        c = self.c ; w = self.widget
        c.widgetWantsFocusNow(w)

        i,j = w.getSelectionRange()
        w.insert(j,s)
        j += 1
        w.setSelectionRange(i,j,insert=j)
        c.frame.body.onBodyChanged('Typing')
    #@nonl
    #@-node:ekr.20061031131434.31:extendSelection
    #@+node:ekr.20061031131434.33:findCalltipWord
    def findCalltipWord (self,w):

        i = w.getInsertPoint()
        s = w.getAllText()
        if i > 0:
            i,j = g.getWord(s,i-1)
            word = s[i:j]
            return word
        else:
            return ''
    #@nonl
    #@-node:ekr.20061031131434.33:findCalltipWord
    #@+node:ekr.20080924032842.5:findAnchor
    def findAnchor (self,w):

        '''Returns (j,word) where j is a Python index.'''

        i = j = w.getInsertPoint()
        s = w.getAllText()

        # New in Leo 4.5: Fix a hanger by stopping when i <= 1.
        while i > 1 and s[i-1] == '.':
            i,j = g.getWord(s,i-2)

        word = s[i:j]
        if word == '.': word = None

        # g.trace(i,j,repr(word))
        return j,word
    #@nonl
    #@-node:ekr.20080924032842.5:findAnchor
    #@+node:ekr.20061031131434.34:finish
    def finish (self):

        c = self.c ; k = c.k

        k.keyboardQuit(event=None,setDefaultStatus=False)
            # Stay in the present input state.

        for name in (self.tabName,'Modules','Info'):
            c.frame.log.deleteTab(name)

        c.frame.body.onBodyChanged('Typing')
        c.recolor()
        self.clear()
        self.theObject = None
    #@-node:ekr.20061031131434.34:finish
    #@+node:ekr.20061031131434.35:getAttr and hasAttr
    # The values of self.attrDictDic are anonymous attrDict's.
    # attrDicts: keys are strings, values are lists of strings.

    def getAttr (self,obj,attr):

        '''Simulate getattr function, regardless of langauge.'''

        if self.language == 'python':
            return getattr(obj,attr)
        else:
            d = self.attrDictDict.get(self.language)
            aList = d.get(obj,[])
            return attr in aList and attr

    def hasAttr (self,obj,attr):

        '''Simulate hasattr function, regardless of langauge.'''

        if self.language == 'python':
            return hasattr(obj,attr)
        else:
            d = self.attrDictDict.get(self.language)
            aList = d.get(obj,[])
            return attr in aList
    #@-node:ekr.20061031131434.35:getAttr and hasAttr
    #@+node:ekr.20061031131434.36:getLeadinWord
    def getLeadinWord (self,w):

        self.verbose = False # User must explicitly ask for verbose.
        self.leadinWord = None
        start = w.getInsertPoint()
        s = w.getAllText()
        start -= 1
        i,word = self.findAnchor(w)

        if word and word.isdigit():
            self.membersList = []
            return False

        self.setObjectAndMembersList(word)
        # g.trace(word,self.theObject,len(self.membersList))

        if not word:
            self.membersList = []
            return False
        elif not self.theObject:
            self.membersList = []
            return False
        else:
            self.beginTabName(word)
            while 0 <= i < start and i <len(s):
                if s[i] != '.':
                    return False
                i,j = g.getWord(s,i+1)
                word = s[i:j]
                # g.trace(word,i,j,start)
                self.setObjectAndMembersList(word)
                if not self.theObject:
                    # g.trace('unknown',word)
                    return False
                self.appendTabName(word)
                i = j
            self.leadinWord = word
            return True
    #@-node:ekr.20061031131434.36:getLeadinWord
    #@+node:ekr.20061031131434.37:getMembersList
    def getMembersList (self,obj):

        '''Return a list of possible autocompletions for self.leadinWord.'''

        if obj:
            aList = inspect.getmembers(obj)
            members = ['%s:%s' % (a,g.prettyPrintType(b))
                for a,b in aList if not a.startswith('__')]
            members.sort()
            return members
        else:
            return []
    #@-node:ekr.20061031131434.37:getMembersList
    #@+node:ekr.20061031131434.38:info
    def info (self):

        c = self.c ; doc = None ; obj = self.theObject ; w = self.widget

        word = w.getSelectedText()

        if not word:
            # Never gets called, but __builtin__.f will work.
            word = self.findCalltipWord(w)
            if word:
                # Try to get the docstring for the Python global.
                f = __builtins__.get(self.leadinWord)
                doc = f and f.__doc__

        if not doc:
            if not self.hasAttr(obj,word):
                g.es('no docstring for',word,color='blue')
                return
            obj = self.getAttr(obj,word)
            doc = inspect.getdoc(obj)

        if doc:
            c.frame.log.clearTab('Info',wrap='word')
            g.es('',doc,tabName='Info')
        else:
            g.es('no docstring for',word,color='blue')
    #@-node:ekr.20061031131434.38:info
    #@+node:ekr.20061031131434.39:insertNormalChar
    def insertNormalChar (self,ch,keysym):

        k = self.k ; w = self.widget

        if g.isWordChar(ch):
            # Look ahead to see if the character completes any item.
            s = w.getSelectedText() + ch
            tabList,common_prefix = g.itemsMatchingPrefixInList(
                s,self.membersList,matchEmptyPrefix=True)
            if tabList:
                # Add the character.
                self.tabList = tabList
                self.extendSelection(ch)
                s = w.getSelectedText()
                if s.startswith(self.prefix):
                    self.prefix = self.prefix + ch
                self.computeCompletionList()
        else:
            word = w.getSelectedText()
            if ch == '(':
                # Similar to chain logic.
                obj = self.theObject
                # g.trace(obj,word,self.hasAttr(obj,word))
                if self.hasAttr(obj,word):
                    obj = self.getAttr(obj,word)
                    self.push(self.theObject)
                    self.theObject = obj
                    self.leadinWord = word
                    self.membersList = self.getMembersList(obj)
                    if k.enable_calltips:
                        # This calls self.finish if the '(' is valid.
                        self.calltip(obj)
                        return
            self.extendSelection(ch)
            self.finish()
    #@-node:ekr.20061031131434.39:insertNormalChar
    #@+node:ekr.20061031131434.40:push, pop, clear, stackNames
    def push (self,obj):

        if obj is not None:
            self.prevObjects.append(obj)
            # g.trace(self.stackNames())

    def pop (self):

        obj = self.prevObjects.pop()
        # g.trace(obj)
        return obj

    def clear (self):

        self.prevObjects = []
        # g.trace(g.callers())

    def stackNames (self):

        aList = []
        for z in self.prevObjects:
            if hasattr(z,'__name__'):
                aList.append(z.__name__)
            elif hasattr(z,'__class__'):
                aList.append(z.__class__.__name__)
            else:
                aList.append(str(z))
        return aList
    #@-node:ekr.20061031131434.40:push, pop, clear, stackNames
    #@+node:ekr.20061031131434.41:setObjectAndMembersList & helpers
    def setObjectAndMembersList (self,word):

        c = self.c

        if not word:
            # Leading dot shows all classes.
            self.leadinWord = None
            self.theObject = sys.modules
            self.membersList = list(sys.modules.keys())
            self.beginTabName('Modules')
        elif word in ( "'",'"'):
            word = 'aString' # This is in the objectsDict.
            self.clear()
            self.push(self.theObject)
            self.theObject = 'aString'
            self.membersList = self.getMembersList(self.theObject)
        elif self.theObject:
            self.getObjectFromAttribute(word)
        # elif word == 'self':
            # self.completeSelf()
        else:
            obj = self.objectDict.get(word) or sys.modules.get(word)
            self.completeFromObject(obj)

        # g.trace(word,self.theObject,len(self.membersList))
    #@+node:ekr.20061031131434.42:getObjectFromAttribute
    def getObjectFromAttribute (self,word):

        obj = self.theObject

        if obj and self.hasAttr(obj,word):
            self.push(self.theObject)
            self.theObject = self.getAttr(obj,word)
            self.appendToKnownObjects(self.theObject)
            self.membersList = self.getMembersList(self.theObject)
        else:
            # No special support for 'self' here.
            # Don't clear the stack here!
            self.membersList = []
            self.theObject = None
    #@-node:ekr.20061031131434.42:getObjectFromAttribute
    #@+node:ekr.20061031131434.43:completeSelf (not used yet)
    def completeSelf (self):

        g.trace(g.callers(4))

        # This scan will be fast if an instant object already exists.
        className,obj,p,s = self.classScanner.scan()
        # g.trace(className,obj,p,s and len(s))

        # First, look up the className.
        if not obj and className:
            obj = self.allClassesDict.get(className)
            # if obj: g.trace('found in allClassesDict: %s = %s' % (className,obj))

        # Second, create the object from class definition.
        if not obj and s:
            theClass = self.computeClassObjectFromString(className,s)
            if theClass:
                obj = self.createProxyObjectFromClass(className,theClass)
                if obj:
                    self.selfObjectsDict [className] = obj
                    # This prevents future rescanning, even if the node moves.
                    self.selfVnodesDict [p.v] = obj
        if obj:
            self.selfClassName = className
            self.push(self.theObject)
            self.theObject = obj
            self.membersList = self.getMembersList(obj=obj)
        else:
            # No further action possible or desirable.
            self.selfClassName = None
            self.theObject = None
            self.clear()
            self.membersList = []
    #@-node:ekr.20061031131434.43:completeSelf (not used yet)
    #@+node:ekr.20061031131434.44:completeFromObject
    def completeFromObject (self,obj):

        if obj:
            self.appendToKnownObjects(obj)
            self.push(self.theObject)
            self.theObject = obj
            self.membersList = self.getMembersList(obj=obj)
        else:
            self.theObject = None
            self.clear()
            self.membersList = []
    #@-node:ekr.20061031131434.44:completeFromObject
    #@-node:ekr.20061031131434.41:setObjectAndMembersList & helpers
    #@+node:ekr.20061031131434.45:setSelection
    def setSelection (self,s):

        c = self.c ; w = self.widget
        c.widgetWantsFocusNow(w)

        if w.hasSelection():
            i,j = w.getSelectionRange()
            w.delete(i,j)
        else:
            i = w.getInsertPoint()

        # Don't go past the ':' that separates the completion from the type.
        n = s.find(':')
        if n > -1: s = s[:n]

        w.insert(i,s)
        j = i + len(s)
        w.setSelectionRange(i,j,insert=j)

        # New in Leo 4.4.2: recolor immediately to preserve the new selection in the new colorizer.
        c.frame.body.recolor(c.p,incremental=True)
        # Usually this call will have no effect because the body text has not changed.
        c.frame.body.onBodyChanged('Typing')
    #@-node:ekr.20061031131434.45:setSelection
    #@+node:ekr.20061031131434.46:start
    def start (self,event=None,w=None,prefix=None):

        c = self.c
        if w: self.widget = w
        else: w = self.widget

        # We wait until now to define these dicts so that more classes and objects will exist.
        if not self.objectDict:
            self.defineClassesDict()
            self.defineObjectDict()

        self.prefix = g.choose(prefix is None,'',prefix)
        self.selection = w.getSelectionRange()
        self.selectedText = w.getSelectedText()
        flag = self.getLeadinWord(w)
        if self.membersList:
            if not flag:
                # Remove the (leading) invocation character.
                i = w.getInsertPoint()
                s = w.getAllText()
                if i > 0 and s[i-1] == '.':
                    s = g.app.gui.stringDelete(s,i-1)
                    w.setAllText(s)
                    c.frame.body.onBodyChanged('Typing')
            if self.useTabs:
                self.autoCompleterStateHandler(event)
            else:
                self.computeCompletionList()
                return self.tabList
        else:
            self.abort()
    #@-node:ekr.20061031131434.46:start
    #@-node:ekr.20061031131434.16:Helpers
    #@+node:ekr.20061031131434.47:Scanning (not used)
    if 0: # Not used at present.
        #@    @+others
        #@+node:ekr.20061031131434.48:initialScan
        # Don't call this finishCreate: the startup logic would call it too soon.

        def initialScan (self):

            g.trace(g.callers())

            self.scan(thread=True)
        #@-node:ekr.20061031131434.48:initialScan
        #@+node:ekr.20061031131434.49:scan
        def scan (self,event=None,verbose=True,thread=True):

            c = self.c
            if not c or not c.exists or c.frame.isNullFrame: return
            if g.app.unitTesting: return

            # g.trace('autocompleter')

            if 0: # thread:
                # Use a thread to do the initial scan so as not to interfere with the user.            
                def scan ():
                    #g.es("This is for testing if g.es blocks in a thread", color = 'pink' )
                    # During unit testing c gets destroyed before the scan finishes.
                    if not g.app.unitTesting:
                        self.scanOutline(verbose=True)

                t = threading.Thread(target=scan)
                t.setDaemon(True)
                t.start()
            else:
                self.scanOutline(verbose=verbose)
        #@-node:ekr.20061031131434.49:scan
        #@+node:ekr.20061031131434.50:definePatterns
        def definePatterns (self):

            self.space = r'[ \t\r\f\v ]+' # one or more whitespace characters.
            self.end = r'\w+\s*\([^)]*\)' # word (\w) ws ( any ) (can cross lines)

            # Define re patterns for various languages.
            # These patterns match method/function definitions.
            self.pats = {}
            self.pats ['python'] = re.compile(r'def\s+%s' % self.end)  # def ws word ( any ) # Can cross line boundaries.
            self.pats ['java'] = re.compile(
                r'((public\s+|private\s+|protected\s+)?(static%s|\w+%s){1,2}%s)' % (
                    self.space,self.space,self.end))
            self.pats ['perl'] = re.compile(r'sub\s+%s' % self.end)
            self.pats ['c++'] = re.compile(r'((virtual\s+)?\w+%s%s)' % (self.space,self.end))
            self.pats ['c'] = re.compile(r'\w+%s%s' % (self.space,self.end))

            # Define self.okchars for getCleaString.
            okchars = {}
            for z in string.ascii_letters:
                okchars [z] = z
            okchars ['_'] = '_'
            self.okchars = okchars 
        #@nonl
        #@-node:ekr.20061031131434.50:definePatterns
        #@+node:ekr.20061031131434.51:scanOutline
        def scanOutline (self,verbose=True):

            '''Traverse an outline and build the autocommander database.'''

            if verbose: g.es_print('scanning for auto-completer...')

            c = self.c ; k = self.k ; count = 0
            for p in c.all_positions():
                if verbose:
                    count += 1 ;
                    if (count % 200) == 0: g.es('','.',newline=False)
                language = g.scanForAtLanguage(c,p)
                # g.trace('language',language,p.h)
                s = p.b
                if k.enable_autocompleter:
                    self.scanForAutoCompleter(s)
                if k.enable_calltips:
                    self.scanForCallTip(s,language)

            if 0:
                g.trace('watchwords...\n\n')
                for key in sorted(self.watchwords):
                    aList = self.watchwords.get(key)
                    g.trace('%s:\n\n' % (key), g.listToString(aList))
            if 0:
                g.trace('calltips...\n\n')
                for key in sorted(self.calltips):
                    d = self.calltips.get(key)
                    if d:
                        g.trace('%s:\n\n' % (key), g.dictToString(d))

            if verbose:        
                g.es_print('\nauto-completer scan complete',color='blue')
        #@-node:ekr.20061031131434.51:scanOutline
        #@+node:ekr.20061031131434.52:scanForCallTip
        def scanForCallTip (self,s,language):

            '''this function scans text for calltip info'''

            d = self.calltips.get(language,{})
            pat = self.pats.get(language or 'python')

            # Set results to a list of all the function/method defintions in s.
            results = pat and pat.findall(s) or []

            for z in results:
                if isinstance(z,tuple): z = z [0]
                pieces2 = z.split('(')
                # g.trace(pieces2)
                pieces2 [0] = pieces2 [0].split() [-1]
                a, junk = pieces2 [0], pieces2 [1]
                aList = d.get(a,[])
                if str(z) not in aList:
                    aList.append(str(z))
                    d [a] = aList

            self.calltips [language] = d
        #@-node:ekr.20061031131434.52:scanForCallTip
        #@+node:ekr.20061031131434.53:scanForAutoCompleter
        def scanForAutoCompleter (self,s):

            '''This function scans text for the autocompleter database.'''

            aList = [] ; t1 = s.split('.')

            if 1: # Slightly faster.
                t1 = s.split('.') ; 
                i = 0 ; n = len(t1)-1
                while i < n:
                    self.makeAutocompletionList(t1[i],t1[i+1],aList)
                    i += 1
            else:
                if g.isPython3:
                    from functools import reduce
                reduce(lambda a,b: self.makeAutocompletionList(a,b,aList),t1)

            if aList:
                for a, b in aList:
                    z = self.watchwords.get(a,[])
                    if str(b) not in z:
                        z.append(str(b))
                        self.watchwords [a] = z
        #@+node:ekr.20061031131434.54:makeAutocompletionList
        def makeAutocompletionList (self,a,b,glist):

            '''We have seen a.b, where a and b are arbitrary strings.
            Append (a1.b1) to glist.
            To compute a1, scan backwards in a until finding whitespace.
            To compute b1, scan forwards in b until finding a char not in okchars.
            '''

            if 1: # Do everything inline.  It's a few percent faster.

                # Compute reverseFindWhitespace inline.
                i = len(a) -1
                while i >= 0:
                    if a[i].isspace() or a [i] == '.':
                        a1 = a [i+1:] ; break
                    i -= 1
                else:
                    a1 = a

                # Compute getCleanString inline.
                i = 0
                for ch in b:
                    if ch not in self.okchars:
                        b1 = b[:i] ; break
                    i += 1
                else:
                    b1 = b

                if b1:
                    glist.append((a1,b1),)

                return b # Not needed unless we are using reduce.
            else:
                a1 = self.reverseFindWhitespace(a)
                if a1:
                    b1 = self.getCleanString(b)
                    if b1:
                        glist.append((a1,b1))
                return b
        #@+node:ekr.20061031131434.55:reverseFindWhitespace
        def reverseFindWhitespace (self,s):

            '''Return the longest tail of s containing no whitespace or period.'''

            i = len(s) -1
            while i >= 0:
                if s[i].isspace() or s [i] == '.': return s [i+1:]
                i -= 1

            return s
        #@-node:ekr.20061031131434.55:reverseFindWhitespace
        #@+node:ekr.20061031131434.56:getCleanString
        def getCleanString (self,s):

            '''Return the prefix of s containing only chars in okchars.'''

            i = 0
            for ch in s:
                if ch not in self.okchars:
                    return s[:i]
                i += 1

            return s
        #@-node:ekr.20061031131434.56:getCleanString
        #@-node:ekr.20061031131434.54:makeAutocompletionList
        #@-node:ekr.20061031131434.53:scanForAutoCompleter
        #@-others
    #@-node:ekr.20061031131434.47:Scanning (not used)
    #@+node:ekr.20061031131434.57:Proxy classes and objects
    #@+node:ekr.20061031131434.58:createProxyObjectFromClass
    def createProxyObjectFromClass (self,className,theClass):

        '''Create a dummy instance object by instantiating theClass with a dummy ctor.'''

        if 0: # Calling the real ctor is way too dangerous.
            # Set args to the list of required arguments.
            args = inspect.getargs(theClass.__init__.im_func.func_code)
            args = args[0] ; n = len(args)-1
            args = [None for z in range(n)]

        def dummyCtor (self):
            pass

        try:
            obj = None
            old_init = hasattr(theClass,'__init__') and theClass.__init__
            theClass.__init__ = dummyCtor
            obj = theClass()
        finally:
            if old_init:
                theClass.__init__ = old_init
            else:
                delattr(theClass,'__init__')

        g.trace(type(theClass),obj)

        # Verify that it has all the proper attributes.
        # g.trace(g.listToString(dir(obj)))
        return obj
    #@-node:ekr.20061031131434.58:createProxyObjectFromClass
    #@+node:ekr.20061031131434.59:createClassObjectFromString
    def computeClassObjectFromString (self,className,s):

        try:
            # Add the the class definition to the present environment.
            exec(s) # Security violation!

            # Get the newly created object from the locals dict.
            theClass = locals().get(className)
            return theClass

        except Exception:
            if 1: # Could be a weird kind of user error.
                g.es_print('unexpected exception in',computeProxyObject)
                g.es_exception()
            return None
    #@-node:ekr.20061031131434.59:createClassObjectFromString
    #@-node:ekr.20061031131434.57:Proxy classes and objects
    #@+node:ekr.20061031131434.60:class forgivingParserClass
    class forgivingParserClass:

        '''A class to create a valid class instances from
        a class definition that may contain syntax errors.'''

        #@    @+others
        #@+node:ekr.20061031131434.61:ctor (forgivingParserClass)
        def __init__ (self,c):

            self.c = c
            self.excludedTnodesList = []
            self.old_putBody = None # Set in parse for communication with newPutBody.
        #@-node:ekr.20061031131434.61:ctor (forgivingParserClass)
        #@+node:ekr.20061031131434.62:parse
        def parse (self,p):

            '''The top-level parser method.

            It patches c.atFileCommands.putBody, calls the forgiving parser and finally
            restores c.atFileCommands.putBody.'''

            c = self.c

            # Create an ivar for communication with newPutBody.
            self.old_putBody = c.atFileCommands.putBody

            # Override atFile.putBody.
            c.atFileCommands.putBody = self.newPutBody

            try:
                s = None
                s = self.forgivingParser(p)
            finally:
                c.atFileCommands.putBody = self.old_putBody

            return s # Don't put a return in a finally clause.


        #@-node:ekr.20061031131434.62:parse
        #@+node:ekr.20061031131434.63:forgivingParser (leoKeys)
        def forgivingParser (self,p,suppress=False):

            c = self.c ; root = p.copy()
            self.excludedTnodesList = []
            s = g.getScript(c,root,useSelectedText=False)
            while s:
                try:
                    if not g.isPython3:
                        s = g.toEncodedString(s)
                    compile(s+'\n','<string>','exec')
                    break
                except SyntaxError:
                    fileName, n = g.getLastTracebackFileAndLineNumber()
                    p = self.computeErrorNode(c,root,n,lines=g.splitLines(s))
                    if not p or p == root:
                        if not suppress:
                            g.es_print('syntax error in class node: can not continue')
                        s = None ; break
                    else:
                        # g.es_print('syntax error: deleting',p.h)
                        self.excludedTnodesList.append(p.v)
                        s = g.getScript(c,root,useSelectedText=False)
                except Exception:
                    g.trace('unexpected exception')
                    g.es_exception()
                    break
            return s or ''
        #@-node:ekr.20061031131434.63:forgivingParser (leoKeys)
        #@+node:ekr.20061031131434.64:computeErrorNode (leoKeys)
        def computeErrorNode (self,c,root,n,lines):

            '''The from c.goToLineNumber that applies to scripts.
            Unlike c.gotoLineNumberOpen, this function returns a position.'''

            if n == 1 or n >= len(lines):
                return root

            # vnodeName, junk, junk, junk, junk = c.convertLineToVnodeNameIndexLine(
                # lines, n, root, scriptFind = True)

            goto = goToLineNumber(c)
            vnodeName,junk,junk,junk = goto.findVnode(
                root,lines,n,ignoreSentinels)

            if vnodeName:
                for p in root.self_and_subtree():
                    if p.matchHeadline(vnodeName):
                        return p

            return None
        #@-node:ekr.20061031131434.64:computeErrorNode (leoKeys)
        #@+node:ekr.20061031131434.65:newPutBody
        def newPutBody (self,p,oneNodeOnly=False,fromString=''):

            if p.v in self.excludedTnodesList:
                pass
                # g.trace('ignoring',p.h)
            else:
                self.old_putBody(p,oneNodeOnly,fromString)
        #@-node:ekr.20061031131434.65:newPutBody
        #@-others
    #@-node:ekr.20061031131434.60:class forgivingParserClass
    #@+node:ekr.20061031131434.66:class classScannerClass
    class classScannerClass:

        '''A class to find class definitions in a node or its parents.'''

        #@    @+others
        #@+node:ekr.20061031131434.67:ctor
        def __init__ (self,c):

            self.c = c

            # Ignore @root for now:
            # self.start_in_doc = c.config.getBool('at_root_bodies_start_in_doc_mode')

            self.start_in_doc = False
        #@-node:ekr.20061031131434.67:ctor
        #@+node:ekr.20061031131434.68:scan
        def scan (self):

            c = self.c

            className,obj,p = self.findParentClass(c.p)
            # g.trace(className,obj,p)

            if p and not obj:
                parser = c.k.autoCompleter.forgivingParser
                s = parser.parse(p)
            else:
                s = None

            return className,obj,p,s
        #@-node:ekr.20061031131434.68:scan
        #@+node:ekr.20061031131434.69:findParentClass
        def findParentClass (self,root):

            autoCompleter = self.c.k.autoCompleter

            # First, see if any parent has already been scanned.
            for p in root.self_and_parents():
                obj = autoCompleter.selfVnodesDict.get(p.v)
                if obj:
                    # g.trace('found',obj,'in',p.h)
                    return None,obj,p

            # Next, do a much slower scan.
            # g.trace('slow scanning...')
            for p in root.self_and_parents():
                className = self.findClass(p)
                if className:
                    # g.trace('found',className,'in',p.h)
                    return className,None,p

            return None,None,None
        #@-node:ekr.20061031131434.69:findParentClass
        #@+node:ekr.20061031131434.70:findClass & helpers
        def findClass (self,p):

            lines = g.splitLines(p.b)
            inDoc = self.start_in_doc
            # g.trace(p.h)
            for s in lines:
                if inDoc:
                    if self.endsDoc(s):
                        inDoc = False
                else:
                    if self.startsDoc(s):
                        inDoc = True
                    else:
                        # Not a perfect scan: a triple-string could start with 'class',
                        # but perfection is not important.
                        className = self.startsClass(s)
                        if className: return className
            else:
                return None
        #@+node:ekr.20061031131434.71:endsDoc
        def endsDoc (self,s):

            return s.startswith('@c')
        #@-node:ekr.20061031131434.71:endsDoc
        #@+node:ekr.20061031131434.72:startsClass
        def startsClass (self,s):

            if s.startswith('class'):
                i = 5
                i = g.skip_ws(s,i)
                j = g.skip_id(s,i)
                word = s[i:j]
                # g.trace(word)
                return word
            else:
                return None
        #@-node:ekr.20061031131434.72:startsClass
        #@+node:ekr.20061031131434.73:startsDoc
        def startsDoc (self,s):

            for s2 in ('@doc','@ ','@\n', '@r', '@\t'):
                if s.startswith(s2):
                    return True
            else:
                return False
        #@-node:ekr.20061031131434.73:startsDoc
        #@-node:ekr.20061031131434.70:findClass & helpers
        #@-others
    #@-node:ekr.20061031131434.66:class classScannerClass
    #@-others
#@-node:ekr.20061031131434.4:class autoCompleterClass
#@+node:ekr.20061031131434.74:class keyHandlerClass
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

    #@    @+others
    #@+node:ekr.20061031131434.75: Birth (keyHandler)
    #@+node:ekr.20061031131434.76: ctor (keyHandler)
    def __init__ (self,c,useGlobalKillbuffer=False,useGlobalRegisters=False):

        '''Create a key handler for c.
        c.frame.miniBufferWidget is a Tk.Label.

        useGlobalRegisters and useGlobalKillbuffer indicate whether to use
        global (class vars) or per-instance (ivars) for kill buffers and registers.'''

        # g.trace('base keyHandler',g.callers())

        self.c = c
        self.dispatchEvent = None
        self.inited = False # Set at end of finishCreate.
        self.widget = c.frame.miniBufferWidget
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
        #@    << define externally visible ivars >>
        #@+node:ekr.20061031131434.78:<< define externally visible ivars >>
        self.abbrevOn = False # True: abbreviations are on.
        self.arg = '' # The value returned by k.getArg.
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
        #@-node:ekr.20061031131434.78:<< define externally visible ivars >>
        #@nl
        #@    << define internal ivars >>
        #@+node:ekr.20061031131434.79:<< define internal ivars >>
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
        #@-node:ekr.20061031131434.79:<< define internal ivars >>
        #@nl

        self.defineTkNames()
        self.defineSpecialKeys()
        self.defineSingleLineCommands()
        self.defineMultiLineCommands()
        self.autoCompleter = autoCompleterClass(self)
        self.setDefaultUnboundKeyAction()
    #@-node:ekr.20061031131434.76: ctor (keyHandler)
    #@+node:ekr.20061031131434.80:k.finishCreate & helpers
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
    #@+node:ekr.20061031131434.81:createInverseCommandsDict
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
    #@-node:ekr.20061031131434.81:createInverseCommandsDict
    #@-node:ekr.20061031131434.80:k.finishCreate & helpers
    #@+node:ekr.20061031131434.82:setDefaultUnboundKeyAction
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
    #@-node:ekr.20061031131434.82:setDefaultUnboundKeyAction
    #@+node:ekr.20070123143428:k.defineTkNames
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
    #@nonl
    # The following are not translated, so what appears in the menu 
    # is the same as what is passed to Tk.  Case is significant.
    # Note: the Tk documentation states that not all of these may be 
    # available on all platforms.
    # 
    # Num_Lock, Pause, Scroll_Lock, Sys_Req,
    # KP_Add, KP_Decimal, KP_Divide, KP_Enter, KP_Equal,
    # KP_Multiply, KP_Separator,KP_Space, KP_Subtract, KP_Tab,
    # KP_F1,KP_F2,KP_F3,KP_F4,
    # KP_0,KP_1,KP_2,KP_3,KP_4,KP_5,KP_6,KP_7,KP_8,KP_9,
    # Insert
    #@-at
    #@-node:ekr.20070123143428:k.defineTkNames
    #@+node:ekr.20080509064108.6:k.defineSingleLineCommands
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
    #@-node:ekr.20080509064108.6:k.defineSingleLineCommands
    #@+node:ekr.20080509064108.7:k.defineMultiLineCommands
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
    #@-node:ekr.20080509064108.7:k.defineMultiLineCommands
    #@+node:ekr.20070123085931:k.defineSpecialKeys
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

    #@-node:ekr.20070123085931:k.defineSpecialKeys
    #@+node:ekr.20061101071425:oops
    def oops (self):

        g.trace('Should be defined in subclass:',g.callers(4))
    #@-node:ekr.20061101071425:oops
    #@-node:ekr.20061031131434.75: Birth (keyHandler)
    #@+node:ekr.20061031131434.88:Binding (keyHandler)
    #@+node:ekr.20061031131434.89:bindKey
    def bindKey (self,pane,shortcut,callback,commandName,modeFlag=False):

        '''Bind the indicated shortcut (a Tk keystroke) to the callback.

        No actual gui bindings are made: only entries in k.masterBindingsDict.'''

        trace = False and not g.unitTesting
        k = self ; c = k.c

        # g.trace(pane,shortcut,commandName)
        if not shortcut:
            # g.trace('No shortcut for %s' % commandName)
            return False
        #@    << give warning and return if we try to bind to Enter or Leave >>
        #@+node:ekr.20061031131434.90:<< give warning and return if we try to bind to Enter or Leave >>
        if shortcut:
            for s in ('enter','leave'):
                if -1 != shortcut.lower().find(s):
                    g.es_print('ignoring invalid key binding:','%s = %s' % (
                        commandName,shortcut),color='blue')
                    return
        #@-node:ekr.20061031131434.90:<< give warning and return if we try to bind to Enter or Leave >>
        #@nl
        if pane.endswith('-mode'):
            g.trace('oops: ignoring mode binding',shortcut,commandName,g.callers())
            return False
        bunchList = k.bindingsDict.get(shortcut,[])
        if trace: g.trace(pane,shortcut,commandName)
        try:
            k.bindKeyToDict(pane,shortcut,callback,commandName)
            b = g.bunch(pane=pane,func=callback,commandName=commandName)
            #@        << remove previous conflicting definitions from bunchList >>
            #@+node:ekr.20061031131434.92:<< remove previous conflicting definitions from bunchList >>
            if not modeFlag and self.warn_about_redefined_shortcuts:
                redefs = [str(b2.commandName) for b2 in bunchList
                    if b2.commandName != commandName and pane in ('button','all',b2.pane)
                        and not b2.pane.endswith('-mode')]
                for z in redefs:
                    g.es_print ('redefining shortcut %30s from %s to %s in %s' % (
                        shortcut,
                        g.choose(pane=='button',z,commandName),
                        g.choose(pane=='button',commandName,z),
                        pane),color='red')

            if not modeFlag:
                bunchList = [b2 for b2 in bunchList if pane not in ('button','all',b2.pane)]
            #@-node:ekr.20061031131434.92:<< remove previous conflicting definitions from bunchList >>
            #@nl
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
    #@-node:ekr.20061031131434.89:bindKey
    #@+node:ekr.20061031131434.93:bindKeyToDict
    def bindKeyToDict (self,pane,stroke,func,commandName):

        k = self
        d =  k.masterBindingsDict.get(pane,{})

        stroke = g.stripBrackets(stroke)

        if 0:
            g.trace('%-4s %-18s %-40s %s' % (
                pane,repr(stroke),commandName,func and func.__name__))

        # New in Leo 4.4.1: Allow redefintions.
        d [stroke] = g.Bunch(commandName=commandName,func=func,pane=pane,stroke=stroke)
        k.masterBindingsDict [pane] = d
    #@-node:ekr.20061031131434.93:bindKeyToDict
    #@+node:ekr.20061031131434.94:bindOpenWith
    def bindOpenWith (self,shortcut,name,data):

        '''Register an open-with command.'''

        k = self ; c = k.c

        # The first parameter must be event, and it must default to None.
        def openWithCallback(event=None,c=c,data=data):
            return c.openWith(data=data)

        # Use k.registerCommand to set the shortcuts in the various binding dicts.
        commandName = 'open-with-%s' % name.lower()
        k.registerCommand(commandName,shortcut,openWithCallback,pane='all',verbose=False)
    #@-node:ekr.20061031131434.94:bindOpenWith
    #@+node:ekr.20061031131434.95:checkBindings
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
    #@-node:ekr.20061031131434.95:checkBindings
    #@+node:ekr.20070218130238:dumpMasterBindingsDict
    def dumpMasterBindingsDict (self):

        k = self ; d = k.masterBindingsDict

        g.pr('\nk.masterBindingsDict...\n')

        for key in sorted(d):
            g.pr(key, '-' * 40)
            d2 = d.get(key)
            for key2 in sorted(d2):
                b = d2.get(key2)
                g.pr('%20s %s' % (key2,b.commandName))
    #@-node:ekr.20070218130238:dumpMasterBindingsDict
    #@+node:ekr.20061031131434.96:k.completeAllBindingsForWidget
    def completeAllBindingsForWidget (self,w):

        k = self ; d = k.bindingsDict

        # g.trace('w',w,'Alt+Key-4' in d)

        for stroke in d:
            k.makeMasterGuiBinding(stroke,w=w)
    #@-node:ekr.20061031131434.96:k.completeAllBindingsForWidget
    #@+node:ekr.20061031131434.97:k.completeAllBindings
    def completeAllBindings (self,w=None):

        '''New in 4.4b3: make an actual binding in *all* the standard places.

        The event will go to k.masterKeyHandler as always, so nothing really changes.
        except that k.masterKeyHandler will know the proper stroke.'''

        # g.trace(w)

        k = self
        for stroke in k.bindingsDict:
            k.makeMasterGuiBinding(stroke,w=w)
    #@-node:ekr.20061031131434.97:k.completeAllBindings
    #@+node:ekr.20061031131434.98:k.makeAllBindings
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
    #@-node:ekr.20061031131434.98:k.makeAllBindings
    #@+node:ekr.20061031131434.99:k.initAbbrev
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
    #@-node:ekr.20061031131434.99:k.initAbbrev
    #@+node:ekr.20061031131434.100:addModeCommands (enterModeCallback)
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
            # g.trace('leoCommands %24s = %s' % (f.__name__,key))
    #@-node:ekr.20061031131434.100:addModeCommands (enterModeCallback)
    #@+node:ekr.20061031131434.101:initSpecialIvars
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
    #@-node:ekr.20061031131434.101:initSpecialIvars
    #@+node:ekr.20061031131434.102:makeBindingsFromCommandsDict
    def makeBindingsFromCommandsDict (self):

        '''Add bindings for all entries in c.commandDict.'''

        k = self ; c = k.c ; d = c.commandsDict

        for commandName in sorted(d):
            command = d.get(commandName)
            key, bunchList = c.config.getShortcut(commandName)
            # if commandName == 'keyboard-quit': g.trace(key,bunchList)
            for bunch in bunchList:
                accel = bunch.val ; pane = bunch.pane
                # if pane.endswith('-mode'): g.trace('skipping',shortcut,commandName)
                if accel and not pane.endswith('-mode'):
                    shortcut = k.shortcutFromSetting(accel)
                    k.bindKey(pane,shortcut,command,commandName)

        # g.trace(g.listToString(sorted(k.bindingsDict))
        # g.trace('Ctrl+g',k.bindingsDict.get('Ctrl+g'))
    #@-node:ekr.20061031131434.102:makeBindingsFromCommandsDict
    #@+node:ekr.20061031131434.103:k.makeMasterGuiBinding
    def makeMasterGuiBinding (self,stroke,w=None):

        '''Make a master gui binding for stroke in pane w, or in all the standard widgets.'''

        k = self ; c = k.c ; f = c.frame

        bindStroke = k.tkbindingFromStroke(stroke)

        # if stroke.lower()=='ctrl+v':
            # g.trace('stroke',repr(stroke),'bindStroke',repr(bindStroke),'w',repr(w),'\n',g.callers())

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
    #@-node:ekr.20061031131434.103:k.makeMasterGuiBinding
    #@-node:ekr.20061031131434.88:Binding (keyHandler)
    #@+node:ekr.20061031131434.104:Dispatching (keyHandler)
    #@+node:ekr.20061031131434.105:masterCommand & helpers
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
        #@    << define specialKeysyms >>
        #@+node:ekr.20061031131434.106:<< define specialKeysyms >>
        specialKeysyms = (
            'Alt_L','Alt_R',
            'Meta_L','Meta_R', # Meta support.
            'Caps_Lock','Control_L','Control_R',
            'Num_Lock',
            'Shift_L','Shift_R',
        )
        #@nonl
        #@-node:ekr.20061031131434.106:<< define specialKeysyms >>
        #@nl
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
            #@        << add character to history >>
            #@+node:ekr.20061031131434.107:<< add character to history >>
            if stroke or len(ch) > 0:
                if len(keyHandlerClass.lossage) > 99:
                    keyHandlerClass.lossage.pop()

                # This looks like a memory leak, but isn't.
                keyHandlerClass.lossage.insert(0,(ch,stroke),)
            #@-node:ekr.20061031131434.107:<< add character to history >>
            #@nl

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

        if k.abbrevOn:
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
    #@nonl
    #@+node:ekr.20061031131434.109:callKeystrokeFunction (not used)
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
    #@-node:ekr.20061031131434.109:callKeystrokeFunction (not used)
    #@+node:ekr.20061031131434.110:k.handleDefaultChar
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
    #@-node:ekr.20061031131434.110:k.handleDefaultChar
    #@-node:ekr.20061031131434.105:masterCommand & helpers
    #@+node:ekr.20061031131434.111:fullCommand (alt-x) & helper
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
    #@+node:ekr.20061031131434.112:callAltXFunction
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
    #@-node:ekr.20061031131434.112:callAltXFunction
    #@-node:ekr.20061031131434.111:fullCommand (alt-x) & helper
    #@+node:ekr.20061031131434.113:k.endCommand
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
    #@-node:ekr.20061031131434.113:k.endCommand
    #@-node:ekr.20061031131434.104:Dispatching (keyHandler)
    #@+node:ekr.20061031131434.114:Externally visible commands
    #@+node:ekr.20061031131434.115:digitArgument & universalArgument
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
    #@-node:ekr.20061031131434.115:digitArgument & universalArgument
    #@+node:ekr.20061031131434.116:k.show/hide/toggleMinibuffer
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
    #@-node:ekr.20061031131434.116:k.show/hide/toggleMinibuffer
    #@+node:ekr.20070613133500:k.menuCommandKey
    def menuCommandKey (self,event=None):

        # This method must exist, but it never gets called.
        pass 
    #@-node:ekr.20070613133500:k.menuCommandKey
    #@+node:ekr.20070613190936:k.propagateKeyEvent
    def propagateKeyEvent (self,event):

        self.oops() # Should be overridden.
    #@nonl
    #@-node:ekr.20070613190936:k.propagateKeyEvent
    #@+node:ekr.20061031131434.117:negativeArgument (redo?)
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
    #@-node:ekr.20061031131434.117:negativeArgument (redo?)
    #@+node:ekr.20061031131434.118:numberCommand
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
    #@-node:ekr.20061031131434.118:numberCommand
    #@+node:ekr.20061031131434.119:printBindings & helper
    def printBindings (self,event=None):

        '''Print all the bindings presently in effect.'''

        k = self ; c = k.c
        d = k.bindingsDict ; tabName = 'Bindings'
        c.frame.log.clearTab(tabName)
        data = [] ; n1 = 4 ; n2 = 20
        if not d: return g.es('no bindings')
        for key in sorted(d):
            bunchList = d.get(key,[])
            for b in bunchList:
                pane = g.choose(b.pane=='all','',' %s:' % (b.pane))
                s1 = pane
                s2 = k.prettyPrintKey(key,brief=True)
                s3 = b.commandName
                n1 = max(n1,len(s1))
                n2 = max(n2,len(s2))
                data.append((s1,s2,s3),)

        # Print keys by type:
        result = []
        sep = '-' * n1
        for prefix in (
            'Alt+Ctrl+Shift', 'Alt+Shift', 'Alt+Ctrl', 'Alt+Key','Alt',
            'Ctrl+Shift', 'Ctrl', 'Shift',
            'Meta+Ctrl+Shift', 'Meta+Shift', 'Meta+Ctrl', 'Meta+Key','Meta',
            # Meta support
        ):
            data2 = []
            for item in data:
                s1,s2,s3 = item
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
    #@+node:ekr.20061031131434.120:printBindingsHelper
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
            for s1,s2,s3 in data:
                # g.es('','%*s %*s %s' % (-n1,s1,-(min(12,n2)),s2,s3),tabName='Bindings')
                result.append('%*s %*s %s\n' % (-n1,s1,-(min(12,n2)),s2,s3))
    #@-node:ekr.20061031131434.120:printBindingsHelper
    #@-node:ekr.20061031131434.119:printBindings & helper
    #@+node:ekr.20061031131434.121:printCommands
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
    #@-node:ekr.20061031131434.121:printCommands
    #@+node:ekr.20061031131434.122:repeatComplexCommand & helper
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
    #@-node:ekr.20061031131434.122:repeatComplexCommand & helper
    #@+node:ekr.20061031131434.123:set-xxx-State
    def setCommandState (self,event):
        '''Enter the 'command' editing state.'''
        # g.trace(g.callers())
        k = self
        k.setInputState('command')
        # This command is also valid in headlines.
        # k.c.bodyWantsFocusNow()
        k.showStateAndMode()

    def setInsertState (self,event):
        '''Enter the 'insert' editing state.'''
        # g.trace(g.callers())
        k = self
        k.setInputState('insert')
        # This command is also valid in headlines.
        # k.c.bodyWantsFocusNow()
        k.showStateAndMode()

    def setOverwriteState (self,event):
        '''Enter the 'overwrite' editing state.'''
        # g.trace(g.callers())
        k = self
        k.setInputState('overwrite')
        # This command is also valid in headlines.
        # k.c.bodyWantsFocusNow()
        k.showStateAndMode()
    #@-node:ekr.20061031131434.123:set-xxx-State
    #@+node:ekr.20061031131434.124:toggle-input-state
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
    #@-node:ekr.20061031131434.124:toggle-input-state
    #@-node:ekr.20061031131434.114:Externally visible commands
    #@+node:ekr.20061031131434.125:Externally visible helpers
    #@+node:ekr.20061031131434.126:manufactureKeyPressForCommandName
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
            g.trace('no shortcut for %s' % (commandName),color='red')
    #@-node:ekr.20061031131434.126:manufactureKeyPressForCommandName
    #@+node:ekr.20061031131434.127:simulateCommand
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
    #@-node:ekr.20061031131434.127:simulateCommand
    #@+node:ekr.20061031131434.128:getArg
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
            #@        << init altX vars >>
            #@+node:ekr.20061031131434.129:<< init altX vars >>
            k.argTabList = tabList and tabList[:] or []
            k.arg_completion = completion
            # g.trace('completion',completion,'tabList',tabList)

            k.mb_prefix = prefix or k.getLabel()
            k.mb_prompt = prefix or ''
            k.mb_tabList = []

            # Clear the list: any non-tab indicates that a new prefix is in effect.
            k.mb_tabListPrefix = k.getLabel()
            k.oneCharacterArg = oneCharacter
            #@-node:ekr.20061031131434.129:<< init altX vars >>
            #@nl
            # Set the states.
            bodyCtrl = c.frame.body.bodyCtrl
            c.widgetWantsFocus(bodyCtrl)
            k.afterGetArgState=returnKind,returnState,handler
            k.setState('getArg',1,k.getArg)
            k.afterArgWidget = event and event.widget or c.frame.body.bodyCtrl
            if useMinibuffer: c.minibufferWantsFocusNow()
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
        else:
            # Clear the list, any other character besides tab indicates that a new prefix is in effect.
            k.mb_tabList = []
            k.updateLabel(event)
            k.mb_tabListPrefix = k.getLabel()
        return 'break'
    #@-node:ekr.20061031131434.128:getArg
    #@+node:ekr.20061031131434.130:keyboardQuit
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
    #@-node:ekr.20061031131434.130:keyboardQuit
    #@+node:ekr.20061031131434.131:k.registerCommand
    def registerCommand (self,commandName,shortcut,func,pane='all',verbose=False, wrap=True):

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
            ok = k.bindKey (pane,stroke,func,commandName) # Must be a stroke.
            k.makeMasterGuiBinding(stroke) # Must be a stroke.
            if verbose and ok and not g.app.silentMode:
                # g.trace(g.callers())
                g.es_print('','@command: %s = %s' % (
                    commandName,k.prettyPrintKey(stroke)),color='blue')
                if 0:
                    d = k.masterBindingsDict.get('button',{})
                    g.print_dict(d)
            c.frame.tree.setBindings()
        elif verbose and not g.app.silentMode:
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
    #@-node:ekr.20061031131434.131:k.registerCommand
    #@+node:ekr.20071212104050:k.overrideCommand
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
    #@-node:ekr.20071212104050:k.overrideCommand
    #@-node:ekr.20061031131434.125:Externally visible helpers
    #@+node:ekr.20061031131434.145:Master event handlers (keyHandler)
    #@+node:ekr.20061031131434.146:masterKeyHandler & helpers
    master_key_count = 0

    def masterKeyHandler (self,event,stroke=None):

        '''This is the handler for almost all key bindings.'''

        #@    << define vars >>
        #@+node:ekr.20061031131434.147:<< define vars >>
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
        #@nonl
        #@-node:ekr.20061031131434.147:<< define vars >>
        #@nl
        trace = False and not g.app.unitTesting # or self.trace_masterKeyHandler)
        traceGC = self.trace_masterKeyHandlerGC and not g.app.unitTesting
        verbose = True

        if keysym in special_keys:
            if trace and verbose: g.trace('keysym',keysym)
            return None
        if traceGC: g.printNewObjects('masterKey 1')
        if trace: g.trace('stroke:',repr(stroke),'keysym:',
            repr(event.keysym),'ch:',repr(event.char),'state',state)

        # Handle keyboard-quit first.
        if k.abortAllModesKey and stroke == k.abortAllModesKey:
            if c.macroCommands.recordingMacro:
                c.macroCommands.endKbdMacro()
                return 'break'
            else:
                return k.masterCommand(event,k.keyboardQuit,stroke,'keyboard-quit')

        if k.inState():
            done,val = k.doMode(event,state,stroke)
            if done: return val

        if traceGC: g.printNewObjects('masterKey 2')

        if stroke and isPlain:
            done,b = k.doPlainKey(event,stroke,w)
            if b: k.masterCommand(event,b.func,b.stroke,b.commandName)
            if done: return 'break'

        b = k.getPaneBinding(stroke,w)
        if b:
            if traceGC: g.printNewObjects('masterKey 3')
            return k.masterCommand(event,b.func,b.stroke,b.commandName)
        else:
            if traceGC: g.printNewObjects('masterKey 4')
            return k.handleUnboundKeys(event,char,keysym,stroke)
    #@+node:ekr.20061031131434.108:callStateFunction
    def callStateFunction (self,event):

        k = self ; val = None ; ch = g.app.gui.eventChar(event)

        # g.trace(k.state.kind,'ch',ch,'ignore-non-ascii',k.ignore_unbound_non_ascii_keys)

        if k.state.kind:
            if (
                k.ignore_unbound_non_ascii_keys and
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
    #@-node:ekr.20061031131434.108:callStateFunction
    #@+node:ekr.20091230094319.6244:doMode
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
                if trace: g.trace('unbound key ends mode',stroke,state)
                k.endMode(event)
                return False,None
        else:
            # New in 4.4b4.
            handler = k.getStateHandler()
            if handler:
                handler(event)
            else:
                g.trace('No state handler for %s' % state)
            return True,'break'
    #@-node:ekr.20091230094319.6244:doMode
    #@+node:ekr.20091230094319.6242:doPlainKey
    def doPlainKey (self,event,stroke,w):

        '''Handle a plain key.  Return done,b.'''

        trace = False and not g.unitTesting
        k = self ; c = k.c

        # Important: only keys bound somewhere have a stroke.
        # All unbound plain keys will be handled by handleUnboundKeys.
        if k.unboundKeyAction in ('insert','overwrite'):
            for key in (k.unboundKeyAction,'body','log','text','all'):
                # Ignore bindings for all plain keys in insert/overwrite mode
                # *except* auto-complete.
                d = k.masterBindingsDict.get(key,{})
                if d:
                    b = d.get(stroke)
                    if b and b.commandName == 'auto-complete':
                        if trace: g.trace('%s: auto-complete key in %s mode' % (
                            stroke,k.unboundKeyAction))
                        return True,b

            if trace: g.trace('unbound key: %s in %s mode' % (stroke,k.unboundKeyAction))
            return True,g.bunch(func=None,stroke=stroke,commandName=None)

        # Ignore all command-state keys if we are not in a text widget.
        elif k.unboundKeyAction == 'command':
            if g.app.gui.isTextWidget(w):
                return False,None
            else:
                c.onCanvasKey(event)
                return True,None
        else:
            return False,None
    #@-node:ekr.20091230094319.6242:doPlainKey
    #@+node:ekr.20091230094319.6240:getPaneBinding
    def getPaneBinding (self,stroke,w):

        trace = False and not g.unitTesting
        verbose = False
        k = self ; w_name = k.c.widget_name(w)
        keyStatesTuple = ('command','insert','overwrite')

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
                key in ('text','all') and g.app.gui.isTextWidget(w) or
                key in ('button','all')
            ):
                d = k.masterBindingsDict.get(key,{})
                if trace and verbose:
                    g.trace('key',key,'name',name,'stroke',stroke,'stroke in d.keys',stroke in d)
                    # g.trace(key,'keys',g.listToString(list(d.keys()),sort=True)) # [:5])
                if d:
                    b = d.get(stroke)
                    if b:
                        if trace: g.trace('%s found %s = %s' % (key,repr(b.stroke),b.commandName))
                        return b
    #@-node:ekr.20091230094319.6240:getPaneBinding
    #@+node:ekr.20061031131434.152:handleMiniBindings
    def handleMiniBindings (self,event,state,stroke):

        k = self ; c = k.c
        trace = False or (self.trace_masterKeyHandler and not g.app.unitTesting)

        # Special case for bindings handled in k.getArg:
        if state in ('getArg','full-command'):
            if stroke in ('BackSpace','Return','Tab','\t','Escape'):
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
                            c.minibufferWantsFocusNow() # New in Leo 4.5.
                        # Pass this on for macro recording.
                        k.masterCommand(event,b.func,stroke,b.commandName)
                        # Careful: the command could exit.
                        if c.exists and not k.silentMode:
                            c.minibufferWantsFocus()
                        return True

        return False
    #@-node:ekr.20061031131434.152:handleMiniBindings
    #@+node:ekr.20080510095819.1:k.handleUnboudKeys
    def handleUnboundKeys (self,event,char,keysym,stroke):

        trace = False and not g.unitTesting
        k = self ; c = k.c
        modesTuple = ('insert','overwrite')

        if trace: g.trace('ch: %s keysym: %s stroke %s' % (
            repr(event.char),repr(event.keysym),repr(stroke)))

        if k.unboundKeyAction == 'command':
            # Ignore all unbound characters in command mode.
            w = g.app.gui.get_focus(c)
            if w and g.app.gui.widget_name(w).lower().startswith('canvas'):
                c.onCanvasKey(event)
            return 'break'

        elif k.isFKey(stroke):
            return 'break'

        elif stroke and k.isPlainKey(stroke) and k.unboundKeyAction in modesTuple:
            # insert/overwrite normal character.  <Return> is *not* a normal character.
            if trace: g.trace('plain key in insert mode',repr(stroke))
            return k.masterCommand(event,func=None,stroke=stroke,commandName=None)

        elif k.ignore_unbound_non_ascii_keys and len(char) > 1:
            # (stroke.find('Alt+') > -1 or stroke.find('Ctrl+') > -1)):
            if trace: g.trace('ignoring unbound non-ascii key')
            return 'break'

        elif (
            keysym and keysym.find('Escape') != -1 or
            stroke and stroke.find('Insert') != -1
        ):
            # Never insert escape or insert characters.
            return 'break'

        else:
            if trace: g.trace(repr(stroke),'no func')
            return k.masterCommand(event,func=None,stroke=stroke,commandName=None)
    #@-node:ekr.20080510095819.1:k.handleUnboudKeys
    #@-node:ekr.20061031131434.146:masterKeyHandler & helpers
    #@+node:ekr.20061031131434.153:masterClickHandler
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
    #@-node:ekr.20061031131434.153:masterClickHandler
    #@+node:ekr.20061031131434.154:masterDoubleClickHandler
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
    #@-node:ekr.20061031131434.154:masterDoubleClickHandler
    #@+node:ekr.20061031131434.155:masterMenuHandler
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
    #@-node:ekr.20061031131434.155:masterMenuHandler
    #@-node:ekr.20061031131434.145:Master event handlers (keyHandler)
    #@+node:ekr.20061031170011.3:Minibuffer (keyHandler)
    # These may be overridden, but this code is now gui-independent.
    #@nonl
    #@+node:ekr.20061031131434.135:k.minibufferWantsFocus/Now
    def minibufferWantsFocus(self):

        c = self.c
        c.widgetWantsFocus(c.miniBufferWidget)


    def minibufferWantsFocusNow(self):

        c = self.c
        c.widgetWantsFocusNow(c.miniBufferWidget)
    #@-node:ekr.20061031131434.135:k.minibufferWantsFocus/Now
    #@+node:ekr.20061031170011.5:getLabel
    def getLabel (self,ignorePrompt=False):

        k = self ; w = self.widget
        if not w: return ''

        s = w.getAllText()

        if ignorePrompt:
            return s[len(k.mb_prefix):]
        else:
            return s or ''
    #@-node:ekr.20061031170011.5:getLabel
    #@+node:ekr.20080408060320.791:k.killLine
    def killLine (self,protect=True):

        k = self ; c = self.c
        w = self.widget
        s = w.getAllText()
        s = s[:len(k.mb_prefix)]

        w.setAllText(s)
        n = len(s)
        w.setSelectionRange(n,n,insert=n)

        if protect:
            k.mb_prefix = s
    #@-node:ekr.20080408060320.791:k.killLine
    #@+node:ekr.20061031170011.6:protectLabel
    def protectLabel (self):

        k = self ; w = self.widget
        if not w: return

        k.mb_prefix = w.getAllText()

    #@-node:ekr.20061031170011.6:protectLabel
    #@+node:ekr.20061031170011.7:resetLabel
    def resetLabel (self):

        k = self ; w = self.widget
        k.setLabelGrey('')
        k.mb_prefix = ''

        if w:    
            w.setSelectionRange(0,0,insert=0)
            state = k.unboundKeyAction
            k.setLabelBlue(label='%s State' % (state.capitalize()),protect=True)
    #@-node:ekr.20061031170011.7:resetLabel
    #@+node:ekr.20061031170011.8:setLabel
    def setLabel (self,s,protect=False):

        trace = (False or self.trace_minibuffer) and not g.app.unitTesting
        k = self ; c = k.c ; w = self.widget
        if not w: return

        if trace: g.trace(repr(s),g.callers(4))

        w.setAllText(s)
        n = len(s)
        w.setSelectionRange(n,n,insert=n)

        if protect:
            k.mb_prefix = s
    #@-node:ekr.20061031170011.8:setLabel
    #@+node:ekr.20061031170011.9:extendLabel
    def extendLabel(self,s,select=False,protect=False):

        k = self ; c = k.c ; w = self.widget
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
    #@-node:ekr.20061031170011.9:extendLabel
    #@+node:ekr.20080408060320.790:selectAll
    def selectAll (self):

        '''Select all the user-editable text of the minibuffer.'''

        w = self.widget
        i,j = self.getEditableTextRange()
        w.setSelectionRange(i,j,insert=j)


    #@-node:ekr.20080408060320.790:selectAll
    #@+node:ekr.20061031170011.10:setLabelBlue
    def setLabelBlue (self,label=None,protect=False):

        k = self ; w = k.widget
        if not w: return

        w.setBackgroundColor(self.minibuffer_background_color) # 'lightblue')

        if label is not None:
            k.setLabel(label,protect)
    #@-node:ekr.20061031170011.10:setLabelBlue
    #@+node:ekr.20061031170011.11:setLabelGrey
    def setLabelGrey (self,label=None):

        k = self ; w = self.widget
        if not w: return

        w.setBackgroundColor(self.minibuffer_warning_color) # 'lightgrey')

        if label is not None:
            k.setLabel(label)

    setLabelGray = setLabelGrey
    #@-node:ekr.20061031170011.11:setLabelGrey
    #@+node:ekr.20080510153327.2:setLabelRed
    def setLabelRed (self,label=None,protect=False):

        k = self ; w = self.widget
        if not w: return

        w.setForegroundColor(self.minibuffer_error_color) # 'red')

        if label is not None:
            k.setLabel(label,protect)
    #@-node:ekr.20080510153327.2:setLabelRed
    #@+node:ekr.20061031170011.12:updateLabel
    def updateLabel (self,event):

        '''Mimic what would happen with the keyboard and a Text editor
        instead of plain accumalation.'''

        trace = False or self.trace_minibuffer and not g.app.unitTesting
        k = self ; c = k.c ; w = self.widget
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
    #@nonl
    #@-node:ekr.20061031170011.12:updateLabel
    #@+node:ekr.20061031170011.13:getEditableTextRange
    def getEditableTextRange (self):

        k = self ; w = self.widget
        trace = self.trace_minibuffer and not g.app.unitTesting

        s = w.getAllText()
        # g.trace(len(s),repr(s))

        i = len(k.mb_prefix)
        j = len(s)

        trace and g.trace(i,j)
        return i,j
    #@-node:ekr.20061031170011.13:getEditableTextRange
    #@-node:ekr.20061031170011.3:Minibuffer (keyHandler)
    #@+node:ekr.20061031131434.156:Modes
    #@+node:ekr.20061031131434.157:badMode
    def badMode(self,modeName):

        k = self

        k.clearState()
        if modeName.endswith('-mode'): modeName = modeName[:-5]
        k.setLabelGrey('@mode %s is not defined (or is empty)' % modeName)
    #@-node:ekr.20061031131434.157:badMode
    #@+node:ekr.20061031131434.158:createModeBindings
    def createModeBindings (self,modeName,d,w):

        '''Create mode bindings for the named mode using dictionary d for w, a text widget.'''

        k = self ; c = k.c

        for commandName in d:
            if commandName in ('*entry-commands*','*command-prompt*'):
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
                    if 0:
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
    #@-node:ekr.20061031131434.158:createModeBindings
    #@+node:ekr.20061031131434.159:endMode
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
    #@-node:ekr.20061031131434.159:endMode
    #@+node:ekr.20061031131434.160:enterNamedMode
    def enterNamedMode (self,event,commandName):

        k = self ; c = k.c
        modeName = commandName[6:]
        c.inCommand = False # Allow inner commands in the mode.
        k.generalModeHandler(event,modeName=modeName)
    #@-node:ekr.20061031131434.160:enterNamedMode
    #@+node:ekr.20061031131434.161:exitNamedMode
    def exitNamedMode (self,event):

        k = self

        if k.inState():
            k.endMode(event)

        k.showStateAndMode()
    #@-node:ekr.20061031131434.161:exitNamedMode
    #@+node:ekr.20061031131434.162:generalModeHandler
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
    #@-node:ekr.20061031131434.162:generalModeHandler
    #@+node:ekr.20061031131434.163:initMode
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
        w = g.choose(k.silentMode,k.modeWidget,k.widget)
        k.createModeBindings(modeName,d,w)
        k.showStateAndMode(prompt=prompt)
    #@-node:ekr.20061031131434.163:initMode
    #@+node:ekr.20061031131434.164:reinitMode
    def reinitMode (self,modeName):

        k = self ; c = k.c

        d = k.modeBindingsDict

        k.inputModeName = modeName
        w = g.choose(k.silentMode,k.modeWidget,k.widget)
        k.createModeBindings(modeName,d,w)

        if k.silentMode:
            k.showStateAndMode()
        else:
            # Do not set the status line here.
            k.setLabelBlue(modeName+': ',protect=True)

    #@-node:ekr.20061031131434.164:reinitMode
    #@+node:ekr.20061031131434.165:modeHelp & helper
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
    #@+node:ekr.20061031131434.166:modeHelpHelper
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
    #@-node:ekr.20061031131434.166:modeHelpHelper
    #@-node:ekr.20061031131434.165:modeHelp & helper
    #@-node:ekr.20061031131434.156:Modes
    #@+node:ekr.20061031131434.167:Shared helpers
    #@+node:ekr.20061031131434.175:k.computeCompletionList
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
    #@-node:ekr.20061031131434.175:k.computeCompletionList
    #@+node:ekr.20061031131434.176:computeInverseBindingDict
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
    #@-node:ekr.20061031131434.176:computeInverseBindingDict
    #@+node:ekr.20061031131434.168:getFileName & helpers
    def getFileName (self,event=None,handler=None,prefix='',filterExt='.leo'):

        '''Similar to k.getArg, but uses completion to indicate files on the file system.'''

        k = self ; c = k.c ; gui = g.app.gui
        tag = 'getFileName' ; state = k.getState(tag)
        tabName = 'Completion'
        keysym = gui.eventKeysym(event)
        # g.trace('state',state,'keysym',keysym)
        if state == 0:
            k.arg = ''
            #@        << init altX vars >>
            #@+node:ekr.20061031131434.169:<< init altX vars >>
            k.filterExt = filterExt
            k.mb_prefix = (prefix or k.getLabel())
            k.mb_prompt = prefix or k.getLabel()
            k.mb_tabList = []

            # Clear the list: any non-tab indicates that a new prefix is in effect.
            theDir = g.os_path_finalize(os.curdir)
            k.extendLabel(theDir,select=False,protect=False)

            k.mb_tabListPrefix = k.getLabel()
            #@-node:ekr.20061031131434.169:<< init altX vars >>
            #@nl
            # Set the states.
            k.getFileNameHandler = handler
            k.setState(tag,1,k.getFileName)
            k.afterArgWidget = event and event.widget or c.frame.body.bodyCtrl
            c.frame.log.clearTab(tabName)
            c.minibufferWantsFocusNow()
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
    #@+node:ekr.20061031131434.170:k.doFileNameBackSpace
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
    #@-node:ekr.20061031131434.170:k.doFileNameBackSpace
    #@+node:ekr.20061031131434.171:k.doFileNameChar
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
    #@-node:ekr.20061031131434.171:k.doFileNameChar
    #@+node:ekr.20061031131434.172:k.doFileNameTab
    def doFileNameTab (self):

        k = self
        common_prefix = k.computeFileNameCompletionList()

        if k.mb_tabList:
            k.setLabel(k.mb_prompt + common_prefix)
    #@-node:ekr.20061031131434.172:k.doFileNameTab
    #@+node:ekr.20061031131434.173:k.computeFileNameCompletionList
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
    #@-node:ekr.20061031131434.173:k.computeFileNameCompletionList
    #@+node:ekr.20061031131434.174:k.showFileNameTabList
    def showFileNameTabList (self):

        k = self ; tabName = 'Completion'

        for path in k.mb_tabList:
            theDir,fileName = g.os_path_split(path)
            s = g.choose(path.endswith('\\'),theDir,fileName)
            s = fileName or g.os_path_basename(theDir) + '\\'
            g.es('',s,tabName=tabName)
    #@-node:ekr.20061031131434.174:k.showFileNameTabList
    #@-node:ekr.20061031131434.168:getFileName & helpers
    #@+node:ekr.20061031131434.179:getShortcutForCommand/Name (should return lists)
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
    #@-node:ekr.20061031131434.179:getShortcutForCommand/Name (should return lists)
    #@+node:ekr.20061031131434.177:k.doBackSpace (minibuffer)
    # Used by getArg and fullCommand.

    def doBackSpace (self,defaultCompletionList,completion=True):

        '''Cut back to previous prefix and update prefix.'''

        trace = False and not g.unitTesting
        k = self ; c = k.c ; w = self.widget

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
    #@-node:ekr.20061031131434.177:k.doBackSpace (minibuffer)
    #@+node:ekr.20061031131434.178:k.doTabCompletion
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

        c.minibufferWantsFocusNow()
    #@-node:ekr.20061031131434.178:k.doTabCompletion
    #@+node:ekr.20061031131434.180:traceBinding
    def traceBinding (self,bunch,shortcut,w):

        k = self ; c = k.c ; gui = g.app.gui

        if not c.config.getBool('trace_bindings'): return

        theFilter = c.config.getString('trace_bindings_filter') or ''
        if theFilter and shortcut.lower().find(theFilter.lower()) == -1: return

        pane_filter = c.config.getString('trace_bindings_pane_filter')

        if not pane_filter or pane_filter.lower() == bunch.pane:
             g.trace(bunch.pane,shortcut,bunch.commandName,gui.widget_name(w))
    #@-node:ekr.20061031131434.180:traceBinding
    #@-node:ekr.20061031131434.167:Shared helpers
    #@+node:ekr.20061031131434.181:Shortcuts (keyHandler)
    #@+node:ekr.20090518072506.8494:isFKey
    def isFKey (self,shortcut):


        if not shortcut: return False

        s = shortcut.lower()

        return s.startswith('f') and len(s) <= 3 and s[1:].isdigit()
    #@-node:ekr.20090518072506.8494:isFKey
    #@+node:ekr.20061031131434.182:isPlainKey
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
    #@-node:ekr.20061031131434.182:isPlainKey
    #@+node:ekr.20061031131434.184:shortcutFromSetting (uses k.guiBindNamesDict)
    def shortcutFromSetting (self,setting,addKey=True):

        k = self

        trace = False and not g.unitTesting
        if not setting:return None

        s = g.stripBrackets(setting.strip())
        #@    << define cmd, ctrl, alt, shift >>
        #@+node:ekr.20061031131434.185:<< define cmd, ctrl, alt, shift >>
        s2 = s.lower()

        cmd   = s2.find("cmd") >= 0     or s2.find("command") >= 0
        ctrl  = s2.find("control") >= 0 or s2.find("ctrl") >= 0
        alt   = s2.find("alt") >= 0
        shift = s2.find("shift") >= 0   or s2.find("shft") >= 0
        meta  = s2.find("meta") >= 0
        #@-node:ekr.20061031131434.185:<< define cmd, ctrl, alt, shift >>
        #@nl
        if k.swap_mac_keys and sys.platform == "darwin":
            #@        << swap cmd and ctrl keys >>
            #@+node:ekr.20061031131434.186:<< swap cmd and ctrl keys >>
            if ctrl and not cmd:
                cmd = True ; ctrl = False
            if alt and not ctrl:
                ctrl = True ; alt = False
            #@-node:ekr.20061031131434.186:<< swap cmd and ctrl keys >>
            #@nl
        #@    << convert minus signs to plus signs >>
        #@+node:ekr.20061031131434.187:<< convert minus signs to plus signs >>
        # Replace all minus signs by plus signs, except a trailing minus:
        if s.endswith('-'):
            s = s[:-1].replace('-','+') + '-'
        else:
            s = s.replace('-','+')
        #@-node:ekr.20061031131434.187:<< convert minus signs to plus signs >>
        #@nl
        #@    << compute the last field >>
        #@+node:ekr.20061031131434.188:<< compute the last field >>
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
        #@-node:ekr.20061031131434.188:<< compute the last field >>
        #@nl
        #@    << compute shortcut >>
        #@+node:ekr.20061031131434.189:<< compute shortcut >>
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
        #@-node:ekr.20061031131434.189:<< compute shortcut >>
        #@nl
        if trace: g.trace('%20s %s' % (setting,shortcut))
        return shortcut

    canonicalizeShortcut = shortcutFromSetting # For compatibility.
    strokeFromSetting = shortcutFromSetting
    #@-node:ekr.20061031131434.184:shortcutFromSetting (uses k.guiBindNamesDict)
    #@+node:ekr.20061031131434.190:k.tkbindingFromStroke
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
    #@-node:ekr.20061031131434.190:k.tkbindingFromStroke
    #@+node:ekr.20061031131434.191:k.prettyPrintKey
    def prettyPrintKey (self,stroke,brief=False):

        k = self
        s = stroke and g.stripBrackets(stroke.strip())
        if not s: return ''

        shift = s.find("shift") >= 0 or s.find("shft") >= 0

        # Replace all minus signs by plus signs, except a trailing minus:
        if s.endswith('-'): s = s[:-1].replace('-','+') + '-'
        else:               s = s.replace('-','+')
        fields = s.split('+')
        last = fields and fields[-1]
        if last and len(last) == 1:
            prev = s[:-1]
            if last.isalpha():
                if last.isupper():
                    if not shift:
                        s = prev + 'Shift+' + last
                elif last.islower():
                    if not prev and not brief:
                        s = 'Key+' + last.upper()
                    else:
                        s = prev + last.upper()
        else:
            last = k.guiBindNamesInverseDict.get(last,last)
            if fields and fields[:-1]:
                s = '%s+%s' % ('+'.join(fields[:-1]),last)
            else:
                s = last
        # g.trace(stroke,s)
        return g.choose(brief,s,'<%s>' % s)
    #@-node:ekr.20061031131434.191:k.prettyPrintKey
    #@-node:ekr.20061031131434.181:Shortcuts (keyHandler)
    #@+node:ekr.20061031131434.193:States
    #@+node:ekr.20061031131434.194:clearState
    def clearState (self):

        k = self
        k.state.kind = None
        k.state.n = None
        k.state.handler = None
    #@-node:ekr.20061031131434.194:clearState
    #@+node:ekr.20061031131434.196:getState
    def getState (self,kind):

        k = self
        val = g.choose(k.state.kind == kind,k.state.n,0)
        # g.trace(state,'returns',val)
        return val
    #@-node:ekr.20061031131434.196:getState
    #@+node:ekr.20061031131434.195:getStateHandler
    def getStateHandler (self):

        return self.state.handler
    #@-node:ekr.20061031131434.195:getStateHandler
    #@+node:ekr.20061031131434.197:getStateKind
    def getStateKind (self):

        return self.state.kind
    #@-node:ekr.20061031131434.197:getStateKind
    #@+node:ekr.20061031131434.198:inState
    def inState (self,kind=None):

        k = self

        if kind:
            return k.state.kind == kind and k.state.n != None
        else:
            return k.state.kind and k.state.n != None
    #@-node:ekr.20061031131434.198:inState
    #@+node:ekr.20080511122507.4:setDefaultInputState
    def setDefaultInputState (self):

        k = self
        k.setInputState(k.defaultUnboundKeyAction)
    #@nonl
    #@-node:ekr.20080511122507.4:setDefaultInputState
    #@+node:ekr.20061031131434.133:setInputState
    def setInputState (self,state):

        k = self
        k.unboundKeyAction = state



    #@-node:ekr.20061031131434.133:setInputState
    #@+node:ekr.20061031131434.199:setState
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
    #@-node:ekr.20061031131434.199:setState
    #@+node:ekr.20061031131434.192:showStateAndMode
    def showStateAndMode(self,w=None,prompt=None):

        k = self ; c = k.c
        state = k.unboundKeyAction
        mode = k.getStateKind()
        inOutline = False
        if not g.app.gui: return

        if not w:
            w = g.app.gui.get_focus(c)
            if not w: return

        # g.trace(w, state, mode,g.callers(5))

        # This fixes a problem with the tk gui plugin.
        if mode and mode.lower().startswith('isearch'):
            return

        wname = g.app.gui.widget_name(w).lower()

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
        elif w and (wname.startswith('canvas') or wname.startswith('head')):
            s = 'In Outline'
            inOutline = True
        else:
            s = '%s State' % state.capitalize()

        if s:
            # g.trace(s,w,g.callers(4))
            k.setLabelBlue(label=s,protect=True)

        if w and g.app.gui.isTextWidget(w):
            k.showStateColors(inOutline,w)
    #@-node:ekr.20061031131434.192:showStateAndMode
    #@+node:ekr.20080512115455.1:showStateColors
    def showStateColors (self,inOutline,w):

        k = self ; c = k.c ; state = k.unboundKeyAction

        body = c.frame.body ; bodyCtrl = body.bodyCtrl

        if state not in ('insert','command','overwrite'):
            g.trace('bad input state',state)

        # g.trace(state,w,g.app.gui.widget_name(w),g.callers(4))

        # if inOutline and w == bodyCtrl:
            # return # Don't recolor the body.
        if w != bodyCtrl and not g.app.gui.widget_name(w).startswith('head'):
            # Don't recolor the minibuffer, log panes, etc.
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

        # g.trace(id(w),bg,fg,self)

        if w == bodyCtrl:
            body.setEditorColors(bg=bg,fg=fg)
        else:
            try:
                w.configure(bg=bg,fg=fg)
            except Exception:
                g.es_exception()
    #@-node:ekr.20080512115455.1:showStateColors
    #@-node:ekr.20061031131434.193:States
    #@+node:ekr.20061031131434.200:universalDispatcher & helpers
    def universalDispatcher (self,event):

        '''Handle accumulation of universal argument.'''

        #@    << about repeat counts >>
        #@+node:ekr.20061031131434.201:<< about repeat counts >>
        #@@nocolor

        #@+at  
        #@nonl
        # Any Emacs command can be given a numeric argument. Some 
        # commands interpret the
        # argument as a repetition count. For example, giving an 
        # argument of ten to the
        # key C-f (the command forward-char, move forward one 
        # character) moves forward ten
        # characters. With these commands, no argument is equivalent 
        # to an argument of
        # one. Negative arguments are allowed. Often they tell a 
        # command to move or act
        # backwards.
        # 
        # If your keyboard has a META key, the easiest way to 
        # specify a numeric argument
        # is to type digits and/or a minus sign while holding down 
        # the the META key. For
        # example,
        # 
        # M-5 C-n
        # 
        # moves down five lines. The characters Meta-1, Meta-2, and 
        # so on, as well as
        # Meta--, do this because they are keys bound to commands 
        # (digit-argument and
        # negative-argument) that are defined to contribute to an 
        # argument for the next
        # command.
        # 
        # Another way of specifying an argument is to use the C-u 
        # (universal-argument)
        # command followed by the digits of the argument. With C-u, 
        # you can type the
        # argument digits without holding down shift keys. To type a 
        # negative argument,
        # start with a minus sign. Just a minus sign normally means 
        # -1. C-u works on all
        # terminals.
        # 
        # C-u followed by a character which is neither a digit nor a 
        # minus sign has the
        # special meaning of "multiply by four". It multiplies the 
        # argument for the next
        # command by four. C-u twice multiplies it by sixteen. Thus, 
        # C-u C-u C-f moves
        # forward sixteen characters. This is a good way to move 
        # forward "fast", since it
        # moves about 1/5 of a line in the usual size screen. Other 
        # useful combinations
        # are C-u C-n, C-u C-u C-n (move down a good fraction of a 
        # screen), C-u C-u C-o
        # (make "a lot" of blank lines), and C-u C-k (kill four 
        # lines).
        # 
        # Some commands care only about whether there is an argument 
        # and not about its
        # value. For example, the command M-q (fill-paragraph) with 
        # no argument fills
        # text; with an argument, it justifies the text as well. 
        # (See section Filling
        # Text, for more information on M-q.) Just C-u is a handy 
        # way of providing an
        # argument for such commands.
        # 
        # Some commands use the value of the argument as a repeat 
        # count, but do something
        # peculiar when there is no argument. For example, the 
        # command C-k (kill-line)
        # with argument n kills n lines, including their terminating 
        # newlines. But C-k
        # with no argument is special: it kills the text up to the 
        # next newline, or, if
        # point is right at the end of the line, it kills the 
        # newline itself. Thus, two
        # C-k commands with no arguments can kill a non-blank line, 
        # just like C-k with an
        # argument of one. (See section Deletion and Killing, for 
        # more information on
        # C-k.)
        # 
        # A few commands treat a plain C-u differently from an 
        # ordinary argument. A few
        # others may treat an argument of just a minus sign 
        # differently from an argument
        # of -1. These unusual cases will be described when they 
        # come up; they are always
        # to make the individual command more convenient to use.
        #@-at
        #@-node:ekr.20061031131434.201:<< about repeat counts >>
        #@nl

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
    #@+node:ekr.20061031131434.202:executeNTimes
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
    #@-node:ekr.20061031131434.202:executeNTimes
    #@+node:ekr.20061031131434.203:doControlU
    def doControlU (self,event,stroke):

        k = self ; c = k.c
        ch = g.app.gui.eventChar(event)

        k.setLabelBlue('Control-u %s' % g.stripBrackets(stroke))

        if ch == '(':
            k.clearState()
            k.resetLabel()
            c.macroCommands.startKbdMacro(event)
            c.macroCommands.callLastKeyboardMacro(event)
    #@-node:ekr.20061031131434.203:doControlU
    #@-node:ekr.20061031131434.200:universalDispatcher & helpers
    #@-others
#@nonl
#@-node:ekr.20061031131434.74:class keyHandlerClass
#@-others
#@-node:ekr.20061031131434:@thin leoKeys.py
#@-leo
