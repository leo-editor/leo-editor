#@+leo-ver=5-thin
#@+node:ekr.20140727075002.18109: * @file importers/basescanner.py
#@+<< basescanner docstring >>
#@+node:ekr.20161029051724.1: ** << basescanner docstring >>
'''
#@@language rest
#@@wrap

Legacy (character-oriented) importers use BaseScanner class.

New (line-oriented) importers use ImportController class. Here's how:

**Executive overview**

New importers, for example, the javascript and perl importers, copy entire
lines from the input file to Leo nodes. This makes the new importers much
less error prone than the legacy (character-by-character) importers.

New importers *nothing* about parsing. They know only about how to scan
tokens *accurately*. Again, this makes the new importers more simple and
robust than the legacy importers.

New importers are simple to write because two base classes handle all
complex details. Importers override just three methods. The `scan_line`
method is the most important of these. It is straightforward token-scanning
code.

**Overview of the code**

`leo/plugins/basescanner.py` contains two new classes: `ImportController`
(IC) and `LineScanner` classes. The IC class replaces the horribly complex
BaseScanner class.

The LineScanner class encapsulates *all* language-dependent knowledge.

Using LineScanner methods, `IC.scan` breaks input files Leo nodes. This is
necessarily a complex algorithm.

Leo's import infrastructure, in `leoImport.py`, instantiates the scanner
and calls `IC.run`, which calls `IC.scan`.

**Writing a new importer**

New style importers consist of the following:

1. A subclass of ImportController class that overrides two methods, the ctor
   and an optional `clean_headline method`. This method tells how to
   simplify headlines.

2. A subclass of the LineScanner class that overrides `LineScanner.scan_line`.

`LineScanner.scan_line` updates the net number of curly brackets and parens
at the end of each line. `scan_line` must compute these numbers
*accurately*, taking into account constructs such as multi-line comments,
strings and regular expressions.

**Importing Python**

The `LineScanner` class would have to be completely rewritten for Python
because Python uses indentation levels to indicate structure, not curly
brackets.

**Summary**

Writing a new-style (line-by-line) importer is easy because the `LineScanner`
and `ImportController` classes hide all complex details.

The `LineScanner` class encapsulate *all* language-specific information.

Most importers simply override `LineScanner.scan_line`, which simply scans
tokens. The entire `LineScanner` would have to be rewritten for languages
such as Python.
'''
#@-<< basescanner docstring >>
#@+<< basescanner imports >>
#@+node:ekr.20161027163734.1: ** << basescanner imports >>
import leo.core.leoGlobals as g
if g.isPython3:
    import io
    StringIO = io.StringIO
else:
    import StringIO
    StringIO = StringIO.StringIO
import re
import time
#@-<< basescanner imports >>
#@+<< basescanner switches >>
#@+node:ekr.20161104071309.1: ** << basescanner switches >>
gen_v2 = g.gen_v2
new_ctors = False
    # Fails at present.
