#@+leo-ver=5-thin
#@+node:ekr.20160412101008.1: * @file importers/ipynb.py
'''The @auto importer for Jupyter (.ipynb) files.'''
import re
import leo.core.leoGlobals as g
try:
    import nbformat
except ImportError:
    g.es_print('import-jupyter-notebook requires nbformat package')
    nbformat = None
#@+others
#@+node:ekr.20160412101537.2: ** class Import_IPYNB
class Import_IPYNB(object):
    '''A class to import .ipynb files.'''
    
    def __init__(self, c=None, importCommands=None, **kwargs):
        self.c = importCommands.c if importCommands else c
            # Commander of present outline.
        self.cell_n = 0
            # The number of untitled cells.
        self.parent = None
            # The parent for the next created node.
        self.root = None
            # The root of the to-be-created outline.

    #@+others
    #@+node:ekr.20180408112531.1: *3* ipynb.Entries
    #@+node:ekr.20160412101537.14: *4* ipynb.import_file
    def import_file(self, fn, root):
        '''
        Import the given .ipynb file.
        https://nbformat.readthedocs.org/en/latest/format_description.html
        '''
        c = self.c
        self.fn = fn
        self.parent = None
        self.root = root.copy()
        d = self.parse(fn)
        if not d:
            return
        self.do_prefix(d)
        for cell in self.cells:
            self.do_cell(cell)
        self.indent_cells()
        c.selectPosition(self.root)
        c.redraw()
    #@+node:ekr.20160412103110.1: *4* ipynb.run
    def run(self, s, parent, parse_body=False):
        '''
        @auto entry point. Called by code in leoImport.py.
        '''
        c = self.c
        fn = parent.atAutoNodeName()
        if c and fn:
            changed = c.isChanged()
            self.import_file(fn, parent)
            # Similar to Importer.run.
            parent.b = (
                '@nocolor-node\n\n' +
                'Note: This node\'s body text is ignored when writing this file.\n\n' +
                'The @others directive is not required\n'
            )
            for p in parent.self_and_subtree():
                p.clearDirty()
            c.setChanged(changed)
        elif not c or not fn:
            g.trace('can not happen', c, fn)
    #@+node:ekr.20180408112600.1: *3* ipynb.JSON handlers
    #@+node:ekr.20160412101537.12: *4* ipynb.do_cell
    def do_cell(self, cell):

        trace = False and not g.unitTesting
        if self.is_empty_code(cell):
            if trace: g.trace('skipping empty cell')
            return
        self.parent = cell_p = self.root.insertAsLastChild()
        # Expand the node if metadata: collapsed is False
        meta = cell.get('metadata')
        collapsed = meta and meta.get('collapsed')
        h = meta.get('leo_headline')
        if not h:
            self.cell_n += 1
            h = 'cell %s' % self.cell_n
        self.parent.h = h
        if collapsed is not None and not collapsed:
            cell_p.v.expand()
        if trace:
            print('')
            g.trace('=====', self.cell_n, cell.get('cell_type'))
        # Handle the body text.
        for key in ('markdown', 'source', 'text'):
            if key in cell:
                val = cell.get(key)
                if val:
                    self.do_source(cell, cell_p, val)
                del cell[key]
        self.set_ua(self.parent, 'cell', cell)
    #@+node:ekr.20160412101537.13: *4* ipynb.do_prefix
    def do_prefix(self, d):
        '''Handle everything except the 'cells' attribute.'''
        if d:
            # Expand the root if requested.
            if 1: # The @auto logic defeats this, but this is correct.
                meta = d.get('metadata')
                collapsed = meta and meta.get('collapsed')
                if collapsed is not None and not collapsed:
                    self.root.v.expand()
            self.cells = d.get('cells',[])
            if self.cells:
                del d['cells']
            self.set_ua(self.root, 'prefix', d)
    #@+node:ekr.20160412101537.9: *4* ipynb.do_source
    def do_source(self, cell, cell_p, val):
        '''Set the cell's body text.'''
        val = val.strip() + '\n'
        if cell.get('cell_type') == 'markdown':
            cell_p.b = '@language md\n@wrap\n\n%s' % val
        else:
            cell_p.b = '@language python\n\n%s' % val
    #@+node:ekr.20160412101537.22: *4* ipynb.is_empty_code
    def is_empty_code(self, cell):
        '''Return True if cell is an empty code cell.'''
        if cell.get('cell_type') != 'code':
            return False
        metadata = cell.get('metadata')
        outputs = cell.get('outputs')
        source = cell.get('source')
        keys = sorted(metadata.keys())
        if 'collapsed' in metadata:
            keys.remove('collapsed')
        return not source and not keys and not outputs
    #@+node:ekr.20160412101537.24: *4* ipynb.parse
    def parse(self, fn):
        '''Parse the file, which should be JSON format.'''
        if g.os_path_exists(fn):
            with open(fn) as f:
                # payload_source = f.name
                payload = f.read()
            try:
                nb = nbformat.reads(payload, as_version=4)
                    # nbformat.NO_CONVERT: no conversion
                    # as_version=4: Require IPython 4.
                return nb
            except Exception:
                g.es_exception()
                return None
        else:
            g.es_print('not found', fn)
            return None
    #@+node:ekr.20180408112636.1: *3* ipynb.Utils
    #@+node:ekr.20160412101845.24: *4* ipynb.get_file_name
    def get_file_name(self):
        '''Open a dialog to write a Jupyter (.ipynb) file.'''
        c = self.c
        fn = g.app.gui.runSaveFileDialog(
            c,
            defaultextension=".ipynb",
            filetypes=[
                ("Jupyter files", "*.ipynb"),
                ("All files", "*"),
            ],
            initialfile='',
            title="Export To Jupyter File",
        )
        c.bringToFront()
        return fn
    #@+node:ekr.20160412101537.15: *4* ipynb.indent_cells & helper
    re_header = re.compile(r'^.*<[hH]([123456])>(.*)</[hH]([123456])>')

    def indent_cells(self):
        '''
        Indent md nodes in self.root.children().
        <h1> nodes and non-md nodes stay where they are,
        <h2> nodes become children of <h1> nodes, etc.
        '''
        # Careful: links change during this loop.
        p = self.root.firstChild()
        stack = []
        after = self.root.nodeAfterTree()
        root_level = self.root.level()
        while p and p != self.root and p != after:
            # Check the first 5 lines of p.b.
            n = 1
            for s in g.splitLines(p.b)[:5]:
                m = self.re_header.search(s)
                if m:
                    try:
                        n = int(m.group(1))
                        break
                    except ValueError:
                        pass
            assert p.level() == root_level + 1, (p.level(), p.h)
            stack = self.move_node(n, p, stack)
            p.moveToNodeAfterTree()
    #@+node:ekr.20160412101537.16: *4* ipynb.move_node
    def move_node(self, n, p, stack):
        '''Move node to level n'''
        # Cut back the stack so that p will be at level n (if possible).
        if stack:
            stack = stack[:n]
            if len(stack) == n:
                prev = stack.pop()
                p.moveAfter(prev)
            else:
                # p will be under-indented if len(stack) < n-1
                # This depends on user markup, so it can't be helped.
                parent = stack[-1]
                n2 = parent.numberOfChildren()
                p.moveToNthChildOf(parent, n2)
        # Push p *after* moving p.
        stack.append(p.copy())
        return stack
    #@+node:ekr.20180407175655.1: *4* ipynb.set_ua
    def set_ua(self, p, key, val):
        '''Set p.v.u'''
        trace = False and not g.unitTesting
        if trace:
            g.trace(p.h, key)
            g.printObj(val)
        d = p.v.u
        d2 = d.get('ipynb') or {}
        d2 [key] = val
        d ['ipynb'] = d2
        p.v.u = d
    #@-others
#@-others
importer_dict = {
    '@auto': [], # '@auto-jupyter', '@auto-ipynb',],
    'class': Import_IPYNB,
    'extensions': ['.ipynb',],
}
#@@language python
#@@tabwidth -4
#@-leo
