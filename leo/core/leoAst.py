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
    leoAst.py --help
    leoAst.py [--fstringify | --fstringify-diff | --orange | --orange-diff] PATHS
    leoAst.py --py-cov [ARGS]
    leoAst.py --pytest [ARGS]
    leoAst.py --unittest [ARGS]

examples:
    --py-cov "-f TestOrange"
    --pytest "-f TestOrange"
    --unittest TestOrange

positional arguments:
  PATHS              directory or list of files

optional arguments:
  -h, --help         show this help message and exit
  --fstringify       leonine fstringify
  --fstringify-diff  show fstringify diff
  --orange           leonine Black
  --orange-diff      show orange diff
  --py-cov           run pytest --cov on leoAst.py
  --pytest           run pytest on leoAst.py
  --unittest         run unittest on leoAst.py


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
import pprint
import re
import sys
import textwrap
import tokenize
import traceback
from typing import Any, Generator, Optional, Union

Node = ast.AST
Settings = Optional[dict[str, Any]]
v1, v2, junk1, junk2, junk3 = sys.version_info
py_version = (v1, v2)

#@-<< leoAst imports & annotations >>
#@+<< leoAst data >>
#@+node:ekr.20220821044107.1: ** << leoAst data >>

# Async tokens exist only in Python 3.5 and 3.6.
# https://docs.python.org/3/library/token.html
has_async_tokens = (3, 5) <= py_version <= (3, 6)
#@-<< leoAst data >>
#@+others
#@+node:ekr.20191226175251.1: **  class LeoGlobals
#@@nosearch


class LeoGlobals:  # pragma: no cover
    """
    Simplified version of functions in leoGlobals.py.
    """

    total_time = 0.0  # For unit testing.

    #@+others
    #@+node:ekr.20191226175903.1: *3* LeoGlobals._caller_name
    def _caller_name(self, n: int) -> str:
        """Return the name of the caller n levels back in the call stack."""
        try:
            # Get the function name from the call stack.
            frame = sys._getframe(n)  # The stack frame, n levels up.
            code = frame.f_code  # The code object
            locals_ = frame.f_locals  # The local namespace.
            name = code.co_name
            obj = locals_.get("self")
            if obj and name == "__init__":
                return f"{obj.__class__.__name__}.{name}"
            return name
        except ValueError:
            # The stack is not deep enough OR
            # sys._getframe does not exist on this platform.
            return ""
        except Exception:
            return ""  # "<no caller name>"
    #@+node:ekr.20230208055034.1: *3* LeoGlobals.caller
    def caller(self, i: int = 1) -> str:
        """Return the caller name i levels up the call stack."""
        return self.callers(i + 1).split(",")[0]
    #@+node:ekr.20191226175426.1: *3* LeoGlobals.callers
    def callers(self, n: int = 4) -> str:
        """
        Return a string containing a comma-separated list of the callers
        of the function that called g.caller_list.
        """
        i, result = 2, []
        while True:
            s = self._caller_name(n=i)
            if s:
                result.append(s)
            if not s or len(result) >= n:
                break
            i += 1
        return ','.join(reversed(result))
    #@+node:ekr.20191226190709.1: *3* leoGlobals.es_exception & helper
    def es_exception(self) -> None:
        typ, val, tb = sys.exc_info()
        for line in traceback.format_exception(typ, val, tb):
            print(line)
    #@+node:ekr.20191226192030.1: *4* LeoGlobals.getLastTracebackFileAndLineNumber
    def getLastTracebackFileAndLineNumber(self) -> tuple[str, int]:
        typ, val, tb = sys.exc_info()
        if typ == SyntaxError:
            # IndentationError is a subclass of SyntaxError.
            # SyntaxError *does* have 'filename' and 'lineno' attributes.
            return val.filename, val.lineno
        #
        # Data is a list of tuples, one per stack entry.
        # The tuples have the form (filename, lineNumber, functionName, text).
        data = traceback.extract_tb(tb)
        item = data[-1]  # Get the item at the top of the stack.
        filename, n, functionName, text = item
        return filename, n
    #@+node:ekr.20191226190425.1: *3* LeoGlobals.plural
    def plural(self, obj: Any) -> str:
        """Return "s" or "" depending on n."""
        if isinstance(obj, (list, tuple, str)):
            n = len(obj)
        else:
            n = obj
        return '' if n == 1 else 's'
    #@+node:ekr.20191226175441.1: *3* LeoGlobals.print_obj
    def print_obj(self, obj: Any, *, tag: str = None) -> None:
        """Print an object."""
        print(self.to_string(obj, tag=tag))
    #@+node:ekr.20220327120618.1: *3* LeoGlobals.short_file_name
    def short_file_name(self, fileName: str) -> str:
        """Return the base name of a path."""
        return os.path.basename(fileName) if fileName else ''
    #@+node:ekr.20191226190131.1: *3* LeoGlobals.split_lines
    def split_lines(self, s: str) -> list[str]:
        """Split s into lines, preserving the number of lines and
        the endings of all lines, including the last line."""
        if s:
            return s.splitlines(True)  # This is a Python string function!
        return []
    #@+node:ekr.20200220065737.1: *3* LeoGlobals.to_string
    def to_string(self, obj: Any, *, indent: int = 0, tag: str = None, width: int = 120) -> str:
        """
        Pretty print any Python object to a string.
        """
        if not isinstance(obj, str):
            result = pprint.pformat(obj, indent=indent, width=width)
        elif "\n" not in obj:
            result = repr(obj)
        else:
            # Return the enumerated lines of the string.
            lines = "".join([f"  {i:4}: {z!r}\n" for i, z in enumerate(self.split_lines(obj))])
            result = f"[\n{lines}]\n"
        return f"{tag.strip()}: {result}" if tag and tag.strip() else result
    #@+node:ekr.20191226190844.1: *3* LeoGlobals.to_encoded_string
    def to_encoded_string(self, s: Any, *, encoding: str = 'utf-8') -> bytes:
        """Convert unicode string to an encoded string."""
        if not isinstance(s, str):
            return s
        try:
            s = s.encode(encoding, "strict")
        except UnicodeError:
            s = s.encode(encoding, "replace")
            print(f"to_encoded_string: Error converting {s!r} to {encoding}")
        return s
    #@+node:ekr.20191226190006.1: *3* LeoGlobals.to_unicode
    def to_unicode(self, s: Any, *, encoding: str = 'utf-8') -> str:
        """Convert bytes to unicode if necessary."""
        tag = 'g.to_unicode'
        if isinstance(s, str):
            return s
        if not isinstance(s, bytes):
            print(f"{tag}: bad s: {s!r}")
            return ''
        b: bytes = s
        try:
            s2 = b.decode(encoding, 'strict')
        except(UnicodeDecodeError, UnicodeError):  # noqa
            s2 = b.decode(encoding, 'replace')
            print(f"{tag}: unicode error. encoding: {encoding!r}, s2:\n{s2!r}")
            g.trace(g.callers())
        except Exception:
            g.es_exception()
            print(f"{tag}: unexpected error! encoding: {encoding!r}, s2:\n{s2!r}")
            g.trace(g.callers())
        return s2
    #@+node:ekr.20191226175436.1: *3* LeoGlobals.trace
    def trace(self, *args: Any) -> None:
        """Print the name of the calling function followed by all the args."""
        name = self._caller_name(2)
        if name.endswith(".pyc"):
            name = name[:-1]
        args_s = " ".join(str(z) for z in args)
        print(f"{name} {args_s}")
    #@+node:ekr.20191226190241.1: *3* LeoGlobals.truncate
    def truncate(self, s: str, n: int) -> str:
        """Return s truncated to n characters."""
        if len(s) <= n:
            return s
        s2 = s[: n - 3] + f"...({len(s)})"
        return s2 + '\n' if s.endswith('\n') else s2
    #@-others
#@+node:ekr.20200702114522.1: **  leoAst.py: top-level commands
# Don't bother covering top-level commands.
if 1:  # pragma: no cover
    #@+others
    #@+node:ekr.20200702114557.1: *3* command: fstringify_command
    def fstringify_command(files: list[str]) -> None:
        """
        Entry point for --fstringify.

        Fstringify the given file, overwriting the file.
        """
        for filename in files:
            if os.path.exists(filename):
                print(f"fstringify {filename}")
                Fstringify().fstringify_file_silent(filename)
            else:
                print(f"file not found: {filename}")
    #@+node:ekr.20200702121222.1: *3* command: fstringify_diff_command
    def fstringify_diff_command(files: list[str]) -> None:
        """
        Entry point for --fstringify-diff.

        Print the diff that would be produced by fstringify.
        """
        for filename in files:
            if os.path.exists(filename):
                print(f"fstringify-diff {filename}")
                Fstringify().fstringify_file_diff(filename)
            else:
                print(f"file not found: {filename}")
    #@+node:ekr.20200702115002.1: *3* command: orange_command
    def orange_command(files: list[str], settings: Settings = None) -> None:

        for filename in files:
            if os.path.exists(filename):
                # print(f"orange {filename}")
                Orange(settings).beautify_file(filename)
            else:
                print(f"file not found: {filename}")
        # print(f"Beautify done: {len(files)} files")
    #@+node:ekr.20200702121315.1: *3* command: orange_diff_command
    def orange_diff_command(files: list[str], settings: Settings = None) -> None:

        for filename in files:
            if os.path.exists(filename):
                print(f"orange-diff {filename}")
                Orange(settings).beautify_file_diff(filename)
            else:
                print(f"file not found: {filename}")
    #@-others
