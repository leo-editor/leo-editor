#@+leo-ver=5-thin
#@+node:ekr.20181009072707.1: * @file ../../run_travis_unit_tests.py
import os
import sys
import traceback
import unittest
tag = 'run_travis_unit_tests.py'
try:
    base_dir = os.path.dirname(__file__)
    unittests_dir = os.path.abspath(os.path.join(base_dir, 'leo', 'unittests'))
    suite = unittest.TestLoader().discover(unittests_dir)
    n = suite.countTestCases()
    assert n > 10, n
    runner = unittest.TextTestRunner(failfast=True, verbosity=1)
    result = runner.run(suite)
    if result.errors or result.failures:
        errors, fails = len(result.errors), len(result.failures)
        print(f"{tag}: {errors} errors, {fails} failures")
        sys.exit(1)
    print(f"{tag}: {n} unit tests passed.")
    sys.exit(0)
except Exception:
    typ, val, tb = sys.exc_info()
    lines = traceback.format_exception(typ, val, tb)
    print(f"{tag}: unexpected exception")
    for line in lines:
        print(line.rstrip())
    sys.exit(1)
#@-leo
