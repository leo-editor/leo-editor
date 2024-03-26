#@+leo-ver=5-thin
#@+node:ekr.20141012064706.18389: * @file leoAst.py
# This file is part of Leo: https://leo-editor.github.io/leo-editor
# Leo's copyright notice is based on the MIT license:
# https://leo-editor.github.io/leo-editor/license.html

# Don't pollute cff searches with matches from this file!
#@@nosearch

#@+<< leoAst docstring >>
#@+node:ekr.20200113081838.1: ** << leoAst docstring >>
"""
leoAst.py: Classes that unify Python's token and ast worlds.

The classes in this file create two-way links between tokens in the token
list and ast nodes in the parse tree.

Use this code at your own risk! It is no longer under active development.


**Classes**


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


**Note re Python 3.8**

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

Memory: The TOG class makes no significant demands on python's resources.
TOG.node_stack is the only variable-length data. This stack resides in
python's heap, so its length is unimportant. In the worst case, it might
contain a few thousand entries. The TOT class uses no variable-length data.

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
import ast
import difflib
import io
import re
import sys
import tokenize
from typing import Any, Generator, Optional, Union

try:
    from leo.core import leoGlobals as g
except Exception:
    # check_g function gives the message.
    g = None

Node = ast.AST
Settings = Optional[dict[str, Any]]
#@-<< leoAst imports & annotations >>

v1, v2, junk1, junk2, junk3 = sys.version_info
if (v1, v2) < (3, 9):  # pragma: no cover
    raise ImportError('The commands in leoAst.py require Python 3.9 or above')

#@+others
#@+node:ekr.20160521104628.1: **  leoAst.py: top-level utils
if 1:  # pragma: no cover
    #@+others
    #@+node:ekr.20231212071217.1: *3* function: check_g
    def check_g() -> bool:
        """print an error message if g is None"""
        if not g:
            print('This statement failed: `from leo.core import leoGlobals as g`')
            print('Please adjust your Python path accordingly')
        return bool(g)
    #@+node:ekr.20200218071822.1: *3* function: regularize_nls
    def regularize_nls(s: str) -> str:
        """Regularize newlines within s."""
        return s.replace('\r\n', '\n').replace('\r', '\n')
    #@+node:ekr.20200103163100.1: *3* function: write_file
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
    #@+node:ekr.20191231110051.1: *3* functions: dumpers...
    #@+node:ekr.20191027074436.1: *4* function: dump_ast
    def dump_ast(ast: Node, tag: str = 'dump_ast') -> None:
        """Utility to dump an ast tree."""
        g.printObj(AstDumper().dump_ast(ast), tag=tag)
    #@+node:ekr.20191228095945.4: *4* function: dump_contents
    def dump_contents(contents: str, tag: str = 'Contents') -> None:
        print('')
        print(f"{tag}...\n")
        for i, z in enumerate(g.splitLines(contents)):
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
        print("Note: values shown are repr(value) *except* for 'string' and 'fstring*' tokens.")
        tokens[0].dump_header()
        for z in tokens:
            print(z.dump())
        print('')
    #@+node:ekr.20191228095945.9: *4* function: dump_tree
    def dump_tree(tokens: list[Token], tree: Node, tag: str = 'Tree') -> None:
        print('')
        print(f"{tag}...\n")
        print(AstDumper().dump_tree(tokens, tree))
    #@+node:ekr.20240116115210.1: *4* function: show_diffs
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
                g.printObj(global_tokens_list[i : j + 1], tag=tag)
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
            kind in ('async', 'await', 'endmarker', 'name', 'number', 'string')
            or kind.startswith('fstring')
            or kind == 'op' and value not in ',;()')

    def is_significant_kind(kind: str) -> bool:
        return (
            kind in ('async', 'await', 'endmarker', 'name', 'number', 'string')
            or kind.startswith('fstring')
        )

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
                'In match_parens\n'
                f"Unmatched parens: level={level}\n"
                f"            file: {filename}\n"
                f"            line: {line_n}\n"
            )
        return j
    #@+node:ekr.20240104095925.1: *4* function: output_tokens_to_string
    def output_tokens_to_string(tokens: list[OutputToken]) -> str:
        """Return the string represented by the list of tokens."""
        if tokens is None:
            # This indicates an internal error.
            print('')
            g.trace('===== output token list is None ===== ')
            print('')
            return ''
        return ''.join([z.to_string() for z in tokens])
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
    #@+node:ekr.20240104112534.1: *4* function: tokens_to_string
    def tokens_to_string(tokens: list[Token]) -> str:
        """Return the string represented by the list of tokens."""
        if tokens is None:
            # This indicates an internal error.
            print('')
            g.trace('===== No tokens ===== ')
            print('')
            return ''
        return ''.join([z.to_string() for z in tokens])
    #@+node:ekr.20200101030236.1: *4* function: input_tokens_to_string
    def input_tokens_to_string(tokens: list[InputToken]) -> str:
        """Return the string represented by the list of tokens."""
        if tokens is None:
            # This indicates an internal error.
            print('')
            g.trace('===== input token list is None ===== ')
            print('')
            return ''
        return ''.join([z.to_string() for z in tokens])
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
    #@+node:ekr.20240104125422.1: *3* node/token creators...
    #@+node:ekr.20200103082049.1: *4* function: make_tokens
    def make_tokens(contents: str) -> list[InputToken]:
        """
        Return a list (not a generator) of Token objects corresponding to the
        list of 5-tuples generated by tokenize.tokenize.

        Perform consistency checks and handle all exceptions.

        Called from unit tests.
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
#@+node:ekr.20141012064706.18390: ** class AstDumper
class AstDumper:  # pragma: no cover
    """A class supporting various kinds of dumps of ast nodes."""
    #@+others
    #@+node:ekr.20191112033445.1: *3* dumper.dump_tree & helper
    def dump_tree(self, tokens: list[Token], tree: Node) -> str:
        """Briefly show a tree, properly indented."""
        self.tokens = tokens
        result = [self.show_header()]
        self.dump_tree_and_links_helper(tree, 0, result)
        return ''.join(result)
    #@+node:ekr.20191125035321.1: *4* dumper.dump_tree_and_links_helper
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
    #@+node:ekr.20191125035600.1: *3* dumper.compute_node_string & helpers
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
    #@+node:ekr.20191113223424.1: *4* dumper.show_fields
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
                if g.python_version_tuple < (3, 12, 0):
                    assert isinstance(z, (ast.FormattedValue, ast.Str))
                    if isinstance(z, ast.Str):
                        results.append(z.s)
                        strings += 1
                    else:
                        results.append(z.__class__.__name__)
                        fstrings += 1
                else:
                    assert isinstance(z, (ast.FormattedValue, ast.Constant))
                    if isinstance(z, ast.Constant):
                        results.append(z.value)
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
    #@+node:ekr.20191114054726.1: *4* dumper.show_line_range
    def show_line_range(self, node: Node) -> str:

        token_list = get_node_token_list(node, self.tokens)
        if not token_list:
            return ''
        min_ = min([z.line_number for z in token_list])
        max_ = max([z.line_number for z in token_list])
        return f"{min_}" if min_ == max_ else f"{min_}..{max_}"
    #@+node:ekr.20191113223425.1: *4* dumper.show_tokens
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
    #@+node:ekr.20191110165235.5: *3* dumper.show_header
    def show_header(self) -> str:
        """Return a header string, but only the fist time."""
        return (
            f"{'parent':<16} {'lines':<10} {'node':<34} {'tokens'}\n"
            f"{'======':<16} {'=====':<10} {'====':<34} {'======'}\n")
    #@+node:ekr.20141012064706.18392: *3* dumper.dump_ast & helper
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
    #@+node:ekr.20141012064706.18393: *4* dumper.get_fields
    def get_fields(self, node: Node) -> Generator:

        return (
            (a, b) for a, b in ast.iter_fields(node)
                if a not in ['ctx',] and b not in (None, [])
        )
    #@-others
