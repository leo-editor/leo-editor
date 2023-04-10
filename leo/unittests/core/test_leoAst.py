#@+leo-ver=5-thin
#@+node:ekr.20210902073413.1: * @file ../unittests/core/test_leoAst.py
"""Tests of leoAst.py"""
#@+<< test_leoAst imports >>
#@+node:ekr.20210902074548.1: ** << test_leoAst imports >>
import ast
import os
import sys
import textwrap
import time
import token as token_module
from typing import Any, Callable, Dict, List, Tuple
import unittest
import warnings
warnings.simplefilter("ignore")
# pylint: disable=import-error
# Third-party.
try:
    import asttokens
except Exception:  # pragma: no cover
    asttokens = None
try:
    # Suppress a warning about imp being deprecated.
    with warnings.catch_warnings():
        import black
except Exception:  # pragma: no cover
    black = None

# pylint: disable=wrong-import-position
from leo.core import leoGlobals as g

from leo.core.leoAst import AstNotEqual
from leo.core.leoAst import Fstringify, Orange
from leo.core.leoAst import Token, TokenOrderGenerator  ###, TokenOrderTraverser
from leo.core.leoAst import get_encoding_directive, read_file, strip_BOM
from leo.core.leoAst import make_tokens, parse_ast, tokens_to_string
from leo.core.leoAst import dump_ast, dump_contents, dump_tokens, dump_tree, _op_names
#@-<< test_leoAst imports >>
v1, v2, junk1, junk2, junk3 = sys.version_info
py_version = (v1, v2)
ActionList = List[Tuple[Callable, Any]]
#@+others
#@+node:ekr.20200107114620.1: ** functions: unit testing
#@+node:ekr.20191027072126.1: *3* function: compare_asts & helpers
def compare_asts(ast1, ast2):  # pragma: no cover
    """Compare two ast trees. Return True if they are equal."""
    # Compare the two parse trees.
    try:
        _compare_asts(ast1, ast2)
    except AstNotEqual:
        dump_ast(ast1, tag='AST BEFORE')
        dump_ast(ast2, tag='AST AFTER')
        return False
    except Exception:
        g.trace("Unexpected exception")
        g.es_exception()
        return False
    return True
#@+node:ekr.20191027071653.2: *4* function._compare_asts
def _compare_asts(node1, node2):  # pragma: no cover
    """
    Compare both nodes, and recursively compare their children.

    See also: http://stackoverflow.com/questions/3312989/
    """
    # Compare the nodes themselves.
    _compare_nodes(node1, node2)
    # Get the list of fields.
    fields1 = getattr(node1, "_fields", [])  # type:ignore
    fields2 = getattr(node2, "_fields", [])  # type:ignore
    if fields1 != fields2:
        raise AstNotEqual(
            f"node1._fields: {fields1}\n" f"node2._fields: {fields2}")
    # Recursively compare each field.
    for field in fields1:
        if field not in ('lineno', 'col_offset', 'ctx'):
            attr1 = getattr(node1, field, None)
            attr2 = getattr(node2, field, None)
            if attr1.__class__.__name__ != attr2.__class__.__name__:
                raise AstNotEqual(f"attrs1: {attr1},\n" f"attrs2: {attr2}")
            _compare_asts(attr1, attr2)
#@+node:ekr.20191027071653.3: *4* function._compare_nodes
def _compare_nodes(node1, node2):  # pragma: no cover
    """
    Compare node1 and node2.
    For lists and tuples, compare elements recursively.
    Raise AstNotEqual if not equal.
    """
    # Class names must always match.
    if node1.__class__.__name__ != node2.__class__.__name__:
        raise AstNotEqual(
            f"node1.__class__.__name__: {node1.__class__.__name__}\n"
            f"node2.__class__.__name__: {node2.__class__.__name_}"
        )
    # Special cases for strings and None
    if node1 is None:
        return
    if isinstance(node1, str):
        if node1 != node2:
            raise AstNotEqual(f"node1: {node1!r}\n" f"node2: {node2!r}")
    # Special cases for lists and tuples:
    if isinstance(node1, (tuple, list)):
        if len(node1) != len(node2):
            raise AstNotEqual(f"node1: {node1}\n" f"node2: {node2}")
        for i, item1 in enumerate(node1):
            item2 = node2[i]
            if item1.__class__.__name__ != item2.__class__.__name__:
                raise AstNotEqual(
                    f"list item1: {i} {item1}\n" f"list item2: {i} {item2}"
                )
            _compare_asts(item1, item2)
#@+node:ekr.20191121081439.1: *3* function: compare_lists
def compare_lists(list1, list2):  # pragma: no cover
    """
    Compare two lists of strings, showing the first mismatch.

    Return the index of the first mismatched lines, or None if identical.
    """
    import itertools
    it = itertools.zip_longest(list1, list2, fillvalue='Missing!')
    for i, (s1, s2) in enumerate(it):
        if s1 != s2:
            return i
    return None
#@+node:ekr.20191226071135.1: *3* function: get_time
def get_time():
    return time.process_time()
#@+node:ekr.20220403080350.1: ** Base Test classes
#@+node:ekr.20191227154302.1: *3* class BaseTest (TestCase)
class BaseTest(unittest.TestCase):
    """
    The base class of all tests of leoAst.py.

    This class contains only helpers.
    """

    # Statistics.
    counts: Dict[str, int] = {}
    times: Dict[str, float] = {}

    # Debugging traces & behavior.
    # create_links: 'full-traceback'
    # make_data: 'contents', 'tokens', 'tree',
    #            'post-tokens', 'post-tree',
    #            'unit-test'
    debug_list: List[str] = []
    link_error: Exception = None

    #@+others
    #@+node:ekr.20200110103036.1: *4* BaseTest.adjust_expected
    def adjust_expected(self, s):
        """Adjust leading indentation in the expected string s."""
        return textwrap.dedent(s.lstrip('\\\n')).rstrip() + '\n'
    #@+node:ekr.20200110092217.1: *4* BaseTest.check_roundtrip
    def check_roundtrip(self, contents):
        """Check that the tokenizer round-trips the given contents."""
        contents, tokens, tree = self.make_data(contents)
        results = tokens_to_string(tokens)
        self.assertEqual(contents, results)
    #@+node:ekr.20191227054856.1: *4* BaseTest.make_data
    def make_data(self, contents, description=None):
        """Return (contents, tokens, tree) for the given contents."""
        contents = contents.lstrip('\\\n')
        if not contents:
            return '', None, None  # pragma: no cover
        self.link_error = None
        t1 = get_time()
        self.update_counts('characters', len(contents))
        # Ensure all tests end in exactly one newline.
        contents = textwrap.dedent(contents).rstrip() + '\n'
        # Create the TOG instance.
        self.tog = TokenOrderGenerator()
        self.tog.filename = description or g.callers(2).split(',')[0]
        # Pass 0: create the tokens and parse tree
        tokens = self.make_tokens(contents)
        if not tokens:
            self.fail('make_tokens failed')  # pragma: no cover
        tree = self.make_tree(contents)
        if not tree:
            self.fail('make_tree failed')  # pragma: no cover
        if 'contents' in self.debug_list:
            dump_contents(contents)  # pragma: no cover
        if 'ast' in self.debug_list:  # pragma: no cover
            if py_version >= (3, 9):
                # pylint: disable=unexpected-keyword-arg
                g.printObj(ast.dump(tree, indent=2), tag='ast.dump')
            else:
                g.printObj(ast.dump(tree), tag='ast.dump')
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
    #@+node:ekr.20191227103533.1: *4* BaseTest.make_file_data
    def make_file_data(self, filename):
        """Return (contents, tokens, tree) from the given file."""
        directory = os.path.dirname(__file__)
        filename = g.finalize_join(directory, '..', '..', 'core', filename)
        assert os.path.exists(filename), repr(filename)
        contents = read_file(filename)
        contents, tokens, tree = self.make_data(contents, filename)
        return contents, tokens, tree
    #@+node:ekr.20191228101601.1: *4* BaseTest: passes...
    #@+node:ekr.20191228095945.11: *5* 0.1: BaseTest.make_tokens
    def make_tokens(self, contents):
        """
        BaseTest.make_tokens.

        Make tokens from contents.
        """
        t1 = get_time()
        # Tokenize.
        tokens = make_tokens(contents)
        t2 = get_time()
        self.update_counts('tokens', len(tokens))
        self.update_times('01: make-tokens', t2 - t1)
        return tokens
    #@+node:ekr.20191228102101.1: *5* 0.2: BaseTest.make_tree
    def make_tree(self, contents):
        """
        BaseTest.make_tree.

        Return the parse tree for the given contents string.
        """
        t1 = get_time()
        tree = parse_ast(contents)
        t2 = get_time()
        self.update_times('02: parse_ast', t2 - t1)
        return tree
    #@+node:ekr.20191228185201.1: *5* 0.3: BaseTest.balance_tokens
    def balance_tokens(self, tokens):
        """
        BastTest.balance_tokens.

        Insert links between corresponding paren tokens.
        """
        t1 = get_time()
        count = self.tog.balance_tokens(tokens)
        t2 = get_time()
        self.update_counts('paren-tokens', count)
        self.update_times('03: balance-tokens', t2 - t1)
        return count
    #@+node:ekr.20191228101437.1: *5* 1.1: BaseTest.create_links
    def create_links(self, tokens, tree, filename='unit test'):
        """
        BaseTest.create_links.

        Insert two-way links between the tokens and ast tree.
        """
        tog = self.tog
        try:
            t1 = get_time()
            tog.create_links(tokens, tree)
            t2 = get_time()
            self.update_counts('nodes', tog.n_nodes)
            self.update_times('11: create-links', t2 - t1)
        except Exception as e:  # pragma: no cover
            if 'full-traceback' in self.debug_list:
                g.es_exception()
            # Weird: calling self.fail creates ugly failures.
            self.link_error = e
    #@+node:ekr.20191228095945.10: *5* 2.1: BaseTest.fstringify
    def fstringify(self, contents, tokens, tree, filename=None, silent=False):
        """
        BaseTest.fstringify.
        """
        t1 = get_time()
        if not filename:
            filename = g.callers(1)
        fs = Fstringify()
        if silent:
            fs.silent = True
        result_s = fs.fstringify(contents, filename, tokens, tree)
        t2 = get_time()
        self.update_times('21: fstringify', t2 - t1)
        return result_s
    #@+node:ekr.20200107175223.1: *5* 2.2: BaseTest.beautify
    def beautify(self, contents, tokens, tree, filename=None, max_join_line_length=None, max_split_line_length=None):
        """
        BaseTest.beautify.
        """
        t1 = get_time()
        if not contents:
            return ''  # pragma: no cover
        if not filename:
            filename = g.callers(2).split(',')[0]
        orange = Orange()
        result_s = orange.beautify(contents, filename, tokens, tree,
            max_join_line_length=max_join_line_length,
            max_split_line_length=max_split_line_length)
        t2 = get_time()
        self.update_times('22: beautify', t2 - t1)
        self.code_list = orange.code_list
        return result_s
    #@+node:ekr.20191228095945.1: *4* BaseTest: stats...
    # Actions should fail by throwing an exception.
    #@+node:ekr.20191228095945.12: *5* BaseTest.dump_stats & helpers
    def dump_stats(self):  # pragma: no cover
        """Show all calculated statistics."""
        if self.counts or self.times:
            print('')
            self.dump_counts()
            self.dump_times()
            print('')
    #@+node:ekr.20191228154757.1: *6* BaseTest.dump_counts
    def dump_counts(self):  # pragma: no cover
        """Show all calculated counts."""
        for key, n in self.counts.items():
            print(f"{key:>16}: {n:>6}")
    #@+node:ekr.20191228154801.1: *6* BaseTest.dump_times
    def dump_times(self):  # pragma: no cover
        """
        Show all calculated times.

        Keys should start with a priority (sort order) of the form `[0-9][0-9]:`
        """
        for key in sorted(self.times):
            t = self.times.get(key)
            key2 = key[3:]
            print(f"{key2:>16}: {t:6.3f} sec.")
    #@+node:ekr.20191228181624.1: *5* BaseTest.update_counts & update_times
    def update_counts(self, key, n):  # pragma: no cover
        """Update the count statistic given by key, n."""
        old_n = self.counts.get(key, 0)
        self.counts[key] = old_n + n

    def update_times(self, key, t):  # pragma: no cover
        """Update the timing statistic given by key, t."""
        old_t = self.times.get(key, 0.0)
        self.times[key] = old_t + t
    #@-others
