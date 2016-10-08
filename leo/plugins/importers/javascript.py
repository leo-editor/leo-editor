#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18144: * @file importers/javascript.py
'''The @auto importer for JavaScript.'''
import leo.core.leoGlobals as g
import leo.plugins.importers.basescanner as basescanner
import re
new_scanner = True
#@+others
#@+node:ekr.20161007052628.1: ** class Block
class Block:
    '''A class describing a block and its possible rescans.'''

    def __init__(self, lines, simple, base=None):
        '''Ctor for the Block class.'''
        self.base = base
        self.children = []
        self.lines = lines
        self.headline = ''
        self.simple = simple
        
    def __repr__(self):
        return 'Block: simple: %s lines: %s children: %s %s' % (
            int(self.simple), len(self.lines), len(self.children), self.get_headline())
            
    __str__ = __repr__
    
    #@+others
    #@+node:ekr.20161008095930.1: *3* block.get_headline
    def get_headline(self):
        '''Return an approximation to the headline (for tracing).'''
        if self.headline:
            return self.headline.strip()
        elif self.lines:
            for line in self.lines:
                if line.strip():
                    return line.strip()
            return '<all blank lines>'
            
        else:
            return '<no headline>'
    #@+node:ekr.20161008074449.1: *3* block.undent
    def undent(self, n):
        '''Unindent all block lines by n.'''
        if n > 0:
            result = []
            for s in self.lines:
                if s.strip():
                    if s[:n] in ('\t' * n, ' ' * n):
                        result.append(s[n:])
                    else:
                        g.trace('can not happen mixed leading whitespace:', repr(s))
                        return
                else:
                    result.append('\n' if s.endswith('\n') else '')
            self.lines = result
    #@-others