#@+node:ekr.20191222083453.1: ** class Fstringify
class Fstringify:
    """A class to fstringify files."""

    silent = True  # for pytest. Defined in all entries.
    line_number = 0
    line = ''

    #@+others
    #@+node:ekr.20191222083947.1: *3* fs.fstringify
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
        string_node = ast.Str if g.python_version_tuple < (3, 12, 0) else ast.Constant
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.BinOp)
                and op_name(node.op) == '%'
                and isinstance(node.left, string_node)
            ):
                self.make_fstring(node)
        results = tokens_to_string(self.tokens)
        return results
    #@+node:ekr.20191222095754.1: *3* fs.make_fstring & helpers
    def make_fstring(self, node: Node) -> None:
        """
        node is BinOp node representing an '%' operator.
        node.left is an ast.Str or ast.Constant node.
        node.right represents the RHS of the '%' operator.

        Convert this tree to an f-string, if possible.
        Replace the node's entire tree with a new ast.Str node.
        Replace all the relevant tokens with a single new 'string' token.
        """
        trace = False
        string_node = ast.Str if g.python_version_tuple < (3, 12, 0) else ast.Constant
        assert isinstance(node.left, string_node), (repr(node.left), g.callers())

        # Careful: use the tokens, not Str.s or Constant.value. This preserves spelling.
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
    #@+node:ekr.20191222102831.3: *4* fs.clean_ws
    ws_pat = re.compile(r'(\s+)([:!][0-9]\})')

    def clean_ws(self, s: str) -> str:
        """Carefully remove whitespace before ! and : specifiers."""
        s = re.sub(self.ws_pat, r'\2', s)
        return s
    #@+node:ekr.20191222102831.4: *4* fs.compute_result & helpers
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
    #@+node:ekr.20200215074309.1: *5* fs.check_back_slashes
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
    #@+node:ekr.20191222102831.7: *5* fs.change_quotes
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
    #@+node:ekr.20191222102831.6: *4* fs.munge_spec
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
    #@+node:ekr.20191222102831.9: *4* fs.scan_format_string
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
    #@+node:ekr.20191222104224.1: *4* fs.scan_rhs
    def scan_rhs(self, node: Node) -> list[list[Token]]:
        """
        Scan the right-hand side of a potential f-string.

        Return a list of the token lists for each element.
        """
        trace = False
        # First, Try the most common cases.
        string_node = ast.Str if g.python_version_tuple < (3, 12, 0) else ast.Constant
        if isinstance(node, string_node):
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
                    g.printObj(tokens, tag=f"Tokens for item {i}")
            return result
        # Now we expect only one result.
        tokens = tokens_for_node(self.filename, node, self.tokens)
        return [tokens]
    #@+node:ekr.20191226155316.1: *4* fs.substitute_values
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
    #@+node:ekr.20200214142019.1: *3* fs.message
    def message(self, message: str) -> None:  # pragma: no cover.
        """
        Print one or more message lines aligned on the first colon of the message.
        """
        # Print a leading blank line.
        print('')
        # Calculate the padding.
        lines = g.splitLines(message)
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
    #@+node:ekr.20191225054848.1: *3* fs.replace
    def replace(self, node: Node, s: str, values: list[list[Token]]) -> None:
        """
        Replace node with an ast.Str or ast.Constant node for s.
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
        new_node: ast.AST
        if g.python_version_tuple < (3, 12, 0):
            # pylint: disable=deprecated-class
            new_node = ast.Str()
            new_node.s = s
        else:
            new_node = ast.Constant()
            new_node.value = s
        replace_node(new_node, node)
        # Update the token.
        token = self.tokens[i1]
        token.node = new_node
        # Update the token list.
        add_token_to_token_list(token, new_node)
    #@-others
#@+node:ekr.20240104082325.1: ** class InputToken
class InputToken:
    """
    A class representing an Orange input token.
    """

    def __init__(self, kind: str, value: str):

        self.kind = kind
        self.value = value
        self.five_tuple: tuple = None
        self.index = 0
        self.line = ''  # The entire line containing the token.
        self.line_number = 0  # The line number, for errors and dumps.
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
    #@+node:ekr.20240104082325.2: *3* itoken.brief_dump
    def brief_dump(self) -> str:  # pragma: no cover
        """Dump a token."""
        return (
            f"{self.index:>3} line: {self.line_number:<2} "
            f"{self.kind:>15} {self.show_val(100)}")
    #@+node:ekr.20240104082325.3: *3* itoken.dump
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
    #@+node:ekr.20240104082325.4: *3* itoken.dump_header
    def dump_header(self) -> None:  # pragma: no cover
        """Print the header for token.dump"""
        print(
            f"\n"
            f"         node    {'':10} token {'':10}   token\n"
            f"line index class {'':10} index {'':10} kind value\n"
            f"==== ===== ===== {'':10} ===== {'':10} ==== =====\n")
    #@+node:ekr.20240104082325.5: *3* itoken.error_dump
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
    #@+node:ekr.20240104082325.6: *3* itoken.show_val
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
#@+node:ekr.20240104082408.1: ** class OutputToken
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
    #@+node:ekr.20240104112740.9: *3* otoken.show_val
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
#@+node:ekr.20200107170126.1: ** class ParseState
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
#@+node:ekr.20191231084514.1: ** class ReassignTokens
class ReassignTokens:
    """A class that reassigns tokens to more appropriate ast nodes."""
    #@+others
    #@+node:ekr.20191231084640.1: *3* reassign.reassign
    def reassign(self, filename: str, tokens: list[Token], tree: Node) -> None:
        """The main entry point."""
        self.filename = filename
        self.tokens = tokens
        # Just handle Call nodes.
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                self.visit_call(node)
    #@+node:ekr.20191231084853.1: *3* reassign.visit_call
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
#@+node:ekr.20191110080535.1: ** class Token
class Token:
    """
    A class representing a *general* token.

    The TOG makes no distinction between input and output tokens.
    """

    def __init__(self, kind: str, value: str):

        self.kind = kind
        self.value = value
        # Injected by Tokenizer.add_token.
        self.five_tuple: tuple = None
        self.index = 0
        # The entire line containing the token.
        # Same as five_tuple.line.
        self.line = ''
        # The line number, for errors and dumps.
        # Same as five_tuple.start[0]
        self.line_number = 0
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
    #@+node:ekr.20191231114927.1: *3* token.brief_dump
    def brief_dump(self) -> str:  # pragma: no cover
        """Dump a token."""
        return (
            f"{self.index:>3} line: {self.line_number:<2} "
            f"{self.kind:>15} {self.show_val(100)}")
    #@+node:ekr.20200223022950.11: *3* token.dump
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
    #@+node:ekr.20200121081151.1: *3* token.dump_header
    def dump_header(self) -> None:  # pragma: no cover
        """Print the header for token.dump"""
        print(
            f"\n"
            f"         node    {'':10} token {'':10}   token\n"
            f"line index class {'':10} index {'':10} kind value\n"
            f"==== ===== ===== {'':10} ===== {'':10} ==== =====\n")
    #@+node:ekr.20191116154328.1: *3* token.error_dump
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
    #@+node:ekr.20191113095507.1: *3* token.show_val
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
#@+node:ekr.20191110165235.1: ** class Tokenizer
class Tokenizer:

    """Create a list of Tokens from contents."""

    token_kind: str
    results: list[Any] = []  # A list of Tokens or InputTokens.

    #@+others
    #@+node:ekr.20191110165235.2: *3* tokenizer.add_token
    token_index = 0
    prev_line_token = None

    def add_token(self, kind: str, five_tuple: tuple, line: str, s_row: int, value: str) -> None:
        """
        Add an InputToken to the results list.

        Subclasses could override this method to filter out specific tokens.
        """
        assert self.token_kind in ('Token', 'InputToken'), repr(self.token_kind)
        tok: Union[Token, InputToken]
        if self.token_kind == 'Token':
            tok = Token(kind, value)
        else:
            tok = InputToken(kind, value)
        tok.five_tuple = five_tuple
        tok.index = self.token_index
        # Bump the token index.
        self.token_index += 1
        tok.line = line
        tok.line_number = s_row
        self.results.append(tok)
    #@+node:ekr.20191110170551.1: *3* tokenizer.check_results
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
    #@+node:ekr.20191110165235.3: *3* tokenizer.create_input_tokens
    def create_input_tokens(self, contents: str, tokens: Generator) -> list[InputToken]:
        """
        Generate a list of Token's from tokens, a list of 5-tuples.
        """
        self.token_kind = 'InputToken'  # For add_token.
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
    #@+node:ekr.20240104114906.1: *3* tokenizer.create_tokens
    def create_tokens(self, contents: str, tokens: Generator) -> list[Token]:
        """
        Generate a list of Token's from tokens, a list of 5-tuples.
        """
        self.token_kind = 'Token'  # For add_token.
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
    #@+node:ekr.20191110165235.4: *3* tokenizer.do_token (the gem)
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
#@+node:ekr.20191113063144.1: ** class TokenOrderGenerator
class TokenOrderGenerator:
    """
    A class that traverses ast (parse) trees in token order.

    Requires Python 3.9+.

    Overview: https://github.com/leo-editor/leo-editor/issues/1440#issue-522090981

    Theory of operation:
    - https://github.com/leo-editor/leo-editor/issues/1440#issuecomment-573661883
    - https://leo-editor.github.io/leo-editor/appendices.html#tokenorder-classes-theory-of-operation

    How to: https://leo-editor.github.io/leo-editor/appendices.html#tokenorder-class-how-to

    Project history: https://github.com/leo-editor/leo-editor/issues/1440#issuecomment-574145510
    """

    begin_end_stack: list[str] = []
    debug_flag: bool = False  # Set by 'debug' in trace_list kwarg.
    equal_sign_spaces = True  # A flag for orange.do_equal_op
    n_nodes = 0  # The number of nodes that have been visited.
    node_index = 0  # The index into the node_stack.
    node_stack: list[ast.AST] = []  # The stack of parent nodes.
    try_stack: list[str] = []  # A stack of either '' (Try) or '*' (TryStar)
    trace_token_method: bool = False  # True: trace the token method

    #@+others
    #@+node:ekr.20200103174914.1: *3* tog: Init...
    #@+node:ekr.20191228184647.1: *4* tog.balance_tokens
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
    #@+node:ekr.20191113063144.4: *4* tog.create_links (inits all ivars)
    def create_links(self, tokens: list[Token], tree: Node, file_name: str = '') -> None:
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
    #@+node:ekr.20191229071733.1: *4* tog.init_from_file
    def init_from_file(self, filename: str) -> tuple[str, str, list[Token], Node]:  # pragma: no cover
        """
        Create the tokens and ast tree for the given file.
        Create links between tokens and the parse tree.
        Return (contents, encoding, tokens, tree).
        """
        self.level = 0
        self.filename = filename
        contents, encoding = g.readFileIntoString(filename)
        if not contents:
            return None, None, None, None
        self.tokens = tokens = self.make_tokens(contents)
        self.tree = tree = parse_ast(contents)
        self.create_links(tokens, tree)
        return contents, encoding, tokens, tree
    #@+node:ekr.20191229071746.1: *4* tog.init_from_string
    def init_from_string(self, contents: str, filename: str) -> tuple[list[Token], Node]:  # pragma: no cover
        """
        Tokenize, parse and create links in the contents string.

        Return (tokens, tree).
        """
        self.filename = filename
        self.level = 0
        self.tokens = tokens = self.make_tokens(contents)
        self.tree = tree = parse_ast(contents)
        self.create_links(tokens, tree)
        return tokens, tree
    #@+node:ekr.20240104114807.1: *4* tog.make_tokens
    def make_tokens(self, contents: str) -> list[Token]:
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
        tokens = Tokenizer().create_tokens(contents, five_tuples)
        assert check(contents, tokens)
        return tokens
    #@+node:ekr.20220402052020.1: *3* tog: synchronizer...
    # The synchronizer sync tokens to nodes.
    #@+node:ekr.20200110162044.1: *4* tog.find_next_significant_token
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
    #@+node:ekr.20191125120814.1: *4* tog.set_links
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
                'set_links\n'
                f"       file: {self.filename}\n"
                f"{line_s:>12} {token.line.strip()}\n"
                f"token index: {self.px}\n"
                f"token.node is not None\n"
                f" token.node: {token.node.__class__.__name__}\n"
                f"    callers: {g.callers()}"
            )
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
    #@+node:ekr.20191124083124.1: *4* tog.name
    def name(self, val: str) -> None:
        """Sync to the given name token."""
        aList = val.split('.')
        if len(aList) == 1:
            self.token('name', val)
        else:
            for i, part in enumerate(aList):
                self.token('name', part)
                if i < len(aList) - 1:
                    self.op('.')
    #@+node:ekr.20220402052102.1: *4* tog.op
    def op(self, val: str) -> None:
        """
        Sync to the given operator.

        val may be '(' or ')' *only* if the parens *will* actually exist in the
        token list.
        """
        self.token('op', val)
    #@+node:ekr.20191113063144.7: *4* tog.token
    px = -1  # Index of the previously synced token.

    def token(self, kind: str, val: str) -> None:
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

        if self.trace_token_method:  # A Superb trace.
            g.trace(
                f"px: {self.px:4} "
                f"node: {node.__class__.__name__:<14} "
                f"significant? {int(is_significant(kind, val))} "
                f"{kind:>10}: {val!r}")
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
                    'tog.token\n'
                    f"       file: {self.filename}\n"
                    f"{line_s:>12} {g.truncate(token.line.strip(), 40)!r}\n"
                    f"Looking for: {kind}.{g.truncate(val, 40)!r}\n"
                    f"      found: {token.kind}.{g.truncate(token.value, 40)!r}\n"
                    f"token.index: {token.index}\n"
                )
            # Skip the insignificant token.
            px += 1
        else:  # pragma: no cover
            val = str(val)  # for g.truncate.
            raise AssignLinksError(
                'tog.token 2\n'
                 f"       file: {self.filename}\n"
                 f"Looking for: {kind}.{g.truncate(val, 40)}\n"
                 f"      found: end of token list"
            )
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
    #@+node:ekr.20231214173003.1: *4* tog.string_helper & helpers
    def string_helper(self, node: Node) -> None:
        """
        Common string and f-string handling for Constant, JoinedStr and Str nodes.

        Handle all concatenated strings, that is, strings separated only by whitespace.
        """

        # The next significant token must be a string or f-string.
        message1 = f"Old token: self.px: {self.px} token @ px: {self.tokens[self.px]}\n"
        token = self.find_next_significant_token()
        message2 = f"New token: self.px: {self.px} token @ px: {self.tokens[self.px]}\n"
        fail_s = f"tog.string_helper: no string!\n{message1}{message2}"
        assert token and token.kind in ('string', 'fstring_start'), fail_s

        # Handle all adjacent strings.
        while token and token.kind in ('string', 'fstring_start'):
            if token.kind == 'string':
                self.token(token.kind, token.value)
            else:
                self.token(token.kind, token.value)
                self.sync_to_kind('fstring_end')
            # Check for concatenated strings.
            token = self.find_next_non_ws_token()
    #@+node:ekr.20231213174617.1: *5* tog.sync_to_kind
    def sync_to_kind(self, kind: str) -> None:
        """Sync to the next significant token of the given kind."""
        assert is_significant_kind(kind), repr(kind)
        while next_token := self.find_next_significant_token():
            self.token(next_token.kind, next_token.value)
            if next_token.kind in (kind, 'endtoken'):
                break

    #@+node:ekr.20231214054225.1: *5* tog.find_next_non_ws_token
    def find_next_non_ws_token(self) -> Optional[Token]:
        """
        Scan from *after* self.tokens[px] looking for the next token that isn't
        whitespace.

        Return the token, or None. Never change self.px.
        """
        px = self.px + 1
        while px < len(self.tokens):
            token = self.tokens[px]
            px += 1
            if token.kind not in ('comment', 'encoding', 'indent', 'newline', 'nl', 'ws'):
                return token

        # This should never happen: endtoken isn't whitespace.
        return None  # pragma: no cover
    #@+node:ekr.20191223052749.1: *3* tog: Traversal...
    #@+node:ekr.20191113063144.3: *4* tog.enter_node
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
    #@+node:ekr.20200104032811.1: *4* tog.leave_node
    def leave_node(self, node: Node) -> None:
        """Leave a visitor."""
        # begin_visitor and end_visitor must be paired.
        entry_name = self.begin_end_stack.pop()
        assert entry_name == node.__class__.__name__, f"{entry_name!r} {node.__class__.__name__}"
        assert self.node == node, (repr(self.node), repr(node))
        # Restore self.node.
        self.node = self.node_stack.pop()
    #@+node:ekr.20191113081443.1: *4* tog.visit
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
    #@+node:ekr.20191113063144.13: *3* tog: Visitors...
    #@+node:ekr.20191113063144.32: *4*  tog.keyword: not called!
    # keyword arguments supplied to call (NULL identifier for **kwargs)

    # keyword = (identifier? arg, expr value)

    def do_keyword(self, node: Node) -> None:  # pragma: no cover
        """A keyword arg in an ast.Call."""
        # This should never be called.
        # tog.handle_call_arguments calls self.visit(kwarg_arg.value) instead.
        filename = getattr(self, 'filename', '<no file>')
        raise AssignLinksError(
            f"do_keyword called: {g.callers(8)}\n"
            f"file: {filename}\n"
        )
    #@+node:ekr.20191113063144.14: *4* tog: Contexts
    #@+node:ekr.20191113063144.28: *5*  tog.arg
    # arg = (identifier arg, expr? annotation)

    def do_arg(self, node: Node) -> None:
        """This is one argument of a list of ast.Function or ast.Lambda arguments."""
        self.name(node.arg)
        annotation = getattr(node, 'annotation', None)
        if annotation is not None:
            self.op(':')
            self.visit(node.annotation)
    #@+node:ekr.20191113063144.27: *5*  tog.arguments
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


    #@+node:ekr.20191113063144.15: *5* tog.AsyncFunctionDef
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
        self.token('name', 'async')
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
    #@+node:ekr.20191113063144.16: *5* tog.ClassDef
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
    #@+node:ekr.20191113063144.17: *5* tog.FunctionDef
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
    #@+node:ekr.20191113063144.18: *5* tog.Interactive
    def do_Interactive(self, node: Node) -> None:  # pragma: no cover

        self.visit(node.body)
    #@+node:ekr.20191113063144.20: *5* tog.Lambda
    def do_Lambda(self, node: Node) -> None:

        self.name('lambda')
        self.visit(node.args)
        self.op(':')
        self.visit(node.body)
    #@+node:ekr.20191113063144.19: *5* tog.Module
    def do_Module(self, node: Node) -> None:

        # Encoding is a non-syncing statement.
        self.visit(node.body)
    #@+node:ekr.20191113063144.21: *4* tog: Expressions
    #@+node:ekr.20191113063144.22: *5* tog.Expr
    def do_Expr(self, node: Node) -> None:
        """An outer expression."""
        # No need to put parentheses.
        self.visit(node.value)
    #@+node:ekr.20191113063144.23: *5* tog.Expression
    def do_Expression(self, node: Node) -> None:  # pragma: no cover
        """An inner expression."""
        # No need to put parentheses.
        self.visit(node.body)
    #@+node:ekr.20191113063144.24: *5* tog.GeneratorExp
    def do_GeneratorExp(self, node: Node) -> None:

        # '<gen %s for %s>' % (elt, ','.join(gens))
        # No need to put parentheses or commas.
        self.visit(node.elt)
        self.visit(node.generators)
    #@+node:ekr.20210321171703.1: *5* tog.NamedExpr
    # NamedExpr(expr target, expr value)

    def do_NamedExpr(self, node: Node) -> None:  # Python 3.8+

        self.visit(node.target)
        self.op(':=')
        self.visit(node.value)
    #@+node:ekr.20191113063144.26: *4* tog: Operands
    #@+node:ekr.20191113063144.29: *5* tog.Attribute
    # Attribute(expr value, identifier attr, expr_context ctx)

    def do_Attribute(self, node: Node) -> None:

        self.visit(node.value)
        self.op('.')
        self.name(node.attr)  # A string.
    #@+node:ekr.20191113063144.30: *5* tog.Bytes
    def do_Bytes(self, node: Node) -> None:

        """
        It's invalid to mix bytes and non-bytes literals, so just
        advancing to the next 'string' token suffices.
        """
        token = self.find_next_significant_token()
        self.token('string', token.value)
    #@+node:ekr.20191113063144.33: *5* tog.comprehension
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
    #@+node:ekr.20191113063144.34: *5* tog.Constant
    # Constant(constant value, string? kind)

    def do_Constant(self, node: Node) -> None:
        """
        https://greentreesnakes.readthedocs.io/en/latest/nodes.html

        A constant. The value attribute holds the Python object it represents.
        This can be simple types such as a number, string or None, but also
        immutable container types (tuples and frozensets) if all of their
        elements are constant.
        """
        if node.value == Ellipsis:
            self.op('...')
        elif isinstance(node.value, str):
            self.string_helper(node)
        elif isinstance(node.value, int):
            # Look at the next token to distinguish 0/1 from True/False.
            token = self.find_next_significant_token()
            kind, value = token.kind, token.value
            assert kind in ('name', 'number'), (kind, value, g.callers())
            if kind == 'name':
                self.name(value)
            else:
                self.token(kind, repr(value))
        elif isinstance(node.value, float):
            self.token('number', repr(node.value))
        elif isinstance(node.value, bytes):
            self.do_Bytes(node)
        elif isinstance(node.value, tuple):
            self.do_Tuple(node)
        elif isinstance(node.value, frozenset):
            self.do_Set(node)
        elif node.value is None:
            self.name('None')
        else:
            # Unknown type.
            g.trace('----- Oops -----', repr(node), g.callers())
    #@+node:ekr.20191113063144.35: *5* tog.Dict
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
    #@+node:ekr.20191113063144.36: *5* tog.DictComp
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
    #@+node:ekr.20191113063144.37: *5* tog.Ellipsis
    def do_Ellipsis(self, node: Node) -> None:  # pragma: no cover (Does not exist for python 3.8+)

        self.op('...')
    #@+node:ekr.20191113063144.38: *5* tog.ExtSlice
    # https://docs.python.org/3/reference/expressions.html#slicings

    # ExtSlice(slice* dims)

    def do_ExtSlice(self, node: Node) -> None:  # pragma: no cover (deprecated)

        # ','.join(node.dims)
        for i, z in enumerate(node.dims):
            self.visit(z)
            if i < len(node.dims) - 1:
                self.op(',')
    #@+node:ekr.20191113063144.39: *5* tog.FormattedValue
    # FormattedValue(expr value, int conversion, expr? format_spec)  Python 3.12+

    def do_FormattedValue(self, node: Node) -> None:  # pragma: no cover
        """
        This node represents the *components* of a *single* f-string.

        Happily, JoinedStr nodes *also* represent *all* f-strings.

        JoinedStr does *not* visit the FormattedValue node,
        so the TOG should *never* visit this node!
        """
        raise AssignLinksError(f"do_FormattedValue called: {g.callers()}")
    #@+node:ekr.20191113063144.40: *5* tog.Index
    def do_Index(self, node: Node) -> None:  # pragma: no cover (deprecated)

        self.visit(node.value)
    #@+node:ekr.20191113063144.41: *5* tog.JoinedStr
    # JoinedStr(expr* values)

    def do_JoinedStr(self, node: Node) -> None:
        """
        JoinedStr nodes represent at least one f-string and all other strings
        concatenated to it.

        Analyzing JoinedStr.values would be extremely tricky, for reasons that
        need not be explained here.

        Instead, we get the tokens *from the token list itself*!
        """

        # Everything in the JoinedStr tree is a string.
        # Do *not* call self.visit.

        # This works for all versions of Python!
        self.string_helper(node)
    #@+node:ekr.20191113063144.42: *5* tog.List
    def do_List(self, node: Node) -> None:

        # No need to put commas.
        self.op('[')
        self.visit(node.elts)
        self.op(']')
    #@+node:ekr.20191113063144.43: *5* tog.ListComp
    # ListComp(expr elt, comprehension* generators)

    def do_ListComp(self, node: Node) -> None:

        self.op('[')
        self.visit(node.elt)
        for z in node.generators:
            self.visit(z)
        self.op(']')
    #@+node:ekr.20191113063144.44: *5* tog.Name
    def do_Name(self, node: Node) -> None:

        self.name(node.id)

    #@+node:ekr.20191113063144.47: *5* tog.Set
    # Set(expr* elts)

    def do_Set(self, node: Node) -> None:

        self.op('{')
        self.visit(node.elts)
        self.op('}')
    #@+node:ekr.20191113063144.48: *5* tog.SetComp
    # SetComp(expr elt, comprehension* generators)

    def do_SetComp(self, node: Node) -> None:

        self.op('{')
        self.visit(node.elt)
        for z in node.generators or []:
            self.visit(z)
        self.op('}')
    #@+node:ekr.20191113063144.49: *5* tog.Slice
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
    #@+node:ekr.20191113063144.50: *5* tog.Str (deprecated)
    # DeprecationWarning: ast.Str is deprecated and will be removed in Python 3.14;
    # use ast.Constant instead

    if g.python_version_tuple < (3, 12, 0):

        def do_Str(self, node: Node) -> None:
            """This node represents a string constant."""
            self.string_helper(node)
    #@+node:ekr.20191113063144.51: *5* tog.Subscript
    # Subscript(expr value, slice slice, expr_context ctx)

    def do_Subscript(self, node: Node) -> None:

        self.visit(node.value)
        self.op('[')
        self.visit(node.slice)
        self.op(']')
    #@+node:ekr.20191113063144.52: *5* tog.Tuple
    # Tuple(expr* elts, expr_context ctx)

    def do_Tuple(self, node: Node) -> None:

        # Do not call op for parens or commas here.
        # They do not necessarily exist in the token list!
        self.visit(node.elts)
    #@+node:ekr.20191113063144.53: *4* tog: Operators
    #@+node:ekr.20191113063144.55: *5* tog.BinOp
    def do_BinOp(self, node: Node) -> None:

        op_name_ = op_name(node.op)
        self.visit(node.left)
        self.op(op_name_)
        self.visit(node.right)
    #@+node:ekr.20191113063144.56: *5* tog.BoolOp
    # BoolOp(boolop op, expr* values)

    def do_BoolOp(self, node: Node) -> None:

        # op.join(node.values)
        op_name_ = op_name(node.op)
        for i, z in enumerate(node.values):
            self.visit(z)
            if i < len(node.values) - 1:
                self.name(op_name_)
    #@+node:ekr.20191113063144.57: *5* tog.Compare
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
    #@+node:ekr.20191113063144.58: *5* tog.UnaryOp
    def do_UnaryOp(self, node: Node) -> None:

        op_name_ = op_name(node.op)
        if op_name_.isalpha():
            self.name(op_name_)
        else:
            self.op(op_name_)
        self.visit(node.operand)
    #@+node:ekr.20191113063144.59: *5* tog.IfExp (ternary operator)
    # IfExp(expr test, expr body, expr orelse)

    def do_IfExp(self, node: Node) -> None:

        self.visit(node.body)
        self.name('if')
        self.visit(node.test)
        self.name('else')
        self.visit(node.orelse)
    #@+node:ekr.20191113063144.60: *4* tog: Statements
    #@+node:ekr.20191113063144.83: *5*  tog.Starred
    # Starred(expr value, expr_context ctx)

    def do_Starred(self, node: Node) -> None:
        """A starred argument to an ast.Call"""
        self.op('*')
        self.visit(node.value)
    #@+node:ekr.20191113063144.61: *5* tog.AnnAssign
    # AnnAssign(expr target, expr annotation, expr? value, int simple)

    def do_AnnAssign(self, node: Node) -> None:

        # {node.target}:{node.annotation}={node.value}\n'
        self.visit(node.target)
        self.op(':')
        self.visit(node.annotation)
        if node.value is not None:  # #1851
            self.op('=')
            self.visit(node.value)
    #@+node:ekr.20191113063144.62: *5* tog.Assert
    # Assert(expr test, expr? msg)

    def do_Assert(self, node: Node) -> None:

        # Guards...
        msg = getattr(node, 'msg', None)
        # No need to put parentheses or commas.
        self.name('assert')
        self.visit(node.test)
        if msg is not None:
            self.visit(node.msg)
    #@+node:ekr.20191113063144.63: *5* tog.Assign
    def do_Assign(self, node: Node) -> None:

        for z in node.targets:
            self.visit(z)
            self.op('=')
        self.visit(node.value)
    #@+node:ekr.20191113063144.64: *5* tog.AsyncFor
    def do_AsyncFor(self, node: Node) -> None:

        # The def line...
        self.token('name', 'async')
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
    #@+node:ekr.20191113063144.65: *5* tog.AsyncWith
    def do_AsyncWith(self, node: Node) -> None:

        self.token('name', 'async')
        self.do_With(node)
    #@+node:ekr.20191113063144.66: *5* tog.AugAssign
    # AugAssign(expr target, operator op, expr value)

    def do_AugAssign(self, node: Node) -> None:

        # %s%s=%s\n'
        op_name_ = op_name(node.op)
        self.visit(node.target)
        self.op(op_name_ + '=')
        self.visit(node.value)
    #@+node:ekr.20191113063144.67: *5* tog.Await
    # Await(expr value)

    def do_Await(self, node: Node) -> None:

        self.token('name', 'await')
        self.visit(node.value)
    #@+node:ekr.20191113063144.68: *5* tog.Break
    def do_Break(self, node: Node) -> None:

        self.name('break')
    #@+node:ekr.20191113063144.31: *5* tog.Call & helpers
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
    #@+node:ekr.20191204114930.1: *6* tog.arg_helper
    def arg_helper(self, node: Union[Node, str]) -> None:
        """
        Yield the node, with a special case for strings.
        """
        if isinstance(node, str):
            self.token('name', node)
        else:
            self.visit(node)
    #@+node:ekr.20191204105506.1: *6* tog.handle_call_arguments
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
            g.printObj([ast.dump(z) for z in args], tag='args')
            g.printObj([ast.dump(z) for z in keywords], tag='keywords')

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
    #@+node:ekr.20191113063144.69: *5* tog.Continue
    def do_Continue(self, node: Node) -> None:

        self.name('continue')
    #@+node:ekr.20191113063144.70: *5* tog.Delete
    def do_Delete(self, node: Node) -> None:

        # No need to put commas.
        self.name('del')
        self.visit(node.targets)
    #@+node:ekr.20191113063144.71: *5* tog.ExceptHandler
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
    #@+node:ekr.20191113063144.73: *5* tog.For
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
    #@+node:ekr.20191113063144.74: *5* tog.Global
    # Global(identifier* names)

    def do_Global(self, node: Node) -> None:

        self.name('global')
        for z in node.names:
            self.name(z)
    #@+node:ekr.20191113063144.75: *5* tog.If & helpers
    # If(expr test, stmt* body, stmt* orelse)

    def do_If(self, node: Node) -> None:
        #@+<< do_If docstring >>
        #@+node:ekr.20191122222412.1: *6* << do_If docstring >>
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
    #@+node:ekr.20191113063144.76: *5* tog.Import & helper
    def do_Import(self, node: Node) -> None:

        self.name('import')
        for alias in node.names:
            self.name(alias.name)
            if alias.asname:
                self.name('as')
                self.name(alias.asname)
    #@+node:ekr.20191113063144.77: *5* tog.ImportFrom
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
    #@+node:ekr.20220401034726.1: *5* tog.Match* (Python 3.10+)
    # Match(expr subject, match_case* cases)

    # match_case = (pattern pattern, expr? guard, stmt* body)

    # https://docs.python.org/3/reference/compound_stmts.html#match

    def do_Match(self, node: Node) -> None:

        cases = getattr(node, 'cases', [])
        self.name('match')
        self.visit(node.subject)
        self.op(':')
        for case in cases:
            self.visit(case)
    #@+node:ekr.20220401034726.2: *6* tog.match_case
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
    #@+node:ekr.20220401034726.3: *6* tog.MatchAs
    # MatchAs(pattern? pattern, identifier? name)

    def do_MatchAs(self, node: Node) -> None:
        pattern = getattr(node, 'pattern', None)
        name = getattr(node, 'name', None)
        if pattern and name:
            self.visit(pattern)
            self.name('as')
            self.name(name)
        elif name:
            self.name(name)
        elif pattern:
            self.visit(pattern)  # pragma: no cover
        else:
            self.token('name', '_')
    #@+node:ekr.20220401034726.4: *6* tog.MatchClass
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
    #@+node:ekr.20220401034726.5: *6* tog.MatchMapping
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
    #@+node:ekr.20220401034726.6: *6* tog.MatchOr
    # MatchOr(pattern* patterns)

    def do_MatchOr(self, node: Node) -> None:
        patterns = getattr(node, 'patterns', [])
        for i, pattern in enumerate(patterns):
            if i > 0:
                self.op('|')
            self.visit(pattern)
    #@+node:ekr.20220401034726.7: *6* tog.MatchSequence
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
            raise AssignLinksError('do_MatchSequence: Ill-formed tuple')  # pragma: no cover
        if token:
            self.op(token.value)
        for pattern in patterns:
            self.visit(pattern)
        if token:
            self.op(']' if token.value == '[' else ')')
    #@+node:ekr.20220401034726.8: *6* tog.MatchSingleton
    # MatchSingleton(constant value)

    def do_MatchSingleton(self, node: Node) -> None:
        """Match True, False or None."""
        # g.trace(repr(node.value))
        self.token('name', repr(node.value))
    #@+node:ekr.20220401034726.9: *6* tog.MatchStar
    # MatchStar(identifier? name)

    def do_MatchStar(self, node: Node) -> None:
        name = getattr(node, 'name', None)
        self.op('*')
        if name:
            self.name(name)
    #@+node:ekr.20220401034726.10: *6* tog.MatchValue
    # MatchValue(expr value)

    def do_MatchValue(self, node: Node) -> None:

        self.visit(node.value)
    #@+node:ekr.20191113063144.78: *5* tog.Nonlocal
    # Nonlocal(identifier* names)

    def do_Nonlocal(self, node: Node) -> None:

        # nonlocal %s\n' % ','.join(node.names))
        # No need to put commas.
        self.name('nonlocal')
        for z in node.names:
            self.name(z)
    #@+node:ekr.20191113063144.79: *5* tog.Pass
    def do_Pass(self, node: Node) -> None:

        self.name('pass')
    #@+node:ekr.20191113063144.81: *5* tog.Raise
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
    #@+node:ekr.20191113063144.82: *5* tog.Return
    def do_Return(self, node: Node) -> None:

        self.name('return')
        self.visit(node.value)
    #@+node:ekr.20191113063144.85: *5* tog.Try
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
    #@+node:ekr.20230615211005.1: *5* tog.TryStar
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
    #@+node:ekr.20191113063144.88: *5* tog.While
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
    #@+node:ekr.20191113063144.89: *5* tog.With
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
    #@+node:ekr.20191113063144.90: *5* tog.Yield
    def do_Yield(self, node: Node) -> None:

        self.name('yield')
        if hasattr(node, 'value'):
            self.visit(node.value)
    #@+node:ekr.20191113063144.91: *5* tog.YieldFrom
    # YieldFrom(expr value)

    def do_YieldFrom(self, node: Node) -> None:

        self.name('yield')
        self.name('from')
        self.visit(node.value)
    #@+node:ekr.20231208092310.1: *4* tog: Types
    #@+node:ekr.20231208092945.1: *5* tog.ParamSpec
    # ParamSpec(identifier name)

    def do_ParamSpec(self, node: Node) -> None:

        self.visit(node.name)
    #@+node:ekr.20231208092326.1: *5* tog.TypeAlias
    # TypeAlias(expr name, type_param* type_params, expr value)

    def do_TypeAlias(self, node: Node) -> None:

        params = getattr(node, 'type_params', [])
        self.visit(node.name)
        for param in params:
            self.visit(param)
        self.visit(node.value)
    #@+node:ekr.20231208092726.1: *5* tog.TypeVar
    #  TypeVar(identifier name, expr? bound)

    def do_TypeVar(self, node: Node) -> None:

        bound = getattr(node, 'bound', None)
        self.visit(node.name)
        if bound:
            self.visit(bound)
    #@+node:ekr.20231208093043.1: *5* tog.TypeVarTuple
    # TypeVarTuple(identifier name)

    def do_TypeVarTuple(self, node: Node) -> None:

        self.visit(node.name)
    #@-others
#@-others

#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
