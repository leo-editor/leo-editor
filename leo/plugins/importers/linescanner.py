#@+leo-ver=5-thin
#@+node:ekr.20161108125620.1: * @file importers/linescanner.py
#@+<< linescanner docstring >>
#@+node:ekr.20161108125805.1: ** << linescanner docstring >>
'''
#@@language rest
#@@wrap

**Overview**

New importers, for example, the javascript and perl importers, copy
entire lines from the input file to Leo nodes. This makes the new
importers much less error prone than the legacy
(character-by-character) importers.

New importers *nothing* about parsing. They know only about how to
scan tokens *accurately*. Again, this makes the new importers more
simple and robust than the legacy importers.

New importers are simple to write because two base classes handle all
complex details. Importers override just three methods. The
`scan_line` method is the most important of these. It is
straightforward token-scanning code.

The `LineScanner` classes replaces the horribly complex BaseScanner
class. It encapsulates *all* language-dependent knowledge.

Leo's import infrastructure, in `leoImport.py`, instantiates the
scanner and calls `LS.run`, which calls `LS.scan`.

**Writing a new importer**

Do the following:

1. Create a new subclass of LineScanner.

2. Override the `clean_headline method` and `scan_line` methods.

`scan_line` updates the net number of curly brackets and parens at the end of each line. `scan_line` must compute these numbers *accurately*, taking into account constructs such as multi-line comments, strings and regular expressions.
'''
#@-<< linescanner docstring >>
#@+<< linescanner imports >>
#@+node:ekr.20161108130715.1: ** << linescanner imports >>
import leo.core.leoGlobals as g
if g.isPython3:
    import io
    StringIO = io.StringIO
else:
    import StringIO
    StringIO = StringIO.StringIO
