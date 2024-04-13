#@+leo-ver=5-thin
#@+node:ekr.20230917013414.1: * @file ../plugins/indented_languages.py
#@+<< docstring: indented_languages.py >>
#@+node:ekr.20231023052313.1: ** << docstring: indented_languages.py >>
#@@language rest
#@@wrap

"""
A plugin defines three Leo commands that create **study outlines**:

=== Part 1: The import-to-indented-c and import-to-indented-typescript commands

These commands remove braces from C and Typescript programs. They are
surprisingly helpful in getting the feel of C and Typescript programs.

These commands assume that indentation corresponds to curly-bracket level!
If this assumption is violated the results may be misleading. Do *not*
assume that it is possible to recreate curly-brackets from the indented
code!

Hacks for increased readability:

- Remove the first block comment (a copyright message) in each file.
- Remove #include statements.
- Replace multiple blank lines by a single blank line.

Won't do:

1. Generate leading whitespace (lws) corresponding to curly-bracket level.
   Doing so would be tricky because the plugin should preserve lws inside
   parens and square brackets.

2. Support an option to disable the hacks listed above.

=== Part 2: The import-to-indented-lisp command

The command removes *some* parentheses from Lisp program.

I do not recommend using this command. The code is merely a prototype and
will remain as it is. It would take lots more work to be useful.

Working on this command reminds me why I never want to use or read Lisp!

"""
#@-<< docstring: indented_languages.py >>

import re
from typing import Any, Callable, Optional, Union
from leo.core import leoGlobals as g
from leo.core.leoNodes import Position
from leo.plugins.importers.c import C_Importer
from leo.plugins.importers.typescript import TS_Importer

#@+others
#@+node:ekr.20230917084259.1: ** top-level
#@+node:ekr.20230917015308.1: *3* init (indented_languages.py)
def init() -> bool:
    """Return True if the plugin has loaded successfully."""
    # g.registerHandler('after-create-leo-frame', onCreate)
    # g.registerHandler('after-reading-external-file', onAfterRead)
    # g.registerHandler('before-writing-external-file', onBeforeWrite)
    return True
#@+node:ekr.20231022071443.1: *3* commands (indented_languages.py)
@g.command('import-to-indented-c')
def import_to_indented_c(event: Any) -> None:
    """The import-to-indented-c command."""
    c = event.get('c')
    if c:
        Indented_C(c).do_import()

@g.command('import-to-indented-lisp')
def import_to_indented_elisp(event: Any) -> None:
    """The import-to-indented-lisp command."""
    c = event.get('c')
    if c:
        Indented_Lisp(c).do_import()

@g.command('import-to-indented-typescript')
def import_to_indented_typescript(event: Any) -> None:
    """The import-to-indented-typescript command."""
    c = event.get('c')
    if c:
        Indented_TypeScript(c).do_import()


