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

    def __init__(self, lines, state, simple=None):
        '''Ctor for the Block class.'''
        assert simple in (True, False), g.callers()
        self.base = state.get_base()
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
        '''Return the block's headline.'''
        if self.headline:
            return self.headline
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
                elif gen_clean:
                    result.append(s)
                else:
                    result.append('\n' if s.endswith('\n') else '')
            self.lines = result
    #@-others
#@+node:ekr.20161004092007.1: ** class ScanState
class ScanState(object):
    '''A class to store and update scanning state.'''
    #@+others
    #@+node:ekr.20161010140018.1: *3* state.ctor & repr
    def __init__(self, c, root):
        '''Ctor for the singleton ScanState class.'''
        # Ivars for traces...
        self.c = c
        self.root = root
        # Ivars representing the scan state...
        self.base_curlies = self.curlies = 0
        self.base_parens = self.parens = 0
        self.context = '' # in ('/*', '"', "'") Comments and regex do *not* create states.
        self.stack = []

    def __repr__(self):
        return 'ScanState: base: %3r state: %3r context: %2r' % (
            '{' * self.base_curlies + '(' * self.base_parens, 
            '{' * self.curlies + '(' * self.parens,
            self.context)
            
    __str__ = __repr__
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
        assert not self.context, repr(self.context)
        return self.curlies, self.parens
    #@+node:ekr.20161006182212.1: *3* state.push & pop
    def pop(self):
        '''Restore the base state from the stack.'''
        self.base_curlies, self.base_parens = self.stack.pop()
        
    def push(self):
        '''Save the base state on the stack and enter a new base state.'''
        self.stack.append((self.base_curlies, self.base_parens),)
        self.base_curlies = self.curlies
        self.base_parens = self.parens

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
        trace = False and self.root.h.endswith('alt.js') and not g.unitTesting
        # if s.strip().startswith('// 1.02 here arrived at'): g.pdb()
        i = 0
        while i < len(s):
            progress = i
            ch, s2 = s[i], s[i:i+2]
            if self.context:
                if self.context == '/*' and s2 == '*/':
                    self.context = ''
                    i += 1
                elif self.context == ch:
                    self.context = ''
                else:
                    pass # Continue the present context
            elif s2 == '//':
                break
            # It's very hard to discover regex's.
            # Instead, we'll just ignore \?
            elif ch == '\\':
                i += 2
            elif s2 == '/*':
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
        if trace and s.strip().startswith('//') and self.continues_block():
            g.trace(self, s.rstrip())
    #@-others
#@+node:ekr.20140723122936.18049: ** class JavaScriptScanner
gen_clean = True
    # None: use @bool js_importer_clean_lws setting
    # True: clean blank lines and regularize indentaion.

