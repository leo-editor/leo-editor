#@+leo-ver=5-thin
#@+node:ekr.20060123151617: * @file leoFind.py
'''Leo's gui-independent find classes.'''

import leo.core.leoGlobals as g
import re
import sys

#@+<< Theory of operation of find/change >>
#@+node:ekr.20031218072017.2414: ** << Theory of operation of find/change >>
#@@nocolor-node
#@+at
# 
# LeoFind.py contains the gui-independant part of all of Leo's
# find/change code. Such code is tricky, which is why it should be
# gui-independent code! Here are the governing principles:
# 
# 1. Find and Change commands initialize themselves using only the state
#    of the present Leo window. In particular, the Find class must not
#    save internal state information from one invocation to the next.
#    This means that when the user changes the nodes, or selects new
#    text in headline or body text, those changes will affect the next
#    invocation of any Find or Change command. Failure to follow this
#    principle caused all kinds of problems earlier versions.
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
# The searching code does not know whether it is searching headline or
# body text. The search code knows only that self.s_text is a text
# widget that contains the text to be searched or changed and the insert
# and sel attributes of self.search_text indicate the range of text to
# be searched.
# 
# Searching headline and body text simultaneously is complicated. The
# findNextMatch() method and its helpers handle the many details
# involved by setting self.s_text and its insert and sel attributes.
#@-<< Theory of operation of find/change >>
#@+others
#@+node:ekr.20070105092022.1: ** class SearchWidget
class SearchWidget:
    '''A class to simulating high-level interface widget.'''
    # This could be a StringTextWrapper, but this code is simple and good.
    def __init__ (self,*args,**keys):
        # g.trace ('SearchWidget',g.callers())
        self.s = ''    # The widget text
        self.i = 0     # The insert point
        self.sel = 0,0 # The selection range
    def __repr__(self):
        return 'SearchWidget id: %s' % (id(self))

    #@+others
    #@+node:ekr.20070105093138: *3* getters (LeoFind)
    def getAllText (self):          return self.s
    def getInsertPoint (self):      return self.i       # Returns Python index.
    def getSelectionRange(self):    return self.sel     # Returns Python indices.
    #@+node:ekr.20070105102419: *3* setters (LeoFind)
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

    def setInsertPoint (self,i,s=None):
        self.i = i

    def setSelectionRange (self,i,j,insert=None):
        self.sel = self.toPythonIndex(i),self.toPythonIndex(j)
        if insert is not None:
            self.i = self.toPythonIndex(insert)
    #@+node:ekr.20070105092022.4: *3* toPythonIndex (LeoFind)
    def toPythonIndex (self,i):

        return g.toPythonIndex(self.s,i)
    #@-others
