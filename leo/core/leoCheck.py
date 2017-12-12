# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20150605175037.1: * @file leoCheck.py
#@@first
'''Experimental code checking for Leo.'''
# To do:
# - Option to ignore defs without args if all calls have no args.
# * explain typical entries
import imp
import leo.core.leoGlobals as g
import leo.core.leoAst as leoAst
imp.reload(leoAst)
import ast
import glob
import importlib
import os
import re
import time
#@+others
#@+node:ekr.20171207095816.1: ** class ConventionChecker
class ConventionChecker (object):
    '''
    A prototype of an extensible convention-checking tool.
    See: https://github.com/leo-editor/leo-editor/issues/632
    
    Here is the body of @button check-conventions:
    
        g.cls()
        if c.changed: c.save()
        
        import imp
        import leo.core.leoCheck as leoCheck
        imp.reload(leoCheck)
        
        fn = g.os_path_finalize_join(g.app.loadDir, '..', 'plugins', 'nodetags.py')
        leoCheck.ConventionChecker(c).check(fn=fn)
    '''
    
    # pylint: disable=no-member
        # Stats class defines __setattr__
        # This is a known limitation of pylint.

    ignore = ('bool', 'dict', 'enumerate', 'list', 'tuple')
        # Things that look like function calls.
    
    patterns = []
        # Set below.

    #@+others
    #@+node:ekr.20171210134449.1: *3* checker.Birth
    def __init__(self, c):
        self.c = c
        self.class_name = None
        # Rudimentary symbol tables...
        self.classes = self.init_classes()
        self.special_class_names = [
            'Commands', 'LeoGlobals', 'Position', 'String', 'VNode'
        ]
        self.special_names = self.init_special_names()
        # Other ivars...
        self.enable_trace = True
        self.file_name = None
        self.line_number = 0
        self.pass_n = 0
        self.recursion_count = 0
        self.s = '' # The line being examined.
        self.stats = Stats()
        self.unknowns = {} # Keys are expression, values are (line, fn) pairs.
    #@+node:ekr.20171209044610.1: *4* checker.init_classes
    def init_classes(self):
        '''
        Init the symbol tables with known classes.
        '''
        return {
            # Pre-enter known classes.
            'Commands': {
                'ivars': {
                    'p': self.Type('instance', 'Position'),
                },
                'methods': {},
            },
            'LeoGlobals': {
                'ivars': {}, # g.app, g.app.gui.
                'methods': {
                    'trace': self.Type('instance', 'None')
                },
            },
            'Position': {
                'ivars': {
                    'v': self.Type('instance', 'VNode'),
                    'h': self.Type('instance', 'String'),
                },
                'methods': {},
            },
            'VNode': {
                'ivars': {
                    'h': self.Type('instance', 'String'),
                    # Vnode has no v instance!
                },
                'methods': {},
            },
            'String': {
                'ivars': {},
                'methods': {}, ### Possible?
            },
        }
        
    #@+node:ekr.20171210133853.1: *4* checker.init_special_names
    def init_special_names(self):
        '''Init known special names.'''
        t = self.Type
        return {
            'c': t('instance', 'Commands'),
            'c.p': t('instance', 'Position'),
            'g': t('instance', 'LeoGlobals'), ### module?
            'p': t('instance', 'Position'),
            'v': t('instance', 'VNode'),
        }
    #@+node:ekr.20171212015700.1: *3* checker.check & helpers (main entry)
    def check(self):
        '''
        The main entry point for the convention checker.

        A stand-alone version of the @button node that tested the
        ConventionChecker class.
        
        The check-conventions command in checkerCommands.py saves c and
        reloads the leoCheck module before instantiating this class and
        calling this method.
        '''
        g.cls()
        c = self.c
        kind = 'all'
        assert kind in ('all', 'files', 'production', 'test'), repr(kind)
        report_stats = True
        trace_fn = True
        trace_skipped = False
        fails_dict = {
            'coverage': ['cmdline.py',],
            'lib2to3': ['fixer_util.py', 'fix_dict.py', 'patcomp.py', 'refactor.py'],
            'leo': [], # All of Leo's core files pass.
            'pylint': [
                'base.py', 'classes.py', 'format.py',
                'logging.py', 'python3.py', 'stdlib.py', 
                'docparams.py', 'lint.py',
            ],
            'rope': ['objectinfo.py', 'objectdb.py', 'runmod.py',],
        }
        if kind == 'production':
            for p in g.findRootsWithPredicate(c, c.p, predicate=None):
                self.check_file(fn=g.fullPath(c, p), trace_fn=trace_fn)
        elif kind == 'all':
            project_name = 'leo'
                # in ('coverage', 'leo', 'lib2to3', 'pylint', 'rope')
            fails = fails_dict.get(project_name, [])
            utils = ProjectUtils()
            aList = utils.project_files(project_name, force_all=False)
            if aList:
                t1 = time.clock()
                for fn in aList:
                    sfn = g.shortFileName(fn)
                    if sfn in fails or fn in fails:
                        if trace_skipped: print('===== skipping', sfn)
                    else:
                        self.check_file(fn=fn, trace_fn=trace_fn)
                t2 = time.clock()
                print('%s files in %4.2f sec.' % (len(aList), (t2-t1)))
            else:
                print('no files for project: %s' % (project_name))
        elif kind == 'test':
            self.test()
        else:
            assert kind == 'files', repr(kind)
            join = g.os_path_finalize_join
            loadDir = g.app.loadDir
            files_table = (
                # join(loadDir, 'leoNodes.py'),
                join(loadDir, '..', 'plugins', 'qt_tree.py'),
            )
            for fn in files_table:
                self.check_file(fn=fn, trace_fn=True)
        if report_stats:
            self.stats.report()
    #@+node:ekr.20171207100432.1: *4* checker.check_file
    def check_file(self, fn=None, s=None, trace_fn=False):
        '''Check the contents of fn or the string s.'''
        # Get the source.
        trace = True
        trace_time = True
        if fn:
            sfn = g.shortFileName(fn)
            if g.os_path_exists(fn):
                s, e = g.readFileIntoString(fn)
                if s:
                    s = g.toEncodedString(s, encoding=e)
                else:
                    return g.trace('empty file:', sfn)
            else:
                return g.trace('file not found:', sfn)
        elif s:
            sfn = '<string>'
        else:
            return g.trace('no fn or s argument')
        # Check the source
        if trace_fn:
            print(('===== %s' % (sfn)) if fn else s)
        t1 = time.clock()
        node = ast.parse(s, filename='before', mode='exec')
        self.check_helper(fn=sfn, node=node, s=s)
        t2 = time.clock()
        if trace and trace_time and fn:
            print('%4.2f sec. %s' % ((t2-t1), sfn))
    #@+node:ekr.20171207101337.1: *4* checker.check_helper
    def check_helper(self, fn, node, s):
        trace = False and self.enable_trace
        trace_source = False
        self.file_name = fn
        dispatch = {
            'call':     self.do_call,
            'class':    self.do_class,
            'def':      self.do_def,
            'assign':   self.do_assn,
            # 'self.x=':  self.do_assn_to_self,
            # 'c.x=':     self.do_assn_to_c,
        }
        s1 = leoAst.AstFormatter().format(node)
        for n in (1, 2):
            self.enable_trace = n == 2
            self.class_name = None
            self.pass_n = n
            if trace:
                print('===== pass: %s' % n)
                if trace_source and n == 2:
                    print('===== source')
                    print(s1)
                    print('----- end source')
            for n, s in enumerate(g.splitLines(s1)):
                self.line_number = n
                self.s = s.rstrip()
                for kind, pattern in self.patterns:
                    m = pattern.match(s)
                    if m:
                        f = dispatch.get(kind)
                        f(kind, m, s)
            self.end_class()
        self.end_file()
    #@+node:ekr.20171209065852.1: *3* checker_check_signature & helpers
    def check_signature(self, func, args, signature):
        
        trace = False
        if trace: g.trace('%s(%s) ==> %s' % (func, args, signature))
        self.stats.check_signature += 1
        if signature[0] == 'self':
            signature = signature[1:]
        result = 'ok'
        for i, arg in enumerate(args):
            if i < len(signature):
                result = self.check_arg(func, arg, signature[i])
                if result == 'fail':
                    print('\nline %s %s\n%s(%s) incompatible with %s(%s)\n' % (
                        self.line_number, self.file_name,
                        func, ','.join(args),
                        func, ','.join(signature)))
                    break
            elif trace:
                g.trace('possible extra arg', arg)
        if len(args) > len(signature):
            if trace:
                g.trace('possible missing args', signature[len(args)-1:])
        if result == 'ok':
            self.stats.sig_ok += 1
        elif result == 'fail':
            self.stats.sig_fail += 1
        else:
            assert result == 'unknown'
            self.stats.sig_unknown += 1
                
    #@+node:ekr.20171212034531.1: *4* checker.check_arg
    def check_arg(self, func, call_arg, sig_arg):
        
        # First, check the ags.
        call_argv = call_arg.split('=')
        sig_argv = sig_arg.split('=')
        result = self.check_arg_helper(func, call_argv[0], sig_argv[0])
        if result == 'fail':
            return result
        # Next, check a keyword call arg against it's assigned value.
        if len(call_argv) > 1:
            arg1, arg2 = call_argv[0], ''.join(call_argv[1:])
            return self.check_arg_helper('KEYWORD', arg1, arg2)
        else:
            return result
    #@+node:ekr.20171212035137.1: *4* checker.check_arg_helper
    def check_arg_helper(self, func, call_arg, sig_arg):
        trace = False
        trace_ok = True
        trace_unknown = True
        special_names = self.special_names
        if call_arg == sig_arg or sig_arg in (None, 'None'):
            # Match anything against a default value of None.
            if trace and trace_ok:
                g.trace('line %4s %s %20s: %20r == %r' % (
                    self.line_number, self.file_name, func, call_arg, sig_arg))
            return 'ok'
        # Resolve the call_arg if possible.
        chain = call_arg.split('.')
        if len(chain) > 1:
            head, tail = chain[0], chain[1:]
            if head in special_names:
                context = special_names.get(head)
                context = self.resolve_chain(tail, context)
                if context.kind == 'error':
                    # Caller will report the error.
                    g.trace('FAIL', call_arg, context)
                    return 'fail'
                if sig_arg in special_names:
                    sig_class = special_names.get(sig_arg)
                    return self.compare_classes(call_arg, sig_arg, context, sig_class)
        if sig_arg in special_names and call_arg in special_names:
            sig_class = special_names.get(sig_arg)
            call_class = special_names.get(call_arg)
            return self.compare_classes(call_arg, sig_arg, call_class, sig_class)
        if trace and trace_unknown:
            g.trace('line %4s %s %20s: %20r ?? %r' % (
                self.line_number, self.file_name, func, call_arg, sig_arg))
        return 'unknown'
    #@+node:ekr.20171212044621.1: *4* checker.compare_classes
    def compare_classes(self, arg1, arg2, class1, class2):

        trace = True
        trace_ok = False
        if class1 == class2:
            if trace and trace_ok:
                g.trace('infer ok', arg1, arg2, class1)
            self.stats.sig_infer_ok += 1
            return 'ok'
        else:
            # The caller reports the failure.
            if trace:
                g.trace('FAIL', arg1, arg2, class1, class2)
            self.stats.sig_infer_fail += 1
            return 'fail'
    #@+node:ekr.20171208090003.1: *3* checker.do_*
    # These are like string-oriented visitors.
    #@+node:ekr.20171212035529.1: *4* checker.do_assn
    assign_pattern = ('assign', re.compile(r'^\s*(\w+(\.\w+)*)\s*=(.*)'))
    patterns.append(assign_pattern)

    def do_assn(self, kind, m, s):
        
        table = (
            (self.assign_to_c_pattern, self.do_assn_to_c),
            (self.assn_to_self_pattern, self.do_assn_to_self),
        )
        for pattern, func in table:
            m = pattern.match(s)
            if m:
                func(kind, m, s)
                return
    #@+node:ekr.20171209063559.1: *4* checker.do_assn_to_c
    assign_to_c_pattern = re.compile(r'^\s*c\.([\w.]+)\s*=(.*)')

    def do_assn_to_c(self, kind, m, s):
        
        trace = False and self.enable_trace
        trace_dict = False
        if trace:
            print('%14s: %s' % (kind, s.strip()))
        if self.pass_n == 1:
            self.stats.assignments += 1
            ivar = m.group(1)
            val = m.group(2).strip()
            # Resolve val, if possible.
            if self.class_name:
                context = self.Type('class', self.class_name)
            else:
                context = self.Type('module', self.file_name)
            self.recursion_count = 0
            val = self.resolve(val, context, trace=False)
            d = self.classes.get('Commands')
            assert d
            ivars = d.get('ivars')
            ivars[ivar] = val
            d['ivars'] = ivars
            if trace and trace_dict:
                g.trace('dict for class Commands...')
                g.printDict(d)
    #@+node:ekr.20171209063559.2: *4* checker.do_assn_to_self
    assn_to_self_pattern = re.compile(r'^\s*self\.(\w+)\s*=(.*)')

    def do_assn_to_self(self, kind, m, s):

        trace = False and self.enable_trace
        trace_dict = False
        assert self.class_name
        if trace:
            print('%14s: %s' % (kind, s.strip()))
        ###
        # if self.class_name in ('Commands', 'Position'):
            # g.trace('IGNORE', s.strip())
            # return
        if self.pass_n == 1:
            self.stats.assignments += 1
            ivar = m.group(1)
            val = m.group(2).strip()
            d = self.classes.get(self.class_name)
            assert d is not None, self.class_name
            ivars = d.get('ivars')
            ivars[ivar] = val
            d['ivars'] = ivars
            if trace and trace_dict:
                g.trace('dict for class', self.class_name)
                g.printDict(d)
    #@+node:ekr.20171209063559.3: *4* checker.do_call & helper
    call_pattern = ('call',  re.compile(r'^\s*(\w+(\.\w+)*)\s*\((.*)\)'))
    patterns.append(call_pattern)

    def do_call(self, kind, m, s):

        trace = False and self.pass_n == 2
        if trace: print('%14s: %s' % (kind, s.strip()))
        if self.pass_n == 1:
            return
        try:
            call = m.group(1)
            trace = not any([call.startswith(z) for z in self.ignore])
        except IndexError:
            pass # No m.group(1)
        self.stats.calls += 1
        obj = self.resolve_call(kind, m, s)
        if obj and obj.kind == 'instance':
            m = self.call_pattern.match(s.strip())
            chain = m.group(1).split('.')
            func = chain[-1]
            args = self.split_args(m.group(3))
            instance = self.classes.get(obj.name)
            if instance:
                d = instance.get('methods')
                signature = d.get(func)
                if signature:
                    if isinstance(signature, self.Type):
                        pass
                    else:
                        signature = signature.split(',')
                        self.check_signature(func, args, signature)
    #@+node:ekr.20171212032532.1: *5* checker.split_args
    def split_args(self, args):
        '''
        Args is a string representing actual arguments.
        This could contain '=' and ',' within calls.
        return an array of actual args.
        '''
        trace = False
        arg, i, result = '', 0, []
        while i < len(args):
            ch = args[i]
            if ch == ',':
                result.append(arg)
                arg = ''
                i += 1
            elif ch == '(':
                j, s = g.skip_to_char(args, i, ')')
                if i < j < len(args) and args[j] == ')':
                    arg += args[i:j+1]
                    i = j+1
                else:
                    g.trace('unmatched paren')
                    return []
            else:
                arg += ch
                i += 1
        if arg:
            result.append(arg)
        if trace:
            g.trace(args)
            g.printList(result)
        return result
                
    #@+node:ekr.20171209063559.4: *4* checker.do_class & end_class
    class_pattern = ('class', re.compile(r'class\s+([a-z_A-Z][a-z_A-Z0-9]*).*:'))
    patterns.append(class_pattern)

    def do_class(self, kind, m, s):

        trace = False
        self.end_class()
        self.class_name = name = m.group(1) if m else None
        if self.pass_n > 1 or not m:
            return
        if trace: print(s.rstrip())
        self.stats.classes += 1
        if name not in self.special_class_names:
            self.classes [name] = {
                'ivars': {},
                'methods': {},
            }
    #@+node:ekr.20171212085210.1: *5* checker.end_class
    def end_class(self):
        '''End (trace) the old class, if it exists'''
        trace = False and self.enable_trace
        trace_dict = False
        # Trace the old class.
        if trace and self.class_name:
            if trace_dict:
                print('----- END class %s. class dict...' % self.class_name)
                g.printDict(self.classes.get(self.class_name))
            else:
                print('----- END class %s', self.class_name)
    #@+node:ekr.20171209063559.5: *4* checker.do_def
    def_pattern = ('def', re.compile(r'^\s*def\s+([\w0-9]+)\s*\((.*)\)\s*:'))
    patterns.append(def_pattern)

    def do_def(self, kind, m, s):

        trace = False and self.pass_n == 1
        if trace: print('%4s%s' % ('', s.strip()))
        # Not quite accurate..
        if self.class_name and self.pass_n == 1:
            self.stats.defs += 1
            if self.class_name not in self.special_class_names:
                def_name = m.group(1)
                def_args = m.group(2)
                the_class = self.classes.get(self.class_name)
                methods = the_class.get('methods')
                assert methods is not None
                methods [def_name] = def_args
    #@+node:ekr.20171208135642.1: *3* checker.end_file & helper
    def end_file(self):
        
        trace = False
        trace_classes = False
        trace_unknowns = True
        if trace:
            print('----- END OF FILE: %s' % self.file_name)
            if trace_classes:
                for key, val in sorted(self.classes.items()):
                    print('class %s' % key)
                    g.printDict(val)
            if trace_unknowns:
                self.trace_unknowns()
        # Do *not* clear self.classes.
        self.unknowns = {}
    #@+node:ekr.20171212100005.1: *4* checker.trace_unknowns
    def trace_unknowns(self):
        print('----- Unknown ivars...')
        d = self.unknowns
        max_key = max([len(key) for key in d ]) if d else 2
        for key, aList in sorted(d.items()):
            # Remove duplicates that vary only in line number.
            aList2, seen = [], []
            for data in aList:
                line, fn, s = data
                data2 = (key, fn, s)
                if data2 not in seen:
                    seen.append(data2)
                    aList2.append(data)
            for data in aList2:
                line, fn, s = data
                print('%*s %4s %s: %s' % (
                    max_key, key, line, fn, g.truncate(s, 60)))
    #@+node:ekr.20171208142646.1: *3* checker.resolve & helpers
    def resolve(self, name, obj, trace=False):
        '''Resolve name in the context of obj.'''
        trace_resolve = True
        # if trace and self.file_name == 'qt_tree.py':
            # g.printDict(self.classes.get('Position'))
        if trace and trace_resolve:
            g.trace('      ===== name: %s obj: %r' % (name, obj))
        self.stats.resolve += 1
        if obj:
            if obj.kind in ('error', 'unknown'):
                result = obj
            elif name == 'self':
                assert obj.name, repr(obj)
                result = self.Type('instance', obj.name)
            elif obj.kind in ('class', 'instance'):
                result = self.resolve_ivar(name, obj)
            else:
                result = self.Type('error', 'unknown kind: %s' % obj.kind)
        else:
            result = self.Type('error', 'unbound name: %s' % name)
        if trace and trace_resolve: g.trace('      ----->', result)
        return result
    #@+node:ekr.20171208134737.1: *4* checker.resolve_call
    call_pattern = re.compile(r'(\w+(\.\w+)*)\s*\((.*)\)')

    def resolve_call(self, kind, m, s):

        trace = False and self.enable_trace
        trace_entry = True
        trace_result = False
        self.stats.resolve_call += 1
        s = s.strip()
        m = self.call_pattern.match(s)
        aList = m.group(1).split('.')
        chain, func = aList[:-1], aList[-1]
        args = m.group(3).split(',')
        if chain:
            self.recursion_count = 0
            if trace and trace_entry:
                g.trace(' ===== %s.%s(%s)' % (
                    '.'.join(chain), func, ','.join(args)))
            if self.class_name:
                context = self.Type('class', self.class_name)
            else:
                context = self.Type('module', self.file_name)
            result = self.resolve_chain(chain, context)
            if trace and trace_result:
                g.trace(' ----> %s.%s' % (result, func))
        else:
            result = None
        return result
    #@+node:ekr.20171209034244.1: *4* checker.resolve_chain
    def resolve_chain(self, chain, context, trace=False):

        if trace:
            g.trace('=====', chain, context)
        self.stats.resolve_chain += 1
        name = '<no name>'
        for name in chain:
            context = self.resolve(name, context, trace=trace)
            if trace: g.trace('%4s ==> %r' % (name, context))
        if trace:
            g.trace('%4s ----> %r' % (name, context))
        return context
    #@+node:ekr.20171208173323.1: *4* checker.resolve_ivar
    # id_pattern = re.compile('\w+')

    def resolve_ivar(self, ivar, obj):
        '''Resolve obj.ivar'''
        trace = False
        trace_c_dict_on_error = False
        trace_dict = False
        trace_dict_on_error = False
        trace_error = True
        trace_ivar = False
        trace_recursive = False
        trace_special = False
        trace_unknown = True
        raise_on_error = True
        self.stats.resolve_ivar += 1
        class_name = 'Commands' if obj.name == 'c' else obj.name
        the_class = self.classes.get(class_name)
        self.recursion_count += 1
        if self.recursion_count > 20:
            print('')
            g.trace('UNBOUNDED RECURSION: %r %r %s' % (ivar, obj, g.callers()))
            if trace_c_dict_on_error:
                g.trace('CLASS DICT: Commands')
                g.printDict(self.classes.get('Commands'))
            if trace_dict_on_error:
                g.trace('CLASS DICT', class_name)
                g.printDict(the_class)
            if raise_on_error:
                assert False, self.recursion_count
            return self.Type('error', 'recursion')
        if not the_class:
            return self.Type('error', 'no class %s' % ivar)
        if trace and trace_dict:
            g.trace('CLASS DICT', class_name)
            g.printDict(the_class)
        ivars = the_class.get('ivars')
        methods = the_class.get('methods')
        if ivar == 'self':
            return self.Type('class', class_name)
        elif methods.get(ivar):
            return self.Type('func', ivar)
        elif ivars.get(ivar):
            val = ivars.get(ivar)
            if trace and trace_ivar:
                g.trace('IVAR:', ivar, 'CONTEXT', obj, 'VAL', val)
            if isinstance(val, self.Type):
                if trace: g.trace('KNOWN: %s %r ==> %r' % (ivar, obj, val))
                return val
            # Check for pre-defined special names.
            for special_name, special_obj in self.special_names.items():
                tail = val[len(special_name):]
                if val == special_name:
                    if trace and trace_special:
                        g.trace('SPECIAL: %s ==> %s' % (val, special_obj))
                    return special_obj
                elif val.startswith(special_name) and tail.startswith('.'):
                    # Resovle the rest of the tail in the found context.
                    if trace: g.trace('TAIL: %s => %s.%s' % (val, special_obj, tail))
                    return self.resolve_chain(tail[1:], special_obj)
            # Avoid recursion 1.
            if ivar == val:
                if trace and trace_unknown:
                    g.trace('AVOID RECURSION: self.%s=%s' % (ivar, val))
                return self.Type('unknown', ivar)
            head2 = val.split('.')
            # Avoid recursion 2.
            if ivar == head2[0]:
                if trace and trace_unknown:
                    g.trace('AVOID RECURSION2: %s=%s' % (ivar, val))
                return self.Type('unknown', ivar)
            if trace and trace_recursive:
                g.trace('RECURSIVE', head2)
            obj2 = obj
            for name2 in head2:
                old_obj2 = obj2
                obj2 = self.resolve(name2, obj2)
                if trace and trace_recursive:
                    g.trace('recursive %s: %r --> %r' % (
                        name2, old_obj2, obj2))
            if trace and trace_recursive:
                g.trace('END RECURSIVE: %r', obj2)
            return obj2
        elif ivar in self.special_names:
            val = self.special_names.get(ivar)
            if trace and trace_special:
                g.trace('FOUND SPECIAL', ivar, val)
            return val
        else:
            # Remember the unknown.
            d = self.unknowns
            aList = d.get(ivar, [])
            data = (self.line_number, self.file_name, self.s.strip())
            aList.append(data)
            d[ivar] = aList
            if trace and trace_error:
                g.trace('NO MEMBER: %-s %s: %s' % (
                    self.line_number,
                    self.file_name,
                    g.truncate(self.s.strip(), 60),
                ))
            return self.Type('error', 'no member %s' % ivar)
    #@+node:ekr.20171212020013.1: *3* checker.test
    def test(self):
        
        s = '''\
    class TC:
        def __init__(self, c):
            c.tc = self
        def add_tag(self, p):
            print(p.v) # AttributeError if p is a vnode.

    class Test:
        def __init__(self,c):
            self.c = c
            self.tc = self.c.tc
        def add_tag(self):
            p = self.c.p
            self.tc.add_tag(p.v) # WRONG: arg should be p.
    '''
        c = self.c
        s = g.adjustTripleString(s, c.tab_width)
        self.check_file(s=s,trace_fn=True)
    #@+node:ekr.20171209030742.1: *3* class Type
    class Type (object):
        '''A class to hold all type-related data.'''

        kinds = ('error', 'class', 'func', 'instance', 'module', 'unknown')
        
        def __init__(self, kind, name, source=None, tag=None):

            assert kind in self.kinds, repr(kind)
            self.kind = kind
            self.name=name
            self.source = source
            self.tag = tag
            
        def __repr__(self):

            return '<%s: %s>' % (self.kind, self.name)
            
        def __eq__(self, other):
            
            return self.kind == other.kind and self.name == other.name
    #@-others
