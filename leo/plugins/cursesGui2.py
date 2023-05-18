#@+leo-ver=5-thin
#@+node:ekr.20170419092835.1: * @file ../plugins/cursesGui2.py
#@+<< cursesGui2 docstring >>
#@+node:ekr.20170608073034.1: ** << cursesGui2 docstring >>
"""
A curses gui for Leo using npyscreen.

The ``--gui=curses`` command-line option enables this plugin.

**Warnings**

- Leo will crash on startup if the console is not big enough.

- This is beta-level code. Be prepared to recover from data loss. Testing
  on files under git control gives you diffs and easy reverts.

- There are many limitations: see
  https://leo-editor.github.io/leo-editor/console-gui.html

Please report any problem here:
https://github.com/leo-editor/leo-editor/issues/488

Devs, please read:
https://leo-editor.github.io/leo-editor/console-gui.html#developing-the-cursesgui2-plugin
"""
#@-<< cursesGui2 docstring >>
#@+<< cursesGui2 imports >>
#@+node:ekr.20170419172102.1: ** << cursesGui2 imports >>
from __future__ import annotations
import copy
import logging
import logging.handlers
import re
import sys
from typing import Any, Callable, Dict, Generator, List, Optional, Tuple, Union
from typing import TYPE_CHECKING

# Third-party.
try:
    import curses
except ImportError:
    print('cursesGui2.py: curses required.')
    raise
from leo.external import npyscreen
import leo.external.npyscreen.utilNotify as utilNotify
from leo.external.npyscreen.wgwidget import(  # type:ignore
    EXITED_DOWN, EXITED_ESCAPE, EXITED_MOUSE, EXITED_UP)
try:
    from tkinter import Tk
except ImportError:
    print('cursesGui2.py: Tk module required for clipboard handling.')
    raise

# Leo imports
from leo.core import leoGlobals as g
from leo.core import leoFrame
from leo.core import leoGui
from leo.core import leoMenu
from leo.core.leoNodes import Position
#@-<< cursesGui2 imports >>
#@+<< cursesGui2 annotations >>
#@+node:ekr.20220911020102.1: ** << cursesGui2 annotations >>
if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    Event = Any  # Not usually a LeoKeyEvent.
    Wrapper = Any  # Everything, including widgets, is a wrapper!
#@-<< cursesGui2 annotations >>
# pylint: disable=arguments-differ,logging-not-lazy
# pylint: disable=not-an-iterable,unsubscriptable-object,unsupported-delete-operation

# True: use native Leo data structures, replacing the
# the values property by a singleton LeoValues object.
native = True
#@+<< forward reference classes >>
#@+node:ekr.20170511053555.1: **  << forward reference classes >>
# These classes aren't necessarily base classes, but
# they must be defined before classes that refer to them.
#@+others
#@+node:ekr.20170602094648.1: *3* class LeoBodyTextfield (npyscreen.Textfield)
class LeoBodyTextfield(npyscreen.Textfield):
    """
    A class to allow an overridden h_addch for body text.
    MultiLines are *not* Textfields, the *contain* Textfields.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:

        self.leo_parent: Wrapper = None  # Injected later.
        super().__init__(*args, **kwargs)
        self.value: str
        self.set_handlers()

    #@+others
    #@+node:ekr.20170604182251.1: *4* LeoBodyTextfield handlers
    # All h_exit_* methods call self.leo_parent.set_box_name.
    # In addition, h_exit_down inserts a blank(!!) for '\n'.
    #@+node:ekr.20170602095236.1: *5* LeoBodyTextfield.h_addch
    def h_addch(self, ch_i: int) -> None:
        """
        Update a single line of the body text, carefully recomputing c.p.b.
        Also, update v.insertSpot, v.selectionLength, and v.selectionStart.
        """
        trace = False and not g.unitTesting
        if not self.editable:
            if trace:
                g.trace('LeoBodyTextfiedl: not editable')
            return
        parent_w = self.leo_parent
        assert isinstance(parent_w, LeoBody), repr(parent_w)
        c = parent_w.leo_c
        p = c.p
        if trace:
            g.trace('LeoBodyTextfield. row: %s len(p.b): %4s ch_i: %s' % (
                parent_w.cursor_line, len(p.b), ch_i))
        try:
            # Careful: chr can fail.
            ch = g.toUnicode(chr(ch_i))
        except Exception:
            if trace:
                g.es_exception()
            return
        # Update this line...
        i = self.cursor_position
        s = self.value
        self.value = s[:i] + ch + s[i:]
        self.cursor_position += len(ch)
        self.update()
        # Update the parent and Leo's data structures.
        parent_w.update_body(self.cursor_position, self.value)
    #@+node:ekr.20170603131317.1: *5* LeoBodyTextfield.h_cursor_left
    def h_cursor_left(self, ch_i: int) -> None:

        self.cursor_position -= 1  # -1 Means something.

    #@+node:ekr.20170603131253.1: *5* LeoBodyTextfield.h_delete_left
    def h_delete_left(self, ch_i: int) -> None:

        # pylint: disable=no-member
        i = self.cursor_position
        if self.editable and i > 0:
            self.value = self.value[: i - 1] + self.value[i:]
        self.cursor_position -= 1
        self.begin_at -= 1
        # #2642.
        self.update()
        parent_w = self.leo_parent
        parent_w.update_body(self.cursor_position, self.value)
    #@+node:ekr.20170602110807.2: *5* LeoBodyTextfield.h_exit_down
    def h_exit_down(self, ch_i: int) -> Optional[bool]:
        """
        From InputHandler.h_exit_down
        Terminate editing for *this* line, but not overall editing.
        """
        if ch_i in (curses.ascii.CR, curses.ascii.NL):
            # A kludge, but much better than adding a blank.
            self.h_addch(ord('\n'))
            self.cursor_position = 0
        if not self._test_safe_to_exit():
            return False
        # Don't end overall editing.
            # self.leo_parent.set_box_name('Body Pane')
        self.editing = False
        self.how_exited = EXITED_DOWN
        return None
    #@+node:ekr.20170602110807.3: *5* LeoBodyTextfield.h_exit_escape
    def h_exit_escape(self, ch_i: int) -> Optional[bool]:
        """From InputHandler.h_exit_escape"""
        # Leo-specific exit code.
        self.leo_parent.set_box_name('Body Pane')
        # Boilerplate exit code...
        if not self._test_safe_to_exit():
            return False
        self.editing = False
        self.how_exited = EXITED_ESCAPE
        return None
    #@+node:ekr.20170602110807.4: *5* LeoBodyTextfield.h_exit_mouse
    def h_exit_mouse(self, ch_i: int) -> None:
        """From InputHandler.h_exit_mouse"""
        # pylint: disable=no-member
        parent_w = self.leo_parent
        parent_w.set_box_name('Body Pane')
        mouse_event = self.parent.safe_get_mouse_event()
        if mouse_event and self.intersted_in_mouse_event(mouse_event):
            self.handle_mouse_event(mouse_event)
        else:
            if mouse_event and self._test_safe_to_exit():
                curses.ungetmouse(*mouse_event)
                ch = self.parent.curses_pad.getch()
                assert ch == curses.KEY_MOUSE
            self.editing = False
            self.how_exited = EXITED_MOUSE
    #@+node:ekr.20170602110807.5: *5* LeoBodyTextfield.h_exit_up
    def h_exit_up(self, ch_i: int) -> None:
        """LeoBodyTextfield.h_exit_up."""
        # Don't end overall editing.
            # self.leo_parent.set_box_name('Body Pane')
        self.editing = False
        self.how_exited = EXITED_UP
    #@+node:ekr.20170604180351.1: *5* LeoBodyTextfield.set_handlers
    def set_handlers(self) -> None:

        # pylint: disable=no-member
        self.handlers = {
            # From InputHandler...
            curses.ascii.NL: self.h_exit_down,
            curses.ascii.CR: self.h_exit_down,
            curses.KEY_DOWN: self.h_exit_down,
            curses.KEY_UP: self.h_exit_up,  # 2017/06/06.
            curses.ascii.ESC: self.h_exit_escape,
            curses.KEY_MOUSE: self.h_exit_mouse,
            # From Textfield...
            curses.KEY_BACKSPACE: self.h_delete_left,
            curses.KEY_DC: self.h_delete_right,
            curses.KEY_LEFT: self.h_cursor_left,
            curses.KEY_RIGHT: self.h_cursor_right,
            curses.ascii.BS: self.h_delete_left,
            curses.ascii.DEL: self.h_delete_left,
            # New bindings...
            curses.ascii.TAB: self.h_addch,
        }
        # dump_handlers(self)
    #@-others
#@+node:ekr.20170603104320.1: *3* class LeoLogTextfield (npyscreen.Textfield)
class LeoLogTextfield(npyscreen.Textfield):
    """
    A class to allow an overridden h_addch for body text.
    MultiLines are *not* Textfields, the *contain* Textfields.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:

        self.leo_parent: Wrapper = None  # Injected later.
        super().__init__(*args, **kwargs)
        self.set_handlers()

    #@+others
    #@+node:ekr.20170604113445.1: *4* LeoLogTextfield handlers
    # All h_exit_* methods call self.leo_parent.set_box_name.
    # In addition, h_exit_down inserts a blank(!!) for '\n'.
    #@+node:ekr.20170603104320.5: *5* LeoLogTextfield.h_exit_escape
    def h_exit_escape(self, ch_i: int) -> Optional[bool]:
        """From InputHandler.h_exit_escape"""
        parent_w = self.leo_parent
        parent_w.set_box_name('Log Pane')
        if not self._test_safe_to_exit():
            return False
        self.editing = False
        self.how_exited = EXITED_ESCAPE
        return None
    #@+node:ekr.20170603104320.6: *5* LeoLogTextfield.h_exit_mouse
    def h_exit_mouse(self, ch_i: int) -> None:
        """From InputHandler.h_exit_mouse"""
        # pylint: disable=no-member
        parent_w = self.leo_parent
        parent_w.set_box_name('Log Pane')
        mouse_event = self.parent.safe_get_mouse_event()
        if mouse_event and self.intersted_in_mouse_event(mouse_event):
            self.handle_mouse_event(mouse_event)
        else:
            if mouse_event and self._test_safe_to_exit():
                curses.ungetmouse(*mouse_event)
                ch = self.parent.curses_pad.getch()
                assert ch == curses.KEY_MOUSE
            self.editing = False
            self.how_exited = EXITED_MOUSE
    #@+node:ekr.20170603104320.8: *5* LeoLogTextfield.h_exit_down
    def h_exit_down(self, ch_i: int) -> Optional[bool]:
        """LeoLogTextfield.h_exit_up. Delegate to LeoLog."""
        # g.trace('(LeoLogTextfield)', self._test_safe_to_exit())
        if ch_i in (curses.ascii.CR, curses.ascii.NL):
            # A pretty horrible kludge.
            self.h_addch(ord(' '))
            self.cursor_position = 0
        else:
            parent_w = self.leo_parent
            parent_w.set_box_name('Log Pane')
        if not self._test_safe_to_exit():
            return False
        self.editing = False
        self.how_exited = EXITED_DOWN
        return None
    #@+node:ekr.20170603104320.9: *5* LeoLogTextfield.h_exit_up
    def h_exit_up(self, ch_i: int) -> Optional[bool]:
        """LeoLogTextfield.h_exit_up. Delegate to LeoLog."""
        parent_w = self.leo_parent
        if not self._test_safe_to_exit():
            return False
        parent_w.set_box_name('Log Pane')
        self.editing = False
        self.how_exited = EXITED_DOWN
        return None
    #@+node:ekr.20170604075324.1: *4* LeoLogTextfield.set_handlers
    def set_handlers(self) -> None:

        # pylint: disable=no-member
        self.handlers = {
            # From InputHandler...
            curses.ascii.NL: self.h_exit_down,
            curses.ascii.CR: self.h_exit_down,
            curses.KEY_DOWN: self.h_exit_down,
            curses.KEY_UP: self.h_exit_up,  # 2017/06/06.
            curses.ascii.ESC: self.h_exit_escape,
            curses.KEY_MOUSE: self.h_exit_mouse,
            # From Textfield...
            curses.KEY_BACKSPACE: self.h_delete_left,
            curses.KEY_DC: self.h_delete_right,
            curses.KEY_LEFT: self.h_cursor_left,
            curses.KEY_RIGHT: self.h_cursor_right,
            curses.ascii.BS: self.h_delete_left,
            curses.ascii.DEL: self.h_delete_left,
            # New bindings...
            curses.ascii.TAB: self.h_addch,
        }
        # dump_handlers(self)
    #@-others
#@+node:ekr.20170507184329.1: *3* class LeoTreeData (npyscreen.TreeData)
class LeoTreeData(npyscreen.TreeData):
    """A TreeData class that has a len and new_first_child methods."""
    #@+<< about LeoTreeData ivars >>
    #@+node:ekr.20170516143500.1: *4* << about LeoTreeData ivars >>
    # EKR: TreeData.__init__ sets the following ivars for keyword args.
        # self._parent # None or weakref.proxy(parent)
        # self.content.
        # self.selectable = selectable
        # self.selected = selected
        # self.highlight = highlight
        # self.expanded = expanded
        # self._children = []
        # self.ignore_root = ignore_root
        # self.sort = False
        # self.sort_function = sort_function
        # self.sort_function_wrapper = True
    #@-<< about LeoTreeData ivars >>

    _children: List["LeoTreeData"]
    content = Union[str, Position]

    def __len__(self) -> int:
        if native:
            p = self.content
            assert p and isinstance(p, Position), repr(p)
            content = p.h
        else:
            content = self.content
        return len(content)

    def __repr__(self) -> str:
        if native:
            p = self.content
            assert p and isinstance(p, Position), repr(p)
            return '<LeoTreeData: %s, %s>' % (id(p), p.h)
        return '<LeoTreeData: %r>' % self.content
    __str__ = __repr__

    #@+others
    #@+node:ekr.20170516153211.1: *4* LeoTreeData.__getitem__
    def __getitem__(self, n: int) -> "LeoTreeData":
        """Return the n'th item in this tree."""
        aList = self.get_tree_as_list()
        data = aList[n] if n < len(aList) else None
        # g.trace(n, len(aList), repr(data))
        return data
    #@+node:ekr.20170516093009.1: *4* LeoTreeData.is_ancestor_of
    def is_ancestor_of(self, node: "LeoTreeData") -> bool:

        assert isinstance(node, LeoTreeData), repr(node)
        parent = node._parent
        while parent:
            if parent == self:
                return True
            parent = parent._parent
        return False
    #@+node:ekr.20170516085427.1: *4* LeoTreeData.overrides
    # Don't use weakrefs!
    #@+node:ekr.20170518103807.6: *5* LeoTreeData.find_depth
    def find_depth(self, d: int=0) -> int:
        if native:
            p = self.content
            n = p.level()
            return n
        parent = self.get_parent()
        while parent:
            d += 1
            parent = parent.get_parent()
        return d
    #@+node:ekr.20170516085427.2: *5* LeoTreeData.get_children
    def get_children(self) -> List["LeoTreeData"]:

        if native:
            p = self.content
            return p.children()
        return self._children
    #@+node:ekr.20170518103807.11: *5* LeoTreeData.get_parent
    def get_parent(self) -> Position:

        if native:
            p = self.content
            return p.parent()
        return self._parent
    #@+node:ekr.20170516085427.3: *5* LeoTreeData.get_tree_as_list
    def get_tree_as_list(self) -> List["LeoTreeData"]:  # only_expanded=True, sort=None, key=None):
        """
        Called only from LeoMLTree.values._getValues.

        Return the result of converting this node and its *visible* descendants
        to a list of LeoTreeData nodes.
        """
        assert g.callers(1) == '_getValues', g.callers()
        aList = [z for z in self.walk_tree(only_expanded=True)]
        # g.trace('LeoTreeData', len(aList))
        return aList
    #@+node:ekr.20170516085427.4: *5* LeoTreeData.new_child
    def new_child(self, *args: Any, **keywords: Any) -> Position:

        if self.CHILDCLASS:
            cld = self.CHILDCLASS
        else:
            cld = type(self)
        child = cld(parent=self, *args, **keywords)
        self._children.append(child)
        return child
    #@+node:ekr.20170516085742.1: *5* LeoTreeData.new_child_at
    def new_child_at(self, index: int, *args: Any, **keywords: Any) -> Position:
        """Same as new_child, with insert(index, c) instead of append(c)"""
        # g.trace('LeoTreeData')
        if self.CHILDCLASS:
            cld = self.CHILDCLASS
        else:
            cld = type(self)
        child = cld(parent=self, *args, **keywords)
        self._children.insert(index, child)
        return child
    #@+node:ekr.20170516085427.5: *5* LeoTreeData.remove_child
    def remove_child(self, child: Position) -> None:

        if native:
            p = self.content
            # g.trace('LeoTreeData', p.h, g.callers())
            p.doDelete()
        else:
            # May be useful when child is cloned.
            self._children = [z for z in self._children if z != child]
    #@+node:ekr.20170518103807.21: *5* LeoTreeData.set_content
    def set_content(self, content: Union[str, Position]) -> None:

        if native:
            if content is None:
                self.content = None
            elif isinstance(content, str):
                # This is a dummy node, not actually used.
                assert content == '<HIDDEN>', repr(content)
                self.content = content
            else:
                p = content
                assert p and isinstance(p, Position), repr(p)
                self.content = content.copy()
        else:
            self.content = content
    #@+node:ekr.20170516085427.6: *5* LeoTreeData.set_parent
    def set_parent(self, parent: Position) -> None:

        self._parent = parent

    #@+node:ekr.20170518103807.24: *5* LeoTreeData.walk_tree (native only)
    if native:

        def walk_tree(
            self,
            only_expanded: bool=True,
            ignore_root: bool=True,
            sort: bool=None,  # not used here.
            sort_function: Callable=None,
        ) -> Generator:
            # Never change the stored position!
            # LeoTreeData(p) makes a copy of p.
            p = self.content.copy()
            if not ignore_root:
                yield self  # The hidden root. Probably not needed.
            if only_expanded:
                while p:
                    if p.has_children() and p.isExpanded():
                        p.moveToFirstChild()
                        yield LeoTreeData(p)
                    elif p.next():
                        p.moveToNext()
                        yield LeoTreeData(p)
                    elif p.parent():
                        p.moveToParent()
                        yield LeoTreeData(p)
                    else:
                        return  # raise StopIteration
            else:
                while p:
                    yield LeoTreeData(p)
                    p.moveToThreadNext()

    # else use the base TreeData.walk_tree method.
    #@-others
