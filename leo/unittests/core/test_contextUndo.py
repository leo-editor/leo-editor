# @+leo-ver=5-thin
# @+node:ekr.20261012161544.1: * @file ../unittests/core/test_contextUndo.py
"""Regression tests for composable undo and coexistence with legacy plugins."""

import ast
from pathlib import Path
from unittest.mock import patch

from leo.core import leoGlobals as g
from leo.core.leoGui import LeoKeyEvent
from leo.core.leoTest2 import LeoUnitTest
from leo.core.leoUndo import TypingBead


# @+others
# @+node:ekr.20261014103356.1: ** class TestContextUndo(LeoUnitTest)
class TestContextUndo(LeoUnitTest):
    # @+others
    # @+node:ekr.20261014103223.1: *3* TestContextUndo.setUp
    def setUp(self):
        super().setUp()
        self.c.undoer.clearUndoState()
        self.c.clearChanged()

    # @+node:ekr.20261014103254.1: *3* TestContextUndo.cycles
    def cycles(self, before, after):
        c = self.c
        u = c.undoer
        for _ in range(3):
            u.undo()
            before()
            self.assertEqual(c.checkOutline(), 0)
            u.redo()
            after()
            self.assertEqual(c.checkOutline(), 0)

    # @+node:ekr.20261014103254.2: *3* TestContextUndo.test_nested_context_composes_helpers_after_inner_exit
    def test_nested_context_composes_helpers_after_inner_exit(self):
        c = self.c
        p = c.p
        u = c.undoer

        def inner() -> None:
            with u.change_node(c.p, 'inner'):
                p.b = 'inner'
            self.assertTrue(len(u.beads) in (0, 1))

        def outer() -> None:
            with u.change_node(c.p, 'outer'):
                p.b = 'outer'
                inner()

        p.b = 'original'
        for _i in range(3):
            u.beads = []
            outer()
            assert p.b == 'inner'
            assert len(u.beads) == 1
            assert u.beads[0].command_name == 'outer'
            u.undo()
            assert p.b == 'original'
            assert len(u.beads) == 1
            assert u.beads[0].command_name == 'outer'
            u.redo()
            assert p.b == 'inner'
            assert len(u.beads) == 1
            assert u.beads[0].command_name == 'outer'
            u.undo()
            assert p.b == 'original'
            assert len(u.beads) == 1
            assert u.beads[0].command_name == 'outer'

    # @+node:ekr.20261014103254.3: *3* TestContextUndo.test_nested_node_contexts_capture_distinct_nodes_and_same_node_once
    def test_nested_node_contexts_capture_distinct_nodes_and_same_node_once(self):
        c = self.c
        u = c.undoer
        p = c.p.copy()
        q = p.insertAfter()
        p.b, q.b = 'p original', 'q original'
        with u.change_node(p, 'nested edits'):
            p.b = 'p intermediate'
            with u.change_node(p, 'same node'):
                u.set_body(p, 'p final')
            with u.change_node(q, 'other node'):
                u.set_body(q, 'q final')
        self.cycles(
            lambda: self.assertEqual((p.b, q.b), ('p original', 'q original')),
            lambda: self.assertEqual((p.b, q.b), ('p final', 'q final')),
        )

    # @+node:ekr.20261014103254.4: *3* TestContextUndo.test_multiple_insert_helpers_share_one_bead
    def test_multiple_insert_helpers_share_one_bead(self):
        c = self.c
        p = c.p
        before = tuple(v for v in c.all_unique_nodes())
        with c.undoer as u:
            u.set_command_name('two inserts')
            first = u.insert_node(p)
            second = u.insert_node(first)
        after = tuple(v for v in c.all_unique_nodes())
        self.assertIn(second.v, after)
        self.cycles(
            lambda: self.assertEqual(tuple(c.all_unique_nodes()), before),
            lambda: self.assertEqual(tuple(c.all_unique_nodes()), after),
        )

    # @+node:ekr.20261014103254.6: *3* TestContextUndo.test_insert_command_redraw_and_edit_replays_once
    def test_insert_command_redraw_and_edit_replays_once(self):
        c = self.c
        p = c.p
        u = c.undoer
        with patch.object(c, 'redrawAndEdit', wraps=c.redrawAndEdit) as edit:
            inserted = c.insertHeadline()
            edit.assert_called_once_with(inserted, selectAll=True)
            edit.reset_mock()
            u.undo()
            edit.assert_called_once_with(p, selectAll=True)
            edit.reset_mock()
            u.redo()
            edit.assert_called_once_with(inserted, selectAll=True)

    # @+node:ekr.20261014103254.7: *3* TestContextUndo.test_snapshot_redraw_restores_body_selection_after_refresh
    def test_snapshot_redraw_restores_body_selection_after_refresh(self):
        c = self.c
        p = c.p
        u = c.undoer
        p.b = 'before'
        w = c.frame.body.wrapper
        w.setSelectionRange(1, 3, insert=1)
        with u.change_node(p, 'edit'):
            p.b = 'after'
            w.setSelectionRange(2, 4, insert=4)
        for _i in range(3):
            u.undo()
            self.assertEqual(w.getSelectionRange(), (1, 3))
            self.assertEqual(w.getInsertPoint(), 1)
            u.redo()
            self.assertEqual(w.getSelectionRange(), (2, 4))
            self.assertEqual(w.getInsertPoint(), 4)

    # @+node:ekr.20261014103254.9: *3* TestContextUndo.test_noop_context_preserves_redo
    def test_noop_context_preserves_redo(self):
        c = self.c
        p = c.p
        with c.undoer as u:
            u.set_command_name('edit')
            u.set_body(p, 'changed')
        u.undo()
        history = u.beads[:]
        with c.undoer as u:
            u.set_command_name('noop')
            u.set_body(p, p.b)
        with u.change_outline('noop bulk'):
            pass
        self.assertEqual(u.beads, history)
        self.assertTrue(u.canRedo())
        u.redo()
        self.assertEqual(p.b, 'changed')

    # @+node:ekr.20261014103254.10: *3* TestContextUndo.test_new_edit_discards_redo
    def test_new_edit_discards_redo(self):
        c = self.c
        p = c.p
        for text in ('one', 'two'):
            with c.undoer as u:
                u.set_command_name('edit')
                u.set_body(p, text)
        u.undo()
        with c.undoer as u:
            u.set_command_name('branch')
            u.set_body(p, 'three')
        self.assertEqual(len(u.beads), 2)
        self.assertFalse(u.canRedo())
        self.cycles(lambda: self.assertEqual(p.b, 'one'), lambda: self.assertEqual(p.b, 'three'))

    # @+node:ekr.20261014103254.11: *3* TestContextUndo.test_cut_and_paste_mark_clean_document_changed_and_restore_selection
    def test_cut_and_paste_mark_clean_document_changed_and_restore_selection(self):
        for command in ('cutText', 'pasteText'):
            with self.subTest(command=command):
                c, p, u = self.c, self.c.p, self.c.undoer
                u.clearUndoState()
                p.b = 'abcdef'
                w = c.frame.body.wrapper
                w.setSelectionRange(1, 4, insert=1)
                c.clearChanged()
                g.app.gui.replaceClipboardWith('XYZ')
                getattr(c.frame, command)(LeoKeyEvent(c, w=w))
                after = 'aef' if command == 'cutText' else 'aXYZef'
                self.assertEqual(p.b, after)
                self.assertTrue(c.changed)

                def before(p=p, w=w):
                    self.assertEqual(p.b, 'abcdef')
                    self.assertEqual(w.getAllText(), p.b)
                    self.assertEqual(w.getSelectionRange(), (1, 4))
                    self.assertEqual(w.getInsertPoint(), 1)

                self.cycles(before, lambda p=p, after=after: self.assertEqual(p.b, after))

    # @+node:ekr.20261014103254.14: *3* TestContextUndo.test_insert_reuses_vnode_and_preserves_later_contents
    def test_insert_reuses_vnode_and_preserves_later_contents(self):
        c = self.c
        original = c.p.copy()
        inserted = c.insertHeadline()
        vnode = inserted.v
        inserted.h = 'renamed directly'
        inserted.b = 'body added directly'
        child = inserted.insertAsLastChild()
        child.h = 'child'

        def before():
            self.assertEqual(c.p, original)
            self.assertFalse(c.positionExists(inserted))

        def after():
            self.assertIs(c.p.v, vnode)
            self.assertEqual(c.p.h, 'renamed directly')
            self.assertEqual(c.p.b, 'body added directly')
            self.assertIs(c.p.firstChild().v, child.v)

        self.cycles(before, after)

    # @+node:ekr.20261014103254.15: *3* TestContextUndo.test_all_insert_commands_repeat
    def test_all_insert_commands_repeat(self):
        for command in (
            'insertChild',
            'insertNodeAsFirstChild',
            'insertNodeAsLastChild',
            'insertHeadlineBefore',
        ):
            with self.subTest(command=command):
                self.setUp()
                c, u = self.c, self.c.undoer
                original = c.p.copy()
                inserted = getattr(c, command)()
                self.assertIsNotNone(inserted)
                vnode = inserted.v
                self.assertTrue(c.changed)
                self.cycles(
                    lambda c=c, original=original: self.assertEqual(c.p, original),
                    lambda c=c, vnode=vnode: self.assertIs(c.p.v, vnode),
                )
                u.undo()

    # @+node:ekr.20261014103254.16: *3* TestContextUndo.test_clone_returns_position_and_selects_it_on_redo
    def test_clone_returns_position_and_selects_it_on_redo(self):
        c = self.c
        p = c.p
        clone = c.clone()
        self.assertEqual(clone, c.p)

        def before():
            self.assertFalse(p.isCloned())
            self.assertEqual(c.p, p)

        def after():
            self.assertTrue(p.isCloned())
            self.assertEqual(c.p, clone)

        self.cycles(before, after)

    # @+node:ekr.20261014103254.17: *3* TestContextUndo.test_delete_first_root_adjusts_following_selection
    def test_delete_first_root_adjusts_following_selection(self):
        c = self.c
        first = c.p.copy()
        second = first.next().copy()
        c.deleteOutline()
        self.assertIs(c.p.v, second.v)

        def before():
            self.assertEqual(c.p, first)
            self.assertIs(c.rootPosition().next().v, second.v)

        def after():
            self.assertIs(c.p.v, second.v)
            self.assertEqual(c.p.childIndex(), 0)

        self.cycles(before, after)

    # @+node:ekr.20261014103254.18: *3* TestContextUndo.test_delete_selected_subtree_preserves_children
    def test_delete_selected_subtree_preserves_children(self):
        c = self.c
        p = c.p
        child = p.insertAsLastChild()
        grandchild = child.insertAsLastChild()
        grandchild.h = 'grandchild'
        p.expand()
        c.selectPosition(child)
        c.deleteOutline()
        self.cycles(
            lambda: self.assertIs(c.p.firstChild().v, grandchild.v),
            lambda: self.assertFalse(c.positionExists(child)),
        )

    # @+node:ekr.20261014103254.19: *3* TestContextUndo.test_outline_context_preserves_clones_and_nested_user_attributes
    def test_outline_context_preserves_clones_and_nested_user_attributes(self):
        c = self.c
        p = c.p
        u = c.undoer
        child = p.insertAsLastChild()
        clone = child.clone()
        child.v.u = {'nested': {'items': [1]}}
        with u.change_outline('bulk'):
            clone.doDelete()
            child.v.u['nested']['items'].append(2)
            child.b = 'new body'
            c.redraw(child)

        def before():
            self.assertTrue(child.isCloned())
            self.assertEqual(child.v.u, {'nested': {'items': [1]}})
            self.assertEqual(child.b, '')

        def after():
            self.assertFalse(child.isCloned())
            self.assertEqual(child.v.u, {'nested': {'items': [1, 2]}})
            self.assertEqual(child.b, 'new body')

        self.cycles(before, after)

    # @+node:ekr.20261014103254.20: *3* TestContextUndo.test_nested_bulk_and_action_helpers_make_one_record
    def test_nested_bulk_and_action_helpers_make_one_record(self):
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
            u.beads = []
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

    # @+node:ekr.20261014103254.21: *3* TestContextUndo.test_plain_and_clone_preserving_paste_repeat
    def test_plain_and_clone_preserving_paste_repeat(self):
        for retain in (False, True):
            with self.subTest(retain=retain):
                self.setUp()
                c = self.c
                p = c.p
                child = p.insertAsLastChild()
                child.h, child.b = 'child', 'child body'
                c.copyOutline()
                before = list(c.hiddenRootNode.children)
                pasted = c.pasteOutlineRetainingClones() if retain else c.pasteOutline()
                vnode = pasted.v
                pasted_child = pasted.firstChild().v
                self.assertEqual(vnode is p.v, retain)
                self.assertEqual(pasted_child is child.v, retain)
                self.cycles(
                    lambda c=c, before=before: self.assertEqual(c.hiddenRootNode.children, before),
                    lambda c=c, vnode=vnode, pasted_child=pasted_child: (
                        self.assertIs(c.p.v, vnode),
                        self.assertIs(c.p.firstChild().v, pasted_child),
                    ),
                )

    # @+node:ekr.20261014103254.22: *3* TestContextUndo.test_move_context_does_not_scan_outline
    def test_move_context_does_not_scan_outline(self):
        c = self.c
        p = c.p
        u = c.undoer
        sibling = p.next()
        c.selectPosition(sibling)
        with patch.object(u, 'capture_outline', side_effect=AssertionError('whole outline scan')):
            c.moveOutlineRight()
        self.cycles(
            lambda: self.assertEqual(c.p, sibling), lambda: self.assertEqual(c.p.parent(), p)
        )

    # @+node:ekr.20261014103254.23: *3* TestContextUndo.test_bulk_context_releases_state_after_exception_and_can_undo_partial_work
    def test_bulk_context_releases_state_after_exception_and_can_undo_partial_work(self):
        c = self.c
        p = c.p
        u = c.undoer
        with self.assertRaisesRegex(RuntimeError, 'partial'):
            with u.change_outline('partial bulk'):
                p.b = 'partial edit'
                raise RuntimeError('partial')
        self.assertIsNone(u.undoBead)
        self.assertEqual(u.undoBeadLevel, 0)
        self.assertEqual(u.capture_level, 0)
        u.undo()
        self.assertEqual(p.b, '')
        with u.change_node(p, 'next edit'):
            p.b = 'next'
        self.assertEqual(p.b, 'next')

    # @+node:ekr.20261014103254.24: *3* TestContextUndo.test_replay_exception_resets_flags_and_keeps_pointer
    def test_replay_exception_resets_flags_and_keeps_pointer(self):
        c = self.c
        p = c.p

        def fail():
            raise RuntimeError('replay')

        with c.undoer as u:
            u.set_command_name('failure')
            u.set_body(p, 'changed')
        b = u.beads[-1]
        with patch.object(b, 'undo_functions', [fail]):
            with self.assertRaisesRegex(RuntimeError, 'replay'):
                u.undo()
        self.assertFalse(u.undoing)
        self.assertEqual(u.bead, 0)
        u.undo()
        with patch.object(b, 'redo_functions', [fail]):
            with self.assertRaisesRegex(RuntimeError, 'replay'):
                u.redo()
        self.assertFalse(u.redoing)
        self.assertEqual(u.bead, -1)
        u.redo()
        self.assertEqual(p.b, 'changed')

    # @+node:ekr.20261014103254.27: *3* TestContextUndo.test_typing_preserves_text_mark_and_newlines
    def test_typing_preserves_text_mark_and_newlines(self):
        c = self.c
        p = c.p
        u = c.undoer
        for marked in (False, True):
            for old, new in (('', '\n'), ('a\n\n', 'a\nb\n\n'), ('a\n', ''), ('a\nb', 'a\nb\n')):
                with self.subTest(marked=marked, old=old, new=new):
                    u.clearUndoState()
                    p.b = old
                    p.setMarked() if marked else p.clearMarked()
                    w = c.frame.body.wrapper
                    w.setAllText(new)
                    w.setSelectionRange(len(new), len(new))
                    u.type_text(p, 'Typing', old, new, oldSel=(len(old), len(old)))
                    self.assertIsInstance(u.beads[-1], TypingBead)
                    self.cycles(
                        lambda old=old: self.assertEqual(p.b, old),
                        lambda new=new: self.assertEqual(p.b, new),
                    )
                    self.assertEqual(p.isMarked(), marked)

    # @+node:ekr.20261014103254.28: *3* TestContextUndo.test_typing_granularity_and_save_boundary
    def test_typing_granularity_and_save_boundary(self):
        c = self.c
        p = c.p
        u = c.undoer
        for granularity in ('char', 'line', 'word', 'node'):
            with self.subTest(granularity=granularity):
                p.b = ''
                u.clearUndoState()
                c.clearChanged()
                u.granularity = granularity
                for old, new in (('', 'a'), ('a', 'ab')):
                    w = c.frame.body.wrapper
                    w.setAllText(new)
                    w.setSelectionRange(len(new), len(new))
                    u.type_text(p, 'Typing', old, new, oldSel=(len(old), len(old)))
                self.assertEqual(len(u.beads), 2 if granularity == 'char' else 1)
                u.undo()
                self.assertEqual(p.b, 'a' if granularity == 'char' else '')
                u.redo()
                c.clearChanged()
                w.setAllText('abc')
                w.setSelectionRange(3, 3)
                u.type_text(p, 'Typing', 'ab', 'abc', oldSel=(2, 2))
                self.assertEqual(len(u.beads), 3 if granularity == 'char' else 2)
                u.undo()
                self.assertEqual(p.b, 'ab')
                self.assertTrue(c.changed)

    # @+node:ekr.20261014103254.29: *3* TestContextUndo.test_typing_word_boundary
    def test_typing_word_boundary(self):
        c = self.c
        p = c.p
        u = c.undoer
        u.granularity = 'word'
        p.b = ''
        for new in ('a', 'ab', 'ab ', 'ab c', 'ab cd'):
            old = p.b
            w = c.frame.body.wrapper
            w.setAllText(new)
            w.setSelectionRange(len(new), len(new))
            u.type_text(p, 'Typing', old, new, oldSel=(len(old), len(old)))
        self.assertEqual(len(u.beads), 2)
        u.undo()
        self.assertEqual(p.b, 'ab')
        u.undo()
        self.assertEqual(p.b, '')
        u.redo()
        u.redo()
        self.assertEqual(p.b, 'ab cd')

    # @+node:ekr.20261014103254.33: *3* TestContextUndo.test_bulk_marks_and_sort_keep_vnode_identity
    def test_bulk_marks_and_sort_keep_vnode_identity(self):
        c = self.c
        p = c.p
        u = c.undoer
        first = p.insertAsLastChild()
        first.h = 'Z'
        second = first.insertAfter()
        second.h = 'A'
        c.sortChildren()
        self.cycles(
            lambda: self.assertEqual(p.v.children, [first.v, second.v]),
            lambda: self.assertEqual(p.v.children, [second.v, first.v]),
        )
        u.clearUndoState()
        c.markSubheads()
        self.cycles(
            lambda: self.assertFalse(first.isMarked() or second.isMarked()),
            lambda: self.assertTrue(first.isMarked() and second.isMarked()),
        )

    # @+node:ekr.20261014103254.34: *3* TestContextUndo.test_copy_marked_repeats
    def test_copy_marked_repeats(self):
        self.setUp()
        c = self.c
        p = c.p
        child = p.insertAsLastChild()
        child.setMarked()
        before = c.hiddenRootNode.children[:]
        container = c.p.copy()
        result_child = container.firstChild().v
        self.cycles(
            lambda c=c, before=before: self.assertEqual(c.hiddenRootNode.children, before),
            lambda c=c, container=container, result_child=result_child: (
                self.assertEqual(c.p, container),
                self.assertIs(c.p.firstChild().v, result_child),
            ),
        )

    # @+node:ekr.20261014103254.35: *3* TestContextUndo.test_drag_clone_is_removed_on_undo
    def test_drag_clone_is_removed_on_undo(self):
        c = self.c
        p = c.p
        target = p.next()
        before = c.hiddenRootNode.children[:]
        c.dragCloneToNthChildOf(p, target, 0)
        clone = c.p.copy()
        self.assertTrue(p.isCloned())
        self.cycles(
            lambda: (
                self.assertEqual(c.hiddenRootNode.children, before),
                self.assertFalse(p.isCloned()),
            ),
            lambda: (self.assertEqual(c.p, clone), self.assertTrue(p.isCloned())),
        )

    # @+node:ekr.20261014103254.36: *3* TestContextUndo.test_randomized_composite_operations_restore_graph
    def test_randomized_composite_operations_restore_graph(self):
        import random

        c = self.c
        rng = random.Random(4996)

        def graph():
            return {
                v.gnx: (
                    v.h,
                    v.b,
                    v.isMarked(),
                    tuple(child.gnx for child in v.children),
                    tuple(sorted(parent.gnx for parent in v.parents)),
                )
                for v in [c.hiddenRootNode, *c.all_unique_nodes()]
            }

        snapshots = [graph()]
        for i in range(40):
            positions = list(c.all_positions())
            p = rng.choice(positions)
            c.selectPosition(p)
            with c.undoer as u:
                u.set_command_name(f'composite {i}')
                action = rng.choice(('insert', 'clone', 'delete', 'body', 'mark'))
                if action == 'insert':
                    inserted = u.insert_node(p, as_child=True)
                    u.change_headline(inserted, f'inserted {i}')
                elif action == 'clone':
                    u.clone_node(p)
                elif action == 'delete' and (p.hasParent() or p.hasNext() or p.hasBack()):
                    u.delete_node(p)
                elif action == 'mark':
                    with u.change_node(p, 'mark'):
                        p.setMarked() if not p.isMarked() else p.clearMarked()
                else:
                    u.set_body(p, f'body {i}')
            self.assertEqual(c.checkOutline(), 0)
            snapshots.append(graph())
        self.assertEqual(len(u.beads), 40)
        for snapshot in reversed(snapshots[:-1]):
            u.undo()
            self.assertEqual(graph(), snapshot)
            self.assertEqual(c.checkOutline(), 0)
        for snapshot in snapshots[1:]:
            u.redo()
            self.assertEqual(graph(), snapshot)
            self.assertEqual(c.checkOutline(), 0)

    # @+node:ekr.20261014103254.37: *3* TestContextUndo.test_per_node_undo_keeps_new_beads
    def test_per_node_undo_keeps_new_beads(self):
        c = self.c
        p = c.p
        u = c.undoer
        u.per_node_undo = True
        with u.change_node(p, 'edit first'):
            p.b = 'first'
        other = p.next()
        c.selectPosition(other)
        with u.change_node(other, 'edit other'):
            other.b = 'other'
        c.selectPosition(p)
        u.undo()
        self.assertEqual(p.b, '')
        self.assertEqual(other.b, 'other')
        u.redo()
        self.assertEqual(p.b, 'first')
        c.selectPosition(other)
        u.undo()
        self.assertEqual(other.b, '')
        self.assertEqual(p.b, 'first')

    # @+node:ekr.20261014103254.38: *3* TestContextUndo.test_core_callers_do_not_use_legacy_undo_api
    def test_core_callers_do_not_use_legacy_undo_api(self):
        root = Path(g.__file__).parents[1]
        legacy = {
            name
            for name in dir(self.c.undoer)
            if name.startswith(('before', 'after')) and name[6:7].isupper()
        }
        # Match all public before/after methods, including aliases.
        legacy.update(
            name for name in dir(self.c.undoer) if name.startswith('after') and name[5:6].isupper()
        )
        for directory in ('core', 'commands'):
            for path in (root / directory).glob('*.py'):
                if path.name == 'leoUndo.py':
                    continue
                for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
                    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                        self.assertNotIn(node.func.attr, legacy, f'{path}:{node.lineno}')

    # @+node:ekr.20261027134713.1: *3* TestContextUndo.test_clone_node
    def test_clone_node(self):
        # Test the changes in PR #5015.
        c = self.c
        p = c.p
        u = c.undoer
        v = p.v
        assert not p.isCloned()
        for _i in range(3):
            c.redraw_count = 0
            clone = c.clone()
            assert c.redraw_count == 1, f"{c.redraw_count=}"
            assert clone == c.p
            assert clone.v == v
            assert clone.isCloned()
            assert c.p.isCloned()
            u.undo()
            assert c.redraw_count == 2, f"{c.redraw_count=}"
            assert c.p.v == v
            assert c.p == p, f"\n{c.p=}\n  {p=}\n"
            assert not c.p.isCloned()
            u.redo()
            assert c.redraw_count == 3, f"{c.redraw_count=}"
            assert clone.v == v
            assert c.p.isCloned()
            u.undo()
            assert c.redraw_count == 4, f"{c.redraw_count=}"
            assert c.p.v == v
            assert c.p == p, f"\n{c.p=}\n  {p=}\n"
            assert not c.p.isCloned()

    # @-others


# @-others

# @-leo
