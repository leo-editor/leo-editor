import time

import leo.plugins.writers.basewriter as basewriter

class CTextWriter(basewriter.BaseWriter):
    
    def recurse(self, nd, level=0):
        self.put(nd.b.strip()+'\n\n')
        for child in nd.children():
            txt = self.cchar*3 + self.cchar*level + ' ' + child.h.strip() + ' '
            txt += self.cchar * max(0, 75-len(txt))
            self.put(txt+'\n\n')
            self.recurse(child, level+1)
    
    def write(self,root):
        
        self.cchar = '#'
        if root.h.lower()[-4:] == '.sql':
            self.cchar = '-'
        if root.h.lower()[-3:] == '.js':
            self.cchar = '/'
        
        self.recurse(root, 0)
        return True

writer_dict = {
    '@auto': ['@auto-ctext',],
    'class': CTextWriter,
}
