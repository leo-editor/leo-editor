#@+leo-ver=5-thin
#@+node:ekr.20181014073705.1: * @file ../../run_pytest_tests.py
import pytest
import sys
path = sys.argv[-1]
args = [
    '--quiet',
    # '--setup-plan',
    # '-x', # Exit on first error.
    path,  # File or directory
]
ignore_paths = [ ]
for ignore_path in ignore_paths:
    args.append(ignore_path)
result = pytest.main(args)
result_kinds = [
    'All tests were collected and passed successfully',
    'Tests were collected and run but some of the tests failed',
    'Test execution was interrupted by the user',
    'Internal error happened while executing tests',
    'pytest command line usage error',
    'No tests were collected',
]
message = '%s: %s:%s' % (path, result, result_kinds[result])
if result == 5:
    sys.stdout.write(message)
    sys.stdout.flush()
if result not in (1, 5):
    sys.stderr.write(message)
    sys.stdout.flush()
#@-leo
