# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20160316095222.1: * @file ../commands/convertCommands.py
#@@first
'''Leo's file-conversion commands.'''
import leo.core.leoGlobals as g
from leo.commands.baseCommands import BaseEditCommandsClass as BaseEditCommandsClass

def cmd(name):
    '''Command decorator for the ConvertCommandsClass class.'''
    return g.new_cmd_decorator(name, ['c', 'convertCommands',])

#@+<< class To_Python >>
#@+node:ekr.20150514063305.123: ** << class To_Python >>
class To_Python:
    '''The base class for x-to-python commands.'''
    #@+others
    #@+node:ekr.20150514063305.124: *3* top.cmd (decorator
    #@+node:ekr.20150514063305.125: *3* ctor (To_Python)
    def __init__(self, c):
        '''Ctor for To_Python class.'''
        self.c = c
        self.p = self.c.p.copy()
        aList = g.get_directives_dict_list(self.p)
        self.tab_width = g.scanAtTabwidthDirectives(aList) or 4
    #@+node:ekr.20150514063305.126: *3* go
    def go(self):
        import time
        t1 = time.time()
        c = self.c
        u, undoType = c.undoer, 'typescript-to-python'
        pp = c.CPrettyPrinter(c)
        u.beforeChangeGroup(c.p, undoType)
        changed, dirtyVnodeList = False, []
        n_files, n_nodes = 0, 0
        special = ('class ', 'module ', '@file ', '@@file ')
        files = ('@file ', '@@file ')
        for p in self.p.self_and_subtree():
            if p.b:
                n_nodes += 1
                if any([p.h.startswith(z) for z in special]):
                    g.es_print(p.h)
                    if any([p.h.startswith(z) for z in files]):
                        n_files += 1
                bunch = u.beforeChangeNodeContents(p)
                s = pp.indent(p, giveWarnings=False)
                aList = list(s)
                self.convertCodeList(aList)
                s = ''.join(aList)
                if s != p.b:
                    p.b = s
                    p.v.setDirty()
                    dirtyVnodeList.append(p.v)
                    u.afterChangeNodeContents(p, undoType, bunch)
                    changed = True
        # Call this only once, at end.
        if changed:
            u.afterChangeGroup(c.p, undoType,
                reportFlag=False, dirtyVnodeList=dirtyVnodeList)
        t2 = time.time()
        g.es_print('done! %s files, %s nodes, %2.2f sec' % (n_files, n_nodes, t2 - t1))
    #@+node:ekr.20150514063305.127: *3* convertCodeList (must be defined in subclasses)
    def convertCodeList(self, aList):
        '''The main search/replace method.'''
        g.trace('must be defined in subclasses.')
    #@+node:ekr.20150514063305.128: *3* Utils
    #@+node:ekr.20150514063305.129: *4* match...
    #@+node:ekr.20150514063305.130: *5* match
    def match(self, s, i, pat):
        '''
        Return True if s[i:] matches the pat string.

        We can't use g.match because s is usually a list.
        '''
        assert pat
        j = 0
        while i + j < len(s) and j < len(pat):
            if s[i + j] == pat[j]:
                j += 1
                if j == len(pat):
                    return True
            else:
                return False
        return False
    #@+node:ekr.20150514063305.131: *5* match_word
    def match_word(self, s, i, pat):
        '''
        Return True if s[i:] word matches the pat string.

        We can't use g.match_word because s is usually a list
        and g.match_word uses s.find.
        '''
        if self.match(s, i, pat):
            j = i + len(pat)
            if j >= len(s):
                return True
            elif not pat[-1].isalnum():
                # Bug fix 10/16/2012: The pattern terminates the word.
                return True
            else:
                ch = s[j]
                return not ch.isalnum() and ch != '_'
        else:
            return False
    #@+node:ekr.20150514063305.132: *4* insert_not
    def insert_not(self, aList):
        '''Change "!" to "not" except before "="'''
        i = 0
        while i < len(aList):
            if self.is_string_or_comment(aList, i):
                i = self.skip_string_or_comment(aList, i)
            elif aList[i] == '!' and not self.match(aList, i + 1, '='):
                aList[i: i + 1] = list('not ')
                i += 4
            else:
                i += 1
    #@+node:ekr.20150514063305.133: *4* is...
    #@+node:ekr.20150514063305.134: *5* is_section_def/ref
    def is_section_def(self, p):
        return self.is_section_ref(p.h)

    def is_section_ref(self, s):
        n1 = s.find("<<", 0)
        n2 = s.find(">>", 0)
        return -1 < n1 < n2 and s[n1 + 2: n2].strip()
    #@+node:ekr.20150514063305.135: *5* is_string_or_comment
    def is_string_or_comment(self, s, i):
        # Does range checking.
        m = self.match
        return m(s, i, "'") or m(s, i, '"') or m(s, i, "//") or m(s, i, "/*")
    #@+node:ekr.20150514063305.136: *5* is_ws and is_ws_or_nl
    def is_ws(self, ch):
        return ch in ' \t'

    def is_ws_or_nl(self, ch):
        return ch in ' \t\n'
    #@+node:ekr.20150514063305.137: *4* prevNonWsChar and prevNonWsOrNlChar
    def prevNonWsChar(self, s, i):
        i -= 1
        while i >= 0 and self.is_ws(s[i]):
            i -= 1
        return i

    def prevNonWsOrNlChar(self, s, i):
        i -= 1
        while i >= 0 and self.is_ws_or_nl(s[i]):
            i -= 1
        return i
    #@+node:ekr.20150514063305.138: *4* remove...
    #@+node:ekr.20150514063305.139: *5* removeBlankLines
    def removeBlankLines(self, aList):
        i = 0
        while i < len(aList):
            j = i
            while j < len(aList) and aList[j] in " \t":
                j += 1
            if j == len(aList) or aList[j] == '\n':
                del aList[i: j + 1]
            else:
                i = self.skip_past_line(aList, i)
    #@+node:ekr.20150514063305.140: *5* removeExcessWs
    def removeExcessWs(self, aList):
        i = 0
        i = self.removeExcessWsFromLine(aList, i)
        while i < len(aList):
            if self.is_string_or_comment(aList, i):
                i = self.skip_string_or_comment(aList, i)
            elif self.match(aList, i, '\n'):
                i += 1
                i = self.removeExcessWsFromLine(aList, i)
            else: i += 1
    #@+node:ekr.20150514063305.141: *5* removeExessWsFromLine
    def removeExcessWsFromLine(self, aList, i):
        assert(i == 0 or aList[i - 1] == '\n')
        i = self.skip_ws(aList, i)
            # Retain the leading whitespace.
        while i < len(aList):
            if self.is_string_or_comment(aList, i):
                break # safe
            elif self.match(aList, i, '\n'):
                break
            elif self.match(aList, i, ' ') or self.match(aList, i, '\t'):
                # Replace all whitespace by one blank.
                j = self.skip_ws(aList, i)
                assert(j > i)
                aList[i: j] = [' ']
                i += 1 # make sure we don't go past a newline!
            else: i += 1
        return i
    #@+node:ekr.20150514063305.142: *5* removeMatchingBrackets
    def removeMatchingBrackets(self, aList, i):
        j = self.skip_to_matching_bracket(aList, i)
        if j > i and j < len(aList):
            # print "del brackets:", ''.join(aList[i:j+1])
            c = aList[j]
            if c == ')' or c == ']' or c == '}':
                del aList[j: j + 1]
                del aList[i: i + 1]
                # print "returning:", ''.join(aList[i:j])
                return j - 1
            else: return j + 1
        else: return j
    #@+node:ekr.20150514063305.143: *5* removeSemicolonsAtEndOfLines
    def removeSemicolonsAtEndOfLines(self, aList):
        i = 0
        while i < len(aList):
            if self.is_string_or_comment(aList, i):
                i = self.skip_string_or_comment(aList, i)
            elif aList[i] == ';':
                j = self.skip_ws(aList, i + 1)
                if (
                    j >= len(aList) or
                    self.match(aList, j, '\n') or
                    self.match(aList, j, '#') or
                    self.match(aList, j, "//")
                ):
                    del aList[i]
                else: i += 1
            else: i += 1
    #@+node:ekr.20150514063305.144: *5* removeTrailingWs
    def removeTrailingWs(self, aList):
        i = 0
        while i < len(aList):
            if self.is_ws(aList[i]):
                j = i
                i = self.skip_ws(aList, i)
                assert(j < i)
                if i >= len(aList) or aList[i] == '\n':
                    # print "removing trailing ws:", `i-j`
                    del aList[j: i]
                    i = j
            else: i += 1
    #@+node:ekr.20150514063305.145: *4* replace... & safe_replace
    #@+node:ekr.20150514063305.146: *5* replace
    def replace(self, aList, findString, changeString):
        '''
        Replaces all occurances of findString by changeString.
        changeString may be the empty string, but not None.
        '''
        if not findString:
            return
        changeList = list(changeString)
        i = 0
        while i < len(aList):
            if self.match(aList, i, findString):
                aList[i: i + len(findString)] = changeList
                i += len(changeList)
            else:
                i += 1
    #@+node:ekr.20150514063305.147: *5* replaceComments
    def replaceComments(self, aList):
        i = 0
        while i < len(aList):
            # Loop invariant: j > progress at end.
            progress = i
            if self.match(aList, i, "//"):
                aList[i: i + 2] = ['#']
                j = self.skip_past_line(aList, i)
            elif self.match(aList, i, "/*"):
                j = self.skip_c_block_comment(aList, i)
                k = i
                while k - 1 >= 0 and aList[k - 1] in ' \t':
                    k -= 1
                assert k == 0 or aList[k - 1] not in ' \t'
                lws = ''.join(aList[k: i])
                comment_body = ''.join(aList[i + 2: j - 2])
                comment_lines = g.splitLines(lws + comment_body)
                comment_lines = self.munge_block_comment(comment_lines)
                comment = '\n'.join(comment_lines) # A list of lines.
                comment_list = list(comment) # A list of characters.
                aList[k: j] = comment_list
                j = k + len(comment_list)
                progress = j - 1 # Disable the check below.
            elif self.match(aList, i, '"') or self.match(aList, i, "'"):
                j = self.skip_string(aList, i)
            else:
                j = i + 1
            # Defensive programming.
            if j == progress:
                j += 1
            assert j > progress
            i = j
    #@+node:ekr.20150514063305.148: *6* munge_block_comment
    def munge_block_comment(self, comment_lines):
        trace = False
        n = len(comment_lines)
        assert n > 0
        s = comment_lines[0]
        junk, w = g.skip_leading_ws_with_indent(s, 0, tab_width=4)
        if n == 1:
            return ['%s# %s' % ((' ' * (w - 1)), s.strip())]
        junk, w = g.skip_leading_ws_with_indent(s, 0, tab_width=4)
        i, result = 0, []
        for i in range(len(comment_lines)):
            s = comment_lines[i]
            if s.strip():
                result.append('%s# %s' % ((' ' * w), s.strip()))
            elif i == n - 1:
                pass # Omit the line entirely.
            else:
                result.append('') # Add a blank line
        if trace:
            g.trace()
            for z in result: print(repr(z))
        return result
    #@+node:ekr.20150514063305.149: *5* replaceSectionDefs
    def replaceSectionDefs(self, aList):
        '''Replaces < < x > > = by @c (at the start of lines).'''
        if not aList:
            return
        i = 0
        j = self.is_section_def(aList[i])
        if j > 0: aList[i: j] = list("@c ")
        while i < len(aList):
            if self.is_string_or_comment(aList, i):
                i = self.skip_string_or_comment(aList, i)
            elif self.match(aList, i, "\n"):
                i += 1
                j = self.is_section_def(aList[i])
                if j > i: aList[i: j] = list("@c ")
            else: i += 1
    #@+node:ekr.20150514063305.150: *5* safe_replace
    def safe_replace(self, aList, findString, changeString):
        '''
        Replaces occurances of findString by changeString,
        but only outside of C comments and strings.
        changeString may be the empty string, but not None.
        '''
        if not findString:
            return
        changeList = list(changeString)
        i = 0
        if findString[0].isalpha(): # use self.match_word
            while i < len(aList):
                if self.is_string_or_comment(aList, i):
                    i = self.skip_string_or_comment(aList, i)
                elif self.match_word(aList, i, findString):
                    aList[i: i + len(findString)] = changeList
                    i += len(changeList)
                else:
                    i += 1
        else: #use self.match
            while i < len(aList):
                if self.match(aList, i, findString):
                    aList[i: i + len(findString)] = changeList
                    i += len(changeList)
                else:
                    i += 1
    #@+node:ekr.20150514063305.151: *4* skip
    #@+node:ekr.20150514063305.152: *5* skip_c_block_comment
    def skip_c_block_comment(self, s, i):
        assert(self.match(s, i, "/*"))
        i += 2
        while i < len(s):
            if self.match(s, i, "*/"):
                return i + 2
            else:
                i += 1
        return i
    #@+node:ekr.20150514063305.153: *5* skip_line
    def skip_line(self, s, i):
        while i < len(s) and s[i] != '\n':
            i += 1
        return i
    #@+node:ekr.20150514063305.154: *5* skip_past_line
    def skip_past_line(self, s, i):
        while i < len(s) and s[i] != '\n':
            i += 1
        if i < len(s) and s[i] == '\n':
            i += 1
        return i
    #@+node:ekr.20150514063305.155: *5* skip_past_word
    def skip_past_word(self, s, i):
        assert(s[i].isalpha() or s[i] == '~')
        # Kludge: this helps recognize dtors.
        if s[i] == '~':
            i += 1
        while i < len(s):
            ch = s[i]
            if ch.isalnum() or ch == '_':
                i += 1
            else:
                break
        return i
    #@+node:ekr.20150514063305.156: *5* skip_string
    def skip_string(self, s, i):
        delim = s[i] # handle either single or double-quoted strings
        assert(delim == '"' or delim == "'")
        i += 1
        while i < len(s):
            if s[i] == delim:
                return i + 1
            elif s[i] == '\\':
                i += 2
            else:
                i += 1
        return i
    #@+node:ekr.20150514063305.157: *5* skip_string_or_comment
    def skip_string_or_comment(self, s, i):
        if self.match(s, i, "'") or self.match(s, i, '"'):
            j = self.skip_string(s, i)
        elif self.match(s, i, "//"):
            j = self.skip_past_line(s, i)
        elif self.match(s, i, "/*"):
            j = self.skip_c_block_comment(s, i)
        else:
            assert(0)
        return j
    #@+node:ekr.20150514063305.158: *5* skip_to_matching_bracket
    def skip_to_matching_bracket(self, s, i):
        ch = s[i]
        if ch == '(': delim = ')'
        elif ch == '{': delim = '}'
        elif ch == '[': delim = ']'
        else: assert(0)
        i += 1
        while i < len(s):
            ch = s[i]
            if self.is_string_or_comment(s, i):
                i = self.skip_string_or_comment(s, i)
            elif ch == delim:
                return i
            elif ch == '(' or ch == '[' or ch == '{':
                i = self.skip_to_matching_bracket(s, i)
                i += 1 # skip the closing bracket.
            else: i += 1
        return i
    #@+node:ekr.20150514063305.159: *5* skip_ws and skip_ws_and_nl
    def skip_ws(self, aList, i):
        while i < len(aList):
            c = aList[i]
            if c == ' ' or c == '\t':
                i += 1
            else: break
        return i

    def skip_ws_and_nl(self, aList, i):
        while i < len(aList):
            c = aList[i]
            if c == ' ' or c == '\t' or c == '\n':
                i += 1
            else: break
        return i
    #@-others
