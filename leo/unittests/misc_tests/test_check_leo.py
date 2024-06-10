#@+leo-ver=5-thin
#@+node:ekr.20240609044830.1: * @file ../unittests/misc_tests/test_check_leo.py
#@+<< test_check_leo.py: imports >>
#@+node:ekr.20240609050025.1: ** << test_check_leo.py: imports >>
import os
import unittest
from leo.core import leoGlobals as g
# from leo.core.leoTest2 import LeoUnitTest
import leo.scripts.check_leo as check_leo
from leo.scripts.check_leo import CheckLeo
assert check_leo
assert g
#@-<< test_check_leo.py: imports >>

#@+others
#@+node:ekr.20240609044535.1: ** class TestCheckLeo
class TestCheckLeo(unittest.TestCase):
    """Unit tests for check_leo.py"""

    def setUp(self):
        super().setUp()
        g.unitTesting = True
        self.path = path = os.path.abspath(os.path.join(
            __file__, '..', '..', '..', 'scripts', 'check_leo.py'))
        assert os.path.exists(path), path
        with open(path, 'r') as f:
            self.file_contents = f.read()
            assert self.file_contents

    #@+others
    #@+node:ekr.20240609045427.1: *3* CheckLeo.test_check_leo
    def test_check_leo(self):

        x = CheckLeo(files=[self.path])
        x.check_leo()
        if x.errors:
            self.assertEqual(x.errors, [])
    #@+node:ekr.20240609100305.1: *3* CheckLeo.test_scan_class (to do)
    def test_scan_class(self):

        x = CheckLeo(files=[self.path])
        assert x  ###
        # x.scan_class()
    #@-others
#@-others
#@-leo
