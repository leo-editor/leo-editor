# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20201203042030.1: * @file ../unittests/core/test_leoNodes.py
#@@first
"""Tests for leo.core.leoNodes"""
import unittest
from leo.core import leoGlobals as g
from leo.core import leoTest2

#@+others
#@+node:ekr.20210828112210.1: ** class NodesTest
class NodesTest(unittest.TestCase):
    """Unit tests for leo/core/leoNodes.py."""
    #@+others
    #@+node:ekr.20210828080615.1: *3* NodesTest: setUp, tearDown...
    #@+node:ekr.20201203042409.2: *4* NodesTest.run_test
    def run_test(self):
        c = self.c
        assert c
    #@+node:ekr.20201203042409.3: *4* NodesTest.setUp & tearDown
    def setUp(self):
        """Create the nodes in the commander."""
        # Create a new commander for each test.
        # This is fast, because setUpClass has done all the imports.
        from leo.core import leoCommands
        self.c = c = leoCommands.Commands(fileName=None, gui=g.app.gui)
        c.selectPosition(c.rootPosition())

    def tearDown(self):
        self.c = None
    #@+node:ekr.20201203042409.4: *4* NodesTest.setUpClass
    @classmethod
    def setUpClass(cls):
        leoTest2.create_app()
    #@+node:ekr.20201203042550.1: *3* NodesTest.test_test
    def test_test(self):
        self.run_test()
    #@+node:ekr.20210828075915.1: *3* NodesTest.test_all_nodes_coverage
    def test_all_nodes_coverage(self):
        # @test c iters: <coverage tests>
        c = self.c
        #@+<< define s >>
        #@+node:ekr.20210828113536.1: *4* << define s >>
        # All inner ''' must be escaped to, say, '\''.
        s = '''\
        <?xml version="1.0" encoding="utf-8"?>
        <!-- Created by Leo: http://leoeditor.com/leo_toc.html -->
        <leo_file xmlns:leo="http://leoeditor.com/namespaces/leo-python-editor/1.1" >
        <leo_header file_format="2"/>
        <vnodes>
        <v t="ekr.20210828112210.1"><vh>class NodesTest</vh>
        <v t="ekr.20210828080615.1"><vh>NodesTest: setUp, tearDown...</vh>
        <v t="ekr.20201203042409.2"><vh>NodesTest.run_test</vh></v>
        <v t="ekr.20201203042409.3"><vh>NodesTest.setUp &amp; tearDown</vh></v>
        <v t="ekr.20201203042409.4"><vh>NodesTest.setUpClass</vh></v>
        </v>
        <v t="ekr.20201203042550.1"><vh>NodesTest.test_test</vh></v>
        <v t="ekr.20210828075915.1"><vh>NodesTest.test_all_nodes_coverage</vh>
        <v t="ekr.20210828113536.1"><vh>&lt;&lt; define s &gt;&gt;</vh></v>
        </v>
        </v>
        </vnodes>
        <tnodes>
        <t tx="ekr.20201203042409.2">def run_test(self):
            c = self.c
            assert c
        </t>
        <t tx="ekr.20201203042409.3">def setUp(self):
            """Create the nodes in the commander."""
            # Create a new commander for each test.
            # This is fast, because setUpClass has done all the imports.
            from leo.core import leoCommands
            self.c = c = leoCommands.Commands(fileName=None, gui=g.app.gui)
            c.selectPosition(c.rootPosition())

        def tearDown(self):
            self.c = None
        </t>
        <t tx="ekr.20201203042409.4">@classmethod
        def setUpClass(cls):
            leoTest2.create_app()
        </t>
        <t tx="ekr.20201203042550.1">def test_test(self):
            self.run_test()
        </t>
        <t tx="ekr.20210828075915.1">def test_all_nodes_coverage(self):
            # @test c iters: &lt;coverage tests&gt;
            g.cls()
            c = self.c
            &lt;&lt; define s &gt;&gt;
            leoTest2.create_outline(c, s)
            v1 = [p.v for p in c.all_positions()]
            v2 = [v for v in c.all_nodes()]
            g.printObj([z.h for z in c.all_positions()])
            for v in v2:
                self.assertTrue(v in v1)
            for v in v1:
                self.assertTrue(v in v2)
        </t>
        <t tx="ekr.20210828080615.1"></t>
        <t tx="ekr.20210828112210.1">class NodesTest(unittest.TestCase):
            """Unit tests for leo/core/leoNodes.py."""
            #@+others
            #@-others
        </t>
        <t tx="ekr.20210828113536.1">s = '\''\
        &lt;?xml version="1.0" encoding="utf-8"?&gt;
        &lt;!-- Created by Leo: http://leoeditor.com/leo_toc.html --&gt;
        &lt;leo_file xmlns:leo="http://leoeditor.com/namespaces/leo-python-editor/1.1" &gt;
        &lt;leo_header file_format="2"/&gt;
        &lt;vnodes&gt;
        &lt;v t="ekr.20031218072017.1551"&gt;&lt;vh&gt;c_oc.pasteOutline&lt;/vh&gt;&lt;/v&gt;
        &lt;/vnodes&gt;
        &lt;tnodes&gt;
        &lt;t tx="ekr.20031218072017.1551"&gt;@g.commander_command('paste-node')
        def pasteOutline(self,
        event=None,
        redrawFlag=True,
        s=None,
        undoFlag=True
        ):
        """
        Paste an outline into the present outline from the clipboard.
        Nodes do *not* retain their original identify.
        """
        c = self
        if s is None:
            s = g.app.gui.getTextFromClipboard()
        c.endEditing()
        if not s or not c.canPasteOutline(s):
            return None  # This should never happen.
        isLeo = g.match(s, 0, g.app.prolog_prefix_string)
        if not isLeo:
            return None
        # Get *position* to be pasted.
        pasted = c.fileCommands.getLeoOutlineFromClipboard(s)
        if not pasted:
            # Leo no longer supports MORE outlines. Use import-MORE-files instead.
            return None
        # Validate.
        c.validateOutline()
        c.checkOutline()
        # Handle the "before" data for undo.
        if undoFlag:
            undoData = c.undoer.beforeInsertNode(c.p,
                pasteAsClone=False,
                copiedBunchList=[],
            )
        # Paste the node into the outline.
        c.selectPosition(pasted)
        pasted.setDirty()
        c.setChanged(redrawFlag=redrawFlag)
            # Prevent flash when fixing #387.
        back = pasted.back()
        if back and back.hasChildren() and back.isExpanded():
            pasted.moveToNthChildOf(back, 0)
        # Finish the command.
        if undoFlag:
            c.undoer.afterInsertNode(pasted, 'Paste Node', undoData)
        if redrawFlag:
            c.redraw(pasted)
            c.recolor()
        return pasted
        &lt;/t&gt;
        &lt;/tnodes&gt;
        &lt;/leo_file&gt;
        '\''
        </t>
        </tnodes>
        </leo_file>
        '''
        #@-<< define s >>
        leoTest2.create_outline(c, s)
        v1 = [p.v for p in c.all_positions()]
        v2 = [v for v in c.all_nodes()]
        # g.printObj([z.h for z in c.all_positions()])
        for v in v2:
            self.assertTrue(v in v1)
        for v in v1:
            self.assertTrue(v in v2)
    #@-others
#@-others

#@-leo
