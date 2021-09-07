# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20201129023817.1: * @file leoTest2.py
#@@first
"""
Support for Leo's new unit tests, contained in leo/unittests/test_*.py.

Run these tests using unittest or pytest from the command line.
See g.run_unit_tests and g.run_coverage_tests.

This file also contains classes that convert @test nodes in unitTest.leo to
tests in leo/unittest. Eventually these classes will move to scripts.leo.
"""
import textwrap
import time
import unittest
from leo.core import leoGlobals as g
from leo.core import leoApp

#@+others
#@+node:ekr.20201130195111.1: ** function.create_app
def create_app():
    """
    Create the Leo application, g.app, the Gui, g.app.gui, and a commander.
    
    This method is expensive (0.5 sec) only the first time it is called.
    
    Thereafter, recreating g.app, g.app.gui, and new commands is fast.
    """
    trace = False
    t1 = time.process_time()
    # Create g.app now, to avoid circular dependencies.
    g.app = leoApp.LeoApp()
    # Late imports.
    from leo.core import leoConfig
    from leo.core import leoNodes
    from leo.core import leoCommands
    from leo.core import leoGui
    t2 = time.process_time()
    g.app.recentFilesManager = leoApp.RecentFilesManager()
    g.app.loadManager = leoApp.LoadManager()
    g.app.loadManager.computeStandardDirectories()
    if not g.app.setLeoID(useDialog=False, verbose=True):
        raise ValueError("unable to set LeoID.")
    g.app.nodeIndices = leoNodes.NodeIndices(g.app.leoID)
    g.app.config = leoConfig.GlobalConfigManager()
    g.app.db = g.NullObject('g.app.db')
    g.app.pluginsController = g.NullObject('g.app.pluginsController')
    g.app.commander_cacher = g.NullObject('g.app.commander_cacher')
    g.app.gui = leoGui.NullGui()
    t3 = time.process_time()
    # Create a dummy commander, to do the imports in c.initObjects.
    c = leoCommands.Commands(fileName=None, gui=g.app.gui)
    t4 = time.process_time()
    # Trace times. This trace happens only once:    
    #     imports: 0.016
    #         gui: 0.000
    #   commander: 0.469
    #       total: 0.484
    if trace and t4 - t3 > 0.1:
        print('create_app:\n'
            f"  imports: {(t2-t1):.3f}\n"
            f"      gui: {(t3-t2):.3f}\n"
            f"commander: {(t4-t2):.3f}\n"
            f"    total: {(t4-t1):.3f}\n")
    return c
#@+node:ekr.20210902014907.1: ** class LeoUnitTest(unittest.TestCase)
class LeoUnitTest(unittest.TestCase):
    """
    The base class for all unit tests in Leo.
    
    Contains setUp/tearDown methods and various utilites.
    """
    #@+others
    #@+node:ekr.20210901140855.2: *3* LeoUnitTest.setUp, tearDown & setUpClass
    @classmethod
    def setUpClass(cls):
        create_app()

    def setUp(self):
        """Create the nodes in the commander."""
        # Do the import here to avoid circular dependencies.
        from leo.core import leoCommands
        # Create a new commander for each test.
        # This is fast, because setUpClass has done all the imports.
        self.c = c = leoCommands.Commands(fileName=None, gui=g.app.gui)
        c.selectPosition(c.rootPosition())
        g.unitTesting = True

    def tearDown(self):
        self.c = None
        g.unitTesting = False
    #@+node:ekr.20210830151601.1: *3* LeoUnitTest.create_test_outline
    def create_test_outline(self):
        c, p = self.c, self.c.p
        self.assertEqual(p.h, 'NewHeadline')
        p.h = 'root'
        # Create the following outline:
        #
        # test-outline: root
        #   child clone a
        #     node clone 1
        #   child b
        #     child clone a
        #       node clone 1
        #   child c
        #     node clone 1
        #   child clone a
        #     node clone 1
        #   child b
        #     child clone a
        #       node clone 1
        self.test_outline = textwrap.dedent('''\
    <?xml version="1.0" encoding="utf-8"?>
    <!-- Created by Leo: http://leoeditor.com/leo_toc.html -->
    <leo_file xmlns:leo="http://leoeditor.com/namespaces/leo-python-editor/1.1" >
    <leo_header file_format="2"/>
    <vnodes>
    <v t="ekr.20210830152319.1"><vh>test-outline: root</vh>
    <v t="ekr.20210830152337.1"><vh>child clone a</vh>
    <v t="ekr.20210830152411.1"><vh>node clone 1</vh></v>
    </v>
    <v t="ekr.20210830152343.1"><vh>child b</vh>
    <v t="ekr.20210830152337.1"></v>
    </v>
    <v t="ekr.20210830152347.1"><vh>child c</vh>
    <v t="ekr.20210830152411.1"></v>
    </v>
    <v t="ekr.20210830152337.1"></v>
    <v t="ekr.20210830152343.1"></v>
    </v>
    </vnodes>
    <tnodes>
    <t tx="ekr.20210830152319.1"></t>
    <t tx="ekr.20210830152337.1"></t>
    <t tx="ekr.20210830152343.1"></t>
    <t tx="ekr.20210830152347.1"></t>
    <t tx="ekr.20210830152411.1"></t>
    </tnodes>
    </leo_file>
    ''')
        # pylint: disable=no-member
        c.pasteOutline(s=self.test_outline, redrawFlag=False, undoFlag=False)
        c.selectPosition(c.rootPosition())
    #@+node:ekr.20210831101111.1: *3* LeoUnitTest.dump_tree
    def dump_tree(self, tag=''):
        c = self.c
        print('')
        g.trace(tag)
        for p in c.all_positions():
            print(f"clone? {int(p.isCloned())} {' '*p.level()} {p.h}")
    #@-others
#@-others
#@-leo
