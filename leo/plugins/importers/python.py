#@+leo-ver=5-thin
#@+node:ekr.20161029103517.1: * @file importers/python.py
'''The new, line-based, @auto importer for Python.'''
import leo.core.leoGlobals as g
import leo.plugins.importers.basescanner as basescanner
import leo.plugins.importers.linescanner as linescanner
import re
ImportController = basescanner.ImportController
Importer = linescanner.Importer
v2 = False
#@+others
#@+node:ekr.20161108203248.1: ** V1 classes
#@+node:ekr.20161029103640.1: *3* class Python_ImportController (ImportController)
class Python_ImportController(ImportController):
    '''The legacy importer for the python language.'''

    def __init__(self, importCommands, atAuto, language=None, alternate_language=None):
        '''The ctor for the Python_ImportController class.'''
        # Init the base class.
        ImportController.__init__(self,
            importCommands,
            atAuto,
            gen_clean = False, # True: clean blank lines & unindent blocks.
            gen_refs = False, # Don't generate section references.
            language = 'python', # For @language.
            scanner = PythonScanner(importCommands, atAuto),
            strict = True, # True: leave leading whitespace alone.
        )
        self.ws_pattern = re.compile(r'^\s*$|^\s*#')
            # Matches lines containing nothing but ws or comments.

    #@+others
    #@+node:ekr.20161107154640.1: *4* python_ic.is_ws_line
    def is_ws_line(self, s):
        '''Return True if s is nothing but whitespace and comments.'''
        return bool(self.ws_pattern.match(s))
    #@+node:ekr.20161029103640.2: *4* python_ic.clean_headline
    def clean_headline(self, s):
        '''Return a cleaned up headline s.'''
        m = re.match(r'\s*def\s+(\w+)', s)
        if m:
            return m.group(1)
        else:
            m = re.match(r'\s*class\s+(\w+)', s)
            if m:
                return 'class %s' % m.group(1)
            else:
                return s.strip()
    #@+node:ekr.20161029103640.3: *4* python_ic.clean_nodes (Does nothing)
    def clean_nodes(self, parent):
        '''
        Clean nodes as part of the post pass.
        Called *before* undent, so there are no underindent escapes here!
        
        For Python, it's best not to move lines around.
        '''
        pass
    #@+node:ekr.20161107111224.1: *4* python_ic.common_lws
    def common_lws(self, lines):
        '''Return the lws common to all lines.'''
        trace = False and not g.unitTesting
        if not lines:
            return ''
        head = True
        for s in lines:
            is_ws = self.is_ws_line(s)
            if head:
                if not is_ws: # A real line.
                    head = False
                    lws = self.get_str_lws(s)
            elif is_ws:
                # Ignore lines containing only whitespace or comments.
                pass
            else:
                lws2 = self.get_str_lws(s)
                if lws2.startswith(lws):
                    pass
                elif lws.startswith(lws2):
                    lws = lws2
                else:
                    lws = '' # Nothing in common.
                    break
        if head:
            lws = '' # All head lines.
        if trace: g.trace(repr(lws), repr(lines[0]))
        return lws
    #@+node:ekr.20161107112448.1: *4* python_ic.undent
    def undent(self, p):
        '''
            Python_ImportController.undent.
            Remove maximal leading whitespace from the start of all lines.
            
            Called *after* clean_node, so all lines have been moved.
        '''
        trace = False and not g.unitTesting
        if self.is_rst:
            return p.b # Never unindent rst code.
        lines = g.splitLines(p.b)
        ws = self.common_lws(lines)
        if trace:
            g.trace('common_lws:', repr(ws))
            print('===== lines:\n%s' % ''.join(lines))
        result = []
        # Move underindented *trailing* whitespace-only lines
        # to the end of the parent.
        parent = p.parent()
        while lines:
            line = lines[-1]
            if line.startswith(ws):
                break
            elif self.is_ws_line(line):
                parent.b = parent.b + lines.pop()
            else:
                break
        p.b = ''.join(lines)
        # Handle the remaining lines.
        for s in lines:
            if s.startswith(ws):
                result.append(s[len(ws):])
            else:
                # Like the base class.
                # Indicate that the line is underindented.
                result.append("%s%s.%s" % (
                    self.c.atFileCommands.underindentEscapeString,
                    g.computeWidth(ws, self.tab_width),
                    s.lstrip()))
        if trace:
            print('----- result:\n%s' % ''.join(result))
        return ''.join(result)
    #@-others
