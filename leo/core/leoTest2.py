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
    # Early imports.
    from leo.core import leoGlobals as g
    from leo.core import leoApp
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
    g.app.db = g.TracingNullObject('g.app.db')
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
    
    Contains standard setUp/tearDown methods and various utilites.
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
#@+node:ekr.20210902013852.1: ** Coverter classes
# Classes to convert tests in unitTest.leo to proper unit tests.

# Eventually these classes will move to scripts.leo.
#@+node:ekr.20201202083003.1: *3* class ConvertTests
class ConvertTests:
    """
    A class that converts @test nodes to proper unit tests.
    
    Subclasses specialize the convert method.
    
    These scripts know nothing about the unit tests they create. They just
    pass the data from the old tests to the new tests using args in the
    run_test method.
    """
    
    class_name = "XXX_Test"  # To be changed with search/replace!
    
    #@+others
    #@+node:ekr.20201130075024.2: *4* ConvertTests.body
    def body(self, after_p, after_sel, before_p, before_sel, command_name):
        """Return the body of the test"""
        real_command_name = command_name.split(' ')[0]
        sel11, sel12 = before_sel.split(',')
        sel21, sel22 = after_sel.split(',')
        delim = "'''" if '"""' in before_p.b else '"""'
        return (
            f"def test_{self.function_name(command_name)}(self):\n"
            f'    """Test case for {command_name}"""\n'
            f'    before_b = {delim}\\\n'
            f"{before_p.b}"
            f'{delim}\n'
            f'    after_b = {delim}\\\n'
            f"{after_p.b}"
            f'{delim}\n'
            f"    self.run_test(\n"
            f"        before_b=before_b,\n"
            f"        after_b=after_b,\n"
            f'        before_sel=("{sel11}", "{sel12}"),\n'
            f'        after_sel=("{sel21}", "{sel22}"),\n'
            f'        command_name="{real_command_name}",\n'
            f"    )\n"
        )
    #@+node:ekr.20210829142807.1: *4* ConvertTests.clean_headline
    def clean_headline(self, p):
        """Make p.h suitable as a function.name."""
        h = p.h
        assert h.startswith('@test')
        h = h[len('@test'):].strip()
        result = []
        for ch in h:
            if ch.isalnum():
                result.append(ch)
            else:
                result.append('_')
        return ''.join(result).replace('__', '_')
    #@+node:ekr.20210902014405.1: *4* ConvertTests.convert_nodes
    def convert_nodes(self, c, root):
        """
        Use converter.convert() to convert all the @test nodes in the
        root's tree to children a new last top-level node.
        """
        if not root:
            print('no root')
            return
        last = c.lastTopLevel()
        target = last.insertAfter()
        target.h = 'Converted nodes'
        count = 0
        for p in root.subtree():
            if p.h.startswith('@test'):
                self.convert_node(p, target)
                count += 1
        target.expand()
        c.redraw(target)
        print(f"converted {count} @test nodes")
    #@+node:ekr.20210829142231.2: *4* ConvertTests.convert_node
    def convert_node(self, p, target):
        """
        Convert p, an @test node, creating a new node as the last child of
        target.
        
        May be overridden in subclasses.
        """
        # Calculate the headline and body text.
        test_name = f"test_{self.clean_headline(p)}"
        body = textwrap.indent(p.b, ' '*4).rstrip()
        # Create the new node.
        test_node = target.insertAsLastChild()
        test_node.h = f"{self.class_name}.{test_name}"
        test_node.b = f"def {test_name}(self):\n{body}\n"
    #@+node:ekr.20201130075024.5: *4* ConvertTests.function_name
    def function_name(self, command_name):
        """Convert a command name into a test function."""
        result = []
        parts = command_name.split('-')
        for part in parts:
            s = part.replace('(', '').replace(')', '')
            inner_parts = s.split(' ')
            result.append('_'.join(inner_parts))
        return '_'.join(result)
    #@-others
#@+node:ekr.20201202083553.1: *3* class ConvertEditCommandsTests (ConvertTests)
class ConvertEditCommandsTests(ConvertTests):

    #@+others
    #@+node:ekr.20201130075024.4: *4* ConvertEditCommandsTests.convert_node
    def convert_node(self, p, target):
        """Convert one @test node, creating a new node."""
        after_p, before_p = None, None
        after_sel, before_sel = None, None
        assert p.h.startswith('@test')
        command_name = p.h[len('@test') :].strip()
        for child in p.children():
            if child.h.startswith('after'):
                after_p = child.copy()
                after_sel = child.h[len('after') :].strip()
                after_sel = after_sel.replace('sel=', '').strip()
            elif child.h.startswith('before'):
                before_p = child.copy()
                before_sel = child.h[len('before') :].strip()
                before_sel = before_sel.replace('sel=', '').strip()
        assert before_p and after_p
        assert before_sel and after_sel
        new_child = target.insertAsLastChild()
        new_child.h = command_name
        new_child.b = self.body(after_p, after_sel, before_p, before_sel, command_name)
    #@-others
#@-others
#@-leo
