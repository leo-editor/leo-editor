# @+leo-ver=5-thin
# @+node:ekr.20031218072017.3603: * @file leoUndo.py
"""
Leo's undo/redo manager.

For the Theory of Operation, see Leo's appendices:
https://leo-editor.github.io/leo-editor/appendices.html
"""

# @+<< leoUndo imports & annotations >>
# @+node:ekr.20220821074023.1: ** << leoUndo imports & annotations >>
from __future__ import annotations
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from copy import deepcopy
from typing import cast, Any, Self, TYPE_CHECKING
from leo.core import leoGlobals as g
from leo.core.leoNodes import Position, VNode

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent
    from leo.plugins.qt_text import QTextMixin


# @-<< leoUndo imports & annotations >>


def cmd(name: str) -> Callable:
    """Command decorator for the Undoer class."""
    return g.new_cmd_decorator(name, ['c', 'undoer'])


# @+others
# @+node:ekr.20261005092455.1: ** class UndoBead
class UndoBead:
    # @+<< UndoBead: slots >>
    # @+node:ekr.20261006122714.1: *3* << UndoBead: slots >>
    __slots__ = (
        'c',
        'command_name',
        'old_p',
        'redo_finishers',
        'redo_functions',
        'redraw_finishers',
        'undoType',
        'undo_finishers',
        'undo_functions',
        'undoer',
    )

    # @-<< UndoBead: slots >>

    def __repr__(self) -> str:
        return f"UndoBead: {self.command_name or '<no command_name>'}"

    # @+others
    # @+node:ekr.20261007113407.1: *3* UndoBead.__init__
    def __init__(self, undoer: Undoer) -> None:
        # Let.
        c = undoer.c
        self.c = c
        self.command_name = None
        self.old_p = c.p.copy()
        self.redo_finishers: list[Callable] = []
        self.redo_functions: list[Callable] = []
        self.redraw_finishers: tuple[Callable, Callable] | None = None
        self.undoType = ''  # Required. Set by u.set_command_name
        self.undo_finishers: list[Callable] = []
        self.undo_functions: list[Callable] = []
        self.undoer = undoer

    # @+node:ekr.20261014182326.1: *3* undoBead.add_redraw_finishers
    def add_redraw_finishers(
        self,
        redo_redraw_finisher: Callable,
        undo_redraw_finisher: Callable,
    ) -> None:

        if self.redraw_finishers is not None:
            message = f"u.redraw_finishers already exist: {g.callers()=}\n"
            if g.unitTesting:
                assert False, message
            print()
            g.trace()

        self.redraw_finishers = redo_redraw_finisher, undo_redraw_finisher

    # @+node:ekr.20261010164513.1: *3* undoBead.add_recolor
    def add_recolor(self, new_p: Position, old_p: Position) -> None:

        c = self.c
        new_p = new_p.copy()
        old_p = old_p.copy()

        def recolor_redoer() -> None:
            c.frame.scanForTabWidth(new_p)
            c.recolor(new_p)

        def recolor_undoer() -> None:
            c.frame.scanForTabWidth(old_p)
            c.recolor(old_p)

        self.add_finishers(recolor_redoer, recolor_undoer)

    # @+node:ekr.20261010150247.9: *3* undoBead.add_redraw
    def add_redraw(self, new_p: Position, old_p: Position) -> None:
        """
        Add finishers that will call c.redraw.
        The caller chooses the final redraw for the entire command.
        """
        c = self.c
        new_p = new_p.copy()
        old_p = old_p.copy()

        def redraw_redoer() -> None:
            c.redraw(new_p)

        def redraw_undoer() -> None:
            c.redraw(old_p)

        self.add_redraw_finishers(redraw_redoer, redraw_undoer)

    # @+node:ekr.20261010150247.10: *3* undoBead.add_redraw_and_edit
    def add_redraw_and_edit(self, new_p: Position, old_p: Position) -> None:

        c = self.c
        new_p = new_p.copy()
        old_p = old_p.copy()

        def redraw_and_edit_redoer_finisher() -> None:
            c.redrawAndEdit(new_p, selectAll=True)

        def redraw_and_edit_undoer_finisher() -> None:
            c.redrawAndEdit(old_p, selectAll=True)

        self.add_redraw_finishers(
            redraw_and_edit_redoer_finisher,
            redraw_and_edit_undoer_finisher,
        )

    # @+node:ekr.20261011192651.1: *3* undoBead.add_redraw_after_head_changed
    def add_redraw_after_head_changed(self) -> None:

        c = self.c

        # A single finisher suffices.
        def redraw_after_head_changed_finisher() -> None:
            c.redraw_after_head_changed()

        self.add_redraw_finishers(
            redraw_after_head_changed_finisher, redraw_after_head_changed_finisher
        )

    # @+node:ekr.20261011185637.1: *3* undoBead.check_undo
    def check_undo(self) -> None:
        """Perform an important sanity check."""
        tag = 'UndoBead.undo'
        c = self.c
        old_p = self.old_p
        if old_p != c.p:
            message = f"{tag}: Bad c.p\n  {c.p.h=}\n{old_p.h=}\n{g.callers()=}\n"
            print()
            g.trace(message)
        if self.redraw_finsishers is None:
            message = f"{tag}: Bad redraw_finishers. {g.callers()=}\n"
            print()
            g.trace(message)

    # @+node:ekr.20261007104333.1: *3* UndoBead.get (compatility)
    def get(self, key, default=None) -> Any:
        """A wrapper for u.undoTyping"""
        # Called infequently, but u.undoTyping *does* sometimes call it.
        d = {
            'kind':     self.undoType.lower(),
            'p':        self.old_p,
            'undoType': self.undoType,
        }  # fmt: skip
        return d.get(key, default)

    # @+node:ekr.20261006040132.1: *3* UndoBead.redo
    def redo(self) -> None:
        c = self.c
        for f in self.redo_functions:
            # g.trace('redoer:', f.__name__)
            f()
        if self.redraw_finishers:
            self.redraw_finishers[0]()
        for f in self.redo_finishers:
            # g.trace('finisher:', f.__name__)
            f()
        c.setChanged()  # Elegant!

    # @+node:ekr.20261006040137.2: *3* UndoBead.add_helpers & add_finishers
    def add_helpers(self, redo_function: Callable, undo_function: Callable) -> None:
        """Append the helpers (in correct order!) to the undo/redo lists."""
        if self.undoer.capture_level:
            return  # The enclosing snapshot records the complete operation.
        self.redo_functions.append(redo_function)
        self.undo_functions.insert(0, undo_function)  # Execute in reverse order.

    def add_finishers(self, redo_finisher: Callable, undo_finisher: Callable) -> None:
        """Append the helpers (in correct order!) to the undo/redo lists."""
        if self.undoer.capture_level:
            return
        self.redo_finishers.append(redo_finisher)
        self.undo_finishers.append(undo_finisher)  # Execute in given order.

    # @+node:ekr.20261006040137.1: *3* UndoBead.undo
    def undo(self) -> None:
        c = self.c
        for f in self.undo_functions:
            # g.trace('undoer:', f.__name__)
            f()
        if self.redraw_finishers:
            self.redraw_finishers[1]()
        for f in self.undo_finishers:
            # g.trace('undo finisher:', f.__name__)
            f()
        # A save may have occurred since this bead was created.
        c.setChanged()

    # @-others


