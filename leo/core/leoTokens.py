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
import glob
import keyword
import io
import os
import re
import subprocess
import sys
import textwrap
import time
import tokenize
import traceback
from typing import Any, Callable, Generator, Optional, Union

try:
    from leo.core import leoGlobals as g
except Exception:
    # check_g function gives the message.
    g = None

Node = ast.AST
Settings = Optional[dict[str, Any]]
#@-<< leoTokens.py: imports & annotations >>

debug: bool = True

#@+others
#@+node:ekr.20240105140814.5: ** command: orange_command (tbo) & helper
def orange_command(
    arg_files: list[str],
    files: list[str],
    settings: Settings = None,
    verbose: bool = False,
) -> None:  # pragma: no cover
    """The outer level of the 'tbo/orange' command."""
    if not check_g():
        return
    global gBeautifier
    t1 = time.process_time()
    for filename in files:
        if os.path.exists(filename):
            # print(f"orange {filename}")
            tbo = TokenBasedOrange(settings)
            gBeautifier = tbo
            tbo.beautify_file(filename)
        else:
            print(f"file not found: {filename}")
    # Report the results.
    t2 = time.process_time()
    print(f"tbo: {t2-t1:3.1f} sec. {len(files):3} files in {','.join(arg_files)}")
#@+node:ekr.20240105140814.8: *3* function: check_g
def check_g() -> bool:
    """print an error message if g is None"""
    if not g:
        print('This statement failed: `from leo.core import leoGlobals as g`')
        print('Please adjust your Python path accordingly')
    return bool(g)
#@+node:ekr.20240114011303.1: ** LeoTokens: alias functions
# These functions are aliases for helper methods of the TokenBasedOrange class.
# The declutter the code.

def expect(i: int, kind: str, value: str = None) -> None:
    gBeautifier.expect(i, kind, value)

def expect_op(i: int, value: str) -> None:
    gBeautifier.expect_op(i, value)

def expect_ops(i: int, values: list) -> None:
    gBeautifier.expect_ops(i, values)

def is_kind(i: int, kind: str) -> bool:
    return gBeautifier.is_kind(i, kind)

def is_op(i: int, value: str) -> bool:
    return g.Beautifier.is_op(i, value)

def is_ops(i: int, values: list[str]) -> bool:
    return g.Beautifier.is_ops(i, values)

def next(i: int) -> Optional[int]:
    return g.Beautifier.next_token(i)

def set_context(i: int, context: str) -> None:
    g.Beautifier.set_context(i, context)
#@+node:ekr.20240106220602.1: ** LeoTokens: debugging functions
#@+node:ekr.20240105140814.41: *3* function: dump_contents
def dump_contents(contents: str, tag: str = 'Contents') -> None:
    print('')
    print(f"{tag}...\n")
    for i, z in enumerate(g.splitLines(contents)):
        print(f"{i+1:<3} ", z.rstrip())
    print('')
#@+node:ekr.20240105140814.42: *3* function: dump_lines
def dump_lines(tokens: list[InputToken], tag: str = 'lines') -> None:
    print('')
    print(f"{tag}...\n")
    for z in tokens:
        if z.line.strip():
            print(z.line.rstrip())
        else:
            print(repr(z.line))
    print('')
#@+node:ekr.20240105140814.43: *3* function: dump_results
def dump_results(tokens: list[OutputToken], tag: str = 'Results') -> None:
    print('')
    print(f"{tag}...\n")
    print(output_tokens_to_string(tokens))
    print('')
#@+node:ekr.20240105140814.44: *3* function: dump_tokens
def dump_tokens(tokens: list[InputToken], tag: str = 'Tokens') -> None:
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
def input_tokens_to_string(tokens: list[InputToken]) -> str:
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
    if tokens is None:
        # This indicates an internal error.
        print('')
        g.trace('===== output token list is None ===== ')
        print('')
        return ''
    return ''.join([z.to_string() for z in tokens])
