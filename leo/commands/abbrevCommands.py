#@+leo-ver=5-thin
#@+node:ekr.20150514035236.1: * @file ../commands/abbrevCommands.py
"""Leo's abbreviations commands."""
#@+<< abbrevCommands imports & abbreviations >>
#@+node:ekr.20150514045700.1: ** << abbrevCommands imports & abbreviations >>
from __future__ import annotations
from collections.abc import Callable
import functools
import re
import string
from typing import Any, TYPE_CHECKING
from leo.core import leoGlobals as g
from leo.core import leoNodes
from leo.commands.baseCommands import BaseEditCommandsClass

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent as Event
    from leo.core.leoNodes import Position
    from leo.plugins.qt_text import QTextEditWrapper as Wrapper
    Stroke = Any
#@-<< abbrevCommands imports & abbreviations >>

def cmd(name: str) -> Callable:
    """Command decorator for the abbrevCommands class."""
    return g.new_cmd_decorator(name, ['c', 'abbrevCommands',])

#@+others
#@+node:ekr.20160514095531.1: ** class AbbrevCommands
class AbbrevCommandsClass(BaseEditCommandsClass):
    """
    A class to handle user-defined abbreviations.
    See apropos-abbreviations for details.
    """
    #@+others
    #@+node:ekr.20150514043850.2: *3* abbrev.Birth
    #@+node:ekr.20150514043850.3: *4* abbrev.ctor
    def __init__(self, c: Cmdr) -> None:
        """Ctor for AbbrevCommandsClass class."""
        # pylint: disable=super-init-not-called
        self.c = c
        # Set local ivars.
        self.abbrevs: dict[str, tuple[str, str]] = {}  # Keys are names, values are (abbrev,tag).
        self.dynaregex = re.compile(  # For dynamic abbreviations
            r'[%s%s\-_]+' % (string.ascii_letters, string.digits))
            # Not a unicode problem.
        self.n_regex = re.compile(r'(?<!\\)\\n')  # to replace \\n but not \\\\n
        self.expanding = False  # True: expanding abbreviations.
        self.event = None
        self.last_hit = None  # Distinguish between text and tree abbreviations.
        self.root = None  # The root of tree abbreviations.
        self.save_ins = None  # Saved insert point.
        self.save_sel = None  # Saved selection range.
        self.store = {'rlist': [], 'stext': ''}  # For dynamic expansion.
        self.tree_abbrevs_d: dict[str, str] = {}  # Keys are names, values are (tree,tag).
        self.w = None
    #@+node:ekr.20150514043850.5: *4* abbrev.finishCreate & helpers
    def finishCreate(self) -> None:
        """AbbrevCommandsClass.finishCreate."""
        self.reload_settings()
    #@+node:ekr.20170221035644.1: *5* abbrev.reload_settings & helpers
    def reload_settings(self) -> None:
        """Reload all abbreviation settings."""
        self.abbrevs = {}
        self.init_settings()
        self.init_abbrev()
        self.init_tree_abbrev()
        self.init_env()

    reloadSettings = reload_settings
    #@+node:ekr.20150514043850.6: *6* abbrev.init_abbrev
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
            for s in result:
                self.addAbbrevHelper(s, tag)

        # fake the next placeholder abbreviation
        if c.config.getString("abbreviations-next-placeholder"):
            self.addAbbrevHelper(
                f'{c.config.getString("abbreviations-next-placeholder")}'
                f'=__NEXT_PLACEHOLDER',
                'global')
    #@+node:ekr.20150514043850.7: *6* abbrev.init_env
    def init_env(self) -> None:
        """
        Init c.abbrev_subst_env by executing the contents of the
        @data abbreviations-subst-env node.
        """
        c = self.c
        at = c.atFileCommands
        if c.abbrev_place_start and self.enabled:
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
                sentinels=False)
            script = script.replace("\r\n", "\n")
            try:
                exec(script, c.abbrev_subst_env, c.abbrev_subst_env)  # type:ignore
            except Exception:
                g.es('Error exec\'ing @data abbreviations-subst-env')
                g.es_exception()
        else:
            c.abbrev_subst_start = ''  # Was False.
    #@+node:ekr.20150514043850.8: *6* abbrev.init_settings (called from reload_settings)
    def init_settings(self) -> None:
        """Called from AbbrevCommands.reload_settings aka reloadSettings."""
        c = self.c
        c.k.abbrevOn = c.config.getBool('enable-abbreviations', default=False)
        c.abbrev_place_end = c.config.getString('abbreviations-place-end')
        c.abbrev_place_start = c.config.getString('abbreviations-place-start')
        c.abbrev_subst_end = c.config.getString('abbreviations-subst-end')
        # The environment for all substitutions.
        # May be augmented in init_env.
        c.abbrev_subst_env = {'c': c, 'g': g, '_values': {},}
        c.abbrev_subst_start = c.config.getString('abbreviations-subst-start') or ''
        # Local settings.
        self.enabled = (
            c.config.getBool('scripting-at-script-nodes') or
            c.config.getBool('scripting-abbreviations'))
        self.globalDynamicAbbrevs = c.config.getBool('globalDynamicAbbrevs')
        #@verbatim
        # @data abbreviations-subst-env must *only* be defined in leoSettings.leo or myLeoSettings.leo!
        if c.config:
            key = 'abbreviations-subst-env'
            if c.config.isLocalSetting(key, 'data'):
                g.issueSecurityWarning(f"@data {key}")
                self.subst_env = ""
            else:
                self.subst_env = c.config.getData(key, strip_data=False)
    #@+node:ekr.20150514043850.9: *6* abbrev.init_tree_abbrev
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
    #@+node:ekr.20170227062001.1: *7* abbrev.init_tree_abbrev_helper
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
    #@+node:ekr.20150514043850.11: *3* abbrev.expandAbbrev & helpers (entry point)
    def expandAbbrev(self, event: Event, stroke: Stroke) -> bool:
        """
        Not a command.  Expand abbreviations in event.widget.

        Words start with '@'.
        """
        # Trace for *either* 'abbrev' or 'keys'
        trace = any(z in g.app.debug for z in ('abbrev', 'keys'))
        # Verbose only for *both* 'abbrev' and 'verbose'.
        verbose = all(z in g.app.debug for z in ('abbrev', 'verbose'))
        c, p = self.c, self.c.p
        w = self.editWidget(event, forceFocus=False)
        w_name = g.app.gui.widget_name(w)
        if not w:
            if trace and verbose:
                g.trace('no w')
            return False
        ch = self.get_ch(event, stroke, w)
        if not ch:
            if trace and verbose:
                g.trace('no ch')
            return False
        s, i, j, prefixes = self.get_prefixes(w)
        for prefix in prefixes:
            i, tag, word, val = self.match_prefix(ch, i, j, prefix, s)
            if word:
                # Fix another part of #438.
                if w_name.startswith('head'):
                    if val == '__NEXT_PLACEHOLDER':
                        i = w.getInsertPoint()
                        if i > 0:
                            w.delete(i - 1)
                            p.h = w.getAllText()
                    # Do not call c.endEditing here.
                break
        else:
            if trace and verbose:
                g.trace(f"No prefix in {s!r}")
            return False
        c.abbrev_subst_env['_abr'] = word
        if trace:
            g.trace(f"Found {word!r} = {val!r}")
        if tag == 'tree':
            self.root = p.copy()
            self.last_hit = p.copy()
            self.expand_tree(w, i, j, val, word)
        else:
            # Never expand a search for text matches.
            place_holder = '__NEXT_PLACEHOLDER' in val
            if place_holder:
                expand_search = bool(self.last_hit)
            else:
                self.last_hit = None
                expand_search = False
            self.expand_text(w, i, j, val, word, expand_search)
            # Restore the selection range.
            if self.save_ins:
                ins = self.save_ins
                # pylint: disable=unpacking-non-sequence
                sel1, sel2 = self.save_sel
                if sel1 == sel2:
                    # New in Leo 5.5
                    self.post_pass()
                else:
                    # some abbreviations *set* the selection range
                    # so only restore non-empty ranges
                    w.setSelectionRange(sel1, sel2, insert=ins)
        return True
    #@+node:ekr.20161121121636.1: *4* abbrev.exec_content
    def exec_content(self, content: str) -> None:
        """Execute the content in the environment, and return the result."""
    #@+node:ekr.20150514043850.12: *4* abbrev.expand_text
    def expand_text(self,
        w: Wrapper,
        i: int,
        j: int,
        val: str,
        word: str,
        expand_search: bool = False,
    ) -> None:
        """Make a text expansion at location i,j of widget w."""
        c = self.c
        if word == c.config.getString("abbreviations-next-placeholder"):
            val = ''
            do_placeholder = True
        else:
            val, do_placeholder = self.make_script_substitutions(i, j, val)
        self.replace_selection(w, i, j, val)
        # Search to the end.  We may have been called via a tree abbrev.
        p = c.p.copy()
        if expand_search:
            while p:
                if self.find_place_holder(p, do_placeholder):
                    return
                p.moveToThreadNext()
        else:
            self.find_place_holder(p, do_placeholder)
    #@+node:ekr.20150514043850.13: *4* abbrev.expand_tree (entry) & helpers
    def expand_tree(self, w: Wrapper, i: int, j: int, tree_s: str, word: str) -> None:
        """
        Paste tree_s as children of c.p.
        This happens *before* any substitutions are made.
        """
        c, u = self.c, self.c.undoer
        if not c.canPasteOutline(tree_s):
            g.trace(f"bad copied outline: {tree_s}")
            return
        old_p = c.p.copy()
        bunch = u.beforeChangeTree(old_p)
        self.replace_selection(w, i, j, None)
        self.paste_tree(old_p, tree_s)
        # Make all script substitutions first.
        # Original code.  Probably unwise to change it.
        do_placeholder = False
        for p in old_p.self_and_subtree():
            # Search for the next place-holder.
            val, do_placeholder = self.make_script_substitutions(0, 0, p.b)
            if not do_placeholder:
                p.b = val
        # Now search for all place-holders.
        for p in old_p.subtree():
            if self.find_place_holder(p, do_placeholder):
                break
        u.afterChangeTree(old_p, 'tree-abbreviation', bunch)
    #@+node:ekr.20150514043850.17: *5* abbrev.paste_tree
    def paste_tree(self, old_p: Position, s: str) -> None:
        """Paste the tree corresponding to s (xml) into the tree."""
        c = self.c
        c.fileCommands.leo_file_encoding = 'utf-8'
        p = c.pasteOutline(s=s, undoFlag=False)
        if p:
            # Promote the name node, then delete it.
            p.moveToLastChildOf(old_p)
            c.selectPosition(p)
            c.promote(undoFlag=False)
            p.doDelete()
            c.redraw(old_p)  # 2017/02/27: required.
        else:
            g.trace('paste failed')
    #@+node:ekr.20150514043850.14: *4* abbrev.find_place_holder
    def find_place_holder(self, p: Position, do_placeholder: bool) -> bool:
        """
        Search for the next place-holder.
        If found, select the place-holder (without the delims).
        """
        c, u = self.c, self.c.undoer
        # Do #438: Search for placeholder in headline.
        s = p.h
        if do_placeholder or c.abbrev_place_start and c.abbrev_place_start in s:
            new_s, i, j = self.next_place(s, offset=0)
            if i is not None:
                p.h = new_s
                c.redraw(p)
                c.editHeadline()
                w = c.edit_widget(p)
                w.setSelectionRange(i, j, insert=j)
                return True
        s = p.b
        if do_placeholder or c.abbrev_place_start and c.abbrev_place_start in s:
            new_s, i, j = self.next_place(s, offset=0)
            if i is None:
                return False
            w = c.frame.body.wrapper
            bunch = u.beforeChangeBody(c.p)
            switch = p != c.p
            if switch:
                c.selectPosition(p)
            else:
                scroll = w.getYScrollPosition()
            w.setAllText(new_s)
            p.v.b = new_s
            u.afterChangeBody(p, 'find-place-holder', bunch)
            if switch:
                c.redraw()
            w.setSelectionRange(i, j, insert=j)
            if switch:
                w.seeInsertPoint()
            else:
                # Keep the scroll point if possible.
                w.setYScrollPosition(scroll)
                w.seeInsertPoint()
            c.bodyWantsFocusNow()
            return True
        # #453: do nothing here.
            # c.frame.body.forceFullRecolor()
            # c.bodyWantsFocusNow()
        return False
    #@+node:ekr.20150514043850.15: *4* abbrev.make_script_substitutions
    def make_script_substitutions(self, i: int, j: int, val: str) -> tuple[str, bool]:
        """Make scripting substitutions in node p."""
        c, u, w = self.c, self.c.undoer, self.c.frame.body.wrapper
        if not c.abbrev_subst_start:
            return val, False
        # Nothing to undo.
        if c.abbrev_subst_start not in val:
            return val, False
        # The *before* snapshot.
        bunch = u.beforeChangeBody(c.p)
        # Perform all scripting substitutions.
        self.save_ins = None
        self.save_sel = None
        while c.abbrev_subst_start in val:
            prefix, rest = val.split(c.abbrev_subst_start, 1)
            content = rest.split(c.abbrev_subst_end, 1)
            if len(content) != 2:
                break
            content, rest = content  # type:ignore
            try:
                self.expanding = True
                c.abbrev_subst_env['x'] = ''
                exec(content, c.abbrev_subst_env, c.abbrev_subst_env)  # type:ignore
            except Exception:
                g.es_print('exception evaluating', content)
                g.es_exception()
            finally:
                self.expanding = False
            x = c.abbrev_subst_env.get('x')
            if x is None:
                x = ''
            val = f"{prefix}{x}{rest}"
            # Save the selection range.
            self.save_ins = w.getInsertPoint()
            self.save_sel = w.getSelectionRange()
        if val == "__NEXT_PLACEHOLDER":
            # user explicitly called for next placeholder in an abbrev.
            # inserted previously
            val = ''
            do_placeholder = True
        else:
            do_placeholder = False
            c.p.v.b = w.getAllText()
            u.afterChangeBody(c.p, 'make-script-substitution', bunch)
        return val, do_placeholder
    #@+node:ekr.20161121102113.1: *4* abbrev.make_script_substitutions_in_headline
    def make_script_substitutions_in_headline(self, p: Position) -> bool:
        """Make scripting substitutions in p.h."""
        c = self.c
        pattern = re.compile(r'^(.*)%s(.+)%s(.*)$' % (
            re.escape(c.abbrev_subst_start),
            re.escape(c.abbrev_subst_end),
        ))
        changed = False
        # Perform at most one scripting substition.
        m = pattern.match(p.h)
        if m:
            content = m.group(2)
            c.abbrev_subst_env['x'] = ''
            try:
                exec(content, c.abbrev_subst_env, c.abbrev_subst_env)
                x = c.abbrev_subst_env.get('x')
                if x:
                    p.h = f"{m.group(1)}{x}{m.group(3)}"
                    changed = True
            except Exception:
                # Leave p.h alone.
                g.trace('scripting error in', p.h)
                g.es_exception()
        return changed
    #@+node:ekr.20161121112837.1: *4* abbrev.match_prefix
    def match_prefix(self, ch: str, i: int, j: int, prefix: str, s: str) -> tuple[int, str, str, str]:
        """A match helper."""
        i = j - len(prefix)
        word = g.checkUnicode(prefix) + g.checkUnicode(ch)
        tag = 'tree'
        val = self.tree_abbrevs_d.get(word)
        if not val:
            val, tag = self.abbrevs.get(word, (None, None))
        if val:
            # Require a word match if the abbreviation is itself a word.
            if ch in ' \t\n':
                word = word.rstrip()
            if word.isalnum() and word[0].isalpha():
                if i == 0 or s[i - 1] in ' \t\n':
                    pass
                else:
                    i -= 1
                    word, val = None, None  # 2017/03/19.
        else:
            i -= 1
            word, val = None, None
        return i, tag, word, val
    #@+node:ekr.20150514043850.16: *4* abbrev.next_place
    def next_place(self, s: str, offset: int = 0) -> tuple[str, int, int]:
        """
        Given string s containing a placeholder like <| block |>,
        return (s2,start,end) where s2 is s without the <| and |>,
        and start, end are the positions of the beginning and end of block.
        """
        c = self.c
        if c.abbrev_place_start is None or c.abbrev_place_end is None:
            return s, None, None  # #1345.
        new_pos = s.find(c.abbrev_place_start, offset)
        new_end = s.find(c.abbrev_place_end, offset)
        if (new_pos < 0 or new_end < 0) and offset:
            new_pos = s.find(c.abbrev_place_start)
            new_end = s.find(c.abbrev_place_end)
            if not (new_pos < 0 or new_end < 0):
                g.es("Found earlier placeholder")
        if new_pos < 0 or new_end < 0:
            return s, None, None
        start = new_pos
        place_holder_delim = s[new_pos : new_end + len(c.abbrev_place_end)]
        place_holder = place_holder_delim[
            len(c.abbrev_place_start) : -len(c.abbrev_place_end)]
        s2 = s[:start] + place_holder + s[start + len(place_holder_delim) :]
        end = start + len(place_holder)
        return s2, start, end
    #@+node:ekr.20161121114504.1: *4* abbrev.post_pass
    def post_pass(self) -> None:
        """The post pass: make script substitutions in all headlines."""
        c = self.c
        if self.root:
            bunch = c.undoer.beforeChangeTree(c.p)
            changed = False
            for p in self.root.self_and_subtree():
                changed2 = self.make_script_substitutions_in_headline(p)
                changed = changed or changed2
            if changed:
                c.undoer.afterChangeTree(c.p, 'tree-post-abbreviation', bunch)
    #@+node:ekr.20150514043850.18: *4* abbrev.replace_selection
    def replace_selection(self, w: Wrapper, i: int, j: int, s: str) -> None:
        """Replace w[i:j] by s."""
        p, u = self.c.p, self.c.undoer
        w_name = g.app.gui.widget_name(w)
        bunch = u.beforeChangeBody(p)
        if i == j:
            abbrev = ''
        else:
            abbrev = w.get(i, j)
            w.delete(i, j)
        if s is not None:
            w.insert(i, s)
        if w_name.startswith('head'):
            pass  # Don't set p.h here!
        else:
            # Fix part of #438. Don't leave the headline.
            p.v.b = w.getAllText()
            u.afterChangeBody(p, 'Abbreviation', bunch)
        # Adjust self.save_sel & self.save_ins
        if s is not None and self.save_sel is not None:
            # pylint: disable=unpacking-non-sequence
            i, j = self.save_sel
            ins = self.save_ins
            delta = len(s) - len(abbrev)
            self.save_sel = i + delta, j + delta
            self.save_ins = ins + delta
    #@+node:ekr.20161121111502.1: *4* abbrev_get_ch
    def get_ch(self, event: Event, stroke: Stroke, w: Wrapper) -> str:
        """Get the ch from the stroke."""
        ch = g.checkUnicode(event and event.char or '')
        if self.expanding:
            return None
        if w.hasSelection():
            return None
        assert g.isStrokeOrNone(stroke), stroke
        if stroke in ('BackSpace', 'Delete'):
            return None
        d = {'Return': '\n', 'Tab': '\t', 'space': ' ', 'underscore': '_'}
        if stroke:
            ch = d.get(stroke.s, stroke.s)
            if len(ch) > 1:
                if (stroke.find('Ctrl+') > -1 or
                    stroke.find('Alt+') > -1 or
                    stroke.find('Meta+') > -1
                ):
                    ch = ''
                else:
                    ch = event.char if event else ''
        else:
            ch = event.char
        return ch
    #@+node:ekr.20161121112346.1: *4* abbrev_get_prefixes
    def get_prefixes(self, w: Wrapper) -> tuple[str, int, int, list[str]]:
        """Return the prefixes at the current insertion point of w."""
        # New code allows *any* sequence longer than 1 to be an abbreviation.
        # Any whitespace stops the search.
        s = w.getAllText()
        j = w.getInsertPoint()
        i, prefixes = j - 1, []
        while len(s) > i >= 0 and s[i] not in ' \t\n':
            prefixes.append(s[i:j])
            i -= 1
        prefixes = list(reversed(prefixes))
        if '' not in prefixes:
            prefixes.append('')
        return s, i, j, prefixes
    #@+node:ekr.20150514043850.19: *3* abbrev.dynamic abbreviation...
    #@+node:ekr.20150514043850.20: *4* abbrev.dynamicCompletion C-M-/
    @cmd('dabbrev-completion')
    def dynamicCompletion(self, event: Event = None) -> None:
        """
        dabbrev-completion
        Insert the common prefix of all dynamic abbrev's matching the present word.
        This corresponds to C-M-/ in Emacs.
        """
        c, p = self.c, self.c.p
        w = self.editWidget(event)
        if not w:
            return
        s = w.getAllText()
        ins = ins1 = w.getInsertPoint()
        if 0 < ins < len(s) and not g.isWordChar(s[ins]):
            ins1 -= 1
        i, j = g.getWord(s, ins1)
        word = w.get(i, j)
        aList = self.getDynamicList(w, word)
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
    #@+node:ekr.20150514043850.21: *4* abbrev.dynamicExpansion M-/ & helper
    @cmd('dabbrev-expands')
    def dynamicExpansion(self, event: Event = None) -> None:
        """
        dabbrev-expands (M-/ in Emacs).

        Inserts the longest common prefix of the word at the cursor. Displays
        all possible completions if the prefix is the same as the word.
        """
        w = self.editWidget(event)
        if not w:
            return
        s = w.getAllText()
        ins = ins1 = w.getInsertPoint()
        if 0 < ins < len(s) and not g.isWordChar(s[ins]):
            ins1 -= 1
        i, j = g.getWord(s, ins1)
        # This allows the cursor to be placed anywhere in the word.
        w.setInsertPoint(j)
        word = w.get(i, j)
        aList = self.getDynamicList(w, word)
        if not aList:
            return
        if word in aList and len(aList) > 1:
            aList.remove(word)
        prefix = functools.reduce(g.longestCommonPrefix, aList)
        prefix = prefix.strip()
        self.dynamicExpandHelper(event, prefix, aList, w)
    #@+node:ekr.20150514043850.22: *5* abbrev.dynamicExpandHelper
    def dynamicExpandHelper(self,
        event: Event,
        prefix: str = None,
        aList: list[str] = None,
        w: Wrapper = None,
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

    def dynamicExpandHelper1(self, event: Event) -> None:
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
    #@+node:ekr.20150514043850.23: *4* abbrev.getDynamicList (helper)
    def getDynamicList(self, w: Wrapper, s: str) -> list[str]:
        """Return a list of dynamic abbreviations."""
        if self.globalDynamicAbbrevs:
            # Look in all nodes.h
            items = []
            for p in self.c.all_unique_positions():
                items.extend(self.dynaregex.findall(p.b))
        else:
            # Just look in this node.
            items = self.dynaregex.findall(w.getAllText())
        items = sorted(set([z for z in items if z.startswith(s)]))
        return items
    #@+node:ekr.20150514043850.24: *3* abbrev.static abbrevs
    #@+node:ekr.20150514043850.25: *4* abbrev.addAbbrevHelper
    def addAbbrevHelper(self, s: str, tag: str = '') -> None:
        """Enter the abbreviation 's' into the self.abbrevs dict."""
        if not s.strip():
            return
        try:
            d = self.abbrevs
            data = s.split('=')
            # Do *not* strip ws so the user can specify ws.
            name = data[0].replace('\\t', '\t').replace('\\n', '\n')
            val = '='.join(data[1:])
            if val.endswith('\n'):
                val = val[:-1]
            val = self.n_regex.sub('\n', val).replace('\\\\n', '\\n')
            old, tag = d.get(name, (None, None),)
            if old and old != val and not g.unitTesting:
                g.es_print('redefining abbreviation', name,
                    '\nfrom', repr(old), 'to', repr(val))
            d[name] = val, tag
        except ValueError:
            g.es_print(f"bad abbreviation: {s}")
    #@+node:ekr.20150514043850.28: *4* abbrev.killAllAbbrevs
    @cmd('abbrev-kill-all')
    def killAllAbbrevs(self, event: Event) -> None:
        """Delete all abbreviations."""
        self.abbrevs = {}
    #@+node:ekr.20150514043850.29: *4* abbrev.listAbbrevs
    @cmd('abbrev-list')
    def listAbbrevs(self, event: Event = None) -> None:
        """List all abbreviations."""
        d = self.abbrevs
        if d:
            g.es_print('Abbreviations...')
            keys = list(d.keys())
            keys.sort()
            for name in keys:
                val, tag = d.get(name)
                val = val.replace('\n', '\\n')
                tag = tag or ''
                tag = tag + ': ' if tag else ''
                g.es_print('', f"{tag}{name}={val}")
        else:
            g.es_print('No present abbreviations')
    #@+node:ekr.20150514043850.32: *4* abbrev.toggleAbbrevMode
    @cmd('toggle-abbrev-mode')
    def toggleAbbrevMode(self, event: Event = None) -> None:
        """Toggle abbreviation mode."""
        k = self.c.k
        k.abbrevOn = not k.abbrevOn
        k.keyboardQuit()
        if not g.unitTesting and not g.app.batchMode:
            g.es('Abbreviations are ' + 'on' if k.abbrevOn else 'off')
    #@-others
#@-others
#@-leo
