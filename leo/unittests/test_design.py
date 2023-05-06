#@+leo-ver=5-thin
#@+node:ekr.20230506095312.1: * @file ../unittests/test_design.py
"""Global design tests."""
import unittest
from leo.core import leoGlobals as g
assert g

#@+others
#@+node:ekr.20230506095516.1: ** class TestAnnotations(unittest.TestCase)
class TestAnnotations(unittest.TestCase):
    """Test that annotations of c, g, p, s, v are as expected."""
#@+node:ekr.20230506095648.1: ** class TestChains(unittest.TestCase)
class TestChains(unittest.TestCase):
    """Ensure that only certain chains exist."""
#@-others
#@-leo
