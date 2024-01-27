#@+leo-ver=5-thin
#@+node:ekr.20240105140814.1: * @file leoTokens.py
# This file is part of Leo: https://leo-editor.github.io/leo-editor
# Leo's copyright notice is based on the MIT license:
# https://leo-editor.github.io/leo-editor/license.html

#@+<< leoTokens.py: docstring >>
#@+node:ekr.20240105140814.2: ** << leoTokens.py: docstring >>
"""
leoTokens.py.

**Stand-alone operation**

usage:
    python -m leo.core.leoTokens --help
    python -m leo.core.leoTokens --orange [ARGS] PATHS
    python -m leo.core.leoTokens --py-cov [ARGS]
    python -m leo.core.leoTokens --pytest [ARGS]
    python -m leo.core.leoTokens --unittest [ARGS]

examples:
    python -m leo.core.leoTokens --orange --force --verbose PATHS
    python -m leo.core.leoTokens --py-cov "-f TestOrange"
    python -m leo.core.leoTokens --pytest "-f TestOrange"
    python -m leo.core.leoTokens --unittest TestOrange

positional arguments:
  PATHS              directory or list of files

optional arguments:
  -h, --help         show this help message and exit
  --force            operate on all files. Otherwise operate only on modified files
  --orange           leonine text formatter (Orange is the new Black)
  --orange-diff      show orange diff
  --py-cov           run pytest --cov on leoAst.py
  --pytest           run pytest on leoAst.py
  --unittest         run unittest on leoAst.py
  --verbose          verbose output

**Links**

Leo...
Ask for help:       https://groups.google.com/forum/#!forum/leo-editor
Report a bug:       https://github.com/leo-editor/leo-editor/issues

black:              https://pypi.org/project/black/
tokenize.py:        https://docs.python.org/3/library/tokenize.html

**Studying this file**

I strongly recommend that you use Leo when studying this code so that you
will see the file's intended outline structure.

Without Leo, you will see only special **sentinel comments** that create
Leo's outline structure. These comments have the form::

    `#@<comment-kind>:<user-id>.<timestamp>.<number>: <outline-level> <headline>`
"""
#@-<< leoTokens.py: docstring >>
#@+<< leoTokens.py: imports & annotations >>
#@+node:ekr.20240105140814.3: ** << leoTokens.py: imports & annotations >>
from __future__ import annotations
import argparse
import ast
import difflib
import glob
import keyword
import io
import os
import re
import subprocess
import textwrap
import time
import tokenize
from typing import Any, Generator, Optional, Union

try:
    from leo.core import leoGlobals as g
except Exception:  # pragma: no cover
    # check_g function gives the message.
    g = None

Node = ast.AST
Settings = Optional[dict[str, Any]]
#@-<< leoTokens.py: imports & annotations >>

debug: bool = True

#@+others
#@+node:ekr.20240105140814.5: ** command: orange_command & helper (leoTokens.py)
def orange_command(
    arg_files: list[str],
    files: list[str],
    settings: Settings = None,
) -> None:  # pragma: no cover
    """The outer level of the 'tbo/orange' command."""
    if not check_g():
        return
    t1 = time.process_time()
    n_tokens = 0
    n_changed = 0
    for filename in files:
        if os.path.exists(filename):
            # print(f"orange {filename}")
            tbo = TokenBasedOrange(settings)
            changed = tbo.beautify_file(filename)
            if changed:
                n_changed += 1
            # Report any unusual scanned/total ratio.
            scanned, tokens = tbo.n_scanned_tokens, len(tbo.tokens)
            token_ratio: float = scanned / tokens

            # Check the ratio: calls to tbo.next/total tokens.
            # This check verifies that there are no serious performance issues.
            # For Leo's sources, this ratio ranges between 0.48 and 1.51.
            if token_ratio > 2.5:
            # A useful performance measure.
                print('')
                g.trace(
                    f"Unexpected token ratio in {g.shortFileName(filename)}\n"
                    f"scanned: {scanned:<5} total: {tokens:<5} ratio: {token_ratio:4.2f}"
                )
            elif 0:  # Print all ratios.
                print(
                    f"scanned: {scanned:<5} total: {tokens:<5} ratio: {token_ratio:4.2f} "
                    f"{g.shortFileName(filename)}"
                )
            n_tokens += tokens
        else:
            print(f"file not found: {filename}")
    # Report the results.
    t2 = time.process_time()
    if n_changed or TokenBasedOrange(settings).verbose:
        print(
            f"tbo: {t2-t1:3.1f} sec. files: {len(files):<3} "
            f"changed: {n_changed:<3} in {','.join(arg_files)}"
        )
#@+node:ekr.20240105140814.8: *3* function: check_g
def check_g() -> bool:  # pragma: no cover
    """print an error message if g is None"""
    if not g:
        print('This statement failed: `from leo.core import leoGlobals as g`')
        print('Please adjust your Python path accordingly')
    return bool(g)
#@+node:ekr.20240106220602.1: ** LeoTokens: debugging functions
#@+node:ekr.20240105140814.41: *3* function: dump_contents
def dump_contents(contents: str, tag: str = 'Contents') -> None:  # pragma: no cover
    print('')
    print(f"{tag}...\n")
    for i, z in enumerate(g.splitLines(contents)):
        print(f"{i+1:<3} ", z.rstrip())
    print('')
#@+node:ekr.20240105140814.42: *3* function: dump_lines
def dump_lines(tokens: list[InputToken], tag: str = 'lines') -> None:  # pragma: no cover
    print('')
    print(f"{tag}...\n")
    for z in tokens:
        if z.line.strip():
            print(z.line.rstrip())
        else:
            print(repr(z.line))
    print('')
#@+node:ekr.20240105140814.43: *3* function: dump_results
def dump_results(tokens: list[OutputToken], tag: str = 'Results') -> None:  # pragma: no cover
    print('')
    print(f"{tag}...\n")
    print(output_tokens_to_string(tokens))
    print('')
#@+node:ekr.20240105140814.44: *3* function: dump_tokens
def dump_tokens(tokens: list[InputToken], tag: str = 'Tokens') -> None:  # pragma: no cover
    print('')
    print(f"{tag}...\n")
    if not tokens:
        return
    print(
        "Note: values shown are repr(value) "
        "*except* for 'string' and 'fstring*' tokens."
    )
    tokens[0].dump_header()
    for z in tokens:
        print(z.dump())
    print('')
#@+node:ekr.20240105140814.27: *3* function: input_tokens_to_string
def input_tokens_to_string(tokens: list[InputToken]) -> str:  # pragma: no cover
    """Return the string represented by the list of tokens."""
    if tokens is None:
        # This indicates an internal error.
        print('')
        g.trace('===== input token list is None ===== ')
        print('')
        return ''
    return ''.join([z.to_string() for z in tokens])
#@+node:ekr.20240105140814.24: *3* function: output_tokens_to_string
def output_tokens_to_string(tokens: list[OutputToken]) -> str:
    """Return the string represented by the list of tokens."""
    if tokens is None:  # pragma: no cover
        # This indicates an internal error.
        print('')
        g.trace('===== output token list is None ===== ')
        print('')
        return ''
    return ''.join([z.to_string() for z in tokens])
#@+node:ekr.20240105140814.52: ** Classes
#@+node:ekr.20240105140814.51: *3* class InternalBeautifierError(Exception)
class InternalBeautifierError(Exception):
    """
    An internal error in the beautifier.

    Errors in the user's source code may raise standard Python errors
    such as IndentationError or SyntaxError.
    """
#@+node:ekr.20240105140814.53: *3* class InputToken
class InputToken:  # leoTokens.py.
    """A class representing a TBO input token."""

    __slots__ = 'context', 'index', 'kind', 'line', 'line_number', 'value'

    def __init__(
        self, kind: str, value: str, index: int, line: str, line_number: int,
    ) -> None:
        self.context: str = None
        self.index = index
        self.kind = kind
        self.line = line  # The entire line containing the token.
        self.line_number = line_number
        self.value = value

    def __repr__(self) -> str:  # pragma: no cover
        s = f"{self.index:<5} {self.kind:>8}"
        return f"Token {s}: {self.show_val(20):22}"

    __str__ = __repr__

    def to_string(self) -> str:
        """Return the contribution of the token to the source file."""
        return self.value if isinstance(self.value, str) else ''

    #@+others
    #@+node:ekr.20240105140814.54: *4* itoken.brief_dump
    def brief_dump(self) -> str:  # pragma: no cover
        """Dump a token."""
        return (
            f"{self.index:>3} line: {self.line_number:<2} "
            f"{self.kind:>15} {self.show_val(100)}")
    #@+node:ekr.20240105140814.55: *4* itoken.dump
    def dump(self) -> str:  # pragma: no cover
        """Dump a token and related links."""
        return (
            f"{self.line_number:4} "
            f"{self.index:>5} {self.kind:>15} "
            f"{self.show_val(100)}"
        )
    #@+node:ekr.20240105140814.56: *4* itoken.dump_header
    def dump_header(self) -> None:  # pragma: no cover
        """Print the header for token.dump"""
        print(
            f"\n"
            f"         node    {'':10} token {'':10}   token\n"
            f"line index class {'':10} index {'':10} kind value\n"
            f"==== ===== ===== {'':10} ===== {'':10} ==== =====\n")
    #@+node:ekr.20240105140814.57: *4* itoken.error_dump
    def error_dump(self) -> str:  # pragma: no cover
        """Dump a token for error message."""
        return f"index: {self.index:<3} {self.kind:>12} {self.show_val(20):<20}"
    #@+node:ekr.20240105140814.58: *4* itoken.show_val
    def show_val(self, truncate_n: int = 8) -> str:  # pragma: no cover
        """Return the token.value field."""
        if self.kind in ('ws', 'indent'):
            val = str(len(self.value))
        elif self.kind == 'string' or self.kind.startswith('fstring'):
            # repr would be confusing.
            val = g.truncate(self.value, truncate_n)
        else:
            val = g.truncate(repr(self.value), truncate_n)
        return val
    #@-others