gen_refs = False
    # None: use @bool js_importer_gen_refs setting
    # True: generate section references.
    # False generate @others

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
        if new_scanner:
            c = self.c
            if gen_clean is None:
                self.gen_clean = c.config.getBool('js_importer_clean_lws', default=False)
            else:
                self.gen_clean = gen_clean
            if gen_refs is None:
                self.gen_refs = c.config.getBool('js_importer_gen_refs', default=False)
            else:
                self.gen_refs = gen_refs
        else:
            # Set the parser vars.
            self.atAutoWarnsAboutLeadingWhitespace = False
            self.blockCommentDelim1 = '/*'
            self.blockCommentDelim2 = '*/'
            self.blockDelim1 = '{'
            self.blockDelim2 = '}'
            self.hasClasses = True # 2016/01/22
            self.hasDecls = False # 2016/01/22
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
            # Set checker vars
            self.atAutoWarnsAboutLeadingWhitespace = False
            self.strict = False
            self.ignoreBlankLines = True
    #@+node:ekr.20161006164715.1: *3* jss.check
    def check(self, unused_s, parent):
        '''Override of javascript checker.'''
        trace = False and not g.unitTesting
        trace_all_lines = False
        s1 = g.toUnicode(self.file_s, self.encoding)
        s2 = self.trialWrite()
        if self.gen_clean:
            clean = self.strip_lws # strip_all, clean_blank_lines
            s1, s2 = clean(s1), clean(s2)
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

    #@+node:ekr.20161008073629.1: *3* jss.max_blocks_indent
    def max_blocks_indent(self, blocks):
        '''Return the maximum indentation that can be removed from all blocks.'''
        n = 16
        for block in blocks:
            for s in block.lines:
                if s.strip() or not self.gen_clean:
                    i = g.find_line_start(s, 0)
                    i, width = g.skip_leading_ws_with_indent(s, i, self.tab_width)
                    n = min(n, width)
        return n
    #@+node:ekr.20161007081548.1: *3* jss.put_block
    def put_block(self, block, parent, create_child=True):
        '''Create nodes for block and all its children.'''
        if create_child:
            p = parent.insertAsLastChild()
            p.h = block.headline
        else:
            p = parent
        p.b = p.b + ''.join(block.lines)
        for child in block.children:
            self.put_block(child, p)
    #@+node:ekr.20161007150618.1: *3* jss.ref_line
    def ref_line(self, block):
        '''Return a reference to the block.'''
        
        def munge(h):
            '''Munge a headline for use in a section reference.'''
            for z in '<>': # {}()[]
                h = h.replace(z,'')
            return h.strip()

        # Always return a reference
        h = munge(block.get_headline())
        return g.angleBrackets(h) + '\n'
       
    #@+node:ekr.20161007151845.1: *3* jss.rescan_block & helpers
    def rescan_block(self, parent_block, strip_lines=True):
        '''Rescan a non-simple block, possibly creating child blocks.'''
        state = self.state
        trace = False and not g.unitTesting
        if trace: g.trace('len: %3s' % len(parent_block.lines), parent_block.get_headline())
        # This is arbitrary, and so a bit confusing.
        # However, it is about right in practice.
        if len(parent_block.lines) < 10:
            return
        if strip_lines:
            # The first and last lines begin and end the block.
            # Only scan the interior lines.
            first_line = parent_block.lines[0]
            last_line = parent_block.lines[-1]
            lines = parent_block.lines[1:-1]
        else:
            # This is the top-level block, when self.gen_refs is True.
            first_line, last_line = None, None
            lines = parent_block.lines
        state.push() # Set the bases to the present counts.
        blocks, block_lines = [], []
        i = 0
        while i < len(lines):
            progress = i
            line = lines[i]
            state.scan_line(line)
            if state.starts_block():
                base = state.get_base()
                assert base is not None, 'rescan_block'
                if block_lines:
                    # Finish any previous block.
                    blocks.append(Block(block_lines, state, simple=True))
                # This is the *only* reparsing that is done.
                i, block_lines = state.scan_block(i, lines)
                blocks.append(Block(block_lines, state, simple=False))
                block_lines = []
            else:
                block_lines.append(line)
                i += 1
            assert progress < i
        state.pop() # Restore the bases.
        # End the lines.
        if block_lines:
            blocks.append(Block(block_lines, state, simple=True))
        if self.gen_refs: 
            # Generate section references.
            self.make_ref_children(blocks, first_line, last_line, parent_block)
        else:
            # Generate only @others.
            self.make_at_others_children(blocks, first_line, last_line, parent_block)
    #@+node:ekr.20161008091434.1: *4* jss.make_at_others_children
    def make_at_others_children(self, blocks, first_line, last_line, parent_block):
        '''Generate child blocks for all blocks using @others.'''
        trace = False and not g.unitTesting
        state = self.state
        if not blocks:
            return
        if trace:
            g.trace(self.root.h)
            g.trace(parent_block)
            for z in blocks:
                print('%s %s' % (self.max_blocks_indent([z]), z))
        # Create child nodes only if there are enough lines.
        # This is arbitrary, and so a bit confusing.
        # However, it is about right in practice.
        n_lines = sum([len(z.lines) for z in blocks])
        if n_lines < 10: # We want this to be a small number.
            return
        max_indent = 4 if self.gen_clean else 0
            # self.max_blocks_indent(blocks) doesn't necessarily work when gen_clean is False.
        parent_block.lines = [
            first_line,
            '%s@others\n' % (' ' * max_indent),
            last_line]
        children = []
        for block in blocks:
            child_block = Block(block.lines, state, simple=block.simple)
            if self.gen_clean:
                child_undent = self.max_blocks_indent([child_block])
            else:
                child_undent = max_indent
            child_block.undent(child_undent)
            children.append(child_block)
        parent_block.children = children
        self.rescan_blocks(children)
    #@+node:ekr.20161008091822.1: *4* jss.make_ref_children
    def make_ref_children(self, blocks, first_line, last_line, parent_block):
        '''Generate child blocks for all blocks using section references'''
        trace = False and not g.unitTesting and self.root.h.endswith('alt.js')
        state = self.state
        if trace: g.trace('len: %3s base: %5s %s' % (
            len(parent_block.lines), parent_block.base, parent_block.get_headline()))
        body, children = [], []
        for block in blocks:
            if block.simple:
                # This line is never a section reference.
                # g.trace(block.get_headline())
                body.extend(block.lines)
            else:
                base = block.base
                assert base is not None, 'make_ref_children'
                child_block = Block(block.lines, state, simple=False)
                children.append(child_block)
                ref = self.ref_line(child_block)
                child_block.headline = ref.strip()
                if self.gen_clean:
                    # This local calculation is probably good enough.
                    child_undent = self.max_blocks_indent([child_block])
                    child_block.undent(child_undent)
                    body.append(' '*child_undent + ref)
                else:
                    # Don't indent the ref, and don't unindent the children.
                    body.append(ref)
        # Replace the block with the child blocks.
        parent_block.lines = []
        if first_line is not None:
            parent_block.lines.append(first_line)
        parent_block.lines.extend(body)
        if last_line is not None:
            parent_block.lines.append(last_line)
        parent_block.children = children
        # Continue the rescan.
        self.rescan_blocks(children)
    #@+node:ekr.20161007075210.1: *3* jss.rescan_blocks
    def rescan_blocks(self, blocks):
        '''Rescan all blocks, finding more blocks and adjusting text.'''
        for block in blocks:
            assert isinstance(block, Block)
            if not block.headline:
                block.headline = block.get_headline()
            if not block.simple:
                self.rescan_block(block)
    #@+node:ekr.20161004115934.1: *3* jss.scan
    def scan(self, s1, parent, parse_body=True):
        '''The new, simpler javascript scanner.'''
        trace = False and not g.unitTesting
        trace_blocks = False
        if trace: g.trace('===== ', self.root.h)
        # pylint: disable=arguments-differ
            # parse_body not used.
        lines = g.splitLines(s1)
        self.state = state = ScanState(self.c, self.root)
        if len(lines) < 20:
            if trace: g.trace('small file: %s' % parent.h)
            parent.b = '@language javascript\n' + ''.join(lines)
            return
        if self.gen_refs:
            block = Block(lines, state, simple=False)
            self.rescan_block(block, strip_lines=False)
            parent.b = '@language javascript\n'
            self.put_block(block, parent, create_child=False)
        else:
            blocks = []
            block_lines = [] # The lines of the present block.
            # Find all top-level blocks.
            i = 0
            while i < len(lines):
                progress = i
                line = lines[i]
                state.scan_line(line)
                if state.starts_block():
                    base = state.get_base()
                    if block_lines: blocks.append(Block(block_lines, state, simple=True))
                    i, block_lines = state.scan_block(i, lines)
                    blocks.append(Block(block_lines, state, simple=False))
                    block_lines = []
                else:
                    block_lines.append(line)
                    i += 1
                assert progress < i
            # End the blocks properly.
            if block_lines:
                blocks.append(Block(block_lines, state, simple=True))
            if trace and trace_blocks:
                self.dump_blocks(blocks, parent)
            # Rescan all the blocks, possibly creating more child blocks.
            self.rescan_blocks(blocks)
            parent.b = '@language javascript\n@others\n'
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
    #@-others
#@-others
importer_dict = {
    'class': JavaScriptScanner,
    'extensions': ['.js',],
}
#@-leo
