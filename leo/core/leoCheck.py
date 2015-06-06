# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20150605175037.1: * @file leoCheck.py
#@@first
'''Experimental code checking for Leo.'''
import leo.core.leoGlobals as g
import leo.core.leoAst as leoAst
import ast
import glob
import re
import time
import tokenize
#@+others
#@+node:ekr.20150606024455.1: ** class ShowDataTraverser
class ShowDataTraverser(leoAst.AstFullTraverser):
    '''
    Add data about classes, defs, returns and calls to controller's dictionaries.

    Sets .context and .parent ivars before visiting each node.
    '''

    def __init__(self, controller, fn):
        '''Ctor for AstFullTraverser class.'''
        module_tuple = g.shortFileName(fn), 'module', '', g.shortFileName(fn)
            # fn, kind, indent, s.
        self.context_stack = [module_tuple]
        self.controller = controller
        self.fn = g.shortFileName(fn)
        self.formatter = leoAst.AstFormatter()
        self.trace = False
    #@+others
    #@+node:ekr.20150606035006.1: *3* sd.context_names
    def context_names(self):
        '''Return the present context names.'''
        result = []
        for i in -1, -2:
            try:
                fn, kind, indent, s = self.context_stack[i]
                assert kind in ('class', 'def', 'module'), kind
                if kind == 'module':
                    result.append(s.strip())
                else:
                    # Append the name following the class or def.
                    i = g.skip_ws(s, 0)
                    i += len(kind)
                    i = g.skip_ws(s, i)
                    j = g.skip_c_id(s, i)
                    result.append(s[i: j])
            except IndexError:
                result.append('')
                break
        return reversed(result)
    #@+node:ekr.20150606024455.16: *3* sd.Call
    # Call(expr func, expr* args, keyword* keywords, expr? starargs, expr? kwargs)

    def do_Call(self, node):
        # Format
        s = self.formatter.format(node)
        if self.trace: g.trace(s)
        # Update data
        name = self.formatter.format(node.func)
        context2, context1 = self.context_names()
        call_tuple = context2, context1, s
        aList = self.controller.calls_d.get(name, [])
        aList.append(call_tuple)
        self.controller.calls_d[name] = aList
        # Visit.
        self.visit(node.func)
        for z in node.args:
            self.visit(z)
        for z in node.keywords:
            self.visit(z)
        if getattr(node, 'starargs', None):
            self.visit(node.starargs)
        if getattr(node, 'kwargs', None):
            self.visit(node.kwargs)
    #@+node:ekr.20150606024455.3: *3* sd.ClassDef
    # ClassDef(identifier name, expr* bases, stmt* body, expr* decorator_list)

    def do_ClassDef(self, node):
        # Format
        if node.bases:
            bases = [self.formatter.format(z) for z in node.bases]
            s = 'class %s(%s):' % (node.name, ','.join(bases))
        else:
            s = 'class %s:' % node.name
        if self.trace: g.trace(s)
        # Enter the new context.
        context_tuple = self.fn, 'class', '', s
            # fn, kind, indent, s.
            # The indent is for compatibility with the regex-based code.
        self.context_stack.append(context_tuple)
        # Update controller data.
        class_tuple = self.context_stack[: -1], s
        aList = self.controller.classes_d.get(node.name, [])
        aList.append(class_tuple)
        self.controller.classes_d[node.name] = aList
        # Visit.
        for z in node.bases:
            self.visit(z)
        for z in node.body:
            self.visit(z)
        for z in node.decorator_list:
            self.visit(z)
        # Leave the context.
        self.context_stack.pop()
    #@+node:ekr.20150606024455.4: *3* sd.FunctionDef
    # FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)

    def do_FunctionDef(self, node):
        # Format.
        args = self.formatter.format(node.args) if node.args else ''
        s = 'def %s(%s):' % (node.name, args)
        if self.trace: g.trace(s)
        # Enter the new context.
        context_tuple = self.fn, 'def', '', s
            # fn, kind, indent, s
            # The indent is for compatibility with the regex-based code.
        self.context_stack.append(context_tuple)
        # Update controller data.
        def_tuple = self.context_stack[: -1], s
        aList = self.controller.defs_d.get(node.name, [])
        aList.append(def_tuple)
        self.controller.defs_d[node.name] = aList
        # Visit.
        for z in node.decorator_list:
            self.visit(z)
        self.visit(node.args)
        for z in node.body:
            self.visit(z)
        # Leave the context.
        self.context_stack.pop()
    #@+node:ekr.20150606024455.55: *3* sd.Return
    # Return(expr? value)

    def do_Return(self, node):
        # Format...
        s = self.formatter.format(node)
        if self.trace: g.trace(s)
        # Update data
        context, name = self.context_names()
        aList = self.controller.returns_d.get(name, [])
        return_tuple = context, s
        aList.append(return_tuple)
        self.controller.returns_d[name] = aList
        # Visit.
        if node.value:
            self.visit(node.value)
    #@+node:ekr.20150606024455.62: *3* sd.visit
    def visit(self, node):
        '''Visit a *single* ast node.  Visitors are responsible for visiting children!'''
        method = getattr(self, 'do_' + node.__class__.__name__)
        method(node)

    def visit_children(self, node):
        assert False, 'must visit children explicitly'
    #@-others
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
    #@+node:ekr.20150604163903.1: *3* run & helpers
    def run(self, files):
        '''Process all files'''
        self.files = files
        t1 = time.clock()
        for fn in files:
            s, e = g.readFileIntoString(fn)
            if s:
                self.tot_s += len(s)
                g.trace('%8s %s' % ("{:,}".format(len(s)), g.shortFileName(fn)))
                if 1:
                    # Fast, accurate:
                    # 1.9 sec for parsing.
                    # 2.5 sec for Null AstFullTraverer traversal.
                    # 2.7 sec to generate all strings.
                    # 3.8 sec to generate all reports.
                    s1 = g.toEncodedString(s)
                    node = ast.parse(s1, filename='before', mode='exec')
                    ShowDataTraverser(self, fn).visit(node)
                elif 0: # Too slow, too clumsy: 3.3 sec for tokenizing
                    readlines = g.ReadLinesClass(s).next
                    for token5tuple in tokenize.generate_tokens(readlines):
                        pass
                else: # Inaccurate. 2.2 sec to generate all reports.
                    self.scan(fn, s)
            else:
                g.trace('skipped', g.shortFileName(fn))
        t2 = time.clock()
            # Get the time exlusive of print time.
        self.show_results()
        g.trace('done: %4.1f sec.' % (t2 - t1))
    #@+node:ekr.20150605054921.1: *4* scan (fast, inaccurate) & helpers
    # The excellent prototype code.
    # It was a roadmap for the ShowDataTraverser class.

    def scan(self, fn, s):
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
    #@+node:ekr.20150605140911.1: *4* context_names
    def context_names(self):
        '''Return the present context name.'''
        if self.context_stack:
            result = []
            for stack_i in -1, -2:
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
    #@+node:ekr.20150605163128.1: *4* plural
    def plural(self, aList):
        return 's' if len(aList) > 1 else ''
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
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
