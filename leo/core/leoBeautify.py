#@+leo-ver=5-thin
#@+node:ekr.20150521115018.1: * @file leoBeautify.py
'''Leo's beautification classes.'''
import leo.core.leoGlobals as g
import ast
import re
import sys
import time
import token
import tokenize
#@+others
#@+node:ekr.20150528131012.1: **  commands (leoBeautifier.py)
#@+node:ekr.20150528131012.2: *3* beautify-all-python
@g.command('beautify-all-python')
@g.command('pretty-print-all-python')
def prettyPrintAllPythonCode (event):
    '''Beautify all Python code in the entire outline.'''
    c = event.get('c')
    if not c: return
    t1 = time.clock()
    pp = PythonTokenBeautifier(c)
    for p in c.all_unique_positions():
        if g.scanForAtLanguage(c,p) == "python":
            pp.prettyPrintNode(p)
    pp.end_undo()
    t2 = time.clock()
    # pp.print_stats()
    g.es('changed %s nodes in %4.2f sec.' % (pp.n_changed_nodes,t2-t1))
#@+node:ekr.20150528131012.3: *3* beautify-c
@g.command('beautify-c')
@g.command('pretty-print-c')
def beautifyCCode (event):
    '''Beautify all C code in the selected tree.'''
    c = event.get('c')
    if not c: return
    u,undoType = c.undoer,'beautify-c'
    pp = CPrettyPrinter(c)
    u.beforeChangeGroup(c.p,undoType)
    dirtyVnodeList = []
    changed = False
    for p in c.p.self_and_subtree():
        if g.scanForAtLanguage(c,p) == "c":
            bunch = u.beforeChangeNodeContents(p)
            s = pp.indent(p)
            if p.b != s:
                # g.es('changed: %s' % (p.h))
                p.b = s
                p.v.setDirty()
                dirtyVnodeList.append(p.v)
                u.afterChangeNodeContents(p,undoType,bunch)
                changed = True
    if changed:
        u.afterChangeGroup(c.p,undoType,
            reportFlag=False,dirtyVnodeList=dirtyVnodeList)
    c.bodyWantsFocus()
#@+node:ekr.20150528131012.4: *3* beautify-node
@g.command('beautify-node')
@g.command('pretty-print-node')
def prettyPrintPythonNode (event):
    '''Beautify a single Python node.'''
    c = event.get('c')
    if not c: return
    ### pp = PythonPrettyPrinter(c)
    pp = PythonTokenBeautifier(c)
    if g.scanForAtLanguage(c,c.p) == "python":
        pp.prettyPrintNode(c.p)
    pp.end_undo()
    # pp.print_stats()
#@+node:ekr.20150528131012.5: *3* beautify-tree
@g.command('beautify-tree')
@g.command('pretty-print-tree')
def beautifyPythonTree (event):
    '''Beautify the Python code in the selected outline.'''
    c = event.get('c')
    t1 = time.clock()
    pp = PythonTokenBeautifier(c)
    for p in c.p.self_and_subtree():
        if g.scanForAtLanguage(c,p) == "python":
            pp.prettyPrintNode(p)
    pp.end_undo()
    t2 = time.clock()
    # pp.print_stats()
    g.es('changed %s nodes in %4.2f sec.' % (pp.n_changed_nodes,t2-t1))
#@+node:ekr.20150528091356.1: **  top-level functions (leoBeautifier.py)
#@+node:ekr.20150529084212.1: *3* comment_leo_lines
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
        k = j > -1 and s.find('>>') or -1
        if -1 < j < k:
            result.append(comment+s)
        elif s.lstrip().startswith('@'):
            # Comment out all other Leonine constructs.
            if (
                s.startswith('@\n') or s.startswith('@doc\n') or
                s.startswith('@ ') or s.startswith('@doc ')
            ):
                # Comment the entire doc part, until @c or @code.
                result.append(comment+s)
                i += 1
                while i < len(lines):
                    s = lines[i]
                    result.append(comment+s)
                    i += 1
                    if (
                        s.startswith('@c\n') or s.startswith('@code\n') or
                        s.startswith('@c ') or s.startswith('@code ')
                    ):
                        break
            else:
                j = g.skip_ws(s, 0)
                assert s[j] == '@'
                j += 1
                k = g.skip_id(s, j, chars='-')
                if k > j:
                    word = s[j:k]
                    if word == 'others':
                        # Remember the original @others line.
                        result.append(comment+s)
                        # Generate a properly-indented pass line.
                        result.append('%spass\n' % (' ' * (j-1)))
                    else:
                        # Comment only Leo directives, not decorators.
                        result.append(comment+s if word in d else s)
                else:
                    result.append(s)
        else:
            # A plain line.
            result.append(s)
        if i == progress:
            i += 1
    # g.trace(''.join(result))
    return comment,''.join(result)
