#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18146: * @file importers/org.py
'''The @auto importer for Emacs org-mode.'''
import leo.core.leoGlobals as g
import leo.plugins.importers.basescanner as basescanner
#@+others
#@+node:ekr.20140723122936.18072: ** class OrgModeScanner
class OrgModeScanner(basescanner.BaseScanner):
    '''A class to scan Emacs org-mode files.'''
    def __init__ (self,importCommands,atAuto):
        '''ctor for OrgModeScanner class.'''
        # Init the base class.
        basescanner.BaseScanner.__init__(self,
            importCommands,atAuto=atAuto,language='plain')
                # Use @language plain.
        # Overrides of base-class ivars.
        self.fullChecks = False
        self.hasDecls = False
        self.parents = []

    #@+others
    #@+node:ekr.20140723122936.18073: *3* OrgModeScanner.scanHelper & helpers
    def scanHelper(self,s,i,end,parent,kind):
        '''
        Create Leo nodes for all org-mode lines.
        Overrides BaseScanner.scanHelper.
        '''
        assert kind == 'outer' and end == len(s)
        putRef = False
        level = 1 # The root has level 0.
        while i < len(s):
            progress = i
            # Get the next line, with k the index of the last char.
            k = g.skip_line(s,i)
            line = s[i:k]
            if line.startswith('*'):
                # Handle the headline & reset the level.
                j = 0
                while j < len(line) and line[j] == '*':
                    j += 1
                level = j
                putRef = True
                # Cut back the stack, then allocate a new (placeholder) node.
                self.parents = self.parents[:level]
                p = self.findParent(level)
                # Set the headline of the placeholder node.
                p.h = line[j:k].strip()
            else:
                # Append the line to the body.
                p = self.findParent(level)
                p.b = p.b + line
            # Move to the next line.
            i = k
            assert progress < i,'i: %s %s' % (i,repr(line))
        return len(s),putRef,0 # bodyIndent not used.
    #@+node:ekr.20140723122936.18074: *4* oms.findParent
    def findParent(self,level):
        '''
        Return the parent at the indicated level, allocating
        place-holder nodes as necessary.
        '''
        trace = False and not g.unitTesting
        assert level >= 0
        if not self.parents:
            self.parents = [self.root]
        if trace: g.trace(level,[z.h for z in self.parents])
        while level >= len(self.parents):
            b = ''
            h = 'placeholder' if level > 1 else 'declarations'
            parent = self.parents[-1]
            p = self.createHeadline(parent,b,h)
            self.parents.append(p)
        return self.parents[level]
    #@+node:ekr.20140723122936.18075: *4* oms.createNode
    def createNode (self,b,h,level):

        parent = self.findParent(level)
        p = self.createHeadline(parent,b,h)
        self.parents = self.parents[:level+1]
        self.parents.append(p)
    #@+node:ekr.20140816065309.18222: *4* oms.endGen
    def endGen (self,s):
        '''End code generation.'''
        warning = '\nWarning: this node is ignored when writing this file.\n\n'
        self.root.b = self.root.b + warning
    #@-others
#@-others
importer_dict = {
    '@auto': ['@auto-org','@auto-org-mode',],
    'class': OrgModeScanner,
    'extensions': ['.org',],
}
#@-leo
