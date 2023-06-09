#@+leo-ver=5-thin
#@+node:ekr.20190515070742.1: * @file leoMarkup.py
"""Supports @adoc, @pandoc and @sphinx nodes and related commands."""
#@+<< leoMarkup imports & annotations >>
#@+node:ekr.20190515070742.3: ** << leoMarkup imports & annotations >>
from __future__ import annotations
import io
from shutil import which
import os
import re
import time
from typing import Optional, TYPE_CHECKING
import leo.core.leoGlobals as g

# Abbreviation.
StringIO = io.StringIO

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent as Event
    from leo.core.leoNodes import Position
    File_List = Optional[list[str]]
#@-<< leoMarkup imports & annotations >>

asciidoctor_exec = which('asciidoctor')
asciidoc3_exec = which('asciidoc3')
pandoc_exec = which('pandoc')
sphinx_build = which('sphinx-build')
#@+others
#@+node:ekr.20191006153522.1: ** adoc, pandoc & sphinx commands
#@+node:ekr.20190515070742.22: *3* @g.command: 'adoc' & 'adoc-with-preview')
@g.command('adoc')
def adoc_command(event: Event = None, verbose: bool = True) -> File_List:
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

    After running the adoc command, use the asciidoctor tool to convert the
    x.adoc files to x.html.

    Settings
    --------

    AciiDoctor markup provides many settings, including::

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
        c.markupCommands.adoc_command(event=event)

    This @button node runs the adoc command and coverts all results to .html::

        import os
        paths = c.markupCommands.adoc_command(event=g.Bunch(p=p))
        paths = [z.replace('/', os.path.sep) for z in paths]
        input_paths = ' '.join(paths)
        g.execute_shell_commands(['asciidoctor %s' % input_paths])

    """
    #@-<< adoc command docstring >>
    c = event and event.get('c')
    if not c:
        return None
    return c.markupCommands.adoc_command(event, preview=False, verbose=verbose)

@g.command('adoc-with-preview')
def adoc_with_preview_command(event: Event = None, verbose: bool = True) -> File_List:
    """Run the adoc command, then show the result in the browser."""
    c = event and event.get('c')
    if not c:
        return None
    return c.markupCommands.adoc_command(event, preview=True, verbose=verbose)
#@+node:ekr.20191006153411.1: *3* @g.command: 'pandoc' & 'pandoc-with-preview'
@g.command('pandoc')
def pandoc_command(event: Event, verbose: bool = True) -> File_List:
    #@+<< pandoc command docstring >>
    #@+node:ekr.20191006153547.1: *4* << pandoc command docstring >>
    """
    The pandoc command writes all @pandoc nodes in the selected tree to the
    files given in each @pandoc node. If no @pandoc nodes are found, the
    command looks up the tree.

    Each @pandoc node should have the form: `@pandoc x.adoc`. Relative file names
    are relative to the base directory.  See below.

    By default, the pandoc command creates AsciiDoctor headings from Leo
    headlines. However, the following kinds of nodes are treated differently:

    - @ignore-tree: Ignore the node and its descendants.
    - @ignore-node: Ignore the node.
    - @no-head:     Ignore the headline. Do not generate a heading.

    After running the pandoc command, use the pandoc tool to convert the x.adoc
    files to x.html.

    Settings
    --------

    @string pandoc-base-directory specifies the base for relative file names.
    The default is c.frame.openDirectory

    Scripting interface
    -------------------

    Scripts may invoke the adoc command as follows::

        event = g.Bunch(base_dicrectory=my_directory, p=some_node)
        c.markupCommands.pandoc_command(event=event)

    This @button node runs the adoc command and coverts all results to .html::

        import os
        paths = c.markupCommands.pandoc_command(event=g.Bunch(p=p))
        paths = [z.replace('/', os.path.sep) for z in paths]
        input_paths = ' '.join(paths)
        g.execute_shell_commands(['asciidoctor %s' % input_paths])

    """
    #@-<< pandoc command docstring >>
    c = event and event.get('c')
    if not c:
        return None
    return c.markupCommands.pandoc_command(event, verbose=verbose)

@g.command('pandoc-with-preview')
def pandoc_with_preview_command(event: Event = None, verbose: bool = True) -> File_List:
    """Run the pandoc command, then show the result in the browser."""
    c = event and event.get('c')
    if not c:
        return None
    return c.markupCommands.pandoc_command(event, preview=True, verbose=verbose)
#@+node:ekr.20191017163422.1: *3* @g.command: 'sphinx' & 'sphinx-with-preview'
@g.command('sphinx')
def sphinx_command(event: Event, verbose: bool = True) -> File_List:
    #@+<< sphinx command docstring >>
    #@+node:ekr.20191017163422.2: *4* << sphinx command docstring >>
    """
    The sphinx command writes all @sphinx nodes in the selected tree to the
    files given in each @sphinx node. If no @sphinx nodes are found, the
    command looks up the tree.

    Each @sphinx node should have the form: `@sphinx x`. Relative file names
    are relative to the base directory.  See below.

    By default, the sphinx command creates Sphinx headings from Leo headlines.
    However, the following kinds of nodes are treated differently:

    - @ignore-tree: Ignore the node and its descendants.
    - @ignore-node: Ignore the node.
    - @no-head:     Ignore the headline. Do not generate a heading.

    After running the sphinx command, use the sphinx tool to convert the
    output files to x.html.

    Settings
    --------

    @string sphinx-base-directory specifies the base for relative file names.
    The default is c.frame.openDirectory

    Scripting interface
    -------------------

    Scripts may invoke the sphinx command as follows::

        event = g.Bunch(base_dicrectory=my_directory, p=some_node)
        c.markupCommands.sphinx_command(event=event)

    This @button node runs the sphinx command and coverts all results to .html::

        import os
        paths = c.markupCommands.sphinx_command(event=g.Bunch(p=p))
        paths = [z.replace('/', os.path.sep) for z in paths]
        input_paths = ' '.join(paths)
        g.execute_shell_commands(['asciidoctor %s' % input_paths])

    """
    #@-<< sphinx command docstring >>
    c = event and event.get('c')
    if not c:
        return None
    return c.markupCommands.sphinx_command(event, verbose=verbose)

@g.command('sphinx-with-preview')
def sphinx_with_preview_command(event: Event = None, verbose: bool = True) -> File_List:
    """Run the sphinx command, then show the result in the browser."""
    c = event and event.get('c')
    if not c:
        return None
    return c.markupCommands.sphinx_command(event, preview=True, verbose=verbose)
#@+node:ekr.20191006154236.1: ** class MarkupCommands
class MarkupCommands:
    """A class to write AsiiDoctor or docutils markup in Leo outlines."""

    def __init__(self, c: Cmdr) -> None:
        self.c = c
        self.kind: str = None  # 'adoc' or 'pandoc'
        self.level_offset = 0
        self.root_level = 0
        self.reload_settings()

    def reload_settings(self) -> None:
        c = self.c
        getString = c.config.getString
        self.sphinx_command_dir = getString('sphinx-command-directory')
        self.sphinx_default_command = getString('sphinx-default-command')
        self.sphinx_input_dir = getString('sphinx-input-directory')
        self.sphinx_output_dir = getString('sphinx-output-directory')

    #@+others
    #@+node:ekr.20191006153233.1: *3* markup.command_helper & helpers
    def command_helper(self, event: Event, kind: str, preview: bool, verbose: bool) -> list[str]:

        def predicate(p: Position) -> str:
            return self.filename(p)

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
                i_path = self.filename(p)
                # #1398.
                i_path = c.expand_path_expression(i_path)
                n_path = c.getNodePath(c.p)  # node path
                i_path = g.finalize_join(n_path, i_path)
                with open(i_path, 'w', encoding='utf-8', errors='replace') as self.output_file:
                    self.write_root(p)
                    i_paths.append(i_path)
            except IOError:
                g.es_print(f"Can not open {i_path!r}")
            except Exception:
                g.es_print(f"Unexpected exception opening {i_path!r}")
                g.es_exception()
        # Convert each file to html.
        o_paths = []
        for i_path in i_paths:
            o_path = self.compute_opath(i_path)
            o_paths.append(o_path)
            if kind == 'adoc':
                self.run_asciidoctor(i_path, o_path)
            elif kind == 'pandoc':
                self.run_pandoc(i_path, o_path)
            elif kind == 'sphinx':
                self.run_sphinx(i_path, o_path)
            else:
                g.trace('BAD KIND')
                return None
            if kind != 'sphinx':
                print(f"{kind}: wrote {o_path}")
        if preview:
            if kind == 'sphinx':
                g.es_print('preview not available for sphinx')
            else:
                # open .html files in the default browser.
                g.execute_shell_commands(o_paths)
        t2 = time.time()
        if verbose:
            n = len(i_paths)
            g.es_print(
                f"{kind}: wrote {n} file{g.plural(n)} "
                f"in {(t2-t1):4.2f} sec.")
        return i_paths
    #@+node:ekr.20190515084219.1: *4* markup.filename
    adoc_pattern = re.compile(r'^@(adoc|asciidoctor)')

    def filename(self, p: Position) -> Optional[str]:
        """Return the filename of the @adoc, @pandoc or @sphinx node, or None."""
        kind = self.kind
        h = p.h.rstrip()
        if kind == 'adoc':
            m = self.adoc_pattern.match(h)
            if m:
                prefix = m.group(1)
                return h[1 + len(prefix) :].strip()
            return None
        if kind in ('pandoc', 'sphinx'):
            prefix = f"@{kind}"
            if g.match_word(h, 0, prefix):
                return h[len(prefix) :].strip()
            return None
        g.trace('BAD KIND', kind)
        return None
    #@+node:ekr.20191007053522.1: *4* markup.compute_opath
    def compute_opath(self, i_path: str) -> str:
        """
        Neither asciidoctor nor pandoc handles extra extentions well.
        """
        c = self.c
        for _i in range(3):
            i_path, ext = os.path.splitext(i_path)
            if not ext:
                break
        # #1373.
        base_dir = os.path.dirname(c.fileName())
        return g.finalize_join(base_dir, i_path + '.html')
    #@+node:ekr.20191007043110.1: *4* markup.run_asciidoctor
    def run_asciidoctor(self, i_path: str, o_path: str) -> None:
        """
        Process the input file given by i_path with asciidoctor or asciidoc3.
        """
        global asciidoctor_exec, asciidoc3_exec
        assert asciidoctor_exec or asciidoc3_exec, g.callers()
        # Call the external program to write the output file.
        # The -e option deletes css.
        prog = 'asciidoctor' if asciidoctor_exec else 'asciidoc3'
        command = f"{prog} {i_path} -o {o_path} -b html5"
        g.execute_shell_commands(command)
    #@+node:ekr.20191007043043.1: *4* markup.run_pandoc
    def run_pandoc(self, i_path: str, o_path: str) -> None:
        """
         Process the input file given by i_path with pandoc.
        """
        global pandoc_exec
        assert pandoc_exec, g.callers()
        # Call pandoc to write the output file.
        # --quiet does no harm.
        command = f"pandoc {i_path} -t html5 -o {o_path}"
        g.execute_shell_commands(command)
    #@+node:ekr.20191017165427.1: *4* markup.run_sphinx
    def run_sphinx(self, i_path: str, o_path: str) -> None:
        """Process i_path and o_path with sphinx."""
        trace = True
        # cd to the command directory, or i_path's directory.
        command_dir = g.finalize(self.sphinx_command_dir or os.path.dirname(i_path))
        if os.path.exists(command_dir):
            if trace:
                g.trace(f"\nos.chdir: {command_dir!r}")
            os.chdir(command_dir)
        else:
            g.error(f"command directory not found: {command_dir!r}")
            return
        #
        # If a default command exists, just call it.
        # The user is responsible for making everything work.
        if self.sphinx_default_command:
            if trace:
                g.trace(f"\ncommand: {self.sphinx_default_command!r}\n")
            g.execute_shell_commands(self.sphinx_default_command)
            return
        # Compute the input directory.
        input_dir = g.finalize(
            self.sphinx_input_dir or os.path.dirname(i_path))
        if not os.path.exists(input_dir):
            g.error(f"input directory not found: {input_dir!r}")
            return
        # Compute the output directory.
        output_dir = g.finalize(self.sphinx_output_dir or os.path.dirname(o_path))
        if not os.path.exists(output_dir):
            g.error(f"output directory not found: {output_dir!r}")
            return
        #
        # Call sphinx-build to write the output file.
        # sphinx-build [OPTIONS] SOURCEDIR OUTPUTDIR [FILENAMES...]
        command = f"sphinx-build {input_dir} {output_dir} {i_path}"
        if trace:
            g.trace(f"\ncommand: {command!r}\n")
        g.execute_shell_commands(command)
    #@+node:ekr.20190515070742.24: *3* markup.write_root & helpers
    def write_root(self, root: Position) -> None:
        """Process all nodes in an @adoc tree to self.output_file"""
        # Write only the body of the root.
        self.write_body(root)
        # Write all nodes of the tree, except ignored nodes.
        self.level_offset = self.compute_level_offset(root)
        self.root_level = root.level()
        p = root.threadNext()  # Returns a copy.
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
    #@+node:ekr.20190515114836.1: *4* markup.compute_level_offset
    adoc_title_pat = re.compile(r'^= ')
    pandoc_title_pat = re.compile(r'^= ')

    def compute_level_offset(self, root: Position) -> int:
        """
        Return 1 if the root.b contains a title.  Otherwise 0.
        """
        pattern = self.adoc_title_pat if self.kind == 'adoc' else self.pandoc_title_pat
        for line in g.splitLines(root.b):
            if pattern.match(line):
                return 1
        return 0
    #@+node:ekr.20190515070742.38: *4* markup.write_body
    def write_body(self, p: Position) -> None:
        """Write p.b"""
        # We no longer add newlines to the start of nodes because
        # we write a blank line after all sections.
        s = self.remove_directives(p.b)
        self.output_file.write(g.ensureTrailingNewlines(s, 2))
    #@+node:ekr.20190515070742.47: *4* markup.write_headline
    def write_headline(self, p: Position) -> None:
        """Generate an AsciiDoctor section"""
        if not p.h.strip():
            return
        level = max(0, self.level_offset + p.level() - self.root_level)
        if self.kind == 'sphinx':
            # For now, assume rST markup!
            # Hard coded characters. Never use '#' underlining.
            chars = '''=+*^~"'`-:><_'''
            if len(chars) > level:
                ch = chars[level]
                line = ch * len(p.h)
                self.output_file.write(f"{p.h}\n{line}\n\n")
            return
        if self.kind == 'pandoc':
            section = '#' * min(level, 6)
        elif self.kind == 'adoc':
            # level 0 (a single #) should be done by hand.
            section = '=' * level
        else:
            g.es_print(f"bad kind: {self.kind!r}")
            return
        self.output_file.write(f"{section} {p.h}\n")
    #@+node:ekr.20191007054942.1: *4* markup.remove_directives
    def remove_directives(self, s: str) -> str:
        lines = g.splitLines(s)
        result = []
        for s in lines:
            if s.startswith('@'):
                i = g.skip_id(s, 1)
                word = s[1:i]
                if word in g.globalDirectiveList:
                    continue
            result.append(s)
        return ''.join(result)
    #@+node:ekr.20191006155051.1: *3* markup.commands
    def adoc_command(self, event: Event = None, preview: bool = False, verbose: bool = True) -> File_List:
        global asciidoctor_exec, asciidoc3_exec
        if asciidoctor_exec or asciidoc3_exec:
            return self.command_helper(
                event, kind='adoc', preview=preview, verbose=verbose)
        name = 'adoc-with-preview' if preview else 'adoc'
        g.es_print(f"{name} requires either asciidoctor or asciidoc3")
        return []

    def pandoc_command(self, event: Event = None, preview: bool = False, verbose: bool = True) -> File_List:
        global pandoc_exec
        if pandoc_exec:
            return self.command_helper(
                event, kind='pandoc', preview=preview, verbose=verbose)
        name = 'pandoc-with-preview' if preview else 'pandoc'
        g.es_print(f"{name} requires pandoc")
        return []

    def sphinx_command(self, event: Event = None, preview: bool = False, verbose: bool = True) -> File_List:
        global sphinx_build
        if sphinx_build:
            return self.command_helper(
                event, kind='sphinx', preview=preview, verbose=verbose)
        name = 'sphinx-with-preview' if preview else 'sphinx'
        g.es_print(f"{name} requires sphinx")
        return []
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
