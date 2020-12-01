# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20201129023817.1: * @file leoTest2.py
#@@first
#@+<< docstring >>
#@+node:ekr.20201129162306.1: ** << docstring >>
"""
Support for coverage tests embedded in Leo's source files.

The general pattern is inspired by the coverage tests in leoAst.py.

Each of Leo's source files will end with:
    
    if __name__ == '__main__':
        run_unit_tests()
        
Full unit tests for x.py can be run from the command line:
    
    python -m leo.core.x
"""
#@-<< docstring >>
#@+<< imports >>
#@+node:ekr.20201129131605.1: ** << imports >> (leoTest2.py)
import leo.core.leoGlobals as g
# import leo.core.leoGui as leoGui  # For UnitTestGui.
# import difflib
# import logging
# import cProfile as profile
import os
# import re
import sys
# import tabnanny
import time
# import timeit
# import tokenize
# import traceback
import unittest
#@-<< imports >>
#@+others
#@+node:ekr.20201129132455.1: ** Top-level functions...
#@+node:ekr.20201130074836.1: *3* function: convert_leoEditCommands_tests
def convert_leoEditCommands_tests(c):
    """Convert old-style tests to new-style tests"""
    root = g.findTopLevelNode(c, 'unit-tests: leoEditCommands')
    target = g.findTopLevelNode(c, 'new-tests')
    #@+others
    #@+node:ekr.20201130075024.2: *4* body
    def body(after_p, after_sel, before_p, before_sel, command_name):
        """Return the body of the test"""
        real_command_name = command_name.split(' ')[0]
        sel11, sel12 = before_sel.split(',')
        sel21, sel22 = after_sel.split(',')
        delim = "'''" if '"""' in before_p.b else '"""'
        return (
            f"def test_{function_name(command_name)}(self):\n"
            f'    """Test case for {command_name}"""\n'
            f'    before_b = {delim}\\\n'
            f"{before_p.b}"
            f'{delim}\n'
            f'    after_b = {delim}\\\n'
            f"{after_p.b}"
            f'{delim}\n'
            f"    self.run_test(\n"
            f"        before_b=before_b,\n"
            f"        after_b=after_b,\n"
            f'        before_sel=("{sel11}", "{sel12}"),\n'
            f'        after_sel=("{sel21}", "{sel22}"),\n'
            f'        command_name="{real_command_name}",\n'
            f"    )\n"
        )
    #@+node:ekr.20201130075024.3: *4* class_name (not used)
    def class_name(command_name):
        """Convert the command name to a class name."""
        result = []
        parts = command_name.split('-')
        for part in parts:
            s = part.replace('(','').replace(')','')
            inner_parts = s.split(' ')
            result.append(''.join([z.capitalize() for z in inner_parts]))
        return ''.join(result)
    #@+node:ekr.20201130075024.4: *4* convert
    def convert(p):
        after_p, before_p = None, None
        after_sel, before_sel = None, None
        assert p.h.startswith('@test')
        command_name = p.h[len('@test'):].strip()
        for child in p.children():
            if child.h.startswith('after'):
                after_p = child.copy()
                after_sel= child.h[len('after'):].strip()
                after_sel = after_sel.replace('sel=','').strip()
            elif child.h.startswith('before'):
                before_p = child.copy()
                before_sel = child.h[len('before'):].strip()
                before_sel = before_sel.replace('sel=','').strip()
        assert before_p and after_p
        assert before_sel and after_sel
        new_child = target.insertAsLastChild()
        new_child.h = command_name
        new_child.b = body(after_p, after_sel, before_p, before_sel, command_name)
            
    #@+node:ekr.20201130075024.5: *4* function_name
    def function_name(command_name):
        """Convert a command name into a test function."""
        result = []
        parts = command_name.split('-')
        for part in parts:
            s = part.replace('(','').replace(')','')
            inner_parts = s.split(' ')
            result.append('_'.join(inner_parts))
        return '_'.join(result)
    #@-others
    count = 0
    if root and target:
        target.deleteAllChildren()
        for p in root.subtree():
            if p.h.startswith('@test') and 'runEditCommandTest' in p.b:
                convert(p)
                count += 1
        c.redraw()
        print(f"converted {count} @test nodes")
    else:
        print('Error: root and target nodes must be top-level nodes.')
