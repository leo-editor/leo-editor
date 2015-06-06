# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20150605175037.1: * @file leoCheck.py
#@@first
'''Experimental code checking for Leo.'''
import leo.core.leoGlobals as g
import glob
import re
import time
import token
import tokenize
#@+others
#@+node:ekr.20150525123715.1: ** class ProjectUtils
class ProjectUtils:
    '''A class to compute the files in a project.'''
    # To do: get project info from @data nodes.
    #@+others
    #@+node:ekr.20150525123715.2: *3* pu.files_in_dir
    def files_in_dir(self, theDir, recursive=True, extList=None, excludeDirs=None):
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
                    fn = g.os_path_finalize_join(root, z)
                    junk, ext = g.os_path_splitext(fn)
                    if not extList or ext in extList:
                        result.append(fn)
                if excludeDirs and dirs:
                    for z in dirs:
                        if z in excludeDirs:
                            dirs.remove(z)
        else:
            for ext in extList:
                result.extend(glob.glob('%s.*%s' % (theDir, ext)))
        return sorted(list(set(result)))
    #@+node:ekr.20150525123715.3: *3* pu.get_project_directory
    def get_project_directory(self, name):
        # Ignore everything after the first space.
        i = name.find(' ')
        if i > -1:
            name = name[: i].strip()
        leo_path, junk = g.os_path_split(__file__)
        d = {
            # Change these paths as required for your system.
            'coverage': r'C:\Python26\Lib\site-packages\coverage-3.5b1-py2.6-win32.egg\coverage',
            'leo': r'C:\leo.repo\leo-editor\leo\core',
            'lib2to3': r'C:\Python26\Lib\lib2to3',
            'pylint': r'C:\Python26\Lib\site-packages\pylint',
            'rope': r'C:\Python26\Lib\site-packages\rope-0.9.4-py2.6.egg\rope\base',
            'test': g.os_path_finalize_join(g.app.loadDir, '..', 'test-proj'),
        }
        dir_ = d.get(name.lower())
        # g.trace(name,dir_)
        if not dir_:
            g.trace('bad project name: %s' % (name))
        if not g.os_path_exists(dir_):
            g.trace('directory not found:' % (dir_))
        return dir_ or ''
    #@+node:ekr.20150525123715.4: *3* pu.project_files
    def project_files(self, name, force_all=False):
        '''Return a list of all files in the named project.'''
        # Ignore everything after the first space.
        i = name.find(' ')
        if i > -1:
            name = name[: i].strip()
        leo_path, junk = g.os_path_split(__file__)
        d = {
            # Change these paths as required for your system.
            'coverage': (
                r'C:\Python26\Lib\site-packages\coverage-3.5b1-py2.6-win32.egg\coverage',
                ['.py'], ['.bzr', 'htmlfiles']),
            'leo': (
                r'C:\leo.repo\leo-editor\leo\core',
                ['.py'], ['.git']), # ['.bzr']
            'lib2to3': (
                r'C:\Python26\Lib\lib2to3',
                ['.py'], ['tests']),
            'pylint': (
                r'C:\Python26\Lib\site-packages\pylint',
                ['.py'], ['.bzr', 'test']),
            'rope': (
                r'C:\Python26\Lib\site-packages\rope-0.9.4-py2.6.egg\rope\base', ['.py'], ['.bzr']),
            # 'test': (
                # g.os_path_finalize_join(leo_path,'test-proj'),
                # ['.py'],['.bzr']),
        }
        data = d.get(name.lower())
        if not data:
            g.trace('bad project name: %s' % (name))
            return []
        theDir, extList, excludeDirs = data
        files = self.files_in_dir(theDir, recursive=True, extList=extList, excludeDirs=excludeDirs)
        if files:
            if name.lower() == 'leo':
                for exclude in ['__init__.py', 'format-code.py']:
                    files = [z for z in files if not z.endswith(exclude)]
                table = (
                    r'C:\leo.repo\leo-editor\leo\commands',
                    # r'C:\leo.repo\leo-editor\leo\plugins\importers',
                    # r'C:\leo.repo\leo-editor\leo\plugins\writers',
                )
                for dir_ in table:
                    files2 = self.files_in_dir(dir_, recursive=True, extList=['.py',], excludeDirs=[])
                    files2 = [z for z in files2 if not z.endswith('__init__.py')]
                    # g.trace(g.os_path_exists(dir_), dir_, '\n'.join(files2))
                    files.extend(files2)
                files.extend(glob.glob(r'C:\leo.repo\leo-editor\leo\plugins\qt_*.py'))
                fn = g.os_path_finalize_join(theDir, '..', 'plugins', 'qtGui.py')
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
#@+node:ekr.20150604164113.1: ** class ShowData
class ShowData:
    #@+others
    #@+node:ekr.20150604165500.1: *3*  ctor
    def __init__(self, c):
        self.c = c
        self.calls_d = {}
        self.classes_d = {}
        self.context_stack = []
        self.context_indent = -1
        self.defs_d = {}
        self.files = None
        self.returns_d = {}
        # Statistics
        self.n_matches = 0
        self.tot_lines = 0
        self.tot_s = 0
        # From beautifier
        ### self.n_changed_nodes = 0
        self.n_input_tokens = 0
        self.n_output_tokens = 0
        ### self.n_strings = 0
        ### self.parse_time = 0.0
        ### self.tokenize_time = 0.0
        ### self.beautify_time = 0.0
        ### self.check_time = 0.0
        ### self.total_time = 0.0
        # Regex patterns. These are really a premature optimization.
        if 1: ### To be removed.
            r_class = r'class[ \t]+([a-z_A-Z][a-z_A-Z0-9]*).*:'
            r_def = r'def[ \t]+([a-z_A-Z][a-z_A-Z0-9]*)[ \t]*\((.*)\)'
            r_return = r'(return[ \t].*)$'
            r_call = r'([a-z_A-Z][a-z_A-Z0-9]*)[ \t]*\(([^)]*)\)'
            self.r_all = re.compile('|'.join([r_class, r_def, r_return, r_call,]))
        # From Beautifier
        # Globals...
        self.code_list = [] # The list of output tokens.
        # The present line and token...
        self.last_line_number = 0
        self.raw_val = None # Raw value for strings, comments.
        self.s = None # The string containing the line.
        self.val = None
        # State vars...
        self.backslash_seen = False
        ### self.decorator_seen = False
        self.level = 0 # indentation level.
        self.lws = '' # Leading whitespace.
            # Typically ' '*self.tab_width*self.level,
            # but may be changed for continued lines.
        self.paren_level = 0 # Number of unmatched left parens.
        self.state_stack = [] # Stack of ParseState objects.
        # Settings...
        self.tab_width = abs(c.tab_width) if c else 4
        # Undo vars
        ### self.changed = False
        ### self.dirtyVnodeList = []
    #@+node:ekr.20150605203204.2: *3* class OutputToken
    class OutputToken:
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
    #@+node:ekr.20150605203204.3: *3* class ParseState
    class ParseState:
        '''A class representing items in the parse state stack.'''

        def __init__(self, kind, value):
            self.kind = kind
            self.value = value

        def __repr__(self):
            return 'State: %10s %s' % (self.kind, repr(self.value))

        __str__ = __repr__
    #@+node:ekr.20150605203204.8: *3* Input token Handlers
    #@+node:ekr.20150605203204.9: *4* do_comment
    def do_comment(self):
        '''Handle a comment token.'''
        raw_val = self.raw_val.rstrip()
        val = self.val.rstrip()
        entire_line = raw_val.lstrip().startswith('#')
        # g.trace(entire_line,raw_val)
        self.backslash_seen = False
            # Putting the comment will put the backslash.
        if entire_line:
            self.clean('line-indent')
            self.add_token('comment', raw_val)
        else:
            self.blank()
            self.add_token('comment', val)
    #@+node:ekr.20150605203204.10: *4* do_endmarker
    def do_endmarker(self):
        '''Handle an endmarker token.'''
    #@+node:ekr.20150605203204.11: *4* do_errortoken
    def do_errortoken(self):
        '''Handle an errortoken token.'''
        # This code is executed for versions of Python earlier than 2.4
        if self.val == '@':
            self.op(self.val)
    #@+node:ekr.20150605203204.12: *4* do_indent & do_dedent
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
    #@+node:ekr.20150605203204.13: *4* do_name (handle class, def, return)
    #@@nobeautify

    def do_name(self):
        '''Handle a name token.'''
        name = self.val
        if name in ('class', 'def'):
            ### Not needed
            # self.decorator_seen = False
            # state = self.state_stack[-1]
            # if state.kind == 'decorator':
                # # self.clean_blank_lines()
                # # self.line_end()
                # self.state_stack.pop()
            # # else:
                # # self.blank_lines(1)
            ########## Set flag for below
            self.push_state(name)
            self.push_state('indent', self.level)
                # For trailing lines after inner classes/defs.
            self.word(name)
        elif name in ('and', 'in', 'not', 'not in', 'or'):
            self.word_op(name)
        else:
            ########## Test for class/def name here
            self.word(name)

            ### To do: handle def.
            # self.update_context(fn, indent, 'def', s)
            # for i, name in enumerate(m.groups()):
                # if name:
                    # aList = self.defs_d.get(name, [])
                    # def_tuple = self.context_stack[: -1], s
                    # aList.append(def_tuple)
                    # self.defs_d[name] = aList
                    # break

            ### To do: handle class
            # self.update_context(fn, indent, 'class', s)
            # for i, name in enumerate(m.groups()):
                # if name:
                    # aList = self.classes_d.get(name, [])
                    # class_tuple = self.context_stack[: -1], s
                    # aList.append(class_tuple)
                    # self.classes_d[name] = aList

            ### To do: handle return
            # context, name = self.context_names()
            # j = s.find('#')
            # if j > -1: s = s[: j]
            # s = s.strip()
            # if s:
                # aList = self.returns_d.get(name, [])
                # return_tuple = context, s
                # aList.append(return_tuple)
                # self.returns_d[name] = aList
    #@+node:ekr.20150605203204.14: *4* do_newline
    def do_newline(self):
        '''Handle a regular newline.'''
        self.line_end()
    #@+node:ekr.20150605203204.15: *4* do_nl
    def do_nl(self):
        '''Handle a continuation line.'''
        self.line_end()
    #@+node:ekr.20150605203204.16: *4* do_number
    def do_number(self):
        '''Handle a number token.'''
        self.add_token('number', self.val)
    #@+node:ekr.20150605203204.17: *4* do_op (changed)
    def do_op(self):
        '''Handle an op token.'''
        val = self.val
        if val == '.':
            self.op_no_blanks(val)
        elif val == '@':
            ###
            # if not self.decorator_seen:
                # self.blank_lines(1)
                # self.decorator_seen = True
            self.op_no_blanks(val)
            ### self.push_state('decorator')
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
    #@+node:ekr.20150605203204.18: *4* do_string
    def do_string(self):
        '''Handle a 'string' token.'''
        self.add_token('string', self.val)
        if self.val.find('\\\n'):
            self.backslash_seen = False
            # This does retain the string's spelling.
        self.blank()
    #@+node:ekr.20150605203204.19: *3* Output token generators
    #@+node:ekr.20150605203204.27: *4* file_start & file_end
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
    #@+node:ekr.20150605203204.22: *4* backslash
    def backslash(self):
        '''Add a backslash token and clear .backslash_seen'''
        self.add_token('backslash', '\\')
        self.add_token('line-end', '\n')
        self.line_indent()
        self.backslash_seen = False
    #@+node:ekr.20150605203204.23: *4* blank
    def blank(self):
        '''Add a blank request on the code list.'''
        prev = self.code_list[-1]
        if not prev.kind in (
            'blank', ### 'blank-lines',
            'file-start',
            'line-end', 'line-indent',
            'lt', 'op-no-blanks', 'unary-op',
        ):
            self.add_token('blank', ' ')
    #@+node:ekr.20150605203204.24: *4* blank_lines (changed)
    def blank_lines(self, n):
        '''
        Add a request for n blank lines to the code list.
        Multiple blank-lines request yield at least the maximum of all requests.
        '''
        self.add_token('line-end', '\n')
        self.line_indent()
        ###
        # self.clean_blank_lines()
        # kind = self.code_list[-1].kind
        # if kind == 'file-start':
            # self.add_token('blank-lines', n)
        # else:
            # for i in range(0, n + 1):
                # self.add_token('line-end', '\n')
            # # Retain the intention for debugging.
            # self.add_token('blank-lines', n)
            # self.line_indent()
    #@+node:ekr.20150605203204.25: *4* clean
    def clean(self, kind):
        '''Remove the last item of token list if it has the given kind.'''
        prev = self.code_list[-1]
        if prev.kind == kind:
            self.code_list.pop()
    #@+node:ekr.20150605203204.26: *4* clean_blank_lines
    def clean_blank_lines(self):
        '''Remove all vestiges of previous lines.'''
        table = ('blank-lines', 'line-end', 'line-indent')
        while self.code_list[-1].kind in table:
            self.code_list.pop()
    #@+node:ekr.20150605203204.28: *4* line_indent
    def line_indent(self, ws=None):
        '''Add a line-indent token if indentation is non-empty.'''
        self.clean('line-indent')
        ws = ws or self.lws
        if ws:
            self.add_token('line-indent', ws)
    #@+node:ekr.20150605203204.29: *4* line_start & line_end
    def line_end(self):
        '''Add a line-end request to the code list.'''
        prev = self.code_list[-1]
        if prev.kind == 'file-start':
            return
        self.clean('blank') # Important!
        ### if self.delete_blank_lines:
        ###    self.clean_blank_lines()
        self.clean('line-indent')
        if self.backslash_seen:
            self.backslash()
        self.add_token('line-end', '\n')
        self.line_indent()
            # Add then indentation for all lines
            # until the next indent or unindent token.

    def line_start(self):
        '''Add a line-start request to the code list.'''
        self.line_indent()
    #@+node:ekr.20150605203204.30: *4* lt (handle calls)
    #@@nobeautify

    def lt(self, s):
        '''Add a left paren request to the code list.'''
        assert s in '([{', repr(s)
        self.paren_level += 1
        self.clean('blank')
        prev = self.code_list[-1]
        # g.trace(prev.kind,prev.value)
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

        ### To do: handle calls
        # for i, name in enumerate(m.groups()):
            # if name:
                # context2, context1 = self.context_names()
                # j = s.find('#')
                # if j > -1:
                    # s = s[: j]
                # s = s.strip().strip(',').strip()
                # if s:
                    # aList = self.calls_d.get(name, [])
                    # call_tuple = context2, context1, s
                    # aList.append(call_tuple)
                    # self.calls_d[name] = aList
                # break
    #@+node:ekr.20150605203204.31: *4* op*
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
    #@+node:ekr.20150605203204.32: *4* possible_unary_op & unary_op
    def possible_unary_op(self, s):
        '''Add a unary or binary op to the token list.'''
        self.clean('blank')
        prev = self.code_list[-1]
        if prev.kind in ('lt', 'op', 'op-no-blanks'):
            self.unary_op(s)
        else:
            self.op(s)

    def unary_op(self, s):
        '''Add an operator request to the code list.'''
        assert s and g.isString(s), repr(s)
        self.blank()
        self.add_token('unary-op', s)
    #@+node:ekr.20150605220143.1: *4* rt
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
    #@+node:ekr.20150605203204.33: *4* star_op
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
    #@+node:ekr.20150605203204.34: *4* star_star_op
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
    #@+node:ekr.20150605203204.35: *4* word & word_op
    def word(self, s):
        '''Add a word request to the code list.'''
        assert s and g.isString(s), repr(s)
        self.blank()
        self.add_token('word', s)
        self.blank()

    def word_op(self, s):
        '''Add a word request to the code list.'''
        assert s and g.isString(s), repr(s)
        self.blank()
        self.add_token('word-op', s)
        self.blank()
    #@+node:ekr.20150604163903.1: *3* run & helpers
    def run(self, files):
        '''Process all files'''
        self.files = files
        t1 = time.clock()
        for fn in files:
            s, e = g.readFileIntoString(fn)
            if s:
                self.tot_s += len(s)
                if 0: # 5 times slower, more accurate.
                    ### The main unsolved problem:
                    ### Determining the end of class/def/return statements.
                    g.trace('%8s %s' % ("{:,}".format(len(s)), g.shortFileName(fn)))
                    readlines = g.ReadLinesClass(s).next
                    tokens = list(tokenize.generate_tokens(readlines))
                    # self.handle_tokens(tokens)
                    # self.n_input_tokens += len(tokens)
                    # self.n_output_tokens += len(self.code_list)
                else: # Fast, inaccurate.
                    self.scan(fn, s)
            else:
                g.trace('skipped', g.shortFileName(fn))
        t2 = time.clock()
            # Get the time exlusive of print time.
        self.show_results()
        g.trace('done: %4.2f sec.' % (t2 - t1))
    #@+node:ekr.20150605203204.7: *4* handle_tokens (slow, accurate)
    def handle_tokens(self, tokens):
        '''Handle all the tokens of a file.'''

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
                ###
                # if self.backslash_seen:
                    # self.backslash()
                    # self.backslash_seen = False
                # Start a new row.
                raw_val = self.raw_val.rstrip()
                ### self.backslash_seen = raw_val.endswith('\\')
                # g.trace('backslash_seen',self.backslash_seen)
                if self.paren_level > 0:
                    s = self.raw_val.rstrip()
                    n = g.computeLeadingWhitespaceWidth(s, self.tab_width)
                    self.line_indent(ws=' ' * n)
                        # Do not set self.lws here!
                self.last_line_number = srow
            # g.trace('%10s %r'% (self.kind,self.val))
            func = getattr(self, 'do_' + self.kind, oops)
            func()
        self.file_end()
        return ''.join([z.to_string() for z in self.code_list])
    #@+node:ekr.20150605054921.1: *4* scan (fast, inaccurate) & helpers
    def scan(self, fn, s):
        g.trace('%8s %s' % ("{:,}".format(len(s)), g.shortFileName(fn)))
        # print(' hit line lvl lws line')
        lines = g.splitLines(s)
        self.tot_lines += len(lines)
        for i, s in enumerate(lines):
            m = re.search(self.r_all, s)
            if m and not s.startswith('@'):
                self.match(fn, i, m, s)
    #@+node:ekr.20150605063318.1: *5* match
    def match(self, fn, i, m, s):
        '''Handle the next match.'''
        trace = False
        self.n_matches += 1
        indent = g.skip_ws(s, 0)
        # Update the context and enter data.
        if g.match_word(s, indent, 'def'):
            self.update_context(fn, indent, 'def', s)
            for i, name in enumerate(m.groups()):
                if name:
                    aList = self.defs_d.get(name, [])
                    def_tuple = self.context_stack[: -1], s
                    aList.append(def_tuple)
                    self.defs_d[name] = aList
                    break
        elif g.match_word(s, indent, 'class'):
            self.update_context(fn, indent, 'class', s)
            for i, name in enumerate(m.groups()):
                if name:
                    aList = self.classes_d.get(name, [])
                    class_tuple = self.context_stack[: -1], s
                    aList.append(class_tuple)
                    self.classes_d[name] = aList
        elif s.find('return') > -1:
            context, name = self.context_names()
            j = s.find('#')
            if j > -1: s = s[: j]
            s = s.strip()
            if s:
                aList = self.returns_d.get(name, [])
                return_tuple = context, s
                aList.append(return_tuple)
                self.returns_d[name] = aList
        else:
            # A call.
            for i, name in enumerate(m.groups()):
                if name:
                    context2, context1 = self.context_names()
                    j = s.find('#')
                    if j > -1:
                        s = s[: j]
                    s = s.strip().strip(',').strip()
                    if s:
                        aList = self.calls_d.get(name, [])
                        call_tuple = context2, context1, s
                        aList.append(call_tuple)
                        self.calls_d[name] = aList
                    break
        if trace:
            print('%4s %4s %3s %3s %s' % (
                self.n_matches, i, len(self.context_stack), indent, s.rstrip()))
    #@+node:ekr.20150605074749.1: *5* update_context
    def update_context(self, fn, indent, kind, s):
        '''Update context info when a class or def is seen.'''
        trace = False and self.n_matches < 100
        while self.context_stack:
            fn2, kind2, indent2, s2 = self.context_stack[-1]
            if indent <= indent2:
                self.context_stack.pop()
                if trace:
                    g.trace('pop ', len(self.context_stack), indent, indent2, kind2)
            else:
                break
        context_tuple = fn, kind, indent, s
        self.context_stack.append(context_tuple)
        if trace:
            g.trace('push', len(self.context_stack), s.rstrip())
        self.context_indent = indent
    #@+node:ekr.20150604164546.1: *3* show_results & helpers
    def show_results(self):
        '''Print a summary of the test results.'''
        make = True
        multiple_only = True # True only show defs defined in more than one place.
        c = self.c
        result = ['@killcolor']
        for name in sorted(self.defs_d):
            aList = self.defs_d.get(name, [])
            if len(aList) > 1 or not multiple_only: # not name.startswith('__') and (
                self.show_defs(name, result)
                self.show_calls(name, result)
                self.show_returns(name, result)
        # Put the result in a new node.
        summary = 'files: %s lines: %s chars: %s classes: %s defs: %s calls: %s returns: %s' % (
            # self.plural(self.files),
            len(self.files),
            "{:,}".format(self.tot_lines),
            "{:,}".format(self.tot_s),
            "{:,}".format(len(self.classes_d.keys())),
            "{:,}".format(len(self.defs_d.keys())),
            "{:,}".format(len(self.calls_d.keys())),
            "{:,}".format(len(self.returns_d.keys())),
        )
        result.insert(1, summary)
        result.extend(['', summary])
        if make:
            last = c.lastTopLevel()
            p2 = last.insertAfter()
            p2.h = 'global signatures'
            p2.b = '\n'.join(result)
            c.redraw(p=p2)
        g.trace(summary)
    #@+node:ekr.20150605155601.1: *4* show_defs
    def show_defs(self, name, result):
        aList = self.defs_d.get(name, [])
        name_added = False
        w = 0
        # Calculate the width
        for def_tuple in aList:
            context_stack, s = def_tuple
            if context_stack:
                fn, kind, indent, context_s = context_stack[-1]
                context_s = context_s.lstrip('class').strip().strip(':').strip()
                w = max(w, len(context_s))
        for def_tuple in aList:
            context_stack, s = def_tuple
            if not name_added:
                name_added = True
                result.append('\n%s' % name)
                result.append('    %s definition%s...' % (len(aList), self.plural(aList)))
            if context_stack:
                fn, kind, indent, context_s = context_stack[-1]
                context_s = context_s.lstrip('class').strip().strip(':').strip()
                def_s = s.strip().strip('def').strip()
                pad = w - len(context_s)
                result.append('%s%s: %s' % (' ' * (8 + pad), context_s, def_s))
            else:
                result.append('%s%s' % (' ' * 4, s.strip()))
    #@+node:ekr.20150605160218.1: *4* show_calls
    def show_calls(self, name, result):
        aList = self.calls_d.get(name, [])
        if not aList:
            return
        result.extend(['', '    %s call%s...' % (len(aList), self.plural(aList))])
        w = 0
        calls = sorted(set(aList))
        for call_tuple in calls:
            context2, context1, s = call_tuple
            w = max(w, len(context2 or '') + len(context1 or ''))
        for call_tuple in calls:
            context2, context1, s = call_tuple
            pad = w - (len(context2 or '') + len(context1 or ''))
            if context2:
                result.append('%s%s::%s: %s' % (
                    ' ' * (8 + pad), context2, context1, s))
            else:
                result.append('%s%s: %s' % (
                    ' ' * (10 + pad), context1, s))
    #@+node:ekr.20150605160341.1: *4* show_returns
    def show_returns(self, name, result):
        aList = self.returns_d.get(name, [])
        if not aList:
            return
        result.extend(['', '    %s return%s...' % (len(aList), self.plural(aList))])
        w, returns = 0, sorted(set(aList))
        for returns_tuple in returns:
            context, s = returns_tuple
            w = max(w, len(context or ''))
            ### returns_tuple = context, s
            ### returns.append(returns_tuple)
        for returns_tuple in returns:
            context, s = returns_tuple
            pad = w - len(context)
            result.append('%s%s: %s' % (' ' * (8 + pad), context, s))
    #@+node:ekr.20150605213753.1: *3* Utils
    #@+node:ekr.20150605203204.20: *4* add_token
    def add_token(self, kind, value=''):
        '''Add a token to the code list.'''
        # if kind in ('line-indent','line-start','line-end'):
            # g.trace(kind,repr(value),g.callers())
        tok = self.OutputToken(kind, value)
        self.code_list.append(tok)
    #@+node:ekr.20150605140911.1: *4* context_names
    def context_names(self):
        '''Return the present context name.'''
        if self.context_stack:
            result = []
            for stack_i in - 1, -2:
                try:
                    fn, kind, indent, s = self.context_stack[stack_i]
                except IndexError:
                    result.append('')
                    break
                s = s.strip()
                assert kind in ('class', 'def'), kind
                i = g.skip_ws(s, 0)
                i += len(kind)
                i = g.skip_ws(s, i)
                j = g.skip_c_id(s, i)
                result.append(s[i: j])
            return reversed(result)
        else:
            return ['', '']
    #@+node:ekr.20150605163128.1: *4* plural
    def plural(self, aList):
        return 's' if len(aList) > 1 else ''
    #@+node:ekr.20150605203204.40: *4* push_state
    def push_state(self, kind, value=None):
        '''Append a state to the state stack.'''
        state = self.ParseState(kind, value)
        self.state_stack.append(state)
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
