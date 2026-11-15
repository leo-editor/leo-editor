# @+leo-ver=5-thin
# @+node:ekr.20210906141410.1: * @file ../unittests/core/test_leoUndo.py
"""Tests of leoUndo.py"""

from __future__ import annotations
from typing import TYPE_CHECKING
from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest

if TYPE_CHECKING:
    from leo.core.leoNodes import Position


# @+others
# @+node:ekr.20210906141410.2: ** class TestUndo (LeoUnitTest)
class TestUndo(LeoUnitTest):
    # @+others
    # @+node:ekr.20210906141410.9: *3* TestUndo.runTest (Test)
    def runTest(self, before, after, i, j, func):
        """TestUndo.runTest."""
        c = self.c
        p = c.p
        u = c.undoer
        w = c.frame.body.wrapper
        # Restore section references.
        before = before.replace('> >', '>>').replace('< <', '<<')
        after = after.replace('> >', '>>').replace('< <', '<<')
        # Check indices.
        self.assertTrue(0 <= i <= len(before), msg=f"i: {i} len(before): {len(before)}")
        self.assertTrue(0 <= j <= len(before), msg=f"j: {j} len(before): {len(before)}")
        # Set the text and selection range.
        p.b = before
        self.assertEqual(p.b, w.getAllText())
        w.setSelectionRange(i, j, insert=i)
        # Test.
        self.assertNotEqual(before, after)
        func()
        result = p.b
        self.assertEqual(result, after, msg='before undo1')
        for _i in range(3):
            u.undo()
            result = w.getAllText()
            self.assertEqual(result, before, msg='after undo1')
            u.redo()
            result = w.getAllText()
            self.assertEqual(result, after, msg='after redo1')

    # @+node:ekr.20210906172626.2: *3* TestUndo.test_addComments
    def test_addComments(self):
        c = self.c
        before = self.prep(
            """
            @language python

            def addCommentTest():
                if 1:
                    a = 2
                    b = 3
                pass
            """
        )
        after = self.prep(
            """
            @language python

            def addCommentTest():
                # if 1:
                #     a = 2
                #     b = 3
                pass
        """
        )
        i = before.find('if 1')
        j = before.find('b = 3')
        func = c.addComments
        self.runTest(before, after, i, j, func)

    # @+node:ekr.20210906172626.3: *3* TestUndo.test_convertAllBlanks
    def test_convertAllBlanks(self):
        c = self.c
        before = self.prep(
            """
            @tabwidth -4

            line 1
                line 2
                  line 3
            line4
        """
        )
        after = self.prep(
            """
            @tabwidth -4

            line 1
            TABline 2
            TAB  line 3
            line4
        """
        ).replace('TAB', '\t')
        i, j = 13, len(before)
        func = c.convertAllBlanks
        self.runTest(before, after, i, j, func)

    # @+node:ekr.20210906172626.4: *3* TestUndo.test_convertAllTabs
    def test_convertAllTabs(self):
        c = self.c
        before = self.prep(
            """
            @tabwidth -4

            line 1
            TABline 2
            TAB  line 3
            line4
        """
        ).replace('TAB', '\t')
        after = self.prep(
            """
            @tabwidth -4

            line 1
                line 2
                  line 3
            line4
        """
        ).replace('TAB', '\t')
        i, j = 13, 45
        func = c.convertAllTabs
        self.runTest(before, after, i, j, func)

    # @+node:ekr.20210906172626.5: *3* TestUndo.test_convertBlanks
    def test_convertBlanks(self):
        c = self.c
        before = self.prep(
            """
            @tabwidth -4

            line 1
                line 2
                  line 3
            line4
        """
        )
        after = self.prep(
            """
            @tabwidth -4

            line 1
            TABline 2
            TAB  line 3
            line4
        """
        ).replace('TAB', '\t')
        i, j = 13, 51
        func = c.convertBlanks
        self.runTest(before, after, i, j, func)

    # @+node:ekr.20210906172626.6: *3* TestUndo.test_convertTabs
    def test_convertTabs(self):
        c = self.c
        before = self.prep(
            """
            @tabwidth -4

            line 1
            TABline 2
            TAB  line 3
            line4
        """
        ).replace('TAB', '\t')
        after = self.prep(
            """
            @tabwidth -4

            line 1
                line 2
                  line 3
            line4
        """
        ).replace('TAB', '\t')
        i, j = 13, 45
        func = c.convertTabs
        self.runTest(before, after, i, j, func)

    # @+node:ekr.20210906172626.7: *3* TestUndo.test_dedentBody
    def test_dedentBody(self):
        c = self.c
        before = self.prep(
            """
            line 1
                line 2
                line 3
            line 4
        """
        )
        after = self.prep(
            """
            line 1
            line 2
            line 3
            line 4
        """
        )
        i = before.find('line 2')
        j = before.find('3')
        func = c.dedentBody
        self.runTest(before, after, i, j, func)

    # @+node:ekr.20210906172626.8: *3* TestUndo.test_deleteComments
    def test_deleteComments(self):
        c = self.c
        before = self.prep(
            """
            @language python

            def deleteCommentTest():

            #     if 1:
            #         a = 2
            #         b = 3

                pass
        """
        )
        after = self.prep("""
            @language python

            def deleteCommentTest():

                if 1:
                    a = 2
                    b = 3

                pass
        """)
        i = before.find('if 1')
        j = before.find('b = 3')
        func = c.deleteComments
        self.runTest(before, after, i, j, func)

    # @+node:ekr.20210906172626.9: *3* TestUndo.test_deleteComments 2
    def test_deleteComments_2(self):
        c = self.c
        before = self.prep(
            """
            @language python

            def deleteCommentTest():

            #     if 1:
            #         a = 2
            #         b = 3

                # if 1:
                    # a = 2
                    # b = 3

                pass
        """
        )
        after = self.prep(
            """
            @language python

            def deleteCommentTest():

                if 1:
                    a = 2
                    b = 3

                if 1:
                    a = 2
                    b = 3

                pass
        """
        )
        i = before.find('if 1')
        j = before.find('# b = 3')
        func = c.deleteComments
        self.runTest(before, after, i, j, func)

    # @+node:ekr.20210906172626.16: *3* TestUndo.test_edit_headline
    def test_edit_headline(self):
        # Brian Theado.
        c = self.c
        p = c.p
        u = c.undoer
        node1 = p.insertAsLastChild()
        node2 = node1.insertAfter()
        node3 = node2.insertAfter()
        node1.h = 'node 1'
        node2.h = 'node 2'
        node3.h = 'node 3'
        self.assertEqual([p.h for p in p.subtree()], ['node 1', 'node 2', 'node 3'])
        # Select 'node 1' and modify the headline as if a user did it
        u.clearUndoState()
        node1 = p.copy().moveToFirstChild()
        c.selectPosition(node1)
        c.editHeadline()
        w = c.frame.tree.headline_wrapper(node1)
        w.insert(0, 'changed - ')
        c.endEditing()
        self.assertEqual([p.h for p in p.subtree()], ['changed - node 1', 'node 2', 'node 3'])
        # Move the selection and undo the headline change
        c.selectPosition(node1.copy().moveToNext())
        for _i in range(3):
            u.undo()
            # The undo should restore the 'node 1' headline string
            self.assertEqual([p.h for p in p.subtree()], ['node 1', 'node 2', 'node 3'])
            # The undo should select the edited headline.
            self.assertEqual(c.p, node1)
            u.redo()

    # @+node:ekr.20210906172626.10: *3* TestUndo.test_extract_test
    def test_extract_test(self):
        c = self.c
        before = self.prep(
            """
            before
                < < section > >
                sec line 1
                    sec line 2 indented
            sec line 3
            after
        """
        )
        after = self.prep(
            """
            before
                < < section > >
            after
        """
        )
        i = before.find('< <')
        j = before.find('line 3')
        func = c.extract
        self.runTest(before, after, i, j, func)

    # @+node:ekr.20210906172626.14: *3* TestUndo.test_line_to_headline
    def test_line_to_headline(self):
        c = self.c
        before = self.prep(
            """
            before
            headline
            after
        """
        )
        after = self.prep(
            """
            before
            after
        """
        )
        i, j = 10, 10
        func = c.line_to_headline
        self.runTest(before, after, i, j, func)

    # @+node:ekr.20250625044932.1: *3* TestUndo.test_multiple_moves (renamed)
    def test_multiple_moves(self):
        # Test a group of moves.
        c = self.c
        p = c.p
        u = c.undoer
        p1 = p.insertAfter()
        p1.h = 'p1'
        p2 = p1.insertAfter()
        p2.h = 'p2'
        p3 = p2.insertAfter()
        p3.h = 'p3'
        p4 = p3.insertAfter()
        p4.h = 'p4'
        u.clearUndoState()
        # Do moves that invalidate nodes.
        c.selectPosition(p2)
        c.moveOutlineRight()  # Invalidates p2, p3, p4
        # Re-establish p3 and p4.
        p3 = p1.next()
        assert p3.h == 'p3', p3.h
        p4 = p3.next()
        assert p4.h == 'p4', p4.h
        c.selectPosition(p3)
        c.moveOutlineDown()
        # Undo and redo thrice.
        for _i in range(3):
            u.undo()
            u.redo()

    # @+node:ekr.20261014103254.20: *3* TestUndo.test_u_clone_node (moved, renamed)
    def test_u_clone_node(self):
        c = self.c
        p = c.p
        u = c.undoer
        p.b = 'before'
        v = p.v

        def test() -> None:
            with u.change_node(p, 'my-command'):
                p.b = 'after'
                clone = u.clone_node(p)
                assert clone.v == v

        for _i in range(3):
            test()
            assert len(u.beads) == 1
            assert p.b == 'after'
            assert c.p.isCloned()
            u.undo()
            assert len(u.beads) == 1
            assert p.b == 'before'
            assert not c.p.isCloned()
            u.redo()
            assert len(u.beads) == 1
            assert p.b == 'after'
            assert c.p.isCloned()
            u.undo()
            assert len(u.beads) == 1
            assert p.b == 'before'
            assert not c.p.isCloned()

    # @+node:ekr.20261115010623.1: *3* TestUndo.test_u_clearAndWarn (new)
    def test_u_clearAndWarn(self):
        c = self.c
        u = c.undoer
        u.clearAndWarn(g.my_name())

    # @+node:ekr.20261114085127.1: *3* TestUndo.test_u_delete_node (new)
    def test_u_delete_node(self):
        c = self.c
        p = c.p
        u = c.undoer

        old_p = p.copy()
        old_h = p.h

        def delete_node() -> None:
            with u:
                u.set_command_name(g.my_name())
                u.delete_node(old_p)

        delete_node()
        new_h = c.p.h
        assert new_h != old_h
        for _i in range(3):
            u.undo()
            assert c.p.h == old_h, c.p.h
            u.redo()
            assert c.p.h == new_h, new_p.h

    # @+node:ekr.20261114073916.1: *3* TestUndo.test_u_insert_node (new)
    def test_u_insert_node(self):
        c = self.c
        p = c.p
        u = c.undoer

        old_p = p.copy()
        old_h = p.h
        inserted_h = 'Test node'
        cloned_h = 'Clone of test node'

        def insert_as_first_child() -> Position:
            with u:
                u.set_command_name(g.my_name())
                new_p = u.insert_node(c.p, as_child=True, index=0)
                new_p.h = inserted_h
                u.redraw_and_edit(new_p)
                new_p.h = cloned_h
                return new_p

        new_p = insert_as_first_child()
        assert new_p.h == cloned_h, new_p.h
        for _i in range(3):
            u.undo()
            assert c.p.h == old_h, c.p.h
            u.redo()
            assert new_p.h == cloned_h, new_p.h

    # @+node:ekr.20261114081317.1: *3* TestUndo.test_u_insert_node_after (new)
    def test_u_insert_node_after(self):
        c = self.c
        p = c.p
        u = c.undoer

        old_p = p.copy()
        old_h = p.h
        inserted_h = 'Test node'
        cloned_h = 'Clone of test node'

        after_p = self.root_p.insertAfter()
        after_p.h = 'after node'

        def insert_before() -> Position:
            with u:
                u.set_command_name(g.my_name())
                new_p = u.insert_node(c.p, before=True)
                new_p.h = inserted_h
                u.redraw_and_edit(new_p)
                new_p.h = cloned_h
                return new_p

        new_p = insert_before()
        assert new_p.h == cloned_h, new_p.h
        for _i in range(3):
            u.undo()
            assert c.p.h == old_h, c.p.h
            u.redo()
            assert new_p.h == cloned_h, new_p.h

    # @+node:ekr.20261114080738.1: *3* TestUndo.test_u_redraw_and_edit (new)
    def test_u_redraw_and_edit(self):
        c = self.c
        p = c.p
        u = c.undoer

        old_h = c.p.h
        new_h = 'changed node'

        def redraw_and_edit() -> None:
            with u:
                u.set_command_name('test_u_redraw_and_edit')
                p.h = new_h
                u.redraw_and_edit(p)

        redraw_and_edit()
        assert c.p.h == new_h, c.p.h
        for _i in range(3):
            u.undo()
            u.redo()

    # @+node:ekr.20261114090239.1: *3* TestUndo.test_u_type_text (new)
    def test_u_type_text(self):
        c = self.c
        p = c.p
        u = c.undoer
        w = c.frame.body.wrapper

        old_ins = w.getInsertPoint()
        old_sel = w.getSelectionRange()
        old_text = w.getAllText()

        new_text = 'New text'
        assert new_text != old_text
        new_ins = len(new_text)
        assert new_ins != old_ins
        new_sel = (0, len(new_text))
        assert new_sel != old_sel
        # g.trace(f"{old_ins=} {new_ins=} {old_sel=} {new_sel=}")

        def test_type_text() -> None:
            w.setAllText(new_text)
            w.setSelectionRange(*new_sel, insert=new_ins)
            p.v.b = new_text
            u.type_text(p, oldIns=old_ins, oldSel=old_sel, oldText=old_text, w=w)

        test_type_text()
        for _i in range(3):
            assert w.getAllText() == new_text, w.getAllText()  # Test 1
            assert w.getInsertPoint() == new_ins, w.getInsertPoint()  # Test 1.
            assert w.getSelectionRange() == new_sel, w.getSelectionRange()  # Test 1.
            u.undo()
            assert w.getAllText() == old_text, w.getAllText()
            assert w.getInsertPoint() == old_ins, w.getInsertPoint()  # Test 2.
            assert w.getSelectionRange() == old_sel, w.getSelectionRange()  # Test 2.
            u.redo()
            assert w.getAllText() == new_text, w.getAllText()  # Test 3.
            assert w.getInsertPoint() == new_ins, w.getInsertPoint()  # Test 3.
            assert w.getSelectionRange() == new_sel, w.getSelectionRange()  # Test 3.

    # @+node:ekr.20261114100249.1: *3* TestUndo.test_u_type_text_with_merge (new)
    def test_u_type_text_with_merge(self):
        c = self.c
        ec = c.editCommands
        p = c.p
        u = c.undoer
        w = c.frame.body.wrapper

        # Setup.
        old_text = 'original text'
        old_ins = len(old_text)
        old_sel = (old_ins, old_ins)

        def merge_beads() -> None:
            # Rename to avoid changing outer vars.
            oldIns = old_ins
            oldSel = old_sel
            oldText = old_text
            p.b = old_text
            w.setAllText(p.b)

            # Delete one character.
            w.setInsertPoint(oldIns)
            ec.backwardDeleteCharacter()
            assert w.getAllText() == 'original tex'
            u.type_text(p, oldIns=oldIns, oldSel=oldSel, oldText=oldText, w=w)
            assert len(u.beads) == 1

            # Insert three characters.
            oldIns -= 1
            oldSel = (oldIns, oldIns)
            p.b = oldText = w.getAllText() + 'XXX'
            w.setAllText(p.b)
            u.type_text(p, oldIns=oldIns, oldSel=oldSel, oldText=oldText, w=w)
            assert len(u.beads) == 1

        merge_beads()
        for _i in range(3):
            assert len(u.beads) == 1
            u.undo()
            assert len(u.beads) == 1
            u.redo()

    # @-others


# @-others
# @-leo