#@+node:ekr.20170508085942.1: *3* class LeoTreeLine (npyscreen.TreeLine)
class LeoTreeLine(npyscreen.TreeLine):
    """A editable TreeLine class."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:

        self.leo_c = None  # Injected later.
        super().__init__(*args, **kwargs)
        # Done in TreeLine.init:
            # self._tree_real_value   = None
                # A weakproxy to LeoTreeData.
            # self._tree_ignore_root  = None
            # self._tree_depth        = False
            # self._tree_sibling_next = False
            # self._tree_has_children = False
            # self._tree_expanded     = True
            # self._tree_last_line    = False
            # self._tree_depth_next   = False
            # self.safe_depth_display = False
            # self.show_v_lines       = True
        self.set_handlers()

    def __repr__(self) -> str:
        val = self._tree_real_value
        if native:
            p = val and val.content
            if p is not None:
                assert p and isinstance(p, Position), repr(p)
            return '<LeoTreeLine: %s>' % (p.h if p else 'None')
        return '<LeoTreeLine: %s>' % (val.content if val else 'None')

    __str__ = __repr__

    #@+others
    #@+node:ekr.20170514104550.1: *4* LeoTreeLine._get_string_to_print
    def _get_string_to_print(self) -> Optional[str]:

        # From TextfieldBase.
        if native:
            if self.value:
                assert isinstance(self.value, LeoTreeData)
                p = self.value.content
                assert p and isinstance(p, Position), repr(p)
                return p.h or ' '
            return ''
        s = self.value.content if self.value else None
        return g.toUnicode(s) if s else None
    #@+node:ekr.20170522032805.1: *4* LeoTreeLine._print
    def _print(self, left_margin: int=0) -> None:
        """LeoTreeLine._print. Adapted from TreeLine._print."""
        # pylint: disable=no-member

        def put(char: str) -> None:
            self.parent.curses_pad.addch(
                self.rely, self.relx + self.left_margin,
                ord(char), curses.A_NORMAL)
            self.left_margin += 1

        self.left_margin = left_margin
        self.parent.curses_pad.bkgdset(' ', curses.A_NORMAL)
        if native:
            c = getattr(self, 'leo_c', None)
            val = self._tree_real_value
            if val is None:
                return  # startup
            p = val.content
            assert isinstance(p, Position), repr(p)
            self.left_margin += 2 * p.level()
            if p.hasChildren():
                put('-' if p.isExpanded() else '+')
            else:
                put(' ')
            put(':')
            put('*' if c and p == c.p else ' ')
            put('C' if p and p.isCloned() else ' ')
            put('M' if p and p.isMarked() else ' ')
            put('T' if p and p.b.strip() else ' ')
            put(':')
        else:
            self.left_margin += self._print_tree(self.relx)
        # Now draw the actual line.
        if self.highlight:
            self.parent.curses_pad.bkgdset(' ', curses.A_STANDOUT)
        # This draws the actual line.
        super()._print()
    #@+node:ekr.20170514183049.1: *4* LeoTreeLine.display_value
    def display_value(self, vl: "LeoTreeData") -> str:

        # vl is a LeoTreeData.
        if native:
            p = vl.content
            assert p and isinstance(p, Position), repr(p)
            return p.h or ' '
        return vl.content if vl else ''
    #@+node:ekr.20170510210908.1: *4* LeoTreeLine.edit
    def edit(self) -> None:
        """Allow the user to edit the widget: ie. start handling keypresses."""
        # g.trace('LeoTreeLine 1')
        self.editing = True
        # self._pre_edit()
        self.highlight = True
        self.how_exited = False
        # self._edit_loop()
        old_parent_editing = self.parent.editing
        self.parent.editing = True
        while self.editing and self.parent.editing:
            self.display()
            self.get_and_use_key_press()  # A base TreeLine method.
        self.parent.editing = old_parent_editing
        self.editing = False
        self.how_exited = True
        # return self._post_edit()
        self.highlight = False
        self.update()
    #@+node:ekr.20170508130016.1: *4* LeoTreeLine.handlers
    #@+node:ekr.20170508130946.1: *5* LeoTreeLine.h_cursor_beginning
    def h_cursor_beginning(self, ch: str) -> None:

        self.cursor_position = 0
    #@+node:ekr.20170508131043.1: *5* LeoTreeLine.h_cursor_end
    def h_cursor_end(self, ch: str) -> None:

        # self.value is a LeoTreeData.
        # native: content is a position.
        content = self.value.content
        s = content.h if native else content
        self.cursor_position = max(0, len(s) - 1)
    #@+node:ekr.20170508130328.1: *5* LeoTreeLine.h_cursor_left
    def h_cursor_left(self, input: Any) -> None:  # input not used.

        # self.value is a LeoTreeData.
        # native: content is a position.
        content = self.value.content
        s = content.h if native else content
        i = min(self.cursor_position, len(s) - 1)
        self.cursor_position = max(0, i - 1)
    #@+node:ekr.20170508130339.1: *5* LeoTreeLine.h_cursor_right
    def h_cursor_right(self, input: Any) -> None:  # input not used.

        # self.value is a LeoTreeData.
        # native: content is a position.
        content = self.value.content
        s = content.h if native else content
        i = self.cursor_position
        i = min(i + 1, len(s) - 1)
        self.cursor_position = max(0, i)



    #@+node:ekr.20170508130349.1: *5* LeoTreeLine.h_delete_left
    def h_delete_left(self, input: Any) -> None:  # input not used.

        # self.value is a LeoTreeData.
        n = self.cursor_position
        if native:
            p = self.value.content
            assert p and isinstance(p, Position), repr(p)
            s = p.h
            if 0 <= n <= len(s):
                c = p.v.context
                h = s[:n] + s[n + 1 :]
                # Sets p.h and handles undo.
                c.frame.tree.onHeadChanged(p, s=h, undoType='Typing')
        else:
            s = self.value.content
            if 0 <= n <= len(s):
                self.value.content = s[:n] + s[n + 1 :]
        self.cursor_position -= 1
    #@+node:ekr.20170510212007.1: *5* LeoTreeLine.h_end_editing
    def h_end_editing(self, ch: str) -> None:

        c = self.leo_c
        c.endEditing()
        self.editing = False
        self.how_exited = None
    #@+node:ekr.20170508125632.1: *5* LeoTreeLine.h_insert (to do: honor v.selection)
    def h_insert(self, i: int) -> None:

        # self.value is a LeoTreeData.
        n = self.cursor_position + 1
        if native:
            p = self.value.content
            c = p.v.context
            s = p.h
            h = s[:n] + chr(i) + s[n:]
            # Sets p.h and handles undo.
            c.frame.tree.onHeadChanged(p, s=h, undoType='Typing')
        else:
            s = self.value.content
            self.value.content = s[:n] + chr(i) + s[n:]
        self.cursor_position += 1
    #@+node:ekr.20170508130025.1: *5* LeoTreeLine.set_handlers
    #@@nobeautify

    def set_handlers(self) -> None:

        # pylint: disable=no-member
        # Override *all* other complex handlers.
        self.complex_handlers = (
            (curses.ascii.isprint, self.h_insert),
        )
        self.handlers.update({
            curses.ascii.ESC:       self.h_end_editing,
            curses.ascii.NL:        self.h_end_editing,
            curses.ascii.LF:        self.h_end_editing,
            curses.KEY_HOME:        self.h_cursor_beginning,  # 262
            curses.KEY_END:         self.h_cursor_end,        # 358.
            curses.KEY_LEFT:        self.h_cursor_left,
            curses.KEY_RIGHT:       self.h_cursor_right,
            curses.ascii.BS:        self.h_delete_left,
            curses.KEY_BACKSPACE:   self.h_delete_left,
            curses.KEY_MOUSE:       self.h_exit_mouse, # New
        })
    #@+node:ekr.20170519023802.1: *4* LeoTreeLine.when_check_value_changed
    if native:

        def when_check_value_changed(self) -> bool:
            """Check whether the widget's value has changed and call when_valued_edited if so."""
            return True
    #@-others
#@+node:ekr.20170618103742.1: *3* class QuitButton (npyscreen.MiniButton)
class QuitButton(npyscreen.MiniButtonPress):
    """Override the "Quit Leo" button so it prompts for save if needed."""

    def whenPressed(self) -> None:

        # #2467.
        # Similar to qt_gui.close_event.
        for c in g.app.commanders():
            allow = c.exists and g.app.closeLeoWindow(c.frame)
            if not allow:
                return
        sys.exit(0)
#@-others
#@-<< forward reference classes >>
#@+others
#@+node:ekr.20170501043944.1: **   curses2: top-level functions
#@+node:ekr.20170603110639.1: *3* curses2: dump_handlers
def dump_handlers(
    obj: Any,
    dump_complex: bool=True,
    dump_handlers: bool=True,
    dump_keys: bool=True,
) -> None:
    tag = obj.__class__.__name__
    if dump_keys:
        g.trace('%s: keys' % tag)
        aList = []
        for z in obj.handlers:
            kind = repr(chr(z)) if isinstance(z, int) and 32 <= z < 127 else ''
            name = method_name(obj.handlers.get(z))
            aList.append('%3s %3s %4s %s' % (z, type(z).__name__, kind, name))
        g.printList(sorted(aList))
    if dump_handlers:
        g.trace('%s: handlers' % tag)
        aList = [method_name(obj.handlers.get(z))
            for z in obj.handlers]
        g.printList(sorted(set(aList)))
    if dump_complex:
        g.trace('%s: complex_handlers' % tag)
        aList = []
        for data in obj.complex_handlers:
            f1, f2 = data
            aList.append('%25s predicate: %s' % (method_name(f2), method_name(f1)))
        g.printList(sorted(set(aList)))
#@+node:ekr.20170419094705.1: *3* curses2: init
def init() -> bool:
    """
    top-level init for cursesGui2.py pseudo-plugin.
    This plugin should be loaded only from leoApp.py.
    """
    if g.app.gui:
        if not g.unitTesting:
            s = "Can't install text gui: previous gui installed"
            g.es_print(s, color="red")
        return False
    return bool(curses and not g.unitTesting)  # Not Ok for unit testing!
#@+node:ekr.20170501032705.1: *3* curses2: leoGlobals replacements
# CGui.init_logger monkey-patches leoGlobals with these functions.
#@+node:ekr.20170430112645.1: *4* curses2: es
def es(*args: Any, **keys: Any) -> None:
    """Monkey-patch for g.es."""
    d = {
        'color': None,
        'commas': False,
        'newline': True,
        'spaces': True,
        'tabName': 'Log',
    }
    d = g.doKeywordArgs(keys, d)
    color = d.get('color')
    s = g.translateArgs(args, d)
    if isinstance(g.app.gui, LeoCursesGui):
        if g.app.gui.log_inited:
            g.app.gui.log.put(s, color=color)
        else:
            g.app.gui.wait_list.append((s, color))
    # else: logging.info(' KILL: %r' % s)
#@+node:ekr.20170613144149.1: *4* curses2: has_logger (not used)
def has_logger() -> bool:

    logger = logging.getLogger()
    return any(isinstance(z, logging.handlers.SocketHandler) for z in logger.handlers or [])
#@+node:ekr.20170501043411.1: *4* curses2: pr
def pr(*args: Any, **keys: Any) -> None:
    """Monkey-patch for g.pr."""
    d = {'commas': False, 'newline': True, 'spaces': True}
    d = g.doKeywordArgs(keys, d)
    s = g.translateArgs(args, d)
    for line in g.splitLines(s):
        if line.strip():  # No need to print blank logging lines.
            line = '   pr: %s' % line.rstrip()
            logging.info(line)
#@+node:ekr.20170429165242.1: *4* curses2: trace
def trace(*args: Any, **keys: Any) -> None:
    """Monkey-patch for g.trace."""
    d: Dict[str, Any] = {
        'align': 0,
        'before': '',
        'newline': True,
        'caller_level': 1,
        'noname': False,
    }
    name: str
    d = g.doKeywordArgs(keys, d)
    align: int = d.get('align', 0)
    caller_level: int = d.get('caller_level', 1)
    # Compute the caller name.
    if d.get('noname'):
        name = ''
    else:
        try:  # get the function name from the call stack.
            f1 = sys._getframe(caller_level)  # The stack frame, one level up.
            code1 = f1.f_code  # The code object
            name = code1.co_name  # The code name
        except Exception:
            name = g.shortFileName(__file__)
        if name == '<module>':
            name = g.shortFileName(__file__)
        if name.endswith('.pyc'):
            name = name[:-1]
    # Pad the caller name.
    if align != 0 and len(name) < abs(align):
        pad = ' ' * (abs(align) - len(name))
        if align > 0:
            name = name + pad
        else:
            name = pad + name
    # Munge *args into s.
    result = [name] if name else []
    for arg in args:
        if isinstance(arg, str):
            pass
        elif isinstance(arg, bytes):
            arg = g.toUnicode(arg)
        else:
            arg = repr(arg)
        if result:
            result.append(" " + arg)
        else:
            result.append(arg)
    s = ''.join(result)
    line = 'trace: %s' % s.rstrip()
    logging.info(line)
#@+node:ekr.20170526075024.1: *3* method_name
def method_name(f: Callable) -> str:
    """Print a method name is a simplified format."""
    pattern = r'<bound method ([\w\.]*\.)?(\w+) of <([\w\.]*\.)?(\w+) object at (.+)>>'
    m = re.match(pattern, repr(f))
    if m:
        # Shows actual method: very useful
        return '%20s%s' % (m.group(1), m.group(2))
    return repr(f)
#@+node:ekr.20210228141208.1: **  decorators (curses2)
def frame_cmd(name: str) -> Callable:
    """Command decorator for the LeoFrame class."""
    return g.new_cmd_decorator(name, ['c', 'frame',])

def log_cmd(name: str) -> Callable:
    """Command decorator for the c.frame.log class."""
    return g.new_cmd_decorator(name, ['c', 'frame', 'log'])
#@+node:ekr.20170524123950.1: ** Gui classes
#@+node:ekr.20171128051435.1: *3* class StringFindTabManager(cursesGui2.py)
class StringFindTabManager:
    """CursesGui.py: A string-based FindTabManager class."""
    # A complete rewrite of the FindTabManager in qt_frame.py.
    #@+others
    #@+node:ekr.20171128051435.2: *4*  sftm.ctor
    def __init__(self, c: Cmdr) -> None:
        """Ctor for the StringFindTabManager class."""
        self.c: Cmdr = c
        assert c.findCommands
        c.findCommands.minibuffer_mode = True
        self.entry_focus: Wrapper = None  # The widget that had focus before find-pane entered.
        # Find/change text boxes.
        self.find_findbox: Wrapper = None
        self.find_replacebox: Wrapper = None
        # Check boxes.
        self.check_box_ignore_case: bool = None
        self.check_box_mark_changes: bool = None
        self.check_box_mark_finds: bool = None
        self.check_box_regexp: bool = None
        self.check_box_search_body: bool = None
        self.check_box_search_headline: bool = None
        self.check_box_whole_word: bool = None
        # self.check_box_wrap_around = None
        # Radio buttons
        self.radio_button_entire_outline: bool = None
        self.radio_button_file_only: bool = None
        self.radio_button_node_only: bool = None
        self.radio_button_suboutline_only: bool = None
        # Push buttons
        self.find_next_button: Wrapper = None
        self.find_prev_button: Wrapper = None
        self.find_all_button: Wrapper = None
        self.help_for_find_commands_button: Wrapper = None
        self.replace_button: Wrapper = None
        self.replace_then_find_button: Wrapper = None
        self.replace_all_button: Wrapper = None
    #@+node:ekr.20171128051435.3: *4* sftm.text getters/setters
    def get_find_text(self) -> str:
        return g.toUnicode(self.find_findbox.text())

    def get_change_text(self) -> str:
        return g.toUnicode(self.find_replacebox.text())

    def set_find_text(self, s: str) -> None:
        w = self.find_findbox
        s = g.toUnicode(s)
        w.clear()
        w.insert(s)

    def set_change_text(self, s: str) -> None:
        w = self.find_replacebox
        s = g.toUnicode(s)
        w.clear()
        w.insert(s)
    #@+node:ekr.20171128051435.4: *4* sftm.*_focus
    def clear_focus(self) -> None:
        pass

    def init_focus(self) -> None:
        pass

    def set_entry_focus(self) -> None:
        pass
    #@+node:ekr.20171128051435.5: *4* sftm.set_ignore_case
    def set_ignore_case(self, aBool: bool) -> None:
        """Set the ignore-case checkbox to the given value."""
        c = self.c
        c.findCommands.ignore_case = aBool
        w = self.check_box_ignore_case
        w.setChecked(aBool)
    #@+node:ekr.20171128051435.6: *4* sftm.init_widgets
    def init_widgets(self) -> None:
        """
        Init widgets and ivars from c.config settings.
        Create callbacks that always keep the LeoFind ivars up to date.
        """
        c = self.c
        find = c.findCommands
        # Find/change text boxes.
        table = (
            ('find_findbox', 'find_text', '<find pattern here>'),
            ('find_replacebox', 'change_text', ''),
        )
        for ivar, setting_name, default in table:
            s = c.config.getString(setting_name) or default
            w = getattr(self, ivar)
            w.insert(s)
        # Check boxes.
        table1 = (
            ('ignore_case', self.check_box_ignore_case),
            ('mark_changes', self.check_box_mark_changes),
            ('mark_finds', self.check_box_mark_finds),
            ('pattern_match', self.check_box_regexp),
            ('search_body', self.check_box_search_body),
            ('search_headline', self.check_box_search_headline),
            ('whole_word', self.check_box_whole_word),
            # ('wrap', self.check_box_wrap_around),
        )
        for setting_name, w in table1:
            val = c.config.getBool(setting_name, default=False)
            # The setting name is also the name of the LeoFind ivar.
            assert hasattr(find, setting_name), setting_name
            setattr(find, setting_name, val)
            if val:
                w.toggle()

            def check_box_callback(n: int, setting_name: str=setting_name, w: Wrapper=w) -> None:
                val = w.isChecked()
                assert hasattr(find, setting_name), setting_name
                setattr(find, setting_name, val)

        # Radio buttons
        table2 = (
            ('entire_outline', None, self.radio_button_entire_outline),
            ('file_only', 'file_only', self.radio_button_file_only),
            ('node_only', 'node_only', self.radio_button_node_only),
            ('suboutline_only', 'suboutline_only', self.radio_button_suboutline_only),
        )
        for setting_name, ivar, w in table2:
            val = c.config.getBool(setting_name, default=False)
            # The setting name is also the name of the LeoFind ivar.
            if ivar is not None:
                assert hasattr(find, setting_name), setting_name
                setattr(find, setting_name, val)
                w.toggle()

            def radio_button_callback(n: int, ivar: str=ivar, setting_name: str=setting_name, w: Wrapper=w) -> None:
                val = w.isChecked()
                if ivar:
                    assert hasattr(find, ivar), ivar
                    setattr(find, ivar, val)

        # Ensure one radio button is set.
        if not find.node_only and not find.suboutline_only:
            w = self.radio_button_entire_outline
            w.toggle()
    #@+node:ekr.20171128051435.7: *4* sftm.set_radio_button
    #@@nobeautify

    def set_radio_button(self, name: str) -> None:
        """Set the value of the radio buttons"""
        c = self.c
        fc = c.findCommands
        d = {
            # commandName       fc.ivar            # radio button.
            'entire-outline':  (None,              self.radio_button_entire_outline),
            'file-only':       ('file_only',       self.radio_button_file_only),
            'node-only':       ('node_only',       self.radio_button_node_only),
            'suboutline-only': ('suboutline_only', self.radio_button_suboutline_only),
        }
        ivar, w = d.get(name)
        assert w, repr(w)
        if not w.isChecked():
            w.toggle() # This just sets the radio button's value.
        # First, clear the ivars.
        fc.node_only = False
        fc.suboutline_only = False
        # Next, set the ivar.
        if ivar:
            setattr(fc, ivar, True)

    #@+node:ekr.20171128051435.8: *4* sftm.toggle_checkbox
    #@@nobeautify

    def toggle_checkbox(self, checkbox_name: str) -> None:
        """Toggle the value of the checkbox whose name is given."""
        c = self.c
        fc = c.findCommands
        if not fc:
            return
        d = {
            'ignore_case':     self.check_box_ignore_case,
            'mark_changes':    self.check_box_mark_changes,
            'mark_finds':      self.check_box_mark_finds,
            'pattern_match':   self.check_box_regexp,
            'search_body':     self.check_box_search_body,
            'search_headline': self.check_box_search_headline,
            'whole_word':      self.check_box_whole_word,
            # 'wrap':            self.check_box_wrap_around,
        }
        w = d.get(checkbox_name)
        assert w, repr(w)
        assert hasattr(fc, checkbox_name),checkbox_name
        setattr(fc, checkbox_name, not getattr(fc, checkbox_name))
        w.toggle() # Only toggles w's internal value.
        # g.trace(checkbox_name, getattr(fc, checkbox_name, None))
    #@-others