import re
# import time
#@-<< linescanner imports >>
#@+others
#@+node:ekr.20161108155730.1: ** class Importer
class Importer(object):
    '''
    The new, unified, simplified, interface to Leo's importer code.
    
    Unifies the old ImportController and Scanner classes.
    
    Eventually, all importers will create use this class.
    '''
    
    #@+others
    #@+node:ekr.20161108155925.1: *3* i.__init__
    #@@nobeautify

    def __init__(self,
        c, ### More logical than previous importCommands, 
        atAuto, # True when called from @auto logic.
        language = None, # For @language directive.
        name = None, # The kind of importer, usually the same as language
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
        self.scanner = None
            # Subclasses will override 
        ### self.state = scanner
            # A scanner instance.
        self.strict = strict
            # True: leading whitespace is significant.
        assert scanner, 'Caller must provide a LineScanner instance'

        # Set from ivars...
        self.has_decls = name not in ('xml', 'org-mode', 'vimoutliner')
        self.is_rst = name in ('rst',)
        self.tree_type = ic.treeType # '@root', '@file', etc.
        
        # Constants...
        ### new_ctors
        self.gen_refs = name in ('javascript',)
        self.gen_clean = name in ('python',)
        ###
        # self.gen_clean = gen_clean
        # self.gen_refs = gen_refs
        self.tab_width = None # Must be set in run()

        # The ws equivalent to one tab.
        # self.tab_ws = ' ' * abs(self.tab_width) if self.tab_width < 0 else '\t'

        # Settings...
        self.at_auto_warns_about_leading_whitespace = c.config.getBool(
            'at_auto_warns_about_leading_whitespace')
        self.warn_about_underindented_lines = True
        # self.at_auto_separate_non_def_nodes = False

        # State vars.
        self.errors = 0
        ic.errors = 0 # Required.
        self.ws_error = False
        self.root = None
    #@+node:ekr.20161108131153.3: *3* i.check & helpers
    def check(self, unused_s, parent):
        '''ImportController.check'''
        trace = False and not g.unitTesting
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
            if ok and not g.unitTesting:
                g.es_print(
                    'indentation error: leading whitespace changed in:',
                    self.root.h)
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
    #@+node:ekr.20161108131153.4: *4* i.clean_blank_lines
    def clean_blank_lines(self, s):
        '''Remove all blanks and tabs in all blank lines.'''
        result = ''.join([
            z if z.strip() else z.replace(' ','').replace('\t','')
                for z in g.splitLines(s)
        ])
        return result
    #@+node:ekr.20161108131153.5: *4* i.strip_*
    def strip_all(self, s):
        '''Strip blank lines and leading whitespace from all lines of s.'''
        return self.strip_lws(self.strip_blank_lines(s))

    def strip_blank_lines(self, s):
        '''Strip all blank lines from s.'''
        return ''.join([z for z in g.splitLines(s) if z.strip()])

    def strip_lws(self, s):
        '''Strip leading whitespace from all lines of s.'''
        return ''.join([z.lstrip() for z in g.splitLines(s)])
    #@+node:ekr.20161108131153.6: *4* i.trial_write
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
    #@+node:ekr.20161108131153.7: *3* i.Overrides
    # These can be overridden in subclasses.
    #@+node:ekr.20161108131153.8: *4* i.adjust_parent
    def adjust_parent(self, parent, headline):
        '''Return the effective parent.

        This is overridden by the RstScanner class.'''
        return parent
    #@+node:ekr.20161108131153.9: *4* i.clean_headline
    def clean_headline(self, s):
        '''
        Return the cleaned version headline s.
        Will typically be overridden in subclasses.
        '''
        return s.strip()
    #@+node:ekr.20161108131153.10: *3* i.run (entry point) & helpers
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
        ###
        self.v2_gen_lines(s, parent)
        # if g.gen_v2:
            # self.v2_gen_lines(s, parent)
        # else:
            # self.v1_scan(s, parent)
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
    #@+node:ekr.20161108131153.11: *4* i.check_blanks_and_tabs
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
    #@+node:ekr.20161108131153.12: *4* i.insert_ignore_directive
    def insert_ignore_directive(self, parent):
        c = self.c
        parent.b = parent.b.rstrip() + '\n@ignore\n'
        if g.unitTesting:
            g.app.unitTestDict['fail'] = g.callers()
        elif parent.isAnyAtFileNode() and not parent.isAtAutoNode():
            g.warning('inserting @ignore')
            c.import_error_nodes.append(parent.h)
    #@+node:ekr.20161108131153.13: *4* i.post_pass
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
                p.b = self.undent(p)
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
    #@+node:ekr.20161108131153.14: *4* i.regularize_whitespace
    def regularize_whitespace(self, s):
        '''
        Regularize leading whitespace in s:
        Convert tabs to blanks or vice versa depending on the @tabwidth in effect.
        '''
        trace = False and not g.unitTesting
        trace_lines = False
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
            if not g.unitTesting:
                # g.es_print('Warning: Intermixed tabs and blanks in', fn)
                # g.es_print('Perfect import test will ignoring leading whitespace.')
                g.es_print('changed leading %s to %s in %s line%s in %s' % (
                    kind2, kind, count, g.plural(count), fn))
            if g.unitTesting: # Sets flag for unit tests.
                self.report('changed %s lines' % count) 
        return ''.join(result)
    #@+node:ekr.20161108131153.15: *3* i.Utils
    #@+node:ekr.20161108131153.16: *4* i.Common Utils
    #@+node:ekr.20161108131153.17: *4* i.get_lws
    def get_lws(self, s):
        '''Return the characters of the lws of s.'''
        m = re.match(r'(\s*)', s)
        return m.group(0) if m else ''
    #@+node:ekr.20161108131153.18: *4* i.Messages
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
    #@+node:ekr.20161108131153.19: *4* i.undent & helper
    def undent(self, p):
        '''Remove maximal leading whitespace from the start of all lines.'''
        trace = False and not g.unitTesting # and self.root.h.find('main') > -1
        lines = g.splitLines(p.b)
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
    #@+node:ekr.20161108131153.20: *5* common_lws
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
    #@+node:ekr.20161108131153.21: *4* i.underindented_comment/line
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
    #@+node:ekr.20161108160409.1: *3* i.v2_gen_lines & helpers
    def v2_gen_lines(self, s, parent):
        '''Parse all lines of s into parent and created child nodes.'''
        trace = False and not g.unitTesting and self.root.h.endswith('.py')
        scanner = self.scanner
        tail_p = None
        prev_state = scanner.initial_state()
        stack = [Target(parent, prev_state)]
        for line in g.splitLines(s):
            new_state = scanner.v2_scan_line(line, prev_state)
            if trace: g.trace('%s tail: %s %r' % (
                new_state, int(bool(tail_p)), line))
            # if trace: g.trace('%s tail: %s +: %s =: %s %r' % (
                # new_state, int(bool(tail_p)), int(starts), int(continues), line))
            if new_state.v2_starts_block(prev_state):
                tail_p = None
                self.start_new_block(line, new_state, stack)
            elif new_state.v2_continues_block(prev_state):
                p = tail_p or stack[-1].p
                p.b = p.b + line
            else:
                tail_p = self.end_block(line, new_state, stack)
            prev_state = new_state
        # Put directives at the end, so as not to interfere with shebang lines, etc.
        parent.b = parent.b + ''.join(self.root_directives())
    #@+node:ekr.20161108160409.2: *4* i.cut_stack
    def cut_stack(self, new_state, stack):
        '''Cut back the stack until stack[-1] matches new_state.'''
        trace = False and not g.unitTesting and self.root.h.endswith('.py')
        trace_stack = True
        if trace and trace_stack:
            print('\n'.join([repr(z) for z in stack]))
        assert stack # Fail on entry.
        while stack:
            top_state = stack[-1].state
            if new_state < top_state:
                if trace: g.trace('new_state < top_state', top_state)
                if len(stack) == 1:
                    break
                else:
                    stack.pop() 
            elif top_state == new_state:
                if trace: g.trace('new_state == top_state', top_state)
                break
            else:
                if trace: g.trace('OVERSHOOT: new_state > top_state', top_state)
                    # Can happen with valid javascript programs.
                break
        assert stack # Fail on exit.
        if trace: g.trace('new target.p:', stack[-1].p.h)
    #@+node:ekr.20161108160409.3: *4* i.end_block & helper
    def end_block(self, line, new_state, stack):
        # The block is ending. Add tail lines until the start of the next block.
        is_python = self.name == 'python'
        p = stack[-1].p # Put the closing line in *this* node.
        if is_python or self.gen_refs:
            tail_p = None
        else:
            tail_p = p # Put trailing lines in this node.
        if is_python:
            self.end_python_block(line, new_state, stack)
        else:
            p.b = p.b + line
            self.cut_stack(new_state, stack)
        ### This doesn't work
        ### if not self.gen_refs:
        ###    tail_p = stack[-1].p
        return tail_p
    #@+node:ekr.20161108160409.4: *5* i.ends_python
    def end_python_block(self, line, new_state, stack):
        '''Handle lines at a lower level.'''
        # Unlike other languages, *this* line not only *ends*
        # a block, but *starts* a block.
        self.cut_stack(new_state, stack)
        target = stack[-1]
        h = self.clean_headline(line)
        child = self.v2_create_child_node(target.p.parent(), line, h)
        stack.pop()
            ###### Is this where the line got lost?
        stack.append(Target(child, new_state))
    #@+node:ekr.20161108160409.5: *4* i.root_directives
    def root_directives(self):
        '''Return the proper directives for the root node p.'''
        return [
            '@language %s\n' % self.language,
            '@tabwidth %d\n' % self.tab_width,
        ]
    #@+node:ekr.20161108160409.6: *4* i.start_new_block
    def start_new_block(self, line, new_state, stack):
        '''Create a child node and update the stack.'''
        target=stack[-1]
        # Insert the reference in *this* node.
        h = self.v2_gen_ref(line, target.p, target)
        # Create a new child and associated target.
        child = self.v2_create_child_node(target.p, line, h)
        stack.append(Target(child, new_state))
    #@+node:ekr.20161108160409.7: *4* i.v2_create_child_node
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
    #@+node:ekr.20161108160409.8: *4* i.v2_gen_ref
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
#@+node:ekr.20161108155143.1: ** class LineScanner
class LineScanner(object):
    '''
    A class to scan lines.
    
    Subclasses overide *both* the scan_line and v2_scan_line methods.
    These methods work with the various X_ScanState classes.
    '''

    #@+others
    #@+node:ekr.20161108155143.2: *3* scanner.__init__ & __repr__
    def __init__(self, c, language=None):
        '''Ctor for the LineScanner class.'''
        self.c = c
        self.language = language 
        self.comment_delims = g.set_delims_from_language(language) if language else None
            # For general_line_scanner
        self.tab_width = c.tab_width
        ###
        # if gen_v2:
            # pass
        # else:
            # self.context = '' # Represents cross-line constructs.
            # self.base_curlies = self.curlies = 0
            # self.stack = []

    def __repr__(self):
        '''LineScanner.__repr__'''
        return 'LineScanner: base: %r now: %r context: %2r' % (
            '{' * self.base_curlies,
            '{' * self.curlies, self.context)
            
    __str__ = __repr__
    #@+node:ekr.20161108155143.3: *3* scanner.get_lws
    def get_lws(self, s):
        '''Return the the lws (a number) of line s.'''
        return g.computeLeadingWhitespaceWidth(s, self.c.tab_width)
    #@+node:ekr.20161108155143.4: *3* scanner.match
    def match(self, s, i, pattern):
        '''Return True if the pattern matches at s[i:]'''
        return s[i:i+len(pattern)] == pattern
    #@+node:ekr.20161108155143.5: *3* scanner.general_scan_line
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
        return ScanState(self.context, self.curlies)
    #@+node:ekr.20161108155143.6: *3* scanner.initial_state
    def initial_state(self):
        '''Return the initial counts.'''
        assert False, 'Subclasses must override LineScanner.initial_state.'
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

    def __ne__(self, other): return not self.__eq__(other)

    def __ge__(self, other): return self > other or self == other

    def __le__(self, other): return self < other or self == other
    #@+node:ekr.20161105180504.1: *3* ScanState: v2.starts/continues_block
    def v2_continues_block(self, prev_state):
        '''Return True if the just-scanned lines should be placed in the inner block.'''
        return self == prev_state

    def v2_starts_block(self, prev_state):
        '''Return True if the just-scanned line starts an inner block.'''
        return self > prev_state
    #@-others

#@+node:ekr.20161108155158.1: ** class Target
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
        return 'Target: state: %s p: %s' % (
            self.state, g.shortFileName(self.p.h))
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