#@+node:ekr.20150526115312.1: *3* compare_ast
# http://stackoverflow.com/questions/3312989/
# elegant-way-to-test-python-asts-for-equality-not-reference-or-object-identity

def compare_ast(node1, node2):
    import itertools
    if type(node1) is not type(node2):
        return False
    if isinstance(node1, ast.AST):
        for k, v in vars(node1).iteritems():
            if k in (
                'lineno', 'col_offset', 'ctx',
                    # standard fields
                # 'trailing_tokens', 'str_spelling',
                    # fields injected by LeoTidy.
            ):
                continue
            v2 = getattr(node2, k)
            if not compare_ast(v, v2):
                name1,name2 = v.__class__.__name__,v2.__class__.__name__
                if name1 == 'str':
                    g.trace('str',repr(v),repr(v2))
                elif name1 == 'Str':
                    g.trace('Str',repr(v.s),repr(v2.s))
                else:
                    n1 = getattr(v,'lineno','???')
                    n2 = getattr(v2,'lineno','???')
                    g.trace(n1,n2,name1,name2)
                    # g.trace(v)
                    # g.trace(v2)
                return False
        return True
    elif isinstance(node1, list):
        return all(itertools.starmap(compare_ast, itertools.izip(node1, node2)))
    else:
        return node1 == node2
#@+node:ekr.20150524215322.1: *3* dumpTokens & dumpToken
def dumpTokens(tokens,verbose=True):
    last_line_number = 0
    for token5tuple in tokens:
        last_line_number = dumpToken(last_line_number,token5tuple,verbose)

def dumpToken (last_line_number,token5tuple,verbose):
    '''Dump the given token.'''
    t1,t2,t3,t4,t5 = token5tuple
    name = token.tok_name[t1].lower()
    val = str(t2) # can fail
    srow,scol = t3
    erow,ecol = t4
    line = str(t5) # can fail
    if last_line_number != srow:
        if verbose:
            print("\n---- line: %3s %3s %r" % (srow,erow,line))
        else:
            print('%3s %7s %r' % (srow,name,line))
    if verbose:
        if name in ('dedent','indent','newline','nl'):
            val = repr(val)
        # print("%10s %3d %3d %-8s" % (name,scol,ecol,val))
        # print('%10s srow: %s erow: %s %s' % (name,srow,erow,val))
        print('%10s %s' % (name,val))
            # line[scol:ecol]
    last_line_number = srow
    return last_line_number
#@+node:ekr.20150530061745.1: *3* main (external entry)
def main():
    '''External entry point for Leo's beautifier.'''
    g.trace(sys.argv)
#@+node:ekr.20150527143619.1: *3* show_lws
def show_lws(s):
    '''Show leading whitespace in a convenient format.'''
    return repr(s) if s.strip(' ') else len(s)
#@+node:ekr.20150521114057.1: *3* test_beautifier (prints stats)
def test_beautifier(c,h,p,settings):
    '''Test Leo's beautifier code'''
    if not p:
        g.trace('not found: %s' % h)
        return
    s = g.getScript(c, p,
                    useSelectedText=False,
                    forcePythonSentinels=True,
                    useSentinels=False)
    g.trace(h.strip())
    t1 = time.clock()
    s1 = g.toEncodedString(s)
    node1 = ast.parse(s1,filename='before',mode='exec')
    t2 = time.clock()
    readlines = g.ReadLinesClass(s).next
    tokens = list(tokenize.generate_tokens(readlines))
    t3 = time.clock()
    beautifier = PythonTokenBeautifier(c)
    s2 = beautifier.run(p,tokens)
    t4 = time.clock()
    try:
        s2_e = g.toEncodedString(s2)
        node2 = ast.parse(s2_e,filename='before',mode='exec')
        ok = compare_ast(node1, node2)
    except Exception:
        g.es_exception()
        ok = False
    t5 = time.clock()
    #  Update the stats
    beautifier.n_input_tokens += len(tokens)
    beautifier.n_output_tokens += len(beautifier.code_list)
    beautifier.n_strings += len(s2)
    beautifier.parse_time += (t2-t1)
    beautifier.tokenize_time += (t3-t2)
    beautifier.beautify_time += (t4-t3)
    beautifier.check_time += (t5-t4)
    beautifier.total_time += (t5-t1)
    if settings.get('input_string'):
        print('==================== input_string')
        for i,z in enumerate(g.splitLines(s)):
            print('%4s %s' % (i+1,z.rstrip()))
    if settings.get('input_lines'):
        print('==================== input_lines')
        dumpTokens(tokens,verbose=False)
    if settings.get('input_tokens'):
        print('==================== input_tokens')
        dumpTokens(tokens,verbose=True)
    if settings.get('output_tokens'):
        print('==================== code_list')
        for i,z in enumerate(beautifier.code_list):
            print('%4s %s' % (i,z))
    if settings.get('output_string'):
        print('==================== output_string')
        for i,z in enumerate(g.splitLines(s2)):
            print('%4s %s' % (i+1,z.rstrip()))
    if settings.get('stats'):
        beautifier.print_stats()
    if not ok:
        print('*************** fail: %s ***************' % (h))
