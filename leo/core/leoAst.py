#@+leo-ver=5-thin
#@+node:ekr.20141012064706.18389: * @file leoAst.py
# This file is part of Leo: https://leo-editor.github.io/leo-editor
# Leo's copyright notice is based on the MIT license:
# https://leo-editor.github.io/leo-editor/license.html

#@+<< leoAst docstring >>
#@+node:ekr.20200113081838.1: ** << leoAst docstring >>
"""
leoAst.py: This file does not depend on Leo in any way.

The classes in this file unify python's token-based and ast-based worlds by
creating two-way links between tokens in the token list and ast nodes in
the parse tree. For more details, see the "Overview" section below.

This file requires Python 3.9 or above.


**Stand-alone operation**

usage:
    python -m leo.core.leoAst.py --help
    python -m leo.core.leoAst.py --fstringify [ARGS] PATHS
    python -m leo.core.leoAst.py --fstringify-diff [ARGS] PATHS
    python -m leo.core.leoAst.py --orange [ARGS] PATHS
    python -m leo.core.leoAst.py --orange-diff [ARGS] PATHS
    python -m leo.core.leoAst.py --py-cov [ARGS]
    python -m leo.core.leoAst.py --pytest [ARGS]
    python -m leo.core.leoAst.py --unittest [ARGS]

examples:
    python -m leo.core.leoAst.py --orange --force --verbose PATHS
    python -m leo.core.leoAst.py --py-cov "-f TestOrange"
    python -m leo.core.leoAst.py --pytest "-f TestOrange"
    python -m leo.core.leoAst.py --unittest TestOrange

positional arguments:
  PATHS              directory or list of files

optional arguments:
  -h, --help         show this help message and exit
  --force            operate on all files. Otherwise operate only on modified files
  --fstringify       leonine fstringify
  --fstringify-diff  show fstringify diff
  --orange           leonine text formatter (Orange is the new Black)
  --orange-diff      show orange diff
  --py-cov           run pytest --cov on leoAst.py
  --pytest           run pytest on leoAst.py
  --unittest         run unittest on leoAst.py
  --verbose          verbose output


**Overview**

leoAst.py unifies python's token-oriented and ast-oriented worlds.

leoAst.py defines classes that create two-way links between tokens
created by python's tokenize module and parse tree nodes created by
python's ast module:

The Token Order Generator (TOG) class quickly creates the following
links:

- An *ordered* children array from each ast node to its children.

- A parent link from each ast.node to its parent.

- Two-way links between tokens in the token list, a list of Token
  objects, and the ast nodes in the parse tree:

  - For each token, token.node contains the ast.node "responsible" for
    the token.

  - For each ast node, node.first_i and node.last_i are indices into
    the token list. These indices give the range of tokens that can be
    said to be "generated" by the ast node.

Once the TOG class has inserted parent/child links, the Token Order
Traverser (TOT) class traverses trees annotated with parent/child
links extremely quickly.


**Applicability and importance**

Many python developers will find asttokens meets all their needs.
asttokens is well documented and easy to use. Nevertheless, two-way
links are significant additions to python's tokenize and ast modules:

- Links from tokens to nodes are assigned to the nearest possible ast
  node, not the nearest statement, as in asttokens. Links can easily
  be reassigned, if desired.

- The TOG and TOT classes are intended to be the foundation of tools
  such as fstringify and black.

- The TOG class solves real problems, such as:
  https://stackoverflow.com/questions/16748029/

**Historical note re Python 3.8**

In Python 3.8 *only*, syncing tokens will fail for function calls like:

    f(1, x=2, *[3, 4], y=5)

that is, for calls where keywords appear before non-keyword args.


**Figures of merit**

Simplicity: The code consists primarily of a set of generators, one
for every kind of ast node.

Speed: The TOG creates two-way links between tokens and ast nodes in
roughly the time taken by python's tokenize.tokenize and ast.parse
library methods. This is substantially faster than the asttokens,
black or fstringify tools. The TOT class traverses trees annotated
with parent/child links even more quickly.

Memory: The TOG class makes no significant demands on python's
resources. Generators add nothing to python's call stack.
TOG.node_stack is the only variable-length data. This stack resides in
python's heap, so its length is unimportant. In the worst case, it
might contain a few thousand entries. The TOT class uses no
variable-length data at all.

**Links**

Leo...
Ask for help:       https://groups.google.com/forum/#!forum/leo-editor
Report a bug:       https://github.com/leo-editor/leo-editor/issues
leoAst.py docs:     https://leo-editor.github.io/leo-editor/appendices.html#leoast-py

Other tools...
asttokens:          https://pypi.org/project/asttokens
black:              https://pypi.org/project/black/
fstringify:         https://pypi.org/project/fstringify/

Python modules...
tokenize.py:        https://docs.python.org/3/library/tokenize.html
ast.py              https://docs.python.org/3/library/ast.html

**Studying this file**

I strongly recommend that you use Leo when studying this code so that you
will see the file's intended outline structure.

Without Leo, you will see only special **sentinel comments** that create
Leo's outline structure. These comments have the form::

    `#@<comment-kind>:<user-id>.<timestamp>.<number>: <outline-level> <headline>`
"""
#@-<< leoAst docstring >>
#@+<< leoAst imports & annotations >>
#@+node:ekr.20200105054219.1: ** << leoAst imports & annotations >>
from __future__ import annotations
import argparse
import ast
import codecs
import difflib
import glob
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

