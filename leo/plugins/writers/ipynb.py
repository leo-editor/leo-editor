#@+leo-ver=5-thin
#@+node:ekr.20160412101901.1: * @file writers/ipynb.py
'''The @auto write code for jupyter (.ipynb) files.'''
import re
import sys
import leo.core.leoGlobals as g
if g.isPython3:
    # pylint: disable=relative-import
        # an unhelpful warning.
    import json # This fails in python 2. It yields writers.json
else:
    json = g.importModule('json')
# print('writers/ipynb.py: json: %s' % json)
#@+others
#@+node:ekr.20160412101845.2: ** class Export_IPYNB
class Export_IPYNB(object):
    '''A class to export outlines to .ipynb files.'''
    
    def __init__(self, c):
        '''Ctor for Import_IPYNB class.'''
        self.c = c
            # Commander of present outline.
        self.root = None
            # The root of the outline.

    #@+others
    #@+node:ekr.20160412114852.1: *3*  ipy_w.Entries
    #@+node:ekr.20160412101845.4: *4* ipy_w.export_outline
    def export_outline(self, root, fn=None):
        '''
        Entry point for export-jupyter-notebook
        Export the given .ipynb file.
        '''
        self.root = root
        if not fn:
            fn = self.get_file_name()
        if not fn:
            return False
        try:
            nb = self.make_notebook()
            s = self.convert_notebook(nb)
        except Exception:
            g.es_exception()
            return False
        if not s:
            return False
        if g.isUnicode(s):
            s = g.toEncodedString(s, encoding='utf-8', reportErrors=True)
        try:
            f = open(fn, 'wb')
            f.write(s)
            f.close()
            g.es_print('wrote: %s' % fn)
        except IOError:
            g.es_print('can not open: %s' % fn)
        return True
    #@+node:ekr.20160412114239.1: *4* ipy_w.write: @auto entry
    def write(self, root):
        '''
        Export_IPYNB: entry point for @auto writes.
        Signature must match signature of BaseWriter.write().
        '''
        at = self.c.atFileCommands
        if not root:
            g.trace('can not happen: no root')
            return False
        if not at and at.outputFile:
            g.trace('can not happen: no at.outputFile')
            return False
        # Write the text to at.outputFile.
        self.root = root
        try:
            nb = self.make_notebook()
            s = self.convert_notebook(nb)
        except Exception:
            g.es_exception()
            return False
        if not s:
            return False
        if g.isUnicode(s):
            s = g.toEncodedString(s, encoding='utf-8', reportErrors=True)
        at.outputFile.write(s)
        return True
    #@+node:ekr.20180409081735.1: *3* ipy_w.cell_type
    def cell_type(self, p):
        '''Return the Jupyter cell type of p.b, honoring ancestor directives.'''
        c = self.c
        language = g.getLanguageAtPosition(c, p)
        return 'code' if language == 'python' else 'markdown'
    #@+node:ekr.20180410045324.1: *3* ipy_w.clean_headline
    def clean_headline(self, s):
        '''
        Return a cleaned version of a headline.
        
        Used to clean section names and the [ ] part of markdown links.
        '''
        aList = [ch for ch in s if ch in '-: ' or ch.isalnum()]
        return ''.join(aList).rstrip('-').strip()
    #@+node:ekr.20180407191227.1: *3* ipy_w.convert_notebook
    def convert_notebook(self, nb):
        '''Convert the notebook to a string.'''
        # Do *not* catch exceptions here.
        s = json.dumps(nb,
            sort_keys=True,
            indent=4, separators=(',', ': '))
        return g.toUnicode(s)
    #@+node:ekr.20160412101845.21: *3* ipy_w.default_metadata
    def default_metadata(self):
        '''Return the default top-level metadata.'''
        n1, n2 = sys.version_info[0], sys.version_info[1]
        version = n1
        long_version = '%s.%s' % (n1, n2)
        return {
            "metadata": {
                "kernelspec": {
                    "display_name": "Python %s" % version,
                    "language": "python",
                    "name": "python%s" % version,
                 },
                 "language_info": {
                    "codemirror_mode": {
                        "name": "ipython",
                        "version": version,
                    },
                  "file_extension": ".py",
                  "mimetype": "text/x-python",
                  "name": "python",
                  "nbconvert_exporter": "python",
                  "pygments_lexer": "ipython3",
                  "version": long_version,
                 }
            },
            "nbformat": 4,
            "nbformat_minor": 0
        }
    #@+node:ekr.20180408103729.1: *3* ipy_w.get_file_name
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
    #@+node:ekr.20180407193222.1: *3* ipy_w.get_ua
    def get_ua(self, p, key=None):
        '''Return the ipynb uA. If key is given, return the inner dict.'''
        d = p.v.u.get('ipynb')
        if not d:
            return {}
        else:
            return d.get(key) if key else d
    #@+node:ekr.20180407191219.1: *3* ipy_w.make_notebook
    def make_notebook(self):
        '''Create a JSON notebook'''
        root = self.root
        nb = self.get_ua(root, key='prefix') or self.default_metadata
        # Write the expansion status of the root.
        meta = nb.get('metadata') or {}
        meta ['collapsed'] = not root.isExpanded()
        # g.trace(meta.get('collapsed'), root.h)
        nb ['metadata'] = meta
        # Put all the cells.
        nb ['cells'] = [self.put_body(p) for p in root.subtree()]
        return nb
    #@+node:ekr.20180407195341.1: *3* ipy_w.put_body & helpers
    def put_body(self, p):
        '''Put the body text of p, as an element of dict d.'''
        cell = self.get_ua(p, 'cell') or {}
        meta = cell.get('metadata') or {}
        self.update_cell_properties(cell, meta, p)
        self.update_cell_body(cell, meta, p)
        # g.printObj(meta, tag='metadata')
        # g.printObj(cell, tag='cell')
        return cell
    #@+node:ekr.20180409120613.1: *4* ipy_w.update_cell_body
    pat1 = re.compile(r'^.*<[hH]([123456])>(.*)</[hH]([123456])>')
    pat2 = re.compile(r'^\s*([#]+)')

    def update_cell_body(self, cell, meta, p):
        '''Create a new body text, depending on kind.'''
        
        def clean(lines):
            lines = [z for z in lines if not g.isDirective(z)]
            s = ''.join(lines).strip() + '\n'
            return g.splitLines(s)
            
        kind = self.cell_type(p)
        lines = g.splitLines(p.b)
        level = p.level() - self.root.level()
        if kind == 'markdown':
            # Remove all header markup lines.
            lines = [z for z in lines if
                not self.pat1.match(z) and not self.pat2.match(z)]
            lines = clean(lines)
            # Insert a new header markup line.
            if level > 0:
                lines.insert(0, '%s %s\n' % ('#'*level, self.clean_headline(p.h)))
        else:
            # Remember the level for the importer.
            meta ['leo_level'] = level
            lines = clean(lines)
            # Remove leading whitespace lines inserted during import.
        cell ['source'] = lines
    #@+node:ekr.20180409120454.1: *4* ipy_w.update_cell_properties
    def update_cell_properties(self, cell, meta, p):
        '''Update cell properties.'''
        # Update the metadata.
        meta ['leo_headline'] = p.h
        meta ['collapsed'] = not p.isExpanded()
        # "cell_type" should not be in the metadata.
        if meta.get('cell_type'):
            del meta ['cell_type']
        cell ['metadata'] = meta
        # Update required properties.
        cell ['cell_type'] = kind = self.cell_type(p)
        if kind == 'code':
            if cell.get('outputs') is None:
                cell ['outputs'] = []
            if cell.get('execution_count') is None:
                cell ['execution_count'] = 0
        else:
            # These properties are invalid!
            for prop in ('execution_count', 'outputs'):
                if cell.get(prop) is not None:
                    del cell [prop]
        return kind
       
    #@-others
#@-others
writer_dict = {
    '@auto': ['@auto-jupyter','@auto-ipynb',],
    'class': Export_IPYNB,
    'extensions': ['.ipynb',],
}
#@@language python
#@@tabwidth -4
#@-leo