#@+node:ekr.20160521104628.1: **  leoAst.py: top-level utils
if 1:  # pragma: no cover
    #@+others
    #@+node:ekr.20220404062739.1: *3* function: scan_ast_args
    def scan_ast_args() -> tuple[Any, dict[str, Any], list[str], bool]:
        description = textwrap.dedent("""\
            Execute fstringify or beautify commands contained in leoAst.py.
        """)
        parser = argparse.ArgumentParser(
            description=description,
            formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument('PATHS', nargs='*', help='directory or list of files')
        group = parser.add_mutually_exclusive_group(required=False)  # Don't require any args.
        add = group.add_argument
        add('--fstringify', dest='f', action='store_true',
            help='fstringify PATHS')
        add('--fstringify-diff', dest='fd', action='store_true',
            help='fstringify diff PATHS')
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
        add2('--recursive', dest='recursive', action='store_true',
            help='include directories recursively')
        add2('--tab-width', dest='tab_width', metavar='N', type=int,
            help='tab-width (default -4)')
        # Create the return values, using EKR's prefs as the defaults.
        parser.set_defaults(
            allow_joined=False,
            max_join=0,
            max_split=0,
            recursive=False,
            tab_width=4,
        )
        args = parser.parse_args()
        files = args.PATHS
        recursive = args.recursive
        # Create the settings dict, ensuring proper values.
        settings_dict: dict[str, Any] = {
            'allow_joined_strings': bool(args.allow_joined),
            'max_join_line_length': abs(args.max_join),
            'max_split_line_length': abs(args.max_split),
            'tab_width': abs(args.tab_width),  # Must be positive!
        }
        return args, settings_dict, files, recursive
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
        s = g.to_unicode(bb, encoding=e)
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
    #@+node:ekr.20200113154120.1: *3* functions: tokens
    #@+node:ekr.20191223093539.1: *4* function: find_anchor_token
    def find_anchor_token(node: Node, global_token_list: list[Token]) -> Optional[Token]:
        """
        Return the anchor_token for node, a token such that token.node == node.

        The search starts at node, and then all the usual child nodes.
        """

        node1 = node

        def anchor_token(node: Node) -> Optional[Token]:
            """Return the anchor token in node.token_list"""
            # Careful: some tokens in the token list may have been killed.
            for token in get_node_token_list(node, global_token_list):
                if is_ancestor(node1, token):
                    return token
            return None

        # This table only has to cover fields for ast.Nodes that
        # won't have any associated token.

        fields = (
                        # Common...
            'elt', 'elts', 'body', 'value',  # Less common...
            'dims', 'ifs', 'names', 's',
            'test', 'values', 'targets',
        )
        while node:
            # First, try the node itself.
            token = anchor_token(node)
            if token:
                return token
            # Second, try the most common nodes w/o token_lists:
            if isinstance(node, ast.Call):
                node = node.func
            elif isinstance(node, ast.Tuple):
                node = node.elts  # type:ignore
            # Finally, try all other nodes.
            else:
                # This will be used rarely.
                for field in fields:
                    node = getattr(node, field, None)
                    if node:
                        token = anchor_token(node)
                        if token:
                            return token
                else:
                    break
        return None
    #@+node:ekr.20191231160225.1: *4* function: find_paren_token
    def find_paren_token(i: int, global_token_list: list[Token]) -> int:
        """Return i of the next paren token, starting at tokens[i]."""
        while i < len(global_token_list):
            token = global_token_list[i]
            if token.kind == 'op' and token.value in '()':
                return i
            if is_significant_token(token):
                break
            i += 1
        return None
    #@+node:ekr.20200113110505.4: *4* function: get_node_tokens_list
    def get_node_token_list(node: Node, global_tokens_list: list[Token]) -> list[Token]:
        """
        tokens_list must be the global tokens list.
        Return the tokens assigned to the node, or [].
        """
        i = getattr(node, 'first_i', None)
        j = getattr(node, 'last_i', None)
        if i is None:
            assert j is None, g.callers()
            return []
        if False:
            name = node.__class__.__name__
            if abs(i - j) > 3:
                tag = f"get_node_token_list: {name} {i}..{j}"
                g.print_obj(global_tokens_list[i : j + 1], tag=tag)
            else:
                g.trace(f"{i!r:>3}..{j!r:3} {name} {global_tokens_list[i : j + 1]}")
        return global_tokens_list[i : j + 1]
    #@+node:ekr.20191124123830.1: *4* function: is_significant & is_significant_token
    def is_significant(kind: str, value: str) -> bool:
        """
        Return True if (kind, value) represent a token that can be used for
        syncing generated tokens with the token list.
        """
        # Making 'endmarker' significant ensures that all tokens are synced.
        return (
            kind in ('async', 'await', 'endmarker', 'name', 'number', 'string') or
            kind == 'op' and value not in ',;()')

    def is_significant_token(token: Token) -> bool:
        """Return True if the given token is a synchronizing token"""
        return is_significant(token.kind, token.value)
    #@+node:ekr.20191224093336.1: *4* function: match_parens
    def match_parens(filename: str, i: int, j: int, tokens: list[Token]) -> int:
        """Match parens in tokens[i:j]. Return the new j."""
        if j >= len(tokens):
            return len(tokens)
        # Calculate paren level...
        level = 0
        for n in range(i, j + 1):
            token = tokens[n]
            if token.kind == 'op' and token.value == '(':
                level += 1
            if token.kind == 'op' and token.value == ')':
                if level == 0:
                    break
                level -= 1
        # Find matching ')' tokens *after* j.
        if level > 0:
            while level > 0 and j + 1 < len(tokens):
                token = tokens[j + 1]
                if token.kind == 'op' and token.value == ')':
                    level -= 1
                elif token.kind == 'op' and token.value == '(':
                    level += 1
                elif is_significant_token(token):
                    break
                j += 1
        if level != 0:  # pragma: no cover.
            line_n = tokens[i].line_number
            raise AssignLinksError(
                f"\n"
                f"Unmatched parens: level={level}\n"
                f"            file: {filename}\n"
                f"            line: {line_n}\n")
        return j
    #@+node:ekr.20191223053324.1: *4* function: tokens_for_node
    def tokens_for_node(filename: str, node: Node, global_token_list: list[Token]) -> list[Token]:
        """Return the list of all tokens descending from node."""
        # Find any token descending from node.
        token = find_anchor_token(node, global_token_list)
        if not token:
            if 0:  # A good trace for debugging.
                print('')
                g.trace('===== no tokens', node.__class__.__name__)
            return []
        assert is_ancestor(node, token)
        # Scan backward.
        i = first_i = token.index
        while i >= 0:
            token2 = global_token_list[i - 1]
            if getattr(token2, 'node', None):
                if is_ancestor(node, token2):
                    first_i = i - 1
                else:
                    break
            i -= 1
        # Scan forward.
        j = last_j = token.index
        while j + 1 < len(global_token_list):
            token2 = global_token_list[j + 1]
            if getattr(token2, 'node', None):
                if is_ancestor(node, token2):
                    last_j = j + 1
                else:
                    break
            j += 1
        last_j = match_parens(filename, first_i, last_j, global_token_list)
        results = global_token_list[first_i : last_j + 1]
        return results
    #@+node:ekr.20200101030236.1: *4* function: tokens_to_string
    def tokens_to_string(tokens: list[Token]) -> str:
        """Return the string represented by the list of tokens."""
        if tokens is None:
            # This indicates an internal error.
            print('')
            g.trace('===== token list is None ===== ')
            print('')
            return ''
        return ''.join([z.to_string() for z in tokens])
    #@+node:ekr.20191223095408.1: *3* node/token nodes...
    # Functions that associate tokens with nodes.
    #@+node:ekr.20200120082031.1: *4* function: find_statement_node
    def find_statement_node(node: Node) -> Optional[Node]:
        """
        Return the nearest statement node.
        Return None if node has only Module for a parent.
        """
        if isinstance(node, ast.Module):
            return None
        parent = node
        while parent:
            if is_statement_node(parent):
                return parent
            parent = parent.parent
        return None
    #@+node:ekr.20191223054300.1: *4* function: is_ancestor
    def is_ancestor(node: Node, token: Token) -> bool:
        """Return True if node is an ancestor of token."""
        t_node = token.node
        if not t_node:
            assert token.kind == 'killed', repr(token)
            return False
        while t_node:
            if t_node == node:
                return True
            t_node = t_node.parent
        return False
    #@+node:ekr.20200120082300.1: *4* function: is_long_statement
    def is_long_statement(node: Node) -> bool:
        """
        Return True if node is an instance of a node that might be split into
        shorter lines.
        """
        return isinstance(node, (
            ast.Assign, ast.AnnAssign, ast.AsyncFor, ast.AsyncWith, ast.AugAssign,
            ast.Call, ast.Delete, ast.ExceptHandler, ast.For, ast.Global,
            ast.If, ast.Import, ast.ImportFrom,
            ast.Nonlocal, ast.Return, ast.While, ast.With, ast.Yield, ast.YieldFrom))
    #@+node:ekr.20200120110005.1: *4* function: is_statement_node
    def is_statement_node(node: Node) -> bool:
        """Return True if node is a top-level statement."""
        return is_long_statement(node) or isinstance(node, (
            ast.Break, ast.Continue, ast.Pass, ast.Try))
    #@+node:ekr.20191231082137.1: *4* function: nearest_common_ancestor
    def nearest_common_ancestor(node1: Node, node2: Node) -> Optional[Node]:
        """
        Return the nearest common ancestor node for the given nodes.

        The nodes must have parent links.
        """

        def parents(node: Node) -> list[Node]:
            aList = []
            while node:
                aList.append(node)
                node = node.parent
            return list(reversed(aList))

        result = None
        parents1 = parents(node1)
        parents2 = parents(node2)
        while parents1 and parents2:
            parent1 = parents1.pop(0)
            parent2 = parents2.pop(0)
            if parent1 == parent2:
                result = parent1
            else:
                break
        return result
    #@+node:ekr.20191231072039.1: *3* functions: utils...
    # General utility functions on tokens and nodes.
    #@+node:ekr.20191119085222.1: *4* function: obj_id
    def obj_id(obj: Any) -> str:
        """Return the last four digits of id(obj), for dumps & traces."""
        return str(id(obj))[-4:]
    #@+node:ekr.20191231060700.1: *4* function: op_name
    #@@nobeautify

    # https://docs.python.org/3/library/ast.html

    _op_names = {
        # Binary operators.
        'Add': '+',
        'BitAnd': '&',
        'BitOr': '|',
        'BitXor': '^',
        'Div': '/',
        'FloorDiv': '//',
        'LShift': '<<',
        'MatMult': '@',  # Python 3.5.
        'Mod': '%',
        'Mult': '*',
        'Pow': '**',
        'RShift': '>>',
        'Sub': '-',
        # Boolean operators.
        'And': ' and ',
        'Or': ' or ',
        # Comparison operators
        'Eq': '==',
        'Gt': '>',
        'GtE': '>=',
        'In': ' in ',
        'Is': ' is ',
        'IsNot': ' is not ',
        'Lt': '<',
        'LtE': '<=',
        'NotEq': '!=',
        'NotIn': ' not in ',
        # Context operators.
        'AugLoad': '<AugLoad>',
        'AugStore': '<AugStore>',
        'Del': '<Del>',
        'Load': '<Load>',
        'Param': '<Param>',
        'Store': '<Store>',
        # Unary operators.
        'Invert': '~',
        'Not': ' not ',
        'UAdd': '+',
        'USub': '-',
    }

    def op_name(node: Node) -> str:
        """Return the print name of an operator node."""
        class_name = node.__class__.__name__
        assert class_name in _op_names, repr(class_name)
        return _op_names[class_name].strip()
    #@+node:ekr.20200107114452.1: *3* node/token creators...
    #@+node:ekr.20200103082049.1: *4* function: make_tokens
    def make_tokens(contents: str) -> list[Token]:
        """
        Return a list (not a generator) of Token objects corresponding to the
        list of 5-tuples generated by tokenize.tokenize.

        Perform consistency checks and handle all exceptions.
        """

        def check(contents: str, tokens: list[Token]) -> bool:
            result = tokens_to_string(tokens)
            ok = result == contents
            if not ok:
                print('\nRound-trip check FAILS')
                print('Contents...\n')
                g.print_obj(contents)
                print('\nResult...\n')
                g.print_obj(result)
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
            g.print_obj(s)
            print('')

        try:
            s1 = g.to_encoded_string(s)
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
    #@+node:ekr.20191231110051.1: *3* node/token dumpers...
    #@+node:ekr.20191027074436.1: *4* function: dump_ast
    def dump_ast(ast: Node, tag: str = 'dump_ast') -> None:
        """Utility to dump an ast tree."""
        g.print_obj(AstDumper().dump_ast(ast), tag=tag)
    #@+node:ekr.20191228095945.4: *4* function: dump_contents
    def dump_contents(contents: str, tag: str = 'Contents') -> None:
        print('')
        print(f"{tag}...\n")
        for i, z in enumerate(g.split_lines(contents)):
            print(f"{i+1:<3} ", z.rstrip())
        print('')
    #@+node:ekr.20191228095945.5: *4* function: dump_lines
    def dump_lines(tokens: list[Token], tag: str = 'Token lines') -> None:
        print('')
        print(f"{tag}...\n")
        for z in tokens:
            if z.line.strip():
                print(z.line.rstrip())
            else:
                print(repr(z.line))
        print('')
    #@+node:ekr.20191228095945.7: *4* function: dump_results
    def dump_results(tokens: list[Token], tag: str = 'Results') -> None:
        print('')
        print(f"{tag}...\n")
        print(tokens_to_string(tokens))
        print('')
    #@+node:ekr.20191228095945.8: *4* function: dump_tokens
    def dump_tokens(tokens: list[Token], tag: str = 'Tokens') -> None:
        print('')
        print(f"{tag}...\n")
        if not tokens:
            return
        print("Note: values shown are repr(value) *except* for 'string' tokens.")
        tokens[0].dump_header()
        for z in tokens:
            print(z.dump())
        print('')
    #@+node:ekr.20191228095945.9: *4* function: dump_tree
    def dump_tree(tokens: list[Token], tree: Node, tag: str = 'Tree') -> None:
        print('')
        print(f"{tag}...\n")
        print(AstDumper().dump_tree(tokens, tree))
    #@+node:ekr.20200107040729.1: *4* function: show_diffs
    def show_diffs(s1: str, s2: str, filename: str = '') -> None:
        """Print diffs between strings s1 and s2."""
        lines = list(difflib.unified_diff(
            g.split_lines(s1),
            g.split_lines(s2),
            fromfile=f"Old {filename}",
            tofile=f"New {filename}",
        ))
        print('')
        tag = f"Diffs for {filename}" if filename else 'Diffs'
        g.print_obj(lines, tag=tag)
    #@+node:ekr.20191225061516.1: *3* node/token replacers...
    # Functions that replace tokens or nodes.
    #@+node:ekr.20191231162249.1: *4* function: add_token_to_token_list
    def add_token_to_token_list(token: Token, node: Node) -> None:
        """Insert token in the proper location of node.token_list."""

        # Note: get_node_token_list returns global_tokens_list[first_i : last_i + 1]

        if getattr(node, 'first_i', None) is None:
            node.first_i = node.last_i = token.index
        else:
            node.first_i = min(node.first_i, token.index)
            node.last_i = max(node.last_i, token.index)
    #@+node:ekr.20191225055616.1: *4* function: replace_node
    def replace_node(new_node: Node, old_node: Node) -> None:
        """Replace new_node by old_node in the parse tree."""
        parent = old_node.parent
        new_node.parent = parent
        new_node.node_index = old_node.node_index
        children = parent.children
        i = children.index(old_node)
        children[i] = new_node
        fields = getattr(old_node, '_fields', None)
        if fields:
            for field in fields:
                field = getattr(old_node, field)
                if field == old_node:
                    setattr(old_node, field, new_node)
                    break
    #@+node:ekr.20191225055626.1: *4* function: replace_token
    def replace_token(token: Token, kind: str, value: str) -> None:
        """Replace kind and value of the given token."""
        if token.kind in ('endmarker', 'killed'):
            return
        token.kind = kind
        token.value = value
        token.node = None  # Should be filled later.
    #@-others
#@+node:ekr.20191027072910.1: ** Exception classes
class AssignLinksError(Exception):
    """Assigning links to ast nodes failed."""


class AstNotEqual(Exception):
    """The two given AST's are not equivalent."""

class BeautifyError(Exception):
    """Leading tabs found."""


class FailFast(Exception):
    """Abort tests in TestRunner class."""
#@+node:ekr.20220402062255.1: ** Classes
#@+node:ekr.20141012064706.18390: *3* class AstDumper
class AstDumper:  # pragma: no cover
    """A class supporting various kinds of dumps of ast nodes."""
    #@+others
    #@+node:ekr.20191112033445.1: *4* dumper.dump_tree & helper
    def dump_tree(self, tokens: list[Token], tree: Node) -> str:
        """Briefly show a tree, properly indented."""
        self.tokens = tokens
        result = [self.show_header()]
        self.dump_tree_and_links_helper(tree, 0, result)
        return ''.join(result)
    #@+node:ekr.20191125035321.1: *5* dumper.dump_tree_and_links_helper
    def dump_tree_and_links_helper(self, node: Node, level: int, result: list[str]) -> None:
        """Return the list of lines in result."""
        if node is None:
            return
        # Let block.
        indent = ' ' * 2 * level
        children: list[ast.AST] = getattr(node, 'children', [])
        node_s = self.compute_node_string(node, level)
        # Dump...
        if isinstance(node, (list, tuple)):
            for z in node:
                self.dump_tree_and_links_helper(z, level, result)
        elif isinstance(node, str):
            result.append(f"{indent}{node.__class__.__name__:>8}:{node}\n")
        elif isinstance(node, ast.AST):
            # Node and parent.
            result.append(node_s)
            # Children.
            for z in children:
                self.dump_tree_and_links_helper(z, level + 1, result)
        else:
            result.append(node_s)
    #@+node:ekr.20191125035600.1: *4* dumper.compute_node_string & helpers
    def compute_node_string(self, node: Node, level: int) -> str:
        """Return a string summarizing the node."""
        indent = ' ' * 2 * level
        parent = getattr(node, 'parent', None)
        node_id = getattr(node, 'node_index', '??')
        parent_id = getattr(parent, 'node_index', '??')
        parent_s = f"{parent_id:>3}.{parent.__class__.__name__} " if parent else ''
        class_name = node.__class__.__name__
        descriptor_s = f"{node_id}.{class_name}: {self.show_fields(class_name, node, 20)}"
        tokens_s = self.show_tokens(node, 70, 100)
        lines = self.show_line_range(node)
        full_s1 = f"{parent_s:<16} {lines:<10} {indent}{descriptor_s} "
        node_s = f"{full_s1:<62} {tokens_s}\n"
        return node_s
    #@+node:ekr.20191113223424.1: *5* dumper.show_fields
    def show_fields(self, class_name: str, node: Node, truncate_n: int) -> str:
        """Return a string showing interesting fields of the node."""
        val = ''
        if class_name == 'JoinedStr':
            values = node.values
            assert isinstance(values, list)
            # Str tokens may represent *concatenated* strings.
            results = []
            fstrings, strings = 0, 0
            for z in values:
                assert isinstance(z, (ast.FormattedValue, ast.Str))
                if isinstance(z, ast.Str):
                    results.append(z.s)
                    strings += 1
                else:
                    results.append(z.__class__.__name__)
                    fstrings += 1
            val = f"{strings} str, {fstrings} f-str"
        elif class_name == 'keyword':
            if isinstance(node.value, ast.Str):
                val = f"arg={node.arg}..Str.value.s={node.value.s}"
            elif isinstance(node.value, ast.Name):
                val = f"arg={node.arg}..Name.value.id={node.value.id}"
            else:
                val = f"arg={node.arg}..value={node.value.__class__.__name__}"
        elif class_name == 'Name':
            val = f"id={node.id!r}"
        elif class_name == 'NameConstant':
            val = f"value={node.value!r}"
        elif class_name == 'Num':
            val = f"n={node.n}"
        elif class_name == 'Starred':
            if isinstance(node.value, ast.Str):
                val = f"s={node.value.s}"
            elif isinstance(node.value, ast.Name):
                val = f"id={node.value.id}"
            else:
                val = f"s={node.value.__class__.__name__}"
        elif class_name == 'Str':
            val = f"s={node.s!r}"
        elif class_name in ('AugAssign', 'BinOp', 'BoolOp', 'UnaryOp'):  # IfExp
            name = node.op.__class__.__name__
            val = f"op={_op_names.get(name, name)}"
        elif class_name == 'Compare':
            ops = ','.join([op_name(z) for z in node.ops])
            val = f"ops='{ops}'"
        else:
            val = ''
        return g.truncate(val, truncate_n)
    #@+node:ekr.20191114054726.1: *5* dumper.show_line_range
    def show_line_range(self, node: Node) -> str:

        token_list = get_node_token_list(node, self.tokens)
        if not token_list:
            return ''
        min_ = min([z.line_number for z in token_list])
        max_ = max([z.line_number for z in token_list])
        return f"{min_}" if min_ == max_ else f"{min_}..{max_}"
    #@+node:ekr.20191113223425.1: *5* dumper.show_tokens
    def show_tokens(self, node: Node, n: int, m: int) -> str:
        """
        Return a string showing node.token_list.

        Split the result if n + len(result) > m
        """
        token_list = get_node_token_list(node, self.tokens)
        result = []
        for z in token_list:
            val = None
            if z.kind == 'comment':
                val = g.truncate(z.value, 10)  # Short is good.
                result.append(f"{z.kind}.{z.index}({val})")
            elif z.kind == 'name':
                val = g.truncate(z.value, 20)
                result.append(f"{z.kind}.{z.index}({val})")
            elif z.kind == 'newline':
                result.append(f"{z.kind}.{z.index}")
            elif z.kind == 'number':
                result.append(f"{z.kind}.{z.index}({z.value})")
            elif z.kind == 'op':
                result.append(f"{z.kind}.{z.index}({z.value})")
            elif z.kind == 'string':
                val = g.truncate(z.value, 30)
                result.append(f"{z.kind}.{z.index}({val})")
            elif z.kind == 'ws':
                result.append(f"{z.kind}.{z.index}({len(z.value)})")
            else:
                # Indent, dedent, encoding, etc.
                # Don't put a blank.
                continue
            if result and result[-1] != ' ':
                result.append(' ')
        # split the line if it is too long.
        line, lines = [], []
        for r in result:
            line.append(r)
            if n + len(''.join(line)) >= m:
                lines.append(''.join(line))
                line = []
        lines.append(''.join(line))
        pad = '\n' + ' ' * n
        return pad.join(lines)
    #@+node:ekr.20191110165235.5: *4* dumper.show_header
    def show_header(self) -> str:
        """Return a header string, but only the fist time."""
        return (
            f"{'parent':<16} {'lines':<10} {'node':<34} {'tokens'}\n"
            f"{'======':<16} {'=====':<10} {'====':<34} {'======'}\n")
    #@+node:ekr.20141012064706.18392: *4* dumper.dump_ast & helper
    annotate_fields = False
    include_attributes = False
    indent_ws = ' '

    def dump_ast(self, node: Node, level: int = 0) -> str:
        """
        Dump an ast tree. Adapted from ast.dump.
        """
        sep1 = '\n%s' % (self.indent_ws * (level + 1))
        if isinstance(node, ast.AST):
            fields = [(a, self.dump_ast(b, level + 1)) for a, b in self.get_fields(node)]
            if self.include_attributes and node._attributes:
                fields.extend([(a, self.dump_ast(getattr(node, a), level + 1))
                    for a in node._attributes])
            if self.annotate_fields:
                aList = ['%s=%s' % (a, b) for a, b in fields]
            else:
                aList = [b for a, b in fields]
            name = node.__class__.__name__
            sep = '' if len(aList) <= 1 else sep1
            return '%s(%s%s)' % (name, sep, sep1.join(aList))
        if isinstance(node, list):
            sep = sep1
            return 'LIST[%s]' % ''.join(
                ['%s%s' % (sep, self.dump_ast(z, level + 1)) for z in node])
        return repr(node)
    #@+node:ekr.20141012064706.18393: *5* dumper.get_fields
    def get_fields(self, node: Node) -> Generator:

        return (
            (a, b) for a, b in ast.iter_fields(node)
                if a not in ['ctx',] and b not in (None, [])
        )
    #@-others
#@+node:ekr.20191222083453.1: *3* class Fstringify
class Fstringify:
    """A class to fstringify files."""

    silent = True  # for pytest. Defined in all entries.
    line_number = 0
    line = ''

    #@+others
    #@+node:ekr.20191222083947.1: *4* fs.fstringify
    def fstringify(self, contents: str, filename: str, tokens: list[Token], tree: Node) -> str:
        """
        Fstringify.fstringify:

        f-stringify the sources given by (tokens, tree).

        Return the resulting string.
        """
        self.filename = filename
        self.tokens = tokens
        self.tree = tree
        # Prepass: reassign tokens.
        ReassignTokens().reassign(filename, tokens, tree)
        # Main pass.
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.BinOp)
                and op_name(node.op) == '%'
                and isinstance(node.left, ast.Str)
            ):
                self.make_fstring(node)
        results = tokens_to_string(self.tokens)
        return results
    #@+node:ekr.20200103054101.1: *4* fs.fstringify_file (entry)
    def fstringify_file(self, filename: str) -> bool:  # pragma: no cover
        """
        Fstringify.fstringify_file.

        The entry point for the fstringify-file command.

        f-stringify the given external file with the Fstrinfify class.

        Return True if the file was changed.
        """
        tag = 'fstringify-file'
        self.filename = filename
        self.silent = False
        tog = TokenOrderGenerator()
        try:
            contents, encoding, tokens, tree = tog.init_from_file(filename)
            if not contents or not tokens or not tree:
                print(f"{tag}: Can not fstringify: {filename}")
                return False
            results = self.fstringify(contents, filename, tokens, tree)
        except Exception as e:
            print(e)
            return False
        # Something besides newlines must change.
        changed = regularize_nls(contents) != regularize_nls(results)
        status = 'Wrote' if changed else 'Unchanged'
        print(f"{tag}: {status:>9}: {filename}")
        if changed:
            write_file(filename, results, encoding=encoding)
        return changed
    #@+node:ekr.20200103065728.1: *4* fs.fstringify_file_diff (entry)
    def fstringify_file_diff(self, filename: str) -> bool:  # pragma: no cover
        """
        Fstringify.fstringify_file_diff.

        The entry point for the diff-fstringify-file command.

        Print the diffs that would result from the fstringify-file command.

        Return True if the file would be changed.
        """
        tag = 'diff-fstringify-file'
        self.filename = filename
        self.silent = False
        tog = TokenOrderGenerator()
        try:
            contents, encoding, tokens, tree = tog.init_from_file(filename)
            if not contents or not tokens or not tree:
                return False
            results = self.fstringify(contents, filename, tokens, tree)
        except Exception as e:
            print(e)
            return False
        # Something besides newlines must change.
        changed = regularize_nls(contents) != regularize_nls(results)
        if changed:
            show_diffs(contents, results, filename=filename)
        else:
            print(f"{tag}: Unchanged: {filename}")
        return changed
    #@+node:ekr.20200112060218.1: *4* fs.fstringify_file_silent (entry)
    def fstringify_file_silent(self, filename: str) -> bool:  # pragma: no cover
        """
        Fstringify.fstringify_file_silent.

        The entry point for the silent-fstringify-file command.

        fstringify the given file, suppressing all but serious error messages.

        Return True if the file would be changed.
        """
        self.filename = filename
        self.silent = True
        tog = TokenOrderGenerator()
        try:
            contents, encoding, tokens, tree = tog.init_from_file(filename)
            if not contents or not tokens or not tree:
                return False
            results = self.fstringify(contents, filename, tokens, tree)
        except Exception as e:
            print(e)
            return False
        # Something besides newlines must change.
        changed = regularize_nls(contents) != regularize_nls(results)
        status = 'Wrote' if changed else 'Unchanged'
        # Write the results.
        print(f"{status:>9}: {filename}")
        if changed:
            write_file(filename, results, encoding=encoding)
        return changed
    #@+node:ekr.20191222095754.1: *4* fs.make_fstring & helpers
    def make_fstring(self, node: Node) -> None:
        """
        node is BinOp node representing an '%' operator.
        node.left is an ast.Str node.
        node.right represents the RHS of the '%' operator.

        Convert this tree to an f-string, if possible.
        Replace the node's entire tree with a new ast.Str node.
        Replace all the relevant tokens with a single new 'string' token.
        """
        trace = False
        assert isinstance(node.left, ast.Str), (repr(node.left), g.callers())
        # Careful: use the tokens, not Str.s.  This preserves spelling.
        lt_token_list = get_node_token_list(node.left, self.tokens)
        if not lt_token_list:  # pragma: no cover
            print('')
            g.trace('Error: no token list in Str')
            dump_tree(self.tokens, node)
            print('')
            return
        lt_s = tokens_to_string(lt_token_list)
        if trace:
            g.trace('lt_s:', lt_s)  # pragma: no cover
        # Get the RHS values, a list of token lists.
        values = self.scan_rhs(node.right)
        if trace:  # pragma: no cover
            for i, z in enumerate(values):
                dump_tokens(z, tag=f"RHS value {i}")
        # Compute rt_s, self.line and self.line_number for later messages.
        token0 = lt_token_list[0]
        self.line_number = token0.line_number
        self.line = token0.line.strip()
        rt_s = ''.join(tokens_to_string(z) for z in values)
        # Get the % specs in the LHS string.
        specs = self.scan_format_string(lt_s)
        if len(values) != len(specs):  # pragma: no cover
            self.message(
                f"can't create f-fstring: {lt_s!r}\n"
                f":f-string mismatch: "
                f"{len(values)} value{g.plural(len(values))}, "
                f"{len(specs)} spec{g.plural(len(specs))}")
            return
        # Replace specs with values.
        results = self.substitute_values(lt_s, specs, values)
        result = self.compute_result(lt_s, results)
        if not result:
            return
        # Remove whitespace before ! and :.
        result = self.clean_ws(result)
        # Show the results
        if trace:  # pragma: no cover
            before = (lt_s + ' % ' + rt_s).replace('\n', '<NL>')
            after = result.replace('\n', '<NL>')
            self.message(
                f"trace:\n"
                f":from: {before!s}\n"
                f":  to: {after!s}")
        # Adjust the tree and the token list.
        self.replace(node, result, values)
    #@+node:ekr.20191222102831.3: *5* fs.clean_ws
    ws_pat = re.compile(r'(\s+)([:!][0-9]\})')

    def clean_ws(self, s: str) -> str:
        """Carefully remove whitespace before ! and : specifiers."""
        s = re.sub(self.ws_pat, r'\2', s)
        return s
    #@+node:ekr.20191222102831.4: *5* fs.compute_result & helpers
    def compute_result(self, lt_s: str, tokens: list[Token]) -> str:
        """
        Create the final result, with various kinds of munges.

        Return the result string, or None if there are errors.
        """
        # Fail if there is a backslash within { and }.
        if not self.check_back_slashes(lt_s, tokens):
            return None  # pragma: no cover
        # Ensure consistent quotes.
        if not self.change_quotes(lt_s, tokens):
            return None  # pragma: no cover
        return tokens_to_string(tokens)
    #@+node:ekr.20200215074309.1: *6* fs.check_back_slashes
    def check_back_slashes(self, lt_s: str, tokens: list[Token]) -> bool:
        """
        Return False if any backslash appears with an {} expression.

        Tokens is a list of tokens on the RHS.
        """
        count = 0
        for z in tokens:
            if z.kind == 'op':
                if z.value == '{':
                    count += 1
                elif z.value == '}':
                    count -= 1
            if (count % 2) == 1 and '\\' in z.value:
                if not self.silent:
                    self.message(  # pragma: no cover (silent during unit tests)
                        f"can't create f-fstring: {lt_s!r}\n"
                        f":backslash in {{expr}}:")
                return False
        return True
    #@+node:ekr.20191222102831.7: *6* fs.change_quotes
    def change_quotes(self, lt_s: str, aList: list[Token]) -> bool:
        """
        Carefully check quotes in all "inner" tokens as necessary.

        Return False if the f-string would contain backslashes.

        We expect the following "outer" tokens.

        aList[0]:  ('string', 'f')
        aList[1]:  ('string',  a single or double quote.
        aList[-1]: ('string', a single or double quote matching aList[1])
        """
        # Sanity checks.
        if len(aList) < 4:
            return True  # pragma: no cover (defensive)
        if not lt_s:  # pragma: no cover (defensive)
            self.message("can't create f-fstring: no lt_s!")
            return False
        delim = lt_s[0]
        # Check tokens 0, 1 and -1.
        token0 = aList[0]
        token1 = aList[1]
        token_last = aList[-1]
        for token in token0, token1, token_last:
            # These are the only kinds of tokens we expect to generate.
            ok = (
                token.kind == 'string' or
                token.kind == 'op' and token.value in '{}')
            if not ok:  # pragma: no cover (defensive)
                self.message(
                    f"unexpected token: {token.kind} {token.value}\n"
                    f":           lt_s: {lt_s!r}")
                return False
        # These checks are important...
        if token0.value != 'f':
            return False  # pragma: no cover (defensive)
        val1 = token1.value
        if delim != val1:
            return False  # pragma: no cover (defensive)
        val_last = token_last.value
        if delim != val_last:
            return False  # pragma: no cover (defensive)
        #
        # Check for conflicting delims, preferring f"..." to f'...'.
        for delim in ('"', "'"):
            aList[1] = aList[-1] = Token('string', delim)
            for z in aList[2:-1]:
                if delim in z.value:
                    break
            else:
                return True
        if not self.silent:  # pragma: no cover (silent unit test)
            self.message(
                f"can't create f-fstring: {lt_s!r}\n"
                f":   conflicting delims:")
        return False
    #@+node:ekr.20191222102831.6: *5* fs.munge_spec
    def munge_spec(self, spec: str) -> tuple[str, str]:
        """
        Return (head, tail).

        The format is spec !head:tail or :tail

        Example specs: s2, r3
        """
        # To do: handle more specs.
        head, tail = [], []
        if spec.startswith('+'):
            pass  # Leave it alone!
        elif spec.startswith('-'):
            tail.append('>')
            spec = spec[1:]
        if spec.endswith('s'):
            spec = spec[:-1]
        if spec.endswith('r'):
            head.append('r')
            spec = spec[:-1]
        tail_s = ''.join(tail) + spec
        head_s = ''.join(head)
        return head_s, tail_s
    #@+node:ekr.20191222102831.9: *5* fs.scan_format_string
    # format_spec ::=  [[fill]align][sign][#][0][width][,][.precision][type]
    # fill        ::=  <any character>
    # align       ::=  "<" | ">" | "=" | "^"
    # sign        ::=  "+" | "-" | " "
    # width       ::=  integer
    # precision   ::=  integer
    # type        ::=  "b" | "c" | "d" | "e" | "E" | "f" | "F" | "g" | "G" | "n" | "o" | "s" | "x" | "X" | "%"

    format_pat = re.compile(r'%(([+-]?[0-9]*(\.)?[0.9]*)*[bcdeEfFgGnoxrsX]?)')

    def scan_format_string(self, s: str) -> list[re.Match]:
        """Scan the format string s, returning a list match objects."""
        result = list(re.finditer(self.format_pat, s))
        return result
    #@+node:ekr.20191222104224.1: *5* fs.scan_rhs
    def scan_rhs(self, node: Node) -> list[list[Token]]:
        """
        Scan the right-hand side of a potential f-string.

        Return a list of the token lists for each element.
        """
        trace = False
        # First, Try the most common cases.
        if isinstance(node, ast.Str):
            token_list = get_node_token_list(node, self.tokens)
            return [token_list]
        if isinstance(node, (list, tuple, ast.Tuple)):
            result = []
            elts = node.elts if isinstance(node, ast.Tuple) else node
            for i, elt in enumerate(elts):
                tokens = tokens_for_node(self.filename, elt, self.tokens)
                result.append(tokens)
                if trace:  # pragma: no cover
                    g.trace(f"item: {i}: {elt.__class__.__name__}")
                    g.print_obj(tokens, tag=f"Tokens for item {i}")
            return result
        # Now we expect only one result.
        tokens = tokens_for_node(self.filename, node, self.tokens)
        return [tokens]
    #@+node:ekr.20191226155316.1: *5* fs.substitute_values
    def substitute_values(self, lt_s: str, specs: list[re.Match], values: list[list[Token]]) -> list[Token]:
        """
        Replace specifiers with values in lt_s string.

        Double { and } as needed.
        """
        i, results = 0, [Token('string', 'f')]
        for spec_i, m in enumerate(specs):
            value = tokens_to_string(values[spec_i])
            start, end, spec = m.start(0), m.end(0), m.group(1)
            if start > i:
                val = lt_s[i:start].replace('{', '{{').replace('}', '}}')
                results.append(Token('string', val[0]))
                results.append(Token('string', val[1:]))
            head, tail = self.munge_spec(spec)
            results.append(Token('op', '{'))
            results.append(Token('string', value))
            if head:
                results.append(Token('string', '!'))
                results.append(Token('string', head))
            if tail:
                results.append(Token('string', ':'))
                results.append(Token('string', tail))
            results.append(Token('op', '}'))
            i = end
        # Add the tail.
        tail = lt_s[i:]
        if tail:
            tail = tail.replace('{', '{{').replace('}', '}}')
            results.append(Token('string', tail[:-1]))
            results.append(Token('string', tail[-1]))
        return results
    #@+node:ekr.20200214142019.1: *4* fs.message
    def message(self, message: str) -> None:  # pragma: no cover.
        """
        Print one or more message lines aligned on the first colon of the message.
        """
        # Print a leading blank line.
        print('')
        # Calculate the padding.
        lines = g.split_lines(message)
        pad = max(lines[0].find(':'), 30)
        # Print the first line.
        z = lines[0]
        i = z.find(':')
        if i == -1:
            print(z.rstrip())
        else:
            print(f"{z[:i+2].strip():>{pad+1}} {z[i+2:].strip()}")
        # Print the remaining message lines.
        for z in lines[1:]:
            if z.startswith('<'):
                # Print left aligned.
                print(z[1:].strip())
            elif z.startswith(':') and -1 < z[1:].find(':') <= pad:
                # Align with the first line.
                i = z[1:].find(':')
                print(f"{z[1:i+2].strip():>{pad+1}} {z[i+2:].strip()}")
            elif z.startswith('>'):
                # Align after the aligning colon.
                print(f"{' ':>{pad+2}}{z[1:].strip()}")
            else:
                # Default: Put the entire line after the aligning colon.
                print(f"{' ':>{pad+2}}{z.strip()}")
        # Print the standard message lines.
        file_s = f"{'file':>{pad}}"
        ln_n_s = f"{'line number':>{pad}}"
        line_s = f"{'line':>{pad}}"
        print(
            f"{file_s}: {self.filename}\n"
            f"{ln_n_s}: {self.line_number}\n"
            f"{line_s}: {self.line!r}")
    #@+node:ekr.20191225054848.1: *4* fs.replace
    def replace(self, node: Node, s: str, values: list[list[Token]]) -> None:
        """
        Replace node with an ast.Str node for s.
        Replace all tokens in the range of values with a single 'string' node.
        """
        # Replace the tokens...
        tokens = tokens_for_node(self.filename, node, self.tokens)
        i1 = i = tokens[0].index
        replace_token(self.tokens[i], 'string', s)
        j = 1
        while j < len(tokens):
            replace_token(self.tokens[i1 + j], 'killed', '')
            j += 1
        # Replace the node.
        new_node = ast.Str()
        new_node.s = s
        replace_node(new_node, node)
        # Update the token.
        token = self.tokens[i1]
        token.node = new_node
        # Update the token list.
        add_token_to_token_list(token, new_node)
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
            'max_join_line_length',
            'max_split_line_length',
            'orange',
            'tab_width',
        )
        # For mypy...
        self.kind: str = ''
        # Default settings...
        self.allow_joined_strings = False  # EKR's preference.
        self.max_join_line_length = 88
        self.max_split_line_length = 88
        self.tab_width = 4
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
    #@+node:ekr.20200107165250.8: *4* orange: Entries
    #@+node:ekr.20200107173542.1: *5* orange.beautify (main token loop)
    def oops(self) -> None:  # pragma: no cover
        g.trace(f"Unknown kind: {self.kind}")

    def beautify(self, contents: str, filename: str, tokens: list[Token], tree: Node,

        max_join_line_length: Optional[int] = None, max_split_line_length: Optional[int] = None,
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
        self.level = 0  # Set only by do_indent and do_dedent.
        self.lws = ''  # Leading whitespace.
        self.paren_level = 0  # Number of unmatched '(' tokens.
        self.square_brackets_stack: list[bool] = []  # A stack of bools, for self.word().
        self.state_stack: list["ParseState"] = []  # Stack of ParseState objects.
        self.val = None  # The input token's value (a string).
        self.verbatim = False  # True: don't beautify.
        #
        # Init output list and state...
        self.code_list: list[Token] = []  # The list of output tokens.
        self.tokens = tokens  # The list of input tokens.
        self.tree = tree
        self.add_token('file-start', '')
        self.push_state('file-start')
        for token in tokens:
            self.token = token
            self.kind, self.val, self.line = token.kind, token.value, token.line
            if self.verbatim:
                self.do_verbatim()
            else:
                func = getattr(self, f"do_{token.kind}", self.oops)
                func()
        # Any post pass would go here.
        return tokens_to_string(self.code_list)
    #@+node:ekr.20200107172450.1: *5* orange.beautify_file (entry)
    def beautify_file(self, filename: str) -> bool:  # pragma: no cover
        """
        Orange: Beautify the the given external file.

        Return True if the file was changed.
        """
        self.filename = filename
        tog = TokenOrderGenerator()
        contents, encoding, tokens, tree = tog.init_from_file(filename)
        if not contents or not tokens or not tree:
            return False  # #2529: Not an error.
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
        print(f"Beautified: {g.short_file_name(filename)}")
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
        tog = TokenOrderGenerator()
        contents, encoding, tokens, tree = tog.init_from_file(filename)
        if not contents or not tokens or not tree:
            print(f"{tag}: Can not beautify: {filename}")
            return False
        # fstringify.
        results = self.beautify(contents, filename, tokens, tree)
        # Something besides newlines must change.
        if regularize_nls(contents) == regularize_nls(results):
            print(f"{tag}: Unchanged: {filename}")
            return False
        # Show the diffs.
        show_diffs(contents, results, filename=filename)
        return True
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
            m = self.comment_pat.match(val)
            if m:
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
        tail: list[Token] = []
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
            # consider adding whitespace around the operators with the lowest priority(ies).
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
    def add_line_end(self) -> Token:
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
    def add_token(self, kind: str, value: Any) -> Token:
        """Add an output token to the code list."""
        tok = Token(kind, value)
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
            return (
                isinstance(node, ast.UnaryOp)
                and not isinstance(node.operand, ast.Num)
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
    #@+node:ekr.20200118120049.1: *4* orange: Split/join
    #@+node:ekr.20200107165250.34: *5* orange.split_line & helpers
    def split_line(self, node: Node, token: Token) -> bool:
        """
        Split token's line, if possible and enabled.

        Return True if the line was broken into two or more lines.
        """
        assert token.kind in ('newline', 'nl'), repr(token)
        # Return if splitting is disabled:
        if self.max_split_line_length <= 0:  # pragma: no cover (user option)
            return False
        # Return if the node can't be split.
        if not is_long_statement(node):
            return False
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
    #@+node:ekr.20200107165250.35: *6* orange.append_tail
    def append_tail(self, prefix: list[Token], tail: list[Token]) -> None:
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
        open_delim = Token(kind='lt', value=prefix[-1].value)
        value = open_delim.value.replace('(', ')').replace('[', ']').replace('{', '}')
        close_delim = Token(kind='rt', value=value)
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
    #@+node:ekr.20200107165250.36: *6* orange.find_prev_line
    def find_prev_line(self) -> list[Token]:
        """Return the previous line, as a list of tokens."""
        line = []
        for t in reversed(self.code_list[:-1]):
            if t.kind in ('hard-newline', 'line-end'):
                break
            line.append(t)
        return list(reversed(line))
    #@+node:ekr.20200107165250.37: *6* orange.find_line_prefix
    def find_line_prefix(self, token_list: list[Token]) -> list[Token]:
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
    #@+node:ekr.20200107165250.39: *5* orange.join_lines
    def join_lines(self, node: Node, token: Token) -> None:
        """
        Join preceding lines, if possible and enabled.
        token is a line_end token. node is the corresponding ast node.
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
        tail_s = tokens_to_string(tail)
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
#@+node:ekr.20191231084514.1: *3* class ReassignTokens
class ReassignTokens:
    """A class that reassigns tokens to more appropriate ast nodes."""
    #@+others
    #@+node:ekr.20191231084640.1: *4* reassign.reassign
    def reassign(self, filename: str, tokens: list[Token], tree: Node) -> None:
        """The main entry point."""
        self.filename = filename
        self.tokens = tokens
        # Just handle Call nodes.
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                self.visit_call(node)
    #@+node:ekr.20191231084853.1: *4* reassign.visit_call
    def visit_call(self, node: Node) -> None:
        """ReassignTokens.visit_call"""
        tokens = tokens_for_node(self.filename, node, self.tokens)
        node0, node9 = tokens[0].node, tokens[-1].node
        nca = nearest_common_ancestor(node0, node9)
        if not nca:
            return
        # Associate () with the call node.
        i = tokens[-1].index
        j = find_paren_token(i + 1, self.tokens)
        if j is None:
            return  # pragma: no cover
        k = find_paren_token(j + 1, self.tokens)
        if k is None:
            return  # pragma: no cover
        self.tokens[j].node = nca
        self.tokens[k].node = nca
        add_token_to_token_list(self.tokens[j], nca)
        add_token_to_token_list(self.tokens[k], nca)
    #@-others
#@+node:ekr.20191110080535.1: *3* class Token
class Token:
    """
    A class representing a 5-tuple, plus additional data.
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
        return f"Token {s}:{self.show_val(20)}"

    __str__ = __repr__


    def to_string(self) -> str:
        """Return the contribution of the token to the source file."""
        return self.value if isinstance(self.value, str) else ''
    #@+others
    #@+node:ekr.20191231114927.1: *4* token.brief_dump
    def brief_dump(self) -> str:  # pragma: no cover
        """Dump a token."""
        return (
            f"{self.index:>3} line: {self.line_number:<2} "
            f"{self.kind:>11} {self.show_val(100)}")
    #@+node:ekr.20200223022950.11: *4* token.dump
    def dump(self) -> str:  # pragma: no cover
        """Dump a token and related links."""
        # Let block.
        node_id = self.node.node_index if self.node else ''
        node_cn = self.node.__class__.__name__ if self.node else ''
        return (
            f"{self.line_number:4} "
            f"{node_id:5} {node_cn:16} "
            f"{self.index:>5} {self.kind:>11} "
            f"{self.show_val(100)}")
    #@+node:ekr.20200121081151.1: *4* token.dump_header
    def dump_header(self) -> None:  # pragma: no cover
        """Print the header for token.dump"""
        print(
            f"\n"
            f"         node    {'':10} token          token\n"
            f"line index class {'':10} index        kind value\n"
            f"==== ===== ===== {'':10} =====        ==== =====\n")
    #@+node:ekr.20191116154328.1: *4* token.error_dump
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
    #@+node:ekr.20191113095507.1: *4* token.show_val
    def show_val(self, truncate_n: int) -> str:  # pragma: no cover
        """Return the token.value field."""
        if self.kind in ('ws', 'indent'):
            val = str(len(self.value))
        elif self.kind == 'string':
            # Important: don't add a repr for 'string' tokens.
            # repr just adds another layer of confusion.
            val = g.truncate(self.value, truncate_n)
        else:
            val = g.truncate(repr(self.value), truncate_n)
        return val
    #@-others
#@+node:ekr.20191110165235.1: *3* class Tokenizer
class Tokenizer:

    """Create a list of Tokens from contents."""

    results: list[Token] = []

    #@+others
    #@+node:ekr.20191110165235.2: *4* tokenizer.add_token
    token_index = 0
    prev_line_token = None

    def add_token(self, kind: str, five_tuple: tuple, line: str, s_row: int, value: str) -> None:
        """
        Add a token to the results list.

        Subclasses could override this method to filter out specific tokens.
        """
        tok = Token(kind, value)
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
        result_lines = g.split_lines(result)
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
    def create_input_tokens(self, contents: str, tokens: Generator) -> list[Token]:
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
#@+node:ekr.20191113063144.1: *3* class TokenOrderGenerator
class TokenOrderGenerator:
    """
    A class that traverses ast (parse) trees in token order.

    Overview: https://github.com/leo-editor/leo-editor/issues/1440#issue-522090981

    Theory of operation:
    - https://github.com/leo-editor/leo-editor/issues/1440#issuecomment-573661883
    - https://leo-editor.github.io/leo-editor/appendices.html#tokenorder-classes-theory-of-operation

    How to: https://leo-editor.github.io/leo-editor/appendices.html#tokenorder-class-how-to

    Project history: https://github.com/leo-editor/leo-editor/issues/1440#issuecomment-574145510
    """

    begin_end_stack: list[str] = []
    equal_sign_spaces = True  # A flag for orange.do_equal_op
    n_nodes = 0  # The number of nodes that have been visited.
    node_index = 0  # The index into the node_stack.
    node_stack: list[ast.AST] = []  # The stack of parent nodes.
    try_stack: list[str] = []  # A stack of either '' (Try) or '*' (TryStar)

    #@+others
    #@+node:ekr.20200103174914.1: *4* tog: Init...
    #@+node:ekr.20191228184647.1: *5* tog.balance_tokens
    def balance_tokens(self, tokens: list[Token]) -> int:
        """
        TOG.balance_tokens.

        Insert two-way links between matching paren tokens.
        """
        count, stack = 0, []
        for token in tokens:
            if token.kind == 'op':
                if token.value == '(':
                    count += 1
                    stack.append(token.index)
                if token.value == ')':
                    if stack:
                        index = stack.pop()
                        tokens[index].matching_paren = token.index
                        tokens[token.index].matching_paren = index
                    else:  # pragma: no cover
                        g.trace(f"unmatched ')' at index {token.index}")
        if stack:  # pragma: no cover
            g.trace("unmatched '(' at {','.join(stack)}")
        return count
    #@+node:ekr.20191113063144.4: *5* tog.create_links (inits all ivars)
    def create_links(self, tokens: list[Token], tree: Node, file_name: str = '') -> list:
        """
        A generator creates two-way links between the given tokens and ast-tree.

        Callers should call this generator with list(tog.create_links(...))

        The sync_tokens method creates the links and verifies that the resulting
        tree traversal generates exactly the given tokens in exact order.

        tokens: the list of Token instances for the input.
                Created by make_tokens().
        tree:   the ast tree for the input.
                Created by parse_ast().
        """
        # Init all ivars.
        self.equal_sign_spaces = True  # For a special case in set_links().
        self.file_name = file_name  # For tests.
        self.level = 0  # Python indentation level.
        self.node = None  # The node being visited.
        self.tokens = tokens  # The immutable list of input tokens.
        self.tree = tree  # The tree of ast.AST nodes.
        # Traverse the tree.
        self.visit(tree)
        # Ensure that all tokens are patched.
        self.node = tree
        self.token('endmarker', '')
        # Return [] for compatibility with legacy code: list(tog.create_links).
        return []
    #@+node:ekr.20191229071733.1: *5* tog.init_from_file
    def init_from_file(self, filename: str) -> tuple[str, str, list[Token], Node]:  # pragma: no cover
        """
        Create the tokens and ast tree for the given file.
        Create links between tokens and the parse tree.
        Return (contents, encoding, tokens, tree).
        """
        self.level = 0
        self.filename = filename
        encoding, contents = read_file_with_encoding(filename)
        if not contents:
            return None, None, None, None
        self.tokens = tokens = make_tokens(contents)
        self.tree = tree = parse_ast(contents)
        self.create_links(tokens, tree)
        return contents, encoding, tokens, tree
    #@+node:ekr.20191229071746.1: *5* tog.init_from_string
    def init_from_string(self, contents: str, filename: str) -> tuple[list[Token], Node]:  # pragma: no cover
        """
        Tokenize, parse and create links in the contents string.

        Return (tokens, tree).
        """
        self.filename = filename
        self.level = 0
        self.tokens = tokens = make_tokens(contents)
        self.tree = tree = parse_ast(contents)
        self.create_links(tokens, tree)
        return tokens, tree
    #@+node:ekr.20220402052020.1: *4* tog: synchronizer...
    # The synchronizer sync tokens to nodes.
    #@+node:ekr.20200110162044.1: *5* tog.find_next_significant_token
    def find_next_significant_token(self) -> Optional[Token]:
        """
        Scan from *after* self.tokens[px] looking for the next significant
        token.

        Return the token, or None. Never change self.px.
        """
        px = self.px + 1
        while px < len(self.tokens):
            token = self.tokens[px]
            px += 1
            if is_significant_token(token):
                return token
        # This will never happen, because endtoken is significant.
        return None  # pragma: no cover
    #@+node:ekr.20191125120814.1: *5* tog.set_links
    last_statement_node = None

    def set_links(self, node: Node, token: Token) -> None:
        """Make two-way links between token and the given node."""
        # Don't bother assigning comment, comma, parens, ws and endtoken tokens.
        if token.kind == 'comment':
            # Append the comment to node.comment_list.
            comment_list: list[Token] = getattr(node, 'comment_list', [])
            node.comment_list = comment_list + [token]
            return
        if token.kind in ('endmarker', 'ws'):
            return
        if token.kind == 'op' and token.value in ',()':
            return
        # *Always* remember the last statement.
        statement = find_statement_node(node)
        if statement:
            self.last_statement_node = statement
            assert not isinstance(self.last_statement_node, ast.Module)
        if token.node is not None:  # pragma: no cover
            line_s = f"line {token.line_number}:"
            raise AssignLinksError(
                    f"       file: {self.filename}\n"
                    f"{line_s:>12} {token.line.strip()}\n"
                    f"token index: {self.px}\n"
                    f"token.node is not None\n"
                    f" token.node: {token.node.__class__.__name__}\n"
                    f"    callers: {g.callers()}")
        # Assign newlines to the previous statement node, if any.
        if token.kind in ('newline', 'nl'):
            # Set an *auxiliary* link for the split/join logic.
            # Do *not* set token.node!
            token.statement_node = self.last_statement_node
            return
        if is_significant_token(token):
            # Link the token to the ast node.
            token.node = node
            # Add the token to node's token_list.
            add_token_to_token_list(token, node)
            # Special case. Inject equal_sign_spaces into '=' tokens.
            if token.kind == 'op' and token.value == '=':
                token.equal_sign_spaces = self.equal_sign_spaces
    #@+node:ekr.20191124083124.1: *5* tog.sync_name (aka name)
    def sync_name(self, val: str) -> None:
        aList = val.split('.')
        if len(aList) == 1:
            self.sync_token('name', val)
        else:
            for i, part in enumerate(aList):
                self.sync_token('name', part)
                if i < len(aList) - 1:
                    self.sync_op('.')

    name = sync_name  # for readability.
    #@+node:ekr.20220402052102.1: *5* tog.sync_op (aka op)
    def sync_op(self, val: str) -> None:
        """
        Sync to the given operator.

        val may be '(' or ')' *only* if the parens *will* actually exist in the
        token list.
        """
        self.sync_token('op', val)

    op = sync_op  # For readability.
    #@+node:ekr.20191113063144.7: *5* tog.sync_token (aka token)
    px = -1  # Index of the previously synced token.

    def sync_token(self, kind: str, val: str) -> None:
        """
        Sync to a token whose kind & value are given. The token need not be
        significant, but it must be guaranteed to exist in the token list.

        The checks in this method constitute a strong, ever-present, unit test.

        Scan the tokens *after* px, looking for a token T matching (kind, val).
        raise AssignLinksError if a significant token is found that doesn't match T.
        Otherwise:
        - Create two-way links between all assignable tokens between px and T.
        - Create two-way links between T and self.node.
        - Advance by updating self.px to point to T.
        """
        node, tokens = self.node, self.tokens
        assert isinstance(node, ast.AST), repr(node)
        if 0:  # A Superb trace.
            g.trace(
                f"px: {self.px:4} "
                f"node: {node.__class__.__name__:<12} "
                f"significant? {int(is_significant(kind, val))} "
                f"kind/val: {kind:>10}: {val!r}")
        #
        # Step one: Look for token T.
        old_px = px = self.px + 1
        while px < len(self.tokens):
            token = tokens[px]
            if (kind, val) == (token.kind, token.value):
                break  # Success.
            if kind == token.kind == 'number':
                val = token.value
                break  # Benign: use the token's value, a string, instead of a number.
            if is_significant_token(token):  # pragma: no cover
                line_s = f"line {token.line_number}:"
                val = str(val)  # for g.truncate.
                raise AssignLinksError(
                    f"       file: {self.filename}\n"
                    f"{line_s:>12} {token.line.strip()}\n"
                    f"Looking for: {kind}.{g.truncate(val, 40)!r}\n"
                    f"      found: {token.kind}.{token.value!r}\n"
                    f"token.index: {token.index}\n")
            # Skip the insignificant token.
            px += 1
        else:  # pragma: no cover
            val = str(val)  # for g.truncate.
            raise AssignLinksError(
                 f"       file: {self.filename}\n"
                 f"Looking for: {kind}.{g.truncate(val, 40)}\n"
                 f"      found: end of token list")
        #
        # Step two: Assign *secondary* links only for newline tokens.
        #           Ignore all other non-significant tokens.
        while old_px < px:
            token = tokens[old_px]
            old_px += 1
            if token.kind in ('comment', 'newline', 'nl'):
                self.set_links(node, token)
        #
        # Step three: Set links in the found token.
        token = tokens[px]
        self.set_links(node, token)
        #
        # Step four: Advance.
        self.px = px

    token = sync_token  # For readability.
    #@+node:ekr.20191223052749.1: *4* tog: Traversal...
    #@+node:ekr.20191113063144.3: *5* tog.enter_node
    def enter_node(self, node: Node) -> None:
        """Enter a node."""
        # Update the stats.
        self.n_nodes += 1
        # Do this first, *before* updating self.node.
        node.parent = self.node
        if self.node:
            children: list[Node] = getattr(self.node, 'children', [])
            children.append(node)
            self.node.children = children
        # Inject the node_index field.
        assert not hasattr(node, 'node_index'), g.callers()
        node.node_index = self.node_index
        self.node_index += 1
        # begin_visitor and end_visitor must be paired.
        self.begin_end_stack.append(node.__class__.__name__)
        # Push the previous node.
        self.node_stack.append(self.node)
        # Update self.node *last*.
        self.node = node
    #@+node:ekr.20200104032811.1: *5* tog.leave_node
    def leave_node(self, node: Node) -> None:
        """Leave a visitor."""
        # begin_visitor and end_visitor must be paired.
        entry_name = self.begin_end_stack.pop()
        assert entry_name == node.__class__.__name__, f"{entry_name!r} {node.__class__.__name__}"
        assert self.node == node, (repr(self.node), repr(node))
        # Restore self.node.
        self.node = self.node_stack.pop()
    #@+node:ekr.20191113081443.1: *5* tog.visit
    def visit(self, node: Node) -> None:
        """Given an ast node, return a *generator* from its visitor."""
        # This saves a lot of tests.
        if node is None:
            return
        if 0:  # pragma: no cover
            # Keep this trace!
            cn = node.__class__.__name__ if node else ' '
            caller1, caller2 = g.callers(2).split(',')
            g.trace(f"{caller1:>15} {caller2:<14} {cn}")
        # More general, more convenient.
        if isinstance(node, (list, tuple)):
            for z in node or []:
                if isinstance(z, ast.AST):
                    self.visit(z)
                else:  # pragma: no cover
                    # Some fields may contain ints or strings.
                    assert isinstance(z, (int, str)), z.__class__.__name__
            return
        # We *do* want to crash if the visitor doesn't exist.
        method = getattr(self, 'do_' + node.__class__.__name__)
        # Don't even *think* about removing the parent/child links.
        # The nearest_common_ancestor function depends upon them.
        self.enter_node(node)
        method(node)
        self.leave_node(node)
    #@+node:ekr.20191113063144.13: *4* tog: Visitors...
    #@+node:ekr.20191113063144.32: *5*  tog.keyword: not called!
    # keyword arguments supplied to call (NULL identifier for **kwargs)

    # keyword = (identifier? arg, expr value)

    def do_keyword(self, node: Node) -> None:  # pragma: no cover
        """A keyword arg in an ast.Call."""
        # This should never be called.
        # tog.handle_call_arguments calls self.visit(kwarg_arg.value) instead.
        filename = getattr(self, 'filename', '<no file>')
        raise AssignLinksError(
            f"file: {filename}\n"
            f"do_keyword should never be called\n"
            f"{g.callers(8)}")
    #@+node:ekr.20191113063144.14: *5* tog: Contexts
    #@+node:ekr.20191113063144.28: *6*  tog.arg
    # arg = (identifier arg, expr? annotation)

    def do_arg(self, node: Node) -> None:
        """This is one argument of a list of ast.Function or ast.Lambda arguments."""
        self.name(node.arg)
        annotation = getattr(node, 'annotation', None)
        if annotation is not None:
            self.op(':')
            self.visit(node.annotation)
    #@+node:ekr.20191113063144.27: *6*  tog.arguments
    # arguments = (
    #       arg* posonlyargs, arg* args, arg? vararg, arg* kwonlyargs,
    #       expr* kw_defaults, arg? kwarg, expr* defaults
    # )

    sync_equal_flag = False  # A small hack.

    def do_arguments(self, node: Node) -> None:
        """Arguments to ast.Function or ast.Lambda, **not** ast.Call."""
        #
        # No need to generate commas anywhere below.
        #
        # Let block. Some fields may not exist pre Python 3.8.
        n_plain = len(node.args) - len(node.defaults)
        posonlyargs = getattr(node, 'posonlyargs', [])
        vararg = getattr(node, 'vararg', None)
        kwonlyargs = getattr(node, 'kwonlyargs', [])
        kw_defaults = getattr(node, 'kw_defaults', [])
        kwarg = getattr(node, 'kwarg', None)
        # 1. Sync the position-only args.
        if posonlyargs:
            for z in posonlyargs:
                self.visit(z)
            self.op('/')
        # 2. Sync all args.
        for i, z in enumerate(node.args):
            assert isinstance(z, ast.arg)
            self.visit(z)
            if i >= n_plain:
                old = self.equal_sign_spaces
                try:
                    self.equal_sign_spaces = getattr(z, 'annotation', None) is not None
                    self.op('=')
                finally:
                    self.equal_sign_spaces = old
                self.visit(node.defaults[i - n_plain])
        # 3. Sync the vararg.
        if vararg:
            self.op('*')
            self.visit(vararg)
        # 4. Sync the keyword-only args.
        if kwonlyargs:
            if not vararg:
                self.op('*')
            for n, z in enumerate(kwonlyargs):
                self.visit(z)
                val = kw_defaults[n]
                if val is not None:
                    self.op('=')
                    self.visit(val)
        # 5. Sync the kwarg.
        if kwarg:
            self.op('**')
            self.visit(kwarg)


    #@+node:ekr.20191113063144.15: *6* tog.AsyncFunctionDef
    # AsyncFunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list,
    #                expr? returns)

    def do_AsyncFunctionDef(self, node: Node) -> None:

        if node.decorator_list:
            for z in node.decorator_list:
                # '@%s\n'
                self.op('@')
                self.visit(z)
        # 'asynch def (%s): -> %s\n'
        # 'asynch def %s(%s):\n'
        async_token_type = 'async' if has_async_tokens else 'name'
        self.token(async_token_type, 'async')
        self.name('def')
        self.name(node.name)  # A string
        self.op('(')
        self.visit(node.args)
        self.op(')')
        returns = getattr(node, 'returns', None)
        if returns is not None:
            self.op('->')
            self.visit(node.returns)
        self.op(':')
        self.level += 1
        self.visit(node.body)
        self.level -= 1
    #@+node:ekr.20191113063144.16: *6* tog.ClassDef
    def do_ClassDef(self, node: Node) -> None:

        for z in node.decorator_list or []:
            #@verbatim
            # @{z}\n
            self.op('@')
            self.visit(z)
        # class name(bases):\n
        self.name('class')
        self.name(node.name)  # A string.
        if node.bases:
            self.op('(')
            self.visit(node.bases)
            self.op(')')
        self.op(':')
        # Body...
        self.level += 1
        self.visit(node.body)
        self.level -= 1
    #@+node:ekr.20191113063144.17: *6* tog.FunctionDef
    # FunctionDef(
    #   identifier name,
    #   arguments args,
    #   stmt* body,
    #   expr* decorator_list,
    #   expr? returns,
    #   string? type_comment)

    def do_FunctionDef(self, node: Node) -> None:

        # Guards...
        returns = getattr(node, 'returns', None)
        # Decorators...
            #@verbatim
            # @{z}\n
        for z in node.decorator_list or []:
            self.op('@')
            self.visit(z)
        # Signature...
            # def name(args): -> returns\n
            # def name(args):\n
        self.name('def')
        self.name(node.name)  # A string.
        self.op('(')
        self.visit(node.args)
        self.op(')')
        if returns is not None:
            self.op('->')
            self.visit(node.returns)
        self.op(':')
        # Body...
        self.level += 1
        self.visit(node.body)
        self.level -= 1
    #@+node:ekr.20191113063144.18: *6* tog.Interactive
    def do_Interactive(self, node: Node) -> None:  # pragma: no cover

        self.visit(node.body)
    #@+node:ekr.20191113063144.20: *6* tog.Lambda
    def do_Lambda(self, node: Node) -> None:

        self.name('lambda')
        self.visit(node.args)
        self.op(':')
        self.visit(node.body)
    #@+node:ekr.20191113063144.19: *6* tog.Module
    def do_Module(self, node: Node) -> None:

        # Encoding is a non-syncing statement.
        self.visit(node.body)
    #@+node:ekr.20191113063144.21: *5* tog: Expressions
    #@+node:ekr.20191113063144.22: *6* tog.Expr
    def do_Expr(self, node: Node) -> None:
        """An outer expression."""
        # No need to put parentheses.
        self.visit(node.value)
    #@+node:ekr.20191113063144.23: *6* tog.Expression
    def do_Expression(self, node: Node) -> None:  # pragma: no cover
        """An inner expression."""
        # No need to put parentheses.
        self.visit(node.body)
    #@+node:ekr.20191113063144.24: *6* tog.GeneratorExp
    def do_GeneratorExp(self, node: Node) -> None:

        # '<gen %s for %s>' % (elt, ','.join(gens))
        # No need to put parentheses or commas.
        self.visit(node.elt)
        self.visit(node.generators)
    #@+node:ekr.20210321171703.1: *6* tog.NamedExpr
    # NamedExpr(expr target, expr value)

    def do_NamedExpr(self, node: Node) -> None:  # Python 3.8+

        self.visit(node.target)
        self.op(':=')
        self.visit(node.value)
    #@+node:ekr.20191113063144.26: *5* tog: Operands
    #@+node:ekr.20191113063144.29: *6* tog.Attribute
    # Attribute(expr value, identifier attr, expr_context ctx)

    def do_Attribute(self, node: Node) -> None:

        self.visit(node.value)
        self.op('.')
        self.name(node.attr)  # A string.
    #@+node:ekr.20191113063144.30: *6* tog.Bytes
    def do_Bytes(self, node: Node) -> None:

        """
        It's invalid to mix bytes and non-bytes literals, so just
        advancing to the next 'string' token suffices.
        """
        token = self.find_next_significant_token()
        self.token('string', token.value)
    #@+node:ekr.20191113063144.33: *6* tog.comprehension
    # comprehension = (expr target, expr iter, expr* ifs, int is_async)

    def do_comprehension(self, node: Node) -> None:

        # No need to put parentheses.
        self.name('for')  # #1858.
        self.visit(node.target)  # A name
        self.name('in')
        self.visit(node.iter)
        for z in node.ifs or []:
            self.name('if')
            self.visit(z)
    #@+node:ekr.20191113063144.34: *6* tog.Constant
    def do_Constant(self, node: Node) -> None:  # pragma: no cover
        """
        https://greentreesnakes.readthedocs.io/en/latest/nodes.html

        A constant. The value attribute holds the Python object it represents.
        This can be simple types such as a number, string or None, but also
        immutable container types (tuples and frozensets) if all of their
        elements are constant.
        """
        # Support Python 3.8.
        if node.value is None or isinstance(node.value, bool):
            # Weird: return a name!
            self.token('name', repr(node.value))
        elif node.value == Ellipsis:
            self.op('...')
        elif isinstance(node.value, str):
            self.do_Str(node)
        elif isinstance(node.value, (int, float)):
            self.token('number', repr(node.value))
        elif isinstance(node.value, bytes):
            self.do_Bytes(node)
        elif isinstance(node.value, tuple):
            self.do_Tuple(node)
        elif isinstance(node.value, frozenset):
            self.do_Set(node)
        else:
            # Unknown type.
            g.trace('----- Oops -----', repr(node.value), g.callers())
    #@+node:ekr.20191113063144.35: *6* tog.Dict
    # Dict(expr* keys, expr* values)

    def do_Dict(self, node: Node) -> None:

        assert len(node.keys) == len(node.values)
        self.op('{')
        # No need to put commas.
        for i, key in enumerate(node.keys):
            key, value = node.keys[i], node.values[i]
            self.visit(key)  # a Str node.
            self.op(':')
            if value is not None:
                self.visit(value)
        self.op('}')
    #@+node:ekr.20191113063144.36: *6* tog.DictComp
    # DictComp(expr key, expr value, comprehension* generators)

    # d2 = {val: key for key, val in d}

    def do_DictComp(self, node: Node) -> None:

        self.token('op', '{')
        self.visit(node.key)
        self.op(':')
        self.visit(node.value)
        for z in node.generators or []:
            self.visit(z)
            self.token('op', '}')
    #@+node:ekr.20191113063144.37: *6* tog.Ellipsis
    def do_Ellipsis(self, node: Node) -> None:  # pragma: no cover (Does not exist for python 3.8+)

        self.op('...')
    #@+node:ekr.20191113063144.38: *6* tog.ExtSlice
    # https://docs.python.org/3/reference/expressions.html#slicings

    # ExtSlice(slice* dims)

    def do_ExtSlice(self, node: Node) -> None:  # pragma: no cover (deprecated)

        # ','.join(node.dims)
        for i, z in enumerate(node.dims):
            self.visit(z)
            if i < len(node.dims) - 1:
                self.op(',')
    #@+node:ekr.20191113063144.40: *6* tog.Index
    def do_Index(self, node: Node) -> None:  # pragma: no cover (deprecated)

        self.visit(node.value)
    #@+node:ekr.20191113063144.39: *6* tog.FormattedValue: not called!
    # FormattedValue(expr value, int? conversion, expr? format_spec)

    def do_FormattedValue(self, node: Node) -> None:  # pragma: no cover
        """
        This node represents the *components* of a *single* f-string.

        Happily, JoinedStr nodes *also* represent *all* f-strings,
        so the TOG should *never visit this node!
        """
        filename = getattr(self, 'filename', '<no file>')
        raise AssignLinksError(
            f"file: {filename}\n"
            f"do_FormattedValue should never be called")

        # This code has no chance of being useful...

            # conv = node.conversion
            # spec = node.format_spec
            # self.visit(node.value)
            # if conv is not None:
                # self.token('number', conv)
            # if spec is not None:
                # self.visit(node.format_spec)
    #@+node:ekr.20191113063144.41: *6* tog.JoinedStr & helpers
    # JoinedStr(expr* values)

    def do_JoinedStr(self, node: Node) -> None:
        """
        JoinedStr nodes represent at least one f-string and all other strings
        concatenated to it.

        Analyzing JoinedStr.values would be extremely tricky, for reasons that
        need not be explained here.

        Instead, we get the tokens *from the token list itself*!
        """
        for z in self.get_concatenated_string_tokens():
            self.token(z.kind, z.value)
    #@+node:ekr.20191113063144.42: *6* tog.List
    def do_List(self, node: Node) -> None:

        # No need to put commas.
        self.op('[')
        self.visit(node.elts)
        self.op(']')
    #@+node:ekr.20191113063144.43: *6* tog.ListComp
    # ListComp(expr elt, comprehension* generators)

    def do_ListComp(self, node: Node) -> None:

        self.op('[')
        self.visit(node.elt)
        for z in node.generators:
            self.visit(z)
        self.op(']')
    #@+node:ekr.20191113063144.44: *6* tog.Name & NameConstant
    def do_Name(self, node: Node) -> None:

        self.name(node.id)

    def do_NameConstant(self, node: Node) -> None:  # pragma: no cover (Does not exist in Python 3.8+)

        self.name(repr(node.value))

    #@+node:ekr.20191113063144.45: *6* tog.Num
    def do_Num(self, node: Node) -> None:  # pragma: no cover (Does not exist in Python 3.8+)

        self.token('number', node.n)
    #@+node:ekr.20191113063144.47: *6* tog.Set
    # Set(expr* elts)

    def do_Set(self, node: Node) -> None:

        self.op('{')
        self.visit(node.elts)
        self.op('}')
    #@+node:ekr.20191113063144.48: *6* tog.SetComp
    # SetComp(expr elt, comprehension* generators)

    def do_SetComp(self, node: Node) -> None:

        self.op('{')
        self.visit(node.elt)
        for z in node.generators or []:
            self.visit(z)
        self.op('}')
    #@+node:ekr.20191113063144.49: *6* tog.Slice
    # slice = Slice(expr? lower, expr? upper, expr? step)

    def do_Slice(self, node: Node) -> None:

        lower = getattr(node, 'lower', None)
        upper = getattr(node, 'upper', None)
        step = getattr(node, 'step', None)
        if lower is not None:
            self.visit(lower)
        # Always put the colon between upper and lower.
        self.op(':')
        if upper is not None:
            self.visit(upper)
        # Put the second colon if it exists in the token list.
        if step is None:
            token = self.find_next_significant_token()
            if token and token.value == ':':
                self.op(':')
        else:
            self.op(':')
            self.visit(step)
    #@+node:ekr.20191113063144.50: *6* tog.Str & helper
    def do_Str(self, node: Node) -> None:
        """This node represents a string constant."""
        # This loop is necessary to handle string concatenation.
        for z in self.get_concatenated_string_tokens():
            self.token(z.kind, z.value)
    #@+node:ekr.20200111083914.1: *7* tog.get_concatenated_tokens
    def get_concatenated_string_tokens(self) -> list[Token]:
        """
        Return the next 'string' token and all 'string' tokens concatenated to
        it. *Never* update self.px here.
        """
        trace = False
        tag = 'tog.get_concatenated_string_tokens'
        i = self.px
        # First, find the next significant token.  It should be a string.
        i, token = i + 1, None
        while i < len(self.tokens):
            token = self.tokens[i]
            i += 1
            if token.kind == 'string':
                # Rescan the string.
                i -= 1
                break
            # An error.
            if is_significant_token(token):  # pragma: no cover
                break
        # Raise an error if we didn't find the expected 'string' token.
        if not token or token.kind != 'string':  # pragma: no cover
            if not token:
                token = self.tokens[-1]
            filename = getattr(self, 'filename', '<no filename>')
            raise AssignLinksError(
                f"\n"
                f"{tag}...\n"
                f"file: {filename}\n"
                f"line: {token.line_number}\n"
                f"   i: {i}\n"
                f"expected 'string' token, got {token!s}")
        # Accumulate string tokens.
        assert self.tokens[i].kind == 'string'
        results = []
        while i < len(self.tokens):
            token = self.tokens[i]
            i += 1
            if token.kind == 'string':
                results.append(token)
            elif token.kind == 'op' or is_significant_token(token):
                # Any significant token *or* any op will halt string concatenation.
                break
            # 'ws', 'nl', 'newline', 'comment', 'indent', 'dedent', etc.
        # The (significant) 'endmarker' token ensures we will have result.
        assert results
        if trace:  # pragma: no cover
            g.print_obj(results, tag=f"{tag}: Results")
        return results
    #@+node:ekr.20191113063144.51: *6* tog.Subscript
    # Subscript(expr value, slice slice, expr_context ctx)

    def do_Subscript(self, node: Node) -> None:

        self.visit(node.value)
        self.op('[')
        self.visit(node.slice)
        self.op(']')
    #@+node:ekr.20191113063144.52: *6* tog.Tuple
    # Tuple(expr* elts, expr_context ctx)

    def do_Tuple(self, node: Node) -> None:

        # Do not call op for parens or commas here.
        # They do not necessarily exist in the token list!
        self.visit(node.elts)
    #@+node:ekr.20191113063144.53: *5* tog: Operators
    #@+node:ekr.20191113063144.55: *6* tog.BinOp
    def do_BinOp(self, node: Node) -> None:

        op_name_ = op_name(node.op)
        self.visit(node.left)
        self.op(op_name_)
        self.visit(node.right)
    #@+node:ekr.20191113063144.56: *6* tog.BoolOp
    # BoolOp(boolop op, expr* values)

    def do_BoolOp(self, node: Node) -> None:

        # op.join(node.values)
        op_name_ = op_name(node.op)
        for i, z in enumerate(node.values):
            self.visit(z)
            if i < len(node.values) - 1:
                self.name(op_name_)
    #@+node:ekr.20191113063144.57: *6* tog.Compare
    # Compare(expr left, cmpop* ops, expr* comparators)

    def do_Compare(self, node: Node) -> None:

        assert len(node.ops) == len(node.comparators)
        self.visit(node.left)
        for i, z in enumerate(node.ops):
            op_name_ = op_name(node.ops[i])
            if op_name_ in ('not in', 'is not'):
                for z in op_name_.split(' '):
                    self.name(z)
            elif op_name_.isalpha():
                self.name(op_name_)
            else:
                self.op(op_name_)
            self.visit(node.comparators[i])
    #@+node:ekr.20191113063144.58: *6* tog.UnaryOp
    def do_UnaryOp(self, node: Node) -> None:

        op_name_ = op_name(node.op)
        if op_name_.isalpha():
            self.name(op_name_)
        else:
            self.op(op_name_)
        self.visit(node.operand)
    #@+node:ekr.20191113063144.59: *6* tog.IfExp (ternary operator)
    # IfExp(expr test, expr body, expr orelse)

    def do_IfExp(self, node: Node) -> None:

        self.visit(node.body)
        self.name('if')
        self.visit(node.test)
        self.name('else')
        self.visit(node.orelse)
    #@+node:ekr.20191113063144.60: *5* tog: Statements
    #@+node:ekr.20191113063144.83: *6*  tog.Starred
    # Starred(expr value, expr_context ctx)

    def do_Starred(self, node: Node) -> None:
        """A starred argument to an ast.Call"""
        self.op('*')
        self.visit(node.value)
    #@+node:ekr.20191113063144.61: *6* tog.AnnAssign
    # AnnAssign(expr target, expr annotation, expr? value, int simple)

    def do_AnnAssign(self, node: Node) -> None:

        # {node.target}:{node.annotation}={node.value}\n'
        self.visit(node.target)
        self.op(':')
        self.visit(node.annotation)
        if node.value is not None:  # #1851
            self.op('=')
            self.visit(node.value)
    #@+node:ekr.20191113063144.62: *6* tog.Assert
    # Assert(expr test, expr? msg)

    def do_Assert(self, node: Node) -> None:

        # Guards...
        msg = getattr(node, 'msg', None)
        # No need to put parentheses or commas.
        self.name('assert')
        self.visit(node.test)
        if msg is not None:
            self.visit(node.msg)
    #@+node:ekr.20191113063144.63: *6* tog.Assign
    def do_Assign(self, node: Node) -> None:

        for z in node.targets:
            self.visit(z)
            self.op('=')
        self.visit(node.value)
    #@+node:ekr.20191113063144.64: *6* tog.AsyncFor
    def do_AsyncFor(self, node: Node) -> None:

        # The def line...
        # Py 3.8 changes the kind of token.
        async_token_type = 'async' if has_async_tokens else 'name'
        self.token(async_token_type, 'async')
        self.name('for')
        self.visit(node.target)
        self.name('in')
        self.visit(node.iter)
        self.op(':')
        # Body...
        self.level += 1
        self.visit(node.body)
        # Else clause...
        if node.orelse:
            self.name('else')
            self.op(':')
            self.visit(node.orelse)
        self.level -= 1
    #@+node:ekr.20191113063144.65: *6* tog.AsyncWith
    def do_AsyncWith(self, node: Node) -> None:

        async_token_type = 'async' if has_async_tokens else 'name'
        self.token(async_token_type, 'async')
        self.do_With(node)
    #@+node:ekr.20191113063144.66: *6* tog.AugAssign
    # AugAssign(expr target, operator op, expr value)

    def do_AugAssign(self, node: Node) -> None:

        # %s%s=%s\n'
        op_name_ = op_name(node.op)
        self.visit(node.target)
        self.op(op_name_ + '=')
        self.visit(node.value)
    #@+node:ekr.20191113063144.67: *6* tog.Await
    # Await(expr value)

    def do_Await(self, node: Node) -> None:

        async_token_type = 'await' if has_async_tokens else 'name'
        self.token(async_token_type, 'await')
        self.visit(node.value)
    #@+node:ekr.20191113063144.68: *6* tog.Break
    def do_Break(self, node: Node) -> None:

        self.name('break')
    #@+node:ekr.20191113063144.31: *6* tog.Call & helpers
    # Call(expr func, expr* args, keyword* keywords)

    # Python 3 ast.Call nodes do not have 'starargs' or 'kwargs' fields.

    def do_Call(self, node: Node) -> None:

        # The calls to op(')') and op('(') do nothing by default.
        # Subclasses might handle them in an overridden tog.set_links.
        self.visit(node.func)
        self.op('(')
        # No need to generate any commas.
        self.handle_call_arguments(node)
        self.op(')')
    #@+node:ekr.20191204114930.1: *7* tog.arg_helper
    def arg_helper(self, node: Union[Node, str]) -> None:
        """
        Yield the node, with a special case for strings.
        """
        if isinstance(node, str):
            self.token('name', node)
        else:
            self.visit(node)
    #@+node:ekr.20191204105506.1: *7* tog.handle_call_arguments
    def handle_call_arguments(self, node: Node) -> None:
        """
        Generate arguments in the correct order.

        Call(expr func, expr* args, keyword* keywords)

        https://docs.python.org/3/reference/expressions.html#calls

        Warning: This code will fail on Python 3.8 only for calls
                 containing kwargs in unexpected places.
        """
        # *args:    in node.args[]:     Starred(value=Name(id='args'))
        # *[a, 3]:  in node.args[]:     Starred(value=List(elts=[Name(id='a'), Num(n=3)])
        # **kwargs: in node.keywords[]: keyword(arg=None, value=Name(id='kwargs'))
        #
        # Scan args for *name or *List
        args = node.args or []
        keywords = node.keywords or []

        def get_pos(obj: Node) -> tuple[int, int, Any]:
            line1 = getattr(obj, 'lineno', None)
            col1 = getattr(obj, 'col_offset', None)
            return line1, col1, obj

        def sort_key(aTuple: tuple) -> int:
            line, col, obj = aTuple
            return line * 1000 + col

        if 0:  # pragma: no cover
            g.print_obj([ast.dump(z) for z in args], tag='args')
            g.print_obj([ast.dump(z) for z in keywords], tag='keywords')

        if py_version >= (3, 9):
            places = [get_pos(z) for z in args + keywords]
            places.sort(key=sort_key)
            ordered_args = [z[2] for z in places]
            for z in ordered_args:
                if isinstance(z, ast.Starred):
                    self.op('*')
                    self.visit(z.value)
                elif isinstance(z, ast.keyword):
                    if getattr(z, 'arg', None) is None:
                        self.op('**')
                        self.arg_helper(z.value)
                    else:
                        self.arg_helper(z.arg)
                        old = self.equal_sign_spaces
                        try:
                            self.equal_sign_spaces = False
                            self.op('=')
                        finally:
                            self.equal_sign_spaces = old
                        self.arg_helper(z.value)
                else:
                    self.arg_helper(z)
        else:  # pragma: no cover
            #
            # Legacy code: May fail for Python 3.8
            #
            # Scan args for *arg and *[...]
            kwarg_arg = star_arg = None
            for z in args:
                if isinstance(z, ast.Starred):
                    if isinstance(z.value, ast.Name):  # *Name.
                        star_arg = z
                        args.remove(z)
                        break
                    elif isinstance(z.value, (ast.List, ast.Tuple)):  # *[...]
                        # star_list = z
                        break
                    raise AttributeError(f"Invalid * expression: {ast.dump(z)}")  # pragma: no cover
            # Scan keywords for **name.
            for z in keywords:
                if hasattr(z, 'arg') and z.arg is None:
                    kwarg_arg = z
                    keywords.remove(z)
                    break
            # Sync the plain arguments.
            for z in args:
                self.arg_helper(z)
            # Sync the keyword args.
            for z in keywords:
                self.arg_helper(z.arg)
                self.op('=')
                self.arg_helper(z.value)
            # Sync the * arg.
            if star_arg:
                self.arg_helper(star_arg)
            # Sync the ** kwarg.
            if kwarg_arg:
                self.op('**')
                self.visit(kwarg_arg.value)
    #@+node:ekr.20191113063144.69: *6* tog.Continue
    def do_Continue(self, node: Node) -> None:

        self.name('continue')
    #@+node:ekr.20191113063144.70: *6* tog.Delete
    def do_Delete(self, node: Node) -> None:

        # No need to put commas.
        self.name('del')
        self.visit(node.targets)
    #@+node:ekr.20191113063144.71: *6* tog.ExceptHandler
    def do_ExceptHandler(self, node: Node) -> None:

        # Except line...
        self.name('except')
        if self.try_stack[-1] == '*':
            self.op('*')
        if getattr(node, 'type', None):
            self.visit(node.type)
        if getattr(node, 'name', None):
            self.name('as')
            self.name(node.name)
        self.op(':')
        # Body...
        self.level += 1
        self.visit(node.body)
        self.level -= 1
    #@+node:ekr.20191113063144.73: *6* tog.For
    def do_For(self, node: Node) -> None:

        # The def line...
        self.name('for')
        self.visit(node.target)
        self.name('in')
        self.visit(node.iter)
        self.op(':')
        # Body...
        self.level += 1
        self.visit(node.body)
        # Else clause...
        if node.orelse:
            self.name('else')
            self.op(':')
            self.visit(node.orelse)
        self.level -= 1
    #@+node:ekr.20191113063144.74: *6* tog.Global
    # Global(identifier* names)

    def do_Global(self, node: Node) -> None:

        self.name('global')
        for z in node.names:
            self.name(z)
    #@+node:ekr.20191113063144.75: *6* tog.If & helpers
    # If(expr test, stmt* body, stmt* orelse)

    def do_If(self, node: Node) -> None:
        #@+<< do_If docstring >>
        #@+node:ekr.20191122222412.1: *7* << do_If docstring >>
        """
        The parse trees for the following are identical!

          if 1:            if 1:
              pass             pass
          else:            elif 2:
              if 2:            pass
                  pass

        So there is *no* way for the 'if' visitor to disambiguate the above two
        cases from the parse tree alone.

        Instead, we scan the tokens list for the next 'if', 'else' or 'elif' token.
        """
        #@-<< do_If docstring >>
        # Use the next significant token to distinguish between 'if' and 'elif'.
        token = self.find_next_significant_token()
        self.name(token.value)
        self.visit(node.test)
        self.op(':')
        #
        # Body...
        self.level += 1
        self.visit(node.body)
        self.level -= 1
        #
        # Else and elif clauses...
        if node.orelse:
            self.level += 1
            token = self.find_next_significant_token()
            if token.value == 'else':
                self.name('else')
                self.op(':')
                self.visit(node.orelse)
            else:
                self.visit(node.orelse)
            self.level -= 1
    #@+node:ekr.20191113063144.76: *6* tog.Import & helper
    def do_Import(self, node: Node) -> None:

        self.name('import')
        for alias in node.names:
            self.name(alias.name)
            if alias.asname:
                self.name('as')
                self.name(alias.asname)
    #@+node:ekr.20191113063144.77: *6* tog.ImportFrom
    # ImportFrom(identifier? module, alias* names, int? level)

    def do_ImportFrom(self, node: Node) -> None:

        self.name('from')
        for _i in range(node.level):
            self.op('.')
        if node.module:
            self.name(node.module)
        self.name('import')
        # No need to put commas.
        for alias in node.names:
            if alias.name == '*':  # #1851.
                self.op('*')
            else:
                self.name(alias.name)
            if alias.asname:
                self.name('as')
                self.name(alias.asname)
    #@+node:ekr.20220401034726.1: *6* tog.Match* (Python 3.10+)
    # Match(expr subject, match_case* cases)

    # match_case = (pattern pattern, expr? guard, stmt* body)

    # Full syntax diagram: # https://peps.python.org/pep-0634/#appendix-a

    def do_Match(self, node: Node) -> None:

        cases = getattr(node, 'cases', [])
        self.name('match')
        self.visit(node.subject)
        self.op(':')
        for case in cases:
            self.visit(case)
    #@+node:ekr.20220401034726.2: *7* tog.match_case
    #  match_case = (pattern pattern, expr? guard, stmt* body)

    def do_match_case(self, node: Node) -> None:

        guard = getattr(node, 'guard', None)
        body = getattr(node, 'body', [])
        self.name('case')
        self.visit(node.pattern)
        if guard:
            self.name('if')
            self.visit(guard)
        self.op(':')
        for statement in body:
            self.visit(statement)
    #@+node:ekr.20220401034726.3: *7* tog.MatchAs
    # MatchAs(pattern? pattern, identifier? name)

    def do_MatchAs(self, node: Node) -> None:
        pattern = getattr(node, 'pattern', None)
        name = getattr(node, 'name', None)
        if pattern and name:
            self.visit(pattern)
            self.name('as')
            self.name(name)
        elif pattern:
            self.visit(pattern)  # pragma: no cover
        else:
            self.name(name or '_')
    #@+node:ekr.20220401034726.4: *7* tog.MatchClass
    # MatchClass(expr cls, pattern* patterns, identifier* kwd_attrs, pattern* kwd_patterns)

    def do_MatchClass(self, node: Node) -> None:

        patterns = getattr(node, 'patterns', [])
        kwd_attrs = getattr(node, 'kwd_attrs', [])
        kwd_patterns = getattr(node, 'kwd_patterns', [])
        self.visit(node.cls)
        self.op('(')
        for pattern in patterns:
            self.visit(pattern)
        for i, kwd_attr in enumerate(kwd_attrs):
            self.name(kwd_attr)  # a String.
            self.op('=')
            self.visit(kwd_patterns[i])
        self.op(')')
    #@+node:ekr.20220401034726.5: *7* tog.MatchMapping
    # MatchMapping(expr* keys, pattern* patterns, identifier? rest)

    def do_MatchMapping(self, node: Node) -> None:
        keys = getattr(node, 'keys', [])
        patterns = getattr(node, 'patterns', [])
        rest = getattr(node, 'rest', None)
        self.op('{')
        for i, key in enumerate(keys):
            self.visit(key)
            self.op(':')
            self.visit(patterns[i])
        if rest:
            self.op('**')
            self.name(rest)  # A string.
        self.op('}')
    #@+node:ekr.20220401034726.6: *7* tog.MatchOr
    # MatchOr(pattern* patterns)

    def do_MatchOr(self, node: Node) -> None:
        patterns = getattr(node, 'patterns', [])
        for i, pattern in enumerate(patterns):
            if i > 0:
                self.op('|')
            self.visit(pattern)
    #@+node:ekr.20220401034726.7: *7* tog.MatchSequence
    # MatchSequence(pattern* patterns)

    def do_MatchSequence(self, node: Node) -> None:
        patterns = getattr(node, 'patterns', [])
        # Scan for the next '(' or '[' token, skipping the 'case' token.
        token = None
        for token in self.tokens[self.px + 1 :]:
            if token.kind == 'op' and token.value in '([':
                break
            if is_significant_token(token):
                # An implicit tuple: there is no '(' or '[' token.
                token = None
                break
        else:
            raise AssignLinksError('Ill-formed tuple')  # pragma: no cover
        if token:
            self.op(token.value)
        for pattern in patterns:
            self.visit(pattern)
        if token:
            self.op(']' if token.value == '[' else ')')
    #@+node:ekr.20220401034726.8: *7* tog.MatchSingleton
    # MatchSingleton(constant value)

    def do_MatchSingleton(self, node: Node) -> None:
        """Match True, False or None."""
        # g.trace(repr(node.value))
        self.token('name', repr(node.value))
    #@+node:ekr.20220401034726.9: *7* tog.MatchStar
    # MatchStar(identifier? name)

    def do_MatchStar(self, node: Node) -> None:
        name = getattr(node, 'name', None)
        self.op('*')
        if name:
            self.name(name)
    #@+node:ekr.20220401034726.10: *7* tog.MatchValue
    # MatchValue(expr value)

    def do_MatchValue(self, node: Node) -> None:

        self.visit(node.value)
    #@+node:ekr.20191113063144.78: *6* tog.Nonlocal
    # Nonlocal(identifier* names)

    def do_Nonlocal(self, node: Node) -> None:

        # nonlocal %s\n' % ','.join(node.names))
        # No need to put commas.
        self.name('nonlocal')
        for z in node.names:
            self.name(z)
    #@+node:ekr.20191113063144.79: *6* tog.Pass
    def do_Pass(self, node: Node) -> None:

        self.name('pass')
    #@+node:ekr.20191113063144.81: *6* tog.Raise
    # Raise(expr? exc, expr? cause)

    def do_Raise(self, node: Node) -> None:

        # No need to put commas.
        self.name('raise')
        exc = getattr(node, 'exc', None)
        cause = getattr(node, 'cause', None)
        tback = getattr(node, 'tback', None)
        self.visit(exc)
        if cause:
            self.name('from')  # #2446.
            self.visit(cause)
        self.visit(tback)
    #@+node:ekr.20191113063144.82: *6* tog.Return
    def do_Return(self, node: Node) -> None:

        self.name('return')
        self.visit(node.value)
    #@+node:ekr.20191113063144.85: *6* tog.Try
    # Try(stmt* body, excepthandler* handlers, stmt* orelse, stmt* finalbody)

    def do_Try(self, node: Node) -> None:

        # Try line...
        self.name('try')
        self.op(':')
        # Body...
        self.level += 1
        self.visit(node.body)
        self.try_stack.append('')
        self.visit(node.handlers)
        self.try_stack.pop()
        # Else...
        if node.orelse:
            self.name('else')
            self.op(':')
            self.visit(node.orelse)
        # Finally...
        if node.finalbody:
            self.name('finally')
            self.op(':')
            self.visit(node.finalbody)
        self.level -= 1
    #@+node:ekr.20230615211005.1: *6* tog.TryStar
    # TryStar(stmt* body, excepthandler* handlers, stmt* orelse, stmt* finalbody)

    # Examples:
    #   except* SpamError:
    #   except* FooError as e:
    #   except* (BarError, BazError) as e:

    def do_TryStar(self, node: Node) -> None:

        # Try line...
        self.name('try')
        self.op(':')
        # Body...
        self.level += 1
        self.visit(node.body)
        self.try_stack.append('*')
        self.visit(node.handlers)
        self.try_stack.pop()
        # Else...
        if node.orelse:
            self.name('else')
            self.op(':')
            self.visit(node.orelse)
        # Finally...
        if node.finalbody:
            self.name('finally')
            self.op(':')
            self.visit(node.finalbody)
        self.level -= 1
    #@+node:ekr.20191113063144.88: *6* tog.While
    def do_While(self, node: Node) -> None:

        # While line...
            # while %s:\n'
        self.name('while')
        self.visit(node.test)
        self.op(':')
        # Body...
        self.level += 1
        self.visit(node.body)
        # Else clause...
        if node.orelse:
            self.name('else')
            self.op(':')
            self.visit(node.orelse)
        self.level -= 1
    #@+node:ekr.20191113063144.89: *6* tog.With
    # With(withitem* items, stmt* body)

    # withitem = (expr context_expr, expr? optional_vars)

    def do_With(self, node: Node) -> None:

        expr: Optional[ast.AST] = getattr(node, 'context_expression', None)
        items: list[ast.AST] = getattr(node, 'items', [])
        self.name('with')
        self.visit(expr)
        # No need to put commas.
        for item in items:
            self.visit(item.context_expr)
            optional_vars = getattr(item, 'optional_vars', None)
            if optional_vars is not None:
                self.name('as')
                self.visit(item.optional_vars)
        # End the line.
        self.op(':')
        # Body...
        self.level += 1
        self.visit(node.body)
        self.level -= 1
    #@+node:ekr.20191113063144.90: *6* tog.Yield
    def do_Yield(self, node: Node) -> None:

        self.name('yield')
        if hasattr(node, 'value'):
            self.visit(node.value)
    #@+node:ekr.20191113063144.91: *6* tog.YieldFrom
    # YieldFrom(expr value)

    def do_YieldFrom(self, node: Node) -> None:

        self.name('yield')
        self.name('from')
        self.visit(node.value)
    #@-others
#@+node:ekr.20200702102239.1: ** function: main (leoAst.py)
def main() -> None:  # pragma: no cover
    """Run commands specified by sys.argv."""
    args, settings_dict, arg_files, recursive = scan_ast_args()
    # Finalize arguments.
    cwd, files = os.getcwd(), []
    for path in arg_files:
        root_dir = os.path.join(cwd, path)
        files = glob.glob(f'{root_dir}**{os.sep}*.py', recursive=recursive)
    if not files:
        print('No files found')
        return
    # Execute the command.
    # print(f"Found {len(files)} file{g.plural(len(files))}.")
    if args.f:
        fstringify_command(files)
    if args.fd:
        fstringify_diff_command(files)
    if args.o:
        orange_command(files, settings_dict)
    if args.od:
        orange_diff_command(files, settings_dict)
#@-others
g = LeoGlobals()
if __name__ == '__main__':
    main()  # pragma: no cover
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
