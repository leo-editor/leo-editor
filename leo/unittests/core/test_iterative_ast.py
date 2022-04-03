# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20220402144737.1: * @file ../unittests/core/test_iterative_ast.py
#@@first
"""Tests of iterative_ast.py"""
import ast
import textwrap
import warnings
from leo.core import leoGlobals as g
from leo.core.leoAst import dump_ast, dump_contents, dump_tokens, dump_tree
from leo.core.iterative_ast import IterativeTokenGenerator
from leo.unittests.core.test_leoAst import TestTOG, get_time

try:
    # Suppress a warning about imp being deprecated.
    with warnings.catch_warnings():
        import black
except Exception:  # pragma: no cover
    black = None

#@+others
#@+node:ekr.20220402152331.1: ** class TestIterative
class TestIterative(TestTOG):
    """
    Tests for the IterativeTokenGenerator class.
    
    This class inherits:
    - all the tests from the TestTOG class.
    - most of the support code from the BaseTest class.
    """
    debug_list = [] # 'full-traceback', 'tokens', 'tree'

    #@+others
    #@+node:ekr.20220402150424.1: *3* TestIterative.make_data (override)
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
    #@+node:ekr.20220403063148.1: *3* Copies of TestOrange tests
    # Required for full coverage.
    #@+node:ekr.20220403062001.1: *4* TestIterative.test_one_line_pet_peeves
    def test_one_line_pet_peeves(self):
        
        # A copy of TestOrange.test_one_line_pet_peeves.
        # Necessary for coverage testings for slices.

        tag = 'test_one_line_pet_peeves'
        # Except where noted, all entries are expected values....
        if 0:
            # Test fails or recents...
            table = (
                # """a[: 1 if True else 2 :]""",
                """a[:-1]""",
            )
        else:
            table = (
                # Assignments...
                # Slices (colons)...
                """a[:-1]""",
                """a[: 1 if True else 2 :]""",
                """a[1 : 1 + 2]""",
                """a[lower:]""",
                """a[lower::]""",
                """a[:upper]""",
                """a[:upper:]""",
                """a[::step]""",
                """a[lower:upper:]""",
                """a[lower:upper:step]""",
                """a[lower + offset : upper + offset]""",
                """a[: upper_fn(x) :]""",
                """a[: upper_fn(x) : step_fn(x)]""",
                """a[:: step_fn(x)]""",
                """a[: upper_fn(x) :]""",
                """a[: upper_fn(x) : 2 + 1]""",
                """a[:]""",
                """a[::]""",
                """a[1:]""",
                """a[1::]""",
                """a[:2]""",
                """a[:2:]""",
                """a[::3]""",
                """a[1:2]""",
                """a[1:2:]""",
                """a[:2:3]""",
                """a[1:2:3]""",
                # * and **, inside and outside function calls.
                """a = b * c""",
                # Now done in test_star_star_operator
                # """a = b ** c""",  # Black has changed recently.
                """f(*args)""",
                """f(**kwargs)""",
                """f(*args, **kwargs)""",
                """f(a, *args)""",
                """f(a=2, *args)""",
                # Calls...
                """f(-1)""",
                """f(-1 < 2)""",
                """f(1)""",
                """f(2 * 3)""",
                """f(2 + name)""",
                """f(a)""",
                """f(a.b)""",
                """f(a=2 + 3, b=4 - 5, c= 6 * 7, d=8 / 9, e=10 // 11)""",
                """f(a[1 + 2])""",
                """f({key: 1})""",
                """t = (0,)""",
                """x, y = y, x""",
                # Dicts...
                """d = {key: 1}""",
                """d['key'] = a[i]""",
                # Trailing comments: expect two spaces.
                """whatever # comment""",
                """whatever  # comment""",
                """whatever   # comment""",
                # Word ops...
                """v1 = v2 and v3 if v3 not in v4 or v5 in v6 else v7""",
                """print(v7 for v8 in v9)""",
                # Unary ops...
                """v = -1 if a < b else -2""",
                # Returns...
                """return -1""",
            )
        fails = 0
        for i, contents in enumerate(table):
            description = f"{tag} part {i}"
            contents, tokens, tree = self.make_data(contents, description)
            expected = self.blacken(contents)
            results = self.beautify(contents, tokens, tree, filename=description)
            message = (
                f"\n"
                f"  contents: {contents.rstrip()}\n"
                f"     black: {expected.rstrip()}\n"
                f"    orange: {results.rstrip()}")
            if results != expected:  # pragma: no cover
                fails += 1
                print(f"Fail: {fails}\n{message}")
        self.assertEqual(fails, 0)
    #@+node:ekr.20220403062532.1: *4* TestIterative.blacken
    def blacken(self, contents, line_length=None):
        """Return the results of running black on contents"""
        # A copy of TestOrange.blacken
        if not black:
            self.skipTest('Can not import black')  # pragma: no cover
        # Suppress string normalization!
        try:
            mode = black.FileMode()
            mode.string_normalization = False
            if line_length is not None:
                mode.line_length = line_length
        except TypeError:  # pragma: no cover
            self.skipTest('old version of black')
        return black.format_str(contents, mode=mode)
    #@-others
#@-others
#@-leo
