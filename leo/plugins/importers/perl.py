#@+leo-ver=5-thin
#@+node:ekr.20161027100313.1: * @file importers/perl.py
'''The @auto importer for Perl.'''
import leo.plugins.importers.basescanner as basescanner
import leo.core.leoGlobals as g
#@+others
#@+node:ekr.20161027094537.5: ** class PerlScanState
class PerlScanState(basescanner.ScanState):
    '''A class to store and update scanning state.'''
    # Use the base class ctor.
    #@+others
    #@+node:ekr.20161027094537.11: *3* state.scan_line
    def scan_line(self, s):
        '''Update the scan state by scanning s.'''
        trace = False and not g.unitTesting
        i = 0
        while i < len(s):
            progress = i
            ch, s2 = s[i], s[i:i+2]
            if self.context:
                assert self.context in ('"', "'"), repr(self.context)
                if ch == '\\':
                    i += 1
                elif self.context == ch:
                    self.context = '' # End the string.
                else:
                    pass # Eat the string character later.
            elif s2 == '#':
                break # The single-line comment ends the line.
            elif ch in ('"', "'"):
                self.context = ch
            elif ch == '{': self.curlies += 1
            elif ch == '}': self.curlies -= 1
            elif ch == '(': self.parens += 1
            elif ch == ')': self.parens -= 1
            elif ch == '/': i = self.skip_regex(s, i+1)
            elif s[i:i+3] == 'm//': i = self.skip_regex(s, i+3)
            elif s[i:i+4] == 's///': i = self.skip_regex(s, i+4)
            elif s[i:i+5] == 'tr///': i = self.skip_regex(s, i+5)
            i += 1
            assert progress < i
        if trace:
            g.trace(self, s.rstrip())
    #@+node:ekr.20161027094537.12: *3* state.skip_regex
    def skip_regex(self, s, i):
        '''look ahead for a regex /'''
        trace = False and not g.unitTesting
        if trace: g.trace(repr(s), self.parens)
        assert s[i-1] == '/', repr(s[i])
        i += 1
        while i < len(s) and s[i] in ' \t':
            i += 1
        if i < len(s) and s[i] == '/':
            i += 1
            while i < len(s):
                progress = i
                ch = s[i]
                # g.trace(repr(ch))
                if ch == '\\':
                    i += 2
                elif ch == '/':
                    i += 1
                    break
                else:
                    i += 1
                assert progress < i
        
        if trace: g.trace('returns', i, s[i] if i < len(s) else '')
        return i-1
    #@-others
#@+node:ekr.20161027094537.13: ** class PerlScanner
gen_clean = True
    # None: use @bool js_importer_clean_lws setting
    # True: clean blank lines and regularize indentaion.

gen_refs = False
    # None: use @bool allow_section_references_in_at_auto setting
        # WAS: use @bool js_importer_gen_refs setting
    # True: generate section references.
    # False generate @others

class PerlScanner(basescanner.BaseLineScanner):
    #@+others
    #@+node:ekr.20161027094537.14: *3* perl.__init__
    def __init__(self, importCommands, atAuto, language='perl', alternate_language=None):
        '''The ctor for the PerlScanner class.'''
        # Init the base class.
        ### basescanner.BaseScanner.__init__(
        basescanner.BaseLineScanner.__init__(
            self,
            importCommands,
            atAuto=atAuto,
            language=language,
                # The language is used to set comment delims.
            alternate_language=alternate_language)
                # The language used in the @language directive.
        self.get_settings()
    #@+node:ekr.20161027094537.15: *4* perl.get_settings()
    def get_settings(self):
        '''Set ivars from settings.'''
        c = self.c
        getBool, getInt = c.config.getBool, c.config.getInt
        if gen_clean is None:
            self.gen_clean = getBool('js_importer_clean_lws', default=False)
        else:
            self.gen_clean = gen_clean
        if gen_refs is None:
            self.gen_refs = getBool('allow_section_references_in_at_auto', default=False)
        else:
            self.gen_refs = gen_refs
        self.min_scan_size = getInt('js_importer_min_scan_size') or 0
        self.min_rescan_size = getInt('js_importer_min_rescan_size') or 0
    #@+node:ekr.20161027094537.25: *3* perl.scan
    def scan(self, s1, parent, parse_body=True):
        '''A line-based Perl scanner.'''
        trace = False and not g.unitTesting
        trace_blocks = False
        if trace: g.trace('===== ', self.root.h)
        # pylint: disable=arguments-differ
            # parse_body not used.
        Block = basescanner.Block
        lines = g.splitLines(s1)
        self.state = state = PerlScanState(self.c, self.root)
        if len(lines) < self.min_scan_size:
            if trace: g.trace('small file: %s' % parent.h)
            parent.b = '@language perl\n' + ''.join(lines)
            return
        if self.gen_refs:
            block = Block(lines, simple=False)
            self.rescan_block(block, strip_lines=False)
            parent.b = '@language perl\n'
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
            if trace and trace_blocks:
                self.dump_blocks(blocks, parent)
            # Rescan all the blocks, possibly creating more child blocks.
            self.rescan_blocks(blocks)
            parent.b = '@language perl\n@others\n'
            for block in blocks:
                self.put_block(block, parent)
    #@-others
#@-others
importer_dict = {
    'class': PerlScanner,
    'extensions': ['.pl',],
}
#@-leo