#@+node:ekr.20150529095117.1: *3* uncomment_leo_lines
def uncomment_leo_lines(comment,p,s0):
    '''Reverse the effect of comment_leo_lines.'''
    i, lines, result = 0, g.splitLines(s0), []
    # g.trace(s0)
    while i < len(lines):
        s = lines[i]
        i += 1
        j = s.find(comment)
        if j == -1:
            # A regular line.
            result.append(s)
            continue
        # A special line. i now points at the *next* line.
        s = s.lstrip().lstrip(comment)
        if (
            s.startswith('@\n') or s.startswith('@doc\n') or
            s.startswith('@ ') or s.startswith('@doc ')
        ):
            result.append(s)
            while i < len(lines):
                s = lines[i].lstrip().lstrip(comment)
                result.append(s)
                i += 1
                if (
                    s.startswith('@c\n') or s.startswith('@code\n') or
                    s.startswith('@c ') or s.startswith('@code ')
                ):
                    break
        elif s.find('@others') > -1:
            # Restore the @others line, including leading whitespace.
            result.append(s)
            # The beautifier may insert blank lines after @others.
            while i < len(lines) and not lines[i].strip():
                i += 1
            # Skip the pass line.
            if i < len(lines) and lines[i].lstrip().startswith('pass'):
                i += 1
            else:
                g.trace('*** no pass after @others',p.h)
        else:
            result.append(s)
    return ''.join(result)