#@+node:ekr.20240105143307.1: *3* class Tokenizer
class Tokenizer:
    """
    Use Python's tokenizer module to create InputTokens
    See: https://docs.python.org/3/library/tokenize.html
    """

    __slots__ = (
        'contents',
        'fstring_line',
        'fstring_line_number',
        'fstring_values',
        'lines',
        'offsets',
        'prev_offset',
        'token_index',
        'token_list',
    )

    def __init__(self) -> None:
        self.contents: str = None
        self.offsets: list[int] = [0]  # Index of start of each line.
        self.prev_offset = -1
        self.token_index = 0
        self.token_list: list[InputToken] = []
        # Describing the scanned f-string...
        self.fstring_line: str = None
        self.fstring_line_number: int = None
        self.fstring_values: Optional[list[str]] = None

    #@+others
    #@+node:ekr.20240105143307.2: *4* Tokenizer.add_token
    def add_token(self, kind: str, line: str, line_number: int, value: str,) -> None:
        """
        Add an InputToken to the token list.

        Convert fstrings to simple strings.
        """
        if self.fstring_values is None:
            if kind == 'fstring_start':
                self.fstring_line = line
                self.fstring_line_number = line_number
                self.fstring_values = [value]
                return
        else:
            # Accumulating an f-string.
            self.fstring_values.append(value)
            if kind != 'fstring_end':
                return
            # Create a single 'string' token from the saved values.
            kind = 'string'
            value = ''.join(self.fstring_values)
            # Use the line and line number of the 'string-start' token.
            line = self.fstring_line
            line_number = self.fstring_line_number
            # Clear the saved values.
            self.fstring_line = None
            self.fstring_line_number = None
            self.fstring_values = None
            # g.trace(kind, value, line_number, repr(line))

        tok = InputToken(kind, value, self.token_index, line, line_number)
        self.token_index += 1
        self.token_list.append(tok)
    #@+node:ekr.20240105143214.2: *4* Tokenizer.check_results
    def check_results(self, contents: str) -> None:

        # Split the results into lines.
        result = ''.join([z.to_string() for z in self.token_list])
        result_lines = g.splitLines(result)
        # Check.
        ok = result == contents and result_lines == self.lines
        assert ok, (
            f"\n"
            f"      result: {result!r}\n"
            f"    contents: {contents!r}\n"
            f"result_lines: {result_lines}\n"
            f"       lines: {self.lines}"
        )
    #@+node:ekr.20240105143214.3: *4* Tokenizer.check_round_trip
    def check_round_trip(self, contents: str, tokens: list[InputToken]) -> bool:
        result = self.tokens_to_string(tokens)
        ok = result == contents
        if not ok:  # pragma: no cover
            print('\nRound-trip check FAILS')
            print('Contents...\n')
            g.printObj(contents)
            print('\nResult...\n')
            g.printObj(result)
        return ok
    #@+node:ekr.20240105143214.4: *4* Tokenizer.create_input_tokens
    def create_input_tokens(
        self,
        contents: str,
        five_tuples: Generator,
    ) -> list[InputToken]:
        """
        InputTokenizer.create_input_tokens.

        Return list of InputToken's from tokens, a list of 5-tuples.
        """
        # Remember the contents for debugging.
        self.contents = contents

        # Create the physical lines.
        self.lines = contents.splitlines(True)

        # Create the list of character offsets of the start of each physical line.
        last_offset = 0
        for line in self.lines:
            last_offset += len(line)
            self.offsets.append(last_offset)

        # Create self.token_list.
        for five_tuple in five_tuples:
            self.do_token(contents, five_tuple)

        # Print the token list when tracing.
        self.check_results(contents)
        return self.token_list
    #@+node:ekr.20240105143214.5: *4* Tokenizer.do_token (the gem)
    def do_token(self, contents: str, five_tuple: tuple) -> None:
        """
        Handle the given token, optionally including between-token whitespace.

        https://docs.python.org/3/library/tokenize.html
        https://docs.python.org/3/library/token.html

        five_tuple is a named tuple with these fields:
        - type:     The token type;
        - string:   The token string.
        - start:    (srow: int, scol: int) The row (line_number!) and column
                    where the token begins in the source.
        - end:      (erow: int, ecol: int)) The row (line_number!) and column
                    where the token ends in the source;
        - line:     The *physical line on which the token was found.
        """
        import token as token_module

        # Unpack..
        tok_type, val, start, end, line = five_tuple
        s_row, s_col = start  # row/col offsets of start of token.
        e_row, e_col = end  # row/col offsets of end of token.
        line_number = s_row
        kind = token_module.tok_name[tok_type].lower()
        # Calculate the token's start/end offsets: character offsets into contents.
        s_offset = self.offsets[max(0, s_row - 1)] + s_col
        e_offset = self.offsets[max(0, e_row - 1)] + e_col
        # tok_s is corresponding string in the line.
        tok_s = contents[s_offset:e_offset]
        # Add any preceding between-token whitespace.
        ws = contents[self.prev_offset:s_offset]
        if ws:  # Create the 'ws' pseudo-token.
            self.add_token('ws', line, line_number, ws)
        # Always add token, even if it contributes no text!
        self.add_token(kind, line, line_number, tok_s)
        # Update the ending offset.
        self.prev_offset = e_offset
    #@+node:ekr.20240105143214.6: *4* Tokenizer.make_input_tokens (entry)
    def make_input_tokens(self, contents: str) -> list[InputToken]:
        """
        Return a list  of InputToken objects using tokenize.tokenize.

        Perform consistency checks and handle all exceptions.
        """
        global debug
        try:
            # Use Python's tokenizer module.
            # https://docs.python.org/3/library/tokenize.html
            five_tuples = tokenize.tokenize(
                io.BytesIO(contents.encode('utf-8')).readline)
        except Exception:  # pragma: no cover
            print('make_tokens: exception in tokenize.tokenize')
            g.es_exception()
            return None
        tokens = self.create_input_tokens(contents, five_tuples)
        if debug:  # True: 2.9 sec. False: 2.8 sec.
            assert self.check_round_trip(contents, tokens)
        return tokens
    #@+node:ekr.20240105143214.7: *4* Tokenizer.tokens_to_string
    def tokens_to_string(self, tokens: list[InputToken]) -> str:
        """Return the string represented by the list of tokens."""
        if tokens is None:  # pragma: no cover
            # This indicates an internal error.
            print('')
            g.trace('===== No tokens ===== ')
            print('')
            return ''
        return ''.join([z.to_string() for z in tokens])
    #@-others
#@+node:ekr.20240105140814.106: *3* class OutputToken
class OutputToken:
    """
    A class representing an Orange output token.
    """

    def __init__(self, kind: str, value: str):

        self.kind = kind
        self.value = value

    def __repr__(self) -> str:  # pragma: no cover
        return f"OutputToken: {self.show_val(20)}"

    __str__ = __repr__


    def to_string(self) -> str:
        """Return the contribution of the token to the source file."""
        return self.value if isinstance(self.value, str) else ''

    #@+others
    #@+node:ekr.20240105140814.107: *4* otoken.show_val
    def show_val(self, truncate_n: int) -> str:  # pragma: no cover
        """Return the token.value field."""
        if self.kind in ('ws', 'indent'):
            val = str(len(self.value))
        elif self.kind == 'string' or self.kind.startswith('fstring'):
            # repr would be confusing.
            val = g.truncate(self.value, truncate_n)
        else:
            val = g.truncate(repr(self.value), truncate_n)
        return val
    #@-others
#@+node:ekr.20240105140814.108: *3* class ParseState
class ParseState:
    """
    A class representing items in the parse state stack.

    The present states:

    'file-start': Ensures the stack stack is never empty.

    'decorator': The last '@' was a decorator.

        do_op():    push_state('decorator')
        do_name():  pops the stack if state.kind == 'decorator'.

    'indent': The indentation level for 'class' and 'def' names.

        do_name():      push_state('indent', self.level)
        do_dendent():   pops the stack once or
                        twice if state.value == self.level.
    """

    def __init__(self, kind: str, value: Union[int, str]) -> None:
        self.kind = kind
        self.value = value

    def __repr__(self) -> str:
        return f"State: {self.kind} {self.value!r}"  # pragma: no cover

    __str__ = __repr__