#@+node:ekr.20161029120457.1: *3* V1: class PythonScanner
class PythonScanner(basescanner.BaseScanner):
    #@+others
    #@+node:ekr.20161029120457.2: *4*  __init__ (PythonScanner)
    def __init__(self, importCommands, atAuto):
        # Init the base class.
        basescanner.BaseScanner.__init__(self, importCommands, atAuto=atAuto, language='python')
        # Set the parser delims.
        self.lineCommentDelim = '#'
        self.classTags = ['class',]
        self.functionTags = ['def',]
        self.ignoreBlankLines = True
        self.blockDelim1 = self.blockDelim2 = None
            # Suppress the check for the block delim.
            # The check is done in skipSigTail.
        self.strict = True
    #@+node:ekr.20161029120457.3: *4* adjustDefStart (PythonScanner)
    def adjustDefStart(self, s, i):
        '''A hook to allow the Python importer to adjust the
        start of a class or function to include decorators.
        '''
        # Invariant: i does not change.
        # Invariant: start is the present return value.
        try:
            assert s[i] != '\n'
            start = j = g.find_line_start(s, i) if i > 0 else 0
            # g.trace('entry',j,i,repr(s[j:i+10]))
            assert j == 0 or s[j - 1] == '\n'
            while j > 0:
                progress = j
                j1 = j = g.find_line_start(s, j - 2)
                # g.trace('line',repr(s[j:progress]))
                j = g.skip_ws(s, j)
                if not g.match(s, j, '@'):
                    break
                k = g.skip_id(s, j + 1)
                word = s[j: k]
                # Leo directives halt the scan.
                if word and word in g.globalDirectiveList:
                    break
                # A decorator.
                start = j = j1
                assert j < progress
            # g.trace('**returns %s, %s' % (repr(s[start:i]),repr(s[i:i+20])))
            return start
        except AssertionError:
            g.es_exception()
            return i
    #@+node:ekr.20161029120457.4: *4* extendSignature
    def extendSignature(self, s, i):
        '''Extend the text to be added to the class node following the signature.

        The text *must* end with a newline.'''
        # Add a docstring to the class node,
        # And everything on the line following it
        j = g.skip_ws_and_nl(s, i)
        if g.match(s, j, '"""') or g.match(s, j, "'''"):
            j = g.skip_python_string(s, j)
            if j < len(s): # No scanning error.
                # Return the docstring only if nothing but whitespace follows.
                j = g.skip_ws(s, j)
                if g.is_nl(s, j):
                    return j + 1
        return i
    #@+node:ekr.20161029120457.5: *4* findClass (PythonScanner)
    def findClass(self, p):
        '''Return the index end of the class or def in a node, or -1.'''
        s, i = p.b, 0
        while i < len(s):
            progress = i
            if s[i] in (' ', '\t', '\n'):
                i += 1
            elif self.startsComment(s, i):
                i = self.skipComment(s, i)
            elif self.startsString(s, i):
                i = self.skipString(s, i)
            elif self.startsClass(s, i):
                return 'class', self.sigStart, self.codeEnd
            elif self.startsFunction(s, i):
                return 'def', self.sigStart, self.codeEnd
            elif self.startsId(s, i):
                i = self.skipId(s, i)
            else:
                i += 1
            assert progress < i, 'i: %d, ch: %s' % (i, repr(s[i]))
        return None, -1, -1
    #@+node:ekr.20161029120457.6: *4* skipCodeBlock (PythonScanner) & helpers
    def skipCodeBlock(self, s, i, kind):
        trace = False; verbose = True
        # if trace: g.trace('***',g.callers())
        startIndent = self.startSigIndent
        if trace: g.trace('startIndent', startIndent)
        assert startIndent is not None
        i = start = g.skip_ws_and_nl(s, i)
        parenCount = 0
        underIndentedStart = None # The start of trailing underindented blank or comment lines.
        while i < len(s):
            progress = i
            ch = s[i]
            if g.is_nl(s, i):
                if trace and verbose: g.trace(g.get_line(s, i))
                backslashNewline = (i > 0 and g.match(s, i - 1, '\\\n'))
                if backslashNewline:
                    # An underindented line, including docstring,
                    # does not end the code block.
                    i += 1 # 2010/11/01
                else:
                    i = g.skip_nl(s, i)
                    j = g.skip_ws(s, i)
                    if g.is_nl(s, j):
                        pass # We have already made progress.
                    else:
                        i, underIndentedStart, breakFlag = self.pythonNewlineHelper(
                            s, i, parenCount, startIndent, underIndentedStart)
                        if breakFlag: break
            elif ch == '#':
                i = g.skip_to_end_of_line(s, i)
            elif ch == '"' or ch == '\'':
                i = g.skip_python_string(s, i)
            elif ch in '[{(':
                i += 1; parenCount += 1
                # g.trace('ch',ch,parenCount)
            elif ch in ']})':
                i += 1; parenCount -= 1
                # g.trace('ch',ch,parenCount)
            else: i += 1
            assert(progress < i)
        # The actual end of the block.
        if underIndentedStart is not None:
            i = underIndentedStart
            if trace: g.trace('***backtracking to underindent range')
            if trace: g.trace(g.get_line(s, i))
        if 0 < i < len(s) and not g.match(s, i - 1, '\n'):
            g.trace('Can not happen: Python block does not end in a newline.')
            g.trace(g.get_line(s, i))
            return i, False
        # 2010/02/19: Include all following material
        # until the next 'def' or 'class'
        i = self.skipToTheNextClassOrFunction(s, i, startIndent)
        if (trace or self.trace) and s[start: i].strip():
            g.trace('%s returns\n' % (kind) + s[start: i])
        return i, True
    #@+node:ekr.20161029120457.7: *5* pythonNewlineHelper
    def pythonNewlineHelper(self, s, i, parenCount, startIndent, underIndentedStart):
        trace = False
        breakFlag = False
        j, indent = g.skip_leading_ws_with_indent(s, i, self.tab_width)
        if trace: g.trace(
            'startIndent', startIndent, 'indent', indent, 'parenCount', parenCount,
            'line', repr(g.get_line(s, j)))
        if indent <= startIndent and parenCount == 0:
            # An underindented line: it ends the block *unless*
            # it is a blank or comment line or (2008/9/1) the end of a triple-quoted string.
            if g.match(s, j, '#'):
                if trace: g.trace('underindent: comment')
                if underIndentedStart is None: underIndentedStart = i
                i = j
            elif g.match(s, j, '\n'):
                if trace: g.trace('underindent: blank line')
                # Blank lines never start the range of underindented lines.
                i = j
            else:
                if trace: g.trace('underindent: end of block')
                breakFlag = True # The actual end of the block.
        else:
            if underIndentedStart and g.match(s, j, '\n'):
                # Add the blank line to the underindented range.
                if trace: g.trace('properly indented blank line extends underindent range')
            elif underIndentedStart and g.match(s, j, '#'):
                # Add the (properly indented!) comment line to the underindented range.
                if trace: g.trace('properly indented comment line extends underindent range')
            elif underIndentedStart is None:
                pass
            else:
                # A properly indented non-comment line.
                # Give a message for all underindented comments in underindented range.
                if trace: g.trace('properly indented line generates underindent errors')
                s2 = s[underIndentedStart: i]
                lines = g.splitlines(s2)
                for line in lines:
                    if line.strip():
                        junk, indent = g.skip_leading_ws_with_indent(line, 0, self.tab_width)
                        if indent <= startIndent:
                            if j not in self.errorLines: # No error yet given.
                                self.errorLines.append(j)
                                self.underindentedComment(line)
                underIndentedStart = None
        if trace: g.trace('breakFlag', breakFlag, 'returns', i, 'underIndentedStart', underIndentedStart)
        return i, underIndentedStart, breakFlag
    #@+node:ekr.20161029120457.8: *5* skipToTheNextClassOrFunction (New in 4.8)
    def skipToTheNextClassOrFunction(self, s, i, lastIndent):
        '''Skip to the next python def or class.
        Return the original i if nothing more is found.
        This allows the "if __name__ == '__main__' hack
        to appear at the top level.'''
        return i # A rewrite is needed.
    #@+node:ekr.20161029120457.9: *4* skipSigTail
    # This must be overridden in order to handle newlines properly.

    def skipSigTail(self, s, i, kind):
        '''Skip from the end of the arg list to the start of the block.'''
        if 1: # New code
            while i < len(s):
                ch = s[i]
                if ch == ':':
                    return i, True
                elif ch == '\n':
                    return i, False
                elif self.startsComment(s, i):
                    i = self.skipComment(s, i)
                else:
                    i += 1
            return i, False
        else: # old code
            while i < len(s):
                ch = s[i]
                if ch == '\n':
                    break
                elif ch in (' ', '\t',):
                    i += 1
                elif self.startsComment(s, i):
                    i = self.skipComment(s, i)
                else:
                    break
            return i, g.match(s, i, ':')
    #@+node:ekr.20161029120457.10: *4* skipString
    def skipString(self, s, i):
        # Returns len(s) on unterminated string.
        return g.skip_python_string(s, i, verbose=False)
    #@-others
