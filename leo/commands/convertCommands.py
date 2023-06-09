#@+leo-ver=5-thin
#@+node:ekr.20160316095222.1: * @file ../commands/convertCommands.py
"""Leo's file-conversion commands."""
#@+<< convertCommands imports & annotations >>
#@+node:ekr.20220824202922.1: ** << convertCommands imports & annotations >>
from __future__ import annotations
from collections.abc import Callable
import re
import time
from typing import Any, TYPE_CHECKING
from leo.core import leoGlobals as g
from leo.core import leoBeautify
from leo.commands.baseCommands import BaseEditCommandsClass

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent as Event
    from leo.core.leoNodes import Position
    Match = re.Match
#@-<< convertCommands imports & annotations >>

def cmd(name: str) -> Callable:
    """Command decorator for the ConvertCommandsClass class."""
    return g.new_cmd_decorator(name, ['c', 'convertCommands',])

#@+<< class To_Python >>
#@+node:ekr.20150514063305.123: ** << class To_Python >>
class To_Python:  # pragma: no cover
    """The base class for x-to-python commands."""

    def __init__(self, c: Cmdr) -> None:
        """Ctor for To_Python class."""
        self.c = c
        self.p = self.c.p.copy()
        aList = g.get_directives_dict_list(self.p)
        self.tab_width = g.scanAtTabwidthDirectives(aList) or 4

    #@+others
    #@+node:ekr.20150514063305.126: *3* To_Python.go
    def go(self) -> None:
        t1 = time.time()
        c = self.c
        u, undoType = c.undoer, 'typescript-to-python'
        pp = leoBeautify.CPrettyPrinter(c)
        u.beforeChangeGroup(c.p, undoType)
        changed = False
        n_files, n_nodes = 0, 0
        special = ('class ', 'module ', '@file ', '@@file ')
        files = ('@file ', '@@file ')
        for p in self.p.self_and_subtree(copy=False):
            if p.b:
                n_nodes += 1
                if any(p.h.startswith(z) for z in special):
                    g.es_print(p.h)
                    if any(p.h.startswith(z) for z in files):
                        n_files += 1
                bunch = u.beforeChangeNodeContents(p)
                s = pp.indent(p, giveWarnings=False)
                aList = list(s)
                self.convertCodeList(aList)
                s = ''.join(aList)
                if s != p.b:
                    p.b = s
                    p.setDirty()
                    u.afterChangeNodeContents(p, undoType, bunch)
                    changed = True
        # Call this only once, at end.
        u.afterChangeGroup(c.p, undoType)
        # Warn if no changes were made at all
        if not changed:
            g.es("Command did not find content to convert")
        t2 = time.time()
        g.es_print(f"done! {n_files} files, {n_nodes} nodes, {t2 - t1:2.2f} sec")
    #@+node:ekr.20150514063305.127: *3* To_Python.convertCodeList
    def convertCodeList(self, lines: list[str]) -> None:
        """The main search/replace method."""
        g.trace('must be defined in subclasses.')
    #@+node:ekr.20150514063305.128: *3* To_Python.Utils
    #@+node:ekr.20150514063305.129: *4* match...
    #@+node:ekr.20150514063305.130: *5* match
    def match(self, lines: list[str], i: int, pat: str) -> bool:
        """Return True if lines[i:] matches the pat string."""
        assert pat
        j = 0
        while i + j < len(lines) and j < len(pat):
            if lines[i + j] == pat[j]:
                j += 1
                if j == len(pat):
                    return True
            else:
                return False
        return False
    #@+node:ekr.20150514063305.131: *5* match_word
    def match_word(self, lines: list[str], i: int, pat: str) -> bool:
        """
        Return True if lines[i:] word matches the pat string.
        """
        if self.match(lines, i, pat):
            j = i + len(pat)
            if j >= len(lines):
                return True
            if not pat[-1].isalnum():
                # Bug fix 10/16/2012: The pattern terminates the word.
                return True
            ch = lines[j]
            return not ch.isalnum() and ch != '_'
        return False
    #@+node:ekr.20150514063305.132: *4* insert_not
    def insert_not(self, lines: list[str]) -> None:
        """Change "!" to "not" except before an equal sign."""
        i = 0
        while i < len(lines):
            if self.is_string_or_comment(lines, i):
                i = self.skip_string_or_comment(lines, i)
            elif lines[i] == '!' and not self.match(lines, i + 1, '='):
                lines[i : i + 1] = list('not ')
                i += 4
            else:
                i += 1
    #@+node:ekr.20150514063305.133: *4* is...
    #@+node:ekr.20150514063305.134: *5* is_section_def/ref
    def is_section_def(self, s: str) -> bool:
        return self.is_section_def(s)

    def is_section_ref(self, s: str) -> bool:
        n1 = s.find("<<", 0)
        n2 = s.find(">>", 0)
        return -1 < n1 < n2 and bool(s[n1 + 2 : n2].strip())
    #@+node:ekr.20150514063305.135: *5* is_string_or_comment
    def is_string_or_comment(self, lines: list[str], i: int) -> bool:
        # Does range checking.
        m = self.match
        return m(lines, i, "'") or m(lines, i, '"') or m(lines, i, "//") or m(lines, i, "/*")
    #@+node:ekr.20150514063305.136: *5* is_ws and is_ws_or_nl
    def is_ws(self, ch: str) -> bool:
        return ch in ' \t'

    def is_ws_or_nl(self, ch: str) -> bool:
        return ch in ' \t\n'
    #@+node:ekr.20150514063305.137: *4* prevNonWsChar and prevNonWsOrNlChar
    def prevNonWsChar(self, s: str, i: int) -> int:
        i -= 1
        while i >= 0 and self.is_ws(s[i]):
            i -= 1
        return i

    def prevNonWsOrNlChar(self, lines: list[str], i: int) -> int:
        i -= 1
        while i >= 0 and self.is_ws_or_nl(lines[i]):
            i -= 1
        return i
    #@+node:ekr.20150514063305.138: *4* remove...
    #@+node:ekr.20150514063305.139: *5* removeBlankLines
    def removeBlankLines(self, lines: list[str]) -> None:
        i = 0
        while i < len(lines):
            j = i
            while j < len(lines) and lines[j] in " \t":
                j += 1
            if j == len(lines) or lines[j] == '\n':
                del lines[i : j + 1]
            else:
                i = self.skip_past_line(lines, i)
    #@+node:ekr.20150514063305.140: *5* removeExcessWs
    def removeExcessWs(self, lines: list[str]) -> None:
        i = 0
        i = self.removeExcessWsFromLine(lines, i)
        while i < len(lines):
            if self.is_string_or_comment(lines, i):
                i = self.skip_string_or_comment(lines, i)
            elif self.match(lines, i, '\n'):
                i += 1
                i = self.removeExcessWsFromLine(lines, i)
            else:
                i += 1
    #@+node:ekr.20150514063305.141: *5* removeExessWsFromLine
    def removeExcessWsFromLine(self, lines: list[str], i: int) -> int:
        assert(i == 0 or lines[i - 1] == '\n')
        i = self.skip_ws(lines, i)  # Retain the leading whitespace.
        while i < len(lines):
            if self.is_string_or_comment(lines, i):
                break  # safe
            elif self.match(lines, i, '\n'):
                break
            elif self.match(lines, i, ' ') or self.match(lines, i, '\t'):
                # Replace all whitespace by one blank.
                j = self.skip_ws(lines, i)
                assert j > i
                lines[i:j] = [' ']
                i += 1  # make sure we don't go past a newline!
            else:
                i += 1
        return i
    #@+node:ekr.20150514063305.142: *5* removeMatchingBrackets
    def removeMatchingBrackets(self, lines: list[str], i: int) -> int:
        j = self.skip_to_matching_bracket(lines, i)
        if i < j < len(lines):
            c = lines[j]
            if c == ')' or c == ']' or c == '}':
                del lines[j : j + 1]
                del lines[i : i + 1]
                return j - 1
            return j + 1
        return j
    #@+node:ekr.20150514063305.143: *5* removeSemicolonsAtEndOfLines
    def removeSemicolonsAtEndOfLines(self, lines: list[str]) -> None:
        i = 0
        while i < len(lines):
            if self.is_string_or_comment(lines, i):
                i = self.skip_string_or_comment(lines, i)
            elif lines[i] == ';':
                j = self.skip_ws(lines, i + 1)
                if (
                    j >= len(lines) or
                    self.match(lines, j, '\n') or
                    self.match(lines, j, '#') or
                    self.match(lines, j, "//")
                ):
                    del lines[i]
                else:
                    i += 1
            else:
                i += 1
    #@+node:ekr.20150514063305.144: *5* removeTrailingWs
    def removeTrailingWs(self, lines: list[str]) -> None:
        i = 0
        while i < len(lines):
            if self.is_ws(lines[i]):
                j = i
                i = self.skip_ws(lines, i)
                assert j < i
                if i >= len(lines) or lines[i] == '\n':
                    del lines[j:i]
                    i = j
            else:
                i += 1
    #@+node:ekr.20150514063305.145: *4* replace... & safe_replace
    #@+node:ekr.20150514063305.146: *5* replace
    def replace(self, lines: list[str], findString: str, changeString: str) -> None:
        """
        Replaces all occurances of findString by changeString.
        changeString may be the empty string, but not None.
        """
        if not findString:
            return
        changeList = list(changeString)
        i = 0
        while i < len(lines):
            if self.match(lines, i, findString):
                lines[i : i + len(findString)] = changeList
                i += len(changeList)
            else:
                i += 1
    #@+node:ekr.20150514063305.147: *5* replaceComments
    def replaceComments(self, lines: list[str]) -> None:
        i = 0
        while i < len(lines):
            # Loop invariant: j > progress at end.
            progress = i
            if self.match(lines, i, "//"):
                lines[i : i + 2] = ['#']
                j = self.skip_past_line(lines, i)
            elif self.match(lines, i, "/*"):
                j = self.skip_c_block_comment(lines, i)
                k = i
                while k - 1 >= 0 and lines[k - 1] in ' \t':
                    k -= 1
                assert k == 0 or lines[k - 1] not in ' \t'
                lws = ''.join(lines[k:i])
                comment_body = ''.join(lines[i + 2 : j - 2])
                comment_lines = g.splitLines(lws + comment_body)
                comment_lines = self.munge_block_comment(comment_lines)
                comment = '\n'.join(comment_lines)  # A list of lines.
                comment_list = list(comment)  # A list of characters.
                lines[k:j] = comment_list
                j = k + len(comment_list)
                progress = j - 1  # Disable the check below.
            elif self.match(lines, i, '"') or self.match(lines, i, "'"):
                j = self.skip_string(lines, i)
            else:
                j = i + 1
            # Defensive programming.
            if j == progress:
                j += 1
            assert j > progress
            i = j
    #@+node:ekr.20150514063305.148: *6* munge_block_comment
    def munge_block_comment(self, comment_lines: list[str]) -> list[str]:

        n = len(comment_lines)
        assert n > 0
        s = comment_lines[0]
        junk, w = g.skip_leading_ws_with_indent(s, 0, tab_width=4)
        if n == 1:
            return [f"{' ' * (w - 1)}# {s.strip()}"]
        junk, w = g.skip_leading_ws_with_indent(s, 0, tab_width=4)
        result: list[str] = []
        for i, s in enumerate(comment_lines):
            if s.strip():
                result.append(f"{' ' * w}# {s.strip()}")
            elif i == n - 1:
                pass  # Omit the line entirely.
            else:
                result.append('')  # Add a blank line
        return result
    #@+node:ekr.20150514063305.149: *5* replaceSectionDefs
    def replaceSectionDefs(self, lines: list[str]) -> None:
        """Replaces < < x > > = by @c (at the start of lines)."""
        if not lines:
            return
        i = 0
        j = self.is_section_def(lines[i])
        if j > 0:
            lines[i:j] = list("@c ")
        while i < len(lines):
            if self.is_string_or_comment(lines, i):
                i = self.skip_string_or_comment(lines, i)
            elif self.match(lines, i, "\n"):
                i += 1
                j = self.is_section_def(lines[i])
                if j > i:
                    lines[i:j] = list("@c ")
            else:
                i += 1
    #@+node:ekr.20150514063305.150: *5* safe_replace
    def safe_replace(self, lines: list[str], findString: str, changeString: str) -> None:
        """
        Replaces occurances of findString by changeString,
        but only outside of C comments and strings.
        changeString may be the empty string, but not None.
        """
        if not findString:
            return
        changeList = list(changeString)
        i = 0
        if findString[0].isalpha():  # use self.match_word
            while i < len(lines):
                if self.is_string_or_comment(lines, i):
                    i = self.skip_string_or_comment(lines, i)
                elif self.match_word(lines, i, findString):
                    lines[i : i + len(findString)] = changeList
                    i += len(changeList)
                else:
                    i += 1
        else:  #use self.match
            while i < len(lines):
                if self.match(lines, i, findString):
                    lines[i : i + len(findString)] = changeList
                    i += len(changeList)
                else:
                    i += 1
    #@+node:ekr.20150514063305.151: *4* skip
    #@+node:ekr.20150514063305.152: *5* skip_c_block_comment
    def skip_c_block_comment(self, lines: list[str], i: int) -> int:
        assert self.match(lines, i, "/*")
        i += 2
        while i < len(lines):
            if self.match(lines, i, "*/"):
                return i + 2
            i += 1
        return i
    #@+node:ekr.20150514063305.153: *5* skip_line
    def skip_line(self, lines: list[str], i: int) -> int:
        while i < len(lines) and lines[i] != '\n':
            i += 1
        return i
    #@+node:ekr.20150514063305.154: *5* skip_past_line
    def skip_past_line(self, lines: list[str], i: int) -> int:
        while i < len(lines) and lines[i] != '\n':
            i += 1
        if i < len(lines) and lines[i] == '\n':
            i += 1
        return i
    #@+node:ekr.20150514063305.155: *5* skip_past_word
    def skip_past_word(self, lines: list[str], i: int) -> int:
        assert lines[i].isalpha() or lines[i] == '~'
        # Kludge: this helps recognize dtors.
        if lines[i] == '~':
            i += 1
        while i < len(lines):
            ch = lines[i]
            if ch.isalnum() or ch == '_':
                i += 1
            else:
                break
        return i
    #@+node:ekr.20150514063305.156: *5* skip_string
    def skip_string(self, lines: list[str], i: int) -> int:
        delim = lines[i]  # handle either single or double-quoted strings
        assert delim == '"' or delim == "'"
        i += 1
        while i < len(lines):
            if lines[i] == delim:
                return i + 1
            if lines[i] == '\\':
                i += 2
            else:
                i += 1
        return i
    #@+node:ekr.20150514063305.157: *5* skip_string_or_comment
    def skip_string_or_comment(self, lines: list[str], i: int) -> int:
        if self.match(lines, i, "'") or self.match(lines, i, '"'):
            j = self.skip_string(lines, i)
        elif self.match(lines, i, "//"):
            j = self.skip_past_line(lines, i)
        elif self.match(lines, i, "/*"):
            j = self.skip_c_block_comment(lines, i)
        else:
            assert False  # noqa
        return j
    #@+node:ekr.20150514063305.158: *5* skip_to_matching_bracket
    def skip_to_matching_bracket(self, lines: list[str], i: int) -> int:
        ch = lines[i]
        if ch == '(':
            delim = ')'
        elif ch == '{':
            delim = '}'
        elif ch == '[':
            delim = ']'
        else:
            assert False  # noqa
        i += 1
        while i < len(lines):
            ch = lines[i]
            if self.is_string_or_comment(lines, i):
                i = self.skip_string_or_comment(lines, i)
            elif ch == delim:
                return i
            elif ch == '(' or ch == '[' or ch == '{':
                i = self.skip_to_matching_bracket(lines, i)
                i += 1  # skip the closing bracket.
            else:
                i += 1
        return i
    #@+node:ekr.20150514063305.159: *5* skip_ws and skip_ws_and_nl
    def skip_ws(self, lines: list[str], i: int) -> int:
        while i < len(lines):
            c = lines[i]
            if c == ' ' or c == '\t':
                i += 1
            else:
                break
        return i

    def skip_ws_and_nl(self, lines: list[str], i: int) -> int:
        while i < len(lines):
            c = lines[i]
            if c == ' ' or c == '\t' or c == '\n':
                i += 1
            else:
                break
        return i
    #@-others