assert argparse and os and subprocess and textwrap  ###
#@-<< leoAst imports & annotations >>

#@+others
#@+node:ekr.20240104093211.1: ** Orange functions
#@+node:ekr.20191119085222.1: *3* function: obj_id
def obj_id(obj: Any) -> str:
    """Return the last four digits of id(obj), for dumps & traces."""
    return str(id(obj))[-4:]
#@+node:ekr.20200107040729.1: *3* function: show_diffs
def show_diffs(s1: str, s2: str, filename: str = '') -> None:
    """Print diffs between strings s1 and s2."""
    lines = list(difflib.unified_diff(
        g.splitLines(s1),
        g.splitLines(s2),
        fromfile=f"Old {filename}",
        tofile=f"New {filename}",
    ))
    print('')
    tag = f"Diffs for {filename}" if filename else 'Diffs'
    g.printObj(lines, tag=tag)
#@+node:ekr.20200101030236.1: *3* function: input_tokens_to_string
def input_tokens_to_string(tokens: list[InputToken]) -> str:
    """Return the string represented by the list of tokens."""
    if tokens is None:
        # This indicates an internal error.
        print('')
        g.trace('===== input token list is None ===== ')
        print('')
        return ''
    return ''.join([z.to_string() for z in tokens])
#@+node:ekr.20240104095925.1: *3* function: output_tokens_to_string
def output_tokens_to_string(tokens: list[OutputToken]) -> str:
    """Return the string represented by the list of tokens."""
    if tokens is None:
        # This indicates an internal error.
        print('')
        g.trace('===== output token list is None ===== ')
        print('')
        return ''
    return ''.join([z.to_string() for z in tokens])
#@+node:ekr.20200107114409.1: *3* functions: reading & writing files
#@+node:ekr.20200218071822.1: *4* function: regularize_nls
def regularize_nls(s: str) -> str:
    """Regularize newlines within s."""
    return s.replace('\r\n', '\n').replace('\r', '\n')
#@+node:ekr.20200106171502.1: *4* function: get_encoding_directive
# This is the pattern in PEP 263.
encoding_pattern = re.compile(r'^[ \t\f]*#.*?coding[:=][ \t]*([-_.a-zA-Z0-9]+)')