#@-<< basescanner switches >>
#@+others
#@+node:ekr.20161027114701.1: ** class BaseScanner
class BaseScanner(object):
    '''The base class for all legacy (character-oriented) scanner classes.'''

    #@+others
    #@+node:ekr.20140727075002.18188: *3* BaseScanner.ctor
    def __init__(self, importCommands, atAuto, language='unnamed', alternate_language=None):
        '''ctor for BaseScanner.'''
        ic = importCommands
        self.atAuto = atAuto
        self.c = c = ic.c
        self.atAutoWarnsAboutLeadingWhitespace = c.config.getBool(
            'at_auto_warns_about_leading_whitespace')
        self.atAutoSeparateNonDefNodes = c.config.getBool(
            'at_auto_separate_non_DefNodes', default=False)
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
        delim1, junk, junk = g.set_delims_from_language(language)
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
        self.hasRegex = False
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
    #@+node:ekr.20140727075002.18189: *3* BaseScanner.Checking
    #@+node:ekr.20140727075002.18190: *4* BaseScanner.check
    def check(self, unused_s, unused_parent):
        '''Make sure the generated nodes are equivalent to the original file.

        1. Regularize and check leading whitespace.
        2. Check that a trial write produces the original file.

        Return True if the nodes are equivalent to the original file.
        '''
        # Note: running full checks on all unit tests is slow.
        if g.app.suppressImportChecks:
            return True
        if (g.unitTesting or self.fullChecks) and self.treeType in (None, '@file'):
            return self.checkTrialWrite()
        else:
            return True
    #@+node:ekr.20140727075002.18191: *4* BaseScanner.checkLeadingWhitespace
    def checkLeadingWhitespace(self, line):
        tab_width = self.tab_width
        lws = line[0: g.skip_ws(line, 0)]
        w = g.computeWidth(lws, tab_width)
        ok = (w % abs(tab_width)) == 0
        if not ok:
            self.report('leading whitespace not consistent with @tabwidth %d' % tab_width)
            g.error('line:', repr(line))
        return ok
    #@+node:ekr.20140727075002.18192: *4* BaseScanner.checkTrialWrite
    def checkTrialWrite(self, s1=None, s2=None):
        '''Return True if a trial write produces the original file.'''
        # s1 and s2 are for unit testing.
        trace = False # and not g.unitTesting
        trace_code = True
        trace_time = False and not g.unitTesting
        if trace_time:
            t1 = time.clock()
        c, at = self.c, self.c.atFileCommands
        if trace: g.trace(s1 and len(s1), s2 and len(s2))
        if s1 is None and s2 is None:
            if self.isRst:
                outputFile = StringIO()
                c.rstCommands.writeAtAutoFile(self.root, self.fileName, outputFile, trialWrite=True)
                s1, s2 = self.file_s, outputFile.getvalue()
                s1, s2 = self.stripRstLines(s1), self.stripRstLines(s2)
                # if g.unitTesting: g.pdb()
            elif self.atAuto:
                # Special case for @auto.
                at.writeOneAtAutoNode(self.root, toString=True, force=True, trialWrite=True)
                s1, s2 = self.file_s, at.stringOutput
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
                s1, s2 = self.file_s, at.stringOutput
                # Now remove sentinels from s2.
                line_delim = self.lineCommentDelim or self.lineCommentDelim2 or ''
                start_delim = self.blockCommentDelim1 or self.blockCommentDelim2 or ''
                # g.trace(self.language,line_delim,start_delim)
                assert line_delim or start_delim
                s2 = self.importCommands.removeSentinelLines(s2,
                    line_delim, start_delim, unused_end_delim=None)
        s1 = g.toUnicode(s1, self.encoding)
        s2 = g.toUnicode(s2, self.encoding)
        # Make sure we have a trailing newline in both strings.
        s1 = s1.replace('\r', '')
        s2 = s2.replace('\r', '')
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
            bad_i1, bad_i2, ok = self.scanAndCompare(s1, s2)
            if ok:
                if trace_time: g.trace(g.timeSince(t1))
                return ok
        else: # Line-based comparison: can not possibly work for html.
            n1, n2 = len(lines1), len(lines2)
            ok = True; bad_i1, bad_i2 = 0, 0
            for i in range(max(n1, n2)):
                ok = self.compareHelper(lines1, lines2, i, self.strict)
                if not ok:
                    bad_i1, bad_i2 = i, i # bug fix: 2016/05/19.
                    break
        # Unit tests do not generate errors unless the mismatch line does not match.
        if g.app.unitTesting:
            d = g.app.unitTestDict
            ok = d.get('expectedMismatchLine') == bad_i1
            if not ok: d['fail'] = g.callers()
        if trace or not ok:
            lines1 = g.splitLines(s1)
            lines2 = g.splitLines(s2)
            self.reportMismatch(lines1, lines2, bad_i1, bad_i2)
        if trace_time: g.trace(g.timeSince(t1))
        return ok
    #@+node:ekr.20140727075002.18193: *4* BaseScanner.compareHelper & helpers
    def compareHelper(self, lines1, lines2, i, strict):
        '''
        Compare lines1[i] and lines2[i] on a line-by-line basis.
        strict is True if leading whitespace is very significant.
        '''

        def pr(*args, **keys): #compareHelper
            g.blue(*args, **keys)

        def pr_mismatch(i, line1, line2):
            g.es_print('first mismatched line at line', str(i + 1))
            g.es_print('original line: ', line1)
            g.es_print('generated line:', line2)

        d = g.app.unitTestDict
        expectedMismatch = g.app.unitTesting and d.get('expectedMismatchLine')
        enableWarning = not self.mismatchWarningGiven and self.atAutoWarnsAboutLeadingWhitespace
        messageKind = None
        if i >= len(lines1):
            if i != expectedMismatch or not g.unitTesting:
                pr('extra lines')
                for line in lines2[i:]:
                    pr(repr(line))
            d['actualMismatchLine'] = i
            return False
        if i >= len(lines2):
            if i != expectedMismatch or not g.unitTesting:
                g.es_print('missing lines')
                for line in lines2[i:]:
                    g.es_print('', repr(line))
            d['actualMismatchLine'] = i
            return False
        line1, line2 = lines1[i], lines2[i]
        if line1 == line2:
            return True # An exact match.
        elif not line1.strip() and not line2.strip():
            return True # Blank lines compare equal.
        elif self.isRst and self.compareRstUnderlines(line1, line2):
            return True
        elif strict:
            s1, s2 = line1.lstrip(), line2.lstrip()
            messageKind = 'comment' if s1 == s2 and self.startsComment(s1, 0) and self.startsComment(s2, 0) else 'error'
        else:
            s1, s2 = line1.lstrip(), line2.lstrip()
            messageKind = 'warning' if s1 == s2 else 'error'
        if g.unitTesting:
            d['actualMismatchLine'] = i + 1
            ok = i + 1 == expectedMismatch
            if not ok: pr_mismatch(i, line1, line2)
            return ok
        elif strict:
            if enableWarning:
                self.mismatchWarningGiven = True
                if messageKind == 'comment':
                    self.warning('mismatch in leading whitespace before comment')
                else:
                    self.error('mismatch in leading whitespace')
                pr_mismatch(i, line1, line2)
            return messageKind == 'comment' # Only mismatched comment lines are valid.
        else:
            if enableWarning:
                self.mismatchWarningGiven = True
                self.checkLeadingWhitespace(line1)
                self.warning('mismatch in leading whitespace')
                pr_mismatch(i, line1, line2)
            return messageKind in ('comment', 'warning') # Only errors are invalid.
    #@+node:ekr.20140727075002.18194: *5* BaseScanner.adjustTestLines
    def adjustTestLines(self, lines):
        '''
        Ignore blank lines and trailing whitespace.

        This fudge allows the rst code generators to insert needed newlines freely.
        '''
        if self.ignoreBlankLines:
            lines = [z for z in lines if z.strip()]
        if self.ignoreLeadingWs:
            lines = [z.lstrip() for z in lines]
        # New in Leo 5.0.
        lines = [z.rstrip() + '\n' if z.endswith('\n') else z.rstrip() for z in lines]
        return lines
    #@+node:ekr.20140727075002.18195: *5* BaseScanner.compareRstUnderlines
    def compareRstUnderlines(self, s1, s2):
        s1, s2 = s1.rstrip(), s2.rstrip()
        if s1 == s2:
            return True # Don't worry about trailing whitespace.
        n1, n2 = len(s1), len(s2)
        ch1 = n1 and s1[0] or ''
        ch2 = n2 and s2[0] or ''
        val = (
            n1 >= 2 and n2 >= 2 and # Underlinings must be at least 2 long.
            ch1 == ch2 and # The underlining characters must match.
            s1 == ch1 * n1 and # The line must consist only of underlining characters.
            s2 == ch2 * n2)
        return val
    #@+node:ekr.20140727075002.18196: *4* BaseScanner.formatTokens
    def formatTokens(self, tokens):
        '''Format tokens for printing or dumping.'''
        i, result = 0, []
        for kind, val, line_number in tokens:
            s = '%3s %3s %6s %s' % (i, line_number, kind, repr(val))
            result.append(s)
            i += 1
        return '\n'.join(result)
    #@+node:ekr.20140727075002.18197: *4* BaseScanner.reportMismatch
    def reportMismatch(self, lines1, lines2, bad_i1, bad_i2):
        # g.trace('**',bad_i1,bad_i2,g.callers())
        trace = False # This causes traces for *non-failing* unit tests.
        if trace and False and len(lines1) < 100:
            g.trace('lines1...\n', ''.join(lines1), '\n')
            g.trace('lines2...\n', ''.join(lines2), '\n')
            return
        kind = '@auto' if self.atAuto else 'import command'
        n1, n2 = len(lines1), len(lines2)
        s1 = '%s did not import %s perfectly\n' % (
            kind, self.root.h)
        s2 = 'The clean-all-lines command may help fix whitespace problems\n'
        s3 = 'first mismatched line: %s (original) = %s (imported)' % (
            bad_i1, bad_i2)
        s = s1 + s2 + s3
        if trace: g.trace(s)
        else: self.error(s)
        aList = []
        aList.append('Original file...\n')
        for i in range(max(0, bad_i1 - 2), min(bad_i1 + 3, n1)):
            line = repr(lines1[i])
            aList.append('%4d %s' % (i, line))
        aList.append('\nImported file...\n')
        for i in range(max(0, bad_i2 - 2), min(bad_i2 + 3, n2)):
            line = repr(lines2[i])
            aList.append('%4d %s' % (i, line))
        if trace or not g.unitTesting:
            g.blue('\n'.join(aList))
        return False
    #@+node:ekr.20140727075002.18198: *4* BaseScanner.scanAndCompare & helpers
    def scanAndCompare(self, s1, s2):
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
            return - 1, -1, True
        else:
            n1, n2 = self.compareTokens(tokens1, tokens2)
            return n1, n2, False
    #@+node:ekr.20140727075002.18199: *5* BaseScanner.compareTokens
    def compareTokens(self, tokens1, tokens2):
        trace = False # and not g.unitTesting
        verbose = True
        i, n1, n2 = 0, len(tokens1), len(tokens2)
        fail_n1, fail_n2 = -1, -1
        while i < max(n1, n2):
            if trace and verbose:
                for n, tokens in ((n1, tokens1), (n2, tokens2),):
                    if i < n: kind, val, line_number = tokens[i]
                    else: kind, val, line_number = 'eof', '', ''
                    try:
                        print('%3s %3s %7s' % (i, line_number, kind), repr(val)[: 40])
                    except UnicodeEncodeError:
                        print('%3s %3s %7s' % (i, line_number, kind), 'unicode error!')
                        # print(val)
            if i < n1: kind1, val1, tok_n1 = tokens1[i]
            else: kind1, val1, tok_n1 = 'eof', '', n1
            if i < n2: kind2, val2, tok_n2 = tokens2[i]
            else: kind2, val2, tok_n2 = 'eof', '', n2
            if fail_n1 == -1 and fail_n2 == -1 and (kind1 != kind2 or val1 != val2):
                if trace: g.trace('fail at lines: %s,%s' % (tok_n1, tok_n2))
                fail_n1, fail_n2 = tok_n1, tok_n2 # Bug fix: 2013/09/08.
                if trace:
                    print('------ Failure ----- i: %s n1: %s n2: %s' % (i, n1, n2))
                    print('tok_n1: %s tok_n2: %s' % (tok_n1, tok_n2))
                    print('kind1: %s kind2: %s\nval1: %s\nval2: %s' % (
                        kind1, kind2, repr(val1), repr(val2)))
                if trace and verbose:
                    n3 = 0
                    i += 1
                    while n3 < 10 and i < max(n1, n2):
                        for n, tokens in ((n1, tokens1), (n2, tokens2),):
                            if i < n: kind, val, junk_n = tokens[i]
                            else: kind, val = 'eof', ''
                            print('%3s %7s %s' % (i, kind, repr(val)))
                        n3 += 1
                        i += 1
                break
            i += 1
        if fail_n1 > -1 or fail_n2 > -1:
            if trace: g.trace('fail', fail_n1, fail_n2)
            return fail_n1, fail_n2
        elif n1 == n2:
            if trace: g.trace('equal')
            return - 1, -1
        else:
            n = min(len(tokens1), len(tokens2))
            if trace: g.trace('fail 2 at line: %s' % (n))
            return n, n
    #@+node:ekr.20140727075002.18200: *5* BaseScanner.filterTokens & helpers
    def filterTokens(self, tokens):
        '''Filter tokens as needed for correct comparisons.

        May be overridden in subclasses.'''
        return tokens
    #@+node:ekr.20140727075002.18201: *6* BaseScanner.removeLeadingWsTokens
    def removeLeadingWsTokens(self, tokens):
        '''Remove tokens representing leading whitespace.'''
        i, last, result = 0, 'nl', []
        while i < len(tokens):
            progress = i
            kind, val, n = tok = tokens[i]
            if kind == 'ws' and last == 'nl':
                pass
            else:
                result.append(tok)
            i += 1
            last = kind
            assert progress + 1 == i
        return result
    #@+node:ekr.20140727075002.18202: *6* BaseScanner.removeBlankLinesTokens
    def removeBlankLinesTokens(self, tokens):
        '''Remove all tokens representing blank lines.'''
        trace = False
        if trace: g.trace('\nbefore:', tokens)
        i, last, lws, result = 0, 'nl', [], []
        while i < len(tokens):
            progress = i
            kind, val, n = tok = tokens[i]
            if kind == 'ws':
                if last in ('nl', 'ws'):
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
            assert i == progress + 1
        # Add any remaining ws.
        if lws: result.extend(lws)
        if trace: g.trace('\nafter: ', result)
        return result
    #@+node:ekr.20161006165248.1: *4* BaseScanner.clean_* & strip_*
    def clean_blank_lines(self, s):
        '''Remove all blanks and tabs in all blank lines.'''
        result = ''.join([
            z if z.strip() else z.replace(' ','').replace('\t','')
                for z in g.splitLines(s)
        ])
        return result

    def strip_all(self, s):
        '''Strip blank lines and leading whitespace from all lines of s.'''
        return self.strip_lws(self.strip_blank_lines(s))

    def strip_blank_lines(self, s):
        '''Strip all blank lines from s.'''
        return ''.join([z for z in g.splitLines(s) if z.strip()])

    def strip_lws(self, s):
        '''Strip leading whitespace from all lines of s.'''
        return ''.join([z.lstrip() for z in g.splitLines(s)])
    #@+node:ekr.20140727075002.18203: *4* BaseScanner.stripTokens
    def stripTokens(self, tokens):
        '''Remove the line_number from all tokens.'''
        return [(kind, val) for(kind, val, line_number) in tokens]
    #@+node:ekr.20140727075002.18204: *4* BaseScanner.stripRstLines
    def stripRstLines(self, s):
        '''Replace rst under/overlines with a dummy line for comparison.'''

        def mungeRstLine(s):
            '''Return a dummy under/over line for rst under/overlines.'''
            if len(s) < 4: return s
            nl = '\n' if s[-1] == '\n' else ''
            ch1 = s[0]
            dummy_line = (ch1 * 10) + nl
            s = s.rstrip() + nl
            if ch1.isalnum(): return s
            for ch in s.rstrip():
                if ch == '\n': return dummy_line
                if ch != ch1: return s
            return dummy_line

        return ''.join([mungeRstLine(z) for z in g.splitLines(s)])
    #@+node:ekr.20140727075002.18205: *3* BaseScanner.Code generation
    #@+node:ekr.20140727075002.18206: *4* BaseScanner.adjustParent
    def adjustParent(self, parent, headline):
        '''Return the effective parent.

        This is overridden by the RstScanner class.'''
        return parent
    #@+node:ekr.20140727075002.18207: *4* BaseScanner.addRef
    def addRef(self, parent):
        '''Create an unindented @others or section reference in the parent node.'''
        if self.isRst and not self.atAuto:
            return
        if self.treeType in ('@clean', '@file', '@nosent', None):
            self.appendStringToBody(parent, '@others\n')
        if self.treeType == '@root' and self.methodsSeen:
            self.appendStringToBody(parent,
                g.angleBrackets(' ' + self.methodName + ' methods ') + '\n\n')
    #@+node:ekr.20140727075002.18208: *4* BaseScanner.appendStringToBody & setBodyString
    def appendStringToBody(self, p, s):
        '''Similar to c.appendStringToBody,
        but does not recolor the text or redraw the screen.'''
        return self.importCommands.appendStringToBody(p, s)

    def setBodyString(self, p, s):
        '''Similar to c.setBodyString,
        but does not recolor the text or redraw the screen.'''
        return self.importCommands.setBodyString(p, s)
    #@+node:ekr.20140727075002.18209: *4* BaseScanner.computeBody
    def computeBody(self, s, start, sigStart, codeEnd):
        '''Return the head and tail of the body.'''
        trace = False
        body1 = s[start: sigStart]
        # Adjust start backwards to get a better undent.
        if body1.strip():
            while start > 0 and s[start - 1] in (' ', '\t'):
                start -= 1
        # g.trace(repr(s[sigStart:codeEnd]))
        body1 = self.undentBody(s[start: sigStart], ignoreComments=False)
        body2 = self.undentBody(s[sigStart: codeEnd])
        body = body1 + body2
        if trace: g.trace('body: %s' % repr(body))
        tail = body[len(body.rstrip()):]
        if '\n' not in tail:
            self.warning(
                '%s %s does not end with a newline; one will be added\n%s' % (
                self.functionSpelling, self.sigId, g.get_line(s, codeEnd)))
        return body1, body2
    #@+node:ekr.20140727075002.18210: *4* BaseScanner.createDeclsNode
    def createDeclsNode(self, parent, s):
        '''Create a child node of parent containing s.'''
        # Create the node for the decls.
        headline = '%s declarations' % self.methodName
        body = self.undentBody(s)
        self.createHeadline(parent, body, headline)
    #@+node:ekr.20140727075002.18211: *4* BaseScanner.createFunctionNode
    def createFunctionNode(self, headline, body, parent):
        # Create the prefix line for @root trees.
        if self.treeType == '@root':
            prefix = g.angleBrackets(' ' + headline + ' methods ') + '=\n\n'
            self.methodsSeen = True
        else:
            prefix = ''
        # Create the node.
        return self.createHeadline(parent, prefix + body, headline)
    #@+node:ekr.20140727075002.18212: *4* BaseScanner.createHeadline
    def createHeadline(self, parent, body, headline):
        return self.importCommands.createHeadline(parent, body, headline)
    #@+node:ekr.20140727075002.18213: *4* BaseScanner.endGen
    def endGen(self, s):
        '''Do any language-specific post-processing.'''
        pass
    #@+node:ekr.20140727075002.18214: *4* BaseScanner.getLeadingIndent
    def getLeadingIndent(self, s, i, ignoreComments=True):
        '''Return the leading whitespace of a line.
        Ignore blank and comment lines if ignoreComments is True'''
        width = 0
        i = g.find_line_start(s, i)
        if ignoreComments:
            while i < len(s):
                # g.trace(g.get_line(s,i))
                j = g.skip_ws(s, i)
                if g.is_nl(s, j) or g.match(s, j, self.comment_delim):
                    i = g.skip_line(s, i) # ignore blank lines and comment lines.
                else:
                    i, width = g.skip_leading_ws_with_indent(s, i, self.tab_width)
                    break
        else:
            i, width = g.skip_leading_ws_with_indent(s, i, self.tab_width)
        # g.trace('returns:',width)
        return width
    #@+node:ekr.20140727075002.18215: *4* BaseScanner.indentBody
    def indentBody(self, s, lws=None):
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
    #@+node:ekr.20140727075002.18216: *4* BaseScanner.insertIgnoreDirective
    def insertIgnoreDirective(self, parent):
        c = self.c
        self.appendStringToBody(parent, '@ignore')
        if g.unitTesting:
            g.app.unitTestDict['fail'] = g.callers()
        else:
            if parent.isAnyAtFileNode() and not parent.isAtAutoNode():
                g.warning('inserting @ignore')
                c.import_error_nodes.append(parent.h)
    #@+node:ekr.20140727075002.18217: *4* BaseScanner.putClass & helpers
    def putClass(self, s, i, sigEnd, codeEnd, start, parent):
        '''Creates a child node c of parent for the class,
        and a child of c for each def in the class.'''
        trace = False
        if trace:
            # g.trace('tab_width',self.tab_width)
            g.trace('sig', repr(s[i: sigEnd]))
        # Enter a new class 1: save the old class info.
        oldMethodName = self.methodName
        oldStartSigIndent = self.startSigIndent
        # Enter a new class 2: init the new class info.
        self.indentRefFlag = None
        class_kind = self.classId
        class_name = self.sigId
        headline = '%s %s' % (class_kind, class_name)
        headline = headline.strip()
        self.methodName = headline
        # Compute the starting lines of the class.
        prefix = self.createClassNodePrefix()
        if not self.sigId:
            g.trace('Can not happen: no sigId')
            self.sigId = 'Unknown class name'
        classHead = s[start: sigEnd]
        i = self.extendSignature(s, sigEnd)
        extend = s[sigEnd: i]
        if extend:
            classHead = classHead + extend
        # Create the class node.
        class_node = self.createHeadline(parent, '', headline)
        # Remember the indentation of the class line.
        undentVal = self.getLeadingIndent(classHead, 0)
        # Call the helper to parse the inner part of the class.
        putRef, bodyIndent, classDelim, decls, trailing = self.putClassHelper(
            s, i, codeEnd, class_node)
        # g.trace('bodyIndent',bodyIndent,'undentVal',undentVal)
        # Set the body of the class node.
        ref = putRef and self.getClassNodeRef(class_name) or ''
        if trace: g.trace('undentVal', undentVal, 'bodyIndent', bodyIndent)
        # Give ref the same indentation as the body of the class.
        if ref:
            bodyWs = g.computeLeadingWhitespace(bodyIndent, self.tab_width)
            ref = '%s%s' % (bodyWs, ref)
        # Remove the leading whitespace.
        result = (
            prefix +
            self.undentBy(classHead, undentVal) +
            self.undentBy(classDelim, undentVal) +
            self.undentBy(decls, undentVal) +
            self.undentBy(ref, undentVal) +
            self.undentBy(trailing, undentVal))
        result = self.adjust_class_ref(result)
        # Append the result to the class node.
        self.appendTextToClassNode(class_node, result)
        # Exit the new class: restore the previous class info.
        self.methodName = oldMethodName
        self.startSigIndent = oldStartSigIndent
    #@+node:ekr.20140727075002.18218: *5* BaseScanner.adjust_class_ref
    def adjust_class_ref(self, s):
        '''Over-ridden by xml and html scanners.'''
        return s
    #@+node:ekr.20140727075002.18219: *5* BaseScanner.appendTextToClassNode
    def appendTextToClassNode(self, class_node, s):
        self.appendStringToBody(class_node, s)
    #@+node:ekr.20140727075002.18220: *5* BaseScanner.createClassNodePrefix
    def createClassNodePrefix(self):
        '''Create the class node prefix.'''
        if self.treeType == '@root':
            prefix = g.angleBrackets(' ' + self.methodName + ' methods ') + '=\n\n'
            self.methodsSeen = True
        else:
            prefix = ''
        return prefix
    #@+node:ekr.20140727075002.18221: *5* BaseScanner.getClassNodeRef
    def getClassNodeRef(self, class_name):
        '''Insert the proper body text in the class_vnode.'''
        if self.treeType in ('@clean', '@file', '@nosent', None):
            s = '@others'
        else:
            s = g.angleBrackets(' class %s methods ' % (class_name))
        return '%s\n' % (s)
    #@+node:ekr.20140727075002.18222: *5* BaseScanner.putClassHelper
    def putClassHelper(self, s, i, end, class_node):
        '''s contains the body of a class, not including the signature.

        Parse s for inner methods and classes, and create nodes.'''
        trace = False and not g.unitTesting
        # Increase the output indentation (used only in startsHelper).
        # This allows us to detect over-indented classes and functions.
        old_output_indent = self.output_indent
        self.output_indent += abs(self.tab_width)
        # Parse the decls.
        if self.hasDecls: # 2011/11/11
            j = i; i = self.skipDecls(s, i, end, inClass=True)
            decls = s[j: i]
        else:
            decls = ''
        # Set the body indent if there are real decls.
        bodyIndent = decls.strip() and self.getIndent(s, i) or None
        if trace: g.trace('bodyIndent', bodyIndent)
        # Parse the rest of the class.
        delim1, delim2 = self.outerBlockDelim1, self.outerBlockDelim2
        if g.match(s, i, delim1):
            # Do *not* use g.skip_ws_and_nl here!
            j = g.skip_ws(s, i + len(delim1))
            if g.is_nl(s, j): j = g.skip_nl(s, j)
            classDelim = s[i: j]
            end2 = self.skipBlock(s, i, delim1=delim1, delim2=delim2)
            start, putRef, bodyIndent2 = self.scanHelper(s, j, end=end2, parent=class_node, kind='class')
        else:
            classDelim = ''
            start, putRef, bodyIndent2 = self.scanHelper(s, i, end=end, parent=class_node, kind='class')
        if bodyIndent is None: bodyIndent = bodyIndent2
        # Restore the output indentation.
        self.output_indent = old_output_indent
        # Return the results.
        trailing = s[start: end]
        return putRef, bodyIndent, classDelim, decls, trailing
    #@+node:ekr.20140727075002.18223: *4* BaseScanner.putFunction
    def putFunction(self, s, sigStart, codeEnd, start, parent):
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
    #@+node:ekr.20140727075002.18224: *4* BaseScanner.putRootText
    def putRootText(self, p):
        self.appendStringToBody(p, '%s@language %s\n@tabwidth %d\n' % (
            self.rootLine, self.alternate_language or self.language, self.tab_width))
    #@+node:ekr.20140727075002.18225: *4* BaseScanner.undentBody
    def undentBody(self, s, ignoreComments=True):
        '''Remove the first line's leading indentation from all lines of s.'''
        trace = False and not g.unitTesting
        verbose = False
        if trace and verbose: g.trace('before...\n', g.listToString(g.splitLines(s)))
        if self.isRst:
            return s # Never unindent rst code.
        # Calculate the amount to be removed from each line.
        undentVal = self.getLeadingIndent(s, 0, ignoreComments=ignoreComments)
        if trace: g.trace(undentVal, g.splitLines(s)[0].rstrip())
        if undentVal == 0:
            return s
        else:
            result = self.undentBy(s, undentVal)
            if trace and verbose: g.trace('after...\n', g.listToString(g.splitLines(result)))
            return result
    #@+node:ekr.20140727075002.18226: *4* BaseScanner.undentBy
    def undentBy(self, s, undentVal):
        '''Remove leading whitespace equivalent to undentVal from each line.
        For strict languages, add an underindentEscapeString for underindented line.'''
        trace = False and not g.app.unitTesting
        if self.isRst:
            return s # Never unindent rst code.
        tag = self.c.atFileCommands.underindentEscapeString
        result = []; tab_width = self.tab_width
        for line in g.splitlines(s):
            lws_s = g.get_leading_ws(line)
            lws = g.computeWidth(lws_s, tab_width)
            s = g.removeLeadingWhitespace(line, undentVal, tab_width)
            # 2011/10/29: Add underindentEscapeString only for strict languages.
            if self.strict and s.strip() and lws < undentVal:
                if trace: g.trace('undentVal: %s, lws: %s, %s' % (
                    undentVal, lws, repr(line)))
                # Bug fix 2012/06/05: end the underindent count with a period,
                # to protect against lines that start with a digit!
                result.append("%s%s.%s" % (tag, undentVal - lws, s.lstrip()))
            else:
                if trace: g.trace(repr(s))
                result.append(s)
        return ''.join(result)
    #@+node:ekr.20140727075002.18227: *4* BaseScanner.underindentedComment & underindentedLine
    def underindentedComment(self, line):
        if self.atAutoWarnsAboutLeadingWhitespace:
            self.warning(
                'underindented python comments.\nExtra leading whitespace will be added\n' + line)

    def underindentedLine(self, line):
        if self.warnAboutUnderindentedLines:
            self.error(
                'underindented line.\n' +
                'Extra leading whitespace will be added\n' + line)
    #@+node:ekr.20140727075002.18228: *3* BaseScanner.error, oops, report and warning
    def error(self, s):
        self.errors += 1
        self.importCommands.errors += 1
        if g.unitTesting:
            if self.errors == 1:
                g.app.unitTestDict['actualErrorMessage'] = s
            g.app.unitTestDict['actualErrors'] = self.errors
            if 0: # For debugging unit tests.
                g.trace(g.callers())
                g.error('', s)
        else:
            g.error('Error:', s)

    def oops(self):
        g.pr('BaseScanner oops: %s must be overridden in subclass' % g.callers())

    def report(self, message):
        if self.strict: self.error(message)
        else: self.warning(message)

    def warning(self, s):
        if not g.unitTesting:
            g.warning('Warning:', s)
    #@+node:ekr.20140727075002.18229: *3* BaseScanner.headlineForNode
    def headlineForNode(self, fn, p):
        '''Return the expected imported headline for p.b'''
        trace = False and not g.unitTesting
        # From scan: parse the decls.s
        s = p.b
        if False: # and self.n_decls == 0 and self.hasDecls:
            i = self.skipDecls(s, 0, len(s), inClass=False)
            decls = s[: i]
            if decls:
                self.n_decls += 1
                val = '%s declarations' % fn
                if trace and val != p.h: g.trace(p.h, '==>', val)
                return val
        # From scanHelper: look for the first def or class.
        i = 0
        while i < len(s):
            progress = i
            if s[i] in (' ', '\t', '\n'):
                i += 1 # Prevent lookahead below, and speed up the scan.
            elif self.startsComment(s, i):
                i = self.skipComment(s, i)
            elif self.startsString(s, i):
                i = self.skipString(s, i)
            elif self.startsClass(s, i):
                val = 'class ' + self.sigId
                if trace and val != p.h: g.trace(p.h, '==>', val)
                return val
            elif self.startsFunction(s, i):
                val = self.sigId
                if trace and val != p.h: g.trace(p.h, '==>', val)
                return val
            elif self.startsId(s, i):
                i = self.skipId(s, i)
            elif g.match(s, i, self.outerBlockDelim1): # and kind == 'outer'
                # Do this after testing for classes.
                i = self.skipBlock(s, i, delim1=self.outerBlockDelim1, delim2=self.outerBlockDelim2)
            else: i += 1
            if progress >= i:
                i = self.skipBlock(s, i, delim1=self.outerBlockDelim1, delim2=self.outerBlockDelim2)
            assert progress < i, 'i: %d, ch: %s' % (i, repr(s[i]))
        return p.h
    #@+node:ekr.20140727075002.18230: *3* BaseScanner.Parsing
    #@+at Scan and skipDecls would typically not be overridden.
    #@+node:ekr.20140727075002.18231: *4* BaseScanner.adjustDefStart
    def adjustDefStart(self, unused_s, i):
        '''A hook to allow the Python importer to adjust the
        start of a class or function to include decorators.'''
        return i
    #@+node:ekr.20140727075002.18232: *4* BaseScanner.extendSignature
    def extendSignature(self, unused_s, i):
        '''Extend the signature line if appropriate.
        The text *must* end with a newline.

        For example, the Python scanner appends docstrings if they exist.'''
        return i
    #@+node:ekr.20140727075002.18233: *4* BaseScanner.getIndent
    def getIndent(self, s, i):
        j, junk = g.getLine(s, i)
        junk, indent = g.skip_leading_ws_with_indent(s, j, self.tab_width)
        return indent
    #@+node:ekr.20140727075002.18234: *4* BaseScanner.prepass & helper
    def prepass(self, s, p):
        '''
        A prepass for the at-file-to-at-auto command.
        Return (ok,aList)
        ok: False if p.b should be split two or more sibling nodes.
        aList: a list of tuples (i,j,headline,p) indicating split nodes.
        '''
        trace = False and not g.unitTesting
        # From scanHelper...
        delim1, delim2 = self.outerBlockDelim1, self.outerBlockDelim2
        p = p.copy()
        classSeen, refSeen = False, False
        i, n, parts, start = 0, 0, [], 0
        while i < len(s):
            progress = i
            if s[i] in (' ', '\t', '\n'):
                i += 1 # Prevent lookahead below, and speed up the scan.
            elif self.startsComment(s, i):
                i = self.skipComment(s, i)
            elif self.startsString(s, i):
                i = self.skipString(s, i)
            elif s[i: i + 2] == '<<':
                j = g.skip_line(s, i + 2)
                k = s.find('>>', i + 2)
                if -1 < k < j:
                    g.trace(s[i: k + 2])
                    refSeen = True
                    i = k + 2
                else:
                    i += 2
            elif self.startsClass(s, i):
                # g.trace('class',i,s[i:i+20])
                # Extend the previous definition.
                if n > 0 and start < i:
                    i1, i2, id2, p2 = parts.pop()
                    parts.append((i1, i, id2, p2),)
                classSeen = True
                start, i = i, self.codeEnd
                parts.append((start, i, self.sigId, p),)
                n += 1
            elif self.startsFunction(s, i):
                # g.trace('func',i,s[i:i+20])
                # Extend the previous definition.
                if n > 0 and start < i:
                    i1, i2, id2, p2 = parts.pop()
                    parts.append((i1, i, id2, p2),)
                start, i = i, self.codeEnd
                parts.append((start, i, self.sigId, p),)
                n += 1
            elif self.startsId(s, i):
                i = self.skipId(s, i)
            elif g.match(s, i, delim1):
                # Do this after testing for classes.
                i = self.skipBlock(s, i, delim1, delim2)
            else:
                i += 1
            if progress >= i:
                i = self.skipBlock(s, i, delim1, delim2)
            assert progress < i, 'i: %d, ch: %s' % (i, repr(s[i]))
        if n > 0 and start < i:
            i1, i2, id2, p2 = parts.pop()
            parts.append((i1, len(s), id2, p2),)
        if n <= 1 and not refSeen:
            return True, [] # Only one definition.
        elif p.hasChildren() or classSeen or refSeen:
            # Can't split safely.
            if trace: g.trace('can not split\n', ''.join([
                '\n----- %s\n%s\n' % (z[2], s[z[0]: z[1]]) for z in parts]))
            return False, []
        else:
            # Multiple defs, no children. Will split the node into children.
            return False, parts
    #@+node:ekr.20140727075002.18235: *4* BaseScanner.scan & scanHelper
    def scan(self, s, parent, parse_body=False):
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
            i = self.skipDecls(s, 0, len(s), inClass=False)
            decls = s[: i]
        else:
            i, decls = 0, ''
        # Create the decls node.
        if decls: self.createDeclsNode(parent, decls)
        # Scan the rest of the file.
        start, junk, junk = self.scanHelper(s, i, end=len(s), parent=parent, kind='outer')
        # Finish adding to the parent's body text.
        self.addRef(parent)
        if start < len(s):
            self.appendStringToBody(parent, s[start:])
        # Do any language-specific post-processing.
        self.endGen(s)
    #@+node:ekr.20140727075002.18236: *5* BaseScanner.scanHelper
    def scanHelper(self, s, i, end, parent, kind):
        '''Common scanning code used by both scan and putClassHelper.'''
        # g.trace(g.callers())
        # g.trace('i',i,g.get_line(s,i))
        assert kind in ('class', 'outer')
        start = i; putRef = False; bodyIndent = None
        # Major change: 2011/11/11: prevent scanners from going beyond end.
        if self.hasNestedClasses and end < len(s):
            s = s[: end] # Potentially expensive, but unavoidable.
        # if g.unitTesting: g.pdb()
        while i < end:
            progress = i
            if s[i] in (' ', '\t', '\n'):
                i += 1 # Prevent lookahead below, and speed up the scan.
            elif self.startsComment(s, i):
                i = self.skipComment(s, i)
            elif self.startsString(s, i):
                i = self.skipString(s, i)
            elif self.hasRegex and self.startsRegex(s, i):
                i = self.skipRegex(s, i)
            elif self.startsClass(s, i): # Sets sigStart,sigEnd & codeEnd ivars.
                putRef = True
                if bodyIndent is None: bodyIndent = self.getIndent(s, i)
                end2 = self.codeEnd # putClass may change codeEnd ivar.
                self.putClass(s, i, self.sigEnd, self.codeEnd, start, parent)
                i = start = end2
            elif self.startsFunction(s, i): # Sets sigStart,sigEnd & codeEnd ivars.
                putRef = True
                if bodyIndent is None: bodyIndent = self.getIndent(s, i)
                self.putFunction(s, self.sigStart, self.codeEnd, start, parent)
                i = start = self.codeEnd
            elif self.startsId(s, i):
                i = self.skipId(s, i)
            elif kind == 'outer' and g.match(s, i, self.outerBlockDelim1): # Do this after testing for classes.
                # i1 = i # for debugging
                i = self.skipBlock(s, i, delim1=self.outerBlockDelim1, delim2=self.outerBlockDelim2)
                # Bug fix: 2007/11/8: do *not* set start: we are just skipping the block.
            else: i += 1
            if progress >= i:
                # g.pdb()
                i = self.skipBlock(s, i, delim1=self.outerBlockDelim1, delim2=self.outerBlockDelim2)
            assert progress < i, 'i: %d, ch: %s' % (i, repr(s[i]))
        return start, putRef, bodyIndent
    #@+node:ekr.20140727075002.18237: *4* BaseScanner.Parser skip methods
    #@+node:ekr.20140727075002.18238: *5* BaseScanner.isSpace
    def isSpace(self, s, i):
        '''Return true if s[i] is a tokenizer space.'''
        # g.trace(repr(s[i]),i < len(s) and s[i] != '\n' and s[i].isspace())
        return i < len(s) and s[i] != '\n' and s[i].isspace()
    #@+node:ekr.20140727075002.18239: *5* BaseScanner.skipArgs
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
    #@+node:ekr.20140727075002.18240: *5* BaseScanner.skipBlock
    def skipBlock(self, s, i, delim1=None, delim2=None):
        '''Skip from the opening delim to *past* the matching closing delim.

        If no matching is found i is set to len(s)'''
        trace = False and not g.unitTesting
        verbose = False
        if delim1 is None: delim1 = self.blockDelim1
        if delim2 is None: delim2 = self.blockDelim2
        match1 = g.match if len(delim1) == 1 else g.match_word
        match2 = g.match if len(delim2) == 1 else g.match_word
        assert match1(s, i, delim1)
        level, start, startIndent = 0, i, self.startSigIndent
        if trace and verbose:
            g.trace('***', 'startIndent', startIndent)
        while i < len(s):
            progress = i
            if g.is_nl(s, i):
                backslashNewline = i > 0 and g.match(s, i - 1, '\\\n')
                i = g.skip_nl(s, i)
                if not backslashNewline and not g.is_nl(s, i):
                    j, indent = g.skip_leading_ws_with_indent(s, i, self.tab_width)
                    line = g.get_line(s, j)
                    if trace and verbose: g.trace('indent', indent, line)
                    if indent < startIndent and line.strip():
                        # An non-empty underindented line.
                        # Issue an error unless it contains just the closing bracket.
                        if level == 1 and match2(s, j, delim2):
                            pass
                        else:
                            if j not in self.errorLines: # No error yet given.
                                self.errorLines.append(j)
                                self.underindentedLine(line)
            elif s[i] in (' ', '\t',):
                i += 1 # speed up the scan.
            elif self.startsComment(s, i):
                i = self.skipComment(s, i)
            elif self.startsString(s, i):
                i = self.skipString(s, i)
            elif match1(s, i, delim1):
                level += 1; i += len(delim1)
            elif match2(s, i, delim2):
                level -= 1; i += len(delim2)
                # Skip junk following Pascal 'end'
                for z in self.blockDelim2Cruft:
                    i2 = self.skipWs(s, i)
                    if g.match(s, i2, z):
                        i = i2 + len(z)
                        break
                if level <= 0:
                    # 2010/09/20
                    # Skip a single-line comment if it exists.
                    j = self.skipWs(s, i)
                    if (g.match(s, j, self.lineCommentDelim) or
                        g.match(s, j, self.lineCommentDelim2)
                    ):
                        i = g.skip_to_end_of_line(s, i)
                    if trace: g.trace('returns:\n\n%s\n\n' % s[start: i])
                    return i
            else: i += 1
            assert progress < i
        self.error('no block: %s' % self.root.h)
        if 1:
            i, j = g.getLine(s, start)
            g.trace(i, s[i: j])
        else:
            if trace: g.trace('** no block')
        return start + 1 # 2012/04/04: Ensure progress in caller.
    #@+node:ekr.20140727075002.18241: *5* BaseScanner.skipCodeBlock
    def skipCodeBlock(self, s, i, kind):
        '''Skip the code block in a function or class definition.'''
        trace = False
        start = i
        i = self.skipBlock(s, i, delim1=None, delim2=None)
        if self.sigFailTokens:
            i = self.skipWs(s, i)
            for z in self.sigFailTokens:
                if g.match(s, i, z):
                    if trace: g.trace('failtoken', z)
                    return start, False
        if i > start:
            i = self.skipNewline(s, i, kind)
        if trace:
            # g.trace(g.callers())
            # g.trace('returns...\n',g.listToString(g.splitLines(s[start:i])))
            g.trace('returns:\n\n%s\n\n' % s[start: i])
        return i, True
    #@+node:ekr.20140727075002.18242: *5* BaseScanner.skipComment & helper
    def skipComment(self, s, i):
        '''Skip a comment and return the index of the following character.'''
        if g.match(s, i, self.lineCommentDelim) or g.match(s, i, self.lineCommentDelim2):
            return g.skip_to_end_of_line(s, i)
        else:
            return self.skipBlockComment(s, i)
    #@+node:ekr.20140727075002.18243: *6* BaseScanner.skipBlockComment
    def skipBlockComment(self, s, i):
        '''Skip past a block comment.'''
        start = i
        # Skip the opening delim.
        if g.match(s, i, self.blockCommentDelim1):
            delim2 = self.blockCommentDelim2
            i += len(self.blockCommentDelim1)
        elif g.match(s, i, self.blockCommentDelim1_2):
            i += len(self.blockCommentDelim1_2)
            delim2 = self.blockCommentDelim2_2
        else:
            assert False
        # Find the closing delim.
        k = s.find(delim2, i)
        if k == -1:
            self.error('Run on block comment: ' + s[start: i])
            return len(s)
        else:
            return k + len(delim2)
    #@+node:ekr.20140727075002.18244: *5* BaseScanner.skipDecls
    def skipDecls(self, s, i, end, inClass):
        '''
        Skip everything until the start of the next class or function.
        The decls *must* end in a newline.
        '''
        trace = False or self.trace
        start = i; prefix = None
        classOrFunc = False
        if trace: g.trace(g.callers())
        # Major change: 2011/11/11: prevent scanners from going beyond end.
        if self.hasNestedClasses and end < len(s):
            s = s[: end] # Potentially expensive, but unavoidable.
        while i < end:
            progress = i
            if s[i] in (' ', '\t', '\n'):
                i += 1 # Prevent lookahead below, and speed up the scan.
            elif self.startsComment(s, i):
                # Add the comment to the decl if it *doesn't* start the line.
                i2, junk = g.getLine(s, i)
                i2 = self.skipWs(s, i2)
                if i2 == i and prefix is None:
                    prefix = i2 # Bug fix: must include leading whitespace in the comment.
                i = self.skipComment(s, i)
            elif self.startsString(s, i):
                i = self.skipString(s, i)
                prefix = None
            elif self.startsClass(s, i):
                # Important: do not include leading ws in the decls.
                classOrFunc = True
                i = g.find_line_start(s, i)
                i = self.adjustDefStart(s, i)
                break
            elif self.startsFunction(s, i):
                # Important: do not include leading ws in the decls.
                classOrFunc = True
                i = g.find_line_start(s, i)
                i = self.adjustDefStart(s, i)
                break
            elif self.startsId(s, i):
                i = self.skipId(s, i)
                prefix = None
            # Don't skip outer blocks: they may contain classes.
            elif g.match(s, i, self.outerBlockDelim1):
                if self.outerBlockEndsDecls:
                    break
                else:
                    i = self.skipBlock(s, i,
                        delim1=self.outerBlockDelim1,
                        delim2=self.outerBlockDelim2)
            else:
                i += 1; prefix = None
            assert(progress < i)
        if prefix is not None:
            i = g.find_line_start(s, prefix) # i = prefix
        decls = s[start: i]
        if inClass and not classOrFunc:
            # Don't return decls if a class contains nothing but decls.
            if trace and decls.strip(): g.trace('**class is all decls...\n', decls)
            return start
        elif decls.strip():
            if trace or self.trace: g.trace('\n' + decls)
            return i
        else: # Ignore empty decls.
            return start
    #@+node:ekr.20140727075002.18245: *5* BaseScanner.skipId
    def skipId(self, s, i):
        return g.skip_id(s, i, chars=self.extraIdChars)
    #@+node:ekr.20140727075002.18246: *5* BaseScanner.skipNewline
    def skipNewline(self, s, i, kind):
        '''
        Called by skipCodeBlock to terminate a function defintion.
        Skip whitespace and comments up to a newline, then skip the newline.
        Issue an error if no newline is found.
        '''
        while i < len(s):
            i = self.skipWs(s, i)
            if self.startsComment(s, i):
                i = self.skipComment(s, i)
            else: break
        if i >= len(s):
            return len(s)
        if g.match(s, i, '\n'):
            i += 1
        else:
            self.error(
                '%s %s does not end in a newline; one will be added\n%s' % (
                    kind, self.sigId, g.get_line(s, i)))
        return i
    #@+node:ekr.20140727075002.18247: *5* BaseScanner.skipParens
    def skipParens(self, s, i):
        '''Skip a parenthisized list, that might contain strings or comments.'''
        return self.skipBlock(s, i, delim1='(', delim2=')')
    #@+node:ekr.20160122061237.1: *5* BaseScanner.skipRegex
    def skipRegex(self, s, i):
        '''Skip the regular expression starting at s[i].'''
        delim = s[i]
        i1 = i
        i += 1
        while i < len(s):
            if s[i] == delim:
                # Count the preceding backslashes.
                i2, n = i - 1, 0
                while 0 <= i2 and s[i2] == '\\':
                    n += 1
                    i2 -= 1
                if (n % 2) == 0:
                    return i + 1
            i += 1
        g.trace('unterminated regex starting at', i1)
        return i

    #@+node:ekr.20140727075002.18248: *5* BaseScanner.skipString
    def skipString(self, s, i):
        # Returns len(s) on unterminated string.
        return g.skip_string(s, i, verbose=False)
    #@+node:ekr.20140727075002.18249: *5* BaseScanner.skipWs
    def skipWs(self, s, i):
        return g.skip_ws(s, i)
    #@+node:ekr.20160122061209.1: *4* BaseScanner.Parser starts methods
    #@+node:ekr.20140727075002.18250: *5* BaseScanner.startsClass/Function & helpers
    # We don't expect to override this code, but subclasses may override the helpers.

    def startsClass(self, s, i):
        '''Return True if s[i:] starts a class definition.
        Sets sigStart, sigEnd, sigId and codeEnd ivars.'''
        val = self.hasClasses and self.startsHelper(s, i, kind='class', tags=self.classTags)
        return val

    def startsFunction(self, s, i):
        '''Return True if s[i:] starts a function.
        Sets sigStart, sigEnd, sigId and codeEnd ivars.'''
        val = self.hasFunctions and self.startsHelper(s, i, kind='function', tags=self.functionTags)
        return val
    #@+node:ekr.20140727075002.18251: *6* BaseScanner.getSigId
    def getSigId(self, ids):
        '''Return the signature's id.

        By default, this is the last id in the ids list.'''
        return ids and ids[-1]
    #@+node:ekr.20140727075002.18252: *6* BaseScanner.skipSigStart
    def skipSigStart(self, s, i, kind, tags):
        '''Skip over the start of a function/class signature.

        tags is in (self.classTags,self.functionTags).

        Return (i,ids) where ids is list of all ids found, in order.'''
        trace = False and self.trace # or kind =='function'
        ids = []; classId = None
        if trace: g.trace('*entry', kind, i, s[i: i + 20])
        start = i
        while i < len(s):
            j = g.skip_ws_and_nl(s, i)
            for z in self.sigFailTokens:
                if g.match(s, j, z):
                    if trace: g.trace('failtoken', z, 'ids', ids)
                    return start, [], None
            for z in self.sigHeadExtraTokens:
                if g.match(s, j, z):
                    i += len(z); break
            else:
                i = self.skipId(s, j)
                theId = s[j: i]
                if theId and theId in tags: classId = theId
                if theId: ids.append(theId)
                else: break
        if trace: g.trace('*exit ', kind, i, i < len(s) and s[i], ids, classId)
        return i, ids, classId
    #@+node:ekr.20140727075002.18253: *6* BaseScanner.skipSigTail
    def skipSigTail(self, s, i, kind):
        '''Skip from the end of the arg list to the start of the block.'''
        trace = False and self.trace
        start = i
        i = self.skipWs(s, i)
        for z in self.sigFailTokens:
            if g.match(s, i, z):
                if trace: g.trace('failToken', z, 'line', g.skip_line(s, i))
                return i, False
        while i < len(s):
            if self.startsComment(s, i):
                i = self.skipComment(s, i)
            elif g.match(s, i, self.blockDelim1):
                if trace: g.trace(repr(s[start: i]))
                return i, True
            else:
                i += 1
        if trace: g.trace('no block delim')
        return i, False
    #@+node:ekr.20140727075002.18254: *6* BaseScanner.startsHelper
    def startsHelper(self, s, i, kind, tags, tag=None):
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
        self.startSigIndent = self.getLeadingIndent(s, i)
        # Get the tag that starts the class or function.
        j = g.skip_ws_and_nl(s, i)
        i = self.skipId(s, j)
        self.sigId = theId = s[j: i] # Set sigId ivar 'early' for error messages.
        if not theId: return False
        if tags:
            if self.caseInsensitive:
                theId = theId.lower()
            if theId not in tags:
                if trace and verbose:
                    # g.trace('**** %s theId: %s not in tags: %s' % (kind,theId,tags))
                    g.trace('%8s: ignoring %s' % (kind, theId))
                return False
        if trace and verbose: g.trace('kind', kind, 'id', theId)
        # Get the class/function id.
        if kind == 'class' and self.sigId in self.anonymousClasses:
            # A hack for Delphi Pascal: interfaces have no id's.
            # g.trace('anonymous',self.sigId)
            classId = theId
            sigId = ''
        else:
            i, ids, classId = self.skipSigStart(s, j, kind, tags) # Rescan the first id.
            sigId = self.getSigId(ids)
            if not sigId:
                if trace and verbose: g.trace('**no sigId', g.get_line(s, i))
                return False
        if self.output_indent < self.startSigIndent:
            if trace: g.trace('**over-indent', sigId)
                #,'output_indent',self.output_indent,'startSigIndent',self.startSigIndent)
            return False
        # Skip the argument list.
        i, ok = self.skipArgs(s, i, kind)
        if not ok:
            if trace and verbose: g.trace('no args', g.get_line(s, i))
            return False
        i = g.skip_ws_and_nl(s, i)
        # Skip the tail of the signature
        i, ok = self.skipSigTail(s, i, kind)
        if not ok:
            if trace and verbose: g.trace('no tail', g.get_line(s, i))
            return False
        sigEnd = i
        # A trick: make sure the signature ends in a newline,
        # even if it overlaps the start of the block.
        if not g.match(s, sigEnd, '\n') and not g.match(s, sigEnd - 1, '\n'):
            if trace and verbose: g.trace('extending sigEnd')
            sigEnd = g.skip_line(s, sigEnd)
        if self.blockDelim1:
            i = g.skip_ws_and_nl(s, i)
            if kind == 'class' and self.sigId in self.anonymousClasses:
                pass # Allow weird Pascal unit's.
            elif not g.match(s, i, self.blockDelim1):
                if trace and verbose: g.trace('no block', g.get_line(s, i))
                return False
        i, ok = self.skipCodeBlock(s, i, kind)
        if not ok: return False
            # skipCodeBlock skips the trailing delim.
        # This assert ensures that all class/function/method definitions end with a newline.
        # It would be False for language like html/xml, but they override this method.
        if self.language != 'javascript':
            assert i > 0 and s[i - 1] == '\n' or i == len(s), (i, len(s))
        # Success: set the ivars.
        self.sigStart = self.adjustDefStart(s, self.sigStart)
        self.codeEnd = i
        self.sigEnd = sigEnd
        self.sigId = sigId
        self.classId = classId
        # Note: backing up here is safe because
        # we won't back up past scan's 'start' point.
        # Thus, characters will never be output twice.
        k = self.sigStart
        if not g.match(s, k, '\n'):
            self.sigStart = g.find_line_start(s, k)
        # Issue this warning only if we have a real class or function.
        if 0: # wrong.
            if s[self.sigStart: k].strip():
                self.error('%s definition does not start a line\n%s' % (
                    kind, g.get_line(s, k)))
        if trace:
            if verbose:
                g.trace(kind, 'returns:\n%s' % s[self.sigStart: i])
            else:
                first_line = g.splitLines(s[self.sigStart: i])[0]
                g.trace(kind, first_line.rstrip())
        return True
    #@+node:ekr.20140727075002.18255: *5* BaseScanner.startsComment
    def startsComment(self, s, i):
        return (
            g.match(s, i, self.lineCommentDelim) or
            g.match(s, i, self.lineCommentDelim2) or
            g.match(s, i, self.blockCommentDelim1) or
            g.match(s, i, self.blockCommentDelim1_2)
        )
    #@+node:ekr.20140727075002.18256: *5* BaseScanner.startsId
    def startsId(self, s, i):
        return g.is_c_id(s[i: i + 1])
    #@+node:ekr.20160122061038.1: *5* BaseScanner.startsRegex
    def startsRegex(self, s, i):
        '''Return True if s[i] starts a regular expression.'''
        return s[i] == '/'
    #@+node:ekr.20140727075002.18257: *5* BaseScanner.startsString
    def startsString(self, s, i):
        return g.match(s, i, '"') or g.match(s, i, "'")
    #@+node:ekr.20140727075002.18258: *3* BaseScanner.run
    def run(self, s, parent, parse_body=False, prepass=False):
        '''The common top-level code for all scanners.'''
        self.isPrepass = prepass
        c = self.c
        self.root = root = parent.copy()
        self.file_s = s
        self.tab_width = c.getTabWidth(p=root)
        # Create the ws equivalent to one tab.
        self.tab_ws = ' ' * abs(self.tab_width) if self.tab_width < 0 else '\t'
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
            return self.prepass(s, parent)
        else:
            self.scan(s, parent, parse_body=parse_body)
            # Check the generated nodes.
            # Return True if the result is equivalent to the original file.
            ok = self.errors == 0 and self.check(s, parent)
            g.app.unitTestDict['result'] = ok
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
    #@+node:ekr.20140727075002.18271: *4* BaseScanner.escapeFalseSectionReferences
    def escapeFalseSectionReferences(self, s):
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
    #@+node:ekr.20140727075002.18259: *4* BaseScanner.checkBlanksAndTabs
    def checkBlanksAndTabs(self, s):
        '''Check for intermixed blank & tabs.'''
        # Do a quick check for mixed leading tabs/blanks.
        blanks = tabs = 0
        for line in g.splitLines(s):
            lws = line[0: g.skip_ws(line, 0)]
            blanks += lws.count(' ')
            tabs += lws.count('\t')
        ok = blanks == 0 or tabs == 0
        if not ok:
            self.report('intermixed blanks and tabs')
        return ok
    #@+node:ekr.20140727075002.18260: *4* BaseScanner.regularizeWhitespace
    def regularizeWhitespace(self, s):
        '''Regularize leading whitespace in s:
        Convert tabs to blanks or vice versa depending on the @tabwidth in effect.
        This is only called for strict languages.'''
        changed = False; lines = g.splitLines(s); result = []; tab_width = self.tab_width
        if tab_width < 0: # Convert tabs to blanks.
            for line in lines:
                i, w = g.skip_leading_ws_with_indent(line, 0, tab_width)
                s = g.computeLeadingWhitespace(w, -abs(tab_width)) + line[i:] # Use negative width.
                if s != line: changed = True
                result.append(s)
        elif tab_width > 0: # Convert blanks to tabs.
            for line in lines:
                s = g.optimizeLeadingWhitespace(line, abs(tab_width)) # Use positive width.
                if s != line: changed = True
                result.append(s)
        if changed:
            action = 'tabs converted to blanks' if self.tab_width < 0 else 'blanks converted to tabs'
            message = 'inconsistent leading whitespace. %s' % action
            self.report(message)
        return ''.join(result)
    #@+node:ekr.20140727075002.18261: *3* BaseScanner.Tokenizing
    #@+node:ekr.20140727075002.18262: *4* BaseScanner.skip...Token
    def skipCommentToken(self, s, i):
        j = self.skipComment(s, i)
        return j, s[i: j]

    def skipIdToken(self, s, i):
        j = self.skipId(s, i)
        return j, s[i: j]

    def skipNewlineToken(self, s, i):
        return i + 1, '\n'

    def skipOtherToken(self, s, i):
        return i + 1, s[i]

    def skipStringToken(self, s, i):
        j = self.skipString(s, i)
        return j, s[i: j]

    def skipWsToken(self, s, i):
        j = i
        while i < len(s) and s[i] != '\n' and s[i].isspace():
            i += 1
        return i, s[j: i]
    #@+node:ekr.20140727075002.18263: *4* BaseScanner.tokenize
    def tokenize(self, s):
        '''Tokenize string s and return a list of tokens (kind,value,line_number)

        where kind is in ('comment,'id','nl','other','string','ws').

        This is used only to verify the imported text.
        '''
        result, i, line_number = [], 0, 0
        while i < len(s):
            progress = j = i
            ch = s[i]
            if ch == '\n':
                kind = 'nl'
                i, val = self.skipNewlineToken(s, i)
            elif ch in ' \t': # self.isSpace(s,i):
                kind = 'ws'
                i, val = self.skipWsToken(s, i)
            elif self.startsComment(s, i):
                kind = 'comment'
                i, val = self.skipCommentToken(s, i)
            elif self.startsString(s, i):
                kind = 'string'
                i, val = self.skipStringToken(s, i)
            elif self.startsId(s, i):
                kind = 'id'
                i, val = self.skipIdToken(s, i)
            else:
                kind = 'other'
                i, val = self.skipOtherToken(s, i)
            assert progress < i and j == progress
            if val:
                result.append((kind, val, line_number),)
            # Use the raw token, s[j:i] to count newlines, not the munged val.
            line_number += s[j: i].count('\n')
            # g.trace('%3s %7s %s' % (line_number,kind,repr(val[:20])))
        return result
    #@-others
