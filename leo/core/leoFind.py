#@+leo-ver=5-thin
#@+node:ekr.20060123151617: * @file leoFind.py
"""Leo's gui-independent find classes."""
import re
import sys
import time

# Transcrypt does not support Python's copy or keyword module.
# __pragma__ ('skip')
import keyword
import unittest
# __pragma__ ('noskip')

from leo.core import leoGlobals as g

#@+<< Theory of operation of find/change >>
#@+node:ekr.20031218072017.2414: ** << Theory of operation of find/change >>
#@@language rest
#@+at
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
    """A class to simulating high-level interface widget."""
    # This could be a StringTextWrapper, but this code is simple and good.

    def __init__(self, *args, **keys):
        self.s = ''  # The widget text
        self.i = 0  # The insert point
        self.sel = 0, 0  # The selection range

    def __repr__(self):
        return f"SearchWidget id: {id(self)}"
    #@+others
    #@+node:ekr.20070105093138: *3* getters (LeoFind)
    def getAllText(self): return self.s

    def getInsertPoint(self): return self.i  # Returns Python index.

    def getSelectionRange(self): return self.sel  # Returns Python indices.
    #@+node:ekr.20070105102419: *3* setters (LeoFind)
    def delete(self, i, j=None):
        i = self.toPythonIndex(i)
        if j is None: j = i + 1
        else: j = self.toPythonIndex(j)
        self.s = self.s[:i] + self.s[j:]
        # Bug fix: 2011/11/13: Significant in external tests.
        self.i = i
        self.sel = i, i

    def insert(self, i, s):
        if not s: return
        i = self.toPythonIndex(i)
        self.s = self.s[:i] + s + self.s[i:]
        self.i = i
        self.sel = i, i

    def setAllText(self, s):
        self.s = s
        self.i = 0
        self.sel = 0, 0

    def setInsertPoint(self, i, s=None):
        self.i = i

    def setSelectionRange(self, i, j, insert=None):
        self.sel = self.toPythonIndex(i), self.toPythonIndex(j)
        if insert is not None:
            self.i = self.toPythonIndex(insert)
    #@+node:ekr.20070105092022.4: *3* toPythonIndex (LeoFind)
    def toPythonIndex(self, i):
        return g.toPythonIndex(self.s, i)
    #@-others
