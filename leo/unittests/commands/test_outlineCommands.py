#@+leo-ver=5-thin
#@+node:ekr.20221113062857.1: * @file ../unittests/commands/test_outlineCommands.py
"""
New unit tests for Leo's outline commands.

Older tests are in unittests/core/test_leoNodes.py
"""
from leo.core.leoTest2 import LeoUnitTest
#@+others
#@+node:ekr.20221113062938.1: ** class TestOutlineCommands(LeoUnitTest)
class TestOutlineCommands(LeoUnitTest):
    """
    Unit tests for Leo's outline commands.
    """

    #@+others
    #@+node:ekr.20221113064908.1: *3* TestOutlineCommands.create_test_sort_outline
    def create_test_sort_outline(self) -> None:
        """Create a test outline suitable for sort commands."""
        p = self.c.p
        assert p == self.root_p
        assert p.h == 'root'
        table = (
            'child a',
            'child z',
            'child b',
            'child w',
        )
        for h in table:
            child = p.insertAsLastChild()
            child.h = h


    #@+node:ekr.20221112051634.1: *3* TestOutlineCommands.test_sort_children
    def test_sort_children(self):
        c, u = self.c, self.c.undoer
        assert self.root_p.h == 'root'
        self.create_test_sort_outline()
        original_children = [z.h for z in self.root_p.v.children]
        sorted_children = sorted(original_children)
        c.sortChildren()
        result_children = [z.h for z in self.root_p.v.children]
        self.assertEqual(result_children, sorted_children)
        u.undo()
        result_children = [z.h for z in self.root_p.v.children]
        self.assertEqual(result_children, original_children)
        u.redo()
        result_children = [z.h for z in self.root_p.v.children]
        self.assertEqual(result_children, sorted_children)
        u.undo()
        result_children = [z.h for z in self.root_p.v.children]
        self.assertEqual(result_children, original_children)
    #@+node:ekr.20221112051650.1: *3* TestOutlineCommands.test_sort_siblings
    def test_sort_siblings(self):
        c, u = self.c, self.c.undoer
        assert self.root_p.h == 'root'
        self.create_test_sort_outline()
        original_children = [z.h for z in self.root_p.v.children]
        sorted_children = sorted(original_children)
        c.selectPosition(self.root_p.firstChild())
        c.sortSiblings()
        result_children = [z.h for z in self.root_p.v.children]
        self.assertEqual(result_children, sorted_children)
        u.undo()
        result_children = [z.h for z in self.root_p.v.children]
        self.assertEqual(result_children, original_children)
        u.redo()
        result_children = [z.h for z in self.root_p.v.children]
        self.assertEqual(result_children, sorted_children)
        u.undo()
        result_children = [z.h for z in self.root_p.v.children]
        self.assertEqual(result_children, original_children)
    #@+node:ekr.20230720202352.1: *3* TestOutlineCommands.test_paste_retaining_clones
    def test_paste_retaining_clones(self):

        c = self.c
        p = c.p
        u = c.undoer
        assert p == self.root_p
        assert p.h == 'root'
        p.deleteAllChildren()
        while p.hasNext():
            p.next().doDelete()
        # cut cc and paste-as-clone again. cc's child1 is surprisingly not a clone!
        # aa
        # bb
        # child1 (clone)
        # cc
        #   child1 (clone)
        #   child2
        aa = p.insertAfter()
        aa.h = 'aa'
        bb = aa.insertAfter()
        bb.h = 'bb'
        cc = bb.insertAfter()
        cc.h = 'cc'
        child1 = cc.insertAsLastChild()
        child1.h = 'child1'
        child1_gnx = child1.gnx
        child2 = child1.insertAfter()
        child2.h = 'child2'
        child2_gnx = child2.gnx
        clone = child1.clone()
        clone.moveAfter(bb)
        assert clone.v == child1.v
        # Careful: position cc has changed.
        cc = clone.next()
        clone_v = clone.v
        cc_gnx = cc.gnx
        assert cc.h == 'cc'

        # Cut node cc
        # self.dump_headlines(c)
        # self.dump_clone_info(c)
        c.selectPosition(cc)
        c.cutOutline()
        assert not clone.isCloned()
        assert c.p == clone
        assert c.p.h == 'child1'

        # Execute paste-retaining-clones
        c.pasteOutlineRetainingClones()
        # self.dump_clone_info(c)
        
        # The quick test.
        for p in c.all_positions():
            if p.h == 'child1':
                assert p.isCloned(), p.h
                # The vnode never changes *and* all positions share the same vnode.
                assert p.v == clone_v, p.h
            else:
                assert not p.isCloned(), p.h

        # Other tests.

        # Recreate the positions.
        clone = bb.next()
        cc = clone.next()
        child1 = cc.firstChild()
        assert clone.v == clone_v
        assert cc.gnx == cc_gnx
        assert child1.gnx == clone.gnx
        self.assertEqual(id(child1.v), id(clone.v))
        assert cc.firstChild().gnx == child1_gnx
        assert cc.firstChild().next().gnx == child2_gnx
        assert clone.isCloned()  # Fails.
        assert cc.firstChild().isCloned()
        
        # Test multiple undo/redo cycles.
        for i in range(3):

            # Undo paste-retaining-clones.
            u.undo()
            for p in c.all_positions():
                assert not p.isCloned(), p.h
                if p.h == 'child1':
                    # The vnode never changes!
                    assert p.v == clone_v, p.h

            # Redo paste-retaining-clones.
            u.redo()
            # self.dump_clone_info(c)
            for p in c.all_positions():
                if p.h == 'child1':
                    assert p.isCloned(), p.h
                    # The vnode never changes *and* all positions share the same vnode.
                    assert p.v == clone_v, p.h
                else:
                    assert not p.isCloned(), p.h
    #@+node:ekr.20230722083123.1: *3* TestOutlineCommands.test_restoreFromCopiedTree (new)
    def test_restoreFromCopiedTree(self):

        ###from leo.core import leoGlobals as g ###

        # Clean the tree.
        c = self.c
        fc = c.fileCommands
        p = c.p
        u = c.undoer
        assert p == self.root_p
        assert p.h == 'root'
        
        #@+<< create test tree >>
        #@+node:ekr.20230722084237.1: *4* << create test tree >>
        p.deleteAllChildren()
        while p.hasNext():
            p.next().doDelete()

        # aa
        # bb
        # child1 (clone)
        # cc
        #   child1 (clone)
        #   child2
        aa = p.insertAfter()
        aa.h = 'aa'
        bb = aa.insertAfter()
        bb.h = 'bb'
        cc = bb.insertAfter()
        cc.h = 'cc'
        child1 = cc.insertAsLastChild()
        child1.h = 'child1'
        child1_gnx = child1.gnx
        child2 = child1.insertAfter()
        child2.h = 'child2'
        child2_gnx = child2.gnx
        clone = child1.clone()
        clone.moveAfter(bb)
        assert clone.v == child1.v
        # Careful: position cc has changed.
        cc = clone.next()
        clone_v = clone.v
        cc_gnx = cc.gnx
        assert cc.h == 'cc'
        #@-<< create test tree >>
        
        assert fc  ###
        
        return ###

        # Cut node cc
        # self.dump_headlines(c)
        # self.dump_clone_info(c)
        c.selectPosition(cc)
        c.cutOutline()
        assert not clone.isCloned()
        assert c.p == clone
        assert c.p.h == 'child1'

        # Execute paste-retaining-clones
        c.pasteOutlineRetainingClones()
        # self.dump_clone_info(c)
        
        # The quick test.
        for p in c.all_positions():
            if p.h == 'child1':
                assert p.isCloned(), p.h
                # The vnode never changes *and* all positions share the same vnode.
                assert p.v == clone_v, p.h
            else:
                assert not p.isCloned(), p.h

        # Other tests.

        # Recreate the positions.
        clone = bb.next()
        cc = clone.next()
        child1 = cc.firstChild()
        assert clone.v == clone_v
        assert cc.gnx == cc_gnx
        assert child1.gnx == clone.gnx
        self.assertEqual(id(child1.v), id(clone.v))
        assert cc.firstChild().gnx == child1_gnx
        assert cc.firstChild().next().gnx == child2_gnx
        assert clone.isCloned()  # Fails.
        assert cc.firstChild().isCloned()
        
        # Test multiple undo/redo cycles.
        for i in range(3):

            # Undo paste-retaining-clones.
            u.undo()
            for p in c.all_positions():
                assert not p.isCloned(), p.h
                if p.h == 'child1':
                    # The vnode never changes!
                    assert p.v == clone_v, p.h

            # Redo paste-retaining-clones.
            u.redo()
            # self.dump_clone_info(c)
            for p in c.all_positions():
                if p.h == 'child1':
                    assert p.isCloned(), p.h
                    # The vnode never changes *and* all positions share the same vnode.
                    assert p.v == clone_v, p.h
                else:
                    assert not p.isCloned(), p.h
    #@+node:ekr.20230722104508.1: *3* TestOutlineCommands.test_fc_getLeoOutlineFromClipBoardRetainingClones (new)
    def test_fc_getLeoOutlineFromClipBoardRetainingClones(self):
        # self.fail('Not ready yet')
        pass
    #@-others
#@-others
#@-leo