#@+node:ekr.20240105145241.1: *3* class TokenBasedOrange
class TokenBasedOrange:  # Orange is the new Black.

    #@+<< TokenBasedOrange: docstring >>
    #@+node:ekr.20240119062227.1: *4* << TokenBasedOrange: docstring >>
    """
    Leo's token-based beautifier.

    This class is like the Orange class in leoAst.py.

    - This class does not use Python's parse tree in any way.

      Instead, this class contains a "good-enough" recursive parser that
      discovers the context for input tokens requiring help. See
      tbo.set_context for details.

    - This class uses bounded look-ahead and look-behind:

      The parser looks ahead at most one *input* token.
      The code generators look behind at most one *output* token.

    - As with leoAst.py, the code generators work much like a peephole
      optimizer.

    - This class is about twice as fast as the Orange class in leoAst.py.
    """
    #@-<< TokenBasedOrange: docstring >>
    #@+<< TokenBasedOrange: __slots__ >>
    #@+node:ekr.20240111035404.1: *4* << TokenBasedOrange: __slots__ >>
    __slots__ = [
        # Command-line arguments.
        'diff', 'force', 'silent', 'tab_width', 'verbose',
        # Debugging.
        'contents', 'filename', 'n_scanned_tokens',
        # Global data.
        'code_list', 'tokens',
        # Token-related data for visitors.
        'index', 'line_number', 'token',  # 'line_start'
        # Parsing state for visitors.
        'decorator_seen', 'in_arg_list', 'in_doc_part',
        'state_stack', 'verbatim',
        # State data for whitespace visitors.
        # Don't even *think* about changing these!
        'curly_brackets_level', 'indent_level', 'lws',
        'paren_level', 'square_brackets_stack',
    ]
    #@-<< TokenBasedOrange: __slots__ >>
    #@+<< TokenBasedOrange: patterns >>
    #@+node:ekr.20240108065133.1: *4* << TokenBasedOrange: patterns >>
    # Patterns...
    nobeautify_pat = re.compile(r'\s*#\s*pragma:\s*no\s*beautify\b|#\s*@@nobeautify')

    # Patterns from FastAtRead class, specialized for python delims.
    node_pat = re.compile(r'^(\s*)#@\+node:([^:]+): \*(\d+)?(\*?) (.*)$')  # @node
    start_doc_pat = re.compile(r'^\s*#@\+(at|doc)?(\s.*?)?$')  # @doc or @
    at_others_pat = re.compile(r'^(\s*)#@(\+|-)others\b(.*)$')  # @others

    # Doc parts end with @c or a node sentinel. Specialized for python.
    end_doc_pat = re.compile(r"^\s*#@(@(c(ode)?)|([+]node\b.*))$")
    #@-<< TokenBasedOrange: patterns >>
    #@+<< TokenBasedOrange: python-related constants >>
    #@+node:ekr.20240116040458.1: *4* << TokenBasedOrange: python-related constants >>
    # Statements that must be followed by ':'.
    # https://docs.python.org/3/reference/compound_stmts.html

    # The value of 'name' Tokens denoting Python compound statements.
    compound_statements = [
        'async',  # Must be followed by 'def', 'for', 'with'.
        'class', 'def', 'elif', 'else', 'except', 'for', 'finally', 'if',
        'match', 'try', 'while', 'with',
    ]

    # Statements that must *not* be followed by ':'.
    # https://docs.python.org/3/reference/simple_stmts.html
    simple_statements = [
        'break', 'continue', 'global', 'nonlocal', 'pass',
        'from', 'import',  # special cases.
    ]

    simple_statements_with_value = [
        'assert', 'del', 'raise', 'return', 'type', 'yield',
    ]

    keywords = compound_statements + simple_statements + simple_statements_with_value

    # 'name' tokens that may appear in expressions.
    expression_keywords = ('for', 'if', 'else')

    # 'name' tokens that may appear in expressions.
    operator_keywords = (
        'await',  # Debatable.
        'and', 'in', 'not', 'not in', 'or',  # Operators.
        'True', 'False', 'None',  # Values.
    )

    # Tokens denoting strings.
    string_kinds = ('string', 'fstring-start', 'fstring-middle', 'fstring-end')

    # 'name' tokens that may appear in ternary operators.
    ternary_keywords = ('for', 'if', 'else')
    #@-<< TokenBasedOrange: python-related constants >>

    #@+others
    #@+node:ekr.20240105145241.2: *4* tbo.ctor
    def __init__(self, settings: Settings = None):
        """Ctor for Orange class."""

        # Global count of the number of calls to tbo.next and tbo.prev.
        # See the docstrings of tbo.next and orange_command for details.
        self.n_scanned_tokens = 0

        # Set default settings.
        if settings is None:
            settings = {}
        self.diff = False
        self.force = False
        self.silent = False
        self.tab_width = 4
        self.verbose = False

        # Override defaults from settings dict.
        valid_keys = ('diff', 'force', 'orange', 'silent', 'tab_width', 'verbose')
        for key in settings:  # pragma: no cover
            value = settings.get(key)
            if key in valid_keys and value is not None:
                setattr(self, key, value)
            else:
                g.trace(f"Unexpected setting: {key} = {value!r}")
                g.trace('(TokenBasedOrange)', g.callers())
    #@+node:ekr.20240126012433.1: *4* tbo: Checking & dumping
    #@+node:ekr.20240106220724.1: *5* tbo.dump_token_range
    def dump_token_range(self, i1: int, i2: int, tag: str = None) -> None:  # pragma: no cover
        """Dump the given range of input tokens."""
        if tag:
            print(tag)
        for token in self.tokens[i1 : i2 + 1]:
            print(token.dump())
    #@+node:ekr.20240106090914.1: *5* tbo.expect
    def expect(self, i: int, kind: str, value: str = None) -> None:
        """Raise an exception if self.tokens[i] is not as expected."""
        try:
            token = self.tokens[i]
        except Exception as e:  # pragma: no cover
            self.oops(f"At index {i!r}: Expected{kind!r}:{value!r}, got {e}")

        if token.kind != kind or (value and token.value != value):
            self.oops(f"Expected {kind!r}:{value!r}, got {token!r}")  # pragma: no cover
    #@+node:ekr.20240116042811.1: *5* tbo.expect_name
    def expect_name(self, i: int) -> None:
        """Raise an exception if self.tokens[i] is not as expected."""
        try:
            token = self.tokens[i]
        except Exception as e:  # pragma: no cover
            self.oops(f"At index {i!r}: Expected 'name', got {e}")

        if token.kind != 'name':
            self.oops(f"Expected 'name', got {token!r}")  # pragma: no cover
    #@+node:ekr.20240114015808.1: *5* tbo.expect_op
    def expect_op(self, i: int, value: str) -> None:
        """Raise an exception if self.tokens[i] is not as expected."""
        try:
            token = self.tokens[i]
        except Exception as e:  # pragma: no cover
            self.oops(f"At index {i!r}: Expected 'op':{value!r}, got {e!r}")

        if (token.kind, token.value) != ('op', value):
            self.oops(f"Expected 'op':{value!r}, got {token!r}")  # pragma: no cover
    #@+node:ekr.20240114013952.1: *5* tbo.expect_ops
    def expect_ops(self, i: int, values: list) -> None:
        """Raise an exception if self.tokens[i] is not as expected."""
        try:
            token = self.tokens[i]
        except Exception as e:  # pragma: no cover
            self.oops(f"At index {i!r}: Expected 'op' in {values!r}, got {e!r}")

        if token.kind != 'op' or token.value not in values:
            self.oops(f"Expected 'op' in {values!r}, got {token!r}")  # pragma: no cover
    #@+node:ekr.20240127051941.1: *5* tbo.get_token
    def get_token(self, i: int) -> InputToken:
        """Return the token at i, with full error checking."""
        try:
            token = self.tokens[i]
        except Exception as e:  # pragma: no cover
            self.oops(f"Invalid index: {i!r}: {e}")
        return token
    #@+node:ekr.20240117053310.1: *5* tbo.oops & helper
    def oops(self, message: str) -> None:  # pragma: no cover
        """Raise InternalBeautifierError."""
        raise InternalBeautifierError(self.error_message(message))
    #@+node:ekr.20240112082350.1: *6* tbo.error_message
    def error_message(self, message: str) -> str:  # pragma: no cover
        """
        Print a full error message.

        Print a traceback only if we are *not* unit testing.
        """
        # Compute lines_s.
        line_number = self.token.line_number
        lines = g.splitLines(self.contents)
        n1 = max(0, line_number - 5)
        n2 = min(line_number + 5, len(lines))
        prev_lines = ['\n']
        for i in range(n1, n2):
            marker_s = '***' if i + 1 == line_number else '   '
            prev_lines.append(f"Line {i+1:5}:{marker_s}{lines[i]!r}\n")
        context_s = ''.join(prev_lines) + '\n'

        # Return the full error message.
        return (
            '\n\n'
            'Error in token-based beautifier!\n'
            f"{message.strip()}\n"
            '\n'
            f"At token {self.index}, line: {line_number} file: {self.filename}\n"
            f"{context_s}"
            "Please report this message to Leo's developers"
        )
    #@+node:ekr.20240125182219.1: *5* tbo.trace & helpers
    def trace(self, i: int, i2: Optional[int] = None, *, tag: str = None) -> None:  # pragma: no cover
        """
        Print i, token, and get_token_line(i).

        A surprisingly useful debugging utility.
        """

        token = self.tokens[i]
        indices_s = f"{i}" if i2 is None else f"i: {i} i2: {i2}"

        # Adjust widths below as necessary.
        print(
            f"{g.callers(1)}: {tag or ''}\n"
            f"  callers: {g.callers()}\n"
            f"  indices: {indices_s} token: {token.kind:}:{token.show_val(30)}\n"
            f"     line: {self.get_token_line(i)!r}\n"
            f"     tail: {self.get_tokens_after(i)!r}\n"
        )
    #@+node:ekr.20240124094344.1: *6* tbo.get_token_line
    def get_token_line(self, i: int) -> str:  # pragma: no cover
        """return self.tokens[i].line"""
        try:
            token = self.tokens[i]
        except Exception as e:
            self.oops(f"Bad token index {i!r}: {e}")

        return token.line.rstrip()
    #@+node:ekr.20240127053011.1: *6* tbo.get_tokens_after
    def get_tokens_after(self, i: int) -> str:
        """Return the string containing the values of self.tokens[i:]."""
        try:
            tokens = self.tokens[i:]
        except Exception as e:  # pragma: no cover
            self.oops(f"Invalid index: {i!r}: {e}")
        s = ''.join([z.value for z in tokens]).rstrip()

        # Leading indentation should match self.trace.
        return f"  {i:3} {s}"
    #@+node:ekr.20240105145241.4: *4* tbo: Entries & helpers
    #@+node:ekr.20240105145241.5: *5* tbo.beautify (main token loop)
    def no_visitor(self) -> None:  # pragma: no cover
        self.oops(f"Unknown kind: {self.token.kind!r}")

    def beautify(self,
        contents: str, filename: str, tokens: list[InputToken],
    ) -> str:
        """
        The main line. Create output tokens and return the result as a string.

        beautify_file and beautify_file_def call this method.
        """
        #@+<< tbo.beautify: init ivars >>
        #@+node:ekr.20240112023403.1: *6* << tbo.beautify: init ivars >>
        # Debugging vars...
        self.contents = contents
        self.filename = filename
        self.line_number: int = None

        # The input and output lists...
        self.code_list: list[OutputToken] = []  # The list of output tokens.
        self.tokens = tokens  # The list of input tokens.

        # State vars for whitespace.
        self.curly_brackets_level = 0  # Number of unmatched '{' tokens.
        self.paren_level = 0  # Number of unmatched '(' tokens.
        self.square_brackets_stack: list[bool] = []  # A stack of bools, for self.gen_word().
        self.indent_level = 0  # Set only by do_indent and do_dedent.

        # Parse state.
        self.decorator_seen = False  # Set by do_name for do_op.
        self.in_arg_list = 0  # > 0 if in an arg list of a def.
        self.in_doc_part = False
        self.state_stack: list["ParseState"] = []  # Stack of ParseState objects.

        # Leo-related state.
        self.verbatim = False  # True: don't beautify.

        # Ivars describing the present input token...
        self.index = 0  # The index within the tokens array of the token being scanned.
        self.lws = ''  # Leading whitespace. Required!
        self.token: InputToken = None
        #@-<< tbo.beautify: init ivars >>

        # Pass 1: start the "good enough" recursive descent parser.
        self.parse_statements()

        # The main loop:
        self.gen_token('file-start', '')
        self.push_state('file-start')
        prev_line_number: int = None

        for self.index, self.token in enumerate(tokens):
            # Set global for visitors.
            if prev_line_number != self.token.line_number:
                prev_line_number = self.token.line_number
            # Call the proper visitor.
            if self.verbatim:
                self.do_verbatim()
            else:
                func = getattr(self, f"do_{self.token.kind}", self.no_visitor)
                func()
        # Any post pass would go here.
        result = output_tokens_to_string(self.code_list)
        return result
    #@+node:ekr.20240105145241.6: *5* tbo.beautify_file (entry. write or diff)
    def beautify_file(self, filename: str) -> bool:  # pragma: no cover
        """
        TokenBasedOrange: Beautify the the given external file.

        Return True if the file was changed.
        """
        if False:
            g.trace(
                f"diff: {int(self.diff)} "
                f"force: {int(self.force)} "
                f"silent: {int(self.silent)} "
                f"verbose: {int(self.verbose)} "
                f"{g.shortFileName(filename)}"
            )
        self.filename = filename
        contents, encoding, tokens = self.init_tokens_from_file(filename)
        if not (contents and tokens):
            return False  # Not an error.
        if not isinstance(tokens[0], InputToken):
            self.oops(f"Not an InputToken: {tokens[0]!r}")
        results = self.beautify(contents, filename, tokens)
        if not results:
            return False

        # Something besides newlines must change.
        regularized_contents = self.regularize_nls(contents)
        regularized_results = self.regularize_nls(results)
        if regularized_contents == regularized_results:
            # g.trace(f"No change: {g.shortFileName(filename)}")
            return False
        if not regularized_contents:
            print(f"tbo: no results {g.shortFileName(filename)}")
            return False

        # Write the results
        if not self.silent:
            print(f"tbo: changed {g.shortFileName(filename)}")

        safe = True
        if safe:
            print('tbo: safe mode')

        # Print the diffs for testing!
        if safe or self.diff:
            print(f"Diffs: {filename}")
            self.show_diffs(regularized_contents, regularized_results)
        else:
            self.write_file(filename, regularized_results, encoding=encoding)
        return True
    #@+node:ekr.20240105145241.8: *5* tbo.init_tokens_from_file
    def init_tokens_from_file(self, filename: str) -> tuple[
        str, str, list[InputToken]
    ]:  # pragma: no cover
        """
        Create the list of tokens for the given file.
        Return (contents, encoding, tokens).
        """
        self.indent_level = 0
        self.filename = filename
        contents, encoding = g.readFileIntoString(filename)
        if not contents:
            return None, None, None
        self.tokens = tokens = Tokenizer().make_input_tokens(contents)
        return contents, encoding, tokens
    #@+node:ekr.20240105140814.17: *5* tbo.write_file
    def write_file(self,
        filename: str,
        s: str,
        encoding: str = 'utf-8',
    ) -> None:  # pragma: no cover
        """
        Write the string s to the file whose name is given.

        Handle all exceptions.

        Before calling this function, the caller should ensure
        that the file actually has been changed.
        """
        # g.trace('Writing', filename, encoding, len(s))
        try:
            s2 = g.toEncodedString(s, encoding=encoding, reportErrors=True)
            with open(filename, 'wb') as f:
                f.write(s2)
        except Exception as e:
            g.trace(f"Error writing {filename}\n{e}")
    #@+node:ekr.20200107040729.1: *5* tbo.show_diffs
    def show_diffs(self, s1: str, s2: str) -> None:  # pragma: no cover
        """Print diffs between strings s1 and s2."""
        filename = self.filename
        lines = list(difflib.unified_diff(
            g.splitLines(s1),
            g.splitLines(s2),
            fromfile=f"Old {filename}",
            tofile=f"New {filename}",
        ))
        print('')
        tag = f"Diffs for {filename}"
        g.printObj(lines, tag=tag)
    #@+node:ekr.20240105145241.9: *4* tbo: Visitors & generators
    # Visitors (tbo.do_* methods) handle input tokens.
    # Generators (tbo.gen_* methods) create zero or more output tokens.
    #@+node:ekr.20240105145241.29: *5* tbo.clean
    def clean(self, kind: str) -> None:
        """Remove the last item of token list if it has the given kind."""
        prev = self.code_list[-1]
        if prev.kind == kind:
            self.code_list.pop()
    #@+node:ekr.20240105145241.10: *5* tbo.do_comment
    comment_pat = re.compile(r'^(\s*)#[^@!# \n]')

    def do_comment(self) -> None:
        """Handle a comment token."""
        val = self.token.value
        #
        # Leo-specific code...
        if self.node_pat.match(val):
            # Clear per-node state.
            self.in_doc_part = False
            self.verbatim = False
            self.decorator_seen = False
            # Do *not clear other state, which may persist across @others.
                # self.curly_brackets_level = 0
                # self.in_arg_list = 0
                # self.indent_level = 0
                # self.lws = ''
                # self.paren_level = 0
                # self.square_brackets_stack = []
                # self.state_stack = []
        else:
            # Keep track of verbatim mode.
            if self.beautify_pat.match(val):
                self.verbatim = False
            elif self.nobeautify_pat.match(val):
                self.verbatim = True
            # Keep trace of @doc parts, to honor the convention for splitting lines.
            if self.start_doc_pat.match(val):
                self.in_doc_part = True
            if self.end_doc_pat.match(val):
                self.in_doc_part = False
        #
        # General code: Generate the comment.
        self.clean('blank')
        entire_line = self.token.line.lstrip().startswith('#')
        if entire_line:
            self.clean('hard-blank')
            self.clean('line-indent')
            # #1496: No further munging needed.
            val = self.token.line.rstrip()
            # #3056: Insure one space after '#' in non-sentinel comments.
            #        Do not change bang lines or '##' comments.
            if m := self.comment_pat.match(val):
                i = len(m.group(1))
                val = val[:i] + '# ' + val[i + 1 :]
        else:
            # Exactly two spaces before trailing comments.
            val = '  ' + val.rstrip()
        self.gen_token('comment', val)
    #@+node:ekr.20240111051726.1: *5* tbo.do_dedent
    def do_dedent(self) -> None:
        """Handle dedent token."""
        # Note: other methods use self.indent_level.
        self.indent_level -= 1
        self.lws = self.indent_level * self.tab_width * ' '
        self.gen_line_indent()
    #@+node:ekr.20240105145241.11: *5* tbo.do_encoding
    def do_encoding(self) -> None:
        """Handle the encoding token."""
    #@+node:ekr.20240105145241.12: *5* tbo.do_endmarker
    def do_endmarker(self) -> None:
        """Handle an endmarker token."""
        # Ensure exactly one blank at the end of the file.
        while self.code_list[-1].kind in ('line-end', 'line-indent'):
            self.code_list.pop()
        self.gen_token('line-end', '\n')
    #@+node:ekr.20240105145241.14: *5* tbo.do_indent
    consider_message = 'consider using python/Tools/scripts/reindent.py'

    def do_indent(self) -> None:
        """Handle indent token."""

        # Refuse to beautify mal-formed files.
        if '\t' in self.token.value:  # pragma: no cover
            raise IndentationError(self.error_message(
                f"Leading tabs found: {self.consider_message}"))

        if (len(self.token.value) % self.tab_width) != 0:  # pragma: no cover
            raise IndentationError(self.error_message(
                f"Indentation error! {self.consider_message}"))

        # Handle the token!
        new_indent = self.token.value
        old_indent = self.indent_level * self.tab_width * ' '
        if new_indent > old_indent:
            self.indent_level += 1
        elif new_indent < old_indent:  # pragma: no cover (defensive)
            g.trace('\n===== can not happen', repr(new_indent), repr(old_indent))
        self.lws = new_indent
        self.gen_line_indent()
    #@+node:ekr.20240105145241.16: *5* tbo.do_name & generators
    def do_name(self) -> None:
        """Handle a name token."""
        name = self.token.value
        if name in self.operator_keywords:
            self.gen_word_op(name)
        else:
            self.gen_word(name)


    #@+node:ekr.20240105145241.40: *6* tbo.gen_word
    def gen_word(self, s: str) -> None:
        """Add a word request to the code list."""
        assert s == self.token.value
        assert s and isinstance(s, str), repr(s)
        self.gen_blank()
        self.gen_token('word', s)
        self.gen_blank()
    #@+node:ekr.20240107141830.1: *6* tbo.gen_word_op
    def gen_word_op(self, s: str) -> None:
        """Add a word-op request to the code list."""
        assert s == self.token.value
        assert s and isinstance(s, str), repr(s)
        self.gen_blank()
        self.gen_token('word-op', s)
        self.gen_blank()
    #@+node:ekr.20240105145241.17: *5* tbo.do_newline, do_nl & generators
    def do_newline(self) -> None:
        """
        do_newline: Handle a regular newline.

        do_nl: Handle a continuation line.

        From https://docs.python.org/3/library/token.html

        - NEWLINE tokens end *logical* lines of Python code.

        - NL tokens end *physical* lines. They appear when when a logical line
          of code spans multiple physical lines.
        """
        # Only do_newline and do_nl should call this method.
        token = self.token
        if token.kind not in ('newline', 'nl'):  # pragma: no cover
            self.oops(f"Unexpected newline token: {token!r}")

        # Create the 'line-end' output token.
        self.gen_line_end()

        # Add the indentation until the next indent/unindent token.
        self.gen_line_indent()

    do_nl = do_newline
    #@+node:ekr.20240105145241.25: *6* tbo.gen_line_end
    def gen_line_end(self) -> OutputToken:
        """Add a line-end request to the code list."""

        # This may be called from do_name as well as do_newline and do_nl.
        token = self.token
        if token.kind not in ('newline', 'nl'):
            self.oops(f"Unexpected newline token: {token!r}")  # pragma: no cover

        self.clean('blank')  # Important!
        self.clean('line-indent')
        t = self.gen_token('line-end', '\n')
        return t
    #@+node:ekr.20240105145241.33: *6* tbo.gen_line_indent
    def gen_line_indent(self) -> None:
        """Add a line-indent token."""
        self.clean('line-indent')  # Defensive. Should never happen.
        self.gen_token('line-indent', self.lws)
    #@+node:ekr.20240105145241.18: *5* tbo.do_number
    def do_number(self) -> None:
        """Handle a number token."""
        self.gen_blank()
        self.gen_token('number', self.token.value)
    #@+node:ekr.20240105145241.19: *5* tbo.do_op & generators
    def do_op(self) -> None:
        """Handle an op token."""
        val = self.token.value
        if val == '.':
            self.gen_dot_op()
        elif val == '@':
            self.clean('blank')
            self.gen_token('op-no-blanks', val)
            self.push_state('decorator')
        elif val == ':':
            # Treat slices differently.
            self.gen_colon()
        elif val in ',;':
            # Pep 8: Avoid extraneous whitespace immediately before
            # comma, semicolon, or colon.
            self.clean('blank')
            self.gen_token('op', val)
            self.gen_blank()
        elif val in '([{':
            # Pep 8: Avoid extraneous whitespace immediately inside
            # parentheses, brackets or braces.
            self.gen_lt()
        elif val in ')]}':
            # Ditto.
            self.gen_rt()
        elif val == '=':
            self.gen_equal_op()
        elif val in '~+-':
            self.gen_possible_unary_op()
        elif val == '*':
            self.gen_star_op()
        elif val == '**':
            self.gen_star_star_op()
        else:
            # Pep 8: always surround binary operators with a single space.
            # '==','+=','-=','*=','**=','/=','//=','%=','!=','<=','>=','<','>',
            # '^','~','*','**','&','|','/','//',
            # Pep 8: If operators with different priorities are used, consider
            # adding whitespace around the operators with the lowest priorities.
            self.gen_blank()
            self.gen_token('op', val)
            self.gen_blank()
    #@+node:ekr.20240105145241.31: *6* tbo.gen_colon & helper
    def gen_colon(self) -> None:
        """Handle a colon."""
        val = self.token.value
        context = self.token.context
        prev_i = self.prev(self.index)
        prev = self.tokens[prev_i]

        # Generate the proper code using the context supplied by the parser.
        self.clean('blank')
        if context == 'complex-slice':
            if prev.value not in '[:':
                self.gen_blank()
            self.gen_token('op', val)
            self.gen_blank()
        elif context == 'simple-slice':
            self.gen_token('op-no-blanks', val)
        elif context == 'end-statement':
            self.gen_token('op-no-blank', val)
        elif context == 'dict':
            self.gen_token('op', val)
            self.gen_blank()
        else:
            self.gen_token('op', val)
            self.gen_blank()
    #@+node:ekr.20240109035004.1: *6* tbo.gen_dot_op
    def gen_dot_op(self) -> None:
        """Handle the '.' input token."""
        context = self.token.context
        # Remove previous 'blank' token *before* calculating prev.
        self.clean('blank')
        prev = self.code_list[-1]
        next_i = self.next(self.index)
        next = 'None' if next_i is None else self.tokens[next_i]
        import_is_next = next and next.kind == 'name' and next.value == 'import'
        if prev.kind == 'word' and prev.value in ('from', 'import'):
            # Handle previous 'from' and 'import' keyword.
            self.gen_blank()
            if import_is_next:
                self.gen_token('op', '.')
                self.gen_blank()
            else:
                self.gen_token('op-no-blanks', '.')
        elif context == 'from':
            # Don't put spaces between '.' tokens.
            # Do put a space between the last '.' and 'import'.
            if import_is_next:
                self.gen_token('op', '.')
                self.gen_blank()
            else:
                self.gen_token('op-no-blanks', '.')
        else:
            self.gen_token('op-no-blanks', '.')
    #@+node:ekr.20240105145241.20: *6* tbo.gen_equal_op
    # Keys: token.index of '=' token. Values: count of ???s
    arg_dict: dict[int, int] = {}

    def gen_equal_op(self) -> None:

        val = self.token.value
        context = self.token.context

        if context == 'initializer':
            # Pep 8: Don't use spaces around the = sign when used to indicate
            #        a keyword argument or a default parameter value.
            #        However, when combining an argument annotation with a default value,
            #        *do* use spaces around the = sign.
            self.clean('blank')
            self.gen_token('op-no-blanks', val)
        else:
            self.gen_blank()
            self.gen_token('op', val)
            self.gen_blank()
    #@+node:ekr.20240105145241.35: *6* tbo.gen_lt
    def gen_lt(self) -> None:
        """Generate code for a left paren or curly/square bracket."""
        val = self.token.value
        assert val in '([{', repr(val)
        if val == '(':
            self.paren_level += 1
        elif val == '[':
            self.square_brackets_stack.append(False)
        else:
            self.curly_brackets_level += 1
        self.clean('blank')
        prev = self.code_list[-1]

        if prev.kind in ('op', 'word-op'):
            self.gen_blank()
            self.gen_token('lt', val)
        elif prev.kind == 'word':
            # Only suppress blanks before '(' or '[' for non-keywords.
            if val == '{' or prev.value in ('if', 'else', 'elif', 'return', 'for', 'while'):
                self.gen_blank()
            elif val == '(':
                self.in_arg_list += 1
            self.gen_token('lt', val)
        else:
            self.clean('blank')
            self.gen_token('op-no-blanks', val)
    #@+node:ekr.20240105145241.37: *6* tbo.gen_possible_unary_op & helper (now simpler)
    def gen_possible_unary_op(self) -> None:
        """Add a unary or binary op to the token list."""
        val = self.token.value
        self.clean('blank')
        if self.is_unary_op(self.index, val):
            prev = self.code_list[-1]
            if prev.kind == 'lt':
                self.gen_token('op-no-blanks', val)
            else:
                self.gen_blank()
                self.gen_token('op-no-blanks', val)
        else:
            self.gen_blank()
            self.gen_token('op', val)
            self.gen_blank()

    #@+node:ekr.20240109082712.1: *7* tbo.is_unary_op
    def is_unary_op(self, i: int, val: str) -> bool:

        if val == '~':
            return True
        if val not in '+-':
            return False
        # Get the previous significant token.
        prev_i = self.prev(i)
        prev_token = self.tokens[prev_i]
        kind, value = prev_token.kind, prev_token.value
        if kind in ('number', 'string'):
            return_val = False
        elif kind == 'op' and value in ')]':
            return_val = False
        elif kind == 'op' and value in '{([:':
            return_val = True
        elif kind != 'name':
            return_val = True
        else:
            # The hard case: prev_token is a 'name' token.
            # Any Python keyword indicates a unary operator.
            return_val = keyword.iskeyword(value) or keyword.issoftkeyword(value)
        return return_val
    #@+node:ekr.20240105145241.36: *6* tbo.gen_rt
    def gen_rt(self) -> None:
        """Generate code for a right paren or curly/square bracket."""
        val = self.token.value
        assert val in ')]}', repr(val)
        if val == ')':
            self.paren_level -= 1
            self.in_arg_list = max(0, self.in_arg_list - 1)
        elif val == ']':
            self.square_brackets_stack.pop()
        else:
            self.curly_brackets_level -= 1
        self.clean('blank')
        self.gen_token('rt', val)
    #@+node:ekr.20240105145241.38: *6* tbo.gen_star_op
    def gen_star_op(self) -> None:
        """Put a '*' op, with special cases for *args."""
        val = self.token.value
        context = self.token.context

        self.clean('blank')
        if context == 'arg':
            self.gen_blank()
            self.gen_token('op-no-blanks', val)
        else:
            self.gen_blank()
            self.gen_token('op', val)
            self.gen_blank()
    #@+node:ekr.20240105145241.39: *6* tbo.gen_star_star_op
    def gen_star_star_op(self) -> None:
        """Put a ** operator, with a special case for **kwargs."""
        val = self.token.value
        context = self.token.context

        self.clean('blank')
        if context == 'arg':
            self.gen_blank()
            self.gen_token('op-no-blanks', val)
        else:
            self.gen_blank()
            self.gen_token('op', val)
            self.gen_blank()
    #@+node:ekr.20240105145241.3: *6* tbo.push_state
    def push_state(self, kind: str, value: Union[int, str] = None) -> None:
        """Append a state to the state stack."""
        state = ParseState(kind, value)
        self.state_stack.append(state)
    #@+node:ekr.20240105145241.21: *5* tbo.do_string
    def do_string(self) -> None:
        """
        Handle a 'string' token.

        The Tokenizer converts all f-string tokens to a single 'string' token.
        """
        # Careful: continued strings may contain '\r'
        val = self.regularize_nls(self.token.value)
        self.gen_token('string', val)
        self.gen_blank()
    #@+node:ekr.20240105145241.22: *5* tbo.do_verbatim
    beautify_pat = re.compile(
        r'#\s*pragma:\s*beautify\b|#\s*@@beautify|#\s*@\+node|#\s*@[+-]others|#\s*@[+-]<<')

    def do_verbatim(self) -> None:
        """
        Handle one token in verbatim mode.
        End verbatim mode when the appropriate comment is seen.
        """
        kind = self.token.kind
        #
        # Careful: tokens may contain '\r'
        val = self.regularize_nls(self.token.value)
        if kind == 'comment':
            if self.beautify_pat.match(val):
                self.verbatim = False
            val = val.rstrip()
            self.gen_token('comment', val)
            return
        if kind == 'indent':
            self.indent_level += 1
            self.lws = self.indent_level * self.tab_width * ' '
        if kind == 'dedent':
            self.indent_level -= 1
            self.lws = self.indent_level * self.tab_width * ' '
        self.gen_token('verbatim', val)
    #@+node:ekr.20240105145241.23: *5* tbo.do_ws
    def do_ws(self) -> None:
        """
        Handle the "ws" pseudo-token.  See Tokenizer.itok.do_token (the gem).

        Put the whitespace only if if ends with backslash-newline.
        """
        val = self.token.value
        # Handle backslash-newline.
        if '\\\n' in val:
            self.clean('blank')
            self.gen_token('op-no-blanks', val)
            return
        # Handle start-of-line whitespace.
        prev = self.code_list[-1]
        inner = self.paren_level or self.square_brackets_stack or self.curly_brackets_level
        if prev.kind == 'line-indent' and inner:
            # Retain the indent that won't be cleaned away.
            self.clean('line-indent')
            self.gen_token('hard-blank', val)
    #@+node:ekr.20240105145241.27: *5* tbo.gen_blank
    def gen_blank(self) -> None:
        """Add a blank request to the code list."""
        prev = self.code_list[-1]
        if prev.kind not in (
            'blank',
            # 'blank-lines',  # black only: Request for n blank lines.
            'file-start',
            'hard-blank',
            'line-end',
            'line-indent',
            'lt',  # A left paren or curly/square bracket.
            'op-no-blanks',  # A demand that no blank follows this op.
            'unary-op',
        ):
            self.gen_token('blank', ' ')
    #@+node:ekr.20240105145241.26: *5* tbo.gen_token
    def gen_token(self, kind: str, value: Any) -> OutputToken:
        """Add an output token to the code list."""
        tok = OutputToken(kind, value)
        tok.index = len(self.code_list)
        self.code_list.append(tok)
        return tok
    #@+node:ekr.20240105140814.12: *5* tbo.regularize_nls
    def regularize_nls(self, s: str) -> str:
        """Regularize newlines within s."""
        return s.replace('\r\n', '\n').replace('\r', '\n')
    #@+node:ekr.20240105145241.41: *4* tbo: Parser
    # Parsers pre-scan input tokens, adding context to tokens that need help.
    #@+node:ekr.20240106181128.1: *5* tbo.parse_annotation
    def parse_annotation(self, i1: int, end: int) -> int:
        """Parse the annotation of a function definition arg."""

        # Scan the ':'
        self.expect_op(i1, ':')
        self.set_context(i1, 'annotation')
        i = self.next(i1)

        # Scan to the next ',' or '=', ignoring inner parens.
        i3 = self.find_delim(i, end, [',', '=', ')'])
        self.expect_ops(i3, [',', '=', ')'])

        # Set the contexts of inner ops.
        for i4 in range(i1 + 1, i3 - 1):
            if self.is_ops(i4, ['=', ':']):
                self.set_context(i4, 'annotation')
        return i3
    #@+node:ekr.20240106173638.1: *5* tbo.parse_arg
    def parse_arg(self, i1: int, end: int) -> int:
        """Parse a single function definition argument."""

        # Scan optional  * and ** operators.
        i = i1
        if self.is_ops(i, ['*', '**']):
            self.set_context(i1, 'arg')
            i = self.next(i)
            # Handle *,
            if self.is_op(i, ','):
                i = self.next(i)
                return i

        # Scan the argument's name.
        self.expect(i, 'name')
        i = self.next(i)

        # Scan an optional annotation.
        has_annotation = self.is_op(i, ':')
        if has_annotation:
            self.set_context(i, 'annotation')
            i = self.parse_annotation(i, end)

        # Scan an optional initializer.
        if self.is_op(i, '='):
            if has_annotation:
                self.set_context(i, 'annotation')
            else:
                self.set_context(i, 'initializer')
            i = self.parse_initializer(i, end)  ###, has_annotation=has_annotation)

        # Scan the optional comma.
        if self.is_op(i, ','):
            i = self.next(i)
        return i
    #@+node:ekr.20240106172905.1: *5* tbo.parse_args
    def parse_args(self, i1: int, end: int) -> int:
        """
        Parse a comma-separated list of function definition arguments.

        Return the index of ending ')' token.
        """

        # Sanity checks.
        assert i1 < end, (i1, end)
        self.expect_op(i1, '(')
        self.expect_op(end, ')')

        # Scan the '('
        i = self.next(i1)

        # Scan each argument.
        while i < end and not self.is_op(i, ')'):
            progress = i
            i = self.parse_arg(i, end)
            assert progress < i, 'parse_args: no progress!'

        # Scan the ')'
        self.expect_op(i, ')')

        # An important sanity check.
        assert i == end, repr((i, end))
        return i
    #@+node:ekr.20240107092559.1: *5* tbo.parse_call_arg
    def parse_call_arg(self, i1: int, end: int) -> int:
        """
        Scan a single function definition argument.

        Set context for every '=' operator.
        """

        self.trace(i1, tag='before')  ###

        # Handle leading * and ** args.
        if self.is_ops(i1, ['*', '**']):
            self.set_context(i1, 'arg')
            i = self.next(i1)
        else:
            i = i1

        # Step one: scan one argument up to a possible initializer.
        while i < end:
            progress = i
            token = self.tokens[i]
            kind, value = token.kind, token.value

            g.trace(token)  ###

            if kind == 'name':
                _is_complex, i = self.parse_name(i, end)
            elif kind == 'op':
                if value in ',=)':
                    break
                i = self.parse_op(i, end)
            else:
                i = self.next(i)

            assert i is not None, (token)
            assert progress < i, (i, token)

        self.trace(i, tag='after')

        # Step 2. Handle the initializer if present.
        if self.is_op(i, ','):
            i = self.next(i)
        elif self.is_op(i, '='):
            # Handle the initializer, setting context for '='
            self.set_context(i, 'initializer')
            i = self.parse_initializer(i, end)  ###, has_annotation=False)
            self.expect_ops(i, [',', ')'])
            if self.is_op(i, ','):
                i = self.next(i)

        # Set the context.
        ### Should be done in inner contexts!.
        # for i3 in range(i1 + 1, i - 1):
            # if self.is_ops(i3, ['*', '**', '=']):
                # self.set_context(i3, 'arg')  ### Was 'expression'

        return i
    #@+node:ekr.20240107092458.1: *5* tbo.parse_call_args
    def parse_call_args(self, i1: int, end: int) -> int:
        """Scan a comma-separated list of function definition arguments."""

        # Scan the '('
        self.expect_op(i1, '(')

        # Find the matching '('.
        i2 = self.find_close_paren(i1)  # Does not skip the ')'.
        self.expect_op(i2, ')')

        # Scan each argument.
        i = i1 + 1
        while i < i2:  ###  and not self.is_op(i, ')'):
            progress = i
            i = self.parse_call_arg(i, i2)  # Sets context.
            if progress >= i:  # pragma: no cover
                self.oops('parse_call_args: no progress')

        return i2  # Do not skip the ')'.
    #@+node:ekr.20240124012707.1: *5* tbo.parse_name
    def parse_name(self, i: int, end: int) -> tuple[bool, int]:
        """
        Parse a name, including possible function calls.

        Return (is_complex, i)
        """

        self.expect_name(i)

        is_complex = False
        token = self.tokens[i]
        if token.value in self.expression_keywords:
            i = self.next(i)
        else:
            # token.value *can* be in self.keywords. For example, re.match.
            i = self.next(i)
            token = self.tokens[i]
            if i < end:
                if token.value == '(':
                    i = self.parse_call(i, end)
                    is_complex = True
                elif token.value == '[':  ### New.
                    i = self.parse_slice(i, end)
                    is_complex = True
        return is_complex, i
    #@+node:ekr.20240124012746.1: *5* tbo.parse_op ?faux helper?
    def parse_op(self, i: int, end: int) -> int:
        """
        Parse an operator, including grouping operators.

        Return the index of the *following* token.

        """
        if self.is_op(i, '['):
            i = self.parse_slice(i, end)
        elif self.is_op(i, '{'):
            i = self.parse_dict_or_set(i, end)
        elif self.is_op(i, '('):
            i = self.parse_parenthesized_expr(i, end)
        else:
            i = self.next(i)
        return self.next(i)
    #@+node:ekr.20240113054641.1: *5* tbo.parse_statement & statement helpers
    def parse_statement(self, i: int) -> int:
        """
        Scan the next statement, including docstrings.
        """
        # All statements add 'end-statement' context "near" the end of the line:
        # - Simple statements call find_end_of_line.
        # - Compound statements call find_delim(i, len(self.tokens), [':'])
        token = self.tokens[i]
        if token.kind == 'name':
            if token.value == 'from':
                return self.parse_from(i)
            if token.value == 'import':
                return self.parse_import(i)
            if token.value in self.compound_statements:
                return self.parse_compound_statement(i)
            if token.value in self.simple_statements:
                return self.parse_simple_statement(i)
            # An expression.
            return self.parse_outer_expression(i)
        if (token.kind, token.value) == ('op', '@'):
            return self.parse_decorator(i)
        # Ensure progress.
        i = self.next(i)
        return i
    #@+node:ekr.20240107091700.1: *6* tbo.parse_call
    def parse_call(self, i1: int, end: int) -> int:
        """Parse a function call"""

        self.trace(i1, end)  ###

        # Find i1 and i2, the boundaries of the argument list.
        self.expect_op(i1, '(')

        # Scan the arguments.
        i = self.parse_call_args(i1, end)

        # Sanity check.
        self.expect_op(i, ')')
        i = self.next(i)
        return i
    #@+node:ekr.20240115101846.1: *6* tbo.parse_class_or_def
    def parse_class_or_def(self, i: int) -> int:
        """Set context for a class or def statement."""
        self.expect(i, 'name')  # The 'class' or 'def' keyword.
        token = self.tokens[i]
        keyword_value = token.value
        assert keyword_value in ('class', 'def'), f"Expecting 'class' or 'def'. Got {token!r}"

        # Scan the define name of the 'class' or 'def'.
        i = self.next(i)
        self.expect(i, 'name')

        # The defined name is *not* a function call.
        self.set_context(i, 'class/def')

        # Caller will handle the rest of the 'class' statement.
        if keyword_value == 'class':
            # Find the trailing ':'!
            i = self.find_delim(i, len(self.tokens), [':'])
            self.expect_op(i, ':')

            # Set the context.
            self.set_context(i, 'end-statement')

            # Move past the ':' token.
            return self.next(i)

        # Handle the rest of the 'def' statement.

        # Find the '(' and ')' tokens.
        i = self.next(i)
        self.expect_op(i, '(')
        i1 = i
        i2 = self.find_close_paren(i)  # Does not skip the ')'.
        self.expect_op(i2, ')')

        # Scan the arguments, setting context.
        i = self.parse_args(i1, i2)

        # Set the context of the trailing ':' token.
        i = self.find_delim(i, len(self.tokens), [':'])
        self.expect_op(i, ':')
        self.set_context(i, 'end-statement')

        # Move past the ':' token.
        return self.next(i)
    #@+node:ekr.20240108062349.1: *6* tbo.parse_compound_statement
    def parse_compound_statement(self, i: int) -> int:
        """
        Scan a compound statement, adding 'end-statement' context to the
        trailing ':' token.
        """

        # Scan the keyword.
        self.expect(i, 'name')

        # Special case for 'async':
        keyword = self.tokens[i].value
        if keyword not in self.compound_statements:  # pragma: no cover
            self.oops(f"Not a compound keyword: {keyword!r}")

        if keyword == 'async':
            i = self.next(i)
            keyword = self.tokens[i].value

        if keyword in ('class', 'def'):
            return self.parse_class_or_def(i)

        # Skip the keyword.
        i = self.next(i)

        # Find the trailing ':' and set the context.
        end = self.find_delim(i, len(self.tokens), [':'])
        self.expect_op(end, ':')
        self.set_context(end, 'end-statement')

        # A harmless hack: treat the rest of the statement as an expression.
        self.parse_expr(i, end)

        # Scan the ':'.
        return self.next(end)
    #@+node:ekr.20240115074103.1: *6* tbo.parse_decorator
    def parse_decorator(self, i: int) -> int:

        # Scan the @
        self.expect_op(i, '@')
        i = self.next(i)

        # Scan the name.
        self.expect(i, 'name')
        i = self.next(i)

        # Set context for any arguments as if they were call arguments.
        if self.is_op(i, '('):
            i = self.parse_call_args(i, len(self.tokens))
            self.expect_op(i, ')')
            i = self.next(i)
        return i

    #@+node:ekr.20240120202324.1: *6* tbo.parse_expr & helpers
    def parse_expr(self, i: int, end: int) -> int:
        """
        Parse an expression spanning self.tokens[i:end],
        looking for the following token patterns:

        - A function call:  'name', '(', ..., ')'.
        - A slice:          '[', ..., ']'.
        - A dictionary:     '{', ..., '}'.

        Set the appropriate context for all inner expressions.
        """

        self.trace(i, end)  ###

        # Scan an arbitrary expression, bounded only by end.
        while i < end:
            progress = i
            token = self.tokens[i]
            kind, value = token.kind, token.value

            if kind == 'name':
                _is_complex, i = self.parse_name(i, end)
            elif kind == 'op':
                ### This is the same as parse_op!
                if value == '(':
                    i = self.parse_parenthesized_expr(i, end)
                elif value == '[':
                    i = self.parse_slice(i, end)
                elif value == '{':
                    i = self.parse_dict_or_set(i, end)
                else:
                    i = self.next(i)
            else:
                i = self.next(i)

            assert i is not None, token
            assert progress < i, (i, token)
        return end
    #@+node:ekr.20240121073127.1: *7* tbo.parse_dict_or_set
    def parse_dict_or_set(self, i1: int, end: int) -> int:
        """
        Parse a '{', ..., '}'.

        Set context for '=' tokens to 'dict' only within dictionaries.
        """

        # Scan the '{'.
        self.expect_op(i1, '{')

        # Find the matching '}'
        i = self.next(i1)
        i2 = self.find_delim(i, end, ['}'])
        self.expect_op(i2, '}')

        # Sanity check.
        assert i2 <= end, (repr(i2), repr(end))

        # Search for ':' at the top level.
        colon_i = self.find_delim(i, i2, [':'])
        if colon_i is None:
            # The opening '{' starts a non-empty set.
            # Note: the Tokenizer converts all f-strings tokens to a single 'string' token.
            pass
        else:
            # The opening '{' starts a non-empty dict.
            self.parse_dict(i1, i2)
        return self.next(i2)
    #@+node:ekr.20240121073925.1: *7* tbo.parse_dict
    def parse_dict(self, i1: int, end: int) -> None:
        """
        Parse '[', ..., ']'.

        Set the context of all outer-level ':' tokens to 'dict'.

        Return None.
        """

        # Initial sanity checks.
        self.expect_op(i1, '{')
        self.expect_op(end, '}')

        # Set context for all outer-level ':' tokens to 'dict'.
        i = self.next(i1)
        while i < end:
            i = self.find_delim(i, end, [':'])
            if i is None:
                break
            self.set_context(i, 'dict')
            i = self.next(i)
    #@+node:ekr.20240121071949.1: *7* tbo.parse_parenthesized_expr ** faux helper?
    def parse_parenthesized_expr(self, i: int, end: int) -> int:
        """
        Parse a parenthesized expression.

        Such expressions have no context.
        """
        # Scan the '('.
        self.expect_op(i, '(')

        # Find the matching ')'.
        i = self.next(i)
        i2 = self.find_delim(i, end, [')'])
        self.expect_op(i2, ')')

        ### Experimental.
        self.parse_expr(i + 1, i2 - 1)

        # Sanity check.
        assert i2 <= end, (repr(i2), repr(end))
        return i2
    #@+node:ekr.20240121024213.1: *7* tbo.parse_slice (TEST)
    def parse_slice(self, i1: int, end: int) -> int:
        """
        Parse '[', ..., ']'.

        Set the context for ':' tokens to 'simple-slice' or 'complex-slice'.
        """

        self.trace(i1, end)  ###

        # Scan the '['.
        self.expect_op(i1, '[')
        i = self.next(i1)

        i2 = self.find_delim(i, end, [']'])
        self.expect_op(i2, ']')
        assert i2 <= end, (repr(i2), repr(end))

        # Context data.
        colons: list[int] = []  # List of outer ':' to be given context.
        final_context: str = 'simple-slice'  # May become 'complex-slice'.
        inter_colon_tokens = 0

        def update_context(i: int) -> None:
            nonlocal colons, final_context, inter_colon_tokens

            # Ignore '.' tokens and the preceding 'name' token.
            if self.is_op(i, '.'):
                prev = self.prev(i)
                if self.is_name(prev):
                    inter_colon_tokens -= 1
                return

            # *Now* we can update the effective complexity of the slice.
            inter_colon_tokens += 1
            if inter_colon_tokens > 1:
                final_context = 'complex-slice'

        # Parse the slice to discover possible inner function calls!
        while i <= i2:  # Required.
            progress = i
            token = self.tokens[i]
            kind, value = token.kind, token.value

            if kind == 'name':
                is_complex, i = self.parse_name(i, end)
                if is_complex:
                    final_context = 'complex-slice'
            elif kind == 'op':
                if value == ']':
                    # An outer ']'
                    i = self.next(i)
                    break
                if value == ':':
                    # An outer ':'.
                    colons.append(i)
                    inter_colon_tokens = 0
                    i = self.next(i)
                elif value in '+-':
                    # Don't update context for unary ops.
                    if not self.is_unary_op(i, value):
                        update_context(i)
                    i = self.next(i)
                elif value == '(':
                    i = self.parse_parenthesized_expr(i, end)
                    final_context = 'complex-slice'
                elif value == '[':
                    i = self.parse_slice(i, end)
                    final_context = 'complex-slice'
                elif value == '{':
                    i = self.parse_dict_or_set(i, end)
                    final_context = 'complex-slice'
                else:
                    update_context(i)
                    i = self.next(i)
            else:
                i = self.next(i)

            assert i is not None, (token)
            assert progress < i, (i, token)

        # Set the context of all outer-level ':' tokens.
        for colon_i in colons:
            self.set_context(colon_i, final_context)

        return self.next(i2)  # Ignore i.

        ###

            # while i < i2:  # Don't scan the ']' token again.
                # progress = i
                # token = self.tokens[i]
                # value = token.value
                # if token.kind == 'op':
                    # if value == ':':
                        # colons.append(i)
                        # inter_colon_tokens = 0
                        # i = self.next(i)
                    # elif value in '+-':
                        # # Don't update context for unary ops.
                        # if not self.is_unary_op(i, value):
                            # update_context(i)
                        # i = self.next(i)
                    # elif value == '(':
                        # i = self.parse_parenthesized_expr(i, end)
                        # final_context = 'complex-slice'
                    # elif value == '[':
                        # i = self.parse_slice(i, end)
                        # final_context = 'complex-slice'
                    # elif value == '{':
                        # i = self.parse_dict_or_set(i, end)
                        # final_context = 'complex-slice'
                    # else:
                        # update_context(i)
                        # i = self.next(i)
                # else:
                    # update_context(i)
                    # i = self.next(i)
                # assert progress < i, (token.kind, value)

                # # Set the context of all outer-level ':' tokens.
                # for colon_i in colons:
                    # self.set_context(colon_i, final_context)

                # # Ignore i.
                # return self.next(i2)
    #@+node:ekr.20240107143500.1: *6* tbo.parse_from
    def parse_from(self, i: int) -> int:
        """
        Parse a `from x import` statement, setting context for leading '.'
        tokens.
        """
        # Find the end of the 'from' statement.
        i = self.index
        end = self.find_end_of_line(i)

        # Add 'from' context to all '.' tokens.
        while i and i < end:
            if self.is_op(i, '.'):
                self.set_context(i, 'from')
            i = self.next(i)

        return end
    #@+node:ekr.20240108083829.1: *6* tbo.parse_import
    def parse_import(self, i: int) -> int:
        # Find the end of the import statement.
        i = self.index
        end = self.find_end_of_line(i)

        # Add 'import' context to all '.' operators.
        while i and i < end:
            if self.is_op(i, '.'):
                self.set_context(i, 'import')
            i = self.next(i)
        return end
    #@+node:ekr.20240106181215.1: *6* tbo.parse_initializer
    def parse_initializer(self, i1: int, end: int) -> int:
        """
        Scan an initializer in a function call or function definition argument.
        """

        self.trace(i1)  ###

        # Scan the '='.
        self.expect_op(i1, '=')

        # Sanity check.
        context = self.tokens[i1].context
        assert context in ('initializer', 'annotation'), repr(context)

        i = self.next(i1)

        # Scan an arbitrary expression, separated by ',' or ')'.
        while i <= end:  ### was '<'
            progress = i
            token = self.tokens[i]
            kind, value = token.kind, token.value

            if kind == 'name':
                _is_complex, i = self.parse_name(i, end)
            elif kind == 'op':
                if value in ',)':
                    break
                i = self.parse_op(i, end)
            else:
                i = self.next(i)

            assert i is not None, token
            assert progress < i, (i, token)

        # Same expect as in the caller.
        self.expect_ops(i, [',', ')'])
        return i
    #@+node:ekr.20240116040636.1: *6* tbo.parse_outer_expression
    def parse_outer_expression(self, i1: int) -> int:
        #@+<< docstring: tbo.parse_outer_expression >>
        #@+node:ekr.20240120201047.1: *7* << docstring: tbo.parse_outer_expression >>
        """
        Parse a line that *isn't* a simple or compound statement.
        See https://docs.python.org/3/reference/expressions.html

        This method's only purpose is to mark the context of '=' and ':'
        tokens. It can ignore unrelated subtleties of Python's grammar.

        1. If the next significant token is a string, just scan it.

        2. Otherwise, we are looking *only* for the following token patterns:

        - A function call:  'name', '(', ... ')'.
        - A slice:          '[', <expr>? ':' <expr> ':'? <expr>? ']'.
        - A dictionary:     '{', <expr> ':' <expr> '}'.

        Notes:

        1. <expr> denotes an inner expression.
        2. ? denotes optional tokens or expressions.
        3. '=' tokens within function calls always have 'initializer' context.
        """
        #@-<< docstring: tbo.parse_outer_expression >>

        token = self.tokens[i1]
        assert self.is_significant_token(token), (token, g.callers())

        # Just scan outer strings and f-strings at the outer level.
        if token.kind in self.string_kinds:
            return self.next(i1)

        # Find the bounds of the expression.
        # This prepass simplifies all the inner logic.

        # Because expressions are scanned twice the token_ratio in
        # the top-level orange_command should be > 2.0.

        end = self.find_end_of_line(i1)
        i = self.parse_expr(i1, end)
        return i
    #@+node:ekr.20240109032639.1: *6* tbo.parse_simple_statement
    def parse_simple_statement(self, i: int) -> int:
        """
        Scan to the end of a simple statement like an `import` statement.
        """

        # Sanity check.
        self.expect_name(i)
        end = self.find_end_of_line(i)
        token = self.get_token(end)
        assert token.context == 'end-statement'

        # Treat the rest of the *statement* as an expression.
        i2 = self.next(i)
        self.parse_expr(i2, end)
        return end
    #@+node:ekr.20240113054629.1: *5* tbo.parse_statements (top-level of parser)
    def parse_statements(self) -> None:
        """
        parse_statements: scan (parse) the entire file.

        This is the entry point for a "good enough" recursive-descent
        parser who's *only* purpose is to add context to a few kinds
        of tokens.  See set_context for details.
        """
        i = self.index
        assert i == 0, repr(i)

        # Skip the encoding token.
        i = self.next(i)
        while i is not None:
            # Set the 'index' and 'token' ivars for each statement.
            self.index = i
            self.token = self.tokens[i]

            # Parse the statement.
            i = self.parse_statement(i)
    #@+node:ekr.20240110205127.1: *4* tbo: Scanning
    # The parser calls scanner methods to move through the list of input tokens.
    #@+node:ekr.20240114022135.1: *5* tbo.find_close_paren
    def find_close_paren(self, i1: int) -> Optional[int]:
        """Find the  ')' matching this '(' token."""

        self.expect_op(i1, '(')
        i = self.next(i1)
        level = 0
        while i < len(self.tokens):
            if self.is_op(i, '('):
                level += 1
            elif self.is_op(i, ')'):
                if level == 0:
                    return i
                if level <= 0:
                    self.oops(f"Unbalanced parens: {self.token.line!r}")  # pragma: no cover
                level -= 1
            i = self.next(i)
        self.oops("Unmatched '('")  # pragma: no cover
        return None  # pragma: no cover
    #@+node:ekr.20240114063347.1: *5* tbo.find_delim
    def find_delim(self, i1: int, end: int, delims: list) -> int:
        """
        Find the next delimiter token, skipping inner expressions.
        Return None if not found. It's not necessarily an error.

        The *caller* is responsible for scanning an opening '(', '[', or '{'
        token when the delims list contains ')', ']', or '}'.

        The *caller* is responsible for scanning the token at the returned index.
        """
        trace = False  ###
        if trace:  # pragma: no cover
            g.trace(f" {i1:3} {g.callers(1):25} {delims} {self.get_token_line(i1)}")

        # We expect only the following 'op' delims: ',', '=', ')' and ':'.
        for z in delims:
            if z not in ',=)}]:':
                self.oops(f"Invalid delim: {z!r}")  # pragma: no cover

        # Skip tokens until one of the delims is found.
        i = i1
        while i <= end:  # '<=' is required.
            token = self.tokens[i]
            if token.kind == 'op':
                value = token.value
                if value in delims:
                    if trace:  ### pragma: no cover
                        token = self.tokens[i]
                        token_s = f"{token.kind:} {token.value!r}"
                        g.trace(f" {i:3} Returns {token_s}\n")
                    return i
                if value == '[':
                    i = self.skip_past_matching_delim(i, '[', ']')
                elif value == '(':
                    i = self.skip_past_matching_delim(i, '(', ')')
                elif value == '{':
                    i = self.skip_past_matching_delim(i, '{', '}')
                else:
                    i = self.next(i)
            else:
                i = self.next(i)
        return None
    #@+node:ekr.20240110062055.1: *5* tbo.find_end_of_line
    def find_end_of_line(self, i: int) -> Optional[int]:
        """
        Return the index the next 'newline', 'nl' or 'endmarker' token,
        skipping inner expressions.

        Set the context of found token to 'end-statement.
        Do *not* set the context of any other token.
        """
        while i < len(self.tokens):
            token = self.tokens[i]
            if token.kind in ('newline', 'nl', 'endmarker'):
                self.set_context(i, 'end-statement')
                return i
            if token.kind == 'op':
                value = token.value
                if value == '[':
                    i = self.skip_past_matching_delim(i, '[', ']')
                elif value == '(':
                    i = self.skip_past_matching_delim(i, '(', ')')
                elif value == '{':
                    i = self.skip_past_matching_delim(i, '{', '}')
                else:
                    i = self.next(i)
            else:
                i = self.next(i)
        self.oops("no matching ')'")  # pragma: no cover
        return len(self.tokens)  # pragma: no cover
    #@+node:ekr.20240106172054.1: *5* tbo.is_op & is_ops
    def is_op(self, i: int, value: str) -> bool:

        if i is None:  # pragma: no cover
            return False
        token = self.tokens[i]
        return token.kind == 'op' and token.value == value

    def is_ops(self, i: int, values: list[str]) -> bool:

        if i is None:  # pragma: no cover
            return False
        token = self.tokens[i]
        return token.kind == 'op' and token.value in values
    #@+node:ekr.20240125082325.1: *5* tbo.is_name
    def is_name(self, i: int) -> bool:

        if i is None:  # pragma: no cover
            return False
        token = self.tokens[i]
        return token.kind == 'name'
    #@+node:ekr.20240106093210.1: *5* tbo.is_significant_token
    def is_significant_token(self, token: InputToken) -> bool:
        """Return true if the given token is not whitespace."""
        return token.kind not in (
            'comment', 'dedent', 'indent', 'newline', 'nl', 'ws',
        )
    #@+node:ekr.20240105145241.43: *5* tbo.next
    def next(self, i: int) -> Optional[int]:
        """
        Return the next *significant* token in the list of *input* tokens.

        Ignore whitespace, indentation, comments, etc.

        The **Global Token Ratio** is tbo.n_scanned_tokens / len(tbo.tokens),
        where tbo.n_scanned_tokens is the total number of calls calls to
        tbo.next or tbo.prev.

        For Leo's sources, this ratio ranges between 0.48 and 1.51!

        The orange_command function warns if this ratio is greater than 2.5.
        Previous versions of this code suffered much higher ratios.
        """
        i += 1
        while i < len(self.tokens):
            self.n_scanned_tokens += 1
            token = self.tokens[i]
            if self.is_significant_token(token):
                return i
            i += 1
        return None
    #@+node:ekr.20240115233050.1: *5* tbo.prev
    def prev(self, i: int) -> Optional[int]:
        """
        Return the previous *significant* token in the list of *input* tokens.

        Ignore whitespace, indentation, comments, etc.
        """
        i -= 1
        while i >= 0:
            self.n_scanned_tokens += 1
            token = self.tokens[i]
            if self.is_significant_token(token):
                return i
            i -= 1
        return None  # pragma: no cover
    #@+node:ekr.20240106170746.1: *5* tbo.set_context
    def set_context(self, i: int, context: str) -> None:
        #@+<< docstring: set_context >>
        #@+node:ekr.20240124030354.1: *6* << docstring: set_context >>
        """
        Set self.tokens[i].context, but only if it does not already exist!

        As a result, the order of scanning tokens in the parser matters!

        Here is a table of tokens and the contexts they may have:

        Token       Possible Contexts
        =====       =================
        ':'         'annotation', 'dict', 'end-statement'
                    'complex-slice', 'simple-slice'
        '='         'annotation', 'expression', 'initializer'
        '*', '**'   'arg', 'expression'
        '.'         'from', 'import'
        '{', '}'    'dict'  (denotes that the dict has been scanned).
        '[', ']     'array' (denotes that the array has been scanned).
        'name'      'class/def'
        'newline'   'end-statement'
        'nl'        'end-statement'
        """
        #@-<< docstring: set_context >>

        trace = False  # Do not delete the trace below.

        valid_contexts = (
            'annotation', 'array', 'arg', 'class/def', 'complex-slice',
            'dict', 'end-statement', 'expression', 'from', 'import',
            'initializer', 'simple-slice',
        )
        if context not in valid_contexts:
            self.oops(f"Unexpected context! {context!r}")  # pragma: no cover

        token = self.tokens[i]

        if trace:  # pragma: no cover
            token_s = f"{token.kind}: {token.value!r}"
            ignore_s = 'Ignore' if token.context else ' ' * 6
            g.trace(f"{i:3} {g.callers(1):25} {ignore_s} {token_s:20} {context}")

        if not token.context:
            token.context = context
    #@+node:ekr.20240115072231.1: *5* tbo.skip_past_matching_delim
    def skip_past_matching_delim(self, i: int, delim1: str, delim2: str) -> int:
        """
        Skip from delim1 *past* the matching delim2.
        Raise InternalBeautifierError if a matching delim2 is not found.
        """
        self.expect_op(i, delim1)
        i = self.next(i)
        while i < len(self.tokens):
            progress = i
            token = self.tokens[i]
            if token.kind == 'op':
                value = token.value
                if value == delim2:
                    return i + 1  # Skip the closing delim
                if value == '[':
                    i = self.skip_past_matching_delim(i, '[', ']')
                elif value == '(':
                    i = self.skip_past_matching_delim(i, '(', ')')
                elif value == '{':
                    i = self.skip_past_matching_delim(i, '{', '}')
                else:
                    i = self.next(i)
            else:
                i = self.next(i)
            if progress >= i:
                self.oops('no progress!')
        self.oops(f"no matching {delim2!r}")  # pragma: no cover
        return None  # pragma: no cover
    #@-others