# @+node:vivainio.202610110002.1: ** class TypingBead(UndoBead)
class TypingBead(UndoBead):
    """An incremental text patch, independent of the legacy Undoer ivars."""

    # @+others
    # @+node:ekr.20261014100558.1: *3* TypingBead.__init__ (trace)
    def __init__(self, undoer, p, old_text, new_text, old_sel, new_sel, new_ins, scroll):
        """Init a new Typing bead when a new bead is needed."""
        super().__init__(undoer)
        self.command_name = self.undoType = 'Typing'
        self.p = p.copy()
        self.old_sel = old_sel
        self.new_sel = new_sel
        self.new_ins = new_ins
        self.scroll = scroll
        self.marked = p.isMarked()
        self.update_patch(old_text, new_text)

    # @+node:ekr.20261014100625.1: *3* TypingBead.split_patch
    @staticmethod
    def split_patch(old_text, new_text):
        old, new = old_text.split('\n'), new_text.split('\n')
        leading = 0
        while leading < min(len(old), len(new)) and old[leading] == new[leading]:
            leading += 1
        trailing = 0
        while (
            trailing < min(len(old), len(new)) - leading
            and old[-trailing - 1] == new[-trailing - 1]
        ):
            trailing += 1
        return (
            leading,
            trailing,
            old[leading : len(old) - trailing],
            new[leading : len(new) - trailing],
        )

    # @+node:ekr.20261014100625.2: *3* TypingBead.update_patch
    def update_patch(self, old_text, new_text):
        self.leading, self.trailing, self.old_lines, self.new_lines = self.split_patch(
            old_text, new_text
        )

    # @+node:ekr.20261014100625.3: *3* TypingBead.replace_middle
    def replace_middle(self, text, middle):
        lines = text.split('\n')
        return '\n'.join(
            lines[: self.leading] + middle + (lines[-self.trailing :] if self.trailing else [])
        )

    # @+node:ekr.20261014100625.4: *3* TypingBead.apply
    def apply(self, middle, sel, ins):
        c = self.c
        p = self.p
        if c.p != p:
            c.selectPosition(p)
        p.v.b = self.replace_middle(p.b, middle)
        p.setDirty()
        if self.marked:
            c.setMarked(p)
        else:
            c.clearMarked(p)
        w = c.frame.body.wrapper
        w.setAllText(p.b)
        if sel is not None:
            w.setSelectionRange(*sel, insert=ins)
        w.setYScrollPosition(self.scroll)
        c.recolor(p)
        c.setChanged()

    # @+node:ekr.20261014100625.5: *3* TypingBead.undo
    def undo(self):
        self.apply(self.old_lines, self.old_sel, self.old_sel[1] if self.old_sel else None)

    # @+node:ekr.20261014100625.6: *3* TypingBead.redo
    def redo(self):
        self.apply(self.new_lines, self.new_sel, self.new_ins)

    # @-others