#@+node:ekr.20161004092007.1: ** class ScanState
class ScanState(object):
    '''A class to store and update scanning state.'''
    
    def __init__(self, base=None):
        '''Ctor for ScanState class.'''
        if base:
            curlies, parens = base
        else:
            curlies, parens = 0, 0
        self.base_curlies = curlies
        self.base_parens = parens
        self.context = '' # in ('/', '/*', '"', "'")
        self.curlies = curlies
        self.parens = parens
        # self.stack = []

    def __repr__(self):
        return 'ScanState: %3s context: %2r' % (
            '{' * self.curlies + '(' * self.parens, self.context)
            
    __str__ = __repr__
    
    #@+others
    #@+node:ekr.20161004092056.1: *3* state.continues_block and starts_block
    def continues_block(self):
        '''Return True if the just-scanned lines should be placed in the inner block.'''
        return self.context or self.curlies > self.base_curlies or self.parens > self.base_parens

    def starts_block(self):
        '''Return True if the just-scanned line starts an inner block.'''
        return not self.context and (
            (self.curlies > self.base_curlies or self.parens > self.base_parens))
    #@+node:ekr.20161007053002.1: *3* state.get_base
    def get_base (self):
        '''Return the present counts.'''
        return self.curlies, self.parens
    #@+node:ekr.20161007061524.1: *3* state.scan_block
    def scan_block(self, i, lines):
        '''Scan lines[i:]. Return (i, lines).'''
        trace = False and not g.unitTesting
        state = self
        assert state.starts_block(), i
        if trace: g.trace('START:', state)
        i1 = i
        i += 1
        while i < len(lines):
            progress = i
            state.scan_line(lines[i])
            if state.continues_block():
                i += 1
            else:
                if trace: g.trace('DONE: ', i-i1)
                i += 1 # Add the line that ends the block
                break
            assert progress < i
        # DON'T DO THIS. The last line *must* have the closing parens.
        if 0:
            # Lookahead: add trailing blank lines.
            while i+1 < len(lines) and not lines[i+1].strip():
                i += 1
        return i, lines[i1:i]
    #@+node:ekr.20161004071532.1: *3* state.scan_line
    def scan_line(self, s):
        '''Update the scan state by scanning s.'''
        i = 0
        while i < len(s):
            progress = i
            ch = s[i]
            if self.context:
                if self.context == '/':
                    if ch == '\\':
                        i += 1
                    elif ch == '/':
                        self.context = ''
                            # Regex modifiers won't affect the scan.
                elif self.context == '/*' and s[i:i+2] == '*/':
                    self.context = ''
                    i += 1
                elif self.context == ch:
                    self.context = ''
                else:
                    pass # Continue the present context
            else:
                if s[i:i+2] == '//':
                    break
                elif ch == '/':
                    self.context = '/' # A regex.
                elif s[i:i+2] == '/*':
                    self.context = '/*'
                    i += 1
                elif ch in ('"', "'"):
                    self.context = ch
                elif ch == '{': self.curlies += 1
                elif ch == '}': self.curlies -= 1
                elif ch == '(': self.parens += 1
                elif ch == ')': self.parens -= 1
                # elif ch == '[': self.squares += 1
                # elif ch == ']': self.squares -= 1
            i += 1
            assert progress < i
        # g.trace(repr(self), s.rstrip())
    #@-others
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
        assert hasattr(self, 'strip_blank_lines')
        if new_scanner:
            self.strict = False
            self.atAutoWarnsAboutLeadingWhitespace = False
            self.ignoreBlankLines = True
        else:
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
    #@+node:ekr.20161006164715.1: *3* jss.check
    def check(self, unused_s, parent):
        '''Override of javascript checker.'''
        trace = False and not g.unitTesting
        trace_all_lines = False
        s1 = g.toUnicode(self.file_s, self.encoding)
        s2 = self.trialWrite()
        s1 = self.clean_blank_lines(s1)
        s2 = self.clean_blank_lines(s2)
        # s2 = self.strip_section_references(s2)
        # s1 = self.strip_all(s1)
        # s2 = self.strip_all(s2)
        ok = s1 == s2
        if not ok:
            lines1, lines2 = g.splitLines(s1), g.splitlines(s2)
            n1, n2 = len(lines1), len(lines2)
            g.trace('===== PERFECT IMPORT FAILED =====')
            g.trace('len(s1): %s len(s2): %s' % (n1, n2))
            for i in range(min(n1, n2)):
                line1, line2 = lines1[i], lines2[i]
                if line1 != line2:
                     g.trace('first mismatched line: %s' % i)
                     g.trace(repr(line1))
                     g.trace(repr(line2))
                     break
            else:
                g.trace('all common lines match')
            if trace and trace_all_lines:
                g.trace('===== s1: %s' % parent.h)
                for i, s in enumerate(g.splitLines(s1)):
                    print('%3s %s' % (i+1, s.rstrip()))
                g.trace('===== s2')
                for i, s in enumerate(g.splitLines(s2)):
                    print('%3s %s' % (i+1, s.rstrip()))
        return ok
    #@+node:ekr.20161007093236.1: *3* jss.dump_block & dump_blocks
    def dump_block(self, block):
        '''Dump one block.'''
        lines = block.lines if isinstance(block, Block) else block
        for j, s in enumerate(lines):
            print('    %3s %s' % (j, s.rstrip()))
            
    def dump_blocks(self, blocks, parent):
        '''Dump all blocks, which may be Block instances or lists of strings.'''
        g.trace('blocks in %s...' % parent.h)
        for i, block in enumerate(blocks):
            print('  block: %s' % i)
            self.dump_block(block)

    #@+node:ekr.20161004105734.1: *3* jss.get_headline
    def get_headline(self, block_lines, n):
        '''
        Return the desired headline of the given block:
                
        - Return (1, first-lines) if block is the leading lines.
        - Return (n, function-name) for functions of various forms.
        - Return (n+1, "block n") if no function name can be found.
        '''
        trace = False and not g.unitTesting
        # define common idioms for defining classes and functions.
        # To do: make this table a user option.
        if 1:
            table = ()
        else:
            #@+<< define table >>
            #@+node:ekr.20161008125203.1: *4* << define table >>
            proto1 = re.compile(
                r'\s*Object.create\s*=\s*function.*\n' +
                r'\s*var\s+(\w+)\s*=\s*function',
                re.MULTILINE)
                   
            # Patterns match only at the start.
            table = (
                # Compound statements.
                (0, 'else',   r'\s*else\((.*)\)\s*\{'),
                # (0, 'else'  r'\s*\}\s*else\((.*)\)\s*\{'),
                (0, 'for',    r'\s*for(.*)\{'),
                (0, 'if',     r'\s*if\((.*)\)\s*\{'),
                (0, 'return', r'\s*return'),
                (0, 'switch', r'\s*switch(.*)\{'),
                (0, 'while',  r'\s*while(.*)\{'),
                # Javascript statements,
                (1, '//',        r'\s*\/\/\s*(.*)'),
                (0, 'use strict', r'\"\s*use\s*strict\s*\"\s*;'),
                (0, 'require',    r'\s*require\s*\('),
                # Field/ object names...
                (1, '', r'\s*(\w+\s*\:)'),
                # Classes, functions, vars...
                (0, 'class', r'\s*define\s*\(\[(.*)\]\s*,\s*function\('),
                    # define ( [*], function (
                (1, 'function',  r'\s*function\s+(\w+)'),
                    # function x
                (1, 'function',  r'\s*var\s+(\w[\w\.]*)\s*=\s*function\('),
                    # var x[.y] = function (
                (1, 'function',  r'\s*(\w[\w\.]*)\s*=\s*function\s*\('),
                    # x[.y] = function (
                (1, 'proto', proto1),
                     # Object.create = function
                     #     var x = function
                (0, 'proto', r'\s*Object.create\s*=\s*function\s*\('),
                    # Object.create = function
                (0, 'proto', r'Function\.prototype\.method\s*=\s*function'),
                    # Function.prototype.method = function
                (1, 'var',   r'\s*var\s+(\w[\w\.]*)\s*=\s*new\s+(\w+)'),
                    # var x[.y] = new
                (1, 'var',   r'\s*var\s+(\w[\w\.]*)\s*=\s*{'),
                    # var x[.y] = {
                (1, 'var',   r'\s*var\s+(\w+)\s*;'),
                    # var x;
            )
            #@-<< define table >>
        s = ''.join(block_lines)
        for i, prefix, pattern in table:
            m = re.match(pattern, s)
            if m:
                if trace: g.trace(m.group(0))
                name = prefix + ' ' + (m.group(i) if i else '')
                return n, name.strip()
        # Use the first non-blank line.
        for line in block_lines:
            if line.strip():
                return n, line.strip()
                # A bad idea.
                # i = line.find('(')
                # if i > -1 and line[:i].strip():
                    # return n, line[:i]
                # else:
                    # return n, line.strip()
        # The last fallback.
        return n+1, 'block %s' % (n)
    #@+node:ekr.20161008073629.1: *3* jss.max_blocks_indent
    def max_blocks_indent(self, blocks):
        '''Return the maximum indentation that can be removed from all blocks.'''
        n = 16
        for block in blocks:
            for s in block.lines:
                if s.strip():
                    i = g.find_line_start(s, 0)
                    i, width = g.skip_leading_ws_with_indent(s, i, self.tab_width)
                    n = min(n, width)
        return n
    #@+node:ekr.20161007081548.1: *3* jss.put_block
    def put_block(self, block, parent):
        '''Create nodes for block and all its children.'''
        p = parent.insertAsLastChild()
        p.h = block.headline
        p.b = p.b + ''.join(block.lines)
        for child in block.children:
            self.put_block(child, p)

    #@+node:ekr.20161007150618.1: *3* jss.ref_line
    def ref_line(self, block, sibling_blocks):
        '''Return a reference to the block, given its sibling blocks.'''
        
        def munge(h):
            '''Munge a headline for use in a section reference.'''
            for z in '{}()[]<>':
                h = h.replace(z,'')
            return h.strip()
            
        n = len(sibling_blocks)
        assert n > 0, sibling_blocks
        if n == 1:
            return '@others\n'
        else:
            h = munge(block.lines[0])
            if 0:
                i = 999 # i = sibling_blocks.index(block)
                headlines = [munge(z.lines[0]) for z in sibling_blocks if z != block]
                if h in headlines:
                    h = '%s: %s' % (i, h)
            return g.angleBrackets(h) + '\n'
    #@+node:ekr.20161007151845.1: *3* jss.rescan_block & helpers
    def rescan_block(self, parent_block):
        '''Rescan a non-simple block, possibly creating child blocks.'''
        trace = False and not g.unitTesting
        if len(parent_block.lines) < 10:
            return
        if trace: g.trace('parent_block', parent_block.get_headline())
        # The first and last lines begin and end the block.
        # Only scan the interior lines.
        first_line = parent_block.lines[0]
        last_line = parent_block.lines[-1]
        lines = parent_block.lines[1:-1]
        # Start the state with the proper base.
        state = ScanState(base=parent_block.base)
        blocks, block_lines = [], []
        i = 0
        while i < len(lines):
            progress = i
            line = lines[i]
            state.scan_line(line)
            if state.starts_block():
                block_base = state.get_base()
                if block_lines: blocks.append(Block(block_lines, simple=True))
                i, block_lines = state.scan_block(i, lines)
                blocks.append(Block(block_lines, simple=False, base=block_base))
                block_lines = []
            else:
                block_lines.append(line)
                i += 1
            assert progress < i
        # End the lines.
        if block_lines:
            blocks.append(Block(block_lines, simple=True))
        if 1: # Use @others only.
            self.make_at_others_children(blocks, first_line, last_line, parent_block)
        else:
            # Alas, at present @auto does not honor section references!
            self.make_ref_children(blocks, first_line, last_line, parent_block)
    #@+node:ekr.20161008093819.1: *4* jss.move_leading_blank_lines
    def move_leading_blank_lines(self, blocks):
        '''Move leading blank lines to the preceding block.'''
        if 0:
            g.trace(len(blocks))
            for block in blocks:
                print(block)
        if 0:
            for i, block in enumerate(blocks):
                if i > 0:
                    prev_block = blocks[i-1]
                    while block.lines and not block.lines[0].strip():
                        print('%s -> %s' % (block.get_headline(), prev_block.get_headline()))
                        prev_block.lines.append('\n')
                        block.lines = block.lines[1:]
    #@+node:ekr.20161008091434.1: *4* jss.make_at_others_children
    def make_at_others_children(self, blocks, first_line, last_line, parent_block):
        '''Generate child blocks for all blocks using @others.'''
        if blocks:
            # Create child nodes only if there are enough lines.
            n_lines = sum([len(z.lines) for z in blocks])
            # g.trace('n_lines', n_lines, 'blocks', len(blocks))
            if n_lines > 20: # We want this to be a small number.
                max_indent = self.max_blocks_indent(blocks)
                parent_block.lines = [
                    first_line,
                    '%s@others\n' % (' ' * max_indent),
                    last_line]
                children = []
                for block in blocks:
                    child_block = Block(block.lines,simple=block.simple)
                    child_block.undent(max_indent)
                    children.append(child_block)
                parent_block.children = children
                self.move_leading_blank_lines(children)
                self.rescan_blocks(children)
    #@+node:ekr.20161008091822.1: *4* jss.make_ref_children
    def make_ref_children(self, blocks, first_line, last_line, parent_block):
        '''Generate child blocks for all blocks using section references'''
        complex_blocks = [z for z in blocks if not z.simple]
        if not complex_blocks:
            return
        body, children, headlines = [], [], []
        for block in blocks:
            if block.simple:
                body.extend(block.lines)
            else:
                child_block = Block(block.lines,simple=True)
                children.append(child_block)
                ref = self.ref_line(child_block, complex_blocks)
                # max_indent = self.max_indent(child_block.lines)
                # child_block.lines = self.unindent(child_block.lines, max_indent)
                headlines.append((child_block, ref.strip()),)
                body.append(ref)
        # Update all child headlines.
        for data in headlines:
            child_block, h = data
            child_block.headline = h
        # Replace the block with the child blocks.
        parent_block.lines = [first_line]
        parent_block.lines.extend(body)
        parent_block.lines.append(last_line)
        parent_block.children = children
        # Continue the rescan.
        self.rescan_blocks(blocks)
    #@+node:ekr.20161007075210.1: *3* jss.rescan_blocks
    def rescan_blocks(self, blocks):
        '''Rescan all blocks, finding more blocks and adjusting text.'''
        n = 1
        for block in blocks:
            assert isinstance(block, Block)
            n, h = self.get_headline(block.lines, n)
            block.headline = h
            if not block.simple:
                self.rescan_block(block)
    #@+node:ekr.20161004115934.1: *3* jss.scan
    def scan(self, s1, parent, parse_body=True):
        '''The new, simpler javascript scanner.'''
        trace = False and not g.unitTesting
        trace_blocks = False
        # pylint: disable=arguments-differ
            # parse_body not used.
        lines = g.splitLines(s1)
        if len(lines) < 20:
            if trace: g.trace('small file: %s' % parent.h)
            parent.b = '@language javascript\n' + ''.join(lines)
            return
        self.level, self.name_stack = 0, [] # Updated by rescan_block.
        state = ScanState()
        blocks = []
        block_lines = [] # The lines of the present block.
        # Find all top-level blocks.
        i = 0
        while i < len(lines):
            progress = i
            line = lines[i]
            state.scan_line(line)
            if state.starts_block():
                block_base = state.get_base()
                if block_lines: blocks.append(Block(block_lines, simple=True))
                i, block_lines = state.scan_block(i, lines)
                blocks.append(Block(block_lines, simple=False, base=block_base))
                block_lines = []
            else:
                block_lines.append(line)
                i += 1
            assert progress < i
        # End the blocks properly.
        if block_lines:
            blocks.append(Block(block_lines, simple=True))
        if trace and trace_blocks:
            self.dump_blocks(blocks, parent)
        # Rescan all the blocks, possibly creating more child blocks.
        self.rescan_blocks(blocks)
        parent.b = '@language javascript\n@others\n'
        simple_lines = sum([len(z.lines) if z.simple else 0 for z in blocks])
        if trace: g.trace('simple lines: %s %s' % (simple_lines, parent.h))
        for block in blocks:
            self.put_block(block, parent)
    #@+node:ekr.20161008060711.1: *3* jss.strip_section_references (not used)
    def strip_section_references(self, s):

        pattern = r'^[ \t]*\<\<.*\>\>[ \t]*$'
        return ''.join([z for z in g.splitLines(s) if re.match(pattern,z) is None])
    #@+node:ekr.20161006164257.1: *3* jss.trialWrite
    def trialWrite(self):
        '''Return the trial write for self.root.'''
        at = self.c.atFileCommands
        if 0:
            # Alas, the *actual* @auto write code refuses to write section references!!
            at.write(self.root,
                    nosentinels=True, ### False,
                    perfectImportFlag=False, ###True,
                    scriptWrite=True, ### False,
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
    #@-others
#@-others
importer_dict = {
    'class': JavaScriptScanner,
    'extensions': ['.js',],
}
#@-leo