#@+node:ekr.20231022073438.1: **  class Indented_Importer
class Indented_Importer:
    """The base class for all indented importers."""

    extensions: list[str] = None  # The file extension for the language.
    language: str = None  # The name of the language.
    importer_class: Callable = None  # The importer class

    def __init__(self, c):
        self.c = c
        self.file_name = None  # Set by import_one_file.
        if self.importer_class:
            self.importer = self.importer_class(c)  # pylint: disable=not-callable

    #@+others
    #@+node:ekr.20231022073537.1: *3* indented_i.do_import (driver)
    def do_import(self) -> Optional[Position]:
        """
        Base_Indented_Importer.do_import: Create a top-level node containing study outlines for all files in
        c.p and its descendants.

        Return the top-level node for unit tests.
        """
        c, p, u = self.c, self.c.p, self.c.undoer

        assert self.extensions

        def predicate(p: Position) -> bool:
            return self.isAtFileNode(p) and p.h.strip().endswith(tuple(self.extensions))

        roots: list[Position] = g.findRootsWithPredicate(c, p, predicate)  # Removes duplicates
        if not roots:
            return None

        # Undoably create top-level organizer node and import all files.
        try:
            ### g.app.disable_redraw = True
            last = c.lastTopLevel()
            c.selectPosition(last)
            undoData = u.beforeInsertNode(last)
            # Always create a new last top-level node.
            parent = last.insertAfter()
            parent.v.h = 'indented files'
            for root in roots:
                self.import_one_file(root, parent)
            u.afterInsertNode(parent, 'recursive-import', undoData)
        except Exception:
            g.es_print(f"Exception in {self.__class__.__name__}")
            g.es_exception()
        finally:
            ### g.app.disable_redraw = False
            for p2 in parent.self_and_subtree(copy=False):
                p2.contract()
            c.redraw(parent)
        return parent
    #@+node:ekr.20231022100000.1: *3* indented_i.import_one_file
    def import_one_file(self, p: Position, parent: Position) -> None:
        """
        Indented_Importer.import_one_file: common setup code.

        p is an @<file> node.

        - Create a parallel tree as the last child of parent.
        - Indent all the nodes of the parallel tree.
        """
        self.file_name = self.atFileName(p)

        # Create root, a parallel outline.
        root = p.copyWithNewVnodes()
        n = parent.numberOfChildren()
        root._linkAsNthChild(parent, n)
        root.h = self.file_name

        # Indent the parallel outline.
        self.indent_outline(root)

    #@+node:ekr.20231022073306.3: *3* indented_i.indent_outline (the pipeline)
    def indent_outline(self, root: Position) -> None:
        """
        Indent the body text of root and all its descendants.
        """
        for p in root.self_and_subtree():
            self.indent_node(p)
            self.remove_trailing_semicolons(p)
            self.remove_includes(p)
            self.remove_blank_lines(p)

        # Remove @path.
        if root.b.startswith('@path'):
            lines = g.splitLines(root.b)
            root.b = ''.join(lines[1:])

        # Remove the useless first block comment.
        self.remove_first_block_comment(root)

        # Append @language.
        if '@language' not in root.b:
            root.b = root.b.rstrip() + f"\n\n@language {self.language}\n"
    #@+node:ekr.20231022073306.6: *4* indented_i.indent_node
    curlies_pat = re.compile(r'{|}')
    close_curly_pat = re.compile(r'}')
    semicolon_pat = re.compile(r'}\s*;')

    def indent_node(self, p: Position) -> None:
        """
        Remove curly brackets from p.b.

        Do not remove matching brackets if ';' follows the closing bracket.
        """

        tag = f"{g.my_name()}"
        if not p.b.strip():
            return

        def oops(message):
            g.es_print(f"{self.file_name:>30}: {message}")

        lines = g.splitLines(p.b)
        guide_lines = self.importer.make_guide_lines(lines)

        # The stack contains tuples(curly_bracket, line_number, column_number) for each curly bracket.
        # Note: adding a 'level' entry to these tuples would be tricky.
        stack: list[tuple[str, int, int]] = []
        info: dict[tuple, tuple] = {}  # Keys and values are tuples, as above.

        # Pass 1: Create the info dict.
        level = 0  # To check for unmatched braces.
        for line_number, line in enumerate(guide_lines):
            last_column = 0
            for m in re.finditer(self.curlies_pat, line):
                curly = m.group(0)
                column_number = m.start()
                assert last_column == 0 or last_column < column_number, f"{tag} unexpected column"
                assert 0 <= column_number < len(line), f"{tag} column out of range"
                last_column = column_number
                # g.trace(f" {curly} lvl: {level} col: {column_number:3} line: {line_number:3} {line!r}")
                if curly == '{':
                    stack.append((curly, line_number, column_number))
                else:
                    assert curly == '}', f"{tag}: not }}"
                    if not stack:
                        oops(f"   Stack underflow: {p.h}")
                        return
                    top = stack.pop()
                    top_curly, top_line_number, top_column_number = top
                    assert top_curly == '{', f"{tag} stack mismatch"
                    this_info = (curly, line_number, column_number)
                    info[top] = this_info
                    info[this_info] = top
                level += (1 if curly == '{' else -1)
        if level != 0:
            oops(f"Unmatched brackets: {p.h} level: {level}")
            return

        # Pass 2: Make the substitutions when '}' is seen.
        result_lines = []  # Must be empty here.
        for line_number, line in enumerate(guide_lines):

            if '}' not in line:
                # No substitution is possible.
                result_lines.append(lines[line_number])
                continue

            # Typescript only: Don't make the substitution if '};' appears on the line.
            if self.language == 'typescript' and self.semicolon_pat.search(line):
                # g.trace('Skip };', repr(line))
                result_lines.append(lines[line_number])
                continue

            for m in re.finditer(self.close_curly_pat, line):
                column_number = m.start()
                this_info = ('}', line_number, column_number)
                assert this_info in info, f"no matching info: {this_info}"
                match_curly, match_line, match_column = info[this_info]
                assert match_curly == '{', f"{tag}: wrong matching curly bracket"

                # Don't make the substitution if the match is on the same line.
                if match_line == line_number:
                    # g.trace('Same line', repr(line))
                    result_lines.append(lines[line_number])
                    break

                if 0:
                    print('')
                    print(f"{tag} Remove")
                    print(f"matching: {{ line: {match_line:3} column: {match_column:2} {guide_lines[match_line]!r}")
                    print(f"    this: }} line: {line_number:3} column: {column_number:2} {line!r}")

                # Replace the previous line in result_lines, *not* lines.
                s = result_lines[match_line]
                new_line = s[:match_column] + ' ' + s[match_column + 1 :]
                result_lines[match_line] = new_line.rstrip() + '\n' if new_line.strip() else '\n'

                # Append this *real* line to result_lines.
                s = lines[line_number]
                this_line = s[:column_number] + ' ' + s[column_number + 1 :]
                result_lines.append(this_line.rstrip() + '\n' if this_line.strip() else '\n')

        # Set the result
        p.b = ''.join(result_lines).rstrip() + '\n'
    #@+node:ekr.20231022150805.1: *4* indented_i.remove_blank_lines
    def remove_blank_lines(self, p: Position) -> None:
        """Replace multiple blank lines with a single blank line."""
        if not p.b.strip():
            return
        result_lines = []
        for line in g.splitLines(p.b):
            if line.strip():
                result_lines.append(line)
            elif result_lines and result_lines[-1].strip():
                # A blank line preceded by a non-blank line.
                result_lines.append('\n')
        p.b = ''.join(result_lines).rstrip() + '\n'
    #@+node:ekr.20231023045225.1: *4* indented_i.remove_first_block_comment
    def remove_first_block_comment(self, p: Position) -> None:
        """Remove the first block C comment."""
        if not p.b.strip():
            return
        lines = g.splitLines(p.b)
        if not lines[0].startswith('/*'):
            return
        for i, line in enumerate(lines):
            if line.strip().endswith('*/'):
                tail = lines[i + 1 :]
                p.b = ''.join(tail).lstrip('\n')
                return
    #@+node:ekr.20231023044845.1: *4* indented_i.remove_includes
    def remove_includes(self, p: Position) -> None:
        """Remove #include lines."""
        if not p.b.strip():
            return
        lines = g.splitLines(p.b)
        result_lines = [z for z in lines if not z.startswith('#include ')]
        p.b = p.b = ''.join(result_lines).rstrip() + '\n'
    #@+node:ekr.20231022152015.1: *4* indented_i.remove_trailing_semicolons
    def remove_trailing_semicolons(self, p: Position) -> None:

        if not p.b.strip():
            return
        lines = g.splitLines(p.b)
        result_lines = []
        for line in lines:
            line_s = line.rstrip()
            if line_s.endswith(';'):
                line = line_s[:-1] + '\n'
            result_lines.append(line)
        p.b = p.b = ''.join(result_lines).rstrip() + '\n'
    #@+node:ekr.20231022150031.1: *3* indented_i.isAtFileNode & atFileName
    def isAtFileNode(self, p: Position) -> bool:
        h = p.h
        if h.startswith('@@'):
            h = h[1:]
        # Not complete.
        return h.startswith(('@auto ', '@clean ', '@edit ', '@file '))

    def atFileName(self, p: Position) -> str:
        assert self.isAtFileNode(p), repr(p.h)
        i = p.h.find(' ')
        assert i > -1, p.h
        return p.h[i:].strip()
    #@-others
