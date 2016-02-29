#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18144: * @file importers/javascript.py
'''The @auto importer for JavaScript.'''
import leo.core.leoGlobals as g
import leo.plugins.importers.basescanner as basescanner
#@+others
#@+node:ekr.20140723122936.18049: ** class JavaScriptScanner
# The syntax for patterns causes all kinds of problems...

class JavaScriptScanner(basescanner.BaseScanner):
    #@+others
    #@+node:ekr.20140723122936.18050: *3* jss.__init__
    def __init__(self, importCommands, atAuto, language='javascript', alternate_language=None):
        '''The ctor for the JavaScriptScanner class.'''
        # Init the base class.
        basescanner.BaseScanner.__init__(self, importCommands,
            atAuto=atAuto,
            language=language,
                # The language is used to set comment delims.
            alternate_language=alternate_language)
                # The language used in the @language directive.
        # Set the parser vars.
        self.atAutoWarnsAboutLeadingWhitespace = False
        self.blockCommentDelim1 = '/*'
        self.blockCommentDelim2 = '*/'
        self.blockDelim1 = '{'
        self.blockDelim2 = '}'
        self.hasClasses = True ### 2016/01/22
        self.hasDecls = False ### 2016/01/22
        self.hasFunctions = True
        self.hasRegex = True
        # self.ignoreBlankLines = True
        self.lineCommentDelim = '//'
        self.lineCommentDelim2 = None
        self.outerBlockDelim1 = None # For now, ignore outer blocks.
        self.outerBlockDelim2 = None
        self.classTags = []
        self.functionTags = ['function',]
        self.sigFailTokens = [';',]
        self.strict = False
        # Extra semantic data...
        self.classNames = []
        self.functionNames = []
    #@+node:ekr.20140723122936.18051: *3* jss.filterTokens
    def filterTokens(self, tokens):
        '''Filter tokens as needed for correct comparisons.

        For JavaScript this means ignoring newlines.
        '''
        if 1: # Permissive: ignore added newlines.
            return [(kind, val, line_number) for(kind, val, line_number) in tokens
                    if kind not in ('nl',)] # 'ws',
        else:
            return tokens
    #@+node:ekr.20160122170805.1: *3* jss.show
    def show(self, s):
        '''Attempt to show s with proper indentation.'''
        print(s)
        # lines = g.splitLines(s)
        # if len(lines) < 2:
            # print(s)
        # else:
            # s1 = lines[1]
            # i, lws = 0, []
            # while i < len(s1) and s1[i] in ' \t':
                # lws.append(s1[i])
                # i += 1
            # lws = ''.join(lws)
            # g.trace('lws:',repr(lws))
            # print(lines[0])
            # for s in lines[1:-1]:
                # if lws and s.startswith(lws):
                    # print(repr(s[len(lws):]))
                # else:
                    # print(repr(s))
            # print(lines[-1].strip())
    #@+node:ekr.20160122103056.1: *3* jss.skipBlock
    def skipBlock(self, s, i, delim1, delim2):
        '''Skip from the opening delim to *past* the matching closing delim.

        If no matching is found i is set to len(s)'''
        trace = False and not g.unitTesting
        # k1, k2 = g.getLine(s,i)
        # g.trace(s[i:])
        i1, level = i, 0
        assert s[i] == delim1, (s[i], delim1, g.callers())
        while i < len(s):
            progress = i
            ch = s[i]
            if g.is_nl(s, i):
                i = g.skip_nl(s, i)
            elif self.startsComment(s, i):
                i = self.skipComment(s, i)
            elif ch in '"\'':
                i = self.skipString(s, i)
            elif ch == '/':
                i = self.skipRegex(s, i)
            elif ch == delim1:
                level += 1
                i += 1
            elif ch == delim2:
                level -= 1
                i += 1
                if level <= 0:
                    # g.trace('returns:\n\n%s\n\n' % s[i1: i])
                    return i
            else:
                i += 1
            assert progress < i
        self.error('no block: %s' % i)
        if trace:
            i2, j2 = g.getLine(s, i1)
            g.trace(i, level, s[i2:j2+1])
        return i
    #@+node:ekr.20160122071725.1: *3* jss.scan & scanHelper
    def scan(self, s, parent, parse_body=False):
        '''A javascript scanner.

        Create a child of self.root containing section references for
        top-level functions and objects containing functions.

        Rescan all functions for innner functions.
        '''
        i = self.scanHelper(parent, s)
        ### Finish adding to the parent's body text.
        ### self.addRef(parent)
        if i < len(s) and s[i:].strip():
            self.appendStringToBody(parent, s[i:])
        ### Do any language-specific post-processing.
        ### self.endGen(s)
    #@+node:ekr.20160122071725.2: *4* jss.scanHelper
    def scanHelper(self, parent, s):
        '''Common scanning code used by both scan and putClassHelper.'''
        i = 0
        while i < len(s):
            progress = i
            ch = s[i]
            if self.startsComment(s, i):
                i = self.skipComment(s, i)
            elif ch in '"\'':
                i = self.skipString(s, i)
            elif ch == '/':
                i = self.skipRegex(s, i)
            # elif ch == '{':
                # i = self.scanObject(parent, s, i)
            elif g.match_word(s, i, 'function'):
                i = self.scanFunction(parent, s, i)
            else:
                i += 1
            assert progress < i, 'i: %d, ch: %s' % (i, repr(s[i]))
        return i
    #@+node:ekr.20160122073855.1: *3* jss.scanFunction (new) & helpers
    def scanFunction(self, parent, s, i):
        '''scan function(args) { body } and then rescan body.'''
        trace = True and not g.unitTesting
        # k1, k2 = g.getLine(s,i)
        # g.trace(s[k1:k2])
        i1 = i
        # Scan backward for '('
        i2 = i-1
        while 0 <= i2 and s[i2].isspace():
            i2 -= 1
        in_expr = s[i2] == '('
        assert g.match(s, i, 'function')
        i += len('function')
        i = g.skip_ws_and_nl(s, i)
        i = self.skipId(s, i)
        i = g.skip_ws_and_nl(s, i)
        # Skip the argument list.
        if not g.match(s, i, '('):
            if trace: g.trace('syntax error: no argument list',i)
            return i
        i = self.skipBlock(s, i,'(', ')')
            # skipBlock skips the ')'
        if i == len(s):
            g.trace('no args', g.get_line(s, i))
            return i
        # Skip the body.
        i = g.skip_ws_and_nl(s, i)
        if not g.match(s, i, '{'):
            if trace: g.trace('no function body', i)
            return i
        block_i1 = i
        block_i2 = i = self.skipBlock(s, i, '{', '}')
        j = g.skip_ws_and_nl(s,i)
        if g.match(s, j, '('):
            i = g.skip_parens(s, i)
        if in_expr:
            j = g.skip_ws_and_nl(s,i)
            if g.match(s, j, ')'):
                i = j + 1
        assert i > i1
        block_s = s[block_i1+1:block_i2-1].strip()
        if trace: g.trace('*** rescanning ***\n\n%s\n\n' % block_s)
        self.scanHelper(parent, block_s)
        return i
    #@+node:ekr.20160122110449.1: *4* jss.skipArgs
    def skipArgs(self, s, i, kind):
        '''Skip the argument or class list.  Return i, ok

        kind is in ('class','function')'''
        start = i
        i = g.skip_ws_and_nl(s, i)
        if not g.match(s, i, '('):
            return start, kind == 'class'
        i = self.skipParens(s, i)
        # skipParens skips the ')'
        if i >= len(s):
            return start, False
        else:
            return i, True
    #@+node:ekr.20160122110306.4: *4* jss.skipSigTail
    def skipSigTail(self, s, i, kind=None):
        '''Skip from the end of the arg list to the start of the block.'''
        trace = False and self.trace
        i1 = i
        i = self.skipWs(s, i)
        for z in self.sigFailTokens:
            if g.match(s, i, z):
                if trace: g.trace('failToken', z, 'line', g.skip_line(s, i))
                return i, False
        while i < len(s):
            progress = i
            if self.startsComment(s, i):
                i = self.skipComment(s, i)
            elif g.match(s, i, self.blockDelim1):
                if trace: g.trace(repr(s[start: i]))
                return i, True
            else:
                i += 1
            assert progress < i
        if trace: g.trace('no block delim')
        return i, False
    #@+node:ekr.20160122102535.1: *3* jss.scanObject (new, not used)
    def scanObject(self, parent, s, i):
        '''
        Scan an object, creating child nodes of prarent for objects that have
        inner functions.
        '''
        assert s[i] == '{'
        g.trace(s[i:])
        i1 = i
        i = self.skipBlock(s, i, '{', '}')
        if g.match(s, i-1, '}'):
            g.trace('returns:\n\n%s\n\n' % s[i1: i+1])
            object_s = s[i1+1:i-1].strip()
            junk_i = self.scanHelper(parent, object_s)
        else:
            g.trace('==== no object')
        return i
    #@+node:ekr.20160122072018.1: *3* jss.putFunction
    def putFunction(self, s, sigStart, codeEnd, start, parent):
        '''Create a node of parent for a function defintion.'''
        trace = False and not g.unitTesting
        verbose = True
        # Enter a new function: save the old function info.
        oldStartSigIndent = self.startSigIndent
        if self.sigId:
            headline = self.sigId
        else:
            ### g.trace('Can not happen: no sigId')
            ### headline = 'unknown function'
            headline = s[sigStart: start]
        body1, body2 = self.computeBody(s, start, sigStart, codeEnd)
        body = body1 + body2
        parent = self.adjustParent(parent, headline)
        if trace:
            # pylint: disable=maybe-no-member
            g.trace('parent', parent and parent.h)
            if verbose:
                # g.trace('**body1...\n',body1)
                g.trace(self.atAutoSeparateNonDefNodes)
                g.trace('**body...\n%s' % body)
        # 2010/11/04: Fix wishlist bug 670744.
        if self.atAutoSeparateNonDefNodes:
            if body1.strip():
                if trace: g.trace('head', body1)
                line1 = g.splitLines(body1.lstrip())[0]
                line1 = line1.strip() or 'non-def code'
                self.createFunctionNode(line1, body1, parent)
                body = body2
        self.lastParent = self.createFunctionNode(headline, body, parent)
        # Exit the function: restore the function info.
        self.startSigIndent = oldStartSigIndent
    #@+node:ekr.20160122074204.1: *3* jss.endGen
    def endGen(self, s):

        g.trace(len(s))
    #@+node:ekr.20140723122936.18054: *3* jss.skipNewline
    def skipNewline(self, s, i, kind):
        '''
        Skip whitespace and comments up to a newline, then skip the newline.
        Unlike the base class:
        - we always skip to a newline, if any.
        - we do *not* issue an error if no newline is found.
        '''
        while i < len(s):
            progress = i
            i = self.skipWs(s, i)
            if self.startsComment(s, i):
                i = self.skipComment(s, i)
            else: break
            assert i > progress
        if i >= len(s):
            return len(s)
        elif g.match(s, i, '\n'):
            return i + 1
        else:
            # A hack, but probably good enough in most cases.
            while i < len(s) and s[i] in ' \t()};':
                i += 1
            if g.match(s, i, '\n'):
                i += 1
            return i
    #@-others
#@-others
importer_dict = {
    'class': JavaScriptScanner,
    'extensions': ['.js',],
}
#@-leo
