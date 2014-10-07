#@+leo-ver=5-thin
#@+node:tbrown.20140801105909.47549: * @file importers/ctext.py
#@@language python
#@@tabwidth -4
#@+others
#@+node:tbrown.20140801105909.47550: ** ctext declarations
import time
# import leo.core.leoGlobals as g
from leo.plugins.importers.basescanner import BaseScanner

#@+node:tbrown.20140801105909.47551: ** class CTextScanner
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
    #@+others
    #@+node:tbrown.20140801105909.47552: *3* write_lines

    def write_lines(self, node, lines):
        """write the body lines to body normalizing whitespace"""
        node.b = '\n'.join(lines).strip('\n')+'\n'
        lines[:] = []

    #@+node:tbrown.20140801105909.47553: *3* run
    def run(self,s,parent,parse_body=False,prepass=False):
        
        cchar = '#'
        if self.fileType.lower() == '.tex':
            cchar = '%'
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
                    self.write_lines(nd, lines)
                    new_level = len(word[0]) - 3
                    if new_level > level:
                        # go down one level
                        level = new_level
                        nd = nd.insertAsLastChild()
                        nd.h = ' '.join(word[1:]).strip(cchar+' ')
                    else:
                        # go up zero or more levels
                        while level > new_level and level > 0:
                            level -= 1
                            nd = nd.parent()
                        nd = nd.insertAfter()
                        nd.h = ' '.join(word[1:]).strip(cchar+' ')
            else:
                lines.append(line)
                
        self.write_lines(nd, lines)
                
        # g.es("CText import in %s" % (time.time()-start))

        return True

    #@-others
#@-others
importer_dict = {
    '@auto': ['@auto-ctext',],
    'class': CTextScanner,
}
#@-leo