#@+node:ekr.20240105140814.121: ** function: main & helpers (leoTokens.py)
def main() -> None:  # pragma: no cover
    """Run commands specified by sys.argv."""
    args, settings_dict, arg_files = scan_args()
    cwd = os.getcwd()

    # Calculate requested files.
    t1 = time.process_time()
    requested_files: list[str] = []
    for path in arg_files:
        if path.endswith('.py'):
            requested_files.append(os.path.join(cwd, path))
        else:
            root_dir = os.path.join(cwd, path)
            requested_files.extend(
                glob.glob(f'{root_dir}**{os.sep}*.py', recursive=True)
            )
    if not requested_files:
        print(f"No files in {arg_files!r}")
        return

    # Calculate the actual list of files.
    files: list[str]
    if args.force:
        # Handle all requested files.
        files = requested_files
    else:
        # Handle only modified files.
        modified_files = get_modified_files(cwd)
        files = [
            z for z in requested_files if os.path.abspath(z) in modified_files
        ]
    if not files:
        return

    # Do the command.
    t2 = time.process_time()
    if 0:  # Negligible.
        print(f"files: {len(files)} setup time: {t2-t1:3.1f} sec.")
    if args.o:
        orange_command(arg_files, files, settings_dict)
    # if args.od:
        # orange_diff_command(files, settings_dict)
