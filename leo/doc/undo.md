# Composable undo

Leo's built-in commands use `c.undoer` contexts. A completed outer context
publishes one undo bead; nested contexts share that bead and keep the outer
command name. Empty contexts leave history, including a pending redo, intact.
Callbacks replay changes in forward order for redo and reverse order for undo.

## Choosing a context

Use the smallest context that captures the operation:

```python
with c.undoer.change_node(p, 'Edit Node'):
    p.b = new_body
    p.u['metadata'] = {'value': 1}
    c.undoer.redraw(p)

with c.undoer.change_position(p, 'Move Node'):
    p.moveToLastChildOf(parent)
    c.undoer.redraw(p)

with c.undoer.change_outline('Bulk Edit'):
    # Perform structural changes, changes to clones, or edits to many nodes.
    perform_bulk_edit()
    c.undoer.redraw(c.p)
```

`change_node` captures headline, body, marked state, and a deep copy of user
attributes. Nested node contexts can edit distinct nodes; nested contexts for
one vnode are absorbed into its outer capture. This context does not capture
structural changes. Put a bulk context outside node contexts, rather than
starting `change_outline` inside `change_node`; the latter is rejected before
its body runs.

`change_position` records an existing position's move without scanning the
outline. Use it for a single move, rather than a sequence of unrelated moves.

`change_outline` captures the reachable vnode graph before and after the
operation. It retains only changed nodes in the bead, preserving vnode identity,
child order, clone parents, content, marks, and user attributes. Capture takes
linear time and temporary memory in the outline size. Nested outline, node,
and action helpers are absorbed by the outer bulk capture. Enter the context
before a reader, paste operation, or import starts mutating the outline.
`enabled=False` supports callers explicitly requesting a non-undoable operation.

Contexts restore the selected position, body selection, insertion point, scroll,
and relevant editor state. If a command raises after making changes, those
changes remain undoable; contexts do not roll back the command automatically.
Undo and redo clear replay flags even if a callback fails, and advance the
history pointer only after successful replay.

## Action helpers

For small operations, compose action helpers in an explicit context:

```python
with c.undoer as u:
    u.set_command_name('Insert and Edit')
    inserted = u.insert_node(c.p)
    u.set_body(inserted, 'New body')
    u.change_headline(inserted, '', 'New headline')
    u.redraw_and_edit(inserted)
```

The outer caller requests one redraw per context, after all edits, using
`u.redraw(p)`, `u.redraw_and_edit(p, select_all=True)`, or
`u.redraw_after_head_changed()`. Action helpers and snapshot restoration do
not redraw. The redraw helpers perform the initial refresh and register one
final refresh for undo/redo, before restoring body selection and scroll.
Nested contexts share the final redraw callback. Redraw helpers also work
with `change_outline(enabled=False)` without recording undo callbacks.

Action helpers require an active context before mutating anything:

- `insert_node(p, as_child=False, index=None, before=False)` returns the inserted
  position. It respects expanded parents, hoists, and insertion configuration.
- `clone_node(p)` returns the clone position, or `None` if validation fails.
- `delete_node(p)` removes an occurrence and updates selection.
- `set_body(p, text, old_body=None)` edits the target vnode, including a
  non-current node. Supply `old_body` when the widget has already changed.
- `change_headline(p, ch, text, update_editor=True)` updates headline state,
  directives, and hooks. Live headline editors can use `update_editor=False`.
- `set_selection_range(old_ins, old_sel, old_y_scroll=None,
  new_y_scroll=None)` records widget state after editing.

Inserts and clones replay by relinking the original vnode instead of creating
new identities. Deletions retain the detached subtree. Changes dirty affected
nodes and their external-file ancestors. Undo and redo mark the document
changed, including replay after a save; an old bead cannot safely restore a
historical clean flag.

`change_recent_files()` captures the recent-files list separately from the
outline, updating menus and the recent-files file during replay.

## Typing

`type_text(p, 'Typing', oldText, newText, newInsert=None, oldSel=None,
newSel=None, oldYview=None)` records text already changed by the body editor.
It stores an incremental line patch and respects character, line, word, and
node undo granularity. Saving, branching history, or an intervening command
ends coalescing. New typing beads do not use the legacy Undoer's shared scratch
state. Qt body editors and core editing commands use this entry point.

## Compatibility and migration

Legacy `before*`/`after*` APIs and `doTyping` remain available for scripts and
plugins. Deprecated snapshot APIs emit `DeprecationWarning`. Legacy and new
beads can share history and legacy groups; legacy calls inside a new context
join the outer command. Prefer the contexts above for new code.

Built-in core and command callers no longer select an implementation through
`g.new_undoers`; the flag remains for compatibility. Tests that intentionally
exercise both flag values now restore the value after each test. The removed
`insertHeadline(as_child=...)` interface is replaced by the dedicated
`insertChild()` command, or `u.insert_node(p, as_child=True)` for helpers.

Do not rely on the Undoer's legacy snapshot ivars while replaying new beads.
The callbacks capture their own state. Keep external effects outside outline
snapshots, and provide separate callbacks or a dedicated context when those
effects must be reversible.
