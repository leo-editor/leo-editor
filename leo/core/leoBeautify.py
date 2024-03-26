#@+leo-ver=5-thin
#@+node:ekr.20150521115018.1: * @file leoBeautify.py
"""Leo's beautification classes."""
#@+<< leoBeautify imports & annotations >>
#@+node:ekr.20220822114944.1: ** << leoBeautify imports & annotations >>
from __future__ import annotations
import sys
import os
import time
from typing import Any, Union, TYPE_CHECKING
# Third-party tools.
try:
    import black
except Exception:
    black = None  # type:ignore
# Leo imports.
from leo.core import leoGlobals as g
from leo.core import leoAst

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent
    from leo.core.leoNodes import Position
#@-<< leoBeautify imports & annotations >>

#@+others
#@+node:ekr.20191104201534.1: **   Top-level functions (leoBeautify.py)
#@+node:ekr.20150528131012.1: *3* Beautify:commands
#@+node:ekr.20150528131012.3: *4* beautify-c
@g.command('beautify-c')
@g.command('pretty-print-c')
def beautifyCCode(event: LeoKeyEvent) -> None:
    """Beautify all C code in the selected tree."""
    c = event.get('c')
    if c:
        CPrettyPrinter(c).pretty_print_tree(c.p)
#@+node:ekr.20200107165628.1: *4* beautify-file-diff
@g.command('diff-beautify-files')
@g.command('beautify-files-diff')
def orange_diff_files(event: LeoKeyEvent) -> None:
    """
    Show the diffs that would result from beautifying the external files at
    c.p.
    """
    c = event.get('c')
    if not c or not c.p:
        return
    t1 = time.process_time()
    tag = 'beautify-files-diff'
    g.es(f"{tag}...")
    settings = orange_settings(c)
    roots = g.findRootsWithPredicate(c, c.p)
    for root in roots:
        filename = c.fullPath(root)
        if os.path.exists(filename):
            print('')
            print(f"{tag}: {g.shortFileName(filename)}")
            changed = leoAst.Orange(settings=settings).beautify_file_diff(filename)
            changed_s = 'changed' if changed else 'unchanged'
            g.es(f"{changed_s:>9}: {g.shortFileName(filename)}")
        else:
            print('')
            print(f"{tag}: file not found:{filename}")
            g.es(f"file not found:\n{filename}")
    t2 = time.process_time()
    print('')
    g.es_print(f"{tag}: {len(roots)} file{g.plural(len(roots))} in {t2 - t1:5.2f} sec.")
#@+node:ekr.20200107165603.1: *4* beautify-files
@g.command('beautify-files')
def orange_files(event: LeoKeyEvent) -> None:
    """beautify one or more files at c.p."""
    c = event.get('c')
    if not c or not c.p:
        return
    t1 = time.process_time()
    tag = 'beautify-files'
    g.es(f"{tag}...")
    settings = orange_settings(c)
    roots = g.findRootsWithPredicate(c, c.p)
    n_changed = 0
    for root in roots:
        filename = c.fullPath(root)
        if os.path.exists(filename):
            changed = leoAst.Orange(settings=settings).beautify_file(filename)
            if changed:
                n_changed += 1
        else:
            g.es_print(f"file not found: {filename}")
    t2 = time.process_time()
    print('')
    g.es_print(
        f"total files: {len(roots)}, "
        f"changed files: {n_changed}, "
        f"in {t2 - t1:5.2f} sec.")
#@+node:ekr.20200103055814.1: *4* blacken-files
@g.command('blacken-files')
def blacken_files(event: LeoKeyEvent) -> None:
    """Run black on one or more files at c.p."""
    tag = 'blacken-files'
    if not black:
        g.es_print(f"{tag} can not import black")
        return
    c = event.get('c')
    if not c or not c.p:
        return
    python = sys.executable
    for root in g.findRootsWithPredicate(c, c.p):
        path = c.fullPath(root)
        if path and os.path.exists(path):
            g.es_print(f"{tag}: {path}")
            g.execute_shell_commands(f'&"{python}" -m black --skip-string-normalization "{path}"')
        else:
            print(f"{tag}: file not found:{path}")
            g.es(f"{tag}: file not found:\n{path}")