# @+node:ekr.20031218072017.3605: ** class Undoer
class Undoer:
    """A class that implements unlimited undo and redo."""

    # @+<< class Undoer: __slots__ >>
    # @+node:ekr.20261102102957.1: *3* << class Undoer: __slots__ >>
    __slots__ = (
        'bead',
        'beads',
        'c',
        'capture_level',
        'granularity',  # Keep, for now, for unit tests.
        'groupCount',
        'inHead',
        'max_undo_stack_size',
        'node_captures',
        'p',
        'realRedoMenuLabel',
        'realUndoMenuLabel',
        'redoMenuLabel',
        'redoing',
        'undoBead',
        'undoBeadLevel',
        'undoMenuLabel',
        'undoType',
        'undoing',
    )
    # @-<< class Undoer: __slots__ >>

    # @+others
    # @+node:ekr.20031218072017.3606: *3* u.__init__
    def __init__(self, c: Cmdr) -> None:
        self.c = c
        # State.
        self.bead = -1  # Index of the present bead.
        self.beads = []  # List of undo nodes.
        self.capture_level = 0
        # self.granularity = None  # Set in reloadSettings.
        self.groupCount = 0
        self.inHead = False
        self.max_undo_stack_size = c.config.getInt('max-undo-stack-size') or 0
        self.node_captures = set()
        self.p = cast(Position, None)
        self.realRedoMenuLabel = "Can't Redo"
        self.realUndoMenuLabel = "Can't Undo"
        self.redoMenuLabel = "Can't Redo"
        self.redoing = False
        self.undoBead = None
        self.undoBeadLevel = 0
        self.undoMenuLabel = "Can't Undo"
        self.undoType = "Can't Undo"
        self.undoing = False
        # Update settings.
        self.reloadSettings()

    # @+node:ekr.20261102104518.1: *3* u: Entries
    # @+node:ekr.20031218072017.3610: *4* u.canRedo & canUndo
    # Translation does not affect these routines.

    def canRedo(self) -> bool:
        u = self
        return u.redoMenuLabel != "Can't Redo"

    def canUndo(self) -> bool:
        u = self
        return u.undoMenuLabel != "Can't Undo"

    # @+node:ekr.20230714012821.1: *4* u.clearAndWarn
    def clearAndWarn(self, command_name: str) -> None:
        """
        Clear all undo state, but *only* if we aren't in an undo-related `with` block.
        """
        u = self
        if u.undoBeadLevel == 0:  # PR #5025
            # We aren't in undo code.
            u.clearUndoState()
            # This message would be annoying.
            # g.es_print_unique_message(f"{command_name} is not undoable")

    # @+node:ekr.20031218072017.3609: *4* u.clearUndoState
    def clearUndoState(self) -> None:
        """Clears the entire Undo state."""
        u = self
        u.setRedoType("Can't Redo")
        u.setUndoType("Can't Undo")
        u.beads = []
        u.bead = -1

    # @+node:ekr.20031218072017.2030: *4* u.redo
    @cmd('redo')
    def redo(self, event: LeoKeyEvent | None = None) -> None:
        """Redo the operation undone by the last undo."""
        u = self
        c = u.c
        if not c.p:
            return
        # End editing *before* getting state.
        c.endEditing()
        if not u.canRedo():
            return
        obj = u.getBead(u.bead + 1)
        if not obj:
            return

        # Init status.
        u.redoing = True
        u.groupCount = 0

        # Dispatch.
        try:
            if isinstance(obj, UndoBead):
                obj.redo()
            else:
                g.es_print_unique_message(f"no redo helper for {u.kind} {u.undoType}")
            c.checkOutline()
        finally:
            u.redoing = False
        u.bead += 1
        u.setUndoTypes()

    # @+node:ekr.20191213085126.1: *4* u.reloadSettings
    def reloadSettings(self) -> None:
        """Undoer.reloadSettings."""
        c = self.c
        if 0:
            self.granularity = c.config.getString('undo-granularity')
            if self.granularity:
                self.granularity = self.granularity.lower()
            if self.granularity not in ('node', 'line', 'word', 'char'):
                self.granularity = 'line'

    # @+node:vivainio.202610110002.2: *4* u.type_text and helper
    def type_text(
        self,
        p: Position,
        oldText: str,
        newText: str,
        *,
        newInsert: int,
        oldSel: tuple[int, int],
        newSel: tuple[int, int],
        oldYview: int | None = None,
    ) -> None:
        """
        Handle all undo tasks related to typing in the body pane. Called by:
        - ec.selfInsertCommand.
        - LeoQListWidget.select_callback.
        - QTextMixin.onTextChanged.
        """
        if self.undoing or self.redoing or oldText == newText:
            return
        u = self
        c = u.c
        w = c.frame.body.wrapper
        newSel = newSel if newSel is not None else w.getSelectionRange()
        newInsert = newInsert if newInsert is not None else w.getInsertPoint()
        scroll = oldYview if oldYview is not None else w.getYScrollPosition()
        bead = u.peekBead(u.bead)
        if u._can_merge(oldText=oldText, newText=newText, oldSel=oldSel, newSel=newSel):
            original = bead.replace_middle(oldText, bead.old_lines)
            bead.update_patch(original, newText)
            assert isinstance(bead, TypingBead)
            bead.new_sel, bead.new_ins = newSel, newInsert
        else:
            bead = TypingBead(u, p, oldText, newText, oldSel, newSel, newInsert, scroll)
            u.pushBead(bead)
        p.v.b = newText  # Do **not** use p.b = newText!!!
        u._update_after_typing(p, w)

    # @+node:ekr.20201127035748.1: *5* u._update_after_typing
    def _update_after_typing(self, p: Position, w: QTextMixin) -> None:
        """
        Perform all update tasks after changing body text.

        This is ugly, ad-hoc code, but should be done uniformly.
        """
        c = self.c
        if g.isTextWrapper(w):
            # An important, ever-present unit test.
            if p == c.p:
                all = w.getAllText()
                if g.unitTesting:
                    assert p.b == all, (w, g.callers())
                elif p.b != all:
                    g.trace(
                        f"\np.b != w.getAllText() p: {p.h} \n"
                        f"w: {w!r} \n{g.callers()}\n"
                    )  # fmt: skip
            p.v.insertSpot = ins = w.getInsertPoint()
            # From u.doTyping.
            newSel = w.getSelectionRange()
            if newSel is None:
                p.v.selectionStart, p.v.selectionLength = (ins, 0)
            else:
                i, j = newSel
                p.v.selectionStart, p.v.selectionLength = (i, j - i)
        else:
            if g.unitTesting:
                assert False, f"Not a text wrapper: {g.callers()}"  # noqa
            g.trace('Not a text wrapper')
            p.v.insertSpot = 0
            p.v.selectionStart, p.v.selectionLength = (0, 0)
        if not p.isDirty():
            p.setDirty()
        if not c.isChanged():
            c.setChanged()

        # Update icons.
        val = p.computeIcon()
        if not hasattr(p.v, "iconVal") or val != p.v.iconVal:
            p.v.iconVal = val
        if p == c.p:
            # Recolor the body.
            c.frame.scanForTabWidth(p)  # Calls frame.setTabWidth()
            c.recolor()
            w.setFocus()

    # @+node:ekr.20031218072017.2039: *4* u.undo
    @cmd('undo')
    def undo(self, event: LeoKeyEvent | None = None) -> None:
        """Undo the operation described by the undo parameters."""
        u = self
        c = u.c
        if not c.p:
            g.trace('no current position')
            return
        # End editing *before* getting state.
        c.endEditing()
        if not u.canUndo():
            return
        obj = u.getBead(u.bead)
        if not obj:
            return

        # Init status.
        u.undoing = True
        u.groupCount = 0

        # Dispatch.
        try:
            if isinstance(obj, UndoBead):
                obj.undo()
            else:
                g.es_print_unique_message(f"no undo helper for {u.kind} {u.undoType}")
            c.checkOutline()
        finally:
            u.undoing = False
        u.bead -= 1
        u.setUndoTypes()

    # @+node:ekr.20261015042013.1: *4* u: actions
    # @+node:ekr.20261006155509.1: *5* u.clone_node
    def clone_node(self, p: Position) -> Position:
        """Clone p, returning and selecting the new occurrence."""
        u = self
        b = u._require_bead()
        c = u.c
        old_p = p.copy()
        clone = p.clone()

        # Do the action.
        clone.setDirty()
        c.p = clone
        clone_p = clone.copy()
        clone_p.setAllAncestorAtFileNodesDirty()

        def clone_redoer():
            clone_p._linkAfter(old_p)
            clone_p.setDirty()
            c.p = clone_p

        def clone_undoer():
            clone_p.doDelete(old_p)
            c.p = old_p

        b.add_helpers(clone_redoer, clone_undoer)
        return clone

    # @+node:ekr.20261005143707.1: *5* u.delete_node
    def delete_node(self, p: Position) -> None:
        """Delete p without scheduling a redraw; retain its original links."""
        u = self
        b = u._require_bead()
        c = u.c
        old_p = p.copy()
        old_back, old_parent = p.back(), p.parent()
        new_p = p.visBack(c) if p.hasVisBack(c) else p.next()
        if not new_p:
            g.trace("Can not delete the outline's only node")
            return

        # Do the action.
        old_p.doDelete(new_p)
        c.p = new_p
        new_p.setDirty()
        c.p.setAllAncestorAtFileNodesDirty()
        c.checkOutline()

        def delete_node_redoer():
            old_p.doDelete()
            c.p = new_p

        def delete_node_undoer():
            if old_back:
                old_p._linkAfter(old_back)
            elif old_parent:
                old_p._linkAsNthChild(old_parent, 0)
            else:
                old_p._linkAsRoot()
            old_p.setDirty()
            c.p = old_p

        if old_p.v not in u.node_captures:
            b.add_helpers(delete_node_redoer, delete_node_undoer)

    # @+node:ekr.20261006155622.1: *5* u.insert_node
    def insert_node(
        self,
        p: Position,
        *,
        as_child: bool = False,
        index: int | None = None,
        before: bool = False,
    ) -> Position:
        """Insert a node once; redo relinks that same vnode, including its subtree."""
        u = self
        b = u._require_bead()
        c = u.c
        old_p = p.copy()
        if before:
            new_p = p.insertBefore()
            # Inserting before p changes p's original index.
        elif (
            as_child
            or p.hasChildren()
            and p.isExpanded()
            or c.hoistStack
            and p == c.hoistStack[-1].p
        ):
            if index is None:
                insert_at_end = c.config.getBool('insert-new-nodes-at-end')
                index = p.numberOfChildren() if insert_at_end else 0
            new_p = p.insertAsNthChild(index)
        else:
            new_p = p.insertAfter()

        # Do the action.
        new_p.setDirty()
        c.p = new_p
        parent = new_p.parent()
        back = new_p.back()
        saved = new_p.copy()
        new_p.setAllAncestorAtFileNodesDirty()

        def insert_node_redoer():
            if back:
                saved._linkAfter(back)
            elif parent:
                saved._linkAsNthChild(parent, 0)
            else:
                saved._linkAsRoot()
            saved.setDirty()
            c.p = saved

        def insert_node_undoer():
            saved.doDelete()
            old_p.setAllAncestorAtFileNodesDirty()
            c.p = old_p

        b.add_helpers(insert_node_redoer, insert_node_undoer)
        g.doHook('create-node', c=c, p=new_p)
        return new_p

    # @+node:ekr.20261005140833.1: *5* u.set_body
    def set_body(
        self,
        new_p: Position,
        new_body: str,
        *,
        old_body: str | None = None,
    ) -> None:
        """Change p.b"""
        u = self
        b = u._require_bead()
        c = u.c
        w = c.frame.body.wrapper
        if not g.isTextWrapper(w):
            g.error(f"Not a text wrapper: {w=} {g.callers()}")
            return

        new_p = new_p.copy()
        if old_body is None:
            old_body = new_p.b
        if old_body == new_body:
            return

        def set_body_update(p: Position, body: str) -> None:
            """Update p's data."""
            # Set p.v.b, not p.b! The p.b setter clears the selection!
            p.v.b = body
            p.setDirty()
            val = p.computeIcon()
            if not hasattr(p.v, "iconVal") or val != p.v.iconVal:
                p.v.iconVal = val
            c.recolor(p)  # Only for QScintilla.
            p.setAllAncestorAtFileNodesDirty()

        # Do the action!
        set_body_update(new_p, new_body)

        if c.p == new_p and w.getAllText() != new_body:
            sel, ins = w.getSelectionRange(), w.getInsertPoint()
            w.setAllText(new_body)
            w.setSelectionRange(*sel, insert=ins)

        # Add helpers. Use distinct names for debugging.

        def set_body_redoer() -> None:
            set_body_update(new_p, new_body)

        def set_body_undoer() -> None:
            set_body_update(new_p, old_body)

        if new_p.v not in u.node_captures:
            b.add_helpers(set_body_redoer, set_body_undoer)

    # @+node:ekr.20261005094529.2: *5* u.set_command_name
    def set_command_name(self, command_name: str) -> None:
        u = self
        b = u._require_bead()
        assert isinstance(b, UndoBead), repr(b)
        if u.undoBeadLevel == 1:
            b.command_name = command_name
            b.undoType = command_name
            # Menu labels are updated when the completed bead is pushed.

    # @+node:ekr.20261015042249.1: *4* u: contexts
    # @+node:ekr.20261009185938.1: *5* u.change_headline
    def change_headline(self, p: Position, new_h: str, *, ch: str = '') -> None:
        """
        Change a headline and preserve directives, dirty bits and editor state.

        Called *only* from LeoTree.onHeadChanged

        This method should *not* have an @contextmanager decorator:
        it is never called from within other @contextmanager methods.
        """
        u = self
        b = u._require_bead()
        c = u.c
        old_h = p.h
        if old_h == new_h:
            return

        p = p.copy()

        def update(head):
            c.p = p
            p.initHeadString(head)
            p.setDirty()  # Call p.v.setAllAncestorAtFileNodesDirty()
            c.frame.tree.setHeadline(p, head)

        # Do the action.
        # Leave the live editor alone: it may contain multiline abbreviation text.
        p.initHeadString(new_h)
        p.setDirty()  # Call p.v.setAllAncestorAtFileNodesDirty()
        c.frame.scanForTabWidth(p)
        c.recolor(p)
        g.doHook('headkey2', c=c, p=p, ch=ch, changed=True)

        # Add helpers

        def change_headline_redoer():
            update(new_h)

        def change_headline_undoer():
            update(old_h)

        b.add_helpers(change_headline_redoer, change_headline_undoer)
        b.add_recolor(p, p)

    # @+node:vivainio.202610110001.1: *5* u.change_node
    @contextmanager
    def change_node(self, p: Position, command_name: str) -> Iterator[Undoer]:
        """
        Handle doing, undoing, and redoing changes to one node.

        u.restore_node does the heavy lifting.
        """
        u = self
        c = u.c
        if u.undoing or u.redoing:
            yield u
            return
        if not c.changed:
            c.setChanged()
        with u:
            u.set_command_name(command_name)
            if u.capture_level > 0 or p.v in u.node_captures:
                yield u
                return
            old_p = c.p
            old_state = u.capture_node(p.v)
            old_ui = u.capture_ui()
            u.node_captures.add(p.v)
            if old_p.v != c.p.v:
                message = f"u.change_node changed p.v: {p.v.h=} {g.callers()=}"
                g.es_print_unique_message(message)
            try:
                yield u
            finally:
                u.node_captures.remove(p.v)
                new_p = c.p
                u._redraw(new_p)  # PR #5005. Calls new_p.setDirty()
                new_state = u.capture_node(p.v)
                if old_state != new_state:
                    new_ui = u.capture_ui()

                    def change_node_redoer() -> None:
                        u.restore_node(p.v, new_state)

                    def change_node_undoer() -> None:
                        u.restore_node(p.v, old_state)

                    u.undoBead.add_helpers(change_node_redoer, change_node_undoer)

                    def change_node_ui_redoer() -> None:
                        u.restore_ui(new_ui)
                        u._redraw(new_p)

                    def change_node_ui_undoer() -> None:
                        u.restore_ui(old_ui)
                        u._redraw(old_p)

                    u.undoBead.add_finishers(change_node_ui_redoer, change_node_ui_undoer)

    # @+node:vivainio.202610110001.2: *5* u.change_outline & helpers
    @contextmanager
    def change_outline(self, command_name: str) -> Iterator[Undoer]:
        """
        Handle doing, undoing, and redoing changes throughout an outline.

        Prefer u.change_node for actions affecting only a single node.

        This method scans the entire outline, but creates minimal undo/redo data.
        Despite the scan, this method is fast, taking about 0.04 sec. to scan LeoPyRef.leo.

        u.restore_node does the heavy lifting of restoring all data.
        """
        u = self
        c = u.c
        if u.undoing or u.redoing:
            yield u
            return
        if not c.changed:
            c.setChanged()
        with u:
            u.set_command_name(command_name)
            if u.capture_level > 0:
                yield u
                return
            assert not u.node_captures, "Use change_outline outside change_node for bulk edits"
            old_p = c.p
            old_state = u.capture_outline()
            old_ui = u.capture_ui()
            u.capture_level += 1
            try:
                yield u
            finally:
                u.capture_level -= 1
                new_p = c.p  # PR #5005
                u._redraw(new_p)  # PR #5005: calls new_p.setDirty()
                new_state = u.capture_outline()
                old_delta, new_delta = {}, {}
                for v in old_state.keys() | new_state.keys():
                    old = old_state.get(v)
                    new = new_state.get(v)
                    if old is None:
                        # Preserve the detached subtree's internal links on undo.
                        old = (*new[:2], tuple(p for p in new[2] if p not in old_state))  # type:ignore
                    if new is None:
                        new = (*old[:2], tuple(p for p in old[2] if p not in new_state))
                    if old != new:
                        old_delta[v], new_delta[v] = old, new
                if old_delta:
                    new_ui = u.capture_ui()

                    def change_outline_redoer() -> None:
                        u.restore_outline(new_delta)

                    def change_outline_undoer() -> None:
                        u.restore_outline(old_delta)

                    u.undoBead.add_helpers(change_outline_redoer, change_outline_undoer)

                    def change_outline_ui_redoer() -> None:
                        u.restore_ui(new_ui)
                        u._redraw(new_p)  # Calls new_p.setDirty()

                    def change_outline_ui_undoer() -> None:
                        u.restore_ui(old_ui)
                        u._redraw(old_p)  # Calls old_p.setDirty()

                    u.undoBead.add_finishers(change_outline_ui_redoer, change_outline_ui_undoer)

    # @+node:ekr.20261015041620.2: *6* u.capture_outline
    def capture_outline(self) -> dict:
        u = self
        c = u.c
        result = {}
        pending = [c.hiddenRootNode]
        while pending:
            v = pending.pop()
            if v in result:
                continue
            result[v] = u.capture_node(v), tuple(v.children), tuple(v.parents)
            pending.extend(v.children)
        return result

    # @+node:ekr.20261015041620.3: *6* u.restore_outline
    def restore_outline(self, delta: dict) -> None:
        # Restore every link before touching content or propagating dirty bits.
        u = self
        for v in delta:
            v.setAllAncestorAtFileNodesDirty()
        for v, (_, children, parents) in delta.items():
            v.children = list(children)
            v.parents = list(parents)
        for v, (state, _, _) in delta.items():
            u.restore_node(v, state)

    # @+node:vivainio.202610110001.4: *5* u.change_recent_files
    @contextmanager
    def change_recent_files(self, command_name: str = 'Clear Recent Files') -> Iterator[Undoer]:
        """
        Handling doing, undoing and redoing for the 'Clear Recent Files' menu item."""
        u = self
        rf = g.app.recentFilesManager
        old_files = rf.recentFiles[:]
        with u:
            u.set_command_name(command_name)
            try:
                yield u
            finally:
                new_files = rf.recentFiles[:]
                if old_files != new_files:

                    def restore_recent_files(files):
                        rf.recentFiles = files[:]
                        for frame in g.app.windowList:
                            rf.createRecentFilesMenuItems(frame.c)
                        rf.writeRecentFilesFile(u.c)

                    def change_recent_files_redoer():
                        restore_recent_files(new_files)

                    def change_recent_files_undoer():
                        restore_recent_files(old_files)

                    u.undoBead.add_helpers(change_recent_files_redoer, change_recent_files_undoer)

    # @+node:vivainio.202610110003.1: *5* u.move_node
    @contextmanager
    def move_node(self, p: Position, command_name: str) -> Iterator[Undoer]:
        """
        Handle doing, undoing, and redoing moving a node.

        The internal move function does the heavy lifting.
        """
        u = self
        c = u.c
        if u.undoing or u.redoing:
            yield u
            return
        if not c.changed:
            c.setChanged()
        with u:
            u.set_command_name(command_name)
            if u.capture_level > 0:
                yield u
                return
            old_p, old_ui = p.copy(), u.capture_ui()
            try:
                yield u
            finally:
                new_p = p.copy()
                if old_p.v != c.p.v:
                    message = f"u.move_node changed p.v: {p.v.h=} {g.callers()=}"
                    g.es_print_unique_message(message)
                if old_p != new_p:
                    new_ui = u.capture_ui()
                    u._redraw(new_p)  # PR #5005: calls new_p.setDirty()

                    def move(source, target):
                        source.v._cutLink(source.childIndex(), source._parentVnode())
                        target.v._addLink(target.childIndex(), target._parentVnode())
                        # These call p.v.setAllAncestorAtFileNodesDirty()
                        source.setDirty()
                        target.setDirty()

                    def move_position_redoer():
                        move(old_p, new_p)

                    def move_position_undoer():
                        move(new_p, old_p)

                    u.undoBead.add_helpers(move_position_redoer, move_position_undoer)

                    def restore_ui_redoer():
                        u.restore_ui(new_ui)
                        u._redraw(new_p)

                    def restore_ui_undoer():
                        u.restore_ui(old_ui)
                        u._redraw(old_p)

                    u.undoBead.add_finishers(restore_ui_redoer, restore_ui_undoer)

    # @+node:ekr.20261018041400.1: *5* u:common context helpers
    # @+node:vivainio.202610110001.3: *6* u.capture_node
    def capture_node(self, v: VNode) -> tuple:
        """
        Record everything needed by u.restore_node.
        """
        return v.h, v.b, v.isMarked(), deepcopy(v.u)

    # @+node:ekr.20261015041620.4: *6* u.capture_ui
    def capture_ui(self) -> tuple:
        c = self.c
        w = c.frame.body.wrapper
        return c.p.copy(), w.getSelectionRange(), w.getInsertPoint(), w.getYScrollPosition()

    # @+node:ekr.20261015041620.1: *6* u.restore_node
    def restore_node(self, v: VNode, state: tuple) -> None:
        """
        Restore everything related to the given VNode:
        - dirty bits, including calling setAllAncestorAtFileNodesDirty.
        - marked bits.
        - uAs.
        - v.b
        - v.h
        """
        u = self
        c = u.c
        head, body, marked, ua = state
        head_changed = v.h != head
        v.initHeadString(head)
        v.setBodyString(body)
        v.u = deepcopy(ua)
        if marked:
            v.setMarked()
        else:
            v.clearMarked()
        val = v.computeIcon()
        if not hasattr(v, "iconVal") or val != v.iconVal:
            v.iconVal = val
        v.setAllAncestorAtFileNodesDirty()
        v.setDirty()

        # Keep the headline editor from restoring stale text at the next redraw.
        if head_changed:
            for p in c.vnode2allPositions(v):
                c.frame.tree.setHeadline(p, head)

    # @+node:ekr.20261015041620.5: *6* u.restore_ui
    def restore_ui(self, state: tuple) -> None:
        c = self.c
        p, sel, ins, scroll = state
        c.p = p
        c.selectPosition(p)
        c.frame.scanForTabWidth(c.p)
        c.recolor(c.p)
        w = c.frame.body.wrapper
        w.setSelectionRange(*sel, insert=ins)
        w.setYScrollPosition(scroll)

    # @+node:ekr.20261015041852.1: *4* u: redrawers & finishers
    # @+node:ekr.20261025152930.1: *5* u._redraw
    def _redraw(self, p: Position) -> None:
        """Redraw now and choose the command's single undo/redo redraw."""
        u = self
        c = u.c
        w = c.frame.body.wrapper
        # Ignore redrawers in inner levels.
        if u.undoBeadLevel > 1:
            return
        p.setDirty()  # Call p.v.setAllAncestorAtFileNodesDirty()
        preserve_body = p == c.p and p.b == w.getAllText()
        if preserve_body:
            sel, ins, scroll = w.getSelectionRange(), w.getInsertPoint(), w.getYScrollPosition()
        c.updateSyntaxColorer(p)
        c.recolor()
        c.redraw(p)
        if preserve_body:
            w.setSelectionRange(*sel, insert=ins)
            w.setYScrollPosition(scroll)

    # @+node:ekr.20261011193020.1: *5* u.redraw_after_head_changed
    def redraw_after_head_changed(self) -> None:
        """Refresh headlines now and after undo/redo."""
        u = self
        u._require_bead()
        c = u.c
        # Ignore redrawers in inner levels.
        if u.undoBeadLevel > 1:
            return
        if not c.changed:
            c.setChanged()
        c.p.setDirty()  # p.setDirty() calls p.v.setAllAncestorAtFileNodesDirty()
        c.redraw_after_head_changed()
        u.undoBead.add_redraw_after_head_changed()

    # @+node:ekr.20261011190258.1: *5* u.redraw_and_edit
    def redraw_and_edit(self, new_p: Position) -> None:
        """Redraw and edit now and after undo/redo."""
        u = self
        c = u.c
        u._require_bead()
        # Ignore redrawers in inner levels.
        if u.undoBeadLevel > 1:
            return
        if not c.changed:
            c.setChanged()
        c.p.setDirty()  # p.setDirty() calls p.v.setAllAncestorAtFileNodesDirty()
        c.redrawAndEdit(new_p, selectAll=True)
        u.undoBead.add_redraw_and_edit(new_p, self.undoBead.old_p)

    # @+node:ekr.20050416092908.1: *3* u: Helpers
    # @+node:ekr.20261005094529.1: *4* u.__enter__ and __exit__
    def __enter__(self) -> Self:
        """Compose nested operations into one bead, published on outermost exit."""
        if self.undoBeadLevel == 0:
            self.undoBead = UndoBead(self)
        self.undoBeadLevel += 1
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        b = self.undoBead
        self.undoBeadLevel -= 1
        if self.undoBeadLevel:
            return
        self.undoBead = None
        if b.undo_functions and not (self.undoing or self.redoing):
            if not b.command_name:
                raise AssertionError("Missing call to u.set_command_name")
            # Record partial mutations even if the command raised an exception.
            self.pushBead(b)

    # @+node:ekr.20261102022551.1: *4* u._can_merge
    def _can_merge(
        self,
        *,
        oldSel: tuple[int, int],
        oldText: str,
        newSel: tuple[int, int],
        newText: str,
    ) -> bool:
        """
        Return True if we should merge changes into the previous UndoTyping node.
        """
        u = self
        bead = u.peekBead(u.bead)
        assert bead is None or isinstance(bead, UndoBead), repr(bead)
        c = u.c
        p = c.p
        if (
            ### u.granularity == 'char'
            not isinstance(bead, TypingBead)  # Intervening command.
            or u.bead != len(u.beads) - 1     # Previous undo.
            or bead.p.v != p.v                # Changed node.
            or not c.changed                  # ???
        ):  # fmt: skip
            ### print('Fail 1')
            return False
        # All lines *except* the current line must match.
        leading, trailing, _, _ = TypingBead.split_patch(oldText, newText)
        if (leading, trailing) != (bead.leading, bead.trailing):
            ### print('Fail 2')
            return False

        ###
        # if u.granularity == 'line':
        #   return True

        # The hard case: u.granularity == 'word'

        # The selection ranges must match.
        if oldSel is None or newSel is None or bead.new_sel is None:
            # print(f"Fail 3 {oldSel=} {newSel=} {bead.new_sel=}")
            return False
        old_start, old_end = oldSel
        new_start, new_end = newSel
        if old_start != old_end or new_start != new_end:
            # print('Fail 4')
            return False

        # The position of the lines must match.
        old_row, old_col = g.convertPythonIndexToRowCol(oldText, old_start)
        new_row, new_col = g.convertPythonIndexToRowCol(newText, new_start)
        prev_row, prev_col = g.convertPythonIndexToRowCol(oldText, bead.new_sel[0])
        if (
            old_col == 0
            or new_col == 0
            or old_row != new_row
            or abs(new_col - prev_col) != 1
        ):  # fmt: skip
            # print(f"Fail 5 {old_col=} {new_col=} {prev_col=}")
            return False
        old_ch = oldText[old_start - 1]
        new_ch = newText[new_start - 1]
        # We must not be starting a new word.

        can_merge = not (not old_ch.isspace() and new_ch.isspace())
        # if not g.unitTesting:
        #     g.trace(f"{can_merge=}")
        return can_merge

    # @+node:vivainio.202610110004.1: *4* u._require_bead
    def _require_bead(self) -> UndoBead:
        """Reject helper calls outside a context before any mutation occurs."""
        assert isinstance(self.undoBead, UndoBead), "Undo helper requires 'with c.undoer'"
        return self.undoBead

    # @+node:ekr.20060127052111.1: *4* u.cutStack
    def cutStack(self) -> None:
        u = self
        n = u.max_undo_stack_size
        if u.bead >= n > 0:
            # This work regardless of how many items appear after bead n.
            u.beads = u.beads[-n:]
            u.bead = n - 1

    # @+node:EKR.20040526150818: *4* u.getBead
    def getBead(self, n: int) -> UndoBead | None:
        """Set Undoer ivars from the bead at the top of the undo stack."""
        u = self
        if n < 0 or n >= len(u.beads):
            return None
        return u.beads[n]

    # @+node:EKR.20040526150818.1: *4* u.peekBead
    def peekBead(self, n: int) -> UndoBead | None:
        u = self
        if n < 0 or n >= len(u.beads):
            return None
        return u.beads[n]

    # @+node:ekr.20060127113243: *4* u.pushBead
    def pushBead(self, bead: UndoBead | None) -> None:
        u = self
        u.bead += 1
        u.beads[u.bead :] = [bead]
        u.setUndoTypes()

    # @+node:ekr.20031218072017.3613: *4* u.redoMenuName, undoMenuName
    def redoMenuName(self, name: str) -> str:
        if name.startswith("Can't Redo"):
            return name
        return "Redo " + name

    def undoMenuName(self, name: str) -> str:
        if name.startswith("Can't Undo"):
            return name
        return "Undo " + name

    # @+node:ekr.20031218072017.3614: *4* u.setRedoType
    # These routines update both the ivar and the menu label.

    def setRedoType(self, theType: str) -> None:
        u = self
        frame = u.c.frame
        if not isinstance(theType, str):  # pragma: no cover
            g.trace(f"oops: expected string for command, got {theType!r}")
            g.trace(g.callers())
            theType = '<unknown>'
        menu = frame.menu.getMenu("Edit")
        name = u.redoMenuName(theType)
        if name != u.redoMenuLabel:
            # Update menu using old name.
            realLabel = frame.menu.getRealMenuName(name)
            if realLabel == name:
                underline = -1 if g.match(name, 0, "Can't") else 0
            else:
                underline = realLabel.find("&")
            realLabel = realLabel.replace("&", "")
            frame.menu.setMenuLabel(menu, u.realRedoMenuLabel, realLabel, underline=underline)
            u.redoMenuLabel = name
            u.realRedoMenuLabel = realLabel

    # @+node:ekr.20091221145433.6381: *4* u.setUndoType
    def setUndoType(self, theType: str) -> None:
        u = self
        frame = u.c.frame
        if not isinstance(theType, str):
            g.trace(f"oops: expected string for command, got {repr(theType)}")
            g.trace(g.callers())
            theType = '<unknown>'
        menu = frame.menu.getMenu("Edit")
        name = u.undoMenuName(theType)
        if name != u.undoMenuLabel:
            # Update menu using old name.
            realLabel = frame.menu.getRealMenuName(name)
            if realLabel == name:
                underline = -1 if g.match(name, 0, "Can't") else 0
            else:
                underline = realLabel.find("&")
            realLabel = realLabel.replace("&", "")
            frame.menu.setMenuLabel(menu, u.realUndoMenuLabel, realLabel, underline=underline)
            u.undoType = theType
            u.undoMenuLabel = name
            u.realUndoMenuLabel = realLabel

    # @+node:ekr.20031218072017.3616: *4* u.setUndoTypes
    def setUndoTypes(self) -> None:
        u = self
        # Set the undo type and undo menu label.
        if bead := u.peekBead(u.bead):
            u.setUndoType(bead.undoType)
        else:
            u.setUndoType("Can't Undo")
        # Set only the redo menu label.
        if bead := u.peekBead(u.bead + 1):
            u.setRedoType(bead.undoType)
        else:
            u.setRedoType("Can't Redo")
        u.cutStack()

    # @-others


# @-others
# @@language python
# @@tabwidth -4
# @@pagewidth 70
# @-leo
