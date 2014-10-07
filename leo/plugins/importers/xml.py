#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18137: * @file importers/xml.py
'''The @auto importer for XML.'''
import leo.core.leoGlobals as g
import leo.plugins.importers.basescanner as basescanner
#@+others
#@+node:ekr.20140723122936.18119: ** class XmlScanner (BaseScanner)
class XmlScanner (basescanner.BaseScanner):

    #@+others
    #@+node:ekr.20140723122936.18120: *3*  ctor_(XmlScanner)
    def __init__ (self,importCommands,atAuto,tags_setting='import_xml_tags'):

        # Init the base class.
        basescanner.BaseScanner.__init__(self,importCommands,atAuto=atAuto,language='xml')
            # sets self.c

        # Set the parser delims.
        self.blockCommentDelim1 = '<!--'
        self.blockCommentDelim2 = '-->'
        self.blockDelim1 = None 
        self.blockDelim2 = None
        self.classTags = [] # Inited by import_xml_tags setting.
        self.extraIdChars = None
        self.functionTags = []
        self.lineCommentDelim = None
        self.lineCommentDelim2 = None
        self.outerBlockDelim1 = None
        self.outerBlockDelim2 = None
        self.outerBlockEndsDecls = False
        self.sigHeadExtraTokens = []
        self.sigFailTokens = []

        # Overrides more attributes.
        self.atAutoWarnsAboutLeadingWhitespace = False
        self.caseInsensitive = True
        self.hasClasses = True
        self.hasDecls = False
        self.hasFunctions = False
        self.hasNestedClasses = True
        self.ignoreBlankLines = False # The tokenizer handles this.
        self.ignoreLeadingWs = True # A drastic step, but there seems to be no other way.
        self.strict = False
        self.tags_setting = tags_setting
        self.trace = False

        self.addTags()
    #@+node:ekr.20140723122936.18121: *3* addTags
    def addTags (self):

        '''Add items to self.class/functionTags and from settings.'''

        trace = False # and not g.unitTesting
        c = self.c

        for ivar,setting in (
            ('classTags',self.tags_setting),
        ):
            aList = getattr(self,ivar)
            aList2 = c.config.getData(setting) or []
            aList2 = [z.lower() for z in aList2]
            aList.extend(aList2)
            setattr(self,ivar,aList)
            if trace: g.trace(ivar,aList)
    #@+node:ekr.20140723122936.18122: *3* adjust_class_ref (XmlScanner)
    def adjust_class_ref(self,s):

        '''Ensure that @others appears at the start of a line.'''


        trace = False and not g.unitTesting
        if trace: g.trace('old',repr(s))

        i = s.find('@others')
        if i > -1:
            j = i
            i -= 1
            while i >= 0 and s[i] in '\t ':
                i -= 1
            if i < j:
                # 2011/11/04: Never put lws before @others.
                s = s[:i+1] + s[j:]
            if i > 0 and s[i] != '\n':
                s = s[:i+1] + '\n' + s [i+1:]

        if trace: g.trace('new',repr(s))
        return s
    #@+node:ekr.20140723122936.18123: *3* adjustTestLines (XmlScanner)
    def adjustTestLines(self,lines):

        '''A desparation measure to attempt reasonable comparisons.'''

        # self.ignoreBlankLines:
        lines = [z for z in lines if z.strip()]
        # if self.ignoreLeadingWs:
        lines = [z.lstrip() for z in lines]
        lines = [z.replace('@others','') for z in lines]
        # lines = [z.replace('>\n','>').replace('\n<','<') for z in lines]
        return lines
    #@+node:ekr.20140723122936.18124: *3* filterTokens (XmlScanner)
    def filterTokens (self,tokens):

        '''Filter tokens as needed for correct comparisons.

        For xml, this means:

        1. Removing newlines after opening elements.
        2. Removing newlines before closing elements.
        3. Converting sequences of whitespace to a single blank.
        '''

        trace = False
        if trace: g.trace(tokens)
        if 1: # Permissive code.
            return [(kind,val,line_number) for (kind,val,line_number) in tokens
                if kind not in ('nl','ws')]
        else: # Accurate code.
            # Pass 1. Insert newlines before and after elements.
            i,n,result = 0,len(tokens),[]
            while i < n:
                progress = i
                # Compute lookahead tokens.
                kind1,val1,n1 = tokens[i]
                kind2,val2,n2 = None,None,None
                kind3,val3,n3 = None,None,None
                kind4,val4,n4 = None,None,None
                if i + 1 < n: kind2,val2,n2 = tokens[i+1]
                if i + 2 < n: kind3,val3,n3 = tokens[i+2]
                if i + 3 < n: kind4,val4,n4 = tokens[i+3]
                # Always insert the present token.
                result.append((kind1,val1,n1),)
                i += 1
                if (
                    kind1 == 'other' and val1 == '>' and
                    kind2 != 'nl'
                ):
                    # insert nl after >
                    if trace: g.trace('** insert nl after >')
                    result.append(('nl','\n',n1),)
                elif (
                    kind1 != 'nl'    and
                    kind2 == 'other' and val2 == '<' and
                    kind3 == 'other' and val3 == '/' and
                    kind4 == 'id'
                ):
                    # Insert nl before </id
                    if trace: g.trace('** insert nl before </%s' % (val4))
                    result.append(('nl','\n',n1),)
                else:
                    pass
                assert progress == i-1
            # Pass 2: collapse newlines and whitespace separately.
            tokens = result
            i,n,result = 0,len(tokens),[]
            while i < n:
                progress = i
                kind1,val1,n1 = tokens[i]
                if kind1 == 'nl':
                    while i < n and tokens[i][0] == 'nl':
                        i += 1
                    result.append(('nl','\n',n1),)
                elif kind1 == 'ws':
                    while i < n and tokens[i][0] == 'ws':
                        i += 1
                    result.append(('ws',' ',n1),)
                else:
                    result.append((kind1,val1,n1),)
                    i += 1
                assert progress < i
            return result
    #@+node:ekr.20140723122936.18125: *3* isSpace (XmlScanner) (Use the base class now)
    # def isSpace(self,s,i):

        # '''Return true if s[i] is a tokenizer space.'''

        # # Unlike the base-class method, xml space tokens include newlines.
        # return i < len(s) and s[i].isspace()
    #@+node:ekr.20140723122936.18126: *3* skip...Token (XmlScanner overrides)
    def skipCommentToken(self,s,i):

        '''Return comment lines with all leading/trailing whitespace removed.'''
        j = self.skipComment(s,i)
        lines = g.splitLines(s[i:j])
        lines = [z.strip() for z in lines]
        return j,'\n'.join(lines)

    # skipIdToken: no change.
    # skipNewlineToken: no change.
    # skipOtherToken: no change.
    # skipStringToken: no change.
    # skipWsToken: no change.

    #@+node:ekr.20140723122936.18127: *3* skipId (override base class) & helper
    #@+at  For characters valid in names see:
    #    www.w3.org/TR/2008/REC-xml-20081126/#NT-Name
    #@@c

    def skipId (self,s,i):

        if 1:
            # Fix bug 501636: Leo's import code should support non-ascii xml tags.
            if i < len(s) and self.isWordChar1(s[i]):
                i += 1
            else:
                return i
            while i < len(s) and self.isWordChar2(s[i]):
                i += 1
            return i
        else:
            # Fix bug 497332: @data import_xml_tags does not allow dashes in tag.
            chars = '.-:' # Allow : anywhere.
            while i < len(s) and (self.isWordChar(s[i]) or s[i] in chars):
                i += 1
            return i
    #@+node:ekr.20140723122936.18128: *4* isWordChar (XmlScanner) To be replaced
    def isWordChar (self,ch):

        '''This allows only ascii tags.'''

        # Same as g.isWordChar. This is not correct.
        return ch and (ch.isalnum() or ch == '_')
    #@+node:ekr.20140723122936.18129: *4* isWordChar1 (XmlScanner)
    #@+at From www.w3.org/TR/2008/REC-xml-20081126/#NT-Name
    # 
    # NameStartChar    ::= ":" | [A-Z] | "_" | [a-z] |
    #     [#xC0-#xD6]     | [#xD8-#xF6]     | [#xF8-#x2FF]    |
    #     [#x370-#x37D]   | [#x37F-#x1FFF]  | [#x200C-#x200D] |
    #     [#x2070-#x218F] | [#x2C00-#x2FEF] | [#x3001-#xD7FF] |
    #     [#xF900-#xFDCF] | [#xFDF0-#xFFFD] | [#x10000-#xEFFFF]
    #@@c

    word_char_table1 = (
        (0xC0,  0xD6),    (0xD8,  0xF6),    (0xF8,  0x2FF),
        (0x370, 0x37D),   (0x37F, 0x1FFF),  (0x200C,0x200D),
        (0x2070,0x218F),  (0x2C00,0x2FEF),  (0x3001,0xD7FF),
        (0xF900,0xFDCF),  (0xFDF0,0xFFFD),  (0x10000,0xEFFFF),
    )

    def isWordChar1(self,ch):

        if not ch: return False

        if ch.isalnum() or ch in '_:': return True

        n = ord(ch)
        for n1,n2 in self.word_char_table1:
            if n1 <= n <= n2:
                return True

        return False
    #@+node:ekr.20140723122936.18130: *4* isWordChar2 (XmlScanner)
    #@+at From www.w3.org/TR/2008/REC-xml-20081126/#NT-Name
    # 
    # NameChar    ::= NameStartChar | "-" | "." | [0-9] | #xB7 |
    #     [#x0300-#x036F] | [#x203F-#x2040]
    #@@c

    word_char_table2 = (
        (0xB7,      0xB7),  # Middle dot.
        (0x0300,    0x036F),
        (0x203F,    0x2040),
    )

    def isWordChar2(self,ch):

        if not ch: return False

        if self.isWordChar1(ch) or ch in "-.0123456789":
            return True

        n = ord(ch)
        for n1,n2 in self.word_char_table2:
            if n1 <= n <= n2:
                return True

        return False
    #@+node:ekr.20140723122936.18131: *3* startsHelper & helpers (XmlScanner)
    def startsHelper(self,s,i,kind,tags,tag=None):
        '''return True if s[i:] starts a class or function.
        Sets sigStart, sigEnd, sigId and codeEnd ivars.'''

        trace = (False and kind == 'class') # and not g.unitTesting
        verbose = True
        self.codeEnd = self.sigEnd = self.sigId = None

        # Underindented lines can happen in any language, not just Python.
        # The skipBlock method of the base class checks for such lines.
        self.startSigIndent = self.getLeadingIndent(s,i)

        # Get the tag that starts the class or function.
        if not g.match(s,i,'<'): return False
        self.sigStart = i
        i += 1
        sigIdStart = j = g.skip_ws_and_nl(s,i)
        i = self.skipId(s,j)

        # Fix bug 501636: Leo's import code should support non-ascii xml tags.
        # The call to g.toUnicode only needed on Python 2.x.
        self.sigId = theId = g.toUnicode(s[j:i].lower())
            # Set sigId ivar 'early' for error messages.
            # Bug fix: html case does not matter.
        if not theId: return False

        if theId not in tags:
            if trace and verbose:
                g.trace('**** %s theId: %s not in tags: %s' % (
                    kind,theId,tags))
            return False

        if trace and verbose: g.trace(theId)
        classId = '' 
        sigId = theId

        # Complete the opening tag.
        i, ok, complete = self.skipToEndOfTag(s,i,start=sigIdStart)
        if not ok:
            if trace and verbose: g.trace('no tail',g.get_line(s,i))
            return False
        sigEnd = i

        # Bug fix: 2011/11/05.
        # For xml/html, make sure the signature includes any trailing whitespace.
        if not g.match(s,sigEnd,'\n') and not g.match(s,sigEnd-1,'\n'):
            # sigEnd = g.skip_line(s,sigEnd)
            sigEnd = g.skip_ws(s,sigEnd)

        if not complete:
            i,ok = self.skipToMatchingTag(s,i,theId,tags,start=sigIdStart)
            if not ok:
                if trace and verbose: g.trace('no matching tag:',theId)
                return False

        # Success: set the ivars.
        # Not used in xml/html.
        # self.sigStart = self.adjustDefStart(s,self.sigStart)
        self.codeEnd = i
        self.sigEnd = sigEnd
        self.sigId = sigId
        self.classId = classId

        # Scan to the start of the next tag.
        done = False
        while not done and i < len(s):
            progress = i
            if self.startsComment(s,i):
                i = self.skipComment(s,i)
            elif self.startsString(s,i):
                i = self.skipString(s,i)
            elif s[i] == '<':
                start = i
                i += 1
                if i < len(s) and s[i] == '/':
                    i += 1
                j = g.skip_ws_and_nl(s,i)
                if self.startsId(s,j):
                    i = self.skipId(s,j)
                    word = s[j:i].lower()
                    if word in tags:
                        self.codeEnd = start
                        done = True
                        break
                else:
                    i = j
            else:
                i += 1

            assert done or progress < i,'i: %d, ch: %s' % (i,repr(s[i]))

        if trace: g.trace(repr(s[self.sigStart:self.codeEnd]))
        return True
    #@+node:ekr.20140723122936.18132: *4* skipToEndOfTag (XmlScanner)
    def skipToEndOfTag(self,s,i,start):

        '''Skip to the end of an open tag.

        return i,ok,complete

        where complete is True if the tag of the form <name/>
        '''

        trace = False
        complete,ok = False,False
        while i < len(s): 
            progress = i
            if i == '"':
                i = self.skipString(s,i)
            elif g.match(s,i,'<!--'):
                i = self.skipComment(s,i)
            elif g.match(s,i,'<'):
                complete,ok = False,False ; break
            elif g.match(s,i,'/>'):
                i = g.skip_ws(s,i+2)
                complete,ok = True,True ; break
            elif g.match(s,i,'>'):
                i += 1
                complete,ok = False,True ; break
            else:
                i += 1
            assert progress < i

        if trace: g.trace('ok',ok,repr(s[start:i]))
        return i,ok,complete
    #@+node:ekr.20140723122936.18133: *4* skipToMatchingTag (XmlScanner)
    def skipToMatchingTag (self,s,i,tag,tags,start):

        '''Skip the entire class definition. Return i,ok.
        '''

        trace = False
        found,level,target_tag = False,1,tag.lower()
        while i < len(s): 
            progress = i
            if s[i] == '"':
                i = self.skipString(s,i)
            elif g.match(s,i,'<!--'):
                i = self.skipComment(s,i)
            elif g.match(s,i,'</'):
                j = i+2
                i = self.skipId(s,j)
                tag2 = s[j:i].lower()
                i,ok,complete = self.skipToEndOfTag(s,i,start=j)
                    # Sets complete if /> terminates the tag.
                if ok and tag2 == target_tag:
                    level -= 1
                    if level == 0:
                        found = True ; break
            elif g.match(s,i,'<'):
                # An open tag.
                j = g.skip_ws_and_nl(s,i+1)
                i = self.skipId(s,j)
                word = s[j:i].lower()
                i,ok,complete = self.skipToEndOfTag(s,i,start=j)
                # **Important**: only bump level for nested *target* tags.
                # This avoids problems when interior tags are not properly nested.
                if ok and word == target_tag and not complete:
                    level += 1
            elif g.match(s,i,'/>'):
                # This is a syntax error.
                # This should have been eaten by skipToEndOfTag.
                i += 2
                g.trace('syntax error: unmatched "/>"')
            else:
                i += 1

            assert progress < i

        if trace: g.trace('%sfound:%s\n%s\n\n*****end %s\n' % (
            '' if found else 'not ',target_tag,s[start:i],target_tag))

        return i,found
    #@+node:ekr.20140723122936.18134: *3* startsId (XmlScanner)
    def startsId(self,s,i):

        # Fix bug 501636: Leo's import code should support non-ascii xml tags.
        return i < len(s) and self.isWordChar1(s[i])
    #@+node:ekr.20140723122936.18135: *3* startsString (XmlScanner)
    def startsString(self,s,i):
            
        '''Single quotes do *not* start strings in xml or html.'''
        
        # Fix bug 1208659: leo parsed the wrong line number of html file.
        # Note: the compare failure was caused by using BaseScanner.startsString.
        # The line number problem is a separate issue.
        return g.match(s,i,'"')
    #@-others
#@-others
importer_dict = {
    'class': XmlScanner,
    'extensions': ['.xml',],
}
#@-leo