#@+node:ekr.20160109102859.1: ** class Context
class Context(object):
    '''
    Context class (NEW)

    Represents a binding context: module, class or def.

    For any Ast context node N, N.cx is a reference to a Context object.
    '''
    #@+others
    #@+node:ekr.20160109103533.1: *3* Context.ctor
    def __init__ (self, fn, kind, name, node, parent_context):
        '''Ctor for Context class.'''
        self.fn = fn
        self.kind = kind
        self.name = name
        self.node = node
        self.parent_context = parent_context
        # Name Data...
        self.defined_names = set()
        self.global_names = set()
        self.imported_names = set()
        self.nonlocal_names = set() # To do.
        self.st = {}
            # Keys are names seen in this context, values are defining contexts.
        self.referenced_names = set()
        # Node lists. Entries are Ast nodes...
        self.inner_contexts_list = []
        self.minor_contexts_list = []
        self.assignments_list = []
        self.calls_list = []
        self.classes_list = []
        self.defs_list = []
        self.expressions_list = []
        self.returns_list = []
        self.statements_list = []
        self.yields_list = []
        # Add this context to the inner context of the parent context.
        if parent_context:
            parent_context.inner_contexts_list.append(self)
    #@+node:ekr.20160109134527.1: *3* Context.define_name
    def define_name(self, name):
        '''Define a name in this context.'''
        self.defined_names.add(name)
        if name in self.referenced_names:
            self.referenced_names.remove(name)
    #@+node:ekr.20160109143040.1: *3* Context.global_name
    def global_name(self, name):
        '''Handle a global name in this context.'''
        self.global_names.add(name)
        # Not yet.
            # Both Python 2 and 3 generate SyntaxWarnings when a name
            # is used before the corresponding global declarations.
            # We can make the same assumpution here:
            # give an *error* if an STE appears in this context for the name.
            # The error indicates that scope resolution will give the wrong result.
            # e = cx.st.d.get(name)
            # if e:
                # self.u.error('name \'%s\' used prior to global declaration' % (name))
                # # Add the name to the global_names set in *this* context.
                # # cx.global_names.add(name)
            # # Regardless of error, bind the name in *this* context,
            # # using the STE from the module context.
            # cx.st.d[name] = module_e
    #@+node:ekr.20160109144139.1: *3* Context.import_name
    def import_name(self, module, name):

        if True and name == '*':
            g.trace('From x import * not ready yet')
        else:
            self.imported_names.add(name)
    #@+node:ekr.20160109145526.1: *3* Context.reference_name
    def reference_name(self, name):

        self.referenced_names.add(name)
    #@-others
