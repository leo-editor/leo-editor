#@+leo-ver=5-thin
#@+node:ekr.20150521115018.1: * @file leoBeautify.py
'''Leo's beautification classes.'''
#@+<< imports >>
#@+node:ekr.20150530081336.1: ** << imports >>
try:
    import leo.core.leoGlobals as g
except ImportError:
    # Allow main() to run in any folder containing leoGlobals.py
    # pylint: disable=relative-import
    import leoGlobals as g
    # Create a dummy decorator.

    def command(func):
        return func

    g.command = command
import ast
# import itertools
import optparse
import os
import sys
import time
import token
import tokenize
#@-<< imports >>
#@+others
#@+node:ekr.20150528131012.1: **  commands (leoBeautifier.py)
#@+node:ekr.20150528131012.3: *3* beautify-c
@g.command('beautify-c')
@g.command('pretty-print-c')
def beautifyCCode(event):
    '''Beautify all C code in the selected tree.'''
    c = event.get('c')
    if not c: return
    if should_kill_beautify(c.p):
        return
    u, undoType = c.undoer, 'beautify-c'
    pp = CPrettyPrinter(c)
    u.beforeChangeGroup(c.p, undoType)
    dirtyVnodeList = []
    changed = False
    for p in c.p.self_and_subtree():
        if g.scanForAtLanguage(c, p) == "c":
            bunch = u.beforeChangeNodeContents(p)
            s = pp.indent(p)
            if p.b != s:
                # g.es('changed: %s' % (p.h))
                p.b = s
                p.v.setDirty()
                dirtyVnodeList.append(p.v)
                u.afterChangeNodeContents(p, undoType, bunch)
                changed = True
    if changed:
        u.afterChangeGroup(c.p, undoType,
            reportFlag=False, dirtyVnodeList=dirtyVnodeList)
    c.bodyWantsFocus()
#@+node:ekr.20150528131012.4: *3* beautify-node
@g.command('beautify-node')
@g.command('pretty-print-node')
def prettyPrintPythonNode(event):
    '''Beautify a single Python node.'''
    c = event.get('c')
    if not c: return
    pp = PythonTokenBeautifier(c)
    if g.scanForAtLanguage(c, c.p) == "python":
        pp.prettyPrintNode(c.p)
    pp.end_undo()
    # pp.print_stats()
#@+node:ekr.20150528131012.5: *3* beautify-tree
@g.command('beautify-tree')
@g.command('pretty-print-tree')
def beautifyPythonTree(event):
    '''Beautify the Python code in the selected outline.'''
    c = event.get('c')
    p0 = event.get('p0')
    is_auto = bool(p0)
    p0 = p0 or c.p
    if should_kill_beautify(p0):
        return
    t1 = time.time()
    pp = PythonTokenBeautifier(c)
    prev_changed = 0
    for p in p0.self_and_subtree():
        if g.scanForAtLanguage(c, p) == "python":
            if p.isAnyAtFileNode():
                # Report changed nodes in previous @<file> node.
                if pp.n_changed_nodes != prev_changed and not is_auto:
                    if not g.unitTesting:
                        n = pp.n_changed_nodes - prev_changed
                        g.es_print('beautified %s node%s' % (
                            n, g.plural(n)))
                prev_changed = pp.n_changed_nodes
                if not is_auto:
                    g.es_print(p.h)
            pp.prettyPrintNode(p)
    # Report any nodes in the last @<file> tree.
    if not g.unitTesting:
        if pp.n_changed_nodes != prev_changed and not is_auto:
            n = pp.n_changed_nodes - prev_changed
            g.es_print('beautified %s node%s' % (
                n, g.plural(n)))
    pp.end_undo()
    t2 = time.time()
    # pp.print_stats()
    if not g.unitTesting:
        if is_auto:
            if pp.n_changed_nodes > 0:
                g.es_print('auto-beautified %s node%s in\n%s' % (
                    pp.n_changed_nodes,
                    g.plural(pp.n_changed_nodes),
                    p0.h))
        else:
            g.es_print('beautified total %s node%s in %4.2f sec.' % (
                pp.n_changed_nodes, g.plural(pp.n_changed_nodes), t2 - t1))
#@+node:ekr.20150528091356.1: **  top-level functions (leoBeautifier.py)
#@+node:ekr.20170202095153.1: *3* compare_ast (diabled)
# http://stackoverflow.com/questions/3312989/
# elegant-way-to-test-python-asts-for-equality-not-reference-or-object-identity

def compare_ast(node1, node2):
    return True
    # Can hang, for mysterious reasons.
        # if type(node1) is not type(node2):
            # return False
        # if isinstance(node1, ast.AST):
            # # Py 2/3: Use items, not itertool.iteritems.
            # for k, v in vars(node1).items():
                # if k in ('lineno', 'col_offset', 'ctx'):
                    # continue
                # if not compare_ast(v, getattr(node2, k)):
                    # return False
            # return True
        # elif isinstance(node1, list):
            # return all(itertools.starmap(compare_ast, zip(node1, node2)))
                # # Py 2/3: Use zip, not itertools.izip.
        # else:
            # return node1 == node2
#@+node:ekr.20150524215322.1: *3* dump_tokens & dump_token
def dump_tokens(tokens, verbose=True):
    last_line_number = 0
    for token5tuple in tokens:
        last_line_number = dump_token(last_line_number, token5tuple, verbose)

def dump_token(last_line_number, token5tuple, verbose):
    '''Dump the given input token.'''
    t1, t2, t3, t4, t5 = token5tuple
    name = token.tok_name[t1].lower()
    val = str(t2) # can fail
    srow, scol = t3
    erow, ecol = t4
    line = str(t5) # can fail
    if last_line_number != srow:
        if verbose:
            print("\n---- line: %3s %3s %r" % (srow, erow, line))
        else:
            print('%3s %7s %r' % (srow, name, line))
    if verbose:
        if name in ('dedent', 'indent', 'newline', 'nl'):
            val = repr(val)
        # print("%10s %3d %3d %-8s" % (name,scol,ecol,val))
        # print('%10s srow: %s erow: %s %s' % (name,srow,erow,val))
        print('%10s %s' % (name, val))
            # line[scol:ecol]
    last_line_number = srow
    return last_line_number
