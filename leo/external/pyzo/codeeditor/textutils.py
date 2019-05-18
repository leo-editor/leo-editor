# -*- coding: utf-8 -*-
# Copyright (C) 2016, the Pyzo development team
#
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.


class TextReshaper:
    """ Object to reshape a piece of text, taking indentation, paragraphs,
    comments and bulletpoints into account.
    """
    
    def __init__(self, lw, margin=3):
        self.lw = lw
        self.margin = margin
        
        self._lines1 = []
        self._lines2 = []
        
        self._wordBuffer = []
        self._charsInBuffer = -1 # First word ads one extra
        
        self._pendingPrefix = None # A one-shot prefix
        self._currentPrefix = None # The prefix used until a new prefix is set
    
    @classmethod
    def reshapeText(cls, text, lw):
        tr = cls(lw)
        tr.pushText(text)
        return tr.popText()
    
    def pushLine(self, line):
        """ Push a single line to the input.
        """
        self._lines1.append(line.rstrip())
    
    def pushText(self, text):
        """ Push a (multiline) text to the input.
        """
        for line in text.splitlines():
            self.pushLine(line)
    
    def popLines(self):
        """ Get all available lines from the output.
        """
        try:
            while True:
                self._popLine()
        except StopIteration:
            self._flush()
        
        return [line for line in self._lines2]
    
    def popText(self):
        """ Get all text from the output (i.e. lines joined with newline).
        """
        return '\n'.join(self.popLines())
    
    
    def _prefixString(self):
        if self._pendingPrefix is not None:
            prefix = self._pendingPrefix
            self._pendingPrefix = None
            return prefix
        else:
            return self._currentPrefix or ''
    
    def _addWordToBuffer(self, word):
        self._wordBuffer.append(word)
        self._charsInBuffer += len(word) + 1 # add one for space
    
    def _flush(self):
        if self._wordBuffer:
            self._lines2.append(self._prefixString() + ' '.join(self._wordBuffer))
        self._wordBuffer, self._charsInBuffer = [], -1
    
    def _addNewParagraph(self):
        # Flush remaining words
        self._flush()
        # Create empty line
        prefix = self._currentPrefix or ''
        prefix = ' ' * len(prefix)
        self._lines2.append(prefix)
        # Allow new prefix
        self._currentPrefix = None
    
    def _popLine(self):
        """ Pop a line from the input. Examine how it starts and convert it
        to words.
        """
        
        # Pop line
        try:
            line = self._lines1.pop(0)
        except IndexError:
            raise StopIteration()
        
        # Strip the line
        strippedline1 = line.lstrip()
        strippedline2 = line.lstrip(' \t#*')
        
        # Analyze this line (how does it start?)
        if not strippedline1:
            self._addNewParagraph()
            return
        elif strippedline1.startswith('* '):
            self._flush()
            indent = len(line) - len(strippedline1)
            linePrefix = line[:indent]
            self._pendingPrefix = linePrefix + '* '
            self._currentPrefix = linePrefix + '  '
        else:
            # Hey, an actual line! Determine prefix
            indent = len(line) - len(strippedline1)
            linePrefix = line[:indent]
            # Check comments
            if strippedline1.startswith('#'):
                linePrefix += '# '
            # What to do now?
            if linePrefix != self._currentPrefix:
                self._flush()
                self._currentPrefix = linePrefix
        
        
        # Process words one by one...
        for word in strippedline2.split(' '):
            self._addWordToBuffer(word)
            currentLineWidth = self._charsInBuffer + len(self._currentPrefix)
            
            if currentLineWidth < self.lw:
                # Not enough words in buffer yet
                pass
            elif len(self._wordBuffer) > 1:
                # Enough words to compose a line
                marginWith = currentLineWidth - self.lw
                marginWithout = self.lw - (currentLineWidth - len(word))
                if marginWith < marginWithout and marginWith < self.margin:
                    # add all buffered words
                    self._flush()
                else:
                    # add all buffered words (except last)
                    self._wordBuffer.pop(-1)
                    self._flush()
                    self._addWordToBuffer(word)
            else:
                # This single word covers more than one line
                self._flush()
    


testText = """

# This is a piece
# of comment
Lorem ipsum dolor sit amet, consectetur
adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi
ut aliquip ex ea
commodo consequat. Duis aute irure dolor
in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat
non proident, sunt in culpa qui officia deserunt mollit anim
id est laborum.

        # Indented comments
        # should work
        # as well
    
skdb-a-very-long-word-ksdbfksasdvbassdfhjsdfbjdfbvhjdbvhjbdfhjvbdfjbvjdfbvjdfbvjdbfvj

   A change in indentation makes it a separate line
sdckj bsdkjcb sdc
sdckj  foo bar
aap noot mies

  * Bullet points are preserved
  * Even if they are very long the should be preserved. I know that brevity is a great virtue but you know,
    sometimes you just need those
    extra words to make a point.

"""

if __name__ == '__main__':
    print(TextReshaper.reshapeText(testText, 70))
    
    
