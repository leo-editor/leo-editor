# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20210926044012.1: * @file ../unittests/test_doctests.py
#@@first
"""Run all doctests in Leo's core."""
import doctest
import unittest
from leo.core import leoGlobals as g
import leo

# The doctest finder should find the doctests in this function.
#@+<< define factorial >>
#@+node:ekr.20210926053601.1: ** << define factorial >>
def factorial(n):
    """Return the factorial of n, an exact integer >= 0.

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
    """

    import math
    if not n >= 0:
        raise ValueError("n must be >= 0")
    if math.floor(n) != n:
        raise ValueError("n must be exact integer")
    if n+1 == n:  # catch a value like 1e300
        raise OverflowError("n too large")
    result = 1
    factor = 2
    while factor <= n:
        result *= factor
        factor += 1
    return result
#@-<< define factorial >>

class TestDocTests(unittest.TestCase):  # Not a subclass of leoTest2.LeoUnitTest.

    def test_all_doctests(self):
        finder = doctest.DocTestFinder()
        g.printObj(finder.find(leo), tag='doctests')
#@-leo
