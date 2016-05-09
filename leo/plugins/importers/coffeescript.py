#@+leo-ver=5-thin
#@+node:ekr.20160505094722.1: * @file importers/coffeescript.py
'''The @auto importer for coffeescript.'''
import re
import leo.core.leoGlobals as g
import leo.plugins.importers.basescanner as basescanner
#@+others
#@+node:ekr.20160505094722.2: ** class CoffeeScriptScanner
class CoffeeScriptScanner(basescanner.BaseScanner):
    
    #@+others
    #@+node:ekr.20160505101118.1: *3* coffee.__init__
    def __init__(self, importCommands, atAuto):
        '''Ctor for CoffeeScriptScanner class.'''
        basescanner.BaseScanner.__init__(self,
            importCommands,
            atAuto=atAuto, language='coffeescript')
        self.strict = False
        self.at_others = []
            # A list of postitions that have an @others directive.
        self.at_tab_width = None
            # Default, overridden later.
        self.def_name = None
        self.errors = 0
        self.tab_width = self.c.tab_width or -4
            # Used to compute lws.
    #@+node:ekr.20160505114047.1: *3* coffee.class_name
    def class_name(self, s):
        '''Return the name of the class in line s.'''
        assert s.startswith('class')
        m = re.match(r'class(\s+)(\w+)',s)
        name = m.group(2) if m else '<**bad class name**>'
        return 'class ' + name
    #@+node:ekr.20160505173347.1: *3* coffee.delete_trailing_lines
    def delete_trailing_lines(self, p):
        '''Delete the trailing lines of p.b and return them.'''
        body_lines, trailing_lines = [], []
        for s in g.splitLines(p.b):
            strip = s.strip()
            if not strip or strip.startswith('#'):
                trailing_lines.append(s)
            else:
                body_lines.extend(trailing_lines)
                body_lines.append(s)
                trailing_lines = []
        # Clear trailing lines if they are all blank.
        if all([not z.strip() for z in trailing_lines]):
            trailing_lines = []
        p.b = ''.join(body_lines)
        return trailing_lines
    #@+node:ekr.20160505111722.1: *3* coffee.lws
    def lws(self, s):
        '''Return the indentation of line s.'''
        return g.computeLeadingWhitespaceWidth(s, self.tab_width)
    #@+node:ekr.20160505170558.1: *3* coffee.move_trailing_lines
    def move_trailing_lines(self, parent):
        '''Move trailing lines into the following node.'''
        prev_lines = []
        last = None
        for p in parent.subtree():
            trailing_lines = self.delete_trailing_lines(p)
            if prev_lines:
                # g.trace('moving lines from', last.h, 'to', p.h)
                p.b = ''.join(prev_lines) + p.b
            prev_lines = trailing_lines
            last = p.copy()
        if prev_lines:
            # These should go after the @others lines in the parent.
            lines = g.splitLines(parent.b)
            for i, s in enumerate(lines):
                if s.strip().startswith('@others'):
                    lines = lines[:i+1] + prev_lines + lines[i+2:]
                    parent.b = ''.join(lines)
                    break
            else:
                # Fall back.
                last.b = last.b + ''.join(prev_lines)
    #@+node:ekr.20160505100917.1: *3* coffee.run
    def run(self, s, parent, parse_body=False, prepass=False):
        '''The top-level code for the coffeescript scanners.'''
        c = self.c
        changed = c.isChanged()
        if prepass:
            return False, []
        self.scan(s, parent, indent=False)
        prefix = '@language coffeescript\n@tabwidth %s\n\n' % (
            self.at_tab_width or -2)
        parent.b =  prefix + parent.b.lstrip()
        self.move_trailing_lines(parent)
        self.undent_nodes(parent)
        ok = self.errors == 0
        # g.app.unitTestDict['result'] = ok
        if self.atAuto and ok:
            for p in parent.self_and_subtree():
                p.clearDirty()
            c.setChanged(changed)
        else:
            parent.setDirty(setDescendentsDirty=False)
            c.setChanged(True)
        return ok
    #@+node:ekr.20160505100958.1: *3* coffee.scan
    def scan(self, s1, parent, indent=True, do_def=True):
        '''Create an outline from Coffeescript (.coffee) file.'''
        # pylint: disable=arguments-differ
        if not s1.strip():
            return
        i, body_lines = 0, []
        lines = g.splitLines(s1)
        level = self.lws(lines[0])
        while i < len(lines):
            progress = i
            s = lines[i]
            strip = s.strip()
            is_class = g.match_word(s, 0, 'class')
            is_def = do_def and not is_class and self.starts_def(s)
            if strip.startswith('#'):
                body_lines.append(s)
                i += 1
            elif is_class or is_def:
                # Important: all undents are done in a later pass.
                child = parent.insertAsLastChild()
                child.h = self.class_name(s) if is_class else self.def_name
                child.b = s
                
                if is_class:
                    # The indentation will be the difference between s and s2
                    if i+1 < len(lines):
                        s2 = ''.join(lines[i+1:])
                        s1_level = self.getLeadingIndent(s, 0, ignoreComments=False)
                        s2_level = self.getLeadingIndent(s2, 0, ignoreComments=True)
                        # g.trace(s1_level, s2_level, s.rstrip())
                    else:
                        self.errors += 1
                        return
                    indent = max(0, s2_level-s1_level)
                    if not self.at_tab_width:
                        self.at_tab_width = -indent
                    child.b = child.b + ' '*indent+'@others\n\n'
                    self.at_others.append(child.copy())
                elif not any([parent == z for z in self.at_others]):
                    self.at_others.append(parent.copy())
                    body_lines.append('@others\n\n')
                block_lines = self.skip_block(lines[i:])
                assert block_lines
                i += len(block_lines)
                s2 = ''.join(block_lines[1:])
                self.scan(s2, child, do_def=not is_def)
            else:
                body_lines.append(s)
                i += 1
            assert progress < i
        parent.b = parent.b + ''.join(body_lines)
    #@+node:ekr.20160505102909.1: *3* coffee.skip_block
    def skip_block(self, lines):
        '''Return all lines of the block that starts at lines[0].'''
        assert lines
        block_lines = [lines[0]]
        level1 = self.lws(lines[0])
        for i, s in enumerate(lines[1:]):
            strip = s.strip()
            level = self.lws(s)
            if not strip or strip.startswith('#') or level > level1:
                block_lines.append(s)
            else:
                break
        return block_lines
    #@+node:ekr.20160505113917.1: *3* coffee.starts_def
    def starts_def(self, s):
        '''
        Return True if line s starts a coffeescript function.
        Sets or clears the def_name ivar.
        '''
        m = re.match('(.+):(.*)->', s) or re.match('(.+)=(.*)->', s)
        self.def_name = m.group(1).strip() if m else None
        return bool(m)
    #@+node:ekr.20160505180032.1: *3* coffee.undent_body
    def undent_body(self, s):
        '''Return the undented body of s.'''
        leading_lines = []
        lines = g.splitLines(s)
        # First, completely undent all leading whitespace or comment lines.
        for s in lines:
            strip = s.strip()
            if not strip or strip.startswith('#'):
                leading_lines.append(strip + '\n')
            else:
                break
        i = len(leading_lines)
        # Don't unindent the def/class line! It prevents later undents.
        s = ''.join(lines[i:])
        s = self.undentBody(s, ignoreComments=True)
            # undentBody is defined in the base class.
        # Remove all blank lines from leading lines.
        while leading_lines and not leading_lines[0].strip():
            leading_lines = leading_lines[1:]
        return ''.join(leading_lines) + s

        
    #@+node:ekr.20160505170639.1: *3* coffee.undent_nodes
    def undent_nodes(self, parent):
        '''Unindent all nodes in parent's tree.'''
        for p in parent.self_and_subtree():
            p.b = self.undent_body(p.b)
    #@-others
#@-others
importer_dict = {
    'class': CoffeeScriptScanner,
    'extensions': ['.coffee', ],
}
#@-leo
