#@+leo-ver=5-thin
#@+node:ekr.20160412101901.1: * @file writers/ipynb.py
'''The @auto write code for jupyter (.ipynb) files.'''
import sys
import leo.core.leoGlobals as g
import json
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
        nb = self.make_notebook()
        s = self.convert_notebook(nb)
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
        nb = self.make_notebook()
        s = self.convert_notebook(nb)
        if not s:
            return False
        if g.isUnicode(s):
            s = g.toEncodedString(s, encoding='utf-8', reportErrors=True)
        at.outputFile.write(s)
        return True
    #@+node:ekr.20180407191227.1: *3* ipy_w.convert_notebook
    def convert_notebook(self, nb):
        '''Write the notebook using nbconvert.writes.'''
        try:
            s = json.dumps(nb,
                sort_keys=True,
                indent=4, separators=(',', ': '),
            )
            return s
        except Exception:
            g.es_print('Error writing notebook', color='red')
            g.es_exception()
            return None
    #@+node:ekr.20160412101845.21: *3* ipy_w.default_metadata
    def default_metadata(self):
        '''Return the top-level metadata to use if there is no {prefix} node.'''
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
    #@+node:ekr.20160412101845.24: *3* ipy_w.get_file_name
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
    def get_ua(self, p):

        return p.v.u.get('ipynb')
    #@+node:ekr.20180407191219.1: *3* ipy_w.make_notebook
    def make_notebook(self):
        '''Create a JSON notebook'''
        root = self.root
        prefix = self.get_ua(root)
        if prefix: prefix = prefix.get('prefix')
        if not prefix:
            prefix = self.default_metadata
        nb = prefix
        nb ['cells'] = [self.put_body(p) for p in root.subtree()]
        return nb
    #@+node:ekr.20180407195341.1: *3* ipy_w.put_body
    def put_body(self, p):
        '''Put the body text of p, as an element of dict d.'''
        trace = False and not g.unitTesting
        ### Should depend @language directives, but ok for testing.
        cell = self.get_ua(p)
        cell = cell.get('cell') if cell else {}
        cell = cell or {}
        if trace:
            g.trace(p.h)
            g.printObj(cell)
        cell ['source'] = g.splitLines(p.b)
            # Must be a list.
        return cell

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
