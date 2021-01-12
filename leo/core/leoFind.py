#@+leo-ver=5-thin
#@+node:ekr.20060123151617: * @file leoFind.py
"""Leo's gui-independent find classes."""
import keyword
import re
import sys
import time
import unittest
from leo.core import leoGlobals as g
from leo.core import leoTest2

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

def cmd(name):
    """Command decorator for the findCommands class."""
    return g.new_cmd_decorator(name, ['c', 'findCommands',])

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
    #@+node:ekr.20031218072017.3053: *4*  find.__init__
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
        # State machine...
        self.escape_handler = None
        self.handler = None
        #
        # Ivars containing internal state...
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
    #@+node:ekr.20210110073117.6: *4* find.default_settings
    def default_settings(self):
        """Return a dict representing all default settings."""
        c = self.c
        return g.Bunch(
            # State...
            in_headline = False,
            p = c.rootPosition(),
            # Find/change strings...
            find_text = '',
            change_text = '',
            # Find options...
            ignore_case = False,
            node_only = False,
            pattern_match = False,
            reverse = False,
            search_body = True,
            search_headline = True,
            suboutline_only = False,
            whole_word = False,
            wrapping = False,
            # User options.
            use_cff = False,  # For find-def.
        )
    #@+node:ekr.20131117164142.17022: *4* find.finishCreate
    def finishCreate(self):
        # New in 4.11.1.
        # Must be called when config settings are valid.
        c = self.c
        self.reloadSettings()
        # now that configuration settings are valid,
        # we can finish creating the Find pane.
        dw = c.frame.top
        if dw: dw.finishCreateLogPane()
    #@+node:ekr.20210110145821.1: *4* find.get_settings (new)
    def get_settings(self):
        """Return all settings in a g.Bunch."""
        c = self.c
        self.initInHeadline()
        settings = self.ftm.get_settings()
        settings.in_headline = self.in_headline
        settings.p = c.p
        # settings.use_cff = False  ### user setting?
        return settings
        
    #@+node:ekr.20210110073117.4: *4* find.init (new)
    def init(self, settings):
        """Initial all ivars from settings."""
        w = self.s_ctrl
        #
        # Init find/change strings.
        self.change_text = settings.change_text
        self.find_text = settings.find_text
        #
        # Init find options.
        self.ignore_case = settings.ignore_case
        self.node_only = settings.node_only
        self.pattern_match = settings.pattern_match 
        self.reverse = settings.reverse
        self.search_body = settings.search_body
        self.search_headline = settings.search_headline
        self.suboutline_only = settings.suboutline_only
        self.whole_word = settings.whole_word
        self.wrapping = settings.wrapping
        #
        # Init user options
        self.use_cff = False  # For find-def
        #
        # Init state.
        self.in_headline = self.was_in_headline = settings.in_headline
        self.p = p = settings.p.copy()
        self.onlyPosition = self.p if self.suboutline_only else None
        self.wrapPos = 0 if self.reverse else len(p.b)
        #
        # Init the search widget.
        s = p.h if self.in_headline else p.b
        w.setAllText(s)
        w.setInsertPoint(len(s) if self.reverse else 0)
    #@+node:ekr.20210110073117.5: *5* NEW:find.init_settings
    def init_settings(self, settings):
        """Initialize all user settings."""
        
    #@+node:ekr.20171113164709.1: *4* find.reloadSettings
    def reloadSettings(self):
        """LeoFind.reloadSettings."""
        c = self.c
        self.ignore_dups = c.config.getBool('find-ignore-duplicates', default=False)
        self.minibuffer_mode = c.config.getBool('minibuffer-find-mode', default=False)
    #@+node:ekr.20031218072017.3055: *3* LeoFind.Commands (immediate execution)
    #@+node:ekr.20150629084204.1: *4* find.find-def, find-var & helpers
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
        if keyword.iskeyword(word):
            return None
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
    #@+node:ekr.20031218072017.3063: *4* find.find-next
    @cmd('find-next')
    def findNextCommand(self, event=None):
        """The find-next command."""
        self.update_ivars()
        self.findNext()
    #@+node:ekr.20031218072017.3064: *4* find.find-prev
    @cmd('find-prev')
    def findPrevCommand(self, event=None):
        """Handle F2 (find-previous)"""
        self.update_ivars()
        self.reverse = True
        try:
            self.findNext()
        finally:
            self.reverse = False
    #@+node:ekr.20141113094129.6: *4* find.focus-to-find
    @cmd('focus-to-find')
    def focusToFind(self, event=None):
        c = self.c
        if c.config.getBool('use-find-dialog', default=True):
            g.app.gui.openFindDialog(c)
        else:
            c.frame.log.selectTab('Find')
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
    #@+node:ekr.20031218072017.3068: *4* find.replace
    @cmd('replace')
    def change(self, event=None):
        if self.checkArgs():
            self.initInHeadline()
            self.change_selection()

    replace = change
    #@+node:ekr.20031218072017.3062: *4* find.replace-then-find & helper
    @cmd('replace-then-find')
    def changeThenFindCommand(self, event=None):
        """Handle the replace-then-find command."""
        if not self.checkArgs():
            return False
        self.initInHeadline()
        if self.change_selection():
            self.findNext(False)  # don't reinitialize
        return True
    #@+node:ekr.20210110073117.27: *5* NEW:do_replace_then_find
    def do_replace_then_find(self, settings):
        """
        Handle the replace-then-find command.
        
        Return (p, pos, newpos).
        """
        p = self.p
        if settings:
            self.init(settings)
        if not self.check_args('replace-then-find'):
            return None, None, None
        if self.change_selection():
            p, pos, newpos = self.find_next_match(p)
            return p, pos, newpos
        return None, None, None
    #@+node:vitalije.20170712162056.1: *4* find.returnToOrigin (search-return-to-origin)
    @cmd('search-return-to-origin')
    def returnToOrigin(self, event):
        data = self.state_on_start_of_search
        if not data: return
        self.restore(data)
        self.restoreAllExpansionStates(data[-1], redraw=True)
    #@+node:ekr.20210110073117.7: *4* NEW:LeoFind: Commands
    #@+node:ekr.20210110073117.12: *5* NEW:find.create_clone_tag_nodes
    def create_clone_tag_nodes(self, clones):
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
    #@+node:ekr.20210110073117.13: *5* NEW:do_find_all
    def do_find_all(self, settings):
        """find-all"""
        c, p, u, w = self.c, self.p, self.c.undoer, self.s_ctrl
        if settings:
            self.init(settings)
        if not self.check_args('find-all'):
            return 0
        if self.pattern_match:
            ok = self.compile_pattern()
            if not ok: return 0
        if self.suboutline_only:
            # Start with p.
            after = p.nodeAfterTree()
        else:
            # Always search the entire outline.
            p = c.rootPosition()
            after = None
        count, found, result = 0, None, []
        while p != after:
            # We can't assert progress on p, because
            # there can be multiple matches in one p.
            p, pos, newpos = self.find_next_match(p)
            if p is None or pos is None:
                 break
            count += 1
            s = w.getAllText()
            i, j = g.getLine(s, pos)
            line = s[i:j]
            if self.search_body and self.search_headline:
                kind = "head" if self.in_headline else "body"
                result.append(
                    f"{'-' * 20} {p.h}\n"
                    f"{kind}: {line.rstrip()}\n\n")
            elif p.isVisited():
                result.append(line.rstrip() + '\n')
            else:
                result.append(
                    f"{'-' * 20} {p.h}\n"
                    f"{line.rstrip()}\n\n")
                p.setVisited()
        if result:
            undoData = u.beforeInsertNode(c.p)
            found = self.create_find_all_node(result)
            u.afterInsertNode(found, 'Find All', undoData)
            c.selectPosition(found)
            c.setChanged()
        g.es("found", count, "matches for", self.find_text)
        return count
    #@+node:ekr.20210110073117.14: *5* NEW:find-def, find-var
    ### @cmd('find-def')
    def find_def(self, settings=None):
        """Find the def or class under the cursor."""
        return self.find_def_helper(defFlag=True, settings=settings)

    ### @cmd('find-var')
    def find_var(self, settings=None):
        """Find the var under the cursor."""
        return self.find_def_helper(defFlag=False, settings=settings)
    #@+node:ekr.20210110073117.15: *6* NEW:find.find_def_helper & helpers
    def find_def_helper(self, defFlag, settings):
        """Find the definition of the class, def or var under the cursor."""
        c = self.c
        tag = 'find-def' if defFlag else 'find-var'
        if settings:
            self.init(settings)
        if not self.check_args(tag):
            return None, None, None
        # Always start in the root position.
        root = c.rootPosition()
        c.redraw(root)  # Required.
        c.bodyWantsFocusNow()
        # Set up the search.
        if defFlag:
            prefix = 'class' if self.find_text[0].isupper() else 'def'
            self.find_text = prefix + ' ' + self.find_text
        else:
            self.find_text = self.find_text + ' ='
        # Save previous settings.
        self.saveBeforeFindDef(root)
        self.setFindDefOptions(root)
        count, found = 0, False
        self.find_seen = set()
        if settings.use_cff:
            count = self.do_clone_find_all_flattened(settings)
            found = count > 0
        else:
            # #1592.  Ignore hits under control of @nosearch
            p = root
            while p:
                progress = p.v
                p, pos, newpos = self.find_next_match(p)
                found = pos is not None
                if found and not g.inAtNosearch(p):
                    break
                assert not p or p.v != progress, p.h  
        if not found and defFlag and not self.find_text.startswith('class'):
            # Leo 5.7.3: Look for an alternative defintion of function/methods.
            word2 = self.switch_style(self.find_text)
            if word2:
                self.find_text = prefix + ' ' + word2
                if settings.use_cff:
                    count = self.do_clone_find_all(settings)
                    found = count > 0
                else:
                    # #1592.  Ignore hits under control of @nosearch
                    p = root  # bug fix!
                    while p:
                        progress = p.v
                        p, pos, newpos = self.find_next_match(p)
                        found = pos is not None
                        if found and not g.inAtNosearch(p):
                            break  # pragma: no cover (minor)
                        assert not p or p.v != progress, p.h
        if not found:
            return None, None, None
        if settings.use_cff:
            last = c.lastTopLevel()
            if count == 1:
                # It's annoying to create a clone in this case.
                # Undo the clone find and just select the proper node.
                last.doDelete()
                self.find_next_match(root)
            else:  # pragma: no cover (to do)
                c.selectPosition(last)
            return None, None, last
        self.restoreAfterFindDef()
            # Failing to do this causes massive confusion!
        return p, pos, newpos
        
    #@+node:ekr.20210110073117.18: *7* NEW:find.switch_style
    def switch_style(self, word):
        """
        Switch between camelCase and underscore_style function defintiions.
        Return None if there would be no change.
        """
        s = word
        if not s:
            return None
        # Don't return something that looks like a class. Changed!
        if s[0].isupper():
            return None
        if s.find('_') > -1:
            # Convert to CamelCase
            s = s.lower()
            while s:
                i = s.find('_')
                if i == -1:
                    break
                s = s[:i] + s[i + 1 :].capitalize()
            return s
        # Convert to underscore_style.
        result = []
        for i, ch in enumerate(s):
            if i > 0 and ch.isupper():
                result.append('_')
            result.append(ch.lower())
        s = ''.join(result)
        return None if s == word else s
    #@+node:ekr.20210110073117.20: *5* NEW:find-next
    ### @cmd('find-next')
    def find_next(self, settings):
        """The find-next command."""
        assert settings
        self.init(settings)
        if not self.check_args('find-next'):
            return None, None, None
        p = self.p
        p, pos, newpos = self.find_next_match(p)
        return p, pos, newpos # For tests.
    #@+node:ekr.20210110073117.21: *5* NEW:find-prev
    ### @cmd('find-prev')
    def find_prev(self, settings):
        """The find-prev command."""
        assert settings
        self.init(settings)
        if not self.check_args('find-prev'):
            return None, None, None
        p = self.p
        self.reverse = True
        try:
            p, pos, newpos = self.find_next_match(p)
        finally:
            self.reverse = False
        return p, pos, newpos
    #@+node:ekr.20210110073117.22: *5* NEW:replace-all & helpers
    ### @cmd('replace-all')
    def replace_all(self, settings):
        """Replace all instances of the search string with the replacement string."""
        c, current, u = self.c, self.c.p, self.c.undoer
        undoType = 'Replace All'
        if settings:
            self.init(settings)
        if not self.check_args('replace-all'):
            return
        t1 = time.process_time()
        count = 0
        u.beforeChangeGroup(current, undoType)
        # Fix bug 338172: ReplaceAll will not replace newlines
        # indicated as \n in target string.
        self.change_text = self.replace_back_slashes(self.change_text)
        if self.pattern_match:
            ok = self.compile_pattern()
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
                count_h, new_h = self.replace_all_helper(p.h)
                if count_h and p.h != new_h:
                    count += count_h
                    p.v.h = new_h
                    p.v.setDirty()
            if self.search_body:
                count_b, new_b = self.replace_all_helper(p.b)
                if count_b and p.b != new_b:
                    p.v.b = new_b
                    p.v.setDirty()
            if count_h or count_b:
                u.afterChangeNodeContents(p, undoType, undoData)
        p = c.p
        u.afterChangeGroup(p, undoType, reportFlag=True)
        t2 = time.process_time()
        if not g.unitTesting:  # pragma: no cover (skip)
            g.es_print(
                f"changed {count} instance{g.plural(count)} "
                f"in {t2 - t1:4.2f} sec.")
        #
        # Bugs #947, #880 and #722:
        # Set ancestor @<file> nodes by brute force.
        for p in c.all_positions():
            if (
                p.anyAtFileNodeName()
                and not p.v.isDirty()
                and any([p2.v.isDirty() for p2 in p.subtree()])
            ):
                p.v.setDirty()
    #@+node:ekr.20210110073117.23: *6* NEW:find.replace_all_helper & helpers
    def replace_all_helper(self, s):
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
            return self.batch_regex_replace(s)
        if self.whole_word:
            return self.batch_word_replace(s)
        return self.batch_plain_replace(s)
    #@+node:ekr.20210110073117.24: *7* NEW:find.batch_plain_replace
    def batch_plain_replace(self, s):
        """
        Perform all plain find/replace on s.
        return (count, new_s)
        """
        find, change = self.find_text, self.change_text
        # #1166: s0 and find0 aren't affected by ignore-case.
        s0 = s
        find0 = self.replace_back_slashes(find)
        if self.ignore_case:
            s = s0.lower()
            find = find0.lower()
        count, prev_i, result = 0, 0, []
        while True:
            progress = prev_i
            # #1166: Scan using s and find.
            i = s.find(find, prev_i)
            if i == -1:
                break
            # #1166: Replace using s0 & change.
            count += 1
            result.append(s0[prev_i:i])
            result.append(change)
            prev_i = max(prev_i + 1, i + len(find))  # 2021/01/08 (!)
            assert prev_i > progress, prev_i
        # #1166: Complete the result using s0.
        result.append(s0[prev_i:])
        return count, ''.join(result)
    #@+node:ekr.20210110073117.25: *7* NEW:find.batch_regex_replace
    def batch_regex_replace(self, s):
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
                change_text = self.make_regex_subs(self.change_text, groups)
            else:
                change_text = self.change_text
            result.append(change_text)
            prev_i = m.end()
        # Compute the result.
        result.append(s[prev_i:])
        s = ''.join(result)
        return count, s
    #@+node:ekr.20210110073117.26: *7* NEW:find.batch_word_replace
    def batch_word_replace(self, s):
        """
        Perform all whole word find/replace on s.
        return (count, new_s)
        """
        find, change = self.find_text, self.change_text
        # #1166: s0 and find0 aren't affected by ignore-case.
        s0 = s
        find0 = self.replace_back_slashes(find)
        if self.ignore_case:
            s = s0.lower()
            find = find0.lower()
        count, prev_i, result = 0, 0, []
        while True:
            progress = prev_i
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
            prev_i = max(prev_i + 1, i + len(find))  # 2021/01/08 (!)
            assert prev_i > progress, prev_i
        # #1166: Complete the result using s0.
        result.append(s0[prev_i:])
        return count, ''.join(result)
    #@+node:ekr.20210110073117.29: *5* NEW:tag-children
    ### @cmd('tag-children') 
    def tag_children(self, p, tag):
        """tag-children: Add the given tag to all children of c.p."""
        c = self.c
        tc = c.theTagController
        if not tc:
            if not g.unitTesting:  # pragma: no cover (skip)
                g.es_print('nodetags not active')
            return
        for p in p.children():
            tc.add_tag(p, tag)
        if not g.unitTesting:  # pragma: no cover (skip)
            g.es_print(f"Added {tag} tag to {len(list(c.p.children()))} nodes")
    #@+node:ekr.20131117164142.17013: *3* LeoFind.Commands (interactive)
    #@+node:ekr.20210110140128.1: *4* find.clone-find-all/-flattened & helper
    #@+node:ekr.20131117164142.17011: *5* find.clone-find-all
    @cmd('clone-find-all')
    @cmd('find-clone-all')
    @cmd('cfa')
    def interactive_clone_find_all(self, event=None, preloaded=None):
        """
        clone-find-all ( aka find-clone-all and cfa).

        Create an organizer node whose descendants contain clones of all nodes
        matching the search string, except @nosearch trees.

        The list is *not* flattened: clones appear only once in the
        descendants of the organizer node.
        """
        w = self.editWidget(event)  # sets self.w
        if not w:
            return
        if not preloaded:
            self.preloadFindPattern(w)
        self.start_state_machine(event,
            prefix='Clone Find All: ',
            handler=self.interactive_clone_find_all)

    def interactive_clone_find_all1(self, event):
        c, k, w = self.c, self.k, self.w
        self.p = c.p
        # Settings...
        pattern = k.arg
        self.ftm.setFindText(pattern)
        self.init_vim_search(pattern)
        settings = self.get_settings()
        # Gui...
        k.clearState()
        k.resetLabel()
        k.showStateAndMode()
        c.widgetWantsFocusNow(w)
        count = self.do_clone_find_all(settings)
        if count:
            c.redraw()
            c.treeWantsFocus()
        return count
        
    # A stand-alone method for unit testing.
    def do_clone_find_all(self, settings):
        """
        Do the clone-all-find commands from settings.
        Return the count of found nodes.
        """
        self.init(settings)
        if self.check_args('clone-find-all'):
            return self.clone_find_all_helper(settings, flatten=False)
        return 0
    #@+node:ekr.20131117164142.16996: *5* find.clone-find-all-flattened
    @cmd('clone-find-all-flattened')
    # @cmd('find-clone-all-flattened')
    @cmd('cff')
    def interactive_cff(self, event=None, preloaded=None):
        """
        clone-find-all-flattened (aka find-clone-all-flattened and cff).

        Create an organizer node whose direct children are clones of all nodes
        matching the search string, except @nosearch trees.

        The list is flattened: every cloned node appears as a direct child
        of the organizer node, even if the clone also is a descendant of
        another cloned node.
        """
        w = self.editWidget(event)  # sets self.w
        if not w:
            return
        if not preloaded:
            self.preloadFindPattern(w)
        self.start_state_machine(event,
            prefix='Clone Find All Flattened: ',
            handler=self.interactive_cff1)

    def interactive_cff1(self, event):
        c, k, w = self.c, self.k, self.w
        k.clearState()
        k.resetLabel()
        k.showStateAndMode()
        # Was self.generalSearchHelper
        pattern = k.arg
        self.ftm.setFindText(pattern)
        self.init_vim_search(pattern)
        c.widgetWantsFocusNow(w)
        self.p = c.p
        settings = self.get_settings()
        count = self.do_clone_find_all(settings)
        if count:
            c.redraw()
            c.treeWantsFocus()
        return count
        
    # A stand-alone method for unit testing.
    def do_clone_find_all_flattened(self, settings):
        """Do the clone-find-all-flattened command from the settings."""
        self.init(settings)
        if self.check_args('clone-find-all-flattened'):
            return self.clone_find_all_helper(settings, flatten=True)
        return 0
    #@+node:ekr.20210110073117.9: *5* new: find.clone_find_all_helper & helper
    def clone_find_all_helper(self, settings, flatten):
        """
        The common part of the clone-find commands.
        
        Return the number of found nodes.
        """
        c, u = self.c, self.c.undoer
        if self.pattern_match:
            ok = self.compile_pattern()
            if not ok: return 0
        if self.suboutline_only:
            p = settings.p.copy()
            after = p.nodeAfterTree()
        else:
            p = c.rootPosition()
            after = None
        count, found = 0, None
        clones, skip = [], set()
        while p and p != after:
            progress = p.copy()
            if p.v in skip:  # pragma: no cover (minor)
                p.moveToThreadNext()
            elif g.inAtNosearch(p):
                p.moveToNodeAfterTree()
            elif self.find_next_batch_match(p):
                count += 1
                if p not in clones:
                    clones.append(p.copy())
                if flatten:
                    p.moveToThreadNext()
                else:
                    # Don't look at the node or it's descendants.
                    for p2 in p.self_and_subtree(copy=False):
                        skip.add(p2.v)
                    p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()
            assert p != progress
        if clones:
            undoData = u.beforeInsertNode(c.p)
            found = self.create_clone_find_all_nodes(clones, flattened=False)
            u.afterInsertNode(found, 'Clone Find All', undoData)
            assert c.positionExists(found, trace=True), found
            c.setChanged()
            c.selectPosition(found)
        g.es("found", count, "matches for", self.find_text)
        return count  # Might be useful for the gui update.
    #@+node:ekr.20210110073117.10: *6* new: find.find_next_batch_match
    def find_next_batch_match(self, p):
        """Find the next batch match at p."""
        table = []
        if self.search_headline:
            table.append(p.h)
        if self.search_body:
            table.append(p.b)
        for s in table:
            self.reverse = False
            pos, newpos = self.inner_search_helper(s, 0, len(s), self.find_text)
            if pos != -1:
                return True
        return False
    #@+node:ekr.20160920110324.1: *4* find.clone-find-tag & helper
    @cmd('clone-find-tag')
    @cmd('find-clone-tag')
    @cmd('cft')
    def interactive_clone_find_tag(self, event=None):
        """
        clone-find-tag (aka find-clone-tag and cft).

        Create an organizer node whose descendants contain clones of all
        nodes matching the given tag, except @nosearch trees.

        The list is *always* flattened: every cloned node appears as a
        direct child of the organizer node, even if the clone also is a
        descendant of another cloned node.
        """
        if self.editWidget(event):  # sets self.w
            self.start_state_machine(event,
                prefix='Clone Find Tag: ',
                handler=self.interactive_clone_find_tag1)

    def interactive_clone_find_tag1(self, event):
        c, k = self.c, self.k
        # Settings...
        self.find_text = tag = k.arg
        # Gui...
        k.clearState()
        k.resetLabel()
        k.showStateAndMode()
        self.do_clone_find_tag(tag)
        c.treeWantsFocus()
    #@+node:ekr.20210110073117.11: *5* NEW:do_clone_find_tag
    # A stand-alone method for unit tests.
    def do_clone_find_tag(self, tag):
        """
        Do the clone-all-find commands from settings.
        Return (len(clones), found) for unit tests.
        """
        c, u = self.c, self.c.undoer
        tc = c.theTagController
        if not tc:
            if not g.unitTesting:  # pragma: no cover (skip)
                g.es_print('nodetags not active')  
            return 0, c.p
        clones = tc.get_tagged_nodes(tag)
        if not clones:
            if not g.unitTesting: # pragma: no cover (skip)
                g.es_print(f"tag not found: {tag}") 
            tc.show_all_tags()
            return 0, c.p
        undoData = u.beforeInsertNode(c.p)
        found = self.create_clone_tag_nodes(clones)
        u.afterInsertNode(found, 'Clone Find Tag', undoData)
        assert c.positionExists(found, trace=True), found
        c.setChanged()
        c.selectPosition(found)
        c.redraw()
        return len(clones), found
    #@+node:ekr.20131117164142.16998: *4* find.find-all
    @cmd('find-all')
    def interactive_find_all(self, event=None):
        """
        Create a summary node containing descriptions of all matches of the
        search string.
        
        Typing tab converts this to the change-all command.
        """
        self.ftm.clear_focus()
        self.ftm.set_entry_focus()
        self.start_state_machine(event, 'Search: ',
            handler=self.interactive_find_all1,
            escape_handler=self.find_all_escape_handler,
        )

    def interactive_find_all1(self, event=None):
        k = self.k
        self.updateFindList(k.arg)
        k.clearState()
        k.resetLabel()
        k.showStateAndMode()
        pattern = k.arg
        self.ftm.setFindText(pattern)
        self.update_ivars()
        self.findAll()
        
    def find_all_escape_handler(self, event):
        k = self.k
        prompt = 'Replace ' + ('Regex' if self.pattern_match else 'String')
        find_pattern = k.arg
        self._sString = k.arg
        self.updateFindList(k.arg)
        s = f"{prompt}: {find_pattern} With: "
        k.setLabelBlue(s)
        self.addChangeStringToLabel()
        k.getNextArg(self.find_all_escape_handler2)

    def find_all_escape_handler2(self, event):
        c,k = self.c, self.k
        self.p = c.p
        find_pattern = self._sString
        change_pattern = k.arg
        self.updateChangeList(change_pattern)
        self.ftm.setFindText(find_pattern)
        self.ftm.setChangeText(change_pattern)
        self.init_vim_search(find_pattern)
        # Gu...
        k.clearState()
        k.resetLabel()
        k.showStateAndMode()
        c.widgetWantsFocusNow(self.w)
        self.changeAllCommand()
    #@+node:ekr.20171226140643.1: *4* find.find-all-unique-regex (test)
    @cmd('find-all-unique-regex')
    def interactive_find_all_unique_regex(self, event=None):
        """
        Create a summary node containing all unique matches of the regex search
        string. This command shows only the matched string itself.
        """
        self.ftm.clear_focus()
        self.match_obj = None
        self.unique_matches = set()
        self.changeAllFlag = False
        self.findAllFlag = True
        self.findAllUniqueFlag = True
        self.ftm.set_entry_focus()
        self.start_state_machine(event,
            prefix='Search Unique Regex: ',
            handler=self.interactive_find_all_unique_regex1,
            escape_handler = self.interactive_change_all_unique_regex1,
        )
        
    def interactive_find_all_unique_regex1(self, event=None):
        k = self.k
        find_pattern = k.arg
        k.clearState()
        k.resetLabel()
        k.showStateAndMode()
        self.updateFindList(find_pattern)
        self.ftm.setFindText(find_pattern)
        self.update_ivars()
        return self.findAll()
        
    def interactive_change_all_unique_regex1(self, event):
        k = self.k
        find_pattern = self._sString = k.arg
        self.updateFindList(k.arg)
        s = f"'Replace All Unique Regex': {find_pattern} With: "
        k.setLabelBlue(s)
        self.addChangeStringToLabel()
        k.getNextArg(self.interactive_change_all_unique_regex2)

    def interactive_change_all_unique_regex2(self, event):
        c,k = self.c, self.k
        self.p = c.p
        find_pattern = self._sString
        change_pattern = k.arg
        self.updateChangeList(change_pattern)
        self.ftm.setFindText(find_pattern)
        self.ftm.setChangeText(change_pattern)
        self.init_vim_search(find_pattern)
        # Gui...
        k.clearState()
        k.resetLabel()
        k.showStateAndMode()
        c.widgetWantsFocusNow(self.w)
        self.changeAllCommand()
    #@+node:ekr.20131117164142.17003: *4* find.re-search
    @cmd('re-search')
    @cmd('re-search-forward')
    def interactive_re_search_forward(self, event):
        """Same as start-find, with regex."""
        self.reverse = False
        self.pattern_match = True
        self.showFindOptions()
        self.start_state_machine(event,
            prefix='Regexp Search: ',
            handler=self.start_search1,  # See start-search
            escape_handler = self.start_search_escape1,  # See start-search
        )
    #@+node:ekr.20210112044303.1: *4* find.re-search-backward
    @cmd('re-search-backward')
    def interactive_re_search_backward(self, event):
        """Same as start-find, but with regex and in reverse."""
        self.reverse = True
        self.pattern_match = True
        self.showFindOptions()
        self.start_state_machine(event,
            prefix='Regexp Search Backward:',
            handler=self.start_search1,  # See start-search
            escape_handler = self.start_search_escape1,  # See start-search
        )

    #@+node:ekr.20131117164142.16994: *4* find.replace-all
    @cmd('replace-all')
    def interactive_replace_all(self, event=None):
        """Replace all instances of the search string with the replacement string."""
        self.ftm.clear_focus()
        self.ftm.set_entry_focus()
        prompt = 'Replace Regex: ' if self.pattern_match else 'Replace: '
        self.start_state_machine(event, prompt,
            handler = self.interactive_replace_all1,
            # Allow either '\t' or '\n' to switch to the change text.
            escape_handler = self.interactive_replace_all1,
        )
        
    def interactive_replace_all1(self, event):
        k = self.k
        find_pattern = k.arg
        self._sString = k.arg
        self.updateFindList(k.arg)
        regex = ' Regex' if self.pattern_match else ''
        prompt = f"Replace{regex}: {find_pattern} With: "
        k.setLabelBlue(prompt)
        self.addChangeStringToLabel()
        k.getNextArg(self.interactive_replace_all2)

    def interactive_replace_all2(self, event):
        c,k = self.c, self.k
        self.p = c.p
        # Settings...
        find_pattern = self._sString
        change_pattern = k.arg
        self.updateChangeList(change_pattern)
        self.ftm.setFindText(find_pattern)
        self.ftm.setChangeText(change_pattern)
        self.init_vim_search(find_pattern)
        # Gui...
        k.clearState()
        k.resetLabel()
        k.showStateAndMode()
        c.widgetWantsFocusNow(self.w)
        self.changeAllCommand()
    #@+node:ekr.20131117164142.17004: *4* find.search_backward
    @cmd('search-backward')
    def interactive_search_backward(self, event):
        """Same as start-find, but in reverse."""
        self.reverse = True
        self.start_state_machine(event,
            prefix='Search Backward: ',
            handler=self.start_search1,  # See start-search
            escape_handler = self.start_search_escape1,  # See start-search
        )
    #@+node:ekr.20131119060731.22452: *4* find.start-search (Ctrl-F)
    @cmd('start-search')
    @cmd('search-forward')  # Compatibility.
    def start_search(self, event):
        """
        The default binding of Ctrl-F.
        
        Also contains default state-machine entries for find/change commands.
        """
        w = self.editWidget(event)
        if w:
            self.preloadFindPattern(w)
        self.find_seen = set()
        if self.minibuffer_mode:
            # Set up the state machine.
            self.ftm.clear_focus()
            self.changeAllFlag = False
            self.findAllFlag = False
            self.findAllUniqueFlag = False
            self.ftm.set_entry_focus()
            self.start_state_machine(event,
                prefix='Search: ',
                handler=self.start_search1,
                escape_handler = self.start_search_escape1,
            )
        else:
            self.openFindTab(event)
            self.ftm.init_focus()
            return

    def start_search1(self, event=None):
        """Common handler for use by vim commands and other find commands."""
        c, k, w = self.c, self.k, self.w
        self.p = c.p
        # Settings...
        find_pattern = k.arg
        self.updateFindList(find_pattern)
        self.ftm.setFindText(find_pattern)
        self.init_vim_search(find_pattern)
        # Gui...
        k.clearState()
        k.resetLabel()
        k.showStateAndMode()
        c.widgetWantsFocusNow(w)
        self.update_ivars()
        self.findNext()  # Handles reverse.
        
    def start_search_escape1(self, event=None):
        """
        Common escape handler for use by find commands.
        
        Prompt for a change pattern.
        """
        k = self.k
        self._sString = find_pattern = k.arg
        # Settings.
        k.getArgEscapeFlag = False
        self.ftm.setFindText(find_pattern)
        self.updateFindList(find_pattern)
        # Gui...
        regex = ' Regex' if self.pattern_match else ''
        backward = ' Backward' if self.reverse else ''
        prompt = f"Replace{regex}{backward}: {find_pattern} With: "
        k.setLabelBlue(prompt)
        self.addChangeStringToLabel()
        k.getNextArg(self._start_search_escape2)

    def _start_search_escape2(self, event):
        c, k = self.c, self.k
        self.p = c.p
        find_pattern = self._sString
        change_pattern = k.arg
        self.updateChangeList(change_pattern)
        self.ftm.setFindText(find_pattern)
        self.ftm.setChangeText(change_pattern)
        self.init_vim_search(find_pattern)
        # Gui...
        k.clearState()
        k.resetLabel()
        k.showStateAndMode()
        c.widgetWantsFocusNow(self.w)
        self.findNext()
    #@+node:ekr.20160920164418.2: *4* find.tag-children
    @cmd('tag-children')
    def interactive_tag_children(self, event=None):
        """tag-children: prompt for a tag and add it to all children of c.p."""
        if self.editWidget(event):  # sets self.w
            self.start_state_machine(event,
                prefix='Tag Children: ',
                handler=self.interactive_tag_children1)

    def interactive_tag_children1(self, event):
        c, k = self.c, self.k
        # Settings...
        tag = k.arg
        # Gui...
        k.clearState()
        k.resetLabel()
        k.showStateAndMode()
        self.tagChildren(tag)
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
    #@+node:ekr.20210112050845.1: *4* find.word-search
    @cmd('word-search')
    @cmd('word-search-forward')
    def wordSearchForward(self, event):
        """Same as start-search, with whole_word setting."""
        self.reverse = False
        self.pattern_match = False
        self.whole_world = True
        self.start_state_machine(event,
            prefix='Word Search: ',
            handler=self.start_search1,  # See start-search
            escape_handler = self.start_search_escape1,  # See start-search
        )
    #@+node:ekr.20131117164142.17009: *4* find.word-search-backward
    @cmd('word-search-backward')
    def wordSearchBackward(self, event):
        self.reverse = True
        self.pattern_match = False
        self.whole_world = True
        self.start_state_machine(event,
            prefix='Word Search Backward: ',
            handler=self.start_search1,  # See start-search
            escape_handler = self.start_search_escape1,  # See start-search
        )
    #@+node:ekr.20031218072017.3082: *3* LeoFind.Initing & finalizing
    #@+node:ekr.20031218072017.3083: *4* find.checkArgs
    def checkArgs(self):
        if not self.search_headline and not self.search_body:
            g.es("not searching headline or body")
            return False
        s = self.ftm.getFindText()
        if not s:
            g.es("empty find patttern")
            return False
        return True
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
        if w == c.frame.body.wrapper:
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
    #@+node:ekr.20131117164142.17007: *4* find.start_state_machine
    def start_state_machine(self, event, prefix, handler, escape_handler=None):

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
        k.getArgEscapes = ['\t'] if escape_handler else []
        self.handler = handler
        self.escape_handler = escape_handler
        k.get1Arg(event, handler=self.state0, tabList=self.findTextList, completion=True)
        
    def state0(self, event):
        """Dispatch the next handler."""
        k = self.k
        if k.getArgEscapeFlag:
            k.getArgEscapeFlag = False
            self.escape_handler(event)
        else:
            self.handler(event)
    #@+node:ekr.20131117164142.17008: *4* find.updateChange/FindList
    def updateChangeList(self, s):
        if s not in self.changeTextList:
            self.changeTextList.append(s)

    def updateFindList(self, s):
        if s not in self.findTextList:
            self.findTextList.append(s)
    #@+node:ekr.20131117164142.16915: *3* LeoFind.Option commands
    #@+node:ekr.20131117164142.16919: *4* find.toggle-find-*-option commands
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
    #@+node:ekr.20131117164142.17019: *4* find.set-find-* commands
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
    #@+node:ekr.20131117164142.16989: *4* find.showFindOptions & helper
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
    #@+node:ekr.20210108084340.1: *3* LeoFind.Script entries
    #@+node:ekr.20210108053422.1: *4* find.batch_change & helper
    def batch_change(self, root, replacements, settings=None):
        """
        Support batch change scripts.
        
        replacement: a list of tuples (find_string, change_string).
        settings: a dict or g.Bunch containing find/change settings.
        
        Example:
            
            h = '@file src/ekr/coreFind.py'
            root = g.findNodeAnywhere(c, h)
            assert root
            replacements = (
                ('clone_find_all', 'do_clone_find_all'),
                ('clone_find_all_flattened', 'do_clone_find_all_flattened'),
            )
            settings = dict(suboutline_only=True)
            count = c.findCommands.batch_change(c, root, replacements, settings)
            if count:
                c.save()
        """
        try:
            self.init_from_dict(settings or {})
            count = 0
            for find, change in replacements:
                count += self.batch_change_helper(root, find, change)
            return count
        except Exception:
            g.es_exception()
            return 0
    #@+node:ekr.20210108070948.1: *5* find.batch_change_helper
    def batch_change_helper(self, p, find_text, change_text):

        c, p1, u = self.c, p.copy(), self.c.undoer
        undoType = 'Batch Change All'
        # Check...
        if not find_text:
            return 0
        if not self.search_headline and not self.search_body:
            return 0
        if self.pattern_match:
            ok = self.precompilePattern()
            if not ok:
                return 0
        # Init...
        self.find_text = find_text
        self.change_text = self.replaceBackSlashes(change_text)
        if self.node_only:
            positions = [p1]
        elif self.suboutline_only:
            positions = p1.self_and_subtree()
        else:
            positions = c.all_unique_positions()
        self.initBatchText()
        u.beforeChangeGroup(p1, undoType)
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
                u.afterChangeNodeContents(p1, 'Replace All', undoData)
        u.afterChangeGroup(p1, undoType, reportFlag=True)
        print(f"{count:3}: {find_text:>30} => {change_text}")
        return count
    #@+node:ekr.20210110213529.1: *3* LeoFind.(To be removed)
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
    #@+node:ekr.20131117164142.17016: *4* find.changeAllCommand (called from generalChangeHelper)
    def changeAllCommand(self, event=None):
        c = self.c
        self.update_ivars()
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
    #@+node:ekr.20031218072017.3067: *3* LeoFind.Utils
    #@+node:ekr.20031218072017.3070: *4* find.change_selection & helper
    # Replace selection with self.change_text.
    # If no selection, insert self.change_text at the cursor.

    def change_selection(self):
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
                change_text = self.make_regex_subs(change_text, groups)
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
                change_text = self.make_regex_subs(self.change_text, groups)
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
    #@+node:ekr.20150630072552.1: *4* find.escapeCommand
    def escapeCommand(self, event):
        """Return the escaped command to execute."""
        d = self.c.k.bindingsDict
        aList = d.get(event.stroke)
        for bi in aList:
            if bi.stroke == event.stroke:
                return bi.commandName
        return None
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
    #@+node:ekr.20131119204029.16479: *4* find.helpForFindCommands
    def helpForFindCommands(self, event=None):
        """Called from Find panel.  Redirect."""
        self.c.helpCommands.helpForFindCommands(event)
    #@+node:ekr.20210108083003.1: *4* find.init_from_dict
    def init_from_dict(self, settings):
        """Initialize ivars from settings (a dict or g.Bunch)."""
        # The valid ivars and reasonable defaults.
        valid = dict(
            ignore_case=False,
            node_only=False,
            pattern_match=False,
            search_body=True,
            search_headline=True,
            suboutline_only=True,  # Seems safest.
            whole_word=True,
        )
        # Set ivars to reasonable defaults.
        for ivar in valid:
            setattr(self, ivar, valid.get(ivar))
        # Override ivars from settings.
        errors = 0
        for ivar in settings.keys():
            if ivar in valid:
                val = settings.get(ivar)
                if val in (True, False):
                    setattr(self, ivar, val)
                else:
                    g.trace("bad value: {ivar!r} = {val!r}")
                    errors += 1
            else:
                g.trace(f"ignoring {ivar!r} setting")
                errors += 1
        if errors:
            g.printObj(sorted(valid.keys()), tag='valid keys')
    #@+node:ekr.20210111082524.1: *4* find.init_vim_search
    def init_vim_search(self, pattern):
        """Initialize searches in vim mode."""
        c = self.c
        if c.vim_mode and c.vimCommands:
            c.vimCommands.update_dot_before_search(
                find_pattern=pattern,
                change_pattern=None)  # A flag.
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
    #@+node:ekr.20210110073117.30: *3* NEW:LeoFind: Helpers
    #@+node:ekr.20210110073117.31: *4* NEW:find.check_args
    def check_args(self, tag):
        if not self.search_headline and not self.search_body:
            if not g.unitTesting:
                g.es_print("not searching headline or body")  # pragma: no cover (skip)
            return False
        if not self.find_text:
            if not g.unitTesting:
                g.es_print(f"{tag}: empty find pattern")  # pragma: no cover (skip)
            return False
        return True
    #@+node:ekr.20210110073117.32: *4* NEW:find.compile_pattern
    def compile_pattern(self):
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
            if not g.unitTesting:  # pragma: no cover (skip)
                g.warning('invalid regular expression:', self.find_text)
            return False
    #@+node:ekr.20210110073117.33: *4* NEW:find.compute_result_status
    def compute_result_status(self, find_all_flag=False):
        """Return the status to be shown in the status line after a find command completes."""
        status = []
        if self.whole_word:
            status.append('word' if find_all_flag else 'word-only')
        if self.ignore_case:
            status.append('ignore-case')
        if self.pattern_match:
            status.append('regex')
        if find_all_flag:
            if self.search_headline:
                status.append('head')
            if self.search_body:
                status.append('body')
            if self.wrapping:
                status.append('wrapping')
        else:
            if self.search_headline:
                status.append('headline-only')
            if self.search_body:
                status.append('body-only')
            if self.suboutline_only:
                status.append('[outline-only]')
            if self.node_only:
                status.append('[node-only]')
        return f" ({', '.join(status)})" if status else ''
    #@+node:ekr.20210110073117.34: *4* NEW:find.create_clone_find_all_nodes
    def create_clone_find_all_nodes(self, clones, flattened):
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
        status = self.compute_result_status(find_all_flag=True)
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
    #@+node:ekr.20210110073117.35: *4* NEW:find.create_find_all_node
    def create_find_all_node(self, result):
        """Create a "Found All" node as the last node of the outline."""
        c = self.c
        found = c.lastTopLevel().insertAfter()
        assert found
        found.h = f"Found All:{self.find_text}"
        status = self.compute_result_status(find_all_flag=True)
        status = status.strip().lstrip('(').rstrip(')').strip()
        found.b = f"# {status}\n{''.join(result)}"
        return found
    #@+node:ekr.20210110073117.36: *4* NEW:find.find_next_match & helpers
    def find_next_match(self, p):
        """
        Resume the search where it left off.
        
        Return (p, pos, newpos) or (None, None, None)
        """
        attempts = 0
        if self.pattern_match:
            ok = self.compile_pattern()
            if not ok: return None, None, None
        while p:
            pos, newpos = self.search_helper()
            if pos is not None:
                # Success.
                return p, pos, newpos
            # Searching the pane failed: switch to another pane or node.
            if self.should_stay_in_node(p):
                # Switching panes is possible.  Do so.
                self.in_headline = not self.in_headline
                self.init_next_text(p)
            else:
                # Switch to the next/prev node, if possible.
                attempts += 1
                p = self.next_node_after_fail(p)
                if p:  # Found another node: select the proper pane.
                    self.in_headline = self.first_search_pane()
                    self.init_next_text(p)
        return None, None, None
    #@+node:ekr.20210110073117.37: *5* NEW:find.first_search_pane
    def first_search_pane(self):
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
        
        g.trace('can not happen: no search enabled')  # pragma: no cover (defensive)
        return False                                  # pragma: no cover (defensive, search body)
    #@+node:ekr.20210110073117.38: *5* NEW:find.init_next_text (gui code)
    def init_next_text(self, p):
        """
        Init s_ctrl when a search fails. On entry:
        - self.in_headline indicates what text to use.
        - self.reverse indicates how to set the insertion point.
        """
        w = self.s_ctrl
        s = p.h if self.in_headline else p.b
        if self.reverse:
            i, j = w.sel
            if i is not None and j is not None and i != j:
                ins = min(i, j)
            else:
                ins = len(s)
        else:
            ins = 0
        ### For vs-code. Also required for tests.
        w.setAllText(s)
        w.setInsertPoint(ins)
        return ins  # For tests.
    #@+node:ekr.20210110073117.39: *5* NEW:find.next_node_after_fail & helpers
    def next_node_after_fail(self, p):
        """Return the next node after a failed search or None."""
        c = self.c
        # Wrapping is disabled by any limitation of search.
        wrap = (
            self.wrapping
            and not self.node_only
            and not self.suboutline_only
            and not c.hoistStack)
        # Move to the next position.
        p = p.threadBack() if self.reverse else p.threadNext()
        # Check it.
        if p and self.outside_search_range(p):
            return None
        if not p and wrap:
            # Stateless wrap: Just set wrapPos and p.
            self.wrapPos = 0 if self.reverse else len(p.b)
            p = self.do_wrap()
        if not p:
            return None
        return p
    #@+node:ekr.20210110073117.40: *6* NEW:find.do_wrap
    def do_wrap(self):
        """Return the position resulting from a wrap."""
        c = self.c
        if self.reverse:
            p = c.rootPosition()
            while p and p.hasNext():
                p = p.next()
            p = p.lastNode()
            return p
        return c.rootPosition()
    #@+node:ekr.20210110073117.41: *6* NEW:find.outside_search_range
    def outside_search_range(self, p):
        """
        Return True if the search is about to go outside its range, assuming
        both the headline and body text of the present node have been searched.
        """
        c = self.c
        if not p:
            return True  # pragma: no cover (minor)
        if self.node_only:
            return True  # pragma: no cover (minor)
        if self.suboutline_only:
            if self.onlyPosition:
                if p != self.onlyPosition and not self.onlyPosition.isAncestorOf(p):
                    return True
            else:  # pragma: no cover (defensive)
                g.trace('Can not happen: onlyPosition!', p.h)
                return True
        if c.hoistStack:  # pragma: no cover (defensive)
            bunch = c.hoistStack[-1]
            if not bunch.p.isAncestorOf(p):
                g.trace('outside hoist', p.h)
                g.warning('found match outside of hoisted outline')
                return True
        return False  # Within range.
    #@+node:ekr.20210110073117.42: *5* NEW:find.should_stay_in_node
    def should_stay_in_node(self, p):
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
    #@+node:ekr.20210110073117.43: *4* NEW:find.inner_search_helper & helpers
    def inner_search_helper(self, s, i, j, pattern):
        """Dispatch the proper search method based on settings."""
        backwards = self.reverse
        nocase = self.ignore_case
        regexp = self.pattern_match
        word = self.whole_word
        if backwards:
            i, j = j, i
        if not s[i:j] or not pattern:
            return -1, -1
        if regexp:
            pos, newpos = self.regex_helper(s, i, j, pattern, backwards, nocase)
        elif backwards:
            pos, newpos = self.backwards_helper(s, i, j, pattern, nocase, word)
        else:
            pos, newpos = self.plain_helper(s, i, j, pattern, nocase, word)
        return pos, newpos
    #@+node:ekr.20210110073117.44: *5* NEW:find.backwards_helper
    debugIndices = []

    def backwards_helper(self, s, i, j, pattern, nocase, word):
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
        pattern = self.replace_back_slashes(pattern)
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
                if k == -1:
                    break
                if self.match_word(s, k, pattern):
                    return k, k + n
                j = max(0, k - 1)
            return -1, -1
        k = s.rfind(pattern, i, j)
        if k == -1:
            return -1, -1
        return k, k + n
    #@+node:ekr.20210110073117.45: *5* NEW:find.match_word
    def match_word(self, s, i, pattern):
        """Do a whole-word search."""
        pattern = self.replace_back_slashes(pattern)
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
    #@+node:ekr.20210110073117.46: *5* NEW:find.plain_helper
    def plain_helper(self, s, i, j, pattern, nocase, word):
        """Do a plain search."""
        if nocase:
            s = s.lower()
            pattern = pattern.lower()
        pattern = self.replace_back_slashes(pattern)
        n = len(pattern)
        if word:
            while 1:
                k = s.find(pattern, i, j)
                if k == -1:
                    break
                if self.match_word(s, k, pattern):
                    return k, k + n
                i = k + n
            return -1, -1
        k = s.find(pattern, i, j)
        if k == -1:
            return -1, -1
        return k, k + n
    #@+node:ekr.20210110073117.47: *5* NEW:find.regex_helper
    def regex_helper(self, s, i, j, pattern, backwards, nocase):
        """Called from inner_search_helper"""
        re_obj = self.re_obj  # Use the pre-compiled object
        if not re_obj:
            if not g.unitTesting:  # pragma: no cover (skip)
                g.trace('can not happen: no re_obj')
            return -1, -1
        if backwards:
            # Scan to the last match using search here.
            i, last_mo = 0, None
            while i < len(s):
                mo = re_obj.search(s, i, j)
                if not mo:
                    break
                i += 1
                last_mo = mo
            mo = last_mo
        else:
            mo = re_obj.search(s, i, j)
        if mo:
            self.match_obj = mo
            return mo.start(), mo.end()
        self.match_obj = None
        return -1, -1
        #
        # The following is mysterious.
        # Félix, please don't both with it.
        # I'll re-enable it if it ever makes sense to me :-)
        ###
            # # if mo and mo.group(0) != 'def': g.trace(i, mo, mo.start(), mo.end())  ###
            # while mo and 0 <= i <= len(s):
                # if mo.start() == mo.end():
                    # if backwards: 
                        # # Search backward using match instead of search.
                        # i -= 1
                        # while 0 <= i < len(s):
                            # mo = re_obj.match(s, i, j)
                            # if mo: break  ###???
                            # i -= 1
                    # else:
                        # i += 1
                        # mo = re_obj.search(s, i, j)
                # else:
                    # self.match_obj = mo
                    # return mo.start(), mo.end()
            # self.match_obj = None
            # return -1, -1
    #@+node:ekr.20210110073117.48: *4* NEW:find.make_regex_subs
    def make_regex_subs(self, change_text, groups):
        """
        Substitute group[i-1] for \\i strings in change_text.
        
        Groups is a tuple of strings, one for every matched group.
        """
        
        # g.printObj(list(groups), tag=f"groups in {change_text!r}")

        def repl(match_object):
            """re.sub calls this function once per group."""
            # # 1494...
            n = int(match_object.group(1)) - 1
            if 0 <= n < len(groups):
                # Executed only if the change text contains groups that match.
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
        return result
    #@+node:ekr.20210110073117.49: *4* NEW:find.replace_back_slashes
    def replace_back_slashes(self, s):
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
    #@+node:ekr.20210110073117.50: *4* NEW:find.search_helper & helpers
    def search_helper(self):
        """
        Search s_ctrl for self.find_text with present options.
        Returns (pos, newpos) or (None,None).
        """
        p, w = self.p, self.s_ctrl
        if self.find_def_data and p.v in self.find_seen:
            # Don't find defs/vars multiple times.
            return None, None  # pragma: no cover (minor)
        index = w.getInsertPoint()
        s = w.getAllText()
        if not s:  # pragma: no cover (minor)
            return None, None
        stopindex = 0 if self.reverse else len(s)
        pos, newpos = self.inner_search_helper(s, index, stopindex, self.find_text)
        if self.in_headline and not self.search_headline:
            return None, None  # pragma: no cover (minor)
        if not self.in_headline and not self.search_body:
            return None, None  # pragma: no cover (minor)
        if pos == -1:
            return None, None
        ins = min(pos, newpos) if self.reverse else max(pos, newpos)
        w.setSelectionRange(pos, newpos, insert=ins)
        if self.find_def_data:
            self.find_seen.add(p.v)
        return pos, newpos
    #@-others