#@+node:ekr.20061212084717: ** class LeoFind (LeoFind.py)
class LeoFind:
    """The base class for Leo's Find commands."""
    #@+others
    #@+node:ekr.20131117164142.17021: *3* LeoFind.birth
    #@+node:ekr.20031218072017.3053: *4* LeoFind.__init__
    #@@nobeautify

    def __init__(self, c):
        """Ctor for LeoFind class."""
        self.c = c
        self.errors = 0
        self.expert_mode = False
            # Set in finishCreate.
        self.ftm = None
            # Created by dw.createFindTab.
        self.frame = None
        self.k = c.k
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
        # For isearch commands...
        self.stack = [] # Entries are (p,sel)
        self.isearch_ignore_case = None
        self.isearch_forward = None
        self.isearch_regexp = None
        self.findTextList = []
        self.changeTextList = []
        # Widget ivars...
        self.change_ctrl = None
        self.s_ctrl = SearchWidget()
            # A helper widget for searches.
        self.find_text = ""
        self.change_text = ""
        self.radioButtonsChanged = False
            # Set by ftm.radio_button_callback
        #
        # Communication betweenfind-def and startSearch
        self.find_def_data = None
            # Saved regular find settings.
        self.find_seen = set()
            # Set of vnodes.
        #
        # Ivars containing internal state...
        self.buttonFlag = False
        self.changeAllFlag = False
        self.findAllFlag = False
        self.findAllUniqueFlag = False
        self.in_headline = False
            # True: searching headline text.
        self.match_obj = None
            # The match object returned for regex or find-all-unique-regex searches.
        self.p = None
            # The position being searched.
            # Never saved between searches!
        self.unique_matches = set()
        self.was_in_headline = None
            # Fix bug: https://groups.google.com/d/msg/leo-editor/RAzVPihqmkI/-tgTQw0-LtwJ
        self.onlyPosition = None
            # The starting node for suboutline-only searches.
        self.wrapping = False
            # True: wrapping is enabled.
            # This must be different from self.wrap, which is set by the checkbox.
        self.wrapPosition = None
            # The start of wrapped searches.
            # Persists between calls.
        self.wrapPos = None
            # The starting position of the wrapped search.
            # Persists between calls.
        self.state_on_start_of_search = None
            # keeps all state data that should be restored once the search is exhausted
    #@+node:ekr.20150509032822.1: *4* LeoFind.cmd (decorator)
    def cmd(name):
        """Command decorator for the findCommands class."""
        # pylint: disable=no-self-argument
        return g.new_cmd_decorator(name, ['c', 'findCommands',])
    #@+node:ekr.20131117164142.17022: *4* LeoFind.finishCreate
    def finishCreate(self):
        # New in 4.11.1.
        # Must be called when config settings are valid.
        c = self.c
        self.reloadSettings()
        # now that configuration settings are valid,
        # we can finish creating the Find pane.
        dw = c.frame.top
        if dw: dw.finishCreateLogPane()
    #@+node:ekr.20171113164709.1: *4* LeoFind.reloadSettings
    def reloadSettings(self):
        """LeoFind.reloadSettings."""
        c = self.c
        self.ignore_dups = c.config.getBool('find-ignore-duplicates', default=False)
        self.minibuffer_mode = c.config.getBool('minibuffer-find-mode', default=False)
    #@+node:ekr.20060123065756.1: *3* LeoFind.Buttons (immediate execution)
    #@+node:ekr.20031218072017.3057: *4* find.changeAllButton
    def changeAllButton(self, event=None):
        """Handle Replace All button."""
        c = self.c
        self.setup_button()
        c.clearAllVisited()  # For context reporting.
        self.changeAll()
    #@+node:ekr.20031218072017.3056: *4* find.changeButton
    def changeButton(self, event=None):
        """Handle Change button."""
        self.setup_button()
        self.change()
    #@+node:ekr.20031218072017.3058: *4* find.changeThenFindButton
    def changeThenFindButton(self, event=None):
        """Handle Change, Then Find button."""
        self.setup_button()
        self.changeThenFind()
    #@+node:ekr.20031218072017.3060: *4* find.findAllButton
    def findAllButton(self, event=None):
        """Handle Find All button."""
        self.setup_button()
        self.findAll()
    #@+node:ekr.20031218072017.3059: *4* find.findButton (headline hack)
    def findButton(self, event=None):
        """Handle pressing the "Find" button in the find panel."""
        c, p = self.c, self.c.p
        p0 = p.copy()
        self.setup_button()
        # Move forward one node if we found a match in a headline:
        #   Pressing the button destroys c.edit_widget(p), so
        #   initInteractiveCommands does not compute ins properly.
        if self.was_in_headline:
            self.was_in_headline = False
            if p.hasThreadNext():
                p.moveToThreadNext()
                c.selectPosition(p)
            self.p = p.copy()
        if not self.findNext() and p0 != c.p:
            # Undo the effect of selecting the next node.
            p0.contract()
            c.selectPosition(p0)
            c.redraw()
    #@+node:ekr.20131117054619.16688: *4* find.findPreviousButton (headline hack)
    def findPreviousButton(self, event=None):
        """Handle the Find Previous button."""
        c, p = self.c, self.c.p
        p0 = p.copy()
        self.setup_button()
        # Move back one node if we found a match in a headline:
        #   Pressing the button destroys c.edit_widget(p), so
        #   initInteractiveCommands does not compute ins properly.
        if self.was_in_headline:
            self.was_in_headline = False
            if p.hasThreadBack():
                p.moveToThreadBack()
                c.selectPosition(p)
            self.p = p.copy()
        self.reverse = True
        try:
            if not self.findNext() and p0 != c.p:
                # Undo the effect of selecting the previous node.
                p0.contract()
                c.selectPosition(p0)
                c.redraw()
        finally:
            self.reverse = False
    #@+node:ekr.20031218072017.3065: *4* find.setup_button
    def setup_button(self):
        """Init a search started by a button in the Find panel."""
        c = self.c
        self.buttonFlag = True
        self.p = c.p
        c.bringToFront()
        if 0:  # We _must_ retain the editing status for incremental searches!
            c.endEditing()
        self.update_ivars()
    #@+node:ekr.20031218072017.3055: *3* LeoFind.Commands (immediate execution)
    #@+node:ekr.20031218072017.3061: *4* find.changeCommand
    def changeCommand(self, event=None):
        """Handle replace command."""
        self.setup_command()
        self.change()
    #@+node:ekr.20031218072017.3062: *4* find.changeThenFindCommand
    @cmd('replace-then-find')
    def changeThenFindCommand(self, event=None):
        """Handle the replace-then-find command."""
        self.setup_command()
        self.changeThenFind()
    #@+node:ekr.20131122231705.16463: *4* find.cloneFindAllCommand
    def cloneFindAllCommand(self, event=None):
        self.setup_command()
        self.findAll(clone_find_all=True)
    #@+node:ekr.20131122231705.16464: *4* find.cloneFindAllFlattenedCommand
    def cloneFindAllFlattenedCommand(self, event=None):
        self.setup_command()
        self.findAll(clone_find_all=True, clone_find_all_flattened=True)
    #@+node:ekr.20131122231705.16465: *4* find.findAllCommand
    def findAllCommand(self, event=None):
        self.setup_command()
        self.findAll()
    #@+node:ekr.20150629084204.1: *4* find.findDef, findVar & helpers
    @cmd('find-def')
    def findDef(self, event=None):
        """Find the def or class under the cursor."""
        self.findDefHelper(event, defFlag=True)

    @cmd('find-var')
    def findVar(self, event=None):
        """Find the var under the cursor."""
        self.findDefHelper(event, defFlag=False)
    #@+node:ekr.20150629125733.1: *5* findDefHelper & helpers
    def findDefHelper(self, event, defFlag):
        """Find the definition of the class, def or var under the cursor."""
        c, find, ftm = self.c, self, self.ftm
        w = c.frame.body.wrapper
        if not w:
            return
        word = self.initFindDef(event)
        if not word:
            return
        save_sel = w.getSelectionRange()
        ins = w.getInsertPoint()
        # For the command, always start in the root position.
        old_p = c.p
        p = c.rootPosition()
        # Required.
        c.selectPosition(p)
        c.redraw()
        c.bodyWantsFocusNow()
        # Set up the search.
        if defFlag:
            prefix = 'class' if word[0].isupper() else 'def'
            find_pattern = prefix + ' ' + word
        else:
            find_pattern = word + ' ='
        find.find_text = find_pattern
        ftm.setFindText(find_pattern)
        # Save previous settings.
        find.saveBeforeFindDef(p)
        find.setFindDefOptions(p)
        self.find_seen = set()
        use_cff = c.config.getBool('find-def-creates-clones', default=False)
        count = 0
        if use_cff:
            count = find.findAll(clone_find_all=True, clone_find_all_flattened=True)
            found = count > 0
        else:
            # #1592.  Ignore hits under control of @nosearch
            while True:
                found = find.findNext(initFlag=False)
                if not found or not g.inAtNosearch(c.p):
                    break
        if not found and defFlag:
            # Leo 5.7.3: Look for an alternative defintion of function/methods.
            word2 = self.switchStyle(word)
            if word2:
                find_pattern = prefix + ' ' + word2
                find.find_text = find_pattern
                ftm.setFindText(find_pattern)
                if use_cff:
                    count = find.findAll(
                        clone_find_all=True, clone_find_all_flattened=True)
                    found = count > 0
                else:
                    # #1592.  Ignore hits under control of @nosearch
                    while True:
                        found = find.findNext(initFlag=False)
                        if not found or not g.inAtNosearch(c.p):
                            break
        if found and use_cff:
            last = c.lastTopLevel()
            if count == 1:
                # It's annoying to create a clone in this case.
                # Undo the clone find and just select the proper node.
                last.doDelete()
                find.findNext(initFlag=False)
            else:
                c.selectPosition(last)
        if found:
            self.find_seen.add(c.p.v)
            self.restoreAfterFindDef()
                # Failing to do this causes massive confusion!
        else:
            c.selectPosition(old_p)
            self.restoreAfterFindDef()  # 2016/03/24
            i, j = save_sel
            c.redraw()
            w.setSelectionRange(i, j, insert=ins)
            c.bodyWantsFocusNow()
    #@+node:ekr.20180511045458.1: *6* switchStyle
    def switchStyle(self, word):
        """
        Switch between camelCase and underscore_style function defintiions.
        Return None if there would be no change.
        """
        s = word
        if s.find('_') > -1:
            if s.startswith('_'):
                # Don't return something that looks like a class.
                return None
            #
            # Convert to CamelCase
            s = s.lower()
            while s:
                i = s.find('_')
                if i == -1:
                    break
                s = s[:i] + s[i + 1 :].capitalize()
            return s
        #
        # Convert to underscore_style.
        result = []
        for i, ch in enumerate(s):
            if i > 0 and ch.isupper():
                result.append('_')
            result.append(ch.lower())
        s = ''.join(result)
        return None if s == word else s
    #@+node:ekr.20150629084611.1: *6* initFindDef
    def initFindDef(self, event):
        """Init the find-def command. Return the word to find or None."""
        c = self.c
        w = c.frame.body.wrapper
        # First get the word.
        c.bodyWantsFocusNow()
        w = c.frame.body.wrapper
        if not w.hasSelection():
            c.editCommands.extendToWord(event, select=True)
        word = w.getSelectedText().strip()
        if not word:
            return None
        # Transcrypt does not support Python's keyword module.
        # __pragma__ ('skip')
        if keyword.iskeyword(word):
            return None
        # __pragma__ ('noskip')
        
        # Return word, stripped of preceding class or def.
        for tag in ('class ', 'def '):
            found = word.startswith(tag) and len(word) > len(tag)
            if found:
                return word[len(tag) :].strip()
        return word
    #@+node:ekr.20150629095633.1: *6* find.saveBeforeFindDef
    def saveBeforeFindDef(self, p):
        """Save the find settings in effect before a find-def command."""
        if not self.find_def_data:
            self.find_def_data = g.Bunch(
                ignore_case=self.ignore_case,
                p=p.copy(),
                pattern_match=self.pattern_match,
                search_body=self.search_body,
                search_headline=self.search_headline,
                whole_word=self.whole_word,
            )
    #@+node:ekr.20150629100600.1: *6* find.setFindDefOptions
    def setFindDefOptions(self, p):
        """Set the find options needed for the find-def command."""
        self.ignore_case = False
        self.p = p.copy()
        self.pattern_match = False
        self.reverse = False
        self.search_body = True
        self.search_headline = False
        self.whole_word = True
    #@+node:ekr.20150629095511.1: *6* find.restoreAfterFindDef
    def restoreAfterFindDef(self):
        """Restore find settings in effect before a find-def command."""
        # pylint: disable=no-member
            # Bunch has these members
        b = self.find_def_data  # A g.Bunch
        if b:
            self.ignore_case = b.ignore_case
            self.p = b.p
            self.pattern_match = b.pattern_match
            self.reverse = False
            self.search_body = b.search_body
            self.search_headline = b.search_headline
            self.whole_word = b.whole_word
            self.find_def_data = None
    #@+node:ekr.20031218072017.3063: *4* find.findNextCommand
    @cmd('find-next')
    def findNextCommand(self, event=None):
        """The find-next command."""
        self.setup_command()
        self.findNext()
    #@+node:ekr.20031218072017.3064: *4* find.findPrevCommand
    @cmd('find-prev')
    def findPrevCommand(self, event=None):
        """Handle F2 (find-previous)"""
        self.setup_command()
        self.reverse = True
        try:
            self.findNext()
        finally:
            self.reverse = False
    #@+node:ekr.20141113094129.6: *4* find.focusToFind
    @cmd('focus-to-find')
    def focusToFind(self, event=None):
        c = self.c
        if c.config.getBool('use-find-dialog', default=True):
            g.app.gui.openFindDialog(c)
        else:
            c.frame.log.selectTab('Find')
    #@+node:ekr.20131119204029.16479: *4* find.helpForFindCommands
    def helpForFindCommands(self, event=None):
        """Called from Find panel.  Redirect."""
        self.c.helpCommands.helpForFindCommands(event)
    #@+node:ekr.20131117164142.17015: *4* find.hideFindTab
    @cmd('find-tab-hide')
    def hideFindTab(self, event=None):
        """Hide the Find tab."""
        c = self.c
        if self.minibuffer_mode:
            c.k.keyboardQuit()
        else:
            self.c.frame.log.selectTab('Log')
    #@+node:ekr.20131117164142.16916: *4* find.openFindTab
    @cmd('find-tab-open')
    def openFindTab(self, event=None, show=True):
        """Open the Find tab in the log pane."""
        c = self.c
        if c.config.getBool('use-find-dialog', default=True):
            g.app.gui.openFindDialog(c)
        else:
            c.frame.log.selectTab('Find')
    #@+node:ekr.20131117164142.17016: *4* find.changeAllCommand
    def changeAllCommand(self, event=None):
        c = self.c
        self.setup_command()
        self.changeAll()
        # Bugs #947, #880 and #722:
        # Set ancestor @<file> nodes by brute force.
        for p in c.all_positions():
            if (
                p.anyAtFileNodeName()
                and not p.v.isDirty()
                and any([p2.v.isDirty() for p2 in p.subtree()])
            ):
                p.setDirty()
        c.redraw()
    #@+node:ekr.20150629072547.1: *4* find.preloadFindPattern
    def preloadFindPattern(self, w):
        """Preload the find pattern from the selected text of widget w."""
        c, ftm = self.c, self.ftm
        if not c.config.getBool('preload-find-pattern', default=False):
            # Make *sure* we don't preload the find pattern if it is not wanted.
            return
        if not w:
            return
        #
        # #1436: Don't create a selection if there isn't one.
        #        Leave the search pattern alone!
        #
            # if not w.hasSelection():
            #     c.editCommands.extendToWord(event=None, select=True, w=w)
        #
        # #177:  Use selected text as the find string.
        # #1436: Make make sure there is a significant search pattern.
        s = w.getSelectedText()
        if s.strip():
            ftm.setFindText(s)
            ftm.init_focus()
    #@+node:ekr.20031218072017.3066: *4* find.setup_command
    # Initializes a search when a command is invoked from the menu.

    def setup_command(self):
        if 0:  # We _must_ retain the editing status for incremental searches!
            self.c.endEditing()
        # Fix bug
        self.buttonFlag = False
        self.update_ivars()
    #@+node:ekr.20131119060731.22452: *4* find.startSearch
    @cmd('start-search')
    def startSearch(self, event):
        w = self.editWidget(event)
        # This causes problems.
            # if self.minibuffer_mode:
                # self.c.frame.log.selectTab('Find')
        if w:
            self.preloadFindPattern(w)
        self.find_seen = set()
        if self.minibuffer_mode:
            self.ftm.clear_focus()
            self.searchWithPresentOptions(event)
        else:
            self.openFindTab(event)
            self.ftm.init_focus()
    #@+node:vitalije.20170712162056.1: *4* find.returnToOrigin
    @cmd('search-return-to-origin')
    def returnToOrigin(self, event):
        data = self.state_on_start_of_search
        if not data: return
        self.restore(data)
        self.restoreAllExpansionStates(data[-1], redraw=True)
    #@+node:ekr.20131117164142.16939: *3* LeoFind.ISearch
    #@+node:ekr.20131117164142.16941: *4* find.isearchForward
    @cmd('isearch-forward')
    def isearchForward(self, event):
        """
        Begin a forward incremental search.

        - Plain characters extend the search.
        - !<isearch-forward>! repeats the search.
        - Esc or any non-plain key ends the search.
        - Backspace reverses the search.
        - Backspacing to an empty search pattern
          completely undoes the effect of the search.
        """
        self.startIncremental(event, 'isearch-forward',
            forward=True, ignoreCase=False, regexp=False)
    #@+node:ekr.20131117164142.16942: *4* find.isearchBackward
    @cmd('isearch-backward')
    def isearchBackward(self, event):
        """
        Begin a backward incremental search.

        - Plain characters extend the search backward.
        - !<isearch-forward>! repeats the search.
        - Esc or any non-plain key ends the search.
        - Backspace reverses the search.
        - Backspacing to an empty search pattern
          completely undoes the effect of the search.
        """
        self.startIncremental(event, 'isearch-backward',
            forward=False, ignoreCase=False, regexp=False)
    #@+node:ekr.20131117164142.16943: *4* find.isearchForwardRegexp
    @cmd('isearch-forward-regexp')
    def isearchForwardRegexp(self, event):
        """
        Begin a forward incremental regexp search.

        - Plain characters extend the search.
        - !<isearch-forward-regexp>! repeats the search.
        - Esc or any non-plain key ends the search.
        - Backspace reverses the search.
        - Backspacing to an empty search pattern
          completely undoes the effect of the search.
        """
        self.startIncremental(event, 'isearch-forward-regexp',
            forward=True, ignoreCase=False, regexp=True)
    #@+node:ekr.20131117164142.16944: *4* find.isearchBackwardRegexp
    @cmd('isearch-backward-regexp')
    def isearchBackwardRegexp(self, event):
        """
        Begin a backward incremental regexp search.

        - Plain characters extend the search.
        - !<isearch-forward-regexp>! repeats the search.
        - Esc or any non-plain key ends the search.
        - Backspace reverses the search.
        - Backspacing to an empty search pattern
          completely undoes the effect of the search.
        """
        self.startIncremental(event, 'isearch-backward-regexp',
            forward=False, ignoreCase=False, regexp=True)
    #@+node:ekr.20131117164142.16945: *4* find.isearchWithPresentOptions
    @cmd('isearch-with-present-options')
    def isearchWithPresentOptions(self, event):
        """
        Begin an incremental search using find panel options.

        - Plain characters extend the search.
        - !<isearch-forward-regexp>! repeats the search.
        - Esc or any non-plain key ends the search.
        - Backspace reverses the search.
        - Backspacing to an empty search pattern
          completely undoes the effect of the search.
        """
        self.startIncremental(event, 'isearch-with-present-options',
            forward=None, ignoreCase=None, regexp=None)
    #@+node:ekr.20131117164142.16946: *3* LeoFind.Isearch utils
    #@+node:ekr.20131117164142.16947: *4* find.abortSearch (incremental)
    def abortSearch(self):
        """Restore the original position and selection."""
        c = self.c; k = self.k
        w = c.frame.body.wrapper
        k.clearState()
        k.resetLabel()
        p, i, j, in_headline = self.stack[0]
        self.in_headline = in_headline
        c.selectPosition(p)
        c.redraw_after_select(p)
        c.bodyWantsFocus()
        w.setSelectionRange(i, j)
    #@+node:ekr.20131117164142.16948: *4* find.endSearch
    def endSearch(self):
        c, k = self.c, self.k
        k.clearState()
        k.resetLabel()
        c.bodyWantsFocus()
    #@+node:ekr.20131117164142.16949: *4* find.iSearch
    def iSearch(self, again=False):
        """Handle the actual incremental search."""
        c, k = self.c, self.k
        self.p = c.p
        reverse = not self.isearch_forward
        pattern = k.getLabel(ignorePrompt=True)
        if not pattern:
            self.abortSearch()
            return
        # Get the base ivars from the find tab.
        self.update_ivars()
        # Save
        oldPattern = self.find_text
        oldRegexp = self.pattern_match
        oldWord = self.whole_word
        # Override
        self.pattern_match = self.isearch_regexp
        self.reverse = reverse
        self.find_text = pattern
        self.whole_word = False  # Word option can't be used!
        # Prepare the search.
        if len(self.stack) <= 1: self.in_headline = False
        w = self.setWidget()
        s = w.getAllText()
        i, j = w.getSelectionRange()
        if again: ins = i if reverse else j + len(pattern)
        else: ins = j + len(pattern) if reverse else i
        self.init_s_ctrl(s, ins)
        # Do the search!
        pos, newpos = self.findNextMatch()
        # Restore.
        self.find_text = oldPattern
        self.pattern_match = oldRegexp
        self.reverse = False
        self.whole_word = oldWord
        # Handle the results of the search.
        if pos is not None:  # success.
            w = self.showSuccess(pos, newpos, showState=False)
            if w: i, j = w.getSelectionRange(sort=False)
            if not again:
                self.push(c.p, i, j, self.in_headline)
        elif self.wrapping:
            # g.es("end of wrapped search")
            k.setLabelRed('end of wrapped search')
        else:
            g.es(f"not found: {pattern}")
            if not again:
                event = g.app.gui.create_key_event(
                    c, binding='BackSpace', char='\b', w=w)
                k.updateLabel(event)
    #@+node:ekr.20131117164142.16950: *4* find.iSearchStateHandler
    def iSearchStateHandler(self, event):
        """The state manager when the state is 'isearch"""
        # c = self.c
        k = self.k
        stroke = event.stroke if event else None
        s = stroke.s if stroke else ''
        # No need to recognize ctrl-z.
        if s in ('Escape', '\n', 'Return'):
            self.endSearch()
        elif stroke in self.iSearchStrokes:
            self.iSearch(again=True)
        elif s in ('\b', 'BackSpace'):
            k.updateLabel(event)
            self.iSearchBackspace()
        elif (
            s.startswith('Ctrl+') or
            s.startswith('Alt+') or
            k.isFKey(s)  # 2011/06/13.
        ):
            # End the search.
            self.endSearch()
            k.masterKeyHandler(event)
        # Fix bug 1267921: isearch-forward accepts non-alphanumeric keys as input.
        elif k.isPlainKey(stroke):
            k.updateLabel(event)
            self.iSearch()
    #@+node:ekr.20131117164142.16951: *4* find.iSearchBackspace
    def iSearchBackspace(self):

        c = self.c
        if len(self.stack) <= 1:
            self.abortSearch()
            return
        # Reduce the stack by net 1.
        self.pop()
        p, i, j, in_headline = self.pop()
        self.push(p, i, j, in_headline)
        if in_headline:
            # Like self.showSuccess.
            selection = i, j, i
            c.redrawAndEdit(p, selectAll=False,
                selection=selection,
                keepMinibuffer=True)
        else:
            c.selectPosition(p)
            w = c.frame.body.wrapper
            c.bodyWantsFocus()
            if i > j: i, j = j, i
            w.setSelectionRange(i, j)
        if len(self.stack) <= 1:
            self.abortSearch()
    #@+node:ekr.20131117164142.16952: *4* find.getStrokes
    def getStrokes(self, commandName):
        aList = self.inverseBindingDict.get(commandName, [])
        return [key for pane, key in aList]
    #@+node:ekr.20131117164142.16953: *4* find.push & pop
    def push(self, p, i, j, in_headline):
        data = p.copy(), i, j, in_headline
        self.stack.append(data)

    def pop(self):
        data = self.stack.pop()
        p, i, j, in_headline = data
        return p, i, j, in_headline
    #@+node:ekr.20131117164142.16954: *4* find.setWidget
    def setWidget(self):
        c = self.c; p = c.currentPosition()
        wrapper = c.frame.body.wrapper
        if self.in_headline:
            w = c.edit_widget(p)
            if not w:
                # Selecting the minibuffer can kill the edit widget.
                selection = 0, 0, 0
                c.redrawAndEdit(p, selectAll=False,
                    selection=selection, keepMinibuffer=True)
                w = c.edit_widget(p)
            if not w:  # Should never happen.
                g.trace('**** no edit widget!')
                self.in_headline = False; w = wrapper
        else:
            w = wrapper
        if w == wrapper:
            c.bodyWantsFocus()
        return w
    #@+node:ekr.20131117164142.16955: *4* find.startIncremental
    def startIncremental(self, event, commandName, forward, ignoreCase, regexp):
        c, k = self.c, self.k
        # None is a signal to get the option from the find tab.
        self.event = event
        self.isearch_forward = not self.reverse if forward is None else forward
        self.isearch_ignore_case = self.ignore_case if ignoreCase is None else ignoreCase
        self.isearch_regexp = self.pattern_match if regexp is None else regexp
        # Note: the word option can't be used with isearches!
        self.w = w = c.frame.body.wrapper
        self.p1 = c.p
        self.sel1 = w.getSelectionRange(sort=False)
        i, j = self.sel1
        self.push(c.p, i, j, self.in_headline)
        self.inverseBindingDict = k.computeInverseBindingDict()
        self.iSearchStrokes = self.getStrokes(commandName)
        k.setLabelBlue(
            "Isearch"
            f"{' Backward' if not self.isearch_forward else ''}"
            f"{' Regexp' if self.isearch_regexp else ''}"
            f"{' NoCase' if self.isearch_ignore_case else ''}"
            ": "
        )
        k.setState('isearch', 1, handler=self.iSearchStateHandler)
        c.minibufferWantsFocus()
    #@+node:ekr.20131117164142.17013: *3* LeoFind.Minibuffer commands
    #@+node:ekr.20131117164142.17011: *4* find.minibufferCloneFindAll
    @cmd('clone-find-all')
    @cmd('find-clone-all')
    @cmd('cfa')
    def minibufferCloneFindAll(self, event=None, preloaded=None):
        """
        clone-find-all ( aka find-clone-all and cfa).

        Create an organizer node whose descendants contain clones of all nodes
        matching the search string, except @nosearch trees.

        The list is *not* flattened: clones appear only once in the
        descendants of the organizer node.
        """
        w = self.editWidget(event)  # sets self.w
        if w:
            if not preloaded:
                self.preloadFindPattern(w)
            self.stateZeroHelper(event,
                prefix='Clone Find All: ',
                handler=self.minibufferCloneFindAll1)

    def minibufferCloneFindAll1(self, event):
        c, k = self.c, self.k
        k.clearState()
        k.resetLabel()
        k.showStateAndMode()
        self.generalSearchHelper(k.arg, cloneFindAll=True)
        c.treeWantsFocus()
    #@+node:ekr.20131117164142.16996: *4* find.minibufferCloneFindAllFlattened
    @cmd('clone-find-all-flattened')
    @cmd('find-clone-all-flattened')
    @cmd('cff')
    def minibufferCloneFindAllFlattened(self, event=None, preloaded=None):
        """
        clone-find-all-flattened (aka find-clone-all-flattened and cff).

        Create an organizer node whose direct children are clones of all nodes
        matching the search string, except @nosearch trees.

        The list is flattened: every cloned node appears as a direct child
        of the organizer node, even if the clone also is a descendant of
        another cloned node.
        """
        w = self.editWidget(event)  # sets self.w
        if w:
            if not preloaded:
                self.preloadFindPattern(w)
            self.stateZeroHelper(event,
                prefix='Clone Find All Flattened: ',
                handler=self.minibufferCloneFindAllFlattened1)

    def minibufferCloneFindAllFlattened1(self, event):
        c = self.c; k = self.k
        k.clearState()
        k.resetLabel()
        k.showStateAndMode()
        self.generalSearchHelper(k.arg, cloneFindAllFlattened=True)
        c.treeWantsFocus()
    #@+node:ekr.20160920110324.1: *4* find.minibufferCloneFindTag
    @cmd('clone-find-tag')
    @cmd('find-clone-tag')
    @cmd('cft')
    def minibufferCloneFindTag(self, event=None):
        """
        clone-find-tag (aka find-clone-tag and cft).

        Create an organizer node whose descendants contain clones of all
        nodes matching the given tag, except @nosearch trees.

        The list is *always* flattened: every cloned node appears as a
        direct child of the organizer node, even if the clone also is a
        descendant of another cloned node.
        """
        if self.editWidget(event):  # sets self.w
            self.stateZeroHelper(event,
                prefix='Clone Find Tag: ',
                handler=self.minibufferCloneFindTag1)

    def minibufferCloneFindTag1(self, event):
        c, k = self.c, self.k
        k.clearState()
        k.resetLabel()
        k.showStateAndMode()
        self.find_text = k.arg
        self.cloneFindTag(k.arg)
        c.treeWantsFocus()
    #@+node:ekr.20131117164142.16998: *4* find.minibufferFindAll
    @cmd('find-all')
    def minibufferFindAll(self, event=None):
        """
        Create a summary node containing descriptions of all matches of the
        search string.
        """
        self.ftm.clear_focus()
        self.searchWithPresentOptions(event, findAllFlag=True)
    #@+node:ekr.20171226140643.1: *4* find.minibufferFindAllUnique
    @cmd('find-all-unique-regex')
    def minibufferFindAllUniqueRegex(self, event=None):
        """
        Create a summary node containing all unique matches of the regex search
        string. This command shows only the matched string itself.
        """
        self.ftm.clear_focus()
        self.match_obj = None
        self.unique_matches = set()
        self.searchWithPresentOptions(event, findAllFlag=True, findAllUniqueFlag=True)
    #@+node:ekr.20131117164142.16994: *4* find.minibufferReplaceAll
    @cmd('replace-all')
    def minibufferReplaceAll(self, event=None):
        """Replace all instances of the search string with the replacement string."""
        self.ftm.clear_focus()
        self.searchWithPresentOptions(event, changeAllFlag=True)
    #@+node:ekr.20160920164418.2: *4* find.minibufferTagChildren & helper
    @cmd('tag-children')
    def minibufferTagChildren(self, event=None):
        """tag-children: prompt for a tag and add it to all children of c.p."""
        if self.editWidget(event):  # sets self.w
            self.stateZeroHelper(event,
                prefix='Tag Children: ',
                handler=self.minibufferTagChildren1)
    def minibufferTagChildren1(self, event):
        c, k = self.c, self.k
        k.clearState()
        k.resetLabel()
        k.showStateAndMode()
        self.tagChildren(k.arg)
        c.treeWantsFocus()
    #@+node:ekr.20160920164418.4: *5* find.tagChildren
    def tagChildren(self, tag):
        """Handle the clone-find-tag command."""
        c = self.c
        tc = c.theTagController
        if tc:
            for p in c.p.children():
                tc.add_tag(p, tag)
            g.es_print(f"Added {tag} tag to {len(list(c.p.children()))} nodes")
        else:
            g.es_print('nodetags not active')
    #@+node:ekr.20131117164142.16983: *3* LeoFind.Minibuffer utils
    #@+node:ekr.20131117164142.16992: *4* find.addChangeStringToLabel
    def addChangeStringToLabel(self):
        """Add an unprotected change string to the minibuffer label."""
        c = self.c
        ftm = c.findCommands.ftm
        s = ftm.getChangeText()
        c.minibufferWantsFocus()
        while s.endswith('\n') or s.endswith('\r'):
            s = s[:-1]
        c.k.extendLabel(s, select=True, protect=False)
    #@+node:ekr.20131117164142.16993: *4* find.addFindStringToLabel
    def addFindStringToLabel(self, protect=True):
        c = self.c; k = c.k
        ftm = c.findCommands.ftm
        s = ftm.getFindText()
        c.minibufferWantsFocus()
        while s.endswith('\n') or s.endswith('\r'):
            s = s[:-1]
        k.extendLabel(s, select=True, protect=protect)
    #@+node:ekr.20131117164142.16985: *4* find.editWidget
    def editWidget(self, event, forceFocus=True):
        """
        An override of baseEditCommands.editWidget that does *not* set
        focus when using anything other than the tk gui.

        This prevents this class from caching an edit widget that is about
        to be deallocated.
        """
        c = self.c
        # Do not cache a pointer to a headline!
        # It will die when the minibuffer is selected.
        self.w = c.frame.body.wrapper
        return self.w
    #@+node:ekr.20131117164142.16999: *4* find.generalChangeHelper
    def generalChangeHelper(self, find_pattern, change_pattern, changeAll=False):
        c = self.c
        self.setupSearchPattern(find_pattern)
        self.setupChangePattern(change_pattern)
        if c.vim_mode and c.vimCommands:
            c.vimCommands.update_dot_before_search(
                find_pattern=find_pattern, change_pattern=change_pattern)
        c.widgetWantsFocusNow(self.w)
        self.p = c.p
        if changeAll:
            self.changeAllCommand()
        else:
            # This handles the reverse option.
            self.findNextCommand()
    #@+node:ekr.20131117164142.17000: *4* find.generalSearchHelper
    def generalSearchHelper(self, pattern,
        cloneFindAll=False,
        cloneFindAllFlattened=False,
        findAll=False,
    ):
        c = self.c
        self.setupSearchPattern(pattern)
        if c.vim_mode and c.vimCommands:
            c.vimCommands.update_dot_before_search(
                find_pattern=pattern,
                change_pattern=None)  # A flag indicating not a change command.
        c.widgetWantsFocusNow(self.w)
        self.p = c.p
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
    def lastStateHelper(self):
        k = self.k
        k.clearState()
        k.resetLabel()
        k.showStateAndMode()
    #@+node:ekr.20131117164142.17003: *4* find.reSearchBackward/Forward
    @cmd('re-search-backward')
    def reSearchBackward(self, event):
        self.setupArgs(forward=False, regexp=True, word=None)
        self.stateZeroHelper(event,
            'Regexp Search Backward:', self.reSearch1,
            escapes=['\t'])  # The Tab Easter Egg.

    @cmd('re-search-forward')
    def reSearchForward(self, event):
        self.setupArgs(forward=True, regexp=True, word=None)
        self.stateZeroHelper(event,
            prefix='Regexp Search:',
            handler=self.reSearch1,
            escapes=['\t'])  # The Tab Easter Egg.

    def reSearch1(self, event):
        k = self.k
        if k.getArgEscapeFlag:
            self.setReplaceString1(event=None)
        else:
            self.updateFindList(k.arg)
            self.lastStateHelper()
            self.generalSearchHelper(k.arg)
    #@+node:ekr.20131117164142.17004: *4* find.seachForward/Backward
    @cmd('search-backward')
    def searchBackward(self, event):
        self.setupArgs(forward=False, regexp=False, word=False)
        self.stateZeroHelper(event,
            prefix='Search Backward: ',
            handler=self.search1,
            escapes=['\t'])  # The Tab Easter Egg.

    @cmd('search-forward')
    def searchForward(self, event):
        self.setupArgs(forward=True, regexp=False, word=False)
        self.stateZeroHelper(event,
            prefix='Search: ',
            handler=self.search1,
            escapes=['\t'])  # The Tab Easter Egg.

    def search1(self, event):
        k = self.k
        if k.getArgEscapeFlag:
            # Switch to the replace command.
            self.setReplaceString1(event=None)
        else:
            self.updateFindList(k.arg)
            self.lastStateHelper()
            self.generalSearchHelper(k.arg)
    #@+node:ekr.20131117164142.17002: *4* find.setReplaceString
    @cmd('set-replace-string')
    def setReplaceString(self, event):
        """A state handler to get the replacement string."""
        prompt = 'Replace ' + ('Regex' if self.pattern_match else 'String')
        prefix = f"{prompt}: "
        self.stateZeroHelper(event,
            prefix=prefix,
            handler=self.setReplaceString1)

    def setReplaceString1(self, event):
        k = self.k
        prompt = 'Replace ' + ('Regex' if self.pattern_match else 'String')
        self._sString = k.arg
        self.updateFindList(k.arg)
        s = f"{prompt}: {self._sString} With: "
        k.setLabelBlue(s)
        self.addChangeStringToLabel()
        k.getNextArg(self.setReplaceString2)

    def setReplaceString2(self, event):
        k = self.k
        self.updateChangeList(k.arg)
        self.lastStateHelper()
        self.generalChangeHelper(self._sString, k.arg, changeAll=self.changeAllFlag)
    #@+node:ekr.20131117164142.17005: *4* find.searchWithPresentOptions & helpers
    @cmd('set-search-string')
    def searchWithPresentOptions(self, event,
    findAllFlag=False,
    findAllUniqueFlag=False,
    changeAllFlag=False,
    ):
        """Open the search pane and get the search string."""
        # Remember the entry focus, just as when using the find pane.
        self.changeAllFlag = changeAllFlag
        self.findAllFlag = findAllFlag
        self.findAllUniqueFlag = findAllUniqueFlag
        self.ftm.set_entry_focus()
        escapes = ['\t']
        escapes.extend(self.findEscapes())
        self.stateZeroHelper(event,
            'Search: ', self.searchWithPresentOptions1,
            escapes=escapes)  # The Tab Easter Egg.

    def searchWithPresentOptions1(self, event):

        c, k = self.c, self.k
        if k.getArgEscapeFlag:
            # 2015/06/30: Special cases for F2/F3 to the escapes
            if event.stroke in self.findEscapes():
                command = self.escapeCommand(event)
                func = c.commandsDict.get(command)
                k.clearState()
                k.resetLabel()
                k.showStateAndMode()
                if func:
                    func(event)
                else:
                    g.trace('unknown command', command)
                    return
            else:
                # Switch to the replace command.
                if self.findAllFlag:
                    self.changeAllFlag = True
                k.getArgEscapeFlag = False
                self.setupSearchPattern(k.arg)
                self.setReplaceString1(event=None)
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
    #@+node:ekr.20150630072025.1: *5* find.findEscapes
    def findEscapes(self):
        """Return the keystrokes corresponding to find-next & find-prev commands."""
        d = self.c.k.computeInverseBindingDict()
        results = []
        for command in ('find-def', 'find-next', 'find-prev', 'find-var',):
            aList = d.get(command, [])
            for data in aList:
                pane, stroke = data
                if pane.startswith('all'):
                    results.append(stroke)
        return results
    #@+node:ekr.20150630072552.1: *5* find.escapeCommand
    def escapeCommand(self, event):
        """Return the escaped command to execute."""
        d = self.c.k.bindingsDict
        aList = d.get(event.stroke)
        for bi in aList:
            if bi.stroke == event.stroke:
                return bi.commandName
        return None
    #@+node:ekr.20131117164142.17007: *4* find.stateZeroHelper
    def stateZeroHelper(self, event, prefix, handler, escapes=None):

        c, k = self.c, self.k
        self.w = self.editWidget(event)
        if not self.w:
            g.trace('no self.w')
            return
        k.setLabelBlue(prefix)
        # New in Leo 5.2: minibuffer modes shows options in status area.
        if self.minibuffer_mode:
            self.showFindOptionsInStatusArea()
        elif c.config.getBool('use-find-dialog', default=True):
            g.app.gui.openFindDialog(c)
        else:
            c.frame.log.selectTab('Find')
        self.addFindStringToLabel(protect=False)
        if escapes is None: escapes = []
        k.getArgEscapes = escapes
        k.getArgEscapeFlag = False  # k.getArg may set this.
        k.get1Arg(event, handler=handler, tabList=self.findTextList, completion=True)
    #@+node:ekr.20131117164142.17008: *4* find.updateChange/FindList
    def updateChangeList(self, s):
        if s not in self.changeTextList:
            self.changeTextList.append(s)

    def updateFindList(self, s):
        if s not in self.findTextList:
            self.findTextList.append(s)
    #@+node:ekr.20131117164142.17009: *4* find.wordSearchBackward/Forward (test)
    @cmd('word-search-backward')
    def wordSearchBackward(self, event):
        self.setupArgs(forward=False, regexp=False, word=True)
        self.stateZeroHelper(event,
            prefix='Word Search Backward: ',
            handler=self.wordSearch1)

    @cmd('word-search-forward')
    def wordSearchForward(self, event):
        self.setupArgs(forward=True, regexp=False, word=True)
        self.stateZeroHelper(event,
            prefix='Word Search: ',
            handler=self.wordSearch1)

    def wordSearch1(self, event):
        k = self.k
        self.lastStateHelper()
        self.generalSearchHelper(k.arg)
    #@+node:ekr.20131117164142.16915: *3* LeoFind.Option commands
    #@+node:ekr.20131117164142.16919: *4* LeoFind.toggle-find-*-option commands
    @cmd('toggle-find-collapses-nodes')
    def toggleFindCollapesNodes(self, event):
        """Toggle the 'Collapse Nodes' checkbox in the find tab."""
        c = self.c
        c.sparse_find = not c.sparse_find
        if not g.unitTesting:
            g.es('sparse_find', c.sparse_find)

    @cmd('toggle-find-ignore-case-option')
    def toggleIgnoreCaseOption(self, event):
        """Toggle the 'Ignore Case' checkbox in the Find tab."""
        return self.toggleOption('ignore_case')

    @cmd('toggle-find-mark-changes-option')
    def toggleMarkChangesOption(self, event):
        """Toggle the 'Mark Changes' checkbox in the Find tab."""
        return self.toggleOption('mark_changes')

    @cmd('toggle-find-mark-finds-option')
    def toggleMarkFindsOption(self, event):
        """Toggle the 'Mark Finds' checkbox in the Find tab."""
        return self.toggleOption('mark_finds')

    @cmd('toggle-find-regex-option')
    def toggleRegexOption(self, event):
        """Toggle the 'Regexp' checkbox in the Find tab."""
        return self.toggleOption('pattern_match')

    @cmd('toggle-find-in-body-option')
    def toggleSearchBodyOption(self, event):
        """Set the 'Search Body' checkbox in the Find tab."""
        return self.toggleOption('search_body')

    @cmd('toggle-find-in-headline-option')
    def toggleSearchHeadlineOption(self, event):
        """Toggle the 'Search Headline' checkbox in the Find tab."""
        return self.toggleOption('search_headline')

    @cmd('toggle-find-word-option')
    def toggleWholeWordOption(self, event):
        """Toggle the 'Whole Word' checkbox in the Find tab."""
        return self.toggleOption('whole_word')

    @cmd('toggle-find-wrap-around-option')
    def toggleWrapSearchOption(self, event):
        """Toggle the 'Wrap Around' checkbox in the Find tab."""
        return self.toggleOption('wrap')

    def toggleOption(self, checkbox_name):
        c, fc = self.c, self.c.findCommands
        self.ftm.toggle_checkbox(checkbox_name)
        options = fc.computeFindOptionsInStatusArea()
        c.frame.statusLine.put(options)
    #@+node:ekr.20131117164142.17019: *4* LeoFind.set-find-* commands
    @cmd('set-find-everywhere')
    def setFindScopeEveryWhere(self, event=None):
        """Set the 'Entire Outline' radio button in the Find tab."""
        return self.setFindScope('entire-outline')

    @cmd('set-find-node-only')
    def setFindScopeNodeOnly(self, event=None):
        """Set the 'Node Only' radio button in the Find tab."""
        return self.setFindScope('node-only')

    @cmd('set-find-suboutline-only')
    def setFindScopeSuboutlineOnly(self, event=None):
        """Set the 'Suboutline Only' radio button in the Find tab."""
        return self.setFindScope('suboutline-only')

    def setFindScope(self, where):
        """Set the radio buttons to the given scope"""
        c, fc = self.c, self.c.findCommands
        self.ftm.set_radio_button(where)
        options = fc.computeFindOptionsInStatusArea()
        c.frame.statusLine.put(options)
    #@+node:ekr.20131117164142.16989: *4* LeoFind.showFindOptions & helper
    @cmd('show-find-options')
    def showFindOptions(self, event=None):
        """
        Show the present find options in the status line.
        This is useful for commands like search-forward that do not show the Find Panel.
        """
        frame = self.c.frame
        frame.clearStatusLine()
        part1, part2 = self.computeFindOptions()
        frame.putStatusLine(part1, bg='blue')
        frame.putStatusLine(part2)
    #@+node:ekr.20171129205648.1: *5* LeoFind.computeFindOptions
    def computeFindOptions(self):
        """Return the status line as two strings."""
        z = []
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
        part1 = f"{head}{sep}{body} {scope}  "
        # Set the type field.
        regex = self.pattern_match
        if regex: z.append('regex')
        table = (
            ('reverse', 'reverse'),
            ('ignore_case', 'noCase'),
            ('whole_word', 'word'),
            ('wrap', 'wrap'),
            ('mark_changes', 'markChg'),
            ('mark_finds', 'markFnd'),
        )
        for ivar, s in table:
            val = getattr(self, ivar)
            if val: z.append(s)
        part2 = ' '.join(z)
        return part1, part2
    #@+node:ekr.20131117164142.16990: *4* LeoFind.setupChangePattern
    def setupChangePattern(self, pattern):
        self.ftm.setChangeText(pattern)
    #@+node:ekr.20131117164142.16991: *4* LeoFind.setupSearchPattern
    def setupSearchPattern(self, pattern):
        self.ftm.setFindText(pattern)
    #@+node:ekr.20031218072017.3067: *3* LeoFind.Utils
    #@+node:ekr.20031218072017.3068: *4* find.change
    @cmd('replace')
    def change(self, event=None):
        if self.checkArgs():
            self.initInHeadline()
            self.changeSelection()

    replace = change
    #@+node:ekr.20031218072017.3069: *4* find.changeAll & helpers
    def changeAll(self):

        c, current, u = self.c, self.c.p, self.c.undoer
        undoType = 'Replace All'
        t1 = time.process_time()
        if not self.checkArgs():
            return
        self.initInHeadline()
        saveData = self.save()
        self.initBatchCommands()
        count = 0
        u.beforeChangeGroup(current, undoType)
        # Fix bug 338172: ReplaceAll will not replace newlines
        # indicated as \n in target string.
        if not self.find_text:
            return
        if not self.search_headline and not self.search_body:
            return
        self.change_text = self.replaceBackSlashes(self.change_text)
        if self.pattern_match:
            ok = self.precompilePattern()
            if not ok:
                return
        # #1428: Honor limiters in replace-all.
        if self.node_only:
            positions = [c.p]
        elif self.suboutline_only:
            positions = c.p.self_and_subtree()
        else:
            positions = c.all_unique_positions()
        count = 0
        for p in positions:
            count_h, count_b = 0, 0
            undoData = u.beforeChangeNodeContents(p)
            if self.search_headline:
                count_h, new_h = self.batchSearchAndReplace(p.h)
                if count_h:
                    count += count_h
                    p.h = new_h
            if self.search_body:
                count_b, new_b = self.batchSearchAndReplace(p.b)
                if count_b:
                    count += count_b
                    p.b = new_b
            if count_h or count_b:
                u.afterChangeNodeContents(p, 'Replace All', undoData)
        p = c.p
        u.afterChangeGroup(p, undoType, reportFlag=True)
        t2 = time.process_time()
        g.es_print(f"changed {count} instances{g.plural(count)} in {t2 - t1:4.2f} sec.")
        c.recolor()
        c.redraw(p)
        self.restore(saveData)
    #@+node:ekr.20190602134414.1: *5* find.batchSearchAndReplace & helpers
    def batchSearchAndReplace(self, s):
        """
        Search s for self.find_text and replace with self.change_text.
        
        Return (found, new text)
        """
        if sys.platform.lower().startswith('win'):
            s = s.replace('\r', '')
                # Ignore '\r' characters, which may appear in @edit nodes.
                # Fixes this bug: https://groups.google.com/forum/#!topic/leo-editor/yR8eL5cZpi4
                # This hack would be dangerous on MacOs: it uses '\r' instead of '\n' (!)
        if not s:
            return False, None
        #
        # Order matters: regex matches ignore whole-word.
        if self.pattern_match:
            return self.batchRegexReplace(s)
        if self.whole_word:
            return self.batchWordReplace(s)
        return self.batchPlainReplace(s)
    #@+node:ekr.20190602151043.4: *6* find.batchPlainReplace
    def batchPlainReplace(self, s):
        """
        Perform all plain find/replace on s.\
        return (count, new_s)
        """
        find, change = self.find_text, self.change_text
        # #1166: s0 and find0 aren't affected by ignore-case.
        s0 = s
        find0 = self.replaceBackSlashes(find)
        if self.ignore_case:
            s = s0.lower()
            find = find0.lower()
        count, prev_i, result = 0, 0, []
        while True:
            # #1166: Scan using s and find.
            i = s.find(find, prev_i)
            if i == -1:
                break
            # #1166: Replace using s0 & change.
            count += 1
            result.append(s0[prev_i:i])
            result.append(change)
            prev_i = i + len(find)
        # #1166: Complete the result using s0.
        result.append(s0[prev_i:])
        return count, ''.join(result)
    #@+node:ekr.20190602151043.2: *6* find.batchRegexReplace
    def batchRegexReplace(self, s):
        """
        Perform all regex find/replace on s.
        return (count, new_s)
        """
        count, prev_i, result = 0, 0, []

        flags = re.MULTILINE
        if self.ignore_case:
            flags |= re.IGNORECASE
        for m in re.finditer(self.find_text, s, flags):
            count += 1
            i = m.start()
            result.append(s[prev_i:i])
            # #1748.
            groups = m.groups()
            if groups:
                change_text = self.makeRegexSubs(self.change_text, groups)
            else:
                change_text = self.change_text
            result.append(change_text)
            prev_i = m.end()
        # Compute the result.
        result.append(s[prev_i:])
        s = ''.join(result)
        return count, s
    #@+node:ekr.20190602155933.1: *6* find.batchWordReplace
    def batchWordReplace(self, s):
        """
        Perform all whole word find/replace on s.
        return (count, new_s)
        """
        find, change = self.find_text, self.change_text
        # #1166: s0 and find0 aren't affected by ignore-case.
        s0 = s
        find0 = self.replaceBackSlashes(find)
        if self.ignore_case:
            s = s0.lower()
            find = find0.lower()
        count, prev_i, result = 0, 0, []
        while True:
            # #1166: Scan using s and find.
            i = s.find(find, prev_i)
            if i == -1:
                break
            # #1166: Replace using s0, change & find0.
            result.append(s0[prev_i:i])
            if g.match_word(s, i, find):
                count += 1
                result.append(change)
            else:
                result.append(find0)
            prev_i = i + len(find)
        # #1166: Complete the result using s0.
        result.append(s0[prev_i:])
        return count, ''.join(result)
    #@+node:ekr.20031218072017.3070: *4* find.changeSelection & helper
    # Replace selection with self.change_text.
    # If no selection, insert self.change_text at the cursor.

    def changeSelection(self):
        c = self.c
        p = self.p or c.p  # 2015/06/22
        wrapper = c.frame.body and c.frame.body.wrapper
        w = c.edit_widget(p) if self.in_headline else wrapper
        if not w:
            self.in_headline = False
            w = wrapper
        if not w: return False
        oldSel = sel = w.getSelectionRange()
        start, end = sel
        if start > end: start, end = end, start
        if start == end:
            g.es("no text selected"); return False
        # Replace the selection in _both_ controls.
        start, end = oldSel
        change_text = self.change_text
        # Perform regex substitutions of \1, \2, ...\9 in the change text.
        if self.pattern_match and self.match_obj:
            groups = self.match_obj.groups()
            if groups:
                change_text = self.makeRegexSubs(change_text, groups)
        # change_text = change_text.replace('\\n','\n').replace('\\t','\t')
        change_text = self.replaceBackSlashes(change_text)
        for w2 in (w, self.s_ctrl):
            if start != end: w2.delete(start, end)
            w2.insert(start, change_text)
            w2.setInsertPoint(start if self.reverse else start + len(change_text))
        # Update the selection for the next match.
        w.setSelectionRange(start, start + len(change_text))
        c.widgetWantsFocus(w)
        # No redraws here: they would destroy the headline selection.
        if self.mark_changes:
            p.setMarked()
            p.setDirty()
        if self.in_headline:
            pass
        else:
            c.frame.body.onBodyChanged('Change', oldSel=oldSel)
        c.frame.tree.updateIcon(p)  # redraw only the icon.
        return True
    #@+node:ekr.20060526201951: *5* makeRegexSubs
    def makeRegexSubs(self, change_text, groups):
        """
        Substitute group[i-1] for \\i strings in change_text.
        """

        def repl(match_object):
            # # 1494...
            n = int(match_object.group(1)) - 1
            if 0 <= n < len(groups):
                return (
                    groups[n].
                        replace(r'\b', r'\\b').
                        replace(r'\f', r'\\f').
                        replace(r'\n', r'\\n').
                        replace(r'\r', r'\\r').
                        replace(r'\t', r'\\t').
                        replace(r'\v', r'\\v'))
            # No replacement.
            return match_object.group(0)

        result = re.sub(r'\\([0-9])', repl, change_text)
        # print(
            # f"makeRegexSubs:\n"
            # f"change_text: {change_text!s}\n"
            # f"     groups: {groups!s}\n"
            # f"     result: {result!s}")
        return result
    #@+node:ekr.20031218072017.3071: *4* find.changeThenFind
    def changeThenFind(self):
        if not self.checkArgs():
            return
        self.initInHeadline()
        if self.changeSelection():
            self.findNext(False)  # don't reinitialize
    #@+node:ekr.20160920114454.1: *4* find.cloneFindTag & helpers
    def cloneFindTag(self, tag):
        """Handle the clone-find-tag command."""
        c, u = self.c, self.c.undoer
        tc = c.theTagController
        if not tc:
            g.es_print('nodetags not active')
            return 0
        clones = tc.get_tagged_nodes(tag)
        if clones:
            undoType = 'Clone Find Tag'
            undoData = u.beforeInsertNode(c.p)
            found = self.createCloneTagNodes(clones)
            u.afterInsertNode(found, undoType, undoData)
            assert c.positionExists(found, trace=True), found
            c.setChanged()
            c.selectPosition(found)
            c.redraw()
        else:
            g.es_print(f"tag not found: {self.find_text}")
        return len(clones)
    #@+node:ekr.20160920112617.2: *5* find.createCloneTagNodes
    def createCloneTagNodes(self, clones):
        """
        Create a "Found Tag" node as the last node of the outline.
        Clone all positions in the clones set as children of found.
        """
        c, p = self.c, self.c.p
        # Create the found node.
        assert c.positionExists(c.lastTopLevel()), c.lastTopLevel()
        found = c.lastTopLevel().insertAfter()
        assert found
        assert c.positionExists(found), found
        found.h = f"Found Tag: {self.find_text}"
        # Clone nodes as children of the found node.
        for p in clones:
            # Create the clone directly as a child of found.
            p2 = p.copy()
            n = found.numberOfChildren()
            p2._linkCopiedAsNthChild(found, n)
        return found
    #@+node:ekr.20031218072017.3073: *4* find.findAll & helpers
    def findAll(self, clone_find_all=False, clone_find_all_flattened=False):

        c, flatten = self.c, clone_find_all_flattened
        clone_find = clone_find_all or flatten
        if flatten:
            undoType = 'Clone Find All Flattened'
        elif clone_find_all:
            undoType = 'Clone Find All'
        else:
            undoType = 'Find All'
        if not self.checkArgs():
            return 0
        self.initInHeadline()
        data = self.save()
        self.initBatchCommands()
            # Sets self.p and self.onlyPosition.
        # Init suboutline-only for clone-find-all commands
        # Much simpler: does not set self.p or any other state.
        if self.pattern_match or self.findAllUniqueFlag:
            ok = self.precompilePattern()
            if not ok: return 0
        if self.suboutline_only:
            p = c.p
            after = p.nodeAfterTree()
        else:
            # Always search the entire outline.
            p = c.rootPosition()
            after = None
        # Fix #292: Never collapse nodes during find-all commands.
        old_sparse_find = c.sparse_find
        try:
            c.sparse_find = False
            if clone_find:
                count = self.doCloneFindAll(after, data, flatten, p, undoType)
            else:
                self.p = p
                count = self.doFindAll(after, data, p, undoType)
            # c.contractAllHeadlines()
        finally:
            c.sparse_find = old_sparse_find
        if count:
            c.redraw()
        g.es("found", count, "matches for", self.find_text)
        return count
    #@+node:ekr.20160422072841.1: *5* find.doCloneFindAll & helpers
    def doCloneFindAll(self, after, data, flatten, p, undoType):
        """Handle the clone-find-all command, from p to after."""
        c, u = self.c, self.c.undoer
        count, found = 0, None
        # 535: positions are not hashable, but vnodes are.
        clones, skip = [], set()
        while p and p != after:
            progress = p.copy()
            if p.v in skip:
                p.moveToThreadNext()
            else:
                count = self.doCloneFindAllHelper(clones, count, flatten, p, skip)
            assert p != progress
        if clones:
            undoData = u.beforeInsertNode(c.p)
            found = self.createCloneFindAllNodes(clones, flatten)
            u.afterInsertNode(found, undoType, undoData)
            assert c.positionExists(found, trace=True), found
            c.setChanged()
            c.selectPosition(found)
        else:
            self.restore(data)
        return count
    #@+node:ekr.20141023110422.1: *6* find.createCloneFindAllNodes
    def createCloneFindAllNodes(self, clones, flattened):
        """
        Create a "Found" node as the last node of the outline.
        Clone all positions in the clones set a children of found.
        """
        c = self.c
        # Create the found node.
        assert c.positionExists(c.lastTopLevel()), c.lastTopLevel()
        found = c.lastTopLevel().insertAfter()
        assert found
        assert c.positionExists(found), found
        found.h = f"Found:{self.find_text}"
        status = self.getFindResultStatus(find_all=True)
        status = status.strip().lstrip('(').rstrip(')').strip()
        flat = 'flattened, ' if flattened else ''
        found.b = f"@nosearch\n\n# {flat}{status}\n\n# found {len(clones)} nodes"
        # Clone nodes as children of the found node.
        for p in clones:
            # Create the clone directly as a child of found.
            p2 = p.copy()
            n = found.numberOfChildren()
            p2._linkCopiedAsNthChild(found, n)
        # Sort the clones in place, without undo.
        found.v.children.sort(key=lambda v: v.h.lower())
        return found
    #@+node:ekr.20160422071747.1: *6* find.doCloneFindAllHelper
    def doCloneFindAllHelper(self, clones, count, flatten, p, skip):
        """Handle the cff or cfa at node p."""
        if g.inAtNosearch(p):
            p.moveToNodeAfterTree()
            return count
        found = self.findNextBatchMatch(p)
        if found:
            if not p in clones:
                clones.append(p.copy())
            count += 1
        if flatten:
            skip.add(p.v)
            p.moveToThreadNext()
        elif found:
            # Don't look at the node or it's descendants.
            for p2 in p.self_and_subtree(copy=False):
                skip.add(p2.v)
            p.moveToNodeAfterTree()
        else:
            p.moveToThreadNext()
        return count
    #@+node:ekr.20160422073500.1: *5* find.doFindAll & helpers
    def doFindAll(self, after, data, p, undoType):
        """Handle the find-all command from p to after."""
        c, u, w = self.c, self.c.undoer, self.s_ctrl
        both = self.search_body and self.search_headline
        count, found, result = 0, None, []
        while 1:
            pos, newpos = self.findNextMatch()
            if not self.p: self.p = c.p
            if pos is None: break
            count += 1
            s = w.getAllText()
            i, j = g.getLine(s, pos)
            line = s[i:j]
            if self.findAllUniqueFlag:
                m = self.match_obj
                if m:
                    self.unique_matches.add(m.group(0).strip())
            elif both:
                result.append('%s%s\n%s%s\n' % (
                    '-' * 20, self.p.h,
                    "head: " if self.in_headline else "body: ",
                    line.rstrip() + '\n'))
            elif self.p.isVisited():
                result.append(line.rstrip() + '\n')
            else:
                result.append('%s%s\n%s' % ('-' * 20, self.p.h, line.rstrip() + '\n'))
                self.p.setVisited()
        if result or self.unique_matches:
            undoData = u.beforeInsertNode(c.p)
            if self.findAllUniqueFlag:
                found = self.createFindUniqueNode()
                count = len(list(self.unique_matches))
            else:
                found = self.createFindAllNode(result)
            u.afterInsertNode(found, undoType, undoData)
            c.selectPosition(found)
            c.setChanged()
        else:
            self.restore(data)
        return count
    #@+node:ekr.20150717105329.1: *6* find.createFindAllNode
    def createFindAllNode(self, result):
        """Create a "Found All" node as the last node of the outline."""
        c = self.c
        found = c.lastTopLevel().insertAfter()
        assert found
        found.h = f"Found All:{self.find_text}"
        status = self.getFindResultStatus(find_all=True)
        status = status.strip().lstrip('(').rstrip(')').strip()
        found.b = f"# {status}\n{''.join(result)}"
        return found
    #@+node:ekr.20171226143621.1: *6* find.createFindUniqueNode
    def createFindUniqueNode(self):
        """Create a "Found Unique" node as the last node of the outline."""
        c = self.c
        found = c.lastTopLevel().insertAfter()
        assert found
        found.h = f"Found Unique Regex:{self.find_text}"
        # status = self.getFindResultStatus(find_all=True)
        # status = status.strip().lstrip('(').rstrip(')').strip()
        # found.b = '# %s\n%s' % (status, ''.join(result))
        result = sorted(self.unique_matches)
        found.b = '\n'.join(result)
        return found
    #@+node:ekr.20160224141710.1: *6* find.findNextBatchMatch
    def findNextBatchMatch(self, p):
        """Find the next batch match at p."""
        table = []
        if self.search_headline:
            table.append(p.h)
        if self.search_body:
            table.append(p.b)
        for s in table:
            self.reverse = False
            pos, newpos = self.searchHelper(s, 0, len(s), self.find_text)
            if pos != -1: return True
        return False
    #@+node:ekr.20031218072017.3074: *4* find.findNext & helper
    def findNext(self, initFlag=True):
        """Find the next instance of the pattern."""
        if not self.checkArgs():
            return False  # for vim-mode find commands.
        # initFlag is False for change-then-find.
        if initFlag:
            self.initInHeadline()
            data = self.save()
            self.initInteractiveCommands()
        else:
            data = self.save()
        pos, newpos = self.findNextMatch()
        if pos is None:
            self.restore(data)
            self.showStatus(False)
            return False  # for vim-mode find commands.
        self.showSuccess(pos, newpos)
        self.showStatus(True)
        return True  # for vim-mode find commands.
    #@+node:ekr.20150622095118.1: *5* find.getFindResultStatus
    def getFindResultStatus(self, find_all=False):
        """Return the status to be shown in the status line after a find command completes."""
        status = []
        if self.whole_word:
            status.append('word' if find_all else 'word-only')
        if self.ignore_case:
            status.append('ignore-case')
        if self.pattern_match:
            status.append('regex')
        if find_all:
            if self.search_headline:
                status.append('head')
            if self.search_body:
                status.append('body')
        else:
            if not self.search_headline:
                status.append('body-only')
            elif not self.search_body:
                status.append('headline-only')
        if not find_all:
            if self.wrapping:
                status.append('wrapping')
            if self.suboutline_only:
                status.append('[outline-only]')
            elif self.node_only:
                status.append('[node-only]')
        return f" ({', '.join(status)})" if status else ''
    #@+node:ekr.20031218072017.3075: *4* find.findNextMatch & helpers
    def findNextMatch(self):
        """Resume the search where it left off."""
        c, p = self.c, self.p
        if not self.search_headline and not self.search_body:
            return None, None
        if not self.find_text:
            return None, None
        self.errors = 0
        attempts = 0
        if self.pattern_match or self.findAllUniqueFlag:
            ok = self.precompilePattern()
            if not ok: return None, None
        while p:
            pos, newpos = self.search()
            if self.errors:
                g.trace('find errors')
                break  # Abort the search.
            if pos is not None:
                # Success.
                if self.mark_finds:
                    p.setMarked()
                    p.setDirty()
                    if not self.changeAllFlag:
                        c.frame.tree.updateIcon(p)  # redraw only the icon.
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
                if p:  # Found another node: select the proper pane.
                    self.in_headline = self.firstSearchPane()
                    self.initNextText()
        return None, None
    #@+node:ekr.20131123071505.16468: *5* find.doWrap
    def doWrap(self):
        """Return the position resulting from a wrap."""
        c = self.c
        if self.reverse:
            p = c.rootPosition()
            while p and p.hasNext():
                p = p.next()
            p = p.lastNode()
            return p
        return c.rootPosition()
    #@+node:ekr.20131124060912.16473: *5* find.firstSearchPane
    def firstSearchPane(self):
        """
        Set return the value of self.in_headline
        indicating which pane to search first.
        """
        if self.search_headline and self.search_body:
            # Fix bug 1228458: Inconsistency between Find-forward and Find-backward.
            if self.reverse:
                return False  # Search the body pane first.
            return True  # Search the headline pane first.
        if self.search_headline or self.search_body:
            # Search the only enabled pane.
            return self.search_headline
        g.trace('can not happen: no search enabled')
        return False  # search the body.
    #@+node:ekr.20131123132043.16477: *5* find.initNextText
    def initNextText(self, ins=None):
        """
        Init s_ctrl when a search fails. On entry:
        - self.in_headline indicates what text to use.
        - self.reverse indicates how to set the insertion point.
        """
        c = self.c
        p = self.p or c.p
        s = p.h if self.in_headline else p.b
        w = self.s_ctrl
        tree = c.frame and c.frame.tree
        if tree and hasattr(tree, 'killEditing'):
            tree.killEditing()
        if self.reverse:
            i, j = w.sel
            if ins is None:
                if i is not None and j is not None and i != j:
                    ins = min(i, j)
        elif ins is None:
            ins = 0
        self.init_s_ctrl(s, ins)
    #@+node:ekr.20131123132043.16476: *5* find.nextNodeAfterFail & helper
    def nextNodeAfterFail(self, p):
        """Return the next node after a failed search or None."""
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
            return None
        if not p and wrap:
            p = self.doWrap()
        if not p:
            return None
        if wrap and p == self.wrapPosition:
            return None
        return p
    #@+node:ekr.20131123071505.16465: *6* find.outsideSearchRange
    def outsideSearchRange(self, p):
        """
        Return True if the search is about to go outside its range, assuming
        both the headline and body text of the present node have been searched.
        """
        c = self.c
        if not p:
            return True
        if self.node_only:
            return True
        if self.suboutline_only:
            if self.onlyPosition:
                if p != self.onlyPosition and not self.onlyPosition.isAncestorOf(p):
                    return True
            else:
                g.trace('Can not happen: onlyPosition!', p.h)
                return True
        if c.hoistStack:
            bunch = c.hoistStack[-1]
            if not bunch.p.isAncestorOf(p):
                g.trace('outside hoist', p.h)
                g.warning('found match outside of hoisted outline')
                return True
        return False  # Within range.
    #@+node:ekr.20131123071505.16467: *5* find.precompilePattern
    def precompilePattern(self):
        """Precompile the regexp pattern if necessary."""
        try:  # Precompile the regexp.
            # pylint: disable=no-member
            flags = re.MULTILINE
            if self.ignore_case: flags |= re.IGNORECASE
            # Escape the search text.
            # Ignore the whole_word option.
            s = self.find_text
            # A bad idea: insert \b automatically.
                # b, s = '\\b', self.find_text
                # if self.whole_word:
                    # if not s.startswith(b): s = b + s
                    # if not s.endswith(b): s = s + b
            self.re_obj = re.compile(s, flags)
            return True
        except Exception:
            g.warning('invalid regular expression:', self.find_text)
            self.errors += 1  # Abort the search.
            return False
    #@+node:ekr.20131124060912.16472: *5* find.shouldStayInNode
    def shouldStayInNode(self, p):
        """Return True if the find should simply switch panes."""
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
    def resetWrap(self, event=None):
        self.wrapPosition = None
        self.onlyPosition = None
    #@+node:ekr.20031218072017.3077: *4* find.search & helpers
    def search(self):
        """
        Search s_ctrl for self.find_text with present options.
        Returns (pos, newpos) or (None,None).
        """
        c = self.c
        p = self.p or c.p
        if (self.ignore_dups or self.find_def_data) and p.v in self.find_seen:
            # Don't find defs/vars multiple times.
            return None, None
        w = self.s_ctrl
        index = w.getInsertPoint()
        s = w.getAllText()
        if sys.platform.lower().startswith('win'):
            s = s.replace('\r', '')
                # Ignore '\r' characters, which may appear in @edit nodes.
                # Fixes this bug: https://groups.google.com/forum/#!topic/leo-editor/yR8eL5cZpi4
                # This hack would be dangerous on MacOs: it uses '\r' instead of '\n' (!)
        if not s:
            return None, None
        stopindex = 0 if self.reverse else len(s)
        pos, newpos = self.searchHelper(s, index, stopindex, self.find_text)
        if self.in_headline and not self.search_headline:
            return None, None
        if not self.in_headline and not self.search_body:
            return None, None
        if pos == -1:
            return None, None
        if self.passedWrapPoint(p, pos, newpos):
            self.wrapPosition = None  # Reset.
            return None, None
        if 0:
            # This doesn't work because index is always zero.
            # Make *sure* we move past the headline.
            g.trace(
                f"CHECK: index: {index!r} in_head: {self.in_headline} "
                f"search_head: {self.search_headline}")
            if (
                self.in_headline and self.search_headline and
                index is not None and index in (pos, newpos)
            ):
                return None, None
        ins = min(pos, newpos) if self.reverse else max(pos, newpos)
        w.setSelectionRange(pos, newpos, insert=ins)
        if (self.ignore_dups or self.find_def_data):
            self.find_seen.add(p.v)
        return pos, newpos
    #@+node:ekr.20060526140328: *5* find.passedWrapPoint
    def passedWrapPoint(self, p, pos, newpos):
        """Return True if the search has gone beyond the wrap point."""
        return (
            self.wrapping and
            self.wrapPosition is not None and
            p == self.wrapPosition and
                (self.reverse and pos < self.wrapPos or
                not self.reverse and newpos > self.wrapPos)
        )
    #@+node:ekr.20060526081931: *5* find.searchHelper & allies
    def searchHelper(self, s, i, j, pattern):
        """Dispatch the proper search method based on settings."""
        backwards = self.reverse
        nocase = self.ignore_case
        regexp = self.pattern_match or self.findAllUniqueFlag
        word = self.whole_word
        if backwards: i, j = j, i
        if not s[i:j] or not pattern:
            return -1, -1
        if regexp:
            pos, newpos = self.regexHelper(s, i, j, pattern, backwards, nocase)
        elif backwards:
            pos, newpos = self.backwardsHelper(s, i, j, pattern, nocase, word)
        else:
            pos, newpos = self.plainHelper(s, i, j, pattern, nocase, word)
        return pos, newpos
    #@+node:ekr.20060526092203: *6* find.regexHelper
    def regexHelper(self, s, i, j, pattern, backwards, nocase):

        re_obj = self.re_obj  # Use the pre-compiled object
        if not re_obj:
            g.trace('can not happen: no re_obj')
            return -1, -1
        if backwards:
            # Scan to the last match using search here.
            last_mo = None; i = 0
            while i < len(s):
                mo = re_obj.search(s, i, j)
                if not mo: break
                i += 1
                last_mo = mo
            mo = last_mo
        else:
            mo = re_obj.search(s, i, j)
        while mo and 0 <= i <= len(s):
            # Bug fix: 2013/12/27: must be 0 <= i <= len(s)
            if mo.start() == mo.end():
                if backwards:
                    # Search backward using match instead of search.
                    i -= 1
                    while 0 <= i < len(s):
                        mo = re_obj.match(s, i, j)
                        if mo: break
                        i -= 1
                else:
                    i += 1; mo = re_obj.search(s, i, j)
            else:
                self.match_obj = mo
                return mo.start(), mo.end()
        self.match_obj = None
        return -1, -1
    #@+node:ekr.20060526140744: *6* find.backwardsHelper
    debugIndices = []

    def backwardsHelper(self, s, i, j, pattern, nocase, word):
        """
        rfind(sub [,start [,end]])

        Return the highest index in the string where substring sub is found,
        such that sub is contained within s[start,end].
        
        Optional arguments start and end are interpreted as in slice notation.

        Return (-1, -1) on failure.
        """
        if nocase:
            s = s.lower()
            pattern = pattern.lower()
        pattern = self.replaceBackSlashes(pattern)
        n = len(pattern)
        # Put the indices in range.  Indices can get out of range
        # because the search code strips '\r' characters when searching @edit nodes.
        i = max(0, i)
        j = min(len(s), j)
        # short circuit the search: helps debugging.
        if s.find(pattern) == -1:
            return -1, -1
        if word:
            while 1:
                k = s.rfind(pattern, i, j)
                if k == -1: return -1, -1
                if self.matchWord(s, k, pattern):
                    return k, k + n
                j = max(0, k - 1)
        else:
            k = s.rfind(pattern, i, j)
            if k == -1:
                return -1, -1
            return k, k + n
        # For pylint:
        return -1, -1
    #@+node:ekr.20060526093531: *6* find.plainHelper
    def plainHelper(self, s, i, j, pattern, nocase, word):
        """Do a plain search."""
        if nocase:
            s = s.lower(); pattern = pattern.lower()
        pattern = self.replaceBackSlashes(pattern)
        n = len(pattern)
        if word:
            while 1:
                k = s.find(pattern, i, j)
                if k == -1:
                    return -1, -1
                if self.matchWord(s, k, pattern):
                    return k, k + n
                i = k + n
        else:
            k = s.find(pattern, i, j)
            if k == -1:
                return -1, -1
            return k, k + n
        # For pylint
        return -1, -1
    #@+node:ekr.20060526140744.1: *6* find.matchWord
    def matchWord(self, s, i, pattern):
        """Do a whole-word search."""
        pattern = self.replaceBackSlashes(pattern)
        if not s or not pattern or not g.match(s, i, pattern):
            return False
        pat1, pat2 = pattern[0], pattern[-1]
        n = len(pattern)
        ch1 = s[i - 1] if 0 <= i - 1 < len(s) else '.'
        ch2 = s[i + n] if 0 <= i + n < len(s) else '.'
        isWordPat1 = g.isWordChar(pat1)
        isWordPat2 = g.isWordChar(pat2)
        isWordCh1 = g.isWordChar(ch1)
        isWordCh2 = g.isWordChar(ch2)
        inWord = isWordPat1 and isWordCh1 or isWordPat2 and isWordCh2
        return not inWord
    #@+node:ekr.20070105165924: *6* find.replaceBackSlashes
    def replaceBackSlashes(self, s):
        """Carefully replace backslashes in a search pattern."""
        # This is NOT the same as:
        # s.replace('\\n','\n').replace('\\t','\t').replace('\\\\','\\')
        # because there is no rescanning.
        i = 0
        while i + 1 < len(s):
            if s[i] == '\\':
                ch = s[i + 1]
                if ch == '\\':
                    s = s[:i] + s[i + 1 :]  # replace \\ by \
                elif ch == 'n':
                    s = s[:i] + '\n' + s[i + 2 :]  # replace the \n by a newline
                elif ch == 't':
                    s = s[:i] + '\t' + s[i + 2 :]  # replace \t by a tab
                else:
                    i += 1  # Skip the escaped character.
            i += 1
        return s
    #@+node:ekr.20131117164142.17006: *4* find.setupArgs
    def setupArgs(self, forward=False, regexp=False, word=False):
        """
        Set up args for commands that force various values for commands
        (re-/word-/search-backward/forward)
        that force one or more of these values to be a spefic value.
        """
        if forward in (True, False): self.reverse = not forward
        if regexp in (True, False): self.pattern_match = regexp
        if word in (True, False): self.whole_word = word
        self.showFindOptions()
    #@+node:ekr.20150615174549.1: *4* find.showFindOptionsInStatusArea & helper
    def showFindOptionsInStatusArea(self):
        """Show find options in the status area."""
        c = self.c
        s = self.computeFindOptionsInStatusArea()
        c.frame.putStatusLine(s)
    #@+node:ekr.20171129211238.1: *5* find.computeFindOptionsInStatusArea
    def computeFindOptionsInStatusArea(self):
        c = self.c
        ftm = c.findCommands.ftm
        table = (
            ('Word', ftm.check_box_whole_word),
            ('Ig-case', ftm.check_box_ignore_case),
            ('regeXp', ftm.check_box_regexp),
            ('Body', ftm.check_box_search_body),
            ('Head', ftm.check_box_search_headline),
            ('wrap-Around', ftm.check_box_wrap_around),
            ('mark-Changes', ftm.check_box_mark_changes),
            ('mark-Finds', ftm.check_box_mark_finds),
        )
        result = [option for option, ivar in table if ivar.checkState()]
        table2 = (
            ('Suboutline', ftm.radio_button_suboutline_only),
            ('Node', ftm.radio_button_node_only),
        )
        for option, ivar in table2:
            if ivar.isChecked():
                result.append(f"[{option}]")
                break
        return f"Find: {' '.join(result)}"
    #@+node:ekr.20150619070602.1: *4* find.showStatus
    def showStatus(self, found):
        """Show the find status the Find dialog, if present, and the status line."""
        c = self.c
        status = 'found' if found else 'not found'
        options = self.getFindResultStatus()
        s = f"{status}:{options} {self.find_text}"
        # Set colors.
        found_bg = c.config.getColor('find-found-bg') or 'blue'
        not_found_bg = c.config.getColor('find-not-found-bg') or 'red'
        found_fg = c.config.getColor('find-found-fg') or 'white'
        not_found_fg = c.config.getColor('find-not-found-fg') or 'white'
        bg = found_bg if found else not_found_bg
        fg = found_fg if found else not_found_fg
        if c.config.getBool("show-find-result-in-status") is not False:
            c.frame.putStatusLine(s, bg=bg, fg=fg)
        if not found:  # Fixes: #457
            self.radioButtonsChanged = True
            self.reset_state_ivars()
    #@+node:ekr.20031218072017.3082: *3* LeoFind.Initing & finalizing
    #@+node:ekr.20031218072017.3083: *4* find.checkArgs
    def checkArgs(self):
        val = True
        if not self.search_headline and not self.search_body:
            g.es("not searching headline or body")
            val = False
        s = self.ftm.getFindText()
        if not s:
            g.es("empty find patttern")
            val = False
        return val
    #@+node:ekr.20131124171815.16629: *4* find.init_s_ctrl
    def init_s_ctrl(self, s, ins):
        """Init the contents of s_ctrl from s and ins."""
        w = self.s_ctrl
        w.setAllText(s)
        if ins is None:  # A flag telling us to search all of w.
            ins = len(s) if self.reverse else 0
        w.setInsertPoint(ins)
    #@+node:ekr.20031218072017.3084: *4* find.initBatchCommands (sets in_headline)
    def initBatchCommands(self):
        """Init for find-all and replace-all commands."""
        c = self.c
        self.errors = 0
        self.in_headline = self.search_headline  # Search headlines first.
        # Select the first node.
        if self.suboutline_only or self.node_only:
            self.p = c.p
            # #188: Find/Replace All Suboutline only same as Node only.
            self.onlyPosition = self.p.copy()
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
    def initBatchText(self, ins=None):
        """Init s_ctrl from self.p and ins at the beginning of a search."""
        c = self.c
        self.wrapping = False
            # Only interactive commands allow wrapping.
        p = self.p or c.p
        s = p.h if self.in_headline else p.b
        self.init_s_ctrl(s, ins)
    #@+node:ekr.20031218072017.3086: *4* find.initInHeadline & helper
    def initInHeadline(self):
        """
        Select the first pane to search for incremental searches and changes.
        This is called only at the start of each search.
        This must not alter the current insertion point or selection range.
        """
        #
        # Fix bug 1228458: Inconsistency between Find-forward and Find-backward.
        if self.search_headline and self.search_body:
            # We have no choice: we *must* search the present widget!
            self.in_headline = self.focusInTree()
        else:
            self.in_headline = self.search_headline
    #@+node:ekr.20131126085250.16651: *5* find.focusInTree
    def focusInTree(self):
        """
        Return True is the focus widget w is anywhere in the tree pane.

        Note: the focus may be in the find pane.
        """
        c = self.c
        ftm = self.ftm
        w = ftm.entry_focus or g.app.gui.get_focus(raw=True)
        ftm.entry_focus = None  # Only use this focus widget once!
        w_name = c.widget_name(w)
        if self.buttonFlag and self.was_in_headline in (True, False):
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
        return val
    #@+node:ekr.20031218072017.3087: *4* find.initInteractiveCommands
    def initInteractiveCommands(self):
        """
        Init an interactive command.  This is tricky!

        *Always* start in the presently selected widget, provided that
        searching is enabled for that widget. Always start at the present
        insert point for the body pane. For headlines, start at beginning or
        end of the headline text.
        """
        c = self.c
        p = self.p = c.p  # *Always* start with the present node.
        wrapper = c.frame.body and c.frame.body.wrapper
        headCtrl = c.edit_widget(p)
        # w is the real widget.  It may not exist for headlines.
        w = headCtrl if self.in_headline else wrapper
        # We only use the insert point, *never* the selection range.
        # None is a signal to self.initNextText()
        ins = w.getInsertPoint() if w else None
        self.errors = 0
        self.initNextText(ins=ins)
        if w: c.widgetWantsFocus(w)
        # Init suboutline-only:
        if self.suboutline_only and not self.onlyPosition:
            self.onlyPosition = p.copy()
        # Wrap does not apply to limited searches.
        if (self.wrap and
            not self.node_only and
            not self.suboutline_only and
            self.wrapPosition is None
        ):
            self.wrapping = True
            self.wrapPos = ins
            # Do not set self.wrapPosition here: that must be done after the first search.
    #@+node:ekr.20031218072017.3088: *4* find.printLine
    def printLine(self, line, allFlag=False):
        both = self.search_body and self.search_headline
        context = self.batch  # "batch" now indicates context
        if allFlag and both and context:
            g.es('', '-' * 20, '', self.p.h)
            theType = "head: " if self.in_headline else "body: "
            g.es('', theType + line)
        elif allFlag and context and not self.p.isVisited():
            # We only need to print the context once.
            g.es('', '-' * 20, '', self.p.h)
            g.es('', line)
            self.p.setVisited()
        else:
            g.es('', line)
    #@+node:ekr.20131126174039.16719: *4* find.reset_state_ivars
    def reset_state_ivars(self):
        """Reset ivars related to suboutline-only and wrapped searches."""
        self.onlyPosition = None
        self.wrapping = False
        self.wrapPosition = None
        self.wrapPos = None
    #@+node:ekr.20031218072017.3089: *4* find.restore (headline hack)
    def restore(self, data):
        """Restore the screen and clear state after a search fails."""
        c = self.c
        in_headline, editing, p, w, insert, start, end, junk = data
        self.was_in_headline = False  # 2015/03/25
        if 0:  # Don't do this here.
            # Reset ivars related to suboutline-only and wrapped searches.
            self.reset_state_ivars()
        c.frame.bringToFront()  # Needed on the Mac
        # Don't try to reedit headline.
        if p and c.positionExists(p):
            c.selectPosition(p)
        else:
            c.selectPosition(c.rootPosition())  # New in Leo 4.5.
        self.restoreAfterFindDef()
        # Fix bug 1258373: https://bugs.launchpad.net/leo-editor/+bug/1258373
        if in_headline:
            c.selectPosition(p)
            if False and editing:
                c.editHeadline()
            else:
                c.treeWantsFocus()
        else:
            # Looks good and provides clear indication of failure or termination.
            w.setSelectionRange(start, end, insert=insert)
            w.seeInsertPoint()
            c.widgetWantsFocus(w)
    #@+node:vitalije.20170712102153.1: *4* find.restoreAllExpansionStates
    def restoreAllExpansionStates(self, expanded, redraw=False):
        """expanded is a set of gnx of nodes that should be expanded"""

        c = self.c; gnxDict = c.fileCommands.gnxDict
        for gnx, v in gnxDict.items():
            if gnx in expanded:
                v.expand()
            else:
                v.contract()
        if redraw:
            c.redraw()
    #@+node:ekr.20031218072017.3090: *4* find.save
    def save(self):
        """Save everything needed to restore after a search fails."""
        c = self.c
        p = self.p or c.p
        # Fix bug 1258373: https://bugs.launchpad.net/leo-editor/+bug/1258373
        if self.in_headline:
            e = c.edit_widget(p)
            w = e or c.frame.tree.canvas
            insert, start, end = None, None, None
        else:
            w = c.frame.body.wrapper
            e = None
            insert = w.getInsertPoint()
            sel = w.getSelectionRange()
            if len(sel) == 2:
                start, end = sel
            else:
                start, end = None, None
        editing = e is not None
        expanded = set(
            gnx for gnx, v in c.fileCommands.gnxDict.items() if v.isExpanded())
        # TODO: this is naive solution that treat all clones the same way if one is expanded
        #       then every other clone is expanded too. A proper way would be to remember
        #       each clone separately
        return self.in_headline, editing, p.copy(), w, insert, start, end, expanded
    #@+node:ekr.20031218072017.3091: *4* find.showSuccess (headline hack)
    def showSuccess(self, pos, newpos, showState=True):
        """Display the result of a successful find operation."""
        c = self.c
        self.p = p = self.p or c.p
        # Set state vars.
        # Ensure progress in backwards searches.
        insert = min(pos, newpos) if self.reverse else max(pos, newpos)
        if self.wrap and not self.wrapPosition:
            self.wrapPosition = self.p
        if c.sparse_find:
            c.expandOnlyAncestorsOfNode(p=p)
        if self.in_headline:
            c.endEditing()
            selection = pos, newpos, insert
            c.redrawAndEdit(p,
                selection=selection,
                keepMinibuffer=True)
            w = c.edit_widget(p)
            self.was_in_headline = True  # 2015/03/25
        else:
            # Tricky code.  Do not change without careful thought.
            w = c.frame.body.wrapper
            # *Always* do the full selection logic.
            # This ensures that the body text is inited  and recolored.
            c.selectPosition(p)
            c.bodyWantsFocus()
            if showState:
                c.k.showStateAndMode(w)
            c.bodyWantsFocusNow()
            w.setSelectionRange(pos, newpos, insert=insert)
            k = g.see_more_lines(w.getAllText(), insert, 4)
            w.see(k)
                # #78: find-next match not always scrolled into view.
            c.outerUpdate()
                # Set the focus immediately.
            if c.vim_mode and c.vimCommands:
                c.vimCommands.update_selection_after_search()
        # Support for the console gui.
        if hasattr(g.app.gui, 'show_find_success'):
            g.app.gui.show_find_success(c, self.in_headline, insert, p)
        c.frame.bringToFront()
        return w  # Support for isearch.
    #@+node:ekr.20031218072017.1460: *4* find.update_ivars
    def update_ivars(self):
        """Update ivars from the find panel."""
        c = self.c
        self.p = c.p
        ftm = self.ftm
        # The caller is responsible for removing most trailing cruft.
        # Among other things, this allows Leo to search for a single trailing space.
        s = ftm.getFindText()
        s = g.checkUnicode(s)
        if s and s[-1] in ('\r', '\n'):
            s = s[:-1]
        if self.radioButtonsChanged or s != self.find_text:
            self.radioButtonsChanged = False
            self.state_on_start_of_search = self.save()
            # Reset ivars related to suboutline-only and wrapped searches.
            self.reset_state_ivars()
        self.find_text = s
        # Get replacement text.
        s = ftm.getReplaceText()
        s = g.checkUnicode(s)
        if s and s[-1] in ('\r', '\n'):
            s = s[:-1]
        self.change_text = s
    #@-others
#@+node:ekr.20200216063538.1: ** class TestFind
# Transcrypt does not support Python's unittest module.
# __pragma__ ('skip')

class TestFind(unittest.TestCase):
    """Test cases for leoFind.py"""
    #@+others
    #@+node:ekr.20200216063929.1: *3* test_regex_replace
    def test_regex_replace(self):
        # #1494.
        x = LeoFind(c=g.NullObject(tag='c'))
        groups = (r"f'", r"line\n")
        change_text = r"""\1 AA \2 BB \3'"""
        expected = r"""f' AA line\\n BB \3'"""
        result = x.makeRegexSubs(change_text, groups)
        assert result == expected, (expected, result)
    #@-others

# __pragma__ ('noskip')
#@-others

# __pragma__ ('skip')
if __name__ == '__main__':
    unittest.main()
# __pragma__ ('noskip')

#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