#@+node:ekr.20161027114718.1: ** class ImportController
class ImportController(object):
    '''The base class for all new (line-oriented) controller classes.'''

    #@+others
    #@+node:ekr.20161027114542.1: *3* IC.__init__
    #@@nobeautify

    def __init__(self,
        importCommands,
        atAuto,
        gen_clean = True, ### To be removed. True: clean blank lines.
        gen_refs = False, ### To be removed. True: generate section references.
        language = None, # For @language directive.
        name = None, # The kind of importer.
        scanner = None, ### To do: use scanner keyword instead of state.
        strict = False,
    ):
        '''ctor for BaseScanner.'''
        # Copies of args...
        self.importCommands = ic = importCommands
        self.atAuto = atAuto
        self.c = c = ic.c
        self.encoding = ic.encoding
        self.language = language or name
            # For the @language directive.
        self.name = name or language
        assert language or name
        if gen_v2:
            self.scanner = scanner
        else:
            self.state = scanner
                # A scanner instance.
        self.strict = strict
            # True: leading whitespace is significant.
        assert scanner, 'Caller must provide a LineScanner instance'

        # Set from ivars...
        self.has_decls = name not in ('xml', 'org-mode', 'vimoutliner')
        self.is_rst = name in ('rst',)
        self.tree_type = ic.treeType # '@root', '@file', etc.
        
        # Constants...
        if new_ctors: ### not yet.
            self.gen_refs = name in ('javascript',)
            self.gen_clean = name in ('python',)
        else:
            self.gen_clean = gen_clean
            self.gen_refs = gen_refs
        self.tab_width = None # Must be set in run()

        # The ws equivalent to one tab.
        # self.tab_ws = ' ' * abs(self.tab_width) if self.tab_width < 0 else '\t'

        # Settings...
        self.at_auto_warns_about_leading_whitespace = c.config.getBool(
            'at_auto_warns_about_leading_whitespace')
        self.warn_about_underindented_lines = True
        self.at_auto_separate_non_def_nodes = False
            # Not used at present.

        # State vars.
        self.errors = 0
        ic.errors = 0 # Required.
        self.ws_error = False
        self.root = None
    #@+node:ekr.20161027094537.16: *3* IC.check & helpers
    def check(self, unused_s, parent):
        '''ImportController.check'''
        trace = True # and not g.unitTesting
        trace_lines = True
        no_clean = True # True: strict lws check for *all* languages.
        fn = g.shortFileName(self.root.h)
        s1 = g.toUnicode(self.file_s, self.encoding)
        s2 = self.trial_write()
        clean = self.strip_lws # strip_all, clean_blank_lines
        if self.ws_error or (not no_clean and self.gen_clean):
            s1, s2 = clean(s1), clean(s2)
        # Forgive trailing whitespace problems in the last line:
        if self.ws_error:
            s1, s2 = s1.rstrip()+'\n', s2.rstrip()+'\n'
        ok = s1 == s2
        if not ok and self.name == 'javascript':
            s1, s2 = clean(s1), clean(s2)
            ok = s1 == s2
            if ok:
                g.es_print('Leading whitespaced changed for javascript.')
        if not ok:
            lines1, lines2 = g.splitLines(s1), g.splitlines(s2)
            n1, n2 = len(lines1), len(lines2)
            g.es_print('\n===== PERFECT IMPORT FAILED =====', fn)
            g.es_print('len(s1): %s len(s2): %s' % (n1, n2))
            for i in range(min(n1, n2)):
                line1, line2 = lines1[i], lines2[i]
                if line1 != line2:
                     g.es_print('first mismatched line: %s' % (i+1))
                     g.es_print(repr(line1))
                     g.es_print(repr(line2))
                     break
            else:
                g.es_print('all common lines match')
            if trace and trace_lines:
                g.es_print('===== s1: %s' % parent.h)
                for i, s in enumerate(g.splitLines(s1)):
                    g.es_print('%3s %r' % (i+1, s))
                g.trace('===== s2')
                for i, s in enumerate(g.splitLines(s2)):
                    g.es_print('%3s %r' % (i+1, s))
        if 0: # This is wrong headed.
            if not self.strict and not ok:
                # Suppress the error if lws is the cause.
                clean = self.strip_lws # strip_all, clean_blank_lines
                ok = clean(s1) == clean(s2)
        return ok
    #@+node:ekr.20161027114045.1: *4* IC.clean_blank_lines
    def clean_blank_lines(self, s):
        '''Remove all blanks and tabs in all blank lines.'''
        result = ''.join([
            z if z.strip() else z.replace(' ','').replace('\t','')
                for z in g.splitLines(s)
        ])
        return result
    #@+node:ekr.20161102131659.1: *4* IC.strip_*
    def strip_all(self, s):
        '''Strip blank lines and leading whitespace from all lines of s.'''
        return self.strip_lws(self.strip_blank_lines(s))

    def strip_blank_lines(self, s):
        '''Strip all blank lines from s.'''
        return ''.join([z for z in g.splitLines(s) if z.strip()])

    def strip_lws(self, s):
        '''Strip leading whitespace from all lines of s.'''
        return ''.join([z.lstrip() for z in g.splitLines(s)])
    #@+node:ekr.20161027094537.27: *4* IC.trial_write
    def trial_write(self):
        '''Return the trial write for self.root.'''
        at = self.c.atFileCommands
        if self.gen_refs:
            # Alas, the *actual* @auto write code refuses to write section references!!
            at.write(self.root,
                    nosentinels=True,           # was False,
                    perfectImportFlag=False,    # was True,
                    scriptWrite=True,           # was False,
                    thinFile=True,
                    toString=True,
                )
        else:
            at.writeOneAtAutoNode(
                self.root,
                toString=True,
                force=True,
                trialWrite=True,
            )
        return g.toUnicode(at.stringOutput, self.encoding)
    #@+node:ekr.20161102181704.1: *3* IC.Overrides
    # These can be overridden in subclasses.
    #@+node:ekr.20161030190924.20: *4* IC.adjust_parent
    def adjust_parent(self, parent, headline):
        '''Return the effective parent.

        This is overridden by the RstScanner class.'''
        return parent
    #@+node:ekr.20161101061949.1: *4* IC.clean_headline
    def clean_headline(self, s):
        '''
        Return the cleaned version headline s.
        Will typically be overridden in subclasses.
        '''
        return s.strip()
    #@+node:ekr.20161027114007.1: *3* IC.run (entry point) & helpers
    def run(self, s, parent, parse_body=False, prepass=False):
        '''The common top-level code for all scanners.'''
        trace = False and not g.unitTesting
        if trace: g.trace('=' * 30, parent.h)
        c = self.c
        if prepass:
            g.trace('(ImportController) Can not happen, prepass is True')
            return True, [] # Don't split any nodes.
        self.root = root = parent.copy()
        self.file_s = s
        # Init the error/status info.
        self.errors = 0
        # Check for intermixed blanks and tabs.
        self.tab_width = c.getTabWidth(p=root)
        ws_ok = self.check_blanks_and_tabs(s) # Only issues warnings.
        # Regularize leading whitespace
        if not ws_ok:
            s = self.regularize_whitespace(s)
        # Generate the nodes, including directives and section references.
        changed = c.isChanged()
        if g.gen_v2:
            self.v2_gen_lines(s, parent)
        else:
            self.v1_scan(s, parent)
        self.post_pass(parent)
        # Check the generated nodes.
        # Return True if the result is equivalent to the original file.
        ok = self.errors == 0 and self.check(s, parent)
        g.app.unitTestDict['result'] = ok
        # Insert an @ignore directive if there were any serious problems.
        if not ok:
            self.insert_ignore_directive(parent)
        # It's always useless for an an import to dirty the outline.
        for p in root.self_and_subtree():
            p.clearDirty()
        c.setChanged(changed)
        if trace: g.trace('-' * 30, parent.h)
        return ok
    #@+node:ekr.20161027114007.3: *4* IC.check_blanks_and_tabs
    def check_blanks_and_tabs(self, lines):
        '''Check for intermixed blank & tabs.'''
        # Do a quick check for mixed leading tabs/blanks.
        trace = False and not g.unitTesting
        fn = g.shortFileName(self.root.h)
        w = self.tab_width
        blanks = tabs = 0
        for s in g.splitLines(lines):
            lws = self.get_lws(s)
            blanks += lws.count(' ')
            tabs += lws.count('\t')
        # Make sure whitespace matches @tabwidth directive.
        if w < 0:
            ok = tabs == 0
            message = 'tabs found with @tabwidth %s in %s' % (w, fn)
        elif w > 0:
            ok = blanks == 0
            message = 'blanks found with @tabwidth %s in %s' % (w, fn)
        if ok:
            ok = blanks == 0 or tabs == 0
            message = 'intermixed blanks and tabs in: %s' % (fn)
        if ok:
            if trace: g.trace('=====', len(lines), blanks, tabs)
        else:
            if g.unitTesting:
                self.report(message)
            else:
                g.es_print(message)
        return ok
    #@+node:ekr.20161027182014.1: *4* IC.insert_ignore_directive
    def insert_ignore_directive(self, parent):
        c = self.c
        parent.b = parent.b.rstrip() + '\n@ignore\n'
        if g.unitTesting:
            g.app.unitTestDict['fail'] = g.callers()
        elif parent.isAnyAtFileNode() and not parent.isAtAutoNode():
            g.warning('inserting @ignore')
            c.import_error_nodes.append(parent.h)
    #@+node:ekr.20161027183458.1: *4* IC.post_pass & helper
    def post_pass(self, parent):
        '''Clean up parent's children.'''
        # Clean the headlines.
        for p in parent.subtree():
            h = self.clean_headline(p.h)
            assert h
            if h != p.h: p.h = h
        # Clean the nodes, in a language-dependent way.
        if hasattr(self, 'clean_nodes'):
            # pylint: disable=no-member
            self.clean_nodes(parent)
        # Unindent nodes.
        for p in parent.subtree():
            if p.b.strip():
                p.b = self.undent(g.splitLines(p.b))
            else:
                p.b = ''
        # Delete empty nodes.
        aList = []
        for p in parent.subtree():
            s = p.b
            back = p.threadBack()
            if not s.strip() and not p.isCloned() and back != parent:
                back.b = back.b + s
                aList.append(p.copy())
        self.c.deletePositionsInList(aList)
    #@+node:ekr.20161027114007.4: *4* IC.regularize_whitespace
    def regularize_whitespace(self, s):
        '''
        Regularize leading whitespace in s:
        Convert tabs to blanks or vice versa depending on the @tabwidth in effect.
        '''
        trace = True # and not g.unitTesting
        trace_lines = False
        report = trace or not g.unitTesting
        kind = 'tabs' if self.tab_width > 0 else 'blanks'
        kind2 = 'blanks' if self.tab_width > 0 else 'tabs'
        fn = g.shortFileName(self.root.h)
        lines = g.splitLines(s)
        count, result, tab_width = 0, [], self.tab_width
        if tab_width < 0: # Convert tabs to blanks.
            for n, line in enumerate(lines):
                i, w = g.skip_leading_ws_with_indent(line, 0, tab_width)
                s = g.computeLeadingWhitespace(w, -abs(tab_width)) + line[i:]
                    # Use negative width.
                if s != line:
                    count += 1
                    if trace and trace_lines:
                        g.es_print('%s: %r\n%s: %r' % (n+1, line, n+1, s))
                result.append(s)
        elif tab_width > 0: # Convert blanks to tabs.
            for n, line in enumerate(lines):
                s = g.optimizeLeadingWhitespace(line, abs(tab_width))
                    # Use positive width.
                if s != line:
                    count += 1
                    if trace and trace_lines:
                        g.es_print('%s: %r\n%s: %r' % (n+1, line, n+1, s))
                result.append(s)
        if count:
            self.ws_error = True # A flag to check.
            if report:
                g.es_print('\nWarning: Intermixed tabs and blanks in', fn)
                # g.es_print('Perfect import test will ignoring leading whitespace.')
                g.es_print('Changed leading %s to %s in %s line%s' % (
                    kind2, kind, count, g.plural(count)))
            if g.unitTesting: # Sets flag for unit tests.
                self.report('Changed %s lines' % count) 
        return ''.join(result)
    #@+node:ekr.20161030190924.19: *3* IC.Utils
    #@+node:ekr.20161030190924.22: *4* IC.append_to_body
    def append_to_body(self, p, s):
        '''
        Similar to c.appendStringToBody,
        but does not recolor the text or redraw the screen.
        '''
        assert g.isString(s), (repr(s), g.callers())
        assert g.isString(p.b), (repr(p.b), g.callers())
        p.b = p.b + s
    #@+node:ekr.20161030190924.26: *4* IC.create_child_node
    def create_child_node(self, parent, body, headline):
        '''Create a child node of parent.'''
        trace = False and not g.unitTesting
        if trace: g.trace('\n\n%s === in === %s\n' % (headline, parent.h))
        p = parent.insertAsLastChild()
        assert g.isString(body), repr(body)
        assert g.isString(headline), repr(headline)
        p.b = g.u(body)
        p.h = g.u(headline)
        return p
    #@+node:ekr.20161102072135.1: *4* IC.get_lws
    def get_lws(self, s):
        '''Return the characters of the lws of s.'''
        m = re.match(r'(\s*)', s)
        return m.group(0) if m else ''
    #@+node:ekr.20161027181903.1: *4* IC.Messages
    def error(self, s):
        self.errors += 1
        self.importCommands.errors += 1
        if g.unitTesting:
            if self.errors == 1:
                g.app.unitTestDict['actualErrorMessage'] = s
            g.app.unitTestDict['actualErrors'] = self.errors
        else:
            g.error('Error:', s)

    def report(self, message):
        if self.strict:
            self.error(message)
        else:
            self.warning(message)

    def warning(self, s):
        if not g.unitTesting:
            g.warning('Warning:', s)
    #@+node:ekr.20161101081522.1: *4* IC.undent & helper
    def undent(self, lines):
        '''Remove maximal leading whitespace from the start of all lines.'''
        trace = False and not g.unitTesting # and self.root.h.find('main') > -1
        if self.is_rst:
            return ''.join(lines) # Never unindent rst code.
        ws = self.common_lws(lines)
        if trace:
            g.trace('common_lws:', repr(ws))
            print('===== lines:\n%s' % ''.join(lines))
        result = []
        for s in lines:
            if s.startswith(ws):
                result.append(s[len(ws):])
            elif self.strict:
                # Indicate that the line is underindented.
                result.append("%s%s.%s" % (
                    self.c.atFileCommands.underindentEscapeString,
                    g.computeWidth(ws, self.tab_width),
                    s.lstrip()))
            else:
                result.append(s.lstrip())
        if trace:
            print('----- result:\n%s' % ''.join(result))
        return ''.join(result)
    #@+node:ekr.20161102055342.1: *5* common_lws
    def common_lws(self, lines):
        '''Return the lws common to all lines.'''
        trace = False and not g.unitTesting
        if not lines:
            return ''
        lws = self.get_lws(lines[0])
        for s in lines:
            lws2 = self.get_lws(s)
            ###
            # if s.strip().endswith('>>') and s.strip().startswith('<<'):
                # pass # Ignore section references.
            # el
            if lws2.startswith(lws):
                pass
            elif lws.startswith(lws2):
                lws = lws2
            else:
                lws = '' # Nothing in common.
                break
        if trace: g.trace(repr(lws), repr(lines[0]))
        return lws
    #@+node:ekr.20161030190924.41: *4* IC.underindented_comment/line
    def underindented_comment(self, line):
        if self.at_auto_warns_about_leading_whitespace:
            self.warning(
                'underindented python comments.\n' +
                'Extra leading whitespace will be added\n' + line)

    def underindented_line(self, line):
        if self.warn_about_underindented_lines:
            self.error(
                'underindented line.\n'
                'Extra leading whitespace will be added\n' + line)
    #@+node:ekr.20161101094729.1: *3* IC.V1: Scanning & code generation
    #@+node:ekr.20161101094324.1: *4* IC.gen_lines (entry) & helpers
    def gen_lines(self, indent_flag, lines, parent, tag='top-level'):
        '''
        The entry point for parsing and code generation. Also called by
        rescan_code_block.
        
        Parse all lines, adding to parent.b, creating child nodes as necessary.
        '''
        trace = True and not g.unitTesting and self.root.h.endswith('.py')
        if not lines:
            return
        gen_refs, state = self.gen_refs, self.state
        if trace:
            g.trace(tag, state)
            print('===== entry lines:...')
            for line in lines:
                print(line.rstrip())
            print('----- end entry lines.')
        assert not state.context, state
        i, ref_flag = 0, False
        while i < len(lines):
            progress = i
            line = lines[i]
            state.scan_line(line)
            if state.starts_block():
                # Generate the reference first.
                ref_flag = self.gen_ref(indent_flag, line, parent, ref_flag)
                # Scan the code block and its tail.
                code_lines, tail_lines = self.skip_code_block(i, lines)
                i += (len(code_lines) + len(tail_lines))
                if gen_refs:
                    self.rescan_code_block(code_lines, parent)
                    self.append_to_body(parent, ''.join(tail_lines))
                else:
                    code_lines.extend(tail_lines)
                    self.rescan_code_block(code_lines, parent)
            else:
                # This works for both @others and section references.
                # After @others, child nodes contain *all* lines.
                if ref_flag and not gen_refs:
                    g.trace('Can not happen: line not in tail: %r' % line)
                self.append_to_body(parent, line)
                i += 1
            assert progress < i
    #@+node:ekr.20161030190924.13: *5* IC.skip_code_block
    def skip_code_block(self, i, lines):
        '''
        lines[i] starts a class or function.
        
        Return (code_lines, tail_lines) where:
        - code_lines are all the lines of the class or function.
        - tail lines are all lines up to but not including the next class or function.
        '''
        trace = True and not g.unitTesting and self.root.h.endswith('.py')
        trace_lines = False
        trace_entry = True
        trace_results = True
        state = self.state
        assert state.starts_block()
        assert not state.context, state
        state.push()
        state.clear()
        if trace and trace_entry:
            g.trace(state)
            print('===== entry lines:...')
            for j in range(i, len(lines)):
                print('  %s' % lines[j].rstrip()) # entry lines.
            print('----- end entry lines')
        # Scan the code block.
        # We have cleared the state, so rescan the first line.
        block_i = i
        state.scan_line(lines[i])
        assert state.starts_block()
        i += 1
        while i < len(lines):
            progress = i
            line = lines[i]
            if trace and trace_lines:
                g.trace(state, line.rstrip())
            state.scan_line(line)
            if state.continues_block():
                i += 1
            elif self.name == 'python':
                break
            else:
                i += 1
                break
            assert progress < i
        code_lines = lines[block_i:i]
        if trace and trace_results:
            g.trace('===== code lines:...')
            for line in code_lines:
                print('  %s' % line.rstrip()) # code lines.
            print('----- end code lines')
        # Scan the block's tail.
        # Line i is *not* part of the code block and it has not been scanned.
        tail_i = i
        if i < len(lines):
            state.scan_line(lines[i])
            if not state.starts_block():
                i += 1 # Add the just-scanned line.
                while i < len(lines):
                    line = lines[i]
                    if trace and trace_lines: g.trace(line.rstrip())
                    state.scan_line(line)
                    if state.starts_block():
                        break
                    else:
                        i += 1
        tail_lines = lines[tail_i:i]
        if trace and trace_results:
            g.trace('===== tail lines:...')
            for line in tail_lines:
                print('  %s' % line.rstrip()) # tail lines.
            print('----- end-tail-lines')
        state.pop()
        return code_lines, tail_lines
    #@+node:ekr.20161101113520.1: *4* IC.gen_ref
    def gen_ref(self, indent_flag, line, parent, ref_flag):
        '''
        Generate the ref line and a flag telling this method whether a previous
        #@+others
        #@-others
        '''
        trace = False and not g.unitTesting
        indent_ws = self.get_lws(line)
            ### Ignore indent_flag: Hurray!
        if self.is_rst and not self.atAuto:
            return None, None
        elif self.gen_refs:
            headline = self.clean_headline(line)
            ref = '%s%s\n' % (
                indent_ws,
                g.angleBrackets(' %s ' % headline))
        else:
            ref = None if ref_flag else '%s@others\n' % indent_ws
            ref_flag = True # Don't generate another @others.
        if ref:
            if trace: g.trace('%s indent_ws: %r line: %r parent: %s' % (
                '*' * 20, indent_ws, line, parent.h))
            self.append_to_body(parent, ref)
        return ref_flag
    #@+node:ekr.20161031041540.1: *4* IC.v1_scan
    def v1_scan(self, s, parent, parse_body=False):
        '''
        v1_scan: V1 of line-based scanners and code generators.
        
        Create a child of self.root for:
        - Leading outer-level declarations.
        - Outer-level classes.
        - Outer-level functions.
        '''
        # Create the initial body text in the root.
        if parse_body:
            pass
        else:
            self.append_to_body(parent,
                '@language %s\n@tabwidth %d\n' % (
                    self.language,
                    self.tab_width))
            self.gen_lines(
                indent_flag = False,
                lines = g.splitlines(s),
                parent = parent,
            )
    #@+node:ekr.20161101124821.1: *4* IC.rescan_code_block (calls gen_lines)
    def rescan_code_block(self, lines, parent):
        '''Create a child of the parent, and add lines to parent.b.'''
        if not lines:
            return
        state = self.state
        first_line = lines[0]
        assert first_line.strip
        headline = self.clean_headline(first_line)
        if self.gen_refs:
            headline = g.angleBrackets(' %s ' % headline)
        child = self.create_child_node(
            parent,
            body = '',
            headline = headline)
        if self.name == 'python':
            last_line = None
            lines = lines[1:]
        else:
            last_line = lines[-1]
            lines = lines[1:-1]
        self.append_to_body(child, first_line)
        state.push()
        self.gen_lines(
            indent_flag = True,
            lines = lines,
            parent = child,
            tag = 'rescan_code_block')
        state.pop()
        if last_line:
            self.append_to_body(child, last_line)
        
    #@+node:ekr.20161104084810.1: *3* IC.V2: v2_gen_lines & helpers
    def v2_gen_lines(self, s, parent):
        '''Parse all lines of s into parent and created child nodes.'''
        trace = False and not g.unitTesting and self.root.h.endswith('javascript-3.js')
        gen_refs, scanner = self.gen_refs, self.scanner
        tail_p = None
        prev_state = scanner.initial_state()
        stack = [Target(parent, prev_state)]
        for line in g.splitLines(s):
            new_state = scanner.v2_scan_line(line, prev_state)
            if trace: g.trace(bool(tail_p), new_state, repr(line))
            if new_state.v2_starts_block(prev_state):
                tail_p = None
                target=stack[-1]
                # Insert the reference in *this* node.
                h = self.v2_gen_ref(line, target.p, target)
                # Create a new child and associated target.
                child = self.v2_create_child_node(target.p, line, h)
                stack.append(Target(child, new_state))
                prev_state = new_state
            elif new_state.v2_continues_block(prev_state):
                p = tail_p or stack[-1].p
                p.b = p.b + line
            else:
                # The block is ending. Add tail lines until the start of the next block.
                p = stack[-1].p # Put the closing line in *this* node.
                if not gen_refs:
                    tail_p = p # Put trailing lines in this node.
                p.b = p.b + line
                self.cut_stack(new_state, stack)
            prev_state = new_state
    #@+node:ekr.20161106104418.1: *4* IC.v2_create_child_node
    def v2_create_child_node(self, parent, body, headline):
        '''Create a child node of parent.'''
        trace = False and not g.unitTesting and self.root.h.endswith('javascript-3.js')
        if trace: g.trace('\n\nREF: %s === in === %s\n%r\n' % (headline, parent.h, body))
        p = parent.insertAsLastChild()
        assert g.isString(body), repr(body)
        assert g.isString(headline), repr(headline)
        p.b = p.b + body
        p.h = headline
        return p
    #@+node:ekr.20161104084810.2: *4* IC.cut_stack
    def cut_stack(self, new_state, stack):
        '''Cut back the stack until stack[-1] matches new_state.'''
        trace = False and not g.unitTesting and self.root.h.endswith('.js')
        trace_stack = True
        if trace and trace_stack:
            g.trace('Stack...')
            print('\n'.join([repr(z) for z in stack]))
        while stack:
            top_state = stack[-1].state
            if top_state > new_state:
                if trace: g.trace('top_state > state', top_state)
                stack.pop()
            elif top_state == new_state:
                if trace: g.trace('top_state == state', top_state)
                break
            else:
                if trace:
                    g.trace('top_state < state', top_state)
                    g.trace('===== overshoot')
                        # Can happen with valid javascript programs.
                break
        if not stack:
            g.trace('===== underflow')
            stack = [self.scanner.initial_state()]
        if trace:
            g.trace('new target.p:', stack[-1].p.h)
    #@+node:ekr.20161105044835.1: *4* IC.v2_gen_ref
    def v2_gen_ref(self, line, parent, target):
        '''
        Generate the ref line and a flag telling this method whether a previous
        #@+others
        #@-others
        '''
        trace = False and not g.unitTesting
        indent_ws = self.get_lws(line)
        h = self.clean_headline(line) 
        if self.is_rst and not self.atAuto:
            return None, None
        elif self.gen_refs:
            headline = g.angleBrackets(' %s ' % h)
            ref = '%s%s\n' % (
                indent_ws,
                g.angleBrackets(' %s ' % h))
        else:
            ref = None if target.ref_flag else '%s@others\n' % indent_ws
            target.ref_flag = True
                # Don't generate another @others in this target.
            headline = h
        if ref:
            if trace: g.trace('%s indent_ws: %r line: %r parent: %s' % (
                '*' * 20, indent_ws, line, parent.h))
            parent.b = parent.b + ref
        return headline
    #@-others
