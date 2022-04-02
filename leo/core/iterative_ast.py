# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20220402094143.1: * @file iterative_ast.py
#@@first
#@+<< imports >>
#@+node:ekr.20220402095728.1: ** << imports >> (iterative_ast.py)
import ast
import sys
from typing import List, Optional, Tuple  # Any, Dict, Generator, Union
from leo.core.leoAst import LeoGlobals
from leo.core.leoAst import AssignLinksError
from leo.core.leoAst import op_name
from leo.core.leoAst import main
from leo.core.leoAst import add_token_to_token_list, is_significant_token, find_statement_node
from leo.core.leoAst import make_tokens, parse_ast
from leo.core.leoAst import read_file_with_encoding
#@-<< imports >>

Node = ast.AST
v1, v2, junk1, junk2, junk3 = sys.version_info
py_version = (v1, v2)

# Async tokens exist only in Python 3.5 and 3.6.
# https://docs.python.org/3/library/token.html
has_async_tokens = (3, 5) <= py_version <= (3, 6)
#@+others
#@+node:ekr.20220330191947.1: ** class IterativeTokenGenerator
class IterativeTokenGenerator:
    """
    Experimental iterative token syncing class.
    """
    
    begin_end_stack: List[str] = []
    n_nodes = 0  # The number of nodes that have been visited.
    level = 0
    node_index = 0  # The index into the node_stack.
    node_stack: List[ast.AST] = []  # The stack of parent nodes.
    
    
    #@+others
    #@+node:ekr.20220402095550.1: *3* iterative: Init...
    #@+node:ekr.20220402095550.2: *4* tog.balance_tokens
    def balance_tokens(self, tokens: List["Token"]) -> int:
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
    #@+node:ekr.20220402095550.3: *4* tog.create_links
    def create_links(self, tokens: List["Token"], tree: Node, file_name: str='') -> List:
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
    #@+node:ekr.20220402095550.4: *4* tog.init_from_file
    def init_from_file(self, filename: str) -> Tuple[str, str, List["Token"], Node]:  # pragma: no cover
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
    #@+node:ekr.20220402095550.5: *4* tog.init_from_string
    def init_from_string(self, contents: str, filename: str) -> Tuple[List["Token"], Node]:  # pragma: no cover
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
    #@+node:ekr.20220402094825.1: *3* iterative: Syncronizers...
    # The synchronizer sync tokens to nodes.
    #@+node:ekr.20220402094825.2: *4* tog.find_next_significant_token
    def find_next_significant_token(self) -> Optional["Token"]:
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
    #@+node:ekr.20220402094825.3: *4* tog.set_links
    last_statement_node = None

    def set_links(self, node: Node, token: "Token") -> None:
        """Make two-way links between token and the given node."""
        # Don't bother assigning comment, comma, parens, ws and endtoken tokens.
        if token.kind == 'comment':
            # Append the comment to node.comment_list.
            comment_list: List["Token"] = getattr(node, 'comment_list', [])
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
            # Set an *auxilliary* link for the split/join logic.
            # Do *not* set token.node!
            token.statement_node = self.last_statement_node
            return
        if is_significant_token(token):
            # Link the token to the ast node.
            token.node = node
            # Add the token to node's token_list.
            add_token_to_token_list(token, node)
    #@+node:ekr.20220402094825.4: *4* tog.sync_name (aka name)
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
    #@+node:ekr.20220402094825.5: *4* tog.sync_op (aka op)
    def sync_op(self, val: str) -> None:
        """
        Sync to the given operator.

        val may be '(' or ')' *only* if the parens *will* actually exist in the
        token list.
        """
        self.sync_token('op', val)

    op = sync_op  # For readability.
    #@+node:ekr.20220402094825.6: *4* tog.sync_token (aka token)
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
        # g.trace(
            # f"px: {self.px:2} "
            # f"node: {node.__class__.__name__:<10} "
            # f"kind: {kind:>10}: val: {val!r}")
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
    #@+node:ekr.20220330164313.1: *3* iterative: Traversal...
    #@+node:ekr.20220402094946.2: *4* iterative.enter_node
    def enter_node(self, node: Node) -> None:
        """Enter a node."""
        # Update the stats.
        self.n_nodes += 1
        # Do this first, *before* updating self.node.
        node.parent = self.node
        if self.node:
            children: List[Node] = getattr(self.node, 'children', [])
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
    #@+node:ekr.20220402094946.3: *4* iterative.leave_node
    def leave_node(self, node: Node) -> None:
        """Leave a visitor."""
        # begin_visitor and end_visitor must be paired.
        entry_name = self.begin_end_stack.pop()
        assert entry_name == node.__class__.__name__, f"{entry_name!r} {node.__class__.__name__}"
        assert self.node == node, (repr(self.node), repr(node))
        # Restore self.node.
        self.node = self.node_stack.pop()
    #@+node:ekr.20220330120220.1: *4* iterative.main_loop
    def main_loop(self, node):

        func = getattr(self, 'do_' + node.__class__.__name__, None)
        if not func:
            print('main_loop: invalid ast node:', repr(node))
            return
        
        exec_list = [(func, node)]
        while exec_list:
            func, arg = exec_list.pop(0)
            result = func(arg)
            if result:
                # Prepend the result, a list of tuples.
                assert isinstance(result, list), repr(result)
                exec_list[:0] = result
    #@+node:ekr.20220330155314.1: *4* iterative.visit
    def visit(self, node):
        """Visit an ast node."""
        trace = False
        # This saves a lot of tests.
        if node is None:
            return []
        if trace:  # pragma: no cover
            # Keep this trace.
            cn = node.__class__.__name__ if node else ' '
            caller1, caller2 = g.callers(2).split(',')
            g.trace(f"{caller1:>15} {caller2:<14} {cn}")
        # More general, more convenient.
        if isinstance(node, (list, tuple)):
            result = []
            for z in node:
                if isinstance(z, ast.AST):
                  
                    result.append((self.visit, z)) ##### Test.
                else:
                    # Some fields may contain ints or strings.
                    assert isinstance(z, (int, str)), z.__class__.__name__
            return result
        # We *do* want to crash if the visitor doesn't exist.
        assert isinstance(node, ast.AST), repr(node)
        method = getattr(self, 'do_' + node.__class__.__name__)
        self.enter_node(node)
        # Visit the node.
        result = method(node)
        self.leave_node(node)
        return result
    #@+node:ekr.20220330133336.1: *3* iterative: Visitors
    #@+node:ekr.20220330133336.2: *4*  iterative.keyword: not called!
    # keyword arguments supplied to call (NULL identifier for **kwargs)

    # keyword = (identifier? arg, expr value)

    def do_keyword(self, node):  # pragma: no cover
        """A keyword arg in an ast.Call."""
        # This should never be called.
        # iterative.hande_call_arguments calls self.visit(kwarg_arg.value) instead.
        filename = getattr(self, 'filename', '<no file>')
        raise AssignLinksError(
            f"file: {filename}\n"
            f"do_keyword should never be called\n"
            f"{g.callers(8)}")
    #@+node:ekr.20220330133336.3: *4* iterative: Contexts (TEST)
    #@+node:ekr.20220330133336.4: *5*  iterative.arg
    # arg = (identifier arg, expr? annotation)

    def do_arg(self, node):
        """This is one argument of a list of ast.Function or ast.Lambda arguments."""

        annotation = getattr(node, 'annotation', None)
        result = [
            (self.name, node.arg),
        ]
        if annotation:
            result.extend([
                (self.op, ':'),
                (self.visit, annotation),
            ])
        return result

    #@+node:ekr.20220330133336.5: *5*  iterative.arguments
    # arguments = (
    #       arg* posonlyargs, arg* args, arg? vararg, arg* kwonlyargs,
    #       expr* kw_defaults, arg? kwarg, expr* defaults
    # )

    def do_arguments(self, node):
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
        result = []
        # 1. Sync the position-only args.
        if posonlyargs:
            for n, z in enumerate(posonlyargs):
                # self.visit(z)
                result.append((self.visit, z))
            # self.op('/')
            result.append(self.op, '/')
        # 2. Sync all args.
        for i, z in enumerate(node.args):
            # self.visit(z)
            result.append(self.visit, z)
            if i >= n_plain:
                # self.op('=')
                # self.visit(node.defaults[i - n_plain])
                result.extend([
                    (self.op, '='),
                    (self.visit, node.defaults[i - n_plain]),
                ])
        # 3. Sync the vararg.
        if vararg:
            # self.op('*')
            # self.visit(vararg)
            result.extend([
                (self.op, '*'),
                (self.visit, vararg),
            ])
        # 4. Sync the keyword-only args.
        if kwonlyargs:
            if not vararg:
                # self.op('*')
                result.append((self.op, '*'))
            for n, z in enumerate(kwonlyargs):
                # self.visit(z)
                result.append((self.visit, z))
                val = kw_defaults[n]
                if val is not None:
                    # self.op('=')
                    # self.visit(val)
                    result.extend([
                        (self.op, '='),
                        (self.visit, val),
                    ])
        # 5. Sync the kwarg.
        if kwarg:
            # self.op('**')
            # self.visit(kwarg)
            result.append([
                (self.op, '**'),
                (self.visit, kwarg),
            ])
        return result



    #@+node:ekr.20220330133336.6: *5* iterative.AsyncFunctionDef
    # AsyncFunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list,
    #                expr? returns)

    def do_AsyncFunctionDef(self, node):

        returns = getattr(node, 'returns', None)
        result = []
        # Decorators...
            # @{z}\n
        for z in node.decorator_list or []:
            result.extend([
                (self.op, '@'),
                (self.visit, z)
            ])
        # Signature...
            # def name(args): -> returns\n
            # def name(args):\n
        result.extend([
            (self.token, 'async'),  ###### test.
            (self.name, 'def'),
            (self.name, node.name),  # A string.
            (self.op, '('),
            (self.visit, node.args),
            (self.op, ')'),
        ])
        if returns is not None:
            result.extend([
                (self.op, '->'),
                (self.visit, node.returns),
            ])
        # Body...
        result.extend([
            (self.op, ':'),
            # (self.change_level, self.level + 1),
            (self.visit, node.body),
            # (self.change_level, self.level),
        ])
        return result
    #@+node:ekr.20220330133336.7: *5* iterative.ClassDef
    def do_ClassDef(self, node):
        
        result = []
        for z in node.decorator_list or []:
            # @{z}\n
            result.extend([
                (self.op, '@'),
                (self.visit, z),
            ])
        # class name(bases):\n
        result.extend([
            (self.name, 'class'),
            (self.name, node.name),  # A string.
        ])
        if node.bases:
            result.extend([
                (self.op, '('),
                (self.visit, node.bases),
                (self.op, ')'),
            ])
        result.extend([
            (self.op, ':'),
            # (self.change_level, self.level + 1),
            (self.visit, node.body),
            # (self.change_level, self.level),
        ])
        return result
    #@+node:ekr.20220330133336.8: *5* iterative.FunctionDef
    # FunctionDef(
    #   identifier name, arguments args,
    #   stmt* body,
    #   expr* decorator_list,
    #   expr? returns,
    #   string? type_comment)

    def do_FunctionDef(self, node):

        returns = getattr(node, 'returns', None)
        result = []
        # Decorators...
            # @{z}\n
        for z in node.decorator_list or []:
            result.extend([
                (self.op, '@'),
                (self.visit, z)
            ])
        # Signature...
            # def name(args): -> returns\n
            # def name(args):\n
        result.extend([
            (self.name, 'def'),
            (self.name, node.name),  # A string.
            (self.op, '('),
            (self.visit, node.args),
            (self.op, ')'),
        ])
        if returns is not None:
            result.extend([
                (self.op, '->'),
                (self.visit, node.returns),
            ])
        # Body...
        result.extend([
            (self.op, ':'),
            # (self.change_level, self.level + 1),
            (self.visit, node.body),
            # (self.change_level, self.level),
        ])
        return result
    #@+node:ekr.20220330133336.9: *5* iterative.Interactive
    def do_Interactive(self, node):  # pragma: no cover

        # self.visit(node.body)
        
        return [
            (self.visit, node.body),
        ]
    #@+node:ekr.20220330133336.10: *5* iterative.Lambda
    def do_Lambda(self, node):

        return [
            (self.name, 'lambda'),
            (self.visit, node.args),
            (self.op, ':'),
            (self.visit, node.body),
        ]

    #@+node:ekr.20220330133336.11: *5* iterative.Module
    def do_Module(self, node):
        
        # Encoding is a non-syncing statement.

        # self.visit(node.body)

        return [
            (self.visit, node.body),
        ]
    #@+node:ekr.20220330133336.12: *4* iterative: Expressions (TEST)
    #@+node:ekr.20220330133336.13: *5* iterative.Expr
    def do_Expr(self, node):
        """An outer expression."""
        # No need to put parentheses.
        
        # self.visit(node.value)

        return [
            (self.visit, node.value),
        ]
    #@+node:ekr.20220330133336.14: *5* iterative.Expression
    def do_Expression(self, node):  # pragma: no cover
        """An inner expression."""
        # No need to put parentheses.
        
        # self.visit(node.body)
        
        return [
            (self.visit, node.body),
        ]
    #@+node:ekr.20220330133336.15: *5* iterative.GeneratorExp
    def do_GeneratorExp(self, node):

        # '<gen %s for %s>' % (elt, ','.join(gens))
        # No need to put parentheses or commas.

        # self.visit(node.elt)
        # self.visit(node.generators)

        return [
            (self.visit, node.elt),
            (self.visit, node.generators),
        ]
    #@+node:ekr.20220330133336.16: *5* iterative.NamedExpr
    # NamedExpr(expr target, expr value)

    def do_NamedExpr(self, node):  # Python 3.8+

        return [
            (self.visit, node.target),
            (self.op, ':='),
            (self.visit, node.value),
        ]
    #@+node:ekr.20220330133336.40: *4* iterative: Operators
    #@+node:ekr.20220330133336.41: *5* iterative.BinOp
    def do_BinOp(self, node):

        return [
            (self.visit, node.left),
            (self.op, op_name(node.op)),
            (self.visit, node.right),
        ]

    #@+node:ekr.20220330133336.42: *5* iterative.BoolOp
    # BoolOp(boolop op, expr* values)

    def do_BoolOp(self, node):

        result = []
        op_name_ = op_name(node.op)
        for i, z in enumerate(node.values):
            result.append(self.visit(z))
            if i < len(node.values) - 1:
                result.append(self.name(op_name_))
        return result
    #@+node:ekr.20220330133336.43: *5* iterative.Compare
    # Compare(expr left, cmpop* ops, expr* comparators)

    def do_Compare(self, node):

        assert len(node.ops) == len(node.comparators)
        result = [self.visit(node.left)]
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
    #@+node:ekr.20220330133336.44: *5* iterative.UnaryOp
    def do_UnaryOp(self, node):

        op_name_ = op_name(node.op)
        if op_name_.isalpha():
            self.name(op_name_)
        else:
            self.op(op_name_)
        self.visit(node.operand)
    #@+node:ekr.20220330133336.45: *5* iterative.IfExp (ternary operator)
    # IfExp(expr test, expr body, expr orelse)

    def do_IfExp(self, node):

        #'%s if %s else %s'
        self.visit(node.body)
        self.name('if')
        self.visit(node.test)
        self.name('else')
        self.visit(node.orelse)
    #@+node:ekr.20220330133336.46: *4* iterative: Statements
    #@+node:ekr.20220330133336.47: *5*  iterative.Starred
    # Starred(expr value, expr_context ctx)

    def do_Starred(self, node):
        """A starred argument to an ast.Call"""
        self.op('*')
        self.visit(node.value)
    #@+node:ekr.20220330133336.48: *5* iterative.AnnAssign
    # AnnAssign(expr target, expr annotation, expr? value, int simple)

    def do_AnnAssign(self, node):

        # {node.target}:{node.annotation}={node.value}\n'
        self.visit(node.target)
        self.op(':')
        self.visit(node.annotation)
        if node.value is not None:  # #1851
            self.op('=')
            self.visit(node.value)
    #@+node:ekr.20220330133336.49: *5* iterative.Assert
    # Assert(expr test, expr? msg)

    def do_Assert(self, node):

        # Guards...
        msg = getattr(node, 'msg', None)
        # No need to put parentheses or commas.
        self.name('assert')
        self.visit(node.test)
        if msg is not None:
            self.visit(node.msg)
    #@+node:ekr.20220330133336.50: *5* iterative.Assign
    def do_Assign(self, node):

        for z in node.targets:
            self.visit(z)
            self.op('=')
        self.visit(node.value)
    #@+node:ekr.20220330133336.51: *5* iterative.AsyncFor
    def do_AsyncFor(self, node):

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
    #@+node:ekr.20220330133336.52: *5* iterative.AsyncWith
    def do_AsyncWith(self, node):

        async_token_type = 'async' if has_async_tokens else 'name'
        self.token(async_token_type, 'async')
        self.do_With(node)
    #@+node:ekr.20220330133336.53: *5* iterative.AugAssign
    # AugAssign(expr target, operator op, expr value)

    def do_AugAssign(self, node):

        # %s%s=%s\n'
        op_name_ = op_name(node.op)
        self.visit(node.target)
        self.op(op_name_ + '=')
        self.visit(node.value)
    #@+node:ekr.20220330133336.54: *5* iterative.Await
    # Await(expr value)

    def do_Await(self, node):

        #'await %s\n'
        async_token_type = 'await' if has_async_tokens else 'name'
        self.token(async_token_type, 'await')
        self.visit(node.value)
    #@+node:ekr.20220330133336.55: *5* iterative.Break
    def do_Break(self, node):

        self.name('break')
    #@+node:ekr.20220330133336.56: *5* iterative.Call & helpers
    # Call(expr func, expr* args, keyword* keywords)

    # Python 3 ast.Call nodes do not have 'starargs' or 'kwargs' fields.

    def do_Call(self, node):

        # The calls to op(')') and op('(') do nothing by default.
        # Subclasses might handle them in an overridden iterative.set_links.
        self.visit(node.func)
        self.op('(')
        # No need to generate any commas.
        self.handle_call_arguments(node)
        self.op(')')
    #@+node:ekr.20220330133336.57: *6* iterative.arg_helper
    def arg_helper(self, node):
        """
        Yield the node, with a special case for strings.
        """
        if isinstance(node, str):
            self.token('name', node)
        else:
            self.visit(node)
    #@+node:ekr.20220330133336.58: *6* iterative.handle_call_arguments
    def handle_call_arguments(self, node):
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

        def get_pos(obj):
            line1 = getattr(obj, 'lineno', None)
            col1 = getattr(obj, 'col_offset', None)
            return line1, col1, obj

        def sort_key(aTuple):
            line, col, obj = aTuple
            return line * 1000 + col

        if 0:
            g.printObj([ast.dump(z) for z in args], tag='args')
            g.printObj([ast.dump(z) for z in keywords], tag='keywords')

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
                        self.op('=')
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
    #@+node:ekr.20220330133336.59: *5* iterative.Continue
    def do_Continue(self, node):

        self.name('continue')
    #@+node:ekr.20220330133336.60: *5* iterative.Delete
    def do_Delete(self, node):

        # No need to put commas.
        self.name('del')
        self.visit(node.targets)
    #@+node:ekr.20220330133336.61: *5* iterative.ExceptHandler
    def do_ExceptHandler(self, node):

        # Except line...
        self.name('except')
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
    #@+node:ekr.20220330133336.62: *5* iterative.For
    def do_For(self, node):

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
    #@+node:ekr.20220330133336.63: *5* iterative.Global
    # Global(identifier* names)

    def do_Global(self, node):

        self.name('global')
        for z in node.names:
            self.name(z)
    #@+node:ekr.20220330133336.64: *5* iterative.If & helpers
    # If(expr test, stmt* body, stmt* orelse)

    def do_If(self, node):
        #@+<< do_If docstring >>
        #@+node:ekr.20220330133336.65: *6* << do_If docstring >>
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
    #@+node:ekr.20220330133336.66: *5* iterative.Import & helper
    def do_Import(self, node):

        self.name('import')
        for alias in node.names:
            self.name(alias.name)
            if alias.asname:
                self.name('as')
                self.name(alias.asname)
    #@+node:ekr.20220330133336.67: *5* iterative.ImportFrom
    # ImportFrom(identifier? module, alias* names, int? level)

    def do_ImportFrom(self, node):

        self.name('from')
        for i in range(node.level):
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
    #@+node:ekr.20220330133336.68: *5* iterative.Match* (Python 3.10+)
    # Match(expr subject, match_case* cases)

    # match_case = (pattern pattern, expr? guard, stmt* body)

    def do_Match(self, node):

        cases = getattr(node, 'cases', [])
        self.name('match')
        self.visit(node.subject)
        self.op(':')
        for case in cases:
            self.visit(case)
    #@+node:ekr.20220330133336.69: *6* iterative.match_case
    #  match_case = (pattern pattern, expr? guard, stmt* body)

    def do_match_case(self, node):

        g.trace(g.callers())
        guard = getattr(node, 'guard', None)
        body = getattr(node, 'body', [])
        self.name('case')
        self.visit(node.pattern)
        if guard:
            self.visit(guard)
        self.op(':')
        for statement in body:
            self.visit(statement)
    #@+node:ekr.20220330133336.70: *6* iterative.MatchAs (test)
    # MatchAs(pattern? pattern, identifier? name)

    def do_MatchAs(self, node):
        pattern = getattr(node, 'pattern', None)
        name = getattr(node, 'name', None)
        g.trace(pattern, name)
        if pattern:
            self.visit(pattern)
        if name:
            self.name(name)

        
    #@+node:ekr.20220330133336.71: *6* iterative.MatchClass (*** to do)
    # MatchClass(expr cls, pattern* patterns, identifier* kwd_attrs, pattern* kwd_patterns)

    def do_MatchClass(self, node):

        cls = node.cls
        patterns = getattr(node, 'patterns', [])
        kwd_attrs = getattr(node, 'kwd_attrs', [])
        kwd_patterns = getattr(node, 'kwd_patterns', [])
        g.trace(node, cls, patterns, kwd_attrs, kwd_patterns)
        ### To do ###
    #@+node:ekr.20220330133336.72: *6* iterative.MatchMapping (*** to do)
    # MatchMapping(expr* keys, pattern* patterns, identifier? rest)

    def do_MatchMapping(self, node):

        keys = getattr(node, 'keys', [])
        patterns = getattr(node, 'patterns', [])
        rest = getattr(node, 'rest', None)
        g.trace(node, keys, patterns, rest)
        ### To do ###
    #@+node:ekr.20220330133336.73: *6* iterative.MatchOr (test)
    # MatchOr(pattern* patterns)

    def do_MatchOr(self, node):
        patterns = getattr(node, 'patterns', [])
        g.trace(node, patterns)
        for pattern in patterns:
            self.visit(pattern)


    #@+node:ekr.20220330133336.74: *6* iterative.MatchSequence (test)
    # MatchSequence(pattern* patterns)

    def do_MatchSequence(self, node):
        patterns = getattr(node, 'patterns', [])
        g.trace(node, patterns)
        for pattern in patterns:
            self.visit(pattern)

    #@+node:ekr.20220330133336.75: *6* iterative.MatchSingleton (test)
    # MatchSingleton(constant value)

    def do_MatchSingleton(self, node):
        g.trace(node, node.value)
        self.visit(node.value)
    #@+node:ekr.20220330133336.76: *6* iterative.MatchStar (test)
    # MatchStar(identifier? name)

    def do_MatchStar(self, node):
        name = getattr(node, 'name', None)
        g.trace(node, repr(name))
        if name:
            self.name(name)
    #@+node:ekr.20220330133336.77: *6* iterative.MatchValue
    # MatchValue(expr value)

    def do_MatchValue(self, node):

        self.visit(node.value)
    #@+node:ekr.20220330133336.78: *5* iterative.Nonlocal
    # Nonlocal(identifier* names)

    def do_Nonlocal(self, node):

        # nonlocal %s\n' % ','.join(node.names))
        # No need to put commas.
        self.name('nonlocal')
        for z in node.names:
            self.name(z)
    #@+node:ekr.20220330133336.79: *5* iterative.Pass
    def do_Pass(self, node):

        return ([
            (self.name, 'pass'),
        ])
    #@+node:ekr.20220330133336.80: *5* iterative.Raise
    # Raise(expr? exc, expr? cause)

    def do_Raise(self, node):

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
    #@+node:ekr.20220330133336.81: *5* iterative.Return
    def do_Return(self, node):

        self.name('return')
        self.visit(node.value)
    #@+node:ekr.20220330133336.82: *5* iterative.Try
    # Try(stmt* body, excepthandler* handlers, stmt* orelse, stmt* finalbody)

    def do_Try(self, node):

        # Try line...
        self.name('try')
        self.op(':')
        # Body...
        self.level += 1
        self.visit(node.body)
        self.visit(node.handlers)
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
    #@+node:ekr.20220330133336.83: *5* iterative.While
    def do_While(self, node):

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
    #@+node:ekr.20220330133336.84: *5* iterative.With
    # With(withitem* items, stmt* body)

    # withitem = (expr context_expr, expr? optional_vars)

    def do_With(self, node):

        expr: Optional[ast.AST] = getattr(node, 'context_expression', None)
        items: List[ast.AST] = getattr(node, 'items', [])
        self.name('with')
        self.visit(expr)
        # No need to put commas.
        for item in items:
            self.visit(item.context_expr)  # type:ignore
            optional_vars = getattr(item, 'optional_vars', None)
            if optional_vars is not None:
                self.name('as')
                self.visit(item.optional_vars)  # type:ignore
        # End the line.
        self.op(':')
        # Body...
        self.level += 1
        self.visit(node.body)
        self.level -= 1
    #@+node:ekr.20220330133336.85: *5* iterative.Yield
    def do_Yield(self, node):

        result = [
            (self.name, 'yield'),
        ]
        if hasattr(node, 'value'):
            result.extend([
                (self.visit, node.value),
            ])
        return result
    #@+node:ekr.20220330133336.86: *5* iterative.YieldFrom
    # YieldFrom(expr value)

    def do_YieldFrom(self, node):

        return ([
            (self.name, 'yield'),
            (self.name, 'from'),
            (self.visit, node.value),
        ])
    #@-others
#@-others
g = LeoGlobals()
if __name__ == '__main__':
    main()  # pragma: no cover
#@-leo
