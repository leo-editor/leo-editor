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
# import os
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
#@+node:ekr.20201129132511.1: *3* function: pytest_main (leoTest2.py)
def pytest_main(path, module):
    """Run selected unit tests with pytest-cov"""
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
#@+node:ekr.20201129161531.1: **  class BaseUnitTest(unittest.TestCase)
class BaseUnitTest(unittest.TestCase):
    """The base of all new-style unit tests."""
    #@+others
    #@-others
#@+node:ekr.20201129162020.1: **  class CommanderTest(BaseUnitTest)
class CommanderTest(BaseUnitTest):
    """The base class of all tests that require a Commander object."""
    #@+others
    #@+node:ekr.20201129174457.1: *3* CommanderTest.setUp
    def setUp(self):
        # Similar to leoBridge.py
        print('CommanderTest.setUp')  ###
        import leo.core.leoGlobals as g
        import leo.core.leoApp as leoApp
        import leo.core.leoConfig as leoConfig
        import leo.core.leoNodes as leoNodes
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
        # Always allocate a new commander...
        import leo.core.leoCommands as leoCommands
        import leo.core.leoGui as leoGui
        g.app.gui=leoGui.NullGui()
        self.c = leoCommands.Commands(fileName=None, gui=g.app.gui)
    #@+node:ekr.20201129161726.8: *3* CommanderTest.tearDown (do nothing)
    def tearDown(self):
        # c = self.c
        print('CommanderTest.tearDown')
        ###
            # tempNode = self.tempNode
            # c.selectPosition(tempNode)
            # if not self.failFlag:
                # tempNode.setBodyString("")
                # # Delete all children of temp node.
                # while tempNode.firstChild():
                    # tempNode.firstChild().doDelete()
            # tempNode.clearDirty()
            # c.undoer.clearUndoState()
    #@-others
#@-others
if False and __name__ == '__main__':  # Not ready yet.
    pytest_main()
#@-leo