#@+node:ekr.20170202095522.1: *3* fail (not used)
def fail(node1, node2, tag):
    '''Report a failed mismatch in the beautifier. This is a bug.'''
    name1 = node1.__class__.__name__
    name2 = node2.__class__.__name__
    format = 'compare_ast failed: %s: %s %s %r %r'
    if name1 == 'str':
        print(format % (tag, name1, name2, node1, node2))
    elif name1 == 'Str':
        print(format % (tag, name1, name2, node1.s, node2.s))
    elif 1:
        format = 'compare_ast failed: %s: %s %s\n%r\n%r'
        print(format % (tag, name1, name2, node1, node2))
    else:
        format = 'compare_ast failed: %s: %s %s\n%r\n%r\n%r %r'
        attr1 = getattr(node1, 'lineno', '<no lineno>')
        attr2 = getattr(node2, 'lineno', '<no lineno>')
        print(format % (tag, name1, name2, node1, node2, attr1, attr2))
#@+node:ekr.20150530061745.1: *3* main (external entry) & helpers
def main():
    '''External entry point for Leo's beautifier.'''
    t1 = time.time()
    base = g.os_path_abspath(os.curdir)
    files, options = scan_options()
    for path in files:
        path = g.os_path_finalize_join(base, path)
        beautify(options, path)
    print('beautified %s files in %4.2f sec.' % (len(files), time.time() - t1))
#@+node:ekr.20150601170125.1: *4* beautify (stand alone)
def beautify(options, path):
    '''Beautify the file with the given path.'''
    fn = g.shortFileName(path)
    s, e = g.readFileIntoString(path)
    if not s:
        return
    print('beautifying %s' % fn)
    s1 = g.toEncodedString(s)
    node1 = ast.parse(s1, filename='before', mode='exec')
    readlines = g.ReadLinesClass(s).next
    tokens = list(tokenize.generate_tokens(readlines))
    beautifier = PythonTokenBeautifier(c=None)
    beautifier.delete_blank_lines = not options.keep
    s2 = beautifier.run(tokens)
    s2_e = g.toEncodedString(s2)
    node2 = ast.parse(s2_e, filename='before', mode='exec')
    if compare_ast(node1, node2):
        f = open(path, 'wb')
        f.write(s2_e)
        f.close()
    else:
        print('failed to beautify %s' % fn)
#@+node:ekr.20150601162203.1: *4* scan_options & helper
def scan_options():
    '''Handle all options. Return a list of files.'''
    # This automatically implements the --help option.
    usage = "usage: python leoBeautify -m file1, file2, ..."
    parser = optparse.OptionParser(usage=usage)
    add = parser.add_option
    add('-d', '--debug', action='store_true', dest='debug',
        help='print the list of files and exit')
    add('-k', '--keep-blank-lines', action='store_true', dest='keep',
        help='keep-blank-lines')
    # Parse the options.
    options, files = parser.parse_args()
    if options.debug:
        # Print the list of files and exit.
        g.trace('files...', files)
        sys.exit(0)
    return files, options
#@+node:ekr.20150531042746.1: *3* munging leo directives
#@+node:ekr.20150529084212.1: *4* comment_leo_lines (leoBeautifier.py)
def comment_leo_lines(p):
    '''Replace lines with Leonine syntax with special comments.'''
    # Choose the comment string so it appears nowhere in s.
    s0 = p.b
    n = 5
    while s0.find('#' + ('!' * n)) > -1:
        n += 1
    comment = '#' + ('!' * n)
    # Create a dict of directives.
    d = {}
    for z in g.globalDirectiveList:
        d[z] = True
    # Convert all Leonine lines to special comments.
    i, lines, result = 0, g.splitLines(s0), []
    while i < len(lines):
        progress = i
        s = lines[i]
        # Comment out any containing a section reference.
        j = s.find('<<')
        k = s.find('>>') if j > -1 else -1
        if -1 < j < k:
            result.append(comment + s)
            # Generate a properly-indented pass line.
            j2 = g.skip_ws(s, 0)
            result.append('%spass\n' % (' ' * j2))
        elif s.lstrip().startswith('@'):
            # Comment out all other Leonine constructs.
            if starts_doc_part(s):
                # Comment the entire doc part, until @c or @code.
                result.append(comment + s)
                i += 1
                while i < len(lines):
                    s = lines[i]
                    result.append(comment + s)
                    i += 1
                    if ends_doc_part(s):
                        break
            else:
                j = g.skip_ws(s, 0)
                assert s[j] == '@'
                j += 1
                k = g.skip_id(s, j, chars='-')
                if k > j:
                    word = s[j: k]
                    if word == 'others':
                        # Remember the original @others line.
                        result.append(comment + s)
                        # Generate a properly-indented pass line.
                        result.append('%spass\n' % (' ' * (j - 1)))
                    else:
                        # Comment only Leo directives, not decorators.
                        result.append(comment + s if word in d else s)
                else:
                    result.append(s)
        else:
            # A plain line.
            result.append(s)
        if i == progress:
            i += 1
    # g.trace(''.join(result))
    return comment, ''.join(result)
#@+node:ekr.20150531042830.1: *4* starts_doc_part & ends_doc_part
def starts_doc_part(s):
    '''Return True if s word matches @ or @doc.'''
    for delim in ('@\n', '@doc\n', '@ ', '@doc '):
        if s.startswith(delim):
            return True
    return False

def ends_doc_part(s):
    '''Return True if s word matches @c or @code.'''
    for delim in ('@c\n', '@code\n', '@c ', '@code '):
        if s.startswith(delim):
            return True
    return False
