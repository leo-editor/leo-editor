# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20220402144737.1: * @file ../unittests/core/test_iterative_ast.py
#@@first
"""Tests of iterative_ast.py"""
import ast
import textwrap
from leo.core import leoGlobals as g
from leo.core.leoAst import dump_ast, dump_contents, dump_tokens, dump_tree
from leo.core.iterative_ast import IterativeTokenGenerator
from leo.unittests.core.test_leoAst import TestTOG, get_time

class TestIterative(TestTOG):
    """
    Tests for the IterativeTokenGenerator class.
    
    This class inherits:
    - all the tests from the TestTOG class.
    - most of the support code from the BaseTest class.
    """
    ### debug_list = ['unit-test']
    #@+others
    #@+node:ekr.20220402150424.1: ** TestIterative.make_data
    def make_data(self, contents, description=None):  # pragma: no cover
        """Return (contents, tokens, tree) for the given contents."""
        contents = contents.lstrip('\\\n')
        if not contents:
            return '', None, None  
        self.link_error = None
        t1 = get_time()
        self.update_counts('characters', len(contents))
        # Ensure all tests end in exactly one newline.
        contents = textwrap.dedent(contents).rstrip() + '\n'
        # Create the TOG instance.
        self.tog = IterativeTokenGenerator()  ### TokenOrderGenerator()
        self.tog.filename = description or g.callers(2).split(',')[0]
        # Pass 0: create the tokens and parse tree
        tokens = self.make_tokens(contents)
        if not tokens:
            self.fail('make_tokens failed')
        tree = self.make_tree(contents)
        if not tree:
            self.fail('make_tree failed')
        if 'contents' in self.debug_list:
            dump_contents(contents)
        if 'ast' in self.debug_list:
            if True:  ###py_version >= (3, 9):
                # pylint: disable=unexpected-keyword-arg
                g.printObj(ast.dump(tree, indent=2), tag='ast.dump')
            # else:
            #     g.printObj(ast.dump(tree), tag='ast.dump')
        if 'tree' in self.debug_list:  # Excellent traces for tracking down mysteries.
            dump_ast(tree)  # pragma: no cover
        if 'tokens' in self.debug_list:
            dump_tokens(tokens)  # pragma: no cover
        self.balance_tokens(tokens)
        # Pass 1: create the links.
        self.create_links(tokens, tree)
        if 'post-tree' in self.debug_list:
            dump_tree(tokens, tree)  # pragma: no cover
        if 'post-tokens' in self.debug_list:
            dump_tokens(tokens)  # pragma: no cover
        t2 = get_time()
        self.update_times('90: TOTAL', t2 - t1)
        if self.link_error:
            self.fail(self.link_error)  # pragma: no cover
        return contents, tokens, tree
    #@-others

#@-leo
