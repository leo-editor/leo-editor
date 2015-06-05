# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20150605175037.1: * @file leoCheck.py
#@@first
'''Experimental code checking for Leo.'''
import leo.core.leoGlobals as g
import glob
import re
import time
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
    #@+node:ekr.20150604165500.1: *3* ctor
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
        # Regex patterns. These are really a premature optimization.
        r_class = r'class[ \t]+([a-z_A-Z][a-z_A-Z0-9]*).*:'
        r_def = r'def[ \t]+([a-z_A-Z][a-z_A-Z0-9]*)[ \t]*\((.*)\)'
        r_return = r'(return[ \t].*)$'
        r_call = r'([a-z_A-Z][a-z_A-Z0-9]*)[ \t]*\(([^)]*)\)'
        self.r_all = re.compile('|'.join([r_class, r_def, r_return, r_call,]))
                                # flags=re.MULTILINE
    #@+node:ekr.20150605140911.1: *3* context_names
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
    #@+node:ekr.20150605063318.1: *3* match
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
    #@+node:ekr.20150604163903.1: *3* run
    def run(self, files):
        '''Process all files'''
        self.files = files
        t1 = time.clock()
        for fn in files:
            s, e = g.readFileIntoString(fn)
            if s:
                self.tot_s += len(s)
                self.scan(fn, s)
            else:
                g.trace('skipped', g.shortFileName(fn))
        t2 = time.clock()
            # Get the time exlusive of print time.
        self.show_results()
        g.trace('done: %4.2f sec.' % (t2 - t1))
    #@+node:ekr.20150605163128.1: *3* plural
    def plural(self, aList):
        return 's' if len(aList) > 1 else ''
    #@+node:ekr.20150605054921.1: *3* scan
    def scan(self, fn, s):
        g.trace('%8s %s' % ("{:,}".format(len(s)), g.shortFileName(fn)))
        # print(' hit line lvl lws line')
        lines = g.splitLines(s)
        self.tot_lines += len(lines)
        for i, s in enumerate(lines):
            m = re.search(self.r_all, s)
            if m and not s.startswith('@'):
                self.match(fn, i, m, s)
    #@+node:ekr.20150604164546.1: *3* show_results & helpers
    def show_results(self):
        '''Print a summary of the test results.'''
        make = True
        multiple_only = True # True only show defs defined in more than one place.
        c = self.c
        result = ['@killcolor']
        for name in sorted(self.defs_d):
            aList = self.defs_d.get(name, [])
            multiple = len(aList) > 1
            enabled = not name.startswith('__')
            margin = ' ' * 8 if multiple else ' ' * 4
            if enabled and (multiple or not multiple_only):
                self.show_defs(margin, name, result)
                self.show_calls(margin, name, result)
                self.show_returns(margin, name, result)
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
    def show_defs(self, margin, name, result):
        aList = self.defs_d.get(name, [])
        name_added = False
        max_context = 0
        # Calculate the width
        for def_tuple in aList:
            context_stack, s = def_tuple
            if context_stack:
                fn, kind, indent, context_s = context_stack[-1]
                max_context = max(max_context, 2 + len(context_s))
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
                pad = max_context - len(context_s)
                result.append('%s%s: %s' % (' ' * pad, context_s, def_s))
            else:
                result.append('%s%s' % (' ' * max_context, s.strip()))
    #@+node:ekr.20150605160218.1: *4* show_calls
    def show_calls(self, margin, name, result):
        aList = self.calls_d.get(name, [])
        if not aList:
            return
        result.extend(['', '    %s call%s...' % (len(aList), self.plural(aList))])
        max_context = 0
        calls = sorted(set(aList))
        for call_tuple in calls:
            context2, context1, s = call_tuple
            max_context = max(
                max_context,
                len(context2 or '') + len(context1 or ''))
        for call_tuple in calls:
            context2, context1, s = call_tuple
            pad = max_context - (len(context2 or '') + len(context1 or ''))
            if context2:
                result.append('%s%s%s::%s: %s' % (
                    margin, ' ' * pad, context2, context1, s))
            else:
                result.append('%s%s%s: %s' % (
                    margin, ' ' * (pad + 2), context1, s))
    #@+node:ekr.20150605160341.1: *4* show_returns
    def show_returns(self, margin, name, result):
        aList = self.returns_d.get(name, [])
        if not aList:
            return
        result.extend(['', '    %s return%s...' % (len(aList), self.plural(aList))])
        max_context, returns = 0, []
        for return_tuple in sorted(set(aList)):
            context, s = return_tuple
            max_context = max(max_context, len(context or ''))
            returns_tuple = context, s
            returns.append(returns_tuple)
        for returns_tuple in returns:
            context, s = returns_tuple
            pad = max_context - len(context)
            result.append('%s%s%s: %s' % (margin, ' ' * pad, context, s))
    #@+node:ekr.20150605074749.1: *3* update_context
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
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