#@+node:edward.20170428174322.1: *3* class KeyEvent
class KeyEvent:
    """A gui-independent wrapper for gui events."""
    #@+others
    #@+node:edward.20170428174322.2: *4* KeyEvent.__init__
    def __init__(
        self,
        c: Cmdr,
        char: str,
        event: Event,
        shortcut: str,
        w: Wrapper,
        x: int=None,
        y: int=None,
        x_root: Position=None,
        y_root: Position=None,
    ) -> None:
        """Ctor for KeyEvent class."""
        assert not g.isStroke(shortcut), g.callers()
        stroke = g.KeyStroke(shortcut) if shortcut else None
        # g.trace('KeyEvent: stroke', stroke)
        self.c = c
        self.char = char or ''
        self.event = event
        self.stroke = stroke
        self.w = self.widget = w
        # Optional ivars
        self.x: int = x
        self.y: int = y
        # Support for fastGotoNode plugin
        self.x_root: Position = x_root
        self.y_root: Position = y_root
    #@+node:edward.20170428174322.3: *4* KeyEvent.__repr__
    def __repr__(self) -> str:
        return 'KeyEvent: stroke: %s, char: %s, w: %s' % (
            repr(self.stroke), repr(self.char), repr(self.w))
    #@+node:edward.20170428174322.4: *4* KeyEvent.get & __getitem__
    def get(self, attr: str) -> Any:
        """Compatibility with g.bunch: return an attr."""
        return getattr(self, attr, None)

    def __getitem__(self, attr: str) -> Any:
        """Compatibility with g.bunch: return an attr."""
        return getattr(self, attr, None)
    #@+node:edward.20170428174322.5: *4* KeyEvent.type
    def type(self) -> str:
        return 'KeyEvent'
    #@-others
#@+node:ekr.20170430114840.1: *3* class KeyHandler
class KeyHandler:

    #@+others
    #@+node:ekr.20170430114930.1: *4* CKey.do_key & helpers
    def do_key(self, ch_i: int) -> bool:
        """
        Handle a key event by calling k.masterKeyHandler.
        Return True if the event was completely handled.
        """
        #  This is a rewrite of LeoQtEventFilter code.
        c = g.app.log and g.app.log.c
        k = c and c.k
        if not c:
            return True  # We are shutting down.
        if self.is_key_event(ch_i):
            try:
                ch = chr(ch_i)
            except Exception:
                ch = '<no ch>'
            char, shortcut = self.to_key(ch_i)
            if g.app.gui.in_dialog:
                if 0:
                    g.trace('(CKey) dialog key', ch)
            elif shortcut:
                try:
                    w = c.frame.body.wrapper
                    event = self.create_key_event(c, w, char, shortcut)
                    k.masterKeyHandler(event)
                except Exception:
                    g.es_exception()
            g.app.gui.show_label(c)
            return bool(shortcut)
        g.app.gui.show_label(c)
        return False
    #@+node:ekr.20170430115131.4: *5* CKey.char_to_tk_name
    tk_dict = {
        # Part 1: same as g.app.guiBindNamesDict
        "&": "ampersand",
        "^": "asciicircum",
        "~": "asciitilde",
        "*": "asterisk",
        "@": "at",
        "\\": "backslash",
        "|": "bar",
        "{": "braceleft",
        "}": "braceright",
        "[": "bracketleft",
        "]": "bracketright",
        ":": "colon",
        ",": "comma",
        "$": "dollar",
        "=": "equal",
        "!": "exclam",
        ">": "greater",
        "<": "less",
        "-": "minus",
        "#": "numbersign",
        '"': "quotedbl",
        "'": "quoteright",
        "(": "parenleft",
        ")": "parenright",
        "%": "percent",
        ".": "period",
        "+": "plus",
        "?": "question",
        "`": "quoteleft",
        ";": "semicolon",
        "/": "slash",
        " ": "space",
        "_": "underscore",
    }

    def char_to_tk_name(self, ch: str) -> str:
        return self.tk_dict.get(ch, ch)
    #@+node:ekr.20170430115131.2: *5* CKey.create_key_event
    def create_key_event(self, c: Cmdr, w: Wrapper, ch: str, binding: str) -> Event:
        trace = False
        # Last-minute adjustments...
        if binding == 'Return':
            ch = '\n'  # Somehow Qt wants to return '\r'.
        elif binding == 'Escape':
            ch = 'Escape'
        # Switch the Shift modifier to handle the cap-lock key.
        if isinstance(ch, int):
            g.trace('can not happen: ch: %r binding: %r' % (ch, binding))
        elif (
            ch and len(ch) == 1 and
            binding and len(binding) == 1 and
            ch.isalpha() and binding.isalpha()
        ):
            if ch != binding:
                if trace:
                    g.trace('caps-lock')
                binding = ch
        if trace:
            g.trace('ch: %r, binding: %r' % (ch, binding))
        return leoGui.LeoKeyEvent(
            c=c,
            char=ch,
            event={'c': c, 'w': w},  # type:ignore
            binding=binding,
            w=w, x=0, y=0, x_root=0, y_root=0,
        )
    #@+node:ekr.20170430115030.1: *5* CKey.is_key_event
    def is_key_event(self, ch_i: int) -> bool:
        # pylint: disable=no-member
        return ch_i not in (curses.KEY_MOUSE,)
    #@+node:ekr.20170430115131.3: *5* CKey.to_key
    def to_key(self, i: int) -> Tuple[str, str]:
        """Convert int i to a char and shortcut."""
        trace = False
        a = curses.ascii
        char, shortcut = '', ''
        s = a.unctrl(i)
        if i <= 32:
            d = {
                8: 'Backspace', 9: 'Tab',
                10: 'Return', 13: 'Linefeed',
                27: 'Escape', 32: ' ',
            }
            shortcut = d.get(i, '')
            # All real ctrl keys lie between 1 and 26.
            if shortcut and shortcut != 'Escape':
                char = chr(i)
            elif len(s) >= 2 and s.startswith('^'):
                shortcut = 'Ctrl+' + self.char_to_tk_name(s[1:].lower())
        elif i == 127:
            pass
        elif i < 128:
            char = shortcut = chr(i)
            if char.isupper():
                shortcut = 'Shift+' + char
            else:
                shortcut = self.char_to_tk_name(char)
        elif 265 <= i <= 276:
            # Special case for F-keys
            shortcut = 'F%s' % (i - 265 + 1)
        elif i == 351:
            shortcut = 'Shift+Tab'
        elif s.startswith('\\x'):
            pass
        elif len(s) >= 3 and s.startswith('!^'):
            shortcut = 'Alt+' + self.char_to_tk_name(s[2:])
        else:
            pass
        if trace:
            g.trace('i: %s s: %s char: %r shortcut: %r' % (i, s, char, shortcut))
        return char, shortcut
    #@-others