#@+node:ekr.20231024024201.1: **  class Token
class Token:
    """
    A class representing a Lisp token.
    """
    def __init__(self, kind, value):
        self.kind = kind
        self.value = value

    def __repr__(self):
        return f"Token: {self.kind!r}: {self.value!r}"

    __str__ = __repr__
#@+node:ekr.20231022080007.1: ** class Indented_C
class Indented_C(Indented_Importer):
    """A class to support indented C files."""

    extensions: list[str] = ['.c', '.cpp', '.cc']
    importer_class = C_Importer
    language = 'c'
#@+node:ekr.20230917083456.1: ** class Indented_Lisp
class Indented_Lisp(Indented_Importer):
    """
    A class to support indented Lisp files.

    This class rearranges tokens. Guide lines won't work.
    """

    extensions: list[str] = ['.el', '.scm']
    importer_class = None  # There is no need for importer.make_guide_lines.
    language = 'lisp'
    operators = (
        # From lowest to highest precedence.
        'and', 'or',
        'max', 'min',
        '==', '<=', '>=', '!=',  # Tokenizer converts '/=' to '!=' and '=' to '=='
        '<', '>',
        '+', '-',
        '*', '/',
        '%',
    )

    # For error messages only. Set in indent_outline.
    p: Position = None

    #@+others
    #@+node:ekr.20231024045727.1: *3* indented_lisp.find_matching_paren
    def find_matching_paren(self, i: int, tokens: list[Token]) -> int:
        """Return the index of the matching closing parenthesis."""
        assert tokens[i].kind == '(', tokens[i]
        start_i = i
        i += 1
        level = 1
        while i < len(tokens):
            token = tokens[i]
            if token.kind == '(':
                level += 1
            elif token.kind == ')':
                level -= 1
                if level == 0:
                    return i
            i += 1
        # Give an error.
        tail_tokens = tokens[start_i:]
        tail_values = [z.value for z in tail_tokens]
        if 0:
            tail_s = ''.join(tail_values)[:20]
            g.trace('No matching close paren', start_i, tail_s, '\n')
        return None
    #@+node:ekr.20231027085715.1: *3* indented_lisp.flatten
    def flatten(self, obj: Union[list, Token]) -> list[Token]:
        """Flatten the given object."""
        if isinstance(obj, Token):
            return [obj]
        assert isinstance(obj, list), (obj.__class__.__name__, g.callers())
        results: list[Token] = []
        for z in obj:
            results.extend(self.flatten(z))
        for z in results:
            assert isinstance(z, Token), (z.__class__.__name__, g.callers())
        return results
    #@+node:ekr.20231024044536.1: *3* indented_lisp.indent_outline (top-level)
    def indent_outline(self, root: Position) -> None:
        """
        Indented_Lisp.indent_outline: Indent the body text of root and all its
        descendants.

        Called by indented_i.do_import.
        """
        for p in root.self_and_subtree():
            self.p = p
            if p.b.strip():
                tokens = self.tokenize(p)
                output_tokens = self.simplify_tokens(tokens)
                p.b = self.tokens_to_body(output_tokens)
            self.remove_blank_lines(p)

        # Remove @path.
        if root.b.startswith('@path'):
            lines = g.splitLines(root.b)
            root.b = ''.join(lines[1:])

        # Append @language.
        if '@language' not in root.b:
            root.b = root.b.rstrip() + f"\n\n@language {self.language}\n"
    #@+node:ekr.20231027084804.1: *3* indented_lisp.parse
    def parse(self, tokens: list[Token]) -> list[list[Token]]:
        """
        Parse the given tokens into a list of items, removing all blanks and parens.

        Items have the following form:

        Atoms:       Lists of length 1.
        Expressions: Lists of length >= 3, beginning with '(' and ending with ')'.
        """
        p = self.p
        items: list[list[Token]] = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            kind = token.kind
            progress = i
            if kind in ' ':
                i += 1  # Ignore blanks
            elif kind == '\n':
                items.append([token])
                i += 1  # Retains newlines for now.
            elif kind == '(':
                j = self.find_matching_paren(i, tokens)
                if j is None:
                    # g.trace(f"Unmatched '(': {i} {p.h}")
                    items.append([token])
                    i += 1
                else:  # Append the Expression *without* parens.
                    assert tokens[j].kind == ')', (i, j, tokens[j])
                    items.append(tokens[i : j + 1])
                    i = j + 1
            elif kind in ('"', 'symbol', 'number'):
                # Append an expected atom.
                items.append([token])
                i += 1
            else:
                # Append an unusual atom.
                items.append([token])
                # g.trace(f"Unusual token: {i} {p.h} {token!r}")
                i += 1
            assert i > progress, (i, token, p.h)
        for item in items:
            assert isinstance(item, list), repr(item)
        return items
    #@+node:ekr.20231027042313.1: *3* indented_lisp.simplify_tokens
    def simplify_tokens(self, tokens: list[Token]) -> list[Token]:
        """
        Simplify all the given items, moving parens and converting prefix operators to infix.

        Items represent either atoms or parenthesized expressions.  See parse.
        """
        results: list[Token] = []
        items = self.parse(tokens)
        for item in items:
            simplified_item = self.simplify_item(item)
            results.extend(self.flatten(simplified_item))
        ### g.printObj(results, tag='simplify_tokens')
        return results
    #@+node:ekr.20231024103253.1: *3* indented_lisp.simplify_item
    def simplify_item(self, item: list[Token]) -> list[Token]:
        """
        Remove as many parentheses as possible from the list of tokens,
        converting prefix operators to infix where possible.
        """
        results: list[Token] = []
        assert isinstance(item, list), repr(item)
        if len(item) == 1:
            atom = item[0]
            assert isinstance(atom, Token), repr(atom)
            results.append(atom)
        else:
            expression = item
            assert isinstance(item, list), (repr(expression.__class__.__name__), g.callers())
            results.extend(self.to_infix(expression))
        return results
    #@+node:ekr.20231027061647.1: *3* indented_lisp.to_infix
    def to_infix(self, item: list[Token], level: int = 0) -> list[Token]:
        """Convert the item to infix notation."""
        p = self.p

        #@+<< to_infix: define predicates >>
        #@+node:ekr.20231028050301.1: *4* << to_infix: define predicates >>
        def is_atom(item: list[Token]) -> bool:
            return len(item) == 1

        def is_known_op(op: Token) -> bool:
            return (
                op.kind in self.operators
                or op.kind == 'symbol' and op.value in self.operators
            )

        def is_newline(item: list[Token]) -> bool:
            return len(item) == 1 and item[0].kind == '\n'

        def is_ws(item: list[Token]) -> bool:
            return len(item) == 1 and item[0].kind in ' \n\t'

        def is_defun(op, args: list[list[Token]]) -> bool:
            return (
                op.kind == 'symbol' and op.value == 'defun'
                and bool(args) and len(args) > 1
                and args[0][0].kind == 'symbol'
                and args[1][0].kind == '('
            )

        def is_setq(op, args: list[list[Token]]) -> bool:
            return (
                op.kind == 'symbol' and op.value == 'setq'
                and bool(args) and len(args) > 1
                and args[0][0].kind == 'symbol'
            )
        #@-<< to_infix: define predicates >>

        # Pre-checks.
        assert isinstance(item, list), repr(item)
        assert item[0].kind == '('
        assert item[-1].kind == ')'

        # Do nothing with atoms or short items.
        if is_atom(item) or len(item) < 3:
            assert isinstance(item[0], Token), repr(item)
            return item

        # Do nothing if the function/operator is a list:
        op = item[1]
        if not isinstance(op, Token):
            g.trace(f"List operator: {op!r} {p.h}")
            return item

        # Let block.
        arg_tokens = item[2:-1]
        args: list[list[Token]] = self.parse(arg_tokens)
        results: list[Token] = []

        # Define tokens.
        comma_token = Token(',', ',')
        lt_token = Token('(', '(')
        rt_token = Token(')', ')')

        # Post check.
        for arg in args:
            assert isinstance(arg, list), repr(arg)

        # Convert!
        if is_known_op(op):
            # Convert to infix notation.
            add_parens = op.value in '%'  # Not sound.
            if add_parens:
                results.append(lt_token)
            for i, arg in enumerate(args):
                if is_newline(arg):
                    results.append(Token('\n', '\n' + 2 * ' ' * max(0, level - 1)))
                    continue
                if is_atom(arg):
                    results.extend(arg)
                else:
                    converted_arg = self.to_infix(arg, level=level + 1)
                    results.extend(self.flatten(converted_arg))
                if i + 1 < len(args):
                    results.append(op)
            if add_parens:
                results.append(rt_token)
        elif is_defun(op, args):
            # Convert defun to def name (args)
            results.append(Token('def', 'def'))
            results.extend(args[0])  # Function name.
            results.extend(args[1])  # Argument list.
            results.append(Token(':', ':'))
            # Convert the body.
            level += 1
            for arg in args[2:]:
                if is_newline(arg):
                    results.append(Token('\n', '\n' + 2 * ' ' * level))
                elif is_atom(arg):
                    results.extend(arg)
                else:
                    converted_arg = self.to_infix(arg, level=level + 1)
                    results.extend(self.flatten(converted_arg))
            level -= 1
        elif is_setq(op, args):
            results.extend(args[0])  # Var name.
            results.append(Token('=', '='))
            # Convert the value.
            level += 1
            for arg in args[1:]:
                if is_newline(arg):
                    results.append(Token('\n', '\n' + 2 * ' ' * level))
                elif is_atom(arg):
                    results.extend(arg)
                else:
                    converted_arg = self.to_infix(arg, level=level)
                    results.extend(self.flatten(converted_arg))
            level -= 1
        else:
            # Convert to function notation.
            level += 1
            results.extend([op, lt_token])
            for i, arg in enumerate(args):
                if is_newline(arg):
                    results.append(Token('\n', '\n' + 2 * ' ' * level))
                    continue
                if is_atom(arg):
                    results.extend(arg)
                else:
                    converted_arg = self.to_infix(arg, level=level)
                    results.extend(self.flatten(converted_arg))
                if i + 1 < len(args):
                    results.append(comma_token)
            results.append(rt_token)
            level -= 1

        # print(f"\nResults: op: {op}, level: {level}\n{self.to_string(results)}")
        return results
    #@+node:ekr.20231026081944.1: *3* indented_lisp.to_string
    def to_string(self, tokens: list[Token]) -> str:
        """Convert a list of tokens to a string."""
        if not tokens:
            return ''
        results: list[str] = []
        for i, token in enumerate(tokens):
            prev_kind = '' if i == 0 else tokens[i - 1].kind
            prev_result = results[-1] if results else ''
            kind = token.kind
            if kind == ' ':
                pass
            elif kind == ')':
                results.append(')')
            elif kind == '(':
                if prev_kind in ('(', 'symbol'):
                    results.append('(')
                else:
                    results.extend([' ', '('])
            elif kind == '\n':
                # To infix adds the indentation.
                results.append(token.value)
            elif kind in '@:,':
                if prev_result == ' ':
                    results[-1] = ''
                results.append(token.value)
            else:
                # All other tokens.
                if prev_kind in '@\n(':
                    results.append(token.value)
                else:
                    # g.trace(repr(prev_kind), repr(token.value))
                    results.extend([' ', token.value])
        return ''.join(results).strip()
    #@+node:ekr.20231024024109.1: *3* indented_lisp.tokenize
    def tokenize(self, p: Position) -> list[Token]:
        """Create p.b to a list of Lisp_Tokens."""
        # ; is the only comment delim.
        # " is the only string delim
        s = p.b.rstrip()  # Remove trailing newlines.
        tokens: list[Token] = []

        def is_symbol1(ch: str) -> bool:
            """Return True if ch can start a symbol."""
            return ch.isalpha() or ch == '_'

        def is_symbol(ch: str) -> bool:
            """Return True if ch is valid within a symbol."""
            # Approximate. This class treats "operators" separately.
            return ch.isalnum() or ch in '_-'

        # Tokenize character by character.
        i = 0
        while i < len(s):
            progress = i
            ch = s[i]
            if ch == '\\':
                # Skip the next character! The lisp colorizer appears to have a bug here.
                tokens.append(Token(ch, ch))
                i += 1
                if i < len(s):
                    ch = s[i]
                    tokens.append(Token(ch, ch))
                    i += 1
            elif ch == ';':  # Scan a comment.
                start = i
                i += 1
                while i < len(s) and s[i] != '\n':
                    i += 1
                tokens.append(Token(ch, s[start:i]))
            elif ch == '"':  # Scan a string.
                start = i
                i += 1
                while i < len(s):
                    if s[i] == '\\':
                        i += 2
                    elif s[i] == '"':
                        i += 1
                        break
                    else:
                        i += 1
                else:
                    g.es_print(f"{self.file_name}: Unterminated string in {p.h}")
                tokens.append(Token(ch, s[start:i]))
            elif ch == ' ':  # Convert multiple blanks to a single blank.
                start = i
                i += 1
                while i < len(s) and s[i] in ' \n':
                    i += 1
                tokens.append(Token(' ', ' '))
            elif ch == '\n':
                tokens.append(Token('\n', '\n'))
                i += 1
            elif ch.isdigit():
                start = i
                while i < len(s) and s[i].isdigit():
                    i += 1
                tokens.append(Token('number', s[start:i]))
            elif ch == '|':  # Everything up to the matching '|' is part of the symbol!
                i += 1
                start = i
                while i < len(s) and s[i] != '|':
                    i += 1
                if i < len(s) and s[i] == '|':
                    tokens.append(Token('symbol', s[start:i]))
                else:
                    g.es_print(f"{self.file_name}: Unterminated '|' symbol in {p.h}")
            elif is_symbol1(ch):
                start = i
                i += 1
                while i < len(s) and is_symbol(s[i]):
                    i += 1
                tokens.append(Token('symbol', s[start:i]))
            elif ch in '/<>':  # Convert '/=' to '!=', and handle '<=' and '>='.
                if i < len(s) and s[i + 1] == '=':
                    op = '!=' if ch == '/' else ch + '='
                    tokens.append(Token(op, op))
                    i += 2
                else:
                    tokens.append(Token(ch, ch))
                    i += 1
            elif ch == '=':  # Convert '=' to '=='
                tokens.append(Token('==', '=='))
                i += 1
            else:  # Everything else gets its own token.
                i += 1
                tokens.append(Token(ch, ch))
            assert i > progress, (repr(ch), i, repr(s[i : i + 20]))
        # g.printObj(tokens, tag='tokenize')
        return tokens
    #@+node:ekr.20231027041906.1: *3* indented_lisp.tokens_to_body
    def tokens_to_body(self, tokens: list[Token]) -> str:
        """Convert a list of tokens to body text."""
        return self.to_string(tokens).strip() + '\n'
    #@-others
#@+node:ekr.20231022073306.1: ** class Indented_TypeScript
class Indented_TypeScript(Indented_Importer):
    """A class to support indented Typescript files."""

    extensions: list[str] = ['.ts',]
    language = 'typescript'
    importer_class = TS_Importer
#@-others
#@-leo
