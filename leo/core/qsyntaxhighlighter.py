#@+leo-ver=5-thin
#@+node:ekr.20130701072841.12673: * @file qsyntaxhighlighter.py
#@+<< docstring >>
#@+node:ekr.20130701072841.12681: ** << docstring >>
'''

To provide your own syntax highlighting, you must subclass
QSyntaxHighlighter and reimplement highlightBlock().

After this your highlightBlock() function will be called
automatically whenever necessary. Use your highlightBlock()
function to apply formatting (e.g. setting the font and color) to
the text that is passed to it. QSyntaxHighlighter provides the
setFormat() function which applies a given QTextCharFormat on
the current text block.

Some syntaxes can have constructs that span several text
blocks. For example, a C++ syntax highlighter should be able to
cope with \c{/}\c{*...*}\c{/} multiline comments. To deal with
these cases it is necessary to know the end state of the previous
text block (e.g. "in comment").

Inside your highlightBlock() implementation you can query the end
state of the previous text block using the previousBlockState()
function. After parsing the block you can save the last state
using setCurrentBlockState().

The currentBlockState() and previousBlockState() functions return
an int value. If no state is set, the returned value is -1. You
can designate any other value to identify any given state using
the setCurrentBlockState() function. Once the state is set the
QTextBlock keeps that value until it is set set again or until the
corresponding paragraph of text is deleted.
'''
#@-<< docstring >>
#@+<< includes >>
#@+node:ekr.20130701072841.12674: ** << includes >>
import leo.core.leoGlobals as g
from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtCore import Qt as QtConst
import time
#@-<< includes >>

class LeoUserData(QtGui.QTextBlockUserData):
    def __init__(self):
        QtGui.QTextBlockUserData.__init__(self)
        self.gen = None

