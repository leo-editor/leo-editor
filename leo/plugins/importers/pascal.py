#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18147: * @file importers/pascal.py
'''The @auto importer for Pascal.'''
import leo.core.leoGlobals as g
import leo.plugins.importers.basescanner as basescanner
#@+others
#@+node:ekr.20140723122936.18076: ** class PascalScanner
class PascalScanner (basescanner.BaseScanner):

    #@+others
    #@+node:ekr.20140723122936.18077: *3* skipArgs
    def skipArgs (self,s,i,kind):

        '''Skip the argument or class list.  Return i, ok

        kind is in ('class','function')'''

        # Pascal interfaces have no argument list.
        if kind == 'class':
            return i, True

        start = i
        i = g.skip_ws_and_nl(s,i)
        if not g.match(s,i,'('):
            return start,kind == 'class'

        i = self.skipParens(s,i)
        # skipParens skips the ')'
        if i >= len(s):
            return start,False
        else:
            return i,True 
    #@+node:ekr.20140723122936.18078: *3* ctor (PascalScanner)
    def __init__ (self,importCommands,atAuto):

        # Init the base class.
        basescanner.BaseScanner.__init__(self,importCommands,atAuto=atAuto,language='pascal')

        # Set the parser overrides.
        self.anonymousClasses = ['interface']
        self.blockCommentDelim1 = '(*'
        self.blockCommentDelim1_2 = '{'
        self.blockCommentDelim2 = '*)'
        self.blockCommentDelim2_2 = '}'
        self.blockDelim1 = 'begin'
        self.blockDelim2 = 'end'
        self.blockDelim2Cruft = [';','.'] # For Delphi.
        self.classTags = ['interface']
        self.functionTags = ['function','procedure','constructor','destructor',]
        self.hasClasses = True
        self.lineCommentDelim = '//'
        self.strict = False
    #@+node:ekr.20140723122936.18079: *3* skipCodeBlock
    def skipCodeBlock (self,s,i,kind):

        '''Skip the code block in a function or class definition.'''

        trace = False
        start = i

        if kind == 'class':
            i = self.skipInterface(s,i)
        else:
            i = self.skipBlock(s,i,delim1=None,delim2=None)

            if self.sigFailTokens:
                i = g.skip_ws(s,i)
                for z in self.sigFailTokens:
                    if g.match(s,i,z):
                        if trace: g.trace('failtoken',z)
                        return start,False

        if i > start:
            i = self.skipNewline(s,i,kind)

        if trace:
            g.trace(g.callers())
            g.trace('returns...\n',g.listToString(g.splitLines(s[start:i])))

        return i,True
    #@+node:ekr.20140723122936.18080: *3* skipInterface
    def skipInterface(self,s,i):

        '''Skip from the opening delim to *past* the matching closing delim.

        If no matching is found i is set to len(s)'''

        trace = False
        start = i
        delim2 = 'end.'
        level = 0 ; start = i
        startIndent = self.startSigIndent
        if trace: g.trace('***','startIndent',startIndent,g.callers())
        while i < len(s):
            progress = i
            if g.is_nl(s,i):
                backslashNewline = i > 0 and g.match(s,i-1,'\\\n')
                i = g.skip_nl(s,i)
                if not backslashNewline and not g.is_nl(s,i):
                    j, indent = g.skip_leading_ws_with_indent(s,i,self.tab_width)
                    line = g.get_line(s,j)
                    if trace: g.trace('indent',indent,line)
                    if indent < startIndent and line.strip():
                        # An non-empty underindented line.
                        # Issue an error unless it contains just the closing bracket.
                        if level == 1 and g.match(s,j,delim2):
                            pass
                        else:
                            if j not in self.errorLines: # No error yet given.
                                self.errorLines.append(j)
                                self.underindentedLine(line)
            elif s[i] in (' ','\t',):
                i += 1 # speed up the scan.
            elif self.startsComment(s,i):
                i = self.skipComment(s,i)
            elif self.startsString(s,i):
                i = self.skipString(s,i)
            elif g.match(s,i,delim2):
                i += len(delim2)
                if trace: g.trace('returns\n',repr(s[start:i]))
                return i

            else: i += 1
            assert progress < i

        self.error('no interface')
        if 1:
            g.pr('** no interface **')
            i,j = g.getLine(s,start)
            g.trace(i,s[i:j])
        else:
            if trace: g.trace('** no interface')
        return start
    #@+node:ekr.20140723122936.18081: *3* skipSigTail
    def skipSigTail(self,s,i,kind):

        '''Skip from the end of the arg list to the start of the block.'''

        trace = False and self.trace

        # Pascal interface has no tail.
        if kind == 'class':
            return i,True

        start = i
        i = g.skip_ws(s,i)
        for z in self.sigFailTokens:
            if g.match(s,i,z):
                if trace: g.trace('failToken',z,'line',g.skip_line(s,i))
                return i,False
        while i < len(s):
            if self.startsComment(s,i):
                i = self.skipComment(s,i)
            elif g.match(s,i,self.blockDelim1):
                if trace: g.trace(repr(s[start:i]))
                return i,True
            else:
                i += 1
        if trace: g.trace('no block delim')
        return i,False
    #@+node:ekr.20140723122936.18082: *3* putClass & helpers
    def putClass (self,s,i,sigEnd,codeEnd,start,parent):

        '''Create a node containing the entire interface.'''

        # Enter a new class 1: save the old class info.
        oldMethodName = self.methodName
        oldStartSigIndent = self.startSigIndent

        # Enter a new class 2: init the new class info.
        self.indentRefFlag = None

        class_kind = self.classId
        class_name = self.sigId
        headline = '%s %s' % (class_kind,class_name)
        headline = headline.strip()
        self.methodName = headline

        # Compute the starting lines of the class.
        # prefix = self.createClassNodePrefix()

        # Create the class node.
        class_node = self.createHeadline(parent,'',headline)

        # Put the entire interface in the body.
        result = s[start:codeEnd]
        self.appendTextToClassNode(class_node,result)

        # Exit the new class: restore the previous class info.
        self.methodName = oldMethodName
        self.startSigIndent = oldStartSigIndent
    #@-others
#@-others
importer_dict = {
    'class': PascalScanner,
    'extensions': ['.pas',],
}
#@-leo
