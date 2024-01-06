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
import textwrap
import tokenize
from typing import Any, Generator, Optional, Union

try:
    from leo.core import leoGlobals as g
except Exception:
    # check_g function gives the message.
    g = None

Node = ast.AST
Settings = Optional[dict[str, Any]]
#@-<< leoTokens.py: imports & annotations >>

#@+others
#@+node:ekr.20240105140814.5: ** command: orange_command
def orange_command(
    files: list[str],
    settings: Settings = None,
) -> None:  # pragma: no cover

    if not check_g():
        return
    for filename in files:
        if os.path.exists(filename):
            # print(f"orange {filename}")
            TokenBasedOrange(settings).beautify_file(filename)
        else:
            print(f"file not found: {filename}")
    # print(f"Beautify done: {len(files)} files")
#@+node:ekr.20240105140814.7: ** leoTokens: functions
if 1:  # pragma: no cover
    #@+others
    #@+node:ekr.20240105140814.8: *3* function: check_g
    def check_g() -> bool:
        """print an error message if g is None"""
        if not g:
            print('This statement failed: `from leo.core import leoGlobals as g`')
            print('Please adjust your Python path accordingly')
        return bool(g)
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
        print("Note: values shown are repr(value) *except* for 'string' and 'fstring*' tokens.")
        tokens[0].dump_header()
        for z in tokens:
            print(z.dump())
        print('')
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
            result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
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
    #@+node:ekr.20240105140814.12: *3* function: regularize_nls
    def regularize_nls(s: str) -> str:
        """Regularize newlines within s."""
        return s.replace('\r\n', '\n').replace('\r', '\n')
    #@+node:ekr.20240105140814.17: *3* function: write_file
    def write_file(filename: str, s: str, encoding: str = 'utf-8') -> None:
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
    #@-others
#@+node:ekr.20240105140814.52: ** Classes
#@+node:ekr.20240105140814.51: *3* class BeautifyError(Exception)
class BeautifyError(Exception):
    """Leading tabs found."""
