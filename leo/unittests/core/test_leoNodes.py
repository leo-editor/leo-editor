# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20201203042030.1: * @file ../unittests/core/test_leoNodes.py
#@@first
"""Tests for leo.core.leoNodes"""
import textwrap
import unittest
from leo.core import leoGlobals as g
from leo.core import leoTest2

#@+others
#@+node:ekr.20210828112210.1: ** class NodesTest
class NodesTest(unittest.TestCase):
    """Unit tests for leo/core/leoNodes.py."""
    
    test_outline = None  # Set by create_test_outline.

    #@+others
    #@+node:ekr.20210828080615.1: *3* NodesTest: setUp, tearDown...
    #@+node:ekr.20210830151601.1: *4* NodesTest.create_test_outline
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
        if 0:
            for p in c.all_positions():
                print(f"{' '*p.level()} {p.h}")
        c.selectPosition(c.rootPosition())
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
        self.create_test_outline()
        c.selectPosition(c.rootPosition())
        g.unitTesting = True

    def tearDown(self):
        self.c = None
        g.unitTesting = False
    #@+node:ekr.20201203042409.4: *4* NodesTest.setUpClass
    @classmethod
    def setUpClass(cls):
        leoTest2.create_app()
    #@+node:ekr.20210830154328.1: *3* Completed tests
    #@+node:ekr.20210830095545.17: *4* TestNode.test_convertTreeToString_and_allies
    def test_convertTreeToString_and_allies(self):
        p = self.c.p
        sib = p.next()
        self.assertTrue(sib)
        s = sib.convertTreeToString()
        for p2 in sib.self_and_subtree():
            self.assertTrue(p2.h in s)
    #@+node:ekr.20210830095545.44: *4* TestNode.test_deleting_the_root_should_select_another_node
    def test_deleting_the_root_should_select_another_node(self):
        c, p = self.c, self.c.p
        root_h = p.h
        child = p.next()
        child.moveToRoot()  # Does not change child position.
        c.setRootPosition(child)
        self.assertTrue(c.positionExists(child))
        self.assertEqual(c.rootPosition().h, child.h)
        next = c.rootPosition().next()
        self.assertEqual(next.h, root_h)
        c.rootPosition().doDelete(newNode=next)
        c.setRootPosition(next)
    #@+node:ekr.20210830144615.1: *3* Passed tests
    if 0:
        #@+others
        #@+node:ekr.20210828075915.1: *4* NodesTest.test_all_nodes_coverage
        def test_all_nodes_coverage(self):
            # @test c iters: <coverage tests>
            c = self.c
            #@+<< define s >>
            #@+node:ekr.20210828113536.1: *5* << define s >>
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
        #@+node:ekr.20210830095545.3: *4* TestNode.test_all_generators_return_unique_positions
        def test_all_generators_return_unique_positions(self):
            # This tests a major bug in *all* generators returning positions.
            c, p = self.c, self.c.p
            root = p.firstChild().firstChild()
            table = (
                ('all_positions', c.all_positions),
                ('all_unique_positions', c.all_unique_positions),
                ('children', root.children),
                ('self_and_siblings', root.self_and_siblings),
                ('self_and_parents', root.firstChild().self_and_parents),
                ('self_and_subtree', root.self_and_subtree),
                ('following_siblings', root.following_siblings),
                ('parents', root.firstChild().firstChild().parents),
                ('unique_subtree', root.unique_subtree),
            )
            for kind, generator in table:
                aList = []
                for p in generator():
                    self.assertFalse(p in aList, msg=f"{kind} {p.gnx} {p.h}")
                    aList.append(p)
        #@+node:ekr.20210830095545.41: *4* TestNode.test_at_most_one_VNode_has_str_leo_pos_attribute
        def test_at_most_one_VNode_has_str_leo_pos_attribute(self):
            c = self.c
            n = 0
            for v in c.all_unique_vnodes_iter():
                if hasattr(v,'unknownAttributes'):
                    d = v.unknownAttributes
                    if d.get('str_leo_pos'):
                        n += 1
            assert n < 2
        #@+node:ekr.20210830095545.58: *4* TestNode.test_at_others_directive
        def test_at_others_directive(self):
            c, p = self.c, self.c.p
            root = p.copy()
            while p.hasChildren():
                p.firstChild().doDelete(newNode=None)
            try:
                p1 = p.insertAsLastChild()
                p1.setHeadString('@file zzz')
                body = '''     %s
                ''' % (chr(64) + 'others') # ugly hack
                p1.setBodyString(body)
                p2 = p1.insertAsLastChild()
                assert p1.textOffset() == 0
                assert p2.textOffset() == 5
                root.firstChild().doDelete(newNode=None)
            finally:
                if 1:
                    while root.hasChildren():
                        root.firstChild().doDelete(newNode=None)
                c.redraw_now()
        #@+node:ekr.20210830095545.6: *4* TestNode.test_c_positionExists
        def test_c_positionExists(self):
            c, p = self.c, self.c.p
            child = p.insertAsLastChild()
            assert c.positionExists(child)
            child.doDelete()
            assert not c.positionExists(child),'fail 1'

            # also check the same on root level
            child = c.rootPosition().insertAfter()
            assert c.positionExists(child)
            child.doDelete()
            assert not c.positionExists(child),'fail 2'
        #@+node:ekr.20210830095545.7: *4* TestNode.test_c_positionExists_for_all_nodes
        def test_c_positionExists_for_all_nodes(self):
            c, p = self.c, self.c.p
            for p in c.all_positions():
                assert c.positionExists(p)
                    # 2012/03/08: If a root is given, the search is confined to that root only.
        #@+node:ekr.20210830095545.8: *4* TestNode.test_c_safe_all_positions
        def test_c_safe_all_positions(self):
            c = self.c
            aList1 = list(c.all_positions())
            aList2 = list(c.safe_all_positions())
            n1,n2 = len(aList1),len(aList2)
            assert n1 == n2,(n1,n2)
        #@+node:ekr.20210830095545.9: *4* TestNode.test_check_all_gnx_s_exist_and_are_unique
        def test_check_all_gnx_s_exist_and_are_unique(self):
            c, p = self.c, self.c.p
            d = {} # Keys are gnx's, values are lists of vnodes with that gnx.
            for p in c.all_positions():
                gnx = p.v.fileIndex
                assert gnx,p.v
                aSet = d.get(gnx,set())
                aSet.add(p.v)
                d[gnx] = aSet
            for gnx in sorted(d.keys()):
                aList = sorted(d.get(gnx))
                assert len(aList) == 1,(gnx,aList)
        #@+node:ekr.20210830095545.42: *4* TestNode.test_clone_and_move_the_clone_to_the_root
        def test_clone_and_move_the_clone_to_the_root(self):
            c, p = self.c, self.c.p
            # Delete all children.
            while p.hasChildren():
                p.firstChild().doDelete(newNode=None)

            child = p.insertAsNthChild(0)
            c.setHeadString(child,'child') # Force the headline to update.

            try:
                assert child, 'no child'
                c.selectPosition(child)
                clone = c.clone()
                assert clone == c.p
                assert clone.h == 'child','fail headstring: %s' % clone.h
                assert child.isCloned(), 'fail 1'
                assert clone.isCloned(), 'fail 2'
                assert child.isCloned(), 'fail 3'
                assert clone.isCloned(), 'fail 4'
                c.undoer.undo()
                assert not child.isCloned(), 'fail 1-a'
                c.undoer.redo()
                assert child.isCloned(),    'fail 1-b'
                c.undoer.undo()
                assert not child.isCloned(), 'fail 1-c'
                c.undoer.redo()
                assert child.isCloned(),    'fail 1-d'
                clone.moveToRoot()  # Does not change child position.
                assert child.isCloned(),    'fail 3-2'
                assert clone.isCloned(),    'fail 4-2'
                assert not clone.parent(),  'fail 5'
                assert not clone.back(),    'fail 6'
                clone.doDelete()
                assert not child.isCloned(), 'fail 7'
            finally:
                # Delete all children.
                if 1:
                    while p.hasChildren():
                        p.firstChild().doDelete(newNode=None)
                c.redraw_now(p)
        #@+node:ekr.20210830095545.2: *4* TestNode.test_consistency_between_parents_iter_and_v_parents
        def test_consistency_between_parents_iter_and_v_parents(self):
            c, p = self.c, self.c.p
            ###try:
            for p in c.all_positions():
                if 0: # Check all ancestors.  This is tricky and doesn't work yet.
                    parents1 = [parent.v for parent in p.parents_iter()]
                    parents2 = []
                    parent2 = p.v.directParents()
                    while parent2:
                        v = parent2[0]
                        parents2.append(v)
                        parent2 = v.directParents()
                else:
                    parents1 = p.v.parents
                    parents2 = p.v.directParents()
                ### assert len(parents1) == len(parents2), "length mismatch: %s" % (p)
                self.assertEqual(len(parents1), len(parents2), msg=f"fail 1: {p.h}")
                for parent in parents1:
                    # assert parent in parents2, "%s not in %s" % (parent, parents1)
                    self.assertTrue(parent in parents2, msg=f"{parent.h} not in parents1")
                for parent in parents2:
                    self.assertTrue(parent in parents1, msg=f"{parent.h} not in parents2")
                    # assert parent in parents1, "%s not in %s" % (parent,parent2)
            # except AssertionError:
                # print('FAIL: @test consistency between parents_iter and v.parents')
                # print("parents1")
                # for parent in parents1: print(parent)
                # print("parents2")
                # for parent in parents2: print(parent)
                # raise
        #@+node:ekr.20210830095545.10: *4* TestNode.test_consistency_of_back_next_links
        def test_consistency_of_back_next_links(self):
            c, p = self.c, self.c.p
            for p in c.all_positions():

                back = p.back()
                next = p.next()
                if back: assert(back.getNext() == p)
                if next: assert(next.getBack() == p)
        #@+node:ekr.20210830095545.11: *4* TestNode.test_consistency_of_c_all_positions__and_p_ThreadNext_
        def test_consistency_of_c_all_positions__and_p_ThreadNext_(self):
            c, p = self.c, self.c.p
            p2 = c.rootPosition()
            for p in c.all_positions():
                assert p==p2, "%s != %s" % (p,p2)
                p2.moveToThreadNext()

            assert not p2, repr(p2)
        #@+node:ekr.20210830095545.12: *4* TestNode.test_consistency_of_firstChild__children_iter_
        def test_consistency_of_firstChild__children_iter_(self):
            c, p = self.c, self.c.p
            for p in c.all_positions():
                p2 = p.firstChild()
                for p3 in p.children_iter():
                    assert p3==p2, "%s != %s" % (p3,p2)
                    p2.moveToNext()

            assert not p2, repr(p2)
        #@+node:ekr.20210830095545.13: *4* TestNode.test_consistency_of_level
        def test_consistency_of_level(self):
            c, p = self.c, self.c.p
            for p in c.all_positions():

                if p.hasParent():
                    assert(p.parent().level() == p.level() - 1)

                if p.hasChildren():
                    assert(p.firstChild().level() == p.level() + 1)

                if p.hasNext():
                    assert(p.next().level() == p.level())

                if p.hasBack():
                    assert(p.back().level() == p.level())
        #@+node:ekr.20210830095545.14: *4* TestNode.test_consistency_of_parent__parents_iter_
        def test_consistency_of_parent__parents_iter_(self):
            c, p = self.c, self.c.p
            for p in c.all_positions():
                p2 = p.parent()
                for p3 in p.parents_iter():
                    assert p3==p2, "%s != %s" % (p3,p2)
                    p2.moveToParent()

                assert not p2, repr(p2)
        #@+node:ekr.20210830095545.15: *4* TestNode.test_consistency_of_parent_child_links
        def test_consistency_of_parent_child_links(self):
            # Test consistency of p.parent, p.next, p.back and p.firstChild.
            c, p = self.c, self.c.p
            for p in c.all_positions():

                if p.hasParent():
                    n = p.childIndex()
                    assert(p == p.parent().moveToNthChild(n))

                for child in p.children_iter():
                    assert(p == child.parent())

                if p.hasNext():
                    assert(p.next().parent() == p.parent())

                if p.hasBack():
                    assert(p.back().parent() == p.parent())
        #@+node:ekr.20210830095545.16: *4* TestNode.test_consistency_of_threadBack_Next_links
        def test_consistency_of_threadBack_Next_links(self):
            c, p = self.c, self.c.p
            for p in c.all_positions():

                threadBack = p.threadBack()
                threadNext = p.threadNext()

                if threadBack:
                    assert(p == threadBack.getThreadNext())

                if threadNext:
                    assert(p == threadNext.getThreadBack())
        #@+node:ekr.20210830095545.43: *4* TestNode.test_delete_node
        def test_delete_node(self):
            # This test requires @bool select-next-after-delete = False
            c, p = self.c, self.c.p
            root = p.copy()
            while p.hasChildren():
                p.firstChild().doDelete(newNode=None)
            try:
                p2 = p.insertAsNthChild(0)
                p2.setHeadString('A')
                p3 = p.insertAsNthChild(1)
                p3.setHeadString('B')
                p4 = p.insertAsNthChild(2)
                p4.setHeadString('C')
                p.expand()
                c.selectPosition(p3)
                c.deleteOutline()
                c.redraw_now()
                p = c.p
                assert p.h == 'A', 'fail 1: got %s' % p.h
                assert p.next().h == 'C', 'fail 2'
                c.undoer.undo()
                c.outerUpdate()
                p = c.p
                assert p.back() == p2, 'fail 4 %s' % p.back()
                assert p.next() == p4, 'fail 5'
                c.undoer.redo()
                c.outerUpdate()
                p = c.p
                assert p.h == 'A',          'fail 1-2'
                assert p.next().h == 'C',   'fail 2-2'
                c.undoer.undo()
                c.outerUpdate()
                p = c.p
                assert p.back() == p2,  'fail 4-2'
                assert p.next() == p4,  'fail 5-2'
                c.undoer.redo()
                c.outerUpdate()
                p = c.p
                assert p.h == 'A',          'fail 1-3'
                assert p.next().h == 'C',   'fail 2-3'

            finally:
                if 1:
                    while root.hasChildren():
                        root.firstChild().doDelete(newNode=None)
                c.redraw_now(root)
        #@+node:ekr.20210830095545.45: *4* TestNode.test_demote
        def test_demote(self):
            c, p = self.c, self.c.p
            root = p.copy()
            while p.hasChildren():
                p.firstChild().doDelete(newNode=None)

            try:
                p2 = p.insertAsNthChild(0)
                p2.setHeadString('A')
                p3 = p.insertAsNthChild(1)
                p3.setHeadString('B')
                p4 = p.insertAsNthChild(2)
                p4.setHeadString('C')
                p5 = p.insertAsNthChild(3)
                p5.setHeadString('D')
                p.expand()
                c.setCurrentPosition(p3)
                c.demote()
                p = c.p
                assert p == p3,         'fail 1'
                assert p.h == 'B',      'fail 2'
                assert not p.next(),    'fail 3'
                assert p.firstChild().h == 'C',          'fail child 1'
                assert p.firstChild().next().h == 'D',   'fail child 2'
                c.undoer.undo()
                p = c.p
                assert p == p3
                assert p.back() == p2, 'fail 5'
                assert p.next() == p4, 'fail 6'
                c.undoer.redo()
                assert p == p3,         'fail 1-2'
                assert p.h == 'B',      'fail 2-2'
                assert not p.next(),    'fail 3-2'
                assert p.firstChild().h == 'C',         'fail child 1-2'
                assert p.firstChild().next().h == 'D',  'fail child 2-2'
                c.undoer.undo()
                p = c.p
                assert p.back() == p2, 'fail 4-2'
                assert p.next() == p4, 'fail 5-2'
                c.undoer.redo()
                assert p == p3,         'fail 1-3'
                assert p.h == 'B',      'fail 2-3'
                assert not p.next(),    'fail 3-3'
                assert p.firstChild().h == 'C',         'fail child 1-3'
                assert p.firstChild().next().h == 'D',  'fail child 2-3'

            finally:
                if 1:
                    while root.hasChildren():
                        root.firstChild().doDelete(newNode=None)
                c.redraw_now(root)
        #@+node:ekr.20210830095545.18: *4* TestNode.test_leoNodes_properties
        def test_leoNodes_properties(self):
            c, p = self.c, self.c.p
            v = p.v
            b = p.b
            p.b = b
            assert p.b == b
            v.b = b
            assert v.b == b

            h = p.h
            p.h = h
            assert p.h == h
            v.h = h
            assert v.h == h

            for p in c.all_positions():
                assert p.b == p.bodyString()
                assert p.v.b == p.v.bodyString()
                assert p.h == p.headString()
                assert p.v.h == p.v.headString()
        #@+node:ekr.20210830095545.47: *4* TestNode.test_move_outline_down__undo_redo
        def test_move_outline_down__undo_redo(self):
            c, p = self.c, self.c.p
            root = p.copy()
            while p.hasChildren():
                p.firstChild().doDelete(newNode=None)
            try:
                p2 = p.insertAsNthChild(0)
                p2.setHeadString('A')
                p3 = p.insertAsNthChild(1)
                p3.setHeadString('B')
                p4 = p.insertAsNthChild(2)
                p4.setHeadString('C')
                p5 = p.insertAsNthChild(3)
                p5.setHeadString('D')
                p.expand()
                c.setCurrentPosition(p3)
                c.moveOutlineDown()
                moved = c.p
                assert moved.h == 'B',          'fail 1: %s' % moved.h
                assert moved.back().h == 'C',   'fail 2'
                assert moved.next().h == 'D',   'fail 3'
                # This assert fails because p4._childIndex != moved.back()._childIndex.
                # assert moved.back() == p4, 'fail 4: %s != %s' % (moved.back(),p4)
                assert moved.next() == p5,      'fail 5: %s != %s' % (moved.next(),p5)
                c.undoer.undo()
                moved = c.p
                assert moved.back() == p2,      'fail 4'
                assert moved.next() == p4,      'fail 5'
                c.undoer.redo()
                moved = c.p
                assert moved.h == 'B',          'fail 1-2: %s' % moved.h
                assert moved.back().h == 'C',   'fail 2-2'
                assert moved.next().h == 'D',   'fail 3-2'
                c.undoer.undo()
                moved = c.p
                assert moved.back() == p2,      'fail 4-2'
                assert moved.next() == p4,      'fail 5-2'
                c.undoer.redo()
                moved = c.p
                assert moved.h == 'B',          'fail 1-3'
                assert moved.back().h == 'C',   'fail 2-3'
                assert moved.next().h == 'D',   'fail 3-3'
            finally:
                if 1:
                    while root.hasChildren():
                        root.firstChild().doDelete(newNode=None)
                c.redraw_now(root)
        #@+node:ekr.20210830095545.48: *4* TestNode.test_move_outline_left
        def test_move_outline_left(self):
            c, p = self.c, self.c.p
            while p.hasChildren():
                p.firstChild().doDelete(newNode=None)
            try:
                p2 = p.insertAsNthChild(0)
                p2.setHeadString('A')
                p.expand()
                c.setCurrentPosition(p2)
                c.moveOutlineLeft()
                moved = c.p
                assert moved.h == 'A','fail 1'
                # This assert fails because p2._childIndex != moved.back()._childIndex.
                assert moved.back() == p, 'fail 2: %s != %s' % (moved.back(),p2)
                c.undoer.undo()
                c.undoer.redo()
                c.undoer.undo()
                c.undoer.redo()
                moved.doDelete(newNode=p)
            finally:
                if 1:
                    while p.hasChildren():
                        p.firstChild().doDelete(newNode=None)
                    c.redraw_now(p)
        #@+node:ekr.20210830095545.49: *4* TestNode.test_move_outline_right
        def test_move_outline_right(self):
            c, p = self.c, self.c.p
            while p.hasChildren():
                p.firstChild().doDelete(newNode=None)

            try:
                p2 = p.insertAsNthChild(0)
                p2.setHeadString('A')
                p3 = p.insertAsNthChild(1)
                p3.setHeadString('B')
                p4 = p.insertAsNthChild(2)
                p4.setHeadString('C')
                p.expand()
                c.setCurrentPosition(p3)
                c.moveOutlineRight()
                moved = c.p
                assert moved.h == 'B', 'fail 1'
                assert moved.parent() == p2
                c.undoer.undo()
                c.undoer.redo()
                c.undoer.undo()
                c.undoer.redo()
            finally:
                if 1:
                    while p.hasChildren():
                        p.firstChild().doDelete(newNode=None)
                if 1:
                    c.redraw_now(p)
        #@+node:ekr.20210830095545.50: *4* TestNode.test_move_outline_up
        def test_move_outline_up(self):
            c, p = self.c, self.c.p
            while p.hasChildren():
                p.firstChild().doDelete(newNode=None)

            try:
                p2 = p.insertAsNthChild(0)
                p2.setHeadString('A')
                p3 = p.insertAsNthChild(1)
                p3.setHeadString('B')
                p4 = p.insertAsNthChild(2)
                p4.setHeadString('C')
                p5 = p.insertAsNthChild(3)
                p5.setHeadString('D')
                p.expand()
                c.setCurrentPosition(p4)
                c.moveOutlineUp()
                moved = c.p
                assert moved.h == 'C',          'fail 1'
                assert moved.back().h == 'A',   'fail 2'
                assert moved.next().h == 'B',   'fail 3'
                assert moved.back() == p2,      'fail 4: %s != %s' % (moved.back(),p2)
                # This assert fails because p4._childIndex != moved.back()._childIndex.
                # assert moved.next() == p3,    'fail 5: %s != %s' % (moved.next(),p3)
                c.undoer.undo()
                c.undoer.redo()
                c.undoer.undo()
                c.undoer.redo()
            finally:
                if 1:
                    while p.hasChildren():
                        p.firstChild().doDelete(newNode=None)
                if 1:
                    c.redraw_now(p)
        #@+node:ekr.20210830095545.19: *4* TestNode.test_new_vnodes_methods
        def test_new_vnodes_methods(self):
            c, p = self.c, self.c.p
            parent_v = p.parent().v or c.hiddenRootNode
            while p.hasChildren():
                p.firstChild().doDelete()
            if 0: # passes
                p.v.cloneAsNthChild(parent_v,p.childIndex())
            if 1:
                v2 = p.v.insertAsFirstChild()
                v2.h = 'insertAsFirstChild'
                v2 = p.v.insertAsLastChild()
                v2.h = 'insertAsLastChild'
                v2 = p.v.insertAsNthChild(1)
                v2.h = 'insertAsNthChild(1)'
            p.expand()
            c.redraw()
        #@+node:ekr.20210830095545.20: *4* TestNode.test_newlines_in_headlines
        def test_newlines_in_headlines(self):
            # Bug https://bugs.launchpad.net/leo-editor/+bug/1245535
            p = self.c.p
            h = p.h
            try:
                p.h = '\nab\nxy\n'
                assert p.h == 'abxy',p.h
            finally:
                p.h = h
        #@+node:ekr.20210830095545.54: *4* TestNode.test_node_that_doesn_t_belong_to_a_derived_file
        def test_node_that_doesn_t_belong_to_a_derived_file(self):
            # Change @file activeUnitTests.txt to @@file activeUnitTests.txt
            c, p = self.c, self.c.p
            for parent in p.parents():
                if parent.isAnyAtFileNode():
                    parent.h = '@' + parent.h
                    break
            else:
                parent = None
            root = p.copy()
            while p.hasChildren():
                p.firstChild().doDelete(newNode=None)
            try:
                p1 = p.insertAsLastChild()
                assert p1.textOffset() is None
            finally:
                if 1:
                    while root.hasChildren():
                        root.firstChild().doDelete(newNode=None)
                if parent:
                    parent.h = parent.h[1:]
                c.redraw_now()
        #@+node:ekr.20210830095545.56: *4* TestNode.test_organizer_node
        def test_organizer_node(self):
            c, p = self.c, self.c.p
            root = p.copy()
            while p.hasChildren():
                p.firstChild().doDelete(newNode=None)
            try:
                p1 = p.insertAsLastChild()
                p1.setHeadString('@file zzz')
                p2 = p1.insertAsLastChild()
                assert p1.textOffset() == 0
                assert p2.textOffset() == 0
            finally:
                if 1:
                    while root.hasChildren():
                        root.firstChild().doDelete(newNode=None)
                c.redraw_now()
        #@+node:ekr.20210830095545.25: *4* TestNode.test_p_deletePositionsInList
        def test_p_deletePositionsInList(self):
            c, p = self.c, self.c.p
            p1 = p.copy()
            while p.hasChildren():
                p.firstChild().doDelete()
            root = p.insertAsLastChild()
            root.h = 'root'
            # Top level
            a1 = root.insertAsLastChild()
            a1.h = 'a'
            a1.clone()
            d1 = a1.insertAfter()
            d1.h = 'd'
            b1 = root.insertAsLastChild()
            b1.h = 'b'
            # Children of a.
            b11 = b1.clone()
            b11.moveToLastChildOf(a1)
            b11.clone()
            c2 = b11.insertAfter()
            c2.h = 'c'
            # Children of d
            b11 = b1.clone()
            b11.moveToLastChildOf(d1)
            
            def parent(p):
                return p.stack[-1][0].h

            # n = root.level()
            aList = []
            nodes = 0
            for p in root.subtree():
                nodes += 1
                if p.h == 'b':
                    # if 0:
                        # parent2 = p.stack[-1][0]
                        # print('found',p.level()-n,p.h,'childIndex',p.childIndex(),'parent:',parent2.h)
                    aList.append(p.copy())
            n_aList = len(aList)
            assert n_aList == 6,n_aList
            try:
                c.deletePositionsInList(aList)
            finally:
                if 1:
                    while p1.hasChildren():
                        p1.firstChild().doDelete()
            c.redraw()
        #@+node:ekr.20210830095545.26: *4* TestNode.test_p_hasNextBack
        def test_p_hasNextBack(self):
            c, p = self.c, self.c.p
            for p in c.all_positions():
                back = p.back()
                next = p.next()
                assert(
                    (back and p.hasBack()) or
                    (not back and not p.hasBack()))
                assert(
                    (next and p.hasNext()) or
                    (not next and not p.hasNext()))
        #@+node:ekr.20210830095545.27: *4* TestNode.test_p_hasParentChild
        def test_p_hasParentChild(self):
            c, p = self.c, self.c.p
            for p in c.all_positions():
                child = p.firstChild()
                parent = p.parent()
                assert(
                    (child and p.hasFirstChild()) or
                    (not child and not p.hasFirstChild()))
                assert(
                    (parent and p.hasParent()) or
                    (not parent and not p.hasParent()))
        #@+node:ekr.20210830095545.28: *4* TestNode.test_p_hasThreadNextBack
        def test_p_hasThreadNextBack(self):
            c, p = self.c, self.c.p
            for p in c.all_positions():

                threadBack = p.getThreadBack()
                threadNext = p.getThreadNext()

                assert(
                    (threadBack and p.hasThreadBack()) or
                    (not threadBack and not p.hasThreadBack()))

                assert(
                    (threadNext and p.hasThreadNext()) or
                    (not threadNext and not p.hasThreadNext()))
        #@+node:ekr.20210830095545.29: *4* TestNode.test_p_isAncestorOf
        def test_p_isAncestorOf(self):
            c, p = self.c, self.c.p
            for p in c.all_positions():
                child = p.firstChild()
                while child:
                    for parent in p.self_and_parents_iter():
                        assert parent.isAncestorOf(child)
                    child.moveToNext()
                next = p.next()
                assert not p.isAncestorOf(next)
        #@+node:ekr.20210830095545.30: *4* TestNode.test_p_isCurrentPosition
        def test_p_isCurrentPosition(self):
            c, p = self.c, self.c.p
            n = g.app.positions
            assert c.isCurrentPosition(None) is False
            assert c.isCurrentPosition(p) is True
            assert g.app.positions == n
        #@+node:ekr.20210830095545.35: *4* TestNode.test_p_nosentinels
        def test_p_nosentinels(self):
            ###@language python
            ###@tabwidth -4
            p = self.c.p

            def not_a_sentinel(x):
                pass
            @not_a_sentinel
            def spam():
                pass

            s1 = ''.join(g.splitLines(p.b) [2:])
            s2 = p.nosentinels   
            assert s1 == s2,'expected:\n%s\ngot:\n%s' % (s1,s2)
        #@+node:ekr.20210830095545.37: *4* TestNode.test_p_u
        def test_p_u(self):
            p = self.c.p
            assert p.u == p.v.u, (p.u, p.v.u)
            p.v.u = None
            assert p.u == {}, p.u
            assert p.v.u == {}, p.v.u
            d = {'my_plugin': 'val'}
            p.u = d
            assert p.u == d, (p.u, d)
            assert p.v.u == d, (p.v.u, d)
        #@+node:ekr.20210830095545.51: *4* TestNode.test_paste_node
        def test_paste_node(self):
            c, p = self.c, self.c.p
            while p.hasChildren():
                p.firstChild().doDelete(newNode=None)
            child = p.insertAsNthChild(0)
            child.setHeadString('child')
            child2 = p.insertAsNthChild(1)
            child2.setHeadString('child2')
            grandChild = child.insertAsNthChild(0)
            grandChild.setHeadString('grand child')
            c.selectPosition(grandChild)
            c.clone()
            c.selectPosition(child)

            try:
                p.expand()
                c.selectPosition(child)
                assert c.p.h == 'child','fail 1'
                c.copyOutline()
                oldVnodes = [p2.v for p2 in child.self_and_subtree()]
                c.selectPosition(child)
                c.p.contract() # Essential
                c.pasteOutline()
                assert c.p != child, 'fail 2'
                assert c.p.h == 'child','fail 3'
                newVnodes = [p2.v for p2 in c.p.self_and_subtree()]
                for v in newVnodes:
                    assert v not in oldVnodes, 'fail 4'
                c.undoer.undo()
                c.undoer.redo()
                c.undoer.undo()
                c.undoer.redo()

            finally:
                if 1:
                    while p.hasChildren():
                        p.firstChild().doDelete(newNode=None)
                if 1:
                    c.redraw_now(p)
        #@+node:ekr.20210830095545.52: *4* TestNode.test_paste_retaining_clones
        def test_paste_retaining_clones(self):
            c, p = self.c, self.c.p
            while p.hasChildren():
                p.firstChild().doDelete(newNode=None)
            child = p.insertAsNthChild(0)
            child.setHeadString('child')
            assert child, 'no child'
            grandChild = child.insertAsNthChild(0)
            grandChild.setHeadString('grand child')

            try:
                c.selectPosition(child)
                c.copyOutline()
                oldVnodes = [p2.v for p2 in child.self_and_subtree()]
                c.p.contract() # Essential
                c.pasteOutlineRetainingClones()
                assert c.p != child, 'fail 2'
                newVnodes = [p2.v for p2 in c.p.self_and_subtree()]
                for v in newVnodes:
                    assert v in oldVnodes, 'fail 3'
            finally:
                if 1:
                    while p.hasChildren():
                        p.firstChild().doDelete(newNode=None)
                if 1:
                    c.redraw_now(p)
        #@+node:ekr.20210830095545.4: *4* TestNode.test_position_not_hashable
        def test_position_not_hashable(self):
            p = self.c.p
            try:
                a = set()
                a.add(p)
                assert False, 'Adding position to set should throw exception'
            except TypeError:
                pass
        #@+node:ekr.20210830095545.53: *4* TestNode.test_promote
        def test_promote(self):
            c, p = self.c, self.c.p
            root = p.copy()
            while p.hasChildren():
                p.firstChild().doDelete(newNode=None)

            try:
                p2 = p.insertAsNthChild(0)
                p2.setHeadString('A')
                p3 = p.insertAsNthChild(1)
                p3.setHeadString('B')
                p4 = p3.insertAsNthChild(0)
                p4.setHeadString('child 1')
                p5 = p3.insertAsNthChild(1)
                p5.setHeadString('child 2')
                p.expand()
                p6 = p.insertAsNthChild(2)
                p6.setHeadString('C')
                c.setCurrentPosition(p3)
                c.promote()
                p = c.p
                assert p == p3,         'fail 1'
                assert p.h == 'B',      'fail 2'
                assert p.next().h=='child 1',            'fail 3'
                assert p.next().next().h == 'child 2',   'fail child 1'
                assert p.next().next().next().h == 'C',  'fail child 2'
                c.undoer.undo()
                p = c.p
                assert p == p3
                assert p.back() == p2,  'fail 5'
                assert p.next() == p6,  'fail 6'
                assert p.firstChild().h=='child 1',          'fail child 3'
                assert p.firstChild().next().h == 'child 2', 'fail child 4'
                c.undoer.redo()
                p = c.p
                assert p == p3,         'fail 1-2'
                assert p.h == 'B',      'fail 2-2'
                assert p.next().h=='child 1',            'fail 3-2'
                assert p.next().next().h == 'child 2',   'fail child 1-2'
                assert p.next().next().next().h == 'C',  'fail child 2-2'
                c.undoer.undo()
                p = c.p
                assert p == p3
                assert p.back() == p2,                      'fail 5-2'
                assert p.next() == p6,                      'fail 6-2'
                assert p.firstChild().h=='child 1',         'fail child 3-2'
                assert p.firstChild().next().h == 'child 2','fail child 4-2'
                c.undoer.redo()
                p = c.p
                assert p == p3,     'fail 1-3'
                assert p.h == 'B',  'fail 2-3'
                assert p.next().h=='child 1',            'fail 3-3'
                assert p.next().next().h == 'child 2',   'fail child 1-3'
                assert p.next().next().next().h == 'C',  'fail child 2-3'

            finally:
                if 1:
                    while root.hasChildren():
                        root.firstChild().doDelete(newNode=None)
                c.redraw_now(root)
        #@+node:ekr.20210830095545.55: *4* TestNode.test_root_of_a_derived_file
        def test_root_of_a_derived_file(self):
            c, p = self.c, self.c.p
            root = p.copy()
            while p.hasChildren():
                p.firstChild().doDelete(newNode=None)
            try:
                p1 = p.insertAsLastChild()
                p1.setHeadString('@file zzz')
                assert p1.textOffset() == 0
            finally:
                if 1:
                    while root.hasChildren():
                        root.firstChild().doDelete(newNode=None)
                c.redraw_now()
        #@+node:ekr.20210830095545.57: *4* TestNode.test_section_node
        def test_section_node(self):
            c, p = self.c, self.c.p
            root = p.copy()
            while p.hasChildren():
                p.firstChild().doDelete(newNode=None)
            try:
                p1 = p.insertAsLastChild()
                p1.setHeadString('@file zzz')
                body = '''   %s
                ''' % (g.angleBrackets(' section '))
                p1.setBodyString(body)
                p2 = p1.insertAsLastChild()
                head = g.angleBrackets(' section ')
                p2.setHeadString(head)
                assert p1.textOffset() == 0
                assert p2.textOffset() == 3
                    # Section nodes can appear in with @others nodes,
                    # so they don't get special treatment.
            finally:
                if 1:
                    while root.hasChildren():
                        root.firstChild().doDelete(newNode=None)
                c.redraw_now()
        #@+node:ekr.20210830095545.39: *4* TestNode.test_v_atAutoNodeName__v_atAutoRstNodeName
        def test_v_atAutoNodeName__v_atAutoRstNodeName(self):
            p = self.c.p
            table = (
                ('@auto-rst rst-file','rst-file','rst-file'),
                ('@auto x','x',''),
                ('xyz','',''),
            )

            for s,expected1,expected2 in table:
                result1 = p.v.atAutoNodeName(h=s)
                result2 = p.v.atAutoRstNodeName(h=s)
                assert result1 == expected1,'fail1: given %s expected %s got %s' % (
                    repr(s),repr(expected1),repr(result1))
                assert result2 == expected2,'fail2: given %s expected %s got %s' % (
                    repr(s),repr(expected2),repr(result2))
        #@-others
    #@+node:ekr.20210830145703.1: *3* Skip fails
    if 0:
        #@+others
        #@+node:ekr.20210830095545.21: *4* TestNode.test_p__eq_
        def test_p__eq_(self):
            c, p = self.c, self.c.p
            # These must not return NotImplemented!
            root = c.rootPosition()
            assert p.__eq__(None) is False, p.__eq__(None)
            assert p.__ne__(None) is True, p.__ne__(None)
            assert p.__eq__(root) is False, p.__eq__(root)
            assert p.__ne__(root) is True, p.__ne__(root)
        #@+node:ekr.20210830095545.23: *4* TestNode.test_p_adjustPositionBeforeUnlink
        def test_p_adjustPositionBeforeUnlink(self):
            c, p = self.c, self.c.p
            table = (
                '1',
                '1-1','1-1-1','1-1-2',
                '1-2','1-2-1','1-2-2',
                '2',
                '2-1','2-1-1','2-1-2',
                '2-2','2-2-1','2-2-2',
                '3',
                '3-1','3-1-1','3-1-2',
                '3-2','3-2-1','3-2-2',
            )

            for suffix in table:
                h = 'node %s' % suffix
                p2 = g.findNodeInTree(c,p,h)
                assert p2,h

            table2 = (
                ('2-1-2','2-1-1','2-1-1'),
                ('3','2','2'),
            )  

            for h1,h2,h3 in table2:
                p1 = g.findNodeInTree(c,p,'node %s' % h1)
                p2 = g.findNodeInTree(c,p,'node %s' % h2)
                p3 = g.findNodeInTree(c,p,'node %s' % h3)
                p1._adjustPositionBeforeUnlink(p2)
                result = p1
                assert result.stack == p3.stack,'expected %s got %s' % (
                    p3.h,result and result.h or '<none>')

            # Data.
            #@+others
            #@-others
        #@+node:ekr.20210830095545.24: *4* TestNode.test_p_comparisons
        def test_p_comparisons(self):
            c, p = self.c, self.c.p
            copy = p.copy()
            assert(p == copy)
            assert(p != p.threadNext())

            root = c.rootPosition()
            # assert p.equal(p.copy()) is True
            # assert p.equal(root) is False
            assert p.__eq__(copy) is True
            assert p.__ne__(copy) is False
            assert p.__eq__(root) is False
            assert p.__ne__(root) is True
        #@+node:ekr.20210830095545.31: *4* TestNode.test_p_isRootPosition
        def test_p_isRootPosition(self):
            c, p = self.c, self.c.p
            assert not c.isRootPosition(None),'fail 1'
            assert not c.isRootPosition(p),'fail 2'
        #@+node:ekr.20210830095545.33: *4* TestNode.test_p_moveToFirst_LastChild
        def test_p_moveToFirst_LastChild(self):
            c, p = self.c, self.c.p

            def setup(p):
                while p.hasChildren():
                    p.firstChild().doDelete()

            child = p.firstChild()
            assert child
            setup(child)
            p2 = child.insertAfter()
            p2.h = "test"
            try:
                assert c.positionExists(p2),p2
                p2.moveToFirstChildOf(child)
                assert c.positionExists(p2),p2
                p2.moveToLastChildOf(child)
                assert c.positionExists(p2),p2
            finally:
                if 1:
                    setup(child)
                c.redraw(p)
        #@+node:ekr.20210830095545.34: *4* TestNode.test_p_moveToVisBack_in_a_chapter
        def test_p_moveToVisBack_in_a_chapter(self):
            c, p = self.c, self.c.p
            # Verify a fix for bug https://bugs.launchpad.net/leo-editor/+bug/1264350
            if g.app.isExternalUnitTest:
                # There is no @chapter node in the copied file.
                self.skipTest('Can not be run externally') 
            else:
                aaa1 = g.findNodeAnywhere(c,'@chapter aaa')
                assert aaa1
                try:
                    c.chapterController.selectChapterByName('aaa',collapse=True)
                    aaa = c.p
                    assert aaa.h == 'aaa node 1',repr(aaa)
                    p2 = p.moveToVisBack(c)
                    assert p2 is None,p2
                finally:
                    c.chapterController.selectChapterByName('main',collapse=True)
        #@+node:ekr.20210830095545.22: *4* TestNode.test_p_relinkAsCloneOf
        def test_p_relinkAsCloneOf(self):
            c, p = self.c, self.c.p
            u = c.undoer
            p1 = g.findNodeInTree(c,p,'a')
            p2 = g.findNodeInTree(c,p,'b')
            assert p1 and p2
            assert not p1.isCloned()
            assert not p2.isCloned()
            bunch = u.beforeChangeTree(p)
            p1._relinkAsCloneOf(p2)
            u.afterChangeTree(p,'relink-clone',bunch)
            assert p.firstChild().isCloned()
            assert p.firstChild().next().isCloned()
            c.redraw()
            u.undo()
            c.redraw()
            p1 = g.findNodeInTree(c,p,'a')
            p2 = g.findNodeInTree(c,p,'b')
            assert not p1.isCloned()
            assert not p2.isCloned()
            assert p1 and p2
            u.clearUndoState()
        #@+node:ekr.20210830095545.36: *4* TestNode.test_p_setBodyString
        def test_p_setBodyString(self):
            # Tests that c.setBodyString works immediately.
            c, p = self.c, self.c.p
            try:
                w = c.frame.body.wrapper
                child = p.firstChild()
                before = child.b
                after = "after"
                c.setBodyString(child,"after")
                c.selectPosition(child)
                s = w.get("1.0","end")
                assert s.rstrip() == after.rstrip(), 'expected %s, got %s' % (
                    repr(after),repr(s))
            finally:
                c.setBodyString(child,before)
                c.selectPosition(p)
        #@+node:ekr.20210830095545.38: *4* TestNode.test_p_unique_nodes
        def test_p_unique_nodes(self):
            p = self.c.p
            aList = [z for z in p.unique_nodes()]
            assert len(aList) == 3,len(aList)
            v1,v2,v3 = aList
            assert v1.h == p.h,p.h
            assert v2.h == 'node 1',v2.h
            assert v3.h == 'node 2',v3.h
        #@-others
    #@+node:ekr.20210830095545.46: *3* TestNode.test_insert_node
    def test_insert_node(self):
        c, p = self.c, self.c.p
        self.assertEqual(p.h, 'root')
        p2 = p.insertAsNthChild(0)
        p2.setHeadString('A')
        p3 = p.insertAsNthChild(1)
        p3.setHeadString('B')
        p.expand()
        c.setCurrentPosition(p2)
        p4 = c.insertHeadline()
        self.assertEqual(p4, c.p)
        p = c.p
        self.assertTrue(p)
        p.setHeadString('inserted')
        self.assertTrue(p.back())
        self.assertEqual(p.back().h, 'A')
        self.assertEqual(p.next().h, 'B')
        # With the new undo logic, it takes 2 undoes.
        # The first undo undoes the headline changes,
        # the second undo undoes the insert node.
        c.undoer.undo()
        c.undoer.undo()
        p = c.p
        self.assertEqual(p, p2) 
        self.assertEqual(p.next(), p3)
        c.undoer.redo()
        p = c.p
        self.assertTrue(p.back())
        self.assertEqual(p.back().h, 'A')
        self.assertEqual(p.next().h, 'B')
        c.undoer.undo()
        p = c.p
        self.assertEqual(p, p2)
        self.assertEqual(p.next(), p3)
        c.undoer.redo()
        p = c.p
        self.assertEqual(p.back().h, 'A')
        self.assertEqual(p.next().h, 'B')
    #@-others
#@-others

#@-leo
