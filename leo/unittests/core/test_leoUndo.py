#@+leo-ver=5-thin
#@+node:ekr.20210906141410.1: * @file ../unittests/core/test_leoUndo.py
"""Tests of leoUndo.py"""

from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest
assert g

#@+others
#@+node:ekr.20210906141410.2: ** class TestUndo (LeoUnitTest)
class TestUndo(LeoUnitTest):
    #@+others
    #@+node:ekr.20210906141410.9: *3* TestUndo.runTest (Test)
    def runTest(self, before, after, i, j, func):
        """TestUndo.runTest."""
        c, p, w = self.c, self.c.p, self.c.frame.body.wrapper
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
        c.undoer.undo()
        result = w.getAllText()
        self.assertEqual(result, before, msg='after undo1')
        c.undoer.redo()
        result = w.getAllText()
        self.assertEqual(result, after, msg='after redo1')
        c.undoer.undo()
        result = w.getAllText()
        self.assertEqual(result, before, msg='after undo2')
    #@+node:ekr.20210906172626.2: *3* TestUndo.test_addComments
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
        """)
        after = self.prep(
        """
            @language python

            def addCommentTest():

                # if 1:
                    # a = 2
                    # b = 3

                pass
        """)
        i = before.find('if 1')
        j = before.find('b = 3')
        func = c.addComments
        self.runTest(before, after, i, j, func)
    #@+node:ekr.20210906172626.3: *3* TestUndo.test_convertAllBlanks
    def test_convertAllBlanks(self):
        c = self.c
        before = self.prep(
        """
            @tabwidth -4

            line 1
                line 2
                  line 3
            line4
        """)
        after = self.prep(
        """
            @tabwidth -4

            line 1
            TABline 2
            TAB  line 3
            line4
        """).replace('TAB', '\t')
        i, j = 13, len(before)
        func = c.convertAllBlanks
        self.runTest(before, after, i, j, func)
    #@+node:ekr.20210906172626.4: *3* TestUndo.test_convertAllTabs
    def test_convertAllTabs(self):
        c = self.c
        before = self.prep(
        """
            @tabwidth -4

            line 1
            TABline 2
            TAB  line 3
            line4
        """).replace('TAB', '\t')
        after = self.prep(
        """
            @tabwidth -4

            line 1
                line 2
                  line 3
            line4
        """).replace('TAB', '\t')
        i, j = 13, 45
        func = c.convertAllTabs
        self.runTest(before, after, i, j, func)
    #@+node:ekr.20210906172626.5: *3* TestUndo.test_convertBlanks
    def test_convertBlanks(self):
        c = self.c
        before = self.prep(
        """
            @tabwidth -4

            line 1
                line 2
                  line 3
            line4
        """)
        after = self.prep(
        """
            @tabwidth -4

            line 1
            TABline 2
            TAB  line 3
            line4
        """).replace('TAB', '\t')
        i, j = 13, 51
        func = c.convertBlanks
        self.runTest(before, after, i, j, func)
    #@+node:ekr.20210906172626.6: *3* TestUndo.test_convertTabs
    def test_convertTabs(self):
        c = self.c
        before = self.prep(
        """
            @tabwidth -4

            line 1
            TABline 2
            TAB  line 3
            line4
        """).replace('TAB', '\t')
        after = self.prep(
        """
            @tabwidth -4

            line 1
                line 2
                  line 3
            line4
        """).replace('TAB', '\t')
        i, j = 13, 45
        func = c.convertTabs
        self.runTest(before, after, i, j, func)
    #@+node:ekr.20210906172626.7: *3* TestUndo.test_dedentBody
    def test_dedentBody(self):
        c = self.c
        before = self.prep(
        """
            line 1
                line 2
                line 3
            line 4
        """)
        after = self.prep(
        """
            line 1
            line 2
            line 3
            line 4
        """)
        i = before.find('line 2')
        j = before.find('3')
        func = c.dedentBody
        self.runTest(before, after, i, j, func)
    #@+node:ekr.20210906172626.8: *3* TestUndo.test_deleteComments
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
        """)
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
    #@+node:ekr.20210906172626.9: *3* TestUndo.test_deleteComments 2
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
        """)
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
        """)
        i = before.find('if 1')
        j = before.find('# b = 3')
        func = c.deleteComments
        self.runTest(before, after, i, j, func)
    #@+node:ekr.20210906172626.16: *3* TestUndo.test_edit_headline
    def test_edit_headline(self):
        # Brian Theado.
        c, p = self.c, self.c.p
        node1 = p.insertAsLastChild()
        node2 = node1.insertAfter()
        node3 = node2.insertAfter()
        node1.h = 'node 1'
        node2.h = 'node 2'
        node3.h = 'node 3'
        self.assertEqual([p.h for p in p.subtree()], ['node 1', 'node 2', 'node 3'])
        # Select 'node 1' and modify the headline as if a user did it
        c.undoer.clearUndoState()
        node1 = p.copy().moveToFirstChild()
        c.selectPosition(node1)
        c.editHeadline()
        w = c.frame.tree.edit_widget(node1)
        w.insert(0, 'changed - ')
        c.endEditing()
        self.assertEqual([p.h for p in p.subtree()], ['changed - node 1', 'node 2', 'node 3'])
        # Move the selection and undo the headline change
        c.selectPosition(node1.copy().moveToNext())
        c.undoer.undo()
        # The undo should restore the 'node 1' headline string
        self.assertEqual([p.h for p in p.subtree()], ['node 1', 'node 2', 'node 3'])
        # The undo should select the edited headline.
        self.assertEqual(c.p, node1)
    #@+node:ekr.20210906172626.10: *3* TestUndo.test_extract_test
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
        """)
        after = self.prep(
        """
            before
                < < section > >
            after
        """)
        i = before.find('< <')
        j = before.find('line 3')
        func = c.extract
        self.runTest(before, after, i, j, func)
    #@+node:ekr.20210906172626.14: *3* TestUndo.test_line_to_headline
    def test_line_to_headline(self):
        c = self.c
        before = self.prep(
        """
            before
            headline
            after
        """)
        after = self.prep(
        """
            before
            after
        """)
        i, j = 10, 10
        func = c.line_to_headline
        self.runTest(before, after, i, j, func)
    #@+node:ekr.20210906172626.15: *3* TestUndo.test_restore_marked_bits
    def test_restore_marked_bits(self):
        c, p = self.c, self.c.p
        # Test of #1694.
        u, w = c.undoer, c.frame.body.wrapper
        oldText = p.b
        newText = p.b + '\n#changed'
        for marked in (True, False):
            c.undoer.clearUndoState()  # Required.
            if marked:
                p.setMarked()
            else:
                p.clearMarked()
            oldMarked = p.isMarked()
            w.setAllText(newText)  # For the new assert in w.updateAfterTyping.
            u.doTyping(p, undo_type='typing', oldText=oldText, newText=newText)
            u.undo()
            self.assertEqual(p.b, oldText)
            self.assertEqual(p.isMarked(), oldMarked)
            u.redo()
            self.assertEqual(p.b, newText)
            self.assertEqual(p.isMarked(), oldMarked)
    #@+node:ekr.20210906172626.17: *3* TestUndo.test_undo_group
    def test_undo_group(self):
        # Test an off-by-one error in c.undoer.bead.
        # The buggy redoGroup code worked if the undo group was the first item on the undo stack.
        c, p = self.c, self.c.p
        original = p.insertAfter()
        original_s = original.b = self.prep(
        """
            @tabwidth -4

            line 1
                line 2
                  line 3
            line4
        """)
        c.undoer.clearUndoState()
        c.selectPosition(original)
        c.copyOutline()  # Add state to the undo stack!
        c.pasteOutline()
        c.convertAllBlanks()  # Uses undoGroup.
        c.undoer.undo()
        self.assertEqual(original.b, original_s)
        c.pasteOutline()
        c.convertAllBlanks()
        c.pasteOutline()
        c.convertAllBlanks()
        c.undoer.undo()
        c.undoer.redo()
        self.assertEqual(original.b, original_s)
    #@-others
#@-others
#@-leo
