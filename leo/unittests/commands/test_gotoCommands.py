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
        delim1, delim2 = x.get_delims(root)
        assert (delim1, delim2) == ('#', None)
        delims = x.get_3_delims(root)

        # A shortcut. All body lines are unique.
        contents_s = x.get_external_file_with_sentinels(root)
        contents = g.splitLines(contents_s)
        # Remove invisible sentinels and convert visible sentinels to
        # their corresponding line in the outline.
        clean_contents = [
            z.replace('#@', '').replace('+others', '@others')
            for i, z in enumerate(contents)
            if not g.is_invisible_sentinel(delims, contents, i)
        ]
        # g.printObj(contents, tag='With sentinels')
        # g.printObj(clean_contents, tag='No sentinels')

        # Test all lines of all nodes.
        for node_i, p in enumerate(c.all_positions()):
            p_offset = x.find_node_start(p) - 1
            assert p_offset is not None, p.h
            line = clean_contents[p_offset]
            if p.h.startswith('@clean'):
                assert line == '@language python\n', (p_offset, repr(p.h), repr(line))
            else:
                # print(f"{p.h:10} {p_offset:3} {line}")
                assert p.h in line, (p_offset, repr(p.h), repr(line))
    #@-others
#@-others
#@-leo
