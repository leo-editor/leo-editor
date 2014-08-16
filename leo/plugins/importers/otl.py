#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18150: * @file importers/otl.py
'''The @auto importer for vim-outline files.'''
import leo.core.leoGlobals as g
import leo.plugins.importers.basescanner as basescanner
#@+others
#@+node:ekr.20140723122936.18114: ** class VimoutlinerScanner
class VimoutlinerScanner(basescanner.BaseScanner):
    
    def __init__ (self,importCommands,atAuto):
        '''ctor for VimoutlinerScanner class.'''
        # Init the base class.
        basescanner.BaseScanner.__init__(self,
            importCommands,atAuto=atAuto,language='plain')
                # Use @language plain.
        # Overrides of base-class ivars.
        self.fullChecks = False
        self.hasDecls = False
        self.parents = []
        # Note: self.tab_width only affects tabs in body text.
        # The read/write code uses hard tabs to write leading identation.

    #@+others
    #@+node:ekr.20140723122936.18115: *3* VimoutlineScanner.scanHelper & helpers
    # Override BaseScanner.scanHelper.

    def scanHelper(self,s,i,end,parent,kind):
        '''Create Leo nodes for all vimoutliner lines.'''
        assert kind == 'outer' and end == len(s)
        while i < len(s):
            # Set k to the end of the line.
            progress = i
            k = g.skip_line(s,i)
            line = s[i:k] # For traces.
            # Skip leading hard tabs, ignore blanks & compute the line's level.
            level = 1 # The root has level 0.
            while i < len(s) and s[i].isspace():
                if s[i] == '\t': level += 1
                i += 1
            if i == k:
                g.trace('ignoring blank line: %s' % (repr(line)))
            elif i < len(s) and s[i] == ':':
                # Append the line to the body.
                i += 1
                if i < len(s) and s[i] == ' ':
                    i += 1
                else:
                    g.trace('missing space after colon: %s' % (repr(line)))
                p = self.findParent(level)
                p.b = p.b + s[i:k]
            else:
                putRef = True
                # Cut back the stack, then allocate a new (placeholder) node.
                self.parents = self.parents[:level]
                p = self.findParent(level)

                # Set the headline of the placeholder node.
                h = s[i:k]
                p.h = h[:-1] if h.endswith('\n') else h
            # Move to the next line.
            i = k
            assert progress < i,'i: %s %s' % (i,repr(line))

        return len(s),putRef,0 # bodyIndent not used.
    #@+node:ekr.20140723122936.18116: *4* vos.findParent
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
    #@+node:ekr.20140723122936.18117: *4* vos.createNode
    def createNode (self,b,h,level):

        parent = self.findParent(level)
        p = self.createHeadline(parent,b,h)
        self.parents = self.parents[:level+1]
        self.parents.append(p)
    #@+node:ekr.20140816075119.18152: *4* vos.endGen
    def endGen (self,s):
        '''End code generation.'''
        warning = '\nWarning: this node is ignored when writing this file.\n\n'
        self.root.b = self.root.b + warning
    #@-others
#@-others
importer_dict = {
    '@auto': ['@auto-otl','@auto-vim-outline',],
    'class': VimoutlinerScanner,
    'extensions': ['.otl',],
}
#@-leo
