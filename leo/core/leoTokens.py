#@+leo-ver=5-thin
#@+node:ekr.20240105140814.1: * @file leoTokens.py
# This file is part of Leo: https://leo-editor.github.io/leo-editor
# Leo's copyright notice is based on the MIT license:
# https://leo-editor.github.io/leo-editor/license.html

# This file may be compiled with mypyc as follows:
# python -m mypyc leo\core\leoTokens.py --strict-optional

#@+<< leoTokens.py: docstring >>
#@+node:ekr.20240105140814.2: ** << leoTokens.py: docstring >>
"""
leoTokens.py: A beautifier for Python that uses *only* tokens.

For help: `python -m leo.core.leoTokens --help`

Use Leo https://leo-editor.github.io/leo-editor/ to study this code!

Without Leo, you will see special **sentinel comments** that create
Leo's outline structure. These comments have the form::

    `#@<comment-kind>:<user-id>.<timestamp>.<number>: <outline-level> <headline>`
"""
#@-<< leoTokens.py: docstring >>
#@+<< leoTokens.py: imports & annotations >>
#@+node:ekr.20240105140814.3: ** << leoTokens.py: imports & annotations >>
from __future__ import annotations
import argparse
import difflib
import glob
import keyword
import io
import os
import re
import textwrap
import time
import tokenize
from typing import Generator, Optional, Union, TYPE_CHECKING

# Leo Imports.
from leo.core import leoGlobals as g
assert g

if TYPE_CHECKING:
    from leo.core.leoNodes import Position

SettingsDict = dict[str, Union[int, bool]]
#@-<< leoTokens.py: imports & annotations >>

#@+others
#@+node:ekr.20240214065940.1: ** top-level functions (leoTokens.py)
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
def dump_results(results: list[str], tag: str = 'Results') -> None:  # pragma: no cover
    print('')
    print(f"{tag}...\n")
    print(''.join(results))
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
        print('===== input token list is None ===== ')
        print('')
        return ''
    return ''.join([z.to_string() for z in tokens])
#@+node:ekr.20240926050431.1: *3* function: beautify_file (leoTokens.py)
def beautify_file(filename: str) -> bool:
    """
    Beautify the given file, writing it if has changed.
    """
    settings: SettingsDict = {
        'all': False,  # Don't beautify all files.
        'beautified': True,  # Report changed files.
        'diff': False,  # Don't show diffs.
        'report': True,  # Report changed files.
        'write': True,  # Write changed files.
    }
    tbo = TokenBasedOrange(settings)
    return tbo.beautify_file(filename)
#@+node:ekr.20240105140814.121: *3* function: main (leoTokens.py)
def main() -> None:  # pragma: no cover
    """Run commands specified by sys.argv."""
    args, settings_dict, arg_files = scan_args()
    cwd = os.getcwd()

    # Calculate requested files.
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
        # print(f"No files in {arg_files!r}")
        return

    # Calculate the actual list of files.
    modified_files = g.getModifiedFiles(cwd)

    def is_dirty(path: str) -> bool:
        return os.path.abspath(path) in modified_files

    # Compute the files to be checked.
    if args.all:
        # Handle all requested files.
        to_be_checked_files = requested_files
    else:
        # Handle only modified files.
        to_be_checked_files = [z for z in requested_files if is_dirty(z)]

    # Compute the dirty files among the to-be-checked files.
    dirty_files = [z for z in to_be_checked_files if is_dirty(z)]

    # Do the command.
    if to_be_checked_files:
        orange_command(arg_files, requested_files, dirty_files, to_be_checked_files, settings_dict)
#@+node:ekr.20240105140814.5: *3* function: orange_command (leoTokens.py)
def orange_command(
    arg_files: list[str],
    requested_files: list[str],
    dirty_files: list[str],
    to_be_checked_files: list[str],
    settings: Optional[SettingsDict] = None,
) -> None:  # pragma: no cover
    """The outer level of the 'tbo/orange' command."""
    t1 = time.process_time()
    # n_tokens = 0
    n_beautified = 0
    if settings is None:
        settings = {}
    for filename in to_be_checked_files:
        if os.path.exists(filename):
            tbo = TokenBasedOrange(settings)
            beautified = tbo.beautify_file(filename)
            if beautified:
                n_beautified += 1
            # n_tokens += len(tbo.input_tokens)
        else:
            print(f"file not found: {filename}")
    # Report the results.
    t2 = time.process_time()
    if n_beautified or settings.get('report'):
        print(
            f"tbo: {t2-t1:4.2f} sec. "
            f"dirty: {len(dirty_files):<3} "
            f"checked: {len(to_be_checked_files):<3} "
            f"beautified: {n_beautified:<3} in {','.join(arg_files)}"
        )
