# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20150514040142.1: * @file ../commands/killBufferCommands.py
#@@first
"""Leo's kill-buffer commands."""
#@+<< imports >>
#@+node:ekr.20150514050411.1: ** << imports >> (killBufferCommands.py)
from leo.core import leoGlobals as g
from leo.commands.baseCommands import BaseEditCommandsClass
#@-<< imports >>

def cmd(name):
    """Command decorator for the KillBufferCommandsClass class."""
    return g.new_cmd_decorator(name, ['c', 'killBufferCommands',])

#@+others
#@+node:ekr.20160514120919.1: ** class KillBufferCommandsClass
class KillBufferCommandsClass(BaseEditCommandsClass):
    """A class to manage the kill buffer."""
    #@+others
    #@+node:ekr.20150514063305.409: *3* kill.ctor & reloadSettings
    def __init__(self, c):
        """Ctor for KillBufferCommandsClass class."""
        # pylint: disable=super-init-not-called
        self.c = c
        self.kbiterator = self.iterateKillBuffer()
        self.last_clipboard = None
            # For interacting with system clipboard.
        self.lastYankP = None
            # Position of the last item returned by iterateKillBuffer.
        self.reset = None
            # The index of the next item to be returned in
            # g.app.globalKillBuffer by iterateKillBuffer.
        self.reloadSettings()

    def reloadSettings(self):
        """KillBufferCommandsClass.reloadSettings."""
        c = self.c
        self.addWsToKillRing = c.config.getBool('add-ws-to-kill-ring')
    #@+node:ekr.20150514063305.411: *3* addToKillBuffer
    def addToKillBuffer(self, text):
        """
        Insert the text into the kill buffer if force is True or
        the text contains something other than whitespace.
        """
        if self.addWsToKillRing or text.strip():
            g.app.globalKillBuffer = [z for z in g.app.globalKillBuffer if z != text]
            g.app.globalKillBuffer.insert(0, text)
    #@+node:ekr.20150514063305.412: *3* backwardKillSentence
    @cmd('backward-kill-sentence')
    def backwardKillSentence(self, event):
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
        self.kill(event, i2, i + 1, undoType=undoType)
        w.setInsertPoint(i2)
        self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.413: *3* backwardKillWord & killWord
    @cmd('backward-kill-word')
    def backwardKillWord(self, event):
        """Kill the previous word."""
        c = self.c
        w = self.editWidget(event)
        if w:
            self.beginCommand(w, undoType='backward-kill-word')
            c.editCommands.backwardWord(event)
            self.killWordHelper(event)

    @cmd('kill-word')
    def killWord(self, event):
        """Kill the word containing the cursor."""
        w = self.editWidget(event)
        if w:
            self.beginCommand(w, undoType='kill-word')
            self.killWordHelper(event)

    def killWordHelper(self, event):
        c = self.c
        e = c.editCommands
        w = e.editWidget(event)
        if w:
            # self.killWs(event)
            e.extendToWord(event)
            i, j = w.getSelectionRange()
            self.kill(event, i, j, undoType=None)
            self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.414: *3* clearKillRing
    @cmd('clear-kill-ring')
    def clearKillRing(self, event=None):
        """Clear the kill ring."""
        g.app.globalKillbuffer = []
    #@+node:ekr.20150514063305.415: *3* getClipboard
    def getClipboard(self):
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
    #@+node:ekr.20150514063305.416: *3* class iterateKillBuffer
    class KillBufferIterClass:
        """Returns a list of positions in a subtree, possibly including the root of the subtree."""
        #@+others
        #@+node:ekr.20150514063305.417: *4* __init__ & __iter__ (iterateKillBuffer)
        def __init__(self, c):
            """Ctor for KillBufferIterClass class."""
            self.c = c
            self.index = 0  # The index of the next item to be returned.

        def __iter__(self):
            return self
        #@+node:ekr.20150514063305.418: *4* __next__
        def __next__(self):
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
            if i < 0 or i >= len(aList): i = 0
            val = aList[i]
            self.index = i + 1
            return val

        #@-others

    def iterateKillBuffer(self):
        return self.KillBufferIterClass(self.c)
    #@+node:ekr.20150514063305.419: *3* kill (helper)
    def kill(self, event, frm, to, force=False, undoType=None):
        """A helper method for all kill commands."""
        w = self.editWidget(event)
        if not w: return
        # 2016/03/05: all kill commands kill selected text, if it exists.
        if not force:
            # Delete the selection range if it spans a line.
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
    #@+node:ekr.20150514063305.420: *3* killToEndOfLine
    @cmd('kill-to-end-of-line')
    def killToEndOfLine(self, event):
        """Kill from the cursor to end of the line."""
        w = self.editWidget(event)
        if not w: return
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
            self.kill(event, i, j, undoType='kill-line')
    #@+node:ekr.20150514063305.421: *3* KillLine
    @cmd('kill-line')
    def killLine(self, event):
        """Kill the line containing the cursor."""
        w = self.editWidget(event)
        if not w: return
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
        self.kill(event, i, j, undoType='kill-line')
    #@+node:ekr.20150514063305.422: *3* killRegion & killRegionSave & helper
    @cmd('kill-region')
    def killRegion(self, event):
        """Kill the text selection."""
        self.killRegionHelper(event, deleteFlag=True)

    @cmd('kill-region-save')
    def killRegionSave(self, event):
        """Add the selected text to the kill ring, but do not delete it."""
        self.killRegionHelper(event, deleteFlag=False)

    def killRegionHelper(self, event, deleteFlag):
        w = self.editWidget(event)
        if not w: return
        i, j = w.getSelectionRange()
        if i == j: return
        s = w.getSelectedText()
        if deleteFlag:
            self.beginCommand(w, undoType='kill-region')
            w.delete(i, j)
            self.endCommand(changed=True, setLabel=True)
        self.addToKillBuffer(s)
        g.app.gui.replaceClipboardWith(s)
        # self.removeRKeys(w)
    #@+node:ekr.20150514063305.423: *3* killSentence
    @cmd('kill-sentence')
    def killSentence(self, event):
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
        self.kill(event, i2, i + 1, undoType=undoType)
        w.setInsertPoint(i2)
        self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.424: *3* killWs
    @cmd('kill-ws')
    def killWs(self, event, undoType='kill-ws'):
        """Kill whitespace."""
        ws = ''
        w = self.editWidget(event)
        if not w: return
        s = w.getAllText()
        i = j = ins = w.getInsertPoint()
        while i >= 0 and s[i] in (' ', '\t'):
            i -= 1
        if i < ins: i += 1
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
    #@+node:ekr.20150514063305.425: *3* yank
    @cmd('yank')
    def yank(self, event, pop=False):
        """
        yank: insert the first entry of the kill ring.
        yank-pop: insert the next entry of the kill ring.
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
            if s is None: s = clip_text or ''
            if i != j: w.deleteTextSelection()
            if s != s.lstrip():  # s contains leading whitespace.
                i2, j2 = g.getLine(text, i)
                k = g.skip_ws(text, i2)
                if i2 < i <= k:
                    # Replace the line's leading whitespace by s's leading whitespace.
                    w.delete(i2, k)
                    i = i2
            w.insert(i, s)
            # Fix bug 1099035: Leo yank and kill behaviour not quite the same as emacs.
            # w.setSelectionRange(i,i+len(s),insert=i+len(s))
            w.setInsertPoint(i + len(s))
            self.lastYankP = current.copy()
        finally:
            self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.426: *3* yankPop
    @cmd('yank-pop')
    def yankPop(self, event):
        """Insert the next entry of the kill ring."""
        self.yank(event, pop=True)
    #@+node:ekr.20150514063305.427: *3* zapToCharacter
    @cmd('zap-to-character')
    def zapToCharacter(self, event):
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
            if i == -1: return
            self.beginCommand(w, undoType='zap-to-char')
            self.addToKillBuffer(s[ins:i])
            g.app.gui.replaceClipboardWith(s[ins:i])  # Support for proper yank.
            w.setAllText(s[:ins] + s[i:])
            w.setInsertPoint(ins)
            self.endCommand(changed=True, setLabel=True)
    #@-others
#@-others
#@-leo