#@+node:ekr.20160108105958.1: ** class Pass1 (AstFullTraverser)
class Pass1 (leoAst.AstFullTraverser): # V2

    ''' Pass1 does the following:

    1. Creates Context objects and injects them into the new_cx field of
       ast.Class, ast.FunctionDef and ast.Lambda nodes.

    2. Calls the following Context methods: cx.define/global/import/reference_name.
       These methods update lists used later to bind names to objects.
    '''
    # pylint: disable=no-member
        # Stats class defines __setattr__
        # This is a known limitation of pylint.

    #@+others
    #@+node:ekr.20160108105958.2: *3*  p1.ctor
    def __init__(self, fn):

        # Init the base class.
        leoAst.AstFullTraverser.__init__(self)
        self.fn = fn
        # Abbreviations...
        self.stats = Stats()
        self.u = ProjectUtils()
        self.format = leoAst.AstFormatter.format
        # Present context...
        self.context = None
        self.in_attr = False
            # True: traversing inner parts of an AST.Attribute tree.
        self.module_context = None
        self.parent = None
    #@+node:ekr.20160108105958.3: *3*  p1.run (entry point)
    def run (self,root):

        self.visit(root)
    #@+node:ekr.20160109125654.1: *3*  p1.visit
    def visit(self, node):
        '''Visit a *single* ast node.  Visitors are responsible for visiting children!'''
        assert isinstance(node, ast.AST), node.__class__.__name__
        # Visit the children with the new parent.
        old_parent = self.parent
        self.parent = node
        method_name = 'do_' + node.__class__.__name__
        method = getattr(self, method_name)
        # g.trace(method_name)
        method(node)
        self.parent = old_parent
    #@+node:ekr.20160108105958.11: *3* p1.visitors
    #@+node:ekr.20160109134854.1: *4* Contexts
    #@+node:ekr.20160108105958.8: *5* p1.def_args_helper
    # arguments = (expr* args, identifier? vararg, identifier? kwarg, expr* defaults)

    def def_args_helper (self,cx,node):

        assert self.kind(node) == 'arguments'
        self.visit_list(node.args)
        self.visit_list(node.defaults)
        for field in ('vararg','kwarg'): # node.field is a string.
            name = getattr(node,field,None)
            if name:
                # e = cx.st.define_name(name)
                self.stats.n_param_names += 1
    #@+node:ekr.20160108105958.16: *5* p1.ClassDef
    # ClassDef(identifier name, expr* bases, stmt* body, expr* decorator_list)

    def do_ClassDef (self,node):

        old_cx = self.context
        name = node.name
        # Define the class name in the old context.
        old_cx.define_name(name)
        # Visit bases in the old context.
        # bases = self.visit_list(node.bases)
        new_cx = Context(
            fn=None,
            kind='class',
            name=name,
            node=node,
            parent_context=old_cx)
        setattr(node,'new_cx',new_cx)
        # Visit the body in the new context.
        self.context = new_cx
        self.visit_list(node.body)
        self.context = old_cx
        # Stats.
        old_cx.classes_list.append(new_cx)
    #@+node:ekr.20160108105958.19: *5* p1.FunctionDef
    # 2: FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)
    # 3: FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list,
    #    expr? returns)

    def do_FunctionDef (self,node):

        # Define the function/method name in the old context.
        old_cx = self.context
        name = node.name
        old_cx.define_name(name)
        # Create the new context.
        new_cx = Context(
            fn=None,
            kind='def',
            name=name,
            node=node,
            parent_context=old_cx)
        setattr(node,'new_cx',new_cx) # Bug fix.
        # Visit in the new context...
        self.context = new_cx
        self.def_args_helper(new_cx,node.args)
        self.visit_list(node.body)
        self.context = old_cx
        # Stats
        old_cx.defs_list.append(new_cx)
    #@+node:ekr.20160108105958.23: *5* p1.Interactive
    def do_Interactive(self,node):

        assert False,'Interactive context not supported'
    #@+node:ekr.20160108105958.24: *5* p1.Lambda
    def do_Lambda (self,node):

        # Synthesize a lambda name in the old context.
        # This name must not conflict with split names of the form name@n.
        old_cx = self.context
        name = 'Lambda@@%s' % self.stats.n_lambdas
        # Define a Context for the 'lambda' variables.
        new_cx = Context(
            fn=None,
            kind='lambda',
            name=name,
            node=node,
            parent_context=old_cx)
        setattr(node,'new_cx',new_cx)
        # Evaluate expression in the new context.
        self.context = new_cx
        self.def_args_helper(new_cx,node.args)
        self.visit(node.body)
        self.context = old_cx
        # Stats...
        self.stats.n_lambdas += 1
    #@+node:ekr.20160108105958.26: *5* p1.Module
    def do_Module (self,node):

        # Not yet: Get the module context from the global dict if possible.
        new_cx = Context(
            fn=self.fn,
            kind='module',
            name=None,
            node=node,
            parent_context=None)
        self.context = new_cx
        self.visit_list(node.body)
        self.context = None
    #@+node:ekr.20160109135022.1: *4* Expressions
    #@+node:ekr.20160108105958.13: *5* p1.Attribute (Revise)
    # Attribute(expr value, identifier attr, expr_context ctx)

    def do_Attribute(self,node):

        # Visit...
        # cx = self.context
        old_attr, self.in_attr = self.in_attr, True
        # ctx = self.kind(node.ctx)
        self.visit(node.value)
        # self.visit(node.ctx)
        self.in_attr = old_attr
        if not self.in_attr:
            base_node = node
            kind = self.kind(base_node)
            if kind in ('Builtin','Name'):
                # base_name = base_node.id
                pass
            elif kind in ('Dict','List','Num','Str','Tuple',):
                pass
            elif kind in ('BinOp','UnaryOp'):
                pass
            else:
                assert False,kind
        # Stats...
        self.stats.n_attributes += 1
    #@+node:ekr.20160108105958.17: *5* p1.Expr
    # Expr(expr value)

    def do_Expr(self,node):

        # Visit...
        cx = self.context
        self.visit(node.value)
        # Stats...
        self.stats.n_expressions += 1
        cx.expressions_list.append(node)
        cx.statements_list.append(node)
    #@+node:ekr.20160108105958.27: *5* p1.Name (REWRITE)
    def do_Name(self,node):

        trace = False
        cx  = self.context
        ctx = self.kind(node.ctx)
        name = node.id
        # def_flag,ref_flag=False,False

        if ctx in ('AugLoad','AugStore','Load'):
            # Note: AugStore does *not* define the symbol.
            cx.reference_name(name)
            self.stats.n_load_names += 1
        elif ctx == 'Store':
            # if name not in cx.global_names:
            if trace: g.trace('Store: %s in %s' % (name,cx))
            self.stats.n_store_names += 1
        elif ctx == 'Param':
            if trace: g.trace('Param: %s in %s' % (name,cx))
            self.stats.n_param_refs += 1
        else:
            assert ctx == 'Del',ctx
            self.stats.n_del_names += 1
    #@+node:ekr.20160109140648.1: *4* Imports
    #@+node:ekr.20160108105958.21: *5* p1.Import
    #@+at From Guido:
    # 
    # import x            -->  x = __import__('x')
    # import x as y       -->  y = __import__('x')
    # import x.y.z        -->  x = __import__('x.y.z')
    # import x.y.z as p   -->  p = __import__('x.y.z').y.z
    #@@c

    def do_Import(self,node):
        '''
        Add the imported file to u.files_list if needed
        and create a context for the file.'''
        cx = self.context
        cx.statements_list.append(node)
        # e_list, names = [],[]
        for fn,asname in self.get_import_names(node):
            self.resolve_import_name(fn)
            # Not yet.
            # # Important: do *not* analyze modules not in the files list.
            # if fn2:
                # mname = self.u.module_name(fn2)
                # if g.shortFileName(fn2) in self.u.files_list:
                    # if mname not in self.u.module_names:
                        # self.u.module_names.append(mname)
                # # if trace: g.trace('%s as %s' % (mname,asname))
                # def_name = asname or mname
                # names.append(def_name)
                # e = cx.st.define_name(def_name) # sets e.defined.
                # cx.imported_symbols_list.append(def_name)
                # if trace: g.trace('define: (Import) %10s in %s' % (def_name,cx))
                # e_list.append(e)

                # # Add the constant type to the list of types for the *variable*.
                # mod_cx = self.u.modules_dict.get(fn2) or LibraryModuleContext(self.u,fn2)
                # e.types_cache[''] = mod_cx.module_type
                # # self.u.stats.n_imports += 1
            # else:
                # if trace: g.trace('can not resolve %s in %s' % (fn,cx))

        # for e in e_list:
            # e.defs_list.append(node)
            # e.refs_list.append(node)
    #@+node:ekr.20160108105958.22: *5* p1.ImportFrom
    #@+at From Guido:
    # 
    # from p.q import x       -->  x = __import__('p.q', fromlist=['x']).x
    # from p.q import x as y  -->  y = __import__('p.q', fromlist=['x']).x
    # from ..x.y import z     -->  z = __import('x.y', level=2, fromlist=['z']).z
    # 
    # All these equivalences are still somewhat approximate; __import__
    # isn't looked up the way other variables are looked up (it is taken
    # from the current builtins), and if the getattr operation in the "from"
    # versions raises AttributeError that is translated into ImportError.
    # 
    # There's also a subtlety where "import x.y" implies that y must be a
    # submodule/subpackage of x, whereas in "from x import y" it may be
    # either a submodule/subpackage or a plain attribute (e.g. a class,
    # function or some other variable).
    #@@c

    def do_ImportFrom(self,node):
        '''
        Add the imported file to u.files_list if needed
        and add the imported symbols to the *present* context.
        '''
        cx = self.context
        cx.statements_list.append(node)
        self.resolve_import_name(node.module)
        for fn,asname in self.get_import_names(node):
            fn2 = asname or fn
            cx.import_name(fn2)
    #@+node:ekr.20160108105958.9: *5* p1.get_import_names
    def get_import_names (self,node):
        '''Return a list of the the full file names in the import statement.'''
        result = []
        for ast2 in node.names:

            if self.kind(ast2) == 'alias':
                data = ast2.name,ast2.asname
                result.append(data)
            else:
                g.trace('unsupported kind in Import.names list',self.kind(ast2))
        return result
    #@+node:ekr.20160108105958.10: *5* p1.resolve_import_name
    def resolve_import_name (self,spec):
        '''Return the full path name corresponding to the import spec.'''
        trace = False ; verbose = False
        if not spec:
            if trace: g.trace('no spec')
            return ''
        # This may not work for leading dots.
        aList,path,paths = spec.split('.'),None,None
        name = 'no name'
        for name in aList:
            try:
                f,path,description = imp.find_module(name,paths)
                if not path: break
                paths = [path]
                if f: f.close()
            except ImportError:
                # Important: imports can fail due to Python version.
                # Thus, such errors are not necessarily searious.
                if trace: g.trace('failed: %s paths: %s cx: %s' % (
                    name,paths,self.context))
                path = None
                break
        if trace and verbose: g.trace(name,path)
        if not path:
            if trace: g.trace('no path')
            return ''
        if path.endswith('.pyd'):
            if trace: g.trace('pyd: %s' % path)
            return ''
        else:
            if trace: g.trace('path: %s' % path)
            return path
    #@+node:ekr.20160108105958.29: *4* Operators... To be deleted???
    # operator = Add | BitAnd | BitOr | BitXor | Div
    # FloorDiv | LShift | Mod | Mult | Pow | RShift | Sub |

    def do_Add(self,node):       setattr(node,'op_name','+')
    def do_BitAnd(self,node):    setattr(node,'op_name','&')
    def do_BitOr(self,node):     setattr(node,'op_name','|')
    def do_BitXor(self,node):    setattr(node,'op_name','^')
    def do_Div(self,node):       setattr(node,'op_name','/')
    def do_FloorDiv(self,node):  setattr(node,'op_name','//')
    def do_LShift(self,node):    setattr(node,'op_name','<<')
    def do_Mod(self,node):       setattr(node,'op_name','%')
    def do_Mult(self,node):      setattr(node,'op_name','*')
    def do_Pow(self,node):       setattr(node,'op_name','**')
    def do_RShift(self,node):    setattr(node,'op_name','>>')
    def do_Sub(self,node):       setattr(node,'op_name','-')

    # boolop = And | Or
    def do_And(self,node):       setattr(node,'op_name',' and ')
    def do_Or(self,node):        setattr(node,'op_name',' or ')

    # cmpop = Eq | Gt | GtE | In |
    # Is | IsNot | Lt | LtE | NotEq | NotIn
    def do_Eq(self,node):        setattr(node,'op_name','==')
    def do_Gt(self,node):        setattr(node,'op_name','>')
    def do_GtE(self,node):       setattr(node,'op_name','>=')
    def do_In(self,node):        setattr(node,'op_name',' in ')
    def do_Is(self,node):        setattr(node,'op_name',' is ')
    def do_IsNot(self,node):     setattr(node,'op_name',' is not ')
    def do_Lt(self,node):        setattr(node,'op_name','<')
    def do_LtE(self,node):       setattr(node,'op_name','<=')
    def do_NotEq(self,node):     setattr(node,'op_name','!=')
    def do_NotIn(self,node):     setattr(node,'op_name',' not in ')

    # unaryop = Invert | Not | UAdd | USub
    def do_Invert(self,node):   setattr(node,'op_name','~')
    def do_Not(self,node):      setattr(node,'op_name',' not ')
    def do_UAdd(self,node):     setattr(node,'op_name','+')
    def do_USub(self,node):     setattr(node,'op_name','-')
    #@+node:ekr.20160109134929.1: *4* Minor contexts
    #@+node:ekr.20160109130719.1: *5* p1.comprehension (to do)
    # comprehension (expr target, expr iter, expr* ifs)

    def do_comprehension(self, node):

        # Visit...
        self.visit(node.target) # A name.
        self.visit(node.iter) # An attribute.
        for z in node.ifs:
            self.visit(z)
    #@+node:ekr.20160108105958.18: *5* p1.For
    # For(expr target, expr iter, stmt* body, stmt* orelse)

    def do_For(self,node):

        # Visit...
        cx = self.context
        self.visit(node.target)
        self.visit(node.iter)
        for z in node.body:
            self.visit(z)
        for z in node.orelse:
            self.visit(z)
        # Stats...
        self.stats.n_fors += 1
        cx.statements_list.append(node)
        cx.assignments_list.append(node)
    #@+node:ekr.20160108105958.30: *5* p1.With
    def do_With(self,node):

        # Visit...
        cx = self.context
        self.visit(node.context_expr)
        if node.optional_vars:
            self.visit(node.optional_vars)
        for z in node.body:
            self.visit(z)
        # Stats...
        self.stats.n_withs += 1
        cx.statements_list.append(node)
    #@+node:ekr.20160109135003.1: *4* Statements
    #@+node:ekr.20160108105958.12: *5* p1.Assign
    def do_Assign(self,node):

        # Visit...
        for z in node.targets:
            self.visit(z)
        self.visit(node.value)
        # Stats...
        cx = self.context
        self.stats.n_assignments += 1
        cx.assignments_list.append(node)
        cx.statements_list.append(node)
    #@+node:ekr.20160108105958.14: *5* p1.AugAssign
    # AugAssign(expr target, operator op, expr value)

    def do_AugAssign(self,node):

        # Visit...
        self.visit(node.target)
        self.visit(node.value)
        # Stats...
        cx = self.context
        self.stats.n_assignments += 1
        cx.assignments_list.append(node)
        cx.statements_list.append(node)
    #@+node:ekr.20160108105958.15: *5* p1.Call
    # Call(expr func, expr* args, keyword* keywords, expr? starargs, expr? kwargs)

    def do_Call(self,node):

        # Visit...
        self.visit(node.func)
        for z in node.args:
            self.visit(z)
        for z in node.keywords:
            self.visit(z)
        if getattr(node, 'starargs', None):
            self.visit(node.starargs)
        if getattr(node, 'kwargs', None):
            self.visit(node.kwargs)
        # Stats...
        cx = self.context
        self.stats.n_calls += 1
        cx.calls_list.append(node)
    #@+node:ekr.20160108105958.20: *5* p1.Global
    def do_Global(self,node):

        # Visit
        cx = self.context
        for name in node.names:
            cx.global_name(name)
        # Stats...
        cx.statements_list.append(node)
        self.stats.n_globals += 1
    #@+node:ekr.20160108105958.28: *5* p1.Return
    def do_Return(self,node):

        # Visit...
        if node.value:
            self.visit(node.value)
        # Stats...
        self.stats.n_returns += 1
        cx = self.context
        cx.returns_list.append(node)
        cx.statements_list.append(node)
    #@-others
