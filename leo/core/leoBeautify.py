#@+leo-ver=5-thin
#@+node:ekr.20150521115018.1: * @file leoBeautify.py
'''Leo's beautification classes.'''

import leo.core.leoGlobals as g
import leo.core.leoAst as leoAst
# import leo.external.PythonTidy as tidy
import ast
import glob
import os
import time
import token
import tokenize

#@+others
#@+node:ekr.20150524215322.1: ** dumpTokens & dumpToken
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
#@+node:ekr.20150521114057.1: ** test_beautifier (prints stats)
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
    if settings.get('code_list'):
        print('==================== code_list')
        for i,z in enumerate(beautifier.code_list):
            print('%4s %s' % (i,z))
    if settings.get('output_string'):
        print('==================== output_string')
        for i,z in enumerate(g.splitLines(s2)):
            print('%4s %s' % (i+1,z.rstrip()))
    if settings.get('stats'):
        print('==================== stats')
        print('tokens:   %s' % len(tokens))
        print('code_list %s' % len(beautifier.code_list))
        print('len(s2):  %s' % len(s2))
        print('parse:    %4.2f sec.' % (t2-t1))
        print('tokenize: %4.2f sec.' % (t3-t2))
        print('format:   %4.2f sec.' % (t4-t3))
        print('total:    %4.2f sec.' % (t4-t1))
    if settings.get('ast-compare'):
        s2 = g.toEncodedString(s2)
        node2 = ast.parse(s2,filename='before',mode='exec')
        if leoAst.compare_ast(node1, node2):
            print('==== passed: %s' % h)
        else:
            print('==== failed: %s' % h)
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
    #@+node:ekr.20150519111713.1: *3*  ptb.ctor
    def __init__ (self,c):
        '''Ctor for PythonPrettyPrinter class.'''
        self.c = c
        self.code_list = []
            # The list of output tokens.
        self.bracketLevel = 0
        self.changed = False
        self.continuation = False # True: line ends with backslash-newline.
        self.indent = ' ' * 4
        self.dirtyVnodeList = []
        ### self.dumping = False
        ### self.erow = self.ecol = 0 # The ending row/col of the token.
        self.last_name = None # The name of the previous token type.
        self.level = 0
        self.line_number = 0 # Same as self.srow
        ### self.lines = [] # List of lines.
        ### self.n_tokens = 0 # Number of tokens processed.
        ### self.name = None
        ### self.p = c.p
        self.paren_level = 0
        self.s = None # The string containing the line.
        self.square_bracket_level = 0
        ### self.srow = self.scol = 0 # The starting row/col of the token.
        self.starts_line = True # True: the token starts a line.
        self.trailing_ws = '' # The whitespace following *this* token.
        self.val = None
        
    #@+node:ekr.20150526201902.1: *3* ptb.Code generators
    #@+node:ekr.20150526195542.1: *4* ptb.add_token
    def add_token(self,kind,value=''):
        '''Add a token to the code list.'''
        # g.trace(kind,repr(value))
        tok = self.OutputToken(kind,self.level,value)
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
            'file-start','line-start','line-end',
                # These tokens implicitly suppress blanks.
            'arg-start','lit-no-blanks','lt',
                # These tokens explicity suppress blanks.
        ):
            self.add_token('blank',' ')
    #@+node:ekr.20150526201701.5: *4* ptb.blank_lines
    def blank_lines(self,n):
        '''
        Add a request for n blank lines to the code list.
        Multiple blank-lines request yield at least the maximum of all requests.
        '''
        # Count the number of 'consecutive' end-line tokens, ignoring blank-lines tokens.
        prev_lines = 0
        i = len(self.code_list)-1 # start-file token guarantees i >= 0
        while True:
            kind = self.code_list[i].kind
            if kind == 'file-start':
                prev_lines = n ; break
            elif kind == 'blank-lines':
                i -= 1
            elif kind == 'line-end':
                i -= 1 ; prev_lines += 1
            else: break
        # g.trace('i: %3s n: %s prev: %s' % (len(self.code_list),n,prev_lines))
        while prev_lines <= n:
            self.line_end()
            prev_lines += 1
        # Retain the intention for debugging.
        self.add_token('blank-lines',n)
    #@+node:ekr.20150526201701.6: *4* ptb.clean
    def clean(self,kind):
        '''Remove the last item of token list if it has the given kind.'''
        prev = self.code_list[-1]
        if prev.kind == kind:
            self.code_list.pop()
    #@+node:ekr.20150526201701.7: *4* ptb.conditional_line_start
    def conditional_line_start(self):
        '''Add a conditional line start to the code list.'''
        prev = self.code_list[-1]
        if prev.kind != 'start-line':
            self.add_token('start-line')
    #@+node:ekr.20150526201701.8: *4* ptb.file_start & file_end
    def file_end(self):
        '''
        Add a file-end token to the code list.
        Retain exactly one line-end token.
        '''
        while True:
            prev = self.code_list[-1]
            if prev.kind in ('blank-lines','line-end'):
                self.code_list.pop()
            else:
                break
        self.add_token('line-end')
        self.add_token('file-end')

    def file_start(self):
        '''Add a file-start token to the code list.'''
        self.add_token('file-start')
    #@+node:ekr.20150526201701.9: *4* ptb.line_start & line_end
    def line_end(self):
        '''Add a line-end request to the code list.'''
        prev = self.code_list[-1]
        if prev.kind != 'file-start':
            self.add_token('line-end','\n')

    def line_start(self):
        '''Add a line-start request to the code list.'''
        prev = self.code_list[-1]
        if prev.kind != 'line-start':
            self.add_token('line-start',self.indent)
    #@+node:ekr.20150526201701.10: *4* ptb.lit*
    def lit(self,s):
        '''Add a request for a literal to the code list.'''
        assert s and g.isString(s),repr(s)
        # g.trace(repr(s),g.callers())
        self.add_token('lit',s)
        
    def lit_blank(self,s):
        '''Add request for a liter (no previous blank) followed by a blank.'''
        self.clean('blank')
        self.lit(s)
        self.blank()

    def lit_no_blanks(self,s):
        '''Add a request for a literal *not* surrounded by blanks.'''
        self.clean('blank')
        self.add_token('lit-no-blanks',s)
    #@+node:ekr.20150526201701.11: *4* ptb.lt & rt
    def lt(self,s):
        '''Add a left paren request to the code list.'''
        assert s in '([{',repr(s)
        self.add_token('lt',s)
        
    def rt(self,s):
        '''Add a right paren request to the code list.'''
        assert s in ')]}',repr(s)
        prev = self.code_list[-1]
        if prev.kind == 'arg-end':
            # Remove a blank token preceding the arg-end token.
            prev = self.code_list.pop()
            self.clean('blank')
            self.code_list.append(prev)   
        else:
            self.clean('blank')
        self.add_token('rt',s)
    #@+node:ekr.20150526201701.12: *4* ptb.op
    def op(self,s):
        '''Add an operator request to the code list.'''
        assert s and g.isString(s),repr(s)
        self.blank()
        self.lit(s)
        self.blank()
    #@+node:ekr.20150526201701.13: *4* ptb.word
    def word(self,s):
        '''Add a word request to the code list.'''
        assert s and g.isString(s),repr(s)
        self.blank()
        self.add_token('word',s)
        self.blank()
    #@+node:ekr.20150526194736.1: *3* ptb.Token Handlers
    #@+node:ekr.20150526203605.1: *4* ptb.do_comment
    def do_comment(self):
        '''Handle a comment token.'''
    #@+node:ekr.20041021102938: *4* ptb.do_endmarker
    def do_endmarker (self):
        '''Handle an endmarker token.'''
    #@+node:ekr.20041021102340.1: *4* ptb.do_errortoken
    def do_errortoken (self):
        '''Handle an errortoken token.'''

        # This code is executed for versions of Python earlier than 2.4
        # if self.val == '@':
            # # Preserve whitespace after @.
            # i = g.skip_ws(self.s,self.scol+1)
            # ws = self.s[self.scol+1:i]
            # if ws:
                # self.array.append(ws)
    #@+node:ekr.20041021102340.2: *4* ptb.do_indent & do_dedent
    def do_dedent (self):
        '''Handle dedent token.'''
        # g.trace(repr(self.val))
        self.indent = self.val
        # g.trace('****',repr(self.leading_ws))
       
    def do_indent (self):
        '''Handle indent token.'''
        self.indent = self.val
        # g.trace(repr(self.val))
    #@+node:ekr.20041021101911.5: *4* ptb.do_name
    def do_name(self):
        '''Handle a name token.'''
        # Ensure whitespace or start-of-line precedes the name.
        val = self.val
        self.word(val) ###
        if val in ('if','else','and','or','not'):
            # Make *sure* we never add an extra space.
            pass
            ###
            # if self.array and self.array[-1].endswith(' '):
                # self.array.append('%s ' % val)
            # elif self.array:
                # self.array.append(' %s ' % val)
            # else:
                # self.array.append('%s ' % val)
        elif val == 'def':
            pass
            ###
            # if True and self.lines:
                # g.trace('DEF',repr(self.leading_ws))
                # self.array.append('\n')
                # self.array.append(self.leading_ws)
            # s = '%s%s' % (val,self.trailing_ws)
            # self.array.append(s)
        else:
            pass
            ###
            # s = '%s%s' % (val,self.trailing_ws)
            # if s == 'lambda': g.trace(repr(str(s)),repr(str(self.trailing_ws)))
            # self.array.append(s)
    #@+node:ekr.20041021101911.3: *4* ptb.do_newline
    def do_newline (self):
        '''Handle a regular newline.'''
        self.line_end()
        self.line_start()
        # if self.continuation:
            # self.array.append('\\')
            # self.continuation = False
        # elif self.array:
            # # Remove trailing whitespace.
            # # This never removes trailing whitespace from multi-line tokens.
            # self.array[-1] = self.array[-1].rstrip()
        # self.array.append('\n')
        # self.putArray()
    #@+node:ekr.20141009151322.17828: *4* ptb.do_nl
    def do_nl(self):
        '''Handle a continuation line.'''
        self.line_end()
        self.line_start()

    #@+node:ekr.20041021101911.6: *4* ptb.do_number
    def do_number (self):

        self.add_token('number',self.val)
    #@+node:ekr.20040711135244.11: *4* ptb.do_op
    def do_op (self):
        '''Put an operator.'''
        val = self.val
        self.op(val)
        return ###
        # outer = self.paren_level == 0 and self.square_bracket_level == 0
        # ws = self.trailing_ws
        # if val in '([{':
            # # From pep 8: Avoid extraneous whitespace immediately inside
            # # parentheses, brackets or braces.
            # pass
            # ###
            # # prev = self.array and self.array[-1]
            # # # strip = self.paren_level > 0 and prev.strip() not in (',','lambda','else')
            # # # g.trace('====',repr(prev))
            # # strip = self.paren_level > 0
            # # self.put(val,strip=strip)
            # # if   val == '(': self.paren_level += 1
            # # elif val == '[': self.square_bracket_level += 1
        # elif val in '}])':
            # # From pep 8: Avoid extraneous whitespace immediately inside
            # # parentheses, brackets or braces.
            # pass
            # ### 
            # # self.put(val+ws,strip=True)
            # # if   val == ')': self.paren_level -= 1
            # # elif val == ']': self.square_bracket_level -= 1
        # elif val == '=':
            # # From pep 8: Don't use spaces around the = sign when used to indicate
            # # a keyword argument or a default parameter value.
            # pass
            # ###
            # # if self.paren_level == 0:
                # # # This is only an approximation.
                # # self.put(' %s ' % val)
            # # else:
                # # self.put(val)
        # elif val in ('==','+=','-=','*=','**=','/=','//=','%=','!=','<=','>=','<','>','<>'):
            # # From pep 8: always surround these binary operators with a single space on either side.
            # self.lit(val)
            # ### self.put(' %s ' % val)
        # elif val in '+-':
            # # Special case for possible unary operator.
            # pass
            # ###
            # # if self.paren_level == 0:
                # # if ws:
                    # # self.put(' %s ' % val,strip=True)
                # # else:
                    # # self.put(val,strip=False)
            # # else:
                # # self.put(val,strip=True)
        # elif val in ('^','~','*','**','&','|','/','//'):
            # # From pep 8: If operators with different priorities are used,
            # # consider adding whitespace around the operators with the lowest priority(ies).
            # # g.trace(repr(str(val)),repr(str(ws)))
            # pass
            # ###
            # # if val in ('*','**'):
                # # # Highest priority.
                # # self.put(val,strip=True)
            # # else:
                # # # Lower priority:
                # # if 1:
                    # # self.put(' %s ' % val,strip=True)
                # # elif 1:
                    # # # Treat all operators the same.  Boo hoo.
                    # # self.put(val,strip=True)
                # # else:
                    # # # Alas, this does not play well with names.
                    # # self.put(val+ws,strip=False)
        # elif val in ',;':
            # # From pep 8: Avoid extraneous whitespace immediately before comma, semicolon, or colon.
            # self.lit_blank(val)
        # elif val == ':':
            # # A very hard case.
            # prev = self.code_list[-1]
            # ###
            # # if prev in ('else ',':',': '):
                # # self.put(val+ws,strip=True)
            # # else:
                # # # We can leave the leading whitespace.
                # # self.put(val+ws,strip=False)
        # elif val in ('%',
                     # '<<',
                     # '>>'
                    # ):
            # # Add leading and trailing blank.
            # self.op(val)
        # else:
            # self.lit(val)
    #@+node:ekr.20150526204248.1: *4* ptb.do_string
    def do_string(self):
        
        self.add_token('string',self.val)
    #@+node:ekr.20150526194715.1: *3* ptb.run
    def run(self,p,tokens):
        '''The main line of PythonTokenBeautifier class.'''

        def oops():
            g.trace('unknown kind',self.kind)

        self.file_start()
        for token5tuple in tokens:
            t1,t2,t3,t4,t5 = self.token5tuple = token5tuple
            self.kind = token.tok_name[t1].lower()
            self.val = g.toUnicode(t2)
            # g.trace('%10s %r'% (self.kind,self.val))
            func = getattr(self,'do_' + self.kind,oops)
            func()
        self.file_end()
        return ''.join([z.to_string() for z in self.code_list])
        
    #@+node:ekr.20150521122451.1: *3* ptb.replace_body (not used yet)
    def replace_body (self,p,s):
        '''Replace p.b with s.'''
        c,u,undoType = self.c,self.c.undoer,'Pretty Print'
        if p.b != s:
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
    #@+node:ekr.20150523132558.1: *3* class OutputToken
    class OutputToken:
        '''A class representing items on the LeoTidy code list.'''
        
        def __init__(self,kind,level,value):
            self.kind = kind
            self.level = level
            self.value = value
            
        def __repr__(self):
            return '%10s %s' % (self.kind,repr(self.value))
       
        __str__ = __repr__

        def to_string(self):
            '''Convert an output token to a string.'''
            return self.value if g.isString(self.value) else ''
            
       
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
