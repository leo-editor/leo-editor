#@+leo-ver=5-thin
#@+node:ekr.20041021120118: * @file pretty_print.py
#@+<< docstring >>
#@+node:ekr.20050912180735: ** << docstring >>
'''Customizes pretty printing.

The plugin creates a do-nothing subclass of the default pretty printer. To
customize, simply override in this file the methods of the base prettyPrinter
class in leoCommands.py. You would typically want to override putNormalToken or
its allies. Templates for these methods have been provided. You may, however,
override any methods you like. You could even define your own class entirely,
provided you implement the prettyPrintNode method.

'''
#@-<< docstring >>

#@@language python
#@@tabwidth -4

#@+<< imports >>
#@+node:ekr.20041021120859: ** << imports >>
import leo.core.leoGlobals as g
import leo.core.leoCommands as leoCommands
#@-<< imports >>

__version__ = "1.1" # 8/1/05: updated example code to match latest code in leoCommands.py.

oldPrettyPrinter = leoCommands.Commands.prettyPrinter

#@+others
#@+node:ekr.20100128073941.5378: ** init
def init():

    ok = not g.app.unitTesting # Not for unit testing:  modifies core.

    if ok:
        leoCommands.Commands.prettyPrinter = myPrettyPrinter
        g.plugin_signon(__name__)

    return ok
