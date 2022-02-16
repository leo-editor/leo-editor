#@+leo-ver=5-thin
#@+node:ekr.20060123151617: * @file leoFind.py
"""Leo's gui-independent find classes."""
import keyword
import re
import sys
import time
from leo.core import leoGlobals as g

#@+<< Theory of operation of find/change >>
#@+node:ekr.20031218072017.2414: ** << Theory of operation of find/change >>
#@@language rest
#@@nosearch
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
# find_next_match() method and its helpers handle the many details
# involved by setting self.s_text and its insert and sel attributes.
#@-<< Theory of operation of find/change >>

def cmd(name):
    """Command decorator for the findCommands class."""
    return g.new_cmd_decorator(name, ['c', 'findCommands',])

#@+others
#@+node:ekr.20061212084717: ** class LeoFind (LeoFind.py)
class LeoFind:
    """The base class for Leo's Find commands."""
    #@+others
    #@+node:ekr.20131117164142.17021: *3* LeoFind.birth
    #@+node:ekr.20031218072017.3053: *4*  find.__init__
    def __init__(self, c):
        """Ctor for LeoFind class."""
        self.c = c
        self.expert_mode = False  # Set in finishCreate.
        self.ftm = None  # Created by dw.createFindTab.
        self.frame = None
        self.k = c.k
        self.re_obj = None
        #
        # The work "widget".
        self.work_s = ''  # p.b or p.c.
        self.work_sel = (0, 0, 0)  # pos, newpos, insert.
        #
        # Options ivars: set by FindTabManager.init.
        self.ignore_case = None
        self.node_only = None
        self.pattern_match = None
        self.search_headline = None
        self.search_body = None
        self.suboutline_only = None
        self.mark_changes = None
        self.mark_finds = None
        self.whole_word = None
        #
        # For isearch commands...
        self.stack = []  # Entries are (p, sel)
        self.isearch_ignore_case = None
        self.isearch_forward_flag = None
        self.isearch_regexp = None
        self.findTextList = []
        self.changeTextList = []
        #
        # For find/change...
        self.find_text = ""
        self.change_text = ""
        #
        # State machine...
        self.escape_handler = None
        self.handler = None
        # "Delayed" requests for do_find_next.
        self.request_reverse = False
        self.request_pattern_match = False
        self.request_whole_word = False
        # Internal state...
        self.changeAllFlag = False
        self.findAllUniqueFlag = False
        self.find_def_data = None
        self.in_headline = False
        self.match_obj = None
        self.reverse = False
        self.root = None  # The start of the search, especially for suboutline-only.
        self.unique_matches = set()
        #
        # User settings.
        self.minibuffer_mode = None
        self.reload_settings()
    #@+node:ekr.20210110073117.6: *4* find.default_settings
    def default_settings(self):
        """Return a dict representing all default settings."""
        c = self.c
        return g.Bunch(
            # State...
            in_headline=False,
            p=c.rootPosition(),
            # Find/change strings...
            find_text='',
            change_text='',
            # Find options...
            ignore_case=False,
            mark_changes=False,
            mark_finds=False,
            node_only=False,
            pattern_match=False,
            reverse=False,
            search_body=True,
            search_headline=True,
            suboutline_only=False,
            whole_word=False,
            wrapping=False,
        )
    #@+node:ekr.20131117164142.17022: *4* find.finishCreate
    def finishCreate(self):
        # New in 4.11.1.
        # Must be called when config settings are valid.
        c = self.c
        self.reload_settings()
        # now that configuration settings are valid,
        # we can finish creating the Find pane.
        dw = c.frame.top
        if dw:
            dw.finishCreateLogPane()
    #@+node:ekr.20210110073117.4: *4* find.init_ivars_from_settings
    def init_ivars_from_settings(self, settings):
        """
        Initialize all ivars from settings, including required defaults.

        This should be called from the do_ methods as follows:

            self.init_ivars_from_settings(settings)
            if not self.check_args('find-next'):
                return <appropriate error indication>
        """
        #
        # Init required defaults.
        self.reverse = False
        #
        # Init find/change strings.
        self.change_text = settings.change_text
        self.find_text = settings.find_text
        #
        # Init find options.
        self.ignore_case = settings.ignore_case
        self.mark_changes = settings.mark_changes
        self.mark_finds = settings.mark_finds
        self.node_only = settings.node_only
        self.pattern_match = settings.pattern_match
        self.search_body = settings.search_body
        self.search_headline = settings.search_headline
        self.suboutline_only = settings.suboutline_only
        self.whole_word = settings.whole_word
        # self.wrapping = settings.wrapping
    #@+node:ekr.20210110073117.5: *5* NEW:find.init_settings
    def init_settings(self, settings):
        """Initialize all user settings."""

    #@+node:ekr.20171113164709.1: *4* find.reload_settings
    def reload_settings(self):
        """LeoFind.reload_settings."""
        c = self.c
        self.minibuffer_mode = c.config.getBool('minibuffer-find-mode', default=False)
        self.reverse_find_defs = c.config.getBool('reverse-find-defs', default=False)
    #@+node:ekr.20210108053422.1: *3* find.batch_change (script helper) & helpers
    def batch_change(self, root, replacements, settings=None):
        #@+<< docstring: find.batch_change >>
        #@+node:ekr.20210925161347.1: *4* << docstring: find.batch_change >>
        """
        Support batch change scripts.

        replacement: a list of tuples (find_string, change_string).
        settings: a dict or g.Bunch containing find/change settings.
                  See find._init_from_dict for a list of valid settings.

        Example:

            h = '@file src/ekr/coreFind.py'
            root = g.findNodeAnywhere(c, h)
            assert root
            replacements = (
                ('clone_find_all', 'do_clone_find_all'),
                ('clone_find_all_flattened', 'do_clone_find_all_flattened'),
            )
            settings = dict(suboutline_only=True)
            count = c.findCommands.batch_change(root, replacements, settings)
            if count:
                c.save()
        """
        #@-<< docstring: find.batch_change >>
        try:
            self._init_from_dict(settings or {})
            count = 0
            for find, change in replacements:
                count += self._batch_change_helper(root, find, change)
            return count
        except Exception:
            g.es_exception()
            return 0
    #@+node:ekr.20210108070948.1: *4* find._batch_change_helper
    def _batch_change_helper(self, p, find_text, change_text):

        c, p1, u = self.c, p.copy(), self.c.undoer
        undoType = 'Batch Change All'
        # Check...
        if not find_text:  # pragma: no cover
            return 0
        if not self.search_headline and not self.search_body:
            return 0  # pragma: no cover
        if self.pattern_match:
            ok = self.precompile_pattern()
            if not ok:  # pragma: no cover
                return 0
        # Init...
        self.find_text = find_text
        self.change_text = self.replace_back_slashes(change_text)
        if self.node_only:
            positions = [p1]
        elif self.suboutline_only:
            positions = p1.self_and_subtree()
        else:
            positions = c.all_unique_positions()
        # Init the work widget.
        s = p.h if self.in_headline else p.b
        self.work_s = s
        self.work_sel = (0, 0, 0)
        # The main loop.
        u.beforeChangeGroup(p1, undoType)
        count = 0
        for p in positions:
            count_h, count_b = 0, 0
            undoData = u.beforeChangeNodeContents(p)
            if self.search_headline:
                count_h, new_h = self._change_all_search_and_replace(p.h)
                if count_h:
                    count += count_h
                    p.h = new_h
            if self.search_body:
                count_b, new_b = self._change_all_search_and_replace(p.b)
                if count_b:
                    count += count_b
                    p.b = new_b
            if count_h or count_b:
                u.afterChangeNodeContents(p1, 'Replace All', undoData)
        u.afterChangeGroup(p1, undoType, reportFlag=True)
        if not g.unitTesting:  # pragma: no cover
            print(f"{count:3}: {find_text:>30} => {change_text}")
        return count
    #@+node:ekr.20210108083003.1: *4* find._init_from_dict
    def _init_from_dict(self, settings):
        """Initialize ivars from settings (a dict or g.Bunch)."""
        # The valid ivars and reasonable defaults.
        valid = dict(
            ignore_case=False,
            node_only=False,
            pattern_match=False,
            search_body=True,
            search_headline=True,
            suboutline_only=False,  # Seems safest.  # Was True !!!
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
                else:  # pragma: no cover
                    g.trace("bad value: {ivar!r} = {val!r}")
                    errors += 1
            else:  # pragma: no cover
                g.trace(f"ignoring {ivar!r} setting")
                errors += 1
        if errors:  # pragma: no cover
            g.printObj(sorted(valid.keys()), tag='valid keys')
    #@+node:ekr.20210925161148.1: *3* find.interactive_search_helper
    def interactive_search_helper(self, root=None, settings=None):
        #@+<< docstring: find.interactive_search >>
        #@+node:ekr.20210925161451.1: *4* << docstring: find.interactive_search >>
        """
        Support interactive find.

        c.findCommands.interactive_search_helper starts an interactive search with
        the given settings. The settings argument may be either a g.Bunch or a
        dict.

        Example 1, settings is a g.Bunch:

            c.findCommands.interactive_search_helper(
                root = c.p,
                settings = g.Bunch(
                    find_text = '^(def )',
                    change_text = '\1',
                    pattern_match=True,
                    search_headline=False,
                    whole_word=False,
                )
            )
            
        Example 2, settings is a python dict:
            
            c.findCommands.interactive_search_helper(
                root = c.p,
                settings = {
                    'find_text': '^(def )',
                    'change_text': '\1',
                    'pattern_match': True,
                    'search_headline': False,
                    'whole_word': False,
                }
            )
        """
        #@-<< docstring: find.interactive_search >>
        # Merge settings into default settings.
        c = self.c
        d = self.default_settings()  # A g.bunch
        if settings:
            # Settings can be a dict or a g.Bunch.
            # g.Bunch has no update method.
            for key in settings.keys():
                d[key] = settings[key]
        self.ftm.set_widgets_from_dict(d)  # So the *next* find-next will work.
        self.show_find_options_in_status_area()
        if not self.check_args('find-next'):
            return
        if root:
            c.selectPosition(root)
        self.do_find_next(d)
    #@+node:ekr.20031218072017.3055: *3* LeoFind.Commands (immediate execution)
    #@+node:ekr.20031218072017.3062: *4* find.change-then-find & helper
    @cmd('replace-then-find')
    @cmd('change-then-find')
    def change_then_find(self, event=None):  # pragma: no cover (cmd)
        """Handle the replace-then-find command."""
        # Settings...
        self.init_in_headline()
        settings = self.ftm.get_settings()
        self.do_change_then_find(settings)
    #@+node:ekr.20210114100105.1: *5* find.do_change_then_find
    # A stand-alone method for unit testing.
    def do_change_then_find(self, settings):
        """
        Do the change-then-find command from settings.

        This is a stand-alone method for unit testing.
        """
        p = self.c.p
        self.init_ivars_from_settings(settings)
        if not self.check_args('change-then-find'):
            return False
        if self.change_selection(p):
            self.do_find_next(settings)
        return True

    #@+node:ekr.20160224175312.1: *4* find.clone-find_marked & helper
    @cmd('clone-find-all-marked')
    @cmd('cfam')
    def cloneFindAllMarked(self, event=None):
        """
        clone-find-all-marked, aka cfam.

        Create an organizer node whose descendants contain clones of all marked
        nodes. The list is *not* flattened: clones appear only once in the
        descendants of the organizer node.
        """
        self.do_find_marked(flatten=False)

    @cmd('clone-find-all-flattened-marked')
    @cmd('cffm')
    def cloneFindAllFlattenedMarked(self, event=None):
        """
        clone-find-all-flattened-marked, aka cffm.

        Create an organizer node whose direct children are clones of all marked
        nodes. The list is flattened: every cloned node appears as a direct
        child of the organizer node, even if the clone also is a descendant of
        another cloned node.
        """
        self.do_find_marked(flatten=True)
    #@+node:ekr.20161022121036.1: *5* find.do_find_marked
    def do_find_marked(self, flatten):
        """
        Helper for clone-find-marked commands.

        This is a stand-alone method for unit testing.
        """
        c = self.c

        def isMarked(p):
            return p.isMarked()

        root = c.cloneFindByPredicate(
            generator=c.all_unique_positions,
            predicate=isMarked,
            failMsg='No marked nodes',
            flatten=flatten,
            undoType='clone-find-marked',
        )
        if root:
            # Unmarking all nodes is convenient.
            for v in c.all_unique_nodes():
                if v.isMarked():
                    v.clearMarked()
            n = root.numberOfChildren()
            root.b = f"# Found {n} marked node{g.plural(n)}"
            c.selectPosition(root)
            c.redraw(root)
        return bool(root)
    #@+node:ekr.20140828080010.18532: *4* find.clone-find-parents
    @cmd('clone-find-parents')
    def cloneFindParents(self, event=None):
        """
        Create an organizer node whose direct children are clones of all
        parents of the selected node, which must be a clone.
        """
        c, u = self.c, self.c.undoer
        p = c.p
        if not p:  # pragma: no cover
            return False
        if not p.isCloned():  # pragma: no cover
            g.es(f"not a clone: {p.h}")
            return False
        p0 = p.copy()
        undoType = 'Find Clone Parents'
        aList = c.vnode2allPositions(p.v)
        if not aList:  # pragma: no cover
            g.trace('can not happen: no parents')
            return False
        # Create the node as the last top-level node.
        # All existing positions remain valid.
        u.beforeChangeGroup(p, undoType)
        b = u.beforeInsertNode(p)
        found = c.lastTopLevel().insertAfter()
        found.h = f"Found: parents of {p.h}"
        u.afterInsertNode(found, 'insert', b)
        seen = []
        for p2 in aList:
            parent = p2.parent()
            if parent and parent.v not in seen:
                seen.append(parent.v)
                b = u.beforeCloneNode(parent)
                # Bug fix 2021/06/15: Create the clone directly as a child of found.
                clone = p.copy()
                n = found.numberOfChildren()
                clone._linkCopiedAsNthChild(found, n)
                u.afterCloneNode(clone, 'clone', b)
        u.afterChangeGroup(p0, undoType)
        c.setChanged()
        c.redraw(found)
        return True
    #@+node:ekr.20150629084204.1: *4* find.find-def, do_find_def & helpers
    @cmd('find-def')
    def find_def(self, event=None, strict=False):  # pragma: no cover (cmd)
        """Find the def or class under the cursor."""
        ftm, p = self.ftm, self.c.p
        # Check.
        word = self._compute_find_def_word(event)
        if not word:
            return
        # Settings...
        prefix = 'class' if word[0].isupper() else 'def'
        find_pattern = prefix + ' ' + word
        ftm.set_find_text(find_pattern)
        self._save_before_find_def(p)  # Save previous settings.
        self.init_vim_search(find_pattern)
        self.update_change_list(self.change_text)  # Optional. An edge case.
        # Do the command!
        settings = self._compute_find_def_settings(find_pattern)
        self.do_find_def(settings, word, strict)

    def find_def_strict(self, event=None):  #pragma: no cover (cmd)
        """Same as find_def, but don't call _switch_style."""
        self.find_def(event=event, strict=True)

    def do_find_def(self, settings, word, strict):
        """A standalone helper for unit tests."""
        return self._fd_helper(settings, word, def_flag=True, strict=strict)

    #@+node:ekr.20210114202757.1: *5* find._compute_find_def_settings
    def _compute_find_def_settings(self, find_pattern):

        settings = self.default_settings()
        table = (
            ('change_text', ''),
            ('find_text', find_pattern),
            ('ignore_case', False),
            ('pattern_match', False),
            ('reverse', False),
            ('search_body', True),
            ('search_headline', False),
            ('whole_word', True),
        )
        for attr, val in table:
            # Guard against renamings & misspellings.
            assert hasattr(self, attr), attr
            assert attr in settings.__dict__, attr
            # Set the values.
            setattr(self, attr, val)
            settings[attr] = val
        return settings
    #@+node:ekr.20150629084611.1: *5* find._compute_find_def_word
    def _compute_find_def_word(self, event):  # pragma: no cover (cmd)
        """Init the find-def command. Return the word to find or None."""
        c = self.c
        w = c.frame.body.wrapper
        # First get the word.
        c.bodyWantsFocusNow()
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
    #@+node:ekr.20150629125733.1: *5* find._fd_helper
    def _fd_helper(self, settings, word, def_flag, strict):
        """
        Find the definition of the class, def or var under the cursor.

        return p, pos, newpos for unit tests.
        """
        c, find, ftm = self.c, self, self.ftm
        #
        # Recompute find_text for unit tests.
        if def_flag:
            prefix = 'class' if word[0].isupper() else 'def'
            self.find_text = settings.find_text = prefix + ' ' + word
        else:
            self.find_text = settings.find_text = word + ' ='
        # g.printObj(settings, tag='_fd_helper: settings')
        #
        # Just search body text.
        self.search_headline = False
        self.search_body = True
        w = c.frame.body.wrapper
        # Check.
        if not w:  # pragma: no cover
            return None, None, None
        save_sel = w.getSelectionRange()
        ins = w.getInsertPoint()
        old_p = c.p
        if self.reverse_find_defs:
            # #2161: start at the last position.
            p = c.lastPosition()
        else:
            # Start in the root position.
            p = c.rootPosition()
        # Required.
        c.selectPosition(p)
        c.redraw()
        c.bodyWantsFocusNow()
        # #1592.  Ignore hits under control of @nosearch
        try:
            # #2161:
            old_reverse = self.reverse
            self.reverse = self.reverse_find_defs
            # # 2288:
            self.work_s = p.b
            if self.reverse_find_defs:
                self.work_sel = (len(p.b), len(p.b), len(p.b))
            else:
                self.work_sel = (0, 0, 0)
            while True:
                p, pos, newpos = self.find_next_match(p)
                found = pos is not None
                if found or not g.inAtNosearch(p):  # do *not* use c.p.
                    break
            if not found and def_flag and not strict:
                # Leo 5.7.3: Look for an alternative defintion of function/methods.
                word2 = self._switch_style(word)
                if self.reverse_find_defs:
                    # #2161: start at the last position.
                    p = c.lastPosition()
                else:
                    p = c.rootPosition()
                if word2:
                    find_pattern = prefix + ' ' + word2
                    find.find_text = find_pattern
                    ftm.set_find_text(find_pattern)
                    # #1592.  Ignore hits under control of @nosearch
                    while True:
                        p, pos, newpos = self.find_next_match(p)
                        found = pos is not None
                        if not found or not g.inAtNosearch(p):
                            break
        finally:
            self.reverse = old_reverse
        if found:
            c.redraw(p)
            w.setSelectionRange(pos, newpos, insert=newpos)
            c.bodyWantsFocusNow()
            return p, pos, newpos
        self._restore_after_find_def()  # Avoid massive confusion!
        i, j = save_sel
        c.redraw(old_p)
        w.setSelectionRange(i, j, insert=ins)
        c.bodyWantsFocusNow()
        return None, None, None
    #@+node:ekr.20150629095511.1: *5* find._restore_after_find_def
    def _restore_after_find_def(self):
        """Restore find settings in effect before a find-def command."""
        # pylint: disable=no-member
        b = self.find_def_data  # A g.Bunch
        if b:
            self.ignore_case = b.ignore_case
            self.pattern_match = b.pattern_match
            self.search_body = b.search_body
            self.search_headline = b.search_headline
            self.whole_word = b.whole_word
            self.find_def_data = None
    #@+node:ekr.20150629095633.1: *5* find._save_before_find_def
    def _save_before_find_def(self, p):
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
    #@+node:ekr.20180511045458.1: *5* find._switch_style
    def _switch_style(self, word):
        """
        Switch between camelCase and underscore_style function defintiions.
        Return None if there would be no change.
        """
        s = word
        if not s:
            return None
        if s[0].isupper():
            return None  # Don't convert class names.
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
    #@+node:ekr.20031218072017.3063: *4* find.find-next, find-prev & do_find_*
    @cmd('find-next')
    def find_next(self, event=None):  # pragma: no cover (cmd)
        """The find-next command."""
        # Settings...
        self.reverse = False
        self.init_in_headline()  # Do this *before* creating the settings.
        settings = self.ftm.get_settings()
        # Do the command!
        self.do_find_next(settings)

    @cmd('find-prev')
    def find_prev(self, event=None):  # pragma: no cover (cmd)
        """Handle F2 (find-previous)"""
        # Settings...
        self.init_in_headline()  # Do this *before* creating the settings.
        settings = self.ftm.get_settings()
        # Do the command!
        self.do_find_prev(settings)
    #@+node:ekr.20031218072017.3074: *5* find.do_find_next & do_find_prev
    def do_find_prev(self, settings):
        """Find the previous instance of self.find_text."""
        self.request_reverse = True
        return self.do_find_next(settings)

    def do_find_next(self, settings):
        """
        Find the next instance of self.find_text.

        Return True (for vim-mode) if a match was found.

        """
        c, p = self.c, self.c.p
        #
        # The gui widget may not exist for headlines.
        gui_w = c.edit_widget(p) if self.in_headline else c.frame.body.wrapper
        #
        # Init the work widget, so we don't get stuck.
        s = p.h if self.in_headline else p.b
        ins = gui_w.getInsertPoint() if gui_w else 0
        self.work_s = s
        self.work_sel = (ins, ins, ins)
        #
        # Set the settings *after* initing the search.
        self.init_ivars_from_settings(settings)
        #
        # Honor delayed requests.
        for ivar in ('reverse', 'pattern_match', 'whole_word'):
            request = 'request_' + ivar
            val = getattr(self, request)
            if val:  # Only *set* the ivar!
                setattr(self, ivar, val)  # Set the ivar.
                setattr(self, request, False)  # Clear the request!
        #
        # Leo 6.4: set/clear self.root
        if self.root:  # pragma: no cover
            if p != self.root and not self.root.isAncestorOf(p):
                # p is outside of self.root's tree.
                # Clear suboutline-only.
                self.root = None
                self.suboutline_only = False
                self.set_find_scope_every_where()  # Update find-tab & status area.
        elif self.suboutline_only:
            # Start the range and set suboutline-only.
            self.root = c.p
            self.set_find_scope_suboutline_only()  # Update find-tab & status area.
        #
        # Now check the args.
        tag = 'find-prev' if self.reverse else 'find-next'
        if not self.check_args(tag):  # Issues error message.
            return None, None, None
        data = self.save()
        p, pos, newpos = self.find_next_match(p)
        found = pos is not None
        if found:
            self.show_success(p, pos, newpos)
        else:
            # Restore previous position.
            self.restore(data)
        self.show_status(found)
        return p, pos, newpos
    #@+node:ekr.20131117164142.17015: *4* find.find-tab-hide
    @cmd('find-tab-hide')
    def hide_find_tab(self, event=None):  # pragma: no cover (cmd)
        """Hide the Find tab."""
        c = self.c
        if self.minibuffer_mode:
            c.k.keyboardQuit()
        else:
            self.c.frame.log.selectTab('Log')
    #@+node:ekr.20131117164142.16916: *4* find.find-tab-open
    @cmd('find-tab-open')
    def open_find_tab(self, event=None, show=True):  # pragma: no cover (cmd)
        """Open the Find tab in the log pane."""
        c = self.c
        if c.config.getBool('use-find-dialog', default=True):
            g.app.gui.openFindDialog(c)
        else:
            c.frame.log.selectTab('Find')
    #@+node:ekr.20210118003803.1: *4* find.find-var & do_find_var
    @cmd('find-var')
    def find_var(self, event=None):  # pragma: no cover (cmd)
        """Find the var under the cursor."""
        ftm, p = self.ftm, self.c.p
        # Check...
        word = self._compute_find_def_word(event)
        if not word:
            return
        # Settings...
        self.find_pattern = find_pattern = word + ' ='
        ftm.set_find_text(find_pattern)
        self._save_before_find_def(p)  # Save previous settings.
        self.init_vim_search(find_pattern)
        self.update_change_list(self.change_text)  # Optional. An edge case.
        settings = self._compute_find_def_settings(find_pattern)
        # Do the command!
        self.do_find_var(settings, word)

    def do_find_var(self, settings, word):
        """A standalone helper for unit tests."""
        return self._fd_helper(settings, word, def_flag=False, strict=False)
    #@+node:ekr.20141113094129.6: *4* find.focus-to-find
    @cmd('focus-to-find')
    def focus_to_find(self, event=None):  # pragma: no cover (cmd)
        c = self.c
        if c.config.getBool('use-find-dialog', default=True):
            g.app.gui.openFindDialog(c)
        else:
            c.frame.log.selectTab('Find')
    #@+node:ekr.20031218072017.3068: *4* find.replace
    @cmd('replace')
    @cmd('change')
    def change(self, event=None):  # pragma: no cover (cmd)
        """Replace the selected text with the replacement text."""
        p = self.c.p
        if self.check_args('replace'):
            self.init_in_headline()
            self.change_selection(p)

    replace = change
    #@+node:ekr.20131117164142.17019: *4* find.set-find-*
    @cmd('set-find-everywhere')
    def set_find_scope_every_where(self, event=None):  # pragma: no cover (cmd)
        """Set the 'Entire Outline' radio button in the Find tab."""
        return self.set_find_scope('entire-outline')

    @cmd('set-find-node-only')
    def set_find_scope_node_only(self, event=None):  # pragma: no cover (cmd)
        """Set the 'Node Only' radio button in the Find tab."""
        return self.set_find_scope('node-only')

    @cmd('set-find-suboutline-only')
    def set_find_scope_suboutline_only(self, event=None):
        """Set the 'Suboutline Only' radio button in the Find tab."""
        return self.set_find_scope('suboutline-only')

    def set_find_scope(self, where):
        """Set the radio buttons to the given scope"""
        c, fc = self.c, self.c.findCommands
        self.ftm.set_radio_button(where)
        options = fc.compute_find_options_in_status_area()
        c.frame.statusLine.put(options)
    #@+node:ekr.20131117164142.16989: *4* find.show-find-options
    @cmd('show-find-options')
    def show_find_options(self, event=None):  # pragma: no cover (cmd)
        """
        Show the present find options in the status line.
        This is useful for commands like search-forward that do not show the Find Panel.
        """
        frame = self.c.frame
        frame.clearStatusLine()
        part1, part2 = self.compute_find_options()
        frame.putStatusLine(part1, bg='blue')
        frame.putStatusLine(part2)
    #@+node:ekr.20171129205648.1: *5* LeoFind.compute_find_options
    def compute_find_options(self):  # pragma: no cover (cmd)
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
        if regex:
            z.append('regex')
        table = (
            ('reverse', 'reverse'),
            ('ignore_case', 'noCase'),
            ('whole_word', 'word'),
            # ('wrap', 'wrap'),
            ('mark_changes', 'markChg'),
            ('mark_finds', 'markFnd'),
        )
        for ivar, s in table:
            val = getattr(self, ivar)
            if val:
                z.append(s)
        part2 = ' '.join(z)
        return part1, part2
    #@+node:ekr.20131117164142.16919: *4* find.toggle-find-*
    @cmd('toggle-find-collapses-nodes')
    def toggle_find_collapes_nodes(self, event):  # pragma: no cover (cmd)
        """Toggle the 'Collapse Nodes' checkbox in the find tab."""
        c = self.c
        c.sparse_find = not c.sparse_find
        if not g.unitTesting:
            g.es('sparse_find', c.sparse_find)

    @cmd('toggle-find-ignore-case-option')
    def toggle_ignore_case_option(self, event):  # pragma: no cover (cmd)
        """Toggle the 'Ignore Case' checkbox in the Find tab."""
        return self.toggle_option('ignore_case')

    @cmd('toggle-find-mark-changes-option')
    def toggle_mark_changes_option(self, event):  # pragma: no cover (cmd)
        """Toggle the 'Mark Changes' checkbox in the Find tab."""
        return self.toggle_option('mark_changes')

    @cmd('toggle-find-mark-finds-option')
    def toggle_mark_finds_option(self, event):  # pragma: no cover (cmd)
        """Toggle the 'Mark Finds' checkbox in the Find tab."""
        return self.toggle_option('mark_finds')

    @cmd('toggle-find-regex-option')
    def toggle_regex_option(self, event):  # pragma: no cover (cmd)
        """Toggle the 'Regexp' checkbox in the Find tab."""
        return self.toggle_option('pattern_match')

    @cmd('toggle-find-in-body-option')
    def toggle_search_body_option(self, event):  # pragma: no cover (cmd)
        """Set the 'Search Body' checkbox in the Find tab."""
        return self.toggle_option('search_body')

    @cmd('toggle-find-in-headline-option')
    def toggle_search_headline_option(self, event):  # pragma: no cover (cmd)
        """Toggle the 'Search Headline' checkbox in the Find tab."""
        return self.toggle_option('search_headline')

    @cmd('toggle-find-word-option')
    def toggle_whole_word_option(self, event):  # pragma: no cover (cmd)
        """Toggle the 'Whole Word' checkbox in the Find tab."""
        return self.toggle_option('whole_word')

    # @cmd('toggle-find-wrap-around-option')
    # def toggleWrapSearchOption(self, event):
        # """Toggle the 'Wrap Around' checkbox in the Find tab."""
        # return self.toggle_option('wrap')

    def toggle_option(self, checkbox_name):  # pragma: no cover (cmd)
        c, fc = self.c, self.c.findCommands
        self.ftm.toggle_checkbox(checkbox_name)
        options = fc.compute_find_options_in_status_area()
        c.frame.statusLine.put(options)
    #@+node:ekr.20131117164142.17013: *3* LeoFind.Commands (interactive)
    #@+node:ekr.20131117164142.16994: *4* find.change-all & helper
    @cmd('change-all')
    @cmd('replace-all')
    def interactive_change_all(self, event=None):  # pragma: no cover (interactive)
        """Replace all instances of the search string with the replacement string."""
        self.ftm.clear_focus()
        self.ftm.set_entry_focus()
        prompt = 'Replace Regex: ' if self.pattern_match else 'Replace: '
        self.start_state_machine(event, prompt,
            handler=self.interactive_replace_all1,
            # Allow either '\t' or '\n' to switch to the change text.
            escape_handler=self.interactive_replace_all1,
        )

    def interactive_replace_all1(self, event):  # pragma: no cover (interactive)
        k = self.k
        find_pattern = k.arg
        self._sString = k.arg
        self.update_find_list(k.arg)
        regex = ' Regex' if self.pattern_match else ''
        prompt = f"Replace{regex}: {find_pattern} With: "
        k.setLabelBlue(prompt)
        self.add_change_string_to_label()
        k.getNextArg(self.interactive_replace_all2)

    def interactive_replace_all2(self, event):  # pragma: no cover (interactive)
        c, k, w = self.c, self.k, self.c.frame.body.wrapper

        # Update settings data.
        find_pattern = self._sString
        change_pattern = k.arg
        self.init_vim_search(find_pattern)
        self.update_change_list(change_pattern)
        # Compute settings...
        self.ftm.set_find_text(find_pattern)
        self.ftm.set_change_text(change_pattern)
        settings = self.ftm.get_settings()
        # Gui...
        k.clearState()
        k.resetLabel()
        k.showStateAndMode()
        c.widgetWantsFocusNow(w)
        # Do the command!
        self.do_change_all(settings)
    #@+node:ekr.20131117164142.17016: *5* find.do_change_all & helpers
    def do_change_all(self, settings):
        c = self.c
        # Settings...
        self.init_ivars_from_settings(settings)
        if not self.check_args('change-all'):
            return 0
        n = self._change_all_helper(settings)
        #
        # Bugs #947, #880 and #722:
        # Set ancestor @<file> nodes by brute force.
        for p in c.all_positions():  # pragma: no cover
            if (
                p.anyAtFileNodeName()
                and not p.v.isDirty()
                and any(p2.v.isDirty() for p2 in p.subtree())
            ):
                p.setDirty()
        c.redraw()
        return n
    #@+node:ekr.20031218072017.3069: *6* find._change_all_helper
    def _change_all_helper(self, settings):
        """Do the change-all command. Return the number of changes, or 0 for error."""
        # Caller has checked settings.

        c, current, u = self.c, self.c.p, self.c.undoer
        undoType = 'Replace All'
        t1 = time.process_time()
        if not self.check_args('change-all'):  # pragma: no cover
            return 0
        self.init_in_headline()
        saveData = self.save()
        self.in_headline = self.search_headline  # Search headlines first.
        # Remember the start of the search.
        p = self.root = c.p.copy()
        # Set the work widget.
        s = p.h if self.in_headline else p.b
        ins = len(s) if self.reverse else 0
        self.work_s = s
        self.work_sel = (ins, ins, ins)
        count = 0
        u.beforeChangeGroup(current, undoType)
        # Fix bug 338172: ReplaceAll will not replace newlines
        # indicated as \n in target string.
        if not self.find_text:  # pragma: no cover
            return 0
        if not self.search_headline and not self.search_body:  # pragma: no cover
            return 0
        self.change_text = self.replace_back_slashes(self.change_text)
        if self.pattern_match:
            ok = self.precompile_pattern()
            if not ok:
                return 0
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
                count_h, new_h = self._change_all_search_and_replace(p.h)
                if count_h:
                    count += count_h
                    p.h = new_h
            if self.search_body:
                count_b, new_b = self._change_all_search_and_replace(p.b)
                if count_b:
                    count += count_b
                    p.b = new_b
            if count_h or count_b:
                u.afterChangeNodeContents(p, 'Replace All', undoData)
        self.ftm.set_radio_button('entire-outline')
        # suboutline-only is a one-shot for batch commands.
        self.root = None
        self.node_only = self.suboutline_only = False
        p = c.p
        u.afterChangeGroup(p, undoType, reportFlag=True)
        t2 = time.process_time()
        if not g.unitTesting:  # pragma: no cover
            g.es_print(
                f"changed {count} instances{g.plural(count)} "
                f"in {t2 - t1:4.2f} sec.")
        c.recolor()
        c.redraw(p)
        self.restore(saveData)
        return count
    #@+node:ekr.20190602134414.1: *6* find._change_all_search_and_replace & helpers
    def _change_all_search_and_replace(self, s):
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
            return self._change_all_regex(s)
        if self.whole_word:
            return self._change_all_word(s)
        return self._change_all_plain(s)
    #@+node:ekr.20190602151043.4: *7* find._change_all_plain
    def _change_all_plain(self, s):
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
    #@+node:ekr.20190602151043.2: *7* find._change_all_regex
    def _change_all_regex(self, s):
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
    #@+node:ekr.20190602155933.1: *7* find._change_all_word
    def _change_all_word(self, s):
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
    #@+node:ekr.20210110073117.23: *6* new:find.replace_all_helper & helpers (merge & delete)
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
    #@+node:ekr.20210110073117.24: *7* new:find.batch_plain_replace
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
    #@+node:ekr.20210110073117.25: *7* new:find.batch_regex_replace
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
    #@+node:ekr.20210110073117.26: *7* new:find.batch_word_replace
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
    #@+node:ekr.20131117164142.17011: *4* find.clone-find-all & helper
    @cmd('clone-find-all')
    @cmd('find-clone-all')
    @cmd('cfa')
    def interactive_clone_find_all(
        self, event=None, preloaded=None):  # pragma: no cover (interactive)
        """
        clone-find-all ( aka find-clone-all and cfa).

        Create an organizer node whose descendants contain clones of all nodes
        matching the search string, except @nosearch trees.

        The list is *not* flattened: clones appear only once in the
        descendants of the organizer node.
        """
        w = self.c.frame.body.wrapper
        if not w:
            return
        if not preloaded:
            self.preload_find_pattern(w)
        self.start_state_machine(event,
            prefix='Clone Find All: ',
            handler=self.interactive_clone_find_all1)

    def interactive_clone_find_all1(self, event):  # pragma: no cover (interactive)
        c, k, w = self.c, self.k, self.c.frame.body.wrapper
        # Settings...
        pattern = k.arg
        self.ftm.set_find_text(pattern)
        self.init_vim_search(pattern)
        self.init_in_headline()
        settings = self.ftm.get_settings()
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
    #@+node:ekr.20210114094846.1: *5* find.do_clone_find_all
    # A stand-alone method for unit testing.
    def do_clone_find_all(self, settings):
        """
        Do the clone-all-find commands from settings.

        Return the count of found nodes.

        This is a stand-alone method for unit testing.
        """
        self.init_ivars_from_settings(settings)
        if not self.check_args('clone-find-all'):
            return 0
        return self._cf_helper(settings, flatten=False)
    #@+node:ekr.20131117164142.16996: *4* find.clone-find-all-flattened & helper
    @cmd('clone-find-all-flattened')
    # @cmd('find-clone-all-flattened')
    @cmd('cff')
    def interactive_cff(
        self, event=None, preloaded=None):  # pragma: no cover (interactive)
        """
        clone-find-all-flattened (aka find-clone-all-flattened and cff).

        Create an organizer node whose direct children are clones of all nodes
        matching the search string, except @nosearch trees.

        The list is flattened: every cloned node appears as a direct child
        of the organizer node, even if the clone also is a descendant of
        another cloned node.
        """
        w = self.c.frame.body.wrapper
        if not w:
            return
        if not preloaded:
            self.preload_find_pattern(w)
        self.start_state_machine(event,
            prefix='Clone Find All Flattened: ',
            handler=self.interactive_cff1)

    def interactive_cff1(self, event):  # pragma: no cover (interactive)
        c, k, w = self.c, self.k, self.c.frame.body.wrapper
        # Settings...
        pattern = k.arg
        self.ftm.set_find_text(pattern)
        self.init_vim_search(pattern)
        self.init_in_headline()
        settings = self.ftm.get_settings()
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
    #@+node:ekr.20210114094944.1: *5* find.do_clone_find_all_flattened
    # A stand-alone method for unit testing.
    def do_clone_find_all_flattened(self, settings):
        """
        Do the clone-find-all-flattened command from the settings.

        Return the count of found nodes.

        This is a stand-alone method for unit testing.
        """
        self.init_ivars_from_settings(settings)
        if self.check_args('clone-find-all-flattened'):
            return self._cf_helper(settings, flatten=True)
        return 0
    #@+node:ekr.20160920110324.1: *4* find.clone-find-tag & helper
    @cmd('clone-find-tag')
    @cmd('find-clone-tag')
    @cmd('cft')
    def interactive_clone_find_tag(self, event=None):  # pragma: no cover (interactive)
        """
        clone-find-tag (aka find-clone-tag and cft).

        Create an organizer node whose descendants contain clones of all
        nodes matching the given tag, except @nosearch trees.

        The list is *always* flattened: every cloned node appears as a
        direct child of the organizer node, even if the clone also is a
        descendant of another cloned node.
        """
        w = self.c.frame.body.wrapper
        if w:
            self.start_state_machine(event,
                prefix='Clone Find Tag: ',
                handler=self.interactive_clone_find_tag1)

    def interactive_clone_find_tag1(self, event):  # pragma: no cover (interactive)
        c, k = self.c, self.k
        # Settings...
        self.find_text = tag = k.arg
        # Gui...
        k.clearState()
        k.resetLabel()
        k.showStateAndMode()
        self.do_clone_find_tag(tag)
        c.treeWantsFocus()
    #@+node:ekr.20210110073117.11: *5* find.do_clone_find_tag & helper
    # A stand-alone method for unit tests.
    def do_clone_find_tag(self, tag):
        """
        Do the clone-all-find commands from settings.
        Return (len(clones), found) for unit tests.
        """
        c, u = self.c, self.c.undoer
        tc = getattr(c, 'theTagController', None)
        if not tc:
            if not g.unitTesting:  # pragma: no cover (skip)
                g.es_print('nodetags not active')
            return 0, c.p
        clones = tc.get_tagged_nodes(tag)
        if not clones:
            if not g.unitTesting:  # pragma: no cover (skip)
                g.es_print(f"tag not found: {tag}")
            tc.show_all_tags()
            return 0, c.p
        undoData = u.beforeInsertNode(c.p)
        found = self._create_clone_tag_nodes(clones)
        u.afterInsertNode(found, 'Clone Find Tag', undoData)
        assert c.positionExists(found, trace=True), found
        c.setChanged()
        c.selectPosition(found)
        c.redraw()
        return len(clones), found
    #@+node:ekr.20210110073117.12: *6* find._create_clone_tag_nodes
    def _create_clone_tag_nodes(self, clones):
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
    #@+node:ekr.20131117164142.16998: *4* find.find-all & helper
    @cmd('find-all')
    def interactive_find_all(self, event=None):  # pragma: no cover (interactive)
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

    def interactive_find_all1(self, event=None):  # pragma: no cover (interactive)
        k = self.k
        # Settings.
        find_pattern = k.arg
        self.ftm.set_find_text(find_pattern)
        settings = self.ftm.get_settings()
        self.find_text = find_pattern
        self.change_text = self.ftm.get_change_text()
        self.update_find_list(find_pattern)
        # Gui...
        k.clearState()
        k.resetLabel()
        k.showStateAndMode()
        self.do_find_all(settings)

    def find_all_escape_handler(self, event):  # pragma: no cover (interactive)
        k = self.k
        prompt = 'Replace ' + ('Regex' if self.pattern_match else 'String')
        find_pattern = k.arg
        self._sString = k.arg
        self.update_find_list(k.arg)
        s = f"{prompt}: {find_pattern} With: "
        k.setLabelBlue(s)
        self.add_change_string_to_label()
        k.getNextArg(self.find_all_escape_handler2)

    def find_all_escape_handler2(self, event):  # pragma: no cover (interactive)
        c, k, w = self.c, self.k, self.c.frame.body.wrapper
        find_pattern = self._sString
        change_pattern = k.arg
        self.update_change_list(change_pattern)
        self.ftm.set_find_text(find_pattern)
        self.ftm.set_change_text(change_pattern)
        self.init_vim_search(find_pattern)
        self.init_in_headline()
        settings = self.ftm.get_settings()
        # Gui...
        k.clearState()
        k.resetLabel()
        k.showStateAndMode()
        c.widgetWantsFocusNow(w)
        self.do_change_all(settings)
    #@+node:ekr.20031218072017.3073: *5* find.do_find_all & helpers
    def do_find_all(self, settings):
        """Top-level helper for find-all command."""
        c = self.c
        count = 0
        self.init_ivars_from_settings(settings)
        if not self.check_args('find-all'):  # pragma: no cover
            return count
        # Init data.
        self.init_in_headline()
        data = self.save()
        self.in_headline = self.search_headline  # Search headlines first.
        self.unique_matches = set()  # 2021/02/20.
        # Remember the start of the search.
        p = self.root = c.p.copy()
        # Set the work widget.
        s = p.h if self.in_headline else p.b
        ins = len(s) if self.reverse else 0
        self.work_s = s
        self.work_sel = (ins, ins, ins)
        if self.pattern_match:
            ok = self.precompile_pattern()
            if not ok:  # pragma: no cover
                return count
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
            count = self._find_all_helper(after, data, p, 'Find All')
            c.contractAllHeadlines()
        finally:
            c.sparse_find = old_sparse_find
            self.root = None
        if count:
            c.redraw()
        g.es("found", count, "matches for", self.find_text)
        return count
    #@+node:ekr.20160422073500.1: *6* find._find_all_helper
    def _find_all_helper(self, after, data, p, undoType):
        """Handle the find-all command from p to after."""
        c, log, u = self.c, self.c.frame.log, self.c.undoer

        def put_link(line, line_number, p):  # pragma: no cover  # #2023
            """Put a link to the given line at the given line_number in p.h."""

            if g.unitTesting:
                return
            unl = p.get_UNL()
            if self.in_headline:
                line_number = 1
            log.put(line.strip() + '\n', nodeLink=f"{unl}::{line_number}")  # Local line.

        seen = []  # List of (vnode, pos).
        both = self.search_body and self.search_headline
        count, found, result = 0, None, []
        while 1:
            p, pos, newpos = self.find_next_match(p)
            if pos is None:
                break
            if (p.v, pos) in seen:  # 2076
                continue  # pragma: no cover
            seen.append((p.v, pos))
            count += 1
            s = self.work_s
            i, j = g.getLine(s, pos)
            line = s[i:j]
            row, col = g.convertPythonIndexToRowCol(s, i)
            line_number = row + 1
            if self.findAllUniqueFlag:
                m = self.match_obj
                if m:
                    self.unique_matches.add(m.group(0).strip())
                    put_link(line, line_number, p)  # #2023
            elif both:
                result.append('%s%s\n%s%s\n' % (
                    '-' * 20, p.h,
                    "head: " if self.in_headline else "body: ",
                    line.rstrip() + '\n'))
                put_link(line, line_number, p)  # #2023
            elif p.isVisited():
                result.append(line.rstrip() + '\n')
                put_link(line, line_number, p)  # #2023
            else:
                result.append('%s%s\n%s' % ('-' * 20, p.h, line.rstrip() + '\n'))
                put_link(line, line_number, p)  # #2023
                p.setVisited()
        if result or self.unique_matches:
            undoData = u.beforeInsertNode(c.p)
            if self.findAllUniqueFlag:
                found = self._create_find_unique_node()
                count = len(list(self.unique_matches))
            else:
                found = self._create_find_all_node(result)
            u.afterInsertNode(found, undoType, undoData)
            c.selectPosition(found)
            c.setChanged()
        else:
            self.restore(data)
        return count
    #@+node:ekr.20150717105329.1: *6* find._create_find_all_node
    def _create_find_all_node(self, result):
        """Create a "Found All" node as the last node of the outline."""
        c = self.c
        found = c.lastTopLevel().insertAfter()
        assert found
        found.h = f"Found All:{self.find_text}"
        status = self.compute_result_status(find_all_flag=True)
        status = status.strip().lstrip('(').rstrip(')').strip()
        found.b = f"# {status}\n{''.join(result)}"
        return found
    #@+node:ekr.20171226143621.1: *6* find._create_find_unique_node
    def _create_find_unique_node(self):
        """Create a "Found Unique" node as the last node of the outline."""
        c = self.c
        found = c.lastTopLevel().insertAfter()
        assert found
        found.h = f"Found Unique Regex:{self.find_text}"
        result = sorted(self.unique_matches)
        found.b = '\n'.join(result)
        return found
    #@+node:ekr.20171226140643.1: *4* find.find-all-unique-regex
    @cmd('find-all-unique-regex')
    def interactive_find_all_unique_regex(
        self, event=None):  # pragma: no cover (interactive)
        """
        Create a summary node containing all unique matches of the regex search
        string. This command shows only the matched string itself.
        """
        self.ftm.clear_focus()
        self.match_obj = None
        self.changeAllFlag = False
        self.findAllUniqueFlag = True
        self.ftm.set_entry_focus()
        self.start_state_machine(event,
            prefix='Search Unique Regex: ',
            handler=self.interactive_find_all_unique_regex1,
            escape_handler=self.interactive_change_all_unique_regex1,
        )

    def interactive_find_all_unique_regex1(
        self, event=None):  # pragma: no cover (interactive)
        k = self.k
        # Settings...
        find_pattern = k.arg
        self.update_find_list(find_pattern)
        self.ftm.set_find_text(find_pattern)
        self.init_in_headline()
        settings = self.ftm.get_settings()
        # Gui...
        k.clearState()
        k.resetLabel()
        k.showStateAndMode()
        return self.do_find_all(settings)

    def interactive_change_all_unique_regex1(
        self, event):  # pragma: no cover (interactive)
        k = self.k
        find_pattern = self._sString = k.arg
        self.update_find_list(k.arg)
        s = f"'Replace All Unique Regex': {find_pattern} With: "
        k.setLabelBlue(s)
        self.add_change_string_to_label()
        k.getNextArg(self.interactive_change_all_unique_regex2)

    def interactive_change_all_unique_regex2(
        self, event):  # pragma: no cover (interactive)
        c, k, w = self.c, self.k, self.c.frame.body.wrapper
        find_pattern = self._sString
        change_pattern = k.arg
        self.update_change_list(change_pattern)
        self.ftm.set_find_text(find_pattern)
        self.ftm.set_change_text(change_pattern)
        self.init_vim_search(find_pattern)
        self.init_in_headline()
        settings = self.ftm.get_settings()
        # Gui...
        k.clearState()
        k.resetLabel()
        k.showStateAndMode()
        c.widgetWantsFocusNow(w)
        self.do_change_all(settings)
    #@+node:ekr.20131117164142.17003: *4* find.re-search
    @cmd('re-search')
    @cmd('re-search-forward')
    def interactive_re_search_forward(self, event):  # pragma: no cover (interactive)
        """Same as start-find, with regex."""
        # Set flag for show_find_options.
        self.pattern_match = True
        self.show_find_options()
        # Set flag for do_find_next().
        self.request_pattern_match = True
        # Go.
        self.start_state_machine(event,
            prefix='Regexp Search: ',
            handler=self.start_search1,  # See start-search
            escape_handler=self.start_search_escape1,  # See start-search
        )
    #@+node:ekr.20210112044303.1: *4* find.re-search-backward
    @cmd('re-search-backward')
    def interactive_re_search_backward(self, event):  # pragma: no cover (interactive)
        """Same as start-find, but with regex and in reverse."""
        # Set flags for show_find_options.
        self.reverse = True
        self.pattern_match = True
        self.show_find_options()
        # Set flags for do_find_next().
        self.request_reverse = True
        self.request_pattern_match = True
        # Go.
        self.start_state_machine(event,
            prefix='Regexp Search Backward:',
            handler=self.start_search1,  # See start-search
            escape_handler=self.start_search_escape1,  # See start-search
        )

    #@+node:ekr.20131117164142.17004: *4* find.search_backward
    @cmd('search-backward')
    def interactive_search_backward(self, event):  # pragma: no cover (interactive)
        """Same as start-find, but in reverse."""
        # Set flag for show_find_options.
        self.reverse = True
        self.show_find_options()
        # Set flag for do_find_next().
        self.request_reverse = True
        # Go.
        self.start_state_machine(event,
            prefix='Search Backward: ',
            handler=self.start_search1,  # See start-search
            escape_handler=self.start_search_escape1,  # See start-search
        )
    #@+node:ekr.20131119060731.22452: *4* find.start-search (Ctrl-F) & common states
    @cmd('start-search')
    @cmd('search-forward')  # Compatibility.
    def start_search(self, event):  # pragma: no cover (interactive)
        """
        The default binding of Ctrl-F.

        Also contains default state-machine entries for find/change commands.
        """
        w = self.c.frame.body.wrapper
        if not w:
            return
        self.preload_find_pattern(w)
        # #1840: headline-only one-shot
        #        Do this first, so the user can override.
        self.ftm.set_body_and_headline_checkbox()
        if self.minibuffer_mode:
            # Set up the state machine.
            self.ftm.clear_focus()
            self.changeAllFlag = False
            self.findAllUniqueFlag = False
            self.ftm.set_entry_focus()
            self.start_state_machine(event,
                prefix='Search: ',
                handler=self.start_search1,
                escape_handler=self.start_search_escape1,
            )
        else:
            self.open_find_tab(event)
            self.ftm.init_focus()
            return

    startSearch = start_search  # Compatibility. Do not delete.
    #@+node:ekr.20210117143611.1: *5* find.start_search1
    def start_search1(self, event=None):  # pragma: no cover
        """Common handler for use by vim commands and other find commands."""
        c, k, w = self.c, self.k, self.c.frame.body.wrapper
        # Settings...
        find_pattern = k.arg
        self.ftm.set_find_text(find_pattern)
        self.update_find_list(find_pattern)
        self.init_vim_search(find_pattern)
        self.init_in_headline()  # Required.
        settings = self.ftm.get_settings()
        # Gui...
        k.clearState()
        k.resetLabel()
        k.showStateAndMode()
        c.widgetWantsFocusNow(w)
        # Do the command!
        self.do_find_next(settings)  # Handles reverse.
    #@+node:ekr.20210117143614.1: *5* find._start_search_escape1
    def start_search_escape1(self, event=None):  # pragma: no cover
        """
        Common escape handler for use by find commands.

        Prompt for a change pattern.
        """
        k = self.k
        self._sString = find_pattern = k.arg
        # Settings.
        k.getArgEscapeFlag = False
        self.ftm.set_find_text(find_pattern)
        self.update_find_list(find_pattern)
        self.find_text = find_pattern
        self.change_text = self.ftm.get_change_text()
        # Gui...
        regex = ' Regex' if self.pattern_match else ''
        backward = ' Backward' if self.reverse else ''
        prompt = f"Replace{regex}{backward}: {find_pattern} With: "
        k.setLabelBlue(prompt)
        self.add_change_string_to_label()
        k.getNextArg(self._start_search_escape2)

    #@+node:ekr.20210117143615.1: *5* find._start_search_escape2
    def _start_search_escape2(self, event):  # pragma: no cover
        c, k, w = self.c, self.k, self.c.frame.body.wrapper
        # Compute settings...
        find_pattern = self._sString
        change_pattern = k.arg
        self.ftm.set_find_text(find_pattern)
        self.ftm.set_change_text(change_pattern)
        self.update_change_list(change_pattern)
        self.init_vim_search(find_pattern)
        self.init_in_headline()  # Required
        settings = self.ftm.get_settings()
        # Gui...
        k.clearState()
        k.resetLabel()
        k.showStateAndMode()
        c.widgetWantsFocusNow(w)
        self.do_find_next(settings)
    #@+node:ekr.20160920164418.2: *4* find.tag-children & helper
    @cmd('tag-children')
    def interactive_tag_children(self, event=None):  # pragma: no cover (interactive)
        """tag-children: prompt for a tag and add it to all children of c.p."""
        w = self.c.frame.body.wrapper
        if not w:
            return
        self.start_state_machine(event,
            prefix='Tag Children: ',
            handler=self.interactive_tag_children1)

    def interactive_tag_children1(self, event):  # pragma: no cover (interactive)
        c, k, p = self.c, self.k, self.c.p
        # Settings...
        tag = k.arg
        # Gui...
        k.clearState()
        k.resetLabel()
        k.showStateAndMode()
        self.do_tag_children(p, tag)
        c.treeWantsFocus()
    #@+node:ekr.20160920164418.4: *5* find.do_tag_children
    def do_tag_children(self, p, tag):
        """Handle the tag-children command."""
        c = self.c
        tc = getattr(c, 'theTagController', None)
        if not tc:
            if not g.unitTesting:  # pragma: no cover (skip)
                g.es_print('nodetags not active')
            return
        for p in p.children():
            tc.add_tag(p, tag)
        if not g.unitTesting:  # pragma: no cover (skip)
            g.es_print(f"Added {tag} tag to {len(list(c.p.children()))} nodes")

    #@+node:ekr.20210112050845.1: *4* find.word-search
    @cmd('word-search')
    @cmd('word-search-forward')
    def word_search_forward(self, event):  # pragma: no cover (interactive)
        """Same as start-search, with whole_word setting."""
        # Set flag for show_find_options.
        self.whole_word = True
        self.show_find_options()
        # Set flag for do_find_next().
        self.request_whole_world = True
        # Go.
        self.start_state_machine(event,
            prefix='Word Search: ',
            handler=self.start_search1,  # See start-search
            escape_handler=self.start_search_escape1,  # See start-search
        )
    #@+node:ekr.20131117164142.17009: *4* find.word-search-backward
    @cmd('word-search-backward')
    def word_search_backward(self, event):  # pragma: no cover (interactive)
        # Set flags for show_find_options.
        self.reverse = True
        self.whole_world = True
        self.show_find_options()
        # Set flags for do_find_next().
        self.request_reverse = True
        self.request_whole_world = True
        # Go
        self.start_state_machine(event,
            prefix='Word Search Backward: ',
            handler=self.start_search1,  # See start-search
            escape_handler=self.start_search_escape1,  # See start-search
        )
    #@+node:ekr.20210112192427.1: *3* LeoFind.Commands: helpers
    #@+node:ekr.20210110073117.9: *4* find._cf_helper & helpers
    def _cf_helper(self, settings, flatten):  # Caller has  checked the settings.
        """
        The common part of the clone-find commands.

        Return the number of found nodes.
        """
        c, u = self.c, self.c.undoer
        if self.pattern_match:
            ok = self.compile_pattern()
            if not ok:
                return 0
        if self.suboutline_only:
            p = c.p
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
            elif self._cfa_find_next_match(p):
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
            else:  # pragma: no cover (minor)
                p.moveToThreadNext()
            assert p != progress
        self.ftm.set_radio_button('entire-outline')
        # suboutline-only is a one-shot for batch commands.
        self.node_only = self.suboutline_only = False
        self.root = None
        if clones:
            undoData = u.beforeInsertNode(c.p)
            found = self._cfa_create_nodes(clones, flattened=False)
            u.afterInsertNode(found, 'Clone Find All', undoData)
            assert c.positionExists(found, trace=True), found
            c.setChanged()
            c.selectPosition(found)
            # Put the count in found.h.
            found.h = found.h.replace('Found:', f"Found {count}:")
        g.es("found", count, "matches for", self.find_text)
        return count  # Might be useful for the gui update.
    #@+node:ekr.20210110073117.34: *5* find._cfa_create_nodes
    def _cfa_create_nodes(self, clones, flattened):
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
    #@+node:ekr.20210110073117.10: *5* find._cfa_find_next_match (for unit tests)
    def _cfa_find_next_match(self, p):
        """
        Find the next batch match at p.
        """
        # Called only from unit tests.
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
    #@+node:ekr.20031218072017.3070: *4* find.change_selection
    def change_selection(self, p):
        """Replace selection with self.change_text."""
        c, p, u = self.c, self.c.p, self.c.undoer
        wrapper = c.frame.body and c.frame.body.wrapper
        gui_w = c.edit_widget(p) if self.in_headline else wrapper
        if not gui_w:  # pragma: no cover
            self.in_headline = False
            gui_w = wrapper
        if not gui_w:  # pragma: no cover
            return False
        oldSel = sel = gui_w.getSelectionRange()
        start, end = sel
        if start > end:  # pragma: no cover
            start, end = end, start
        if start == end:  # pragma: no cover
            g.es("no text selected")
            return False
        bunch = u.beforeChangeBody(p)
        start, end = oldSel
        change_text = self.change_text
        # Perform regex substitutions of \1, \2, ...\9 in the change text.
        if self.pattern_match and self.match_obj:
            groups = self.match_obj.groups()
            if groups:
                change_text = self.make_regex_subs(change_text, groups)
        change_text = self.replace_back_slashes(change_text)
        # Update both the gui widget and the work "widget"
        new_ins = start if self.reverse else start + len(change_text)
        if start != end:
            gui_w.delete(start, end)
        gui_w.insert(start, change_text)
        gui_w.setInsertPoint(new_ins)
        self.work_s = gui_w.getAllText()  # #2220.
        self.work_sel = (new_ins, new_ins, new_ins)
        # Update the selection for the next match.
        gui_w.setSelectionRange(start, start + len(change_text))
        c.widgetWantsFocus(gui_w)
        # No redraws here: they would destroy the headline selection.
        if self.mark_changes:  # pragma: no cover
            p.setMarked()
            p.setDirty()
        if self.in_headline:
            # #2220: Let onHeadChanged handle undo, etc.
            c.frame.tree.onHeadChanged(p, undoType='Change Headline')
            # gui_w will change after a redraw.
            gui_w = c.edit_widget(p)
            if gui_w:
                # find-next and find-prev work regardless of insert point.
                gui_w.setSelectionRange(start, start + len(change_text))
        else:
            p.v.b = gui_w.getAllText()
            u.afterChangeBody(p, 'Change Body', bunch)
        c.frame.tree.updateIcon(p)  # redraw only the icon.
        return True
    #@+node:ekr.20210110073117.31: *4* find.check_args
    def check_args(self, tag):
        """Check the user arguments to a command."""
        if not self.search_headline and not self.search_body:
            if not g.unitTesting:
                g.es_print("not searching headline or body")  # pragma: no cover (skip)
            return False
        if not self.find_text:
            if not g.unitTesting:
                g.es_print(f"{tag}: empty find pattern")  # pragma: no cover (skip)
            return False
        return True
    #@+node:ekr.20210110073117.32: *4* find.compile_pattern
    def compile_pattern(self):
        """Precompile the regexp pattern if necessary."""
        try:  # Precompile the regexp.
            # pylint: disable=no-member
            flags = re.MULTILINE
            if self.ignore_case:
                flags |= re.IGNORECASE
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
    #@+node:ekr.20031218072017.3075: *4* find.find_next_match & helpers
    def find_next_match(self, p):
        """
        Resume the search where it left off.

        Return (p, pos, newpos).
        """
        c = self.c
        if not self.search_headline and not self.search_body:  # pragma: no cover
            return None, None, None
        if not self.find_text:  # pragma: no cover
            return None, None, None
        attempts = 0
        if self.pattern_match:
            ok = self.precompile_pattern()
            if not ok:
                return None, None, None
        while p:
            pos, newpos = self._fnm_search(p)
            if pos is not None:
                # Success.
                if self.mark_finds:  # pragma: no cover
                    p.setMarked()
                    p.setDirty()
                    if not self.changeAllFlag:
                        c.frame.tree.updateIcon(p)  # redraw only the icon.
                return p, pos, newpos
            # Searching the pane failed: switch to another pane or node.
            if self._fnm_should_stay_in_node(p):
                # Switching panes is possible.  Do so.
                self.in_headline = not self.in_headline
                s = p.h if self.in_headline else p.b
                ins = len(s) if self.reverse else 0
                self.work_s = s
                self.work_sel = (ins, ins, ins)
            else:
                # Switch to the next/prev node, if possible.
                attempts += 1
                p = self._fnm_next_after_fail(p)
                if p:  # Found another node: select the proper pane.
                    self.in_headline = self._fnm_first_search_pane()
                    s = p.h if self.in_headline else p.b
                    ins = len(s) if self.reverse else 0
                    self.work_s = s
                    self.work_sel = (ins, ins, ins)
        return None, None, None
    #@+node:ekr.20131123132043.16476: *5* find._fnm_next_after_fail & helper
    def _fnm_next_after_fail(self, p):
        """Return the next node after a failed search or None."""
        # Move to the next position.
        p = p.threadBack() if self.reverse else p.threadNext()
        # Check it.
        if p and self._fail_outside_range(p):  # pragma: no cover
            return None
        if not p:  # pragma: no cover
            return None
        return p
    #@+node:ekr.20131123071505.16465: *6* find._fail_outside_range
    def _fail_outside_range(self, p):  # pragma: no cover
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
            if self.root and p != self.root and not self.root.isAncestorOf(p):
                return True
        if c.hoistStack:
            bunch = c.hoistStack[-1]
            if not bunch.p.isAncestorOf(p):
                g.trace('outside hoist', p.h)
                g.warning('found match outside of hoisted outline')
                return True
        return False  # Within range.
    #@+node:ekr.20131124060912.16473: *5* find._fnm_first_search_pane
    def _fnm_first_search_pane(self):
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
        return False  # pragma: no cover (now search the body)
    #@+node:ekr.20031218072017.3077: *5* find._fnm_search
    def _fnm_search(self, p):
        """
        Search self.work_s for self.find_text with present options.
        Returns (pos, newpos) or (None, dNone).
        """
        index = self.work_sel[2]
        s = self.work_s
        if sys.platform.lower().startswith('win'):
            s = s.replace('\r', '')
                # Ignore '\r' characters, which may appear in @edit nodes.
                # Fixes this bug: https://groups.google.com/forum/#!topic/leo-editor/yR8eL5cZpi4
                # This hack would be dangerous on MacOs: it uses '\r' instead of '\n' (!)
        if not s:  # pragma: no cover
            return None, None
        stopindex = 0 if self.reverse else len(s)
        pos, newpos = self.inner_search_helper(s, index, stopindex, self.find_text)
        if self.in_headline and not self.search_headline:  # pragma: no cover
            return None, None
        if not self.in_headline and not self.search_body:  # pragma: no cover
            return None, None
        if pos == -1:  # pragma: no cover
            return None, None
        ins = min(pos, newpos) if self.reverse else max(pos, newpos)
        self.work_sel = (pos, newpos, ins)
        return pos, newpos
    #@+node:ekr.20131124060912.16472: *5* find._fnm_should_stay_in_node
    def _fnm_should_stay_in_node(self, p):
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
    #@+node:ekr.20210110073117.43: *4* find.inner_search_helper & helpers
    def inner_search_helper(self, s, i, j, pattern):
        """
        Dispatch the proper search method based on settings.
        """
        backwards = self.reverse
        nocase = self.ignore_case
        regexp = self.pattern_match
        word = self.whole_word
        if backwards:
            i, j = j, i
        if not s[i:j] or not pattern:
            return -1, -1
        if regexp:
            pos, newpos = self._inner_search_regex(s, i, j, pattern, backwards, nocase)
        elif backwards:
            pos, newpos = self._inner_search_backward(s, i, j, pattern, nocase, word)
        else:
            pos, newpos = self._inner_search_plain(s, i, j, pattern, nocase, word)
        return pos, newpos
    #@+node:ekr.20210110073117.44: *5* find._inner_search_backward
    def _inner_search_backward(self, s, i, j, pattern, nocase, word):
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
                if self._inner_search_match_word(s, k, pattern):
                    return k, k + n
                j = max(0, k - 1)
            return -1, -1
        k = s.rfind(pattern, i, j)
        if k == -1:
            return -1, -1
        return k, k + n
    #@+node:ekr.20210110073117.45: *5* find._inner_search_match_word
    def _inner_search_match_word(self, s, i, pattern):
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
    #@+node:ekr.20210110073117.46: *5* find._inner_search_plain
    def _inner_search_plain(self, s, i, j, pattern, nocase, word):
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
                if self._inner_search_match_word(s, k, pattern):
                    return k, k + n
                i = k + n
            return -1, -1
        k = s.find(pattern, i, j)
        if k == -1:
            return -1, -1
        return k, k + n
    #@+node:ekr.20210110073117.47: *5* find._inner_search_regex
    def _inner_search_regex(self, s, i, j, pattern, backwards, nocase):
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
    #@+node:ekr.20210110073117.48: *4* find.make_regex_subs
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
    #@+node:ekr.20131123071505.16467: *4* find.precompile_pattern
    def precompile_pattern(self):
        """Precompile the regexp pattern if necessary."""
        try:  # Precompile the regexp.
            # pylint: disable=no-member
            flags = re.MULTILINE
            if self.ignore_case:
                flags |= re.IGNORECASE
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
            if not g.unitTesting:
                g.warning('invalid regular expression:', self.find_text)
            return False
    #@+node:ekr.20210110073117.49: *4* find.replace_back_slashes
    def replace_back_slashes(self, s):
        """Carefully replace backslashes in a search pattern."""
        # This is NOT the same as:
        #
        #   s.replace('\\n','\n').replace('\\t','\t').replace('\\\\','\\')
        #
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
    #@+node:ekr.20031218072017.3082: *3* LeoFind.Initing & finalizing
    #@+node:ekr.20031218072017.3086: *4* find.init_in_headline & helper
    def init_in_headline(self):
        """
        Select the first pane to search for incremental searches and changes.
        This is called only at the start of each search.
        This must not alter the current insertion point or selection range.
        """
        #
        # Fix bug 1228458: Inconsistency between Find-forward and Find-backward.
        if self.search_headline and self.search_body:
            # We have no choice: we *must* search the present widget!
            self.in_headline = self.focus_in_tree()
        else:
            self.in_headline = self.search_headline
    #@+node:ekr.20131126085250.16651: *5* find.focus_in_tree
    def focus_in_tree(self):
        """
        Return True is the focus widget w is anywhere in the tree pane.

        Note: the focus may be in the find pane.
        """
        c = self.c
        ftm = self.ftm
        w = ftm and ftm.entry_focus or g.app.gui.get_focus(raw=True)
        if ftm:
            ftm.entry_focus = None  # Only use this focus widget once!
        w_name = c.widget_name(w)
        if w == c.frame.body.wrapper:
            val = False
        elif w == c.frame.tree.treeWidget:  # pragma: no cover
            val = True
        else:
            val = w_name.startswith('head')  # pragma: no cover
        return val
    #@+node:ekr.20031218072017.3089: *4* find.restore
    def restore(self, data):
        """
        Restore Leo's gui and settings from data, a g.Bunch.
        """
        c, p = self.c, data.p
        c.frame.bringToFront()  # Needed on the Mac
        if not p or not c.positionExists(p):  # pragma: no cover
            # Better than selecting the root!
            return
        c.selectPosition(p)
        # Fix bug 1258373: https://bugs.launchpad.net/leo-editor/+bug/1258373
        if self.in_headline:
            c.treeWantsFocus()
        else:
            # Looks good and provides clear indication of failure or termination.
            w = c.frame.body.wrapper
            w.setSelectionRange(data.start, data.end, insert=data.insert)
            w.seeInsertPoint()
            c.widgetWantsFocus(w)
    #@+node:ekr.20031218072017.3090: *4* find.save
    def save(self):
        """Save everything needed to restore after a search fails."""
        c = self.c
        if self.in_headline:  # pragma: no cover
            # Fix bug 1258373: https://bugs.launchpad.net/leo-editor/+bug/1258373
            # Don't try to re-edit the headline.
            insert, start, end = None, None, None
        else:
            w = c.frame.body.wrapper
            insert = w.getInsertPoint()
            start, end = w.getSelectionRange()
        data = g.Bunch(
            end=end,
            in_headline=self.in_headline,
            insert=insert,
            p=c.p.copy(),
            start=start,
        )
        return data
    #@+node:ekr.20031218072017.3091: *4* find.show_success
    def show_success(self, p, pos, newpos, showState=True):
        """Display the result of a successful find operation."""
        c = self.c
        # Set state vars.
        # Ensure progress in backwards searches.
        insert = min(pos, newpos) if self.reverse else max(pos, newpos)
        if c.sparse_find:  # pragma: no cover
            c.expandOnlyAncestorsOfNode(p=p)
        if self.in_headline:
            c.endEditing()
            c.redraw(p)
            c.frame.tree.editLabel(p)
            w = c.edit_widget(p)  # #2220
            if w:
                w.setSelectionRange(pos, newpos, insert)  # #2220
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
            if c.vim_mode and c.vimCommands:  # pragma: no cover
                c.vimCommands.update_selection_after_search()
        # Support for the console gui.
        if hasattr(g.app.gui, 'show_find_success'):  # pragma: no cover
            g.app.gui.show_find_success(c, self.in_headline, insert, p)
        c.frame.bringToFront()
        return w  # Support for isearch.
    #@+node:ekr.20131117164142.16939: *3* LeoFind.ISearch
    #@+node:ekr.20210112192011.1: *4* LeoFind.Isearch commands
    #@+node:ekr.20131117164142.16941: *5* find.isearch_forward
    @cmd('isearch-forward')
    def isearch_forward(self, event):  # pragma: no cover (cmd)
        """
        Begin a forward incremental search.

        - Plain characters extend the search.
        - !<isearch-forward>! repeats the search.
        - Esc or any non-plain key ends the search.
        - Backspace reverses the search.
        - Backspacing to an empty search pattern
          completely undoes the effect of the search.
        """
        self.start_incremental(event, 'isearch-forward',
            forward=True, ignoreCase=False, regexp=False)
    #@+node:ekr.20131117164142.16942: *5* find.isearch_backward
    @cmd('isearch-backward')
    def isearch_backward(self, event):  # pragma: no cover (cmd)
        """
        Begin a backward incremental search.

        - Plain characters extend the search backward.
        - !<isearch-forward>! repeats the search.
        - Esc or any non-plain key ends the search.
        - Backspace reverses the search.
        - Backspacing to an empty search pattern
          completely undoes the effect of the search.
        """
        self.start_incremental(event, 'isearch-backward',
            forward=False, ignoreCase=False, regexp=False)
    #@+node:ekr.20131117164142.16943: *5* find.isearch_forward_regexp
    @cmd('isearch-forward-regexp')
    def isearch_forward_regexp(self, event):  # pragma: no cover (cmd)
        """
        Begin a forward incremental regexp search.

        - Plain characters extend the search.
        - !<isearch-forward-regexp>! repeats the search.
        - Esc or any non-plain key ends the search.
        - Backspace reverses the search.
        - Backspacing to an empty search pattern
          completely undoes the effect of the search.
        """
        self.start_incremental(event, 'isearch-forward-regexp',
            forward=True, ignoreCase=False, regexp=True)
    #@+node:ekr.20131117164142.16944: *5* find.isearch_backward_regexp
    @cmd('isearch-backward-regexp')
    def isearch_backward_regexp(self, event):  # pragma: no cover (cmd)
        """
        Begin a backward incremental regexp search.

        - Plain characters extend the search.
        - !<isearch-forward-regexp>! repeats the search.
        - Esc or any non-plain key ends the search.
        - Backspace reverses the search.
        - Backspacing to an empty search pattern
          completely undoes the effect of the search.
        """
        self.start_incremental(event, 'isearch-backward-regexp',
            forward=False, ignoreCase=False, regexp=True)
    #@+node:ekr.20131117164142.16945: *5* find.isearch_with_present_options
    @cmd('isearch-with-present-options')
    def isearch_with_present_options(self, event):  # pragma: no cover (cmd)
        """
        Begin an incremental search using find panel options.

        - Plain characters extend the search.
        - !<isearch-forward-regexp>! repeats the search.
        - Esc or any non-plain key ends the search.
        - Backspace reverses the search.
        - Backspacing to an empty search pattern
          completely undoes the effect of the search.
        """
        self.start_incremental(event, 'isearch-with-present-options',
            forward=None, ignoreCase=None, regexp=None)
    #@+node:ekr.20131117164142.16946: *4* LeoFind.Isearch utils
    #@+node:ekr.20131117164142.16947: *5* find.abort_search (incremental)
    def abort_search(self):  # pragma: no cover (cmd)
        """Restore the original position and selection."""
        c, k = self.c, self.k
        w = c.frame.body.wrapper
        k.clearState()
        k.resetLabel()
        p, i, j, in_headline = self.stack[0]
        self.in_headline = in_headline
        c.selectPosition(p)
        c.redraw_after_select(p)
        c.bodyWantsFocus()
        w.setSelectionRange(i, j)
    #@+node:ekr.20131117164142.16948: *5* find.end_search
    def end_search(self):  # pragma: no cover (cmd)
        c, k = self.c, self.k
        k.clearState()
        k.resetLabel()
        c.bodyWantsFocus()
    #@+node:ekr.20131117164142.16949: *5* find.iSearch_helper
    def iSearch_helper(self, again=False):  # pragma: no cover (cmd)
        """Handle the actual incremental search."""
        c, k, p = self.c, self.k, self.c.p
        reverse = not self.isearch_forward_flag
        pattern = k.getLabel(ignorePrompt=True)
        if not pattern:
            self.abort_search()
            return
        # Settings...
        self.find_text = self.ftm.get_find_text()
        self.change_text = self.ftm.get_change_text()
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
        if len(self.stack) <= 1:
            self.in_headline = False
        # Init the work widget from the gui widget.
        gui_w = self.set_widget()
        s = gui_w.getAllText()
        i, j = gui_w.getSelectionRange()
        if again:
            ins = i if reverse else j + len(pattern)
        else:
            ins = j + len(pattern) if reverse else i
        self.work_s = s
        self.work_sel = (ins, ins, ins)
        # Do the search!
        p, pos, newpos = self.find_next_match(p)
        # Restore.
        self.find_text = oldPattern
        self.pattern_match = oldRegexp
        self.reverse = False
        self.whole_word = oldWord
        # Handle the results of the search.
        if pos is not None:  # success.
            w = self.show_success(p, pos, newpos, showState=False)
            if w:
                i, j = w.getSelectionRange(sort=False)
            if not again:
                self.push(c.p, i, j, self.in_headline)
        else:
            g.es(f"not found: {pattern}")
            if not again:
                event = g.app.gui.create_key_event(
                    c, binding='BackSpace', char='\b', w=w)
                k.updateLabel(event)
    #@+node:ekr.20131117164142.16950: *5* find.isearch_state_handler
    def isearch_state_handler(self, event):  # pragma: no cover (cmd)
        """The state manager when the state is 'isearch"""
        # c = self.c
        k = self.k
        stroke = event.stroke if event else None
        s = stroke.s if stroke else ''
        # No need to recognize ctrl-z.
        if s in ('Escape', '\n', 'Return'):
            self.end_search()
        elif stroke in self.iSearchStrokes:
            self.iSearch_helper(again=True)
        elif s in ('\b', 'BackSpace'):
            k.updateLabel(event)
            self.isearch_backspace()
        elif (
            s.startswith('Ctrl+') or
            s.startswith('Alt+') or
            k.isFKey(s)  # 2011/06/13.
        ):
            # End the search.
            self.end_search()
            k.masterKeyHandler(event)
        # Fix bug 1267921: isearch-forward accepts non-alphanumeric keys as input.
        elif k.isPlainKey(stroke):
            k.updateLabel(event)
            self.iSearch_helper()
    #@+node:ekr.20131117164142.16951: *5* find.isearch_backspace
    def isearch_backspace(self):  # pragma: no cover (cmd)

        c = self.c
        if len(self.stack) <= 1:
            self.abort_search()
            return
        # Reduce the stack by net 1.
        self.pop()
        p, i, j, in_headline = self.pop()
        self.push(p, i, j, in_headline)
        if in_headline:
            # Like self.show_success.
            selection = i, j, i
            c.redrawAndEdit(p, selectAll=False,
                selection=selection,
                keepMinibuffer=True)
        else:
            c.selectPosition(p)
            w = c.frame.body.wrapper
            c.bodyWantsFocus()
            if i > j:
                i, j = j, i
            w.setSelectionRange(i, j)
        if len(self.stack) <= 1:
            self.abort_search()
    #@+node:ekr.20131117164142.16952: *5* find.get_strokes
    def get_strokes(self, commandName):  # pragma: no cover (cmd)
        aList = self.inverseBindingDict.get(commandName, [])
        return [key for pane, key in aList]
    #@+node:ekr.20131117164142.16953: *5* find.push & pop
    def push(self, p, i, j, in_headline):  # pragma: no cover (cmd)
        data = p.copy(), i, j, in_headline
        self.stack.append(data)

    def pop(self):  # pragma: no cover (cmd)
        data = self.stack.pop()
        p, i, j, in_headline = data
        return p, i, j, in_headline
    #@+node:ekr.20131117164142.16954: *5* find.set_widget
    def set_widget(self):  # pragma: no cover (cmd)
        c, p = self.c, self.c.p
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
                self.in_headline = False
                w = wrapper
        else:
            w = wrapper
        if w == wrapper:
            c.bodyWantsFocus()
        return w
    #@+node:ekr.20131117164142.16955: *5* find.start_incremental
    def start_incremental(self, event, commandName, forward, ignoreCase, regexp):  # pragma: no cover (cmd)
        c, k = self.c, self.k
        # None is a signal to get the option from the find tab.
        self.event = event
        self.isearch_forward_flag = not self.reverse if forward is None else forward
        self.isearch_ignore_case = self.ignore_case if ignoreCase is None else ignoreCase
        self.isearch_regexp = self.pattern_match if regexp is None else regexp
        # Note: the word option can't be used with isearches!
        w = c.frame.body.wrapper
        self.p1 = c.p
        self.sel1 = w.getSelectionRange(sort=False)
        i, j = self.sel1
        self.push(c.p, i, j, self.in_headline)
        self.inverseBindingDict = k.computeInverseBindingDict()
        self.iSearchStrokes = self.get_strokes(commandName)
        k.setLabelBlue(
            "Isearch"
            f"{' Backward' if not self.isearch_forward_flag else ''}"
            f"{' Regexp' if self.isearch_regexp else ''}"
            f"{' NoCase' if self.isearch_ignore_case else ''}"
            ": "
        )
        k.setState('isearch', 1, handler=self.isearch_state_handler)
        c.minibufferWantsFocus()
    #@+node:ekr.20031218072017.3067: *3* LeoFind.Utils
    #@+node:ekr.20131117164142.16992: *4* find.add_change_string_to_label
    def add_change_string_to_label(self):  # pragma: no cover (cmd)
        """Add an unprotected change string to the minibuffer label."""
        c = self.c
        s = self.ftm.get_change_text()
        c.minibufferWantsFocus()
        while s.endswith('\n') or s.endswith('\r'):
            s = s[:-1]
        c.k.extendLabel(s, select=True, protect=False)
    #@+node:ekr.20131117164142.16993: *4* find.add_find_string_to_label
    def add_find_string_to_label(self, protect=True):  # pragma: no cover (cmd)
        c, k = self.c, self.c.k
        ftm = c.findCommands.ftm
        s = ftm.get_find_text()
        c.minibufferWantsFocus()
        while s.endswith('\n') or s.endswith('\r'):
            s = s[:-1]
        k.extendLabel(s, select=True, protect=protect)
    #@+node:ekr.20210110073117.33: *4* find.compute_result_status
    def compute_result_status(self, find_all_flag=False):  # pragma: no cover (cmd)
        """Return the status to be shown in the status line after a find command completes."""
        # Too similar to another method...
        status = []
        table = (
            ('whole_word', 'Word'),
            ('ignore_case', 'Ignore Case'),
            ('pattern_match', 'Regex'),
            ('suboutline_only', '[Outline Only]'),
            ('node_only', '[Node Only]'),
            ('search_headline', 'Head'),
            ('search_body', 'Body'),
        )
        for ivar, val in table:
            if getattr(self, ivar):
                status.append(val)
        return f" ({', '.join(status)})" if status else ''
    #@+node:ekr.20131119204029.16479: *4* find.help_for_find_commands
    def help_for_find_commands(self, event=None):  # pragma: no cover (cmd)
        """Called from Find panel.  Redirect."""
        self.c.helpCommands.help_for_find_commands(event)
    #@+node:ekr.20210111082524.1: *4* find.init_vim_search
    def init_vim_search(self, pattern):  # pragma: no cover (cmd)
        """Initialize searches in vim mode."""
        c = self.c
        if c.vim_mode and c.vimCommands:
            c.vimCommands.update_dot_before_search(
                find_pattern=pattern,
                change_pattern=None)  # A flag.
    #@+node:ekr.20150629072547.1: *4* find.preload_find_pattern
    def preload_find_pattern(self, w):  # pragma: no cover (cmd)
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
            ftm.set_find_text(s)
            ftm.init_focus()
    #@+node:ekr.20150619070602.1: *4* find.show_status
    def show_status(self, found):
        """Show the find status the Find dialog, if present, and the status line."""
        c = self.c
        status = 'found' if found else 'not found'
        options = self.compute_result_status()
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
    #@+node:ekr.20150615174549.1: *4* find.show_find_options_in_status_area & helper
    def show_find_options_in_status_area(self):  # pragma: no cover (cmd)
        """Show find options in the status area."""
        c = self.c
        s = self.compute_find_options_in_status_area()
        c.frame.putStatusLine(s)
    #@+node:ekr.20171129211238.1: *5* find.compute_find_options_in_status_area
    def compute_find_options_in_status_area(self):
        c = self.c
        ftm = c.findCommands.ftm
        table = (
            ('Word', ftm.check_box_whole_word),
            ('Ig-case', ftm.check_box_ignore_case),
            ('regeXp', ftm.check_box_regexp),
            ('Body', ftm.check_box_search_body),
            ('Head', ftm.check_box_search_headline),
            # ('wrap-Around', ftm.check_box_wrap_around),
            ('mark-Changes', ftm.check_box_mark_changes),
            ('mark-Finds', ftm.check_box_mark_finds),
        )
        result = [option for option, ivar in table if ivar.isChecked()]
        table2 = (
            ('Suboutline', ftm.radio_button_suboutline_only),
            ('Node', ftm.radio_button_node_only),
        )
        for option, ivar in table2:
            if ivar.isChecked():
                result.append(f"[{option}]")
                break
        return f"Find: {' '.join(result)}"
    #@+node:ekr.20131117164142.17007: *4* find.start_state_machine
    def start_state_machine(self, event, prefix, handler, escape_handler=None):  # pragma: no cover (cmd)
        """
        Initialize and start the state machine used to get user arguments.
        """
        c, k = self.c, self.k
        w = c.frame.body.wrapper
        if not w:
            return
        # Gui...
        k.setLabelBlue(prefix)
        # New in Leo 5.2: minibuffer modes shows options in status area.
        if self.minibuffer_mode:
            self.show_find_options_in_status_area()
        elif c.config.getBool('use-find-dialog', default=True):
            g.app.gui.openFindDialog(c)
        else:
            c.frame.log.selectTab('Find')
        self.add_find_string_to_label(protect=False)
        k.getArgEscapes = ['\t'] if escape_handler else []
        self.handler = handler
        self.escape_handler = escape_handler
        # Start the state maching!
        k.get1Arg(event, handler=self.state0, tabList=self.findTextList, completion=True)

    def state0(self, event):  # pragma: no cover (cmd)
        """Dispatch the next handler."""
        k = self.k
        if k.getArgEscapeFlag:
            k.getArgEscapeFlag = False
            self.escape_handler(event)
        else:
            self.handler(event)
    #@+node:ekr.20131117164142.17008: *4* find.updateChange/FindList
    def update_change_list(self, s):  # pragma: no cover (cmd)
        if s not in self.changeTextList:
            self.changeTextList.append(s)

    def update_find_list(self, s):  # pragma: no cover (cmd)
        if s not in self.findTextList:
            self.findTextList.append(s)
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
