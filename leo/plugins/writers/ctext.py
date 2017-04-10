#@+leo-ver=5-thin
#@+node:tbrown.20140804103545.29975: * @file writers/ctext.py
#@@language python
#@@tabwidth -4
import leo.plugins.writers.basewriter as basewriter
#@+others
#@+node:tbrown.20140804103545.29977: ** class CTextWriter
class CTextWriter(basewriter.BaseWriter):
    #@+others
    #@+node:tbrown.20140804103545.29978: *3* recurse
    def recurse(self, nd, level=0):
        self.put(nd.b.strip()+'\n\n')
        for child in nd.children():
            txt = self.cchar*3 + self.cchar*level + ' ' + child.h.strip() + ' '
            txt += self.cchar * max(0, 75-len(txt))
            self.put(txt+'\n\n')
            self.recurse(child, level+1)
    #@+node:tbrown.20140804103545.29979: *3* write
    def write(self,root):

        self.cchar = '#'
        if root.h.lower()[-4:] == '.tex':
            self.cchar = '%'
        if root.h.lower()[-4:] == '.sql':
            self.cchar = '-'
        if root.h.lower()[-3:] == '.js':
            self.cchar = '/'
        self.recurse(root, 0)
        return True

    #@-others
#@-others
writer_dict = {
    '@auto': ['@auto-ctext',],
    'class': CTextWriter,
}
#@@language python
#@@tabwidth -4
#@-leo