#@+node:ekr.20110917174948.6903: ** class CPrettyPrinter
class CPrettyPrinter:

    #@+others
    #@+node:ekr.20110917174948.6904: *3* __init__ (CPrettyPrinter)
    def __init__ (self,c):
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
    #@+node:ekr.20110917174948.6911: *3* indent & helpers
    def indent (self,p,toList=False,giveWarnings=True):

        # c = self.c
        if not p.b: return
        self.p = p.copy()

        aList = self.tokenize(p.b)
        assert ''.join(aList) == p.b

        aList = self.add_statement_braces(aList,giveWarnings=giveWarnings)

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
    def add_statement_braces (self,s,giveWarnings=False):

        p = self.p
        trace = False

        def oops(message,i,j):
            # This can be called from c-to-python, in which case warnings should be suppressed.
            if giveWarnings:
                g.error('** changed ',p.h)
                g.es_print('%s after\n%s' % (
                    message,repr(''.join(s[i:j]))))

        i,n,result = 0,len(s),[]
        while i < n:
            token_ = s[i] # token is a module.
            progress = i
            if token_ in ('if','for','while',):
                j = self.skip_ws_and_comments(s,i+1)
                if self.match(s,j,'('):
                    j = self.skip_parens(s,j)
                    if self.match(s,j,')'):
                        old_j = j+1
                        j = self.skip_ws_and_comments(s,j+1)
                        if self.match(s,j,';'):
                            # Example: while (*++prefix);
                            result.extend(s[i:j])
                        elif self.match(s,j,'{'):
                            result.extend(s[i:j])
                        else:
                            oops("insert '{'",i,j)
                            # Back up, and don't go past a newline or comment.
                            j = self.skip_ws(s,old_j)
                            result.extend(s[i:j])
                            result.append(' ')
                            result.append('{')
                            result.append('\n')
                            i = j
                            j = self.skip_statement(s,i)
                            result.extend(s[i:j])
                            result.append('\n')
                            result.append('}')
                            oops("insert '}'",i,j)
                    else:
                        oops("missing ')'",i,j)
                        result.extend(s[i:j])
                else:
                    oops("missing '('",i,j)
                    result.extend(s[i:j])
                i = j
            else:
                result.append(token_)
                i += 1
            assert progress < i

        if trace: g.trace(''.join(result))
        return result

    #@+node:ekr.20110919184022.6903: *5* skip_ws
    def skip_ws (self,s,i):

        while i < len(s):
            token_ = s[i] # token is a module.
            if token_.startswith(' ') or token_.startswith('\t'):
                i += 1
            else:
                break

        return i
    #@+node:ekr.20110918225821.6820: *5* skip_ws_and_comments
    def skip_ws_and_comments (self,s,i):

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
    def skip_parens(self,s,i):

        '''Skips from the opening ( to the matching ).

        If no matching is found i is set to len(s)'''

        assert(self.match(s,i,'('))

        level = 0
        while i < len(s):
            ch = s[i]
            if ch == '(':
                level += 1 ; i += 1
            elif ch == ')':
                level -= 1
                if level <= 0:  return i
                i += 1
            else: i += 1
        return i
    #@+node:ekr.20110918225821.6818: *5* skip_statement
    def skip_statement (self,s,i):

        '''Skip to the next ';' or '}' token.'''

        while i < len(s):
            if s[i] in ';}':
                i += 1
                break
            else:
                i += 1
        return i
    #@+node:ekr.20110917204542.6967: *4* put_token & helpers
    def put_token (self,s):

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

    #@+at
    #     # It doesn't hurt to increase indentation after *all* '{'.
    #     if s == '{':
    #         # Increase brackets unless '=' precedes it.
    #         if self.prev_token('='):
    #             self.ignored_brackets += 1
    #         else:
    #             self.brackets += 1
    #     elif s == '}':
    #         if self.ignored_brackets:
    #             self.ignored_brackets -= 1
    #         else:
    #             self.brackets -= 1
    #             self.remove_indent()
    #@+node:ekr.20110917204542.6968: *5* prev_token
    def prev_token (self,s):

        '''Return the previous token, ignoring whitespace and comments.'''

        i = len(self.result)-1
        while i >= 0:
            s2 = self.result[i]
            if s == s2:
                return True
            elif s.isspace() or s.startswith('//') or s.startswith ('/*'):
                i -= 1
            else:
                return False
    #@+node:ekr.20110918184425.6916: *5* reformat_block_comment
    def reformat_block_comment (self,s):

        return s
    #@+node:ekr.20110917204542.6969: *5* remove_indent
    def remove_indent (self):

        '''Remove one tab-width of blanks from the previous token.'''

        w = abs(self.tab_width)

        if self.result:
            s = self.result[-1]
            if s.isspace():
                self.result.pop()
                s = s.replace('\t',' ' * w)
                if s.startswith('\n'):
                    s2 = s[1:]
                    self.result.append('\n'+s2[:-w])
                else:
                    self.result.append(s[:-w])
    #@+node:ekr.20110918225821.6819: *3* match
    def match(self,s,i,pat):

        return i < len(s) and s[i] == pat
    #@+node:ekr.20110917174948.6930: *3* tokenize & helper
    def tokenize (self,s):

        '''Tokenize comments, strings, identifiers, whitespace and operators.'''

        i,result = 0,[]
        while i < len(s):
            # Loop invariant: at end: j > i and s[i:j] is the new token.
            j = i
            ch = s[i]
            if ch in '@\n': # Make *sure* these are separate tokens.
                j += 1
            elif ch == '#': # Preprocessor directive.
                j = g.skip_to_end_of_line(s,i)
            elif ch in ' \t':
                j = g.skip_ws(s,i)
            elif ch.isalpha() or ch == '_':
                j = g.skip_c_id(s,i)
            elif g.match(s,i,'//'):
                j = g.skip_line(s,i)
            elif g.match(s,i,'/*'):
                j = self.skip_block_comment(s,i)
            elif ch in "'\"":
                j = g.skip_string(s,i)
            else:
                j += 1

            assert j > i
            result.append(''.join(s[i:j]))
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
    #@+node:ekr.20110917193725.6974: *4* skip_block_comment
    def skip_block_comment (self,s,i):

        assert(g.match(s,i,"/*"))

        j = s.find("*/",i)
        if j == -1:
            return len(s)
        else:
            return j + 2
    #@-others