#@+node:ekr.20240105140814.9: *3* function: get_modified_files
def get_modified_files(repo_path: str) -> list[str]:  # pragma: no cover
    """Return the modified files in the given repo."""
    if not repo_path:
        return []
    old_cwd = os.getcwd()
    os.chdir(repo_path)
    try:
        # We are not checking the return code here, so:
        # pylint: disable=subprocess-run-check
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True)
        if result.returncode != 0:
            print("Error running git command")
            return []
        modified_files = []
        for line in result.stdout.split('\n'):
            if line.startswith((' M', 'M ', 'A ', ' A')):
                modified_files.append(line[3:])
        return [os.path.abspath(z) for z in modified_files]
    finally:
        os.chdir(old_cwd)
#@+node:ekr.20240105140814.10: *3* function: scan_args (leoTokens.py)
def scan_args() -> tuple[Any, dict[str, Any], list[str]]:  # pragma: no cover
    description = textwrap.dedent("""\
        Execute fstringify or beautify commands contained in leoAst.py.
    """)
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('PATHS', nargs='*', help='directory or list of files')
    # Don't require any args.
    group = parser.add_mutually_exclusive_group(required=False)
    add = group.add_argument
    add2 = parser.add_argument

    # Commands.
    add('--orange', dest='o', action='store_true',
        help='beautify PATHS')

    # Unused commands...
        # add('--fstringify', dest='f', action='store_true',
            # help='fstringify PATHS')
        # add('--fstringify-diff', dest='fd', action='store_true',
            # help='fstringify diff PATHS')
        # add('--orange-diff', dest='od', action='store_true',
            # help='diff beautify PATHS')

    # Arguments.
    add2('--diff', dest='diff', action='store_true',
        help='show diffs instead of changing files')
    add2('--force', dest='force', action='store_true',
        help='force beautification of all files')
    add2('--silent', dest='silent', action='store_true',
        help="don't list changed files")
    add2('--verbose', dest='verbose', action='store_true',
        help='verbose (per-file) output')

    # Unused arguments..
        # add2('--allow-joined', dest='allow_joined', action='store_true',
            # help='allow joined strings')
        # add2('--max-join', dest='max_join', metavar='N', type=int,
            # help='max unsplit line length (default 0)')
        # add2('--max-split', dest='max_split', metavar='N', type=int,
            # help='max unjoined line length (default 0)')
        # add2('--tab-width', dest='tab_width', metavar='N', type=int,
            # help='tab-width (default -4)')

    # Create the return values, using EKR's prefs as the defaults.
    parser.set_defaults(
        diff=False,
        force=False,
        silent=False,
        recursive=False,
        tab_width=4,
        verbose=False
        # allow_joined=False, max_join=0, max_split=0,
    )
    args: Any = parser.parse_args()
    files = args.PATHS
    # Create the settings dict, ensuring proper values.
    settings_dict: dict[str, Any] = {
        'diff': bool(args.diff),
        'force': bool(args.force),
        'tab_width': abs(args.tab_width),  # Must be positive!
        'silent': bool(args.silent),
        'verbose': bool(args.verbose),
        # 'allow_joined_strings': bool(args.allow_joined),
        # 'max_join_line_length': abs(args.max_join),
        # 'max_split_line_length': abs(args.max_split),
    }
    return args, settings_dict, files
#@-others

if __name__ == '__main__':
    main()  # pragma: no cover

#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