#@+node:ekr.20150529095117.1: *4* uncomment_leo_lines
def uncomment_leo_lines(comment, p, s0):
    '''Reverse the effect of comment_leo_lines.'''
    lines = g.splitLines(s0)
    i, result = 0, []
    # g.trace(s0)
    while i < len(lines):
        progress = i
        s = lines[i]
        i += 1
        if s.find(comment) == -1:
            # A regular line.
            result.append(s)
        else:
            # One or more special lines.
            i = uncomment_special_lines(comment, i, lines, p, result, s)
        assert progress < i
    return ''.join(result).rstrip() + '\n'
#@+node:ekr.20150531041720.1: *4* uncomment_special_line & helpers
def uncomment_special_lines(comment, i, lines, p, result, s):
    '''
    s is a line containing the comment delim.
    i points at the *next* line.
    Handle one or more lines, appending stripped lines to result.
    '''
    s = s.lstrip().lstrip(comment)
    if starts_doc_part(s):
        result.append(s)
        while i < len(lines):
            s = lines[i].lstrip().lstrip(comment)
            i += 1
            result.append(s)
            if ends_doc_part(s):
                break
        return i
    else:
        j = s.find('<<')
        k = s.find('>>') if j > -1 else -1
        if -1 < j < k or s.find('@others') > -1:
            # A section reference line or an @others line.
            # Such lines are followed by a pass line.
            # The beautifier may insert blank lines before the pass line.
            kind = 'section ref' if -1 < j < k else '@others'
            # Restore the original line, including leading whitespace.
            result.append(s)
            # Skip blank lines.
            while i < len(lines) and not lines[i].strip():
                i += 1
            # Skip the pass line.
            if i < len(lines) and lines[i].lstrip().startswith('pass'):
                i += 1
            else:
                g.trace('*** no pass after %s: %s' % (kind, p.h))
        else:
            # A directive line.
            result.append(s)
        return i
#@+node:ekr.20150602154951.1: *3* should_beautify
def should_beautify(p):
    '''
    Return True if @beautify is in effect for node p.
    Ambiguous @beautify
    '''
    for p2 in p.self_and_parents():
        d = g.get_directives_dict(p2)
        if 'killbeautify' in d:
            return False
        elif 'beautify' in d and 'nobeautify' in d:
            if p == p2:
                # honor whichever comes first.
                for line in g.splitLines(p2.b):
                    if line.startswith('@beautify'):
                        return True
                    elif line.startswith('@nobeautify'):
                        return False
                g.trace('can not happen', p2.h)
                return False
            else:
                # The ambiguous node has no effect.
                # Look up the tree.
                pass
        elif 'beautify' in d:
            return True
        elif 'nobeautify' in d:
            # This message would quickly become annoying.
            # self.skip_message('@nobeautify',p)
            return False
    # The default is to beautify.
    return True
#@+node:ekr.20150602204440.1: *3* should_kill_beautify
def should_kill_beautify(p):
    '''Return True if p.b contains @killbeautify'''
    return 'killbeautify' in g.get_directives_dict(p)
#@+node:ekr.20150527143619.1: *3* show_lws
def show_lws(s):
    '''Show leading whitespace in a convenient format.'''
    return repr(s) if s.strip(' ') else len(s)
#@+node:ekr.20150521114057.1: *3* test_beautifier (prints stats)
def test_beautifier(c, h, p, settings):
    '''Test Leo's beautifier code'''
    if not p:
        g.trace('not found: %s' % h)
        return
    s = g.getScript(c, p,
            useSelectedText=False,
            forcePythonSentinels=True,
            useSentinels=False)
    g.trace(h.strip())
    t1 = time.time()
    s1 = g.toEncodedString(s)
    node1 = ast.parse(s1, filename='before', mode='exec')
    t2 = time.time()
    readlines = g.ReadLinesClass(s).next
    tokens = list(tokenize.generate_tokens(readlines))
    t3 = time.time()
    beautifier = PythonTokenBeautifier(c)
    keep_blank_lines = settings.get('tidy-keep-blank-lines')
    if keep_blank_lines is not None:
        beautifier.delete_blank_lines = not keep_blank_lines
    s2 = beautifier.run(tokens)
    t4 = time.time()
    try:
        s2_e = g.toEncodedString(s2)
        node2 = ast.parse(s2_e, filename='before', mode='exec')
        ok = compare_ast(node1, node2)
    except Exception:
        g.es_exception()
        ok = False
    t5 = time.time()
    #  Update the stats
    beautifier.n_input_tokens += len(tokens)
    beautifier.n_output_tokens += len(beautifier.code_list)
    beautifier.n_strings += len(s2)
    beautifier.parse_time += (t2 - t1)
    beautifier.tokenize_time += (t3 - t2)
    beautifier.beautify_time += (t4 - t3)
    beautifier.check_time += (t5 - t4)
    beautifier.total_time += (t5 - t1)
    if settings.get('input_string'):
        print('==================== input_string')
        for i, z in enumerate(g.splitLines(s)):
            print('%4s %s' % (i + 1, z.rstrip()))
    if settings.get('input_lines'):
        print('==================== input_lines')
        dump_tokens(tokens, verbose=False)
    if settings.get('input_tokens'):
        print('==================== input_tokens')
        dump_tokens(tokens, verbose=True)
    if settings.get('output_tokens'):
        print('==================== code_list')
        for i, z in enumerate(beautifier.code_list):
            print('%4s %s' % (i, z))
    if settings.get('output_string'):
        print('==================== output_string')
        for i, z in enumerate(g.splitLines(s2)):
            if z == '\n':
                print('%4s' % (i + 1))
            elif z.rstrip():
                print('%4s %s' % (i + 1, z.rstrip()))
            else:
                print('%4s %r' % (i + 1, str(z)))
    if settings.get('stats'):
        beautifier.print_stats()
    if not ok:
        print('*************** fail: %s ***************' % (h))
    return beautifier
        # For statistics.
