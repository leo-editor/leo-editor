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
        
        # Add body text to each node.
        root = c.rootPosition()
        assert root.h == 'root'
        root.h = '@clean test.py'  # Make the root an @clean node.
        root.b = '@language python\n'
        for v in c.all_unique_nodes():
            for i in range(2):
               v.b += f"{v.h} line {i}\n"
        root.b += '@others\n'
        
        if 0:
            for node_i, p in enumerate(c.all_positions()):
                print(f"\nnode {node_i} {p.h}")
                for body_i, line in enumerate(g.splitLines(p.b)):
                    print(f"{body_i}: {line!r}")
        
        # Compute expected line numbers.
        expected_lines: list[list[int]] = []
        file_line_number = 0
        for p in c.all_positions():
            expected_node_lines = []
            for line in g.splitLines(p.b):
                if line.startswith('@'):
                    expected_node_lines.append(max(0, file_line_number-1))
                else:
                    expected_node_lines.append(file_line_number)
                    file_line_number += 1
            expected_lines.append(expected_node_lines)
            
        self.assertEqual(len(expected_lines), len(list(c.all_positions())))
            
        # trace/test expected line numbers:
        trace = True
        for node_i, p in enumerate(c.all_positions()):
            msg = f"node {node_i} {p.h}"
            if trace:
                print(f"\n{msg}")
            p_offset = x.find_node_start(p=p)
            self.assertFalse(p_offset is None, msg=msg)
            node_lines = g.splitLines(p.b)
            expected_node_lines = expected_lines[node_i]
            self.assertEqual(len(node_lines), len(expected_node_lines), msg=f"\nnode {node_i} {p.h}")
            for line_i, line in enumerate(node_lines):
                expected_line = expected_node_lines[line_i]
                msg = f"line {line_i}: file line: {expected_line} {line!r}"
                if trace:
                    print(msg)
                self.assertEqual(p_offset + line_i, expected_line, msg=msg)
                
        # g.printObj(expected_lines)
                    
    #@-others
#@-others
#@-leo
