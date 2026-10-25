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
        c, p = self.c, self.p
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
        c, u = self.c, self
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
            # Leo *must* support both old and new beads "forever"!
            if isinstance(obj, UndoBead):
                obj.redo()
            elif u.redoHelper:
                u.redoHelper()
            else:
                g.trace(f"no redo helper for {u.kind} {u.undoType}")

            # Finish.
            c.checkOutline()
            u.update_status(redraw=not (isinstance(obj, UndoBead) and obj.redraw_finishers))
        finally:
            u.redoing = False
        u.bead += 1
        u.setUndoTypes()

    # @+node:ekr.20031218072017.2039: *3* u.undo
    @cmd('undo')
    def undo(self, event: LeoKeyEvent | None = None) -> None:
        """Undo the operation described by the undo parameters."""
        c, u = self.c, self
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
            # Leo *must* support both old and new beads "forever"!
            if isinstance(obj, UndoBead):
                obj.undo()
            elif u.undoHelper:
                if u.per_node_undo:
                    u.setIvarsFromVnode(c.p)
                u.undoHelper()
            else:
                g.trace(f"no undo helper for {u.kind} {u.undoType}")

            # Finish.
            c.checkOutline()
            u.update_status(redraw=not (isinstance(obj, UndoBead) and obj.redraw_finishers))
        finally:
            u.undoing = False
        u.bead -= 1
        u.setUndoTypes()

    # @+node:ekr.20261018092455.1: *3* u: Deprecated methods
    # @+node:ekr.20050318085432.4: *4* u.afterX... (deprecated)
    # @+node:ekr.20201109075104.1: *5* u.afterChangeBody
    def afterChangeBody(self, p: Position, command: str, bunch: g.Bunch) -> None:
        """
        Create an undo node using d created by beforeChangeNode.

        *Important*: Before calling this method, caller must:
        - Set p.v.b. (Setting p.b would cause a redraw).
        - Set the desired selection range and insert point.
        - Set the y-scroll position, if desired.
        """
        u = self
        u.deprecated()
        c = u.c
        w = c.frame.body.wrapper
        if u.redoing or u.undoing:
            return  # pragma: no cover
        # Set the type & helpers.
        bunch.kind = 'body'
        bunch.undoType = command
        bunch.undoHelper = u.undoChangeBody
        bunch.redoHelper = u.redoChangeBody
        bunch.newBody = p.b
        bunch.newHead = p.h
        bunch.newIns = w.getInsertPoint()
        bunch.newMarked = p.isMarked()
        # Careful: don't use ternary operator.
        if w:
            bunch.newSel = w.getSelectionRange()
        else:
            bunch.newSel = 0, 0  # pragma: no cover
        bunch.newYScroll = w.getYScrollPosition() if w else 0
        u.pushBead(bunch)

        if g.unitTesting:
            assert command.lower() != 'typing', g.callers()
        elif command.lower() == 'typing':  # pragma: no cover
            g.trace(
                'Error: undoType should not be "Typing"\n'
                'Call u.doTyping instead'
            )  # fmt: skip
        u.updateAfterTyping(p, w)

    # @+node:ekr.20050315134017.4: *5* u.afterChangeGroup
    def afterChangeGroup(
        self,
        p: Position,
        undoType: str,
        reportFlag: bool = False,
    ) -> None:
        """
        Create an undo node for general tree operations using d created by
        beforeChangeGroup
        """
        u = self
        u.deprecated()
        c = u.c
        w = c.frame.body.wrapper
        if u.undoBead is not None:
            u.__exit__(None, None, None)
            return
        if u.redoing or u.undoing:
            return  # pragma: no cover
        if not u.beads:  # pragma: no cover
            g.trace('oops: empty undo stack.')
            return
        bunch = u.beads[u.bead]
        if bunch.kind == 'beforeGroup':
            bunch.kind = 'afterGroup'
        else:  # pragma: no cover
            g.trace(f"oops: expecting beforeGroup, got {bunch.kind}")
        # Set the types & helpers.
        bunch.kind = 'afterGroup'
        bunch.undoType = undoType
        bunch.undoHelper = u.undoGroup
        bunch.redoHelper = u.redoGroup
        bunch.p = p.copy()  # PR #4991.
        bunch.newP = p.copy()
        bunch.newMarked = p.isMarked()
        bunch.newSel = w.getSelectionRange()
        # Tells whether to report the number of separate changes undone/redone.
        if 0:
            # Push the bunch.
            u.bead += 1
            u.beads[u.bead :] = [bunch]
        # Recalculate the menu labels.
        u.setUndoTypes()

    # @+node:ekr.20050315134017.2: *5* u.afterChangeNodeContents
    def afterChangeNodeContents(self, p: Position, command: str, bunch: g.Bunch) -> None:
        """Create an undo node using d created by beforeChangeNode."""
        u = self
        u.deprecated()
        c = u.c
        w = c.frame.body.wrapper
        if u.redoing or u.undoing:
            return
        # Set the type & helpers.
        bunch.kind = 'afterChangeNodeContents'
        bunch.undoType = command
        bunch.undoHelper = u.undoNodeContents
        bunch.redoHelper = u.redoNodeContents
        bunch.inHead = False  # 2013/08/26
        bunch.newBody = p.b
        bunch.newHead = p.h
        bunch.newMarked = p.isMarked()
        # Bug fix 2017/11/12: don't use ternary operator.
        if w:
            bunch.newSel = w.getSelectionRange()
        else:
            bunch.newSel = 0, 0  # pragma: no cover
        bunch.newYScroll = w.getYScrollPosition() if w else 0
        u.pushBead(bunch)

    # @+node:ekr.20201107145642.1: *5* u.afterChangeHeadline
    def afterChangeHeadline(self, p: Position, command: str, bunch: g.Bunch) -> None:
        """Create an undo node using d created by beforeChangeHeadline."""
        u = self
        u.deprecated()
        if u.redoing or u.undoing:
            return  # pragma: no cover

        # Set the type & helpers.
        bunch.kind = 'headline'
        bunch.undoType = command
        bunch.undoHelper = u.undoChangeHeadline
        bunch.redoHelper = u.redoChangeHeadline
        bunch.newHead = p.h
        u.pushBead(bunch)

    afterChangeHead = afterChangeHeadline

    # @+node:felix.20230326225405.1: *5* u.afterChangeMultiHeadline
    def afterChangeMultiHeadline(self, command: str, bunch: g.Bunch) -> None:
        """Create an undo node using d created by beforeChangeMultiHeadline."""
        u = self
        u.deprecated()
        c = self.c
        if u.redoing or u.undoing:
            return  # pragma: no cover
        # Set the type & helpers.
        bunch.kind = 'multipleHeadline'
        bunch.undoType = command
        bunch.undoHelper = u.undoChangeMultiHeadline
        bunch.redoHelper = u.redoChangeMultiHeadline
        oldHeadlines = bunch.headlines
        newHeadlines = {}
        for p in c.all_unique_positions():
            if p.h != oldHeadlines[p.gnx][0]:
                newHeadlines[p.gnx] = (oldHeadlines[p.gnx][0], p.h)
        # Filtered down dict containing only the changed ones.
        bunch.headlines = newHeadlines
        u.pushBead(bunch)

    afterChangeMultiHead = afterChangeMultiHeadline

    # @+node:ekr.20230721130238.1: *5* u.afterChangeTree
    def afterChangeTree(self, command: str, bunch: g.Bunch) -> None:
        u = self
        u.deprecated()
        c = self.c
        p = self.p
        w = c.frame.body.wrapper
        # Set types.
        bunch.kind = 'afterChangeTree'
        bunch.undoType = command
        bunch.undoHelper = u.undoChangeTree
        bunch.redoHelper = u.redoChangeTree
        bunch.newPastedTree = c.fileCommands.outline_to_clipboard_string(c.p)
        bunch.newIns = w.getInsertPoint()
        bunch.newSel = w.getSelectionRange()
        bunch.newMarked = p.isMarked()

        # Push the bunch.
        u.pushBead(bunch)
        # Recalculate the menu labels.
        u.setUndoTypes()

    # @+node:ekr.20231225132413.1: *5* u.afterChangeUA
    def afterChangeUA(self, p: Position, command: str, bunch: g.Bunch) -> None:
        u = self
        u.deprecated()
        if u.redoing or u.undoing:
            return  # pragma: no cover
        bunch.undoType = command
        bunch.newUA = p.v.u
        bunch.undoHelper = u.undoChangeUA
        bunch.redoHelper = u.redoChangeUA
        u.pushBead(bunch)

    # @+node:ekr.20050424161505: *5* u.afterClearRecentFiles
    def afterClearRecentFiles(self, bunch: g.Bunch) -> g.Bunch:
        u = self
        u.deprecated()
        bunch.newRecentFiles = g.app.config.recentFiles[:]
        bunch.undoType = 'Clear Recent Files'
        bunch.undoHelper = u.undoClearRecentFiles
        bunch.redoHelper = u.redoClearRecentFiles
        u.pushBead(bunch)
        return bunch

    # @+node:ekr.20160502175451.1: *5* u.afterCopyMarkedNodes
    def afterCopyMarkedNodes(self, p: Position) -> None:
        u = self
        u.deprecated()
        if u.redoing or u.undoing:
            return
        # createCommonBunch sets:
        #   oldDirty = p.isDirty()
        #   oldMarked = p.isMarked()
        #   oldSel = w and w.getSelectionRange() or None
        #   p = p.copy()
        bunch = u.createCommonBunch(p)
        # Set types.
        bunch.kind = 'copy-marked-nodes'
        bunch.undoType = 'copy-marked-nodes'
        # Set helpers.
        bunch.undoHelper = u.undoCopyMarkedNodes
        bunch.redoHelper = u.redoCopyMarkedNodes
        bunch.newP = p.next()
        bunch.newMarked = p.isMarked()
        u.pushBead(bunch)

    # @+node:ekr.20050411193627.5: *5* u.afterCloneNode
    def afterCloneNode(self, p: Position, command: str, bunch: g.Bunch) -> None:
        u = self
        u.deprecated()
        if u.redoing or u.undoing:
            return  # pragma: no cover
        # Set types & helpers
        bunch.kind = 'clone'
        bunch.undoType = command
        # Set helpers
        bunch.undoHelper = u.undoCloneNode
        bunch.redoHelper = u.redoCloneNode
        bunch.newBack = p.back()  # 6/15/05
        bunch.newParent = p.parent()  # 6/15/05
        bunch.newP = p.copy()
        bunch.newMarked = p.isMarked()
        u.pushBead(bunch)

    # @+node:ekr.20050411193627.8: *5* u.afterDeleteNode
    def afterDeleteNode(self, p: Position, command: str, bunch: g.Bunch) -> None:
        u = self
        u.deprecated()
        if u.redoing or u.undoing:
            return
        # Set types & helpers
        bunch.kind = 'delete'
        bunch.undoType = command
        # Set helpers
        bunch.undoHelper = u.undoDeleteNode
        bunch.redoHelper = u.redoDeleteNode
        bunch.newP = p.copy()
        bunch.newMarked = p.isMarked()
        u.pushBead(bunch)

    # @+node:ekr.20111005152227.15555: *5* u.afterDeleteMarkedNodes
    def afterDeleteMarkedNodes(self, data: list[Position], p: Position) -> None:
        u = self
        u.deprecated()
        if u.redoing or u.undoing:
            return
        bunch = u.createCommonBunch(p)
        # Set types & helpers
        bunch.kind = 'delete-marked-nodes'
        bunch.undoType = 'delete-marked-nodes'
        # Set helpers
        bunch.undoHelper = u.undoDeleteMarkedNodes
        bunch.redoHelper = u.redoDeleteMarkedNodes
        bunch.newP = p.copy()
        bunch.deleteMarkedNodesData = data
        bunch.newMarked = p.isMarked()
        u.pushBead(bunch)

    # @+node:ekr.20080425060424.8: *5* u.afterDemote
    def afterDemote(self, p: Position, followingSibs: list[VNode]) -> None:
        """Create an undo node for demote operations."""
        u = self
        u.deprecated()
        bunch = u.createCommonBunch(p)
        # Set types.
        bunch.kind = 'demote'
        bunch.undoType = 'Demote'
        bunch.undoHelper = u.undoDemote
        bunch.redoHelper = u.redoDemote
        bunch.followingSibs = followingSibs
        # Push the bunch.
        u.pushBead(bunch)
        # Recalculate the menu labels.
        u.setUndoTypes()

    # @+node:ekr.20050411193627.9: *5* u.afterInsertNode
    def afterInsertNode(self, p: Position, command: str, bunch: g.Bunch) -> None:
        u = self
        u.deprecated()
        if u.redoing or u.undoing:
            return
        # Set types & helpers
        bunch.kind = 'insert'
        bunch.undoType = command
        # Set helpers
        bunch.undoHelper = u.undoInsertNode
        bunch.redoHelper = u.redoInsertNode
        bunch.newP = p.copy()
        bunch.newBack = p.back()
        bunch.newParent = p.parent()
        bunch.newMarked = p.isMarked()
        if bunch.pasteAsClone:
            beforeTree = bunch.beforeTree
            afterTree = []
            for bunch2 in beforeTree:
                v = bunch2.v
                afterTree.append(g.Bunch(v=v, head=v.h[:], body=v.b[:]))
            bunch.afterTree = afterTree
        u.pushBead(bunch)

    # @+node:ekr.20050526124257: *5* u.afterMark
    def afterMark(self, p: Position, command: str, bunch: g.Bunch) -> None:
        """Create an undo node for mark and unmark commands."""
        # 'command' unused, but present for compatibility with similar methods.
        u = self
        u.deprecated()
        if u.redoing or u.undoing:
            return  # pragma: no cover
        # Set the type & helpers.
        bunch.undoHelper = u.undoMark
        bunch.redoHelper = u.redoMark
        bunch.newMarked = p.isMarked()
        u.pushBead(bunch)

    # @+node:ekr.20050410110343: *5* u.afterMoveNode
    def afterMoveNode(self, p: Position, command: str, bunch: g.Bunch) -> None:
        u = self
        u.deprecated()
        if u.redoing or u.undoing:
            return
        # Set the types & helpers.
        bunch.kind = 'move'
        bunch.undoType = command
        # Set helper only for undo:
        # The bead pointer will point to an 'beforeGroup' bead for redo.
        bunch.undoHelper = u.undoMove
        bunch.redoHelper = u.redoMove
        bunch.newMarked = p.isMarked()
        bunch.newN = p.childIndex()
        bunch.newParent_v = p._parentVnode()
        bunch.newP = p.copy()
        u.pushBead(bunch)

    # @+node:ekr.20080425060424.12: *5* u.afterPromote
    def afterPromote(self, p: Position, children: list[VNode]) -> None:
        """Create an undo node for demote operations."""
        u = self
        u.deprecated()
        bunch = u.createCommonBunch(p)
        # Set types.
        bunch.kind = 'promote'
        bunch.undoType = 'Promote'
        bunch.undoHelper = u.undoPromote
        bunch.redoHelper = u.redoPromote
        bunch.children = children
        # Push the bunch.
        u.pushBead(bunch)
        # Recalculate the menu labels.
        u.setUndoTypes()

    # @+node:ekr.20080425060424.2: *5* u.afterSort
    def afterSort(self, p: Position, bunch: g.Bunch) -> None:
        """Completes bead for sort operations, which was added to u.beads in beforeSort"""
        u = self
        u.deprecated()
        if u.redoing or u.undoing:
            return  # pragma: no cover
        # Recalculate the menu labels.
        u.setUndoTypes()

    # @+node:ekr.20050318085432.3: *4* u.beforeX... (deprecated)
    # @+node:ekr.20201109074740.1: *5* u.beforeChangeBody
    def beforeChangeBody(self, p: Position) -> g.Bunch:
        """Return data that gets passed to afterChangeBody."""
        u = self
        u.deprecated()
        w = u.c.frame.body.wrapper
        bunch = self.createCommonBunch(p)  # Sets u.oldMarked, u.oldSel, u.p
        bunch.oldBody = p.b
        bunch.oldHead = p.h
        bunch.oldIns = w.getInsertPoint()
        bunch.oldYScroll = w.getYScrollPosition()
        return bunch

    # @+node:ekr.20050315134017.7: *5* u.beforeChangeGroup
    changeGroupWarning = False

    def beforeChangeGroup(self, p: Position, command: str, verboseUndoGroup: bool = False) -> None:
        """Prepare to undo a group of undoable operations."""
        u = self
        u.deprecated()
        if u.undoBead is not None:
            u.__enter__()
            return
        bunch = u.createCommonBunch(p)
        # Set types.
        bunch.kind = 'beforeGroup'
        bunch.undoType = command
        bunch.verboseUndoGroup = verboseUndoGroup
        # Set helper only for redo:
        # The bead pointer will point to an 'afterGroup' bead for undo.
        bunch.undoHelper = u.undoGroup
        bunch.redoHelper = u.redoGroup
        bunch.items = []
        # Push the bunch.
        u.bead += 1
        u.beads[u.bead :] = [bunch]

    # @+node:ekr.20201107145859.1: *5* u.beforeChangeHeadline
    def beforeChangeHeadline(self, p: Position) -> g.Bunch:
        """
        Return data that gets passed to afterChangeNode.

        The oldHead kwarg works around a Qt difficulty when changing headlines.
        """
        u = self
        u.deprecated()
        bunch = u.createCommonBunch(p)
        bunch.oldHead = p.h
        return bunch

    beforeChangeHead = beforeChangeHeadline

    # @+node:felix.20230326230839.1: *5* u.beforeChangeMultiHeadline
    def beforeChangeMultiHeadline(self, p: Position) -> g.Bunch:
        """
        Return data that gets passed to afterChangeMultiHeadline.
        p is used to select position after undo/redo multiple headline changes is done
        """
        c, u = self.c, self
        u.deprecated()
        bunch = u.createCommonBunch(p)
        headlines = {}
        for p in c.all_unique_positions():
            headlines[p.gnx] = (p.h, None)
        # contains all, but will get reduced by afterChangeMultiHeadline
        bunch.headlines = headlines
        return bunch

    beforeChangeMultiHead = beforeChangeMultiHeadline

    # @+node:ekr.20050315133212.2: *5* u.beforeChangeNodeContents
    def beforeChangeNodeContents(self, p: Position) -> g.Bunch:
        """Return data that gets passed to afterChangeNode."""
        c, u = self.c, self
        u.deprecated()
        w = c.frame.body.wrapper
        bunch = u.createCommonBunch(p)
        bunch.kind = 'beforeChangeNodeContents'
        bunch.oldBody = p.b
        bunch.oldHead = p.h
        # #1413: Always restore yScroll if possible.
        bunch.oldYScroll = w.getYScrollPosition() if w else 0
        return bunch

    # @+node:ekr.20230721130319.1: *5* u.beforeChangeTree
    def beforeChangeTree(self, p: Position) -> g.Bunch:
        u = self
        u.deprecated()
        c = u.c
        w = c.frame.body.wrapper
        bunch = self.createCommonBunch(p)  # Sets u.oldMarked, u.oldSel, u.p
        bunch.kind = 'beforeChangeTree'
        bunch.oldPastedTree = c.fileCommands.outline_to_clipboard_string(c.p)
        bunch.oldBody = p.b
        bunch.oldHead = p.h
        bunch.oldIns = w.getInsertPoint()
        bunch.oldYScroll = w.getYScrollPosition()
        return bunch

    # @+node:ekr.20231225131907.1: *5* u.beforeChangeUA
    def beforeChangeUA(self, p: Position) -> g.Bunch:
        u = self
        u.deprecated()
        bunch = u.createCommonBunch(p)
        bunch.oldUA = p.v.u
        return bunch

    # @+node:ekr.20050424161505.1: *5* u.beforeClearRecentFiles
    def beforeClearRecentFiles(self) -> g.Bunch:
        u = self
        u.deprecated()
        p = u.c.p
        bunch = u.createCommonBunch(p)
        bunch.oldRecentFiles = g.app.config.recentFiles[:]
        return bunch

    # @+node:ekr.20050412080354: *5* u.beforeCloneNode
    def beforeCloneNode(self, p: Position) -> g.Bunch:
        u = self
        u.deprecated()
        bunch = u.createCommonBunch(p)
        return bunch

    # @+node:ekr.20050411193627.3: *5* u.beforeDeleteNode
    def beforeDeleteNode(self, p: Position) -> g.Bunch:
        u = self
        u.deprecated()
        bunch = u.createCommonBunch(p)
        bunch.oldBack = p.back()
        bunch.oldParent = p.parent()
        return bunch

    # @+node:ekr.20050411193627.4: *5* u.beforeInsertNode
    def beforeInsertNode(
        self,
        p: Position,
        pasteAsClone: bool = False,
        copiedBunchList: list[g.Bunch] | None = None,
    ) -> g.Bunch:
        u = self
        u.deprecated()
        if copiedBunchList is None:
            copiedBunchList = []
        bunch = u.createCommonBunch(p)
        bunch.pasteAsClone = pasteAsClone
        if pasteAsClone:
            # Save the list of bunched.
            bunch.beforeTree = copiedBunchList
        return bunch

    # @+node:ekr.20050526131252: *5* u.beforeMark
    def beforeMark(self, p: Position, command: str) -> g.Bunch:
        u = self
        u.deprecated()
        bunch = u.createCommonBunch(p)
        bunch.kind = 'mark'
        bunch.undoType = command
        return bunch

    # @+node:ekr.20050410110215: *5* u.beforeMoveNode
    def beforeMoveNode(self, p: Position) -> g.Bunch:
        u = self
        u.deprecated()
        bunch = u.createCommonBunch(p)
        bunch.oldN = p.childIndex()
        bunch.oldParent_v = p._parentVnode()
        return bunch

    # @+node:ekr.20080425060424.3: *5* u.beforeSort
    def beforeSort(
        self,
        p: Position,
        undoType: str,
        oldChildren: list[VNode],
        newChildren: list[VNode],
        sortChildren: bool,
    ) -> g.Bunch:
        """Create an undo node for sort operations."""
        u = self
        u.deprecated()
        if sortChildren:
            bunch = u.createCommonBunch(p.parent())
        else:
            bunch = u.createCommonBunch(p)
        # Set types.
        bunch.kind = 'sort'
        bunch.undoType = undoType
        bunch.undoHelper = u.undoSort
        bunch.redoHelper = u.redoSort
        bunch.oldChildren = oldChildren
        bunch.newChildren = newChildren
        bunch.sortChildren = sortChildren  # A bool
        # Push the bunch.
        u.pushBead(bunch)
        return bunch

    # @+node:ekr.20110519074734.6092: *4* u.redo helpers (deprecated)
    # @+node:ekr.20191213085226.1: *5*  u.reloadHelper (do nothing)
    def redoHelper(self) -> None:
        """The default do-nothing redo helper."""

    # @+node:ekr.20201109080732.1: *5* u.redoChangeBody
    def redoChangeBody(self) -> None:
        c, u, w = self.c, self, self.c.frame.body.wrapper
        # selectPosition causes recoloring, so don't do this unless needed.
        if c.p != u.p:  # #1333.
            c.selectPosition(u.p)
        u.p.setDirty()
        u.p.b = u.newBody
        u.p.h = u.newHead
        # This is required so. Otherwise redraw will revert the change!
        c.frame.tree.setHeadline(u.p, u.newHead)
        if u.newMarked:
            u.p.setMarked()
        else:
            u.p.clearMarked()
        if u.groupCount == 0:
            w.setAllText(u.newBody)
            i, j = u.newSel
            w.setSelectionRange(i, j, insert=u.newIns)
            w.setYScrollPosition(u.newYScroll)
            c.recolor(u.p)
        u.updateMarks('new')
        u.p.setDirty()

    # @+node:ekr.20201107150619.1: *5* u.redoChangeHeadline (legacy)
    def redoChangeHeadline(self) -> None:
        c, u = self.c, self
        # selectPosition causes recoloring, so don't do this unless needed.
        if c.p != u.p:  # #1333.
            c.selectPosition(u.p)
        u.p.setDirty()
        c.recolor(u.p)
        # Restore the headline.
        u.p.initHeadString(u.newHead)
        # This is required. Otherwise redraw will revert the change!
        c.frame.tree.setHeadline(u.p, u.newHead)

    # @+node:felix.20230326231408.1: *5* u.redoChangeMultiHeadline
    def redoChangeMultiHeadline(self) -> None:
        c, u = self.c, self
        c.recolor(u.p)
        # Swap the ones from the 'bunch.headline' dict
        for gnx, oldNewTuple in u.headlines.items():
            v = c.fileCommands.gnxDict.get(gnx)
            v.initHeadString(oldNewTuple[1])
            if v.gnx == u.p.gnx:
                u.p.setDirty()
                # This is required.  Otherwise redraw will revert the change!
                c.frame.tree.setHeadline(u.p, oldNewTuple[1])
        # selectPosition causes recoloring, so don't do this unless needed.
        if c.p != u.p:  # #1333.
            c.selectPosition(u.p)

    # @+node:ekr.20230721131611.1: *5* u.redoChangeTree (no calls!)
    def redoChangeTree(self) -> None:
        c, u, w = self.c, self, self.c.frame.body.wrapper
        # selectPosition causes recoloring, so don't do this unless needed.
        if c.p != u.p:
            c.selectPosition(u.p)
        u.p.setDirty()
        u.p.b = u.newBody
        u.p.h = u.newHead
        # This is required so. Otherwise redraw will revert the change!
        c.frame.tree.setHeadline(u.p, u.newHead)
        if u.newMarked:
            u.p.setMarked()
        else:
            u.p.clearMarked()
        if u.groupCount == 0:
            w.setAllText(u.newBody)
            i, j = u.newSel
            w.setSelectionRange(i, j, insert=u.newIns)
            w.setYScrollPosition(u.newYScroll)
            c.recolor(u.p)
        u.updateMarks('new')
        u.p.setDirty()

    # @+node:ekr.20231225134021.1: *5* u.redoChangeUA
    def redoChangeUA(self) -> None:
        u = self
        v = u.p.v
        v.setDirty()
        v.u = u.newUA

    # @+node:ekr.20050424170219: *5* u.redoClearRecentFiles
    def redoClearRecentFiles(self) -> None:
        c, u = self.c, self
        rf = g.app.recentFilesManager
        rf.setRecentFiles(u.newRecentFiles[:])
        rf.createRecentFilesMenuItems(c)

    # @+node:ekr.20160502175557.1: *5* u.redoCopyMarkedNodes
    def redoCopyMarkedNodes(self) -> None:
        c, u = self.c, self
        c.selectPosition(u.p)
        c.copyMarked()
        u.newP = c.p

    # @+node:ekr.20050412083057: *5* u.redoCloneNode (calls p methods only)
    def redoCloneNode(self) -> None:
        c, u = self.c, self
        if cc := c.chapterController:
            cc.selectChapterByName('main')
        if u.newBack:
            u.newP._linkAfter(u.newBack)
        elif u.newParent:
            u.newP._linkAsNthChild(u.newParent, 0)
        else:
            u.newP._linkAsRoot()
        c.selectPosition(u.newP)
        u.newP.setDirty()

    # @+node:ekr.20111005152227.15559: *5* u.redoDeleteMarkedNodes (converted)
    def redoDeleteMarkedNodes(self) -> None:
        u = self
        c = u.c

        # PR #4996: Remove dependency on c.deleteOutline.

        # c.selectPosition(u.p)
        # c.deleteMarked()
        p = c.rootPosition()  # Doesn't use c.p!
        while p:
            if p.isMarked():
                next = p.positionAfterDeletedTree()
                p.doDelete()
                p = next
            else:
                p.moveToThreadNext()

        # Legacy
        c.selectPosition(u.newP)

    # @+node:EKR.20040526072519.2: *5* u.redoDeleteNode (converted)
    def redoDeleteNode(self) -> None:
        c, u = self.c, self
        newP = u.newP.copy() if u.newP else c.p

        # PR #4996: Remove dependency on c.deleteOutline.

        # c.selectPosition(u.p)
        p = u.p

        # c.deleteOutline()
        newNode = p.visBack(c) if p.hasVisBack(c) else p.next()
        p.doDelete(newNode)

        # Legacy.
        if c.positionExists(newP):  # PR #4991.
            c.p = newP

    # @+node:ekr.20080425060424.9: *5* u.redoDemote
    def redoDemote(self) -> None:
        c, u = self.c, self
        parent_v = u.p._parentVnode()
        n = u.p.childIndex()
        # Move the demoted nodes from the old parent to the new parent.
        parent_v.children = parent_v.children[: n + 1]
        u.p.v.children.extend(u.followingSibs)
        # Adjust the parent links of the moved nodes.
        # There is no need to adjust descendant links.
        for v in u.followingSibs:
            v.parents.remove(parent_v)
            v.parents.append(u.p.v)
        u.p.setDirty()
        c.p = u.p

    # @+node:ekr.20050318085432.6: *5* u.redoGroup
    def redoGroup(self) -> None:
        """Process beads until the matching 'afterGroup' bead is seen."""
        c, u = self.c, self
        newSel = u.newSel
        u.groupCount += 1
        bunch = u.beads[u.bead + 1]
        count = 0
        if not hasattr(bunch, 'items'):
            g.trace(f"oops: expecting bunch.items. got bunch.kind = {bunch.kind}")
            g.trace(bunch)
        else:
            for z in bunch.items:
                if isinstance(z, UndoBead):
                    z.redo()
                    count += 1
                    continue
                self.setIvarsFromBunch(z)
                if z.redoHelper:
                    z.redoHelper()
                    count += 1
                else:
                    g.trace(f"oops: no redo helper for {u.undoType} {u.p.h}")
        u.groupCount -= 1
        u.updateMarks('new')  # Bug fix: Leo 4.4.6.
        if not g.unitTesting and u.verboseUndoGroup:
            g.es("redo", count, "instances")

        # PR #4991: Helpers set dirty bits and c.p. Do not set c.p here!

        # Set the selection, independently of helpers.
        if newSel:
            i, j = newSel
            c.frame.body.wrapper.setSelectionRange(i, j)

    # @+node:ekr.20050412085138.1: *5* u.redoHoistNode & redoDehoistNode (call c.hoist/dehoist)
    def redoHoistNode(self) -> None:
        c, u = self.c, self
        u.p.setDirty()
        c.selectPosition(u.p)
        c.hoist()

    def redoDehoistNode(self) -> None:
        c, u = self.c, self
        u.p.setDirty()
        c.selectPosition(u.p)
        c.dehoist()

    # @+node:ekr.20050412084532: *5* u.redoInsertNode (calls only p/v methods)
    def redoInsertNode(self) -> None:
        c, u = self.c, self
        if cc := c.chapterController:
            cc.selectChapterByName('main')
        if u.newBack:
            u.newP._linkAfter(u.newBack)
        elif u.newParent:
            u.newP._linkAsNthChild(u.newParent, 0)
        else:
            u.newP._linkAsRoot()
        if u.pasteAsClone:
            for bunch in u.afterTree:
                v = bunch.v
                if u.newP.v == v:
                    u.newP.b = bunch.body
                    u.newP.h = bunch.head
                else:
                    v.setBodyString(bunch.body)
                    v.setHeadString(bunch.head)
        u.newP.setDirty()
        c.selectPosition(u.newP)

    # @+node:ekr.20050526125801: *5* u.redoMark
    def redoMark(self) -> None:
        c, u = self.c, self
        u.updateMarks('new')
        if u.groupCount == 0:
            u.p.setDirty()
            c.selectPosition(u.p)

    # @+node:ekr.20050411111847: *5* u.redoMove
    def redoMove(self) -> None:
        c, u = self.c, self
        cc = c.chapterController
        v = u.p.v
        assert u.oldParent_v
        assert u.newParent_v
        assert v
        if cc:
            cc.selectChapterByName('main')
        # Adjust the children arrays of the old parent.
        assert u.oldParent_v.children[u.oldN] == v
        del u.oldParent_v.children[u.oldN]
        u.oldParent_v.setDirty()
        # Adjust the children array of the new parent.
        parent_v = u.newParent_v
        parent_v.children.insert(u.newN, v)
        v.parents.append(u.newParent_v)
        v.parents.remove(u.oldParent_v)
        u.newParent_v.setDirty()
        u.updateMarks('new')
        u.newP.setDirty()
        c.selectPosition(u.newP)

    # @+node:ekr.20050318085432.7: *5* u.redoNodeContents
    def redoNodeContents(self) -> None:
        c, u = self.c, self
        w = c.frame.body.wrapper
        # selectPosition causes recoloring, so don't do this unless needed.
        if c.p != u.p:  # #1333.
            c.selectPosition(u.p)
        u.p.setDirty()
        # Restore the body.
        u.p.setBodyString(u.newBody)
        w.setAllText(u.newBody)
        c.recolor(u.p)
        # Restore the headline.
        u.p.initHeadString(u.newHead)
        # This is required so.  Otherwise redraw will revert the change!
        c.frame.tree.setHeadline(u.p, u.newHead)  # New in 4.4b2.
        if u.groupCount == 0 and u.newSel:
            i, j = u.newSel
            w.setSelectionRange(i, j)
        if u.groupCount == 0 and u.newYScroll is not None:
            w.setYScrollPosition(u.newYScroll)
        u.updateMarks('new')
        u.p.setDirty()

    # @+node:ekr.20230713150847.1: *5* u.redoParseBody (calls ic.parse_body)
    def redoParseBody(self) -> None:
        """Redo the parse-body command."""
        u = self
        c = u.c
        ic = c.importCommands
        p = u.p
        if c.p != p:
            c.selectPosition(p)
        ic.parse_body(p)

    # @+node:ekr.20080425060424.13: *5* u.redoPromote
    def redoPromote(self) -> None:
        c, u = self.c, self
        parent_v = u.p._parentVnode()
        # Add the children to parent_v's children.
        n = u.p.childIndex() + 1
        old_children = parent_v.children[:]
        # Add children up to the promoted nodes.
        parent_v.children = old_children[:n]
        # Add the promoted nodes.
        parent_v.children.extend(u.children)
        # Add the children up to the promoted nodes.
        parent_v.children.extend(old_children[n:])
        # Remove the old children.
        u.p.v.children = []
        # Adjust the parent links in the moved children.
        # There is no need to adjust descendant links.
        for child in u.children:
            child.parents.remove(u.p.v)
            child.parents.append(parent_v)
        u.p.setDirty()
        c.p = u.p

    # @+node:ekr.20080425060424.4: *5* u.redoSort
    def redoSort(self) -> None:
        c, u = self.c, self
        p = u.p
        if u.sortChildren:
            p.v.children = u.newChildren[:]
        else:
            parent_v = p._parentVnode()
            parent_v.children = u.newChildren[:]
            # Only the child index of new position changes!
            for i, v in enumerate(parent_v.children):
                if v.gnx == p.v.gnx:
                    p._childIndex = i
                    break
        p.setAllAncestorAtFileNodesDirty()
        c.p = p

    # @+node:EKR.20040526075238.5: *5* u.redoTyping
    def redoTyping(self) -> None:
        c, u = self.c, self
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

    # @+node:ekr.20110519074734.6093: *4* u.undo helpers (deprecated)
    # @+node:ekr.20191213085246.1: *5*  u.undoHelper
    def undoHelper(self) -> None:
        """The default do-nothing undo helper."""

    # @+node:ekr.20201109080631.1: *5* u.undoChangeBody
    def undoChangeBody(self) -> None:
        """
        Undo all changes to the contents of a node,
        including headline and body text, and marked bits.
        """
        c, u, w = self.c, self, self.c.frame.body.wrapper
        # PR #4991: do not change c.p here!
        u.p.setDirty()
        u.p.b = u.oldBody
        u.p.h = u.oldHead
        # This is required.  Otherwise c.redraw will revert the change!
        c.frame.tree.setHeadline(u.p, u.oldHead)
        if u.oldMarked:
            u.p.setMarked()
        else:
            u.p.clearMarked()
        if u.groupCount == 0:
            w.setAllText(u.oldBody)
            i, j = u.oldSel
            w.setSelectionRange(i, j, insert=u.oldIns)
            w.setYScrollPosition(u.oldYScroll)
            c.recolor(u.p)
        u.updateMarks('old')

    # @+node:ekr.20201107150041.1: *5* u.undoChangeHeadline
    def undoChangeHeadline(self) -> None:
        """Undo a change to a node's headline."""
        c, u = self.c, self
        # selectPosition causes recoloring, so don't do this unless needed.
        if c.p != u.p:  # #1333.
            c.selectPosition(u.p)
        u.p.setDirty()
        c.recolor(u.p)
        u.p.initHeadString(u.oldHead)
        # This is required. Otherwise c.redraw will revert the change!
        c.frame.tree.setHeadline(u.p, u.oldHead)

    # @+node:felix.20230326231543.1: *5* u.undoChangeMultiHeadline
    def undoChangeMultiHeadline(self) -> None:
        """Undo a change to a node's headline."""
        c, u = self.c, self
        # selectPosition causes recoloring, so don't do this unless needed.
        c.recolor(u.p)

        # Swap the ones from the 'bunch.headline' dict
        for gnx, oldNewTuple in u.headlines.items():
            v = c.fileCommands.gnxDict.get(gnx)
            v.initHeadString(oldNewTuple[0])
            if v.gnx == u.p.gnx:
                u.p.setDirty()
                # This is required.  Otherwise redraw will revert the change!
                c.frame.tree.setHeadline(u.p, oldNewTuple[0])
        if c.p != u.p:
            c.selectPosition(u.p)

    # @+node:ekr.20231225133712.1: *5* u.undoChangeUA
    def undoChangeUA(self) -> None:
        u = self
        v = u.p.v
        v.setDirty()
        v.u = u.oldUA

    # @+node:ekr.20050424170219.1: *5* u.undoClearRecentFiles
    def undoClearRecentFiles(self) -> None:
        c, u = self.c, self
        rf = g.app.recentFilesManager
        rf.setRecentFiles(u.oldRecentFiles[:])
        rf.createRecentFilesMenuItems(c)

    # @+node:ekr.20050412083057.1: *5* u.undoCloneNode (converted)
    def undoCloneNode(self) -> None:
        c, u = self.c, self
        if cc := c.chapterController:
            cc.selectChapterByName('main')

        # PR #4996: Remove dependency on c.deleteOutline.

        # c.selectPosition(u.newP)
        p = u.newP

        # c.deleteOutline()
        newNode = p.visBack(c) if p.hasVisBack(c) else p.next()
        p.doDelete(newNode)

        # Legacy code.
        u.p.setDirty()
        c.selectPosition(u.p)

    # @+node:ekr.20160502175653.1: *5* u.undoCopyMarkedNodes
    def undoCopyMarkedNodes(self) -> None:
        u = self
        next = u.p.next()
        assert next.h == 'Copies of marked nodes', (u.p.h, next.h)
        next.doDelete()
        u.p.setAllAncestorAtFileNodesDirty()
        u.c.selectPosition(u.p)

    # @+node:ekr.20111005152227.15557: *5* u.undoDeleteMarkedNodes (calls p methods)
    def undoDeleteMarkedNodes(self) -> None:
        c, u = self.c, self
        # Undo the deletes in reverse order
        aList = u.deleteMarkedNodesData[:]
        aList.reverse()
        for p in aList:
            if p.stack:
                parent_v, _ = p.stack[-1]
            else:
                parent_v = c.hiddenRootNode
            p.v._addLink(p._childIndex, parent_v)
            p.v.setDirty()
        u.p.setAllAncestorAtFileNodesDirty()
        c.selectPosition(u.p)

    # @+node:ekr.20050412084055: *5* u.undoDeleteNode (calls p methods)
    def undoDeleteNode(self) -> None:
        c, u = self.c, self
        if u.oldBack:
            u.p._linkAfter(u.oldBack)
        elif u.oldParent:
            u.p._linkAsNthChild(u.oldParent, 0)
        else:
            u.p._linkAsRoot()
        u.p.setDirty()
        c.selectPosition(u.p)  # Required.

    # @+node:ekr.20080425060424.10: *5* u.undoDemote
    def undoDemote(self) -> None:
        c, u = self.c, self
        parent_v = u.p._parentVnode()
        n = len(u.followingSibs)
        # Remove the demoted nodes from p's children.
        u.p.v.children = u.p.v.children[:-n]
        # Add the demoted nodes to the parent's children.
        parent_v.children.extend(u.followingSibs)
        # Adjust the parent links.
        # There is no need to adjust descendant links.
        parent_v.setDirty()
        for sib in u.followingSibs:
            sib.parents.remove(u.p.v)
            sib.parents.append(parent_v)
        u.p.setAllAncestorAtFileNodesDirty()
        c.p = u.p

    # @+node:ekr.20050318085713: *5* u.undoGroup
    def undoGroup(self) -> None:
        """Process beads until the matching 'beforeGroup' bead is seen."""
        c, u = self.c, self
        oldSel = u.oldSel
        u.groupCount += 1
        bunch = u.beads[u.bead]
        count = 0
        if not hasattr(bunch, 'items'):
            g.trace(f"oops: expecting bunch.items. got bunch.kind = {bunch.kind}")
            g.trace(bunch)
        else:
            # Important bug fix: 9/8/06: reverse the items first.
            reversedItems = bunch.items[:]
            reversedItems.reverse()
            for z in reversedItems:
                if isinstance(z, UndoBead):
                    z.undo()
                    count += 1
                    continue
                self.setIvarsFromBunch(z)
                if z.undoHelper:
                    z.undoHelper()
                    count += 1
                else:
                    g.trace(f"oops: no undo helper for {u.undoType} {u.p.v}")
        u.groupCount -= 1
        u.updateMarks('old')  # Bug fix: Leo 4.4.6.
        if not g.unitTesting and u.verboseUndoGroup:
            g.es("undo", count, "instances")

        # PR #4991: Helpers set dirty bits and c.p. Do not set c.p here!

        if oldSel:
            # Restore the selection, independently of helpers.
            i, j = oldSel
            c.frame.body.wrapper.setSelectionRange(i, j)

    # @+node:ekr.20050412083244: *5* u.undoHoistNode & undoDehoistNode (call c.hoist/deHoist)
    def undoHoistNode(self) -> None:
        c, u = self.c, self
        u.p.setDirty()
        c.selectPosition(u.p)
        c.dehoist()

    def undoDehoistNode(self) -> None:
        c, u = self.c, self
        u.p.setDirty()
        c.selectPosition(u.p)
        c.hoist()

    # @+node:ekr.20050412085112: *5* u.undoInsertNode (converted, calls only p methods)
    def undoInsertNode(self) -> None:
        c, u = self.c, self
        if cc := c.chapterController:
            cc.selectChapterByName('main')
        u.newP.setAllAncestorAtFileNodesDirty()
        c.selectPosition(u.newP)
        p = c.p
        newNode = p.visBack(c) if p.hasVisBack(c) else p.next()
        p.doDelete(newNode)
        c.redraw(newNode)
        c.checkOutline()

        if u.pasteAsClone:
            for bunch in u.beforeTree:
                v = bunch.v
                if u.p.v == v:
                    u.p.b = bunch.body
                    u.p.h = bunch.head
                else:
                    v.setBodyString(bunch.body)
                    v.setHeadString(bunch.head)

    # @+node:ekr.20050526124906: *5* u.undoMark
    def undoMark(self) -> None:
        c, u = self.c, self
        u.updateMarks('old')
        if u.groupCount == 0:
            u.p.setDirty()
            c.selectPosition(u.p)

    # @+node:ekr.20050411112033: *5* u.undoMove
    def undoMove(self) -> None:
        c, u = self.c, self
        if cc := c.chapterController:
            cc.selectChapterByName('main')
        v = u.p.v
        assert u.oldParent_v
        assert u.newParent_v
        assert v
        # Adjust the children arrays.
        assert u.newParent_v.children[u.newN] == v
        del u.newParent_v.children[u.newN]
        u.oldParent_v.children.insert(u.oldN, v)
        # Recompute the parent links.
        v.parents.append(u.oldParent_v)
        v.parents.remove(u.newParent_v)
        u.updateMarks('old')
        u.p.setDirty()
        c.selectPosition(u.p)

    # @+node:ekr.20050318085713.1: *5* u.undoNodeContents
    def undoNodeContents(self) -> None:
        """
        Undo all changes to the contents of a node,
        including headline and body text, and marked bits.
        """
        c, u = self.c, self
        w = c.frame.body.wrapper
        # selectPosition causes recoloring, so don't do this unless needed.
        if c.p != u.p:  # #1333.
            c.selectPosition(u.p)
        u.p.setDirty()
        u.p.b = u.oldBody
        w.setAllText(u.oldBody)
        c.recolor(u.p)
        u.p.h = u.oldHead
        # This is required.  Otherwise c.redraw will revert the change!
        c.frame.tree.setHeadline(u.p, u.oldHead)
        if u.groupCount == 0 and u.oldSel:
            i, j = u.oldSel
            w.setSelectionRange(i, j)
        if u.groupCount == 0 and u.oldYScroll is not None:
            w.setYScrollPosition(u.oldYScroll)
        u.updateMarks('old')

    # @+node:ekr.20230721131446.1: *5* u.undoChangeTree (calls c.p.back().doDelete)
    def undoChangeTree(self) -> None:
        """
        Undo all changes to the node and its subtree.
        """
        c = self.c
        u = self
        w = c.frame.body.wrapper
        # selectPosition causes recoloring, so don't do this unless needed.
        if c.p != u.p:
            c.selectPosition(u.p)
        assert c.p == u.p
        p = u.p
        # u.p.setDirty()

        # Paste the outline and select it.
        s = u.oldPastedTree
        pasted = c.fileCommands.getLeoOutlineFromClipboardRetainingClones(s)
        assert c.p == pasted

        # Delete the old tree. Its position should still exist.
        c.p.back().doDelete(pasted)  # 2025/12/01

        # Finish
        w.setAllText(u.oldBody)
        c.recolor(u.p)
        p.h = u.oldHead
        # This is required.  Otherwise c.redraw will revert the change!
        c.frame.tree.setHeadline(p, u.oldHead)
        i, j = u.oldSel
        w.setSelectionRange(i, j)
        w.setYScrollPosition(u.oldYScroll)
        u.updateMarks('old')

    # @+node:ekr.20230713150109.1: *5* u.undoParseBody (calls p.deleteAllChildren)
    def undoParseBody(self) -> None:
        """Restore p.b and delete all children."""
        u = self
        c = u.c
        p = u.p
        w = c.frame.body.wrapper
        p.deleteAllChildren()
        c.selectPosition(p)
        p.setDirty()
        p.b = u.oldBody
        w.setAllText(u.oldBody)
        w.setSelectionRange(0, 0, insert=0)
        w.setYScrollPosition(0)

    # @+node:ekr.20080425060424.14: *5* u.undoPromote
    def undoPromote(self) -> None:
        c, u = self.c, self
        parent_v = u.p._parentVnode()  # The parent of the all the *promoted* nodes.
        # Remove the promoted nodes from parent_v's children.
        n = u.p.childIndex() + 1
        # Adjust the old parents children
        old_children = parent_v.children
        # Add the nodes before the promoted nodes.
        parent_v.children = old_children[:n]
        # Add the nodes after the promoted nodes.
        parent_v.children.extend(old_children[n + len(u.children) :])
        # Add the demoted nodes to v's children.
        u.p.v.children = u.children[:]
        # Adjust the parent links.
        # There is no need to adjust descendant links.
        parent_v.setDirty()
        for child in u.children:
            child.parents.remove(parent_v)
            child.parents.append(u.p.v)
        u.p.setAllAncestorAtFileNodesDirty()
        c.p = u.p

    # @+node:ekr.20031218072017.1493: *5* u.undoRedoText
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
        c, u = self.c, self
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

    # @+node:ekr.20080425060424.5: *5* u.undoSort
    def undoSort(self) -> None:
        c, u = self.c, self
        p = u.p
        if u.sortChildren:
            p.v.children = u.oldChildren[:]
        else:
            parent_v = p._parentVnode()
            parent_v.children = u.oldChildren[:]
            # Only the child index of new position changes!
            for i, v in enumerate(parent_v.children):
                if v.gnx == p.v.gnx:
                    p._childIndex = i
                    break
        p.setAllAncestorAtFileNodesDirty()
        c.p = p

    # @+node:EKR.20040526090701.4: *5* u.undoTyping
    def undoTyping(self) -> None:
        c, u = self.c, self
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

    # @+node:vivainio.202610110002.2: *5* u.type_text
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
        p.v.b = newText
        u.updateAfterTyping(p, w)
        if u.per_node_undo:
            u.putIvarsToVnode(p)

    # @+node:ekr.20031218072017.1490: *5* u.doTyping & helper
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
        c, u, w = self.c, self, self.c.frame.body.wrapper
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
        c, u = self.c, self
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

    # @+node:ekr.20191213092304.1: *5* u.update_status
    def update_status(self, *, redraw: bool = True) -> None:
        """
        Update status after either an undo or redo:
        """
        c, u = self.c, self
        w = c.frame.body.wrapper

        # PR #4809. c.p has already been set.

        # # 1451. *Always* set the changed bit.
        # Redrawing *must* be done here before setting u.undoing to False.
        i, j = w.getSelectionRange()
        ins = w.getInsertPoint()
        if redraw:
            c.redraw()
        c.recolor()
        if u.inHead:
            c.editHeadline()
            u.inHead = False
        else:
            c.bodyWantsFocus()
            w.setSelectionRange(i, j, insert=ins)
            w.seeInsertPoint()

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
    def clone_node(self, p: Position) -> Position | None:
        """Clone p, returning and selecting the new occurrence."""
        c, b = self.c, self._require_bead()
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
        c, b = u.c, u._require_bead()
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
        c, b = self.c, self._require_bead()
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

    # @+node:ekr.20261005140833.1: *6* u.set_body
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
        w = u.c.frame.body.wrapper
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
    def change_headline(
        self,
        p: Position,
        new_h: str,
        *,
        ch: str = '',
        update_editor: bool = True,
    ) -> None:
        """
        Change a headline and preserve directives, dirty bits and editor state.

        Called *only* from LeoTree.onHeadChanged (except for unit tests).

        This method should *not* have an @contextmanager decorator:
        it is never called from within other @contextmanager methods.
        """
        c = self.c
        b = self._require_bead()
        old_h = p.h
        if old_h == new_h:
            return

        p = p.copy()

        def update(head):
            c.p = p
            p.initHeadString(head)
            # p.setDirty() calls p.v.setAllAncestorAtFileNodesDirty()
            p.setDirty()
            c.frame.tree.setHeadline(p, head)

        # Do the action.
        # Leave the live editor alone: it may contain multiline abbreviation text.
        p.initHeadString(new_h)
        p.setDirty()
        if update_editor:  # This test is required.
            c.frame.tree.setHeadline(p, new_h)
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
        c = self.c
        if self.undoing or self.redoing:
            yield self
            return
        if not c.changed:
            c.setChanged()
        with self as u:
            u.set_command_name(command_name)
            if u.capture_level > 0 or p.v in u.node_captures:
                yield u
                return
            old_p = c.p
            old_state = u.capture_node(p.v)
            old_ui = u.capture_ui()
            u.node_captures.add(p.v)
            try:
                yield u
            finally:
                u.node_captures.remove(p.v)
                new_p = c.p
                u._redraw(new_p)  # PR #5005.
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
        if self.undoing or self.redoing:
            yield self
            return
        c = self.c
        if not c.changed:
            c.setChanged()
        with self as u:
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
                u._redraw(new_p)  # PR #5005
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
                        u._redraw(new_p)

                    def change_outline_ui_undoer() -> None:
                        u.restore_ui(old_ui)
                        u._redraw(old_p)

                    u.undoBead.add_finishers(change_outline_ui_redoer, change_outline_ui_undoer)

    # @+node:ekr.20261015041620.2: *7* u.capture_outline
    def capture_outline(self) -> dict:
        result = {}
        pending = [self.c.hiddenRootNode]
        while pending:
            v = pending.pop()
            if v in result:
                continue
            result[v] = self.capture_node(v), tuple(v.children), tuple(v.parents)
            pending.extend(v.children)
        return result

    # @+node:ekr.20261015041620.3: *7* u.restore_outline
    def restore_outline(self, delta: dict) -> None:
        # Restore every link before touching content or propagating dirty bits.
        for v in delta:
            v.setAllAncestorAtFileNodesDirty()
        for v, (_, children, parents) in delta.items():
            v.children = list(children)
            v.parents = list(parents)
        for v, (state, _, _) in delta.items():
            self.restore_node(v, state)

    # @+node:vivainio.202610110001.4: *6* u.change_recent_files
    @contextmanager
    def change_recent_files(self, command_name: str = 'Clear Recent Files') -> Iterator[Undoer]:
        """
        Handling doing, undoing and redoing for the 'Clear Recent Files' menu item."""
        rf = g.app.recentFilesManager
        old_files = rf.recentFiles[:]
        with self as u:
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
        if self.undoing or self.redoing:
            yield self
            return
        c = self.c
        if not c.changed:
            c.setChanged()
        with self as u:
            u.set_command_name(command_name)
            if u.capture_level > 0:
                yield u
                return
            old_p, old_ui = p.copy(), u.capture_ui()
            try:
                yield u
            finally:
                new_p = p.copy()
                if old_p != new_p:
                    new_ui = u.capture_ui()
                    u._redraw(new_p)  # PR #5005

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
            for p in self.c.vnode2allPositions(v):
                self.c.frame.tree.setHeadline(p, head)

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
        sel, ins, scroll = w.getSelectionRange(), w.getInsertPoint(), w.getYScrollPosition()
        c.updateSyntaxColorer(p)
        c.redraw(p)
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
        c, u = self.c, self
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