#@+node:ekr.20161027115813.1: ** class LineScanner
class LineScanner(object):
    '''
    A class to scan lines.
    
    Subclasses overide *both* the scan_line and v2_scan_line methods.
    These methods work with the various X_ScanState classes.
    '''

    #@+others
    #@+node:ekr.20161027115813.2: *3* scanner.__init__ & __repr__
    def __init__(self, c, language=None):
        '''Ctor for the LineScanner class.'''
        self.c = c
        self.language = language 
        self.comment_delims = g.set_delims_from_language(language) if language else None
            # For general_line_scanner
        self.tab_width = c.tab_width
        if gen_v2:
            pass
        else:
            self.context = '' # Represents cross-line constructs.
            self.base_curlies = self.curlies = 0
            self.stack = []

    def __repr__(self):
        '''LineScanner.__repr__'''
        return 'LineScanner: base: %r now: %r context: %2r' % (
            '{' * self.base_curlies,
            '{' * self.curlies, self.context)
            
    __str__ = __repr__
    #@+node:ekr.20161104143211.3: *3* scanner.get_lws
    def get_lws(self, s):
        '''Return the the lws (a number) of line s.'''
        return g.computeLeadingWhitespaceWidth(s, self.c.tab_width)
    #@+node:ekr.20161103065140.1: *3* scanner.match
    def match(self, s, i, pattern):
        '''Return True if the pattern matches at s[i:]'''
        return s[i:i+len(pattern)] == pattern
    #@+node:ekr.20161105141816.1: *3* V1 methods
    #@+node:ekr.20161027115813.5: *4* scanner.clear, push & pop
    if gen_v2:
        
        pass
        
    else:

        def clear(self):
            '''Clear the state.'''
            self.base_curlies = self.curlies = 0
            self.context = ''
        
        def pop(self):
            '''Restore the base state from the stack.'''
            self.base_curlies = self.stack.pop()
            
        def push(self):
            '''Save the base state on the stack and enter a new base state.'''
            self.stack.append(self.base_curlies)
            self.base_curlies = self.curlies
    #@+node:ekr.20161027115813.7: *4* scanner.scan_line
    def scan_line(self, s):
        '''
        A *typical* line scanner. Subclasses should redefine this method.

        Commented-out code illustrates how to handle block comments.
        '''
        trace = False and not g.unitTesting
        contexts = strings = ['"', "'"]
        # match = self.match
        # block1, block2 = '/*', '*/
        # contexts.append(block1)
        i = 0
        while i < len(s):
            progress = i
            ch = s[i]
            if self.context:
                assert self.context in contexts, repr(self.context)
                if ch == '\\':
                    i += 1 # Eat the next character later.
                elif self.context in strings and self.context == ch:
                    self.context = '' # End the string.
                # elif self.context == block1 and match(s, i, block2):
                    # self.context = '' # End the block comment.
                    # i += (len(block2) - 1)
                else:
                    pass # Eat the string character later.
            elif ch in strings:
                self.context = ch
            # elif match(s, i, block1):
                # self.context = block1
                # i += (len(block1) - 1)
            # elif match(s, i, line_comment):
            elif ch == '#':
                break # The single-line comment ends the line.
            elif ch == '{': self.curlies += 1
            elif ch == '}': self.curlies -= 1
            i += 1
            assert progress < i
        if trace:
            g.trace(self, s.rstrip())
        if gen_v2:
            return ScanState(self.context, self.curlies)
    #@+node:ekr.20161027115813.3: *4* scanner.V1: continues_block and starts_block
    if gen_v2:
        
        pass
        
    else:

        def continues_block(self):
            '''Return True if the just-scanned lines should be placed in the inner block.'''
            return self.context or self.curlies > self.base_curlies
        
        def starts_block(self):
            '''Return True if the just-scanned line starts an inner block.'''
            return not self.context and self.curlies > self.base_curlies
    #@+node:ekr.20161105141836.1: *3* V2 methods
    #@+node:ekr.20161106180704.1: *4* scanner.general_scan_line
    def general_scan_line(self, s):
        '''
        A generalized line scanner, using comment delims set in the ctor from
        the language keword arg.
        '''
        trace = False and not g.unitTesting
        
        match = self.match
        assert self.comment_delims
        line_comment, block1, block2 = self.comment_delims
        contexts = strings = ['"', "'"]
        if block1:
            contexts.append(block1)
        i = 0
        while i < len(s):
            progress = i
            ch = s[i]
            if self.context:
                assert self.context in contexts, repr(self.context)
                if ch == '\\':
                    i += 1 # Eat the next character later.
                elif self.context in strings and self.context == ch:
                    self.context = '' # End the string.
                elif block1 and self.context == block1 and match(s, i, block2):
                    self.context = '' # End the block comment.
                    i += (len(block2) - 1)
                else:
                    pass # Eat the string character later.
            elif ch in strings:
                self.context = ch
            elif block1 and match(s, i, block1):
                self.context = block1
                i += (len(block1) - 1)
            elif line_comment and match(s, i, line_comment):
                break # The single-line comment ends the line.
            elif ch == '{': self.curlies += 1
            elif ch == '}': self.curlies -= 1
            i += 1
            assert progress < i
        if trace:
            g.trace(self, s.rstrip())
        if gen_v2:
            return ScanState(self.context, self.curlies)
    #@+node:ekr.20161104144603.1: *4* scanner.initial_state
    def initial_state(self):
        '''Return the initial counts.'''
        assert False, 'Subclasses must override LineScanner.initial_state.'
    #@+node:ekr.20161105140842.4: *4* scanner.v2_scan_line
    def v2_scan_line(self, s, prev_state, block_comment=None, line_comment='#'):
        '''
        A generalized line scanner.  This will suffice for many languages,
        but it should be overridden for languages that have regex syntax
        or for languages like Python that do not delimit structure with brackets.

        Sets three ivars for LineScanner.starts_block and LineScanner.continues_block:
        
        - .context is non-empty if we are scanning a multi-line string, comment
          or regex.
        
        - .curlies and .parens are the present counts of open curly-brackets
          and parentheses.
        '''
        trace = False and not g.unitTesting
        match = self.match
        context, curlies = prev_state.context, prev_state.curlies
        contexts = strings = ['"', "'"]
        block1, block2 = None, None
        if block_comment:
            block1, block2 = block_comment
            contexts.append(block1)
        i = 0
        while i < len(s):
            progress = i
            ch = s[i]
            if context:
                assert context in contexts, repr(context)
                if ch == '\\':
                    i += 1 # Eat the next character later.
                elif context in strings and context == ch:
                    context = '' # End the string.
                elif context == block1 and match(s, i, block2):
                    context = '' # End the block comment.
                    i += (len(block2) - 1)
                else:
                    pass # Eat the string character later.
            elif ch in strings:
                context = ch
            elif match(s, i, block1):
                context = block1
                i += (len(block1) - 1)
            elif match(s, i, line_comment):
                break # The single-line comment ends the line.
            elif ch == '{': curlies += 1
            elif ch == '}': curlies -= 1
            i += 1
            assert progress < i
        if trace:
            g.trace(self, s.rstrip())
        if gen_v2:
            return ScanState_V2(context, curlies)
    #@-others