#@+node:ekr.20150525123715.1: ** class ProjectUtils
class ProjectUtils:
    '''A class to compute the files in a project.'''
    # To do: get project info from @data nodes.

    #@+others
    #@+node:ekr.20150525123715.2: *3* pu.files_in_dir
    def files_in_dir (self,theDir,recursive=True,extList=None,excludeDirs=None):
        '''
        Return a list of all Python files in the directory.
        Include all descendants if recursiveFlag is True.
        Include all file types if extList is None.
        '''
        import glob
        import os
        # if extList is None: extList = ['.py']
        if excludeDirs is None: excludeDirs = []
        result = []
        if recursive:
            for root, dirs, files in os.walk(theDir):
                for z in files:
                    fn = g.os_path_finalize_join(root,z)
                    junk,ext = g.os_path_splitext(fn)
                    if not extList or ext in extList:
                        result.append(fn)
                if excludeDirs and dirs:
                    for z in dirs:
                        if z in excludeDirs:
                            dirs.remove(z)
        else:
            for ext in extList:
                result.extend(glob.glob('%s.*%s' % (theDir,ext)))
        return sorted(list(set(result)))
    #@+node:ekr.20150525123715.3: *3* pu.get_project_directory
    def get_project_directory(self,name):
        
        # Ignore everything after the first space.
        i = name.find(' ')
        if i > -1:
            name = name[:i].strip()
        leo_path,junk = g.os_path_split(__file__)
        d = { # Change these paths as required for your system.
            'coverage': r'C:\Python26\Lib\site-packages\coverage-3.5b1-py2.6-win32.egg\coverage',
            'leo':      r'C:\leo.repo\leo-editor\leo\core',
            'lib2to3':  r'C:\Python26\Lib\lib2to3',
            'pylint':   r'C:\Python26\Lib\site-packages\pylint',
            'rope':     r'C:\Python26\Lib\site-packages\rope-0.9.4-py2.6.egg\rope\base',
            'test':     g.os_path_finalize_join(g.app.loadDir,'..','test-proj'),
        }
        dir_ = d.get(name.lower())
        # g.trace(name,dir_)
        if not dir_:
            g.trace('bad project name: %s' % (name))
        if not g.os_path_exists(dir_):
            g.trace('directory not found:' % (dir_))
        return dir_ or ''
    #@+node:ekr.20150525123715.4: *3* pu.project_files
    def project_files(self,name,force_all=False):
        '''Return a list of all files in the named project.'''
        # Ignore everything after the first space.
        i = name.find(' ')
        if i > -1:
            name = name[:i].strip()
        leo_path,junk = g.os_path_split(__file__)
        d = { # Change these paths as required for your system.
            'coverage': (
                r'C:\Python26\Lib\site-packages\coverage-3.5b1-py2.6-win32.egg\coverage',
                ['.py'],['.bzr','htmlfiles']),
            'leo':(
                r'C:\leo.repo\leo-editor\leo\core',
                # leo_path,
                ['.py'],['.bzr']),
            'lib2to3': (
                r'C:\Python26\Lib\lib2to3',
                ['.py'],['tests']),
            'pylint': (
                r'C:\Python26\Lib\site-packages\pylint',
                ['.py'],['.bzr','test']),
            'rope': (
                r'C:\Python26\Lib\site-packages\rope-0.9.4-py2.6.egg\rope\base',['.py'],['.bzr']),
            # 'test': (
                # g.os_path_finalize_join(leo_path,'test-proj'),
                # ['.py'],['.bzr']),
        }
        data = d.get(name.lower())
        if not data:
            g.trace('bad project name: %s' % (name))
            return []
        theDir,extList,excludeDirs=data
        files = self.files_in_dir(theDir,recursive=True,extList=extList,excludeDirs=excludeDirs)
        if files:
            if name.lower() == 'leo':
                for exclude in ['__init__.py','format-code.py']:
                    files = [z for z in files if not z.endswith(exclude)]
                fn = g.os_path_finalize_join(theDir,'..','plugins','qtGui.py')
                if fn and g.os_path_exists(fn):
                    files.append(fn)
            if g.app.runningAllUnitTests and len(files) > 1 and not force_all:
                return [files[0]]
        if not files:
            g.trace(theDir)
        if g.app.runningAllUnitTests and len(files) > 1 and not force_all:
            return [files[0]]
        else:
            return files
    #@-others
