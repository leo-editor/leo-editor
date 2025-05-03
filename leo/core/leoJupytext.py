#@+leo-ver=5-thin
#@+node:ekr.20241022090855.1: * @file leoJupytext.py
"""
Support for pairing .ipynb and .py files with jupytext.

https://github.com/mwouts/jupytext
"""

#@+<< leoJupytext: imports and annotations >>
#@+node:ekr.20241022093347.1: ** << leoJupytext: imports and annotations >>
from __future__ import annotations
import io
import os
import textwrap
from typing import Any, Tuple, TYPE_CHECKING

try:
    import jupytext  # pylint: disable=unused-import
    has_jupytext = True
except Exception:
    has_jupytext = False

from leo.core import leoGlobals as g

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position
    Notebook = Any  # nbformat.notebooknode.NotebookNode
#@-<< leoJupytext: imports and annotations >>

#@+others
#@+node:ekr.20241022093215.1: ** class JupytextManager
class JupytextManager:

    #@+others
    #@+node:ekr.20241029065713.1: *3* jtm.create_outline & helpers
    def create_outline(self, c: Cmdr, root: Position) -> None:
        """
        Scan root.b, creating child nodes and
        replacing root.b by standard Leo markup.
        """
        if root.hasChildren():
            g.es_print(f"{root.h!r} has children", color='blue')
            g.es_print('Adding an empty child preserves raw text')
            return
        contents = root.b
        # Recover from a read exception in jupytext.read.
        if contents.strip().startswith('{'):
            g.es_print('Using raw contents', color='blue')
            return
        # Make the header if it exists.
        i = self.make_prefix(0, contents, root)
        header = contents[0:i]
        # Make all other cells.
        while i < len(contents):
            progress = i
            i = self.make_cell(c, i, contents, root)
            assert i > progress
        # Replace root.b by the computed markup.
        root.b = self.compute_markup(header)
        c.redraw()
    #@+node:ekr.20241029153032.1: *4* jtm.compute_headline
    def compute_headline(self, c: Cmdr, cell: str, p: Position) -> str:
        """Return the headline given the contents of a cell."""

        width = c.config.getInt('jupytext-max-headline-length') or 60

        def shorten(s: str) -> str:
            """Shorten s to the configured width"""
            return textwrap.shorten(s, width=width, placeholder='')

        lines = g.splitLines(cell)

        # Handle markdown sections.
        if len(lines) > 1 and '[markdown]' in lines[0]:
            line1 = lines[1].strip()
            if line1.startswith('# '):
                section = line1[2:].strip()
                if section.startswith('#'):
                    return shorten(section)
            return shorten(line1)

        # Filter blank lines.
        stripped_lines = [z.strip() for z in lines[1:] if z.strip()]
        if not stripped_lines:
            return f"Cell {p.childIndex()}"

        # Now we'll return the first line, possibly shortened.
        line1 = stripped_lines[0]

        # Case 1: the first line is a non-trivial comment.
        if line1.startswith('#'):
            comment = line1[1:].strip()
            if comment:
                return shorten(comment)

        # Case 2: The first line contains a non-trivial comment.
        i = line1.find('#')
        if i > -1:
            comment = line1[i + 1 :].strip()
            if comment:
                return shorten(comment)

        # Case 3: Return the entire shortened python line.
        return shorten(line1)
    #@+node:ekr.20241029160441.1: *4* jtm.compute_markup
    def compute_markup(self, header: str) -> str:
        """Return the proper markup for root.b"""
        markup_list = [
            '@others\n',
            '@language jupytext\n',
            '@tabwidth -4\n',
        ]
        if header:
            markup_list.insert(0, g.angleBrackets(' prefix ') + '\n')
        return ''.join(markup_list)
    #@+node:ekr.20241029152029.1: *4* jtm.make_cell
    def make_cell(self, c: Cmdr, i: int, contents: str, root: Position) -> int:
        """
        Scan for a cell starting at contents[i].
        If found, create a new node as the last child of the root.
        Return the index of the line following the cell.
        """
        cell_marker = '# %%'  # The start of all cells.
        i = contents.find(cell_marker, i)
        if i == -1:
            return len(contents)
        j = contents.find(cell_marker, i + len(cell_marker) + 1)
        if j == -1:
            j = len(contents)
        cell = contents[i:j]
        child = root.insertAsLastChild()
        child.b = cell
        child.h = self.compute_headline(c, cell, child)
        return j
    #@+node:ekr.20241029155214.1: *4* jtm.make_prefix
    def make_prefix(self, i: int, contents: str, root: Position) -> int:
        """
        Create a child node for the header.
        Return index after the prefix, or i if there is no prefix.
        """
        prefix_marker = '# ---\n'  # The start of all prefixes.
        start = contents.find(prefix_marker)
        if start == -1:
            return i
        end = contents.find(prefix_marker, start + len(prefix_marker)) + len(prefix_marker)
        if end == -1:
            return i
        p = root.insertAsLastChild()
        p.h = g.angleBrackets(' prefix ')
        # The prefix starts at 0, not start.
        p.b = contents[0:end]
        return end
    #@+node:ekr.20241023162459.1: *3* jtm.dump_notebook
    def dump_notebook(self, nb: Notebook) -> None:
        """Dump a notebook (class nbformat.notebooknode.NotebookNode)"""
        g.trace(g.callers())
        # keys are 'cells', 'metadata', 'nbformat', 'nbformat_minor'.
        if 0:
            for z in nb:
                print(f"{z:>20} {nb[z]}")
        if 1:
            print('metadata...')
            d = nb['metadata']
            for z in d:
                print(f"{z}: {g.objToString(d[z])}")
        if 1:
            print('')
            print('cells...')
            for i, cell in enumerate(nb['cells']):
                print(f"cell {i}: {g.objToString(cell)}")
    #@+node:ekr.20241023152818.1: *3* jtm.full_path
    def full_path(self, c: Cmdr, p: Position) -> str:
        """
        Return the full path in effect for the `@jupytext x.ipynb` node at p.
        
        On errors, print an error message and return ''.
        """
        if not has_jupytext:
            self.warn_no_jupytext()
            return ''
        if not p.h.startswith('@jupytext'):
            g.trace(f"Can not happen: not an @jupytext node: {p.h!r}")
            return ''
        full_path = c.fullPath(p)
        return full_path
    #@+node:ekr.20241024160108.1: *3* jtm.get_jupytext_config_file
    def get_jupytext_config_file(self) -> str:
        """
        Print the name and contents of the jupytext config file in effect.
        Call this method with this Leonine script:
        
            g.app.jupytextManager.get_jupytext_config_file()
        """
        from jupytext.config import find_jupytext_configuration_file
        import tomllib
        config_file = find_jupytext_configuration_file(os.getcwd())
        if config_file:
            with open(config_file, 'rb') as f:
                data = tomllib.load(f)
                g.printObj(data, tag=f"jupytext: contents of {config_file!r}")
        return config_file
    #@+node:ekr.20241023155136.1: *3* jtm.read
    def read(self, c: Cmdr, p: Position) -> Tuple[str, str]:  # pragma: no cover
        """
        Called from at.readOneAtJupytextNode.
        p must be an @jupytext node describing an .ipynb file.
        Convert x.ipynb to a string s.
        Return (s, path)
        """
        path = self.full_path(c, p)
        if not path:
            # full_path has given the error.
            return '', ''
        if not os.path.exists(path):
            message = f"\njtm.read: File not found: {path!r}\n"
            g.es_print_unique_message(message)
            return '', ''

        # Read the .ipynb file into contents.
        # jupytext.read can crash, so be safe.
        fmt = c.config.getString('jupytext-fmt') or 'py:percent'
        try:
            notebook = jupytext.read(path, fmt=fmt)
            with io.StringIO() as f:
            # Use jupytext.write, *not* jupytext.writes.
                jupytext.write(notebook, f, fmt=fmt)
                contents = f.getvalue()
        except Exception:
            g.es_print('Exception in jupytext!', color='red')
            g.es_exception()
            with open(path, 'rb') as f:
                raw_contents = f.read()
                contents = g.toUnicode(raw_contents)
        return contents, path
    #@+node:ekr.20241023073354.1: *3* jtm.update
    def update(self, c: Cmdr, p: Position, path: str) -> None:
        """
        Update the @jupytext node at p when the path has changed externally.
        """
        at = c.atFileCommands
        at.readOneAtJupytextNode(p)
        c.redraw()
    #@+node:ekr.20241023161034.1: *3* jtm.warn_no_jupytext
    warning_given = False

    def warn_no_jupytext(self) -> None:
        """Warn (once) that jupytext is not available"""
        if not self.warning_given:
            self.warning_given = True
            print('')
            g.es_print('can not import `jupytext`', color='red')
            g.es_print('`pip install jupytext`', color='blue')
            print('')
    #@+node:ekr.20241023155519.1: *3* jtm.write
    def write(self, c: Cmdr, p: Position, contents: str) -> None:
        """
        - Check that p is an @jupytext node.
        - Write the .ipynb file corresponding to p.b
        """
        path = self.full_path(c, p)
        if not path:
            # full_path has given the error.
            return

        # Write the .ipynb file.
        # Write the paired .py file, only if fmt specifies pairing.
        # See https://jupytext.readthedocs.io/en/latest/config.html
        fmt = c.config.getString('jupytext-fmt') or 'py:percent'
        notebook = jupytext.reads(contents, fmt=fmt)
        jupytext.write(notebook, path, fmt=fmt)
    #@-others
#@-others

#@-leo
