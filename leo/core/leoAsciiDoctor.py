# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20190515070742.1: * @file leoAsciiDoctor.py
#@@first
"""Supports AsciiDoctor by defining the adoc command."""
#@+<< leoAsciiDoctor imports >>
#@+node:ekr.20190515070742.3: ** << leoAsciiDoctor imports >>
import io
StringIO = io.StringIO
import re
import time
import leo.core.leoGlobals as g

#@-<< leoAsciiDoctor imports >>
#@+others
#@+node:ekr.20191006153522.1: ** commands
#@+node:ekr.20190515070742.22: *3* adoc_command: @cmd('adoc')
@g.command('adoc')
def adoc_command(event=None, verbose=True):
    #@+<< adoc command docstring >>
    #@+node:ekr.20190515115100.1: *4* << adoc command docstring >>
    """
    The adoc command writes all @adoc nodes in the selected tree to the
    files given in each @@doc node. If no @adoc nodes are found, the
    command looks up the tree.

    Each @adoc node should have the form: `@adoc x.adoc`. Relative file names
    are relative to the base directory.  See below.

    By default, the adoc command creates AsciiDoctor headings from Leo
    headlines. However, the following kinds of nodes are treated differently:
        
    - @ignore-tree: Ignore the node and its descendants.
    - @ignore-node: Ignore the node.
    - @no-head:     Ignore the headline. Do not generate a heading.

    After running the adoc command, use the asciidoctor command to convert the
    x.adoc files to x.html.
        
    Settings
    --------

    AsciiDoctor itself provides many settings, including::
        
        = Title
        :stylesdir: mystylesheets/
        :stylesheet: mystyles.css
        
    These can also be specified on the command line::

        asciidoctor -a stylesdir=mystylesheets/ -a stylesheet=mystyles.css 

    @string adoc-base-directory specifies the base for relative file names.
    The default is c.frame.openDirectory

    Scripting interface
    -------------------

    Scripts may invoke the adoc command as follows::
        
        event = g.Bunch(base_dicrectory=my_directory, p=some_node)
        c.asciiDoctorCommands.ad_command(event=event)
        
    This @button node runs the adoc command and coverts all results to .html::
        
        import os
        paths = c.asciiDoctorCommands.ad_command(event=g.Bunch(p=p))
        paths = [z.replace('/', os.path.sep) for z in paths]
        input_paths = ' '.join(paths)
        g.execute_shell_commands(['asciidoctor %s' % input_paths])

    """
    #@-<< adoc command docstring >>
    c = event and event.get('c')
    if not c:
        return None
    return c.asciiDoctorCommands.adoc_command(event, verbose=verbose)
#@+node:ekr.20191006153411.1: *3* pandoc_command: @cmd('pandoc')
@g.command('pandoc')
def pandoc_command(event, verbose=True):
    #@+<< pandoc command docstring >>
    #@+node:ekr.20191006153547.1: *4* << pandoc command docstring >>
    """
    The pandoc command writes all @pandoc nodes in the selected tree to the
    files given in each @pandoc node. If no @pandoc nodes are found, the
    command looks up the tree.

    Each @pandoc node should have the form: `@pandoc x.adoc`. Relative file names
    are relative to the base directory.  See below.

    By default, the adoc command creates AsciiDoctor headings from Leo
    headlines. However, the following kinds of nodes are treated differently:
        
    - @ignore-tree: Ignore the node and its descendants.
    - @ignore-node: Ignore the node.
    - @no-head:     Ignore the headline. Do not generate a heading.

    After running the adoc command, use the asciidoctor command to convert the
    x.adoc files to x.html.
        
    Settings
    --------

    AsciiDoctor itself provides many settings, including::
        
        = Title
        :stylesdir: mystylesheets/
        :stylesheet: mystyles.css
        
    These can also be specified on the command line::

        asciidoctor -a stylesdir=mystylesheets/ -a stylesheet=mystyles.css 

    @string adoc-base-directory specifies the base for relative file names.
    The default is c.frame.openDirectory

    Scripting interface
    -------------------

    Scripts may invoke the adoc command as follows::
        
        event = g.Bunch(base_dicrectory=my_directory, p=some_node)
        c.asciiDoctorCommands.ad_command(event=event)
        
    This @button node runs the adoc command and coverts all results to .html::
        
        import os
        paths = c.asciiDoctorCommands.ad_command(event=g.Bunch(p=p))
        paths = [z.replace('/', os.path.sep) for z in paths]
        input_paths = ' '.join(paths)
        g.execute_shell_commands(['asciidoctor %s' % input_paths])

    """
    #@-<< pandoc command docstring >>
    c = event and event.get('c')
    if not c:
        return None
    return c.asciiDoctorCommands.pandoc_command(event, verbose=verbose)