#@+node:ekr.20161108203332.1: ** V2 classes
#@+node:ekr.20161029103615.1: *3* class Py_Importer(Importer)
class Py_Importer(Importer):
    '''A class to store and update scanning state.'''
    
    def __init__(self, importCommands, atAuto, language=None, alternate_language=None):
        '''Py_Importer.ctor.'''
        # Init the base class.
        Importer.__init__(self,
            importCommands,
            atAuto = atAuto,
            language = 'python',
        )
        self.starts_pattern = re.compile(r'\s*(class|def)')
            # Matches lines that apparently starts a class or def.

    #@+others
    #@+node:ekr.20161104143211.4: *4* py_scan.initial_state
    def initial_state(self):
        '''Return the initial counts.'''
        return Python_State('', 0)
    #@+node:ekr.20161105140842.3: *4* py_scan.v2_scan_line
    def v2_scan_line(self, s, prev_state):
        '''Update the scan state by scanning s.'''
        trace = False and not g.unitTesting
        context, indent = prev_state.context, prev_state.indent
        assert context in prev_state.contexts, repr(context)
        was_bs_nl = context == 'bs-nl'
        starts = bool(self.starts_pattern.match(s)) and not was_bs_nl
        ws = self.is_ws_line(s) and not was_bs_nl
        if was_bs_nl:
            context = '' # Don't change indent.
        else:
            indent = self.get_int_lws(s)
        i = 0
        while i < len(s):
            progress = i
            ch = s[i]
            if context:
                if ch == '\\':
                    i += 1 # Eat the *next* character too.
                elif context == ch:
                    context = '' # End the string.
                else:
                    pass # Eat the string character later.
            elif ch == '#':
                # The single-line comment ends the line.
                break
            elif s[i:i+3] in ('"""', "'''"):
                context = s[i:i+3]
            elif ch in ('"', "'"):
                context = ch
            elif s[i:] == r'\\\n':
                context = 'bs-nl' # The *next* line is a continuation line.
                break
            elif ch == r'\\':
                i += 1 # Eat the *next* character.
            i += 1
            assert progress < i
        if trace: g.trace(self, s.rstrip())
        return Python_State(context, indent, starts=starts, ws=ws)
    #@-others