#@+node:ekr.20170419094731.1: *3* class LeoCursesGui (leoGui.LeoGui)
class LeoCursesGui(leoGui.LeoGui):
    """
    Leo's curses gui wrapper.
    This is g.app.gui, when --gui=curses.
    """

    #@+others
    #@+node:ekr.20171128041849.1: *4* CGui.Birth & death
    #@+node:ekr.20170608112335.1: *5* CGui.__init__
    def __init__(self) -> None:
        """Ctor for the CursesGui class."""
        super().__init__('curses')  # Init the base class.
        self.consoleOnly: bool = False  # Required attribute.
        self.curses_app: Wrapper = None  # The singleton LeoApp instance.
        # The top-level curses Form instance. Form.editw is the widget with focus.
        self.curses_form: Wrapper = None
        self.curses_gui_arg: str = None  # A hack for interfacing with k.getArg.
        self.in_dialog: bool = False  # True: executing a modal dialog.
        self.log: Wrapper = None  # The present log. Used by g.es
        self.log_inited: bool = False  # True: don't use the wait_list.
        self.minibuffer_label: str = ''  # The label set by k.setLabel.
        self.wait_list: List[Tuple[str, Any]] = []  # Queued log messages.
        # Do this as early as possible. It monkey-patches g.pr and g.trace.
        self.init_logger()
        self.top_form: Wrapper = None  # The top-level form. Set in createCursesTop.
        self.key_handler = KeyHandler()
    #@+node:ekr.20170502083158.1: *5* CGui.createCursesTop & helpers
    def createCursesTop(self) -> Wrapper:
        """Create the top-level curses Form."""
        trace = False and not g.unitTesting
        # Assert the key relationships required by the startup code.
        assert self == g.app.gui
        c = g.app.log.c
        assert c == g.app.windowList[0].c
        assert isinstance(c.frame, CoreFrame), repr(c.frame)
        if trace:
            g.trace('commanders in g.app.windowList')
            g.printList([z.c.shortFileName() for z in g.app.windowList])
        # Create the top-level form.
        self.curses_form = form = LeoForm(name='Dummy Name')  # This call clears the screen.
        self.createCursesLog(c, form)
        self.createCursesTree(c, form)
        self.createCursesBody(c, form)
        self.createCursesMinibuffer(c, form)
        self.createCursesStatusLine(c, form)
        self.monkeyPatch(c)
        self.redraw_in_context(c)
        c.frame.tree.set_status_line(c.p)
        # self.focus_to_body(c)
        return form
    #@+node:ekr.20170502084106.1: *6* CGui.createCursesBody
    def createCursesBody(self, c: Cmdr, form: Wrapper) -> None:
        """
        Create the curses body widget in the given curses Form.
        Populate it with c.p.b.
        """
        trace = False

        class BoxTitleBody(npyscreen.BoxTitle):
            # pylint: disable=used-before-assignment
            _contained_widget = LeoBody
            how_exited = None

        box = form.add(
            BoxTitleBody,
            max_height=8,  # Subtract 4 lines
            name='Body Pane',
            footer="Press e to edit line, esc to end editing, d to delete line",
            values=g.splitLines(c.p.b),
            slow_scroll=True,
        )
        assert isinstance(box, BoxTitleBody), repr(box)
        # Get the contained widget.
        widgets = box._my_widgets
        assert len(widgets) == 1
        w = widgets[0]
        if trace:
            g.trace('\nBODY', w, '\nBOX', box)
        assert isinstance(w, LeoBody), repr(w)
        # Link and check.
        # The generic LeoFrame class
        assert isinstance(c.frame, leoFrame.LeoFrame), repr(c.frame)
        # The generic LeoBody class
        assert isinstance(c.frame.body, leoFrame.LeoBody), repr(c.frame.body)
        assert c.frame.body.widget is None, repr(c.frame.body.widget)
        c.frame.body.widget = w
        assert c.frame.body.wrapper is None, repr(c.frame.body.wrapper)
        # A Union: hard to annotate.
        c.frame.body.wrapper = wrapper = BodyWrapper(c, 'body', w)  # type:ignore
        # Inject the wrapper for get_focus.
        box.leo_wrapper = wrapper
        w.leo_wrapper = wrapper
        # Inject leo_c.
        w.leo_c = c
        w.leo_box = box

    #@+node:ekr.20170502083613.1: *6* CGui.createCursesLog
    def createCursesLog(self, c: Cmdr, form: Wrapper) -> None:
        """
        Create the curses log widget in the given curses Form.
        Populate the widget with the queued log messages.
        """
        class BoxTitleLog(npyscreen.BoxTitle):
            # pylint: disable=used-before-assignment
            _contained_widget = LeoLog
            how_exited = None

        box = form.add(
            BoxTitleLog,
            max_height=8,  # Subtract 4 lines
            name='Log Pane',
            footer="Press e to edit line, esc to end editing, d to delete line",
            values=[s for s, color in self.wait_list],
            slow_scroll=False,
        )
        assert isinstance(box, BoxTitleLog), repr(box)
        # Clear the wait list and disable it.
        self.wait_list = []
        self.log_inited = True
        widgets: List[Wrapper] = box._my_widgets
        assert len(widgets) == 1
        w = widgets[0]
        assert isinstance(w, LeoLog), repr(w)
        # Link and check...
        assert isinstance(self.log, CoreLog), repr(self.log)
        self.log.widget = w  # type:ignore
        w.firstScroll()
        # The generic LeoFrame class
        assert isinstance(c.frame, leoFrame.LeoFrame), repr(c.frame)
        c.frame.log.wrapper = wrapper = LogWrapper(c, 'log', w)
        # Inject the wrapper for get_focus.
        box.leo_wrapper = wrapper
        w.leo_wrapper = wrapper
        w.leo_box = box
    #@+node:ekr.20170502084249.1: *6* CGui.createCursesMinibuffer
    def createCursesMinibuffer(self, c: Cmdr, form: Wrapper) -> None:
        """Create the curses minibuffer widget in the given curses Form."""
        trace = False

        class MiniBufferBox(npyscreen.BoxTitle):
            """An npyscreen class representing Leo's minibuffer, with binding."""
            # pylint: disable=used-before-assignment
            _contained_widget = LeoMiniBuffer
            how_exited = None

        box = form.add(MiniBufferBox, name='Mini-buffer', max_height=3)
        assert isinstance(box, MiniBufferBox)
        # Link and check...
        widgets = box._my_widgets
        assert len(widgets) == 1
        w = widgets[0]
        if trace:
            g.trace('\nMINI', w, '\nBOX', box)
        assert isinstance(w, LeoMiniBuffer), repr(w)
        assert isinstance(c.frame, CoreFrame), repr(c.frame)
        assert c.frame.miniBufferWidget is None
        wrapper = MiniBufferWrapper(c, 'minibuffer', w)
        assert wrapper.widget == w, repr(wrapper.widget)
        c.frame.miniBufferWidget = wrapper
        # Inject the box into the wrapper
        wrapper.box = box
        # Inject the wrapper for get_focus.
        box.leo_wrapper = wrapper
        w.leo_c = c
        w.leo_wrapper = wrapper

    #@+node:ekr.20171129193946.1: *6* CGui.createCursesStatusLine
    def createCursesStatusLine(self, c: Cmdr, form: Wrapper) -> None:
        """Create the curses minibuffer widget in the given curses Form."""

        class StatusLineBox(npyscreen.BoxTitle):
            """An npyscreen class representing Leo's status line."""
            # pylint: disable=used-before-assignment
            _contained_widget = LeoStatusLine
            how_exited = None

        box = form.add(StatusLineBox, name='Status Line', max_height=3)
        assert isinstance(box, StatusLineBox)
        # Link and check...
        widgets = box._my_widgets
        assert len(widgets) == 1
        w = widgets[0]
        assert isinstance(w, LeoStatusLine), repr(w)
        assert isinstance(c.frame, CoreFrame), repr(c.frame)
        wrapper = StatusLineWrapper(c, 'status-line', w)
        assert wrapper.widget == w, repr(wrapper.widget)
        assert isinstance(c.frame.statusLine, g.NullObject)
        # assert c.frame.statusLine is None
        c.frame.statusLine = wrapper
        c.frame.statusText = wrapper
        # Inject the wrapper for get_focus.
        box.leo_wrapper = wrapper
        w.leo_c = c
        w.leo_wrapper = wrapper
    #@+node:ekr.20170502083754.1: *6* CGui.createCursesTree
    def createCursesTree(self, c: Cmdr, form: Wrapper) -> None:
        """Create the curses tree widget in the given curses Form."""

        class BoxTitleTree(npyscreen.BoxTitle):
            # pylint: disable=used-before-assignment
            _contained_widget = LeoMLTree
            how_exited = None

        hidden_root_node = LeoTreeData(content='<HIDDEN>', ignore_root=True)
        if native:
            pass  # cacher created below.
        else:
            for i in range(3):
                node = hidden_root_node.new_child(content='node %s' % (i))
                for j in range(2):
                    child = node.new_child(content='child %s.%s' % (i, j))
                    for k in range(4):
                        grand_child = child.new_child(
                            content='grand-child %s.%s.%s' % (i, j, k))
                        assert grand_child  # for pyflakes.
        box = form.add(
            BoxTitleTree,
            max_height=8,  # Subtract 4 lines
            name='Tree Pane',
            footer="Press d to delete node, e to edit headline (return to end), i to insert node",
            values=hidden_root_node,
            slow_scroll=False,
        )
        assert isinstance(box, BoxTitleTree), repr(box)
        # Link and check...
        widgets = box._my_widgets
        assert len(widgets) == 1
        w = leo_tree = widgets[0]
        assert isinstance(w, LeoMLTree), repr(w)
        leo_tree.leo_c = c
        if native:
            leo_tree.values = LeoValues(c=c, tree=leo_tree)
        assert getattr(leo_tree, 'hidden_root_node') is None, leo_tree
        leo_tree.hidden_root_node = hidden_root_node
        # CoreFrame is a LeoFrame
        assert isinstance(c.frame, leoFrame.LeoFrame), repr(c.frame)
        assert isinstance(c.frame.tree, CoreTree), repr(c.frame.tree)
        # A standard ivar, used by Leo's core.
        assert c.frame.tree.canvas is None, repr(c.frame.canvas)
        c.frame.canvas = leo_tree  # A LeoMLTree.
        assert not hasattr(c.frame.tree, 'treeWidget'), repr(c.frame.tree.treeWidget)
        c.frame.tree.treeWidget = leo_tree
        # treeWidget is an official ivar.
        assert c.frame.tree.widget is None
        c.frame.tree.widget = leo_tree  # Set CoreTree.widget.
        # Inject the wrapper for get_focus.
        wrapper = c.frame.tree
        assert wrapper
        box.leo_wrapper = wrapper
        w.leo_wrapper = wrapper
    #@+node:ekr.20171126191726.1: *6* CGui.monkeyPatch
    def monkeyPatch(self, c: Cmdr) -> None:
        """Monkey patch commands"""
        table = (
            ('start-search', self.startSearch),
        )
        for commandName, func in table:
            g.global_commands_dict[commandName] = func
            c.k.overrideCommand(commandName, func)
        # A new ivar.
        c.inFindCommand = False
    #@+node:ekr.20170419110052.1: *5* CGui.createLeoFrame
    def createLeoFrame(self, c: Cmdr, title: str) -> Wrapper:
        """
        Create a LeoFrame for the current gui.
        Called from Leo's core (c.initObjects).
        """
        return CoreFrame(c, title)
    #@+node:ekr.20170502103338.1: *5* CGui.destroySelf
    def destroySelf(self) -> None:
        """
        Terminate the curses gui application.
        Leo's core calls this only if the user agrees to terminate the app.
        """
        sys.exit(0)
    #@+node:ekr.20220618070256.1: *5* CGui.getFullVersion
    def getFullVersion(self, c: Cmdr=None) -> str:
        return 'Leo Console Gui (npyscreen)'
    #@+node:ekr.20170501032447.1: *5* CGui.init_logger
    def init_logger(self) -> None:

        self.rootLogger = logging.getLogger('')
        self.rootLogger.setLevel(logging.DEBUG)
        socketHandler = logging.handlers.SocketHandler(
            'localhost',
            logging.handlers.DEFAULT_TCP_LOGGING_PORT,
        )
        self.rootLogger.addHandler(socketHandler)
        logging.info('-' * 20)
        # Monkey-patch leoGlobals functions.
        g.es = es
        g.pr = pr  # Most ouput goes through here, including g.es_exception.
        g.trace = trace
    #@+node:ekr.20170419140914.1: *5* CGui.runMainLoop
    def runMainLoop(self) -> None:
        """The curses gui main loop."""
        # pylint: disable=no-member
        #
        # Do NOT change g.app!
        self.curses_app = LeoApp()
        stdscr = curses.initscr()
        if 1:  # Must follow initscr.
            self.dump_keys()
        try:
            self.curses_app.run()  # run calls CApp.main(), which calls CGui.run().
        finally:
            curses.nocbreak()
            stdscr.keypad(0)
            curses.echo()
            curses.endwin()
            if 'shutdown' in g.app.debug:
                g.pr('Exiting Leo...')
    #@+node:ekr.20170502020354.1: *5* CGui.run
    def run(self) -> None:
        """
        Create and run the top-level curses form.
        """
        self.top_form = self.createCursesTop()
        # g.trace('(CGui) top_form', self.top_form)
        self.top_form.edit()
    #@+node:ekr.20170504112655.1: *4* CGui.Clipboard
    # Yes, using Tkinter seems to be the standard way.
    #@+node:ekr.20170504112744.3: *5* CGui.getTextFromClipboard
    def getTextFromClipboard(self) -> str:
        """Get a unicode string from the clipboard."""
        if not Tk:
            return ''
        root = Tk()
        root.withdraw()
        try:
            s = root.clipboard_get()
        except Exception:  # _tkinter.TclError:
            s = ''
        root.destroy()
        return g.toUnicode(s)
    #@+node:ekr.20170504112744.2: *5* CGui.replaceClipboardWith
    def replaceClipboardWith(self, s: str) -> None:
        """Replace the clipboard with the string s."""
        if not Tk:
            return
        root = Tk()
        root.withdraw()
        root.clipboard_clear()
        root.clipboard_append(s)
        root.destroy()

    # Do *not* define setClipboardSelection.
    # setClipboardSelection = replaceClipboardWith
    #@+node:ekr.20170502021145.1: *4* CGui.dialogs
    #@+node:ekr.20170712145632.2: *5* CGui.createFindDialog
    def createFindDialog(self, c: Cmdr) -> None:
        """Create and init a non-modal Find dialog."""
        g.trace('not implemented')
    #@+node:ekr.20171126182120.1: *5* CGui.dialog_message
    def dialog_message(self, message: str) -> None:
        """No longer used: a placeholder for dialogs."""
        if not g.unitTesting:
            for s in g.splitLines(message):
                g.pr(s.rstrip())

    #@+node:ekr.20171126182120.2: *5* CGui.runAboutLeoDialog
    def runAboutLeoDialog(self, c: Cmdr, version: str, theCopyright: str, url: str, email: str) -> None:
        """Create and run Leo's About Leo dialog."""
        if not g.unitTesting:
            message = '%s\n%s\n%s\n%s' % (version, theCopyright, url, email)
            # form_color='STANDOUT', wrap=True, wide=False, editw=0)
            utilNotify.notify_confirm(message, title="About Leo")

    #@+node:ekr.20171126182120.3: *5* CGui.runAskLeoIDDialog
    def runAskLeoIDDialog(self) -> None:
        """Create and run a dialog to get g.app.LeoID."""
        if not g.unitTesting:
            message = (
                "leoID.txt not found\n\n" +
                "The curses gui can not set this file." +
                "Exiting..."
            )
            g.trace(message)
            # "Please enter an id that identifies you uniquely.\n" +
            # "Your cvs/bzr login name is a good choice.\n\n" +
            # "Leo uses this id to uniquely identify nodes.\n\n" +
            # "Your id must contain only letters and numbers\n" +
            # "and must be at least 3 characters in length."
            sys.exit(0)

    #@+node:ekr.20171126182120.5: *5* CGui.runAskOkCancelNumberDialog
    def runAskOkCancelNumberDialog(self,
        c: Cmdr,
        title: str,
        message: str,
        cancelButtonText: str=None,
        okButtonText: str=None,
    ) -> str:
        """Create and run askOkCancelNumber dialog ."""
        if g.unitTesting:
            return 'no'
        if self.curses_app:
            self.in_dialog = True
            val = utilNotify.notify_ok_cancel(message=message, title=title)
            self.in_dialog = False
            return val
        return 'no'
    #@+node:ekr.20171126182120.6: *5* CGui.runAskOkCancelStringDialog
    def runAskOkCancelStringDialog(
        self,
        c: Cmdr,
        title: str,
        message: str,
        cancelButtonText: str=None,
        okButtonText: str=None,
        default: str="",
        wide: bool=False,
    ) -> str:
        """Create and run askOkCancelString dialog ."""
        if g.unitTesting:
            return ''
        self.in_dialog = True
        val = utilNotify.notify_ok_cancel(message=message, title=title)  # val is True/False
        self.in_dialog = False
        return 'yes' if val else 'no'
    #@+node:ekr.20171126182120.4: *5* CGui.runAskOkDialog
    def runAskOkDialog(
        self,
        c: Cmdr,
        title: str,
        message: str=None,
        text: str="Ok",
    ) -> bool:
        """Create and run an askOK dialog ."""
        if g.unitTesting:
            return False
        if self.curses_app:
            self.in_dialog = True
            val = utilNotify.notify_confirm(message=message, title=title)
            self.in_dialog = False
            return val
        return False

    #@+node:ekr.20171126182120.8: *5* CGui.runAskYesNoCancelDialog
    def runAskYesNoCancelDialog(
        self,
        c: Cmdr,
        title: str,
        message: str=None,
        yesMessage: str="Yes",
        noMessage: str="No",
        yesToAllMessage: str=None,
        defaultButton: str="Yes",
        cancelMessage: str=None,
    ) -> str:
        """Create and run an askYesNoCancel dialog ."""
        if g.unitTesting:
            return ''
        self.in_dialog = True
        # Important: don't use notify_ok_cancel.
        val = utilNotify.notify_yes_no(message=message, title=title)
        self.in_dialog = False
        return 'yes' if val else 'no'

    #@+node:ekr.20171126182120.7: *5* CGui.runAskYesNoDialog
    def runAskYesNoDialog(
        self,
        c: Cmdr,
        title: str,
        message: str=None,
        yes_all: bool=False,
        no_all: bool=False,
    ) -> str:
        """Create and run an askYesNo dialog."""
        if g.unitTesting:
            return ''
        self.in_dialog = True
        val = utilNotify.notify_ok_cancel(message=message, title=title)
        self.in_dialog = False
        return 'yes' if val else 'no'

    #@+node:ekr.20171126182120.9: *5* CGui.runOpenFileDialog
    def runOpenFileDialog(self,
        c: Cmdr,
        title: str,
        filetypes: List[str],
        defaultextension: str,
        multiple: bool=False,
        startpath: str=None,
    ) -> Union[List[str], str]:  # Return type depends on the evil multiple keyword.
        if not g.unitTesting:
            g.trace('not ready yet', title)
        return ''

    #@+node:ekr.20171126182120.10: *5* CGui.runPropertiesDialog
    def runPropertiesDialog(
        self,
        title: str='Properties',
        data: Any=None,
        callback: Callable=None,
        buttons: List[str]=None,
    ) -> None:
        """Dispay a modal TkPropertiesDialog"""
        if not g.unitTesting:
            g.trace('not ready yet', title)

    #@+node:ekr.20171126182120.11: *5* CGui.runSaveFileDialog
    def runSaveFileDialog(self, c: Cmdr, title: str, filetypes: List[str], defaultextension: str) -> str:
        if g.unitTesting:
            return None
        # Not tested.
        from leo.external.npyscreen.fmFileSelector import selectFile
        self.in_dialog = True
        s = selectFile(
            select_dir=False,
            must_exist=False,
            confirm_if_exists=True,
            sort_by_extension=True,
        )
        self.in_dialog = False
        s = s or ''
        if s:
            c.last_dir = g.os_path_dirname(s)
        return s
    #@+node:ekr.20170430114709.1: *4* CGui.do_key
    def do_key(self, ch_i: int) -> bool:

        # Ignore all printable characters.
        if not self.in_dialog and 32 <= ch_i < 128:
            g.trace('ignoring', chr(ch_i))
            return True
        return self.key_handler.do_key(ch_i)
    #@+node:ekr.20170526051256.1: *4* CGui.dump_keys
    def dump_keys(self) -> None:
        """Show all defined curses.KEY_ constants."""
        if 0:
            aList = ['%3s %s' % (getattr(curses, z), z)
                for z in dir(curses)
                    if isinstance(getattr(curses, z), int)]
            g.trace()
            g.printList(sorted(aList))
    #@+node:ekr.20170522005855.1: *4* CGui.event_generate
    def event_generate(self, c: Cmdr, char: str, shortcut: str, w: Wrapper) -> None:

        k = c.k
        event = KeyEvent(
            c=c,
            char=char,
            event=g.NullObject(),
            shortcut=shortcut,
            w=w,
        )
        k.masterKeyHandler(event)
        g.app.gui.show_label(c)
        c.outerUpdate()
    #@+node:ekr.20171128041920.1: *4* CGui.Focus
    #@+node:ekr.20171127171659.1: *5* CGui.focus_to_body
    def focus_to_body(self, c: Cmdr) -> None:
        """Put focus in the body pane."""
        self.set_focus(c, c.frame.body)
    #@+node:ekr.20171202092838.1: *5* CGui.focus_to_head
    def focus_to_head(self, c: Cmdr, p: Position) -> None:
        """Put focus in the headline."""
        self.set_focus(c, c.frame.tree)
    #@+node:ekr.20171127162649.1: *5* CGui.focus_to_minibuffer
    def focus_to_minibuffer(self, c: Cmdr) -> None:
        """Put focus in minibuffer text widget."""
        self.set_focus(c, c.frame.miniBufferWidget)
    #@+node:ekr.20170502101347.1: *5* CGui.get_focus
    def get_focus(self, c: Cmdr=None, raw: bool=False, at_idle: bool=False) -> Optional[Wrapper]:
        """
        Return the Leo wrapper for the npyscreen widget that is being edited.
        """
        # Careful during startup.
        trace = 'focus' in g.app.debug
        editw = getattr(g.app.gui.curses_form, 'editw', None)
        if editw is None:
            if trace:
                g.trace('(CursesGui) no editw')
            return None
        widget = self.curses_form._widgets__[editw]  # pylint: disable=invalid-sequence-index
        if hasattr(widget, 'leo_wrapper'):
            if trace:
                g.trace('(CursesGui)', widget.leo_wrapper.__class__.__name__)
                g.trace(g.callers())
            return widget.leo_wrapper
        # At present, HeadWrappers have no widgets.
        g.trace('(CursesGui) ===== no leo_wrapper', widget)
        return None
    #@+node:ekr.20171128041805.1: *5* CGui.set_focus & helpers
    set_focus_fail: List[Wrapper] = []  # List of widgets

    def set_focus(self, c: Cmdr, w: Wrapper) -> None:
        """Given a Leo wrapper, set focus to the underlying npyscreen widget."""
        new_focus = False
        if new_focus:
            self.NEW_set_focus(c, w)
        else:
            self.OLD_set_focus(c, w)
    #@+node:ekr.20171204040620.1: *6* CGui.NEW_set_focus & helper
    def NEW_set_focus(self, c: Cmdr, w: Wrapper) -> None:
        """
        Given a Leo wrapper w, set focus to the underlying npyscreen widget.
        """
        trace = 'focus' in g.app.debug
        # Get the wrapper's npyscreen widget.
        widget = getattr(w, 'widget', None)
        if trace:
            g.trace('widget', widget.__class__.__name__)
            g.trace(g.callers())
        if not widget:
            g.trace('no widget', repr(w))
            return
        if not isinstance(widget, npyscreen.wgwidget.Widget):
            g.trace('not an npyscreen.Widget', repr(w))
            return
        form = self.curses_form
        # Find the widget to be edited
        for i, widget2 in enumerate(form._widgets__):
            if widget == widget2:
                # if trace: g.trace('FOUND', i, widget.__class__.__name__)
                self.switch_editing(i, widget)
                return
            for j, widget3 in enumerate(getattr(widget2, '_my_widgets', [])):
                if widget == widget3 or repr(widget) == repr(widget3):
                    # if trace: g.trace('FOUND INNER', i, j, widget2.__class__.__name__)
                    self.switch_editing(i, widget)
                    return
        if trace and widget not in self.set_focus_fail:
            self.set_focus_fail.append(widget)
            g.trace('Fail\n%r\n%r' % (widget, w))
    #@+node:ekr.20171204040620.2: *7* CGui.switch_editing
    def switch_editing(self, i: int, w: Wrapper) -> None:
        """Clear editing for *all* widgets and set form.editw to i"""
        trace = 'focus' in g.app.debug
        how = None  # 'leo-set-focus'
        form = self.curses_form
        if i == form.editw:
            if trace:
                g.trace('NO CHANGE', i, w.__class__.__name__)
            return
        if trace:
            g.trace('-----', i, w.__class__.__name__)

        # Select the widget for editing.
        form.editw = i

        if 0:
            # Inject 'leo-set-focus' into form.how_exited_handers

            def switch_focus_callback(form: Wrapper=form, i: int=i, w: Wrapper=w) -> None:
                g.trace(i, w.__class__.__name__)
                g.trace(g.callers(verbose=True))
                w.display()
                form.display()

            form.how_exited_handers[how] = switch_focus_callback
        if 1:
            # Clear editing for the editw widget:
            w = form._widgets__[i]
            # if trace: g.trace('editing', getattr(w, 'editing', None))
            if hasattr(w, 'editing'):
                w.editing = False
            w.how_exited = how
        if 1:
            # Clear editing for all widgets.
            for i, w1 in enumerate(form._widgets__):
                # if trace: g.trace('CLEAR',  w.__class__.__name__)
                if getattr(w1, 'editing', None):
                    if trace:
                        g.trace('End EDITING', w1.__class__.__name__)
                    w1.editing = False
                # w1.how_exited = how
                w1.display()
                for j, w2 in enumerate(getattr(w, '_my_widgets', [])):
                    # if trace: g.trace('CLEAR INNER',  w.__class__.__name__)
                    if getattr(w2, 'editing', None):
                        if trace:
                            g.trace('END EDITING', w2.__class__.__name__)
                        w2.editing = False
                    # w2.how_exited = how
                    w2.display()

        # Start editing the widget.
        w.editing = True
        w.display()
        form.display()
        w.edit()  # Does not return
    #@+node:ekr.20171204100910.1: *6* CGui.OLD_set_focus
    def OLD_set_focus(self, c: Cmdr, w: Wrapper) -> None:
        """Given a Leo wrapper, set focus to the underlying npyscreen widget."""
        trace = 'focus' in g.app.debug
        verbose = True  # Full trace of callers.
        # Get the wrapper's npyscreen widget.
        widget = getattr(w, 'widget', None)
        if trace:
            g.trace('widget', widget.__class__.__name__)
            g.trace(g.callers())
        if not widget:
            if trace or not w:
                g.trace('no widget', repr(w))
            return
        if not isinstance(widget, npyscreen.wgwidget.Widget):
            g.trace('not an npyscreen.Widget', repr(w))
            return
        form = self.curses_form
        if 1:  # Seems to cause problems.
            # End editing in the previous form.
            i = form.editw
            w = form._widgets__[i]
            if trace and verbose:
                g.trace('CLEAR FOCUS', i, w.__class__.__name__)
            if w:
                w.editing = False
                w.how_exited = EXITED_ESCAPE
                w.display()
        for i, widget2 in enumerate(form._widgets__):
            if widget == widget2:
                if trace:
                    g.trace('FOUND', i, widget)
                form.editw = i
                form.display()
                return
            for j, widget3 in enumerate(getattr(widget2, '_my_widgets', [])):
                if widget == widget3 or repr(widget) == repr(widget3):
                    if trace:
                        g.trace('FOUND INNER', i, j, widget2)
                    form.editw = i  # Select the *outer* widget.
                    # Like BoxTitle.edit.
                    if 1:
                        # So weird.
                        widget2.editing = True
                        widget2.display()
                        # widget2.entry_widget.edit()
                        widget3.edit()
                        widget2.how_exited = widget3.how_exited
                        widget2.editing = False
                        widget2.display()
                    form.display()
                    return
        if trace and widget not in self.set_focus_fail:
            self.set_focus_fail.append(widget)
            g.trace('Fail\n%r\n%r' % (widget, w))
    #@+node:ekr.20170514060742.1: *4* CGui.Fonts
    def getFontFromParams(self,
        family: str, size: str, slant: str, weight: str, defaultSize: int = 12, tag: str = '',
    ) -> None:
        return None
    #@+node:ekr.20170504052119.1: *4* CGui.isTextWrapper
    def isTextWrapper(self, w: Wrapper) -> bool:
        """Return True if w is a Text widget suitable for text-oriented commands."""
        return bool(w and getattr(w, 'supportsHighLevelInterface', None))
    #@+node:ekr.20170612063102.1: *4* CGui.put_help
    def put_help(self, c: Cmdr, s: str, short_title: str) -> None:
        """Put a help message in a dialog."""
        if not g.unitTesting:
            utilNotify.notify_confirm(
                message=s,
                title=short_title or 'Help',
            )
    #@+node:ekr.20171130195357.1: *4* CGui.redraw_in_context
    def redraw_in_context(self, c: Cmdr) -> None:
        """Redraw p in context."""
        w = c.frame.tree.widget
        c.expandAllAncestors(c.p)
        g.app.gui.show_label(c)
        w.values.clear_cache()
        w.select_leo_node(c.p)
        w.update(forceInit=True)
        g.app.gui.curses_form.display()
    #@+node:ekr.20171130181722.1: *4* CGui.repeatComplexCommand (commandName, event)
    def repeatComplexCommand(self, c: Cmdr) -> None:
        """An override of the 'repeat-complex-command' command."""
        trace = False and not g.unitTesting
        k = c.k
        if k.mb_history:
            commandName = k.mb_history[0]
            if trace:
                g.trace(commandName)
                g.printObj(k.mb_history)
            k.masterCommand(
                commandName=commandName,
                event=KeyEvent(c, char='', event='', shortcut='', w=None),
                func=None,
                stroke=None,
            )
        else:
            g.warning('no previous command')
    #@+node:ekr.20171201084211.1: *4* CGui.set_minibuffer_label
    def set_minibuffer_label(self, c: Cmdr, s: str) -> None:
        """Remember the minibuffer label."""
        self.minibuffer_label = s
        self.show_label(c)
    #@+node:ekr.20171202092230.1: *4* CGui.show_find_success
    def show_find_success(self, c: Cmdr, in_headline: bool, insert: int, p: Position) -> None:
        """Handle a successful find match."""
        trace = False and not g.unitTesting
        if in_headline:
            if trace:
                g.trace('HEADLINE', p.h)
            c.frame.tree.widget.select_leo_node(p)
            self.focus_to_head(c, p)  # Does not return.
        else:
            w = c.frame.body.widget
            row, col = g.convertPythonIndexToRowCol(p.b, insert)
            if trace:
                g.trace('BODY ROW', row, p.h)
            w.cursor_line = row
            self.focus_to_body(c)  # Does not return.
    #@+node:ekr.20171201081700.1: *4* CGui.show_label
    def show_label(self, c: Cmdr) -> None:
        """
        Set the minibuffer's label the value set by set_minibuffer_label.
        """
        trace = False and not g.unitTesting
        wrapper = c.frame.miniBufferWidget
        if not wrapper:
            return
        box = wrapper.box
        if not box:
            return
        s = self.minibuffer_label
        if trace:
            g.trace(repr(s))
        box.name = 'Mini-buffer: %s' % s.strip()
        box.update()
        g.app.gui.curses_form.display()

    #@+node:ekr.20171126192144.1: *4* CGui.startSearch
    def startSearch(self, event: Event) -> None:
        c = event.get('c')
        if not c:
            return
        # This does not work because the console doesn't show the message!
            # if not isinstance(w, MiniBufferWrapper):
                # g.es_print('Sorry, Ctrl-F must be run from the minibuffer.')
                # return
        fc = c.findCommands
        ftm = c.frame.ftm
        c.inCommand = False
        c.inFindCommand = True  # A new flag.
        fc.minibuffer_mode = True
        if 0:  # Allow hard settings, for tests.
            table = (
                ('pattern_match', ftm.check_box_regexp, True),
            )
            for setting_name, w, val in table:
                assert hasattr(fc, setting_name), setting_name
                setattr(fc, setting_name, val)
                w.setCheckState(val)
        c.findCommands.startSearch(event)
        options = fc.computeFindOptionsInStatusArea()
        c.frame.statusLine.put(options)
        self.focus_to_minibuffer(c)  # Does not return!
    #@-others