#@+node:ekr.20191006154236.1: ** class AsciiDoctorCommands
class AsciiDoctorCommands:
    """A class to write AsiiDoctor markup in Leo outlines."""
    
    def __init__(self, c):
        self.c = c
        self.base_directory = None
        self.kind = None # 'adoc' or 'pandoc'
        self.level_offset = 0
        self.root_level = 0

    #@+others
    #@+node:ekr.20191006155051.1: *3* adoc.commands
    def adoc_command(self, event=None, verbose=True):
        return self.command_helper(event, kind='adoc', verbose=verbose)
        
    def pandoc_command(self, event=None, verbose=True):
        return self.command_helper(event, kind='pandoc', verbose=verbose)

    #@+node:ekr.20191006153233.1: *3* adoc.command_helper
    def command_helper(self, event, kind, verbose):

        def predicate(p):
            return self.ad_filename(p)

        # Find all roots.
        t1 = time.time()
        c = self.c
        self.kind = kind
        p = event.p if event and hasattr(event, 'p') else c.p
        if event and hasattr(event, 'base_directory'):
            self.base_directory = event.base_directory
        else:
            directory = c.config.getString('adoc-base-directory')
            self.base_directory = directory or c.frame.openDirectory
        roots = g.findRootsWithPredicate(c, p, predicate=predicate)
        if not roots:
            g.warning('No @ascii-doctor nodes in', p.h)
            return []
        # Write each root.
        paths = []
        for p in roots:
            path = self.write_root(p)
            if path:
                paths.append(path)
        t2 = time.time()
        if verbose:
            g.es_print('adoc: wrote %s file%s in %4.2f sec.' % (
                len(paths), g.plural(len(paths)), t2 - t1))
        return paths
    #@+node:ekr.20190515084219.1: *3* adoc.ad_filename
    adoc_pattern = re.compile(r'^@(adoc|ascii-doctor)')

    def ad_filename(self, p):
        """Return the filename of the @adoc or @pandoc node, or None."""
        h = p.h.rstrip()
        if self.kind == 'adoc':
            m = self.adoc_pattern.match(h)
            if m:
                prefix = m.group(1)
                return h[1+len(prefix):].strip()
            return None
        assert self.kind == 'pandoc', g.callers()
        prefix = '@pandoc'
        if g.match_word(h, 0, prefix):
            return h[len(prefix):].strip()
        return None
    #@+node:ekr.20190515091706.1: *3* adoc.open_file & helper
    def open_file(self, fn):
        """Open the file, returning (fn, f)"""
        fn = g.os_path_finalize_join(self.base_directory, fn)
        if not self.create_directory(fn):
            return fn, None
        try:
            return fn, open(fn, 'w', encoding='utf-8', errors='replace')
        except Exception:
            g.es_print('can not open: %r' % fn)
            g.es_exception()
            return fn, None
    #@+node:ekr.20190515070742.79: *4* adoc.create_directory
    def create_directory(self, fn):
        """
        Create the directory for fn if
        a) it doesn't exist and
        b) the user options allow it.

        Return True if the directory existed or was made.
        """
        c = self.c
        theDir, junk = g.os_path_split(fn)
        theDir = g.os_path_finalize(theDir) # #1341.
        if g.os_path_exists(theDir):
            return True
        ok = g.makeAllNonExistentDirectories(theDir, c=c, force=False)
        if not ok:
            g.error('did not create:', theDir)
        return ok
    #@+node:ekr.20190515070742.24: *3* adoc.write_root & helpers
    def write_root(self, root):
        """Process all nodes in an @ad tree."""
        fn =  self.ad_filename(root)
        if not fn:
            g.es_print('Can not happen: not a @ad node: %r' % root.h)
            return None
        path, self.output_file = self.open_file(fn)
        if not self.output_file:
            return None
        # Write only the body of the root.
        self.write_body(root)
        # Write all nodes of the tree, except ignored nodes.
        self.level_offset = self.compute_level_offset(root)
        self.root_level = root.level()
        p = root.threadNext() # Returns a copy.
        after = root.nodeAfterTree()
        while p and p != after:
            h = p.h.rstrip()
            if g.match_word(h, 0, '@ignore-tree'):
                p.moveToNodeAfterTree()
                continue
            if g.match_word(h, 0, '@ignore-node'):
                p.moveToThreadNext()
                continue
            if not g.match_word(h, 0, '@no-head'):
                self.write_headline(p)
            self.write_body(p)
            p.moveToThreadNext()
        self.output_file.close()
        return path
    #@+node:ekr.20190515114836.1: *4* adoc.compute_level_offset
    title_pattern = re.compile(r'^= ')

    def compute_level_offset(self, root):
        """
        Return 1 if the root.b contains a title.  Otherwise 0.
        """
        for line in g.splitLines(root.b):
            if self.title_pattern.match(line):
                return 1
        return 0
    #@+node:ekr.20190515070742.38: *4* adoc.write_body
    def write_body(self, p):
        """Write p.b"""
        # We no longer add newlines to the start of nodes because
        # we write a blank line after all sections.
        self.output_file.write(g.ensureTrailingNewlines(p.b, 2))
    #@+node:ekr.20190515070742.47: *4* adoc.write_headline
    def write_headline(self, p):
        """Generate an AsciiDoctor section"""
        if not p.h.strip():
            return
        level = self.level_offset + p.level() - self.root_level
        section = '=' * max(0, level)
        if self.kind == 'pandoc':
            section = ' ' + section
        self.output_file.write('%s %s\n' % (section, p.h))
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