#@+node:ekr.20201130195111.1: *3* function: create_app
def create_app():
    """
    Create the Leo application, g.app, the Gui, g.app.gui, and a commander.
    
    Return the commander.
    
    This method is expensive (about 1 sec) only the first time it is called.
    """
    # Similar to leoBridge.py
    # print('CommanderTest.setUp')
    import time
    t1 = time.process_time()
    import leo.core.leoGlobals as g
    import leo.core.leoApp as leoApp
    import leo.core.leoConfig as leoConfig
    import leo.core.leoNodes as leoNodes
    import leo.core.leoCommands as leoCommands
    import leo.core.leoGui as leoGui
    t2 = time.process_time()
    g.app = leoApp.LeoApp()
    g.app.recentFilesManager = leoApp.RecentFilesManager()
    g.app.loadManager = leoApp.LoadManager()
    g.app.loadManager.computeStandardDirectories()
    if not g.app.setLeoID(useDialog=False, verbose=True):
        raise ValueError("unable to set LeoID.")
    g.app.nodeIndices = leoNodes.NodeIndices(g.app.leoID)
    g.app.config = leoConfig.GlobalConfigManager()
    g.app.db = g.TracingNullObject('g.app.db')
    g.app.pluginsController = g.NullObject('g.app.pluginsController')
    g.app.commander_cacher = g.NullObject('g.app.commander_cacher')
    g.app.gui=leoGui.NullGui()
    t3 = time.process_time()
    # Create a dummy commander, to do the imports in c.initObjects.
    leoCommands.Commands(fileName=None, gui=g.app.gui)
    t4 = time.process_time()
    if t4 - t3 > 0.1:
        print('create_app\n'
            f"  imports: {(t2-t1):.3f}\n"
            f"      gui: {(t3-t2):.3f}\n"
            f"commander: {(t4-t2):.3f}\n"
            f"    total: {(t4-t1):.3f}\n")
#@+node:ekr.20201129133424.6: *3* function: expected_got
def expected_got(expected, got):
    """Return a message, mostly for unit tests."""
    #
    # Let block.
    e_lines = g.splitLines(expected)
    g_lines = g.splitLines(got)
    #
    # Print all the lines.
    result = ['\n']
    result.append('Expected:\n')
    for i, z in enumerate(e_lines):
        result.extend(f"{i:3} {z!r}\n")
    result.append('Got:\n')
    for i, z in enumerate(g_lines):
        result.extend(f"{i:3} {z!r}\n")
    #
    # Report first mismatched line.
    for i, data in enumerate(zip(e_lines, g_lines)):
        e_line, g_line = data
        if e_line != g_line:
            result.append(f"\nFirst mismatch at line {i}\n")
            result.append(f"expected: {i:3} {e_line!r}\n")
            result.append(f"     got: {i:3} {g_line!r}\n")
            break
    else:
        result.append('\nDifferent lengths\n')
    return ''.join(result)
#@+node:ekr.20201129133502.1: *3* function: get_time
def get_time():
    return time.process_time()
#@+node:ekr.20201129132511.1: *3* function: pytest_main
def pytest_main(path, module):
    """Run selected unit tests with pytest-cov"""
    g.cls()
    try:
        import pytest
    except Exception:
        print('pytest not found')
        return
    if 0:
        # Pytest.
        pytest.main(args=sys.argv)
    elif 1: # unittest
        unittest.main()
    else: # Full coverage test.
        pycov_args = sys.argv + [
            '--cov-report=html',
            '--cov-report=term-missing',
            f'--cov={module}',
            __file__,
        ]
        pytest.main(args=pycov_args)
#@+node:ekr.20201130215055.1: *3* function: run_all_tests
def run_all_tests():
    pass
    
