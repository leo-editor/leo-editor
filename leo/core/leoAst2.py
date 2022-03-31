# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20220330191842.1: * @file leoAst2.py
#@@first
# This file is part of Leo: https://leoeditor.com
# Leo's copyright notice is based on the MIT license: http://leoeditor.com/license.html
#@+<< imports >>
#@+node:ekr.20220330191903.1: ** << imports >> (leoAst2.py)
import ast
from leo.core import leoGlobals as g

# import argparse
# import ast
# import codecs
# import difflib
# import glob
# import io
# import os
# import re
# import sys
# import textwrap
# import tokenize
# import traceback
# from typing import List, Optional
#@-<< imports >>
#@+others
#@+node:ekr.20220330191947.1: ** class IterativeTokenSync
class IterativeTokenSync:
    """
    Experimental iterative token syncing class.
    """
    
    #@+others
    #@+node:ekr.20220330164313.1: *3* iterative: Traversal...
    #@+node:ekr.20220330164313.4: *4* iterative.find_next_significant_token
    def find_next_significant_token(self):
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
    #@+node:ekr.20220330164313.8: *4* iterative.name & op
    # It's valid for these to return None.

    def name(self, val):  # was sync_name
        aList = val.split('.')
        if len(aList) == 1:
            self.sync_token('name', val)
        else:
            for i, part in enumerate(aList):
                self.sync_token('name', part)
                if i < len(aList) - 1:
                    self.sync_op('.')

    def op(self, val):  # was sync_op
        """
        Sync to the given operator.

        val may be '(' or ')' *only* if the parens *will* actually exist in the
        token list.
        """
        self.sync_token('op', val)
    #@+node:ekr.20220330164313.6: *4* iterative.token & set_links
    px = -1  # Index of the previously synced token.

    def token(self, data):  # Was sync_token.
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
        kind, val = data
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
    #@+node:ekr.20220330164313.7: *5* iterative.set_links
    last_statement_node = None

    def set_links(self, node, token):
        """Make two-way links between token and the given node."""
        # Don't bother assigning comment, comma, parens, ws and endtoken tokens.
        if token.kind == 'comment':
            # Append the comment to node.comment_list.
            comment_list = getattr(node, 'comment_list', [])  # type:ignore
            node.comment_list = comment_list + [token]
            return
        if token.kind in ('endmarker', 'ws'):
            return
        if token.kind == 'op' and token.value in ',()':
            return
        # *Always* remember the last statement.
        statement = find_statement_node(node)
        if statement:
            self.last_statement_node = statement  # type:ignore
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
            token.node = node  # type:ignore
            # Add the token to node's token_list.
            add_token_to_token_list(token, node)
    #@+node:ekr.20220330155314.1: *4* iterative.visit
    def visit(self, node):
        """Visit an ast node."""
        trace = False
        # This saves a lot of tests.
        if node is None:
            return
        if trace:  # pragma: no cover
            # Keep this trace. It's useful.
            cn = node.__class__.__name__ if node else ' '
            caller1, caller2 = g.callers(2).split(',')
            g.trace(f"{caller1:>15} {caller2:<14} {cn}")
        # More general, more convenient.
        if isinstance(node, (list, tuple)):
            result = []
            for z in node: ### or []:
                if isinstance(z, ast.AST):
                    ### yield from self.visitor(z)
                    result.append((self.visit, z)) ##### Test.
                else:
                    # Some fields may contain ints or strings.
                    assert isinstance(z, (int, str)), z.__class__.__name__
            if result:
                stack[:0] = result
            return
        # We *do* want to crash if the visitor doesn't exist.
        assert isinstance(node, ast.AST), repr(node)
        method = getattr(self, 'do_' + node.__class__.__name__)
        # Save the old node, enter the new node.
        self.node_stack.append(self.node)
        self.node = node
        # Visit the node.
        result = method(node)
        # Restore the old node.
        self.node = self.node_stack.pop()
        return result
    #@+node:ekr.20220330120220.1: *4* iterative: main loop
    def main_loop(self, node):

        func = getattr(self, 'do_' + tree.__class__.__name__, None)
        if not func:
            print('main_loop: invalid ast node:', repr(node))
            return
        
        # Make exec_list an ivar for debugging.
        self.exec_list = [(func, node)]
        while self.exec_list:
            func, arg = self.exec_list.pop(0)
            result = func(arg)
            if result:
                # Prepend the result, a list of tuples.
                assert isinstance(result, list), repr(result)
                stack[:0] = result
    #@+node:ekr.20220330133336.1: *3* iterative: Visitors
    #@+node:ekr.20220330133336.2: *4*  iterative.keyword: not called!
    # keyword arguments supplied to call (NULL identifier for **kwargs)

    # keyword = (identifier? arg, expr value)

    def do_keyword(self, node):  # pragma: no cover
        """A keyword arg in an ast.Call."""
        # This should never be called.
        # iterative.hande_call_arguments calls self.gen(kwarg_arg.value) instead.
        filename = getattr(self, 'filename', '<no file>')
        raise AssignLinksError(
            f"file: {filename}\n"
            f"do_keyword should never be called\n"
            f"{g.callers(8)}")
    #@+node:ekr.20220330133336.3: *4* iterative: Contexts (TEST)
    #@+node:ekr.20220330133336.4: *5*  iterative.arg
    # arg = (identifier arg, expr? annotation)

    def do_arg(node):
        """This is one argument of a list of ast.Function or ast.Lambda arguments."""
        
        # annotation = getattr(node, 'annotation', None)
        # yield from self.gen_name(node.arg)
        # if annotation is not None:
            # yield from self.gen_op(':')
            # yield from self.gen(node.annotation)

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
        posonlyargs = getattr(node, 'posonlyargs', [])  # type:ignore
        vararg = getattr(node, 'vararg', None)
        kwonlyargs = getattr(node, 'kwonlyargs', [])  # type:ignore
        kw_defaults = getattr(node, 'kw_defaults', [])  # type:ignore
        kwarg = getattr(node, 'kwarg', None)
        if 0:
            g.printObj(ast.dump(node.vararg) if node.vararg else 'None', tag='node.vararg')
            g.printObj([ast.dump(z) for z in node.args], tag='node.args')
            g.printObj([ast.dump(z) for z in node.defaults], tag='node.defaults')
            g.printObj([ast.dump(z) for z in posonlyargs], tag='node.posonlyargs')
            g.printObj([ast.dump(z) for z in kwonlyargs], tag='kwonlyargs')
            g.printObj([ast.dump(z) if z else 'None' for z in kw_defaults], tag='kw_defaults')
            
        ###
            # # 1. Sync the position-only args.
            # if posonlyargs:
                # for n, z in enumerate(posonlyargs):
                    # # g.trace('pos-only', ast.dump(z))
                    # yield from self.gen(z)
                # yield from self.gen_op('/')
            # # 2. Sync all args.
            # for i, z in enumerate(node.args):
                # yield from self.gen(z)
                # if i >= n_plain:
                    # yield from self.gen_op('=')
                    # yield from self.gen(node.defaults[i - n_plain])
            # # 3. Sync the vararg.
            # if vararg:
                # # g.trace('vararg', ast.dump(vararg))
                # yield from self.gen_op('*')
                # yield from self.gen(vararg)
            # # 4. Sync the keyword-only args.
            # if kwonlyargs:
                # if not vararg:
                    # yield from self.gen_op('*')
                # for n, z in enumerate(kwonlyargs):
                    # # g.trace('keyword-only', ast.dump(z))
                    # yield from self.gen(z)
                    # val = kw_defaults[n]
                    # if val is not None:
                        # yield from self.gen_op('=')
                        # yield from self.gen(val)
            # # 5. Sync the kwarg.
            # if kwarg:
                # # g.trace('kwarg', ast.dump(kwarg))
                # yield from self.gen_op('**')
                # yield from self.gen(kwarg)
                
        result = []
        # 1. Sync the position-only args.
        if posonlyargs:
            for n, z in enumerate(posonlyargs):
                # yield from self.gen(z)
                result.append((self.visit, z))
            # yield from self.gen_op('/')
            result.append(self.op, '/')
        # 2. Sync all args.
        for i, z in enumerate(node.args):
            # yield from self.gen(z)
            result.append(self.visit, z)
            if i >= n_plain:
                # yield from self.gen_op('=')
                # yield from self.gen(node.defaults[i - n_plain])
                result.extend([
                    (self.op, '='),
                    (self.visit, node.defaults[i - n_plain]),
                ])
        # 3. Sync the vararg.
        if vararg:
            # g.trace('vararg', ast.dump(vararg))
            # yield from self.gen_op('*')
            # yield from self.gen(vararg)
            result.extend([
                (self.op, '*'),
                (self.visit, vararg),
            ])
        # 4. Sync the keyword-only args.
        if kwonlyargs:
            if not vararg:
                # yield from self.gen_op('*')
                result.append((self.op, '*'))
            for n, z in enumerate(kwonlyargs):
                # g.trace('keyword-only', ast.dump(z))
                # yield from self.gen(z)
                result.append((self.visit, z))
                val = kw_defaults[n]
                if val is not None:
                    # yield from self.gen_op('=')
                    # yield from self.gen(val)
                    result.extend([
                        (self.op, '='),
                        (self.visit, val),
                    ])
        # 5. Sync the kwarg.
        if kwarg:
            # g.trace('kwarg', ast.dump(kwarg))
            # yield from self.gen_op('**')
            # yield from self.gen(kwarg)
            result.append([
                (self.op, '**'),
                (self.visit, kwarg),
            ])
        return result



    #@+node:ekr.20220330133336.6: *5* iterative.AsyncFunctionDef
    # AsyncFunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list,
    #                expr? returns)

    def do_AsyncFunctionDef(self, node):

        # if node.decorator_list:
            # for z in node.decorator_list:
                # # '@%s\n'
                # yield from self.gen_op('@')
                # yield from self.gen(z)
        # # 'asynch def (%s): -> %s\n'
        # # 'asynch def %s(%s):\n'
        # async_token_type = 'async' if has_async_tokens else 'name'
        # yield from self.gen_token(async_token_type, 'async')
        # yield from self.gen_name('def')
        # yield from self.gen_name(node.name)  # A string
        # yield from self.gen_op('(')
        # yield from self.gen(node.args)
        # yield from self.gen_op(')')
        # returns = getattr(node, 'returns', None)
        # if returns is not None:
            # yield from self.gen_op('->')
            # yield from self.gen(node.returns)
        # yield from self.gen_op(':')
        # self.level += 1
        # yield from self.gen(node.body)
        # self.level -= 1
        
        # Guards...
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
            (self,token, 'async'),  ###### test.
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

        # for z in node.decorator_list or []:
            # # @{z}\n
            # yield from self.gen_op('@')
            # yield from self.gen(z)
        # # class name(bases):\n
        # yield from self.gen_name('class')
        # yield from self.gen_name(node.name)  # A string.
        # if node.bases:
            # yield from self.gen_op('(')
            # yield from self.gen(node.bases)
            # yield from self.gen_op(')')
        # yield from self.gen_op(':')
        # # Body...
        # self.level += 1
        # yield from self.gen(node.body)
        # self.level -= 1
        
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

        # # Guards...
        # returns = getattr(node, 'returns', None)
        # # Decorators...
            # # @{z}\n
        # for z in node.decorator_list or []:
            # yield from self.gen_op('@')
            # yield from self.gen(z)
        # # Signature...
            # # def name(args): -> returns\n
            # # def name(args):\n
        # yield from self.gen_name('def')
        # yield from self.gen_name(node.name)  # A string.
        # yield from self.gen_op('(')
        # yield from self.gen(node.args)
        # yield from self.gen_op(')')
        # if returns is not None:
            # yield from self.gen_op('->')
            # yield from self.gen(node.returns)
        # yield from self.gen_op(':')
        # # Body...
        # self.level += 1
        # yield from self.gen(node.body)
        # self.level -= 1
        
        # Guards...
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

        # yield from self.gen(node.body)
        
        return [
            (self.visit, node.body),
        ]
    #@+node:ekr.20220330133336.10: *5* iterative.Lambda
    def do_Lambda(self, node):

        # yield from self.gen_name('lambda')
        # yield from self.gen(node.args)
        # yield from self.gen_op(':')
        # yield from self.gen(node.body)
        
        return [
            (self.name, 'lambda'),
            (self.visit, node.args),
            (self.op, ':'),
            (self.visit, node.body),
        ]

    #@+node:ekr.20220330133336.11: *5* iterative.Module
    def do_Module(self, node):
        
        # Encoding is a non-syncing statement.

        # yield from self.gen(node.body)

        return [
            (self.visit, node.body),
        ]
    #@+node:ekr.20220330133336.12: *4* iterative: Expressions (TEST)
    #@+node:ekr.20220330133336.13: *5* iterative.Expr
    def do_Expr(self, node):
        """An outer expression."""
        # No need to put parentheses.
        
        # yield from self.gen(node.value)

        return [
            (self.visit, node.value),
        ]
    #@+node:ekr.20220330133336.14: *5* iterative.Expression
    def do_Expression(self, node):  # pragma: no cover
        """An inner expression."""
        # No need to put parentheses.
        
        # yield from self.gen(node.body)
        
        return [
            (self.visit, node.body),
        ]
    #@+node:ekr.20220330133336.15: *5* iterative.GeneratorExp
    def do_GeneratorExp(self, node):

        # '<gen %s for %s>' % (elt, ','.join(gens))
        # No need to put parentheses or commas.

        # yield from self.gen(node.elt)
        # yield from self.gen(node.generators)

        return [
            (self.visit, node.elt),
            (self.visit, node.generators),
        ]
    #@+node:ekr.20220330133336.16: *5* iterative.NamedExpr
    # NamedExpr(expr target, expr value)

    def do_NamedExpr(self, node):  # Python 3.8+

        # yield from self.gen(node.target)
        # yield from self.gen_op(':=')
        # yield from self.gen(node.value)

        return [
            (self.visit, node.target),
            (self.op, ':='),
            (self.visit, node.value),
        ]
    #@+node:ekr.20220330133336.17: *4* iterative: Operands
    #@+node:ekr.20220330133336.18: *5* iterative.Attribute
    # Attribute(expr value, identifier attr, expr_context ctx)

    def do_Attribute(self, node):

        # yield from self.gen(node.value)
        # yield from self.gen_op('.')
        # yield from self.gen_name(node.attr)  # A string.
        
        return [
            (self.visit, node.value),
            (self.op, '.'),
            (self.name, node.attr),  # A string.
        ]
    #@+node:ekr.20220330133336.19: *5* iterative.Bytes
    def do_Bytes(self, node):

        """
        It's invalid to mix bytes and non-bytes literals, so just
        advancing to the next 'string' token suffices.
        """
        token = self.find_next_significant_token()
        # yield from self.gen_token('string', token.value)
        
        return [
            (self.token, ('string', token.value)),
        ]
    #@+node:ekr.20220330133336.20: *5* iterative.comprehension
    # comprehension = (expr target, expr iter, expr* ifs, int is_async)

    def do_comprehension(self, node):

        # No need to put parentheses.
        # yield from self.gen_name('for')  # #1858.
        # yield from self.gen(node.target)  # A name
        # yield from self.gen_name('in')
        # yield from self.gen(node.iter)
        # for z in node.ifs or []:
            # yield from self.gen_name('if')
            # yield from self.gen(z)
            
        result = [
            (self.name, 'for'),
            (self.visit, node.target),  # A name
            (self.name, 'in'),
            (self.visit, node.iter),
        ]
        for z in node.ifs or []:
            result.extend([
                (self.name, 'if'),
                (self.visit, z),
            ])
        return result
    #@+node:ekr.20220330133336.21: *5* iterative.Constant
    def do_Constant(self, node):  # pragma: no cover
        """

        https://greentreesnakes.readthedocs.io/en/latest/nodes.html

        A constant. The value attribute holds the Python object it represents.
        This can be simple types such as a number, string or None, but also
        immutable container types (tuples and frozensets) if all of their
        elements are constant.
        """

        # # Support Python 3.8.
        # if node.value is None or isinstance(node.value, bool):
            # # Weird: return a name!
            # yield from self.gen_token('name', repr(node.value))
        # elif node.value == Ellipsis:
            # yield from self.gen_op('...')
        # elif isinstance(node.value, str):
            # yield from self.do_Str(node)
        # elif isinstance(node.value, (int, float)):
            # yield from self.gen_token('number', repr(node.value))
        # elif isinstance(node.value, bytes):
            # yield from self.do_Bytes(node)
        # elif isinstance(node.value, tuple):
            # yield from self.do_Tuple(node)
        # elif isinstance(node.value, frozenset):
            # yield from self.do_Set(node)
        # else:
            # # Unknown type.
            # g.trace('----- Oops -----', repr(node.value), g.callers())
            
        # Support Python 3.8.
        if node.value is None or isinstance(node.value, bool):
            # Weird: return a name!
            return [
                (self.token, ('name', repr(node.value))),
            ]
        if node.value == Ellipsis:
            return [
                (self.op, '...'),
            ]
        if isinstance(node.value, str):
            return self.do_Str(node)
        if isinstance(node.value, (int, float)):
            return [
                (self.token, ('number', repr(node.value))),
            ]
        if isinstance(node.value, bytes):
            return self.do_Bytes(node)
        if isinstance(node.value, tuple):
            return self.do_Tuple(node)
        if isinstance(node.value, frozenset):
            return self.do_Set(node)
        g.trace('----- Oops -----', repr(node.value), g.callers())

    #@+node:ekr.20220330133336.22: *5* iterative.Dict
    # Dict(expr* keys, expr* values)

    def do_Dict(self, node):

        assert len(node.keys) == len(node.values)
        yield from self.gen_op('{')
        # No need to put commas.
        for i, key in enumerate(node.keys):
            key, value = node.keys[i], node.values[i]
            yield from self.gen(key)  # a Str node.
            yield from self.gen_op(':')
            if value is not None:
                yield from self.gen(value)
        yield from self.gen_op('}')
    #@+node:ekr.20220330133336.23: *5* iterative.DictComp
    # DictComp(expr key, expr value, comprehension* generators)

    # d2 = {val: key for key, val in d}

    def do_DictComp(self, node):

        # yield from self.gen_token('op', '{')
        # yield from self.gen(node.key)
        # yield from self.gen_op(':')
        # yield from self.gen(node.value)
        # for z in node.generators or []:
            # yield from self.gen(z)
            # yield from self.gen_token('op', '}')
            
        result = [
            (self.token, ('op', '{')),
            (self.visit, node.key),
            (self.op, ':'),
            (self.visit, node.value),
        ]
        for z in node.generators or []:
            result.extend([
                (self.visit, z),
                (self.token, ('op', '}')),
            ])
        return result

    #@+node:ekr.20220330133336.24: *5* iterative.Ellipsis
    def do_Ellipsis(self, node):  # pragma: no cover (Does not exist for python 3.8+)

        # yield from self.gen_op('...')
        
        return [
            (self.op, '...'),
        ]
    #@+node:ekr.20220330133336.25: *5* iterative.ExtSlice
    # https://docs.python.org/3/reference/expressions.html#slicings

    # ExtSlice(slice* dims)

    def do_ExtSlice(self, node):  # pragma: no cover (deprecated)

        # ','.join(node.dims)
        # for i, z in enumerate(node.dims):
            # yield from self.gen(z)
            # if i < len(node.dims) - 1:
                # yield from self.gen_op(',')
        
        result = []
        for i, z in enumerate(node.dims):
            # yield from self.gen(z)
            result.append((self.visit, z))
            if i < len(node.dims) - 1:
                # yield from self.gen_op(',')
                result.append(self.op, ',')
        return result
    #@+node:ekr.20220330133336.26: *5* iterative.Index
    def do_Index(self, node):  # pragma: no cover (deprecated)

        # yield from self.gen(node.value)
        
        return [
            (self.visit, node.value),
        ]
    #@+node:ekr.20220330133336.27: *5* iterative.FormattedValue: not called!
    # FormattedValue(expr value, int? conversion, expr? format_spec)

    def do_FormattedValue(self, node):  # pragma: no cover
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
            # yield from self.gen(node.value)
            # if conv is not None:
                # yield from self.gen_token('number', conv)
            # if spec is not None:
                # yield from self.gen(node.format_spec)
    #@+node:ekr.20220330133336.28: *5* iterative.JoinedStr & helpers
    # JoinedStr(expr* values)

    def do_JoinedStr(self, node):
        """
        JoinedStr nodes represent at least one f-string and all other strings
        concatentated to it.

        Analyzing JoinedStr.values would be extremely tricky, for reasons that
        need not be explained here.

        Instead, we get the tokens *from the token list itself*!
        """
        # for z in self.get_concatenated_string_tokens():
            # yield from self.gen_token(z.kind, z.value)
            
        return [
            (self.token, (z.kind, z.value))
                for z in self.get_concatenated_string_tokens()
        ]
    #@+node:ekr.20220330133336.29: *5* iterative.List
    def do_List(self, node):

        # No need to put commas.
        
        # yield from self.gen_op('[')
        # yield from self.gen(node.elts)
        # yield from self.gen_op(']')
        
        return [
            (self.op, '['),
            (self.visit, node.elts),
            (self.op, ']'),
        ]
    #@+node:ekr.20220330133336.30: *5* iterative.ListComp
    # ListComp(expr elt, comprehension* generators)

    def do_ListComp(self, node):

        # yield from self.gen_op('[')
        # yield from self.gen(node.elt)
        # for z in node.generators:
            # yield from self.gen(z)
        # yield from self.gen_op(']')
        
        result = [
            (self.op, '['),
            (self.visit, node.elt),
        ]
        for z in node.generators:
            result.append((self.visit, z))
        result.append((self.op, ']'))
        return result
    #@+node:ekr.20220330133336.31: *5* iterative.Name & NameConstant
    def do_Name(self, node):

        # yield from self.gen_name(node.id)

        return [
            (self.name, node.id),
        ]

    def do_NameConstant(self, node):  # pragma: no cover (Does not exist in Python 3.8+)

        # yield from self.gen_name(repr(node.value))
        
        return [
            (self.name, repr(node.value)),
        ]

    #@+node:ekr.20220330133336.32: *5* iterative.Num
    def do_Num(self, node):  # pragma: no cover (Does not exist in Python 3.8+)

        # yield from self.gen_token('number', node.n)
        
        return [
            (self.token, ('number', node.n)),
        ]
    #@+node:ekr.20220330133336.33: *5* iterative.Set
    # Set(expr* elts)

    def do_Set(self, node):

        # yield from self.gen_op('{')
        # yield from self.gen(node.elts)
        # yield from self.gen_op('}')
        
        return [
            (self.op, '{'),
            (self.visit, node.elts),
            (self.op, '}'),
        ]
    #@+node:ekr.20220330133336.34: *5* iterative.SetComp
    # SetComp(expr elt, comprehension* generators)

    def do_SetComp(self, node):

        yield from self.gen_op('{')
        yield from self.gen(node.elt)
        for z in node.generators or []:
            yield from self.gen(z)
        yield from self.gen_op('}')
    #@+node:ekr.20220330133336.35: *5* iterative.Slice
    # slice = Slice(expr? lower, expr? upper, expr? step)

    def do_Slice(self, node):

        lower = getattr(node, 'lower', None)
        upper = getattr(node, 'upper', None)
        step = getattr(node, 'step', None)
        if lower is not None:
            yield from self.gen(lower)
        # Always put the colon between upper and lower.
        yield from self.gen_op(':')
        if upper is not None:
            yield from self.gen(upper)
        # Put the second colon if it exists in the token list.
        if step is None:
            token = self.find_next_significant_token()
            if token and token.value == ':':
                yield from self.gen_op(':')
        else:
            yield from self.gen_op(':')
            yield from self.gen(step)
    #@+node:ekr.20220330133336.36: *5* iterative.Str & helper
    def do_Str(self, node):
        """This node represents a string constant."""
        # This loop is necessary to handle string concatenation.
        
        # for z in self.get_concatenated_string_tokens():
            # yield from self.gen_token(z.kind, z.value)
        
        return [
            (self.token, (z.kind, z.value))
                for z in self.get_concatenated_string_tokens()
        ]
            
    #@+node:ekr.20220330133336.37: *6* iterative.get_concatenated_tokens
    def get_concatenated_string_tokens(self):
        """
        Return the next 'string' token and all 'string' tokens concatenated to
        it. *Never* update self.px here.
        """
        trace = False
        tag = 'iterative.get_concatenated_string_tokens'
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
            g.printObj(results, tag=f"{tag}: Results")
        return results
    #@+node:ekr.20220330133336.38: *5* iterative.Subscript
    # Subscript(expr value, slice slice, expr_context ctx)

    def do_Subscript(self, node):

        # yield from self.gen(node.value)
        # yield from self.gen_op('[')
        # yield from self.gen(node.slice)
        # yield from self.gen_op(']')
        
        return [
            (self.visit, node.value),
            (self.op, '['),
            (self.visit, node.slice),
            (self.op, ']'),
        ]
    #@+node:ekr.20220330133336.39: *5* iterative.Tuple
    # Tuple(expr* elts, expr_context ctx)

    def do_Tuple(self, node):

        # Do not call gen_op for parens or commas here.
        # They do not necessarily exist in the token list!
        
        # yield from self.gen(node.elts)
        
        return [
            (self.visit, node.elts),
        ]
    #@+node:ekr.20220330133336.40: *4* iterative: Operators
    #@+node:ekr.20220330133336.41: *5* iterative.BinOp
    def do_BinOp(self, node):

        op_name_ = op_name(node.op)
        yield from self.gen(node.left)
        yield from self.gen_op(op_name_)
        yield from self.gen(node.right)
    #@+node:ekr.20220330133336.42: *5* iterative.BoolOp
    # BoolOp(boolop op, expr* values)

    def do_BoolOp(self, node):

        # op.join(node.values)
        op_name_ = op_name(node.op)
        for i, z in enumerate(node.values):
            yield from self.gen(z)
            if i < len(node.values) - 1:
                yield from self.gen_name(op_name_)
    #@+node:ekr.20220330133336.43: *5* iterative.Compare
    # Compare(expr left, cmpop* ops, expr* comparators)

    def do_Compare(self, node):

        assert len(node.ops) == len(node.comparators)
        yield from self.gen(node.left)
        for i, z in enumerate(node.ops):
            op_name_ = op_name(node.ops[i])
            if op_name_ in ('not in', 'is not'):
                for z in op_name_.split(' '):
                    yield from self.gen_name(z)
            elif op_name_.isalpha():
                yield from self.gen_name(op_name_)
            else:
                yield from self.gen_op(op_name_)
            yield from self.gen(node.comparators[i])
    #@+node:ekr.20220330133336.44: *5* iterative.UnaryOp
    def do_UnaryOp(self, node):

        op_name_ = op_name(node.op)
        if op_name_.isalpha():
            yield from self.gen_name(op_name_)
        else:
            yield from self.gen_op(op_name_)
        yield from self.gen(node.operand)
    #@+node:ekr.20220330133336.45: *5* iterative.IfExp (ternary operator)
    # IfExp(expr test, expr body, expr orelse)

    def do_IfExp(self, node):

        #'%s if %s else %s'
        yield from self.gen(node.body)
        yield from self.gen_name('if')
        yield from self.gen(node.test)
        yield from self.gen_name('else')
        yield from self.gen(node.orelse)
    #@+node:ekr.20220330133336.46: *4* iterative: Statements
    #@+node:ekr.20220330133336.47: *5*  iterative.Starred
    # Starred(expr value, expr_context ctx)

    def do_Starred(self, node):
        """A starred argument to an ast.Call"""
        yield from self.gen_op('*')
        yield from self.gen(node.value)
    #@+node:ekr.20220330133336.48: *5* iterative.AnnAssign
    # AnnAssign(expr target, expr annotation, expr? value, int simple)

    def do_AnnAssign(self, node):

        # {node.target}:{node.annotation}={node.value}\n'
        yield from self.gen(node.target)
        yield from self.gen_op(':')
        yield from self.gen(node.annotation)
        if node.value is not None:  # #1851
            yield from self.gen_op('=')
            yield from self.gen(node.value)
    #@+node:ekr.20220330133336.49: *5* iterative.Assert
    # Assert(expr test, expr? msg)

    def do_Assert(self, node):

        # Guards...
        msg = getattr(node, 'msg', None)
        # No need to put parentheses or commas.
        yield from self.gen_name('assert')
        yield from self.gen(node.test)
        if msg is not None:
            yield from self.gen(node.msg)
    #@+node:ekr.20220330133336.50: *5* iterative.Assign
    def do_Assign(self, node):

        for z in node.targets:
            yield from self.gen(z)
            yield from self.gen_op('=')
        yield from self.gen(node.value)
    #@+node:ekr.20220330133336.51: *5* iterative.AsyncFor
    def do_AsyncFor(self, node):

        # The def line...
        # Py 3.8 changes the kind of token.
        async_token_type = 'async' if has_async_tokens else 'name'
        yield from self.gen_token(async_token_type, 'async')
        yield from self.gen_name('for')
        yield from self.gen(node.target)
        yield from self.gen_name('in')
        yield from self.gen(node.iter)
        yield from self.gen_op(':')
        # Body...
        self.level += 1
        yield from self.gen(node.body)
        # Else clause...
        if node.orelse:
            yield from self.gen_name('else')
            yield from self.gen_op(':')
            yield from self.gen(node.orelse)
        self.level -= 1
    #@+node:ekr.20220330133336.52: *5* iterative.AsyncWith
    def do_AsyncWith(self, node):

        async_token_type = 'async' if has_async_tokens else 'name'
        yield from self.gen_token(async_token_type, 'async')
        yield from self.do_With(node)
    #@+node:ekr.20220330133336.53: *5* iterative.AugAssign
    # AugAssign(expr target, operator op, expr value)

    def do_AugAssign(self, node):

        # %s%s=%s\n'
        op_name_ = op_name(node.op)
        yield from self.gen(node.target)
        yield from self.gen_op(op_name_ + '=')
        yield from self.gen(node.value)
    #@+node:ekr.20220330133336.54: *5* iterative.Await
    # Await(expr value)

    def do_Await(self, node):

        #'await %s\n'
        async_token_type = 'await' if has_async_tokens else 'name'
        yield from self.gen_token(async_token_type, 'await')
        yield from self.gen(node.value)
    #@+node:ekr.20220330133336.55: *5* iterative.Break
    def do_Break(self, node):

        yield from self.gen_name('break')
    #@+node:ekr.20220330133336.56: *5* iterative.Call & helpers
    # Call(expr func, expr* args, keyword* keywords)

    # Python 3 ast.Call nodes do not have 'starargs' or 'kwargs' fields.

    def do_Call(self, node):

        # The calls to gen_op(')') and gen_op('(') do nothing by default.
        # Subclasses might handle them in an overridden iterative.set_links.
        yield from self.gen(node.func)
        yield from self.gen_op('(')
        # No need to generate any commas.
        yield from self.handle_call_arguments(node)
        yield from self.gen_op(')')
    #@+node:ekr.20220330133336.57: *6* iterative.arg_helper
    def arg_helper(self, node):
        """
        Yield the node, with a special case for strings.
        """
        if isinstance(node, str):
            yield from self.gen_token('name', node)
        else:
            yield from self.gen(node)
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
                    yield from self.gen_op('*')
                    yield from self.gen(z.value)
                elif isinstance(z, ast.keyword):
                    if getattr(z, 'arg', None) is None:
                        yield from self.gen_op('**')
                        yield from self.arg_helper(z.value)
                    else:
                        yield from self.arg_helper(z.arg)
                        yield from self.gen_op('=')
                        yield from self.arg_helper(z.value)
                else:
                    yield from self.arg_helper(z)
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
                yield from self.arg_helper(z)
            # Sync the keyword args.
            for z in keywords:
                yield from self.arg_helper(z.arg)
                yield from self.gen_op('=')
                yield from self.arg_helper(z.value)
            # Sync the * arg.
            if star_arg:
                yield from self.arg_helper(star_arg)
            # Sync the ** kwarg.
            if kwarg_arg:
                yield from self.gen_op('**')
                yield from self.gen(kwarg_arg.value)
    #@+node:ekr.20220330133336.59: *5* iterative.Continue
    def do_Continue(self, node):

        yield from self.gen_name('continue')
    #@+node:ekr.20220330133336.60: *5* iterative.Delete
    def do_Delete(self, node):

        # No need to put commas.
        yield from self.gen_name('del')
        yield from self.gen(node.targets)
    #@+node:ekr.20220330133336.61: *5* iterative.ExceptHandler
    def do_ExceptHandler(self, node):

        # Except line...
        yield from self.gen_name('except')
        if getattr(node, 'type', None):
            yield from self.gen(node.type)
        if getattr(node, 'name', None):
            yield from self.gen_name('as')
            yield from self.gen_name(node.name)
        yield from self.gen_op(':')
        # Body...
        self.level += 1
        yield from self.gen(node.body)
        self.level -= 1
    #@+node:ekr.20220330133336.62: *5* iterative.For
    def do_For(self, node):

        # The def line...
        yield from self.gen_name('for')
        yield from self.gen(node.target)
        yield from self.gen_name('in')
        yield from self.gen(node.iter)
        yield from self.gen_op(':')
        # Body...
        self.level += 1
        yield from self.gen(node.body)
        # Else clause...
        if node.orelse:
            yield from self.gen_name('else')
            yield from self.gen_op(':')
            yield from self.gen(node.orelse)
        self.level -= 1
    #@+node:ekr.20220330133336.63: *5* iterative.Global
    # Global(identifier* names)

    def do_Global(self, node):

        yield from self.gen_name('global')
        for z in node.names:
            yield from self.gen_name(z)
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
        yield from self.gen_name(token.value)
        yield from self.gen(node.test)
        yield from self.gen_op(':')
        #
        # Body...
        self.level += 1
        yield from self.gen(node.body)
        self.level -= 1
        #
        # Else and elif clauses...
        if node.orelse:
            self.level += 1
            token = self.find_next_significant_token()
            if token.value == 'else':
                yield from self.gen_name('else')
                yield from self.gen_op(':')
                yield from self.gen(node.orelse)
            else:
                yield from self.gen(node.orelse)
            self.level -= 1
    #@+node:ekr.20220330133336.66: *5* iterative.Import & helper
    def do_Import(self, node):

        yield from self.gen_name('import')
        for alias in node.names:
            yield from self.gen_name(alias.name)
            if alias.asname:
                yield from self.gen_name('as')
                yield from self.gen_name(alias.asname)
    #@+node:ekr.20220330133336.67: *5* iterative.ImportFrom
    # ImportFrom(identifier? module, alias* names, int? level)

    def do_ImportFrom(self, node):

        yield from self.gen_name('from')
        for i in range(node.level):
            yield from self.gen_op('.')
        if node.module:
            yield from self.gen_name(node.module)
        yield from self.gen_name('import')
        # No need to put commas.
        for alias in node.names:
            if alias.name == '*':  # #1851.
                yield from self.gen_op('*')
            else:
                yield from self.gen_name(alias.name)
            if alias.asname:
                yield from self.gen_name('as')
                yield from self.gen_name(alias.asname)
    #@+node:ekr.20220330133336.68: *5* iterative.Match* (Python 3.10+)
    # Match(expr subject, match_case* cases)

    # match_case = (pattern pattern, expr? guard, stmt* body)

    def do_Match(self, node):

        cases = getattr(node, 'cases', [])
        yield from self.gen_name('match')
        yield from self.gen(node.subject)
        yield from self.gen_op(':')
        for case in cases:
            yield from self.gen(case)
    #@+node:ekr.20220330133336.69: *6* iterative.match_case
    #  match_case = (pattern pattern, expr? guard, stmt* body)

    def do_match_case(self, node):

        g.trace(g.callers())
        guard = getattr(node, 'guard', None)
        body = getattr(node, 'body', [])
        yield from self.gen_name('case')
        yield from self.gen(node.pattern)
        if guard:
            yield from self.gen(guard)
        yield from self.gen_op(':')
        for statement in body:
            yield from self.gen(statement)
    #@+node:ekr.20220330133336.70: *6* iterative.MatchAs (test)
    # MatchAs(pattern? pattern, identifier? name)

    def do_MatchAs(self, node):
        pattern = getattr(node, 'pattern', None)
        name = getattr(node, 'name', None)
        g.trace(pattern, name)
        if pattern:
            yield from self.gen(pattern)
        if name:
            yield from self.gen_name(name)

        
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
            yield from self.gen(pattern)


    #@+node:ekr.20220330133336.74: *6* iterative.MatchSequence (test)
    # MatchSequence(pattern* patterns)

    def do_MatchSequence(self, node):
        patterns = getattr(node, 'patterns', [])
        g.trace(node, patterns)
        for pattern in patterns:
            yield from self.gen(pattern)

    #@+node:ekr.20220330133336.75: *6* iterative.MatchSingleton (test)
    # MatchSingleton(constant value)

    def do_MatchSingleton(self, node):
        g.trace(node, node.value)
        yield from self.gen(node.value)
    #@+node:ekr.20220330133336.76: *6* iterative.MatchStar (test)
    # MatchStar(identifier? name)

    def do_MatchStar(self, node):
        name = getattr(node, 'name', None)
        g.trace(node, repr(name))
        if name:
            yield from self.gen_name(name)
    #@+node:ekr.20220330133336.77: *6* iterative.MatchValue
    # MatchValue(expr value)

    def do_MatchValue(self, node):

        yield from self.gen(node.value)
    #@+node:ekr.20220330133336.78: *5* iterative.Nonlocal
    # Nonlocal(identifier* names)

    def do_Nonlocal(self, node):

        # nonlocal %s\n' % ','.join(node.names))
        # No need to put commas.
        yield from self.gen_name('nonlocal')
        for z in node.names:
            yield from self.gen_name(z)
    #@+node:ekr.20220330133336.79: *5* iterative.Pass
    def do_Pass(self, node):

        # yield from self.gen_name('pass')
        
        return ([
            (self.name, 'pass'),
        ])
    #@+node:ekr.20220330133336.80: *5* iterative.Raise
    # Raise(expr? exc, expr? cause)

    def do_Raise(self, node):

        # No need to put commas.
        yield from self.gen_name('raise')
        exc = getattr(node, 'exc', None)
        cause = getattr(node, 'cause', None)
        tback = getattr(node, 'tback', None)
        yield from self.gen(exc)
        if cause:
            yield from self.gen_name('from')  # #2446.
            yield from self.gen(cause)
        yield from self.gen(tback)
    #@+node:ekr.20220330133336.81: *5* iterative.Return
    def do_Return(self, node):

        yield from self.gen_name('return')
        yield from self.gen(node.value)
    #@+node:ekr.20220330133336.82: *5* iterative.Try
    # Try(stmt* body, excepthandler* handlers, stmt* orelse, stmt* finalbody)

    def do_Try(self, node):

        # Try line...
        yield from self.gen_name('try')
        yield from self.gen_op(':')
        # Body...
        self.level += 1
        yield from self.gen(node.body)
        yield from self.gen(node.handlers)
        # Else...
        if node.orelse:
            yield from self.gen_name('else')
            yield from self.gen_op(':')
            yield from self.gen(node.orelse)
        # Finally...
        if node.finalbody:
            yield from self.gen_name('finally')
            yield from self.gen_op(':')
            yield from self.gen(node.finalbody)
        self.level -= 1
    #@+node:ekr.20220330133336.83: *5* iterative.While
    def do_While(self, node):

        # While line...
            # while %s:\n'
        yield from self.gen_name('while')
        yield from self.gen(node.test)
        yield from self.gen_op(':')
        # Body...
        self.level += 1
        yield from self.gen(node.body)
        # Else clause...
        if node.orelse:
            yield from self.gen_name('else')
            yield from self.gen_op(':')
            yield from self.gen(node.orelse)
        self.level -= 1
    #@+node:ekr.20220330133336.84: *5* iterative.With
    # With(withitem* items, stmt* body)

    # withitem = (expr context_expr, expr? optional_vars)

    def do_With(self, node):

        expr: Optional[ast.AST] = getattr(node, 'context_expression', None)
        items: List[ast.AST] = getattr(node, 'items', [])
        yield from self.gen_name('with')
        yield from self.gen(expr)
        # No need to put commas.
        for item in items:
            yield from self.gen(item.context_expr)  # type:ignore
            optional_vars = getattr(item, 'optional_vars', None)
            if optional_vars is not None:
                yield from self.gen_name('as')
                yield from self.gen(item.optional_vars)  # type:ignore
        # End the line.
        yield from self.gen_op(':')
        # Body...
        self.level += 1
        yield from self.gen(node.body)
        self.level -= 1
    #@+node:ekr.20220330133336.85: *5* iterative.Yield
    def do_Yield(self, node):

        # yield from self.gen_name('yield')
        # if hasattr(node, 'value'):
            # yield from self.gen(node.value)
            
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

        # yield from self.gen_name('yield')
        # yield from self.gen_name('from')
        # yield from self.gen(node.value)
        
        return ([
            (self.name, 'yield'),
            (self.name, 'from'),
            (self.visit, node.value),
        ])
    #@-others
#@-others
#@-leo
