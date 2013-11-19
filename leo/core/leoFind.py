#@+leo-ver=5-thin
#@+node:ekr.20060123151617: * @file leoFind.py
'''Leo's gui-independent find classes.'''

#@@language python
#@@tabwidth -4
#@@pagewidth 70

import leo.core.leoGlobals as g
import re

#@+<< global leoFind switch >>
#@+node:ekr.20131118113639.17704: ** << global leoFind switch >>
stateless_find = True # True, use stateless finds.
#@-<< global leoFind switch >>
#@+<< Theory of operation of find/change >>
#@+node:ekr.20031218072017.2414: ** << Theory of operation of find/change >>
#@@nocolor-node
#@+at
# 
# leoFind.py contains the gui-independant part of all of Leo's
# find/change code.
# 
# Such code is tricky, which is why it should be gui-independent code!
# 
# Here are the governing principles:
# 
# 1. Find and Change commands initialize themselves using only the state
#    of the present Leo window. In particular, the Find class must not
#    save internal state information from one invocation to the next.
#    This means that when the user changes the nodes, or selects new
#    text in headline or body text, those changes will affect the next
#    invocation of any Find or Change command. Failure to follow this
#    principle caused all kinds of problems earlier versions.
#    
#    There is one exception to this rule: we must remember where
#    interactive wrapped searches start.
#    
#    This principle simplifies the code because most ivars do not
#    persist. However, each command must ensure that the Leo window is
#    left in a state suitable for restarting the incremental
#    (interactive) Find and Change commands. Details of initialization
#    are discussed below.
# 
# 2. The Find and Change commands must not change the state of the
#    outline or body pane during execution. That would cause severe
#    flashing and slow down the commands a great deal. In particular,
#    c.selectPosition and c.editPosition must not be called while
#    looking for matches.
# 
# 3. When incremental Find or Change commands succeed they must leave
#    the Leo window in the proper state to execute another incremental
#    command. We restore the Leo window as it was on entry whenever an
#    incremental search fails and after any Find All and Replace All
#    command. Initialization involves setting the self.c, self.v,
#    self.in_headline, self.wrapping and self.s_text ivars.
# 
# Setting self.in_headline is tricky; we must be sure to retain the
# state of the outline pane until initialization is complete.
# Initializing the Find All and Replace All commands is much easier
# because such initialization does not depend on the state of the Leo
# window. Using the same kind of text widget for both headlines and body
# text results in a huge simplification of the code.
# 
# Indeed, the searching code does not know whether it is searching
# headline or body text. The search code knows only that self.s_text is
# a text widget that contains the text to be searched or changed and the
# insert and sel attributes of self.search_text indicate the range of
# text to be searched. Searching headline and body text simultaneously
# is complicated. The selectNextVnode() method handles the many details
# involved by setting self.s_text and its insert and sel attributes.
#@-<< Theory of operation of find/change >>

#@+others
#@+node:ekr.20070105092022.1: ** class searchWidget (to be eliminated)
### (to be deleted)
class searchWidget:

    '''A class to simulating a hidden Tk Text widget.'''

    def __repr__(self):
        return 'searchWidget id: %s' % (id(self))

    #@+others
    #@+node:ekr.20070105092438: *3* ctor (searchWidget)
    def __init__ (self,*args,**keys):

        # g.trace ('searchWidget',g.callers())

        self.s = ''    # The widget text
        self.i = 0     # The insert point
        self.sel = 0,0 # The selection range
    #@+node:ekr.20070105093138: *3* getters
    def getAllText (self):          return self.s
    def getInsertPoint (self):      return self.i       # Returns Python index.
    def getSelectionRange(self):    return self.sel     # Returns Python indices.

    #@+node:ekr.20070105102419: *3* setters (leoFind)
    def delete(self,i,j=None):
        i = self.toPythonIndex(i)
        if j is None: j = i + 1
        else: j = self.toPythonIndex(j)
        self.s = self.s[:i] + self.s[j:]
        # Bug fix: 2011/11/13: Significant in external tests.
        self.i = i
        self.sel = i,i

    def insert(self,i,s):
        if not s: return
        i = self.toPythonIndex(i)
        self.s = self.s[:i] + s + self.s[i:]
        self.i = i
        self.sel = i,i

    def setAllText (self,s):
        self.s = s
        self.i = 0
        self.sel = 0,0

    def setInsertPoint (self,i):
        self.i = i

    def setSelectionRange (self,i,j,insert=None):
        self.sel = self.toPythonIndex(i),self.toPythonIndex(j)
        if insert is not None:
            self.i = self.toPythonIndex(insert)
    #@+node:ekr.20070105092022.4: *3* toPythonIndex (leoFind)
    def toPythonIndex (self,i):

        return g.toPythonIndex(self.s,i)
    #@-others