#@+node:ekr.20150525123715.1: ** class ProjectUtils
class ProjectUtils(object):
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
    #@@nobeautify

    def project_files(self, name, force_all=False):
        '''Return a list of all files in the named project.'''
        # Ignore everything after the first space.
        i = name.find(' ')
        if i > -1:
            name = name[: i].strip()
        leo_path, junk = g.os_path_split(__file__)
        # Import the appropriate module.
        try:
            m = importlib.import_module(
                'core' if name == 'leo' else name, # module name.
                name, # package name.
            )
            theDir = g.os_path_dirname(m.__file__)
        except ImportError:
            g.trace('package not found', name)
            return []
        d = {
            'coverage': (['.py'], ['.bzr', 'htmlfiles']),
            'leo':      (['.py'], ['.git']),
            'lib2to3':  (['.py'], ['tests']),
            'pylint':   (['.py'], ['.bzr', 'test']),
            'rope':     (['.py'], ['.bzr']),
        }
        data = d.get(name.lower())
        if not data:
            g.trace('bad project name: %s' % (name))
            return []
        extList, excludeDirs = data
        files = self.files_in_dir(theDir,
            recursive=True,
            extList=extList,
            excludeDirs=excludeDirs,
        )
        if files:
            if name.lower() == 'leo':
                for exclude in ['__init__.py', 'format-code.py']:
                    files = [z for z in files if not z.endswith(exclude)]
                commands_dir = g.os_path_finalize_join(theDir, '..', 'commands')
                command_files = glob.glob('%s%s%s' % (commands_dir, os.sep, '*.py'))
                command_files = [z for z in command_files if not z.endswith('__init__.py')]
                files.extend(command_files)
                plugins_dir = g.os_path_finalize_join(theDir, '..', 'plugins')
                plugins_files = glob.glob('%s%s%s' % (plugins_dir, os.sep, 'qt_*.py'))
                files.extend(plugins_files)
                fn = g.os_path_finalize_join(theDir, '..', 'plugins', 'qtGui.py')
                if fn and g.os_path_exists(fn):
                    files.append(fn)
            if g.app.runningAllUnitTests and len(files) > 1 and not force_all:
                return [files[0]]
        if not files:
            g.trace('no files found in', theDir)
        if g.app.runningAllUnitTests and len(files) > 1 and not force_all:
            return [files[0]]
        else:
            return files
    #@-others