def get_encoding_directive(bb: bytes) -> str:
    """
    Get the encoding from the encoding directive at the start of a file.

    bb: The bytes of the file.

    Returns the codec name, or 'UTF-8'.

    Adapted from pyzo. Copyright 2008 to 2020 by Almar Klein.
    """
    for line in bb.split(b'\n', 2)[:2]:
        # Try to make line a string
        try:
            line2 = line.decode('ASCII').strip()
        except Exception:
            continue
        # Does the line match the PEP 263 pattern?
        m = encoding_pattern.match(line2)
        if not m:
            continue
        # Is it a known encoding? Correct the name if it is.
        try:
            c = codecs.lookup(m.group(1))
            return c.name
        except Exception:
            pass
    return 'UTF-8'
#@+node:ekr.20200103113417.1: *4* function: read_file
def read_file(filename: str, encoding: str = 'utf-8') -> Optional[str]:
    """
    Return the contents of the file with the given name.
    Print an error message and return None on error.
    """
    tag = 'read_file'
    try:
        # Translate all newlines to '\n'.
        with open(filename, 'r', encoding=encoding) as f:
            s = f.read()
        return regularize_nls(s)
    except Exception:
        print(f"{tag}: can not read {filename}")
        return None
#@+node:ekr.20200106173430.1: *4* function: read_file_with_encoding
def read_file_with_encoding(filename: str) -> tuple[str, str]:
    """
    Read the file with the given name,  returning (e, s), where:

    s is the string, converted to unicode, or '' if there was an error.

    e is the encoding of s, computed in the following order:

    - The BOM encoding if the file starts with a BOM mark.
    - The encoding given in the # -*- coding: utf-8 -*- line.
    - The encoding given by the 'encoding' keyword arg.
    - 'utf-8'.
    """
    # First, read the file.
    tag = 'read_with_encoding'
    try:
        with open(filename, 'rb') as f:
            bb = f.read()
    except Exception:
        print(f"{tag}: can not read {filename}")
        return 'UTF-8', None
    # Look for the BOM.
    e, bb = strip_BOM(bb)
    if not e:
        # Python's encoding comments override everything else.
        e = get_encoding_directive(bb)
    s = g.toUnicode(bb, encoding=e)
    s = regularize_nls(s)
    return e, s
#@+node:ekr.20200106174158.1: *4* function: strip_BOM
def strip_BOM(bb: bytes) -> tuple[Optional[str], bytes]:
    """
    bb must be the bytes contents of a file.

    If bb starts with a BOM (Byte Order Mark), return (e, bb2), where:

    - e is the encoding implied by the BOM.
    - bb2 is bb, stripped of the BOM.

    If there is no BOM, return (None, bb)
    """
    assert isinstance(bb, bytes), bb.__class__.__name__
    table = (
                    # Test longer bom's first.
        (4, 'utf-32', codecs.BOM_UTF32_BE),
        (4, 'utf-32', codecs.BOM_UTF32_LE),
        (3, 'utf-8', codecs.BOM_UTF8),
        (2, 'utf-16', codecs.BOM_UTF16_BE),
        (2, 'utf-16', codecs.BOM_UTF16_LE),
    )
    for n, e, bom in table:
        assert len(bom) == n
        if bom == bb[: len(bom)]:
            return e, bb[len(bom) :]
    return None, bb
#@+node:ekr.20200103163100.1: *4* function: write_file
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
#@+node:ekr.20200107114452.1: *3* node/token creators...
#@+node:ekr.20200103082049.1: *4* function: make_tokens
def make_tokens(contents: str) -> list[InputToken]:
    """
    Return a list (not a generator) of Token objects corresponding to the
    list of 5-tuples generated by tokenize.tokenize.

    Perform consistency checks and handle all exceptions.
    """

    def check(contents: str, tokens: list[InputToken]) -> bool:
        result = input_tokens_to_string(tokens)
        ok = result == contents
        if not ok:
            print('\nRound-trip check FAILS')
            print('Contents...\n')
            g.printObj(contents)
            print('\nResult...\n')
            g.printObj(result)
        return ok

    try:
        five_tuples = tokenize.tokenize(
            io.BytesIO(contents.encode('utf-8')).readline)
    except Exception:
        print('make_tokens: exception in tokenize.tokenize')
        g.es_exception()
        return None
    tokens = Tokenizer().create_input_tokens(contents, five_tuples)
    assert check(contents, tokens)
    return tokens