#@+node:ekr.20200216063538.1: ** class TestFind (LeoFind.py)
class TestFind(unittest.TestCase):
    """Test cases for leoFind.py"""
    #@+others
    #@+node:ekr.20210110073117.55: *3* TestFind: Top level
    #@+node:ekr.20210110073117.56: *4* TestFind.make_test_tree
    def make_test_tree(self):
        """Make a test tree for other tests"""
        c = self.c
        root = c.rootPosition()
        root.h = 'Root'
        root.b = f"def root():\n    pass\n"
        last = root

        def make_child(n, p):
            p2 = p.insertAsLastChild()
            p2.h = f"child {n}"
            p2.b = f"def child{n}():\n    v{n} = 2\n"
            return p2

        def make_top(n, sib):
            p = sib.insertAfter()
            p.h = f"Node {n}"
            p.b = f"def top{n}():\n    v{n} = 3\n"
            return p
            
        for n in range(0, 4, 3):
            last = make_top(n+1, last)
            child = make_child(n+2, last)
            make_child(n+3, child)
            
        for p in c.all_positions():
            p.v.clearDirty()
            p.v.clearVisited()

    #@+node:ekr.20210110073117.57: *4* TestFind.setUp & tearDown
    def setUp(self):
        
        # pylint: disable=import-self
        from leo.core import leoFind
        g.unitTesting = True
        self.c = leoTest2.create_app()
        self.x = leoFind.LeoFind(self.c)
        self.settings = self.x.default_settings()
        self.make_test_tree()

    def tearDown(self):
        g.unitTesting = False

    #@+node:ekr.20210110073117.58: *4* TestFind.test_tree
    def test_tree(self):
        table = (
            (0, 'Root'),
            (0, 'Node 1'),
            (1, 'child 2'),
            (2, 'child 3'),
            (0, 'Node 4'),
            (1, 'child 5'),
            (2, 'child 6'),
        )
        i = 0
        for p in self.c.all_positions():
            level, h = table[i]
            i += 1
            assert p.h == h, (p.h, h)
            assert p.level() == level, (p.level(), level, p.h)
            # print(' '*p.level(), p.h)
            # g.printObj(g.splitLines(p.b), tag=p.h)
    #@+node:ekr.20210110073117.59: *3* Tests of Commands...
    #@+node:ekr.20210110073117.60: *4* TestFind.clone-find-all
    def test_clone_find_all(self):
        settings, x = self.settings, self.x
        # Regex find.
        settings.find_text = r'^def\b'
        settings.change_text = 'def'  # Don't actually change anything!
        settings.pattern_match = True
        x.do_clone_find_all(settings)
        # Word find.
        settings.find_text = 'def'
        settings.match_word = True
        settings.pattern_match = False
        x.do_clone_find_all(settings)
        # Suboutline only.
        settings.suboutline_only = True
        x.do_clone_find_all(settings)
    #@+node:ekr.20210110073117.61: *4* TestFind.clone-find-all-flattened
    def test_clone_find_all_flattened(self):
        settings, x = self.settings, self.x
        # regex find.
        settings.find_text = r'^def\b'
        settings.pattern_match = True
        x.do_clone_find_all_flattened(settings)
        # word find.
        settings.find_text = 'def'
        settings.match_word = True
        settings.pattern_match = False
        x.do_clone_find_all_flattened(settings)
        # Suboutline only.
        settings.suboutline_only = True
        x.do_clone_find_all_flattened(settings)
    #@+node:ekr.20210110073117.62: *4* TestFind.clone-find-tag
    def test_clone_find_tag(self):
        c, x = self.c, self.x
        
        class DummyTagController:
            
            def __init__(self, clones):
                self.clones = clones
                
            def get_tagged_nodes(self, tag):
                return self.clones
                
            def show_all_tags(self):
                pass

        c.theTagController = DummyTagController([c.rootPosition()])
        x.do_clone_find_tag('test')
        c.theTagController = DummyTagController([])
        x.do_clone_find_tag('test')
        c.theTagController = None
        x.do_clone_find_tag('test')
    #@+node:ekr.20210110073117.63: *4* TestFind.find-all
    def test_find_all(self):
        settings, x = self.settings, self.x
        # Test 1.
        settings.find_text = r'^def\b'
        settings.pattern_match = True
        x.do_find_all(settings)
        # Test 2.
        settings.suboutline_only = True
        x.do_find_all(settings)
        # Test 3.
        settings.suboutline_only = False
        settings.search_headline = False
        settings.p.setVisited()
        x.do_find_all(settings)
    #@+node:ekr.20210110073117.64: *4* TestFind.find-next & find-prev
    def test_find_next(self):
        c, settings, x = self.c, self.settings, self.x
        settings.find_text = 'def top1'
        # find-next
        p, pos, newpos = x.find_next(settings)
        assert p and p.h == 'Node 1', p.h
        s = p.b[pos:newpos]
        assert s == settings.find_text, repr(s)
        # find-prev: starts at end, so we stay in the node.
        last = c.lastTopLevel()
        child = last.firstChild()
        grand_child = child.firstChild()
        assert grand_child.h == 'child 6', grand_child.h
        settings.p = grand_child.copy()
        settings.find_text = 'def child2'
        p, pos, newpos = x.find_prev(settings)
        assert p.h == 'child 2', p.h
        s = p.b[pos:newpos]
        assert s == settings.find_text, repr(s)
    #@+node:ekr.20210110073117.65: *4* TestFind.find-def
    def test_find_def(self):
        c, settings, x = self.c, self.settings, self.x
        root = c.rootPosition()
        settings.find_text = 'child5'
        # Test 1.
        p, pos, newpos = x.find_def(settings)
        assert p and p.h == 'child 5'
        s = p.b[pos:newpos]
        assert s == 'def child5', repr(s)
        # Test 2: switch style.
        settings.find_text = 'child_5'
        x.find_def(settings)
        # Test3: not found after switching style.
        settings.p = root.next()
        settings.find_text = 'def notFound'
        x.find_def(settings)
        
    def test_find_def_use_cff(self):
        settings, x = self.settings, self.x
        settings.find_text = 'child5'
        # Test 1: Set p *without* use_cff.
        p, pos, newpos = x.find_def(settings)
        assert p and p.h == 'child 5'
        s = p.b[pos:newpos]
        assert s == 'def child5', repr(s)
        # Test 2.
        settings.use_cff = True
        x.find_def(settings)
        # Test 3: switch style.
        settings.find_text = 'child_5'
        x.find_def(settings)
    #@+node:ekr.20210110073117.66: *4* TestFind.find-var
    def test_find_var(self):
        settings, x = self.settings, self.x
        settings.find_text = r'v5'
        p, pos, newpos = x.find_var(settings)
        assert p and p.h == 'child 5', repr(p)
        s = p.b[pos:newpos]
        assert s == 'v5 =', repr(s)
    #@+node:ekr.20210110073117.67: *4* TestFind.replace-all
    def test_replace_all(self):
        c, settings, x = self.c, self.settings, self.x
        root = c.rootPosition()
        settings.find_text = 'def'
        settings.change_text = '_DEF_'
        settings.ignore_case = False
        settings.match_word = True
        settings.pattern_match = False
        settings.suboutline_only = False
        x.replace_all(settings)
        # Node only.
        settings.node_only = True
        x.replace_all(settings)
        settings.node_only = False
        # Suboutline only.
        settings.suboutline_only = True
        x.replace_all(settings)
        settings.suboutline_only = False
        # Pattern match.
        settings.pattern_match = True
        x.replace_all(settings)
        # Multiple matches
        root.h = 'abc'
        root.b = 'abc\nxyz abc\n'
        settings.find_text = settings.change_text = 'abc'
        x.replace_all(settings)
        # Set ancestor @file node dirty.
        root.h = '@file xyzzy'
        settings.find_text = settings.change_text = 'child1'
        
    def test_replace_all_with_at_file_node(self):
        c, settings, x = self.c, self.settings, self.x
        root = c.rootPosition().next()  # Must have children.
        settings.find_text = 'def'
        settings.change_text = '_DEF_'
        settings.ignore_case = False
        settings.match_word = True
        settings.pattern_match = False
        settings.suboutline_only = False
        # Ensure that the @file node is marked dirty.
        root.h = '@file xyzzy.py'
        root.b = ''
        root.v.clearDirty()
        assert root.anyAtFileNodeName()
        x.replace_all(settings)
        assert root.v.isDirty(), root.h
        
    def test_replace_all_headline(self):
        settings, x = self.settings, self.x
        settings.find_text = 'child'
        settings.change_text = '_CHILD_'
        settings.ignore_case = False
        settings.in_headline = True
        settings.match_word = True
        settings.pattern_match = False
        settings.suboutline_only = False
        x.replace_all(settings)
    #@+node:ekr.20210110073117.68: *4* TestFind.replace-then-find
    def test_replace_then_find(self):
        settings, w, x = self.settings, self.c.frame.body.wrapper, self.x
        settings.find_text = 'def top1'
        settings.change_text = 'def top'
        # find-next
        p, pos, newpos = x.find_next(settings)
        assert p and p.h == 'Node 1', p.h
        s = p.b[pos:newpos]
        assert s == settings.find_text, repr(s)
        # replace-then-find
        w.setSelectionRange(pos, newpos, insert=pos)
        x.do_replace_then_find(settings)
        # Failure exit.
        w.setSelectionRange(0, 0)
        x.do_replace_then_find(settings)
        
    def test_replace_then_find_regex(self):
        settings, w, x = self.settings, self.c.frame.body.wrapper, self.x
        settings.find_text = r'(def) top1'
        settings.change_text = r'\1\1'
        settings.pattern_match = True
        # find-next
        p, pos, newpos = x.find_next(settings)
        s = p.b[pos:newpos]
        assert s == 'def top1', repr(s)
        # replace-then-find
        w.setSelectionRange(pos, newpos, insert=pos)
        x.do_replace_then_find(settings)
        
    def test_replace_then_find_in_headline(self):
        settings, x = self.settings, self.x
        p = settings.p
        settings.find_text = 'Node 1'
        settings.change_text = 'Node 1a'
        settings.in_headline = True
        # find-next
        p, pos, newpos = x.find_next(settings)
        assert p and p.h == settings.find_text, p.h
        w = self.c.edit_widget(p)
        assert w
        s = p.h[pos:newpos]
        assert s == settings.find_text, repr(s)
    #@+node:ekr.20210110073117.69: *4* TestFind.tag-children
    def test_tag_children(self):
        
        c, x = self.c, self.x
        
        class DummyTagController:
            def add_tag(self, p, tag):
                pass

        p = c.rootPosition().next()
        c.theTagController = None
        x.tag_children(p, 'test')
        c.theTagController = DummyTagController()
        x.tag_children(p, 'test')
    #@+node:ekr.20210110073117.70: *3* Tests of Helpers...
    #@+node:ekr.20210110073117.71: *4* TestFind.backwards_helper
    def test_backwards_helper(self):
        settings, x = self.settings, self.x
        pattern = 'def'
        for nocase in (True, False):
            settings.ignore_case = nocase
            for word in (True, False):
                for s in ('def spam():\n', 'define spam'):
                    settings.whole_word = word
                    x.init(settings)
                    x.backwards_helper(s, 0, len(s), pattern, nocase, word)
                    x.backwards_helper(s, 0, 0, pattern, nocase, word)
    #@+node:ekr.20210110073117.72: *4* TestFind.bad compile_pattern
    def test_argument_errors(self):

        settings, x = self.settings, self.x
        # Bad search pattern.
        settings.find_text = r'^def\b(('
        settings.pattern_match = True
        x.do_clone_find_all(settings)
        x.find_next_match(p=None)
        x.replace_all(settings)
    #@+node:ekr.20210110073117.73: *4* TestFind.batch_word_replace
    def test_batch_word_replace(self):
        settings, x = self.settings, self.x
        settings.find_text = 'b'
        settings.change_text = 'B'
        for ignore in (True, False):
            settings.ignore_case = ignore
            x.init(settings)
            s = 'abc b z'
            count, s2 = x.batch_word_replace(s)
            assert count == 1 and s2 == 'abc B z', (ignore, count, repr(s2))
    #@+node:ekr.20210110073117.74: *4* TestFind.batch_plain_replace
    def test_batch_plain_replace(self):
        settings, x = self.settings, self.x
        settings.find_text = 'b'
        settings.change_text = 'B'
        for ignore in (True, False):
            settings.ignore_case = ignore
            x.init(settings)
            s = 'abc b z'
            count, s2 = x.batch_plain_replace(s)
            assert count == 2 and s2 == 'aBc B z', (ignore, count, repr(s2))
    #@+node:ekr.20210110073117.75: *4* TestFind.batch_regex_replace
    def test_batch_regex_replace(self):
        settings, x = self.settings, self.x
        s = 'abc b z'
        table = (
            (1, 2, 'B', 'B', 'aBc B z'),
            (0, 2, 'b', 'B', 'aBc B z'),
            (1, 2, r'([BX])', 'B', 'aBc B z'),
        )
        for ignore, count, find, change, expected_s in table:
            settings.ignore_case = bool(ignore)
            settings.find_text = find
            settings.change_text = change
            x.init(settings)
            actual_count, actual_s = x.batch_regex_replace(s)
            assert actual_count == count and actual_s == expected_s, (
                f"ignore: {ignore} find: {find} change {change}\n"
                f"expected count: {count} s: {expected_s}\n"
                f"     got count: {actual_count} s: {actual_s}")
               
    #@+node:ekr.20210110073117.76: *4* TestFind.check_args
    def test_check_args(self):
        # Bad search patterns..
        x = self.x
        settings = self.settings
        # Not searching headline or body.
        settings.search_body = False
        settings.search_headline = False
        x.do_clone_find_all(settings)
        # Empty find pattern.
        settings.search_body = True
        settings.find_text = ''
        x.do_clone_find_all(settings)
        x.do_clone_find_all_flattened(settings)
        x.do_find_all(settings)
        x.find_def(settings)
        x.find_var(settings)
        x.find_next(settings)
        x.find_next_match(None)
        x.find_prev(settings)
        x.replace_all(settings)
        x.do_replace_then_find(settings)
    #@+node:ekr.20210110073117.77: *4* TestFind.compute_result_status
    def test_compute_result_status(self):
        x = self.x
        # find_all_flag is True
        all_settings = x.default_settings()
        all_settings.ignore_case = True
        all_settings.pattern_match = True
        all_settings.whole_word = True
        all_settings.wrapping = True
        x.init(all_settings)
        x.compute_result_status(find_all_flag=True)
        # find_all_flag is False
        partial_settings = x.default_settings()
        partial_settings.search_body = True
        partial_settings.search_headline = True
        partial_settings.node_only = True
        partial_settings.suboutline_only = True
        partial_settings.wrapping = True
        x.init(partial_settings)
        x.compute_result_status(find_all_flag=False)
    #@+node:ekr.20210110073117.78: *4* TestFind.do_wrap
    def test_do_wrap(self):
        settings, x = self.settings, self.x
        for reverse in (True, False):
            settings.reverse = reverse
            x.init(settings)
            x.do_wrap()

    #@+node:ekr.20210110073117.79: *4* TestFind.dump_tree
    def dump_tree(self, tag=''):  # pragma: no cover (skip)
        """Dump the test tree created by make_test_tree."""
        c = self.c
        print('dump_tree', tag)
        for p in c.all_positions():
            print(' '*p.level(),  p.h, 'dirty', p.v.isDirty())
            # g.printObj(g.splitLines(p.b), tag=p.h)
    #@+node:ekr.20210110073117.80: *4* TestFind.find_next_batch_match
    def test_find_next_batch_match(self):
        c, settings, x = self.c, self.settings, self.x
        p = c.rootPosition()
        for find in ('xxx', 'def'):
            settings.find_text = find
            x.find_next_batch_match(p)
    #@+node:ekr.20210110073117.81: *4* TestFind.init_next_text
    def test_init_next_text(self):
        settings, x = self.settings, self.x
        for reverse in (True, False):
            settings.reverse = reverse
            for in_head in (True, False):
                settings.in_headline = in_head
                x.init(settings)
                for sel in (0, 0), (0, 2):
                    x.s_ctrl.sel = sel
                    x.init_next_text(settings.p)
    #@+node:ekr.20210110073117.82: *4* TestFind.make_regex_subs (to do)
    def test_make_regex_subs(self):
        x = self.x
        x.re_obj = re.compile(r'(.*)pattern')  # The search pattern.
        m = x.re_obj.search('test pattern')  # The find pattern.
        change_text = r'\1Pattern\2'  # \2 is non-matching group.
        x.make_regex_subs(change_text, m.groups())

        # OLD
        # groups = (r"f'", r"line\n")
        # change_text = r"""\1 AA \2 BB \3'"""
        # expected = r"""f' AA line\\n BB \3'"""
        # result = x.makeRegexSubs(change_text, groups)
        # assert result == expected, (expected, result)
    #@+node:ekr.20210110073117.83: *4* TestFind.match_word
    def test_match_word(self):
        x = self.x
        x.match_word("def spam():", 0, "spam")
        x.match_word("def spam():", 0, "xxx")
        
    #@+node:ekr.20210110073117.84: *4* TestFind.next_node_after_fail
    def test_next_node_after_fail(self):
        settings, x = self.settings, self.x
        for reverse in (True, False):
            settings.reverse = reverse
            for wrapping in (True, False):
                settings.wrapping = wrapping
                x.init(settings)
                x.next_node_after_fail(settings.p)
    #@+node:ekr.20210110073117.85: *4* TestFind.plain_helper
    def test_plain_helper(self):
        settings, x = self.settings, self.x
        pattern = 'def'
        for nocase in (True, False):
            settings.ignore_case = nocase
            for word in (True, False):
                for s in ('def spam():\n', 'define'):
                    settings.whole_word = word
                    x.init(settings)
                    x.plain_helper(s, 0, len(s), pattern, nocase, word)
                    x.plain_helper(s, 0, 0, pattern, nocase, word)
    #@+node:ekr.20210110073117.86: *4* TestFind.replace_all_helper
    def test_replace_all_helper(self):
        settings, x = self.settings, self.x
        settings.find_text = 'xyzzy'
        settings.change_text = 'xYzzy'
        s = 'abc xyzzy done'
        x.replace_all_helper('')  # Error test.
        for regex in (True, False):
            settings.pattern_match = regex
            for word in (True, False):
                settings.whole_word = word
                x.init(settings)
                x.replace_all_helper(s)
    #@+node:ekr.20210110073117.87: *4* TestFind.replace_back_slashes
    def test_replace_back_slashes(self):
        x = self.x
        table = (
            (r'a\bc', r'a\bc'),
            (r'a\\bc', r'a\bc'),
            (r'a\tc', 'a\tc'), # Replace \t by a tab.
            (r'a\nc', 'a\nc'), # Replace \n by a newline.
        )
        for s, expected in table:
            result = x.replace_back_slashes(s)
            assert result == expected, (s, result, expected)
    #@+node:ekr.20210110073117.88: *4* TestFind.regex_helper
    def test_regex_helper(self):
        x = self.x
        pattern = r'(.*)pattern'
        x.re_obj = re.compile(pattern)
        table = (
            'test pattern',  # Match.
            'xxx',  # No match.
        )
        for backwards in (True, False):
            for nocase in (True, False):
                for s in table:
                    if backwards:
                        i = j = len(s)
                    else:
                        i = j = 0
                    x.regex_helper(s, i, j, pattern, backwards, nocase)
        # Error test.
        x.re_obj = None
        backwards = pattern = nocase = None
        x.regex_helper("", 0, 0, pattern, backwards, nocase)

        # for change_text, groups, expected in table:
            # result = x.make_regex_subs(change_text, groups)
            # assert result == expected, (
                # f"change_text: {change_text}\n"
                # f"     groups: {groups}\n"
                # f"   expected: {expected}\n"
                # f"        got: {result}")
    #@+node:ekr.20210110073117.89: *4* TestFind.switch_style
    def test_switch_style(self):
        x = self.x
        table = (
            ('', None),
            ('TestClass', None),
            ('camelCase', 'camel_case'),
            ('under_score', 'underScore'),
        )
        for s, expected in table:
            result = x.switch_style(s)
            assert result == expected, (
                f"       s: {s}\n"
                f"expected: {expected!r}\n"
                f"     got: {result!r}")
    #@-others
