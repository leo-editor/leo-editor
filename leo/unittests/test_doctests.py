# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20210926044012.1: * @file ../unittests/test_doctests.py
#@@first
"""Run all doctests in Leo's core."""
import doctest
import unittest
from leo.core import leoGlobals as g
### import leo.plugins as plugins
import leo


class TestDocTests(unittest.TestCase):  # Not a subclass of leoTest2.LeoUnitTest.

    def test_all_doctests(self):
        print('\n\n===== test_all_doctests\n\n')
        finder = doctest.DocTestFinder()
        g.printObj(finder.find(leo))

        ## leo.plugins.importers.javascript
#@-leo