#@+node:ekr.20240105140814.10: *3* function: scan_args (leoTokens.py)
def scan_args() -> tuple[argparse.Namespace, SettingsDict, list[str]]:  # pragma: no cover
    description = textwrap.dedent(
    """Beautify or diff files""")
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument('PATHS', nargs='*', help='directory or list of files')
    add2 = parser.add_argument

    # Arguments.
    add2('-a', '--all', dest='all', action='store_true',
        help='Beautify all files, even unchanged files')
    add2('-b', '--beautified', dest='beautified', action='store_true',
        help='Report beautified files individually, even if not written')
    add2('-d', '--diff', dest='diff', action='store_true',
        help='show diffs instead of changing files')
    add2('-r', '--report', dest='report', action='store_true',
        help='show summary report')
    add2('-w', '--write', dest='write', action='store_true',
        help='write beautifed files (dry-run mode otherwise)')

    # Create the return values, using EKR's prefs as the defaults.
    parser.set_defaults(
        all=False, beautified=False, diff=False, report=False, write=False,
        tab_width=4,
    )
    args: argparse.Namespace = parser.parse_args()
    files = args.PATHS

    # Create the settings dict, ensuring proper values.
    settings_dict: SettingsDict = {
        'all': bool(args.all),
        'beautified': bool(args.beautified),
        'diff': bool(args.diff),
        'report': bool(args.report),
        'write': bool(args.write)
    }
    return args, settings_dict, files
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

    __slots__ = (
        'context',
        'index',
        'kind',
        'line',
        'line_number',
        'value',
    )

    def __init__(
        self, kind: str, value: str, index: int, line: str, line_number: int,
    ) -> None:
        self.context: Optional[str] = None
        self.index = index
        self.kind = kind
        self.line = line  # The entire line containing the token.
        self.line_number = line_number
        self.value = value

    def __repr__(self) -> str:  # pragma: no cover
        s = f"{self.index:<5} {self.kind:>8}"
        return f"Token {s}: {self.show_val(20):22}"

    def __str__(self) -> str:  # pragma: no cover
        s = f"{self.index:<5} {self.kind:>8}"
        return f"Token {s}: {self.show_val(20):22}"

    def to_string(self) -> str:
        """Return the contribution of the token to the source file."""
        return self.value if isinstance(self.value, str) else ''

    #@+others
    #@+node:ekr.20240105140814.54: *4* itoken.brief_dump
    def brief_dump(self) -> str:  # pragma: no cover
        """Dump a token."""
        token_s = f"{self.kind:>10} : {self.show_val(10):12}"
        return f"<line: {self.line_number} index: {self.index:3} {token_s}>"

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
        if self.kind in ('dedent', 'indent', 'newline', 'ws'):
            # val = str(len(self.value))
            val = repr(self.value)
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
        'fstring_level',
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
        self.contents: str = ''
        self.offsets: list[int] = [0]  # Index of start of each line.
        self.prev_offset = -1
        self.token_index = 0
        self.token_list: list[InputToken] = []
        # Describing the scanned f-string...
        self.fstring_level: int = 0
        self.fstring_line: Optional[str] = None
        self.fstring_line_number: Optional[int] = None
        self.fstring_values: Optional[list[str]] = None

    #@+others
    #@+node:ekr.20240105143307.2: *4* Tokenizer.add_token
    def add_token(self, kind: str, line: str, line_number: int, value: str,) -> None:
        """
        Add an InputToken to the token list.

        Convert (potentially nested!) fstrings to simple strings.
        """
        if kind == 'fstring_start':
            self.fstring_level += 1
            if self.fstring_level == 1:
                self.fstring_values = []
                self.fstring_line = line
                self.fstring_line_number = line_number
            self.fstring_values.append(value)
            return
        if self.fstring_level > 0:
            # Accumulating an f-string.
            self.fstring_values.append(value)
            if kind == 'fstring_end':
                self.fstring_level -= 1
            if self.fstring_level > 0:
                return
            # End of the outer f-string.
            # Create a single 'string' token from the saved values.
            kind = 'string'
            value = ''.join(self.fstring_values)
            # Use the line and line number of the 'string-start' token.
            line = self.fstring_line or ''
            line_number = self.fstring_line_number or 0
            # Clear the saved values.
            assert self.fstring_level == 0
            self.fstring_line = None
            self.fstring_line_number = None
            self.fstring_values = None

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
            print(contents)
            print('\nResult...\n')
            print(result)
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
        if ws:
            # Create the 'ws' pseudo-token.
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
        try:
            five_tuples = tokenize.tokenize(
                io.BytesIO(contents.encode('utf-8')).readline)
        except Exception as e:  # pragma: no cover
            print(f"make_input_tokens: exception {e!r}")
            return []
        tokens = self.create_input_tokens(contents, five_tuples)
        if 1:
            # True: 2.9 sec. False: 2.8 sec.
            assert self.check_round_trip(contents, tokens)
        return tokens
    #@+node:ekr.20240105143214.7: *4* Tokenizer.tokens_to_string
    def tokens_to_string(self, tokens: list[InputToken]) -> str:
        """Return the string represented by the list of tokens."""
        if tokens is None:  # pragma: no cover
            # This indicates an internal error.
            print('')
            print('===== No tokens ===== ')
            print('')
            return ''
        return ''.join([z.to_string() for z in tokens])
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

    __slots__ = ('kind', 'value')

    def __init__(self, kind: str, value: Union[int, str, None]) -> None:
        self.kind = kind
        self.value = value

    def __repr__(self) -> str:
        return f"State: {self.kind} {self.value!r}"  # pragma: no cover

    def __str__(self) -> str:
        return f"State: {self.kind} {self.value!r}"  # pragma: no cover
#@+node:ekr.20240128114842.1: *3* class ScanState
class ScanState:  # leoTokens.py.
    """
    A class representing tbo.pre_scan's scanning state.

    Valid (kind, value) pairs:

       kind  Value
       ====  =====
      'args' None
      'from' None
    'import' None
     'slice' list of colon indices
      'dict' list of colon indices

    """

    __slots__ = ('kind', 'token', 'value')

    def __init__(self, kind: str, token: InputToken) -> None:
        self.kind = kind
        self.token = token
        self.value: list[int] = []  # Not always used.

    def __repr__(self) -> str:  # pragma: no cover
        return f"ScanState: i: {self.token.index:<4} kind: {self.kind} value: {self.value}"

    def __str__(self) -> str:  # pragma: no cover
        return f"ScanState: i: {self.token.index:<4} kind: {self.kind} value: {self.value}"
