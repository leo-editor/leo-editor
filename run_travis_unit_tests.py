#@+leo-ver=5-thin
#@+node:ekr.20181009072707.1: * @file ../../run_travis_unit_tests.py
# -*- coding: utf-8 -*-
import os
import sys
import unittest
from leo.core import leoBridge
# Open the bridge.
controller = leoBridge.controller(gui='nullGui',
    loadPlugins=False, readSettings=True,
    silent=False, verbose=False)
g = controller.globals()
#@+others
#@+node:ekr.20210910180232.1: ** function: get_legacy_suite
def get_legacy_suite(c):
    # Run all unit tests locally.
    root = g.findTopLevelNode(c, 'Active Unit Tests', exact=True)
    assert root, 'Not found: Active Unit Tests'
    c.selectPosition(root)
    tm = c.testManager
    ###g.unitTesting = g.app.unitTesting = True
    suite = unittest.makeSuite(unittest.TestCase)
    aList = tm.findAllUnitTestNodes(all=False, marked=False)
    setup_script = None
    found = False
    for p in aList:
        if tm.isTestSetupNode(p):
            setup_script = p.b
            test = None
        elif tm.isTestNode(p):
            test = tm.makeTestCase(p, setup_script)
        elif tm.isSuiteNode(p):
            test = tm.makeTestSuite(p, setup_script)
        elif tm.isTestClassNode(p):
            test = tm.makeTestClass(p)
        else:
            test = None
        if test:
            suite.addTest(test)
            found = True
    if found:
        return suite
    print('No unit tests')
    sys.exit(1)
#@+node:ekr.20210910180509.1: ** function: get_new_suite
def get_new_suite():
    suite = unittest.makeSuite(unittest.TestCase)
    ### To do.
    return suite
#@+node:ekr.20210910181115.1: ** function: open_unittest_dot_leo
def open_unittest_dot_leo():
    """open unitTest.leo and return its commander."""
    load_dir = os.path.abspath(os.path.dirname(__file__))
    test_dir = os.path.join(load_dir, 'leo', 'test')
    path = os.path.join(test_dir, 'unitTest.leo')
    assert os.path.exists(path), repr(path)
    c = controller.openLeoFile(path)
    assert c
    return c
#@-others
try:
    g.unitTesting = g.app.unitTesting = True
    if 1:
        suite = get_new_suite()
    else:
        c = open_unittest_dot_leo()
    suite = get_legacy_suite(c)
    runner = unittest.TextTestRunner(failfast=True, verbosity=1)
    result = runner.run(suite)
    if result.errors or result.failures:
        print(f"errors: {len(result.errors)}, failures: {len(result.failures)}")
        sys.exit(1)
    else:
        print('Travis unit tests all passed.')
        sys.exit(0)
except Exception:
    print('Unexpected exception')
    g.es_exception()
    sys.exit(1)
#@-leo
