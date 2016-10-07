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

    def __init__(self, block_lines, simple):
        '''Ctor for the Block class.'''
        self.children = []
        self.block_lines = block_lines
        self.simple = simple
        
    def __repr__(self):
        return 'Block: simple: %s lines: %s children: %s' % (
            self.simple, len(self.block_lines), len(self.children))
            
    __str__ = __repr__
#@+node:ekr.20161004092007.1: ** class ScanState
class ScanState(object):
    '''A class to store and update scanning state.'''
    #@+others
    #@+node:ekr.20161004092045.1: *3*  state.ctor
    def __init__(self):
        '''Ctor for ScanState class.'''
        self.base_curlies = 0
        self.base_parens = 0
        self.context = '' # in ('/', '/*', '"', "'")
        self.curlies = 0
        self.parens = 0
        self.stack = []
        # self.squares = 0
            # Probably don't want to keep track of these.
            
    def __repr__(self):
        return 'ScanState: top: %s { %s (: %s, context: %2r' % (
            int(self.at_top_level()),
            self.curlies, self.parens, self.context)
            
    __str__ = __repr__
    #@+node:ekr.20161004092056.1: *3* state.continues_block and starts_block
    def continues_block(self):
        '''Return True if the just-scanned lines should be placed in the inner block.'''
        return self.curlies > self.base_curlies or self.parens > self.base_parens

    def starts_block(self):
        '''Return True if the just-scanned line starts an inner block.'''
        return not self.context and (
            (self.curlies > self.base_curlies or self.parens > self.base_parens))
    #@+node:ekr.20161007053002.1: *3* state.base (to be deleted?)
    def base (self):
        '''Return the present counts.'''
        return self.curlies, self.parens
    #@+node:ekr.20161007061524.1: *3* state.scan_block
    def scan_block(self, i, lines):
        '''Scan lines[i:]. Return i, block_lines.'''
        state = self
        assert state.starts_block(), i
        i1 = i
        i += 1
        while i < len(lines):
            progress = i
            state.scan_line(lines[i])
            if state.continues_block():
                i += 1
            else:
                i += 1 # Add the line that ends the block
                break
            assert progress < i
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
        s1 = g.toUnicode(self.file_s, self.encoding)
        s2 = self.trialWrite(s1)
        # s1 = self.strip_all(s1)
        # s2 = self.strip_all(s2)
        ok = s1 == s2
        if not ok:
            g.trace('===== s1: %s' % parent.h)
            for i, s in enumerate(g.splitLines(s1)):
                print('%3s %s' % (i, s.rstrip()))
            g.trace('===== s2')
            for i, s in enumerate(g.splitLines(s2)):
                print('%3s %s' % (i, s.rstrip()))
        return ok
    #@+node:ekr.20161007093236.1: *3* jss.dump_blocks
    def dump_blocks(self, blocks, parent):
        '''Dump all blocks, which may be Block instances or lists of strings.'''
        g.trace('blocks in %s...' % parent.h)
        for i, block in enumerate(blocks):
            print('  block: %s' % i)
            lines = block.block_lines if isinstance(block, Block) else block
            for j, s in enumerate(lines):
                print('    %3s %s' % (j, s.rstrip()))
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
        proto1 = re.compile(
            r'(\s*)Object.create(\s*)=(\s*)function(.*)\n' +
            r'(\s*)var(\s+)(\w+)(\s*)=(\s*)function',
            re.MULTILINE)
               
        # Patterns match only at the start.
        table = (
            # Compound statements.
            (0, 'else',   r'(\s*)else\((.*)\)(\s*)\{'),
            # (0, 'else'    r'(\s*)\}(\s*)else\((.*)\)(\s*)\{'),
            (0, 'for',    r'(\s*)for(.*)\{'),
            (0, 'if',     r'(\s*)if\((.*)\)(\s*)\{'),
            (0, 'switch', r'(\s*)switch(.*)\{'),
            (0, 'while',  r'(\s*)while(.*)\{'),
            # Classes, functions, vars...
            (0, 'class', r'(\s*)define(\s*)\(\[(.*)\](\s*),(\s*)function\('),
                # define ( [*], function (
            (3, 'func',  r'(\s*)function(\s+)(\w+)'),
                # function x
            (3, 'func',  r'(\s*)var(\s+)(\w[\w\.]*)(\s*)=(\s*)function\('),
                # var x[.y] = function (
            (2, 'func',  r'(\s*)(\w[\w\.]*)(\s*)=(\s*)function(\s*)\('),
                # x[.y] = function (
            (7, 'proto', proto1),
                 # Object.create = function
                 #     var x = function
            (0, 'proto', r'(\s*)Object.create(\s*)=(\s*)function(\s*)\('),
                # Object.create = function
            (0, 'proto', r'Function\.prototype\.method(\s*)=(\s*)function'),
                # Function.prototype.method = function
            (3, 'var',   r'(\s*)var(\s+)(\w[\w\.]*)(\s*)=(\s*)new(\s+)(\w+)'),
                # var x[.y] = new
            (3, 'var',   r'(\s*)var(\s+)(\w[\w\.]*)(\s*)=(\s*){'),
                # var x[.y] = {
            (3, 'var',   r'(\s*)var(\s+)(\w+)(\s*);'),
                # var x;
        )
        s = ''.join(block_lines)
        for i, prefix, pattern in table:
            m = re.match(pattern, s)
            if m:
                if trace: g.trace(m.group(0))
                name = prefix + ' ' + (m.group(i) if i else '')
                return n, name.strip()
        return n+1, 'block %s' % (n)
    #@+node:ekr.20161007081548.1: *3* jss.put_block
    def put_block(self, block, parent):
        '''Create nodes for block and all its children.'''
        p = parent.insertAsLastChild()
        p.h = block.headline
        p.b = p.b + ''.join(block.block_lines)
        for child in block.children:
            self.put_block(child, p)
    #@+node:ekr.20161007075210.1: *3* jss.rescan_blocks
    def rescan_blocks(self, blocks):
        '''Rescan all blocks, looking for further substitutions.'''
        # The first and last lines begin and end the block.
        n, result = 1, []
        for block in blocks:
            assert isinstance(block, Block)
            n, h = self.get_headline(block.block_lines, n)
            block.headline = h
            result.append(block)
        return result
    #@+node:ekr.20161004115934.1: *3* jss.scan
    def scan(self, s1, parent, parse_body=True):
        '''The new, simpler javascript scanner.'''
        trace = False and not g.unitTesting
        # pylint: disable=arguments-differ
            # parse_body not used.
        lines = g.splitLines(s1)
        if len(lines) < 20:
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
                if block_lines: blocks.append(Block(block_lines, simple=True))
                i, block_lines = state.scan_block(i, lines)
                blocks.append(Block(block_lines, simple=False))
                block_lines = []
            else:
                block_lines.append(line)
                i += 1
            assert progress < i
        # End the blocks properly.
        if block_lines:
            blocks.append(Block(block_lines, simple=True))
        if trace:
            self.dump_blocks(blocks, parent)
        # Rescan all the blocks in context.
        blocks = self.rescan_blocks(blocks)
        parent.b = '@language javascript\n@others\n'
        for block in blocks:
            self.put_block(block, parent)
    #@-others
#@-others
importer_dict = {
    'class': JavaScriptScanner,
    'extensions': ['.js',],
}
#@-leo