#@+node:ekr.20191227051737.1: *3* class TestTOG (BaseTest)
class TestTOG(BaseTest):
    """
    Tests for the TokenOrderGenerator class.

    These tests call BaseTest.make_data, which creates the two-way links
    between tokens and the parse tree.

    The asserts in tog.sync_tokens suffice to create strong unit tests.
    """

    debug_list = ['unit-test']

    #@+others
    #@+node:ekr.20210318213945.1: *4* TestTOG.Recent bugs & features
    #@+node:ekr.20210321172902.1: *5* test_bug_1851
    def test_bug_1851(self):

        contents = r'''\
    def foo(a1):
        pass
    '''
        contents, tokens, tree = self.make_data(contents)
    #@+node:ekr.20210914161519.1: *5* test_bug_2171
    def test_bug_2171(self):

        if py_version < (3, 9):
            self.skipTest('Requires Python 3.9')  # pragma: no cover

        contents = "'HEAD:%s' % g.os_path_join( *(relative_path + [filename]) )"
        contents, tokens, tree = self.make_data(contents)
    #@+node:ekr.20210318213133.1: *5* test_full_grammar
    def test_full_grammar(self):
        # Load py3_test_grammar.py.
        dir_ = os.path.dirname(__file__)
        path = os.path.abspath(os.path.join(dir_, '..', 'py3_test_grammar.py'))
        assert os.path.exists(path), path
        if py_version < (3, 9):
            self.skipTest('Requires Python 3.9 or above')  # pragma: no cover
        # Verify that leoAst can parse the file.
        contents = read_file(path)
        self.make_data(contents)
    #@+node:ekr.20210318214057.1: *5* test_line_315
    def test_line_315(self):

        #
        # Known bug: position-only args exist in Python 3.8,
        #            but there is no easy way of syncing them.
        #            This bug will not be fixed.
        #            The workaround is to require Python 3.9
        if py_version >= (3, 9):
            contents = '''\
    f(1, x=2,
        *[3, 4], y=5)
    '''
        elif 1:  # pragma: no cover
            contents = '''f(1, *[a, 3], x=2, y=5)'''  # pragma: no cover
        else:  # pragma: no cover
            contents = '''f(a, *args, **kwargs)'''
        contents, tokens, tree = self.make_data(contents)
    #@+node:ekr.20210320095504.8: *5* test_line_337
    def test_line_337(self):

        if py_version >= (3, 8):  # Requires neither line_no nor col_offset fields.
            contents = '''def f(a, b:1, c:2, d, e:3=4, f=5, *g:6, h:7, i=8, j:9=10, **k:11) -> 12: pass'''
        else:
            contents = '''def f(a, b, d=4, *arg, **keys): pass'''  # pragma: no cover
        contents, tokens, tree = self.make_data(contents)
    #@+node:ekr.20210320065202.1: *5* test_line_483
    def test_line_483(self):

        if py_version < (3, 8):
            # Python 3.8: https://bugs.python.org/issue32117
            self.skipTest(f"Python {v1}.{v2} does not support generalized iterable assignment")  # pragma: no cover
        contents = '''def g3(): return 1, *return_list'''
        contents, tokens, tree = self.make_data(contents)
    #@+node:ekr.20210320065344.1: *5* test_line_494
    def test_line_494(self):

        """
        https://docs.python.org/3/whatsnew/3.8.html#other-language-changes

        Generalized iterable unpacking in yield and return statements no longer
        requires enclosing parentheses. This brings the yield and return syntax
        into better agreement with normal assignment syntax.
        """
        if py_version < (3, 8):
            # Python 3.8: https://bugs.python.org/issue32117
            self.skipTest(f"Python {v1}.{v2} does not support generalized iterable assignment")  # pragma: no cover
        contents = '''def g2(): yield 1, *yield_list'''
        contents, tokens, tree = self.make_data(contents)
    #@+node:ekr.20210319130349.1: *5* test_line_875
    def test_line_875(self):

        contents = '''list((x, y) for x in 'abcd' for y in 'abcd')'''
        contents, tokens, tree = self.make_data(contents)
    #@+node:ekr.20210319130616.1: *5* test_line_898
    def test_line_898(self):

        contents = '''g = ((i,j) for i in range(x) if t for j in range(x))'''
        contents, tokens, tree = self.make_data(contents)
    #@+node:ekr.20210320085705.1: *5* test_walrus_operator
    def test_walrus_operator(self):

        if py_version < (3, 8):
            self.skipTest(f"Python {v1}.{v2} does not support assignment expressions")  # pragma: no cover
        contents = '''if (n := len(a)) > 10: pass'''
        contents, tokens, tree = self.make_data(contents)
    #@+node:ekr.20191227052446.10: *4* TestTOG.Contexts...
    #@+node:ekr.20191227052446.11: *5* test_ClassDef
    def test_ClassDef(self):
        contents = """\
    class TestClass1:
        pass

    def decorator():
        pass

    @decorator
    class TestClass2:
        pass

    @decorator
    class TestClass(base1, base2):
        pass
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.12: *5* test_ClassDef2
    def test_ClassDef2(self):
        contents = r'''\
    """ds 1"""
    class TestClass:
        """ds 2"""
        def long_name(a, b=2):
            """ds 3"""
            print('done')
    '''
        self.make_data(contents)
    #@+node:ekr.20191227052446.13: *5* test_FunctionDef
    def test_FunctionDef(self):
        contents = r"""\
    def run(fileName=None, pymacs=None):
        pass
    """
        self.make_data(contents)
    #@+node:ekr.20200111171738.1: *5* test_FunctionDef_with_annotations
    def test_FunctionDef_with_annotations(self):
        contents = r"""\
    def foo(a: 'x', b: 5 + 6, c: list) -> max(2, 9):
        pass
    """
        self.make_data(contents)
        # contents, tokens, tree = self.make_data(contents)
        # dump_ast(tree)
    #@+node:ekr.20210802162650.1: *5* test_FunctionDef_with_posonly_args
    def test_FunctionDef_with_posonly_args(self):

        if py_version < (3, 9):
            self.skipTest('Requires Python 3.9')  # pragma: no cover

        # From PEP 570
        contents = r"""\
    def pos_only_arg(arg, /):
        pass
    def kwd_only_arg(*, arg):
        pass
    def combined_example(pos_only, /, standard, *, kwd_only):
        pass
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.14: *4* TestTOG.Expressions & operators...
    #@+node:ekr.20191227052446.15: *5* test_attribute
    def test_attribute(self):
        contents = r"""\
    open(os.devnull, "w")
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.16: *5* test_CompareOp
    def test_CompareOp(self):
        contents = r"""\
    if a and not b and c:
        pass
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.17: *5* test_Dict_1
    def test_Dict(self):
        contents = r"""\
    d = {'a' if x else 'b': True,}
    """
        self.make_data(contents)
    #@+node:ekr.20200111191153.1: *5* test_Dict_2
    def test_Dict_2(self):
        contents = r"""\
    d = {}
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.18: *5* test_DictComp
    def test_DictComp(self):
        # leoGlobals.py, line 3028.
        contents = r"""\
    d2 = {val: key for key, val in d}
    """
        self.make_data(contents)
    #@+node:ekr.20200112042410.1: *5* test_ExtSlice
    def test_ExtSlice(self):
        contents = r"""a [1, 2: 3]"""
        self.make_data(contents)
    #@+node:ekr.20191227052446.19: *5* test_ListComp
    def test_ListComp(self):
        # ListComp and comprehension.
        contents = r"""\
    any([p2.isDirty() for p2 in p.subtree()])
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.20: *5* test_NameConstant
    def test_NameConstant(self):
        contents = r"""\
    run(a=None, b=str)
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.21: *5* test_Operator: semicolon
    def test_op_semicolon(self):
        contents = r"""\
    print('c');
    print('d')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.22: *5* test_Operator: semicolon between statements
    def test_op_semicolon2(self):
        contents = r"""\
    a = 1 ; b = 2
    print('a') ; print('b')
    """
        self.make_data(contents)
    #@+node:ekr.20200111194454.1: *5* test_Set
    def test_Set(self):
        contents = """{'a', 'b'}"""
        self.make_data(contents)
    #@+node:ekr.20200111195654.1: *5* test_SetComp
    def test_SetComp(self):
        contents = """aSet = { (x, y) for x in r for y in r if x < y }"""
        self.make_data(contents)
    #@+node:ekr.20191227052446.23: *5* test_UnaryOp
    def test_UnaryOp(self):
        contents = r"""\
    print(-(2))
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.65: *4* TestTOG.f-strings....
    #@+node:ekr.20191227052446.66: *5* test_fstring01: complex Call
    def test_fstring1(self):
        # Line 1177, leoApp.py
        contents = r"""\
    print(
        message = f"line 1: {old_id!r}\n" "line 2\n"
    )
    print('done')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.67: *5* test_fstring02: Ternary
    def test_fstring2(self):
        contents = r"""\
    func(f"{b if not cond1 else ''}")
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.68: *5* test_fstring03: single f-string
    def test_fstring3(self):
        contents = r"""\
    print(f'{7.1}')
    print('end')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.69: *5* test_fstring04: f-string + plain
    def test_fstring4(self):
        contents = r"""\
    print(f'{7.1}' 'p7.2')
    print('end')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.70: *5* test_fstring05: plain + f-string
    def test_fstring5(self):
        contents = r"""\
    print('p1' f'{f2}')
    'end'
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.71: *5* test_fstring06: f-string + fstring
    def test_fstring6(self):
        contents = r"""\
    print(f'{f1}' f'{f2}')
    'end'
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.72: *5* test_fstring07: many
    def test_fstring7(self):
        contents = r"""\
    print('s1', f'{f2}' f'f3' f'{f4}' 's5')
    'end'
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.73: *5* test_fstring08: ternary op
    def test_fstring8(self):
        # leoFind.py line 856
        contents = r"""\
    a = f"{'a' if x else 'b'}"
    f()

    # Pass
    # print(f"{'a' if x else 'b'}")
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.74: *5* test_fstring09: leoFind.py line 856
    def test_fstring9(self):
        contents = r"""\
    func(
        "Isearch"
        f"{' Backward' if True else ''}"
    )
    print('done')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.75: *5* test_fstring10: leoFind.py: line 861
    def test_fstring10(self):
        # leoFind.py: line 861
        contents = r"""\
    one(f"{'B'}" ": ")
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.76: *5* test_fstring11: joins
    def test_fstring11(self):
        contents = r"""\
    print(f'x3{e3+1}y3' f'x4{e4+2}y4')
    print('done')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.77: *6* more
    # Single f-strings.
    # 'p1' ;
    # f'f1' ;
    # f'x1{e1}y1' ;
    # f'x2{e2+1}y2{e2+2}z2' ;

    # Concatentated strings...
    # 'p2', 'p3' ;
    # f'f2' 'f3' ;

    # f'x5{e5+1}y5{e5+1}z5' f'x6{e6+1}y6{e6+1}z6' ;
    #@+node:ekr.20191227052446.78: *5* test_fstring12: joins + 1 f-expr
    def test_fstring12(self):
        contents = r"""\
    print(f'x1{e1}y1', 'p1')
    print(f'x2{e2}y2', f'f2')
    print(f'x3{e3}y3', f'x4{e4}y4')
    print('end')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.79: *5* test_fstring13: joins + 2 f-exprs
    def test_fstring13(self):
        contents = r"""\
    print(f'x1{e1}y1{e2}z1', 'p1')
    print(f'x2{e3}y2{e3}z2', f'f2')
    print(f'x3{e4}y3{e5}z3', f'x4{e6}y4{e7}z4')
    print('end')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.80: *5* test_fstring14: complex, with commas
    def test_fstring14(self):
        contents = r"""\
    print(f"{list(z for z in ('a', 'b', 'c') if z != 'b')}")
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.81: *5* test_fstring15
    def test_fstring15(self):
        contents = r"""\
    print(f"test {a}={2}")
    print('done')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.83: *5* test_fstring16: simple
    def test_fstring16(self):
        contents = r"""\
    'p1' ;
    f'f1' ;
    'done' ;
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.82: *5* test_regex_fstring
    def test_regex_fstring(self):
        # Line 7709, leoGlobals.py
        contents = r'''\
    fr"""{kinds}://[^\s'"]+[\w=/]"""
    '''
        self.make_data(contents)
    #@+node:ekr.20191227052446.32: *4* TestTOG.If...
    #@+node:ekr.20191227052446.33: *5* test_from leoTips.py
    def test_if1(self):
        # Line 93, leoTips.py
        contents = r"""\
    self.make_data(contents)
    unseen = [i for i in range(5) if i not in seen]
    for issue in data:
        for a in aList:
            print('a')
        else:
            print('b')
    if b:
        print('c')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.34: *5* test_if + tuple
    def test_if2(self):
        contents = r"""\
    for i, j in b:
        pass
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.35: *5* test_if + unary op
    def test_if3(self):
        contents = r"""\
    if -(2):
        pass
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.36: *5* test_if, elif
    def test_if4(self):
        contents = r"""\
    if 1:
        print('a')
    elif 2:
        print('b')
    elif 3:
        print('c')
        print('d')
    print('-')
    if 1:
        print('e')
    elif 2:
        print('f')
        print('g')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.37: *5* test_if, elif + 2
    def test_if5(self):
        contents = r"""\
    if 1:
        pass
    elif 2:
        pass
        pass
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.38: *5* test_if, elif, else
    def test_if6(self):
        contents = r"""\
    if (a):
        print('a1')
        print('a2')
    elif b:
        print('b1')
        print('b2')
    else:
        print('c1')
        print('c2')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.39: *5* test_if, else
    def test_if7(self):
        contents = r"""\
    if 1:
        print('a')
    else:
        print('b')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.40: *5* test_if, else, if
    def test_if8(self):
        contents = r"""\
    if 1:
        print('a')
    else:
        if 2:
            print('b')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.41: *5* test_Nested If's
    def test_if9(self):
        contents = r"""\
    if a:
        if b:
            print('b')
    else:
        if d:
            print('d')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.42: *5* test_ternary + if
    def test_if10(self):
        contents = r"""\
    if 1:
        a = 'class' if cond else 'def'
        # find_pattern = prefix + ' ' + word
        print('1')
    else:
        print('2')
    """
        self.make_data(contents)
    #@+node:ekr.20191227145620.1: *4* TestTOG.Miscellaneous...
    #@+node:ekr.20200206041753.1: *5* test_comment_in_set_links
    def test_comment_in_set_links(self):
        contents = """
    def spam():
        # comment
        pass
    """
        self.make_data(contents)
    #@+node:ekr.20200112065944.1: *5* test_ellipsis_1
    def test_ellipsis_1(self):
        contents = """
    def spam():
        ...
    """
        self.make_data(contents)
    #@+node:ekr.20200112070228.1: *5* test_ellipsis_2
    def test_ellipsis_2(self):
        contents = """
    def partial(func: Callable[..., str], *args):
        pass
    """
        self.make_data(contents)
    #@+node:ekr.20191227075951.1: *5* test_end_of_line
    def test_end_of_line(self):
        self.make_data("""# Only a comment.""")
    #@+node:ekr.20191227052446.50: *4* TestTOG.Plain Strings...
    #@+node:ekr.20191227052446.52: *5* test_\x and \o escapes
    def test_escapes(self):
        # Line 4609, leoGlobals.py
        contents = r"""\
    print("\x7e" "\0777") # tilde.
    print('done')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.53: *5* test_backslashes in docstring
    def test_backslashes(self):
        # leoGlobals.py.
        contents = r'''\
    class SherlockTracer:
        """before\\after"""
    '''
        self.make_data(contents)
    #@+node:ekr.20191227052446.54: *5* test_bs/nl
    def test_bs_nl(self):
        contents = r"""\
    print('hello\
    world')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.55: *5* test_bytes bs-x
    def test_bytes(self):
        # Line 201, leoApp.py
        contents = r"""\
    print(b'\xfe')
    print('done')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.56: *5* test_empty string
    def test_empyt_string(self):
        contents = r"""\
    self.s = ''
    self.i = 0
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.57: *5* test_escaped string delims
    def test_escaped_delims(self):
        contents = r"""\
    print("a\"b")
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.58: *5* test_escaped strings
    def test_escaped_strings(self):
        contents = r"""\
    f1(a='\b', b='\n', t='\t')
    f2(f='\f', r='\r', v='\v')
    f3(bs='\\')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.59: *5* test_f-string join
    def test_fstring_join(self):
        # The first newline causes the fail.
        contents = r"""\
    print(f"a {old_id!r}\n" "b\n")
    print('done')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.64: *5* test_potential_fstring
    def test_potential_fstring(self):
        contents = r"""\
    print('test %s=%s'%(a, 2))
    print('done')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.60: *5* test_raw docstring
    def test_raw_docstring(self):
        contents = r'''\
    # Line 1619 leoFind.py
    print(r"""DS""")
    '''
        self.make_data(contents)
    #@+node:ekr.20191227052446.61: *5* test_raw escaped strings
    def test_raw_escapes(self):
        contents = r"""\
    r1(a=r'\b', b=r'\n', t=r'\t')
    r2(f=r'\f', r=r'\r', v=r'\v')
    r3(bs=r'\\')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.62: *5* test_single quote
    def test_single_quote(self):
        # leoGlobals.py line 806.
        contents = r"""\
    print('"')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.63: *5* test_string concatenation_1
    def test_concatenation_1(self):
        contents = r"""\
    print('a' 'b')
    print('c')
    """
        self.make_data(contents)
    #@+node:ekr.20200111042825.1: *5* test_string_concatenation_2
    def test_string_concatenation_2(self):
        # Crash in leoCheck.py.
        contents = """return self.Type('error', 'no member %s' % ivar)"""
        self.make_data(contents)
    #@+node:ekr.20191227052446.43: *4* TestTOG.Statements...
    #@+node:ekr.20200112075707.1: *5* test_AnnAssign
    def test_AnnAssign(self):
        contents = """x: int = 0"""
        self.make_data(contents)
    #@+node:ekr.20200112071833.1: *5* test_AsyncFor
    def test_AsyncFor(self):
        # This may require Python 3.7.
        contents = """\
    async def commit(session, data):
        async for z in session.transaction():
            await z(data)
        else:
            print('oops')
    """
        self.make_data(contents)
    #@+node:ekr.20200111175043.1: *5* test_AsyncFunctionDef
    def test_AsyncFunctionDef(self):
        contents = """\
    @my_decorator
    async def count() -> 42:
        print("One")
        await asyncio.sleep(1)
    """
        self.make_data(contents)
    #@+node:ekr.20200112073151.1: *5* test_AsyncWith
    def test_AsyncWith(self):
        contents = """\
    async def commit(session, data):
        async with session.transaction():
            await session.update(data)
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.44: *5* test_Call
    def test_Call(self):
        contents = """func(a, b, one='one', two=2, three=4+5, *args, **kwargs)"""
        # contents = """func(*args, **kwargs)"""
    # f1(a,b=2)
    # f2(1 + 2)
    # f3(arg, *args, **kwargs)
    # f4(a='a', *args, **kwargs)
        self.make_data(contents)
    #@+node:ekr.20200206040732.1: *5* test_Delete
    def test_Delete(self):

        # Coverage test for spaces
        contents = """del x"""
        self.make_data(contents)
    #@+node:ekr.20200111175335.1: *5* test_For
    def test_For(self):
        contents = r"""\
    for a in b:
        pass
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.45: *5* test_Global
    def test_Global(self):
        # Line 1604, leoGlobals.py
        contents = r"""
    def spam():
        global gg
        print('')
    """
        self.make_data(contents)
    #@+node:ekr.20200111200424.1: *5* test_ImportFrom
    def test_ImportFrom(self):
        contents = r"""from a import b as c"""
        self.make_data(contents)
    #@+node:ekr.20210318174705.1: *5* test_ImportFromStar
    def test_ImportFromStar(self):
        contents = r"""from sys import *"""
        self.make_data(contents)
    #@+node:ekr.20200206040424.1: *5* test_Lambda
    def test_Lambda(self):

        # Coverage test for spaces
        contents = """f = lambda x: x"""
        self.make_data(contents)
    #@+node:ekr.20220329095904.1: *5* test_Match
    def test_Match(self):

        if py_version < (3, 10):  # pragma: no cover
            self.skipTest('Require python 3.10')
        contents = r"""\
    match node:
        # Passed...
        case 1: pass
        case (2, 3): pass
        case BinOp("+", a, BinOp("*", b, c)): pass
        case {"text": message, "color": c}: pass
        case 401 | 403 | 404: pass
        case xyzzy if a > 1: pass
        case {"sound": _, "format": _}: pass
        case BinOp2("+", a, BinOp("*", d = 2)): pass
        case BinOp2("-", d, e = 2): pass
        case {"pat1": 2, **rest}: pass
        case _: pass
        case (4, 5, *rest): pass
        case [6, 5, *rest]: pass
        case ['a'|'b' as ab, c]: pass
        case True: pass
        case False: pass
        case None: pass
        case True | False | None: pass
        case True, False, None: pass  # A tuple!
    """
        try:
            # self.debug_list.append('contents')
            # self.debug_list.append('tokens')
            # self.debug_list.append('tree')
            # self.debug_list.append('full-traceback')
            self.make_data(contents)
        finally:
            self.debug_list = []
    #@+node:ekr.20200111200640.1: *5* test_Nonlocal
    def test_Nonlocal(self):
        contents = r"""nonlocal name1, name2"""
        self.make_data(contents)
    #@+node:ekr.20220224120239.1: *5* test_Raise
    def test_Raise(self):
        contents = "raise ImportError from None"
        self.make_data(contents)
    #@+node:ekr.20191227052446.46: *5* test_Try
    def test_Try(self):
        contents = r"""\
    try:
        print('a1')
        print('a2')
    except ImportError:
        print('b1')
        print('b2')
    except SyntaxError:
        print('c1')
        print('c2')
    finally:
        print('d1')
        print('d2')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.47: *5* test_TryExceptElse
    def test_Try2(self):
        # Line 240: leoDebugger.py
        contents = r"""\
    try:
        print('a')
    except ValueError:
        print('b')
    else:
        print('c')
    """
        self.make_data(contents)
    #@+node:ekr.20200206041336.1: *5* test_While
    def test_While(self):
        contents = r"""\
    while f():
        print('continue')
    else:
        print('done')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.48: *5* test_With
    def test_With(self):
        # leoGlobals.py, line 1785.
        contents = r"""\
    with open(fn) as f:
        pass
    """
        self.make_data(contents)
    #@+node:ekr.20200206041611.1: *5* test_Yield
    def test_Yield(self):
        contents = r"""\
    def gen_test():
        yield self.gen_token('newline', '\n')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.49: *5* test_YieldFrom
    def test_YieldFrom(self):
        # Line 1046, leoAst.py
        contents = r"""\
    def gen_test():
        self.node = tree
        yield from self.gen_token('newline', '\n')
        print('done')
    """
        self.make_data(contents)
    #@+node:ekr.20191228193740.1: *4* TestTOG.test_aa && zz
    def test_aaa(self):
        """The first test."""
        g.total_time = get_time()

    def test_zzz(self):
        """The last test."""
        t2 = get_time()
        self.update_times('90: TOTAL', t2 - g.total_time)
        # self.dump_stats()
    #@-others
#@+node:ekr.20210902074155.1: ** Test classes...
#@+node:ekr.20200122161530.1: *3* class Optional_TestFiles (BaseTest)
class Optional_TestFiles(BaseTest):
    """
    Tests for the TokenOrderGenerator class that act on files.

    These are optional tests. They take a long time and are not needed
    for 100% coverage.

    All of these tests failed at one time.
    """
    #@+others
    #@+node:ekr.20200726145235.2: *4* TestFiles.test_leoApp
    def test_leoApp(self):

        self.make_file_data('leoApp.py')
    #@+node:ekr.20200726145235.1: *4* TestFiles.test_leoAst
    def test_leoAst(self):

        self.make_file_data('leoAst.py')
    #@+node:ekr.20200726145333.1: *4* TestFiles.test_leoDebugger
    def test_leoDebugger(self):

        self.make_file_data('leoDebugger.py')
    #@+node:ekr.20200726145333.2: *4* TestFiles.test_leoFind
    def test_leoFind(self):

        self.make_file_data('leoFind.py')
    #@+node:ekr.20200726145333.3: *4* TestFiles.test_leoGlobals
    def test_leoGlobals(self):

        self.make_file_data('leoGlobals.py')
    #@+node:ekr.20200726145333.4: *4* TestFiles.test_leoTips
    def test_leoTips(self):

        self.make_file_data('leoTips.py')
    #@+node:ekr.20200726145735.1: *4* TestFiles.test_runLeo
    def test_runLeo(self):

        self.make_file_data('runLeo.py')
    #@+node:ekr.20200115162419.1: *4* TestFiles.compare_tog_vs_asttokens
    def compare_tog_vs_asttokens(self):  # pragma: no cover
        """Compare asttokens token lists with TOG token lists."""
        if not asttokens:
            self.skipTest('requires asttokens')
        # Define TestToken class and helper functions.
        stack: List[ast.AST] = []
        #@+others
        #@+node:ekr.20200124024159.2: *5* class TestToken (internal)
        class TestToken:
            """A patchable representation of the 5-tuples created by tokenize and used by asttokens."""

            def __init__(self, kind, value):
                self.kind = kind
                self.value = value
                self.node_list: List[ast.AST] = []

            def __str__(self):
                tokens_s = ', '.join([z.__class__.__name__ for z in self.node_list])
                return f"{self.kind:14} {self.value:20} {tokens_s!s}"

            __repr__ = __str__
        #@+node:ekr.20200124024159.3: *5* function: atok_name
        def atok_name(token):
            """Return a good looking name for the given 5-tuple"""
            return token_module.tok_name[token[0]].lower()  # type:ignore
        #@+node:ekr.20200124024159.4: *5* function: atok_value
        def atok_value(token):
            """Print a good looking value for the given 5-tuple"""
            return token.string if atok_name(token) == 'string' else repr(token.string)
        #@+node:ekr.20200124024159.5: *5* function: dump_token
        def dump_token(token):
            node_list = list(set(getattr(token, 'node_set', [])))
            node_list = sorted([z.__class__.__name__ for z in node_list])
            return f"{token.index:2} {atok_name(token):12} {atok_value(token):20} {node_list}"
        #@+node:ekr.20200124024159.6: *5* function: postvisit
        def postvisit(node, par_value, value):
            nonlocal stack
            stack.pop()
            return par_value or []
        #@+node:ekr.20200124024159.7: *5* function: previsit
        def previsit(node, par_value):
            nonlocal stack
            if isinstance(node, ast.Module):
                stack = []
            if stack:
                parent = stack[-1]
                children: List[ast.AST] = getattr(parent, 'children', [])
                parent.children = children + [node]  # type:ignore
                node.parent = parent
            else:
                node.parent = None
                node.children = []
            stack.append(node)
            return par_value, []
        #@-others
        directory = r'c:\Repos\leo-editor\leo\core'
        filename = 'leoAst.py'
        filename = os.path.join(directory, filename)
        # A fair comparison omits the read time.
        t0 = get_time()
        contents = read_file(filename)
        t1 = get_time()
        # Part 1: TOG.
        tog = TokenOrderGenerator()
        tog.filename = filename
        tokens = make_tokens(contents)
        tree = parse_ast(contents)
        tog.create_links(tokens, tree)
        tog.balance_tokens(tokens)
        t2 = get_time()
        # Part 2: Create asttokens data.
        atok = asttokens.ASTTokens(contents, parse=True, filename=filename)
        t3 = get_time()
        # Create a patchable list of TestToken objects.
        tokens = [TestToken(atok_name(z), atok_value(z)) for z in atok.tokens]  # type:ignore
        # Inject parent/child links into nodes.
        asttokens.util.visit_tree(atok.tree, previsit, postvisit)
        # Create token.token_list for each token.
        for node in asttokens.util.walk(atok.tree):
            # Inject node into token.node_list
            for ast_token in atok.get_tokens(node, include_extra=True):
                i = ast_token.index
                token = tokens[i]
                token.node_list.append(node)
        t4 = get_time()
        if 1:
            print(
                f"       read: {t1-t0:5.3f} sec.\n"
                f"        TOG: {t2-t1:5.3f} sec.\n"
                f"asttokens 1: {t3-t2:5.3f} sec.\n"
                f"asttokens 2: {t4-t3:5.3f} sec.\n")
        if 0:
            print('===== asttokens =====\n')
            for node in asttokens.util.walk(tree):
                print(f"{node.__class__.__name__:>10} {atok.get_text(node)!s}")
    #@-others
#@+node:ekr.20191229083512.1: *3* class TestFstringify (BaseTest)
class TestFstringify(BaseTest):
    """Tests for the TokenOrderGenerator class."""
    #@+others
    #@+node:ekr.20200111043311.1: *4* Bugs...
    #@+node:ekr.20210318054321.1: *5* TestFstringify.test_bug_1851
    def test_bug_1851(self):
        # leoCheck.py.
        contents = """\
    from dataclasses import dataclass

    @dataclass(frozen=True)
    class TestClass:
        value: str
        start: int
        end: int

    f = TestClass('abc', 0, 10)
    """
        contents, tokens, tree = self.make_data(contents)
        expected = textwrap.dedent(contents).rstrip() + '\n'
        results = self.fstringify(contents, tokens, tree)
        self.assertEqual(results, expected)
    #@+node:ekr.20200111043311.2: *5* TestFstringify.test_crash_1
    def test_crash_1(self):
        # leoCheck.py.
        contents = """return ('error', 'no member %s' % ivar)"""
        expected = """return ('error', f"no member {ivar}")\n"""
        contents, tokens, tree = self.make_data(contents)
        results = self.fstringify(contents, tokens, tree)
        self.assertEqual(results, expected)
    #@+node:ekr.20200111075114.1: *5* TestFstringify.test_crash_2
    def test_crash_2(self):
        # leoCheck.py, line 1704.
        # format =
            # 'files: %s lines: %s chars: %s classes: %s\n'
            # 'defs: %s calls: %s undefined calls: %s returns: %s'
        # )
        contents = r"""'files: %s\n' 'defs: %s'"""
        expected = contents + '\n'
        contents, tokens, tree = self.make_data(contents)
        results = self.fstringify(contents, tokens, tree)
        self.assertEqual(results, expected)
    #@+node:ekr.20200214155156.1: *4* TestFstringify.show_message
    def show_message(self):  # pragma: no cover
        """Separate test of fs.message."""
        fs = Fstringify()
        fs.filename = 'test_file.py'
        fs.line_number = 42
        fs.line = 'The test line\n'
        fs.silent = False
        # Test message.
        fs.message(
            "Test:\n"
            "<  Left align\n"
            ":Colon: align\n"
            ">  Right align\n"
            "   Default align")
        #
        # change_quotes...
        fs.message("can't create f-fstring: no lt_s!")
        lt_s = "lt_s"
        delim = 'Delim'
        token = Token('Kind', 'Value')
        fs.message(
            f"unexpected token: {token.kind} {token.value}\n"
            f"            lt_s: {lt_s!r}")
        fs.message(
            f"can't create f-fstring: {lt_s!r}\n"
            f":    conflicting delim: {delim!r}")
        fs.message(
            f"can't create f-fstring: {lt_s!r}\n"
            f":backslash in {{expr}}: {delim!r}")
        # Check newlines...
        fs.message(
            f"  can't create f-fstring: {lt_s!r}\n"
            f":curly bracket underflow:")
        fs.message(
            f"      can't create f-fstring: {lt_s!r}\n"
            f":string contains a backslash:")
        fs.message(
            f" can't create f-fstring: {lt_s!r}\n"
            f":unclosed curly bracket:")
        # Make fstring
        before, after = 'Before', 'After'
        fs.message(
            f"trace:\n"
            f":from: {before!s}\n"
            f":  to: {after!s}")
    #@+node:ekr.20200106163535.1: *4* TestFstringify.test_braces
    def test_braces(self):

        # From pr.construct_stylesheet in leoPrinting.py
        contents = """'h1 {font-family: %s}' % (family)"""
        expected = """f"h1 {{font-family: {family}}}"\n"""
        contents, tokens, tree = self.make_data(contents)
        results = self.fstringify(contents, tokens, tree)
        self.assertEqual(results, expected)
    #@+node:ekr.20200217171334.1: *4* TestFstringify.test_backslash_in_expr
    def test_backslash_in_expr(self):
        # From get_flake8_config.
        contents = r"""print('aaa\n%s' % ('\n'.join(dir_table)))"""
        expected = contents.rstrip() + '\n'
        contents, tokens, tree = self.make_data(contents)
        results = self.fstringify(contents, tokens, tree, silent=True)
        self.assertEqual(results, expected)
    #@+node:ekr.20191230150653.1: *4* TestFstringify.test_call_in_rhs
    def test_call_in_rhs(self):

        contents = """'%s' % d()"""
        expected = """f"{d()}"\n"""
        contents, tokens, tree = self.make_data(contents)
        results = self.fstringify(contents, tokens, tree)
        self.assertEqual(results, expected)
    #@+node:ekr.20200104045907.1: *4* TestFstringify.test_call_in_rhs_2
    def test_call_in_rhs_2(self):

        # From LM.traceSettingsDict
        contents = """print('%s' % (len(d.keys())))"""
        expected = """print(f"{len(d.keys())}")\n"""
        contents, tokens, tree = self.make_data(contents)
        results = self.fstringify(contents, tokens, tree)
        self.assertEqual(results, expected)
    #@+node:ekr.20200105073155.1: *4* TestFstringify.test_call_with_attribute
    def test_call_with_attribute(self):

        contents = """g.blue('wrote %s' % p.atShadowFileNodeName())"""
        expected = """g.blue(f"wrote {p.atShadowFileNodeName()}")\n"""
        contents, tokens, tree = self.make_data(contents)
        results = self.fstringify(contents, tokens, tree)
        self.assertEqual(results, expected)
    #@+node:ekr.20200122035055.1: *4* TestFstringify.test_call_with_comments
    def test_call_with_comments(self):

        contents = """\
    print('%s in %5.2f sec' % (
        "done", # message
        2.9, # time
    )) # trailing comment"""

        expected = """\
    print(f'{"done"} in {2.9:5.2f} sec') # trailing comment
    """
        contents, tokens, tree = self.make_data(contents)
        expected = textwrap.dedent(expected).rstrip() + '\n'
        results = self.fstringify(contents, tokens, tree)
        self.assertEqual(results, expected)
    #@+node:ekr.20200206173126.1: *4* TestFstringify.test_change_quotes
    def test_change_quotes(self):

        contents = """ret = '[%s]' % ','.join([show(z) for z in arg])"""
        expected = """ret = f"[{','.join([show(z) for z in arg])}]"\n"""
        contents, tokens, tree = self.make_data(contents)
        results = self.fstringify(contents, tokens, tree)
        self.assertEqual(results, expected)
    #@+node:ekr.20200101060616.1: *4* TestFstringify.test_complex_rhs
    def test_complex_rhs(self):
        # From LM.mergeShortcutsDicts.
        contents = (
            """g.trace('--trace-binding: %20s binds %s to %s' % ("""
            """   c.shortFileName(), binding, d.get(binding) or []))""")
        expected = (
            """g.trace(f"--trace-binding: {c.shortFileName():20} """
            """binds {binding} to {d.get(binding) or []}")\n""")
        contents, tokens, tree = self.make_data(contents)
        results = self.fstringify(contents, tokens, tree)
        self.assertEqual(results, expected)
    #@+node:ekr.20200206174208.1: *4* TestFstringify.test_function_call
    def test_function_call(self):

        contents = """mods = ''.join(['%s+' % z.capitalize() for z in self.mods])"""
        expected = """mods = ''.join([f"{z.capitalize()}+" for z in self.mods])\n"""
        contents, tokens, tree = self.make_data(contents)
        results = self.fstringify(contents, tokens, tree)
        self.assertEqual(results, expected)
    #@+node:ekr.20200106085608.1: *4* TestFstringify.test_ImportFrom
    def test_ImportFrom(self):

        table = (
            """from .globals import a, b""",
            """from ..globals import x, y, z""",
            """from . import j""",
        )
        for contents in table:
            contents, tokens, tree = self.make_data(contents)
            results = self.fstringify(contents, tokens, tree)
            self.assertEqual(results, contents)
    #@+node:ekr.20200106042452.1: *4* TestFstringify.test_ListComp
    def test_ListComp(self):

        table = (
            """replaces = [L + c + R[1:] for L, R in splits if R for c in letters]""",
            """[L for L in x for c in y]""",
            """[L for L in x for c in y if L if not c]""",
        )
        for contents in table:
            contents, tokens, tree = self.make_data(contents)
            results = self.fstringify(contents, tokens, tree)
            expected = contents
            self.assertEqual(results, expected)
    #@+node:ekr.20200112163031.1: *4* TestFstringify.test_munge_spec
    def test_munge_spec(self):

        # !head:tail or :tail
        table = (
            ('+1s', '', '+1'),
            ('-2s', '', '>2'),
            ('3s', '', '3'),
            ('4r', 'r', '4'),
        )
        for spec, e_head, e_tail in table:
            head, tail = Fstringify().munge_spec(spec)
            assert(head, tail) == (e_head, e_tail), (
                f"\n"
                f"         spec: {spec}\n"
                f"expected head: {e_head}\n"
                f"     got head: {head}\n"
                f"expected tail: {e_tail}\n"
                f"     got tail: {tail}\n")
    #@+node:ekr.20200104042705.1: *4* TestFstringify.test_newlines
    def test_newlines(self):

        contents = r"""\
    print("hello\n")
    print('world\n')
    print("hello\r\n")
    print('world\r\n')
    """
        contents, tokens, tree = self.make_data(contents)
        expected = contents
        results = self.fstringify(contents, tokens, tree)
        self.assertEqual(results, expected)
    #@+node:ekr.20191230183652.1: *4* TestFstringify.test_parens_in_rhs
    def test_parens_in_rhs(self):

        contents = """print('%20s' % (ivar), val)"""
        expected = """print(f"{ivar:20}", val)\n"""
        contents, tokens, tree = self.make_data(contents)
        results = self.fstringify(contents, tokens, tree)
        self.assertEqual(results, expected)
    #@+node:ekr.20200106091740.1: *4* TestFstringify.test_single_quotes
    def test_single_quotes(self):

        table = (
            # Case 0.
            ("""print('%r "default"' % style_name)""",
             """print(f'{style_name!r} "default"')\n"""),
            # Case 1.
            ("""print('%r' % "val")""",
             """print(f'{"val"!r}')\n"""),
            # Case 2.
            ("""print("%r" % "val")""",
             """print(f'{"val"!r}')\n"""),
        )
        for i, data in enumerate(table):
            contents, expected = data
            description = f"test_single_quotes: {i}"
            contents, tokens, tree = self.make_data(contents, description)
            results = self.fstringify(contents, tokens, tree, filename=description)
            self.assertEqual(results, expected, msg=i)
    #@+node:ekr.20200214094938.1: *4* TestFstringify.test_switch_quotes
    def test_switch_quotes(self):
        table = (
            (
                """print('%r' % 'style_name')""",
                """print(f"{'style_name'!r}")\n""",
            ),
        )
        for i, data in enumerate(table):
            contents, expected = data
            description = f"test_single_quotes: {i}"
            contents, tokens, tree = self.make_data(contents, description)
            results = self.fstringify(contents, tokens, tree, filename=description)
            self.assertEqual(results, expected, msg=i)
    #@+node:ekr.20200206173725.1: *4* TestFstringify.test_switch_quotes_2
    def test_switch_quotes_2(self):

        contents = """
    g.es('%s blah blah' % (
        g.angleBrackets('*')))
    """
        expected = """g.es(f"{g.angleBrackets(\'*\')} blah blah")\n"""
        contents, tokens, tree = self.make_data(contents)
        results = self.fstringify(contents, tokens, tree)
        self.assertEqual(results, expected)
    #@+node:ekr.20200206173628.1: *4* TestFstringify.test_switch_quotes_3
    def test_switch_quotes_3(self):

        contents = """print('Test %s' % 'one')"""
        expected = """print(f"Test {'one'}")\n"""
        contents, tokens, tree = self.make_data(contents)
        results = self.fstringify(contents, tokens, tree)
        self.assertEqual(results, expected)
    #@+node:ekr.20200219125956.1: *4* TestFstringify.test_switch_quotes_fail
    def test_switch_quotes_fail(self):

        contents = """print('Test %s %s' % ('one', "two"))"""
        contents, tokens, tree = self.make_data(contents)
        expected = contents
        results = self.fstringify(contents, tokens, tree)
        self.assertEqual(results, expected)
    #@-others
#@+node:ekr.20200107174645.1: *3* class TestOrange (BaseTest)
class TestOrange(BaseTest):
    """
    Tests for the Orange class.

    **Important**: All unit tests assume that black_mode is False.
                   That is, unit tests assume that no blank lines
                   are ever inserted or deleted.
    """
    #@+others
    #@+node:ekr.20200115201823.1: *4* TestOrange.blacken
    def blacken(self, contents, line_length=None):
        """Return the results of running black on contents"""
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
    #@+node:ekr.20230115150916.1: *4* TestOrange.test_annotations
    def test_annotations(self):

        table = (
        # Case 0.
        '''\
    def annotated_f(s: str = None, x=None) -> None:
        pass
    ''',
        )
        for i, contents in enumerate(table):
            contents, tokens, tree = self.make_data(contents)
            expected = self.blacken(contents).rstrip() + '\n'
            results = self.beautify(contents, tokens, tree)
            self.assertEqual(results, expected)

    #@+node:ekr.20200219114415.1: *4* TestOrange.test_at_doc_part
    def test_at_doc_part(self):

        line_length = 40  # For testing.
        contents = """\
    #@+at Line 1
    # Line 2
    #@@c

    print('hi')
    """
        contents, tokens, tree = self.make_data(contents)
        expected = contents.rstrip() + '\n'
        results = self.beautify(contents, tokens, tree,
            max_join_line_length=line_length,
            max_split_line_length=line_length,
        )
        self.assertEqual(results, expected)
    #@+node:ekr.20200116102345.1: *4* TestOrange.test_backslash_newline
    def test_backslash_newline(self):
        """
        This test is necessarily different from black, because orange doesn't
        delete semicolon tokens.
        """
        contents = r"""
    print(a);\
    print(b)
    print(c); \
    print(d)
    """
        contents, tokens, tree = self.make_data(contents)
        expected = contents.rstrip() + '\n'
        # expected = self.blacken(contents).rstrip() + '\n'
        results = self.beautify(contents, tokens, tree)
        self.assertEqual(results, expected)
    #@+node:ekr.20200219145639.1: *4* TestOrange.test_blank_lines_after_function
    def test_blank_lines_after_function(self):

        contents = """\
    # Comment line 1.
    # Comment line 2.

    def spam():
        pass
        # Properly indented comment.

    # Comment line3.
    # Comment line4.
    a = 2
    """
        contents, tokens, tree = self.make_data(contents)
        expected = contents
        results = self.beautify(contents, tokens, tree)
        self.assertEqual(results, expected)
    #@+node:ekr.20200220050758.1: *4* TestOrange.test_blank_lines_after_function_2
    def test_blank_lines_after_function_2(self):

        contents = """\
    # Leading comment line 1.
    # Leading comment lines 2.

    def spam():
        pass

    # Trailing comment line.
    a = 2
    """
        contents, tokens, tree = self.make_data(contents)
        expected = contents
        results = self.beautify(contents, tokens, tree)
        self.assertEqual(results, expected)
    #@+node:ekr.20200220053212.1: *4* TestOrange.test_blank_lines_after_function_3
    def test_blank_lines_after_function_3(self):

        # From leoAtFile.py.
        contents = r"""\
    def writeAsisNode(self, p):
        print('1')

        def put(s):
            print('2')

        # Trailing comment 1.
        # Trailing comment 2.
        print('3')
    """
        contents, tokens, tree = self.make_data(contents)
        expected = contents
        results = self.beautify(contents, tokens, tree)
        self.assertEqual(results, expected)
    #@+node:ekr.20200228074455.1: *4* TestOrange.test_bug_1429
    def test_bug_1429(self):

        contents = r'''\
    def get_semver(tag):
        """bug 1429 docstring"""
        try:
            import semantic_version
            version = str(semantic_version.Version.coerce(tag, partial=True))
                # tuple of major, minor, build, pre-release, patch
                # 5.6b2 --> 5.6-b2
        except(ImportError, ValueError) as err:
            print('\n', err)
            print("""*** Failed to parse Semantic Version from git tag '{0}'.
            Expecting tag name like '5.7b2', 'leo-4.9.12', 'v4.3' for releases.
            This version can't be uploaded to PyPi.org.""".format(tag))
            version = tag
        return version
    '''
        contents, tokens, tree = self.make_data(contents)
        expected = contents.rstrip() + '\n'
        results = self.beautify(contents, tokens, tree,
            max_join_line_length=0, max_split_line_length=0)
        self.assertEqual(results, expected)
    #@+node:ekr.20210318055702.1: *4* TestOrange.test_bug_1851
    def test_bug_1851(self):

        contents = r'''\
    def foo(a1):
        pass
    '''
        contents, tokens, tree = self.make_data(contents)
        expected = contents.rstrip() + '\n'
        results = self.beautify(contents, tokens, tree,
            max_join_line_length=0, max_split_line_length=0)
        self.assertEqual(results, expected)
    #@+node:ekr.20200209152745.1: *4* TestOrange.test_comment_indented
    def test_comment_indented(self):

        line_length = 40  # For testing.
        table = (
    """\
    if 1:
        pass
            # An indented comment.
    """,
    """\
    table = (
        # Indented comment.
    )
    """
        )

        fails = 0
        for contents in table:
            contents, tokens, tree = self.make_data(contents)
            expected = contents
            if 0:
                dump_contents(contents)
                dump_tokens(tokens)
                # dump_tree(tokens, tree)
            results = self.beautify(contents, tokens, tree,
                max_join_line_length=line_length,
                max_split_line_length=line_length,
            )
            message = (
                f"\n"
                f"  contents: {contents!r}\n"
                f"  expected: {expected!r}\n"
                f"       got: {results!r}")
            if results != expected:  # pragma: no cover
                fails += 1
                print(f"Fail: {fails}\n{message}")
        assert not fails, fails
    #@+node:ekr.20230117043931.1: *4* TestOrange.test_comment_space_after_delim
    def test_comment_space_after_delim(self):

        line_length = 40  # For testing.
        table = (
            # Test 1.
            (
                """#No space after delim.\n""",
                """# No space after delim.\n""",
            ),
            # Test 2.  Don't change bang lines.
            (
                """#! /usr/bin/env python\n""",
                """#! /usr/bin/env python\n""",
            ),
            # Test 3.  Don't change ### comments.
            (
                """### To do.\n""",
                """### To do.\n""",
            ),
        )
        fails = 0
        for contents, expected in table:
            contents, tokens, tree = self.make_data(contents)
            if 0:
                dump_contents(contents)
                dump_tokens(tokens)
                # dump_tree(tokens, tree)
            results = self.beautify(contents, tokens, tree,
                max_join_line_length=line_length,
                max_split_line_length=line_length,
            )
            message = (
                f"\n"
                f"  contents: {contents!r}\n"
                f"  expected: {expected!r}\n"
                f"       got: {results!r}")
            if results != expected:  # pragma: no cover
                fails += 1
                print(f"Fail: {fails}\n{message}")
        assert not fails, fails
    #@+node:ekr.20200210120455.1: *4* TestOrange.test_decorator
    def test_decorator(self):

        table = (
        # Case 0.
        """\
    @my_decorator(1)
    def func():
        pass
    """,
        # Case 1.
        """\
    if 1:
        @my_decorator
        def func():
            pass
    """,
        # Case 2.
        '''\
    @g.commander_command('promote')
    def promote(self, event=None, undoFlag=True):
        """Make all children of the selected nodes siblings of the selected node."""
    ''',
        )
        for i, contents in enumerate(table):
            contents, tokens, tree = self.make_data(contents)
            expected = contents
            results = self.beautify(contents, tokens, tree)
            if results != expected:
                g.trace('Fail:', i)  # pragma: no cover
            self.assertEqual(results, expected)
    #@+node:ekr.20200211094614.1: *4* TestOrange.test_dont_delete_blank_lines
    def test_dont_delete_blank_lines(self):

        line_length = 40  # For testing.
        contents = """\
    class Test:

        def test_func():

            pass

        a = 2
    """
        contents, tokens, tree = self.make_data(contents)
        expected = contents.rstrip() + '\n'
        results = self.beautify(contents, tokens, tree,
            max_join_line_length=line_length,
            max_split_line_length=line_length,
        )
        self.assertEqual(results, expected)
    #@+node:ekr.20200116110652.1: *4* TestOrange.test_function_defs
    def test_function_defs(self):

        table = (
        # Case 0.
        """\
    def f1(a=2 + 5):
        pass
    """,
        # Case 2
         """\
    def f1():
        pass
    """,
        # Case 3.
        """\
    def f1():
        pass
    """,
        # Case 4.
        '''\
    def should_kill_beautify(p):
        """Return True if p.b contains @killbeautify"""
        return 'killbeautify' in g.get_directives_dict(p)
    ''',
        )
        for i, contents in enumerate(table):
            contents, tokens, tree = self.make_data(contents)
            expected = self.blacken(contents).rstrip() + '\n'
            results = self.beautify(contents, tokens, tree)
            self.assertEqual(results, expected)
    #@+node:ekr.20200116104031.1: *4* TestOrange.test_join_and_strip_condition
    def test_join_and_strip_condition(self):

        contents = """\
    if (
        a == b or
        c == d
    ):
        pass
    """
        expected = """\
    if (a == b or c == d):
        pass
    """
        contents, tokens, tree = self.make_data(contents)
        expected = textwrap.dedent(expected)
        # Black also removes parens, which is beyond our scope at present.
            # expected = self.blacken(contents, line_length=40)
        results = self.beautify(contents, tokens, tree)
        self.assertEqual(results, expected)
    #@+node:ekr.20200208041446.1: *4* TestOrange.test_join_leading_whitespace
    def test_join_leading_whitespace(self):

        line_length = 40  # For testing.
        table = (
                            #1234567890x1234567890x1234567890x1234567890x
    """\
    if 1:
        print('4444',
            '5555')
    """,
    """\
    if 1:
        print('4444', '5555')\n""",
        )
        fails = 0
        for contents in table:
            contents, tokens, tree = self.make_data(contents)
            if 0:
                dump_contents(contents)
                dump_tokens(tokens)
                # dump_tree(tokens, tree)
            expected = contents
            # expected = self.blacken(contents, line_length=line_length)
            results = self.beautify(contents, tokens, tree,
                max_join_line_length=line_length,
                max_split_line_length=line_length,
            )
            message = (
                f"\n"
                f"  contents: {contents!r}\n"
                f"  expected: {expected!r}\n"
                f"       got: {results!r}")
            if results != expected:  # pragma: no cover
                fails += 1
                print(f"Fail: {fails}\n{message}")
        assert not fails, fails
    #@+node:ekr.20200121093134.1: *4* TestOrange.test_join_lines
    def test_join_lines(self):

        # Except where noted, all entries are expected values....
        line_length = 40  # For testing.
        table = (
            #1234567890x1234567890x1234567890x1234567890x
            """print('4444',\n    '5555')""",
            """print('4444', '5555')\n""",
        )
        fails = 0
        for contents in table:
            contents, tokens, tree = self.make_data(contents)
            if 0:
                dump_contents(contents)
                dump_tokens(tokens)
                # dump_tree(tokens, tree)
            expected = contents
            results = self.beautify(contents, tokens, tree,
                max_join_line_length=line_length,
                max_split_line_length=line_length,
            )
            message = (
                f"\n"
                f"  contents: {contents!r}\n"
                f"  expected: {expected!r}\n"
                f"    orange: {results!r}")
            if results != expected:  # pragma: no cover
                fails += 1
                print(f"Fail: {fails}\n{message}")
        self.assertEqual(fails, 0)
    #@+node:ekr.20200210051900.1: *4* TestOrange.test_join_suppression
    def test_join_suppression(self):

        contents = """\
    class T:
        a = 1
        print(
           a
        )
    """
        expected = """\
    class T:
        a = 1
        print(a)
    """
        contents, tokens, tree = self.make_data(contents)
        expected = textwrap.dedent(expected)
        results = self.beautify(contents, tokens, tree)
        self.assertEqual(results, expected)
    #@+node:ekr.20200207093606.1: *4* TestOrange.test_join_too_long_lines
    def test_join_too_long_lines(self):

        # Except where noted, all entries are expected values....
        line_length = 40  # For testing.
        table = (
                            #1234567890x1234567890x1234567890x1234567890x
            (
                """print('aaaaaaaaaaaa',\n    'bbbbbbbbbbbb', 'cccccccccccccccc')""",
                """print('aaaaaaaaaaaa',\n    'bbbbbbbbbbbb', 'cccccccccccccccc')\n""",
            ),
        )
        fails = 0
        for contents, expected in table:
            contents, tokens, tree = self.make_data(contents)
            if 0:
                dump_contents(contents)
                dump_tokens(tokens)
                # dump_tree(tokens, tree)
            results = self.beautify(contents, tokens, tree,
                max_join_line_length=line_length,
                max_split_line_length=line_length,
            )
            message = (
                f"\n"
                f"  contents: {contents!r}\n"
                f"  expected: {expected!r}\n"
                f"       got: {results!r}")
            if results != expected:  # pragma: no cover
                fails += 1
                print(f"Fail: {fails}\n{message}")
        assert not fails, fails
    #@+node:ekr.20220327131225.1: *4* TestOrange.test_leading_stars
    def test_leading_stars(self):

        # #2533.
        contents = """\
            def f(
                arg1,
                *args,
                **kwargs
            ):
                pass
    """
        expected = textwrap.dedent("""\
            def f(arg1, *args, **kwargs):
                pass
    """)
        contents, tokens, tree = self.make_data(contents)
        results = self.beautify(contents, tokens, tree)
        self.assertEqual(expected, results)
    #@+node:ekr.20200108075541.1: *4* TestOrange.test_leo_sentinels
    def test_leo_sentinels_1(self):

        # Careful: don't put a sentinel into the file directly.
        # That would corrupt leoAst.py.
        sentinel = '#@+node:ekr.20200105143308.54: ** test'
        contents = f"""\
    {sentinel}
    def spam():
        pass
    """
        contents, tokens, tree = self.make_data(contents)
        expected = contents.rstrip() + '\n'
        results = self.beautify(contents, tokens, tree)
        self.assertEqual(results, expected)
    #@+node:ekr.20200209155457.1: *4* TestOrange.test_leo_sentinels_2
    def test_leo_sentinels_2(self):

        # Careful: don't put a sentinel into the file directly.
        # That would corrupt leoAst.py.
        sentinel = '#@+node:ekr.20200105143308.54: ** test'
        contents = f"""\
    {sentinel}
    class TestClass:
        pass
    """
        contents, tokens, tree = self.make_data(contents)
        expected = contents.rstrip() + '\n'
        results = self.beautify(contents, tokens, tree)
        self.assertEqual(results, expected)
    #@+node:ekr.20200108082833.1: *4* TestOrange.test_lines_before_class
    def test_lines_before_class(self):

        contents = """\
    a = 2
    class aClass:
        pass
    """
        contents, tokens, tree = self.make_data(contents)
        expected = contents
        results = self.beautify(contents, tokens, tree)
        self.assertEqual(results, expected)
    #@+node:ekr.20200110014220.86: *4* TestOrange.test_multi_line_pet_peeves
    def test_multi_line_pet_peeves(self):

        contents = """\
    if x == 4: pass
    if x == 4 : pass
    print (x, y); x, y = y, x
    print (x , y) ; x , y = y , x
    if(1):
        pass
    elif(2):
        pass
    while(3):
        pass
    """
        # At present Orange doesn't split lines...
        expected = """\
    if x == 4: pass
    if x == 4: pass
    print(x, y); x, y = y, x
    print(x, y); x, y = y, x
    if (1):
        pass
    elif (2):
        pass
    while (3):
        pass
    """
        contents, tokens, tree = self.make_data(contents)
        expected = self.adjust_expected(expected)
        results = self.beautify(contents, tokens, tree)
        self.assertEqual(results, expected)
    #@+node:ekr.20200110014220.95: *4* TestOrange.test_one_line_pet_peeves
    def test_one_line_pet_peeves(self):

        # See https://peps.python.org/pep-0008/#pet-peeves
        # See https://peps.python.org/pep-0008/#other-recommendations

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
            if results != expected:  # pragma: no cover
                fails += 1
                print('')
                print(
                    f"TestOrange.test_one_line_pet_peeves: FAIL {fails}\n"
                    f"  contents: {contents.rstrip()}\n"
                    f"     black: {expected.rstrip()}\n"
                    f"    orange: {results.rstrip()}")
        self.assertEqual(fails, 0)
    #@+node:ekr.20220327135448.1: *4* TestOrange.test_relative_imports
    def test_relative_imports(self):

        # #2533.
        contents = """\
            from .module1 import w
            from . module2 import x
            from ..module1 import y
            from .. module2 import z
            from . import a
            from.import b
            from leo.core import leoExternalFiles
            import leo.core.leoGlobals as g
    """
        expected = textwrap.dedent("""\
            from .module1 import w
            from .module2 import x
            from ..module1 import y
            from ..module2 import z
            from . import a
            from . import b
            from leo.core import leoExternalFiles
            import leo.core.leoGlobals as g
    """)
        contents, tokens, tree = self.make_data(contents)
        results = self.beautify(contents, tokens, tree)
        self.assertEqual(expected, results)
    #@+node:ekr.20200210050646.1: *4* TestOrange.test_return
    def test_return(self):

        contents = """return []"""
        expected = self.blacken(contents)
        contents, tokens, tree = self.make_data(contents)
        results = self.beautify(contents, tokens, tree)
        self.assertEqual(results, expected)
    #@+node:ekr.20200107174742.1: *4* TestOrange.test_single_quoted_string
    def test_single_quoted_string(self):

        contents = """print('hi')"""
        # blacken suppresses string normalization.
        expected = self.blacken(contents)
        contents, tokens, tree = self.make_data(contents)
        results = self.beautify(contents, tokens, tree)
        self.assertEqual(results, expected)
    #@+node:ekr.20200117180956.1: *4* TestOrange.test_split_lines
    def test_split_lines(self):

        line_length = 40  # For testing.
        table = (
        #1234567890x1234567890x1234567890x1234567890x
            """\
    if 1:
        print('1111111111', '2222222222', '3333333333')
    """,
    """print('aaaaaaaaaaaaa', 'bbbbbbbbbbbbbb', 'cccccc')""",
    """print('aaaaaaaaaaaaa', 'bbbbbbbbbbbbbb', 'cccccc', 'ddddddddddddddddd')""",
        )
        fails = 0
        for contents in table:
            contents, tokens, tree = self.make_data(contents)
            if 0:
                dump_tokens(tokens)
                # dump_tree(tokens, tree)
            expected = self.blacken(contents, line_length=line_length)
            results = self.beautify(contents, tokens, tree,
                max_join_line_length=line_length,
                max_split_line_length=line_length,
            )
            message = (
                f"\n"
                f"  contents: {contents!s}\n"
                f"     black: {expected!s}\n"
                f"    orange: {results!s}")
            if results != expected:  # pragma: no cover
                fails += 1
                print(f"Fail: {fails}\n{message}")
        self.assertEqual(fails, 0)
    #@+node:ekr.20200210073227.1: *4* TestOrange.test_split_lines_2
    def test_split_lines_2(self):

        line_length = 40  # For testing.
        # Different from how black handles things.
        contents = """\
    if not any([z.kind == 'lt' for z in line_tokens]):
        return False
    """
        expected = """\
    if not any(
        [z.kind == 'lt' for z in line_tokens]):
        return False
    """
        fails = 0
        contents, tokens, tree = self.make_data(contents)
        # expected = self.blacken(contents, line_length=line_length)
        expected = textwrap.dedent(expected)
        results = self.beautify(contents, tokens, tree,
            max_join_line_length=line_length,
            max_split_line_length=line_length,
        )
        message = (
            f"\n"
            f"  contents: {contents!r}\n"
            f"  expected: {expected!r}\n"
            f"       got: {results!r}")
        if results != expected:  # pragma: no cover
            fails += 1
            print(f"Fail: {fails}\n{message}")
        self.assertEqual(fails, 0)
    #@+node:ekr.20200219144837.1: *4* TestOrange.test_split_lines_3
    def test_split_lines_3(self):

        line_length = 40  # For testing.
        # Different from how black handles things.
        contents = """print('eee', ('fffffff, ggggggg', 'hhhhhhhh', 'iiiiiii'), 'jjjjjjj', 'kkkkkk')"""
        # This is a bit different from black, but it's good enough for now.
        expected = """\
    print(
        'eee',
        ('fffffff, ggggggg', 'hhhhhhhh', 'iiiiiii'),
        'jjjjjjj',
        'kkkkkk',
    )
    """
        fails = 0
        contents, tokens, tree = self.make_data(contents)
        # expected = self.blacken(contents, line_length=line_length)
        expected = textwrap.dedent(expected)
        results = self.beautify(contents, tokens, tree,
            max_join_line_length=line_length,
            max_split_line_length=line_length,
        )
        message = (
            f"\n"
            f"  contents: {contents!r}\n"
            f"  expected: {expected!r}\n"
            f"       got: {results!r}")
        if results != expected:  # pragma: no cover
            fails += 1
            print(f"Fail: {fails}\n{message}")
        self.assertEqual(fails, 0)
    #@+node:ekr.20220401191253.1: *4* TestOrange.test_star_star_operator
    def test_star_star_operator(self):
        # Was tested in pet peeves, but this is more permissive.
        contents = """a = b ** c"""
        contents, tokens, tree = self.make_data(contents)
        # Don't rely on black for this test.
        # expected = self.blacken(contents)
        expected = contents
        results = self.beautify(contents, tokens, tree)
        self.assertEqual(results, expected)
    #@+node:ekr.20200119155207.1: *4* TestOrange.test_sync_tokens
    def test_sync_tokens(self):

        contents = """if x == 4: pass"""
        # At present Orange doesn't split lines...
        expected = """if x == 4: pass"""
        contents, tokens, tree = self.make_data(contents)
        expected = self.adjust_expected(expected)
        results = self.beautify(contents, tokens, tree)
        self.assertEqual(results, expected)
    #@+node:ekr.20200209161226.1: *4* TestOrange.test_ternary
    def test_ternary(self):

        contents = """print(2 if name == 'class' else 1)"""
        contents, tokens, tree = self.make_data(contents)
        expected = contents
        results = self.beautify(contents, tokens, tree)
        self.assertEqual(results, expected)
    #@+node:ekr.20200211093359.1: *4* TestOrange.test_verbatim
    def test_verbatim(self):

        line_length = 40  # For testing.
        contents = textwrap.dedent("""\
    #@@nobeautify

    def addOptionsToParser(self, parser, trace_m):

        add = parser.add_option

        def add_bool(option, help, dest=None):
            add(option, action='store_true', dest=dest, help=help)

        add_bool('--diff',          'use Leo as an external git diff')
        # add_bool('--dock',          'use a Qt dock')
        add_bool('--fullscreen',    'start fullscreen')
        add_bool('--init-docks',    'put docks in default positions')
        # Multiple bool values.
        add('-v', '--version', action='store_true',
            help='print version number and exit')

    # From leoAtFile.py
    noDirective     =  1 # not an at-directive.
    allDirective    =  2 # at-all (4.2)
    docDirective    =  3 # @doc.

    #@@beautify
    """)
        contents, tokens, tree = self.make_data(contents)
        expected = contents
        results = self.beautify(contents, tokens, tree,
            max_join_line_length=line_length,
            max_split_line_length=line_length,
        )
        self.assertEqual(results, expected, msg=contents)
    #@+node:ekr.20200211094209.1: *4* TestOrange.test_verbatim_with_pragma
    def test_verbatim_with_pragma(self):

        line_length = 40  # For testing.
        contents = """\
    # pragma: no beautify

    def addOptionsToParser(self, parser, trace_m):

        add = parser.add_option

        def add_bool(option, help, dest=None):
            add(option, action='store_true', dest=dest, help=help)

        add_bool('--diff',          'use Leo as an external git diff')
        # add_bool('--dock',          'use a Qt dock')
        add_bool('--fullscreen',    'start fullscreen')
        add_other('--window-size',  'initial window size (height x width)', m='SIZE')
        add_other('--window-spot',  'initial window position (top x left)', m='SPOT')
        # Multiple bool values.
        add('-v', '--version', action='store_true',
            help='print version number and exit')

    # pragma: beautify
    """
        contents, tokens, tree = self.make_data(contents)
        expected = contents
        results = self.beautify(contents, tokens, tree,
            max_join_line_length=line_length,
            max_split_line_length=line_length,
        )
        self.assertEqual(results, expected, msg=contents)
    #@+node:ekr.20200729083027.1: *4* TestOrange.verbatim2
    def test_verbatim2(self):

        contents = """\
    #@@beautify
    #@@nobeautify
    #@+at Starts doc part
    # More doc part.
    # The @c ends the doc part.
    #@@c
    """
        contents, tokens, tree = self.make_data(contents)
        expected = contents
        results = self.beautify(contents, tokens, tree)
        self.assertEqual(results, expected, msg=contents)
    #@-others
#@+node:ekr.20191231130208.1: *3* class TestReassignTokens (BaseTest)
class TestReassignTokens(BaseTest):
    """Test cases for the ReassignTokens class."""
    #@+others
    #@+node:ekr.20191231130320.1: *4* test_reassign_tokens (to do)
    def test_reassign_tokens(self):
        pass
    #@+node:ekr.20191231130334.1: *4* test_nearest_common_ancestor
    def test_nearest_common_ancestor(self):

        contents = """name='uninverted %s' % d.name()"""
        self.make_data(contents)
    #@-others
#@+node:ekr.20200110093802.1: *3* class TestTokens (BaseTest)
class TestTokens(BaseTest):
    """Unit tests for tokenizing."""
    #@+others
    #@+node:ekr.20200122165910.1: *4* TT.show_asttokens_script
    def show_asttokens_script(self):  # pragma: no cover
        """
        A script showing how asttokens can *easily* do the following:
        - Inject parent/child links into ast nodes.
        - Inject many-to-many links between tokens and ast nodes.
        """
        # pylint: disable=import-error,reimported
        import ast
        import asttokens
        import token as token_module
        stack: List[ast.AST] = []
        # Define TestToken class and helper functions.
        #@+others
        #@+node:ekr.20200122170101.3: *5* class TestToken
        class TestToken:
            """A patchable representation of the 5-tuples created by tokenize and used by asttokens."""

            def __init__(self, kind, value):
                self.kind = kind
                self.value = value
                self.node_list: List[Any] = []

            def __str__(self):
                tokens_s = ', '.join([z.__class__.__name__ for z in self.node_list])
                return f"{self.kind:12} {self.value:20} {tokens_s!s}"

            __repr__ = __str__
        #@+node:ekr.20200122170101.1: *5* function: atok_name
        def atok_name(token):
            """Return a good looking name for the given 5-tuple"""
            return token_module.tok_name[token[0]].lower()  # type:ignore
        #@+node:ekr.20200122170101.2: *5* function: atok_value
        def atok_value(token):
            """Print a good looking value for the given 5-tuple"""
            return token.string if atok_name(token) == 'string' else repr(token.string)
        #@+node:ekr.20200122170057.1: *5* function: dump_token
        def dump_token(token):
            node_list = list(set(getattr(token, 'node_set', [])))
            node_list = sorted([z.__class__.__name__ for z in node_list])
            return f"{token.index:2} {atok_name(token):12} {atok_value(token):20} {node_list}"
        #@+node:ekr.20200122170337.1: *5* function: postvisit
        def postvisit(node, par_value, value):
            nonlocal stack
            stack.pop()
            return par_value or []
        #@+node:ekr.20200122170101.4: *5* function: previsit
        def previsit(node, par_value):
            nonlocal stack
            if isinstance(node, ast.Module):
                stack = []
            if stack:
                parent = stack[-1]
                children: List[ast.AST] = getattr(parent, 'children', [])
                parent.children = children + [node]  # type:ignore
                node.parent = parent
            else:
                node.parent = None
                node.children = []
            stack.append(node)
            return par_value, []
        #@-others
        table = (
                        # """print('%s in %5.2f sec' % ("done", 2.9))\n""",
            """print(a[1:2:3])\n""",
        )
        for source in table:
            print(f"Source...\n\n{source}")
            atok = asttokens.ASTTokens(source, parse=True)
            # Create a patchable list of Token objects.
            tokens = [TestToken(atok_name(z), atok_value(z)) for z in atok.tokens]
            # Inject parent/child links into nodes.
            asttokens.util.visit_tree(atok.tree, previsit, postvisit)
            # Create token.token_list for each token.
            for node in asttokens.util.walk(atok.tree):
                # Inject node into token.node_list
                for ast_token in atok.get_tokens(node, include_extra=True):
                    i = ast_token.index
                    token = tokens[i]
                    token.node_list.append(node)
            # Print the resulting parent/child links.
            for node in ast.walk(atok.tree):
                if hasattr(node, 'first_token'):
                    parent = getattr(node, 'parent', None)
                    parent_s = parent.__class__.__name__ if parent else 'None'
                    children: List[ast.AST] = getattr(node, 'children', [])
                    if children:
                        children_s = ', '.join(z.__class__.__name__ for z in children)
                    else:
                        children_s = 'None'
                    print(
                        f"\n"
                        f"    node: {node.__class__.__name__}\n"
                        f"  parent: {parent_s}\n"
                        f"children: {children_s}")
            # Print the resulting tokens.
            g.printObj(tokens, tag='Tokens')
    #@+node:ekr.20200121025938.1: *4* TT.show_example_dump
    def show_example_dump(self):  # pragma: no cover

        # Will only be run when enabled explicitly.

        contents = """\
    print('line 1')
    print('line 2')
    print('line 3')
    """
        contents, tokens, tree = self.make_data(contents)
        dump_contents(contents)
        dump_tokens(tokens)
        dump_tree(tokens, tree)
    #@+node:ekr.20200110015014.6: *4* TT.test_bs_nl_tokens
    def test_bs_nl_tokens(self):
        # Test https://bugs.python.org/issue38663.

        contents = """\
    print \
        ('abc')
    """
        self.check_roundtrip(contents)
    #@+node:ekr.20200110015014.8: *4* TT.test_continuation_1
    def test_continuation_1(self):

        contents = """\
    a = (3,4,
        5,6)
    y = [3, 4,
        5]
    z = {'a': 5,
        'b':15, 'c':True}
    x = len(y) + 5 - a[
        3] - a[2] + len(z) - z[
        'b']
    """
        self.check_roundtrip(contents)
    #@+node:ekr.20200111085210.1: *4* TT.test_continuation_2
    def test_continuation_2(self):
        # Backslash means line continuation, except for comments
        contents = (
            'x=1+\\\n    2'
            '# This is a comment\\\n    # This also'
        )
        self.check_roundtrip(contents)
    #@+node:ekr.20200111085211.1: *4* TT.test_continuation_3
    def test_continuation_3(self):

        contents = """\
    # Comment \\\n
    x = 0
    """
        self.check_roundtrip(contents)
    #@+node:ekr.20200110015014.10: *4* TT.test_string_concatenation_1
    def test_string_concatentation_1(self):
        # Two *plain* string literals on the same line
        self.check_roundtrip("""'abc' 'xyz'""")
    #@+node:ekr.20200111081801.1: *4* TT.test_string_concatenation_2
    def test_string_concatentation_2(self):
        # f-string followed by plain string on the same line
        self.check_roundtrip("""f'abc' 'xyz'""")
    #@+node:ekr.20200111081832.1: *4* TT.test_string_concatenation_3
    def test_string_concatentation_3(self):
        # plain string followed by f-string on the same line
        self.check_roundtrip("""'abc' f'xyz'""")
    #@+node:ekr.20160521103254.1: *4* TT.test_visitors_exist
    def test_visitors_exist(self):
        """Ensure that visitors for all ast nodes exist."""
        import _ast
        # Compute all fields to BaseTest.
        aList = sorted(dir(_ast))
        remove = [
            'Interactive', 'Suite',  # Not necessary.
            'AST',  # The base class,
            # Constants...
            'PyCF_ALLOW_TOP_LEVEL_AWAIT',
            'PyCF_ONLY_AST',
            'PyCF_TYPE_COMMENTS',
            # New ast nodes for Python 3.8.
            # We can ignore these nodes because:
            # 1. ast.parse does not generate them by default.
            # 2. The type comments are ordinary comments.
            #    They do not need to be specially synced.
            # 3. Tools such as black, orange, and fstringify will
            #    only ever handle comments as comments.
            'FunctionType', 'NamedExpr', 'TypeIgnore',
        ]
        aList = [z for z in aList if not z[0].islower()]
            # Remove base classes.
        aList = [z for z in aList
            if not z.startswith('_') and not z in remove]
        # Now test them.
        table = (
            TokenOrderGenerator,
        )
        for class_ in table:
            traverser = class_()
            errors, nodes, ops = 0, 0, 0
            for z in aList:
                if hasattr(traverser, 'do_' + z):
                    nodes += 1
                elif _op_names.get(z):
                    ops += 1
                else:  # pragma: no cover
                    errors += 1
                    print(
                        f"Missing visitor: "
                        f"{traverser.__class__.__name__}.{z}")
        msg = f"{nodes} node types, {ops} op types, {errors} errors"
        assert not errors, msg
    #@-others
#@+node:ekr.20200107144010.1: *3* class TestTopLevelFunctions (BaseTest)
class TestTopLevelFunctions(BaseTest):
    """Tests for the top-level functions in leoAst.py."""
    #@+others
    #@+node:ekr.20200107144227.1: *4* test_get_encoding_directive
    def test_get_encoding_directive(self):

        filename = __file__
        assert os.path.exists(filename), repr(filename)
        with open(filename, 'rb') as f:
            bb = f.read()
        e = get_encoding_directive(bb)
        self.assertEqual(e.lower(), 'utf-8')
    #@+node:ekr.20200107150857.1: *4* test_strip_BOM
    def test_strip_BOM(self):

        filename = __file__
        assert os.path.exists(filename), repr(filename)
        with open(filename, 'rb') as f:
            bb = f.read()
        assert bb, filename
        e, s = strip_BOM(bb)
        assert e is None or e.lower() == 'utf-8', repr(e)
    #@-others
#@-others
#@-leo