#@+node:ekr.20210108053422.1: ** find.batch_change & helper
def batch_change(self, root, replacements, settings=None):
    """
    Support batch change scripts.
    
    replacement: a list of tuples (find_string, change_string).
    settings: a dict or g.Bunch containing find/change settings.
    
    Example:
        
        h = '@file src/ekr/coreFind.py'
        root = g.findNodeAnywhere(c, h)
        assert root
        replacements = (
            ('clone_find_all', 'do_clone_find_all'),
            ('clone_find_all_flattened', 'do_clone_find_all_flattened'),
        )
        settings = dict(suboutline_only=True)
        count = c.findCommands.batch_change(c, root, replacements, settings)
        if count:
            c.save()
    """
    try:
        self.init_from_dict(settings or {})
        count = 0
        for find, change in replacements:
            count += self.batch_change_helper(root, find, change)
        return count
    except Exception:
        g.es_exception()
        return 0
#@+node:ekr.20210108070948.1: *3* find.batch_change_helper
def batch_change_helper(self, p, find_text, change_text):

    c, p1, u = self.c, p.copy(), self.c.undoer
    undoType = 'Batch Change All'
    # Check...
    if not find_text:
        return 0
    if not self.search_headline and not self.search_body:
        return 0
    if self.pattern_match:
        ok = self.precompilePattern()
        if not ok:
            return 0
    # Init...
    self.find_text = find_text
    self.change_text = self.replaceBackSlashes(change_text)
    if self.node_only:
        positions = [p1]
    elif self.suboutline_only:
        positions = p1.self_and_subtree()
    else:
        positions = c.all_unique_positions()
    self.initBatchText()
    u.beforeChangeGroup(p1, undoType)
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
            u.afterChangeNodeContents(p1, 'Replace All', undoData)
    u.afterChangeGroup(p1, undoType, reportFlag=True)
    print(f"{count:3}: {find_text:>30} => {change_text}")
    return count
#@-others
if __name__ == '__main__':
    unittest.main()

#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
