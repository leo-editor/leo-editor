# @+leo-ver=5-thin
# @+node:ekr.20150514035236.1: * @file ../commands/abbrevCommands.py
"""Leo's abbreviations commands."""

# @+<< abbrevCommands imports & abbreviations >>
# @+node:ekr.20150514045700.1: ** << abbrevCommands imports & abbreviations >>
from __future__ import annotations
from collections.abc import Callable
import functools
import re
import string
from typing import TYPE_CHECKING
from leo.core import leoGlobals as g
from leo.core import leoNodes
from leo.commands.baseCommands import BaseEditCommandsClass

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent
    from leo.plugins.qt_text import QTextMixin

# @-<< abbrevCommands imports & abbreviations >>


def cmd(name: str) -> Callable:
    """Command decorator for the abbrevCommands class."""
    return g.new_cmd_decorator(name, ['c', 'abbrevCommands'])


# @+others
# @+node:ekr.20160514095531.1: ** class AbbrevCommands
class AbbrevCommandsClass(BaseEditCommandsClass):
    """
    A class to handle user-defined abbreviations.
    See apropos-abbreviations for details.
    """

    # @+<< AbbrevCommandsClass: __slots__ >>
    # @+node:ekr.20260515152425.1: *3* << AbbrevCommandsClass: __slots__ >>
    __slots__ = (
        'abbrevs',
        'c',
        'dyna_regex',
        'in_head',
        'scripting_enabled',
        'expanding',
        'number_regex',
        'tree_abbrevs_d',
        'w',
    )
    # @-<< AbbrevCommandsClass: __slots__ >>

    # @+others
    # @+node:ekr.20150514043850.3: *3* abbrev.__init__
    def __init__(self, c: Cmdr) -> None:
        """Ctor for AbbrevCommandsClass class."""
        # pylint: disable=super-init-not-called
        self.c = c
        # Set local ivars.
        self.abbrevs: dict[str, str] = {}  # Keys are names, values are abbreviations.
        self.dyna_regex = re.compile(  # For dynamic abbreviations
            r'[%s%s\-_]+' % (string.ascii_letters, string.digits)
        )
        self.in_head = False  #
        self.number_regex = re.compile(r'(?<!\\)\\n')  # to replace \\n but not \\\\n
        self.scripting_enabled = False  # Global setting.
        self.expanding = False  # True: expanding abbreviations.
        self.subst_env: list[str] = []  # The scripting environment.
        self.tree_abbrevs_d: dict[str, str] = {}  # Keys are names, values are (tree,tag).
        self.w: QTextMixin = None

    # @+node:ekr.20150514043850.11: *3* abbrev.expandAbbrev & helpers (entry point)
    def expandAbbrev(self, event: LeoKeyEvent, stroke: g.KeyStroke) -> bool:
        """
        Not a command.  Expand abbreviations..

        Return True if the abbreviation was expanded.
        """
        # Define ins, prefixes, self.in_head and self.w
        # Return if there is nothing to do.
        # @+<< expandAbbrev: prolog >>
        # @+node:ekr.20260516052046.1: *4* << expandAbbrev: prolog >>
        c = self.c
        ch = self.get_ch(event, stroke)
        w = event.w if event else c.frame.body.wrapper
        if self.expanding or not g.isTextWrapper(w) or w.hasSelection() or not ch.strip():
            return False
        w_name = g.app.gui.widget_name(w)
        if not w_name.startswith(('body', 'head')):
            return False
        s = w.getAllText()
        if not s:
            return False
        ins = w.getInsertPoint()
        prefixes = self.get_prefixes(ins, s)
        if not prefixes:
            return False
        # Set local ivars.
        self.in_head = w_name.startswith('head')
        self.w = w
        # @-<< expandAbbrev: prolog >>

        # Try to match an abbreviation.
        for prefix in prefixes:
            word = prefix + ch
            i = ins - len(prefix)
            if expansion := self.tree_abbrevs_d.get(word):
                self.expand_tree(i, ins, word, expansion)
                self.make_all_scripting_substitutions(word)
                self.init_place_holder_search(node_only=False)
                return True
            if expansion := self.abbrevs.get(word):
                self.replace_selection(i, ins, expansion)
                self.make_script_substitutions(word)
                self.init_place_holder_search(node_only=True)
                return True
        return False

    # @+node:ekr.20260516063712.1: *4* abbrev: startup
    # @+node:ekr.20161121111502.1: *5* abbrev.get_ch
    def get_ch(self, event: LeoKeyEvent, stroke: g.KeyStroke) -> str:
        """Return the ch from the stroke or event."""
        event_ch = event.char or '' if event else ''
        assert g.isStrokeOrNone(stroke), stroke
        if stroke in ('BackSpace', 'Delete'):
            return ''
        d = {'Return': '\n', 'Tab': '\t', 'space': ' ', 'underscore': '_'}
        if not stroke:
            return event_ch
        ch = d.get(stroke.s, stroke.s)
        if len(ch) == 1:
            return ch
        if any(stroke.find(z) > -1 for z in ('Ctrl+', 'Alt+', 'Meta+')):
            return ''
        return event_ch

    # @+node:ekr.20161121112346.1: *5* abbrev.get_prefixes
    def get_prefixes(self, ins: int, s: str) -> list[str]:
        """
        Return the prefixes at given insert point.

        Any sequence longer than 1 may abbreviation.

        Any whitespace stops the search.
        """
        i, prefixes = ins - 1, []
        while len(s) > i >= 0 and s[i] not in ' \t\n':
            prefixes.append(s[i:ins])
            i -= 1
        prefixes = list(reversed(prefixes))
        if '' not in prefixes:
            prefixes.append('')
        return prefixes

    # @+node:ekr.20260516063651.1: *4* abbrev: expansion
    # @+node:ekr.20150514043850.13: *5* abbrev.expand_tree
    def expand_tree(self, i: int, j: int, word: str, expansion: str) -> None:
        """
        Paste `expansion` as children of c.p.
        This happens *before* any substitutions are made.
        """
        c = self.c
        u, undoType = c.undoer, 'Expand Tree Abbreviation'
        if c.p.hasChildren():
            g.es_print('tree abbreviations must not have children', color='blue')
            return
        if not c.canPasteOutline(expansion):
            g.es_print(f"bad copied outline: {expansion}")
            return

        # Begin the undo.
        u.beforeChangeGroup(c.p, command=undoType, verboseUndoGroup=True)
        self.replace_selection(i, j, '')

        # Set status flags.
        isRoot = c.p.isRoot()
        wasHoisted = len(c.hoistStack) > 0
        parent = c.p.getParent()
        noSiblings = parent and parent.numberOfChildren() == 1
        isFirstChild = parent and parent.firstChild() == c.p
        prevSibling = c.p.moveToBack()
        prevSiblingExpanded = prevSibling and prevSibling.isExpanded()

        # Carefully replace the old node with the new node.
        if c.canDeleteHeadline():
            if prevSiblingExpanded:
                prevSibling.contract()  # To prevent pasting as last child of prevSibling.
            c.deleteOutline(op_name="Cut Node")
            c.pasteOutline(s=expansion)
            if noSiblings:
                c.moveOutlineRight()  # Inserted below instead of as child, so move right.
            if isRoot:
                c.moveOutlineUp()  # Delete & paste made it second position, so move up.
        else:
            c.pasteOutline(s=expansion)
            c.selectPosition(c.p.moveToBack())
            c.deleteOutline(op_name="Cut Node")
            if wasHoisted:
                c.selectVisNext()

        # Replace the container node with its first child.
        child = c.p.copy().moveToFirstChild()
        if child:
            c.selectPosition(child)
            c.moveOutlineLeft()
            c.goToPrevSibling()
            c.deleteOutline(op_name="Cut Node")
            if isFirstChild or (not isRoot):
                c.selectVisNext()

        # Restore the previous expansion.
        if prevSiblingExpanded:
            prevSibling.expand()

        # End the undo.
        u.afterChangeGroup(c.p, undoType=undoType)
        c.redraw(c.p)

    # @+node:ekr.20260515084054.1: *5* abbrev.init_place_holder_search
    def init_place_holder_search(self, *, node_only: bool) -> None:
        c = self.c
        p = c.p
        finder = c.findCommands
        start_pat = re.escape(c.abbrev_place_start)
        end_pat = re.escape(c.abbrev_place_end)
        template_regex = re.compile(rf"^.*?{start_pat}.*?{end_pat}")
        finder.reverse = False

        # Define the settings for Leo's find command.
        settings = g.Bunch(
            p               = c.p,
            in_headline     = False,
            find_text       = rf"({start_pat}.*?{end_pat})",
            change_text     = '',
            file_only       = False,
            mark_changes    = False,
            mark_finds      = False,
            ignore_case     = True,
            node_only       = node_only,
            pattern_match   = True,
            search_body     = True,
            search_headline = True,
            suboutline_only = not node_only,
            whole_word      = False,
        )  # fmt: skip
        assert settings

        def find_template(s: str) -> bool:
            return any(template_regex.match(z) for z in g.splitLines(s))

        # Init the search only if <\...\> appears in the expansion.
        positions = [p] if node_only else (z for z in p.self_and_subtree())
        for p in positions:
            if any(find_template(z) for z in (p.h, p.b)):
                break
        else:
            return

        # Tell the search command to restore settings on failure.
        bunch = g.Bunch()
        for ivar in finder.ivars:
            bunch[ivar] = getattr(finder, ivar)
        finder.previous_settings = bunch

        # Search!
        c.endEditing()  # No need to re-edit the headline!
        self.w.setInsertPoint(0)  # Start search at start.
        finder.interactive_search_helper(settings=settings)

    # @+node:ekr.20150514043850.18: *5* abbrev.replace_selection
    def replace_selection(self, i: int, j: int, s: str) -> None:
        """Undoably replace w[i:j] by s."""
        c = self.c
        p = c.p
        u = c.undoer
        w = self.w

        # Start the undo.
        bunch = u.beforeChangeNodeContents(p)

        # Make the replacement.
        w.delete(i, j)
        w.insert(i, s)

        # Update only body text. Setting p.h here would be wrong.
        if not self.in_head:
            p.v.b = w.getAllText()

        # Complete the undo.
        u.afterChangeNodeContents(p, command='Abbreviation', bunch=bunch)

    # @+node:ekr.20260516063743.1: *4* abbrev: script substitution
    # @+node:ekr.20260516063159.1: *5* abbrev.make_all_scripting_substitutions
    def make_all_scripting_substitutions(self, word: str) -> None:
        """Make scripting substitutions throughout c.p's tree."""
        c = self.c
        if not self.scripting_enabled:
            return

        # Do nothing if {|{... appears nowwhere in c.p's tree.
        start_pat = re.escape(c.abbrev_subst_start)
        end_pat = re.escape(c.abbrev_subst_end)
        substitution_regex = re.compile(rf"^.*?{start_pat}.*?{end_pat}")

        def find_template(s: str) -> bool:
            return any(substitution_regex.match(z) for z in g.splitLines(s))

        for p in c.p.self_and_subtree():
            if any(find_template(z) for z in (p.h, p.b)):
                break
        else:
            return

        c.abbrev_subst_env['_abr'] = word
        c.endEditing()  # No need to re-edit the headline!

        # A hack to accommodate existing abbreviations: evaluate bodies before headlines.
        for p in c.p.self_and_subtree():
            p.b = self._substitution_helper(p.b)
            p.h = self._substitution_helper(p.h)

    # @+node:ekr.20150514043850.15: *5* abbrev.make_script_substitutions
    def make_script_substitutions(self, word: str) -> None:
        """
        Replace word by scripting expansion in p.h or p.b.
        """
        c = self.c
        p = c.p
        w = self.w
        if not self.scripting_enabled:
            return

        c.abbrev_subst_env['_abr'] = word

        # Replace the contents only if they have changed!
        ins = w.getInsertPoint()
        if self.in_head:
            c.endEditing()
            try:
                contents = p.h
                end_text = contents[ins:]
                new_contents = self._substitution_helper(contents)
                if new_contents != contents:
                    p.h = new_contents
                    if new_contents.endswith(end_text):
                        new_ins = len(new_contents) - len(end_text)
                    else:
                        new_ins = min(ins, len(new_contents))
                    w.setInsertPoint(new_ins)
            finally:
                c.treeWantsFocusNow()
                c.editHeadline()
        else:
            contents = p.b
            end_text = contents[ins:]
            new_contents = self._substitution_helper(contents)
            if new_contents != contents:
                p.b = new_contents
                if new_contents.endswith(end_text):
                    new_ins = len(new_contents) - len(end_text)
                else:
                    new_ins = min(ins, len(new_contents))
                p.setSelection(new_ins, len(new_contents))
                w.setInsertPoint(new_ins)

    # @+node:ekr.20260516060909.1: *5* abbrev._substitution_helper
    def _substitution_helper(self, content: str) -> str:
        """
        Replace 'word' by the 'definition' in the 'content' string.
        """
        c = self.c
        if c.abbrev_subst_start not in content:
            return content
        while c.abbrev_subst_start in content:
            prefix, rest = content.split(c.abbrev_subst_start, 1)
            content_list = rest.split(c.abbrev_subst_end, 1)
            if len(content_list) != 2:
                break
            content, rest = content_list
            try:
                self.expanding = True
                c.abbrev_subst_env['x'] = ''
                exec(content, c.abbrev_subst_env, c.abbrev_subst_env)
            except NameError:
                pass  # The script should define the name ???
            except Exception as e:
                g.es_print(f"exception evaluating {content!r}: {e}")
                g.trace(g.callers())
                g.es_exception()
            finally:
                self.expanding = False
            x = c.abbrev_subst_env.get('x') or ''
            # Make sure there are no endless expansions.
            x = x.replace(c.abbrev_subst_start, '').replace(c.abbrev_subst_end, '')
            content = f"{prefix}{x}{rest}"
        return content

    # @+node:ekr.20150514043850.5: *3* abbrev.finishCreate
    def finishCreate(self) -> None:
        """AbbrevCommandsClass.finishCreate."""
        self.reload_settings()

    # @+node:ekr.20170221035644.1: *3* abbrev.reload_settings & helpers
    def reload_settings(self) -> None:
        """Reload all abbreviation settings."""
        self.abbrevs = {}
        self.init_settings()
        self.init_abbrev()
        self.init_tree_abbrev()
        self.init_env()

    reloadSettings = reload_settings

    # @+node:ekr.20150514043850.6: *4* abbrev.init_abbrev & helper
    def init_abbrev(self) -> None:
        """
        Init the user abbreviations from @data global-abbreviations
        and @data abbreviations nodes.
        """
        c = self.c
        table = (
            ('global-abbreviations', 'global'),
            ('abbreviations', 'local'),
        )
        for source, tag in table:
            aList = c.config.getData(source, strip_data=False) or []
            abbrev, result = [], []
            for s in aList:
                if s.startswith('\\:'):
                    # Continue the previous abbreviation.
                    abbrev.append(s[2:])
                else:
                    # End the previous abbreviation.
                    if abbrev:
                        result.append(''.join(abbrev))
                        abbrev = []
                    # Start the new abbreviation.
                    if s.strip():
                        abbrev.append(s)
            # End any remaining abbreviation.
            if abbrev:
                result.append(''.join(abbrev))
            for s in sorted(result):
                self.addAbbrevHelper(s)

    # @+node:ekr.20150514043850.25: *5* abbrev.addAbbrevHelper
    def addAbbrevHelper(self, s: str, tag: str = '') -> None:
        """Enter the abbreviation 's' into the self.abbrevs dict."""
        if not s.strip():
            return
        try:
            d = self.abbrevs
            # crudely allow use of '=' in abbreviation definition -
            #  substitute '\=' with Unicode FULLWIDTH EQUALS SIGN
            data = re.sub("\\\\=", '\uff1d', s).split('=')
            # Do *not* strip ws, so the user can specify ws. in replacement
            name = data[0].replace('\\t', '\t').replace('\\n', '\n')
            val = '='.join(data[1:])
            if val.endswith('\n'):
                val = val[:-1]
            val = self.number_regex.sub('\n', val).replace('\\\\n', '\\n')
            old = d.get(name)
            if old and old != val and not g.unitTesting:
                g.es_print(f"redefining abbreviation {name}\nfrom {old!r} to {val!r}")
            # add undecorated entry into dict
            d[re.sub('\uff1d', '=', name)] = val
        except ValueError:
            g.es_print(f"bad abbreviation: {s}")

    # @+node:ekr.20150514043850.7: *4* abbrev.init_env
    def init_env(self) -> None:
        """
        Init c.abbrev_subst_env by executing the contents of the
        @data abbreviations-subst-env node.
        """
        c = self.c
        at = c.atFileCommands
        if not self.scripting_enabled:
            return
        if not c.abbrev_place_start or not c.abbrev_place_end:
            return
        aList = self.subst_env
        script_list = []
        for z in aList:
            # Compatibility with original design.
            if z.startswith('\\:'):
                script_list.append(z[2:])
            else:
                script_list.append(z)
        script = ''.join(script_list)
        # Allow Leo directives in @data abbreviations-subst-env trees.
        # #1674: Avoid unnecessary entries in c.fileCommands.gnxDict.
        root = c.rootPosition()
        if root:
            v = root.v
        else:
            # Defensive programming. Probably will never happen.
            v = leoNodes.VNode(context=c)
            root = leoNodes.Position(v)
        # Similar to g.getScript.
        script = at.stringToString(
            root=root,
            s=script,
            forcePythonSentinels=True,
            sentinels=False,
        )
        script = script.replace("\r\n", "\n")
        try:
            exec(script, c.abbrev_subst_env, c.abbrev_subst_env)
        except Exception:
            g.es('Error executing @data abbreviations-subst-env')
            g.es_exception()

    # @+node:ekr.20150514043850.8: *4* abbrev.init_settings
    def init_settings(self) -> None:
        """Called from AbbrevCommands.reload_settings aka reloadSettings."""
        c = self.c
        if not c.config:
            return
        getBool, getString = c.config.getBool, c.config.getString

        # Local settings. Normally not accessed via c.abbrev_subst_env.
        self.scripting_enabled = (
            getBool('scripting-at-script-nodes') or
            getBool('scripting-abbreviations')
        )  # fmt: skip
        self.globalDynamicAbbrevs = getBool('global-dynamic-abbrevs')

        # Allow @data abbreviations-subst-env *only* in leoSettings.leo or myLeoSettings.leo!
        key = 'abbreviations-subst-env'
        if c.config.isLocalSetting(key, 'data'):
            g.issueSecurityWarning(f"@data {key}")
            self.subst_env = []
        else:
            self.subst_env = c.config.getData(key, strip_data=False)

        # Inject one ivar.
        c.k.abbrevOn = getBool('enable-abbreviations', default=False)

        # Commander ivars for scripting environments, unit tests, etc.
        c.abbrev_place_end = getString('abbreviations-place-end') or '|>'
        c.abbrev_place_start = getString('abbreviations-place-start') or '<|'
        c.abbrev_subst_env = {'c': c, 'g': g, '_values': {}}  # May be augmented in init_env.
        c.abbrev_subst_start = getString('abbreviations-subst-start') or '{|{'
        c.abbrev_subst_end = getString('abbreviations-subst-end') or '}|}'

    # @+node:ekr.20150514043850.9: *4* abbrev.init_tree_abbrev
    def init_tree_abbrev(self) -> None:
        """Init tree_abbrevs_d from @data tree-abbreviations nodes."""
        c = self.c
        #
        # Careful. This happens early in startup.
        root = c.rootPosition()
        if not root:
            return
        if not c.p:
            c.selectPosition(root)
        if not c.p:
            return
        data = c.config.getOutlineData('tree-abbreviations')
        if data is None:
            return
        d: dict[str, str] = {}
        # #904: data may be a string or a list of two strings.
        aList = [data] if isinstance(data, str) else data
        for tree_s in aList:
            #
            # Expand the tree so we can traverse it.
            if not c.canPasteOutline(tree_s):
                return
            c.fileCommands.leo_file_encoding = 'utf-8'
            #
            # As part of #427, disable all redraws.
            old_disable = g.app.disable_redraw
            try:
                g.app.disable_redraw = True
                self.init_tree_abbrev_helper(d, tree_s)
            finally:
                g.app.disable_redraw = old_disable
        self.tree_abbrevs_d = d

    # @+node:ekr.20170227062001.1: *5* abbrev.init_tree_abbrev_helper
    def init_tree_abbrev_helper(self, d: dict[str, str], tree_s: str) -> None:
        """Init d from tree_s, the text of a copied outline."""
        c = self.c
        hidden_root = c.fileCommands.getPosFromClipboard(tree_s)
        if not hidden_root:
            g.trace('no pasted node')
            return
        for p in hidden_root.children():
            for s in g.splitLines(p.b):
                if s.strip() and not s.startswith('#'):
                    abbrev_name = s.strip()
                    # #926: Allow organizer nodes by searching all descendants.
                    for child in p.subtree():
                        if child.h.strip() == abbrev_name:
                            abbrev_s = c.fileCommands.outline_to_clipboard_string(child)
                            d[abbrev_name] = abbrev_s
                            break
                    else:
                        g.trace(f"no definition for {abbrev_name}")

    # @+node:ekr.20260511152312.1: *3* abbrev: Commands & helpers
    # @+node:ekr.20150514043850.23: *4* abbrev._getDynamicList (helper)
    def _getDynamicList(self, w: QTextMixin, s: str) -> list[str]:
        """Return a list of dynamic abbreviations."""
        if self.globalDynamicAbbrevs:
            # Look in all nodes.h
            items = []
            for p in self.c.all_unique_positions():
                items.extend(self.dyna_regex.findall(p.b))
        else:
            # Just look in this node.
            items = self.dyna_regex.findall(w.getAllText())
        items = sorted(set([z for z in items if z.startswith(s)]))
        return items

    # @+node:ekr.20150514043850.20: *4* abbrev.dynamicCompletion C-M-/
    @cmd('dabbrev-completion')
    def dynamicCompletion(self, event: LeoKeyEvent = None) -> None:
        """
        dabbrev-completion
        Insert the common prefix of all dynamic abbrev's matching the present word.
        This corresponds to C-M-/ in Emacs.
        """
        c, p = self.c, self.c.p
        w = event.w if event else c.frame.body.wrapper
        if not g.isTextWrapper(w):
            return
        s = w.getAllText()
        ins = ins1 = w.getInsertPoint()
        if 0 < ins < len(s) and not g.isWordChar(s[ins]):
            ins1 -= 1
        i, j = g.getWord(s, ins1)
        word = w.get(i, j)
        aList = self._getDynamicList(w, word)
        if not aList:
            return
        # Bug fix: remove s itself, otherwise we can not extend beyond it.
        if word in aList and len(aList) > 1:
            aList.remove(word)
        prefix = functools.reduce(g.longestCommonPrefix, aList)
        if prefix.strip():
            ypos = w.getYScrollPosition()
            b = c.undoer.beforeChangeNodeContents(p)
            s = s[:i] + prefix + s[j:]
            w.setAllText(s)
            w.setInsertPoint(i + len(prefix))
            w.setYScrollPosition(ypos)
            c.undoer.afterChangeNodeContents(p, command='dabbrev-completion', bunch=b)
            c.recolor()

    # @+node:ekr.20150514043850.21: *4* abbrev.dynamicExpansion M-/ & helper
    @cmd('dabbrev-expands')
    def dynamicExpansion(self, event: LeoKeyEvent = None) -> None:
        """
        dabbrev-expands (M-/ in Emacs).

        Inserts the longest common prefix of the word at the cursor. Displays
        all possible completions if the prefix is the same as the word.
        """
        c = self.c
        w = event.w if event else c.frame.body.wrapper
        if not g.isTextWrapper(w):
            return
        s = w.getAllText()
        ins = ins1 = w.getInsertPoint()
        if 0 < ins < len(s) and not g.isWordChar(s[ins]):
            ins1 -= 1
        i, j = g.getWord(s, ins1)
        # This allows the cursor to be placed anywhere in the word.
        w.setInsertPoint(j)
        word = w.get(i, j)
        aList = self._getDynamicList(w, word)
        if not aList:
            return
        if word in aList and len(aList) > 1:
            aList.remove(word)
        prefix = functools.reduce(g.longestCommonPrefix, aList)
        prefix = prefix.strip()
        self.dynamicExpandHelper(event, prefix, aList, w)

    # @+node:ekr.20150514043850.22: *5* abbrev.dynamicExpandHelper
    def dynamicExpandHelper(
        self,
        event: LeoKeyEvent,
        prefix: str = None,
        aList: list[str] = None,
        w: QTextMixin = None,
    ) -> None:
        """State handler for dabbrev-expands command."""
        c, k = self.c, self.c.k
        self.w = w
        if prefix is None:
            prefix = ''
        prefix2 = 'dabbrev-expand: '
        c.frame.log.deleteTab('Completion')
        g.es('', '\n'.join(aList or []), tabName='Completion')
        # Protect only prefix2 so tab completion and backspace to work properly.
        k.setLabelBlue(prefix2, protect=True)
        k.setLabelBlue(prefix2 + prefix, protect=False)
        k.get1Arg(event, handler=self.dynamicExpandHelper1, tabList=aList, prefix=prefix)

    def dynamicExpandHelper1(self, event: LeoKeyEvent) -> None:
        """Finisher for dabbrev-expands."""
        c, k = self.c, self.c.k
        p = c.p
        c.frame.log.deleteTab('Completion')
        k.clearState()
        k.resetLabel()
        if k.arg:
            w = self.w
            s = w.getAllText()
            ypos = w.getYScrollPosition()
            b = c.undoer.beforeChangeNodeContents(p)
            ins = ins1 = w.getInsertPoint()
            if 0 < ins < len(s) and not g.isWordChar(s[ins]):
                ins1 -= 1
            i, j = g.getWord(s, ins1)
            # word = s[i: j]
            s = s[:i] + k.arg + s[j:]
            w.setAllText(s)
            w.setInsertPoint(i + len(k.arg))
            w.setYScrollPosition(ypos)
            c.undoer.afterChangeNodeContents(p, command='dabbrev-expand', bunch=b)
            c.recolor()

    # @+node:ekr.20150514043850.28: *4* abbrev.killAllAbbrevs
    @cmd('abbrev-kill-all')
    def killAllAbbrevs(self, event: LeoKeyEvent) -> None:
        """Delete all abbreviations."""
        self.abbrevs = {}

    # @+node:ekr.20150514043850.29: *4* abbrev.listAbbrevs
    @cmd('abbrev-list')
    def listAbbrevs(self, event: LeoKeyEvent = None) -> None:
        """List all abbreviations."""
        d = self.abbrevs
        if not d:
            return
        g.es_print('')
        g.es_print(f"Abbreviations for {self.c.shortFileName()}...")
        for name, s in sorted(d.items()):
            s = s.replace('\n', '\\n')
            tail = s.removesuffix('\\n')
            g.es_print(f"{name:>15} {g.truncate(tail, 90)}")

    # @+node:ekr.20150514043850.32: *4* abbrev.toggleAbbrevMode
    @cmd('toggle-abbrev-mode')
    def toggleAbbrevMode(self, event: LeoKeyEvent = None) -> None:
        """Toggle abbreviation mode."""
        k = self.c.k
        k.abbrevOn = not k.abbrevOn
        k.keyboardQuit()
        if not g.unitTesting and not g.app.batchMode:
            g.es('Abbreviations are ' + ('on' if k.abbrevOn else 'off'))

    # @-others


# @-others
# @-leo
