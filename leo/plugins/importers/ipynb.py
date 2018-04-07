#@+leo-ver=5-thin
#@+node:ekr.20160412101008.1: * @file importers/ipynb.py
'''The @auto importer for Jupyter (.ipynb) files.'''
# import json
import re
import leo.core.leoGlobals as g
new = True # True: New code
try:
    import nbformat
except ImportError:
    g.es_print('import-jupyter-notebook requires nbformat package')
    nbformat = None
#@+others
#@+node:ekr.20160412101537.2: ** class Import_IPYNB
class Import_IPYNB(object):
    '''A class to import .ipynb files.'''

    #@+others
    #@+node:ekr.20160412101537.3: *3* ipynb.ctor
    def __init__(self, c=None, importCommands=None, **kwargs):
        '''Ctor for Import_IPYNB class.'''
        self.c = importCommands.c if importCommands else c
            # Commander of present outline.
        # g.trace('(Import_IPYNB)', self.c)
        self.cell = None
            # The present cell node.
        self.cell_n = None
            # The number of the top-level node being scanned.
        self.code_language = None
            # The language in effect for code cells.
        self.cell_type = None
            # The pre-computed cell type of the node.
        self.in_data = False
            # True if in range of any dict.
        self.parent = None
            # The parent for the next created node.
        self.re_header = re.compile(r'^.*<[hH]([123456])>(.*)</[hH]([123456])>')
            # A regex matching html headers.
        self.root = None
            # The root of the to-be-created outline.
    #@+node:ekr.20180407182138.1: *3* ipynb.Entries
    #@+node:ekr.20160412101537.14: *4* ipynb.import_file: (entry) & helpers
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
        # 1. Do everything except cells.
        self.do_prefix(d)
        self.code_language = self.get_code_language(d)
        # 2. Do all cells.
        ### cells = d.get('cells', [])
        for n, cell in enumerate(self.cells):
            self.do_cell(cell, n)
        self.indent_cells()
        c.selectPosition(self.root)
        c.redraw()
    #@+node:ekr.20160412101537.12: *5* ipynb.do_cell & helpers
    def do_cell(self, cell, n):

        trace = True and not g.unitTesting
        self.cell_n = n
        if self.is_empty_code(cell):
            if trace: g.trace('skipping empty cell', n)
            return
        # Careful: don't use self.new_node here.
        self.parent = self.cell = self.root.insertAsLastChild()
        self.parent.h = 'cell %s' % (n + 1)
        # Pre-compute the cell_type.
        self.cell_type = cell.get('cell_type')
        if trace:
            print('')
            g.trace('=====', self.cell_n, self.cell_type)
        if new:
            for key in ('markdown', 'source', 'text'):
                val = cell.get(key)
                if val is not None:
                    self.do_source(key, val)
                    del cell[key]
            if cell:
                self.set_ua(self.parent, 'cell', cell)
        else:
            for key in sorted(cell):
                val = cell.get(key)
                self.do_any(key, val)
        if trace:
            print('-----')
    #@+node:ekr.20160412101537.9: *6* ipynb.do_source & helpers
    def do_source(self, key, val):
        '''Set the cell's body text, or create a 'source' node.'''
        assert key == 'source', (key, val)
        is_cell = self.parent == self.cell
        if is_cell:
            # Set the body's text, splitting markdown nodes as needed.
            if self.cell_type == 'markdown':
                self.do_markdown_cell(self.cell, val)
            elif self.cell_type == 'raw':
                self.cell.b = '@nocolor\n\n' + val
            else:
                ### Is this correct???
                self.cell.b = '@language python\n\n' + val
        else:
            # Do create a new node.
            p = self.new_node('# list:%s' % key)
            p.b = val
    #@+node:ekr.20160412101537.10: *7* ipynb.check_header
    def check_header(self, m):
        '''Return (n, name) or (None, None) on error.'''
        val = (None, None)
        if m:
            n1, name, n2 = m.group(1), m.group(2), m.group(3)
            try:
                if int(n1) == int(n2):
                    val = int(n1), name
            except Exception:
                pass
            if val == (None, None):
                g.trace('malformed header:', m.group(0))
        return val
    #@+node:ekr.20160412101537.11: *7* ipynb.do_markdown_cell
    def do_markdown_cell(self, p, s):
        '''Split the markdown cell p if it contains one or more html headers.'''
        trace = False and not g.unitTesting
        SPLIT = False
            # Perhaps this should be a user option,
            # but splitting adds signifincant whitespace.
            # The user can always split nodes manually if desired.
        i0, last = 0, p.copy()
        if not s.strip():
            return
        lines = g.splitLines(s)
        if SPLIT:
            for i, s in enumerate(lines):
                m = self.re_header.search(s)
                n, name = self.check_header(m)
                if n is None: continue
                h = '<h%s> %s </h%s>' % (n, name.strip(), n)
                prefix = ''.join(lines[i0: i])
                suffix = ''.join(lines[i+1:]) # i+1: skip the heading.
                if trace: g.trace('%2s %2s %s' % (i-i0, len(lines)-i, h))
                if prefix.strip():
                    p2 = last.insertAfter()
                    p2.h = h
                    p2.b = suffix
                    last.b = '@language md\n\n' + prefix
                    last = p2
                    i0 = i
                else:
                    last.h = h
                    last.b = '@language md\n\n' + suffix
        else:
            for i, s in enumerate(lines):
                m = self.re_header.search(s)
                n, name = self.check_header(m)
                if n is not None:
                    h = '<h%s> %s </h%s>' % (n, name.strip(), n)
                    p.h = h
                    break
            p.b = '@language md\n\n' + ''.join(lines)
    #@+node:ekr.20160412101537.23: *7* ipynb.new_node
    def new_node(self, h):

        parent = self.parent or self.root
        p = parent.insertAsLastChild()
        p.h = h
        return p
    #@+node:ekr.20160412101537.22: *6* ipynb.is_empty_code
    def is_empty_code(self, cell):
        '''Return True if cell is an empty code cell.'''
        if cell.get('cell_type') == 'code':
            source = cell.get('source','')
            metadata = cell.get('metadata')
            keys = sorted(metadata.keys())
            if 'collapsed' in metadata:
                keys.remove('collapsed')
            outputs = cell.get('outputs')
            # g.trace(len(source), self.parent.h, sorted(cell))
            return not source and not keys and not outputs
        return False
    #@+node:ekr.20160412101537.13: *5* ipynb.do_prefix
    def do_prefix(self, d):
        '''
        Handle the top-level non-cell data:
        metadata (dict)
        nbformat (int)
        nbformat_minor (int)
        '''
        if not d:
            return
        self.cells = d.get('cells',[])
        if new:
            if self.cells:
                del d['cells']
            self.set_ua(self.root, 'prefix', d)
        else:
            self.parent = self.new_node('# {prefix}')
            for key in sorted(d):
                if key != 'cells':
                    val = d.get(key)
                    self.do_any(key, val)
    #@+node:ekr.20160412101537.19: *5* ipynb.get_code_language
    def get_code_language(self, d):
        '''Return the language specified by the top-level metadata.'''
        name = None
        m = d.get('metadata')
        if m:
            info = m.get('language_info')
            if info:
                name = info.get('name')
        return name
    #@+node:ekr.20160412101537.15: *5* ipynb.indent_cells & helper
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
            m = self.re_header.search(p.h)
            n, name = self.check_header(m)
            if n is None: n = 1
            assert p.level() == root_level + 1, (p.level(), p.h)
            # g.trace('n', n, 'stack', len(stack), p.h)
            stack = self.move_node(n, p, stack)
            p.moveToNodeAfterTree()
            # g.trace('=====', p and p.h)
    #@+node:ekr.20160412101537.16: *6* ipynb.move_node
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
        # g.trace('   n', n, 'stack', len(stack), p.h)
        return stack
    #@+node:ekr.20160412101537.24: *5* ipynb.parse
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
    #@+node:ekr.20180407180754.1: *3* ipynb.To be deleted
    if not new:
        #@+others
        #@+node:ekr.20160412101537.4: *4* ipynb.do_any & helpers
        def do_any(self, key, val):
            trace = True and not g.unitTesting
            if trace:
                if key in ('markdown', 'source', 'text'):
                    g.trace(key, val.__class__.__name__)
                else:
                    g.trace(key, val)
            if key == 'source':
                self.do_source(key, val)
            elif g.isString(val):
                self.do_string(key, val)
            elif isinstance(val, (list, tuple)):
                self.do_list(key, val)
            elif self.is_dict(val):
                self.do_dict(key, val)
            else:
                # Can be ints, None, etc.
                self.do_other(key, val)
        #@+node:ekr.20160412101537.5: *5* ipynb.do_dict
        def do_dict(self, key, d):

            assert self.is_dict(d), d.__class__.__name__
            keys = list(d.keys())
            is_cell = self.parent == self.cell
            if key == 'metadata' and is_cell:
                if 'collapsed' in keys:
                    if d.get('collapsed') in (False, 'false'):
                        self.cell.expand()
                    keys.remove('collapsed')
                if 'leo_headline' in keys:
                    h = d.get('leo_headline')
                    if h:
                        self.cell.h = h
                    keys.remove('leo_headline')
            # g.trace(key, is_cell, keys)
            if is_cell and key == 'metadata' and not keys:
                return # experimental
            old_parent = self.parent
            self.parent = self.new_node('# dict:%s' % key)
            old_in_dict = self.in_data
            self.in_data = key == 'data'
            for key2 in sorted(keys):
                val2 = d.get(key2)
                self.do_any(key2, val2)
            self.in_data = old_in_dict
            self.parent = old_parent
        #@+node:ekr.20160412101537.6: *5* ipynb.do_other
        def do_other(self, key, val):

            if key == 'execution_count' and val is None:
                pass # The exporter will create the proper value.
            else:
                name = 'null' if val is None else val.__class__.__name__
                p = self.new_node('# %s:%s' % (name, key))
                if val is None:
                    p.b = '' # Exporter will translate to 'null'
                else:
                    p.b = repr(val)
        #@+node:ekr.20160412101537.7: *5* ipynb.do_string (test-jup-import)
        def do_string(self, key, val):

            assert g.isString(val)
            is_cell = self.parent == self.cell
            if is_cell and key == 'cell_type':
                # Do *not* create a cell_type child.
                pass
            else:
                # Do create all other nodes.
                if self.in_data or len(g.splitLines(val.strip())) > 1:
                    key = 'list:' + key
                else:
                    key = 'str:' + key
                p = self.new_node('# ' + key)
                if key.startswith('list:'):
                    if key.endswith('html'):
                        val = '@language html\n\n' + val
                    elif key.endswith('xml'):
                        val = '@language html\n\n' + val
                    else:
                        val = '@nocolor-node\n\n' + val
                # g.trace(key, g.splitLines(val)[:5])
                p.b = val
        #@+node:ekr.20160412101537.8: *5* ipynb.do_list
        def do_list(self, key, aList):

            assert isinstance(aList, (list, tuple)), aList.__class__.__name__
            is_cell = self.parent == self.cell
            if is_cell and not aList:
                return # Experimental.
            old_parent = self.parent
            self.parent = self.new_node('# list:%s' % key)
            for z in aList:
                if self.is_dict(z):
                    for key in sorted(z):
                        val = z.get(key)
                        self.do_any(key, val)
                else:
                    self.error('unexpected item in list: %r' % z)
            self.parent = old_parent
        #@+node:ekr.20160412101537.18: *4* ipynb.error
        def error(self, s):

            g.es_print('error: %s' % (s), color='red')
        #@+node:ekr.20160412101537.20: *4* ipynb.get_file_name
        def get_file_name(self):
            '''Open a dialog to get a Jupyter (.ipynb) file.'''
            c = self.c
            fn = g.app.gui.runOpenFileDialog(
                c,
                title="Open Jupyter File",
                filetypes=[
                    ("All files", "*"),
                    ("Jupyter files", "*.ipynb"),
                ],
                defaultextension=".ipynb",
            )
            c.bringToFront()
            return fn
        #@+node:ekr.20160412101537.21: *4* ipynb.is_dict
        def is_dict(self, obj):

            return isinstance(obj, (dict, nbformat.NotebookNode))
        #@-others
    #@+node:ekr.20180407175655.1: *3* ipynb.set_ua
    def set_ua(self, p, key, val):
        '''Set the uA with the given key, value in p.'''
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