#@+node:ekr.20170524124010.1: ** Leo widget classes
# Most are subclasses Leo's base gui classes.
# All classes have a "c" ivar.
#@+node:ekr.20170501024433.1: *3* class CoreBody (leoFrame.LeoBody)
class CoreBody(leoFrame.LeoBody):
    """
    A class that represents curses body pane.
    This is c.frame.body.
    """

    def __init__(self, c: Cmdr) -> None:

        # Init the base class.
        super().__init__(frame=c.frame, parentFrame=None)
        self.c: Cmdr = c
        self.colorizer: Wrapper = leoFrame.NullColorizer(c)
        self.widget: Wrapper = None
        self.wrapper: Wrapper = None  # Set in createCursesBody.
#@+node:ekr.20170419105852.1: *3* class CoreFrame (leoFrame.LeoFrame)
class CoreFrame(leoFrame.LeoFrame):
    """The LeoFrame when --gui=curses is in effect."""

    #@+others
    #@+node:ekr.20170501155347.1: *4* CFrame.birth
    def __init__(self, c: Cmdr, title: str) -> None:

        leoFrame.LeoFrame.instances += 1  # Increment the class var.
        super().__init__(c, gui=g.app.gui)  # Init the base class.
        assert c and self.c == c
        c.frame = self
        self.log = CoreLog(c)
        g.app.gui.log = self.log
        self.title: str = title
        # Standard ivars.
        self.ratio = self.secondary_ratio = 0.5
        # Widgets
        self.top = TopFrame(c)
        self.body = CoreBody(c)
        self.menu = CoreMenu(c)
        self.miniBufferWidget: MiniBufferWrapper = None
        self.statusLine: Wrapper = g.NullObject()  # For unit tests.
        assert self.tree is None, self.tree
        self.tree = CoreTree(c)
    #@+node:ekr.20170420163932.1: *5* CFrame.finishCreate
    def finishCreate(self) -> None:

        c = self.c
        g.app.windowList.append(self)
        ftm = StringFindTabManager(c)
        c.findCommands.ftm = ftm  # type:ignore
        self.ftm = ftm
        self.createFindTab()
        self.createFirstTreeNode()  # Call the base-class method.
    #@+node:ekr.20171128052121.1: *5* CFrame.createFindTab & helpers
    def createFindTab(self) -> None:
        """Create a Find Tab in the given parent."""
        # Like DynamicWindow.createFindTab.
        ftm = self.ftm
        assert ftm
        self.create_find_findbox()
        self.create_find_replacebox()
        self.create_find_checkboxes()
        # Official ivars (in addition to checkbox ivars).
        self.leo_find_widget = None
        ftm.init_widgets()
    #@+node:ekr.20171128052121.4: *6* CFrame.create_find_findbox
    def create_find_findbox(self) -> None:
        """Create the Find: label and text area."""
        c = self.c
        fc = c.findCommands
        ftm = self.ftm
        assert ftm
        assert ftm.find_findbox is None
        ftm.find_findbox = self.createLineEdit('findPattern', disabled=fc.expert_mode)
    #@+node:ekr.20171128052121.5: *6* CFrame.create_find_replacebox
    def create_find_replacebox(self) -> None:
        """Create the Replace: label and text area."""
        c = self.c
        fc = c.findCommands
        ftm = self.ftm
        assert ftm
        assert ftm.find_replacebox is None
        ftm.find_replacebox = self.createLineEdit('findChange', disabled=fc.expert_mode)
    #@+node:ekr.20171128052121.6: *6* CFrame.create_find_checkboxes
    def create_find_checkboxes(self) -> None:
        """Create check boxes and radio buttons."""
        # c = self.c
        ftm = self.ftm

        def mungeName(kind: str, label: str) -> str:
            # The returned value is the name of an ivar.
            kind = 'check_box_' if kind == 'box' else 'radio_button_'
            name = label.replace(' ', '_').replace('&', '').lower()
            return '%s%s' % (kind, name)

        d = {
            'box': self.createCheckBox,
            'rb': self.createRadioButton,
        }
        table = (
            # Left column.
            ('box', 'whole &Word'),
            ('box', '&Ignore case'),
            ('box', 'rege&Xp'),
            ('box', 'mark &Finds'),
            ('box', 'mark &Changes'),
            # Right colunn.
            ('rb', '&Entire outline'),
            ('rb', '&Suboutline only'),
            ('rb', '&Node only'),
            ('rb', 'fi&Le only'),  # #2684.
            ('box', 'search &Headline'),
            ('box', 'search &Body'),
        )
        for kind, label in table:
            name = mungeName(kind, label)
            func = d.get(kind)
            assert func
            label = label.replace('&', '')
            w = func(name, label)
            assert getattr(ftm, name) is None
            setattr(ftm, name, w)
    #@+node:ekr.20171128053531.3: *6* CFrame.createCheckBox
    def createCheckBox(self, name: str, label: str) -> Wrapper:

        return leoGui.StringCheckBox(name, label)
    #@+node:ekr.20171128053531.8: *6* CFrame.createLineEdit
    def createLineEdit(self, name: str, disabled: bool=True) -> Wrapper:

        return leoGui.StringLineEdit(name, disabled)
    #@+node:ekr.20171128053531.9: *6* CFrame.createRadioButton
    def createRadioButton(self, name: str, label: str) -> Wrapper:

        return leoGui.StringRadioButton(name, label)
    #@+node:ekr.20170501161029.1: *4* CFrame.do nothings
    def bringToFront(self) -> None:
        pass

    def contractPane(self, event: Event=None) -> None:
        pass

    def deiconify(self) -> None:
        pass

    def destroySelf(self) -> None:
        pass

    def forceWrap(self, p: Position) -> None:
        pass

    def get_window_info(self) -> Tuple[int, int, int, int]:
        """Return width, height, left, top."""
        return 700, 500, 50, 50

    def iconify(self) -> None:
        pass

    def lift(self) -> None:
        pass

    def getShortCut(self, *args: Any, **kwargs: Any) -> None:
        return None

    def getTitle(self) -> str:
        return self.title

    def minimizeAll(self, event: Event=None) -> None:
        pass

    def resizePanesToRatio(self, ratio: float, secondary_ratio: float) -> None:
        """Resize splitter1 and splitter2 using the given ratios."""

    def resizeToScreen(self, event: Event=None) -> None:
        pass

    def setInitialWindowGeometry(self) -> None:
        pass

    def setTitle(self, title: str) -> None:
        self.title = g.toUnicode(title)

    def setTopGeometry(self, w: int, h: int, x: int, y: int) -> None:
        pass

    def setWrap(self, p: Position) -> None:
        pass

    def update(self, *args: Any, **keys: Any) -> None:
        pass
    #@+node:ekr.20170524144717.1: *4* CFrame.get_focus
    def getFocus(self) -> None:

        return g.app.gui.get_focus()
    #@+node:ekr.20170522015906.1: *4* CFrame.pasteText (cursesGui2)
    @frame_cmd('paste-text')
    def pasteText(self, event: Event=None, middleButton: bool=False) -> None:
        """
        Paste the clipboard into a widget.
        If middleButton is True, support x-windows middle-mouse-button easter-egg.
        """
        trace = False and not g.unitTesting
        c, p, u = self.c, self.c.p, self.c.undoer
        w = event and event.widget
        if not isinstance(w, leoFrame.StringTextWrapper):
            g.trace('not a StringTextWrapper', repr(w))
            return
        bunch = u.beforeChangeBody(p)
        wname = c.widget_name(w)
        i, j = w.getSelectionRange()  # Returns insert point if no selection.
        s = g.app.gui.getTextFromClipboard()
        s = g.toUnicode(s)
        if trace:
            g.trace('wname', wname, 'len(s)', len(s))
        single_line = any(wname.startswith(z) for z in ('head', 'minibuffer'))
        if single_line:
            # Strip trailing newlines so the truncation doesn't cause confusion.
            while s and s[-1] in ('\n', '\r'):
                s = s[:-1]
        # Update the widget.
        if i != j:
            w.delete(i, j)
        w.insert(i, s)
        if wname.startswith('body'):
            p.v.b = w.getAllText()
            u.afterChangeBody(p, 'Paste', bunch)
        elif wname.startswith('head'):
            # New for Curses gui.
            c.frame.tree.onHeadChanged(c.p, s=w.getAllText(), undoType='Paste')

    OnPasteFromMenu = pasteText
    #@-others
#@+node:ekr.20170419143731.1: *3* class CoreLog (leoFrame.LeoLog)
class CoreLog(leoFrame.LeoLog):
    """
    A class that represents curses log pane.
    This is c.frame.log.
    """

    #@+others
    #@+node:ekr.20170419143731.4: *4* CLog.__init__
    def __init__(self, c: Cmdr) -> None:
        """Ctor for CLog class."""
        super().__init__(frame=None, parentFrame=None)
        self.c = c
        self.enabled = True  # Required by Leo's core.
        self.isNull = False  # Required by Leo's core.
        # The npyscreen log widget. Queue all output until set. Set in CApp.main.
        self.widget: Wrapper = None
        self.contentsDict: Dict[str, Wrapper] = {}  # Keys are tab names.  Values are widgets.
        self.logDict: Dict[str, Wrapper] = {}  # Keys are tab names.  Values are the widgets.
        self.tabWidget: Wrapper = None
    #@+node:ekr.20170419143731.7: *4* CLog.clearLog
    @log_cmd('clear-log')
    def clearLog(self, event: Event=None) -> None:
        """Clear the log pane."""
    #@+node:ekr.20170420035717.1: *4* CLog.enable/disable
    def disable(self) -> None:
        self.enabled = False

    def enable(self, enabled: bool=True) -> None:
        self.enabled = enabled
    #@+node:ekr.20170420041119.1: *4* CLog.finishCreate
    def finishCreate(self) -> None:
        """CoreLog.finishCreate."""

    #@+node:ekr.20170513183826.1: *4* CLog.isLogWidget
    def isLogWidget(self, w: Wrapper) -> bool:
        return w == self or w in list(self.contentsDict.values())
    #@+node:ekr.20170513184115.1: *4* CLog.orderedTabNames
    def orderedTabNames(self, LeoLog: Wrapper=None) -> List[str]:  # Unused: LeoLog
        """Return a list of tab names in the order in which they appear in the QTabbedWidget."""
        return []
        # w = self.tabWidget
        # return [w.tabText(i) for i in range(w.count())]
    #@+node:ekr.20170419143731.15: *4* CLog.put
    # Signature is different.
    def put(self, s: str, color: str=None, tabName: str='Log', from_redirect: bool=False) -> None:  # type:ignore
        """All output to the log stream eventually comes here."""
        c, w = self.c, self.widget
        if not c or not c.exists or not w:
            # logging.info('CLog.put: no c: %r' % s)
            return
        assert isinstance(w, npyscreen.MultiLineEditable), repr(w)
        # Fix #508: Part 1: Handle newlines correctly.
        lines = s.split('\n')
        for line in lines:
            w.values.append(line)
        # Fix #508: Part 2: Scroll last line into view.
        w.cursor_line += len(lines)
        w.start_display_at += len(lines)
        w.update()
    #@+node:ekr.20170419143731.16: *4* CLog.putnl
    def putnl(self, tabName: str='Log') -> None:
        """Put a newline to the Qt log."""
        # This is not called normally.
        # print('CLog.put: %s' % g.callers())
        if g.app.quitting:
            return
    #@-others
#@+node:ekr.20170419111515.1: *3* class CoreMenu (leoMenu.LeoMenu)
class CoreMenu(leoMenu.LeoMenu):

    def __init__(self, c: Cmdr) -> None:
        dummy_frame = g.Bunch(c=c)
        super().__init__(dummy_frame)
        self.c = c
#@+node:ekr.20170501024424.1: *3* class CoreTree (leoFrame.LeoTree)
class CoreTree(leoFrame.LeoTree):
    """
    A class that represents curses tree pane.

    This is the c.frame.tree instance.
    """

    #@+others
    #@+node:ekr.20170511111242.1: *4*  CTree.ctor
    class DummyFrame:
        def __init__(self, c: Cmdr) -> None:
            self.c = c

    def __init__(self, c: Cmdr) -> None:

        dummy_frame = self.DummyFrame(c)
        super().__init__(dummy_frame)  # Init the base class.
        assert self.c
        assert not hasattr(self, 'widget')
        self.redrawCount = 0  # For unit tests.
        self.widget: Wrapper = None  # A LeoMLTree set by CGui.createCursesTree.
        # self.setConfigIvars()
        # Status flags, for busy()
        self.contracting = False
        self.expanding = False
        self.redrawing = False
        self.selecting = False
    #@+node:ekr.20170511094217.1: *4* CTree.Drawing
    #@+node:ekr.20170511094217.3: *5* CTree.redraw
    def redraw(self, p: Position=None) -> None:
        """
        Redraw all visible nodes of the tree.
        Preserve the vertical scrolling unless scroll is True.
        """
        trace = False and not g.unitTesting
        if g.unitTesting:
            return  # There is no need. At present, the tests hang.
        if trace:
            g.trace(g.callers())
        if self.widget and not self.busy():
            self.redrawCount += 1  # To keep a unit test happy.
            self.widget.update()
    # Compatibility

    full_redraw = redraw
    redraw_now = redraw
    repaint = redraw
    #@+node:ekr.20170511100356.1: *5* CTree.redraw_after...
    def redraw_after_contract(self, p: Position=None) -> None:
        self.redraw(p)

    def redraw_after_expand(self, p: Position=None) -> None:
        self.redraw(p)

    def redraw_after_head_changed(self) -> None:
        self.redraw()

    def redraw_after_select(self, p: Position=None) -> None:
        """Redraw the entire tree when an invisible node is selected."""
        # Prevent the selecting lockout from disabling the redraw.
        oldSelecting = self.selecting
        self.selecting = False
        try:
            if not self.busy():
                self.redraw(p=p)
        finally:
            self.selecting = oldSelecting
        # Do *not* call redraw_after_select here!
    #@+node:ekr.20170511104032.1: *4* CTree.error
    def error(self, s: str) -> None:
        if not g.unitTesting:
            g.trace('LeoQtTree Error: %s' % (s), g.callers())
    #@+node:ekr.20170511104533.1: *4* CTree.Event handlers
    #@+node:ekr.20170511104533.10: *5* CTree.busy
    def busy(self) -> str:
        """Return True (actually, a debugging string)
        if any lockout is set."""
        trace = False
        table = ('contracting', 'expanding', 'redrawing', 'selecting')
        kinds = ','.join([z for z in table if getattr(self, z)])
        if kinds and trace:
            g.trace(kinds)
        return kinds  # Return the string for debugging
    #@+node:ekr.20170511104533.12: *5* CTree.onHeadChanged (cursesGui2)
    # Tricky code: do not change without careful thought and testing.

    def onHeadChanged(self, p: Position, s: str=None, undoType: str='Typing') -> None:  # type:ignore
        """
        Officially change a headline.
        This is c.frame.tree.onHeadChanged.
        """
        trace = False
        c, u = self.c, self.c.undoer
        if not c.frame.body.wrapper:
            if trace:
                g.trace('NO wrapper')
            return  # Startup.
        w = self.edit_widget(p)
        if not w:
            if trace:
                g.trace('****** no w for p: %s', repr(p))
            return
        ch = '\n'  # New in 4.4: we only report the final keystroke.
        if s is None:
            s = w.getAllText()
        # if trace: g.trace('CoreTree: %r ==> %r' % (p and p.h, s))
        #@+<< truncate s if it has multiple lines >>
        #@+node:ekr.20170511104533.13: *6* << truncate s if it has multiple lines >>
        # Remove trailing newlines before warning of truncation.
        while s and s[-1] == '\n':
            s = s[:-1]
        # Warn if there are multiple lines.
        i = s.find('\n')
        if i > -1:
            s = s[:i]
            # if s != oldHead:
                # g.warning("truncating headline to one line")
        limit = 1000
        if len(s) > limit:
            s = s[:limit]
            # if s != oldHead:
                # g.warning("truncating headline to", limit, "characters")
        #@-<< truncate s if it has multiple lines >>
        # Make the change official, but undo to the *old* revert point.
        changed = s != p.h
        if not changed:
            return  # Leo 6.4: only call hooks if the headline has changed.
        if trace:
            g.trace('changed', changed, 'new', repr(s))
        if g.doHook("headkey1", c=c, p=p, ch=ch, changed=changed):
            return  # The hook claims to have handled the event.
        #
        # Handle undo
        undoData = u.beforeChangeHeadline(p)
        p.initHeadString(s)  # Change p.h *after* calling the undoer's before method.
        if not c.changed:
            c.setChanged()
        # New in Leo 4.4.5: we must recolor the body because
        # the headline may contain directives.
            # c.frame.scanForTabWidth(p)
            # c.frame.body.recolor(p)
        p.setDirty()
        u.afterChangeHeadline(p, undoType, undoData)
        # if changed:
        #    c.redraw_after_head_changed()
            # Fix bug 1280689: don't call the non-existent c.treeEditFocusHelper
        g.doHook("headkey2", c=c, p=p, ch=ch, changed=changed)
    #@+node:ekr.20170511104121.1: *4* CTree.Scroll bars
    #@+node:ekr.20170511104121.2: *5* Ctree.getScroll
    def getScroll(self) -> Tuple[int, int]:
        """Return the hPos,vPos for the tree's scrollbars."""
        return 0, 0
    #@+node:ekr.20170511104121.4: *5* Ctree.setH/VScroll
    def setHScroll(self, hPos: int) -> None:
        pass
        # w = self.widget
        # hScroll = w.horizontalScrollBar()
        # hScroll.setValue(hPos)

    def setVScroll(self, vPos: int) -> None:
        pass
        # w = self.widget
        # vScroll = w.verticalScrollBar()
        # vScroll.setValue(vPos)
    #@+node:ekr.20170511105355.1: *4* CTree.Selecting & editing
    #@+node:ekr.20170511105355.4: *5* CTree.edit_widget
    def edit_widget(self, p: Position) -> Wrapper:
        """Returns the edit widget for position p."""
        return HeadWrapper(c=self.c, name='head', p=p)
    #@+node:ekr.20170511095353.1: *5* CTree.editLabel (cursesGui2) (not used)
    def editLabel(self, p: Position, selectAll: bool=False, selection: Tuple=None) -> Tuple[None, None]:
        """Start editing p's headline."""
        return None, None
    #@+node:ekr.20170511105355.7: *5* CTree.endEditLabel (cursesGui2)
    def endEditLabel(self) -> None:
        """Override LeoTree.endEditLabel.
        End editing of the presently-selected headline.
        """
        c = self.c
        p = c.currentPosition()
        self.onHeadChanged(p)
    #@+node:ekr.20170511105355.8: *5* CTree.getSelectedPositions (called from Leo's core)
    def getSelectedPositions(self) -> List[Position]:
        """This can be called from Leo's core."""
        # Not called from unit tests.
        return [self.c.p]
    #@+node:ekr.20170511105355.9: *5* CTree.setHeadline
    def setHeadline(self, p: Position, s: str) -> None:
        """Force the actual text of the headline widget to p.h."""
        trace = False and not g.unitTesting
        # This is used by unit tests to force the headline and p into alignment.
        if not p:
            if trace:
                g.trace('*** no p')
            return
        # Don't do this here: the caller should do it.
        # p.setHeadString(s)
        e = self.edit_widget(p)
        assert isinstance(e, HeadWrapper), repr(e)
        e.setAllText(s)
        if trace:
            g.trace(e)
    #@+node:ekr.20170523115818.1: *5* CTree.set_body_text_after_select
    def set_body_text_after_select(self, p: Position, old_p: Position) -> None:
        """Set the text after selecting a node."""
        c = self.c
        wrapper = c.frame.body.wrapper
        widget = c.frame.body.widget
        # Important: do this *before* setting text,
        # so that the colorizer will have the proper c.p.
        c.setCurrentPosition(p)
        s = p.v.b
        wrapper.setAllText(s)
        widget.values = g.splitLines(s)
        widget.update()
        # Now done after c.p has been changed.
        # p.restoreCursorAndScroll()
    #@-others