#@+node:ekr.20150604164113.1: ** class ShowData
class ShowData(object):
    '''The driver class for analysis project.'''
    #@+others
    #@+node:ekr.20150604165500.1: *3*  ctor
    def __init__(self, c):
        '''Ctor for ShowData controller class.'''
        self.c = c
        self.files = None
        # Data.
        self.assigns_d = {}
        self.calls_d = {}
        self.classes_d = {}
        self.context_stack = []
        self.defs_d = {}
        self.returns_d = {}
        # Statistics
        self.n_matches = 0
        self.n_undefined_calls = 0
        self.tot_lines = 0
        self.tot_s = 0
    #@+node:ekr.20150604163903.1: *3* run & helpers
    def run(self, files):
        '''Process all files'''
        self.files = files
        t1 = time.time()
        for fn in files:
            s, e = g.readFileIntoString(fn)
            if s:
                self.tot_s += len(s)
                g.trace('%8s %s' % ("{:,}".format(len(s)), g.shortFileName(fn)))
                    # Print len(s), with commas.
                # Fast, accurate:
                # 1.9 sec for parsing.
                # 2.5 sec for Null AstFullTraverer traversal.
                # 2.7 sec to generate all strings.
                # 3.8 sec to generate all reports.
                s1 = g.toEncodedString(s)
                self.tot_lines += len(g.splitLines(s))
                    # Adds less than 0.1 sec.
                node = ast.parse(s1, filename='before', mode='exec')
                ShowDataTraverser(self, fn).visit(node)
                # elif 0: # Too slow, too clumsy: 3.3 sec for tokenizing
                    # readlines = g.ReadLinesClass(s).next
                    # for token5tuple in tokenize.generate_tokens(readlines):
                        # pass
                # else: # Inaccurate. 2.2 sec to generate all reports.
                    # self.scan(fn, s)
            else:
                g.trace('skipped', g.shortFileName(fn))
        t2 = time.time()
            # Get the time exlusive of print time.
        self.show_results()
        g.trace('done: %4.1f sec.' % (t2 - t1))
    #@+node:ekr.20150605054921.1: *3* scan & helpers (a prototype: no longer used)
    if 0:
        # The excellent prototype code, fast, easy but inaccurate.
        # It was a roadmap for the ShowDataTraverser class.

        # Regex patterns (were defined in the ctor)
        r_class = r'class[ \t]+([a-z_A-Z][a-z_A-Z0-9]*).*:'
        r_def = r'def[ \t]+([a-z_A-Z][a-z_A-Z0-9]*)[ \t]*\((.*)\)'
        r_return = r'(return[ \t].*)$'
        r_call = r'([a-z_A-Z][a-z_A-Z0-9]*)[ \t]*\(([^)]*)\)'
        r_all = re.compile('|'.join([r_class, r_def, r_return, r_call,]))

        def scan(self, fn, s):
            lines = g.splitLines(s)
            self.tot_lines += len(lines)
            for i, s in enumerate(lines):
                m = re.search(self.r_all, s)
                if m and not s.startswith('@'):
                    self.match(fn, i, m, s)
    #@+node:ekr.20150605063318.1: *4* match
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
    #@+node:ekr.20150605074749.1: *4* update_context
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
        multiple_only = False # True only show defs defined in more than one place.
        c = self.c
        result = ['@killcolor\n']
        for name in sorted(self.defs_d):
            aList = self.defs_d.get(name, [])
            if len(aList) > 1 or not multiple_only: # not name.startswith('__') and (
                self.show_defs(name, result)
                self.show_calls(name, result)
                self.show_returns(name, result)
        self.show_undefined_calls(result)
        # Put the result in a new node.
        summary = 'files: %s lines: %s chars: %s classes: %s\ndefs: %s calls: %s undefined calls: %s returns: %s' % (
            # g.plural(self.files),
            len(self.files),
            "{:,}".format(self.tot_lines),
            "{:,}".format(self.tot_s),
            "{:,}".format(len(self.classes_d.keys())),
            "{:,}".format(len(self.defs_d.keys())),
            "{:,}".format(len(self.calls_d.keys())),
            "{:,}".format(self.n_undefined_calls),
            "{:,}".format(len(self.returns_d.keys())),
        )
        result.insert(1, summary)
        result.extend(['', summary])
        if c and make:
            last = c.lastTopLevel()
            p2 = last.insertAfter()
            p2.h = 'global signatures'
            p2.b = '\n'.join(result)
            c.redraw(p=p2)
        print(summary)
    #@+node:ekr.20150605160218.1: *4* show_calls
    def show_calls(self, name, result):
        aList = self.calls_d.get(name, [])
        if not aList:
            return
        result.extend(['', '    %s call%s...' % (len(aList), g.plural(aList))])
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
                fn, kind, context_s = context_stack[-1]
                w = max(w, len(context_s))
        for def_tuple in aList:
            context_stack, s = def_tuple
            if not name_added:
                name_added = True
                result.append('\n%s' % name)
                result.append('    %s definition%s...' % (len(aList), g.plural(aList)))
            if context_stack:
                fn, kind, context_s = context_stack[-1]
                def_s = s.strip()
                pad = w - len(context_s)
                result.append('%s%s: %s' % (' ' * (8 + pad), context_s, def_s))
            else:
                result.append('%s%s' % (' ' * 4, s.strip()))
    #@+node:ekr.20150605160341.1: *4* show_returns
    def show_returns(self, name, result):
        aList = self.returns_d.get(name, [])
        if not aList:
            return
        result.extend(['', '    %s return%s...' % (len(aList), g.plural(aList))])
        w, returns = 0, sorted(set(aList))
        for returns_tuple in returns:
            context, s = returns_tuple
            w = max(w, len(context or ''))
        for returns_tuple in returns:
            context, s = returns_tuple
            pad = w - len(context)
            result.append('%s%s: %s' % (' ' * (8 + pad), context, s))
    #@+node:ekr.20150606092147.1: *4* show_undefined_calls
    def show_undefined_calls(self, result):
        '''Show all calls to undefined functions.'''
        # g.trace(sorted(self.defs_d.keys()))
        call_tuples = []
        for s in self.calls_d:
            i = 0
            while True:
                progress = i
                j = s.find('.', i)
                if j == -1:
                    name = s[i:].strip()
                    call_tuple = name, s
                    call_tuples.append(call_tuple)
                    break
                else:
                    i = j + 1
                assert progress < i
        undef = []
        for call_tuple in call_tuples:
            name, s = call_tuple
            if name not in self.defs_d:
                undef.append(call_tuple)
        undef = list(set(undef))
        result.extend(['', '%s undefined call%s...' % (
            len(undef), g.plural(undef))])
        self.n_undefined_calls = len(undef)
        # Merge all the calls for name.
        # There may be several with different s values.
        results_d = {}
        for undef_tuple in undef:
            name, s = undef_tuple
            calls = self.calls_d.get(s, [])
            aList = results_d.get(name, [])
            for call_tuple in calls:
                aList.append(call_tuple)
            results_d[name] = aList
        # Print the final results.
        for name in sorted(results_d):
            calls = results_d.get(name)
            result.extend(['', '%s %s call%s...' % (name, len(calls), g.plural(calls))])
            w = 0
            for call_tuple in calls:
                context2, context1, s = call_tuple
                if context2:
                    w = max(w, 2 + len(context2) + len(context1))
                else:
                    w = max(w, len(context1))
            for call_tuple in calls:
                context2, context1, s = call_tuple
                pad = w - (len(context2) + len(context1))
                if context2:
                    result.append('%s%s::%s: %s' % (
                        ' ' * (2 + pad), context2, context1, s))
                else:
                    result.append('%s%s: %s' % (
                        ' ' * (2 + pad), context1, s))
    #@+node:ekr.20150605140911.1: *3* context_names
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
    #@-others
