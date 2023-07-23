#@+leo-ver=5-thin
#@+node:ekr.20210829124658.1: * @file ../unittests/core/test_leoFind.py
"""Tests of leoFind.py"""

import re
from leo.core import leoGlobals as g
import leo.core.leoFind as leoFind
from leo.core.leoGui import StringFindTabManager
from leo.core.leoTest2 import LeoUnitTest

#@+others
#@+node:ekr.20200216063538.1: ** class TestFind(LeoUnitTest)
class TestFind(LeoUnitTest):
    """Test cases for leoFind.py"""
    #@+others
    #@+node:ekr.20210110073117.57: *3* TestFind.setUp
    def setUp(self):
        """setUp for TestFind class"""
        super().setUp()
        c = self.c
        c.findCommands = self.x = x = leoFind.LeoFind(c)
        x.ftm = StringFindTabManager(c)
        self.settings = x.default_settings()
        self.make_test_tree()
    #@+node:ekr.20210110073117.56: *3* TestFind.make_test_tree
    def make_test_tree(self):
        """Make a test tree for other tests"""
        c = self.c

        # 2023/01/24: Remove any previous tree.
        root = c.rootPosition()
        while root.hasChildren():
            root.firstChild().doDelete()
        while root.hasNext():
            root.next().doDelete()

        root = c.rootPosition()
        root.h = '@file test.py'
        root.b = "def root():\n    pass\n"
        last = root

        def make_child(n, p):
            p2 = p.insertAsLastChild()
            p2.h = f"child {n}"
            p2.b = (
                f"def child{n}():\n"
                f"    v{n} = 2\n"
                f"    # node {n} line 1: blabla second blabla bla second ble blu\n"
                f"    # node {n} line 2: blabla second blabla bla second ble blu"
            )
            return p2

        def make_top(n, sib):
            p = sib.insertAfter()
            p.h = f"Node {n}"
            p.b = (
                f"def top{n}():\n:"
                f"    v{n} = 3\n"
            )
            return p

        for n in range(0, 4, 3):
            last = make_top(n + 1, last)
            child = make_child(n + 2, last)
            make_child(n + 3, child)

        for p in c.all_positions():
            p.v.clearDirty()
            p.v.clearVisited()

        # Always start with the root selected.
        c.selectPosition(c.rootPosition())
    #@+node:ekr.20210110073117.59: *3* Tests of Commands...
    #@+node:ekr.20210110073117.67: *4* TestFind.test_change-all
    def test_change_all(self):
        c, settings, x = self.c, self.settings, self.x
        root = c.rootPosition()

        def init():
            self.make_test_tree()  # Reinit the whole tree.
            settings.change_text = '_DEF_'
            settings.find_text = 'def'
            settings.ignore_case = False
            settings.node_only = False
            settings.pattern_match = False
            settings.suboutline_only = False
            settings.whole_word = True

        # Default settings.
        init()
        x.do_change_all(settings)
        # Plain search, ignore case.
        init()
        settings.whole_word = False
        settings.ignore_case = True
        x.do_change_all(settings)
        # Node only.
        init()
        settings.node_only = True
        x.do_change_all(settings)
        # Suboutline only.
        init()
        settings.suboutline_only = True
        x.do_change_all(settings)
        # Pattern match.
        init()
        settings.pattern_match = True
        x.do_change_all(settings)
        # Pattern match, ignore case.
        init()
        settings.pattern_match = True
        settings.ignore_case = True
        x.do_change_all(settings)
        # Pattern match, with groups.
        init()
        settings.pattern_match = True
        settings.find_text = r'^(def)'
        settings.change_text = '*\1*'
        x.do_change_all(settings)
        # Ignore case
        init()
        settings.ignore_case = True
        x.do_change_all(settings)
        # Word, ignore case.
        init()
        settings.ignore_case = True
        settings.whole_word = True
        x.do_change_all(settings)
        # Multiple matches
        init()
        root.h = 'abc'
        root.b = 'abc\nxyz abc\n'
        settings.find_text = settings.change_text = 'abc'
        x.do_change_all(settings)
        # Set ancestor @file node dirty.
        root.h = '@file xyzzy'
        settings.find_text = settings.change_text = 'child1'
        x.do_change_all(settings)
    #@+node:ekr.20210220091434.1: *4* TestFind.test_change-all (@file node)
    def test_change_all_with_at_file_node(self):
        c, settings, x = self.c, self.settings, self.x
        root = c.rootPosition().next()  # Must have children.
        settings.find_text = 'def'
        settings.change_text = '_DEF_'
        settings.ignore_case = False
        settings.whole_word = True
        settings.pattern_match = False
        settings.suboutline_only = False
        # Ensure that the @file node is marked dirty.
        root.h = '@file xyzzy.py'
        root.b = ''
        root.v.clearDirty()
        assert root.anyAtFileNodeName()
        x.do_change_all(settings)
        assert root.v.isDirty(), root.h

    #@+node:ekr.20210220091434.2: *4* TestFind.test_change-all (headline)
    def test_change_all_headline(self):
        settings, x = self.settings, self.x
        settings.find_text = 'child'
        settings.change_text = '_CHILD_'
        settings.ignore_case = False
        settings.in_headline = True
        settings.whole_word = True
        settings.pattern_match = False
        settings.suboutline_only = False
        x.do_change_all(settings)
    #@+node:ekr.20210110073117.60: *4* TestFind.test_clone-find-all
    def test_clone_find_all(self):
        settings, x = self.settings, self.x
        # Regex find.
        settings.find_text = r'^def\b'
        settings.change_text = 'def'  # Don't actually change anything!
        settings.pattern_match = True
        x.do_clone_find_all(settings)
        # Word find.
        settings.find_text = 'def'
        settings.whole_word = True
        settings.pattern_match = False
        x.do_clone_find_all(settings)
        # Suboutline only.
        settings.suboutline_only = True
        x.do_clone_find_all(settings)
    #@+node:ekr.20210110073117.61: *4* TestFind.test_clone-find-all-flattened
    def test_clone_find_all_flattened(self):
        settings, x = self.settings, self.x
        # regex find.
        settings.find_text = r'^def\b'
        settings.pattern_match = True
        x.do_clone_find_all_flattened(settings)
        # word find.
        settings.find_text = 'def'
        settings.whole_word = True
        settings.pattern_match = False
        x.do_clone_find_all_flattened(settings)
        # Suboutline only.
        settings.suboutline_only = True
        x.do_clone_find_all_flattened(settings)
    #@+node:ekr.20210617072622.1: *4* TestFind.test_clone-find-marked
    def test_clone_find_marked(self):
        c, x = self.c, self.x
        root = c.rootPosition()
        root.setMarked()
        x.cloneFindAllMarked()
        x.cloneFindAllFlattenedMarked()
        root.setMarked()
    #@+node:ekr.20210615084049.1: *4* TestFind.test_clone-find-parents
    def test_clone_find_parents(self):

        c, x = self.c, self.x
        root = c.rootPosition()
        p = root.next().firstChild()
        p.clone()  # c.p must be a clone.
        c.selectPosition(p)
        x.cloneFindParents()

    #@+node:ekr.20210110073117.62: *4* TestFind.test_clone-find-tag
    def test_clone_find_tag(self):
        c, x = self.c, self.x

        class DummyTagController:

            def __init__(self, clones):
                self.clones = clones

            def get_tagged_nodes(self, tag):
                return self.clones

            def show_all_tags(self):
                pass

        c.theTagController = DummyTagController([c.rootPosition()])
        x.do_clone_find_tag('test')
        c.theTagController = DummyTagController([])
        x.do_clone_find_tag('test')
        c.theTagController = None
        x.do_clone_find_tag('test')
    #@+node:ekr.20210110073117.63: *4* TestFind.test_find-all
    def test_find_all(self):
        settings, x = self.settings, self.x

        def init():
            self.make_test_tree()  # Reinit the whole tree.
            settings.change_text = ''
            settings.find_text = ''
            settings.ignore_case = False
            settings.node_only = False
            settings.pattern_match = False
            settings.suboutline_only = False
            settings.whole_word = True

        # Debugging.
        if 0:
            init()
            g.cls()
            g.trace('test_find_all')
            for i, p in enumerate(self.c.all_positions()):
                g.printObj(g.splitLines(p.b), tag=f"node {i}: {p.h}")

        # Test 1.
        for aTuple in (
            ('settings', (True, False, False)),
            ('def', 7),
            ('bla', 40),
        ):
            if aTuple[0] == 'settings':
                case, regex, word = aTuple[1]
            else:
                find_text, expected_count = aTuple
                init()
                settings.find_text = find_text
                settings.ignore_case = case
                settings.pattern_match = regex
                settings.whole_word = word
                self.assertTrue(self.c, self.c.rootPosition())
                result_dict = x.do_find_all(settings)
                count = result_dict['total_matches']
                self.assertEqual(count, expected_count, msg=find_text)

        ### return

        # Test 2.
        init()
        settings.suboutline_only = True
        x.do_find_all(settings)
        # Test 3.
        init()
        settings.search_headline = False
        settings.p.setVisited()
        x.do_find_all(settings)
        # Test 4.
        init()
        settings.pattern_match = True
        settings.find_text = r'^(def)'
        settings.change_text = '*\1*'
        x.do_find_all(settings)
        # Test 5: no match.
        init()
        settings.find_text = 'not-found-xyzzy'
        x.do_find_all(settings)

    #@+node:ekr.20210110073117.65: *4* TestFind.test_find-def
    def test_find_def(self):
        x = self.x

        # Test 1: Test methods called by x.find_def.
        x._save_before_find_def(x.c.rootPosition())  # Also tests _restore_after_find_def.

        # Test 2:
        for reverse in (True, False):
            # Successful search.
            x.reverse_find_defs = reverse
            settings = x._compute_find_def_settings('def child5')
            p, pos, newpos = x.do_find_def(settings)
            self.assertTrue(p)
            self.assertEqual(p.h, 'child 5')
            s = p.b[pos:newpos]
            self.assertEqual(s, 'def child5')
            # Unsuccessful search.
            settings = x._compute_find_def_settings('def xyzzy')
            p, pos, newpos = x.do_find_def(settings)
            assert p is None, repr(p)
    #@+node:ekr.20210110073117.64: *4* TestFind.test_find-next
    def test_find_next(self):
        settings, x = self.settings, self.x
        settings.find_text = 'def top1'
        p, pos, newpos = x.do_find_next(settings)
        assert p
        self.assertEqual(p.h, 'Node 1')
        s = p.b[pos:newpos]
        self.assertEqual(s, settings.find_text)
    #@+node:ekr.20220525100840.1: *4* TestFind.test_find-next (file-only)
    def test_find_next_file_only(self):
        settings, x = self.settings, self.x
        settings.file_only = True  # init_ivars_from_settings will set the ivar.
        settings.find_text = 'def root()'
        p, pos, newpos = x.do_find_next(settings)
        assert p
        self.assertEqual(p.h, '@file test.py')
        s = p.b[pos:newpos]
        self.assertEqual(s, settings.find_text)
    #@+node:ekr.20210220072631.1: *4* TestFind.test_find-next (suboutline-only)
    def test_find_next_suboutline_only(self):
        settings, x = self.settings, self.x
        settings.find_text = 'def root()'
        settings.suboutline_only = True  # init_ivars_from_settings will set the ivar.
        p, pos, newpos = x.do_find_next(settings)
        assert p
        self.assertEqual(p.h, '@file test.py')
        s = p.b[pos:newpos]
        self.assertEqual(s, settings.find_text)
    #@+node:ekr.20210924032146.1: *4* TestFind.test_change-then-find (headline)
    def test_change_then_find_in_headline(self):
        # Test #2220:
        # https://github.com/leo-editor/leo-editor/issues/2220
        # Let block.
        settings, c, x = self.settings, self.c, self.x
        # Set up the search.
        settings.find_text = 'Test'
        settings.change_text = 'XX'
        # Create the tree.
        test_p = self.c.rootPosition().insertAfter()
        test_p.h = 'Test1 Test2 Test3'
        after_p = test_p.insertAfter()
        after_p.h = 'After'
        # Find test_p.
        p, pos, newpos = x.do_find_next(settings)
        self.assertEqual(p, test_p)
        w = c.edit_widget(p)
        self.assertEqual(test_p.h, w.getAllText())
        self.assertEqual(w.getSelectionRange(), (pos, newpos))
        # Do change-then-find.
        ok = x.do_change_then_find(settings)
        self.assertTrue(ok)
        p = c.p
        self.assertEqual(p, test_p)
        self.assertEqual(p.h, 'XX1 Test2 Test3')
    #@+node:ekr.20210216094444.1: *4* TestFind.test_find-prev
    def test_find_prev(self):
        c, settings, x = self.c, self.settings, self.x
        settings.find_text = 'def top1'
        # Start at end, so we stay in the node.
        grand_child = g.findNodeAnywhere(c, 'child 6')
        settings.p = grand_child
        assert settings.p
        settings.find_text = 'def child2'
        # Set c.p in the command.
        x.c.selectPosition(grand_child)
        p, pos, newpos = x.do_find_prev(settings)
        assert p
        self.assertEqual(p.h, 'child 2')
        s = p.b[pos:newpos]
        self.assertEqual(s, settings.find_text)
    #@+node:ekr.20210110073117.66: *4* TestFind.test_find-var
    def test_find_var(self):
        x = self.x
        settings = x._compute_find_def_settings('v5 =')
        p, pos, newpos = x.do_find_var(settings)
        assert p
        self.assertEqual(p.h, 'child 5')
        s = p.b[pos:newpos]
        self.assertEqual(s, 'v5 =')
    #@+node:ekr.20210110073117.68: *4* TestFind.test_replace-then-find
    def test_replace_then_find(self):
        settings, w, x = self.settings, self.c.frame.body.wrapper, self.x
        settings.find_text = 'def top1'
        settings.change_text = 'def top'
        # find-next
        p, pos, newpos = x.do_find_next(settings)
        assert p
        self.assertEqual(p.h, 'Node 1')
        s = p.b[pos:newpos]
        self.assertEqual(s, settings.find_text)
        # replace-then-find
        w.setSelectionRange(pos, newpos, insert=pos)
        x.do_change_then_find(settings)
        # Failure exit.
        w.setSelectionRange(0, 0)
        x.do_change_then_find(settings)

    def test_replace_then_find_regex(self):
        settings, w, x = self.settings, self.c.frame.body.wrapper, self.x
        settings.find_text = r'(def) top1'
        settings.change_text = r'\1\1'
        settings.pattern_match = True
        # find-next
        p, pos, newpos = x.do_find_next(settings)
        s = p.b[pos:newpos]
        self.assertEqual(s, 'def top1')
        # replace-then-find
        w.setSelectionRange(pos, newpos, insert=pos)
        x.do_change_then_find(settings)

    def test_replace_then_find_in_headline(self):
        settings, x = self.settings, self.x
        p = settings.p
        settings.find_text = 'Node 1'
        settings.change_text = 'Node 1a'
        settings.in_headline = True
        # find-next
        p, pos, newpos = x.do_find_next(settings)
        assert p
        self.assertEqual(p.h, settings.find_text)
        w = self.c.edit_widget(p)
        assert w
        s = p.h[pos:newpos]
        self.assertEqual(s, settings.find_text)
    #@+node:ekr.20210110073117.69: *4* TestFind.test_tag-children
    def test_tag_children(self):

        c, x = self.c, self.x

        class DummyTagController:
            def add_tag(self, p, tag):
                pass

        p = c.rootPosition().next()
        c.theTagController = None
        x.do_tag_children(p, 'test')
        c.theTagController = DummyTagController()
        x.do_tag_children(p, 'test')
    #@+node:ekr.20210219181001.1: *4* testFind.test_batch_change_regex
    def test_batch_change_regex(self):
        c, x = self.c, self.x
        # self.dump_tree()
        # Test 1: Match in body.
        settings = dict(
            ignore_case=False,
            node_only=False,
            pattern_match=True,
            search_body=True,
            search_headline=True,
            suboutline_only=False,
            whole_word=False,
        )
        # Test 1: Match in body.
        n = x.batch_change(
            root=c.rootPosition(),
            replacements=((r'^def\b', 'DEF'),),
            settings=settings)
        assert n > 3, n  # Test 1.
        # Test 2: Match in headline.
        n = x.batch_change(
            root=c.rootPosition(),
            replacements=((r'^Node\b', 'DEF'),),
            settings=settings)
        self.assertEqual(n, 2)
        # Test 3: node-only.
        settings['node_only'] = True
        n = x.batch_change(
            root=c.rootPosition(),
            replacements=((r'^DEF\b', 'def'),),
            settings=settings)
        self.assertEqual(n, 1)
        # Test 4: suboutline-only.
        settings['node_only'] = False
        settings['suboutline_only'] = True
        n = x.batch_change(
            root=c.rootPosition(),
            replacements=((r'^def\b', 'DEF'),),
            settings=settings)
        self.assertEqual(n, 1)
    #@+node:ekr.20210219175850.1: *4* testFind.test_batch_change_word
    def test_batch_change_word(self):
        # settings, x = self.settings, self.x
        c, x = self.c, self.x
        settings = dict(
            ignore_case=False,
            node_only=False,
            pattern_match=False,
            search_body=True,
            search_headline=True,
            suboutline_only=False,
            whole_word=True,
        )
        n = x.batch_change(
            root=c.rootPosition(),
            replacements=(('def', 'DEF'),),
            settings=settings)
        assert n > 0

    #@+node:ekr.20210110073117.58: *4* TestFind.test_test_tree
    def test_tree(self):
        c = self.c
        table = (
            (0, '@file test.py'),
            (0, 'Node 1'),
            (1, 'child 2'),
            (2, 'child 3'),
            (0, 'Node 4'),
            (1, 'child 5'),
            (2, 'child 6'),
        )
        for level, h in table:
            p = g.findNodeAnywhere(c, h)
            self.assertEqual(p.h, h)
            self.assertEqual(p.level(), level)
    #@+node:ekr.20210110073117.70: *3* Tests of Helpers...
    #@+node:ekr.20210110073117.72: *4* TestFind.test_argument_errors
    def test_argument_errors(self):

        settings, x = self.settings, self.x
        # Bad search pattern.
        settings.find_text = r'^def\b(('
        settings.pattern_match = True
        x.do_clone_find_all(settings)
        x.find_next_match(p=None)
        x.do_change_all(settings)
    #@+node:ekr.20210110073117.71: *4* TestFind.test_cfa_backwards_search
    def test_cfa_backwards_search(self):
        settings, x = self.settings, self.x
        pattern = 'def'
        for nocase in (True, False):
            settings.ignore_case = nocase
            for word in (True, False):
                for s in ('def spam():\n', 'define spam'):
                    settings.whole_word = word
                    x.init_ivars_from_settings(settings)
                    x._inner_search_backward(s, 0, len(s), pattern, nocase, word)
                    x._inner_search_backward(s, 0, 0, pattern, nocase, word)
    #@+node:ekr.20210110073117.80: *4* TestFind.test_cfa_find_next_match
    def test_cfa_find_next_match(self):
        c, settings, x = self.c, self.settings, self.x
        p = c.rootPosition()
        for find in ('xxx', 'def'):
            settings.find_text = find
            x._cfa_find_next_match(p)
    #@+node:ekr.20210110073117.83: *4* TestFind.test_cfa_match_word
    def test_cfa_match_word(self):
        x = self.x
        x._inner_search_match_word("def spam():", 0, "spam")
        x._inner_search_match_word("def spam():", 0, "xxx")

    #@+node:ekr.20210110073117.85: *4* TestFind.test_cfa_plain_search
    def test_cfa_plain_search(self):
        settings, x = self.settings, self.x
        pattern = 'def'
        for nocase in (True, False):
            settings.ignore_case = nocase
            for word in (True, False):
                for s in ('def spam():\n', 'define'):
                    settings.whole_word = word
                    x.init_ivars_from_settings(settings)
                    x._inner_search_plain(s, 0, len(s), pattern, nocase, word)
                    x._inner_search_plain(s, 0, 0, pattern, nocase, word)
    #@+node:ekr.20210110073117.88: *4* TestFind.test_cfa_regex_search
    def test_cfa_regex_search(self):
        x = self.x
        pattern = r'(.*)pattern'
        x.re_obj = re.compile(pattern)
        table = (
            'test pattern',  # Match.
            'xxx',  # No match.
        )
        for backwards in (True, False):
            for nocase in (True, False):
                for s in table:
                    if backwards:
                        i = j = len(s)
                    else:
                        i = j = 0
                    x._inner_search_regex(s, i, j, pattern, backwards, nocase)
        # Error test.
        x.re_obj = None
        backwards = pattern = nocase = None
        x._inner_search_regex("", 0, 0, pattern, backwards, nocase)
    #@+node:ekr.20210110073117.76: *4* TestFind.test_check_args
    def test_check_args(self):
        # Bad search patterns..
        x = self.x
        settings = self.settings
        # Not searching headline or body.
        settings.search_body = False
        settings.search_headline = False
        x.do_clone_find_all(settings)
        # Empty find pattern.
        settings.search_body = True
        settings.find_text = ''
        x.do_clone_find_all(settings)
        x.do_clone_find_all_flattened(settings)
        x.do_find_all(settings)
        x.do_find_next(settings)
        x.do_find_next(settings)
        x.do_find_prev(settings)
        x.do_change_all(settings)
        x.do_change_then_find(settings)
    #@+node:ekr.20210829203927.10: *4* TestFind.test_clean_init
    def test_clean_init(self):
        c = self.c
        x = leoFind.LeoFind(c)
        table = (
            'ignore_case', 'node_only', 'pattern_match',
            'search_headline', 'search_body', 'suboutline_only',
            'mark_changes', 'mark_finds', 'whole_word',
        )
        for ivar in table:
            assert getattr(x, ivar) is None, ivar
        assert x.reverse is False
    #@+node:ekr.20210110073117.77: *4* TestFind.test_compute_result_status
    def test_compute_result_status(self):
        x = self.x
        # find_all_flag is True
        all_settings = x.default_settings()
        all_settings.ignore_case = True
        all_settings.pattern_match = True
        all_settings.whole_word = True
        all_settings.wrapping = True
        x.init_ivars_from_settings(all_settings)
        x.compute_result_status(find_all_flag=True)
        # find_all_flag is False
        partial_settings = x.default_settings()
        partial_settings.search_body = True
        partial_settings.search_headline = True
        partial_settings.node_only = True
        partial_settings.suboutline_only = True
        partial_settings.wrapping = True
        x.init_ivars_from_settings(partial_settings)
        x.compute_result_status(find_all_flag=False)
    #@+node:ekr.20230124162455.1: *4* TestFind.test_find_all_plain
    #@@nobeautify
    def test_find_all_plain(self):
        c = self.c
        fc = c.findCommands
        table = (
            (False, False),
            # s         find    expected
            ('aA',      'a',    [0]),
            ('aAa',     'A',    [1]),
            ('AAbabc',  'b',    [2, 4]),

            (True, False),
            ('axA',     'a',    [0, 2]),
            ('aAa',     'A',    [0, 1, 2]),
            ('ABbabc',  'b',    [1, 2, 4]),

            (True, True),
            ('ax aba ab abc',   'ab', [7]),
            ('ax aba\nab abc',  'ab', [7]),
            ('ax aba ab\babc',  'ab', [7]),
        )
        for aTuple in table:
            if len(aTuple) == 2:
                fc.ignore_case, fc.whole_word = aTuple
            else:
                s, find, expected = aTuple
                aList = fc.find_all_plain(find, s)
                self.assertEqual(aList, expected, msg=s)
    #@+node:ekr.20230124162609.1: *4* TestFind.test_find_all_regex
    #@@nobeautify
    def test_find_all_regex(self):
        c = self.c
        fc = c.findCommands
        regex_table = (
            # s                  find        expected
            ('a ba aa a ab a',   r'\b\w+\b', [0, 2, 5, 8, 10, 13]),
            ('a AA aa aab ab a', r'\baa\b',  [5]),
            # Multi-line
            ('aaa AA\naa aab',   r'\baa\b',  [7]),
        )
        for s, find, expected in regex_table:
            fc.ignore_case = False
            aList = fc.find_all_regex(find, s)
            self.assertEqual(aList, expected, msg=s)
    #@+node:ekr.20210829203927.12: *4* TestFind.test_inner_search_backward
    def test_inner_search_backward(self):
        c = self.c
        x = leoFind.LeoFind(c)

        def test(table, table_name, nocase, word):
            test_n = 0
            for pattern, s, i, j, expected, expected_i, expected_j in table:
                test_n += 1
                if j == -1:
                    j = len(s)
                got_i, got_j = x._inner_search_backward(s, i, j,
                    pattern, nocase=nocase, word=word)
                got = s[got_i:got_j]
                assert expected == got and got_i == expected_i and got_j == expected_j, (
                    '\n     table: %s'
                    '\n    i test: %s'
                    '\n   pattern: %r'
                    '\n         s: %r'
                    '\n  expected: %r'
                    '\n       got: %r'
                    '\nexpected i: %s'
                    '\n     got i: %s'
                    '\nexpected j: %s'
                    '\n     got j: %s'
                    % (table_name, test_n, pattern, s, expected, got, expected_i, got_i, expected_j, got_j))

        plain_table = (
            # pattern   s           i,  j   expected, expected_i, expected_j
            ('a', 'abaca', 0, -1, 'a', 4, 5),
            ('A', 'Abcde', 0, -1, 'A', 0, 1),
        )
        nocase_table = (
            # pattern   s           i,  j   expected, expected_i, expected_j
            ('a', 'abaAca', 0, -1, 'a', 5, 6),
            ('A', 'Abcdca', 0, -1, 'a', 5, 6),
        )
        word_table = (
            # pattern   s           i,  j   expected, expected_i, expected_j
            ('a', 'abaAca', 0, -1, '', -1, -1),
            ('A', 'AA A AB', 0, -1, 'A', 3, 4),
        )
        test(plain_table, 'plain_table', nocase=False, word=False)
        test(nocase_table, 'nocase_table', nocase=True, word=False)
        test(word_table, 'word_table', nocase=False, word=True)
    #@+node:ekr.20210829203927.13: *4* TestFind.test_inner_search_plain
    def test_inner_search_plain(self):
        c = self.c
        x = leoFind.LeoFind(c)

        def test(table, table_name, nocase, word):
            test_n = 0
            for pattern, s, i, j, expected, expected_i, expected_j in table:
                test_n += 1
                if j == -1:
                    j = len(s)
                got_i, got_j = x._inner_search_plain(s, i, j, pattern,
                    nocase=nocase, word=word)
                got = s[got_i:got_j]
                assert expected == got and got_i == expected_i and got_j == expected_j, (
                    '\n     table: %s'
                    '\n    i test: %s'
                    '\n   pattern: %r'
                    '\n         s: %r'
                    '\n  expected: %r'
                    '\n       got: %r'
                    '\nexpected i: %s'
                    '\n     got i: %s'
                    '\nexpected j: %s'
                    '\n     got j: %s'
                    % (table_name, test_n, pattern, s, expected, got, expected_i, got_i, expected_j, got_j))

        plain_table = (
            # pattern   s           i,  j   expected, expected_i, expected_j
            ('a', 'baca', 0, -1, 'a', 1, 2),
            ('A', 'bAcde', 0, -1, 'A', 1, 2),
        )
        nocase_table = (
            # pattern   s           i,  j   expected, expected_i, expected_j
            ('a', 'abaAca', 0, -1, 'a', 0, 1),
            ('A', 'abcdca', 0, -1, 'a', 0, 1),
        )
        word_table = (
            # pattern   s           i,  j   expected, expected_i, expected_j
            ('a', 'abaAca', 0, -1, '', -1, -1),
            ('A', 'AA A AAB', 0, -1, 'A', 3, 4),
        )
        test(plain_table, 'plain_table', nocase=False, word=False)
        test(nocase_table, 'nocase_table', nocase=True, word=False)
        test(word_table, 'word_table', nocase=False, word=True)
    #@+node:ekr.20210829203927.11: *4* TestFind.test_inner_search_regex
    def test_inner_search_regex(self):
        c = self.c
        x = leoFind.LeoFind(c)

        def test(table, table_name, back, nocase):
            for pattern, s, expected in table:
                flags = re.IGNORECASE if nocase else 0
                x.re_obj = re.compile(pattern, flags)
                pos, new_pos = x._inner_search_regex(s, 0, len(s),
                    pattern, backwards=back, nocase=nocase)
                got = s[pos:new_pos]
                assert expected == got, (
                    '\n   table: %s'
                    '\n pattern: %r'
                    '\n       s: %r'
                    '\nexpected: %r'
                    '\n     got: %r' % (table_name, pattern, s, expected, got)
                )

        plain_table = (
            # pattern   s       expected
            (r'.', 'A', 'A'),
            (r'A', 'xAy', 'A'),
        )
        nocase_table = (
            # pattern   s       expected
            (r'.', 'A', 'A'),
            (r'.', 'a', 'a'),
            (r'A', 'xay', 'a'),
            (r'a', 'xAy', 'A'),
        )
        back_table = (
            # pattern   s           expected
            (r'a.b', 'a1b a2b', 'a2b'),
        )
        test(plain_table, 'plain_table', back=False, nocase=False)
        test(nocase_table, 'nocase_table', back=False, nocase=True)
        test(back_table, 'back_table', back=True, nocase=False)
    #@+node:ekr.20210110073117.82: *4* TestFind.test_make_regex_subs
    def test_make_regex_subs(self):
        x = self.x
        x.re_obj = re.compile(r'(.*)pattern')  # The search pattern.
        m = x.re_obj.search('test pattern')  # The find pattern.
        change_text = r'\1Pattern\2'  # \2 is non-matching group.
        x.make_regex_subs(change_text, m.groups())
    #@+node:ekr.20210110073117.84: *4* TestFind.test_next_node_after_fail
    def test_fnm_next_after_fail(self):
        settings, x = self.settings, self.x
        for reverse in (True, False):
            settings.reverse = reverse
            for wrapping in (True, False):
                settings.wrapping = wrapping
                x.init_ivars_from_settings(settings)
                x._fnm_next_after_fail(settings.p)
    #@+node:ekr.20210829203927.2: *4* TestFind.test_replace_all_plain_search
    def test_replace_all_plain_search(self):
        c = self.c
        fc = c.findCommands
        plain_table = (
            # s         find    change  count   result
            ('aA', 'a', 'C', 1, 'CA'),
            ('Aa', 'A', 'C', 1, 'Ca'),
            ('Aba', 'b', 'C', 1, 'ACa'),
        )
        for s, find, change, count, result in plain_table:
            fc.ignore_case = False
            fc.find_text = find
            fc.change_text = change
            count2, result2 = fc._change_all_plain(s)
            self.assertEqual(result, result2)
            self.assertEqual(count, count2)
    #@+node:ekr.20210829203927.3: *4* TestFind.test_replace_all_plain_search_ignore_case
    def test_replace_all_plain_search_ignore_case(self):
        c = self.c
        fc = c.findCommands
        plain_table = (
            # s         find    change  count   result
            ('aA', 'a', 'C', 2, 'CC'),
            ('AbBa', 'b', 'C', 2, 'ACCa'),
        )
        for s, find, change, count, result in plain_table:
            fc.ignore_case = True
            fc.find_text = find
            fc.change_text = change
            count2, result2 = fc._change_all_plain(s)
            self.assertEqual(result, result2)
            self.assertEqual(count, count2)
    #@+node:ekr.20210829203927.4: *4* TestFind.test_replace_all_regex_search
    def test_replace_all_regex_search(self):
        c = self.c
        fc = c.findCommands
        regex_table = (
            # s                 find        change  count   result
            ('a ba aa a ab a', r'\b\w+\b', 'C', 6, 'C C C C C C'),
            ('a AA aa aab ab a', r'\baa\b', 'C', 1, 'a AA C aab ab a'),
            # Multi-line
            ('aaa AA\naa aab', r'\baa\b', 'C', 1, 'aaa AA\nC aab'),
        )
        for s, find, change, count, result in regex_table:
            fc.ignore_case = False
            fc.find_text = find
            fc.change_text = change
            count2, result2 = fc._change_all_regex(s)
            self.assertEqual(result, result2)
            self.assertEqual(count, count2)
    #@+node:ekr.20210829203927.5: *4* TestFind.test_replace_all_word_search
    def test_replace_all_word_search(self):
        c = self.c
        fc = c.findCommands
        word_table = (
            # s                 find    change  count   result
            ('a ba aa a ab a', 'a', 'C', 3, 'C ba aa C ab C'),
            ('a ba aa a ab a', 'aa', 'C', 1, 'a ba C a ab a'),
        )
        for s, find, change, count, result in word_table:
            fc.ignore_case = False
            fc.find_text = find
            fc.change_text = change
            count2, result2 = fc._change_all_word(s)
            self.assertEqual(result, result2)
            self.assertEqual(count, count2)
    #@+node:ekr.20210829203927.6: *4* TestFind.test_replace_all_word_search_ignore_case
    def test_replace_all_word_search_ignore_case(self):
        c = self.c
        fc = c.findCommands
        word_table = (
            # s                 find    change  count   result
            ('a ba aa A ab a', 'a', 'C', 3, 'C ba aa C ab C'),
            ('a ba aa AA ab a', 'aa', 'C', 2, 'a ba C C ab a'),
        )
        for s, find, change, count, result in word_table:
            fc.ignore_case = True
            fc.find_text = find
            fc.change_text = change
            count2, result2 = fc._change_all_word(s)
            self.assertEqual(result, result2)
            self.assertEqual(count, count2)
    #@+node:ekr.20210829203927.14: *4* TestFind.test_replace_back_slashes
    def test_replace_back_slashes(self):
        c = self.c
        x = leoFind.LeoFind(c)
        table = (
            ('\\\\', '\\'),
            ('\\n', '\n'),
            ('\\t', '\t'),
            (r'a\bc', r'a\bc'),
            (r'a\\bc', r'a\bc'),
            (r'a\tc', 'a\tc'),  # Replace \t by a tab.
            (r'a\nc', 'a\nc'),  # Replace \n by a newline.
        )
        for s, expected in table:
            got = x.replace_back_slashes(s)
            self.assertEqual(expected, got, msg=s)
    #@+node:ekr.20210110073117.89: *4* TestFind.test_switch_style
    def test_switch_style(self):
        x = self.x
        table = (
            ('', None),
            ('TestClass', None),
            ('camelCase', 'camel_case'),
            ('under_score', 'underScore'),
        )
        for s, expected in table:
            result = x._switch_style(s)
            self.assertEqual(result, expected, msg=repr(s))
    #@-others
#@-others

#@-leo
