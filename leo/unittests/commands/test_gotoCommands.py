#@+leo-ver=5-thin
#@+node:ekr.20230802060212.1: * @file ../unittests/commands/test_gotoCommands.py
"""Tests of leo.commands.gotoCommands."""
from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest
from leo.commands.gotoCommands import GoToCommands
assert g
from leo.core.leoNodes import Position

#@+others
#@+node:ekr.20230802060212.2: ** class TestGotoCommands(LeoUnitTest)
class TestGotoCommands(LeoUnitTest):
    """Unit tests for leo/commands/gotoCommands.py."""

    #@+others
    #@+node:ekr.20230802060444.1: *3* TestGotoCommands.test_show_file_line
    def test_show_file_line(self):

        c = self.c
        x = GoToCommands(c)

        clean_contents: list[str]
        real_clean_contents: list[str]
        root: Position

        #@+others  # Create helpers
        #@+node:ekr.20230804093924.1: *4* function: create_test_tree
        def create_test_tree() -> Position:

            self.clean_tree()
            self.create_test_paste_outline()

            # Demote all of the root's headlines!
            c.demote()

            # Add body text to each node.
            root = c.rootPosition()
            assert root.h == 'root'
            root.h = '@clean test.py'  # Make the root an @clean node.
            for v in c.all_unique_nodes():
                for i in range(2):
                    v.b += f"{v.h} line {i}\n"
            root.b = (
                '@language python\n'
                'before\n'
                '@others\n'
                'after\n'
            )
            return root
        #@+node:ekr.20230804093956.1: *4* function: init_unchanging_data
        def init_unchanging_data() -> None:

            nonlocal clean_contents, real_clean_contents

            # Init the comment delims.
            delim1, delim2 = x.get_delims(root)
            assert(delim1, delim2) == ('#', None)
            delims = x.get_3_delims(root)

            # Create contents, the file *with* sentinels.
            contents_s = x.get_external_file_with_sentinels(root)
            contents = g.splitLines(contents_s)

            # Create real_clean_contents, the contents produced by atCleanToString.
            real_clean_s = c.atFileCommands.atCleanToString(root)
            real_clean_contents = g.splitLines(real_clean_s)

            # Create clean_contents, contents without invisible sentinels
            # converting visible sentinels to their corresponding line in the outline.
            clean_contents = [
                z.replace('#@', '').replace('+others', '@others')
                for i, z in enumerate(contents)
                if not g.is_invisible_sentinel(delims, contents, i)
            ]

            # Test 0: A strong test of g.is_invisible_sentinel.
            self.assertEqual(clean_contents, real_clean_contents)

        #@+node:ekr.20230804094419.1: *4* test1
        def test1() -> None:

            nonlocal clean_contents

            # test the helper for show-file-line
            for node_i, p in enumerate(c.all_positions()):
                offset = x.find_node_start(p) - 1
                line = clean_contents[offset]
                if p.h.startswith('@clean'):
                    if offset == 0:
                        assert line == 'before\n', (offset, repr(p.h), repr(line))
                        assert g.splitLines(p.b)[0] == '@language python\n', repr(p.b[0])
                else:
                    # print(f"{p.h:10} {offset:3} {line}")
                    assert p.h in line, (offset, repr(p.h), repr(line))
        #@+node:ekr.20230804094514.1: *4* test2
        def test2() -> None:

            nonlocal clean_contents

            # test the helper for goto-global-line.
            for i, clean_line in enumerate(clean_contents):
                p, offset = x.find_file_line(i)
                assert offset is not None, repr(p)
                assert offset > 0, (offset, repr(p))
                line = g.splitLines(p.b)[offset - 1]

                # g.trace(f"{i:>2} {offset} {p.h:20} {line!r}")
                if p.h.startswith('@clean'):
                    if offset == 1:
                        # We are testing p.b, not clean_line.
                        assert line == '@language python\n', (offset, repr(p.h), repr(line))
                else:
                    assert p.h in line, (offset, repr(p.h), repr(line))
        #@+node:ekr.20230804105414.1: *4* test3
        def test3() -> None:
            # test show-file-line & goto-global-line directly >>

            global_i = 0  # Global line index.
            for p in c.all_positions():

                # Init and test lines.
                lines = g.splitLines(p.b)
                if p != root:
                    for i, line in enumerate(lines):
                        # print(f"{global_i:2} {i} {p.h:30} {line!r}")
                        assert p.h in line, (p.h, line)

                # Test show-file-line.
                show_offset = x.find_node_start(p)
                assert show_offset not in (None, -1), (show_offset, p.h)

                # Test goto-global-line.
                goto_p, goto_offset = x.find_file_line(global_i)
                assert p.h == goto_p.h, (p, goto_p)
                assert goto_offset == 1, repr(p)

                # Update global_i.
                if p == root:
                    # Count `before`, `@others`, but *not* `@language python`.
                    global_i += 2
                else:
                    global_i += len(lines)
        #@-others

        # All body lines are unique, which simplifies the tests below.
        root = create_test_tree()

        # self.dump_headlines(c)
        # self.dump_clone_info(c)

        init_unchanging_data()

        # g.printObj(real_clean_contents, tag='atCleanToString')
        # g.printObj(contents, tag='With sentinels')
        # g.printObj(clean_contents, tag='No sentinels')

        test1()
        test2()
        test3()
    #@-others
#@-others
#@-leo
