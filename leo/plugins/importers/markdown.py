#@+leo-ver=5-thin
#@+node:ekr.20140725190808.18066: * @file importers/markdown.py
'''The @auto importer for markdown.'''
import leo.core.leoGlobals as g
import leo.plugins.importers.basescanner as basescanner
#@+others
#@+node:ekr.20140725190808.18067: ** class MarkdownScanner
class MarkdownScanner (basescanner.BaseScanner):

    #@+others
    #@+node:ekr.20140725190808.18068: *3* mds.__init__
    def __init__ (self,importCommands,atAuto):
        '''ctor for MarkdownScanner class.'''
        # Init the base class.
        basescanner.BaseScanner.__init__(self,importCommands,
            atAuto=atAuto,language='md')
        # Scanner overrides
        self.atAutoSeparateNonDefNodes = False # Fix bug 66.
        self.atAutoWarnsAboutLeadingWhitespace = True
        self.blockDelim1 = self.blockDelim2 = None
        self.classTags = []
        self.escapeSectionRefs = False
        self.functionTags = []
        self.hasClasses = False
        self.hasDecls = True # Fix bug 66.
        self.ignoreBlankLines = True
        self.isRst = False # Don't set this: it messes with underlining.
        self.lineCommentDelim = None
        self.outerBlockDelim1 = None
        self.sigFailTokens = []
        self.strict = False # Mismatches in leading whitespace are irrelevant.
        # Ivars unique to markdown scanning & code generation.
        self.lastParent = None # The previous parent.
        self.lastSectionLevel = 0 # The section level of previous section.
        self.sectionLevel = 0 # The section level of the just-parsed section.
        self.underlineDict = {}
            # Keys are names. Values are underlining styles.

    #@+node:ekr.20140725190808.18069: *3* mds.adjustParent
    def adjustParent (self,parent,headline):
        '''Return the proper parent of the new node.'''
        trace = False and not g.unitTesting
        level,lastLevel = self.sectionLevel,self.lastSectionLevel
        lastParent = self.lastParent
        if trace: g.trace('**entry level: %s lastLevel: %s lastParent: %s' % (
            level,lastLevel,lastParent and lastParent.h or '<none>'))
        if self.lastParent:
            if level <= lastLevel:
                parent = lastParent.parent()
                while level < lastLevel:
                    level += 1
                    parent = parent.parent()
            else: # level > lastLevel.
                level -= 1
                parent = lastParent
                while level > lastLevel:
                    level -= 1
                    h2 = 'placeholder' if level > 1 else 'declarations'
                    body = ''
                    parent = self.createFunctionNode(h2,body,parent)
        else:
            assert self.root
            self.lastParent = self.root
        if not parent:
            parent = self.root
        if trace: g.trace('level %s lastLevel %s %s returns %s' % (
            level,lastLevel,headline,parent.h))
        self.lastParent = parent.copy()
        return parent.copy()
    #@+node:ekr.20140725190808.18070: *3* mds.computeBody
    def computeBody (self,s,start,sigStart,codeEnd):
        '''Return the body of a section.'''
        trace = False and not g.unitTesting
        # Never indent any text; discard the entire signature.
        body1 = ''
        body2 = s[self.sigEnd:codeEnd]
        body2 = g.removeLeadingBlankLines(body2) 
        # Don't warn about missing tail newlines: they will be added.
        if trace:
            # g.trace(s[start:sigStart])
            g.trace('body: %s' % repr(body1 + body2),'\n',g.callers())
        return body1,body2
    #@+node:ekr.20141110223158.16: *3* mds.createDeclsNode (new)
    def createDeclsNode (self,parent,s):
        '''Create a child node of parent containing s.'''
        # Create the node for the decls.
        headline = 'markdown declarations'
        body = self.undentBody(s)
        p = self.createHeadline(parent,body,headline)
        # Remember that this node should not have its headline written.
        d = self.underlineDict
        d [headline] = None
        return p
    #@+node:ekr.20141110223158.15: *3* mds.endGen
    def endGen (self,s):
        '''Finish code generation.'''
        p = self.root
        # Add the warning to the root's body text.
        warning = '\nWarning: this node is ignored when writing this file.\n'
        self.root.b = p.b + warning
        # Put the underlineDict in self.root.v.u
        u = p.v.u
        tag = 'markdown-import'
        d = u.get(tag,{})
        d ['underline_dict'] = self.underlineDict
        p.v.u [tag] = d
    #@+node:ekr.20140725190808.18074: *3* mds.isUnderline
    def isUnderline(self,s):
        '''
        Return 1 if s is all '=' characters.
        Return 2 if s is all '-' characters.
        Return 0 otherwise.
        '''
        if not s: return 0
        ch1 = s[0]
        if not ch1 in '=-':
            return False
        for ch in s:
            if ch == '\n':
                break
            elif ch != ch1:
                return 0
        return 1 if ch1 == '=' else 2
    #@+node:ekr.20140725190808.18075: *3* mds.startsComment/ID/String
    # These do not affect parsing.
    def startsComment (self,s,i):
        return False

    def startsID (self,s,i):
        return False

    def startsString (self,s,i):
        return False
    #@+node:ekr.20140725190808.18076: *3* mds.startsHelper
    def startsHelper(self,s,i,kind,tags,tag=None):
        '''
        return True if s[i:] starts an markdown section.
        Sets sigStart, sigEnd, sigId and codeEnd ivars.
        '''
        trace = False and not g.unitTesting
        level,name,i = self.startsSection(s,i)
        if level == 0:
            return False
        self.lastSectionLevel = self.sectionLevel
        self.sectionLevel = level
        self.sigStart = g.find_line_start(s,i)
        self.sigEnd = i
        self.sigId = name
        i += 1
        while i < len(s):
            progress = i
            i,j = g.getLine(s,i)
            level,name,j = self.startsSection(s,i)
            if level > 0: break
            else: i = j
            assert i > progress
        self.codeEnd = i
        if trace: g.trace('found %s...\n%s' % (
            self.sigId,s[self.sigStart:self.codeEnd]))
        return True
    #@+node:ekr.20140725190808.18077: *3* mds.startsSection
    def startsSection (self,s,i):
        '''
        Scan one or two lines looking for the start of a section.
        Sections are an underlined name or a line starting with '#'s.
        Return (level,name,i):
            level: 0 for plain lines, n > 0 for section lines.
            name: the section name or None.
            i: the new i.
        '''
        i2,j2 = g.getLine(s,i)
        line = s[i2:j2]
        if line.startswith('#'):
            # Found a section line.
            level = 0
            while level < len(line) and line[level] == '#':
                level += 1
            name = line[level:].rstrip() # Retain leading ws.
            kind = '#'
        else:
            # Look ahead if the next line is an underline.
            i2,j2 = g.getLine(s,j2)
            line2 = s[i2:j2]
            level = self.isUnderline(line2)
            name = line.rstrip() if level > 0 else None
            kind = {0: '#', 1: '=', 2: '-'}.get(level)
        # Update the kind dict.
        if name:
            d = self.underlineDict
            d [name] = kind
        return level,name,j2
    #@-others
#@-others
importer_dict = {
    '@auto': ['@auto-markdown',],
    'class': MarkdownScanner,
    'extensions': ['.md',],
}
#@-leo