#@-<< class To_Python >>
#@+others
#@+node:ekr.20160316111303.1: ** class ConvertCommandsClass
class ConvertCommandsClass(BaseEditCommandsClass):
    '''Leo's file-conversion commands'''
    
    def __init__(self, c):
        '''Ctor for EditCommandsClass class.'''
        # pylint: disable=super-init-not-called
        self.c = c

    #@+others
    #@+node:ekr.20160316091843.1: *3* ccc.c-to-python
    @cmd('c-to-python')
    def cToPy(self, event):
        '''
        The c-to-python command converts c or c++ text to python text.
        The conversion is not perfect, but it eliminates a lot of tedious
        text manipulation.
        '''
        self.C_To_Python(self.c).go()
        self.c.bodyWantsFocus()

    #@+node:ekr.20150514063305.160: *4* class C_To_Python (To_Python)
    class C_To_Python(To_Python):
        #@+others
        #@+node:ekr.20150514063305.161: *5* ctor & helpers (C_To_Python)
        def __init__(self, c):
            '''Ctor for C_To_Python class.'''
            # pylint: disable=super-init-not-called
            c.convertCommands.To_Python.__init__(self, c)
                # init the base class
            # Internal state...
            self.class_name = ''
                # The class name for the present function.  Used to modify ivars.
            self.ivars = []
                # List of ivars to be converted to self.ivar
            self.get_user_types()
        #@+node:ekr.20150514063305.162: *6* get_user_types
        def get_user_types(self):
            c = self.c
            self.class_list = c.config.getData('c-to-python-class-list') or []
            self.type_list = (
                c.config.getData('c-to-python-type-list') or
                ["char", "void", "short", "long", "int", "double", "float"]
            )
            aList = c.config.getData('c-to-python-ivars-dict')
            if aList:
                self.ivars_dict = self.parse_ivars_data(aList)
            else:
                self.ivars_dict = {}
            if 0:
                #g.trace('class_list',self.class_list)
                #g.trace('type_list',self.type_list)
                g.trace('ivars_dict...')
                d = self.ivars_dict
                keys = list(d.keys())
                for key in sorted(keys):
                    print('%s:' % (key))
                    for val in d.get(key):
                        print('  %s' % (val))
        #@+node:ekr.20150514063305.163: *6* parse_ivars_data
        def parse_ivars_data(self, aList):
            d, key = {}, None
            aList = [z.strip() for z in aList if z.strip()]
            for s in aList:
                if s.endswith(':'):
                    key = s[: -1].strip()
                elif key:
                    ivars = [z.strip() for z in s.split(',') if z.strip()]
                    aList = d.get(key, [])
                    aList.extend(ivars)
                    d[key] = aList
                else:
                    g.error('invalid @data c-to-python-ivars-dict', repr(s))
                    return {}
            return d
        #@+node:ekr.20150514063305.164: *5* convertCodeList (C_To_Python) & helpers
        def convertCodeList(self, aList):
            r, sr = self.replace, self.safe_replace
            # First...
            r(aList, "\r", '')
            # self.convertLeadingBlanks(aList) # Now done by indent.
            # if leoFlag: replaceSectionDefs(aList)
            self.mungeAllFunctions(aList)
            # Next...
            if 1:
                # CC2 stuff:
                sr(aList, "TRACEPB", "if trace: g.trace")
                sr(aList, "TRACEPN", "if trace: g.trace")
                sr(aList, "TRACEPX", "if trace: g.trace")
                sr(aList, "TICKB", "if trace: g.trace")
                sr(aList, "TICKN", "if trace: g.trace")
                sr(aList, "TICKX", "if trace: g.trace")
                sr(aList, "g.trace(ftag,", "g.trace(")
                sr(aList, "ASSERT_TRACE", "assert")
            sr(aList, "ASSERT", "assert")
            sr(aList, " -> ", '.')
            sr(aList, "->", '.')
            sr(aList, " . ", '.')
            sr(aList, "this.self", "self")
            sr(aList, "{", '')
            sr(aList, "}", '')
            sr(aList, "#if", "if")
            sr(aList, "#else", "else")
            sr(aList, "#endif", '')
            sr(aList, "else if", "elif")
            sr(aList, "else", "else:")
            sr(aList, "&&", " and ")
            sr(aList, "||", " or ")
            sr(aList, "TRUE", "True")
            sr(aList, "FALSE", "False")
            sr(aList, "NULL", "None")
            sr(aList, "this", "self")
            sr(aList, "try", "try:")
            sr(aList, "catch", "except:")
            # if leoFlag: sr(aList, "@code", "@c")
            # Next...
            self.handle_all_keywords(aList)
            self.insert_not(aList)
            self.removeSemicolonsAtEndOfLines(aList)
                # after processing for keywords
            # Last...
            # if firstPart and leoFlag: removeLeadingAtCode(aList)
            self.removeBlankLines(aList)
            self.removeExcessWs(aList)
            # your taste may vary: in Python I don't like extra whitespace
            sr(aList, " :", ":")
            sr(aList, ", ", ",")
            sr(aList, " ,", ",")
            sr(aList, " (", "(")
            sr(aList, "( ", "(")
            sr(aList, " )", ")")
            sr(aList, ") ", ")")
            sr(aList, "@language c", "@language python")
            self.replaceComments(aList) # should follow all calls to safe_replace
            self.removeTrailingWs(aList)
            r(aList, "\t ", "\t") # happens when deleting declarations.
        #@+node:ekr.20150514063305.165: *6* handle_all_keywords
        def handle_all_keywords(self, aList):
            '''
            converts if ( x ) to if x:
            converts while ( x ) to while x:
            '''
            i = 0
            while i < len(aList):
                if self.is_string_or_comment(aList, i):
                    i = self.skip_string_or_comment(aList, i)
                elif(
                    self.match_word(aList, i, "if") or
                    self.match_word(aList, i, "while") or
                    self.match_word(aList, i, "for") or
                    self.match_word(aList, i, "elif")
                ):
                    i = self.handle_keyword(aList, i)
                else:
                    i += 1
            # print "handAllKeywords2:", ''.join(aList)
        #@+node:ekr.20150514063305.166: *7* handle_keyword
        def handle_keyword(self, aList, i):
            if self.match_word(aList, i, "if"):
                i += 2
            elif self.match_word(aList, i, "elif"):
                i += 4
            elif self.match_word(aList, i, "while"):
                i += 5
            elif self.match_word(aList, i, "for"):
                i += 3
            else: assert(0)
            # Make sure one space follows the keyword.
            k = i
            i = self.skip_ws(aList, i)
            if k == i:
                c = aList[i]
                aList[i: i + 1] = [' ', c]
                i += 1
            # Remove '(' and matching ')' and add a ':'
            if aList[i] == "(":
                # Look ahead.  Don't remove if we span a line.
                j = self.skip_to_matching_bracket(aList, i)
                k = i
                found = False
                while k < j and not found:
                    found = aList[k] == '\n'
                    k += 1
                if not found:
                    j = self.removeMatchingBrackets(aList, i)
                if j > i and j < len(aList):
                    ch = aList[j]
                    aList[j: j + 1] = [ch, ":", " "]
                    j = j + 2
                return j
            return i
        #@+node:ekr.20150514063305.167: *6* mungeAllFunctions
        def mungeAllFunctions(self, aList):
            '''Scan for a '{' at the top level that is preceeded by ')' '''
            prevSemi = 0 # Previous semicolon: header contains all previous text
            i = 0
            firstOpen = None
            while i < len(aList):
                progress = i
                if self.is_string_or_comment(aList, i):
                    j = self.skip_string_or_comment(aList, i)
                    prevSemi = j
                elif self.match(aList, i, '('):
                    if not firstOpen:
                        firstOpen = i
                    j = i + 1
                elif self.match(aList, i, '#'):
                    # At this point, it is a preprocessor directive.
                    j = self.skip_past_line(aList, i)
                    prevSemi = j
                elif self.match(aList, i, ';'):
                    j = i + 1
                    prevSemi = j
                elif self.match(aList, i, "{"):
                    j = self.handlePossibleFunctionHeader(aList, i, prevSemi, firstOpen)
                    prevSemi = j
                    firstOpen = None # restart the scan
                    # g.trace(repr(''.join(aList[prevSemi:prevSemi+20])))
                else:
                    j = i + 1
                # Handle unusual cases.
                if j <= progress:
                    j = progress + 1
                assert j > progress
                i = j
        #@+node:ekr.20150514063305.168: *7* handlePossibleFunctionHeader
        def handlePossibleFunctionHeader(self, aList, i, prevSemi, firstOpen):
            '''
            Converts function header lines from c++ format to python format.
            That is, converts
                x1..nn w::y ( t1 z1,..tn zn) {
            to
                def y (z1,..zn): {
            '''
            trace = False
            assert(self.match(aList, i, "{"))
            prevSemi = self.skip_ws_and_nl(aList, prevSemi)
            close = self.prevNonWsOrNlChar(aList, i)
            if close < 0 or aList[close] != ')':
                # Should not increase *Python* indent.
                return 1 + self.skip_to_matching_bracket(aList, i)
            if not firstOpen:
                return 1 + self.skip_to_matching_bracket(aList, i)
            close2 = self.skip_to_matching_bracket(aList, firstOpen)
            if close2 != close:
                return 1 + self.skip_to_matching_bracket(aList, i)
            open_paren = firstOpen
            assert(aList[open_paren] == '(')
            head = aList[prevSemi: open_paren]
            # do nothing if the head starts with "if", "for" or "while"
            k = self.skip_ws(head, 0)
            if k >= len(head) or not head[k].isalpha():
                return 1 + self.skip_to_matching_bracket(aList, i)
            kk = self.skip_past_word(head, k)
            if kk > k:
                headString = ''.join(head[k: kk])
                # C keywords that might be followed by '{'
                # print "headString:", headString
                if headString in ["class", "do", "for", "if", "struct", "switch", "while"]:
                    return 1 + self.skip_to_matching_bracket(aList, i)
            args = aList[open_paren: close + 1]
            k = 1 + self.skip_to_matching_bracket(aList, i)
            body = aList[close + 1: k]
            if True and trace:
                g.trace('\nhead: %s\nargs: %s\nbody: %s' % (
                    ''.join(head), ''.join(args), ''.join(body)))
            head = self.massageFunctionHead(head)
            args = self.massageFunctionArgs(args)
            body = self.massageFunctionBody(body)
            if False and trace:
                g.trace('\nhead2: %s\nargs2: %s\nbody2: %s' % (
                    ''.join(head), ''.join(args), ''.join(body)))
            result = []
            if head: result.extend(head)
            if args: result.extend(args)
            if body: result.extend(body)
            aList[prevSemi: k] = result
            return prevSemi + len(result)
        #@+node:ekr.20150514063305.169: *7* massageFunctionArgs
        def massageFunctionArgs(self, args):
            assert(args[0] == '(')
            assert(args[-1] == ')')
            result = ['(']
            lastWord = []
            if self.class_name:
                for item in list("self,"): result.append(item) #can put extra comma
            i = 1
            while i < len(args):
                i = self.skip_ws_and_nl(args, i)
                c = args[i]
                if c.isalpha():
                    j = self.skip_past_word(args, i)
                    lastWord = args[i: j]
                    i = j
                elif c == ',' or c == ')':
                    for item in lastWord:
                        result.append(item)
                    if lastWord != [] and c == ',':
                        result.append(',')
                    lastWord = []
                    i += 1
                else: i += 1
            if result[-1] == ',':
                del result[-1]
            result.append(')')
            result.append(':')
            # print "new args:", ''.join(result)
            return result
        #@+node:ekr.20150514063305.170: *7* massageFunctionHead (sets .class_name)
        def massageFunctionHead(self, head):
            result = []
            prevWord = []
            self.class_name = ''
            i = 0
            # g.trace(repr(''.join(head)))
            while i < len(head):
                i = self.skip_ws_and_nl(head, i)
                if i < len(head) and head[i].isalpha():
                    result = []
                    j = self.skip_past_word(head, i)
                    prevWord = head[i: j]
                    i = j
                    # look for ::word2
                    i = self.skip_ws(head, i)
                    if self.match(head, i, "::"):
                        # Set the global to the class name.
                        self.class_name = ''.join(prevWord)
                        # print(class name:", self.class_name)
                        i = self.skip_ws(head, i + 2)
                        if i < len(head) and (head[i] == '~' or head[i].isalpha()):
                            j = self.skip_past_word(head, i)
                            if head[i: j] == prevWord:
                                result.extend('__init__')
                            elif head[i] == '~' and head[i + 1: j] == prevWord:
                                result.extend('__del__')
                            else:
                                # result.extend(list('::'))
                                result.extend(head[i: j])
                            i = j
                    else:
                        result.extend(prevWord)
                else: i += 1
            finalResult = list("def ")
            finalResult.extend(result)
            return finalResult
        #@+node:ekr.20150514063305.171: *7* massageFunctionBody & helpers
        def massageFunctionBody(self, body):
            body = self.massageIvars(body)
            body = self.removeCasts(body)
            body = self.removeTypeNames(body)
            body = self.dedentBlocks(body)
            return body
        #@+node:ekr.20150514063305.172: *8* dedentBlocks
        def dedentBlocks(self, body):
            '''Look for '{' preceded by '{' or '}' or ';'
            (with intervening whitespace and comments).
            '''
            i = 0
            while i < len(body):
                j = i
                ch = body[i]
                if self.is_string_or_comment(body, i):
                    j = self.skip_string_or_comment(body, i)
                elif ch in '{};':
                    # Look ahead ofr '{'
                    j += 1
                    while True:
                        k = j
                        j = self.skip_ws_and_nl(body, j)
                        if self.is_string_or_comment(body, j):
                            j = self.skip_string_or_comment(body, j)
                        if k == j: break
                        assert k < j
                    if self.match(body, j, '{'):
                        k = j
                        j = self.skip_to_matching_bracket(body, j)
                        # g.trace('found block\n',''.join(body[k:j+1]))
                        m = '# <Start dedented block>...'
                        body[k: k + 1] = list(m)
                        j += len(m)
                        while k < j:
                            progress = k
                            if body[k] == '\n':
                                k += 1
                                spaces = 0
                                while spaces < 4 and k < j:
                                    if body[k] == ' ':
                                        spaces += 1
                                        k += 1
                                    else:
                                        break
                                if spaces > 0:
                                    del body[k - spaces: k]
                                    k -= spaces
                                    j -= spaces
                            else:
                                k += 1
                            assert progress < k
                        m = '    # <End dedented block>'
                        body[j: j + 1] = list(m)
                        j += len(m)
                else:
                    j = i + 1
                # Defensive programming.
                if i == j:
                    j += 1
                assert i < j
                i = j
            return body
        #@+node:ekr.20150514063305.173: *8* massageIvars
        def massageIvars(self, body):
            ivars = self.ivars_dict.get(self.class_name, [])
            i = 0
            while i < len(body):
                if self.is_string_or_comment(body, i):
                    i = self.skip_string_or_comment(body, i)
                elif body[i].isalpha():
                    j = self.skip_past_word(body, i)
                    word = ''.join(body[i: j])
                    # print "looking up:", word
                    if word in ivars:
                        # replace word by self.word
                        # print "replacing", word, " by self.", word
                        word = "self." + word
                        word = list(word)
                        body[i: j] = word
                        delta = len(word) - (j - i)
                        i = j + delta
                    else: i = j
                else: i += 1
            return body
        #@+node:ekr.20150514063305.174: *8* removeCasts
        def removeCasts(self, body):
            i = 0
            while i < len(body):
                if self.is_string_or_comment(body, i):
                    i = self.skip_string_or_comment(body, i)
                elif self.match(body, i, '('):
                    start = i
                    i = self.skip_ws(body, i + 1)
                    if body[i].isalpha():
                        j = self.skip_past_word(body, i)
                        word = ''.join(body[i: j])
                        i = j
                        if word in self.class_list or word in self.type_list:
                            i = self.skip_ws(body, i)
                            while self.match(body, i, '*'):
                                i += 1
                            i = self.skip_ws(body, i)
                            if self.match(body, i, ')'):
                                i += 1
                                # print "removing cast:", ''.join(body[start:i])
                                del body[start: i]
                                i = start
                else: i += 1
            return body
        #@+node:ekr.20150514063305.175: *8* removeTypeNames
        def removeTypeNames(self, body):
            '''Do _not_ remove type names when preceeded by new.'''
            i = 0
            while i < len(body):
                if self.is_string_or_comment(body, i):
                    i = self.skip_string_or_comment(body, i)
                elif self.match_word(body, i, "new"):
                    i = self.skip_past_word(body, i)
                    i = self.skip_ws(body, i)
                    # don't remove what follows new.
                    if body[i].isalpha():
                        i = self.skip_past_word(body, i)
                elif body[i].isalpha():
                    j = self.skip_past_word(body, i)
                    word = ''.join(body[i: j])
                    if word in self.class_list or word in self.type_list:
                        j = self.skip_ws(body, j)
                        while self.match(body, j, '*'):
                            j += 1
                        # print "Deleting type name:", ''.join(body[i:j])
                        j = self.skip_ws(body, j)
                        del body[i: j]
                    else:
                        i = j
                else: i += 1
            return body
        #@-others
    #@+node:ekr.20160111190632.1: *3* ccc.makeStubFiles
    @cmd('make-stub-files')
    def make_stub_files(self, event):
        '''
        Make stub files for all nearby @<file> nodes.
        Take configuration settings from @x stub-y nodes.
        '''
        #@+others
        #@+node:ekr.20160213070235.1: *4* class MakeStubFileAdapter
        class MakeStubFileAdapter:
            '''
            An class that adapts leo/external/make_stub_files.py to Leo.

            Settings are taken from Leo settings nodes, not a .cfg file.
            '''
            #@+others
            #@+node:ekr.20160213070235.2: *5* msf.ctor & helpers
            def __init__(self, c):
                '''MakeStubFile.ctor. From StandAloneMakeStubFile.ctor.'''
                self.c = c
                self.msf = msf = g.importExtension(moduleName='make_stub_files',
                    pluginName=None, verbose=False, required=False)
                x = msf.StandAloneMakeStubFile()
                    # x is used *only* to init ivars.
                # Ivars set on the command line...
                self.config_fn = None
                self.enable_unit_tests = False
                self.files = [] # May also be set in the config file.
                self.output_directory = self.finalize(
                    c.config.getString('stub-output-directory') or '.')
                self.output_fn = None
                self.overwrite = c.config.getBool('stub-overwrite', default=False)
                self.trace_matches =  c.config.getBool('stub-trace-matches', default = False)
                self.trace_patterns =  c.config.getBool('stub-trace-patterns', default = False)
                self.trace_reduce =  c.config.getBool('stub-trace-reduce', default = False)
                self.trace_visitors =  c.config.getBool('stub-trace-visitors', default = False)
                self.update_flag = c.config.getBool('stub-update', default = False)
                self.verbose =  c.config.getBool('stub-verbose', default = False)
                self.warn =  c.config.getBool('stub-warn', default = False)
                # Pattern lists & dicts, set by config sections...
                self.patterns_dict = {}
                self.names_dict = {}
                self.def_patterns = self.scan_patterns('stub-def-name-patterns')
                self.general_patterns = self.scan_patterns('stub-general-patterns')
                self.prefix_lines = self.scan('stub-prefix-lines')
                self.regex_patterns = self.scan_patterns('stub-regex-patterns')
                # Complete the dicts.
                x.make_patterns_dict()
                self.patterns_dict = x.patterns_dict
                self.op_name_dict = x.op_name_dict = x.make_op_name_dict()
                # Copy the ivars.
                x.def_patterns = self.def_patterns
                x.general_patterns = self.general_patterns
                x.regex_patterns = self.regex_patterns
                x.prefix_lines = self.prefix_lines
            #@+node:ekr.20160213070235.3: *6* msf.scan
            def scan(self, kind):
                '''Return a list of *all* lines from an @data node, including comments.'''
                c = self.c
                aList = c.config.getData(kind,
                    strip_comments=False,
                    strip_data=False)
                if not aList:
                    g.trace('warning: no @data %s node' % kind)
                return aList
            #@+node:ekr.20160213070235.4: *6* msf.scan_d
            def scan_d(self, kind):
                '''Return a dict created from an @data node of the given kind.'''
                trace = False and not g.unitTesting
                c = self.c
                aList = c.config.getData(kind, strip_comments=True, strip_data=True)
                d = {}
                if aList is None:
                    g.trace('warning: no @data %s node' % kind)
                for s in aList or []:
                    name, value = s.split(':',1)
                    # g.trace('name',name,'value',value)
                    d[name.strip()] = value.strip()
                if trace:
                    print('@data %s...' % kind)
                    for key in sorted(d.keys()):
                        print('  %s: %s' % (key, d.get(key)))
                return d
            #@+node:ekr.20160213070235.5: *6* msf.scan_patterns
            def scan_patterns(self, kind):
                '''Parse the config section into a list of patterns, preserving order.'''
                trace = False or self.trace_patterns
                d = self.scan_d(kind)
                aList = []
                seen = set()
                for key in d:
                    value = d.get(key)
                    # A kludge: strip leading \\ from patterns.
                    # if key.startswith(r'\\'):
                        # key = '[' + key[2:]
                        # if trace: g.trace('removing escapes', key)
                    if key in seen:
                        g.trace('duplicate key', key)
                    else:
                        seen.add(key)
                        aList.append(self.msf.Pattern(key, value))
                if trace:
                    g.trace('@data %s ...\n' % kind)
                    for z in aList:
                        print(z)
                    print('')
                return aList
            #@+node:ekr.20160213070235.6: *5* msf.finalize
            def finalize(self, fn):
                '''Finalize and regularize a filename.'''
                return g.os_path_normpath(g.os_path_abspath(g.os_path_expanduser(fn)))
            #@+node:ekr.20160213070235.7: *5* msf.make_stub_file
            def make_stub_file(self, p):
                '''Make a stub file in ~/stubs for the @<file> node at p.'''
                import ast
                assert p.isAnyAtFileNode()
                c = self.c
                fn = p.anyAtFileNodeName()
                if not fn.endswith('.py'):
                    g.es_print('not a python file', fn)
                    return
                abs_fn = g.fullPath(c, p)
                if not g.os_path_exists(abs_fn):
                    g.es_print('not found', abs_fn)
                    return
                if g.os_path_exists(self.output_directory):
                    base_fn = g.os_path_basename(fn)
                    out_fn = g.os_path_finalize_join(self.output_directory, base_fn)
                else:
                    g.es_print('not found', self.output_directory)
                    return
                out_fn = out_fn[:-3] + '.pyi'
                out_fn = g.os_path_normpath(out_fn)
                self.output_fn = out_fn
                    # compatibility with stand-alone script
                s = open(abs_fn).read()
                node = ast.parse(s,filename=fn,mode='exec')
                # Make the traverser *after* creating output_fn and output_directory ivars.
                x = self.msf.StubTraverser(controller=self)
                x.output_fn = self.output_fn
                x.output_directory = self.output_directory
                x.trace_matches = self.trace_matches
                x.trace_patterns = self.trace_patterns
                x.trace_reduce = self.trace_reduce
                x.trace_visitors = self.trace_visitors
                x.run(node)

            #@+node:ekr.20160213070235.8: *5* msf.run
            def run(self, p):
                '''Make stub files for all files in p's tree.'''
                if p.isAnyAtFileNode():
                    self.make_stub_file(p)
                    return
                # First, look down tree.
                after, p2 = p.nodeAfterTree(), p.firstChild()
                found = False
                while p2 and p != after:
                    if p2.isAnyAtFileNode():
                        self.make_stub_file(p2)
                        p2.moveToNext()
                        found = True
                    else:
                        p2.moveToThreadNext()
                if not found:
                    # Look up the tree.
                    for p2 in p.parents():
                        if p2.isAnyAtFileNode():
                            self.make_stub_file(p2)
                            break
                    else:
                        g.es('no files found in tree:', p.h)
            #@-others
        #@-others
        MakeStubFileAdapter(self.c).run(self.c.p)
    #@+node:ekr.20160316091923.1: *3* ccc.python-to-coffeescript
    @cmd('python-to-coffeescript')
    def python2coffeescript(self, event):
        '''
        Converts python text to coffeescript text. The conversion is not
        perfect, but it eliminates a lot of tedious text manipulation.
        '''
        #@+others
        #@+node:ekr.20160316092837.1: *4* class Python_To_Coffeescript_Adapter
        class Python_To_Coffeescript_Adapter:
            '''An interface class between Leo and leo/external/py2cs.py.'''
            #@+others
            #@+node:ekr.20160316112717.1: *5* py2cs.ctor
            def __init__(self,c):
                '''Ctor for Python_To_Coffeescript_Adapter class.'''
                self.c = c
                self.files = []
                self.output_directory = self.finalize(
                    c.config.getString('py2cs-output-directory'))
                # self.output_fn = None
                self.overwrite = c.config.getBool('py2cs-overwrite', default=False)
                # Connect to the external module.
                self.py2cs = py2cs = g.importExtension(
                    'py2cs',
                    pluginName=None,
                    verbose=False,
                    required=False,
                )
            #@+node:ekr.20160316093019.1: *5* py2cs.main
            def main(self):
                '''Main line for Python_To_CoffeeScript class.'''
                if self.py2cs:
                    self.run()
                else:
                    g.es_print('can not load py2cs.py')
                   
                
            #@+node:ekr.20160316094011.7: *5* py2cs.finalize
            def finalize(self, fn):
                '''Finalize and regularize a filename.'''
                return g.os_path_normpath(g.os_path_abspath(g.os_path_expanduser(fn)))
            #@+node:ekr.20160316094011.8: *5* py2cs.to_coffeescript
            def to_coffeescript(self, p):
                '''Convert the @<file> node at p to a .coffee file.'''
                assert p.isAnyAtFileNode()
                c = self.c
                fn = p.anyAtFileNodeName()
                if not fn.endswith('.py'):
                    g.es_print('not a python file', fn)
                    return
                abs_fn = g.fullPath(c, p)
                if not g.os_path_exists(abs_fn):
                    g.es_print('not found', abs_fn)
                    return
                if g.os_path_exists(self.output_directory):
                    base_fn = g.os_path_basename(fn)
                    out_fn = g.os_path_finalize_join(self.output_directory, base_fn)
                else:
                    g.es_print('not found', self.output_directory)
                    return
                out_fn = out_fn[:-3] + '.coffee'
                out_fn = g.os_path_normpath(out_fn)
                s = open(abs_fn).read()
                # s = self.strip_sentinels(s)
                if 0:
                    for z in g.splitLines(s)[:20]:
                        print(z.rstrip())
                x = self.py2cs.MakeCoffeeScriptController()
                # copy ivars and run.
                x.enable_unit_tests = False
                x.files = [abs_fn,]
                x.output_directory = self.output_directory
                x.overwrite = self.overwrite
                x.make_coffeescript_file(abs_fn, s=s)
            #@+node:ekr.20160316094011.9: *5* py2cs.run
            def run(self):
                '''Create .coffee files for all @<file> nodes in p's tree.'''
                p = c.p
                if p.isAnyAtFileNode():
                    self.to_coffeescript(p)
                    return
                # First, look down tree.
                after, p2 = p.nodeAfterTree(), p.firstChild()
                found = False
                while p2 and p != after:
                    if p2.isAnyAtFileNode():
                        self.to_coffeescript(p2)
                        p2.moveToNext()
                        found = True
                    else:
                        p2.moveToThreadNext()
                if not found:
                    # Look up the tree.
                    for p2 in p.parents():
                        if p2.isAnyAtFileNode():
                            self.to_coffeescript(p2)
                            return
                g.es_print('no files found in tree:', p.h)
            #@+node:ekr.20160316141812.1: *5* py2cs.strip_sentinels
            def strip_sentinels(self, s):
                '''
                Strip s of all sentinel lines.
                This may be dubious because it destroys outline structure.
                '''
                delims = ['#', None, None]
                return ''.join([z for z in g.splitLines(s) if not g.is_sentinel(z, delims)])
            #@-others
        #@-others
        c = self.c
        Python_To_Coffeescript_Adapter(c).main()
        c.bodyWantsFocus()
    #@+node:ekr.20160316091843.2: *3* ccc.typescript-to-py
    @cmd('typescript-to-py')
    def tsToPy(self, event):
        '''
        The typescript-to-python command converts typescript text to python
        text. The conversion is not perfect, but it eliminates a lot of tedious
        text manipulation.
        '''
        #@+others
        #@+node:ekr.20150514063305.176: *4* class TS_To_Python (To_Python)
        class TS_To_Python(To_Python):
            #@+others
            #@+node:ekr.20150514063305.177: *5* ctor (TS_To_Python)
            def __init__(self, c):
                '''Ctor for TS_To_Python class.'''
                # pylint: disable=super-init-not-called
                c.convertCommands.To_Python.__init__(self, c)
                    # init the base class
                self.class_name = ''
                    # The class name for the present function.  Used to modify ivars.
            #@+node:ekr.20150514063305.178: *5* convertCodeList (TS_To_Python) & helpers
            def convertCodeList(self, aList):
                r, sr = self.replace, self.safe_replace
                # First...
                r(aList, '\r', '')
                self.mungeAllFunctions(aList)
                self.mungeAllClasses(aList)
                # Second...
                sr(aList, ' -> ', '.')
                sr(aList, '->', '.')
                sr(aList, ' . ', '.')
                # sr(aList, 'this.self', 'self')
                sr(aList, '{', '')
                sr(aList, '}', '')
                sr(aList, 'else if', 'elif')
                sr(aList, 'else', 'else:')
                sr(aList, '&&', ' and ')
                sr(aList, '||', ' or ')
                sr(aList, 'true', 'True')
                sr(aList, 'false', 'False')
                sr(aList, 'null', 'None')
                sr(aList, 'this', 'self')
                sr(aList, 'try', 'try:')
                sr(aList, 'catch', 'except:')
                sr(aList, 'constructor', '__init__')
                sr(aList, 'new ', '')
                # sr(aList, 'var ','')
                    # var usually indicates something weird, or an uninited var,
                    # so it may be good to retain as a marker.
                # Third...
                self.handle_all_keywords(aList)
                self.insert_not(aList)
                self.removeSemicolonsAtEndOfLines(aList)
                    # after processing for keywords
                self.comment_scope_ids(aList)
                # Last...
                self.removeBlankLines(aList)
                self.removeExcessWs(aList)
                # I usually don't like extra whitespace. YMMV.
                sr(aList, '  and ', ' and ')
                sr(aList, '  not ', ' not ')
                sr(aList, '  or ', ' or ')
                sr(aList, ' and  ', ' and ')
                sr(aList, ' not  ', ' not ')
                sr(aList, ' or  ', ' or ')
                sr(aList, ' :', ':')
                sr(aList, ', ', ',')
                sr(aList, ' ,', ',')
                sr(aList, ' (', '(')
                sr(aList, '( ', '(')
                sr(aList, ' )', ')')
                sr(aList, ') ', ')')
                sr(aList, ' and(', ' and (')
                sr(aList, ' not(', ' not (')
                sr(aList, ' or(', ' or (')
                sr(aList, ')and ', ') and ')
                sr(aList, ')not ', ') not ')
                sr(aList, ')or ', ') or ')
                sr(aList, ')and(', ') and (')
                sr(aList, ')not(', ') not (')
                sr(aList, ')or(', ') or (')
                sr(aList, '@language javascript', '@language python')
                self.replaceComments(aList) # should follow all calls to safe_replace
                self.removeTrailingWs(aList)
                r(aList, '\t ', '\t') # happens when deleting declarations.
            #@+node:ekr.20150514063305.179: *6* comment_scope_ids
            def comment_scope_ids(self, aList):
                '''convert (public|private|export) aLine to aLine # (public|private|export)'''
                scope_ids = ('public', 'private', 'export',)
                i = 0
                if any([self.match_word(aList, i, z) for z in scope_ids]):
                    i = self.handle_scope_keyword(aList, i)
                while i < len(aList):
                    progress = i
                    if self.is_string_or_comment(aList, i):
                        i = self.skip_string_or_comment(aList, i)
                    elif aList[i] == '\n':
                        i += 1
                        i = self.skip_ws(aList, i)
                        if any([self.match_word(aList, i, z) for z in scope_ids]):
                            i = self.handle_scope_keyword(aList, i)
                    else:
                        i += 1
                    assert i > progress
                # print "handAllKeywords2:", ''.join(aList)
            #@+node:ekr.20150514063305.180: *7* handle_scope_keyword
            def handle_scope_keyword(self, aList, i):
                i1 = i
                # pylint: disable=undefined-loop-variable
                # word *is* defined below.
                for word in ('public', 'private', 'export'):
                    if self.match_word(aList, i, word):
                        i += len(word)
                        break
                else:
                    return
                    # assert False, 'not a scope id: %s' % word
                # Skip any following spaces.
                i2 = self.skip_ws(aList, i)
                # Scan to the next newline:
                i3 = self.skip_line(aList, i)
                # Optional: move the word to a trailing comment.
                comment = list(' # %s' % word) if False else []
                # Change the list in place.
                aList[i1: i3] = aList[i2: i3] + comment
                i = i1 + (i3 - i2) + len(comment)
                # g.trace(''.join(aList[i1:i]))
                return i
            #@+node:ekr.20150514063305.181: *6* handle_all_keywords
            def handle_all_keywords(self, aList):
                '''
                converts if ( x ) to if x:
                converts while ( x ) to while x:
                '''
                statements = ('elif', 'for', 'if', 'while',)
                i = 0
                while i < len(aList):
                    if self.is_string_or_comment(aList, i):
                        i = self.skip_string_or_comment(aList, i)
                    elif any([self.match_word(aList, i, z) for z in statements]):
                        i = self.handle_keyword(aList, i)
                    # elif (
                        # self.match_word(aList,i,"if") or
                        # self.match_word(aList,i,"while") or
                        # self.match_word(aList,i,"for") or
                        # self.match_word(aList,i,"elif")
                    # ):
                        # i = self.handle_keyword(aList,i)
                    else:
                        i += 1
                # print "handAllKeywords2:", ''.join(aList)
            #@+node:ekr.20150514063305.182: *7* handle_keyword
            def handle_keyword(self, aList, i):
                if self.match_word(aList, i, "if"):
                    i += 2
                elif self.match_word(aList, i, "elif"):
                    i += 4
                elif self.match_word(aList, i, "while"):
                    i += 5
                elif self.match_word(aList, i, "for"):
                    i += 3
                else: assert False, 'not a keyword'
                # Make sure one space follows the keyword.
                k = i
                i = self.skip_ws(aList, i)
                if k == i:
                    c = aList[i]
                    aList[i: i + 1] = [' ', c]
                    i += 1
                # Remove '(' and matching ')' and add a ':'
                if aList[i] == "(":
                    # Look ahead.  Don't remove if we span a line.
                    j = self.skip_to_matching_bracket(aList, i)
                    k = i
                    found = False
                    while k < j and not found:
                        found = aList[k] == '\n'
                        k += 1
                    if not found:
                        j = self.removeMatchingBrackets(aList, i)
                    if j > i and j < len(aList):
                        ch = aList[j]
                        aList[j: j + 1] = [ch, ":", " "]
                        j = j + 2
                    return j
                return i
            #@+node:ekr.20150514063305.183: *6* mungeAllClasses
            def mungeAllClasses(self, aList):
                '''Scan for a '{' at the top level that is preceeded by ')' '''
                i = 0
                while i < len(aList):
                    progress = i
                    if self.is_string_or_comment(aList, i):
                        i = self.skip_string_or_comment(aList, i)
                    elif self.match_word(aList, i, 'class'):
                        i1 = i
                        i = self.skip_line(aList, i)
                        aList[i - 1: i] = list('%s:' % aList[i - 1])
                        s = ''.join(aList[i1: i])
                        k = s.find(' extends ')
                        if k > -1:
                            k1 = k
                            k = g.skip_id(s, k + 1)
                            k = g.skip_ws(s, k)
                            if k < len(s) and g.is_c_id(s[k]):
                                k2 = g.skip_id(s, k)
                                word = s[k: k2]
                                aList[i1: i] = list('%s (%s)' % (s[: k1], word))
                    elif self.match_word(aList, i, 'interface'):
                        aList[i: i + len('interface')] = list('class')
                        i = self.skip_line(aList, i)
                        aList[i - 1: i] = list('%s: # interface' % aList[i - 1])
                        i = self.skip_line(aList, i) # Essential.
                    else:
                        i += 1
                    assert i > progress
            #@+node:ekr.20150514063305.184: *6* mungeAllFunctions & helpers
            def mungeAllFunctions(self, aList):
                '''Scan for a '{' at the top level that is preceeded by ')' '''
                prevSemi = 0 # Previous semicolon: header contains all previous text
                i = 0
                firstOpen = None
                while i < len(aList):
                    progress = i
                    if self.is_string_or_comment(aList, i):
                        j = self.skip_string_or_comment(aList, i)
                        prevSemi = j
                    elif self.match(aList, i, '('):
                        if not firstOpen:
                            firstOpen = i
                        j = i + 1
                    elif self.match(aList, i, ';'):
                        j = i + 1
                        prevSemi = j
                    elif self.match(aList, i, "{"):
                        j = self.handlePossibleFunctionHeader(aList, i, prevSemi, firstOpen)
                        prevSemi = j
                        firstOpen = None # restart the scan
                        # g.trace(repr(''.join(aList[prevSemi:prevSemi+20])))
                    else:
                        j = i + 1
                    # Handle unusual cases.
                    if j <= progress:
                        j = progress + 1
                    assert j > progress
                    i = j
            #@+node:ekr.20150514063305.185: *7* handlePossibleFunctionHeader
            def handlePossibleFunctionHeader(self, aList, i, prevSemi, firstOpen):
                '''
                converts function header lines from typescript format to python format.
                That is, converts
                    x1..nn w::y ( t1 z1,..tn zn) { C++
                    (public|private|export) name (t1: z1, ... tn: zn {
                to
                    def y (z1,..zn): { # (public|private|export)
                '''
                trace = False
                assert(self.match(aList, i, "{"))
                prevSemi = self.skip_ws_and_nl(aList, prevSemi)
                close = self.prevNonWsOrNlChar(aList, i)
                if close < 0 or aList[close] != ')':
                    # Should not increase *Python* indent.
                    return 1 + self.skip_to_matching_bracket(aList, i)
                if not firstOpen:
                    return 1 + self.skip_to_matching_bracket(aList, i)
                close2 = self.skip_to_matching_bracket(aList, firstOpen)
                if close2 != close:
                    return 1 + self.skip_to_matching_bracket(aList, i)
                open_paren = firstOpen
                assert(aList[open_paren] == '(')
                head = aList[prevSemi: open_paren]
                # do nothing if the head starts with "if", "for" or "while"
                k = self.skip_ws(head, 0)
                if k >= len(head) or not head[k].isalpha():
                    return 1 + self.skip_to_matching_bracket(aList, i)
                kk = self.skip_past_word(head, k)
                if kk > k:
                    headString = ''.join(head[k: kk])
                    # C keywords that might be followed by '{'
                    # print "headString:", headString
                    if headString in ["do", "for", "if", "struct", "switch", "while"]:
                        return 1 + self.skip_to_matching_bracket(aList, i)
                args = aList[open_paren: close + 1]
                k = 1 + self.skip_to_matching_bracket(aList, i)
                body = aList[close + 1: k]
                if trace:
                    g.trace('\nhead: %s\nargs: %s\nbody: %s' % (
                        ''.join(head), ''.join(args), ''.join(body)))
                head = self.massageFunctionHead(head)
                args = self.massageFunctionArgs(args)
                body = self.massageFunctionBody(body)
                if False and trace:
                    g.trace('\nhead2: %s\nargs2: %s\nbody2: %s' % (
                        ''.join(head), ''.join(args), ''.join(body)))
                result = []
                if head: result.extend(head)
                if args: result.extend(args)
                if body: result.extend(body)
                aList[prevSemi: k] = result
                return prevSemi + len(result)
            #@+node:ekr.20150514063305.186: *7* massageFunctionArgs
            def massageFunctionArgs(self, args):
                assert(args[0] == '(')
                assert(args[-1] == ')')
                result = ['(']
                lastWord = []
                if self.class_name:
                    for item in list("self,"): result.append(item) #can put extra comma
                i = 1
                while i < len(args):
                    i = self.skip_ws_and_nl(args, i)
                    c = args[i]
                    if c.isalpha():
                        j = self.skip_past_word(args, i)
                        lastWord = args[i: j]
                        i = j
                    elif c == ',' or c == ')':
                        for item in lastWord:
                            result.append(item)
                        if lastWord != [] and c == ',':
                            result.append(',')
                        lastWord = []
                        i += 1
                    else: i += 1
                if result[-1] == ',':
                    del result[-1]
                result.append(')')
                result.append(':')
                return result
            #@+node:ekr.20150514063305.187: *7* massageFunctionHead (sets .class_name)
            def massageFunctionHead(self, head):
                result = []
                prevWord = []
                self.class_name = ''
                i = 0
                # g.trace(repr(''.join(head)))
                while i < len(head):
                    i = self.skip_ws_and_nl(head, i)
                    if i < len(head) and head[i].isalpha():
                        result = []
                        j = self.skip_past_word(head, i)
                        prevWord = head[i: j]
                        i = j
                        # look for ::word2
                        i = self.skip_ws(head, i)
                        if self.match(head, i, "::"):
                            # Set the global to the class name.
                            self.class_name = ''.join(prevWord)
                            # print(class name:", self.class_name)
                            i = self.skip_ws(head, i + 2)
                            if i < len(head) and (head[i] == '~' or head[i].isalpha()):
                                j = self.skip_past_word(head, i)
                                if head[i: j] == prevWord:
                                    result.extend('__init__')
                                elif head[i] == '~' and head[i + 1: j] == prevWord:
                                    result.extend('__del__')
                                else:
                                    # result.extend(list('::'))
                                    result.extend(head[i: j])
                                i = j
                        else:
                            result.extend(prevWord)
                    else: i += 1
                finalResult = list("def ")
                finalResult.extend(result)
                return finalResult
            #@+node:ekr.20150514063305.188: *7* massageFunctionBody & helper
            def massageFunctionBody(self, body):
                # body = self.massageIvars(body)
                # body = self.removeCasts(body)
                # body = self.removeTypeNames(body)
                body = self.dedentBlocks(body)
                return body
            #@+node:ekr.20150514063305.189: *8* dedentBlocks
            def dedentBlocks(self, body):
                '''
                Look for '{' preceded by '{' or '}' or ';'
                (with intervening whitespace and comments).
                '''
                i = 0
                while i < len(body):
                    j = i
                    ch = body[i]
                    if self.is_string_or_comment(body, i):
                        j = self.skip_string_or_comment(body, i)
                    elif ch in '{};':
                        # Look ahead ofr '{'
                        j += 1
                        while True:
                            k = j
                            j = self.skip_ws_and_nl(body, j)
                            if self.is_string_or_comment(body, j):
                                j = self.skip_string_or_comment(body, j)
                            if k == j: break
                            assert k < j
                        if self.match(body, j, '{'):
                            k = j
                            j = self.skip_to_matching_bracket(body, j)
                            # g.trace('found block\n',''.join(body[k:j+1]))
                            m = '# <Start dedented block>...'
                            body[k: k + 1] = list(m)
                            j += len(m)
                            while k < j:
                                progress = k
                                if body[k] == '\n':
                                    k += 1
                                    spaces = 0
                                    while spaces < 4 and k < j:
                                        if body[k] == ' ':
                                            spaces += 1
                                            k += 1
                                        else:
                                            break
                                    if spaces > 0:
                                        del body[k - spaces: k]
                                        k -= spaces
                                        j -= spaces
                                else:
                                    k += 1
                                assert progress < k
                            m = '    # <End dedented block>'
                            body[j: j + 1] = list(m)
                            j += len(m)
                    else:
                        j = i + 1
                    # Defensive programming.
                    if i == j:
                        j += 1
                    assert i < j
                    i = j
                return body
            #@-others
        #@-others
        c = self.c
        self.Python_To_CoffeeScript(c).go()
        c.bodyWantsFocus()
    #@+node:ekr.20160321042444.1: *3* ccc.import-jupyter-notebook
    @cmd('import-jupyter-notebook')
    def importJupyterNotebook(self, event):
        '''Prompt for a Jupyter (.ipynb) file and convert it to a Leo outline.'''
        try:
            # from nbformat import reads, NBFormatError
            import nbformat
        except ImportError:
            g.es_print('import-jupyter-notebook requires nbformat package')
            return
        #@+others
        #@+node:ekr.20160320183705.1: *4* class Import_IPYNB
        class Import_IPYNB:
            '''A class to import .ipynb files.'''

            #@+others
            #@+node:ekr.20160321051844.1: *5* ctor
            def __init__(self, c):
                '''Ctor for Import_IPYNB class.'''
                self.brief = True
                    # True: don't show source & data lines.
                self.c = c
                    # Commander of present outline.
                self.cell_p = None
                    # Position of present cell.
                self.dump = False
                    # True: do show data.
                self.gen = True
                    # True: generate Leo outline from cells.
                self.parent = None
                    # The parent for the next created node.
                self.root = None
                    # The root of the to-be-created outline.
            #@+node:ekr.20160320184226.1: *5* do_cell
            def do_cell(self, cell, n):
                
                cell_name = 'cell %s' % (n + 1)
                if self.dump:
                    print(cell_name)
                if self.gen:
                    self.parent = self.root.insertAsLastChild()
                    self.parent.h = cell_name
                    self.cell_p = self.parent
                else:
                    self.parent = None
                cell_type = cell.get('cell_type')
                if cell_type:
                    self.do_cell_type('cell_type', cell_type)
                for key in sorted(cell):
                    val = cell.get(key)
                    g.trace(key, val.__class__.__name__)
                    if self.is_dict(val):
                        self.do_dict(key, val)
                    elif isinstance(val, (list, tuple)):
                        self.do_list(key, val)
                    # if key == 'cell_type':
                        # pass # Done above
                    # elif key == 'metadata':
                        # self.do_metadata(key, val)
                    # elif key == 'outputs':
                        # self.do_outputs(key, val)
                    # elif key == 'source':
                        # self.do_source(key, val)
                    else:
                        self.do_general(key, val)
                if self.dump:
                    print('')
            #@+node:ekr.20160321131740.1: *5* do_dict
            def do_dict(self, key, d):
                
                assert self.is_dict(d), d.__class__.__name__
                if not d:
                    return
                if self.parent:
                    old_parent = self.parent
                    self.parent = old_parent.insertAsLastChild()
                    self.parent.h = '# %s' % key
                else:
                    old_parent = None
                    parent = None
                self.put(key, '{')
                self.indent += 8
                for key2 in d:
                    val2 = d.get(key2)
                    if self.parent:
                        if key2 == 'collapsed' and val2 in (False, 'false'):
                            self.cell_p.expand()
                        p = self.parent.insertAsLastChild()
                        p.h = '# ' + key2
                        p.b = self.toString(key2, val2)
                    try:
                        self.put(key2, '{')
                        self.indent += 8
                        for key3 in val2:
                            val3 = val2.get(key3)
                            self.put(key3, val3)
                        self.indent -= 8
                        self.put(key2, '}')
                    except TypeError:
                        self.put(key2, val2)
                self.indent -= 8
                self.put(key, '}')
                if old_parent:
                    self.parent = old_parent
            #@+node:ekr.20160321053212.1: *5* do_cell_type
            def do_cell_type(self, key, val):
                
                self.put(key, val)
                if not self.parent:
                    return
                if val == 'code':
                    s = '@language python'
                elif val == 'markdown':
                    s = '@language rest\n@wrap'
                elif val == 'raw':
                    s = '@killcolor'
                if s:
                    self.parent.b = s + '\n\n' + self.parent.b
            #@+node:ekr.20160320185816.1: *5* do_data
            def do_data(self, key, val):
                
                if not val:
                    return
                self.put(key, '{')
                self.indent += 8
                for key2 in val:
                    val2 = val.get(key2)
                    if self.parent:
                        p = self.parent.insertAsLastChild()
                        p.h = '# ' + key2
                        p.b = self.toString(key2, val2)
                    if g.isString(val2):
                        lines = g.splitLines(val2)
                        if self.brief:
                            self.put(key2, len(lines))
                        else:
                            self.put(key2)
                            for s in lines:
                                print(s.rstrip())
                    else:
                        self.put(key2, len(val2 or ''))
                self.indent -= 8
                self.put(key, '}')
            #@+node:ekr.20160321062745.1: *5* do_general
            def do_general(self, key, val):
                
                if self.parent:
                    p = self.parent.insertAsLastChild()
                    p.h = '# ' + key
                    p.b = self.toString(key, val)
                self.put(key,val)
            #@+node:ekr.20160321132453.1: *5* do_list
            def do_list(self, key, aList):
                
                assert isinstance(aList, (list, tuple)), aList.__class__.__name__
                if not aList:
                    return
                if self.parent:
                    g.trace(key, len(aList))
                    self.parent.b += (''.join(aList).rstrip() + '\n')
                lines = g.splitLines(aList)
                if self.brief:
                    self.put(key, len(lines))
                else:
                    self.put(key)
                    for s in lines:
                        print(s.rstrip())
            #@+node:ekr.20160320192424.1: *5* do_metadata (no longer used)
            def do_metadata(self, key, val):

                if not val:
                    return
                if self.parent:
                    old_parent = self.parent
                    self.parent = old_parent.insertAsLastChild()
                    self.parent.h = '# metadata'
                else:
                    old_parent = None
                    parent = None
                self.put(key, '{')
                self.indent += 8
                for key2 in val:
                    val2 = val.get(key2)
                    if self.parent:
                        if key2 == 'collapsed' and val2 in (False, 'false'):
                            self.cell_p.expand()
                        p = self.parent.insertAsLastChild()
                        p.h = '# ' + key2
                        p.b = self.toString(key2, val2)
                    try:
                        self.put(key2, '{')
                        self.indent += 8
                        for key3 in val2:
                            val3 = val2.get(key3)
                            self.put(key3, val3)
                        self.indent -= 8
                        self.put(key2, '}')
                    except TypeError:
                        self.put(key2, val2)
                self.indent -= 8
                self.put(key, '}')
                if old_parent:
                    self.parent = old_parent

            #@+node:ekr.20160320185354.1: *5* do_outputs (no longer used)
            def do_outputs(self, key, val):
                
                # Val is a list of dicts.
                if not val:
                    return
                if self.parent:
                    old_parent = self.parent
                    self.parent = old_parent.insertAsLastChild()
                    self.parent.h = '# outputs'
                else:
                    old_parent = None
                    parent = None
                for d in val:
                    self.put(key, '{')
                    self.indent += 8
                    for key2 in d.keys():
                        val2 = d.get(key2)
                        if key2 == 'data':
                            self.do_data(key2, val2)
                        elif self.parent:
                            p = self.parent.insertAsLastChild()
                            p.h = '# ' + key2
                            p.b = self.toString(key2, val2)
                            self.put(key2, val2)
                        else:
                            self.put(key2, val2)
                    self.indent -= 8
                    self.put(key, '}')
                if old_parent:
                    self.parent = old_parent
            #@+node:ekr.20160320192858.1: *5* do_prefix
            def do_prefix(self, d):
                '''
                Handle the top-level non-cell data:
                    
                metadata (dict)
                nbformat (int)
                nbformat_minor (int)
                '''
                if self.dump:
                    print('non-cell data:')
                for key in sorted(d):
                    if key != 'cells':
                        val = d.get(key)
                        # if key == 'metadata':
                        if self.is_dict(val):
                            self.do_dict(key, val)
                            ### self.do_metadata(key, val)
                        else:
                            ### self.put(key, val)
                            self.do_general(key, val)
                if self.dump:
                    print('')
            #@+node:ekr.20160320184422.1: *5* do_source
            def do_source(self, key, val):

                if not val:
                    return
                if self.parent:
                    self.parent.b = self.parent.b + val.rstrip() + '\n'
                lines = g.splitLines(val)
                if self.brief:
                    self.put(key, len(lines))
                else:
                    self.put(key)
                    for s in lines:
                        print(s.rstrip())
            #@+node:ekr.20160321044209.1: *5* get_file_name
            def get_file_name(self):
                '''Open a dialog to get a Jupyter (.ipynb) file.'''
                c = self.c
                fn = g.app.gui.runOpenFileDialog(
                    c,
                    title="Open Jupyter File",
                    filetypes=[
                        ("All files", "*"),
                        ("Jypyter files", "*.ipynb"),
                    ],
                    defaultextension=".ipynb",
                )
                c.bringToFront()
                return fn
            #@+node:ekr.20160320183944.1: *5* import_file (entry point)
            def import_file(self, fn, root, brief=True, dump=False, gen=True):
                '''
                Import the given .ipynb file.
                
                https://nbformat.readthedocs.org/en/latest/format_description.html
                At the highest level, a Jupyter notebook is a dictionary with a few keys:

                metadata (dict)
                nbformat (int)
                nbformat_minor (int)
                cells (list)
                '''
                self.brief = brief
                self.dump = dump
                self.fn = fn
                self.gen = gen
                self.indent = 0
                self.parent = None
                self.root = root.copy()
                d = self.parse(fn)
                self.do_prefix(d)
                cells = d.get('cells', [])
                for n, cell in enumerate(cells):
                    self.do_cell(cell, n)
                # self.root.expand()
            #@+node:ekr.20160321131938.1: *5* is_dict
            def is_dict(self, obj):
                
                return isinstance(obj, (dict, nbformat.NotebookNode))
            #@+node:ekr.20160320140531.1: *5* parse
            def parse(self, fn):
                
                if g.os_path_exists(fn):
                    with open(fn) as f:
                        payload_source = f.name
                        payload = f.read()
                    nb = nbformat.reads(payload, as_version=4)
                        # Require IPython 4.
                    return nb
                else:
                    g.es_print('not found', fn)
                    return None
            #@+node:ekr.20160320184721.1: *5* put
            def put(self, key, val=''):

                if self.dump:
                    print('%s%18s: %s' % (' '*self.indent, key, val))
            #@+node:ekr.20160321060950.1: *5* toString
            def toString(self, key, val):
                
                if not g.isString(val):
                    val = repr(val)
                if key.endswith('html'):
                    s = '@language html'
                elif key.endswith('xml'):
                    s = '@language xml'
                else:
                    s = None
                return s + '\n\n' + val if s else val
            #@-others
        #@-others
        c = self.c
        x = Import_IPYNB(c)
        fn = x.get_file_name()
        if fn:
            p = c.lastTopLevel()
            root = p.insertAfter()
            root.h = fn
            x.import_file(fn, root)
            c.redraw(root)
        c.bodyWantsFocus()
    #@+node:ekr.20160321072007.1: *3* ccc.export-jupyter-notebook
    @cmd('export-jupyter-notebook')
    def exportJupyterNotebook(self, event):
        '''Prompt for a Jupyter (.ipynb) file and convert it to a Leo outline.'''
        # try:
            # from nbformat import writes, NBFormatError
        # except ImportError:
            # g.es_print('import-jupyter-notebook requires nbformat package')
            # return
        #@+others
        #@+node:ekr.20160321072233.1: *4* class Export_IPYNB
        class Export_IPYNB:
            '''A class to export outlines to .ipynb files.'''

            #@+others
            #@+node:ekr.20160321072233.2: *5* ctor
            def __init__(self, c):
                '''Ctor for Import_IPYNB class.'''
                self.c = c
                    # Commander of present outline.
                # self.excludes = [
                    # 'cell_type', 'collapsed', 'data', 'execution_count',
                    # 'metadata', 'outputs', 'source',
                    # 'image/svg+xml', 'text/html', 'text/plain',
                # ]
                self.indent = 0
                    # The indentation level of generated lines.
                self.lines = []
                    # The lines of the output.
                self.nest = False
                    # True if cells can nest.
                self.p = None
                    # Position of node being generated
                self.root = None
                    # The root of the to-be-created outline.
            #@+node:ekr.20160321072504.1: *5* export_outline (entry point)
            def export_outline(self, root):
                '''Import the given .ipynb file.'''
                trace = True # and not g.unitTesting
                self.indent = 0
                self.lines = []
                self.put('{')
                self.indent += 2
                self.put('"cells": [')
                self.indent += 2
                self.put_cell(root)
                self.indent -= 2
                self.put(']')
                self.indent -= 2
                self.put('}')
                if trace:
                    print('\n'.join(self.lines))
                # To do: write the file.
            #@+node:ekr.20160321140725.1: *5* is_cell
            def is_cell(self, p):
                
                return not p.h.startswith('#')
            #@+node:ekr.20160321074510.1: *5* put
            def put(self, s):
                
                line = '%s%s' % (' '*self.indent, s)
                self.lines.append(line)
            #@+node:ekr.20160321073531.1: *5* put_cell
            def put_cell(self, p):

                self.put('{')
                self.indent += 2
                self.put_cell_data(p)
                self.indent -= 2
                self.put('},')
                for child in p.children():
                    if self.is_cell(child):
                        self.put_cell(child)
            #@+node:ekr.20160321074345.1: *5* put_cell_data
            def put_cell_data(self, p):

                if self.is_cell(p):
                    self.put_cell_type(p)
                    # self.put('"leo_headline": %s' % p.h)
                    self.put_key_val('leo_headline', p.h)
                for child in p.children():
                    if not self.is_cell(child):
                        self.indent += 2
                        h = child.h[1:].strip()
                        if h.startswith('metadata'):
                            self.put_metadata(child)
                        elif h.startswith('outputs'):
                            self.put_outputs(child)
                        else:
                            self.put_key_val(h, child.b)

                        self.indent -= 2
                if self.is_cell(p):
                    self.put_source(p)
            #@+node:ekr.20160321080900.1: *5* put_cell_children
            def put_cell_children(self, p):
                
                for child in p.children():
                    if not child.h.startswith('#'):
                        self.put_cell(child)
            #@+node:ekr.20160321135341.1: *5* put_cell_type (to do: header types)
            def put_cell_type(self, p):

                s = p.b.strip()
                if s.find('@language python') > -1:
                    s2 = 'code'
                elif (
                    s.find('@language rest') > -1 or
                    s.find('@language markdown') > -1
                ):
                    s2 = 'markdown'
                elif s:
                    s2 = 'code'
                else:
                    s2 = 'code' # New default.
                if s2:
                    self.put('"cell_type": %s,' % s2)
            #@+node:ekr.20160321142517.1: *5* put_key_val
            def put_key_val(self, key, val):
                
                self.put('"%s": %s' % (key, val))
            #@+node:ekr.20160321142040.1: *5* put_list_helper
            def put_list_helper(self, key, s):
                
                if s.strip():
                    lines = g.splitLines(s)
                    self.put('"%s": [' % key)
                    self.indent += 2
                    for s in lines:
                        s = s.replace('"', '\"').rstrip()
                        self.put('"%s\\n",' % s)
                    self.indent -= 2
                    self.put('],')
            #@+node:ekr.20160321141639.1: *5* put_metadata
            def put_metadata(self, p):
                
                assert p.h.startswith('#'), p.h
                h = p.h[1:].strip()
                assert h.startswith('metadata')
                for child in p.children():
                    if self.is_cell(child):
                        g.trace('ignoring', child.h)
                    else:
                        key = child.h[1:].strip()
                        val = child.b
                        self.put_key_val(key, val)
            #@+node:ekr.20160321141823.1: *5* put_outputs
            def put_outputs(self, p):
                
                assert p.h.startswith('#'), p.h
                h = p.h[1:].strip()
                assert h.startswith('outputs')
                self.put_list_helper('outputs', p.b)
            #@+node:ekr.20160321140041.1: *5* put_source
            def put_source(self, p):
                
                self.put_list_helper('source', p.b)
            #@-others
        #@-others
        c = self.c
        Export_IPYNB(c).export_outline(c.p)
    #@-others
#@-others
#@-leo