#@+node:ekr.20110917174948.6903: ** class CPrettyPrinter
class CPrettyPrinter(object):
    #@+others
    #@+node:ekr.20110917174948.6904: *3* cpp.__init__
    def __init__(self, c):
        '''Ctor for CPrettyPrinter class.'''
        self.c = c
        self.brackets = 0
            # The brackets indentation level.
        self.p = None
            # Set in indent.
        self.parens = 0
            # The parenthesis nesting level.
        self.result = []
            # The list of tokens that form the final result.
        self.tab_width = 4
            # The number of spaces in each unit of leading indentation.
    #@+node:ekr.20110917174948.6911: *3* cpp.indent & helpers
    def indent(self, p, toList=False, giveWarnings=True):
        '''Beautify a node with @language C in effect.'''
        if not should_beautify(p):
            return
        if not p.b:
            return
        self.p = p.copy()
        aList = self.tokenize(p.b)
        assert ''.join(aList) == p.b
        aList = self.add_statement_braces(aList, giveWarnings=giveWarnings)
        self.bracketLevel = 0
        self.parens = 0
        self.result = []
        for s in aList:
            # g.trace(repr(s))
            self.put_token(s)
        if 0:
            for z in self.result:
                print(repr(z))
        if toList:
            return self.result
        else:
            return ''.join(self.result)
    #@+node:ekr.20110918225821.6815: *4* add_statement_braces
    def add_statement_braces(self, s, giveWarnings=False):
        p = self.p
        trace = False

        def oops(message, i, j):
            # This can be called from c-to-python, in which case warnings should be suppressed.
            if giveWarnings:
                g.error('** changed ', p.h)
                g.es_print('%s after\n%s' % (
                    message, repr(''.join(s[i: j]))))

        i, n, result = 0, len(s), []
        while i < n:
            token_ = s[i] # token is a module.
            progress = i
            if token_ in ('if', 'for', 'while',):
                j = self.skip_ws_and_comments(s, i + 1)
                if self.match(s, j, '('):
                    j = self.skip_parens(s, j)
                    if self.match(s, j, ')'):
                        old_j = j + 1
                        j = self.skip_ws_and_comments(s, j + 1)
                        if self.match(s, j, ';'):
                            # Example: while (*++prefix);
                            result.extend(s[i: j])
                        elif self.match(s, j, '{'):
                            result.extend(s[i: j])
                        else:
                            oops("insert '{'", i, j)
                            # Back up, and don't go past a newline or comment.
                            j = self.skip_ws(s, old_j)
                            result.extend(s[i: j])
                            result.append(' ')
                            result.append('{')
                            result.append('\n')
                            i = j
                            j = self.skip_statement(s, i)
                            result.extend(s[i: j])
                            result.append('\n')
                            result.append('}')
                            oops("insert '}'", i, j)
                    else:
                        oops("missing ')'", i, j)
                        result.extend(s[i: j])
                else:
                    oops("missing '('", i, j)
                    result.extend(s[i: j])
                i = j
            else:
                result.append(token_)
                i += 1
            assert progress < i
        if trace: g.trace(''.join(result))
        return result
    #@+node:ekr.20110919184022.6903: *5* skip_ws
    def skip_ws(self, s, i):
        while i < len(s):
            token_ = s[i] # token is a module.
            if token_.startswith(' ') or token_.startswith('\t'):
                i += 1
            else:
                break
        return i
    #@+node:ekr.20110918225821.6820: *5* skip_ws_and_comments
    def skip_ws_and_comments(self, s, i):
        while i < len(s):
            token_ = s[i] # token is a module.
            if token_.isspace():
                i += 1
            elif token_.startswith('//') or token_.startswith('/*'):
                i += 1
            else:
                break
        return i
    #@+node:ekr.20110918225821.6817: *5* skip_parens
    def skip_parens(self, s, i):
        '''Skips from the opening ( to the matching ).

        If no matching is found i is set to len(s)'''
        assert(self.match(s, i, '('))
        level = 0
        while i < len(s):
            ch = s[i]
            if ch == '(':
                level += 1; i += 1
            elif ch == ')':
                level -= 1
                if level <= 0: return i
                i += 1
            else: i += 1
        return i
    #@+node:ekr.20110918225821.6818: *5* skip_statement
    def skip_statement(self, s, i):
        '''Skip to the next ';' or '}' token.'''
        while i < len(s):
            if s[i] in ';}':
                i += 1
                break
            else:
                i += 1
        return i
    #@+node:ekr.20110917204542.6967: *4* put_token & helpers
    def put_token(self, s):
        '''Append token s to self.result as is,
        *except* for adjusting leading whitespace and comments.

        '{' tokens bump self.brackets or self.ignored_brackets.
        self.brackets determines leading whitespace.
        '''
        if s == '{':
            self.brackets += 1
        elif s == '}':
            self.brackets -= 1
            self.remove_indent()
        elif s == '(':
            self.parens += 1
        elif s == ')':
            self.parens -= 1
        elif s.startswith('\n'):
            if self.parens <= 0:
                s = '\n%s' % (' ' * self.brackets * self.tab_width)
            else: pass # Use the existing indentation.
        elif s.isspace():
            if self.parens <= 0 and self.result and self.result[-1].startswith('\n'):
                # Kill the whitespace.
                s = ''
            else: pass # Keep the whitespace.
        elif s.startswith('/*'):
            s = self.reformat_block_comment(s)
        else:
            pass # put s as it is.
        if s:
            self.result.append(s)
    #@+node:ekr.20110917204542.6968: *5* prev_token
    def prev_token(self, s):
        '''Return the previous token, ignoring whitespace and comments.'''
        i = len(self.result) - 1
        while i >= 0:
            s2 = self.result[i]
            if s == s2:
                return True
            elif s.isspace() or s.startswith('//') or s.startswith('/*'):
                i -= 1
            else:
                return False
    #@+node:ekr.20110918184425.6916: *5* reformat_block_comment
    def reformat_block_comment(self, s):
        return s
    #@+node:ekr.20110917204542.6969: *5* remove_indent
    def remove_indent(self):
        '''Remove one tab-width of blanks from the previous token.'''
        w = abs(self.tab_width)
        if self.result:
            s = self.result[-1]
            if s.isspace():
                self.result.pop()
                s = s.replace('\t', ' ' * w)
                if s.startswith('\n'):
                    s2 = s[1:]
                    self.result.append('\n' + s2[: -w])
                else:
                    self.result.append(s[: -w])
    #@+node:ekr.20110918225821.6819: *3* cpp.match
    def match(self, s, i, pat):
        return i < len(s) and s[i] == pat
    #@+node:ekr.20110917174948.6930: *3* cpp.tokenize & helper
    def tokenize(self, s):
        '''Tokenize comments, strings, identifiers, whitespace and operators.'''
        i, result = 0, []
        while i < len(s):
            # Loop invariant: at end: j > i and s[i:j] is the new token.
            j = i
            ch = s[i]
            if ch in '@\n': # Make *sure* these are separate tokens.
                j += 1
            elif ch == '#': # Preprocessor directive.
                j = g.skip_to_end_of_line(s, i)
            elif ch in ' \t':
                j = g.skip_ws(s, i)
            elif ch.isalpha() or ch == '_':
                j = g.skip_c_id(s, i)
            elif g.match(s, i, '//'):
                j = g.skip_line(s, i)
            elif g.match(s, i, '/*'):
                j = self.skip_block_comment(s, i)
            elif ch in "'\"":
                j = g.skip_string(s, i)
            else:
                j += 1
            assert j > i
            result.append(''.join(s[i: j]))
            i = j # Advance.
        return result
    #@+at The following could be added to the 'else' clause::
    #     # Accumulate everything else.
    #     while (
    #         j < n and
    #         not s[j].isspace() and
    #         not s[j].isalpha() and
    #         not s[j] in '"\'_@' and
    #             # start of strings, identifiers, and single-character tokens.
    #         not g.match(s,j,'//') and
    #         not g.match(s,j,'/*') and
    #         not g.match(s,j,'-->')
    #     ):
    #         j += 1
    #@+node:ekr.20110917193725.6974: *4* cpp.skip_block_comment
    def skip_block_comment(self, s, i):
        assert(g.match(s, i, "/*"))
        j = s.find("*/", i)
        if j == -1:
            return len(s)
        else:
            return j + 2
    #@-others
