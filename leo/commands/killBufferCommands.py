#@+leo-ver=5-thin
#@+node:ekr.20150514040142.1: * @file ../commands/killBufferCommands.py
"""Leo's kill-buffer commands."""
#@+<< killBufferCommands imports & annotations >>
#@+node:ekr.20150514050411.1: ** << killBufferCommands imports & annotations >>
from __future__ import annotations
from collections.abc import Callable
from typing import Any, Optional, TYPE_CHECKING
from leo.core import leoGlobals as g
from leo.commands.baseCommands import BaseEditCommandsClass

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent
    from leo.core.leoNodes import Position
    from leo.plugins.qt_text import QTextEditWrapper as Wrapper
#@-<< killBufferCommands imports & annotations >>

def cmd(name: str) -> Callable:
    """Command decorator for the KillBufferCommandsClass class."""
    return g.new_cmd_decorator(name, ['c', 'killBufferCommands',])

#@+others
#@+node:ekr.20160514120919.1: ** class KillBufferCommandsClass
class KillBufferCommandsClass(BaseEditCommandsClass):
    """A class to manage the kill buffer."""
    #@+others
    #@+node:ekr.20150514063305.409: *3* kill.ctor & reloadSettings
    def __init__(self, c: Cmdr) -> None:
        """Ctor for KillBufferCommandsClass class."""
        # pylint: disable=super-init-not-called
        self.c = c
        self.kbiterator = self.iterateKillBuffer()  # An instance of KillBufferIterClass.
        # For interacting with system clipboard.
        self.last_clipboard: str = None
        # Position of the last item returned by iterateKillBuffer.
        self.lastYankP: Position = None
        # The index of the next item to be returned in
        # g.app.globalKillBuffer by iterateKillBuffer.
        self.reset: int = None
        self.reloadSettings()

    def reloadSettings(self) -> None:
        """KillBufferCommandsClass.reloadSettings."""
        c = self.c
        self.addWsToKillRing = c.config.getBool('add-ws-to-kill-ring')
    #@+node:ekr.20150514063305.411: *3* addToKillBuffer
    def addToKillBuffer(self, text: Any) -> None:
        """
        Insert the text into the kill buffer if force is True or
        the text contains something other than whitespace.
        """
        if self.addWsToKillRing or text.strip():
            g.app.globalKillBuffer = [z for z in g.app.globalKillBuffer if z != text]
            g.app.globalKillBuffer.insert(0, text)
    #@+node:ekr.20150514063305.412: *3* backwardKillSentence
    @cmd('backward-kill-sentence')
    def backwardKillSentence(self, event: LeoKeyEvent) -> None:
        """Kill the previous sentence."""
        w = self.editWidget(event)
        if not w:
            return
        s = w.getAllText()
        ins = w.getInsertPoint()
        i = s.rfind('.', ins)
        if i == -1:
            return
        undoType = 'backward-kill-sentence'
        self.beginCommand(w, undoType=undoType)
        i2 = s.rfind('.', 0, i) + 1
        self.killHelper(event, i2, i + 1, w, undoType=undoType)
        w.setInsertPoint(i2)
        self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.413: *3* backwardKillWord & killWord
    @cmd('backward-kill-word')
    def backwardKillWord(self, event: LeoKeyEvent) -> None:
        """Kill the previous word."""
        c = self.c
        w = self.editWidget(event)
        if w:
            self.beginCommand(w, undoType='backward-kill-word')
            c.editCommands.backwardWord(event)
            self.killWordHelper(event)

    @cmd('kill-word')
    def killWord(self, event: LeoKeyEvent) -> None:
        """Kill the word containing the cursor."""
        w = self.editWidget(event)
        if w:
            self.beginCommand(w, undoType='kill-word')
            self.killWordHelper(event)

    def killWordHelper(self, event: LeoKeyEvent) -> None:
        c = self.c
        e = c.editCommands
        w = e.editWidget(event)
        if w:
            # self.killWs(event)
            e.extendToWord(event)
            i, j = w.getSelectionRange()
            self.killHelper(event, i, j, w)
            self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.414: *3* clearKillRing
    @cmd('clear-kill-ring')
    def clearKillRing(self, event: LeoKeyEvent = None) -> None:
        """Clear the kill ring."""
        g.app.globalKillbuffer = []
    #@+node:ekr.20150514063305.415: *3* getClipboard
    def getClipboard(self) -> Optional[str]:
        """Return the contents of the clipboard."""
        try:
            ctxt = g.app.gui.getTextFromClipboard()
            if not g.app.globalKillBuffer or ctxt != self.last_clipboard:
                self.last_clipboard = ctxt
                if not g.app.globalKillBuffer or g.app.globalKillBuffer[0] != ctxt:
                    return ctxt
        except Exception:
            g.es_exception()
        return None
    #@+node:ekr.20150514063305.416: *3* class KillBufferIterClass
    class KillBufferIterClass:
        """Returns a list of positions in a subtree, possibly including the root of the subtree."""
        #@+others
        #@+node:ekr.20150514063305.417: *4* __init__ & __iter__ (iterateKillBuffer)
        def __init__(self, c: Cmdr) -> None:
            """Ctor for KillBufferIterClass class."""
            self.c = c
            self.index = 0  # The index of the next item to be returned.

        def __iter__(self) -> Any:
            return self
        #@+node:ekr.20150514063305.418: *4* __next__
        def __next__(self) -> str:
            commands = self.c.killBufferCommands
            aList = g.app.globalKillBuffer  # commands.killBuffer
            if not aList:
                self.index = 0
                return None
            if commands.reset is None:
                i = self.index
            else:
                i = commands.reset
                commands.reset = None
            if i < 0 or i >= len(aList):
                i = 0
            val = aList[i]
            self.index = i + 1
            return val

        #@-others

    def iterateKillBuffer(self) -> KillBufferIterClass:
        return self.KillBufferIterClass(self.c)
    #@+node:ekr.20150514063305.419: *3* ec.killHelper
    def killHelper(self,
        event: LeoKeyEvent, frm: int, to: int, w: Wrapper, undoType: str = None,
    ) -> None:
        """
        A helper method for all kill commands except kill-paragraph commands.
        """
        c = self.c
        w = self.editWidget(event)
        if not w:
            return
        # Extend (frm, to) if it spans a line.
        i, j = w.getSelectionRange()
        s = w.get(i, j)
        if s.find('\n') > -1:
            frm, to = i, j
        s = w.get(frm, to)
        if undoType:
            self.beginCommand(w, undoType=undoType)
        self.addToKillBuffer(s)
        g.app.gui.replaceClipboardWith(s)
        w.delete(frm, to)
        w.setInsertPoint(frm)
        if undoType:
            self.endCommand(changed=True, setLabel=True)
        g.app.gui.set_focus(c, w)  # 2607
    #@+node:ekr.20220121073752.1: *3* ec.killParagraphHelper
    def killParagraphHelper(self,
        event: LeoKeyEvent, frm: Any, to: Any, undoType: str = None,
    ) -> None:
        """A helper method for kill-paragraph commands."""
        w = self.editWidget(event)
        if not w:
            return
        s = w.get(frm, to)
        if undoType:
            self.beginCommand(w, undoType=undoType)
        self.addToKillBuffer(s)
        g.app.gui.replaceClipboardWith(s)
        w.delete(frm, to)
        w.setInsertPoint(frm)
        if undoType:
            self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.420: *3* ec.killToEndOfLine
    @cmd('kill-to-end-of-line')
    def killToEndOfLine(self, event: LeoKeyEvent) -> None:
        """Kill from the cursor to end of the line."""
        w = self.editWidget(event)
        if not w:
            return
        s = w.getAllText()
        ins = w.getInsertPoint()
        i, j = g.getLine(s, ins)
        if ins >= len(s) and g.match(s, j - 1, '\n'):
            # Kill the trailing newline of the body text.
            i = max(0, len(s) - 1)
            j = len(s)
        elif ins + 1 < j and s[ins : j - 1].strip() and g.match(s, j - 1, '\n'):
            # Kill the line, but not the newline.
            i, j = ins, j - 1
        elif g.match(s, j - 1, '\n'):
            i = ins  # Kill the newline in the present line.
        else:
            i = j
        if i < j:
            self.killHelper(event, i, j, w, undoType='kill-to-end-of-line')
    #@+node:ekr.20150514063305.421: *3* ec.killLine
    @cmd('kill-line')
    def killLine(self, event: LeoKeyEvent) -> None:
        """Kill the line containing the cursor."""
        w = self.editWidget(event)
        if not w:
            return
        s = w.getAllText()
        ins = w.getInsertPoint()
        i, j = g.getLine(s, ins)
        if ins >= len(s) and g.match(s, j - 1, '\n'):
            # Kill the trailing newline of the body text.
            i = max(0, len(s) - 1)
            j = len(s)
        elif j > i + 1 and g.match(s, j - 1, '\n'):
            # Kill the line, but not the newline.
            j -= 1
        else:
            pass  # Kill the newline in the present line.
        self.killHelper(event, i, j, w, undoType='kill-line')
    #@+node:ekr.20150514063305.422: *3* killRegion & killRegionSave
    @cmd('kill-region')
    def killRegion(self, event: LeoKeyEvent) -> None:
        """Kill the text selection."""
        w = self.editWidget(event)
        if not w:
            return
        i, j = w.getSelectionRange()
        if i == j:
            return
        s = w.getSelectedText()
        self.beginCommand(w, undoType='kill-region')
        w.delete(i, j)
        self.endCommand(changed=True, setLabel=True)
        self.addToKillBuffer(s)
        g.app.gui.replaceClipboardWith(s)

    @cmd('kill-region-save')
    def killRegionSave(self, event: LeoKeyEvent) -> None:
        """Add the selected text to the kill ring, but do not delete it."""
        w = self.editWidget(event)
        if not w:
            return
        i, j = w.getSelectionRange()
        if i == j:
            return
        s = w.getSelectedText()
        self.addToKillBuffer(s)
        g.app.gui.replaceClipboardWith(s)
    #@+node:ekr.20150514063305.423: *3* ec.killSentence
    @cmd('kill-sentence')
    def killSentence(self, event: LeoKeyEvent) -> None:
        """Kill the sentence containing the cursor."""
        w = self.editWidget(event)
        if not w:
            return
        s = w.getAllText()
        ins = w.getInsertPoint()
        i = s.find('.', ins)
        if i == -1:
            return
        undoType = 'kill-sentence'
        self.beginCommand(w, undoType=undoType)
        i2 = s.rfind('.', 0, ins) + 1
        self.killHelper(event, i2, i + 1, w, undoType=undoType)
        w.setInsertPoint(i2)
        self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.424: *3* killWs
    @cmd('kill-ws')
    def killWs(self, event: LeoKeyEvent, undoType: str = 'kill-ws') -> None:
        """Kill whitespace."""
        ws = ''
        w = self.editWidget(event)
        if not w:
            return
        s = w.getAllText()
        i = j = ins = w.getInsertPoint()
        while i >= 0 and s[i] in (' ', '\t'):
            i -= 1
        if i < ins:
            i += 1
        while j < len(s) and s[j] in (' ', '\t'):
            j += 1
        if j > i:
            ws = s[i:j]
            w.delete(i, j)
            if undoType:
                self.beginCommand(w, undoType=undoType)
            if self.addWsToKillRing:
                self.addToKillBuffer(ws)
            if undoType:
                self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.425: *3* yank & yankPop
    @cmd('yank')
    @cmd('yank')
    def yank(self, event: LeoKeyEvent = None) -> None:
        """Insert the next entry of the kill ring."""
        self.yankHelper(event, pop=False)

    @cmd('yank-pop')
    def yankPop(self, event: LeoKeyEvent = None) -> None:
        """Insert the first entry of the kill ring."""
        self.yankHelper(event, pop=True)

    def yankHelper(self, event: LeoKeyEvent, pop: bool) -> None:
        """
        Helper for yank and yank-pop:
        pop = False: insert the first entry of the kill ring.
        pop = True:  insert the next entry of the kill ring.
        """
        c = self.c
        w = self.editWidget(event)
        if not w:
            return
        current = c.p
        if not current:
            return
        text = w.getAllText()
        i, j = w.getSelectionRange()
        clip_text = self.getClipboard()
        if not g.app.globalKillBuffer and not clip_text:
            return
        undoType = 'yank-pop' if pop else 'yank'
        self.beginCommand(w, undoType=undoType)
        try:
            if not pop or self.lastYankP and self.lastYankP != current:
                self.reset = 0
            s = self.kbiterator.__next__()
            if s is None:
                s = clip_text or ''
            if i != j:
                w.deleteTextSelection()
            if s != s.lstrip():  # s contains leading whitespace.
                i2, j2 = g.getLine(text, i)
                k = g.skip_ws(text, i2)
                if i2 < i <= k:
                    # Replace the line's leading whitespace by s's leading whitespace.
                    w.delete(i2, k)
                    i = i2
            w.insert(i, s)
            # Fix bug 1099035: Leo yank and kill behavior not quite the same as emacs.
            # w.setSelectionRange(i,i+len(s),insert=i+len(s))
            w.setInsertPoint(i + len(s))
            self.lastYankP = current.copy()
        finally:
            self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.427: *3* zapToCharacter
    @cmd('zap-to-character')
    def zapToCharacter(self, event: LeoKeyEvent) -> None:
        """Kill characters from the insertion point to a given character."""
        k = self.c.k
        w = self.editWidget(event)
        if not w:
            return
        state = k.getState('zap-to-char')
        if state == 0:
            k.setLabelBlue('Zap To Character: ')
            k.setState('zap-to-char', 1, handler=self.zapToCharacter)
        else:
            ch = event.char if event else ' '
            k.resetLabel()
            k.clearState()
            s = w.getAllText()
            ins = w.getInsertPoint()
            i = s.find(ch, ins)
            if i == -1:
                return
            self.beginCommand(w, undoType='zap-to-char')
            self.addToKillBuffer(s[ins:i])
            g.app.gui.replaceClipboardWith(s[ins:i])  # Support for proper yank.
            w.setAllText(s[:ins] + s[i:])
            w.setInsertPoint(ins)
            self.endCommand(changed=True, setLabel=True)
    #@-others
#@-others
#@-leo