#@+node:ekr.20200103060057.1: *4* blacken-files-diff
@g.command('blacken-files-diff')
def blacken_files_diff(event: LeoKeyEvent) -> None:
    """
    Show the diffs that would result from blacking the external files at
    c.p.
    """
    tag = 'blacken-files-diff'
    if not black:
        g.es_print(f"{tag} can not import black")
        return
    c = event.get('c')
    if not c or not c.p:
        return
    python = sys.executable
    for root in g.findRootsWithPredicate(c, c.p):
        path = c.fullPath(root)
        if path and os.path.exists(path):
            g.es_print(f"{tag}: {path}")
            g.execute_shell_commands(f'&"{python}" -m black --skip-string-normalization --diff "{path}"')
        else:
            print(f"{tag}: file not found:{path}")
            g.es(f"{tag}: file not found:\n{path}")
#@+node:ekr.20191025072511.1: *4* fstringify-files
@g.command('fstringify-files')
def fstringify_files(event: LeoKeyEvent) -> None:
    """fstringify one or more files at c.p."""
    c = event.get('c')
    if not c or not c.p:
        return
    t1 = time.process_time()
    tag = 'fstringify-files'
    g.es(f"{tag}...")
    roots = g.findRootsWithPredicate(c, c.p)
    n_changed = 0
    for root in roots:
        filename = c.fullPath(root)
        if os.path.exists(filename):
            print('')
            print(g.shortFileName(filename))
            changed = leoAst.Fstringify().fstringify_file(filename)
            changed_s = 'changed' if changed else 'unchanged'
            if changed:
                n_changed += 1
            g.es_print(f"{changed_s:>9}: {g.shortFileName(filename)}")
        else:
            print('')
            print(f"File not found:{filename}")
            g.es(f"File not found:\n{filename}")
    t2 = time.process_time()
    print('')
    g.es_print(
        f"total files: {len(roots)}, "
        f"changed files: {n_changed}, "
        f"in {t2 - t1:5.2f} sec.")
#@+node:ekr.20200103055858.1: *4* fstringify-files-diff
@g.command('diff-fstringify-files')
@g.command('fstringify-files-diff')
def fstringify_diff_files(event: LeoKeyEvent) -> None:
    """
    Show the diffs that would result from fstringifying the external files at
    c.p.
    """
    c = event.get('c')
    if not c or not c.p:
        return
    t1 = time.process_time()
    tag = 'fstringify-files-diff'
    g.es(f"{tag}...")
    roots = g.findRootsWithPredicate(c, c.p)
    for root in roots:
        filename = c.fullPath(root)
        if os.path.exists(filename):
            print('')
            print(g.shortFileName(filename))
            changed = leoAst.Fstringify().fstringify_file_diff(filename)
            changed_s = 'changed' if changed else 'unchanged'
            g.es_print(f"{changed_s:>9}: {g.shortFileName(filename)}")
        else:
            print('')
            print(f"File not found:{filename}")
            g.es(f"File not found:\n{filename}")
    t2 = time.process_time()
    print('')
    g.es_print(f"{len(roots)} file{g.plural(len(roots))} in {t2 - t1:5.2f} sec.")
#@+node:ekr.20200112060001.1: *4* fstringify-files-silent
@g.command('silent-fstringify-files')
@g.command('fstringify-files-silent')
def fstringify_files_silent(event: LeoKeyEvent) -> None:
    """Silently fstringifying the external files at c.p."""
    c = event.get('c')
    if not c or not c.p:
        return
    t1 = time.process_time()
    tag = 'silent-fstringify-files'
    g.es(f"{tag}...")
    n_changed = 0
    roots = g.findRootsWithPredicate(c, c.p)
    for root in roots:
        filename = c.fullPath(root)
        if os.path.exists(filename):
            changed = leoAst.Fstringify().fstringify_file_silent(filename)
            if changed:
                n_changed += 1
        else:
            print('')
            print(f"File not found:{filename}")
            g.es(f"File not found:\n{filename}")
    t2 = time.process_time()
    print('')
    n_tot = len(roots)
    g.es_print(
        f"{n_tot} total file{g.plural(len(roots))}, "
        f"{n_changed} changed file{g.plural(n_changed)} "
        f"in {t2 - t1:5.2f} sec.")