#@+node:ekr.20171129200050.1: *3* class CoreStatusLine
class CoreStatusLine:
    """A do-nothing status line."""

    def __init__(self, c: Cmdr, parentFrame: Wrapper) -> None:
        """Ctor for CoreStatusLine class."""
        # g.trace('(CoreStatusLine)', c)
        self.c = c
        self.enabled = False
        self.parentFrame: Wrapper = parentFrame
        self.textWidget: Wrapper = None
        # The official ivars.
        c.frame.statusFrame = None
        c.frame.statusLabel = None
        c.frame.statusText = None

    #@+others
    #@-others
#@+node:ekr.20170502093200.1: *3* class TopFrame
class TopFrame:
    """A representation of c.frame.top."""

    def __init__(self, c: Cmdr) -> None:
        self.c = c

    def select(self, *args: Any, **kwargs: Any) -> None:
        pass

    def findChild(self, *args: Any, **kwargs: Any) -> Any:
        # Called by nested_splitter.py.
        return g.NullObject()

    def finishCreateLogPane(self, *args: Any, **kwargs: Any) -> None:
        pass
#@+node:ekr.20170524124449.1: ** Npyscreen classes
# These are subclasses of npyscreen base classes.
# These classes have "leo_c" ivars.
#@+node:ekr.20170420054211.1: *3* class LeoApp (npyscreen.NPSApp)
class LeoApp(npyscreen.NPSApp):
    """
    The *anonymous* npyscreen application object, created from
    CGui.runMainLoop. This is *not* g.app.
    """

    # No ctor needed.
        # def __init__(self):
            # super().__init__()

    def main(self) -> None:
        """
        Called automatically from the ctor.
        Create and start Leo's singleton npyscreen window.
        """
        g.app.gui.run()
#@+node:ekr.20170526054750.1: *3* class LeoBody (npyscreen.MultiLineEditable)
class LeoBody(npyscreen.MultiLineEditable):

    continuation_line = "- more -"  # value of contination line.
    _contained_widgets = LeoBodyTextfield

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.values: List[Any]
        self.cursor_line: int
        self.start_display_at: int
        self.leo_box: Wrapper = None
        self.leo_c: Cmdr = None
        self.leo_wrapper: Wrapper = None
        self.set_handlers()
        # createCursesBody  sets the leo_box and leo_c ivars.

    #@+others
    #@+node:ekr.20170604183231.1: *4*  LeoBody handlers
    #@+node:ekr.20170526114040.4: *5* LeoBody.h_cursor_line_down
    def h_cursor_line_down(self, ch_i: int) -> None:
        """
        From MultiLine.h_cursor_line_down. Never exit.
        """
        # pylint: disable=access-member-before-definition
        #
        # Reset editing mode.
        self.set_box_name('Body Pane')
        # Boilerplate...
        i = self.cursor_line
        j = self.start_display_at
        self.cursor_line = min(len(self.values) - 1, i + 1)
        if self._my_widgets[i - j].task == self.continuation_line:
            if self.slow_scroll:
                self.start_display_at += 1
            else:
                self.start_display_at = self.cursor_line
    #@+node:ekr.20170526114040.5: *5* LeoBody.h_cursor_line_up
    def h_cursor_line_up(self, ch_i: int) -> None:
        """From MultiLine.h_cursor_line_up. Never exit here."""
        # Reset editing mode.
        self.set_box_name('Body Pane')
        self.cursor_line = max(0, self.cursor_line - 1)
    #@+node:ekr.20170604181755.1: *5* LeoBody.h_exit_down
    def h_exit_down(self, ch_i: int) -> Optional[bool]:
        """Called when user leaves the widget to the next widget"""
        if ch_i in (curses.ascii.CR, curses.ascii.NL):
            return False
        self.set_box_name('Body Pane')
        if not self._test_safe_to_exit():
            return False
        self.editing = False
        self.how_exited = EXITED_DOWN
        return None
    #@+node:ekr.20170604181821.1: *5* LeoBody.h_exit_up
    def h_exit_up(self, ch_i: int) -> Optional[bool]:

        self.set_box_name('Body Pane')
        if not self._test_safe_to_exit():
            return False
        # Called when the user leaves the widget to the previous widget
        self.editing = False
        self.how_exited = EXITED_UP
        return None
    #@+node:ekr.20170526114452.2: *5* LeoBody.h_edit_cursor_line_value
    def h_edit_cursor_line_value(self, ch_i: int) -> None:
        """From MultiLineEditable.h_edit_cursor_line_value"""
        self.set_box_name('Body Pane (Editing)')
        continue_line = self.edit_cursor_line_value()
        if continue_line and self.CONTINUE_EDITING_AFTER_EDITING_ONE_LINE:
            self._continue_editing()
    #@+node:ekr.20170604185028.1: *4* LeoBody.delete_line_value
    def delete_line_value(self, ch_i: int=None) -> None:

        c = self.leo_c
        if self.values:
            del self.values[self.cursor_line]
            self.display()
            # #1224:
            c.p.b = ''.join(self.values)
    #@+node:ekr.20170602103122.1: *4* LeoBody.make_contained_widgets
    def make_contained_widgets(self) -> None:
        """
        LeoBody.make_contained_widgets.
        Make widgets and inject the leo_parent ivar for later access to leo_c.
        """
        # pylint: disable=no-member
        trace_widgets = False
        self._my_widgets = []
        height = self.height // self.__class__._contained_widget_height
        # g.trace(self.__class__.__name__, height)
        for h in range(height):
            self._my_widgets.append(
                self._contained_widgets(
                    self.parent,
                    rely=(h * self._contained_widget_height) + self.rely,
                    relx=self.relx,
                    max_width=self.width,
                    max_height=self.__class__._contained_widget_height
            ))
        # Inject leo_parent ivar so the contained widgets can get leo_c later.
        for w in self._my_widgets:
            w.leo_parent = self
        if trace and trace_widgets:
            g.printList(self._my_widgets)
            g.printList(['value: %r' % (z.value) for z in self._my_widgets])
    #@+node:ekr.20170604073733.1: *4* LeoBody.set_box_name
    def set_box_name(self, name: str) -> None:
        """Update the title of the Form surrounding the Leo Body."""
        box = self.leo_box
        box.name = name
        box.update()
    #@+node:ekr.20170526064136.1: *4* LeoBody.set_handlers
    #@@nobeautify
    def set_handlers(self) -> None:
        """LeoBody.set_handlers."""
        # pylint: disable=no-member
        self.handlers = {
            # From InputHandler...
            curses.KEY_BTAB:    self.h_exit_up,
            curses.ascii.TAB:   self.h_exit_down,
            curses.ascii.ESC:   self.h_exit_escape,
            curses.KEY_MOUSE:   self.h_exit_mouse,
            # From MultiLine...
            curses.KEY_DOWN:    self.h_cursor_line_down,
            curses.KEY_END:     self.h_cursor_end,
            curses.KEY_HOME:    self.h_cursor_beginning,
            curses.KEY_NPAGE:   self.h_cursor_page_down,
            curses.KEY_PPAGE:   self.h_cursor_page_up,
            curses.KEY_UP:      self.h_cursor_line_up,
            # From MultiLineEditable...
                # ord('i'):     self.h_insert_value,
                # ord('o'):     self.h_insert_next_line,
            # New bindings...
            ord('d'):           self.delete_line_value,
            ord('e'):           self.h_edit_cursor_line_value,
        }
        # self.dump_handlers()
    #@+node:ekr.20170606100707.1: *4* LeoBody.update_body (cursesGui2)
    def update_body(self, ins: int, s: str) -> None:
        """
        Update self.values and p.b and vnode ivars after the present line changes.
        """
        # pylint: disable=no-member,access-member-before-definition
        trace = False and not g.unitTesting
        c = self.leo_c
        p, u, v = c.p, c.undoer, c.p.v
        undoType = 'update-body'
        bunch = u.beforeChangeBody(p)
        i = self.cursor_line
        wrapper = c.frame.body.wrapper
        assert isinstance(wrapper, BodyWrapper), repr(wrapper)
        lines = self.values
        if trace:
            g.trace(i, len(lines), s.endswith('\n'), repr(s))
            g.trace(g.callers())
        head = lines[:i]
        tail = lines[i + 1 :]
        if i < len(lines):
            if not s.endswith('\n'):
                s = s + '\n'
            aList = head + [s] + tail
            self.values = aList
            c.p.b = ''.join(aList)
            v.selectionLength = 0
            v.selectionStart = ins
            wrapper.ins = ins
            wrapper.sel = ins, ins
            u.afterChangeBody(p, undoType, bunch)
        elif i == len(lines):
            aList = head + [s]
            self.values = aList
            c.p.b = ''.join(aList)
            v.selectionLength = 0
            v.selectionStart = ins
            wrapper.ins = ins
            wrapper.sel = ins, ins
            u.afterChangeBody(p, undoType, bunch)
        else:
            g.trace('Can not happen', i, len(lines), repr(s))
            v.selectionLength = 0
            v.selectionStart = 0
        if g.splitLines(c.p.b) != self.values:
            g.trace('self.values')
            g.printList(self.values)
            g.trace('g.splitLines(c.p.b)')
            g.printList(g.splitLines(c.p.b))
    #@-others
#@+node:ekr.20170603103946.1: *3* class LeoLog (npyscreen.MultiLineEditable)
class LeoLog(npyscreen.MultiLineEditable):

    continuation_line = "- more -"  # value of contination line.
    _contained_widgets = LeoLogTextfield

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.cursor_line: int
        self.start_display_at: int
        self.leo_parent: Wrapper
        self.set_handlers()
        self.leo_box: Wrapper = None
        self.leo_c: Cmdr = None
        # createCursesLog sets the leo_c and leo_box ivars.

    #@+others
    #@+node:ekr.20170604184928.2: *4* LeoLog.delete_line_value
    def delete_line_value(self, ch_i: int=None) -> None:
        if self.values:
            del self.values[self.cursor_line]
            self.display()
    #@+node:ekr.20170604183417.1: *4*  LeoLog handlers
    #@+node:ekr.20170603103946.32: *5* LeoLog.h_cursor_line_down
    def h_cursor_line_down(self, ch_i: int) -> None:
        """
        From MultiLine.h_cursor_line_down. Never exit.
        """
        # pylint: disable=no-member,access-member-before-definition
        trace = False and not g.unitTesting
        self.set_box_name('Log Pane')
        i = self.cursor_line
        j = self.start_display_at
        n = len(self.values)
        n2 = len(self._my_widgets)
        # Scroll only if there are more lines left.
        if i < n - 2:
            # Update self.cursor_line
            self.cursor_line = i2 = max(0, min(i + 1, n - 1))
            # Update self.start_display_at.
            if self._my_widgets[i - j].task == self.continuation_line:
                self.start_display_at = min(j, max(i2 + 1, n2 - 1))
        if trace:
            g.trace('n: %s, start: %s, line: %s' % (
                n, self.start_display_at, self.cursor_line))
    #@+node:ekr.20170603103946.31: *5* LeoLog.h_cursor_line_up
    def h_cursor_line_up(self, ch_i: int) -> None:
        """From MultiLine.h_cursor_line_up. Never exit here."""
        self.set_box_name('Log Pane')
        self.cursor_line = max(0, self.cursor_line - 1)

    #@+node:ekr.20170604061933.4: *5* LeoLog.h_edit_cursor_line_value
    def h_edit_cursor_line_value(self, ch_i: int) -> None:
        """From MultiLineEditable.h_edit_cursor_line_value"""
        self.set_box_name('Log Pane (Editing)')
        continue_line = self.edit_cursor_line_value()
        if continue_line and self.CONTINUE_EDITING_AFTER_EDITING_ONE_LINE:
            self._continue_editing()
    #@+node:ekr.20170604113733.2: *5* LeoLog.h_exit_down
    def h_exit_down(self, ch_i: int) -> Optional[bool]:
        """Called when user leaves the widget to the next widget"""
        trace = False and not g.unitTesting
        if ch_i in (curses.ascii.CR, curses.ascii.NL):
            return False
        if trace:
            g.trace('(LeoLog) safe:', self._test_safe_to_exit())
            g.trace(g.callers())
        self.set_box_name('Log Pane')
        if not self._test_safe_to_exit():
            return False
        self.editing = False
        self.how_exited = EXITED_DOWN
        return None
    #@+node:ekr.20170604113733.4: *5* LeoLog.h_exit_up
    def h_exit_up(self, ch_i: int) -> Optional[bool]:
        self.set_box_name('Log Pane')
        if not self._test_safe_to_exit():
            return False
        # Called when the user leaves the widget to the previous widget
        self.editing = False
        self.how_exited = EXITED_UP
        return None
    #@+node:ekr.20170603103946.34: *4* LeoLog.make_contained_widgets
    def make_contained_widgets(self) -> None:
        """
        LeoLog.make_contained_widgets.
        Make widgets and inject the leo_parent ivar for later access to leo_c.
        """
        # pylint: disable=no-member
        trace = False
        trace_widgets = False
        self._my_widgets = []
        height = self.height // self.__class__._contained_widget_height
        if trace:
            g.trace(self.__class__.__name__, height)
        for h in range(height):
            self._my_widgets.append(
                self._contained_widgets(
                    self.parent,
                    rely=(h * self._contained_widget_height) + self.rely,
                    relx=self.relx,
                    max_width=self.width,
                    max_height=self.__class__._contained_widget_height
            ))
        # Inject leo_parent ivar so the contained widgets can get leo_c later.
        for w in self._my_widgets:
            w.leo_parent = self
        if trace and trace_widgets:
            g.printList(self._my_widgets)
            g.printList(['value: %r' % (z.value) for z in self._my_widgets])
    #@+node:ekr.20170604073322.1: *4* LeoLog.set_box_name
    def set_box_name(self, name: str) -> None:
        """Update the title of the Form surrounding the Leo Log."""
        box = self.leo_box
        box.name = name
        box.update()
    #@+node:ekr.20170603103946.33: *4* LeoLog.set_handlers
    def set_handlers(self) -> None:
        """LeoLog.set_handlers."""
        # pylint: disable=no-member
        self.handlers = {
            # From InputHandler...
            curses.KEY_BTAB: self.h_exit_up,
            curses.KEY_MOUSE: self.h_exit_mouse,
            curses.ascii.CR: self.h_exit_down,
            curses.ascii.ESC: self.h_exit_escape,
            curses.ascii.NL: self.h_exit_down,
            curses.ascii.TAB: self.h_exit_down,
            # From MultiLine...
            curses.KEY_DOWN: self.h_cursor_line_down,
            curses.KEY_END: self.h_cursor_end,
            curses.KEY_HOME: self.h_cursor_beginning,
            curses.KEY_NPAGE: self.h_cursor_page_down,
            curses.KEY_PPAGE: self.h_cursor_page_up,
            curses.KEY_UP: self.h_cursor_line_up,
            # From MultiLineEditable...
                # ord('i'):     self.h_insert_value,
                # ord('o'):     self.h_insert_next_line,
            # New bindings...
            ord('d'): self.delete_line_value,
            ord('e'): self.h_edit_cursor_line_value,
        }
        # dump_handlers(self)
    #@+node:ekr.20170708181422.1: *4* LeoLog.firstScroll
    def firstScroll(self) -> None:
        """Scroll the log pane so the last lines are in view."""
        # Fix #508: Part 0.
        n = len(self.values)
        self.cursor_line = max(0, n - 2)
        self.start_display_at = max(0, n - len(self._my_widgets))
        self.update()
    #@-others
#@+node:ekr.20170507194035.1: *3* class LeoForm (npyscreen.Form)
class LeoForm(npyscreen.Form):

    OK_BUTTON_TEXT = 'Quit Leo'
    OKBUTTON_TYPE: Wrapper = QuitButton
    how_exited = None

    def display(self, *args: Any, **kwargs: Any) -> None:
        changed = any(z.c.isChanged() for z in g.app.windowList)
        c = g.app.log.c
        self.name = 'Welcome to Leo: %s%s' % (
            '(changed) ' if changed else '',
            c.fileName() if c else '')
        super().display(*args, **kwargs)
#@+node:ekr.20170510092721.1: *3* class LeoMiniBuffer (npyscreen.Textfield)
class LeoMiniBuffer(npyscreen.Textfield):
    """An npyscreen class representing Leo's minibuffer, with binding."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.value: str
        self.leo_c: Cmdr = None  # Set later
        self.leo_wrapper: Wrapper = None  # Set later.
        self.leo_completion_index: int = 0
        self.leo_completion_list: List[str] = []
        self.leo_completion_prefix: str = ''
        self.set_handlers()

    #@+others
    #@+node:ekr.20170510172335.1: *4* LeoMiniBuffer.Handlers
    #@+node:ekr.20171201054825.1: *5* LeoMiniBuffer.do_tab_completion
    def do_tab_completion(self) -> None:
        """Perform tab completion."""
        trace = False and not g.unitTesting
        c = self.leo_c
        command: str = self.value
        i = self.leo_completion_index
        if trace:
            g.trace('command: %r prefix: %r' % (command, self.leo_completion_prefix))
        # Restart the completions if necessary.
        if not command.startswith(self.leo_completion_prefix):
            i = 0
        if i == 0:
            # Compute new completions.
            self.leo_completion_prefix = command
            command_list = sorted(c.k.c.commandsDict.keys())
            tab_list, common_prefix = g.itemsMatchingPrefixInList(command, command_list)
            self.leo_completion_list = tab_list
            if trace:
                g.printObj(tab_list)
        # Update the index and the widget.
        if self.leo_completion_list:
            tab_list = self.leo_completion_list
            self.value = tab_list[i]
            i = 0 if i + 1 >= len(tab_list) else i + 1
            self.leo_completion_index = i
            self.update()
        elif trace:
            g.trace('no completions for', command)
    #@+node:ekr.20170510095136.2: *5* LeoMiniBuffer.h_cursor_beginning
    def h_cursor_beginning(self, ch: str) -> None:

        self.cursor_position = 0
    #@+node:ekr.20170510095136.3: *5* LeoMiniBuffer.h_cursor_end
    def h_cursor_end(self, ch: str) -> None:

        self.cursor_position = len(self.value)
    #@+node:ekr.20170510095136.4: *5* LeoMiniBuffer.h_cursor_left
    def h_cursor_left(self, ch: str) -> None:

        self.cursor_position = max(0, self.cursor_position - 1)
    #@+node:ekr.20170510095136.5: *5* LeoMiniBuffer.h_cursor_right
    def h_cursor_right(self, ch: str) -> None:

        self.cursor_position = min(len(self.value), self.cursor_position + 1)


    #@+node:ekr.20170510095136.6: *5* LeoMiniBuffer.h_delete_left
    def h_delete_left(self, ch: str) -> None:

        n = self.cursor_position
        s = self.value
        if n == 0:
            # Delete the character under the cursor.
            self.value = s[1:]
        else:
            # Delete the character to the left of the cursor
            self.value = s[: n - 1] + s[n:]
            self.cursor_position -= 1
    #@+node:ekr.20171201053817.1: *5* LeoMiniBuffer.h_exit_down
    def h_exit_down(self, ch: str) -> Optional[bool]:
        """LeoMiniBuffer.h_exit_down.  Override InputHandler.h_exit_down."""
        trace = False and not g.unitTesting
        c = self.leo_c
        if trace:
            g.trace('(LeoMiniBuffer)', repr(ch))
        if c and self.value.strip():
            self.do_tab_completion()
        else:
            # Restart completion cycling.
            self.leo_completion_index = 0
            # The code in InputHandler.h_exit_down.
            if not self._test_safe_to_exit():
                return False
            self.editing = False
            self.how_exited = EXITED_DOWN
        return None
    #@+node:ekr.20170510095136.7: *5* LeoMiniBuffer.h_insert
    def h_insert(self, ch: int) -> None:

        n = self.cursor_position + 1
        s = self.value
        self.value = s[:n] + chr(ch) + s[n:]
        self.cursor_position += 1
    #@+node:ekr.20170510100003.1: *5* LeoMiniBuffer.h_return (executes command) (complex kwargs!)
    def h_return(self, ch: str) -> None:
        """
        Handle the return key in the minibuffer.
        Send the contents to k.masterKeyHandler.
        """
        c = self.leo_c
        k = c.k
        val = self.value.strip()
        self.value = ''
        self.update()
        # g.trace('===== inState: %r val: %r' % (k.inState(), val))
        commandName = val
        # This may be changed by the command.
        c.frame.tree.set_status_line(c.p)
        if k.inState():
            # Handle the key.
            k.w = self.leo_wrapper
            k.arg = val
            g.app.gui.curses_gui_arg = val
            k.masterKeyHandler(
                event=KeyEvent(c, char='\n', event='', shortcut='\n', w=None))
            g.app.gui.curses_gui_arg = None
            k.clearState()
        elif commandName == 'repeat-complex-command':
            g.app.gui.repeatComplexCommand(c)
        else:
            # All other alt-x command
            event = KeyEvent(c, char='', event='', shortcut='', w=None)
            c.doCommandByName(commandName, event)  # type:ignore
            # Support repeat-complex-command.
            c.setComplexCommand(commandName=commandName)
            c.redraw()
        # Do a full redraw, with c.p as the first visible node.
        # g.trace('----- after command')
        g.app.gui.redraw_in_context(c)
    #@+node:ekr.20170510094104.1: *5* LeoMiniBuffer.set_handlers
    def set_handlers(self) -> None:

        # pylint: disable=no-member
        # Override *all* other complex handlers.
        self.complex_handlers = [
            (curses.ascii.isprint, self.h_insert),
        ]
        self.handlers.update({
            # All other keys are passed on.
                # curses.ascii.TAB:    self.h_exit_down,
                # curses.KEY_BTAB:     self.h_exit_up,
            curses.ascii.NL: self.h_return,
            curses.ascii.CR: self.h_return,
            curses.KEY_HOME: self.h_cursor_beginning,  # 262
            curses.KEY_END: self.h_cursor_end,  # 358.
            curses.KEY_LEFT: self.h_cursor_left,
            curses.KEY_RIGHT: self.h_cursor_right,
            curses.ascii.BS: self.h_delete_left,
            curses.KEY_BACKSPACE: self.h_delete_left,
        })
    #@-others
#@+node:ekr.20171129194909.1: *3* class LeoStatusLine (npyscreen.Textfield)
class LeoStatusLine(npyscreen.Textfield):
    """An npyscreen class representing Leo's status line"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # These are injected later.
        self.leo_c: Cmdr = None
        self.leo_wrapper: Wrapper = None
        # Use the default handlers.
            # self.set_handlers()

    #@+others
    #@-others