#@+node:ekr.20150606024455.1: ** class ShowDataTraverser
class ShowDataTraverser(leoAst.AstFullTraverser):
    '''
    Add data about classes, defs, returns and calls to controller's
    dictionaries.
    '''

    def __init__(self, controller, fn):
        '''Ctor for ShopDataTraverser class.'''
        leoAst.AstFullTraverser.__init__(self)
        module_tuple = g.shortFileName(fn), 'module', g.shortFileName(fn)
            # fn, kind, s.
        self.context_stack = [module_tuple]
        self.controller = controller
        self.fn = g.shortFileName(fn)
        self.formatter = leoAst.AstFormatter()
            # leoAst.AstPatternFormatter()
        self.trace = False
    #@+others
    #@+node:ekr.20150609053332.1: *3* sd.Helpers
    #@+node:ekr.20150606035006.1: *4* sd.context_names
    def context_names(self):
        '''Return the present context names.'''
        result = []
        n = len(self.context_stack)
        for i in n - 1, n - 2:
            if i >= 0:
                fn, kind, s = self.context_stack[i]
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
            else:
                result.append('')
                break
        # g.trace(list(reversed(result)))
        return reversed(result)
    #@+node:ekr.20150609053010.1: *4* sd.format
    def format(self, node):
        '''Return the formatted version of an Ast Node.'''
        return self.formatter.format(node).strip()
    #@+node:ekr.20150606024455.62: *3* sd.visit
    def visit(self, node):
        '''
        Visit a *single* ast node. Visitors must visit their children
        explicitly.
        '''
        method = getattr(self, 'do_' + node.__class__.__name__)
        method(node)

    def visit_children(self, node):
        '''Override to ensure this method is never called.'''
        assert False, 'must visit children explicitly'
    #@+node:ekr.20150609052952.1: *3* sd.Visitors
    #@+node:ekr.20150607200422.1: *4* sd.Assign
    def do_Assign(self, node):
        '''Handle an assignment statement: Assign(expr* targets, expr value)'''
        value = self.format(self.visit(node.value))
        assign_tuples = []
        for target in node.targets:
            target = self.format(self.visit(target))
            s = '%s=%s' % (target, value)
            context2, context1 = self.context_names()
            assign_tuple = context2, context1, s
            assign_tuples.append(assign_tuple)
            aList = self.controller.assigns_d.get(target, [])
            aList.extend(assign_tuples)
            self.controller.calls_d[target] = aList
    #@+node:ekr.20150607200439.1: *4* sd.AugAssign
    def do_AugAssign(self, node):
        '''
        Handle an augmented assignement:
        AugAssign(expr target, operator op, expr value).
        '''
        target = self.format(self.visit(node.target))
        s = '%s=%s' % (target, self.format(self.visit(node.value)))
        context2, context1 = self.context_names()
        assign_tuple = context2, context1, s
        aList = self.controller.assigns_d.get(target, [])
        aList.append(assign_tuple)
        self.controller.calls_d[target] = aList
    #@+node:ekr.20150606024455.16: *4* sd.Call
    def do_Call(self, node):
        '''
        Handle a call statement:
        Call(expr func, expr* args, keyword* keywords, expr? starargs, expr? kwargs)
        '''
        # Update data.
        s = self.format(node)
        name = self.format(node.func)
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
    #@+node:ekr.20150606024455.3: *4* sd.ClassDef
    def do_ClassDef(self, node):
        '''
        Handle a class defintion:
        ClassDef(identifier name, expr* bases, stmt* body, expr* decorator_list)
        '''
        # Format.
        if node.bases:
            bases = [self.format(z) for z in node.bases]
            s = 'class %s(%s):' % (node.name, ','.join(bases))
        else:
            s = 'class %s:' % node.name
        if self.trace: g.trace(s)
        # Enter the new context.
        context_tuple = self.fn, 'class', s
        self.context_stack.append(context_tuple)
        # Update data.
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
    #@+node:ekr.20150606024455.4: *4* sd.FunctionDef
    def do_FunctionDef(self, node):
        '''
        Visit a function defintion:
        FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)
        '''
        # Format.
        args = self.format(node.args) if node.args else ''
        s = 'def %s(%s):' % (node.name, args)
        if self.trace: g.trace(s)
        # Enter the new context.
        context_tuple = self.fn, 'def', s
        self.context_stack.append(context_tuple)
        # Update data.
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
    #@+node:ekr.20150606024455.55: *4* sd.Return
    def do_Return(self, node):
        '''Handle a 'return' statement: Return(expr? value)'''
        # Update data.
        s = self.format(node)
        if self.trace: g.trace(s)
        context, name = self.context_names()
        aList = self.controller.returns_d.get(name, [])
        return_tuple = context, s
        aList.append(return_tuple)
        self.controller.returns_d[name] = aList
        # Visit.
        if node.value:
            self.visit(node.value)
    #@-others
#@+node:ekr.20171211163833.1: ** class Stats
class Stats(object):
    '''
    A basic statistics class.  Use this way:
        
        stats = Stats()
        stats.classes += 1
        stats.defs += 1
        stats.report()
    '''

    d = {}
    
    def __getattr__(self, name):
        return self.d.get(name, 0)
        
    def __setattr__(self, name, val):
        self.d[name] = val
        
    def report(self):
        if self.d:
            n = max([len(key) for key in self.d])
            for key, val in sorted(self.d.items()):
                print('%*s: %s' % (n, key, val))
        else:
            print('no stats')
#@+node:ekr.20171211061816.1: ** top-level test functions
#@+node:ekr.20150704135836.1: *3* testShowData (leoCheck.py)
def test(c, files):
    r'''
    A stand-alone version of @button show-data.  Call as follows:

        import leo.core.leoCheck as leoCheck
        files = (
            [
                # r'c:\leo.repo\leo-editor\leo\core\leoNodes.py',
            ] or
            leoCheck.ProjectUtils().project_files('leo')
        )
        leoCheck.test(files)
    '''
    # pylint: disable=import-self
    import leo.core.leoCheck as leoCheck
    leoCheck.ShowData(c=c).run(files)
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