#@+node:ekr.20200108045048.1: *4* orange_settings
def orange_settings(c: Cmdr) -> dict[str, Any]:
    """Return a dictionary of settings for the leo.core.leoAst.Orange class."""
    allow_joined_strings = c.config.getBool(
        'beautify-allow-joined-strings', default=False)
    n_max_join = c.config.getInt('beautify-max-join-line-length')
    max_join_line_length = 88 if n_max_join is None else n_max_join
    n_max_split = c.config.getInt('beautify-max-split-line-length')
    max_split_line_length = 88 if n_max_split is None else n_max_split
    # Join <= Split.
    # pylint: disable=consider-using-min-builtin
    if max_join_line_length > max_split_line_length:
        max_join_line_length = max_split_line_length
    return {
        'allow_joined_strings': allow_joined_strings,
        'max_join_line_length': max_join_line_length,
        'max_split_line_length': max_split_line_length,
        'tab_width': abs(c.tab_width),
    }
#@+node:ekr.20191028140926.1: *3* Beautify:test functions
#@+node:ekr.20191029184103.1: *4* function: show
def show(obj: Any, tag: str, dump: bool) -> None:
    print(f"{tag}...\n")
    if dump:
        g.printObj(obj)
    else:
        print(obj)
#@+node:ekr.20150602154951.1: *3* function: should_beautify
def should_beautify(p: Position) -> bool:
    """
    Return True if @beautify is in effect for node p.
    Ambiguous directives have no effect.
    """
    for p2 in p.self_and_parents(copy=False):
        d = g.get_directives_dict(p2)
        if 'killbeautify' in d:
            return False
        if 'beautify' in d and 'nobeautify' in d:
            if p == p2:
                # honor whichever comes first.
                for line in g.splitLines(p2.b):
                    if line.startswith('@beautify'):
                        return True
                    if line.startswith('@nobeautify'):
                        return False
                g.trace('can not happen', p2.h)
                return False
            # The ambiguous node has no effect.
            # Look up the tree.
            pass
        elif 'beautify' in d:
            return True
        if 'nobeautify' in d:
            # This message would quickly become annoying.
            # g.warning(f"{p.h}: @nobeautify")
            return False
    # The default is to beautify.
    return True
#@+node:ekr.20150602204440.1: *3* function: should_kill_beautify
def should_kill_beautify(p: Position) -> bool:
    """Return True if p.b contains @killbeautify"""
    return 'killbeautify' in g.get_directives_dict(p)