#@+node:ekr.20170506035146.1: *3* class LeoMLTree (npyscreen.MLTree, object)
class LeoMLTree(npyscreen.MLTree):

    # pylint: disable=used-before-assignment
    _contained_widgets: Wrapper = LeoTreeLine
    continuation_line = "- more -"  # value of contination line.
    _cached_tree: "LeoTreeData"
    _cached_tree_as_list: List["LeoTreeData"]
    start_display_at: int
    cursor_line: int

    # Note: The startup sequence sets leo_c and the value property/ivar.

    #@+others
    #@+node:ekr.20170510171826.1: *4* LeoMLTree.Entries
    #@+node:ekr.20170506044733.6: *5* LeoMLTree.delete_line
    def delete_line(self) -> None:

        trace = False
        trace_values = True
        node = self.values[self.cursor_line]
        assert isinstance(node, LeoTreeData), repr(node)
        if trace:
            g.trace('before', node.content)
            if trace_values:
                self.dump_values()
        if native:
            p = node.content
            assert p and isinstance(p, Position), repr(p)
            if p.hasParent() or p.hasNext() or p.hasBack():
                p.doDelete()
                self.values.clear_cache()
            else:
                g.trace('Can not delete the last top-level node')
                return
        else:
            parent = node.get_parent()
            grand_parent = parent and parent._parent
            if not grand_parent and len(parent._children) == 1:
                g.trace('Can not delete the last top-level node')
                return
            # Remove node and all its descendants.
            i = self.cursor_line
            nodes = [(i, node)]
            j = i + 1
            while j < len(self.values):
                node2 = self.values[j]
                if node.is_ancestor_of(node2):
                    nodes.append((j, node2),)
                    j += 1
                else:
                    break
            for j, node2 in reversed(nodes):
                del self.values[j]
            # Update the parent.
            parent._children = [z for z in parent._children if z != node]
        # Clearing these caches suffice to do a proper redraw
        self._last_values = None
        self._last_value = None
        if trace and trace_values:
            g.trace('after')
            self.dump_values()
        # This is widget.display:
        # (when not self.hidden)
        # self.update()
        # LeoMLTree.update or MultiLine.update
        # self.parent.refresh()
        # LeoForm.refresh
        self.display()
    #@+node:ekr.20170507171518.1: *5* LeoMLTree.dump_code/values/widgets
    def dump_code(self, code: int) -> str:
        d = {
            -2: 'left', -1: 'up', 1: 'down', 2: 'right',
            127: 'escape', 130: 'mouse',
        }
        return d.get(code) or 'unknown how_exited: %r' % code

    def dump_values(self) -> None:

        def info(z: Any) -> str:
            return '%15s: %s' % (z._parent.get_content(), z.get_content())

        g.printList([info(z) for z in self.values])

    def dump_widgets(self) -> None:

        def info(z: Any) -> str:
            return '%s.%s' % (id(z), z.__class__.__name__)

        g.printList([info(z) for z in self._my_widgets])
    #@+node:ekr.20170506044733.4: *5* LeoMLTree.edit_headline
    def edit_headline(self) -> bool:

        trace = False and not g.unitTesting
        assert self.values, g.callers()
        try:
            active_line: "LeoTreeLine" = self._my_widgets[(self.cursor_line - self.start_display_at)]
            assert isinstance(active_line, LeoTreeLine)
            if trace:
                g.trace('LeoMLTree.active_line: %r' % active_line)
        except IndexError:
            # pylint: disable=pointless-statement
            self._my_widgets[0]  # Does this have something to do with weakrefs?
            self.cursor_line = 0
            self.insert_line()
            return True
        active_line.highlight = False
        active_line.edit()
        if native:
            self.values.clear_cache()
        else:
            try:
                # pylint: disable=unsupported-assignment-operation
                self.values[self.cursor_line] = active_line.value
            except IndexError:
                self.values.append(active_line.value)
                if not self.cursor_line:
                    self.cursor_line = 0
                self.cursor_line = len(self.values) - 1
        self.reset_display_cache()
        self.display()
        return True
    #@+node:ekr.20170523113530.1: *5* LeoMLTree.get_nth_visible_position
    def get_nth_visible_position(self, n: int) -> Optional[Position]:
        """Return the n'th visible position."""
        c = self.leo_c
        limit, junk = c.visLimit()
        p = limit.copy() if limit else c.rootPosition()
        i = 0
        while p:
            if i == n:
                return p
            p.moveToVisNext(c)
            i += 1
        g.trace('Can not happen', n)
        return None
    #@+node:ekr.20171128191134.1: *5* LeoMLTree.select_leo_node
    def select_leo_node(self, p: Position) -> None:
        """
        Set .start_display_at and .cursor_line ivars to display node p, with 2
        lines of preceding context if possible.
        """
        trace = False and not g.unitTesting
        c = self.leo_c
        limit, junk = c.visLimit()
        p2 = limit.copy() if limit else c.rootPosition()
        i = 0
        while p2:
            if p2 == p:
                if trace:
                    g.trace('FOUND', i, p.h)
                # Provide context if possible.
                self.cursor_line = i
                for j in range(2):
                    if p.hasVisBack(c):
                        p.moveToVisBack(c)
                        i -= 1
                self.start_display_at = i
                return
            p2.moveToVisNext(c)
            i += 1
        if trace:
            # Can happen during unit tests.
            g.trace('Not found', p and p.h)
    #@+node:ekr.20170514065422.1: *5* LeoMLTree.intraFileDrop
    def intraFileDrop(self, fn: str, p1: Position, p2: Position) -> None:
        pass
    #@+node:ekr.20170506044733.2: *5* LeoMLTree.new_mltree_node
    def new_mltree_node(self) -> Position:
        """
        Insert a new outline TreeData widget at the current line.
        As with Leo, insert as the first child of the current line if
        the current line is expanded. Otherwise insert after the current line.
        """
        trace = False
        trace_values = True
        node = self.values[self.cursor_line]
        headline = 'New headline'
        if node.has_children() and node.expanded:
            node = node.new_child_at(index=0, content=headline)
        elif node.get_parent():
            parent = node.get_parent()
            node = parent.new_child(content=headline)
        else:
            parent = self.hidden_root_node
            index = parent._children.index(node)
            node = parent.new_child_at(index=index, content=headline)
        if trace:
            g.trace('LeoMLTree: line: %s %s' % (self.cursor_line, headline))
            if trace_values:
                self.dump_values()
        return node
    #@+node:ekr.20170506044733.5: *5* LeoMLTree.insert_line
    def insert_line(self) -> None:
        """Insert an MLTree line and mark c changed."""
        trace = False
        c = self.leo_c
        c.changed = True  # Just set the changed bit.
        # c.p.setDirty()
        n = 0 if self.cursor_line is None else self.cursor_line
        if trace:
            g.trace('line: %r', n)
        if native:
            data = self.values[n]  # data is a LeoTreeData
            p = data.content
            assert p and isinstance(p, Position)
            if p.hasChildren() and p.isExpanded():
                p2 = p.insertAsFirstChild()
            else:
                p2 = p.insertAfter()
            p2.h = 'New Headline'
            self.cursor_line += 1
            c.selectPosition(p2)
            g.app.gui.redraw_in_context(c)
        else:
            self.values.insert(n + 1, self.new_mltree_node())
            self.cursor_line += 1
        self.display()
        self.edit_headline()

    #@+node:ekr.20170506045346.1: *4* LeoMLTree.Handlers
    # These insert or delete entire outline nodes.
    #@+node:ekr.20170523112839.1: *5* LeoMLTree.handle_mouse_event
    def handle_mouse_event(self, mouse_event: Event) -> None:
        """Called from InputHandler.h_exit_mouse."""
        # pylint: disable=no-member
        #
        # From MultiLine...
        data = self.interpret_mouse_event(mouse_event)
        mouse_id, rel_x, rel_y, z, bstate = data
        self.cursor_line = (
            rel_y //
            self._contained_widget_height + self.start_display_at
        )
        # Now, set the correct position.
        if native:
            c = self.leo_c
            p = self.get_nth_visible_position(self.cursor_line)
            c.frame.tree.select(p)
    #@+node:ekr.20170516055435.4: *5* LeoMLTree.h_collapse_all
    def h_collapse_all(self, ch: str) -> None:

        if native:
            c = self.leo_c
            for p in c.all_unique_positions():
                p.v.contract()
            self.values.clear_cache()
        else:
            for v in self._walk_tree(self._myFullValues, only_expanded=True):
                v.expanded = False
        self._cached_tree = None
        self.cursor_line = 0
        self.display()

    #@+node:ekr.20170516055435.2: *5* LeoMLTree.h_collapse_tree
    def h_collapse_tree(self, ch: str) -> None:

        node = self.values[self.cursor_line]
        if native:
            p = node.content
            assert p and isinstance(p, Position), repr(p)
            p.contract()
            self.values.clear_cache()
        else:
            if node.expanded and self._has_children(node):  # Collapse the node.
                node.expanded = False
            elif 0:  # Optional.
                # Collapse all the children.
                depth = self._find_depth(node) - 1
                cursor_line = self.cursor_line - 1
                while cursor_line >= 0:
                    if depth == self._find_depth(node):
                        self.cursor_line = cursor_line
                        node.expanded = False
                        break
                    else:
                        cursor_line -= 1
        self._cached_tree = None  # Invalidate the display cache.
        self.display()
    #@+node:ekr.20170513091821.1: *5* LeoMLTree.h_cursor_line_down
    def h_cursor_line_down(self, ch: str) -> None:

        c = self.leo_c
        self.cursor_line = min(len(self.values) - 1, self.cursor_line + 1)
        if native:
            p = self.get_nth_visible_position(self.cursor_line)
            c.frame.tree.select(p)
    #@+node:ekr.20170513091928.1: *5* LeoMLTree.h_cursor_line_up
    def h_cursor_line_up(self, ch: str) -> None:

        c = self.leo_c
        self.cursor_line = max(0, self.cursor_line - 1)
        if native:
            p = self.get_nth_visible_position(self.cursor_line)
            c.frame.tree.select(p)
    #@+node:ekr.20170506044733.12: *5* LeoMLTree.h_delete
    def h_delete(self, ch: str) -> None:

        c = self.leo_c
        c.changed = True  # Just set the changed bit.
        self.delete_line()
        if native:
            p = self.get_nth_visible_position(self.cursor_line)
            c.frame.tree.select(p)
    #@+node:ekr.20170506044733.10: *5* LeoMLTree.h_edit_headline
    def h_edit_headline(self, ch: str) -> None:
        """Called when the user types "h"."""
        # Remember the starting headline, for CTree.onHeadChanged.
        self.edit_headline()
    #@+node:ekr.20170516055435.5: *5* LeoMLTree.h_expand_all
    def h_expand_all(self, ch: str) -> None:

        if native:
            c = self.leo_c
            for p in c.all_unique_positions():
                p.v.expand()
            self.values.clear_cache()
        else:
            for v in self._walk_tree(self._myFullValues, only_expanded=False):
                v.expanded = True
        self._cached_tree = None
        self.cursor_line = 0
        self.display()
    #@+node:ekr.20170516055435.3: *5* LeoMLTree.h_expand_tree
    def h_expand_tree(self, ch: str) -> None:

        node = self.values[self.cursor_line]
        if native:
            p = node.content
            assert p and isinstance(p, Position), repr(p)
            p.expand()  # Don't use p.v.expand()
            self.values.clear_cache()
        else:
            # First, expand the node.
            if not node.expanded:
                node.expanded = True
            elif 0:  # Optional.
                # Next, expand all children.
                for z in self._walk_tree(node, only_expanded=False):
                    z.expanded = True
        self._cached_tree = None  # Invalidate the cache.
        self.display()
    #@+node:ekr.20170506044733.11: *5* LeoMLTree.h_insert
    def h_insert(self, ch: str) -> None:

        self.insert_line()
        if native:
            c = self.leo_c
            p = self.get_nth_visible_position(self.cursor_line)
            c.frame.tree.select(p)
    #@+node:ekr.20170506035413.1: *5* LeoMLTree.h_move_left
    def h_move_left(self, ch: str) -> None:

        trace = False and not g.unitTesting
        node = self.values[self.cursor_line]
        if not node:
            g.trace('no node', self.cursor_line, repr(node))
            return
        if native:
            c = self.leo_c
            p = node.content
            assert p and isinstance(p, Position), repr(p)
            if p.hasChildren() and p.isExpanded():
                self.h_collapse_tree(ch)
                self.values.clear_cache()
            elif p.hasParent():
                parent = p.parent()
                parent.contract()  # Don't use parent.v.contract.
                # Set the cursor to the parent's index.
                i = self.cursor_line - 1
                while i >= 0:
                    node2 = self.values[i]
                    if node2 is None:
                        g.trace('oops: no node2', i)
                        break
                    p2 = node2.content
                    if p2 == parent:
                        break
                    i -= 1
                self.cursor_line = max(0, i)
                if trace:
                    g.trace('new line', self.cursor_line)
                self.values.clear_cache()
                self._cached_tree = None  # Invalidate the cache.
                self.display()
                c.frame.tree.select(parent)
            elif trace:
                # This is what Leo does.
                g.trace('no parent')
        else:
            if self._has_children(node) and node.expanded:
                self.h_collapse_tree(ch)
            else:
                self.h_cursor_line_up(ch)
    #@+node:ekr.20170506035419.1: *5* LeoMLTree.h_move_right
    def h_move_right(self, ch: str) -> None:

        node = self.values[self.cursor_line]
        if not node:
            g.trace('no node')
            return
        if native:
            p = node.content
            assert p and isinstance(p, Position), repr(p)
            if p.hasChildren():
                if p.isExpanded():
                    self.h_cursor_line_down(ch)
                else:
                    self.h_expand_tree(ch)
            else:
                pass  # This is what Leo does.
        else:
            if self._has_children(node):
                if node.expanded:
                    self.h_cursor_line_down(ch)
                else:
                    self.h_expand_tree(ch)
            else:
                self.h_cursor_line_down(ch)
    #@+node:ekr.20170507175304.1: *5* LeoMLTree.set_handlers
    #@@nobeautify
    def set_handlers(self) -> None:

        # pylint: disable=no-member
        d = {
            curses.KEY_MOUSE:   self.h_exit_mouse,
            curses.KEY_BTAB:    self.h_exit_up,
            curses.KEY_DOWN:    self.h_cursor_line_down,
            curses.KEY_LEFT:    self.h_move_left,
            curses.KEY_RIGHT:   self.h_move_right,
            curses.KEY_UP:      self.h_cursor_line_up,
            curses.ascii.TAB:   self.h_exit_down,
            ord('d'):           self.h_delete,
            ord('e'):           self.h_edit_headline,
            ord('i'):           self.h_insert,
            # curses.ascii.CR:        self.h_edit_cursor_line_value,
            # curses.ascii.NL:        self.h_edit_cursor_line_value,
            # curses.ascii.SP:        self.h_edit_cursor_line_value,
            # curses.ascii.DEL:       self.h_delete_line_value,
            # curses.ascii.BS:        self.h_delete_line_value,
            # curses.KEY_BACKSPACE:   self.h_delete_line_value,
            # ord('<'): self.h_collapse_tree,
            # ord('>'): self.h_expand_tree,
            # ord('['): self.h_collapse_tree,
            # ord(']'): self.h_expand_tree,
            # ord('{'): self.h_collapse_all,
            # ord('}'): self.h_expand_all,
            # ord('h'): self.h_collapse_tree,
            # ord('l'): self.h_expand_tree,
        }
        # self.handlers.update(d)
        # dump_handlers(self)
        self.handlers = d
    #@+node:ekr.20170516100256.1: *5* LeoMLTree.set_up_handlers
    def set_up_handlers(self) -> None:
        super().set_up_handlers()
        assert not hasattr(self, 'hidden_root_node'), repr(self)
        self.leo_c = None  # Set later.
        self.currentItem = None  # Used by CoreTree class.
        self.hidden_root_node = None
        self.set_handlers()

    #@+node:ekr.20170513032502.1: *4* LeoMLTree.update & helpers
    def update(self, clear: bool=True, forceInit: bool=False) -> None:
        """Redraw the tree."""
        # This is a major refactoring of MultiLine.update.
        trace = False and not g.unitTesting
        c = self.leo_c
        if trace:
            g.trace('(LeoMLTree)', c.p and c.p.h)
            g.trace(g.callers())
        # Ensures that the selected node is always highlighted.
        self.select_leo_node(c.p)
        if self.editing or forceInit:
            self._init_update()
        if self._must_redraw(clear):
            self._redraw(clear)
        # Remember the previous values.
        self._last_start_display_at = self.start_display_at
        self._last_cursor_line = self.cursor_line
        if native:
            pass
        else:
            self._last_values = copy.copy(self.values)
            self._last_value = copy.copy(self.value)
    #@+node:ekr.20170513122253.1: *5* LeoMLTree._init_update
    def _init_update(self) -> None:
        """Put self.cursor_line and self.start_display_at in range."""
        # pylint: disable=access-member-before-definition,consider-using-max-builtin
        display_length = len(self._my_widgets)
        self.cursor_line = max(0, min(len(self.values) - 1, self.cursor_line))
        if self.slow_scroll:
            # Scroll by lines.
            if self.cursor_line > self.start_display_at + display_length - 1:
                self.start_display_at = self.cursor_line - (display_length - 1)
            if self.cursor_line < self.start_display_at:
                self.start_display_at = self.cursor_line
        else:
            # Scroll by pages.
            if self.cursor_line > self.start_display_at + (display_length - 2):
                self.start_display_at = self.cursor_line
            if self.cursor_line < self.start_display_at:
                self.start_display_at = self.cursor_line - (display_length - 2)
                if self.start_display_at < 0:
                    self.start_display_at = 0
    #@+node:ekr.20170513123010.1: *5* LeoMLTree._must_redraw
    def _must_redraw(self, clear: bool) -> Generator:
        """Return a list of reasons why we must redraw."""
        trace = False and not g.unitTesting
        table = (
            ('cache', not self._safe_to_display_cache or self.never_cache),
            ('value', self._last_value is not self.value),
            ('values', self.values != self._last_values),
            ('start', self.start_display_at != self._last_start_display_at),
            ('clear', not clear),
            ('cursor', self._last_cursor_line != self.cursor_line),
            ('filter', self._last_filter != self._filter),
            ('editing', not self.editing),
        )
        reasons = (reason for (reason, cond) in table if cond)
        if trace:
            g.trace('line: %2s %-20s %s' % (
                self.cursor_line,
                ','.join(reasons),
                self.values[self.cursor_line].content))
        return reasons
    #@+node:ekr.20170513122427.1: *5* LeoMLTree._redraw & helpers
    def _redraw(self, clear: bool) -> None:
        """Do the actual redraw."""
        trace = False and not g.unitTesting
        # pylint: disable=no-member
        #
        # self.clear is Widget.clear. It does *not* use _myWidgets.
        if trace:
            g.trace('start: %r cursor: %r' % (self.start_display_at, self.cursor_line))
        if (clear is True or
            clear is None and self._last_start_display_at != self.start_display_at
        ):
            self.clear()
        self._last_start_display_at = start = self.start_display_at
        i = self.start_display_at
        for line in self._my_widgets[:-1]:
            assert isinstance(line, LeoTreeLine), repr(line)
            self._print_line(line, i)
            line.update(clear=True)
            i += 1
        # Do the last line
        line = self._my_widgets[-1]
        if len(self.values) <= i + 1:
            self._print_line(line, i)
            line.update(clear=False)
        elif len((self._my_widgets) * self._contained_widget_height) < self.height:
            self._print_line(line, i)
            line.update(clear=False)
            self._put_continuation_line()
        else:
            line.clear()  # This is Widget.clear.
            self._put_continuation_line()
        # Assert that print_line leaves start_display_at unchanged.
        assert start == self.start_display_at, (start, self.start_display_at)
        # Finish
        if self.editing:
            line = self._my_widgets[(self.cursor_line - start)]
            line.highlight = True
            line.update(clear=True)
    #@+node:ekr.20170513032717.1: *6* LeoMLTree._print_line
    def _print_line(self, line: str, i: int) -> None:

        # if self.widgets_inherit_color and self.do_colors():
            # line.color = self.color
        self._set_line_values(line, i)  # Sets line.value
        if line.value is not None:
            assert isinstance(line.value, LeoTreeData), repr(line.value)
        self._set_line_highlighting(line, i)
    #@+node:ekr.20170513102428.1: *6* LeoMLTree._put_continuation_line
    def _put_continuation_line(self) -> None:
        """Print the line indicating there are more lines left."""
        s = self.continuation_line
        x = self.relx
        y = self.rely + self.height - 1
        if self.do_colors():
            style = self.parent.theme_manager.findPair(self, 'CONTROL')
            self.parent.curses_pad.addstr(y, x, s, style)
        else:
            self.parent.curses_pad.addstr(y, x, s)
    #@+node:ekr.20170513075423.1: *6* LeoMLTree._set_line_values
    def _set_line_values(self, line: str, i: int) -> None:
        """Set internal values of line using self.values[i] and self.values[i+1]"""
        trace = False
        trace_ok = True
        trace_empty = True
        line.leo_c = self.leo_c  # Inject the ivar.
        values = self.values
        n = len(values)
        val = values[i] if 0 <= i < n else None
        if trace:
            g.trace(repr(val))
        if val is None:
            line._tree_depth = False
            line._tree_depth_next = False
            line._tree_expanded = False
            line._tree_has_children = False
            line._tree_ignore_root = None
            line._tree_last_line = True
            line._tree_real_value = None
            line._tree_sibling_next = False
            line.value = None
            if trace and trace_empty:
                g.trace(i, n, '<empty>', repr(val))
            return
        assert isinstance(val, LeoTreeData), repr(val)
        # Aliases
        val1 = values[i + 1] if i + 1 < n else None
        val1_depth = val1.find_depth() if val1 else False
        # Common settings.
        line._tree_depth = val.find_depth()
        line._tree_depth_next = val1_depth
        line._tree_ignore_root = self._get_ignore_root(self._myFullValues)
        line._tree_sibling_next = line._tree_depth == val1_depth
        line._tree_real_value = val
        line.value = val
        if native:
            p = val.content
            assert p and isinstance(p, Position), repr(p)
            line._tree_expanded = p.isExpanded()
            line._tree_has_children = p.hasChildren()
            line._tree_last_line = not p.hasNext()
        else:
            line._tree_expanded = val.expanded
            line._tree_has_children = bool(val._children)
            line._tree_last_line = not bool(line._tree_sibling_next)
        if trace and trace_ok:
            content = line.value.content
            s = content.h if native else content
            g.trace(i, n, s)
    #@+node:ekr.20170516101203.1: *4* LeoMLTree.values
    if native:
        _myFullValues = LeoTreeData()
        values = None
    else:
        #
        # This property converts the (possibly cached) result of converting
        # the root node (_myFullValues) and its *visible* decendants to a list.
        # To invalidate the cache, set __cached_tree = None
        #@+others
        #@+node:ekr.20170517142822.1: *5* _getValues
        def _getValues(self) -> List["LeoTreeData"]:
            """
            Return the (possibly cached) list returned by self._myFullValues.get_tree_as_list().

            Setting _cached_tree to None invalidates the cache.
            """
            # pylint: disable=access-member-before-definition
            if getattr(self, '_cached_tree', None):
                return self._cached_tree_as_list
            self._cached_tree = self._myFullValues
            self._cached_tree_as_list = self._myFullValues.get_tree_as_list()
            return self._cached_tree_as_list
        #@+node:ekr.20170518054457.1: *5* _setValues
        def _setValues(self, tree: "LeoTreeData") -> None:
            self._myFullValues = tree or LeoTreeData()
        #@-others
        values = property(_getValues, _setValues)
    #@-others