#@+node:ekr.20240105140814.52: ** Classes
#@+node:ekr.20240105140814.51: *3* class BeautifyError(Exception)
class BeautifyError(Exception):
    """Any error in the beautifier."""
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
        s = f"{self.index:<3} {self.kind:}"
        return f"Token {s}: {self.show_val(20)}"

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
    def show_val(self, truncate_n: int = 20) -> str:  # pragma: no cover
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
        'last_offset', 'lines',
        'offsets', 'prev_offset',
        'token_index', 'token_list',
    )

    def __init__(self) -> None:
        # self.token_index = 0
        # # The computed list of input tokens.
        # self.token_list: list[InputToken] = []
        # self.last_offset = 0
        # self.offsets: list[int] = [0]
         # Init all ivars.
        self.offsets: list[int] = [0]  # Index of start of each line.
        self.prev_offset = -1
        self.token_index = 0
        self.token_list: list[InputToken] = []

    #@+others
    #@+node:ekr.20240105143307.2: *4* itok.add_token
    def add_token(self, kind: str, line: str, line_number: int, value: str,) -> None:
        """Add an InputToken to the token list."""
        tok = InputToken(kind, value, self.token_index, line, line_number)
        self.token_index += 1
        self.token_list.append(tok)
    #@+node:ekr.20240105143214.2: *4* itok.check_results
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
    #@+node:ekr.20240105143214.3: *4* itok.check_round_trip
    def check_round_trip(self, contents: str, tokens: list[InputToken]) -> bool:
        result = self.tokens_to_string(tokens)
        ok = result == contents
        if not ok:
            print('\nRound-trip check FAILS')
            print('Contents...\n')
            g.printObj(contents)
            print('\nResult...\n')
            g.printObj(result)
        return ok
    #@+node:ekr.20240105143214.4: *4* itok.create_input_tokens
    def create_input_tokens(
        self,
        contents: str,
        five_tuples: Generator,
    ) -> list[InputToken]:
        """
        InputTokenizer.create_input_tokens.

        Return list of InputToken's from tokens, a list of 5-tuples.
        """
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
    #@+node:ekr.20240105143214.5: *4* itok.do_token (the gem)
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
    #@+node:ekr.20240105143214.6: *4* itok.make_input_tokens (entry)
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
        except Exception:
            print('make_tokens: exception in tokenize.tokenize')
            g.es_exception()
            return None
        tokens = self.create_input_tokens(contents, five_tuples)
        if debug:  # True: 2.9 sec. False: 2.8 sec.
            assert self.check_round_trip(contents, tokens)
        return tokens
    #@+node:ekr.20240105143214.7: *4* itok.tokens_to_string
    def tokens_to_string(self, tokens: list[InputToken]) -> str:
        """Return the string represented by the list of tokens."""
        if tokens is None:
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
    """
    Leo's token-based beautifier.
    
    This class is simpler and faster than the Orange class in leoAst.py.
    """
    #@+<< TokenBasedOrange: __slots__ >>
    #@+node:ekr.20240111035404.1: *4* << TokenBasedOrange: __slots__ >>
    __slots__ = [
        # Command-line arguments.
        'force', 'silent', 'tab_width', 'verbose',
        # Debugging.
        'contents', 'filename',
        # Global data.
        'code_list', 'line_indices', 'tokens', 'word_dispatch',
        # Token-related data for visitors.
        'index', 'line_start', 'line_number', 'token',  # 'line_end'
        # Parsing state for visitors.
        'decorator_seen', 'in_arg_list', 'in_doc_part', 'in_fstring',
        'state_stack', 'verbatim',
        # State data for whitespace visitors.
        # Don't even *think* about changing these!
        'curly_brackets_level', 'paren_level', 'square_brackets_stack',
        'indent_level', 'lws',
    ]
    #@-<< TokenBasedOrange: __slots__ >>
    #@+<< TokenBasedOrange: constants >>
    #@+node:ekr.20240108065205.1: *4* << TokenBasedOrange: constants >>
    # Values of operator InputToken that require context assistance.
    # context_op_values: list[str] = [':', '*', '**', '-']

    compound_statements = ('elif', 'else', 'for', 'if', 'while')
    operator_keywords = ('and', 'in', 'not', 'not in', 'or')
    #@-<< TokenBasedOrange: constants >>
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

    #@+others
    #@+node:ekr.20240105145241.2: *4* tbo.ctor
    def __init__(self, settings: Settings = None):
        """Ctor for Orange class."""
        # Set g.Beautifier for the alias functions.
        g.Beautifier = self

        # Set default settings.
        if settings is None:
            settings = {}
        self.force = False
        self.silent = False
        self.tab_width = 4
        self.verbose = False

        # Override defaults from settings dict.
        valid_keys = ('force', 'orange', 'silent', 'tab_width', 'verbose')
        for key in settings:  # pragma: no cover
            value = settings.get(key)
            if key in valid_keys and value is not None:
                setattr(self, key, value)
            else:
                g.trace(f"Unexpected setting: {key} = {value!r}")
                g.trace('(TokenBasedOrange)', g.callers())

        # Init the dispatch dict for 'word' generator.
        self.word_dispatch: dict[str, Callable] = {
            'from': self.scan_from,
            'def': self.scan_def,
            'import': self.scan_import,
        }
        for z in self.compound_statements:
            self.word_dispatch[z] = self.scan_compound_statement
    #@+node:ekr.20240105145241.4: *4* tbo: Entries & helpers
    #@+node:ekr.20240105145241.5: *5* tbo.beautify (main token loop)
    def oops(self) -> None:  # pragma: no cover
        g.trace(f"Unknown kind: {self.token.kind!r}")

    def beautify(self,
        contents: str,
        filename: str,
        tokens: list[InputToken],
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

        # The input and output lists...
        self.code_list: list[OutputToken] = []  # The list of output tokens.
        self.tokens = tokens  # The list of input tokens.

        # The indices of the first/last tokens of the line.
        self.line_start: int = None  # The index of first token of this line.
        ### self.line_end: int = None  # The index of the last token of this line.
        self.line_number: int = None  # The line number of this line.

        # State vars for whitespace.
        self.curly_brackets_level = 0  # Number of unmatched '{' tokens.
        self.paren_level = 0  # Number of unmatched '(' tokens.
        self.square_brackets_stack: list[bool] = []  # A stack of bools, for self.gen_word().
        self.indent_level = 0  # Set only by do_indent and do_dedent.

        # Parse state.
        self.decorator_seen = False  # Set by do_name for do_op.
        self.in_arg_list = 0  # > 0 if in an arg list of a def.
        self.in_doc_part = False
        self.in_fstring = False  # True: scanning an f-string.
        self.state_stack: list["ParseState"] = []  # Stack of ParseState objects.

        # Leo-related state.
        self.verbatim = False  # True: don't beautify.

        # Ivars describing the present input token...
        self.index = 0  # The index within the tokens array of the token being scanned.
        self.lws = ''  # Leading whitespace. Required!
        self.token: InputToken = None

        # Log.
        if self.verbose:
            sfn = filename if '__init__' in filename else g.shortFileName(filename)
            print(f"tbo: {sfn}")
        #@-<< tbo.beautify: init ivars >>

        # Create per-line range data.
        if 0:
            self.line_indices: list[int] = self.create_indices(tokens)

        # The top level of a "good enough" recursive descent parser.
        # Create per-statement range data and per-token context data.
        self.scan_statements()

        # The main loop:
        self.gen_token('file-start', '')
        self.push_state('file-start')
        prev_line_number: int = None
        try:
            for self.index, self.token in enumerate(tokens):
                # Set global for visitors.
                if prev_line_number != self.token.line_number:
                    self.line_start = self.token.line_number
                    prev_line_number = self.token.line_number
                # Call the proper visitor.
                if self.verbatim:
                    self.do_verbatim()
                elif self.in_fstring:
                    self.continue_fstring()
                else:
                    func = getattr(self, f"do_{self.token.kind}", self.oops)
                    func()
            # Any post pass would go here.
            result = output_tokens_to_string(self.code_list)
            return result
        # We can assume the incoming file is syntactically correct!
        # Catching all exceptions saves *lots* of range and value tests.
        except Exception as e:
            print('')
            print("Error in Leo's token-based beautifier")
            print(f"{self.error_message(e)}")
            print('')
            typ, val, tb = sys.exc_info()
            traceback.print_tb(tb)
            print('')
            print("Please report this message to Leo's developers")
            print('')
        return None
    #@+node:ekr.20240105145241.6: *5* tbo.beautify_file (entry. possible live)
    def beautify_file(self, filename: str) -> bool:  # pragma: no cover
        """
        TokenBasedOrange: Beautify the the given external file.

        Return True if the file was changed.
        """
        self.filename = filename
        contents, encoding, tokens = self.init_tokens_from_file(filename)
        if not (contents and tokens):
            return False  # Not an error.
        assert isinstance(tokens[0], InputToken), repr(tokens[0])
        results = self.beautify(contents, filename, tokens)
        # Something besides newlines must change.
        if not results:
            return False
        if self.regularize_nls(contents) == self.regularize_nls(results):
            return False
        # Write the results
        if not self.silent:
            print(f"tbo: changed {g.shortFileName(filename)}")
        if 0:  ###
            self.write_file(filename, results, encoding=encoding)
        return True
    #@+node:ekr.20240112021737.1: *5* tbo.create_indices
    def create_indices(self, tokens: list[InputToken]) -> list[int]:
        """
        Create a list (one per logical line) of the index of the first token of
        the *next* line.
        """
        indices: list[int] = []
        if not tokens:
            return indices
        assert tokens[0].line_number == 0, tokens[0].line_number
        # The start of the line 1 is token[1]
        indices.append(1)
        prev_line = 1
        for i, token in enumerate(tokens):
            if i > 0 and token.line_number != prev_line:
                indices.append(i)
                # Careful! token.line_number may be > prev_line + 1
                while len(indices) < token.line_number:
                    indices.append(i)
                prev_line = token.line_number
        # Add an entry for the last line.
        indices.append(len(tokens) - 1)
        return indices
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
    #@+node:ekr.20240112082350.1: *5* tbo.error_message
    def error_message(self, exception: Exception) -> str:
        """Return a full message for BeautifyError."""
        return (
            f"\n{exception.__class__.__name__}! {exception!s}\n"
            f"At token {self.index}, line number: {self.token.line_number}:\n"
            f"Line: {self.token.line!r}"
        )
    #@+node:ekr.20240105140814.17: *5* tbo.write_file
    def write_file(self, filename: str, s: str, encoding: str = 'utf-8') -> None:
        """
        Write the string s to the file whose name is given.

        Handle all exceptions.

        Before calling this function, the caller should ensure
        that the file actually has been changed.
        """
        try:
            # Write the file with platform-dependent newlines.
            with open(filename, 'w', encoding=encoding) as f:
                f.write(s)
        except Exception as e:
            g.trace(f"Error writing {filename}\n{e}")
    #@+node:ekr.20240105145241.9: *4* tbo: Input visitors & generators
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
    #@+node:ekr.20240105145241.13: *5* tbo.do_fstring_start & continue_fstring
    def do_fstring_start(self) -> None:
        """Handle the 'fstring_start' token. Enter f-string mode."""
        self.in_fstring = True
        self.gen_token('verbatim', self.token.value)

    def continue_fstring(self) -> None:
        """
        Put the next token in f-fstring mode.
        Exit f-string mode if the token is 'fstring_end'.
        """
        self.gen_token('verbatim', self.token.value)
        if self.token.kind == 'fstring_end':
            self.in_fstring = False
    #@+node:ekr.20240105145241.14: *5* tbo.do_indent
    consider_message = 'consider using python/Tools/scripts/reindent.py'

    def do_indent(self) -> None:
        """Handle indent token."""

        # Refuse to beautify mal-formed files.
        if '\t' in self.token.value:  # pragma: no cover
            raise BeautifyError(f"Leading tabs found: {self.consider_message}")

        if (len(self.token.value) % self.tab_width) != 0:  # pragma: no cover
            raise BeautifyError(f"Indentation error! {self.consider_message}")

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
        ### WRONG: must handle compound statements explicitly #####
        if name in self.compound_statements:
            self.gen_word(name)
        elif name in self.operator_keywords:
            self.gen_word_op(name)
        else:
            self.gen_word(name)
    #@+node:ekr.20240105145241.40: *6* tbo.gen_word
    def gen_word(self, s: str) -> None:
        """Add a word request to the code list."""
        assert s == self.token.value
        assert s and isinstance(s, str), repr(s)

        # Scan special statements, adding context to *later* input tokens.
        func = self.word_dispatch.get(s)
        if func:
            # Call scan_compound_statement, scan_def, scan_from, scan_import.
            func()

        # Add context to *this* input token.
        if s in ('class', 'def'):
            # The defined name is not a function call.
            i = next(self.index)
            if is_kind(i, 'name'):
                set_context(i, 'class/def')
        elif self.token.context != 'class/def':
            # A possible function call.
            i = next(self.index)
            if i and self.is_op(i, '('):
                self.scan_call(i)

        # Finally: generate output tokens.
        if False and s == 'i':  ###
            g.trace(self.token.line_number, 's', s, self.token.line.strip())
        self.gen_blank()
        self.gen_token('word', s)
        self.gen_blank()

        ###
        # if self.square_brackets_stack:
            # # A previous 'op-no-blanks' token may cancel this blank.
            # self.gen_blank()
            # self.gen_token('word', s)
        # elif self.in_arg_list > 0:
            # self.gen_token('word', s)
            # self.gen_blank()
        # else:
            # self.gen_blank()
            # self.gen_token('word', s)
            # self.gen_blank()
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

        - NL tokens end *physical* lines. They appear whe when a logical line
          of code spans multiple physical lines.
        """
        # Only do_newline and do_nl should call this method.
        token = self.token
        assert token.kind in ('newline', 'nl'), (token.kind, g.callers())

        # Create the 'line-end' output token.
        self.gen_line_end()

        # Add the indentation until the next indent/unindent token.
        self.gen_line_indent()

    do_nl = do_newline
    #@+node:ekr.20240105145241.25: *6* tbo.gen_line_end
    def gen_line_end(self) -> OutputToken:
        """Add a line-end request to the code list."""
        # This may be called from do_name as well as do_newline and do_nl.
        assert self.token.kind in ('newline', 'nl'), self.token.kind
        self.clean('blank')  # Important!
        self.clean('line-indent')
        t = self.gen_token('line-end', '\n')
        # Distinguish between kinds of 'line-end' tokens.
        t.newline_kind = self.token.kind
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
        prev_i = self.prev_token(self.index)
        prev = self.tokens[prev_i]
        if context is None:
            # Find the boundaries of the slice: the enclosing square brackets.
            context = self.scan_slice()
        # Now we can generate proper code.
        self.clean('blank')
        if context == 'complex-slice':
            if prev.value not in '[:':
                self.gen_blank()
            self.gen_token('op', val)
            self.gen_blank()
        elif context == 'simple-slice':
            ### g.trace('simple-slice', self.token.line.strip())  ###
            self.gen_token('op-no-blanks', val)
        elif context == 'end-statement':
            self.gen_token('op-no-blank', val)
        else:
            self.gen_token('op', val)
            self.gen_blank()
    #@+node:ekr.20240109115925.1: *7* tbo.scan_slice & helpers
    def scan_slice(self) -> Optional[str]:
        """
        Find the enclosing square brackets.
        
        Return one of (None, 'simple-slice', 'complex-slice')
        """
        # Scan backward.
        i = self.index
        i1 = self.find_open_square_bracket(i)
        if not is_op(i1, '['):
            return None

        # Scan forward.
        i2 = self.find_close_square_bracket(i)
        if not is_op(i2, ']'):
            return None

        # Sanity checks.
        expect_op(i1, '[')
        expect_op(i2, ']')

        if 0:  ###
            g.trace('Found []', 'line:', self.token.line_number,
                i1, self.index, i2, self.token.line.strip())
            g.printObj(self.tokens[i1 : i2 + 1])

        # Set complex if the inner area contains something other than 'name' or 'number' tokens.
        is_complex = False
        i = next(i1)
        while i and i < i2:
            token = self.tokens[i]
            if is_op(i, ':'):
                # Look ahead for '+', '-' unary ops.
                next_i = next(i)
                if is_ops(next_i, ['-', '+']):
                    i = next_i  # Skip the unary.
            elif token.kind == 'number':
                pass
            elif token.kind != 'name' or token.value in ('if', 'else'):
                is_complex = True
                break
            i = next(i)

        ### g.trace('Complex?', is_complex, '\n')

        # Set the context for all ':' tokens.
        context = 'complex-slice' if is_complex else 'simple-slice'
        i = next(i1)
        while i and i < i2:
            if is_op(i, ':'):
                set_context(i, context)
            i = next(i)
        return context
    #@+node:ekr.20240114022153.1: *8* tbo.find_close_square_bracket
    def find_close_square_bracket(self, i: int) -> Optional[int]:
        """
        Search forwards for a ']', ignoring ']' tokens inner groups.
        
        This strategy is valid assuming the Python text is well formed!
        """
        level = 0
        while i < len(self.tokens):
            if is_op(i, '['):
                level += 1
            elif is_op(i, ']'):
                if level == 0:
                    return i
                assert level > 0, f"Unbalanced square brackets: {self.token.line!r}"
                level -= 1
            i += 1
        return None
    #@+node:ekr.20240114022212.1: *8* tbo.find_open_square_bracket
    def find_open_square_bracket(self, i: int) -> Optional[int]:
        """
        Search backwards for a '[', ignoring '[' tokens in inner groups.
        
        This strategy is valid assuming the Python text is well formed!
        """
        level = 0
        while i >= 0:
            if is_op(i, '['):
                if level == 0:
                    return i
                assert level < 0, f"Unbalanced square brackets: {self.token.line!r}"
            elif is_op(i, ']'):
                # Now we expect an inner '[' token before the final match.
                level -= 1
            i -= 1
        return None
    #@+node:ekr.20240109035004.1: *6* tbo.gen_dot_op
    def gen_dot_op(self) -> None:
        """Handle the '.' input token."""
        context = self.token.context
        # Remove previous 'blank' token *before* calculating prev.
        self.clean('blank')
        prev = self.code_list[-1]
        next_i = self.next_token(self.index)
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
            #        However, hen combining an argument annotation with a default value,
            #        *do* use spaces around the = sign
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
    #@+node:ekr.20240105145241.37: *6* tbo.gen_possible_unary_op & helper
    def gen_possible_unary_op(self) -> None:
        """Add a unary or binary op to the token list."""
        val = self.token.value
        self.clean('blank')
        if self.is_unary_op(val):
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
    def is_unary_op(self, val: str) -> bool:

        if val == '~':
            return True
        if val not in '+-':
            return False
        # Get the previous significant token.
        prev_i = self.prev_token(self.index)
        prev_token = self.tokens[prev_i]
        kind, value = prev_token.kind, prev_token.value
        ### g.trace('prev', prev_token, repr(self.token.line))
        if kind in ('number', 'string'):
            return False
        if kind == 'op' and value in ')]':
            return False
        if self.is_keyword(prev_token):
            return True
        if kind == 'name':
            return False
        ### g.trace('Unary!')
        return True
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
        prev = self.code_list[-1]

        self.clean('blank')

        ### g.trace('prev:', prev, val, 'context:', context)

        if context == 'arg':
            self.gen_blank()
            self.gen_token('op-no-blanks', val)
        else:
            self.gen_blank()
            self.gen_token('op', val)
            self.gen_blank()

        if 0:  ### OLD

            ### if context not in ('annotation', 'initializer'):
            if context not in ('arg', 'annotation', 'initializer'):
                self.gen_blank()
                self.gen_token('op', val)
                return  # #2533


            if self.paren_level > 0:
                prev = self.code_list[-1]
                ###
                # if prev.kind == 'lt' or (prev.kind, prev.value) == ('op', ','):
                    # self.gen_blank()
                    # self.gen_token('op', val)
                    # return
                if prev.kind == 'lt':
                    self.gen_token('op', val)
                    return
                if (prev.kind, prev.value) == ('op', ','):
                    self.gen_blank()
                    self.gen_token('op', val)
                    return

            self.gen_blank()
            self.gen_token('op', val)
            self.gen_blank()
    #@+node:ekr.20240105145241.39: *6* tbo.gen_star_star_op
    def gen_star_star_op(self) -> None:
        """Put a ** operator, with a special case for **kwargs."""
        val = self.token.value
        context = self.token.context
        prev = self.code_list[-1]

        self.clean('blank')

        ### g.trace('prev:', prev, val, 'context:', context)

        if context == 'arg':
            self.gen_blank()
            self.gen_token('op-no-blanks', val)
        else:
            self.gen_blank()
            self.gen_token('op', val)
            self.gen_blank()

        if 0:  ### OLD
            if context not in ('annotation', 'initializer'):
                self.gen_blank()
                self.gen_token('op', val)
                return  # #2533
            if self.paren_level > 0:
                prev = self.code_list[-1]
                if prev.kind == 'lt' or (prev.kind, prev.value) == ('op', ','):
                    self.gen_blank()
                    self.gen_token('op', val)
                    return
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
        """Handle a 'string' token."""
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
    #@+node:ekr.20240105145241.41: *4* tbo: Scanners & helpers
    #@+node:ekr.20240106181128.1: *5* tbo.scan_annotation
    def scan_annotation(self, i1: int) -> Optional[int]:
        """Scan an annotation if a function definition arg."""

        ###
        # print('')  ###
        # g.trace(f"{i1:2} {self.tokens[i1].line!r}")  ###
        # g.printObj(self.tokens[i1:i1+3], tag=str(i1))  ###

        # Scan the ':'
        expect_op(i1, ':')
        set_context(i1, 'annotation')
        i = next(i1)

        # Scan to the next ',' or '=', ignoring inner parens.
        i3 = self.find_delim(i, [',', '=', ')'])
        ### g.trace('FOUND', i3, self.tokens[i3])

        # Set the contexts of inner ops.
        for i4 in range(i1 + 1, i3 - 1):
            if is_ops(i4, ['=', ':']):
                set_context(i4, 'annotation')
        return i3
    #@+node:ekr.20240106173638.1: *5* tbo.scan_arg
    def scan_arg(self, i1: int) -> Optional[int]:
        """Scan a single function definition argument"""

        # Scan optional  * and ** operators.
        i = i1
        if is_ops(i, ['*', '**']):
            self.set_context(i1, 'arg')
            i = next(i)
            # Handle *,
            if is_op(i, ','):
                i = next(i)
                return i

        # Scan the argument's name.
        expect(i, 'name')
        i = next(i)

        # Scan an optional annotation.
        has_annotation = is_op(i, ':')
        if has_annotation:
            set_context(i, 'annotation')
            i = self.scan_annotation(i)

        # Scan an optional initializer.
        if is_op(i, '='):
            if has_annotation:
                set_context(i, 'annotation')
            else:
                set_context(i, 'initializer')
            i = self.scan_initializer(i, has_annotation)

        # Scan the optional comma.
        if is_op(i, ','):
            i = next(i)
        return i
    #@+node:ekr.20240106172905.1: *5* tbo.scan_args
    def scan_args(self, i1: int, i2: int) -> Optional[int]:
        """Scan a comma-separated list of function definition arguments."""

        # Sanity checks.
        assert i2 > i1, (i1, i2)
        expect_op(i1, '(')
        expect_op(i2, ')')

        # Scan the '('
        i = next(i1)

        # Scan each argument.
        while i and i < i2 and not is_op(i, ')'):
            i = self.scan_arg(i)

        # Scan the ')'
        expect_op(i, ')')
        return i
    #@+node:ekr.20240107091700.1: *5* tbo.scan_call
    def scan_call(self, i1: int) -> None:
        """Scan a function call"""

        # Find i1 and i2, the boundaries of the argument list.
        expect_op(i1, '(')

        # Scan the arguments.
        i = self.scan_call_args(i1)

        # Sanity check.
        expect_op(i, ')')
    #@+node:ekr.20240107092559.1: *5* tbo.scan_call_arg
    def scan_call_arg(self, i1: int) -> Optional[int]:
        """
        Scan a single function definition argument.
        
        Set context for every '=' operator.
        """
        # Handle leading * and ** args.
        if self.is_ops(i1, ['*', '**']):
            self.set_context(i1, 'arg')

        # Find the closing ')', ignoring nested parens.
        i = self.find_delim(i1, [',', ')'])

        # Set the context for all args.
        for i2 in range(i1 + 1, i - 1):
            if self.is_op(i2, '='):
                self.set_context(i2, 'initializer')
        return i
    #@+node:ekr.20240107092458.1: *5* tbo.scan_call_args
    def scan_call_args(self, i1: int) -> Optional[int]:
        """Scan a comma-separated list of function definition arguments."""

        # Scan the '('
        expect_op(i1, '(')
        i = next(i1)

        # Quit if there are no args.
        if is_op(i, ')'):
            return i

        # Scan arguments.
        while i and i < len(self.tokens):
            i = self.scan_call_arg(i)
            if is_op(i, ')'):
                break
            i = next(i)

        # Sanity check.
        expect_op(i, ')')

        # The caller will eat the ')'.
        return i
    #@+node:ekr.20240108062349.1: *5* tbo.scan_compound_statement
    def scan_compound_statement(self) -> None:
        """
        Scan a compound statement, adding 'end-statement' context to the
        trailing ':' token.
        """
        # Scan the keyword.
        i = self.index
        ### g.trace('=====', repr(self.tokens[i].line), g.callers())
        expect(i, 'name')
        keyword = self.tokens[i].value
        i = next(i)

        if is_op(i, '('):
            # Find the matching ')'
            i = next(i)
            i = self.find_delim(i, [')'])
            i = next(i)

        # Find the trailing ':'.
        ### g.trace('----', self.tokens[i])
        i = self.find_delim(i, [':'])

        if i is not None:
            # Set the context.
            expect_op(i, ':')
            set_context(i, 'end-statement')
            return

        # Last check.
        word_ops = ('if', 'else', 'for')
        if keyword not in word_ops:
            raise BeautifyError(f"Expecting one of {word_ops}, got {keyword!r}")
    #@+node:ekr.20240105145241.42: *5* tbo.scan_def
    def scan_def(self) -> None:
        """Scan a complete 'def' statement."""

        # Find i1 and i2, the boundaries of the argument list.
        i = self.index
        expect(i, 'name', 'def')
        i = next(i)
        expect(i, 'name')
        i = next(i)
        expect_op(i, '(')
        i1 = i

        # Find the closing ')', ignoring nested parens.
        i = i2 = self.find_close_paren(i)
        expect_op(i, ')')
        i = next(i)
        expect_ops(i, ['->', ':'])

        # Find i3, the ending ':' of the def statement.
        i3 = self.find_delim(i, [':'])
        expect_op(i3, ':')
        self.set_context(i3, 'end-statement')

        # Scan the arguments.
        self.scan_args(i1, i2)
    #@+node:ekr.20240107143500.1: *5* tbo.scan_from
    def scan_from(self) -> None:
        """
        Scan a `from x import` statement just enough to handle leading '.'.
        """

        # Find the end of the 'from' statement.
        end = self.find_end_of_line()
        if end is None:
            return

        # Add 'from' context to all '.' tokens.
        i = self.index
        while i and i < end:
            if is_op(i, '.'):
                set_context(i, 'from')
            i = next(i)
    #@+node:ekr.20240108083829.1: *5* tbo.scan_import
    def scan_import(self) -> None:

        # Find the end of the import statement.
        end = self.find_end_of_line()
        if end is None:
            return

        # Add 'import' context to all '.' operators.
        i = self.index
        while i and i < end:
            if is_op(i, '.'):
                set_context(i, 'import')
            i = next(i)
    #@+node:ekr.20240106181215.1: *5* tbo.scan_initializer
    def scan_initializer(self, i1: int, has_annotation: bool) -> Optional[int]:
        """Scan an initializer in a function definition argument."""

        # Scan the '='.
        expect_op(i1, '=')
        set_context(i1, 'initializer')
        i = next(i1)

        # Scan up to ',' or ')'
        if is_op(i, '('):
            i = self.find_close_paren(i)
            expect_op(i, ')')
        else:
            i = self.find_delim(i, [',', ')'])
            expect_ops(i, [',', ')'])
        return i
    #@+node:ekr.20240109032639.1: *5* tbo.scan_simple_statement
    def scan_simple_statement(self) -> int:
        """
        Scan to the end of a simple statement like an `import` statement.
        """
        i = self.find_end_of_line()
        if i is None:
            return None
        self.expect(i, 'newline')
        return i
    #@+node:ekr.20240113054629.1: *5* tbo.scan_statements
    def scan_statements(self) -> None:
        """
        Scan the entire file
        """
        i = self.index
        assert i == 0, repr(i)
        while i is not None:
            i = self.scan_statement(i)
    #@+node:ekr.20240113054641.1: *5* tbo.scan_statement (** To do **)
    def scan_statement(self, i: int) -> int:
        """
        Scan the next statement, including docstrings.
        
        Notes & questions.
        
        - How does scan_statement coordinate with the main loop?
        
        - Maybe via per-statement data?
        
        - Maybe a statement_info array, similar to line_indices?
          
        - Note: statements do *not* have to start at the star of a line:
            
          if 1: a = 2
          else: a = 3
        """
        i = next(i)
        return i
    #@+node:ekr.20240110205127.1: *5* tbo: Scan helpers
    #@+node:ekr.20240106220724.1: *6* tbo.dump_token_range
    def dump_token_range(self, i1: int, i2: int, tag: str = None) -> None:
        """Dump the given range of input tokens."""
        if tag:
            print(tag)
        for token in self.tokens[i1 : i2 + 1]:
            print(token.dump())
    #@+node:ekr.20240106090914.1: *6* tbo.expect (with alias)
    def expect(self, i: int, kind: str, value: str = None) -> None:
        """Raise an exception if self.tokens[i] is not as expected."""
        full = False
        trace = True
        tag = 'TBO.expect'
        try:
            line = self.tokens[i].line
            line_number = self.tokens[i].line_number
        except Exception:
            g.es_exception()
            line = '<no line>'
            line_number = 0

        def dump() -> None:
            if not trace:
                return
            print('')
            print(f"{tag}: Error at token {i}, line number: {line_number}:")
            print(f"file: {self.filename}")
            print(f"line: {line!r}\n")
            print('callers:', g.callers())
            print('')
            if 1:
                lines = g.splitLines(self.contents)
                n1, n2 = max(0, line_number - 10), line_number + 5
                g.printObj(lines[n1 : n2 + 1], tag=f"{tag}: lines[{n1}:{n2}]...", offset=n1)
            if full:
                g.printObj(self.tokens, tag=f"{tag}: tokens")
            else:
                i1, i2 = max(0, i - 5), i + 5
                g.printObj(self.tokens[i1 : i2 + 1], tag=f"{tag}: tokens[{i1}:{i2}]...", offset=i1)

        token = self.tokens[i]
        if value is None:
            if token.kind != kind:
                dump()
                raise BeautifyError(
                    f"expect: expected token.kind: {kind!r} got {token}\n"
                    f"callers: {g.callers()}"
                )
        elif (token.kind, token.value) != (kind, value):
            dump()
            raise BeautifyError(
                f"expect: expected token.kind: {kind!r} token.value: "
                f"{value!r} got {token}\n"
                f"Callers: {g.callers()}"
            )
    #@+node:ekr.20240114015808.1: *6* tbo.expect_op (with alias)
    def expect_op(self, i: int, value: str) -> None:
        """Raise an exception if self.tokens[i] is not as expected."""
        token = self.tokens[i]
        if token.kind != 'op':
            raise BeautifyError(
                f"expect_op: expected op token, got {token.kind!r}\n"
                f"callers: {g.callers()}"
            )
        if token.value != value:
            raise BeautifyError(
                f"expect_op: expected value: {value!r}, got {token.value!r}\n"
                f"callers: {g.callers()}"
            )
    #@+node:ekr.20240114013952.1: *6* tbo.expect_ops (with alias)
    def expect_ops(self, i: int, values: list) -> None:
        """Raise an exception if self.tokens[i] is not as expected."""
        token = self.tokens[i]
        if token.kind != 'op':
            raise BeautifyError(
                f"expect_ops: expected token.kind == 'op', got {token.kind!r}\n"
                f"callers: {g.callers()}"
            )
        if token.value not in values:
            raise BeautifyError(
                f"expect_ops: expected token.value in {values!r}, got {token.value!r}\n"
                f"callers: {g.callers()}"
            )
    #@+node:ekr.20240110062055.1: *6* tbo.find_end_of_line
    def find_end_of_line(self) -> Optional[int]:
        """
        Return the index the next newline at the outer paren level.
        """
        i = self.index
        parens = 0
        while i and 0 <= i < len(self.tokens):
            token = self.tokens[i]
            # Precheck.
            if token.kind == 'newline' and parens == 0:
                return i
            if token.kind == 'op':
                # Bump counts.
                if token.value == '(':
                    parens += 1
                elif token.value == ')':
                    parens -= 1
            # Post-check.
            if token.kind == 'newline' and parens == 0:
                return i
            i += 1
        return None
    #@+node:ekr.20240114063347.1: *6* tbo.find_delim
    def find_delim(self, i: int, delims: list) -> Optional[int]:
        """Find the next delimiter token, skipping inner grouped tokens."""

        # The code assumes only works for ')' and non-grouping tokens.
        assert not any(z in delims for z in '([]'), (delims, g.callers())

        # The code assumes that the first token is *not* '('.
        if ')' in delims:
            assert not is_op(i, '('), g.callers()

        # Skip tokens until one of the delims is found.
        parens, square_brackets = 0, 0
        if 0:  ###
            print('')  ###
            print(i, 'delims:', delims, repr(self.tokens[i].line), g.callers(2))
        while i < len(self.tokens):
            ### g.trace(i, self.tokens[i])
            if is_op(i, '['):
                square_brackets += 1
            elif is_op(i, ']'):
                square_brackets -= 1
            elif is_op(i, '('):
                parens += 1
            elif is_op(i, ')'):
                if ')' in delims and (parens, square_brackets) == (0, 0):
                    return i
                parens -= 1
                assert parens >= 0, "unexpected ')' token"
            elif is_ops(i, delims) and (parens, square_brackets) == (0, 0):
                return i
            i += 1
        return None
    #@+node:ekr.20240114022135.1: *6* tbo.find_close_paren
    def find_close_paren(self, i: int) -> Optional[int]:
        """Find the  ')' matching this '(' token."""
        expect_op(i, '(')
        i = next(i)
        level = 0
        while i < len(self.tokens):
            if is_op(i, '('):
                level += 1
            elif is_op(i, ')'):
                if level == 0:
                    return i
                assert level > 0, f"Unbalanced parens: {self.token.line!r}"
                level -= 1
            i += 1
        return None
    #@+node:ekr.20240106053414.1: *6* tbo.is_keyword
    def is_keyword(self, token: InputToken) -> bool:
        """
        Return True if the token represents a Python keyword.
        
        But return False for 'True', 'False' or 'None':
        these can appear in expressions.
        """
        value = token.value
        return (
            token.kind == 'name'
            and value not in ('True', 'False', None)
            and (keyword.iskeyword(value) or keyword.issoftkeyword(value))
        )
    #@+node:ekr.20240106172054.1: *6* tbo.is_op & is_ops (with alias)
    def is_op(self, i: int, value: str) -> bool:

        if i is None:
            return False
        token = self.tokens[i]
        return token.kind == 'op' and token.value == value

    def is_ops(self, i: int, values: list[str]) -> bool:

        if i is None:
            return False
        token = self.tokens[i]
        return token.kind == 'op' and token.value in values
    #@+node:ekr.20240114021152.1: *6* tbo.is_kind (with alias)
    def is_kind(self, i: int, kind: str) -> bool:

        return self.tokens[i].kind == kind

    #@+node:ekr.20240106093210.1: *6* tbo.is_significant_token
    def is_significant_token(self, token: InputToken) -> bool:
        """Return true if the given token is not whitespace."""
        return token.kind not in (
            'comment', 'dedent', 'indent', 'newline', 'nl', 'ws',
        )
    #@+node:ekr.20240105145241.43: *6* tbo.next/prev_token (with aliases)
    def next_token(self, i: int) -> Optional[int]:
        """
        Return the next *significant* token in the list of *input* tokens.

        Ignore whitespace, indentation, comments, etc.
        """
        i += 1
        while i < len(self.tokens):
            token = self.tokens[i]
            if self.is_significant_token(token):
                return i
            i += 1
        return None

    def prev_token(self, i: int) -> Optional[int]:
        """
        Return the previous *significant* token in the list of *input* tokens.

        Ignore whitespace, indentation, comments, etc.
        """
        i -= 1
        while i >= 0:
            token = self.tokens[i]
            if self.is_significant_token(token):
                return i
            i -= 1
        return None
    #@+node:ekr.20240106170746.1: *6* tbo.set_context (with alias)
    def set_context(self, i: int, context: str) -> None:
        """
        Set the context for self.tokens[i].
        
        This method may be called more than once for the same token!
        
        The *first* context is the valid context.
        """
        token = self.tokens[i]
        if not token.context:
            ### g.trace(f"{i:4} {context:14} {g.callers(1)}")
            token.context = context
    #@-others
#@+node:ekr.20240105140814.121: ** function: (leoTokens.py) main & helpers
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
        orange_command(arg_files, files, settings_dict, args.verbose)
    # if args.od:
        # orange_diff_command(files, settings_dict)
#@+node:ekr.20240105140814.9: *3* function: get_modified_files
def get_modified_files(repo_path: str) -> list[str]:
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
def scan_args() -> tuple[Any, dict[str, Any], list[str]]:
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

gBeautifier: TokenBasedOrange = None

if __name__ == '__main__':
    main()  # pragma: no cover

#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
