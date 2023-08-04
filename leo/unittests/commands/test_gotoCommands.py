#@+leo-ver=5-thin
#@+node:ekr.20230802060212.1: * @file ../unittests/commands/test_gotoCommands.py
"""Tests of leo.commands.gotoCommands."""
from leo.core import leoGlobals as g
# from leo.core.leoTest2 import LeoUnitTest
from leo.commands.gotoCommands import GoToCommands
from leo.unittests.commands.test_outlineCommands import TestOutlineCommands
assert g

#@+others
#@+node:ekr.20230802060212.2: ** class TestGotoCommands(TestOutlineCommands)
class TestGotoCommands(TestOutlineCommands):
    """Unit tests for leo/commands/gotoCommands.py."""

    #@+others
    #@+node:ekr.20230802060444.1: *3* TestGotoCommands.test_show_file_line
    def test_show_file_line(self):

        c = self.c
        x = GoToCommands(c)
        self.clean_tree()
        self.create_test_paste_outline()

        # Demote all of the root's headlines!
        c.demote()

        # Add body text to each node.
        # All body lines are unique, which simplifies the tests below.
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
        # self.dump_headlines(c)
        # self.dump_clone_info(c)

        # Init unchanging data.
        delim1, delim2 = x.get_delims(root)
        assert (delim1, delim2) == ('#', None)
        delims = x.get_3_delims(root)
        contents_s = x.get_external_file_with_sentinels(root)
        contents = g.splitLines(contents_s)

        # Get the contents as produced by atCleanToString.
        real_clean_s = c.atFileCommands.atCleanToString(root)
        real_clean_contents = g.splitLines(real_clean_s)

        # Remove invisible sentinels and convert visible sentinels to
        # their corresponding line in the outline.
        clean_contents = [
            z.replace('#@', '').replace('+others', '@others')
            for i, z in enumerate(contents)
            if not g.is_invisible_sentinel(delims, contents, i)
        ]

        # g.printObj(real_clean_contents, tag='atCleanToString')
        # g.printObj(contents, tag='With sentinels')
        # g.printObj(clean_contents, tag='No sentinels')

        # A strong test of is_invisible_sentinel.
        self.assertEqual(real_clean_contents, clean_contents)

        # Test 1: x.find_node_start returns the 1-based index of the first line of each node.
        for node_i, p in enumerate(c.all_positions()):
            offset = x.find_node_start(p) - 1
            assert offset is not None, p.h
            line = clean_contents[offset]
            if p.h.startswith('@clean'):
                if offset == 0:
                    assert line == 'before\n', (offset, repr(p.h), repr(line))
                    assert g.splitLines(p.b)[0] == '@language python\n', repr(p.b[0])
            else:
                # print(f"{p.h:10} {offset:3} {line}")
                assert p.h in line, (offset, repr(p.h), repr(line))

        # Test 2: x.find_file_line returns the expected node and offset.
        for i, clean_line in enumerate(clean_contents):
            p, offset = x.find_file_line(i)
            if offset == -1:
                g.trace('Not found', i, repr(clean_line))
                continue
            assert offset > 0, (offset, repr(p))
            line = g.splitLines(p.b)[offset-1]
            # g.trace(f"{i:>2} {offset} {p.h:20} {line!r}")
            if p.h.startswith('@clean'):
                if offset == 1:
                    # We are testing p.b, not clean_line.
                    assert line == '@language python\n', (offset, repr(p.h), repr(line))
            else:
                assert p.h in line, (offset, repr(p.h), repr(line))
    #@-others
#@-others
#@-leo