#@+node:ekr.20191027075648.1: *4* function: parse_ast
def parse_ast(s: str) -> Optional[Node]:
    """
    Parse string s, catching & reporting all exceptions.
    Return the ast node, or None.
    """

    def oops(message: str) -> None:
        print('')
        print(f"parse_ast: {message}")
        g.printObj(s)
        print('')

    try:
        s1 = g.toEncodedString(s)
        tree = ast.parse(s1, filename='before', mode='exec')
        return tree
    except IndentationError:
        oops('Indentation Error')
    except SyntaxError:
        oops('Syntax Error')
    except Exception:
        oops('Unexpected Exception')
        g.es_exception()
    return None
#@+node:ekr.20191027072910.1: ** Exception classes
class AssignLinksError(Exception):
    """Assigning links to ast nodes failed."""

class AstNotEqual(Exception):
    """The two given AST's are not equivalent."""

class BeautifyError(Exception):
    """Leading tabs found."""

class FailFast(Exception):
    """Abort tests in TestRunner class."""
#@+node:ekr.20240104092757.1: ** Orange classes
#@+node:ekr.20240104082325.1: *3* class InputToken
class InputToken:
    """
    A class representing input tokens.
    """

    def __init__(self, kind: str, value: str):

        self.kind = kind
        self.value = value
        #
        # Injected by Tokenizer.add_token.
        self.five_tuple: tuple = None
        self.index = 0
        # The entire line containing the token.
        # Same as five_tuple.line.
        self.line = ''
        # The line number, for errors and dumps.
        # Same as five_tuple.start[0]
        self.line_number = 0
        #
        # Injected by Tokenizer.add_token.
        self.level = 0
        self.node: Optional[Node] = None

    def __repr__(self) -> str:  # pragma: no cover
        s = f"{self.index:<3} {self.kind:}"
        return f"Token {s}: {self.show_val(20)}"

    __str__ = __repr__


    def to_string(self) -> str:
        """Return the contribution of the token to the source file."""
        return self.value if isinstance(self.value, str) else ''
    #@+others
    #@+node:ekr.20240104082325.2: *4* token.brief_dump
    def brief_dump(self) -> str:  # pragma: no cover
        """Dump a token."""
        return (
            f"{self.index:>3} line: {self.line_number:<2} "
            f"{self.kind:>15} {self.show_val(100)}")
    #@+node:ekr.20240104082325.3: *4* token.dump
    def dump(self) -> str:  # pragma: no cover
        """Dump a token and related links."""
        # Let block.
        node_id = self.node.node_index if self.node else ''
        node_cn = self.node.__class__.__name__ if self.node else ''
        return (
            f"{self.line_number:4} "
            f"{node_id:5} {node_cn:16} "
            f"{self.index:>5} {self.kind:>15} "
            f"{self.show_val(100)}")
    #@+node:ekr.20240104082325.4: *4* token.dump_header
    def dump_header(self) -> None:  # pragma: no cover
        """Print the header for token.dump"""
        print(
            f"\n"
            f"         node    {'':10} token {'':10}   token\n"
            f"line index class {'':10} index {'':10} kind value\n"
            f"==== ===== ===== {'':10} ===== {'':10} ==== =====\n")
    #@+node:ekr.20240104082325.5: *4* token.error_dump
    def error_dump(self) -> str:  # pragma: no cover
        """Dump a token or result node for error message."""
        if self.node:
            node_id = obj_id(self.node)
            node_s = f"{node_id} {self.node.__class__.__name__}"
        else:
            node_s = "None"
        return (
            f"index: {self.index:<3} {self.kind:>12} {self.show_val(20):<20} "
            f"{node_s}")
    #@+node:ekr.20240104082325.6: *4* token.show_val
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
#@+node:ekr.20200107165250.1: *3* class Orange
class Orange:
    """
    A flexible and powerful beautifier for Python.
    Orange is the new black.

    This is a predominantly a *token-based* beautifier. However,
    orange.do_op, orange.colon, and orange.possible_unary_op use the parse
    tree to provide context that would otherwise be difficult to deduce.
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
    #@+node:ekr.20200107165250.2: *4* orange.ctor
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
    #@+node:ekr.20200107165250.51: *4* orange.push_state
    def push_state(self, kind: str, value: Union[int, str] = None) -> None:
        """Append a state to the state stack."""
        state = ParseState(kind, value)
        self.state_stack.append(state)
    #@+node:ekr.20200107165250.8: *4* orange: Entries & helpers
    #@+node:ekr.20200107173542.1: *5* orange.beautify (main token loop)
    def oops(self) -> None:  # pragma: no cover
        g.trace(f"Unknown kind: {self.kind}")

    def beautify(self,
        contents: str,
        filename: str,
        tokens: list[InputToken],
        tree: Optional[Node] = None,
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
        self.level = 0  # Set only by do_indent and do_dedent.
        self.lws = ''  # Leading whitespace.
        self.paren_level = 0  # Number of unmatched '(' tokens.
        self.square_brackets_stack: list[bool] = []  # A stack of bools, for self.word().
        self.state_stack: list["ParseState"] = []  # Stack of ParseState objects.
        self.val = None  # The input token's value (a string).
        self.verbatim = False  # True: don't beautify.
        #
        # Init output list and state...
        self.code_list: list[OutputToken] = []  # The list of output tokens.
        self.tokens = tokens  # The list of input tokens.
        self.tree = tree
        self.add_token('file-start', '')
        self.push_state('file-start')
        for token in tokens:
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
    #@+node:ekr.20200107172450.1: *5* orange.beautify_file (entry)
    def beautify_file(self, filename: str) -> bool:  # pragma: no cover
        """
        Orange: Beautify the the given external file.

        Return True if the file was changed.
        """
        self.filename = filename
        ###
            # tog = TokenOrderGenerator()
            # contents, encoding, tokens, tree = tog.init_from_file(filename)
            # if not contents or not tokens or not tree:
                # return False  # #2529: Not an error.
        
        tree = None
        contents, encoding, tokens = self.init_tokens_from_file(filename)
        if not (contents and tokens):
            return False

        # Beautify.
        try:
            results = self.beautify(contents, filename, tokens, tree)
        except BeautifyError:
            return False  # #2578.
        # Something besides newlines must change.
        if regularize_nls(contents) == regularize_nls(results):
            return False
        if 0:  # This obscures more import error messages.
            show_diffs(contents, results, filename=filename)
        # Write the results
        print(f"Beautified: {g.shortFileName(filename)}")
        write_file(filename, results, encoding=encoding)
        return True
    #@+node:ekr.20200107172512.1: *5* orange.beautify_file_diff (entry)
    def beautify_file_diff(self, filename: str) -> bool:  # pragma: no cover
        """
        Orange: Print the diffs that would result from the orange-file command.

        Return True if the file would be changed.
        """
        tag = 'diff-beautify-file'
        self.filename = filename
        
        ###
            # tog = TokenOrderGenerator()
            # contents, encoding, tokens, tree = tog.init_from_file(filename)
            # if not contents or not tokens or not tree:
                # print(f"{tag}: Can not beautify: {filename}")
                # return False
                
        tree = None
        contents, encoding, tokens = self.init_tokens_from_file(filename)
        if not (contents and tokens):
            return False

        # Beautify
        results = self.beautify(contents, filename, tokens, tree)
        # Something besides newlines must change.
        if regularize_nls(contents) == regularize_nls(results):
            print(f"{tag}: Unchanged: {filename}")
            return False
        # Show the diffs.
        show_diffs(contents, results, filename=filename)
        return True
    #@+node:ekr.20240104093833.1: *5* orange.init_tokens_from_file
    def init_tokens_from_file(self, filename: str) -> tuple[str, str, list[InputToken]]:  # pragma: no cover
        """
        Create the list of tokens for the given file.
        Return (contents, encoding, tokens).
        """
        self.level = 0
        self.filename = filename
        encoding, contents = read_file_with_encoding(filename)
        if not contents:
            return None, None, None
        self.tokens = tokens = make_tokens(contents)
        return contents, encoding, tokens
    #@+node:ekr.20200107165250.13: *4* orange: Input token handlers
    #@+node:ekr.20200107165250.14: *5* orange.do_comment
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
    #@+node:ekr.20200107165250.15: *5* orange.do_encoding
    def do_encoding(self) -> None:
        """
        Handle the encoding token.
        """
        pass
    #@+node:ekr.20200107165250.16: *5* orange.do_endmarker
    def do_endmarker(self) -> None:
        """Handle an endmarker token."""
        # Ensure exactly one blank at the end of the file.
        self.clean_blank_lines()
        self.add_token('line-end', '\n')
    #@+node:ekr.20231215212951.1: *5* orange.do_fstring_start & continue_fstring
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
    #@+node:ekr.20200107165250.18: *5* orange.do_indent & do_dedent & helper
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
    #@+node:ekr.20200220054928.1: *6* orange.handle_dedent_after_class_or_def
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
                #@verbatim
                # @+node comments must never be in the tail.
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
    #@+node:ekr.20200107165250.20: *5* orange.do_name
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
    #@+node:ekr.20200107165250.21: *5* orange.do_newline & do_nl
    def do_newline(self) -> None:
        """Handle a regular newline."""
        self.line_end()

    def do_nl(self) -> None:
        """Handle a continuation line."""
        self.line_end()
    #@+node:ekr.20200107165250.22: *5* orange.do_number
    def do_number(self) -> None:
        """Handle a number token."""
        self.blank()
        self.add_token('number', self.val)
    #@+node:ekr.20200107165250.23: *5* orange.do_op & helper
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
    #@+node:ekr.20230115141629.1: *6* orange.do_equal_op
    # Keys: token.index of '=' token. Values: count of ???s
    arg_dict: dict[int, int] = {}

    dump_flag = True

    def do_equal_op(self, val: str) -> None:

        if 0:
            token = self.token
            g.trace(
                f"token.index: {token.index:2} paren_level: {self.paren_level} "
                f"token.equal_sign_spaces: {int(token.equal_sign_spaces)} "
                # f"{token.node.__class__.__name__}"
            )
            # dump_tree(self.tokens, self.tree)
        if self.token.equal_sign_spaces:
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
    #@+node:ekr.20200107165250.24: *5* orange.do_string
    def do_string(self) -> None:
        """Handle a 'string' token."""
        # Careful: continued strings may contain '\r'
        val = regularize_nls(self.val)
        self.add_token('string', val)
        self.blank()
    #@+node:ekr.20200210175117.1: *5* orange.do_verbatim
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
    #@+node:ekr.20200107165250.25: *5* orange.do_ws
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
    #@+node:ekr.20200107165250.26: *4* orange: Output token generators
    #@+node:ekr.20200118145044.1: *5* orange.add_line_end
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
    #@+node:ekr.20200107170523.1: *5* orange.add_token
    def add_token(self, kind: str, value: Any) -> OutputToken:
        """Add an output token to the code list."""
        tok = OutputToken(kind, value)
        tok.index = len(self.code_list)
        self.code_list.append(tok)
        return tok
    #@+node:ekr.20200107165250.27: *5* orange.blank
    def blank(self) -> None:
        """Add a blank request to the code list."""
        prev = self.code_list[-1]
        if prev.kind not in (
            'blank',
            'blank-lines',
            'file-start',
            'hard-blank',  # Unique to orange.
            'line-end',
            'line-indent',
            'lt',
            'op-no-blanks',
            'unary-op',
        ):
            self.add_token('blank', ' ')
    #@+node:ekr.20200107165250.29: *5* orange.blank_lines (black only)
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
    #@+node:ekr.20200107165250.30: *5* orange.clean
    def clean(self, kind: str) -> None:
        """Remove the last item of token list if it has the given kind."""
        prev = self.code_list[-1]
        if prev.kind == kind:
            self.code_list.pop()
    #@+node:ekr.20200107165250.31: *5* orange.clean_blank_lines
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
    #@+node:ekr.20200107165250.32: *5* orange.colon
    def colon(self, val: str) -> None:
        """Handle a colon."""

        def is_expr(node: Node) -> bool:
            """True if node is any expression other than += number."""
            if isinstance(node, (ast.BinOp, ast.Call, ast.IfExp)):
                return True
            num_node = ast.Num if g.python_version_tuple < (3, 12, 0) else ast.Constant
            return (
                isinstance(node, ast.UnaryOp)
                and not isinstance(node.operand, num_node)
            )

        node = self.token.node
        self.clean('blank')
        if not isinstance(node, ast.Slice):
            self.add_token('op', val)
            self.blank()
            return
        # A slice.
        lower = getattr(node, 'lower', None)
        upper = getattr(node, 'upper', None)
        step = getattr(node, 'step', None)
        if any(is_expr(z) for z in (lower, upper, step)):
            prev = self.code_list[-1]
            if prev.value not in '[:':
                self.blank()
            self.add_token('op', val)
            self.blank()
        else:
            self.add_token('op-no-blanks', val)
    #@+node:ekr.20200107165250.33: *5* orange.line_end
    def line_end(self) -> None:
        """Add a line-end request to the code list."""
        # This should be called only be do_newline and do_nl.
        node, token = self.token.statement_node, self.token
        assert token.kind in ('newline', 'nl'), (token.kind, g.callers())
        # Create the 'line-end' output token.
        self.add_line_end()
        # Attempt to split the line.
        was_split = self.split_line(node, token)
        # Attempt to join the line only if it has not just been split.
        if not was_split and self.max_join_line_length > 0:
            self.join_lines(node, token)
        # Add the indentation for all lines
        # until the next indent or unindent token.
        self.line_indent()
    #@+node:ekr.20200107165250.40: *5* orange.line_indent
    def line_indent(self) -> None:
        """Add a line-indent token."""
        self.clean('line-indent')  # Defensive. Should never happen.
        self.add_token('line-indent', self.lws)
    #@+node:ekr.20200107165250.41: *5* orange.lt & rt
    #@+node:ekr.20200107165250.42: *6* orange.lt
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
    #@+node:ekr.20200107165250.43: *6* orange.rt
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
    #@+node:ekr.20200107165250.45: *5* orange.possible_unary_op & unary_op
    def possible_unary_op(self, s: str) -> None:
        """Add a unary or binary op to the token list."""
        node = self.token.node
        self.clean('blank')
        if isinstance(node, ast.UnaryOp):
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
    #@+node:ekr.20200107165250.46: *5* orange.star_op
    def star_op(self) -> None:
        """Put a '*' op, with special cases for *args."""
        val = '*'
        node = self.token.node
        self.clean('blank')
        if isinstance(node, ast.arguments):
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
    #@+node:ekr.20200107165250.47: *5* orange.star_star_op
    def star_star_op(self) -> None:
        """Put a ** operator, with a special case for **kwargs."""
        val = '**'
        node = self.token.node
        self.clean('blank')
        if isinstance(node, ast.arguments):
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
    #@+node:ekr.20200107165250.48: *5* orange.word & word_op
    def word(self, s: str) -> None:
        """Add a word request to the code list."""
        assert s and isinstance(s, str), repr(s)
        node = self.token.node
        if isinstance(node, ast.ImportFrom) and s == 'import':  # #2533
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
    #@-others
#@+node:ekr.20240104082408.1: *3* class OutputToken
class OutputToken:
    """
    A class representing an output token.
    """

    def __init__(self, kind: str, value: str):

        self.kind = kind
        self.value = value
        #
        # Injected by Tokenizer.add_token.
        self.five_tuple: tuple = None
        self.index = 0
        # The entire line containing the token.
        # Same as five_tuple.line.
        self.line = ''
        # The line number, for errors and dumps.
        # Same as five_tuple.start[0]
        self.line_number = 0
        #
        # Injected by Tokenizer.add_token.
        self.level = 0
        self.node: Optional[Node] = None

    def __repr__(self) -> str:  # pragma: no cover
        s = f"{self.index:<3} {self.kind:}"
        return f"Token {s}: {self.show_val(20)}"

    __str__ = __repr__


    def to_string(self) -> str:
        """Return the contribution of the token to the source file."""
        return self.value if isinstance(self.value, str) else ''
    #@+others
    #@+node:ekr.20240104082408.2: *4* token.brief_dump
    def brief_dump(self) -> str:  # pragma: no cover
        """Dump a token."""
        return (
            f"{self.index:>3} line: {self.line_number:<2} "
            f"{self.kind:>15} {self.show_val(100)}")
    #@+node:ekr.20240104082408.3: *4* token.dump
    def dump(self) -> str:  # pragma: no cover
        """Dump a token and related links."""
        # Let block.
        node_id = self.node.node_index if self.node else ''
        node_cn = self.node.__class__.__name__ if self.node else ''
        return (
            f"{self.line_number:4} "
            f"{node_id:5} {node_cn:16} "
            f"{self.index:>5} {self.kind:>15} "
            f"{self.show_val(100)}")
    #@+node:ekr.20240104082408.4: *4* token.dump_header
    def dump_header(self) -> None:  # pragma: no cover
        """Print the header for token.dump"""
        print(
            f"\n"
            f"         node    {'':10} token {'':10}   token\n"
            f"line index class {'':10} index {'':10} kind value\n"
            f"==== ===== ===== {'':10} ===== {'':10} ==== =====\n")
    #@+node:ekr.20240104082408.5: *4* token.error_dump
    def error_dump(self) -> str:  # pragma: no cover
        """Dump a token or result node for error message."""
        if self.node:
            node_id = obj_id(self.node)
            node_s = f"{node_id} {self.node.__class__.__name__}"
        else:
            node_s = "None"
        return (
            f"index: {self.index:<3} {self.kind:>12} {self.show_val(20):<20} "
            f"{node_s}")
    #@+node:ekr.20240104082408.6: *4* token.show_val
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
#@+node:ekr.20200107170126.1: *3* class ParseState
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
#@+node:ekr.20191110165235.1: *3* class Tokenizer
class Tokenizer:

    """Create a list of Tokens from contents."""

    results: list[InputToken] = []

    #@+others
    #@+node:ekr.20191110165235.2: *4* tokenizer.add_token
    token_index = 0
    prev_line_token = None

    def add_token(self, kind: str, five_tuple: tuple, line: str, s_row: int, value: str) -> None:
        """
        Add an InputToken to the results list.

        Subclasses could override this method to filter out specific tokens.
        """
        tok = InputToken(kind, value)
        tok.five_tuple = five_tuple
        tok.index = self.token_index
        # Bump the token index.
        self.token_index += 1
        tok.line = line
        tok.line_number = s_row
        self.results.append(tok)
    #@+node:ekr.20191110170551.1: *4* tokenizer.check_results
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
    #@+node:ekr.20191110165235.3: *4* tokenizer.create_input_tokens
    def create_input_tokens(self, contents: str, tokens: Generator) -> list[InputToken]:
        """
        Generate a list of Token's from tokens, a list of 5-tuples.
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
        for token in tokens:
            self.do_token(contents, token)
        # Print results when tracing.
        self.check_results(contents)
        # Return results, as a list.
        return self.results
    #@+node:ekr.20191110165235.4: *4* tokenizer.do_token (the gem)
    header_has_been_shown = False

    def do_token(self, contents: str, five_tuple: tuple) -> None:
        """
        Handle the given token, optionally including between-token whitespace.

        This is part of the "gem".

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
    #@-others
#@-others

if __name__ == '__main__':
    assert glob  ###
    ### main()  # pragma: no cover
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