#@+node:ekr.20161105172716.1: ** class ScanState
class ScanState:
    '''A class representing the state of the v1 scan.'''
    
    def __init__(self, context, curlies):
        '''Ctor for the ScanState class.'''
        self.base_curlies = curlies
        self.context = context
        self.curlies = curlies
        
    def __repr__(self):
        '''ScanState.__repr__'''
        return 'ScanState context: %r curlies: %s' % (
            self.context, self.curlies)

    #@+others
    #@+node:ekr.20161105172716.3: *3* ScanState: V1: starts/continues_block
    def continues_block(self):
        '''Return True if the just-scanned lines should be placed in the inner block.'''
        return self.context or self.curlies > self.base_curlies

    def starts_block(self):
        '''Return True if the just-scanned line starts an inner block.'''
        return not self.context and self.curlies > self.base_curlies
    #@-others
#@+node:ekr.20161105045904.1: ** class ScanState_V2
class ScanState_V2:
    '''A class representing the state of the v2 scan.'''
    
    def __init__(self, context, curlies):
        '''Ctor for the ScanState class.'''
        self.context = context
        self.curlies = curlies
        
    def __repr__(self):
        '''ScanState.__repr__'''
        return 'ScanState_V2 context: %r curlies: %s' % (
            self.context, self.curlies)

    #@+others
    #@+node:ekr.20161105085900.1: *3* ScanState: V2: comparisons
    def __eq__(self, other):
        '''Return True if the state continues the previous state.'''
        return self.context or self.curlies == other.curlies
        
    def __lt__(self, other):
        '''Return True if we should exit one or more blocks.'''
        return not self.context and self.curlies < other.curlies

    def __gt__(self, other):
        '''Return True if we should enter a new block.'''
        return not self.context and self.curlies < other.curlies
        
    def __ne__(self, other): return not self.__ne__(other)  
    def __ge__(self, other): return NotImplemented
    def __le__(self, other): return NotImplemented
    #@+node:ekr.20161105180504.1: *3* ScanState: v2.starts/continues_block
    def v2_continues_block(self, prev_state):
        '''Return True if the just-scanned lines should be placed in the inner block.'''
        return self == prev_state

    def v2_starts_block(self, prev_state):
        '''Return True if the just-scanned line starts an inner block.'''
        return self > prev_state
    #@-others

#@+node:ekr.20161104090312.1: ** class Target
class Target:
    '''
    A class describing a target node p.
    state is used to cut back the stack.
    '''

    def __init__(self, p, state):
        '''Ctor for the Block class.'''
        self.p = p
        self.ref_flag = False
            # True: @others or section reference should be generated.
            # It's always True when gen_refs is True.
        self.state = state

    def __repr__(self):
        return 'Target: state: %s p: %s' % (self.state, self.p.h)
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 60
#@-leo