#@+node:ekr.20240105145241.1: *3* class TokenBasedOrange
class TokenBasedOrange:  # Orange is the new Black.

    #@+<< TokenBasedOrange: docstring >>
    #@+node:ekr.20240119062227.1: *4* << TokenBasedOrange: docstring >>
    #@@language rest
    #@@wrap

    """
    Leo's token-based beautifier, three times faster than the beautifier in leoAst.py.

    **Design**

    The *pre_scan* method is the heart of the algorithm. It sets context
    for the `:`, `=`, `**` and `.` tokens *without* using the parse tree.
    *pre_scan* calls three *finishers*.

    Each finisher uses a list of *relevant earlier tokens* to set the
    context for one kind of (input) token. Finishers look behind (in the
    stream of input tokens) with essentially no cost.

    After the pre-scan, *tbo.beautify* (the main loop) calls *visitors*
    for each separate type of *input* token.

    Visitors call *code generators* to generate strings in the output
    list, using *lazy evaluation* to generate whitespace.
    """
    #@-<< TokenBasedOrange: docstring >>
    #@+<< TokenBasedOrange: __slots__ >>
    #@+node:ekr.20240111035404.1: *4* << TokenBasedOrange: __slots__ >>
    __slots__ = [
        # Command-line arguments.
        'all', 'beautified', 'diff', 'report', 'write',

        # Global data.
        'contents', 'filename', 'input_tokens', 'output_list', 'tab_width',
        'insignificant_tokens',  # New.

        # Token-related data for visitors.
        'index', 'input_token', 'line_number',
        'pending_lws', 'pending_ws', 'prev_output_kind', 'prev_output_value',  # New.

        # Parsing state for visitors.
        'decorator_seen', 'in_arg_list', 'in_doc_part', 'state_stack', 'verbatim',

        # Whitespace state. Don't even *think* about changing these!
        'curly_brackets_level', 'indent_level', 'lws', 'paren_level', 'square_brackets_stack',

        # Regular expressions.
        'at_others_pat', 'beautify_pat', 'comment_pat', 'end_doc_pat',
        'nobeautify_pat', 'nobeautify_sentinel_pat', 'node_pat', 'start_doc_pat',
    ]
    #@-<< TokenBasedOrange: __slots__ >>
    #@+<< TokenBasedOrange: python-related constants >>
    #@+node:ekr.20240116040458.1: *4* << TokenBasedOrange: python-related constants >>
    insignificant_kinds = (
        'comment', 'dedent', 'encoding', 'endmarker', 'indent', 'newline', 'nl', 'ws',
    )

    # 'name' tokens that may appear in expressions.
    operator_keywords = (
        'await',  # Debatable.
        'and', 'in', 'not', 'not in', 'or',  # Operators.
        'True', 'False', 'None',  # Values.
    )
    #@-<< TokenBasedOrange: python-related constants >>

    #@+others
    #@+node:ekr.20240105145241.2: *4* tbo.ctor
    def __init__(self, settings: Optional[SettingsDict] = None):
        """Ctor for Orange class."""

        # Set default settings.
        if settings is None:
            settings = {}

        # Hard-code 4-space tabs.
        self.tab_width = 4

        # Define tokens even for empty files.
        self.input_token: InputToken = None
        self.input_tokens: list[InputToken] = []
        self.lws: str = ""  # Set only by Indent/Dedent tokens.
        self.pending_lws: str = ""
        self.pending_ws: str = ""

        # Set by gen_token and all do_* methods that bypass gen_token.
        self.prev_output_kind: str = None
        self.prev_output_value: str = None

        # Set ivars from the settings dict *without* using setattr.
        self.all = settings.get('all', False)
        self.beautified = settings.get('beautified', False)
        self.diff = settings.get('diff', False)
        self.report = settings.get('report', False)
        self.write = settings.get('write', False)

        # The list of tokens that tbo._next/_prev skip.
        self.insignificant_tokens = (
            'comment', 'dedent', 'indent', 'newline', 'nl', 'ws',
        )

        # General patterns.
        self.beautify_pat = re.compile(
            r'#\s*pragma:\s*beautify\b|#\s*@@beautify|#\s*@\+node|#\s*@[+-]others|#\s*@[+-]<<')
        self.comment_pat = re.compile(r'^(\s*)#[^@!# \n]')
        self.nobeautify_pat = re.compile(r'\s*#\s*pragma:\s*no\s*beautify\b|#\s*@@nobeautify')
        self.nobeautify_sentinel_pat = re.compile(r'^#\s*@@nobeautify\s*$', re.MULTILINE)

        # Patterns from FastAtRead class, specialized for python delims.
        self.node_pat = re.compile(r'^(\s*)#@\+node:([^:]+): \*(\d+)?(\*?) (.*)$')  # @node
        self.start_doc_pat = re.compile(r'^\s*#@\+(at|doc)?(\s.*?)?$')  # @doc or @
        self.at_others_pat = re.compile(r'^(\s*)#@(\+|-)others\b(.*)$')  # @others

        # Doc parts end with @c or a node sentinel. Specialized for python.
        self.end_doc_pat = re.compile(r"^\s*#@(@(c(ode)?)|([+]node\b.*))$")
    #@+node:ekr.20240126012433.1: *4* tbo: Checking & dumping
    #@+node:ekr.20240106220724.1: *5* tbo.dump_token_range
    def dump_token_range(self, i1: int, i2: int, tag: Optional[str] = None) -> None:  # pragma: no cover
        """Dump the given range of input tokens."""
        if tag:
            print(tag)
        for token in self.input_tokens[i1 : i2 + 1]:
            print(token.dump())
    #@+node:ekr.20240112082350.1: *5* tbo.internal_error_message
    def internal_error_message(self, message: str) -> str:  # pragma: no cover
        """Print a message about an error in the beautifier itself."""
        # Compute lines_s.
        line_number = self.input_token.line_number
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
            # '\n\n'
            'Error in token-based beautifier!\n'
            f"{message.strip()}\n"
            '\n'
            f"At token {self.index}, line: {line_number} file: {self.filename}\n"
            f"{context_s}"
            "Please report this message to Leo's developers"
        )
    #@+node:ekr.20240226131015.1: *5* tbo.user_error_message
    def user_error_message(self, message: str) -> str:  # pragma: no cover
        """Print a message about a user error."""
        # Compute lines_s.
        line_number = self.input_token.line_number
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
            f"{message.strip()}\n"
            '\n'
            f"At token {self.index}, line: {line_number} file: {self.filename}\n"
            f"{context_s}"
        )
    #@+node:ekr.20240117053310.1: *5* tbo.oops
    def oops(self, message: str) -> None:  # pragma: no cover
        """Raise InternalBeautifierError."""
        raise InternalBeautifierError(self.internal_error_message(message))
    #@+node:ekr.20240105145241.4: *4* tbo: Entries & helpers
    #@+node:ekr.20240105145241.5: *5* tbo.beautify (main token loop)
    def no_visitor(self) -> None:  # pragma: no cover
        self.oops(f"Unknown kind: {self.input_token.kind!r}")

    def beautify(self,
        contents: str, filename: str, input_tokens: list[InputToken],
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
        self.line_number: Optional[int] = None

        # The input and output lists...
        self.output_list: list[str] = []
        self.input_tokens = input_tokens  # The list of input tokens.

        # State vars for whitespace.
        self.curly_brackets_level = 0  # Number of unmatched '{' tokens.
        self.paren_level = 0  # Number of unmatched '(' tokens.
        self.square_brackets_stack: list[bool] = []  # A stack of bools, for self.gen_word().
        self.indent_level = 0  # Set only by do_indent and do_dedent.

        # Parse state.
        self.decorator_seen = False  # Set by do_name for do_op.
        self.in_arg_list = 0  # > 0 if in an arg list of a def.
        self.in_doc_part = False
        self.state_stack: list[ParseState] = []  # Stack of ParseState objects.

        # Leo-related state.
        self.verbatim = False  # True: don't beautify.

        # Ivars describing the present input token...
        self.index = 0  # The index within the tokens array of the token being scanned.
        self.lws = ''  # Leading whitespace. Required!
        #@-<< tbo.beautify: init ivars >>

        try:
            # Pre-scan the token list, setting context.s
            self.pre_scan()

            # Init ivars first.
            self.input_token = None
            self.pending_lws = ''
            self.pending_ws = ''
            self.prev_output_kind = None
            self.prev_output_value = None

            # Init state.
            self.gen_token('file-start', '')
            self.push_state('file-start')

            # The main loop:
            prev_line_number: int = 0
            for self.index, self.input_token in enumerate(input_tokens):
                # Set global for visitors.
                if prev_line_number != self.input_token.line_number:
                    prev_line_number = self.input_token.line_number
                # Call the proper visitor.
                if self.verbatim:
                    self.do_verbatim()
                else:
                    func = getattr(self, f"do_{self.input_token.kind}", self.no_visitor)
                    func()

            # Return the result.
            result = ''.join(self.output_list)
            return result

        # Make no change if there is any error.
        except InternalBeautifierError as e:  # pragma: no cover
            # oops calls self.internal_error_message to creates e.
            print(repr(e))
        except AssertionError as e:  # pragma: no cover
            print(self.internal_error_message(repr(e)))
        return contents
    #@+node:ekr.20240105145241.6: *5* tbo.beautify_file (entry) (stats & diffs)
    def beautify_file(self, filename: str) -> bool:  # pragma: no cover
        """
        TokenBasedOrange: Beautify the the given external file.

        Return True if the file was beautified.
        """
        if 0:
            print(
                f"all: {int(self.all)} "
                f"beautified: {int(self.beautified)} "
                f"diff: {int(self.diff)} "
                f"report: {int(self.report)} "
                f"write: {int(self.write)} "
                f"{g.shortFileName(filename)}"
            )
        self.filename = filename
        contents, tokens = self.init_tokens_from_file(filename)
        if not (contents and tokens):
            return False  # Not an error.
        if self.nobeautify_sentinel_pat.search(contents):
            return False  # Honor @nobeautify sentinel within the file.
        if not isinstance(tokens[0], InputToken):
            self.oops(f"Not an InputToken: {tokens[0]!r}")

        # Beautify the contents, returning the original contents on any error.
        results = self.beautify(contents, filename, tokens)

        # Ignore changes only to newlines.
        if self.regularize_newlines(contents) == self.regularize_newlines(results):
            return False

        # Print reports.
        if self.beautified:  # --beautified.
            print(f"tbo: beautified: {g.shortFileName(filename)}")
        if self.diff:  # --diff.
            print(f"Diffs: {filename}")
            self.show_diffs(contents, results)

        # Write the (changed) file .
        if self.write:  # --write.
            self.write_file(filename, results)
        return True
    #@+node:ekr.20250508041634.1: *5* tbo.beautify_script_tree (entry) and helper
    def beautify_script_tree(self, root: Position) -> None:
        """Undoably beautify root's entire tree."""
        c = root.v.context
        u, undoType = c.undoer, 'beautify-script'
        u.beforeChangeGroup(c.p, undoType)
        n_changed = 0
        for p in root.self_and_subtree():
            bunch = u.beforeChangeNodeContents(p)
            changed = self.beautify_script_node(p)
            if changed:
                n_changed += 1
                u.afterChangeNodeContents(p, undoType, bunch)
        if n_changed:
            u.afterChangeGroup(root, undoType)
            c.redraw(root)
            if not g.unitTesting:
                g.es_print(f"Beautified {n_changed} node{g.plural(n_changed)}")
    #@+node:ekr.20250508030747.1: *6* tbo.beautify_script_node
    def beautify_script_node(self, p: Position) -> bool:
        """Beautify a single node"""

        # Patterns for lines that must be replaced.
        section_ref_pat = re.compile(r'(\s*)\<\<(.+)\>\>(.*)')
        nobeautify_pat = re.compile(r'(\s*)\@nobeautify(.*)')
        trailing_ws_pat = re.compile(r'(.*)#(.*)')

        # Part 1: Replace @others and section references with 'pass'
        #         This hack is valid!
        indices: list[int] = []  # Indices of replaced lines.
        contents: list[str] = []  # Contents after replacements.
        for i, s in enumerate(g.splitLines(p.b)):
            if m := section_ref_pat.match(s):
                contents.append(f"{m.group(1)}pass\n")
                indices.append(i)
            elif m := nobeautify_pat.match(s):
                return False
            else:
                contents.append(s)

        # Part 2: Beautify.
        self.indent_level = 0
        self.filename = 'beautify-script'
        contents_s = ''.join(contents)
        tokens = Tokenizer().make_input_tokens(contents_s)
        if not tokens:
            return False
        results_s: str = self.beautify(contents_s, self.filename, tokens)

        # Part 3: Undo replacements, regularize comments and clean trailing ws.
        body_lines: list[str] = g.splitLines(p.b)
        results: list[str] = g.splitLines(results_s)
        for i in indices:
            old_line = body_lines[i]
            if m := trailing_ws_pat.match(old_line):
                old_line = f"{m.group(1).rstrip()}  #{m.group(2)}"
            results[i] = old_line.rstrip() + '\n'

        # Part 4: Update the body if necessary.
        new_body = ''.join(results)
        changed = p.b.rstrip() != new_body.rstrip()
        if changed:
            p.b = new_body
        return changed
    #@+node:ekr.20240105145241.8: *5* tbo.init_tokens_from_file
    def init_tokens_from_file(self, filename: str) -> tuple[
        str, list[InputToken]
    ]:  # pragma: no cover
        """
        Create the list of tokens for the given file.
        Return (contents, encoding, tokens).
        """
        self.indent_level = 0
        self.filename = filename
        t1 = time.perf_counter_ns()
        contents = g.readFile(filename)
        t2 = time.perf_counter_ns()
        if not contents:
            self.input_tokens = []
            return '', []
        t3 = time.perf_counter_ns()
        self.input_tokens = input_tokens = Tokenizer().make_input_tokens(contents)
        t4 = time.perf_counter_ns()
        if 0:
            print(f"       read: {(t2-t1)/1000000:6.2f} ms")
            print(f"make_tokens: {(t4-t3)/1000000:6.2f} ms")
            print(f"      total: {(t4-t1)/1000000:6.2f} ms")
        return contents, input_tokens
    #@+node:ekr.20240105140814.12: *5* tbo.regularize_newlines
    def regularize_newlines(self, s: str) -> str:
        """Regularize newlines within s."""
        return s.replace('\r\n', '\n').replace('\r', '\n')
    #@+node:ekr.20240105140814.17: *5* tbo.write_file
    def write_file(self, filename: str, s: str) -> None:  # pragma: no cover
        """
        Write the string s to the file whose name is given.

        Handle all exceptions.

        Before calling this function, the caller should ensure
        that the file actually has been changed.
        """
        try:
            s2 = g.toEncodedString(s)  # May raise exception.
            with open(filename, 'wb') as f:
                f.write(s2)
        except Exception as e:  # pragma: no cover
            print(f"Error {e!r}: {filename!r}")
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
        print(f"Diffs for {filename}")
        for line in lines:
            print(line)
    #@+node:ekr.20240105145241.9: *4* tbo: Visitors & generators
    # Visitors (tbo.do_* methods) handle input tokens.
    # Generators (tbo.gen_* methods) create zero or more output tokens.
    #@+node:ekr.20240105145241.10: *5* tbo.do_comment
    def do_comment(self) -> None:
        """Handle a comment token."""
        val = self.input_token.value
        #@+<< do_comment: update comment-related state >>
        #@+node:ekr.20240420034216.1: *6* << do_comment: update comment-related state >>
        # Leo-specific code...
        if self.node_pat.match(val):
            # Clear per-node state.
            self.in_doc_part = False
            self.verbatim = False
            self.decorator_seen = False
            # Do *not* clear other state, which may persist across @others.
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
        #@-<< do_comment: update comment-related state >>

        # Generate the comment.
        self.pending_lws = ''
        self.pending_ws = ''
        entire_line = self.input_token.line.lstrip().startswith('#')
        if entire_line:
            # The comment includes all ws.
            # #1496: No further munging needed.
            val = self.input_token.line.rstrip()
            # #3056: Insure one space after '#' in non-sentinel comments.
            #        Do not change bang lines or '##' comments.
            if m := self.comment_pat.match(val):
                i = len(m.group(1))
                val = val[:i] + '# ' + val[i + 1 :]
        else:
            # Exactly two spaces before trailing comments.
            i = val.find('#')
            if i == -1:
                g.trace('OOPS', repr(val), g.callers())
            # Special case for ###.
            elif val[i:].startswith('###'):
                val = val[:i].rstrip() + '  ### ' + val[i + 3 :].strip()
            else:
                val = val[:i].rstrip() + '  # ' + val[i + 1 :].strip()
        self.gen_token('comment', val.rstrip())
    #@+node:ekr.20240111051726.1: *5* tbo.do_dedent
    def do_dedent(self) -> None:
        """Handle dedent token."""
        # Note: other methods use self.indent_level.
        self.indent_level -= 1
        self.lws = self.indent_level * self.tab_width * ' '
        self.pending_lws = self.lws
        self.pending_ws = ''
        self.prev_output_kind = 'dedent'
    #@+node:ekr.20240105145241.11: *5* tbo.do_encoding
    def do_encoding(self) -> None:
        """Handle the encoding token."""
    #@+node:ekr.20240105145241.12: *5* tbo.do_endmarker
    def do_endmarker(self) -> None:
        """Handle an endmarker token."""

        # Ensure exactly one newline at the end of file.
        if self.prev_output_kind not in (
            'indent', 'dedent', 'line-indent', 'newline',
        ):
            self.output_list.append('\n')
        self.pending_lws = ''  # Defensive.
        self.pending_ws = ''  # Defensive.
    #@+node:ekr.20240105145241.14: *5* tbo.do_indent
    consider_message = 'consider using python/Tools/scripts/reindent.py'

    def do_indent(self) -> None:
        """Handle indent token."""

        # Only warn about indentation errors.
        if '\t' in self.input_token.value:  # pragma: no cover
            print(f"Found tab character in {self.filename}")
            print(self.consider_message)
        elif (len(self.input_token.value) % self.tab_width) != 0:  # pragma: no cover
            print(f"Indentation error in {self.filename}")
            print(self.consider_message)

        # Handle the token!
        new_indent = self.input_token.value
        old_indent = self.indent_level * self.tab_width * ' '
        if new_indent > old_indent:
            self.indent_level += 1
        elif new_indent < old_indent:  # pragma: no cover (defensive)
            print(f"\n===== do_indent: can not happen {new_indent!r}, {old_indent!r}")

        self.lws = new_indent
        self.pending_lws = self.lws
        self.pending_ws = ''
        self.prev_output_kind = 'indent'
    #@+node:ekr.20240105145241.16: *5* tbo.do_name & generators
    #@+node:ekr.20240418050017.1: *6* tbo.do_name
    def do_name(self) -> None:
        """Handle a name token."""
        name = self.input_token.value
        if name in self.operator_keywords:
            self.gen_word_op(name)
        else:
            self.gen_word(name)
    #@+node:ekr.20240105145241.40: *6* tbo.gen_word
    def gen_word(self, s: str) -> None:
        """Add a word request to the code list."""
        assert s == self.input_token.value
        assert s and isinstance(s, str), repr(s)
        self.gen_blank()
        self.gen_token('word', s)
        self.gen_blank()
    #@+node:ekr.20240107141830.1: *6* tbo.gen_word_op
    def gen_word_op(self, s: str) -> None:
        """Add a word-op request to the code list."""
        assert s == self.input_token.value
        assert s and isinstance(s, str), repr(s)
        self.gen_blank()
        self.gen_token('word-op', s)
        self.gen_blank()
    #@+node:ekr.20240105145241.17: *5* tbo.do_newline & do_nl
    #@+node:ekr.20240418043826.1: *6* tbo.do_newline
    def do_newline(self) -> None:
        """
        do_newline: Handle a regular newline.

        From https://docs.python.org/3/library/token.html

        NEWLINE tokens end *logical* lines of Python code.
        """

        # #4349: Remove trailing ws.
        while self.input_tokens:
            last_token = self.input_tokens[-1]
            if last_token.kind == 'ws':
                self.input_tokens.pop()
            else:
                break

        self.output_list.append('\n')
        self.pending_lws = ''  # Set only by 'dedent', 'indent' or 'ws' tokens.
        self.pending_ws = ''
        self.prev_output_kind = 'newline'
        self.prev_output_value = '\n'
    #@+node:ekr.20240418043827.1: *6* tbo.do_nl
    def do_nl(self) -> None:
        """
        do_nl: Handle a continuation line.

        From https://docs.python.org/3/library/token.html

        NL tokens end *physical* lines. They appear when when a logical line of
        code spans multiple physical lines.
        """
        self.do_newline()
    #@+node:ekr.20240105145241.18: *5* tbo.do_number
    def do_number(self) -> None:
        """Handle a number token."""
        self.gen_blank()
        self.gen_token('number', self.input_token.value)
    #@+node:ekr.20240105145241.19: *5* tbo.do_op & generators
    #@+node:ekr.20240418045924.1: *6* tbo.do_op
    def do_op(self) -> None:
        """Handle an op token."""
        val = self.input_token.value

        if val == '.':
            self.gen_dot_op()
        elif val == '@':
            self.gen_token('op-no-blanks', val)
            self.push_state('decorator')
        elif val == ':':
            # Treat slices differently.
            self.gen_colon()
        elif val in ',;':
            # Pep 8: Avoid extraneous whitespace immediately before
            # comma, semicolon, or colon.
            self.pending_ws = ''
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
        val = self.input_token.value
        context = self.input_token.context

        self.pending_ws = ''
        if context == 'complex-slice':
            if self.prev_output_value not in '[:':
                self.gen_blank()
            self.gen_token('op', val)
            self.gen_blank()
        elif context == 'simple-slice':
            self.gen_token('op-no-blanks', val)
        elif context == 'dict':
            self.gen_token('op', val)
            self.gen_blank()
        else:
            self.gen_token('op', val)
            self.gen_blank()
    #@+node:ekr.20240109035004.1: *6* tbo.gen_dot_op & _next
    def gen_dot_op(self) -> None:
        """Handle the '.' input token."""
        context = self.input_token.context

        # Get the previous significant **input** token.
        # This is the only call to next(i) anywhere!
        next_i = self._next(self.index)
        next = 'None' if next_i is None else self.input_tokens[next_i]
        import_is_next = next and next.kind == 'name' and next.value == 'import'  # type:ignore

        if context == 'import':
            if (
                self.prev_output_kind == 'word'
                and self.prev_output_value in ('from', 'import')
            ):
                self.gen_blank()
                op = 'op' if import_is_next else 'op-no-blanks'
                self.gen_token(op, '.')
            elif import_is_next:
                self.gen_token('op', '.')
                self.gen_blank()
            else:
                self.pending_ws = ''
                self.gen_token('op-no-blanks', '.')
        else:
            self.pending_ws = ''
            self.gen_token('op-no-blanks', '.')
    #@+node:ekr.20240105145241.43: *7* tbo._next
    def _next(self, i: int) -> Optional[int]:
        """
        Return the next *significant* input token.

        Ignore insignificant tokens: whitespace, indentation, comments, etc.

        The **Global Token Ratio** is tbo.n_scanned_tokens / len(tbo.tokens),
        where tbo.n_scanned_tokens is the total number of calls calls to
        tbo.next or tbo.prev.

        For Leo's sources, this ratio ranges between 0.48 and 1.51!

        The orange_command function warns if this ratio is greater than 2.5.
        Previous versions of this code suffered much higher ratios.
        """
        i += 1
        while i < len(self.input_tokens):
            token = self.input_tokens[i]
            if token.kind not in self.insignificant_tokens:
                # g.trace(f"token: {token!r}")
                return i
            i += 1
        return None  # pragma: no cover
    #@+node:ekr.20240105145241.20: *6* tbo.gen_equal_op
    def gen_equal_op(self) -> None:

        val = self.input_token.value
        context = self.input_token.context

        if context == 'initializer':
            # Pep 8: Don't use spaces around the = sign when used to indicate
            #        a keyword argument or a default parameter value.
            #        However, when combining an argument annotation with a default value,
            #        *do* use spaces around the = sign.
            self.pending_ws = ''
            self.gen_token('op-no-blanks', val)
        else:
            self.gen_blank()
            self.gen_token('op', val)
            self.gen_blank()
    #@+node:ekr.20240105145241.35: *6* tbo.gen_lt
    def gen_lt(self) -> None:
        """Generate code for a left paren or curly/square bracket."""
        val = self.input_token.value
        assert val in '([{', repr(val)

        # Update state vars.
        if val == '(':
            self.paren_level += 1
        elif val == '[':
            self.square_brackets_stack.append(False)
        else:
            self.curly_brackets_level += 1

        # Generate or suppress the leading blank.
        # Update self.in_arg_list if necessary.
        if self.input_token.context == 'import':
            self.gen_blank()
        elif self.prev_output_kind in ('op', 'word-op'):
            self.gen_blank()
        elif self.prev_output_kind == 'word':
            # Only suppress blanks before '(' or '[' for non-keywords.
            if val == '{' or self.prev_output_value in (
                'if', 'else', 'elif', 'return', 'for', 'while',
            ):
                self.gen_blank()
            elif val == '(':
                self.in_arg_list += 1
                self.pending_ws = ''
            else:
                self.pending_ws = ''
        elif self.prev_output_kind != 'line-indent':
            self.pending_ws = ''

        # Output the token!
        self.gen_token('op-no-blanks', val)
    #@+node:ekr.20240105145241.37: *6* tbo.gen_possible_unary_op & helper
    def gen_possible_unary_op(self) -> None:
        """Add a unary or binary op to the token list."""
        val = self.input_token.value
        if self.is_unary_op(self.index, val):
            prev = self.input_token
            if prev.kind == 'lt':
                self.gen_token('op-no-blanks', val)
            else:
                self.gen_blank()
                self.gen_token('op-no-blanks', val)
        else:
            self.gen_blank()
            self.gen_token('op', val)
            self.gen_blank()

    #@+node:ekr.20240109082712.1: *7* tbo.is_unary_op & _prev
    def is_unary_op(self, i: int, val: str) -> bool:

        if val == '~':
            return True
        if val not in '+-':  # pragma: no cover
            return False

        # Get the previous significant **input** token.
        # This is the only call to _prev(i) anywhere!
        prev_i = self._prev(i)
        prev_token = None if prev_i is None else self.input_tokens[prev_i]
        kind = prev_token.kind if prev_token else ''
        value = prev_token.value if prev_token else ''

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
    #@+node:ekr.20240115233050.1: *8* tbo._prev
    def _prev(self, i: int) -> Optional[int]:
        """
        Return the previous *significant* input token.

        Ignore insignificant tokens: whitespace, indentation, comments, etc.
        """
        i -= 1
        while i >= 0:
            token = self.input_tokens[i]
            if token.kind not in self.insignificant_tokens:
                return i
            i -= 1
        return None  # pragma: no cover
    #@+node:ekr.20240105145241.36: *6* tbo.gen_rt
    def gen_rt(self) -> None:
        """Generate code for a right paren or curly/square bracket."""
        val = self.input_token.value
        assert val in ')]}', repr(val)

        # Update state vars.
        if val == ')':
            self.paren_level -= 1
            self.in_arg_list = max(0, self.in_arg_list - 1)
            if self.prev_output_kind != 'line-indent':
                self.pending_ws = ''
        elif val == ']':
            self.square_brackets_stack.pop()
            if self.prev_output_kind != 'line-indent':
                self.pending_ws = ''
        else:
            self.curly_brackets_level -= 1
            # A hack: put a space before a comma.
            last = self.output_list[-1]
            if last == ',':
                self.pending_ws = ' '
            elif self.prev_output_kind != 'line-indent':
                self.pending_ws = ''
        self.gen_token('rt', val)
    #@+node:ekr.20240105145241.38: *6* tbo.gen_star_op
    def gen_star_op(self) -> None:
        """Put a '*' op, with special cases for *args."""
        val = self.input_token.value
        context = self.input_token.context

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
        val = self.input_token.value
        context = self.input_token.context

        if context == 'arg':
            self.gen_blank()
            self.gen_token('op-no-blanks', val)
        else:
            self.gen_blank()
            self.gen_token('op', val)
            self.gen_blank()
    #@+node:ekr.20240105145241.3: *6* tbo.push_state
    def push_state(self, kind: str, value: Union[int, str, None] = None) -> None:
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
        val = self.regularize_newlines(self.input_token.value)
        if val.startswith(('"""', "'''")):
            # #4346: Strip trailing ws in docstrings.
            while ' \n' in val:
                val = val.replace(' \n', '\n')
        self.gen_token('string', val)
        self.gen_blank()
    #@+node:ekr.20240105145241.22: *5* tbo.do_verbatim
    def do_verbatim(self) -> None:
        """
        Handle one token in verbatim mode.
        End verbatim mode when the appropriate comment is seen.
        """
        kind = self.input_token.kind
        #
        # Careful: tokens may contain '\r'
        val = self.regularize_newlines(self.input_token.value)
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
        val = self.input_token.value
        last_token = self.input_tokens[self.index - 1]

        if last_token.kind in ('nl', 'newline'):
            self.pending_lws = val
            self.pending_ws = ''
        elif '\\\n' in val:
            self.pending_lws = ''
            self.pending_ws = val
        else:
            self.pending_ws = ' ' if val else ''  # #4346.
    #@+node:ekr.20240105145241.27: *5* tbo.gen_blank
    def gen_blank(self) -> None:
        """
        Queue a *request* for a blank.
        Change *neither* prev_output_kind *nor* pending_lws.
        """
        prev_kind = self.prev_output_kind
        if prev_kind == 'op-no-blanks':
            # A demand that no blank follows this op.
            self.pending_ws = ''
        elif prev_kind == 'hard-blank':
            # Eat any further blanks.
            self.pending_ws = ''
        elif prev_kind in (
            'dedent',
            'file-start',
            'indent',
            'line-indent',
            'newline',
        ):
            # Suppress the blank, but do *not* change the pending ws.
            pass
        elif self.pending_ws:
            # Use the existing pending ws.
            pass
        else:
            self.pending_ws = ' '
    #@+node:ekr.20240105145241.26: *5* tbo.gen_token
    def gen_token(self, kind: str, value: str) -> None:
        """Add an output token to the code list."""

        if self.pending_lws:
            self.output_list.append(self.pending_lws)
        elif self.pending_ws:
            self.output_list.append(self.pending_ws)

        self.output_list.append(value)
        self.pending_lws = ''
        self.pending_ws = ''
        self.prev_output_value = value
        self.prev_output_kind = kind
    #@+node:ekr.20240110205127.1: *4* tbo: Scanning
    # The parser calls scanner methods to move through the list of input tokens.
    #@+node:ekr.20240128114622.1: *5* tbo.pre_scan & helpers
    def pre_scan(self) -> None:
        """
        Scan the entire file in one iterative pass, adding context to a few
        kinds of tokens as follows:

        Token   Possible Contexts (or None)
        =====   ===========================
        ':'     'annotation', 'dict', 'complex-slice', 'simple-slice'
        '='     'annotation', 'initializer'
        '*'     'arg'
        '**'    'arg'
        '.'     'import'
        """

        # The main loop.
        in_import = False
        scan_stack: list[ScanState] = []
        prev_token: Optional[InputToken] = None
        for i, token in enumerate(self.input_tokens):
            kind, value = token.kind, token.value
            if kind in 'newline':
                #@+<< pre-scan 'newline' tokens >>
                #@+node:ekr.20240128230812.1: *6* << pre-scan 'newline' tokens >>
                # 'import' and 'from x import' statements may span lines.
                # 'ws' tokens represent continued lines like this:   ws: ' \\\n    '
                if in_import and not scan_stack:
                    in_import = False
                #@-<< pre-scan 'newline' tokens >>
            elif kind == 'op':
                #@+<< pre-scan 'op' tokens >>
                #@+node:ekr.20240128123117.1: *6* << pre-scan 'op' tokens >>
                top_state: Optional[ScanState] = scan_stack[-1] if scan_stack else None

                # Handle '[' and ']'.
                if value == '[':
                    scan_stack.append(ScanState('slice', token))
                elif value == ']':
                    assert top_state and top_state.kind == 'slice'
                    self.finish_slice(i, top_state)
                    scan_stack.pop()

                # Handle '{' and '}'.
                if value == '{':
                    scan_stack.append(ScanState('dict', token))
                elif value == '}':
                    assert top_state and top_state.kind == 'dict'
                    self.finish_dict(i, top_state)
                    scan_stack.pop()

                # Handle '(' and ')'
                elif value == '(':
                    if self.is_python_keyword(prev_token) or prev_token and prev_token.kind != 'name':
                        state_kind = '('
                    else:
                        state_kind = 'arg'
                    scan_stack.append(ScanState(state_kind, token))
                elif value == ')':
                    assert top_state and top_state.kind in ('(', 'arg'), repr(top_state)
                    if top_state.kind == 'arg':
                        self.finish_arg(i, top_state)
                    else:
                        self.finish_paren(i, top_state)
                    scan_stack.pop()

                # Handle interior tokens in 'arg' and 'slice' states.
                if top_state:
                    if top_state.kind in ('dict', 'slice') and value == ':':
                        top_state.value.append(i)
                    if top_state.kind == 'arg' and value in '**=:,':
                        top_state.value.append(i)

                # Handle '.' and '(' tokens inside 'import' and 'from' statements.
                if in_import and value in '(.':
                    self.set_context(i, 'import')
                #@-<< pre-scan 'op' tokens >>
            elif kind == 'name':
                #@+<< pre-scan 'name' tokens >>
                #@+node:ekr.20240128231119.1: *6* << pre-scan 'name' tokens >>
                prev_is_yield = prev_token and prev_token.kind == 'name' and prev_token.value == 'yield'
                if value in ('from', 'import') and not prev_is_yield:
                    # 'import' and 'from x import' statements should be at the outer level.
                    assert not scan_stack, scan_stack
                    in_import = True
                #@-<< pre-scan 'name' tokens >>
            # Remember the previous significant token.
            if kind not in self.insignificant_kinds:
                prev_token = token
        # Sanity check.
        if scan_stack:  # pragma: no cover
            print('pre_scan: non-empty scan_stack')
            print(scan_stack)
    #@+node:ekr.20240129041304.1: *6* tbo.finish_arg
    def finish_arg(self, end: int, state: Optional[ScanState]) -> None:
        """Set context for '=', ':', '*', and '**' tokens when scanning from '(' to ')'."""

        # Sanity checks.
        if not state:
            return
        assert state.kind == 'arg', repr(state)
        token = state.token
        assert token.value == '(', repr(token)
        values = state.value
        assert isinstance(values, list), repr(values)
        i1 = token.index
        assert i1 < end, (i1, end)
        if not values:
            return

        # Compute the context for each *separate* '=' token.
        equal_context = 'initializer'
        for i in values:
            token = self.input_tokens[i]
            assert token.kind == 'op', repr(token)
            if token.value == ',':
                equal_context = 'initializer'
            elif token.value == ':':
                equal_context = 'annotation'
            elif token.value == '=':
                self.set_context(i, equal_context)
                equal_context = 'initializer'

        # Set the context of all outer-level ':', '*', and '**' tokens.
        prev: Optional[InputToken] = None
        for i in range(i1, end):
            token = self.input_tokens[i]
            if token.kind not in self.insignificant_kinds:
                if token.kind == 'op':
                    if token.value in ('*', '**'):
                        if self.is_unary_op_with_prev(prev, token):
                            self.set_context(i, 'arg')
                    elif token.value == '=':
                        # The code above has set the context.
                        assert token.context in ('initializer', 'annotation'), (i, repr(token.context))
                    elif token.value == ':':
                        self.set_context(i, 'annotation')
                prev = token
    #@+node:ekr.20250507041900.1: *6* tbo.finish_paren
    def finish_paren(self, end: int, state: Optional[ScanState]) -> None:
        """Set context for '=' tokens when scanning from '(' to ')'."""

        # Sanity checks.
        if not state:
            return
        assert state.kind == '(', repr(state)
        token = state.token
        assert token.value == '(', repr(token)
        i1 = token.index
        assert i1 < end, (i1, end)

        # Compute the context for each *separate* '=' token.
        for token in self.input_tokens[i1:end]:
            if token.kind == 'op' and token.value == '=':
                self.set_context(token.index, 'initializer')
    #@+node:ekr.20240128233406.1: *6* tbo.finish_slice
    def finish_slice(self, end: int, state: ScanState) -> None:
        """Set context for all ':' when scanning from '[' to ']'."""

        # Sanity checks.
        assert state.kind == 'slice', repr(state)
        token = state.token
        assert token.value == '[', repr(token)
        colons = state.value
        assert isinstance(colons, list), repr(colons)
        i1 = token.index
        assert i1 < end, (i1, end)

        # Do nothing if there are no ':' tokens in the slice.
        if not colons:
            return

        # Compute final context by scanning the tokens.
        final_context = 'simple-slice'
        inter_colon_tokens = 0
        prev = token
        for i in range(i1 + 1, end - 1):
            token = self.input_tokens[i]
            kind, value = token.kind, token.value
            if kind not in self.insignificant_kinds:
                if kind == 'op':
                    if value == '.':
                        # Ignore '.' tokens and any preceding 'name' token.
                        if prev and prev.kind == 'name':  # pragma: no cover
                            inter_colon_tokens -= 1
                    elif value == ':':
                        inter_colon_tokens = 0
                    elif value in '-+':
                        # Ignore unary '-' or '+' tokens.
                        if not self.is_unary_op_with_prev(prev, token):
                            inter_colon_tokens += 1
                            if inter_colon_tokens > 1:
                                final_context = 'complex-slice'
                                break
                    elif value == '~':
                        # '~' is always a unary op.
                        pass
                    else:
                        # All other ops contribute.
                        inter_colon_tokens += 1
                        if inter_colon_tokens > 1:
                            final_context = 'complex-slice'
                            break
                else:
                    inter_colon_tokens += 1
                    if inter_colon_tokens > 1:
                        final_context = 'complex-slice'
                        break
                prev = token

        # Set the context of all outer-level ':' tokens.
        for i in colons:
            self.set_context(i, final_context)
    #@+node:ekr.20240129040347.1: *6* tbo.finish_dict
    def finish_dict(self, end: int, state: Optional[ScanState]) -> None:
        """
        Set context for all ':' when scanning from '{' to '}'

        Strictly speaking, setting this context is unnecessary because
        tbo.gen_colon generates the same code regardless of this context.

        In other words, this method can be a do-nothing!
        """

        # Sanity checks.
        if not state:
            return
        assert state.kind == 'dict', repr(state)
        token = state.token
        assert token.value == '{', repr(token)
        colons = state.value
        assert isinstance(colons, list), repr(colons)
        i1 = token.index
        assert i1 < end, (i1, end)

        # Set the context for all ':' tokens.
        for i in colons:
            self.set_context(i, 'dict')
    #@+node:ekr.20240129034209.1: *5* tbo.is_unary_op_with_prev
    def is_unary_op_with_prev(self, prev: Optional[InputToken], token: InputToken) -> bool:
        """
        Return True if token is a unary op in the context of prev, the previous
        significant token.
        """
        if token.value == '~':  # pragma: no cover
            return True
        if prev is None:
            return True  # pragma: no cover
        assert token.value in '**-+', repr(token.value)
        if prev.kind in ('number', 'string'):
            return_val = False
        elif prev.kind == 'op' and prev.value in ')]':
            # An unnecessary test?
            return_val = False  # pragma: no cover
        elif prev.kind == 'op' and prev.value in '{([:,':
            return_val = True
        elif prev.kind != 'name':
            # An unnecessary test?
            return_val = True  # pragma: no cover
        else:
            # prev is a'name' token.
            return self.is_python_keyword(token)
        return return_val
    #@+node:ekr.20240129035336.1: *5* tbo.is_python_keyword
    def is_python_keyword(self, token: Optional[InputToken]) -> bool:
        """Return True if token is a 'name' token referring to a Python keyword."""
        if not token or token.kind != 'name':
            return False
        return keyword.iskeyword(token.value) or keyword.issoftkeyword(token.value)
    #@+node:ekr.20240106170746.1: *5* tbo.set_context
    def set_context(self, i: int, context: str) -> None:
        """
        Set self.input_tokens[i].context, but only if it does not already exist!

        See the docstring for pre_scan for details.
        """

        trace = False  # Do not delete the trace below.

        valid_contexts = (
            'annotation', 'arg', 'complex-slice', 'simple-slice',
            'dict', 'import', 'initializer',
        )
        if context not in valid_contexts:
            self.oops(f"Unexpected context! {context!r}")  # pragma: no cover

        token = self.input_tokens[i]

        if trace:  # pragma: no cover
            token_s = f"<{token.kind}: {token.show_val(12)}>"
            ignore_s = 'Ignore' if token.context else ' ' * 6
            print(f"{i:3} {ignore_s} token: {token_s} context: {context}")

        if not token.context:
            token.context = context
    #@-others
#@-others

if __name__ == '__main__':
    main()  # pragma: no cover

#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
