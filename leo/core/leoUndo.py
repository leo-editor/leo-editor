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
import warnings
from typing import cast, Any, Self, TYPE_CHECKING
from leo.core import leoGlobals as g
from leo.core.leoFileCommands import FastRead
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
    # @+node:ekr.20261014100558.1: *3* TypingBead.__init__
    def __init__(self, undoer, p, old_text, new_text, old_sel, new_sel, new_ins, scroll):
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

    # @+node:ekr.20261014100625.7: *3* TypingBead.get
    def get(self, key, default=None):
        # Legacy doTyping must not try to extend a new-style typing bead.
        if key == 'kind':
            return 'new-typing'
        return super().get(key) or default

    # @-others


# @+node:ekr.20031218072017.3605: ** class Undoer
class Undoer:
    """A class that implements unlimited undo and redo."""

    # @+others
    # @+node:ekr.20031218072017.3606: *3* u.__init__
    def __init__(self, c: Cmdr) -> None:
        self.c = c
        self.p = cast(Position, None)  # The position/node being operated upon for undo and redo.
        self.granularity = None  # Set in reloadSettings.
        self.max_undo_stack_size = c.config.getInt('max-undo-stack-size') or 0
        # State ivars...
        self.beads = []  # List of undo nodes.
        self.bead = -1  # Index of the present bead: -1:len(beads)
        self.inHead = False
        self.capture_level = 0
        self.node_captures = set()
        self.undoBeadLevel = 0  # PR #4996
        self.undoBead = None  # PR #4994
        self.undoType = "Can't Undo"
        # These must be set here, _not_ in clearUndoState.
        self.last_undoable_command_name = None  # Name of last undoable command.
        self.redoMenuLabel = "Can't Redo"
        self.undoMenuLabel = "Can't Undo"
        self.realRedoMenuLabel = "Can't Redo"
        self.realUndoMenuLabel = "Can't Undo"
        self.undoing = False  # True if executing an Undo command.
        self.redoing = False  # True if executing a Redo command.
        self.per_node_undo = False  # True: v may contain undo_info ivar.
        # New in 4.2...
        self.optionalIvars = []
        # Update settings.
        self.reloadSettings()

    # @+node:ekr.20191213085126.1: *3* u.reloadSettings
    def reloadSettings(self) -> None:
        """Undoer.reloadSettings."""
        c = self.c
        self.granularity = c.config.getString('undo-granularity')
        if self.granularity:
            self.granularity = self.granularity.lower()
        if self.granularity not in ('node', 'line', 'word', 'char'):
            self.granularity = 'line'

    # @+node:ekr.20031218072017.2030: *3* u.redo
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
            # WRONG: Leo *must* support both old and new beads "forever"!
            ### assert isinstance(obj, UndoBead), g.callers()
            if isinstance(obj, UndoBead):
                obj.redo()
            elif u.redoHelper:
                g.print_unique_message(f"\nOops: using g.Bunch: {g.callers()=}")
                u.redoHelper()
            else:
                g.trace(f"no redo helper for {u.kind} {u.undoType}")
            c.checkOutline()
        finally:
            u.redoing = False
        u.bead += 1
        u.setUndoTypes()

    # @+node:ekr.20031218072017.2039: *3* u.undo
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
            ### assert isinstance(obj, UndoBead), g.callers()
            # WRONG: Leo *must* support both old and new beads "forever"!
            if isinstance(obj, UndoBead):
                obj.undo()
            elif u.undoHelper:
                g.print_unique_message(f"\nOops: using g.Bunch: {g.callers()=}")
                if u.per_node_undo:
                    u.setIvarsFromVnode(c.p)
                u.undoHelper()
            else:
                g.trace(f"no undo helper for {u.kind} {u.undoType}")
            c.checkOutline()
        finally:
            u.undoing = False
        u.bead -= 1
        u.setUndoTypes()

    # @+node:ekr.20031218072017.3608: *3* u: Externally visible entries
    # @+node:ekr.20050318085432.2: *4* u.createCommonBunch
    def createCommonBunch(self, p: Position) -> g.Bunch:
        """
        Return a bunch containing all common undo info.

        This method is *not* deprecated.
        """
        c = self.c
        w = c.frame.body.wrapper
        return g.Bunch(
            oldMarked=p and p.isMarked(),
            oldSel=w.getSelectionRange() if w else None,
            p=p.copy() if p else None,
        )

    # @+node:ekr.20261018092627.1: *4* u: Legacy entries
    # @+node:ekr.20031218072017.3610: *5* u.canRedo & canUndo
    # Translation does not affect these routines.

    def canRedo(self) -> bool:
        u = self
        return u.redoMenuLabel != "Can't Redo"

    def canUndo(self) -> bool:
        u = self
        return u.undoMenuLabel != "Can't Undo"

    # @+node:ekr.20230714012821.1: *5* u.clearAndWarn
    def clearAndWarn(self, command_name: str) -> None:
        """
        Clear all undo state and issue a warning.

        All non-undoable commands should call this method.
        """
        u = self
        u.last_undoable_command_name = command_name
        u.clearUndoState()

    # @+node:ekr.20031218072017.3609: *5* u.clearUndoState
    def clearUndoState(self) -> None:
        """Clears the entire Undo state."""
        u = self
        u.clearOptionalIvars()  # Do this first.
        u.setRedoType("Can't Redo")
        if u.last_undoable_command_name:
            undoType = f"Can't Undo {u.last_undoable_command_name}"
        else:
            undoType = "Can't Undo"
        u.setUndoType(undoType)
        u.beads = []  # List of undo nodes.
        u.bead = -1  # Index of the present bead: -1:len(beads)

    # @+node:ekr.20031218072017.1490: *5* u.doTyping & helper (keep???)
    def doTyping(
        self,
        p: Position,
        undo_type: str,
        oldText: str,
        newText: str,
        newInsert: int | None = None,
        oldSel: tuple[int, int] | None = None,
        newSel: tuple[int, int] | None = None,
        oldYview: int | None = None,
    ) -> None:
        """
        Save enough information to undo or redo a typing operation efficiently,
        that is, with the proper granularity.

        Do nothing when called from the undo/redo logic because the Undo
        and Redo commands merely reset the bead pointer.

        **Important**: Code should call this method *only* when the user has
        actually typed something. Commands should use u.beforeChangeBody and
        u.afterChangeBody.
        """
        u = self
        c = u.c
        w = c.frame.body.wrapper
        # Leo 6.4: undo_type must be 'Typing'.
        undo_type = undo_type.capitalize()
        assert undo_type == 'Typing', (repr(undo_type), g.callers())
        # @+<< return if there is nothing to do >>
        # @+node:ekr.20040324061854: *6* << return if there is nothing to do >>
        if u.redoing or u.undoing:
            return  # pragma: no cover
        if undo_type is None:
            return  # pragma: no cover
        if undo_type == "Can't Undo":
            u.clearUndoState()
            u.setUndoTypes()  # Must still recalculate the menu labels.
            return  # pragma: no cover
        if oldText == newText:
            u.setUndoTypes()  # Must still recalculate the menu labels.
            return  # pragma: no cover
        # @-<< return if there is nothing to do >>
        # @+<< init the undo params >>
        # @+node:ekr.20040324061854.1: *6* << init the undo params >>
        u.clearOptionalIvars()
        # Set the params.
        u.undoType = undo_type
        u.p = p.copy()
        # @-<< init the undo params >>
        # @+<< compute leading, middle & trailing  lines >>
        # @+node:ekr.20031218072017.1491: *6* << compute leading, middle & trailing  lines >>
        # @+at Incremental undo typing is similar to incremental syntax coloring. We compute
        # the number of leading and trailing lines that match, and save both the old and
        # new middle lines. NB: the number of old and new middle lines may be different.
        # @@c
        old_lines = oldText.split('\n')
        new_lines = newText.split('\n')
        new_len = len(new_lines)
        old_len = len(old_lines)
        min_len = min(old_len, new_len)
        i = 0
        while i < min_len:
            if old_lines[i] != new_lines[i]:
                break
            i += 1
        leading = i
        if leading == new_len:
            # This happens when we remove lines from the end.
            # The new text is simply the leading lines from the old text.
            trailing = 0
        else:
            i = 0
            while i < min_len - leading:
                if old_lines[old_len - i - 1] != new_lines[new_len - i - 1]:
                    break
                i += 1
            trailing = i
        # NB: the number of old and new middle lines may be different.
        if trailing == 0:
            old_middle_lines = old_lines[leading:]
            new_middle_lines = new_lines[leading:]
        else:
            old_middle_lines = old_lines[leading:-trailing]
            new_middle_lines = new_lines[leading:-trailing]
        # Remember how many trailing newlines in the old and new text.
        i = len(oldText) - 1
        old_newlines = 0
        while i >= 0 and oldText[i] == '\n':
            old_newlines += 1
            i -= 1
        i = len(newText) - 1
        new_newlines = 0
        while i >= 0 and newText[i] == '\n':
            new_newlines += 1
            i -= 1
        # @-<< compute leading, middle & trailing  lines >>
        # @+<< save undo text info >>
        # @+node:ekr.20031218072017.1492: *6* << save undo text info >>
        u.oldText = None
        u.newText = None
        u.leading = leading
        u.trailing = trailing
        u.oldMiddleLines = old_middle_lines
        u.newMiddleLines = new_middle_lines
        u.oldNewlines = old_newlines
        u.newNewlines = new_newlines
        # @-<< save undo text info >>
        # @+<< save the selection and scrolling position >>
        # @+node:ekr.20040324061854.2: *6* << save the selection and scrolling position >>
        # Remember the selection.
        u.oldSel = oldSel
        u.newSel = newSel
        # Remember the scrolling position.
        if oldYview:
            u.yview = oldYview
        else:
            u.yview = c.frame.body.wrapper.getYScrollPosition()
        # @-<< save the selection and scrolling position >>
        # @+<< adjust the undo stack, clearing all forward entries >>
        # @+node:ekr.20040324061854.3: *6* << adjust the undo stack, clearing all forward entries >>
        # @+at
        # New in Leo 4.3. Instead of creating a new bead on every character, we
        # may adjust the top bead:
        # word granularity: adjust the top bead if the typing would continue the word.
        # line granularity: adjust the top bead if the typing is on the same line.
        # node granularity: adjust the top bead if the typing is anywhere on the same node.
        # @@c
        granularity = u.granularity
        old_d = u.peekBead(u.bead)
        old_p = old_d and old_d.get('p')
        # @+<< set newBead if we can't share the previous bead >>
        # @+node:ekr.20050125220613: *7* << set newBead if we can't share the previous bead >>
        # Set newBead to True if undo_type is not 'Typing' so that commands that
        # get treated like typing don't get lumped with 'real' typing.
        if (
            not old_d
            or not old_p
            or old_p.v != p.v
            or old_d.get('kind') != 'typing'
            or old_d.get('undoType') != 'Typing'
            or undo_type != 'Typing'
        ):
            newBead = True  # We can't share the previous node.
        elif granularity == 'char':
            newBead = True  # This was the old way.
        elif granularity == 'node':
            newBead = False  # Always replace previous bead.
        else:
            assert granularity in ('line', 'word')
            # Replace the previous bead if only the middle lines have changed.
            newBead = old_d.get('leading', 0) != u.leading or old_d.get('trailing', 0) != u.trailing
            if granularity == 'word' and not newBead:
                # Protect the method that may be changed by the user
                try:
                    # @+<< set newBead if the change does not continue a word >>
                    # @+node:ekr.20050125203937: *8* << set newBead if the change does not continue a word >>
                    # Fix #653: undoer problem: be wary of the ternary operator here.
                    old_start = old_end = new_start = new_end = 0
                    if oldSel is not None:
                        old_start, old_end = oldSel
                    if newSel is not None:
                        new_start, new_end = newSel
                    if u.prevSel is None:
                        prev_start, prev_end = 0, 0
                    else:
                        prev_start, prev_end = u.prevSel
                    if old_start != old_end or new_start != new_end:
                        # The new and old characters are not contiguous.
                        newBead = True
                    else:
                        # 2011/04/01: Patch by Sam Hartsfield
                        old_row, old_col = g.convertPythonIndexToRowCol(oldText, old_start)
                        new_row, new_col = g.convertPythonIndexToRowCol(newText, new_start)
                        prev_row, prev_col = g.convertPythonIndexToRowCol(oldText, prev_start)
                        old_lines = g.splitLines(oldText)
                        new_lines = g.splitLines(newText)
                        # Recognize backspace, del, etc. as contiguous.
                        if old_row != new_row or abs(old_col - new_col) != 1:
                            # The new and old characters are not contiguous.
                            newBead = True
                        elif old_col == 0 or new_col == 0:
                            # py-lint: disable=W0511
                            # W0511:1362: TODO
                            # TODO this is not true, we might as well just have entered a
                            # char at the beginning of an existing line
                            pass  # We have just inserted a line.
                        else:
                            # 2011/04/01: Patch by Sam Hartsfield
                            old_s = old_lines[old_row]
                            new_s = new_lines[new_row]
                            # New in 4.3b2:
                            # Guard against invalid oldSel or newSel params.
                            if old_col - 1 >= len(old_s) or new_col - 1 >= len(new_s):
                                newBead = True
                            else:
                                old_ch = old_s[old_col - 1]
                                new_ch = new_s[new_col - 1]
                                newBead = self.recognizeStartOfTypingWord(
                                    old_lines,
                                    old_row,
                                    old_col,
                                    old_ch,
                                    new_lines,
                                    new_row,
                                    new_col,
                                    new_ch,
                                    prev_row,
                                    prev_col,
                                )
                    # @-<< set newBead if the change does not continue a word >>
                except Exception:
                    g.error('Unexpected exception...')
                    g.es_exception()
                    newBead = True
        # @-<< set newBead if we can't share the previous bead >>
        # Save end selection as new "previous" selection
        u.prevSel = u.newSel
        if newBead:
            # Push params on undo stack, clearing all forward entries.
            bunch = g.Bunch(
                p=p.copy(),
                kind='typing',  # lowercase.
                undoType=undo_type,  # capitalized.
                undoHelper=u.undoTyping,
                redoHelper=u.redoTyping,
                oldMarked=old_p.isMarked() if old_p else p.isMarked(),  # #1694
                oldText=u.oldText,
                oldSel=u.oldSel,
                oldNewlines=u.oldNewlines,
                oldMiddleLines=u.oldMiddleLines,
            )
            u.pushBead(bunch)
        else:
            bunch = old_d
        bunch.leading = u.leading  # type:ignore
        bunch.trailing = u.trailing  # type:ignore
        bunch.newMarked = p.isMarked()  # type:ignore # #1694
        bunch.newNewlines = u.newNewlines  # type:ignore
        bunch.newMiddleLines = u.newMiddleLines  # type:ignore
        bunch.newSel = u.newSel  # type:ignore
        bunch.newText = u.newText  # type:ignore
        bunch.yview = u.yview  # type:ignore
        # @-<< adjust the undo stack, clearing all forward entries >>
        if 'undo' in g.app.debug and 'verbose' in g.app.debug:
            print(f"u.doTyping: {len(oldText)} => {len(newText)}")
        if u.per_node_undo:
            u.putIvarsToVnode(p)

        # Finish updating the text.
        p.v.setBodyString(newText)
        u.updateAfterTyping(p, w)

    # Compatibility

    setUndoTypingParams = doTyping

    # @+node:ekr.20050126081529: *6* u.recognizeStartOfTypingWord
    def recognizeStartOfTypingWord(
        self,
        old_lines: list[str],
        old_row: int,
        old_col: int,
        old_ch: str,
        new_lines: list[str],
        new_row: int,
        new_col: int,
        new_ch: str,
        prev_row: int,
        prev_col: int,
    ) -> bool:
        """
        A potentially user-modifiable method that should return True if the
        typing indicated by the params starts a new 'word' for the purposes of
        undo with 'word' granularity.

        u.doTyping calls this method only when the typing could possibly
        continue a previous word. In other words, undo will work safely regardless
        of the value returned here.

        old_ch is the char at the given (Tk) row, col of old_lines.
        new_ch is the char at the given (Tk) row, col of new_lines.

        The present code uses only old_ch and new_ch. The other arguments are given
        for use by more sophisticated algorithms.
        """
        # Start a word if new_ch begins whitespace + word
        new_word_started = not old_ch.isspace() and new_ch.isspace()
        # Start a word if the cursor has been moved since the last change
        moved_cursor = new_row != prev_row or new_col != prev_col + 1
        return new_word_started or moved_cursor

    # @+node:ekr.20261008093043.1: *5* u.dump_stack
    def dump_stack(self, message: str = '') -> None:
        u = self
        print()
        print(f"Dump of undo stack: {g.caller()} {message}")
        for i, obj in enumerate(u.beads):
            s = obj.kind if isinstance(obj, g.Bunch) else repr(obj)
            prefix = '**' if i == u.bead else '  '
            print(f"{prefix} {i:} {obj.__class__.__name__} {s}")

    # @+node:ekr.20031218072017.3611: *5* u.enableMenuItems
    def enableMenuItems(self) -> None:
        u = self
        frame = u.c.frame
        if menu := frame.menu.getMenu("Edit"):
            frame.menu.enableMenu(menu, u.redoMenuLabel, u.canRedo())
            frame.menu.enableMenu(menu, u.undoMenuLabel, u.canUndo())

    # @+node:ekr.20110519074734.6094: *5* u.onSelect & helpers
    def onSelect(self, old_p: Position, p: Position) -> None:
        u = self
        if u.per_node_undo and not (u.undoing or u.redoing):
            if old_p and u.beads:
                u.putIvarsToVnode(old_p)
            u.setIvarsFromVnode(p)
            u.setUndoTypes()

    # @+node:ekr.20110519074734.6096: *6* u.putIvarsToVnode
    def putIvarsToVnode(self, p: Position) -> None:
        u, v = self, p.v
        assert self.per_node_undo
        bunch = g.bunch()
        for key in self.optionalIvars:
            bunch[key] = getattr(u, key)
        # Put these ivars by hand.
        for key in ('bead', 'beads', 'undoType'):
            bunch[key] = getattr(u, key)
        v.undo_info = bunch

    # @+node:ekr.20110519074734.6095: *6* u.setIvarsFromVnode
    def setIvarsFromVnode(self, p: Position) -> None:
        u = self
        v = p.v
        assert self.per_node_undo
        u.clearUndoState()
        if hasattr(v, 'undo_info'):
            u.setIvarsFromBunch(v.undo_info)  # type:ignore

    # @+node:EKR.20040526075238.5: *5* u.redoTyping (keep???)
    def redoTyping(self) -> None:
        u = self
        c = u.c
        current = c.p
        w = c.frame.body.wrapper
        # selectPosition causes recoloring, so avoid if possible.
        if current != u.p:
            c.selectPosition(u.p)
        u.p.setDirty()
        self.undoRedoText(
            u.p,
            u.leading,
            u.trailing,
            u.newMiddleLines,
            u.oldMiddleLines,
            u.newNewlines,
            u.oldNewlines,
            tag="redo",
            undoType=u.undoType,
        )
        u.updateMarks('new')
        if u.newSel:
            c.bodyWantsFocus()
            i, j = u.newSel
            w.setSelectionRange(i, j, insert=j)
        if u.yview:
            c.bodyWantsFocus()
            w.setYScrollPosition(u.yview)

    # @+node:ekr.20230722062645.1: *5* u.restoreFromCopiedTree
    def restoreFromCopiedTree(self, v: VNode, s: str) -> None:
        # @+<< docstring: restoreFromCopiedTree >>
        # @+node:ekr.20230722062838.1: *6* << docstring: restoreFromCopiedTree >>
        """
        c.restoreFromCopiedTree: restore v from a copied tree.

        This is a low-level method. See u.undo/redoChangeTree for examples.

        The caller is responsible for:

        - Calling c.endEditing.
        - Setting c.p correctly.
        - Updating selection range and y-scroll position in c.frame.body.wrapper.
        - Calling c.redraw.
        """
        # @-<< docstring: restoreFromCopiedTree >>
        u = self
        c = u.c
        fc = c.fileCommands
        if not isinstance(v, VNode):
            g.trace("Can't happen: not a vnode: {v!r}")
            return
        old_parents = v.parents[:]  # Essential.

        # This encoding must match the encoding used in outline_to_clipboard_string.
        encoding = fc.leo_file_encoding

        # Create a tree of vnodes from s.
        x = FastRead(c, fc.gnxDict)  # Must use fc.gnxDict.
        fc.initReadIvars()
        s_bytes = g.toEncodedString(s, encoding, reportErrors=True)
        hidden_v = x.readFileFromClipboard(s_bytes)
        fc.initReadIvars()
        if not hidden_v:
            u.clearAndWarn('undo-change-tree')
            return

        # The big switcharoo: change v in place.
        new_v = hidden_v.children[0]
        new_v.parents = old_parents  # restore v.parents.
        assert v.gnx == new_v.gnx
        v = new_v

        # All pasted nodes should have unique gnx's.
        ni = g.app.nodeIndices
        for v in c.all_unique_nodes():
            ni.check_gnx(c, v.fileIndex, v)

    # @+node:vivainio.202610110002.2: *5* u.type_text (legacy: revise!!!)
    def type_text(
        self,
        p: Position,
        undo_type: str,
        oldText: str,
        newText: str,
        newInsert: int | None = None,
        oldSel: tuple[int, int] | None = None,
        newSel: tuple[int, int] | None = None,
        oldYview: int | None = None,
    ) -> None:
        """Record actual typing, retaining the configured char/line/word/node granularity."""
        if self.undoing or self.redoing or oldText == newText:
            return
        assert undo_type.capitalize() == 'Typing', undo_type
        u = self
        c = u.c
        w = c.frame.body.wrapper
        newSel = newSel if newSel is not None else w.getSelectionRange()
        newInsert = newInsert if newInsert is not None else w.getInsertPoint()
        scroll = oldYview if oldYview is not None else w.getYScrollPosition()
        bead = u.peekBead(u.bead)
        # A save, intervening command, selection change, or undo ends coalescing.
        merge = (
            isinstance(bead, TypingBead)
            and u.bead == len(u.beads) - 1
            and bead.p.v == p.v
            and c.changed
            and u.granularity != 'char'
        )
        if merge and u.granularity in ('line', 'word'):
            leading, trailing, _, _ = TypingBead.split_patch(oldText, newText)
            merge = (leading, trailing) == (bead.leading, bead.trailing)
            if merge and u.granularity == 'word':
                merge = oldSel is not None and newSel is not None and bead.new_sel is not None
                if merge:
                    old_start, old_end = oldSel
                    new_start, new_end = newSel
                    merge = old_start == old_end and new_start == new_end
                    if merge:
                        old_row, old_col = g.convertPythonIndexToRowCol(oldText, old_start)
                        new_row, new_col = g.convertPythonIndexToRowCol(newText, new_start)
                        prev_row, prev_col = g.convertPythonIndexToRowCol(oldText, bead.new_sel[0])
                        merge = old_row == new_row and abs(old_col - new_col) == 1
                        if merge and old_col and new_col:
                            merge = not u.recognizeStartOfTypingWord(
                                g.splitLines(oldText),
                                old_row,
                                old_col,
                                oldText[old_start - 1],
                                g.splitLines(newText),
                                new_row,
                                new_col,
                                newText[new_start - 1],
                                prev_row,
                                prev_col,
                            )
        if u.undoBead is not None:
            # Typing within an explicit command belongs to that command's bead.
            u.set_body(p, newText, old_body=oldText)
            return
        if merge:
            original = bead.replace_middle(oldText, bead.old_lines)
            bead.update_patch(original, newText)
            bead.new_sel, bead.new_ins = newSel, newInsert  # type:ignore
        else:
            bead = TypingBead(u, p, oldText, newText, oldSel, newSel, newInsert, scroll)
            u.pushBead(bead)
        p.b = newText
        u.updateAfterTyping(p, w)
        if u.per_node_undo:
            u.putIvarsToVnode(p)

    # @+node:ekr.20031218072017.1493: *5* u.undoRedoText (keep???)
    def undoRedoText(
        self,
        p: Position,
        leading: int,
        trailing: int,  # Number of matching leading & trailing lines.
        oldMidLines: list[str],
        newMidLines: list[str],  # Lists of unmatched lines.
        oldNewlines: int,
        newNewlines: int,
        tag: str = "undo",  # "undo" or "redo"
        undoType: str | None = None,
    ) -> None:
        """Handle text undo and redo: converts _new_ text into _old_ text."""
        # newNewlines is unused, but it has symmetry.
        u = self
        c = u.c
        w = c.frame.body.wrapper
        # @+<< Compute the result using p's body text >>
        # @+node:ekr.20061106105812.1: *6* << Compute the result using p's body text >>
        # Recreate the text using the present body text.
        body = p.b
        body = g.checkUnicode(body)
        body_lines = body.split('\n')
        aList = []
        if leading > 0:
            aList.extend(body_lines[:leading])
        if oldMidLines:
            aList.extend(oldMidLines)
        if trailing > 0:
            aList.extend(body_lines[-trailing:])
        s = '\n'.join(aList)
        # Remove trailing newlines in s.
        while s and s[-1] == '\n':
            s = s[:-1]
        # Add oldNewlines newlines.
        if oldNewlines > 0:
            s = s + '\n' * oldNewlines
        result = s
        # @-<< Compute the result using p's body text >>
        p.setBodyString(result)
        p.setDirty()
        w.setAllText(result)
        if sel := u.oldSel if tag == 'undo' else u.newSel:
            i, j = sel
            w.setSelectionRange(i, j, insert=j)
        c.recolor(u.p)
        w.seeInsertPoint()  # 2009/12/21

    # @+node:EKR.20040526090701.4: *5* u.undoTyping (keep???)
    def undoTyping(self) -> None:
        u = self
        c = u.c
        w = c.frame.body.wrapper
        # selectPosition causes recoloring, so don't do this unless needed.
        if c.p != u.p:
            c.selectPosition(u.p)
        u.p.setDirty()
        u.undoRedoText(
            u.p,
            u.leading,
            u.trailing,
            u.oldMiddleLines,
            u.newMiddleLines,
            u.oldNewlines,
            u.newNewlines,
            tag="undo",
            undoType=u.undoType,
        )
        u.updateMarks('old')
        if u.oldSel:
            c.bodyWantsFocus()
            i, j = u.oldSel
            w.setSelectionRange(i, j, insert=j)
        if u.yview:
            c.bodyWantsFocus()
            w.setYScrollPosition(u.yview)

    # @+node:ekr.20201127035748.1: *5* u.updateAfterTyping
    def updateAfterTyping(self, p: Position, w: QTextMixin) -> None:
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

    # @+node:ekr.20261005135125.1: *4* u: New entries
    # @+node:ekr.20261005094529.1: *5* u.__enter__ and __exit__
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

    # @+node:vivainio.202610110004.1: *5* u._require_bead
    def _require_bead(self) -> UndoBead:
        """Reject helper calls outside a context before any mutation occurs."""
        assert isinstance(self.undoBead, UndoBead), "Undo helper requires 'with c.undoer'"
        return self.undoBead

    # @+node:ekr.20261015042013.1: *5* u: actions
    # @+node:ekr.20261006155509.1: *6* u.clone_node
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

    # @+node:ekr.20261005143707.1: *6* u.delete_node
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

    # @+node:ekr.20261006155622.1: *6* u.insert_node
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

    # @+node:ekr.20261005140833.1: *6* u.set_body (to be deleted)
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

    # @+node:ekr.20261005094529.2: *6* u.set_command_name
    def set_command_name(self, command_name: str) -> None:
        u = self
        b = u._require_bead()
        assert isinstance(b, UndoBead), repr(b)
        if u.undoBeadLevel == 1:
            b.command_name = command_name
            b.undoType = command_name
            # Menu labels are updated when the completed bead is pushed.

    # @+node:ekr.20261015042249.1: *5* u: contexts
    # @+node:ekr.20261009185938.1: *6* u.change_headline
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

    # @+node:vivainio.202610110001.1: *6* u.change_node
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

    # @+node:vivainio.202610110001.2: *6* u.change_outline & helpers
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

    # @+node:ekr.20261015041620.2: *7* u.capture_outline
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

    # @+node:ekr.20261015041620.3: *7* u.restore_outline
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

    # @+node:vivainio.202610110001.4: *6* u.change_recent_files
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

    # @+node:vivainio.202610110003.1: *6* u.move_node
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

    # @+node:ekr.20261018041400.1: *6* u:common context helpers
    # @+node:vivainio.202610110001.3: *7* u.capture_node
    def capture_node(self, v: VNode) -> tuple:
        """
        Record everything needed by u.restore_node.
        """
        return v.h, v.b, v.isMarked(), deepcopy(v.u)

    # @+node:ekr.20261015041620.4: *7* u.capture_ui
    def capture_ui(self) -> tuple:
        c = self.c
        w = c.frame.body.wrapper
        return c.p.copy(), w.getSelectionRange(), w.getInsertPoint(), w.getYScrollPosition()

    # @+node:ekr.20261015041620.1: *7* u.restore_node
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

    # @+node:ekr.20261015041620.5: *7* u.restore_ui
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

    # @+node:ekr.20261015041852.1: *5* u: redrawers & finishers
    # @+node:ekr.20261025152930.1: *6* u._redraw
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

    # @+node:ekr.20261011193020.1: *6* u.redraw_after_head_changed
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

    # @+node:ekr.20261011190258.1: *6* u.redraw_and_edit
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

    # @+node:ekr.20050416092908.1: *3* u: Internal helpers
    # @+node:ekr.20031218072017.3607: *4* u.clearOptionalIvars
    def clearOptionalIvars(self) -> None:
        u = self
        u.p = None  # type:ignore
        for ivar in u.optionalIvars:
            setattr(u, ivar, None)

    # @+node:ekr.20060127052111.1: *4* u.cutStack
    def cutStack(self) -> None:
        u = self
        n = u.max_undo_stack_size
        if u.bead >= n > 0 and not g.unitTesting:
            # Do nothing if we are in the middle of creating a group.
            i = len(u.beads) - 1
            while i >= 0:
                bunch = u.beads[i]
                if hasattr(bunch, 'kind') and bunch.kind == 'beforeGroup':
                    return
                i -= 1
            # This work regardless of how many items appear after bead n.
            u.beads = u.beads[-n:]
            u.bead = n - 1
        if 'undo' in g.app.debug and 'verbose' in g.app.debug:  # pragma: no cover
            print(f"u.cutStack: {len(u.beads):3}")

    # @+node:ekr.20261009154747.1: *4* u.deprecated
    def deprecated(self):
        warnings.warn(
            f"Undoer.{g.caller()} is deprecated; use composable undo contexts instead",
            DeprecationWarning,
            stacklevel=3,
        )

    # @+node:ekr.20080623083646.10: *4* u.dumpBead
    def dumpBead(self, n: int) -> str:  # pragma: no cover
        u = self
        if n < 0 or n >= len(u.beads):
            return f"no bead: {n=}"
        # bunch = u.beads[n]
        result = []
        result.append('-' * 10)
        result.append(f"len(u.beads): {len(u.beads)}, n: {n}")
        for ivar in ('kind', 'newP', 'newN', 'p', 'oldN', 'undoHelper'):
            result.append(f"{ivar} = {getattr(self, ivar)}")
        return '\n'.join(result)

    def dumpTopBead(self) -> str:  # pragma: no cover
        u = self
        n = len(u.beads)
        if n > 0:
            return self.dumpBead(n - 1)
        return '<no top bead>'

    # @+node:EKR.20040526150818: *4* u.getBead
    def getBead(self, n: int) -> g.Bunch | UndoBead | None:
        """Set Undoer ivars from the bunch at the top of the undo stack."""
        u = self
        if n < 0 or n >= len(u.beads):
            return None  # pragma: no cover
        bunch = u.beads[n]
        if 'undo' in g.app.debug:  # pragma: no cover
            print(f" u.getBead: {n:3} of {len(u.beads)}")
        if isinstance(bunch, g.Bunch):  # Legacy undo code:
            self.setIvarsFromBunch(bunch)
        return bunch

    # @+node:EKR.20040526150818.1: *4* u.peekBead
    def peekBead(self, n: int) -> g.Bunch | None:
        u = self
        if n < 0 or n >= len(u.beads):
            return None
        return u.beads[n]

    # @+node:ekr.20060127113243: *4* u.pushBead
    def pushBead(self, bunch: g.Bunch | UndoBead | None) -> None:
        u = self
        if u.undoBead is not None and not isinstance(bunch, UndoBead):

            def replay(helper):
                u.setIvarsFromBunch(bunch)  # type:ignore
                helper()

            def push_bead_redoer():
                replay(bunch.redoHelper)

            def push_bead_undoer():
                replay(bunch.undoHelper)

            u.undoBead.add_helpers(push_bead_redoer, push_bead_undoer)
            return

        # Add the bunch to the group if it is being accumulated.
        bunch2 = u.bead >= 0 and u.bead < len(u.beads) and u.beads[u.bead]
        if bunch2 and hasattr(bunch2, 'kind') and bunch2.kind == 'beforeGroup':
            # Just append the new bunch the group's items.
            bunch2.items.append(bunch)
        else:
            # Push the bunch.
            u.bead += 1
            u.beads[u.bead :] = [bunch]
            # Recalculate the menu labels.
            u.setUndoTypes()
        if 'undo' in g.app.debug:  # pragma: no cover
            print(f"u.pushBead: {len(u.beads):3} {bunch.undoType}")

    # @+node:ekr.20031218072017.3613: *4* u.redoMenuName, undoMenuName
    def redoMenuName(self, name: str) -> str:
        if name.startswith("Can't Redo"):
            return name
        return "Redo " + name

    def undoMenuName(self, name: str) -> str:
        if name.startswith("Can't Undo"):
            return name
        return "Undo " + name

    # @+node:ekr.20060127070008: *4* u.setIvarsFromBunch
    def setIvarsFromBunch(self, bunch: g.Bunch) -> None:
        u = self
        u.clearOptionalIvars()
        if False and not g.unitTesting:  # Debugging. # pragma: no cover
            print('-' * 40)
            for key in list(bunch.keys()):
                g.trace(f"{key:20} {bunch.get(key)!r}")
            print('-' * 20)
        # bunch is not a dict, so bunch.keys() is required.
        for key in list(bunch.keys()):
            val = bunch.get(key)
            setattr(u, key, val)
            if key not in u.optionalIvars:
                u.optionalIvars.append(key)

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
        if bunch := u.peekBead(u.bead):
            u.setUndoType(bunch.undoType)
        else:
            if u.last_undoable_command_name:
                undoType = f"Can't Undo {u.last_undoable_command_name}"
            else:
                undoType = "Can't Undo"
            u.setUndoType(undoType)
        # Set only the redo menu label.
        if bunch := u.peekBead(u.bead + 1):
            u.setRedoType(bunch.undoType)
        else:
            u.setRedoType("Can't Redo")
        u.cutStack()

    # @+node:ekr.20050525151449: *4* u.trace
    def trace(self) -> None:  # pragma: no cover
        ivars = ('kind', 'undoType')
        for ivar in ivars:
            g.pr(ivar, getattr(self, ivar))

    # @+node:ekr.20050410095424: *4* u.updateMarks
    def updateMarks(self, oldOrNew: str) -> None:
        """Update dirty and marked bits."""
        u = self
        c = u.c
        if oldOrNew not in ('new', 'old'):  # pragma: no cover
            g.trace("can't happen")
            return
        isOld = oldOrNew == 'old'
        marked = u.oldMarked if isOld else u.newMarked
        # Note: c.set/clearMarked call a hook.
        if marked:
            c.setMarked(u.p)
        else:
            c.clearMarked(u.p)
        # Undo/redo always set changed/dirty bits because the file may have been saved.
        u.p.setDirty()
        u.c.setChanged()

    # @-others


# @-others
# @@language python
# @@tabwidth -4
# @@pagewidth 70
# @-leo
