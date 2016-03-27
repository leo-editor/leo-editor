# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20160316095222.1: * @file ../commands/convertCommands.py
#@@first
'''Leo's file-conversion commands.'''
import leo.core.leoGlobals as g
from leo.commands.baseCommands import BaseEditCommandsClass as BaseEditCommandsClass
import re
import sys

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
                self.c = c
                    # Commander of present outline.
                self.cell = None
                    # The present cell node.
                self.cell_n = None
                    # The number of the top-level node being scanned.
                self.code_language = None
                    # The language in effect for code cells.
                self.cell_type = None
                    # The pre-computed cell type of the node.
                self.in_data = False
                    # True if in range of any dict.
                self.parent = None
                    # The parent for the next created node.
                self.re_header = re.compile(r'^.*<[hH]([123456])>(.*)</[hH]([123456])>')
                    # A regex matching html headers.
                self.root = None
                    # The root of the to-be-created outline.
            #@+node:ekr.20160321161756.1: *5* do_any & helpers
            def do_any(self, key, val):
                
                # if key == 'output_type': g.trace(val.__class__.__name__)
                if key == 'source':
                    self.do_source(key, val)
                elif g.isString(val):
                    self.do_string(key, val)
                elif isinstance(val, (list, tuple)):
                    self.do_list(key, val)
                elif self.is_dict(val):
                    self.do_dict(key, val)
                else:
                    # Can be ints, None, etc.
                    self.do_other(key, val)
            #@+node:ekr.20160321131740.1: *6* do_dict
            def do_dict(self, key, d):
                
                assert self.is_dict(d), d.__class__.__name__
                keys = list(d.keys())
                is_cell = self.parent == self.cell
                if key == 'metadata' and is_cell:
                    if 'collapsed' in keys:
                        if d.get('collapsed') in (False, 'false'):
                            self.cell.expand()
                        keys.remove('collapsed')
                    if 'leo_headline' in keys:
                        h = d.get('leo_headline')
                        if h:
                            self.cell.h = h
                        keys.remove('leo_headline')
                # g.trace(key, is_cell, keys)
                if is_cell and key == 'metadata' and not keys:
                    return # experimental
                old_parent = self.parent
                self.parent = self.new_node('# dict:%s' % key)
                old_in_dict = self.in_data
                self.in_data = key == 'data'
                for key2 in sorted(keys):
                    val2 = d.get(key2)
                    self.do_any(key2, val2)
                self.in_data = old_in_dict
                self.parent = old_parent
            #@+node:ekr.20160322104653.1: *6* do_other
            def do_other(self, key, val):
                
                if key == 'execution_count' and val is None:
                    pass # The exporter will create the proper value.
                else:
                    name = 'null' if val is None else val.__class__.__name__
                    p = self.new_node('# %s:%s' % (name, key))
                    if val is None:
                        p.b = '' # Exporter will translate to 'null'
                    else:
                        p.b = repr(val)
            #@+node:ekr.20160321062745.1: *6* do_string
            def do_string(self, key, val):
                
                assert g.isString(val)
                is_cell = self.parent == self.cell
                if is_cell and key == 'cell_type':
                    # Do *not* create a cell_type child.
                    pass
                else:
                    # Do create all other nodes.
                    if self.in_data or len(g.splitLines(val.strip())) > 1:
                        key = 'list:' + key
                    else:
                        key = 'str:' + key
                    p = self.new_node('# ' + key)
                    if key.startswith('list:'):
                        if key.endswith('html'):
                            val = '@language html\n\n' + val
                        elif key.endswith('xml'):
                            val = '@language html\n\n' + val
                        else:
                            val = '@nocolor-node\n\n' + val
                    # g.trace(key, g.splitLines(val)[:5])
                    p.b = val
            #@+node:ekr.20160321132453.1: *6* do_list
            def do_list(self, key, aList):

                assert isinstance(aList, (list, tuple)), aList.__class__.__name__
                is_cell = self.parent == self.cell
                if is_cell and not aList:
                    return # Experimental.
                old_parent = self.parent
                self.parent = self.new_node('# list:%s' % key)
                for z in aList:
                    if self.is_dict(z):
                        for key in sorted(z):
                            val = z.get(key)
                            self.do_any(key, val)
                    else:
                        self.error('unexpected item in list: %r' % z)
                self.parent = old_parent
            #@+node:ekr.20160323104332.1: *6* do_source & helpers
            def do_source(self, key, val):
                '''Set the cell's body text, or create a 'source' node.'''
                assert key == 'source', (key, val)
                is_cell = self.parent == self.cell
                if is_cell:
                    # Set the body's text, splitting markdown nodes as needed.
                    if self.cell_type == 'markdown':
                        self.do_markdown_cell(self.cell, val)
                    elif self.cell_type == 'raw':
                        self.cell.b = '@nocolor\n\n' + val
                    else:
                        self.cell.b = '@language %s\n\n' + val
                else:
                    # Do create a new node.
                    p = self.new_node('# list:%s' % key)
                    p.b = val
            #@+node:ekr.20160326124507.1: *7* check_header
            def check_header(self, m):
                '''Return (n, name) or (None, None) on error.'''
                val = (None, None)
                if m:
                    n1, name, n2 = m.group(1), m.group(2), m.group(3)
                    try:
                        if int(n1) == int(n2):
                            val = int(n1), name
                    except Exception:
                        pass
                    if val == (None, None):
                        g.trace('malformed header:', m.group(0))
                return val
            #@+node:ekr.20160326082322.1: *7* do_markdown_cell
            def do_markdown_cell(self, p, s):
                '''Split the markdown cell p if it contains one or more html headers.'''
                trace = False and not g.unitTesting
                i0, last, parent = 0, p.copy(), p.copy()
                if not s.strip():
                    return
                lines = g.splitLines(s)
                for i, s in enumerate(lines):
                    m = self.re_header.search(s)
                    n, name = self.check_header(m)
                    if n is None: continue
                    h = '<h%s> %s </h%s>' % (n, name.strip(), n)
                    prefix = ''.join(lines[i0: i])
                    suffix = ''.join(lines[i:])
                    if trace: g.trace('%2s %2s %s' % (i-i0, len(lines)-i, h))
                    if prefix.strip():
                        p2 = last.insertAfter()
                        p2.h = h
                        p2.b = suffix
                        last.b = '@language md\n\n' + prefix
                        last = p2
                        i0 = i
                    else:
                        last.h = h
                        last.b = '@language md\n\n' + suffix
            #@+node:ekr.20160320184226.1: *5* do_cell
            def do_cell(self, cell, n):

                self.cell_n = n
                if self.is_empty_code(cell):
                    g.trace('skipping empty cell', n)
                else:
                    # Careful: don't use self.new_node here.
                    self.parent = self.cell = self.root.insertAsLastChild()
                    self.parent.h = 'cell %s' % (n + 1)
                    # Pre-compute the cell_type.
                    self.cell_type = cell.get('cell_type')
                    for key in sorted(cell):
                        val = cell.get(key)
                        self.do_any(key, val)
            #@+node:ekr.20160320192858.1: *5* do_prefix
            def do_prefix(self, d):
                '''
                Handle the top-level non-cell data:
                metadata (dict)
                nbformat (int)
                nbformat_minor (int)
                '''
                if d:
                    self.parent = self.new_node('# {prefix}')
                    for key in sorted(d):
                        if key != 'cells':
                            val = d.get(key)
                            self.do_any(key, val)
            #@+node:ekr.20160320183944.1: *5* import_file (entry point)
            def import_file(self, fn, root):
                '''
                Import the given .ipynb file.
                https://nbformat.readthedocs.org/en/latest/format_description.html
                '''
                self.fn = fn
                self.parent = None
                self.root = root.copy()
                d = self.parse(fn)
                self.do_prefix(d)
                self.code_language = self.get_code_language(d)
                cells = d.get('cells', [])
                for n, cell in enumerate(cells):
                    self.do_cell(cell, n)
                self.indent_cells()
                c.selectPosition(self.root)
                c.redraw()
            #@+node:ekr.20160326133626.1: *5* indent_cells & helpers
            def indent_cells(self):
                '''
                Indent md nodes in self.root.children().
                <h1> nodes and non-md nodes stay where they are,
                <h2> nodes become children of <h1> nodes, etc.
                '''
                # Careful: links change during this loop.
                p = self.root.firstChild()
                stack = []
                while p and p != self.root:
                    m = self.re_header.search(p.h)
                    n, name = self.check_header(m)
                    if n is None: n = 1
                    assert p.level() == 1, (p.level(), p.h)
                    # g.trace('n', n, 'stack', len(stack), p.h)
                    stack = self.move_node(n, p, stack)
                    p.moveToNodeAfterTree()
            #@+node:ekr.20160326214638.1: *6* move_node
            def move_node(self, n, p, stack):
                '''Move node to level n'''
                if stack:
                    stack = stack[:n]
                    if len(stack) == n:
                        prev = stack.pop()
                        p.moveAfter(prev)
                    else:
                        parent = stack[-1]
                        n2 = parent.numberOfChildren()
                        p.moveToNthChildOf(parent, n2)
                stack.append(p.copy())
                # g.trace('   n', n, 'stack', len(stack), p.h)
                return stack
            #@+node:ekr.20160322144620.1: *5* Utils
            #@+node:ekr.20160322053732.1: *6* error
            def error(self, s):
                
                g.es_print('error: %s' % (s), color='red')
            #@+node:ekr.20160323110625.1: *6* get_code_language
            def get_code_language(self, d):
                '''Return the language specified by the top-level metadata.'''
                name = None
                m = d.get('metadata')
                if m:
                    info = m.get('language_info')
                    if info:
                        name = info.get('name')
                return name
            #@+node:ekr.20160321044209.1: *6* get_file_name
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
            #@+node:ekr.20160321131938.1: *6* is_dict
            def is_dict(self, obj):
                
                return isinstance(obj, (dict, nbformat.NotebookNode))
            #@+node:ekr.20160326100052.1: *6* is_empty_code
            def is_empty_code(self, cell):
                '''Return True if cell is an empty code cell.'''
                if cell.get('cell_type') == 'code':
                    source = cell.get('source','')
                    metadata = cell.get('metadata')
                    keys = sorted(metadata.keys())
                    if 'collapsed' in metadata:
                        keys.remove('collapsed')
                    outputs = cell.get('outputs')
                    # g.trace(len(source), self.parent.h, sorted(cell))
                    return not source and not keys and not outputs
                return False
            #@+node:ekr.20160321154510.1: *6* new_node
            def new_node(self, h):
                
                parent = self.parent or self.root
                p = parent.insertAsLastChild()
                p.h = h
                return p
            #@+node:ekr.20160320140531.1: *6* parse
            def parse(self, fn):
                
                if g.os_path_exists(fn):
                    with open(fn) as f:
                        payload_source = f.name
                        payload = f.read()
                    nb = nbformat.reads(payload, as_version=4)
                        # nbformat.NO_CONVERT: no conversion
                        # as_version=4: Require IPython 4.
                    return nb
                else:
                    g.es_print('not found', fn)
                    return None
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
        #@+others
        #@+node:ekr.20160321072233.1: *4* class Export_IPYNB
        class Export_IPYNB:
            '''A class to export outlines to .ipynb files.'''

            #@+others
            #@+node:ekr.20160321072233.2: *5*  ctor
            def __init__(self, c):
                '''Ctor for Import_IPYNB class.'''
                self.c = c
                    # Commander of present outline.
                self.required_cell_keys = ('cell_type', 'metatdata', 'outputs', 'source')
                    # Keys that exist for the present cell.
                self.indent = 0
                    # The indentation level of generated lines.
                self.lines = []
                    # The lines of the output.
                self.root = None
                    # The root of the outline.
            #@+node:ekr.20160321072504.1: *5* export_outline (entry point)
            def export_outline(self, root, fn=None):
                '''Import the given .ipynb file.'''
                trace = True # and not g.unitTesting
                self.root = root
                self.indent = 0
                self.lines = []
                if not fn:
                    fn = self.get_file_name()
                if fn:
                    self.put_outline()
                    self.lines = self.clean_outline()
                    s = '\n'.join(self.lines)
                    if g.isUnicode(s):
                        s = g.toEncodedString(s, encoding='utf-8', reportErrors=True)
                    try:
                        f = open(fn, 'wb')
                        f.write(s)
                        f.close()
                        g.es_print('wrote: %s' % fn)
                    except IOError:
                        g.es_print('can not open: %s' % fn)
            #@+node:ekr.20160321074510.1: *5* put, put_key_string & put_key_val
            def put(self, s):

                # End every line with a comma, unless s ends with '[' or '{'.
                # Clean_outline will remove commas as needed.
                if s.endswith('[') or s.endswith('{') or s.endswith(','):
                    pass
                else:
                    s = s + ','
                line = '%s%s' % (' '*self.indent, s)
                self.lines.append(line)
                
            def put_key_string(self, key, s):
                
                self.put('"%s": "%s"' % (key, self.clean(s)))

            def put_key_val(self, key, val, indent=False):

                self.put('"%s": %s' % (key, val))
                if indent:
                    self.indent += 1
            #@+node:ekr.20160322040710.1: *5* put_any_non_cell_data
            def put_any_non_cell_data(self, p, exclude=None):
                
                if self.is_cell(p):
                    return # put_cell handles this.
                assert p.h.startswith('#'), p.h
                key = p.h[1:].strip()
                if key == '{prefix}':
                    return # put prefix handles this.
                has_children = self.has_data_children(p)
                i = key.find(':')
                if i > -1:
                    kind = key[:i+1]
                    key = key[i+1:]
                else:
                    kind = '???'
                    key = '???'
                if key == exclude:
                    return # The caller will generate this key.
                if kind == 'list:':
                    if has_children:
                        # Lists are always lists of dicts.
                        self.put_key_val(key, '[', indent=True)
                        self.put_indent('{')
                        for child in p.children():
                            self.put_any_non_cell_data(child)
                        self.put_dedent('}')
                        self.put_dedent(']')
                    elif p.b.strip():
                        self.put_list(key, p.b)
                    else:
                        self.put_key_val(key, '[],')
                elif kind == 'dict:':
                    if p.b.strip():
                        self.oops(p, 'ignoring body text')
                    if has_children:
                        self.put_key_val(key, '{', indent=True)
                        if has_children:
                            for child in p.children():
                                self.put_any_non_cell_data(child)
                        self.put_dedent('}')
                    else:
                        # Assume there is a reason for the empty dict.
                        self.put_key_val(key, '{}')
                elif kind == 'str:':
                    self.put_key_string(key, p.b)
                elif kind == 'null:':
                    self.put_key_val(key, 'null')
                else:
                    # Unusual case: int, etc.
                    self.put_key_val(key, p.b)
            #@+node:ekr.20160321073531.1: *5* put_cell
            def put_cell(self, p):
                '''Put the cell and all it's hidden data.'''
                self.put_indent('{')
                self.put_cell_data(p)
                self.put_dedent('}')
                for child in p.children():
                    if self.is_cell(child):
                        self.put_cell(child)
            #@+node:ekr.20160321074345.1: *5* put_cell_data & helpers
            def put_cell_data(self, p):
                '''Put all the hidden data for cell p.'''
                if self.is_cell(p):
                    type_ = self.put_cell_type(p)
                    self.put_metadata(p, type_)
                    if type_ != 'markdown':
                        self.put_execution_count(p)
                        self.put_outputs(p)
                    self.put_source(p, type_)
                else:
                    for child in p.children():
                        self.put_any_non_cell_data(child)
            #@+node:ekr.20160321135341.1: *6* put_cell_type
            def put_cell_type(self, p):
                '''Put the 'cell_type' dict for cell p.'''
                assert self.is_cell(p), p.h
                p_key = self.find_key('cell_type', p)
                if p_key:
                    type_ = p_key.b.strip()
                else:
                    colorizer = self.c.frame.body.colorizer
                    language = colorizer.scanColorDirectives(p)
                    if language in ('rest', 'markdown', 'md'):
                        type_ = 'markdown'
                    else:
                        type_ = 'code'
                self.put_key_string('cell_type', type_)
                return type_
            #@+node:ekr.20160323095357.1: *6* put_execution_count
            def put_execution_count(self, p):
                '''Put the 'execution_count' for cell p.'''
                assert self.is_cell(p), p.h
                p_key = self.find_key('execution_count', p)
                if p_key and p_key.b.strip():
                    count = p_key.b.strip()
                else:
                    count = 'null'
                self.put_key_val('execution_count', count)
            #@+node:ekr.20160323082439.1: *6* put_metadata
            def put_metadata(self, p, type_):
                '''Put the 'metadata' dict for cell p.'''
                assert self.is_cell(p), p.h
                self.put_key_val('metadata', '{', indent=True)
                p_key = self.find_key('metadata', p)
                if p_key:
                    # Put the existing keys, but not collapsed.
                    for child in p_key.children():
                        self.put_any_non_cell_data(child, exclude='collapsed')
                if type_ == 'code':
                    self.put_key_val('collapsed', 'true' if p.isExpanded() else 'false')
                self.put_key_string('leo_headline', p.h)
                    # Remember the headline.
                self.put_dedent('}')
            #@+node:ekr.20160323082525.1: *6* put_outputs
            def put_outputs(self, p):
                '''Return the 'outputs' list for p.'''
                assert self.is_cell(p), p.h
                p_key = self.find_key('outputs', p)
                if p_key and self.has_data_children(p_key):
                    # Similar to put_any_non_cell_data.
                    self.put_key_val('outputs', '[', indent=True)
                    self.put_indent('{')
                    for child in p_key.children():
                        self.put_any_non_cell_data(child)
                    self.put_dedent('}')
                    self.put_dedent(']')
                else:
                    self.put_key_val('outputs', '[]')
            #@+node:ekr.20160323140748.1: *6* put_source
            header_re = re.compile(r'^<[hH][123456]>')

            def put_source(self, p, type_):
                '''Put the 'source' key for p.'''
                s = ''.join([z for z in g.splitLines(p.b) if not g.isDirective(z)])
                # Auto add headlines.
                if type_ == 'markdown' and not self.header_re.search(p.b):
                    n = min(6, self.level(p))
                    heading = '<h%(level)s>%(headline)s</h%(level)s>\n\n' % {
                        'level': n,
                        'headline': p.h,
                    }
                    s = heading + s
                    # Not completely accurate, but good for now.
                self.put_list('source', s or '# no code!')
            #@+node:ekr.20160323070611.1: *5* put_indent & put_dedent
            def put_dedent(self, key=None):
                '''Increase indentation level and put the key.'''
                self.indent -= 1
                if key:
                    self.put(key)
                
            def put_indent(self, key=None):
                '''Put the key and then decrease the indentation level.'''
                if key:
                    self.put(key)
                self.indent += 1
            #@+node:ekr.20160321142040.1: *5* put_list
            def put_list(self, key, s):
                '''Put a json list.'''
                if s.strip():
                    self.put_indent('"%s": [' % key)
                    for s in g.splitLines(s):
                        self.put('"%s\\n",' % self.clean(s))
                    self.put_dedent(']')
                else:
                    self.put_key_val(key, '[]')
                        ### Bug fix?
            #@+node:ekr.20160322063045.1: *5* put_outline
            def put_outline(self):
                '''Put all cells in the outline.'''
                self.put_indent('{')
                self.put_indent('"cells": [')
                for child in self.root.children():
                    if self.is_cell(child):
                        self.put_cell(child)
                self.put_dedent(']')
                self.put_dedent()
                self.put_prefix()
                self.put('}')
            #@+node:ekr.20160322061416.1: *5* put_prefix
            def put_prefix(self):
                '''Put the data contained in the prefix node, or defaults.'''
                p = self.find_key('# {prefix}', self.root)
                self.indent += 1
                if p:
                    for child in p.children():
                        self.put_any_non_cell_data(child)
                else:
                    prefix = self.default_metadata()
                    for s in g.splitLines(prefix):
                        self.put(s.rstrip())
                self.indent -= 1
            #@+node:ekr.20160323080255.1: *5* Utils
            #@+node:ekr.20160322071826.1: *6* clean (TO DO)
            def clean(self, s):
                '''Perform json escapes on s.'''
                return s.replace('\\','\\\\').replace('"', '\\"').rstrip()
            #@+node:ekr.20160322073018.1: *6* clean_outline
            def clean_outline(self):
                '''Remove commas before } and ]'''
                # JSON sure is picky.
                n, result = len(self.lines), []
                for i, s in enumerate(self.lines):
                    assert not s.endswith('\n')
                    if s.endswith(','):
                        if i == n-1:
                            val = s[:-1]
                        else:
                            s2 = self.lines[i+1].strip()
                            if s2.startswith(']') or s2.startswith('}'):
                                val = s[:-1]
                            else:
                                val = s
                    else:
                        val = s
                    result.append(val)
                return result
            #@+node:ekr.20160323134348.1: *6* default_metadata
            def default_metadata(self):
                '''Return the top-level metadata to use if there is no {prefix} node.'''
                s = '''\
            "metadata": {
             "kernelspec": {
              "display_name": "Python %(version)s",
              "language": "python",
              "name": "python%(version)s"
             },
             "language_info": {
              "codemirror_mode": {
               "name": "ipython",
               "version": %(version)s
              },
              "file_extension": ".py",
              "mimetype": "text/x-python",
              "name": "python",
              "nbconvert_exporter": "python",
              "pygments_lexer": "ipython3",
              "version": "%(long_version)s"
             }
            },
            "nbformat": 4,
            "nbformat_minor": 0'''
                n1, n2 = sys.version_info[0], sys.version_info[1]
                s = s % {
                   'version': n1,
                   'long_version': '%s.%s' % (n1, n2),
                }
                return g.adjustTripleString(s, 1)
            #@+node:ekr.20160323070240.1: *6* find_key
            def find_key(self, key, p):
                '''Return the non-cell node in p's direct children with the given key.'''
                for child in p.children():
                    if child.h.endswith(key):
                        return child
                return None
            #@+node:ekr.20160323094152.1: *6* has_data_children
            def has_data_children(self, p):
                '''Return True if p has any non-cell direct children.'''
                return p.hasChildren() and any([not self.is_cell(z) for z in p.children()])
            #@+node:ekr.20160322062914.1: *6* get_file_name (export)
            def get_file_name(self):
                '''Open a dialog to write a Jupyter (.ipynb) file.'''
                c = self.c
                fn = g.app.gui.runSaveFileDialog(
                    c,
                    defaultextension=".ipynb",
                    filetypes=[
                        ("Jypyter files", "*.ipynb"),
                        ("All files", "*"),
                    ],
                    initialfile='',
                    title="Export To Jupyter File",
                )
                c.bringToFront()
                return fn
            #@+node:ekr.20160321140725.1: *6* is_cell
            def is_cell(self, p):
                '''Return True if p is a cell node.'''
                return not p.h.startswith('#')
            #@+node:ekr.20160323144924.1: *6* level
            def level(self, p):
                '''Return the level of p relative to self.root (one-based)'''
                return p.level() - self.root.level()

            #@+node:ekr.20160322092429.1: *6* oops
            def oops(self, p, s):
                '''Give an error message.'''
                g.es_trace('===== %s %s' % (s, p.h), color='red')
            #@-others
        #@-others
        c = self.c
        Export_IPYNB(c).export_outline(c.p)
    #@-others
#@-others
#@-leo
