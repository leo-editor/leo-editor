#@+leo-ver=5-thin
#@+node:ekr.20140727075002.18109: * @file importers/basescanner.py
'''The BaseScanner class used by all importers in leo.plugins.importers.'''
import leo.core.leoGlobals as g
# import leo.core.leoImport as leoImport
if g.isPython3:
    import io
    StringIO = io.StringIO
else:
    import StringIO
    StringIO = StringIO.StringIO
import time

class BaseScanner:
    '''The base class for all import scanner classes.'''
    #@+others
    #@+node:ekr.20140727075002.18188: ** BaseScanner.ctor
    def __init__ (self,importCommands,atAuto,language='unnamed',alternate_language=None):
        '''ctor for BaseScanner.'''
        ic = importCommands
        self.atAuto = atAuto
        self.c = c = ic.c
        self.atAutoWarnsAboutLeadingWhitespace = c.config.getBool(
            'at_auto_warns_about_leading_whitespace')
        self.atAutoSeparateNonDefNodes = c.config.getBool(
            'at_auto_separate_non_DefNodes',default=False)
        self.classId = None
            # The identifier containing the class tag:
            # 'class', 'interface', 'namespace', etc.
        self.codeEnd = None
            # The character after the last character of the class, method or function.
            # An error will be given if this is not a newline.
        self.compare_tokens = True
        self.encoding = ic.encoding
        self.errors = 0
        ic.errors = 0
        self.errorLines = []
        self.escapeSectionRefs = True
        self.extraIdChars = ''
        self.fileName = ic.fileName
            # The original filename.
        self.fileType = ic.fileType
            # The extension,  '.py', '.c', etc.
        self.file_s = ''
            # The complete text to be parsed.
        self.fullChecks = c.config.getBool('full_import_checks')
        self.functionSpelling = 'function'
            # for error message.
        self.importCommands = ic
        self.indentRefFlag = None
            # None, True or False.
        self.isPrepass = False
            # True if we are running at-file-to-at-auto prepass.
        self.isRst = False
        self.language = language
            # The language used to set comment delims.
        self.lastParent = None
            # The last generated parent node (used only by RstScanner).
        self.methodName = ic.methodName
            # x, as in < < x methods > > =
        self.methodsSeen = False
        self.mismatchWarningGiven = False
        self.n_decls = 0
            # For headLineForNode only. The number of decls seen.
        self.output_newline = ic.output_newline
            # = c.config.getBool('output_newline')
        self.output_indent = 0
            # The minimum indentation presently in effect.
        self.root = None
            # The top-level node of the generated tree.
        self.rootLine = ic.rootLine
            # '' or @root + self.fileName
        self.sigEnd = None
            # The index of the end of the signature.
        self.sigId = None
            # The identifier contained in the signature,
            # that is, the function or method name.
        self.sigStart = None
            # The start of the line containing the signature.
            # An error will be given if something other
            # than whitespace precedes the signature.
        self.startSigIndent = None
        self.tab_width = None
            # Set in run: the tab width in effect in the c.currentPosition.
        self.tab_ws = ''
            # Set in run: the whitespace equivalent to one tab.
        self.trace = False or ic.trace
            # ic.trace is c.config.getBool('trace_import')
        self.treeType = ic.treeType
            # '@root' or '@file'
        self.webType = ic.webType
            # 'cweb' or 'noweb'
        # Compute language ivars.
        delim1,junk,junk = g.set_delims_from_language(language)
        self.comment_delim = delim1
        # May be overridden in subclasses...
        self.alternate_language = alternate_language
            # Optional: for @language.
        self.anonymousClasses = []
            # For Delphi Pascal interfaces.
        self.blockCommentDelim1 = None
        self.blockCommentDelim2 = None
        self.blockCommentDelim1_2 = None
        self.blockCommentDelim2_2 = None
        self.blockDelim1 = '{'
        self.blockDelim2 = '}'
        self.blockDelim2Cruft = []
            # Stuff that can follow .blockDelim2.
        self.caseInsensitive = False
        self.classTags = ['class',]
            # tags that start a tag.
        self.functionTags = []
        self.hasClasses = True
        self.hasDecls = True
        self.hasFunctions = True
        self.hasNestedClasses = False
        self.ignoreBlankLines = False
        self.ignoreLeadingWs = False
        self.lineCommentDelim = None
        self.lineCommentDelim2 = None
        self.outerBlockDelim1 = None
        self.outerBlockDelim2 = None
        self.outerBlockEndsDecls = True
        self.sigHeadExtraTokens = []
            # Extra tokens valid in head of signature.
        self.sigFailTokens = []
            # A list of strings that abort a signature when seen in a tail.
            # For example, ';' and '=' in C.
        self.strict = False # True if leading whitespace is very significant.
        self.warnAboutUnderindentedLines = True
    #@+node:ekr.20140727075002.18189: ** BaseScanner.Checking
    #@+node:ekr.20140727075002.18190: *3* BaseScanner.check
    def check (self,unused_s,unused_parent):

        '''Make sure the generated nodes are equivalent to the original file.

        1. Regularize and check leading whitespace.
        2. Check that a trial write produces the original file.

        Return True if the nodes are equivalent to the original file.
        '''
        # Note: running full checks on all unit tests is slow.
        if g.app.suppressImportChecks:
            return True
        if (g.unitTesting or self.fullChecks) and self.treeType in (None,'@file'):
            return self.checkTrialWrite()
        else:
            return True
    #@+node:ekr.20140727075002.18191: *3* BaseScanner.checkLeadingWhitespace
    def checkLeadingWhitespace (self,line):

        tab_width = self.tab_width
        lws = line[0:g.skip_ws(line,0)]
        w = g.computeWidth(lws,tab_width)
        ok = (w % abs(tab_width)) == 0

        if not ok:
            self.report('leading whitespace not consistent with @tabwidth %d' % tab_width)
            g.error('line:',repr(line))

        return ok
    #@+node:ekr.20140727075002.18192: *3* BaseScanner.checkTrialWrite
    def checkTrialWrite (self,s1=None,s2=None):
        '''Return True if a trial write produces the original file.'''
        # s1 and s2 are for unit testing.
        trace = False and not g.unitTesting
        trace_code = True
        trace_time = False and not g.unitTesting
        if trace_time:
            t1 = time.clock()
        c,at=self.c,self.c.atFileCommands
        if trace: g.trace(s1 and len(s1),s2 and len(s2))
        if s1 is None and s2 is None:
            if self.isRst:
                outputFile = StringIO()
                c.rstCommands.writeAtAutoFile(self.root,self.fileName,outputFile,trialWrite=True)
                s1,s2 = self.file_s,outputFile.getvalue()
                s1,s2 = self.stripRstLines(s1),self.stripRstLines(s2)
                # if g.unitTesting: g.pdb()
            elif self.atAuto:
                # Special case for @auto.
                at.writeOneAtAutoNode(self.root,toString=True,force=True,trialWrite=True)
                s1,s2 = self.file_s,at.stringOutput
            else:
                # *Do* write sentinels in s2 to handle @others correctly.
                # But we should not handle section references.
                at.write(self.root,
                    nosentinels=False,
                    perfectImportFlag=True,
                    scriptWrite=False,
                    thinFile=True,
                    toString=True,
                )
                s1,s2 = self.file_s, at.stringOutput
                # Now remove sentinels from s2.
                line_delim = self.lineCommentDelim or self.lineCommentDelim2 or ''
                start_delim = self.blockCommentDelim1 or self.blockCommentDelim2 or ''
                # g.trace(self.language,line_delim,start_delim)
                assert line_delim or start_delim
                s2 = self.importCommands.removeSentinelLines(s2,
                    line_delim,start_delim,unused_end_delim=None)
        s1 = g.toUnicode(s1,self.encoding)
        s2 = g.toUnicode(s2,self.encoding)
        # Make sure we have a trailing newline in both strings.
        s1 = s1.replace('\r','')
        s2 = s2.replace('\r','')
        if not s1.endswith('\n'): s1 = s1 + '\n'
        if not s2.endswith('\n'): s2 = s2 + '\n'
        if s1 == s2:
            if trace_time: g.trace(g.timeSince(t1))
            return True
        if self.ignoreBlankLines or self.ignoreLeadingWs or not self.compare_tokens:
            lines1 = g.splitLines(s1)
            lines2 = g.splitLines(s2)
            lines1 = self.adjustTestLines(lines1)
            lines2 = self.adjustTestLines(lines2)
            s1 = ''.join(lines1)
            s2 = ''.join(lines2)
        if trace and trace_code:
            g.trace('s1...\n%s' % s1)
            g.trace('s2...\n%s' % s2)
        # if g.unitTesting: g.pdb()
        if self.compare_tokens: # Token-based comparison.
            bad_i1,bad_i2,ok = self.scanAndCompare(s1,s2)
            if ok:
                if trace_time: g.trace(g.timeSince(t1))
                return ok
        else: # Line-based comparison: can not possibly work for html.
            n1,n2 = len(lines1), len(lines2)
            ok = True ; bad_i1,bad_i2 = 0,0
            for i in range(max(n1,n2)):
                ok = self.compareHelper(lines1,lines2,i,self.strict)
                if not ok:
                    bad_1i,bad_i2 = i,i
                    break
        # Unit tests do not generate errors unless the mismatch line does not match.
        if g.app.unitTesting:
            d = g.app.unitTestDict
            ok = d.get('expectedMismatchLine') == bad_i1
            if not ok: d['fail'] = g.callers()
        if trace or not ok:
            lines1 = g.splitLines(s1)
            lines2 = g.splitLines(s2)
            self.reportMismatch(lines1,lines2,bad_i1,bad_i2)
        if trace_time: g.trace(g.timeSince(t1))
        return ok
    #@+node:ekr.20140727075002.18193: *3* BaseScanner.compareHelper & helpers
    def compareHelper (self,lines1,lines2,i,strict):
        '''
        Compare lines1[i] and lines2[i] on a line-by-line basis.
        strict is True if leading whitespace is very significant.
        '''
        def pr(*args,**keys): #compareHelper
            g.blue(*args,**keys)
        def pr_mismatch(i,line1,line2):
            g.es_print('first mismatched line at line',str(i+1))
            g.es_print('original line: ',line1)
            g.es_print('generated line:',line2)
        d = g.app.unitTestDict
        expectedMismatch = g.app.unitTesting and d.get('expectedMismatchLine')
        enableWarning = not self.mismatchWarningGiven and self.atAutoWarnsAboutLeadingWhitespace
        messageKind = None
        if i >= len(lines1):
            if i != expectedMismatch or not g.unitTesting:
                pr('extra lines')
                for line in lines2[i:]:
                    pr(repr(line))
            d ['actualMismatchLine'] = i
            return False
        if i >= len(lines2):
            if i != expectedMismatch or not g.unitTesting:
                g.es_print('missing lines')
                for line in lines2[i:]:
                    g.es_print('',repr(line))
            d ['actualMismatchLine'] = i
            return False
        line1,line2 = lines1[i],lines2[i]
        if line1 == line2:
            return True # An exact match.
        elif not line1.strip() and not line2.strip():
            return True # Blank lines compare equal.
        elif self.isRst and self.compareRstUnderlines(line1,line2):
            return True
        elif strict:
            s1,s2 = line1.lstrip(),line2.lstrip()
            messageKind = 'comment' if s1 == s2 and self.startsComment(s1,0) and self.startsComment(s2,0) else 'error'
        else:
            s1,s2 = line1.lstrip(),line2.lstrip()
            messageKind = 'warning' if s1==s2 else 'error'
        if g.unitTesting:
            d ['actualMismatchLine'] = i+1
            ok = i+1 == expectedMismatch
            if not ok:  pr_mismatch(i,line1,line2)
            return ok
        elif strict:
            if enableWarning:
                self.mismatchWarningGiven = True
                if messageKind == 'comment':
                    self.warning('mismatch in leading whitespace before comment')
                else:
                    self.error('mismatch in leading whitespace')
                pr_mismatch(i,line1,line2)
            return messageKind == 'comment' # Only mismatched comment lines are valid.
        else:
            if enableWarning:
                self.mismatchWarningGiven = True
                self.checkLeadingWhitespace(line1)
                self.warning('mismatch in leading whitespace')
                pr_mismatch(i,line1,line2)
            return messageKind in ('comment','warning') # Only errors are invalid.
    #@+node:ekr.20140727075002.18194: *4* BaseScanner.adjustTestLines
    def adjustTestLines(self,lines):
        '''
        Ignore blank lines and trailing whitespace.

        This fudge allows the rst code generators to insert needed newlines freely.
        '''
        if self.ignoreBlankLines:
            lines = [z for z in lines if z.strip()]
        if self.ignoreLeadingWs:
            lines = [z.lstrip() for z in lines]
        # New in Leo 5.0.
        lines = [z.rstrip()+'\n' if z.endswith('\n') else z.rstrip() for z in lines]
        return lines
    #@+node:ekr.20140727075002.18195: *4* BaseScanner.compareRstUnderlines
    def compareRstUnderlines(self,s1,s2):

        s1,s2 = s1.rstrip(),s2.rstrip()
        if s1 == s2:
            return True # Don't worry about trailing whitespace.

        n1, n2 = len(s1),len(s2)
        ch1 = n1 and s1[0] or ''
        ch2 = n2 and s2[0] or ''

        val = (
            n1 >= 2 and n2 >= 2 and # Underlinings must be at least 2 long.
            ch1 == ch2 and # The underlining characters must match.
            s1 == ch1 * n1 and # The line must consist only of underlining characters.
            s2 == ch2 * n2)

        return val
    #@+node:ekr.20140727075002.18196: *3* BaseScanner.formatTokens
    def formatTokens(self,tokens):

        '''Format tokens for printing or dumping.'''

        i,result = 0,[]
        for kind,val,line_number in tokens:
            s = '%3s %3s %6s %s' % (i,line_number,kind,repr(val))
            result.append(s)
            i += 1

        return '\n'.join(result)
    #@+node:ekr.20140727075002.18197: *3* BaseScanner.reportMismatch
    def reportMismatch (self,lines1,lines2,bad_i1,bad_i2):

        # g.trace('**',bad_i1,bad_i2,g.callers())
        trace = False # This causes traces for *non-failing* unit tests.
        if trace and False and len(lines1) < 100:
            g.trace('lines1...\n',''.join(lines1),'\n')
            g.trace('lines2...\n',''.join(lines2),'\n')
            return
        kind = '@auto' if self.atAuto else 'import command'
        n1,n2 = len(lines1),len(lines2)
        s1 = '%s did not import %s perfectly\n' % (
            kind,self.root.h)
        s2 = 'The clean-all-lines command may help fix whitespace problems\n'
        s3 = 'first mismatched line: %s (original) = %s (imported)' % (
            bad_i1,bad_i2)
        s = s1 + s2 + s3
        if trace: g.trace(s)
        else:     self.error(s)
        aList = []
        aList.append('Original file...\n')
        for i in range(max(0,bad_i1-2),min(bad_i1+3,n1)):
            line = repr(lines1[i])
            aList.append('%4d %s' % (i,line))
        aList.append('\nImported file...\n')
        for i in range(max(0,bad_i2-2),min(bad_i2+3,n2)):
            line = repr(lines2[i])
            aList.append('%4d %s' % (i,line))
        if trace or not g.unitTesting:
            g.blue('\n'.join(aList))
        return False
    #@+node:ekr.20140727075002.18198: *3* BaseScanner.scanAndCompare & helpers
    def scanAndCompare (self,s1,s2):

        '''Tokenize both s1 and s2, then perform a token-based comparison.

        Blank lines and leading whitespace has already been stripped
        according to the ignoreBlankLines and ignoreLeadingWs ivars.

        Return (n,ok), where n is the first mismatched line in s1.
        '''

        tokens1 = self.tokenize(s1)
        tokens2 = self.tokenize(s2)
        tokens1 = self.filterTokens(tokens1)
        tokens2 = self.filterTokens(tokens2)
        if self.stripTokens(tokens1) == self.stripTokens(tokens2):
            # g.trace('stripped tokens are equal')
            return -1,-1,True
        else:
            n1,n2 = self.compareTokens(tokens1,tokens2)
            return n1,n2,False
    #@+node:ekr.20140727075002.18199: *4* BaseScanner.compareTokens
    def compareTokens(self,tokens1,tokens2):

        trace = False and not g.unitTesting
        verbose = True
        i,n1,n2 = 0,len(tokens1),len(tokens2)
        fail_n1,fail_n2 = -1,-1
        while i < max(n1,n2):
            if trace and verbose:
                for n,tokens in ((n1,tokens1),(n2,tokens2),):
                    if i < n: kind,val,line_number = tokens[i]
                    else:     kind,val,line_number = 'eof','',''
                    try:
                        print('%3s %3s %7s' % (i,line_number,kind),repr(val)[:40])
                    except UnicodeEncodeError:
                        print('%3s %3s %7s' % (i,line_number,kind),'unicode error!')
                        # print(val)
            if i < n1: kind1,val1,tok_n1 = tokens1[i]
            else:      kind1,val1,tok_n1 = 'eof','',n1
            if i < n2: kind2,val2,tok_n2 = tokens2[i]
            else:      kind2,val2,tok_n2 = 'eof','',n2
            if fail_n1 == -1 and fail_n2 == -1 and (kind1 != kind2 or val1 != val2):
                if trace: g.trace('fail at lines: %s,%s' % (tok_n1,tok_n2))
                fail_n1,fail_n2 = tok_n1,tok_n2 # Bug fix: 2013/09/08.
                if trace:
                    print('------ Failure ----- i: %s n1: %s n2: %s' % (i,n1,n2))
                    print('tok_n1: %s tok_n2: %s' % (tok_n1,tok_n2))
                    print('kind1: %s kind2: %s\nval1: %s\nval2: %s' % (
                        kind1,kind2,repr(val1),repr(val2)))
                if trace and verbose:
                    n3 = 0
                    i += 1
                    while n3 < 10 and i < max(n1,n2):
                        for n,tokens in ((n1,tokens1),(n2,tokens2),):
                            if i < n: kind,val,junk_n = tokens[i]
                            else:     kind,val = 'eof',''
                            print('%3s %7s %s' % (i,kind,repr(val)))
                        n3 += 1
                        i += 1
                break
            i += 1
        if fail_n1 > -1 or fail_n2 > -1:
            if trace: g.trace('fail',fail_n1,fail_n2)
            return fail_n1,fail_n2
        elif n1 == n2:
            if trace: g.trace('equal')
            return -1,-1
        else:
            n = min(len(tokens1),len(tokens2))
            if trace: g.trace('fail 2 at line: %s' % (n))
            return n,n
    #@+node:ekr.20140727075002.18200: *4* BaseScanner.filterTokens & helpers
    def filterTokens (self,tokens):

        '''Filter tokens as needed for correct comparisons.

        May be overridden in subclasses.'''

        return tokens
    #@+node:ekr.20140727075002.18201: *5* BaseScanner.removeLeadingWsTokens
    def removeLeadingWsTokens (self,tokens):

        '''Remove tokens representing leading whitespace.'''

        i,last,result = 0,'nl',[]
        while i < len(tokens):
            progress = i
            kind,val,n = tok = tokens[i]
            if kind == 'ws' and last == 'nl':
                pass
            else:
                result.append(tok)
            i += 1
            last = kind
            assert progress + 1 == i

        return result
    #@+node:ekr.20140727075002.18202: *5* BaseScanner.removeBlankLinesTokens
    def removeBlankLinesTokens(self,tokens):

        '''Remove all tokens representing blank lines.'''

        trace = False
        if trace: g.trace('\nbefore:',tokens)

        i,last,lws,result = 0,'nl',[],[]
        while i < len(tokens):
            progress = i
            kind,val,n = tok = tokens[i]
            if kind == 'ws':
                if last in ('nl','ws'):
                    # Continue to append leading whitespace.
                    # Wrong, if ws tok ends in newline.
                    lws.append(tok)
                else:
                    # Not leading whitespace: add it.
                    if lws: result.extend(lws)
                    lws = []
                    result.append(tok)
            elif kind == 'nl':
                # Ignore any previous blank line and remember *this* newline.
                lws = [tok]
            else:
                # A non-blank line: append the leading whitespace.
                if lws: result.extend(lws)
                lws = []
                result.append(tok)
            last = kind
            i += 1
            assert i == progress+1
        # Add any remaining ws.
        if lws: result.extend(lws)

        if trace: g.trace('\nafter: ',result)
        return result
    #@+node:ekr.20140727075002.18203: *3* BaseScanner.stripTokens
    def stripTokens(self,tokens):

        '''Remove the line_number from all tokens.'''

        return [(kind,val) for (kind,val,line_number) in tokens]
    #@+node:ekr.20140727075002.18204: *3* BaseScanner.stripRstLines
    def stripRstLines(self,s):
        '''Replace rst under/overlines with a dummy line for comparison.'''
        
        def mungeRstLine(s):
            '''Return a dummy under/over line for rst under/overlines.'''
            if len(s) < 4: return s
            nl = '\n' if s[-1] == '\n' else ''
            ch1 = s[0]
            dummy_line = (ch1*10) + nl
            s = s.rstrip() + nl
            if ch1.isalnum(): return s
            for ch in s.rstrip():
                if ch == '\n': return dummy_line
                if ch != ch1: return s
            return dummy_line

        return ''.join([mungeRstLine(z) for z in g.splitLines(s)])
    #@+node:ekr.20140727075002.18205: ** BaseScanner.Code generation
    #@+node:ekr.20140727075002.18206: *3* BaseScanner.adjustParent
    def adjustParent (self,parent,headline):

        '''Return the effective parent.

        This is overridden by the RstScanner class.'''

        return parent
    #@+node:ekr.20140727075002.18207: *3* BaseScanner.addRef
    def addRef (self,parent):

        '''Create an unindented @others or section reference in the parent node.'''

        if self.isRst and not self.atAuto:
            return

        if self.treeType in ('@file',None):
            self.appendStringToBody(parent,'@others\n')

        if self.treeType == '@root' and self.methodsSeen:
            self.appendStringToBody(parent,
                g.angleBrackets(' ' + self.methodName + ' methods ') + '\n\n')
    #@+node:ekr.20140727075002.18208: *3* BaseScanner.appendStringToBody & setBodyString
    def appendStringToBody (self,p,s):

        '''Similar to c.appendStringToBody,
        but does not recolor the text or redraw the screen.'''

        return self.importCommands.appendStringToBody(p,s)

    def setBodyString (self,p,s):

        '''Similar to c.setBodyString,
        but does not recolor the text or redraw the screen.'''

        return self.importCommands.setBodyString(p,s)
    #@+node:ekr.20140727075002.18209: *3* BaseScanner.computeBody
    def computeBody (self,s,start,sigStart,codeEnd):
        '''Return the head and tail of the body.'''
        trace = False
        body1 = s[start:sigStart]
        # Adjust start backwards to get a better undent.
        if body1.strip():
            while start > 0 and s[start-1] in (' ','\t'):
                start -= 1
        # g.trace(repr(s[sigStart:codeEnd]))
        body1 = self.undentBody(s[start:sigStart],ignoreComments=False)
        body2 = self.undentBody(s[sigStart:codeEnd])
        body = body1 + body2
        if trace: g.trace('body: %s' % repr(body))
        tail = body[len(body.rstrip()):]
        if not '\n' in tail:
            self.warning(
                '%s %s does not end with a newline; one will be added\n%s' % (
                self.functionSpelling,self.sigId,g.get_line(s,codeEnd)))
        return body1,body2
    #@+node:ekr.20140727075002.18210: *3* BaseScanner.createDeclsNode
    def createDeclsNode (self,parent,s):

        '''Create a child node of parent containing s.'''

        # Create the node for the decls.
        headline = '%s declarations' % self.methodName
        body = self.undentBody(s)
        self.createHeadline(parent,body,headline)
    #@+node:ekr.20140727075002.18211: *3* BaseScanner.createFunctionNode
    def createFunctionNode (self,headline,body,parent):

        # Create the prefix line for @root trees.
        if self.treeType == '@root':
            prefix = g.angleBrackets(' ' + headline + ' methods ') + '=\n\n'
            self.methodsSeen = True
        else:
            prefix = ''

        # Create the node.
        return self.createHeadline(parent,prefix + body,headline)

    #@+node:ekr.20140727075002.18212: *3* BaseScanner.createHeadline
    def createHeadline (self,parent,body,headline):

        return self.importCommands.createHeadline(parent,body,headline)
    #@+node:ekr.20140727075002.18213: *3* BaseScanner.endGen
    def endGen (self,s):
        '''Do any language-specific post-processing.'''
        pass
    #@+node:ekr.20140727075002.18214: *3* BaseScanner.getLeadingIndent
    def getLeadingIndent (self,s,i,ignoreComments=True):

        '''Return the leading whitespace of a line.
        Ignore blank and comment lines if ignoreComments is True'''

        width = 0
        i = g.find_line_start(s,i)
        if ignoreComments:
            while i < len(s):
                # g.trace(g.get_line(s,i))
                j = g.skip_ws(s,i)
                if g.is_nl(s,j) or g.match(s,j,self.comment_delim):
                    i = g.skip_line(s,i) # ignore blank lines and comment lines.
                else:
                    i, width = g.skip_leading_ws_with_indent(s,i,self.tab_width)
                    break      
        else:
            i, width = g.skip_leading_ws_with_indent(s,i,self.tab_width)

        # g.trace('returns:',width)
        return width
    #@+node:ekr.20140727075002.18215: *3* BaseScanner.indentBody
    def indentBody (self,s,lws=None):

        '''Add whitespace equivalent to one tab for all non-blank lines of s.'''

        result = []
        if not lws: lws = self.tab_ws

        for line in g.splitLines(s):
            if line.strip():
                result.append(lws + line)
            elif line.endswith('\n'):
                result.append('\n')

        result = ''.join(result)
        return result
    #@+node:ekr.20140727075002.18216: *3* BaseScanner.insertIgnoreDirective (leoImport)
    def insertIgnoreDirective (self,parent):

        c = self.c

        self.appendStringToBody(parent,'@ignore')

        if g.unitTesting:
            g.app.unitTestDict['fail'] = g.callers()
        else:
            if parent.isAnyAtFileNode() and not parent.isAtAutoNode():
                g.warning('inserting @ignore')
                c.import_error_nodes.append(parent.h)

    #@+node:ekr.20140727075002.18217: *3* BaseScanner.putClass & helpers
    def putClass (self,s,i,sigEnd,codeEnd,start,parent):

        '''Creates a child node c of parent for the class,
        and a child of c for each def in the class.'''

        trace = False
        if trace:
            # g.trace('tab_width',self.tab_width)
            g.trace('sig',repr(s[i:sigEnd]))

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
        prefix = self.createClassNodePrefix()
        if not self.sigId:
            g.trace('Can not happen: no sigId')
            self.sigId = 'Unknown class name'
        classHead = s[start:sigEnd]
        i = self.extendSignature(s,sigEnd)
        extend = s[sigEnd:i]
        if extend:
            classHead = classHead + extend

        # Create the class node.
        class_node = self.createHeadline(parent,'',headline)

        # Remember the indentation of the class line.
        undentVal = self.getLeadingIndent(classHead,0)

        # Call the helper to parse the inner part of the class.
        putRef,bodyIndent,classDelim,decls,trailing = self.putClassHelper(
            s,i,codeEnd,class_node)
        # g.trace('bodyIndent',bodyIndent,'undentVal',undentVal)

        # Set the body of the class node.
        ref = putRef and self.getClassNodeRef(class_name) or ''

        if trace: g.trace('undentVal',undentVal,'bodyIndent',bodyIndent)

        # Give ref the same indentation as the body of the class.
        if ref:
            bodyWs = g.computeLeadingWhitespace (bodyIndent,self.tab_width)
            ref = '%s%s' % (bodyWs,ref)

        # Remove the leading whitespace.
        result = (
            prefix +
            self.undentBy(classHead,undentVal) +
            self.undentBy(classDelim,undentVal) +
            self.undentBy(decls,undentVal) +
            self.undentBy(ref,undentVal) +
            self.undentBy(trailing,undentVal))

        result = self.adjust_class_ref(result)

        # Append the result to the class node.
        self.appendTextToClassNode(class_node,result)

        # Exit the new class: restore the previous class info.
        self.methodName = oldMethodName
        self.startSigIndent = oldStartSigIndent
    #@+node:ekr.20140727075002.18218: *4* BaseScanner.adjust_class_ref
    def adjust_class_ref(self,s):

        '''Over-ridden by xml and html scanners.'''

        return s
    #@+node:ekr.20140727075002.18219: *4* BaseScanner.appendTextToClassNode
    def appendTextToClassNode (self,class_node,s):

        self.appendStringToBody(class_node,s) 
    #@+node:ekr.20140727075002.18220: *4* BaseScanner.createClassNodePrefix
    def createClassNodePrefix (self):

        '''Create the class node prefix.'''

        if  self.treeType == '@root':
            prefix = g.angleBrackets(' ' + self.methodName + ' methods ') + '=\n\n'
            self.methodsSeen = True
        else:
            prefix = ''

        return prefix
    #@+node:ekr.20140727075002.18221: *4* BaseScanner.getClassNodeRef
    def getClassNodeRef (self,class_name):

        '''Insert the proper body text in the class_vnode.'''

        if self.treeType in ('@file',None):
            s = '@others'
        else:
            s = g.angleBrackets(' class %s methods ' % (class_name))

        return '%s\n' % (s)
    #@+node:ekr.20140727075002.18222: *4* BaseScanner.putClassHelper
    def putClassHelper(self,s,i,end,class_node):

        '''s contains the body of a class, not including the signature.

        Parse s for inner methods and classes, and create nodes.'''

        trace = False and not g.unitTesting

        # Increase the output indentation (used only in startsHelper).
        # This allows us to detect over-indented classes and functions.
        old_output_indent = self.output_indent
        self.output_indent += abs(self.tab_width)

        # Parse the decls.
        if self.hasDecls: # 2011/11/11
            j = i ; i = self.skipDecls(s,i,end,inClass=True)
            decls = s[j:i]
        else:
            decls = ''

        # Set the body indent if there are real decls.
        bodyIndent = decls.strip() and self.getIndent(s,i) or None
        if trace: g.trace('bodyIndent',bodyIndent)

        # Parse the rest of the class.
        delim1, delim2 = self.outerBlockDelim1, self.outerBlockDelim2
        if g.match(s,i,delim1):
            # Do *not* use g.skip_ws_and_nl here!
            j = g.skip_ws(s,i + len(delim1))
            if g.is_nl(s,j): j = g.skip_nl(s,j)
            classDelim = s[i:j]
            end2 = self.skipBlock(s,i,delim1=delim1,delim2=delim2)
            start,putRef,bodyIndent2 = self.scanHelper(s,j,end=end2,parent=class_node,kind='class')
        else:
            classDelim = ''
            start,putRef,bodyIndent2 = self.scanHelper(s,i,end=end,parent=class_node,kind='class')

        if bodyIndent is None: bodyIndent = bodyIndent2

        # Restore the output indentation.
        self.output_indent = old_output_indent

        # Return the results.
        trailing = s[start:end]
        return putRef,bodyIndent,classDelim,decls,trailing
    #@+node:ekr.20140727075002.18223: *3* BaseScanner.putFunction
    def putFunction (self,s,sigStart,codeEnd,start,parent):
        '''Create a node of parent for a function defintion.'''
        trace = False and not g.unitTesting
        verbose = True
        # Enter a new function: save the old function info.
        oldStartSigIndent = self.startSigIndent
        if self.sigId:
            headline = self.sigId
        else:
            g.trace('Can not happen: no sigId')
            headline = 'unknown function'
        body1,body2 = self.computeBody(s,start,sigStart,codeEnd)
        body = body1 + body2
        parent = self.adjustParent(parent,headline)
        if trace:
            # pylint: disable=maybe-no-member
            g.trace('parent',parent and parent.h)
            if verbose:
                # g.trace('**body1...\n',body1)
                g.trace(self.atAutoSeparateNonDefNodes)
                g.trace('**body...\n%s' % body)
        # 2010/11/04: Fix wishlist bug 670744.
        if self.atAutoSeparateNonDefNodes:
            if body1.strip():
                if trace: g.trace('head',body1)
                line1 = g.splitLines(body1.lstrip())[0]
                line1 = line1.strip() or 'non-def code'
                self.createFunctionNode(line1,body1,parent)
                body = body2
        self.lastParent = self.createFunctionNode(headline,body,parent)
        # Exit the function: restore the function info.
        self.startSigIndent = oldStartSigIndent
    #@+node:ekr.20140727075002.18224: *3* BaseScanner.putRootText
    def putRootText (self,p):

        self.appendStringToBody(p,'%s@language %s\n@tabwidth %d\n' % (
            self.rootLine,self.alternate_language or self.language,self.tab_width))
    #@+node:ekr.20140727075002.18225: *3* BaseScanner.undentBody
    def undentBody (self,s,ignoreComments=True):

        '''Remove the first line's leading indentation from all lines of s.'''

        trace = False
        if trace: g.trace('before...\n',g.listToString(g.splitLines(s)))

        if self.isRst:
            return s # Never unindent rst code.

        # Calculate the amount to be removed from each line.
        undentVal = self.getLeadingIndent(s,0,ignoreComments=ignoreComments)
        if undentVal == 0:
            return s
        else:
            result = self.undentBy(s,undentVal)
            if trace: g.trace('after...\n',g.listToString(g.splitLines(result)))
            return result
    #@+node:ekr.20140727075002.18226: *3* BaseScanner.undentBy
    def undentBy (self,s,undentVal):

        '''Remove leading whitespace equivalent to undentVal from each line.
        For strict languages, add an underindentEscapeString for underindented line.'''

        trace = False and not g.app.unitTesting
        if self.isRst:
            return s # Never unindent rst code.

        tag = self.c.atFileCommands.underindentEscapeString
        result = [] ; tab_width = self.tab_width
        for line in g.splitlines(s):
            lws_s = g.get_leading_ws(line)
            lws = g.computeWidth(lws_s,tab_width)
            s = g.removeLeadingWhitespace(line,undentVal,tab_width)
            # 2011/10/29: Add underindentEscapeString only for strict languages.
            if self.strict and s.strip() and lws < undentVal:
                if trace: g.trace('undentVal: %s, lws: %s, %s' % (
                    undentVal,lws,repr(line)))
                # Bug fix 2012/06/05: end the underindent count with a period,
                # to protect against lines that start with a digit!
                result.append("%s%s.%s" % (tag,undentVal-lws,s.lstrip()))
            else:
                if trace: g.trace(repr(s))
                result.append(s)
        return ''.join(result)
    #@+node:ekr.20140727075002.18227: *3* BaseScanner.underindentedComment & underindentedLine
    def underindentedComment (self,line):

        if self.atAutoWarnsAboutLeadingWhitespace:
            self.warning(
                'underindented python comments.\nExtra leading whitespace will be added\n' + line)

    def underindentedLine (self,line):

        if self.warnAboutUnderindentedLines:
            self.error(
                'underindented line.\n' +
                'Extra leading whitespace will be added\n' + line)
    #@+node:ekr.20140727075002.18228: ** BaseScanner.error, oops, report and warning
    def error (self,s):
        self.errors += 1
        self.importCommands.errors += 1
        if g.unitTesting:
            if self.errors == 1:
                g.app.unitTestDict ['actualErrorMessage'] = s
            g.app.unitTestDict ['actualErrors'] = self.errors
            if 0: # For debugging unit tests.
                g.trace(g.callers())
                g.error('',s)
        else:
            g.error('Error:',s)

    def oops (self):
        g.pr('BaseScanner oops: %s must be overridden in subclass' % g.callers())

    def report (self,message):
        if self.strict: self.error(message)
        else:           self.warning(message)

    def warning (self,s):
        if not g.unitTesting:
            g.warning('Warning:',s)
    #@+node:ekr.20140727075002.18229: ** BaseScanner.headlineForNode
    def headlineForNode(self,fn,p):
        '''Return the expected imported headline for p.b'''
        trace = False and not g.unitTesting
        # From scan: parse the decls.s
        s = p.b
        if False: # and self.n_decls == 0 and self.hasDecls:
            i = self.skipDecls(s,0,len(s),inClass=False)
            decls = s[:i]
            if decls:
                self.n_decls += 1
                val = '%s declarations' % fn
                if trace and val != p.h: g.trace(p.h,'==>',val)
                return val
        # From scanHelper: look for the first def or class.
        i = 0
        while i < len(s):
            progress = i
            if s[i] in (' ','\t','\n'):
                i += 1 # Prevent lookahead below, and speed up the scan.
            elif self.startsComment(s,i):
                i = self.skipComment(s,i)
            elif self.startsString(s,i):
                i = self.skipString(s,i)
            elif self.startsClass(s,i):
                val = 'class '+self.sigId
                if trace and val != p.h: g.trace(p.h,'==>',val)
                return val
            elif self.startsFunction(s,i):
                val = self.sigId
                if trace and val != p.h: g.trace(p.h,'==>',val)
                return val
            elif self.startsId(s,i):
                i = self.skipId(s,i)
            elif g.match(s,i,self.outerBlockDelim1): # and kind == 'outer'
                # Do this after testing for classes.
                i = self.skipBlock(s,i,delim1=self.outerBlockDelim1,delim2=self.outerBlockDelim2)
            else: i += 1
            if progress >= i:
                i = self.skipBlock(s,i,delim1=self.outerBlockDelim1,delim2=self.outerBlockDelim2)
            assert progress < i,'i: %d, ch: %s' % (i,repr(s[i]))
        return p.h
    #@+node:ekr.20140727075002.18230: ** BaseScanner.Parsing
    #@+at Scan and skipDecls would typically not be overridden.
    #@+node:ekr.20140727075002.18231: *3* BaseScanner.adjustDefStart
    def adjustDefStart (self,unused_s,i):

        '''A hook to allow the Python importer to adjust the 
        start of a class or function to include decorators.'''

        return i
    #@+node:ekr.20140727075002.18232: *3* BaseScanner.extendSignature
    def extendSignature(self,unused_s,i):

        '''Extend the signature line if appropriate.
        The text *must* end with a newline.

        For example, the Python scanner appends docstrings if they exist.'''

        return i
    #@+node:ekr.20140727075002.18233: *3* BaseScanner.getIndent
    def getIndent (self,s,i):

        j,junk = g.getLine(s,i)
        junk,indent = g.skip_leading_ws_with_indent(s,j,self.tab_width)
        return indent
    #@+node:ekr.20140727075002.18234: *3* BaseScanner.prepass & helper
    def prepass (self,s,p):
        '''
        A prepass for the at-file-to-at-auto command.
        Return (ok,aList)
        ok: False if p.b should be split two or more sibling nodes.
        aList: a list of tuples (i,j,headline,p) indicating split nodes.
        '''
        trace = False and not g.unitTesting
        # From scanHelper...
        delim1,delim2 = self.outerBlockDelim1,self.outerBlockDelim2
        p = p.copy()
        classSeen,refSeen = False,False
        i,n,parts,start = 0,0,[],0
        while i < len(s):
            progress = i
            if s[i] in (' ','\t','\n'):
                i += 1 # Prevent lookahead below, and speed up the scan.
            elif self.startsComment(s,i):
                i = self.skipComment(s,i)
            elif self.startsString(s,i):
                i = self.skipString(s,i)
            elif s[i:i+2] == '<<':
                j = g.skip_line(s,i+2)
                k = s.find('>>',i+2)
                if -1 < k < j:
                    g.trace(s[i:k+2])
                    refSeen = True
                    i = k+2
                else:
                    i += 2
            elif self.startsClass(s,i):
                # g.trace('class',i,s[i:i+20])
                # Extend the previous definition.
                if n > 0 and start < i:
                    i1,i2,id2,p2 = parts.pop()
                    parts.append((i1,i,id2,p2),)
                classSeen = True
                start,i = i,self.codeEnd
                parts.append((start,i,self.sigId,p),)
                n += 1
            elif self.startsFunction(s,i):
                # g.trace('func',i,s[i:i+20])
                # Extend the previous definition.
                if n > 0 and start < i:
                    i1,i2,id2,p2 = parts.pop()
                    parts.append((i1,i,id2,p2),)
                start,i = i,self.codeEnd
                parts.append((start,i,self.sigId,p),)
                n += 1
            elif self.startsId(s,i):
                i = self.skipId(s,i)
            elif g.match(s,i,delim1):
                # Do this after testing for classes.
                i = self.skipBlock(s,i,delim1,delim2)
            else:
                i += 1
            if progress >= i:
                i = self.skipBlock(s,i,delim1,delim2)
            assert progress < i,'i: %d, ch: %s' % (i,repr(s[i]))
        if n > 0 and start < i:
            i1,i2,id2,p2 = parts.pop()
            parts.append((i1,len(s),id2,p2),)
        if n <= 1 and not refSeen:
            return True,[] # Only one definition.
        elif p.hasChildren() or classSeen or refSeen:
            # Can't split safely.
            if trace: g.trace('can not split\n',''.join([
                '\n----- %s\n%s\n' % (z[2],s[z[0]:z[1]]) for z in parts]))
            return False,[]
        else:
            # Multiple defs, no children. Will split the node into children.
            return False,parts
    #@+node:ekr.20140727075002.18235: *3* BaseScanner.scan & scanHelper
    def scan (self,s,parent,parse_body=False):
        '''A language independent scanner: it uses language-specific helpers.

        Create a child of self.root for:
        - Leading outer-level declarations.
        - Outer-level classes.
        - Outer-level functions.
        '''
        # Init the parser status ivars.
        self.methodsSeen = False
        # Create the initial body text in the root.
        if parse_body:
            pass
        else:
            self.putRootText(parent)
        # Parse the decls.
        if self.hasDecls:
            i = self.skipDecls(s,0,len(s),inClass=False)
            decls = s[:i]
        else:
            i,decls = 0,''
        # Create the decls node.
        if decls: self.createDeclsNode(parent,decls)
        # Scan the rest of the file.
        start,junk,junk = self.scanHelper(s,i,end=len(s),parent=parent,kind='outer')
        # Finish adding to the parent's body text.
        self.addRef(parent)
        if start < len(s):
            self.appendStringToBody(parent,s[start:])
        # Do any language-specific post-processing.
        self.endGen(s)
    #@+node:ekr.20140727075002.18236: *4* BaseScanner.scanHelper
    def scanHelper(self,s,i,end,parent,kind):
        '''Common scanning code used by both scan and putClassHelper.'''
        # g.trace(g.callers())
        # g.trace('i',i,g.get_line(s,i))
        assert kind in ('class','outer')
        start = i ; putRef = False ; bodyIndent = None
        # Major change: 2011/11/11: prevent scanners from going beyond end.
        if self.hasNestedClasses and end < len(s):
            s = s[:end] # Potentially expensive, but unavoidable.
        # if g.unitTesting: g.pdb()
        while i < end:
            progress = i
            if s[i] in (' ','\t','\n'):
                i += 1 # Prevent lookahead below, and speed up the scan.
            elif self.startsComment(s,i):
                i = self.skipComment(s,i)
            elif self.startsString(s,i):
                i = self.skipString(s,i)
            elif self.startsClass(s,i):  # Sets sigStart,sigEnd & codeEnd ivars.
                putRef = True
                if bodyIndent is None: bodyIndent = self.getIndent(s,i)
                end2 = self.codeEnd # putClass may change codeEnd ivar.
                self.putClass(s,i,self.sigEnd,self.codeEnd,start,parent)
                i = start = end2
            elif self.startsFunction(s,i): # Sets sigStart,sigEnd & codeEnd ivars.
                putRef = True
                if bodyIndent is None: bodyIndent = self.getIndent(s,i)
                self.putFunction(s,self.sigStart,self.codeEnd,start,parent)
                i = start = self.codeEnd
            elif self.startsId(s,i):
                i = self.skipId(s,i)
            elif kind == 'outer' and g.match(s,i,self.outerBlockDelim1): # Do this after testing for classes.
                # i1 = i # for debugging
                i = self.skipBlock(s,i,delim1=self.outerBlockDelim1,delim2=self.outerBlockDelim2)
                # Bug fix: 2007/11/8: do *not* set start: we are just skipping the block.
            else: i += 1
            if progress >= i:
                # g.pdb()
                i = self.skipBlock(s,i,delim1=self.outerBlockDelim1,delim2=self.outerBlockDelim2)
            assert progress < i,'i: %d, ch: %s' % (i,repr(s[i]))

        return start,putRef,bodyIndent
    #@+node:ekr.20140727075002.18237: *3* BaseScanner.Parser skip methods
    #@+node:ekr.20140727075002.18238: *4* BaseScanner.isSpace
    def isSpace(self,s,i):

        '''Return true if s[i] is a tokenizer space.'''

        # g.trace(repr(s[i]),i < len(s) and s[i] != '\n' and s[i].isspace())

        return i < len(s) and s[i] != '\n' and s[i].isspace()
    #@+node:ekr.20140727075002.18239: *4* BaseScanner.skipArgs
    def skipArgs (self,s,i,kind):

        '''Skip the argument or class list.  Return i, ok

        kind is in ('class','function')'''

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
    #@+node:ekr.20140727075002.18240: *4* BaseScanner.skipBlock
    def skipBlock(self,s,i,delim1=None,delim2=None):

        '''Skip from the opening delim to *past* the matching closing delim.

        If no matching is found i is set to len(s)'''

        trace = False and not g.unitTesting
        verbose = False
        if delim1 is None: delim1 = self.blockDelim1
        if delim2 is None: delim2 = self.blockDelim2
        match1 = g.match if len(delim1)==1 else g.match_word
        match2 = g.match if len(delim2)==1 else g.match_word
        assert match1(s,i,delim1)
        level,start,startIndent = 0,i,self.startSigIndent
        if trace and verbose:
            g.trace('***','startIndent',startIndent)
        while i < len(s):
            progress = i
            if g.is_nl(s,i):
                backslashNewline = i > 0 and g.match(s,i-1,'\\\n')
                i = g.skip_nl(s,i)
                if not backslashNewline and not g.is_nl(s,i):
                    j, indent = g.skip_leading_ws_with_indent(s,i,self.tab_width)
                    line = g.get_line(s,j)
                    if trace and verbose: g.trace('indent',indent,line)
                    if indent < startIndent and line.strip():
                        # An non-empty underindented line.
                        # Issue an error unless it contains just the closing bracket.
                        if level == 1 and match2(s,j,delim2):
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
            elif match1(s,i,delim1):
                level += 1 ; i += len(delim1)
            elif match2(s,i,delim2):
                level -= 1 ; i += len(delim2)
                # Skip junk following Pascal 'end'
                for z in self.blockDelim2Cruft:
                    i2 = self.skipWs(s,i)
                    if g.match(s,i2,z):
                        i = i2 + len(z)
                        break
                if level <= 0:
                    # 2010/09/20
                    # Skip a single-line comment if it exists.
                    j = self.skipWs(s,i)
                    if (g.match(s,j,self.lineCommentDelim) or
                        g.match(s,j,self.lineCommentDelim2)
                    ):
                        i = g.skip_to_end_of_line(s,i)
                    if trace: g.trace('returns:\n\n%s\n\n' % s[start:i])
                    return i

            else: i += 1
            assert progress < i

        self.error('no block: %s' % self.root.h)
        if 1:
            i,j = g.getLine(s,start)
            g.trace(i,s[i:j])
        else:
            if trace: g.trace('** no block')
        return start+1 # 2012/04/04: Ensure progress in caller.
    #@+node:ekr.20140727075002.18241: *4* BaseScanner.skipCodeBlock
    def skipCodeBlock (self,s,i,kind):
        '''Skip the code block in a function or class definition.'''
        trace = False
        start = i
        i = self.skipBlock(s,i,delim1=None,delim2=None)
        if self.sigFailTokens:
            i = self.skipWs(s,i)
            for z in self.sigFailTokens:
                if g.match(s,i,z):
                    if trace: g.trace('failtoken',z)
                    return start,False
        if i > start:
            i = self.skipNewline(s,i,kind)
        if trace:
            # g.trace(g.callers())
            # g.trace('returns...\n',g.listToString(g.splitLines(s[start:i])))
            g.trace('returns:\n\n%s\n\n' % s[start:i])
        return i,True
    #@+node:ekr.20140727075002.18242: *4* BaseScanner.skipComment & helper
    def skipComment (self,s,i):

        '''Skip a comment and return the index of the following character.'''

        if g.match(s,i,self.lineCommentDelim) or g.match(s,i,self.lineCommentDelim2):
            return g.skip_to_end_of_line(s,i)
        else:
            return self.skipBlockComment(s,i)
    #@+node:ekr.20140727075002.18243: *5* BaseScanner.skipBlockComment
    def skipBlockComment (self,s,i):

        '''Skip past a block comment.'''

        start = i

        # Skip the opening delim.
        if g.match(s,i,self.blockCommentDelim1):
            delim2 = self.blockCommentDelim2
            i += len(self.blockCommentDelim1)
        elif g.match(s,i,self.blockCommentDelim1_2):
            i += len(self.blockCommentDelim1_2)
            delim2 = self.blockCommentDelim2_2
        else:
            assert False

        # Find the closing delim.
        k = s.find(delim2,i)
        if k == -1:
            self.error('Run on block comment: ' + s[start:i])
            return len(s)
        else:
            return k + len(delim2)
    #@+node:ekr.20140727075002.18244: *4* BaseScanner.skipDecls
    def skipDecls (self,s,i,end,inClass):
        '''
        Skip everything until the start of the next class or function.
        The decls *must* end in a newline.
        '''
        trace = False or self.trace
        start = i ; prefix = None
        classOrFunc = False
        if trace: g.trace(g.callers())
        # Major change: 2011/11/11: prevent scanners from going beyond end.
        if self.hasNestedClasses and end < len(s):
            s = s[:end] # Potentially expensive, but unavoidable.
        while i < end:
            progress = i
            if s[i] in (' ','\t','\n'):
                i += 1 # Prevent lookahead below, and speed up the scan.
            elif self.startsComment(s,i):
                # Add the comment to the decl if it *doesn't* start the line.
                i2,junk = g.getLine(s,i)
                i2 = self.skipWs(s,i2)
                if i2 == i and prefix is None:
                    prefix = i2 # Bug fix: must include leading whitespace in the comment.
                i = self.skipComment(s,i)
            elif self.startsString(s,i):
                i = self.skipString(s,i)
                prefix = None
            elif self.startsClass(s,i):
                # Important: do not include leading ws in the decls.
                classOrFunc = True
                i = g.find_line_start(s,i)
                i = self.adjustDefStart(s,i)
                break
            elif self.startsFunction(s,i):
                # Important: do not include leading ws in the decls.
                classOrFunc = True
                i = g.find_line_start(s,i)
                i = self.adjustDefStart(s,i)
                break
            elif self.startsId(s,i):
                i = self.skipId(s,i)
                prefix = None
            # Don't skip outer blocks: they may contain classes.
            elif g.match(s,i,self.outerBlockDelim1):
                if self.outerBlockEndsDecls:
                    break
                else:
                    i = self.skipBlock(s,i,
                        delim1=self.outerBlockDelim1,
                        delim2=self.outerBlockDelim2)
            else:
                i += 1 ;  prefix = None
            assert(progress < i)
        if prefix is not None:
            i = g.find_line_start(s,prefix) # i = prefix
        decls = s[start:i]
        if inClass and not classOrFunc:
            # Don't return decls if a class contains nothing but decls.
            if trace and decls.strip(): g.trace('**class is all decls...\n',decls)
            return start
        elif decls.strip(): 
            if trace or self.trace: g.trace('\n'+decls)
            return i
        else: # Ignore empty decls.
            return start
    #@+node:ekr.20140727075002.18245: *4* BaseScanner.skipId
    def skipId (self,s,i):

        return g.skip_id(s,i,chars=self.extraIdChars)
    #@+node:ekr.20140727075002.18246: *4* BaseScanner.skipNewline
    def skipNewline(self,s,i,kind):
        '''
        Called by skipCodeBlock to terminate a function defintion.
        Skip whitespace and comments up to a newline, then skip the newline.
        Issue an error if no newline is found.
        '''
        while i < len(s):
            i = self.skipWs(s,i)
            if self.startsComment(s,i):
                i = self.skipComment(s,i)
            else: break
        if i >= len(s):
            return len(s)
        if g.match(s,i,'\n'):
            i += 1
        else:
            self.error(
                '%s %s does not end in a newline; one will be added\n%s' % (
                    kind,self.sigId,g.get_line(s,i)))
        return i
    #@+node:ekr.20140727075002.18247: *4* BaseScanner.skipParens
    def skipParens (self,s,i):

        '''Skip a parenthisized list, that might contain strings or comments.'''

        return self.skipBlock(s,i,delim1='(',delim2=')')
    #@+node:ekr.20140727075002.18248: *4* BaseScanner.skipString
    def skipString (self,s,i):

        # Returns len(s) on unterminated string.
        return g.skip_string(s,i,verbose=False)
    #@+node:ekr.20140727075002.18249: *4* BaseScanner.skipWs
    def skipWs (self,s,i):

        return g.skip_ws(s,i)
    #@+node:ekr.20140727075002.18250: *3* BaseScanner.startsClass/Function & helpers
    # We don't expect to override this code, but subclasses may override the helpers.

    def startsClass (self,s,i):
        '''Return True if s[i:] starts a class definition.
        Sets sigStart, sigEnd, sigId and codeEnd ivars.'''
        val = self.hasClasses and self.startsHelper(s,i,kind='class',tags=self.classTags)
        return val

    def startsFunction (self,s,i):
        '''Return True if s[i:] starts a function.
        Sets sigStart, sigEnd, sigId and codeEnd ivars.'''
        val = self.hasFunctions and self.startsHelper(s,i,kind='function',tags=self.functionTags)
        return val
    #@+node:ekr.20140727075002.18251: *4* BaseScanner.getSigId
    def getSigId (self,ids):

        '''Return the signature's id.

        By default, this is the last id in the ids list.'''

        return ids and ids[-1]
    #@+node:ekr.20140727075002.18252: *4* BaseScanner.skipSigStart
    def skipSigStart (self,s,i,kind,tags):

        '''Skip over the start of a function/class signature.

        tags is in (self.classTags,self.functionTags).

        Return (i,ids) where ids is list of all ids found, in order.'''

        trace = False and self.trace # or kind =='function'
        ids = [] ; classId = None
        if trace: g.trace('*entry',kind,i,s[i:i+20])
        start = i
        while i < len(s):
            j = g.skip_ws_and_nl(s,i)
            for z in self.sigFailTokens:
                if g.match(s,j,z):
                    if trace: g.trace('failtoken',z,'ids',ids)
                    return start, [], None
            for z in self.sigHeadExtraTokens:
                if g.match(s,j,z):
                    i += len(z) ; break
            else:
                i = self.skipId(s,j)
                theId = s[j:i]
                if theId and theId in tags: classId = theId
                if theId: ids.append(theId)
                else: break

        if trace: g.trace('*exit ',kind,i,i < len(s) and s[i],ids,classId)
        return i, ids, classId
    #@+node:ekr.20140727075002.18253: *4* BaseScanner.skipSigTail
    def skipSigTail(self,s,i,kind):

        '''Skip from the end of the arg list to the start of the block.'''

        trace = False and self.trace
        start = i
        i = self.skipWs(s,i)
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
    #@+node:ekr.20140727075002.18254: *4* BaseScanner.startsHelper
    def startsHelper(self,s,i,kind,tags,tag=None):
        '''
        tags is a list of id's.  tag is a debugging tag.
        return True if s[i:] starts a class or function.
        Sets sigStart, sigEnd, sigId and codeEnd ivars.
        '''
        trace = False or self.trace
        verbose = True # kind=='function'
        self.codeEnd = self.sigEnd = self.sigId = None
        self.sigStart = i
        # Underindented lines can happen in any language, not just Python.
        # The skipBlock method of the base class checks for such lines.
        self.startSigIndent = self.getLeadingIndent(s,i)
        # Get the tag that starts the class or function.
        j = g.skip_ws_and_nl(s,i)
        i = self.skipId(s,j)
        self.sigId = theId = s[j:i] # Set sigId ivar 'early' for error messages.
        if not theId: return False
        if tags:
            if self.caseInsensitive:
                theId = theId.lower()
            if theId not in tags:
                if trace and verbose:
                    # g.trace('**** %s theId: %s not in tags: %s' % (kind,theId,tags))
                    g.trace('%8s: ignoring %s' % (kind,theId))
                return False
        if trace and verbose: g.trace('kind',kind,'id',theId)
        # Get the class/function id.
        if kind == 'class' and self.sigId in self.anonymousClasses:
            # A hack for Delphi Pascal: interfaces have no id's.
            # g.trace('anonymous',self.sigId)
            classId = theId
            sigId = ''
        else:
            i, ids, classId = self.skipSigStart(s,j,kind,tags) # Rescan the first id.
            sigId = self.getSigId(ids)
            if not sigId:
                if trace and verbose: g.trace('**no sigId',g.get_line(s,i))
                return False
        if self.output_indent < self.startSigIndent:
            if trace: g.trace('**over-indent',sigId)
                #,'output_indent',self.output_indent,'startSigIndent',self.startSigIndent)
            return False
        # Skip the argument list.
        i, ok = self.skipArgs(s,i,kind)
        if not ok:
            if trace and verbose: g.trace('no args',g.get_line(s,i))
            return False
        i = g.skip_ws_and_nl(s,i)
        # Skip the tail of the signature
        i, ok = self.skipSigTail(s,i,kind)
        if not ok:
            if trace and verbose: g.trace('no tail',g.get_line(s,i))
            return False
        sigEnd = i
        # A trick: make sure the signature ends in a newline,
        # even if it overlaps the start of the block.
        if not g.match(s,sigEnd,'\n') and not g.match(s,sigEnd-1,'\n'):
            if trace and verbose: g.trace('extending sigEnd')
            sigEnd = g.skip_line(s,sigEnd)
        if self.blockDelim1:
            i = g.skip_ws_and_nl(s,i)
            if kind == 'class' and self.sigId in self.anonymousClasses:
                pass # Allow weird Pascal unit's.
            elif not g.match(s,i,self.blockDelim1):
                if trace and verbose: g.trace('no block',g.get_line(s,i))
                return False
        i,ok = self.skipCodeBlock(s,i,kind)
        if not ok: return False
            # skipCodeBlock skips the trailing delim.
        # This assert ensures that all class/function/method definitions end with a newline.
        # It would be False for language like html/xml, but they override this method.
        assert i > 0 and s[i-1] == '\n' or i == len(s)
        # Success: set the ivars.
        self.sigStart = self.adjustDefStart(s,self.sigStart)
        self.codeEnd = i
        self.sigEnd = sigEnd
        self.sigId = sigId
        self.classId = classId
        # Note: backing up here is safe because
        # we won't back up past scan's 'start' point.
        # Thus, characters will never be output twice.
        k = self.sigStart
        if not g.match(s,k,'\n'):
            self.sigStart = g.find_line_start(s,k)
        # Issue this warning only if we have a real class or function.
        if 0: # wrong.
            if s[self.sigStart:k].strip():
                self.error('%s definition does not start a line\n%s' % (
                    kind,g.get_line(s,k)))
        if trace:
            if verbose:
                g.trace(kind,'returns:\n%s' % s[self.sigStart:i])
            else:
                first_line = g.splitLines(s[self.sigStart:i])[0]
                g.trace(kind,first_line.rstrip())
        return True
    #@+node:ekr.20140727075002.18255: *3* BaseScanner.startsComment
    def startsComment (self,s,i):

        return (
            g.match(s,i,self.lineCommentDelim) or
            g.match(s,i,self.lineCommentDelim2) or
            g.match(s,i,self.blockCommentDelim1) or
            g.match(s,i,self.blockCommentDelim1_2)
        )
    #@+node:ekr.20140727075002.18256: *3* BaseScanner.startsId
    def startsId(self,s,i):

        return g.is_c_id(s[i:i+1])
    #@+node:ekr.20140727075002.18257: *3* BaseScanner.startsString
    def startsString(self,s,i):

        return g.match(s,i,'"') or g.match(s,i,"'")
    #@+node:ekr.20140727075002.18258: ** BaseScanner.run
    def run (self,s,parent,parse_body=False,prepass=False):
        '''The common top-level code for all scanners.'''
        self.isPrepass = prepass
        c = self.c
        self.root = root = parent.copy()
        self.file_s = s
        self.tab_width = self.importCommands.getTabWidth(p=root)
        # Create the ws equivalent to one tab.
        self.tab_ws = ' '*abs(self.tab_width) if self.tab_width < 0 else '\t'
        # Init the error/status info.
        self.errors = 0
        self.errorLines = []
        self.mismatchWarningGiven = False
        changed = c.isChanged()
        # Use @verbatim to escape section references (but not for @auto).
        if self.escapeSectionRefs and not self.atAuto: 
            s = self.escapeFalseSectionReferences(s)
        # Check for intermixed blanks and tabs.
        if self.strict or self.atAutoWarnsAboutLeadingWhitespace:
            if not self.isRst:
                self.checkBlanksAndTabs(s)
        # Regularize leading whitespace (strict languages only).
        if self.strict: s = self.regularizeWhitespace(s) 
        # Generate the nodes, including directives and section references.
        if self.isPrepass:
            return self.prepass(s,parent)
        else:
            self.scan(s,parent,parse_body=parse_body)
            # Check the generated nodes.
            # Return True if the result is equivalent to the original file.
            ok = self.errors == 0 and self.check(s,parent)
            g.app.unitTestDict ['result'] = ok
            # Insert an @ignore directive if there were any serious problems.
            if not ok: self.insertIgnoreDirective(parent)
            if self.atAuto and ok:
                for p in root.self_and_subtree():
                    p.clearDirty()
                c.setChanged(changed)
            else:
                root.setDirty(setDescendentsDirty=False)
                c.setChanged(True)
            return ok
    #@+node:ekr.20140727075002.18271: *3* BaseScanner.escapeFalseSectionReferences
    def escapeFalseSectionReferences(self,s):
        '''
        Probably a bad idea.  Keep the apparent section references.
        The perfect-import write code no longer attempts to expand references
        when the perfectImportFlag is set.
        '''
        return s 

        # result = []
        # for line in g.splitLines(s):
            # r1 = line.find('<<')
            # r2 = line.find('>>')
            # if r1>=0 and r2>=0 and r1<r2:
                # result.append("@verbatim\n")
                # result.append(line)
            # else:
                # result.append(line)
        # return ''.join(result)
    #@+node:ekr.20140727075002.18259: *3* BaseScanner.checkBlanksAndTabs
    def checkBlanksAndTabs(self,s):

        '''Check for intermixed blank & tabs.'''

        # Do a quick check for mixed leading tabs/blanks.
        blanks = tabs = 0

        for line in g.splitLines(s):
            lws = line[0:g.skip_ws(line,0)]
            blanks += lws.count(' ')
            tabs += lws.count('\t')

        ok = blanks == 0 or tabs == 0

        if not ok:
            self.report('intermixed blanks and tabs')

        return ok
    #@+node:ekr.20140727075002.18260: *3* BaseScanner.regularizeWhitespace
    def regularizeWhitespace (self,s):

        '''Regularize leading whitespace in s:
        Convert tabs to blanks or vice versa depending on the @tabwidth in effect.
        This is only called for strict languages.'''

        changed = False ; lines = g.splitLines(s) ; result = [] ; tab_width = self.tab_width

        if tab_width < 0: # Convert tabs to blanks.
            for line in lines:
                i, w = g.skip_leading_ws_with_indent(line,0,tab_width)
                s = g.computeLeadingWhitespace(w,-abs(tab_width)) + line [i:] # Use negative width.
                if s != line: changed = True
                result.append(s)
        elif tab_width > 0: # Convert blanks to tabs.
            for line in lines:
                s = g.optimizeLeadingWhitespace(line,abs(tab_width)) # Use positive width.
                if s != line: changed = True
                result.append(s)

        if changed:
            action = 'tabs converted to blanks' if self.tab_width < 0 else 'blanks converted to tabs'
            message = 'inconsistent leading whitespace. %s' % action
            self.report(message)

        return ''.join(result)
    #@+node:ekr.20140727075002.18261: ** BaseScanner.Tokenizing
    #@+node:ekr.20140727075002.18262: *3* BaseScanner.skip...Token
    def skipCommentToken (self,s,i):
        j = self.skipComment(s,i)
        return j,s[i:j]

    def skipIdToken (self,s,i):
        j = self.skipId(s,i)
        return j,s[i:j]

    def skipNewlineToken (self,s,i):
        return i+1,'\n'

    def skipOtherToken (self,s,i):
        return i+1,s[i]

    def skipStringToken(self,s,i):
        j = self.skipString(s,i)
        return j,s[i:j]

    def skipWsToken(self,s,i):
        j = i
        while i < len(s) and s[i] != '\n' and s[i].isspace():
            i += 1
        return i,s[j:i]

    #@+node:ekr.20140727075002.18263: *3* BaseScanner.tokenize
    def tokenize (self,s):

        '''Tokenize string s and return a list of tokens (kind,value,line_number)

        where kind is in ('comment,'id','nl','other','string','ws').

        This is used only to verify the imported text.
        '''

        result,i,line_number = [],0,0
        while i < len(s):
            progress = j = i
            ch = s[i]
            if ch == '\n':
                kind = 'nl'
                i,val = self.skipNewlineToken(s,i)
            elif ch in ' \t': # self.isSpace(s,i):
                kind = 'ws'
                i,val = self.skipWsToken(s,i)
            elif self.startsComment(s,i):
                kind = 'comment'
                i,val = self.skipCommentToken(s,i)
            elif self.startsString(s,i):
                kind = 'string'
                i,val = self.skipStringToken(s,i)
            elif self.startsId(s,i):
                kind = 'id'
                i,val = self.skipIdToken(s,i)
            else:
                kind = 'other'
                i,val = self.skipOtherToken(s,i)
            assert progress < i and j == progress
            if val:
                result.append((kind,val,line_number),)
            # Use the raw token, s[j:i] to count newlines, not the munged val.
            line_number += s[j:i].count('\n')
            # g.trace('%3s %7s %s' % (line_number,kind,repr(val[:20])))
        return result
    #@-others
#@-leo