#@+node:ekr.20061212084717: ** class leoFind (leoFind.py)
class leoFind:

    """The base class for Leo's Find commands."""

    #@+others
    #@+node:ekr.20131117164142.17021: *3* leoFind.birth
    #@+node:ekr.20031218072017.3053: *4* leoFind.__init__ & helpers
    def __init__ (self,c):
        # g.trace('(leoFind)',c.shortFileName(),id(self),g.callers())
        self.c = c
        self.clone_find_all = None
        self.errors = 0
        self.expert_mode = False # set in finishCreate.
        self.findTabManager = None
            # Created by dw.createFindTab.
        self.frame = None
        self.k = k = c.k
        assert k
        self.generation = 0 # Incremented on wrapped searches.
        self.trace = False
        # Options ivars: set by FindTabManager.init.
        self.batch = None
        self.ignore_case = None
        self.node_only = None
        self.pattern_match = None
        self.search_headline = None
        self.search_body = None
        self.suboutline_only = None
        self.mark_changes = None
        self.mark_finds = None
        self.reverse = None
        self.wrap = None
        self.whole_word = None
        # For isearch commands.
        self.stack = [] # Entries are (p,sel)
        self.isearch_ignore_case = None
        self.isearch_forward = None
        self.isearch_regexp = None
        self.findTextList = []
        self.changeTextList = []
        # Widget ivars.
        self.change_ctrl = None
        self.find_ctrl = None
        self.newStringKeys = ["radio-find-type", "radio-search-scope"]
        # These are the names of leoFind ivars.
        ### Remove these?
        self.intKeys = [
            "batch","ignore_case", "node_only",
            "pattern_match", "search_headline", "search_body",
            "suboutline_only", "mark_changes", "mark_finds", "reverse",
            "script_search","script_change","selection_only",
            "wrap", "whole_word",
        ]
        self.s_ctrl = searchWidget() # The search text for this search.
        # Status ivars.
        self.backwardAttempts = 0
        self.wrapPosition = None
        self.onlyPosition = None
        self.find_text = ""
        self.change_text = ""
        self.unstick = False
        self.re_obj = None
        # Ivars containing internal state...
        self.clone_find_all = False
        self.clone_find_all_flattened = False
        self.p = None # The position being searched.  Never saved between searches!
        self.in_headline = False # True: searching headline text.
        self.wrapping = False # True: wrapping is enabled.
        ### To be removed.
        # wrapPosition must be reset when the find pattern changes.
        self.wrapPosition = None # The start of wrapped searches: persists between calls.
        self.onlyPosition = None # The starting node for suboutline-only searches.
        self.wrapPos = None # The starting position of the wrapped search: persists between calls.
    #@+node:ekr.20131117164142.17022: *4* leoFind.finishCreate
    def finishCreate(self):
        
        # New in 4.11.1.  Must be called after keyHandler is initied.
        c = self.c
        k = c.k
        # This is used to convert Shift-Ctrl-R to replace-string.
        s = k.getShortcutForCommandName('replace-string')
        s = k.prettyPrintKey(s)
        s = k.strokeFromSetting(s)
        self.replaceStringShortcut = s
        self.expert_mode = c.config.getBool('expert-mode',default=False)
        # now that configuration settings are valid,
        # we can finish creating the Find pane.
        dw = c.frame.top
        if dw: dw.finishCreateLogPane()
    #@+node:ekr.20060123065756.1: *3* leoFind.Buttons (immediate execution)
    #@+node:ekr.20031218072017.3057: *4* changeAllButton
    def changeAllButton(self,event=None):
        '''Handle Replace All button.'''
        c = self.c
        self.setup_button()
        c.clearAllVisited() # For context reporting.
        self.changeAll()
    #@+node:ekr.20031218072017.3056: *4* changeButton
    def changeButton(self,event=None):
        '''Handle Change button.'''
        self.setup_button()
        self.change()
    #@+node:ekr.20031218072017.3058: *4* changeThenFindButton
    def changeThenFindButton(self,event=None):
        '''Handle Change, Then Find button.'''
        self.setup_button()
        self.changeThenFind()
    #@+node:ekr.20031218072017.3060: *4* findAllButton
    def findAllButton(self,event=None):
        '''Handle Find All button.'''
        c = self.c
        self.setup_button()
        ### c.clearAllVisited()
        self.findAll()
    #@+node:ekr.20031218072017.3059: *4* findButton
    def findButton(self,event=None):
        '''Handle pressing the "Find" button in the find panel.'''
        self.setup_button()
        self.findNext()
    #@+node:ekr.20131117054619.16688: *4* findPreviousButton (new in 4.11.1)
    def findPreviousButton(self,event=None):
        '''Handle the Find Previous button.'''
        self.setup_button()
        self.reverse = not self.reverse
        try:
            self.findNext()
        finally:
            self.reverse = not self.reverse
    #@+node:ekr.20031218072017.3065: *4* setup_button
    def setup_button(self):
        '''Init a search started by a button in the Find panel.'''
        c = self.c
        self.p = c.p.copy()
        c.bringToFront()
        if 0: # We _must_ retain the editing status for incremental searches!
            c.endEditing()
        self.update_ivars()
    #@+node:ekr.20031218072017.3055: *3* leoFind.Commands (immediate execution)
    #@+node:ekr.20031218072017.3061: *4* find.changeCommand
    def changeCommand(self,event=None):
        '''Handle replace command.'''
        self.setup_command()
        self.change()
    #@+node:ekr.20031218072017.3062: *4* find.changeThenFindCommand
    def changeThenFindCommand(self,event=None):
        '''Handle the replace-then-find command.'''
        self.setup_command()
        self.changeThenFind()
    #@+node:ekr.20031218072017.3063: *4* find.findNextCommand
    # The user has selected the "Find Next" menu item.

    def findNextCommand(self,event=None):
        self.setup_command()
        self.findNext()
    #@+node:ekr.20031218072017.3064: *4* find.findPrevCommand
    # The user has selected the "Find Previous" menu item.

    def findPrevCommand(self,event=None):
        self.setup_command()
        self.reverse = not self.reverse
        try:
            self.findNext()
        finally:
            self.reverse = not self.reverse
        
    ### findPreviousCommand = findPrevCommand
    #@+node:ekr.20131117164142.17015: *4* find.hideFindTab
    def hideFindTab (self,event=None):
        '''Hide the Find tab.'''
        self.c.frame.log.selectTab('Log')
    #@+node:ekr.20131117164142.16916: *4* find.openFindTab
    def openFindTab (self,event=None,show=True):
        '''Open the Find tab in the log pane.'''
        self.c.frame.log.selectTab('Find')
    #@+node:ekr.20131117164142.17016: *4* find.changeAllCommand (NEW)
    def changeAllCommand(self,event=None):
        
        self.setup_command()
        self.changeAll()
    #@+node:ekr.20031218072017.3066: *4* find.setup_command
    # Initializes a search when a command is invoked from the menu.

    def setup_command(self):

        if 0: # We _must_ retain the editing status for incremental searches!
            self.c.endEditing()
        self.update_ivars()
    #@+node:ekr.20131117164142.16939: *3* leoFind.ISearch
    #@+node:ekr.20131117164142.16941: *4* find.isearchForward
    def isearchForward (self,event):

        '''Begin a forward incremental search.

        - Plain characters extend the search.
        - !<isearch-forward>! repeats the search.
        - Esc or any non-plain key ends the search.
        - Backspace reverses the search.
        - Backspacing to an empty search pattern 
          completely undoes the effect of the search.
        '''

        self.startIncremental(event,'isearch-forward',
            forward=True,ignoreCase=False,regexp=False)
    #@+node:ekr.20131117164142.16942: *4* find.isearchBackward
    def isearchBackward (self,event):

        '''Begin a backward incremental search.

        - Plain characters extend the search backward.
        - !<isearch-forward>! repeats the search.
        - Esc or any non-plain key ends the search.
        - Backspace reverses the search.
        - Backspacing to an empty search pattern 
          completely undoes the effect of the search.
        '''

        self.startIncremental(event,'isearch-backward',
            forward=False,ignoreCase=False,regexp=False)
    #@+node:ekr.20131117164142.16943: *4* find.isearchForwardRegexp
    def isearchForwardRegexp (self,event):

        '''Begin a forward incremental regexp search.

        - Plain characters extend the search.
        - !<isearch-forward-regexp>! repeats the search.
        - Esc or any non-plain key ends the search.
        - Backspace reverses the search.
        - Backspacing to an empty search pattern 
          completely undoes the effect of the search.
        '''

        self.startIncremental(event,'isearch-forward-regexp',
            forward=True,ignoreCase=False,regexp=True)
    #@+node:ekr.20131117164142.16944: *4* find.isearchBackwardRegexp
    def isearchBackwardRegexp (self,event):

        '''Begin a backward incremental regexp search.

        - Plain characters extend the search.
        - !<isearch-forward-regexp>! repeats the search.
        - Esc or any non-plain key ends the search.
        - Backspace reverses the search.
        - Backspacing to an empty search pattern 
          completely undoes the effect of the search.
        '''

        self.startIncremental(event,'isearch-backward-regexp',
            forward=False,ignoreCase=False,regexp=True)
    #@+node:ekr.20131117164142.16945: *4* find.isearchWithPresentOptions
    def isearchWithPresentOptions (self,event):

        '''Begin an incremental search using find panel options.

        - Plain characters extend the search.
        - !<isearch-forward-regexp>! repeats the search.
        - Esc or any non-plain key ends the search.
        - Backspace reverses the search.
        - Backspacing to an empty search pattern 
          completely undoes the effect of the search.
        '''

        self.startIncremental(event,'isearch-with-present-options',
            forward=None,ignoreCase=None,regexp=None)
    #@+node:ekr.20131117164142.16946: *3* leoFind.Isearch utils
    #@+node:ekr.20131117164142.16947: *4* find.abortSearch
    def abortSearch (self):

        '''Restore the original position and selection.'''

        c = self.c ; k = self.k
        w = c.frame.body.bodyCtrl
        k.clearState()
        k.resetLabel()
        p,i,j,in_headline = self.stack[0]
        self.in_headline = in_headline
        c.selectPosition(p)
        c.redraw_after_select(p)
        c.bodyWantsFocus()
        w.setSelectionRange(i,j)
    #@+node:ekr.20131117164142.16948: *4* find.endSearch
    def endSearch (self):

        c,k = self.c,self.k

        k.clearState()
        k.resetLabel()
        c.bodyWantsFocus()
    #@+node:ekr.20131117164142.16949: *4* find.iSearch
    def iSearch (self,again=False):

        '''Handle the actual incremental search.'''

        c = self.c
        p = c.p
        k = self.k
        self.p = c.p.copy()
        reverse = not self.isearch_forward
        pattern = k.getLabel(ignorePrompt=True)
        if not pattern:
            return self.abortSearch()
        # Get the base ivars from the find tab.
        self.update_ivars()
        # Save
        oldPattern = self.find_text
        oldRegexp  = self.pattern_match
        oldReverse = self.reverse
        oldWord =  self.whole_word
        # Override
        self.pattern_match = self.isearch_regexp
        self.reverse = reverse
        self.find_text = pattern
        self.whole_word = False # Word option can't be used!
        # Prepare the search.
        if len(self.stack) <= 1: self.in_headline = False
        w = self.setWidget()
        s = w.getAllText()
        i,j = w.getSelectionRange()
        if again: ins = i if reverse else j+len(pattern)
        else:     ins = j+len(pattern) if reverse else i
        self.init_s_ctrl(s,ins)
        # Do the search!
        pos, newpos = self.findNextMatch()
        # Restore.
        self.find_text = oldPattern
        self.pattern_match = oldRegexp
        self.reverse = oldReverse
        self.whole_word = oldWord
        # Handle the results of the search.
        if pos is not None: # success.
            w = self.showSuccess(pos,newpos,showState=False)
            if w: i,j = w.getSelectionRange(sort=False)
            # else: g.trace('****')
            if not again: self.push(c.p,i,j,self.in_headline)
        elif self.wrapping:
            # g.es("end of wrapped search")
            k.setLabelRed('end of wrapped search')
        else:
            g.es("not found: %s" % (pattern))
            if not again:
                event = g.app.gui.create_key_event(c,'\b','BackSpace',w)
                k.updateLabel(event)
    #@+node:ekr.20131117164142.16950: *4* find.iSearchStateHandler
    # Called from the state manager when the state is 'isearch'

    def iSearchStateHandler (self,event):

        trace = False and not g.unitTesting
        # c = self.c
        k = self.k

        stroke = event and event.stroke or None
        s = stroke.s if stroke else ''

        if trace: g.trace('again',stroke in self.iSearchStrokes,'s',repr(s))

        # No need to recognize ctrl-z.
        if s in ('Escape','\n','Return'):
            self.endSearch()
        elif stroke in self.iSearchStrokes:
            self.iSearch(again=True)
        elif s in ('\b','BackSpace'):
            k.updateLabel(event)
            self.iSearchBackspace()
        elif (
            s.startswith('Ctrl+') or
            s.startswith('Alt+') or
            k.isFKey(s) # 2011/06/13.
        ):
            # End the search.
            self.endSearch()
            k.masterKeyHandler(event)
        else:
            if trace: g.trace('event',event)
            k.updateLabel(event)
            self.iSearch()
    #@+node:ekr.20131117164142.16951: *4* find.iSearchBackspace
    def iSearchBackspace (self):

        trace = False and not g.unitTesting
        c = self.c
        if len(self.stack) <= 1:
            self.abortSearch()
            return

        # Reduce the stack by net 1.
        junk = self.pop()
        p,i,j,in_headline = self.pop()
        self.push(p,i,j,in_headline)
        if trace: g.trace(p.h,i,j,in_headline)

        if in_headline:
            # Like self.showSuccess.
            selection = i,j,i
            c.redrawAndEdit(p,selectAll=False,
                selection=selection,
                keepMinibuffer=True)
        else:
            c.selectPosition(p)
            w = c.frame.body.bodyCtrl
            c.bodyWantsFocus()
            if i > j: i,j = j,i
            w.setSelectionRange(i,j)

        if len(self.stack) <= 1:
            self.abortSearch()



    #@+node:ekr.20131117164142.16952: *4* find.getStrokes
    def getStrokes (self,commandName):

        aList = self.inverseBindingDict.get(commandName,[])
        return [key for pane,key in aList]
    #@+node:ekr.20131117164142.16953: *4* find.push & pop
    def push (self,p,i,j,in_headline):

        data = p.copy(),i,j,in_headline
        self.stack.append(data)

    def pop (self):

        data = self.stack.pop()
        p,i,j,in_headline = data
        return p,i,j,in_headline
    #@+node:ekr.20131117164142.16954: *4* find.setWidget
    def setWidget (self):

        c = self.c ; p = c.currentPosition()
        bodyCtrl = c.frame.body.bodyCtrl
        if self.in_headline:
            w = c.edit_widget(p)
            if not w:
                # Selecting the minibuffer can kill the edit widget.
                selection = 0,0,0
                c.redrawAndEdit(p,selectAll=False,
                    selection=selection,keepMinibuffer=True)
                w = c.edit_widget(p)
            if not w: # Should never happen.
                g.trace('**** no edit widget!')
                self.in_headline = False ; w = bodyCtrl
        else:
            w = bodyCtrl
        if w == bodyCtrl:
            c.bodyWantsFocus()
        return w
    #@+node:ekr.20131117164142.16955: *4* find.startIncremental
    def startIncremental (self,event,commandName,forward,ignoreCase,regexp):

        c,k = self.c,self.k
        # None is a signal to get the option from the find tab.
        ### if forward is None or not self.findTabHandler: self.openFindTab(show=False)
        ###if not self.minibufferFindHandler:
        ###    self.minibufferFindHandler = minibufferFind(c,self.findTabHandler)
        ### getOption = self.minibufferFindHandler.getOption
        self.event = event
        ##########
        ###self.forward    = not getOption('reverse') if forward is None else forward
        ###self.ignoreCase = getOption('ignore_case') if ignoreCase is None else ignoreCase
        ###self.regexp     = getOption('pattern_match') if regexp is None else regexp
        self.isearch_forward = not self.reverse if forward is None else forward
        self.isearch_ignore_case = self.ignore_case if ignoreCase is None else ignoreCase
        self.isearch_regexp = self.pattern_match if regexp is None else regexp
        # Note: the word option can't be used with isearches!
        self.w = w = c.frame.body.bodyCtrl
        self.p1 = c.p.copy()
        self.sel1 = w.getSelectionRange(sort=False)
        i,j = self.sel1
        self.push(c.p,i,j,self.in_headline)
        self.inverseBindingDict = k.computeInverseBindingDict()
        self.iSearchStrokes = self.getStrokes(commandName)
        k.setLabelBlue('Isearch%s%s%s: ' % (
                g.choose(self.isearch_forward,'',' Backward'),
                g.choose(self.isearch_regexp,' Regexp',''),
                g.choose(self.isearch_ignore_case,' NoCase',''),
            ),protect=True)
        k.setState('isearch',1,handler=self.iSearchStateHandler)
        c.minibufferWantsFocus()
    #@+node:ekr.20131117164142.17013: *3* leoFind.Minibuffer commands
    #@+node:ekr.20131117164142.17011: *4* find.minibufferCloneFindAll
    def minibufferCloneFindAll (self,event=None):
        c = self.c ; k = self.k ; tag = 'clone-find-all'
        state = k.getState(tag)
        if state == 0:
            w = self.editWidget(event) # sets self.w
            if not w: return
            self.setupArgs(forward=None,regexp=None,word=None)
            # Init the pattern from the search pattern.
            self.stateZeroHelper(event,tag,'Clone Find All: ',self.minibufferCloneFindAll)
        else:
            k.clearState()
            k.resetLabel()
            k.showStateAndMode()
            self.generalSearchHelper(k.arg,cloneFindAll=True)
            c.treeWantsFocus()
    #@+node:ekr.20131117164142.16996: *4* find.minibufferCloneFindAllFlattened
    def minibufferCloneFindAllFlattened (self,event=None):

        c = self.c ; k = self.k ; tag = 'clone-find-all-flattened'
        state = k.getState(tag)
        if state == 0:
            w = self.editWidget(event) # sets self.w
            if not w: return
            self.setupArgs(forward=None,regexp=None,word=None)
            # Init the pattern from the search pattern.
            self.stateZeroHelper(
                event,tag,'Clone Find All Flattened: ',self.minibufferCloneFindAllFlattened)
        else:
            k.clearState()
            k.resetLabel()
            k.showStateAndMode()
            self.generalSearchHelper(k.arg,cloneFindAllFlattened=True)
            c.treeWantsFocus()
    #@+node:ekr.20131117164142.16998: *4* find.minibufferFindAll
    def minibufferFindAll (self,event=None):

        k = self.k ; state = k.getState('find-all')
        if state == 0:
            w = self.editWidget(event) # sets self.w
            if not w: return
            self.setupArgs(forward=True,regexp=False,word=True)
            k.setLabelBlue('Find All: ',protect=True)
            k.getArg(event,'find-all',1,self.minibufferFindAll)
        else:
            k.clearState()
            k.resetLabel()
            k.showStateAndMode()
            self.generalSearchHelper(k.arg,findAll=True)
    #@+node:ekr.20131117164142.16994: *4* find.minibufferReplaceAll
    def minibufferReplaceAll (self,event=None):

        k = self.k ; tag = 'replace-all' ; state = k.getState(tag)
        if state == 0:
            w = self.editWidget(event) # sets self.w
            if not w: return
            # Bug fix: 2009-5-31.
            # None denotes that we use the present value of the option.
            self.setupArgs(forward=None,regexp=None,word=None)
            k.setLabelBlue('Replace All From: ',protect=True)
            k.getArg(event,tag,1,self.minibufferReplaceAll)
        elif state == 1:
            self._sString = k.arg
            self.updateFindList(k.arg)
            s = 'Replace All: %s With: ' % (self._sString)
            k.setLabelBlue(s,protect=True)
            self.addChangeStringToLabel()
            k.getArg(event,tag,2,self.minibufferReplaceAll,completion=False,prefix=s)
        elif state == 2:
            self.updateChangeList(k.arg)
            self.lastStateHelper()
            self.generalChangeHelper(self._sString,k.arg,changeAll=True)
    #@+node:ekr.20131117164142.16983: *3* leoFind.Minibuffer utils
    #@+node:ekr.20131117164142.16992: *4* find.addChangeStringToLabel
    def addChangeStringToLabel (self,protect=True):

        c = self.c
        ftm = c.findCommands.findTabManager
        s = ftm.getChangeText()
        c.frame.log.selectTab('Find')
        c.minibufferWantsFocus()
        while s.endswith('\n') or s.endswith('\r'):
            s = s[:-1]
        c.k.extendLabel(s,select=True,protect=protect)
    #@+node:ekr.20131117164142.16993: *4* find.addFindStringToLabel
    def addFindStringToLabel (self,protect=True):

        c = self.c ; k = c.k
        ftm = c.findCommands.findTabManager
        s = ftm.getFindText()
        c.frame.log.selectTab('Find')
        c.minibufferWantsFocus()
        while s.endswith('\n') or s.endswith('\r'):
            s = s[:-1]
        k.extendLabel(s,select=True,protect=protect)
    #@+node:ekr.20131117164142.16985: *4* find.editWidget
    def editWidget (self,event,forceFocus=True):

        '''An override of baseEditCommands.editWidget

        that does *not* set focus when using anything other than the tk gui.

        This prevents this class from caching an edit widget
        that is about to be deallocated.'''

        c = self.c
        bodyCtrl = c.frame.body and c.frame.body.bodyCtrl

        # Do not cache a pointer to a headline!
        # It will die when the minibuffer is selected.
        self.w = bodyCtrl
        return self.w
    #@+node:ekr.20131117164142.16999: *4* find.generalChangeHelper
    def generalChangeHelper (self,find_pattern,change_pattern,changeAll=False):

        c = self.c
        self.setupSearchPattern(find_pattern)
        self.setupChangePattern(change_pattern)
        c.widgetWantsFocusNow(self.w)
        self.p = c.p.copy()
        if changeAll:
            self.changeAllCommand()
        else:
            # This handles the reverse option.
            self.findNextCommand()
    #@+node:ekr.20131117164142.17000: *4* find.generalSearchHelper
    def generalSearchHelper (self,pattern,
        cloneFindAll=False,
        cloneFindAllFlattened=False,
        findAll=False
    ):
        c = self.c
        self.setupSearchPattern(pattern)
        c.widgetWantsFocusNow(self.w)
        self.p = c.p.copy()
        if findAll:
            self.minibufferFindAll()
        elif cloneFindAll:
            self.minibufferCloneFindAll()
        elif cloneFindAllFlattened:
            self.minibufferCloneFindAll()
        else:
            # This handles the reverse option.
            self.findNextCommand()
    #@+node:ekr.20131117164142.17001: *4* find.lastStateHelper
    def lastStateHelper (self):

        k = self.k
        k.clearState()
        k.resetLabel()
        k.showStateAndMode()
    #@+node:ekr.20131117164142.17003: *4* find.reSearchBackward/Forward
    def reSearchBackward (self,event):

        k = self.k ; tag = 're-search-backward' ; state = k.getState(tag)

        if state == 0:
            self.setupArgs(forward=False,regexp=True,word=None)
            self.stateZeroHelper(
                event,tag,'Regexp Search Backward:',self.reSearchBackward,
                escapes=[self.replaceStringShortcut])
        elif k.getArgEscape:
            # Switch to the replace command.
            k.setState('replace-string',1,self.setReplaceString)
            self.setReplaceString(event=None)
        else:
            self.updateFindList(k.arg)
            self.lastStateHelper()
            self.generalSearchHelper(k.arg)

    def reSearchForward (self,event):

        k = self.k ; tag = 're-search-forward' ; state = k.getState(tag)
        if state == 0:
            self.setupArgs(forward=True,regexp=True,word=None)
            self.stateZeroHelper(
                event,tag,'Regexp Search:',self.reSearchForward,
                escapes=[self.replaceStringShortcut])
        elif k.getArgEscape:
            # Switch to the replace command.
            k.setState('replace-string',1,self.setReplaceString)
            self.setReplaceString(event=None)
        else:
            self.updateFindList(k.arg)
            self.lastStateHelper()
            self.generalSearchHelper(k.arg)
    #@+node:ekr.20131117164142.17004: *4* find.seachForward/Backward
    def searchBackward (self,event):

        k = self.k ; tag = 'search-backward' ; state = k.getState(tag)

        if state == 0:
            self.setupArgs(forward=False,regexp=False,word=False)
            self.stateZeroHelper(
                event,tag,'Search Backward: ',self.searchBackward,
                escapes=[self.replaceStringShortcut])
        elif k.getArgEscape:
            # Switch to the replace command.
            k.setState('replace-string',1,self.setReplaceString)
            self.setReplaceString(event=None)
        else:
            self.updateFindList(k.arg)
            self.lastStateHelper()
            self.generalSearchHelper(k.arg)

    def searchForward (self,event):

        k = self.k ; tag = 'search-forward' ; state = k.getState(tag)

        if state == 0:
            self.setupArgs(forward=True,regexp=False,word=False)
            self.stateZeroHelper(
                event,tag,'Search: ',self.searchForward,
                escapes=[self.replaceStringShortcut])
        elif k.getArgEscape:
            # Switch to the replace command.
            k.setState('replace-string',1,self.setReplaceString)
            self.setReplaceString(event=None)
        else:
            self.updateFindList(k.arg)
            self.lastStateHelper()
            self.generalSearchHelper(k.arg)
    #@+node:ekr.20131117164142.17002: *4* find.setReplaceString
    def setReplaceString (self,event):

        k = self.k ; tag = 'replace-string' ; state = k.getState(tag)
        ### pattern_match = self.getOption ('pattern_match')
        prompt = 'Replace ' + 'Regex' if self.pattern_match else 'String'
        if state == 0:
            self.setupArgs(forward=None,regexp=None,word=None)
            prefix = '%s: ' % prompt
            self.stateZeroHelper(event,tag,prefix,self.setReplaceString)
        elif state == 1:
            self._sString = k.arg
            self.updateFindList(k.arg)
            s = '%s: %s With: ' % (prompt,self._sString)
            k.setLabelBlue(s,protect=True)
            self.addChangeStringToLabel()
            k.getArg(event,'replace-string',2,self.setReplaceString,completion=False,prefix=s)
        elif state == 2:
            self.updateChangeList(k.arg)
            self.lastStateHelper()
            self.generalChangeHelper(self._sString,k.arg)
    #@+node:ekr.20131117164142.17005: *4* find.setSearchString (searchWithPresentOptions)
    def searchWithPresentOptions (self,event):
        '''Open the search pane and get the search string.'''
        trace = False and not g.unitTesting
        k = self.k ; tag = 'search-with-present-options'
        state = k.getState(tag)
        if trace: g.trace('state',state)
        if state == 0:
            self.setupArgs(forward=None,regexp=None,word=None)
            self.stateZeroHelper(
                event,tag,'Search: ',self.setSearchString,
                escapes=[self.replaceStringShortcut])
        elif k.getArgEscape:
            # Switch to the replace command.
            self.setupSearchPattern(k.arg) # 2010/01/10: update the find text immediately.
            k.setState('replace-string',1,self.setReplaceString)
            self.setReplaceString(event=None)
        else:
            self.updateFindList(k.arg)
            k.clearState()
            k.resetLabel()
            k.showStateAndMode()
            self.generalSearchHelper(k.arg)
            
    # Compatibility, especially for settings.
    setSearchString = searchWithPresentOptions
    #@+node:ekr.20131117164142.17007: *4* find.stateZeroHelper
    def stateZeroHelper (self,event,tag,prefix,handler,escapes=None):

        k = self.k
        self.w = self.editWidget(event)
        if not self.w:
            g.trace('no self.w')
            return
        k.setLabelBlue(prefix,protect=True)
        self.addFindStringToLabel(protect=False)
        # g.trace(escapes,g.callers())
        if escapes is None: escapes = []
        k.getArgEscapes = escapes
        k.getArgEscape = None # k.getArg may set this.
        k.getArg(event,tag,1,handler, # enter state 1
            tabList=self.findTextList,completion=True,prefix=prefix)
    #@+node:ekr.20131117164142.17008: *4* find.updateChange/FindList
    def updateChangeList (self,s):

        if s not in self.changeTextList:
            self.changeTextList.append(s)

    def updateFindList (self,s):

        if s not in self.findTextList:
            self.findTextList.append(s)
    #@+node:ekr.20131117164142.17009: *4* find.wordSearchBackward/Forward
    def wordSearchBackward (self,event):

        k = self.k ; tag = 'word-search-backward' ; state = k.getState(tag)

        if state == 0:
            self.setupArgs(forward=False,regexp=False,word=True)
            self.stateZeroHelper(event,tag,'Word Search Backward: ',self.wordSearchBackward)
        else:
            self.lastStateHelper()
            self.generalSearchHelper(k.arg)

    def wordSearchForward (self,event):

        k = self.k ; tag = 'word-search-forward' ; state = k.getState(tag)

        if state == 0:
            self.setupArgs(forward=True,regexp=False,word=True)
            self.stateZeroHelper(event,tag,'Word Search: ',self.wordSearchForward)
        else:
            self.lastStateHelper()
            self.generalSearchHelper(k.arg)
    #@+node:ekr.20131117164142.16915: *3* leoFind.Option commands
    #@+node:ekr.20131117164142.16919: *4* toggle checkbox commands
    def toggleFindCollapesNodes(self,event):
        '''Toggle the 'Collapse Nodes' checkbox in the find tab.'''
        c = self.c
        c.sparse_find = not c.sparse_find
        if not g.unitTesting:
            g.es('sparse_find',c.sparse_find)
    def toggleIgnoreCaseOption     (self, event):
        '''Toggle the 'Ignore Case' checkbox in the Find tab.'''
        return self.toggleOption('ignore_case')
    def toggleMarkChangesOption (self, event):
        '''Toggle the 'Mark Changes' checkbox in the Find tab.'''
        return self.toggleOption('mark_changes')
    def toggleMarkFindsOption (self, event):
        '''Toggle the 'Mark Finds' checkbox in the Find tab.'''
        return self.toggleOption('mark_finds')
    def toggleRegexOption (self, event):
        '''Toggle the 'Regexp' checkbox in the Find tab.'''
        return self.toggleOption('pattern_match')
    def toggleSearchBodyOption (self, event):
        '''Set the 'Search Body' checkbox in the Find tab.'''
        return self.toggleOption('search_body')
    def toggleSearchHeadlineOption (self, event):
        '''Toggle the 'Search Headline' checkbox in the Find tab.'''
        return self.toggleOption('search_headline')
    def toggleWholeWordOption (self, event):
        '''Toggle the 'Whole Word' checkbox in the Find tab.'''
        return self.toggleOption('whole_word')
    def toggleWrapSearchOption (self, event):
        '''Toggle the 'Wrap Around' checkbox in the Find tab.'''
        return self.toggleOption('wrap')
    def toggleOption(self,checkbox_name):
        self.findTabManager.toggle_checkbox(checkbox_name)
    #@+node:ekr.20131117164142.17019: *4* setFindScope...
    def setFindScopeEveryWhere (self,event=None):
        '''Set the 'Entire Outline' radio button in the Find tab.'''
        return self.setFindScope('entire-outline')
    def setFindScopeNodeOnly  (self,event=None):
        '''Set the 'Node Only' radio button in the Find tab.'''
        return self.setFindScope('node-only')
    def setFindScopeSuboutlineOnly (self,event=None):
        '''Set the 'Suboutline Only' radio button in the Find tab.'''
        return self.setFindScope('suboutline-only')
    def setFindScope(self,where):
        '''Set the radio buttons to the given scope'''
        self.findTabManager.set_radio_button(where)
    #@+node:ekr.20131117164142.16989: *4* showFindOptions
    def showFindOptions (self,event=None):
        '''Show the present find options in the status line.'''
        frame = self.c.frame ; z = []
        # Set the scope field.
        head  = self.search_headline ### self.getOption('search_headline')
        body  = self.search_body ### self.getOption('search_body')
        if self.suboutline_only:
            scope = 'tree'
        elif self.node_only:
            scope = 'node'
        else:
            scope = 'all'
        # scope = self.getOption('radio-search-scope')
        # d = {'entire-outline':'all','suboutline-only':'tree','node-only':'node'}
        # scope = d.get(scope) or ''
        head = g.choose(head,'head','')
        body = g.choose(body,'body','')
        sep = g.choose(head and body,'+','')
        frame.clearStatusLine()
        s = '%s%s%s %s  ' % (head,sep,body,scope)
        frame.putStatusLine(s,color='blue')
        # Set the type field.
        # script = self.script_search ### self.getOption('script_search')
        regex  = self.pattern_match ### self.getOption('pattern_match')
        ### change = self.getOption('script_change')
        # if script:
            # s1 = '*Script-find'
            # s2 = g.choose(change,'-change*','*')
            # z.append(s1+s2)
        # el
        if regex: z.append('regex')

        table = (
            ('reverse',         'reverse'),
            ('ignore_case',     'noCase'),
            ('whole_word',      'word'),
            ('wrap',            'wrap'),
            ('mark_changes',    'markChg'),
            ('mark_finds',      'markFnd'),
        )
        for ivar,s in table:
            ### val = self.getOption(ivar)
            val = getattr(self,ivar)
            if val: z.append(s)
        frame.putStatusLine(' '.join(z))
    #@+node:ekr.20131117164142.16990: *4* setupChangePattern
    def setupChangePattern (self,pattern):
        
        ftm = self.c.findCommands.findTabManager
        ftm.setChangeText(pattern)
    #@+node:ekr.20131117164142.16991: *4* setupSearchPattern
    def setupSearchPattern (self,pattern):

        ftm = self.c.findCommands.findTabManager
        ftm.setFindText(pattern)
    #@+node:ekr.20031218072017.3067: *3* leoFind.Utils
    #@+node:ekr.20031218072017.2293: *4* find.batchChange (sets start of replace-all group)
    #@+at This routine performs a single batch change operation, updating the
    # head or body string of p and leaving the result in s_ctrl. We update
    # the body if we are changing the body text of c.currentVnode().
    # 
    # s_ctrl contains the found text on entry and contains the changed text
    # on exit. pos and pos2 indicate the selection. The selection will never
    # be empty. NB: we can not assume that self.p is visible.
    #@@c

    def batchChange (self,pos1,pos2):

        c = self.c ; u = c.undoer
        p = self.p ; w = self.s_ctrl
        # Replace the selection with self.change_text
        if pos1 > pos2: pos1,pos2=pos2,pos1
        s = w.getAllText()
        if pos1 != pos2: w.delete(pos1,pos2)
        w.insert(pos1,self.change_text)
        # Update the selection.
        insert=g.choose(self.reverse,pos1,pos1+len(self.change_text))
        w.setSelectionRange(insert,insert)
        w.setInsertPoint(insert)
        # Update the node
        s = w.getAllText() # Used below.
        if self.in_headline:
            #@+<< change headline >>
            #@+node:ekr.20031218072017.2294: *5* << change headline >>
            if len(s) > 0 and s[-1]=='\n':
                s = s[:-1]
            if s != p.h:
                undoData = u.beforeChangeNodeContents(p)
                p.initHeadString(s)
                if self.mark_changes:
                    p.setMarked()
                p.setDirty()
                if not c.isChanged():
                    c.setChanged(True)
                u.afterChangeNodeContents(p,'Change Headline',undoData)
            #@-<< change headline >>
        else:
            #@+<< change body >>
            #@+node:ekr.20031218072017.2295: *5* << change body >>
            if len(s) > 0 and s[-1]=='\n': s = s[:-1]

            if s != p.b:

                undoData = u.beforeChangeNodeContents(p)

                c.setBodyString(p,s)
                if self.mark_changes:
                    p.setMarked()
                p.setDirty()
                if not c.isChanged():
                    c.setChanged(True)

                u.afterChangeNodeContents(p,'Change Body',undoData)
            #@-<< change body >>
    #@+node:ekr.20031218072017.3068: *4* find.change
    def change(self,event=None):
        if self.checkArgs():
            self.initInHeadline()
            self.changeSelection()

    replace = change
    #@+node:ekr.20031218072017.3069: *4* find.changeAll
    def changeAll(self):
        trace = False and not g.unitTesting
        c = self.c ; u = c.undoer ; undoType = 'Replace All'
        current = c.p
        if not self.checkArgs():
            if trace: g.trace('checkArgs failed')
            return
        self.initInHeadline()
        saveData = self.save()
        self.initBatchCommands()
        count = 0
        u.beforeChangeGroup(current,undoType)
        while 1:
            pos1, pos2 = self.findNextMatch()
            if pos1 is None:
                if trace: g.trace('findNextMatch failed')
                break
            if trace: g.trace(pos1,pos2,self.p and self.p.h)
            count += 1
            self.batchChange(pos1,pos2)
        p = c.p
        u.afterChangeGroup(p,undoType,reportFlag=True)
        g.es("changed:",count,"instances")
        c.redraw(p)
        self.restore(saveData)
    #@+node:ekr.20031218072017.3070: *4* find.changeSelection
    # Replace selection with self.change_text.
    # If no selection, insert self.change_text at the cursor.

    def changeSelection(self):

        c = self.c ; p = self.p
        bodyCtrl = c.frame.body and c.frame.body.bodyCtrl
        w = g.choose(self.in_headline,c.edit_widget(p),bodyCtrl)
        if not w:
            self.in_headline = False
            w = bodyCtrl
        if not w: return

        oldSel = sel = w.getSelectionRange()
        start,end = sel
        if start > end: start,end = end,start
        if start == end:
            g.es("no text selected") ; return False

        # g.trace(start,end)

        # Replace the selection in _both_ controls.
        start,end = oldSel
        change_text = self.change_text

        # Perform regex substitutions of \1, \2, ...\9 in the change text.
        if self.pattern_match and self.match_obj:
            groups = self.match_obj.groups()
            if groups:
                change_text = self.makeRegexSubs(change_text,groups)
        # change_text = change_text.replace('\\n','\n').replace('\\t','\t')
        change_text = self.replaceBackSlashes(change_text)

        for w2 in (w,self.s_ctrl):
            if start != end: w2.delete(start,end)
            w2.insert(start,change_text)
            w2.setInsertPoint(g.choose(self.reverse,start,start+len(change_text)))

        # Update the selection for the next match.
        w.setSelectionRange(start,start+len(change_text))
        c.widgetWantsFocus(w)

        # No redraws here: they would destroy the headline selection.
        if self.mark_changes:
            p.setMarked()
        if self.in_headline:
            c.frame.tree.onHeadChanged(p,'Change')
        else:
            c.frame.body.onBodyChanged('Change',oldSel=oldSel)

        c.frame.tree.drawIcon(p) # redraw only the icon.

        return True
    #@+node:ekr.20060526201951: *5* makeRegexSubs
    def makeRegexSubs(self,s,groups):

        '''Carefully substitute group[i-1] for \i strings in s.
        The group strings may contain \i strings: they are *not* substituted.'''

        digits = '123456789'
        result = [] ; n = len(s)
        i = j = 0 # s[i:j] is the text between \i markers.
        while j < n:
            k = s.find('\\',j)
            if k == -1 or k + 1 >= n:
                break
            j = k + 1 ; ch = s[j]
            if ch in digits:
                j += 1
                result.append(s[i:k]) # Append up to \i
                i = j
                gn = int(ch)-1
                if gn < len(groups):
                    result.append(groups[gn]) # Append groups[i-1]
                else:
                    result.append('\\%s' % ch) # Append raw '\i'
        result.append(s[i:])
        return ''.join(result)
    #@+node:ekr.20031218072017.3071: *4* find.changeThenFind
    def changeThenFind(self):
        if not self.checkArgs():
            return
        self.initInHeadline()
        if self.changeSelection():
            self.findNext(False) # don't reinitialize
    #@+node:ekr.20031218072017.3073: *4* find.findAll & helper
    def findAll(self):
        trace = False and not g.unitTesting
        c = self.c ; w = self.s_ctrl ; u = c.undoer
        undoType = ('Clone Find All Flattened'
            if self.clone_find_all_flattened else 'Clone Find All')
        if not self.checkArgs():
            return
        self.initInHeadline()
        if self.clone_find_all:
            self.p = None # Restore will select the root position.
        data = self.save()
        self.initBatchCommands()
        skip = {} # Nodes that should be skipped.
            # Keys are vnodes, values not important.
        count,found = 0,None
        if trace: g.trace(self.clone_find_all_flattened,self.p and self.p.h)
        while 1:
            pos, newpos = self.findNextMatch() # sets self.p.
            if not self.p: self.p = c.p.copy()
            if pos is None: break
            if self.clone_find_all and self.p.v in skip:
                continue
            count += 1
            s = w.getAllText()
            i,j = g.getLine(s,pos)
            line = s[i:j]
            if self.clone_find_all:
                if not skip:
                    undoData = u.beforeInsertNode(c.p)
                    found = self.createCloneFindAllNode()
                if self.clone_find_all_flattened:
                    skip[self.p.v] = True
                else:
                    # Don't look at the node or it's descendants.
                    for p2 in self.p.self_and_subtree():
                        skip[p2.v] = True
                # Create a clone of self.p under the find node.
                p2 = self.p.clone()
                p2.moveToLastChildOf(found)
            else:
                self.printLine(line,allFlag=True)
        if self.clone_find_all and skip:
            u.afterInsertNode(found,undoType,undoData,dirtyVnodeList=[])
            c.selectPosition(found)
            c.setChanged(True)
        self.restore(data)
        c.redraw()
        g.es("found",count,"matches")
    #@+node:ekr.20051113110735: *5* createCloneFindAllNode
    def createCloneFindAllNode(self):

        c = self.c
        oldRoot = c.rootPosition()
        found = oldRoot.insertAfter()
        found.moveToRoot(oldRoot)
        c.setHeadString(found,'Found: ' + self.find_text)
        return found
    #@+node:ekr.20031218072017.3074: *4* find.findNext
    def findNext(self,initFlag=True):

        if not self.checkArgs():
            return
        if initFlag:
            self.initInHeadline()
            data = self.save()
            self.initInteractiveCommands()
        else:
            data = self.save()
        pos, newpos = self.findNextMatch()
        if pos is None:
            if self.wrapping:
                g.es("end of wrapped search")
            else:
                g.es("not found","'%s'" % (self.find_text))
            self.restore(data)
        else:
            self.showSuccess(pos,newpos)
    #@+node:ekr.20031218072017.3075: *4* find.findNextMatch
    def findNextMatch(self):
        '''
        Resume the search where it left off.
        The caller must call set_first_incremental_search or
        set_first_batch_search.
        '''
        trace = False and not g.unitTesting
        c = self.c ; p = self.p
        if trace: g.trace('entry','p',p and p.h,
            'search_headline',self.search_headline,
            'search_body',self.search_body)
        if not self.search_headline and not self.search_body:
            if trace: g.trace('nothing to search')
            return None, None
        if len(self.find_text) == 0:
            if trace: g.trace('no find text')
            return None, None
        self.errors = 0
        attempts = 0
        self.backwardAttempts = 0
        # New in Leo 4.4.8: precompute the regexp for regexHelper.
        if self.pattern_match:
            try: # Precompile the regexp.
                flags = re.MULTILINE
                if self.ignore_case: flags |= re.IGNORECASE
                # New in Leo 4.5: escape the search text.
                b,s = '\\b',self.find_text
                if self.whole_word:
                    if not s.startswith(b): s = b + s
                    if not s.endswith(b): s = s + b
                # g.trace(self.whole_word,repr(s))
                self.re_obj = re.compile(s,flags)
                # self.re_obj = re.compile(re.escape(self.find_text),flags)
            except Exception:
                g.warning('invalid regular expression:',self.find_text)
                self.errors += 1 # Abort the search.
                return None,None
        while p:
            pos, newpos = self.search()
            if trace: g.trace('attempt','pos',pos,'p',p.h,'in_headline',self.in_headline)
            if pos is not None:
                if self.mark_finds:
                    p.setMarked()
                    c.frame.tree.drawIcon(p) # redraw only the icon.
                if trace: g.trace('success',pos,newpos)
                return pos, newpos
            elif self.errors:
                g.trace('find errors')
                return None,None # Abort the search.
            elif self.node_only:
                # Bug fix: 2009-5-31.
                # Attempt to switch from headline to body.
                if self.in_headline:
                    self.in_headline = False
                    self.initNextText()
                else: 
                    if trace: g.trace('fail: node only')
                    return None,None # We are only searching one node.
            else:
                if trace: g.trace('failed attempt',p)
                attempts += 1
                p = self.p = self.selectNextPosition()
        if trace: g.trace('attempts',attempts,'backwardAttempts',self.backwardAttempts)
        return None, None
    #@+node:ekr.20031218072017.3076: *4* find.resetWrap
    def resetWrap (self,event=None):

        self.wrapPosition = None
        self.onlyPosition = None
    #@+node:ekr.20031218072017.3077: *4* find.search & helpers
    def search (self):

        """Search s_ctrl for self.find_text under the control of the
        whole_word, ignore_case, and pattern_match ivars.

        Returns (pos, newpos) or (None,None)."""

        trace = False and not g.unitTesting
        c = self.c
        p = self.p or c.p.copy()
        w = self.s_ctrl
        index = w.getInsertPoint()
        s = w.getAllText()

        if trace: g.trace(index,repr(s[index:index+20]))
        stopindex = g.choose(self.reverse,0,len(s)) # 'end' doesn't work here.
        pos,newpos = self.searchHelper(s,index,stopindex,self.find_text,
            backwards=self.reverse,nocase=self.ignore_case,
            regexp=self.pattern_match,word=self.whole_word)

        if trace: g.trace('pos,newpos',pos,newpos)
        if pos == -1:
            if trace: g.trace('** pos is -1',pos,newpos)
            return None,None
        #@+<< fail if we are passed the wrap point >>
        #@+node:ekr.20060526140328: *5* << fail if we are passed the wrap point >>
        if self.wrapping and self.wrapPos is not None and self.wrapPosition and p == self.wrapPosition:

            if self.reverse and pos < self.wrapPos:
                if trace: g.trace("** reverse wrap done",pos,newpos)
                return None, None

            if not self.reverse and newpos > self.wrapPos:
                if trace: g.trace('** wrap done',pos,newpos)
                return None, None
        #@-<< fail if we are passed the wrap point >>
        insert = g.choose(self.reverse,min(pos,newpos),max(pos,newpos))
        w.setSelectionRange(pos,newpos,insert=insert)

        if trace: g.trace('** returns',pos,newpos)
        return pos,newpos
    #@+node:ekr.20060526081931: *5* searchHelper & allies
    def searchHelper (self,s,i,j,pattern,backwards,nocase,regexp,word,swapij=True):

        trace = self.trace

        if swapij and backwards: i,j = j,i

        if trace: g.trace('back,nocase,regexp,word,',
            backwards,nocase,regexp,word,i,j,repr(s[i:i+20]))

        if not s[i:j] or not pattern:
            if trace: g.trace('empty',i,j,'len(s)',len(s),'pattern',pattern)
            return -1,-1

        if regexp:
            pos,newpos = self.regexHelper(s,i,j,pattern,backwards,nocase)
        elif backwards:
            pos,newpos = self.backwardsHelper(s,i,j,pattern,nocase,word)
        else:
            pos,newpos = self.plainHelper(s,i,j,pattern,nocase,word)

        if trace: g.trace('returns',pos,newpos)
        return pos,newpos
    #@+node:ekr.20060526092203: *6* regexHelper
    def regexHelper (self,s,i,j,pattern,backwards,nocase):

        re_obj = self.re_obj # Use the pre-compiled object
        if not re_obj:
            g.trace('can not happen: no re_obj')
            return -1,-1

        if backwards: # Scan to the last match.  We must use search here.
            last_mo = None ; i = 0
            while i < len(s):
                mo = re_obj.search(s,i,j)
                if not mo: break
                i += 1 ; last_mo = mo
            mo = last_mo
        else:
            mo = re_obj.search(s,i,j)

        if 0:
            g.trace('i',i,'j',j,'s[i:j]',repr(s[i:j]),
                'mo.start',mo and mo.start(),'mo.end',mo and mo.end())

        while mo and 0 <= i < len(s):
            if mo.start() == mo.end():
                if backwards:
                    # Search backward using match instead of search.
                    i -= 1
                    while 0 <= i < len(s):
                        mo = re_obj.match(s,i,j)
                        if mo: break
                        i -= 1
                else:
                    i += 1 ; mo = re_obj.search(s,i,j)
            else:
                self.match_obj = mo
                return mo.start(),mo.end()
        self.match_obj = None
        return -1,-1
    #@+node:ekr.20060526140744: *6* backwardsHelper
    debugIndices = []

    #@+at
    # rfind(sub [,start [,end]])
    # 
    # Return the highest index in the string where substring sub is found, such that
    # sub is contained within s[start,end]. Optional arguments start and end are
    # interpreted as in slice notation. Return -1 on failure.
    #@@c

    def backwardsHelper (self,s,i,j,pattern,nocase,word):

        debug = False
        if nocase:
            s = s.lower()
            pattern = pattern.lower()
                # Bug fix: 10/5/06: At last the bug is found!
        pattern = self.replaceBackSlashes(pattern)
        n = len(pattern)
        if i < 0 or i > len(s) or j < 0 or j > len(s):
            g.trace('bad index: i = %s, j = %s' % (i,j))
            i = 0 ; j = len(s)
        if debug and (s and i == 0 and j == 0):
            g.trace('two zero indices')
        self.backwardAttempts += 1
        # short circuit the search: helps debugging.
        if s.find(pattern) == -1:
            if debug:
                self.debugCount += 1
                if self.debugCount < 50:
                    g.trace(i,j,'len(s)',len(s),self.p.h)
            return -1,-1
        if word:
            while 1:
                k = s.rfind(pattern,i,j)
                if debug: g.trace('**word** %3s %3s %5s -> %s %s' % (
                    i,j,g.choose(j==len(s),'(end)',''),k,self.p.h))
                if k == -1: return -1, -1
                if self.matchWord(s,k,pattern):
                    return k,k+n
                else:
                    j = max(0,k-1)
        else:
            k = s.rfind(pattern,i,j)
            if debug: g.trace('%3s %3s %5s -> %s %s' % (
                i,j,g.choose(j==len(s),'(end)',''),k,self.p.h))
            if k == -1:
                return -1, -1
            else:
                return k,k+n
    #@+node:ekr.20060526093531: *6* plainHelper
    def plainHelper (self,s,i,j,pattern,nocase,word):

        trace = self.trace

        # if trace: g.trace(i,j,repr(s[i:i+20]),'pattern',repr(pattern),'word',repr(word))
        if trace: g.trace(i,j,repr(s[i:i+20]))

        if nocase:
            s = s.lower() ; pattern = pattern.lower()
        pattern = self.replaceBackSlashes(pattern)
        n = len(pattern)
        if word:
            while 1:
                k = s.find(pattern,i,j)
                # g.trace(k,n)
                if k == -1:
                    if trace: g.trace('no match word',i)
                    return -1, -1
                elif self.matchWord(s,k,pattern):
                    if trace: g.trace('match word',k)
                    return k, k + n
                else: i = k + n
        else:
            k = s.find(pattern,i,j)
            if k == -1:
                if trace: g.trace('no match word',i)
                return -1, -1
            else:
                if trace: g.trace('match', k)
                return k, k + n
    #@+node:ekr.20060526140744.1: *6* matchWord
    def matchWord(self,s,i,pattern):

        trace = self.trace

        pattern = self.replaceBackSlashes(pattern)
        if not s or not pattern or not g.match(s,i,pattern):
            if trace: g.trace('empty')
            return False

        pat1,pat2 = pattern[0],pattern[-1]
        # n = self.patternLen(pattern)
        n = len(pattern)
        ch1 = 0 <= i-1 < len(s) and s[i-1] or '.'
        ch2 = 0 <= i+n < len(s) and s[i+n] or '.'

        isWordPat1 = g.isWordChar(pat1)
        isWordPat2 = g.isWordChar(pat2)
        isWordCh1 = g.isWordChar(ch1)
        isWordCh2 = g.isWordChar(ch2)

        # g.trace('i',i,'ch1,ch2,pat',repr(ch1),repr(ch2),repr(pattern))

        inWord = isWordPat1 and isWordCh1 or isWordPat2 and isWordCh2
        if trace: g.trace('returns',not inWord)
        return not inWord

    #@+node:ekr.20070105165924: *6* replaceBackSlashes
    def replaceBackSlashes (self,s):

        '''Carefully replace backslashes in a search pattern.'''

        # This is NOT the same as s.replace('\\n','\n').replace('\\t','\t').replace('\\\\','\\')
        # because there is no rescanning.

        i = 0
        while i + 1 < len(s):
            if s[i] == '\\':
                ch = s[i+1]
                if ch == '\\':
                    s = s[:i] + s[i+1:] # replace \\ by \
                elif ch == 'n':
                    s = s[:i] + '\n' + s[i+2:] # replace the \n by a newline
                elif ch == 't':
                    s = s[:i] + '\t' + s[i+2:] # replace \t by a tab
                else:
                    i += 1 # Skip the escaped character.
            i += 1

        if self.trace: g.trace(repr(s))
        return s
    #@+node:ekr.20031218072017.3081: *4* find.selectNextPosition
    # Selects the next node to be searched.

    def selectNextPosition(self):

        trace = False and not g.unitTesting
        c = self.c
        p = self.p or c.p.copy()
        # Start suboutline only searches.
        if self.suboutline_only and not self.onlyPosition:
            # p.copy not needed because the find code never calls p.moveToX.
            # Furthermore, p might be None, so p.copy() would be wrong!
            self.onlyPosition = p 
        # Start wrapped searches.
        if self.wrapping and not self.wrapPosition:
            assert(self.wrapPos != None)
            # p.copy not needed because the find code never calls p.moveToX.
            # Furthermore, p might be None, so p.copy() would be wrong!
            self.wrapPosition = p 
        if self.in_headline and self.search_body:
            # just switch to body pane.
            self.in_headline = False
            self.initNextText()
            if trace: g.trace('switching to body',g.callers(5))
            return p
        if self.reverse: p = p.threadBack()
        else:            p = p.threadNext()
        # if trace: g.trace(p and p.h or 'None')
        # New in 4.3: restrict searches to hoisted area.
        # End searches outside hoisted area.
        if c.hoistStack:
            if not p:
                if self.wrapping:
                    g.warning('wrap disabled in hoisted outlines')
                return
            bunch = c.hoistStack[-1]
            if not bunch.p.isAncestorOf(p):
                g.warning('found match outside of hoisted outline')
                return None
        # Wrap if needed.
        if not p and self.wrapping and not self.suboutline_only:
            p = c.rootPosition()
            if self.reverse:
                # Set search_v to the last node of the tree.
                while p and p.next():
                    p = p.next()
                if p: p = p.lastNode()
        # End wrapped searches.
        if self.wrapping and p and p == self.wrapPosition:
            if trace: g.trace("ending wrapped search")
            p = None ; self.resetWrap()
        # End suboutline only searches.
        if (self.suboutline_only and self.onlyPosition and p and
            (p == self.onlyPosition or not self.onlyPosition.isAncestorOf(p))):
            # g.trace("end outline-only")
            p = None ; self.onlyPosition = None
        # p.copy not needed because the find code never calls p.moveToX.
        # Furthermore, p might be None, so p.copy() would be wrong!
        self.p = p # used in initNextText().
        if p: # select p and set the search point within p.
            self.in_headline = self.search_headline
            self.initNextText()
        return p
    #@+node:ekr.20131117164142.17006: *4* find.setupArgs
    def setupArgs (self,forward=False,regexp=False,word=False):
        
        if forward is not None: self.reverse = not forward
        if regexp  is not None: self.patern_match = True
        if word    is not None: self.whole_word = True
        self.showFindOptions()
    #@+node:ekr.20031218072017.3082: *3* leoFind.Initing & finalizing
    #@+node:ekr.20031218072017.3083: *4* find.checkArgs
    def checkArgs (self):

        val = True
        if not self.search_headline and not self.search_body:
            g.es("not searching headline or body")
            val = False
        s = self.c.findCommands.findTabManager.getFindText()
        if len(s) == 0:
            g.es("empty find patttern")
            val = False
        return val
    #@+node:EKR.20040503070514: *4* find.handleUserClick
    def handleUserClick (self,p):

        """Reset suboutline-only search when the user clicks a headline."""

        try:
            if self.c and self.suboutline_only:
                # g.trace(p)
                self.onlyPosition = p.copy()
        except: pass
    #@+node:ekr.20031218072017.3084: *4* find.initBatchCommands
    # Initializes for the Find All and Replace All commands.

    def initBatchCommands (self):

        c = self.c
        self.in_headline = self.search_headline # Search headlines first.
        self.errors = 0

        # Select the first node.
        if self.suboutline_only or self.node_only:
            self.p = c.p.copy()
        else:
            p = c.rootPosition()
            if self.reverse:
                while p and p.next():
                    p = p.next()
                p = p.lastNode()
            self.p = p
            assert self.p

        # Set the insert point.
        self.initBatchText()
    #@+node:ekr.20031218072017.3085: *4* find.initBatchText, initNextText & init_s_ctrl
    # Returns s_ctrl with "insert" point set properly for batch searches.
    def initBatchText(self,ins=None):
        c = self.c
        p = self.p or c.p.copy()
        self.wrapping = False # Only interactive commands allow wrapping.
        s = g.choose(self.in_headline,p.h, p.b)
        self.init_s_ctrl(s,ins)

    # Call this routine when moving to the next node when a search fails.
    # Same as above except we don't reset wrapping flag.
    def initNextText(self,ins=None):
        c = self.c
        p = self.p or c.p.copy()
        s = p.h if self.in_headline else p.b
        if True:
            tree = c.frame and c.frame.tree
            if tree and hasattr(tree,'killEditing'):
                # g.trace('kill editing before find')
                tree.killEditing()
        self.init_s_ctrl(s,ins)

    def init_s_ctrl (self,s,ins):
        w = self.s_ctrl
        w.setAllText(s)
        if ins is None:
            ins = len(s) if self.reverse else 0
        else:
            pass # g.trace('ins',ins)
        w.setInsertPoint(ins)
    #@+node:ekr.20031218072017.3086: *4* find.initInHeadline
    # Guesses which pane to start in for incremental searches and changes.
    # This must not alter the current "insert" or "sel" marks.

    def initInHeadline (self):

        trace = False
        c = self.c
        p = self.p or c.p.copy()
        # Do not change this without careful thought and extensive testing!
        if self.search_headline and self.search_body:
            # A temporary expedient.
            if self.reverse:
                self.in_headline = False
            else:
                editPosition = c.frame.tree.editPosition()
                focus = c.get_focus()
                # Search headline first.
                self.in_headline = (
                    p == editPosition and
                    focus != c.frame.body.bodyCtrl)
                if trace: g.trace(
                    '** p: %s, editPosition: %s, focus: %s, bodyCtrl: %s' % (
                    p and p.h,editPosition,focus, c.frame.body.bodyCtrl))
        else:
            self.in_headline = self.search_headline
    #@+node:ekr.20031218072017.3087: *4* find.initInteractiveCommands
    def initInteractiveCommands(self):

        c = self.c
        p = self.p or c.p.copy()
        bodyCtrl = c.frame.body and c.frame.body.bodyCtrl
        w = g.choose(self.in_headline,c.edit_widget(p),bodyCtrl)
        if not w:
            self.in_headline = False
            w = bodyCtrl
        if not w: return
        self.errors = 0
        # We only use the insert point, *never* the selection range.
        ins = w.getInsertPoint()
        # g.trace('ins',ins)
        self.debugCount = 0
        self.initNextText(ins=ins)
        c.widgetWantsFocus(w)
        self.wrapping = self.wrap
        if self.wrap and self.wrapPosition == None:
            self.wrapPos = ins
            # Do not set self.wrapPosition here: that must be done after the first search.
    #@+node:ekr.20031218072017.3088: *4* find.printLine
    def printLine (self,line,allFlag=False):

        both = self.search_body and self.search_headline
        context = self.batch # "batch" now indicates context
        if allFlag and both and context:
            g.es('','-' * 20,'',self.p.h)
            theType = g.choose(self.in_headline,"head: ","body: ")
            g.es('',theType + line)
        elif allFlag and context and not self.p.isVisited():
            # We only need to print the context once.
            g.es('','-' * 20,'',self.p.h)
            g.es('',line)
            self.p.setVisited()
        else:
            g.es('',line)
    #@+node:ekr.20031218072017.3089: *4* find.restore
    # Restores the screen after a search fails

    def restore (self,data):

        c = self.c
        in_headline,p,t,insert,start,end = data

        c.frame.bringToFront() # Needed on the Mac

        # Don't try to reedit headline.
        if p:
            c.selectPosition(p)
        else:
            c.selectPosition(c.rootPosition()) # New in Leo 4.5.

        if not in_headline:
            # Looks good and provides clear indication of failure or termination.
            t.setSelectionRange(insert,insert)
            t.setInsertPoint(insert)
            t.seeInsertPoint()

        if 1: # I prefer always putting the focus in the body.
            c.invalidateFocus()
            c.bodyWantsFocus()
            c.k.showStateAndMode(c.frame.body.bodyCtrl)
        else:
            c.widgetWantsFocus(t)
    #@+node:ekr.20031218072017.3090: *4* find.save
    def save (self):

        c = self.c
        p = self.p or c.p.copy()
        w = c.edit_widget(p) if self.in_headline else c.frame.body.bodyCtrl
        if w:
            insert = w.getInsertPoint()
            sel = w.getSelectionRange()
            if len(sel) == 2:
                start,end = sel
            else:
                start,end = None,None
        else:
            insert,start,end = None,None,None
        return (self.in_headline,p,w,insert,start,end)
    #@+node:ekr.20031218072017.3091: *4* find.showSuccess
    def showSuccess(self,pos,newpos,showState=True):
        '''Display the result of a successful find operation.'''
        trace = False and not g.unitTesting
        c = self.c
        p = self.p or c.p.copy()
        # Set state vars.
        # Ensure progress in backwards searches.
        insert = g.choose(self.reverse,min(pos,newpos),max(pos,newpos))
        if self.wrap and not self.wrapPosition:
            self.wrapPosition = self.p
        if trace: g.trace('in_headline',self.in_headline)
        if self.in_headline:
            c.endEditing()
            selection = pos,newpos,insert
            c.redrawAndEdit(p,
                selection=selection,
                keepMinibuffer=True)
            w = c.edit_widget(p)
        else:
            w = c.frame.body.bodyCtrl
            # Bug fix: 2012/11/26: *Always* do the full selection logic.
            # This ensures that the body text is inited  and recolored.
            c.selectPosition(p)
            c.bodyWantsFocus()
            if showState:
                c.k.showStateAndMode(w)
            c.bodyWantsFocusNow()
            assert w.getAllText() == p.b.replace('\r','')
            w.setSelectionRange(pos,newpos,insert=insert)
            c.outerUpdate()
        return w # Support for isearch.
    #@+node:ekr.20031218072017.1460: *4* find.update_ivars
    def update_ivars (self):
        """Update ivars from the find panel."""
        trace = False and not g.unitTesting
        c = self.c
        self.p = c.p.copy()
        ftm = self.findTabManager    
        # The caller is responsible for removing most trailing cruft.
        # Among other things, this allows Leo to search for a single trailing space.
        s = ftm.getFindText()
        s = g.toUnicode(s)
        if trace: g.trace('find',repr(s),self.find_ctrl)
        if s and s[-1] in ('\r','\n'):
            s = s[:-1]
        # clear wrap_pos if the find_text changes.
        if s != self.find_text:
            # g.trace('clearing self.wrap_pos')
            self.wrapPosition = None
        self.find_text = s
        # Get replacement text.
        s = ftm.getReplaceText()
        s = g.toUnicode(s)
        if s and s[-1] in ('\r','\n'):
            s = s[:-1]
        self.change_text = s
        if trace: g.trace('change',repr(s))
    #@-others
#@-others
#@-leo
