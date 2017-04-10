#@+leo-ver=5-thin
#@+node:ekr.20160412101901.1: * @file writers/ipynb.py
'''The @auto write code for jupyter (.ipynb) files.'''
import re
import sys
import leo.core.leoGlobals as g
#@+others
#@+node:ekr.20160412101845.2: ** class Export_IPYNB
class Export_IPYNB(object):
    '''A class to export outlines to .ipynb files.'''

    #@+others
    #@+node:ekr.20160412101845.3: *3*  ctor
    def __init__(self, c):
        '''Ctor for Import_IPYNB class.'''
        self.c = c
            # Commander of present outline.
        self.at = c.atFileCommands
            # The actual writing is done by @auto write code.
        self.required_cell_keys = ('cell_type', 'metatdata', 'outputs', 'source')
            # Keys that exist for the present cell.
        self.indent = 0
            # The indentation level of generated lines.
        self.lines = []
            # The lines of the output.
        self.root = None
            # The root of the outline.
    #@+node:ekr.20160412114852.1: *3* Entries
    #@+node:ekr.20160412101845.4: *4* export_outline: export-jupyter-notebook entry
    def export_outline(self, root, fn=None):
        '''
        Entry point for export-jupyter-notebook
        Import the given .ipynb file.
        '''
        self.root = root
        self.indent = 0
        self.lines = []
        if not fn:
            fn = self.get_file_name()
        if fn:
            self.put_outline()
            self.lines = self.clean_outline()
            s = '\n'.join(self.lines)
            if g.isUnicode(s):
                s = g.toEncodedString(s, encoding='utf-8', reportErrors=True)
            try:
                f = open(fn, 'wb')
                f.write(s)
                f.close()
                g.es_print('wrote: %s' % fn)
            except IOError:
                g.es_print('can not open: %s' % fn)
    #@+node:ekr.20160412114239.1: *4* write: @auto entry
    def write(self, root):
        '''
        Export_IPYNB: entry point for @auto writes.
        Signature must match signature of BaseWriter.write().
        '''
        at = self.at
        # fn = root.atAutoNodeName()
        if not root:
            g.trace('can not happen: no root')
            return False
        if not at and at.outputFile:
            g.trace('can not happen: no at.outputFile')
            return False
        # Write the text to at.outputFile and return True.
        self.root = root
        self.put_outline()
        self.lines = self.clean_outline()
        s = '\n'.join(self.lines)
        if g.isUnicode(s):
            s = g.toEncodedString(s, encoding='utf-8', reportErrors=True)
        self.at.outputFile.write(s)
        return True
    #@+node:ekr.20160412115016.1: *3* put_*
    #@+node:ekr.20160412101845.5: *4* put, put_key_string & put_key_val
    def put(self, s):

        # End every line with a comma, unless s ends with '[' or '{'.
        # Clean_outline will remove commas as needed.
        if s.endswith('[') or s.endswith('{') or s.endswith(','):
            pass
        else:
            s = s + ','
        line = '%s%s' % (' '*self.indent, s)
        self.lines.append(line)

    def put_key_string(self, key, s):

        self.put('"%s": "%s"' % (key, self.clean(s)))

    def put_key_val(self, key, val, indent=False):

        self.put('"%s": %s' % (key, val))
        if indent:
            self.indent += 1
    #@+node:ekr.20160412101845.6: *4* put_any_non_cell_data
    def put_any_non_cell_data(self, p, exclude=None):

        if self.is_cell(p):
            return # put_cell handles this.
        assert p.h.startswith('#'), p.h
        key = p.h[1:].strip()
        if key == '{prefix}':
            return # put prefix handles this.
        has_children = self.has_data_children(p)
        i = key.find(':')
        if i > -1:
            kind = key[:i+1]
            key = key[i+1:]
        else:
            kind = '???'
            key = '???'
        if key == exclude:
            return # The caller will generate this key.
        if kind == 'list:':
            if has_children:
                # Lists are always lists of dicts.
                self.put_key_val(key, '[', indent=True)
                self.put_indent('{')
                for child in p.children():
                    self.put_any_non_cell_data(child)
                self.put_dedent('}')
                self.put_dedent(']')
            elif p.b.strip():
                self.put_list(key, p.b)
            else:
                self.put_key_val(key, '[],')
        elif kind == 'dict:':
            if p.b.strip():
                self.oops(p, 'ignoring body text')
            if has_children:
                self.put_key_val(key, '{', indent=True)
                if has_children:
                    for child in p.children():
                        self.put_any_non_cell_data(child)
                self.put_dedent('}')
            else:
                # Assume there is a reason for the empty dict.
                self.put_key_val(key, '{}')
        elif kind == 'str:':
            self.put_key_string(key, p.b)
        elif kind == 'null:':
            self.put_key_val(key, 'null')
        else:
            # Unusual case: int, etc.
            self.put_key_val(key, p.b)
    #@+node:ekr.20160412101845.7: *4* put_cell
    def put_cell(self, p):
        '''Put the cell and all it's hidden data.'''
        self.put_indent('{')
        self.put_cell_data(p)
        self.put_dedent('}')
        for child in p.children():
            if self.is_cell(child):
                self.put_cell(child)
    #@+node:ekr.20160412101845.8: *4* put_cell_data & helpers
    def put_cell_data(self, p):
        '''Put all the hidden data for cell p.'''
        if self.is_cell(p):
            type_ = self.put_cell_type(p)
            self.put_metadata(p, type_)
            if type_ != 'markdown':
                self.put_execution_count(p)
                self.put_outputs(p)
            self.put_source(p, type_)
        else:
            for child in p.children():
                self.put_any_non_cell_data(child)
    #@+node:ekr.20160412101845.9: *5* put_cell_type
    def put_cell_type(self, p):
        '''Put the 'cell_type' dict for cell p.'''
        assert self.is_cell(p), p.h
        p_key = self.find_key('cell_type', p)
        if p_key:
            type_ = p_key.b.strip()
        else:
            colorizer = self.c.frame.body.colorizer
            language = colorizer.scanLanguageDirectives(p)
            if language in ('rest', 'markdown', 'md'):
                type_ = 'markdown'
            else:
                type_ = 'code'
        self.put_key_string('cell_type', type_)
        return type_
    #@+node:ekr.20160412101845.10: *5* put_execution_count
    def put_execution_count(self, p):
        '''Put the 'execution_count' for cell p.'''
        assert self.is_cell(p), p.h
        p_key = self.find_key('execution_count', p)
        if p_key and p_key.b.strip():
            count = p_key.b.strip()
        else:
            count = 'null'
        self.put_key_val('execution_count', count)
    #@+node:ekr.20160412101845.11: *5* put_metadata
    def put_metadata(self, p, type_):
        '''Put the 'metadata' dict for cell p.'''
        assert self.is_cell(p), p.h
        self.put_key_val('metadata', '{', indent=True)
        p_key = self.find_key('metadata', p)
        if p_key:
            # Put the existing keys, but not collapsed.
            for child in p_key.children():
                self.put_any_non_cell_data(child, exclude='collapsed')
        if type_ == 'code':
            self.put_key_val('collapsed', 'true' if p.isExpanded() else 'false')
        self.put_key_string('leo_headline', p.h)
            # Remember the headline.
        self.put_dedent('}')
    #@+node:ekr.20160412101845.12: *5* put_outputs
    def put_outputs(self, p):
        '''Return the 'outputs' list for p.'''
        assert self.is_cell(p), p.h
        p_key = self.find_key('outputs', p)
        if p_key and self.has_data_children(p_key):
            # Similar to put_any_non_cell_data.
            self.put_key_val('outputs', '[', indent=True)
            self.put_indent('{')
            for child in p_key.children():
                self.put_any_non_cell_data(child)
            self.put_dedent('}')
            self.put_dedent(']')
        else:
            self.put_key_val('outputs', '[]')
    #@+node:ekr.20160412101845.13: *5* put_source
    header_re = re.compile(r'^<[hH][123456]>')

    def put_source(self, p, type_):
        '''Put the 'source' key for p.'''
        lines = [z for z in g.splitLines(p.b) if not g.isDirective(z)]
        # skip blank lines.
        i = 0
        while i < len(lines) and not lines[i].strip():
            i += 1
        lines = lines[i:]
        # skip trailing lines:
        i = len(lines)-1
        while i > 0 and not lines[i].strip():
            i -= 1
        lines = lines[:i+1]
        has_header = any([self.header_re.search(z) for z in lines])
        if lines and lines[-1].endswith('\n'):
            s_last = lines.pop()
            lines.append(s_last.rstrip())
        s = ''.join(lines)
        # Auto add headlines.
        if type_ == 'markdown' and not has_header:
            if 1: # Just put the headline.
                heading = p.h.strip()+'\n'
            else:
                # Not needed now that the import code sets headlines.
                n = min(6, self.level(p))
                heading = '<h%(level)s>%(headline)s</h%(level)s>\n' % {
                    'level': n,
                    'headline': p.h,
                }
            s = heading + s
            # Not completely accurate, but good for now.
        self.put_list('source', s or '# no code!')
    #@+node:ekr.20160412101845.14: *4* put_indent & put_dedent
    def put_dedent(self, key=None):
        '''Increase indentation level and put the key.'''
        self.indent -= 1
        if key:
            self.put(key)

    def put_indent(self, key=None):
        '''Put the key and then decrease the indentation level.'''
        if key:
            self.put(key)
        self.indent += 1
    #@+node:ekr.20160412101845.15: *4* put_list
    def put_list(self, key, s):
        '''Put a json list.'''
        if s.strip():
            self.put_indent('"%s": [' % key)
            lines = g.splitLines(s)
            for i, s in enumerate(lines):
                if i == len(lines)-1:
                    self.put('"%s",' % self.clean(s.rstrip()))
                else:
                    self.put('"%s\\n",' % self.clean(s.rstrip()))
            self.put_dedent(']')
        else:
            self.put_key_val(key, '[]')

    #@+node:ekr.20160412101845.16: *4* put_outline
    def put_outline(self):
        '''Put all cells in the outline.'''
        self.put_indent('{')
        self.put_indent('"cells": [')
        for child in self.root.children():
            if self.is_cell(child):
                self.put_cell(child)
        self.put_dedent(']')
        self.put_dedent()
        self.put_prefix()
        self.put('}')
    #@+node:ekr.20160412101845.17: *4* put_prefix
    def put_prefix(self):
        '''Put the data contained in the prefix node, or defaults.'''
        p = self.find_key('# {prefix}', self.root)
        self.indent += 1
        if p:
            for child in p.children():
                self.put_any_non_cell_data(child)
        else:
            prefix = self.default_metadata()
            for s in g.splitLines(prefix):
                self.put(s.rstrip())
        self.indent -= 1
    #@+node:ekr.20160412101845.18: *3* Utils
    #@+node:ekr.20160412101845.19: *4* clean
    def clean(self, s):
        '''Perform json escapes on s.'''
        table = (
            ('\\','\\\\'), # Must be first.
            ('\b', '\\b'),
            ('\f', '\\f'),
            ('\n', '\\n'),
            ('\r', ''),
            ('\t', '\\t'),
            ('"', '\\"'),
        )
        for ch1, ch2 in table:
            s = s.replace(ch1, ch2)
        return s
    #@+node:ekr.20160412101845.20: *4* clean_outline
    def clean_outline(self):
        '''Remove commas before } and ]'''
        # JSON sure is picky.
        n, result = len(self.lines), []
        for i, s in enumerate(self.lines):
            assert not s.endswith('\n')
            if s.endswith(','):
                if i == n-1:
                    val = s[:-1]
                else:
                    s2 = self.lines[i+1].strip()
                    if s2.startswith(']') or s2.startswith('}'):
                        val = s[:-1]
                    else:
                        val = s
            else:
                val = s
            result.append(val)
        return result
    #@+node:ekr.20160412101845.21: *4* default_metadata
    def default_metadata(self):
        '''Return the top-level metadata to use if there is no {prefix} node.'''
        s = '''\
    "metadata": {
     "kernelspec": {
      "display_name": "Python %(version)s",
      "language": "python",
      "name": "python%(version)s"
     },
     "language_info": {
      "codemirror_mode": {
       "name": "ipython",
       "version": %(version)s
      },
      "file_extension": ".py",
      "mimetype": "text/x-python",
      "name": "python",
      "nbconvert_exporter": "python",
      "pygments_lexer": "ipython3",
      "version": "%(long_version)s"
     }
    },
    "nbformat": 4,
    "nbformat_minor": 0'''
        n1, n2 = sys.version_info[0], sys.version_info[1]
        s = s % {
           'version': n1,
           'long_version': '%s.%s' % (n1, n2),
        }
        return g.adjustTripleString(s, 1)
    #@+node:ekr.20160412101845.22: *4* find_key
    def find_key(self, key, p):
        '''Return the non-cell node in p's direct children with the given key.'''
        for child in p.children():
            if child.h.endswith(key):
                return child
        return None
    #@+node:ekr.20160412101845.23: *4* has_data_children
    def has_data_children(self, p):
        '''Return True if p has any non-cell direct children.'''
        return p.hasChildren() and any([not self.is_cell(z) for z in p.children()])
    #@+node:ekr.20160412101845.24: *4* get_file_name (export)
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
    #@+node:ekr.20160412101845.25: *4* is_cell
    def is_cell(self, p):
        '''Return True if p is a cell node.'''
        return not p.h.startswith('#')
    #@+node:ekr.20160412101845.26: *4* level
    def level(self, p):
        '''Return the level of p relative to self.root (one-based)'''
        return p.level() - self.root.level()

    #@+node:ekr.20160412101845.27: *4* oops
    def oops(self, p, s):
        '''Give an error message.'''
        g.es_trace('===== %s %s' % (s, p.h), color='red')
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
