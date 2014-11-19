#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18151: * @file importers/leo_rst.py
'''
The @auto importer for restructured text.

This module must **not** be named rst, so as not to conflict with docutils.
'''
import leo.core.leoGlobals as g
import leo.plugins.importers.basescanner as basescanner
#@+others
#@+node:ekr.20140723122936.18099: ** class RstScanner
class RstScanner (basescanner.BaseScanner):

    #@+others
    #@+node:ekr.20140723122936.18100: *3*  __init__ (RstScanner)
    def __init__ (self,importCommands,atAuto):

        # Init the base class.
        basescanner.BaseScanner.__init__(self,importCommands,atAuto=atAuto,language='rest')

        # Scanner overrides
        self.atAutoWarnsAboutLeadingWhitespace = True
        self.blockDelim1 = self.blockDelim2 = None
        self.classTags = []
        self.escapeSectionRefs = False
        self.functionSpelling = 'section'
        self.functionTags = []
        self.hasClasses = False
        self.ignoreBlankLines = True
        self.isRst = True
        self.lineCommentDelim = '..'
        self.outerBlockDelim1 = None
        self.sigFailTokens = []
        self.strict = False # Mismatches in leading whitespace are irrelevant.

        # Ivars unique to rst scanning & code generation.
        self.lastParent = None # The previous parent.
        self.lastSectionLevel = 0 # The section level of previous section.
        self.sectionLevel = 0 # The section level of the just-parsed section.
        self.underlineCh = '' # The underlining character of the last-parsed section.
        self.underlines = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~" # valid rst underlines.
        self.underlines1 = [] # Underlining characters for underlines.
        self.underlines2 = [] # Underlining characters for over/underlines.
    #@+node:ekr.20140723122936.18101: *3* adjustParent (RstScanner)
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
                    h2 = '@rst-no-head %s' % headline
                    body = ''
                    parent = self.createFunctionNode(h2,body,parent)
        else:
            assert self.root
            self.lastParent = self.root
        if not parent:
            parent = self.root
        if trace: g.trace('level %s lastLevel %s %s returns %s' % (
            level,lastLevel,headline,parent.h))
        #self.lastSectionLevel = self.sectionLevel
        self.lastParent = parent.copy()
        return parent.copy()
    #@+node:ekr.20140723122936.18102: *3* computeBody (RstScanner)
    def computeBody (self,s,start,sigStart,codeEnd):

        trace = False and not g.unitTesting

        body1 = s[start:sigStart]
        # Adjust start backwards to get a better undent.
        if body1.strip():
            while start > 0 and s[start-1] in (' ','\t'):
                start -= 1

        # Never indent any text; discard the entire signature.
        body1 = s[start:sigStart]
        body2 = s[self.sigEnd+1:codeEnd]
        body2 = g.removeLeadingBlankLines(body2) # 2009/12/28
        body = body1 + body2

        # Don't warn about missing tail newlines: they will be added.
        if trace: g.trace('body: %s' % repr(body))
        return body1,body2
    #@+node:ekr.20140723122936.18103: *3* computeSectionLevel
    def computeSectionLevel (self,ch,kind):
        '''Return the section level of the underlining character ch.'''
        if kind == 'over':
            assert ch in self.underlines2
            level = 0
        else:
            level = 1 + self.underlines1.index(ch)
        if 0:
            g.trace('level: %s kind: %s ch: %s under2: %s under1: %s' % (
                level,kind,ch,self.underlines2,self.underlines1))
        return level
    #@+node:ekr.20140723122936.18104: *3* createDeclsNode
    def createDeclsNode (self,parent,s):

        '''Create a child node of parent containing s.'''

        # Create the node for the decls.
        headline = '@rst-no-head %s declarations' % self.methodName
        body = self.undentBody(s)
        self.createHeadline(parent,body,headline)
    #@+node:ekr.20140723122936.18105: *3* endGen (RstScanner)
    def endGen (self,s):

        '''Remember the underlining characters in the root's uA.'''

        trace = False and not g.unitTesting
        p = self.root
        if p:
            tag = 'rst-import'
            d = p.v.u.get(tag,{})
            underlines1 = ''.join([str(z) for z in self.underlines1])
            underlines2 = ''.join([str(z) for z in self.underlines2])
            d ['underlines1'] = underlines1
            d ['underlines2'] = underlines2
            self.underlines1 = underlines1
            self.underlines2 = underlines2
            if trace: g.trace(repr(underlines1),repr(underlines2),g.callers(4))
            p.v.u [tag] = d

        # Append a warning to the root node.
        warningLines = (
            'Warning: this node is ignored when writing this file.',
            'However, @ @rst-options are recognized in this node.',
        )
        lines = ['.. %s' % (z) for z in warningLines]
        warning = '\n%s\n' % '\n'.join(lines)
        self.root.b = self.root.b + warning
    #@+node:ekr.20140723122936.18106: *3* isUnderLine
    def isUnderLine(self,s):

        '''Return True if s consists of only the same rST underline character.'''

        if not s: return False
        ch1 = s[0]

        if not ch1 in self.underlines:
            return False

        for ch in s:
            if ch != ch1:
                return False

        return True
    #@+node:ekr.20140723122936.18107: *3* startsComment/ID/String
    # These do not affect parsing.

    def startsComment (self,s,i):
        return False

    def startsID (self,s,i):
        return False

    def startsString (self,s,i):
        return False
    #@+node:ekr.20140723122936.18108: *3* startsHelper (RstScanner)
    def startsHelper(self,s,i,kind,tags,tag=None):

        '''return True if s[i:] starts an rST section.
        Sets sigStart, sigEnd, sigId and codeEnd ivars.'''

        trace = False and not g.unitTesting
        verbose = True
        kind,name,next,ch = self.startsSection(s,i)
        if kind == 'plain': return False

        self.underlineCh = ch
        self.lastSectionLevel = self.sectionLevel
        self.sectionLevel = self.computeSectionLevel(ch,kind)
        self.sigStart = g.find_line_start(s,i)
        self.sigEnd = next
        self.sigId = name
        i = next + 1

        if trace: g.trace('sigId',self.sigId,'next',next)

        while i < len(s):
            progress = i
            i,j = g.getLine(s,i)
            kind,name,next,ch = self.startsSection(s,i)
            if trace and verbose: g.trace(kind,repr(s[i:j]))
            if kind in ('over','under'):
                break
            else:
                i = j
            assert i > progress

        self.codeEnd = i

        if trace:
            if verbose:
                g.trace('found...\n%s' % s[self.sigStart:self.codeEnd])
            else:
                g.trace('level %s %s' % (self.sectionLevel,self.sigId))
        return True
    #@+node:ekr.20140723122936.18109: *3* startsSection & helper
    def startsSection (self,s,i):

        '''Scan a line and possible one or two other lines,
        looking for an underlined or overlined/underlined name.

        Return (kind,name,i):
            kind: in ('under','over','plain')
            name: the name of the underlined or overlined line.
            i: the following character if kind is not 'plain'
            ch: the underlining and possibly overlining character.
        '''

        trace = False and not g.unitTesting
        verbose = False

        # Under/overlines can not begin with whitespace.
        i1,j,nows,line = self.getLine(s,i)
        ch,kind = '','plain' # defaults.

        if nows and self.isUnderLine(line): # an overline.
            name_i = g.skip_line(s,i1)
            name_i,name_j = g.getLine(s,name_i)
            name = s[name_i:name_j].strip()
            next_i = g.skip_line(s,name_i)
            i,j,nows,line2 = self.getLine(s,next_i)
            n1,n2,n3 = len(line),len(name),len(line2)
            ch1,ch3 = line[0],line2 and line2[0]
            ok = (nows and self.isUnderLine(line2) and
                n1 >= n2 and n2 > 0 and n3 >= n2 and ch1 == ch3)
            if ok:
                i += n3
                ch,kind = ch1,'over'
                if ch1 not in self.underlines2:
                    self.underlines2.append(ch1)
                    if trace: g.trace('*** underlines2',self.underlines2,name)
                if trace and verbose:
                    g.trace('\nline  %s\nname  %s\nline2 %s' % (
                        repr(line),repr(name),repr(line2))) #,'\n',g.callers(4))
        else:
            name = line.strip()
            i = g.skip_line(s,i1)
            i,j,nows2,line2 = self.getLine(s,i)
            n1,n2 = len(name),len(line2)
            # look ahead two lines.
            i3,j3 = g.getLine(s,j)
            name2 = s[i3:j3].strip()
            i4,j4,nows4,line4 = self.getLine(s,j3)
            n3,n4 = len(name2),len(line4)
            overline = (
                nows2 and self.isUnderLine(line2) and
                nows4 and self.isUnderLine(line4) and
                n3 > 0 and n2 >= n3 and n4 >= n3)
            ok = (not overline and nows2 and self.isUnderLine(line2) and
                n1 > 0 and n2 >= n1)
            if ok:
                i += n2
                ch,kind = line2[0],'under'
                if ch not in self.underlines1:
                    self.underlines1.append(ch)
                    if trace: g.trace('*** underlines1',self.underlines1,name)
                if trace and verbose: g.trace('\nname  %s\nline2 %s' % (
                    repr(name),repr(line2)))
        return kind,name,i,ch
    #@+node:ekr.20140723122936.18110: *4* getLine
    def getLine (self,s,i):

        i,j = g.getLine(s,i)
        line = s[i:j]
        nows = i == g.skip_ws(s,i)
        line = line.strip()

        return i,j,nows,line
    #@-others
#@-others
importer_dict = {
    '@auto': ['@auto-rst',],
    'class': RstScanner,
    'extensions': ['.rst','.rest',],
}
#@-leo