#@+node:ekr.20150519111457.1: ** class PythonTokenBeautifier
class PythonTokenBeautifier(object):
    '''A token-based Python beautifier.'''
    #@+others
    #@+node:ekr.20150523132558.1: *3* class OutputToken
    class OutputToken(object):
        '''A class representing Output Tokens'''

        def __init__(self, kind, value):
            self.kind = kind
            self.value = value

        def __repr__(self):
            if self.kind == 'line-indent':
                assert not self.value.strip(' ')
                return '%15s %s' % (self.kind, len(self.value))
            else:
                return '%15s %r' % (self.kind, self.value)

        __str__ = __repr__

        def to_string(self):
            '''Convert an output token to a string.'''
            return self.value if g.isString(self.value) else ''
    #@+node:ekr.20150527113020.1: *3* class ParseState
    class ParseState(object):
        '''A class representing items parse state stack.'''

        def __init__(self, kind, value):
            self.kind = kind
            self.value = value

        def __repr__(self):
            return 'State: %10s %s' % (self.kind, repr(self.value))

        __str__ = __repr__
    #@+node:ekr.20150519111713.1: *3* ptb.ctor
    def __init__(self, c):
        '''Ctor for PythonPrettyPrinter class.'''
        self.c = c
        # Globals...
        self.code_list = [] # The list of output tokens.
        # The present line and token...
        self.last_line_number = 0
        self.raw_val = None # Raw value for strings, comments.
        self.s = None # The string containing the line.
        self.val = None
        # State vars...
        self.backslash_seen = False
        self.decorator_seen = False
        self.level = 0 # indentation level.
        self.lws = '' # Leading whitespace.
            # Typically ' '*self.tab_width*self.level,
            # but may be changed for continued lines.
        self.paren_level = 0 # Number of unmatched left parens.
        self.state_stack = [] # Stack of ParseState objects.
        # Settings...
        if c:
            self.delete_blank_lines = not c.config.getBool(
                'tidy-keep-blank-lines', default=True)
            self.args_style = c.config.getString('tidy-args-style')
            # Not used yet.
            # if self.args_style not in ('align', 'asis', 'indent'):
                # self.args_style = 'align'
            self.tab_width = abs(c.tab_width) if c else 4
        else:
            self.tab_width = 4
        # Statistics
        self.n_changed_nodes = 0
        self.n_input_tokens = 0
        self.n_output_tokens = 0
        self.n_strings = 0
        self.parse_time = 0.0
        self.tokenize_time = 0.0
        self.beautify_time = 0.0
        self.check_time = 0.0
        self.total_time = 0.0
        # Undo vars
        self.changed = False
        self.dirtyVnodeList = []
    #@+node:ekr.20150530072449.1: *3* ptb.Entries
    #@+node:ekr.20150528171137.1: *4* ptb.prettyPrintNode
    def prettyPrintNode(self, p):
        '''The driver for beautification: beautify a single node.'''
        # c = self.c
        # trace = False and not g.unitTesting
        if not should_beautify(p):
            # @nobeautify is in effect.
            return
        if not p.b:
            # Pretty printing might add text!
            return
        if not p.b.strip():
            # Do this *after* we are sure @beautify is in effect.
            self.replace_body(p, '')
            return
        t1 = time.time()
        # Replace Leonine syntax with special comments.
        comment_string, s0 = comment_leo_lines(p)
        try:
            s1 = g.toEncodedString(s0)
            node1 = ast.parse(s1, filename='before', mode='exec')
        except IndentationError:
            self.skip_message('IndentationError', p)
            return
        except SyntaxError:
            self.skip_message('SyntaxError', p)
            return
        except Exception:
            g.es_exception()
            self.skip_message('Exception', p)
            return
        t2 = time.time()
        readlines = g.ReadLinesClass(s0).next
        tokens = list(tokenize.generate_tokens(readlines))
        t3 = time.time()
        s2 = self.run(tokens)
        t4 = time.time()
        try:
            s2_e = g.toEncodedString(s2)
            node2 = ast.parse(s2_e, filename='before', mode='exec')
            ok = compare_ast(node1, node2)
        except Exception:
            g.es_exception()
            g.trace('Error in %s...\n%s' % (p.h, s2_e))
            self.skip_message('BeautifierError', p)
            return
        if not ok:
            self.skip_message('BeautifierError', p)
            return
        t5 = time.time()
        # Restore the tags after the compare
        s3 = uncomment_leo_lines(comment_string, p, s2)
        self.replace_body(p, s3)
        # Update the stats
        self.n_input_tokens += len(tokens)
        self.n_output_tokens += len(self.code_list)
        self.n_strings += len(s3)
        self.parse_time += (t2 - t1)
        self.tokenize_time += (t3 - t2)
        self.beautify_time += (t4 - t3)
        self.check_time += (t5 - t4)
        self.total_time += (t5 - t1)
    #@+node:ekr.20150526194715.1: *4* ptb.run
    def run(self, tokens):
        '''
        The main line of PythonTokenBeautifier class.
        Called by prettPrintNode & test_beautifier.
        '''

        def oops():
            g.trace('unknown kind', self.kind)

        self.code_list = []
        self.state_stack = []
        self.file_start()
        for token5tuple in tokens:
            t1, t2, t3, t4, t5 = token5tuple
            srow, scol = t3
            self.kind = token.tok_name[t1].lower()
            self.val = g.toUnicode(t2)
            self.raw_val = g.toUnicode(t5)
            if srow != self.last_line_number:
                # Handle a previous backslash.
                if self.backslash_seen:
                    self.backslash()
                # Start a new row.
                raw_val = self.raw_val.rstrip()
                self.backslash_seen = raw_val.endswith('\\')
                # g.trace('backslash_seen',self.backslash_seen)
                if self.paren_level > 0:
                    s = self.raw_val.rstrip()
                    n = g.computeLeadingWhitespaceWidth(s, self.tab_width)
                    # This n will be one-too-many if formatting has
                    # changed: foo (
                    # to:      foo(
                    self.line_indent(ws=' ' * n)
                        # Do not set self.lws here!
                self.last_line_number = srow
            # g.trace('%10s %r'% (self.kind,self.val))
            func = getattr(self, 'do_' + self.kind, oops)
            func()
        self.file_end()
        return ''.join([z.to_string() for z in self.code_list])
    #@+node:ekr.20150526194736.1: *3* ptb.Input token Handlers
    #@+node:ekr.20150526203605.1: *4* ptb.do_comment
    def do_comment(self):
        '''Handle a comment token.'''
        raw_val = self.raw_val.rstrip()
        val = self.val.rstrip()
        entire_line = raw_val.lstrip().startswith('#')
        self.backslash_seen = False
            # Putting the comment will put the backslash.
        if entire_line:
            self.clean('line-indent')
            self.add_token('comment', raw_val)
        else:
            self.blank()
            self.add_token('comment', val)
    #@+node:ekr.20041021102938: *4* ptb.do_endmarker
    def do_endmarker(self):
        '''Handle an endmarker token.'''
        pass
    #@+node:ekr.20041021102340.1: *4* ptb.do_errortoken
    def do_errortoken(self):
        '''Handle an errortoken token.'''
        # This code is executed for versions of Python earlier than 2.4
        if self.val == '@':
            self.op(self.val)
    #@+node:ekr.20041021102340.2: *4* ptb.do_indent & do_dedent
    def do_dedent(self):
        '''Handle dedent token.'''
        self.level -= 1
        self.lws = self.level * self.tab_width * ' '
        self.line_start()
        state = self.state_stack[-1]
        if state.kind == 'indent' and state.value == self.level:
            self.state_stack.pop()
            state = self.state_stack[-1]
            if state.kind in ('class', 'def'):
                self.state_stack.pop()
                self.blank_lines(1)
                    # Most Leo nodes aren't at the top level of the file.
                    # self.blank_lines(2 if self.level == 0 else 1)

    def do_indent(self):
        '''Handle indent token.'''
        self.level += 1
        self.lws = self.val
        self.line_start()
    #@+node:ekr.20041021101911.5: *4* ptb.do_name
    def do_name(self):
        '''Handle a name token.'''
        name = self.val
        if name in ('class', 'def'):
            self.decorator_seen = False
            state = self.state_stack[-1]
            if state.kind == 'decorator':
                self.clean_blank_lines()
                self.line_end()
                self.state_stack.pop()
            else:
                self.blank_lines(1)
                # self.blank_lines(2 if self.level == 0 else 1)
            self.push_state(name)
            self.push_state('indent', self.level)
                # For trailing lines after inner classes/defs.
            self.word(name)
        elif name in ('and', 'in', 'not', 'not in', 'or'):
            self.word_op(name)
        else:
            self.word(name)
    #@+node:ekr.20041021101911.3: *4* ptb.do_newline
    def do_newline(self):
        '''Handle a regular newline.'''
        self.line_end()
    #@+node:ekr.20141009151322.17828: *4* ptb.do_nl
    def do_nl(self):
        '''Handle a continuation line.'''
        self.line_end()
    #@+node:ekr.20041021101911.6: *4* ptb.do_number
    def do_number(self):
        '''Handle a number token.'''
        self.add_token('number', self.val)
    #@+node:ekr.20040711135244.11: *4* ptb.do_op
    def do_op(self):
        '''Handle an op token.'''
        val = self.val
        if val == '.':
            self.op_no_blanks(val)
        elif val == '@':
            if not self.decorator_seen:
                self.blank_lines(1)
                self.decorator_seen = True
            self.op_no_blanks(val)
            self.push_state('decorator')
        elif val in ',;:':
            # Pep 8: Avoid extraneous whitespace immediately before
            # comma, semicolon, or colon.
            self.op_blank(val)
        elif val in '([{':
            # Pep 8: Avoid extraneous whitespace immediately inside
            # parentheses, brackets or braces.
            self.lt(val)
        elif val in ')]}':
            # Ditto.
            self.rt(val)
        elif val == '=':
            # Pep 8: Don't use spaces around the = sign when used to indicate
            # a keyword argument or a default parameter value.
            if self.paren_level:
                self.op_no_blanks(val)
            else:
                self.op(val)
        elif val in '~+-':
            self.possible_unary_op(val)
        elif val == '*':
            self.star_op()
        elif val == '**':
            self.star_star_op()
        else:
            # Pep 8: always surround binary operators with a single space.
            # '==','+=','-=','*=','**=','/=','//=','%=','!=','<=','>=','<','>',
            # '^','~','*','**','&','|','/','//',
            # Pep 8: If operators with different priorities are used,
            # consider adding whitespace around the operators with the lowest priority(ies).
            self.op(val)
    #@+node:ekr.20150526204248.1: *4* ptb.do_string
    def do_string(self):
        '''Handle a 'string' token.'''
        self.add_token('string', self.val)
        if self.val.find('\\\n'):
            self.backslash_seen = False
            # This *does* retain the string's spelling.
        self.blank()
    #@+node:ekr.20150526201902.1: *3* ptb.Output token generators
    #@+node:ekr.20150526195542.1: *4* ptb.add_token
    def add_token(self, kind, value=''):
        '''Add a token to the code list.'''
        # if kind in ('line-indent','line-start','line-end'):
            # g.trace(kind,repr(value),g.callers())
        tok = self.OutputToken(kind, value)
        self.code_list.append(tok)
    #@+node:ekr.20150526201701.3: *4* ptb.arg_start & arg_end (not used)
    # def arg_end(self):
        # '''Add a token indicating the end of an argument list.'''
        # self.add_token('arg-end')
    # def arg_start(self):
        # '''Add a token indicating the start of an argument list.'''
        # self.add_token('arg-start')
    #@+node:ekr.20150601095528.1: *4* ptb.backslash
    def backslash(self):
        '''Add a backslash token and clear .backslash_seen'''
        self.add_token('backslash', '\\')
        self.add_token('line-end', '\n')
        self.line_indent()
        self.backslash_seen = False
    #@+node:ekr.20150526201701.4: *4* ptb.blank
    def blank(self):
        '''Add a blank request on the code list.'''
        prev = self.code_list[-1]
        if prev.kind not in (
            'blank', 'blank-lines',
            'file-start',
            'line-end', 'line-indent',
            'lt', 'op-no-blanks', 'unary-op',
        ):
            self.add_token('blank', ' ')
    #@+node:ekr.20150526201701.5: *4* ptb.blank_lines
    def blank_lines(self, n):
        '''
        Add a request for n blank lines to the code list.
        Multiple blank-lines request yield at least the maximum of all requests.
        '''
        self.clean_blank_lines()
        kind = self.code_list[-1].kind
        if kind == 'file-start':
            self.add_token('blank-lines', n)
        else:
            for i in range(0, n + 1):
                self.add_token('line-end', '\n')
            # Retain the token (intention) for debugging.
            self.add_token('blank-lines', n)
            self.line_indent()
    #@+node:ekr.20150526201701.6: *4* ptb.clean
    def clean(self, kind):
        '''Remove the last item of token list if it has the given kind.'''
        prev = self.code_list[-1]
        if prev.kind == kind:
            self.code_list.pop()
    #@+node:ekr.20150527175750.1: *4* ptb.clean_blank_lines
    def clean_blank_lines(self):
        '''Remove all vestiges of previous lines.'''
        table = ('blank-lines', 'line-end', 'line-indent')
        while self.code_list[-1].kind in table:
            self.code_list.pop()
    #@+node:ekr.20150526201701.8: *4* ptb.file_start & file_end
    def file_end(self):
        '''
        Add a file-end token to the code list.
        Retain exactly one line-end token.
        '''
        self.clean_blank_lines()
        self.add_token('line-end', '\n')
        self.add_token('line-end', '\n')
        self.add_token('file-end')

    def file_start(self):
        '''Add a file-start token to the code list and the state stack.'''
        self.add_token('file-start')
        self.push_state('file-start')
    #@+node:ekr.20150530190758.1: *4* ptb.line_indent
    def line_indent(self, ws=None):
        '''Add a line-indent token if indentation is non-empty.'''
        self.clean('line-indent')
        ws = ws or self.lws
        if ws:
            self.add_token('line-indent', ws)
    #@+node:ekr.20150526201701.9: *4* ptb.line_start & line_end
    def line_end(self):
        '''Add a line-end request to the code list.'''
        prev = self.code_list[-1]
        if prev.kind == 'file-start':
            return
        self.clean('blank') # Important!
        if self.delete_blank_lines:
            self.clean_blank_lines()
        self.clean('line-indent')
        if self.backslash_seen:
            self.backslash()
        self.add_token('line-end', '\n')
        self.line_indent()
            # Add the indentation for all lines
            # until the next indent or unindent token.

    def line_start(self):
        '''Add a line-start request to the code list.'''
        self.line_indent()
    #@+node:ekr.20150526201701.11: *4* ptb.lt & rt
    def lt(self, s):
        '''Add a left paren request to the code list.'''
        assert s in '([{', repr(s)
        self.paren_level += 1
        self.clean('blank')
        prev = self.code_list[-1]
        if prev.kind in ('op', 'word-op'):
            self.blank()
            self.add_token('lt', s)
        elif prev.kind == 'word':
            # Only suppress blanks before '(' or '[' for non-keyworks.
            if s == '{' or prev.value in ('if', 'else', 'return'):
                self.blank()
            self.add_token('lt', s)
        elif prev.kind == 'op':
            self.op(s)
        else:
            self.op_no_blanks(s)

    def rt(self, s):
        '''Add a right paren request to the code list.'''
        assert s in ')]}', repr(s)
        self.paren_level -= 1
        prev = self.code_list[-1]
        if prev.kind == 'arg-end':
            # Remove a blank token preceding the arg-end token.
            prev = self.code_list.pop()
            self.clean('blank')
            self.code_list.append(prev)
        else:
            self.clean('blank')
        self.add_token('rt', s)
    #@+node:ekr.20150526201701.12: *4* ptb.op*
    def op(self, s):
        '''Add op token to code list.'''
        assert s and g.isString(s), repr(s)
        self.blank()
        self.add_token('op', s)
        self.blank()

    def op_blank(self, s):
        '''Remove a preceding blank token, then add op and blank tokens.'''
        assert s and g.isString(s), repr(s)
        self.clean('blank')
        self.add_token('op', s)
        self.blank()

    def op_no_blanks(self, s):
        '''Add an operator *not* surrounded by blanks.'''
        self.clean('blank')
        self.add_token('op-no-blanks', s)
    #@+node:ekr.20150527213419.1: *4* ptb.possible_unary_op & unary_op
    def possible_unary_op(self, s):
        '''Add a unary or binary op to the token list.'''
        self.clean('blank')
        prev = self.code_list[-1]
        if prev.kind in ('lt', 'op', 'op-no-blanks', 'word-op'):
            self.unary_op(s)
        elif prev.kind == 'word' and prev.value in ('elif', 'if', 'return', 'while'):
            self.unary_op(s)
        else:
            self.op(s)

    def unary_op(self, s):
        '''Add an operator request to the code list.'''
        assert s and g.isString(s), repr(s)
        self.blank()
        self.add_token('unary-op', s)
    #@+node:ekr.20150531051827.1: *4* ptb.star_op
    def star_op(self):
        '''Put a '*' op, with special cases for *args.'''
        val = '*'
        if self.paren_level:
            i = len(self.code_list) - 1
            if self.code_list[i].kind == 'blank':
                i -= 1
            token = self.code_list[i]
            if token.kind == 'lt':
                self.op_no_blanks(val)
            elif token.value == ',':
                self.blank()
                self.add_token('op-no-blanks', val)
            else:
                self.op(val)
        else:
            self.op(val)
    #@+node:ekr.20150531053417.1: *4* ptb.star_star_op
    def star_star_op(self):
        '''Put a ** operator, with a special case for **kwargs.'''
        val = '**'
        if self.paren_level:
            i = len(self.code_list) - 1
            if self.code_list[i].kind == 'blank':
                i -= 1
            token = self.code_list[i]
            if token.value == ',':
                self.blank()
                self.add_token('op-no-blanks', val)
            else:
                self.op(val)
        else:
            self.op(val)
    #@+node:ekr.20150526201701.13: *4* ptb.word & word_op
    def word(self, s):
        '''Add a word request to the code list.'''
        assert s and g.isString(s), repr(s)
        self.blank()
        self.add_token('word', s)
        self.blank()

    def word_op(self, s):
        '''Add a word-op request to the code list.'''
        assert s and g.isString(s), repr(s)
        self.blank()
        self.add_token('word-op', s)
        self.blank()
    #@+node:ekr.20150530064617.1: *3* ptb.Utils
    #@+node:ekr.20150528171420.1: *4* ppp.replace_body
    def replace_body(self, p, s):
        '''Replace the body with the pretty version.'''
        c, u = self.c, self.c.undoer
        undoType = 'Pretty Print'
        if p.b == s:
            return
        self.n_changed_nodes += 1
        if not self.changed:
            # Start the group.
            u.beforeChangeGroup(p, undoType)
            self.changed = True
            self.dirtyVnodeList = []
        undoData = u.beforeChangeNodeContents(p)
        c.setBodyString(p, s)
        dirtyVnodeList2 = p.setDirty()
        self.dirtyVnodeList.extend(dirtyVnodeList2)
        u.afterChangeNodeContents(p, undoType, undoData, dirtyVnodeList=self.dirtyVnodeList)
    #@+node:ekr.20150528180738.1: *4* ptb.end_undo
    def end_undo(self):
        '''Complete undo processing.'''
        c = self.c; u = c.undoer; undoType = 'Pretty Print'
        current = c.p
        if self.changed:
            # Tag the end of the command.
            u.afterChangeGroup(current, undoType, dirtyVnodeList=self.dirtyVnodeList)
    #@+node:ekr.20150528172940.1: *4* ptb.print_stats
    def print_stats(self):
        print('==================== stats')
        print('changed nodes  %s' % self.n_changed_nodes)
        print('tokens         %s' % self.n_input_tokens)
        print('len(code_list) %s' % self.n_output_tokens)
        print('len(s)         %s' % self.n_strings)
        print('parse          %4.2f sec.' % self.parse_time)
        print('tokenize       %4.2f sec.' % self.tokenize_time)
        print('format         %4.2f sec.' % self.beautify_time)
        print('check          %4.2f sec.' % self.check_time)
        print('total          %4.2f sec.' % self.total_time)
    #@+node:ekr.20150528084644.1: *4* ptb.push_state
    def push_state(self, kind, value=None):
        '''Append a state to the state stack.'''
        state = self.ParseState(kind, value)
        self.state_stack.append(state)
    #@+node:ekr.20150528192109.1: *4* ptb.skip_message
    def skip_message(self, s, p):
        '''Print a standard message about skipping a node.'''
        message = '%s. skipped:' % s
        g.warning('%22s %s' % (message, p.h))
    #@-others
#@-others
if __name__ == "__main__":
    main()
#@@language python
#@@tabwidth -4
#@-leo