#@+node:ekr.20110917174948.6903: ** class CPrettyPrinter
class CPrettyPrinter:
    #@+others
    #@+node:ekr.20110917174948.6904: *3* cpp.__init__
    def __init__(self, c: Cmdr) -> None:
        """Ctor for CPrettyPrinter class."""
        self.c = c
        self.brackets = 0  # The brackets indentation level.
        self.p: Position = None  # Set in indent.
        self.parens = 0  # The parenthesis nesting level.
        self.result: list[Any] = []  # The list of tokens that form the final result.
        self.tab_width = 4  # The number of spaces in each unit of leading indentation.
    #@+node:ekr.20191104195610.1: *3* cpp.pretty_print_tree
    def pretty_print_tree(self, p: Position) -> None:

        c = self.c
        if should_kill_beautify(p):
            return
        u, undoType = c.undoer, 'beautify-c'
        u.beforeChangeGroup(c.p, undoType)
        changed = False
        for p in c.p.self_and_subtree():
            if g.scanForAtLanguage(c, p) == "c":
                bunch = u.beforeChangeNodeContents(p)
                s = self.indent(p)
                if p.b != s:
                    p.b = s
                    p.setDirty()
                    u.afterChangeNodeContents(p, undoType, bunch)
                    changed = True
        # Call this only once, at end.
        u.afterChangeGroup(c.p, undoType)
        if not changed:
            g.es("Command did not find any content to beautify")
        c.bodyWantsFocus()
    #@+node:ekr.20110917174948.6911: *3* cpp.indent & helpers
    def indent(self, p: Position, toList: bool = False, giveWarnings: bool = True) -> Union[str, list[str]]:
        """Beautify a node with @language C in effect."""
        if not should_beautify(p):
            return [] if toList else ''  # #2271
        if not p.b:
            return [] if toList else ''  # #2271
        self.p = p.copy()
        aList = self.tokenize(p.b)
        assert ''.join(aList) == p.b
        ### This type mismatch looks serious. Tests needed!
        aList = self.add_statement_braces(aList, giveWarnings=giveWarnings)  # type:ignore
        self.bracketLevel = 0
        self.parens = 0
        self.result = []
        for s in aList:
            self.put_token(s)
        return self.result if toList else ''.join(self.result)
    #@+node:ekr.20110918225821.6815: *4* cpp.add_statement_braces
    def add_statement_braces(self, s: str, giveWarnings: bool = False) -> list[str]:
        p = self.p

        def oops(message: str, i: int, j: int) -> None:
            # This can be called from c-to-python, in which case warnings should be suppressed.
            if giveWarnings:
                g.error('** changed ', p.h)
                g.es_print(f'{message} after\n{repr("".join(s[i:j]))}')

        i, n = 0, len(s)
        result: list[str] = []
        while i < n:
            token = s[i]
            progress = i
            if token in ('if', 'for', 'while'):
                j = self.skip_ws_and_comments(s, i + 1)
                if self.match(s, j, '('):
                    j = self.skip_parens(s, j)
                    if self.match(s, j, ')'):
                        old_j = j + 1
                        j = self.skip_ws_and_comments(s, j + 1)
                        if self.match(s, j, ';'):
                            # Example: while (*++prefix);
                            result.extend(s[i:j])
                        elif self.match(s, j, '{'):
                            result.extend(s[i:j])
                        else:
                            oops("insert '{'", i, j)
                            # Back up, and don't go past a newline or comment.
                            j = self.skip_ws(s, old_j)
                            result.extend(s[i:j])
                            result.append(' ')
                            result.append('{')
                            result.append('\n')
                            i = j
                            j = self.skip_statement(s, i)
                            result.extend(s[i:j])
                            result.append('\n')
                            result.append('}')
                            oops("insert '}'", i, j)
                    else:
                        oops("missing ')'", i, j)
                        result.extend(s[i:j])
                else:
                    oops("missing '('", i, j)
                    result.extend(s[i:j])
                i = j
            else:
                result.append(token)
                i += 1
            assert progress < i
        return result
    #@+node:ekr.20110919184022.6903: *5* cpp.skip_ws
    def skip_ws(self, s: str, i: int) -> int:
        while i < len(s):
            token = s[i]
            if token.startswith(' ') or token.startswith('\t'):
                i += 1
            else:
                break
        return i
    #@+node:ekr.20110918225821.6820: *5* cpp.skip_ws_and_comments
    def skip_ws_and_comments(self, s: str, i: int) -> int:
        while i < len(s):
            token = s[i]
            if token.isspace():
                i += 1
            elif token.startswith('//') or token.startswith('/*'):
                i += 1
            else:
                break
        return i
    #@+node:ekr.20110918225821.6817: *5* cpp.skip_parens
    def skip_parens(self, s: str, i: int) -> int:
        """Skips from the opening ( to the matching ).

        If no matching is found i is set to len(s)"""
        assert self.match(s, i, '(')
        level = 0
        while i < len(s):
            ch = s[i]
            if ch == '(':
                level += 1
                i += 1
            elif ch == ')':
                level -= 1
                if level <= 0:
                    return i
                i += 1
            else:
                i += 1
        return i
    #@+node:ekr.20110918225821.6818: *5* cpp.skip_statement
    def skip_statement(self, s: str, i: int) -> int:
        """Skip to the next ';' or '}' token."""
        while i < len(s):
            if s[i] in ';}':
                i += 1
                break
            else:
                i += 1
        return i
    #@+node:ekr.20110917204542.6967: *4* cpp.put_token & helpers
    def put_token(self, s: str) -> None:
        """Append token s to self.result as is,
        *except* for adjusting leading whitespace and comments.

        '{' tokens bump self.brackets or self.ignored_brackets.
        self.brackets determines leading whitespace.
        """
        if s == '{':
            self.brackets += 1
        elif s == '}':
            self.brackets -= 1
            self.remove_indent()
        elif s == '(':
            self.parens += 1
        elif s == ')':
            self.parens -= 1
        elif s.startswith('\n'):
            if self.parens <= 0:
                s = f'\n{" "*self.brackets*self.tab_width}'
            else:
                pass  # Use the existing indentation.
        elif s.isspace():
            if self.parens <= 0 and self.result and self.result[-1].startswith('\n'):
                # Kill the whitespace.
                s = ''
            else:
                pass  # Keep the whitespace.
        elif s.startswith('/*'):
            s = self.reformat_block_comment(s)
        else:
            pass  # put s as it is.
        if s:
            self.result.append(s)
    #@+node:ekr.20110917204542.6968: *5* prev_token
    def prev_token(self, s: str) -> bool:
        """Return the previous token, ignoring whitespace and comments."""
        i = len(self.result) - 1
        while i >= 0:
            s2 = self.result[i]
            if s == s2:
                return True
            if s.isspace() or s.startswith('//') or s.startswith('/*'):
                i -= 1
            else:
                return False
        return False
    #@+node:ekr.20110918184425.6916: *5* reformat_block_comment
    def reformat_block_comment(self, s: str) -> str:
        return s
    #@+node:ekr.20110917204542.6969: *5* remove_indent
    def remove_indent(self) -> None:
        """Remove one tab-width of blanks from the previous token."""
        w = abs(self.tab_width)
        if self.result:
            s = self.result[-1]
            if s.isspace():
                self.result.pop()
                s = s.replace('\t', ' ' * w)
                if s.startswith('\n'):
                    s2 = s[1:]
                    self.result.append('\n' + s2[:-w])
                else:
                    self.result.append(s[:-w])
    #@+node:ekr.20110918225821.6819: *3* cpp.match
    def match(self, s: str, i: int, pat: str) -> bool:
        return i < len(s) and s[i] == pat
    #@+node:ekr.20110917174948.6930: *3* cpp.tokenize & helper
    def tokenize(self, s: str) -> list[str]:
        """Tokenize comments, strings, identifiers, whitespace and operators."""
        result: list[str] = []
        i = 0
        while i < len(s):
            # Loop invariant: at end: j > i and s[i:j] is the new token.
            j = i
            ch = s[i]
            if ch in '@\n':  # Make *sure* these are separate tokens.
                j += 1
            elif ch == '#':  # Preprocessor directive.
                j = g.skip_to_end_of_line(s, i)
            elif ch in ' \t':
                j = g.skip_ws(s, i)
            elif ch.isalpha() or ch == '_':
                j = g.skip_c_id(s, i)
            elif g.match(s, i, '//'):
                j = g.skip_line(s, i)
            elif g.match(s, i, '/*'):
                j = self.skip_block_comment(s, i)
            elif ch in "'\"":
                j = g.skip_string(s, i)
            else:
                j += 1
            assert j > i
            result.append(''.join(s[i:j]))
            i = j  # Advance.
        return result

    # The following could be added to the 'else' clause::
        # Accumulate everything else.
        # while (
            # j < n and
            # not s[j].isspace() and
            # not s[j].isalpha() and
            # # start of strings, identifiers, and single-character tokens.
            # not s[j] in '"\'_@' and
            # not g.match(s,j,'//') and
            # not g.match(s,j,'/*') and
            # not g.match(s,j,'-->')
        # ):
            # j += 1
    #@+node:ekr.20110917193725.6974: *4* cpp.skip_block_comment
    def skip_block_comment(self, s: str, i: int) -> int:
        assert g.match(s, i, "/*")
        j = s.find("*/", i)
        if j == -1:
            return len(s)
        return j + 2
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