#@+node:ekr.20170517072429.1: *3* class LeoValues (npyscreen.TreeData)
class LeoValues(npyscreen.TreeData):
    """
    A class to replace the MLTree.values property.
    This is formally an subclass of TreeData.
    """

    #@+others
    #@+node:ekr.20170619070717.1: *4* values.__init__
    def __init__(self, c: Cmdr, tree: "LeoTreeData") -> None:
        """Ctor for LeoValues class."""
        super().__init__()  # Init the base class.
        self.c: Cmdr = c  # The commander of this outline.
        self.data_cache: Dict[int, "LeoTreeData"] = {}  # Keys are ints, values are LeoTreeData objects.
        self.last_generation = -1  # The last value of c.frame.tree.generation.
        self.last_len = 0  # The last computed value of the number of visible nodes.
        self.n_refreshes = 0  # Number of calls to refresh_cache.
        self.tree: "LeoTreeData" = tree  # not used here.
    #@+node:ekr.20170517090738.1: *4* values.__getitem__ and get_data
    def __getitem__(self, n: int) -> "LeoTreeData":
        """Called from LeoMLTree._setLineValues."""
        return self.get_data(n)

    def get_data(self, n: int) -> "LeoTreeData":
        """Return a LeoTreeData for the n'th visible position of the outline."""
        c = self.c
        # This will almost always be true, because __len__ updates the cache.
        if self.last_len > -1 and c.frame.tree.generation == self.last_generation:
            return self.data_cache.get(n)
        self.refresh_cache()
        data = self.data_cache.get(n)
        g.trace('uncached', data)
        return data
    #@+node:ekr.20170518060014.1: *4* values.__len__
    def __len__(self) -> int:
        """
        Return the putative length of the values array,
        that is, the number of visible nodes in the outline.

        Return self.last_len if the tree generations match.
        Otherwise, find and cache all visible node.

        This is called often from the npyscreen core.
        """
        c = self.c
        tree_gen = c.frame.tree.generation
        if self.last_len > -1 and tree_gen == self.last_generation:
            return self.last_len
        self.last_len = self.refresh_cache()
        return self.last_len
    #@+node:ekr.20170519041459.1: *4* values.clear_cache
    def clear_cache(self) -> None:
        """Called only from this file."""
        self.data_cache = {}
        self.last_len = -1
    #@+node:ekr.20170619072048.1: *4* values.refresh_cache
    def refresh_cache(self) -> int:
        """Update all cached values."""
        trace = False
        c = self.c
        self.n_refreshes += 1
        self.clear_cache()
        self.last_generation = c.frame.tree.generation
        n, p = 0, c.rootPosition()
        while p:
            self.data_cache[n] = LeoTreeData(p)
            n += 1
            p.moveToVisNext(c)
        self.last_len = n
        if trace:
            g.trace('%3s vis: %3s generation: %s' % (
                self.n_refreshes, n, c.frame.tree.generation))
        return n
    #@-others
#@+node:ekr.20170522081122.1: ** Wrapper classes
#@+others
#@+node:ekr.20170511053143.1: *3*  class TextMixin: cursesGui2.py
class TextMixin:
    """A minimal mixin class for QTextEditWrapper and QScintillaWrapper classes."""
    #@+others
    #@+node:ekr.20170511053143.2: *4* tm.ctor & helper
    def __init__(self, c: Cmdr=None) -> None:
        """Ctor for TextMixin class"""
        self.c = c
        # self.changingText = False  # A lockout for onTextChanged.
        self.enabled = True
        self.supportsHighLevelInterface = True  # Flag for k.masterKeyHandler and isTextWrapper.
        # self.tags = {}
        # self.configDict = {}  # Keys are tags, values are colors (names or values).
        # self.configUnderlineDict = {}  # Keys are tags, values are True
        # self.virtualInsertPoint = None
        if c:
            self.injectIvars(c)
    #@+node:ekr.20170511053143.3: *5* tm.injectIvars (cursesGui2)
    def injectIvars(self, c: Cmdr) -> Wrapper:
        """Inject standard leo ivars into the QTextEdit or QsciScintilla widget."""
        self.leo_p = c.p.copy() if c.p else None
        self.leo_active = True
        # Inject the scrollbar items into the text widget.
        self.leo_bodyBar = None
        self.leo_bodyXBar = None
        self.leo_chapter = None
        self.leo_frame = None
        self.leo_name = '1'
        self.leo_label = None
        return self
    #@+node:ekr.20170511053143.4: *4* tm.getName
    def getName(self) -> str:
        return self.name  # Essential.
    #@+node:ekr.20170511053143.8: *4* tm.Generic high-level interface
    # These call only wrapper methods.
    #@+node:ekr.20170511053143.13: *5* tm.appendText
    def appendText(self, s: str) -> None:
        """TextMixin"""
        s2 = self.getAllText()
        self.setAllText(s2 + s)
        self.setInsertPoint(len(s2))
    #@+node:ekr.20170511053143.10: *5* tm.clipboard_clear/append
    def clipboard_append(self, s: str) -> None:
        s1 = g.app.gui.getTextFromClipboard()
        g.app.gui.replaceClipboardWith(s1 + s)

    def clipboard_clear(self) -> None:
        g.app.gui.replaceClipboardWith('')
    #@+node:ekr.20170511053143.14: *5* tm.delete
    def delete(self, i: int, j: int=None) -> None:
        """TextMixin"""
        s = self.getAllText()
        if j is None:
            j = i + 1
        # This allows subclasses to use this base class method.
        if i > j:
            i, j = j, i
        self.setAllText(s[:i] + s[j:])
        # Bug fix: Significant in external tests.
        self.setSelectionRange(i, i, insert=i)
    #@+node:ekr.20170511053143.15: *5* tm.deleteTextSelection
    def deleteTextSelection(self) -> None:
        """TextMixin"""
        i, j = self.getSelectionRange()
        self.delete(i, j)
    #@+node:ekr.20170511053143.9: *5* tm.Enable/disable
    def disable(self) -> None:
        self.enabled = False

    def enable(self, enabled: bool=True) -> None:
        self.enabled = enabled
    #@+node:ekr.20170511053143.16: *5* tm.get
    def get(self, i: int, j: int=None) -> str:
        """TextMixin"""
        # 2012/04/12: fix the following two bugs by using the vanilla code:
        # https://bugs.launchpad.net/leo-editor/+bug/979142
        # https://bugs.launchpad.net/leo-editor/+bug/971166
        all_s = self.getAllText()
        if j is None:
            j = i + 1
        return all_s[i:j]
    #@+node:ekr.20170511053143.17: *5* tm.getLastIndex & getLength
    def getLastIndex(self, s: str=None) -> int:
        """TextMixin"""
        return len(self.getAllText()) if s is None else len(s)

    def getLength(self, s: str=None) -> int:
        """TextMixin"""
        return len(self.getAllText()) if s is None else len(s)
    #@+node:ekr.20170511053143.18: *5* tm.getSelectedText
    def getSelectedText(self) -> str:
        """TextMixin"""
        i, j = self.getSelectionRange()
        if i == j:
            return ''
        s = self.getAllText()
        return s[i:j]
    #@+node:ekr.20170511053143.19: *5* tm.insert
    def insert(self, i: int, s: str) -> int:
        """TextMixin"""
        all_s = self.getAllText()
        self.setAllText(all_s[:i] + s + all_s[i:])
        self.setInsertPoint(i + len(s))
        return i
    #@+node:ekr.20170511053143.24: *5* tm.rememberSelectionAndScroll
    def rememberSelectionAndScroll(self) -> None:

        v = self.c.p.v  # Always accurate.
        v.insertSpot = self.getInsertPoint()
        i, j = self.getSelectionRange()
        if i > j:
            i, j = j, i
        assert i <= j
        v.selectionStart = i
        v.selectionLength = j - i
        v.scrollBarSpot = self.getYScrollPosition()
    #@+node:ekr.20170511053143.20: *5* tm.seeInsertPoint
    def seeInsertPoint(self) -> None:
        """Ensure the insert point is visible."""
        # getInsertPoint defined in client classes.
        self.see(self.getInsertPoint())
    #@+node:ekr.20170511053143.21: *5* tm.selectAllText
    def selectAllText(self, s: str=None) -> None:
        """TextMixin."""
        self.setSelectionRange(0, self.getLength(s))
    #@+node:ekr.20170511053143.11: *5* tm.setFocus
    def setFocus(self) -> None:
        """TextMixin.setFocus"""
        g.app.gui.set_focus(self)

    #@+node:ekr.20170511053143.23: *5* tm.toPythonIndexRowCol
    def toPythonIndexRowCol(self, index: int) -> Tuple[int, int]:
        """TextMixin"""
        s = self.getAllText()
        row, col = g.convertPythonIndexToRowCol(s, index)
        return row, col
    #@-others
#@+node:ekr.20170504034655.1: *3* class BodyWrapper (leoFrame.StringTextWrapper)
class BodyWrapper(leoFrame.StringTextWrapper):
    """
    A Wrapper class for Leo's body.
    This is c.frame.body.wrapper.
    """

    def __init__(self, c: Cmdr, name: str, w: Wrapper) -> None:
        """Ctor for BodyWrapper class"""
        super().__init__(c, name)
        self.widget: Wrapper = w
        self.injectIvars(c)  # These are used by Leo's core.

    #@+others
    #@+node:ekr.20170504034655.3: *4* bw.injectIvars (cursesGui2)
    def injectIvars(self, c: Cmdr) -> None:
        """Inject standard leo ivars into the QTextEdit or QsciScintilla widget."""
        self.leo_p = c.p.copy() if c.p else None
        self.leo_active = True
        # Inject the scrollbar items into the text widget.
        self.leo_bodyBar = None
        self.leo_bodyXBar = None
        self.leo_chapter = None
        self.leo_frame = None
        self.leo_name = '1'
        self.leo_label = None
    #@+node:ekr.20170504034655.6: *4* bw.onCursorPositionChanged
    def onCursorPositionChanged(self, event: Event=None) -> None:
        if 0:
            g.trace('=====', event)
    #@-others
#@+node:ekr.20170522002403.1: *3* class HeadWrapper (leoFrame.StringTextWrapper)
class HeadWrapper(leoFrame.StringTextWrapper):
    """
    A Wrapper class for headline widgets, returned by c.edit_widget(p)
    """

    def __init__(self, c: Cmdr, name: str, p: Position) -> None:
        """Ctor for HeadWrapper class"""
        super().__init__(c, name)
        self.trace = False  # For tracing in base class.
        self.p = p.copy()
        self.s = p.v._headString

    #@+others
    #@+node:ekr.20170522014009.1: *4* hw.setAllText
    def setAllText(self, s: str) -> None:
        """HeadWrapper.setAllText"""
        # Don't allow newlines.
        self.s = s.replace('\n', '').replace('\r', '')
        i = len(self.s)
        self.ins = i
        self.sel = i, i
        self.p.v._headString = self.s
    #@-others
#@+node:ekr.20170525062512.1: *3* class LogWrapper (leoFrame.StringTextWrapper)
class LogWrapper(leoFrame.StringTextWrapper):
    """A Wrapper class for the log pane."""

    def __init__(self, c: Cmdr, name: str, w: Wrapper) -> None:
        """Ctor for LogWrapper class"""
        super().__init__(c, name)
        self.trace = False  # For tracing in base class.
        self.widget: Wrapper = w

    #@+others
    #@-others
#@+node:ekr.20170525105707.1: *3* class MiniBufferWrapper (leoFrame.StringTextWrapper)
class MiniBufferWrapper(leoFrame.StringTextWrapper):
    """A Wrapper class for the minibuffer."""

    def __init__(self, c: Cmdr, name: str, w: Wrapper) -> None:
        """Ctor for MiniBufferWrapper class"""
        super().__init__(c, name)
        self.trace = False  # For tracing in base class.
        self.box: Wrapper = None  # Injected
        self.widget: Wrapper = w
#@+node:ekr.20171129194610.1: *3* class StatusLineWrapper (leoFrame.StringTextWrapper)
class StatusLineWrapper(leoFrame.StringTextWrapper):
    """A Wrapper class for the status line."""

    def __init__(self, c: Cmdr, name: str, w: Wrapper) -> None:
        """Ctor for StatusLineWrapper class"""
        super().__init__(c, name)
        self.trace = False  # For tracing in base class.
        self.widget: Wrapper = w

    def isEnabled(self) -> bool:
        return True

    #@+others
    #@+node:ekr.20171129204751.1: *4* StatusLineWrapper.do nothings
    def disable(self, *args: Any, **kwargs: Any) -> None:
        pass

    def enable(self, *args: Any, **kwargs: Any) -> None:
        pass

    def setFocus(self) -> None:
        pass
    #@+node:ekr.20171129204736.1: *4* StatusLineWrapper.redirectors
    def clear(self) -> None:
        self.widget.value = ''
        self.widget.display()

    # The signature is different.
    def get(self) -> Any:  # type:ignore
        return self.widget.value

    def put(self, s: str, *args: Any, **kwargs: Any) -> None:
        i = s.find('#')
        if i > -1:
            s = s[i + 1 :]
        self.widget.value = s
        self.widget.display()

    def update(self, *args: Any, **kwargs: Any) -> None:
        self.widget.update()
    #@-others
#@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