#@+node:ekr.20240105140814.53: *3* class InputToken
class InputToken:
    """
    A class representing an Orange input token.
    """

    def __init__(self, kind: str, value: str):
        # Basic data.
        self.kind = kind
        self.value = value
        # Context data.
        self.context: dict[str, Any] = {}  # Injected context data.
        self.level = 0
        # Debugging data.
        self.index = 0
        self.line = ''  # The entire line containing the token.
        self.line_number = 0  # The line number, for errors and dumps.

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
#@+node:ekr.20240105143307.1: *3* class Tokenizer
class Tokenizer:
    """Create a list of InputTokens from contents."""

    results: list[InputToken] = []

    #@+others
    #@+node:ekr.20240105143307.2: *4* itok.add_token
    token_index = 0
    prev_line_token = None

    def add_token(self, kind: str, five_tuple: tuple, line: str, s_row: int, value: str) -> None:
        """
        Add an InputToken to the results list.
        """
        tok = InputToken(kind, value)
        tok.index = self.token_index
        # Bump the token index.
        self.token_index += 1
        tok.line = line
        tok.line_number = s_row
        self.results.append(tok)
    #@+node:ekr.20240105143214.2: *4* itok.check_results
    def check_results(self, contents: str) -> None:

        # Split the results into lines.
        result = ''.join([z.to_string() for z in self.results])
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
    def create_input_tokens(self, contents: str, five_tuples: Generator) -> list[InputToken]:
        """
        InputTokenizer.create_input_tokens.

        Return list of InputToken's from tokens, a list of 5-tuples.
        """
        # Create the physical lines.
        self.lines = contents.splitlines(True)

        # Create the list of character offsets of the start of each physical line.
        last_offset, self.offsets = 0, [0]
        for line in self.lines:
            last_offset += len(line)
            self.offsets.append(last_offset)
        # Handle each token, appending tokens and between-token whitespace to results.
        self.prev_offset, self.results = -1, []
        for five_tuple in five_tuples:
            # Subclsasses create lists of Tokens or InputTokens.
            self.do_token(contents, five_tuple)
        # Print results when tracing.
        self.check_results(contents)
        # Return results, as a list.
        return self.results
    #@+node:ekr.20240105143214.5: *4* itok.do_token (the gem)
    header_has_been_shown = False

    def do_token(self, contents: str, five_tuple: tuple) -> None:
        """
        Handle the given token, optionally including between-token whitespace.

        This is part of the "gem".

        Note: this method creates tokens using the *overridden* add_token method.

        Links:

        - 11/13/19: ENB: A much better untokenizer
          https://groups.google.com/forum/#!msg/leo-editor/DpZ2cMS03WE/VPqtB9lTEAAJ

        - Untokenize does not round-trip ws before bs-nl
          https://bugs.python.org/issue38663
        """
        import token as token_module
        # Unpack..
        tok_type, val, start, end, line = five_tuple
        s_row, s_col = start  # row/col offsets of start of token.
        e_row, e_col = end  # row/col offsets of end of token.
        kind = token_module.tok_name[tok_type].lower()
        # Calculate the token's start/end offsets: character offsets into contents.
        s_offset = self.offsets[max(0, s_row - 1)] + s_col
        e_offset = self.offsets[max(0, e_row - 1)] + e_col
        # tok_s is corresponding string in the line.
        tok_s = contents[s_offset:e_offset]
        # Add any preceding between-token whitespace.
        ws = contents[self.prev_offset:s_offset]
        if ws:
            # No need for a hook.
            self.add_token('ws', five_tuple, line, s_row, ws)
        # Always add token, even if it contributes no text!
        self.add_token(kind, five_tuple, line, s_row, tok_s)
        # Update the ending offset.
        self.prev_offset = e_offset
    #@+node:ekr.20240105143214.6: *4* itok.make_input_tokens
    def make_input_tokens(self, contents: str) -> list[InputToken]:
        """
        Return a list (not a generator) of InputToken objects corresponding to the
        list of 5-tuples generated by tokenize.tokenize.

        Perform consistency checks and handle all exceptions.

        Called from unit tests.
        """
        try:
            # Use Python's tokenizer module
            five_tuples = tokenize.tokenize(
                io.BytesIO(contents.encode('utf-8')).readline)
        except Exception:
            print('make_tokens: exception in tokenize.tokenize')
            g.es_exception()
            return None
        tokens = self.create_input_tokens(contents, five_tuples)
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
        do_dendent():   pops the stack once or twice if state.value == self.level.

    """

    def __init__(self, kind: str, value: Union[int, str]) -> None:
        self.kind = kind
        self.value = value

    def __repr__(self) -> str:
        return f"State: {self.kind} {self.value!r}"  # pragma: no cover

    __str__ = __repr__
#@+node:ekr.20240105145241.1: *3* class TokenBasedOrange
class TokenBasedOrange:
    """
    A flexible and powerful beautifier for Python.
    Orange is the new black.

    This is a *completely token-based* beautifier.
    
    The Orange class in leoAst.py uses data from Python's parse tree.
    """
    # This switch is really a comment. It will always be false.
    # It marks the code that simulates the operation of the black tool.
    black_mode = False

    # Patterns...
    nobeautify_pat = re.compile(r'\s*#\s*pragma:\s*no\s*beautify\b|#\s*@@nobeautify')

    # Patterns from FastAtRead class, specialized for python delims.
    node_pat = re.compile(r'^(\s*)#@\+node:([^:]+): \*(\d+)?(\*?) (.*)$')  # @node
    start_doc_pat = re.compile(r'^\s*#@\+(at|doc)?(\s.*?)?$')  # @doc or @
    at_others_pat = re.compile(r'^(\s*)#@(\+|-)others\b(.*)$')  # @others

    # Doc parts end with @c or a node sentinel. Specialized for python.
    end_doc_pat = re.compile(r"^\s*#@(@(c(ode)?)|([+]node\b.*))$")

    #@+others
    #@+node:ekr.20240105145241.2: *4* tbo.ctor
    def __init__(self, settings: Settings = None):
        """Ctor for Orange class."""
        if settings is None:
            settings = {}
        valid_keys = (
            'allow_joined_strings',
            'force',
            'max_join_line_length',
            'max_split_line_length',
            'orange',
            'tab_width',
            'verbose',
        )
        # For mypy...
        self.kind: str = ''
        # Default settings...
        self.allow_joined_strings = False  # EKR's preference.
        self.force = False
        self.max_join_line_length = 88
        self.max_split_line_length = 88
        self.tab_width = 4
        self.verbose = False
        # Override from settings dict...
        for key in settings:  # pragma: no cover
            value = settings.get(key)
            if key in valid_keys and value is not None:
                setattr(self, key, value)
            else:
                g.trace(f"Unexpected setting: {key} = {value!r}")
    #@+node:ekr.20240105145241.4: *4* tbo: Entries & helpers
    #@+node:ekr.20240105145241.5: *5* tbo.beautify (main token loop)
    def oops(self) -> None:  # pragma: no cover
        g.trace(f"Unknown kind: {self.kind}")

    def beautify(self,
        contents: str,
        filename: str,
        tokens: list[InputToken],
        max_join_line_length: Optional[int] = None,
        max_split_line_length: Optional[int] = None,
    ) -> str:
        """
        The main line. Create output tokens and return the result as a string.

        beautify_file and beautify_file_def call this method.
        """
        # Config overrides
        if max_join_line_length is not None:
            self.max_join_line_length = max_join_line_length
        if max_split_line_length is not None:
            self.max_split_line_length = max_split_line_length
        # State vars...
        self.curly_brackets_level = 0  # Number of unmatched '{' tokens.
        self.decorator_seen = False  # Set by do_name for do_op.
        self.in_arg_list = 0  # > 0 if in an arg list of a def.
        self.in_fstring = False  # True: scanning an f-string.
        self.index = 0  # The index within the tokens array of the token being scanned.
        self.level = 0  # Set only by do_indent and do_dedent.
        self.lws = ''  # Leading whitespace.
        self.paren_level = 0  # Number of unmatched '(' tokens.
        self.square_brackets_stack: list[bool] = []  # A stack of bools, for self.word().
        self.state_stack: list["ParseState"] = []  # Stack of ParseState objects.
        self.tokens = tokens  # The list of input tokens.
        self.val = None  # The input token's value (a string).
        self.verbatim = False  # True: don't beautify.
        #
        # Init output list and state...
        self.code_list: list[OutputToken] = []  # The list of output tokens.
        self.tokens = tokens  # The list of input tokens.
        self.add_token('file-start', '')
        self.push_state('file-start')
        for self.index, token in enumerate(tokens):
            self.token = token
            self.kind, self.val, self.line = token.kind, token.value, token.line
            if self.verbatim:
                self.do_verbatim()
            elif self.in_fstring:
                self.continue_fstring()
            else:
                func = getattr(self, f"do_{token.kind}", self.oops)
                func()
        # Any post pass would go here.
        return output_tokens_to_string(self.code_list)
    #@+node:ekr.20240105145241.6: *5* tbo.beautify_file (entry)
    def beautify_file(self, filename: str) -> bool:  # pragma: no cover
        """
        Orange: Beautify the the given external file.

        Return True if the file was changed.
        """
        self.filename = filename
        contents, encoding, tokens = self.init_tokens_from_file(filename)
        if not (contents and tokens):
            return False  # Not an error.
        assert isinstance(tokens[0], InputToken), repr(tokens[0])
        try:
            results = self.beautify(contents, filename, tokens)
        except BeautifyError:
            return False  # #2578.
        # Something besides newlines must change.
        if regularize_nls(contents) == regularize_nls(results):
            return False
        # Write the results
        print(f"Beautified: {g.shortFileName(filename)}")
        write_file(filename, results, encoding=encoding)
        return True
    #@+node:ekr.20240105145241.8: *5* tbo.init_tokens_from_file
    def init_tokens_from_file(self, filename: str) -> tuple[
        str, str, list[InputToken]
    ]:  # pragma: no cover
        """
        Create the list of tokens for the given file.
        Return (contents, encoding, tokens).
        """
        self.level = 0
        self.filename = filename
        contents, encoding = g.readFileIntoString(filename)
        if not contents:
            return None, None, None
        self.tokens = tokens = Tokenizer().make_input_tokens(contents)
        return contents, encoding, tokens
    #@+node:ekr.20240105145241.3: *5* tbo.push_state
    def push_state(self, kind: str, value: Union[int, str] = None) -> None:
        """Append a state to the state stack."""
        state = ParseState(kind, value)
        self.state_stack.append(state)
    #@+node:ekr.20240105145241.9: *4* tbo: Input token handlers
    #@+node:ekr.20240105145241.10: *5* tbo.do_comment
    in_doc_part = False

    comment_pat = re.compile(r'^(\s*)#[^@!# \n]')

    def do_comment(self) -> None:
        """Handle a comment token."""
        val = self.val
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
                # self.level = 0
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
        entire_line = self.line.lstrip().startswith('#')
        if entire_line:
            self.clean('hard-blank')
            self.clean('line-indent')
            # #1496: No further munging needed.
            val = self.line.rstrip()
            # #3056: Insure one space after '#' in non-sentinel comments.
            #        Do not change bang lines or '##' comments.
            if m := self.comment_pat.match(val):
                i = len(m.group(1))
                val = val[:i] + '# ' + val[i + 1 :]
        else:
            # Exactly two spaces before trailing comments.
            val = '  ' + self.val.rstrip()
        self.add_token('comment', val)
    #@+node:ekr.20240105145241.11: *5* tbo.do_encoding
    def do_encoding(self) -> None:
        """
        Handle the encoding token.
        """
        pass
    #@+node:ekr.20240105145241.12: *5* tbo.do_endmarker
    def do_endmarker(self) -> None:
        """Handle an endmarker token."""
        # Ensure exactly one blank at the end of the file.
        self.clean_blank_lines()
        self.add_token('line-end', '\n')
    #@+node:ekr.20240105145241.13: *5* tbo.do_fstring_start & continue_fstring
    def do_fstring_start(self) -> None:
        """Handle the 'fstring_start' token. Enter f-string mode."""
        self.in_fstring = True
        self.add_token('verbatim', self.val)

    def continue_fstring(self) -> None:
        """
        Put the next token in f-fstring mode.
        Exit f-string mode if the token is 'fstring_end'.
        """
        self.add_token('verbatim', self.val)
        if self.kind == 'fstring_end':
            self.in_fstring = False
    #@+node:ekr.20240105145241.14: *5* tbo.do_indent & do_dedent & helper
    # Note: other methods use self.level.

    def do_dedent(self) -> None:
        """Handle dedent token."""
        self.level -= 1
        self.lws = self.level * self.tab_width * ' '
        self.line_indent()
        if self.black_mode:  # pragma: no cover (black)
            state = self.state_stack[-1]
            if state.kind == 'indent' and state.value == self.level:
                self.state_stack.pop()
                state = self.state_stack[-1]
                if state.kind in ('class', 'def'):
                    self.state_stack.pop()
                    self.handle_dedent_after_class_or_def(state.kind)

    def do_indent(self) -> None:
        """Handle indent token."""
        # #2578: Refuse to beautify files containing leading tabs or unusual indentation.
        consider_message = 'consider using python/Tools/scripts/reindent.py'
        if '\t' in self.val:  # pragma: no cover
            message = f"Leading tabs found: {self.filename}"
            print(message)
            print(consider_message)
            raise BeautifyError(message)
        if (len(self.val) % self.tab_width) != 0:  # pragma: no cover
            message = f" Indentation error: {self.filename}"
            print(message)
            print(consider_message)
            raise BeautifyError(message)
        new_indent = self.val
        old_indent = self.level * self.tab_width * ' '
        if new_indent > old_indent:
            self.level += 1
        elif new_indent < old_indent:  # pragma: no cover (defensive)
            g.trace('\n===== can not happen', repr(new_indent), repr(old_indent))
        self.lws = new_indent
        self.line_indent()
    #@+node:ekr.20240105145241.15: *6* tbo.handle_dedent_after_class_or_def
    def handle_dedent_after_class_or_def(self, kind: str) -> None:  # pragma: no cover (black)
        """
        Insert blank lines after a class or def as the result of a 'dedent' token.

        Normal comment lines may precede the 'dedent'.
        Insert the blank lines *before* such comment lines.
        """
        #
        # Compute the tail.
        i = len(self.code_list) - 1
        tail: list[OutputToken] = []
        while i > 0:
            t = self.code_list.pop()
            i -= 1
            if t.kind == 'line-indent':
                pass
            elif t.kind == 'line-end':
                tail.insert(0, t)
            elif t.kind == 'comment':
                # Only underindented single-line comments belong in the tail.
                # at+node comments must never be in the tail.
                single_line = self.code_list[i].kind in ('line-end', 'line-indent')
                lws = len(t.value) - len(t.value.lstrip())
                underindent = lws <= len(self.lws)
                if underindent and single_line and not self.node_pat.match(t.value):
                    # A single-line comment.
                    tail.insert(0, t)
                else:
                    self.code_list.append(t)
                    break
            else:
                self.code_list.append(t)
                break
        #
        # Remove leading 'line-end' tokens from the tail.
        while tail and tail[0].kind == 'line-end':
            tail = tail[1:]
        #
        # Put the newlines *before* the tail.
        # For Leo, always use 1 blank lines.
        n = 1  # n = 2 if kind == 'class' else 1
        # Retain the token (intention) for debugging.
        self.add_token('blank-lines', n)
        for _i in range(0, n + 1):
            self.add_token('line-end', '\n')
        if tail:
            self.code_list.extend(tail)
        self.line_indent()
    #@+node:ekr.20240105145241.16: *5* tbo.do_name
    def do_name(self) -> None:
        """Handle a name token."""
        name = self.val
        if self.black_mode and name in ('class', 'def'):  # pragma: no cover (black)
            # Handle newlines before and after 'class' or 'def'
            self.decorator_seen = False
            state = self.state_stack[-1]
            if state.kind == 'decorator':
                # Always do this, regardless of @bool clean-blank-lines.
                self.clean_blank_lines()
                # Suppress split/join.
                self.add_token('hard-newline', '\n')
                self.add_token('line-indent', self.lws)
                self.state_stack.pop()
            else:
                # Always do this, regardless of @bool clean-blank-lines.
                self.blank_lines(2 if name == 'class' else 1)
            self.push_state(name)
            # For trailing lines after inner classes/defs.
            self.push_state('indent', self.level)
            self.word(name)
            return
        #
        # Leo mode...
        if name in ('class', 'def'):
            self.word(name)
        elif name in (
            'and', 'elif', 'else', 'for', 'if', 'in', 'not', 'not in', 'or', 'while'
        ):
            self.word_op(name)
        else:
            self.word(name)
    #@+node:ekr.20240105145241.17: *5* tbo.do_newline & do_nl
    def do_newline(self) -> None:
        """Handle a regular newline."""
        self.line_end()

    def do_nl(self) -> None:
        """Handle a continuation line."""
        self.line_end()
    #@+node:ekr.20240105145241.18: *5* tbo.do_number
    def do_number(self) -> None:
        """Handle a number token."""
        self.blank()
        self.add_token('number', self.val)
    #@+node:ekr.20240105145241.19: *5* tbo.do_op & helper
    def do_op(self) -> None:
        """Handle an op token."""
        val = self.val
        if val == '.':
            self.clean('blank')
            prev = self.code_list[-1]
            # #2495 & #2533: Special case for 'from .'
            if prev.kind == 'word' and prev.value == 'from':
                self.blank()
            self.add_token('op-no-blanks', val)
        elif val == '@':
            if self.black_mode:  # pragma: no cover (black)
                if not self.decorator_seen:
                    self.blank_lines(1)
                    self.decorator_seen = True
            self.clean('blank')
            self.add_token('op-no-blanks', val)
            self.push_state('decorator')
        elif val == ':':
            # Treat slices differently.
            self.colon(val)
        elif val in ',;':
            # Pep 8: Avoid extraneous whitespace immediately before
            # comma, semicolon, or colon.
            self.clean('blank')
            self.add_token('op', val)
            self.blank()
        elif val in '([{':
            # Pep 8: Avoid extraneous whitespace immediately inside
            # parentheses, brackets or braces.
            self.lt(val)
        elif val in ')]}':
            # Ditto.
            self.rt(val)
        elif val == '=':
            self.do_equal_op(val)
        elif val in '~+-':
            self.possible_unary_op(val)
        elif val == '*':
            self.star_op()
        elif val == '**':
            self.star_star_op()
        else:
            # Pep 8: always surround binary operators with a single space.
            # '==','+=','-=','*=','**=','/=','//=','%=','!=','<=','>=','<','>',
            # '^','~','*','**','&','|','/','//',
            # Pep 8: If operators with different priorities are used,
            # consider adding whitespace around the operators with the lowest priorities.
            self.blank()
            self.add_token('op', val)
            self.blank()
    #@+node:ekr.20240105145241.20: *6* tbo.do_equal_op
    # Keys: token.index of '=' token. Values: count of ???s
    arg_dict: dict[int, int] = {}

    dump_flag = True

    def do_equal_op(self, val: str) -> None:

        if 0:
            token = self.token
            g.trace(
                f"token.index: {token.index:2} paren_level: {self.paren_level} "
                f"token.equal_sign_spaces: {int(token.equal_sign_spaces)} "
            )

        equal_sign_spaces = self.token.context.get('equal_sign_spaces')
        if equal_sign_spaces:  ###self.token.equal_sign_spaces:
            self.blank()
            self.add_token('op', val)
            self.blank()
        else:
            # Pep 8: Don't use spaces around the = sign when used to indicate
            #        a keyword argument or a default parameter value.
            #        However, hen combining an argument annotation with a default value,
            #        *do* use spaces around the = sign
            self.clean('blank')
            self.add_token('op-no-blanks', val)
    #@+node:ekr.20240105145241.21: *5* tbo.do_string
    def do_string(self) -> None:
        """Handle a 'string' token."""
        # Careful: continued strings may contain '\r'
        val = regularize_nls(self.val)
        self.add_token('string', val)
        self.blank()
    #@+node:ekr.20240105145241.22: *5* tbo.do_verbatim
    beautify_pat = re.compile(
        r'#\s*pragma:\s*beautify\b|#\s*@@beautify|#\s*@\+node|#\s*@[+-]others|#\s*@[+-]<<')

    def do_verbatim(self) -> None:
        """
        Handle one token in verbatim mode.
        End verbatim mode when the appropriate comment is seen.
        """
        kind = self.kind
        #
        # Careful: tokens may contain '\r'
        val = regularize_nls(self.val)
        if kind == 'comment':
            if self.beautify_pat.match(val):
                self.verbatim = False
            val = val.rstrip()
            self.add_token('comment', val)
            return
        if kind == 'indent':
            self.level += 1
            self.lws = self.level * self.tab_width * ' '
        if kind == 'dedent':
            self.level -= 1
            self.lws = self.level * self.tab_width * ' '
        self.add_token('verbatim', val)
    #@+node:ekr.20240105145241.23: *5* tbo.do_ws
    def do_ws(self) -> None:
        """
        Handle the "ws" pseudo-token.

        Put the whitespace only if if ends with backslash-newline.
        """
        val = self.val
        # Handle backslash-newline.
        if '\\\n' in val:
            self.clean('blank')
            self.add_token('op-no-blanks', val)
            return
        # Handle start-of-line whitespace.
        prev = self.code_list[-1]
        inner = self.paren_level or self.square_brackets_stack or self.curly_brackets_level
        if prev.kind == 'line-indent' and inner:
            # Retain the indent that won't be cleaned away.
            self.clean('line-indent')
            self.add_token('hard-blank', val)
    #@+node:ekr.20240105145241.24: *4* tbo: Output token generators
    #@+node:ekr.20240105145241.25: *5* tbo.add_line_end
    def add_line_end(self) -> OutputToken:
        """Add a line-end request to the code list."""
        # This may be called from do_name as well as do_newline and do_nl.
        assert self.token.kind in ('newline', 'nl'), self.token.kind
        self.clean('blank')  # Important!
        self.clean('line-indent')
        t = self.add_token('line-end', '\n')
        # Distinguish between kinds of 'line-end' tokens.
        t.newline_kind = self.token.kind
        return t
    #@+node:ekr.20240105145241.26: *5* tbo.add_token
    def add_token(self, kind: str, value: Any) -> OutputToken:
        """Add an output token to the code list."""
        tok = OutputToken(kind, value)
        tok.index = len(self.code_list)
        self.code_list.append(tok)
        return tok
    #@+node:ekr.20240105145241.27: *5* tbo.blank
    def blank(self) -> None:
        """Add a blank request to the code list."""
        prev = self.code_list[-1]
        if prev.kind not in (
            'blank',
            'blank-lines',
            'file-start',
            'hard-blank',  # Unique to tbo.
            'line-end',
            'line-indent',
            'lt',
            'op-no-blanks',
            'unary-op',
        ):
            self.add_token('blank', ' ')
    #@+node:ekr.20240105145241.28: *5* tbo.blank_lines (black only)
    def blank_lines(self, n: int) -> None:  # pragma: no cover (black)
        """
        Add a request for n blank lines to the code list.
        Multiple blank-lines request yield at least the maximum of all requests.
        """
        self.clean_blank_lines()
        prev = self.code_list[-1]
        if prev.kind == 'file-start':
            self.add_token('blank-lines', n)
            return
        for _i in range(0, n + 1):
            self.add_token('line-end', '\n')
        # Retain the token (intention) for debugging.
        self.add_token('blank-lines', n)
        self.line_indent()
    #@+node:ekr.20240105145241.29: *5* tbo.clean
    def clean(self, kind: str) -> None:
        """Remove the last item of token list if it has the given kind."""
        prev = self.code_list[-1]
        if prev.kind == kind:
            self.code_list.pop()
    #@+node:ekr.20240105145241.30: *5* tbo.clean_blank_lines
    def clean_blank_lines(self) -> bool:
        """
        Remove all vestiges of previous blank lines.

        Return True if any of the cleaned 'line-end' tokens represented "hard" newlines.
        """
        cleaned_newline = False
        table = ('blank-lines', 'line-end', 'line-indent')
        while self.code_list[-1].kind in table:
            t = self.code_list.pop()
            if t.kind == 'line-end' and getattr(t, 'newline_kind', None) != 'nl':
                cleaned_newline = True
        return cleaned_newline
    #@+node:ekr.20240105145241.31: *5* tbo.colon
    def colon(self, val: str) -> None:
        """Handle a colon."""
        ###
            # def is_expr(node: Node) -> bool:
                # """True if node is any expression other than += number."""
                # if isinstance(node, (ast.BinOp, ast.Call, ast.IfExp)):
                    # return True
                # num_node = ast.Num if g.python_version_tuple < (3, 12, 0) else ast.Constant
                # return (
                    # isinstance(node, ast.UnaryOp)
                    # and not isinstance(node.operand, num_node)
                # )

        self.clean('blank')
        if True:  ### not isinstance(node, ast.Slice):
            self.add_token('op', val)
            self.blank()
            return
        # A slice.
        # lower = getattr(node, 'lower', None)
        # upper = getattr(node, 'upper', None)
        # step = getattr(node, 'step', None)
        if False:  ### any(is_expr(z) for z in (lower, upper, step)):
            prev = self.code_list[-1]
            if prev.value not in '[:':
                self.blank()
            self.add_token('op', val)
            self.blank()
        else:
            self.add_token('op-no-blanks', val)
    #@+node:ekr.20240105145241.32: *5* tbo.line_end (disabled calls to split/join)
    def line_end(self) -> None:
        """Add a line-end request to the code list."""
        # Only do_newline and do_nl should call this method.
        token = self.token
        assert token.kind in ('newline', 'nl'), (token.kind, g.callers())
        # Create the 'line-end' output token.
        self.add_line_end()
        if 0:  ### Not ready yet.
            # Attempt to split the line.
            was_split = self.split_line(token)
            # Attempt to join the line only if it has not just been split.
            if not was_split and self.max_join_line_length > 0:
                self.join_lines(token)
        # Add the indentation for all lines
        # until the next indent or unindent token.
        self.line_indent()
    #@+node:ekr.20240105145241.33: *5* tbo.line_indent
    def line_indent(self) -> None:
        """Add a line-indent token."""
        self.clean('line-indent')  # Defensive. Should never happen.
        self.add_token('line-indent', self.lws)
    #@+node:ekr.20240105145241.34: *5* tbo.lt & rt
    #@+node:ekr.20240105145241.35: *6* tbo.lt
    def lt(self, val: str) -> None:
        """Generate code for a left paren or curly/square bracket."""
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
            self.blank()
            self.add_token('lt', val)
        elif prev.kind == 'word':
            # Only suppress blanks before '(' or '[' for non-keywords.
            if val == '{' or prev.value in ('if', 'else', 'return', 'for'):
                self.blank()
            elif val == '(':
                self.in_arg_list += 1
            self.add_token('lt', val)
        else:
            self.clean('blank')
            self.add_token('op-no-blanks', val)
    #@+node:ekr.20240105145241.36: *6* tbo.rt
    def rt(self, val: str) -> None:
        """Generate code for a right paren or curly/square bracket."""
        assert val in ')]}', repr(val)
        if val == ')':
            self.paren_level -= 1
            self.in_arg_list = max(0, self.in_arg_list - 1)
        elif val == ']':
            self.square_brackets_stack.pop()
        else:
            self.curly_brackets_level -= 1
        self.clean('blank')
        self.add_token('rt', val)
    #@+node:ekr.20240105145241.37: *5* tbo.possible_unary_op & unary_op (to do)
    def possible_unary_op(self, s: str) -> None:
        """Add a unary or binary op to the token list."""
        self.clean('blank')
        is_unary = self.token.context.get('is_unary')
        if is_unary:  ### isinstance(node, ast.UnaryOp):
            self.unary_op(s)
        else:
            self.blank()
            self.add_token('op', s)
            self.blank()

    def unary_op(self, s: str) -> None:
        """Add an operator request to the code list."""
        assert s and isinstance(s, str), repr(s)
        self.clean('blank')
        prev = self.code_list[-1]
        if prev.kind == 'lt':
            self.add_token('unary-op', s)
        else:
            self.blank()
            self.add_token('unary-op', s)
    #@+node:ekr.20240105145241.38: *5* tbo.star_op (to do)
    def star_op(self) -> None:
        """Put a '*' op, with special cases for *args."""
        val = '*'
        self.clean('blank')
        in_arg = self.token.context.get('in_args')
        if in_arg:  ### isinstance(node, ast.arguments):
            self.blank()
            self.add_token('op', val)
            return  # #2533
        if self.paren_level > 0:
            prev = self.code_list[-1]
            if prev.kind == 'lt' or (prev.kind, prev.value) == ('op', ','):
                self.blank()
                self.add_token('op', val)
                return
        self.blank()
        self.add_token('op', val)
        self.blank()
    #@+node:ekr.20240105145241.39: *5* tbo.star_star_op (to do)
    def star_star_op(self) -> None:
        """Put a ** operator, with a special case for **kwargs."""
        val = '**'
        self.clean('blank')
        in_arg = self.token.context.get('in_args')
        if in_arg:  ### isinstance(node, ast.arguments):
            self.blank()
            self.add_token('op', val)
            return  # #2533
        if self.paren_level > 0:
            prev = self.code_list[-1]
            if prev.kind == 'lt' or (prev.kind, prev.value) == ('op', ','):
                self.blank()
                self.add_token('op', val)
                return
        self.blank()
        self.add_token('op', val)
        self.blank()
    #@+node:ekr.20240105145241.40: *5* tbo.word & word_op (to do)
    def word(self, s: str) -> None:
        """Add a word request to the code list."""
        assert s and isinstance(s, str), repr(s)
        if s == 'def':
            self.scan_def()
        in_import_from = self.token.context.get('in_import_from')
        if in_import_from:  ### isinstance(node, ast.ImportFrom) and s == 'import':  # #2533
            self.clean('blank')
            self.add_token('blank', ' ')
            self.add_token('word', s)
        elif self.square_brackets_stack:
            # A previous 'op-no-blanks' token may cancel this blank.
            self.blank()
            self.add_token('word', s)
        elif self.in_arg_list > 0:
            self.add_token('word', s)
            self.blank()
        else:
            self.blank()
            self.add_token('word', s)
            self.blank()

    def word_op(self, s: str) -> None:
        """Add a word-op request to the code list."""
        assert s and isinstance(s, str), repr(s)
        self.blank()
        self.add_token('word-op', s)
        self.blank()
    #@+node:ekr.20240105145241.41: *4* tbo: Scanning
    #@+node:ekr.20240106094211.1: *5* tbo.check_token_index
    def check_token_index(self, i: int) -> None:
        # pylint: disable=raise-missing-from
        try:
            self.tokens[i]
        except IndexError:
            raise BeautifyError(f"IndexError: tokens[{i}]")
    #@+node:ekr.20240106090914.1: *5* tbo.expect
    def expect(self, i: int, kind: str, value: str = None) -> None:
        self.check_token_index(i)
        token = self.tokens[i]
        kind, value = token.kind, token.value
        if value is not None:
            message = f"Expected token.kind: {kind} token.value: {value} got {token!r}"
        else:
            message = f"Expected token.kind: {kind} got {token!r}"
        if not token or token.kind != kind or value is not None and token.value != value:
            raise BeautifyError(message)
    #@+node:ekr.20240106053414.1: *5* tbo.is_keyword
    def is_keyword(self, token: InputToken) -> bool:
        """
        Return True if the token represents a Python keyword.
        
        But return False for 'True', 'False' or 'None':
        these can appear in expressions.
        """
        value = token.value
        return (
            token.kind == 'word'
            and value not in ('True', 'False', None)
            and (keyword.iskeyword(value) or keyword.issoftkeyword(value))
        )
    #@+node:ekr.20240106093210.1: *5* tbo.is_significant_token
    def is_significant_token(self, token: InputToken) -> bool:
        """Return true if the given token is not whitespace."""
        return token.kind not in (
            'comment', 'dedent', 'indent', 'newline', 'nl', 'ws',
        )
    #@+node:ekr.20240105145241.42: *5* tbo.scan_def (to do)
    def scan_def(self) -> None:
        """The root of a recursive-descent parser for Python 'def' statements."""
        expect, next = self.expect, self.next_token
        i = self.index
        expect(i, 'name', 'def')
        i = next(i)
        expect(i, 'name')
        i = next(i)
        expect(i, 'op', '(')
        ### Scan for matching ')'
    #@+node:ekr.20240105145241.43: *5* tbo.next/prev_token (to do)
    def next_token(self, i: int) -> Optional[int]:
        """
        Return the next *significant* token in the list of *input* tokens.
        
        Ignore whitespace, indentation, comments, etc.
        """
        self.check_token_index(i)
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
    #@+node:ekr.20240105145241.44: *4* tbo: Split/join (not used yet)
    #@+node:ekr.20240105145241.45: *5* tbo.split_line & helpers (to do)
    def split_line(self, token: InputToken) -> bool:
        """
        Split token's line, if possible and enabled.

        Return True if the line was broken into two or more lines.
        """
        assert token.kind in ('newline', 'nl'), repr(token)
        # Return if splitting is disabled:
        if self.max_split_line_length <= 0:  # pragma: no cover (user option)
            return False
        # Return if the line can't be split.
        ### Not yet.
            # if not is_long_statement(node):
                # return False
        # Find the *output* tokens of the previous lines.
        line_tokens = self.find_prev_line()
        line_s = ''.join([z.to_string() for z in line_tokens])
        # Do nothing for short lines.
        if len(line_s) < self.max_split_line_length:
            return False
        # Return if the previous line has no opening delim: (, [ or {.
        if not any(z.kind == 'lt' for z in line_tokens):  # pragma: no cover (defensive)
            return False
        prefix = self.find_line_prefix(line_tokens)
        # Calculate the tail before cleaning the prefix.
        tail = line_tokens[len(prefix) :]
        # Cut back the token list: subtract 1 for the trailing line-end.
        self.code_list = self.code_list[: len(self.code_list) - len(line_tokens) - 1]
        # Append the tail, splitting it further, as needed.
        self.append_tail(prefix, tail)
        # Add the line-end token deleted by find_line_prefix.
        self.add_token('line-end', '\n')
        return True
    #@+node:ekr.20240105145241.46: *6* tbo.append_tail
    def append_tail(self, prefix: list[OutputToken], tail: list[OutputToken]) -> None:
        """Append the tail tokens, splitting the line further as necessary."""
        tail_s = ''.join([z.to_string() for z in tail])
        if len(tail_s) < self.max_split_line_length:
            # Add the prefix.
            self.code_list.extend(prefix)
            # Start a new line and increase the indentation.
            self.add_token('line-end', '\n')
            self.add_token('line-indent', self.lws + ' ' * 4)
            self.code_list.extend(tail)
            return
        # Still too long.  Split the line at commas.
        self.code_list.extend(prefix)
        # Start a new line and increase the indentation.
        self.add_token('line-end', '\n')
        self.add_token('line-indent', self.lws + ' ' * 4)
        open_delim = OutputToken(kind='lt', value=prefix[-1].value)
        value = open_delim.value.replace('(', ')').replace('[', ']').replace('{', '}')
        close_delim = OutputToken(kind='rt', value=value)
        delim_count = 1
        lws = self.lws + ' ' * 4
        for i, t in enumerate(tail):
            if t.kind == 'op' and t.value == ',':
                if delim_count == 1:
                    # Start a new line.
                    self.add_token('op-no-blanks', ',')
                    self.add_token('line-end', '\n')
                    self.add_token('line-indent', lws)
                    # Kill a following blank.
                    if i + 1 < len(tail):
                        next_t = tail[i + 1]
                        if next_t.kind == 'blank':
                            next_t.kind = 'no-op'
                            next_t.value = ''
                else:
                    self.code_list.append(t)
            elif t.kind == close_delim.kind and t.value == close_delim.value:
                # Done if the delims match.
                delim_count -= 1
                if delim_count == 0:
                    # Start a new line
                    self.add_token('op-no-blanks', ',')
                    self.add_token('line-end', '\n')
                    self.add_token('line-indent', self.lws)
                    self.code_list.extend(tail[i:])
                    return
                lws = lws[:-4]
                self.code_list.append(t)
            elif t.kind == open_delim.kind and t.value == open_delim.value:
                delim_count += 1
                lws = lws + ' ' * 4
                self.code_list.append(t)
            else:
                self.code_list.append(t)
        g.trace('BAD DELIMS', delim_count)  # pragma: no cover
    #@+node:ekr.20240105145241.47: *6* tbo.find_prev_line
    def find_prev_line(self) -> list[OutputToken]:
        """Return the previous line, as a list of tokens."""
        line = []
        for t in reversed(self.code_list[:-1]):
            if t.kind in ('hard-newline', 'line-end'):
                break
            line.append(t)
        return list(reversed(line))
    #@+node:ekr.20240105145241.48: *6* tbo.find_line_prefix
    def find_line_prefix(self, token_list: list[OutputToken]) -> list[OutputToken]:
        """
        Return all tokens up to and including the first lt token.
        Also add all lt tokens directly following the first lt token.
        """
        result = []
        for t in token_list:
            result.append(t)
            if t.kind == 'lt':
                break
        return result
    #@+node:ekr.20240105145241.49: *5* tbo.join_lines (to do)
    def join_lines(self, token: InputToken) -> None:
        """
        Join preceding lines, if possible and enabled.
        token is a line_end token.
        """
        if self.max_join_line_length <= 0:  # pragma: no cover (user option)
            return
        assert token.kind in ('newline', 'nl'), repr(token)
        if token.kind == 'nl':
            return
        # Scan backward in the *code* list,
        # looking for 'line-end' tokens with tok.newline_kind == 'nl'
        nls = 0
        i = len(self.code_list) - 1
        t = self.code_list[i]
        assert t.kind == 'line-end', repr(t)
        # Not all tokens have a newline_kind ivar.
        assert t.newline_kind == 'newline'
        i -= 1
        while i >= 0:
            t = self.code_list[i]
            if t.kind == 'comment':
                # Can't join.
                return
            if t.kind == 'string' and not self.allow_joined_strings:
                # An EKR preference: don't join strings, no matter what black does.
                # This allows "short" f-strings to be aligned.
                return
            if t.kind == 'line-end':
                if getattr(t, 'newline_kind', None) == 'nl':
                    nls += 1
                else:
                    break  # pragma: no cover
            i -= 1
        # Retain at the file-start token.
        if i <= 0:
            i = 1
        if nls <= 0:  # pragma: no cover (rare)
            return
        # Retain line-end and and any following line-indent.
        # Required, so that the regex below won't eat too much.
        while True:
            t = self.code_list[i]
            if t.kind == 'line-end':
                if getattr(t, 'newline_kind', None) == 'nl':  # pragma: no cover (rare)
                    nls -= 1
                i += 1
            elif self.code_list[i].kind == 'line-indent':
                i += 1
            else:
                break  # pragma: no cover (defensive)
        if nls <= 0:  # pragma: no cover (defensive)
            return
        # Calculate the joined line.
        tail = self.code_list[i:]
        tail_s = output_tokens_to_string(tail)
        tail_s = re.sub(r'\n\s*', ' ', tail_s)
        tail_s = tail_s.replace('( ', '(').replace(' )', ')')
        tail_s = tail_s.rstrip()
        # Don't join the lines if they would be too long.
        if len(tail_s) > self.max_join_line_length:  # pragma: no cover (defensive)
            return
        # Cut back the code list.
        self.code_list = self.code_list[:i]
        # Add the new output tokens.
        self.add_token('string', tail_s)
        self.add_token('line-end', '\n')
    #@-others
#@+node:ekr.20240105140814.121: ** function: (leoTokens.py) main & helpers
def main() -> None:  # pragma: no cover
    """Run commands specified by sys.argv."""
    args, settings_dict, arg_files = scan_args()
    # Finalize arguments.
    cwd = os.getcwd()
    # Calculate requested files.
    requested_files: list[str] = []
    for path in arg_files:
        if path.endswith('.py'):
            requested_files.append(os.path.join(cwd, path))
        else:
            root_dir = os.path.join(cwd, path)
            requested_files.extend(glob.glob(f'{root_dir}**{os.sep}*.py', recursive=True))
    if not requested_files:
        print(f"No files in {arg_files!r}")
        return
    files: list[str]
    if args.force:
        # Handle all requested files.
        files = requested_files
    else:
        # Handle only modified files.
        modified_files = get_modified_files(cwd)
        files = [z for z in requested_files if os.path.abspath(z) in modified_files]
    if not files:
        return
    if args.verbose:
        kind = (
            # 'fstringify' if args.f else
            # 'fstringify-diff' if args.fd else
            'orange' if args.o else
            # 'orange-diff' if args.od else
            None
        )
        if kind:
            n = len(files)
            n_s = f" {n:>3} file" if n == 1 else f"{n:>3} files"
            print(f"{kind}: {n_s} in {', '.join(arg_files)}")
    # Do the command.
    # if args.f:
        # fstringify_command(files)
    # if args.fd:
        # fstringify_diff_command(files)
    if args.o:
        orange_command(files, settings_dict)
    # if args.od:
        # orange_diff_command(files, settings_dict)
#@+node:ekr.20240105140814.10: *3* function: scan_args
def scan_args() -> tuple[Any, dict[str, Any], list[str]]:
    description = textwrap.dedent("""\
        Execute fstringify or beautify commands contained in leoAst.py.
    """)
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('PATHS', nargs='*', help='directory or list of files')
    group = parser.add_mutually_exclusive_group(required=False)  # Don't require any args.
    add = group.add_argument
    # add('--fstringify', dest='f', action='store_true',
        # help='fstringify PATHS')
    # add('--fstringify-diff', dest='fd', action='store_true',
        # help='fstringify diff PATHS')
    add('--orange', dest='o', action='store_true',
        help='beautify PATHS')
    add('--orange-diff', dest='od', action='store_true',
        help='diff beautify PATHS')
    # New arguments.
    add2 = parser.add_argument
    add2('--allow-joined', dest='allow_joined', action='store_true',
        help='allow joined strings')
    add2('--max-join', dest='max_join', metavar='N', type=int,
        help='max unsplit line length (default 0)')
    add2('--max-split', dest='max_split', metavar='N', type=int,
        help='max unjoined line length (default 0)')
    add2('--tab-width', dest='tab_width', metavar='N', type=int,
        help='tab-width (default -4)')
    # Newer arguments.
    add2('--force', dest='force', action='store_true',
        help='force beautification of all files')
    add2('--verbose', dest='verbose', action='store_true',
        help='verbose (per-file) output')
    # Create the return values, using EKR's prefs as the defaults.
    parser.set_defaults(
        allow_joined=False,
        force=False,
        max_join=0,
        max_split=0,
        recursive=False,
        tab_width=4,
        verbose=False
    )
    args: Any = parser.parse_args()
    files = args.PATHS
    # Create the settings dict, ensuring proper values.
    settings_dict: dict[str, Any] = {
        'allow_joined_strings': bool(args.allow_joined),
        'force': bool(args.force),
        'max_join_line_length': abs(args.max_join),
        'max_split_line_length': abs(args.max_split),
        'tab_width': abs(args.tab_width),  # Must be positive!
        'verbose': bool(args.verbose),
    }
    return args, settings_dict, files
#@-others

if __name__ == '__main__':
    main()  # pragma: no cover

#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
