# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20150605175037.1: * @file leoCheck.py
#@@first
"""Experimental code checking for Leo."""
import leo.core.leoGlobals as g
import leo.core.leoAst as leoAst
if 0:
    import importlib
    importlib.reload(leoAst)
import os
#@+others
#@+node:ekr.20160109102859.1: ** class Context
class Context:
    """
    Context class (NEW)

    Represents a binding context: module, class or def.

    For any Ast context node N, N.cx is a reference to a Context object.
    """
    #@+others
    #@+node:ekr.20160109103533.1: *3* Context.ctor
    def __init__ (self, fn, kind, name, node, parent_context):
        """Ctor for Context class."""
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
        """Define a name in this context."""
        self.defined_names.add(name)
        if name in self.referenced_names:
            self.referenced_names.remove(name)
    #@+node:ekr.20160109143040.1: *3* Context.global_name
    def global_name(self, name):
        """Handle a global name in this context."""
        self.global_names.add(name)
        # Not yet.
            # Both Python 2 and 3 generate SyntaxWarnings when a name
            # is used before the corresponding global declarations.
            # We can make the same assumpution here:
            # give an *error* if an STE appears in this context for the name.
            # The error indicates that scope resolution will give the wrong result.
            # e = cx.st.d.get(name)
            # if e:
                # self.u.error(f"name {name!r} used prior to global declaration")
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
#@+node:ekr.20150525123715.1: ** class ProjectUtils
class ProjectUtils:
    """A class to compute the files in a project."""
    # To do: get project info from @data nodes.
    #@+others
    #@+node:ekr.20150525123715.2: *3* pu.files_in_dir
    def files_in_dir(self, theDir, recursive=True, extList=None, excludeDirs=None):
        """
        Return a list of all Python files in the directory.
        Include all descendants if recursiveFlag is True.
        Include all file types if extList is None.
        """
        # import glob
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
                result.extend(g.glob_glob(f"{theDir}.*{ext}"))
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
        if not dir_:
            g.trace(f"bad project name: {name}")
        if not g.os_path_exists(dir_):
            g.trace('directory not found:' % (dir_))
        return dir_ or ''
    #@+node:ekr.20171213071416.1: *3* pu.leo_core_files
    def leo_core_files(self):
        """Return all the files in Leo's core."""
        loadDir = g.app.loadDir
        # Compute directories.
        commands_dir = g.os_path_finalize_join(loadDir, '..', 'commands')
        plugins_dir = g.os_path_finalize_join(loadDir, '..', 'plugins')
        # Compute files.
        core_files = g.glob_glob('%s%s%s' % (loadDir, os.sep, '*.py'))
        for exclude in ['format-code.py',]:
            core_files = [z for z in core_files if not z.endswith(exclude)]
        command_files = g.glob_glob(f"{commands_dir}{os.sep}{'*.py'}")
        plugins_files = g.glob_glob(f"{plugins_dir}{os.sep}{'qt_*.py'}")
        # Compute the result.
        files = core_files + command_files + plugins_files
        files = [z for z in files if not z.endswith('__init__.py')]
        return files
    #@+node:ekr.20150525123715.4: *3* pu.project_files
    #@@nobeautify

    def project_files(self, name, force_all=False):
        """Return a list of all files in the named project."""
        # Ignore everything after the first space.
        i = name.find(' ')
        if i > -1:
            name = name[: i].strip()
        leo_path, junk = g.os_path_split(__file__)
        if name == 'leo':
            # Get the leo files directly.
            return self.leo_core_files()
        # Import the appropriate module.
        try:
            m = importlib.import_module(name, name)
            theDir = g.os_path_dirname(m.__file__)
        except ImportError:
            g.trace('package not found', name)
            return []
        d = {
            'coverage': (['.py'], ['.bzr', 'htmlfiles']),
            'lib2to3':  (['.py'], ['tests']),
            'pylint':   (['.py'], ['.bzr', 'test']),
            'rope':     (['.py'], ['.bzr']),
        }
        data = d.get(name.lower())
        if not data:
            g.trace(f"bad project name: {name}")
            return []
        extList, excludeDirs = data
        files = self.files_in_dir(theDir,
            recursive=True,
            extList=extList,
            excludeDirs=excludeDirs,
        )
        if files:
            if g.app.runningAllUnitTests and len(files) > 1 and not force_all:
                return [files[0]]
        if not files:
            g.trace(f"no files found for {name} in {theDir}")
        if g.app.runningAllUnitTests and len(files) > 1 and not force_all:
            return [files[0]]
        return files
    #@-others
#@+node:ekr.20171211163833.1: ** class Stats
class Stats:
    """
    A basic statistics class.  Use this way:
        
        stats = Stats()
        stats.classes += 1
        stats.defs += 1
        stats.report()
    """

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
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
