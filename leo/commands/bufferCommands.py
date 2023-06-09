#@+leo-ver=5-thin
#@+node:ekr.20150514035559.1: * @file ../commands/bufferCommands.py
"""Leo's buffer commands."""
#@+<< bufferCommands imports & annotations >>
#@+node:ekr.20150514045750.1: ** << bufferCommands imports & annotations >>
from __future__ import annotations
from collections.abc import Callable
from typing import Any, Optional, TYPE_CHECKING
from leo.core import leoGlobals as g
from leo.commands.baseCommands import BaseEditCommandsClass

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent as Event
    from leo.core.leoNodes import Position, VNode
#@-<< bufferCommands imports & annotations >>

def cmd(name: str) -> Callable:
    """Command decorator for the BufferCommands class."""
    return g.new_cmd_decorator(name, ['c', 'bufferCommands',])

#@+others
#@+node:ekr.20160514095727.1: ** class BufferCommandsClass
class BufferCommandsClass(BaseEditCommandsClass):
    """
    An Emacs instance does not have knowledge of what is considered a
    buffer in the environment.

    """
    #@+others
    #@+node:ekr.20150514045829.3: *3* buffer.ctor
    def __init__(self, c: Cmdr) -> None:
        """Ctor for the BufferCommandsClass class."""
        # pylint: disable=super-init-not-called
        self.c = c
        self.fromName = ''  # Saved name from getBufferName.
        self.nameList: list[str] = []  # [n: <headline>]
        self.names: dict[str, list[str]] = {}
        self.vnodes: dict[str, VNode] = {}  # Keys are n: <headline>, values are vnodes.
    #@+node:ekr.20150514045829.5: *3* buffer.Entry points
    #@+node:ekr.20150514045829.6: *4* appendToBuffer
    @cmd('buffer-append-to')
    def appendToBuffer(self, event: Event) -> None:
        """Add the selected body text to the end of the body text of a named buffer (node)."""
        self.w = self.editWidget(event)
        if self.w:
            self.c.k.setLabelBlue('Append to buffer: ')
            self.getBufferName(event, self.appendToBuffer1)

    def appendToBuffer1(self, name: str) -> None:
        c, w = self.c, self.w
        s = w.getSelectedText()
        p = self.findBuffer(name)
        if s and p:
            w = self.w
            c.selectPosition(p)
            self.beginCommand(w, f"append-to-buffer: {p.h}")
            end = w.getLastIndex()
            w.insert(end, s)
            w.setInsertPoint(end + len(s))
            w.seeInsertPoint()
            self.endCommand()
            c.recolor()
    #@+node:ekr.20150514045829.7: *4* copyToBuffer
    @cmd('buffer-copy')
    def copyToBuffer(self, event: Event) -> None:
        """Add the selected body text to the end of the body text of a named buffer (node)."""
        self.w = self.editWidget(event)
        if self.w:
            self.c.k.setLabelBlue('Copy to buffer: ')
            self.getBufferName(event, self.copyToBuffer1)

    def copyToBuffer1(self, name: str) -> None:
        c, w = self.c, self.w
        s = w.getSelectedText()
        p = self.findBuffer(name)
        if s and p:
            c.selectPosition(p)
            self.beginCommand(w, f"copy-to-buffer: {p.h}")
            w.insert(w.getLastIndex(), s)
            w.setInsertPoint(w.getLastIndex())
            self.endCommand()
            c.recolor()
    #@+node:ekr.20150514045829.8: *4* insertToBuffer
    @cmd('buffer-insert')
    def insertToBuffer(self, event: Event) -> None:
        """Add the selected body text at the insert point of the body text of a named buffer (node)."""
        self.w = self.editWidget(event)
        if self.w:
            self.c.k.setLabelBlue('Insert to buffer: ')
            self.getBufferName(event, self.insertToBuffer1)

    def insertToBuffer1(self, name: str) -> None:
        c, w = self.c, self.w
        s = w.getSelectedText()
        p = self.findBuffer(name)
        if s and p:
            c.selectPosition(p)
            self.beginCommand(w, undoType=f"insert-to-buffer: {p.h}")
            i = w.getInsertPoint()
            w.insert(i, s)
            w.seeInsertPoint()
            self.endCommand()
    #@+node:ekr.20150514045829.9: *4* killBuffer
    @cmd('buffer-kill')
    def killBuffer(self, event: Event) -> None:
        """Delete a buffer (node) and all its descendants."""
        self.w = self.editWidget(event)
        if self.w:
            self.c.k.setLabelBlue('Kill buffer: ')
            self.getBufferName(event, self.killBuffer1)

    def killBuffer1(self, name: str) -> None:
        c = self.c
        p = self.findBuffer(name)
        if p:
            h = p.h
            current = c.p
            c.selectPosition(p)
            c.deleteOutline(op_name=f"kill-buffer: {h}")
            c.selectPosition(current)
            self.c.k.setLabelBlue(f"Killed buffer: {h}")
            c.redraw(current)
    #@+node:ekr.20150514045829.10: *4* listBuffers & listBuffersAlphabetically
    @cmd('buffers-list')
    def listBuffers(self, event: Event) -> None:
        """
        List all buffers (node headlines), in outline order. Nodes with the
        same headline are disambiguated by giving their parent or child index.
        """
        self.computeData()
        g.es('buffers...')
        for name in self.nameList:
            g.es('', name)

    @cmd('buffers-list-alphabetically')
    def listBuffersAlphabetically(self, event: Event) -> None:
        """
        List all buffers (node headlines), in alphabetical order. Nodes with
        the same headline are disambiguated by giving their parent or child
        index.
        """
        self.computeData()
        names = sorted(self.nameList)
        g.es('buffers...')
        for name in names:
            g.es('', name)
    #@+node:ekr.20150514045829.11: *4* prependToBuffer
    @cmd('buffer-prepend-to')
    def prependToBuffer(self, event: Event) -> None:
        """Add the selected body text to the start of the body text of a named buffer (node)."""
        self.w = self.editWidget(event)
        if self.w:
            self.c.k.setLabelBlue('Prepend to buffer: ')
            self.getBufferName(event, self.prependToBuffer1)

    def prependToBuffer1(self, name: str) -> None:
        c, w = self.c, self.w
        s = w.getSelectedText()
        p = self.findBuffer(name)
        if s and p:
            c.selectPosition(p)
            self.beginCommand(w, f"prepend-to-buffer: {p.h}")
            w.insert(0, s)
            w.setInsertPoint(0)
            w.seeInsertPoint()
            self.endCommand()
            c.recolor()
    #@+node:ekr.20150514045829.12: *4* renameBuffer (not ready)
    def renameBuffer(self, event: Event) -> None:
        """Rename a buffer, i.e., change a node's headline."""
        g.es('rename-buffer not ready yet')
        if 0:
            self.c.k.setLabelBlue('Rename buffer from: ')
            self.getBufferName(event, self.renameBufferFinisher1)

    def renameBufferFinisher1(self, name: str) -> None:
        self.fromName = name
        self.c.k.setLabelBlue(f"Rename buffer from: {name} to: ")
        event = None
        self.getBufferName(event, self.renameBufferFinisher2)

    def renameBufferFinisher2(self, name: str) -> None:
        c = self.c
        p = self.findBuffer(self.fromName)
        if p:
            c.endEditing()
            p.h = name
            c.redraw(p)
    #@+node:ekr.20150514045829.13: *4* switchToBuffer
    @cmd('buffer-switch-to')
    def switchToBuffer(self, event: Event) -> None:
        """Select a buffer (node) by its name (headline)."""
        self.c.k.setLabelBlue('Switch to buffer: ')
        self.getBufferName(event, self.switchToBuffer1)

    def switchToBuffer1(self, name: str) -> None:
        c = self.c
        p = self.findBuffer(name)
        if p:
            c.selectPosition(p)
            c.redraw_after_select(p)
    #@+node:ekr.20150514045829.14: *3* buffer.Utils
    #@+node:ekr.20150514045829.15: *4* computeData
    def computeData(self) -> None:
        self.nameList = []
        self.names = {}
        self.vnodes = {}
        for p in self.c.all_unique_positions():
            h = p.h.strip()
            v = p.v
            nameList = self.names.get(h, [])
            if nameList:
                if p.parent():
                    key = f"{h}, parent: {p.parent().h}"
                else:
                    key = f"{h}, child index: {p.childIndex()}"
            else:
                key = h
            self.nameList.append(key)
            self.vnodes[key] = v
            nameList.append(key)
            self.names[h] = nameList
    #@+node:ekr.20150514045829.16: *4* findBuffer
    def findBuffer(self, name: str) -> Optional[Position]:
        v = self.vnodes.get(name)
        for p in self.c.all_unique_positions():
            if p.v == v:
                return p
        g.es_print("no node named", name, color='orange')
        return None
    #@+node:ekr.20150514045829.17: *4* getBufferName
    def getBufferName(self, event: Event, finisher: Any) -> None:
        """Get a buffer name into k.arg and call k.setState(kind,n,handler)."""
        k = self.c.k
        self.computeData()
        self.getBufferNameFinisher = finisher
        prefix = k.getLabel()
        k.get1Arg(event, handler=self.getBufferName1, prefix=prefix, tabList=self.nameList)

    def getBufferName1(self, event: Event) -> None:
        k = self.c.k
        k.resetLabel()
        k.clearState()
        finisher = self.getBufferNameFinisher
        self.getBufferNameFinisher = None
        finisher(k.arg)
    #@-others
#@-others
#@-leo
