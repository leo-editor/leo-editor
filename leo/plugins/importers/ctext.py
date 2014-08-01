import time
import leo.core.leoGlobals as g
from basescanner import BaseScanner

class CTextScanner(BaseScanner):
    """
    Read/Write simple text files with hierarchy embedded in headlines::
        
        Leading text in root node of subtree
        
        Etc. etc.
        
        ### A level one node #####################################
        
        This would be the text in this level one node.
        
        And this.
        
        ### Another level one node ###############################
        
        Another one
        
        #### A level 2 node ######################################
        
        See what we did there - one more '#' - this is a subnode.
        
    Leading / trailing whitespace may not be preserved.  '-' and '/'
    are used in place of '#' for SQL and JavaScript.
        
    """
    
    def write_lines(self, node, lines):
        """write the body lines to body normalizing whitespace"""
        node.b = '\n'.join(lines).strip('\n')+'\n'
        lines[:] = []
    
    def run(self,s,parent,parse_body=False,prepass=False):
        
        cchar = '#'
        if self.fileType.lower() == '.sql':
            cchar = '-'
        if self.fileType.lower() == '.js':
            cchar = '/'

        level = -1
        nd = parent.copy()
        start = time.time()
        lines = []
        for line in s.split('\n'):
            if line.startswith(cchar*3):
                word = line.split()
                if word[0].strip(cchar) == '':
                    new_level = len(word[0]) - 3
                    if new_level > level:
                        level = new_level
                        self.write_lines(nd, lines)
                        nd = nd.insertAsLastChild()
                        nd.h = ' '.join(word[1:]).strip(cchar+' ')
                    else:
                        while level > new_level and level > 0:
                            level -= 1
                            nd = nd.parent()
                        self.write_lines(nd, lines)
                        nd = nd.insertAfter()
                        nd.h = ' '.join(word[1:]).strip(cchar+' ')
            else:
                lines.append(line)
                
        self.write_lines(nd, lines)
                
        # g.es("CText import in %s" % (time.time()-start))

        return True

importer_dict = {
    '@auto': ['@auto-ctext',],
    'class': CTextScanner,
}