#@+node:ekr.20061212084717: ** class LeoFind (LeoFind.py)
class LeoFind:

    """The base class for Leo's Find commands."""

    #@+others
    #@+node:ekr.20131117164142.17021: *3* LeoFind.birth
    #@+node:ekr.20031218072017.3053: *4* find.__init__ & helpers
    def __init__ (self,c):
        # g.trace('(LeoFind)',c.shortFileName(),id(self),g.callers())
        self.c = c
        self.errors = 0
        self.expert_mode = False # set in finishCreate.
        self.ftm = None
            # Created by dw.createFindTab.
        self.frame = None
        self.k = k = c.k
        self.re_obj = None
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
        self.s_ctrl = SearchWidget() # For searches.
        self.find_text = ""
        self.change_text = ""
        self.radioButtonsChanged = False # Set by ftm.radio_button_callback
        # Ivars containing internal state...
        self.buttonFlag = False
        self.changeAllFlag = False
        self.findAllFlag = False
        self.in_headline = False # True: searching headline text.
        self.p = None # The position being searched.  Never saved between searches!
        self.was_in_headline = None
            # Fix bug: https://groups.google.com/d/msg/leo-editor/RAzVPihqmkI/-tgTQw0-LtwJ
        # For suboutline-only
        self.onlyPosition = None # The starting node for suboutline-only searches.
        # For wrapped searches.
        self.wrapping = False # True: wrapping is enabled.
            # This must be different from self.wrap, which is set by the checkbox.
        self.wrapPosition = None # The start of wrapped searches: persists between calls.
        self.wrapPos = None # The starting position of the wrapped search: persists between calls.
    #@+node:ekr.20131117164142.17022: *4* LeoFind.finishCreate
    def finishCreate(self):
        
        # New in 4.11.1.
        # Must be called when config settings are valid.
        c = self.c
        self.minibuffer_mode = c.config.getBool('minibuffer-find-mode',default=False)
        # now that configuration settings are valid,
        # we can finish creating the Find pane.
        dw = c.frame.top
        if dw: dw.finishCreateLogPane()
    #@+node:ekr.20060123065756.1: *3* LeoFind.Buttons (immediate execution)
    #@+node:ekr.20031218072017.3057: *4* find.changeAllButton
    def changeAllButton(self,event=None):
        '''Handle Replace All button.'''
        c = self.c
        self.setup_button()
        c.clearAllVisited() # For context reporting.
        self.changeAll()
    #@+node:ekr.20031218072017.3056: *4* find.changeButton
    def changeButton(self,event=None):
        '''Handle Change button.'''
        self.setup_button()
        self.change()
    #@+node:ekr.20031218072017.3058: *4* find.changeThenFindButton
    def changeThenFindButton(self,event=None):
        '''Handle Change, Then Find button.'''
        self.setup_button()
        self.changeThenFind()
    #@+node:ekr.20031218072017.3060: *4* find.findAllButton
    def findAllButton(self,event=None):
        '''Handle Find All button.'''
        self.setup_button()
        self.findAll()
    #@+node:ekr.20031218072017.3059: *4* find.findButton
    def findButton(self,event=None):
        '''Handle pressing the "Find" button in the find panel.'''
        self.setup_button()
        self.findNext()
    #@+node:ekr.20131117054619.16688: *4* find.findPreviousButton
    def findPreviousButton(self,event=None):
        '''Handle the Find Previous button.'''
        self.setup_button()
        self.reverse = not self.reverse
        try:
            self.findNext()
        finally:
            self.reverse = not self.reverse
    #@+node:ekr.20031218072017.3065: *4* find.setup_button
    def setup_button(self):
        '''Init a search started by a button in the Find panel.'''
        c = self.c
        self.buttonFlag = True
        self.p = c.p.copy()
        c.bringToFront()
        if 0: # We _must_ retain the editing status for incremental searches!
            c.endEditing()
        self.update_ivars()
    #@+node:ekr.20031218072017.3055: *3* LeoFind.Commands (immediate execution)
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
    #@+node:ekr.20131122231705.16463: *4* find.cloneFindAllCommand
    def cloneFindAllCommand(self,event=None):
     
        self.setup_command()
        self.findAll(clone_find_all=True)
    #@+node:ekr.20131122231705.16464: *4* find.cloneFindAllFlattenedCommand
    def cloneFindAllFlattenedCommand(self,event=None):
        
        self.setup_command()
        self.findAll(clone_find_all=True,clone_find_all_flattened=True)
    #@+node:ekr.20131122231705.16465: *4* find.findAllCommand
    def findAllCommand(self,event=None):
        
        self.setup_command()
        self.findAll()
    #@+node:ekr.20031218072017.3063: *4* find.findNextCommand
    def findNextCommand(self,event=None):
        '''The find-next command.'''
        self.setup_command()
        self.findNext()
    #@+node:ekr.20031218072017.3064: *4* find.findPrevCommand
    def findPrevCommand(self,event=None):
        '''Handle F2 (find-previous)'''
        self.setup_command()
        self.reverse = not self.reverse
        try:
            self.findNext()
        finally:
            self.reverse = not self.reverse
    #@+node:ekr.20141113094129.6: *4* find.focusToFind
    def focusToFind(self,event=None):
        self.c.frame.log.selectTab('Find')
    #@+node:ekr.20131119204029.16479: *4* find.helpForFindCommands
    def helpForFindCommands(self,event=None):
        '''Called from Find panel.  Redirect.'''
        self.c.helpCommands.helpForFindCommands(event)
    #@+node:ekr.20131117164142.17015: *4* find.hideFindTab
    def hideFindTab (self,event=None):
        '''Hide the Find tab.'''
        c = self.c
        if self.minibuffer_mode:
            c.k.keyboardQuit()
        else:
            self.c.frame.log.selectTab('Log')
    #@+node:ekr.20131117164142.16916: *4* find.openFindTab
    def openFindTab (self,event=None,show=True):
        '''Open the Find tab in the log pane.'''
        self.c.frame.log.selectTab('Find')
    #@+node:ekr.20131117164142.17016: *4* find.changeAllCommand
    def changeAllCommand(self,event=None):
        
        self.setup_command()
        self.changeAll()
    #@+node:ekr.20031218072017.3066: *4* find.setup_command
    # Initializes a search when a command is invoked from the menu.

    def setup_command(self):

        if 0: # We _must_ retain the editing status for incremental searches!
            self.c.endEditing()
        # Fix bug
        self.buttonFlag = False
        self.update_ivars()
    #@+node:ekr.20131119060731.22452: *4* find.startSearch
    def startSearch(self,event):
        
        if self.minibuffer_mode:
            self.ftm.clear_focus()
            self.searchWithPresentOptions(event)
        else:
            self.openFindTab(event)
            self.ftm.init_focus()
    #@+node:ekr.20131117164142.16939: *3* LeoFind.ISearch
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
    #@+node:ekr.20131117164142.16946: *3* LeoFind.Isearch utils
    #@+node:ekr.20131117164142.16947: *4* find.abortSearch (incremental)
    def abortSearch (self):
        '''Restore the original position and selection.'''
        c = self.c ; k = self.k
        w = c.frame.body.wrapper
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
    def iSearchStateHandler (self,event):
        '''The state manager when the state is 'isearch'''
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
        # Fix bug 1267921: isearch-forward accepts non-alphanumeric keys as input.
        elif k.isPlainKey(stroke):
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
            w = c.frame.body.wrapper
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
        wrapper = c.frame.body.wrapper
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
                self.in_headline = False ; w = wrapper
        else:
            w = wrapper
        if w == wrapper:
            c.bodyWantsFocus()
        return w
    #@+node:ekr.20131117164142.16955: *4* find.startIncremental
    def startIncremental (self,event,commandName,forward,ignoreCase,regexp):

        c,k = self.c,self.k
        # None is a signal to get the option from the find tab.
        self.event = event
        self.isearch_forward = not self.reverse if forward is None else forward
        self.isearch_ignore_case = self.ignore_case if ignoreCase is None else ignoreCase
        self.isearch_regexp = self.pattern_match if regexp is None else regexp
        # Note: the word option can't be used with isearches!
        self.w = w = c.frame.body.wrapper
        self.p1 = c.p.copy()
        self.sel1 = w.getSelectionRange(sort=False)
        i,j = self.sel1
        self.push(c.p,i,j,self.in_headline)
        self.inverseBindingDict = k.computeInverseBindingDict()
        self.iSearchStrokes = self.getStrokes(commandName)
        k.setLabelBlue('Isearch%s%s%s: ' % (
            '' if self.isearch_forward else ' Backward',
            ' Regexp' if self.isearch_regexp else '',
            ' NoCase' if self.isearch_ignore_case else '',
        ))
        k.setState('isearch',1,handler=self.iSearchStateHandler)
        c.minibufferWantsFocus()
    #@+node:ekr.20131117164142.17013: *3* LeoFind.Minibuffer commands
    #@+node:ekr.20131117164142.17011: *4* find.minibufferCloneFindAll
    def minibufferCloneFindAll (self,event=None):
        c = self.c ; k = self.k ; tag = 'clone-find-all'
        state = k.getState(tag)
        if state == 0:
            w = self.editWidget(event) # sets self.w
            if not w: return
            # self.setupArgs(forward=None,regexp=None,word=None)
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
            # self.setupArgs(forward=None,regexp=None,word=None)
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
        '''handle the find-all command.'''
        self.ftm.clear_focus()
        self.searchWithPresentOptions(event,findAllFlag=True)
        
    #@+node:ekr.20131117164142.16994: *4* find.minibufferReplaceAll
    def minibufferReplaceAll (self,event=None):
        '''Handle the change-all command.'''
        self.ftm.clear_focus()
        self.searchWithPresentOptions(event,changeAllFlag=True)
        
    #@+node:ekr.20131117164142.16983: *3* LeoFind.Minibuffer utils
    #@+node:ekr.20131117164142.16992: *4* find.addChangeStringToLabel
    def addChangeStringToLabel (self):
        '''Add an unprotected change string to the minibuffer label.'''
        c = self.c
        ftm = c.findCommands.ftm
        s = ftm.getChangeText()
        c.frame.log.selectTab('Find')
        c.minibufferWantsFocus()
        while s.endswith('\n') or s.endswith('\r'):
            s = s[:-1]
        c.k.extendLabel(s,select=True,protect=False)
    #@+node:ekr.20131117164142.16993: *4* find.addFindStringToLabel
    def addFindStringToLabel (self,protect=True):

        c = self.c ; k = c.k
        ftm = c.findCommands.ftm
        s = ftm.getFindText()
        c.frame.log.selectTab('Find')
        c.minibufferWantsFocus()
        while s.endswith('\n') or s.endswith('\r'):
            s = s[:-1]
        k.extendLabel(s,select=True,protect=protect)
    #@+node:ekr.20131117164142.16985: *4* find.editWidget
    def editWidget (self,event,forceFocus=True):
        '''
        An override of baseEditCommands.editWidget that does *not* set
        focus when using anything other than the tk gui.

        This prevents this class from caching an edit widget that is about
        to be deallocated.
        '''
        c = self.c
        # Do not cache a pointer to a headline!
        # It will die when the minibuffer is selected.
        self.w = c.frame.body.wrapper
        return self.w
    #@+node:ekr.20131117164142.16999: *4* find.generalChangeHelper
    def generalChangeHelper (self,find_pattern,change_pattern,changeAll=False):

        c = self.c
        self.setupSearchPattern(find_pattern)
        self.setupChangePattern(change_pattern)
        if c.vim_mode and c.vimCommands:
            c.vimCommands.update_dot_before_search(
                find_pattern=find_pattern,change_pattern=change_pattern)
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
        if c.vim_mode and c.vimCommands:
            c.vimCommands.update_dot_before_search(
                find_pattern=pattern,
                change_pattern=None) # A flag indicating not a change command.
        c.widgetWantsFocusNow(self.w)
        self.p = c.p.copy()
        if findAll:
            self.findAllCommand()
        elif cloneFindAll:
            self.cloneFindAllCommand()
        elif cloneFindAllFlattened:
            self.cloneFindAllFlattenedCommand()
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
                escapes=['\t']) # The Tab Easter Egg.
        elif k.getArgEscapeFlag:
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
                escapes=['\t']) # The Tab Easter Egg.
        elif k.getArgEscapeFlag:
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
                escapes=['\t']) # The Tab Easter Egg.
        elif k.getArgEscapeFlag:
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
                escapes=['\t']) # The Tab Easter Egg.
        elif k.getArgEscapeFlag:
            # Switch to the replace command.
            k.setState('replace-string',1,self.setReplaceString)
            self.setReplaceString(event=None)
        else:
            self.updateFindList(k.arg)
            self.lastStateHelper()
            self.generalSearchHelper(k.arg)
    #@+node:ekr.20131117164142.17002: *4* find.setReplaceString
    def setReplaceString (self,event):
        '''A state handler to get the replacement string.'''
        trace = False and not g.unitTesting
        k = self.k ; tag = 'replace-string' ; state = k.getState(tag)
        prompt = 'Replace ' + 'Regex' if self.pattern_match else 'String'
        if trace: g.trace(state)
        if state == 0:
            # self.setupArgs(forward=None,regexp=None,word=None)
            prefix = '%s: ' % prompt
            self.stateZeroHelper(event,tag,prefix,self.setReplaceString)
        elif state == 1:
            self._sString = k.arg
            self.updateFindList(k.arg)
            s = '%s: %s With: ' % (prompt,self._sString)
            k.setLabelBlue(s)
            self.addChangeStringToLabel()
            k.getArg(event,'replace-string',2,self.setReplaceString,completion=False)
        elif state == 2:
            self.updateChangeList(k.arg)
            self.lastStateHelper()
            self.generalChangeHelper(self._sString,k.arg,changeAll=self.changeAllFlag)
    #@+node:ekr.20131117164142.17005: *4* find.searchWithPresentOptions
    def searchWithPresentOptions (self,event,findAllFlag=False,changeAllFlag=False):
        '''Open the search pane and get the search string.'''
        trace = False and not g.unitTesting
        k = self.k ; tag = 'search-with-present-options'
        state = k.getState(tag)
        if trace: g.trace('state',state,k.getArgEscapeFlag)
        if state == 0:
            # Remember the entry focus, just as when using the find pane.
            self.changeAllFlag = changeAllFlag
            self.findAllFlag = findAllFlag
            self.ftm.set_entry_focus()
            # self.setupArgs(forward=None,regexp=None,word=None)
            self.stateZeroHelper(
                event,tag,'Search: ',self.searchWithPresentOptions,
                escapes=['\t']) # The Tab Easter Egg.
        elif k.getArgEscapeFlag:
            # Switch to the replace command.
            if self.findAllFlag: self.changeAllFlag = True
            self.setupSearchPattern(k.arg) # 2010/01/10: update the find text immediately.
            k.setState('replace-string',1,self.setReplaceString)
            if trace: g.trace(k.getState('replace-string'))
            self.setReplaceString(event=None)
        else:
            self.updateFindList(k.arg)
            k.clearState()
            k.resetLabel()
            k.showStateAndMode()
            if self.findAllFlag:
                self.setupSearchPattern(k.arg)
                self.findAllCommand()
            else:
                self.generalSearchHelper(k.arg)
    #@+node:ekr.20131117164142.17007: *4* find.stateZeroHelper
    def stateZeroHelper (self,event,tag,prefix,handler,escapes=None):

        k = self.k
        self.w = self.editWidget(event)
        if not self.w:
            g.trace('no self.w')
            return
        k.setLabelBlue(prefix)
        self.addFindStringToLabel(protect=False)
        # g.trace(escapes,g.callers())
        if escapes is None: escapes = []
        k.getArgEscapes = escapes
        k.getArgEscapeFlag = False # k.getArg may set this.
        k.getArg(event,tag,1,handler, # enter state 1
            tabList=self.findTextList,completion=True)
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
    #@+node:ekr.20131117164142.16915: *3* LeoFind.Option commands
    #@+node:ekr.20131117164142.16919: *4* LeoFind.toggle checkbox commands
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
        self.ftm.toggle_checkbox(checkbox_name)
    #@+node:ekr.20131117164142.17019: *4* LeoFind.setFindScope...
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
        self.ftm.set_radio_button(where)
    #@+node:ekr.20131117164142.16989: *4* LeoFind.showFindOptions
    def showFindOptions (self,event=None):
        '''
        Show the present find options in the status line.
        This is useful for commands like search-forward that do not show the Find Panel.
        '''
        frame = self.c.frame ; z = []
        # Set the scope field.
        head = self.search_headline
        body = self.search_body
        if self.suboutline_only:
            scope = 'tree'
        elif self.node_only:
            scope = 'node'
        else:
            scope = 'all'
        # scope = self.getOption('radio-search-scope')
        # d = {'entire-outline':'all','suboutline-only':'tree','node-only':'node'}
        # scope = d.get(scope) or ''
        head = 'head' if head else ''
        body = 'body' if body else ''
        sep = '+' if head and body else ''
        frame.clearStatusLine()
        s = '%s%s%s %s  ' % (head,sep,body,scope)
        frame.putStatusLine(s,color='blue')
        # Set the type field.
        regex  = self.pattern_match
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
            val = getattr(self,ivar)
            if val: z.append(s)
        frame.putStatusLine(' '.join(z))
    #@+node:ekr.20131117164142.16990: *4* LeoFind.setupChangePattern
    def setupChangePattern (self,pattern):

        self.ftm.setChangeText(pattern)
    #@+node:ekr.20131117164142.16991: *4* LeoFind.setupSearchPattern
    def setupSearchPattern (self,pattern):

        self.ftm.setFindText(pattern)
    #@+node:ekr.20031218072017.3067: *3* LeoFind.Utils
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
        p = self.p
        w = self.s_ctrl
        # Replace the selection with self.change_text
        if pos1 > pos2: pos1,pos2=pos2,pos1
        s = w.getAllText()
        if pos1 != pos2: w.delete(pos1,pos2)
        w.insert(pos1,self.change_text)
        # Update the selection.
        insert=pos1 if self.reverse else pos1+len(self.change_text)
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
        # Fix bug 338172: ReplaceAll will not replace newlines indicated as \n in target string.
        self.change_text = self.replaceBackSlashes(self.change_text)
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
        g.es("changed:",count,"instances of",self.find_text,"to",self.change_text)
        c.redraw(p)
        self.restore(saveData)
    #@+node:ekr.20031218072017.3070: *4* find.changeSelection
    # Replace selection with self.change_text.
    # If no selection, insert self.change_text at the cursor.

    def changeSelection(self):

        c = self.c ; p = self.p
        wrapper = c.frame.body and c.frame.body.wrapper
        w = c.edit_widget(p) if self.in_headline else wrapper
        if not w:
            self.in_headline = False
            w = wrapper
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
            w2.setInsertPoint(start if self.reverse else start+len(change_text))
        
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
        r'''
        Carefully substitute group[i-1] for \i strings in s.
        The group strings may contain \i strings: they are *not* substituted.
        '''
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
    def findAll(self,clone_find_all=False,clone_find_all_flattened=False):
        trace = False and not g.unitTesting
        c,w = self.c,self.s_ctrl
        if clone_find_all_flattened:
            undoType = 'Clone Find All Flattened'
        elif clone_find_all:
            undoType = 'Clone Find All'
        else:
            undoType = 'Find All'
        if not self.checkArgs():
            return
        self.initInHeadline()
        if clone_find_all or clone_find_all_flattened:
            self.p = None # Restore will select the root position.
        data = self.save()
        self.initBatchCommands()
        skip = set() # vnodes that should be skipped.
        count = 0
        if trace: g.trace(self.find_text)
        # 2014/04/24: Init suboutline-only for clone-find-all commands
        if clone_find_all or clone_find_all_flattened:
            self.p = c.p.copy()
            if self.suboutline_only:
                self.onlyPosition = self.p.copy()
        clones = set()
        while 1:
            pos, newpos = self.findNextMatch() # sets self.p.
            if not self.p: self.p = c.p.copy()
            if pos is None: break
            if clone_find_all and self.p.v in skip:
                continue
            count += 1
            s = w.getAllText()
            i,j = g.getLine(s,pos)
            line = s[i:j]
            if clone_find_all or clone_find_all_flattened:
                if clone_find_all_flattened:
                    skip.add(self.p.v)
                else:
                    # Don't look at the node or it's descendants.
                    for p2 in self.p.self_and_subtree():
                        skip.add(p2.v)
                clones.add(self.p.copy())
            else:
                self.printLine(line,allFlag=True)
        if clones and (clone_find_all or clone_find_all_flattened):
            u = c.undoer
            undoData = u.beforeInsertNode(c.p)
            found = self.createCloneFindAllNodes(clones,clone_find_all_flattened)
            u.afterInsertNode(found,undoType,undoData,dirtyVnodeList=[])
            c.selectPosition(found)
            c.setChanged(True)
        else:
            self.restore(data)
        c.redraw()
        g.es("found",count,"matches for",self.find_text)
    #@+node:ekr.20141023110422.1: *5* find.createCloneFindAllNodes
    def createCloneFindAllNodes(self,clones,flattened):
        '''
        Create a "Found" node as the last node of the outline.
        Clone all positions in the clones set a children of found.
        '''
        c = self.c
        # Create the found node.
        last = c.rootPosition()
        while last.hasNext():
            last.moveToNext()
        found = last.insertAfter()
        found.h = 'Found:%s %s' % (' (flattened)' if flattened else '',self.find_text)
        # Clone nodes as children of the found node.
        for p in clones:
            p2 = p.clone()
            p2.moveToLastChildOf(found)
        return found
    #@+node:ekr.20031218072017.3074: *4* find.findNext
    def findNext(self,initFlag=True):
        '''Find the next instance of the pattern.'''
        if not self.checkArgs():
            return False # for vim-mode find commands.
        # initFlag is False for change-then-find.
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
            return False # for vim-mode find commands.
        else:
            self.showSuccess(pos,newpos)
            return True # for vim-mode find commands.
    #@+node:ekr.20031218072017.3075: *4* find.findNextMatch & helpers
    def findNextMatch(self):
        '''
        Resume the search where it left off.
        The caller must call set_first_incremental_search or
        set_first_batch_search.
        '''
        trace = False and not g.unitTesting
        verbose = True
        c = self.c ; p = self.p
        if trace:
            g.trace('*** entry','p',p,'\n',
                'search_headline',self.search_headline,
                'search_body',self.search_body)
            for parent in p.parents():
                print(parent)
        if not self.search_headline and not self.search_body:
            if trace: g.trace('nothing to search')
            return None, None
        if len(self.find_text) == 0:
            if trace: g.trace('no find text')
            return None, None
        self.errors = 0
        attempts = 0
        if self.pattern_match:
            ok = self.precompilePattern()
            if not ok: return None,None
        while p:
            pos, newpos = self.search()
            if self.errors:
                g.trace('find errors')
                break # Abort the search.
            if trace and verbose:
                g.trace('pos: %s p: %s head: %s' % (pos,p.h,self.in_headline))
            if pos is not None:
                # Success.
                if self.mark_finds:
                    p.setMarked()
                    c.frame.tree.drawIcon(p) # redraw only the icon.
                if trace: g.trace('success',pos,newpos,p.h)
                return pos, newpos
            # Searching the pane failed: switch to another pane or node.
            if self.shouldStayInNode(p):
                # Switching panes is possible.  Do so.
                self.in_headline = not self.in_headline
                self.initNextText()
            else:
                # Switch to the next/prev node, if possible.
                attempts += 1
                p = self.p = self.nextNodeAfterFail(p)
                if p: # Found another node: select the proper pane.
                    self.in_headline = self.firstSearchPane()
                    self.initNextText()
        if trace: g.trace('failed after %s attempts' % attempts)
        return None, None
    #@+node:ekr.20131123071505.16468: *5* find.doWrap
    def doWrap(self):
        '''Return the position resulting from a wrap.'''
        c = self.c
        if self.reverse:
            p = c.rootPosition()
            while p and p.hasNext():
                p = p.next()
            p = p.lastNode()
            return p
        else:
            return c.rootPosition()
    #@+node:ekr.20131124060912.16473: *5* find.firstSearchPane
    def firstSearchPane(self):
        '''
        Set return the value of self.in_headline
        indicating which pane to search first.
        '''
        if self.search_headline and self.search_body:
            # Fix bug 1228458: Inconsistency between Find-forward and Find-backward.
            if self.reverse:
                return False # Search the body pane first.
            else:
                return True # Search the headline pane first.
        elif self.search_headline or self.search_body:
            # Search the only enabled pane.
            return self.search_headline
        else:
            g.trace('can not happen: no search enabled')
            return False # search the body.
    #@+node:ekr.20131123132043.16477: *5* find.initNextText
    def initNextText(self,ins=None):
        '''
        Init s_ctrl when a search fails. On entry:
        - self.in_headline indicates what text to use.
        - self.reverse indicates how to set the insertion point.
        '''
        trace = False and not g.unitTesting
        c = self.c
        p = self.p or c.p.copy()
        s = p.h if self.in_headline else p.b
        w = self.s_ctrl
        tree = c.frame and c.frame.tree
        if tree and hasattr(tree,'killEditing'):
            # g.trace('kill editing before find')
            tree.killEditing()
        if self.reverse:
            i,j = w.sel
            if ins is None:
                if i is not None and j is not None and i != j:
                    ins = min(i,j)
            # Fix bug https://groups.google.com/d/msg/leo-editor/RAzVPihqmkI/-tgTQw0-LtwJ
            # editLabelHelper now properly sets the insertion range.
                # elif ins in (i,j): ins = min(i,j)
        elif ins is None:
            ins = 0
        if trace and self.in_headline and ins is not None: g.trace(ins,p.h)
        self.init_s_ctrl(s,ins)
    #@+node:ekr.20131123132043.16476: *5* find.nextNodeAfterFail & helper (use p.moveTo...?)
    def nextNodeAfterFail(self,p):
        '''Return the next node after a failed search or None.'''
        trace = False and not g.unitTesting
        c = self.c
        # Wrapping is disabled by any limitation of screen or search.
        wrap = (self.wrapping and not self.node_only and 
            not self.suboutline_only and not c.hoistStack)
        if wrap and not self.wrapPosition:
            self.wrapPosition = p.copy()
            self.wrapPos = 0 if self.reverse else len(p.b)
        # Move to the next position.
        p = p.threadBack() if self.reverse else p.threadNext()
        # Check it.
        if p and self.outsideSearchRange(p):
            if trace: g.trace('outside search range',p and p.h)
            return None
        if not p and wrap:
            p = self.doWrap()
        if not p:
            if trace: g.trace('end of search')
            return None
        if wrap and p == self.wrapPosition:
            if trace: g.trace('end of wrapped search',p and p.h)
            return None
        else:
            if trace: g.trace('found',p and p.h)
            return p
    #@+node:ekr.20131123071505.16465: *6* find.outsideSearchRange
    def outsideSearchRange(self,p):
        '''
        Return True if the search is about to go outside its range, assuming
        both the headline and body text of the present node have been searched.
        '''
        trace = False and not g.unitTesting
        c = self.c
        if not p:
            if trace: g.trace('no p')
            return True
        if self.node_only:
            if trace: g.trace('Node only',p.h)
            return True
        if self.suboutline_only:
            if self.onlyPosition:
                if p != self.onlyPosition and not self.onlyPosition.isAncestorOf(p):
                    if trace: g.trace('outside suboutline-only',p.h,self.onlyPosition.h)
                    return True
            else:
                g.trace('Can not happen: onlyPosition!',p.h)
                return True
        if c.hoistStack:
            bunch = c.hoistStack[-1]
            if not bunch.p.isAncestorOf(p):
                g.trace('outside hoist',p.h)
                g.warning('found match outside of hoisted outline')
                return True
        return False # Within range.
    #@+node:ekr.20131123071505.16467: *5* find.precompilePattern
    def precompilePattern(self):
        '''Precompile the regexp pattern if necessary.'''
        trace = False and not g.unitTesting
        try: # Precompile the regexp.
            flags = re.MULTILINE
            if self.ignore_case: flags |= re.IGNORECASE
            # Escape the search text.
            b,s = '\\b',self.find_text
            if self.whole_word:
                if not s.startswith(b): s = b + s
                if not s.endswith(b): s = s + b
            if trace: g.trace(self.whole_word,repr(s))
            self.re_obj = re.compile(s,flags)
            return True
        except Exception:
            g.warning('invalid regular expression:',self.find_text)
            self.errors += 1 # Abort the search.
            return False
    #@+node:ekr.20131124060912.16472: *5* find.shouldStayInNode
    def shouldStayInNode (self,p):
        '''Return True if the find should simply switch panes.'''
        # Errors here cause the find command to fail badly.
        # Switch only if:
        #   a) searching both panes and,
        #   b) this is the first pane of the pair.
        # There is *no way* this can ever change.
        # So simple in retrospect, so difficult to see.
        return (
            self.search_headline and self.search_body and (
            (self.reverse and not self.in_headline) or
            (not self.reverse and self.in_headline)))
    #@+node:ekr.20031218072017.3076: *4* find.resetWrap
    def resetWrap (self,event=None):

        self.wrapPosition = None
        self.onlyPosition = None
    #@+node:ekr.20031218072017.3077: *4* find.search & helpers
    def search (self):
        """
        Search s_ctrl for self.find_text with present options.
        Returns (pos, newpos) or (None,None).
        """
        trace = False and not g.unitTesting
        c = self.c
        p = self.p or c.p.copy()
        w = self.s_ctrl
        index = w.getInsertPoint()
        s = w.getAllText()
        if sys.platform.lower().startswith('win'):
            s = s.replace('\r','')
                # Ignore '\r' characters, which may appear in @edit nodes.
                # Fixes this bug: https://groups.google.com/forum/#!topic/leo-editor/yR8eL5cZpi4
                # This hack would be dangerous on MacOs: it uses '\r' instead of '\n' (!)
        if s:
            if trace: g.trace('=====',index,repr(s[max(0,index-10):index+40]))
        else:
            if trace: g.trace('returning: no text',p.h)
            return None,None
        stopindex = 0 if self.reverse else len(s)
        pos,newpos = self.searchHelper(s,index,stopindex,self.find_text)
        if trace: g.trace('pos,newpos',pos,newpos)
        # Bug fix: 2013/11/23.
        if self.in_headline and not self.search_headline:
            if trace: g.trace('not searching headlines')
            return None,None
        if not self.in_headline and not self.search_body:
            if trace: g.trace('not searching bodies')
            return None,None
        if pos == -1:
            if trace: g.trace('Returning: pos is -1')
            return None,None
        if self.passedWrapPoint(p,pos,newpos):
            if trace:
                kind = 'reverse ' if self.reverse else ''
                g.trace("** %swrap done",kind,pos,newpos)
            self.wrapPosition = None # Reset.
            return None,None
        ins = min(pos,newpos) if self.reverse else max(pos,newpos)
        w.setSelectionRange(pos,newpos,insert=ins)
        if trace: g.trace('** returns',pos,newpos)
        return pos,newpos
    #@+node:ekr.20060526140328: *5* passedWrapPoint
    def passedWrapPoint(self,p,pos,newpos):
        '''Return True if the search has gone beyond the wrap point.'''
        return (
            self.wrapping and
            self.wrapPosition is not None and
            p == self.wrapPosition and
                (self.reverse and pos < self.wrapPos or
                not self.reverse and newpos > self.wrapPos)
        )
    #@+node:ekr.20060526081931: *5* searchHelper & allies
    def searchHelper (self,s,i,j,pattern):
        '''Dispatch the proper search method based on settings.'''
        trace = False and not g.unitTesting
        backwards=self.reverse
        nocase=self.ignore_case
        regexp=self.pattern_match
        word=self.whole_word
        if backwards: i,j = j,i
        if trace: g.trace('entry',i,j,repr(s[min(i,j):max(i,j)]))
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
        trace = False and not g.unitTesting
        re_obj = self.re_obj # Use the pre-compiled object
        if not re_obj:
            g.trace('can not happen: no re_obj')
            return -1,-1
        if backwards:
            # Scan to the last match using search here.
            last_mo = None ; i = 0
            while i < len(s):
                mo = re_obj.search(s,i,j)
                if not mo: break
                i += 1
                last_mo = mo
            mo = last_mo
        else:
            mo = re_obj.search(s,i,j)
        if trace: g.trace('backwards',backwards,'pattern',pattern,
            i,j,'s[i:j]',repr(s[i:j]),
            'mo.start/end',mo and mo.start(),mo and mo.end())
        while mo and 0 <= i <= len(s):
            # Bug fix: 2013/12/27: must be 0 <= i <= len(s)
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

        trace = False and not g.unitTesting
        if nocase:
            s = s.lower()
            pattern = pattern.lower()
                # Bug fix: 10/5/06: At last the bug is found!
        pattern = self.replaceBackSlashes(pattern)
        n = len(pattern)
        # 2014/09/18: Put the indices in range.  Indices can get out of range
        # because the search code strips '\r' characters when searching @edit nodes.
        i = max(0,i)
        j = min(len(s),j)
        # Old code:
            # if i < 0 or i > len(s) or j < 0 or j > len(s):
                # g.trace('bad index: i = %s, j = %s' % (i,j))
                # i = 0 ; j = len(s)
        if trace and (s and i == 0 and j == 0):
            g.trace('two zero indices')
        # short circuit the search: helps debugging.
        if s.find(pattern) == -1:
            return -1,-1
        if word:
            while 1:
                k = s.rfind(pattern,i,j)
                if trace: g.trace('**word** %3s %3s %5s -> %s %s' % (
                    i,j,'(end)' if j==len(s) else '',k,self.p.h))
                if k == -1: return -1, -1
                if self.matchWord(s,k,pattern):
                    return k,k+n
                else:
                    j = max(0,k-1)
        else:
            k = s.rfind(pattern,i,j)
            if trace: g.trace('%3s %3s %5s -> %s %s' % (
                i,j,'(end)' if j==len(s) else '',k,self.p.h))
            if k == -1:
                return -1, -1
            else:
                return k,k+n
    #@+node:ekr.20060526093531: *6* plainHelper
    def plainHelper (self,s,i,j,pattern,nocase,word):
        '''Do a plain search.'''
        trace = False and not g.unitTesting
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
        '''Do a whole-word search.'''
        trace = False and not g.unitTesting
        pattern = self.replaceBackSlashes(pattern)
        if not s or not pattern or not g.match(s,i,pattern):
            if trace: g.trace('empty')
            return False
        pat1,pat2 = pattern[0],pattern[-1]
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
        # This is NOT the same as:
        # s.replace('\\n','\n').replace('\\t','\t').replace('\\\\','\\')
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
        return s
    #@+node:ekr.20131117164142.17006: *4* find.setupArgs
    def setupArgs (self,forward=False,regexp=False,word=False):
        '''
        Set up args for commands that force various values for commands
        (re-/word-/search-backward/forward)
        that force one or more of these values to be a spefic value.
        '''
        if forward is not None: self.reverse = not forward
        if regexp  is not None: self.patern_match = True
        if word    is not None: self.whole_word = True
        self.showFindOptions()
    #@+node:ekr.20031218072017.3082: *3* LeoFind.Initing & finalizing
    #@+node:ekr.20031218072017.3083: *4* find.checkArgs
    def checkArgs (self):

        val = True
        if not self.search_headline and not self.search_body:
            g.es("not searching headline or body")
            val = False
        s = self.ftm.getFindText()
        if len(s) == 0:
            g.es("empty find patttern")
            val = False
        return val
    #@+node:ekr.20131124171815.16629: *4* find.init_s_ctrl
    def init_s_ctrl (self,s,ins):
        '''Init the contents of s_ctrl from s and ins.'''
        w = self.s_ctrl
        w.setAllText(s)
        if ins is None: # A flag telling us to search all of w.
            ins = len(s) if self.reverse else 0
        w.setInsertPoint(ins)
    #@+node:ekr.20031218072017.3084: *4* find.initBatchCommands (sets in_headline)
    def initBatchCommands (self):
        '''Init for find-all and replace-all commands.'''
        c = self.c
        self.errors = 0
        self.in_headline = self.search_headline # Search headlines first.
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
        # Set the insert point.
        self.initBatchText()
    #@+node:ekr.20031218072017.3085: *4* find.initBatchText
    def initBatchText(self,ins=None):
        '''Init s_ctrl from self.p and ins at the beginning of a search.'''
        c = self.c
        self.wrapping = False
            # Only interactive commands allow wrapping.
        p = self.p or c.p.copy()
        s = p.h if self.in_headline else p.b
        self.init_s_ctrl(s,ins)
    #@+node:ekr.20031218072017.3086: *4* find.initInHeadline & helper
    def initInHeadline (self):
        '''
        Select the first pane to search for incremental searches and changes.
        This is called only at the start of each search.
        This must not alter the current insertion point or selection range.
        '''
        c = self.c
        p = self.p or c.p.copy()
        # Fix bug 1228458: Inconsistency between Find-forward and Find-backward.
        if self.search_headline and self.search_body:
            # We have no choice: we *must* search the present widget!
            self.in_headline = self.focusInTree()
        else:
            self.in_headline = self.search_headline
        # g.trace(self.in_headline,p and p.h)
    #@+node:ekr.20131126085250.16651: *5* find.focusInTree
    def focusInTree(self):
        '''Return True is the focus widget w is anywhere in the tree pane.
        
        Note: the focus may be in the find pane.
        '''
        c = self.c
        ftm = self.ftm
        w = ftm.entry_focus or g.app.gui.get_focus(raw=True)
        ftm.entry_focus = None # Only use this focus widget once!
        w_name = w and g.app.gui.widget_name(w) or ''
        if self.buttonFlag and self.was_in_headline in (True,False):
            # Fix bug: https://groups.google.com/d/msg/leo-editor/RAzVPihqmkI/-tgTQw0-LtwJ
            self.in_headline = self.was_in_headline
            val = self.was_in_headline
        # Easy case: focus in body.
        elif w == c.frame.body.wrapper:
            val = False
        elif w == c.frame.tree.treeWidget:
            val = True
        else:
            val = w_name.startswith('head')
        # g.trace(self.was_in_headline,val,c.p.h)
        return val
    #@+node:ekr.20031218072017.3087: *4* find.initInteractiveCommands
    def initInteractiveCommands(self):
        '''
        Init an interactive command.  This is tricky!
        
        *Always* start in the presently selected widget, provided that
        searching is enabled for that widget. Always start at the present
        insert point for the body pane. For headlines, start at beginning or
        end of the headline text.
        '''
        trace = False and not g.unitTesting
        c = self.c
        p = self.p = c.p # *Always* start with the present node.
        wrapper = c.frame.body and c.frame.body.wrapper
        headCtrl = c.edit_widget(p)
        # w is the real widget.  It may not exist for headlines.
        w = headCtrl if self.in_headline else wrapper
        # We only use the insert point, *never* the selection range.
        # None is a signal to self.initNextText()
        ins = w.getInsertPoint() if w else None
        # g.trace('inHead',self.in_headline,ins,w)
        self.errors = 0
        self.initNextText(ins=ins)
        if w: c.widgetWantsFocus(w)
        # Init suboutline-only:
        if self.suboutline_only and not self.onlyPosition:
            self.onlyPosition = p.copy()
        # Wrap does not apply to limited searches.
        if (self.wrap and
            not self.node_only and
            not self.suboutline_only
            and self.wrapPosition == None
        ):
            self.wrapping = True
            self.wrapPos = ins
            # Do not set self.wrapPosition here: that must be done after the first search.
    #@+node:ekr.20031218072017.3088: *4* find.printLine
    def printLine (self,line,allFlag=False):

        both = self.search_body and self.search_headline
        context = self.batch # "batch" now indicates context
        if allFlag and both and context:
            g.es('','-' * 20,'',self.p.h)
            theType = "head: " if self.in_headline else "body: "
            g.es('',theType + line)
        elif allFlag and context and not self.p.isVisited():
            # We only need to print the context once.
            g.es('','-' * 20,'',self.p.h)
            g.es('',line)
            self.p.setVisited()
        else:
            g.es('',line)
    #@+node:ekr.20131126174039.16719: *4* find.reset_state_ivars
    def reset_state_ivars(self):
        '''Reset ivars related to suboutline-only and wrapped searches.'''
        self.onlyPosition = None
        self.wrapping = False
        self.wrapPosition = None
        self.wrapPos = None
    #@+node:ekr.20031218072017.3089: *4* find.restore
    def restore (self,data):
        '''Restore the screen and clear state after a search fails.'''
        c = self.c
        in_headline,editing,p,w,insert,start,end = data
        self.was_in_headline = not self.was_in_headline
        if 0: # Don't do this here.
            # Reset ivars related to suboutline-only and wrapped searches.
            self.reset_state_ivars()
        c.frame.bringToFront() # Needed on the Mac
        # Don't try to reedit headline.
        if p and c.positionExists(p): # 2013/11/22.
            c.selectPosition(p)
        else:
            c.selectPosition(c.rootPosition()) # New in Leo 4.5.
        # Fix bug 1258373: https://bugs.launchpad.net/leo-editor/+bug/1258373
        if in_headline:
            c.selectPosition(p)
            if False and editing:
                c.editHeadline()
            else:
                c.treeWantsFocus()
        else:
            # Looks good and provides clear indication of failure or termination.
            w.setSelectionRange(insert,insert)
            w.setInsertPoint(insert)
            w.seeInsertPoint()
            c.widgetWantsFocus(w)
    #@+node:ekr.20031218072017.3090: *4* find.save
    def save (self):
        '''Save everything needed to restore after a search fails.'''
        c = self.c
        p = self.p or c.p
        # Fix bug 1258373: https://bugs.launchpad.net/leo-editor/+bug/1258373
        if self.in_headline:
            e = c.edit_widget(p)
            w = e or c.frame.tree.canvas
            insert,start,end = None,None,None
        else:
            w = c.frame.body.wrapper
            e = None
            insert = w.getInsertPoint()
            sel = w.getSelectionRange()
            if len(sel) == 2:
                start,end = sel
            else:
                start,end = None,None
        editing = e is not None
        return self.in_headline,editing,p.copy(),w,insert,start,end
    #@+node:ekr.20031218072017.3091: *4* find.showSuccess
    def showSuccess(self,pos,newpos,showState=True):
        '''Display the result of a successful find operation.'''
        trace = False and not g.unitTesting
        c = self.c
        self.p = p = self.p or c.p.copy()
        # Set state vars.
        # Ensure progress in backwards searches.
        insert = min(pos,newpos) if self.reverse else max(pos,newpos)
        if self.wrap and not self.wrapPosition:
            self.wrapPosition = self.p
        if trace: g.trace('in_headline',self.in_headline,p)
        if c.sparse_find:
            c.expandOnlyAncestorsOfNode(p=p)
        if self.in_headline:
            c.endEditing()
            selection = pos,newpos,insert
            c.redrawAndEdit(p,
                selection=selection,
                keepMinibuffer=True)
            w = c.edit_widget(p)
        else:
            w = c.frame.body.wrapper
            # Bug fix: 2012/11/26: *Always* do the full selection logic.
            # This ensures that the body text is inited  and recolored.
            c.selectPosition(p)
            c.bodyWantsFocus()
            if showState:
                c.k.showStateAndMode(w)
            c.bodyWantsFocusNow()
            # assert w.getAllText() == p.b.replace('\r','')
            w.setSelectionRange(pos,newpos,insert=insert)
            w.see(insert)
            p.v.scrollBarSpot = None
                # Fix bug 78: F3 find-next target not always highlighted
                # Disable the scrolling in v.restoreCursorAndScroll
            if trace: g.trace('p.b',len(p.b),'w.text',len(w.getAllText()),'sel',w.getSelectionRange())
            c.outerUpdate()
            if c.vim_mode and c.vimCommands:
                c.vimCommands.update_selection_after_search()
        return w # Support for isearch.
    #@+node:ekr.20031218072017.1460: *4* find.update_ivars
    def update_ivars (self):
        """Update ivars from the find panel."""
        trace = False and not g.unitTesting
        c = self.c
        self.p = c.p.copy()
        ftm = self.ftm
        # The caller is responsible for removing most trailing cruft.
        # Among other things, this allows Leo to search for a single trailing space.
        s = ftm.getFindText()
        s = g.toUnicode(s)
        if trace: g.trace('find',repr(s))
        if s and s[-1] in ('\r','\n'):
            s = s[:-1]
        if self.radioButtonsChanged or s != self.find_text:
            self.radioButtonsChanged = False
            # Reset ivars related to suboutline-only and wrapped searches.
            self.reset_state_ivars()
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
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