#@+node:ekr.20161105100227.1: *3* class Python_State
class Python_State:
    '''A class representing the state of the v2 scan.'''

    def __init__(self, context, indent, starts=False, ws=False):
        '''Ctor for the Python_State class.'''
        self.context = context
        self.contexts = ['', '"""', "'''", '"', "'"]
        self.indent = indent
        self.starts = starts
        self.ws = ws # whitespace line, possibly ending in a comment.
        
    def __repr__(self):
        '''Py_State.__repr__'''
        return '<PyState %r indent: %s starts: %s ws: %s>' % (
            self.context, self.indent, int(self.starts), int(self.ws))
    
    __str__ = __repr__

    #@+others
    #@+node:ekr.20161105100227.3: *4* py_state.comparisons
    def __eq__(self, other):
        '''Return True if the state continues the previous state.'''
        return self.context or self.indent == other.indent

    def __lt__(self, other):
        '''Return True if we should exit one or more blocks.'''
        return not self.context and self.indent < other.indent

    def __gt__(self, other):
        '''Return True if we should enter a new block.'''
        return not self.context and self.indent > other.indent

    def __ne__(self, other): return not self.__eq__(other)

    def __ge__(self, other): return self > other or self == other

    def __le__(self, other): return self < other or self == other
    #@+node:ekr.20161105042258.1: *4* py_state.v2_starts/continues_block
    def v2_continues_block(self, prev_state):
        '''Return True if the just-scanned line continues the present block.'''
        if prev_state.starts:
            # The first line *after* the class or def *is* in the block.
            prev_state.starts = False
            return True
        else:
            return self == prev_state or self.ws

    def v2_starts_block(self, prev_state):
        '''Return True if the just-scanned line starts an inner block.'''
        return not self.context and self.starts and self >= prev_state
    #@-others
#@-others
importer_dict = {
    'class': Py_Importer if v2 else PythonScanner,
    'extensions': ['.py', '.pyw', '.pyi'],
        # mypy uses .pyi extension.
}
#@-leo
