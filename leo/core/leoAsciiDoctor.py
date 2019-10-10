# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20190515070742.1: * @file leoAsciiDoctor.py
#@@first
"""Supports AsciiDoctor by defining the adoc command."""
#@+<< leoAsciiDoctor imports >>
#@+node:ekr.20190515070742.3: ** << leoAsciiDoctor imports >>
from shutil import which
import io
StringIO = io.StringIO
import os
import re
import time
import leo.core.leoGlobals as g

#@-<< leoAsciiDoctor imports >>
asciidoctor_exec = which('asciidoctor')
asciidoc3_exec = which('asciidoc3')
pandoc_exec = which('pandoc')
#@+others
#@+node:ekr.20191006153522.1: ** adoc & pandoc commands
#@+node:ekr.20190515070742.22: *3* @cmd('adoc') & @cmd('adoc-with-preview')
@g.command('adoc')
def adoc_command(event=None, verbose=True):
    #@+<< adoc command docstring >>
    #@+node:ekr.20190515115100.1: *4* << adoc command docstring >>
    """
    The adoc command writes all @adoc nodes in the selected tree to the
    files given in each @doc node. If no @adoc nodes are found, the
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
    return c.asciiDoctorCommands.adoc_command(event, preview=False, verbose=verbose)
    
@g.command('adoc-with-preview')
def adoc_with_preview_command(event=None, verbose=True):
    """Run the adoc command, then show the result in the browser."""
    c = event and event.get('c')
    if not c:
        return None
    return c.asciiDoctorCommands.adoc_command(event, preview=True, verbose=verbose)
#@+node:ekr.20191006153411.1: *3* @cmd('pandoc') & @cmd('pandoc-with-preview')
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

@g.command('pandoc-with-preview')
def pandoc_with_preview_command(event=None, verbose=True):
    """Run the pandoc command, then show the result in the browser."""
    c = event and event.get('c')
    if not c:
        return None
    return c.asciiDoctorCommands.pandoc_command(event, preview=True, verbose=verbose)
#@+node:ekr.20191006154236.1: ** class AsciiDoctorCommands
class AsciiDoctorCommands:
    """A class to write AsiiDoctor or docutils markup in Leo outlines."""
    
    def __init__(self, c):
        self.c = c
        self.kind = None # 'adoc' or 'pandoc'
        self.level_offset = 0
        self.root_level = 0

    #@+others
    #@+node:ekr.20191006153233.1: *3* adoc.command_helper & helpers
    def command_helper(self, event, kind, preview, verbose):

        def predicate(p):
            return self.ad_filename(p)

        # Find all roots.
        t1 = time.time()
        c = self.c
        self.kind = kind
        p = event.p if event and hasattr(event, 'p') else c.p
        roots = g.findRootsWithPredicate(c, p, predicate=predicate)
        if not roots:
            g.warning('No @adoc nodes in', p.h)
            return []
        # Write each root to a file.
        i_paths = []
        for p in roots:
            try:
                i_path = self.ad_filename(p)
                i_path = g.os_path_finalize(i_path)
                with open(i_path, 'w', encoding='utf-8', errors='replace') as self.output_file:
                    self.write_root(p)
                    i_paths.append(i_path)
            except IOError:
                g.es_print(f"Can not open {i_path!r}")
            except Exception:
                g.es_print('Unexpected exception')
                g.es_exception()
        # Convert each file to html.
        o_paths = []
        for i_path in i_paths:
            o_path = self.compute_opath(i_path)
            o_paths.append(o_path)
            if kind == 'adoc':
                self.run_asciidoctor(i_path, o_path)
            else:
                self.run_pandoc(i_path, o_path)
            print(f"{kind}: wrote {o_path}")
        if preview:
            # open .html files in the default browser.
            g.execute_shell_commands(o_paths)
        t2 = time.time()
        if verbose:
            n = len(i_paths)
            g.es_print(f"{kind}: wrote {n} file{g.plural(n)} in {(t2-t1):4.2f} sec.")
        return i_paths
    #@+node:ekr.20190515084219.1: *4* adoc.ad_filename
    adoc_pattern = re.compile(r'^@(adoc|asciidoctor)')

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
    #@+node:ekr.20191007053522.1: *4* adoc.compute_opath
    def compute_opath(self, i_path):
        """
        Neither asciidoctor nor pandoc handles extra extentions well.
        """
        c = self.c
        for i in range(3):
            i_path, ext = os.path.splitext(i_path)
            if not ext:
                break
        # #1373.
        base_dir = os.path.dirname(c.fileName())
        return g.os_path_finalize_join(base_dir, i_path + '.html')
    #@+node:ekr.20191007043110.1: *4* adoc.run_asciidoctor
    def run_asciidoctor(self, i_path, o_path):
        """
        Process the input file given by i_path with asciidoctor or asciidoc3.
        """
        global asciidoctor_exec, asciidoc3_exec
        assert asciidoctor_exec or asciidoc3_exec, g.callers()
        # Call the external program to write the output file.
        prog = 'asciidoctor' if asciidoctor_exec else 'asciidoc3'
        command = f"{prog} {i_path} -o {o_path} -b html5"
            # The -e option deletes css.
        g.execute_shell_commands(command)
    #@+node:ekr.20191007043043.1: *4* adoc.run_pandoc
    def run_pandoc(self, i_path, o_path):
        """
         Process the input file given by i_path with pandoc.
        """
        global pandoc_exec
        assert pandoc_exec, g.callers()
        # Call pandoc to write the output file.
        command = f"pandoc {i_path} -t html5 -o {o_path}"
            # --quiet does no harm.
        g.execute_shell_commands(command)
    #@+node:ekr.20190515070742.24: *3* adoc.write_root & helpers
    def write_root(self, root):
        """Process all nodes in an @adoc tree to self.output_file"""
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
    #@+node:ekr.20190515114836.1: *4* adoc.compute_level_offset
    adoc_title_pat = re.compile(r'^= ')
    pandoc_title_pat = re.compile(r'^= ')

    def compute_level_offset(self, root):
        """
        Return 1 if the root.b contains a title.  Otherwise 0.
        """
        pattern = self.adoc_title_pat if self.kind == 'adoc' else self.pandoc_title_pat
        for line in g.splitLines(root.b):
            if pattern.match(line):
                return 1
        return 0
    #@+node:ekr.20190515070742.38: *4* adoc.write_body
    def write_body(self, p):
        """Write p.b"""
        # We no longer add newlines to the start of nodes because
        # we write a blank line after all sections.
        s = self.remove_directives(p.b)
        self.output_file.write(g.ensureTrailingNewlines(s, 2))
    #@+node:ekr.20190515070742.47: *4* adoc.write_headline
    def write_headline(self, p):
        """Generate an AsciiDoctor section"""
        if not p.h.strip():
            return
        level = max(0, self.level_offset + p.level() - self.root_level)
        if self.kind == 'pandoc':
            section = '#' * min(level, 6)
        else:
            section = '=' * level
        self.output_file.write(f"{section} {p.h}\n\n")
    #@+node:ekr.20191007054942.1: *4* adoc.remove_directives
    def remove_directives(self, s):
        lines = g.splitLines(s)
        result = []
        for s in lines:
            if s.startswith('@'):
                i = g.skip_id(s, 1)
                word = s[1: i]
                if word in g.globalDirectiveList:
                    continue
            result.append(s)
        return ''.join(result)
    #@+node:ekr.20191006155051.1: *3* adoc.commands
    def adoc_command(self, event=None, preview=False, verbose=True):
        global asciidoctor_exec, asciidoc3_exec
        if asciidoctor_exec or asciidoc3_exec:
            return self.command_helper(event, kind='adoc', preview=preview, verbose=verbose)
        name = 'adoc-with-preview' if preview else 'adoc'
        g.es_print(f"{name} requires either asciidoctor or asciidoc3")
        return []
        
    def pandoc_command(self, event=None, preview=False, verbose=True):
        global pandoc_exec
        if pandoc_exec:
            return self.command_helper(event, kind='pandoc', preview=preview, verbose=verbose)
        name = 'pandoc-with-preview' if preview else 'pandoc'
        g.es_print(f"{name} requires pandoc")
        return []
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