#@+node:ekr.20201201085828.1: ** class RunAllLeoTests(unittest.TestCase)
class RunAllLeoTests(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        print('RunAllLeoTests.setUpClass', cls)
        create_app()
        
    def setUp(self):
        self._leo_dir = os.path.join(os.path.dirname(__file__), '..')
        # import leo.core.leoCommands as leoCommands
        # self.c = c = leoCommands.Commands(fileName=None, gui=g.app.gui)
        
    def test_all_core_files(self):
        import glob
        files = glob.glob(os.path.join(self._leo_dir, 'core', '*.py'))
        for fn in ('__init__.py', 'leoAst_ns.py', 'leoTest.py', 'leoTest2.py'):
            path = os.path.join(self._leo_dir, 'core', fn)
            if path in files:
                files.remove(path)
        for z in files:
            fn = os.path.basename(z)
            suite = unittest.TestLoader().discover(
                start_dir=self._leo_dir, pattern=fn)
            result = unittest.TestResult()
            suite.run(result)
            if result.testsRun:
                run = result.testsRun
                errors = result.errors
                failures = result.failures
                skipped = result.skipped
                g.trace(
                    f"{fn:>20} "
                    f"run: {run:>3}, "
                    f"errors: {len(errors):>2}, "
                    f"failures: {len(failures):>2}, "
                    f"skipped: {len(skipped):>2}"
                )

    def test_all_commands_files(self):
        suite = unittest.TestLoader().discover(
            start_dir=os.path.join(self._leo_dir, 'commands'),
            pattern='editCommands.py',
        )
        # g.trace(f"{suite.countTestCases()} tests in leo/commands")
        result = unittest.TestResult()
        suite.run(result)
        if result.testsRun:
            g.trace(result)
#@+node:ekr.20201129161531.1: ** class TestUtils(unittest.TestCase)
class TestUtils(unittest.TestCase):
    """
    Utilities for test class.
    
    This class has no "organizational" consequences because it contains no
    setUp/tearDown methods.
    """
    #@+others
    #@+node:ekr.20201129195238.1: *3* BaseUnitTest.compareOutlines
    def compareOutlines(self, root1, root2, compareHeadlines=True, tag='', report=True):
        """
        Compares two outlines, making sure that their topologies, content and
        join lists are equivalent
        """
        p2 = root2.copy()
        ok = True
        p1 = None
        for p1 in root1.self_and_subtree():
            b1 = p1.b
            b2 = p2.b
            if p1.h.endswith('@nonl') and b1.endswith('\n'):
                b1 = b1[:-1]
            if p2.h.endswith('@nonl') and b2.endswith('\n'):
                b2 = b2[:-1]
            ok = (
                p1 and p2
                and p1.numberOfChildren() == p2.numberOfChildren()
                and (not compareHeadlines or (p1.h == p2.h))
                and b1 == b2
                and p1.isCloned() == p2.isCloned()
            )
            if not ok: break
            p2.moveToThreadNext()
        if report and not ok:
            g.pr('\ncompareOutlines failed: tag:', (tag or ''))
            g.pr('p1.h:', p1 and p1.h or '<no p1>')
            g.pr('p2.h:', p2 and p2.h or '<no p2>')
            g.pr(f"p1.numberOfChildren(): {p1.numberOfChildren()}")
            g.pr(f"p2.numberOfChildren(): {p2.numberOfChildren()}")
            if b1 != b2:
                self.showTwoBodies(p1.h, p1.b, p2.b)
            if p1.isCloned() != p2.isCloned():
                g.pr('p1.isCloned() == p2.isCloned()')
        return ok
    #@+node:ekr.20201129204348.1: *3* BaseUnitTest.showTwoBodies
    def showTwoBodies(self, t, b1, b2):
        print('\n', '-' * 20)
        print(f"expected for {t}...")
        for line in g.splitLines(b1):
            print(f"{len(line):3d}", repr(line))
        print('-' * 20)
        print(f"result for {t}...")
        for line in g.splitLines(b2):
            print(f"{len(line):3d}", repr(line))
        print('-' * 20)
    #@+node:ekr.20201129205031.1: *3* BaseUnitTest.adjustTripleString
    def adjustTripleString(self, s):
        return g.adjustTripleString(s, tab_width=-4)
    #@-others
#@-others
if __name__ == '__main__':
    pytest_main(__file__, 'leo.core.leoTest2')
#@-leo