#@+node:ekr.20041021120454: ** class myPrettyPrinter
class myPrettyPrinter(leoCommands.Commands.prettyPrinter):

    '''An example subclass of Leo's prettyPrinter class.

    Not all the base class methods are shown here:
    just the ones you are likely to want to override.'''

    #@+others
    #@+node:ekr.20041021123018: *3* myPrettyPrinter.__init__
    def __init__ (self,c):

        # Init the base class.
        oldPrettyPrinter.__init__(self,c)
        self.tracing = False

        # g.pr("Overriding class leoCommands.prettyPrinter")
    #@+node:ekr.20041021123018.1: *3* putNormalToken & allies
    if 0: # The orignal code...

        def putNormalToken (self,token5tuple):

            t1,t2,t3,t4,t5 = token5tuple
            self.name = token.tok_name[t1].lower() # The token type
            self.val = t2  # the token string
            self.srow,self.scol = t3 # row & col where the token begins in the source.
            self.erow,self.ecol = t4 # row & col where the token ends in the source.
            self.s = t5 # The line containing the token.
            self.startLine = self.line != self.srow
            self.line = self.srow

            if self.startLine:
                self.doStartLine()

            # Dispatch a helper function.
            f = self.dispatchDict.get(self.name,self.oops)
            self.trace()
            f()
    #@+node:ekr.20041021123018.2: *3* doEndMarker
    if 0: # The orignal code...

        def doEndMarker (self):

            self.putArray()
    #@+node:ekr.20041021123018.3: *3* doErrorToken
    if 0: # The orignal code...

        def doErrorToken (self):

            self.array.append(self.val)

            if self.val == '@':
                # Preserve whitespace after @.
                i = g.skip_ws(self.s,self.scol+1)
                ws = self.s[self.scol+1:i]
                if ws:
                    self.array.append(ws)
    #@+node:ekr.20041021123018.4: *3* doIndent & doDedent
    if 0: # The orignal code...

        def doDedent (self):

            pass

        def doIndent (self):

            self.array.append(self.val)
    #@+node:ekr.20041021123018.5: *3* doMultiLine
    if 0: # The orignal code...

        def doMultiLine (self):

            # Ensure a blank before comments not preceded entirely by whitespace.

            if self.val.startswith('#') and self.array:
                prev = self.array[-1]
                if prev and prev[-1] != ' ':
                    self.put(' ') 

            # These may span lines, so duplicate the end-of-line logic.
            lines = g.splitLines(self.val)
            for line in lines:
                self.array.append(line)
                if line and line[-1] == '\n':
                    self.putArray()

            # Add a blank after the string if there is something in the last line.
            if self.array:
                line = self.array[-1]
                if line.strip():
                    self.put(' ')

            # Suppress start-of-line logic.
            self.line = self.erow
    #@+node:ekr.20041021123018.6: *3* doName
    if 0: # The orignal code...

        def doName(self):

            # Ensure whitespace or start-of-line precedes the name.
            if self.array:
                last = self.array[-1]
                ch = last[-1]
                outer = self.parenLevel == 0 and self.squareBracketLevel == 0
                chars = '@ \t{([.'
                if not outer: chars += ',=<>*-+&|/'
                if ch not in chars:
                    self.array.append(' ')

            self.array.append("%s " % self.val)

            if self.prevName == "def": # A personal idiosyncracy.
                self.array.append(' ') # Retain the blank before '('.

            self.prevName = self.val
    #@+node:ekr.20041021123018.7: *3* doNewline
    if 0: # The orignal code...

        def doNewline (self):

            # Remove trailing whitespace.
            # This never removes trailing whitespace from multi-line tokens.
            if self.array:
                self.array[-1] = self.array[-1].rstrip()

            self.array.append('\n')
            self.putArray()
    #@+node:ekr.20041021123018.8: *3* doNumber
    if 0: # The orignal code...

        def doNumber (self):

            self.array.append(self.val)
    #@+node:ekr.20041021123018.9: *3* doOp
    if 0: # The orignal code...

        def doOp (self):

            val = self.val
            outer = self.lineParenLevel <= 0 or (self.parenLevel == 0 and self.squareBracketLevel == 0)
            # New in Python 2.4: '@' is an operator, not an error token.
            if self.val == '@':
                self.array.append(self.val)
                # Preserve whitespace after @.
                i = g.skip_ws(self.s,self.scol+1)
                ws = self.s[self.scol+1:i]
                if ws: self.array.append(ws)
            elif val == '(':
                # Nothing added; strip leading blank before function calls but not before Python keywords.
                strip = self.lastName=='name' and not keyword.iskeyword(self.prevName)
                self.put('(',strip=strip)
                self.parenLevel += 1 ; self.lineParenLevel += 1
            elif val in ('=','==','+=','-=','!=','<=','>=','<','>','<>','*','**','+','&','|','/','//'):
                # Add leading and trailing blank in outer mode.
                s = g.choose(outer,' %s ','%s')
                self.put(s % val)
            elif val in ('^','~','{','['):
                # Add leading blank in outer mode.
                s = g.choose(outer,' %s','%s')
                self.put(s % val)
                if val == '[': self.squareBracketLevel += 1
            elif val in (',',':','}',']',')'):
                # Add trailing blank in outer mode.
                s = g.choose(outer,'%s ','%s')
                self.put(s % val)
                if val == ']': self.squareBracketLevel -= 1
                if val == ')':
                    self.parenLevel -= 1 ; self.lineParenLevel -= 1
            # no difference between outer and inner modes
            elif val in (';','%'):
                # Add leading and trailing blank.
                self.put(' %s ' % val)
            elif val == '>>':
                # Add leading blank.
                self.put(' %s' % val)
            elif val == '<<':
                # Add trailing blank.
                self.put('%s ' % val)
            elif val in ('-'):
                # Could be binary or unary.  Or could be a hyphen in a section name.
                # Add preceding blank only for non-id's.
                if outer:
                    if self.array:
                        prev = self.array[-1].rstrip()
                        if prev and prev[-1] not in string.digits + string.letters:
                            self.put(' %s' % val)
                        else: self.put(val)
                    else: self.put(val) # Try to leave whitespace unchanged.
                else:
                    self.put(val)
            else:
                self.put(val)
    #@+node:ekr.20041021123018.10: *3* doStartLine
    if 0: # The orignal code...

        def doStartLine (self):

            before = self.s[0:self.scol]
            i = g.skip_ws(before,0)
            self.ws = self.s[0:i]

            if self.ws:
                self.array.append(self.ws)
    #@+node:ekr.20041021123018.11: *3* oops
    if 0: # The orignal code...

        def oops(self):

            g.pr("unknown PrettyPrinting code: %s" % (self.name))
    #@+node:ekr.20041021123018.12: *3* trace
    if 0: # The orignal code...

        def trace(self):

            if self.tracing:

                g.trace("%10s: %s" % (
                    self.name,
                    repr(g.toEncodedString(self.val))
                ))
    #@-others
#@-others
#@-leo
