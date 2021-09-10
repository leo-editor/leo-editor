# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20210910065135.1: * @file ../unittests/core/test_leoFileCommands.py
#@@first
"""Tests of leoFileCommands.py"""

from leo.core import leoGlobals as g
import leo.core.leoApp as leoApp
from leo.core.leoTest2 import LeoUnitTest
import leo.core.leoExternalFiles as leoExternalFiles

#@+others
#@+node:ekr.20210910065135.2: ** class TestFileCommands (LeoUnitTest)
class TestFileCommands(LeoUnitTest):
    #@+others
    #@+node:ekr.20210910065135.3: *3* TestFileCommands.setUp
    def setUp(self):
        """setUp for TestFind class"""
        super().setUp()
        c = self.c
        g.app.idleTimeManager = leoApp.IdleTimeManager()
        g.app.idleTimeManager.start()
        g.app.externalFilesController = leoExternalFiles.ExternalFilesController(c=c)
    #@-others
#@-others
#@-leo