class LeoSyntaxHighlighter:
    #@+others
    #@+node:ekr.20130701072841.12682: ** ctor
    def __init__(self,c,parent):

        # parent must be a LeoQTextBrowser,a subclass of QTextEdit.
        assert parent
        assert parent.document
        self.parent = parent
        
        # Tunable parameters.
        self.max_lines = c.config.getInt('colorer_max_lines')
        if self.max_lines is None: self.max_lines = 100
            # The max number of lines colored at once.
        self.delay = c.config.getInt('colorer_delay')
        if self.delay is None: self.delay = 200
            # The number of milliseconds to delay queued coloring.
        # g.trace('(LeoSyntaxHighlighter)',self.max_lines,self.delay)
        
        # Was in private class.
        self.c = c
        self.doc = None
        self.formatChanges = [] # was QVector<QTextCharFormat>
        self._currentBlock = None
        self.generation = 0 # New ivar.
        # self.interruptedFlag = False
            # True if incremental highlighting interrupted a full recolor.
        self.inReformatBlocks = False
        self.recolorAll = False # New ivar.
        
        # Delayed coloring.
        self.delayedBlock = None
        self.delayedForceHighlight = False
        self.delayedEndPosition = None
        
        # Debugging.
        self.apply_count = 0
        self.bounded_reformat_count = 0
        
        self.setDocument(parent.document())
    #@+node:ekr.20130701072841.12683: ** setDocument
    # Installs the syntax highlighter on the given QTextDocument doc.
    # This class may only be used with one document at a time.
    def setDocument(self,doc):

        d = self.doc
        if d:
            d.disconnect(d,Qt.SIGNAL('contentsChange(int,int,int)'),
                self._q_reformatBlocks)
            cursor = QtGui.QTextCursor(self.doc)
            cursor.beginEditBlock()
            blk = self.doc.begin()
            while blk.isValid(): 
                blk.layout().clearAdditionalFormats()
                blk = blk.next()
            cursor.endEditBlock()
        self.doc = d = doc
        if d:
            d.connect(d,Qt.SIGNAL('contentsChange(int,int,int)'),
                self._q_reformatBlocks)
    #@+node:ekr.20130701072841.12684: ** document
    def document(self):
        
        ''' Returns the QTextDocument for this syntax highlighter.'''
        
        return self.doc
    #@+node:ekr.20130701072841.12685: ** rehighlight (sets recolorAll)
    def rehighlight(self):
        
        ''' Reapplies the highlighting to the whole document.'''

        if self.doc:
            self.t1 = time.clock()
            self.recolorAll = True
            self.generation += 1
            self._clearDelayedFormat()
            cursor = QtGui.QTextCursor(self.doc)
            self._rehighlightCursor(cursor,QtGui.QTextCursor.End)
            
    # base_rehighlight = rehighlight
    #@+node:ekr.20130701072841.12686: ** rehighlightBlock
    def rehighlightBlock(self,block):
        
        '''Reapplies the highlighting to the given QTextBlock block.'''
        
        if self.doc and block and block.isValid and block.document == self.doc:
            cursor = QtGui.QTextCursor(block)
            self._rehighlightCursor(cursor,QtGui.QTextCursor.EndOfBlock)
    #@+node:ekr.20130701072841.12688: ** setFormat
    #@+at
    # Apply a format to the the syntax highlighter's current text block (i.e. the
    # text that is passed to the highlightBlock() function).
    # 
    # The formatting properties set in format are merged at display time with the
    # formatting information stored directly in the document, for example as
    # previously set with QTextCursor's functions. Note that the document itself
    # remains unmodified by the format set through this function.
    #@@c

    def setFormat(self,start,count,format):
        
        # g.trace(start,count,self.apply_count,format.foreground().color().getRgb())
        n = len(self.formatChanges)
        if 0 <= start < n and count > 0:
            end = min(start+count,n)
            i = start
            while i < end:
                self.formatChanges[i] = format
                i += 1
    #@+node:ekr.20130701072841.12689: ** format
    def format(self,pos):
        
        '''Returns the format at position inside the syntax highlighter's current text block.'''
            
        if 0 <= pos < len(self.formatChanges):
            return self.formatChanges[pos]
        else:
            return QtGui.QTextCharFormat()
    #@+node:ekr.20130701072841.12699: ** getters/setters for blocks
    #@+node:ekr.20130701072841.12695: *3* currentBlock
    def currentBlock(self):

        '''Returns the current block.'''

        cb = self._currentBlock
        return cb if cb and cb.isValid() else None
    #@+node:ekr.20130701072841.12691: *3* currentBlockState
    def currentBlockState(self):

        '''Returns the state of the current text block or -1.'''
        
        cb = self._currentBlock
        return cb.userState() if cb and cb.isValid() else -1
    #@+node:ekr.20130701072841.12694: *3* currentBlockUserData
    def currentBlockUserData(self):
        
        ''' Returns the QTextBlockUserData object previously attached to the current text block.'''
        
        cb = self._currentBlock
        return cb.userData() if cb and cb.isValid() else None
    #@+node:ekr.20130701072841.12690: *3* previousBlockState
    def previousBlockState(self):
        
        '''Returns the end state of the text block previous to the syntax
        highlighter's current block. If no value was previously set,the
        returned value is -1. '''

        cb = self._currentBlock
        if cb and cb.isValid():
            previous = cb.previous()
            return previous.userState() if previous.isValid() else -1
        else:
            return -1
    #@+node:ekr.20130701072841.12692: *3* setCurrentBlockState
    def setCurrentBlockState(self,newState):
        
        '''Sets the state of the current text block to newState.'''
        
        cb = self._currentBlock
        if cb and cb.isValid():
            cb.setUserState(newState)
    #@+node:ekr.20130701072841.12693: *3* setCurrentBlockUserData
    def setCurrentBlockUserData(self,data):
        
        '''Attaches the given data to the current text block.'''
        
        cb = self._currentBlock
        if cb and cb.isValid():
            cb.setUserData(data)
    #@+node:ekr.20130701072841.12675: ** low-level private methods
    # All private methods start with '_'.  They all were in the private class.
    #@+node:ekr.20130701072841.12676: *3* _applyFormatChanges
    def _applyFormatChanges(self):

        formatsChanged = False
        formatChanges = self.formatChanges
        cb = self._currentBlock
        layout = cb.layout()
        ranges = layout.additionalFormats()
        preeditAreaStart = layout.preeditAreaPosition()
        # preeditAreaLength = layout.preeditAreaText().length()
        s = layout.preeditAreaText()
        preeditAreaLength = len(s) if isinstance(s,str) else s.length()
        if preeditAreaLength != 0:
            it = ranges.begin()
            while it != ranges.end():
                if(
                    it.start >= preeditAreaStart and
                    it.start + it.length <= preeditAreaStart + preeditAreaLength
                ):
                    it += 1
                else:
                    it = ranges.erase(it)
                    formatsChanged = True
        elif ranges:
            ranges = []
            formatsChanged = True
        emptyFormat = QtGui.QTextCharFormat()
        FormatRange = QtGui.QTextLayout.FormatRange
        r = FormatRange()
        r.start = -1
        i = 0
        while i < len(formatChanges):
            while i < len(formatChanges) and formatChanges[i] == emptyFormat:
                ++i
            if i >= len(formatChanges):
                break
            r.start = i
            r.format = formatChanges[i].toCharFormat()
            while i < len(formatChanges) and formatChanges[i].toCharFormat() == r.format:
                i += 1
            if i >= len(formatChanges):
                break
            r.length = i - r.start
            if preeditAreaLength != 0:
                if r.start >= preeditAreaStart:
                    r.start += preeditAreaLength
                elif r.start + r.length >= preeditAreaStart:
                    r.length += preeditAreaLength
            ranges.append(r)
            r = FormatRange() # Create a new copy each time through the loop!
            formatsChanged = True
            r.start = -1
        if r.start != -1:
            r.length = len(formatChanges) - r.start
            if preeditAreaLength != 0:
                if r.start >= preeditAreaStart:
                    r.start += preeditAreaLength
                elif r.start + r.length >= preeditAreaStart:
                    r.length += preeditAreaLength
            ranges.append(r)
            formatsChanged = True
        if formatsChanged:
            self.apply_count += 1
            if 0:
                g.trace(self.apply_count,len(ranges))
                for z in ranges:
                    g.trace(z.start,z.length,z.format.foreground().color().getRgb())
            layout.setAdditionalFormats(ranges)
            self.doc.markContentsDirty(cb.position(),cb.length())
    #@+node:ekr.20130701072841.12677: *3* _q_reformatBlocks *
    def _q_reformatBlocks(self,pos1,charsRemoved,charsAdded):
        
        '''The actual contentsChange event handler.'''
        
        # This does incremental changes.
        trace = False and not g.unitTesting
        if self.inReformatBlocks or  self.c.frame.body.colorizer.changingText:
            return
        # Do nothing if we haven't recolored the present block.
        if self.recolorAll:
            block = self.doc.findBlock(pos1)
            if block and block.isValid():
                data = block.userData()
                if not (data and data.gen == self.generation):
                    if trace: g.trace('ignoring interruption',data and data.gen)
                    return
        # g.trace(pos1,charsRemoved,charsAdded,g.callers())
        # if self.recolorAll and self.delayedBlock:
            # if trace: g.trace('ignoring interruption 2')
            # self.interruptedFlag = True
            # return
        self._reformatBlocks(pos1,charsRemoved,charsAdded)
    #@+node:ekr.20130701072841.12678: *3* _reformatBlocks & helpers
    def _reformatBlocks(self,pos1,charsRemoved,charsAdded):
        
        '''The helper for the contentsChange event handler.'''
        
        # if g.unitTesting: return # Adds almost 20% to unit tests.
        trace = False and not g.unitTesting
        if trace: g.trace(self.c.p.h)
        doc = self.doc
        self._clearDelayedFormat() # Essential.
        block = doc.findBlock(pos1)
        if block and block.isValid():
            lastBlock = doc.findBlock(pos1 + charsAdded + (1 if charsRemoved > 0 else 0))
            if lastBlock and lastBlock.isValid():
                endPosition = lastBlock.position() + lastBlock.length()
            else:
                endPosition = doc.characterCount() # was doc.docHandle().length()
            self._boundedReformatBlocks(block,endPosition,forceHighlightOfNextBlock=False)
    #@+node:ekr.20130702174205.12637: *4* _boundedReformatBlocks
    def _boundedReformatBlocks(self,block,endPosition,forceHighlightOfNextBlock):
        
        '''Reformat at most self.n_max_lines blocks.
        Queue _idleReformatBlocks if more blocks remain.'''

        trace = False and not g.unitTesting
        trace_block = False ; trace_delay = True ; trace_end = True
        count = 0
        generation = self.generation
        while True:
            if (block and block.isValid() and (
                    block.position() < endPosition or
                    forceHighlightOfNextBlock or
                    self.recolorAll)
            ):
                self.bounded_reformat_count += 1
                if trace and trace_block: g.trace('%4s block: %s' % (
                    self.bounded_reformat_count,id(block)))
                stateBeforeHighlight = block.userState()
                self._reformatBlock(block)
                forceHighlightOfNextBlock = block.userState() != stateBeforeHighlight
                block = block.next()
                count += 1
                if count > self.max_lines:
                    # g.app.gui.qtApp.processEvents();
                    # if self.generation != generation:
                        # if trace: g.trace('interrupt')
                        # return
                    if block and block.isValid():
                        if trace and trace_delay: g.trace('delay %4s %s' % (
                            self.bounded_reformat_count,g.timeSince(self.t1)))
                        self.delayedBlock = block
                        self.delayedForceHighlight = forceHighlightOfNextBlock
                        self.delayedEndPosition = endPosition
                        Qt.QTimer.singleShot(self.delay,self._idleReformatBlocks)
                    break
            else:
                self.recolorAll = False
                if trace and trace_end: g.trace('*done %4s %s' % (
                    self.bounded_reformat_count,g.timeSince(self.t1)))
                # if self.interruptedFlag:
                    # self.interruptedFlag = False
                    # if trace and trace_end: g.trace('redoing all highlighting')
                    # Qt.QTimer.singleShot(1000,self.base_rehighlight)
                break
        self.formatChanges = []
    #@+node:ekr.20130702174205.12636: *4* _clearDelayedFormat
    def _clearDelayedFormat(self):
        
        '''Disable any delayed redraw.'''
        
        self.delayedBlock = None
        self.delayedForceHighlight = False
        self.delayedEndPosition = None
        
        # Clearing this would defeat its purpose.
        # self.recolorAll = False
    #@+node:ekr.20130702174205.12635: *4* _idleReformatBlocks
    def _idleReformatBlocks(self):
            
        # Get the saved data.
        block = self.delayedBlock
        forceHighlightOfNextBlock = self.delayedForceHighlight
        endPosition = self.delayedEndPosition
        
        # Clear the saved data.
        self._clearDelayedFormat()
        
        # Continue coloring if possible.
        if block and block.isValid():
            self._boundedReformatBlocks(block,endPosition,forceHighlightOfNextBlock)
    #@+node:ekr.20130701072841.12679: *4* _reformatBlock *
    def _reformatBlock(self,block):

        if self._currentBlock and self._currentBlock.isValid():
            g.trace('can not happen: recursive call to _reformatBlock')
        else:
            self._currentBlock = block
            self.formatChanges = [QtGui.QTextFormat()] * (block.length())
            self.highlightBlock(block.text())
                # Calls the Leo-specifc coloring code, which calls setFormat.
            if block and block.isValid():
                data = block.userData() or LeoUserData()
                data.generation = self.generation
            block.setUserData(data)
            self._applyFormatChanges()
            self._currentBlock = QtGui.QTextBlock()
    #@+node:ekr.20130701072841.12697: *4* _rehighlightCursor
    # This was the rehighlight method of the private class.

    def _rehighlightCursor(self,cursor,operation):
        
        '''Low-level rehighlight.'''
        
        self.inReformatBlocks = True
        try:
            cursor.beginEditBlock()
            pos1 = cursor.position()
            cursor.movePosition(operation)
            self._reformatBlocks(pos1,0,cursor.position()-pos1)
            cursor.endEditBlock()
        finally:
            self.inReformatBlocks = False
    #@-others
    
#@@language python
#@@tabwidth -4
#@-leo