#@-<< class To_Python >>

#@+others
#@+node:ekr.20210830070921.1: ** function: convert_at_test_nodes
def convert_at_test_nodes(
    c: Cmdr,
    converter: Any,
    root: Position,
    copy_tree: bool = False,
) -> None:  # pragma: no cover
    """
    Use converter.convert() to convert all the @test nodes in the
    root's tree to children a new last top-level node.
    """
    if not root:
        print('no root')
        return
    last = c.lastTopLevel()
    target = last.insertAfter()
    target.h = 'Converted nodes'
    count = 0
    for p in root.subtree():
        if p.h.startswith('@test'):
            converter.convert_node(c, p, target)
            if copy_tree and p.hasChildren():
                converter.copy_children(c, p, target.lastChild())
            count += 1
    target.expand()
    c.redraw(target)
    print(f"converted {count} @test nodes")
#@+node:ekr.20220416082017.1: ** class AnnotationError
class AnnotationError(Exception):
    pass
#@+node:ekr.20160316111303.1: ** class ConvertCommandsClass
class ConvertCommandsClass(BaseEditCommandsClass):
    """Leo's file-conversion commands"""

    def __init__(self, c: Cmdr) -> None:
        """Ctor for EditCommandsClass class."""
        # pylint: disable=super-init-not-called
        self.c = c

    #@+others
    #@+node:ekr.20220105151235.1: *3* ccc.add-mypy-annotations
    @cmd('add-mypy-annotations')
    def addMypyAnnotations(self, event: Event) -> None:  # pragma: no cover
        """
        The add-mypy-annotations command adds mypy annotations to function and
        method definitions based on naming conventions.

        To use, select an @<file> node for a python external file and execute
        add-mypy-annotations. The command rewrites the @<file> tree, adding
        mypy annotations for untyped function/method arguments.

        The command attempts no type analysis. It uses "Any" as the type of
        functions and methods that do not specify a return type. As as special
        case, the type of __init__ methods is "None".

        @data add-mypy-annotations in leoSettings.leo contains a list of
        key/value pairs. Keys are argument names (as used in Leo); values are
        mypy type names.

        This command adds annotations for kwargs that have a constant initial
        value.
        """
        self.Add_Mypy_Annotations(self.c).add_annotations()
        self.c.bodyWantsFocus()
    #@+node:ekr.20220105152521.1: *4* class Add_Mypy_Annotations

    class Add_Mypy_Annotations:

        """A class that implements the add-mypy-annotations command."""

        changed_lines = 0
        default_annotation = 'Any'  # The 'DEFAULT' @data add-mypy-annotations key overrides this.
        default_return_annotation = 'None'
        tag = 'add-mypy-annotations'
        types_d: dict[str, str] = {}  # Keys are argument names. Values are mypy types.

        def __init__(self, c: Cmdr) -> None:
            self.c = c

        class AnnotationError(Exception):
            pass

        #@+others
        #@+node:ekr.20220105154019.1: *5* ama.init_types_d
        def init_types_d(self) -> None:  # pragma: no cover
            """Init the annotations dict."""
            c, d, tag = self.c, self.types_d, self.tag
            data = c.config.getData(tag)
            if not data:
                print(f"@data {tag} not found")
                return
            for s in data:
                try:
                    key, val = s.split(',', 1)
                    if key in d:
                        print(f"{tag}: ignoring duplicate key: {s!r}")
                    elif key == 'DEFAULT':
                        self.default_annotation = val.strip()
                    elif key == 'DEFAULT_RETURN':
                        self.default_return_annotation = val.strip()
                    else:
                        d[key] = val.strip()
                except ValueError:
                    print(f"{tag}: ignoring invalid key/value pair: {s!r}")
            self.types_d = d
        #@+node:ekr.20220105154158.1: *5* ama.add_annotations (entry)
        def add_annotations(self) -> None:  # pragma: no cover

            c, p, tag = self.c, self.c.p, self.tag
            # Checks.
            if not p.isAnyAtFileNode():
                g.es_print(f"{tag}: not an @file node: {p.h}")
                return
            if not p.h.endswith(('py', 'pyw')):
                g.es_print(f"{tag}: not a python file: {p.h}")
                return
            # Init.
            self.init_types_d()
            if not self.types_d:
                print(f"{self.tag}: no types given")
                return
            try:
                # Convert p and (recursively) all its descendants.
                self.convert_node(p)
                # Redraw.
                c.expandAllSubheads(p)
                c.treeWantsFocusNow()
            except Exception:
                g.es_exception()
        #@+node:ekr.20220105155837.4: *5* ama.convert_node
        def convert_node(self, p: Position) -> None:  # pragma: no cover
            """Convert p and all its descendants."""
            # Convert p.b.
            self.convert_body(p)
            # Recursively create all descendants.
            for child in p.children():
                self.convert_node(child)
        #@+node:ekr.20220105173331.1: *5* ama.convert_body
        def convert_body(self, p: Position) -> None:
            """Convert p.b in place."""
            c = self.c
            if not p.b.strip():  # pragma: no cover
                return
            try:
                s = self.def_pat.sub(self.do_def, p.b)
            except AnnotationError as e:  # pragma: no cover
                print(f"Unchanged: {p.h}: {e!r}")
                return
            if p.b != s:
                self.changed_lines += 1
                if not g.unitTesting:  # pragma: no cover
                    print(f"changed {p.h}")
                p.setDirty()
                c.setChanged()
                p.b = s
        #@+node:ekr.20220105174453.1: *5* ama.do_def
        # The old regex recognizes existing return values.
        # def_pat = re.compile(r'^([ \t]*)def[ \t]+(\w+)\s*\((.*?)\)(.*?):(.*?)\n', re.MULTILINE + re.DOTALL)

        # Alas, the old regex can put too much in the return value, thereby putting too little in the argument.
        # *Warning*: a greedy (MULTILINE) search for arguments would match to the *next* def!

        # #2606: End the pattern at the *first* "):" so arguments don't end prematurely.
        #        Alas, now we can't convert defs that already have return values.
        def_pat = re.compile(r'^([ \t]*)def[ \t]+(\w+)\s*\((.*?)\):(.*?)\n', re.MULTILINE + re.DOTALL)

        return_dict: dict[str, str] = {
            '__init__': 'None',
            '__repr__': 'str',
            '__str__': 'str',
        }

        def do_def(self, m: Match) -> str:
            lws, name, args, tail = m.group(1), m.group(2), m.group(3), m.group(4)
            args = self.do_args(args)
            return_val_s = self.return_dict.get(name, self.default_return_annotation)
            return_val = f" -> {return_val_s}"
            if not tail.strip():
                tail = ''
            return f"{lws}def {name}({args}){return_val}:{tail}\n"
        #@+node:ekr.20220105174453.2: *5* ama.do_args
        arg_pat = re.compile(r'(\s*[\*\w]+\s*)([:,=])?')
        comment_pat = re.compile(r'(\s*#.*?\n)')

        def do_args(self, args: str) -> str:
            """Add type annotations for all arguments."""
            multiline = '\n' in args.strip()
            comma = ',\n' if multiline else ', '
            lws = ' ' * 4 if multiline else ''
            result: list[str] = []
            i = 0
            while i < len(args):
                rest = args[i:]
                if not rest.strip():
                    break
                # Handle comments following arguments.
                if multiline and result:
                    m = self.comment_pat.match(rest)
                    if m:
                        comment = m.group(0)
                        i += len(comment)
                        last = result.pop()
                        result.append(f"{last.rstrip()}  {comment.strip()}\n")
                        continue
                m = self.arg_pat.match(rest)
                if not m:  # pragma: no cover
                    g.printObj(args, tag='args')
                    raise AnnotationError(f"no match for arg_pat.match({rest})")
                name1, tail = m.group(1), m.group(2)
                name = name1.strip()
                i += len(name1)
                if name == 'self':
                    # Don't annotate self, but allow unusual self=expr.
                    if tail == '=':
                        arg, i = self.find_arg(args, i)
                        result.append(f"{lws}{name}={arg}{comma}")
                    else:
                        result.append(f"{lws}{name}{comma}")
                        if i < len(args) and args[i] == ',':
                            i += 1
                elif tail == ':':  # pragma: no cover
                    # Never change an already-annotated arg.
                    arg, i = self.find_arg(args, i)
                    result.append(f"{lws}{name}: {arg}{comma}")
                elif tail == '=':
                    arg, i = self.find_arg(args, i)
                    if arg == 'None':
                        # Use a known type for the arg, if it exists.
                        kind = self.types_d.get(name, self.default_annotation)
                    else:
                        kind = self.kind(arg)
                    result.append(f"{lws}{name}: {kind}={arg}{comma}")
                elif tail == ',':
                    kind = self.types_d.get(name.strip(), self.default_annotation)
                    result.append(f"{lws}{name}: {kind}{comma}")
                    i += 1
                else:
                    kind = self.types_d.get(name.strip(), self.default_annotation)
                    result.append(f"{lws}{name}: {kind}{comma}")
            s = ''.join(result)
            if multiline:
                s = '\n' + s
            if not multiline and s.endswith(', '):
                s = s[:-2]
            return s
        #@+node:ekr.20220105190332.1: *5* ama.find_arg
        def find_arg(self, s: str, i: int) -> tuple[str, int]:
            """
            Scan over type annotations or initializers.

            Return (arg, j), the index of the character following the argument starting at s[i].
            """
            assert s[i] in ':=', (i, s[i], s)
            i += 1
            while i < len(s) and s[i] == ' ':
                i += 1
            i1 = i
            level = 0  # Assume balanced parens, brackets and strings.
            while i < len(s):
                ch = s[i]
                i += 1
                if ch in '[{(':
                    level += 1
                elif ch in ')]}':
                    level -= 1
                elif ch in '\'"':
                    i = g.skip_python_string(s, i - 1)
                elif ch == ',' and level == 0:
                    # Skip the comma, but don't include it in the result.
                    break
            if level > 0:  # pragma: no cover
                raise AnnotationError(f"Bad level: {level}, {s!r}")
            result = s[i1:i].strip()
            if result.endswith(','):
                result = result[:-1].strip()
            return result, i
        #@+node:ekr.20220105222028.1: *5* ama.kind
        bool_pat = re.compile(r'(True|False)')
        float_pat = re.compile(r'[0-9]*\.[0-9]*')
        int_pat = re.compile(r'[0-9]+')
        string_pat = re.compile(r'[\'"].*[\'"]')

        def kind(self, s: str) -> str:
            """Return the kind of the initial value s."""
            if self.bool_pat.match(s):
                return 'bool'
            if self.float_pat.match(s):
                return 'float'
            if self.int_pat.match(s):
                return 'int'
            if self.string_pat.match(s):
                return 'str'
            return self.default_annotation  # pragma: no cover
        #@-others
    #@+node:ekr.20160316091843.1: *3* ccc.c-to-python
    @cmd('c-to-python')
    def cToPy(self, event: Event) -> None:  # pragma: no cover
        """
        The c-to-python command converts c or c++ text to python text.
        The conversion is not perfect, but it eliminates a lot of tedious
        text manipulation.
        """
        self.C_To_Python(self.c).go()
        self.c.bodyWantsFocus()
    #@+node:ekr.20150514063305.160: *4* class C_To_Python (To_Python)
    class C_To_Python(To_Python):  # pragma: no cover
        #@+others
        #@+node:ekr.20150514063305.161: *5* ctor & helpers (C_To_Python)
        def __init__(self, c: Cmdr) -> None:
            """Ctor for C_To_Python class."""
            super().__init__(c)
            #
            # Internal state...
            # The class name for the present function.  Used to modify ivars.
            self.class_name = ''
            # List of ivars to be converted to self.ivar
            self.ivars: list[str] = []
            self.get_user_types()
        #@+node:ekr.20150514063305.162: *6* get_user_types (C_To_Python)
        def get_user_types(self) -> None:
            c = self.c
            self.class_list = c.config.getData('c-to-python-class-list') or []
            self.type_list = (
                c.config.getData('c-to-python-type-list') or
                ["char", "void", "short", "long", "int", "double", "float"]
            )
            aList = c.config.getData('c-to-python-ivars-dict')
            if aList:
                self.ivars_dict = self.parse_ivars_data(aList)
            else:
                self.ivars_dict = {}
        #@+node:ekr.20150514063305.163: *6* parse_ivars_data
        def parse_ivars_data(self, aList: list[str]) -> dict[str, list[str]]:
            d: dict[str, list[str]] = {}
            key = None
            aList = [z.strip() for z in aList if z.strip()]
            for s in aList:
                if s.endswith(':'):
                    key = s[:-1].strip()
                elif key:
                    ivars = [z.strip() for z in s.split(',') if z.strip()]
                    aList = d.get(key, [])
                    aList.extend(ivars)
                    d[key] = aList
                else:
                    g.error('invalid @data c-to-python-ivars-dict', repr(s))
                    return {}
            return d
        #@+node:ekr.20150514063305.164: *5* convertCodeList (C_To_Python) & helpers
        def convertCodeList(self, lines: list[str]) -> None:
            r, sr = self.replace, self.safe_replace
            # First...
            r(lines, "\r", '')
            # self.convertLeadingBlanks(lines) # Now done by indent.
            # if leoFlag: replaceSectionDefs(lines)
            self.mungeAllFunctions(lines)
            # Next...
            if 1:
                # CC2 stuff:
                sr(lines, "TRACEPB", "if trace: g.trace")
                sr(lines, "TRACEPN", "if trace: g.trace")
                sr(lines, "TRACEPX", "if trace: g.trace")
                sr(lines, "TICKB", "if trace: g.trace")
                sr(lines, "TICKN", "if trace: g.trace")
                sr(lines, "TICKX", "if trace: g.trace")
                sr(lines, "g.trace(ftag,", "g.trace(")
                sr(lines, "ASSERT_TRACE", "assert")
            sr(lines, "ASSERT", "assert")
            sr(lines, " -> ", '.')
            sr(lines, "->", '.')
            sr(lines, " . ", '.')
            sr(lines, "this.self", "self")
            sr(lines, "{", '')
            sr(lines, "}", '')
            sr(lines, "#if", "if")
            sr(lines, "#else", "else")
            sr(lines, "#endif", '')
            sr(lines, "else if", "elif")
            sr(lines, "else", "else:")
            sr(lines, "&&", " and ")
            sr(lines, "||", " or ")
            sr(lines, "TRUE", "True")
            sr(lines, "FALSE", "False")
            sr(lines, "NULL", "None")
            sr(lines, "this", "self")
            sr(lines, "try", "try:")
            sr(lines, "catch", "except:")
            # if leoFlag: sr(lines, "@code", "@c")
            # Next...
            self.handle_all_keywords(lines)
            self.insert_not(lines)
            # after processing for keywords
            self.removeSemicolonsAtEndOfLines(lines)
            # Last...
            # if firstPart and leoFlag: removeLeadingAtCode(lines)
            self.removeBlankLines(lines)
            self.removeExcessWs(lines)
            # your taste may vary: in Python I don't like extra whitespace
            sr(lines, " :", ":")
            sr(lines, ", ", ",")
            sr(lines, " ,", ",")
            sr(lines, " (", "(")
            sr(lines, "( ", "(")
            sr(lines, " )", ")")
            sr(lines, ") ", ")")
            sr(lines, "@language c", "@language python")
            self.replaceComments(lines)  # should follow all calls to safe_replace
            self.removeTrailingWs(lines)
            r(lines, "\t ", "\t")  # happens when deleting declarations.
        #@+node:ekr.20150514063305.165: *6* handle_all_keywords
        def handle_all_keywords(self, lines: list[str]) -> None:
            """
            converts if ( x ) to if x:
            converts while ( x ) to while x:
            """
            i = 0
            while i < len(lines):
                if self.is_string_or_comment(lines, i):
                    i = self.skip_string_or_comment(lines, i)
                elif (
                    self.match_word(lines, i, "if") or
                    self.match_word(lines, i, "while") or
                    self.match_word(lines, i, "for") or
                    self.match_word(lines, i, "elif")
                ):
                    i = self.handle_keyword(lines, i)
                else:
                    i += 1

        #@+node:ekr.20150514063305.166: *7* handle_keyword
        def handle_keyword(self, lines: list[str], i: int) -> int:
            if self.match_word(lines, i, "if"):
                i += 2
            elif self.match_word(lines, i, "elif"):
                i += 4
            elif self.match_word(lines, i, "while"):
                i += 5
            elif self.match_word(lines, i, "for"):
                i += 3
            else:
                assert False  # noqa
            # Make sure one space follows the keyword.
            k = i
            i = self.skip_ws(lines, i)
            if k == i:
                c = lines[i]
                lines[i : i + 1] = [' ', c]
                i += 1
            # Remove '(' and matching ')' and add a ':'
            if lines[i] == "(":
                # Look ahead.  Don't remove if we span a line.
                j = self.skip_to_matching_bracket(lines, i)
                k = i
                found = False
                while k < j and not found:
                    found = lines[k] == '\n'
                    k += 1
                if not found:
                    j = self.removeMatchingBrackets(lines, i)
                if i < j < len(lines):
                    ch = lines[j]
                    lines[j : j + 1] = [ch, ":", " "]
                    j = j + 2
                return j
            return i
        #@+node:ekr.20150514063305.167: *6* mungeAllFunctions
        def mungeAllFunctions(self, lines: list[str]) -> None:
            """Scan for a '{' at the top level that is preceeded by ')' """
            prevSemi = 0  # Previous semicolon: header contains all previous text
            i = 0
            firstOpen = None
            while i < len(lines):
                progress = i
                if self.is_string_or_comment(lines, i):
                    j = self.skip_string_or_comment(lines, i)
                    prevSemi = j
                elif self.match(lines, i, '('):
                    if not firstOpen:
                        firstOpen = i
                    j = i + 1
                elif self.match(lines, i, '#'):
                    # At this point, it is a preprocessor directive.
                    j = self.skip_past_line(lines, i)
                    prevSemi = j
                elif self.match(lines, i, ';'):
                    j = i + 1
                    prevSemi = j
                elif self.match(lines, i, "{"):
                    j = self.handlePossibleFunctionHeader(lines, i, prevSemi, firstOpen)
                    prevSemi = j
                    firstOpen = None  # restart the scan
                else:
                    j = i + 1
                # Handle unusual cases.
                if j <= progress:
                    j = progress + 1
                assert j > progress
                i = j
        #@+node:ekr.20150514063305.168: *7* handlePossibleFunctionHeader
        def handlePossibleFunctionHeader(self,
            lines: list[str],
            i: int,
            prevSemi: int,
            firstOpen: int,
        ) -> int:
            """
            Converts function header lines from c++ format to python format.
            That is, converts
                x1..nn w::y ( t1 z1,..tn zn) {
            to
                def y (z1,..zn): {
            """
            assert self.match(lines, i, "{")
            prevSemi = self.skip_ws_and_nl(lines, prevSemi)
            close = self.prevNonWsOrNlChar(lines, i)
            if close < 0 or lines[close] != ')':
                # Should not increase *Python* indent.
                return 1 + self.skip_to_matching_bracket(lines, i)
            if not firstOpen:
                return 1 + self.skip_to_matching_bracket(lines, i)
            close2 = self.skip_to_matching_bracket(lines, firstOpen)
            if close2 != close:
                return 1 + self.skip_to_matching_bracket(lines, i)
            open_paren = firstOpen
            assert lines[open_paren] == '('
            head = lines[prevSemi:open_paren]
            # do nothing if the head starts with "if", "for" or "while"
            k = self.skip_ws(head, 0)
            if k >= len(head) or not head[k].isalpha():
                return 1 + self.skip_to_matching_bracket(lines, i)
            kk = self.skip_past_word(head, k)
            if kk > k:
                headString = ''.join(head[k:kk])
                # C keywords that might be followed by '{'
                if headString in [
                    "class", "do", "for", "if", "struct", "switch", "while"]:
                    return 1 + self.skip_to_matching_bracket(lines, i)
            args = lines[open_paren : close + 1]
            k = 1 + self.skip_to_matching_bracket(lines, i)
            body = lines[close + 1 : k]
            head = self.massageFunctionHead(head)
            args = self.massageFunctionArgs(args)
            body = self.massageFunctionBody(body)
            result = []
            if head:
                result.extend(head)
            if args:
                result.extend(args)
            if body:
                result.extend(body)
            lines[prevSemi:k] = result
            return prevSemi + len(result)
        #@+node:ekr.20150514063305.170: *7* massageFunctionHead (sets .class_name)
        def massageFunctionHead(self, head: list[str]) -> list[str]:
            result: list[str] = []
            prevWord = []
            self.class_name = ''
            i = 0
            while i < len(head):
                i = self.skip_ws_and_nl(head, i)
                if i < len(head) and head[i].isalpha():
                    result = []
                    j = self.skip_past_word(head, i)
                    prevWord = head[i:j]
                    i = j
                    # look for ::word2
                    i = self.skip_ws(head, i)
                    if self.match(head, i, "::"):
                        # Set the global to the class name.
                        self.class_name = ''.join(prevWord)
                        # print(class name:", self.class_name)
                        i = self.skip_ws(head, i + 2)
                        if i < len(head) and (head[i] == '~' or head[i].isalpha()):
                            j = self.skip_past_word(head, i)
                            if head[i:j] == prevWord:
                                result.extend('__init__')
                            elif head[i] == '~' and head[i + 1 : j] == prevWord:
                                result.extend('__del__')
                            else:
                                # result.extend(list('::'))
                                result.extend(head[i:j])
                            i = j
                    else:
                        result.extend(prevWord)
                else:
                    i += 1
            finalResult = list("def ")
            finalResult.extend(result)
            return finalResult
        #@+node:ekr.20150514063305.169: *7* massageFunctionArgs
        def massageFunctionArgs(self, args: list[str]) -> list[str]:
            assert args[0] == '('
            assert args[-1] == ')'
            result: list[str] = ['(']
            lastWord = []
            if self.class_name:
                for item in list("self,"):
                    result.append(item)  #can put extra comma
            i = 1
            while i < len(args):
                i = self.skip_ws_and_nl(args, i)
                ch = args[i]
                if ch.isalpha():
                    j = self.skip_past_word(args, i)
                    lastWord = args[i:j]
                    i = j
                elif ch == ',' or ch == ')':
                    for item in lastWord:
                        result.append(item)
                    if lastWord and ch == ',':
                        result.append(',')
                    lastWord = []
                    i += 1
                else:
                    i += 1
            if result[-1] == ',':
                del result[-1]
            result.append(')')
            result.append(':')
            return result
        #@+node:ekr.20150514063305.171: *7* massageFunctionBody & helpers
        def massageFunctionBody(self, body: list[str]) -> list[str]:
            body = self.massageIvars(body)
            body = self.removeCasts(body)
            body = self.removeTypeNames(body)
            body = self.dedentBlocks(body)
            return body
        #@+node:ekr.20150514063305.172: *8* dedentBlocks
        def dedentBlocks(self, body: list[str]) -> list[str]:
            """Look for '{' preceded by '{' or '}' or ';'
            (with intervening whitespace and comments).
            """
            i = 0
            while i < len(body):
                j = i
                ch = body[i]
                if self.is_string_or_comment(body, i):
                    j = self.skip_string_or_comment(body, i)
                elif ch in '{};':
                    # Look ahead ofr '{'
                    j += 1
                    while True:
                        k = j
                        j = self.skip_ws_and_nl(body, j)
                        if self.is_string_or_comment(body, j):
                            j = self.skip_string_or_comment(body, j)
                        if k == j:
                            break
                        assert k < j
                    if self.match(body, j, '{'):
                        k = j
                        j = self.skip_to_matching_bracket(body, j)
                        m = '# <Start dedented block>...'
                        body[k : k + 1] = list(m)
                        j += len(m)
                        while k < j:
                            progress = k
                            if body[k] == '\n':
                                k += 1
                                spaces = 0
                                while spaces < 4 and k < j:
                                    if body[k] == ' ':
                                        spaces += 1
                                        k += 1
                                    else:
                                        break
                                if spaces > 0:
                                    del body[k - spaces : k]
                                    k -= spaces
                                    j -= spaces
                            else:
                                k += 1
                            assert progress < k
                        m = '    # <End dedented block>'
                        body[j : j + 1] = list(m)
                        j += len(m)
                else:
                    j = i + 1
                # Defensive programming.
                if i == j:
                    j += 1
                assert i < j
                i = j
            return body
        #@+node:ekr.20150514063305.173: *8* massageIvars
        def massageIvars(self, body: list[str]) -> list[str]:
            ivars = self.ivars_dict.get(self.class_name, [])
            i = 0
            while i < len(body):
                if self.is_string_or_comment(body, i):
                    i = self.skip_string_or_comment(body, i)
                elif body[i].isalpha():
                    j = self.skip_past_word(body, i)
                    word = ''.join(body[i:j])
                    if word in ivars:
                        # replace word by self.word
                        word = "self." + word
                        word = list(word)  # type:ignore
                        body[i:j] = word
                        delta = len(word) - (j - i)
                        i = j + delta
                    else:
                        i = j
                else:
                    i += 1
            return body
        #@+node:ekr.20150514063305.174: *8* removeCasts
        def removeCasts(self, body: list[str]) -> list[str]:
            i = 0
            while i < len(body):
                if self.is_string_or_comment(body, i):
                    i = self.skip_string_or_comment(body, i)
                elif self.match(body, i, '('):
                    start = i
                    i = self.skip_ws(body, i + 1)
                    if body[i].isalpha():
                        j = self.skip_past_word(body, i)
                        word = ''.join(body[i:j])
                        i = j
                        if word in self.class_list or word in self.type_list:
                            i = self.skip_ws(body, i)
                            while self.match(body, i, '*'):
                                i += 1
                            i = self.skip_ws(body, i)
                            if self.match(body, i, ')'):
                                i += 1
                                del body[start:i]
                                i = start
                else:
                    i += 1
            return body
        #@+node:ekr.20150514063305.175: *8* removeTypeNames
        def removeTypeNames(self, body: list[str]) -> list[str]:
            """Do _not_ remove type names when preceeded by new."""
            i = 0
            while i < len(body):
                if self.is_string_or_comment(body, i):
                    i = self.skip_string_or_comment(body, i)
                elif self.match_word(body, i, "new"):
                    i = self.skip_past_word(body, i)
                    i = self.skip_ws(body, i)
                    # don't remove what follows new.
                    if body[i].isalpha():
                        i = self.skip_past_word(body, i)
                elif body[i].isalpha():
                    j = self.skip_past_word(body, i)
                    word = ''.join(body[i:j])
                    if word in self.class_list or word in self.type_list:
                        j = self.skip_ws(body, j)
                        while self.match(body, j, '*'):
                            j += 1
                        j = self.skip_ws(body, j)
                        del body[i:j]
                    else:
                        i = j
                else:
                    i += 1
            return body
        #@-others
    #@+node:ekr.20160111190632.1: *3* ccc.makeStubFiles
    @cmd('make-stub-files')
    def make_stub_files(self, event: Event) -> None:  # pragma: no cover
        """
        Make stub files for all nearby @<file> nodes.
        Take configuration settings from @x stub-y nodes.
        """
        #@+others
        #@+node:ekr.20160213070235.1: *4* class MakeStubFileAdapter
        class MakeStubFileAdapter:  # pragma: no cover
            """
            An class that adapts leo/external/make_stub_files.py to Leo.

            Settings are taken from Leo settings nodes, not a .cfg file.
            """
            #@+others
            #@+node:ekr.20160213070235.2: *5* msf.ctor & helpers
            def __init__(self, c: Cmdr) -> None:
                """MakeStubFile.ctor. From StandAloneMakeStubFile.ctor."""
                self.c = c
                self.msf = msf = g.import_module('make_stub_files')
                x = msf.StandAloneMakeStubFile()  # x is used *only* to init ivars.
                # Ivars set on the command line...
                self.config_fn = None
                self.enable_unit_tests = False
                self.files: list[str] = []  # May also be set in the config file.
                self.output_directory = self.finalize(
                    c.config.getString('stub-output-directory') or '.')
                self.output_fn: str = None
                self.overwrite = c.config.getBool('stub-overwrite', default=False)
                self.trace_matches = c.config.getBool(
                    'stub-trace-matches', default=False)
                self.trace_patterns = c.config.getBool(
                    'stub-trace-patterns', default=False)
                self.trace_reduce = c.config.getBool('stub-trace-reduce', default=False)
                self.trace_visitors = c.config.getBool(
                    'stub-trace-visitors', default=False)
                self.update_flag = c.config.getBool('stub-update', default=False)
                self.verbose = c.config.getBool('stub-verbose', default=False)
                self.warn = c.config.getBool('stub-warn', default=False)
                # Pattern lists & dicts, set by config sections...
                self.patterns_dict: dict[str, Any] = {}
                self.names_dict: dict[str, Any] = {}
                self.def_patterns = self.scan_patterns('stub-def-name-patterns')
                self.general_patterns = self.scan_patterns('stub-general-patterns')
                self.prefix_lines = self.scan('stub-prefix-lines')
                self.regex_patterns = self.scan_patterns('stub-regex-patterns')
                # Complete the dicts.na
                x.make_patterns_dict()
                self.patterns_dict = x.patterns_dict
                self.op_name_dict = x.op_name_dict = x.make_op_name_dict()
                # Copy the ivars.
                x.def_patterns = self.def_patterns
                x.general_patterns = self.general_patterns
                x.regex_patterns = self.regex_patterns
                x.prefix_lines = self.prefix_lines
            #@+node:ekr.20160213070235.3: *6* msf.scan
            def scan(self, kind: str) -> list[str]:
                """Return a list of *all* lines from an @data node, including comments."""
                c = self.c
                aList = c.config.getData(kind, strip_comments=False, strip_data=False)
                if not aList:
                    g.trace(f"warning: no @data {kind} node")
                return aList
            #@+node:ekr.20160213070235.4: *6* msf.scan_d
            def scan_d(self, kind: str) -> dict[str, list[str]]:
                """Return a dict created from an @data node of the given kind."""
                c = self.c
                aList = c.config.getData(kind, strip_comments=True, strip_data=True)
                d: dict[str, list[str]] = {}
                if aList is None:
                    g.trace(f"warning: no @data {kind} node")
                for s in aList or []:
                    name, value = s.split(':', 1)
                    d[name.strip()] = value.strip()
                return d
            #@+node:ekr.20160213070235.5: *6* msf.scan_patterns
            def scan_patterns(self, kind: str) -> list[str]:
                """Parse the config section into a list of patterns, preserving order."""
                d = self.scan_d(kind)
                aList: list[str] = []
                seen = set()
                for key in d:
                    value = d.get(key)
                    if key in seen:
                        g.trace('duplicate key', key)
                    else:
                        seen.add(key)
                        aList.append(self.msf.Pattern(key, value))
                return aList
            #@+node:ekr.20160213070235.6: *5* msf.finalize
            def finalize(self, fn: str) -> str:
                """Finalize and regularize a filename."""
                return g.finalize(fn)
            #@+node:ekr.20160213070235.7: *5* msf.make_stub_file
            def make_stub_file(self, p: Position) -> None:
                """Make a stub file in ~/stubs for the @<file> node at p."""
                import ast
                assert p.isAnyAtFileNode()
                c = self.c
                fn = p.anyAtFileNodeName()
                if not fn.endswith(('py', 'pyw')):
                    g.es_print('not a python file', fn)
                    return
                abs_fn = c.fullPath(p)
                if not g.os_path_exists(abs_fn):
                    g.es_print('not found', abs_fn)
                    return
                if g.os_path_exists(self.output_directory):
                    base_fn = g.os_path_basename(fn)
                    out_fn = g.finalize_join(self.output_directory, base_fn)
                else:
                    g.es_print('not found', self.output_directory)
                    return
                out_fn = out_fn[:-3] + '.pyi'
                out_fn = g.os_path_normpath(out_fn)
                self.output_fn = out_fn  # compatibility with stand-alone script
                s = open(abs_fn).read()
                node = ast.parse(s, filename=fn, mode='exec')
                # Make the traverser *after* creating output_fn and output_directory ivars.
                x = self.msf.StubTraverser(controller=self)
                x.output_fn = self.output_fn
                x.output_directory = self.output_directory
                x.trace_matches = self.trace_matches
                x.trace_patterns = self.trace_patterns
                x.trace_reduce = self.trace_reduce
                x.trace_visitors = self.trace_visitors
                x.run(node)
            #@+node:ekr.20160213070235.8: *5* msf.run
            def run(self, p: Position) -> None:
                """Make stub files for all files in p's tree."""
                if p.isAnyAtFileNode():
                    self.make_stub_file(p)
                    return
                # First, look down tree.
                after, p2 = p.nodeAfterTree(), p.firstChild()
                found = False
                while p2 and p != after:
                    if p2.isAnyAtFileNode():
                        self.make_stub_file(p2)
                        p2.moveToNext()
                        found = True
                    else:
                        p2.moveToThreadNext()
                if not found:
                    # Look up the tree.
                    for p2 in p.parents():
                        if p2.isAnyAtFileNode():
                            self.make_stub_file(p2)
                            break
                    else:
                        g.es('no files found in tree:', p.h)
            #@-others
        #@-others
        MakeStubFileAdapter(self.c).run(self.c.p)
    #@+node:ekr.20160316091923.1: *3* ccc.python-to-coffeescript
    @cmd('python-to-coffeescript')
    def python2coffeescript(self, event: Event) -> None:  # pragma: no cover
        """
        Converts python text to coffeescript text. The conversion is not
        perfect, but it eliminates a lot of tedious text manipulation.
        """
        #@+others
        #@+node:ekr.20160316092837.1: *4* class Python_To_Coffeescript_Adapter
        class Python_To_Coffeescript_Adapter:  # pragma: no cover
            """An interface class between Leo and leo/external/py2cs.py."""
            #@+others
            #@+node:ekr.20160316112717.1: *5* py2cs.ctor
            def __init__(self, c: Cmdr) -> None:
                """Ctor for Python_To_Coffeescript_Adapter class."""
                self.c = c
                self.files: list[str] = []
                self.output_directory = self.finalize(
                    c.config.getString('py2cs-output-directory'))
                # self.output_fn = None
                self.overwrite = c.config.getBool('py2cs-overwrite', default=False)
                # Connect to the external module.
                self.py2cs = g.import_module('leo.external.py2cs')
            #@+node:ekr.20160316093019.1: *5* py2cs.main
            def main(self) -> None:
                """Main line for Python_To_CoffeeScript class."""
                if self.py2cs:
                    self.run()
                else:
                    g.es_print('can not load py2cs.py')
            #@+node:ekr.20160316094011.7: *5* py2cs.finalize
            def finalize(self, fn: str) -> str:
                """Finalize and regularize a filename."""
                return g.finalize(fn)
            #@+node:ekr.20160316094011.8: *5* py2cs.to_coffeescript
            def to_coffeescript(self, p: Position) -> None:
                """Convert the @<file> node at p to a .coffee file."""
                assert p.isAnyAtFileNode()
                c = self.c
                fn = p.anyAtFileNodeName()
                if not fn.endswith(('py', 'pyw')):
                    g.es_print('not a python file', fn)
                    return
                abs_fn = c.fullPath(p)
                if not g.os_path_exists(abs_fn):
                    g.es_print('not found', abs_fn)
                    return
                if g.os_path_exists(self.output_directory):
                    base_fn = g.os_path_basename(fn)
                    out_fn = g.finalize_join(self.output_directory, base_fn)
                else:
                    g.es_print('not found', self.output_directory)
                    return
                out_fn = out_fn[:-3] + '.coffee'
                out_fn = g.os_path_normpath(out_fn)
                s = open(abs_fn).read()
                # s = self.strip_sentinels(s)
                if 0:
                    for z in g.splitLines(s)[:20]:
                        print(z.rstrip())
                x = self.py2cs.MakeCoffeeScriptController()
                # copy ivars and run.
                x.enable_unit_tests = False
                x.files = [abs_fn,]
                x.output_directory = self.output_directory
                x.overwrite = self.overwrite
                x.make_coffeescript_file(abs_fn, s=s)
            #@+node:ekr.20160316094011.9: *5* py2cs.run
            def run(self) -> None:
                """Create .coffee files for all @<file> nodes in p's tree."""
                p = c.p
                if p.isAnyAtFileNode():
                    self.to_coffeescript(p)
                    return
                # First, look down tree.
                after, p2 = p.nodeAfterTree(), p.firstChild()
                found = False
                while p2 and p != after:
                    if p2.isAnyAtFileNode():
                        self.to_coffeescript(p2)
                        p2.moveToNext()
                        found = True
                    else:
                        p2.moveToThreadNext()
                if not found:
                    # Look up the tree.
                    for p2 in p.parents():
                        if p2.isAnyAtFileNode():
                            self.to_coffeescript(p2)
                            return
                g.es_print('no files found in tree:', p.h)
            #@+node:ekr.20160316141812.1: *5* py2cs.strip_sentinels
            def strip_sentinels(self, s: str) -> str:
                """
                Strip s of all sentinel lines.
                This may be dubious because it destroys outline structure.
                """
                delims = ['#', None, None]
                return ''.join(
                    [z for z in g.splitLines(s) if not g.is_sentinel(z, delims)])
            #@-others
        #@-others
        c = self.c
        Python_To_Coffeescript_Adapter(c).main()
        c.bodyWantsFocus()
    #@+node:ekr.20211013080132.1: *3* ccc.python-to-typescript
    @cmd('python-to-typescript')
    def pythonToTypescriptCommand(self, event: Event) -> None:  # pragma: no cover
        """
        The python-to-typescript command converts python to typescript text.
        The conversion is not perfect, but it eliminates a lot of tedious text
        manipulation.

        To use, select any @<file> node and execute python-to-typescript. The
        command creates (safe!) results in the last top-level node of the
        outline.

        The command attempts no type analysis. It uses "void" as the type of
        all functions and methods. However, the script will annotate
        function/method arguments:

        @data python-to-typescript-types in leoSettings.leo contains a list of
        key/value pairs. Keys are argument names (as used in Leo); values are
        typescript type names.
        """
        c = self.c
        self.PythonToTypescript(c).convert(c.p)
        self.c.bodyWantsFocus()
    #@+node:ekr.20211013080132.2: *4* class PythonToTypescript
    #@@nobeautify
    class PythonToTypescript:  # pragma: no cover

        # The handlers are clear as they are.
        # pylint: disable=no-else-return

        # Keys are argument names. Values are typescript types.
        # Typescript can infer types of initialized kwargs.
        types_d: dict[str, str] = {}

        #@+others
        #@+node:ekr.20211020162251.1: *5* py2ts.ctor
        def __init__(self, c: Cmdr, alias: str = None) -> None:
            self.c = c
            self.alias = alias  # For scripts. An alias for 'self'.
            data = c.config.getData('python-to-typescript-types') or []
            for line in data:
                try:
                    key, value = line.split(',')
                    self.types_d[key.strip()] = value.strip()
                except Exception:
                    g.es_print('ignoring bad key/value pair in @data python-to-typescript-types')
                    g.es_print(repr(line))
            # Create the list of patterns.
            self.patterns = (
                # Head: order matters.
                (self.comment_pat, self.do_comment),
                (self.docstring_pat, self.do_docstring),
                (self.section_ref_pat, self.do_section_ref),
                # Middle: order doesn't matter.
                (self.class_pat, self.do_class),
                (self.def_pat, self.do_def),
                (self.elif_pat, self.do_elif),
                (self.else_pat, self.do_else),
                (self.except_pat, self.do_except),
                (self.finally_pat, self.do_finally),
                (self.for_pat, self.do_for),
                (self.if_pat, self.do_if),
                (self.import_pat, self.do_import),
                (self.try_pat, self.do_try),
                (self.while_pat, self.do_while),
                (self.with_pat, self.do_with),
                # Tail: order matters.
                (self.trailing_comment_pat, self.do_trailing_comment)
            )
        #@+node:ekr.20211013081549.1: *5* py2ts.convert
        def convert(self, p: Position) -> None:
            """
            The main line.

            Convert p and all descendants as a child of a new last top-level node.
            """
            c = self.c
            # Create the parent node. It will be deleted.
            parent = c.lastTopLevel().insertAfter()
            # Convert p and all its descendants.
            try:
                self.convert_node(p, parent)
                # Promote the translated node.
                parent.promote()
                parent.doDelete()
                p = c.lastTopLevel()
                p.h = p.h.replace('.py', '.ts').replace('@', '@@')
                c.redraw(p)
                c.expandAllSubheads(p)
                c.treeWantsFocusNow()
            except Exception:
                g.es_exception()
        #@+node:ekr.20211013101327.1: *5* py2ts.convert_node
        def convert_node(self, p: Position, parent: Position) -> None:
            # Create a copy of p as the last child of parent.
            target = parent.insertAsLastChild()
            target.h = p.h  # The caller will rename this node.
            # Convert p.b into child.b
            self.convert_body(p, target)
            # Recursively create all descendants.
            for child in p.children():
                self.convert_node(child, target)
        #@+node:ekr.20211013102209.1: *5* py2ts.convert_body, handlers &helpers
        def convert_body(self, p: Position, target: Position) -> None:
            """
            Convert p.b into target.b.

            This is the heart of the algorithm.
            """
            trace = False
            # The loop may change lines, but each line is scanned only once.
            i, lines = 0, g.splitLines(self.pre_pass(p.b))
            old_lines = lines[:]
            while i < len(lines):
                progress = i
                line = lines[i]
                for (pattern, handler) in self.patterns:
                    m = pattern.match(line)
                    if m:
                        i = handler(i, lines, m, p)  # May change lines.
                        break
                else:
                    self.do_operators(i, lines, p)
                    self.do_semicolon(i, lines, p)
                    i += 1
                assert progress < i
            if trace and g.unitTesting and lines != old_lines:
                print(f"\nchanged {p.h}:\n")
                for z in lines:
                    print(z.rstrip())
            # Run the post-pass
            target.b = self.post_pass(lines)
            # Munge target.h.
            target.h = target.h.replace('__init__', 'constructor')
        #@+node:ekr.20211018154815.1: *6* handlers
        #@+node:ekr.20211014023141.1: *7* py2ts.do_class
        class_pat = re.compile(r'^([ \t]*)class(.*):(.*)\n')

        def do_class(self, i: int, lines: list[str], m: Match, p: Position) -> int:

            j = self.find_indented_block(i, lines, m, p)
            lws, base, tail = m.group(1), m.group(2).strip(), m.group(3).strip()
            base_s = f" {base} " if base else ''
            tail_s = f" // {tail}" if tail else ''
            lines[i] = f"{lws}class{base_s}{{{tail_s}\n"
            lines.insert(j, f"{lws}}}\n")
            return i + 1
        #@+node:ekr.20211013165615.1: *7* py2ts.do_comment
        comment_pat = re.compile(r'^([ \t]*)#(.*)\n')

        def do_comment(self, i: int, lines: list[str], m: Match, p: Position) -> int:
            """Handle a stand-alone comment line."""
            lws, comment = m.group(1), m.group(2).strip()
            if comment:
                lines[i] = f"{lws}// {comment}\n"
            else:
                lines[i] = '\n'  # Write blank line for an empty comment.
            return i + 1
        #@+node:ekr.20211013130041.1: *7* py2ts.do_def & helper
        def_pat = re.compile(r'^([ \t]*)def[ \t]+([\w_]+)\s*\((.*)\):(.*)\n')
        this_pat = re.compile(r'^.*?\bthis\b')  # 'self' has already become 'this'.

        def do_def(self, i: int, lines: list[str], m: Match, p: Position) -> int:

            j = self.find_indented_block(i, lines, m, p)
            lws, name, args, tail = m.group(1), m.group(2), m.group(3).strip(), m.group(4).strip()
            args = self.do_args(args)
            if name == '__init__':
                name = 'constructor'
            tail_s = f" // {tail}" if tail else ''
            # Use void as a placeholder type.
            type_s = ' ' if name == 'constructor' else ': void '
            function_s = ' ' if self.this_pat.match(lines[i]) else ' function '
            lines[i] = f"{lws}public{function_s}{name}({args}){type_s}{{{tail_s}\n"
            lines.insert(j, f"{lws}}}\n")
            return i + 1
        #@+node:ekr.20211014031722.1: *8* py2ts.do_args
        def do_args(self, args: list[str]) -> str:
            """Add type annotations and remove the 'self' argument."""
            result = []
            for arg in (z.strip() for z in args.split(',')):
                # Omit the self arg.
                if arg != 'this':  # Already converted.
                    val = self.types_d.get(arg)
                    result.append(f"{arg}: {val}" if val else arg)
            return ', '.join(result)
        #@+node:ekr.20211013165952.1: *7* py2ts.do_docstring
        docstring_pat = re.compile(r'^([ \t]*)r?("""|\'\'\')(.*)\n')

        def do_docstring(self, i: int, lines: list[str], m: Match, p: Position) -> int:
            """
            Convert a python docstring.

            Always use the full multi-line typescript format, even for single-line
            python docstrings.
            """
            lws, delim, docstring = m.group(1), m.group(2), m.group(3).strip()
            tail = docstring.replace(delim, '').strip()
            lines[i] = f"{lws}/**\n"
            if tail:
                lines.insert(i + 1, f"{lws} * {tail}\n")
                i += 1
            if delim in docstring:
                lines.insert(i + 1, f"{lws} */\n")
                return i + 2
            i += 1
            while i < len(lines):
                line = lines[i]
                # Buglet: ignores whatever might follow.
                tail = line.replace(delim, '').strip()
                # pylint: disable=no-else-return
                if delim in line:
                    if tail:
                        lines[i] = f"{lws} * {tail}\n"
                        lines.insert(i + 1, f"{lws} */\n")
                        return i + 2
                    else:
                        lines[i] = f"{lws} */\n"
                        return i + 1
                elif tail:
                    lines[i] = f"{lws} * {tail}\n"
                else:
                    lines[i] = f"{lws} *\n"
                i += 1
            return i
        #@+node:ekr.20211014030113.1: *7* py2ts.do_except
        except_pat = re.compile(r'^([ \t]*)except(.*):(.*)\n')

        def do_except(self, i: int, lines: list[str], m: Match, p: Position) -> int:

            j = self.find_indented_block(i, lines, m, p)
            lws, error, tail = m.group(1), m.group(2).strip(), m.group(3).strip()
            tail_s = f" // {tail}" if tail else ''
            error_s = f" ({error}) " if error else ''
            lines[i] = f"{lws}catch{error_s}{{{tail_s}\n"
            lines.insert(j, f"{lws}}}\n")
            return i + 1
        #@+node:ekr.20211013141725.1: *7* py2ts.do_for
        for1_s = r'^([ \t]*)for[ \t]+(.*):(.*)\n'  # for (cond):
        for2_s = r'^([ \t]*)for[ \t]*\((.*)\n'  # for (

        for1_pat = re.compile(for1_s)
        for2_pat = re.compile(for2_s)
        for_pat = re.compile(fr"{for1_s}|{for2_s}")  # Used by main loop.

        def do_for(self, i: int, lines: list[str], m: Match, p: Position) -> int:

            line = lines[i]
            m1 = self.for1_pat.match(line)
            m2 = self.for2_pat.match(line)
            if m1:
                j = self.find_indented_block(i, lines, m, p)
                lws, cond, tail = m.group(1), m.group(2).strip(), m.group(3).strip()
                cond_s = cond if cond.startswith('(') else f"({cond})"
                tail_s = f" // {tail}" if tail else ''
                lines[i] = f"{lws}for {cond_s} {{{tail_s}\n"
                self.do_operators(i, lines, p)
                lines.insert(j, f"{lws}}}\n")
                return i + 1
            else:
                j = self.find_indented_block(i, lines, m2, p)
                # Generate the 'for' line.
                lws, tail = m2.group(1), m2.group(2).strip()
                tail_s = f" // {tail}" if tail else ''
                lines[i] = f"{lws}for ({tail_s}\n"
                # Tell do_semicolons that lines[i:j] are not statements.
                self.kill_semicolons(lines, i, j)
                # Assume line[j] closes the paren.  Insert '{'
                lines[j] = lines[j].rstrip().replace(':', '') + ' {\n'
                # Insert '}'
                k = self.find_indented_block(j, lines, m2, p)
                lines.insert(k, f"{lws}}}\n")
                return i + 1
        #@+node:ekr.20211017202104.1: *7* py2ts.do_import
        import_s = r'^([ \t]*)import[ \t]+(.*)\n'
        import_from_s = r'^([ \t]*)from[ \t]+(.*)[ \t]+import[ \t]+(.*)\n'
        import_pat = re.compile(fr"{import_s}|{import_from_s}")  # Used by main loop.
        import1_pat = re.compile(import_s)
        import2_pat = re.compile(import_from_s)

        def do_import(self, i: int, lines: list[str], m: Match, p: Position) -> int:

            line = lines[i]
            m1 = self.import1_pat.match(line)
            m2 = self.import2_pat.match(line)
            # Comment out all imports.
            if m1:
                lws, import_list = m1.group(1), m1.group(2).strip()
                lines[i] = f'{lws}// import "{import_list}"\n'
            else:
                lws, module, import_list = m2.group(1), m2.group(2).strip(), m2.group(3).strip()
                lines[i] = f'{lws}// from "{module}" import {import_list}\n'
            return i + 1
        #@+node:ekr.20211014022432.1: *7* py2ts.do_elif
        elif1_s = r'^([ \t]*)elif[ \t]+(.*):(.*)\n'  # elif (cond):
        elif2_s = r'^([ \t]*)elif[ \t]*\((.*)\n'  # elif (

        elif1_pat = re.compile(elif1_s)
        elif2_pat = re.compile(elif2_s)
        elif_pat = re.compile(fr"{elif1_s}|{elif2_s}")  # Used by main loop.

        def do_elif(self, i: int, lines: list[str], m: Match, p: Position) -> int:

            line = lines[i]
            m1 = self.elif1_pat.match(line)
            m2 = self.elif2_pat.match(line)
            if m1:
                j = self.find_indented_block(i, lines, m, p)
                lws, cond, tail = m.group(1), m.group(2).strip(), m.group(3).strip()
                cond_s = cond if cond.startswith('(') else f"({cond})"
                tail_s = f" // {tail}" if tail else ''
                lines[i] = f"{lws}else if {cond_s} {{{tail_s}\n"
                lines.insert(j, f"{lws}}}\n")
                self.do_operators(i, lines, p)
                return i + 1
            else:
                j = self.find_indented_block(i, lines, m2, p)
                # Generate the 'else if' line.
                lws, tail = m2.group(1), m2.group(2).strip()
                tail_s = f" // {tail}" if tail else ''
                lines[i] = f"{lws}else if ({tail_s}\n"
                # Tell do_semicolons that lines[i:j] are not statements.
                self.kill_semicolons(lines, i, j)
                # Assume line[j] closes the paren.  Insert '{'
                lines[j] = lines[j].rstrip().replace(':', '') + ' {\n'
                # Insert '}'
                k = self.find_indented_block(j, lines, m2, p)
                lines.insert(k, f"{lws}}}\n")
                return i + 1

        #@+node:ekr.20211014022445.1: *7* py2ts.do_else
        else_pat = re.compile(r'^([ \t]*)else:(.*)\n')

        def do_else(self, i: int, lines: list[str], m: Match, p: Position) -> int:

            j = self.find_indented_block(i, lines, m, p)
            lws, tail = m.group(1), m.group(2).strip()
            tail_s = f" // {tail}" if tail else ''
            lines[i] = f"{lws}else {{{tail_s}\n"
            lines.insert(j, f"{lws}}}\n")
            return i + 1
        #@+node:ekr.20211014022453.1: *7* py2ts.do_finally
        finally_pat = re.compile(r'^([ \t]*)finally:(.*)\n')

        def do_finally(self, i: int, lines: list[str], m: Match, p: Position) -> int:

            j = self.find_indented_block(i, lines, m, p)
            lws, tail = m.group(1), m.group(2).strip()
            tail_s = f" // {tail}" if tail else ''
            lines[i] = f"{lws}finally {{{tail_s}\n"
            lines.insert(j, f"{lws}}}\n")
            return i + 1
        #@+node:ekr.20211013131016.1: *7* py2ts.do_if
        if1_s = r'^([ \t]*)if[ \t]+(.*):(.*)\n'  # if (cond):
        if2_s = r'^([ \t]*)if[ \t]*\((.*)\n'  # if (

        if1_pat = re.compile(if1_s)
        if2_pat = re.compile(if2_s)
        if_pat = re.compile(fr"{if1_s}|{if2_s}")  # Used by main loop.

        def do_if(self, i: int, lines: list[str], m: Match, p: Position) -> int:

            line = lines[i]
            m1 = self.if1_pat.match(line)
            m2 = self.if2_pat.match(line)
            if m1:
                j = self.find_indented_block(i, lines, m1, p)
                lws, cond, tail = m.group(1), m.group(2).strip(), m.group(3).strip()
                cond_s = cond if cond.startswith('(') else f"({cond})"
                tail_s = f" // {tail}" if tail else ''
                lines[i] = f"{lws}if {cond_s} {{{tail_s}\n"
                self.do_operators(i, lines, p)
                lines.insert(j, f"{lws}}}\n")
                return i + 1
            else:
                j = self.find_indented_block(i, lines, m2, p)
                # Generate the 'if' line.
                lws, tail = m2.group(1), m2.group(2).strip()
                tail_s = f" // {tail}" if tail else ''
                lines[i] = f"{lws}if ({tail_s}\n"
                # Tell do_semicolons that lines[i:j] are not statements.
                self.kill_semicolons(lines, i, j)
                # Assume line[j] closes the paren.  Insert '{'
                lines[j] = lines[j].rstrip().replace(':', '') + ' {\n'
                # Insert '}'
                k = self.find_indented_block(j, lines, m2, p)
                lines.insert(k, f"{lws}}}\n")
                return i + 1
        #@+node:ekr.20211018125503.1: *7* py2ts.do_section_ref
        section_ref_pat = re.compile(r"^([ \t]*)(\<\<.*?\>\>)\s*(.*)$")

        def do_section_ref(self, i: int, lines: list[str], m: Match, p: Position) -> int:
            # Handle trailing code.
            lws, section_name, tail = m.group(1), m.group(2), m.group(3).strip()
            if tail.startswith('#'):
                lines[i] = f"{lws}{section_name}  // {tail[1:]}\n"
            return i + 1
        #@+node:ekr.20211014022506.1: *7* py2ts.do_try
        try_pat = re.compile(r'^([ \t]*)try:(.*)\n')

        def do_try(self, i: int, lines: list[str], m: Match, p: Position) -> int:

            j = self.find_indented_block(i, lines, m, p)
            lws, tail = m.group(1), m.group(2).strip()
            tail_s = f" // {tail}" if tail else ''
            lines[i] = f"{lws}try {{{tail_s}\n"
            lines.insert(j, f"{lws}}}\n")
            return i + 1
        #@+node:ekr.20211013141809.1: *7* py2ts.do_while
        while1_s = r'^([ \t]*)while[ \t]+(.*):(.*)\n'  # while (cond):
        while2_s = r'^([ \t]*)while[ \t]*\((.*)\n'  # while (

        while1_pat = re.compile(while1_s)
        while2_pat = re.compile(while2_s)
        while_pat = re.compile(fr"{while1_s}|{while2_s}")  # Used by main loop.

        def do_while(self, i: int, lines: list[str], m: Match, p: Position) -> int:

            line = lines[i]
            m1 = self.while1_pat.match(line)
            m2 = self.while2_pat.match(line)
            if m1:
                j = self.find_indented_block(i, lines, m, p)
                lws, cond, tail = m.group(1), m.group(2).strip(), m.group(3).strip()
                cond_s = cond if cond.startswith('(') else f"({cond})"
                tail_s = f" // {tail}" if tail else ''
                lines[i] = f"{lws}while {cond_s} {{{tail_s}\n"
                self.do_operators(i, lines, p)
                lines.insert(j, f"{lws}}}\n")
                return i + 1
            else:
                j = self.find_indented_block(i, lines, m2, p)
                # Generate the 'while' line.
                lws, tail = m2.group(1), m2.group(2).strip()
                tail_s = f" // {tail}" if tail else ''
                lines[i] = f"{lws}while ({tail_s}\n"
                # Tell do_semicolons that lines[i:j] are not statements.
                self.kill_semicolons(lines, i, j)
                # Assume line[j] closes the paren.  Insert '{'
                lines[j] = lines[j].rstrip().replace(':', '') + ' {\n'
                # Insert '}'
                k = self.find_indented_block(j, lines, m2, p)
                lines.insert(k, f"{lws}}}\n")
                return i + 1

        #@+node:ekr.20211014022554.1: *7* py2ts.do_with
        with_pat = re.compile(r'^([ \t]*)with(.*):(.*)\n')

        def do_with(self, i: int, lines: list[str], m: Match, p: Position) -> int:

            j = self.find_indented_block(i, lines, m, p)
            lws, clause, tail = m.group(1), m.group(2).strip(), m.group(3).strip()
            tail_s = f" // {tail}" if tail else ''
            clause_s = f" ({clause}) " if clause else ''
            lines[i] = f"{lws}with{clause_s}{{{tail_s}\n"
            lines.insert(j, f"{lws}}}\n")
            return i + 1
        #@+node:ekr.20211013172540.1: *7* py2ts.do_trailing_comment
        trailing_comment_pat = re.compile(r'^([ \t]*)(.*)#(.*)\n')

        def do_trailing_comment(self, i: int, lines: list[str], m: Match, p: Position) -> int:
            """
            Handle a trailing comment line.

            All other patterns have already been scanned on the line.
            """
            lws, statement, trailing_comment = m.group(1), m.group(2).rstrip(), m.group(3).strip()
            statement_s = f"{statement};" if self.ends_statement(i, lines) else statement
            lines[i] = f"{lws}{statement_s}  // {trailing_comment}\n"
            return i + 1
        #@+node:ekr.20211022090919.1: *6* helpers
        #@+node:ekr.20211017210122.1: *7* py2ts.do_operators
        def do_operators(self, i: int, lines: list[str], p: Position) -> None:

            # Regex replacements.
            table = (
                ('True', 'true'),
                ('False', 'false'),
                # ('None', 'null'), # Done in post-pass.
                ('default', 'default_val'),
                ('and', '&&'),
                ('or', '||'),
                ('is not', '!='),
                ('is', '=='),
                ('not', '!'),
                ('assert', '// assert'),
            )
            for a, b in table:
                lines[i] = re.sub(fr"\b{a}\b", b, lines[i])

        #@+node:ekr.20211017134103.1: *7* py2ts.do_semicolon
        def do_semicolon(self, i: int, lines: list[str], p: Position) -> None:
            """
            Insert a semicolon in lines[i] is appropriate.

            No other handler has matched, so we know that the line:
            - Does not end in a comment.
            - Is not part of a docstring.
            """
            # Honor the flag inserted by kill_semicolons.
            flag = self.kill_semicolons_flag
            if lines[i].endswith(flag):
                lines[i] = lines[i].replace(flag, '\n')
                return
            # For now, use a maximal policy.
            if self.ends_statement(i, lines):
                lines[i] = f"{lines[i].rstrip()};\n"


        #@+node:ekr.20211017135603.1: *7* py2ts.ends_statement
        def ends_statement(self, i: int, lines: list[str]) -> bool:
            """
            Return True if lines[i] ends a statement.

            If so, the line should end with a semicolon,
            before any trailing comment, that is.
            """
            # https://stackoverflow.com/questions/38823062/
            s = lines[i].strip()
            next_line = lines[i + 1] if i + 1 < len(lines) else ''
            # Return False for blank lines.
            if not s:
                return False
            # Return False for Leo directives.
            if s.startswith('@'):
                return False
            # Return False for section references.
            i = s.find('<<')
            j = s.find('>>')
            if -1 < i < j:
                return False
            # Return False if this line ends in any of the following:
            if s.endswith(('{', '(', '[', ':', '||', '&&', '!', ',', '`')):
                return False
            # Return False if the next line starts with '{', '(', '['.
            if next_line.lstrip().startswith(('[', '(', '[', '&&', '||', '!')):
                return False
            # Return False for '}' lines.
            if s.startswith('}'):
                return False
            return True
        #@+node:ekr.20211013123001.1: *7* py2ts.find_indented_block
        lws_pat = re.compile(r'^([ \t]*)')

        def find_indented_block(self, i: int, lines: list[str], m: Match, p: Position) -> int:
            """Return j, the index of the line *after* the indented block."""
            # Scan for the first non-empty line with the same or less indentation.
            lws = m.group(1)
            j = i + 1
            while j < len(lines):
                line = lines[j]
                m2 = self.lws_pat.match(line)
                lws2 = m2.group(1)
                if line.strip() and len(lws2) <= len(lws):
                    # Don't add a blank line at the end of a block.
                    if j > 1 and not lines[j - 1].strip():
                        j -= 1
                    break
                j += 1
            return j

        #@+node:ekr.20211020101415.1: *7* py2ts.kill_semicolons
        kill_semicolons_flag = '  // **kill-semicolon**\n'  # Must end with a newline.

        def kill_semicolons(self, lines: list[str], i: int, j: int) -> None:
            """
            Tell later calls to do_semicolon that lines[i : j] should *not* end with a semicolon.
            """
            for n in range(i, j):
                lines[n] = lines[n].rstrip() + self.kill_semicolons_flag
        #@+node:ekr.20211016214742.1: *7* py2ts.move_docstrings
        class_or_def_pat = re.compile(r'^(\s*)(public|class)\s+([\w_]+)')

        def move_docstrings(self, lines: list[str]) -> None:
            """Move docstrings before the preceding class or def line."""
            i = 0
            while i < len(lines):
                m = self.class_or_def_pat.match(lines[i])
                i += 1
                if not m:
                    continue
                # Set j to the start of the docstring.
                j = i
                while j < len(lines):
                    if lines[j].strip():
                        break
                    j += 1
                if j >= len(lines):
                    continue
                if not lines[j].strip().startswith('/**'):
                    continue
                # Set k to the end of the docstring.
                k = j
                while k < len(lines) and '*/' not in lines[k]:
                    k += 1
                if k >= len(lines):
                    g.printObj(lines[i - 1 : len(lines) - 1], tag='OOPS')
                    continue
                # Remove 4 blanks from the docstrings.
                for n in range(j, k + 1):
                    if lines[n].startswith(' ' * 4):
                        lines[n] = lines[n][4:]
                # Rearrange the lines.
                lines[i - 1 : k + 1] = lines[j : k + 1] + [lines[i - 1]]
                i = k + 1
        #@+node:ekr.20211016200908.1: *7* py2ts.post_pass & helpers
        def post_pass(self, lines: list[str]) -> str:

            # Munge lines in place
            self.move_docstrings(lines)
            self.do_f_strings(lines)
            self.do_ternary(lines)
            self.do_assignment(lines)  # Do this last, so it doesn't add 'const' to inserted comments.
            s = (''.join(lines)
                .replace('@language python', '@language typescript')
                .replace(self.kill_semicolons_flag, '\n')
            )
            return re.sub(r'\bNone\b', 'null', s)


        #@+node:ekr.20211021061023.1: *8* py2ts.do_assignment
        assignment_pat = re.compile(r'^([ \t]*)(.*?)\s+=\s+(.*)$')  # Require whitespace around the '='

        def do_assignment(self, lines: list[str]) -> None:
            """Add const to all non-tuple assignments."""
            # Do this late so that we can test for the ending semicolon.

            # Suppression table.
            # Missing elements are likely to cause this method to generate '= ='.
            table = (
                ',',  # Tuple assignment or  mutli-line argument lists.
                '*',  # A converted docstring.
                '`',  # f-string.
                '//',  # Comment.
                '=',  # Condition.
                # Keywords that might be followed by '='
                'class', 'def', 'elif', 'for', 'if', 'print', 'public', 'return', 'with', 'while',
            )
            for i, s in enumerate(lines):
                m = self.assignment_pat.match(s)
                if m:
                    lws, lhs, rhs = m.group(1), m.group(2), m.group(3).rstrip()
                    if not any(z in lhs for z in table):
                        lines[i] = f"{lws}const {lhs} = {rhs}\n"
        #@+node:ekr.20211020185016.1: *8* py2ts.do_f_strings
        f_string_pat = re.compile(r'([ \t]*)(.*?)f"(.*?)"(.*)$')

        def do_f_strings(self, lines: list[str]) -> None:

            i = 0
            while i < len(lines):
                progress = i
                s = lines[i]
                m = self.f_string_pat.match(s)
                if not m:
                    i += 1
                    continue
                lws, head, string, tail = m.group(1), m.group(2), m.group(3), m.group(4).rstrip()
                string_s = (
                    string.replace('{', '${')  # Add the '$'
                    .replace('! ', 'not ')  # Undo erroneous replacement.
                )
                # Remove format strings. Not perfect, but seemingly good enough.
                string_s = re.sub(r'\:[0-9]\.+[0-9]+[frs]', '', string_s)
                string_s = re.sub(r'\![frs]', '', string_s)
                # A hack. If the fstring is on a line by itself, remove a trailing ';'
                if not head.strip() and tail.endswith(';'):
                    tail = tail[:-1].strip()
                if 1:  # Just replace the line.
                    lines[i] = f"{lws}{head}`{string_s}`{tail.rstrip()}\n"
                    i += 1
                else:
                    # These comments quickly become annoying.
                    # Add the original line as a comment as a check.
                    lines[i] = f"{lws}// {s.strip()}\n"  # Add the replacement line.
                    lines.insert(i + 1, f"{lws}{head}`{string_s}`{tail.rstrip()}\n")
                    i += 2
                assert i > progress
        #@+node:ekr.20211021051033.1: *8* py2ts.do_ternary
        ternary_pat1 = re.compile(r'^([ \t]*)(.*?)\s*=\s*(.*?) if (.*?) else (.*);$')  # assignment
        ternary_pat2 = re.compile(r'^([ \t]*)return\s+(.*?) if (.*?) else (.*);$')  # return statement

        def do_ternary(self, lines: list[str]) -> None:

            i = 0
            while i < len(lines):
                progress = i
                s = lines[i]
                m1 = self.ternary_pat1.match(s)
                m2 = self.ternary_pat2.match(s)
                if m1:
                    lws, target, a, cond, b = m1.group(1), m1.group(2), m1.group(3), m1.group(4), m1.group(5)
                    lines[i] = f"{lws}// {s.strip()}\n"
                    lines.insert(i + 1, f"{lws}{target} = {cond} ? {a} : {b};\n")
                    i += 2
                elif m2:
                    lws, a, cond, b = m2.group(1), m2.group(2), m2.group(3), m2.group(4)
                    lines[i] = f"{lws}// {s.strip()}\n"
                    lines.insert(i + 1, f"{lws}return {cond} ? {a} : {b};\n")
                    i += 2
                else:
                    i += 1
                assert progress < i
        #@+node:ekr.20211017044939.1: *7* py2ts.pre_pass
        def pre_pass(self, s: str) -> str:

            # Remove the python encoding lines.
            s = s.replace('', '')

            # Replace 'self' by 'this' *everywhere*.
            s = re.sub(r'\bself\b', 'this', s)

            # Comment out @cmd decorators.
            s = re.sub(r"^@cmd(.*?)$", r'// @cmd\1\n', s, flags=re.MULTILINE)

            # Replace the alias for 'self' by 'this' *only* in specif contexts.
            # Do *not* replace the alias everywhere: that could do great harm.
            if self.alias:
                s = re.sub(fr"\b{self.alias}\.", 'this.', s)
                # Remove lines like `at = self`.
                s = re.sub(fr"^\s*{self.alias}\s*=\s*this\s*\n", '', s, flags=re.MULTILINE)
                # Remove lines like `at, c = self, self.c`.
                s = re.sub(
                    fr"^(\s*){self.alias}\s*,\s*c\s*=\s*this,\s*this.c\n",
                    r'\1c = this.c\n',  # do_assignment adds const.
                    s,
                    flags=re.MULTILINE)
                # Remove lines like `at, p = self, self.p`.
                s = re.sub(fr"^(\s*){self.alias}\s*,\s*p\s*=\s*this,\s*this.p\n",
                    r'\1p = this.p\n',  # do_assignment adds const.
                    s,
                    flags=re.MULTILINE)
                # Do this last.
                s = re.sub(fr"\b{self.alias},", 'this,', s)
            return s
        #@-others
    #@+node:ekr.20160316091843.2: *3* ccc.typescript-to-py
    @cmd('typescript-to-py')
    def tsToPy(self, event: Event) -> None:  # pragma: no cover
        """
        The typescript-to-python command converts typescript text to python
        text. The conversion is not perfect, but it eliminates a lot of tedious
        text manipulation.
        """
        #@+others
        #@+node:ekr.20150514063305.176: *4* class TS_To_Python (To_Python)
        class TS_To_Python(To_Python):  # pragma: no cover
            #@+others
            #@+node:ekr.20150514063305.177: *5* ctor (TS_To_Python)
            def __init__(self, c: Cmdr) -> None:
                """Ctor for TS_To_Python class."""
                super().__init__(c)
                # The class name for the present function.  Used to modify ivars.
                self.class_name = ''
            #@+node:ekr.20150514063305.178: *5* convertCodeList (TS_To_Python) & helpers
            def convertCodeList(self, lines: list[str]) -> None:
                r, sr = self.replace, self.safe_replace
                # First...
                r(lines, '\r', '')
                self.mungeAllFunctions(lines)
                self.mungeAllClasses(lines)
                # Second...
                sr(lines, ' -> ', '.')
                sr(lines, '->', '.')
                sr(lines, ' . ', '.')
                # sr(lines, 'this.self', 'self')
                sr(lines, '{', '')
                sr(lines, '}', '')
                sr(lines, 'else if', 'elif')
                sr(lines, 'else', 'else:')
                sr(lines, '&&', ' and ')
                sr(lines, '||', ' or ')
                sr(lines, 'true', 'True')
                sr(lines, 'false', 'False')
                sr(lines, 'null', 'None')
                sr(lines, 'this', 'self')
                sr(lines, 'try', 'try:')
                sr(lines, 'catch', 'except:')
                sr(lines, 'constructor', '__init__')
                sr(lines, 'new ', '')
                # sr(lines, 'var ','')
                    # var usually indicates something weird, or an uninited var,
                    # so it may be good to retain as a marker.
                # Third...
                self.handle_all_keywords(lines)
                self.insert_not(lines)
                # after processing for keywords
                self.removeSemicolonsAtEndOfLines(lines)
                self.comment_scope_ids(lines)
                # Last...
                self.removeBlankLines(lines)
                self.removeExcessWs(lines)
                # I usually don't like extra whitespace. YMMV.
                sr(lines, '  and ', ' and ')
                sr(lines, '  not ', ' not ')
                sr(lines, '  or ', ' or ')
                sr(lines, ' and  ', ' and ')
                sr(lines, ' not  ', ' not ')
                sr(lines, ' or  ', ' or ')
                sr(lines, ' :', ':')
                sr(lines, ', ', ',')
                sr(lines, ' ,', ',')
                sr(lines, ' (', '(')
                sr(lines, '( ', '(')
                sr(lines, ' )', ')')
                sr(lines, ') ', ')')
                sr(lines, ' and(', ' and (')
                sr(lines, ' not(', ' not (')
                sr(lines, ' or(', ' or (')
                sr(lines, ')and ', ') and ')
                sr(lines, ')not ', ') not ')
                sr(lines, ')or ', ') or ')
                sr(lines, ')and(', ') and (')
                sr(lines, ')not(', ') not (')
                sr(lines, ')or(', ') or (')
                sr(lines, '@language javascript', '@language python')
                self.replaceComments(lines)  # should follow all calls to safe_replace
                self.removeTrailingWs(lines)
                r(lines, '\t ', '\t')  # happens when deleting declarations.
            #@+node:ekr.20150514063305.179: *6* comment_scope_ids
            def comment_scope_ids(self, lines: list[str]) -> None:
                """convert (public|private|export) aLine to aLine # (public|private|export)"""
                scope_ids = ('public', 'private', 'export',)
                i = 0
                if any(self.match_word(lines, i, z) for z in scope_ids):
                    i = self.handle_scope_keyword(lines, i)
                while i < len(lines):
                    progress = i
                    if self.is_string_or_comment(lines, i):
                        i = self.skip_string_or_comment(lines, i)
                    elif lines[i] == '\n':
                        i += 1
                        i = self.skip_ws(lines, i)
                        if any(self.match_word(lines, i, z) for z in scope_ids):
                            i = self.handle_scope_keyword(lines, i)
                    else:
                        i += 1
                    assert i > progress

            #@+node:ekr.20150514063305.180: *7* handle_scope_keyword
            def handle_scope_keyword(self, lines: list[str], i: int) -> int:
                i1 = i
                # pylint: disable=undefined-loop-variable
                for word in ('public', 'private', 'export'):
                    if self.match_word(lines, i, word):
                        i += len(word)
                        break
                else:
                    return None
                # Skip any following spaces.
                i2 = self.skip_ws(lines, i)
                # Scan to the next newline:
                i3 = self.skip_line(lines, i)
                # Optional: move the word to a trailing comment.
                comment: list[str] = list(f" # {word}") if False else []
                # Change the list in place.
                lines[i1:i3] = lines[i2:i3] + comment
                i = i1 + (i3 - i2) + len(comment)
                return i
            #@+node:ekr.20150514063305.181: *6* handle_all_keywords
            def handle_all_keywords(self, lines: list[str]) -> None:
                """
                converts if ( x ) to if x:
                converts while ( x ) to while x:
                """
                statements = ('elif', 'for', 'if', 'while',)
                i = 0
                while i < len(lines):
                    if self.is_string_or_comment(lines, i):
                        i = self.skip_string_or_comment(lines, i)
                    elif any(self.match_word(lines, i, z) for z in statements):
                        i = self.handle_keyword(lines, i)
                    else:
                        i += 1
            #@+node:ekr.20150514063305.182: *7* handle_keyword
            def handle_keyword(self, lines: list[str], i: int) -> int:
                if self.match_word(lines, i, "if"):
                    i += 2
                elif self.match_word(lines, i, "elif"):
                    i += 4
                elif self.match_word(lines, i, "while"):
                    i += 5
                elif self.match_word(lines, i, "for"):
                    i += 3
                else:
                    assert False, 'not a keyword'  # noqa
                # Make sure one space follows the keyword.
                k = i
                i = self.skip_ws(lines, i)
                if k == i:
                    c = lines[i]
                    lines[i : i + 1] = [' ', c]
                    i += 1
                # Remove '(' and matching ')' and add a ':'
                if lines[i] == "(":
                    # Look ahead.  Don't remove if we span a line.
                    j = self.skip_to_matching_bracket(lines, i)
                    k = i
                    found = False
                    while k < j and not found:
                        found = lines[k] == '\n'
                        k += 1
                    if not found:
                        j = self.removeMatchingBrackets(lines, i)
                    if i < j < len(lines):
                        ch = lines[j]
                        lines[j : j + 1] = [ch, ":", " "]
                        j = j + 2
                    return j
                return i
            #@+node:ekr.20150514063305.183: *6* mungeAllClasses
            def mungeAllClasses(self, lines: list[str]) -> None:
                """Scan for a '{' at the top level that is preceded by ')' """
                i = 0
                while i < len(lines):
                    progress = i
                    if self.is_string_or_comment(lines, i):
                        i = self.skip_string_or_comment(lines, i)
                    elif self.match_word(lines, i, 'class'):
                        i1 = i
                        i = self.skip_line(lines, i)
                        lines[i - 1 : i] = list(f"{lines[i - 1]}:")
                        s = ''.join(lines[i1:i])
                        k = s.find(' extends ')
                        if k > -1:
                            k1 = k
                            k = g.skip_id(s, k + 1)
                            k = g.skip_ws(s, k)
                            if k < len(s) and g.is_c_id(s[k]):
                                k2 = g.skip_id(s, k)
                                word = s[k:k2]
                                lines[i1:i] = list(f"{s[:k1]} ({word})")
                    elif self.match_word(lines, i, 'interface'):
                        lines[i : i + len('interface')] = list('class')
                        i = self.skip_line(lines, i)
                        lines[i - 1 : i] = list(f"{lines[i - 1]}: # interface")
                        i = self.skip_line(lines, i)  # Essential.
                    else:
                        i += 1
                    assert i > progress
            #@+node:ekr.20150514063305.184: *6* mungeAllFunctions & helpers
            def mungeAllFunctions(self, lines: list[str]) -> None:
                """Scan for a '{' at the top level that is preceded by ')' """
                prevSemi = 0  # Previous semicolon: header contains all previous text
                i = 0
                firstOpen = None
                while i < len(lines):
                    progress = i
                    if self.is_string_or_comment(lines, i):
                        j = self.skip_string_or_comment(lines, i)
                        prevSemi = j
                    elif self.match(lines, i, '('):
                        if not firstOpen:
                            firstOpen = i
                        j = i + 1
                    elif self.match(lines, i, ';'):
                        j = i + 1
                        prevSemi = j
                    elif self.match(lines, i, "{"):
                        j = self.handlePossibleFunctionHeader(
                            lines, i, prevSemi, firstOpen)
                        prevSemi = j
                        firstOpen = None  # restart the scan
                    else:
                        j = i + 1
                    # Handle unusual cases.
                    if j <= progress:
                        j = progress + 1
                    assert j > progress
                    i = j
            #@+node:ekr.20150514063305.185: *7* handlePossibleFunctionHeader
            def handlePossibleFunctionHeader(self,
                lines: list[str],
                i: int,
                prevSemi: int,
                firstOpen: int,
            ) -> int:
                """
                converts function header lines from typescript format to python format.
                That is, converts
                    x1..nn w::y ( t1 z1,..tn zn) { C++
                    (public|private|export) name (t1: z1, ... tn: zn {
                to
                    def y (z1,..zn): { # (public|private|export)
                """
                assert self.match(lines, i, "{")
                prevSemi = self.skip_ws_and_nl(lines, prevSemi)
                close = self.prevNonWsOrNlChar(lines, i)
                if close < 0 or lines[close] != ')':
                    # Should not increase *Python* indent.
                    return 1 + self.skip_to_matching_bracket(lines, i)
                if not firstOpen:
                    return 1 + self.skip_to_matching_bracket(lines, i)
                close2 = self.skip_to_matching_bracket(lines, firstOpen)
                if close2 != close:
                    return 1 + self.skip_to_matching_bracket(lines, i)
                open_paren = firstOpen
                assert lines[open_paren] == '('
                head = lines[prevSemi:open_paren]
                # do nothing if the head starts with "if", "for" or "while"
                k = self.skip_ws(head, 0)
                if k >= len(head) or not head[k].isalpha():
                    return 1 + self.skip_to_matching_bracket(lines, i)
                kk = self.skip_past_word(head, k)
                if kk > k:
                    headString = ''.join(head[k:kk])
                    # C keywords that might be followed by '{'
                    if headString in ["do", "for", "if", "struct", "switch", "while"]:
                        return 1 + self.skip_to_matching_bracket(lines, i)
                args = lines[open_paren : close + 1]
                k = 1 + self.skip_to_matching_bracket(lines, i)
                body = lines[close + 1 : k]
                head = self.massageFunctionHead(head)
                args = self.massageFunctionArgs(args)
                body = self.massageFunctionBody(body)
                result = []
                if head:
                    result.extend(head)
                if args:
                    result.extend(args)
                if body:
                    result.extend(body)
                lines[prevSemi:k] = result
                return prevSemi + len(result)
            #@+node:ekr.20150514063305.186: *7* massageFunctionArgs
            def massageFunctionArgs(self, args: list[str]) -> list[str]:
                assert args[0] == '('
                assert args[-1] == ')'
                result: list[str] = ['(']
                lastWord = []
                if self.class_name:
                    for item in list("self,"):
                        result.append(item)  #can put extra comma
                i = 1
                while i < len(args):
                    i = self.skip_ws_and_nl(args, i)
                    ch = args[i]
                    if ch.isalpha():
                        j = self.skip_past_word(args, i)
                        lastWord = args[i:j]
                        i = j
                    elif ch == ',' or ch == ')':
                        for item in lastWord:
                            result.append(item)
                        if lastWord and ch == ',':
                            result.append(',')
                        lastWord = []
                        i += 1
                    else:
                        i += 1
                if result[-1] == ',':
                    del result[-1]
                result.append(')')
                result.append(':')
                return result
            #@+node:ekr.20150514063305.187: *7* massageFunctionHead (sets .class_name)
            def massageFunctionHead(self, head: list[str]) -> list[str]:
                result: list[str] = []
                prevWord = []
                self.class_name = ''
                i = 0
                while i < len(head):
                    i = self.skip_ws_and_nl(head, i)
                    if i < len(head) and head[i].isalpha():
                        result = []
                        j = self.skip_past_word(head, i)
                        prevWord = head[i:j]
                        i = j
                        # look for ::word2
                        i = self.skip_ws(head, i)
                        if self.match(head, i, "::"):
                            # Set the global to the class name.
                            self.class_name = ''.join(prevWord)
                            # print(class name:", self.class_name)
                            i = self.skip_ws(head, i + 2)
                            if i < len(head) and (head[i] == '~' or head[i].isalpha()):
                                j = self.skip_past_word(head, i)
                                if head[i:j] == prevWord:
                                    result.extend('__init__')
                                elif head[i] == '~' and head[i + 1 : j] == prevWord:
                                    result.extend('__del__')
                                else:
                                    # result.extend(list('::'))
                                    result.extend(head[i:j])
                                i = j
                        else:
                            result.extend(prevWord)
                    else:
                        i += 1
                finalResult = list("def ")
                finalResult.extend(result)
                return finalResult
            #@+node:ekr.20150514063305.188: *7* massageFunctionBody & helper
            def massageFunctionBody(self, body: list[str]) -> list[str]:
                # body = self.massageIvars(body)
                # body = self.removeCasts(body)
                # body = self.removeTypeNames(body)
                body = self.dedentBlocks(body)
                return body
            #@+node:ekr.20150514063305.189: *8* dedentBlocks
            def dedentBlocks(self, body: list[str]) -> list[str]:
                """
                Look for '{' preceded by '{' or '}' or ';'
                (with intervening whitespace and comments).
                """
                i = 0
                while i < len(body):
                    j = i
                    ch = body[i]
                    if self.is_string_or_comment(body, i):
                        j = self.skip_string_or_comment(body, i)
                    elif ch in '{};':
                        # Look ahead ofr '{'
                        j += 1
                        while True:
                            k = j
                            j = self.skip_ws_and_nl(body, j)
                            if self.is_string_or_comment(body, j):
                                j = self.skip_string_or_comment(body, j)
                            if k == j:
                                break
                            assert k < j
                        if self.match(body, j, '{'):
                            k = j
                            j = self.skip_to_matching_bracket(body, j)
                            m = '# <Start dedented block>...'
                            body[k : k + 1] = list(m)
                            j += len(m)
                            while k < j:
                                progress = k
                                if body[k] == '\n':
                                    k += 1
                                    spaces = 0
                                    while spaces < 4 and k < j:
                                        if body[k] == ' ':
                                            spaces += 1
                                            k += 1
                                        else:
                                            break
                                    if spaces > 0:
                                        del body[k - spaces : k]
                                        k -= spaces
                                        j -= spaces
                                else:
                                    k += 1
                                assert progress < k
                            m = '    # <End dedented block>'
                            body[j : j + 1] = list(m)
                            j += len(m)
                    else:
                        j = i + 1
                    # Defensive programming.
                    if i == j:
                        j += 1
                    assert i < j
                    i = j
                return body
            #@-others
        #@-others
        c = self.c
        TS_To_Python(c).go()
        c.bodyWantsFocus()
    #@-others
#@-others
#@-leo
