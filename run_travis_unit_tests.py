# -*- coding: utf-8 -*-
import leo.core.leoBridge as leoBridge
import os
import sys
# import pdb ; pdb.set_trace()
import unittest

load_dir = os.path.abspath(os.path.dirname(__file__))
test_dir = os.path.join(load_dir, 'leo', 'test')
path = os.path.join(test_dir, 'unitTest.leo')
assert os.path.exists(path), repr(path)
controller = leoBridge.controller(gui='nullGui',
    loadPlugins=False, readSettings=True,
    silent=False, verbose=False)
g = controller.globals()
c = controller.openLeoFile(path)
try:
    # Run all unit tests locally.
    root = g.findTopLevelNode(c, 'Active Unit Tests', exact=True)
    assert root, 'Not found: Active Unit Tests'
    c.selectPosition(root)
    tm = c.testManager
    g.unitTesting = g.app.unitTesting = True
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
    if not found:
        print('No unit tests')
        sys.exit(1)
    runner = unittest.TextTestRunner(failfast=True, verbosity=1)
    try:
        result = runner.run(suite)
        if result.errors or result.failures:
            print(f'errors: {len(result.errors)}, failures: {len(result.failures)}')
            sys.exit(1)
        else:
            print('Travis unit tests all passed.')
            sys.exit(0)
    except Exception:
        print('Unexpected exception')
        g.es_exception()
        sys.exit(1)
except Exception as e:
    print('Unexpected exception 2', e)
    sys.exit(1)
