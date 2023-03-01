#@+leo-ver=5-thin
#@+node:ekr.20210911052754.1: * @file ../unittests/core/test_leoExternalFiles.py
"""Tests of leoExternalFiles.py"""

from leo.core import leoGlobals as g
import leo.core.leoApp as leoApp
from leo.core.leoTest2 import LeoUnitTest
import leo.core.leoExternalFiles as leoExternalFiles

#@+others
#@+node:ekr.20210911052754.2: ** class TestExternalFiles (LeoUnitTest)
class TestExternalFiles(LeoUnitTest):
    #@+others
    #@+node:ekr.20210911052754.3: *3* TestExternalFiles.setUp
    def setUp(self):
        """setUp for TestFind class"""
        super().setUp()
        c = self.c
        g.app.idleTimeManager = leoApp.IdleTimeManager()
        g.app.idleTimeManager.start()
        g.app.externalFilesController = leoExternalFiles.ExternalFilesController(c=c)
    #@+node:ekr.20210911052754.4: *3* TestExternalFiles.test_on_idle
    def test_on_idle(self):
        """
        A minimal test of the on_idle and all its helpers.

        More detail tests would be difficult.
        """
        efc = g.app.externalFilesController
        for i in range(100):
            efc.on_idle()
    #@-others
#@-others
#@-leo
