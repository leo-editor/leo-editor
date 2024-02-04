#@+leo-ver=5-thin
#@+node:ekr.20210926044012.1: * @file ../unittests/misc_tests/test_doctests.py
"""Run all doctests."""
import doctest
import glob
import os
import unittest
from leo.core import leoGlobals as g

unittest_dir = os.path.dirname(__file__)
leo_dir = os.path.abspath(os.path.join(unittest_dir, '..', '..'))

#@+others  # Define a function containing a doctest.
#@+node:ekr.20210926053601.1: ** factorial (test_dectests.py)
def factorial(n):
    # Modified from https://docs.python.org/3/library/doctest.html
    # Must import factorial. See: stackoverflow.com/questions/65066002
    """Return the factorial of n, an exact integer >= 0.

    >>> from leo.unittests.misc_tests.test_doctests import factorial

    >>> [factorial(n) for n in range(6)]
    [1, 1, 2, 6, 24, 120]
    >>> factorial(30)
    265252859812191058636308480000000
    >>> factorial(-1)
    Traceback (most recent call last):
        ...
    ValueError: n must be >= 0

    Factorials of floats are OK, but the float must be an exact integer:
    >>> factorial(30.1)
    Traceback (most recent call last):
        ...
    ValueError: n must be exact integer
    >>> factorial(30.0)
    265252859812191058636308480000000

    It must also not be ridiculously large:
    >>> factorial(1e100)
    Traceback (most recent call last):
        ...
    OverflowError: n too large

    """  # Blank line above is required.

    import math
    if not n >= 0:
        raise ValueError("n must be >= 0")
    if math.floor(n) != n:
        raise ValueError("n must be exact integer")
    if n + 1 == n:  # catch a value like 1e300
        raise OverflowError("n too large")
    result = 1
    factor = 2
    while factor <= n:
        result *= factor
        factor += 1
    return result
#@-others

class TestDocTests(unittest.TestCase):  # No need to be a subclass of leoTest2.LeoUnitTest.

    def test_all_doctests(self):
        fails_list = []  # List of files with failing doctests.
        files_list = []  # List of files containing a doctest.
        n = 0  # Total doctests found
        for module in ('core', 'plugins', 'unittests'):
            module_path = os.path.join(leo_dir, module)
            self.assertTrue(os.path.exists(module_path), msg=repr(module_path))
            path = os.path.join(module_path, '**', '*.py')
            files = glob.glob(path, recursive=True)
            files = [z for z in files if not z.endswith('__init__.py')]
            for f in files:
                # Exclude two problematic files.
                if 'dtest.py' in f or 'javascript.py' in f:
                    continue
                fails, count = doctest.testfile(f, False)
                n += count
                if count:
                    files_list.append(f)
                if fails:  # pragma: no cover
                    fails_list.append(f)
                    print(f"{fails} failures in {g.shortFileName(f)}")
            self.assertEqual(fails_list, [])
        if 0:
            g.trace(f"{n} doctests found in {len(files_list)} file{g.plural(len(files_list))}")
            g.printObj(files_list, tag="files containing any doctest")
            g.printObj(fails_list, tag="files containing a failed doctest")
#@-leo