#@+node:ekr.20150519111457.1: ** class PythonTokenBeautifier
class PythonTokenBeautifier:
    '''A token-based Python beautifier.'''
    #@+others
    #@+node:ekr.20150523132558.1: *3* class OutputToken
    class OutputToken:
        '''A class representing Output Tokens'''

        def __init__(self,kind,value):
            self.kind = kind
            self.value = value

        def __repr__(self):
            return '%15s %s' % (self.kind,repr(self.value))

        __str__ = __repr__

        def to_string(self):
            '''Convert an output token to a string.'''
            return self.value if g.isString(self.value) else ''
    #@+node:ekr.20150527113020.1: *3* class ParseState
    class ParseState:
        '''A class representing items parse state stack.'''
        
        def __init__(self,kind,value):
            self.kind = kind
            self.value = value
            
        def __repr__(self):
            return 'State: %10s %s' % (self.kind,repr(self.value))

        __str__ = __repr__
    #@+node:ekr.20150519111713.1: *3* ptb.ctor
    def __init__ (self,c):
        '''Ctor for PythonPrettyPrinter class.'''
        self.c = c
        # Globals...
        self.code_list = [] # The list of output tokens.
        self.regex_lws = re.compile(r'([ \t]*)')
        # The present line and token...
        self.line_lws = ''
        self.extra_ws = ''
        self.raw_val = None # Raw value for strings, comments.
        self.s = None # The string containing the line.
        self.val = None
        # State vars...
        self.decorator_seen = False
        self.level = 0 # indentation level.
        self.lws = '' # Leading whitespace.
            # Typically ' '*self.tab_width*self.level,
            # but may be changed for continued lines.
        self.paren_level = 0 # Number of unmatched left parens.
        self.state_stack = [] # Stack of ParseState objects.
        # Settings...
        self.delete_blank_lines = not c.config.getBool(
            'tidy-keep-blank-lines',default=True)
        self.args_style = c.config.getString('tidy-args-style')
        if self.args_style not in ('align','asis','indent'):
            self.args_style = 'align'
        self.tab_width = abs(c.tab_width) if c else 4
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
    def prettyPrintNode(self,p):
        '''The driver for beautification: beautify a single node.'''
        c = self.c
        trace = False and not g.unitTesting
        if not p.b:
            # Pretty printing might add text!
            return
        if not p.b.strip():
            self.replace_body(p,'')
            return
        t1 = time.clock()
        # Replace Leonine syntax with special comments.
        comment_string,s0 = comment_leo_lines(p)
        try:
            s1 = g.toEncodedString(s0)
            node1 = ast.parse(s1,filename='before',mode='exec')
        except IndentationError:
            self.skip_message('IndentationError',p)
            return
        except SyntaxError:
            self.skip_message('SyntaxError',p)
            return
        except Exception:
            g.es_exception()
            self.skip_message('Exception',p)
            return
        t2 = time.clock()
        readlines = g.ReadLinesClass(s0).next
        tokens = list(tokenize.generate_tokens(readlines))
        t3 = time.clock()
        s2 = self.run(p,tokens)
        t4 = time.clock()
        try:
            s2_e = g.toEncodedString(s2)
            node2 = ast.parse(s2_e,filename='before',mode='exec')
            ok = compare_ast(node1, node2)
        except Exception:
            g.es_exception()
            self.skip_message('BeautifierError',p)
            return
        if not ok:
            self.skip_message('BeautifierError',p)
            return
        t5 = time.clock()
        # Restore the tags after the compare
        s3 = uncomment_leo_lines(comment_string,p,s2)
        self.replace_body(p,s3)
        # Update the stats
        self.n_input_tokens += len(tokens)
        self.n_output_tokens += len(self.code_list)
        self.n_strings += len(s3)
        self.parse_time += (t2-t1)
        self.tokenize_time += (t3-t2)
        self.beautify_time += (t4-t3)
        self.check_time += (t5-t4)
        self.total_time += (t5-t1)
    #@+node:ekr.20150526194715.1: *4* ptb.run
    def run(self,p,tokens):
        '''
        The main line of PythonTokenBeautifier class.
        Called by prettPrintNode & test_beautifier.
        '''

        def oops():
            g.trace('unknown kind',self.kind)

        self.code_list = []
        self.state_stack = []
        self.file_start()
        for token5tuple in tokens:
            t1,t2,t3,t4,t5 = token5tuple
            self.kind = token.tok_name[t1].lower()
            self.val = g.toUnicode(t2)
            self.raw_val = g.toUnicode(t5)
            # g.trace('%10s %r'% (self.kind,self.val))
            func = getattr(self,'do_' + self.kind,oops)
            func()
        self.file_end()
        return ''.join([z.to_string() for z in self.code_list])
    #@+node:ekr.20150526194736.1: *3* ptb.Input token Handlers
    #@+node:ekr.20150526203605.1: *4* ptb.do_comment
    def do_comment(self):
        '''Handle a comment token.'''
        s = self.raw_val.rstrip()
        n1 = len(self.lws)
        n2 = g.computeLeadingWhitespaceWidth (s,self.tab_width)
        if n2 > n1:
            self.add_token('indent-comment',' '*(n2-n1))
            self.add_token('comment',self.val)
        else:
            self.blank()
            self.add_token('comment',self.val)
    #@+node:ekr.20041021102938: *4* ptb.do_endmarker
    def do_endmarker (self):
        '''Handle an endmarker token.'''
        pass
    #@+node:ekr.20041021102340.1: *4* ptb.do_errortoken
    def do_errortoken (self):
        '''Handle an errortoken token.'''
        # This code is executed for versions of Python earlier than 2.4
        if self.val == '@':
            self.op(self.val)
    #@+node:ekr.20041021102340.2: *4* ptb.do_indent & do_dedent
    def do_dedent (self):
        '''Handle dedent token.'''
        self.level -= 1
        self.lws = self.level*self.tab_width*' '
        self.line_start()
        state = self.state_stack[-1]
        if state.kind == 'indent' and state.value == self.level:
            self.state_stack.pop()
            state = self.state_stack[-1]
            if state.kind in ('class','def'):
                self.state_stack.pop()
                self.blank_lines(1)
                    # Most Leo nodes aren't at the top level of the file.
                    # self.blank_lines(2 if self.level == 0 else 1)

    def do_indent (self):
        '''Handle indent token.'''
        self.level += 1
        # assert self.val == ' '*self.tab_width*self.level,(repr(self.val),self.level,g.callers())
        self.lws = self.val
        self.line_start()
    #@+node:ekr.20041021101911.5: *4* ptb.do_name
    def do_name(self):
        '''Handle a name token.'''
        name = self.val
        if name in ('class','def'):
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
            self.push_state('indent',self.level)
                # For trailing lines after inner classes/defs.
            self.word(name)
        elif name in ('and','in','not','not in','or'):
            self.word_op(name)
        else:
            self.word(name)
    #@+node:ekr.20041021101911.3: *4* ptb.do_newline
    def do_newline (self):
        '''Handle a regular newline.'''
        self.line_end()
    #@+node:ekr.20141009151322.17828: *4* ptb.do_nl
    def do_nl(self):
        '''Handle a continuation line.'''
        self.line_end()
    #@+node:ekr.20041021101911.6: *4* ptb.do_number
    def do_number (self):
        '''Handle a number token.'''
        self.add_token('number',self.val)
    #@+node:ekr.20040711135244.11: *4* ptb.do_op
    def do_op (self):
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
        elif val in '+-':
            self.possible_unary_op(val)
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
        self.add_token('string',self.val)
        self.blank()
            # This does retain the string's spelling.
    #@+node:ekr.20150526201902.1: *3* ptb.Output token generators
    #@+node:ekr.20150526195542.1: *4* ptb.add_token
    def add_token(self,kind,value=''):
        '''Add a token to the code list.'''
        # g.trace(kind,repr(value))
        tok = self.OutputToken(kind,value)
        self.code_list.append(tok)
    #@+node:ekr.20150526201701.3: *4* ptb.arg_start & arg_end
    def arg_end(self):
        '''Add a token indicating the end of an argument list.'''
        self.add_token('arg-end')
        
    def arg_start(self):
        '''Add a token indicating the start of an argument list.'''
        self.add_token('arg-start')
    #@+node:ekr.20150526201701.4: *4* ptb.blank
    def blank(self):
        '''Add a blank request on the code list.'''
        prev = self.code_list[-1]
        if prev.kind not in (
            'blank','blank-lines',
                # Suppress duplicates.
            'file-start',
            'line-start','line-end','line-indent',
            'unary-op',
                # These tokens implicitly suppress blanks.
            'arg-start','lt','op-no-blanks',
                # These tokens explicity suppress blanks.
        ):
            self.add_token('blank',' ')
    #@+node:ekr.20150526201701.5: *4* ptb.blank_lines
    def blank_lines(self,n):
        '''
        Add a request for n blank lines to the code list.
        Multiple blank-lines request yield at least the maximum of all requests.
        '''
        self.clean_blank_lines()
        kind = self.code_list[-1].kind
        if kind == 'file-start':
            self.add_token('blank-lines',n)
        else:
            for i in range(0,n+1):
                self.add_token('line-end','\n')
            # Retain the intention for debugging.
            self.add_token('blank-lines',n)
            self.add_token('line-indent',self.lws)
    #@+node:ekr.20150526201701.6: *4* ptb.clean
    def clean(self,kind):
        '''Remove the last item of token list if it has the given kind.'''
        prev = self.code_list[-1]
        if prev.kind == kind:
            self.code_list.pop()
            return True
        else:
            return False

    #@+node:ekr.20150527175750.1: *4* ptb.clean_blank_lines
    def clean_blank_lines(self):
        '''Remove all vestiges of previous lines.'''
        table = ('blank-lines','line-end','line-indent')
        while True:
            for kind in table:
                if self.clean(kind):
                    break
            else:
                break
    #@+node:ekr.20150526201701.8: *4* ptb.file_start & file_end
    def file_end(self):
        '''
        Add a file-end token to the code list.
        Retain exactly one line-end token.
        '''
        self.clean_blank_lines()
        self.add_token('line-end','\n')
        # self.add_token('line-end','\n')
        self.add_token('file-end')

    def file_start(self):
        '''Add a file-start token to the code list and the state stack.'''
        self.add_token('file-start')
        self.push_state('file-start')
    #@+node:ekr.20150526201701.9: *4* ptb.line_start & line_end
    def line_end(self):
        '''Add a line-end request to the code list.'''
        prev = self.code_list[-1]
        if prev.kind == 'file-start':
            return
        if self.delete_blank_lines:
            self.clean_blank_lines()
        self.clean('line-indent')
        self.add_token('line-end','\n')
        self.add_token('line-indent',self.lws)
            # Add then indentation for all lines
            # until the next indent or unindent token.

    def line_start(self):
        '''Add a line-start request to the code list.'''
        self.clean('line-indent')
        self.add_token('line-indent',self.lws)
    #@+node:ekr.20150526201701.11: *4* ptb.lt & rt
    def lt(self,s):
        '''Add a left paren request to the code list.'''
        assert s in '([{',repr(s)
        self.paren_level += 1
        self.clean('blank')
        prev = self.code_list[-1]
        # g.trace(prev.kind,prev.value)
        if prev.kind in ('op','word-op'):
            self.blank()
            self.add_token('op-no-blanks',s)
        elif prev.kind == 'word':
            self.add_token('op-no-blanks',s)
        elif prev.kind == 'op':
            self.op(s)
        else:
            self.op_no_blanks(s)
        
    def rt(self,s):
        '''Add a right paren request to the code list.'''
        assert s in ')]}',repr(s)
        self.paren_level -= 1
        prev = self.code_list[-1]
        if prev.kind == 'arg-end':
            # Remove a blank token preceding the arg-end token.
            prev = self.code_list.pop()
            self.clean('blank')
            self.code_list.append(prev)   
        else:
            self.clean('blank')
        self.add_token('rt',s)
    #@+node:ekr.20150526201701.12: *4* ptb.op*
    def op(self,s):
        '''Add op token to code list.'''
        assert s and g.isString(s),repr(s)
        self.blank()
        self.add_token('op',s)
        self.blank()
        
    def op_blank(self,s):
        '''Remove a preceding blank token, then add op and blank tokens.'''
        assert s and g.isString(s),repr(s)
        self.clean('blank')
        self.add_token('op',s)
        self.blank()
        
    def op_no_blanks(self,s):
        '''Add an operator *not* surrounded by blanks.'''
        self.clean('blank')
        self.add_token('op-no-blanks',s)
    #@+node:ekr.20150527213419.1: *4* ptb.possible_unary_op & unary_op
    def possible_unary_op(self,s):
        '''Add a unary or binary op to the token list.'''
        self.clean('blank')
        prev = self.code_list[-1]
        if prev.kind in ('lt','op','op-no-blanks'):
            self.unary_op(s)
        else:
            self.op(s)

    def unary_op(self,s):
        '''Add an operator request to the code list.'''
        assert s and g.isString(s),repr(s)
        self.blank()
        self.add_token('unary-op',s)
    #@+node:ekr.20150526201701.13: *4* ptb.word & word_op
    def word(self,s):
        '''Add a word request to the code list.'''
        assert s and g.isString(s),repr(s)
        self.blank()
        self.add_token('word',s)
        self.blank()

    def word_op(self,s):
        '''Add a word request to the code list.'''
        assert s and g.isString(s),repr(s)
        self.blank()
        self.add_token('word-op',s)
        self.blank()
    #@+node:ekr.20150530064617.1: *3* ptb.Utils
    #@+node:ekr.20150528171420.1: *4* ppp.replace_body
    def replace_body (self,p,s):
        '''Replace the body with the pretty version.'''
        c,u = self.c,self.c.undoer
        undoType = 'Pretty Print'
        if p.b == s:
            return
        self.n_changed_nodes += 1
        if not self.changed:
            # Start the group.
            u.beforeChangeGroup(p,undoType)
            self.changed = True
            self.dirtyVnodeList = []
        undoData = u.beforeChangeNodeContents(p)
        c.setBodyString(p,s)
        dirtyVnodeList2 = p.setDirty()
        self.dirtyVnodeList.extend(dirtyVnodeList2)
        u.afterChangeNodeContents(p,undoType,undoData,dirtyVnodeList=self.dirtyVnodeList)
    #@+node:ekr.20150528180738.1: *4* ptb.end_undo
    def end_undo (self):
        '''Complete undo processing.'''
        c = self.c ; u = c.undoer ; undoType = 'Pretty Print'
        current = c.p
        if self.changed:
            # Tag the end of the command.
            u.afterChangeGroup(current,undoType,dirtyVnodeList=self.dirtyVnodeList)
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
    def push_state(self,kind,value=None):
        '''Append a state to the state stack.'''
        state = self.ParseState(kind,value)
        self.state_stack.append(state)
    #@+node:ekr.20150528192109.1: *4* ptb.skip_message
    def skip_message(self,s,p):
        '''Print a standard message about skipping a node.'''
        message = '%s. skipped:' % s
        g.warning('%22s %s' % (message,p.h))
    #@-others
#@-others
if __name__ == "__main__":
    main()
#@@language python
#@@tabwidth -4
#@-leo
